---
title: CodeMap-Relations-Methods-EmguALG — 代码地图·方法级影响面·EmguALG（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-EmguALG — 方法级影响面（低置信 · 调用方在 EmguALG）

> **一句话**：**调用方位于 `EmguALG` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 33 |
| 调用点数 | 33 |

## 章节导航

- [ApplyConfig](#ApplyConfig)
- [BuildViewGeometry](#BuildViewGeometry)
- [CalcTwoLineCrossPoint](#CalcTwoLineCrossPoint)
- [CancelScan](#CancelScan)
- [CollectRangeFileRows](#CollectRangeFileRows)
- [ConvertToBinary](#ConvertToBinary)
- [ConvertToGray](#ConvertToGray)
- [Copy2](#Copy2)
- [DrawCalibrationBackdrop](#DrawCalibrationBackdrop)
- [DrawFallbackGrid](#DrawFallbackGrid)
- [DrawMillimeterGrid](#DrawMillimeterGrid)
- [DrawProfile](#DrawProfile)
- [DrawRangeLabels](#DrawRangeLabels)
- [DrawTextOnImage](#DrawTextOnImage)
- [EnsureCanvas](#EnsureCanvas)
- [ExecuteCore](#ExecuteCore)
- [FinishPlaybackLocked](#FinishPlaybackLocked)
- [GetDefaultParametersForOperation](#GetDefaultParametersForOperation)
- [LoadThumbnail](#LoadThumbnail)
- [OnPropertyChanged](#OnPropertyChanged)
- [PrepareOverlayMat](#PrepareOverlayMat)
- [RaiseCompleted](#RaiseCompleted)
- [RaiseProgress](#RaiseProgress)
- [RaiseStateChanged](#RaiseStateChanged)
- [RebasePlayClockLocked](#RebasePlayClockLocked)
- [ResetParametersForOperation](#ResetParametersForOperation)
- [Resolve](#Resolve)
- [SeekToFrameLocked](#SeekToFrameLocked)
- [StartThumbnailLoader](#StartThumbnailLoader)
- [StopLocked](#StopLocked)
- [TargetPlayFrameLocked](#TargetPlayFrameLocked)
- [ToPixel](#ToPixel)
- [UpdateMatFromCanvas](#UpdateMatFromCanvas)

## ApplyConfig

> 1 处调用 / 1 个调用方文件

- `EmguALG/Manager/AlgorithmManager.cs` — 行 [220]

## BuildViewGeometry

> 1 处调用 / 1 个调用方文件

- `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` — 行 [360]

## CalcTwoLineCrossPoint

> 1 处调用 / 1 个调用方文件

- `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` — 行 [160, 159, 158, 157]

## CancelScan

> 1 处调用 / 1 个调用方文件

- `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` — 行 [611, 443, 273]

## CollectRangeFileRows

> 1 处调用 / 1 个调用方文件

- `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` — 行 [287]

## ConvertToBinary

> 1 处调用 / 1 个调用方文件

- `EmguALG/Core/ImageAlgorithm.cs` — 行 [207]

## ConvertToGray

> 1 处调用 / 1 个调用方文件

- `EmguALG/Core/ImageAlgorithm.cs` — 行 [575, 466, 355, 291, 290, 175, 110, 99, 84, 75]

## Copy2

> 1 处调用 / 1 个调用方文件

- `EmguALG/LineLaserContour/LineLaserContourData.cs` — 行 [131, 130, 129, 128, 127]

## DrawCalibrationBackdrop

> 1 处调用 / 1 个调用方文件

- `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` — 行 [362]

## DrawFallbackGrid

> 1 处调用 / 1 个调用方文件

- `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` — 行 [361]

## DrawMillimeterGrid

> 1 处调用 / 1 个调用方文件

- `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` — 行 [364]

## DrawProfile

> 1 处调用 / 1 个调用方文件

- `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` — 行 [363]

## DrawRangeLabels

> 1 处调用 / 1 个调用方文件

- `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` — 行 [365]

## DrawTextOnImage

> 1 处调用 / 1 个调用方文件

- `EmguALG/Core/ImageAlgorithm.cs` — 行 [629, 586, 557, 526, 380, 335, 328, 324, 286]

## EnsureCanvas

> 1 处调用 / 1 个调用方文件

- `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` — 行 [351]

## ExecuteCore

> 1 处调用 / 1 个调用方文件

- `EmguALG/Core/AlgorithmBase.cs` — 行 [113]

## FinishPlaybackLocked

> 1 处调用 / 1 个调用方文件

- `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` — 行 [489, 473]

## GetDefaultParametersForOperation

> 1 处调用 / 1 个调用方文件

- `EmguALG/Core/Stages.cs` — 行 [32]

## LoadThumbnail

> 1 处调用 / 1 个调用方文件

- `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` — 行 [201]

## OnPropertyChanged

> 1 处调用 / 1 个调用方文件

- `EmguALG/Core/Stages.cs` — 行 [311, 302, 248, 234, 178, 165, 129, 116, 61, 48, 33, 26]

## PrepareOverlayMat

> 1 处调用 / 1 个调用方文件

- `EmguALG/Core/ImageAlgorithm.cs` — 行 [574, 465]

## RaiseCompleted

> 1 处调用 / 1 个调用方文件

- `EmguALG/Manager/AlgorithmManager.cs` — 行 [142, 131]

## RaiseProgress

> 1 处调用 / 1 个调用方文件

- `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` — 行 [544, 486, 444, 435, 428, 415, 353]

## RaiseStateChanged

> 1 处调用 / 1 个调用方文件

- `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` — 行 [545, 445, 436, 407, 394, 380, 352]

## RebasePlayClockLocked

> 1 处调用 / 1 个调用方文件

- `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` — 行 [405, 392]

## ResetParametersForOperation

> 1 处调用 / 1 个调用方文件

- `EmguALG/Core/Stages.cs` — 行 [301, 233, 177, 128, 60]

## Resolve

> 1 处调用 / 1 个调用方文件

- `EmguALG/Roi/ImageRoiTool.cs` — 行 [113, 93]

## SeekToFrameLocked

> 1 处调用 / 1 个调用方文件

- `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` — 行 [426, 414, 372]

## StartThumbnailLoader

> 1 处调用 / 1 个调用方文件

- `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` — 行 [303]

## StopLocked

> 1 处调用 / 1 个调用方文件

- `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` — 行 [609, 442, 434, 327]

## TargetPlayFrameLocked

> 1 处调用 / 1 个调用方文件

- `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` — 行 [507, 462]

## ToPixel

> 1 处调用 / 1 个调用方文件

- `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` — 行 [144, 140, 139, 138, 137]

## UpdateMatFromCanvas

> 1 处调用 / 1 个调用方文件

- `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` — 行 [367]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
