---
title: ADR-012 运控调整模块架构决策
date: 2026-07-16
tags: [决策, 运控, 模块, 解耦, VirtualCam, MotionControl]
status: accepted
source: 用户反馈「新增功能必须遵循代码规则」+ 本模块设计
---

> ⚠️ 历史名称提示：本页为**历史决策记录**，正文中的下列文件名为决策当时的旧名，
> 保留原文以留存上下文，现役对应如下：
>
> - `HorizontalMoveWorkflow.cs` → 已移除（ADR-012 后移除）
>

# ADR-012：运控调整模块架构决策

## 背景

「运控调整三件套」（水平移动标定/缓存 + 虚拟相机模拟 A/B/C + 运控参数 UI）初版实现**违反了用户既定的代码规则**：
- 虚拟调试相机 `VirtualCameraRun` / `CameraSelector` 被错误挂在 `SmartRayCam/` 下（用户要求「虚拟相机的层级与 SmartRay 同级」）；
- 运控数据 `MoveControlData` / `IMotionAxisController` 被错误挂在 `InteliWeld/` 下，模拟 A/B/C 与水平移动线程的 hack 被塞进 `Workflow/LineLaserWorkflow.cs` 与 `Workflow/HorizontalMoveWorkflow.cs`（用户要求「控制流程的 UI 和数据需要遵循流程开发」，即归入独立流程模块）。

这同时违背了 [[decisions/ADR-009-MonitorCameraModule]] 确立的「新增功能 = 独立模块；SDK 抽象接口放 `模块/Api/`；`XxxRun`(设备控制) 与 `XxxWorkflow`(编排) 分离；枚举/事件参数放 `Comm/SystemComm.cs`」范式。

## 决策

1. **新增独立模块 `VirtualCam`**（与 `SmartRayCam` **平级**）：含 `VirtualCameraRun`（虚拟相机，`ICameraRun` 实现）与 `CameraSelector`（相机选择器静态类）。
2. **新增独立模块 `MotionControl`**（不挂载于 InteliWeld）：含 `MoveControlData`（运控标定+计算+缓存）、`IMotionAxisController`（运动轴接口 + `NullMotionAxisController` 空实现）、`MotionControlWorkflow`（运控调整工作流状态机：水平移动后台线程 + A/B/C 模拟 + 机器人X模拟）。
3. **相机运行契约 `ICameraRun` 放 `SmartRayCam/Api/`**（命名空间 `AdaWeldSystem.SmartRayCameraRun`）：真实 `CameraRun` 与虚拟 `VirtualCameraRun` 共享，工作流/界面仅依赖接口。
4. **Run / Workflow 分离**：`VirtualCameraRun`（设备控制，IDisposable）与 `MotionControlWorkflow`（编排，状态机）各司其职。
5. **枚举与事件参数放 `Comm/SystemComm.cs`**：`SimTestMode` / `MotionControlWorkflowState` / `MotionControlStateChangedEventArgs`（命名空间级，非嵌套，遵循 [[guides/Namespace-Compilation]]）。
6. **配置/资源释放规范**：遵循 [[decisions/ADR-001-DisposePattern]]（`DisposeComponents()` 不重写 `Dispose(bool)`）、[[decisions/ADR-002-CS73-Constraint]]（构造函数初始化，无 auto-property initializer）、[[decisions/ADR-005-CallbackAcquisition]]（回调等待取图）、[[decisions/ADR-007-ConfigLayout]]。

## 关键设计

- `MotionControlWorkflow` 水平移动线程消费 `MoveControlData` 缓存，`GetEffectiveRobotX()` 统一读取（真实/模拟）；A/B/C 模拟循环取图经 `CameraSelector.Active` 后回调等待 `AcquisitionCompletedSignal`。
- `MoveControlData.ComputeAndCacheHorizontalMove` 为水平移动计算**单一真源**，被 `WeldProcess`（真实流程）与 `MotionControlWorkflow`（模拟流程）统一调用，消除逻辑分散（修复 [[guides/Namespace-Compilation]]）。
- `IMotionAxisController` 插拔式：默认 `NullMotionAxisController` 留空，待对接 KUKA。
- `WeldProcess` 仅保留 `CurrentRobotX`（真实坐标）与对 `MoveControlData` 的委派；移除了 `SimStartX`/`SimSpeed`/机器人X模拟等运控专属字段。

## 后果

- 优点：运控功能完全独立，符合用户代码规则与 ADR-009 范式；虚拟相机与 SmartRay 平级；数据/UI/流程归属清晰，新增硬件对接仅需实现 `IMotionAxisController` 与切换 `CameraSelector`。
- 代价：模块数增多（VirtualCam / MotionControl），多一层单例与线程状态管理；初版返工成本。
- 历史：初版（2026-07-15/16）误挂子目录，2026-07-16 按本 ADR 重构成平级独立模块；2026-07-17 将运控参数 UI 由 `Sub3UI/MotionControlParamForm`（误置弹窗目录）迁入 `Sub2UI/MotionControlPage` 并改为设计器生成（`.Designer.cs` 布局），接入 `Sub1UI/ParamPage` 工艺配置节点，符合 ParamPage 子页均位于 Sub2UI 的既有约定。

## 涉及约束

- [[decisions/ADR-001-DisposePattern]] ✅
- [[decisions/ADR-002-CS73-Constraint]] ✅
- [[decisions/ADR-004-WorkflowStepEnum]] ✅（状态机）
- [[decisions/ADR-005-CallbackAcquisition]] ✅
- [[decisions/ADR-007-ConfigLayout]] ✅
- [[decisions/ADR-009-MonitorCameraModule]] ✅（范式复用）
- [[guides/Namespace-Compilation]] ✅（6 新文件注册 .csproj）
- [[guides/Namespace-Compilation]] ✅（枚举命名空间级）
- [[guides/Namespace-Compilation]] ✅（确保 `MoveControlData.ComputeAndCacheHorizontalMove` 等被引用方法确实存在）

---

*来源：AdaWeldSystem/VirtualCam/ + AdaWeldSystem/MotionControl/ 模块源码 + 用户反馈*
