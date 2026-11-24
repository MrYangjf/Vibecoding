---
title: CodeMap-Relations-Methods-FileOperate — 代码地图·方法级影响面·FileOperate（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-FileOperate — 方法级影响面（低置信 · 调用方在 FileOperate）

> **一句话**：**调用方位于 `FileOperate` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 39 |
| 调用点数 | 39 |

## 章节导航

- [Backup](#Backup)
- [BuildDisplayName](#BuildDisplayName)
- [BuildMigrationMap](#BuildMigrationMap)
- [CheckFile](#CheckFile)
- [CheckLogLife](#CheckLogLife)
- [CopyDirectory](#CopyDirectory)
- [DetectChildIndent](#DetectChildIndent)
- [DetectNewline](#DetectNewline)
- [DetectNodeIndent](#DetectNodeIndent)
- [EnsureChildren](#EnsureChildren)
- [FindMatch](#FindMatch)
- [FindMissingIniKeys](#FindMissingIniKeys)
- [FindSectionInsertIndex](#FindSectionInsertIndex)
- [GetDate](#GetDate)
- [GetElement](#GetElement)
- [GetElementByPath](#GetElementByPath)
- [GetNowToString](#GetNowToString)
- [InitLogDir](#InitLogDir)
- [InitLogFilePath](#InitLogFilePath)
- [InsertAtTail](#InsertAtTail)
- [LoadFromFile](#LoadFromFile)
- [Log](#Log)
- [LogBuildSummary](#LogBuildSummary)
- [MoveDirectoryIfNeeded](#MoveDirectoryIfNeeded)
- [MoveToCurrentPath](#MoveToCurrentPath)
- [NewXdocument](#NewXdocument)
- [PatchIniText](#PatchIniText)
- [PruneEmptyDirectories](#PruneEmptyDirectories)
- [ReadString](#ReadString)
- [ReadTextPreserveEncoding](#ReadTextPreserveEncoding)
- [ReadXmlPreserve](#ReadXmlPreserve)
- [ReplaceFile](#ReplaceFile)
- [SaveXdocument](#SaveXdocument)
- [TryDelete](#TryDelete)
- [VerifyXml](#VerifyXml)
- [WriteIniTemplate](#WriteIniTemplate)
- [WriteString](#WriteString)
- [WriteTextAtomically](#WriteTextAtomically)
- [WriteXmlAtomically](#WriteXmlAtomically)

## Backup

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [242, 201]

## BuildDisplayName

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [522]

## BuildMigrationMap

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigPathMigrator.cs` — 行 [161]

## CheckFile

> 1 处调用 / 1 个调用方文件

- `FileOperate/XdocumentReaderWriter.cs` — 行 [62]

## CheckLogLife

> 1 处调用 / 1 个调用方文件

- `FileOperate/Log.cs` — 行 [37, 21]

## CopyDirectory

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigBackupHelper.cs` — 行 [92, 30]

## DetectChildIndent

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [560]

## DetectNewline

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [559]

## DetectNodeIndent

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [604, 568]

## EnsureChildren

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [647, 516, 137]

## FindMatch

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [512]

## FindMissingIniKeys

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [83, 74]

## FindSectionInsertIndex

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [376, 370]

## GetDate

> 1 处调用 / 1 个调用方文件

- `FileOperate/Log.cs` — 行 [94]

## GetElement

> 1 处调用 / 1 个调用方文件

- `FileOperate/XdocumentReaderWriter.cs` — 行 [425, 408]

## GetElementByPath

> 1 处调用 / 1 个调用方文件

- `FileOperate/XdocumentReaderWriter.cs` — 行 [417, 398]

## GetNowToString

> 1 处调用 / 1 个调用方文件

- `FileOperate/Log.cs` — 行 [195, 190, 185, 180]

## InitLogDir

> 1 处调用 / 1 个调用方文件

- `FileOperate/Log.cs` — 行 [20]

## InitLogFilePath

> 1 处调用 / 1 个调用方文件

- `FileOperate/Log.cs` — 行 [130]

## InsertAtTail

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [521]

## LoadFromFile

> 1 处调用 / 1 个调用方文件

- `FileOperate/INIFile.cs` — 行 [319, 45]

## Log

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [703, 657, 650, 263, 212, 150, 127, 98, 86, 69]

## LogBuildSummary

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [682, 670, 145, 92]

## MoveDirectoryIfNeeded

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigPathMigrator.cs` — 行 [178]

## MoveToCurrentPath

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigPathMigrator.cs` — 行 [166]

## NewXdocument

> 1 处调用 / 1 个调用方文件

- `FileOperate/XdocumentReaderWriter.cs` — 行 [77, 68]

## PatchIniText

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [78]

## PruneEmptyDirectories

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigPathMigrator.cs` — 行 [190, 149]

## ReadString

> 1 处调用 / 1 个调用方文件

- `FileOperate/INIFile.cs` — 行 [120, 105, 90]

## ReadTextPreserveEncoding

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [82, 73]

## ReadXmlPreserve

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [132]

## ReplaceFile

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [257, 206]

## SaveXdocument

> 1 处调用 / 1 个调用方文件

- `FileOperate/XdocumentReaderWriter.cs` — 行 [189, 69]

## TryDelete

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [262, 211]

## VerifyXml

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [144, 128]

## WriteIniTemplate

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [67]

## WriteString

> 1 处调用 / 1 个调用方文件

- `FileOperate/INIFile.cs` — 行 [240, 231, 222]

## WriteTextAtomically

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [487, 79]

## WriteXmlAtomically

> 1 处调用 / 1 个调用方文件

- `FileOperate/ConfigSelfHeal.cs` — 行 [227, 141, 125]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
