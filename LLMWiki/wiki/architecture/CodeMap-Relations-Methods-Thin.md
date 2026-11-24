---
title: CodeMap-Relations-Methods-Thin — 代码地图·方法级影响面·薄模块合并页（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-Thin — 方法级影响面（低置信 · 调用方在 薄模块合并页）

> **一句话**：**调用方位于 `薄模块合并页` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 38 |
| 调用点数 | 39 |

## 章节导航

- [AbsolutePath](#AbsolutePath)
- [AnnotateSpot](#AnnotateSpot)
- [BuildIniDefaults](#BuildIniDefaults)
- [BuildMat](#BuildMat)
- [CollectScalars](#CollectScalars)
- [Disconnect](#Disconnect)
- [Display](#Display)
- [Emit](#Emit)
- [EnsureRecordDirectory](#EnsureRecordDirectory)
- [EnsureSdkInitialized](#EnsureSdkInitialized)
- [EvaluateHealth](#EvaluateHealth)
- [GetRecordFrameRate](#GetRecordFrameRate)
- [IsChanged](#IsChanged)
- [IsColorPixelFormat](#IsColorPixelFormat)
- [IsIgnored](#IsIgnored)
- [IsScalar](#IsScalar)
- [LoadFromIni](#LoadFromIni)
- [ModuleRelativeDir](#ModuleRelativeDir)
- [QueryDeviceIp](#QueryDeviceIp)
- [RaiseFrameCompleted](#RaiseFrameCompleted)
- [ReadFrameFormat](#ReadFrameFormat)
- [RecordLocalFailure](#RecordLocalFailure)
- [RecordVendorResult](#RecordVendorResult)
- [RelativeToBase](#RelativeToBase)
- [Same](#Same)
- [SaveIniWithAudit](#SaveIniWithAudit)
- [SaveToIni](#SaveToIni)
- [SetProcessDPIAware](#SetProcessDPIAware)
- [SetState](#SetState)
- [StartGrabThreadLocked](#StartGrabThreadLocked)
- [StopCapture](#StopCapture)
- [StopRecord](#StopRecord)
- [StopSupervision](#StopSupervision)
- [SupervisionTransitionTo](#SupervisionTransitionTo)
- [TriggerSingleShot](#TriggerSingleShot)
- [TrySelectDevice](#TrySelectDevice)
- [Walk](#Walk)
- [Write](#Write)

## StopCapture

> 2 处调用 / 2 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [286]
- `MonitorCam/MonitorCamManager.cs` — 行 [356]

## AbsolutePath

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/ConfigFileManager.cs` — 行 [50]

## AnnotateSpot

> 1 处调用 / 1 个调用方文件

- `MonitorCam/MonitorCamManager.cs` — 行 [381, 215]

## BuildIniDefaults

> 1 处调用 / 1 个调用方文件

- `MonitorCam/MonitorCamConfig.cs` — 行 [165, 145]

## BuildMat

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [865, 468, 327]

## CollectScalars

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/ConfigChangeLogger.cs` — 行 [155, 154]

## Disconnect

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [658]

## Display

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/ConfigChangeLogger.cs` — 行 [130, 130]

## Emit

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/ConfigChangeLogger.cs` — 行 [184, 166]

## EnsureRecordDirectory

> 1 处调用 / 1 个调用方文件

- `MonitorCam/MonitorCamManager.cs` — 行 [166]

## EnsureSdkInitialized

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [242, 129]

## EvaluateHealth

> 1 处调用 / 1 个调用方文件

- `MonitorCam/MonitorCamManager.cs` — 行 [569]

## GetRecordFrameRate

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [519]

## IsChanged

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/ConfigChangeLogger.cs` — 行 [179, 164]

## IsColorPixelFormat

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [745]

## IsIgnored

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/ConfigChangeLogger.cs` — 行 [58, 38]

## IsScalar

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/ConfigChangeLogger.cs` — 行 [58, 38]

## LoadFromIni

> 1 处调用 / 1 个调用方文件

- `MonitorCam/MonitorCamConfig.cs` — 行 [130]

## ModuleRelativeDir

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/ConfigFileManager.cs` — 行 [131, 119, 101]

## QueryDeviceIp

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [708, 259]

## RaiseFrameCompleted

> 1 处调用 / 1 个调用方文件

- `MonitorCam/MonitorCamManager.cs` — 行 [537, 531]

## ReadFrameFormat

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [509]

## RecordLocalFailure

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [537, 511, 502, 495, 430, 382, 351, 329, 313, 197, 155, 147, 131]

## RecordVendorResult

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [526, 480, 460, 451, 443, 376, 368, 331, 320, 190, 164, 139]

## RelativeToBase

> 1 处调用 / 1 个调用方文件

- `MonitorCam/MonitorCamConfig.cs` — 行 [164, 144]

## Same

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/ConfigSnapshot.cs` — 行 [99]

## SaveIniWithAudit

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/ConfigFileManager.cs` — 行 [161]

## SaveToIni

> 1 处调用 / 1 个调用方文件

- `MonitorCam/MonitorCamConfig.cs` — 行 [123]

## SetProcessDPIAware

> 1 处调用 / 1 个调用方文件

- `Program.cs` — 行 [23]

## SetState

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [299, 198, 191, 166, 156, 148, 140, 132]

## StartGrabThreadLocked

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [375]

## StopRecord

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [396]

## StopSupervision

> 1 处调用 / 1 个调用方文件

- `MonitorCam/MonitorCamManager.cs` — 行 [502, 289]

## SupervisionTransitionTo

> 1 处调用 / 1 个调用方文件

- `MonitorCam/MonitorCamManager.cs` — 行 [602, 494, 457]

## TriggerSingleShot

> 1 处调用 / 1 个调用方文件

- `MonitorCam/MonitorCamManager.cs` — 行 [375]

## TrySelectDevice

> 1 处调用 / 1 个调用方文件

- `MonitorCam/HikCam/HikCam.cs` — 行 [145]

## Walk

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/ConfigSnapshot.cs` — 行 [74, 59]

## Write

> 1 处调用 / 1 个调用方文件

- `ConfigFileControl/Implementations/XmlConfigFile.cs` — 行 [96]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
