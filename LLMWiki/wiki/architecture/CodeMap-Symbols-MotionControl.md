---
title: CodeMap-Symbols-MotionControl — 代码地图·符号签名层·MotionControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-MotionControl — MotionControl 的类型与签名

> **一句话**：模块 `MotionControl` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> 运控：Y / TA 两轴 + 焊接头从站 OD（0x7000 / 0x6020 / 0x7010）
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.MotionControl.DeltaEtherCAT` | 14 | 23 | 运控 · 台达 EtherCAT 三层 | [[modules/MotionControl]] | ADR-027/030/040/079 |
| `AdaWeldSystem.MotionControl.DeltaEtherCAT.Native` | 8 | 8 | 运控 · 台达 P/Invoke 封装 | [[modules/MotionControl]] | ADR-027 |
| `AdaWeldSystem.MotionControl.IMotion` | 8 | 10 | 运控 · 抽象契约（轴/IO/缸） | [[modules/MotionControl]] | ADR-006/027 |
| `AdaWeldSystem.MotionControl` | 6 | 14 | 运控 · Manager 与从站设备 | [[modules/MotionControl]] | ADR-027/028/030 |

| 项 | 值 |
|---|---|
| 类型数 | 55 |
| 方法数 | 882 |

## 章节导航

- [AxisInstructionEntry](#AxisInstructionEntry)
- [AxisRegistry](#AxisRegistry)
- [AxisStatusBits](#AxisStatusBits)
- [ConfigDirectoryScan](#ConfigDirectoryScan)
- [ConfigPackageFile](#ConfigPackageFile)
- [ConfigPackageManifest](#ConfigPackageManifest)
- [CspResult](#CspResult)
- [Cylinder](#Cylinder)
- [CylinderRegistry](#CylinderRegistry)
- [DeltaAxisConfig](#DeltaAxisConfig)
- [DeltaControllerConfigImporter](#DeltaControllerConfigImporter)
- [DeltaCylinderConfig](#DeltaCylinderConfig)
- [DeltaErrorCode](#DeltaErrorCode)
- [DeltaIOConfig](#DeltaIOConfig)
- [DeltaInputIO](#DeltaInputIO)
- [DeltaMontionAxis](#DeltaMontionAxis)
- [DeltaMontionControl](#DeltaMontionControl)
- [DeltaMotionConfig](#DeltaMotionConfig)
- [DeltaOutputIO](#DeltaOutputIO)
- [DeltaSlaveDevice](#DeltaSlaveDevice)
- [DeltaSlaveScanner](#DeltaSlaveScanner)
- [DeltaTaHomeConfig](#DeltaTaHomeConfig)
- [EsiPdoPoint](#EsiPdoPoint)
- [EtherCATAdvancedNative](#EtherCATAdvancedNative)
- [EtherCATEcam2Native](#EtherCATEcam2Native)
- [EtherCATIONative](#EtherCATIONative)
- [EtherCATMasterNative](#EtherCATMasterNative)
- [EtherCATMotionBufferNative](#EtherCATMotionBufferNative)
- [EtherCATMotionNative](#EtherCATMotionNative)
- [EtherCATPVTNative](#EtherCATPVTNative)
- [FlowTimeoutConfig](#FlowTimeoutConfig)
- [FlowTimeoutSettings](#FlowTimeoutSettings)
- [GalvoGlobalParams](#GalvoGlobalParams)
- [GalvoParams](#GalvoParams)
- [GalvoShapeParams](#GalvoShapeParams)
- [HeadAlarmStatus](#HeadAlarmStatus)
- [IORegistry](#IORegistry)
- [InputIO](#InputIO)
- [InterpolationMontionParam](#InterpolationMontionParam)
- [LaserHeadTemperatureData](#LaserHeadTemperatureData)
- [MontionAxis](#MontionAxis)
- [MontionControl](#MontionControl)
- [MontionIO](#MontionIO)
- [MontionManager](#MontionManager)
- [MotionConfigImporter](#MotionConfigImporter)
- [MoveControlData](#MoveControlData)
- [OutputIO](#OutputIO)
- [PVTResult](#PVTResult)
- [SlaveInfo](#SlaveInfo)
- [SystemConfigPackager](#SystemConfigPackager)
- [WeldHeadConfig](#WeldHeadConfig)
- [WeldHeadPdoEntry](#WeldHeadPdoEntry)
- [WeldHeadSlaveConfig](#WeldHeadSlaveConfig)
- [WeldHeadSlaveDevice](#WeldHeadSlaveDevice)
- [XlsxSheetReader](#XlsxSheetReader)

## AxisInstructionEntry

- 签名：`private sealed class AxisInstructionEntry`
- 位置：`MotionControl/MontionManager.cs:95`
- 命名空间：`AdaWeldSystem.MotionControl`
- 成员：（无）

## AxisRegistry

- 签名：`public class AxisRegistry`
- 位置：`MotionControl/AxisRegistry.cs:10`
- 命名空间：`AdaWeldSystem.MotionControl`
- 方法（9）：
  - `void Log(string message, MessageLevel level)` — `MotionControl/AxisRegistry.cs:42`
  - `void Register(string name, DeltaMontionAxis axis)` — `MotionControl/AxisRegistry.cs:54`
  - ` Get(string name)` — `MotionControl/AxisRegistry.cs:63`
  - `bool Contains(string name)` — `MotionControl/AxisRegistry.cs:71`
  - `List<DeltaMontionAxis> GetAll()` — `MotionControl/AxisRegistry.cs:78`
  - `List<string> GetNames()` — `MotionControl/AxisRegistry.cs:85`
  - `void Remove(string name)` — `MotionControl/AxisRegistry.cs:92`
  - `void Clear()` — `MotionControl/AxisRegistry.cs:98`
  - `void AttachAll(MontionControl control)` — `MotionControl/AxisRegistry.cs:105`
- 构造（1）：
  - `AxisRegistry()` — `MotionControl/AxisRegistry.cs:30`
- 属性（1）：
  - `int Count { get; set; }` — `MotionControl/AxisRegistry.cs:23`

## AxisStatusBits

- 签名：`public static class AxisStatusBits`
- 位置：`MotionControl/IMotion/MontionAxis.cs:269`
- 命名空间：`AdaWeldSystem.MotionControl.IMotion`
- 成员：（无）

## ConfigDirectoryScan

- 签名：`public sealed class ConfigDirectoryScan`
- 位置：`MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:25`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 成员：（无）

## ConfigPackageFile

- 签名：`public sealed class ConfigPackageFile`
- 位置：`MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:40`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 属性（3）：
  - `string Path { get; set; }` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:43`
  - `string Sha256 { get; set; }` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:46`
  - `long Length { get; set; }` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:49`

## ConfigPackageManifest

- 签名：`public sealed class ConfigPackageManifest`
- 位置：`MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:15`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 属性（7）：
  - `string SchemaVersion { get; set; }` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:18`
  - `string Scope { get; set; }` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:21`
  - `string MachineModel { get; set; }` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:24`
  - `string AppVersion { get; set; }` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:27`
  - `string ExportedAt { get; set; }` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:30`
  - `List<ConfigPackageFile> Files { get; set; }` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:33`
  - `List<string> Excluded { get; set; }` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:36`

## CspResult

- 签名：`public static class CspResult`
- 位置：`MotionControl/IMotion/MontionAxis.cs:319`
- 命名空间：`AdaWeldSystem.MotionControl.IMotion`
- 成员：（无）

## Cylinder

- 签名：`public class Cylinder`
- 位置：`MotionControl/IMotion/Cylinder.cs:7`
- 命名空间：`AdaWeldSystem.MotionControl.IMotion`
- 方法（12）：
  - ` Builder(string name)` — `MotionControl/IMotion/Cylinder.cs:59`
  - ` SetInStretchSensor(InputIO inputIO)` — `MotionControl/IMotion/Cylinder.cs:67`
  - ` SetInRetractSensor(InputIO inputIO)` — `MotionControl/IMotion/Cylinder.cs:76`
  - ` SetInCenterSensor(InputIO inputIO)` — `MotionControl/IMotion/Cylinder.cs:85`
  - ` SetOutCylinderStretch(OutputIO outputIO, = null)` — `MotionControl/IMotion/Cylinder.cs:95`
  - ` SetOutCylinderRetract(OutputIO outputIO, = null)` — `MotionControl/IMotion/Cylinder.cs:106`
  - `bool IsInStretch()` — `MotionControl/IMotion/Cylinder.cs:115`
  - `bool IsInRetract()` — `MotionControl/IMotion/Cylinder.cs:122`
  - `bool IsInCenter()` — `MotionControl/IMotion/Cylinder.cs:129`
  - `void Stretch()` — `MotionControl/IMotion/Cylinder.cs:135`
  - `void Retract()` — `MotionControl/IMotion/Cylinder.cs:143`
  - `IEnumerable<MontionIO> GetAllIO()` — `MotionControl/IMotion/Cylinder.cs:152`
- 构造（1）：
  - `Cylinder(string name)` — `MotionControl/IMotion/Cylinder.cs:45`
- 属性（8）：
  - `string Name { get; set; }` — `MotionControl/IMotion/Cylinder.cs:18`
  - `InputIO InStretchSensor { get; set; }` — `MotionControl/IMotion/Cylinder.cs:21`
  - `InputIO InRetractSensor { get; set; }` — `MotionControl/IMotion/Cylinder.cs:24`
  - `InputIO InCenterSensor { get; set; }` — `MotionControl/IMotion/Cylinder.cs:27`
  - `OutputIO OutCylinderStretch { get; set; }` — `MotionControl/IMotion/Cylinder.cs:30`
  - `OutputIO OutCylinderRetract { get; set; }` — `MotionControl/IMotion/Cylinder.cs:33`
  - `string StretchName { get; set; }` — `MotionControl/IMotion/Cylinder.cs:36`
  - `string RetractName { get; set; }` — `MotionControl/IMotion/Cylinder.cs:39`

## CylinderRegistry

- 签名：`public class CylinderRegistry`
- 位置：`MotionControl/CylinderRegistry.cs:9`
- 命名空间：`AdaWeldSystem.MotionControl`
- 方法（9）：
  - `void Log(string message, MessageLevel level)` — `MotionControl/CylinderRegistry.cs:41`
  - `void Register(string name, Cylinder cylinder)` — `MotionControl/CylinderRegistry.cs:53`
  - ` Get(string name)` — `MotionControl/CylinderRegistry.cs:62`
  - `bool Contains(string name)` — `MotionControl/CylinderRegistry.cs:70`
  - `List<Cylinder> GetAll()` — `MotionControl/CylinderRegistry.cs:77`
  - `List<string> GetNames()` — `MotionControl/CylinderRegistry.cs:84`
  - `void Remove(string name)` — `MotionControl/CylinderRegistry.cs:91`
  - `void Clear()` — `MotionControl/CylinderRegistry.cs:97`
  - `void AttachAll(MontionControl control)` — `MotionControl/CylinderRegistry.cs:104`
- 构造（1）：
  - `CylinderRegistry()` — `MotionControl/CylinderRegistry.cs:29`
- 属性（1）：
  - `int Count { get; set; }` — `MotionControl/CylinderRegistry.cs:22`

## DeltaAxisConfig

- 签名：`public class DeltaAxisConfig`
- 位置：`MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:4`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 构造（2）：
  - `DeltaAxisConfig()` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:79`
  - `DeltaAxisConfig(string axisName, ushort nodeId, ushort slotNo)` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:97`
- 属性（22）：
  - `string AxisName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:9`
  - `ushort NodeId { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:12`
  - `ushort SlotNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:15`
  - `bool Enabled { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:18`
  - `double Equiv { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:21`
  - `double StrVel { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:24`
  - `double ConstVel { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:27`
  - `double EndVel { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:30`
  - `double AccTime { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:33`
  - `double DecTime { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:36`
  - `double STime { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:39`
  - `short HomeMode { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:42`
  - `double HomeOffset { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:45`
  - `double HomeFirstVel { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:48`
  - `double HomeSecondVel { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:51`
  - `double HomeAcc { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:54`
  - `double PositiveLimit { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:57`
  - `double NegativeLimit { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:60`
  - `ushort SoftLimitMode { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:63`
  - `bool TorqueModeEnabled { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:66`
  - `short TorqueTarget { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:69`
  - `uint TorqueSlope { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs:72`

## DeltaControllerConfigImporter

- 签名：`public static class DeltaControllerConfigImporter`
- 位置：`MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:113`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（29）：
  - `void BuildSkipList(ConfigDirectoryScan scan)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:138`
  - `void NormalizeObjectKeyHex(string text)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:153`
  - `void BuildPartialMessage(ConfigDirectoryScan scan, List<string> missingFiles, List<string> badContent, string prefix)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:171`
  - `void GenerateCore(ConfigDirectoryScan scan, string directoryPath, IList<WeldHeadPdoEntry> pdoEntries, bool tableSource, string message)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:195`
  - ` Scan(string directoryPath)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:318`
  - `string BuildPdoObjectKey(WeldHeadPdoEntry entry)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:395`
  - `List<string> GetParseFailures(ConfigDirectoryScan scan)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:414`
  - `bool Generate(string directoryPath, string message)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:432`
  - `bool Generate(string directoryPath, IList<WeldHeadPdoEntry> pdoEntries, string message)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:442`
  - `bool TryReadCsvTable(string filePath, string[] headers, List<string[]> rows, string message)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:478`
  - `void HasCsvSignature(string filePath, string signature, bool exists)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:523`
  - `void ScanWeldHeadFiles(ConfigDirectoryScan scan)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:551`
  - `void TryParseEsi(string path, ConfigDirectoryScan scan)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:589`
  - `void ReadVendorId(XDocument doc)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:638`
  - `void ReadSlaveIdentity(ConfigDirectoryScan scan)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:655`
  - `void CrossCheckProtocol(ConfigDirectoryScan scan)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:690`
  - `void ReadEsiPdoContainers(XDocument doc, Dictionary<string, List<EsiPdoPoint>> containers)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:781`
  - `void NormalizeContainerKey(string index)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:820`
  - `void BuildPdoKey(string index, string subIndex)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:832`
  - `void ParseIndexNumber(string text)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:842`
  - `void ReadChildText(XElement parent, string localName)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:859`
  - `void TryParseProtocol(string path)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:872`
  - `void BuildHeaderMap(string[] header)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:923`
  - `void GetCell(string[] row, Dictionary<string, int> map, string key)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:941`
  - `void NormalizeHeader(string text)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:951`
  - `void NormalizeHex(string text)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:960`
  - `void ParseHexUInt(string text, uint defaultValue)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:976`
  - `void ReadAttribute(XElement element, string localName)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:992`
  - `void SplitCsvLine(string line)` — `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:1004`

## DeltaCylinderConfig

- 签名：`public class DeltaCylinderConfig`
- 位置：`MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:43`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 构造（1）：
  - `DeltaCylinderConfig()` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:70`
- 属性（8）：
  - `string CylinderName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:46`
  - `string StretchSensorName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:49`
  - `string RetractSensorName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:52`
  - `string CenterSensorName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:55`
  - `string StretchOutputName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:58`
  - `string RetractOutputName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:61`
  - `string StretchActionName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:64`
  - `string RetractActionName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:67`

## DeltaErrorCode

- 签名：`public static class DeltaErrorCode`
- 位置：`MotionControl/DeltaEtherCAT/Native/DeltaErrorCode.cs:4`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT.Native`
- 方法（1）：
  - `string GetMessage(ushort code)` — `MotionControl/DeltaEtherCAT/Native/DeltaErrorCode.cs:112`

## DeltaIOConfig

- 签名：`public class DeltaIOConfig`
- 位置：`MotionControl/DeltaEtherCAT/DeltaIOConfig.cs:4`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 构造（2）：
  - `DeltaIOConfig()` — `MotionControl/DeltaEtherCAT/DeltaIOConfig.cs:31`
  - `DeltaIOConfig(string ioName, ushort nodeId, ushort slotNo, ushort bitNo)` — `MotionControl/DeltaEtherCAT/DeltaIOConfig.cs:43`
- 属性（6）：
  - `string IOName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaIOConfig.cs:9`
  - `ushort NodeId { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaIOConfig.cs:12`
  - `ushort SlotNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaIOConfig.cs:15`
  - `ushort BitNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaIOConfig.cs:18`
  - `bool Enabled { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaIOConfig.cs:21`
  - `string Remark { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaIOConfig.cs:24`

## DeltaInputIO

- 签名：`public class DeltaInputIO : InputIO`
- 位置：`MotionControl/DeltaEtherCAT/DeltaInputIO.cs:8`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（2）：
  - `bool IsON()` — `MotionControl/DeltaEtherCAT/DeltaInputIO.cs:54`
  - `int GetIOStatus()` — `MotionControl/DeltaEtherCAT/DeltaInputIO.cs:61`
- 构造（1）：
  - `DeltaInputIO(MontionControl mControl, string ioName, ushort nodeId, ushort slotNo)` — `MotionControl/DeltaEtherCAT/DeltaInputIO.cs:39`
- 属性（3）：
  - `ushort CardNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaInputIO.cs:18`
  - `ushort NodeId { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaInputIO.cs:25`
  - `ushort SlotNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaInputIO.cs:28`

## DeltaMontionAxis

- 签名：`public class DeltaMontionAxis : MontionAxis`
- 位置：`MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:11`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（60）：
  - `void ReadConnectStatus(ushort opState, ushort alarmStatus)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:137`
  - `void Log(string message, MessageLevel level)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:172`
  - `void LogFail(string funcName, ushort ret)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:180`
  - `void RecordCmdOk(string funcName)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:188`
  - `void PreMotionCheck(string funcName)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:196`
  - `void EnsureDriveTorqueLimit()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:216`
  - `void ProbeTorqueLimitObjectsOnce()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:256`
  - `void TryWriteTorqueLimitSdo(int limit, string reason)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:273`
  - `void ToPulse(double value)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:361`
  - `void ToUnit(int pulse)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:370`
  - `void StartMove(double pos, double minVel, double maxVel, double stopVel, double accTime, double decTime, double sTime, ushort posMode)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:385`
  - `void StartHome()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:406`
  - `void VerifyHomeModeReadback(ushort modeWord)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:477`
  - `void ToHomeModeLogical(byte raw)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:501`
  - `void ToHomeModeWord(short mode)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:509`
  - `void ReverseTorqueOutput(short targetTorque, uint slope)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:519`
  - `void WaitReverseStopDone()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:628`
  - `void LogTorqueLimitRelation(short requestedTorque, short appliedTorque, int limit)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:652`
  - `void EnsureCspMotionStoppedForTorque()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:684`
  - `void RestoreCspMode()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:707`
  - `bool IsMoving()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:718`
  - `bool WaitMoveDone()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:728`
  - `void AxisStop(ushort stopMode)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:743`
  - `bool IsServoOn()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:760`
  - `void ServoOn()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:766`
  - `void ServoOff()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:805`
  - `bool RestoreTorqueLimitAfterHome()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:821`
  - `void ResetAlarm()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:858`
  - `bool Home()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:867`
  - `bool HomeNoBlock()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:874`
  - `bool WaitHomeDone()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:881`
  - `bool AbsMove(double pos, = 1)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:941`
  - `bool AbsMove(double pos, double minVel, double maxVel, double stopVel, double accTime, double decTime, double sTime, = 1)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:956`
  - `bool AbsMoveNoBlock(double pos, = 1)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:966`
  - `bool AbsMoveNoBlock(double pos, double minVel, double maxVel, double stopVel, double accTime, double decTime, double sTime, = 1)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:981`
  - `void JogMove(ushort dir)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:989`
  - `void JogMove(double minVel, double maxVel, double stopVel, double accTime, double decTime, double sTime, ushort dir)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1002`
  - `double GetPosition()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1016`
  - `double GetCommandPosition()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1025`
  - `void SetPosition(double pos)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1034`
  - `void SetHomePosition()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1042`
  - `double GetCurrentSpeed()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1050`
  - `short GetCurrentTorque()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1059`
  - `ushort GetStatusWord()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1068`
  - `ushort GetMoveMode()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1078`
  - `ushort GetHomeStatus()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1087`
  - `bool SetTorque(short targetTorque, uint slope)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1099`
  - `bool StopTorque()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1236`
  - `bool SetSoftTargetReach(uint positionWindow, ushort windowTime, bool enable)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1270`
  - `bool TryGetSoftTargetReachStatus(ushort status)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1283`
  - `ushort GetSoftTargetReachStatus()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1294`
  - `bool ChangeSpeed(double newSpeed, double changeTime)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1308`
  - `bool StartCrdBuffer(double maxVelMmPerS, double maxAccMmPerS2)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1331`
  - `ushort BufferLineTo(double targetPosMm, double velMmPerS, double endVelMmPerS, double accMmPerS2)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1362`
  - `bool BufferStart()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1374`
  - `ushort BufferStop(ushort mode)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1387`
  - `ushort BufferRemainSize(int remainSize)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1396`
  - `ushort BufferMotionStatus(ushort status, int blockNum)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1407`
  - `ushort ReadSlaveStatus(ushort opState, ushort alarmStatus)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1420`
  - `ushort BufferClear()` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:1430`
- 构造（1）：
  - `DeltaMontionAxis(MontionControl mControl, string aName, ushort nodeId, ushort slotNo)` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:154`
- 属性（21）：
  - `int MoveDoneTimeoutSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:17`
  - `int HomeDoneTimeoutSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:18`
  - `int ServoOnTimeoutSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:19`
  - `int PollIntervalMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:20`
  - `int StopSettleMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:21`
  - `double TorqueEntryStabilizeTimeoutSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:76`
  - `ushort CardNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:79`
  - `ushort NodeId { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:86`
  - `ushort SlotNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:89`
  - `double HomeOffset { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:92`
  - `double HomeFirstVel { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:95`
  - `double HomeSecondVel { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:98`
  - `double HomeAcc { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:101`
  - `string LastCommand { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:104`
  - `bool TorqueOutputEnabled { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:107`
  - `bool TorqueRetractFailed { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:110`
  - `ushort TorqueRetractFailCode { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:113`
  - `int TorqueLimitPerMille { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:116`
  - `bool FullTorqueOnEnable { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:119`
  - `bool HomeVerified { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:122`
  - `string HomeEvidence { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs:128`

## DeltaMontionControl

- 签名：`public class DeltaMontionControl : MontionControl`
- 位置：`MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:12`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（16）：
  - `void Log(string message, MessageLevel level)` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:61`
  - `void OpenAndInitialCards(string strMsg)` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:69`
  - `void WaitInitialDone(string strMsg)` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:126`
  - `void IsSlaveOperational(ushort nodeId, ushort slotNo)` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:160`
  - `void LogScanList()` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:170`
  - `bool Initialization(string strMsg)` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:189`
  - `void Close()` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:211`
  - `void AddAxis(MontionAxis axis)` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:240`
  - `void AddIO(MontionIO io)` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:248`
  - `List<MontionAxis> GetAxes()` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:263`
  - `List<InputIO> GetInPutIOs()` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:270`
  - `List<OutputIO> GetOutPutIOs()` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:277`
  - `void SetEmergencyStop(bool isEmergencyStop)` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:284`
  - ` GetControlType()` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:298`
  - ` GetManufacturerType()` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:305`
  - `bool CheckBusOK(string faultDesc)` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:314`
- 构造（1）：
  - `DeltaMontionControl(string devName)` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:47`
- 属性（5）：
  - `int InitialTimeoutSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:18`
  - `int InitialPollIntervalMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:19`
  - `ushort CardNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:33`
  - `DeltaSlaveScanner SlaveScanner { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:36`
  - `ushort ExistCardCount { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs:39`

## DeltaMotionConfig

- 签名：`public class DeltaMotionConfig`
- 位置：`MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:291`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（38）：
  - `string AxisOwnerKey(string axisName)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:325`
  - `void Log(string message, MessageLevel level)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:448`
  - `void LogLegacyKeyRename()` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:454`
  - `void ReadDouble(XdocumentReaderWriter reader, string path, double def)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:494`
  - `void ReadInt(XdocumentReaderWriter reader, string path, int def)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:505`
  - `void ReadUShort(XdocumentReaderWriter reader, string path, ushort def)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:516`
  - `void ReadBool(XdocumentReaderWriter reader, string path, bool def)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:527`
  - `void ReadWeldHeadEnabled(XdocumentReaderWriter reader)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:537`
  - `void ReadHexUInt(XdocumentReaderWriter reader, string path, uint def)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:560`
  - `void Text(double value)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:571`
  - `void LoadFlowTimeouts(XdocumentReaderWriter reader, bool writeLog)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:580`
  - `void ReadAxis(XElement element)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:639`
  - `void LoadTaHome(XdocumentReaderWriter reader, bool writeLog)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:678`
  - `void NormalizeTaTorqueLimit()` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:714`
  - `void ReadIO(XElement element)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:735`
  - `void ReadCylinder(XElement element)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:752`
  - `void WriteIO(XdocumentReaderWriter reader, XElement parent, DeltaIOConfig io)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:772`
  - `void WriteCylinder(XdocumentReaderWriter reader, XElement parent, DeltaCylinderConfig cyl)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:787`
  - `void ChildValue(XElement parent, string name, string def)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:805`
  - `void ChildValueAny(XElement parent, string def)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:816`
  - `void ParseDouble(string txt)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:830`
  - `void ParseUShort(string txt)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:838`
  - `void ParseShort(string txt)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:847`
  - `void ParseInt(string txt)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:855`
  - `void FindIO(List<DeltaIOConfig> list, string ioName)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:863`
  - `void WriteConfigNodes(XdocumentReaderWriter reader)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:876`
  - `void LoadConfig()` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1002`
  - `void LoadConfig(bool writeLog)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1009`
  - `void LoadConfig(bool writeLog, bool allowHeal)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1018`
  - `void ValidateNodeIdConflicts()` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1121`
  - `void RegisterNodeOwner(Dictionary<string, string> occupied, ushort nodeId, ushort slotNo, string ownerKey, string ownerLabel)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1148`
  - `void SaveConfig()` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1165`
  - `void SaveConfig(string backupFolder)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1173`
  - `void SelfHealMissingKeys(bool allowWrite, bool includeTorqueDirection)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1205`
  - ` GetAxis(string axisName)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1237`
  - ` GetInput(string ioName)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1250`
  - ` GetOutput(string ioName)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1258`
  - ` GetCylinder(string cylinderName)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:1266`
- 构造（1）：
  - `DeltaMotionConfig()` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:414`
- 属性（24）：
  - `List<string> ConflictingDeviceKeys { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:317`
  - `string ConfigFileName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:335`
  - `ushort CardNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:342`
  - `int InitialTimeoutMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:345`
  - `int InitialPollIntervalMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:348`
  - `bool WatchDogEnable { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:351`
  - `double WatchDogSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:354`
  - `IList<DeltaAxisConfig> Axes { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:357`
  - `IList<DeltaIOConfig> Inputs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:360`
  - `IList<DeltaIOConfig> Outputs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:363`
  - `IList<DeltaCylinderConfig> Cylinders { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:366`
  - `PVTTimeMode PVTTimeMode { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:369`
  - `int PVTBatchSize { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:372`
  - `int PVTRefillThreshold { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:375`
  - `double PVTSmoothStopTime { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:378`
  - `double TrackMaxVel { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:381`
  - `double TrackMaxAcc { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:384`
  - `double TrackFeedForwardSec { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:387`
  - `double TrackDeadZone { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:390`
  - `WeldHeadSlaveConfig WeldHeadSlave { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:395`
  - `string SeamTrackAxisName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:398`
  - `string TaAxisName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:401`
  - `DeltaTaHomeConfig TaHome { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:404`
  - `FlowTimeoutConfig FlowTimeouts { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:407`

## DeltaOutputIO

- 签名：`public class DeltaOutputIO : OutputIO`
- 位置：`MotionControl/DeltaEtherCAT/DeltaOutputIO.cs:8`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（6）：
  - `void IsBusReady()` — `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs:54`
  - `void LogFail(string funcName, ushort ret)` — `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs:66`
  - `bool IsON()` — `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs:78`
  - `int GetIOStatus()` — `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs:85`
  - `int SetON()` — `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs:100`
  - `int SetOFF()` — `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs:112`
- 构造（1）：
  - `DeltaOutputIO(MontionControl mControl, string ioName, ushort nodeId, ushort slotNo)` — `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs:39`
- 属性（3）：
  - `ushort CardNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs:18`
  - `ushort NodeId { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs:25`
  - `ushort SlotNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs:28`

## DeltaSlaveDevice

- 签名：`public class DeltaSlaveDevice`
- 位置：`MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:9`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（19）：
  - `void Log(string message, MessageLevel level)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:66`
  - `void WaitSdoDone(ushort slotNo)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:74`
  - `string Describe(SdoResult result)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:113`
  - ` ReadSdo(ushort index, ushort subIndex, ushort size, byte[] buffer)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:140`
  - `bool SdoRead(ushort index, ushort subIndex, ushort size, byte[] buffer)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:189`
  - ` WriteSdo(ushort index, ushort subIndex, ushort size, byte[] data)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:205`
  - `bool SdoWrite(ushort index, ushort subIndex, ushort size, byte[] data)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:238`
  - `bool PdoGet(ushort odIndex, ushort odSubIndex, ushort size, byte[] buffer, = 0)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:254`
  - `bool PdoSet(ushort odIndex, ushort odSubIndex, byte[] data)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:280`
  - `bool ReadUInt16(ushort index, ushort subIndex, ushort value)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:306`
  - `bool ReadInt16(ushort index, ushort subIndex, short value)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:320`
  - `bool ReadUInt32(ushort index, ushort subIndex, uint value)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:334`
  - `bool PdoGetScaledUInt16(ushort odIndex, ushort odSubIndex, double scale, double value)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:349`
  - `bool PdoGetScaledInt16(ushort odIndex, ushort odSubIndex, double scale, double value)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:364`
  - `bool PdoSetScaledUInt16(ushort odIndex, ushort odSubIndex, double scale, double value)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:379`
  - `bool PdoSetScaledInt16(ushort odIndex, ushort odSubIndex, double scale, double value)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:392`
  - `bool PdoSetBool(ushort odIndex, ushort odSubIndex, bool value)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:404`
  - `bool PdoGetBool(ushort odIndex, ushort odSubIndex, bool value)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:414`
  - `bool PdoGetByte(ushort odIndex, ushort odSubIndex, byte value)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:428`
- 构造（1）：
  - `DeltaSlaveDevice(ushort cardNo, ushort nodeId, ushort slotNo)` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:52`
- 属性（7）：
  - `int SdoPollIntervalMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:15`
  - `int SdoPollMaxCount { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:16`
  - `int SdoPreDelayMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:19`
  - `int SdoMailboxRetryDelayMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:22`
  - `ushort CardNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:36`
  - `ushort NodeId { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:39`
  - `ushort SlotNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs:42`

## DeltaSlaveScanner

- 签名：`public class DeltaSlaveScanner`
- 位置：`MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:32`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（4）：
  - `void IdentifyDevice(SlaveInfo info)` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:64`
  - `bool Scan(ushort cardNo)` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:126`
  - `List<SlaveInfo> GetByType(SlaveDeviceType deviceType)` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:164`
  - ` FindByNodeId(ushort nodeId)` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:172`
- 构造（1）：
  - `DeltaSlaveScanner()` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:53`
- 属性（1）：
  - `List<SlaveInfo> SlaveInfos { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:46`

## DeltaTaHomeConfig

- 签名：`public class DeltaTaHomeConfig`
- 位置：`MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:6`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（3）：
  - `void CopyFrom(DeltaAxisConfig axis)` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:63`
  - `void CopyTo(DeltaAxisConfig axis)` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:75`
  - `int GetTorqueLimitPerMille()` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:87`
- 构造（1）：
  - `DeltaTaHomeConfig()` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:42`
- 属性（9）：
  - `short HomeMode { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:9`
  - `double HomeFirstVel { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:12`
  - `double HomeSecondVel { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:15`
  - `double HomeAcc { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:18`
  - `double WorkOriginMm { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:21`
  - `double Force100PctN { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:24`
  - `double TorqueLimitN { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:27`
  - `int TorqueDirection { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:32`
  - `bool TorqueDirectionKeyPresent { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs:39`

## EsiPdoPoint

- 签名：`private sealed class EsiPdoPoint`
- 位置：`MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs:767`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 成员：（无）

## EtherCATAdvancedNative

- 签名：`public static class EtherCATAdvancedNative`
- 位置：`MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:6`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT.Native`
- 方法（11）：
  - `ushort CS_ECAT_Slave_CSP_Start_Multiaxes_Move(ushort CardNo, ushort AxisNum, ushort AxisArray, ushort SlotArray, int Dist, int StrVel, int ConstVel, int EndVel, double Tacc, double Tdec, ushort SCurve, ushort IsAbs)` — `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:15`
  - `ushort CS_ECAT_Slave_CSP_Start_Arc_Move(ushort CardNo, ushort NodeID, ushort SlotNo, int CenterPoint, double Angle, int StrVel, int ConstVel, int EndVel, double Tacc, double Tdec, ushort SCurve, ushort IsAbs)` — `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:21`
  - `ushort CS_ECAT_Slave_CSP_Start_Heli_Move(ushort CardNo, ushort NodeID, ushort SlotNo, int CenterPoint, int Depth, int Pitch, ushort Dir, int StrVel, int ConstVel, int EndVel, double Tacc, double Tdec, ushort SCurve, ushort IsAbs)` — `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:27`
  - `ushort CS_ECAT_Slave_CSP_Sync_Config(ushort CardNo, ushort AxisNum, ushort AxisArray, ushort SlotArray, ushort Enable)` — `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:33`
  - `ushort CS_ECAT_Slave_CSP_Sync_Move(ushort CardNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:38`
  - `ushort CS_ECAT_Slave_CSP_Gantry_Enable(ushort CardNo, ushort GantryNo, ushort MasterNodeID, ushort MasterSlotID, ushort SlaveNodeID, ushort SlaveSlotID, int Motor_Pulse_Per_Turn, double Motor_MaxTorque, double K_I, double K_VI, double Filter_Frequency, ushort Enable)` — `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:42`
  - `ushort CS_ECAT_Slave_Motion_Set_TouchProbe_Config(ushort CardNo, ushort NodeID, ushort SlotNo, ushort TriggerMode, ushort Signal_Source)` — `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:49`
  - `ushort CS_ECAT_Slave_Motion_Get_TouchProbe_Status(ushort CardNo, ushort NodeID, ushort SlotNo, ushort Status)` — `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:54`
  - `ushort CS_ECAT_Slave_Motion_Get_TouchProbe_Position(ushort CardNo, ushort NodeID, ushort SlotNo, int LatchPosition)` — `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:59`
  - `ushort CS_ECAT_Slave_CSP_Virtual_Set_Enable(ushort CardNo, ushort NodeID, ushort SlotID, ushort Enable)` — `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:64`
  - `ushort CS_ECAT_Slave_CSP_Virtual_Set_Command(ushort CardNo, ushort NodeID, ushort SlotID, int Command)` — `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs:69`

## EtherCATEcam2Native

- 签名：`public static class EtherCATEcam2Native`
- 位置：`MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:6`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT.Native`
- 方法（24）：
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_Data(ushort CardNo, ushort CamNo, ushort DataNum, double MasterPos_mm, double SlavePos_mm, ushort Curve_Type, double Velocity_Scale)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:35`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Set_Profile_Mode(ushort CardNo, ushort Mode)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:41`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_Auto_Smooth(ushort CardNo, ushort CamNo, ushort DataNum, double SlavePosUserUnit)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:45`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Delete_Profile_Data(ushort CardNo, ushort CamNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:50`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamIn(ushort CardNo, ushort NodeID, ushort SlotID, ushort MasterNodeID, ushort MasterSlotID, ushort SourceType, ushort SourceNo, ushort CamNo, ushort Periodic, ushort MasterAbsolute, ushort SlaveAbsolute, double MasterOffset, double SlaveOffset, double MasterScaling, double SlaveScaling, ushort StartMode, int MasterAxis_mm_Pulse, int SlaveAxis_mm_Pulse, double Slave_MaxVel_mm, double Slave_Acc_mm, double Slave_Dec_mm, short MasterAxis_Dir, short SlaveAxis_Dir, ushort BufferMode)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:54`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamIn_TimeMode(ushort CardNo, ushort NodeID, ushort SlotID, ushort CamNo, ushort Periodic, ushort SlaveAbsolute, double SlaveOffset, double SlaveScaling, ushort StartMode, int SlaveAxis_mm_Pulse, double Slave_MaxVel_mm, double Slave_Acc_mm, double Slave_Dec_mm, short SlaveAxis_Dir, ushort BufferMode)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:63`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Master_Axis_Source_Unit_Type(ushort CardNo, ushort NodeID, ushort SlotID, ushort SourceUnitType, int PerodicTime)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:70`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamOut(ushort CardNo, ushort NodeID, ushort SlotID)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:75`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Disable(ushort CardNo, ushort NodeID, ushort SlotID)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:80`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamSet(ushort CardNo, ushort NodeID, ushort SlotID)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:85`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_Modify(ushort CardNo, ushort CamNo, ushort PointNo, double Parameters)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:94`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Phasing(ushort CardNo, ushort NodeID, ushort SlotID, double Dist, double MaxVel, double Acceleration, double Deceleration)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:99`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_CamSwitch(ushort CardNo, ushort CamNo, ushort SwitchNum, ushort Percent, ushort Cam_Mode)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:104`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_CamSwitch_Status(ushort CardNo, ushort NodeID, ushort SlotID, ushort Status)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:109`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Set_Engage_Parameters(ushort CardNo, ushort NodeID, ushort SlotID, ushort SourceType, ushort EngageNodeID, ushort EngageSlotID, ushort SourceNo, ushort Enable)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:114`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Set_DisEngage_Parameters(ushort CardNo, ushort NodeID, ushort SlotID, ushort SourceType, ushort DisEngageNodeID, ushort DisEngageSlotID, ushort SourceNo, ushort Enable)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:120`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Set_Compensate_Parameters(ushort CardNo, ushort NodeID, ushort SlotID, ushort SourceType, ushort CompensateNodeID, ushort CompensateSlotID, ushort SourceNo, double TargetPos, double ActiveRangeRatio, double MaxVel, double Acceleration, double Deceleration, ushort Enable)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:126`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_FlyingShear_Initial(ushort CardNo, ushort FlyingShearNo, double MasterRadius, double SlaveRadius, double CutLength, double MasterStartPosition, double MasterSyncPosition, double SlaveSyncPosition, double SlaveEndPosition, double SlaveWaitPosition, double SlaveVelocity, double SlaveAcceleration, double SlaveDeceleration)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:137`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_FlyingShear_Move(ushort CardNo, ushort NodeID, ushort SlotID, ushort FlyingShearNo, ushort MasterNodeID, ushort MasterSlotID, ushort SourceType, ushort SourceNo, int MasterAxis_PulseRev, int SlaveAxis_PulseRev, short MasterAxis_Dir, short SlaveAxis_Dir)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:145`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_RotaryCut_Initial(ushort CardNo, ushort RotCutNo, double RotaryAxisRadius, ushort RotaryAxisKnifeNum, double FeedAxisRadius, double CutLenth, double SyncStartPos, double SyncStopPos)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:152`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_RotaryCut_Move(ushort CardNo, ushort NodeID, ushort SlotID, ushort RotCutNo, ushort MasterNodeID, ushort MasterSlotID, ushort SourceType, ushort SourceNo, int RotaryAxis_PulseRev, int FeedAxis_PulseRev, short RotaryAxis_Dir, short FeedAxis_Dir)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:158`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Get_Status(ushort CardNo, ushort NodeID, ushort SlotID, ushort Status)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:169`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Get_Slave_Info(ushort CardNo, ushort NodeID, ushort SlotID, short pi16_CurrentCamNo, int pi32_CurrentTablePos)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:174`
  - `ushort CS_ECAT_Slave_CSP_Start_ECAM2_Get_PreviewTable(ushort CardNo, ushort CamNo, double MasterPosMm, double MasterOffset, double SlaveOffset, double MasterScaling, double SlaveScaling, double SlavePosMm)` — `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs:179`

## EtherCATIONative

- 签名：`public static class EtherCATIONative`
- 位置：`MotionControl/DeltaEtherCAT/Native/EtherCATIONative.cs:6`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT.Native`
- 方法（6）：
  - `ushort CS_ECAT_Slave_DIO_Get_Input_Value(ushort CardNo, ushort NodeID, ushort SlotNo, ushort value)` — `MotionControl/DeltaEtherCAT/Native/EtherCATIONative.cs:15`
  - `ushort CS_ECAT_Slave_DIO_Get_Output_Value(ushort CardNo, ushort NodeID, ushort SlotNo, ushort value)` — `MotionControl/DeltaEtherCAT/Native/EtherCATIONative.cs:20`
  - `ushort CS_ECAT_Slave_DIO_Set_Output_Value(ushort CardNo, ushort NodeID, ushort SlotNo, ushort value)` — `MotionControl/DeltaEtherCAT/Native/EtherCATIONative.cs:25`
  - `ushort CS_ECAT_Slave_DIO_Get_Single_Input_Value(ushort CardNo, ushort NodeID, ushort SlotNo, ushort BitNum, ushort value)` — `MotionControl/DeltaEtherCAT/Native/EtherCATIONative.cs:30`
  - `ushort CS_ECAT_Slave_DIO_Get_Single_Output_Value(ushort CardNo, ushort NodeID, ushort SlotNo, ushort BitNum, ushort value)` — `MotionControl/DeltaEtherCAT/Native/EtherCATIONative.cs:35`
  - `ushort CS_ECAT_Slave_DIO_Set_Single_Output_Value(ushort CardNo, ushort NodeID, ushort SlotNo, ushort BitNum, ushort value)` — `MotionControl/DeltaEtherCAT/Native/EtherCATIONative.cs:40`

## EtherCATMasterNative

- 签名：`public static class EtherCATMasterNative`
- 位置：`MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:7`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT.Native`
- 方法（28）：
  - `ushort CS_ECAT_Master_Open(ushort existcard)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:16`
  - `ushort CS_ECAT_Master_Initial(ushort CardNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:20`
  - `ushort CS_ECAT_Master_Reset(ushort CardNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:24`
  - `ushort CS_ECAT_Master_Close()` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:28`
  - `ushort CS_ECAT_Master_Get_CardSeq(ushort CardNo_seq, ushort CardNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:32`
  - `ushort CS_ECAT_Master_Get_SlaveNum(ushort CardNo, ushort SlaveNum)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:36`
  - `ushort CS_ECAT_Master_Get_Slave_Info(ushort CardNo, ushort SeqID, ushort NodeID, uint VendorID, uint ProductCode, uint RevisionNo, uint DCTime)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:40`
  - `ushort CS_ECAT_Master_Check_Initial_Done(ushort CardNo, ushort InitDone)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:45`
  - `ushort CS_ECAT_Master_Get_Initial_ErrorCode(ushort CardNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:49`
  - `ushort CS_ECAT_Master_Get_Return_Code_Message(ushort ReturnCode, string Message)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:53`
  - `ushort CS_ECAT_Slave_Get_Connect_Status(ushort CardNo, ushort NodeID, ushort SlotNo, ushort OpState, ushort AlarmStatus)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:57`
  - `ushort CS_ECAT_Slave_Request_State(ushort CardNo, ushort NodeID, ushort SlotNo, ushort OpState)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:62`
  - `ushort CS_ECAT_Slave_Get_EMCY_Data(ushort CardNo, ushort NodeID, ushort SlotNo, ushort ErrorCode, byte ErrorRegister, byte[] Data)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:67`
  - `ushort CS_ECAT_Slave_SDO_Send_Message(ushort CardNo, ushort NodeID, ushort SlotNo, ushort Index, ushort SubIndex, ushort Datasize, byte Data)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:72`
  - `ushort CS_ECAT_Slave_SDO_Read_Message(ushort CardNo, ushort NodeID, ushort SlotNo, ushort Index, ushort SubIndex, ushort Datasize, byte Data)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:77`
  - `ushort CS_ECAT_Slave_SDO_Quick_Send_Message(ushort CardNo, ushort NodeID, ushort SlotNo, ushort Index, ushort SubIndex, ushort Datasize, byte Data)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:82`
  - `ushort CS_ECAT_Slave_SDO_Check_Done(ushort CardNo, ushort NodeID, ushort SlotNo, ushort Done)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:87`
  - `ushort CS_ECAT_Slave_SDO_Get_ErrorCode(ushort CardNo, ushort NodeID, ushort SlotNo, uint ErrorCode)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:92`
  - `ushort CS_ECAT_Slave_DeltaServo_Write_Parameter(ushort CardNo, ushort NodeID, ushort SlotNo, ushort Page, ushort Index, int WriteData)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:97`
  - `ushort CS_ECAT_Slave_DeltaServo_Read_Parameter(ushort CardNo, ushort NodeID, ushort SlotNo, ushort Page, ushort Index, int ReadData)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:102`
  - `ushort CS_ECAT_Slave_PDO_Get_OD_Data(ushort CardNo, ushort NodeID, ushort SlotNo, ushort IOType, ushort ODIndex, ushort ODSubIndex, ushort ByteSize, byte Data)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:107`
  - `ushort CS_ECAT_Slave_PDO_Set_OD_Data(ushort CardNo, ushort NodeID, ushort SlotNo, ushort ODIndex, ushort ODSubIndex, byte Data)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:112`
  - `ushort CS_ECAT_Master_Get_Connect_Status(ushort CardNo, ushort Status)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:131`
  - `ushort CS_ECAT_Master_Check_Working_Counter(ushort CardNo, ushort Abnormal_Flag, ushort Working_Slave_Cnt)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:135`
  - `ushort CS_ECAT_Master_Get_Working_Counter_ErrorCounter(ushort CardNo, ushort Error_Cnt)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:140`
  - `ushort CS_ECAT_Master_Get_Frame_Counter(ushort CardNo, uint TxFrameCnt, uint RxFrameCnt, uint Frame_Error_Cnt)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:145`
  - `ushort CS_ECAT_Master_Get_Cycle_SpendTime(ushort CardNo, double Tx_Time, double Tx_MaxTime, double Rx_Time, double Rx_MaxTime)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:150`
  - `ushort CS_ECAT_Master_Virtual_NodeID_Alias_Enable(ushort CardNo, ushort Enable)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs:155`

## EtherCATMotionBufferNative

- 签名：`public static class EtherCATMotionBufferNative`
- 位置：`MotionControl/DeltaEtherCAT/Native/EtherCATMotionBufferNative.cs:6`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT.Native`
- 方法（8）：
  - `ushort CS_ECAT_Slave_CSP_Start_MotionBuffer_Set_Crd_Parameters(ushort CardNo, ushort TableNo, ushort AxisNum, ushort AxisArray, ushort SlotArray, int SycMaxVel, int SycMaxAcc, ushort S_Curve_Time, ushort Max_IO_Advance_Time, ushort SetOriginFlag, int OriginPos)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionBufferNative.cs:15`
  - `ushort CS_ECAT_Slave_CSP_Start_MotionBuffer_Line_MultiAxis2(ushort CardNo, ushort TableNo, ushort AxesNum, ushort Line_Axis, int TargetPosition, int SynTargetVel, int SynEndVel, int SynAcc, ushort AbsMode, ushort FifoNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionBufferNative.cs:23`
  - `ushort CS_ECAT_Slave_CSP_Start_MotionBuffer_Start(ushort CardNo, ushort TableNo, ushort FifoNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionBufferNative.cs:30`
  - `ushort CS_ECAT_Slave_CSP_Start_MotionBuffer_Stop(ushort CardNo, ushort TableNo, ushort FifoNo, ushort Mode)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionBufferNative.cs:35`
  - `ushort CS_ECAT_Slave_CSP_Start_MotionBuffer_Get_Remain_Buffer_Size(ushort CardNo, ushort TableNo, int RemainBufSize, ushort FifoNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionBufferNative.cs:40`
  - `ushort CS_ECAT_Slave_CSP_Start_MotionBuffer_Get_Motion_Status(ushort CardNo, ushort TableNo, ushort Status, int BlockNum, ushort FifoNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionBufferNative.cs:45`
  - `ushort CS_ECAT_Slave_CSP_Start_MotionBuffer_Clear_Buffer(ushort CardNo, ushort TableNo, ushort FifoNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionBufferNative.cs:50`
  - `ushort CS_ECAT_Slave_CSP_Start_MotionBuffer_Clear_Crd(ushort CardNo, ushort TableNo, ushort FifoNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionBufferNative.cs:55`

## EtherCATMotionNative

- 签名：`public static class EtherCATMotionNative`
- 位置：`MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:6`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT.Native`
- 方法（26）：
  - `ushort CS_ECAT_Slave_Motion_Get_MoveMode(ushort CardNo, ushort NodeID, ushort SlotNo, byte Mode)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:15`
  - `ushort CS_ECAT_Slave_Motion_Set_MoveMode(ushort CardNo, ushort NodeID, ushort SlotNo, ushort OpMode)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:20`
  - `ushort CS_ECAT_Slave_Motion_Set_Svon(ushort CardNo, ushort NodeID, ushort SlotNo, ushort On_Off)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:25`
  - `ushort CS_ECAT_Slave_Motion_Ralm(ushort CardNo, ushort NodeID, ushort SlotNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:30`
  - `ushort CS_ECAT_Slave_Motion_Set_Position(ushort CardNo, ushort NodeID, ushort SlotNo, int Pos)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:34`
  - `ushort CS_ECAT_Slave_Motion_Emg_Stop(ushort CardNo, ushort NodeID, ushort SlotNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:39`
  - `ushort CS_ECAT_Slave_Motion_Sd_Stop(ushort CardNo, ushort NodeID, ushort SlotNo, double Tdec)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:43`
  - `ushort CS_ECAT_Slave_Motion_Get_StatusWord(ushort CardNo, ushort NodeID, ushort SlotNo, ushort StatusWord)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:48`
  - `ushort CS_ECAT_Slave_Motion_Get_Command(ushort CardNo, ushort NodeID, ushort SlotNo, int Command)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:53`
  - `ushort CS_ECAT_Slave_Motion_Get_Position(ushort CardNo, ushort NodeID, ushort SlotNo, int Position)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:58`
  - `ushort CS_ECAT_Slave_Motion_Get_Actual_Position(ushort CardNo, ushort NodeID, ushort SlotNo, int ActualPosition)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:63`
  - `ushort CS_ECAT_Slave_Motion_Get_Mdone(ushort CardNo, ushort NodeID, ushort SlotNo, ushort Mdone)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:68`
  - `ushort CS_ECAT_Slave_Motion_Get_Current_Speed(ushort CardNo, ushort NodeID, ushort SlotNo, int Speed)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:73`
  - `ushort CS_ECAT_Slave_Motion_Get_Torque(ushort CardNo, ushort NodeID, ushort SlotNo, short Torque)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:78`
  - `ushort CS_ECAT_Slave_CSP_Start_Move(ushort CardNo, ushort NodeID, ushort SlotNo, int Dist, int StrVel, int ConstVel, int EndVel, double Tacc, double Tdec, ushort SCurve, ushort IsAbs)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:83`
  - `ushort CS_ECAT_Slave_CSP_Start_V_Move(ushort CardNo, ushort NodeID, ushort SlotNo, ushort Dir, int StrVel, int ConstVel, double Tacc, ushort SCurve)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:88`
  - `ushort CS_ECAT_Slave_CSP_Velocity_Change(ushort CardNo, ushort NodeID, ushort SlotNo, int NewSpeed, double Tsec)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:93`
  - `ushort CS_ECAT_Slave_CSV_Start_Move(ushort CardNo, ushort NodeID, ushort SlotNo, int Target_Velocity, double Acceleration, ushort Curve_Mode, ushort Acc_Type)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:98`
  - `ushort CS_ECAT_Slave_CST_Start_Move(ushort CardNo, ushort NodeID, ushort SlotNo, short Target_Torque, uint Slope, ushort Curve_Mode)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:103`
  - `ushort CS_ECAT_Slave_CST_Output_Enable(ushort CardNo, ushort NodeID, ushort SlotID, ushort Enable)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:108`
  - `ushort CS_ECAT_Slave_Home_Config(ushort CardNo, ushort NodeID, ushort SlotNo, ushort Mode, int Offset, uint FirstVel, uint SecondVel, uint Acceleration)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:113`
  - `ushort CS_ECAT_Slave_Home_Move(ushort CardNo, ushort NodeID, ushort SlotNo)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:118`
  - `ushort CS_ECAT_Slave_Home_Status(ushort CardNo, ushort NodeID, ushort SlotNo, ushort Status)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:122`
  - `ushort CS_ECAT_Slave_CSP_Set_Gear(ushort CardNo, ushort NodeID, ushort SlotNo, double Numerator, double Denominator, short Enable)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:127`
  - `ushort CS_ECAT_Slave_CSP_Set_SoftTargetReach(ushort CardNo, ushort NodeID, ushort SlotID, ushort Window_Time, uint Position_Window, ushort Enable)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:136`
  - `ushort CS_ECAT_Slave_CSP_Get_SoftTargetReach_Status(ushort CardNo, ushort NodeID, ushort SlotID, ushort Status)` — `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs:142`

## EtherCATPVTNative

- 签名：`public static class EtherCATPVTNative`
- 位置：`MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs:6`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT.Native`
- 方法（10）：
  - `ushort CS_ECAT_Slave_CSP_Start_PVT_Move(ushort CardNo, ushort NodeID, ushort SlotID, int DataCnt, int TargetPos, int TargetTime, int TargetVel, ushort Abs)` — `MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs:26`
  - `ushort CS_ECAT_Slave_CSP_Start_PVTComplete_Move(ushort CardNo, ushort NodeID, ushort SlotID, int DataCnt, int TargetPos, int TargetTime, int StrVel, int EndVel, ushort Abs)` — `MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs:31`
  - `ushort CS_ECAT_Slave_CSP_Start_PVT_Config(ushort CardNo, ushort NodeID, ushort SlotID, int DataCnt, int TargetPos, int TargetTime, int TargetVel, ushort Abs)` — `MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs:36`
  - `ushort CS_ECAT_Slave_CSP_Start_PVTComplete_Config(ushort CardNo, ushort NodeID, ushort SlotID, int DataCnt, int TargetPos, int TargetTime, int StrVel, int EndVel, ushort Abs)` — `MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs:41`
  - `ushort CS_ECAT_Slave_CSP_Start_PVT_Sync_Move(ushort CardNo, ushort AxisNum, ushort AxisArray, ushort SlotArray)` — `MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs:46`
  - `ushort CS_ECAT_Slave_CSP_PVT_Get_NowMotCount(ushort CardNo, ushort NodeID, ushort SlotID, ushort NowMotCount)` — `MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs:51`
  - `ushort CS_ECAT_Slave_CSP_Start_PVT_Begin_Move(ushort CardNo, ushort NodeID, ushort SlotID, int DataCount, double Pos, double Time, double Vel, ushort TimeAbsMode, ushort Finial, ushort Retain, double SdStopTime)` — `MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs:60`
  - `ushort CS_ECAT_Slave_CSP_Start_PVT_Continue_Move(ushort CardNo, ushort NodeID, ushort SlotID, int DataCount, double Pos, double Time, double Vel, ushort Finial)` — `MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs:66`
  - `ushort CS_ECAT_Slave_CSP_Start_PVT_Get_Information(ushort CardNo, ushort NodeID, ushort SlotID, int TotalMcCount, int MdoneMcCount, int RemainBufSize, ushort Status)` — `MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs:71`
  - `ushort CS_ECAT_Slave_CSP_Start_PVT_CycleStart(ushort CardNo, ushort NodeID, ushort SlotID)` — `MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs:76`

## FlowTimeoutConfig

- 签名：`public class FlowTimeoutConfig`
- 位置：`MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:84`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（3）：
  - `void Clamp(Action<string> log, string key, int value, int min, int max, int def)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:206`
  - `void Clamp(Action<string> log, string key, double value, double min, double max, double def)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:220`
  - `void Normalize(Action<string> log)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:229`
- 构造（1）：
  - `FlowTimeoutConfig()` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:168`
- 属性（27）：
  - `double InstructionDetectSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:87`
  - `int InstructionSampleMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:90`
  - `int InstructionStableSamples { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:93`
  - `int InstructionTorqueSamples { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:96`
  - `int MoveDoneSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:99`
  - `int HomeDoneSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:102`
  - `int ServoOnSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:105`
  - `int AxisPollMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:108`
  - `int StopSettleMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:111`
  - `double TorqueEntryStabilizeSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:114`
  - `double PositionReachNoChangeSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:117`
  - `double PositionReachMinSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:120`
  - `double PositionReachMaxSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:123`
  - `double PositionReachResultWaitSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:126`
  - `int SdoPollMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:129`
  - `int SdoPollMaxCount { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:132`
  - `int SdoPreDelayMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:135`
  - `int SdoMailboxRetryMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:138`
  - `int MasterInitSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:141`
  - `int MasterInitPollMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:144`
  - `int CascadeConnectMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:147`
  - `double CameraAcquireSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:150`
  - `double RecordFlushSeconds { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:153`
  - `int LineLaserCallbackMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:156`
  - `int ModbusConnectMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:159`
  - `int ModbusReadWriteMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:162`
  - `int UiRefreshMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:165`

## FlowTimeoutSettings

- 签名：`public static class FlowTimeoutSettings`
- 位置：`MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:269`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（1）：
  - `void Publish(FlowTimeoutConfig config)` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:284`
- 属性（2）：
  - `int UiRefreshMs { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:277`
  - `FlowTimeoutConfig Current { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:280`

## GalvoGlobalParams

- 签名：`public class GalvoGlobalParams`
- 位置：`MotionControl/WeldHeadSlaveDevice.cs:666`
- 命名空间：`AdaWeldSystem.MotionControl`
- 构造（1）：
  - `GalvoGlobalParams()` — `MotionControl/WeldHeadSlaveDevice.cs:699`
- 属性（10）：
  - `int Angle { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:669`
  - `double StartAngle { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:672`
  - `double EndAngle { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:675`
  - `double XCenter { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:678`
  - `double YCenter { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:681`
  - `int XCompression { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:684`
  - `int YCompression { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:687`
  - `double TargetSize { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:690`
  - `int ObliqueEllipseCorrection { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:693`
  - `bool GalvoEnable { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:696`

## GalvoParams

- 签名：`public class GalvoParams`
- 位置：`MotionControl/WeldHeadSlaveDevice.cs:573`
- 命名空间：`AdaWeldSystem.MotionControl`
- 方法（1）：
  - ` CreateLogicalHome()` — `MotionControl/WeldHeadSlaveDevice.cs:643`
- 构造（1）：
  - `GalvoParams()` — `MotionControl/WeldHeadSlaveDevice.cs:621`
- 属性（15）：
  - `WsgGalvoPattern Pattern { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:576`
  - `int Frequency { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:579`
  - `double Width { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:582`
  - `double Length { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:585`
  - `int Angle { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:588`
  - `double StartAngle { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:591`
  - `double EndAngle { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:594`
  - `double XCenter { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:597`
  - `double YCenter { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:600`
  - `int XCompression { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:603`
  - `int YCompression { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:606`
  - `double TargetSize { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:609`
  - `double ActualSize { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:612`
  - `int ObliqueEllipseCorrection { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:615`
  - `bool GalvoEnable { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:618`

## GalvoShapeParams

- 签名：`public class GalvoShapeParams`
- 位置：`MotionControl/WeldHeadSlaveDevice.cs:715`
- 命名空间：`AdaWeldSystem.MotionControl`
- 构造（2）：
  - `GalvoShapeParams()` — `MotionControl/WeldHeadSlaveDevice.cs:727`
  - `GalvoShapeParams(double width, double length, int frequency)` — `MotionControl/WeldHeadSlaveDevice.cs:738`
- 属性（3）：
  - `double Width { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:718`
  - `double Length { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:721`
  - `int Frequency { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:724`

## HeadAlarmStatus

- 签名：`public class HeadAlarmStatus`
- 位置：`MotionControl/WeldHeadSlaveDevice.cs:775`
- 命名空间：`AdaWeldSystem.MotionControl`
- 方法（1）：
  - `string Describe()` — `MotionControl/WeldHeadSlaveDevice.cs:812`
- 构造（1）：
  - `HeadAlarmStatus()` — `MotionControl/WeldHeadSlaveDevice.cs:806`
- 属性（7）：
  - `bool ProtectiveLensTempAlarm { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:778`
  - `bool ProtectiveLensRiseTempAlarm { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:781`
  - `bool CuttingAirPressureAlarm { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:784`
  - `bool DriverAlarm { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:787`
  - `bool GalvoOn { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:790`
  - `bool HasAlarm { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:793`
  - `DateTime Timestamp { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:803`

## IORegistry

- 签名：`public class IORegistry`
- 位置：`MotionControl/IORegistry.cs:9`
- 命名空间：`AdaWeldSystem.MotionControl`
- 方法（11）：
  - `void Log(string message, MessageLevel level)` — `MotionControl/IORegistry.cs:46`
  - `void RegisterInput(string name, InputIO io)` — `MotionControl/IORegistry.cs:58`
  - ` GetInput(string name)` — `MotionControl/IORegistry.cs:67`
  - `List<InputIO> GetAllInputs()` — `MotionControl/IORegistry.cs:74`
  - `void RemoveInput(string name)` — `MotionControl/IORegistry.cs:81`
  - `void RegisterOutput(string name, OutputIO io)` — `MotionControl/IORegistry.cs:89`
  - ` GetOutput(string name)` — `MotionControl/IORegistry.cs:98`
  - `List<OutputIO> GetAllOutputs()` — `MotionControl/IORegistry.cs:105`
  - `void RemoveOutput(string name)` — `MotionControl/IORegistry.cs:112`
  - `void Clear()` — `MotionControl/IORegistry.cs:118`
  - `void AttachAll(MontionControl control)` — `MotionControl/IORegistry.cs:126`
- 构造（1）：
  - `IORegistry()` — `MotionControl/IORegistry.cs:33`
- 属性（2）：
  - `int InputCount { get; set; }` — `MotionControl/IORegistry.cs:23`
  - `int OutputCount { get; set; }` — `MotionControl/IORegistry.cs:26`

## InputIO

- 签名：`public abstract class InputIO : MontionIO`
- 位置：`MotionControl/IMotion/InputIO.cs:4`
- 命名空间：`AdaWeldSystem.MotionControl.IMotion`
- 方法（1）：
  - ` GetIOType()` — `MotionControl/IMotion/InputIO.cs:22`
- 构造（1）：
  - `InputIO(MontionControl container, string ioName)` — `MotionControl/IMotion/InputIO.cs:11`

## InterpolationMontionParam

- 签名：`public class InterpolationMontionParam`
- 位置：`MotionControl/IMotion/InterpolationMontionParam.cs:4`
- 命名空间：`AdaWeldSystem.MotionControl.IMotion`
- 构造（1）：
  - `InterpolationMontionParam(InterpolationType montionType, ushort axisCount)` — `MotionControl/IMotion/InterpolationMontionParam.cs:53`
- 属性（2）：
  - `InterpolationType MontionType { get; set; }` — `MotionControl/IMotion/InterpolationMontionParam.cs:9`
  - `ushort AxisCount { get; set; }` — `MotionControl/IMotion/InterpolationMontionParam.cs:48`

## LaserHeadTemperatureData

- 签名：`public class LaserHeadTemperatureData`
- 位置：`MotionControl/WeldHeadSlaveDevice.cs:747`
- 命名空间：`AdaWeldSystem.MotionControl`
- 构造（1）：
  - `LaserHeadTemperatureData()` — `MotionControl/WeldHeadSlaveDevice.cs:768`
- 属性（6）：
  - `double ProtectiveLensTemp { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:750`
  - `double ProtectiveLensAmbientTemp { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:753`
  - `double ProtectiveLensRiseTemp { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:756`
  - `double CuttingAirPressure { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:759`
  - `byte SensorStatus { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:762`
  - `DateTime Timestamp { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:765`

## MontionAxis

- 签名：`public abstract class MontionAxis : IPVTMotion`
- 位置：`MotionControl/IMotion/MontionAxis.cs:7`
- 命名空间：`AdaWeldSystem.MotionControl.IMotion`
- 方法（28）：
  - `bool IsMoving()` — `MotionControl/IMotion/MontionAxis.cs:93`
  - `bool WaitMoveDone()` — `MotionControl/IMotion/MontionAxis.cs:97`
  - `void AxisStop(ushort stopMode)` — `MotionControl/IMotion/MontionAxis.cs:101`
  - `bool IsServoOn()` — `MotionControl/IMotion/MontionAxis.cs:105`
  - `void ServoOn()` — `MotionControl/IMotion/MontionAxis.cs:108`
  - `void ServoOff()` — `MotionControl/IMotion/MontionAxis.cs:111`
  - `void ResetAlarm()` — `MotionControl/IMotion/MontionAxis.cs:114`
  - `bool Home()` — `MotionControl/IMotion/MontionAxis.cs:118`
  - `bool HomeNoBlock()` — `MotionControl/IMotion/MontionAxis.cs:122`
  - `bool WaitHomeDone()` — `MotionControl/IMotion/MontionAxis.cs:126`
  - `bool AbsMove(double pos, = 1)` — `MotionControl/IMotion/MontionAxis.cs:132`
  - `bool AbsMove(double pos, double minVel, double maxVel, double stopVel, double accTime, double decTime, double sTime, = 1)` — `MotionControl/IMotion/MontionAxis.cs:144`
  - `bool AbsMoveNoBlock(double pos, = 1)` — `MotionControl/IMotion/MontionAxis.cs:151`
  - `bool AbsMoveNoBlock(double pos, double minVel, double maxVel, double stopVel, double accTime, double decTime, double sTime, = 1)` — `MotionControl/IMotion/MontionAxis.cs:163`
  - `void JogMove(ushort dir)` — `MotionControl/IMotion/MontionAxis.cs:168`
  - `void JogMove(double minVel, double maxVel, double stopVel, double accTime, double decTime, double sTime, ushort dir)` — `MotionControl/IMotion/MontionAxis.cs:178`
  - `double GetPosition()` — `MotionControl/IMotion/MontionAxis.cs:183`
  - `double GetCommandPosition()` — `MotionControl/IMotion/MontionAxis.cs:187`
  - `void SetPosition(double pos)` — `MotionControl/IMotion/MontionAxis.cs:191`
  - `void SetHomePosition()` — `MotionControl/IMotion/MontionAxis.cs:194`
  - `double GetCurrentSpeed()` — `MotionControl/IMotion/MontionAxis.cs:198`
  - `short GetCurrentTorque()` — `MotionControl/IMotion/MontionAxis.cs:202`
  - `ushort GetStatusWord()` — `MotionControl/IMotion/MontionAxis.cs:206`
  - `bool IsAlarm()` — `MotionControl/IMotion/MontionAxis.cs:214`
  - `ushort BeginMove(IList<PVTPoint> points, PVTTimeMode timeMode, bool isFinal, bool retain, double sdStopTime)` — `MotionControl/IMotion/MontionAxis.cs:230`
  - `ushort ContinueMove(IList<PVTPoint> points, bool isFinal)` — `MotionControl/IMotion/MontionAxis.cs:241`
  - `ushort GetInformation(PVTInformation info)` — `MotionControl/IMotion/MontionAxis.cs:250`
  - `ushort CycleStart()` — `MotionControl/IMotion/MontionAxis.cs:259`
- 构造（1）：
  - `MontionAxis(MontionControl container, string aName)` — `MotionControl/IMotion/MontionAxis.cs:73`
- 属性（14）：
  - `MontionControl Container { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:18`
  - `string AxisName { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:21`
  - `ushort AxisNo { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:24`
  - `double Equiv { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:27`
  - `double MinVel { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:30`
  - `double MaxVel { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:33`
  - `double AccTime { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:36`
  - `double DecTime { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:39`
  - `double STime { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:42`
  - `double StopVel { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:45`
  - `short HomeMode { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:48`
  - `ushort HomeDir { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:51`
  - `double HomeMaxVel { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:54`
  - `string LastCommand { get; set; }` — `MotionControl/IMotion/MontionAxis.cs:57`

## MontionControl

- 签名：`public abstract class MontionControl`
- 位置：`MotionControl/IMotion/MontionControl.cs:6`
- 命名空间：`AdaWeldSystem.MotionControl.IMotion`
- 方法（11）：
  - `bool Initialization(string strMsg)` — `MotionControl/IMotion/MontionControl.cs:65`
  - `void Close()` — `MotionControl/IMotion/MontionControl.cs:68`
  - `void AddAxis(MontionAxis axis)` — `MotionControl/IMotion/MontionControl.cs:72`
  - `void AddIO(MontionIO io)` — `MotionControl/IMotion/MontionControl.cs:76`
  - `List<MontionAxis> GetAxes()` — `MotionControl/IMotion/MontionControl.cs:80`
  - `List<InputIO> GetInPutIOs()` — `MotionControl/IMotion/MontionControl.cs:84`
  - `List<OutputIO> GetOutPutIOs()` — `MotionControl/IMotion/MontionControl.cs:88`
  - `void SetEmergencyStop(bool isEmergencyStop)` — `MotionControl/IMotion/MontionControl.cs:92`
  - ` GetControlType()` — `MotionControl/IMotion/MontionControl.cs:96`
  - ` GetManufacturerType()` — `MotionControl/IMotion/MontionControl.cs:100`
  - `bool CheckBusOK(string faultDesc)` — `MotionControl/IMotion/MontionControl.cs:106`
- 构造（1）：
  - `MontionControl(string devName)` — `MotionControl/IMotion/MontionControl.cs:53`
- 属性（4）：
  - `ushort ConnectNo { get; set; }` — `MotionControl/IMotion/MontionControl.cs:17`
  - `string DeviceName { get; set; }` — `MotionControl/IMotion/MontionControl.cs:20`
  - `bool Initial { get; set; }` — `MotionControl/IMotion/MontionControl.cs:23`
  - `bool EmergencyStop { get; set; }` — `MotionControl/IMotion/MontionControl.cs:26`

## MontionIO

- 签名：`public abstract class MontionIO`
- 位置：`MotionControl/IMotion/MontionIO.cs:4`
- 命名空间：`AdaWeldSystem.MotionControl.IMotion`
- 方法（3）：
  - `bool IsON()` — `MotionControl/IMotion/MontionIO.cs:55`
  - `int GetIOStatus()` — `MotionControl/IMotion/MontionIO.cs:59`
  - ` GetIOType()` — `MotionControl/IMotion/MontionIO.cs:63`
- 构造（1）：
  - `MontionIO(MontionControl container, string ioName)` — `MotionControl/IMotion/MontionIO.cs:40`
- 属性（4）：
  - `MontionControl Container { get; set; }` — `MotionControl/IMotion/MontionIO.cs:15`
  - `string IOName { get; set; }` — `MotionControl/IMotion/MontionIO.cs:18`
  - `ushort IONo { get; set; }` — `MotionControl/IMotion/MontionIO.cs:21`
  - `bool IOEnable { get; set; }` — `MotionControl/IMotion/MontionIO.cs:24`

## MontionManager

- 签名：`public class MontionManager`
- 位置：`MotionControl/MontionManager.cs:16`
- 命名空间：`AdaWeldSystem.MotionControl`
- 方法（85）：
  - `void IsNodeDetected(ushort nodeId)` — `MotionControl/MontionManager.cs:253`
  - `void IsAxisSlaveMissing(MontionAxis axis)` — `MotionControl/MontionManager.cs:267`
  - `bool IsSlaveDetected(ushort nodeId)` — `MotionControl/MontionManager.cs:276`
  - `string GetAxisGateReason(MontionAxis axis)` — `MotionControl/MontionManager.cs:285`
  - `string GetAxisHomingGateReason(MontionAxis axis)` — `MotionControl/MontionManager.cs:302`
  - ` GetAxisStatus(MontionAxis axis)` — `MotionControl/MontionManager.cs:319`
  - `bool TryGetAxisReadout(string axisName, double positionMm, string lastCommand, bool servoOn, bool fault)` — `MotionControl/MontionManager.cs:332`
  - `string DescribeAxisStatusWord(MontionAxis axis)` — `MotionControl/MontionManager.cs:354`
  - `string DescribeAxisCspRuntime(MontionAxis axis)` — `MotionControl/MontionManager.cs:368`
  - `string DescribeAxisCommandReturnCode(int code)` — `MotionControl/MontionManager.cs:385`
  - `string DescribeAxisRetractFailure(ushort code)` — `MotionControl/MontionManager.cs:393`
  - `string DescribeAxisDiagnosis(MontionAxis axis, string phase, bool withBus)` — `MotionControl/MontionManager.cs:404`
  - `void WaitAxisAtTargetCore(MontionAxis axis, double targetMm, double tolMm, double timeoutSeconds, double noChangeSeconds, bool requireStableSpeed, Func<bool> cancelRequested, string evidence)` — `MotionControl/MontionManager.cs:505`
  - `void MarkInitCompleted(bool allAxesReady)` — `MotionControl/MontionManager.cs:580`
  - `void NotifyAxisReadinessChanged(string axisName)` — `MotionControl/MontionManager.cs:591`
  - `void SetTaZeroPoseGate(bool done, string reason)` — `MotionControl/MontionManager.cs:602`
  - `bool TryBeginAxisInstruction(string axisName, string instructionName, CancellationToken token, string reason)` — `MotionControl/MontionManager.cs:615`
  - `void EndAxisInstruction(string axisName)` — `MotionControl/MontionManager.cs:661`
  - `bool IsAxisInstructionBusy(string axisName)` — `MotionControl/MontionManager.cs:678`
  - `string GetAxisInstructionBusyText(string axisName)` — `MotionControl/MontionManager.cs:689`
  - `void CancelAllAxisInstructions(string reason)` — `MotionControl/MontionManager.cs:704`
  - `bool WaitAxisAtTarget(MontionAxis axis, double targetMm, double tolMm, CancellationToken token, string evidence)` — `MotionControl/MontionManager.cs:725`
  - `bool WaitAxisAtTarget(MontionAxis axis, double targetMm, double tolMm, double timeoutSeconds, double noChangeSeconds, Func<bool> cancelRequested, string evidence)` — `MotionControl/MontionManager.cs:742`
  - `bool TryMoveAbsoluteNoBlock(MontionAxis axis, double targetMm, double velMmPerSec, double tolMm, bool alreadyInPosition, string rejectReason)` — `MotionControl/MontionManager.cs:757`
  - `bool WaitAxisHomed(MontionAxis axis, CancellationToken token, string evidence)` — `MotionControl/MontionManager.cs:798`
  - `bool WaitTaTorqueOn(DeltaMontionAxis axis, CancellationToken token, string evidence)` — `MotionControl/MontionManager.cs:893`
  - `bool WaitTaTorqueOff(DeltaMontionAxis axis, double holdMm, double tolMm, CancellationToken token, string evidence)` — `MotionControl/MontionManager.cs:949`
  - `bool WaitLaMotorAtTarget(double targetMm, CancellationToken token, string evidence)` — `MotionControl/MontionManager.cs:1008`
  - `void Log(string message, MessageLevel level)` — `MotionControl/MontionManager.cs:1085`
  - `void CancelAxisInstruction(string axisName)` — `MotionControl/MontionManager.cs:1092`
  - `void CreateAxesFromConfig()` — `MotionControl/MontionManager.cs:1107`
  - `void ApplyTaHomeOnLoad(DeltaAxisConfig cfg, MontionAxis axis)` — `MotionControl/MontionManager.cs:1135`
  - `void ApplyAxisConfig(MontionAxis axis, DeltaAxisConfig cfg)` — `MotionControl/MontionManager.cs:1160`
  - `void CreateIOsFromConfig()` — `MotionControl/MontionManager.cs:1181`
  - `void CreateCylindersFromConfig()` — `MotionControl/MontionManager.cs:1215`
  - `void CreateWeldHeadFromConfig()` — `MotionControl/MontionManager.cs:1285`
  - `void ReadWeldHeadInt(XdocumentReaderWriter reader, string path, int def)` — `MotionControl/MontionManager.cs:1345`
  - `void ReadWeldHeadDouble(XdocumentReaderWriter reader, string path, double def)` — `MotionControl/MontionManager.cs:1355`
  - `void ReadAttribute(XElement element, string name)` — `MotionControl/MontionManager.cs:1366`
  - `void WeldHeadText(double value)` — `MotionControl/MontionManager.cs:1376`
  - `void GalvoShapeNodeName(WsgGalvoPattern pattern)` — `MotionControl/MontionManager.cs:1384`
  - `bool LoadTaAxisConfig()` — `MotionControl/MontionManager.cs:1398`
  - `void SaveWeldHeadConfig()` — `MotionControl/MontionManager.cs:1421`
  - `void LoadWeldHeadConfig()` — `MotionControl/MontionManager.cs:1490`
  - `void FindAxisNameByKeys(string[] keys)` — `MotionControl/MontionManager.cs:1575`
  - `void IsTaAxis(MontionAxis axis)` — `MotionControl/MontionManager.cs:1595`
  - `void ExitTaTorqueMode(MontionAxis axis, string action)` — `MotionControl/MontionManager.cs:1610`
  - `bool Initialization(string devName, string msg)` — `MotionControl/MontionManager.cs:1622`
  - `void AttachAll()` — `MotionControl/MontionManager.cs:1647`
  - `bool ReloadRuntimeFromConfig()` — `MotionControl/MontionManager.cs:1657`
  - `void Close()` — `MotionControl/MontionManager.cs:1688`
  - `void AddAxis(string name, DeltaMontionAxis axis)` — `MotionControl/MontionManager.cs:1718`
  - ` GetAxis(string name)` — `MotionControl/MontionManager.cs:1727`
  - ` GetDeltaAxis(string name)` — `MotionControl/MontionManager.cs:1735`
  - ` GetAxisByKeys()` — `MotionControl/MontionManager.cs:1743`
  - `bool TryGetAxisNameByKeys(string[] keys, string axisName)` — `MotionControl/MontionManager.cs:1760`
  - ` GetDeltaAxisByKeys()` — `MotionControl/MontionManager.cs:1773`
  - ` GetAxisConfigByKeys()` — `MotionControl/MontionManager.cs:1785`
  - ` GetAxisConfigByName(string axisName)` — `MotionControl/MontionManager.cs:1796`
  - ` CreatePreviewMotionConfig()` — `MotionControl/MontionManager.cs:1805`
  - `void ApplyFlowTimeouts()` — `MotionControl/MontionManager.cs:1813`
  - `void EnsureMotionConfigKeys(bool allowWrite, int torqueDirection)` — `MotionControl/MontionManager.cs:1842`
  - `bool ApplyTaAxisRuntimeConfig()` — `MotionControl/MontionManager.cs:1853`
  - `bool SaveTaHomeConfig(DeltaTaHomeConfig value)` — `MotionControl/MontionManager.cs:1881`
  - `bool MoveTo(MontionAxis axis, double target)` — `MotionControl/MontionManager.cs:1918`
  - `bool StepMove(MontionAxis axis, double delta)` — `MotionControl/MontionManager.cs:1930`
  - `bool MoveToNoBlock(MontionAxis axis, double target)` — `MotionControl/MontionManager.cs:1941`
  - `bool StepMoveNoBlock(MontionAxis axis, double delta)` — `MotionControl/MontionManager.cs:1953`
  - `bool ToggleServo(MontionAxis axis)` — `MotionControl/MontionManager.cs:1963`
  - `void JogStart(MontionAxis axis, ushort dir)` — `MotionControl/MontionManager.cs:1975`
  - `void StopAxis(MontionAxis axis)` — `MotionControl/MontionManager.cs:1985`
  - `bool HomeAxisAndWait(MontionAxis axis)` — `MotionControl/MontionManager.cs:1996`
  - `void AddInputIO(string name, InputIO io)` — `MotionControl/MontionManager.cs:2009`
  - ` GetInputIO(string name)` — `MotionControl/MontionManager.cs:2018`
  - `void AddOutputIO(string name, OutputIO io)` — `MotionControl/MontionManager.cs:2026`
  - ` GetOutputIO(string name)` — `MotionControl/MontionManager.cs:2035`
  - `void AddCylinder(string name, Cylinder cylinder)` — `MotionControl/MontionManager.cs:2043`
  - ` GetCylinder(string name)` — `MotionControl/MontionManager.cs:2052`
  - `void RegisterCylinderIO(Cylinder cylinder, MontionControl control)` — `MotionControl/MontionManager.cs:2060`
  - `void ServoOnAll()` — `MotionControl/MontionManager.cs:2071`
  - `bool EnableAxesAfterInit()` — `MotionControl/MontionManager.cs:2083`
  - `void ServoOffAll()` — `MotionControl/MontionManager.cs:2150`
  - `void ResetAlarmAll()` — `MotionControl/MontionManager.cs:2160`
  - `bool HomeAll()` — `MotionControl/MontionManager.cs:2171`
  - `void SetEmergencyStop(bool isEmergencyStop)` — `MotionControl/MontionManager.cs:2184`
- 构造（1）：
  - `MontionManager()` — `MotionControl/MontionManager.cs:1061`
- 属性（29）：
  - `double EffectiveDetectTimeoutSeconds { get; set; }` — `MotionControl/MontionManager.cs:46`
  - `int EffectiveSampleIntervalMs { get; set; }` — `MotionControl/MontionManager.cs:47`
  - `int EffectiveStableSampleCount { get; set; }` — `MotionControl/MontionManager.cs:48`
  - `int EffectiveTorqueConfirmSamples { get; set; }` — `MotionControl/MontionManager.cs:49`
  - `MontionManager Instance { get; set; }` — `MotionControl/MontionManager.cs:115`
  - `MontionControl MontionControl { get; set; }` — `MotionControl/MontionManager.cs:118`
  - `bool IsInitialized { get; set; }` — `MotionControl/MontionManager.cs:121`
  - `MoveControlData MoveData { get; set; }` — `MotionControl/MontionManager.cs:124`
  - `AxisRegistry Axes { get; set; }` — `MotionControl/MontionManager.cs:127`
  - `IORegistry IOs { get; set; }` — `MotionControl/MontionManager.cs:130`
  - `CylinderRegistry Cylinders { get; set; }` — `MotionControl/MontionManager.cs:133`
  - `WeldHeadSlaveDevice WeldHead { get; set; }` — `MotionControl/MontionManager.cs:136`
  - `WeldHeadConfig WeldHeadConfig { get; set; }` — `MotionControl/MontionManager.cs:139`
  - `bool TaAvailable { get; set; }` — `MotionControl/MontionManager.cs:142`
  - `bool TaAtWorkZero { get; set; }` — `MotionControl/MontionManager.cs:148`
  - `string TaZeroPoseReason { get; set; }` — `MotionControl/MontionManager.cs:151`
  - `bool TaHomed { get; set; }` — `MotionControl/MontionManager.cs:154`
  - `bool TaMotionReady { get; set; }` — `MotionControl/MontionManager.cs:157`
  - `double TaZeroPoseTargetMm { get; set; }` — `MotionControl/MontionManager.cs:170`
  - `string TaDegradedReason { get; set; }` — `MotionControl/MontionManager.cs:182`
  - `bool YReady { get; set; }` — `MotionControl/MontionManager.cs:199`
  - `string YGateReason { get; set; }` — `MotionControl/MontionManager.cs:211`
  - `bool LaReady { get; set; }` — `MotionControl/MontionManager.cs:226`
  - `string LaGateReason { get; set; }` — `MotionControl/MontionManager.cs:237`
  - `bool IsInitCompleted { get; set; }` — `MotionControl/MontionManager.cs:486`
  - `bool IsInitSucceeded { get; set; }` — `MotionControl/MontionManager.cs:489`
  - `DeltaTaHomeConfig TaHomeConfig { get; set; }` — `MotionControl/MontionManager.cs:1750`
  - `FlowTimeoutConfig FlowTimeouts { get; set; }` — `MotionControl/MontionManager.cs:1753`
  - `DeltaAxisConfig TaAxisConfig { get; set; }` — `MotionControl/MontionManager.cs:1780`

## MotionConfigImporter

- 签名：`public static class MotionConfigImporter`
- 位置：`MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:11`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（26）：
  - `void Log(string message, MessageLevel level)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:28`
  - `void ReadCsvRows(string path, List<string[]> rows, string error)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:38`
  - `void SplitCsvLine(string line)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:72`
  - `void BuildColumnMap(string[] header)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:121`
  - `void Cell(string[] row, Dictionary<string, int> map, string column)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:136`
  - `void ParseEnabled(string txt)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:145`
  - `void ToInt(string txt, int def, string where, List<string> errors)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:156`
  - `void ToIntRange(string txt, int def, string where, int min, int max, List<string> errors)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:173`
  - `void ToDouble(string txt, double def, string where, List<string> errors)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:191`
  - `void AssertUnique(HashSet<string> seen, string name, string where, List<string> errors)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:204`
  - `void ImportAxes(string dir, List<string> errors)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:216`
  - `void ImportIOs(string dir, List<DeltaIOConfig> inputs, List<DeltaIOConfig> outputs, HashSet<string> inputNames, HashSet<string> outputNames, List<string> errors)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:287`
  - `void ImportCylinders(string dir, HashSet<string> inputNames, HashSet<string> outputNames, List<string> errors)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:353`
  - `void CheckIORef(string ioName, HashSet<string> names, string column, string where, List<string> errors)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:411`
  - `void CsvField(string text)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:424`
  - `void CsvBool(bool value)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:437`
  - `void CsvDouble(double value)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:446`
  - `void WriteCsv(string path, List<string[]> rows)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:454`
  - `void AppendAxisRows(List<string[]> rows, IList<DeltaAxisConfig> axes)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:467`
  - `void AppendIORows(List<string[]> rows, IList<DeltaIOConfig> list, string ioType)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:503`
  - `void AppendCylinderRows(List<string[]> rows, IList<DeltaCylinderConfig> cylinders)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:523`
  - `void WriteAllCsv(string dir, DeltaMotionConfig config)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:545`
  - `bool Import(string dir, string msg)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:583`
  - `bool Import(string dir, bool importAxes, bool importIos, bool importCylinders, string msg)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:596`
  - `bool Import(string dir, bool importAxes, bool importIos, bool importCylinders, string backupFolder, string msg)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:610`
  - `bool Export(string dir, string msg)` — `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs:688`

## MoveControlData

- 签名：`public class MoveControlData`
- 位置：`MotionControl/MoveControlData.cs:8`
- 命名空间：`AdaWeldSystem.MotionControl`
- 方法（3）：
  - `void Log(string message, MessageLevel level)` — `MotionControl/MoveControlData.cs:38`
  - `void Load()` — `MotionControl/MoveControlData.cs:48`
  - `void Save()` — `MotionControl/MoveControlData.cs:62`
- 构造（1）：
  - `MoveControlData()` — `MotionControl/MoveControlData.cs:26`
- 属性（1）：
  - `DeltaMotionConfig MotionConfig { get; set; }` — `MotionControl/MoveControlData.cs:19`

## OutputIO

- 签名：`public abstract class OutputIO : MontionIO`
- 位置：`MotionControl/IMotion/OutputIO.cs:4`
- 命名空间：`AdaWeldSystem.MotionControl.IMotion`
- 方法（3）：
  - `int SetON()` — `MotionControl/IMotion/OutputIO.cs:22`
  - `int SetOFF()` — `MotionControl/IMotion/OutputIO.cs:26`
  - ` GetIOType()` — `MotionControl/IMotion/OutputIO.cs:30`
- 构造（1）：
  - `OutputIO(MontionControl container, string ioName)` — `MotionControl/IMotion/OutputIO.cs:11`

## PVTResult

- 签名：`public static class PVTResult`
- 位置：`MotionControl/IMotion/IPVTMotion.cs:107`
- 命名空间：`AdaWeldSystem.MotionControl.IMotion`
- 成员：（无）

## SlaveInfo

- 签名：`public class SlaveInfo`
- 位置：`MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:181`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 属性（8）：
  - `ushort SeqId { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:184`
  - `ushort NodeId { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:187`
  - `uint VendorId { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:190`
  - `uint ProductCode { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:193`
  - `uint RevisionNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:196`
  - `string DeviceName { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:199`
  - `SlaveDeviceType DeviceType { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:202`
  - `ushort AxisCount { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs:205`

## SystemConfigPackager

- 签名：`public static class SystemConfigPackager`
- 位置：`MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:53`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（18）：
  - `bool Export(string targetFile, string message)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:88`
  - `bool Import(string packageFile, string message)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:154`
  - `void CollectFiles()` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:254`
  - `void BuildExcludedList()` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:292`
  - `void IsExcluded(string relative)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:305`
  - `void IsStagingPath(string relative)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:322`
  - `void AddFile(List<ConfigPackageFile> files, string baseDirectory, string relative)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:332`
  - `void ReadPackage(string packageFile, ConfigPackageManifest manifest, List<KeyValuePair<string, byte[]>> payload, string message)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:356`
  - `void WriteStaging(string stagingRoot, List<KeyValuePair<string, byte[]>> payload)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:430`
  - `void Rollback(List<string> written, string backupFolder)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:445`
  - `void IsUnderBaseDirectory(string fullPath)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:467`
  - `void IsSafeRelativePath(string relative)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:477`
  - `void IsAllowedTarget(string relative)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:489`
  - `void ReadEntryBytes(ZipArchiveEntry entry)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:507`
  - `void WriteTextEntry(ZipArchive archive, string name, string content)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:521`
  - `void Sha256(string path)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:534`
  - `void Sha256(byte[] bytes)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:546`
  - `void ToHex(byte[] hash)` — `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs:557`

## WeldHeadConfig

- 签名：`public class WeldHeadConfig`
- 位置：`MotionControl/WeldHeadSlaveDevice.cs:874`
- 命名空间：`AdaWeldSystem.MotionControl`
- 方法（2）：
  - ` GetGalvoShape(WsgGalvoPattern pattern)` — `MotionControl/WeldHeadSlaveDevice.cs:950`
  - ` BuildGalvoParamsFor(WsgGalvoPattern pattern)` — `MotionControl/WeldHeadSlaveDevice.cs:960`
- 构造（1）：
  - `WeldHeadConfig()` — `MotionControl/WeldHeadSlaveDevice.cs:921`
- 属性（13）：
  - `double TempWarnThreshold { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:877`
  - `double TempAlarmThreshold { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:880`
  - `double RiseWarnThreshold { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:883`
  - `double RiseAlarmThreshold { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:886`
  - `double PressureAlarmThreshold { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:889`
  - `int PressureDelayMs { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:892`
  - `GalvoGlobalParams DefaultGalvo { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:895`
  - `System.Collections.Generic.Dictionary<WsgGalvoPattern, GalvoShapeParams> GalvoShapePresets { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:898`
  - `double MotorPulsePerMm { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:904`
  - `IList<WeldHeadPdoEntry> PdoMap { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:909`
  - `string IoMapSourceFile { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:912`
  - `string IoMapSourceTime { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:915`
  - `int IoMapSourceRows { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:918`

## WeldHeadPdoEntry

- 签名：`public class WeldHeadPdoEntry`
- 位置：`MotionControl/WeldHeadSlaveDevice.cs:825`
- 命名空间：`AdaWeldSystem.MotionControl`
- 构造（1）：
  - `WeldHeadPdoEntry()` — `MotionControl/WeldHeadSlaveDevice.cs:858`
- 属性（10）：
  - `string Seq { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:828`
  - `string VarName { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:831`
  - `string DisplayName { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:834`
  - `string DataType { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:837`
  - `string SdoIndex { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:840`
  - `string SdoSubIndex { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:843`
  - `string Access { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:846`
  - `string PdoIndex { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:849`
  - `string PdoSubIndex { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:852`
  - `string Description { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:855`

## WeldHeadSlaveConfig

- 签名：`public class WeldHeadSlaveConfig`
- 位置：`MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:14`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 构造（1）：
  - `WeldHeadSlaveConfig()` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:32`
- 属性（5）：
  - `ushort NodeId { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:17`
  - `bool Enabled { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:20`
  - `uint VendorId { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:23`
  - `uint ProductCode { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:26`
  - `uint RevisionNo { get; set; }` — `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs:29`

## WeldHeadSlaveDevice

- 签名：`public class WeldHeadSlaveDevice : IDisposable`
- 位置：`MotionControl/WeldHeadSlaveDevice.cs:9`
- 命名空间：`AdaWeldSystem.MotionControl`
- 方法（19）：
  - `void Log(string message, MessageLevel level)` — `MotionControl/WeldHeadSlaveDevice.cs:77`
  - `bool Initialize()` — `MotionControl/WeldHeadSlaveDevice.cs:134`
  - `void Shutdown()` — `MotionControl/WeldHeadSlaveDevice.cs:158`
  - ` ReadTemperature()` — `MotionControl/WeldHeadSlaveDevice.cs:174`
  - ` ReadAlarmStatus()` — `MotionControl/WeldHeadSlaveDevice.cs:209`
  - `bool SetGalvoParams(GalvoParams galvo)` — `MotionControl/WeldHeadSlaveDevice.cs:241`
  - ` ReadGalvoParams()` — `MotionControl/WeldHeadSlaveDevice.cs:275`
  - `bool SetAlarmThresholds(double tempWarn, double tempAlarm, double riseWarn, double riseAlarm, double pressureAlarm, int pressureDelay)` — `MotionControl/WeldHeadSlaveDevice.cs:339`
  - `bool EnableLaser()` — `MotionControl/WeldHeadSlaveDevice.cs:366`
  - `bool DisableLaser()` — `MotionControl/WeldHeadSlaveDevice.cs:376`
  - `bool ResetHead()` — `MotionControl/WeldHeadSlaveDevice.cs:389`
  - `uint GetMcuVersion()` — `MotionControl/WeldHeadSlaveDevice.cs:398`
  - `bool SetMotorPosEnable(double positionMm, bool enable)` — `MotionControl/WeldHeadSlaveDevice.cs:412`
  - `MotorState? ReadMotorStatus()` — `MotionControl/WeldHeadSlaveDevice.cs:433`
  - `bool StopMotor()` — `MotionControl/WeldHeadSlaveDevice.cs:468`
  - `void MmToMotorCount(double mm)` — `MotionControl/WeldHeadSlaveDevice.cs:488`
  - `void ReadScaledWithIndex(ushort odIndex, ushort subIndex, double scale, bool signed, double value)` — `MotionControl/WeldHeadSlaveDevice.cs:496`
  - `string DescribeTemperatureThreshold(double temp, double limit, bool isAlarm)` — `MotionControl/WeldHeadSlaveDevice.cs:509`
  - `void Dispose()` — `MotionControl/WeldHeadSlaveDevice.cs:521`
- 构造（1）：
  - `WeldHeadSlaveDevice(ushort cardNo, ushort nodeId)` — `MotionControl/WeldHeadSlaveDevice.cs:120`
- 属性（6）：
  - `bool IsInitialized { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:87`
  - `bool IsLaserReady { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:90`
  - `LaserHeadTemperatureData CurrentTemperature { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:93`
  - `HeadAlarmStatus CurrentAlarmStatus { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:96`
  - `double TemperatureAlarmThreshold { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:102`
  - `double MotorPulsePerMm { get; set; }` — `MotionControl/WeldHeadSlaveDevice.cs:111`

## XlsxSheetReader

- 签名：`public static class XlsxSheetReader`
- 位置：`MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:13`
- 命名空间：`AdaWeldSystem.MotionControl.DeltaEtherCAT`
- 方法（12）：
  - `bool TryReadFirstSheet(string path, List<string[]> rows, string error)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:31`
  - `void ReadSharedStrings(ZipArchive archive)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:75`
  - `void ResolveFirstSheetPath(ZipArchive archive)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:92`
  - `void ReadSheetRows(XDocument sheet, List<string> shared)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:133`
  - `void ApplyMergedCells(XDocument sheet, List<string[]> rows)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:186`
  - `void TrimEmptyRows(List<string[]> rows)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:225`
  - `void CellText(XElement cell, List<string> shared)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:246`
  - `void ConcatText(XElement element)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:281`
  - `void CellPosition(string reference)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:294`
  - `void ColumnIndex(string reference)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:310`
  - `void GetAttribute(XElement element, string localName)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:330`
  - `void LoadXml(ZipArchive archive, string path)` — `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs:343`

## 相关页面

- [[architecture/CodeMap]]
