---
title: IntelligentLaserCameraRun API 参考
date: 2026-07-24
tags: [API, 相机, 英莱, 线激光, ICameraRun]
source: AdaWeldSystem/LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs
---

# IntelligentLaserCameraRun API 参考

> 英莱(IntelligentLaser / ANLE) 工业 3D 线激光相机运行控制，位于 `LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`，命名空间 `AdaWeldSystem.IntelligentLaserCam`（与目录同名，与 `SmartRayCameraRun`/`VirtualCam` 等同例，各自保留命名空间）。
> 实现 [[api/ICameraRun]] 契约，**无缝替换** `SmartRayCam.CameraRun` / `VirtualCam.VirtualCameraRun` 注入 `LineLaserWorkflow`：**取图链（`AcquireImage` 经 `CameraSelector.Active`）零改动**；仅 `Start()` 相机选择逻辑新增 `IntelligentLaser` 分支以尊重用户选择（模拟模式仍强制虚拟），并接入 `LLCamWorkJob` 相机下拉框。
> SDK 包装为厂商 CppSharp 生成的 `IntelligentLaser_CSharp.dll`（.Net Framework 构建，供 .NET 4.8），无需手写 P/Invoke。开发手册见 [[api/IntelligentLaserSDK_CSharp_DevManual]]。

## 数据链路

```
MillionOutlineInspect 回调（原生线程）
   → IntelligentMillionOutlineInspect.__GetOrCreateInstance(pOutlineData)  [务必 using 释放]
   → inspect.ContourData.PointArray[]（托管 FPoint[]，CppSharp 封装）
   → PointCloudData.AddPoint(0, YPos, ZPos)  [托管点云]
   → ConvertContourToMatDemo(cloud)  [GDI+ 画法，参照官方 demo PictureBox 画法；有校准数据时叠加校准框/十字架/角点/特征点]
   → 复用持久画布 Clear 重绘 + CopyTo 原地更新 _currentMat（不再每帧 new，详见「关键设计-轮廓Mat复用持久画布」），置 AcquisitionCompletedSignal → NotifyFrameReady() 触发 ContourFrameReady

InternalRefCornerPts 回调（原生线程，校准数据）
   → IntelligentCalibrationInfo.__GetOrCreateInstance(fRegioninfo)  [务必 using 释放]
   → 拷贝 中心点 + 4 角点（mm）到 IlCalibrationInfo 快照（_calibLock 保护）
   → 供 ConvertContourToMatDemo 绘制校准框（矩形区域）+ 大十字架
```
与 SmartRay / Virtual 同构：工作流 `AcquireImage()` 经 `CameraSelector.Active.CurrentMat.Clone()` 取帧，链路零改动。

> ⚠️ **三层控制完全解耦（2026-08-18 用户澄清）**：`SetSensorEnable(true)` 是 `MillionOutlineInspect` 回调的**触发源头**——传感器使能后回调即持续出数据；`SetLaserEnable` 仅控制物理激光照射，与回调触发**无任何关系**（激光未开时回调仍正常触发，只是轮廓数据可能无有效激光线）；`SetSensorCaptureCameraEnable` 仅影响 YUV 预览回调。`OpenSensor` 中 `SetSensor/SetLaser/SetCaptureCamera` 为三个独立并列调用，`MillionOutlineCallback` 内不检查激光状态。见 [[lessons/IntelligentLaser-Pitfalls]]。

## 成员

| 成员 | 说明 |
|------|------|
| `bool IsConnected { get; }` | 是否已连上硬件（`OpenSensor` 成功后置 true）；供 `CameraSelector.ConnectionState` 派生「已连接」 |
| `double ScanRateHz { get; }` | 当前采集扫描率(Hz)。**2026-08-20 升级为运行时实时刷新**：`MillionOutlineCallback` 中每 500ms 从 `FetchSensorFps` 读取一次硬件实际帧率并更新，反映传感器运行时的实时采集分析频率。此前仅在 `OpenSensor` / `ApplyFrameRateModel` / `DetectHardwareStatus` 三个时机更新。工作流据此缩放 `WaitOne` 超时。**注意**：SDK 调用 `dwInstanceId` 必须为 1（默认值），传 0 会返回 `INTELLIGENT_E_UNINIT` 导致读不到帧率 |
| `Mat CurrentMat { get; }` | 最近一帧轮廓 Mat（克隆返回，调用方独占）。内部 `_currentMat` 为**持久复用 Mat**（2026-08-26 重构：`ConvertContourToMatDemo` 每帧 `Clear` 重绘 + `CopyTo` 原地更新，不再每帧 new），`CurrentMat` getter 克隆返回，调用方独占；资源释放统一在 Dispose 路径（`ReleaseNativeResources` 同步释放持久画布 `_canvasBmp`/`_canvasG`） |
| `void OpenSensor(string ip)` | 一键全开（自动工作流用）。幂等：复用 `ConnectCore` 连接 → 复用 `SetSensor(true)`/`SetLaser(true)`/`SetCaptureCamera(true)` 分步开外设 → 设 STANDERD(60Hz) → FetchSensorFps。默认 IP `192.168.178.210`。幂等判断由 `_isOpened` 改为 `_isConnected`（2026-08-25 状态精简） |
| `void SensorRunContinue()` | 未打开则先 `OpenSensor(DefaultSensorIp)`；未运行时 `SetSensor(true)`（2026-08-25 起经统一封装更新本地 `_isCameraOn`，弃直接 SDK 调用） |
| `void SensorStop()` | `SetSensor(false)`，保留 SDK 初始化（2026-08-25 起经统一封装） |
| `bool IsRunning { get; }` | **2026-08-25 派生化**：`=> _isCameraOn`（ICameraRun 接口契约保留；`_isRunning` 字段已删） |
| `void Dispose()` | 按顺序关外设→`UnInitSDK`→释放 GCHandle→释放 `_currentMat`→`GC.SuppressFinalize`。**2026-08-25 释放优化**：外设关闭归集 `ShutdownPeripherals()`（幂等 `_peripheralsOff` 防护，与 `DisconnectManual` 共用，避免重复 SDK 调用/回调等待）；回调等待超时 2000→500ms（回调源先停，在途回调快速归零）；`ReleaseNativeResources` 幂等 `_released` 防护（Dispose/析构只完整执行一次）（遵循 [[decisions/ADR-001-DisposePattern]]，未重写 `Dispose(bool)`） |
| `~IntelligentLaserCameraRun()` | **析构函数（finalizer，2026-08-14 新增）**：调 `ReleaseNativeResources()` 按序释放 SDK 非托管资源（幂等 `_released` 防护，Dispose 已执行则跳过），不触碰托管对象（如 `_currentMat`） |
| `bool ConnectManual(string ip)` | **2026-08-14 新增**：分步手动连接——复用 `ConnectCore` 只连接（**不开传感器/激光/相机**）；与 `OpenSensor`（一键全开）**共用同一套 `ConnectCore` 连接逻辑**，供英莱相机页面 `ILCamPage` 分步控制；**`CameraSelector.DetectConnection` 英莱分支亦改调此方法（启动只连接，不开激光/相机）** |
| `private bool ConnectCore(string ip)` | **2026-08-17 新增（私有，手动/自动统一封装）**：**首次连接**才 InitSDK→注册回调→ConnectToSensor→Core 连通校验；重连仅 ConnectToSensor。**回调委托只注册一次、全程存活**（2026-08-20 优化，与 demo 做法一致），避免频繁连接断开导致 CallbackOnCollectedDelegate。成功置 `_isConnected=true` + 重置 `_peripheralsOff` + `SyncHardwareStatus()`。**回调必须在连接前注册**（2026-08-18 修正）：SDK 连接完成时一次性触发 `InternalRefCornerPts`（校准框）与 `RecvInitJobParamsInfo`（Job 参数元数据）回调，注册晚了两个回调都会丢失。`OpenSensor` 与 `ConnectManual` 均复用此方法 |
| `bool ConfigureDefaultCommPeriod()` | **2026-08-20 新增**：配置默认回调周期（SetSensorCommPeriod），参数：DwSendCycle=10ms / DwBufferDuration=1000ms（英莱技术支持建议）。**仅首次配置有效**（`_commPeriodConfigured` 标志防重复），后续连接/重连不重复设置。仅在 `LineLaserWorkflow.InitializeWorker` 初始化成功后调用一次；手动连接不调用。返回 true=配置成功，false=已配置过或未连接或失败 |
| `static string LoadSavedIp()` | 读 `Config/INI/IntelligentLaser.ini` 保存的 IP，未配置回退默认 `192.168.178.210`；供页面初始化填充 IP 框 + `DetectConnection` 读取（替代硬编码） |
| `static void SaveSensorIp(string ip)` | 保存英莱相机 IP 到 `Config/INI/IntelligentLaser.ini`（扫描选中相机后调用） |
| `List<IlSensorInfo> ScanSensors()` | 扫描网口下英莱相机（`DetectAllSensor`+`FetchAllSensorInfo2`），返回 IP/SN/版本列表（`IlSensorInfo` 托管快照）；未初始化时临时 `InitSDK`、扫完反初始化。⚠️ `IntelligentSensorMsg` 字段名/`FetchAllSensorInfo2` 形参以 VS x64 生成代码为准（QA P0） |
| `void DisconnectManual()` | **2026-08-25 重构**：复用 `ShutdownPeripherals()`（关传感器→激光→采集相机→监控相机→断连，幂等 `_peripheralsOff` 防护）。**不 UnInitSDK、不释放委托**（回调委托全程存活，避免 CallbackOnCollectedDelegate），仅 Dispose 时完整释放 |
| `void SetSensor/SetLaser/SetCaptureCamera/SetMonitorCamera(bool)` | 分步启停传感器/激光/采集相机/监控相机。⚠️ **线激光工作方式：启停传感器用 `SetSensor`（`SetSensorEnable` 是 `MillionOutlineInspect` 回调的触发源头）；`SetCaptureCamera` 仅上电采集相机、不起传感器，非线激光页面（ILCamPage）工作方式，2026-08-24 已从 ILCamPage 移除调用**。激光/传感器状态判断统一用 `IsLaserOn()` / `IsCameraOn()`。**2026-08-25：`SetSensor`/`SetLaser` 成功后本地状态同步更新（`_isCameraOn`/`_isLaserOn`），`IsCameraOn()` 对应 `StCtrl.DwCameraEnable`（用户澄清：由 `SetSensor(bool)` 控制）** |
| `int ApplyFrameRateModel(EmIntelligentFpsModel)` | **2026-08-18 新增（private，内部实现）**：SDK 原生枚举版本，已降为私有；UI 层请使用 `IlFpsModel` 托管枚举重载 |
| `int ApplyFrameRateModel(IlFpsModel)` | **2026-08-18 新增（UI 层推荐入口）**：托管枚举版本，UI 层调用无需引用 SDK 原生 `EmIntelligentFpsModel`；内部映射到 SDK 枚举后调用私有重载 |
| `IlFpsModel FetchFpsModel()` | **2026-08-18 新增**：从硬件读取当前帧率模式（`FetchSensorFpsModel`），失败回退 STANDERD。供 UI 连接后同步下拉选中项 |
| ~~`IsCaptureCameraOn()` / `IsSensorRunning()`~~ | **已从代码移除（2026-08-25 状态精简）**：三态 `IsConnected`/`IsLaserOn()`/`IsCameraOn()` 已覆盖；勿再引用 |
| `void SyncHardwareStatus()` | **2026-08-25 更名**（原 `DetectHardwareStatus()`，`IlHardwareStatus` 快照类已删）：从硬件同步激光/相机实际状态到本地字段（`_isLaserOn`/`_isCameraOn`）并刷新 `_scanRateHz`。连接成功（`ConnectCore`）后自动调用一次（"第一次正确"，解决「上次异常退出未关硬件」）；`ILCamPage.SyncFromHardwareCore` 亦调用 |
| `double MeasuredFps { get; }` | **2026-08-18 新增**：实测帧率(Hz)。由 `MillionOutline` 回调逐帧计算（首帧剔除），供 UI 实时显示 |
| `void ResetMeasuredFps()` | **2026-08-18 新增**：重置实测 FPS 计数器（`_lastFrameTime` + `_firstFrameSkipped` + `_measuredFps`）。相机关闭/重新开启时调用，确保首帧被剔除 |
| `bool IsManualMode { get; set; }` | **2026-08-20 新增**：手动模式标志。true=手动调试模式（回调生成 Mat + 触发 ContourFrameReady UI 事件）；false=自动/其他模式（回调仅外传 ContourDataReady 数据，不生成 Mat、不触发 UI 事件，节省 CPU/GPU）。默认 true（兼容手动页面直接使用场景）。由 `ILCamPage.UpdateModeUi` 根据工作流运行状态自动设置 |
| `bool IsLaserOn()` | 激光状态。**2026-08-25 起本地状态**：`_isConnected && _isLaserOn`（连接时 `SyncHardwareStatus` 同步 + `SetLaser` 更新，UI 读取无延迟；弃每次 `FetchLaserStatus` 硬件查询） |
| `List<string> GetJointTypeDisplayKeys(int jointType)` | **2026-08-25 新增**：该接头类型应显示的参数键集（jointtypelist.json `display`，技术员确认的 Job 实际使用参数）；供 `ILAlgoPage` 参数表过滤 |
| `int LastContourPointCount { get; }` | 最近一次毫米轮廓点数量（MillionOutline 回调内更新，供页面显示轮廓点数） |
| `IlCalibrationInfo CalibrationInfo { get; }` | **校准数据快照（2026-08-17 新增）**：中心点 + 4 角点（mm 物理坐标，[0]=Y 横向 / [1]=Z 高度），由 `InternalRefCornerPts` 回调填充（`_calibLock` 保护）；未收到校准回调时为 null。供 `ConvertContourToMatDemo` 绘制校准框（矩形区域）+ 大十字架（参照官方 demo） |
| `event EventHandler ContourFrameReady` | **轮廓帧就绪事件（2026-08-17 新增，回调驱动显示）**：每成功换一帧触发一次，按 ~20fps（50ms）节流（`NotifyFrameReady`），由 `ILCamPage`/`ILAlgoPage` 订阅后直接刷新轮廓画面与识别结果，**替代 UI 层轮询 Timer**（与英莱官方 demo 的「回调更新画面」一致）；在 SDK 原生线程触发，订阅方须 `InvokeRequired` 封送。**2026-08-20 回调重构后仅手动模式触发**：`IsManualMode=true` 时才生成 Mat 并触发此事件；自动模式不触发，节省 CPU/GPU |
| `event EventHandler<ContourDataEventArgs> ContourDataReady` | **轮廓数据就绪事件（2026-08-18 新增，数据分发中心）**：每帧 MillionOutline 回调成功产出轮廓后触发，携带 `PointCloudData`（YZ 坐标，mm）+ `IlInspectResult`（ParseRes+特征）+ 实测帧率。供 MainPage 轮廓 ScottPlot 订阅做实时显示、供 `LineLaserWorkflow` Running 模式订阅做结果码监听。**不节流**，完全跟随回调帧率（默认 ~60Hz）。在 SDK 原生线程触发，订阅方须 `InvokeRequired` 封送。**2026-08-20 回调重构后两种模式均触发**：手动模式和自动模式都会外传此事件，数据消费方（ScottPlot / 工作流）不受影响。详见 [[decisions/ADR-039-YinglaiDataFlow]] |
| `int FetchCurrentJobId()` | 获取当前 JOB ID（`FetchJobInfo`；⚠️ dwCmd=0 查询语义待真机验证） |
| `List<IlJobDescInfo> FetchJobList()` | **2026-08-24 新增**：读取运行目录 `IntelligentLaser_jobdesclist.json`（连接相机后原生 SDK 自动落盘，**这是「全部 Job 号」的官方数据源**，SDK 无枚举 API 但落盘 JSON 提供），返回全部 Job 描述（Id/JointType/JobDescribe）；文件缺失/解析失败返回空列表，不缓存不兜底 |
| `IlJobDescInfo GetCurrentJobInfo()` | **2026-08-24 新增**：当前 JOB 完整描述（`FetchCurrentJobId` + `FetchJobList` 按 id 匹配）；未连接/查不到返回 null。供 UI 展示当前 JOB 与接头类型 |
| `string GetJointTypeName(int jointType)` | **2026-08-24 新增**：从运行目录 `IntelligentLaser_jointtypelist.json` 查询接头类型中文名（如 32=对接、16=左搭接）；文件缺失/未命中返回 null。实现复用 `FetchJointTypes()` 按 `Int` 匹配 |
| `List<IlJointTypeInfo> FetchJointTypes()` | **2026-08-24 新增**：读取运行目录 `IntelligentLaser_jointtypelist.json` 返回**全部接头类型**（`Int` 编号 + `NameZh` 中文名），供新建 JOB 弹窗枚举可用类型；文件缺失/解析失败返回空列表 |
| `int SwitchJob(int jobId)` | 切换 JOB（`SetSensorJobInfo` + `EmJobSettingCmd.SWITCH`） |
| `int CreateJob(int jointType, string desc)` | 新建 JOB（`SetSensorJobInfo` + `CREATE` + 焊缝类型 + 备注） |
| `int DeleteJob(int jobId)` | 删除 JOB（`SetSensorJobInfo` + `DELETE`） |
| `IlInspectResult LastInspectResult { get; }` | 最近一次英莱 SDK 算法解析结果快照（线程安全拷贝）。含特征点 mm 坐标(FeatureY/FeatureZ)、尺寸(Width/Height)、面积、角度等；仅当 `HasInspectResult==true` 时有效 |
| `bool HasInspectResult { get; }` | 最近一次 SDK 算法结果是否已被回调写入（供工作流判定走英莱算法路线） |
| `List<IlJobParamInfo> FetchAllJobParams()` | **2026-08-25 语义修正**：返回**当前 JOB** 的 Job Parameter 列表（值/类型/范围取自回调缓存）。与官方 demo 一致——`OnJobParamsChanged` 回调推送的参数自带当前值，**不再逐个 `FetchJobParamter` 二次查询**（避免 N 次网络调用）。未连接抛 `InvalidOperationException`，由 UI 层捕获提示 |
| `int ApplyJobParams(IEnumerable<IlJobParamInfo>)` | 将编辑后参数下发到设备，返回 SDK 返回值（0=成功）；未连接返回 -1；范围校验由 UI 层调用前完成。下发成功后 SDK 经 `OnJobParamsChanged` 回调更新缓存并触发 `JobParamsChanged` |
| `event EventHandler JobParamsChanged` | **2026-08-24 新增 / 2026-08-25 缓存职责修正**：设备侧 Job Parameter 缓存被刷新后触发。回调内：连接/切 JOB 推**当前 Job 完整参数集**（arraySize=当前 Job 参数数，如 21）→ 替换式重建 `_jobParams`（只保留当前 Job 参数，与 demo 一致）；单参数修改推少量变更 → 按名增量更新（保留其余参数）；范围从 `_jobMeta` 元数据补全。在 SDK 原生线程触发，订阅方须 `InvokeRequired` 封送 |
| `IlCameraParam FetchCameraParams()` | **相机基础参数（2026-08-15 新增）**：读曝光/伽马/激光功率（`FetchSensorBaseParam`→`IntelligentSensorBaseParams`），未连接返回 null。**与 Job Parameter（算法参数）是两套独立 API** |
| `int ApplyCameraParams(IlCameraParam)` | **相机基础参数（2026-08-15 新增）**：下发曝光/伽马/激光功率（`SetSensorBaseParam`），返回 SDK 返回值（0=成功）；未连接返回 -1 |

## 相机参数 vs Job 参数（两套独立体系）

英莱 SDK 有两套**完全独立**的参数体系，勿混淆：

| 参数体系 | SDK 结构 / API | 内容 | 托管封装 |
|---------|---------------|------|---------|
| **相机参数（基础参数）** | `IntelligentSensorBaseParams` / `FetchSensorBaseParam`·`SetSensorBaseParam` | 曝光(`Exptime`·uint)、激光强度(`Power`·uint)、抗弧光/伽马(`Gama`·float)、温度(`FTempCpu` 只读) | `IlCameraParam` + `FetchCameraParams`/`ApplyCameraParams` |
| **Job 参数（算法参数）** | `TIntelligentJobParam` / `FetchJobParamter`·`SetJobParamter` | 焊缝接头种类、特征点、向量等算法参数（名称/类型/范围由 SDK 初始化回调下发，**不硬编码**） | `IlJobParamInfo` + `FetchAllJobParams`/`ApplyJobParams` |

> 相机参数编辑 UI 为 `Sub3UI/ILParamPage`（Table 单元格编辑曝光/激光强度/抗弧光）；Job 参数编辑在 `Sub3UI/AlgorithmEditForm` 模块 B（`ILAlgoPage`）。

## 校准数据（InternalRefCornerPts，显示画面）

英莱相机在 `RegisterCallbacks()` 中额外注册 `IntelligentRegisterCallBack_InternalRefCornerPts` 校准回调（`_cbCalibration` 存字段防 GC），捕获**校准框（矩形区域）+ 大十字架**所需的几何数据（参照官方 demo `Form1.cs:572` `intelligentInternalRefCornerPtsCallBackCSharp`）。

> ⚠️ **回调注册时机（2026-08-18 修正）**：`RegisterCallbacks()` 必须在 `ConnectToSensor` **之前**调用。SDK 在连接完成时**一次性触发** `InternalRefCornerPts` 校准回调，若注册在连接之后，该回调丢失 → 校准框/十字架永不显示。官方 demo 顺序为 `InitSDK → 注册全部回调 → ConnectToSensor`（Form1.cs:84/103-108/164）。详见 [[lessons/IntelligentLaser-Pitfalls]]。

### 数据契约 IlCalibrationInfo（命名空间级托管类）
字段对齐 SDK `IntelligentCalibrationInfo`：`Center`（中心点）+ `LeftTopCorner`/`RightTopCorner`/`LeftBottomCorner`/`RightBottomCorner`（4 角点），坐标均为**物理 mm**，`[0]=Y 横向 / [1]=Z 高度`；`HasData` 标记是否已收到有效校准数据。由 `CalibrationCallback` 在 `using` 块内拷贝（务必 Dispose 包装对象），`_calibLock` 保护换入快照，`CalibrationInfo` 属性线程安全读取。

### 绘制（ConvertContourToMatDemo，参照 demo resetInnerData/TransPoint/Paint）
有校准数据（`CalibrationInfo.HasData`）时：
- **比例换算**：`rate = min((w-2*margin)/cornerW, (h-2*margin)/cornerH)`（cornerW/H 由角点差求得，同 demo）。
- **居中（2026-08-18 终版）**：**恢复 demo 原版角点公式 `center ± |corner*rate|`，仅改 `center = (w/2, h/2)`**（弃用 demo 的 `fPersent/dwOffset` 计算）。`trans(y,z) = (center.X + y*rate, center.Y - z*rate)` 同 demo。mm 原点(0,0) 在图像中心，十字交叉居中，轮廓负值 mm 向两侧展开。
  - ⚠️ 演进记录：初始 demo 的 `fPersent/dwOffset` 计算使十字未对齐图像中心；前三轮改动（矩形折叠/originX 间接映射/halfExtent 相对偏移）均偏离 demo 正确公式。**终版：demo 原版公式 + 仅改 center 为图像中心**。见 [[lessons/IntelligentLaser-Pitfalls]]。
- **校准框**：`FillPolygon` 深色背景（`0x3B3B3B`）+ `DrawPolygon` 黄色边框（2px）。
- **大十字架**：水平线（过中心点向右 100px）与左右边交点、垂直线（过中心点向下 100px）与上下边交点，经 `CalcTwoLineCrossPoint` 求交后 `DrawLine` 浅灰色（2px）——十字线裁剪到校准框四边。
- **角点/中心点**：浅绿圆点（6px 直径）；**特征点**：`ParseRes==1` 时红色 8px 方块（`trans(FeatureY, FeatureZ)`）。
- **轮廓折线**：按 `trans(y,z) = (center.X + y*rate, center.Y - z*rate)` 映射物理坐标到屏幕（绿色 1.5px），mm 原点(0,0) 在图像中心。
- **mm 虚线刻度栅格（校准模式，画在最上层）**：原点(0,0) 在图像中心，`stepMm=max(1, round(40/rate))`，垂直网格 `screen_x = center.X + mm*rate`、水平网格 `screen_y = center.Y - mm*rate`；底部/左侧 8.5px 灰色宋体标注 mm 值。

无校准数据时回退原自动缩放画法（网格 + 折线 + Y/Z 轴标签）。`CalcTwoLineCrossPoint` 为线段交点辅助方法（对应 demo `Form1.cs:659`，平行返回 `(-1,-1)`）。

## Job Parameter（英莱算法参数）

英莱相机自带一套**设备侧 Job Parameter**（焊缝接头种类、特征点、向量等算法参数，名称/类型/范围由 SDK 初始化回调下发，**不硬编码**），与 EmguALG 的 `PipelineConfig`（项目算法参数）是两套完全不同的参数体系。二者已合并进同一 UI 窗体 `Sub3UI/AlgorithmEditForm`（见 [[api/AlgorithmEditForm]] 模块 B），但后端由本类以 `IlJobParamInfo` 托管缓存封装，**UI 绝不直连 `IntelligentLaser_export`**（呼应 [[api/IntelligentLaserSDK_CSharp_DevManual]] §7「参数读写封装进相机模块」）。

### 数据契约 IlJobParamInfo（命名空间级托管类）
`ValueType`：`1=string` / `2=float` / `3=int`；范围仅 float/int 有效。字段：`Name`/`StringValue`/`FloatValue(double)`/`IntValue(long)`/`HasRange`/`FloatMin/FloatMax`/`IntMin/IntMax`。

### 生命周期
- **初始化缓存（2026-08-25 职责修正）**：`RegisterCallbacks()` 注册两个 Job 回调——`RecvInitJobParamsInfo`（`_cbInitJobParams`）与 `OnJobParamsChanged`（`_cbJobParamsChanged`）。二者均遵循 GC 三层保护（`GCHandle.Alloc` 钉住 + 回调末尾 `GC.KeepAlive` + `FreeCallbackHandles` 统一释放），与 demo 同时注册两回调一致。
- **元数据（Init 回调）**：`InitJobParamsCallback` 按 `Marshal.SizeOf(TIntelligentJobParamsGroup.__Internal)` 步进，marshaling `TIntelligentJobParamsGroup[]` → 提取 `DwParamNum`/`StParamArray[]` 中每个 `SzParamName`(64B)/`DwValueType`/`value_Range`，**仅填充 `_jobMeta` 元数据字典**（参数名→类型/范围）。⚠️ **不填充 `_jobParams`**——Init 回调下发的是全量参数元数据（含所有 Job 类型），若全量缓存会导致参数表显示远超当前 Job 实际参数（用户反馈的膨胀根因，2026-08-25 修复）。
- **当前 Job 参数集（Changed 回调）**：`JobParamsChangedCallback` 按 `Marshal.SizeOf(TIntelligentJobParam.__Internal)` 步进，marshaling `TIntelligentJobParam[]`。连接/切 JOB 时 SDK 推送**当前 Job 完整参数集**（arraySize=当前 Job 参数数，如 21，与官方 demo 一致）→ **替换式重建 `_jobParams`**；单参数修改推送少量变更 → 按名增量更新（保留其余参数）。范围从 `_jobMeta` 补全（Changed 回调结构无 value_Range）。完成后触发 `JobParamsChanged` 事件。
- **读取**：`FetchAllJobParams()` **直接返回 `_jobParams` 回调缓存拷贝**（回调携带当前值，不再逐个 `FetchJobParamter` 二次查询，2026-08-25 优化）。
- **下发**：`ApplyJobParams(values)` 构造 `TIntelligentJobParam`（`CurValue` 按类型填 `SzValue/FValue/DwValue`），调 `SetJobParamter(arr, (uint)arr.Count)`；返回值透传给调用方判定成败。成功后 SDK 经 Changed 回调更新缓存并触发事件。
- **无离线缓存（2026-08-24 移除）**：参数以线激光设备为唯一真相源——未连接设备即无 Job 参数，原 `LoadOfflineCache`/`SaveOfflineCache`/`_ilIniFile`/`HasJobParamCache` 及 `Config/Jobs/IntelligentLaserJobParams.ilini` 落盘逻辑已全部删除（呼应 [[lessons/IntelligentLaser-JobParamNoOfflineCache]]：异常退出后离线缓存会误导用户显示为过时默认值）。

### Job 列表与接头类型（运行目录 JSON 数据源，2026-08-24 接入）
连接相机后，原生 SDK 会在**运行目录**（`AppDomain.CurrentDomain.BaseDirectory`）自动落盘两个 JSON，**这是「全部 Job 号」与「接头类型语义」的官方数据源**（技术员确认，SDK 无枚举 API 但落盘 JSON 提供）：
- **`IntelligentLaser_jobdesclist.json`**：`[{"jobdescribe":"","jointtype":32,"id":1}, ...]` → 全部 Job（Id + JointType + JobDescribe）。`FetchJobList()` 解析，UI 填入 cmbJob 下拉（需求①「读取所有 job 号」落地）。
- **`IntelligentLaser_jointtypelist.json`**：`{"joint_types":[{"hex":"0x10","int":16,"name_zh":"左搭接","name_en":"Left-Lap","lines":[...],"calculations":[...],"display":{参数key:默认值},"green/blue/orange":[参数key分组]}, ...]}` → 接头类型语义字典（20+ 类型：对接 32/微对接 33/左搭接 16/右搭接 17/V坡口 49/平板 80/直线圆管 96 等）。`GetJointTypeName()` 取中文名，cmbJob 项显示 `JOB 1 [对接]`、ILAlgoPage 顶部显示当前接头类型。`display` 键为「该类型应显示的参数集」，green/blue/orange 为参数类别分组，后续 UI 拆分（相机参数 vs Job 算法参数）可据此过滤/着色。
- **注意**：JSON 由原生层生成，SDK C# 包装与官方 demo 均未读取——解析须自行实现（本项目用 Newtonsoft.Json，csproj 已引用 `3rdDepend\Newtonsoft.Json.dll`）；文件缺失/未连接时按「无线激光即无 Job」返回空，不缓存不兜底。

### 线程与资源
- 回调 `_cbInitJobParams` 存字段防 GC；`_jobLock` 保护 `_jobParams` 缓存；`System.Runtime.InteropServices.Marshal.SizeOf` 全限定（规避 SDK `Marshal` 遮蔽，同轮廓读法）。
- `Make64Bytes`/`Read64Bytes` 处理 64 字节 ASCII 缓冲（不足补 0、超长截断、遇 NUL 终止），严格遵循 [[api/IntelligentLaserSDK_CSharp_DevManual]] §6 的 64 字节缓冲约束。

### ⚠️ 字段名待 VS x64 构建确认（QA P0）
`TIntelligentJobParamsGroup.__Internal` 与 `TIntelligentJobParam.CurValue` 的具体 CppSharp 生成成员名（`StParamArray`/`SzParamName`/`CurValue.SzValue`/`CurValue.FValue`/`CurValue.DwValue`/`value_Range.float_range.FloatMin` 等）以开发手册 §6 文档形状为准，**首次使用此类类型**；需在 VS x64 构建中确认字段名与 union 布局，必要时按生成代码微调。`IntelligentLaserCameraRun.cs` 已加 `// QA P0` 注释标注。详见 [[lessons/IntelligentLaser-Pitfalls]]。

## 关键设计

- **手动/自动统一封装（2026-08-17）**：`ConnectCore(ip)` 是唯一连接入口（InitSDK→**注册回调**→ConnectToSensor→Core 校验，2026-08-18 修正顺序），`OpenSensor`（自动全开）与 `ConnectManual`（手动只连）均复用；`OpenSensor` 开外设也复用 `SetLaser`/`SetCaptureCamera`/`SetSensor` 同一套封装，不再直接调 SDK。手动/自动共用一套函数，手动仅多 `ScanSensors`（扫描 IP）能力。
- **回调常驻 + 三层 GC 保护（2026-08-20 升级）**：三个 SDK 回调委托（`MillionOutlineInspect` / `InternalRefCornerPts` / `RecvInitJobParamsInfo`）各有独立 `GCHandle` 钉住（`_hCbMillionOutline` / `_hCbInitJobParams` / `_hCbCalibration`），不再仅依赖 `_hostHandle` 钉住 `this` 间接保活；`GCHandle.Alloc(this)` 仍保留作 `pUser` 传入注册；三个回调方法末尾加 `GC.KeepAlive(this)` 防 JIT 提前回收；释放路径全覆盖（`ReleaseNativeResources` / `ConnectCore` 失败 / `DisconnectManual` / `RegisterCallbacks` 重试清理），统一由 `FreeCallbackHandles()` 释放委托句柄。彻底根治 `CallbackOnCollectedDelegate` MDA。详见 [[lessons/IntelligentLaser-Pitfalls]] 第 6 章。
- **回调释放竞态防护（2026-08-20 下午，第四层防御）**：新增 `_activeCallbacks` 引用计数器（`Interlocked.Increment/Decrement` + `try/finally`），三个回调均参与计数；新增 `WaitForCallbacksToFinish()` 自旋等待归零（超时 2s，超时记警告仍继续释放避免死锁）；`DisconnectManual` / `ReleaseNativeResources` 在关传感器 + 反初始化 SDK 后、释放委托 GCHandle 前等待回调归零 + `Thread.Sleep(50)`，消除「关传感器→释放委托」之间在途回调触发 `CallbackOnCollectedDelegate` 的竞态窗口。高帧率下回退中在途回调更多，此层防御尤为关键。详见 [[lessons/IntelligentLaser-Pitfalls]] 第 6 章。
- **务必 Dispose 回调包装**：`__GetOrCreateInstance` 拿到的是拥有原生内存的包装对象，必须 `using` 释放，否则 100Hz 下每帧泄漏（见 [[api/IntelligentLaserSDK_CSharp_DevManual]] 第 4 条约定）。所有原生字段读取在 `using` 块内完成，`Mat` 在块外由托管 `PointCloudData` 生成。
- **raw-Marshal 规避 GC 压力**：弃用 `ContourData.PointArray` 的托管 getter（每帧 `new` 2048 个 FPoint 包装），改用 `contour.__Instance` 基址 + `IntPtr.Add` + **全限定 `System.Runtime.InteropServices.Marshal.Copy` + `System.BitConverter.ToSingle`** 直接读 `FPoint`（y@0 / z@4），读完即走（彻底规避 SDK 命名空间遮蔽 BCL `Marshal` 的编译错误，见 [[lessons/IntelligentLaser-Pitfalls]]）。
- **SDK 自有算法结果捕获（InspectResult）**：同一 `MillionOutlineInspect` 回调在读取轮廓后，额外在 `using` 块内读取 `inspect.InspectResult[0]`（`RuntimeInspectResult`：ParseRes / CurrentFeaturePoint.YPos-ZPos(mm) / Width[2] / HeightOrDepth[2] / Area / Angles[3] / Radii[2] / Vec[2] / Timestamp），拷贝进线程安全快照 `IlInspectResult`（双锁 `_ilLock` 保护 `_lastInspect`/`_hasInspect`），经 `HasInspectResult`/`LastInspectResult` 暴露。工作流 `AnalyzeImage()` 据此走英莱自有算法路线（详见下方「算法路线分支」）。
- **轮廓 Mat 复用持久画布（2026-08-26 重构）**：`ConvertContourToMatDemo` 不再每帧 `new Bitmap`/`new Graphics`/`new Mat`。改为**复用持久 `_canvasBmp`(834×554)+`_canvasG`**（`EnsureCanvas()` 首次创建）每帧 `Clear` 重绘，并通过 `UpdateCurrentMatFromCanvas()` 把画布 `CopyTo` 进**持久 `_currentMat`**（首帧新建、后续原地复用，同尺寸/类型零新分配）。整段绘制在 `lock(_matLock)` 内执行，与 `CurrentMat` getter 互斥，且避免回调并发重入；销毁路径 `_matLock` 内同步 `Dispose` 画布，无 GDI 句柄泄漏。采用 `Bitmap.ToMat()`+`Mat.CopyTo()`（Emgu.CV 4.x 确定性 API），版本安全。回调手动分支因此移除旧「双缓冲换帧（`newMat` 交换 + 旧帧 `Dispose`）」，由方法内部原地更新 `_currentMat` 天然替代。
- **回调驱动显示（2026-08-17）**：`MillionOutline` 回调成功换帧后调 `NotifyFrameReady()`，按 ~20fps（50ms 节流）触发 `ContourFrameReady` 事件，由 `ILCamPage`（轮廓画面）/`ILAlgoPage`（实时识别结果）订阅后经 `InvokeRequired` 封送到 UI 线程刷新——**替代此前 UI 层 `Timer` 轮询显示**。与英莱官方 demo 一致：**回调更新画面，轮询只用于查状态**（见 [[lessons/IntelligentLaser-Pitfalls]]）。
- **校准数据双回调（2026-08-17）**：`RegisterCallbacks()` 在轮廓回调之外额外注册 `InternalRefCornerPts` 校准回调（`_cbCalibration` 存字段防 GC），`CalibrationCallback` 在 `using` 块内把 `IntelligentCalibrationInfo`（中心点+4角点）拷贝进 `IlCalibrationInfo` 快照（`_calibLock` 保护）。`ConvertContourToMatDemo` 改为实例方法读取校准数据：有校准数据时按 demo `resetInnerData`/`TransPoint`/`Paint` 绘制**黄色校准框 + 浅灰大十字架 + 浅绿角点/中心点 + 红色特征点**，轮廓折线按像素/mm 比例映射；无校准数据回退自动缩放画法。
- **连接位掩码（Core 未连=硬失败）**：`ConnectToSensor` 返回位掩码。`EM_INTELLIGENT_CONNECT_E_CORE` 位为 1 表示 Core 服务未连上 → **视为硬失败**：记录 `Error` 日志、`UnInitSDK()` 清理、直接返回（不置 `_isConnected`/`_isOpened`），避免状态栏假阳性「已连接」。仅当 Core 连上时才继续启用传感器/激光/采集相机。

## 算法路线分支（英莱自有算法）

英莱 SDK 自带算法与反馈，`IntelligentLaserCameraRun` 将每帧 `InspectResult[0]` 捕获为 `IlInspectResult` 快照。工作流 `LineLaserWorkflow.AnalyzeImage()` 据此分支（详见 [[api/LineLaserWorkflow]]）：

- **英莱 + `ParseRes==1`（有有效识别）**：直接以 `IlInspectResult` 构造 `SeamFeatureResult`（FeatureY→CenterY、FeatureZ→CenterX、平均 Width→SeamWidth、Area→SeamArea），经 `PipelineManager.ReportExternalResult(...)` 复用类级 `_completedArgs` 触发 `AlgorithmCompleted`，下游 `WeldProcess`/`MotionControlWorkflow` 照常消费焊缝特征；**不再运行 Emgu 通用管线**，满足"启用英莱相机时算法走自己路线"的诉求。显示沿用当前轮廓帧（`_lastResultMat = _lastAcquiredMat`）。
- **英莱但 `ParseRes!=1`（本帧无有效识别）/ 其他相机**：回退 `PipelineManager.Instance.Execute(_lastAcquiredMat, robotX)` 通用 Emgu 管线，与 SmartRay/Virtual 一致。
- 坐标映射（FeatureY/Z → CenterY/X）为按物理 mm 的初步对齐，具体标定关系需现场复核（见交付报告已知局限）。

## 接入点（CameraSelector）

- `CameraKind.IntelligentLaser = 4`（在 [[api/ICameraRun]] 同文件枚举新增）。
- `CameraSelector.SelectIntelligentLaser()`：懒创建 `IntelligentLaserCameraRun` 并激活，`Kind=IntelligentLaser`。
- `CameraSelector.ConnectionState`：`IntelligentLaser` 分支按 `_intelligentInstance.IsConnected` 派生 Connected/Disconnected。
- `CameraSelector.DetectConnection()`：`IntelligentLaser` 分支懒创建并 `OpenSensor("192.168.178.210")`（IP 硬编码 TODO，待从 `Config/INI/CameraPresets.ini` 读取，与其他相机一致）。
- `CameraSelector.Load()`：读 `Camera/Type==4` 时 `SelectIntelligentLaser()`，持久化复用现有 `CameraSelector.ini`。
- **UI 选择**：`LLCamWorkJob.cmbCameraSelect` 下拉框新增「英莱相机(IntelligentLaser)」项（index 2）；`SelectedIndexChanged` 调 `SelectIntelligentLaser()` 并 `CameraSelector.Save()`（持久化到 `Config/INI/CameraSelector.ini` 的 `Type=4`）；`UpdateStatusDisplay`/`UpdateFrameRateDisplay` 增加英莱相机状态与帧率显示。
- **工作流启动**：`LineLaserWorkflow.Start()` 相机选择逻辑新增 `CameraSelector.Kind == CameraKind.IntelligentLaser` 分支——模拟模式仍强制虚拟，生产流程尊重用户选择（不再强行回退 SmartRay）；`InitializeWorker()` 后台初始化线程新增 `camera is IntelligentLaserCameraRun` 分支，调用 `SensorRunContinue()`（内部幂等 `OpenSensor(默认IP)`）使相机进入 Standby，**修复此前对英莱强转 `(CameraRun)` 抛 `InvalidCastException` 导致无法启动**；取图链 `AcquireImage` 仍经 `CameraSelector.Active`，**零改动**。

## 构建与部署（必读）

- **x64 硬性要求**：原生 `IntelligentLaser.dll` 为 64 位，`AdaWeldSystem.csproj` 已把 `Release|AnyCPU` 的 `PlatformTarget` 改为 `x64`（Debug 早已是 x64），避免 32 位进程加载 64 位 DLL 抛 `BadImageFormatException`。
- **托管引用**：`IntelligentLaser_CSharp.dll`、`CppSharp.Runtime.dll`（SDK 运行库依赖），均 `<Private>True</Private>` 拷贝到输出。
- **原生依赖**：`Libs/IntelligentLaser/native/` 下 10 个 DLL（IntelligentLaser.dll + SDL2/av*/jsoncpp 等 FFmpeg/SDL 依赖）经 csproj `<None Link=... CopyToOutputDirectory=PreserveNewest>` **扁平化拷贝到输出根目录**，满足 `DllImport("IntelligentLaser")` 与同目录依赖搜索。
- 详见 [[api/IntelligentLaserSDK_CSharp_DevManual]]「0. 概述与部署」。

## 与现有相机对比

| 维度 | SmartRay | Virtual | **IntelligentLaser** |
|------|----------|---------|----------------------|
| 实现类 | `SmartRayCameraRun.CameraRun` | `VirtualCam.VirtualCameraRun` | `IntelligentLaserCam.IntelligentLaserCameraRun` |
| 数据来源 | SRAPI 回调(3D 点云) | 自生成轮廓 | `MillionOutlineInspect` 回调(mm 轮廓 FPoint) |
| 接入工作流 | 是 | 是 | **是（同链路）** |
| 启动检测 | `OpenSensor(ip,"40")` | 跳过 | `OpenSensor(ip)` |
| 默认 IP | 192.168.178.200 | — | 192.168.178.210 |

---

## 编译陷阱（.NET Framework 4.8 实测）

1. **`Mat` 类型歧义 → `CurrentMat` 无法实现接口**：本模块 `using IntelligentLaser_CSharp;`，而该 SDK 命名空间**自身也导出 `Mat` 类型**。若不消除歧义，类内 `Mat` 会被解析为 `IntelligentLaser_CSharp.Mat`，与 `ICameraRun.CurrentMat`（要求 `Emgu.CV.Mat`）不一致，报 *"does not implement interface member / no matching return type of Mat"*。
   - ✅ 修复：类内所有 `Mat` 使用**全限定名 `Emgu.CV.Mat`**（字段 `_currentMat`、`CurrentMat` 属性等），**不要**加 `using Emgu.CV;`（否则 `Mat` 变成两命名空间二义性）。

2. **`Marshal.ReadFloat` / `Marshal.ReadSingle` 均不存在（根因：SDK 命名空间遮蔽 BCL `Marshal`）**：本模块 `using IntelligentLaser_CSharp;` 且 `using System.Runtime.InteropServices;`，而 **SDK 命名空间自身也导出 `Marshal` 类型**，会遮蔽（shadow）BCL 的 `System.Runtime.InteropServices.Marshal`。裸写 `Marshal.ReadFloat`/`ReadSingle` 实际解析到 SDK 的 `Marshal`（二者该方法都无），报 *"Marshal 未包含 ReadFloat/ReadSingle 的定义"*。此前把 `ReadSingle`→`ReadFloat` 的修改**未触达根因**（同被遮蔽）。
   - ✅ 修复：使用**全限定 BCL** `System.Runtime.InteropServices.Marshal.Copy(IntPtr, byte[], int, int)` 拷贝 8 字节到 `byte[8]`，再用 `System.BitConverter.ToSingle(buf, 0/4)` 取 y/z（float@0 / float@4）。全限定名绕过 `using` 解析、命中 BCL，彻底规避遮蔽。详见 [[lessons/IntelligentLaser-Pitfalls]]。
   - raw-Marshal 提取 FPoint：`System.Runtime.InteropServices.Marshal.Copy(fp, buf, 0, 8); float y = System.BitConverter.ToSingle(buf, 0); float z = System.BitConverter.ToSingle(buf, 4);`

*来源：AdaWeldSystem/LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs*
