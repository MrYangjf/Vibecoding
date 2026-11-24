---
title: CodeMap-Symbols-MainDeviceControl — 代码地图·符号签名层·MainDeviceControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-MainDeviceControl — MainDeviceControl 的类型与签名

> **一句话**：模块 `MainDeviceControl` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> 整机编排：设备初始化 / 状态机 / 五个模组 workflow
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.MainDeviceControl.DeviceWorkflow` | 5 | 6 | 主控 · 五个模组工作流 | [[modules/DeviceControl]] | ADR-016/038/041/044 |
| `AdaWeldSystem.MainDeviceControl.DeviceStateApiCore` | 4 | 7 | 主控 · 三态契约与命令常量 | [[modules/DeviceControl]] | ADR-013/038 |
| `AdaWeldSystem.MainDeviceControl` | 3 | 12 | 主控层 · 整机编排 | [[modules/DeviceControl]] | ADR-013/014/017/038/041 |

| 项 | 值 |
|---|---|
| 类型数 | 25 |
| 方法数 | 751 |

## 章节导航

- [CommandCore](#CommandCore)
- [DeviceControlWork](#DeviceControlWork)
- [DeviceInitOutcomeItem](#DeviceInitOutcomeItem)
- [DeviceInitSummaryEventArgs](#DeviceInitSummaryEventArgs)
- [DeviceStateBase](#DeviceStateBase)
- [DeviceStatusWork](#DeviceStatusWork)
- [DeviceWorkflowBase](#DeviceWorkflowBase)
- [InitNode](#InitNode)
- [LaserWeldHeadWorkflow](#LaserWeldHeadWorkflow)
- [LineLaserWorkflow](#LineLaserWorkflow)
- [MachineAlarmInfo](#MachineAlarmInfo)
- [MachineStatusSnapshot](#MachineStatusSnapshot)
- [MainDeviceStatusChangedEventArgs](#MainDeviceStatusChangedEventArgs)
- [MonitorCameraWorkflow](#MonitorCameraWorkflow)
- [MonitorResult](#MonitorResult)
- [MotionControlWorkflow](#MotionControlWorkflow)
- [SafetyFlow](#SafetyFlow)
- [SafetyInterlockChecker](#SafetyInterlockChecker)
- [SafetyInterlockResult](#SafetyInterlockResult)
- [SimulationConfig](#SimulationConfig)
- [SimulationStoppedEventArgs](#SimulationStoppedEventArgs)
- [SubDeviceStateChangedEventArgs](#SubDeviceStateChangedEventArgs)
- [WeldParamControlWorkflow](#WeldParamControlWorkflow)
- [WeldStatusChangedEventArgs](#WeldStatusChangedEventArgs)
- [WorkThreadEntry](#WorkThreadEntry)

## CommandCore

- 签名：`public static class CommandCore`
- 位置：`MainDeviceControl/DeviceStateApiCore/CommandCore.cs:7`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`
- 方法（10）：
  - `string Normalize(string raw)` — `MainDeviceControl/DeviceStateApiCore/CommandCore.cs:86`
  - `bool TrySplitPayload(string normalized, string command, string payload)` — `MainDeviceControl/DeviceStateApiCore/CommandCore.cs:98`
  - `bool IsKnownCommand(string raw)` — `MainDeviceControl/DeviceStateApiCore/CommandCore.cs:125`
  - `string TranslateCommand(string command)` — `MainDeviceControl/DeviceStateApiCore/CommandCore.cs:182`
  - `void BuildTxCodeReverse()` — `MainDeviceControl/DeviceStateApiCore/CommandCore.cs:233`
  - `string RxCodeToCommandName(int rxCode)` — `MainDeviceControl/DeviceStateApiCore/CommandCore.cs:246`
  - `string TxCodeToCommandName(int txCode)` — `MainDeviceControl/DeviceStateApiCore/CommandCore.cs:254`
  - `int CommandToTxCodeValue(string command)` — `MainDeviceControl/DeviceStateApiCore/CommandCore.cs:262`
  - `string DescribeRxCode(int rxCode)` — `MainDeviceControl/DeviceStateApiCore/CommandCore.cs:272`
  - `string DescribeTxCode(int txCode)` — `MainDeviceControl/DeviceStateApiCore/CommandCore.cs:283`

## DeviceControlWork

- 签名：`public class DeviceControlWork : IDisposable`
- 位置：`MainDeviceControl/DeviceControlWork.cs:136`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 方法（160）：
  - `void Log(string message, MessageLevel level)` — `MainDeviceControl/DeviceControlWork.cs:597`
  - `void MachineStatusTrans(MainDeviceStatus target)` — `MainDeviceControl/DeviceControlWork.cs:606`
  - `void SetStatus(MainDeviceStatus newStatus, string reason)` — `MainDeviceControl/DeviceControlWork.cs:626`
  - `void WeldStatusTrans()` — `MainDeviceControl/DeviceControlWork.cs:667`
  - `void NewWorkThread(ThreadStart body, string name)` — `MainDeviceControl/DeviceControlWork.cs:684`
  - `void RegisterWorkThread(Thread thread, int timeoutMs)` — `MainDeviceControl/DeviceControlWork.cs:700`
  - `string GetWorkThreadSnapshot()` — `MainDeviceControl/DeviceControlWork.cs:720`
  - `void SubDeviceWork(DeviceWorkflowBase flow, string name)` — `MainDeviceControl/DeviceControlWork.cs:743`
  - `void LogDriveStopped()` — `MainDeviceControl/DeviceControlWork.cs:776`
  - `void LaserHeadWork()` — `MainDeviceControl/DeviceControlWork.cs:783`
  - `void LineLaserWork()` — `MainDeviceControl/DeviceControlWork.cs:786`
  - `void MonitorCamWork()` — `MainDeviceControl/DeviceControlWork.cs:789`
  - `void MotionControlWork()` — `MainDeviceControl/DeviceControlWork.cs:792`
  - `void WeldParamControlWork()` — `MainDeviceControl/DeviceControlWork.cs:795`
  - `void HeartInspectWork()` — `MainDeviceControl/DeviceControlWork.cs:798`
  - `void EvaluateHeartbeatLevel(CommunicationManager comm)` — `MainDeviceControl/DeviceControlWork.cs:827`
  - `void IsNoValueOverLimit()` — `MainDeviceControl/DeviceControlWork.cs:841`
  - `void LogHeartbeatEdge(RobotHeartbeatLevel from, RobotHeartbeatLevel to, bool needHeartbeat)` — `MainDeviceControl/DeviceControlWork.cs:852`
  - `void CommCommandWork()` — `MainDeviceControl/DeviceControlWork.cs:868`
  - `void DequeueCommand()` — `MainDeviceControl/DeviceControlWork.cs:927`
  - `void MapCommandToIo(string command)` — `MainDeviceControl/DeviceControlWork.cs:939`
  - `void IsCommandPreconditionMet(string command, string ioName)` — `MainDeviceControl/DeviceControlWork.cs:975`
  - `void OnCommRecived(object sender, string message)` — `MainDeviceControl/DeviceControlWork.cs:1004`
  - `void ApplyRobotStopPose(double stopX)` — `MainDeviceControl/DeviceControlWork.cs:1032`
  - `void TryParseFirstDouble(string payload, double value)` — `MainDeviceControl/DeviceControlWork.cs:1056`
  - `void OnRobotDataReceived(object sender, KUKADataReceivedEventArgs e)` — `MainDeviceControl/DeviceControlWork.cs:1078`
  - `void CommWork()` — `MainDeviceControl/DeviceControlWork.cs:1101`
  - `void SendRobotCommand(string command)` — `MainDeviceControl/DeviceControlWork.cs:1143`
  - `void ClearRobotCommand()` — `MainDeviceControl/DeviceControlWork.cs:1169`
  - `void DisconnectChild(DeviceWorkflowBase child, string name)` — `MainDeviceControl/DeviceControlWork.cs:1187`
  - `void CascadeDisconnectWithWait()` — `MainDeviceControl/DeviceControlWork.cs:1207`
  - `void WaitChildDisconnected(DeviceWorkflowBase child, string name)` — `MainDeviceControl/DeviceControlWork.cs:1226`
  - `void CascadeDisconnect()` — `MainDeviceControl/DeviceControlWork.cs:1240`
  - `void EvaluateInitializationResult()` — `MainDeviceControl/DeviceControlWork.cs:1248`
  - `void EnableAxesAfterInit()` — `MainDeviceControl/DeviceControlWork.cs:1290`
  - `void IsRobotReachable()` — `MainDeviceControl/DeviceControlWork.cs:1309`
  - `void AllInitTargetsConnected()` — `MainDeviceControl/DeviceControlWork.cs:1330`
  - `void IsActionAborted(MainDeviceStatus expected, string action)` — `MainDeviceControl/DeviceControlWork.cs:1352`
  - `void IsInitPreempted()` — `MainDeviceControl/DeviceControlWork.cs:1362`
  - `void CascadeResetProcess()` — `MainDeviceControl/DeviceControlWork.cs:1371`
  - `void CascadeClearStatus()` — `MainDeviceControl/DeviceControlWork.cs:1399`
  - `void InitializeMotionControl()` — `MainDeviceControl/DeviceControlWork.cs:1411`
  - `void InitializeRobotComm()` — `MainDeviceControl/DeviceControlWork.cs:1431`
  - `void OnSimLineLaserStateChanged(object sender, SubDeviceStateChangedEventArgs e)` — `MainDeviceControl/DeviceControlWork.cs:1439`
  - `void SimTestWorkOpen()` — `MainDeviceControl/DeviceControlWork.cs:1450`
  - `void SimTestWorkClose()` — `MainDeviceControl/DeviceControlWork.cs:1459`
  - `void SimTestWork()` — `MainDeviceControl/DeviceControlWork.cs:1476`
  - `void SimTick()` — `MainDeviceControl/DeviceControlWork.cs:1494`
  - `void CheckActionGate(string action, ReadinessStage required, DeviceWorkflowBase flow, string reason)` — `MainDeviceControl/DeviceControlWork.cs:1513`
  - `void DoSubPrework()` — `MainDeviceControl/DeviceControlWork.cs:1533`
  - `void DoSubWork()` — `MainDeviceControl/DeviceControlWork.cs:1544`
  - `void IsSubWorkGateOpen()` — `MainDeviceControl/DeviceControlWork.cs:1564`
  - `void CheckSubWorkPending()` — `MainDeviceControl/DeviceControlWork.cs:1570`
  - `void LogPendingGateOnce()` — `MainDeviceControl/DeviceControlWork.cs:1599`
  - `void DoSubStop()` — `MainDeviceControl/DeviceControlWork.cs:1607`
  - `void DoSubManualStop()` — `MainDeviceControl/DeviceControlWork.cs:1617`
  - `void DoSubAlarmStop()` — `MainDeviceControl/DeviceControlWork.cs:1627`
  - `void BeginWeldMonitor()` — `MainDeviceControl/DeviceControlWork.cs:1637`
  - `void EndWeldMonitor()` — `MainDeviceControl/DeviceControlWork.cs:1665`
  - `void CheckWeldProgress()` — `MainDeviceControl/DeviceControlWork.cs:1671`
  - `void EndProductSessionSafely(string result, string info)` — `MainDeviceControl/DeviceControlWork.cs:1712`
  - `void OnLineLaserJobChanged(object sender, int jobId)` — `MainDeviceControl/DeviceControlWork.cs:1722`
  - `void SimScheduleTick()` — `MainDeviceControl/DeviceControlWork.cs:1734`
  - `void CascadeWeldStatus(SubDeviceWeldStatus target, string reason)` — `MainDeviceControl/DeviceControlWork.cs:1801`
  - `void PrepareSimulationMonitorCam()` — `MainDeviceControl/DeviceControlWork.cs:1815`
  - `void SimMonitorCamStartWeld()` — `MainDeviceControl/DeviceControlWork.cs:1848`
  - `void SimMonitorCamStopWeld()` — `MainDeviceControl/DeviceControlWork.cs:1865`
  - `void HandleRxCommand(int rxCmd, double rxPayload)` — `MainDeviceControl/DeviceControlWork.cs:1892`
  - `void SetVirtualIo(string ioName)` — `MainDeviceControl/DeviceControlWork.cs:1917`
  - `void ClearVirtualIo(string ioName)` — `MainDeviceControl/DeviceControlWork.cs:1925`
  - `bool IsVirtualIoSet(string ioName)` — `MainDeviceControl/DeviceControlWork.cs:1935`
  - `bool TakeVirtualIo(string ioName)` — `MainDeviceControl/DeviceControlWork.cs:1945`
  - `void ClearAllVirtualIo()` — `MainDeviceControl/DeviceControlWork.cs:1952`
  - `string[] SnapshotVirtualIo()` — `MainDeviceControl/DeviceControlWork.cs:1959`
  - `bool ExecuteIo(string ioName)` — `MainDeviceControl/DeviceControlWork.cs:1973`
  - `void CheckPreworkFailed()` — `MainDeviceControl/DeviceControlWork.cs:2032`
  - `void ConsistencyTick()` — `MainDeviceControl/DeviceControlWork.cs:2057`
  - `void CorrectIllegalCombination()` — `MainDeviceControl/DeviceControlWork.cs:2082`
  - `void HasFlowStatus(SubDeviceWeldStatus target)` — `MainDeviceControl/DeviceControlWork.cs:2108`
  - `void HasFlowStatusOtherThan(SubDeviceWeldStatus target)` — `MainDeviceControl/DeviceControlWork.cs:2118`
  - `void FindAbortedFlowName()` — `MainDeviceControl/DeviceControlWork.cs:2128`
  - `void SendCutWireRequest(bool on)` — `MainDeviceControl/DeviceControlWork.cs:2176`
  - `void MonitorAlignTick()` — `MainDeviceControl/DeviceControlWork.cs:2187`
  - `double ComposeWireFeedSpeed(double algoFeedSpeed)` — `MainDeviceControl/DeviceControlWork.cs:2293`
  - `void ApplySpotAlignCompensation()` — `MainDeviceControl/DeviceControlWork.cs:2300`
  - ` GetMainDeviceStatus()` — `MainDeviceControl/DeviceControlWork.cs:2320`
  - ` GetSubDeviceStatus(string tag)` — `MainDeviceControl/DeviceControlWork.cs:2328`
  - `Dictionary<string, SubDeviceWeldStatus> GetAllSubDeviceStatus()` — `MainDeviceControl/DeviceControlWork.cs:2342`
  - ` GetAlarmInfo()` — `MainDeviceControl/DeviceControlWork.cs:2356`
  - ` GetStatusSnapshot()` — `MainDeviceControl/DeviceControlWork.cs:2363`
  - `string[] GetIOState()` — `MainDeviceControl/DeviceControlWork.cs:2384`
  - ` GetWeldParam()` — `MainDeviceControl/DeviceControlWork.cs:2391`
  - `bool SetWeldParam(WeldParamAdaptControl param)` — `MainDeviceControl/DeviceControlWork.cs:2400`
  - `bool SetRobotCoord(double offsetX, double offsetY, double offsetZ)` — `MainDeviceControl/DeviceControlWork.cs:2426`
  - `void GetRobotCoord(double offsetX, double offsetY, double offsetZ)` — `MainDeviceControl/DeviceControlWork.cs:2453`
  - `void WaitChildConnectedTick(DeviceStateBase child)` — `MainDeviceControl/DeviceControlWork.cs:2469`
  - `void AdvanceInitNode()` — `MainDeviceControl/DeviceControlWork.cs:2476`
  - `void PrepareSimulationCamera()` — `MainDeviceControl/DeviceControlWork.cs:2484`
  - `void SuspendRealHardwareForSimulation()` — `MainDeviceControl/DeviceControlWork.cs:2497`
  - `void EnsureRunningForSimulation()` — `MainDeviceControl/DeviceControlWork.cs:2506`
  - `void LogSimulationStarted()` — `MainDeviceControl/DeviceControlWork.cs:2514`
  - `void DisposeComponents()` — `MainDeviceControl/DeviceControlWork.cs:2524`
  - `void ShutdownBudgetExceeded(Stopwatch watch, string step)` — `MainDeviceControl/DeviceControlWork.cs:2589`
  - `void CloseRobotChannel()` — `MainDeviceControl/DeviceControlWork.cs:2598`
  - `void GetWorkThreadExitSummary(int exited, int total)` — `MainDeviceControl/DeviceControlWork.cs:2614`
  - `void LoadTaAxisConfigForInit()` — `MainDeviceControl/DeviceControlWork.cs:2658`
  - `void MachineFlowWorkOpen()` — `MainDeviceControl/DeviceControlWork.cs:2680`
  - `void MachineCommandWorkOpen()` — `MainDeviceControl/DeviceControlWork.cs:2704`
  - `void EnsureHeartbeatThread()` — `MainDeviceControl/DeviceControlWork.cs:2722`
  - `void MachineFlowWorkClose()` — `MainDeviceControl/DeviceControlWork.cs:2731`
  - `void MachineCommandWorkClose()` — `MainDeviceControl/DeviceControlWork.cs:2739`
  - `void JoinModuleWorkThreads()` — `MainDeviceControl/DeviceControlWork.cs:2747`
  - `void JoinCommWorkThreads()` — `MainDeviceControl/DeviceControlWork.cs:2760`
  - `void JoinWorkThread(Thread thread, string name)` — `MainDeviceControl/DeviceControlWork.cs:2773`
  - `void GetWorkThreadTimeoutMs(string name)` — `MainDeviceControl/DeviceControlWork.cs:2796`
  - `void SetWorkThreadState(string name, bool exited, bool timedOut)` — `MainDeviceControl/DeviceControlWork.cs:2810`
  - `bool InitializeMachine()` — `MainDeviceControl/DeviceControlWork.cs:2823`
  - `void EndInitWithoutChain(string message, MessageLevel level)` — `MainDeviceControl/DeviceControlWork.cs:2840`
  - `bool DoInitializeMachine()` — `MainDeviceControl/DeviceControlWork.cs:2853`
  - `void BuildInitPlan()` — `MainDeviceControl/DeviceControlWork.cs:2904`
  - `void GetWeldHeadSkipReason()` — `MainDeviceControl/DeviceControlWork.cs:2941`
  - `void IsWeldHeadConfiguredButOffline()` — `MainDeviceControl/DeviceControlWork.cs:2953`
  - `void BuildInitOrderText()` — `MainDeviceControl/DeviceControlWork.cs:2963`
  - `void StartRobotCommNode()` — `MainDeviceControl/DeviceControlWork.cs:2982`
  - `void StartMotionNode()` — `MainDeviceControl/DeviceControlWork.cs:2988`
  - `void StartWeldHeadNode()` — `MainDeviceControl/DeviceControlWork.cs:2998`
  - `void StartLineLaserNode()` — `MainDeviceControl/DeviceControlWork.cs:3022`
  - `void StartMonitorCamNode()` — `MainDeviceControl/DeviceControlWork.cs:3039`
  - `void RecordInitOutcome(InitNode node, DeviceInitOutcome outcome, string blockedBy, string reason)` — `MainDeviceControl/DeviceControlWork.cs:3060`
  - `void RaiseInitSummary()` — `MainDeviceControl/DeviceControlWork.cs:3087`
  - `void FinishInitialization()` — `MainDeviceControl/DeviceControlWork.cs:3106`
  - `void EnsureCommandWorkStarted()` — `MainDeviceControl/DeviceControlWork.cs:3163`
  - `void InitializeMachineTick()` — `MainDeviceControl/DeviceControlWork.cs:3171`
  - `void ClearMachine()` — `MainDeviceControl/DeviceControlWork.cs:3303`
  - `bool ResetMachine()` — `MainDeviceControl/DeviceControlWork.cs:3316`
  - `bool DoResetMachine()` — `MainDeviceControl/DeviceControlWork.cs:3333`
  - `bool StartMachine()` — `MainDeviceControl/DeviceControlWork.cs:3384`
  - `bool DoStartMachine()` — `MainDeviceControl/DeviceControlWork.cs:3402`
  - `void StopMachine()` — `MainDeviceControl/DeviceControlWork.cs:3432`
  - `void DoStopMachine()` — `MainDeviceControl/DeviceControlWork.cs:3439`
  - `bool ClearAlarm()` — `MainDeviceControl/DeviceControlWork.cs:3456`
  - `bool DoClearAlarm()` — `MainDeviceControl/DeviceControlWork.cs:3469`
  - `void DoMotionBusFault()` — `MainDeviceControl/DeviceControlWork.cs:3481`
  - `void EstopMachine(string reason)` — `MainDeviceControl/DeviceControlWork.cs:3491`
  - `void DoEstopMachine()` — `MainDeviceControl/DeviceControlWork.cs:3498`
  - `void EstopCancel()` — `MainDeviceControl/DeviceControlWork.cs:3524`
  - `void EmergencyStop()` — `MainDeviceControl/DeviceControlWork.cs:3532`
  - `void ReportAlarm(string reason)` — `MainDeviceControl/DeviceControlWork.cs:3547`
  - `void ReportAlarmCleared()` — `MainDeviceControl/DeviceControlWork.cs:3568`
  - `void StartSimulation()` — `MainDeviceControl/DeviceControlWork.cs:3582`
  - `void DisableSimulation(= "用户手动停止", = false, = false)` — `MainDeviceControl/DeviceControlWork.cs:3621`
  - `void StartRobotXSimulation()` — `MainDeviceControl/DeviceControlWork.cs:3684`
  - `void StopRobotXSimulation()` — `MainDeviceControl/DeviceControlWork.cs:3704`
  - `void StartSimulationLineLaser()` — `MainDeviceControl/DeviceControlWork.cs:3713`
  - `void StopSimulationLineLaser()` — `MainDeviceControl/DeviceControlWork.cs:3727`
  - `void ResetSimulationLineLaser()` — `MainDeviceControl/DeviceControlWork.cs:3734`
  - `double GetEffectiveRobotX()` — `MainDeviceControl/DeviceControlWork.cs:3743`
  - `void LoadSimulation()` — `MainDeviceControl/DeviceControlWork.cs:3751`
  - `void SaveSimulation()` — `MainDeviceControl/DeviceControlWork.cs:3764`
  - `void Dispose()` — `MainDeviceControl/DeviceControlWork.cs:3777`
- 构造（1）：
  - `DeviceControlWork()` — `MainDeviceControl/DeviceControlWork.cs:567`
- 属性（21）：
  - `double CascadeConnectTimeoutMs { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:159`
  - `MontionManager Motion { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:321`
  - `DeviceControlWork Instance { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:453`
  - `MonitorResult AlignDatum { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:456`
  - `MainDeviceStatus Status { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:462`
  - `IList<DeviceInitOutcomeItem> LastInitOutcomes { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:477`
  - `bool IsWelding { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:489`
  - `bool IsAutoWeldingRunning { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:495`
  - `bool IsAlarmstop { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:508`
  - `bool IsRobotOnline { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:515`
  - `RobotHeartbeatLevel HeartbeatLevel { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:518`
  - `bool IsSimulationEnabled { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:523`
  - `string CurrentProductSn { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:529`
  - `bool ShouldUseVirtualCamera { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:536`
  - `bool ShouldMoveAxis { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:547`
  - `int SimLaserFrequencyHz { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:557`
  - `MainDeviceStatus Current { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:583`
  - `MainDeviceStatus Last { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:589`
  - `bool IsInitializing { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:1316`
  - `bool IsShuttingDown { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:1322`
  - `double WireFeedCompensation { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:2171`

## DeviceInitOutcomeItem

- 签名：`public sealed class DeviceInitOutcomeItem`
- 位置：`MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs:20`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`
- 属性（5）：
  - `string Key { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs:23`
  - `string DisplayName { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs:26`
  - `DeviceInitOutcome Outcome { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs:29`
  - `string BlockedBy { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs:32`
  - `string Reason { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs:35`

## DeviceInitSummaryEventArgs

- 签名：`public sealed class DeviceInitSummaryEventArgs : EventArgs`
- 位置：`MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs:39`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`
- 属性（4）：
  - `int SuccessCount { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs:42`
  - `int FailedCount { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs:45`
  - `int SkippedCount { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs:48`
  - `IList<DeviceInitOutcomeItem> Items { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs:51`

## DeviceStateBase

- 签名：`public abstract class DeviceStateBase`
- 位置：`MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:75`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`
- 方法（9）：
  - `void SetState(SubDeviceState newState, string reason)` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:162`
  - `void BeginConnectAttempt()` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:171`
  - `void MarkConnectFailed(string reason)` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:183`
  - `void SetWeldStatus(SubDeviceWeldStatus newStatus, string reason)` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:194`
  - `void EmergencyStop()` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:201`
  - `void SettleConnect(string result)` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:213`
  - `void CheckDeviceIOSafe()` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:224`
  - `void OnStateSwitched(SubDeviceState oldState, SubDeviceState newState)` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:232`
  - `void OnWeldStatusChanged(SubDeviceWeldStatus oldStatus, SubDeviceWeldStatus newStatus)` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:247`
- 属性（6）：
  - `SubDeviceState State { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:92`
  - `SubDeviceWeldStatus WeldStatus { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:105`
  - `bool IsAlarm { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:118`
  - `bool ConnectSettled { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:142`
  - `string ConnectResult { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:148`
  - `string StateName { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:154`

## DeviceStatusWork

- 签名：`public class DeviceStatusWork`
- 位置：`MainDeviceControl/DeviceStatusWork.cs:16`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 方法（16）：
  - `void Log(string message, MessageLevel level)` — `MainDeviceControl/DeviceStatusWork.cs:120`
  - `void IOWork()` — `MainDeviceControl/DeviceStatusWork.cs:126`
  - `void ReadPhysicalEmg()` — `MainDeviceControl/DeviceStatusWork.cs:197`
  - `void ScanPulseIo(string ioName, bool requireRunning)` — `MainDeviceControl/DeviceStatusWork.cs:211`
  - `void DispatchAction(string ioName)` — `MainDeviceControl/DeviceStatusWork.cs:230`
  - `void ScanRunningIo()` — `MainDeviceControl/DeviceStatusWork.cs:271`
  - `void ScanMotionBusFault()` — `MainDeviceControl/DeviceStatusWork.cs:287`
  - `void EMGWork()` — `MainDeviceControl/DeviceStatusWork.cs:326`
  - `void LightStatusWork()` — `MainDeviceControl/DeviceStatusWork.cs:367`
  - `void DriveTricolorLamp(MainDeviceStatus status)` — `MainDeviceControl/DeviceStatusWork.cs:394`
  - `void JoinThread(Thread thread, string name, int timeoutMs)` — `MainDeviceControl/DeviceStatusWork.cs:440`
  - `void MachineIOWorkOpen()` — `MainDeviceControl/DeviceStatusWork.cs:453`
  - `void MachineIOWorkClose()` — `MainDeviceControl/DeviceStatusWork.cs:487`
  - ` Check()` — `MainDeviceControl/DeviceStatusWork.cs:508`
  - `void Reset()` — `MainDeviceControl/DeviceStatusWork.cs:516`
  - `void Dispose()` — `MainDeviceControl/DeviceStatusWork.cs:522`
- 构造（1）：
  - `DeviceStatusWork()` — `MainDeviceControl/DeviceStatusWork.cs:108`
- 属性（8）：
  - `DeviceStatusWork Instance { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:70`
  - `bool IsRunning { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:73`
  - `bool IsIOWorking { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:76`
  - `bool IsEMGWorking { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:79`
  - `bool IsLightStatusWorking { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:82`
  - `SafetyInterlockResult LastResult { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:85`
  - `SafetyFlow Config { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:92`
  - `bool IsSafe { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:95`

## DeviceWorkflowBase

- 签名：`public abstract class DeviceWorkflowBase : DeviceStateBase, IDisposable`
- 位置：`MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:42`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`
- 方法（29）：
  - `void DisposeManaged()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:177`
  - `void Dispose()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:190`
  - `void RequestWeldStatus(SubDeviceWeldStatus target, string reason)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:202`
  - `void SetRunMode(WorkflowRunMode mode)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:209`
  - `string ModeName(WorkflowRunMode mode)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:217`
  - `void LogAction(WorkflowRunMode mode, string action, MessageLevel level)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:232`
  - `void AdvanceStep(int step)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:240`
  - `void ResetStepTime()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:247`
  - `void IsStepTimeout()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:254`
  - `void Log(string message, MessageLevel level)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:262`
  - `void SetWorkTimeStart()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:271`
  - `void ReadInt(string elementName, int defaultValue)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:281`
  - `void ReadDouble(string elementName, double defaultValue)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:291`
  - `string ReadinessName(ReadinessStage stage)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:348`
  - `bool IsReadinessAtLeast(ReadinessStage required)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:364`
  - `bool EnsureReadiness(ReadinessStage required, string action, string reason)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:374`
  - `void FlowProcess()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:395`
  - `bool ResetProcess()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:399`
  - `void ClearStatus()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:402`
  - `void ResetWorkTime()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:405`
  - `bool InitializeOn()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:409`
  - `bool InitializeOff()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:413`
  - `void SubDeviceLog()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:416`
  - `void LoadConfig()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:419`
  - `void SaveConfig()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:422`
  - `void WeldStatusTrans()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:425`
  - `bool ConnectOn()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:433`
  - `bool ConnectOff()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:437`
  - `void GetStepName(int step)` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:446`
- 构造（1）：
  - `DeviceWorkflowBase()` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:165`
- 属性（26）：
  - `string Tag { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:84`
  - `bool IsEnable { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:87`
  - `WorkflowRunMode RunMode { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:94`
  - `int RunStep { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:100`
  - `TimeSpan StepWorkTime { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:107`
  - `int TimeOutSeconds { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:113`
  - `double StepElapsedMs { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:120`
  - `DateTime WorkTime { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:123`
  - `double WorkElapsedMs { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:126`
  - `string WorkStepName { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:129`
  - `string StepStatusText { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:132`
  - `string ConfigFileName { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:142`
  - `string ConfigModule { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:145`
  - `XdocumentReaderWriter Config { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:148`
  - `string LastActionMessage { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:184`
  - `string ModeText { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:223`
  - `bool IsConnected { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:302`
  - `bool IsEnabled { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:308`
  - `bool IsHomed { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:311`
  - `bool IsAtWorkZero { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:314`
  - `bool NeedHoming { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:317`
  - `bool HasAbsoluteEncoder { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:320`
  - `string WorkZeroSource { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:323`
  - `ReadinessStage MinReadinessStage { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:326`
  - `string ReadinessReason { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:329`
  - `ReadinessStage ReadinessStage { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs:332`

## InitNode

- 签名：`private sealed class InitNode`
- 位置：`MainDeviceControl/DeviceControlWork.cs:382`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 成员：（无）

## LaserWeldHeadWorkflow

- 签名：`public class LaserWeldHeadWorkflow : DeviceWorkflowBase`
- 位置：`MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:13`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
- 方法（37）：
  - `void OnAxisReadinessChanged(string axisName)` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:154`
  - `void SubscribeWeldHeadEvents()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:173`
  - `void UnsubscribeWeldHeadEvents()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:182`
  - `void OnWeldHeadTemperatureAlarm(object sender, LaserHeadTemperatureData data)` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:194`
  - `void OnWeldHeadAlarmTriggered(object sender, HeadAlarmStatus status)` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:221`
  - `void DisposeManaged()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:232`
  - `void ApplyGalvoAmplitude()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:241`
  - ` ResolveGalvoPattern(int configValue)` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:300`
  - `bool IsGalvoWeaveEnabled()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:312`
  - `void LaMoveTo(double posMm, string actionName, bool verbose)` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:323`
  - `void ApplyLaFollow()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:346`
  - `void LaApplySpot(double spotMm, string actionName)` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:363`
  - `void LaMoveToPose(double posMm, string actionName)` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:411`
  - `void FlowProcess()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:446`
  - `bool ResetProcess()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:470`
  - `void ClearStatus()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:478`
  - `void ResetWorkTime()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:485`
  - `bool InitializeOn()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:493`
  - `bool InitializeOff()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:503`
  - `void SubDeviceLog()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:511`
  - `void LoadConfig()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:528`
  - `void SaveConfig()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:543`
  - `void WeldStatusTrans()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:550`
  - `bool ConnectOn()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:562`
  - `bool ConnectOff()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:570`
  - `bool EnsureManualWeldHeadActionAllowed(string actionName, string reason)` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:581`
  - `bool LaAuto()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:592`
  - `bool LaSpot1()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:611`
  - `bool LaSpot2()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:625`
  - `bool LaPose1()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:639`
  - `bool LaDefaultFocus()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:653`
  - `bool MoveToDefaultFocus()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:667`
  - `bool GalvoHome()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:696`
  - `bool GalvoManualStart(WsgGalvoPattern pattern, GalvoShapeParams shape)` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:721`
  - `bool GalvoManualStop()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:762`
  - `void ApplyGalvoCenterOffset(double xMm, double yMm)` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:772`
  - `void GetStepName(int step)` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:785`
- 构造（1）：
  - `LaserWeldHeadWorkflow()` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:164`
- 属性（17）：
  - `LaserWeldHeadWorkflow Instance { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:72`
  - `string StateName { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:82`
  - `string ConfigFileName { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:85`
  - `string ConfigModule { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:88`
  - `LaserHeadTemperatureData LastTemperature { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:91`
  - `HeadAlarmStatus LastAlarmStatus { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:94`
  - `bool IsTemperatureAlarm { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:97`
  - `bool LaReady { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:125`
  - `string LaGateReason { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:128`
  - `bool IsEnabled { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:131`
  - `bool IsHomed { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:134`
  - `bool IsAtWorkZero { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:137`
  - `bool NeedHoming { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:140`
  - `string WorkZeroSource { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:143`
  - `string ReadinessReason { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:146`
  - `bool LaFollowActive { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:149`
  - `double TargetSpotMm { get; set; }` — `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs:152`

## LineLaserWorkflow

- 签名：`public class LineLaserWorkflow : DeviceWorkflowBase`
- 位置：`MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:14`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
- 方法（48）：
  - `void InitializeInternal()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:133`
  - `void RunInitializeSteps(Func<bool> connect, Func<bool> readConfiguration, Func<bool> verifyHardwareStatus)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:173`
  - `void RunStepAction(Func<bool> step, string stepName, string failureReason, LineLaserErrorContext context)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:192`
  - `void IsTimeout(int seconds)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:211`
  - `void BindCamera()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:217`
  - `void ReleaseCameraBinding()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:223`
  - `void DoPreWork()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:232`
  - `void DoPreWorkOn()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:252`
  - `void DoPreWorkStable()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:272`
  - `void DoPreWorkWaitWork()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:287`
  - `void SimPrepareCamera()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:295`
  - `void DoWorking()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:313`
  - `void DoStopping()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:352`
  - `void DoFinishOk()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:361`
  - `void DoFinishFail()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:373`
  - `void SafeShutdownPeripherals()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:381`
  - `void SubscribeCameraEvents()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:387`
  - `void UnsubscribeCameraEvents()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:396`
  - `void ManagerResultReady(object sender, LineLaserResultEventArgs e)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:401`
  - `void RunAutoAdjust()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:433`
  - `void ResetFailureCounters()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:455`
  - `void OnCommunicationCommandReceived(object sender, string message)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:460`
  - `void HandleFailure(string failureSource)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:468`
  - `void Fail(string reason)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:480`
  - `void ConnectWorker(WorkflowRunMode mode)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:488`
  - `void DisconnectWorker(WorkflowRunMode mode)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:521`
  - `void SimReset()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:543`
  - `void Start()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:558`
  - `void Stop()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:585`
  - `void FinishMeasureByStroke()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:600`
  - `void BeginWorking()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:613`
  - `void FlowProcess()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:653`
  - `bool ResetProcess()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:699`
  - `void ClearStatus()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:728`
  - `void ResetWorkTime()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:739`
  - `bool InitializeOn()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:747`
  - `bool InitializeOff()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:775`
  - `void SubDeviceLog()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:795`
  - `void LoadConfig()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:802`
  - `void SaveConfig()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:811`
  - `void WeldStatusTrans()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:821`
  - `bool ConnectOn()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:843`
  - `bool ConnectOff()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:865`
  - `void OnWeldStatusChanged(SubDeviceWeldStatus oldStatus, SubDeviceWeldStatus newStatus)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:891`
  - `void DisposeManaged()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:923`
  - `void StopPendingConnectThreads()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:940`
  - `void JoinPendingThread(Thread thread, string name)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:949`
  - `void GetStepName(int step)` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:969`
- 构造（1）：
  - `LineLaserWorkflow()` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:119`
- 属性（13）：
  - `int DataStableTimeoutSeconds { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:30`
  - `int WaitWorkingTimeoutSeconds { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:33`
  - `int FirstResultTimeoutSeconds { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:36`
  - `bool IsSimulation { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:81`
  - `bool IsVirtualCamera { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:84`
  - `LineLaserWorkflow Instance { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:94`
  - `string StateName { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:101`
  - `bool IsPreWorkDone { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:104`
  - `bool IsDataStable { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:107`
  - `string ConfigFileName { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:110`
  - `string ConfigModule { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:113`
  - `double MaxWeldLengthMm { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:641`
  - `bool IsPreWorkFeedbackDone { get; set; }` — `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs:647`

## MachineAlarmInfo

- 签名：`public class MachineAlarmInfo`
- 位置：`MainDeviceControl/DeviceControlWork.cs:62`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 属性（5）：
  - `bool HasAlarm { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:65`
  - `string ErrorCode { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:68`
  - `string Description { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:71`
  - `DateTime OccurTime { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:74`
  - `MainDeviceStatus StatusAtOccur { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:77`

## MachineStatusSnapshot

- 签名：`public class MachineStatusSnapshot`
- 位置：`MainDeviceControl/DeviceControlWork.cs:81`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 属性（12）：
  - `MainDeviceStatus DeviceStatus { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:84`
  - `MainDeviceStatus LastDeviceStatus { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:87`
  - `Dictionary<string, SubDeviceWeldStatus> SubStatuses { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:90`
  - `ReadinessStage MotionReadiness { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:93`
  - `string ThreadSnapshot { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:96`
  - `bool IsWorking { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:99`
  - `bool IsReseting { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:102`
  - `bool IsInitializing { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:105`
  - `bool IsSimulationEnabled { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:108`
  - `bool IsWelding { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:111`
  - `MachineAlarmInfo Alarm { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:114`
  - `DateTime Timestamp { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:117`

## MainDeviceStatusChangedEventArgs

- 签名：`public class MainDeviceStatusChangedEventArgs : EventArgs`
- 位置：`MainDeviceControl/DeviceControlWork.cs:26`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 属性（4）：
  - `MainDeviceStatus OldStatus { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:29`
  - `MainDeviceStatus NewStatus { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:32`
  - `string Reason { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:35`
  - `DateTime Timestamp { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:38`

## MonitorCameraWorkflow

- 签名：`public class MonitorCameraWorkflow : DeviceWorkflowBase`
- 位置：`MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:18`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
- 方法（50）：
  - `void WirePlaybackEvents()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:180`
  - `void OnPlaybackScanStarted(string caption)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:192`
  - `void OnPlaybackScanCompleted(PlaybackScanResult result)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:197`
  - `void OnPlaybackScanCrashed(string message)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:202`
  - `void OnPlaybackThumbnailReady(PlaybackFileInfo info)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:207`
  - `void OnPlaybackFrameReady(Mat frame)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:212`
  - `void OnPlaybackProgress(int frameIndex, int totalFrames, double fps)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:217`
  - `void OnPlaybackStateChanged(bool isPlaying, double speed)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:222`
  - `void CancelScan()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:228`
  - `void LoadRange(DateTime start, DateTime end)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:236`
  - `string PlayFile(string path)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:244`
  - `string TogglePlayPause()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:251`
  - `void CycleSlow()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:257`
  - `void CycleFast()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:263`
  - `void SeekToFrame(int frameIndex)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:270`
  - `void SeekBySeconds(double seconds)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:277`
  - `void StopPlayback()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:283`
  - `void RequireStandby(string method)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:302`
  - `void EnsureConnected()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:312`
  - `void EnterWeldStatus(SubDeviceWeldStatus status, string reason)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:325`
  - `void Fail(string reason)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:344`
  - `void DoAcquireTrigger()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:353`
  - `void DoAcquireWait()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:366`
  - `void DoAnalyze()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:389`
  - `void DoFinishOk()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:402`
  - `void DoFinishFail()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:416`
  - `void AnalyzeImage()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:426`
  - `void FillResult(WireFeedResult alignment, WeldQualityResult quality)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:463`
  - `void OnManagerPreviewFrame(Mat frame)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:510`
  - `void DisposeFrame(Mat frame)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:538`
  - `void Start(MonitorCameraPhase phase, bool continuous)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:551`
  - `void Stop()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:561`
  - `bool StartRecording(string prefix, string fileName, string failureMessage)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:573`
  - `void StopRecording()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:601`
  - `void StartWeldPreview()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:607`
  - `void StopWeldPreview()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:620`
  - `void FlowProcess()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:636`
  - `bool ResetProcess()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:665`
  - `void ClearStatus()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:674`
  - `void ResetWorkTime()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:683`
  - `bool InitializeOn()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:690`
  - `bool InitializeOff()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:718`
  - `void SubDeviceLog()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:737`
  - `void LoadConfig()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:746`
  - `void SaveConfig()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:752`
  - `void WeldStatusTrans()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:759`
  - `bool ConnectOn()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:776`
  - `bool ConnectOff()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:819`
  - `void GetStepName(int step)` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:834`
  - `void DisposeManaged()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:849`
- 构造（1）：
  - `MonitorCameraWorkflow()` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:292`
- 属性（10）：
  - `MonitorCameraWorkflow Instance { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:76`
  - `string StateName { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:83`
  - `string ConfigFileName { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:86`
  - `string ConfigModule { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:89`
  - `MonitorResult LastResult { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:95`
  - `Mat LastOverlay { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:125`
  - `PlaybackAlgorithm Playback { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:135`
  - `bool HasSource { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:141`
  - `bool IsPlaying { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:147`
  - `double Speed { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:153`

## MonitorResult

- 签名：`public class MonitorResult`
- 位置：`MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:865`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
- 属性（16）：
  - `MonitorCameraPhase Phase { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:868`
  - `bool Pass { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:871`
  - `double QualityScore { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:874`
  - `double OffsetX { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:877`
  - `double OffsetY { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:880`
  - `double WireStickoutDeviation { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:883`
  - `double LateralDevMm { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:886`
  - `WireAlignGrade Grade { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:889`
  - `bool WireMatched { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:892`
  - `bool WireHeadAdhesion { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:895`
  - `bool WireAnomalyDetected { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:898`
  - `string WireAnomalyReason { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:901`
  - `double Angle { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:904`
  - `int DefectCount { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:907`
  - `string Message { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:910`
  - `DateTime Timestamp { get; set; }` — `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs:913`

## MotionControlWorkflow

- 签名：`public class MotionControlWorkflow : DeviceWorkflowBase`
- 位置：`MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:23`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
- 方法（101）：
  - `void ResetToIdle(string reason)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:461`
  - `void EnterWeldStatus(SubDeviceWeldStatus status, string reason, bool enterServoStep)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:474`
  - `void IsTimeout(int seconds)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:496`
  - `void IsAllServoOn()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:503`
  - `void DoServoOn()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:515`
  - `void DoReturnToCalibration()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:574`
  - `void IsWithinYStroke(double pos, double minLimit, double maxLimit)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:715`
  - `void DoStopping()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:723`
  - `void ShutdownSeamAxis()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:751`
  - `void ConfigureSoftTargetReachWindow()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:766`
  - `void ResetSeamAxisBufferBeforeMove()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:777`
  - `void IsSeamAxisSettled()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:803`
  - `void StopSeamTrackingOutput()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:815`
  - `void DoFinishFail()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:826`
  - `void Fail(string reason)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:853`
  - `bool Start()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:867`
  - `void Stop(= false)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:883`
  - `void ClearSeamAlarm()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:910`
  - `void AttachSeamTrackAxis()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:921`
  - `void DetachSeamTrackAxis()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:936`
  - `void OnSeamResultReady(object sender, LineLaserResultEventArgs e)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:955`
  - `void EnqueueSeamPoints(PVTPoint[] points)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:985`
  - `void TryStartSeamTraceYOnReady()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:995`
  - `void UpdateSeamTracking()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1014`
  - `void OnSeamTrackingStart(bool cspMode)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1037`
  - `void OnSeamTrackingStop(bool cspMode)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1067`
  - `void CspTick()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1094`
  - `void PvtTick()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1107`
  - `void TryFlushSeamBuffer(bool isFinal)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1124`
  - `void FlushSeamBuffer(bool isFinal)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1137`
  - `void FlowProcess()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1181`
  - `bool ResetProcess()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1226`
  - `void ClearStatus()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1250`
  - `void ResetWorkTime()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1262`
  - `void TimeBeginPeriod(uint periodMs)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1272`
  - `void TimeEndPeriod(uint periodMs)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1278`
  - `void StartCspOutput()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1292`
  - `void StopCspOutput()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1363`
  - `void OutputCspTick()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1401`
  - `void RunCspTick()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1417`
  - `void IsNoValueThresholdReached(WeldParamConfig config)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1522`
  - `void RaiseNoValueAlarm(WeldParamConfig config)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1532`
  - `void ResolveCspQueryRobotX()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1549`
  - `void QueueCspSegment(double command, double segMm, WeldParamConfig config, double axisNowMm)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1561`
  - `void DetectCspExecutionStall(bool wroteSeg, double axisNow)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1636`
  - `void TryGetSeamAxisSoftLimit(double minMm, double maxMm)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1666`
  - `void ClampToStroke(double value)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1680`
  - `void ReportStrokeClamp(double rawTarget, double target)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1692`
  - `void LogCspBufferDiagnostics()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1703`
  - `void LogCspCorrectionDebug(WeldParamConfig config, double targetY)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1720`
  - `void LogCspMotionDebug(double robotX, double robotY, bool ready, double targetY, double axisNow, double target, double command, double segMm, int commandPulse, bool wroteSeg)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1749`
  - `void ToPulseMm(double valueMm)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1763`
  - `void IsElapsed(DateTime lastTime, int intervalMs)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1772`
  - `void TakeElapsed(DateTime lastTime, int intervalMs)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1781`
  - `void RecordCspPoint(double cspOutY, double axisY)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1791`
  - `void RecordOnlyTick()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1802`
  - `void TakeCspElapsedSeconds()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1829`
  - `void IsEmergencyStop()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1842`
  - `void StepCspTarget(double target, double tickSeconds, double minVelocityMmPerS)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1854`
  - `void EstimateRobotVelocityX(double robotX)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1885`
  - `void ReportCspResult(ushort ret)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1909`
  - `void OnSeamTrackingAlarmRequested(object sender, TrackingAlarmEventArgs e)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1929`
  - `bool InitializeOn()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1939`
  - `bool InitializeOff()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1973`
  - `void SubDeviceLog()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2000`
  - `void LoadConfig()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2008`
  - `void SaveConfig()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2014`
  - `void WeldStatusTrans()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2021`
  - `bool ConnectOn()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2044`
  - `bool ConnectOff()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2053`
  - `void NotifyTaZeroPoseStageChanged()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2219`
  - `void MarkTaZeroPoseRunning(bool running)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2227`
  - `void MarkTaZeroPoseSucceeded()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2239`
  - `void MarkTaZeroPoseFailed(string reason)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2248`
  - `bool ExitTaTorque(string reason)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2265`
  - `bool SetTaTorqueMode(bool enabled, = null)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2281`
  - `bool SetTaTorque(short targetTorque, uint slope)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2301`
  - `bool StopTaTorque(= null)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2332`
  - `string BuildMachineInitSummary()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2349`
  - `void LogAxisGateReport()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2377`
  - `void OnAxisReadinessChanged(string axisName)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2419`
  - `void CheckTaAvailable(string actionName)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2428`
  - `void CheckAutoWeldingConflict(string actionName)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2440`
  - `void TaMoveTo(double posMm, string actionName)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2452`
  - `void TryResolveTaTorque(string actionName, bool reverse, DeltaMontionAxis axis, DeltaAxisConfig axisCfg, short torque, double forceMag, int torqueDirection)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2509`
  - `void TaMoveToPreset(bool pose1)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2596`
  - `void ExecuteTaTorque(TaCommand command)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2614`
  - `void ExecuteTaBreak()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2704`
  - `void ExecuteTaZeroPose()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2765`
  - `string GetTaGateReason(bool allowZeroPose)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2854`
  - `bool TaExecute(TaCommand command)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2873`
  - `bool RunTaZeroPoseAfterInit()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2898`
  - `bool RunInitAutoHomeIfEnabled()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2906`
  - `void EnsureResetReadiness()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2915`
  - `void ResetAxesToWorkZero()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2941`
  - `bool RunTaHomeThenZeroPose()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2993`
  - `bool TryHomeAxisWithWait(string[] roleKeys, string actionName, string axisName, string rejectCode, string rejectDetail, string evidence)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:3014`
  - `bool TryMoveAxisToTarget(string[] roleKeys, double targetMm, string actionName, string axisName, string rejectCode, string rejectDetail, string evidence)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:3098`
  - `void GetStepName(int step)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:3174`
  - `bool TryManualAxisOperation(string[] roleKeys, AxisManualOperation operation, double value, ushort dir, string axisName, bool servoOn, bool commandOk, string rejectReason)` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:3198`
  - `void DisposeManaged()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:3258`
- 构造（1）：
  - `MotionControlWorkflow()` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:444`
- 属性（43）：
  - `MontionManager Manager { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:119`
  - `bool IsSimulation { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:291`
  - `string SeamTrackAxisName { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:294`
  - `bool HasSeamTrackAxis { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:297`
  - `bool IsSeamWelding { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:300`
  - `bool IsCspMode { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:303`
  - `bool IsSimRecordOnly { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:306`
  - `bool IsEnabled { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:312`
  - `bool IsHomed { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:315`
  - `bool IsAtWorkZero { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:318`
  - `bool HasAbsoluteEncoder { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:329`
  - `string WorkZeroSource { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:332`
  - `ReadinessStage MinReadinessStage { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:335`
  - `string ReadinessReason { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:338`
  - `double SeamAxisPosMm { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:344`
  - `MotionControlWorkflow Instance { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:408`
  - `string StateName { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:415`
  - `bool IsRunning { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:418`
  - `bool IsInitialized { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:429`
  - `bool IsCalibrationYReady { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:432`
  - `string ConfigFileName { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:435`
  - `string ConfigModule { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:438`
  - `double AxisEquivMm { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:1282`
  - `DeltaMontionAxis TaAxis { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2068`
  - `DeltaAxisConfig TaAxisConfig { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2078`
  - `bool YReady { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2106`
  - `string YGateReason { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2109`
  - `bool TaAvailable { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2112`
  - `bool TaMotionReady { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2115`
  - `string TaDegradedReason { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2118`
  - `bool TaTorqueActive { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2121`
  - `bool TaTorqueRetractFailed { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2131`
  - `ushort TaTorqueRetractFailCode { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2141`
  - `string TaTorqueRetractFailureText { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2151`
  - `double TaPositionMm { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2162`
  - `double TaBreakHoldMm { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2172`
  - `bool TaBreakHoldValid { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2178`
  - `bool IsTaZeroPoseRunning { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2208`
  - `bool IsTaZeroPoseAttempted { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2211`
  - `bool IsTaZeroPoseDone { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2214`
  - `bool IsTaZeroPoseFailed { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2217`
  - `bool HasHomingRequiredAxis { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2985`
  - `bool HasFreeHomingAxis { get; set; }` — `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs:2988`

## SafetyFlow

- 签名：`public class SafetyFlow`
- 位置：`MainDeviceControl/DeviceStatusWork.cs:531`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 构造（1）：
  - `SafetyFlow()` — `MainDeviceControl/DeviceStatusWork.cs:600`
- 属性（22）：
  - `double MinGasPressure { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:534`
  - `double MinCoolantFlow { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:537`
  - `double MaxCoolantTemperature { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:540`
  - `double MaxHeadTemperature { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:543`
  - `bool RequireAutoMode { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:546`
  - `int PlcDb { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:549`
  - `int EmergencyStopBit { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:552`
  - `int SafetyDoorBit { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:555`
  - `int GasPressureWord { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:558`
  - `int CoolantFlowWord { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:561`
  - `int CoolantTempWord { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:564`
  - `int HeadTempWord { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:567`
  - `int ModeWord { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:570`
  - `int StatusLampDb { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:573`
  - `int GreenLightByte { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:576`
  - `int GreenLightBit { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:579`
  - `int YellowLightByte { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:582`
  - `int YellowLightBit { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:585`
  - `int RedLightByte { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:588`
  - `int RedLightBit { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:591`
  - `int BuzzerByte { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:594`
  - `int BuzzerBit { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:597`

## SafetyInterlockChecker

- 签名：`public class SafetyInterlockChecker`
- 位置：`MainDeviceControl/DeviceStatusWork.cs:646`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 方法（7）：
  - `void ReadWord(SiemensS7Comm plc, int db, int word)` — `MainDeviceControl/DeviceStatusWork.cs:679`
  - `void CheckLowerBound(SafetyInterlockResult result, string name, double value, double min)` — `MainDeviceControl/DeviceStatusWork.cs:689`
  - `void CheckUpperBound(SafetyInterlockResult result, string name, double value, double max)` — `MainDeviceControl/DeviceStatusWork.cs:702`
  - `void CheckPlc(SiemensS7Comm plc, SafetyInterlockResult result)` — `MainDeviceControl/DeviceStatusWork.cs:713`
  - `void CheckDeviceStates(SafetyInterlockResult result)` — `MainDeviceControl/DeviceStatusWork.cs:746`
  - `void CheckDevice(string name, DeviceStateBase device, SafetyInterlockResult result)` — `MainDeviceControl/DeviceStatusWork.cs:766`
  - ` Check()` — `MainDeviceControl/DeviceStatusWork.cs:780`
- 构造（1）：
  - `SafetyInterlockChecker(SafetyFlow thresholds)` — `MainDeviceControl/DeviceStatusWork.cs:665`
- 属性（1）：
  - `SafetyFlow Thresholds { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:657`

## SafetyInterlockResult

- 签名：`public class SafetyInterlockResult`
- 位置：`MainDeviceControl/DeviceStatusWork.cs:628`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 属性（4）：
  - `bool IsPassed { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:631`
  - `List<string> FailedItems { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:634`
  - `string Reason { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:639`
  - `DateTime CheckTime { get; set; }` — `MainDeviceControl/DeviceStatusWork.cs:642`

## SimulationConfig

- 签名：`public sealed class SimulationConfig`
- 位置：`MainDeviceControl/SimulationConfig.cs:9`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 方法（2）：
  - `int LoadLaserFrequencyHz(int fallback)` — `MainDeviceControl/SimulationConfig.cs:49`
  - `bool SaveLaserFrequencyHz(int value)` — `MainDeviceControl/SimulationConfig.cs:71`
- 构造（1）：
  - `SimulationConfig(string filePath)` — `MainDeviceControl/SimulationConfig.cs:35`

## SimulationStoppedEventArgs

- 签名：`public class SimulationStoppedEventArgs : EventArgs`
- 位置：`MainDeviceControl/DeviceControlWork.cs:42`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 构造（1）：
  - `SimulationStoppedEventArgs(string reason, bool hasError, bool isAuto)` — `MainDeviceControl/DeviceControlWork.cs:53`
- 属性（3）：
  - `string Reason { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:45`
  - `bool HasError { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:48`
  - `bool IsAuto { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:51`

## SubDeviceStateChangedEventArgs

- 签名：`public class SubDeviceStateChangedEventArgs : EventArgs`
- 位置：`MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:43`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`
- 属性（4）：
  - `SubDeviceState OldState { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:46`
  - `SubDeviceState NewState { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:49`
  - `string Reason { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:52`
  - `DateTime Timestamp { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:55`

## WeldParamControlWorkflow

- 签名：`public class WeldParamControlWorkflow : DeviceWorkflowBase`
- 位置：`MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:12`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
- 方法（29）：
  - `void FillOutput(WeldParamManager wp)` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:89`
  - `void FillXlOutput(double robotX, double laserPower, double feedSpeed, double robotSpeed, double spotWidth, double seamWidth)` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:109`
  - `void TickXlOutput()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:124`
  - `void CalcGalvoAmplitude(double seamWidthMm)` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:171`
  - `void CalcGalvoFrequency(double seamWidthMm)` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:204`
  - `void SendToRobot(WeldParamAdaptControl output)` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:231`
  - `void Fail(string reason)` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:263`
  - `void DoCompute()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:273`
  - `void DoOutput()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:301`
  - `void DoFinishOk()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:323`
  - `void DoFinishFail()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:336`
  - `bool LoadParameters()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:351`
  - `bool PreWork()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:378`
  - `bool ComputeAndOutput()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:430`
  - `void Complete()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:437`
  - `bool SwitchParameter(string configId)` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:445`
  - `void FlowProcess()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:464`
  - `bool ResetProcess()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:509`
  - `void ClearStatus()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:519`
  - `void ResetWorkTime()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:529`
  - `bool InitializeOn()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:537`
  - `bool InitializeOff()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:550`
  - `void SubDeviceLog()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:560`
  - `void LoadConfig()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:568`
  - `void SaveConfig()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:574`
  - `void WeldStatusTrans()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:581`
  - `bool ConnectOn()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:592`
  - `bool ConnectOff()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:601`
  - `void GetStepName(int step)` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:617`
- 构造（1）：
  - `WeldParamControlWorkflow()` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:76`
- 属性（7）：
  - `WeldParamControlWorkflow Instance { get; set; }` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:48`
  - `string StateName { get; set; }` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:55`
  - `bool IsParamReady { get; set; }` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:58`
  - `int ConsecutiveFailureCount { get; set; }` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:61`
  - `WeldParamAdaptControl LastOutput { get; set; }` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:64`
  - `string ConfigFileName { get; set; }` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:67`
  - `string ConfigModule { get; set; }` — `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs:70`

## WeldStatusChangedEventArgs

- 签名：`public class WeldStatusChangedEventArgs : EventArgs`
- 位置：`MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:59`
- 命名空间：`AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`
- 属性（4）：
  - `SubDeviceWeldStatus OldStatus { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:62`
  - `SubDeviceWeldStatus NewStatus { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:65`
  - `string Reason { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:68`
  - `DateTime Timestamp { get; set; }` — `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs:71`

## WorkThreadEntry

- 签名：`private sealed class WorkThreadEntry`
- 位置：`MainDeviceControl/DeviceControlWork.cs:3784`
- 命名空间：`AdaWeldSystem.MainDeviceControl`
- 属性（6）：
  - `string Name { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:3787`
  - `Thread Thread { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:3790`
  - `int TimeoutMs { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:3793`
  - `DateTime RegisteredAt { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:3796`
  - `bool Exited { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:3799`
  - `bool JoinTimedOut { get; set; }` — `MainDeviceControl/DeviceControlWork.cs:3802`

## 相关页面

- [[architecture/CodeMap]]
