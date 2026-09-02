---
title: ADR-015 Workflow 模块作为流程管理中枢
date: 2026-07-17
tags: [决策, 工作流, 模块, 迁移, 监督]
status: accepted
source: 用户需求「Workflow 统一管理所有工作流程」
---

# ADR-015：Workflow 模块作为流程管理中枢

## 状态
已采纳（2026-07-17）｜**已被取代（2026-09-01 治理标注）**

> **⚠️ 已被取代 —— 中枢载体与监督机制均已变更**
> - ❌ **失效 1（目录）**：「所有工作流迁入 `Workflow/`、命名空间 `AdaWeldSystem.Workflow`」已被 [[decisions/ADR-041-MainDeviceControlArchitecture]] 推翻——中枢目录现为 `MainDeviceControl/DeviceWorkflow/`。
> - ❌ **失效 2（监督）**：决策 2 的 `MonitorSupervisionWorkflow`（后台轮询 + `StatusChanged` 事件）已被 [[decisions/ADR-043-WorkflowResponsibilityBoundary]] 推翻——健康巡检下沉子设备 `MonitorCameraRun`，工作流零自定义事件、只做编排。
> - ✅ **仍然有效**：决策 1 `MonitorAlgorithmManager`（单例 + INI 持久化、无 JOB 切换）维持不变。
> - **当前真相源**：[[modules/DeviceControl]]、[[standards/WorkflowResponsibilityBoundary]]、[[api/MonitorCameraRun]]。

## 背景

系统中的工作流编排器原本分散在多个模块：
- `LineLaserWorkflow` 在 `Workflow/`（线激光 3D 采集 + 焊缝跟踪）
- `MonitorCameraWorkflow` 在 `MonitorCam/`（焊前对中 / 焊中质检，采集→分析→显示→结果）
- `MotionControlWorkflow` 在 `MotionControl/`（水平移动 + A/B/C 模拟，2026-07-16 由 ADR-014 归入 MotionControl 模块）

用户明确：① 监控相机算法需单独做管理器并持久化；② 单独开一个监控流程判断监控相机是否工作/工作状态/工作内容，放入 Workflow；③ `MotionControlWorkflow` 也应移入 `Workflow`，**因为 Workflow 是对所有工作流程进行管理的**。

## 决策

1. **新增 `MonitorAlgorithmManager`**（单例，位于 `MonitorCam/`）：持有监控相机唯一一套可配置算法参数（对中容差 / 质量合格分），持久化到 `Config/INI/MonitorAlgorithm.ini`，**无 JOB 切换**（针对仅是焊缝检查、无多种类）。`MonitorCameraWorkflow.AnalyzeImage()` 改从该管理器读取，取代从 `MonitorCameraConfig` 直接取阈值，实现算法配置与相机硬件配置分离（镜像 EmguALG 的 AlgorithmManager 范式）。
2. **新增 `MonitorSupervisionWorkflow`**（单例，位于 `Workflow/`）：对监控相机子系统健康巡检，回答「是否工作 / 工作状态 / 工作内容（检测阶段）」三问；后台轮询线程 + `StatusChanged` 事件上报；与 `MonitorCam` 单向依赖。
3. **将 `MotionControlWorkflow` 从 `MotionControl/` 迁移至 `Workflow/`**（命名空间 `AdaWeldSystem.Workflow`），由 Workflow 统一管理所有工作流。其依赖的 `MoveControlData` / `IMotionAxisController` 仍留在 `MotionControl` 模块（数据/接口层），`Workflow → MotionControl` 单向依赖，无循环依赖。

## 关键设计

- `MotionControlWorkflow` 迁移后须补 `using AdaWeldSystem.MotionControl;`（原靠同命名空间访问 `MoveControlData`/`IMotionAxisController`/`NullMotionAxisController`），否则编译失败（见 [[guides/Namespace-Compilation]]）。
- `MonitorSupervisionWorkflow` 的状态枚举与事件参数定义在 `Workflow` 文件内（命名空间级），**不放入 `Comm/SystemComm.cs`**，以避免 `Comm` 反向依赖 `MonitorCam.Api` 形成循环依赖。
- `MonitorAlgorithmManager` 的 `Load()` 与 `SimulationWorkflow.Instance.Load()` 均在 `FormMain` 启动期、创建子页面前集中调用（参见 [[guides/Project-Tools]]）。

## 后果

- 优点：所有工作流编排器集中于 `Workflow`，职责清晰、便于统一驱动与监督；监控相机算法配置独立持久化。
- 代价：`Workflow` 模块新增对 `MonitorCam` / `MotionControl` 的依赖（单向，无循环）；ADR-014 中「MotionControlWorkflow 归属 MotionControl 模块」的归属被本 ADR 推翻（仅工作流文件迁移，数据/接口仍留 MotionControl）。

## 涉及约束

- [[decisions/ADR-001-DisposePattern]] ✅（DisposeComponents，不重写 Dispose）
- [[decisions/ADR-002-CS73-Constraint]] ✅
- [[decisions/ADR-003-SingleAlgorithmFile]] ✅（算法仍在 ImageAlgorithm.cs）
- [[decisions/ADR-004-WorkflowStepEnum]] ✅（状态机）
- [[decisions/ADR-008-ConfigLayout]] ✅（INI 归 Config/INI）
- [[decisions/ADR-011-MonitorCameraModule]] ✅（Run/Workflow 分离、SDK 抽象保留）
- [[guides/Namespace-Compilation]] ✅（新文件已注册 .csproj）
- [[guides/Project-Tools]] ✅
- [[guides/Namespace-Compilation]] ✅（迁移类补 using）

---

*来源：AdaWeldSystem/Workflow/ + AdaWeldSystem/MonitorCam/MonitorAlgorithmManager.cs + 用户需求*

---

> **更新（2026-08-03）**：`MonitorSupervisionWorkflow` 已于 2026-08-03 合并入 `MonitorCameraWorkflow`。原监督工作流的巡检逻辑（是否工作 / 工作状态 / 工作内容）已整合至 `MonitorCameraWorkflow` 内部，不再作为独立工作流存在。
