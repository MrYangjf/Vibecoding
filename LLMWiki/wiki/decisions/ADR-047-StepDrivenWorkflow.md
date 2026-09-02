---
title: ADR-047 步骤驱动工作流模型
date: 2026-09-01
tags: [决策, 架构, 工作流, 步骤驱动, WorkStep, GoStep, 命令变量, 监听线程, 可观测性, ADR-047]
status: accepted
---

> ⚠️ **已被取代（2026-09-02）**：本 ADR 的步骤驱动机制保留，但其「阶段态枚举对外暴露 + `MapToDeviceState` 四态映射」被新主控设计三态模型（`SubDeviceWeldStatus` + `SetWeldStatus`）取代，详见 [[decisions/ADR-049-ThreeStateModelRefactor]]。本页保留作历史参考，不再作为现行约束。

# ADR-047：步骤驱动工作流模型（命令变量 + 监听线程 + int 执行步）

## 背景

用户提供外部参考实现（项目 `HonorMachineTest`，`PcomDeviceInterface/Work/Process/`）：

- `StationProcess.cs` —— 抽象基类，承载 `WorkStep`（int 工作步数）、`WorkStartTime`（步进入时间）、轴/气缸动作原语（统一 `bool` 返回供短路）、6 个抽象契约（`FlowProcess` / `ResetProcess` / `ClearStatus` / `ResetWorkTime` / `ClearProduct` / `LoadConfig`·`SaveConfig`）。
- `AssemblyProcess.cs` —— 具体实现，`FlowProcess()` 内 `switch (WorkStep)` 分派上百步，每次改步必同步刷新 `WorkStartTime`，每步自带超时分支。
- `MachineControlWork.cs` —— 每流程一条常驻线程 `while(!IsClose) { XxxProcess.Instance.FlowProcess(); Thread.Sleep(10); }`。

该写法的收益：**主程序加载流程后，仅凭「步骤数字 + 进入时间」两个变量即可完全监控流程状态**（UI 显示 `工位：RUNNING / step:213 / 3.4s`，卡死时步号不动、时长持续涨）。

对照 AdaWeldSystem 现状的 `MainDeviceWorkflow`：事件驱动（`GlobalCommData.CommunicationCommandReceived` 回调内直接驱动状态机）、无常驻线程、状态控制全靠 `SetStep()` 转移 8 个阶段态——**能看出"在哪一态"，看不出"卡在哪一步、卡了多久"**，且无超时自愈能力。

## 决策

采纳**步骤驱动（Step-Driven）**模型，但**不照搬**、与既有架构三层并存：

1. **命令变量取代事件内直接处理**：通讯层回调只给一个 `_pendingCommand` 变量赋值；业务一律在常驻监听线程内执行。
2. **每流程一条常驻监听线程**：`while(!closing) { 消费命令变量 → FlowProcess() → Sleep(节拍) }`；非运行/暂停态每拍调 `ResetStepTime()` 刷新时间戳。
3. **新增「执行步」层 `WorkStep`(int) + `WorkStartTime`(DateTime)**：`switch` 分派，改步必成对刷新时间，每步自带超时分支，超时走「置 Alarm + 记故障 + 跳 9xx 收尾」。
   **改步一律经 `GoStep(n)` 方法**（基类 protected，内部同步刷新步号 + 时间戳 + 记日志），**禁止直接给 `WorkStep` / `WorkStartTime` 赋值**——以机制而非约定保障「成对刷新」（2026-09-01 落地时用户选定）。
4. **三层并存，不是替换**：
   - 设备四态 `State`（Disconnect/Connect/Work/Alarm）—— 经 `MapToDeviceState()` 映射，ADR-041 不变；
   - 阶段态 `Step`（`TStep` 枚举，7~9 态）—— 经基类 `SetStep()` 变更，ADR-042/043 不变，**对外语义与 UI 判断仍以此为准**；
   - 执行步 `WorkStep`（int）—— 新增，**流程内部游标**，承载推进、超时、现场排故。

   > 一句话：**阶段态是对外名片，执行步是内部游标。** 一个阶段态可横跨多个执行步。
5. **单步内禁止阻塞**：`Thread.Sleep` / `while` 轮询 / 同步 `WaitXxx` 不出现在 `case` 体内，等待靠「节拍重入 + 时间戳判超时」。参考实现 `CylinderStretch()` 内部轮询与其 `case 17` 的 `Thread.Sleep(500)` 属其既有做法，**本地明确不引入**（阻塞会同时冻结超时判据与指令响应）。
6. **步骤号段位化**（0 待机 / 10~99 主链路 A / 100~199 主链路 B / 700~799 清料 / 800~899 成功收尾 / 900~999 失败收尾），并强制维护「步号 → 中文名」映射表。

执行细则见 [[standards/StepDrivenWorkflow]]。

## 与既有 ADR 的关系（重要）

| ADR | 结论 |
|---|---|
| [[decisions/ADR-004-WorkflowStepEnum]] | **补充而非推翻**。ADR-004 反对的是「顺序直写流程」，确立的是「Step + switch-case 分派」；本 ADR 保留分派模型，只是把分派键从「8 个语义枚举」细化为「int 执行步」，并补上时间维度。ADR-004 的枚举仍作为阶段态层保留。 |
| ADR-041（已删除，见 ADR-049） | 维持。设备四态、禁手工 `State=` 赋值不变。 |
| ADR-042（已删除，见 ADR-049） | 维持。`SetStep()` / `StateChanged` / `MapToDeviceState` 仍是阶段态唯一机制。 |
| [[decisions/ADR-043-WorkflowResponsibilityBoundary]] | 维持。R1~R5 在步骤驱动下同等有效（流程仍不得替设备发数据、不得转发子设备事件）。 |
| [[decisions/ADR-044-SafetyCheckConsolidation]] | 不受影响。安全监控为独立周期线程，其 `Thread.Sleep(50)` 属周期节拍例外（[[standards/CodeSimplification]] 已标注），非本 ADR 所指"阻塞等待"。 |

## 备选方案

| 方案 | 取舍 |
|---|---|
| A. 全盘改用 int 步号，删阶段态枚举 | ❌ 否决：UI 与跨模块判断失语义；与 ADR-042/043 直接冲突；`SetStep` 校验与事件机制全废 |
| B. 保留现状（事件驱动 + 阶段态），只加时间戳 | ❌ 否决：无法表达阶段内多步推进；命令丢失/重复仍无自恢复；排故粒度不足 |
| C. **三层并存（本决策）** | ✅ 采纳：新增层不破坏既有契约，收益（超时/可观测/自恢复）全拿 |
| D. 引入第三方状态机库（Stateless） | ❌ 否决：ADR-033 已决策保持自定义状态机；且库不解决"步内超时"问题 |

## 后果

**正面**
- 流程卡死可精确定位到步号 + 停留时长，现场排故成本大幅下降。
- 每步自带超时 → 自动进告警与失败收尾，不再"卡死等人工"。
- 命令变量天然去重/可覆盖，通讯抖动不再导致流程停滞。
- 失败重试零额外代码（动作原语返 `false` 即 `break`，步号不变，下拍重入）。

**代价 / 风险**
- 每流程新增一条线程（6~7 条），需统一启停与 `Dispose` 级联（[[decisions/ADR-034-DisposePatternFullCoverage]]）。**缓解**：线程由基类 `StartRunLoop`/`StopRunLoop` 统一托管，`Dispose` 模板方法先停线程再调子类 `DisposeManaged()`；骨架流程（如 `LaserWeldHeadWorkflow`）重写 `IsRunLoopActive => false`，实际不启线程。
- `WorkStep` 与 `WorkStartTime` 的成对刷新原为**人工约定**。**已消除**：强制走 `GoStep(n)`，直接赋值的写法在机制上不存在（字段为基类私有）。
- 步号与阶段态双轨，需防"用 `WorkStep` 顶替 `Step`"的退化写法（已列红线 1）。**缓解**：阶段态切换统一在 `OnStepChanged` 钩子里把执行步复位到该阶段入口步，二者是「名片 vs 游标」的显式映射关系而非竞争关系。
- 步骤表随业务膨胀（参考实现单流程即 100+ 步），须靠段位规范与映射表治理。

## 落地清单完成情况（2026-09-01 全量实施，P0+P1+P2 一次到位）

| 优先级 | 文件 | 改造内容 | 状态 |
|---|---|---|---|
| P0 | `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs` | 加 `WorkStep`/`WorkStartTime`/`StepElapsedMs`/`WorkStepName`/`StepStatusText`、`GoStep(n)`、`ResetStepTime()`、`IsStepTimeout()`、`ClearStatus()`、抽象 `FlowProcess()`/`GetStepName(int)`、常驻监听线程 `StartRunLoop`/`StopRunLoop`、`Dispose()` 模板方法 + `DisposeManaged()` 钩子、`RunLoopPriority` | ✅ |
| P0 | `MainDeviceControl/DeviceWorkflow/MainDeviceWorkflow.cs` | 三槽命令变量（`_pendingPose`/`_pendingCommand`/`_pendingAbort`）+ `ConsumeCommand()` + 10 步分派（0/10/11/20/21/30/31/40/800/900）+ 超时三步走 | ✅ |
| P1 | `DeviceWorkflow/LineLaserWorkflow.cs` | 删阻塞 `SpinWait` 与自建 `WorkflowLoopWorker`，改常驻监听线程；9 个执行步（10/11/20/30/31/100/700/800/900）；`OnStepChanged` 复位 + 离开运行态解绑相机 | ✅ |
| P1 | `DeviceWorkflow/MonitorCameraWorkflow.cs` | 删每轮新线程；`WaitOne(5000)` 改 `WaitOne(0)` 非阻塞探测 + `IsStepTimeout`；5 个执行步（10/20/30/800/900）；连续模式回环 | ✅ |
| P2 | `DeviceWorkflow/MotionControlWorkflow.cs` | 独立 `MonitorLoop`（50Hz）并入基类监听线程（`BeatMs=20`）；启动/停止改步骤驱动；7 个执行步（10/20/30/100/110/700/900） | ✅ |
| P2 | `DeviceWorkflow/WeldParamControlWorkflow.cs` | `ComputeAndOutput()` 改命令变量（只置 `_pendingCompute`），由监听线程按 10/20/800/900 执行；`Dispose` 迁 `DisposeManaged` | ✅ |
| P2 | `DeviceWorkflow/LaserWeldHeadWorkflow.cs` | 骨架期补 `FlowProcess()`/`GetStepName()` 契约，`IsRunLoopActive => false` 不启线程；`Dispose` 移除（基类托管） | ✅ |
| P2 | `DeviceWorkflow/SafetyWorkflow.cs` | 自建高优先级线程并入基类（保留 `BeatMs=50` + `Priority=Highest`）；周期检查改执行步 10/900，报警后持续检查至恢复 | ✅ |

### 落地后新增的两条实现约定（超出原标准页，后续改动须遵守）

1. **`GoStep(n)` 是唯一改步入口**：基类私有字段 + protected 方法，子类无法绕过。
2. **`OnStepChanged` 复位执行步**：阶段态（对外名片）一切换，执行步（内部游标）即复位到该阶段入口步，`FlowProcess` 内 `SetStep` 后**必须立即 `return`**，否则会覆盖刚复位的步号。
3. **`DisposeManaged()` 取代子类 `Dispose()`**：基类已实现 `IDisposable.Dispose()` 模板方法，子类改在钩子里释放，避免重写 `Dispose` 违反 [[decisions/ADR-001-DisposePattern]]。

## 已知待办（技术债，不阻塞本次落地）

1. **基类生命周期包装器的兜底赋值**：`DeviceWorkflowBase.Initialize()` / `ManualStart()` / `ManualStop()` / `AutoRun()` 仍有 `State = DeviceState.Connect/Disconnect/Work` 兜底赋值，与红线 2「设备四态禁手工赋值」存在张力。暂保留——若移除，`LineLaserWorkflow.InitializeFlow()` 异步初始化期间 `State` 会是 `Work`（`Initializing` 映射），主设备 `IsChildConnected` 会误判为已连接。待 `Initializing` 的设备态语义厘清后收敛。
2. **`LineLaserWorkflow` 分步驱动未集成**：`BeginStarting()` / `BeginWorking()` 目前无主设备调用方。改造前为「30 秒超时后继续无限等待」，改造后按本 ADR 走「30 秒超时 → 失败收尾 → ErrorAborted」。**这是有意为之的行为变化**（暴露未集成缺陷），UI 单独调试时需注意或启用模拟模式自驱动。
3. **PLC 未连接时安全监控必报警**：`SafetyInterlockChecker.Check()` 在 PLC 未连接时恒定返回失败（记一条失败项并跳过硬件项），启动监控即会门控整机（继承自 [[decisions/ADR-044-SafetyCheckConsolidation]] 的既有待办）。

## 状态

`accepted` —— 2026-09-01 经用户确认全量范围（P0+P1+P2，8 个文件一次到位）后实施完毕，执行步写入方式选定为强制 `GoStep(n)`。
标准页见 [[standards/StepDrivenWorkflow]]，各工作流 API 见 [[api/DeviceControlWork]] / [[api/LineLaserWorkflow]] / [[api/MonitorCameraWorkflow]] / [[api/MotionControlWorkflow]] / [[api/WeldParamControlWorkflow]] / [[api/DeviceStatusWork]]。

---

*参考实现来源：外部项目 `HonorMachineTest`（`StationProcess.cs` / `AssemblyProcess.cs` / `MachineControlWork.cs`），由用户于 2026-09-01 提供。*
