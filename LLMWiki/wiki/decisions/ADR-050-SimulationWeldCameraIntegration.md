---
title: ADR-050 模拟测试接入焊接相机（自动运行模式：Ready 在线检查 → Start 采集+录像 → 结束收口）
date: 2026-09-29
updated: 2026-10-08
tags: [决策, 模拟, 监控相机, 焊接相机, 录像, ADR-050]
status: accepted
---

# ADR-050 — 模拟测试接入焊接相机（自动运行模式：Ready 在线检查 → Start 采集+录像 → 结束收口）

- 状态：✅ accepted
- 日期：2026-09-29
- 关联：[[decisions/ADR-046-MonitorCamIpScanAndStrictMatch]]、[[decisions/ADR-047-MonitorCamSwitchToHikMvs]]、[[decisions/ADR-048-MonitorCamTabsRecordPlayback]]、[[decisions/ADR-049-MainPageDualChartAndCamPreview]]、[[api/MonitorCamManager]]、[[decisions/ADR-039-SimulationTestAutoTerminationAndRecordCacheRelease]]（模拟自动终止契约）

## 背景

模拟测试主链（`DeviceControlWork.SimScheduleTick`，步号 10/20/21/22/30）此前不含焊接（监控）相机动作；业主裁定在模拟测试中增加焊接相机功能，随焊接生命周期自动启停（自动运行模式，预览走主页 30Hz 管线），与调试页手动模式（ADR-048）并行构成双消费场景（每订阅方独立副本，ADR-048 三次补充）。

## 决策

1. **Ready = 在线检查 + 打开设备**（`PrepareSimulationMonitorCam`，挂 `StartSimulation()` 启动序列 `PrepareSimulationCamera()` 之后）：
 - `ScanDevices()` 枚举比对配置 IP（忽略大小写）确认**在线**；不在线或 `OpenSensor` 失败**只告警不阻断模拟**（模拟异常守卫本就不判监控相机，2026-09-20「开启即结束」教训同源）；
 - 打开即连接语义（ADR-050 时点：连接不开取流，对齐 demo——ADR-048 二次勘误）。
2. **PreWork 跳过**：光丝对中未做，PreWork 阶段相机无动作（业主裁定）。
3. **Start = 连续采集 + 打开录像**（`SimMonitorCamStartWeld`，挂 `case 22` 下发焊接启动 `DoSubWork()` 之后）：
 - `StartCapture()`（连续模式，帧经 `PreviewFrameEvent` 逐帧分发独立副本 → 主页 30Hz 自动出图，2026-11-11 起经 `MonitorCameraWorkflow.StartWeldPreview`）；
 - 成功后 `StartRecord("焊接相机_yyyyMMdd_HHmmss.avi")`（落配置录像目录，默认 BaseDir\焊接）；
 - 采集或录像失败只告警不阻断焊接。
4. **焊接结束 = 关录像 + 停采集**（`SimMonitorCamStopWeld`，按 `IsRecording`/`IsCapturing` 实际状态动作，重复调用零害）：
 - 三停止命令链统一收口：`DoSubStop`（正常到程）/ `DoSubManualStop` / `DoSubAlarmStop`（`EndWeldMonitor()` 之后各一行）；
 - `DisableSimulation()` 兜底一行（异常自动终止路径不经三停止命令）。
 - **2026-11-11 追加**：`SimMonitorCamStopWeld` **首行**（早退之前）调 `MonitorCameraWorkflow.StopWeldPreview()`，保证「采集已停」时预览订阅同样收口。

## 备选方案

| 方案 | 结论 |
|---|---|
| 相机不在线即终止模拟 | 放弃：模拟价值在线激光+运控链路，相机缺失不应阻断（与异常守卫口径一致） |
| 结束收口只挂 `DisableSimulation` 单点 | 放弃：手动/报警停止后模拟可能继续，录像应随焊接结束即停；多点收口靠幂等守卫保证零害 |
| 经 `MonitorCameraWorkflow.Start` 走检测流程 | 放弃：那是「采集→分析」单轮/连续检测语义，与本需求「持续预览+录像」不同；模拟直接用 Manager 层 API |

## 后果

- 正面：模拟全程具备焊接相机预览（主页）与录像留档，生命周期与焊接启停严格同步；不在线降级不伤模拟主链。
- 负面：模拟期间相机持续取流（全帧率建 Mat 分发），CPU 占用上升；收口依赖 Manager/HikCam 幂等守卫，新增停止路径须记得带 `SimMonitorCamStopWeld`。
- 遗留：真实链路（非模拟）的自动模式相机启停编排待机器人命令驱动细化后另行裁定。

## 相关页面

- [[api/MonitorCamManager]] —— StartCapture/StartRecord/StopRecord/StopCapture/ScanDevices/OpenSensor 语义
- [[decisions/ADR-048-MonitorCamTabsRecordPlayback]] —— 录像 API 与双订阅方独立副本契约
- [[decisions/ADR-049-MainPageDualChartAndCamPreview]] —— 主页预览管线沿革（2026-10-22 移除页内 30Hz 表；2026-11-11 改为 `MonitorCameraWorkflow` 节流后交付，见 [[decisions/ADR-016-WorkflowResponsibilityBoundary]] 演进记录）
- [[decisions/ADR-039-SimulationTestAutoTerminationAndRecordCacheRelease]] —— 模拟测试自动终止契约（DisableSimulation 统一出口）
