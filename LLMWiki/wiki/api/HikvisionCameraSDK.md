---
title: 海康威视工业相机 SDK（MvCameraControl.Net）使用手册
date: 2026-07-14
tags: [API, 相机, 海康, MVS, 面阵相机, 二次开发]
source: C:\Program Files (x86)\MVS\Development\Documentations\工业相机Windows SDK开发指南V4.4.1（.NET）.chm；Samples\C#\MvCameraControlNet\（MVCameraSDK\Source\MVCamera.cs、BasicDemo\BasicDemo.cs）
---

# 海康威视工业相机 SDK（MvCameraControl.Net）使用手册

> 面向 AdaWeldSystem / MonitorCam 模块的面阵工业相机二次开发知识。基于本机 MVS 安装（C:\Program Files (x86)\MVS）的 .NET 示例与开发指南整理。
> 本项目已在 `AdaWeldSystem/MonitorCam/Api/HikvisionCameraApi.cs` 中按本手册实现 `IMonitorCameraApi`。

## 1. 程序集与命名空间

| 项 | 值 |
|----|----|
| 托管封装 DLL | `MvCameraControl.Net.dll`（命名空间 `MvCamCtrl.NET`） |
| 封装类 | `MyCamera`（实例方法）+ 大量 `public static` 设备枚举/全局方法 |
| 原生核心 DLL | `MvCameraControl.dll`（C 导出，由托管 DLL P/Invoke） |
| 两种引入方式 | ① 引用 `MvCameraControl.Net.dll`；② 直接把 `MVCamera.cs` 源码加入工程 |
| 本工程选择 | ① 引用 DLL；`MvCameraControl.Net.dll` 已复制到 `AdaWeldSystem/Libs/MvCameraControl/` 并注册到 .csproj（CopyLocal=true） |

> ⚠️ 原生 `MvCameraControl.dll` **不在 Development 示例包内**，由完整 MVS 运行时提供。详见 [[guides/Project-Tools]]。

## 2. 初始化与设备枚举

```csharp
using MvCamCtrl.NET;

// 枚举在线设备（GigE + USB3）。nTLayerType 标志位可 OR 组合。
MV_CC_DEVICE_INFO_LIST devList = new MV_CC_DEVICE_INFO_LIST();
int nRet = MyCamera.MV_CC_EnumDevices_NET(
    MyCamera.MV_GIGE_DEVICE | MyCamera.MV_USB_DEVICE, ref devList);
if (nRet != MyCamera.MV_OK || devList.nDeviceNum == 0) { /* 无设备 */ }

// 遍历：pDeviceInfo 是 IntPtr[]（长度 MV_MAX_DEVICE_NUM），需 Marshal 到结构体
for (int i = 0; i < devList.nDeviceNum; i++)
{
    MV_CC_DEVICE_INFO dev = (MV_CC_DEVICE_INFO)Marshal.PtrToStructure(
        devList.pDeviceInfo[i], typeof(MV_CC_DEVICE_INFO));
    // dev.nTLayerType == MV_GIGE_DEVICE / MV_USB_DEVICE
}
```

- 设备类型常量（位于 `MyCamera` 类，`Int32`）：`MV_GIGE_DEVICE = 0x1`、`MV_USB_DEVICE = 0x4`、`MV_GENTL_GIGE_DEVICE = 0x40`。
- 成功码：`public const Int32 MV_OK = 0`。所有 API 返回 `0` 即成功，非 `0` 为错误码（详见第 8 节）。

## 3. 按 IP 查找 GigE 设备并连接

`IMonitorCameraApi.Connect(ip, port)` 的核心实现：枚举 → 匹配 GigE `nCurrentIp` → `CreateDevice` → `OpenDevice`。

```csharp
// 在 GigE 设备信息中取当前 IP（nCurrentIp 为 UInt32，大端：最高字节为第一段）
MV_GIGE_DEVICE_INFO_EX gige = (MV_GIGE_DEVICE_INFO_EX)MyCamera.ByteToStruct(
    dev.SpecialInfo.stGigEInfo, typeof(MV_GIGE_DEVICE_INFO_EX));
uint n = gige.nCurrentIp;
byte[] b = BitConverter.GetBytes(n);
string ip = string.Format("{0}.{1}.{2}.{3}", b[3], b[2], b[1], b[0]); // 大端解析

// 找到匹配设备后创建并打开
MyCamera cam = new MyCamera();
nRet = cam.MV_CC_CreateDevice_NET(ref matchedDev);
if (nRet != MyCamera.MV_OK) { /* 失败 */ }
nRet = cam.MV_CC_OpenDevice_NET();
if (nRet != MyCamera.MV_OK) { cam.MV_CC_DestroyDevice_NET(); /* 失败 */ }

// GigE 必须探测最优包大小（仅 GigE 有效），否则易丢包
if (matchedDev.nTLayerType == MyCamera.MV_GIGE_DEVICE)
{
    int pkt = cam.MV_CC_GetOptimalPacketSize_NET();
    if (pkt > 0) cam.MV_CC_SetIntValueEx_NET("GevSCPSPacketSize", pkt);
}
```

- `MV_CC_DEVICE_INFO.SpecialInfo` 是 `[StructLayout(Explicit, Size=540)]` 的联合（`stGigEInfo`/`stUsb3VInfo`/`stCMLInfo` 等重叠）。取 GigE 信息用 `stGigEInfo`（Byte[216]）+ `ByteToStruct(..., typeof(MV_GIGE_DEVICE_INFO_EX))`。
- `MV_GIGE_DEVICE_INFO_EX` 关键字段：`nCurrentIp`（UInt32）、`nCurrentSubNetMask`、`chSerialNumber`、`chUserDefinedName`、`chModelName`。
- USB3 设备无 IP（`nTLayerType == MV_USB_DEVICE`），按序列号/用户自定义名匹配；本工程 `Connect(ip,port)` 对 USB 设备退化为“取第一台”。

## 4. Live 模式（连续采集 + 帧回调）

参考 BasicDemo 的 `bnStartGrab` 流程：先设采集模式，再 `StartGrabbing` + 注册回调。

```csharp
// 连续采集、关闭触发（监控为自由流）
cam.MV_CC_SetEnumValue_NET("AcquisitionMode",
    (uint)MyCamera.MV_CAM_ACQUISITION_MODE.MV_ACQ_MODE_CONTINUOUS);
cam.MV_CC_SetEnumValue_NET("TriggerMode",
    (uint)MyCamera.MV_CAM_TRIGGER_MODE.MV_TRIGGER_MODE_OFF);

// 注册图像回调（注意：委托实例必须被持有，否则被 GC 回收导致回调失效）
cbOutputExdelegate cb = new cbOutputExdelegate(OnImageCallback);
cam.MV_CC_RegisterImageCallBackEx_NET(cb, IntPtr.Zero);
cam.MV_CC_StartGrabbing_NET();

// 回调签名（SDK 头文件 line 54）
// public delegate void cbOutputExdelegate(IntPtr pData, ref MV_FRAME_OUT_INFO_EX pFrameInfo, IntPtr pUser);
void OnImageCallback(IntPtr pData, ref MV_FRAME_OUT_INFO_EX info, IntPtr pUser)
{
    // pData 为本帧像素数据，info 含 nWidth/nHeight/enPixelType/时间戳等
}

// 停止：先 StopGrabbing，再注销回调（传 null 注销）
cam.MV_CC_StopGrabbing_NET();
cam.MV_CC_RegisterImageCallBackEx_NET(null, IntPtr.Zero);
```

- `cbOutputExdelegate` 是 SDK 定义的委托；**必须用字段/变量长期持有**，不能写匿名内联临时变量（会被 GC）。
- 取流策略：`MV_CC_SetGrabStrategy_NET(MV_GRAB_STRATEGY)`，默认 `MV_GrabStrategy_OneByOne`（逐帧）；监控可用 `MV_GrabStrategy_LatestImagesOnly` 仅留最新帧。

## 5. 单帧采集（PIL 模式）

推荐用 `MV_CC_GetImageBuffer_NET` + `MV_CC_FreeImageBuffer_NET`（SDK 负责内存管理）：

```csharp
MV_FRAME_OUT frameOut = new MV_FRAME_OUT();
int nRet = cam.MV_CC_GetImageBuffer_NET(ref frameOut, 1000); // 超时 1000ms
if (nRet == MyCamera.MV_OK && frameOut.pBufAddr != IntPtr.Zero)
{
    // frameOut.pBufAddr = 像素数据指针；frameOut.stFrameInfo = MV_FRAME_OUT_INFO_EX
    // frameOut.stFrameInfo.enPixelType / nWidth / nHeight
    cam.MV_CC_FreeImageBuffer_NET(ref frameOut); // 必须释放
}

// 备选：MV_CC_GetOneFrameTimeout_NET(IntPtr pData, UInt32 nDataSize, ref MV_FRAME_OUT_INFO_EX, Int32 nMsec)
// 需调用方预先分配 nDataSize 字节的非托管缓冲区（Mono8 = w*h；RGB8 = w*h*3）。
```

- 单帧前必须先 `StartGrabbing`（可临时开启、取完即停，避免与 Live 冲突）。
- `MV_FRAME_OUT` 结构：`public IntPtr pBufAddr; public MV_FRAME_OUT_INFO_EX stFrameInfo;`。

## 6. 像素格式 → Emgu Mat 转换

`MV_FRAME_OUT_INFO_EX.enPixelType` 类型为 `MvGvspPixelType`（枚举，line 7887）。常用值：

| 像素格式 | 枚举值 | Emgu 映射 |
|----------|--------|-----------|
| 单色 8bit | `PixelType_Gvsp_Mono8 = 0x01080001` | `new Mat(h, w, DepthType.Cv8U, 1, pData, w)` |
| RGB 8bit 打包 | `PixelType_Gvsp_RGB8_Packed = 0x02180014` | `new Mat(h, w, DepthType.Cv8U, 3, pData, w*3)`（注意通道顺序） |
| BGR 8bit 打包 | `PixelType_Gvsp_BGR8_Packed = 0x02180015` | `new Mat(h, w, DepthType.Cv8U, 3, pData, w*3)` |

```csharp
// 关键：pData 指向 SDK 内部缓冲，回调返回/FreeImageBuffer 后可能被回收，
// 必须 Clone 出独立 Mat 再使用/跨线程传递。
Mat mat = new Mat(h, w, DepthType.Cv8U, channels, pData, step);
Mat safeCopy = mat.Clone();
mat.Dispose();
```

- Bayer（RGGB/GRBG 等）格式需先 `MV_CC_ConvertPixelTypeEx_NET` 转成 Mono/RGB 再处理。
- Emgu 默认 3 通道按 **BGR** 解释；`RGB8_Packed` 直接当 3 通道会通道顺序相反（监控灰度场景无影响，彩色场景需转码）。

## 7. 常用参数设置

```csharp
// 枚举型（Key 字符串，值用 MV_CAM_* 枚举）
cam.MV_CC_SetEnumValue_NET("TriggerMode", (uint)MyCamera.MV_CAM_TRIGGER_MODE.MV_TRIGGER_MODE_OFF);
cam.MV_CC_SetEnumValue_NET("AcquisitionMode", (uint)MyCamera.MV_CAM_ACQUISITION_MODE.MV_ACQ_MODE_CONTINUOUS);
cam.MV_CC_SetEnumValueByString_NET("TriggerMode", "Off"); // 也可用字符串

// 整型 / 浮点 / Bool
cam.MV_CC_SetIntValueEx_NET("GevSCPSPacketSize", pkt);     // GigE 包大小
cam.MV_CC_SetFloatValue_NET("ExposureTime", 10000.0f);     // 曝光（us）
cam.MV_CC_SetFloatValue_NET("Gain", 0.0f);                 // 增益
cam.MV_CC_SetBoolValue_NET("AcquisitionFrameRateEnable", true);

// 读取
MVCC_FLOATVALUE fv = new MVCC_FLOATVALUE();
cam.MV_CC_GetFloatValue_NET("ExposureTime", ref fv); // fv.fCur 为当前值
```

- 参数 Key 名遵循 GenICam 标准（`ExposureTime`、`Gain`、`TriggerMode`、`AcquisitionMode`、`GevSCPSPacketSize` 等）。
- 连续模式 + 触发关闭是监控场景的默认配置。

## 8. 错误码与排查

- 所有 API 返回 `Int32`，`== MV_OK(0)` 成功。非 0 为错误（如 `MV_E_HANDLE`、`MV_E_NETER` 等，详见 .NET 开发指南错误码附录）。
- 连接失败常见原因：IP 不在同一子网、防火墙拦截 GigE 端口、未装 MVS 运行时（原生 DLL 缺失 → P/Invoke 失败）、最优包大小未设导致 GigE 丢包。
- `MV_CC_IsDeviceConnected_NET()` 可在采集中检测掉线；`MV_CC_RegisterExceptionCallBack_NET(cbExceptiondelegate, IntPtr)` 注册异常回调。

## 9. 本工程落地（MonitorCam）

- 实现类：`AdaWeldSystem/MonitorCam/Api/HikvisionCameraApi.cs`（实现 `IMonitorCameraApi`，是 `MonitorCameraRun` 当前唯一底层实现）。
- `MonitorCameraRun` 构造函数直接实例化 `HikvisionCameraApi`；UI/Workflow 代码无需改动（契约一致）。
- 历史说明：早期曾以 `MonitorCameraSimulator` 占位生成合成帧用于离线联调，SDK 确定后已删除整个模拟部分，仅保留真实相机实现。
- 模块文档见 [[modules/MonitorCam]]；原生运行时陷阱见 [[guides/Project-Tools]]。
