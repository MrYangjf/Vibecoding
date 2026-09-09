# 监控相机开发指导（MecaVision MVSDK 版）

> 版本：v1.0
> 适用：主程序内"监控相机"模块开发（设备挂载于 KUKA 机器人，监控相机用于工件监控/拍照/存档）
> 配套文档：《运动控制模块开发文档_台达版》《台达EtherCAT_PVT与电子凸轮运动开发指南》
> 架构风格：与线激光、台达控制器模块完全一致——模块化目录、Native/抽象/实现三层 + Manager、回调"一个入口拆两个出口"、UI 轮询、工作流线程

---

## 1. 概述

### 1.1 模块定位

监控相机是主程序的一个**独立模块**（非独立解决方案），与 MotionControl（台达）、LineLaser（英莱）平级。职责：

| 职责 | 说明 |
|------|------|
| 连接/初始化 | 枚举、打开、关闭相机 |
| 图像采集 | 连续预览 / 软触发拍照 / 硬触发拍照 |
| 图像处理 | Bayer/YUV → RGB888、保存 BMP/JPG/PNG |
| 状态监控 | 连接状态回调、帧率统计、丢帧统计 |
| 配置 | 曝光/增益/分辨率/触发模式等参数管理 |
| UI | 实时画面显示（轮询最新帧）、参数配置界面 |

### 1.2 与线激光/台达的边界

| 设备 | 实时性 | 数据去向 | 断联级别 |
|------|--------|----------|----------|
| 台达控制器 | 8ms 周期 | Y 轴控制 | 急停（伺服 Fault、失控） |
| 英莱线激光 | 60~120Hz | 结果→Y轴PVT、轮廓→UI | 报警（工艺停，不动动力） |
| **监控相机** | 30fps 左右 | 画面→UI 显示、拍照→存档 | **报警**（不影响控制链路） |

**关键结论：监控相机断联属于普通 Alarm（报警），不是 Estop（急停）**——相机断联不影响伺服与运动控制的安全性，伺服仍可控，按报警流程处理即可。

---

## 2. SDK 性质与 .NET 4.8 兼容性

### 2.1 核心结论

| 项 | 结论 |
|----|------|
| 原生 DLL | `MVCAMSDK.dll`（x86）/ `MVCAMSDK_X64.dll`（x64），非托管 C DLL |
| C# 封装 | 官方已提供完整封装 `MVSDK.cs`（6884 行，静态类 `MvApi`），**.NET 4.8 直接可用，无需自己写 DllImport** |
| 加载方式 | 动态加载（`LoadLibrary` + `GetProcAddress` + `Marshal.GetDelegateForFunctionPointer`），静态构造函数按进程位数自动选择 X86/X64 DLL |
| 平台目标 | 与台达一致：**x86 或 x64 必须显式指定，不能用 AnyCPU**（MVCAMSDK.dll 与 MVCAMSDK_X64.dll 是不同 DLL） |
| 句柄类型 | `CameraHandle = System.Int32`（相机句柄） |
| 分发方式 | `MVCAMSDK.dll`(x86)/`MVCAMSDK_X64.dll`(x64) + `MVImageProcess.dll` 需与应用同目录（来自 SDK 安装目录的 SDK/ 与 SDK/X64/） |

### 2.2 错误码体系

所有 API 返回 `CameraSdkStatus` 枚举（int）。**0 = 成功**，非 0 为错误码。常用：

| 错误码 | 值 | 含义 | 处理 |
|--------|-----|------|------|
| CAMERA_STATUS_SUCCESS | 0 | 成功 | — |
| CAMERA_STATUS_FAILED | -1 | 失败 | 通用失败 |
| CAMERA_STATUS_NOT_INITIALIZED | -5 | 未初始化 | 检查是否调过 CameraSdkInit |
| CAMERA_STATUS_PARAMETER_INVALID | -6 | 参数无效 | 查参数 |
| CAMERA_STATUS_TIME_OUT | -12 | 超时 | 检查触发模式（未触发会一直超时） |
| CAMERA_STATUS_IO_ERROR | -13 | 硬件 IO 错误 | **Win7/8 非管理员访问注册表会报 -13**，需管理员权限 |
| CAMERA_STATUS_COMM_ERROR | -14 | 通讯错误 | 检查线缆/驱动 |
| CAMERA_STATUS_NO_DEVICE_FOUND | -16 | 没找到设备 | 枚举列表为空 |
| CAMERA_STATUS_DEVICE_IS_OPENED | -18 | 设备已打开 | 重复 Init |
| CAMERA_STATUS_DEVICE_LOST | -38 | 设备丢失 | 触发连接状态回调 |
| CAMERA_STATUS_GRAB_FAILED | -25 | 抓图失败 | 检查触发/带宽 |
| CAMERA_STATUS_LOST_DATA | -26 | 丢数据 | 带宽不足/线路不稳 |
| CAMERA_STATUS_BUSY | -28 | 忙 | 上一次操作未完成 |

---

## 3. 目录结构（主程序模块，对齐雷赛 MotionControl 风格）

> 与台达模块相同原则：**不引入 SDK 官方目录结构**，按主程序模块组织。

```
设备程序根/
├── MotionControl/                  # 台达运控模块（已有）
│   ├── IMotion.cs
│   ├── DeltaEtherCAT.cs
│   └── MontionManager.cs
├── LineLaser/                      # 英莱线激光模块（已有）
│   ├── EnLiLaser.cs
│   └── LineLaserManager.cs
└── MonitorCamera/                  # ★ 监控相机模块（本指南）
    ├── Native/
    │   ├── MvApi.cs                # 官方 MVSDK.cs 原样拷贝（P/Invoke 全部封装）
    │   └── MvCameraException.cs    # SDK 错误码 → 异常/日志（可选）
    ├── IVisionCamera.cs            # 抽象层（厂商无关）
    ├── MecaVisionCamera.cs         # 实现层（MVSDK 实现 IVisionCamera）
    ├── MonitorCameraManager.cs     # Manager：连接/配置/回调分发/状态/拍照流程
    ├── CameraFrameStore.cs         # 最新帧缓存（池化快照 + 版本号）
    └── CameraWorkflow.cs           # 工作流线程（拍照工艺状态机）
```

**依赖方向（只允许单向）**：

```
UI 层（UIControl/MonitorCameraControls）
    │
    ▼
MonitorCameraManager ──> CameraWorkflow ──> MecaVisionCamera ──> Native/MvApi
    │                                                        └──> MVCAMSDK.dll
    ├──> CameraFrameStore（帧缓存）
    └──> 消费：LineLaserManager（同级，经事件/委托，不反向依赖）
```

---

## 4. 分层设计与类图

### 4.1 抽象层 `IVisionCamera.cs`

```csharp
/// <summary>视觉相机抽象接口（厂商无关，UI/业务只依赖此层）</summary>
public interface IVisionCamera : IDisposable
{
    // ---- 状态 ----
    bool IsConnected { get; }              // 已连接
    bool IsCapturing { get; }              // 采集中
    string DeviceName { get; }             // 设备昵称/序列号

    // ---- 连接生命周期 ----
    bool Connect(int timeoutMs);           // 枚举+初始化（阻塞）
    void Disconnect();                     // 反初始化（必须调用，否则内存错误）

    // ---- 采集控制 ----
    bool StartCapture();                   // CameraPlay，开始连续采集
    void StopCapture();                    // CameraStop
    bool SoftTrigger();                    // 软触发一帧（触发模式下）

    // ---- 参数配置 ----
    bool SetExposureTime(double us);       // 曝光（微秒）
    bool SetAnalogGain(double db);         // 增益
    bool SetResolution(int width, int height);  // 分辨率
    bool SetFrameRate(double fps);         // 帧率
    bool SetTriggerMode(TriggerMode mode); // 连续/软触发/硬触发
    bool SaveParameterFile(string path);   // 参数存文件
    bool LoadParameterFile(string path);   // 参数从文件加载

    // ---- 事件 ----
    event EventHandler<FrameData> FrameReceived;          // 帧回调（生产线程）
    event EventHandler<CameraStatusChanged> StatusChanged; // 连接状态变化（0断开/1恢复）
}

public enum TriggerMode { Continuation = 0, SoftTrigger = 1, ExternalTrigger = 2 }

/// <summary>帧数据（引用语义：回调线程写入，消费者持有引用）</summary>
public class FrameData
{
    public int Width, Height;
    public uint MediaType;        // 图像格式
    public uint TimeStamp;        // 采集时间，单位 0.1ms
    public uint ExpTime;          // 曝光 us
    public IntPtr Buffer;         // 原始缓冲区（Bayer/YUV）
    public byte[] RgbBuffer;      // 处理后 RGB888（可选）
}
```

### 4.2 实现层 `MecaVisionCamera.cs`（MVSDK 实现）

职责：把 `MvApi` 静态类调用封装成实例方法 + 事件，内部持有句柄。

```csharp
public class MecaVisionCamera : IVisionCamera
{
    private CameraHandle _hCamera = 0;
    private tSdkCameraDevInfo _devInfo;
    private CAMERA_SNAP_PROC _frameCb;               // 必须持有引用防 GC
    private CAMERA_CONNECTION_STATUS_CALLBACK _connCb; // 必须持有引用防 GC

    public bool Connect(int timeoutMs)
    {
        // 1. 枚举
        tSdkCameraDevInfo[] list;
        var st = MvApi.CameraEnumerateDevice(out list);
        if (list == null || list.Length == 0) return false;   // -16 没设备

        // 2. 初始化（按序列号匹配，多相机时按 uInstance 区分）
        st = MvApi.CameraInit(ref list[0], -1, -1, ref _hCamera);
        if (st != CameraSdkStatus.CAMERA_STATUS_SUCCESS) return false;

        // 3. 注册连接状态回调（断联检测，SDK 自带！）
        _connCb = OnConnectionStatusChanged;
        MvApi.CameraSetConnectionStatusCallback(_hCamera, _connCb, IntPtr.Zero);
        return true;
    }

    public bool StartCapture()
    {
        // 注册帧回调（与 CameraGetImageBuffer 二选一，不能混用否则死锁）
        _frameCb = OnFrame;
        MvApi.CameraSetCallbackFunction(_hCamera, _frameCb, IntPtr.Zero, ref _oldCb);
        return MvApi.CameraPlay(_hCamera) == CameraSdkStatus.CAMERA_STATUS_SUCCESS;
    }

    private void OnFrame(CameraHandle h, IntPtr buf, ref tSdkFrameHead head, IntPtr ctx)
    {
        // 生产线程（SDK 内部线程）——只做"翻译 + 写缓存"，不做处理/UI
        FrameReceived?.Invoke(this, new FrameData { ... });
    }

    private void OnConnectionStatusChanged(CameraHandle h, uint msg, uint param, IntPtr ctx)
    {
        // msg: 0=断开  1=恢复
        // 网口相机恢复时 param: 0=网络通讯失败  1=相机掉电
        StatusChanged?.Invoke(this, new CameraStatusChanged(msg == 0 ? ConnState.Lost : ConnState.Recovered, param));
    }
}
```

### 4.3 Manager 层 `MonitorCameraManager.cs`

> 对齐 LineLaserManager 的设计原则：**依赖注入最小依赖，不反向依赖 UI/其他 Manager**。

```csharp
public class MonitorCameraManager
{
    private readonly IVisionCamera _camera;          // 注入抽象相机
    private readonly CameraFrameStore _frameStore;   // 帧缓存（Latest + Version）
    private readonly Func<bool> _isEmergencyStop;    // 注入安全状态委托（可选）

    public bool IsConnected => _camera.IsConnected;
    public event EventHandler<bool> OnlineChanged;   // 在线/离线事件（UI/工作流订阅）
    public event EventHandler<ImageSaveResult> ImageSaved;  // 存图完成

    public MonitorCameraManager(IVisionCamera camera, CameraFrameStore store,
                                Func<bool> isEmergencyStop = null)
    {
        _camera = camera;
        _frameStore = store;
        _isEmergencyStop = isEmergencyStop;
        _camera.FrameReceived += OnFrame;      // 回调入口
        _camera.StatusChanged += OnStatusChanged;
    }

    // ===== 回调"一个入口拆两个出口" =====
    private void OnFrame(object s, FrameData f)
    {
        // 出口1：业务消费（拍照存图触发、测量判定）——由工作流线程处理，这里只入队标志
        // 出口2：UI 显示——写最新帧缓存（池化快照+版本号），UI Timer 轮询
        _frameStore.Publish(f);   // 只留最新帧，中间帧丢弃
    }

    private void OnStatusChanged(object s, CameraStatusChanged e)
    {
        // 断联 → 报警（非急停）：通知 UI + 工作流暂停拍照
        if (e.State == ConnState.Lost)
        {
            OnlineChanged?.Invoke(this, false);
            // 触发报警（普通 Alarm）：记录日志、通知 UI 状态灯
        }
        else
        {
            OnlineChanged?.Invoke(this, true);
        }
    }

    // ===== 对外操作（工作流线程/UI 调用，阻塞型） =====
    public bool CaptureAndSave(string filePath)     // 软触发拍照+存图
    {
        if (!_camera.IsConnected) return false;
        return _camera.SoftTrigger()
            && _camera.SaveImage(filePath);         // 内部 CameraSaveImage
    }
}
```

---

## 5. 连接检测设计（与台达的区别）

### 5.1 台达 vs 相机 SDK

| 项 | 台达控制器 | MecaVision 相机 |
|----|-----------|----------------|
| 应用层心跳 | **无**，靠 WKC 看门狗硬件维护 | **自带连接状态回调**，无需自建心跳 |
| 检测 API | Master_Get_Connect_Status / Check_Working_Counter 等（程序轮询） | `CameraSetConnectionStatusCallback` 注册回调，**事件驱动** |
| 断开语义 | 伺服 Fault → 急停 | 设备丢失（-38）→ 报警 |
| 恢复语义 | 需程序重新建立连接 | 回调 MSG=1 通知恢复，uParam 给出掉线原因 |

### 5.2 相机连接状态回调协议

```
CameraSetConnectionStatusCallback(hCamera, pCallBack, pContext)

回调参数：
  MSG:   0 = 相机连接断开
         1 = 相机连接恢复
  uParam（网口相机，MSG=1 时）:
         0 = 上次掉线原因：网络通讯失败
         1 = 上次掉线原因：相机掉电
```

### 5.3 推荐检测方案（双保险）

```
方案1（主）：连接状态回调 —— 断联/恢复即时事件，驱动 OnlineChanged 事件
方案2（兜底）：帧率监控 —— UI Timer 检查"距上帧时间戳"，超过 N 秒无新帧
             （如 3 倍帧周期）判定画面冻结，即使回调未触发也报警
```

```csharp
// UI Timer（33ms 轮询）中兜底检测：
var now = Environment.TickCount;
if (_lastFrameTick > 0 && now - _lastFrameTick > _noFrameAlarmMs)
{
    // 画面无新帧 → 报警（普通 Alarm）
}
```

---

## 6. 配置方式（两种，推荐组合）

### 6.1 方式一：参数文件（推荐，省 UI）

SDK 自带相机配置窗口（Basic 例程思路）：调好参数 → `CameraSaveParameter` 存成二进制文件 → 随程序发布，运行时 `CameraLoadParameter` 加载。**日常工艺参数不需要自研 UI**。

### 6.2 方式二：程序 API 配置（工艺联动需要）

| 参数 | API | 说明 |
|------|-----|------|
| 曝光 | `CameraSetExposureTime(hCamera, fExposureTime)` | 微秒 us |
| 增益 | `CameraSetAnalogGain(hCamera, fAnalogGain)` | dB |
| 分辨率 | `CameraSetImageResolution(hCamera, ref tSdkImageResolution)` | 需先从能力枚举选 |
| 帧率 | `CameraSetFrameRate(hCamera, fFrameRate)` | fps |
| 触发模式 | `CameraSetTriggerCount` / `CameraSetExtTrigSignalType` | 软/硬触发 |
| 镜像 | `CameraSetMirror(hCamera, iDir, bEnable)` | 水平/垂直 |
| IO | `CameraSetInPutIOMode` / `CameraSetOutPutIOMode` | 相机 IO 方向 |
| 闪光灯 | `CameraSetStrobeMode` / `CameraSetStrobeDelayTime` 等 | 硬触发时打光 |

### 6.3 程序启动配置顺序

```
1. CameraSdkInit(1)                     // SDK 初始化（必须最先）
2. CameraSetSysOption("NumBuffers","3") // 缓冲数（可选，默认 3）
3. CameraEnumerateDevice                // 枚举
4. CameraInit                           // 打开相机
5. CameraLoadParameter(配置文件)         // 加载参数文件（如有）
   └─ 或逐个 API 设置曝光/增益/触发
6. CameraSetConnectionStatusCallback    // 注册连接状态回调
7. CameraSetCallbackFunction + CameraPlay  // 开始采集
```

---

## 7. 回调与线程模型

### 7.1 线程职责总表

| 线程 | 周期 | 职责 | 谁 |
|------|------|------|-----|
| SDK 帧回调线程 | 相机帧率（如 30fps） | 翻译帧头 + 写最新帧缓存 + 触发业务事件 | SDK 内部 |
| 连接状态回调线程 | 事件驱动 | 断联/恢复 → OnlineChanged | SDK 内部 |
| CameraWorkflow 线程 | 10~100ms | 拍照工艺状态机（触发/等待/存图/判定） | Manager 驱动 |
| UI Timer | 33ms | 轮询最新帧显示 + 画面冻结兜底检测 | 主窗体 |
| 其他 Manager 线程 | — | 运动控制/线激光各自独立 | — |

### 7.2 帧数据"一个入口拆两个出口"

```
SDK 帧回调（生产线程）
    │  OnFrame
    ▼
MonitorCameraManager.OnFrame
    ├── 出口1（业务）：触发 CameraWorkflow 标志位/事件
    │     （如"有新帧"→ 工作流判断是否拍照/存图）
    └── 出口2（显示）：_frameStore.Publish(frame)   ← 池化快照+版本号
                                        │
                                        ▼
                              UI Timer（33ms）轮询 GetLatest(out version)
                              版本号去重 → 渲染到 PictureBox/EmguCV
```

### 7.3 帧缓存（CameraFrameStore）：池化快照 + 版本号

与线激光轮廓缓存完全同构（详见《台达EtherCAT_PVT与电子凸轮运动开发指南》第四部分）：

- **写缓冲覆盖写**：回调线程只写专用写槽，读者看不到半写状态
- **原子发布**：`Interlocked.Exchange(ref _latest, frame)` + `Interlocked.Increment(ref _version)`
- **对象池**：缓冲复用，零 GC 分配
- **版本号**：UI 判断新帧，去重渲染

### 7.4 CameraWorkflow 工作流线程（拍照工艺状态机）

```
Idle → WaitTrigger → Capturing → Saving → Completed
  ↑                                       │
  └────────────── Error ←─────────────────┘
```

适合做的事（对齐 LaserLineWorkflow 原则）：
- 拍照触发判定（机器人到位 / IO 信号 / 定时）
- 等待帧到位（阻塞 `WaitOne`，可超时）
- 存图（`CameraSaveImage`，IO 阻塞）
- 合格判定（图像质量/尺寸检查）
- 恢复流程（断联重连 → 重新初始化）

**不做**：帧数据处理（回调线程）、UI 渲染（UI Timer）、实时控制（不涉及）。

---

## 8. UI 设计（对齐 UIControl 风格）

> 对齐用户 UIControl 代码规范：`UserControl + IUpdate` 接口、构造注入、`UpdateStatus()→ShowStatus()`（InvokeRequired+BeginInvoke）、Label 背景色状态灯（绿=ON/红=OFF/银=无效）、静态 IsUIOperating、Timer 轮询。

### 8.1 控件清单（置于 UIControl/MonitorCameraControls/）

| 控件 | 职责 | 关键点 |
|------|------|--------|
| `CameraConnectionControl` | 连接/断开、设备选择、状态灯 | 枚举设备下拉、连接按钮、绿灯=在线/红灯=断联 |
| `CameraPreviewControl` | 实时画面显示 | **不订阅事件，UI Timer 轮询** `_frameStore.GetLatest` |
| `CameraParameterControl` | 曝光/增益/分辨率/触发配置 | 读写参数、保存/加载参数文件 |
| `CameraCaptureControl` | 拍照/存图按钮 | 调 Manager.CaptureAndSave，Task 异步 |
| `CameraStatusBarControl` | 帧率/丢帧/在线状态 | 读帧统计 + 连接状态 |

### 8.2 预览显示（Timer 轮询，不用事件）

```csharp
public class CameraPreviewControl : UserControl, IUpdate
{
    private readonly MonitorCameraManager _mgr;
    private readonly CameraFrameStore _store;
    private Timer _uiTimer;                 // 33ms
    private int _lastVersion;

    public CameraPreviewControl(MonitorCameraManager mgr, CameraFrameStore store)
    {
        _mgr = mgr;  _store = store;
        _uiTimer = new Timer { Interval = 33 };
        _uiTimer.Tick += (s, e) => UpdateStatus();
        _uiTimer.Start();
    }

    public void UpdateStatus()
    {
        int version;
        var frame = _store.GetLatest(out version);
        if (version == _lastVersion) return;   // 版本号去重
        _lastVersion = version;
        // 渲染最新帧（PictureBox / EmguCV Mat+ImageBox）
    }
}
```

### 8.3 在线状态显示

```csharp
// 订阅 OnlineChanged 事件（低频率事件可用事件，高频帧数据才用轮询）
_mgr.OnlineChanged += (s, online) =>
{
    if (InvokeRequired) { BeginInvoke(new Action(() => SetOnline(online))); return; }
    _lblStatus.BackColor = online ? Color.Lime : Color.Red;  // 绿=在线 红=断联
};
```

---

## 9. 与运动控制 / 线激光的协作

### 9.1 依赖关系（单向，不循环）

```
MotionControl（台达）           ← 被依赖（注入 Y 轴）
LineLaserManager               ← 被依赖（若拍照需联动测量）
MonitorCameraManager           ← 本模块
        │ 构造注入
        ├─ IVisionCamera（抽象）
        ├─ CameraFrameStore
        └─ Func<bool> isEmergencyStop（安全状态委托，非整个 MotionManager）
```

### 9.2 典型联动场景

| 场景 | 协作方式 |
|------|----------|
| 机器人到位 → 拍照 | CameraWorkflow 判定到位 → SoftTrigger → 存图 |
| 拍照 → 通知测量 | Manager 抛 `ImageSaved` 事件，业务层订阅 |
| 相机断联 | 报警（Alarm）：UI 红灯 + 日志；**不停动力**（区别于台达急停） |
| 急停联动 | 急停时 CameraWorkflow 通过注入的 `isEmergencyStop` 委托停止拍照 |

---

## 10. 关键注意事项（踩坑清单）

1. **管理员权限**：SDK 访问注册表，Win7/8 非管理员运行初始化报 -13，程序需申请管理员权限（app.manifest）
2. **反初始化必须调用**：退出前 `CameraUnInit`，否则内存错误
3. **回调中禁止调用 CameraGetImageBuffer**：死锁
4. **GetImageBuffer / SnapToBuffer 后必须 ReleaseImageBuffer**：否则预览通道阻塞
5. **SnapToBuffer 会切换分辨率，速度慢**：实时处理用回调或 GetImageBuffer
6. **回调委托必须持有引用**（类字段），防止被 GC 回收导致回调失效
7. **触发模式下抓图超时**：先检查是否设置了触发模式（未触发会一直 -12 超时）
8. **平台目标**：x86/x64 显式指定，AnyCPU 会加载错 DLL
9. **多相机**：按 `tSdkCameraDevInfo.acSn`（序列号）+ `uInstance`（实例索引）区分，别用数组下标
10. **掉线原因**：网口相机恢复时 uParam 区分"网络通讯失败(0)/相机掉电(1)"，日志要记录

---

## 附录 A：核心 API 速查表

| 函数 | 签名要点 | 用途 |
|------|----------|------|
| CameraSdkInit | `(int iLanguageSel)` | SDK 初始化（最先调用，1=中文） |
| CameraSetSysOption | `(string name, string value)` | 系统选项，如 `("NumBuffers","3")` |
| CameraEnumerateDevice | `(out tSdkCameraDevInfo[])` | 枚举设备 |
| CameraInit | `(ref tSdkCameraDevInfo, int mode, int team, ref CameraHandle)` | 打开相机，mode/team 传 -1 |
| CameraSetCallbackFunction | `(hCam, CAMERA_SNAP_PROC, IntPtr, ref old)` | 注册帧回调 |
| CameraSetConnectionStatusCallback | `(hCam, CAMERA_CONNECTION_STATUS_CALLBACK, IntPtr)` | 注册连接状态回调 |
| CameraPlay / CameraPause / CameraStop | `(hCam)` | 采集启停 |
| CameraGetImageBuffer | `(hCam, out tSdkFrameHead, out IntPtr, uint timeout)` | 主动取帧（必须 Release） |
| CameraReleaseImageBuffer | `(hCam, IntPtr)` | 释放缓冲 |
| CameraSnapToBuffer | `(hCam, out head, out buf, uint timeout)` | 软触发快照（慢） |
| CameraImageProcess | `(hCam, IntPtr in, IntPtr out, ref head)` | Bayer/YUV → RGB888 |
| CameraSaveImage | `(hCam, string path, ref head, IntPtr buf, uint type)` | 存图（JPG/BMP/PNG/RAW） |
| CameraSetExposureTime / CameraGetExposureTime | `(hCam, float/ref float)` | 曝光 us |
| CameraSetAnalogGain / CameraGetAnalogGain | `(hCam, float/ref float)` | 增益 dB |
| CameraSetImageResolution | `(hCam, ref tSdkImageResolution)` | 分辨率 |
| CameraSetFrameRate / CameraGetFrameRate | `(hCam, float/ref float)` | 帧率 |
| CameraSetTriggerCount | `(hCam, int count)` | 软触发帧数 |
| CameraSetExtTrigSignalType | `(hCam, ref tSdkTrigger)` | 外触发信号类型 |
| CameraSetMirror | `(hCam, int dir, bool enable)` | 镜像 |
| CameraGetFrameStatistic | `(hCam, ref tSdkFrameStatistic)` | 帧统计（丢帧） |
| CameraGetCapability | `(hCam, out tSdkCameraCapbility)` | 能力描述（用于动态建 UI） |
| CameraUnInit | `(hCam)` | 反初始化（必须） |

## 附录 B：关键结构体

```csharp
// 设备信息（枚举结果）
tSdkCameraDevInfo {
    byte[32] acProductSeries;   // 产品系列
    byte[32] acProductName;     // 产品名称
    byte[32] acFriendlyName;    // 昵称（可改名）
    byte[32] acDriverVersion;   // 驱动版本
    byte[32] acSensorType;      // Sensor 类型
    byte[32] acPortType;        // 接口类型（USB2.0/USB3.0/GIGE）
    byte[32] acSn;              // 唯一序列号
    uint uInstance;             // 同型号多相机的实例索引
}

// 帧头（回调/取帧都带）
tSdkFrameHead {
    uint uiMediaType;   // 图像格式（Bayer/YUV/RGB）
    uint uBytes;        // 数据字节数
    int iWidth, iHeight;// 宽高
    uint bIsTrigger;    // 是否触发帧
    uint uiTimeStamp;   // 采集时间（0.1ms）
    uint uiExpTime;     // 曝光（us）
    float fAnalogGain;  // 模拟增益
    // ... 伽马/对比度/饱和度/RGB增益等
}

// 能力描述（动态构建 UI 时用）
tSdkCameraCapbility {
    int iOutputIoCounts, iInputIoCounts;  // IO 数量
    tSdkExpose sExposeDesc;               // 曝光范围
    tSdkResolutionRange sResolutionRange; // 分辨率范围
    tRgbGainRange sRgbGainRange;          // 增益范围
    // ... 触发描述/帧速描述/媒体格式等
}
```
