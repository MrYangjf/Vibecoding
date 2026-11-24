---
title: CodeMap-Relations-Methods-WeldParamControl — 代码地图·方法级影响面·WeldParamControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-WeldParamControl — 方法级影响面（低置信 · 调用方在 WeldParamControl）

> **一句话**：**调用方位于 `WeldParamControl` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 97 |
| 调用点数 | 103 |

## 章节导航

- [AccumulateNoValueDistanceOnPose](#AccumulateNoValueDistanceOnPose)
- [AddLookupEntry](#AddLookupEntry)
- [AddPoint](#AddPoint)
- [ApplyMonotonic](#ApplyMonotonic)
- [AttachRobotPoseChannel](#AttachRobotPoseChannel)
- [BuildLookupTable](#BuildLookupTable)
- [BuildProfileFromLookupTable](#BuildProfileFromLookupTable)
- [BuildRegions](#BuildRegions)
- [CachePose](#CachePose)
- [ClampPredictVelocity](#ClampPredictVelocity)
- [ClearAlarm](#ClearAlarm)
- [ClearFault](#ClearFault)
- [DiffDict](#DiffDict)
- [Display](#Display)
- [Domain](#Domain)
- [Emit](#Emit)
- [EnsureDefaultConfigExists](#EnsureDefaultConfigExists)
- [EstimateNoValueTravelMm](#EstimateNoValueTravelMm)
- [FeedLatestSeamWidth](#FeedLatestSeamWidth)
- [FeedSpeedCal](#FeedSpeedCal)
- [FilterRobotY](#FilterRobotY)
- [FormatWidth](#FormatWidth)
- [HealAlgorithmsConfigKeys](#HealAlgorithmsConfigKeys)
- [IndexOf](#IndexOf)
- [InsertMapPoint](#InsertMapPoint)
- [Interpolate](#Interpolate)
- [IsIngestPaused](#IsIngestPaused)
- [IsOutlier](#IsOutlier)
- [IsValid](#IsValid)
- [LaserPowerCal](#LaserPowerCal)
- [LoadAlgorithmsConfig](#LoadAlgorithmsConfig)
- [LoadCurrentConfig](#LoadCurrentConfig)
- [LoadProfileIntoLookupTable](#LoadProfileIntoLookupTable)
- [LoadZoneIni](#LoadZoneIni)
- [LoadZoneIniAdapt](#LoadZoneIniAdapt)
- [LoadZoneIniFlow](#LoadZoneIniFlow)
- [LoadZoneIniPreset](#LoadZoneIniPreset)
- [LoadZoneIniQuick](#LoadZoneIniQuick)
- [LoadZoneIniSystem](#LoadZoneIniSystem)
- [LoadZoneXml](#LoadZoneXml)
- [LoadZoneXmlPreset](#LoadZoneXmlPreset)
- [LoadZoneXmlSystem](#LoadZoneXmlSystem)
- [Log](#Log)
- [LogNoValueDistance](#LogNoValueDistance)
- [ManualFixedWidthMm](#ManualFixedWidthMm)
- [MigrateLegacyTaZeroPoseMm](#MigrateLegacyTaZeroPoseMm)
- [MigrateLegacyTorqueTarget](#MigrateLegacyTorqueTarget)
- [NormalizeTaForceDirection](#NormalizeTaForceDirection)
- [Num](#Num)
- [OnParamFrame](#OnParamFrame)
- [ParseDict](#ParseDict)
- [ParseList](#ParseList)
- [ParsePoint](#ParsePoint)
- [PosePredictElapsedSeconds](#PosePredictElapsedSeconds)
- [ProcessLaserResult](#ProcessLaserResult)
- [ProcessRsiPose](#ProcessRsiPose)
- [ProcessSample](#ProcessSample)
- [QueryTargetY](#QueryTargetY)
- [RaiseAbortRecord](#RaiseAbortRecord)
- [RaiseAdjustmentRecord](#RaiseAdjustmentRecord)
- [RaiseAlarmRequest](#RaiseAlarmRequest)
- [RaiseFrameRecord](#RaiseFrameRecord)
- [Range](#Range)
- [ReadDouble](#ReadDouble)
- [ReadDoubleIni](#ReadDoubleIni)
- [ReadInt](#ReadInt)
- [ReadIntIni](#ReadIntIni)
- [ReadPoints](#ReadPoints)
- [ReadRobotX](#ReadRobotX)
- [ReadTrackingMode](#ReadTrackingMode)
- [RemoveChild](#RemoveChild)
- [ReseedMonotonic](#ReseedMonotonic)
- [ResetNoValueDistance](#ResetNoValueDistance)
- [ResetToDefaultPoints](#ResetToDefaultPoints)
- [SaveCurrentIdToIni](#SaveCurrentIdToIni)
- [SaveCurrentProfile](#SaveCurrentProfile)
- [SaveToFile](#SaveToFile)
- [SaveZoneIni](#SaveZoneIni)
- [SaveZoneIniAdapt](#SaveZoneIniAdapt)
- [SaveZoneIniFlow](#SaveZoneIniFlow)
- [SaveZoneIniPreset](#SaveZoneIniPreset)
- [SaveZoneIniQuick](#SaveZoneIniQuick)
- [SaveZoneIniSystem](#SaveZoneIniSystem)
- [SaveZoneXmlPreset](#SaveZoneXmlPreset)
- [SaveZoneXmlSystem](#SaveZoneXmlSystem)
- [SetChild](#SetChild)
- [SetConfig](#SetConfig)
- [SetFault](#SetFault)
- [SetNoValueMeasuring](#SetNoValueMeasuring)
- [StoreChartData](#StoreChartData)
- [TakePending](#TakePending)
- [Text](#Text)
- [TrackPathDistance](#TrackPathDistance)
- [TryLookup](#TryLookup)
- [UpdateDirection](#UpdateDirection)
- [UpdatePosePredictor](#UpdatePosePredictor)
- [WritePoints](#WritePoints)

## Log

> 4 处调用 / 4 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [675, 668, 653, 423, 403, 368, 330]
- `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` — 行 [129]
- `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` — 行 [454, 377, 320]
- `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs` — 行 [120]

## SetConfig

> 3 处调用 / 3 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [811]
- `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` — 行 [281]
- `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` — 行 [305]

## ApplyMonotonic

> 2 处调用 / 2 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [949]
- `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` — 行 [230]

## AccumulateNoValueDistanceOnPose

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [831, 626]

## AddLookupEntry

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs` — 行 [149, 141]

## AddPoint

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` — 行 [248]

## AttachRobotPoseChannel

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [503]

## BuildLookupTable

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs` — 行 [103]

## BuildProfileFromLookupTable

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [1082]

## BuildRegions

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [377]

## CachePose

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [693]

## ClampPredictVelocity

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [652, 651]

## ClearAlarm

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [870, 788]

## ClearFault

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` — 行 [356]

## DiffDict

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamProfileAudit.cs` — 行 [152, 151, 150, 149, 148, 147]

## Display

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamProfileAudit.cs` — 行 [65, 65]

## Domain

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Curves/TaLaCurveConfig.cs` — 行 [367, 366, 357, 354, 342, 341, 333]

## Emit

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamProfileAudit.cs` — 行 [158, 52, 44, 37]

## EnsureDefaultConfigExists

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [520]

## EstimateNoValueTravelMm

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [698]

## FeedLatestSeamWidth

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [1424]

## FeedSpeedCal

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs` — 行 [70]

## FilterRobotY

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [690]

## FormatWidth

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamProfileAudit.cs` — 行 [52, 44, 38]

## HealAlgorithmsConfigKeys

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [1286]

## IndexOf

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamData.cs` — 行 [70]

## InsertMapPoint

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [433]

## Interpolate

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Curves/TaLaCurveConfig.cs` — 行 [183, 175, 167]

## IsIngestPaused

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [1561]

## IsOutlier

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [413]

## IsValid

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Curves/TaLaCurveConfig.cs` — 行 [278, 278, 202, 202]

## LaserPowerCal

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs` — 行 [71]

## LoadAlgorithmsConfig

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [522]

## LoadCurrentConfig

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [1035, 521]

## LoadProfileIntoLookupTable

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [1274, 576]

## LoadZoneIni

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [659, 658, 657, 656, 655]

## LoadZoneIniAdapt

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [737]

## LoadZoneIniFlow

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [736]

## LoadZoneIniPreset

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [738]

## LoadZoneIniQuick

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [735]

## LoadZoneIniSystem

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [734]

## LoadZoneXml

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [630, 629]

## LoadZoneXmlPreset

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [699]

## LoadZoneXmlSystem

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [698]

## LogNoValueDistance

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [713]

## ManualFixedWidthMm

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` — 行 [398]

## MigrateLegacyTaZeroPoseMm

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [1284]

## MigrateLegacyTorqueTarget

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [1282]

## NormalizeTaForceDirection

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [855]

## Num

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamProfileAudit.cs` — 行 [52, 44, 44, 38]

## OnParamFrame

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` — 行 [493]

## ParseDict

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamProfileAudit.cs` — 行 [152, 152, 151, 151, 150, 150, 149, 149, 148, 148, 147, 147]

## ParseList

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamProfileAudit.cs` — 行 [155, 154]

## ParsePoint

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Curves/TaLaCurveConfig.cs` — 行 [267]

## PosePredictElapsedSeconds

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [233, 210]

## ProcessLaserResult

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [998]

## ProcessRsiPose

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [1013]

## ProcessSample

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` — 行 [296]

## QueryTargetY

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [944]

## RaiseAbortRecord

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` — 行 [381]

## RaiseAdjustmentRecord

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` — 行 [479, 474]

## RaiseAlarmRequest

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [1017]

## RaiseFrameRecord

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` — 行 [464]

## Range

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Curves/TaLaCurveConfig.cs` — 行 [373, 372, 360, 348, 348, 334]

## ReadDouble

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [858, 857, 856, 819, 818, 816, 812, 802, 801, 800]

## ReadDoubleIni

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [1027, 1025, 1024, 1023, 1022, 1020, 1019, 1018, 1017, 1016, 995, 906, 905, 904, 903, 902, 901, 900, 898, 897, 896, 895, 894, 892, 891, 890, 889, 881]

## ReadInt

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [817, 804]

## ReadIntIni

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [1028, 994, 893]

## ReadPoints

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Curves/TaLaCurveConfig.cs` — 行 [198, 197]

## ReadRobotX

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` — 行 [295]

## ReadTrackingMode

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [803]

## RemoveChild

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [835, 834]

## ReseedMonotonic

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [606, 584]

## ResetNoValueDistance

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [1577, 1556]

## ResetToDefaultPoints

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Curves/TaLaCurveConfig.cs` — 行 [118]

## SaveCurrentIdToIni

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [567, 176]

## SaveCurrentProfile

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [1171]

## SaveToFile

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Curves/TaLaCurveConfig.cs` — 行 [297]

## SaveZoneIni

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [677, 676, 675, 674, 673]

## SaveZoneIniAdapt

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [779, 761]

## SaveZoneIniFlow

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [778, 760]

## SaveZoneIniPreset

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [780, 762]

## SaveZoneIniQuick

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [777, 759]

## SaveZoneIniSystem

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [776, 758]

## SaveZoneXmlPreset

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [790, 720, 647]

## SaveZoneXmlSystem

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [789, 719, 646]

## SetChild

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [870, 869, 866, 849, 848, 847, 846, 843, 840, 839, 838, 837, 836]

## SetFault

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` — 行 [211]

## SetNoValueMeasuring

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [1578, 1540, 1530]

## StoreChartData

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` — 行 [442]

## TakePending

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` — 行 [325, 315, 300]

## Text

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamConfig.cs` — 行 [1058, 1056, 1055, 1054, 1053, 1051, 1050, 1049, 1048, 1047, 1010, 954, 953, 952, 951, 950, 949, 948, 946, 945, 944, 943, 942, 940, 939, 938, 937, 936, 870, 869, 866, 849, 848, 846, 843, 838, 837, 836]

## TrackPathDistance

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [695]

## TryLookup

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs` — 行 [212]

## UpdateDirection

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 [766]

## UpdatePosePredictor

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/WeldParamManager.cs` — 行 [830, 625]

## WritePoints

> 1 处调用 / 1 个调用方文件

- `WeldParamControl/Curves/TaLaCurveConfig.cs` — 行 [231, 230]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
