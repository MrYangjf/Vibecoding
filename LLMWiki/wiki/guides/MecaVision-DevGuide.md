---
title: MecaVision 监控相机开发指导
date: 2026-09-08
tags: [指导, 相机, 监控相机, MecaVision, MVSDK, 麦格威]
source: raw/knowledge/监控相机开发指导_MecaVision版.md（二手，已核验订正）+ raw/mecavision/（SDK 原文）
---

# MecaVision 监控相机开发指导

> **结论先行**：麦格威（MecaVision）MVSDK 作为监控相机新 SDK，**不新建平行模块**——以
> `MecaVisionCameraApi` 实现**现有** `IMonitorCameraApi` 契约（[[modules/MonitorCam]]、[[decisions/ADR-007-MonitorCameraModule]]），
> 在 `MonitorCamManager` 处替换/切换海康实现，业务层（`MonitorCameraWorkflow`）与 UI（`MonitorCamPage`）**零改动**。
> 二手文档《监控相机开发指导_MecaVision版》的**线程模型/帧缓存/踩坑清单可复用**；其**目录树与类名不可照抄**（见 §5 订正表）。
> SDK 原文核验：33 个声称 API **零臆造**（2026-09-08 脚本核对，见 [[api/MecaVisionMVSDK-Native]]）。
> 架构决策见 [[decisions/ADR-037-MecaVisionMonitorCamera]]。

## 章节导航

- [1. SDK 资产清单](#1-sdk-资产清单)
- [2. 工程配置](#2-工程配置)
- [3. 落地目录结构（对照现有实现）](#3-落地目录结构对照现有实现)
- [4. 典型流程（以官方例程实证）](#4-典型流程以官方例程实证)
- [5. 二手文档订正表（必读）](#5-二手文档订正表必读)
- [6. 契约适配映射](#6-契约适配映射)
- [7. 线程模型与帧缓存（复用二手文档结论）](#7-线程模型与帧缓存复用二手文档结论)
- [8. 踩坑清单](#8-踩坑清单)
- [9. 落地步骤（代码实施 plan）](#9-落地步骤代码实施-plan)
- [10. OPEN 清单](#10-open-清单)

## 1. SDK 资产清单

SDK 包已归档：`LLMWiki/raw/mecavision/MecaVision_SDK…/MecaVision/`

| 资产 | 路径 | 用途 |
|------|------|------|
| `MVSDK.cs` | `Demo/C#/MVSDK/MVSDK.cs` | **C# 官方封装源文件（6885 行，静态类 `MvApi`）**——拷入项目即用 |
| `MVCAMSDK.dll` / `MVCAMSDK_X64.dll` | `SDK/`、`SDK/X64/` | 原生主库（x86/x64） |
| `MVImageProcess.dll`（_X64） | `SDK/`、`SDK/X64/` | 图像处理库（ISP） |
| `*.Interface` | `SDK/`、`SDK/X64/` | GigE/USB3 协议插件 |
| `MVSDK_API_CHS.chm` / `_ENG.chm` | `Document/` | 官方 API 手册 |
| C# 例程 ×12 | `Demo/C#/` | FirstStep（Grabber 路径）、TriggerAndStrobe（触发+闪光灯）、GPIO、ROI、SaveImage、Record、TwoCameras、WpfFirstStep 等 |
| **C 原生头文件**（6 个） | `SDK/Include/` | **接口声明真相源**：`CameraApi.h`（`extern "C"` 全部 API）· `CameraApiLoad.h` · `CameraDefine.H`（枚举/结构体）· `CameraStatus.h`（错误码）· `RawDecodeApi.h` · `mvocx.h`。**2026-09-14 从 `Demo/VC++/Include/` 抽入**并独立存放 |
| 驱动 | `Drivers/USB/` | USB 相机驱动 |

> ⚠️ **原档裁剪（2026-09-14）**：`Demo/` 现仅保留 **C# 例程**（本项目技术栈）。其余 10 种语言示例（LabView / Delphi6 / VB6 / VB.NET / QT / QT5 / Java / Python / Visual FoxPro8 / C++ Builder）与 VC++ 的 MFC 样板、`.cpp` 范例已删除；**其中唯一的 C 原生头文件已抽存至 `SDK/Include/`**（删前已核验 `Demo/VC++/Include` 与 `Demo/QT/Include` 同 md5，仅存一份）。`Demo/` 26.07 MB → 1.29 MB。原始完整性由 `LLMWiki_backup_20260913_211524.tar.gz` 保障。

## 2. 工程配置

1. **`MVSDK.cs` 原样拷入** `MonitorCam/Native/MVSDK.cs`，命名空间按项目惯例调整（文件内为 `MvApi` 静态类 + pfn 委托 + 结构体/枚举）。
2. **csproj 注册**：`MonitorCam\Native\MVSDK.cs` 与 `MonitorCam\Api\MecaVisionCameraApi.cs` 各加 `<Compile Include>`（[[guides/Namespace-Compilation]] §1.1）。
3. **平台目标**：必须显式 x86 或 x64（与台达模块一致），**禁 AnyCPU**——`MvApi` 静态构造按 `IntPtr.Size` 加载对应 DLL。
4. **DLL 部署**：所选位数对应的 `MVCAMSDK*.dll` + `MVImageProcess*.dll` 与 exe 同目录（参照海康「原生 DLL 由运行时提供」的部署心智，但麦格威需**自己拷**到输出目录）。**2026-09-09 增补**：仅落 `3rdDepend/MecaVision/` 不够——必须把 4 个文件（`MVCAMSDK_X64.dll`、`MVImageProcess_X64.DLL`、2 个 `*.Interface` 协议插件）加进 csproj `CopyNative3rdDependToOutput` 目标，否则输出目录无 DLL，`MvApi` 静态构造 `LoadLibrary` 静默失败、委托全 null，首次调用即 NullReferenceException（见 [[lessons/MecaVision-NativeDllLoadNRE]]）。
5. **管理员权限**：SDK 访问注册表，Win7/8 非管理员报 -13；程序 `app.manifest` 申请管理员权限。

## 3. 落地目录结构（✅ 2026-09-08 已按此落地，ADR-037 accepted）

**三层结构（用户裁定：不保留海康实现，参照 MotionControl/线激光范式）**：

```
MonitorCam/
├── IMonitorCam/                    # 抽象层 L2：MonitorCamType.cs（3 枚举）+ MonitorCamEventArgs.cs（2 事件参数）+ IMonitorCamApi.cs
├── MecaVisionCam/                  # 麦格威实现层 L3（只做回调触发，ADR-039 准则）
│   ├── MecaVisionCam.cs            # 实现 IMonitorCamApi（Connect/StartAcquisition/CaptureSingleFrame/FrameReceived）
│   └── Native/MVSDK.cs             # 官方封装原样拷贝（静态类 MvApi，6885 行，动态加载 MVCAMSDK.dll）
└── MonitorCamManager.cs            # 业务中枢（原 MonitorCamManager 改名承接），见 [[api/MonitorCamManager]]
```

**依赖方向**：`MonitorCamManager → IMonitorCamApi ← MecaVisionCam → Native/MvApi → MVCAMSDK.dll`。业务层与 UI 不感知 SDK（与 [[modules/LineLaserCam]] 三层范式同构）。原 `Api/HikvisionCameraApi.cs` 已整删（ADR-038 先例），`MvCameraControl.Net` 引用已从 csproj 移除，原生 DLL 部署 `3rdDepend/MecaVision/`（x64）。

## 4. 典型流程（以官方例程实证）

### 4.1 FirstStep 例程（Grabber 高层路径，调试/预览用）

调用序列实录（`Demo/C#/FirstStep/Form1.cs`）：

```
CameraEnumerateDevice → CameraGrabber_Create / CreateFromDevicePage
→ CameraGrabber_GetCameraDevInfo / GetCameraHandle
→ CameraGetCapability → CameraSetIspOutFormat
→ CameraGrabber_SetRGBCallback → CameraGrabber_SetHWnd
→ CameraGrabber_StartLive / StopLive / SaveImage / GetStat
→ CameraImage_SaveAsBmp → CameraImage_Destroy → CameraGrabber_Destroy
```

> Grabber 是**高层封装**（自带显示/ISP/统计），适合调试工具；**生产模块走低层 API**（§4.2），控制粒度更细、符合 ADR-027 数据归属。

### 4.2 TriggerAndStrobe 例程（低层路径，生产模块参照）

调用序列实录：

```
初始化：CameraEnumerateDevice → CameraInit → CameraGetCapability
        → CameraSetIspOutFormat → CameraSetCallbackFunction
采集：  CameraPlay → (帧回调或 CameraGetImageBuffer)
处理：  CameraImageProcess → CameraDisplayRGB24（显示）/ 转 Mat
释放：  CameraReleaseImageBuffer → CameraUnInit
触发：  CameraSetTriggerMode → CameraSetExtTrigSignalType
        → CameraSetStrobeMode / StrobePolarity / StrobeDelayTime
        → CameraSetOutPutIOMode / CameraSetIOState
```

### 4.3 推荐的生产初始化顺序

```
1. MvApi.CameraSdkInit(1)                    // 必须最先
2. MvApi.CameraEnumerateDevice               // 枚举
3. MvApi.CameraInit(ref devInfo, -1, -1, ref hCamera)   // 打开（SN/IP 匹配见 §10 OPEN-1）
4. MvApi.CameraLoadParameter(...)            // 参数文件（推荐，免自研参数 UI）
   └─ 或逐项 CameraSetExposureTime / CameraSetAnalogGain / CameraSetTriggerMode
5. MvApi.CameraSetConnectionStatusCallback   // 断联回调（SDK 自带，无需心跳）
6. MvApi.CameraSetCallbackFunction + CameraPlay   // Live 采集
```

## 5. 二手文档订正表（必读）

> 二手文档按「另一项目」风格写（平行新建 `MonitorCamera/` 模块），与本项目 ADR-009 现状冲突。**API 名零臆造**，订正集中在架构映射：

| # | 二手文档声称 | 核验结论 | 采纳 |
|---|-------------|---------|------|
| 1 | 新建 `MonitorCamera/` 目录 + `IVisionCamera` 接口 + `MonitorCameraManager` + `CameraFrameStore` + `CameraWorkflow` | 与 ADR-009/ADR-027 现状冲突（已有 `MonitorCam/` + `IMonitorCameraApi` + `MonitorCamManager` + `MonitorCameraWorkflow`） | ⛔ 不新建；新增 `MecaVisionCameraApi` 实现现有契约 |
| 2 | `MVSDK.cs` 6884 行 / 静态类 `MvApi` | 实测 **6885 行**，类名属实 | ✅ |
| 3 | DLL：`MVCAMSDK.dll`/`MVCAMSDK_X64.dll` + `MVImageProcess.dll`，动态加载，按位数选择 | 与 `SDK/`、`SDK/X64/` 原文一致；`MvApi` 静态构造 `IntPtr.Size==8` 判断属实 | ✅ |
| 4 | 33 个 API 名 + 13 个错误码数值 + 9 结构体 | **逐一核对全对，零臆造** | ✅ |
| 5 | 抽象接口 `Connect(int timeoutMs)` / `SoftTrigger()` / `SaveImage(path)` | 现有契约为 `Connect(ip, port)` / `CaptureSingleFrame(): Mat`，**无 SoftTrigger 直通** | ⚠️ 按现有契约适配（§6） |
| 6 | `FrameData` / `TriggerMode` / `CameraStatusChanged` 新类型 | 现有 `MonitorFrameEventArgs` / `MonitorCameraConnectionState` 已承载同语义（ADR-026 枚举去重精神） | ⛔ 不新增平行类型 |
| 7 | 附录未列 `CameraSoftTrigger` | 真实存在（`pfnCameraSoftTrigger`/`Ex`），PIL 单帧实现要用 | ✅ 补录 |
| 8 | 例程 bin 里的 `MVSDK.dll` | 旧版 .NET 互操作组件（107KB, 2019），**勿用** | ⛔ |

## 6. 契约适配映射

`IMonitorCameraApi` 契约 → MVSDK 实现要点（实现类 `MecaVisionCameraApi`）：

| 契约成员 | MVSDK 实现 | 注意 |
|---|---|---|
| `ConnectState` | `MonitorCameraConnectionState` 映射 | 枚举成功→Connecting，Init 成功→Connected；断联回调 Msg=0→Error/Disconnected，Msg=1→Connected |
| `Connect(ip, port)` | `CameraEnumerateDevice` → 按 SN/IP 匹配（见 OPEN-1）→ `CameraInit(ref devInfo, -1, -1, ref h)` → `CameraSetConnectionStatusCallback` | 枚举结构体**无 IP 字段**，GigE IP 需 init 后 `CameraGigeGetIp` 查询比对 |
| `Disconnect()` | `CameraStop` + `CameraUnInit`（句柄清零） | UnInit 必须调用 |
| `StartAcquisition()` | `CameraSetCallbackFunction`（委托存字段！）+ `CameraPlay` | 回调内 `CameraImageProcess`→RGB→`Mat`→`FrameReceived` |
| `StopAcquisition()` | `CameraPause`/`CameraStop` | 回调继续注册 |
| `CaptureSingleFrame(): Mat` | 连续模式下 `CameraGetImageBuffer`(超时) → `CameraImageProcess` → 转 Mat → `CameraReleaseImageBuffer` | **取后必 Release**；失败返回 null（契约要求） |
| `FrameReceived` 事件 | Live 回调中 `Clone` 独立 Mat 后上行 | 与海康实现同模式 |
| `Dispose()` | `Disconnect()` | 幂等 |

**格式转换**：`CameraSetIspOutFormat` 设为 RGB888 → 回调/取帧后按 `tSdkFrameHead.iWidth/iHeight` 构造 `Mat(w, h, CV_8UC3, buffer)` 再 `Clone` 出独立副本（SDK 缓冲会被复用，禁止直接引用）。

## 7. 线程模型与帧缓存（复用二手文档结论）

二手文档 §7 线程职责表与「一个入口拆两个出口」设计**与本项目现役范式一致**（对照 [[api/LineLaserManager]] ADR-039 的 Manager 业务中枢、[[api/ProfileMatRenderer]] 显示开关）：

| 线程 | 职责 |
|------|------|
| SDK 帧回调线程 | 翻译帧头 → 转 Mat → `FrameReceived` 事件（**只触发不处理**） |
| `MonitorCamManager`/`MonitorCameraWorkflow` | 现役承载：采集→分析→结果（回调等待取图 ADR-005 路径不变） |
| UI Timer 33ms | 轮询最新帧/结果（版本号去重），**不订阅高频事件** |
| 断联回调线程 | Msg=0 → 报警（普通 Alarm 非急停）→ `StatusChanged`；帧冻结兜底用「距上帧超时」检测 |

## 8. 踩坑清单

1. **回调委托必须存类字段**——`CAMERA_SNAP_PROC`/`CAMERA_CONNECTION_STATUS_CALLBACK` 被 GC 回收后回调静默失效。
2. **回调内禁调 `CameraGetImageBuffer`**（死锁）；回调与主动取帧**二选一**。
3. **`CameraGetImageBuffer` 后必须 `CameraReleaseImageBuffer`**，否则预览通道阻塞。
4. **`CameraSnapToBuffer` 内部切换分辨率、速度慢**——实时路径用回调或 GetImageBuffer。
5. **退出必须 `CameraUnInit`**，否则内存错误。
6. **触发模式下取帧超时 -12**——先确认触发模式与触发源。
7. **Win7/8 非管理员报 -13**——app.manifest 申请管理员权限。
8. **AnyCPU 会加载错 DLL**——平台目标显式 x86/x64。
9. **多相机用 `acSn` 序号匹配**，勿用枚举数组下标（插拔顺序不稳定）。
10. **SDK 缓冲禁止长期持有**——`ImageProcess`/`Clone` 出独立副本再上行。
11. **断联属普通 Alarm 非急停**（不影响伺服安全链路）——与台达急停语义区分。

## 9. 落地步骤（✅ 2026-09-08 已执行，静态校验通过；真编译待 VS）

| # | 步骤 | 结果 |
|---|------|------|
| 1 | 备份压缩包 `AdaWeldSystem_backup_*.tar.gz` | ✅ |
| 2 | 拷入 `MonitorCam/MecaVisionCam/Native/MVSDK.cs`（官方原样不改） | ✅ |
| 3 | 建抽象层 `MonitorCam/IMonitorCam/`（3 文件迁入 + 改名 `IMonitorCamApi`） | ✅ |
| 4 | `MonitorCam/MecaVisionCam/MecaVisionCam.cs` 实现 `IMonitorCamApi`（Live=`SetCallbackFunction`+`Play`；PIL=`GetImageBuffer`+`ImageProcess`+`Release`；断联回调→Alarm） | ✅ |
| 5 | `MonitorCamManager` → `MonitorCamManager` 改名承接，构造切麦格威；消费方（`MonitorCameraWorkflow` ~15 处 + `MonitorCamPage` + `FormMain`）批量改写 | ✅ |
| 6 | 删除 `Api/HikvisionCameraApi.cs` + csproj 移除海康引用；DLL 部署 `3rdDepend/MecaVision/`（x64） | ✅ |
| 7 | Python 静态校验 14/14 通过（旧符号零残留 / 委托持引用 / Dispose 规约） | ✅ |
| 8 | 三扫描全绿 + log 回灌 + drift REMOVED 登记 | ✅ |

**真编译待 Visual Studio** 为已知遗留项。

## 10. OPEN 清单

| # | 阻塞项 | 候选方案 |
|---|--------|---------|
| 1 | **GigE IP 匹配**：`tSdkCameraDevInfo` 无 IP 字段，无法在枚举期按 IP 选机 | ① init 后 `CameraGigeGetIp` 比对、不符则 UnInit 换下一台；② 改用 SN 配置匹配（推荐，插拔稳定） |
| 2 | **平台目标**：现工程 x86 还是 x64 需核对（决定部署哪套 DLL） | 打开 csproj `PlatformTarget` 确认 |
| 3 | **相机连接形态**：监控相机是 USB3 还是 GigE（影响驱动与部署） | 现场确认 |
| 4 | **PixelMmScale 标定**：算法侧 px→mm 系数随相机分辨率/视场变化 | 标定板实标；与 [[api/AlgorithmManager]] 参数联动 |
| 5 | 管理员权限 manifest 是否需要（Win10 通常免） | 实测 -13 是否出现 |

## 相关页面

- [[api/MecaVisionMVSDK-Native]] —— 原生 API 速查（核验过的签名与错误码）
- [[decisions/ADR-037-MecaVisionMonitorCamera]] —— 架构决策
- [[modules/MonitorCam]] / [[api/MonitorCamManager]] / [[decisions/ADR-007-MonitorCameraModule]] —— 现役模块
- [[guides/Project-Tools]] —— 原生 DLL 部署心智（海康同款问题）
