---
title: ADR-103 缺值保持与自适应按距离分段
date: 2026-11-17
updated: 2026-11-18
tags: [决策, 焊缝跟踪, 缺值, 报警, 自适应, 分段, 输出触发, 段落长度]
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

### 2026-11-18 · 落地演进 · 工艺参数输出触发由「时间周期」改为「段落长度」

> 业主 2026-11-18 裁定：自适应输出不再按时间周期节流，**改用段落长度**（替代周期功能）。

- **删除** `WeldAlgorithmsConfig.ParamOutputHz`（③Adapt 区，INI `PARAM_OUTPUT_HZ`）与其 UI 落点 `selParamOutputHz`（见 [[decisions/ADR-076-SettingsZoneSaveWiring]] 决策 D5）。
- `WeldParamControlWorkflow.TickXlOutput` 的时间维节流（`Environment.TickCount` + `intervalMs`）⇒ **距离维节流**：机器人 X 位移达 `SegmentDistanceMm` 才输出一次（首拍立即输出）。
- 节流阈值**复用** `SegmentDistanceMm`（同一把距离尺：分段算宽 + 按段输出）⇒ ⛔ 不另设「输出间隔距离」配置项、⛔ 不新增变量（`_lastXlOutputTick` 被 `_lastXlOutputRobotX` **替换**而非叠加）。
- **依据**：自动模式下机器人 RSI 的输出频率固定，节拍不由上位机定时器决定；模拟测试的线激光频率属 `VirtualCam.FrameRateHz`（系统设置页「线激光数据频率」，独立位置，不动）。
- **Manual 分支同口径**：Manual 源（振镜未启用）走的也是按段触发（宽度恒定但仍按段落长度推进），不再是「恒定周期重发」。
- 本演进把「按距离分段」从**计算分段**扩展到**输出触发** —— 同一把尺子贯穿两段。

### 2026-11-23 演进 · 自适应复位后首帧播种（不算突变）
- **决策**：`WeldParamAdjustmentAlgorithm` 新增 `_seamWidthSeeded`；复位后首个**有效宽度（>0）**直接作为会话初始值播种 `CurrentSeamWidth` 并同步 `_lastLoggedSeamWidth`，不计入变化次数、不打「宽度变化」日志；后续变化才按原判据留痕。Laser 源首拍未成段（宽度 0）不播种，等首个段均值产生再播种。
- **理由**：现场日志证实复位后首帧 0→1.0 被记成「第 1 次变化」，业主裁定「重载完成就要有初始数据，不能一出来做第一次突变判断」。
- **边界**：只改变化留痕的基准播种，查表 / 分段 / 缺值报警口径不变。见 [[lessons/SimulationAutoBranching]] 陷阱廿三。

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-104-rsi-channel-payload-freeze-alarm-stop]]
- [[decisions/ADR-102-heartbeat-levels-and-comm-reconnect]]
- [[api/MotionControlWorkflow]]
- [[api/WeldParamManager]]
- [[api/WeldParamAdjustmentAlgorithm]]
- [[api/SeamMapTrackingAlgorithm]]
- [[api/ProcessControlPage]]
