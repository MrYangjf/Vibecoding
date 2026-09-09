---
title: 英莱传感器控制与激光/传感器按钮 UI 统一
date: 2026-08-24
tags: [教训, 英莱, 线激光, 传感器, UI, 代码精简]
source: AdaWeldSystem/UIDesign/TabPage/ILCamPage.cs, LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs
---

# 英莱传感器控制与激光/传感器按钮 UI 统一

## 核心结论（2026-08-24 用户澄清 + 代码精简）

### 1. 传感器启停：用 `SetSensor`，弃 `SetCaptureCamera`
- **`SetSensor(bool)`** → `SetSensorEnable`，是 `MillionOutlineInspect` 回调的**触发源头**，是线激光启停传感器的正确方式（`ILCamPage.btnCaptureCamera_Click` 开/关传感器统一调它）。
- **`SetCaptureCamera(bool)`** 仅上电采集相机（YUV 预览），**不起传感器、不触发轮廓回调**，非线激光页面的工作方式。2026-08-24 已从 `ILCamPage` 移除其调用（后端方法保留，`LineLaserWorkflow` 自动流程仍可用）。

### 2. 传感器是否启动：用 `IsCameraOn()`（=`StCtrl.DwCameraEnable`）作真相源
- **用户澄清（2026-08-25）：`StCtrl.DwCameraEnable` 由 `SetSensor(bool)` 控制**——`IsCameraOn()` 即传感器/相机状态真相源。
- **2026-08-25 状态本地化**：`IsCameraOn()`/`IsLaserOn()` 改为**本地状态读取**（`_isCameraOn`/`_isLaserOn`）——连接成功时 `SyncHardwareStatus()` 从硬件同步一次（"第一次正确"），`SetSensor`/`SetLaser` 操作成功后本地更新。UI 点击立即生效，无硬件查询延迟（消除"越点越乱"）。**状态在设备层维护**，UI 层仍不维护本地 bool 副本（不违反 UiStateSimplification 原则①）。
- ❌ **禁止**在 UI 层维护「是否已开传感器」的本地 bool 副本（`_isCameraOn` 之类）——会与设备层状态脱节。
- 激光状态同理用 `IsLaserOn()`（本地 `_isLaserOn`），不维护 UI 层副本。

### 3. 激光/传感器按钮 text 与 `ExtraMouseDown`：单一控制函数 `UpdateLaserSensorUi()`
- 收敛前：`btnLaser_Click` / `btnCaptureCamera_Click` / `SyncFromHardwareCore` / `UpdateConnectionUiCore` 各自独立 set `btnLaser.Text` / `btnCaptureCamera.Text` / `ExtraMouseDown`，text 逻辑重复且易不同步。
- 收敛后：上述四处全部汇聚到 `UpdateLaserSensorUi()` 单一函数，基于 `IsLaserOn()` / `IsCameraOn()` 统一设置两个按钮的 text 与 `ExtraMouseDown`。按钮点击后、硬件同步后、连接态刷新后都调它。

```csharp
private void UpdateLaserSensorUi()
{
    if (_ilCamera == null) return;
    bool laserOn = _ilCamera.IsLaserOn();
    bool sensorOn = _ilCamera.IsCameraOn();
    btnLaser.Text = laserOn ? "关闭激光" : "开启激光";
    btnLaser.ExtraMouseDown = laserOn;
    btnCaptureCamera.Text = sensorOn ? "关闭传感器" : "开启传感器";
    btnCaptureCamera.ExtraMouseDown = sensorOn;
}
```

## 调用映射（ILCamPage）
| 入口 | 动作 | 调 `UpdateLaserSensorUi` |
|------|------|------------------------|
| `btnLaser_Click` | `SetLaser(!IsLaserOn())` | ✅ |
| `btnCaptureCamera_Click` | `SetSensor(!IsCameraOn())` | ✅ |
| `SyncFromHardwareCore`（`RefreshUi(Hardware)`） | `DetectHardwareStatus()` 后 | ✅ |
| `UpdateConnectionUiCore` 断开分支 | 断开后统一刷 text | ✅ |

## 关联
- [[api/IntelligentLaserCam]] — `SetSensor`/`SetCaptureCamera`/`IsCameraOn`/`IsLaserOn`/`DetectHardwareStatus` 契约
- [[lessons/IntelligentLaser-Pitfalls]] — 三层控制解耦（SetSensorEnable 触发回调、SetLaser 仅物理激光、SetCaptureCamera 仅预览）
- [[lessons/UiRefreshUnifiedEntry]] — UI 状态刷新统一入口 `RefreshUi(RefreshUiScope)`
- [[decisions/ADR-025-CodeSimplificationStandard]] — 代码精简规范（去冗余副本、合并重复逻辑）
