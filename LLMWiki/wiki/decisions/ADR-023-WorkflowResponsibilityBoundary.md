---
title: ADR-027 流程与子设备对象权责边界（R1~R5）
date: 2026-08-31
status: accepted
tags: [决策, 架构, 工作流, 权责边界, 事件, 子设备, ADR-027]
---

> ⚠️ 历史名称提示：本页为**历史决策记录**，正文中的下列文件名为决策当时的旧名，
> 保留原文以留存上下文，现役对应如下：
>
> - `MainDeviceWorkflow.cs` → 现役 `MainDeviceControl/DeviceControlWork.cs`
>

# ADR-027 流程与子设备对象权责边界

> **唯一可执行细则见 [[standards/WorkflowResponsibilityBoundary]]**（由 `index.md` 路由，触发即读，免用户重复输入）。本 ADR 只记录"为什么这样决策"。
>
> **术语已更新（2026-09-02，ADR-028 三态模型）**：本 ADR 成文时的「流程态对外枚举 + `MapToDeviceState` 四态映射」已废止——各工作流的阶段枚举降为**私有**，对外只暴露 `SubDeviceState`（连接态）/ `SubDeviceWeldStatus`（焊接过程态）/ `MainDeviceStatus`（整机运行态）。文中 `MainDeviceWorkflow` 现为 `DeviceControlWork`、`SafetyWorkflow` 现为 `DeviceStatusWork`、泛型 `WorkflowStateBase<TStep>` 已删除（现为非泛型 `DeviceWorkflowBase`）。**R1~R5 五条规则本身继续有效**，仅承载者改名。

## 背景

用户在审查 `MonitorCameraWorkflow` 时提出质疑：

> 监控相机流程下很多完成事件。我们有专门的监控相机的代码（`MonitorCameraRun`）。流程只是在触发和调用、读取结果，不是对监控相机的图像负责的。是不是流程和子设备对象的权责不清晰？

全量核查 6 个子流程后确认：**权责边界此前从未被显式定义**，导致流程层逐步吸附了三类本不属于它的职责。

### 核查发现（2026-08-31）

| 越权类型 | 实例 | 数量 |
|---|---|---|
| 流程输出设备/算法数据 | `MonitorCameraWorkflow.DisplayEvent`（Mat 图像）、`ResultEvent`（算法结果）、`StatusChanged`（相机健康） | 3 |
| 流程转发子设备事件 | `MotionControlWorkflow.TrackingError` / `PointAdded`（转发 `CamBoxTracker`） | 2 |
| 流程自造流程态事件 | `MonitorCameraWorkflow.ErrorAborted` / `ManualStopped`、`MainDeviceWorkflow.FlowStateSwitched` / `PowerOnInitializeCompleted` | 4 |
| 流程职责外推为事件 | `WeldParamControlWorkflow.ParamOutputReady`（职责本是"计算后下发机器人"这一动作） | 1 |
| 流程态含外部职责态 | `MonitorWorkflowState.Displaying`（显示属 UI） | 1 |
| 依赖倒置 | `MonitorCameraRun`（子设备）`using ...MainDeviceControl.DeviceWorkflow`（因 `MonitorCameraPhase` 枚举定义在流程文件内） | 1 |

其中 **5 个事件零订阅**，属纯死代码；`DisplayEvent` 与 `MonitorCameraRun.FrameCompletedEvent` 功能重复，构成双通道。

## 决策

确立五条权责规则（R1~R5），流程层职责收敛为：**触发 → 调用 → 读取结果 → 推进流程态 → 执行动作**。

| 编号 | 规则 | 判据 |
|---|---|---|
| **R1** | 数据产出归属：谁产生数据，谁输出事件 | 流程不得输出设备数据（图像/连接态/健康度）与算法结果 |
| **R2** | 禁止转发子设备事件 | 订阅方直接订阅子设备对象；流程只暴露子设备属性（如 `Tracker`） |
| **R3** | 流程态通知统一 | 起停/终止/完成一律由基类 `StateChanged(WorkflowStepChangedEventArgs<TStep>)` 承载 |
| **R4** | 流程做动作而非抛事件 | 结果以只读属性暴露（如 `LastOutput` / `LastResult`），不抛事件等订阅 |
| **R5** | 流程态只描述流程 | 流程态枚举不得含 UI/显示等外部职责态 |

### 判定口诀

> **数据是设备的，进度是流程的。**
> 流程可以读数据、可以叫设备干活，但不能替设备发数据、不能替设备喊健康、不能把设备的事件再喊一遍。

### 合规范式

`LineLaserWorkflow` 与 `LaserWeldHeadWorkflow` 零自定义事件，仅依赖基类 `StateChanged` —— 本次核查确认的正确范式。

## 备选方案

| 方案 | 放弃原因 |
|---|---|
| 维持现状，仅补注释说明 | 注释无法阻止继续劣化；5 个零订阅事件已成死代码 |
| 统一用 `GlobalCommData` 事件总线广播 | 全局总线会让权责更模糊，且丢失类型安全 |
| 保留 `DisplayEvent` 作为"分析结果图"专用通道 | 与 `FrameCompletedEvent` 双通道，且叠加图可直接由流程只读属性暴露 |

## 后果

### 正面

- 监控相机健康能力回到 `MonitorCameraRun`，`MonitorCameraWorkflow` 由 665 行降至 435 行（-35%）
- 全项目自定义工作流事件由 11 个降至 1 个（`WeldParamControlWorkflow` 无，实际降至 **0** 个越权事件）
- 消除 `DisplayEvent`/`FrameCompletedEvent` 双通道与 5 处零订阅死代码
- 解除子设备对流程层的反向依赖（`MonitorCameraPhase` 下沉至 `MonitorCam/Api`）

### 负面

- `MonitorCameraRun` 新增巡检线程，需关注线程生命周期（已纳入 `Dispose`）
- UI 由"推模式"改为"推状态 + 拉数据"，订阅方需在 `StateChanged` 后主动读取只读属性

## 实施清单

| 文件 | 变更 |
|---|---|
| `MonitorCam/Api/IMonitorCameraApi.cs` | 新增 `MonitorCameraPhase`、`MonitorSupervisionState`、`MonitorSupervisionStatusChangedEventArgs` |
| `MonitorCam/MonitorCameraRun.cs` | 承接健康巡检（`StartSupervision`/`StopSupervision`/`SupervisionState`/`LastHealthyTime`/`IsMonitorCameraWorking` + `StatusChanged`）；移除对流程层的 using |
| `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` | 删 5 事件 + 5 参数类 + 健康巡检块 + `Displaying` 态；结果改 `LastResult`/`LastOverlay` 只读属性 |
| `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` | 删 `TrackingError`/`PointAdded` 转发与 `LaserCamBoxTrackingErrorEventArgs`；异常仅记日志 |
| `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` | 删 `ParamOutputReady` |
| `MainDeviceControl/DeviceWorkflow/MainDeviceWorkflow.cs` | 删 `FlowStateSwitched`（含 `OnStepChanged` 重写）与 `PowerOnInitializeCompleted` |
| `UIDesign/TabPage/MonitorCamPage.cs` | 订阅平移：图像←相机、流程态←基类、结果按需拉取；新增健康状态显示 |
| `UIDesign/MainWindow/FormMain.cs` | `FlowStateSwitched` → `StateChanged` |

## 反例警示（勿重犯）

| 反例 | 正确做法 |
|---|---|
| 流程里 `TriggerDisplay()` 抛图像事件 | 图像归 `MonitorCameraRun.FrameCompletedEvent`；叠加图由流程只读属性暴露 |
| 流程里做设备健康巡检 | 归位到相机/设备对象自身 |
| 把 `CamBoxTracker` 事件在流程里再抛一遍 | 订阅方订阅 `MotionControlWorkflow.Instance.Tracker` |
| 给流程加 `XxxCompleted` 事件 | 用基类 `StateChanged`，`NewState` 即完成态 |
| 流程算完参数抛 `ParamOutputReady` 等外部订阅 | 流程直接执行动作（下发），结果放 `LastOutput` |
| 流程态枚举里放 `Displaying` | 流程态只描述流程进度 |
| 子设备枚举定义在流程文件里 | 放子设备自己的 Api 层 |

## 关联

- 标准页（执行细则）：[[standards/WorkflowResponsibilityBoundary]]
- 架构：[[architecture/DeviceControlArchitecture]]
- 模块：[[modules/DeviceControl]]、[[modules/MonitorCam]]
- API：[[api/MonitorCameraWorkflow]]、[[api/MonitorCamManager]]、[[api/MotionControlWorkflow]]、[[api/WeldParamControlWorkflow]]、[[api/DeviceControlWork]]
- 互补规范：[[standards/CodeSimplification]]（死代码/过度属性）、[[standards/UiStateSimplification]]（UI 真相源唯一）
