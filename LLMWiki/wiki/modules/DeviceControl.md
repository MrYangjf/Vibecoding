---
title: DeviceControl 模块 — 设备控制（三态模型：SubDeviceState / SubDeviceWeldStatus / MainDeviceStatus）
date: 2026-09-02
tags: [模块, 设备控制, 状态机, 连接态, 焊接过程态, 主设备运行态, 工作流, 步骤驱动, DeviceControlWork, DeviceStatusWork, SimTrajectoryRecorder, ADR-034, ADR-032]
source: AdaWeldSystem/MainDeviceControl/ 模块源码
---

# DeviceControl 模块 — 设备控制

> 位于 `AdaWeldSystem/MainDeviceControl/`，是全部设备状态管理与工作流编排的唯一归属地。
> **架构规范页**：[[architecture/DeviceControlArchitecture]] — 详细的分层、映射规则、主控流程见该页。
> **决策记录**：[[decisions/ADR-013-ThreeStateModelRefactor]]（现行唯一有效约束）。
>
> **⚠️ 2026-09-03 原档细化已裁定（改码前必读）**：用户更新 `raw/architecture/主控设计.xlsx`（成员级清单）与新增 `激光焊接系统业务流程图.pdf`（业务流 + 检查清单），**7 项冲突已由用户逐条裁定**。
> 裁定要点：**完全重构**——新档是全新设计，不是对旧文档的补充。旧的基类常驻监听线程、`GoStep` 改步入口、命令三槽、const int 指令表、机器人 pose 监控**全部清除**，代之以 `DeviceControlWork` 7 条常驻线程 + `RunStep` bool 推进 + `CommandCore` const string 协议。
> 落地清单见 [[architecture/DeviceControlArchitecture]] §15（架构页已按裁定整体重写）。决策记录：[[decisions/ADR-035-RawDesignRefinement20260903]]（**accepted**）。

> **✅ 2026-09-23 常驻流程非阻塞范式换轨（ADR-041/063）**：① 基类契约 region「全阻塞流程」改名「**常驻流程（设备主流程）**」、「非阻塞流程」改名「非阻塞动作指令」，5 个 workflow 同步，行为零改动——**非阻塞三层铁律**：流程层常驻按拍 / 等待层按拍轮询变量 false→true 跳步 / 命令层下发即返回；**步号范式**：大步 10/20/30、小步 +1（`MotionControlWorkflow` 10/15→11/12 已换轨，其余保留现步号）。② `DoInitializeMachine` 改**受理制 + 步驱动**（`InitializeMachineTick` 由 IOWork 每拍推进 10→12→14→20/21→30/31→40），根除 thIOWork 内 `Thread.Sleep` 等连接阻塞 IO 刷新；`WaitChildConnected`/`IsInitAborted` 已删。③ `CommCommandWork` 增**指令前置条件问询** `IsCommandPreconditionMet`（启动类需 Stop+无模组 ErrorAborted / 停止类需 Running）。④ `DoSubWork` 增**焊接启动门控**（运控 PreWork 且未回标定 → 挂起按拍轮询 `IsCalibrationYReady` 补执行；运控未启动放行），模拟调度器 `SimScheduleTick` 同构化（10/20/21/30，与真实同一扇门）。详见 [[decisions/ADR-041-ResidentFlowNonBlockingParadigm]]、[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]。

---

## 核心语义：三态模型（取代「设备四态 + 流程态」）

> **2026-09-02（ADR-034）**：新主控设计明确「原流程态概念不再存在」。设备侧状态收敛为**两个正交枚举 + 一个主设备过程态**：

| 枚举 | 取值 | 用途 | 命名空间 | 属性 |
|---|---|---|---|---|
| `SubDeviceState` | `Disconnected`(0) / `Connected`(1) | 模组连接态（只两态） | `...MainDeviceControl.DeviceStateApiCore` | `Instance.State` |
| `SubDeviceWeldStatus` | **新档（裁定 C2，改码目标）**：`NoReset`(0)/`Standby`(1)/`PreWork`(2)/`Working`(3)/`Stopping`(4)/`ErrorAborted`(5)/`ManualStopped`(6)　⛔ 现状代码仍为旧取值 `Standby`(0)/`PreWork`(1)/`Starting`(2)/`Working`(3)... —— **删除 `Starting`、新增 `NoReset`(0)**，余值顺延 | 模组焊接过程态（7 态） | 同上 | `Instance.WeldStatus` |
| `MainDeviceStatus` | `Running`(0)/`Alarm`(1)/`EStop`(2)/`Stop`(3)/`NoReset`(4)/`Reseting`(5) | 主设备运行态（6 态，过程状态） | 同上 | `DeviceControlWork.Instance.Status` |

- 旧四态 `DeviceState` 枚举**已删除**。
- 旧各工作流自有流程态枚举（`LineLaserWorkflowState`/`MonitorWorkflowState`/`LaserCamBoxWorkflowState`/`WeldParamControlWorkflowState`/`LaserWeldHeadWorkflowState`）**降为私有 `_phase`/`_flowState` 字段**，仅驱动 `FlowProcess()`，不再对外暴露；对外状态统一经 `SubDeviceWeldStatus` 承载。
- `MainDeviceFlowState` 枚举（机器人 Pose 驱动的整机流程态）**已删除**，由 `MainDeviceStatus` 取代。

### 状态写入唯一入口（强制）

| 方法 | 承载 | 触发事件 | 事件参数 |
|---|---|---|---|
| `SetState(SubDeviceState, reason)` | 连接态（`protected`，基类） | `StateSwitched` | `SubDeviceStateChangedEventArgs`(OldState/NewState/Reason/Timestamp) |
| `SetWeldStatus(SubDeviceWeldStatus, reason)` | 焊接过程态（`protected`，基类） | `WeldStatusChanged` | `WeldStatusChangedEventArgs`(OldStatus/NewStatus/Reason/Timestamp) |
| `DeviceControlWork.SetStatus(MainDeviceStatus, reason)` | 主设备运行态 | `StatusChanged` | `MainDeviceStatusChangedEventArgs`(OldStatus/NewStatus/Reason/Timestamp) |

> **禁止任何子类手工 `State = ...` / `WeldStatus = ...` 赋值**——一律走上述方法。

> **2026-09-02 代码精简（ADR-009）**：删除 5 个无消费方死属性——`LineLaserWorkflow.IsInWorkflow` / `MaxConsecutiveFailures` / `MaxWeldLength` / `RealTimeAnalysisFps`、`MonitorCameraWorkflow.CurrentPhase`（违反 ADR-021 R5 对外名片约束，对应内部字段均保留）；`DeviceControlWork` 私有方法归位私有函数区。对外状态只暴露 `State` / `WeldStatus` / `WorkStep`。

### 执行步层（⛔ 代码现状为旧机制，待批次 1/2 改造）

> 本节描述的是**代码当前状态**（改造尚未开工）。下列旧机制**已由用户裁定清除**，
> 保留描述仅为对照代码现状，**不得据本节改码**。现行规范见 [[architecture/DeviceControlArchitecture]] §5 · §7.2 · §16。

| 项 | 旧（现状代码，⛔ 已裁定清除） | 新（改码目标） |
|---|---|---|
| 步号字段 | `WorkStep` | **`RunStep`** |
| 计时字段 | `WorkStartTime`（`DateTime`） | **`StepWorkTime`（`TimeSpan`）+ `TimeOutSeconds`（int，**秒**）** |
| 改步入口 | `GoStep(n)` 唯一入口 | **无入口方法**——每个 `case` 内 bool 判定后直接 `RunStep = M; break;` |
| 驱动线程 | 每流程自带常驻监听线程（`StartRunLoop` + 节拍调 `FlowProcess()`） | **删除**；由 `DeviceControlWork` 的 7 条常驻线程驱动 `FlowProcess()` |
| 命令变量 | 三槽分存（`_pendingAbort` > `_pendingCommand` > `_pendingPose`） | **删除**；`CommandCore` 的 `const string` 解析，且不监控机器人 pose |
| 配套标准 | [[architecture/DeviceControlArchitecture]] §5 · §16 | ⛔ ~~standards/StepDrivenWorkflow~~（已废弃，2026-09-17 删除） |

> **不变的原则**：连接态 / 焊接过程态 / 执行步**三层并存、互不顶替**。
> 焊接过程态是对外名片，执行步是内部游标，一个过程态可横跨多个执行步。
> **改码后仍需保证**：改步时同步刷新步骤计时（否则暂停/停机期间的时间被计入，导致误判超时）。

---

## 目录与核心文件

```
MainDeviceControl/
├── DeviceControlWork.cs            整机运行编排单例（7 常驻线程 + §7.5 九公共方法）  ns ...MainDeviceControl
├── DeviceStatusWork.cs             安全/IO/状态管控（3 常驻线程）                   ns ...MainDeviceControl
├── ~~SimTrajectoryRecorder.cs~~    ⛔ 2026-09-20 已删除：模拟轨迹记录并入记录模块 `ProductFileControl/Records/TrajectoryRecord.cs`（2026-09-24 改名 `SeamTraceYRecord.cs`，列改 5 列；模拟与真实统一走 ProductFileRecordManager，[[modules/ProductFileManager]]）
├── DeviceStateApiCore/             基类 API 核心（2026-09-01 由 DeviceState/ + FlowState/ 合并）
│   │                               ※ 2026-09-14 起命名空间随目录对齐（ADR-005）：
│   │                                 统一为 ...DeviceStateApiCore
│   ├── DeviceStateBase.cs          设备态/过程态基类 + 三枚举 + 事件参数    ns ...DeviceStateApiCore
│   ├── CommandCore.cs              机器人指令协议（const string）           ns ...DeviceStateApiCore
│   └── DeviceWorkflowBase.cs       工作流基类（非泛型）                     ns ...DeviceStateApiCore
└── DeviceWorkflow/                 命名空间 AdaWeldSystem.MainDeviceControl.DeviceWorkflow
    ├── LineLaserWorkflow.cs        线激光
    ├── MonitorCameraWorkflow.cs    监控相机
    ├── MotionControlWorkflow.cs    运控（CAMBOX）
    ├── WeldParamControlWorkflow.cs 焊接工艺控制
    └── LaserWeldHeadWorkflow.cs    焊接头（骨架）
    ※ 2026-09-01 `FaultRecoveryManager.cs`（含 FaultCategory / FaultRecord）迁出至 [[modules/ProductFileManager]]，
      本目录 7 个类为其消费方（ADR-021 §3）；模拟模式真相源为 `DeviceControlWork`（`*Simulation` API）
    ※ 2026-09-04 ADR-012 批次 0~3 + 4.4 已落地；本页「旧机制」横幅仅作改造前后对照，
      现行规范唯一出处 = [[architecture/DeviceControlArchitecture]]
```

> **命名空间已随目录对齐（2026-09-14，ADR-005）**：`DeviceState/` 与 `FlowState/` 合并为物理目录 `DeviceStateApiCore/` 后，三文件命名空间先保持不变（2026-09-01）；本轮按「命名空间 = 路径」统一为 `AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`。同批：根目录两个管控类 `DeviceControlWork.cs` / `DeviceStatusWork.cs` 由 `...DeviceWorkflow` 归位 `AdaWeldSystem.MainDeviceControl`；`DeviceWorkflow/` 5 个工作流不变。

### DeviceStateApiCore/DeviceStateBase.cs（ns ...DeviceStateApiCore）

定义三枚举 `SubDeviceState` / `SubDeviceWeldStatus` / `MainDeviceStatus` 及事件参数 `SubDeviceStateChangedEventArgs`(OldState/NewState/Reason/Timestamp)、`WeldStatusChangedEventArgs`(OldStatus/NewStatus/Reason/Timestamp)；非泛型抽象基类 `DeviceStateBase`：

| 成员 | 说明 |
|---|---|
| `State` | 连接态 `SubDeviceState`，`protected set`，变更触发 `StateSwitched` |
| `WeldStatus` | 焊接过程态 `SubDeviceWeldStatus`，`protected set`，变更触发 `WeldStatusChanged` |
| `IsAlarm` | 是否报警（过程态 == `ErrorAborted` 或主设备 `Alarm`） |
| `SetState(SubDeviceState, reason)` | 连接态写入唯一入口（protected） |
| `SetWeldStatus(SubDeviceWeldStatus, reason)` | 焊接过程态写入唯一入口（protected） |
| `StateSwitched` / `WeldStatusChanged` | 变更事件 |
| `EmergencyStop()` | 急停 |
| `CheckDeviceIOSafe()` | IO 安全检查 |
| `OnStateSwitched(old,new)` / `OnWeldStatusChanged(old,new)` | 切换钩子，可重写 |
| `BeginConnectAttempt()` | 发起连接尝试前调用，复位上次结果（`ConnectSettled`→false） |
| `MarkConnectFailed(reason)` | 标记连接尝试**已失败**并置 `Disconnected`（异步连接线程拿到确定失败结果时调用） |
| `ConnectSettled` | 连接尝试是否已出结果（成功或失败都置 true） |
| `ConnectResult` | 最近一次连接尝试结果描述（成功为「已连接」，失败为失败原因） |

#### 连接结果三态：为何不能只看 `State`（2026-09-07）

`SubDeviceState` **只有两值**，`Disconnected` 同时表示「从未连过」「连接失败」「运行期掉线」三种情形，
等待方（`WaitChildConnected`）无法区分，**只能一律空等到超时**——
现场表现为「相机连接已明确失败返回，程序却仍等满 10 秒才报超时」。

修法：连接结果独立于 `State` 表达——`ConnectSettled` 表示「本轮尝试已有结论」，
`ConnectResult` 承载结论内容。等待逻辑改为**出结果即退出**，只有始终无反馈才走超时：

| 情形 | `ConnectSettled` | `State` | 等待方行为 |
|---|---|---|---|
| 连接成功 | true | Connected | 立即返回 true |
| 连接失败（已确认） | true | Disconnected | 立即返回 false，日志记 `连接失败 {ConnectResult}` |
| 始终无反馈 | false | Disconnected | 等满超时，日志记 `连接等待超时（N 毫秒无反馈）` |

> **纪律**：异步连接线程在失败分支**必须**调 `MarkConnectFailed`，
> 只调 `SetState(Disconnected, ...)` 不足以让等待方收敛。

### DeviceStateApiCore/CommandCore.cs（ns ...DeviceStateApiCore）

> **✅ 2026-09-04 已落地（ADR-012 批次 0.3 / 0.4，裁定 C3）**：⛔ `CommandTable.cs` **已删除**，现役 **`CommandCore.cs`**——
> 指令载体由 `const int` + 三枚举（`RobotPose` / `RobotCommand` / `DeviceCommand`）改为 **`const string` 固定指令**，
> **机器人指令按字符串解析**；`RobotPoseCode` / `SignalCode` / `InteractionTable` 一并删除；
> **不再监控机器人 pose**（设备由机器人指令驱动，无权限管理机器人状态）。
> 完整常量表与消费链路见 [[api/CommandCore]]，规范见 [[architecture/DeviceControlArchitecture]] §3.1。

| 类别 | 常量 |
|---|---|
| 方向标识 | `ReceiveCommand` / `SendCommand` |
| 接收指令 `Rx*`（9 条） | `RxHomePose` / `RxStartSafePose` / `RxPreWeldPose` / `RxWeldStartPose` / `RxPreStopPose` / `RxWeldStopPose` / `RxStopSafePose` / `RxPreWeldRequest` / `RxAbort` |
| 下发指令 `Tx*`（9 条） | `TxGoHome` / `TxGoStartSafe` / `TxGoPreWeld` / `TxGoWeldStart` / `TxGoPreStop` / `TxGoWeldStop` / `TxGoStopSafe` / `TxOK` / `TxAbort` |
| 工具函数 | `Normalize(string)`（去空白 + 转大写）/ `IsKnownCommand(string)`（命中判定） |

消费链路：`GlobalCommData.CommunicationCommandReceived` → `OnCommRecived()` 规整并入队
→ `CommCommandWork` 线程 `DequeueCommand()` → `DispatchCommand(cmd)`。
位姿类指令**仅记录不驱动流程**（裁定 C3），`RxAbort` 转 `EstopMachine`。

### DeviceStateApiCore/DeviceWorkflowBase.cs（ns ...DeviceStateApiCore；非泛型，ADR-034）

> **✅ 2026-09-04 批次 1 已落地**。下表为**改造前后对照**（改造前成员 → 现行成员），不是现状描述。按 2026-09-03 原档与用户裁定：
>
> | 项 | 处置 |
> |---|---|
> | 契约数量 | 6 项 → **17 项**（5 属性 + 10 阻塞方法 + 2 非阻塞方法），见架构页 §4 |
> | `WorkStep` / `WorkStartTime` | → **`RunStep` / `StepWorkTime` / `TimeOutSeconds`（秒）**（裁定 C6） |
> | `GoStep` / `FailFlow` / `FailReason` / `FailStep` | ⛔ **删除**（裁定 C6） |
> | `StartRunLoop` / `StopRunLoop` / `BeatMs` / `RunLoopPriority` | ⛔ **删除**（裁定 C1，子流程不再自带线程） |
> | 「`FlowProcess` 自动运行唯一执行器」 | ⛔ 表述错误，新档为 **`FlowProcess` + `ResetProcess` 双流程** |
> | 配置读写 | 新增 `LoadConfig()` / `SaveConfig()` **无参**，走本项目 `XdocumentReaderWriter`；模组各自持有路径（裁定 D1，架构页 §4.6 / §16.8） |
>
> ⚠️ 改码前**先读架构页 §16（代码模板）**，**不要按本表照抄**。

`public abstract class DeviceWorkflowBase : DeviceStateBase, IDisposable`。

**六抽象契约 + `GetStepName(int)`（子类实现）**：

| 成员 | 说明 |
|---|---|
| `FlowProcess()` | 单步分派 `switch(WorkStep)`，监听线程按节拍调用，**自动运行唯一执行器** |
| `bool ResetProcess()` | 复位流程（急停/报警后回待机），返回是否成功 |
| `ClearStatus()` | 清除报警（仅清报警态回就绪态，与复位正交） |
| `ResetWorkTime()` | 复位工作时间计时 |
| `bool ConnectOn()` | 手动连接（子类内部自起后台线程，UI 开关直调，返回是否受理） |
| `ConnectOff()` | 手动断开（子类内部自起后台线程） |
| `protected abstract string GetStepName(int)` | 执行步号→中文名映射表 |

> `ConnectOn`/`ConnectOff` 取代旧 `ManualOn`/`ManualOff`/`InitializeFlow`/`ResetFlow`/`ClearAlarmFlow`；旧 `Initialize()`/`Reset()`/`ClearAlarm()` 三公开生命周期由基类模板方法承载（记日志后调用上述契约）。

**执行步层（基类提供）**：

| 成员 | 说明 |
|---|---|
| `WorkStep` / `WorkStartTime` | 执行步号 / 步进入时间（只读） |
| `StepElapsedMs` / `WorkStepName` / `StepStatusText` | 可观测性：`"step:21 / 3.4s 等待数据稳定"` |
| `GoStep(int)` | **唯一改步入口**（protected），成对刷新步号 + 时间戳 |
| `ResetStepTime()` | 刷新当前步时间戳（非活跃态每拍调用，防恢复瞬间误判超时） |
| `IsStepTimeout(double)` | 统一超时判据入口 |
| `ClearStatus()` | 状态与执行步清零（虚） |

**常驻监听线程（基类提供）**：

| 成员 | 说明 |
|---|---|
| `StartRunLoop()` / `StopRunLoop()` | 启停监听线程（幂等；`IsBackground`） |
| `IsRunLoopRunning` | 线程是否运行 |
| `IsRunLoopActive`（虚） | 是否执行业务，默认 `true`；骨架流程重写 `false` 可避免空转线程 |
| `ConsumeCommand()`（虚） | 命令变量消费钩子 |
| `BeatMs`（默认 10ms）/ `RunLoopPriority`（默认 Normal） | 节拍与线程优先级 |
| `DisposeManaged()`（虚） | **子类释放钩子**：原 `Dispose()` 内容搬到这里 |

**通用执行步号常量与失败收尾（基类下沉，子类不得重复定义）**：

| 成员 | 值 | 说明 |
|---|---|---|
| `StepIdle`（protected const） | 0 | 待机 |
| `StepFinishOk`（protected const） | 800 | 成功收尾 |
| `StepFinishFail`（protected const） | 900 | 失败收尾 |
| `FailFlow(string reason)` | — | **失败收尾唯一入口**：记录 `_failStep` / `_failReason` 后 `GoStep(StepFinishFail)` |
| `FailStep` / `FailReason` | — | 触发失败的执行步号 / 失败原因（只读） |

> **命名约定（硬约束）**：步号常量一律 `StepXxx`，单步方法一律 `DoXxx()`。两者同名会触发 **CS0102**；子类重复定义基类 `protected const` 会触发 **CS0108**。详见 [[architecture/DeviceControlArchitecture]] §5 与 [[lessons/StepDrivenWorkflowPitfalls]]（七.6）。

三公开生命周期（基类实现，含状态语义赋值）：

| 方法 | 行为 |
|---|---|
| `Initialize()` | 阻塞同步 `ConnectOn()` 成功→`Connected`，失败→`Disconnected` |
| `Reset()` | 模板方法：记日志 → `ResetProcess()` |
| `ClearAlarm()` | 模板方法：记日志 → `ClearStatus()`（清除报警入口，与 `Reset` 并列） |
| `Dispose()` | 停监听线程 → `DisposeManaged()`（子类不再重写 `Dispose`，ADR-001） |

> **易误判点**：`Reset`/`Dispose`/`State`/`WeldStatus`/`StateSwitched`/`WeldStatusChanged`/`RunStep`/`FlowProcess`/`ResetWorkTime` 都由基类提供或约束，具体工作流文件内 grep 不到属正常，不是缺陷。
> 手动连接/断开的 `ConnectOn`/`ConnectOff` 为 `public abstract`，UI 直调，线程由子类内部自起。

### 子工作流现行范式（2026-09-04 批次 0~4.4 落地）

各子工作流**不自带线程**，由 `DeviceControlWork` 5 条模组线程五段式驱动 `FlowProcess()`；执行步走基类 `RunStep`（`switch(RunStep)` → 每 `case` 内 bool 判定推进，`AdvanceStep(n)` 改步并刷新计时）。

- 阶段枚举为**私有 `_phase`**（或直接 `RunStep` 步号），切换经 `MapWeldStatus(...)` 映射为对外 `SubDeviceWeldStatus` 后走 `SetWeldStatus`；
- `GoStep`/`SetStep`/`WorkStep` **均已删除**（裁定 C6）；超时用 `TimeOutSeconds`（秒）+ `ResetWorkTime()`；
- 5 子类实现基类 17 项契约（含 `InitializeOn`/`Off` 阻塞连接、`ConnectOn`/`Off` 非阻塞、`LoadConfig`/`SaveConfig` 无参、`WeldStatusTrans`、`SubDeviceLog`）。
- 外部驱动（模组级命令）经 `DeviceControlWork` 虚拟 IO（§7.9）→ `CascadeWeldStatus` → 基类 `RequestWeldStatus` 统一下发。
---

## 整机主控与安全：删除并归并

### DeviceControlWork

`public class DeviceControlWork`（单例，**独立管控类，不继承任何基类**）——整机运行编排者，**2026-09-04 已按 ADR-012 重构落地**：

- 7 条常驻线程（5 模组驱动 `FlowProcess` + 心跳 + 指令）共用私有体 `SubDeviceWork(flow,name)` 五段式驱动，防空转 `Sleep(10)`/`Sleep(100)`
- `Current`/`Last` 双 `MainDeviceStatus` 快照 + `IsReseting`/`IsWorking`/`IsAlarmstop`/`IsCloseWork` 标志位；`MachineStatusTrans` 校验迁移合法
- §7.5 九公共方法：`MachineFlowWorkOpen`/`MachineCommandWorkOpen`/`InitializeMachine`/`ClearMachine`/`ResetMachine`/`StartMachine`/`ClearAlarm`/`EstopMachine`/`EstopCancel`
- 命令经虚拟 IO（§7.9）：机器人指令 `MapCommandToIo` → 置位，`DeviceStatusWork` 双线程扫描后 `ExecuteIo` 统一执行
- 模拟模式由第 8 条按需线程 `thSimTestWork` 承载（2026-09-04 用户裁定），随 `StartSimulation()` / `DisableSimulation()` 启停；**2026-09-17 ADR-032** 取消 A/B/C 模式（删 `SimTestMode`），按设备连接态**自动分支**（线激光未连 → 虚拟相机；运控未连 → 只记录不写轴），~~轨迹点由 `SimTrajectoryRecorder` 缓存并终止落盘~~（**2026-09-20 演进**：记录器删除，轨迹记录并入 [[modules/ProductFileManager]] 的 `TrajectoryRecord`，模拟与真实统一归口 `ProductFileRecordManager`，模拟文件名加「模拟」前缀；`SimTick` 统一喂数——模拟 X 同步 `WeldParamManager.CurrentRobotX`）

> ⛔ **本页下方原有「改造前」结构存档**（自带线程节拍 `BeatMs=10`、内部执行步 `_workStep`/`GetStepName`、命令三槽 `_pendingPose`>`_pendingCommand`>`_pendingAbort`、`RobotPose`/`RobotCommand` 指令消费、`EStopMachine`/`StartWork` 旧名）
> **已全部清除**（ADR-012 裁定 C1/C3/C6 + §2 同源约束 + 2026-09-04 批次落地）。现行 API 见 [[api/DeviceControlWork]]，设计见 [[architecture/DeviceControlArchitecture]] §7；主设备运行态为 `MainDeviceStatus`（Running/Alarm/EStop/Stop/NoReset/Reseting）。
### DeviceStatusWork

`public class DeviceStatusWork`（单例），安全检查三合一（`IsSafe` / `CheckDeviceStates` / 故障记录）归并至此；监控未启动返回 `true`（不阻断整机）。API 详见 [[api/DeviceStatusWork]]（现述 DeviceStatusWork）。

---

## 各工作流

| 工作流 | 私有阶段枚举 | 执行步 | 状态 | 说明 |
|---|---|---|---|---|
| `DeviceControlWork` | （无，直接 `MainDeviceStatus`） | — | 全实现 | 整机主控：7 常驻线程编排（5 模组驱动 `FlowProcess`）+ 指令队列消费 + 上电初始化 + 模拟模式（第 8 条按需线程） |
| `LineLaserWorkflow` | （无，`RunStep` 段位直驱） | 0/10/20/30/31/100/700/800/900 | 全实现 | 线激光焊缝跟踪，触发焊接工艺计算 |
| `MonitorCameraWorkflow` | `MonitorWorkflowState`(同文件公共枚举，仅内部驱动) | 0/10/20/30/800/900 | 全实现 | 监控相机触发采集/分析/结果（健康巡检归 `MonitorCameraRun`） |
| `MotionControlWorkflow` | `LaserCamBoxWorkflowState`(同文件公共枚举，仅内部驱动) | 0/10/20/30/100/110/700/900 | 全实现 | CAMBOX 硬件实时跟踪（`FlowProcess` 每拍开头刷跟踪状态） |
| `WeldParamControlWorkflow` | `WeldParamControlWorkflowState`(同文件公共枚举，仅内部驱动) | 0/10/20/800/900 | 全实现 | 焊接工艺计算与下发（**非设备**，`_pendingCompute` 触发变量） |
| `LaserWeldHeadWorkflow` | `LaserWeldHeadWorkflowState`(同文件公共枚举，仅内部驱动) | 仅 0 | 骨架 | 温度阈值监控（原档 R009）待落地，`FlowProcess()` 空转 |
| `DeviceStatusWork` | （无，三线程内部态 thIOWork/thEMGWork/thLightStatusWork） | —（三线程非步骤驱动） | 全实现 | 安全/IO/状态管控：IOWork 互锁→Alarm、EMGWork 急停→EStop、LightStatusWork 反射三色灯 |

**分层就绪（ADR-098）**：`DeviceWorkflowBase` 暴露 `IsConnected / IsEnabled / IsHomed / IsAtWorkZero / ReadinessStage / ReadinessReason`，并保留轴级能力 `NeedHoming / HasAbsoluteEncoder / WorkZeroSource`。等级：断连 → L0 已连接 → L1 已使能 → L2 未回零（需回零轴）→ L3 已回零 → L4 已到工作零位。**免回零轴（Y）使能即 L3**，需回零轴（TA）使能后为 L2。动作门槛：点动 L1、寻位 L3、自动焊接 L4；线激光/监控相机/焊接工艺/焊接头为 L0。未达门槛由 `EnsureReadiness` 拒绝，原因含「当前 L / 需 L / 动作 / 原因」。⛔ 禁按轴名写分支。

> 段位规范：0 待机 / 1~9 入口准备 / 10~99 主链路 A / 100~199 主链路 B / 700~799 清料 / 800~899 成功收尾 / 900~999 失败收尾。详见 [[architecture/DeviceControlArchitecture]] §5。

### DeviceStatusWork — 安全/IO/状态管控

`DeviceStatusWork.cs` 单文件承载：互锁阈值与 PLC 地址（`SafetyFlow` 配置类）+ 互锁判定（`SafetyInterlockChecker`）+ 三线程监控循环（ADR-011 三合一 + ADR-034 归并）。设计参照 `PcomDeviceInterface/MachineStatusWork.cs` 的 IOWork/EMGWork/StatusWork 三线程模型（见 `主控设计.xlsx`「设备安全/IO/状态管控」泳道）。

**三线程（非步骤驱动，2026-09-04 对齐原档命名）**：`DeviceStatusWork` 是独立管控类，不继承 `DeviceWorkflowBase`，由三个常驻线程驱动（各 20Hz）——`thIOWork`（线程体 `IOWork()`，AboveNormal）周期互锁检查 → 失败 `ReportAlarm` + `RecordFault`，恢复 `ReportAlarmCleared`；`thEMGWork`（线程体 `EMGWork()`，Highest）**只看物理急停位（反逻辑：无信号=急停，IO 上电=设备通知安全才允许 `EstopCancel`；无虚拟 IO，`EstopMachine` 直通同步执行，2026-09-08 裁定）**；`thLightStatusWork`（线程体 `LightStatusWork()`，Normal）反射 `DeviceControlWork.Status` 到三色灯。

**主设备门控（⛔ 旧写法，裁定 C3 已移除）**：~~`DeviceControlWork.IsRobotPoseSafe()` 读 `DeviceStatusWork.Instance.IsSafe`~~ → 新方法名与 pose 语义一并删除，**直接读 `DeviceStatusWork.Instance.IsSafe`**（本机安全 IO，与机器人 pose 无关）。监控未启动时不门控（返回 true）。

**随整机启动**：`MachineIOWorkOpen()` 由 `DeviceControlWork.InitializeMachine`/`StartMachine` 调用、`MachineIOWorkClose()` 由 `StopMachine`/`Dispose` 调用（2026-09-04 取代旧 `StartWork()`/`CloseWork()`）。

API 详见 [[api/DeviceStatusWork]]（现述 DeviceStatusWork）。

### DeviceControlWork — 上电初始化按依赖层级（2026-11-09 改）

```
[1] 机器人通讯(软依赖·需界面就绪) → [2] 运动控制器(EtherCAT 主站·根节点)
     → [3] 焊接头从站(硬依赖：父=[2]) → [4] 线激光相机(软依赖) → [5] 监控相机(软依赖)
     → FinishInitialization()：EvaluateInitializationResult → TA 配置 → 统一使能 → MarkInitCompleted（先开闸）→ 自动 TA_ZeroPose → 轴闸门报告 → 汇总事件
```

**层级驱动**：节点表由 `BuildInitPlan()` 声明（`InitNode { Key, ParentKey, Device, Start }`），顺序即执行顺序、父在前；⛔ 不再有 `switch(_initStep)` 步进机。

**父失败子跳过**：进入节点前先查父节点结果，父结果 ≠ `Success` ⇒ 子级记 `DeviceInitOutcome.Skipped`（带 `BlockedBy`）并直接推进，**不调用 `Start`、不发起连接、不等待超时**。⛔ 不用固定 `Sleep`，连接等待沿用 `CASCADE_CONNECT_MS`。

**三态汇总**：`Success / Failed / Skipped` 分开计数，`Skipped` **不计入失败**但必须能被操作者看到（日志 + `InitializationSummaryReady` 事件 → 界面提示「先修上级」）。详见 [[standards/DeviceInitializationDependency]]。

聚合判定：`Mandatory` 节点全部 `Success` 且全部轴使能成功 → 整机就绪；否则 → `MainDeviceStatus.Alarm`。

**关键边界**：机器人/PLC 连接由顶层 [[modules/Comm]] 的 `CommunicationManager` 管控，本工作流只做信号交互（收 `RobotPose` / 下发 `DeviceCommand`），不持有连接。

### WeldParamControlWorkflow — 非设备的工艺控制流程

**不是有连接动作的设备**，是设备内部控制焊接工艺的流程。`ConnectOn()` 在此表示「工艺参数就绪」（无物理连接）。

输入（机器人信息 + 线激光结果）→ 计算 → 输出（焊接功率 / 送丝速度 / 振镜摆幅 / 焊接速度）→ 下发机器人。数据链路与"不入上电级联"的原因详见 [[modules/WeldParamControl]]。

### MotionControlWorkflow — Idle 一态两义

`Idle` 既可能是"未连接就绪"也可能是"已连接就绪"，按初始化标记区分：
```csharp
return _initialized ? SubDeviceState.Connected : SubDeviceState.Disconnected;
```

---

## 安全互锁与故障恢复（合并后）

| 文件 | 职责 |
|---|---|
| `DeviceStatusWork.cs` | 安全检查流程（三合一）：互锁阈值与 PLC 地址 + 互锁判定 + 监控循环 |
| `ProductFileManager/FaultRecoveryManager.cs` | **已迁出本模块（2026-09-01，ADR-021 §3）**：单例，故障恢复闭环 + `FaultCategory` / `FaultRecord` 数据载体；本目录 7 工作流为其消费方 |

详见 [[modules/Safety]]、[[modules/ProductFileManager]]、[[api/DeviceStatusWork]]。

重试策略：通讯 3 次/5s、相机 2 次、线激光 3 次、安全类 0 次。

> **P0 坑**：故障恢复设备键名必须用**英文 key**，与 `RegisterRecoveryStrategy` 注册一致。详见 [[lessons/FaultRecoveryDeviceKey]]。

---

## UI 接入

须引入 `using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;`（读连接态另需 `using AdaWeldSystem.MainDeviceControl.DeviceStateApiCore;`）

**三个属性不可混淆**：

| 属性 | 含义 | 用途 |
|---|---|---|
| `Instance.WeldStatus` | 焊接过程态（`SubDeviceWeldStatus`） | 判断是否运行、显示分步进度 |
| `Instance.State` | 连接态（`SubDeviceState`） | 判断能否操作、销毁前是否断开 |
| `Instance.WorkStep` / `StepStatusText` | 执行步（内部游标） | **现场排故**：卡在哪个子步、卡了多久 |

`StepStatusText` 形如 `"step:21 / 3.4s 等待数据稳定"`，可直接挂 UI 状态标签；卡死时步号不动、时长持续涨。
红线：UI 线程**禁止直接调用 `FlowProcess()`**（[[architecture/DeviceControlArchitecture]] §5 红线）。

当前接入：`FormMain.cs`、`ILCamPage.cs`、`MonitorCamPage.cs`、`SystemControlPage.cs`、`MainPage.cs`

---

## 初始化日志（2026-11-09 修订）

初始化链输出按**两个阶段 + 唯一收尾**组织，规格见 [[standards/InitializationLogSpec]]：

| 阶段 | 覆盖内容 | 日志形态 |
|---|---|---|
| **阶段一 连接** | 5 个节点 `[1/5]`~`[5/5]` 恒定编号 | `[{i}/5] {模组} 连接 开始` → `成功` / `失败 原因 …` / `跳过 原因 …` |
| **阶段二 使能** | 仅当运动控制器就绪才展开 | `阶段二 使能 开始` → 逐轴 → `完成 成功 X 轴 失败 Y 轴` |
| **收尾** | 恒为最后一条 | `模组初始化汇总 成功 X / 失败 Y / 跳过 Z` |

关键修正：

- **机器人通讯成功判据**改为 `CommunicationManager.ConnectRobot()` 的真实返回值；`通道就绪` 不再算成功，失败原因取 `LastRobotConnectError`（如「本机无可用网口承载 HOST_IP …」）。
- **阶段二门禁**取 `_initMotionReady`（运动控制器节点是否 Success）；未就绪只打一条 `阶段二 使能 跳过 原因 …`，⛔ 不再逐轴/逐门禁铺开。
- `轴闸门` 与 `整机轴汇总` 前移到汇总之前；`整机轴汇总` 降 Debug。
- 各工作流/设备层的同义开始/失败日志（`连接开始`、`初始化步骤 1/3`、`监控相机初始化连接开始` 等）统一降 **Debug**，只留 `DeviceControlWork` 的权威行。

---

## 协作关系

| 模块 | 关系 |
|---|---|
| [[modules/Comm]] | 机器人/PLC 连接归属地；主控经 `GlobalCommData` 做信号交互 |
| [[modules/WeldParamControl]] | `WeldProcess` 提供工艺计算，由 `WeldParamControlWorkflow` 驱动 |
| [[modules/LineLaserCam]] | 英莱相机，焊缝信息源头 |
| [[modules/EmguALG]] | `PipelineManager` 承载 `SeamFeatureResult` 上报 |
| [[modules/MotionControl]] | 运控硬件层，CAMBOX 依托正运动控制器 |
| [[modules/UIDesign]] | UI 层，读 `WeldStatus`/`State` |

---

## 已知约束

- 本环境**无法编译**，改动后必须做静态编译安全自检（类型解析 / csproj 完整性 / 无未注册孤儿 / `Dispose(bool)` / 继承链）
- C# 7.3（[[decisions/ADR-001-CS73-Constraint]]）：禁 switch 表达式、属性模式、nullable、record、range
- 非 UI 类统一标准 `IDisposable.Dispose()`（ADR-002（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[decisions/ADR-002-DisposePatternFullCoverage]]）
- 振镜摆幅 `CalcGalvoAmplitude` 为 TODO 占位返回 0.0，`WeaveWidth` 是查表项而非公式
- 旧四态 `DeviceState` 枚举、泛型 `WorkflowStateBase<TStep>`/`DeviceWorkflowBase<TStep>`、`MainDeviceFlowState` 枚举均已删除，引用这些旧符号的代码/文档视为冲突，须改用三态模型
- **线程问询范式（2026-09-07 用户裁定 + 参考基线合规核对）**：线程只判断「状态是否属于自己」，**只读 `Current` 决定执行/不执行，绝不修改状态**——状态变化只归 IO 动作链（`DoXxx` → `SetStatus`）专门管理；所有循环必须有节拍防快速空转（流程线程 100ms 空闲 / 10ms 工作，连接等待 100ms，IO 三线程 50ms）。落点：`SubDeviceWork` 每拍问询（局部 `wasDriving` 门控，仅从 Running 真正跌出才经 `LogDriveStopped` 记一次日志；**启动默认态 NoReset 不打日志**，2026-09-08 用户裁定）、`CascadeResetProcess` 每步问询 `Reseting`、`DoResetMachine`/`DoStartMachine` 走 `IsActionAborted`、初始化链走 `IsInitAborted`/`IsInitPreempted`、`ScanPulseIo(requireRunning)` 分派前问询。详见 [[api/DeviceControlWork]] 与 [[api/HonorMachineTest-IOReference]] §6.1
- **报警源虚拟 IO 化（2026-09-08 用户裁定）**：控制器状态变量注册成**电平型**虚拟 IO（`IoMotionBusFault`），由 `IOWork.ScanMotionBusFault()` 每 200ms 非阻塞监督（`MontionControl.CheckBusOK` L2 virtual 契约）；**普通 Alarm 走 IOWork，EMGWork 专责急停**；NG→OK 不自动消警（归 ClearAlarm 链）；`DoMotionBusFault` 纯状态迁移 µs 级，与急停同属「同步执行白名单」（报警不允许被 `DispatchAction` 忙丢弃）。WKC 错误计数（掉线前兆）v1 未纳入，见 [[api/MontionManager]] 总线健康检查契约

## 初始化与复位分离（2026-11-16，阶段 3 / ADR-099）

- 生命周期切成两段：**初始化 = 连接 + 使能**（结束态「已连接/已使能/未回零/无运动」），**复位 = 按轴能力回工作零位**（门槛 L1）。
- 初始化受理门禁：进行中、运行中、急停、复位中一律拒绝；规划目标全连即跳过，实现「保留已连、只补未连」。
- 复位走既有链路：`ResetMachine()` → `IoReset` → `DoResetMachine()` 复位线程 → `CascadeResetProcess()` 逐子流程 → 子流程 `ResetProcess()` → 各管理器动作；主控只编排顺序与结果，⛔ 不新增第二套复位通道。
- 运控子流程复位 `MotionControlWorkflow.ResetProcess()`：门槛 L1，需回零轴 `Home()` → 工作零位，免回零轴只去工作零位；失败停 L2/L3 可重试。
- 初始化期 `IOWork` 不判安全互锁，避免未连接先报 Alarm；初始化结束互锁照常。
- 回退路径：配置 `INIT_RUN_TA_HOME=1` 恢复初始化末尾自动回零。
- 详见 [[decisions/ADR-099-init-reset-separation]] · [[api/DeviceControlWork]] · [[api/MotionControlWorkflow]]

## 两套状态联合与动作双闸门（2026-11-17，阶段 4 / ADR-100）

- 设备 6 态 × 流程 7 态组成联合矩阵；设备态变化不自动级联流程态，流程态仍只由 `CascadeWeldStatus → WeldStatusTrans` 写入。
- 1 s 一致性巡检挂既有 `thIOWork`（`ConsistencyTick`）：只纠 `Stop × Working`、`NoReset × 非 NoReset`、`Alarm/EStop × Working` 三类非法组合，每类一条 `Warning`；`Alarm` 自进入起 3 s 宽限，放行报警停焊瞬时组合。
- 子流程 `ErrorAborted` 只经 `ReportAlarm` 上升为设备 `Alarm`，只升不降；`Alarm/EStop` 下不重复上报。
- 动作入口双闸门：设备态须 `Running` 且 `EnsureReadiness` 达标（自动焊接 L4、焊前检查 L0），模拟沿用既有旁路。
- 设备态变化沿一条 `Info`，流程态级联一条；`GetStatusSnapshot()` 一次读出设备态/流程态/就绪/线程登记。
- 详见 [[decisions/ADR-100-state-union-and-action-gate]] · [[api/DeviceControlWork]] · [[api/DeviceStatusWork]]

## 关闭闭环与急停（2026-11-17，阶段 5 / ADR-101）

- 关闭唯一顺序：清虚拟 IO → 模组线程（Join）→ 通讯线程（`MachineCommandWorkClose`+Join）→ 状态/动作线程 → 模拟线程（Join）→ 逐台断设备（每台等 5 s）→ 关机器人通道；总预算 30 s，超时一条「强制退出 原因 步骤 时点」。
- `DisposeComponents` 以 `_disposed` 幂等、`_shuttingDown` 拒绝新业务；末条汇总 `关闭完成 线程 n/11 设备 m/4 用时 xms`。
- `CascadeDisconnect` 由「受理即返回」改为「受理 + 等待 `Disconnected` + 单台超时」，`DoStopMachine` 共用；断不全记 Warning 留现场。
- 线程标志拆分：模组 `IsCloseWork`、通讯 `_commCloseWork`；停模组不再连带停心跳与指令线程。
- 关闭期 `IOWork` 只保活，不推进扫描/巡检/初始化/对齐。
- 急停固定「停运动 → 置 EStop → 停模组线程 → `ServoOffAll`」，不调用级联断开；设备保持在线，T09~T11 继续运行，解除走 `EstopCancel → NoReset`。
- 运控关闭唯一入口 `InitializeOff`（幂等），`DisposeManaged` 委派；线激光连接/断开线程与模拟线程关闭时 Join；退出链补管理器 SDK 释放。
- 详见 [[decisions/ADR-101-shutdown-closure-and-estop]] · [[api/DeviceControlWork]] · [[api/MotionControlWorkflow]]
