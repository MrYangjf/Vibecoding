---
title: ADR-103 缺值保持与自适应按距离分段
date: 2026-11-17
updated: 2026-11-17
tags: [决策, 焊缝跟踪, 缺值, 报警, 自适应, 分段]
status: accepted
---

# ADR-103 缺值保持与自适应按距离分段

> **决策一句话**：缺值未达阈值时 CSP 保持上次有效目标（不回落标定位）并暂停入图；达阈值唯一一次报警停焊；自适应分段统一为「每段距离 mm」。

## 背景

N09 要求「缺值期间禁止回落标定位、禁止续焊，Y 取最后有效目标并继续按拍下发」；原 `RunCspTick` 用 `ready ? targetY : config.TeachLockYMm`，缺值即回标定位，且地图仍按错误键入点。N10 要求缺值达阈值报警停焊（含 `TX_NG`）、流程 `ErrorAborted(NoValueAlarm)`、不复用 `DoStopMachine`、不自动清累计器。N15 要求自适应分段从「按点数」改为「按距离」，原 `EnsureSupportedSegmentation()` 把按距离静默降级，`WeldParamAdjustmentAlgorithm` 对应分支为空实现。

## 决策

1. `RunCspTick` 新增 `_cspHasHeldTarget` / `_cspHeldTargetY`：有效目标即刷新 held；缺值取 held 继续下发；仅首个有效目标前允许以 `TeachLockYMm` 起步。
2. 缺值累计达 `NoValueToleranceMm` 时 `RaiseNoValueAlarm`：一条 Error → `ReportAlarm`（内含 `TX_NG`）→ `StopCspOutput` → `Fail("NoValueAlarm ...")`；`_noValueAlarmRaised` 保证一次焊段只报一次，断设备与模组线程保持不动。
3. `SeamMapTrackingAlgorithm` 新增 `PauseIngest`；`WeldParamManager.OnSeamLaserResult` 按「缺值累计 > 0 或位姿 `PoseAgeMs > 2×RSI 周期`」置位，恢复后自动解除。
4. 自适应配置删除 `IsCountType`/`CountNum`/`EnsureSupportedSegmentation`/`DistanceSegmentationUnsupportedReason`，新增 `SEGMENT_DISTANCE_MM`（1~50，默认 5，越界钳位并 Warning）；旧键 `IS_COUNT_TYPE`/`COUNT_NUM` 迁移期保留读取、忽略并记一条 Info，不再写出。
5. `WeldParamAdjustmentAlgorithm` 按距离分段：累计 `|ΔrobotX|` 达段距取段内有效宽度均值查表；段内无有效点不查表，交 N10 统一报警；`AccumulateSeamWidth` 同时喂滑动窗与段累计。
6. UI 删除「分段方式」下拉，`txtFlowCountNum` 文案改「每段距离(mm)」，新增红色提示条说明「缺值报警停焊、清警后回起始位从头重焊」；不新增续焊入口。
7. 心跳 `EvaluateHeartbeatLevel` 接入 H2（缺值超阈值），只做分级与 Debug 边沿日志；唯一 Error 仍由缺值报警发出，避免同一事实两处记录。

## 备选方案

- 缺值期继续用标定位 → 违反 N09，且会在焊缝上产生横向阶跃，弃。
- 缺值报警复用 `DoStopMachine` → 会断设备、关模组线程，解除后无法读状态，弃。
- 缺值报警另起独立线程/定时器 → 新增并行机制，弃。
- 保留「按点数」作为可选分段 → 与 N15 唯一分段口径冲突，旧键仅供回退一版，弃。

## 后果

### 正面
- 缺值期 Y 轴不再横向跳回标定位，焊缝连续性可控。
- 报警后设备与通讯保持可读，现场可清警后回起始位重焊。
- 自适应查表口径与现场「每段距离」一致，配置与 UI 同键同义。

### 负面
- 缺值期保持目标依赖 held 值，若首个有效目标前即超阈值，仍以标定位起步并报警，需现场确认起步姿态。
- 段内无有效点时不查表，输出保持旧值，需依赖缺值报警兜底。

## 落地

- `MotionControlWorkflow.RunCspTick` / `IsNoValueThresholdReached` / `RaiseNoValueAlarm` / `StartCspOutput`
- `SeamMapTrackingAlgorithm.PauseIngest` / `OnLaserResult`
- `WeldParamManager.PoseAgeMs` / `OnSeamLaserResult` / `IsIngestPaused` / `FeedLatestSeamWidth`
- `WeldAlgorithmsConfig.SegmentDistanceMm` / `LoadZoneIniAdapt` / `SaveZoneIniAdapt`
- `WeldParamAdjustmentAlgorithm.AccumulateSeamWidth` / 按距离分段分支
- `ProcessControlPage` / `ProcessControlPage.Designer`
- `DeviceControlWork.EvaluateHeartbeatLevel` / `IsNoValueOverLimit` / `LogHeartbeatEdge`

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-104-rsi-channel-payload-freeze-alarm-stop]]
- [[decisions/ADR-102-heartbeat-levels-and-comm-reconnect]]
- [[api/MotionControlWorkflow]]
- [[api/WeldParamManager]]
- [[api/WeldParamAdjustmentAlgorithm]]
- [[api/SeamMapTrackingAlgorithm]]
- [[api/ProcessControlPage]]
