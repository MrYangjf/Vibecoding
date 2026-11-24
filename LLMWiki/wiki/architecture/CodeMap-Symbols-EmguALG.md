---
title: CodeMap-Symbols-EmguALG — 代码地图·符号签名层·EmguALG（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-EmguALG — EmguALG 的类型与签名

> **一句话**：模块 `EmguALG` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> 视觉算法五层：EmguALG.Core / RealtimeMonitor / LineLaserContour
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.EmguALG.Core` | 7 | 18 | 图像算法 · 核心算子 | [[modules/EmguALG]] | ADR-022 |
| `AdaWeldSystem.EmguALG.Manager` | 3 | 3 | 图像算法 · Manager 唯一口 | [[modules/EmguALG]] | ADR-022 |
| `AdaWeldSystem.EmguALG.RealtimeMonitor.Playback` | 3 | 3 | — | — | — |
| `AdaWeldSystem.EmguALG.RealtimeMonitor.WeldQuality` | 3 | 3 | 图像算法 · 焊缝质量检测 | [[modules/EmguALG]] | ADR-022 |
| `AdaWeldSystem.EmguALG.RealtimeMonitor.WireFeedDistance` | 3 | 3 | 图像算法 · 光丝对中（领域包装） | [[modules/EmguALG]] | ADR-022/056 |
| `AdaWeldSystem.EmguALG.LineLaserContour` | 2 | 4 | 图像算法 · 线激光轮廓 | [[modules/EmguALG]] | ADR-022/024 |
| `AdaWeldSystem.EmguALG.Roi` | 2 | 2 | — | — | — |

| 项 | 值 |
|---|---|
| 类型数 | 36 |
| 方法数 | 272 |

## 章节导航

- [AlgorithmBase](#AlgorithmBase)
- [AlgorithmCompletedEventArgs](#AlgorithmCompletedEventArgs)
- [AlgorithmManager](#AlgorithmManager)
- [AlgorithmResult](#AlgorithmResult)
- [AlgorithmResultStore](#AlgorithmResultStore)
- [EdgeConfig](#EdgeConfig)
- [EdgeDetectionStage](#EdgeDetectionStage)
- [FeatureExtractionStage](#FeatureExtractionStage)
- [FilterConfig](#FilterConfig)
- [FilterStage](#FilterStage)
- [ImageAlgorithm](#ImageAlgorithm)
- [ImageRoi](#ImageRoi)
- [ImageRoiTool](#ImageRoiTool)
- [LineLaserCalibrationData](#LineLaserCalibrationData)
- [LineLaserConfig](#LineLaserConfig)
- [LineLaserContourAlgorithm](#LineLaserContourAlgorithm)
- [LineLaserProfileData](#LineLaserProfileData)
- [MorphologyConfig](#MorphologyConfig)
- [MorphologyStage](#MorphologyStage)
- [PipelineConfig](#PipelineConfig)
- [PlaybackAlgorithm](#PlaybackAlgorithm)
- [PlaybackFileInfo](#PlaybackFileInfo)
- [PlaybackScanResult](#PlaybackScanResult)
- [PreprocessConfig](#PreprocessConfig)
- [RangeAttribute](#RangeAttribute)
- [StageBase](#StageBase)
- [TemplateMatchStage](#TemplateMatchStage)
- [UnitAttribute](#UnitAttribute)
- [ViewGeometry](#ViewGeometry)
- [WeldDefect](#WeldDefect)
- [WeldQualityAlgorithm](#WeldQualityAlgorithm)
- [WeldQualityConfig](#WeldQualityConfig)
- [WeldQualityResult](#WeldQualityResult)
- [WireFeedConfig](#WireFeedConfig)
- [WireFeedDistanceAlgorithm](#WireFeedDistanceAlgorithm)
- [WireFeedResult](#WireFeedResult)

## AlgorithmBase

- 签名：`public abstract class AlgorithmBase`
- 位置：`EmguALG/Core/AlgorithmBase.cs:8`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（6）：
  - `void SaveToIni(INIFile ini)` — `EmguALG/Core/AlgorithmBase.cs:16`
  - `void LoadFromIni(INIFile ini)` — `EmguALG/Core/AlgorithmBase.cs:19`
  - `void ExecuteCore(Mat input)` — `EmguALG/Core/AlgorithmBase.cs:22`
  - `void Preprocess(Mat src, PreprocessConfig cfg)` — `EmguALG/Core/AlgorithmBase.cs:31`
  - `void FindContours(Mat bin, double thr)` — `EmguALG/Core/AlgorithmBase.cs:98`
  - ` Execute(Mat input)` — `EmguALG/Core/AlgorithmBase.cs:107`
- 属性（1）：
  - `string AlgorithmName { get; set; }` — `EmguALG/Core/AlgorithmBase.cs:13`

## AlgorithmCompletedEventArgs

- 签名：`public class AlgorithmCompletedEventArgs : EventArgs`
- 位置：`EmguALG/Manager/AlgorithmCompletedEventArgs.cs:6`
- 命名空间：`AdaWeldSystem.EmguALG.Manager`
- 属性（4）：
  - `string AlgorithmName { get; set; }` — `EmguALG/Manager/AlgorithmCompletedEventArgs.cs:9`
  - `bool Success { get; set; }` — `EmguALG/Manager/AlgorithmCompletedEventArgs.cs:12`
  - `double ElapsedMilliseconds { get; set; }` — `EmguALG/Manager/AlgorithmCompletedEventArgs.cs:15`
  - `string ErrorMessage { get; set; }` — `EmguALG/Manager/AlgorithmCompletedEventArgs.cs:18`

## AlgorithmManager

- 签名：`public sealed class AlgorithmManager`
- 位置：`EmguALG/Manager/AlgorithmManager.cs:19`
- 命名空间：`AdaWeldSystem.EmguALG.Manager`
- 方法（10）：
  - ` DetectWireFeed(Mat image)` — `EmguALG/Manager/AlgorithmManager.cs:127`
  - ` DetectWeldQuality(Mat image)` — `EmguALG/Manager/AlgorithmManager.cs:138`
  - `void DrawSpotMark(Mat frame, int x, int y)` — `EmguALG/Manager/AlgorithmManager.cs:150`
  - ` GetLatestWireFeed(int version)` — `EmguALG/Manager/AlgorithmManager.cs:165`
  - ` GetLatestQuality(int version)` — `EmguALG/Manager/AlgorithmManager.cs:173`
  - `void ApplyConfig()` — `EmguALG/Manager/AlgorithmManager.cs:179`
  - ` CreateEmptyPipelineConfig()` — `EmguALG/Manager/AlgorithmManager.cs:190`
  - `void Load()` — `EmguALG/Manager/AlgorithmManager.cs:196`
  - `void Save()` — `EmguALG/Manager/AlgorithmManager.cs:229`
  - `void RaiseCompleted(string algorithmName, bool success, double elapsedMs, string error)` — `EmguALG/Manager/AlgorithmManager.cs:263`
- 构造（1）：
  - `AlgorithmManager()` — `EmguALG/Manager/AlgorithmManager.cs:105`
- 属性（7）：
  - `AlgorithmManager Instance { get; set; }` — `EmguALG/Manager/AlgorithmManager.cs:53`
  - `WireFeedConfig WireFeed { get; set; }` — `EmguALG/Manager/AlgorithmManager.cs:59`
  - `WeldQualityConfig Quality { get; set; }` — `EmguALG/Manager/AlgorithmManager.cs:65`
  - `ILineLaserContourAlgorithm LineLaserContour { get; set; }` — `EmguALG/Manager/AlgorithmManager.cs:71`
  - `PlaybackAlgorithm Playback { get; set; }` — `EmguALG/Manager/AlgorithmManager.cs:77`
  - `int WireFeedVersion { get; set; }` — `EmguALG/Manager/AlgorithmManager.cs:83`
  - `int QualityVersion { get; set; }` — `EmguALG/Manager/AlgorithmManager.cs:89`

## AlgorithmResult

- 签名：`public class AlgorithmResult`
- 位置：`EmguALG/Core/AlgorithmResult.cs:6`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 构造（1）：
  - `AlgorithmResult()` — `EmguALG/Core/AlgorithmResult.cs:20`
- 属性（4）：
  - `bool Success { get; set; }` — `EmguALG/Core/AlgorithmResult.cs:9`
  - `double ElapsedMs { get; set; }` — `EmguALG/Core/AlgorithmResult.cs:12`
  - `string ErrorMessage { get; set; }` — `EmguALG/Core/AlgorithmResult.cs:15`
  - `string Algorithm { get; set; }` — `EmguALG/Core/AlgorithmResult.cs:18`

## AlgorithmResultStore

- 签名：`public sealed class AlgorithmResultStore : IResultStore<T>`
- 位置：`EmguALG/Manager/AlgorithmResultStore.cs:8`
- 命名空间：`AdaWeldSystem.EmguALG.Manager`
- 方法（2）：
  - ` GetLatest(int version)` — `EmguALG/Manager/AlgorithmResultStore.cs:33`
  - `void Publish(TResult result)` — `EmguALG/Manager/AlgorithmResultStore.cs:44`
- 属性（1）：
  - `int Version { get; set; }` — `EmguALG/Manager/AlgorithmResultStore.cs:21`

## EdgeConfig

- 签名：`public class EdgeConfig`
- 位置：`EmguALG/Core/PreprocessConfig.cs:89`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（3）：
  - `Dictionary<string, string> GetParameters()` — `EmguALG/Core/PreprocessConfig.cs:104`
  - `void SetParameters(string> p)` — `EmguALG/Core/PreprocessConfig.cs:112`
  - ` Clone()` — `EmguALG/Core/PreprocessConfig.cs:125`
- 构造（1）：
  - `EdgeConfig()` — `EmguALG/Core/PreprocessConfig.cs:96`

## EdgeDetectionStage

- 签名：`public class EdgeDetectionStage : StageBase`
- 位置：`EmguALG/Core/Stages.cs:155`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（2）：
  - `void GetDefaultParametersForOperation(Enum op)` — `EmguALG/Core/Stages.cs:184`
  - ` Clone()` — `EmguALG/Core/Stages.cs:206`
- 属性（2）：
  - `bool Enabled { get; set; }` — `EmguALG/Core/Stages.cs:161`
  - `EdgeDetectionOperation Operation { get; set; }` — `EmguALG/Core/Stages.cs:168`

## FeatureExtractionStage

- 签名：`public class FeatureExtractionStage : StageBase`
- 位置：`EmguALG/Core/Stages.cs:218`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（2）：
  - `void GetDefaultParametersForOperation(Enum op)` — `EmguALG/Core/Stages.cs:255`
  - ` Clone()` — `EmguALG/Core/Stages.cs:274`
- 属性（2）：
  - `FeatureExtractionOperation Operation { get; set; }` — `EmguALG/Core/Stages.cs:224`
  - `ChainApproxMethod ApproximationMethod { get; set; }` — `EmguALG/Core/Stages.cs:239`

## FilterConfig

- 签名：`public class FilterConfig`
- 位置：`EmguALG/Core/PreprocessConfig.cs:8`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（3）：
  - `Dictionary<string, string> GetParameters()` — `EmguALG/Core/PreprocessConfig.cs:24`
  - `void SetParameters(string> p)` — `EmguALG/Core/PreprocessConfig.cs:33`
  - ` Clone()` — `EmguALG/Core/PreprocessConfig.cs:46`
- 构造（1）：
  - `FilterConfig()` — `EmguALG/Core/PreprocessConfig.cs:15`

## FilterStage

- 签名：`public class FilterStage : StageBase`
- 位置：`EmguALG/Core/Stages.cs:38`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（2）：
  - `void GetDefaultParametersForOperation(Enum op)` — `EmguALG/Core/Stages.cs:67`
  - ` Clone()` — `EmguALG/Core/Stages.cs:94`
- 属性（2）：
  - `bool Enabled { get; set; }` — `EmguALG/Core/Stages.cs:44`
  - `FilterOperation Operation { get; set; }` — `EmguALG/Core/Stages.cs:51`

## ImageAlgorithm

- 签名：`public static class ImageAlgorithm`
- 位置：`EmguALG/Core/ImageAlgorithm.cs:15`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（29）：
  - ` GaussianBlur(Mat image, = 5, = 1.5)` — `EmguALG/Core/ImageAlgorithm.cs:19`
  - ` MedianBlur(Mat image, = 5)` — `EmguALG/Core/ImageAlgorithm.cs:27`
  - ` MeanBlur(Mat image, = 5)` — `EmguALG/Core/ImageAlgorithm.cs:36`
  - ` BilateralFilter(Mat image, = 9, = 75, = 75)` — `EmguALG/Core/ImageAlgorithm.cs:45`
  - ` Sharpen(Mat image)` — `EmguALG/Core/ImageAlgorithm.cs:53`
  - ` CannyEdge(Mat image, = 50, = 150, = 3)` — `EmguALG/Core/ImageAlgorithm.cs:72`
  - ` GradientEdge(Mat image, = 3)` — `EmguALG/Core/ImageAlgorithm.cs:81`
  - ` LaplacianEdge(Mat image, = 3)` — `EmguALG/Core/ImageAlgorithm.cs:96`
  - ` RobertsEdge(Mat image)` — `EmguALG/Core/ImageAlgorithm.cs:107`
  - ` Dilate(Mat image, = 3)` — `EmguALG/Core/ImageAlgorithm.cs:130`
  - ` Erode(Mat image, = 3)` — `EmguALG/Core/ImageAlgorithm.cs:139`
  - ` MorphologyOpen(Mat image, = 3)` — `EmguALG/Core/ImageAlgorithm.cs:148`
  - ` MorphologyClose(Mat image, = 3)` — `EmguALG/Core/ImageAlgorithm.cs:157`
  - ` FindContours(Mat image, = 127, = ChainApproxMethod.ChainApproxSimple)` — `EmguALG/Core/ImageAlgorithm.cs:171`
  - ` DrawContours(Mat image, VectorOfVectorOfPoint contours, = 2)` — `EmguALG/Core/ImageAlgorithm.cs:185`
  - ` ExtractSkeleton(Mat image, = 127, = 100)` — `EmguALG/Core/ImageAlgorithm.cs:204`
  - `double CalculateSeamWidth(VectorOfPoint contour)` — `EmguALG/Core/ImageAlgorithm.cs:238`
  - `double CalculateSeamArea(VectorOfPoint contour)` — `EmguALG/Core/ImageAlgorithm.cs:247`
  - ` CalculateWeldPoint(VectorOfPoint contour)` — `EmguALG/Core/ImageAlgorithm.cs:254`
  - ` TemplateMatch(Mat image, Mat template, TemplateMatchingType method, bool showResult, string resultInfo)` — `EmguALG/Core/ImageAlgorithm.cs:266`
  - `void ConvertToGray(Mat image)` — `EmguALG/Core/ImageAlgorithm.cs:345`
  - `void ConvertToBinary(Mat image, double threshold, double maxVal)` — `EmguALG/Core/ImageAlgorithm.cs:353`
  - `void DrawTextOnImage(Mat image, string text, Point origin, MCvScalar color)` — `EmguALG/Core/ImageAlgorithm.cs:361`
  - `void DrawTextOnImage(Mat image, string text)` — `EmguALG/Core/ImageAlgorithm.cs:375`
  - ` DrawPointsDefaultRange(List<PointF> points)` — `EmguALG/Core/ImageAlgorithm.cs:384`
  - `void DrawHorizontalBoundsDefaultRange(Mat image, float upperBound, float lowerBound)` — `EmguALG/Core/ImageAlgorithm.cs:425`
  - `void PrepareOverlayMat(Mat image)` — `EmguALG/Core/ImageAlgorithm.cs:445`
  - ` DetectPreWeldAlignment(Mat image, WireFeedConfig config)` — `EmguALG/Core/ImageAlgorithm.cs:456`
  - ` DetectWeldQuality(Mat image, WeldQualityConfig config)` — `EmguALG/Core/ImageAlgorithm.cs:565`

## ImageRoi

- 签名：`public sealed class ImageRoi`
- 位置：`EmguALG/Roi/ImageRoi.cs:6`
- 命名空间：`AdaWeldSystem.EmguALG.Roi`
- 方法（5）：
  - ` ClampTo(int imageWidth, int imageHeight)` — `EmguALG/Roi/ImageRoi.cs:55`
  - ` MapToSource(int roiX, int roiY)` — `EmguALG/Roi/ImageRoi.cs:79`
  - ` MapToSource(Point roiPoint)` — `EmguALG/Roi/ImageRoi.cs:87`
  - ` MapToRoi(int sourceX, int sourceY)` — `EmguALG/Roi/ImageRoi.cs:96`
  - ` MapToRoi(Point sourcePoint)` — `EmguALG/Roi/ImageRoi.cs:104`
- 属性（8）：
  - `bool Enabled { get; set; }` — `EmguALG/Roi/ImageRoi.cs:11`
  - `int X { get; set; }` — `EmguALG/Roi/ImageRoi.cs:14`
  - `int Y { get; set; }` — `EmguALG/Roi/ImageRoi.cs:17`
  - `int Width { get; set; }` — `EmguALG/Roi/ImageRoi.cs:20`
  - `int Height { get; set; }` — `EmguALG/Roi/ImageRoi.cs:23`
  - `Rectangle Bounds { get; set; }` — `EmguALG/Roi/ImageRoi.cs:26`
  - `bool IsValid { get; set; }` — `EmguALG/Roi/ImageRoi.cs:36`
  - `bool IsActive { get; set; }` — `EmguALG/Roi/ImageRoi.cs:42`

## ImageRoiTool

- 签名：`public static class ImageRoiTool`
- 位置：`EmguALG/Roi/ImageRoiTool.cs:13`
- 命名空间：`AdaWeldSystem.EmguALG.Roi`
- 方法（5）：
  - ` Load()` — `EmguALG/Roi/ImageRoiTool.cs:33`
  - `void Save(ImageRoi roi)` — `EmguALG/Roi/ImageRoiTool.cs:49`
  - `void Resolve(Mat source, ImageRoi roi)` — `EmguALG/Roi/ImageRoiTool.cs:77`
  - ` Crop(Mat source, ImageRoi roi)` — `EmguALG/Roi/ImageRoiTool.cs:89`
  - ` ApplyMask(Mat source, ImageRoi roi)` — `EmguALG/Roi/ImageRoiTool.cs:109`

## LineLaserCalibrationData

- 签名：`public sealed class LineLaserCalibrationData`
- 位置：`EmguALG/LineLaserContour/LineLaserContourData.cs:81`
- 命名空间：`AdaWeldSystem.EmguALG.LineLaserContour`
- 方法（1）：
  - `void Copy2(float[] source)` — `EmguALG/LineLaserContour/LineLaserContourData.cs:141`
- 构造（2）：
  - `LineLaserCalibrationData()` — `EmguALG/LineLaserContour/LineLaserContourData.cs:108`
  - `LineLaserCalibrationData(float[] center, float[] leftTop, float[] rightTop, float[] leftBottom, float[] rightBottom)` — `EmguALG/LineLaserContour/LineLaserContourData.cs:123`
- 属性（6）：
  - `bool HasData { get; set; }` — `EmguALG/LineLaserContour/LineLaserContourData.cs:86`
  - `float[] Center { get; set; }` — `EmguALG/LineLaserContour/LineLaserContourData.cs:89`
  - `float[] LeftTopCorner { get; set; }` — `EmguALG/LineLaserContour/LineLaserContourData.cs:92`
  - `float[] RightTopCorner { get; set; }` — `EmguALG/LineLaserContour/LineLaserContourData.cs:95`
  - `float[] LeftBottomCorner { get; set; }` — `EmguALG/LineLaserContour/LineLaserContourData.cs:98`
  - `float[] RightBottomCorner { get; set; }` — `EmguALG/LineLaserContour/LineLaserContourData.cs:101`

## LineLaserConfig

- 签名：`public class LineLaserConfig`
- 位置：`EmguALG/Core/PreprocessConfig.cs:132`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（10）：
  - `void Log(string message, MessageLevel level)` — `LineLaserCam/LineLaserConfig.cs:96`
  - `void ReadInt(XdocumentReaderWriter reader, string path, int def)` — `LineLaserCam/LineLaserConfig.cs:106`
  - `void ReadDouble(XdocumentReaderWriter reader, string path, double def)` — `LineLaserCam/LineLaserConfig.cs:117`
  - `void ReadBool(XdocumentReaderWriter reader, string path, bool def)` — `LineLaserCam/LineLaserConfig.cs:128`
  - `void SanitizeSeconds(int seconds)` — `LineLaserCam/LineLaserConfig.cs:138`
  - ` Clone()` — `EmguALG/Core/PreprocessConfig.cs:145`
  - `void WriteConfigNodes(XdocumentReaderWriter reader)` — `LineLaserCam/LineLaserConfig.cs:152`
  - `void LoadConfig()` — `LineLaserCam/LineLaserConfig.cs:176`
  - `void LoadConfig(bool allowHeal)` — `LineLaserCam/LineLaserConfig.cs:183`
  - `void SaveConfig()` — `LineLaserCam/LineLaserConfig.cs:232`
- 构造（2）：
  - `LineLaserConfig()` — `LineLaserCam/LineLaserConfig.cs:73`
  - `LineLaserConfig()` — `EmguALG/Core/PreprocessConfig.cs:138`
- 属性（11）：
  - `string ConfigFileName { get; set; }` — `LineLaserCam/LineLaserConfig.cs:36`
  - `LineLaserKind DefaultKind { get; set; }` — `LineLaserCam/LineLaserConfig.cs:39`
  - `bool AutoConnectOnStart { get; set; }` — `LineLaserCam/LineLaserConfig.cs:42`
  - `string SensorIp { get; set; }` — `LineLaserCam/LineLaserConfig.cs:45`
  - `int LineLaserDataFrequencyHz { get; set; }` — `LineLaserCam/LineLaserConfig.cs:48`
  - `bool DisplayEnabled { get; set; }` — `LineLaserCam/LineLaserConfig.cs:51`
  - `double DisplayFps { get; set; }` — `LineLaserCam/LineLaserConfig.cs:54`
  - `bool ConvertMatEnabled { get; set; }` — `LineLaserCam/LineLaserConfig.cs:57`
  - `int DataStableTimeoutSeconds { get; set; }` — `LineLaserCam/LineLaserConfig.cs:60`
  - `int WaitWorkingTimeoutSeconds { get; set; }` — `LineLaserCam/LineLaserConfig.cs:63`
  - `int FirstResultTimeoutSeconds { get; set; }` — `LineLaserCam/LineLaserConfig.cs:66`

## LineLaserContourAlgorithm

- 签名：`public class LineLaserContourAlgorithm : ILineLaserContourAlgorithm`
- 位置：`EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:10`
- 命名空间：`AdaWeldSystem.EmguALG.LineLaserContour`
- 方法（12）：
  - `void EnsureCanvas()` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:37`
  - `void UpdateMatFromCanvas()` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:47`
  - `void CalcTwoLineCrossPoint(PointF line1P1, PointF line1P2, PointF line2P1, PointF line2P2)` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:67`
  - `void ToPixel(PointF origin, float rate, float[] mm)` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:86`
  - `void BuildViewGeometry(LineLaserCalibrationData calib, bool hasCalib, LineLaserProfileData pts, int count)` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:97`
  - `void DrawFallbackGrid(Graphics g, ViewGeometry view)` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:194`
  - `void DrawCalibrationBackdrop(Graphics g, ViewGeometry view)` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:211`
  - `void DrawProfile(Graphics g, LineLaserProfileData pts, int count, ViewGeometry view, bool hasCalib, LineLaserSeamFeature result)` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:245`
  - `void DrawMillimeterGrid(Graphics g, ViewGeometry view)` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:278`
  - `void DrawRangeLabels(Graphics g, ViewGeometry view)` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:320`
  - ` Render(LineLaserProfileData profile, LineLaserCalibrationData calib, LineLaserSeamFeature result)` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:345`
  - `void Dispose()` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:373`
- 属性（1）：
  - `Mat LastMat { get; set; }` — `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:30`

## LineLaserProfileData

- 签名：`public sealed class LineLaserProfileData`
- 位置：`EmguALG/LineLaserContour/LineLaserContourData.cs:4`
- 命名空间：`AdaWeldSystem.EmguALG.LineLaserContour`
- 方法（2）：
  - `void SetCount(int count)` — `EmguALG/LineLaserContour/LineLaserContourData.cs:63`
  - `void Clear()` — `EmguALG/LineLaserContour/LineLaserContourData.cs:72`
- 构造（2）：
  - `LineLaserProfileData()` — `EmguALG/LineLaserContour/LineLaserContourData.cs:42`
  - `LineLaserProfileData(double[] ys, double[] zs)` — `EmguALG/LineLaserContour/LineLaserContourData.cs:50`
- 属性（3）：
  - `double[] Ys { get; set; }` — `EmguALG/LineLaserContour/LineLaserContourData.cs:23`
  - `double[] Zs { get; set; }` — `EmguALG/LineLaserContour/LineLaserContourData.cs:29`
  - `int Count { get; set; }` — `EmguALG/LineLaserContour/LineLaserContourData.cs:35`

## MorphologyConfig

- 签名：`public class MorphologyConfig`
- 位置：`EmguALG/Core/PreprocessConfig.cs:53`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（3）：
  - `Dictionary<string, string> GetParameters()` — `EmguALG/Core/PreprocessConfig.cs:66`
  - `void SetParameters(string> p)` — `EmguALG/Core/PreprocessConfig.cs:73`
  - ` Clone()` — `EmguALG/Core/PreprocessConfig.cs:82`
- 构造（1）：
  - `MorphologyConfig()` — `EmguALG/Core/PreprocessConfig.cs:59`

## MorphologyStage

- 签名：`public class MorphologyStage : StageBase`
- 位置：`EmguALG/Core/Stages.cs:106`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（2）：
  - `void GetDefaultParametersForOperation(Enum op)` — `EmguALG/Core/Stages.cs:135`
  - ` Clone()` — `EmguALG/Core/Stages.cs:143`
- 属性（2）：
  - `bool Enabled { get; set; }` — `EmguALG/Core/Stages.cs:112`
  - `MorphologyOperation Operation { get; set; }` — `EmguALG/Core/Stages.cs:119`

## PipelineConfig

- 签名：`public class PipelineConfig`
- 位置：`EmguALG/Core/Stages.cs:335`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（1）：
  - ` Clone()` — `EmguALG/Core/Stages.cs:377`
- 构造（1）：
  - `PipelineConfig()` — `EmguALG/Core/Stages.cs:355`
- 属性（5）：
  - `FilterStage Filter { get; set; }` — `EmguALG/Core/Stages.cs:339`
  - `MorphologyStage Morphology { get; set; }` — `EmguALG/Core/Stages.cs:342`
  - `EdgeDetectionStage EdgeDetection { get; set; }` — `EmguALG/Core/Stages.cs:345`
  - `FeatureExtractionStage FeatureExtraction { get; set; }` — `EmguALG/Core/Stages.cs:348`
  - `TemplateMatchStage TemplateMatch { get; set; }` — `EmguALG/Core/Stages.cs:351`

## PlaybackAlgorithm

- 签名：`public sealed class PlaybackAlgorithm : IDisposable`
- 位置：`EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:14`
- 命名空间：`AdaWeldSystem.EmguALG.RealtimeMonitor.Playback`
- 方法（22）：
  - `void CollectRangeFileRows(string root, DateTime start, DateTime end, string rangeText, CancellationToken token)` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:124`
  - `void StartThumbnailLoader(List<PlaybackFileInfo> files)` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:193`
  - `void LoadThumbnail(string path)` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:222`
  - `void CancelScan()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:252`
  - `void LoadRange(string root, DateTime start, DateTime end)` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:269`
  - `string PlayFile(string path)` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:319`
  - `string TogglePlayPause()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:359`
  - `void CycleSlow()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:385`
  - `void CycleFast()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:398`
  - `void SeekToFrame(int frameIndex)` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:412`
  - `void SeekBySeconds(double seconds)` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:420`
  - `void Stop()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:432`
  - `void Reset()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:440`
  - `void PlayTimerTick(object state)` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:454`
  - `void TargetPlayFrameLocked()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:499`
  - `void RebasePlayClockLocked()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:505`
  - `void SeekToFrameLocked(int frameIndex)` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:514`
  - `void FinishPlaybackLocked()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:538`
  - `void StopLocked()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:549`
  - `void RaiseProgress()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:569`
  - `void RaiseStateChanged()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:585`
  - `void Dispose()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:603`
- 构造（1）：
  - `PlaybackAlgorithm()` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:108`
- 属性（3）：
  - `bool HasSource { get; set; }` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:86`
  - `bool IsPlaying { get; set; }` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:92`
  - `double Speed { get; set; }` — `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs:98`

## PlaybackFileInfo

- 签名：`public class PlaybackFileInfo`
- 位置：`EmguALG/RealtimeMonitor/Playback/PlaybackFileInfo.cs:6`
- 命名空间：`AdaWeldSystem.EmguALG.RealtimeMonitor.Playback`
- 属性（5）：
  - `string FileName { get; set; }` — `EmguALG/RealtimeMonitor/Playback/PlaybackFileInfo.cs:9`
  - `string FullPath { get; set; }` — `EmguALG/RealtimeMonitor/Playback/PlaybackFileInfo.cs:12`
  - `string Modified { get; set; }` — `EmguALG/RealtimeMonitor/Playback/PlaybackFileInfo.cs:15`
  - `string Size { get; set; }` — `EmguALG/RealtimeMonitor/Playback/PlaybackFileInfo.cs:18`
  - `Bitmap Thumbnail { get; set; }` — `EmguALG/RealtimeMonitor/Playback/PlaybackFileInfo.cs:21`

## PlaybackScanResult

- 签名：`public class PlaybackScanResult`
- 位置：`EmguALG/RealtimeMonitor/Playback/PlaybackScanResult.cs:6`
- 命名空间：`AdaWeldSystem.EmguALG.RealtimeMonitor.Playback`
- 属性（3）：
  - `List<PlaybackFileInfo> Files { get; set; }` — `EmguALG/RealtimeMonitor/Playback/PlaybackScanResult.cs:9`
  - `string Caption { get; set; }` — `EmguALG/RealtimeMonitor/Playback/PlaybackScanResult.cs:12`
  - `string Error { get; set; }` — `EmguALG/RealtimeMonitor/Playback/PlaybackScanResult.cs:15`

## PreprocessConfig

- 签名：`public class PreprocessConfig`
- 位置：`EmguALG/Core/PreprocessConfig.cs:157`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（3）：
  - ` Clone()` — `EmguALG/Core/PreprocessConfig.cs:173`
  - `void SaveToIni(INIFile ini)` — `EmguALG/Core/PreprocessConfig.cs:188`
  - `void LoadFromIni(INIFile ini)` — `EmguALG/Core/PreprocessConfig.cs:203`
- 构造（1）：
  - `PreprocessConfig()` — `EmguALG/Core/PreprocessConfig.cs:165`

## RangeAttribute

- 签名：`public class RangeAttribute : Attribute`
- 位置：`EmguALG/Core/RangeAttribute.cs:6`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 构造（1）：
  - `RangeAttribute(double min, double max)` — `EmguALG/Core/RangeAttribute.cs:12`
- 属性（2）：
  - `double Min { get; set; }` — `EmguALG/Core/RangeAttribute.cs:9`
  - `double Max { get; set; }` — `EmguALG/Core/RangeAttribute.cs:10`

## StageBase

- 签名：`public abstract class StageBase : INotifyPropertyChanged`
- 位置：`EmguALG/Core/Stages.cs:10`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（3）：
  - `void OnPropertyChanged(string name)` — `EmguALG/Core/Stages.cs:14`
  - `void GetDefaultParametersForOperation(Enum operation)` — `EmguALG/Core/Stages.cs:17`
  - `void ResetParametersForOperation(Enum newOp)` — `EmguALG/Core/Stages.cs:30`
- 属性（1）：
  - `Dictionary<string, string> Parameters { get; set; }` — `EmguALG/Core/Stages.cs:19`

## TemplateMatchStage

- 签名：`public class TemplateMatchStage : StageBase`
- 位置：`EmguALG/Core/Stages.cs:286`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 方法（2）：
  - `void GetDefaultParametersForOperation(Enum op)` — `EmguALG/Core/Stages.cs:315`
  - ` Clone()` — `EmguALG/Core/Stages.cs:323`
- 属性（2）：
  - `TemplateMatchOperation Operation { get; set; }` — `EmguALG/Core/Stages.cs:292`
  - `bool ShowResult { get; set; }` — `EmguALG/Core/Stages.cs:307`

## UnitAttribute

- 签名：`public class UnitAttribute : Attribute`
- 位置：`EmguALG/Core/UnitAttribute.cs:6`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 构造（1）：
  - `UnitAttribute(string unit)` — `EmguALG/Core/UnitAttribute.cs:11`
- 属性（1）：
  - `string Unit { get; set; }` — `EmguALG/Core/UnitAttribute.cs:9`

## ViewGeometry

- 签名：`private class ViewGeometry`
- 位置：`EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs:394`
- 命名空间：`AdaWeldSystem.EmguALG.LineLaserContour`
- 成员：（无）

## WeldDefect

- 签名：`public class WeldDefect`
- 位置：`EmguALG/Core/ImageAlgorithm.cs:648`
- 命名空间：`AdaWeldSystem.EmguALG.Core`
- 属性（3）：
  - `WeldDefectType Type { get; set; }` — `EmguALG/Core/ImageAlgorithm.cs:650`
  - `Rectangle Bounds { get; set; }` — `EmguALG/Core/ImageAlgorithm.cs:651`
  - `double Area { get; set; }` — `EmguALG/Core/ImageAlgorithm.cs:652`

## WeldQualityAlgorithm

- 签名：`public sealed class WeldQualityAlgorithm : IAlgorithm<T>, IConfigurableAlgorithm<T>`
- 位置：`EmguALG/RealtimeMonitor/WeldQuality/WeldQualityAlgorithm.cs:10`
- 命名空间：`AdaWeldSystem.EmguALG.RealtimeMonitor.WeldQuality`
- 方法（2）：
  - `void SetConfig(WeldQualityConfig config)` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityAlgorithm.cs:52`
  - ` Execute(Mat input)` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityAlgorithm.cs:60`
- 构造（1）：
  - `WeldQualityAlgorithm()` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityAlgorithm.cs:41`
- 属性（3）：
  - `string AlgorithmName { get; set; }` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityAlgorithm.cs:22`
  - `bool IsBusy { get; set; }` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityAlgorithm.cs:28`
  - `WeldQualityConfig Config { get; set; }` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityAlgorithm.cs:31`

## WeldQualityConfig

- 签名：`public class WeldQualityConfig`
- 位置：`EmguALG/RealtimeMonitor/WeldQuality/WeldQualityConfig.cs:4`
- 命名空间：`AdaWeldSystem.EmguALG.RealtimeMonitor.WeldQuality`
- 构造（1）：
  - `WeldQualityConfig()` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityConfig.cs:10`
- 属性（1）：
  - `double PassScore { get; set; }` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityConfig.cs:7`

## WeldQualityResult

- 签名：`public class WeldQualityResult : AlgorithmResult`
- 位置：`EmguALG/RealtimeMonitor/WeldQuality/WeldQualityResult.cs:8`
- 命名空间：`AdaWeldSystem.EmguALG.RealtimeMonitor.WeldQuality`
- 构造（1）：
  - `WeldQualityResult()` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityResult.cs:26`
- 属性（5）：
  - `int DefectCount { get; set; }` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityResult.cs:11`
  - `List<WeldDefect> Defects { get; set; }` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityResult.cs:14`
  - `double QualityScore { get; set; }` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityResult.cs:17`
  - `bool Pass { get; set; }` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityResult.cs:20`
  - `Mat OverlayMat { get; set; }` — `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityResult.cs:23`

## WireFeedConfig

- 签名：`public class WireFeedConfig`
- 位置：`EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:4`
- 命名空间：`AdaWeldSystem.EmguALG.RealtimeMonitor.WireFeedDistance`
- 构造（1）：
  - `WireFeedConfig()` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:43`
- 属性（12）：
  - `double ToleranceX { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:7`
  - `double ToleranceY { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:10`
  - `double CenterWarnMm { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:13`
  - `double CenterFailMm { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:16`
  - `double PixelMmScale { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:19`
  - `double SpotRefX { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:22`
  - `double SpotRefY { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:25`
  - `double WireStickoutTargetMm { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:28`
  - `bool StickoutAxisHorizontal { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:31`
  - `int StickoutSign { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:34`
  - `double WireFeedCompGain { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:37`
  - `bool WireAnomalyCutWire { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs:40`

## WireFeedDistanceAlgorithm

- 签名：`public sealed class WireFeedDistanceAlgorithm : IAlgorithm<T>, IConfigurableAlgorithm<T>`
- 位置：`EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedDistanceAlgorithm.cs:10`
- 命名空间：`AdaWeldSystem.EmguALG.RealtimeMonitor.WireFeedDistance`
- 方法（2）：
  - `void SetConfig(WireFeedConfig config)` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedDistanceAlgorithm.cs:52`
  - ` Execute(Mat input)` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedDistanceAlgorithm.cs:60`
- 构造（1）：
  - `WireFeedDistanceAlgorithm()` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedDistanceAlgorithm.cs:41`
- 属性（3）：
  - `string AlgorithmName { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedDistanceAlgorithm.cs:22`
  - `bool IsBusy { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedDistanceAlgorithm.cs:28`
  - `WireFeedConfig Config { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedDistanceAlgorithm.cs:31`

## WireFeedResult

- 签名：`public class WireFeedResult : AlgorithmResult`
- 位置：`EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:21`
- 命名空间：`AdaWeldSystem.EmguALG.RealtimeMonitor.WireFeedDistance`
- 属性（14）：
  - `double OffsetX { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:24`
  - `double OffsetY { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:27`
  - `double AngleDeg { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:30`
  - `bool Aligned { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:33`
  - `double DevXMm { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:36`
  - `double DevYMm { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:39`
  - `double WireStickoutDevMm { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:42`
  - `double LateralDevMm { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:45`
  - `WireAlignGrade Grade { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:48`
  - `bool WireMatched { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:51`
  - `bool WireHeadAdhesion { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:54`
  - `PointF LaserCenter { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:57`
  - `PointF WireCenter { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:60`
  - `Mat OverlayMat { get; set; }` — `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs:63`

## 相关页面

- [[architecture/CodeMap]]
