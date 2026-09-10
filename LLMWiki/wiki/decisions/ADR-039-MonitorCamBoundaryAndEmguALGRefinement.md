---
title: ADR-039 监控相机业务边界澄清与 EmguALG 五层细化
date: 2026-09-09
tags: [决策, MonitorCam, EmguALG, 2D相机, 算法架构, ADR-039]
status: accepted
---

# ADR-039：监控相机业务边界澄清与 EmguALG 五层细化

## 背景

监控相机模块在前期实现中引入了 **Live/PIL 双模式** 语义（`IsLiveMode`、`ChangeMode`、`StartAcquisition`/`StopAcquisition`、`FrameReceived` 连续回调），并存在以下事实错位：

1. 监控相机为 **2D 面阵相机**，无 Live/PIL 业务模式；该模式切换属于已废弃的 SmartRay 线激光旧实现，当前线激光使用英莱相机，完全不需要此切换。
2. 监控相机的算法需求被过度放大：实际只需要基于 EMGU 的 **焊丝距离检测** 与 **焊接质量检测** 两种 2D 分析，不需要复用为线激光设计的基础视觉链路。
3. EmguALG 目录结构不满足用户要求的五层划分：需要明确区分「算法抽象 / EMGU 算子封装 / 在线检测算法实现 / 线激光轮廓 Mat 生成 / 外部统一入口」。

## 决策

1. **监控相机业务边界修正**：
   - 监控相机为 2D 面阵相机，**不存在 Live/PIL 业务语义**；所有画面显示均采用「触发采集后刷新 Mat」的方式（与线激光手动调试页同构，频率可控）。
   - `IMonitorCamApi` 只保留：连接、断开、单次触发取帧 `CaptureSingleFrame()`、释放。
   - 删除 `FrameReceived` 事件、`StartAcquisition()` / `StopAcquisition()`、`IsLiveMode`、`ChangeMode`、`MonitorFrameEventArgs`、`FrameCompletedEventArgs.IsLive`。
   - `MonitorCamPage` 删除 `chkLive` 实时预览复选框；画面由单次/连续检测触发后通过 `FrameCompletedEvent` 刷新。

2. **EmguALG 五层结构**：
   ```
   EmguALG/
   ├── Abstractions/          # IAlgorithm / IConfigurableAlgorithm / IResultStore
   ├── Core/                  # AlgorithmBase / AlgorithmResult / 算子枚举 / 预处理配置
   ├── RealtimeMonitor/       # 在线检测算法实现
   │   ├── WireFeedDistance/  # 焊丝距离检测
   │   └── WeldQuality/       # 焊接质量检测
   ├── LineLaserContour/      # 线激光轮廓 Mat 渲染
   │   ├── ILineLaserContourAlgorithm.cs
   │   └── LineLaserContourAlgorithm.cs
   └── Manager/               # AlgorithmManager 统一调度入口
   ```

3. **算法职责边界**：
   - 监控相机只消费 `DetectWireFeed` / `DetectWeldQuality`，不消费线激光轮廓/点云算法。
   - 线激光轮廓渲染从 `LineLaserManager.ProfileMatRenderer` 上提为 `EmguALG.LineLaserContour.LineLaserContourAlgorithm`，`LineLaserManager` 通过 `ILineLaserContourAlgorithm` 接口调用。

## 后果

### 正面
- 监控相机业务语义与 2D 面阵相机硬件一致，消除 SmartRay 遗留模式污染。
- EmguALG 五层结构与用户指定方案对齐，外部调用入口唯一（`AlgorithmManager`）。
- 线激光显示渲染与线激光采集/识别职责解耦，符合 ADR-038 算子库统一与职责下沉原则。

### 负面 / 遗留
- `MonitorCamManager.SensorStop()` 变为空实现（单次触发任务由 Task 自行结束），保留方法仅兼容既有调用方。
- 真编译待 Visual Studio；Python 静态校验已完成（命名空间一致、csproj 注册一致、无残留 Live/PIL 业务符号）。

## 相关页面

- [[modules/MonitorCam]]
- [[modules/EmguALG]]
- [[api/MonitorCamManager]]
- [[api/MonitorCameraWorkflow]]
- [[api/AlgorithmManager]]
- [[decisions/ADR-038-EmguALGThreeLayer]]
- [[decisions/ADR-037-MecaVisionMonitorCamera]]
- [[decisions/ADR-007-MonitorCameraModule]]
