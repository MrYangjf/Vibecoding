---
title: ILCamPage 英莱线激光相机页
date: 2026-11-17
updated: 2026-11-17
tags: [API, UI, 线激光, 英莱, 权限, 页面生命周期, ADR-105]
source: AdaWeldSystem/UIDesign/TabPage/ILCamPage.cs + .Designer.cs
---

# ILCamPage — 英莱线激光相机页

> 页面职责：显示线激光相机连接态、轮廓预览、识别结果、JOB 与帧率设置。**只查询、不直连硬件**；连接/断开统一交 `LineLaserWorkflow` 后台线程，页面释放不断设备。

## 基本信息

| 项 | 值 |
|---|---|
| 类 | `AdaWeldSystem.UIDesign.TabPage.ILCamPage` |
| 基类 | `UserControl`（由 `NavPage` 挂载） |
| 文件 | `UIDesign/TabPage/ILCamPage.cs` + `.Designer.cs` |
| 挂载 | `FormMain` → `navPageParam.LoadTabs(..., ("线激光设置", new ILCamPage(), ...))` |
| 真相源 | 连接态 = `LineLaserWorkflow.State`；硬件回填由 `StateSwitched` 边沿触发 |

## 连接与断开（ADR-105）

| 动作 | 实现 |
|---|---|
| 连接 | 校验 IP 非空 → 写 `LineLaserManager.Config.SensorIp` 并 `SaveConfig()` → `LineLaserWorkflow.ConnectOn()`；受理失败提示「连接正在进行中」 |
| 断开 | 仅 `LineLaserWorkflow.ConnectOff()`；不再调用相机实例 `DisconnectManual()` |
| 状态判据 | `LineLaserWorkflow.Instance.State == SubDeviceState.Connected` |
| 硬件回填 | `Disconnected→Connected` 时 `RefreshUi(Hardware)`：同步激光/传感器开关、JOB 列表、帧率模式 |

⛔ 页面内不得出现 `_ilCamera.ConnectManual(...)` / `_ilCamera.DisconnectManual(...)`（缺陷 D18 已关闭）。

## 页面动作门控

`TryPassPageAction(action)` 按顺序判定，任一不通过即提示并记 Warning：

| 档 | 判据 | 提示 |
|---|---|---|
| 关闭中 | `DeviceControlWork.IsShuttingDown` | 程序正在关闭，暂不支持该动作 |
| 初始化中 | `DeviceControlWork.IsInitializing` | 设备初始化中仅可查询，该动作已拒绝 |
| 权限不足 | `!PermissionLevel.IsEngineerOrAbove(GlobalCommData.mOperateLevel)` | 无权该动作，需工程师及以上权限 |

初始化/关闭期间 `btnConnect` 置灰，`alert_ConnStatus` 显示「初始化中，连接已锁定」（橙色）；`InitializationCompleted` 回调恢复按钮与标签。

## 页面释放

`HandleDestroyed` 只做：退订 `WeldStatusChanged` / `StateSwitched` / `InitializationCompleted` / `MatUpdated` / `JobParamsChanged`、释放 `_displayedClone`。**不断设备、不改设备态**；设备断开归主设备关闭链。

## 其它交互（不受本轮改动影响）

- 扫描相机（UDP 广播发现）→ 选中后自动填 IP 并保存配置。
- 激光 / 传感器开关、JOB 切换、帧率模式切换：运行中（PreWork/Working/Stopping）统一禁用。
- 自动运行时本页不绘制 Mat，结果交主页面。

## 相关页面

- [[decisions/ADR-105-page-action-workflow-and-permission-gate]]
- [[api/LineLaserWorkflow]]
- [[api/LineLaserManager]]
- [[modules/UIDesign]]
