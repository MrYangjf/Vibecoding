---
title: CodeMap-Symbols-Comm — 代码地图·符号签名层·Comm（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-Comm — Comm 的类型与签名

> **一句话**：模块 `Comm` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> 通讯：RSI 唯一机器人通道 + 日志双通道
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.Comm.Communication.Implementations` | 4 | 25 | 通讯 · 各厂商通道实现 | [[modules/Comm]] | ADR-025/026/027 |
| `AdaWeldSystem.Comm.SystemComm` | 3 | 5 | 通讯 · 全局单例与事件 | [[modules/Comm]] | ADR-025 |
| `AdaWeldSystem.Comm.Communication` | 1 | 4 | 通讯 · 通道管理（唯一出口） | [[modules/Comm]] | ADR-025/026 |
| `AdaWeldSystem.Comm.Communication.Abstractions` | 1 | 2 | 通讯 · 抽象契约（CommChannelBase） | [[modules/Comm]] | ADR-025/006 |

| 项 | 值 |
|---|---|
| 类型数 | 36 |
| 方法数 | 274 |

## 章节导航

- [CommChannelBase](#CommChannelBase)
- [CommDataEventArgs](#CommDataEventArgs)
- [CommunicationConfig](#CommunicationConfig)
- [CommunicationManager](#CommunicationManager)
- [ControlCommands](#ControlCommands)
- [ControlRegisters](#ControlRegisters)
- [DeviceWaitSettings](#DeviceWaitSettings)
- [EthernetXmlComm](#EthernetXmlComm)
- [GlobalCommData](#GlobalCommData)
- [ILModbusData](#ILModbusData)
- [ILModbusInspectResult](#ILModbusInspectResult)
- [InLaserModbusComm](#InLaserModbusComm)
- [InspectResultValues](#InspectResultValues)
- [KUKAConnectionEventArgs](#KUKAConnectionEventArgs)
- [KUKACorrectionData](#KUKACorrectionData)
- [KUKADataReceivedEventArgs](#KUKADataReceivedEventArgs)
- [KUKARobotData](#KUKARobotData)
- [KUKAXMLConfig](#KUKAXMLConfig)
- [KukaRsiComm](#KukaRsiComm)
- [MessageArgs](#MessageArgs)
- [ModbusErrorEventArgs](#ModbusErrorEventArgs)
- [PermissionLevel](#PermissionLevel)
- [RSIConfig](#RSIConfig)
- [RSIDataEventArgs](#RSIDataEventArgs)
- [RSIElement](#RSIElement)
- [RSIErrorEventArgs](#RSIErrorEventArgs)
- [ResultRegisters](#ResultRegisters)
- [RsiFormatAttribute](#RsiFormatAttribute)
- [RsiFormatElement](#RsiFormatElement)
- [RsiPacketFormat](#RsiPacketFormat)
- [RsiRobotPacket](#RsiRobotPacket)
- [SiemensS7Comm](#SiemensS7Comm)
- [Snapshot](#Snapshot)
- [SstTcpClient](#SstTcpClient)
- [SstTcpServer](#SstTcpServer)
- [StatusValues](#StatusValues)

## CommChannelBase

- 签名：`public abstract class CommChannelBase`
- 位置：`Comm/Communication/Abstractions/CommChannelBase.cs:32`
- 命名空间：`AdaWeldSystem.Comm.Communication.Abstractions`
- 方法（7）：
  - `void Log(string message, MessageLevel level)` — `Comm/Communication/Abstractions/CommChannelBase.cs:59`
  - `void Connect()` — `Comm/Communication/Abstractions/CommChannelBase.cs:65`
  - `void Disconnect()` — `Comm/Communication/Abstractions/CommChannelBase.cs:68`
  - `void Send(byte[] data)` — `Comm/Communication/Abstractions/CommChannelBase.cs:72`
  - `void Send(string text)` — `Comm/Communication/Abstractions/CommChannelBase.cs:79`
  - `void Dispose()` — `Comm/Communication/Abstractions/CommChannelBase.cs:90`
  - `void OnDataReceived(byte[] data, string text)` — `Comm/Communication/Abstractions/CommChannelBase.cs:95`
- 构造（1）：
  - `CommChannelBase(string tag)` — `Comm/Communication/Abstractions/CommChannelBase.cs:51`
- 属性（3）：
  - `string Name { get; set; }` — `Comm/Communication/Abstractions/CommChannelBase.cs:38`
  - `bool IsConnected { get; set; }` — `Comm/Communication/Abstractions/CommChannelBase.cs:41`
  - `string LastErrorMessage { get; set; }` — `Comm/Communication/Abstractions/CommChannelBase.cs:44`

## CommDataEventArgs

- 签名：`public class CommDataEventArgs : EventArgs`
- 位置：`Comm/Communication/Abstractions/CommChannelBase.cs:9`
- 命名空间：`AdaWeldSystem.Comm.Communication.Abstractions`
- 构造（1）：
  - `CommDataEventArgs(byte[] data, string text)` — `Comm/Communication/Abstractions/CommChannelBase.cs:23`
- 属性（3）：
  - `byte[] Data { get; set; }` — `Comm/Communication/Abstractions/CommChannelBase.cs:12`
  - `string Text { get; set; }` — `Comm/Communication/Abstractions/CommChannelBase.cs:15`
  - `DateTime Timestamp { get; set; }` — `Comm/Communication/Abstractions/CommChannelBase.cs:18`

## CommunicationConfig

- 签名：`public class CommunicationConfig`
- 位置：`Comm/Communication/CommunicationManager.cs:36`
- 命名空间：`AdaWeldSystem.Comm.Communication`
- 构造（1）：
  - `CommunicationConfig()` — `Comm/Communication/CommunicationManager.cs:63`

## CommunicationManager

- 签名：`public class CommunicationManager : IDisposable`
- 位置：`Comm/Communication/CommunicationManager.cs:77`
- 命名空间：`AdaWeldSystem.Comm.Communication`
- 方法（40）：
  - `void Log(string message, MessageLevel level)` — `Comm/Communication/CommunicationManager.cs:345`
  - `void HealCommunicationIni()` — `Comm/Communication/CommunicationManager.cs:350`
  - `void InitializeXmlDocuments()` — `Comm/Communication/CommunicationManager.cs:369`
  - `void EnsureElementExists(XdocumentReaderWriter xdoc, string elementName, string defaultValue)` — `Comm/Communication/CommunicationManager.cs:408`
  - `void EnsureRobotServerConfigSection()` — `Comm/Communication/CommunicationManager.cs:418`
  - `void EnsureConfigElementExists(XdocumentReaderWriter xdoc, string elementName, string defaultValue)` — `Comm/Communication/CommunicationManager.cs:455`
  - `void Dispose()` — `Comm/Communication/CommunicationManager.cs:491`
  - `void InitializeRobotComm()` — `Comm/Communication/CommunicationManager.cs:504`
  - `void UpdateRobotPose(RSIDataEventArgs e)` — `Comm/Communication/CommunicationManager.cs:593`
  - `void RsiComm_DataReceived(object sender, RSIDataEventArgs e)` — `Comm/Communication/CommunicationManager.cs:608`
  - `void BuildReplyFormatElement()` — `Comm/Communication/CommunicationManager.cs:624`
  - `void BuildSendFormatElement()` — `Comm/Communication/CommunicationManager.cs:641`
  - `void HasRequiredElements(XElement section, string rootTag, string[] requiredTags)` — `Comm/Communication/CommunicationManager.cs:660`
  - `void EnsureRsiFormatSections(XdocumentReaderWriter xdoc)` — `Comm/Communication/CommunicationManager.cs:684`
  - `bool TryGetRobotPose(RobotPoseSnapshot pose)` — `Comm/Communication/CommunicationManager.cs:733`
  - `bool ConnectRobot()` — `Comm/Communication/CommunicationManager.cs:744`
  - `bool DisconnectRobot()` — `Comm/Communication/CommunicationManager.cs:761`
  - `bool EnsureRobotChannelHealthy()` — `Comm/Communication/CommunicationManager.cs:778`
  - `void SendRobotData(KUKARobotData data)` — `Comm/Communication/CommunicationManager.cs:812`
  - `bool SendRobotCommandByName(string command)` — `Comm/Communication/CommunicationManager.cs:824`
  - `void SendRobotCommand(int txCmd, = 0.0)` — `Comm/Communication/CommunicationManager.cs:839`
  - `void ClearRobotCommand()` — `Comm/Communication/CommunicationManager.cs:847`
  - `void UpdateRobotWeldParams(double laserPower, double wireSpeed, = 0.0, = 0.0, = 0.0)` — `Comm/Communication/CommunicationManager.cs:861`
  - `void SetRsiCycleMs(int cycleMs)` — `Comm/Communication/CommunicationManager.cs:869`
  - `string SaveRobotRsiXml()` — `Comm/Communication/CommunicationManager.cs:885`
  - `void WriteXmlWithRetry(string filePath, Func<XDocument> docFactory)` — `Comm/Communication/CommunicationManager.cs:964`
  - `void TryDeleteTempFile(string path)` — `Comm/Communication/CommunicationManager.cs:1008`
  - `void InitializePlcComm()` — `Comm/Communication/CommunicationManager.cs:1030`
  - `void InitializeModbusComm()` — `Comm/Communication/CommunicationManager.cs:1051`
  - `void ReloadFromDisk()` — `Comm/Communication/CommunicationManager.cs:1077`
  - `void Load()` — `Comm/Communication/CommunicationManager.cs:1090`
  - `void Save()` — `Comm/Communication/CommunicationManager.cs:1144`
  - `void AddOrUpdate(CommunicationConfig config)` — `Comm/Communication/CommunicationManager.cs:1180`
  - `void Remove(string name)` — `Comm/Communication/CommunicationManager.cs:1198`
  - ` GetByName(string name)` — `Comm/Communication/CommunicationManager.cs:1210`
  - `List<CommunicationConfig> GetByType(CommunicationType type)` — `Comm/Communication/CommunicationManager.cs:1217`
  - `void GetElementBool(XElement parent, string name, bool defaultValue)` — `Comm/Communication/CommunicationManager.cs:1224`
  - `void GetElementInt(XElement parent, string name, int defaultValue)` — `Comm/Communication/CommunicationManager.cs:1230`
  - `void GetElementValue(XElement parent, string name, string defaultValue)` — `Comm/Communication/CommunicationManager.cs:1236`
  - `void InitializeDefaultConfigs()` — `Comm/Communication/CommunicationManager.cs:1242`
- 构造（1）：
  - `CommunicationManager()` — `Comm/Communication/CommunicationManager.cs:309`
- 属性（21）：
  - `EthernetXmlComm EthernetComm { get; set; }` — `Comm/Communication/CommunicationManager.cs:155`
  - `KukaRsiComm RsiComm { get; set; }` — `Comm/Communication/CommunicationManager.cs:158`
  - `SiemensS7Comm S7Comm { get; set; }` — `Comm/Communication/CommunicationManager.cs:161`
  - `InLaserModbusComm ModbusComm { get; set; }` — `Comm/Communication/CommunicationManager.cs:164`
  - `List<CommunicationConfig> Configs { get; set; }` — `Comm/Communication/CommunicationManager.cs:167`
  - `bool ShowCommLog { get; set; }` — `Comm/Communication/CommunicationManager.cs:173`
  - `bool ShowDebugLog { get; set; }` — `Comm/Communication/CommunicationManager.cs:184`
  - `bool ShowRobotCommLog { get; set; }` — `Comm/Communication/CommunicationManager.cs:196`
  - `bool ShowPlcCommLog { get; set; }` — `Comm/Communication/CommunicationManager.cs:207`
  - `bool ShowModbusCommLog { get; set; }` — `Comm/Communication/CommunicationManager.cs:218`
  - `bool IsPlcEnabled { get; set; }` — `Comm/Communication/CommunicationManager.cs:229`
  - `bool IsRobotEnabled { get; set; }` — `Comm/Communication/CommunicationManager.cs:240`
  - `bool NeedHeartbeat { get; set; }` — `Comm/Communication/CommunicationManager.cs:251`
  - `bool IsGeneralEnabled { get; set; }` — `Comm/Communication/CommunicationManager.cs:257`
  - `bool HasRobotPose { get; set; }` — `Comm/Communication/CommunicationManager.cs:268`
  - `bool RobotConnected { get; set; }` — `Comm/Communication/CommunicationManager.cs:280`
  - `bool IsRobotOnline { get; set; }` — `Comm/Communication/CommunicationManager.cs:286`
  - `string LastRobotConnectError { get; set; }` — `Comm/Communication/CommunicationManager.cs:292`
  - `DateTime LastRobotReceiveTime { get; set; }` — `Comm/Communication/CommunicationManager.cs:298`
  - `int RsiCycleMs { get; set; }` — `Comm/Communication/CommunicationManager.cs:303`
  - `RobotCommModeType RobotCommMode { get; set; }` — `Comm/Communication/CommunicationManager.cs:475`

## ControlCommands

- 签名：`public static class ControlCommands`
- 位置：`Comm/Communication/Implementations/InLaserModbusComm.cs:543`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 成员：（无）

## ControlRegisters

- 签名：`public static class ControlRegisters`
- 位置：`Comm/Communication/Implementations/InLaserModbusComm.cs:409`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 成员：（无）

## DeviceWaitSettings

- 签名：`public static class DeviceWaitSettings`
- 位置：`Comm/SystemComm/DeviceWaitSettings.cs:6`
- 命名空间：`AdaWeldSystem.Comm.SystemComm`
- 方法（1）：
  - `void Publish(double cameraAcquireSeconds, double recordFlushSeconds, int lineLaserCallbackMs, int modbusConnectMs, int modbusReadWriteMs)` — `Comm/SystemComm/DeviceWaitSettings.cs:42`
- 属性（5）：
  - `double CameraAcquireSeconds { get; set; }` — `Comm/SystemComm/DeviceWaitSettings.cs:27`
  - `double RecordFlushSeconds { get; set; }` — `Comm/SystemComm/DeviceWaitSettings.cs:30`
  - `int LineLaserCallbackMs { get; set; }` — `Comm/SystemComm/DeviceWaitSettings.cs:33`
  - `int ModbusConnectMs { get; set; }` — `Comm/SystemComm/DeviceWaitSettings.cs:36`
  - `int ModbusReadWriteMs { get; set; }` — `Comm/SystemComm/DeviceWaitSettings.cs:39`

## EthernetXmlComm

- 签名：`public class EthernetXmlComm : CommChannelBase`
- 位置：`Comm/Communication/Implementations/EthernetXmlComm.cs:13`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 方法（12）：
  - `void Connect()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:53`
  - `void Disconnect()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:59`
  - `void Dispose()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:66`
  - `void StartServer()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:80`
  - `void StopServer()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:86`
  - `void ConnectClient()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:96`
  - `void DisconnectClient()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:102`
  - `void Send(byte[] data)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:109`
  - `void Send(string text)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:116`
  - `bool SendXmlDocument(string rootName, string>> elements)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:125`
  - `string BuildXmlDocument(string rootName, string>> elements)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:145`
  - `Dictionary<string, string> ParseXmlDocument(string xml)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:175`
- 构造（1）：
  - `EthernetXmlComm()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:43`
- 属性（4）：
  - `string Name { get; set; }` — `Comm/Communication/Implementations/EthernetXmlComm.cs:19`
  - `bool IsConnected { get; set; }` — `Comm/Communication/Implementations/EthernetXmlComm.cs:25`
  - `SstTcpServer Server { get; set; }` — `Comm/Communication/Implementations/EthernetXmlComm.cs:31`
  - `SstTcpClient Client { get; set; }` — `Comm/Communication/Implementations/EthernetXmlComm.cs:37`

## GlobalCommData

- 签名：`static class GlobalCommData`
- 位置：`Comm/SystemComm/SystemComm.cs:50`
- 命名空间：`AdaWeldSystem.Comm.SystemComm`
- 方法（9）：
  - `void IsDuplicateWithinSecond(string tag, string message, MessageLevel level)` — `Comm/SystemComm/SystemComm.cs:93`
  - `void ShowLog(string TAG, string message, = MessageLevel.Info, = MessageType.Debug)` — `Comm/SystemComm/SystemComm.cs:114`
  - `void ShowCommunicationLog(string source, string message)` — `Comm/SystemComm/SystemComm.cs:167`
  - `void ShowCommLogForView(string source, string message)` — `Comm/SystemComm/SystemComm.cs:186`
  - `void MarkUiReady()` — `Comm/SystemComm/SystemComm.cs:218`
  - `void MarkAppRunning()` — `Comm/SystemComm/SystemComm.cs:224`
  - `void BroadcastCommunicationCommand(string message)` — `Comm/SystemComm/SystemComm.cs:231`
  - `void SetOperateLevel(OperateLevel level)` — `Comm/SystemComm/SystemComm.cs:251`
  - `void UIConfigSetting()` — `Comm/SystemComm/SystemComm.cs:305`
- 构造（1）：
  - `GlobalCommData()` — `Comm/SystemComm/SystemComm.cs:275`
- 属性（4）：
  - `bool ShowDebugToUi { get; set; }` — `Comm/SystemComm/SystemComm.cs:81`
  - `bool IsUiReady { get; set; }` — `Comm/SystemComm/SystemComm.cs:206`
  - `bool IsAppRunning { get; set; }` — `Comm/SystemComm/SystemComm.cs:212`
  - `DateTime SoftwareStartTime { get; set; }` — `Comm/SystemComm/SystemComm.cs:263`

## ILModbusData

- 签名：`public static class ILModbusData`
- 位置：`Comm/Communication/Implementations/InLaserModbusComm.cs:402`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 方法（8）：
  - `float ToMillimeter(ushort registerValue)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:489`
  - `ushort FromMillimeter(float mmValue)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:496`
  - `float ToDegree(ushort registerValue)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:503`
  - `ushort FromDegree(float degreeValue)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:510`
  - `float ToPercent(ushort registerValue)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:517`
  - `float ToTemperature(ushort registerValue)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:524`
  - `string ToFirmwareVersion(ushort regValue)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:531`
  - `ushort[] GetStatusRegisterAddresses()` — `Comm/Communication/Implementations/InLaserModbusComm.cs:595`

## ILModbusInspectResult

- 签名：`public class ILModbusInspectResult`
- 位置：`Comm/Communication/Implementations/InLaserModbusComm.cs:624`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 方法（2）：
  - ` FromRegisters(ushort[] registers, ushort firmwareReg)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:681`
  - `string ToString()` — `Comm/Communication/Implementations/InLaserModbusComm.cs:729`
- 属性（17）：
  - `ushort InspectResult { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:627`
  - `float SeamWidthMm { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:630`
  - `float SeamHeightMm { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:633`
  - `float SeamOffsetXmm { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:636`
  - `float SeamOffsetYmm { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:639`
  - `float SeamAreaMm2 { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:642`
  - `float SeamAngleDeg { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:645`
  - `ushort ContourPointCount { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:648`
  - `ushort FrameRate { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:651`
  - `float LaserPowerPercent { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:654`
  - `ushort ExposureTime { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:657`
  - `float DeviceTempC { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:660`
  - `uint RunTimeSeconds { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:663`
  - `uint TotalCount { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:666`
  - `uint OkCount { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:669`
  - `uint NgCount { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:672`
  - `string FirmwareVersion { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:675`

## InLaserModbusComm

- 签名：`public class InLaserModbusComm : CommChannelBase`
- 位置：`Comm/Communication/Implementations/InLaserModbusComm.cs:12`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 方法（14）：
  - `void Connect()` — `Comm/Communication/Implementations/InLaserModbusComm.cs:77`
  - `void Disconnect()` — `Comm/Communication/Implementations/InLaserModbusComm.cs:83`
  - `bool Open()` — `Comm/Communication/Implementations/InLaserModbusComm.cs:90`
  - `void Close()` — `Comm/Communication/Implementations/InLaserModbusComm.cs:128`
  - `void Dispose()` — `Comm/Communication/Implementations/InLaserModbusComm.cs:145`
  - `ushort[] ReadHoldingRegisters(ushort startAddress, ushort count)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:156`
  - `bool WriteSingleRegister(ushort address, ushort value)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:197`
  - `bool WriteMultipleRegisters(ushort startAddress, ushort[] values)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:225`
  - `void Execute(byte[] pdu)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:268`
  - `void ReadExact(NetworkStream stream, byte[] buffer, int offset, int count)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:339`
  - `void HandleErrorResponse(byte[] response)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:355`
  - `void OnConnected()` — `Comm/Communication/Implementations/InLaserModbusComm.cs:370`
  - `void OnDisconnected()` — `Comm/Communication/Implementations/InLaserModbusComm.cs:375`
  - `void OnErrorOccurred(string message, Exception ex)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:380`
- 构造（1）：
  - `InLaserModbusComm()` — `Comm/Communication/Implementations/InLaserModbusComm.cs:66`
- 属性（7）：
  - `string Name { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:20`
  - `string RemoteIP { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:26`
  - `int RemotePort { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:29`
  - `byte SlaveId { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:32`
  - `int ConnectTimeoutMs { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:35`
  - `int ReadWriteTimeoutMs { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:38`
  - `bool IsConnected { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:41`

## InspectResultValues

- 签名：`public static class InspectResultValues`
- 位置：`Comm/Communication/Implementations/InLaserModbusComm.cs:572`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 成员：（无）

## KUKAConnectionEventArgs

- 签名：`public class KUKAConnectionEventArgs : EventArgs`
- 位置：`Comm/Communication/CommunicationManager.cs:1335`
- 命名空间：`AdaWeldSystem.Comm.Communication`
- 成员：（无）

## KUKACorrectionData

- 签名：`public class KUKACorrectionData`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:1043`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 构造（1）：
  - `KUKACorrectionData()` — `Comm/Communication/Implementations/KukaRsiComm.cs:1051`

## KUKADataReceivedEventArgs

- 签名：`public class KUKADataReceivedEventArgs : EventArgs`
- 位置：`Comm/Communication/CommunicationManager.cs:1321`
- 命名空间：`AdaWeldSystem.Comm.Communication`
- 成员：（无）

## KUKARobotData

- 签名：`public class KUKARobotData`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:1012`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 构造（1）：
  - `KUKARobotData()` — `Comm/Communication/Implementations/KukaRsiComm.cs:1028`

## KUKAXMLConfig

- 签名：`public static partial class KUKAXMLConfig`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:1263`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 方法（6）：
  - `string GenerateRSIXML(RSIConfig config)` — `Comm/Communication/Implementations/KukaRsiComm.cs:1268`
  - ` ParseRSIXML(string xmlContent)` — `Comm/Communication/Implementations/KukaRsiComm.cs:1324`
  - ` ParseFormatSection(XElement section)` — `Comm/Communication/Implementations/KukaRsiComm.cs:1375`
  - ` LoadPacketFormat(XdocumentReaderWriter writer, string sectionName)` — `Comm/Communication/Implementations/KukaRsiComm.cs:1416`
  - `void SaveRSIConfig(string filePath, RSIConfig config)` — `Comm/Communication/Implementations/KukaRsiComm.cs:1426`
  - ` LoadRSIConfig(string filePath)` — `Comm/Communication/Implementations/KukaRsiComm.cs:1433`

## KukaRsiComm

- 签名：`public class KukaRsiComm : CommChannelBase`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:19`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 方法（22）：
  - `void IsLocalAddressReady(IPAddress address, string nicName, string reason)` — `Comm/Communication/Implementations/KukaRsiComm.cs:234`
  - `void ResolvePlaceholder(string placeholder, double laserPower, double wireSpeed, string ipoc, double cutWireSignal, double weldSpeed, double weaveAmp, int txCmd, double txPayload, int txSeq)` — `Comm/Communication/Implementations/KukaRsiComm.cs:281`
  - `void GetAttrByIndex(XmlNode node, List<RsiFormatAttribute> attributes, int index)` — `Comm/Communication/Implementations/KukaRsiComm.cs:327`
  - `void ReceiveLoop()` — `Comm/Communication/Implementations/KukaRsiComm.cs:338`
  - `void CheckReceiveStall()` — `Comm/Communication/Implementations/KukaRsiComm.cs:415`
  - `void SendLoop()` — `Comm/Communication/Implementations/KukaRsiComm.cs:434`
  - `void ParseDouble(string value)` — `Comm/Communication/Implementations/KukaRsiComm.cs:506`
  - `void OnErrorOccurred(string message, Exception ex, RSIErrorType errorType)` — `Comm/Communication/Implementations/KukaRsiComm.cs:513`
  - `bool Initialize(string xmlConfigPath)` — `Comm/Communication/Implementations/KukaRsiComm.cs:525`
  - `bool Initialize(RSIConfig config)` — `Comm/Communication/Implementations/KukaRsiComm.cs:542`
  - `void Connect()` — `Comm/Communication/Implementations/KukaRsiComm.cs:561`
  - `void Disconnect()` — `Comm/Communication/Implementations/KukaRsiComm.cs:567`
  - `bool Start()` — `Comm/Communication/Implementations/KukaRsiComm.cs:574`
  - `bool Stop()` — `Comm/Communication/Implementations/KukaRsiComm.cs:666`
  - `void SetReplyValues(double laserPower, double wireSpeed, = 0.0, = 0.0, = 0.0)` — `Comm/Communication/Implementations/KukaRsiComm.cs:711`
  - `void SendTxCommand(int txCmd, = 0.0)` — `Comm/Communication/Implementations/KukaRsiComm.cs:728`
  - `void ClearTxCommand()` — `Comm/Communication/Implementations/KukaRsiComm.cs:740`
  - ` ParseRobotPacket(string xml)` — `Comm/Communication/Implementations/KukaRsiComm.cs:752`
  - ` ParseRobotPacket(string xml, RsiPacketFormat sendFormat)` — `Comm/Communication/Implementations/KukaRsiComm.cs:762`
  - `byte[] BuildReplyXml(double laserPower, double wireSpeed, string ipoc, string sensorType, = 0.0, = 0.0, = 0.0, = 0, = 0.0, = 0)` — `Comm/Communication/Implementations/KukaRsiComm.cs:868`
  - `byte[] BuildReplyXml(RsiPacketFormat replyFormat, double laserPower, double wireSpeed, string ipoc, string sensorType, = 0.0, = 0.0, = 0.0, = 0, = 0.0, = 0)` — `Comm/Communication/Implementations/KukaRsiComm.cs:884`
  - `void Dispose()` — `Comm/Communication/Implementations/KukaRsiComm.cs:929`
- 构造（2）：
  - `KukaRsiComm()` — `Comm/Communication/Implementations/KukaRsiComm.cs:211`
  - `KukaRsiComm(string robotIP, int robotPort, int localPort)` — `Comm/Communication/Implementations/KukaRsiComm.cs:217`
- 属性（23）：
  - `string Name { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:75`
  - `bool IsConnected { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:81`
  - `bool IsRunning { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:87`
  - `string RobotIP { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:93`
  - `int RobotPort { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:96`
  - `int LocalPort { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:99`
  - `string LocalIp { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:102`
  - `string LastError { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:105`
  - `string SenType { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:108`
  - `int CycleMs { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:111`
  - `RsiPacketFormat SendPacketFormat { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:114`
  - `RsiPacketFormat ReplyPacketFormat { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:117`
  - `RsiRobotPacket LatestPacket { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:120`
  - `long RxPacketCount { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:138`
  - `long TxPacketCount { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:144`
  - `string LastRxRaw { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:150`
  - `string LastTxRaw { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:156`
  - `int OfflineTimeoutMs { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:162`
  - `DateTime LastReceiveTime { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:168`
  - `bool IsRobotOnline { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:178`
  - `int LastRxCmd { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:193`
  - `double LastRxPayload { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:199`
  - `string LastIpoc { get; set; }` — `Comm/Communication/Implementations/KukaRsiComm.cs:205`

## MessageArgs

- 签名：`public class MessageArgs : EventArgs`
- 位置：`Comm/SystemComm/SystemComm.cs:43`
- 命名空间：`AdaWeldSystem.Comm.SystemComm`
- 成员：（无）

## ModbusErrorEventArgs

- 签名：`public class ModbusErrorEventArgs : EventArgs`
- 位置：`Comm/Communication/Implementations/InLaserModbusComm.cs:389`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 构造（1）：
  - `ModbusErrorEventArgs(string message, Exception ex)` — `Comm/Communication/Implementations/InLaserModbusComm.cs:394`
- 属性（2）：
  - `string Message { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:391`
  - `Exception Exception { get; set; }` — `Comm/Communication/Implementations/InLaserModbusComm.cs:392`

## PermissionLevel

- 签名：`public static class PermissionLevel`
- 位置：`Comm/SystemComm/PermissionLevel.cs:6`
- 命名空间：`AdaWeldSystem.Comm.SystemComm`
- 方法（5）：
  - `string GetDisplayName(OperateLevel level)` — `Comm/SystemComm/PermissionLevel.cs:11`
  - `string GetDutyText(OperateLevel level)` — `Comm/SystemComm/PermissionLevel.cs:29`
  - `bool IsAdmin(OperateLevel level)` — `Comm/SystemComm/PermissionLevel.cs:47`
  - `bool IsEngineerOrAbove(OperateLevel level)` — `Comm/SystemComm/PermissionLevel.cs:55`
  - `void SetLevel(OperateLevel level)` — `Comm/SystemComm/PermissionLevel.cs:62`

## RSIConfig

- 签名：`public class RSIConfig`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:1242`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 构造（1）：
  - `RSIConfig()` — `Comm/Communication/Implementations/KukaRsiComm.cs:1251`

## RSIDataEventArgs

- 签名：`public class RSIDataEventArgs : EventArgs`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:1059`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 成员：（无）

## RSIElement

- 签名：`public class RSIElement`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:1234`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 成员：（无）

## RSIErrorEventArgs

- 签名：`public class RSIErrorEventArgs : EventArgs`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:1075`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 成员：（无）

## ResultRegisters

- 签名：`public static class ResultRegisters`
- 位置：`Comm/Communication/Implementations/InLaserModbusComm.cs:425`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 成员：（无）

## RsiFormatAttribute

- 签名：`public class RsiFormatAttribute`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:1083`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 构造（1）：
  - `RsiFormatAttribute(string name, string placeholder)` — `Comm/Communication/Implementations/KukaRsiComm.cs:1094`

## RsiFormatElement

- 签名：`public class RsiFormatElement`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:1102`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 构造（1）：
  - `RsiFormatElement(string tag)` — `Comm/Communication/Implementations/KukaRsiComm.cs:1115`

## RsiPacketFormat

- 签名：`public class RsiPacketFormat`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:1123`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 方法（3）：
  - `void CreateTextElement(string tag, string placeholder)` — `Comm/Communication/Implementations/KukaRsiComm.cs:1144`
  - ` CreateDefaultSendFormat()` — `Comm/Communication/Implementations/KukaRsiComm.cs:1157`
  - ` CreateDefaultReplyFormat()` — `Comm/Communication/Implementations/KukaRsiComm.cs:1206`
- 构造（1）：
  - `RsiPacketFormat()` — `Comm/Communication/Implementations/KukaRsiComm.cs:1135`

## RsiRobotPacket

- 签名：`public class RsiRobotPacket`
- 位置：`Comm/Communication/Implementations/KukaRsiComm.cs:984`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 成员：（无）

## SiemensS7Comm

- 签名：`public class SiemensS7Comm : CommChannelBase`
- 位置：`Comm/Communication/Implementations/SiemensS7Comm.cs:10`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 方法（11）：
  - `void EnsureConnected()` — `Comm/Communication/Implementations/SiemensS7Comm.cs:55`
  - `void Connect()` — `Comm/Communication/Implementations/SiemensS7Comm.cs:64`
  - `void Disconnect()` — `Comm/Communication/Implementations/SiemensS7Comm.cs:83`
  - `byte[] ReadBytes(DataType dataType, int db, int startByteAdr, int count)` — `Comm/Communication/Implementations/SiemensS7Comm.cs:109`
  - `void WriteBytes(DataType dataType, int db, int startByteAdr, byte[] value)` — `Comm/Communication/Implementations/SiemensS7Comm.cs:120`
  - ` Read(string variable)` — `Comm/Communication/Implementations/SiemensS7Comm.cs:127`
  - `void Write(string variable, T value)` — `Comm/Communication/Implementations/SiemensS7Comm.cs:134`
  - `bool ReadBit(DataType dataType, int db, int startByteAdr, int bitIndex)` — `Comm/Communication/Implementations/SiemensS7Comm.cs:146`
  - `void WriteBit(DataType dataType, int db, int startByteAdr, int bitIndex, bool value)` — `Comm/Communication/Implementations/SiemensS7Comm.cs:159`
  - `string ReadString(DataType dataType, int db, int startByteAdr, int length)` — `Comm/Communication/Implementations/SiemensS7Comm.cs:176`
  - `void Dispose()` — `Comm/Communication/Implementations/SiemensS7Comm.cs:186`
- 构造（1）：
  - `SiemensS7Comm(CpuType cpuType, string ipAddress, short rack, short slot)` — `Comm/Communication/Implementations/SiemensS7Comm.cs:45`
- 属性（4）：
  - `string Name { get; set; }` — `Comm/Communication/Implementations/SiemensS7Comm.cs:21`
  - `bool IsConnected { get; set; }` — `Comm/Communication/Implementations/SiemensS7Comm.cs:27`
  - `CpuType CpuType { get; set; }` — `Comm/Communication/Implementations/SiemensS7Comm.cs:33`
  - `string IpAddress { get; set; }` — `Comm/Communication/Implementations/SiemensS7Comm.cs:39`

## Snapshot

- 签名：`private sealed class Snapshot`
- 位置：`Comm/SystemComm/DeviceWaitSettings.cs:8`
- 命名空间：`AdaWeldSystem.Comm.SystemComm`
- 成员：（无）

## SstTcpClient

- 签名：`public class SstTcpClient : IDisposable`
- 位置：`Comm/Communication/Implementations/EthernetXmlComm.cs:353`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 方法（6）：
  - `void Log(string message, MessageLevel level)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:387`
  - `void Send(string message)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:394`
  - `void Send(byte[] data)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:401`
  - `void StartConnect()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:407`
  - `void Disconnect()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:416`
  - `void Dispose()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:430`
- 构造（1）：
  - `SstTcpClient()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:379`
- 属性（3）：
  - `string TargetIp { get; set; }` — `Comm/Communication/Implementations/EthernetXmlComm.cs:362`
  - `int TargetPort { get; set; }` — `Comm/Communication/Implementations/EthernetXmlComm.cs:369`
  - `STTech.BytesIO.Tcp.TcpClient TcpClient { get; set; }` — `Comm/Communication/Implementations/EthernetXmlComm.cs:376`

## SstTcpServer

- 签名：`public class SstTcpServer : IDisposable`
- 位置：`Comm/Communication/Implementations/EthernetXmlComm.cs:208`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 方法（9）：
  - `void Log(string message, MessageLevel level)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:251`
  - `void ServerSocket_ClientDisconnected(object sender, ClientDisconnectedEventArgs e)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:259`
  - `void ServerSocket_Closed(object sender, EventArgs e)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:267`
  - `void ServerSocket_Started(object sender, EventArgs e)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:277`
  - `void ServerSocket_ClientConnected(object sender, ClientConnectedEventArgs e)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:287`
  - `void Client_OnDataReceived(object sender, STTech.BytesIO.Core.DataReceivedEventArgs e)` — `Comm/Communication/Implementations/EthernetXmlComm.cs:296`
  - `void Dispose()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:305`
  - `void StartListening()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:326`
  - `void StopListening()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:338`
- 构造（1）：
  - `SstTcpServer()` — `Comm/Communication/Implementations/EthernetXmlComm.cs:243`
- 属性（4）：
  - `string ServerIp { get; set; }` — `Comm/Communication/Implementations/EthernetXmlComm.cs:219`
  - `int ServerPort { get; set; }` — `Comm/Communication/Implementations/EthernetXmlComm.cs:226`
  - `uint ClientLimited { get; set; }` — `Comm/Communication/Implementations/EthernetXmlComm.cs:233`
  - `TcpServer ServerSocket { get; set; }` — `Comm/Communication/Implementations/EthernetXmlComm.cs:240`

## StatusValues

- 签名：`public static class StatusValues`
- 位置：`Comm/Communication/Implementations/InLaserModbusComm.cs:559`
- 命名空间：`AdaWeldSystem.Comm.Communication.Implementations`
- 成员：（无）

## 相关页面

- [[architecture/CodeMap]]
