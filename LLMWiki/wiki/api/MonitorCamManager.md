---
title: MonitorCamManager — 监控相机业务中枢（原 MonitorCamManager，ADR-041 三层重构后改名承接）
date: 2026-09-08
tags: [API, 相机, 监控, 管理器, 健康巡检, MecaVision]
source: AdaWeldSystem/MonitorCam/MonitorCamManager.cs
---

# MonitorCamManager — 监控相机业务中枢

> `AdaWeldSystem.MonitorCam.MonitorCamManager`（`MonitorCam/MonitorCamManager.cs`）。
> **2026-09-08 ADR-041**：原 `MonitorCamManager`（`MonitorCam/MonitorCamManager.cs`，已删除）改名承接，构造切至 `MecaVisionCam` 实现；对外唯一入口，Lazy 单例。参照线激光 ADR-039 分工：实现层只做回调触发，本类是业务中枢。

## 对外入口（单例）

| 成员 | 说明 |
|---|---|
| `static MonitorCamManager Instance` | Lazy 单例 |
| `Mat CurrentMat` | 最近一帧（业务层读取） |
| `bool IsRun` | 采集中标志 |
| `MonitorCameraConnectionState ConnectionState` | 连接态 |
| `MonitorCamConfig Config` | 配置（持久化走 XML） |
| `bool LastAcquisitionSuccess` | 最近一次采集成功与否 |

## 模式与生命周期

| 成员 | 说明 |
|---|---|
| `void OpenSensor(string ip, string port)` | 连接相机（委托实现层 `Connect`） |
| `void SetPhase(MonitorCameraPhase phase)` | 设置当前阶段（焊前对中/焊中质检），驱动算法选择 |
| `void ChangeMode(bool enableLive)` | Live/PIL 模式切换（`IsLiveMode`） |
| `void SensorRunContinue()` / `void SensorStop()` | 连续采集启停 |
| `void Dispose()` | 释放（含实现层） |

## 健康巡检（ADR-027 R1 自工作流下沉，保留不变）

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
| `static event MonitorCameraFrameCompletedHandler FrameCompletedEvent` | 帧采集完成（`AutoResetEvent AcquisitionCompletedSignal` 配合同步等待） |

## 关联

- 实现层：[[api/MecaVisionMVSDK-Native]]（`MonitorCam/MecaVisionCam/`，实现 `IMonitorCamApi`）
- 抽象层：`MonitorCam/IMonitorCam/`（接口 + 3 枚举 + 2 事件参数）
- 模块页：[[modules/MonitorCam]]；决策：[[decisions/ADR-041-MecaVisionMonitorCamera]]
- 算法侧：[[api/AlgorithmManager]]（EmguALG.Manager，承接原 AlgorithmManager 职责）

> 历史沿革：健康巡检原属 `MonitorSupervisionWorkflow`，2026-08-31 经 ADR-027 下沉至本类前身 `MonitorCamManager`（ADR-013 ②）。
