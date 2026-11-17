---
title: ADR-047 监控相机实现切换海康 MVS
date: 2026-09-29
updated: 2026-10-30
tags: [决策, 监控相机, 海康, MVS, MvCameraControl, MecaVision, SDK 切换, 三层架构]
status: accepted
---

# ADR-047：监控相机实现切换海康 MVS

## 背景

业主实证（2026-09-29）：麦格威（MecaVision）SDK 本质是**海康相机底层魔改**——直接用海康官方 MVS 客户端连接同一台相机效果一致。机器上已安装海康 MVS 客户端：

- 开发文档：`C:\Program Files (x86)\MVS\Development\Documentations`（工业相机Windows SDK开发指南V4.8.1（.NET）等）
- C# 示例：`C:\Program Files (x86)\MVS\Development\Samples\C#\MvCameraControlNet_V2\AreaScanCamera\BasicDemo`（含枚举/打开/取流/取帧/参数全链路）

继续持有麦格威 `MVSDK.cs`（6885 行静态封装）意味着维护一份魔改版二开 SDK，而官方 SDK 有完整文档、示例与长期支持。因此监控相机实现层整体切换为海康 MVS 官方 .NET 封装。

## 决策

1. **实现层换载体、契约不动**：新增 `MonitorCam/HikCam/HikCam.cs`（命名空间 `AdaWeldSystem.MonitorCam.HikCam`，命名空间=类名同形）实现既有 `IMonitorCamApi`（ScanDevices / Connect(ip,port) / Disconnect / CaptureSingleFrame / Dispose / ConnectionState）；抽象层、业务层（`MonitorCamManager`）、UI、工作流零改动——仅 `MonitorCamManager` 构造函数实例化改为 `new HikCam.HikCam()`（[[decisions/ADR-006-ModuleOrganizationPatternStandard]] 三层范式红利兑现）。
2. **封装引用**：`3rdDepend/Hik/MvCameraControl.Net.dll`（取自 `MVS\Development\DotNet\win64\net40`，与 PlatformTarget=x64、.NET 4.8 一致），csproj `<Reference>` HintPath 引用；原生运行时 `MvCameraControl.dll` 由已安装的 MVS 客户端提供（**现场部署机须装 MVS 客户端/运行时**）。
3. **麦格威实现退役**：删除 `MonitorCam/MecaVisionCam/MecaVisionCam.cs` 与 `MonitorCam/MecaVisionCam/Native/MVSDK.cs`（csproj 退注册，`drift_scan_precise.py` REMOVED 登记）；csproj 移除 `3rdDepend/MecaVision/*` 原生依赖复制项（`3rdDepend/MecaVision/` 物理文件保留备查）。
4. **ADR-046 语义原样继承**：`Connect(ip)` 指定 IP 时经 `IGigEDeviceInfo.CurrentIp` 精确匹配（忽略大小写），匹配不到即连接失败并记日志、**不回退枚举首台**；仅 IP 为空取首台；非 GigE（USB3）IP 为空串。连接 IP 先落盘后连接的 UI 链路不变。
5. **取帧链路**（照官方 BasicDemo / Image_ConvertPixelType / GigE_ConnectCameraByIP 示例原文）：
 - `SDKSystem.Initialize()` 进程级一次（静态守卫），`Finalize()` 仅在 `Dispose()`；
 - 连接 = `DeviceEnumerator.EnumDevices` → 按 IP 选台 → `DeviceFactory.CreateDevice` → `Open()` → GigE `GetOptimalPacketSize` 设 `GevSCPSPacketSize` → `AcquisitionMode=Continuous` + `TriggerMode=Off` → ~~`StreamGrabber.StartGrabbing()`（取流常开）~~
 ⚠️ **已被 2026-09-29 业主裁定演进**：连接仅打开设备并预置采集参数（`AcquisitionMode=Continuous` + `TriggerMode=Off`），**不开启取流**（对齐官方 demo「打开设备 ≠ 开始采集」）；采集由 `StartCapture()` 显式开启（`StartGrabbing` + 取帧线程），见 [[decisions/ADR-048-MonitorCamTabsRecordPlayback]] 勘误节；
 - 单次取帧 = `GetImageBuffer(500)` → 彩色经 `device.PixelTypeConverter` 转 `RGB8_Packed`、其余非 Mono8 转 `Mono8` → `IImage.PixelData`（byte[]）经 `Marshal.Copy` 建独立 Mat → `outImage.Dispose()` + `FreeImageBuffer(frameOut)`（必须，否则后续取帧超时）；
 - 海康输出为正常方向，**无需**麦格威 SDK 的垂直镜像步骤。
6. **设备信息映射**：`MonitorCamDeviceInfo` 字段映射 `Ip=CurrentIp 点分解码`、`ProductName=UserDefinedName||ModelName`、`SerialNumber=SerialNumber`、`PortType=TLayerType.ToString()`、`SensorType=ManufacturerName`。

## 备选方案

| 方案 | 结论 |
|---|---|
| 保留麦格威 SDK 作为并行实现 | 放弃：魔改版无官方文档/示例支撑，且与海康客户端驱动同一硬件，双栈徒增维护面 |
| 只改 MecaVisionCam 内部换 MVS 调用 | 放弃：类名与语义（MecaVisionCam）将名不副实，且命名空间=类名同形规约下改名成本为零，直接新建 HikCam 更干净 |
| 原生 P/Invoke 直调 MvCameraControl.dll | 放弃：官方已提供 .NET 封装（BasicDemo 即用），无需自建 Interop 层 |

## 后果

### 正面

- 官方文档 / 示例 / 错误码表齐全，不再依赖 6885 行魔改封装的自证。
- 三层契约零改动，验证了抽象层投资回报：换 SDK 只动了实现层一个目录。
- 严格 IP 匹配、扫描、先落盘后连接等 ADR-046 语义无损继承。

### 负面

- **部署依赖变更**：运行需安装海康 MVS 客户端（提供原生运行时）；`3rdDepend/MecaVision/` 原生件不再随构建复制。
- 行为差异：麦格威断联回调（`CameraSetConnectionStatusCallback`）未在 MVS 版复刻——连接态异常由 `MonitorCamManager` 健康巡检（连接态 + 近期有效采集）兜底，语义等价。
- `MonitorCamera.ini` 历史遗留 IP 若不匹配将连接失败（ADR-046 已有同样后果，非本次新增）。

## 相关页面

- [[modules/MonitorCam]] —— 核心文件表与实现要点更新
- [[api/HikCam]] —— 新实现类 API 页（本决策的落地细节）
- [[api/MonitorCamManager]] —— 实例化载体变更
- [[decisions/ADR-046-MonitorCamIpScanAndStrictMatch]] —— 严格 IP 匹配语义母页
- ADR-019（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）—— 上一轮载体决策（切麦格威），本次整链退役 · [[decisions/ADR-006-ModuleOrganizationPatternStandard]]
- [[guides/MecaVision-DevGuide]]、[[api/MecaVisionMVSDK-Native]] —— 已随本次退役标记 deprecated
