---
title: VirtualCam API 参考（虚拟调试相机）
date: 2026-09-08
tags: [API, 相机, 虚拟, 模拟, ADR-038, ADR-039]
source: AdaWeldSystem/LineLaserCam/VirtualCam/VirtualCam.cs
---

# VirtualCam API 参考（虚拟调试相机）

> **位置**：`LineLaserCam/VirtualCam/VirtualCam.cs`（命名空间 `AdaWeldSystem.LineLaserCam.VirtualCam`）
> **类名 `VirtualCam : LineLaserCameraBase`**（2026-09-08 ADR-038 改名并同步文件名，与目录/命名空间对齐；⛔ 旧类名 `VirtualCameraRun` 已废，代码与 wiki 一律用 `VirtualCam`）。
> 不依赖任何相机 SDK，自生成轮廓点云，完全复用真实相机「取帧 → 算法分析」链路，可与英莱相机互换。
> 相机键名「虚拟线激光」；`IsConnected` 恒为 `true`、`ScanRateHz` 恒为 120。
> **2026-09-08 二次分工（ADR-039）**：与英莱一致，**只触发回调不做业务**——`SensorRunContinue` 生成点云后调 `RaiseResultReady` + `RaiseProfileReady` 即返回；⛔ `RaiseFrameReady` / `CurrentMat` 自绘已删除，绘制与 PVT 下载由 [[api/LineLaserManager]] 承担。

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

## 抽象层实现（`LineLaserCameraBase` 覆写）

| 成员 | 说明 |
|------|------|
| `Kind` | 固定 `LineLaserKind.Virtual` |
| `IsConnected` | 恒 `true`（无硬件连接语义） |
| `IsRunning` / `LastAcquisitionSuccess` / `ScanRateHz` | 取自后备字段 / 常量 120 |
| `AcquisitionCompletedSignal` | `AutoResetEvent` |
| `SensorRunContinue()` | 生成一帧 `PointCloudData`（`GenerateSeamContour()`）→ `RaiseResultReady(BuildResult(cloud), 0)` + `RaiseProfileReady(cloud, 0)` → 置 `AcquisitionCompletedSignal` → `RaiseStateChanged()`。**不生成 Mat**（⛔ 原 `ImageAlgorithm.ConvertContourToMat` → `RaiseFrameReady` 已删） |
| `SensorStop()` | 停运行标志 + `RaiseStateChanged()` |
| `Dispose()` | `UpdateDisplayMat(null)` 交还基类（标准 `IDisposable.Dispose()`，遵循 ADR-001/ADR-023，未重写 `Dispose(bool)`） |

> 模拟参数（`SeamProfile` / `RandomMode` / `TargetDistance` / `BaseSeamWidth` / `BaseSeamDepth`）由 `LineLaserManager.ApplyConfig()` 从 `LineLaserConfig` 套用。

## GenerateSeamContour

121 采样点，X=0（单帧线激光），Y=横向、Z=深度按 `SimSeamProfile`；逐帧引入 `centerOffset`（V/U/Flat 用正弦、Random 用随机），使焊缝中心偏离标定中心，产生非零水平移动需求。

## BuildResult（ADR-039 新增）

虚拟相机不走英莱算法，用**最低点即焊缝特征点**推算一个中性 `LineLaserSeamResult`（`Valid=true`、`ParseRes=1`、`FeatureY`=最低点 Y、`FeatureZ`=最低点 Z、宽度=Y 跨度、面积=宽×深×0.5），**用于在模拟模式下打通「结果 → Y 轴 PVT」链路**——使 [[api/SeamPvtFeeder]] 在无真机时也能被验证。

## 协作

- 由 [[api/LineLaserManager]] 激活（`SelectVirtual()`）；被 `LineLaserWorkflow`（[[modules/DeviceControl]]）在模拟模式下驱动，被 [[modules/UIDesign]] 的 `MotionControlPage` 设定 `SeamProfile`/`RandomMode`。
- 与英莱相机同为 L3 实现，二者对业务层**完全同构**：业务层只认 `LineLaserCameraBase`。

## 关联

- 模块：[[modules/VirtualCam]]、[[modules/LineLaserCam]]
- 决策：[[decisions/ADR-038-LineLaserThreeLayerRefactor]]、[[decisions/ADR-039-LineLaserResponsibilitySplit]]
- 同层实现：[[api/IntelligentLaserCam]]

---

*来源：AdaWeldSystem/LineLaserCam/VirtualCam/VirtualCam.cs*
