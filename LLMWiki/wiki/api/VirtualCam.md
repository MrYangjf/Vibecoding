---
title: VirtualCam API 参考（虚拟调试相机）
date: 2026-09-17
tags: [API, 相机, 虚拟, 模拟, ADR-003, ADR-032, ADR-033, ADR-032]
source: AdaWeldSystem/LineLaserCam/VirtualCam/VirtualCam.cs
---

# VirtualCam API 参考（虚拟调试相机）

> **位置**：`LineLaserCam/VirtualCam/VirtualCam.cs`（命名空间 `AdaWeldSystem.LineLaserCam.VirtualCam`）
> **类名 `VirtualCam : LineLaserCameraBase`**（2026-09-08 ADR-007 改名并同步文件名，与目录/命名空间对齐；⛔ 旧类名 `VirtualCameraRun` 已废，代码与 wiki 一律用 `VirtualCam`）。
> 不依赖任何相机 SDK，自生成轮廓点云，完全复用真实相机「取帧 → 算法分析」链路，可与英莱相机互换。
> 相机键名「虚拟线激光」；`IsConnected` 恒为 `true`；`ScanRateHz` = `FrameRateHz`。
> **2026-09-08 二次分工（ADR-028）**：与英莱一致，**只触发回调不做业务**——`SensorRunContinue` 生成点云后调 `RaiseResultReady` + `RaiseProfileReady` 即返回；⛔ `RaiseFrameReady` / `CurrentMat` 自绘已删除，绘制与 PVT 下载由 [[api/LineLaserManager]] 承担。
> **2026-09-17（ADR-032）统一平直搭接**：⛔ 删除 `SimSeamProfile` 枚举与 `SeamProfile` / `RandomMode` / `TargetDistance` 属性；固定生成**平直搭接**轮廓（基准 **1000 点**），中心焊缝点 = 最接近 `y=0` 的点；**不生成 MAT 给调试界面**（`Dispose()` 调 `UpdateDisplayMat(null)`）。

## 属性

| 属性 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `BaseSeamWidth` | `double` | 8.0 | 焊缝基准宽度（mm），平直搭接轮廓全跨 |
| `BaseSeamDepth` | `double` | 3.0 | 焊缝基准深度（mm），中心搭接缝槽深度 |
| `FrameRateHz` | `int` | 30 | 线激光数据频率（Hz）：30/60/80/120，决定模拟出图节拍与 `ScanRateHz` |

> 所有属性于构造函数显式初始化（遵循 ADR-001，不使用 auto-property initializer）。
> 频率由 [[api/LineLaserManager]] `ApplyConfig()` 从 `LineLaserConfig.LineLaserDataFrequencyHz` 套用。
> ⛔ 已删除：`SimSeamProfile` 枚举、`SeamProfile`、`RandomMode`、`TargetDistance`。

## 抽象层实现（`LineLaserCameraBase` 覆写）

| 成员 | 说明 |
|------|------|
| `Kind` | 固定 `LineLaserKind.Virtual` |
| `IsConnected` | 恒 `true`（无硬件连接语义） |
| `IsRunning` / `LastAcquisitionSuccess` / `ScanRateHz` | 取自后备字段 / `ScanRateHz` = `FrameRateHz` |
| `AcquisitionCompletedSignal` | `AutoResetEvent` |
| `SensorRunContinue()` | 起 `System.Threading.Timer`，间隔 = `1000 / FrameRateHz` ms（`FrameRateHz <= 0` 回退 33ms），持续产帧：生成一帧 `PointCloudData`（`GenerateSeamContour()`）→ `RaiseResultReady(BuildResult(cloud), ScanRateHz)` + `RaiseProfileReady(cloud, ScanRateHz)` → 置 `AcquisitionCompletedSignal` → `RaiseStateChanged()`。**不生成 Mat**（⛔ 原 `ImageAlgorithm.ConvertContourToMat` → `RaiseFrameReady` 已删）。`SensorStop()` / `Dispose()` 停表 |
| `SensorStop()` | 停运行标志 + 停表 + `RaiseStateChanged()` |
| `Dispose()` | `UpdateDisplayMat(null)` 交还基类（标准 `IDisposable.Dispose()`，遵循 ADR-001，未重写 `Dispose(bool)`） |

> **Timer 是相机固有产帧语义，不是模拟编排线程**：ADR-042/ADR-032 禁止模组工作流**新增编排线程**，虚拟相机自带帧定时器属相机自身出图节拍，保留。

## GenerateSeamContour

固定 **1000 点** 平直搭接轮廓：单帧 X=0（线激光原理，YZ 构成轮廓线），`t = i/(sampleCount-1)`，`Y = -halfWidth + 2·halfWidth·t`（横向），`Z` 按 `|Y|` 分两段——`|Y| < seamHalf`（`seamHalf = halfWidth × 0.25`）取 `-depth·(1 - |Y|/seamHalf)`（中心搭接缝槽最低点），否则 `Z = 0`（平直搭接面）；再叠加 `depth × 0.02 × sin(Y/halfWidth × π)` 极轻微起伏，保证 YZ 范围有效、避免绝对水平。

## BuildResult（ADR-028 新增，ADR-032 调整中心点口径）

虚拟相机不走英莱算法，遍历点云取 **最接近 y=0 的点**为中心焊缝点（`centerY`/`centerZ`），宽度 = Y 跨度（`maxY - minY`），深度 = `|minZ|`，面积 = 宽 × 深 × 0.5，构造中性 `LineLaserSeamResult`（`Valid=true`、`ParseRes=1`），**用于在模拟模式下打通「结果 → Y 轴目标」链路**——使 [[api/MotionControlWorkflow]] 的 CSP 目标与追踪算法在无真机时也能被验证。

## 协作

- 由 [[api/LineLaserManager]] 激活（`SelectVirtual()`，ADR-032 后由 `DeviceControlWork.ShouldUseVirtualCamera` 自动判定）；被 [[api/LineLaserWorkflow]] 在模拟下驱动；被 [[modules/UIDesign]] 的 [[api/ProcessControlPage]]（`tbPanelSimTest`）仅设定 **线激光数据频率**（经 `LineLaserManager` 套用至 `FrameRateHz`，⛔ 不再设 `SeamProfile`/`RandomMode`）。
- 与英莱相机同为 L3 实现，二者对业务层**完全同构**：业务层只认 `LineLaserCameraBase`。

## 关联

- 模块：[[modules/LineLaserCam]]（本类即 `LineLaserCam/VirtualCam/` 模块全部内容，模块页已并入本页）
- 决策：[[decisions/ADR-024-LineLaserThreeLayerRefactor]]、ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[decisions/ADR-032-SimulationTestRedesign]]
- 同层实现：[[api/IntelligentLaserCam]]

---

*来源：AdaWeldSystem/LineLaserCam/VirtualCam/VirtualCam.cs*
