---
title: ADR-027 工作流状态文件合并
date: 2026-08-04
tags: [决策, 工作流, 状态枚举, 文件合并, 代码组织]
status: accepted
---

# ADR-027：工作流状态文件合并

> **2026-08-28 废止说明**：本 ADR 决定的「状态契约集中到 WorkflowState.cs」已被 ADR-041 二次修订推翻——契约按归属内联至各工作流文件，WorkflowState.cs 已删除。本页仅作历史追溯。

## 背景

工作流状态枚举和事件参数原分散于三个独立文件：

- `Workflow/LineLaserWorkflowState.cs` — 线激光工作流状态
- `Workflow/MonitorWorkflowState.cs` — 监控相机工作流状态
- `Workflow/MotionControlWorkflowState.cs` — 运控调整工作流状态

三个文件之间存在以下问题：
1. 枚举定义分散，维护时需要跨文件查找
2. 存在潜在的枚举重复定义风险（见 [[decisions/ADR-026-EnumDeduplication]]）
3. 用户明确要求「工作流程的状态文件集合到一个 WorkflowState.cs 中」

同时，本次合并还修复了三个发现的问题：
- **属性名遮蔽**：`LineLaserWorkflow`、`MotionControlWorkflow`、`MonitorCameraWorkflow` 中的 `DeviceState` 属性名遮蔽了 `DeviceState` 枚举，导致 `TryTransition(DeviceState.Working, ...)` 编译错误。修改为 `StateMachine`。
- **MotionControlStateMachine 缺少 Initializing 状态**：`DeviceState` 枚举定义了 `Initializing` 状态，但 `MotionControlStateMachine` 的转换表未包含该状态。已补全 `Uninitialized → Initializing → Standby` 路径。
- **DeviceStatusModels 无效状态字符串**：使用了 `"Disconnected"`、`"Idle"`、`"Connected"` 等不在 `DeviceState` 枚举中的字符串，已统一替换为合法值。

## 决策

将三个工作流状态文件合并为单一 `Workflow/WorkflowState.cs`，使用 `#region` 分区组织不同工作流的状态定义。

## 备选方案

1. **保持三个文件分离** — 已被用户规则明确否决
2. **合并到 `Comm/SystemComm.cs`** — 会导致 `SystemComm.cs` 膨胀，且工作流状态与通讯模块无直接关系，违反模块边界
3. **合并为单一 `WorkflowState.cs`（采用）** — 集中管理、便于查找、消除重复定义风险

## 后果

### 正面
- 所有工作流状态定义集中在一个文件，便于查找和维护
- 消除跨文件枚举重复定义风险
- `DeviceState` → `StateMachine` 重命名消除属性名遮蔽问题
- `MotionControlStateMachine` 补全 `Initializing` 状态，与当时的架构设计一致（该状态机已于 2026-08-28 随 `DeviceStateMachine/` 目录删除）
- `DeviceStatusModels` 状态字符串统一使用 `DeviceState` 合法值

### 负面
- 单文件包含多个工作流的状态定义，可能随项目增长变大
- 需要确保 `region` 分区清晰，避免混淆

## 相关页面

- [[modules/DeviceControl]] — 设备控制模块（状态契约已内联各工作流文件，本 ADR 的集中文件方案已废止）
- [[modules/MotionControl]] — 运动控制模块
- [[decisions/ADR-026-EnumDeduplication]] — 枚举去重策略
- [[decisions/ADR-042-WorkflowStateBaseGeneric]] — 通用流程态机制下沉泛型基类（本 ADR 的现行替代）