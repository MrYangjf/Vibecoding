---
title: CameraSelector API 参考
date: 2026-07-16
tags: [API, 相机, 选择]
source: AdaWeldSystem/LineLaserCam/Api/CameraSelector.cs
---

# CameraSelector API 参考

> 相机选择器静态类，位于 `LineLaserCam/Api/CameraSelector.cs`（与 `ICameraRun` 同处线激光相机族统一对外接口层），命名空间 `AdaWeldSystem.LineLaserCamApi`（与 Api 目录对齐，统一对外接口层命名空间）。
> 维护当前激活的 `ICameraRun`（真实 / 虚拟），工作流与界面经 `CameraSelector.Active` 取相机，无需关心具体类型。
> **[2026-07-21 扩展]** 同时聚合「线激光相机连接态」与「相机种类」，并负责启动连通性检测（详见 [[decisions/ADR-018-CameraConnectionStateDecoupled]]）。

## 成员

| 成员 | 说明 |
|------|------|
| `bool IsVirtual { get; }` | 当前是否使用虚拟调试相机 |
| `ICameraRun Active { get; }` | 当前激活相机（未显式选择时默认真实 `CameraRun.Instance`） |
| `CameraKind Kind { get; }` | **[2026-07-21 新增]** 当前配置的相机种类（None/SmartRay/Hik/Virtual/IntelligentLaser） |
| `LineLaserCameraConnectionState ConnectionState { get; }` | **[2026-07-21 新增]** 线激光相机连接状态（连接/断开/工作中），与工作流程状态相互独立 |
| `void SelectVirtual()` | 创建并激活 `VirtualCameraRun`；置 `Kind=Virtual` |
| `void SelectReal()` | 激活真实 `CameraRun.Instance`；置 `Kind=SmartRay` |
| `void SelectIntelligentLaser()` | **[2026-07-24 新增]** 创建并激活 `IntelligentLaserCameraRun`；置 `Kind=IntelligentLaser` |
| `void SetWorking(bool)` | **[2026-07-21 新增]** 由工作流驱动：采集开始置 true（→`Working`），结束置 false（→回退派生态） |
| `void Load()` | 启动时从 `Config/INI/CameraSelector.ini` 恢复相机选择，须在创建任何页面之前调用；优先读 `Camera/Type`，回退历史 `IsVirtual` |
| `void Save()` | 将当前 `IsVirtual` 与 `Kind`（写入 `Camera/Type`）持久化到 `Config/INI/CameraSelector.ini` |
| `void DetectConnection()` | **[2026-07-21 新增]** 启动后按上次配置做连通性检测：Virtual/None 跳过；SmartRay→`CameraRun.OpenSensor`；Hik→`HikCameraRun.OpenSensorByIP`（IP 硬编码 TODO 待读 `CameraPresets.ini`）；IntelligentLaser→`IntelligentLaserCameraRun.OpenSensor("192.168.178.210")`（IP 同样硬编码 TODO） |

## 枚举（定义于 `LineLaserCam/Api/ICameraRun.cs`）

`csharp
// 相机自身连接状态（与工作流程状态相互独立）
public enum LineLaserCameraConnectionState
{
    Disconnected,  // 未连接（无相机或连接失败）
    Connected,     // 已连接，空闲待命
    Working        // 已连接且正在采集/出图中（工作流处于采集态）
}

// 当前配置的相机种类（用于启动检测与状态显示）
public enum CameraKind
{
    None = 0,      // 未配置相机
    SmartRay = 1,  // SmartRay 工业 3D 线激光（真实）
    Hik = 2,       // 海康机器人 3D 线激光（真实，仅检测不接入工作流）
    Virtual = 3,   // 虚拟调试相机（仅模拟测试启用，启动不检测）
    IntelligentLaser = 4  // 英莱(IntelligentLaser) 工业 3D 线激光（真实，接入工作流采集）
}
`

## 连接状态模型（2026-07-21 新增）

> `ConnectionState` 是派生值，**不**由相机自己设置，而是由 `CameraSelector` 聚合：
> - `_working == true` → `Working`（仅 `SetWorking(true)` 驱动，调用方仅为 `LineLaserWorkflow`）。
> - 否则按 `Kind` 派生：
>   - `None` → `Disconnected`
>   - `Virtual` → `Connected`（始终可用；UI 据 `ConnectionState` 再区分「虚拟相机工作中」/「虚拟相机（待启用）」）
>   - `SmartRay` → `CameraRun.Instance.IsConnected ? Connected : Disconnected`
>   - `Hik` → `HikCameraRun.Instance.IsCameraInitialized ? Connected : Disconnected`
>   - `IntelligentLaser` → `_intelligentInstance != null && _intelligentInstance.IsConnected ? Connected : Disconnected`
>
> ⚠️ 相机连接态**只表达硬件事实**，不感知工作流语义；工作流只通过 `SetWorking` 影响「工作中」这一态。

## 启动检测（2026-07-21 新增）

> `FormMain` 构造期在 `CameraSelector.Load()` 之后调用 `CameraSelector.DetectConnection()`（参见 [[guides/Project-Tools]]）。
> - Virtual / None：跳过（虚拟相机仅在模拟测试启用，无硬件可连）。
> - SmartRay：`if (!CameraRun.Instance.IsConnected) CameraRun.Instance.OpenSensor("192.168.178.200", "40")`
> - Hik：`if (!HikCameraRun.Instance.IsCameraInitialized) HikCameraRun.Instance.OpenSensorByIP("192.168.178.201")`
> - IntelligentLaser：`if (_intelligentInstance == null) _intelligentInstance = new IntelligentLaserCameraRun(); if (!_intelligentInstance.IsConnected) _intelligentInstance.OpenSensor("192.168.178.210")`
> - 检测失败（无硬件等）仅表现为「未连接」，不阻塞启动。
> - ⚠️ TODO：IP/Port 当前硬编码，应改从 `Config/INI/CameraPresets.ini` 读取。

## 配置持久化

- 持久化文件：`Config/INI/CameraSelector.ini`（符合 [[decisions/ADR-008-ConfigLayout]]），节 `[Camera]` 键 `IsVirtual`（`1`=虚拟，`0`=真实）与 `Type`（`(int)CameraKind`）。
- `Load()` 优先读 `Camera/Type`（None/SmartRay/Hik/Virtual）；缺省时回退历史 `IsVirtual`。`None`/`Hik` 分支**仅设 `_kind`/`IsVirtual`，不调用 `SelectReal()`**，以免覆盖刚读出的种类（见 [[decisions/ADR-018-CameraConnectionStateDecoupled]]）。
- `Save()` 同时写 `IsVirtual` 与 `Type`，由 `LLCamWorkJob.cmbCameraSelect_SelectedIndexChanged` 在用户切换相机后调用。
- 仅保存**用户显式选择**，工作流内部 `SelectReal()`/`SelectVirtual()`（如 `LineLaserWorkflow.Start()`）不触发 `Save`，避免运行时强制真实相机覆盖用户偏好。

## 使用

- `LineLaserWorkflow` / `MotionControlWorkflow` 取图经 `CameraSelector.Active`（真实回退 `CameraRun.Instance`）。
- `LLCamWorkJob`（`Sub2UI`）`cmbCameraSelect` 下拉框 `SelectedIndexChanged` 切换 `SelectVirtual()`/`SelectReal()` 并调用 `Save()`；`imageBox1` 显示 `CameraSelector.Active.CurrentMat`。

> 真实相机引用 `SmartRayCam.CameraRun`，虚拟相机引用 `VirtualCam.VirtualCameraRun`，二者均实现 [[api/ICameraRun]]。

---

*来源：AdaWeldSystem/LineLaserCam/Api/CameraSelector.cs*
