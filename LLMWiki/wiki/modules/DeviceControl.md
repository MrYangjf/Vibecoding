---
title: DeviceControl 模块 — 设备控制（三态模型：SubDeviceState / SubDeviceWeldStatus / MainDeviceStatus）
date: 2026-09-02
tags: [模块, 设备控制, 状态机, 连接态, 焊接过程态, 主设备运行态, 工作流, 步骤驱动, DeviceControlWork, DeviceStatusWork, ADR-049]
source: AdaWeldSystem/MainDeviceControl/ 模块源码
---

# DeviceControl 模块 — 设备控制

> 位于 `AdaWeldSystem/MainDeviceControl/`，是全部设备状态管理与工作流编排的唯一归属地。
> **架构规范页**：[[architecture/DeviceControlArchitecture]] — 详细的分层、映射规则、主控流程见该页。
> **决策记录**：[[decisions/ADR-049-ThreeStateModelRefactor]]（现行唯一有效约束，取代 ADR-041/042/047/048）。

---

## 核心语义：三态模型（取代「设备四态 + 流程态」）

> **2026-09-02（ADR-049）**：新主控设计明确「原流程态概念不再存在」。设备侧状态收敛为**两个正交枚举 + 一个主设备过程态**：

| 枚举 | 取值 | 用途 | 命名空间 | 属性 |
|---|---|---|---|---|
| `SubDeviceState` | `Disconnected`(0) / `Connected`(1) | 子设备连接态（只两态） | `...MainDeviceControl.DeviceState` | `Instance.State` |
| `SubDeviceWeldStatus` | `Standby`(0)/`PreWork`(1)/`Starting`(2)/`Working`(3)/`Stopping`(4)/`ErrorAborted`(5)/`ManualStopped`(6) | 子设备焊接过程态（7 态） | 同上 | `Instance.WeldStatus` |
| `MainDeviceStatus` | `Running`(0)/`Alarm`(1)/`EStop`(2)/`Stop`(3)/`NoReset`(4)/`Reseting`(5) | 主设备运行态（6 态，过程状态） | 同上 | `DeviceControlWork.Instance.Status` |

- 旧四态 `DeviceState` 枚举、**已删除**；旧各工作流自有流程态枚举（`LineLaserWorkflowState`/`MonitorWorkflowState`/`LaserCamBoxWorkflowState`/`WeldParamControlWorkflowState`/`LaserWeldHeadWorkflowState`）**降为私有 `_phase`/`_flowState` 字段**，仅驱动 `FlowProcess()`，不再对外暴露；对外状态统一经 `SubDeviceWeldStatus` 承载。
- `MainDeviceFlowState` 枚举（机器人 Pose 驱动的整机流程态）**已删除**，由 `MainDeviceStatus` 取代。

### 状态写入唯一入口（强制）

| 方法 | 承载 | 触发事件 | 事件参数 |
|---|---|---|---|
| `SetState(SubDeviceState, reason)` | 连接态（`protected`，基类） | `StateSwitched` | `SubDeviceStateChangedEventArgs`(OldState/NewState/Reason/Timestamp) |
| `SetWeldStatus(SubDeviceWeldStatus, reason)` | 焊接过程态（`protected`，基类） | `WeldStatusChanged` | `WeldStatusChangedEventArgs`(OldStatus/NewStatus/Reason/Timestamp) |
| `DeviceControlWork.SetStatus(MainDeviceStatus, reason)` | 主设备运行态 | `StatusChanged` | `MainDeviceStatusChangedEventArgs`(OldStatus/NewStatus/Reason/Timestamp) |

> **禁止任何子类手工 `State = ...` / `WeldStatus = ...` 赋值**——一律走上述方法。

> **2026-09-02 代码精简（ADR-038）**：删除 5 个无消费方死属性——`LineLaserWorkflow.IsInWorkflow` / `MaxConsecutiveFailures` / `MaxWeldLength` / `RealTimeAnalysisFps`、`MonitorCameraWorkflow.CurrentPhase`（违反 ADR-043 R5 对外名片约束，对应内部字段均保留）；`DeviceControlWork` 私有方法归位私有函数区。对外状态只暴露 `State` / `WeldStatus` / `WorkStep`。

### 执行步层（步骤驱动，沿用）

除三态外，仍保留 **`WorkStep`(int) + `WorkStartTime`(DateTime)** 执行步层，作为流程内部推进游标：

| 层 | 载体 | 粒度 | 消费方 | 变更入口 |
|---|---|---|---|---|
| 连接态 | `SubDeviceState` 枚举 | 2 态 | UI 连接灯、级联 | `SetState()`（禁手工赋值） |
| 焊接过程态 | `SubDeviceWeldStatus` 枚举 | 7 态 | UI 语义、跨模块判断 | `SetWeldStatus()`（子类私有 `SetStep` 桥接） |
| **执行步** | `int` + `DateTime` | 数十~上百步 | 流程内部推进、超时判定、现场排故 | **`GoStep(n)`（唯一入口）** |

> **焊接过程态是对外名片，执行步是内部游标。** 一个过程态可横跨多个执行步。三层并存，执行步**不取代**过程态。
> 配套：命令变量（通讯层只赋值不做业务）+ 每流程一条常驻监听线程（`StartRunLoop` + 节拍调 `FlowProcess()`）。
> 标准见 [[standards/StepDrivenWorkflow]]。

**两条强制约定**：

1. `GoStep(n)` 是唯一改步入口（基类 `protected` 方法，内部成对刷新步号 + 时间戳 + 记日志），字段为基类私有，子类无法直接赋值。
2. 过程态切换时在 `OnWeldStatusChanged` 钩子里把执行步复位到该阶段入口步；故 `FlowProcess()` 内 `SetWeldStatus(...)`（经私有 `SetStep`）后**必须立即 `return`**，否则会覆盖刚复位的步号。

---

## 目录与核心文件

```
MainDeviceControl/
├── DeviceStateApiCore/               基类 API 核心（2026-09-01 由 DeviceState/ + FlowState/ 合并）
│   │                                 ※ 目录合并但命名空间不变，下分两个：
│   │                                   ...DeviceState / ...FlowState（详见下方「目录 ≠ 命名空间」）
│   ├── DeviceStateBase.cs            设备态/过程态基类 + 三枚举 + 事件参数    ns ...DeviceState
│   ├── CommandTable.cs               机器人握手协议        ns ...DeviceState
│   └── DeviceWorkflowBase.cs         工作流基类（非泛型）  ns ...FlowState
├── DeviceWorkflow/                   命名空间 AdaWeldSystem.MainDeviceControl.DeviceWorkflow
│   ├── DeviceControlWork.cs          整机主控（取代 MainDeviceWorkflow）   ns ...DeviceWorkflow
│   ├── DeviceStatusWork.cs           安全检查（取代 SafetyWorkflow）        ns ...DeviceWorkflow
│   ├── LineLaserWorkflow.cs          线激光
│   ├── MonitorCameraWorkflow.cs      监控相机
│   ├── MotionControlWorkflow.cs      运控（CAMBOX）
│   ├── WeldParamControlWorkflow.cs   焊接工艺控制
│   └── LaserWeldHeadWorkflow.cs      焊接头（骨架）
│   ※ 2026-09-01 `WorkflowStateBase.cs` 已删除，泛型机制并入非泛型 `DeviceWorkflowBase`（ADR-049）
│   ※ `SimulationWorkflow.cs` 已删除，成员归并 `DeviceControlWork`（模拟真相源 = [[api/MainDeviceWorkflow]]）
│   ※ Safety/ 子目录已解散平铺；状态契约已内联各工作流文件
│     （WorkflowState.cs 删除，AdaWeldSystem.Workflow 命名空间不复存在，2026-08-28）
│   ※ 2026-09-01 `FaultRecoveryManager.cs`（含 FaultCategory / FaultRecord）迁出至 [[modules/ProductFileManager]]，
│     本目录 7 工作流为其消费方（ADR-046 §3）
```

> **目录 ≠ 命名空间（2026-09-01 起）**：`DeviceState/` 与 `FlowState/` 已合并为物理目录 `DeviceStateApiCore/`，但**命名空间刻意保持不变**——`DeviceStateBase.cs` / `CommandTable.cs` 仍为 `AdaWeldSystem.MainDeviceControl.DeviceState`，`DeviceWorkflowBase.cs` 仍为 `AdaWeldSystem.MainDeviceControl.FlowState`。理由：改名会波及 7 个工作流及全部消费方的 `using`，收益为零。以下小节标题沿用**命名空间语义**标注。

### DeviceStateApiCore/DeviceStateBase.cs（ns ...DeviceState）

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

### DeviceStateApiCore/CommandTable.cs（ns ...DeviceState）

机器人握手协议（均 `enum : int`）：
- `RobotPose` — 机器人状态上报
- `RobotCommand` — 机器人下发指令
- `DeviceCommand` — 设备侧指令（`CmdGoXxx` 对齐 Pose + `CmdOK` + `CmdAbort`）
- `InteractionTable` — 交互合法性表（`IsValidPose` 等）

### DeviceStateApiCore/DeviceWorkflowBase.cs（ns ...FlowState；非泛型，ADR-049）

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

> **命名约定（硬约束）**：步号常量一律 `StepXxx`，单步方法一律 `DoXxx()`。两者同名会触发 **CS0102**；子类重复定义基类 `protected const` 会触发 **CS0108**。详见 [[standards/StepDrivenWorkflow]] §五 与 [[lessons/StepMemberNameCollision]]。

三公开生命周期（基类实现，含状态语义赋值）：

| 方法 | 行为 |
|---|---|
| `Initialize()` | 阻塞同步 `ConnectOn()` 成功→`Connected`，失败→`Disconnected` |
| `Reset()` | 模板方法：记日志 → `ResetProcess()` |
| `ClearAlarm()` | 模板方法：记日志 → `ClearStatus()`（清除报警入口，与 `Reset` 并列） |
| `Dispose()` | 停监听线程 → `DisposeManaged()`（子类不再重写 `Dispose`，ADR-001） |

> **易误判点**：`Reset`/`Dispose`/`State`/`WeldStatus`/`StateSwitched`/`WeldStatusChanged`/`GoStep`/`FlowProcess` 都由基类提供或约束，具体工作流文件内 grep 不到属正常，不是缺陷。
> 手动连接/断开的 `ConnectOn`/`ConnectOff` 为 `public abstract`，UI 直调，线程由子类内部自起。

### 子工作流的等价最小改写（ADR-049）

各子工作流保留各自阶段枚举为**私有 `_phase`/`_flowState` 字段**驱动 `FlowProcess`；私有 `SetStep(枚举, reason)` 内部：
1. 刷新 `_phase` + 调 `SetWeldStatus(MapWeldStatus(...))`；
2. 按旧 `OnWeldStatusChanged` 规则调 `GoStep(段位)`。

行为与新主控设计完全等价，规避旧 API 编译失败。对外仅暴露 `State`/`WeldStatus`/`WorkStep` 三态 + 步骤驱动三件套。

---

## 整机主控与安全：删除并归并

### DeviceControlWork（取代 MainDeviceWorkflow）

`public class DeviceControlWork`（单例，**独立管控类，不继承 `DeviceWorkflowBase`/`DeviceStateBase`**），自带运行线程（节拍 `BeatMs=10`）与内部执行步（`_workStep` + `GetStepName`）。对外状态为 `MainDeviceStatus`（6 态），原整机流程态 `MainDeviceFlowState` 不再存在（转内部私有执行步常量）。承接：

- 主设备运行态 `Status`(MainDeviceStatus) + `StatusChanged`(`MainDeviceStatusChangedEventArgs`)；内部 `SetStatus(...)` 为唯一写入入口
- 对外操作契约：`InitializeMachine` / `StartMachine` / `StopMachine` / `ResetMachine` / `ClearAlarm` / `EStopMachine` / `EStopCancel`；`EmergencyStop` / `ReportAlarm` / `ReportAlarmCleared`
- `RobotPose` / `RobotCommand` 命令消费（三槽：`_pendingPose` > `_pendingCommand` > `_pendingAbort`，Pose/Command 分槽避免 `StartSafePose=1` 与 `PreWeldRequest=1` 编码重叠丢指令）
- 模拟模式统一管理：`EnableSimulation` / `DisableSimulation` / `LoadSimulation` / `SaveSimulation` / `StartSimulationLineLaser` / `StopSimulationLineLaser` / `ResetSimulationLineLaser` / `StartRobotXSimulation` / `StopRobotXSimulation` / `IsSimulationEnabled` / `CurrentMode` / `SelectedMode` / `ShouldUseVirtualCamera` / `ShouldMoveAxis` / `SimStartX` / `SimSpeed` / `SimTargetDistance` / `SeamProfile` / `RandomMode` / `GetEffectiveRobotX`
- `IsWelding`（焊接中）、`WorkStep` / `WorkStepName`（内部执行步可观测）
- 子设备级联：经 `DeviceStatusWork.Instance.IsSafe` 门控；`ConnectOn`/`ConnectOff` 级联各子设备

> 主设备不再有「整机流程态」，改为 **主设备运行态（过程状态）** `MainDeviceStatus`。各 `SetStatus(...)` 调用见 `DeviceControlWork.cs`（Running/Alarm/EStop/Stop/NoReset/Reseting）。
> API 详见 [[api/MainDeviceWorkflow]]（现述 DeviceControlWork）。

### DeviceStatusWork（取代 SafetyWorkflow）

`public class DeviceStatusWork`（单例），安全检查三合一（`IsSafe` / `CheckDeviceStates` / 故障记录）归并至此；监控未启动返回 `true`（不阻断整机）。API 详见 [[api/SafetyWorkflow]]（现述 DeviceStatusWork）。

---

## 各工作流

| 工作流 | 私有阶段枚举 | 执行步 | 状态 | 说明 |
|---|---|---|---|---|
| `DeviceControlWork` | （无，直接 `MainDeviceStatus`） | — | 全实现 | 整机主控：三槽命令变量 + 上电初始化 5 步 + 机器人信号交互 + 模拟模式 |
| `LineLaserWorkflow` | `LineLaserWorkflowState`(私有) | 0/10/11/20/30/31/100/700/800/900 | 全实现 | 线激光焊缝跟踪，触发焊接工艺计算 |
| `MonitorCameraWorkflow` | `MonitorWorkflowState`(私有) | 0/10/20/30/800/900 | 全实现 | 监控相机触发采集/分析/结果 + 健康巡检 |
| `MotionControlWorkflow` | `LaserCamBoxWorkflowState`(私有) | 0/10/20/30/100/110/700/900 | 全实现 | CAMBOX 硬件实时跟踪（`BeatMs=20`） |
| `WeldParamControlWorkflow` | `WeldParamControlWorkflowState`(私有) | 0/10/20/800/900 | 全实现 | 焊接工艺计算与下发（**非设备**，命令变量触发） |
| `LaserWeldHeadWorkflow` | `LaserWeldHeadWorkflowState`(私有) | 仅 0 | 骨架 | 私有逻辑待实现（`IsRunLoopActive=false`，不启线程） |
| `DeviceStatusWork` | （无，三线程内部态 IOWork/EMGWork/StatusWork） | —（三线程非步骤驱动） | 全实现 | 安全/IO/状态管控：IOWork 互锁→Alarm、EMGWork 急停→EStop、StatusWork 反射三色灯 |

> 段位规范：0 待机 / 1~9 入口准备 / 10~99 主链路 A / 100~199 主链路 B / 700~799 清料 / 800~899 成功收尾 / 900~999 失败收尾。详见 [[standards/StepDrivenWorkflow]] 第五章。

### DeviceStatusWork — 安全/IO/状态管控（取代 SafetyWorkflow）

由 `SafetyFlow.cs`（阈值与 PLC 地址）+ `SafetyInterlock.cs`（互锁判定）+ `SafetyWorkflow.cs`（监控循环）合并后，整体迁为 `DeviceStatusWork.cs`（ADR-044 三合一 + ADR-049 归并）。设计参照 `PcomDeviceInterface/MachineStatusWork.cs` 的 IOWork/EMGWork/StatusWork 三线程模型（见 `主控设计.xlsx`「设备安全/IO/状态管控」泳道）。

**三线程（非步骤驱动）**：`DeviceStatusWork` 是独立管控类，不继承 `DeviceWorkflowBase`，由三个常驻线程驱动（各 20Hz）——`IOWork`（AboveNormal）周期互锁检查 → 失败 `ReportAlarm` + `RecordFault`，恢复 `ReportAlarmCleared`；`EMGWork`（Highest）急停轮询 → 按下 `EStopMachine`、释放 `EStopCancel`；`StatusWork`（Normal）反射 `DeviceControlWork.Status` 到三色灯。

**主设备门控**：`DeviceControlWork.IsRobotPoseSafe()` 读 `DeviceStatusWork.Instance.IsSafe`（监控未启动时不门控，返回 true）。

**随整机启动**：`StartWork()` 由 `DeviceControlWork.StartMachine` 调用、`CloseWork()` 由 `StopMachine`/`Dispose` 调用，不再需显式单独启动。

API 详见 [[api/SafetyWorkflow]]（现述 DeviceStatusWork）。

### DeviceControlWork — 上电初始化 5 步

```
[1/5] 焊接头 → [2/5] 运动控制器(+CAMBOX) → [3/5] 线激光(ConnectOn)
     → [4/5] 监控相机 → [5/5] 机器人通讯(RSI/EKI) → EvaluateInitializationResult()
```

聚合判定：子设备 `Connected` 正常，否则计为未就绪。全就绪→`MainDeviceStatus.Stop`（整机就绪）→ 待 `Running`；否则→`MainDeviceStatus.Alarm`。

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
| `ProductFileManager/FaultRecoveryManager.cs` | **已迁出本模块（2026-09-01，ADR-046 §3）**：单例，故障恢复闭环 + `FaultCategory` / `FaultRecord` 数据载体；本目录 7 工作流为其消费方 |

详见 [[modules/Safety]]、[[modules/ProductFileManager]]、[[api/SafetyWorkflow]]。

重试策略：通讯 3 次/5s、相机 2 次、线激光 3 次、安全类 0 次。

> **P0 坑**：故障恢复设备键名必须用**英文 key**，与 `RegisterRecoveryStrategy` 注册一致。详见 [[lessons/FaultRecoveryDeviceKey]]。

---

## UI 接入

须引入 `using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;`（读连接态另需 `using AdaWeldSystem.MainDeviceControl.DeviceState;`）

**三个属性不可混淆**：

| 属性 | 含义 | 用途 |
|---|---|---|
| `Instance.WeldStatus` | 焊接过程态（`SubDeviceWeldStatus`） | 判断是否运行、显示分步进度 |
| `Instance.State` | 连接态（`SubDeviceState`） | 判断能否操作、销毁前是否断开 |
| `Instance.WorkStep` / `StepStatusText` | 执行步（内部游标） | **现场排故**：卡在哪个子步、卡了多久 |

`StepStatusText` 形如 `"step:21 / 3.4s 等待数据稳定"`，可直接挂 UI 状态标签；卡死时步号不动、时长持续涨。
红线：UI 线程**禁止直接调用 `FlowProcess()`**（[[standards/StepDrivenWorkflow]] 红线 6）。

当前接入：`FormMain.cs`、`ILCamPage.cs`、`MonitorCamPage.cs`、`MotionControlPage.cs`、`MainPage.cs`

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
- C# 7.3（[[decisions/ADR-002-CS73-Constraint]]）：禁 switch 表达式、属性模式、nullable、record、range
- 非 UI 类统一标准 `IDisposable.Dispose()`（[[decisions/ADR-001-DisposePattern]]、[[decisions/ADR-034-DisposePatternFullCoverage]]）
- 振镜摆幅 `CalcGalvoAmplitude` 为 TODO 占位返回 0.0，`WeaveWidth` 是查表项而非公式
- 旧四态 `DeviceState` 枚举、泛型 `WorkflowStateBase<TStep>`/`DeviceWorkflowBase<TStep>`、`MainDeviceFlowState` 枚举均已删除，引用这些旧符号的代码/文档视为冲突，须改用三态模型
