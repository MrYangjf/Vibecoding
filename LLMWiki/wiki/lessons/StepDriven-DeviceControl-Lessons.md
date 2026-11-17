---
title: StepDriven-DeviceControl-Lessons
date: 2026-10-30
updated: 2026-10-30
tags: [教训, 步骤驱动, 执行步, DeviceWorkflowBase, 并发, 编译, 设备控制, 状态机, 线程调度]
status: active
---


# 设备控制与步骤驱动教训汇总

> 来源：2026-09-01 全量步骤驱动改造（当时已 accepted，该决策现已删除），8 个文件一次到位的实战总结。
> 规范正文见 [[architecture/DeviceControlArchitecture]]（⛔ ~~standards/StepDrivenWorkflow~~（已废弃，2026-09-17 删除）），本页只记**踩过的坑**与规避动作。

## 章节导航

- [七、设备控制与状态机教训](#七设备控制与状态机教训原六独立页-2026-09-17-并入)
  - [七.1 StateMachine-DoubleTransition](#七1-statemachine-doubletransition状态机重复转换模板方法与工作流层双重转换)
  - [七.2 CrossThreadNoStepAdvance](#七2-crossthreadnostepadvance跨线程不推进执行步rsi-报警-_seamalarmpending-volatile-标志范式)
  - [七.3 DeviceControlWorkInheritanceBypass](#七3-devicecontrolworkinheritancebypass继承绕过子类重声明-taglog-遮蔽基类-cs0108日志出口发散)
  - [七.4 DeviceWorkflowDualFlowCallerGate](#七4-deviceworkflowdualflowcallergate双流程调用方门控)
  - [七.5 HighResolutionThreadScheduling](#七5-highresolutionthreadscheduling1ms-高精度线程调度经验)
  - [七.6 StepMemberNameCollision](#七6-stepmembernamecollision步号常量与单步方法同名-cs0102常量下沉-cs0108)
  - [七.7 以上六页原文件名与坑号对照表](#七7-以上六页原文件名与坑号对照表)
- [相关页面](#相关页面)


## 七、设备控制与状态机教训（原六独立页 2026-09-17 并入）

> 2026-09-17 将 6 个独立教训页整体并入本页（原文件保留存档、不再维护），以下内容为源页原文收拢、逐坑保留；与上方坑一~坑六重复的主题仅留一句互指。

### 七.1 StateMachine-DoubleTransition（状态机重复转换：模板方法与工作流层双重转换）

> ⛔ **机制失效标注（2026-09-09 治理，ADR-021/029）**：本节针对的旧「设备状态机模板方法 + TryTransition」机制已随四态模型删除（现行 = 三态模型非泛型基类，`SetState`/`SetWeldStatus` 唯一写入入口）。**「同一状态转换不要两层各转一次」的思想仍有效**，落点变为：工作流层不得绕过基类手工给 `State`/`WeldStatus` 赋值。

> **历史语境注记（2026-09-02，ADR-034）**：本节记录的是**已删除的旧架构**——`DeviceStateMachine/` 目录、`DeviceStateMachineBase` 模板方法、`_deviceStateMachine` 字段、`DeviceState` 四态枚举均已不复存在（2026-08-28 起）。现行状态由 `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` 承载三态模型，写入唯一入口为 `SetState`/`SetWeldStatus`/`SetStatus`。
> **本节保留的通用教训**：同一目标状态被两层代码各自推进一次 → 第二次命中非法转换守卫。**该反模式在三态模型下依然存在**（例如基类 `ConnectOn()` 与子类 `FlowProcess()` 都调 `SetState(Connected)`），规避动作不变：状态推进只允许一处负责。

#### 现象

初始化日志中出现 `非法状态转换: Initializing -> Initializing`，随后初始化立即失败，设备状态停留在 `Initializing` 而无法进入 `Standby`。

#### 根因

工作流层（`LineLaserWorkflow.Initialize()` / `InitializeSync()`）手动调用了一次 `_deviceStateMachine.TryTransition(DeviceState.Initializing, ...)`，而设备状态机模板方法 `_deviceStateMachine.Initialize()` 内部第一步也会调用 `TryTransition(DeviceState.Initializing, ...)`。两次转换同一个目标状态，第二次必然命中"非法状态转换"守卫，`Initialize()` 直接返回 false。

```
工作流层:  TryTransition(Initializing)   → 成功  Uninitialized → Initializing
模板方法:  TryTransition(Initializing)   → 失败  Initializing → Initializing（非法）
          Initialize() 返回 false        → 初始化失败
```

#### 修复

移除工作流层的重复 `TryTransition(Initializing)` 调用。设备状态机的 `Initializing → 四步初始化 → Standby/Alarm` 完整流程统一由 `DeviceInitializationStateMachineBase.Initialize()` 模板方法负责，工作流层只需要转换自己的工作流状态（`LineLaserWorkflowState`）。

**正确模式**：
```csharp
// 工作流层：只管工作流状态机
TransitionTo(LineLaserWorkflowState.Initializing);
// 设备状态机的 Initializing 转换由模板方法内部负责
InitializeWorker();  // 内部调 _deviceStateMachine.Initialize(...)
```

#### 预防措施

1. **职责分层**：工作流状态机（WorkflowState）和设备状态机（DeviceState）各司其职，工作流层不要越俎代庖操作设备状态机的初始化转换。
2. **代码审查**：新增初始化入口方法时，检查是否存在重复的状态转换。
3. **错误日志定位**：看到 `非法状态转换: X -> X` 时，第一反应就是找重复的 `TryTransition(X)` 调用。

> 相关：[[modules/DeviceControl]]、[[api/IntelligentLaserCam]]（原模块页 2026-09-17 并入）。
> 与坑一（执行步复位覆盖）同属「状态被后续代码/他人覆盖」一族，但机制不同。

### 七.2 CrossThreadNoStepAdvance（跨线程不推进执行步：RSI 报警 `_seamAlarmPending` volatile 标志范式）

> **语境**：CSP 焊缝跟踪的 X 折返报警在 **RSI 接收线程**（~83Hz）上判定；
> 而停机动作（`Fail()` → 状态转换 + `RunStep` 推进）属**设备流程线程**的职责。
> 直接在 RSI 线程里调 `Fail()` 会踩状态机并发双转换。落点：[[api/MotionControlWorkflow]]。

#### 现象

折返报警触发后偶发「非法状态转换」日志、设备状态停在中间态，或 `RunStep` 与 `WeldStatus` 不同步。

#### 根因

`Fail()` 内部会**同时**做两件事：写 `_phase` → 映射 `WeldStatus` → 复位 `RunStep`。
这些都不是原子操作。RSI 线程与流程线程并发进入 → **同一目标状态被两层各转一次**，
或读到「相位已改、执行步未改」的中间态。

> 这与本页七.1 是**同一反模式的两个来源**：
> 那里是「两层代码各推进一次」，这里是「**另一个线程**推进一次」。规避原则一致——**状态推进只允许一处负责**。

#### 范式：置标志 + 流程线程处置

```csharp
// RSI 接收线程 / 算法事件处理器：只置标志，不做任何状态推进
private volatile bool _seamAlarmPending;

private void OnSeamTrackingAlarmRequested(object sender, TrackingAlarmEventArgs e)
{
    _seamAlarmPending = true;          // 到此为止
}

// 设备流程线程（RunStep = StepReady 的执行步内）：唯一处置点
private void UpdateSeamTracking()
{
    if (_seamAlarmPending)
    {
        _seamAlarmPending = false;     // 先清后处置，防重入
        Fail(WeldParamManager.Instance.SeamTrackingAlarmReason);
        return;
    }
    ...
}
```

要点：

| # | 要求 | 原因 |
|---|---|---|
| 1 | 标志位用 `volatile bool` | 单字节读写本身原子，`volatile` 保证**可见性**（不需要 `lock`） |
| 2 | 订阅方**只置标志**，不传业务数据 | 报警原因等细节由被订阅方（算法）自持属性读取，避免跨线程搬运对象 |
| 3 | 处置点**唯一**且在执行步内 | 保证状态转换与 `RunStep` 推进在同一线程、同一拍完成 |
| 4 | 停止/断开路径要**清标志** | `DoStopping()` / `DetachSeamTrackAxis()` 内 `_seamAlarmPending = false`，否则上一段的残留报警会在下一段开焊瞬间触发 |
| 5 | 事件在**锁外**触发 | 订阅方回调若在发布方锁内执行 → 重入死锁（见 [[api/SeamMapTrackingAlgorithm]] `RaiseAlarmRequest`） |

#### 同族误区

- **用 `lock` 保护整个 `Fail()`**（否决）：只是把并发变成串行，**没有解决「谁有权推进」**；
  且流程线程等待 RSI 线程持锁 → 抖动增大。
- **在回调里直接改 `RunStep` 数值**（否决）：绕过状态门禁，出现与 `_phase` 不一致的执行步。
- **用 `Invoke`/`BeginInvoke` 切回 UI 线程处置**（否决）：状态推进的正确线程是**设备流程线程**，不是 UI 线程；
  切到 UI 线程只是换了个错的地方，还给 UI 加负担。

> 相关：[[api/MotionControlWorkflow]] — 落点（`OnSeamTrackingAlarmRequested` / `UpdateSeamTracking`）；
> [[api/SeamMapTrackingAlgorithm]] — 报警发布方（锁外 `RaiseAlarmRequest`）；
> [[decisions/ADR-013-ThreeStateModelRefactor]] — 状态写入唯一入口（`SetState`/`SetWeldStatus`）；
> ~~standards/StepDrivenWorkflow~~（已废弃，2026-09-17 删除）— 执行步驱动规范；
> [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — 决策。

### 七.3 DeviceControlWorkInheritanceBypass（继承绕过：子类重声明 Tag/Log 遮蔽基类 CS0108、日志出口发散）

> **来源**：2026-09-03 对 `MainDeviceControl/` 的一次完整性审计 + 修复，共 5 个 BUG、8 个文件、约 63 处日志调用改造。
> 规范正文见 [[architecture/DeviceControlArchitecture]] 与 [[standards/CodeSimplification]] §三（⛔ ~~standards/StepDrivenWorkflow~~（已废弃，2026-09-17 删除））。本节只记**踩过的坑**与规避动作。
>
> **⚠️ 2026-09-03 机制变更（ADR-012，用户裁定「完全重构」）**：本节记录的 5 类 BUG 与「独立管控类另起炉灶会腐化」的**根因继续有效**，
> 但正文中的成员名已随旧框架清除（裁定 C1/C6）：`GoStep` → **`RunStep` 由 `case` 内 bool 推进**；`IsStepTimeout` → **`TimeOutSeconds`（秒）**；
> `FailFlow` → 超时后 Alarm + RecordFault + 跳 9xx 段；`ResetStepTime` → **`ResetWorkTime()`**。
> 另：`DeviceControlWork` **仍不继承** `DeviceWorkflowBase`（新架构下它是 7 线程编排层，与基类职责本就不同），
> 因此**本节「抄一份会腐化」的警示完全适用**，改码时须让它的步机制与基类保持同步演进。
> 现行规范见 [[architecture/DeviceControlArchitecture]] §4 · §5 · §7.2 · §16。

#### 一句话根因

> **独立管控类（`DeviceControlWork` / `DeviceStatusWork`）不继承 `DeviceWorkflowBase`，于是把基类机制「抄」了一份私有实现。
> 抄的那份会随基类演进而腐化——基类后来补的正确性保障（原子读写、非运行态刷新时间戳）永远传导不过去。**

这是「子类重复基类功能导致继承失效」反模式的一个变体：**不是继承后重写覆盖，而是压根不继承、另起炉灶**。
前者至少还能被 `base.` 拉回来，后者连编译期关联都没有，审计时极易漏掉。

#### 坑一：子类 `private const string Tag` 遮蔽基类 `public object Tag` → CS0108 + 类型对撞

##### 现象

`MotionControlWorkflow` 常量区有：

```csharp
private const string Tag = "运动控制工作流";   // 基类已有 public object Tag
```

基类 `DeviceWorkflowBase` 提供 `public object Tag { get; set; }`。两者同名 → 编译器报 **CS0108**（`Tag` 隐藏继承成员）；
更要命的是**类型冲突**：基类是 `object`，子类是 `string`，任何经基类引用访问 `Tag` 的代码拿到的都是另一个东西，多态语义彻底失效。

##### 根因

`Tag` 是 `raw/architecture/主控设计.xlsx` 列为**基类契约成员**的字段，但全库 **0 消费者**——
5 个子工作流实际都靠 **`private readonly string _tag` + 抽象属性 `StateName`** 承担日志标识，`Tag` 被架空。

审计时第一反应是「0 消费者 = 死成员，删掉」。**这个判断是错的**，被用户当场纠正：

> `Tag` 的作用我来说明，你沉淀进去：每个流程应该还需要增加 log 的统一写法，**tag 是给 log 用的**。
> 另外两个主设备 `StartWork` 也需要有统一的 log。这里的 log 写法是**将 comm 的 ShowLog 写法封装**。

##### 规避（硬约束）

1. **`Tag` 不是死成员，是日志标签的真相源**——保留并收紧为 `public string Tag { get; protected set; }`（`object` → `string`，setter 降为 `protected`）。
2. **子类禁止再声明任何 `Tag` / `_tag` 同名成员**；日志标签只能在构造函数里给基类属性赋值：`Tag = "线激光工作流";`。
3. 每个流程与管控类**必须有且只有一个日志出口**（`GlobalCommData.ShowLog` 直连，无中间封装）。见 [[api/GlobalCommData]]。
4. **判据**：审计报「0 消费者」时，先问「它是不是某种横切关注点的载体（日志/权限/序列化）」，
   不要直接下「死成员」结论——尤其当 `raw/` 原档把它列为契约成员时。

> 同类问题另见本页七.6 坑二（下沉 `protected const` 后子类残留同名定义 → CS0108）。

#### 坑二：日志出口发散 —— 63 处 `ShowLog` 各写各的标签

##### 现象

改造前 `MainDeviceControl/` 共 **63 处** `GlobalCommData.ShowLog`，标签来源四套并存：

| 写法 | 使用者 |
|---|---|
| 私有 `readonly string _tag = "..."` | 4 个子工作流 |
| 私有 `const string Tag = "..."`（遮蔽基类） | `MotionControlWorkflow` |
| 抽象属性 `StateName` | `DeviceStateBase` |
| 私有 `_tag` / `_simTag` | `DeviceControlWork` / `DeviceStatusWork` |

后果：标签拼写无约束、级别默认值不统一（`MessageLevel.Info` 有的省略有的显式）、
新增流程时「照抄一个 `_tag`」成为默认动作，进一步加剧发散。

##### 规避（硬约束）

曾新建 `DeviceLog` 静态类作唯一出口（**2026-09-04 按用户裁定移除**——新架构未要求中间层），现行=直连 `GlobalCommData.ShowLog` + 标签约定：

| 角色 | 标签来源 | 调用写法 |
|---|---|---|
| 子工作流 | 基类 `Tag` | 基类 `protected void Log(string message, MessageLevel level = MessageLevel.Info)` |
| 独立管控类 | 私有 `_tag` | 本类私有 `Log(...)` → `GlobalCommData.ShowLog(_tag, ...)` |
| 状态基座 | `StateName` | `GlobalCommData.ShowLog(StateName, ...)` |
| 模拟模式 | `_simTag` | `GlobalCommData.ShowLog(_simTag, ...)` |

**验收口径（可用 grep 自检）**：

```
MainDeviceControl/ 下无 DeviceLog 中间类（仅剩 C7 契约 `SubDeviceLog` 抽象名）；日志直连 `GlobalCommData.ShowLog`
```

设备日志直连 `GlobalCommData.ShowLog`；**通讯收发报文仍走 `GlobalCommData.ShowCommunicationLog`，二者不得混用**
（连接 `open`/`close` 归设备日志，报文 `content`/`stop` 归通信日志）。

#### 坑三：`long` 时间戳裸读写 —— 32 位平台非原子

##### 现象

```csharp
_workStartTicks = DateTime.Now.Ticks;                       // 写
var start = new DateTime(_workStartTicks);                  // 读
```

`_workStartTicks` 是 `long`。**32 位平台上 `long` 的读写不保证原子性**，可能被拆成两次 32 位操作。
运行线程写、UI/排故/监控线程读，读到「高 32 位新 + 低 32 位旧」的撕裂值 → `DateTime` 构造出一个荒谬时间，
`IsStepTimeout` 直接误判。

> 本机目标框架是 .NET Framework 4.8、平台目标 x64，但**依赖「当前是 64 位」来保证正确性是脆弱假设**——
> 同一份代码被 AnyCPU 编译或部署到 32 位运行环境时即失效，且失效表现为**偶发**，极难复现。

##### 规避（硬约束）

```csharp
Interlocked.Exchange(ref _workStartTicks, DateTime.Now.Ticks);   // 写
new DateTime(Interlocked.Read(ref _workStartTicks))              // 读
```

**判据**：跨线程共享的 `long`/`double`/`decimal` 字段（时间戳、计数器、累计量），
一律用 `Interlocked` 或锁，不允许裸读写。`bool`/`int`/引用类型才是天然原子的。

> 相关：[[lessons/CSharp-Language-Pitfalls]] §3.5 泛型类型参数不能声明 `volatile`（CS0677）——
> 想用 `volatile long` 也不行，只能走 `Interlocked`。

#### 坑四：`_status` 字段直读绕过 `Status` 属性的锁（8 处）

##### 现象

`DeviceControlWork` 同时有：

```csharp
private MainDeviceStatus _status;
private readonly object _statusLock = new object();
public MainDeviceStatus Status { get { lock (_statusLock) { return _status; } } }
```

但有 **8 处**业务代码图省事直接读 `_status`：

```csharp
if (_status != MainDeviceStatus.Stop || !_pendingPreWeldRequest) return;   // DoIdle
if (_status != MainDeviceStatus.Running)                                   // OnPoseArrived
if (_status != MainDeviceStatus.EStop && _status != MainDeviceStatus.Alarm) // StartMachine
```

`Status` 属性上的锁形同虚设——**加锁和不加锁的读混用，等于没加锁**。
`SetStatus` 在锁内改，直读方在锁外读，可能读到撕裂/陈旧值，状态门控在竞态窗口内失效。

##### 规避（硬约束）

- **除 backing field 声明、属性 getter、`SetStatus` 锁内写块外，任何位置不得出现裸 `_status`**。
- 全部改走 `Status` 属性。
- **例外（必须保留裸读）**：`ClearAlarm` 里的「检查 + 写入」必须在**同一把锁内**完成（TOCTOU），
  写成 `if (Status != Alarm) return; SetStatus(...)` 会拆成两次加锁，中间可插入其他写入。

**自检**：

```bash
grep -n "_status" AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs
# 合法残留仅 5 处：110 声明 / 111 锁对象 / 199 getter / 375-379 SetStatus 锁内块 / 1304-1306 ClearAlarm 锁内块
```

> 通用判据：**字段有配套锁 ⇒ 该字段在锁外出现的每一处都是 BUG**，无一例外。

#### 坑五：重造的私有步机制缺了基类两处保障 → 停机再启动首拍误判超时

##### 现象

`DeviceControlWork` 不继承 `DeviceWorkflowBase`，于是自己抄了一套步机制：
`private GoStep` / `private IsStepTimeout` / `private FailFlow` / `private GetStepName` / 步号常量。
抄的版本**缺了基类后来补的两处正确性保障**：

| 基类 `DeviceWorkflowBase` | 抄到 `DeviceControlWork` 的版本 | 后果 |
|---|---|---|
| `RunLoop` 非运行态 `else { ResetStepTime(); }` | **无 else 分支** | 停机期间时间戳冻结在停机时刻 |
| `Interlocked.Exchange` / `Interlocked.Read` | 裸赋值/裸读（见坑三） | 32 位平台撕裂 |
| `ResetStepTime()` 公有可外部调用 | 无 | 无法在 `StartMachine` 里主动复位 |

**故障链**：停机 5 分钟 → `StartMachine()` 拉起线程 → 首拍 `IsStepTimeout(PoseWaitTimeoutMs)` 用**停机时刻**的时间戳计算 →
`5 min > 60 s` 直接判超时 → 跳 900 失败收尾。**现场表现为「停机久了再开机，一开机就报流程超时」。**

##### 根因

旧标准（已废弃，现行 [[architecture/DeviceControlArchitecture]] §5）早已把「非运行态必须持续 `ResetStepTime()`」写为**关键细节（易漏）**，
§七「暂停/非运行态」、§十一审查清单也都列了这一条。

——**但那条规范只对继承基类的工作流生效。** `DeviceControlWork` 是独立管控类，
抄了一份实现就游离在规范覆盖范围之外，**规范写得再全也传导不过去**。

##### 规避（硬约束）

1. `RunLoop` 必须补上非运行态分支：

   ```csharp
   if (_running) { ConsumeCommand(); FlowProcess(); }
   else { ResetStepTime(); }   // 非运行态持续刷新，防止恢复瞬间误判超时
   ```

2. `StartMachine()` 内显式 `GoStep(StepIdle)` 复位步号与时间戳——**重启一律从待机步起算**。
3. **审计新判据**：独立管控类若出现与基类同名的私有机制（`GoStep`/`IsStepTimeout`/`FailFlow`/`GetStepName`/`ResetStepTime`），
   逐成员比对两者实现差异，**差异处即为腐化点**，不得默认「抄的时候是一样的」。
4. 长期方向：把这套机制抽成可组合的组件（而非只能靠继承获得），让独立管控类也能复用同一份实现。

> 同源红线见 [[architecture/DeviceControlArchitecture]] §5（单步内禁止无界阻塞等待）与
> 原步骤驱动决策。本坑说明：**规范围不住「抄代码的人」**。

#### 本次修复清单（验收用）

| # | BUG | 修复 | 文件 |
|---|---|---|---|
| 1 | 子类 `const string Tag` 遮蔽基类 `Tag`（CS0108） | 基类 `Tag` 收紧为 `public string { get; protected set; }`；子类删遮蔽声明，构造函数首行赋值 | `DeviceWorkflowBase.cs` + 5 个子工作流 |
| 2 | 日志出口发散 63 处 | 直连 `GlobalCommData.ShowLog` + 统一标签（曾建 `DeviceLog` 中间类，2026-09-04 按裁定移除） | `DeviceLog.cs` 删除，8 文件改直连 |
| 3 | `long` 时间戳裸读写 | `Interlocked.Exchange` / `Interlocked.Read` | `DeviceControlWork.cs` |
| 4 | `_status` 直读绕过锁（8 处） | 全部改走 `Status` 属性（保留 `ClearAlarm` 锁内 check-and-set） | `DeviceControlWork.cs` |
| 5 | 停机再启动首拍误判超时 | `RunLoop` 补 `else ResetStepTime()`；`StartMachine` 内 `GoStep(StepIdle)` | `DeviceControlWork.cs` |

**附加**：移除 `LaserWeldHeadWorkflow.cs` 中因改造而失效的 `using AdaWeldSystem.Comm;`。
**用户裁定**：其余 0 消费死成员（`CheckDeviceIOSafe()` / `IsStepTimeout()` 无参重载 / `StepStatusText` / `WorkElapsedMs`）**一律保留不删**——
可观测性 API 的 0 消费不构成删除理由。

> 关联：[[api/GlobalCommData]] — 设备日志直连出口（标签约定另见 [[standards/CodeSimplification]] §三⑤）；
> [[standards/CodeSimplification]] §三 — 设备日志规范（内容无符号、记录时机、通讯全记录）；
> [[api/DeviceControlWork]] — 主设备运行管控（坑三/四/五 的现场）；
> [[lessons/CSharp-Language-Pitfalls]] — C# 语言层陷阱合集；
> [[decisions/ADR-013-ThreeStateModelRefactor]] — 三态模型与独立管控类定位；
> [[architecture/DeviceControlArchitecture]] §2 — 独立管控类为何不在继承链上；
> 本节七.4 — 另一条关于「调用方入口」的红线；
> 本节七.6 — CS0108 的另一形态（常量下沉后子类残留）。

### 七.4 DeviceWorkflowDualFlowCallerGate（双流程调用方门控）

#### 坑

驱动任一 `DeviceWorkflowBase` 子类（各子设备工作流）时，
**必须走基类提供的公共入口**，禁止直接调子类自身暴露的同名便捷方法：

| 应调用（基类入口） | 禁止调用（子类内部方法） | 后果 |
|---|---|---|
| `ConnectOn()`（开启连接，public abstract，受理式，UI 直调） | 内部编排方法（如连接后台线程方法） | 绕过受理式置态与连接语义 |
| `ConnectOff()`（断开连接，public abstract，UI 直调） | 内部断开方法 | 绕过断开置态语义 |
| `ResetProcess()`（流程复位） | 子类自有便捷方法 | 复位口径不一致 |
| `ClearStatus()`（清报警回待机） | 子类自有便捷方法 | 报警态清理遗漏 |

> **⚠️ 2026-09-03 机制变更（ADR-012，用户裁定「完全重构」）**：
> ① 「自动运行由**常驻监听线程**驱动」已废止（裁定 C1）——子流程**无自带线程**，改由 `DeviceControlWork` 的 7 条常驻线程驱动 `FlowProcess()`；
> ② `ConnectOn()` / `ConnectOff()` 现归**非阻塞组**（非常驻后台线程，动作即退出释放）；新原档另有一组**阻塞**接口
> `InitializeOn()`（同步等待）/ `InitializeOff()`（异步等待），**两组并存不重叠**（裁定 C4，架构页 §4.4）；
> ③ 「后台常驻线程由子类内部自起」同样废止——子类不起常驻/长生命周期线程；短生命周期线程（如 `ConnectOn/ConnectOff` 内 `new Thread(IsBackground=true)` 动作即退出释放）允许，但须 `finally` 中释放资源与标志。
> **本节「必须走基类公共入口、禁止直调子类便捷方法」的红线本身继续有效**，且新增：禁止直调 `InitializeOn/Off`。
> 现行规范见 [[architecture/DeviceControlArchitecture]] §4.2 · §4.3 · §4.4 · §7.2。
>
> ~~自动运行无独立入口：自动运行 = 仅 `FlowProcess()`，由常驻监听线程驱动；~~
> **自动运行 = 仅 `FlowProcess()`，由 `DeviceControlWork` 的常驻线程驱动**；
> 主设备 `DeviceControlWork` 在其单步分派中级联子设备（如启动焊接步内 `_lineLaser` 相应动作）。

`ConnectOn()`/`ConnectOff()` 为 `public abstract`，是连接/断开的唯一契约，**界面 UI 开关按钮直调**，由子类内部自起**短生命周期线程**完成（`IsBackground=true`，`finally` 释放 `_manualBusy` 等标志，基类不包线程、不设看门狗）——此属允许的短生命周期线程，非「常驻监听线程」红线；直接调子类内部方法会跳过受理式置位。

#### 踩坑实录

- 2026-09-01 审计：顶层调用方 `FormMain.cs` 曾直接调 `PowerOnInitialize()` + `Start()`，绕过基类入口。
- 2026-09-02 收敛：`PowerOnInitialize` 收敛为私有初始化编排（自动初始化共用实现），外部无第三入口。
- 2026-09-02 再收敛：删除「手动初始化/反初始化」`BeginManualInit`/`BeginManualUnInit`，仅保留「手动连接/断开」入口（升抽象）。
- 2026-09-02 三度收敛：删除基类 `ManualStart`/`ManualStop` 中间包装（原「基类起线程再调子类」线程套线程、流程套流程）；连接/断开升为 `public abstract`，后台线程由子类内部自起，UI 按钮直调。
- 2026-09-02 ADR-034 三态模型定稿：基类泛型 `DeviceWorkflowBase<TStep>` 删除，连接/断开入口定名 **`ConnectOn()`/`ConnectOff()`**（原 `ManualOn`/`ManualOff` 废止）；初始化/启动收口为 `DeviceControlWork.InitializeMachine()` / `StartMachine()`。
- 2026-09-01 同轮修正 `MotionControlPage.cs`：**越权直驱非所属设备**——直接调 `LineLaserWorkflow.Instance` 的初始化/启停方法
  （线激光属线激光/ILCamPage 边界，且其模拟生命周期应由主设备统一编排）。
  已将线激光模拟启动/停止/复位上收至 `DeviceControlWork`（见 ADR-034），`MotionControlPage` 仅经这些方法触发，并**订阅事件 + 读状态消费结果**。
- 2026-09-02 修正 `MainPage.cs`：**主页面线激光设备开关按钮**直接调线激光流程的运行方法，
  三重违规——(1) 调子类便捷方法而非连接契约入口；(2) 语义错误，把「连接设备」实现成「开激光跑焊接流程」；
  (3) `MainPage` 属主设备边界，线激光非其所属设备，越权直驱。
  已改为**基于连接态判断**：`Disconnected` → `ConnectOn()`，`Connected` → `ConnectOff()`。
  徽标判定同步改为按连接态/焊接过程态判定（连接语义，与开关一致）。
- `ILCamPage.cs` 经核查为**正确调用**：仅用 `ConnectOn()`/`ConnectOff()`（public 连接/断开入口）驱动线激光连接/断开，
  线激光状态通过 `StateChanged`/`WeldStatusChanged` 事件与业务状态消费，无越权直驱。

#### 第二条红线：UI 页设备归属边界

> 一个 UI 页只可**直接驱动其自身所属设备**的工作流；对**非所属设备**只能**消费结果**（订阅 `StateChanged`/`WeldStatusChanged` 事件、读取 `State`/`WeldStatus`/业务状态），
> 不得越权直调其 `ConnectOn`/`ConnectOff`/`ResetProcess`。
> 非所属设备的驱动应上收到**归属编排方**——模拟流程统一由 `DeviceControlWork` 编排，因其级联拥有线激光子设备且「模拟由主设备统一管理」。
>
> 例：`MotionControlPage`（运控页）属 `MotionControlWorkflow`（V3 跟踪）→ 可直驱 `MotionControlWorkflow`；
> 线激光（`LineLaserWorkflow`）不在其归属内 → 必须经 `DeviceControlWork` 模拟编排入口，不得直驱线激光内部方法。

#### 红线（结论）

> 工作流的「驱动开关」只认基类入口；且**驱动权按设备归属划分**：UI 页只直驱自身设备，非自身设备只消费结果、由归属编排方编排。
> 子类暴露的内部启停方法不是对外驱动入口（对外连接/断开用 `ConnectOn`/`ConnectOff`）。
> 新增调用点前先确认：(1) 用的是 `ConnectOn/ConnectOff/ResetProcess/ClearStatus`；(2) 该设备确属本页/本调用方。

### 七.5 HighResolutionThreadScheduling（1ms 高精度线程调度经验）

> ⛔ **机制失效声明（2026-09-16 治理，ADR-042，沿用原页横幅）**：本节描述的**独立 1ms 高精度输出线程已删除**。
> CSP 目标写入改由 [[api/MotionControlWorkflow]] 的 `FlowProcess` CSP 分支**按拍推进**（`#region CSP 步骤输出`，运行态 10ms/100Hz）：
> 不再有 `ThreadPriority.Highest` / 绝对目标时刻漂移校正 / `Sleep`+自旋 / `Join` 这一整套线程设施；
> `SEAM_GUIDE/CYCLE_TIME_MS` 配置项亦已删除，dt 全取**实测**（`TakeCspElapsedSeconds()`）。
> **不得据本节恢复线程方案**；已失效细节（四件套历史结构、`SleepToCspTick`、`CspOutputLoop` 等）见原页存档与 ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。

以下仅收录**仍有效（✅）的通用经验**：

**四件套中仍有效项**：

1. **`timeBeginPeriod(1)` 是前提**——把系统计时器分辨率从默认 15.6ms 提到 1ms，不调则高精度节拍全白搭。
   `DllImport("winmm.dll")`，**调用时调、退出时 `timeEndPeriod(1)` 配对归还**。
   ADR-042 后仅调用时机改变：**起焊沿 `StartCspOutput()` 调用、停焊沿 `StopCspOutput()` 归还**（不再挂线程起停，空闲期不占高分辨率）。

**必须配的防护中仍有效项**：

2. **`timeEndPeriod` 必须配对归还**（仍有效）：调用点在 `StopCspOutput()` 内，与起焊沿 `TimeBeginPeriod(1)` 严格配对。
3. **急停必须每拍检查**（仍有效，且已加强）：`OutputCspTick()` 每拍查 `MontionManager.Instance.MontionControl.EmergencyStop`。
   不检查的后果依然严重：驱动器已停机、程序仍在写目标 → **重新驱动轴**。ADR-042 另加编排层 `Current != Running` 门控作**双保险**。
4. **热路径日志必须限频**（仍有效）：按拍（100Hz）打日志同样会压垮 UI 与磁盘。做法——保存 `_lastErrorCode` + `_lastErrorLogTime`，
   **同错误码 1s 内只记一次**（不同码立即记）。参见 [[decisions/ADR-007-CodeSimplificationStandard]]。

**边界（务必上机验证）**：

- **「逼近」不是「保证」**：~~1ms~~ → **10ms** 同样受 CPU 负载、电源策略、其他进程影响。**真机实测节拍分布为验收项**，不能凭代码推断。
- **抖动只能被吸收、不能被消除**：ADR-042 后 dt 全取**实测**并两端钳位 `[0.001, 0.1]s`，**限幅量纲随实测值自适应、无需重算**——
  把调度事实交回调度层，工艺参数不再承担调度职责，比「手工抬周期 + 重算参数」更稳。
- **`timeBeginPeriod` 是全局副作用**：它会抬高**整个进程**的计时器分辨率、增加功耗。故必须成对调用、及时归还；
  ADR-042 把生效区间进一步收窄到**起焊沿 → 停焊沿**，空闲期不再占用高分辨率计时器。

> 现行结构：`OutputCspTick()` 每拍调一次、无循环、无睡眠、无句柄（现行代码见 [[api/MotionControlWorkflow]] 的 `StartCspOutput` / `OutputCspTick` / `TakeCspElapsedSeconds` / `StopCspOutput`）。
> 相关：[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — 原始决策（原页为其线程方案的即时经验沉淀）；
> ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — **现行决策**（撤销线程、并入流程步骤）；
> api/ICspMotion — 被调用的热路径契约；[[modules/MotionControl]] — 模块；
> [[architecture/DeviceControlArchitecture]] — §5 `RunStep` 驱动（子设备线程节拍来源）；
> 步骤驱动红线（`case` 内禁阻塞）见本页坑二与七.6。

### 七.6 StepMemberNameCollision（步号常量与单步方法同名 CS0102、常量下沉 CS0108）

> 来源：2026-09-01 步骤驱动改造**落地后的第二轮精简审查**。
> 上一轮改造把 8 个 workflow 全部改成「常量步号 + 同名单步方法」的写法，本轮审查才发现这套写法**根本编译不过**。
> 规范正文见 [[architecture/DeviceControlArchitecture]] §5（⛔ ~~standards/StepDrivenWorkflow~~（已废弃，2026-09-17 删除））。

> **类名与规模注记（2026-09-02，ADR-034）**：文中「8 个 workflow」现为 **7 个**——5 个子设备工作流（`LineLaser`/`MonitorCamera`/`MotionControl`/`WeldParamControl`/`LaserWeldHead`）+ `DeviceControlWork` + `DeviceStatusWork`；`SafetyWorkflow` 现为 `DeviceStatusWork`（其 `StepAlarm = 900` 与 `DoAlarm()` 已随三线程模型移除）；`MainDeviceWorkflow` 现为 `DeviceControlWork`。**CS0102 同名冲突的规避动作继续有效**。
>
> **🔥 2026-09-03 新增实战案例（裁定 C6，改码前必看）**：按新原档把 `WorkStep` 改名为基类属性 **`RunStep`** 时，
> `LineLaserWorkflow.cs` 中**已存在** `private bool RunStep(Func<bool>, string, string)` 方法 → 新增属性 `RunStep` 直接触发
> **CS0102（同类成员重名）**。这是本节坑一的同型案例，**批次 1 改码第一步必须先给该方法改名**（建议 `RunStepGuard` / `ExecuteStep`），
> 否则全项目编译失败。同理 `StepWorkTime` / `TimeOutSeconds` 落地前也要先在 5 个子类里 grep 同名成员。
> 现行规范见 [[architecture/DeviceControlArchitecture]] §4.1、§16.3。

#### 坑一：`const int StepXxx` 与 `void StepXxx()` 同一作用域 → CS0102

##### 现象

按直觉给每一步写一对「常量 + 方法」，二者同名：

```csharp
private const int StepPreWork = 10;

private void StepPreWork()      // CS0102：类型已包含同名成员定义
{
    ...
}
```

C# 的常量、字段、方法、属性、事件**共享同一个成员命名空间**，不存在「常量名与方法名互不干扰」这回事。

##### 影响面

本次实测：6 个 workflow 共 **27 处**同名冲突（`LineLaser` 9 / `MotionControl` 7 / `MonitorCamera` 5 / `WeldParamControl` 4 / `SafetyWorkflow` 2）。
**整个 `MainDeviceControl` 改造后处于无法编译状态**——而改造当时只做了 Grep 与人工核对，没人编译（本项目在本环境无法编译，见 [[guides/Namespace-Compilation]]）。

##### 根因

命名时把「步号（数据）」与「动作（行为）」当成了两个维度，实际 C# 只认一个成员表。

##### 规避（硬约束）

**步号常量 `StepXxx`，单步方法 `DoXxx()`，分派处 `case StepXxx: DoXxx(); break;`**

选 Do 前缀而非改常量名（Ws 前缀）或嵌套 `Steps` 静态类的原因：

| 方案 | 改动面 | 取舍 |
|---|---|---|
| **方法加 `Do` 前缀** | 只碰 `private` 方法名，无外部依赖 | ✅ 采纳 |
| 常量改 `Ws` 前缀 | 常量在 `case`/`GoStep`/`GetStepName` 三处出现，改动面×3 | 放弃 |
| 嵌套 `static class Steps` | 每个引用点都要加 `Steps.` 前缀，且段位表可读性下降 | 放弃 |

##### 检索自检命令

改完必须跑（去注释后比对常量名与方法名）：

```bash
python - << 'EOF'
import io, re, glob
for p in glob.glob("MainDeviceControl/**/*.cs", recursive=True):
    code = re.sub(r'//[^\n]*', '', io.open(p, encoding="utf-8-sig").read())
    consts = set(re.findall(r'\bconst\s+int\s+(\w+)\s*=', code))
    methods = set(re.findall(r'\b(?:void|bool|int|string|double|DeviceState)\s+(\w+)\s*\(', code))
    if consts & methods:
        print(p, sorted(consts & methods))
EOF
```

#### 坑二：下沉 `protected const` 后，子类残留同名定义 → CS0108

##### 现象

把 8 个流程各抄一份的 `StepIdle=0` / `StepFinishOk=800` / `StepFinishFail=900` 下沉到基类后，若忘记删子类里的旧定义：

```csharp
// 基类
protected const int StepFinishFail = 900;

// 子类残留
private const int StepFinishFail = 900;   // CS0108 警告：隐藏继承成员
```

##### 规避

下沉后**必须**全目录扫一遍重复定义：

```bash
grep -rn "StepFinishFail\s*=\|StepFinishOk\s*=\|StepIdle\s*=" AdaWeldSystem/MainDeviceControl
```

预期输出**只剩基类的 3 行**。子类里出现即未清理干净。

同理，`_failReason` / `_failStep` 字段与 `FailFlow()` 方法在 5 个文件各有一份实现，一并下沉基类后，子类改读基类的 `FailReason` / `FailStep` 只读属性。

##### 语义合并注意

`SafetyWorkflow` 原本有自己的 `StepAlarm = 900`。安全流程没有 800 成功段，报警收尾与失败收尾语义重合，**直接并入基类 `StepFinishFail`**，方法名保留领域语义 `DoAlarm()`。
→ 教训：**下沉常量时要检查「同值不同名」的常量，它们往往是同一语义的两套叫法。**

#### 坑三：反向问题——`DeviceControlWork`（原 `MainDeviceWorkflow`）一个常量都没有

与其余 6 个流程相反，主设备流程改造后**0 个步号常量**，`GoStep(10)` / `case 800:` 全是魔法数字。

**教训**：审查不能只盯「报错的那类问题」。同名冲突是硬错误、会报警，而魔法数字不报错、只能靠人工比对发现。
→ 落地后应对**整组文件做横向一致性检查**（有没有常量、常量命名是否统一、`case` 是否写常量），而不只是跑一遍报错扫描。

#### 坑四：`csharp_review.py` 把形参表与对象初始化器误判成字段

##### 现象

成员顺序检查报出「字段 private string message, MessageLevel level 出现在更高顺序区域之后」，但该文件成员顺序其实完全正确。

##### 根因

`FIELD_RE` 依赖「修饰符 + 类型 + 名称 + `;`」匹配，两类非字段文本被误吃：

1. 方法形参表 `private void Log(string message, MessageLevel level = MessageLevel.Info)` → 伪字段「`private string message, MessageLevel level`」
2. 属性体内的对象初始化器 `new MonitorResult { Phase = _result.Phase, ... }` → 伪字段「`private _result.Phase, Pass`」

伪字段访问级 `private`（顺序 1）落在方法（顺序 4/5）之后，于是假报「顺序破缺」。

##### 规避

已在 `scripts/csharp_review.py` 新增 `_drop_pseudo_fields()`：凡落在任一方法或属性行区间内的「字段」一律剔除（C# 不允许在方法体/属性体内声明字段，此过滤无副作用）。

→ **通用教训**：lint 报「成员顺序错误」时，先确认报错的那个「字段」在源文件里真的存在；名字里带 `,` `.` 或空格的，基本都是解析器误读。

#### 坑五：批量移动多行属性时，块边界识别不全 → 文件结构被拆散

##### 现象

写脚本把 `IsRunLoopActive` 属性从尾部 region 移到「公共变量」区，单行表达式体（`{ get { return _running; } }`）搬对了，多行体（`{ get { ... } }` 换行展开）**只搬走了签名行**，`{ get {...} }` 被留在原 region，文件结构直接损坏。

##### 根因

判定块结束的 brace 计数从签名行起算，而多行体的签名行本身不含 `{`，计数为 0 立即判定「块已结束」。

##### 规避

1. 签名行无 `{` 时，**先向下推进到含 `{` 的行再开始计数**。
2. 批量移动成员后，**必须立刻 `sed -n` 抽查首尾两处**，确认没有产生孤立的 `{ ... }` 残块。
3. 更稳的做法：批量改动前先 `tar.gz` 备份，出问题直接回滚重做——比就地修补更省时间。

> 关联：规范见 [[architecture/DeviceControlArchitecture]] §5；精简见 [[standards/CodeSimplification]]；模块见 [[modules/DeviceControl]]；决策见 [[architecture/DeviceControlArchitecture]]。

### 七.7 以上六页原文件名与坑号对照表

| 原页名 | 原坑主题 | 并入后子节号 |
|---|---|---|
| lessons/StateMachine-DoubleTransition | 状态机重复转换：模板方法与工作流层双重转换 | 七.1 |
| lessons/CrossThreadNoStepAdvance | 跨线程不推进执行步：RSI 报警 `_seamAlarmPending` volatile 标志范式 | 七.2 |
| lessons/DeviceControlWorkInheritanceBypass | 继承绕过：Tag 遮蔽 CS0108、日志出口发散、时间戳非原子、字段直读绕锁、停机重启误判超时 | 七.3 |
| lessons/DeviceWorkflowDualFlowCallerGate | 双流程调用方门控：基类公共入口红线 + UI 页设备归属边界 | 七.4 |
| lessons/HighResolutionThreadScheduling | 1ms 高精度线程调度（⛔ 2026-09-16 起随独立线程移除失效，仅通用经验有效） | 七.5 |
| lessons/StepMemberNameCollision | 步号常量与单步方法同名 CS0102、常量下沉 CS0108（含脚本误报与块边界两则） | 七.6 |

## 相关页面

- [[lessons/StepDriven-SixPitfalls]] —— 同源拆分页
- [[lessons/StepDrivenWorkflowPitfalls]] —— 源页（拆分前全量）
