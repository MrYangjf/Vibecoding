---
title: CodeMap-Symbols-WeldParamControl — 代码地图·符号签名层·WeldParamControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-WeldParamControl — WeldParamControl 的类型与签名

> **一句话**：模块 `WeldParamControl` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> 焊接工艺参数与自适应：焊参真相源 + 算法规格
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.WeldParamControl` | 4 | 15 | 焊参 · Manager 与配置 | [[modules/WeldParamControl]] | ADR-033/043 |
| `AdaWeldSystem.WeldParamControl.Algorithms` | 4 | 6 | 焊参 · 算法实现 | [[modules/WeldParamControl]] | ADR-042/043 |
| `AdaWeldSystem.WeldParamControl.Abstractions` | 1 | 1 | 焊参 · 抽象契约（WeldAlgorithmBase） | [[modules/WeldParamControl]] | ADR-006/043 |
| `AdaWeldSystem.WeldParamControl.Curves` | 1 | 2 | 焊参 · 标定曲线与摆幅取值（2026-10-08 新增，ADR-053） | [[modules/WeldParamControl]] | ADR-053（曲线与量纲）/ 红线原文 `api/WeldParamControlWorkflow.md`（⛔ 不用自创公式；⚠️ ADR-043 正文无此条款，原标注为悬空引用，2026-10-08 审计改指）/ ADR-033（四点闭环） |

| 项 | 值 |
|---|---|
| 类型数 | 24 |
| 方法数 | 436 |

## 章节导航

- [AutoParam](#AutoParam)
- [ChartVar](#ChartVar)
- [ConfigRegion](#ConfigRegion)
- [CurvePoint](#CurvePoint)
- [RobotWeldData](#RobotWeldData)
- [SeamCalData](#SeamCalData)
- [SeamMapTrackingAlgorithm](#SeamMapTrackingAlgorithm)
- [SeamTrackingAlgorithm](#SeamTrackingAlgorithm)
- [TaLaCurveConfig](#TaLaCurveConfig)
- [TrackingAlarmEventArgs](#TrackingAlarmEventArgs)
- [WeldAdjustmentRecordEventArgs](#WeldAdjustmentRecordEventArgs)
- [WeldAlgorithmBase](#WeldAlgorithmBase)
- [WeldFlowStepInfo](#WeldFlowStepInfo)
- [WeldFlowSteps](#WeldFlowSteps)
- [WeldFrameRecordEventArgs](#WeldFrameRecordEventArgs)
- [WeldParamAdaptControl](#WeldParamAdaptControl)
- [WeldParamAdjustmentAlgorithm](#WeldParamAdjustmentAlgorithm)
- [WeldParamConfig](#WeldParamConfig)
- [WeldParamLookupAlgorithm](#WeldParamLookupAlgorithm)
- [WeldParamManager](#WeldParamManager)
- [WeldParamMontionControl](#WeldParamMontionControl)
- [WeldParamProfileAudit](#WeldParamProfileAudit)
- [WeldProcessCompletedEventArgs](#WeldProcessCompletedEventArgs)
- [XLPoint](#XLPoint)

## AutoParam

- 签名：`public class AutoParam`
- 位置：`WeldParamControl/WeldParamData.cs:266`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 方法（3）：
  - ` CreateDefault()` — `WeldParamControl/WeldParamData.cs:361`
  - `void CalVar()` — `WeldParamControl/WeldParamData.cs:367`
  - `int CalSwingFrequency(double swingWidthMm)` — `WeldParamControl/WeldParamData.cs:400`
- 构造（1）：
  - `AutoParam(string identity, DateTime creatTime)` — `WeldParamControl/WeldParamData.cs:338`
- 属性（1）：
  - `bool IsDefault { get; set; }` — `WeldParamControl/WeldParamData.cs:333`

## ChartVar

- 签名：`public class ChartVar`
- 位置：`WeldParamControl/WeldParamData.cs:431`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 方法（5）：
  - `void Add(double x, double y)` — `WeldParamControl/WeldParamData.cs:449`
  - `int Count()` — `WeldParamControl/WeldParamData.cs:460`
  - `void Clear()` — `WeldParamControl/WeldParamData.cs:469`
  - `bool TrySnapshot(double[] xs, double[] ys)` — `WeldParamControl/WeldParamData.cs:483`
  - `bool TryCopyRange(int startIndex, int count, double[] xs, double[] ys)` — `WeldParamControl/WeldParamData.cs:508`
- 构造（1）：
  - `ChartVar()` — `WeldParamControl/WeldParamData.cs:440`

## ConfigRegion

- 签名：`public class ConfigRegion`
- 位置：`WeldParamControl/WeldParamConfig.cs:35`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 属性（3）：
  - `string Name { get; set; }` — `WeldParamControl/WeldParamConfig.cs:38`
  - `string[] Sections { get; set; }` — `WeldParamControl/WeldParamConfig.cs:41`
  - `Dictionary<string, string[]> Keys { get; set; }` — `WeldParamControl/WeldParamConfig.cs:44`

## CurvePoint

- 签名：`public class CurvePoint`
- 位置：`WeldParamControl/Curves/TaLaCurveConfig.cs:32`
- 命名空间：`AdaWeldSystem.WeldParamControl.Curves`
- 构造（2）：
  - `CurvePoint()` — `WeldParamControl/Curves/TaLaCurveConfig.cs:41`
  - `CurvePoint(double x, double y)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:50`
- 属性（2）：
  - `double X { get; set; }` — `WeldParamControl/Curves/TaLaCurveConfig.cs:35`
  - `double Y { get; set; }` — `WeldParamControl/Curves/TaLaCurveConfig.cs:38`

## RobotWeldData

- 签名：`public class RobotWeldData`
- 位置：`WeldParamControl/WeldParamData.cs:75`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 方法（7）：
  - `void SetStartX(double startX)` — `WeldParamControl/WeldParamData.cs:104`
  - `void SetEndX(double endX)` — `WeldParamControl/WeldParamData.cs:111`
  - `void SetEndDelayDistance(double delayDistance)` — `WeldParamControl/WeldParamData.cs:118`
  - `void SetWeldRange(double startX, double endX, double delayDistance)` — `WeldParamControl/WeldParamData.cs:127`
  - `bool IsInWeldArea(double robotX)` — `WeldParamControl/WeldParamData.cs:136`
  - `bool IsBeyondEnd(double robotX)` — `WeldParamControl/WeldParamData.cs:143`
  - `bool SetRobot(string posX, string posY, string posZ, string speed)` — `WeldParamControl/WeldParamData.cs:154`
- 构造（1）：
  - `RobotWeldData()` — `WeldParamControl/WeldParamData.cs:91`
- 属性（1）：
  - `double EffectiveEndX { get; set; }` — `WeldParamControl/WeldParamData.cs:85`

## SeamCalData

- 签名：`public class SeamCalData`
- 位置：`WeldParamControl/WeldParamData.cs:165`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 方法（2）：
  - `double SeamWidthCal()` — `WeldParamControl/WeldParamData.cs:180`
  - `void AddSeamWidth(double seamWidth)` — `WeldParamControl/WeldParamData.cs:195`
- 构造（1）：
  - `SeamCalData()` — `WeldParamControl/WeldParamData.cs:172`

## SeamMapTrackingAlgorithm

- 签名：`public class SeamMapTrackingAlgorithm : WeldAlgorithmBase`
- 位置：`WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:74`
- 命名空间：`AdaWeldSystem.WeldParamControl.Algorithms`
- 方法（24）：
  - `void Log(string message, MessageLevel level)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:305`
  - `void ClearAlarm()` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:311`
  - `void RaiseAlarmRequest(string reason)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:320`
  - `void ProcessLaserResult(double featureY, double axisPosMm)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:338`
  - `void IsOutlier(double newTargetY, double arriveX)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:448`
  - `void InsertMapPoint(double robotX, double targetY, double robotY, double pathDistance, long timestamp)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:507`
  - `void QueryTargetY(double robotX, double targetY, double pointRobotY)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:534`
  - `void ApplyMonotonic(double rawValue, double robotX)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:577`
  - `void ReseedMonotonic(double rawValue, double robotX)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:622`
  - `void UpdateDirection(double dx)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:636`
  - `void ProcessRsiPose(double robotX, double robotY, double robotZ)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:688`
  - `void FilterRobotY(double robotY)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:700`
  - `void CachePose(double robotX, double robotY, double robotZ)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:719`
  - `void TrackPathDistance(double robotX, double robotY, double robotZ)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:756`
  - `void UpdatePredictedRobotX(double robotX)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:777`
  - `void ClearAlarmState()` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:784`
  - `void SetConfig(WeldParamConfig config)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:798`
  - `void LoadConfig(object config)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:809`
  - `void Reset()` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:815`
  - `void BeginCorrection()` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:885`
  - `bool TryGetRequiredAxisVelocityMmPerS(double robotVxMmPerS, double requiredVelMmPerS)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:900`
  - `bool TryGetTargetY(double robotX, double robotY, double targetY)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:937`
  - `void OnLaserResult(LineLaserSeamResult result, double axisPosMm)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:980`
  - `void OnRsiPose(double robotX, double robotY, double robotZ)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:1006`
- 构造（1）：
  - `SeamMapTrackingAlgorithm()` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:292`
- 属性（28）：
  - `string Name { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:197`
  - `bool IsReady { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:200`
  - `WeldParamConfig Config { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:203`
  - `bool IsTracking { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:206`
  - `bool PauseIngest { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:209`
  - `double CorrectionMm { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:216`
  - `bool HasCorrection { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:219`
  - `bool HasAlarm { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:222`
  - `string AlarmReason { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:225`
  - `double RobotX { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:228`
  - `double RobotY { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:231`
  - `double PathDistance { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:234`
  - `int MapPointCount { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:237`
  - `int OutlierCount { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:240`
  - `int TimeRejectCount { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:243`
  - `int SpaceRejectCount { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:246`
  - `int TargetStepRejectCount { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:249`
  - `double AxisAtMeasureMm { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:252`
  - `double LastAcceptedTargetY { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:255`
  - `double LastMapEntryKeyX { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:258`
  - `bool HasLastMapEntry { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:261`
  - `int InvalidFrameCount { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:264`
  - `int SmoothSkipCount { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:267`
  - `double LastDy { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:270`
  - `double LastCorrectionMm { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:273`
  - `double LastFeatureY { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:276`
  - `double PathYOffset { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:279`
  - `int JitterRejectCount { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:282`

## SeamTrackingAlgorithm

- 签名：`public class SeamTrackingAlgorithm : WeldAlgorithmBase`
- 位置：`WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:13`
- 命名空间：`AdaWeldSystem.WeldParamControl.Algorithms`
- 方法（14）：
  - `void Log(string message, MessageLevel level)` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:103`
  - `void ReadRobotX()` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:110`
  - `void SetFault(string reason)` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:124`
  - `void ClearFault()` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:133`
  - `void ApplyMonotonic(double rawDev, double robotX)` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:144`
  - `void AddPoint(double pos, double time, double vel)` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:187`
  - `void ProcessSample(SeamGuideSample sample)` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:196`
  - `void TakePending()` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:253`
  - `void SetConfig(WeldParamConfig config)` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:268`
  - `void LoadConfig(object config)` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:279`
  - `PVTPoint[] Feed(LineLaserSeamResult result, double measuredFps, double axisCurrentPos)` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:289`
  - `PVTPoint[] Tick()` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:309`
  - `PVTPoint[] Drain()` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:321`
  - `void Reset()` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:330`
- 构造（1）：
  - `SeamTrackingAlgorithm()` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:88`
- 属性（7）：
  - `string Name { get; set; }` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:63`
  - `bool IsReady { get; set; }` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:66`
  - `WeldParamConfig Config { get; set; }` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:69`
  - `bool HasFault { get; set; }` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:72`
  - `string FaultReason { get; set; }` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:75`
  - `double LastDeviation { get; set; }` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:78`
  - `double LastTargetPos { get; set; }` — `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs:81`

## TaLaCurveConfig

- 签名：`public class TaLaCurveConfig`
- 位置：`WeldParamControl/Curves/TaLaCurveConfig.cs:58`
- 命名空间：`AdaWeldSystem.WeldParamControl.Curves`
- 方法（14）：
  - `void ParsePoint(string[] cells, double x, double y)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:128`
  - `void ResetToDefaultPoints()` — `WeldParamControl/Curves/TaLaCurveConfig.cs:153`
  - `double QueryLaPositionMm(double spotMm)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:165`
  - `double QuerySpotMm(double laMm)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:173`
  - `double QueryLaOffsetMm(double taMm)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:181`
  - `bool LoadFromFile()` — `WeldParamControl/Curves/TaLaCurveConfig.cs:189`
  - `void SaveToFile()` — `WeldParamControl/Curves/TaLaCurveConfig.cs:219`
  - `bool ImportFromCsv(string path, string error)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:244`
  - `bool IsValid(List<CurvePoint> points)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:305`
  - `void Interpolate(List<CurvePoint> points, double value, bool invert)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:325`
  - `void Domain(CurvePoint p, bool invert)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:383`
  - `void Range(CurvePoint p, bool invert)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:392`
  - `void ReadPoints(XdocumentReaderWriter reader, string key)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:401`
  - `void WritePoints(XdocumentReaderWriter reader, string key, List<CurvePoint> points)` — `WeldParamControl/Curves/TaLaCurveConfig.cs:421`
- 构造（1）：
  - `TaLaCurveConfig()` — `WeldParamControl/Curves/TaLaCurveConfig.cs:111`
- 属性（6）：
  - `List<CurvePoint> PointsA { get; set; }` — `WeldParamControl/Curves/TaLaCurveConfig.cs:79`
  - `List<CurvePoint> PointsB { get; set; }` — `WeldParamControl/Curves/TaLaCurveConfig.cs:82`
  - `CurveInterpolation Interpolation { get; set; }` — `WeldParamControl/Curves/TaLaCurveConfig.cs:85`
  - `CurveExtrapolation Extrapolation { get; set; }` — `WeldParamControl/Curves/TaLaCurveConfig.cs:88`
  - `string Version { get; set; }` — `WeldParamControl/Curves/TaLaCurveConfig.cs:91`
  - `double AnchorSpotMm { get; set; }` — `WeldParamControl/Curves/TaLaCurveConfig.cs:94`

## TrackingAlarmEventArgs

- 签名：`public class TrackingAlarmEventArgs : EventArgs`
- 位置：`WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:52`
- 命名空间：`AdaWeldSystem.WeldParamControl.Algorithms`
- 构造（1）：
  - `TrackingAlarmEventArgs(string reason)` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:65`
- 属性（1）：
  - `string Reason { get; set; }` — `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs:57`

## WeldAdjustmentRecordEventArgs

- 签名：`public class WeldAdjustmentRecordEventArgs : WeldFrameRecordEventArgs`
- 位置：`WeldParamControl/WeldParamData.cs:612`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 构造（1）：
  - `WeldAdjustmentRecordEventArgs(double robotX, double robotY, double robotZ, double robotSpeed, double feedSpeed, double laserPower, double weldWidth)` — `WeldParamControl/WeldParamData.cs:617`
- 属性（1）：
  - `double RobotSpeedOutput { get; set; }` — `WeldParamControl/WeldParamData.cs:615`

## WeldAlgorithmBase

- 签名：`public abstract class WeldAlgorithmBase`
- 位置：`WeldParamControl/Abstractions/WeldAlgorithmBase.cs:4`
- 命名空间：`AdaWeldSystem.WeldParamControl.Abstractions`
- 方法（2）：
  - `void LoadConfig(object config)` — `WeldParamControl/Abstractions/WeldAlgorithmBase.cs:14`
  - `void Reset()` — `WeldParamControl/Abstractions/WeldAlgorithmBase.cs:17`
- 属性（2）：
  - `string Name { get; set; }` — `WeldParamControl/Abstractions/WeldAlgorithmBase.cs:7`
  - `bool IsReady { get; set; }` — `WeldParamControl/Abstractions/WeldAlgorithmBase.cs:10`

## WeldFlowStepInfo

- 签名：`public class WeldFlowStepInfo`
- 位置：`WeldParamControl/WeldParamData.cs:19`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 构造（1）：
  - `WeldFlowStepInfo(WeldFlowStep step, string title, string subTitle, string description)` — `WeldParamControl/WeldParamData.cs:32`

## WeldFlowSteps

- 签名：`public static class WeldFlowSteps`
- 位置：`WeldParamControl/WeldParamData.cs:42`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 方法（2）：
  - `int IndexOf(WeldFlowStep step)` — `WeldParamControl/WeldParamData.cs:60`
  - ` Get(WeldFlowStep step)` — `WeldParamControl/WeldParamData.cs:68`
- 属性（1）：
  - `int Count { get; set; }` — `WeldParamControl/WeldParamData.cs:55`

## WeldFrameRecordEventArgs

- 签名：`public class WeldFrameRecordEventArgs : EventArgs`
- 位置：`WeldParamControl/WeldParamData.cs:571`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 构造（1）：
  - `WeldFrameRecordEventArgs(double robotX, double robotY, double robotZ, double robotSpeed, double feedSpeed, double laserPower, double weldWidth)` — `WeldParamControl/WeldParamData.cs:597`
- 属性（8）：
  - `double RobotX { get; set; }` — `WeldParamControl/WeldParamData.cs:574`
  - `double RobotY { get; set; }` — `WeldParamControl/WeldParamData.cs:577`
  - `double RobotZ { get; set; }` — `WeldParamControl/WeldParamData.cs:580`
  - `double RobotSpeed { get; set; }` — `WeldParamControl/WeldParamData.cs:583`
  - `double FeedSpeed { get; set; }` — `WeldParamControl/WeldParamData.cs:586`
  - `double LaserPower { get; set; }` — `WeldParamControl/WeldParamData.cs:589`
  - `double WeldWidth { get; set; }` — `WeldParamControl/WeldParamData.cs:592`
  - `DateTime Timestamp { get; set; }` — `WeldParamControl/WeldParamData.cs:595`

## WeldParamAdaptControl

- 签名：`public class WeldParamAdaptControl`
- 位置：`WeldParamControl/WeldParamData.cs:214`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 成员：（无）

## WeldParamAdjustmentAlgorithm

- 签名：`public class WeldParamAdjustmentAlgorithm : WeldAlgorithmBase`
- 位置：`WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:14`
- 命名空间：`AdaWeldSystem.WeldParamControl.Algorithms`
- 方法（13）：
  - `void ManualFixedWidthMm()` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:222`
  - `void Log(string message, MessageLevel level)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:236`
  - `void RaiseFrameRecord(double robotX)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:243`
  - `void RaiseAdjustmentRecord(double robotX)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:254`
  - `void RaiseAbortRecord()` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:269`
  - `void StoreChartData(double robotX, List<System.Drawing.Point> contourPoints)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:278`
  - `void LoadConfig(object config)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:303`
  - `void SetConfig(WeldParamConfig config)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:310`
  - `void Reset()` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:317`
  - `void AccumulateSeamWidth(double seamWidth)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:351`
  - `void ExecuteAdjustment(AutoParam autoParam, = 0, = null)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:363`
  - `void OnParamFrame(double measureRobotX, double laserPower, double feedSpeed, double robotSpeed, double spotWidth, double seamWidth)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:505`
  - `bool TryGetOutputAt(double robotXNow, double laserPower, double feedSpeed, double robotSpeed, double spotWidth, double seamWidth)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:550`
- 构造（1）：
  - `WeldParamAdjustmentAlgorithm(WeldParamLookupAlgorithm lookup, RobotWeldData robotWeldData)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:195`
- 属性（18）：
  - `string Name { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:86`
  - `bool IsReady { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:89`
  - `WeldParamConfig Config { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:92`
  - `int ConsecutiveFailureCount { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:116`
  - `int MaxConsecutiveFailures { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:119`
  - `int TotalExecuteCount { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:126`
  - `SeamCalData SeamCalData { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:129`
  - `double FeedforwardSafetyFactor { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:136`
  - `bool EnableMonotonicConstraint { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:143`
  - `ChartVar ContourChart { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:150`
  - `ChartVar LaserPowerChart { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:153`
  - `ChartVar FeedSpeedChart { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:156`
  - `ChartVar SeamWidthChart { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:159`
  - `ChartVar RobotSpeedChart { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:162`
  - `long OutputVersion { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:165`
  - `int XlCacheCount { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:168`
  - `int XlJitterRejectCount { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:171`
  - `int XlDroppedCount { get; set; }` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:174`

## WeldParamConfig

- 签名：`public class WeldParamConfig`
- 位置：`WeldParamControl/WeldParamConfig.cs:28`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 方法（33）：
  - `void BuildRegions()` — `WeldParamControl/WeldParamConfig.cs:456`
  - `void ReadInt(XdocumentReaderWriter reader, string path, int def)` — `WeldParamControl/WeldParamConfig.cs:533`
  - `void ReadDouble(XdocumentReaderWriter reader, string path, double def)` — `WeldParamControl/WeldParamConfig.cs:539`
  - `void ReadTrackingMode(XdocumentReaderWriter reader, string path, SeamTrackingMode def)` — `WeldParamControl/WeldParamConfig.cs:550`
  - `void Text(double value)` — `WeldParamControl/WeldParamConfig.cs:564`
  - `void SetChild(XdocumentReaderWriter reader, XElement parent, string name, string value)` — `WeldParamControl/WeldParamConfig.cs:575`
  - `void RemoveChild(XElement parent, string name)` — `WeldParamControl/WeldParamConfig.cs:595`
  - `void ReadDoubleIni(INIFile ini, string section, string key, double def)` — `WeldParamControl/WeldParamConfig.cs:605`
  - `void ReadIntIni(INIFile ini, string section, string key, int def)` — `WeldParamControl/WeldParamConfig.cs:614`
  - `void LoadConfig()` — `WeldParamControl/WeldParamConfig.cs:627`
  - `void SaveConfig()` — `WeldParamControl/WeldParamConfig.cs:636`
  - `void LoadProcessIni()` — `WeldParamControl/WeldParamConfig.cs:653`
  - `void SaveProcessIni()` — `WeldParamControl/WeldParamConfig.cs:671`
  - `void LoadZoneXml(AlgorithmsZone zone)` — `WeldParamControl/WeldParamConfig.cs:691`
  - `void SaveZoneXml(AlgorithmsZone zone)` — `WeldParamControl/WeldParamConfig.cs:707`
  - `void LoadZoneIni(AlgorithmsZone zone)` — `WeldParamControl/WeldParamConfig.cs:728`
  - `void SaveZoneIni(AlgorithmsZone zone)` — `WeldParamControl/WeldParamConfig.cs:746`
  - `void WriteZoneIniTo(INIFile ini, AlgorithmsZone zone)` — `WeldParamControl/WeldParamConfig.cs:770`
  - `void WriteConfigTo(XdocumentReaderWriter reader)` — `WeldParamControl/WeldParamConfig.cs:786`
  - `void LoadZoneXmlSystem(XdocumentReaderWriter reader)` — `WeldParamControl/WeldParamConfig.cs:798`
  - `void SaveZoneXmlSystem(XdocumentReaderWriter reader)` — `WeldParamControl/WeldParamConfig.cs:829`
  - `void LoadZoneXmlPreset(XdocumentReaderWriter reader)` — `WeldParamControl/WeldParamConfig.cs:854`
  - `void SaveZoneXmlPreset(XdocumentReaderWriter reader)` — `WeldParamControl/WeldParamConfig.cs:863`
  - `void LoadZoneIniSystem(INIFile ini)` — `WeldParamControl/WeldParamConfig.cs:878`
  - `void SaveZoneIniSystem(INIFile ini)` — `WeldParamControl/WeldParamConfig.cs:934`
  - `void LoadZoneIniQuick(INIFile ini)` — `WeldParamControl/WeldParamConfig.cs:958`
  - `void SaveZoneIniQuick(INIFile ini)` — `WeldParamControl/WeldParamConfig.cs:964`
  - `void LoadZoneIniFlow(INIFile ini)` — `WeldParamControl/WeldParamConfig.cs:970`
  - `void SaveZoneIniFlow(INIFile ini)` — `WeldParamControl/WeldParamConfig.cs:981`
  - `void LoadZoneIniAdapt(INIFile ini)` — `WeldParamControl/WeldParamConfig.cs:992`
  - `void SaveZoneIniAdapt(INIFile ini)` — `WeldParamControl/WeldParamConfig.cs:1007`
  - `void LoadZoneIniPreset(INIFile ini)` — `WeldParamControl/WeldParamConfig.cs:1014`
  - `void SaveZoneIniPreset(INIFile ini)` — `WeldParamControl/WeldParamConfig.cs:1045`
- 构造（1）：
  - `WeldParamConfig()` — `WeldParamControl/WeldParamConfig.cs:375`
- 属性（61）：
  - `Dictionary<AlgorithmsZone, ConfigRegion> Regions { get; set; }` — `WeldParamControl/WeldParamConfig.cs:48`
  - `IniConfigFile IniCarrier { get; set; }` — `WeldParamControl/WeldParamConfig.cs:57`
  - `XmlConfigFile XmlCarrier { get; set; }` — `WeldParamControl/WeldParamConfig.cs:63`
  - `SeamTrackingMode TrackingMode { get; set; }` — `WeldParamControl/WeldParamConfig.cs:176`
  - `double RobotYFilterAlpha { get; set; }` — `WeldParamControl/WeldParamConfig.cs:179`
  - `double GaussianSigmaMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:182`
  - `double GaussianHalfWindowMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:185`
  - `double TeachLockYMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:188`
  - `double CalibratedCenterY { get; set; }` — `WeldParamControl/WeldParamConfig.cs:191`
  - `double CalibratedCenterZ { get; set; }` — `WeldParamControl/WeldParamConfig.cs:194`
  - `double LaserToHorizontalAngleDeg { get; set; }` — `WeldParamControl/WeldParamConfig.cs:197`
  - `int MaxMapPoints { get; set; }` — `WeldParamControl/WeldParamConfig.cs:200`
  - `double NoValueToleranceMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:203`
  - `double OutlierLimitMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:206`
  - `double NearbyWindowMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:209`
  - `double OutlierSigmaK { get; set; }` — `WeldParamControl/WeldParamConfig.cs:212`
  - `double OutlierSlopeLimitMmPerMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:215`
  - `double MaxStepChangeMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:218`
  - `double MaxTargetStepMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:221`
  - `int ConsecutiveRejectFrames { get; set; }` — `WeldParamControl/WeldParamConfig.cs:224`
  - `double MonotonicWindowMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:227`
  - `double MonotonicDeadbandMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:230`
  - `double MonotonicReleaseMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:233`
  - `bool EnableMonotonicConstraint { get; set; }` — `WeldParamControl/WeldParamConfig.cs:236`
  - `double OutputDeadbandMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:239`
  - `double MaxVelMmPerS { get; set; }` — `WeldParamControl/WeldParamConfig.cs:242`
  - `double MaxAccMmPerS2 { get; set; }` — `WeldParamControl/WeldParamConfig.cs:245`
  - `double FeedforwardSafetyFactor { get; set; }` — `WeldParamControl/WeldParamConfig.cs:248`
  - `double CspMinSegMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:251`
  - `double ReverseAlarmMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:254`
  - `double ReverseDeadbandMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:257`
  - `bool EnableSeamTrace { get; set; }` — `WeldParamControl/WeldParamConfig.cs:264`
  - `bool EnableWireAlign { get; set; }` — `WeldParamControl/WeldParamConfig.cs:267`
  - `bool EnableTempCtrl { get; set; }` — `WeldParamControl/WeldParamConfig.cs:270`
  - `bool EnableGalvoWeave { get; set; }` — `WeldParamControl/WeldParamConfig.cs:273`
  - `bool EnableGuide { get; set; }` — `WeldParamControl/WeldParamConfig.cs:276`
  - `bool LockYCalib { get; set; }` — `WeldParamControl/WeldParamConfig.cs:279`
  - `int MaxConsecutiveFailures { get; set; }` — `WeldParamControl/WeldParamConfig.cs:286`
  - `double SegmentDistanceMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:289`
  - `SeamWidthSource SeamWidthSource { get; set; }` — `WeldParamControl/WeldParamConfig.cs:292`
  - `double AxisMmPerLaserMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:302`
  - `int GuideSign { get; set; }` — `WeldParamControl/WeldParamConfig.cs:305`
  - `double LeadDistanceMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:308`
  - `double RobotYGain { get; set; }` — `WeldParamControl/WeldParamConfig.cs:311`
  - `double TaForceN { get; set; }` — `WeldParamControl/WeldParamConfig.cs:314`
  - `double TaPose1Mm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:317`
  - `double TaPose2Mm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:320`
  - `double TaZeroPoseMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:323`
  - `double LaSpotTargetMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:326`
  - `double LaSpot1Mm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:329`
  - `double LaSpot2Mm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:332`
  - `double LaPose1Mm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:335`
  - `double LaDefaultFocusMm { get; set; }` — `WeldParamControl/WeldParamConfig.cs:338`
  - `int GalvoPattern { get; set; }` — `WeldParamControl/WeldParamConfig.cs:341`
  - `bool GalvoAutoCenterComp { get; set; }` — `WeldParamControl/WeldParamConfig.cs:344`
  - `double GalvoCenterCompGain { get; set; }` — `WeldParamControl/WeldParamConfig.cs:347`
  - `int BatchSize { get; set; }` — `WeldParamControl/WeldParamConfig.cs:354`
  - `int MinRemainBuffer { get; set; }` — `WeldParamControl/WeldParamConfig.cs:357`
  - `double DefaultFrameSeconds { get; set; }` — `WeldParamControl/WeldParamConfig.cs:360`
  - `int MaxOutputIntervalMs { get; set; }` — `WeldParamControl/WeldParamConfig.cs:363`
  - `int MaxPendingPoints { get; set; }` — `WeldParamControl/WeldParamConfig.cs:366`

## WeldParamLookupAlgorithm

- 签名：`public class WeldParamLookupAlgorithm : WeldAlgorithmBase`
- 位置：`WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:10`
- 命名空间：`AdaWeldSystem.WeldParamControl.Algorithms`
- 方法（11）：
  - `void AddLookupEntry(AutoParam autoParam, double seamWidthValue)` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:67`
  - `void Log(string message, MessageLevel level)` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:92`
  - `void LoadConfig(object config)` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:99`
  - `void BuildLookupTable(AutoParam autoParam)` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:110`
  - `bool TryLookup(double seamWidth, double laserPower, double feedSpeed, double robotSpeed)` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:162`
  - `bool TryLookupWithSpot(double seamWidth, double laserPower, double feedSpeed, double robotSpeed, double spotWidth)` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:208`
  - `bool TryLookupSwingWidth(double seamWidth, double swingWidth)` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:245`
  - `bool TryLookupSwingFrequency(double seamWidth, int frequencyHz)` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:278`
  - `double FeedSpeedCal(AutoParam autoParam, double robotSpeed, double seamWidth)` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:313`
  - `double LaserPowerCal(AutoParam autoParam, double feedSpeed)` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:327`
  - `void Reset()` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:338`
- 构造（1）：
  - `WeldParamLookupAlgorithm()` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:44`
- 属性（9）：
  - `List<double> SeamWidthList { get; set; }` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:18`
  - `string Name { get; set; }` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:21`
  - `Dictionary<double, double> LaserPowerDic { get; set; }` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:23`
  - `Dictionary<double, double> FeedSpeedDic { get; set; }` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:26`
  - `Dictionary<double, double> RobotSpeedDic { get; set; }` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:29`
  - `Dictionary<double, double> SpotWidthDic { get; set; }` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:32`
  - `Dictionary<double, double> SwingWidthDic { get; set; }` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:35`
  - `Dictionary<double, int> SwingFrequencyDic { get; set; }` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:38`
  - `bool IsReady { get; set; }` — `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs:41`

## WeldParamManager

- 签名：`public class WeldParamManager`
- 位置：`WeldParamControl/WeldParamManager.cs:25`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 方法（53）：
  - `bool TryGetRobotPose(double x, double y, double z)` — `WeldParamControl/WeldParamManager.cs:475`
  - `void EnsureDefaultConfigExists()` — `WeldParamControl/WeldParamManager.cs:530`
  - `void SaveCurrentIdToIni()` — `WeldParamControl/WeldParamManager.cs:552`
  - `void LoadCurrentConfig()` — `WeldParamControl/WeldParamManager.cs:559`
  - `void BuildProfileFromLookupTable()` — `WeldParamControl/WeldParamManager.cs:583`
  - `void AttachRobotPoseChannel()` — `WeldParamControl/WeldParamManager.cs:598`
  - `void OnRobotDataReceived(object sender, KUKADataReceivedEventArgs e)` — `WeldParamControl/WeldParamManager.cs:615`
  - `void UpdatePosePredictor(double x, double y)` — `WeldParamControl/WeldParamManager.cs:635`
  - `void AccumulateNoValueDistanceOnPose(double x)` — `WeldParamControl/WeldParamManager.cs:674`
  - `void EstimateNoValueTravelMm(double seconds)` — `WeldParamControl/WeldParamManager.cs:719`
  - `void ResetNoValueDistance()` — `WeldParamControl/WeldParamManager.cs:727`
  - `void SetNoValueMeasuring(bool on)` — `WeldParamControl/WeldParamManager.cs:738`
  - `void LogNoValueDistance(double distanceMm, bool estimated)` — `WeldParamControl/WeldParamManager.cs:749`
  - `void PosePredictElapsedSeconds()` — `WeldParamControl/WeldParamManager.cs:771`
  - `void ClampPredictVelocity(double velocity)` — `WeldParamControl/WeldParamManager.cs:782`
  - ` GetOrCreateJointDefault(int jointType)` — `WeldParamControl/WeldParamManager.cs:793`
  - `void UpdateRobotPose(double x, double y, double z)` — `WeldParamControl/WeldParamManager.cs:828`
  - `void MigrateLegacyTorqueTarget(WeldParamConfig config)` — `WeldParamControl/WeldParamManager.cs:844`
  - `void MigrateLegacyTaZeroPoseMm(WeldParamConfig config)` — `WeldParamControl/WeldParamManager.cs:891`
  - `void NormalizeTaForceDirection(WeldParamConfig config, MontionManager manager, DeltaTaHomeConfig taHome)` — `WeldParamControl/WeldParamManager.cs:920`
  - `void HealAlgorithmsConfigKeys(WeldParamConfig config)` — `WeldParamControl/WeldParamManager.cs:954`
  - `void SwitchConfig(string configId)` — `WeldParamControl/WeldParamManager.cs:1022`
  - `void SaveCurrentAutoParam()` — `WeldParamControl/WeldParamManager.cs:1039`
  - `void SaveCurrentProfile()` — `WeldParamControl/WeldParamManager.cs:1074`
  - ` AddConfig(string configId)` — `WeldParamControl/WeldParamManager.cs:1098`
  - `bool DeleteConfig(string configId)` — `WeldParamControl/WeldParamManager.cs:1132`
  - `void ReloadCurrentParamValues()` — `WeldParamControl/WeldParamManager.cs:1154`
  - `void DeserializeOrNull(string json)` — `WeldParamControl/WeldParamManager.cs:1178`
  - `void LoadProfileIntoLookupTable(string identityInfo)` — `WeldParamControl/WeldParamManager.cs:1198`
  - `void LoadAlgorithmsConfig()` — `WeldParamControl/WeldParamManager.cs:1252`
  - `void SaveAlgorithmsConfig()` — `WeldParamControl/WeldParamManager.cs:1290`
  - `void LoadAlgorithmsZone()` — `WeldParamControl/WeldParamManager.cs:1307`
  - `void SaveAlgorithmsZone(WeldParamConfig.AlgorithmsZone zone)` — `WeldParamControl/WeldParamManager.cs:1326`
  - `void FeedLatestSeamWidth()` — `WeldParamControl/WeldParamManager.cs:1395`
  - `void TriggerAdjustment()` — `WeldParamControl/WeldParamManager.cs:1417`
  - `void BuildLookupTable(AutoParam autoParam)` — `WeldParamControl/WeldParamManager.cs:1431`
  - `bool TryLookup(double seamWidth, double laserPower, double feedSpeed, double robotSpeed)` — `WeldParamControl/WeldParamManager.cs:1442`
  - `bool TryLookupSwingWidth(double seamWidth, double swingWidth)` — `WeldParamControl/WeldParamManager.cs:1452`
  - `bool TryLookupSwingFrequency(double seamWidth, int frequencyHz)` — `WeldParamControl/WeldParamManager.cs:1462`
  - `bool TryGetParamOutputAt(double robotX, double laserPower, double feedSpeed, double robotSpeed, double spotWidth, double seamWidth)` — `WeldParamControl/WeldParamManager.cs:1476`
  - `void Reset()` — `WeldParamControl/WeldParamManager.cs:1490`
  - `PVTPoint[] FeedSeamTracking(LineLaserSeamResult result, double measuredFps, double axisCurrentPos)` — `WeldParamControl/WeldParamManager.cs:1503`
  - `PVTPoint[] TickSeamTracking()` — `WeldParamControl/WeldParamManager.cs:1510`
  - `PVTPoint[] DrainSeamTracking()` — `WeldParamControl/WeldParamManager.cs:1517`
  - `void ResetSeamTracking(= "")` — `WeldParamControl/WeldParamManager.cs:1523`
  - `void ResetTrackingForWeldStart(= "")` — `WeldParamControl/WeldParamManager.cs:1534`
  - `void ClearSeamTrackingAlarm()` — `WeldParamControl/WeldParamManager.cs:1544`
  - `void OnSeamLaserResult(LineLaserSeamResult result, double axisPosMm)` — `WeldParamControl/WeldParamManager.cs:1553`
  - `void IsIngestPaused()` — `WeldParamControl/WeldParamManager.cs:1567`
  - `void BeginSeamTrackingCorrection()` — `WeldParamControl/WeldParamManager.cs:1574`
  - `bool TryGetSeamTrackingCorrectionMm(double correctionMm)` — `WeldParamControl/WeldParamManager.cs:1589`
  - `bool TryGetSeamTrackingTargetY(double robotX, double robotY, double targetY)` — `WeldParamControl/WeldParamManager.cs:1601`
  - `bool TryGetSeamTrackingRequiredVelocityMmPerS(double robotVxMmPerS, double requiredVelMmPerS)` — `WeldParamControl/WeldParamManager.cs:1611`
- 构造（1）：
  - `WeldParamManager()` — `WeldParamControl/WeldParamManager.cs:496`
- 属性（68）：
  - `WeldParamManager Instance { get; set; }` — `WeldParamControl/WeldParamManager.cs:33`
  - `RobotWeldData RobotWeldData { get; set; }` — `WeldParamControl/WeldParamManager.cs:152`
  - `AutoParam CurrentAutoParam { get; set; }` — `WeldParamControl/WeldParamManager.cs:155`
  - `AutoParamHelper AutoParamHelper { get; set; }` — `WeldParamControl/WeldParamManager.cs:158`
  - `ConfigHelper ConfigHelper { get; set; }` — `WeldParamControl/WeldParamManager.cs:161`
  - `TaLaCurveConfig TaLaCurve { get; set; }` — `WeldParamControl/WeldParamManager.cs:164`
  - `double AnchorSpotMm { get; set; }` — `WeldParamControl/WeldParamManager.cs:167`
  - `string CurrentAutoParamId { get; set; }` — `WeldParamControl/WeldParamManager.cs:170`
  - `double SegmentDistanceMm { get; set; }` — `WeldParamControl/WeldParamManager.cs:181`
  - `double FeedforwardSafetyFactor { get; set; }` — `WeldParamControl/WeldParamManager.cs:188`
  - `bool EnableMonotonicConstraint { get; set; }` — `WeldParamControl/WeldParamManager.cs:195`
  - `double CurrentRobotX { get; set; }` — `WeldParamControl/WeldParamManager.cs:202`
  - `double CurrentRobotY { get; set; }` — `WeldParamControl/WeldParamManager.cs:225`
  - `int MaxConsecutiveFailures { get; set; }` — `WeldParamControl/WeldParamManager.cs:248`
  - `int ConsecutiveFailureCount { get; set; }` — `WeldParamControl/WeldParamManager.cs:255`
  - `int TotalExecuteCount { get; set; }` — `WeldParamControl/WeldParamManager.cs:258`
  - `double FeedSpeedOutput { get; set; }` — `WeldParamControl/WeldParamManager.cs:261`
  - `double RobotSpeedOutput { get; set; }` — `WeldParamControl/WeldParamManager.cs:264`
  - `double LaserPowerOutput { get; set; }` — `WeldParamControl/WeldParamManager.cs:267`
  - `double SpotWidthOutput { get; set; }` — `WeldParamControl/WeldParamManager.cs:270`
  - `double CurrentSeamWidth { get; set; }` — `WeldParamControl/WeldParamManager.cs:273`
  - `double CurrentRobotZ { get; set; }` — `WeldParamControl/WeldParamManager.cs:276`
  - `double CurrentRobotSpeed { get; set; }` — `WeldParamControl/WeldParamManager.cs:279`
  - `double NoValueDistanceMm { get; set; }` — `WeldParamControl/WeldParamManager.cs:282`
  - `string NoValueSource { get; set; }` — `WeldParamControl/WeldParamManager.cs:288`
  - `double PoseAgeMs { get; set; }` — `WeldParamControl/WeldParamManager.cs:294`
  - `double LastSeamPointY { get; set; }` — `WeldParamControl/WeldParamManager.cs:307`
  - `double LastSeamPointZ { get; set; }` — `WeldParamControl/WeldParamManager.cs:310`
  - `int CurrentLaserJobId { get; set; }` — `WeldParamControl/WeldParamManager.cs:313`
  - `List<double> SeamWidthList { get; set; }` — `WeldParamControl/WeldParamManager.cs:316`
  - `Dictionary<double, double> LaserPowerDic { get; set; }` — `WeldParamControl/WeldParamManager.cs:323`
  - `Dictionary<double, double> FeedSpeedDic { get; set; }` — `WeldParamControl/WeldParamManager.cs:330`
  - `Dictionary<double, double> RobotSpeedDic { get; set; }` — `WeldParamControl/WeldParamManager.cs:337`
  - `Dictionary<double, double> SpotWidthDic { get; set; }` — `WeldParamControl/WeldParamManager.cs:344`
  - `Dictionary<double, double> SwingWidthDic { get; set; }` — `WeldParamControl/WeldParamManager.cs:351`
  - `Dictionary<double, int> SwingFrequencyDic { get; set; }` — `WeldParamControl/WeldParamManager.cs:358`
  - `ChartVar ContourChart { get; set; }` — `WeldParamControl/WeldParamManager.cs:365`
  - `ChartVar LaserPowerChart { get; set; }` — `WeldParamControl/WeldParamManager.cs:368`
  - `ChartVar FeedSpeedChart { get; set; }` — `WeldParamControl/WeldParamManager.cs:371`
  - `ChartVar SeamWidthChart { get; set; }` — `WeldParamControl/WeldParamManager.cs:374`
  - `ChartVar RobotSpeedChart { get; set; }` — `WeldParamControl/WeldParamManager.cs:377`
  - `long AdjustmentOutputVersion { get; set; }` — `WeldParamControl/WeldParamManager.cs:380`
  - `WeldParamConfig AlgorithmsConfig { get; set; }` — `WeldParamControl/WeldParamManager.cs:383`
  - `SeamTrackingMode TrackingMode { get; set; }` — `WeldParamControl/WeldParamManager.cs:386`
  - `bool IsCspTrackingMode { get; set; }` — `WeldParamControl/WeldParamManager.cs:396`
  - `bool HasRobotPose { get; set; }` — `WeldParamControl/WeldParamManager.cs:399`
  - `double SeamTrackingCorrectionMm { get; set; }` — `WeldParamControl/WeldParamManager.cs:416`
  - `double SeamTrackingLastCorrectionMm { get; set; }` — `WeldParamControl/WeldParamManager.cs:419`
  - `double SeamTrackingLastFeatureY { get; set; }` — `WeldParamControl/WeldParamManager.cs:422`
  - `double SeamTrackingPathYOffset { get; set; }` — `WeldParamControl/WeldParamManager.cs:425`
  - `double SeamTrackingLastMapKeyX { get; set; }` — `WeldParamControl/WeldParamManager.cs:428`
  - `double SeamTrackingLastMapEntryY { get; set; }` — `WeldParamControl/WeldParamManager.cs:431`
  - `bool SeamTrackingHasMapEntry { get; set; }` — `WeldParamControl/WeldParamManager.cs:434`
  - `bool SeamTrackingHasAlarm { get; set; }` — `WeldParamControl/WeldParamManager.cs:437`
  - `string SeamTrackingAlarmReason { get; set; }` — `WeldParamControl/WeldParamManager.cs:440`
  - `int ParamCacheCount { get; set; }` — `WeldParamControl/WeldParamManager.cs:1356`
  - `int SeamTrackingMapPointCount { get; set; }` — `WeldParamControl/WeldParamManager.cs:1359`
  - `int SeamTrackingOutlierCount { get; set; }` — `WeldParamControl/WeldParamManager.cs:1362`
  - `int SeamTrackingInvalidFrameCount { get; set; }` — `WeldParamControl/WeldParamManager.cs:1365`
  - `int SeamTrackingSmoothSkipCount { get; set; }` — `WeldParamControl/WeldParamManager.cs:1368`
  - `int SeamTrackingJitterRejectCount { get; set; }` — `WeldParamControl/WeldParamManager.cs:1371`
  - `int SeamTrackingTargetStepRejectCount { get; set; }` — `WeldParamControl/WeldParamManager.cs:1374`
  - `double SeamTrackingAxisAtMeasureMm { get; set; }` — `WeldParamControl/WeldParamManager.cs:1377`
  - `double SeamTrackingRobotX { get; set; }` — `WeldParamControl/WeldParamManager.cs:1380`
  - `bool SeamTrackingHasFault { get; set; }` — `WeldParamControl/WeldParamManager.cs:1383`
  - `string SeamTrackingFaultReason { get; set; }` — `WeldParamControl/WeldParamManager.cs:1386`
  - `double SeamTrackingLastDeviation { get; set; }` — `WeldParamControl/WeldParamManager.cs:1389`
  - `double SeamTrackingLastTargetPos { get; set; }` — `WeldParamControl/WeldParamManager.cs:1392`

## WeldParamMontionControl

- 签名：`public class WeldParamMontionControl`
- 位置：`WeldParamControl/WeldParamData.cs:245`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 方法（1）：
  - `void Reset()` — `WeldParamControl/WeldParamData.cs:257`

## WeldParamProfileAudit

- 签名：`public static class WeldParamProfileAudit`
- 位置：`WeldParamControl/WeldParamProfileAudit.cs:11`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 方法（8）：
  - `void DiffDict(string scene, string label, Dictionary<double, double> before, Dictionary<double, double> after)` — `WeldParamControl/WeldParamProfileAudit.cs:21`
  - `void Emit(string scene, string name, string before, string after)` — `WeldParamControl/WeldParamProfileAudit.cs:62`
  - `void Display(string value)` — `WeldParamControl/WeldParamProfileAudit.cs:71`
  - `void Num(double value)` — `WeldParamControl/WeldParamProfileAudit.cs:79`
  - `void FormatWidth(double value)` — `WeldParamControl/WeldParamProfileAudit.cs:87`
  - `void ParseList(string json)` — `WeldParamControl/WeldParamProfileAudit.cs:95`
  - `void ParseDict(string json)` — `WeldParamControl/WeldParamProfileAudit.cs:116`
  - `void LogProfileDiff(string scene, WeldAutoParamProfile before, WeldAutoParamProfile after)` — `WeldParamControl/WeldParamProfileAudit.cs:138`

## WeldProcessCompletedEventArgs

- 签名：`public class WeldProcessCompletedEventArgs : EventArgs`
- 位置：`WeldParamControl/WeldParamData.cs:531`
- 命名空间：`AdaWeldSystem.WeldParamControl`
- 构造（1）：
  - `WeldProcessCompletedEventArgs(double robotX, ChartVar contourData, double laserPower, double feedSpeed, double seamWidth, double robotSpeed, bool success)` — `WeldParamControl/WeldParamData.cs:557`
- 属性（8）：
  - `double RobotX { get; set; }` — `WeldParamControl/WeldParamData.cs:534`
  - `ChartVar ContourData { get; set; }` — `WeldParamControl/WeldParamData.cs:537`
  - `double LaserPower { get; set; }` — `WeldParamControl/WeldParamData.cs:540`
  - `double FeedSpeed { get; set; }` — `WeldParamControl/WeldParamData.cs:543`
  - `double SeamWidth { get; set; }` — `WeldParamControl/WeldParamData.cs:546`
  - `double RobotSpeed { get; set; }` — `WeldParamControl/WeldParamData.cs:549`
  - `bool Success { get; set; }` — `WeldParamControl/WeldParamData.cs:552`
  - `DateTime Timestamp { get; set; }` — `WeldParamControl/WeldParamData.cs:555`

## XLPoint

- 签名：`private class XLPoint`
- 位置：`WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:593`
- 命名空间：`AdaWeldSystem.WeldParamControl.Algorithms`
- 构造（1）：
  - `XLPoint(double robotXL, double laserPower, double feedSpeed, double robotSpeed, double spotWidth, double seamWidth)` — `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs:620`

## 相关页面

- [[architecture/CodeMap]]
