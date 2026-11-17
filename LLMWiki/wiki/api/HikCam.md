---
title: HikCam — 监控相机海康 MVS 实现类（IMonitorCamApi 落地）
date: 2026-09-29
tags: [API, 相机, 监控, 海康, MVS, MvCameraControl, 实现层]
status: accepted
---

# HikCam — 监控相机海康 MVS 实现类

> 监控相机实现层（ADR-047）：以海康官方 `MvCameraControl.Net.dll`（V2 封装）落地 [[modules/MonitorCam|MonitorCam]] 的 `IMonitorCamApi` 契约。文件 `MonitorCam/HikCam/HikCam.cs`，命名空间 `AdaWeldSystem.MonitorCam.HikCam`（**命名空间=类名同形**，实例化必须写 `new HikCam.HikCam()`，裸名报 CS0118）。
> 上一代实现 `MecaVisionCam`（麦格威 MVSDK）已于 2026-09-29 删除。

## 契约方法

> 取流模型（2026-09-29 二次勘误，业主裁定对齐官方 demo）：**连接仅打开设备并预置参数，不开启取流**；连续采集 `StartCapture`（TriggerMode Off + `StartGrabbing` + 取帧线程 GrabLoop，帧经 `PreviewFrame` 逐帧抛出，录像帧由同一线程喂 VideoRecorder）与软触发单帧 `TriggerSingleShot`（TriggerMode On + Software，触发后保持触发模式，`StartCapture` 恢复连续模式）两种；`CaptureSingleFrame` 保留供工作流分析链路。详见 [[decisions/ADR-048-MonitorCamTabsRecordPlayback]] 勘误节（含二次勘误）。

| 成员 | 签名 | 说明 |
|---|---|---|
| `ConnectionState` | `MonitorCameraConnectionState { get; }` | 当前连接态（Disconnected/Connecting/Connected/Error） |
| `IsGrabbing` | `bool { get; }` | 是否正在连续取流（采集） |
| `IsRecording` | `bool { get; }` | 是否正在录像（须处于连续取流中） |
| `PreviewFrame` | `event Action<Mat>` | 连续取流中每帧抛出独立副本 Mat；软触发单帧不经此事件 |
| `ScanDevices()` | `List<MonitorCamDeviceInfo>` | 枚举设备；GigE 经 `IGigEDeviceInfo.CurrentIp` 点分解码，非 GigE IP 为空串；无需已连接 |
| `Connect(ip, port)` | `bool` | 连接；**指定 IP 精确匹配（忽略大小写），不匹配即失败不回退首台**（ADR-046 语义）；`port` 不使用保留契约；成功后**仅置 Connected、不开取流**（demo 语义：连接不采集，2026-09-29 二次勘误） |
| `Disconnect()` | `void` | StopCapture（录像中先停录像）→ Close → Dispose 设备；SDK 全局资源不在此时释放 |
| `StartCapture()` | `bool` | 连续采集（对齐 demo 开始采集）：未取流则 `StartGrabbing`（恢复 TriggerMode Off），随后启动取帧线程；守卫 `IsGrabbing && GrabRunning`——已在采返回 true |
| `StopCapture()` | `void` | 录像中先 StopRecord → 停取帧线程 → StopGrabbing（用户裁定顺序） |
| `CaptureSingleFrame()` | `Mat`（可 null） | 单次取帧（500ms 超时）：GetImageBuffer → 像素归一 → Marshal.Copy 独立 Mat → FreeImageBuffer |
| `TriggerSingleShot()` | `Mat`（可 null） | 软触发单帧：切触发模式 → StartGrabbing → TriggerSoftware → GetImageBuffer(5000) → StopGrabbing（保持触发模式） |
| `StartRecord(path)` | `bool` | 录像 AVI（须在采集中）：RecordParam 宽高取参数 Width/Height（long 收窄 uint）、PixelType 取 PixelFormat 当前值、帧率 ResultingFrameRate（回退 30） |
| `StopRecord()` | `void` | 停止录像 |
| `SetExposureTime(us)` | `bool` | ExposureAuto=0 后 SetFloatValue("ExposureTime") |
| `SetGain(db)` | `bool` | GainAuto=0 后 SetFloatValue("Gain") |
| `GetExposureTime()` | `float` | 读当前曝光（μs）；失败 -1 |
| `GetGain()` | `float` | 读当前增益（dB）；失败 -1 |
| `Dispose()` | `void` | Disconnect + `SDKSystem.Finalize()` |

## 关键事实（MVS 4.8.1 官方示例原文核验）

1. **引用**：`3rdDepend/Hik/MvCameraControl.Net.dll`（win64/net40，与 x64/.NET 4.8 一致）；原生运行时 `MvCameraControl.dll` 由已安装的 MVS 客户端提供——**现场部署机须装 MVS 客户端/运行时**。
2. **SDK 生命周期**：`SDKSystem.Initialize()` 进程级一次（静态守卫 `_sdkInitialized` + `_sdkInitLock`），`Finalize()` 仅 `Dispose()` 调用；枚举层组合 `DeviceTLayerType.MvGigEDevice | MvUsbDevice | MvGenTL*`（照 BasicDemo）。
3. **取流模型**（2026-09-29 二次勘误）：连接**不**开取流（仅预置 `AcquisitionMode=Continuous` + `TriggerMode=Off`），取流/取帧线程由 `StartCapture` 显式开启；每次 `CaptureSingleFrame` 走 `GetImageBuffer(500)`；**成功取帧后必须 `FreeImageBuffer(frameOut)`**，否则后续取帧持续超时（与麦格威 `CameraReleaseImageBuffer` 同构教训）。
4. **GrabLoop 锁边界**：`_sync` 锁内只做 SDK 帧操作（`GetImageBuffer` / `InputOneFrame` / `BuildMat` / `FreeImageBuffer`）；`PreviewFrame` 事件分发**必须在锁外**——锁内同步分发 UI 会与页面/健康链路的锁内 SDK 调用（`CaptureSingleFrame` 等）形成竞争窗口（2026-09-29 实测 AV 成因）。
4. **像素归一**：彩色（Bayer/YUV/BGR8 等，含 10/12bit Packed）→ `PixelTypeConverter.ConvertPixelType(..., RGB8_Packed)`；其余非 Mono8 → 转 `Mono8`；`IImage.PixelData` 为 **byte[]**，`Marshal.Copy` 进新建 Mat 即为独立副本（无需 Clone）。海康输出方向正常，**无垂直镜像**。
5. **GigE 优化**：打开后 `GetOptimalPacketSize` → `GevSCPSPacketSize`；失败仅告警不阻断（照示例）。
6. **无断联回调**：麦格威版的连接状态回调未复刻，链路异常由 `MonitorCamManager` 健康巡检（连接态 + 近期有效采集）兜底，语义等价。
7. **设备信息映射**：`ProductName=UserDefinedName||ModelName`、`SerialNumber`、`PortType=TLayerType.ToString()`、`SensorType=ManufacturerName`。
8. **类型坑（2026-09-29 真编译 CS0266 实证）**：`IImage.Width/Height` 为 **uint**——传 Emgu `Mat` 构造（int 参数）须显式收窄 `(int)`；`uint * int` 按数值提升变 **long**（宽×高×通道数直乘即触发），必须先用 int 变量收窄再相乘；同方法内外层禁止同名局部变量（外层 `List result` 与内层 `int result` 嵌套即 CS0136），SDK 返回码变量统一用 `nRet`/`convRet` 等专名。

## 相关页面

- [[modules/MonitorCam]] · [[api/MonitorCamManager]] · [[decisions/ADR-047-MonitorCamSwitchToHikMvs]] · [[decisions/ADR-046-MonitorCamIpScanAndStrictMatch]]
