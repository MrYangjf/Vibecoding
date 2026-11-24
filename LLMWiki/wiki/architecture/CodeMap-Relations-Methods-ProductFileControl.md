---
title: CodeMap-Relations-Methods-ProductFileControl — 代码地图·方法级影响面·ProductFileControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-ProductFileControl — 方法级影响面（低置信 · 调用方在 ProductFileControl）

> **一句话**：**调用方位于 `ProductFileControl` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 35 |
| 调用点数 | 40 |

## 章节导航

- [AbortRecording](#AbortRecording)
- [AddRecord](#AddRecord)
- [AppendToTempFile](#AppendToTempFile)
- [ClonePointCloud](#ClonePointCloud)
- [EndSeamTraceYSession](#EndSeamTraceYSession)
- [Enqueue](#Enqueue)
- [EnsureDateRecordDirectory](#EnsureDateRecordDirectory)
- [EnsureDirectoriesExist](#EnsureDirectoriesExist)
- [EnsureSessionDirectory](#EnsureSessionDirectory)
- [EnsureWorker](#EnsureWorker)
- [FlushPending](#FlushPending)
- [FlushSeamTraceY](#FlushSeamTraceY)
- [FlushToFile](#FlushToFile)
- [GetDateRecordDirectoryPath](#GetDateRecordDirectoryPath)
- [LoadConfigFromIni](#LoadConfigFromIni)
- [Log](#Log)
- [NormalizeDirectoryPath](#NormalizeDirectoryPath)
- [ObfuscateBytes](#ObfuscateBytes)
- [OnAbort](#OnAbort)
- [OnStart](#OnStart)
- [OnStop](#OnStop)
- [ParseFromTempFile](#ParseFromTempFile)
- [Persist](#Persist)
- [PickExisting](#PickExisting)
- [ReadActionFromStream](#ReadActionFromStream)
- [ReadPDatFile](#ReadPDatFile)
- [ReadPointCloudFromStream](#ReadPointCloudFromStream)
- [RecordWeldResult](#RecordWeldResult)
- [SaveActionsToPDat](#SaveActionsToPDat)
- [SaveFramesToPly](#SaveFramesToPly)
- [SaveTempFileInternal](#SaveTempFileInternal)
- [StartRecording](#StartRecording)
- [StopRecording](#StopRecording)
- [WriteActionToStream](#WriteActionToStream)
- [WritePointCloudToStream](#WritePointCloudToStream)

## Enqueue

> 3 处调用 / 3 个调用方文件

- `ProductFileControl/Records/LineLaserContourRecord.cs` — 行 [36]
- `ProductFileControl/Records/WeldParamControlRecord.cs` — 行 [74, 60, 47]
- `ProductFileControl/Records/WeldResultRecord.cs` — 行 [31]

## Log

> 3 处调用 / 3 个调用方文件

- `ProductFileControl/Abstractions/ProductRecordBase.cs` — 行 [247, 234, 221, 207, 193, 178]
- `ProductFileControl/ProductFileRecordManager.cs` — 行 [796, 469, 465, 394, 357, 215]
- `ProductFileControl/Records/WeldResultRecord.cs` — 行 [85, 68, 56, 48]

## GetDateRecordDirectoryPath

> 2 处调用 / 2 个调用方文件

- `ProductFileControl/ProductFileRecordManager.cs` — 行 [413]
- `ProductFileControl/Records/RecordFileStore.cs` — 行 [1014, 114]

## AbortRecording

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/ProductFileRecordManager.cs` — 行 [274]

## AddRecord

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [359, 316, 278]

## AppendToTempFile

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [252]

## ClonePointCloud

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [858, 818, 247]

## EndSeamTraceYSession

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/ProductFileRecordManager.cs` — 行 [390]

## EnsureDateRecordDirectory

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [623, 449]

## EnsureDirectoriesExist

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [1001, 989, 977, 621, 447, 163]

## EnsureSessionDirectory

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [628, 455]

## EnsureWorker

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Abstractions/ProductRecordBase.cs` — 行 [219]

## FlushPending

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Abstractions/ProductRecordBase.cs` — 行 [245, 232]

## FlushSeamTraceY

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/ProductFileRecordManager.cs` — 行 [389]

## FlushToFile

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/SeamTraceYRecord.cs` — 行 [157]

## LoadConfigFromIni

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/ProductFileRecordManager.cs` — 行 [190]

## NormalizeDirectoryPath

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/ProductFileRecordManager.cs` — 行 [646, 645]

## ObfuscateBytes

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [897]

## OnAbort

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Abstractions/ProductRecordBase.cs` — 行 [246]

## OnStart

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Abstractions/ProductRecordBase.cs` — 行 [220]

## OnStop

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Abstractions/ProductRecordBase.cs` — 行 [233]

## ParseFromTempFile

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [619]

## Persist

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Abstractions/ProductRecordBase.cs` — 行 [174]

## PickExisting

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/ProductFileRecordManager.cs` — 行 [419, 418, 417]

## ReadActionFromStream

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [583]

## ReadPDatFile

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [913]

## ReadPointCloudFromStream

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [574]

## RecordWeldResult

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/ProductFileRecordManager.cs` — 行 [392]

## SaveActionsToPDat

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [635, 462]

## SaveFramesToPly

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [631, 458]

## SaveTempFileInternal

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [212]

## StartRecording

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/ProductFileRecordManager.cs` — 行 [351]

## StopRecording

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/ProductFileRecordManager.cs` — 行 [388]

## WriteActionToStream

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [504]

## WritePointCloudToStream

> 1 处调用 / 1 个调用方文件

- `ProductFileControl/Records/RecordFileStore.cs` — 行 [537, 498]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
