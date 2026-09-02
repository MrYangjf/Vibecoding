---
title: VirtualCameraRun API 参考
date: 2026-07-16
tags: [API, 相机, 虚拟, 模拟]
source: AdaWeldSystem/LineLaserCam/VirtualCam/VirtualCameraRun.cs
---

# VirtualCameraRun API 参考

> 虚拟调试相机，位于 `LineLaserCam/VirtualCam/VirtualCameraRun.cs`，命名空间 `AdaWeldSystem.VirtualCam`，`class VirtualCameraRun : ICameraRun`。
> 不依赖 SmartRay SDK，自生成轮廓点云经 `ImageAlgorithm.ConvertContourToMat` 出 Mat，完全复用真实相机「取帧 → 算法分析」链路。

## 枚举

```csharp
public enum SimSeamProfile { VGroove=0, UGroove=1, Flat=2, Random=3 }
```

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `SeamProfile` | `SimSeamProfile` | 模拟焊缝轮廓类型 |
| `RandomMode` | `bool` | 每帧随机演化宽度/中心偏移 |
| `TargetDistance` | `double` | 模拟目标距离（工作流循环至机器人X达此值即停，mm） |
| `BaseSeamWidth` | `double` | 焊缝基准宽度（mm） |
| `BaseSeamDepth` | `double` | 焊缝基准深度（mm） |

> 所有属性于构造函数显式初始化（遵循 ADR-002，不使用 auto-property initializer）。

## 接口实现

| 成员 | 说明 |
|------|------|
| `AcquisitionCompletedSignal` | AutoResetEvent |
| `IsRunning` / `LastAcquisitionSuccess` / `CurrentMat` | 取自后备字段 |
| `SensorRunContinue()` | 生成一帧 `PointCloudData`（`GenerateSeamContour()`）→ `ImageAlgorithm.ConvertContourToMat` → `CurrentMat` → 置 `AcquisitionCompletedSignal` |
| `SensorStop()` | 停运行标志 |
| `Dispose()` | 释放 `_currentMat`（未重写 `Dispose(bool)`，遵循 ADR-001） |

## GenerateSeamContour

121 采样点，X=0（单帧线激光），Y=横向、Z=深度按 `SimSeamProfile`；逐帧引入 `centerOffset`（V/U/Flat 用正弦、Random 用随机），使焊缝中心偏离标定中心，产生非零水平移动需求。

## 协作

- 由 [[api/CameraSelector]] 激活；被 `LineLaserWorkflow`（[[modules/DeviceControl]]）在模拟模式下取图、被 [[modules/UIDesign]] 的 `MotionControlPage` 设定 `SeamProfile`/`RandomMode`。
- 接口契约见 [[api/ICameraRun]]。

---

*来源：AdaWeldSystem/LineLaserCam/VirtualCam/VirtualCameraRun.cs*
