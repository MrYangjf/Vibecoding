---
title: VirtualCam 模块 — 虚拟调试相机
date: 2026-07-16
tags: [模块, 相机, 虚拟, 调试, 模拟]
source: AdaWeldSystem/LineLaserCam/VirtualCam/ 模块源码
---

# VirtualCam 模块 — 虚拟调试相机

> 与 SmartRayCam **平级**的相机模块，提供「虚拟调试相机」`VirtualCameraRun`，用于不接真实硬件时的模拟测试（A/B 模式）与离线联调。
> **位置**：`AdaWeldSystem/LineLaserCam/VirtualCam/`（2026-07-21 由根目录迁入 `LineLaserCam/` 父目录，与 SmartRayCam / HikRobotCam 同属线激光相机族）。
> 真实相机（`SmartRayCam.CameraRun`）与虚拟相机（`VirtualCam.VirtualCameraRun`）均实现 `ICameraRun` 契约（位于 `LineLaserCam/Api/`，命名空间 `AdaWeldSystem.LineLaserCamApi`），工作流与界面仅依赖接口，不关心具体相机。

## 核心文件

| 文件 | 职责 |
|------|------|
| LineLaserCam/VirtualCam/VirtualCameraRun.cs | 虚拟调试相机：自生成轮廓点云，`class VirtualCameraRun : ICameraRun` |

> ⚠️ **[2026-07-21 上提]** 相机选择器 `CameraSelector` 已迁至 `LineLaserCam/Api/CameraSelector.cs`（与 `ICameraRun` 同处线激光相机族统一对外接口层，命名空间 `AdaWeldSystem.LineLaserCamApi`），详见 [[api/CameraSelector]] 与 [[decisions/ADR-016-CameraSelectorUnifiedToApi]]。`VirtualCam` 现仅保留 `VirtualCameraRun` 实现（命名空间 `AdaWeldSystem.VirtualCam`）。

## VirtualCameraRun 自生成轮廓

- 不依赖 SmartRay SDK，使用程序自有 `PointCloudData`（**非** SmartRay `Api.Point3d`）经 `ImageAlgorithm.ConvertContourToMat(cloud)` 生成 Mat，完全复用真实相机「取帧 → 算法分析」链路。
- `GenerateSeamContour()`：121 采样点，X=0（单帧线激光），Y=横向、Z=深度按 `SimSeamProfile` 生成；逐帧引入 `centerOffset` 变化，使焊缝中心偏离标定中心，产生非零水平移动需求，可驱动后续 `MoveControlData` 缓存与 `MotionControlWorkflow` 水平移动消费。
- `enum SimSeamProfile { VGroove=0, UGroove=1, Flat=2, Random=3 }`：V 型坡口 / U 型坡口 / 平直焊缝 / 随机演化。
- 属性：`SeamProfile`、`RandomMode`、`TargetDistance`、`BaseSeamWidth`、`BaseSeamDepth`（均于构造函数显式初始化，遵循 ADR-002）。
- `SensorRunContinue()`：生成一帧 → `CurrentMat` → 置 `AcquisitionCompletedSignal`（回调等待模式，ADR-005）；`Dispose()` 释放 `_currentMat`。

## CameraSelector 选择逻辑

> 注意：`CameraSelector` 现已上提至 `LineLaserCam/Api/`（见 [[api/CameraSelector]]），不再属于 `VirtualCam` 模块；下方逻辑说明仍适用。

| 调用 | 效果 |
|------|------|
| `CameraSelector.SelectVirtual()` | 创建并激活 `VirtualCameraRun`，`IsVirtual=true` |
| `CameraSelector.SelectReal()` | 回退为 `CameraRun.Instance`，`IsVirtual=false` |
| `CameraSelector.Active` | 取当前相机（虚拟/真实自动回退） |

`LLCamWorkJob`（`Sub2UI`）右侧面板 `cmbCameraSelect` 下拉框（真实相机(SmartRay) / 虚拟调试相机）经 `SelectedIndexChanged` 切换 `CameraSelector` 并 `Save()`；`imageBox1` 显示 `CameraSelector.Active.CurrentMat`。

> **[2026-07-17 持久化修复]** 相机选择此前仅存内存、每次启动重置为真实相机。现新增 `Load()`（启动时由 `FormMain` 在创建子页面前调用，从 `Config/INI/CameraSelector.ini` 恢复）与 `Save()`（用户切换时调用）。详见 [[api/CameraSelector]]。

## 设计决策

- 虚拟相机**不挂载**于 SmartRayCam，而是与之平级的 `VirtualCam` 模块（遵循 ADR-009 的「独立模块」范式，用户明确要求虚拟相机层级与 SmartRay 同级）。
- 相机运行契约 `ICameraRun` 放在 `LineLaserCam/Api/`（线激光相机族统一对外接口目录），三套相机模块共享同一接口。
- 详见 [[decisions/ADR-012-MotionControlModule]]、[[api/VirtualCameraRun]]、[[api/CameraSelector]]、[[api/ICameraRun]]。

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| [[modules/SmartRayCam]] | 共享 `ICameraRun` 契约（`CameraRun` 实现） |
| [[modules/EmguALG]] | `ImageAlgorithm.ConvertContourToMat` / `PipelineManager` |
| [[modules/MotionControl]] | `MotionControlWorkflow` 取图（`CameraSelector.Active`）+ `VirtualCameraRun` 轮廓驱动水平移动缓存 |
| [[modules/UIDesign]] | `LLCamWorkJob`（相机切换）、`MotionControlPage`（模拟参数写入 `VirtualCameraRun`） |

---

*来源：AdaWeldSystem/LineLaserCam/VirtualCam/ 模块源码*
