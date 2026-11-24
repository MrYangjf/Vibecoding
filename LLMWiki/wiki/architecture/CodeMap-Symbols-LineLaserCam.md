---
title: CodeMap-Symbols-LineLaserCam — 代码地图·符号签名层·LineLaserCam（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-LineLaserCam — LineLaserCam 的类型与签名

> **一句话**：模块 `LineLaserCam` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> 线激光相机：Manager 唯一口 + 英莱/虚拟实现
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.LineLaserCam` | 3 | 4 | 线激光 · 管理与配置 | [[modules/LineLaserCam]] | ADR-023/024 |
| `AdaWeldSystem.LineLaserCam.ILineLaser` | 3 | 6 | 线激光 · 抽象契约 | [[modules/LineLaserCam]] | ADR-024 |
| `AdaWeldSystem.LineLaserCam.IntelligentLaserCam` | 1 | 6 | 线激光 · 英莱 SDK 实现 | [[modules/LineLaserCam]] | ADR-024/051 |
| `AdaWeldSystem.LineLaserCam.VirtualCam` | 1 | 1 | 线激光 · 虚拟相机（模拟） | [[modules/LineLaserCam]] | ADR-032/039 |

| 项 | 值 |
|---|---|
| 类型数 | 17 |
| 方法数 | 232 |

## 章节导航

- [CameraRegistry](#CameraRegistry)
- [IlCameraParam](#IlCameraParam)
- [IlJobDescInfo](#IlJobDescInfo)
- [IlJobParamInfo](#IlJobParamInfo)
- [IlJointTypeInfo](#IlJointTypeInfo)
- [IlSensorInfo](#IlSensorInfo)
- [IntelligentLaserCam](#IntelligentLaserCam)
- [LineLaserCalibration](#LineLaserCalibration)
- [LineLaserCameraBase](#LineLaserCameraBase)
- [LineLaserConfig](#LineLaserConfig)
- [LineLaserManager](#LineLaserManager)
- [LineLaserMatEventArgs](#LineLaserMatEventArgs)
- [LineLaserProfileEventArgs](#LineLaserProfileEventArgs)
- [LineLaserResultEventArgs](#LineLaserResultEventArgs)
- [LineLaserStateEventArgs](#LineLaserStateEventArgs)
- [ProfileSnapshot](#ProfileSnapshot)
- [VirtualCam](#VirtualCam)

## CameraRegistry

- 签名：`public class CameraRegistry`
- 位置：`LineLaserCam/CameraRegistry.cs:7`
- 命名空间：`AdaWeldSystem.LineLaserCam`
- 方法（7）：
  - `void Register(string name, LineLaserCameraBase camera)` — `LineLaserCam/CameraRegistry.cs:37`
  - ` Get(string name)` — `LineLaserCam/CameraRegistry.cs:46`
  - `bool Contains(string name)` — `LineLaserCam/CameraRegistry.cs:54`
  - `List<LineLaserCameraBase> GetAll()` — `LineLaserCam/CameraRegistry.cs:61`
  - `List<string> GetNames()` — `LineLaserCam/CameraRegistry.cs:68`
  - `void Remove(string name)` — `LineLaserCam/CameraRegistry.cs:75`
  - `void Clear()` — `LineLaserCam/CameraRegistry.cs:81`
- 构造（1）：
  - `CameraRegistry()` — `LineLaserCam/CameraRegistry.cs:25`
- 属性（1）：
  - `int Count { get; set; }` — `LineLaserCam/CameraRegistry.cs:18`

## IlCameraParam

- 签名：`public class IlCameraParam`
- 位置：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:58`
- 命名空间：`AdaWeldSystem.LineLaserCam.IntelligentLaserCam`
- 成员：（无）

## IlJobDescInfo

- 签名：`public class IlJobDescInfo`
- 位置：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:42`
- 命名空间：`AdaWeldSystem.LineLaserCam.IntelligentLaserCam`
- 成员：（无）

## IlJobParamInfo

- 签名：`public class IlJobParamInfo`
- 位置：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:18`
- 命名空间：`AdaWeldSystem.LineLaserCam.IntelligentLaserCam`
- 成员：（无）

## IlJointTypeInfo

- 签名：`public class IlJointTypeInfo`
- 位置：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:50`
- 命名空间：`AdaWeldSystem.LineLaserCam.IntelligentLaserCam`
- 成员：（无）

## IlSensorInfo

- 签名：`public class IlSensorInfo`
- 位置：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:31`
- 命名空间：`AdaWeldSystem.LineLaserCam.IntelligentLaserCam`
- 成员：（无）

## IntelligentLaserCam

- 签名：`public class IntelligentLaserCam : LineLaserCameraBase`
- 位置：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:74`
- 命名空间：`AdaWeldSystem.LineLaserCam.IntelligentLaserCam`
- 方法（50）：
  - `void RecordVendorResult(string operation, int code)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:198`
  - `void RecordLocalFailure(string operation)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:209`
  - `string DescribeLastError(LineLaserErrorContext context)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:222`
  - `void ConnectCore(string ip)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:269`
  - `void ShutdownPeripherals()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:311`
  - `void ReleaseNativeResources()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:332`
  - `bool ConfigureDefaultCommPeriod()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:363`
  - `void OpenSensor(string ip)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:397`
  - `void SensorRunContinue()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:425`
  - `void SensorStop()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:439`
  - `void Dispose()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:453`
  - `void ApplyFrameRateModel(EmIntelligentFpsModel model)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:482`
  - `List<IlSensorInfo> ScanSensors()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:514`
  - ` FetchCameraParams()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:573`
  - `int ApplyCameraParams(IlCameraParam param)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:601`
  - `bool ConnectManual(string ip)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:631`
  - `void DisconnectManual()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:651`
  - `void SetSensor(bool enable)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:660`
  - `void SetLaser(bool enable)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:675`
  - `bool IsLaserOn()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:684`
  - `bool IsCameraOn()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:691`
  - ` FetchFpsModel()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:698`
  - `void SyncHardwareStatus()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:718`
  - `void ResetMeasuredFps()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:744`
  - `int ApplyFrameRateModel(IlFpsModel model)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:754`
  - `List<IlJobDescInfo> FetchJobList()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:761`
  - `List<IlJointTypeInfo> FetchJointTypes()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:779`
  - `List<string> GetJointTypeDisplayKeys(int jointType)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:817`
  - `string GetJointTypeName(int jointType)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:826`
  - ` GetCurrentJobInfo()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:834`
  - `int FetchCurrentJobId()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:843`
  - `int SwitchJob(int jobId)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:866`
  - `int CreateJob(int jointType, string desc)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:896`
  - `int DeleteJob(int jobId)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:926`
  - `void RegisterCallbacks()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:956`
  - `void FreeCallbackHandles()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:981`
  - `void WaitForCallbacksToFinish()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:989`
  - `void CalibrationCallback(IntPtr fRegioninfo, IntPtr pUser, uint dwInstanceId)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1008`
  - `void MillionOutlineCallback(IntPtr pOutlineData, IntPtr pUser, uint dwInstanceId)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1038`
  - `void BuildCloudFromInspect(IntPtr pOutlineData, PointCloudData cloud)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1075`
  - `void UpdateFrameRate(DateTime now)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1135`
  - `void SetInvalidInspect()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1161`
  - `void HandleFrameReady(PointCloudData cloud)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1168`
  - `void HandleEmptyFrame()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1180`
  - `void InitJobParamsCallback(IntPtr pInstance, uint arraySize, IntPtr pUser, uint dwInstanceId)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1193`
  - `void JobParamsChangedCallback(IntPtr pInstance, uint arraySize, IntPtr pUser, uint dwInstanceId)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1299`
  - `void Make64Bytes(string name)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1378`
  - `void ReadAsciiBytes(byte[] buf)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1387`
  - `List<IlJobParamInfo> FetchAllJobParams()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1397`
  - `int ApplyJobParams(IEnumerable<IlJobParamInfo> values)` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:1414`
- 构造（1）：
  - `IntelligentLaserCam()` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:150`
- 属性（12）：
  - `int CallbackWaitTimeoutMs { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:137`
  - `string SensorIp { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:160`
  - `LineLaserKind Kind { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:171`
  - `AutoResetEvent AcquisitionCompletedSignal { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:174`
  - `bool IsRunning { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:177`
  - `bool LastAcquisitionSuccess { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:180`
  - `bool IsConnected { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:183`
  - `double ScanRateHz { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:186`
  - `double MeasuredFps { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:189`
  - `LineLaserCalibration Calibration { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:192`
  - `LineLaserSeamResult LastInspectResult { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:260`
  - `int LastContourPointCount { get; set; }` — `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs:480`

## LineLaserCalibration

- 签名：`public class LineLaserCalibration`
- 位置：`LineLaserCam/ILineLaser/LineLaserCalibration.cs:4`
- 命名空间：`AdaWeldSystem.LineLaserCam.ILineLaser`
- 构造（2）：
  - `LineLaserCalibration()` — `LineLaserCam/ILineLaser/LineLaserCalibration.cs:31`
  - `LineLaserCalibration(float[] center, float[] leftTop, float[] rightTop, float[] leftBottom, float[] rightBottom)` — `LineLaserCam/ILineLaser/LineLaserCalibration.cs:46`
- 属性（6）：
  - `bool HasData { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCalibration.cs:9`
  - `float[] Center { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCalibration.cs:12`
  - `float[] LeftTopCorner { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCalibration.cs:15`
  - `float[] RightTopCorner { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCalibration.cs:18`
  - `float[] LeftBottomCorner { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCalibration.cs:21`
  - `float[] RightBottomCorner { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCalibration.cs:24`

## LineLaserCameraBase

- 签名：`public abstract class LineLaserCameraBase : IDisposable`
- 位置：`LineLaserCam/ILineLaser/LineLaserCameraBase.cs:11`
- 命名空间：`AdaWeldSystem.LineLaserCam.ILineLaser`
- 方法（16）：
  - `void RaiseResultReady(LineLaserSeamResult result, double measuredFps)` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:92`
  - `void RaiseProfileReady(PointCloudData cloud, double measuredFps)` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:100`
  - `void RaiseStateChanged()` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:106`
  - `void Log(string message, MessageLevel level)` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:114`
  - `void UpdateDisplayMat(Mat mat)` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:126`
  - `void SensorRunContinue()` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:139`
  - `void SensorStop()` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:142`
  - `void Dispose()` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:145`
  - `bool ConnectManual(string ip)` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:155`
  - `void DisconnectManual()` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:162`
  - `bool ConfigureDefaultCommPeriod()` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:169`
  - `bool IsCameraOn()` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:176`
  - `bool IsLaserOn()` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:183`
  - `void SetSensor(bool enable)` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:190`
  - `void SetLaser(bool enable)` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:196`
  - `string DescribeLastError(LineLaserErrorContext context)` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:208`
- 构造（1）：
  - `LineLaserCameraBase(string cameraName)` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:80`
- 属性（10）：
  - `string CameraName { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:24`
  - `LineLaserKind Kind { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:27`
  - `bool IsConnected { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:30`
  - `bool IsRunning { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:33`
  - `bool LastAcquisitionSuccess { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:36`
  - `Mat CurrentMat { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:39`
  - `double ScanRateHz { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:51`
  - `AutoResetEvent AcquisitionCompletedSignal { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:54`
  - `LineLaserCalibration Calibration { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:57`
  - `LineLaserConnectionState ConnectionState { get; set; }` — `LineLaserCam/ILineLaser/LineLaserCameraBase.cs:60`

## LineLaserConfig

- 签名：`public class LineLaserConfig`
- 位置：`LineLaserCam/LineLaserConfig.cs:13`
- 命名空间：`AdaWeldSystem.LineLaserCam`
- 方法（10）：
  - `void Log(string message, MessageLevel level)` — `LineLaserCam/LineLaserConfig.cs:96`
  - `void ReadInt(XdocumentReaderWriter reader, string path, int def)` — `LineLaserCam/LineLaserConfig.cs:106`
  - `void ReadDouble(XdocumentReaderWriter reader, string path, double def)` — `LineLaserCam/LineLaserConfig.cs:117`
  - `void ReadBool(XdocumentReaderWriter reader, string path, bool def)` — `LineLaserCam/LineLaserConfig.cs:128`
  - `void SanitizeSeconds(int seconds)` — `LineLaserCam/LineLaserConfig.cs:138`
  - ` Clone()` — `EmguALG/Core/PreprocessConfig.cs:145`
  - `void WriteConfigNodes(XdocumentReaderWriter reader)` — `LineLaserCam/LineLaserConfig.cs:152`
  - `void LoadConfig()` — `LineLaserCam/LineLaserConfig.cs:176`
  - `void LoadConfig(bool allowHeal)` — `LineLaserCam/LineLaserConfig.cs:183`
  - `void SaveConfig()` — `LineLaserCam/LineLaserConfig.cs:232`
- 构造（2）：
  - `LineLaserConfig()` — `LineLaserCam/LineLaserConfig.cs:73`
  - `LineLaserConfig()` — `EmguALG/Core/PreprocessConfig.cs:138`
- 属性（11）：
  - `string ConfigFileName { get; set; }` — `LineLaserCam/LineLaserConfig.cs:36`
  - `LineLaserKind DefaultKind { get; set; }` — `LineLaserCam/LineLaserConfig.cs:39`
  - `bool AutoConnectOnStart { get; set; }` — `LineLaserCam/LineLaserConfig.cs:42`
  - `string SensorIp { get; set; }` — `LineLaserCam/LineLaserConfig.cs:45`
  - `int LineLaserDataFrequencyHz { get; set; }` — `LineLaserCam/LineLaserConfig.cs:48`
  - `bool DisplayEnabled { get; set; }` — `LineLaserCam/LineLaserConfig.cs:51`
  - `double DisplayFps { get; set; }` — `LineLaserCam/LineLaserConfig.cs:54`
  - `bool ConvertMatEnabled { get; set; }` — `LineLaserCam/LineLaserConfig.cs:57`
  - `int DataStableTimeoutSeconds { get; set; }` — `LineLaserCam/LineLaserConfig.cs:60`
  - `int WaitWorkingTimeoutSeconds { get; set; }` — `LineLaserCam/LineLaserConfig.cs:63`
  - `int FirstResultTimeoutSeconds { get; set; }` — `LineLaserCam/LineLaserConfig.cs:66`

## LineLaserManager

- 签名：`public class LineLaserManager : IDisposable`
- 位置：`LineLaserCam/LineLaserManager.cs:118`
- 命名空间：`AdaWeldSystem.LineLaserCam`
- 方法（36）：
  - `string DescribeLastError(LineLaserErrorContext context)` — `LineLaserCam/LineLaserManager.cs:271`
  - `void Log(string message, MessageLevel level)` — `LineLaserCam/LineLaserManager.cs:306`
  - `void ApplyConfig()` — `LineLaserCam/LineLaserManager.cs:312`
  - `void SetActive(LineLaserCameraBase camera)` — `LineLaserCam/LineLaserManager.cs:332`
  - `void ReleaseCamera(LineLaserCameraBase camera, string reason)` — `LineLaserCam/LineLaserManager.cs:349`
  - `void FindOtherRunningCamera(LineLaserCameraBase except)` — `LineLaserCam/LineLaserManager.cs:374`
  - `void IsActiveSender(object sender, string eventName)` — `LineLaserCam/LineLaserManager.cs:388`
  - `void OnCameraStateChanged(object sender, LineLaserStateEventArgs e)` — `LineLaserCam/LineLaserManager.cs:410`
  - `void OnCameraResultReady(object sender, LineLaserResultEventArgs e)` — `LineLaserCam/LineLaserManager.cs:419`
  - `void OnCameraProfileReady(object sender, LineLaserProfileEventArgs e)` — `LineLaserCam/LineLaserManager.cs:429`
  - `void UpdateProfileSnapshot(PointCloudData cloud, double measuredFps)` — `LineLaserCam/LineLaserManager.cs:453`
  - `void ConvertCalibration(LineLaserCalibration calib)` — `LineLaserCam/LineLaserManager.cs:478`
  - `void RenderDisplayFrame(PointCloudData cloud)` — `LineLaserCam/LineLaserManager.cs:493`
  - `void Register(string name, LineLaserCameraBase camera)` — `LineLaserCam/LineLaserManager.cs:529`
  - `void Unregister(string name)` — `LineLaserCam/LineLaserManager.cs:549`
  - ` Get(string name)` — `LineLaserCam/LineLaserManager.cs:567`
  - `void SelectIntelligentLaser()` — `LineLaserCam/LineLaserManager.cs:573`
  - `void SelectVirtual()` — `LineLaserCam/LineLaserManager.cs:580`
  - `int FetchCurrentJobId()` — `LineLaserCam/LineLaserManager.cs:591`
  - `int SwitchJob(int jobId)` — `LineLaserCam/LineLaserManager.cs:600`
  - `bool Select(string name)` — `LineLaserCam/LineLaserManager.cs:615`
  - `bool Connect()` — `LineLaserCam/LineLaserManager.cs:626`
  - `void Disconnect()` — `LineLaserCam/LineLaserManager.cs:643`
  - `bool ConfigureDefaultCommPeriod()` — `LineLaserCam/LineLaserManager.cs:652`
  - `bool IsCameraOn()` — `LineLaserCam/LineLaserManager.cs:660`
  - `bool IsLaserOn()` — `LineLaserCam/LineLaserManager.cs:667`
  - `void SetSensor(bool enable)` — `LineLaserCam/LineLaserManager.cs:674`
  - `void SetLaser(bool enable)` — `LineLaserCam/LineLaserManager.cs:681`
  - `void ShutdownPeripherals()` — `LineLaserCam/LineLaserManager.cs:687`
  - `void SetWorking(bool working)` — `LineLaserCam/LineLaserManager.cs:706`
  - `void SetDisplayOptions(bool enabled, double fps, bool convertMat)` — `LineLaserCam/LineLaserManager.cs:716`
  - `void StartAcquisition()` — `LineLaserCam/LineLaserManager.cs:724`
  - `void StopAcquisition()` — `LineLaserCam/LineLaserManager.cs:731`
  - `void LoadConfig()` — `LineLaserCam/LineLaserManager.cs:737`
  - `void SaveConfig()` — `LineLaserCam/LineLaserManager.cs:744`
  - `void Dispose()` — `LineLaserCam/LineLaserManager.cs:750`
- 构造（1）：
  - `LineLaserManager()` — `LineLaserCam/LineLaserManager.cs:283`
- 属性（16）：
  - `LineLaserManager Instance { get; set; }` — `LineLaserCam/LineLaserManager.cs:160`
  - `CameraRegistry Cameras { get; set; }` — `LineLaserCam/LineLaserManager.cs:163`
  - `LineLaserConfig Config { get; set; }` — `LineLaserCam/LineLaserManager.cs:166`
  - `LineLaserCameraBase Active { get; set; }` — `LineLaserCam/LineLaserManager.cs:169`
  - `IntelligentLaserCam.IntelligentLaserCam IntelligentLaser { get; set; }` — `LineLaserCam/LineLaserManager.cs:189`
  - `VirtualCam.VirtualCam VirtualCamera { get; set; }` — `LineLaserCam/LineLaserManager.cs:204`
  - `string ActiveName { get; set; }` — `LineLaserCam/LineLaserManager.cs:219`
  - `LineLaserKind Kind { get; set; }` — `LineLaserCam/LineLaserManager.cs:222`
  - `bool IsVirtual { get; set; }` — `LineLaserCam/LineLaserManager.cs:225`
  - `bool IsWorking { get; set; }` — `LineLaserCam/LineLaserManager.cs:228`
  - `LineLaserConnectionState ConnectionState { get; set; }` — `LineLaserCam/LineLaserManager.cs:231`
  - `ProfileSnapshot Profile { get; set; }` — `LineLaserCam/LineLaserManager.cs:242`
  - `LineLaserSeamResult LastResult { get; set; }` — `LineLaserCam/LineLaserManager.cs:245`
  - `bool DisplayEnabled { get; set; }` — `LineLaserCam/LineLaserManager.cs:248`
  - `double DisplayFps { get; set; }` — `LineLaserCam/LineLaserManager.cs:251`
  - `bool ConvertMatEnabled { get; set; }` — `LineLaserCam/LineLaserManager.cs:254`

## LineLaserMatEventArgs

- 签名：`public class LineLaserMatEventArgs : EventArgs`
- 位置：`LineLaserCam/ILineLaser/LineLaserEventArgs.cs:158`
- 命名空间：`AdaWeldSystem.LineLaserCam.ILineLaser`
- 构造（1）：
  - `LineLaserMatEventArgs(string cameraName, Mat frame)` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:175`
- 属性（2）：
  - `string CameraName { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:163`
  - `Mat Frame { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:166`

## LineLaserProfileEventArgs

- 签名：`public class LineLaserProfileEventArgs : EventArgs`
- 位置：`LineLaserCam/ILineLaser/LineLaserEventArgs.cs:126`
- 命名空间：`AdaWeldSystem.LineLaserCam.ILineLaser`
- 构造（1）：
  - `LineLaserProfileEventArgs(string cameraName, PointCloudData cloud, double measuredFps)` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:147`
- 属性（3）：
  - `string CameraName { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:131`
  - `PointCloudData Cloud { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:134`
  - `double MeasuredFps { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:137`

## LineLaserResultEventArgs

- 签名：`public class LineLaserResultEventArgs : EventArgs`
- 位置：`LineLaserCam/ILineLaser/LineLaserEventArgs.cs:94`
- 命名空间：`AdaWeldSystem.LineLaserCam.ILineLaser`
- 构造（1）：
  - `LineLaserResultEventArgs(string cameraName, LineLaserSeamResult result, double measuredFps)` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:115`
- 属性（3）：
  - `string CameraName { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:99`
  - `LineLaserSeamResult Result { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:102`
  - `double MeasuredFps { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:105`

## LineLaserStateEventArgs

- 签名：`public class LineLaserStateEventArgs : EventArgs`
- 位置：`LineLaserCam/ILineLaser/LineLaserEventArgs.cs:185`
- 命名空间：`AdaWeldSystem.LineLaserCam.ILineLaser`
- 构造（1）：
  - `LineLaserStateEventArgs(string cameraName, bool isConnected, bool isRunning, LineLaserConnectionState connectionState)` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:210`
- 属性（4）：
  - `string CameraName { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:190`
  - `bool IsConnected { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:193`
  - `bool IsRunning { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:196`
  - `LineLaserConnectionState ConnectionState { get; set; }` — `LineLaserCam/ILineLaser/LineLaserEventArgs.cs:199`

## ProfileSnapshot

- 签名：`public class ProfileSnapshot`
- 位置：`LineLaserCam/LineLaserManager.cs:19`
- 命名空间：`AdaWeldSystem.LineLaserCam`
- 方法（2）：
  - `void Fill(double[] ys, double[] zs, int count, bool hasResult, double featureY, double featureZ, double measuredFps, long version)` — `LineLaserCam/LineLaserManager.cs:81`
  - `void Clear(long version)` — `LineLaserCam/LineLaserManager.cs:104`
- 构造（1）：
  - `ProfileSnapshot()` — `LineLaserCam/LineLaserManager.cs:62`
- 属性（8）：
  - `double[] Ys { get; set; }` — `LineLaserCam/LineLaserManager.cs:34`
  - `double[] Zs { get; set; }` — `LineLaserCam/LineLaserManager.cs:37`
  - `int Count { get; set; }` — `LineLaserCam/LineLaserManager.cs:40`
  - `bool HasResult { get; set; }` — `LineLaserCam/LineLaserManager.cs:43`
  - `double FeatureY { get; set; }` — `LineLaserCam/LineLaserManager.cs:46`
  - `double FeatureZ { get; set; }` — `LineLaserCam/LineLaserManager.cs:49`
  - `double MeasuredFps { get; set; }` — `LineLaserCam/LineLaserManager.cs:52`
  - `long Version { get; set; }` — `LineLaserCam/LineLaserManager.cs:55`

## VirtualCam

- 签名：`public class VirtualCam : LineLaserCameraBase`
- 位置：`LineLaserCam/VirtualCam/VirtualCam.cs:11`
- 命名空间：`AdaWeldSystem.LineLaserCam.VirtualCam`
- 方法（14）：
  - `string DescribeLastError(LineLaserErrorContext context)` — `LineLaserCam/VirtualCam/VirtualCam.cs:62`
  - `void GenerateSeamContour()` — `LineLaserCam/VirtualCam/VirtualCam.cs:84`
  - `void BuildResult(PointCloudData cloud)` — `LineLaserCam/VirtualCam/VirtualCam.cs:115`
  - `void OnSimTick(object state)` — `LineLaserCam/VirtualCam/VirtualCam.cs:147`
  - `void GenerateFrame()` — `LineLaserCam/VirtualCam/VirtualCam.cs:154`
  - `void StopSimTimer()` — `LineLaserCam/VirtualCam/VirtualCam.cs:177`
  - `void SensorRunContinue()` — `LineLaserCam/VirtualCam/VirtualCam.cs:184`
  - `void SensorStop()` — `LineLaserCam/VirtualCam/VirtualCam.cs:196`
  - `void Dispose()` — `LineLaserCam/VirtualCam/VirtualCam.cs:204`
  - `bool ConnectManual(string ip)` — `LineLaserCam/VirtualCam/VirtualCam.cs:214`
  - `bool IsCameraOn()` — `LineLaserCam/VirtualCam/VirtualCam.cs:221`
  - `bool IsLaserOn()` — `LineLaserCam/VirtualCam/VirtualCam.cs:228`
  - `void SetSensor(bool enable)` — `LineLaserCam/VirtualCam/VirtualCam.cs:235`
  - `void SetLaser(bool enable)` — `LineLaserCam/VirtualCam/VirtualCam.cs:242`
- 构造（1）：
  - `VirtualCam()` — `LineLaserCam/VirtualCam/VirtualCam.cs:72`
- 属性（7）：
  - `int FrameRateHz { get; set; }` — `LineLaserCam/VirtualCam/VirtualCam.cs:39`
  - `LineLaserKind Kind { get; set; }` — `LineLaserCam/VirtualCam/VirtualCam.cs:42`
  - `bool IsConnected { get; set; }` — `LineLaserCam/VirtualCam/VirtualCam.cs:45`
  - `bool IsRunning { get; set; }` — `LineLaserCam/VirtualCam/VirtualCam.cs:48`
  - `bool LastAcquisitionSuccess { get; set; }` — `LineLaserCam/VirtualCam/VirtualCam.cs:51`
  - `double ScanRateHz { get; set; }` — `LineLaserCam/VirtualCam/VirtualCam.cs:54`
  - `AutoResetEvent AcquisitionCompletedSignal { get; set; }` — `LineLaserCam/VirtualCam/VirtualCam.cs:57`

## 相关页面

- [[architecture/CodeMap]]
