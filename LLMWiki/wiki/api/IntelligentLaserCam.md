---
title: IntelligentLaserCam API 参考
date: 2026-07-24
tags: [API, 相机, 英莱, 线激光, ADR-038, ADR-039]
source: AdaWeldSystem/LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs
---

# IntelligentLaserCam API 参考

> 英莱(IntelligentLaser / ANLE) 工业 3D 线激光相机运行控制，位于 `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs`（2026-09-08 由 `IntelligentLaserCameraRun.cs` 改名，与目录同名），命名空间 `AdaWeldSystem.LineLaserCam.IntelligentLaserCam`（**2026-09-08 类名同步改为 `IntelligentLaserCam`，与文件/目录同名**）。
> **2026-09-08（ADR-038）**：本类由实现 `ICameraRun` 改为**继承 `LineLaserCameraBase`**（`LineLaserCam/ILineLaser/`，相机键名「英莱线激光」），
> 实现 [[api/LineLaserManager]] 的三层契约，与 `VirtualCam.VirtualCameraRun` 可互换注入 `LineLaserWorkflow`；取图链（`LineLaserManager.Instance.Active`）零改动。
> ⛔ 旧 `CameraSelector` / `SmartRayCam.CameraRun` 已删除。
>
> **2026-09-08 二次分工（ADR-039）**：本类**只做回调触发，不做业务处理**。已删除 ⛔`ConvertContourToMatDemo`/画布/`_currentMat`、⛔`IsManualMode`、⛔`ContourFrameReady`/`ContourDataReady`/`ContourDataEventArgs`、⛔`NotifyFrameReady`/`EnsureCanvas`/`CalcTwoLineCrossPoint`、⛔`IlInspectResult`/`IlCalibrationInfo`；
> 新增/改型：`LastInspectResult` → `LineLaserSeamResult`（struct）、`Calibration` → `LineLaserCalibration`，回调尾部只调 `RaiseResultReady(snapResult, fps)` + `RaiseProfileReady(cloud, fps)`。
> 业务（PVT 点下载 / Mat 生成 / 快照刷新）全部上移 [[api/LineLaserManager]]，绘制上移 [[api/ProfileMatRenderer]]。文件 1746 行 → 1324 行。
> SDK 包装为厂商 CppSharp 生成的 `IntelligentLaser_CSharp.dll`（.Net Framework 构建，供 .NET 4.8），无需手写 P/Invoke。开发手册见 [[api/IntelligentLaserSDK_CSharp_DevManual]]。

## 数据链路

```
MillionOutlineInspect 回调（原生线程）— ADR-039 后只做三件事
   → IntelligentMillionOutlineInspect.__GetOrCreateInstance(pOutlineData)  [务必 using 释放]
   → inspect.ContourData.PointArray[]（托管 FPoint[]，CppSharp 封装）→ raw-Marshal 直接读 y@0/z@4
   → ① PointCloudData.AddPoint(0, YPos, ZPos)               [托管点云]
   → ② InspectResult[0] → LineLaserSeamResult 快照（_ilLock 保护）
   → ③ _acquisitionCompletedSignal.Set()
        → RaiseResultReady(snapResult, _measuredFps)   [结果处理 → Manager: PVT 点下载]
        → RaiseProfileReady(cloud, _measuredFps)       [轮廓处理 → Manager: 记录/快照/显示 Mat]
   → 返回（回调内不做绘制、不做业务）

InternalRefCornerPts 回调（原生线程，校准数据）
   → IntelligentCalibrationInfo.__GetOrCreateInstance(fRegioninfo)  [务必 using 释放]
   → 拷贝 中心点 + 4 角点（mm）到中性快照 LineLaserCalibration（_calibLock 保护）
   → 经 override Calibration 属性暴露，供 LineLaserManager 调 ProfileMatRenderer 绘制校准框/十字架
```

> ⛔ **2026-09-08 删除（ADR-039）**：原链路中的 `ConvertContourToMatDemo`（GDI+ 绘制 → 持久画布 → `CopyTo` 原地更新 `_currentMat` → `NotifyFrameReady()` → `ContourFrameReady`）**已整段移除**，绘制逻辑上提 `LineLaserCam/ProfileMatRenderer.cs`（画布一次分配、终身复用，`Render(cloud, calib, result)` 返回 Mat）；显示开关由 `LineLaserManager.SetDisplayOptions(enabled, fps, convert)` 控制，默认关闭。

与 Virtual 同构：二者均继承 `LineLaserCameraBase`，Manager 与工作流只认基类契约，可互换。

> ⚠️ **三层控制完全解耦（2026-08-18 用户澄清）**：`SetSensorEnable(true)` 是 `MillionOutlineInspect` 回调的**触发源头**——传感器使能后回调即持续出数据；`SetLaserEnable` 仅控制物理激光照射，与回调触发**无任何关系**（激光未开时回调仍正常触发，只是轮廓数据可能无有效激光线）；`SetSensorCaptureCameraEnable` 仅影响 YUV 预览回调。`OpenSensor` 中 `SetSensor/SetLaser/SetCaptureCamera` 为三个独立并列调用，`MillionOutlineCallback` 内不检查激光状态。见 [[lessons/IntelligentLaser-Pitfalls]]。

## 成员

| 成员 | 说明 |
|------|------|
| `bool IsConnected { get; }` | 是否已连上硬件（`OpenSensor` 成功后置 true）；供 `CameraSelector.ConnectionState` 派生「已连接」 |
| `double ScanRateHz { get; }` | 当前采集扫描率(Hz)。**2026-08-20 升级为运行时实时刷新**：`MillionOutlineCallback` 中每 500ms 从 `FetchSensorFps` 读取一次硬件实际帧率并更新，反映传感器运行时的实时采集分析频率。此前仅在 `OpenSensor` / `ApplyFrameRateModel` / `DetectHardwareStatus` 三个时机更新。工作流据此缩放 `WaitOne` 超时。**注意**：SDK 调用 `dwInstanceId` 必须为 1（默认值），传 0 会返回 `INTELLIGENT_E_UNINIT` 导致读不到帧率 |
| ~~`Mat CurrentMat`~~ | **2026-09-08 上提基类（ADR-039）**：由 `LineLaserCameraBase.CurrentMat` 承载（`lock(_matLock)` + `Clone()` 返回），本类不再持有 `_currentMat`/画布；写入口改为基类 `UpdateDisplayMat(Mat)`（由 `LineLaserManager` 调 `ProfileMatRenderer` 生成后回写，Dispose 时传 null 释放）。⛔ 原「持久复用 Mat + 画布 Clear 重绘」实现已删 |
| `void OpenSensor(string ip)` | 一键全开（自动工作流用）。幂等：复用 `ConnectCore` 连接 → 复用 `SetSensor(true)`/`SetLaser(true)`/`SetCaptureCamera(true)` 分步开外设 → 设 STANDERD(60Hz) → FetchSensorFps。默认 IP `192.168.178.210`。幂等判断由 `_isOpened` 改为 `_isConnected`（2026-08-25 状态精简） |
| `void SensorRunContinue()` | 未打开则先 `OpenSensor(DefaultSensorIp)`；未运行时 `SetSensor(true)`（2026-08-25 起经统一封装更新本地 `_isCameraOn`，弃直接 SDK 调用） |
| `void SensorStop()` | `SetSensor(false)`，保留 SDK 初始化（2026-08-25 起经统一封装） |
| `bool IsRunning { get; }` | **2026-08-25 派生化**：`=> _isCameraOn`（ICameraRun 接口契约保留；`_isRunning` 字段已删） |
| `void Dispose()` | 按顺序关外设→`UnInitSDK`→释放 GCHandle→释放 `_currentMat`→`GC.SuppressFinalize`。**2026-08-25 释放优化**：外设关闭归集 `ShutdownPeripherals()`（幂等 `_peripheralsOff` 防护，与 `DisconnectManual` 共用，避免重复 SDK 调用/回调等待）；回调等待超时 2000→500ms（回调源先停，在途回调快速归零）；`ReleaseNativeResources` 幂等 `_released` 防护（Dispose/析构只完整执行一次）（遵循 [[decisions/ADR-001-DisposePattern]]，未重写 `Dispose(bool)`） |
| `~IntelligentLaserCameraRun()` | **析构函数（finalizer，2026-08-14 新增）**：调 `ReleaseNativeResources()` 按序释放 SDK 非托管资源（幂等 `_released` 防护，Dispose 已执行则跳过），不触碰托管对象（如 `_currentMat`） |
| `bool ConnectManual(string ip)` | **2026-08-14 新增**：分步手动连接——复用 `ConnectCore` 只连接（**不开传感器/激光/相机**）；与 `OpenSensor`（一键全开）**共用同一套 `ConnectCore` 连接逻辑**，供英莱相机页面 `ILCamPage` 分步控制；**`CameraSelector.DetectConnection` 英莱分支亦改调此方法（启动只连接，不开激光/相机）** |
| `private bool ConnectCore(string ip)` | **2026-08-17 新增（私有，手动/自动统一封装）**：**首次连接**才 InitSDK→注册回调→ConnectToSensor→Core 连通校验；重连仅 ConnectToSensor。**回调委托只注册一次、全程存活**（2026-08-20 优化，与 demo 做法一致），避免频繁连接断开导致 CallbackOnCollectedDelegate。成功置 `_isConnected=true` + 重置 `_peripheralsOff` + `SyncHardwareStatus()`。**回调必须在连接前注册**（2026-08-18 修正）：SDK 连接完成时一次性触发 `InternalRefCornerPts`（校准框）与 `RecvInitJobParamsInfo`（Job 参数元数据）回调，注册晚了两个回调都会丢失。`OpenSensor` 与 `ConnectManual` 均复用此方法 |
| `bool ConfigureDefaultCommPeriod()` | **2026-08-20 新增**：配置默认回调周期（SetSensorCommPeriod），参数：DwSendCycle=10ms / DwBufferDuration=1000ms（英莱技术支持建议）。**仅首次配置有效**（`_commPeriodConfigured` 标志防重复），后续连接/重连不重复设置。仅在 `LineLaserWorkflow.InitializeWorker` 初始化成功后调用一次；手动连接不调用。返回 true=配置成功，false=已配置过或未连接或失败 |
| ~~`static string LoadSavedIp()`~~ | **2026-09-08 移除**：改由 `LineLaserManager.Instance.Config.SensorIp` 读取（`Config/XML/LineLaserConfig.xml`） |
| ~~`static void SaveSensorIp(string ip)`~~ | **2026-09-08 移除**：改为赋值 `LineLaserManager.Instance.Config.SensorIp` 后调 `SaveConfig()` |
| `string SensorIp { get; set; }` | **2026-09-08 新增**：相机 IP，由 `LineLaserManager.ApplyConfig()` 套用；`SensorRunContinue()` 未连接时按此 IP 打开，默认 `192.168.178.210` |
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
| ~~`bool IsManualMode`~~ | **2026-09-08 已删除（ADR-039）**：模式分支不再由相机层承担。显示与否改由 `LineLaserManager.SetDisplayOptions(enabled, fps, convert)` 控制（`DisplayEnabled` 默认 false） |
| `bool IsLaserOn()` | 激光状态。**2026-08-25 起本地状态**：`_isConnected && _isLaserOn`（连接时 `SyncHardwareStatus` 同步 + `SetLaser` 更新，UI 读取无延迟；弃每次 `FetchLaserStatus` 硬件查询） |
| `List<string> GetJointTypeDisplayKeys(int jointType)` | **2026-08-25 新增**：该接头类型应显示的参数键集（jointtypelist.json `display`，技术员确认的 Job 实际使用参数）；供 `ILAlgoForm` 参数表过滤 |
| `int LastContourPointCount { get; }` | 最近一次毫米轮廓点数量（MillionOutline 回调内更新，供页面显示轮廓点数） |
| `LineLaserCalibration Calibration { get; }` | **校准数据快照（2026-09-08 改型，ADR-039）**：`override` 基类虚属性，返回中性结构 `LineLaserCalibration`（`ILineLaser/`，Center + 4 角点，mm，`[0]=Y 横向 / [1]=Z 高度`，`HasData` 标记）。由 `InternalRefCornerPts` 回调填充（`_calibLock` 保护）。⛔ 原 `IlCalibrationInfo`/`CalibrationInfo` 已删除。供 `LineLaserManager` 调 [[api/ProfileMatRenderer]] 绘制校准框/十字架 |
| ~~`event EventHandler ContourFrameReady`~~ | **2026-09-08 已删除（ADR-039）**：显示事件改由业务层发出——`LineLaserManager.MatUpdated`（`LineLaserMatEventArgs`），`ILCamPage` 订阅之。原节流 ~20fps（50ms）逻辑随之删除 |
| ~~`event EventHandler<ContourDataEventArgs> ContourDataReady`~~ | **2026-09-08 已删除（ADR-039，拆为两个中性回调）**：改为 `LineLaserCameraBase` 的 `ResultReady`（`LineLaserResultEventArgs`，带 `LineLaserSeamResult` + 实测帧率）与 `ProfileReady`（`LineLaserProfileEventArgs`，带 `PointCloudData` + 实测帧率）。二者在回调尾部无条件触发（原「自动模式才外传」的分支取消），由 `LineLaserManager` 注册并处理：`ResultReady` → `SeamPvtFeeder` 下载 Y 轴 PVT 点；`ProfileReady` → 记录入库 + 快照刷新 + 显示 Mat。⛔ 直接订阅本类事件的旧写法（`LineLaserWorkflow` / `MainPage`）已全部改订阅 `LineLaserManager` |
| `int FetchCurrentJobId()` | 获取当前 JOB ID（`FetchJobInfo`；⚠️ dwCmd=0 查询语义待真机验证） |
| `List<IlJobDescInfo> FetchJobList()` | **2026-08-24 新增**：读取运行目录 `IntelligentLaser_jobdesclist.json`（连接相机后原生 SDK 自动落盘，**这是「全部 Job 号」的官方数据源**，SDK 无枚举 API 但落盘 JSON 提供），返回全部 Job 描述（Id/JointType/JobDescribe）；文件缺失/解析失败返回空列表，不缓存不兜底 |
| `IlJobDescInfo GetCurrentJobInfo()` | **2026-08-24 新增**：当前 JOB 完整描述（`FetchCurrentJobId` + `FetchJobList` 按 id 匹配）；未连接/查不到返回 null。供 UI 展示当前 JOB 与接头类型 |
| `string GetJointTypeName(int jointType)` | **2026-08-24 新增**：从运行目录 `IntelligentLaser_jointtypelist.json` 查询接头类型中文名（如 32=对接、16=左搭接）；文件缺失/未命中返回 null。实现复用 `FetchJointTypes()` 按 `Int` 匹配 |
| `List<IlJointTypeInfo> FetchJointTypes()` | **2026-08-24 新增**：读取运行目录 `IntelligentLaser_jointtypelist.json` 返回**全部接头类型**（`Int` 编号 + `NameZh` 中文名），供新建 JOB 弹窗枚举可用类型；文件缺失/解析失败返回空列表 |
| `int SwitchJob(int jobId)` | 切换 JOB（`SetSensorJobInfo` + `EmJobSettingCmd.SWITCH`） |
| `int CreateJob(int jointType, string desc)` | 新建 JOB（`SetSensorJobInfo` + `CREATE` + 焊缝类型 + 备注） |
| `int DeleteJob(int jobId)` | 删除 JOB（`SetSensorJobInfo` + `DELETE`） |
| `LineLaserSeamResult LastInspectResult { get; }` | 最近一次英莱 SDK 算法解析结果快照（线程安全拷贝）。**2026-09-08 类型改型（ADR-039）**：由 `IlInspectResult`（class）改为中性 **struct** `LineLaserSeamResult`（`ILineLaser/LineLaserEventArgs.cs`），字段 `Valid`/`ParseRes`/`ErrorCode`/`Timestamp`/`FeatureY`/`FeatureZ`/`Width0/1`/`Height0/1`/`Area`/`AverageWidth`，无效工厂 `LineLaserSeamResult.Invalid(parseRes, errorCode)`。⛔ `IlInspectResult` 已删除；判有效改为 `r.Valid`（原 `HasInspectResult == true`） |
| ~~`bool HasInspectResult`~~ | **2026-09-08 已删除（ADR-039）**：有效性并入 struct 的 `Valid` 字段（`_lastInspect.Valid`），避免双字段不一致 |
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

> 相机参数编辑 UI 为 `Sub3UI/ILParamForm`（Table 单元格编辑曝光/激光强度/抗弧光）；Job 参数编辑在 `Sub3UI/ILAlgorithmEditForm` 模块 B（`ILAlgoForm`）。

## 校准数据（InternalRefCornerPts，显示画面）

英莱相机在 `RegisterCallbacks()` 中额外注册 `IntelligentRegisterCallBack_InternalRefCornerPts` 校准回调（`_cbCalibration` 存字段防 GC），捕获**校准框（矩形区域）+ 大十字架**所需的几何数据（参照官方 demo `Form1.cs:572` `intelligentInternalRefCornerPtsCallBackCSharp`）。

> ⚠️ **回调注册时机（2026-08-18 修正）**：`RegisterCallbacks()` 必须在 `ConnectToSensor` **之前**调用。SDK 在连接完成时**一次性触发** `InternalRefCornerPts` 校准回调，若注册在连接之后，该回调丢失 → 校准框/十字架永不显示。官方 demo 顺序为 `InitSDK → 注册全部回调 → ConnectToSensor`（Form1.cs:84/103-108/164）。详见 [[lessons/IntelligentLaser-Pitfalls]]。

### 数据契约 LineLaserCalibration（ADR-039 起）

⛔ 原命名空间级 `IlCalibrationInfo` 已删除，改为 `ILineLaser/LineLaserCalibration.cs` 的中性结构（业务层不依赖厂商类型）。字段对齐 SDK `IntelligentCalibrationInfo`：`Center`（中心点）+ `LeftTopCorner`/`RightTopCorner`/`LeftBottomCorner`/`RightBottomCorner`（4 角点），坐标均为**物理 mm** 的 `float[2]`，`[0]=Y 横向 / [1]=Z 高度`；`HasData` 标记是否已收到有效校准数据。由 `CalibrationCallback` 在 `using` 块内拷贝（务必 Dispose 包装对象），`_calibLock` 保护换入快照，`Calibration` 属性（`override`）线程安全读取。构造函数两款：空结构、`(center, lt, rt, lb, rb)` 全量。

### 绘制（已上提 ProfileMatRenderer，ADR-039）

⛔ `ConvertContourToMatDemo` 及约 250 行 GDI 绘制、**`CalcTwoLineCrossPoint` 已从本类删除**，上提为 `LineLaserCam/ProfileMatRenderer.cs`（`Render(PointCloudData cloud, LineLaserCalibration calib, LineLaserSeamResult result)` → `Mat`，画布一次分配终身复用，`LastMat` 取最近帧）。绘制内容不变（校准框 / 大十字架 / 角点 / 特征点 / 轮廓折线 / mm 虚线刻度 / 无校准回退），调用方为 `LineLaserManager`：
- **比例换算**：`rate = min((w-2*margin)/cornerW, (h-2*margin)/cornerH)`（cornerW/H 由角点差求得，同 demo）。
- **居中（2026-08-18 终版）**：**恢复 demo 原版角点公式 `center ± |corner*rate|`，仅改 `center = (w/2, h/2)`**（弃用 demo 的 `fPersent/dwOffset` 计算）。`trans(y,z) = (center.X + y*rate, center.Y - z*rate)` 同 demo。mm 原点(0,0) 在图像中心，十字交叉居中，轮廓负值 mm 向两侧展开。
  - ⚠️ 演进记录：初始 demo 的 `fPersent/dwOffset` 计算使十字未对齐图像中心；前三轮改动（矩形折叠/originX 间接映射/halfExtent 相对偏移）均偏离 demo 正确公式。**终版：demo 原版公式 + 仅改 center 为图像中心**。见 [[lessons/IntelligentLaser-Pitfalls]]。
- **校准框**：`FillPolygon` 深色背景（`0x3B3B3B`）+ `DrawPolygon` 黄色边框（2px）。
- **大十字架**：水平线（过中心点向右 100px）与左右边交点、垂直线（过中心点向下 100px）与上下边交点，经 `CalcTwoLineCrossPoint` 求交后 `DrawLine` 浅灰色（2px）——十字线裁剪到校准框四边。
- **角点/中心点**：浅绿圆点（6px 直径）；**特征点**：`ParseRes==1` 时红色 8px 方块（`trans(FeatureY, FeatureZ)`）。
- **轮廓折线**：按 `trans(y,z) = (center.X + y*rate, center.Y - z*rate)` 映射物理坐标到屏幕（绿色 1.5px），mm 原点(0,0) 在图像中心。
- **mm 虚线刻度栅格（校准模式，画在最上层）**：原点(0,0) 在图像中心，`stepMm=max(1, round(40/rate))`，垂直网格 `screen_x = center.X + mm*rate`、水平网格 `screen_y = center.Y - mm*rate`；底部/左侧 8.5px 灰色宋体标注 mm 值。

无校准数据时回退原自动缩放画法（网格 + 折线 + Y/Z 轴标签）。⛔ `CalcTwoLineCrossPoint`（线段交点辅助，对应 demo `Form1.cs:659`，平行返回 `(-1,-1)`）已随绘制代码上提 `ProfileMatRenderer` 私有方法。

> ⚠️ **2026-09-08 修正（ADR-039 落地时）**：大十字架的**中心点改为图像中心** `center = (w/2, h/2)`（原 renderer 沿用 demo 的 `fPersent/dwOffset` 推导，未真正居中）；角点公式仍为 demo 原版 `center ± |corner*rate|`。

## Job Parameter（英莱算法参数）

英莱相机自带一套**设备侧 Job Parameter**（焊缝接头种类、特征点、向量等算法参数，名称/类型/范围由 SDK 初始化回调下发，**不硬编码**），与 EmguALG 的 `PipelineConfig`（项目算法参数）是两套完全不同的参数体系。二者已合并进同一 UI 窗体 `Sub3UI/ILAlgorithmEditForm`（见 [[api/ILAlgorithmEditForm]] 模块 B），但后端由本类以 `IlJobParamInfo` 托管缓存封装，**UI 绝不直连 `IntelligentLaser_export`**（呼应 [[api/IntelligentLaserSDK_CSharp_DevManual]] §7「参数读写封装进相机模块」）。

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
- **`IntelligentLaser_jointtypelist.json`**：`{"joint_types":[{"hex":"0x10","int":16,"name_zh":"左搭接","name_en":"Left-Lap","lines":[...],"calculations":[...],"display":{参数key:默认值},"green/blue/orange":[参数key分组]}, ...]}` → 接头类型语义字典（20+ 类型：对接 32/微对接 33/左搭接 16/右搭接 17/V坡口 49/平板 80/直线圆管 96 等）。`GetJointTypeName()` 取中文名，cmbJob 项显示 `JOB 1 [对接]`、ILAlgoForm 顶部显示当前接头类型。`display` 键为「该类型应显示的参数集」，green/blue/orange 为参数类别分组，后续 UI 拆分（相机参数 vs Job 算法参数）可据此过滤/着色。
- **注意**：JSON 由原生层生成，SDK C# 包装与官方 demo 均未读取——解析须自行实现（本项目用 Newtonsoft.Json，csproj 已引用 `3rdDepend\Newtonsoft.Json.dll`）；文件缺失/未连接时按「无线激光即无 Job」返回空，不缓存不兜底。

### 线程与资源
- 回调 `_cbInitJobParams` 存字段防 GC；`_jobLock` 保护 `_jobParams` 缓存；`System.Runtime.InteropServices.Marshal.SizeOf` 全限定（规避 SDK `Marshal` 遮蔽，同轮廓读法）。
- `Make64Bytes`/`Read64Bytes` 处理 64 字节 ASCII 缓冲（不足补 0、超长截断、遇 NUL 终止），严格遵循 [[api/IntelligentLaserSDK_CSharp_DevManual]] §6 的 64 字节缓冲约束。

### ⚠️ 字段名待 VS x64 构建确认（QA P0）
`TIntelligentJobParamsGroup.__Internal` 与 `TIntelligentJobParam.CurValue` 的具体 CppSharp 生成成员名（`StParamArray`/`SzParamName`/`CurValue.SzValue`/`CurValue.FValue`/`CurValue.DwValue`/`value_Range.float_range.FloatMin` 等）以开发手册 §6 文档形状为准，**首次使用此类类型**；需在 VS x64 构建中确认字段名与 union 布局，必要时按生成代码微调。`IntelligentLaserCam.cs` 已加 `// QA P0` 注释标注。详见 [[lessons/IntelligentLaser-Pitfalls]]。

## 关键设计

- **手动/自动统一封装（2026-08-17）**：`ConnectCore(ip)` 是唯一连接入口（InitSDK→**注册回调**→ConnectToSensor→Core 校验，2026-08-18 修正顺序），`OpenSensor`（自动全开）与 `ConnectManual`（手动只连）均复用；`OpenSensor` 开外设也复用 `SetLaser`/`SetCaptureCamera`/`SetSensor` 同一套封装，不再直接调 SDK。手动/自动共用一套函数，手动仅多 `ScanSensors`（扫描 IP）能力。
- **回调常驻 + 三层 GC 保护（2026-08-20 升级）**：三个 SDK 回调委托（`MillionOutlineInspect` / `InternalRefCornerPts` / `RecvInitJobParamsInfo`）各有独立 `GCHandle` 钉住（`_hCbMillionOutline` / `_hCbInitJobParams` / `_hCbCalibration`），不再仅依赖 `_hostHandle` 钉住 `this` 间接保活；`GCHandle.Alloc(this)` 仍保留作 `pUser` 传入注册；三个回调方法末尾加 `GC.KeepAlive(this)` 防 JIT 提前回收；释放路径全覆盖（`ReleaseNativeResources` / `ConnectCore` 失败 / `DisconnectManual` / `RegisterCallbacks` 重试清理），统一由 `FreeCallbackHandles()` 释放委托句柄。彻底根治 `CallbackOnCollectedDelegate` MDA。详见 [[lessons/IntelligentLaser-Pitfalls]] 第 6 章。
- **回调释放竞态防护（2026-08-20 下午，第四层防御）**：新增 `_activeCallbacks` 引用计数器（`Interlocked.Increment/Decrement` + `try/finally`），三个回调均参与计数；新增 `WaitForCallbacksToFinish()` 自旋等待归零（超时 2s，超时记警告仍继续释放避免死锁）；`DisconnectManual` / `ReleaseNativeResources` 在关传感器 + 反初始化 SDK 后、释放委托 GCHandle 前等待回调归零 + `Thread.Sleep(50)`，消除「关传感器→释放委托」之间在途回调触发 `CallbackOnCollectedDelegate` 的竞态窗口。高帧率下回退中在途回调更多，此层防御尤为关键。详见 [[lessons/IntelligentLaser-Pitfalls]] 第 6 章。
- **务必 Dispose 回调包装**：`__GetOrCreateInstance` 拿到的是拥有原生内存的包装对象，必须 `using` 释放，否则 100Hz 下每帧泄漏（见 [[api/IntelligentLaserSDK_CSharp_DevManual]] 第 4 条约定）。所有原生字段读取在 `using` 块内完成，`Mat` 在块外由托管 `PointCloudData` 生成。
- **raw-Marshal 规避 GC 压力**：弃用 `ContourData.PointArray` 的托管 getter（每帧 `new` 2048 个 FPoint 包装），改用 `contour.__Instance` 基址 + `IntPtr.Add` + **全限定 `System.Runtime.InteropServices.Marshal.Copy` + `System.BitConverter.ToSingle`** 直接读 `FPoint`（y@0 / z@4），读完即走（彻底规避 SDK 命名空间遮蔽 BCL `Marshal` 的编译错误，见 [[lessons/IntelligentLaser-Pitfalls]]）。
- **SDK 自有算法结果捕获（InspectResult）**：同一 `MillionOutlineInspect` 回调在读取轮廓后，额外在 `using` 块内读取 `inspect.InspectResult[0]`（`RuntimeInspectResult`：ParseRes / CurrentFeaturePoint.YPos-ZPos(mm) / Width[2] / HeightOrDepth[2] / Area / Angles[3] / Radii[2] / Vec[2] / Timestamp），拷贝进线程安全快照 **`LineLaserSeamResult`**（`_ilLock` 保护 `_lastInspect`），经 `LastInspectResult` 暴露（⛔ `HasInspectResult` 已删，改用 `Valid`）。**ADR-039 后**：该快照在回调尾部直接作为 `RaiseResultReady` 的载荷交给 `LineLaserManager`（→ `SeamPvtFeeder` → Y 轴 PVT），不再等人来轮询。工作流 `AnalyzeImage()` 据此走英莱自有算法路线（详见下方「算法路线分支」）。
- ⛔ ~~**轮廓 Mat 复用持久画布（2026-08-26 重构）**~~：**2026-09-08 随绘制代码一并上提（ADR-039）**。`_canvasBmp`/`_canvasG`/`_matLock`/`EnsureCanvas`/`UpdateCurrentMatFromCanvas` 均已从本类删除；复用画布的责任转由 [[api/ProfileMatRenderer]] 承担（画布 + Mat 一次分配终身复用，`Dispose()` 统一释放，日志标签「线激光渲染器」）。本类 Dispose 内改为 `UpdateDisplayMat(null)` 交还基类。
- ⛔ ~~**回调驱动显示（2026-08-17）**~~：**2026-09-08 已删除 `NotifyFrameReady` / `ContourFrameReady`（ADR-039）**。现行两条显示路径：**手动 UI 页**（`ILCamPage`）订阅 `LineLaserManager.Instance.MatUpdated`（业务层在 `DisplayEnabled` 为真时才生成 Mat，故天然低频）；**主页面轮廓**改为**线程轮询** `LineLaserManager.Instance.Profile` 快照（33ms + 版本号比对），不再走相机回调——60Hz 回调直接压 UI 线程是原设计的隐患，见 [[decisions/ADR-039-LineLaserResponsibilitySplit]] D5。英莱官方 demo「回调更新画面」的结论**仅适用于同进程低频画面**，本项目主页面不适用。
- **校准数据双回调（2026-08-17 / 2026-09-08 改型）**：`RegisterCallbacks()` 在轮廓回调之外额外注册 `InternalRefCornerPts` 校准回调（`_cbCalibration` 存字段防 GC），`CalibrationCallback` 在 `using` 块内把 `IntelligentCalibrationInfo`（中心点+4角点）拷贝进 **`LineLaserCalibration`** 快照（`_calibLock` 保护），经 `override Calibration` 暴露。⛔ 绘制不再由本类执行：`LineLaserManager` 取 `Active.Calibration` 传给 [[api/ProfileMatRenderer]]（绘制内容同下：黄色校准框 + 浅灰大十字架 + 浅绿角点/中心点 + 红色特征点，无校准回退自动缩放画法）。
- **连接位掩码（Core 未连=硬失败）**：`ConnectToSensor` 返回位掩码。`EM_INTELLIGENT_CONNECT_E_CORE` 位为 1 表示 Core 服务未连上 → **视为硬失败**：记录 `Error` 日志、`UnInitSDK()` 清理、直接返回（不置 `_isConnected`/`_isOpened`），避免状态栏假阳性「已连接」。仅当 Core 连上时才继续启用传感器/激光/采集相机。

## 算法路线分支（英莱自有算法）

英莱 SDK 自带算法与反馈，`IntelligentLaserCameraRun` 将每帧 `InspectResult[0]` 捕获为 `LineLaserSeamResult` 快照（⛔ 原 `IlInspectResult` 已于 2026-09-08 删除，ADR-039）。工作流 `LineLaserWorkflow` 经 `LineLaserManager.Instance.ResultReady` 拿到结果后分支（详见 [[api/LineLaserWorkflow]]）：

- **英莱 + `ParseRes==1`（有有效识别）**：直接以 `LineLaserSeamResult` 构造 `SeamFeatureResult`（FeatureY→CenterY、FeatureZ→CenterX、平均 Width→SeamWidth、Area→SeamArea），经 `PipelineManager.ReportExternalResult(...)` 复用类级 `_completedArgs` 触发 `AlgorithmCompleted`，下游 `WeldProcess`/`MotionControlWorkflow` 照常消费焊缝特征；**不再运行 Emgu 通用管线**，满足"启用英莱相机时算法走自己路线"的诉求。显示沿用当前轮廓帧（`_lastResultMat = _lastAcquiredMat`）。
- **英莱但 `ParseRes!=1`（本帧无有效识别）/ 其他相机**：回退 `PipelineManager.Instance.Execute(_lastAcquiredMat, robotX)` 通用 Emgu 管线，与 SmartRay/Virtual 一致。
- 坐标映射（FeatureY/Z → CenterY/X）为按物理 mm 的初步对齐，具体标定关系需现场复核（见交付报告已知局限）。

## 接入点（LineLaserManager，2026-09-08 现行）

- `LineLaserKind.IntelligentLaser = 1`（枚举定义于 `ILineLaser/LineLaserType.cs`）。
- `LineLaserManager.Instance.SelectIntelligentLaser()`：懒创建 `IntelligentLaserCameraRun`、登记进 `CameraRegistry` 并订阅其事件、套用配置后激活。
- `LineLaserManager.Instance.ConnectionState`：`_working` 为真时 `Working`，否则按 `Active.ConnectionState`（即 `IsConnected`）派生 Connected/Disconnected。
- **相机 IP**：`LineLaserManager.Instance.Config.SensorIp`（`Config/XML/LineLaserConfig.xml`）；`ILCamPage` 的 IP 输入框与「扫描选中」均走此处并调 `SaveConfig()`。⛔ 旧 `Config/INI/IntelligentLaser.ini`、`CameraSelector.ini`、`Config/INI/CameraPresets.ini` 均已弃用。
- **UI 选择（2026-09-08 改，ADR-039）**：`ILCamPage` 仍经 `LineLaserManager.Instance.Active as IntelligentLaserCameraRun` 取实例，但**订阅面收窄**——⛔ `ContourFrameReady` / ⛔ `ContourDataReady` 已删，现只订阅 `JobParamsChanged`；画面帧改订阅 `LineLaserManager.Instance.MatUpdated`，识别结果读 `_ilCamera.LastInspectResult`（`LineLaserSeamResult`）。`UpdateModeUiCore` 中原 `_ilCamera.IsManualMode = !running` 改为 `LineLaserManager.Instance.SetDisplayOptions(!running, DisplayFps, true)`。
- **工作流启动**：`LineLaserWorkflow.InitializeInternal()` 与 `Start()` 相机分支一律经 `LineLaserManager.Instance`（`SelectVirtual` / `SelectIntelligentLaser` / `IsVirtual` / `SetWorking`）；连接用 `ConnectManual(LineLaserManager.Instance.Config.SensorIp)`；取图链 `AcquireImage` 仍经 `LineLaserManager.Instance.Active`，**零改动**。

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
   - ✅ 修复：类内所有 `Mat` 使用**全限定名 `Emgu.CV.Mat`**，**不要**加 `using Emgu.CV;`（否则 `Mat` 变成两命名空间二义性）。
   - **2026-09-08（ADR-039）影响**：`CurrentMat` 已上提基类 `LineLaserCameraBase`（`ILineLaser/` 命名空间，**不** `using IntelligentLaser_CSharp`，故可直接 `using Emgu.CV`）；
     本类的 `using Emgu.CV;` / `using System.Drawing;` / `using System.Drawing.Drawing2D;` / `using EmguALG;` / `using ProductFileManager;` 已随绘制代码一并移除。**保留的 SDK 遮蔽风险只剩 `Marshal`（见下条）**；若日后在本类内再写 Emgu 代码，仍须全限定 `Emgu.CV.Mat`。

2. **`Marshal.ReadFloat` / `Marshal.ReadSingle` 均不存在（根因：SDK 命名空间遮蔽 BCL `Marshal`）**：本模块 `using IntelligentLaser_CSharp;` 且 `using System.Runtime.InteropServices;`，而 **SDK 命名空间自身也导出 `Marshal` 类型**，会遮蔽（shadow）BCL 的 `System.Runtime.InteropServices.Marshal`。裸写 `Marshal.ReadFloat`/`ReadSingle` 实际解析到 SDK 的 `Marshal`（二者该方法都无），报 *"Marshal 未包含 ReadFloat/ReadSingle 的定义"*。此前把 `ReadSingle`→`ReadFloat` 的修改**未触达根因**（同被遮蔽）。
   - ✅ 修复：使用**全限定 BCL** `System.Runtime.InteropServices.Marshal.Copy(IntPtr, byte[], int, int)` 拷贝 8 字节到 `byte[8]`，再用 `System.BitConverter.ToSingle(buf, 0/4)` 取 y/z（float@0 / float@4）。全限定名绕过 `using` 解析、命中 BCL，彻底规避遮蔽。详见 [[lessons/IntelligentLaser-Pitfalls]]。
   - raw-Marshal 提取 FPoint：`System.Runtime.InteropServices.Marshal.Copy(fp, buf, 0, 8); float y = System.BitConverter.ToSingle(buf, 0); float z = System.BitConverter.ToSingle(buf, 4);`

*来源：AdaWeldSystem/LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs*
