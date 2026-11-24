---
title: CodeMap-Relations-Methods-MainDeviceControl-2 — 代码地图·方法级影响面·MainDeviceControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-MainDeviceControl-2 — 方法级影响面（低置信 · 调用方在 MainDeviceControl · 名首字母 N-Z）

> **一句话**：**调用方位于 `MainDeviceControl` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 110 |
| 调用点数 | 130 |

## 章节导航

- [NewWorkThread](#NewWorkThread)
- [Normalize](#Normalize)
- [NotifyTaZeroPoseStageChanged](#NotifyTaZeroPoseStageChanged)
- [OnSeamTrackingStart](#OnSeamTrackingStart)
- [OnSeamTrackingStop](#OnSeamTrackingStop)
- [OnStateSwitched](#OnStateSwitched)
- [OnWeldStatusChanged](#OnWeldStatusChanged)
- [OutputCspTick](#OutputCspTick)
- [PrepareSimulationCamera](#PrepareSimulationCamera)
- [PrepareSimulationMonitorCam](#PrepareSimulationMonitorCam)
- [PvtTick](#PvtTick)
- [QueueCspSegment](#QueueCspSegment)
- [RaiseInitSummary](#RaiseInitSummary)
- [RaiseNoValueAlarm](#RaiseNoValueAlarm)
- [ReadDouble](#ReadDouble)
- [ReadInt](#ReadInt)
- [ReadPhysicalEmg](#ReadPhysicalEmg)
- [ReadWord](#ReadWord)
- [ReadinessName](#ReadinessName)
- [RecordCspPoint](#RecordCspPoint)
- [RecordInitOutcome](#RecordInitOutcome)
- [RecordOnlyTick](#RecordOnlyTick)
- [RegisterWorkThread](#RegisterWorkThread)
- [ReleaseCameraBinding](#ReleaseCameraBinding)
- [ReportAlarm](#ReportAlarm)
- [ReportAlarmCleared](#ReportAlarmCleared)
- [ReportCspResult](#ReportCspResult)
- [ReportStrokeClamp](#ReportStrokeClamp)
- [RequireStandby](#RequireStandby)
- [ResetAxesToWorkZero](#ResetAxesToWorkZero)
- [ResetFailureCounters](#ResetFailureCounters)
- [ResetSeamAxisBufferBeforeMove](#ResetSeamAxisBufferBeforeMove)
- [ResetStepTime](#ResetStepTime)
- [ResetToIdle](#ResetToIdle)
- [ResetWorkTime](#ResetWorkTime)
- [ResolveCspQueryRobotX](#ResolveCspQueryRobotX)
- [ResolveGalvoPattern](#ResolveGalvoPattern)
- [RunAutoAdjust](#RunAutoAdjust)
- [RunCspTick](#RunCspTick)
- [RunInitializeSteps](#RunInitializeSteps)
- [RunStepAction](#RunStepAction)
- [RunTaHomeThenZeroPose](#RunTaHomeThenZeroPose)
- [RxCodeToCommandName](#RxCodeToCommandName)
- [SafeShutdownPeripherals](#SafeShutdownPeripherals)
- [SaveSimulation](#SaveSimulation)
- [ScanMotionBusFault](#ScanMotionBusFault)
- [ScanPulseIo](#ScanPulseIo)
- [ScanRunningIo](#ScanRunningIo)
- [SendCutWireRequest](#SendCutWireRequest)
- [SendRobotCommand](#SendRobotCommand)
- [SendToRobot](#SendToRobot)
- [SetState](#SetState)
- [SetStatus](#SetStatus)
- [SetVirtualIo](#SetVirtualIo)
- [SetWeldStatus](#SetWeldStatus)
- [SetWorkThreadState](#SetWorkThreadState)
- [SettleConnect](#SettleConnect)
- [ShutdownBudgetExceeded](#ShutdownBudgetExceeded)
- [ShutdownSeamAxis](#ShutdownSeamAxis)
- [SimMonitorCamStartWeld](#SimMonitorCamStartWeld)
- [SimMonitorCamStopWeld](#SimMonitorCamStopWeld)
- [SimPrepareCamera](#SimPrepareCamera)
- [SimScheduleTick](#SimScheduleTick)
- [SimTestWorkClose](#SimTestWorkClose)
- [SimTestWorkOpen](#SimTestWorkOpen)
- [SimTick](#SimTick)
- [SnapshotVirtualIo](#SnapshotVirtualIo)
- [StartCspOutput](#StartCspOutput)
- [StartLineLaserNode](#StartLineLaserNode)
- [StartMonitorCamNode](#StartMonitorCamNode)
- [StartMotionNode](#StartMotionNode)
- [StartRobotCommNode](#StartRobotCommNode)
- [StartRobotXSimulation](#StartRobotXSimulation)
- [StartWeldHeadNode](#StartWeldHeadNode)
- [StepCspTarget](#StepCspTarget)
- [Stop](#Stop)
- [StopCspOutput](#StopCspOutput)
- [StopPendingConnectThreads](#StopPendingConnectThreads)
- [StopRobotXSimulation](#StopRobotXSimulation)
- [StopSeamTrackingOutput](#StopSeamTrackingOutput)
- [StopWeldPreview](#StopWeldPreview)
- [SubDeviceWork](#SubDeviceWork)
- [SubscribeCameraEvents](#SubscribeCameraEvents)
- [SubscribeWeldHeadEvents](#SubscribeWeldHeadEvents)
- [SuspendRealHardwareForSimulation](#SuspendRealHardwareForSimulation)
- [TaMoveTo](#TaMoveTo)
- [TaMoveToPreset](#TaMoveToPreset)
- [TakeCspElapsedSeconds](#TakeCspElapsedSeconds)
- [TakeElapsed](#TakeElapsed)
- [TickXlOutput](#TickXlOutput)
- [TimeBeginPeriod](#TimeBeginPeriod)
- [TimeEndPeriod](#TimeEndPeriod)
- [ToPulseMm](#ToPulseMm)
- [TranslateCommand](#TranslateCommand)
- [TryFlushSeamBuffer](#TryFlushSeamBuffer)
- [TryGetSeamAxisSoftLimit](#TryGetSeamAxisSoftLimit)
- [TryHomeAxisWithWait](#TryHomeAxisWithWait)
- [TryMoveAxisToTarget](#TryMoveAxisToTarget)
- [TryParseFirstDouble](#TryParseFirstDouble)
- [TryResolveTaTorque](#TryResolveTaTorque)
- [TrySplitPayload](#TrySplitPayload)
- [TryStartSeamTraceYOnReady](#TryStartSeamTraceYOnReady)
- [TxCodeToCommandName](#TxCodeToCommandName)
- [UnsubscribeCameraEvents](#UnsubscribeCameraEvents)
- [UnsubscribeWeldHeadEvents](#UnsubscribeWeldHeadEvents)
- [UpdateSeamTracking](#UpdateSeamTracking)
- [WaitChildConnectedTick](#WaitChildConnectedTick)
- [WaitChildDisconnected](#WaitChildDisconnected)
- [WeldStatusTrans](#WeldStatusTrans)
- [WirePlaybackEvents](#WirePlaybackEvents)

## ResetStepTime

> 6 处调用 / 6 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs` — 行 [243]
- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [487]
- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [741]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [685]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1264]
- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [531]

## SetState

> 6 处调用 / 6 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` — 行 [187]
- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [572, 564, 505, 495, 226, 209]
- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [783, 767, 529, 496]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [822, 791, 725, 699]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2056, 2047, 1988, 1959]
- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [605, 595, 554, 541]

## SetWeldStatus

> 6 处调用 / 6 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs` — 行 [204]
- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [553, 506, 496, 481, 473]
- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [784, 768, 763, 735, 723, 712, 632, 595, 570, 549, 511, 504, 375, 365]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [765, 726, 724, 705, 679, 669, 649, 646, 565, 557, 418, 409, 406, 327]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1989, 1960, 1258, 476]
- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [604, 555, 553, 544, 525, 514, 474, 454, 439, 402, 395, 370, 365, 361, 353, 338, 328, 287, 275]

## ReadInt

> 5 处调用 / 5 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [530]
- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [807, 805, 804]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [748]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2908, 2010]
- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [570]

## Stop

> 2 处调用 / 2 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [821, 723, 667]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2055]

## NewWorkThread

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2726, 2715, 2698, 2697, 2696, 2695, 2694, 1454]

## Normalize

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/CommandCore.cs` — 行 [265, 185, 127]

## NotifyTaZeroPoseStageChanged

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2255, 2244, 2235]

## OnSeamTrackingStart

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1025]

## OnSeamTrackingStop

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1026]

## OnStateSwitched

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` — 行 [100]

## OnWeldStatusChanged

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` — 行 [113]

## OutputCspTick

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1103]

## PrepareSimulationCamera

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3592]

## PrepareSimulationMonitorCam

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3595]

## PvtTick

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1032]

## QueueCspSegment

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1469]

## RaiseInitSummary

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3141]

## RaiseNoValueAlarm

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1431]

## ReadDouble

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [806]

## ReadPhysicalEmg

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [337]

## ReadWord

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [733, 731, 729, 727, 725]

## ReadinessName

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs` — 行 [385, 385]

## RecordCspPoint

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1815, 1474, 1115]

## RecordInitOutcome

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3296, 3290, 3278, 3255, 3235, 3223, 3210]

## RecordOnlyTick

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1102]

## RegisterWorkThread

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [691]

## ReleaseCameraBinding

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [917, 913, 782, 528]

## ReportAlarm

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2264, 2215, 2073]

## ReportAlarmCleared

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2221]

## ReportCspResult

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1622]

## ReportStrokeClamp

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1456]

## RequireStandby

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [553]

## ResetAxesToWorkZero

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1246]

## ResetFailureCounters

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [721, 566, 234]

## ResetSeamAxisBufferBeforeMove

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [837, 737]

## ResetToIdle

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1236, 892]

## ResetWorkTime

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [347, 281]

## ResolveCspQueryRobotX

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1424]

## ResolveGalvoPattern

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [282]

## RunAutoAdjust

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [323]

## RunCspTick

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1413]

## RunInitializeSteps

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [151]

## RunStepAction

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [181, 179, 177]

## RunTaHomeThenZeroPose

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2910]

## RxCodeToCommandName

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/CommandCore.cs` — 行 [274]

## SafeShutdownPeripherals

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [911, 781, 720, 609, 527, 355, 243, 226]

## SaveSimulation

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3612]

## ScanMotionBusFault

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [155]

## ScanPulseIo

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [283, 282, 281, 280, 279, 277, 276, 275, 274, 273]

## ScanRunningIo

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [141]

## SendCutWireRequest

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2277, 2272]

## SendRobotCommand

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3560, 3534, 3484]

## SendToRobot

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [417, 310, 163]

## SetStatus

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3662, 3575, 3561, 3528, 3509, 3485, 3476, 3449, 3417, 3366, 3361, 3343, 3309, 2050, 1283]

## SetVirtualIo

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3461, 3434, 3394, 3325, 2831, 914]

## SetWorkThreadState

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2788, 2784, 2777]

## SettleConnect

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` — 行 [186, 166]

## ShutdownBudgetExceeded

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2570, 2563, 2557, 2551, 2545, 2538]

## ShutdownSeamAxis

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [841, 742]

## SimMonitorCamStartWeld

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1787]

## SimMonitorCamStopWeld

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3636, 1631, 1621, 1611]

## SimPrepareCamera

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [661]

## SimScheduleTick

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1483]

## SimTestWorkClose

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3664, 2559]

## SimTestWorkOpen

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3607]

## SimTick

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1482]

## SnapshotVirtualIo

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2386]

## StartCspOutput

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1062]

## StartLineLaserNode

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2928]

## StartMonitorCamNode

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2933]

## StartMotionNode

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2916]

## StartRobotCommNode

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2911]

## StartRobotXSimulation

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3598]

## StartWeldHeadNode

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2921]

## StepCspTarget

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1813, 1466]

## StopCspOutput

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1542, 1498, 1408, 1298, 1074, 939, 817]

## StopPendingConnectThreads

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [925]

## StopRobotXSimulation

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3663]

## StopSeamTrackingOutput

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2033, 2026, 903, 831, 729]

## StopWeldPreview

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [851]

## SubDeviceWork

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [795, 792, 789, 786, 783]

## SubscribeCameraEvents

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [219]

## SubscribeWeldHeadEvents

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [169]

## SuspendRealHardwareForSimulation

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3601]

## TaMoveTo

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2607]

## TaMoveToPreset

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2887, 2885]

## TakeCspElapsedSeconds

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1813, 1422]

## TakeElapsed

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1818, 1695, 1654, 1506, 1505, 1005]

## TickXlOutput

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [501]

## TimeBeginPeriod

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1302]

## TimeEndPeriod

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1373]

## ToPulseMm

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1571, 1571, 1510, 1466]

## TranslateCommand

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/CommandCore.cs` — 行 [287, 276]

## TryFlushSeamBuffer

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1110]

## TryGetSeamAxisSoftLimit

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1697, 1682, 675]

## TryHomeAxisWithWait

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2995, 2948]

## TryMoveAxisToTarget

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2969]

## TryParseFirstDouble

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1021]

## TryResolveTaTorque

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2634]

## TrySplitPayload

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/CommandCore.cs` — 行 [188]

## TryStartSeamTraceYOnReady

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1018]

## TxCodeToCommandName

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/CommandCore.cs` — 行 [285]

## UnsubscribeCameraEvents

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [929, 707, 547, 225]

## UnsubscribeWeldHeadEvents

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [234]

## UpdateSeamTracking

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1209]

## WaitChildConnectedTick

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3294]

## WaitChildDisconnected

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1215]

## WeldStatusTrans

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1809]

## WirePlaybackEvents

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [295]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
