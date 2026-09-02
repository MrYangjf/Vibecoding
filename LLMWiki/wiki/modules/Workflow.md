---
title: Workflow 模块 — 已删除（重定向存根）
date: 2026-09-01
tags: [模块, 已删除, 重定向, 工作流]
status: deleted-placeholder
redirect_to: modules/DeviceControl
---

# Workflow 模块 — 已删除

> **本模块已不存在，本页仅作链接重定向存根**，避免既有 26 处引用成为红链。**不得作为开发依据。**
>
> - `AdaWeldSystem/Workflow/` 目录：2026-08-28 整目录删除。
> - `MainDeviceControl/WorkflowState.cs`（共享状态契约）：同日删除，状态枚举与事件参数**内联至各工作流文件**。
> - `AdaWeldSystem.Workflow` 命名空间**不复存在**。
>
> 决策记录：[[decisions/ADR-041-MainDeviceControlArchitecture]]、[[decisions/ADR-027-WorkflowStateFileConsolidation]]。

## 内容去向

| 原内容 | 现在在哪 |
|---|---|
| 线激光 / 监控相机 / 运控 CAMBOX / 焊接工艺 / 焊接头工作流实现 | `MainDeviceControl/DeviceWorkflow/` → [[modules/DeviceControl]]、[[architecture/DeviceControlArchitecture]] |
| `LineLaserWorkflowState` 等流程态枚举 | 内联至各自工作流文件（ADR-042 后由泛型基类 `WorkflowStateBase<TStep>` 承载通用机制） |
| `WorkflowSignalCode` / `WorkflowCompletedEventArgs` / `WorkflowErrorAbortedEventArgs` / `WorkflowManualStoppedEventArgs` | **零消费，已直接删除**（ADR-043 R3：流程态通知统一走基类 `StateChanged`） |
| `SimulationWorkflow`（原 `SimulationController`） | `MainDeviceControl/DeviceWorkflow/SimulationWorkflow.cs` → [[api/SimulationWorkflow]] |
| `WeldActionRecord` | `PCLOperate/RunFileRecord/WeldActionRecord.cs` → [[decisions/ADR-012-WeldActionRecord]] |

## 请改读

- [[modules/DeviceControl]] — 设备控制模块（工作流实现类与设备态体系）
- [[architecture/DeviceControlArchitecture]] — 设备控制架构（唯一规范页）
- [[standards/WorkflowResponsibilityBoundary]] — 流程与子设备权责边界
