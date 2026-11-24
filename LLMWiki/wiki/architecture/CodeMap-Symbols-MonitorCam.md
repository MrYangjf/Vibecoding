---
title: CodeMap-Symbols-MonitorCam — 代码地图·符号签名层·MonitorCam（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-MonitorCam — MonitorCam 的类型与签名

> **一句话**：模块 `MonitorCam` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> 监控相机：Manager 唯一口 + 海康/虚拟实现
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.MonitorCam` | 2 | 2 | 监控相机 · Manager 与配置 | [[modules/MonitorCam]] | ADR-019/021/047/094 |
| `AdaWeldSystem.MonitorCam.IMonitorCam` | 2 | 3 | 监控相机 · 抽象契约 | [[modules/MonitorCam]] | ADR-019/021/047 |
| `AdaWeldSystem.MonitorCam.HikCam` | 1 | 1 | 监控相机 · 海康 MVS 实现 | [[modules/MonitorCam]] | ADR-047 |

| 项 | 值 |
|---|---|
| 类型数 | 6 |
| 方法数 | 108 |

## 章节导航

- [HikCam](#HikCam)
- [MonitorCamConfig](#MonitorCamConfig)
- [MonitorCamDeviceInfo](#MonitorCamDeviceInfo)
- [MonitorCamManager](#MonitorCamManager)
- [MonitorCameraFrameCompletedEventArgs](#MonitorCameraFrameCompletedEventArgs)
- [MonitorSupervisionStatusChangedEventArgs](#MonitorSupervisionStatusChangedEventArgs)

## HikCam

- 签名：`public class HikCam : IMonitorCamApi`
- 位置：`MonitorCam/HikCam/HikCam.cs:14`
- 命名空间：`AdaWeldSystem.MonitorCam.HikCam`
- 方法（27）：
  - `void RecordVendorResult(string operation, int code)` — `MonitorCam/HikCam/HikCam.cs:92`
  - `void RecordLocalFailure(string operation)` — `MonitorCam/HikCam/HikCam.cs:104`
  - `bool Connect(string ip, string port)` — `MonitorCam/HikCam/HikCam.cs:119`
  - `string DescribeLastError(MonitorCamErrorContext context)` — `MonitorCam/HikCam/HikCam.cs:209`
  - `List<MonitorCamDeviceInfo> ScanDevices()` — `MonitorCam/HikCam/HikCam.cs:235`
  - `void Disconnect()` — `MonitorCam/HikCam/HikCam.cs:280`
  - ` CaptureSingleFrame()` — `MonitorCam/HikCam/HikCam.cs:307`
  - `bool StartCapture()` — `MonitorCam/HikCam/HikCam.cs:345`
  - `void StopCapture()` — `MonitorCam/HikCam/HikCam.cs:390`
  - ` TriggerSingleShot()` — `MonitorCam/HikCam/HikCam.cs:424`
  - `bool StartRecord(string filePath)` — `MonitorCam/HikCam/HikCam.cs:489`
  - `void StopRecord()` — `MonitorCam/HikCam/HikCam.cs:545`
  - `bool SetExposureTime(float valueUs)` — `MonitorCam/HikCam/HikCam.cs:566`
  - `bool SetGain(float valueDb)` — `MonitorCam/HikCam/HikCam.cs:594`
  - `float GetExposureTime()` — `MonitorCam/HikCam/HikCam.cs:621`
  - `float GetGain()` — `MonitorCam/HikCam/HikCam.cs:638`
  - `void Dispose()` — `MonitorCam/HikCam/HikCam.cs:654`
  - `void EnsureSdkInitialized()` — `MonitorCam/HikCam/HikCam.cs:676`
  - `void TrySelectDevice(List<IDeviceInfo> devices, string ip, IDeviceInfo selected)` — `MonitorCam/HikCam/HikCam.cs:701`
  - `void QueryDeviceIp(IDeviceInfo info)` — `MonitorCam/HikCam/HikCam.cs:722`
  - `void BuildMat(IFrameOut frameOut)` — `MonitorCam/HikCam/HikCam.cs:735`
  - `void IsColorPixelFormat(MvGvspPixelType type)` — `MonitorCam/HikCam/HikCam.cs:798`
  - `void StartGrabThreadLocked()` — `MonitorCam/HikCam/HikCam.cs:833`
  - `void GrabLoop()` — `MonitorCam/HikCam/HikCam.cs:846`
  - `void ReadFrameFormat(uint width, uint height, MvGvspPixelType pixelType)` — `MonitorCam/HikCam/HikCam.cs:886`
  - `void GetRecordFrameRate()` — `MonitorCam/HikCam/HikCam.cs:905`
  - `void SetState(MonitorCameraConnectionState newState)` — `MonitorCam/HikCam/HikCam.cs:919`
- 构造（1）：
  - `HikCam()` — `MonitorCam/HikCam/HikCam.cs:79`
- 属性（3）：
  - `MonitorCameraConnectionState ConnectionState { get; set; }` — `MonitorCam/HikCam/HikCam.cs:54`
  - `bool IsGrabbing { get; set; }` — `MonitorCam/HikCam/HikCam.cs:60`
  - `bool IsRecording { get; set; }` — `MonitorCam/HikCam/HikCam.cs:66`

## MonitorCamConfig

- 签名：`public class MonitorCamConfig`
- 位置：`MonitorCam/MonitorCamConfig.cs:10`
- 命名空间：`AdaWeldSystem.MonitorCam`
- 方法（6）：
  - `void BuildIniDefaults()` — `MonitorCam/MonitorCamConfig.cs:72`
  - `void RelativeToBase(string fullPath)` — `MonitorCam/MonitorCamConfig.cs:91`
  - `void SaveToIni(string filePath)` — `MonitorCam/MonitorCamConfig.cs:101`
  - `void SaveConfig()` — `MonitorCam/MonitorCamConfig.cs:121`
  - `void LoadFromIni(string filePath)` — `MonitorCam/MonitorCamConfig.cs:128`
  - `void LoadFromIni(string filePath, bool allowHeal)` — `MonitorCam/MonitorCamConfig.cs:136`
- 构造（1）：
  - `MonitorCamConfig()` — `MonitorCam/MonitorCamConfig.cs:56`
- 属性（10）：
  - `string DefaultConfigPath { get; set; }` — `MonitorCam/MonitorCamConfig.cs:19`
  - `string IpAddress { get; set; }` — `MonitorCam/MonitorCamConfig.cs:29`
  - `string Port { get; set; }` — `MonitorCam/MonitorCamConfig.cs:32`
  - `int ExposureMs { get; set; }` — `MonitorCam/MonitorCamConfig.cs:35`
  - `int ImageWidth { get; set; }` — `MonitorCam/MonitorCamConfig.cs:38`
  - `int ImageHeight { get; set; }` — `MonitorCam/MonitorCamConfig.cs:41`
  - `string RecordDir { get; set; }` — `MonitorCam/MonitorCamConfig.cs:44`
  - `double MmPerPixel { get; set; }` — `MonitorCam/MonitorCamConfig.cs:47`
  - `int SpotX { get; set; }` — `MonitorCam/MonitorCamConfig.cs:50`
  - `int SpotY { get; set; }` — `MonitorCam/MonitorCamConfig.cs:53`

## MonitorCamDeviceInfo

- 签名：`public class MonitorCamDeviceInfo`
- 位置：`MonitorCam/IMonitorCam/MonitorCamDeviceInfo.cs:4`
- 命名空间：`AdaWeldSystem.MonitorCam.IMonitorCam`
- 构造（1）：
  - `MonitorCamDeviceInfo()` — `MonitorCam/IMonitorCam/MonitorCamDeviceInfo.cs:22`
- 属性（5）：
  - `string Ip { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamDeviceInfo.cs:7`
  - `string ProductName { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamDeviceInfo.cs:10`
  - `string SerialNumber { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamDeviceInfo.cs:13`
  - `string PortType { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamDeviceInfo.cs:16`
  - `string SensorType { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamDeviceInfo.cs:19`

## MonitorCamManager

- 签名：`public class MonitorCamManager`
- 位置：`MonitorCam/MonitorCamManager.cs:16`
- 命名空间：`AdaWeldSystem.MonitorCam`
- 方法（28）：
  - `void EnsureRecordDirectory()` — `MonitorCam/MonitorCamManager.cs:172`
  - `void RelayPreviewFrame(Mat frame)` — `MonitorCam/MonitorCamManager.cs:208`
  - `bool OpenSensor(string ip, string port)` — `MonitorCam/MonitorCamManager.cs:276`
  - `void CloseSensor()` — `MonitorCam/MonitorCamManager.cs:287`
  - `List<MonitorCamDeviceInfo> ScanDevices()` — `MonitorCam/MonitorCamManager.cs:296`
  - `void SaveConfig()` — `MonitorCam/MonitorCamManager.cs:302`
  - `bool StartCapture()` — `MonitorCam/MonitorCamManager.cs:311`
  - `void StopCapture()` — `MonitorCam/MonitorCamManager.cs:318`
  - `bool StartRecord(string fileName)` — `MonitorCam/MonitorCamManager.cs:327`
  - `void StopRecord()` — `MonitorCam/MonitorCamManager.cs:345`
  - ` TriggerSingleShot()` — `MonitorCam/MonitorCamManager.cs:353`
  - `bool TryAcquireCalibFrame(Mat frame, string failureMessage)` — `MonitorCam/MonitorCamManager.cs:364`
  - `string DescribeLastError(MonitorCamErrorContext context)` — `MonitorCam/MonitorCamManager.cs:396`
  - `bool SetExposureTime(float valueUs)` — `MonitorCam/MonitorCamManager.cs:409`
  - `bool SetGain(float valueDb)` — `MonitorCam/MonitorCamManager.cs:417`
  - `float GetExposureTime()` — `MonitorCam/MonitorCamManager.cs:424`
  - `float GetGain()` — `MonitorCam/MonitorCamManager.cs:431`
  - `void SetPhase(MonitorCameraPhase phase)` — `MonitorCam/MonitorCamManager.cs:438`
  - `void SensorRunContinue()` — `MonitorCam/MonitorCamManager.cs:444`
  - `void StartSupervision()` — `MonitorCam/MonitorCamManager.cs:452`
  - `void StopSupervision()` — `MonitorCam/MonitorCamManager.cs:467`
  - `void Dispose()` — `MonitorCam/MonitorCamManager.cs:498`
  - `void AnnotateSpot(Mat frame)` — `MonitorCam/MonitorCamManager.cs:512`
  - `void AcquireOnce()` — `MonitorCam/MonitorCamManager.cs:520`
  - `void RaiseFrameCompleted(Mat frame, bool success)` — `MonitorCam/MonitorCamManager.cs:543`
  - `void SupervisionLoop()` — `MonitorCam/MonitorCamManager.cs:565`
  - `void EvaluateHealth()` — `MonitorCam/MonitorCamManager.cs:575`
  - `void SupervisionTransitionTo(MonitorSupervisionState newState, string reason)` — `MonitorCam/MonitorCamManager.cs:606`
- 构造（1）：
  - `MonitorCamManager()` — `MonitorCam/MonitorCamManager.cs:162`
- 属性（14）：
  - `MonitorCamManager Instance { get; set; }` — `MonitorCam/MonitorCamManager.cs:65`
  - `Mat CurrentMat { get; set; }` — `MonitorCam/MonitorCamManager.cs:71`
  - `bool IsRun { get; set; }` — `MonitorCam/MonitorCamManager.cs:77`
  - `MonitorCameraConnectionState ConnectionState { get; set; }` — `MonitorCam/MonitorCamManager.cs:83`
  - `MonitorCamConfig Config { get; set; }` — `MonitorCam/MonitorCamManager.cs:89`
  - `bool LastAcquisitionSuccess { get; set; }` — `MonitorCam/MonitorCamManager.cs:96`
  - `MonitorSupervisionState SupervisionState { get; set; }` — `MonitorCam/MonitorCamManager.cs:103`
  - `bool IsMonitorCameraWorking { get; set; }` — `MonitorCam/MonitorCamManager.cs:110`
  - `DateTime LastHealthyTime { get; set; }` — `MonitorCam/MonitorCamManager.cs:121`
  - `int CheckIntervalMs { get; set; }` — `MonitorCam/MonitorCamManager.cs:127`
  - `int HealthyValidMs { get; set; }` — `MonitorCam/MonitorCamManager.cs:134`
  - `string RecordDirectory { get; set; }` — `MonitorCam/MonitorCamManager.cs:248`
  - `bool IsCapturing { get; set; }` — `MonitorCam/MonitorCamManager.cs:261`
  - `bool IsRecording { get; set; }` — `MonitorCam/MonitorCamManager.cs:267`

## MonitorCameraFrameCompletedEventArgs

- 签名：`public class MonitorCameraFrameCompletedEventArgs : EventArgs`
- 位置：`MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:32`
- 命名空间：`AdaWeldSystem.MonitorCam.IMonitorCam`
- 属性（4）：
  - `Mat Frame { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:35`
  - `MonitorCameraPhase Phase { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:38`
  - `bool Success { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:41`
  - `DateTime Timestamp { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:44`

## MonitorSupervisionStatusChangedEventArgs

- 签名：`public class MonitorSupervisionStatusChangedEventArgs : EventArgs`
- 位置：`MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:7`
- 命名空间：`AdaWeldSystem.MonitorCam.IMonitorCam`
- 属性（7）：
  - `MonitorSupervisionState State { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:10`
  - `bool IsWorking { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:13`
  - `MonitorCameraPhase Phase { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:16`
  - `MonitorCameraConnectionState ConnectionState { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:19`
  - `DateTime LastHealthyTime { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:22`
  - `string Message { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:25`
  - `DateTime Timestamp { get; set; }` — `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs:28`

## 相关页面

- [[architecture/CodeMap]]
