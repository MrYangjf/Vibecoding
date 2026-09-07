---
title: ADR-010 WeldActionRecord 归属与双记录设计
date: 2026-07-15
tags: [决策, 工作流, 记录, 数据模型]
status: accepted
---

# ADR-010 WeldActionRecord 数据模型归属与双记录设计

## 状态
已采纳（2026-07-15）｜**部分已被取代（2026-09-01 治理标注）**

> **⚠️ 已被取代 —— 仅「归属目录 / 命名空间」一条失效**
> - ❌ **失效**：决策 1「迁移至 `Workflow/WeldActionRecord.cs`，命名空间 `AdaWeldSystem.Workflow`」已被 [[decisions/ADR-030-ProductLifecycleRecordModule]] 推翻——`Workflow/` 目录已解散，记录类现位于 `ProductFileManager/`，命名空间 `AdaWeldSystem.ProductFileManager`。
> - ✅ **仍然有效**：决策 2「11 字段」与决策 3「双记录入口 `RecordProcessFrame` / `RecordAdjustment`」——ADR-027 明确维持该核心设计。
> - **当前真相源**：[[modules/ProductFileManager]]、[[decisions/ADR-030-ProductLifecycleRecordModule]]。编码前以真相源为准。

## 背景
`WeldActionRecord` 最初位于 `PointCloudData/RunFileRecord/`，但其语义是「焊接流程生成数据」，且需要与图像算法（EmguALG）、智能焊接调整（InteliWeld.WeldProcess）联动。原单记录入口无法区分「每帧过程数据」与「调整动作数据」，且 `DataReview` 需在一张折线图上同时展示过程曲线与红色调整点。

## 决策
1. **归属迁移**：`WeldActionRecord` 迁移至 `Workflow/WeldActionRecord.cs`，命名空间 `AdaWeldSystem.Workflow`（与线激光工作流、WeldActionRecord 概念同域）。
2. **字段扩充为 11 字段**：`FrameIndex` / `Timestamp` / `ActionType` / `RobotX,Y,Z` / `RobotSpeed` / `FeedSpeed` / `LaserPower` / `WeldWidth` / `AdjustExecuted` / `AdjustData`。
3. **双记录入口**：`RunRecordManager` 提供
   - `RecordProcessFrame(...)` —— 每帧过程快照（`ActionType=ProcessFrame`，`AdjustExecuted=false`）
   - `RecordAdjustment(...)` —— 仅调整时记录（`ActionType=WeldParamAdjust`，`AdjustExecuted=true`）
   二者都落盘到同一 `.pDat` 文件（v2 序列化），`DataReview` 回溯时用红色点标记调整记录。
4. **记录驱动源**：由 `InteliWeld.WeldProcess`（订阅 `PipelineManager.Instance.AlgorithmCompleted`）每帧调用，与 `LineLaserWorkflow.RunAutoAdjust()` 桩函数**解耦**。

## 后果
- 正面：WeldActionRecord 概念归属清晰，记录维度完整，DataReview 可同时展示过程曲线 + 调整红点。
- 负面 / 待决（已解决）：`LineLaserWorkflow.RunAutoAdjust()` 原为空桩，未接入 WeldProcess；该问题已于 **2026-07-15** 通过 [[decisions/ADR-011-WorkflowAsAdjustmentDriver]] 解决——`RunAutoAdjust()` → `WeldProcess.TriggerAdjustment()`，WeldProcess 仅暂存帧特征，由 Workflow 统一驱动调整。
- 序列化：`.pDat` 采用 version=2（二进制 + 文本回退），`.tmp` 用于崩溃恢复。

## 相关
- [[modules/DeviceControl]]（WeldActionRecord 归属）
- [[modules/WeldParamControl]]（WeldProcess 调用入口）
- [[modules/PointCloudData]]（RunRecordManager 落盘）
- [[modules/UIDesign]]（DataReview 回溯）
- [[api/LineLaserWorkflow]]（RunAutoAdjust 桩 + 已知问题）
