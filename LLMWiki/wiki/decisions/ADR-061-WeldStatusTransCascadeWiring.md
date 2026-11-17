---
title: ADR-061 WeldStatusTrans 编排入口接线与恒假判据修复
date: 2026-10-10
updated: 2026-10-30
tags: [决策, DeviceControl, 工作流, 状态迁移, 停焊沿, 主控缺陷]
status: accepted
---

# ADR-061 WeldStatusTrans 编排入口接线与恒假判据修复

> 2026-10-10 上机实测轮 · 解决 2026-10-10 精简轮遗留的两项「待业主裁定」主控缺陷
> （[[lessons/CommentSimplificationBatchPitfalls]] 待裁定点 1/2），业主裁定「修两处 + 接线」。

## 背景

### 缺陷 1 — 恒假判据（行为缺陷）

两处 `WeldStatusTrans()` 内存在 `WeldStatus == X && WeldStatus != X` 形态的永假条件：

- `MotionControlWorkflow`：`WeldStatus == Stopping && WeldStatus != Stopping`（**ADR-042 要求的停焊沿收尾分支永不执行**）
- `WeldParamControlWorkflow`：`WeldStatus == ErrorAborted && WeldStatus != ErrorAborted`

**为什么这样写（历史语义）**：原判据是**双源镜像** `WeldStatus == X && _phase != X`——整机级联已把
`WeldStatus` 推到 X、子流程自建 `_phase` 尚未同步 ⇒ 同步 `_phase` 并执行该态进入动作。
**为什么变 BUG**：[[decisions/ADR-055-SubFlowStateEliminationAndParamClassRelocation]] 把 `_phase` 整个删除后，
第二子句被机械改写为 `WeldStatus != X`，与第一子句自相矛盾 ⇒ 分支整体不可达。

### 缺陷 2 — SubDeviceLog 格式串（潜伏崩溃）

`MotionControlWorkflow.SubDeviceLog` 格式串 5 个占位符 `{0}~{4}` 只有 4 个实参，**调用瞬间抛
`FormatException`**；且「相位 {2}」标签是 ADR-055 删枚举后的陈旧文案（实参实为步骤名）。

### 缺陷 3（本轮新发现）— 编排入口零调用方

双重 Grep 交叉验证（`WeldStatusTrans\s*\(` 9 处 / `SubDeviceLog\s*\(` 6 处）：
`DeviceControlWork.WeldStatusTrans()` 私有编排入口与 `SubDeviceLog()` **均无任何调用方**。
根因：旧链路 `CommCommandWork → DispatchCommand(cmd) → WeldStatusTrans()` 中的 `DispatchCommand`
在指令驱动重构（[[decisions/ADR-038-RobotCommandDrivenStepFlow]]）中消失，**委托调用随之丢失**，
[[api/DeviceControlWork]] 仍记载该旧链路（文档陈旧）。后果：

- ADR-042「停焊沿必须在 `WeldStatusTrans()` 的 Stopping 分支调 `StopSeamTrackingOutput()`」**永远不触发**
- ADR-038「LineLaser 的 Stopping 仅经 WeldStatusTrans 进入」**永远不触发**
- 5 个子流程的该契约实现整体处于死链（`Stop()`/模拟收尾路径的手工补偿正是为绕开此缺失而生）

## 决策

### 决 1 — 接线触发点 = `CascadeWeldStatus()` 末尾

`DeviceControlWork.CascadeWeldStatus(target, reason)` 是「向 5 个子设备统一下发焊接态迁移请求」的
唯一收口（5 个调用方：DoSubPrework / DoSubWork / DoSubStop / DoSubManualStop / DoSubAlarmStop）。
在 5 次 `RequestWeldStatus` 与日志之后追加 `WeldStatusTrans();`——整机写完目标态，再委托各子流程
执行该态的进入动作（与 `RequestWeldStatus`「整机统一写入口」+ `WeldStatusTrans`「委托编排入口」的契约分工一致）。

> ⛔ **不接在 `CommCommandWork`**：`DispatchCommand` 已不存在，按陈旧文档回填等于复活死链。
> ⛔ **不接在 `DisableSimulation` 的散装 `RequestWeldStatus(Standby)`**：模拟结束复位已自带逐流程补偿
> （`_motion.Stop()` + 五流程 Standby 复位），重复触发无增益且引入新时序风险。

### 决 2 — 恒假判据按 `LineLaserWorkflow` 模板对齐（ADR-055 的基准实现）

- 运控：`Stopping` ⇒ `StopSeamTrackingOutput()` + `EnterWeldStatus(Stopping, …, false)`（进 StepStopping）；
 `ManualStopped / ErrorAborted` ⇒ `StopSeamTrackingOutput()` + `EnterWeldStatus(Standby, …, false)`。
 删除恒假的 `&& WeldStatus != Stopping` / 冗余的 `&& WeldStatus != Standby`。
- 焊参：**镜像判据已无存在基础**（WeldStatus 单源、级联写入即到位），死分支整体删除，保留 `NoReset` 守卫；
 ErrorAborted 下的输出停走由 FlowProcess「`WeldStatus != Working`」消费门禁承担（它无步号入口需推进）。

### 决 3 — `SubDeviceLog` 格式串对齐 4 实参

「运控 连接态 {0} 焊接过程态 {1} 步骤 {2} 已初始化 {3}」，删陈旧「相位」标签；
`SubDeviceLog` 零调用方状态**维持不动**（原 rules/KR-011（已并入 lessons/StaticVerifier-Wiring-Integrity）：可观测性契约不因未使用而删除），
格式串按「一旦接线即正确」修复。

## 备选方案

| 方案 | 为何放弃 |
|---|---|
| 只修两处死码、不接线 | 停焊沿收尾（ADR-042）与 Stopping 入口（ADR-038）继续永不触发，缺陷 1 的修复无从验证 |
| 接在 `CommCommandWork` 指令分发后 | 按已删除的 `DispatchCommand` 回填，语义错位（指令 ≠ 状态迁移） |
| 恒假分支原地保留 + 注释 | 永假条件是阅读者最大的误导源，且掩盖停焊沿缺失 |

## 后果

### 正面
- 停焊沿收尾在级联后确定性触发：`StopSeamTrackingOutput`（幂等）→ 进入收尾步，消除「跟踪态/缓冲态残留 →
 二跑首拍写段 0x1100」的整类风险入口
- LineLaser 停止链恢复（Stopping → StepStopping → 关激光传感器 → 回待机）
- `SubDeviceLog` 潜伏 `FormatException` 消除

### 负面 / 风险
- **运行行为变化**：真实焊接停止路径此前从未走过该委托链，现恢复——**须上机验证**
 （停稳时序、`EnterWeldStatus(Standby)` 与报警态的交互、LineLaser 收尾是否重复执行）
- 级联 5 态中 PreWork/Working 两态对多数子流程为无动作（仅状态确认），符合契约

### 真机验证项
1. 真实/模拟焊接停稳后：运控进入 StepStopping 并回 Standby，跟踪态无残留（重启焊接首拍无 0x1100）
2. 手动停止、报警停止两路径下 5 子流程状态无残留（Working/Stopping 残留即为回归）

## 相关页面

- [[decisions/ADR-042-SeamTrackingConsolidated]] —— 停焊沿收尾要求（本 ADR 使其真正可达）
- [[decisions/ADR-038-RobotCommandDrivenStepFlow]] —— Stopping 仅经 WeldStatusTrans（同上）
- [[decisions/ADR-055-SubFlowStateEliminationAndParamClassRelocation]] —— 恒假判据的根因（_phase 删除）
- [[api/DeviceControlWork]] —— CascadeWeldStatus 接线点（同轮修正其陈旧 DispatchCommand 描述）
- [[api/MotionControlWorkflow]] · [[api/WeldParamControlWorkflow]] —— 修复后契约实现形状
- [[lessons/CommentSimplificationBatchPitfalls]] —— 待裁定点 1/2 的出处（本 ADR 销项）
