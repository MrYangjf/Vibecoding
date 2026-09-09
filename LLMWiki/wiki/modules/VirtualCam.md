---
title: VirtualCam 模块 — 虚拟调试相机
date: 2026-09-08
tags: [模块, 相机, 虚拟, 调试, 模拟, ADR-038]
source: AdaWeldSystem/LineLaserCam/VirtualCam/ 模块源码
---

# VirtualCam 模块 — 虚拟调试相机

> **位置**：`AdaWeldSystem/LineLaserCam/VirtualCam/`，与 `IntelligentLaserCam/` 平级，同属 `ILineLaser/` 抽象之下的实现层（2026-09-08 ADR-038 重排）。
> **2026-09-08**：由实现 `ICameraRun` 改为继承 `LineLaserCameraBase`（[[modules/LineLaserCam]]）；注册与选中统一由 `LineLaserManager` 承担，本模块不再持有选择器。

> **2026-09-08 补模拟节拍（ADR-040）**：`SensorRunContinue()` 起 `System.Threading.Timer`（33ms ≈ 30Hz）持续产帧，`SensorStop()` / `Dispose()` 停表；
> 此前每次调用只出一帧，工作流 `PreWork` 凑不满 5 帧必然超时。

## 核心文件

| 文件 | 职责 |
|------|------|
| LineLaserCam/VirtualCam/VirtualCam.cs | 虚拟调试相机：自生成轮廓点云，`class VirtualCam : LineLaserCameraBase`；`enum SimSeamProfile`（**2026-09-08 由 `VirtualCameraRun.cs` 改名**） |

## VirtualCam 自生成轮廓

- 不依赖任何相机 SDK，使用程序自有 `PointCloudData` 生成轮廓；⛔ **自绘 Mat 已删**（原 `ImageAlgorithm.ConvertContourToMat(cloud)` → `CurrentMat`），ADR-039 起显示 Mat 由 [[api/ProfileMatRenderer]] 在业务层按需生成。
- `GenerateSeamContour()`：121 采样点，X=0（单帧线激光），Y=横向、Z=深度按 `SimSeamProfile` 生成；逐帧引入 `centerOffset` 变化，使焊缝中心偏离标定中心，产生非零水平移动需求。
- `enum SimSeamProfile { VGroove=0, UGroove=1, Flat=2, Random=3 }`：V 型坡口 / U 型坡口 / 平直焊缝 / 随机演化。
- 属性：`SeamProfile`、`RandomMode`、`TargetDistance`、`BaseSeamWidth`、`BaseSeamDepth`（均于构造函数显式初始化，遵循 ADR-002），由 `LineLaserManager.ApplyConfig()` 从 XML 配置套用。
- `SensorRunContinue()`：生成一帧点云 → `RaiseResultReady(BuildResult(cloud), 0)` + `RaiseProfileReady(cloud, 0)` → 置 `AcquisitionCompletedSignal` → `RaiseStateChanged()`（⛔ 原 `RaiseFrameReady` 已删，ADR-039）。
- `BuildResult(cloud)`：以**最低点为焊缝特征点**推算中性 `LineLaserSeamResult`，使模拟模式也能走通「结果 → Y 轴 PVT」链路（[[api/SeamPvtFeeder]]）。
- `IsConnected` 恒为 `true`（虚拟相机无硬件连接语义），`ScanRateHz` 恒为 120。

## 选中方式（2026-09-08 起）

| 调用 | 效果 |
|------|------|
| `LineLaserManager.Instance.SelectVirtual()` | 创建并激活 `VirtualCam`，`IsVirtual=true` |
| `LineLaserManager.Instance.SelectIntelligentLaser()` | 切回英莱真实相机，`IsVirtual=false` |
| `LineLaserManager.Instance.Active` | 取当前相机；未显式选择时按 `Config.DefaultKind` 惰性创建 |

> 旧 `CameraSelector.SelectVirtual()` / `SelectReal()` 与 `Config/INI/CameraSelector.ini` 已随 ADR-038 删除；相机选择持久化改由 `LineLaserConfig.DefaultKind` 承载。

## 设计决策

- 虚拟相机与真实相机**平级**，共享同一抽象基类，可无缝互换注入 [[api/LineLaserWorkflow]]。
- 抽象契约与事件基础设施上提基类，实现层只保留「产帧 + 硬件交互」。
- 详见 [[decisions/ADR-038-LineLaserThreeLayerRefactor]]、[[decisions/ADR-039-LineLaserResponsibilitySplit]]、[[api/VirtualCam]]、[[api/LineLaserManager]]。

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| [[modules/LineLaserCam]] | 同族抽象与管理器 |
| [[modules/EmguALG]] | `ImageAlgorithm.ConvertContourToMat` / `PipelineManager` |
| [[modules/MotionControl]] | `MotionControlWorkflow` 取图（`LineLaserManager.Instance.Active`）+ 虚拟轮廓驱动水平移动缓存 |
| [[modules/UIDesign]] | `MotionControlPage`（模拟参数写入 `VirtualCam`） |

---

*来源：AdaWeldSystem/LineLaserCam/VirtualCam/ 模块源码*
