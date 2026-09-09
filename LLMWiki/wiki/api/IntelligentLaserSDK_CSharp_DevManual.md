# IntelligentLaser SDK（C# 版）开发手册

> 来源：`M3/IntelligentLaserSDK_1.5.827.15028_C#`（唐山英莱 / ANLE 线激光传感器）
> 版本：`IntelligentLaserSDK_1.5.827.15028_C#`（C++ 核心 `IntelligentLaser.dll` 为 `V1.5.827`，头文件标注 `V1.2.664`）
> 适用平台：原厂提供 **C# 托管包装 `IntelligentLaser_CSharp.dll`**（CppSharp 生成），含 `.Net Framework`（用于 .NET 4.8 项目）与 `.Net6 及以上` 两个构建。
> 编写依据：包装源码 `IntelligentLaser_CSharp/IntelligentLaser.cs` + 官方 `.NET Framework 4.8` 示例 `IntelligentLaser_CSharp_Demo/IntelligentLaser_CSharp_NetFramework_Demo/Form1.cs`。

---

## 0. 概述与部署（必读）

SDK 由 **原生核心 DLL + C# 托管包装** 两部分组成，C# 侧只需引用包装 DLL，无需手写 P/Invoke。

| 组件 | 说明 |
|------|------|
| `IntelligentLaser_CSharp.dll` | C# 托管包装（CppSharp 生成）。**你的项目是 .NET Framework 4.8，必须选 `IntelligentLaser_CSharp及其依赖文件/IntelligentLaser_CSharp(选择对应版本)/.Net Framework/` 下的版本**，不要选 `.Net6及以上`。** |
| `IntelligentLaser.dll` | 原生核心（MSVC Win64，**64 位**）。由包装内部 `DllImport("IntelligentLaser", ...)` 加载。 |
| `CppSharp.Runtime.dll` | 包装依赖的运行库，**必须随包装 DLL 一起部署**。 |
| `avcodec-58 / avdevice-58 / avfilter-7 / avformat-58 / avutil-56 / swresample-3 / swscale-5 / SDL2.dll / jsoncpp.dll` | `IntelligentLaser.dll` 自身的 FFmpeg / SDL / jsoncpp 依赖，**必须全部拷贝到程序运行目录（或 PATH）**。 |

- **命名空间**：`IntelligentLaser_CSharp`（包装类统一在此命名空间）。
- **核心静态类**：`IntelligentLaser_export` —— 所有 `Init/Connect/SetXxx/FetchXxx/RegisterCallBack` 方法都是它的 `public static` 方法。
- **平台硬性要求**：原生 DLL 为 **x64**，托管进程必须 64 位。
  - ⚠️ 原生 DLL 为 **x64**，托管进程必须 64 位：早期 `AdaWeldSystem.csproj` 的 `Release|AnyCPU` 为 `AnyCPU`（.NET Framework 默认 Prefer32Bit=true → 进程 32 位 → 加载 64 位 DLL 抛 `BadImageFormatException`）。**集成（2026-07-24，参见 [[api/IntelligentLaserCam]] 构建与部署）已把 `Release|AnyCPU` 的 `PlatformTarget` 改为 `x64`**（Debug 早已是 x64），故 64 位原生 DLL 可正常加载。
- **所有包装对象均实现 `IDisposable`**（如 `IntelligentYUV` / `IntelligentMillionOutlineInspect` / `TIntelligentJobParam` …）。从回调拿到的实例，**[必须]** 在提取完数据后调用 `.Dispose()`，否则原生内存泄漏。
- **回调跑在 SDK 原生线程上**，访问 WinForms 控件必须 `BeginInvoke/Invoke` 切回 UI 线程（呼应项目 [[guides/WinForms-UI-Threading]]）。

---

## 1. 初始化（InitSDK → 发现 → 连接 → 启停）

### 1.1 初始化与反初始化
```csharp
using IntelligentLaser_CSharp;

// 程序启动时（如 Form.Load）最先调用，返回 0 表示成功
int initRet = IntelligentLaser_export.InitSDK();   // 参数: string strAppDir=".", uint dwInstanceId=1
if (initRet != 0) { /* 失败处理 */ }

// 程序退出时（如 Form.FormClosing）最后调用
IntelligentLaser_export.UnInitSDK();
```

### 1.2 设备发现
```csharp
// 1) 扫描（未连接下位机时先扫描）
IntelligentLaser_export.DetectAllSensor();

// 2) 取结果：注意数组个数必须与传入的 count 一致
IntelligentSensorMsg[] devices = new IntelligentSensorMsg[10];   // 数量可按需调整
StringBuilder netCard = new StringBuilder(32);
int count = devices.Length;
IntelligentLaser_export.FetchAllSensorInfo2(netCard, devices, ref count);
for (int i = 0; i < count; i++)
{
    string ip = ByteArrayToString(devices[i].SzIP, Encoding.ASCII); // SzIP 为 byte[32]
    // 加入下拉框供选择
}
```
> `IntelligentSensorMsg` 字段：`dwCameraNum`、`szIP[32]`、`szSoftWareVer[32]`、`szHardWareVer[32]`、`szProtocolVer[32]`、`szSN[32]`、`szSensorType[32]`（均为定长 `byte[]`，用 `Encoding.ASCII.GetString(...).TrimEnd('\0')` 转字符串）。

### 1.3 连接与断开
```csharp
// 连接（传入设备 IP 字符串）
int ret = IntelligentLaser_export.ConnectToSensor(ipString);

// 返回值 ret 是「位掩码」，按位判断各服务是否连上（某位 == 0 表示该服务成功）
// 枚举 EmIntelligentConnectStatus:
//   EM_INTELLIGENT_CONNECT_E_MASK    = 1
//   EM_INTELLIGENT_CONNECT_E_CORE    = 2
//   EM_INTELLIGENT_CONNECT_E_LOGS    = 4
//   EM_INTELLIGENT_CONNECT_E_CAPTURE = 8
//   EM_INTELLIGENT_CONNECT_E_MONITOR = 16
//   EM_INTELLIGENT_CONNECT_E_FILES   = 32
if ((ret & (int)EmIntelligentConnectStatus.EM_INTELLIGENT_CONNECT_E_CORE) == 0)
    /* Core 服务连上 */;

// 断开
IntelligentLaser_export.DisConnSensor();
```
> 示例里用 `Timer`（1s 间隔）轮询状态；你的项目已有 `CameraSelector.DetectConnection` 体系，建议把连接结果映射到 `ConnectionState`，而非另起轮询。

### 1.4 传感器 / 激光 / 相机 启停
```csharp
IntelligentLaser_export.SetSensorEnable(true);            // 传感器（采集）开关
IntelligentLaser_export.SetLaserEnable(true);             // 激光开关
IntelligentLaser_export.SetSensorCaptureCameraEnable(true);  // 采集相机（YUV 预览）开关
IntelligentLaser_export.SetSensorMonitorCameraEnable(true);  // 监控相机（YUV 预览）开关
```
### 1.5 状态轮询
```csharp
IntelligentSensorInfo info = new IntelligentSensorInfo();
if (IntelligentLaser_export.FetchSensorInfo(info) == 0)
{
    // info.StCtrl.DwCameraEnable : 0=关 1=开
    // info.DwCaptureCameraEnable / info.DwMonitorCameraEnable
}
uint laser = 0;
if (IntelligentLaser_export.FetchLaserStatus(ref laser) == 0) { /* 0=关 1=开 */ }
```
### 1.6 帧率模式（与 100Hz 目标相关）
```csharp
// 枚举 EmIntelligentFpsModel: STANDERD=1, FAST_SPEED=2, HIGH_SPEED=3, ILLEGAL=16
IntelligentLaser_export.SetSensorFpsModel(EmIntelligentFpsModel.EM_INTELLIGENT_FPS_MODEL_HIGH_SPEED);
// 读取当前帧率
float fps = 0; IntelligentLaser_export.FetchSensorFps(ref fps);
```

---

## 2. 回调机制（Callback）

所有回调统一通过 `IntelligentLaser_export.IntelligentRegisterCallBack_<X>(委托, IntPtr pUser)` 注册。

### 2.1 关键约定
1. **pUser 传宿主对象**：用 `GCHandle.Alloc(this)` 把窗体（或你的管理器）钉住，传 `GCHandle.ToIntPtr(handle)`；回调里 `GCHandle.FromIntPtr(pUser).Target` 取回。必须 **保存 GCHandle 到字段** 防止 GC，并在退出时 `handle.Free()`。
2. **委托实例必须常驻**：把委托存成字段（如 `IntelligentMillionOutlineInspectCallBack _cb`），不要写成内联 lambda，否则被回收后原生侧调用会崩。
3. **回调签名**：
   - 单对象类：`(IntPtr Instance/IntPtr pYUV/IntPtr fRegioninfo, IntPtr pUser, uint dwInstanceId)`
   - **数组类**（参数初始化/变更）：`(IntPtr Instance, uint arraySize, IntPtr pUser, uint dwInstanceId)` —— `Instance` 指向结构体数组首地址，需按 `Marshal.SizeOf(typeof(X.__Internal))` 步进逐个读取。
4. **务必 Dispose**：回调内 `X.__GetOrCreateInstance(ptr)` 拿到包装对象 → 提取数据 → **先 `Marshal.Copy`/读字段，再 `.Dispose()`**。
5. **UI 线程**：回调在原生线程，更新控件用 `BeginInvoke`。建议加时间戳节流（示例用 50ms → 20fps）。

### 2.2 可用回调一览
| 注册方法 | 委托类型 | 回调数据 | 用途 |
|----------|----------|----------|------|
| `IntelligentRegisterCallBack_MillionOutlineInspect` | `IntelligentMillionOutlineInspectCallBack` | `IntelligentMillionOutlineInspect` | **毫米轮廓 + 算法结果**（核心） |
| `IntelligentRegisterCallBack_CaptureCameraYUVData` | `IntelligentCaptureCameraYUVDataCallBack` | `IntelligentYUV` | 采集相机 YUV 图像 |
| `IntelligentRegisterCallBack_MonitorCameraYUVData` | `IntelligentCaptureCameraYUVDataCallBack` | `IntelligentYUV` | 监控相机 YUV 图像 |
| `IntelligentRegisterCallBack_RecvInitJobParamsInfo` | `IntelligentJobParamInitCallBack` | `TIntelligentJobParamsGroup[]`（数组） | 参数初始化全量 |
| `IntelligentRegisterCallBack_OnJobParamsChanged` | `IntelligentJobParamChangedCallBack` | `TIntelligentJobParam[]`（数组） | 参数变更通知 |
| `IntelligentRegisterCallBack_InternalRefCornerPts` | `IntelligentInternalRefCornerPtsCallBack` | `IntelligentCalibrationInfo` | 内参角点（校准框） |
| `IntelligentRegisterCallBack_RuntimeParamsUpdate` | `IntelligentRuntimeParamsUpdateCallBack` | `IntelligentParamsSettingArray` | 运行时参数更新 |
| `IntelligentRegisterCallBack_PixelOutlineData` | `IntelligentPixelOutlineCallBack` | `IntelligentPixelOutlineArray` | 像素轮廓 |
| `IntelligentRegisterCallBack_ImageInspectionArray` | `IntelligentImageInspectionArrayCallBack` | `IntelligentImageInspectionArray` | 图像检测统计结果集 |
| `IntelligentRegisterCallBack_RealTimeLog` | `IntelligentRealTimeLogCallBack` | `IntelligentRealTimeLogInfo` | 实时日志 |
| `IntelligentRegisterCallBack_SensorStatusNotify` | `IntelligentSensorStatusNotifyCallBack` | `errorid, pStrError` | 设备状态/报错 |
| `IntelligentRegisterCallBack_NetStatusNotify` | `IntelligentNetStatusNotifyCallBack` | `EmIntelligentConnStatus, EmIntelligentServerInfo` | 网络状态变化 |
| `IntelligentRegisterCallBack_InitParamsInfo` | `IntelligentInitParamsInfoCallBack` | `IntelligentConfigDataInitArray` | 初始化配置 |
| `IntelligentRegisterCallBack_LicenseAuth` | `IntelligentLicenseAuthCallBack` | `IntelligentWeldLineAuthInfo` | 授权信息 |

### 2.3 注册示例（来自官方 Demo）
```csharp
GCHandle? _cbHandle = GCHandle.Alloc(this);
IntelligentMillionOutlineInspectCallBack cbOutline =
    new IntelligentMillionOutlineInspectCallBack(intelligentMillionOutlineInspectCallBackCSharp);

IntelligentLaser_export.IntelligentRegisterCallBack_MillionOutlineInspect(
    cbOutline, GCHandle.ToIntPtr(_cbHandle.Value));
// 其余回调同理……

// 窗体关闭时
if (_cbHandle?.IsAllocated == true) _cbHandle.Value.Free();
```

---

## 3. 图像数据（YUV 相机预览）

采集/监控相机回调给的是 **`IntelligentYUV`**（YUV420P 原始图像），不是已解码的 Bitmap。

### 3.1 数据结构 `IntelligentYUV`
| 属性 | 类型 | 说明 |
|------|------|------|
| `ImageWidth` | `int` | 图像宽 |
| `ImageHeight` | `int` | 图像高 |
| `DataPlane` | `IntPtr[3]` | 三平面指针：`[0]=Y`, `[1]=U`, `[2]=V` |
| `dwImageType` | `int` | 图像类型 |

### 3.2 提取与显示
YUV420P 内存布局：`Y` 大小 = `W*H`；`U`、`V` 各 = `(W/2)*(H/2)`。
```csharp
void OnYuv(IntPtr pYUV, IntPtr pUser, uint id)
{
    using (var yuv = IntelligentYUV.__GetOrCreateInstance(pYUV))
    {
        int w = yuv.ImageWidth, h = yuv.ImageHeight;
        byte[] y = new byte[w * h];
        byte[] u = new byte[w * h / 4];
        byte[] v = new byte[w * h / 4];
        Marshal.Copy(yuv.DataPlane[0], y, 0, y.Length);
        Marshal.Copy(yuv.DataPlane[1], u, 0, u.Length);
        Marshal.Copy(yuv.DataPlane[2], v, 0, v.Length);
        // 注意：必须在 Dispose 前完成拷贝；using 块结束即 Dispose
        // 切 UI 线程显示
        pictureBox.BeginInvoke((MethodInvoker)(() => ShowYuv420P(pictureBox, y, u, v, w, h)));
    }
}
```
> **YUV→Bitmap 转换**：官方 Demo 用 **OpenCvSharp**（`Mat.FromPixelData` + `Cv2.CvtColor(..., YUV2BGR_I420)` + `BitmapConverter.ToBitmap`）。
> ⚠️ 你的项目用的是 **EmguCV（非 OpenCvSharp）**，需改写为 Emgu 等价实现：构造 I420 `Mat`（高度 `h*3/2`、单通道），`CvInvoke.CvtColor(mat, dst, ColorConversion.Yuv420pToBgr)`（或对应枚举），再转 `Bitmap`。**不要直接引用 Demo 的 OpenCvSharp 包**，避免引入第二套 CV 库。

---

## 4. 图像数据 与 实际轮廓（两者区别与关联）

这是最容易混淆的点：**YUV 图像只是 2D 预览，真正用于焊接的是「毫米轮廓」**。

| 维度 | 图像数据（YUV） | 实际轮廓（毫米轮廓） |
|------|----------------|---------------------|
| 来源回调 | `CaptureCameraYUVData` / `MonitorCameraYUVData` | `MillionOutlineInspect` |
| 数据结构 | `IntelligentYUV` | `IntelligentMillionOutlineInspect` |
| 内容 | 相机原始画面（2D，无深度） | 线激光实测的 **3D 轮廓点云**（物理坐标 mm） |
| 用途 | 人机预览 / 监控 | **算法融合、偏差计算、焊接引导**（这才是"实际轮廓"） |

### 4.1 实际轮廓结构 `IntelligentMillionOutlineInspect`
| 属性 | 类型 | 说明 |
|------|------|------|
| `LlTimeStamp` | `ulong` | 时间戳 |
| `ContourData` | `IntelligentMillionOutlineArray` | 轮廓点集合 |
| `LlResultCount` | `ulong` | 结果数量 |
| `InspectResult` | `RuntimeInspectResult[20]` | **算法解析结果**（见 §5） |

`IntelligentMillionOutlineArray`：
- `ContourPointCount`（`uint`）：有效点数。
- `PointArray`（`FPoint[2048]`）：每个点 `FPoint { float y_pos; float z_pos; }`，单位 **mm**（`y_pos`=横向位移，`z_pos`=高度/深度）。

### 4.2 校准框（把 mm 映射到屏幕像素）
`IntelligentRegisterCallBack_InternalRefCornerPts` 回调给 `IntelligentCalibrationInfo`，含四个角点 + 中心点（均为 `float[2]`，物理坐标 mm）：
`LeftTopCorner / RightTopCorner / LeftBottomCorner / RightBottomCorner / Center`。
Demo 据此计算缩放比 `m_fRate`（Pixel/mm）与偏移，把 `FPoint(y,z)` 经 `TransPoint` 转成屏幕像素，绘制黄色校准框 + 蓝色轮廓点 + 红色特征点。

> 结论：**「图像数据」用于看，「实际轮廓」用于算**。二者通过时间戳/校准参数关联，但在 SDK 里是两条独立回调流。集成到你的 `LineLaserWorkflow` 时，应把 `ContourData` 当作与 SmartRay `CurrentMat` 对等的"线激光实测数据"接入，而非把 YUV 当分析源。

---

## 5. 算法应用解析（InspectResult）

`IntelligentMillionOutlineInspect.InspectResult` 是 `RuntimeInspectResult[20]`，承载 **SDK 内部算法对当前轮廓的解析结果**（缺陷/特征识别）。

### 5.1 `RuntimeInspectResult` 字段
| 字段 | 类型 | 说明 |
|------|------|------|
| `ParseRes` | `int` | **解析结果**：Demo 中 `==1` 表示检测到有效特征点 |
| `ErrorCode` | `int` | 错误码 |
| `Timestamp` | `ulong` | 时间戳 |
| `Width[2]` | `float[2]` | 宽度尺寸 |
| `HeightOrDepth[2]` | `float[2]` | 高度/深度尺寸 |
| `Area` | `float` | 面积 |
| `Angles[3]` | `float[3]` | 角度特征 |
| `Radii[2]` | `float[2]` | 半径特征 |
| `Vec[2]` | `float[2]` | 向量特征 |
| `FeaturePoints[64]` | `byte[64]` | 特征点原始数据 |
| `CurrentFeaturePoint` | `FPoint` | **检测到的特征点（mm，y_pos/z_pos）** |
| `ErrMsgLen` / `StrErrMsg[256]` | `uint` / `byte[256]` | 错误信息 |

> Demo 用法：
> ```csharp
> if (instance.InspectResult[0].ParseRes == 1)
> {
>     m_bHasFeaturePos = true;
>     m_posFeature = TransPoint(instance.InspectResult[0].CurrentFeaturePoint); // 转屏幕坐标
> }
> ```
> 即：`ParseRes==1` → 本帧有有效识别；特征点的物理坐标从 `CurrentFeaturePoint.YPos/ZPos` 取，单位 mm，可直接用于偏差计算。

### 5.2 批量检测回调
另有 `IntelligentRegisterCallBack_ImageInspectionArray` → `IntelligentImageInspectionArray`（`IntelligentImageInspectionResult` 批量，含 `parseRes/width/heightOrDepth/area/angles/radii/vec/featurePoints/currentFeaturePoint`），适合需要整帧统计结果的场景。

---

## 6. 参数设置解析（Job Parameter）

所有可调参数以 **`TIntelligentJobParam`** 为单位（SDK 内部称 Job Parameter）。

### 6.1 `TIntelligentJobParam` 结构
| 字段 | 类型 | 说明 |
|------|------|------|
| `SzParamName` | `byte[64]` | 参数名（**ASCII，必须固定 64 字节缓冲**） |
| `DwValueType` | `uint` | **1=string, 2=float, 3=int** |
| `CurValue` | 联合体 | 三选一：`SzValue byte[64]` / `FValue float` / `DwValue uint` |

> ⚠️ 坑：`SzParamName` 与 `CurValue.SzValue` 都是 **定长 64 字节**。写入时必须 `Array.Copy(Encoding.ASCII.GetBytes(name), 0, resultBytes, 0, Math.Min(len,64))`，否则封送报错。

### 6.2 查询参数
```csharp
TIntelligentJobParam p = new TIntelligentJobParam();
// 设 SzParamName(64字节) + DwValueType(1/2/3)
TIntelligentJobParam[] arr = new TIntelligentJobParam[1] { p };
int ret = IntelligentLaser_export.FetchJobParamter(arr, (uint)arr.Length);
// 读回：arr[0].CurValue.SzValue / .FValue / .DwValue （按 DwValueType 取）
```

### 6.3 设置参数
```csharp
TIntelligentJobParam p = new TIntelligentJobParam();
p.SzParamName = Make64Bytes("ExposureTime"); // 64 字节缓冲
p.DwValueType = 2; // float
p.CurValue = new TIntelligentJobParam.CurValue { FValue = 100.0f };
int ret = IntelligentLaser_export.SetJobParamter(new[]{p}, 1);
```

### 6.4 参数范围（Min/Max）与初始化全量
- 初始化全量：`IntelligentRegisterCallBack_RecvInitJobParamsInfo` → `TIntelligentJobParamsGroup[]`（数组回调，`Instance` 为数组首地址，按 `Marshal.SizeOf(TIntelligentJobParamsGroup.__Internal)` 步进）；每组含 `DwParamNum` 与 `StParamArray[]`，元素为 `TIntelligentJobParamFullInfo`（带 `value_Range`：`float_range.FloatMin/FloatMax`、`int_range.IntMin/IntMax`）。
- 变更通知：`IntelligentRegisterCallBack_OnJobParamsChanged` → `TIntelligentJobParam[]`。
- Demo 的 `QueryParamRange(name)` 展示了如何在本地缓存的全量参数里按名查 Min/Max，供 UI 显示与校验。

---

## 7. 与本项目的集成提示

1. **不要引入 OpenCvSharp**：Demo 用它做 YUV→Bitmap，但你的项目统一用 **EmguCV**，请改写转换层（§3.2）。
2. **命名空间/目录**：建议把该 SDK 封装为一个新模块（如 `LineLaserCam/IntelligentLaserCam/`），对外暴露与 `ICameraRun` 对齐的接口，纳入 `CameraSelector` 选择器（呼应 [[api/LineLaserManager]]、[[decisions/ADR-016-CameraSelectorUnifiedToApi]]），而非在 UI 里直接调 `IntelligentLaser_export`。
3. **连接态映射**：`ConnectToSensor` 的位掩码结果应映射到 `ConnectionState`（呼应 [[decisions/ADR-015-CameraConnectionStateDecoupled]]）。
4. **线程安全**：所有回调 → UI 的更新走 `BeginInvoke` + `InvokeRequired` 守卫（呼应 [[guides/WinForms-UI-Threading]]）。
5. **x64 构建**：集成前先把 `Release` 配成 x64（当前 `Release|AnyCPU` 是 AnyCPU，会加载 64 位 DLL 失败）。
6. **资源释放**：回调里拿到的所有 `IDisposable` 包装对象，提取完数据后立即 `Dispose()`；GCHandle 在退出时 `Free()`。

---

## 附：核心 API 速查

| 功能 | 方法 |
|------|------|
| 初始化/反初始化 | `InitSDK()` / `UnInitSDK()` |
| 设备发现 | `DetectAllSensor()` / `FetchAllSensorInfo2(StringBuilder, IntelligentSensorMsg[], ref int)` |
| 连接 | `ConnectToSensor(string)` / `DisConnSensor()` |
| 启停 | `SetSensorEnable` / `SetLaserEnable` / `SetSensorCaptureCameraEnable` / `SetSensorMonitorCameraEnable` |
| 状态 | `FetchSensorInfo(IntelligentSensorInfo)` / `FetchLaserStatus(ref uint)` |
| 帧率 | `SetSensorFpsModel(EmIntelligentFpsModel)` / `FetchSensorFps(ref float)` |
| 回调注册 | `IntelligentRegisterCallBack_<X>(委托, IntPtr pUser)` |
| 参数 | `FetchJobParamter(TIntelligentJobParam[], uint)` / `SetJobParamter(TIntelligentJobParam[], uint)` |
