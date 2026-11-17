---
title: ADR-046 监控相机 IP 扫描与严格匹配
date: 2026-09-29
updated: 2026-10-30
tags: [决策, 监控相机, UI, 顶栏, 扫描, IP 匹配, MecaVision, 配置]
status: accepted
---

# ADR-046：监控相机 IP 扫描与严格匹配

> ⚠️ **演进（2026-09-29）**：本页决策全部继续有效；实现载体的麦格威专属措辞（`CameraEnumerateDevice` / `CameraGigeGetIp` / `MecaVisionCam.ScanDevices`）已随 [[decisions/ADR-047-MonitorCamSwitchToHikMvs]] 演进为海康 MVS 对应物（`DeviceEnumerator.EnumDevices` / `IGigEDeviceInfo.CurrentIp` / `HikCam.ScanDevices`），语义不变。

## 背景

线激光调试页（`UIDesign/TabPage/ILCamPage`）顶栏早已具备完整连接入口：连接态 `Alert` + 「相机IP」标签 + IP 输入框 + 扫描按钮 + 连接/断开按钮（`StatustabPanel`），并配 `ILScanForm` 单选回填、选中即保存到 `LineLaserConfig.SensorIp`。

监控（焊接）相机页（`UIDesign/TabPage/MonitorCamPage`）**只有** `lblStatus`（文本「相机: 未连接」）与 `uiLightStatus` 信号灯，**没有** IP 输入、没有设备扫描、没有显式连接/断开入口；IP 只能靠 `Config/MonitorCam/Monitor_INI/MonitorCamera.ini` 手工改。

同时实现层 `MecaVisionCam.SelectDevice()` 在**指定 IP 未匹配到任何设备时静默回退枚举首台**——单机台架无感，现场多台相机时可能连到非目标相机，属 [[guides/MecaVision-DevGuide]] §10 OPEN-1 遗留隐患。

业主需求（2026-09-29）：**参考线激光调试页面 UI 顶栏的设置，焊接（监控）相机也需要找到 IP 和设备，保存连接 IP。**

## 决策

1. **顶栏复刻**：`MonitorCamPage` 采用与线激光页同构的连接顶栏——`TableLayoutPanel`（6 列：连接态 Alert / 弹性间隔 / 「相机IP」Label / IP 输入 / 扫描 / 连接），置于页面**全宽顶行**（既有根 `tableLayoutPanel1` 由 1 行扩为 2 行，顶行 `Absolute 45F`，图像框与右侧调试面板下移至第 1 行）。
2. **扫描能力三层落位**（照 [[decisions/ADR-006-ModuleOrganizationPatternStandard]]）：
 - 抽象层 `IMonitorCamApi.ScanDevices() : List<MonitorCamDeviceInfo>` + 新类型 `MonitorCamDeviceInfo`（IP / 产品名称 / 序列号 / 接口类型 / 传感器类型）；
 - 实现层 `MecaVisionCam.ScanDevices()`：`CameraSdkInit` → `CameraEnumerateDevice` → 逐台 `CameraGigeGetIp`；非 GigE（USB3）相机 IP 返回空字符串；
 - 业务层 `MonitorCamManager.ScanDevices()` 为**对外唯一口**，UI 不感知 SDK。
3. **扫描结果对话框**：新增 `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm`（照 [[decisions/ADR-036-UIControlPlacementRule]] 归 `SubDialog/<业务域>Dialog/`），复用 `ILScanForm` 的 Table 单选范式（`ColumnCheck` + `SetAutoCheck(false)` + `CellClick` 手动互斥），确定后回填选中 IP。
4. **保存连接 IP**：扫描选中或手工输入后，一律**先落盘再连接**——写 `MonitorCamConfig.IpAddress` → `MonitorCamManager.SaveConfig()`（`SaveToIni(MonitorCamConfig.DefaultConfigPath)`）→ 再 `OpenSensor`。
5. **严格 IP 匹配（本决策的关键行为变更）**：`Connect(ip, port)` 在 `ip` 非空时必须精确匹配某台相机（`CameraGigeGetIp` + 忽略大小写）；**匹配不到即连接失败并记日志，不再回退枚举首台**；仅当 `ip` 为空时才取枚举首台。UI 侧失败即 `AntdUI.Message.warn` 提示「连接失败，请检查IP {ip} 与设备是否匹配！」。
6. **连接/断开入口**：`MonitorCamManager.OpenSensor` 由 `void` 改为**返回 `bool`**（既有唯一调用方 `MonitorCameraWorkflow.EnsureConnected` 为语句调用，源码兼容）；新增 `MonitorCamManager.CloseSensor()`（停巡检 + `_api.Disconnect()`）——此前 `InitializeOff` / `ConnectOff` **只改状态、不断硬件**，UI 断开按钮需要真正释放设备。
7. **连接态驱动**：连接/断开后由工作流 `ConnectOn` / `ConnectOff` 同步「监控相机」子设备态（与线激光页同构）；顶栏自身按页面既有 500ms 定时器节拍 `UpdateConnectionUi()`，覆盖工作流自动连接等非本页发起的连接。

## 备选方案

| 方案 | 结论 |
|---|---|
| 复用 `ILScanForm` | 放弃：参数类型为 `IlSensorInfo`（英莱专用），监控相机复用需改公共类型，违反 ADR-003 枚举/类型去重精神 |
| 在 UI 内直接 `MvApi` 枚举 | 放弃：UI 感知 SDK，破坏三层边界（ADR-006） |
| 保留「IP 不匹配回退首台」 | 放弃：现场多相机时静默连错设备，且与「找到 IP 和设备」的需求相反；改为失败即报错，由用户扫描后重连 |
| IP 输入框设为只读（照线激光 `txtIP.ReadOnly = true`） | 放弃：本决策要求「保存连接 IP」，允许手工输入更便于现场调试；线激光页仍保持只读 |

## 后果

### 正面

- 监控相机页获得与线激光页一致的连接入口：可见连接态、可扫描设备、可存 IP、可连接/断开。
- IP 语义变为**确定**：配错 IP 立即报错，不会连到别的相机。
- 设备枚举能力落位抽象层，后续换 SDK/加实现零 UI 改动。

### 负面

- **行为变更**：`MecaVisionCam.Connect` 不再对错误 IP 做兜底。历史配置 `MonitorCamera.ini` 若 IP 与实际不符，`MonitorCameraWorkflow.EnsureConnected`（初始化链 / 手动连接）将直接失败——需现场用扫描按钮确认 IP 后重新保存（默认值仍为 `192.168.1.100`）。
- `ScanDevices()` 每次调用 `CameraSdkInit(0)`：与既有 `Connect` 的初始化方式一致（模块既有约定），未引入新的生命周期管理。

## 相关页面

- [[modules/MonitorCam]] —— 模块核心文件与职责更新
- [[api/MonitorCamManager]] —— 新增 `ScanDevices` / `CloseSensor` / `SaveConfig`，`OpenSensor` 返回 bool
- [[api/MecaVisionMVSDK-Native]] —— `CameraEnumerateDevice` / `CameraGigeGetIp` 用法
- [[guides/MecaVision-DevGuide]] —— §10 OPEN-1（GigE IP 匹配）闭环
- [[decisions/ADR-006-ModuleOrganizationPatternStandard]]、[[decisions/ADR-016-WorkflowResponsibilityBoundary]]、[[decisions/ADR-036-UIControlPlacementRule]]、[[decisions/ADR-021-CameraConnectionStateDecoupled]]
- [[decisions/ADR-019-MonitorCamBoundaryAndEmguALGRefinement]] —— 监控相机现行决策母页
