---
title: SmartRayCam 模块 — SmartRay 工业3D相机
date: 2026-07-01
tags: [模块, 相机, SmartRay, 线激光]
source: raw/knowledge/AdaWeldSystem_Wiki.md
---

# SmartRayCam 模块 — SmartRay 工业3D相机

> 负责 SmartRay 工业3D轮廓传感器的 SDK 封装、设备连接、参数配置、连续采集控制和数据回调。
> **位置**：`AdaWeldSystem/LineLaserCam/SmartRayCam/`（2026-07-21 由根目录迁入 `LineLaserCam/` 父目录，与 VirtualCam / HikRobotCam 同属线激光相机族）。

## 核心文件

| 文件 | 职责 |
|------|------|
| ApiCore/Sensor.cs | SmartRay SRAPI 传感器底层封装 |
| ApiCore/SensorManager.cs | 传感器管理器（设备发现、连接、配置） |
| ApiCore/SensorState.cs | 传感器状态定义 |
| ApiCore/SensorImageData.cs | 传感器图像数据结构 |
| ApiCore/SensorPointCloud.cs | 传感器点云数据结构 |
| ApiCore/SensorPointCloudMSR.cs | 传感器点云 MSR 数据结构 |
| ApiCore/SensorHelper.cs | 传感器辅助工具方法 |
| ApiCore/PackagedImage.cs | 封装图像数据 |
| CameraRun.cs | 相机运行控制（连续采集循环、回调管理），**2026-07-15 起实现 `ICameraRun`** |
| CameraPresetManager.cs | 相机参数预设管理（曝光/增益/激光功率） |
| Api/ICameraRun.cs | **[2026-07-21 已上提]** 相机运行抽象接口现已上提到 `LineLaserCam/Api/ICameraRun.cs`（线激光相机族统一对外接口），本模块不再保留该文件，详见 [[api/ICameraRun]] |
| VirtualCameraRun.cs / CameraSelector.cs | **[2026-07-16 迁移至 [[modules/VirtualCam]]]** 虚拟调试相机与相机选择器已迁出本模块，作为与 SmartRayCam **平级**的独立 `VirtualCam` 模块（遵循 [[decisions/ADR-012-MotionControlModule]]） |

## 回调等待取图机制

CameraRun.OnCompletedAcqEvent (SmartRay SDK 连续采集回调)
├── if (!IsLiveMode)  // PIL 模式
│     ├── 处理点云数据 → Mat
│     ├── LastAcquisitionSuccess = true/false
│     └── AcquisitionCompletedSignal.Set()  // 通知 Workflow
└── if (IsLiveMode)   // Live 模式：仅显示，不参与 Workflow
      └── 直接更新 Live 显示，不触发 Signal

## 关键属性

| 属性 | 类型 | 说明 |
|------|------|------|
| AcquisitionCompletedSignal | AutoResetEvent | Workflow 等待的回调信号 |
| LastAcquisitionSuccess | bool | 最近一次采集是否成功 |
| CurrentMat | Mat | 当前帧的 OpenCV Mat |
| IsLiveMode | bool | 是否处于实时预览模式 |

## 相机运行抽象层（ICameraRun，2026-07-21 上提至 LineLaserCam/Api/）

> 为支持模拟测试（A/B 模式）与真实相机（C 模式）无缝切换，`ICameraRun` 接口抽象位于 `LineLaserCam/Api/`（线激光相机族统一对外接口），使 `CameraRun`（真实 SmartRay）与 `VirtualCam.VirtualCameraRun`（虚拟）可互换。
> ⚠️ 虚拟调试相机 `VirtualCameraRun` 与相机选择器 `CameraSelector` 已迁出本模块，归与 SmartRayCam 平级的 [[modules/VirtualCam]] 模块（详见 [[decisions/ADR-012-MotionControlModule]]）。

### ICameraRun 接口

```csharp
interface ICameraRun : IDisposable {
    AutoResetEvent AcquisitionCompletedSignal { get; }
    bool IsRunning { get; }
    bool LastAcquisitionSuccess { get; }
    Mat CurrentMat { get; }
    void SensorRunContinue();
    void SensorStop();
}
```

- `CameraRun` 改造：原 `public readonly AutoResetEvent` 字段改为后备字段 `_acquisitionCompletedSignal` + 属性包装；新增 `IsRunning`（映射 `isRun` 字段）以符合接口。
- 状态显示仍直接读 `CameraRun.Instance.isRun`（显示用途，保留兼容）。⚠️ 此处原引 `LLCameraSetting.cs:183` / `LLCamWorkJob.cs:149`，两文件均已改名迁出，现役为 `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` / `UIDesign/TabPage/ILCamPage.cs`，行号已失效。

### CameraSelector 选择逻辑（实现已迁移至 [[modules/VirtualCam]]）

| 调用 | 效果 |
|------|------|
| `CameraSelector.SelectVirtual()` | `IsVirtual=true`，`Active` 返回 `VirtualCameraRun` 实例 |
| `CameraSelector.SelectReal()` | `IsVirtual=false`，`Active` 回退为 `CameraRun.Instance` |
| `CameraSelector.Active` | 取当前选中相机（虚拟/真实自动回退） |

> `CameraSelector` 现位于 `LineLaserCam/Api/CameraSelector.cs`（命名空间 `AdaWeldSystem.LineLaserCamApi`，与 `ICameraRun` 同处统一对外接口层），详见 [[api/CameraSelector]]、[[decisions/ADR-016-CameraSelectorUnifiedToApi]]。本模块 `CameraRun` / `CameraPresetManager` 位于命名空间 `AdaWeldSystem.LineLaserCam.SmartRayCam`（与目录 `LineLaserCam/SmartRayCam/` 一致）。
`LLCamWorkJob` 右侧面板 `cmbCameraSelect` 下拉框（真实相机(SmartRay) / 虚拟调试相机），`SelectedIndexChanged` 切换 `CameraSelector`。

### VirtualCameraRun 自生成轮廓（实现已迁移至 [[modules/VirtualCam]]）

> 虚拟调试相机 `VirtualCameraRun` 已迁出本模块，归与 SmartRayCam 平级的 [[modules/VirtualCam]] 模块，详见 [[api/VirtualCameraRun]]。要点：
- 不依赖 SmartRay SDK，使用程序自有 `PointCloudData`（**非** SmartRay `Api.Point3d`）经 `ImageAlgorithm.ConvertContourToMat(cloud)` 生成 Mat。
- `GenerateSeamContour()`：121 采样点，X=0（单帧），Y=横向、Z=深度按 `SimSeamProfile` 生成；逐帧引入 centerOffset 变化，使水平移动距离非零，可触发后续 [[api/MoveControlData]] 缓存与 `MotionControlWorkflow` 消费。
- 由 [[modules/UIDesign]] 的 `MotionControlPage`「模拟测试参数」组设定 `SeamProfile` / `RandomMode` / `TargetDistance` 等。

## 设计决策

- [[decisions/ADR-005-CallbackAcquisition]]：Workflow 取图使用回调等待模式（取代轮询）
- [[guides/Project-Tools]]：Live 模式不触发 AcquisitionCompletedSignal

---

*来源：raw/knowledge/AdaWeldSystem_Wiki.md + raw/skills/02-Development/CameraSpecialist.md*
