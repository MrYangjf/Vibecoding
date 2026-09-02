---
title: 步骤驱动工作流标准
date: 2026-09-01
tags: [规范, 工作流, 步骤驱动, WorkStep, 超时, 可观测性, 命令变量, 监听线程, ADR-047]
---

# 步骤驱动工作流标准（StepDrivenWorkflow）

> **触发**：用户提出「流程怎么推进 / 步骤怎么编号 / 流程卡在哪一步 / 流程超时怎么判 / 主流程改成监听线程写法」等问题时，AI **直接读取本页执行**，无需用户重复输入。决策见 [[decisions/ADR-047-StepDrivenWorkflow]]。
>
> **参考实现来源**：外部项目 `HonorMachineTest` 的 `PcomDeviceInterface/Work/Process/StationProcess.cs`（抽象基类）+ `AssemblyProcess.cs`（实现，约 3000 行 / 100+ 步）。本页是把该写法**提炼并适配**到 AdaWeldSystem 后的标准，**不是原样照搬**——差异见第三章「三层融合」与第九章「红线」。

---

## 一、为什么要有这套标准

### 1.1 现架构的痛点（AdaWeldSystem 现状）

步骤驱动改造前，主设备控制（`DeviceControlWork` 前身 `MainDeviceWorkflow`）是**事件驱动 + 状态转移**模型：

```csharp
// 现状：通讯层回调 → 立即处理 → SetStep 换态 → 结束
GlobalCommData.CommunicationCommandReceived += OnCommunicationCommand;
private void OnCommunicationCommand(object sender, string message)
{
    if (code >= 0 && code <= 6) ReceiveRobotPose((RobotPose)code);   // 直接驱动
}
protected override void OnRobotPoseReceived(RobotPose pose)
{
    switch (pose) { case RobotPose.PreWeldPose: EnterPreWeldPose(); break; ... }
}
```

三个结构性缺陷：

| 缺陷 | 表现 | 后果 |
|---|---|---|
| **无持续线程** | 无 `while` 循环体，全靠外部事件推一下动一下 | 事件丢失/重复即流程停滞，无法自恢复 |
| **状态粒度粗** | 旧主设备流程态枚举仅覆盖数态（Idle…Alarm） | 只知道"在 Preworking"，不知道"Preworking 里的第几步、卡在哪" |
| **无时间维度** | 流程态无进入时间戳 | 无法判超时、无法自动告警、无法回答"卡了多久" |

### 1.2 参考实现的收益

`StationProcess`/`AssemblyProcess` 的写法恰好补齐三点：主程序加载流程后，**仅凭「步骤数字 + 进入时间」两个变量就能完全监控流程状态**——UI 上显示 `组装工位：RUNNING / step:213 / 3.4s`，卡死时步号不动、时长持续涨，一眼定位。

---

## 二、核心模型：三件套

```
外部指令 ──写──> [命令变量 Command Slot] ──读──> [常驻监听线程 Run Loop] ──> [FlowProcess() 单步分派]
                        (单一 int/枚举)              (while + 节拍)              switch(WorkStep)
                                                                                      │
                                                                        WorkStep + WorkStartTime
```

### 2.1 命令变量（Command Slot）

通讯层**只写变量，不做业务**：一个变量承载当前待处理指令，流程侧消费后置回 `None`。

```csharp
// 写入侧：通讯适配层（唯一写入点）
private void OnCommunicationCommand(object sender, string message)
{
    int code;
    if (!int.TryParse(message.Trim(), out code)) return;
    _pendingCommand = (RobotSignalCode)code;      // 只赋值，不处理
}

// 消费侧：监听线程（唯一读取点）
private void RunLoop()
{
    while (!_closing)
    {
        RobotSignalCode cmd = _pendingCommand;    // 取快照
        if (cmd != RobotSignalCode.None)
        {
            _pendingCommand = RobotSignalCode.None;   // 先清，防重入
            EnterFlowByCommand(cmd);                  // 进入对应流程（设置起始 WorkStep）
        }
        FlowProcess();                                // 单步分派
        Thread.Sleep(_beatMs);
    }
}
```

**要点**：命令变量取代"事件回调里直接干活"。好处是① 事件丢失时可被下一次指令覆盖纠正；② 重复指令天然去重；③ 指令与执行解耦，可加优先级/队列。

### 2.2 常驻监听线程（Run Loop）

每个流程一个 `while(!closing)` 线程，固定节拍（参考实现 10ms，本地建议 10~20ms）反复调用 `FlowProcess()`。

```csharp
void AssemblyWork()
{
    while (!IsClose)
    {
        if (CommenData.CurrentStatus != MachineStatus.Running)
        {
            Thread.Sleep(100);
            AssemblyProcess.Instance.ResetWorkTime();   // 非运行态持续刷新时间戳
            continue;
        }
        AssemblyProcess.Instance.FlowProcess();
        Thread.Sleep(10);
    }
}
```

> **关键细节（易漏）**：非运行/暂停态必须持续调 `ResetWorkTime()`。否则暂停 10 分钟后恢复，`DateTime.Now - WorkStartTime` 直接超阈值，第一步就误报超时。

### 2.3 执行步（WorkStep + WorkStartTime）

```csharp
/// <summary>工作步数（流程内部游标，int 编号，见第五章段位规范）。</summary>
public int WorkStep = 0;
/// <summary>当前步进入时间（每次改 WorkStep 必须同步刷新，用于超时判定与可观测性）。</summary>
public DateTime WorkStartTime = DateTime.Now;
```

**成对写，禁止拆开**：

```csharp
WorkStep = 20;                    // 正确：步号与时间成对
WorkStartTime = DateTime.Now;
```

---

## 三、三层融合（关键：执行步不是阶段态的替代品）

照搬参考实现会与 [[decisions/ADR-041-MainDeviceControlArchitecture]]、[[decisions/ADR-042-WorkflowStateBaseGeneric]] 冲突。正确做法是**三层并存、各司其职**：

| 层 | 载体 | 粒度 | 消费方 | 变更入口 | 状态 |
|---|---|---|---|---|---|
| **连接态** `State` | `SubDeviceState` 枚举 | 2 态（Disconnected/Connected） | UI 连接指示灯 | `ConnectOn`/`ConnectOff` → 基类 `SetState()`，**禁手工赋值** | ADR-049 |
| **焊接过程态** `WeldStatus`（原阶段态 `Step`） | `SubDeviceWeldStatus` 枚举 | 7 态（Standby/PreWork/Starting/Working/Stopping/ErrorAborted/ManualStopped） | UI 语义、跨模块判断、事件订阅 | 基类 `SetWeldStatus()`（私有 `SetStep`→`MapWeldStatus` 映射） | ADR-049 |
| **主设备运行态** `Status` | `MainDeviceStatus` 枚举 | 6 态（Running/Alarm/EStop/Stop/NoReset/Reseting） | UI 状态灯、整机门控 | `DeviceControlWork.SetStatus()`（私有，禁手工赋值） | ADR-049 |
| **执行步** `WorkStep` | `int` + `DateTime` | 数十~上百步 | 流程内部推进、超时判定、现场排故 | `GoStep(n)` 唯一入口（基类成对刷新步号+时间） | 本页（ADR-047/049） |

> **一句话**：**焊接过程态（阶段态）是对外名片，执行步是内部游标。** 一个焊接过程态可横跨多个执行步（如 `PreWork` 阶段包含 10→11→12→…→19）；执行步推进到收尾段时才触发 `SetWeldStatus()` 换阶段态。
>
> **易误判**：不要在 `WorkStep` 上套枚举——步号需要跳跃、需要段位、需要现场口头报号排故，枚举做不到；也不要用 `WorkStep` 取代 `Step`，否则 UI 与跨模块判断全部失语义。

**映射时机约定**：

```csharp
// 进入新阶段时：先切焊接过程态（对外可见），再落起始执行步
SetWeldStatus(SubDeviceWeldStatus.PreWork, "进入焊前准备");   // 阶段态：对外
GoStep(10);                                                       // 执行步：内部游标（GoStep 成对刷新步号+时间）

// 阶段内推进：只动执行步，不动阶段态
case 10:  ...; GoStep(11); break;

// 阶段收尾：执行步回到待机，同时切焊接过程态
case 19:  SetWeldStatus(SubDeviceWeldStatus.Working, "进入焊接"); GoStep(100); break;
```

---

## 四、基类契约（参考实现 → 本地命名映射）

参考基类 `StationProcess` 的「1 字段组 + 2 方法区 + 6 抽象契约」结构，本地对应如下：

| 参考实现 | 本地命名 | 语义 | 是否新增 |
|---|---|---|---|
| `TAG` / `IsStationEnable` / `moManager` | `_tag` / 沿用 | 日志前缀、工位使能、设备句柄 | 已有 |
| `WorkStep` / `WorkStartTime` | 同名 | 执行步游标 + 进入时间 | **新增** |
| `abstract void FlowProcess()` | `protected abstract void FlowProcess()` | 单步分派（switch），被线程反复调用 | **新增** |
| `abstract bool ResetProcess()` | `protected abstract bool ResetFlow()` | 复位流程（回零/清气缸/清真空），返回成败 | 复用 `InitializeFlow` 语义，按流程需要定 |
| `abstract void ClearStatus()` | `protected abstract void ClearStatus()` | 状态与 `WorkStep` 清零（含 `WorkStartTime` 刷新） | 新增/扩展 |
| `abstract void ResetWorkTime()` | `public void ResetStepTime()` | 刷新 `WorkStartTime`（非运行态每拍调用） | **新增** |
| `abstract void ClearProduct()` | `protected abstract void ClearProduct()` | 清料流程（排空在制品） | **新增** |
| `abstract void LoadConfig(XmlReader)` / `SaveConfig(XmlWriter)` | 按现有持久化约定（本地为 INI） | 配置持久化 | **不引入 XML**，沿用项目既有方式 |
| `AxisCheck/AxisAbsMoveNoBlock/AxisWaitCheckDone/CylinderStretch` 等 | 对应子设备 API（运控/IO） | 设备动作原语，**统一返回 bool 供 `if(!…) break;` 短路** | 复用现有 API |

> **短路范式（参考实现精髓）**：动作原语一律 `bool` 返回，失败即 `break` 出 switch，**保持 `WorkStep` 不变**，下一拍重入重试。这样"失败重试"不需要额外代码：
>
> ```csharp
> case 18:
>     if (!SafeMoveAxis(_axis, _safePos)) break;     // 失败 → 步号不变 → 下拍重来
>     if (!SafeWaitAxis(_axis)) break;
>     if (!CheckAxisDone(_axis, _safePos)) break;
>     WorkStep = 19; WorkStartTime = DateTime.Now;    // 全部成功才推进
>     break;
> ```

---

## 五、步骤号段位规范（编码约定）

参考 `AssemblyProcess` 用 0/1/10~19/30~39/80/100/700~702/800~801/900~901 表达"主链路 + 变体 + 清料 + 成功收尾 + 失败收尾"。本地统一约定：

| 段位 | 含义 | 说明 |
|---|---|---|
| `0` | 待机 / 入口判定 | 每拍重入，做前置检查与分支派发 |
| `1~9` | 入口准备 | 安全位、模式判定、资源检查 |
| `10~99` | **主链路 A** | 主工艺路径，步长 10 起步，中间插步用 +1（11/12…） |
| `100~199` | **主链路 B** | 第二条主路径（如双工位、双料仓） |
| `200~699` | 预留扩展 | 按主链路序号 ×100 递增 |
| `700~799` | **清料 / 排空** | 清料专用，结束回 `0` |
| `800~899` | **成功收尾** | 置结果 OK、允许流走、回 `0` |
| `900~999` | **失败收尾** | 置结果 NG、记录故障、回 `0` 或 `Alarm` |

**编号规则**：
1. 主链路步号间隔 ≥10，便于后续插步（在 10 与 20 之间插 11/12/13，不必重排全表）。
2. 同一语义的并行变体用「百位」区分（料仓1=`1x`，料仓2=`3x`，参考实现即如此）。
3. 每一步必须配一张「步号 → 中文名」映射表（常量类或 `switch` 转字符串），供 UI 与日志使用——**没有映射表的步号等于不可观测**。

```csharp
/// <summary>执行步名称映射（UI 与日志可观测性依赖此表，新增步必须同步登记）。</summary>
public static string GetStepName(int step)
{
    switch (step)
    {
        case 0:  return "待机-入口判定";
        case 10: return "焊前准备-子设备连接";
        case 11: return "焊前准备-开激光";
        case 700: return "清料-回等待位";
        case 900: return "失败收尾-壳体流走";
        default: return "步骤 " + step;
    }
}
```

### 5.1 成员命名约定（2026-09-01 确立，硬约束）

**步号（数据）与单步方法（行为）必须异名**，否则 C# 报 **CS0102「类型已包含同名成员定义」**——`private const int StepPreWork = 10;` 与 `private void StepPreWork()` 处在同一类作用域，常量名与方法名直接冲突。

| 角色 | 命名 | 示例 |
|---|---|---|
| 步号常量 | `StepXxx`（帕斯卡，常量） | `private const int StepPreWork = 10;` |
| 单步方法 | `DoXxx()`（Do 前缀） | `private void DoPreWork()` |
| 分派写法 | 常量在 `case`，方法在调用位 | `case StepPreWork: DoPreWork(); break;` |

**配套规则**：

1. `FlowProcess()` 的 `switch` 与 `GetStepName()` 的 `case` 一律写常量，**禁止裸数字**（魔法数字不可检索、不可维护）。
2. 通用步号由基类提供，子类**不得重复定义**（重复定义触发 CS0108 警告）：

   | 基类常量 | 值 | 子类中 |
   |---|---|---|
   | `StepIdle` | 0 | 直接引用，不定义 |
   | `StepFinishOk` | 800 | 直接引用，不定义 |
   | `StepFinishFail` | 900 | 直接引用，不定义（含报警收尾步骤） |

3. 失败收尾统一调基类 `FailFlow(reason)`（内部自动取 `_workStep` 作为 `FailStep`），**子类不再自造 `FailFlow`**；失败原因读基类 `FailReason`、卡点步号读基类 `FailStep`。
4. 领域语义允许保留在方法名上（如报警收尾步骤的 `DoAlarm()` 挂在 `case StepFinishFail`）。

> 踩坑实录与批量改名步骤见 [[lessons/StepMemberNameCollision]]。

---

## 六、单步写法三范式

### 范式 A：瞬时动作步（发完就走）

```csharp
case 10:
    Log("下发机器人焊前位指令");
    SendDeviceCommand(DeviceCommand.CmdGoPreWeld);
    WorkStep = 11; WorkStartTime = DateTime.Now;
    break;
```

### 范式 B：等待完成步（条件达成推进 / 超时进告警）

```csharp
case 14:
    if (_io.VacuumCheck.IsOn() || _vacuumDisabled)
    {
        Log("吸取托盘真空 OK");
        WorkStep = 15; WorkStartTime = DateTime.Now;
    }
    else if ((DateTime.Now - WorkStartTime).TotalMilliseconds > CylinderMoveTimeout)
    {
        SetWeldStatus(SubDeviceWeldStatus.ErrorAborted, reason);   // 焊接过程态 → ErrorAborted（经 SetWeldStatus，非手工赋值）
        Log("吸取托盘真空超时", MessageLevel.Error);
        FaultRecoveryManager.Instance.RecordFault("Xxx", "真空超时", FaultCategory.Timeout);
        WorkStep = 900; WorkStartTime = DateTime.Now;   // 进失败收尾，不留在原步死等
    }
    break;
```

### 范式 C：分支派发步（按模式变量跳段）

```csharp
case 1:
    if (_cmd == Command.ClearLine) { WorkStep = 700; WorkStartTime = DateTime.Now; break; }
    if (_spaceModel == 2 && _space2.Ready) { WorkStep = 30; WorkStartTime = DateTime.Now; break; }
    if (_spaceModel == 1 && _space1.Ready) { WorkStep = 10; WorkStartTime = DateTime.Now; break; }
    break;    // 条件不满足：步号不变，下拍重入等待
```

---

## 七、超时判据

| 项 | 约定 |
|---|---|
| **时间戳刷新** | 每次 `WorkStep = n;` 必须紧跟 `WorkStartTime = DateTime.Now;`（成对，见 2.3） |
| **暂停/非运行态** | 监听线程每拍调 `ResetStepTime()`，防止恢复瞬间误判超时（见 2.2 关键细节） |
| **阈值来源** | 统一常量/配置（参考实现 `CommenData.CylinderMoveTimeOut`），**禁止硬编码魔法数** |
| **超时去向** | 三步走：置 Alarm（经 `SetStep` 映射）→ 记错误日志 + `FaultRecoveryManager.RecordFault` → 跳 `9xx` 失败收尾段 |
| **禁止** | 超时后仍留在原步继续等（等于没判）；超时后直接 `return` 不进收尾（丢状态） |

---

## 八、可观测性（本标准的首要收益）

主程序加载流程后，读两个变量即可完全监控：

```csharp
int step = workflow.WorkStep;
double elapsedMs = (DateTime.Now - workflow.WorkStartTime).TotalMilliseconds;

// UI 呈现（参考 FormMain 的 "组装工位：RUNNING / step:213 / 3.4s"）
lblStatus.Text = string.Format("{0}：{1} / step:{2} / {3:F1}s",
    workflow.StateName, workflow.Step, step, elapsedMs / 1000.0);
lblStepName.Text = GetStepName(step);
```

**排故判据**：

| 现象 | 判读 |
|---|---|
| 步号持续不变 + 时长持续上涨 | 卡在当前步：查该步的等待条件（传感器/回调/超时阈值） |
| 步号在两三步间来回跳 | 条件震荡：查推进条件与回退条件是否互斥 |
| 时长恒定不涨 | 线程未跑（`IsStationEnable=false` 或线程未启动）——参考实现 `!IsStationEnable` 时 `Sleep(100)` 直接 return |
| 步号直接跳 9xx | 失败收尾：查上一步的错误日志 |

---

## 九、红线（违反即回退）

1. **不得废弃焊接过程态枚举（`SubDeviceWeldStatus`）与 `SetWeldStatus()`**。执行步是新增层，不是替代品（[[decisions/ADR-049-ThreeStateModelRefactor]]、[[decisions/ADR-043-WorkflowResponsibilityBoundary]] 继续有效）。
2. **连接态/焊接过程态/主设备运行态禁止手工赋值**，一律经 `SetState`/`SetWeldStatus`/`SetStatus` 写入（ADR-049）；旧 `MapToDeviceState()` 已废弃。
3. **单步内禁止无界阻塞等待**。`Thread.Sleep` / `while` 轮询 / **无上界的**同步 `WaitXxx` 一律不允许出现在 `case` 体内——等待靠"节拍重入 + 时间戳判超时"实现。
   > 参考实现 `CylinderStretch()` 内部 `while` 轮询 + `case 17` 里 `Thread.Sleep(500)` 属其既有做法，**本地不引入**：阻塞会冻结整个流程线程，使超时判定与指令响应同时失效。
   >
   > **⚠️ 与 [[decisions/ADR-005-CallbackAcquisition]] 的边界裁定（2026-09-01）**：ADR-005 的取图 `WaitOne(超时上限 5000ms)` **不违反本红线**，因为它满足三条——①**有界**（超时上界按帧周期缩放，默认上限 5000ms）；②**可失败**（超时后 `_lastAcquiredMat = null`，走失败/重试分支，不静默继续）；③**有外部信号源**（相机回调 `Set()`，不是空转轮询）。
   > 判据一句话：**有界 + 可失败 = 合法（等待完成范式）；无界 + 静默 = 违规**。若采用步骤驱动，ADR-005 的实现应落在「等待完成」单步内并保证超时后跳 9xx 失败收尾，不得演化为 `while(true)`。
   >
   > **⚠️ 与 [[decisions/ADR-048-AutoManualDualWorkflow]] 的边界（2026-09-02 两度修订）**：红线 3 约束的是 **`FlowProcess()` / 执行步**（监听线程反复重入的执行体）。ADR-048 修订后**自动运行 = 仅 `FlowProcess()`**（`AutoRunFlow`/`AutoRun` 阻塞式自动线程已废弃），主设备在其 `FlowProcess` 中级联子设备 `FlowProcess`；初始化 `InitializeFlow()` 阻塞同步（统一由主设备级联）、手动连接 `ManualOn()` 非阻塞起线程（内置超时看门狗，超时反馈 Info 不置 Alarm）。红线精神贯通：所有阻塞必须有界、可失败、可中止。
4. **命令变量单一写入点**：通讯层只赋值，业务逻辑一律在监听线程内执行。禁止在通讯回调里直接调 `SetStep` 或动作方法。
5. **步间传值用流程字段**，禁止依赖局部变量跨步传递（每拍重入，局部变量必然丢失）。
6. **UI 线程禁止直接调用 `FlowProcess()`**，只能读 `WorkStep`/`WorkStartTime`/只读属性（[[guides/WinForms-UI-Threading]]）。
7. **新增步必须同步登记名称映射表**（第五章），否则该步不可观测。
8. **流程不替设备发数据、不转发子设备事件**（[[standards/WorkflowResponsibilityBoundary]] R1/R2 在步骤驱动下同等有效）。

---

## 十、落地清单（✅ 2026-09-01 全量落地，ADR-047 转 accepted）

| 文件 | 改造项 | 优先级 | 状态 |
|---|---|---|---|
| `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs` | 新增 `WorkStep` / `WorkStartTime` / `StepElapsedMs` / `WorkStepName` / `StepStatusText`、`ResetStepTime()`、`IsStepTimeout()`、**`GoStep(n)` 唯一改步入口**、`GetStepName()` 与 `FlowProcess()` 抽象、监听线程 `RunLoop()` + `StartRunLoop`/`StopRunLoop`、`BeatMs`/`RunLoopPriority`、`Dispose()` 模板方法 + `DisposeManaged()` 钩子 | P0 | ✅ |
| `MainDeviceControl/DeviceWorkflow/DeviceControlWork.cs` | 命令变量**三槽** `_pendingAbort` / `_pendingCommand` / `_pendingPose`（Pose 与 Command 编码区间重叠，必须分槽）；`ReceiveRobotPose`/`ReceiveRobotCommand` 只写变量；内部执行步随编排推进（详情见 [[api/MainDeviceWorkflow]]） | P0 | ✅ |
| `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` | 删 `SpinWait` 与自建线程；执行步 0/10/11/20/30/31/100/700/800/900；失败计数改时长判据 | P1 | ✅ |
| `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` | `WaitOne(5000)` → `WaitOne(0)` 非阻塞探测；执行步 0/10/20/30/800/900 | P1 | ✅ |
| `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` | `MonitorLoop` 并入基类线程（`BeatMs=20`）；执行步 0/10/20/30/100/110/700/900；`Start()` 改「受理指令」语义 | P2 | ✅ |
| `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` | `ComputeAndOutput()` 改命令变量模式；执行步 0/10/20/800/900 | P2 | ✅ |
| `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` | 骨架期补空 `FlowProcess()`/`GetStepName()`，`IsRunLoopActive = false`（不起空转线程） | P2 | ✅ |
| `MainDeviceControl/DeviceWorkflow/DeviceStatusWork.cs` | 三线程 `IOWork`/`EMGWork`/`StatusWork`（非步骤驱动，随整机启动 `StartWork`）；互锁/急停/三色灯专责分离 | P2 | ✅ |
| `UIDesign/.../MainPage.cs` 等 | 状态标签加 `step:xx / x.xs` 显示 | P3 | ⬜ 未做（可选） |

### 10.1 落地后新增的三条约定（超出原规划，2026-09-01 确立）

1. **`GoStep(n)` 是唯一改步入口**。基类提供 `protected void GoStep(int step)`，内部成对刷新 `_workStep` 与 `_workStartTicks` 并记日志；两个字段均为基类私有，子类**无法绕过**。原规划的「手写 `WorkStep = n; WorkStartTime = DateTime.Now;`」已废弃——从机制上杜绝「只改步号不刷新时间」。
2. **`OnStepChanged` 复位执行步**。阶段态一切换，执行步即复位到该阶段入口步，使「阶段态（名片）↔ 执行步（游标）」关系显式化。**推论（硬约束）**：`FlowProcess()` 内 `SetStep(...)` 后**必须立即 `return`**，否则后续代码会覆盖刚复位的步号。
3. **`DisposeManaged()` 取代子类 `Dispose()`**。基类 `Dispose()` 为模板方法（停线程 → `DisposeManaged()` → `GC.SuppressFinalize`），子类一律在 `DisposeManaged()` 里释放资源，**不得重写 `Dispose()`/`Dispose(bool)`**（守 ADR-001/034）。

> 踩坑记录见 [[lessons/StepDrivenWorkflowPitfalls]]。

---

## 十一、审查清单（改任何 Workflow 前逐条过）

- [ ] **改步入口**：是否所有改步都走 `GoStep(n)`？有无直接给 `WorkStep` 赋值或手写 `WorkStartTime`？（基类字段为私有，绕不过；若发现说明改错了文件）
- [ ] **`SetStep` 后立即 return**：`FlowProcess()` 每个分支里 `SetStep(...)` 之后还有没有代码？（`OnStepChanged` 已复位执行步，继续跑会覆盖步号）
- [ ] **暂停刷新**：监听线程在非运行态是否每拍调 `ResetStepTime()`？
- [ ] **无阻塞**：`case` 体内是否有 `Thread.Sleep` / `while` 轮询 / 同步等待？（红线 3）
- [ ] **超时去向**：超时分支是否走了 Alarm + 日志 + `9xx` 收尾三步？
- [ ] **阈值常量**：超时阈值是否来自常量/配置，无硬编码魔法数？
- [ ] **映射表**：新增步号是否登记到 `GetStepName()`？
- [ ] **命令变量**：是否存在通讯回调里直接做业务的地方？（红线 4）
- [ ] **阶段态未退化**：`SetStep()` 是否仍在阶段切换点被调用？是否有人用 `WorkStep` 顶替 `Step`？
- [ ] **状态映射**：是否出现手工 `State=`/`WeldStatus=`/`Status=` 赋值？（红线 2）
- [ ] **步间传值**：是否有依赖局部变量跨步传递的写法？（红线 5）

---

## 十二、正反例对照

```csharp
// 反例 1：单步内阻塞等待（红线 3）
case 20:
    _cam.StartAcquisition();
    while (!_cam.IsFrameReady()) Thread.Sleep(10);   // 冻结线程，超时判据失效
    WorkStep = 21;
    break;

// 正例 1：等待靠重入 + 时间戳
case 20:
    if (_started) { /* 已触发，等结果 */ }
    else { _cam.StartAcquisition(); _started = true; WorkStartTime = DateTime.Now; break; }
    if (_cam.IsFrameReady()) { _started = false; WorkStep = 21; WorkStartTime = DateTime.Now; }
    else if ((DateTime.Now - WorkStartTime).TotalMilliseconds > FrameTimeout)
    { SetWeldStatus(SubDeviceWeldStatus.ErrorAborted, reason); GoStep(900); }
    break;
```

```csharp
// 反例 2：只改步号不刷新时间 → 超时立即误判
case 10: WorkStep = 11; break;

// 正例 2：成对刷新
case 10: WorkStep = 11; WorkStartTime = DateTime.Now; break;
```

```csharp
// 反例 3：通讯回调里直接做业务（红线 4）
private void OnCommunicationCommand(object sender, string message)
{
    ReceiveRobotPose((RobotPose)int.Parse(message));   // 直接驱动状态机
}

// 正例 3：只写命令变量，业务交给监听线程
private void OnCommunicationCommand(object sender, string message)
{
    int code;
    if (int.TryParse(message.Trim(), out code)) _pendingCommand = (RobotSignalCode)code;
}
```

---

## 关联

- 决策：[[decisions/ADR-047-StepDrivenWorkflow]]
- 相邻决策：[[decisions/ADR-048-AutoManualDualWorkflow]] — 自动运行/手动连接（自动运行=FlowProcess 唯一执行器，初始化阻塞同步 + 手动连接非阻塞）
- 教训：[[lessons/StepDrivenWorkflowPitfalls]] — 落地五坑（执行步复位覆盖 / 步内阻塞 / 抽象成员级联编译 / 命令槽碰撞 / 失败计数爆表）
- 架构：[[architecture/DeviceControlArchitecture]]
- 模块：[[modules/DeviceControl]]
- API：[[api/MainDeviceWorkflow]]、[[api/LineLaserWorkflow]]、[[api/MonitorCameraWorkflow]]、[[api/MotionControlWorkflow]]、[[api/WeldParamControlWorkflow]]
- 互补：[[standards/WorkflowResponsibilityBoundary]]（权责 R1~R5）、[[standards/CodeSimplification]]（五维度精简）、[[standards/UiStateSimplification]]（真相源唯一）
- 教训：[[guides/WinForms-UI-Threading]]、[[lessons/CSharp-Language-Pitfalls]]
- 参考实现（外部）：`HonorMachineTest/PcomDeviceInterface/Work/Process/StationProcess.cs`、`AssemblyProcess.cs`、`MachineControlWork.cs`
