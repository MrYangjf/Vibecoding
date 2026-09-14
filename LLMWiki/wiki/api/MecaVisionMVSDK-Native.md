---
title: MecaVision MVSDK 原生 API 速查
date: 2026-09-08
tags: [API, 相机, 监控相机, MecaVision, MVSDK, 麦格威]
source: raw/mecavision/（SDK 原文核验抽取，2026-09-08）
---

# MecaVision MVSDK 原生 API 速查

> **真相源**：`raw/mecavision/MecaVision_SDK…/MecaVision/Demo/C#/MVSDK/MVSDK.cs`（官方 C# 封装，**6885 行**，唯一类 = 静态类 `MvApi`）。
> **C 原生声明基线（2026-09-14 新增）**：`raw/mecavision/MecaVision_SDK…/MecaVision/SDK/Include/` —— `CameraApi.h`（`extern "C"` 全部 API，328 KB）/ `CameraApiLoad.h` / `CameraDefine.H`（枚举·结构体）/ `CameraStatus.h`（错误码）/ `RawDecodeApi.h` / `mvocx.h`。本页的枚举、结构体与错误码可回溯该处核对——**`MVSDK.cs` 是 C# 镜像，头文件才是 C 原文**（原藏于 `Demo/VC++/Include/`，VC++ 示例裁剪时抽存）。
> 本页全部 API 名与签名由脚本从该文件抽取核验（2026-09-08），**与厂商原文逐字一致**。
> 落地架构约束见 [[decisions/ADR-037-MecaVisionMonitorCamera]]；开发指导见 [[guides/MecaVision-DevGuide]]；模块上下文见 [[modules/MonitorCam]]。

## 章节导航

- [加载机制（动态加载，无 DllImport）](#加载机制动态加载无-dllimport)
- [原生 DLL 资产](#原生-dll-资产)
- [初始化与生命周期](#初始化与生命周期)
- [采集与帧获取](#采集与帧获取)
- [图像处理与保存](#图像处理与保存)
- [参数设置](#参数设置)
- [触发与闪光灯](#触发与闪光灯)
- [回调委托](#回调委托)
- [核心结构体](#核心结构体)
- [错误码（CameraSdkStatus）](#错误码camerasdkstatus)
- [核验配方](#核验配方)

## 加载机制（动态加载，无 DllImport）

`MvApi` 静态构造函数按进程位数动态加载，**业务代码不写任何 DllImport**：

```csharp
static MvApi()
{
    IntPtr hSdkDll;
    bool b64Bit = (IntPtr.Size == 8);
    if (b64Bit) hSdkDll = LoadLibrary("MVCAMSDK_X64.dll");
    else        hSdkDll = LoadLibrary("MVCAMSDK.dll");
    // GetProcAddress + Marshal.GetDelegateForFunctionPointer 绑定全部 pfnXxx 委托
}
```

- 共 **336 个 `pfn*` 函数指针委托**（`public delegate`）+ **27 个结构体** + **19 个枚举**。
- 平台目标必须显式 x86 或 x64（`IntPtr.Size` 决定加载哪个 DLL），AnyCPU 会加载错位。

## 原生 DLL 资产

| 文件 | 位数 | 位置（SDK 包内） | 部署要求 |
|------|------|-----------------|---------|
| `MVCAMSDK.dll` | x86 | `SDK/` | 与 exe 同目录 |
| `MVCAMSDK_X64.dll` | x64 | `SDK/X64/` | 与 exe 同目录 |
| `MVImageProcess.dll` / `MVImageProcess_X64.DLL` | 对应位数 | `SDK/`、`SDK/X64/` | 与 exe 同目录 |
| `GiGeCamera*.Interface` / `Usb3Camera0*.Interface` | 对应位数 | `SDK/`、`SDK/X64/` | GigE/USB3 协议插件 |

> ⚠️ 例程 `bin/Release/MVSDK.dll`（107KB, 2019）是**旧版 .NET 互操作组件**，勿与本项目混用。正确方式 = `MVSDK.cs` 源文件拷入项目 + 部署上表原生 DLL。

## 初始化与生命周期

| API（MvApi. 前缀省略） | 签名要点 | 说明 |
|---|---|---|
| `CameraSdkInit` | `(int iLanguageSel)` | **必须最先调用**（1=中文） |
| `CameraSdkGetVersionString` | `()` | 版本字符串 |
| `CameraSetSysOption` | `(string name, string value)` | 系统选项，如 `("NumBuffers","3")` |
| `CameraEnumerateDevice` | `(ref tSdkCameraDevInfo, ref int)` | 枚举设备（C# 封装另有多相机重载） |
| `CameraInit` | `(ref tSdkCameraDevInfo, int mode, int team, ref IntPtr hCamera)` | 打开相机；mode/team 传 -1 |
| `CameraInitEx` / `CameraInitEx2` | 按索引/名字打开 | 多相机便捷入口 |
| `CameraIsOpened` | `(ref tSdkCameraDevInfo)` | 是否已打开 |
| `CameraUnInit` | `(IntPtr hCamera)` | **退出前必须调用**，否则内存错误 |
| `CameraSetConnectionStatusCallback` | `(IntPtr hCamera, CAMERA_CONNECTION_STATUS_CALLBACK, IntPtr pContext)` | 断联/恢复回调（SDK 自带，无需心跳） |
| `CameraGetErrorString` | `(int errorCode)` | 错误码 → 描述文本 |
| `CameraShowSettingPage` / `CameraCreateSettingPage` | `(IntPtr hCamera, ...)` | 官方参数设置页（调试用） |

## 采集与帧获取

| API | 签名要点 | 说明 |
|---|---|---|
| `CameraSetCallbackFunction` | `(IntPtr hCamera, CAMERA_SNAP_PROC pCallBack, IntPtr pContext, ref IntPtr pOldCallBack)` | 注册帧回调（**与 CameraGetImageBuffer 二选一，混用死锁**） |
| `CameraSetFrameEventCallback` | `(IntPtr hCamera, CAMERA_FRAME_EVENT_CALLBACK, IntPtr)` | 事件型帧回调 |
| `CameraPlay` / `CameraPause` / `CameraStop` | `(IntPtr hCamera)` | 采集启停 |
| `CameraSoftTrigger` / `CameraSoftTriggerEx` | `(IntPtr hCamera)` | 软触发一帧 |
| `CameraGetImageBuffer` | `(IntPtr hCamera, ref tSdkFrameHead, ref IntPtr, uint dwTimeoutMs)` | 主动取原始帧（**必须 Release**） |
| `CameraGetImageBufferEx` | 直接返回缓冲指针 | 变体 |
| `CameraSnapToBuffer` | `(IntPtr hCamera, ...)` | 抓帧（内部切换分辨率，**慢**） |
| `CameraReleaseImageBuffer` | `(IntPtr hCamera, IntPtr)` | 释放取帧缓冲（**不释放会阻塞预览通道**） |
| `CameraGetFrameStatistic` | `(IntPtr hCamera, ref tSdkFrameStatistic)` | 帧统计（丢帧/总帧） |
| `CameraGetCapability` | `(IntPtr hCamera, ref tSdkCameraCapbility)` | 能力描述（曝光/分辨率范围、IO 数、媒体格式） |
| `CameraGetIOState` / `CameraSetIOState` | `(IntPtr hCamera, int, bool)` | 相机 IO 读写 |
| `CameraGetInPutIOMode` / `CameraSetInPutIOMode` / `CameraGetOutPutIOMode` / `CameraSetOutPutIOMode` | `(IntPtr hCamera, int, ...)` | IO 方向模式 |

## 图像处理与保存

| API | 签名要点 | 说明 |
|---|---|---|
| `CameraImageProcess` | `(IntPtr hCamera, IntPtr pbyIn, IntPtr pbyOut, ref tSdkFrameHead)` | Bayer/YUV → 目标格式（RGB888 等） |
| `CameraImageProcessEx` | 带 ISP 参数版本 | 变体 |
| `CameraSetIspOutFormat` | `(IntPtr hCamera, uint format)` | 设置 ISP 输出格式（emImageFormat） |
| `CameraSaveImage` | `(IntPtr hCamera, string path, ref tSdkFrameHead, IntPtr pbyBuffer, uint format, int quality)` | 存图（BMP/JPG/PNG/RAW） |
| `CameraSaveImageEx` | 扩展版 | 变体 |
| `CameraSetMediaType` / `CameraGetMediaType` | `(IntPtr hCamera, uint)` | 媒体格式选择 |
| `CameraImage_*` 系列 | `CameraImage_Create / Draw / SaveAsBmp / SaveAsJpeg / SaveAsPng / SaveAsRaw / Destroy` | CameraImage 对象操作（FirstStep 例程路径） |
| `CameraGrabber_*` 系列 | `CameraGrabber_Create / CreateByIndex / CreateByName / SetRGBCallback / StartLive / StopLive / SaveImage / GetStat / Destroy` | 高层抓取器（FirstStep 例程推荐路径，**内部自带显示与 ISP**） |

## 参数设置

| API | 单位/说明 |
|---|---|
| `CameraSetExposureTime` / `CameraGetExposureTime` | **微秒 us**；范围查 `CameraGetExposureTimeRange` / `tSdkCameraCapbility.sExposeDesc` |
| `CameraSetAnalogGain` / `CameraGetAnalogGain` | 模拟增益；另有 `CameraSetAnalogGainX`（扩展） |
| `CameraSetFrameRate` / `CameraGetFrameRate` | fps |
| `CameraSetImageResolution` / `CameraGetImageResolution` | `ref tSdkImageResolution`；范围查 `sResolutionRange` |
| `CameraSetMirror` / `CameraGetMirror` | `(hCamera, int iDir, bool bEnable)`，方向 emSdkMirrorDirection |
| `CameraSetTriggerMode` / `CameraGetTriggerMode` | `(hCamera, int mode)`：0=连续 1=软触发 2=硬触发 |
| `CameraSetWhiteLevel` / `CameraSetGamma` / `CameraSetSaturation` / `CameraSetContrast` / `CameraSetSharpness` | ISP 图像参数 |
| `CameraSetParameterMode` / `CameraGetCurrentParameterGroup` | 参数组 |
| `CameraSaveParameterToFile` / `CameraLoadParameter` | 参数存/读文件（**推荐：免自研参数 UI**） |
| `CameraSetAutoConnect` / `CameraReConnect` / `CameraGetReConnectCounts` | 自动重连 |

## 触发与闪光灯

| API | 说明 |
|---|---|
| `CameraGetExtTrigCapability` | 外触发能力位（TriggerAndStrobe 例程先查此项） |
| `CameraSetExtTrigSignalType` | `ref tSdkTrigger`：外触发信号类型（下降沿/上升沿/高电平/低电平） |
| `CameraSetExtTrigDelayTime` / `CameraSetExtTrigIntervalTime` / `CameraSetExtTrigJitterTime` / `CameraSetExtTrigBufferedDelayTime` | 外触发时序 |
| `CameraSetExtTrigShutterType` | 外触发快门模式（emExtTrigShutterMode） |
| `CameraSetStrobeMode` / `CameraSetStrobeDelayTime` / `CameraSetStrobePolarity` / `CameraSetStrobePulseWidth` | 闪光灯（硬触发打光） |
| `CameraSetTriggerCount` | 软触发帧数 |
| `CameraSetTriggerDelayTime` | 触发延时 |

## 回调委托

| 委托 | 用途 | 关键约定 |
|---|---|---|
| `CAMERA_SNAP_PROC` | 帧回调 | `(IntPtr hCamera, IntPtr pFrameBuffer, ref tSdkFrameHead pFrameHead, IntPtr pContext)`；**回调内禁调 CameraGetImageBuffer（死锁）**；委托引用必须存字段防 GC |
| `CAMERA_CONNECTION_STATUS_CALLBACK` | 断联回调 | `(IntPtr hCamera, uint Msg, uint Param, IntPtr pContext)`；Msg 0=断开 1=恢复；GigE 恢复时 Param 0=网络失败 1=相机掉电 |
| `CAMERA_FRAME_EVENT_CALLBACK` | 事件帧回调 | 变体路径 |
| `CAMERA_SNAP_PROC` 上下文 | `pContext` | 原样回传 IntPtr，可传 GCHandle |

## 核心结构体

```csharp
tSdkCameraDevInfo {          // 枚举结果
    byte[] acProductSeries/acProductName/acFriendlyName/acDriverVersion;  // 各 32 字节
    byte[] acSensorType/acPortType/acSn;                                  // 32 字节
    uint uInstance;            // 同型号多相机实例索引
}

tSdkFrameHead {              // 帧头（回调/取帧都带）
    uint uiMediaType;          // emImageFormat
    uint uBytes;               // 数据字节数
    int  iWidth, iHeight;
    uint bIsTrigger;
    uint uiTimeStamp;          // 0.1ms
    uint uiExpTime;            // us
    float fAnalogGain;         // dB
    // 另有伽马/对比度/饱和度/RGB 增益等
}

tSdkCameraCapbility {        // 能力描述（注意官方拼写就是 Capbility）
    int iOutputIoCounts, iInputIoCounts;
    tSdkExpose sExposeDesc;              // 曝光范围
    tSdkResolutionRange sResolutionRange;
    tRgbGainRange sRgbGainRange;
    tSdkMediaType sMediaType;            // 支持的输出格式
    // 触发/帧速描述等
}
```

## 错误码（CameraSdkStatus）

> 全部枚举值已从 MVSDK.cs 原文核验（2026-09-08）。0 = 成功，负数 = 失败。

| 常量 | 值 | 含义 |
|------|-----|------|
| CAMERA_STATUS_SUCCESS | 0 | 成功 |
| CAMERA_STATUS_FAILED | -1 | 通用失败 |
| CAMERA_STATUS_NOT_INITIALIZED | -5 | 未初始化（未调 CameraSdkInit） |
| CAMERA_STATUS_PARAMETER_INVALID | -6 | 参数无效 |
| CAMERA_STATUS_TIME_OUT | -12 | 超时（触发模式下未触发会一直超时） |
| CAMERA_STATUS_IO_ERROR | -13 | 硬件 IO 错误（Win7/8 非管理员访问注册表会报此码） |
| CAMERA_STATUS_COMM_ERROR | -14 | 通讯错误 |
| CAMERA_STATUS_NO_DEVICE_FOUND | -16 | 没找到设备 |
| CAMERA_STATUS_DEVICE_IS_OPENED | -18 | 设备已打开 |
| CAMERA_STATUS_GRAB_FAILED | -25 | 抓图失败 |
| CAMERA_STATUS_LOST_DATA | -26 | 丢数据（带宽不足） |
| CAMERA_STATUS_BUSY | -28 | 忙 |
| CAMERA_STATUS_DEVICE_LOST | -38 | 设备丢失（触发断联回调） |

## 核验配方

SDK 升级后重跑以下脚本核对 API 名（本页生成方法，完整脚本曾存 `tools/_tmp_mecavision_verify.py`，用后即删）：

```python
import io, re
t = io.open(MVSDK_CS_PATH, encoding="utf-8-sig", errors="replace").read()
delegates = set(re.findall(r"public\s+delegate\s+[\w\*\[\]\.]+\s+(\w+)\s*\(", t))
structs = set(re.findall(r"public\s+struct\s+(\w+)", t))
# 比对：文档声称 API 名 in delegates（pfn 前缀）；错误码枚举值逐个 re 搜索
```

## 相关页面

- [[guides/MecaVision-DevGuide]] —— 开发指导（落地步骤/映射表/踩坑）
- [[decisions/ADR-037-MecaVisionMonitorCamera]] —— 监控相机切换麦格威架构决策
- [[modules/MonitorCam]] —— 监控相机模块现状
- [[api/MonitorCamManager]] —— 现役运行控制（本 API 的唯一消费入口）
