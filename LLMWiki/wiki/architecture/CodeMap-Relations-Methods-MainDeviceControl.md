---
title: CodeMap-Relations-Methods-MainDeviceControl — 代码地图·方法级影响面·MainDeviceControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-MainDeviceControl — 方法级影响面（低置信 · 调用方在 MainDeviceControl · 名首字母 A-M）

> **一句话**：**调用方位于 `MainDeviceControl` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 176 |
| 调用点数 | 205 |

## 章节导航

- [AdvanceInitNode](#AdvanceInitNode)
- [AdvanceStep](#AdvanceStep)
- [AllInitTargetsConnected](#AllInitTargetsConnected)
- [AnalyzeImage](#AnalyzeImage)
- [ApplyGalvoAmplitude](#ApplyGalvoAmplitude)
- [ApplyLaFollow](#ApplyLaFollow)
- [ApplyRobotStopPose](#ApplyRobotStopPose)
- [ApplySpotAlignCompensation](#ApplySpotAlignCompensation)
- [AttachSeamTrackAxis](#AttachSeamTrackAxis)
- [BeginConnectAttempt](#BeginConnectAttempt)
- [BeginWeldMonitor](#BeginWeldMonitor)
- [BindCamera](#BindCamera)
- [BuildInitOrderText](#BuildInitOrderText)
- [BuildInitPlan](#BuildInitPlan)
- [BuildMachineInitSummary](#BuildMachineInitSummary)
- [BuildTxCodeReverse](#BuildTxCodeReverse)
- [CalcGalvoAmplitude](#CalcGalvoAmplitude)
- [CalcGalvoFrequency](#CalcGalvoFrequency)
- [CascadeClearStatus](#CascadeClearStatus)
- [CascadeDisconnect](#CascadeDisconnect)
- [CascadeDisconnectWithWait](#CascadeDisconnectWithWait)
- [CascadeResetProcess](#CascadeResetProcess)
- [CascadeWeldStatus](#CascadeWeldStatus)
- [CheckActionGate](#CheckActionGate)
- [CheckAutoWeldingConflict](#CheckAutoWeldingConflict)
- [CheckDevice](#CheckDevice)
- [CheckDeviceStates](#CheckDeviceStates)
- [CheckLowerBound](#CheckLowerBound)
- [CheckPlc](#CheckPlc)
- [CheckSubWorkPending](#CheckSubWorkPending)
- [CheckTaAvailable](#CheckTaAvailable)
- [CheckUpperBound](#CheckUpperBound)
- [CheckWeldProgress](#CheckWeldProgress)
- [ClampToStroke](#ClampToStroke)
- [ClearAllVirtualIo](#ClearAllVirtualIo)
- [ClearMachine](#ClearMachine)
- [ClearRobotCommand](#ClearRobotCommand)
- [ClearStatus](#ClearStatus)
- [CloseRobotChannel](#CloseRobotChannel)
- [CommWork](#CommWork)
- [ComposeWireFeedSpeed](#ComposeWireFeedSpeed)
- [ConfigureSoftTargetReachWindow](#ConfigureSoftTargetReachWindow)
- [ConnectWorker](#ConnectWorker)
- [CorrectIllegalCombination](#CorrectIllegalCombination)
- [CspTick](#CspTick)
- [DequeueCommand](#DequeueCommand)
- [DetachSeamTrackAxis](#DetachSeamTrackAxis)
- [DetectCspExecutionStall](#DetectCspExecutionStall)
- [DisableSimulation](#DisableSimulation)
- [DisconnectChild](#DisconnectChild)
- [DisconnectWorker](#DisconnectWorker)
- [DispatchAction](#DispatchAction)
- [DisposeComponents](#DisposeComponents)
- [DisposeFrame](#DisposeFrame)
- [DisposeManaged](#DisposeManaged)
- [DoAcquireTrigger](#DoAcquireTrigger)
- [DoAcquireWait](#DoAcquireWait)
- [DoAnalyze](#DoAnalyze)
- [DoClearAlarm](#DoClearAlarm)
- [DoCompute](#DoCompute)
- [DoEstopMachine](#DoEstopMachine)
- [DoFinishFail](#DoFinishFail)
- [DoFinishOk](#DoFinishOk)
- [DoInitializeMachine](#DoInitializeMachine)
- [DoMotionBusFault](#DoMotionBusFault)
- [DoOutput](#DoOutput)
- [DoPreWork](#DoPreWork)
- [DoPreWorkOn](#DoPreWorkOn)
- [DoPreWorkStable](#DoPreWorkStable)
- [DoPreWorkWaitWork](#DoPreWorkWaitWork)
- [DoResetMachine](#DoResetMachine)
- [DoReturnToCalibration](#DoReturnToCalibration)
- [DoServoOn](#DoServoOn)
- [DoStartMachine](#DoStartMachine)
- [DoStopMachine](#DoStopMachine)
- [DoStopping](#DoStopping)
- [DoSubAlarmStop](#DoSubAlarmStop)
- [DoSubManualStop](#DoSubManualStop)
- [DoSubPrework](#DoSubPrework)
- [DoSubStop](#DoSubStop)
- [DoSubWork](#DoSubWork)
- [DoWorking](#DoWorking)
- [DriveTricolorLamp](#DriveTricolorLamp)
- [EmergencyStop](#EmergencyStop)
- [EnableAxesAfterInit](#EnableAxesAfterInit)
- [EndInitWithoutChain](#EndInitWithoutChain)
- [EndProductSessionSafely](#EndProductSessionSafely)
- [EndWeldMonitor](#EndWeldMonitor)
- [EnqueueSeamPoints](#EnqueueSeamPoints)
- [EnsureCommandWorkStarted](#EnsureCommandWorkStarted)
- [EnsureConnected](#EnsureConnected)
- [EnsureHeartbeatThread](#EnsureHeartbeatThread)
- [EnsureManualWeldHeadActionAllowed](#EnsureManualWeldHeadActionAllowed)
- [EnsureResetReadiness](#EnsureResetReadiness)
- [EnsureRunningForSimulation](#EnsureRunningForSimulation)
- [EnterWeldStatus](#EnterWeldStatus)
- [EstimateRobotVelocityX](#EstimateRobotVelocityX)
- [EstopMachine](#EstopMachine)
- [EvaluateHeartbeatLevel](#EvaluateHeartbeatLevel)
- [EvaluateInitializationResult](#EvaluateInitializationResult)
- [ExecuteTaBreak](#ExecuteTaBreak)
- [ExecuteTaTorque](#ExecuteTaTorque)
- [ExecuteTaZeroPose](#ExecuteTaZeroPose)
- [ExitTaTorque](#ExitTaTorque)
- [Fail](#Fail)
- [FillOutput](#FillOutput)
- [FillResult](#FillResult)
- [FillXlOutput](#FillXlOutput)
- [FindAbortedFlowName](#FindAbortedFlowName)
- [FinishInitialization](#FinishInitialization)
- [FlushSeamBuffer](#FlushSeamBuffer)
- [GalvoHome](#GalvoHome)
- [GetAlarmInfo](#GetAlarmInfo)
- [GetAllSubDeviceStatus](#GetAllSubDeviceStatus)
- [GetEffectiveRobotX](#GetEffectiveRobotX)
- [GetStepName](#GetStepName)
- [GetWeldHeadSkipReason](#GetWeldHeadSkipReason)
- [GetWorkThreadExitSummary](#GetWorkThreadExitSummary)
- [GetWorkThreadSnapshot](#GetWorkThreadSnapshot)
- [GetWorkThreadTimeoutMs](#GetWorkThreadTimeoutMs)
- [HandleFailure](#HandleFailure)
- [HandleRxCommand](#HandleRxCommand)
- [HasFlowStatus](#HasFlowStatus)
- [HasFlowStatusOtherThan](#HasFlowStatusOtherThan)
- [InitializeInternal](#InitializeInternal)
- [InitializeMotionControl](#InitializeMotionControl)
- [InitializeOff](#InitializeOff)
- [InitializeRobotComm](#InitializeRobotComm)
- [IsActionAborted](#IsActionAborted)
- [IsAllServoOn](#IsAllServoOn)
- [IsCommandPreconditionMet](#IsCommandPreconditionMet)
- [IsElapsed](#IsElapsed)
- [IsEmergencyStop](#IsEmergencyStop)
- [IsGalvoWeaveEnabled](#IsGalvoWeaveEnabled)
- [IsInitPreempted](#IsInitPreempted)
- [IsKnownCommand](#IsKnownCommand)
- [IsNoValueOverLimit](#IsNoValueOverLimit)
- [IsNoValueThresholdReached](#IsNoValueThresholdReached)
- [IsRobotReachable](#IsRobotReachable)
- [IsSeamAxisSettled](#IsSeamAxisSettled)
- [IsSubWorkGateOpen](#IsSubWorkGateOpen)
- [IsTimeout](#IsTimeout)
- [IsWeldHeadConfiguredButOffline](#IsWeldHeadConfiguredButOffline)
- [IsWithinYStroke](#IsWithinYStroke)
- [JoinCommWorkThreads](#JoinCommWorkThreads)
- [JoinModuleWorkThreads](#JoinModuleWorkThreads)
- [JoinPendingThread](#JoinPendingThread)
- [JoinThread](#JoinThread)
- [JoinWorkThread](#JoinWorkThread)
- [LaApplySpot](#LaApplySpot)
- [LaMoveTo](#LaMoveTo)
- [LaMoveToPose](#LaMoveToPose)
- [LoadConfig](#LoadConfig)
- [LoadParameters](#LoadParameters)
- [LoadTaAxisConfigForInit](#LoadTaAxisConfigForInit)
- [Log](#Log)
- [LogAction](#LogAction)
- [LogCspBufferDiagnostics](#LogCspBufferDiagnostics)
- [LogCspCorrectionDebug](#LogCspCorrectionDebug)
- [LogCspMotionDebug](#LogCspMotionDebug)
- [LogDriveStopped](#LogDriveStopped)
- [LogHeartbeatEdge](#LogHeartbeatEdge)
- [LogPendingGateOnce](#LogPendingGateOnce)
- [LogSimulationStarted](#LogSimulationStarted)
- [MachineCommandWorkClose](#MachineCommandWorkClose)
- [MachineCommandWorkOpen](#MachineCommandWorkOpen)
- [MachineFlowWorkClose](#MachineFlowWorkClose)
- [MachineFlowWorkOpen](#MachineFlowWorkOpen)
- [MachineIOWorkClose](#MachineIOWorkClose)
- [MachineStatusTrans](#MachineStatusTrans)
- [MapCommandToIo](#MapCommandToIo)
- [MarkConnectFailed](#MarkConnectFailed)
- [MarkTaZeroPoseFailed](#MarkTaZeroPoseFailed)
- [MarkTaZeroPoseRunning](#MarkTaZeroPoseRunning)
- [MarkTaZeroPoseSucceeded](#MarkTaZeroPoseSucceeded)
- [ModeName](#ModeName)

## Log

> 8 处调用 / 8 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3737, 3730, 3678, 3671, 3654, 3650, 3640, 3633, 3629, 3541, 3520, 3462, 3450, 3435, 3427, 3413, 3406, 3395, 3390, 3371, 3358, 3344, 3337, 3326, 3321, 3310, 3266, 3247, 3180, 3152, 3148, 3133, 3122, 3118, 3083, 2897, 2896, 2863, 2858, 2847, 2832, 2789, 2765, 2755, 2735, 2727, 2718, 2717, 2700, 2674, 2670, 2663, 2607, 2605, 2592, 2580, 2566, 2531, 2445, 2435, 2430, 2415, 2410, 2405, 2280, 2270, 2263, 2228, 2220, 2214, 2196, 2102, 2093, 2086, 2072, 2048, 1977, 1897, 1883, 1880, 1861, 1859, 1853, 1844, 1842, 1837, 1833, 1808, 1785, 1778, 1759, 1749, 1747, 1745, 1730, 1715, 1706, 1703, 1700, 1690, 1685, 1657, 1603, 1585, 1579, 1558, 1540, 1537, 1526, 1519, 1446, 1406, 1392, 1386, 1356, 1302, 1235, 1217, 1199, 1194, 1179, 1164, 1154, 1049, 1015, 995, 987, 981, 920, 915, 907, 904, 896, 889, 864, 862, 860, 858, 856, 779, 763, 674, 663, 644, 575]
- `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs` — 行 [387, 234]
- `MainDeviceControl/DeviceStatusWork.cs` — 行 [503, 483, 444, 430, 385, 359, 319, 313, 257, 251, 236, 222, 218, 187]
- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [688, 684, 678, 672, 659, 645, 631, 617, 605, 519, 514, 431, 428, 425, 416, 396, 392, 386, 375, 368, 352, 340, 336, 328, 225, 213, 207, 198]
- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [958, 935, 910, 797, 789, 779, 758, 753, 717, 629, 624, 619, 608, 592, 450, 377, 354, 333, 309, 276, 266, 258, 246, 203, 201, 180, 178, 176, 163, 145]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [741, 731, 722, 711, 694, 628, 616, 420]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [3002, 2999, 2980, 2977, 2973, 2960, 2956, 2952, 2931, 2925, 2919, 2909, 2827, 2814, 2802, 2794, 2784, 2779, 2772, 2752, 2748, 2735, 2730, 2727, 2720, 2715, 2710, 2692, 2691, 2684, 2680, 2671, 2666, 2660, 2656, 2645, 2639, 2604, 2586, 2580, 2572, 2562, 2553, 2547, 2537, 2531, 2526, 2520, 2489, 2484, 2481, 2475, 2472, 2463, 2457, 2443, 2432, 2390, 2386, 2382, 2380, 2342, 2337, 2325, 2322, 2317, 2312, 2307, 2292, 2286, 2270, 2254, 2224, 2003, 1994, 1979, 1966, 1961, 1943, 1932, 1922, 1821, 1752, 1722, 1710, 1698, 1657, 1539, 1515, 1496, 1409, 1390, 1384, 1357, 1350, 1320, 1317, 1175, 1083, 1070, 1042, 1010, 1006, 979, 932, 926, 873, 847, 832, 810, 795, 790, 782, 772, 759, 756, 745, 730, 699, 678, 656, 642, 617, 606, 597, 588, 564, 533]
- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [562, 420, 396, 388, 340, 256]

## AdvanceStep

> 5 处调用 / 5 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [480, 463, 458, 453]
- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [916, 912, 905, 902, 898, 832, 826, 734, 711, 689, 686, 683, 676, 673, 670, 667, 550, 484]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [655, 652, 643, 348, 337, 334, 331]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1215, 1212, 1205, 1202, 1195, 857, 490, 487, 482]
- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [495, 483, 480, 477, 325, 267]

## DoFinishFail

> 4 处调用 / 4 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [689]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [655]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1215]
- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [483]

## Fail

> 4 处调用 / 4 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [473, 290]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [393, 379, 372]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1543, 1119, 1099, 696, 687, 650, 625, 537]
- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [314, 280]

## MarkConnectFailed

> 4 处调用 / 4 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [510, 503]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [801, 793, 710, 701]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1952]
- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [543]

## BeginConnectAttempt

> 3 处调用 / 3 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [848]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [780, 695]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1945]

## DoFinishOk

> 3 处调用 / 3 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [686]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [652]
- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [480]

## LogAction

> 3 处调用 / 3 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [755, 750, 732, 727, 712, 702, 586]
- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [534, 530, 525, 512, 505, 497, 492]
- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [802, 797, 787]

## DoStopping

> 2 处调用 / 2 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [683]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1212]

## EnterWeldStatus

> 2 处调用 / 2 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [795, 703]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2034, 2027, 1986, 1958, 1951, 1944, 1244, 904, 895, 876, 845, 746, 466]

## IsTimeout

> 2 处调用 / 2 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [344, 289, 279]
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [809, 537]

## AdvanceInitNode

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3299, 3291, 3282, 3256, 3236, 3224, 3212]

## AllInitTargetsConnected

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2878]

## AnalyzeImage

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [391]

## ApplyGalvoAmplitude

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [457]

## ApplyLaFollow

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [462, 389]

## ApplyRobotStopPose

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1904, 1023]

## ApplySpotAlignCompensation

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2241]

## AttachSeamTrackAxis

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1957]

## BeginWeldMonitor

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1556]

## BindCamera

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [581, 304]

## BuildInitOrderText

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2897]

## BuildInitPlan

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3187, 2877, 1332]

## BuildMachineInitSummary

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2380]

## BuildTxCodeReverse

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/CommandCore.cs` — 行 [228]

## CalcGalvoAmplitude

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [118, 96]

## CalcGalvoFrequency

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [119, 97]

## CascadeClearStatus

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3446, 3306]

## CascadeDisconnect

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3447]

## CascadeDisconnectWithWait

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2565, 1242]

## CascadeResetProcess

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3363]

## CascadeWeldStatus

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3564, 2103, 2094, 2087, 1632, 1622, 1612, 1555, 1538]

## CheckActionGate

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1547, 1535]

## CheckAutoWeldingConflict

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2876]

## CheckDevice

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [751, 750, 749, 748]

## CheckDeviceStates

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [798]

## CheckLowerBound

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [726, 724]

## CheckPlc

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [791]

## CheckSubWorkPending

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [769]

## CheckTaAvailable

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2769, 2706, 2633, 2599]

## CheckUpperBound

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [730, 728]

## CheckWeldProgress

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [766]

## ClampToStroke

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1810, 1455]

## ClearAllVirtualIo

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2535]

## ClearMachine

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3353]

## ClearRobotCommand

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3574, 3475]

## ClearStatus

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [472]

## CloseRobotChannel

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2572]

## CommWork

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1433]

## ComposeWireFeedSpeed

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2182]

## ConfigureSoftTargetReachWindow

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [693]

## ConnectWorker

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [851]

## CorrectIllegalCombination

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2078]

## CspTick

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1031]

## DequeueCommand

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [876]

## DetachSeamTrackAxis

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1982]

## DetectCspExecutionStall

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1477]

## DisableSimulation

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1748, 1705]

## DisconnectChild

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1214]

## DisconnectWorker

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [872]

## DispatchAction

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [223]

## DisposeComponents

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3779]

## DisposeFrame

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [529, 522, 515]

## DisposeManaged

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs` — 行 [194]

## DoAcquireTrigger

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [643]

## DoAcquireWait

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [646]

## DoAnalyze

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [649]

## DoClearAlarm

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2509, 1999]

## DoCompute

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [474]

## DoEstopMachine

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3494]

## DoInitializeMachine

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1983]

## DoMotionBusFault

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2003]

## DoOutput

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [477]

## DoPreWork

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [667]

## DoPreWorkOn

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [670]

## DoPreWorkStable

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [673]

## DoPreWorkWaitWork

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [676]

## DoResetMachine

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1987]

## DoReturnToCalibration

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1205]

## DoServoOn

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1202]

## DoStartMachine

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2510, 1991]

## DoStopMachine

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1995]

## DoSubAlarmStop

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2023]

## DoSubManualStop

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2019]

## DoSubPrework

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2007, 1777]

## DoSubStop

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2015, 1702]

## DoSubWork

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2011, 1784, 1594]

## DoWorking

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [680]

## DriveTricolorLamp

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [379]

## EmergencyStop

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3503]

## EnableAxesAfterInit

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3124]

## EndInitWithoutChain

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2880, 2874, 2869]

## EndProductSessionSafely

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3670, 1746, 1633, 1623, 1613]

## EndWeldMonitor

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1630, 1620, 1610]

## EnqueueSeamPoints

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1109, 975]

## EnsureCommandWorkStarted

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3183, 3159, 2846]

## EnsureConnected

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [788, 696, 358]

## EnsureHeartbeatThread

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1125]

## EnsureManualWeldHeadActionAllowed

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [764, 723, 698, 655, 641, 627, 613, 594]

## EnsureResetReadiness

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1240]

## EnsureRunningForSimulation

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3604]

## EstimateRobotVelocityX

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1460]

## EstopMachine

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [945]

## EvaluateHeartbeatLevel

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [813]

## EvaluateInitializationResult

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3112]

## ExecuteTaBreak

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2883]

## ExecuteTaTorque

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2881]

## ExecuteTaZeroPose

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [3003, 2958, 2900, 2889]

## ExitTaTorque

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2796, 2600]

## FillOutput

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [409, 294, 143]

## FillResult

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` — 行 [450]

## FillXlOutput

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [153]

## FindAbortedFlowName

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2068]

## FinishInitialization

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3190]

## FlushSeamBuffer

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1132, 1087, 940, 818]

## GalvoHome

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [765]

## GetAlarmInfo

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2377]

## GetAllSubDeviceStatus

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2369, 2120, 2110, 2038, 984]

## GetEffectiveRobotX

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1728, 1701, 1696, 1675, 1645]

## GetStepName

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs` — 行 [137, 129]

## GetWeldHeadSkipReason

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2922]

## GetWorkThreadExitSummary

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2579]

## GetWorkThreadSnapshot

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2718, 2371]

## GetWorkThreadTimeoutMs

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2781]

## HandleFailure

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [345, 280]

## HandleRxCommand

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1095]

## HasFlowStatus

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2099, 2084]

## HasFlowStatusOtherThan

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2091]

## InitializeInternal

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [754, 493]

## InitializeMotionControl

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2990]

## InitializeOff

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [3260]

## InitializeRobotComm

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2984]

## IsActionAborted

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3418, 3364, 3354]

## IsAllServoOn

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [525]

## IsCommandPreconditionMet

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [912]

## IsElapsed

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1918, 1783]

## IsEmergencyStop

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1405]

## IsGalvoWeaveEnabled

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [253]

## IsInitPreempted

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3176]

## IsKnownCommand

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/CommandCore.cs` — 行 [116, 103]

## IsNoValueOverLimit

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [834]

## IsNoValueThresholdReached

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1429]

## IsRobotReachable

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3341, 1339]

## IsSeamAxisSettled

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [835, 734]

## IsSubWorkGateOpen

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1772, 1588, 1548]

## IsWeldHeadConfiguredButOffline

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2923]

## IsWithinYStroke

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [685, 685]

## JoinCommWorkThreads

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2743, 2710]

## JoinModuleWorkThreads

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3513, 3445, 2689, 2541]

## JoinPendingThread

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 [943, 942]

## JoinThread

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [495, 494, 493, 492]

## JoinWorkThread

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2764, 2763, 2754, 2753, 2752, 2751, 2750]

## LaApplySpot

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [634, 620, 598]

## LaMoveTo

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [687, 423, 384, 355]

## LaMoveToPose

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 [662, 648]

## LoadConfig

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [80]

## LoadParameters

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` — 行 [539, 513, 450]

## LoadTaAxisConfigForInit

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3123]

## LogCspBufferDiagnostics

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1505]

## LogCspCorrectionDebug

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1820, 1508]

## LogCspMotionDebug

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [1509]

## LogDriveStopped

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [753]

## LogHeartbeatEdge

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [817]

## LogPendingGateOnce

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [1774, 1590, 1551]

## LogSimulationStarted

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3613]

## MachineCommandWorkClose

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [2547]

## MachineCommandWorkOpen

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3424, 3165]

## MachineFlowWorkClose

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3512, 3443, 2540]

## MachineFlowWorkOpen

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3423, 3182, 3111, 2845]

## MachineIOWorkClose

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStatusWork.cs` — 行 [524]

## MachineStatusTrans

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [3411, 3388, 3356, 634]

## MapCommandToIo

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceControlWork.cs` — 行 [885]

## MarkTaZeroPoseFailed

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2838, 2833, 2807]

## MarkTaZeroPoseRunning

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2843, 2791]

## MarkTaZeroPoseSucceeded

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 [2826, 2813]

## ModeName

> 1 处调用 / 1 个调用方文件

- `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs` — 行 [234, 225]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
