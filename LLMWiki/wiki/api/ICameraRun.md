---
title: ICameraRun API 参考
date: 2026-07-16
tags: [API, 相机, 接口]
source: AdaWeldSystem/LineLaserCam/Api/ICameraRun.cs
---

# ICameraRun API 参考

> 相机运行抽象接口（LineLaserCam 线激光相机族的**统一对外接口**），位于 `LineLaserCam/Api/ICameraRun.cs`，命名空间 `AdaWeldSystem.LineLaserCamApi`。
> 使真实相机 `SmartRayCam.CameraRun` 与虚拟相机 `VirtualCam.VirtualCameraRun` 可互换；工作流（`LineLaserWorkflow` / `MotionControlWorkflow` 取图）与界面（`LLCamWorkJob` / `MotionControlPage`）仅依赖此接口。
> **[2026-07-21]** 同一文件还定义了线激光相机连接态相关枚举 `LineLaserCameraConnectionState`（连接/断开/工作中）与 `CameraKind`（None/SmartRay/Hik/Virtual/IntelligentLaser），由 [[api/CameraSelector]] 聚合派生相机连接态（详见 [[decisions/ADR-018-CameraConnectionStateDecoupled]]）。

## 接口定义

```csharp
public interface ICameraRun : IDisposable
{
    AutoResetEvent AcquisitionCompletedSignal { get; }
    bool IsRunning { get; }
    bool LastAcquisitionSuccess { get; }
    Mat CurrentMat { get; }
    void SensorRunContinue();
    void SensorStop();
    double ScanRateHz { get; }
}
```

## 成员说明

| 成员 | 说明 |
|------|------|
| `AcquisitionCompletedSignal` | AutoResetEvent，采集完成信号（Workflow 等待此信号后读取 CurrentMat） |
| `IsRunning` | 相机是否正在运行 |
| `LastAcquisitionSuccess` | 最近一次采集是否成功 |
| `CurrentMat` | 最近一次采集到的图像（Mat） |
| `SensorRunContinue()` | 触发连续/单帧采集 |
| `SensorStop()` | 停止采集 |
| `ScanRateHz` | 当前采集扫描率（Hz）；工作流据此按帧周期缩放 WaitOne 超时（120Hz→紧超时；虚拟相机=120，SmartRay 缓存内部触发频率/最大扫描率） |

## 实现者

- `SmartRayCam.CameraRun`（真实 SmartRay 3D 相机，SDK 回调驱动）
- `VirtualCam.VirtualCameraRun`（虚拟调试相机，自生成轮廓点云）
- `IntelligentLaserCam.IntelligentLaserCameraRun`（英莱 IntelligentLaser 3D 线激光，MillionOutlineInspect 回调驱动，无缝接入取图链，详见 [[api/IntelligentLaserCameraRun]]）

> 回调等待取图模式见 [[decisions/ADR-005-CallbackAcquisition]]；Live 模式不触发信号见 [[guides/Project-Tools]]。

---

*来源：AdaWeldSystem/LineLaserCam/Api/ICameraRun.cs*
