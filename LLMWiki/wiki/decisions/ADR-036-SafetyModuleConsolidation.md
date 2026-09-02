---
title: ADR-036 Safety 模块整合进 Workflow
date: 2026-08-21
tags: [决策, V3, 安全互锁, 故障恢复, 模块整合, Workflow]
status: accepted
---

# ADR-036：Safety 模块整合进 Workflow

## 状态
已采纳（2026-08-21）｜**已被取代（2026-09-01 治理标注）**

> **⚠️ 已被取代 —— 目标目录与文件划分均已二次变更**
> - ❌ **失效 1（目录）**：「整体移入 `Workflow/`、命名空间 `AdaWeldSystem.Workflow`」已被 [[decisions/ADR-041-MainDeviceControlArchitecture]] 推翻——现位于 `MainDeviceControl/DeviceWorkflow/`。
> - ❌ **失效 2（文件划分）**：本 ADR 划定的 `SafetyInterlock.cs`（检查器 + 结果）与 `SafetyFlow.cs`（阈值配置）**两文件均已删除**，三文件再合并为单一 `SafetyWorkflow.cs`——见 [[decisions/ADR-044-SafetyCheckConsolidation]]。
> - ✅ **仍然有效**：「安全检查与故障恢复不建独立文件夹、并入工作流层」的归属判断。
> - **当前真相源**：[[api/SafetyWorkflow]]（单文件承载 4 态枚举 + 监控循环 + 阈值配置 + 检查器）、[[modules/Safety]]。

## 背景

`AdaWeldSystem/Safety/` 原为 V3 阶段B（安全互锁）与阶段C（故障恢复）的独立模块，命名空间 `AdaWeldSystem.Safety`。其唯一外部调用方是 `Workflow/MainDeviceThread.cs`（已处于 `AdaWeldSystem.Workflow` 命名空间），通过 `using AdaWeldSystem.Safety;` 引用其中的 `FaultRecoveryManager` / `FaultRecord` / `SafetyInterlockChecker` / `SafetyInterlockResult` / `FaultCategory`。

用户要求对 safety 文件夹做整合：
1. `FaultRecord` / `SafetyInterlockResult` / `SafetyInterlockChecker` 作为功能模块**合并**为单文件；
2. `FaultRecoveryManager` 作为**管理器**保留，对外提供配置入口；
3. `SafetyThresholds` **更名为 `SafetyFlow`**；
4. 整合后**放入 `Workflow/` 下，不单独建立文件夹**。

## 决策

将 safety 能力整合进 [[modules/Workflow]]，遵循项目既有的「工作流相关文件归集到 `Workflow/`」先例（见 [[decisions/ADR-027-WorkflowStateFileConsolidation]]、[[decisions/ADR-015-WorkflowAsHub]]）：

| 原文件（`Safety/`） | 整合后（`Workflow/`） | 处理 |
|--------------------|----------------------|------|
| `FaultRecord.cs` | `Workflow/SafetyInterlock.cs` | 与 `SafetyInterlockResult` + `SafetyInterlockChecker` 合并为单文件功能模块 |
| `SafetyInterlockResult.cs` | `Workflow/SafetyInterlock.cs` | 同上 |
| `SafetyInterlockChecker.cs` | `Workflow/SafetyInterlock.cs` | 同上，内部 `SafetyThresholds` 引用改为 `SafetyFlow` |
| `SafetyThresholds.cs` | `Workflow/SafetyFlow.cs` | **类与文件更名** `SafetyThresholds` → `SafetyFlow` |
| `FaultRecoveryManager.cs` | `Workflow/FaultRecoveryManager.cs` | 原样迁移，命名空间改为 `AdaWeldSystem.Workflow`，作为对外配置管理器 |

- **命名空间统一为 `AdaWeldSystem.Workflow`**，`MainDeviceThread.cs` 移除 `using AdaWeldSystem.Safety;`（同命名空间直接可见）。
- **不新建 `Safety/` 或 `SafetyFlow/` 子文件夹**，三文件直接置于 `Workflow/`。
- `.csproj` 将 5 个 `Safety\*.cs` 条目替换为 3 个 `Workflow\*.cs` 条目。

## 备选方案

- **保留独立 `Safety/` 模块**：维持现状，仅做内部合并。放弃，因调用方已全在 Workflow 且用户明确要求整合进 Workflow。
- **按类拆成多个文件放 Workflow/**：与用户「合并为功能模块」指令不符，且违背 ADR-027 的归集倾向。

## 后果

### 正面
- 安全能力与其唯一编排方 `MainDeviceThread` 共置于 `Workflow/`，依赖关系清晰，消除跨模块 `using`。
- 互锁三要素（记录 + 结果 + 检查器）内聚为单文件功能模块，减少零散文件。
- `SafetyThresholds` → `SafetyFlow` 命名与「safety flow」语义一致。

### 负面
- `AdaWeldSystem.Safety` 命名空间不再存在，历史文档/注释中若硬编码该命名空间需同步更新（已更新 [[modules/Safety]]、[[modules/Workflow]]）。

## 相关页面

- [[modules/Safety]] — 整合后职责说明（代码已迁 Workflow）
- [[modules/Workflow]] — 整合后代码归属地（含「安全互锁与故障恢复」小节）
- [[decisions/ADR-033-V3SystemArchitecture]] — V3 架构决策（阶段B/C 落地依据）
- [[decisions/ADR-027-WorkflowStateFileConsolidation]] — 工作流文件归集先例
- [[lessons/FaultRecoveryDeviceKey]] — 故障恢复设备键名匹配陷阱
