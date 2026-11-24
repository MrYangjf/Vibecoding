---
title: CodeMap-Relations-Methods-LineLaserCam — 代码地图·方法级影响面·LineLaserCam（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-LineLaserCam — 方法级影响面（低置信 · 调用方在 LineLaserCam）

> **一句话**：**调用方位于 `LineLaserCam` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 52 |
| 调用点数 | 60 |

## 章节导航

- [ApplyConfig](#ApplyConfig)
- [ApplyFrameRateModel](#ApplyFrameRateModel)
- [BuildCloudFromInspect](#BuildCloudFromInspect)
- [BuildResult](#BuildResult)
- [ConnectCore](#ConnectCore)
- [ConvertCalibration](#ConvertCalibration)
- [FetchCurrentJobId](#FetchCurrentJobId)
- [FetchJobList](#FetchJobList)
- [FetchJointTypes](#FetchJointTypes)
- [FindOtherRunningCamera](#FindOtherRunningCamera)
- [FreeCallbackHandles](#FreeCallbackHandles)
- [GenerateFrame](#GenerateFrame)
- [GenerateSeamContour](#GenerateSeamContour)
- [HandleEmptyFrame](#HandleEmptyFrame)
- [HandleFrameReady](#HandleFrameReady)
- [IsActiveSender](#IsActiveSender)
- [LoadConfig](#LoadConfig)
- [Log](#Log)
- [Make64Bytes](#Make64Bytes)
- [OpenSensor](#OpenSensor)
- [RaiseProfileReady](#RaiseProfileReady)
- [RaiseResultReady](#RaiseResultReady)
- [RaiseStateChanged](#RaiseStateChanged)
- [ReadAsciiBytes](#ReadAsciiBytes)
- [ReadBool](#ReadBool)
- [ReadDouble](#ReadDouble)
- [ReadInt](#ReadInt)
- [RecordLocalFailure](#RecordLocalFailure)
- [RecordVendorResult](#RecordVendorResult)
- [Register](#Register)
- [RegisterCallbacks](#RegisterCallbacks)
- [ReleaseCamera](#ReleaseCamera)
- [ReleaseNativeResources](#ReleaseNativeResources)
- [RenderDisplayFrame](#RenderDisplayFrame)
- [ResetMeasuredFps](#ResetMeasuredFps)
- [SanitizeSeconds](#SanitizeSeconds)
- [SaveConfig](#SaveConfig)
- [SelectIntelligentLaser](#SelectIntelligentLaser)
- [SelectVirtual](#SelectVirtual)
- [SetActive](#SetActive)
- [SetInvalidInspect](#SetInvalidInspect)
- [SetLaser](#SetLaser)
- [SetSensor](#SetSensor)
- [ShutdownPeripherals](#ShutdownPeripherals)
- [StopAcquisition](#StopAcquisition)
- [StopSimTimer](#StopSimTimer)
- [SyncHardwareStatus](#SyncHardwareStatus)
- [UpdateDisplayMat](#UpdateDisplayMat)
- [UpdateFrameRate](#UpdateFrameRate)
- [UpdateProfileSnapshot](#UpdateProfileSnapshot)
- [WaitForCallbacksToFinish](#WaitForCallbacksToFinish)
- [WriteConfigNodes](#WriteConfigNodes)

## Log

> 5 处调用 / 5 个调用方文件

- `LineLaserCam/ILineLaser/LineLaserCameraBase.cs` — 行 [157]
- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1369, 1290, 1279, 1061, 1029, 1003, 947, 918, 887, 858, 809, 772, 735, 712, 707, 645, 639, 623, 593, 558, 554, 526, 507, 500, 495, 420, 415, 389, 382, 377, 326, 294, 278]
- `LineLaserCam/LineLaserConfig.cs` — 行 [244, 228, 196, 190]
- `LineLaserCam/LineLaserManager.cs` — 行 [767, 634, 398, 368, 365, 359]
- `LineLaserCam/VirtualCam/VirtualCam.cs` — 行 [171]

## RaiseProfileReady

> 2 处调用 / 2 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1183, 1176]
- `LineLaserCam/VirtualCam/VirtualCam.cs` — 行 [165]

## RaiseResultReady

> 2 处调用 / 2 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1175]
- `LineLaserCam/VirtualCam/VirtualCam.cs` — 行 [164]

## RaiseStateChanged

> 2 处调用 / 2 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [670, 655, 307]
- `LineLaserCam/VirtualCam/VirtualCam.cs` — 行 [200, 192]

## UpdateDisplayMat

> 2 处调用 / 2 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [466]
- `LineLaserCam/VirtualCam/VirtualCam.cs` — 行 [208]

## ApplyConfig

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [740, 582, 575, 212, 197]

## ApplyFrameRateModel

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [756]

## BuildCloudFromInspect

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1045]

## BuildResult

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/VirtualCam/VirtualCam.cs` — 行 [164]

## ConnectCore

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [636, 402]

## ConvertCalibration

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [506]

## FetchCurrentJobId

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [836]

## FetchJobList

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [838]

## FetchJointTypes

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [828, 819]

## FindOtherRunningCamera

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [631]

## FreeCallbackHandles

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [351]

## GenerateFrame

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/VirtualCam/VirtualCam.cs` — 行 [150]

## GenerateSeamContour

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/VirtualCam/VirtualCam.cs` — 行 [158]

## HandleEmptyFrame

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1056]

## HandleFrameReady

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1048]

## IsActiveSender

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [432, 421]

## LoadConfig

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserConfig.cs` — 行 [178]

## Make64Bytes

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1433, 1429, 909]

## OpenSensor

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [429]

## ReadAsciiBytes

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1319, 1315, 1243, 549, 548, 547, 546, 545, 544]

## ReadBool

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserConfig.cs` — 行 [208, 206, 201]

## ReadDouble

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserConfig.cs` — 行 [207]

## ReadInt

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserConfig.cs` — 行 [215, 213, 211, 204, 200]

## RecordLocalFailure

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1418, 946, 930, 917, 900, 886, 870, 622, 605]

## RecordVendorResult

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1441, 940, 911, 880, 617, 302, 293, 277]

## Register

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [211, 196]

## RegisterCallbacks

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [285]

## ReleaseCamera

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [343]

## ReleaseNativeResources

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [472, 459]

## RenderDisplayFrame

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [447, 439]

## ResetMeasuredFps

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [668]

## SanitizeSeconds

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserConfig.cs` — 行 [214, 212, 210]

## SaveConfig

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserConfig.cs` — 行 [189]

## SelectIntelligentLaser

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [181]

## SelectVirtual

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [177]

## SetActive

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [620, 583, 576]

## SetInvalidInspect

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1127, 1084]

## SetLaser

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [405]

## SetSensor

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [444, 434, 404]

## ShutdownPeripherals

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [653, 336]

## StopAcquisition

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [691]

## StopSimTimer

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/VirtualCam/VirtualCam.cs` — 行 [207, 199]

## SyncHardwareStatus

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [306]

## UpdateFrameRate

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [1091]

## UpdateProfileSnapshot

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserManager.cs` — 行 [446]

## WaitForCallbacksToFinish

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 [344]

## WriteConfigNodes

> 1 处调用 / 1 个调用方文件

- `LineLaserCam/LineLaserConfig.cs` — 行 [240, 222]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
