---
title: ADR-049 主控设计三态模型重构（SubDeviceState / SubDeviceWeldStatus / MainDeviceStatus）
date: 2026-09-02
tags: [决策, 架构, 设备控制, 主控设计, 三态模型, 状态机, 重构, ADR-049, 取代ADR-041, 取代ADR-042]
status: accepted
supersedes: [ADR-041, ADR-042]
---

# ADR-049：主控设计三态模型重构

> **2026-09-02 接受**：用户提交新主控设计（`主控设计.xlsx`，原档约定见 [[decisions/ADR-050-ArchitectureRawSource]]），对设备控制层状态模型做根本性重定义。
> 本 ADR 取代 [[decisions/ADR-041-MainDeviceControlArchitecture]]、[[decisions/ADR-042-WorkflowStateBaseGeneric]] 的设计。
> **[[decisions/ADR-047-StepDrivenWorkflow]] 步骤驱动机制沿用**（三件套由新基类承载，见 §3）；**[[decisions/ADR-048-AutoManualDualWorkflow]] 部分取代**（`FlowProcess` 唯一执行器沿用；`ManualOn`/`ManualOff` 契约由 `ConnectOn`/`ConnectOff` 取代，见 §3）。
> 旧四态 `DeviceState` 枚举、泛型 `WorkflowStateBase<TStep>` / `DeviceWorkflowBase<TStep>`、`MainDeviceFlowState` 枚举均已删除。

## 背景

旧设计采用「设备四态 `DeviceState`(Disconnect/Connect/Work/Alarm) + 流程态(各工作流自有枚举) + 执行步(int)」三层模型，基类为泛型 `DeviceWorkflowBase<TStep>`。
新主控设计明确：

- **原「流程态」概念不再存在**；设备侧状态收敛为两个正交枚举 + 一个主设备过程态。
- 主设备不再有「整机流程态」，改为 **主设备运行态（过程状态）**。

## 决策

### 1. 三枚举状态模型（取代设备四态 + 流程态）

| 枚举 | 取值 | 用途 | 命名空间 |
|---|---|---|---|
| `SubDeviceState` | `Disconnected`(0) / `Connected`(1) | 子设备连接态（只两态） | `AdaWeldSystem.MainDeviceControl.DeviceState` |
| `SubDeviceWeldStatus` | `Standby`(0)/`PreWork`(1)/`Starting`(2)/`Working`(3)/`Stopping`(4)/`ErrorAborted`(5)/`ManualStopped`(6) | 子设备焊接过程态（7 态） | 同上 |
| `MainDeviceStatus` | `Running`(0)/`Alarm`(1)/`EStop`(2)/`Stop`(3)/`NoReset`(4)/`Reseting`(5) | 主设备运行态（6 态，过程状态） | 同上 |

- 旧 `DeviceState` 四态枚举 **已删除**；`FaultRecord.State` 由 `DeviceState` 改型为 `SubDeviceWeldStatus`（[[modules/ProductFileManager]]）。
- 旧各工作流自有流程态枚举（`LineLaserWorkflowState`/`MonitorWorkflowState`/`LaserCamBoxWorkflowState`/`WeldParamControlWorkflowState`/`LaserWeldHeadWorkflowState`）**降为私有 `_phase`/`_flowState` 字段，仅驱动 `FlowProcess()`，不再对外暴露**；对外状态经 `SubDeviceWeldStatus` 承载。

### 2. 状态写入唯一入口（取代 `SetStep` + `MapToDeviceState` + 手工 `State=`）

| 方法 | 承载 | 触发事件 |
|---|---|---|
| `SetState(SubDeviceState, reason)` | 连接态（基类 `protected`） | `StateSwitched`(`SubDeviceStateChangedEventArgs`) |
| `SetWeldStatus(SubDeviceWeldStatus, reason)` | 焊接过程态（基类 `protected`） | `WeldStatusChanged`(`WeldStatusChangedEventArgs`) |
| 主设备运行态由 `DeviceControlWork.SetStatus(MainDeviceStatus, reason)` | — | `StatusChanged`(`MainDeviceStatusChangedEventArgs`) |

> 禁止任何子类手工 `State = ...` / `WeldStatus = ...` 赋值（强制走上述方法，与旧设计红线一致）。

### 3. 非泛型 `DeviceWorkflowBase`（取代 `WorkflowStateBase<TStep>` + `DeviceWorkflowBase<TStep>`）

`public abstract class DeviceWorkflowBase : DeviceStateBase, IDisposable`（namespace `AdaWeldSystem.MainDeviceControl.FlowState`）。

**六抽象契约 + `GetStepName(int)`（子类实现）**：

| 成员 | 说明 |
|---|---|
| `FlowProcess()` | 单步分派 `switch(WorkStep)`，监听线程按节拍调用，**自动运行唯一执行器** |
| `bool ResetProcess()` | 复位流程（急停/报警后回待机） |
| `ClearStatus()` | 清除报警（仅清报警态回就绪态，与复位正交） |
| `ResetWorkTime()` | 复位工作时间计时 |
| `bool ConnectOn()` | 手动连接（子类内部自起后台线程，UI 开关直调，返回是否受理） |
| `ConnectOff()` | 手动断开（子类内部自起后台线程） |
| `protected abstract string GetStepName(int)` | 执行步号→中文名映射表 |

> `ConnectOn`/`ConnectOff` 取代旧 `ManualOn`/`ManualOff`/`InitializeFlow`/`ResetFlow`/`ClearAlarmFlow`；旧 `Initialize()`/`Reset()`/`ClearAlarm()` 三公开生命周期由基类模板方法承载（记日志后调用上述契约）。

**步骤驱动三件套（基类提供）**：`GoStep(int)`（唯一改步入口）/ `ResetStepTime()` / `IsStepTimeout(double)` / `FailFlow(reason)` / `StartRunLoop()`/`StopRunLoop()` / `ConsumeCommand()` / `BeatMs`(默认10) / `RunLoopPriority` / `DisposeManaged()`（子类释放钩子，ADR-001）。
段位规范、命名约定（`StepXxx`/`DoXxx`）、失败重试零代码、超时置 Alarm 等沿用 [[standards/StepDrivenWorkflow]]。

### 4. 删除并归并整机主控与安全流程

- **`MainDeviceWorkflow` 删除** → 新建 **`DeviceControlWork`**（单例）：承接 `MainDeviceStatus` 运行态、上电初始化级联（`InitializeMachine`/`StartMachine`/`StopMachine`/`ResetMachine`/`ClearAlarm`/`EStopMachine`/`EStopCancel`）、`RobotPose`/`RobotCommand` 命令消费、模拟模式统一管理（`EnableSimulation`/`DisableSimulation`/`LoadSimulation`/`SaveSimulation`/`StartSimulationLineLaser`/`StopSimulationLineLaser`/`ResetSimulationLineLaser`/`IsSimulationEnabled`/`CurrentMode`/`SelectedMode`/`SimStartX`/`SimSpeed`/`SimTargetDistance`/`SeamProfile`/`RandomMode`/`GetEffectiveRobotX`）。
- **`SafetyWorkflow` 删除** → 新建 **`DeviceStatusWork`**（单例）：安全检查三合一（`IsSafe`/`CheckDeviceStates`/故障记录）归并至此；监控未启动返回 `true`（不阻断整机）。
- `SimulationWorkflow` 此前已删除，成员现全部归属 `DeviceControlWork`。

### 5. UI 接入变更

| 旧（已删除） | 新 |
|---|---|
| `Instance.State`(四态) | `Instance.State`(`SubDeviceState`) / `Instance.WeldStatus`(`SubDeviceWeldStatus`) |
| `Instance.Step`(流程态枚举) | `Instance.WeldStatus` / `Instance.WorkStep`(int 执行步) |
| `StateChanged`(`WorkflowStepChangedEventArgs<TStep>`) | 连接态 `StateSwitched`(`SubDeviceStateChangedEventArgs`)；焊接过程态 `WeldStatusChanged`(`WeldStatusChangedEventArgs`) |
| `ManualOn()`/`ManualOff()` | `ConnectOn()`/`ConnectOff()` |
| `MainDeviceWorkflow.Instance` | `DeviceControlWork.Instance` |

## 影响文件

- 基类：`MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs`（三枚举 + 事件参数）、`DeviceWorkflowBase.cs`（非泛型）
- 子工作流：`LineLaserWorkflow` / `MonitorCameraWorkflow` / `MotionControlWorkflow` / `WeldParamControlWorkflow` / `LaserWeldHeadWorkflow`（基类改 `DeviceWorkflowBase`，私有 `_phase`/`_flowState` + 私有 `SetStep` 等价旧 `OnStepChanged`）
- 新建：`DeviceControlWork.cs`、`DeviceStatusWork.cs`
- 删除：`MainDeviceWorkflow.cs`、`SafetyWorkflow.cs`、`WorkflowStateBase.cs`
- csproj：`DeviceWorkflowBase.cs`/`DeviceControlWork.cs`/`DeviceStatusWork.cs` 注册；`WorkflowStateBase.cs`/`MainDeviceWorkflow.cs`/`SafetyWorkflow.cs` 移除
- 消费方（UI）：`FormMain.cs` / `MainPage.cs` / `ILCamPage.cs` / `MonitorCamPage.cs` / `MotionControlPage.cs`；`FaultRecoveryManager.cs`（`FaultRecord.State` 改型）
- 模块文档：[[modules/DeviceControl]]、[[modules/Safety]]；API：[[api/MainDeviceWorkflow]]（现述 DeviceControlWork）、[[api/SafetyWorkflow]]（现述 DeviceStatusWork）

## 已知约束

- 本环境无法编译，改动后须静态自检（类型解析 / csproj 完整性 / 无孤儿文件 / `Dispose(bool)` 禁止 / 继承链）。
- 等价最小改写：子工作流保留各自阶段枚举为私有字段驱动 `FlowProcess`，私有 `SetStep` 内部刷新 `_phase` + 调 `SetWeldStatus(MapWeldStatus(...))` + 按旧 `OnStepChanged` 规则调 `GoStep(段位)`——行为与旧设计完全等价，规避旧 API 编译失败。
