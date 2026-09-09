---
title: ADR-016 CameraSelector 上提至 LineLaserCam/Api 统一对外接口层
status: accepted
date: 2026-07-21
tags: [决策, 相机, 目录, 线激光, 接口层, 重构]
---

# ADR-016 CameraSelector 上提至 LineLaserCam/Api 统一对外接口层

## 状态
Accepted（已采纳，2026-07-21 执行）

## 背景（Context）

- `CameraSelector` 最初位于 `LineLaserCam/VirtualCam/CameraSelector.cs`，仅因为历史上它只在「真实相机（SmartRay）/ 虚拟调试相机」之间切换。
- 经 [[decisions/ADR-015-CameraConnectionStateDecoupled]] 扩展后，`CameraSelector` 已演变为跨 **SmartRay / Hik / Virtual** 三套线激光相机的**族级编排器**：
  - 选择逻辑覆盖三种相机（`SelectReal`→SmartRay、`SelectVirtual`→Virtual、`Load` 依据 `Camera/Type` 还可能选 Hik）；
  - 聚合「相机连接态模型」：`Kind` / `ConnectionState` / `SetWorking` / `DetectConnection`（`CameraKind`、`LineLaserCameraConnectionState` 枚举已与 `ICameraRun` 同文件 `LineLaserCam/Api/ICameraRun.cs`）。
- 此前 2026-07-21 已将 `ICameraRun` 由 `SmartRayCam/Api/` 上提至 `LineLaserCam/Api/`，作为「线激光相机族统一对外接口」（见 [[modules/LineLaserCam]]、[[api/LineLaserManager]]）。`CameraSelector` 仍留在 `VirtualCam/` 与之割裂。

## 决策（Decision）

将 `CameraSelector.cs` 由 `LineLaserCam/VirtualCam/` **迁移至 `LineLaserCam/Api/`**，与 `ICameraRun` 共同构成线激光相机族的**统一对外接口层**。

- **命名空间（初版决策：保持不变）**：`AdaWeldSystem.VirtualCam`。遵循项目既有惯例「命名空间与目录解耦」（ICameraRun 上提后命名空间仍为 `AdaWeldSystem.SmartRayCameraRun`）。
- **命名空间（2026-07-21 修订：与目录对齐）**：用户要求将 `LineLaserCam/Api/` 下两文件命名空间统一为 `AdaWeldSystem.LineLaserCamApi`。故 `CameraSelector` 由 `AdaWeldSystem.VirtualCam` 改为 `AdaWeldSystem.LineLaserCamApi`；`ICameraRun` 由 `AdaWeldSystem.SmartRayCameraRun` 改为 `AdaWeldSystem.LineLaserCamApi`。调用方相应调整 `using`：`CameraSelector` 自身保留 `using AdaWeldSystem.SmartRayCameraRun;`（直接引用 `CameraRun.Instance`，与目录解耦：`CameraRun` 命名空间仍为 `SmartRayCameraRun`）；`FormMain`/`LLCamWorkJob`/`LineLaserWorkflow` 新增 `using AdaWeldSystem.LineLaserCamApi;`（用于 `CameraSelector` 及枚举）并保留 `using AdaWeldSystem.SmartRayCameraRun;`（用于 `CameraRun`）；`SimulationWorkflow`（⛔ 已于 2026-09-03 删除、成员归并 `DeviceControlWork`）新增 `using AdaWeldSystem.LineLaserCamApi;`；`VirtualCameraRun`/`CameraRun` 将 `using AdaWeldSystem.SmartRayCameraRun;` 改为 `using AdaWeldSystem.LineLaserCamApi;`。`MotionControlPage`/`MotionControlWorkflow` 的 `using AdaWeldSystem.VirtualCam;` 变为未使用（无害，保留）。
- **`.csproj` 同步**：`<Compile Include>` 路径由 `LineLaserCam\VirtualCam\CameraSelector.cs` 改为 `LineLaserCam\Api\CameraSelector.cs`（遵循 [[guides/Namespace-Compilation]]）。
- **`VirtualCam` 模块收窄**：仅保留 `VirtualCameraRun`（虚拟相机实现），不再持有选择器。

## 后果（Consequences）

- ✅ `CameraSelector` 与 `ICameraRun` 同处 `LineLaserCam/Api/`，族级接口边界清晰，呼应「`CameraSelector` 是 LineLaserCam 业务而非 VirtualCam 专属」的诉求。
- ✅ 无行为变化：`DetectConnection`/`SetWorking`/连接态模型语义不受影响；命名空间由 `VirtualCam` 改为 `LineLaserCamApi`，各文件 `using` 相应调整（含 `CameraSelector` 自身保留 `SmartRayCameraRun` 以引用 `CameraRun`，见 [[guides/Namespace-Compilation]]）。
- ✅ 迁移符合 [[guides/Namespace-Compilation]]（csproj 已更新）与 [[guides/Project-Tools]]（`FormMain` 启动期 `Load()`/`DetectConnection()` 调用点未变）。
- ⚠️ 物理位置（`Api/`）与命名空间（`VirtualCam`）不一致——这是项目既定惯例，非本次引入；若未来要彻底统一命名空间为 `AdaWeldSystem.LineLaserCam.Api` 之类，需同步改造 `ICameraRun` 及所有实现者命名空间，属更大重构，本次不做。

## 相关
- [[decisions/ADR-015-CameraConnectionStateDecoupled]]（连接态模型，CameraSelector 已聚合）
- [[api/LineLaserManager]]（迁移后位置与用法）
- [[api/LineLaserManager]]（同处 Api/ 的统一契约）
- [[modules/LineLaserCam]]（族级目录与统一对外接口层）
- [[modules/VirtualCam]]（迁移后仅含 VirtualCameraRun）
- [[guides/Namespace-Compilation]]（csproj 注册）
- [[guides/Project-Tools]]（启动加载）
