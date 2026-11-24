---
title: CodeMap-Relations-Methods-MotionControl — 代码地图·方法级影响面·MotionControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-MotionControl — 方法级影响面（低置信 · 调用方在 MotionControl · 名首字母 A-M）

> **一句话**：**调用方位于 `MotionControl` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 98 |
| 调用点数 | 111 |

## 章节导航

- [AbsMove](#AbsMove)
- [AbsMoveNoBlock](#AbsMoveNoBlock)
- [AddFile](#AddFile)
- [AppendAxisRows](#AppendAxisRows)
- [AppendCylinderRows](#AppendCylinderRows)
- [AppendIORows](#AppendIORows)
- [ApplyAxisConfig](#ApplyAxisConfig)
- [ApplyMergedCells](#ApplyMergedCells)
- [ApplyTaAxisRuntimeConfig](#ApplyTaAxisRuntimeConfig)
- [ApplyTaHomeOnLoad](#ApplyTaHomeOnLoad)
- [AssertUnique](#AssertUnique)
- [AttachAll](#AttachAll)
- [AxisOwnerKey](#AxisOwnerKey)
- [AxisStop](#AxisStop)
- [BuildColumnMap](#BuildColumnMap)
- [BuildExcludedList](#BuildExcludedList)
- [BuildHeaderMap](#BuildHeaderMap)
- [BuildPartialMessage](#BuildPartialMessage)
- [BuildPdoKey](#BuildPdoKey)
- [BuildSkipList](#BuildSkipList)
- [CancelAllAxisInstructions](#CancelAllAxisInstructions)
- [CancelAxisInstruction](#CancelAxisInstruction)
- [Cell](#Cell)
- [CellPosition](#CellPosition)
- [CellText](#CellText)
- [CheckIORef](#CheckIORef)
- [ChildValue](#ChildValue)
- [ChildValueAny](#ChildValueAny)
- [Clamp](#Clamp)
- [CollectFiles](#CollectFiles)
- [ColumnIndex](#ColumnIndex)
- [ConcatText](#ConcatText)
- [CreateAxesFromConfig](#CreateAxesFromConfig)
- [CreateCylindersFromConfig](#CreateCylindersFromConfig)
- [CreateIOsFromConfig](#CreateIOsFromConfig)
- [CreateWeldHeadFromConfig](#CreateWeldHeadFromConfig)
- [CrossCheckProtocol](#CrossCheckProtocol)
- [CsvBool](#CsvBool)
- [CsvDouble](#CsvDouble)
- [CsvField](#CsvField)
- [Describe](#Describe)
- [DescribeAxisDiagnosis](#DescribeAxisDiagnosis)
- [DisableLaser](#DisableLaser)
- [EnsureCspMotionStoppedForTorque](#EnsureCspMotionStoppedForTorque)
- [EnsureDriveTorqueLimit](#EnsureDriveTorqueLimit)
- [ExitTaTorqueMode](#ExitTaTorqueMode)
- [FindAxisNameByKeys](#FindAxisNameByKeys)
- [FindIO](#FindIO)
- [GalvoShapeNodeName](#GalvoShapeNodeName)
- [GenerateCore](#GenerateCore)
- [GetAttribute](#GetAttribute)
- [GetAxis](#GetAxis)
- [GetAxisByKeys](#GetAxisByKeys)
- [GetAxisConfigByKeys](#GetAxisConfigByKeys)
- [GetAxisStatus](#GetAxisStatus)
- [GetCell](#GetCell)
- [GetCommandPosition](#GetCommandPosition)
- [GetCurrentTorque](#GetCurrentTorque)
- [GetDeltaAxis](#GetDeltaAxis)
- [GetDeltaAxisByKeys](#GetDeltaAxisByKeys)
- [GetGalvoShape](#GetGalvoShape)
- [GetHomeStatus](#GetHomeStatus)
- [GetIOStatus](#GetIOStatus)
- [GetMcuVersion](#GetMcuVersion)
- [GetMoveMode](#GetMoveMode)
- [GetParseFailures](#GetParseFailures)
- [GetPosition](#GetPosition)
- [GetStatusWord](#GetStatusWord)
- [HasCsvSignature](#HasCsvSignature)
- [IdentifyDevice](#IdentifyDevice)
- [Import](#Import)
- [ImportAxes](#ImportAxes)
- [ImportCylinders](#ImportCylinders)
- [ImportIOs](#ImportIOs)
- [IsAllowedTarget](#IsAllowedTarget)
- [IsAxisSlaveMissing](#IsAxisSlaveMissing)
- [IsBusReady](#IsBusReady)
- [IsExcluded](#IsExcluded)
- [IsMoving](#IsMoving)
- [IsNodeDetected](#IsNodeDetected)
- [IsSafeRelativePath](#IsSafeRelativePath)
- [IsServoOn](#IsServoOn)
- [IsSlaveOperational](#IsSlaveOperational)
- [IsStagingPath](#IsStagingPath)
- [IsTaAxis](#IsTaAxis)
- [IsUnderBaseDirectory](#IsUnderBaseDirectory)
- [JogMove](#JogMove)
- [LoadConfig](#LoadConfig)
- [LoadFlowTimeouts](#LoadFlowTimeouts)
- [LoadTaHome](#LoadTaHome)
- [LoadWeldHeadConfig](#LoadWeldHeadConfig)
- [LoadXml](#LoadXml)
- [Log](#Log)
- [LogFail](#LogFail)
- [LogLegacyKeyRename](#LogLegacyKeyRename)
- [LogScanList](#LogScanList)
- [LogTorqueLimitRelation](#LogTorqueLimitRelation)
- [MmToMotorCount](#MmToMotorCount)

## Log

> 11 处调用 / 11 个调用方文件

- `MotionControl/AxisRegistry.cs` — 行 [113]
- `MotionControl/CylinderRegistry.cs` — 行 [118]
- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1347, 1248, 1228, 1206, 1193, 1172, 1144, 1139, 1132, 1127, 1110, 1103, 931, 922, 914, 907, 852, 846, 843, 833, 797, 735, 702, 696, 688, 677, 672, 666, 657, 635, 621, 614, 602, 597, 590, 585, 572, 561, 554, 549, 536, 531, 494, 490, 485, 449, 446, 439, 431, 425, 417, 390, 351, 343, 333, 322, 316, 310, 296, 289, 284, 264, 251, 245, 240, 235, 229, 210, 200, 183]
- `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs` — 行 [293, 235, 204, 199, 191, 175, 152, 147, 140, 118, 106, 97, 85, 75]
- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1196, 1155, 1113, 1109, 1058, 1054, 1032, 1025, 727, 721, 689, 685, 629, 624, 613, 551, 543, 485, 478]
- `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` — 行 [296, 289, 270, 263, 242, 193, 86]
- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [716, 710, 693, 655, 641]
- `MotionControl/IORegistry.cs` — 行 [140]
- `MotionControl/MontionManager.cs` — 行 [2178, 2166, 2156, 2141, 2137, 2131, 2129, 2124, 2116, 2108, 2107, 2100, 2087, 2077, 1903, 1892, 1886, 1871, 1860, 1712, 1707, 1681, 1667, 1661, 1640, 1624, 1615, 1565, 1495, 1486, 1417, 1411, 1407, 1336, 1330, 1317, 1305, 1300, 1295, 1290, 1281, 1272, 1261, 1250, 1239, 1228, 1211, 1154, 1151, 1129, 1116, 863, 857, 852, 778, 712, 654, 641, 633, 596, 585]
- `MotionControl/MoveControlData.cs` — 行 [71, 67, 57, 53]
- `MotionControl/WeldHeadSlaveDevice.cs` — 行 [476, 461, 426, 420, 392, 383, 370, 359, 352, 332, 269, 262, 234, 215, 182, 168, 164, 153, 148, 145, 138]

## GetAxis

> 2 处调用 / 2 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [887, 680]
- `MotionControl/MontionManager.cs` — 行 [1746]

## GetIOStatus

> 2 处调用 / 2 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaInputIO.cs` — 行 [56]
- `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs` — 行 [80]

## LogFail

> 2 处调用 / 2 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1442, 1436, 1379, 1351, 1313, 1300, 1275, 1247, 1216, 1205, 1185, 1163, 1045, 1038, 1010, 861, 812, 788, 749, 609, 596, 578, 542, 526, 471, 462, 400]
- `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs` — 行 [118, 106, 94]

## AbsMove

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [943]

## AbsMoveNoBlock

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [968]

## AddFile

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [279]

## AppendAxisRows

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [556]

## AppendCylinderRows

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [571]

## AppendIORows

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [562, 561]

## ApplyAxisConfig

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1863, 1121]

## ApplyMergedCells

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` — 行 [179]

## ApplyTaAxisRuntimeConfig

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1902]

## ApplyTaHomeOnLoad

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1122]

## AssertUnique

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [381, 316, 244]

## AttachAll

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1680, 1639]

## AxisOwnerKey

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1132]

## AxisStop

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [689, 566]

## BuildColumnMap

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [367, 301, 230]

## BuildExcludedList

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [109]

## BuildHeaderMap

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [884]

## BuildPartialMessage

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [379, 358]

## BuildPdoKey

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [805, 713]

## BuildSkipList

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [199]

## CancelAllAxisInstructions

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [2187]

## CancelAxisInstruction

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1988, 714]

## Cell

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [392, 391, 390, 389, 388, 387, 386, 374, 331, 330, 329, 328, 327, 309, 308, 269, 268, 267, 266, 265, 264, 263, 262, 261, 260, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 237]

## CellPosition

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` — 行 [202, 201]

## CellText

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` — 行 [160]

## CheckIORef

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [398, 397, 396, 395, 394]

## ChildValue

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [763, 762, 761, 760, 759, 758, 757, 756, 744, 743, 742, 741, 740, 739, 652, 651, 650, 641]

## ChildValueAny

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [670, 669, 668, 667, 666, 665, 664, 663, 662, 661, 660, 659, 658, 657, 656, 655, 654, 653]

## Clamp

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [263, 262, 261, 260, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232]

## CollectFiles

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [93]

## ColumnIndex

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` — 行 [298, 158]

## ConcatText

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` — 行 [254, 84]

## CreateAxesFromConfig

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1675, 1633]

## CreateCylindersFromConfig

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1677, 1635]

## CreateIOsFromConfig

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1676, 1634]

## CreateWeldHeadFromConfig

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1678, 1636]

## CrossCheckProtocol

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [580]

## CsvBool

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [514, 492, 476]

## CsvDouble

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [490, 489, 488, 487, 486, 485, 483, 482, 481, 480, 479, 478, 477]

## CsvField

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [536, 535, 534, 533, 532, 531, 530, 529, 515, 510, 473]

## Describe

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` — 行 [242, 193]

## DescribeAxisDiagnosis

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [2131, 310, 294]

## DisableLaser

> 1 处调用 / 1 个调用方文件

- `MotionControl/WeldHeadSlaveDevice.cs` — 行 [162]

## EnsureCspMotionStoppedForTorque

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1179]

## EnsureDriveTorqueLimit

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [781]

## ExitTaTorqueMode

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1999, 1989, 1978, 1966, 1956, 1944, 1933, 1921]

## FindAxisNameByKeys

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1787, 1775, 1763, 1745]

## FindIO

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1260, 1252]

## GalvoShapeNodeName

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1525, 1454]

## GenerateCore

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [469, 434]

## GetAttribute

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` — 行 [248, 192, 158, 120, 118, 109]

## GetAxisByKeys

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [291, 217, 205]

## GetAxisConfigByKeys

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1855, 1780]

## GetAxisStatus

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [2130, 345, 311]

## GetCell

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [913, 912, 911, 910, 909, 908, 907, 906, 904, 899]

## GetCommandPosition

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [557]

## GetCurrentTorque

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1243]

## GetDeltaAxis

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1776]

## GetDeltaAxisByKeys

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [2093, 1856, 1403, 860, 307, 289, 188, 163]

## GetGalvoShape

> 1 处调用 / 1 个调用方文件

- `MotionControl/WeldHeadSlaveDevice.cs` — 行 [962]

## GetHomeStatus

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1136, 421]

## GetMcuVersion

> 1 处调用 / 1 个调用方文件

- `MotionControl/WeldHeadSlaveDevice.cs` — 行 [142]

## GetMoveMode

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1244, 1190, 1148, 582, 546]

## GetParseFailures

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [208]

## GetPosition

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [930, 921, 913, 903, 885, 534]

## GetStatusWord

> 1 处调用 / 1 个调用方文件

- `MotionControl/IMotion/MontionAxis.cs` — 行 [216]

## HasCsvSignature

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 [333, 332, 331]

## IdentifyDevice

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs` — 行 [155]

## Import

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [598, 585]

## ImportAxes

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [615]

## ImportCylinders

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [635]

## ImportIOs

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 [625]

## IsAllowedTarget

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [188]

## IsAxisSlaveMissing

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [2097, 309, 293, 219, 190]

## IsBusReady

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs` — 行 [114, 102, 87]

## IsExcluded

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [494, 278]

## IsMoving

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [731, 692, 686, 631]

## IsNodeDetected

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1298, 431, 278, 270]

## IsSafeRelativePath

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [491, 401]

## IsServoOn

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1333, 793, 414, 388]

## IsSlaveOperational

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs` — 行 [325]

## IsStagingPath

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [494, 278]

## IsTaAxis

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1612]

## IsUnderBaseDirectory

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 [182]

## JogMove

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [991]

## LoadConfig

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1012, 1004]

## LoadFlowTimeouts

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1097]

## LoadTaHome

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1096]

## LoadWeldHeadConfig

> 1 处调用 / 1 个调用方文件

- `MotionControl/MontionManager.cs` — 行 [1075]

## LoadXml

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` — 行 [112, 95, 78, 50]

## LogLegacyKeyRename

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 [1181]

## LogScanList

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs` — 行 [206]

## LogTorqueLimitRelation

> 1 处调用 / 1 个调用方文件

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 [1120]

## MmToMotorCount

> 1 处调用 / 1 个调用方文件

- `MotionControl/WeldHeadSlaveDevice.cs` — 行 [420, 416]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
