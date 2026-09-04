---
title: ADR-011 工作流作为焊接调整主驱动
date: 2026-07-15
tags: [决策, 工作流, 焊接, 驱动]
status: accepted
---

# ADR-011 LineLaserWorkflow 作为焊接调整（WeldProcess）的主驱动

## 状态
已采纳（2026-07-15）｜**结论有效，目录已迁移（2026-09-01 治理标注）**

> **ℹ️ 路径过期（结论不变）**：本 ADR 中的 `Workflow/` 目录已解散，工作流实现类现位于 `MainDeviceControl/DeviceWorkflow/`。
> **核心结论仍然有效且仍是硬约束**：`LineLaserWorkflow` 是 `WeldProcess` 调整的**唯一驱动源**，`TriggerAdjustment()` 无参、由流程在 Adjust 步骤调用，手动模式直接跳 Complete 从而天然跳过调整。
> **当前真相源**：[[modules/DeviceControl]]、[[api/LineLaserWorkflow]]、[[api/WeldParamControlWorkflow]]。

## 背景
上一轮审查发现 [[api/LineLaserWorkflow]] 存在两路并存且脱节的链路：
1. `WeldProcess.OnAlgorithmCompleted` 订阅 `PipelineManager.AlgorithmCompleted`，**每帧自调** `AutoAction`（落盘 WeldActionRecord、做调整）。
2. `LineLaserWorkflow.RunAutoAdjust()` 是**空桩**（直接置 `_lastAdjustSuccess = true`），未调用 WeldProcess 真实调整逻辑。

后果：调整/记录逻辑与 Workflow 的 Step 编排完全脱节，Workflow 无法控制「何时调整」「手动模式跳过调整」「失败计数重置时机」，且 `GetCurrentRobotX()` 恒返回 0 导致失败距离保护形同虚设。

## 决策
确立 **LineLaserWorkflow 为 WeldProcess 调整的唯一主驱动**：
1. **WeldProcess 退为数据暂存者**：`OnAlgorithmCompleted` 不再每帧调用 `AutoAction`，仅暂存 `_lastSeamFeature`、`_lastRobotX`。
2. **新增统一入口** `WeldProcess.TriggerAdjustment()`：由 Workflow 在 Adjust 步骤调用，内部以暂存的 `_lastSeamFeature`/`_lastRobotX` 驱动 `AutoAction`（单一调用点）。
3. **Workflow 驱动调整时机**：`ExecuteStep_Adjust` → `RunAutoAdjust()` → `WeldProcess.TriggerAdjustment()`；手动模式在 `ExecuteStep_Display` 直接跳到 `Complete`，**不再进入 Adjust**，因此天然跳过调整（仅分析+显示）。

同步修复的其他问题（同轮，见 [[api/LineLaserWorkflow]] 已修复项）：
- **持续运行**：`WorkflowLoopWorker` 主循环退出条件仅 `ErrorAborted || ManualStopped`；`ExecuteStep_Complete` 进入 `Completed` 状态后 `Completed → Acquiring` 立即开启下一轮，直至手动停止/信号停止/异常终止。
- **Completed 状态可达 + WorkflowCompleted 事件触发**：`ExecuteStep_Complete` 调用 `FireWorkflowCompletedEvent()`。
- **失败计数清零**：`ExecuteStep_AnalyzeImage` 识别成功后 `_consecutiveFailureCount = 0`（识别 ok 退出失败计数）。
- **异常终止双条件**：`CheckFailureThresholds` 中 `连续失败次数 ≥ 上限` **或** `Math.Abs(GetCurrentRobotX() - _startRobotX) >= _maxWeldLength`（行程长度超限，默认 1000mm）。
- **GetCurrentRobotX 真实化**：改为从 `WeldProcess.Instance.RobotWeldData.PosX` 读取（通信层对接前占位；TODO：对接 KUKA RSI/EKI 读取真实机器人 X）。

## 后果
- 正面：调整/记录驱动源收敛为单一链路，Workflow 完全掌控「何时调整、何时跳过、何时终止」；失败距离保护与连续失败保护同时生效；手动模式语义明确（仅分析+显示）。
- 负面 / 待决：机器人 X 真实读取仍依赖通信层对接（当前为 WeldProcess.RobotWeldData.PosX 占位）；合并 [[decisions/ADR-010-WeldActionRecord]] 中「WeldProcess 独立驱动」的旧描述已在本 ADR 纠正。

## 相关
- [[modules/DeviceControl]]（LineLaserWorkflow 状态机/Step）
- [[modules/WeldParamControl]]（WeldProcess.TriggerAdjustment）
- [[api/LineLaserWorkflow]]（状态转换 + 已修复问题清单）
- [[decisions/ADR-010-WeldActionRecord]]（双记录数据模型）
