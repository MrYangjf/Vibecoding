---
title: CodeMap-Relations-Methods-MotionControl-2 — 代码地图·方法级影响面·MotionControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-MotionControl-2 — 方法级影响面（低置信 · 调用方在 MotionControl · 名首字母 N-Z）

> **一句话**：**调用方位于 `MotionControl` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 92 |
| 调用点数 | 94 |

## 章节导航

- [NormalizeContainerKey](#NormalizeContainerKey)
- [NormalizeHeader](#NormalizeHeader)
- [NormalizeHex](#NormalizeHex)
- [NormalizeObjectKeyHex](#NormalizeObjectKeyHex)
- [NormalizeTaTorqueLimit](#NormalizeTaTorqueLimit)
- [NotifyAxisReadinessChanged](#NotifyAxisReadinessChanged)
- [OpenAndInitialCards](#OpenAndInitialCards)
- [ParseDouble](#ParseDouble)
- [ParseEnabled](#ParseEnabled)
- [ParseHexUInt](#ParseHexUInt)
- [ParseIndexNumber](#ParseIndexNumber)
- [ParseShort](#ParseShort)
- [ParseUShort](#ParseUShort)
- [PdoGet](#PdoGet)
- [PdoSet](#PdoSet)
- [PreMotionCheck](#PreMotionCheck)
- [ProbeTorqueLimitObjectsOnce](#ProbeTorqueLimitObjectsOnce)
- [ReadAlarmStatus](#ReadAlarmStatus)
- [ReadAttribute](#ReadAttribute)
- [ReadAxis](#ReadAxis)
- [ReadBool](#ReadBool)
- [ReadChildText](#ReadChildText)
- [ReadCsvRows](#ReadCsvRows)
- [ReadCylinder](#ReadCylinder)
- [ReadDouble](#ReadDouble)
- [ReadEntryBytes](#ReadEntryBytes)
- [ReadEsiPdoContainers](#ReadEsiPdoContainers)
- [ReadHexUInt](#ReadHexUInt)
- [ReadIO](#ReadIO)
- [ReadInt](#ReadInt)
- [ReadPackage](#ReadPackage)
- [ReadScaledWithIndex](#ReadScaledWithIndex)
- [ReadSdo](#ReadSdo)
- [ReadSharedStrings](#ReadSharedStrings)
- [ReadSheetRows](#ReadSheetRows)
- [ReadSlaveIdentity](#ReadSlaveIdentity)
- [ReadTemperature](#ReadTemperature)
- [ReadUShort](#ReadUShort)
- [ReadVendorId](#ReadVendorId)
- [ReadWeldHeadDouble](#ReadWeldHeadDouble)
- [ReadWeldHeadEnabled](#ReadWeldHeadEnabled)
- [ReadWeldHeadInt](#ReadWeldHeadInt)
- [RecordCmdOk](#RecordCmdOk)
- [RegisterCylinderIO](#RegisterCylinderIO)
- [RegisterNodeOwner](#RegisterNodeOwner)
- [ResolveFirstSheetPath](#ResolveFirstSheetPath)
- [RestoreCspMode](#RestoreCspMode)
- [ReverseTorqueOutput](#ReverseTorqueOutput)
- [Rollback](#Rollback)
- [SaveConfig](#SaveConfig)
- [Scan](#Scan)
- [ScanWeldHeadFiles](#ScanWeldHeadFiles)
- [SdoRead](#SdoRead)
- [SelfHealMissingKeys](#SelfHealMissingKeys)
- [SetPosition](#SetPosition)
- [SetTaZeroPoseGate](#SetTaZeroPoseGate)
- [Sha256](#Sha256)
- [Shutdown](#Shutdown)
- [SplitCsvLine](#SplitCsvLine)
- [StartHome](#StartHome)
- [StartMove](#StartMove)
- [StopTorque](#StopTorque)
- [Text](#Text)
- [ToDouble](#ToDouble)
- [ToHex](#ToHex)
- [ToHomeModeLogical](#ToHomeModeLogical)
- [ToHomeModeWord](#ToHomeModeWord)
- [ToInt](#ToInt)
- [ToIntRange](#ToIntRange)
- [ToPulse](#ToPulse)
- [ToUnit](#ToUnit)
- [TrimEmptyRows](#TrimEmptyRows)
- [TryParseEsi](#TryParseEsi)
- [TryParseProtocol](#TryParseProtocol)
- [TryWriteTorqueLimitSdo](#TryWriteTorqueLimitSdo)
- [ValidateNodeIdConflicts](#ValidateNodeIdConflicts)
- [VerifyHomeModeReadback](#VerifyHomeModeReadback)
- [WaitAxisAtTargetCore](#WaitAxisAtTargetCore)
- [WaitHomeDone](#WaitHomeDone)
- [WaitInitialDone](#WaitInitialDone)
- [WaitMoveDone](#WaitMoveDone)
- [WaitReverseStopDone](#WaitReverseStopDone)
- [WaitSdoDone](#WaitSdoDone)
- [WeldHeadText](#WeldHeadText)
- [WriteAllCsv](#WriteAllCsv)
- [WriteConfigNodes](#WriteConfigNodes)
- [WriteCsv](#WriteCsv)
- [WriteCylinder](#WriteCylinder)
- [WriteIO](#WriteIO)
- [WriteSdo](#WriteSdo)
- [WriteStaging](#WriteStaging)
- [WriteTextEntry](#WriteTextEntry)

## ReadAttribute

> 2 处调用 / 2 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [618, 606]
- `MotionControl/MontionManager.cs` — 行 [1560, 1559, 1558, 1557, 1556, 1555, 1554, 1553, 1552, 1551]

## SplitCsvLine

> 2 处调用 / 2 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [535, 496]
- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [63]

## NormalizeContainerKey

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [792, 705]

## NormalizeHeader

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [929]

## NormalizeHex

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [623, 622, 621]

## NormalizeObjectKeyHex

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [404, 403, 400, 399]

## NormalizeTaTorqueLimit

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [709]

## NotifyAxisReadinessChanged

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [2143, 586]

## OpenAndInitialCards

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs` — 行 [193]

## ParseDouble

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [666, 665, 664, 663, 662, 661, 659, 658, 657, 656, 655, 654, 653]

## ParseEnabled

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [330, 267, 251]

## ParseHexUInt

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [968, 270, 269, 268]

## ParseIndexNumber

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [835, 834, 822, 801, 728, 677]

## ParseShort

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [660]

## ParseUShort

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [742, 741, 740, 670, 669, 667, 651, 650]

## PdoGet

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` — 行 [432, 418, 368, 353]

## PdoSet

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` — 行 [406, 396, 383]

## PreMotionCheck

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1333, 1122, 1005, 768, 408, 388]

## ProbeTorqueLimitObjectsOnce

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [226]

## ReadAlarmStatus

> 1 处调用 / 1 个调用方文件

- `MotionControl/WeldHeadSlaveDevice.cs` — 行 [151]

## ReadAxis

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1046]

## ReadBool

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1040]

## ReadChildText

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [806, 799, 798, 792, 680, 676, 624, 619, 607]

## ReadCsvRows

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [357, 290, 219]

## ReadCylinder

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1076]

## ReadDouble

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1086, 1085, 1084, 1083, 1082, 1041, 703, 700, 696, 693, 692, 691, 605, 604, 596, 595, 594, 593, 592, 583]

## ReadEntryBytes

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [415]

## ReadEsiPdoContainers

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [695, 625]

## ReadHexUInt

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1092, 1091, 1090]

## ReadIO

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1070, 1064]

## ReadInt

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1081, 1080, 1079, 1039, 1038, 690, 609, 608, 607, 606, 603, 602, 601, 600, 599, 598, 597, 591, 590, 589, 588, 587, 586, 585, 584]

## ReadPackage

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [175]

## ReadScaledWithIndex

> 1 处调用 / 1 个调用方文件

- `MotionControl/WeldHeadSlaveDevice.cs` — 行 [307, 306, 305, 304, 303, 302, 301, 300, 299, 298, 297, 296, 295, 294]

## ReadSdo

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` — 行 [191]

## ReadSharedStrings

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` — 行 [47]

## ReadSheetRows

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` — 行 [57]

## ReadSlaveIdentity

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [339]

## ReadTemperature

> 1 处调用 / 1 个调用方文件

- `MotionControl/WeldHeadSlaveDevice.cs` — 行 [150]

## ReadUShort

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1088, 1037]

## ReadVendorId

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [596]

## ReadWeldHeadDouble

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1531, 1527, 1526, 1520, 1519, 1513, 1510, 1509, 1508, 1507, 1503, 1502, 1501, 1500, 1499]

## ReadWeldHeadEnabled

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1089]

## ReadWeldHeadInt

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1528, 1521, 1515, 1512, 1511, 1506, 1504]

## RecordCmdOk

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1378, 1345, 1260, 1224, 1169, 1011, 813, 801, 752, 620, 470, 399]

## RegisterCylinderIO

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [2046]

## RegisterNodeOwner

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1137, 1131]

## ResolveFirstSheetPath

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` — 行 [48]

## RestoreCspMode

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1256, 1218, 1208, 1195, 1186, 1165, 611, 599, 587, 579, 569, 551, 543]

## ReverseTorqueOutput

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1156]

## Rollback

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [224]

## SaveConfig

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1167]

## Scan

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [444, 434]

## ScanWeldHeadFiles

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [338]

## SdoRead

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` — 行 [338, 324, 310]

## SelfHealMissingKeys

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1103]

## SetPosition

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [560, 535]

## SetTaZeroPoseGate

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1401, 1128]

## Sha256

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [416, 345]

## Shutdown

> 1 处调用 / 1 个调用方文件

- `MotionControl/WeldHeadSlaveDevice.cs` — 行 [525]

## StartHome

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [876, 869]

## StartMove

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [984, 959]

## StopTorque

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [809, 754]

## Text

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [994, 993, 985, 984, 983, 982, 981, 972, 966, 965, 964, 963, 962, 961, 943, 942, 941, 940, 939, 910, 909, 908, 907, 906, 905, 903, 902, 901, 900, 899, 898, 897, 884]

## ToDouble

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [265, 264, 263, 262, 261, 260, 258, 257, 256, 255, 254, 253, 252]

## ToHex

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [550, 539]

## ToHomeModeLogical

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [489]

## ToHomeModeWord

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [445]

## ToInt

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [329, 328, 327, 269, 268, 266, 250, 249, 175]

## ToIntRange

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [259]

## ToPulse

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1368, 1368, 1368, 1365, 1341, 1341, 1311, 1037, 1008, 1008, 457, 450, 396, 396, 396, 396]

## ToUnit

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1054, 1029, 1020]

## TrimEmptyRows

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` — 行 [180]

## TryParseEsi

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [557]

## TryParseProtocol

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [569]

## TryWriteTorqueLimitSdo

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [840, 237]

## ValidateNodeIdConflicts

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1117]

## VerifyHomeModeReadback

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [467]

## WaitAxisAtTargetCore

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [745, 728]

## WaitHomeDone

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [869]

## WaitInitialDone

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs` — 行 [194]

## WaitMoveDone

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [959]

## WaitReverseStopDone

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [567]

## WaitSdoDone

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` — 行 [163]

## WeldHeadText

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1461, 1456, 1455, 1447, 1444, 1443, 1442, 1441, 1434, 1433, 1432, 1431, 1430]

## WriteAllCsv

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [705]

## WriteConfigNodes

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1209, 1189]

## WriteCsv

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [572, 563, 557]

## WriteCylinder

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [932]

## WriteIO

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [926, 920]

## WriteSdo

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` — 行 [240]

## WriteStaging

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [208]

## WriteTextEntry

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [119]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
