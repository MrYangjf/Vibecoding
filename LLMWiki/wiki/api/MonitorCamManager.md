---
title: MonitorCamManager — 监控相机业务中枢（原 MonitorCamManager，ADR-034 三层重构后改名承接）
date: 2026-09-08
updated: 2026-11-09
tags: [API, 相机, 监控, 管理器, 健康巡检, MecaVision, IP扫描]
source: AdaWeldSystem/MonitorCam/MonitorCamManager.cs
---

# MonitorCamManager — 监控相机业务中枢

> `AdaWeldSystem.MonitorCam.MonitorCamManager`（`MonitorCam/MonitorCamManager.cs`）。
> **2026-09-08 ADR-034**：原 `MonitorCamManager`（`MonitorCam/MonitorCamManager.cs`，已删除）改名承接，构造切至 `MecaVisionCam` 实现；对外唯一入口，Lazy 单例。参照线激光 ADR-032 分工：实现层只做取帧，本类是业务中枢。
> **2026-09-09 ADR-028**：监控相机为 **2D 面阵相机，无 Live/PIL 模式**；删除 `IsLiveMode`、`ChangeMode`、`FrameReceived`、`StartAcquisition`/`StopAcquisition`；所有采集均为单次触发。
> **2026-09-29 ADR-046**：新增设备扫描 `ScanDevices()`（三层唯一口，实现层枚举 + `CameraGigeGetIp`）、`CloseSensor()`（真正断硬件，此前 `ConnectOff` 只改状态）、`SaveConfig()`（含连接 IP 落盘 INI）；`OpenSensor` 由 `void` 改 **`bool`**。

## 对外入口（单例）

| 成员 | 说明 |
|---|---|
| `static MonitorCamManager Instance` | Lazy 单例 |
| `Mat CurrentMat` | 最近一帧（业务层读取） |
| `bool IsRun` | 相机是否已连接 |
| `MonitorCameraConnectionState ConnectionState` | 连接态 |
| `MonitorCamConfig Config` | 配置（持久化走 XML） |
| `bool LastAcquisitionSuccess` | 最近一次采集成功与否 |
| `string DescribeLastError(MonitorCamErrorContext context)` | **2026-11-09** 失败描述成品：连接/采集语境由实现层映射厂商返回码，分析语境走本层口径；流程与 UI 只读，不自行拼 `ret=` |
| `bool TryAcquireCalibFrame(out Mat frame, out string failureMessage)` | **2026-11-09** 送丝距离测试取帧：软触发 + 判空 + 标定十字（成品帧），失败文案由本层给出 |

> 已删除：`bool IsLiveMode`（ADR-028）。

## 模式与生命周期

| 成员 | 说明 |
|---|---|
| `bool OpenSensor(string ip, string port)` | 连接相机（委托实现层 `Connect`）；**返回是否成功**（2026-09-29 ADR-046 由 void 改 bool，已连接时返回 true）。唯一调用方 `MonitorCameraWorkflow.EnsureConnected` 为语句调用，源码兼容 |
| `List<MonitorCamDeviceInfo> ScanDevices()` | **新增（ADR-046）** 扫描（枚举）可用相机，返回含 GigE IP 的设备列表；无设备/失败返回空列表（不返回 null） |
| `void CloseSensor()` | **新增（ADR-046）** 停健康巡检 + 实现层 `Disconnect()`；UI 断开入口使用（`ConnectOff()` 只切设备态、不断硬件） |
| `void SaveConfig()` | **新增（ADR-046）** 把 `Config` 落盘到 `MonitorCamConfig.DefaultConfigPath`（连接 IP 变更后调用） |
| `void SetPhase(MonitorCameraPhase phase)` | 设置当前阶段（焊前对中/焊中质检），驱动算法选择 |
| `void SensorRunContinue()` | 触发一次采集（单次触发，2D 面阵相机唯一采集方式） |
| `void SensorStop()` | 停止采集（单次触发任务由 Task 自行结束，当前为空实现，保留以兼容既有调用方） |
| `void Dispose()` | 释放（含实现层） |

> 已删除：`void ChangeMode(bool enableLive)` / `void StartAcquisition()` / `void StopAcquisition()` / `event FrameReceived`（ADR-028）。

## 健康巡检（ADR-023 R1 自工作流下沉，保留不变）

| 成员 | 说明 |
|---|---|
| `void StartSupervision()` / `void StopSupervision()` | 巡检启停 |
| `MonitorSupervisionState SupervisionState` | 巡检状态 |
| `bool IsMonitorCameraWorking` | 相机是否健康 |
| `DateTime LastHealthyTime` | 最近健康时刻 |
| `int CheckIntervalMs` / `int HealthyValidMs` | 巡检周期/健康有效期 |
| `event EventHandler<MonitorSupervisionStatusChangedEventArgs> StatusChanged` | 巡检状态变化 |

## 事件

| 成员 | 说明 |
|---|---|
| `static event MonitorCameraFrameCompletedHandler FrameCompletedEvent` | 帧采集完成（`AutoResetEvent AcquisitionCompletedSignal` 配合同步等待）；事件参数不再携带 `IsLive` 标志（ADR-028） |

## 关联

- 实现层：[[api/HikCam]]（`MonitorCam/HikCam/`，实现 `IMonitorCamApi`；2026-09-29 ADR-047 由 MecaVision 切换海康 MVS，构造函数 `new HikCam.HikCam()`）
- 取流/录像/参数透传（ADR-048）：`StartCapture`/`StopCapture`/`IsCapturing`/`StartRecord(fileName)`/`StopRecord`/`IsRecording`/`TriggerSingleShot`（采集中自动停采集）/`SetExposureTime`/`SetGain`/`GetExposureTime`/`GetGain`/`RecordDirectory`（配置 RecordDir，默认 BaseDir\焊接）；**2026-10-30 ADR-078：`StartRecord(fileName)` 内部落 `RecordDirectory\yyyyMMdd\` 日期子目录**（自动建目录，手动录像与模拟焊接自动录像同口；实现层 `IMonitorCamApi.StartRecord(filePath)` 契约不变）；`PreviewFrameEvent` 预览帧通道（**每订阅方独立副本**：`RelayPreviewFrame` 先按标定就地标注十字、再经 `GetInvocationList()` 逐订阅方 `Clone()` 分发、订阅方拥有并负责释放、分发毕释放原始帧——2026-09-29 双订阅方 AV 勘误，主页运行时自动模式 / 调试页点采集手动模式）与 `FrameCompletedEvent` 分析链路相互独立；2026-11-09 ADR-097：UI 只接收成品帧，不再自行标注或处理像素
- 抽象层：`MonitorCam/IMonitorCam/`（接口 + 3 枚举 + 2 事件参数 + `MonitorCamDeviceInfo`）
- 模块页：[[modules/MonitorCam]]；决策：ADR-019（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[decisions/ADR-019-MonitorCamBoundaryAndEmguALGRefinement]]、[[decisions/ADR-046-MonitorCamIpScanAndStrictMatch]]、[[decisions/ADR-047-MonitorCamSwitchToHikMvs]]、[[decisions/ADR-048-MonitorCamTabsRecordPlayback]]、[[decisions/ADR-078-MonitorPlaybackControlBarAndDatedRecords]]
- UI：`UIDesign/TabPage/MonitorCamPage`（顶栏连接区）+ `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm`（扫描单选回填）
- 算法侧：[[api/AlgorithmManager]]（EmguALG.Manager，承接原 AlgorithmManager 职责）

> 历史沿革：健康巡检原属 `MonitorSupervisionWorkflow`，2026-08-31 经 ADR-023 下沉至本类前身 `MonitorCamManager`（ADR-016 ②）。2026-09-09 删除 Live/PIL 模式相关业务语义。
