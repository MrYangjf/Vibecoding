---
title: CodeMap-Symbols-ProductFileControl — 代码地图·符号签名层·ProductFileControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-ProductFileControl — ProductFileControl 的类型与签名

> **一句话**：模块 `ProductFileControl` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> 产品记录与追溯 Schema
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.ProductFileControl` | 7 | 14 | 记录 · Manager | [[modules/SQLiteDatabase]] | ADR-031/037 |

| 项 | 值 |
|---|---|
| 类型数 | 14 |
| 方法数 | 203 |

## 章节导航

- [ContourFrameItem](#ContourFrameItem)
- [LineLaserContourRecord](#LineLaserContourRecord)
- [ProductFileRecordManager](#ProductFileRecordManager)
- [ProductRecordBase](#ProductRecordBase)
- [RecordFileStore](#RecordFileStore)
- [RecordFrame](#RecordFrame)
- [RecordItem](#RecordItem)
- [SeamTraceYPoint](#SeamTraceYPoint)
- [SeamTraceYRecord](#SeamTraceYRecord)
- [WeldActionRecord](#WeldActionRecord)
- [WeldParamAdjustItem](#WeldParamAdjustItem)
- [WeldParamControlRecord](#WeldParamControlRecord)
- [WeldResultItem](#WeldResultItem)
- [WeldResultRecord](#WeldResultRecord)

## ContourFrameItem

- 签名：`public class ContourFrameItem : RecordItem`
- 位置：`ProductFileControl/Abstractions/ProductRecordBase.cs:24`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 属性（2）：
  - `PointCloudData PointCloud { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:27`
  - `double RobotX { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:30`

## LineLaserContourRecord

- 签名：`public class LineLaserContourRecord : ProductRecordBase`
- 位置：`ProductFileControl/Records/LineLaserContourRecord.cs:8`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 方法（5）：
  - `void AddPointCloud(PointCloudData pointCloud, = 0.0)` — `ProductFileControl/Records/LineLaserContourRecord.cs:30`
  - `void Persist(RecordItem item)` — `ProductFileControl/Records/LineLaserContourRecord.cs:41`
  - `void OnStart()` — `ProductFileControl/Records/LineLaserContourRecord.cs:55`
  - `void OnStop()` — `ProductFileControl/Records/LineLaserContourRecord.cs:61`
  - `void OnAbort()` — `ProductFileControl/Records/LineLaserContourRecord.cs:67`
- 构造（1）：
  - `LineLaserContourRecord(RecordFileStore store)` — `ProductFileControl/Records/LineLaserContourRecord.cs:20`
- 属性（1）：
  - `string Name { get; set; }` — `ProductFileControl/Records/LineLaserContourRecord.cs:13`

## ProductFileRecordManager

- 签名：`public sealed class ProductFileRecordManager : IDisposable`
- 位置：`ProductFileControl/ProductFileRecordManager.cs:13`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 方法（41）：
  - `void Log(string message, MessageLevel level)` — `ProductFileControl/ProductFileRecordManager.cs:20`
  - `void OnFrameRecordRequested(object sender, WeldFrameRecordEventArgs e)` — `ProductFileControl/ProductFileRecordManager.cs:225`
  - `void OnAdjustmentRecordRequested(object sender, WeldAdjustmentRecordEventArgs e)` — `ProductFileControl/ProductFileRecordManager.cs:248`
  - `void OnAbortRecordRequested(object sender, EventArgs e)` — `ProductFileControl/ProductFileRecordManager.cs:271`
  - `void OnLineLaserFrameReady(object sender, LineLaserResultEventArgs e)` — `ProductFileControl/ProductFileRecordManager.cs:280`
  - `void PickExisting(string sessionDir, string baseName, string dateDir, string ext)` — `ProductFileControl/ProductFileRecordManager.cs:329`
  - `void BeginProductSession(string sn, bool isSimulation)` — `ProductFileControl/ProductFileRecordManager.cs:340`
  - `void EndProductSession(string result, string info)` — `ProductFileControl/ProductFileRecordManager.cs:365`
  - `List<string> GetSessionRecordFiles(DateTime startTime, string sn, string status)` — `ProductFileControl/ProductFileRecordManager.cs:408`
  - `void StartRecording()` — `ProductFileControl/ProductFileRecordManager.cs:428`
  - `void StopRecording()` — `ProductFileControl/ProductFileRecordManager.cs:437`
  - `void AbortRecording()` — `ProductFileControl/ProductFileRecordManager.cs:474`
  - `bool BeginSeamTraceYSession()` — `ProductFileControl/ProductFileRecordManager.cs:483`
  - `void RecordSeamTraceYPoint(double robotX, double mapKeyX, double cspInYt, double cspOutY, double axisY)` — `ProductFileControl/ProductFileRecordManager.cs:500`
  - `List<SeamTraceYPoint> ReadSeamTraceYPoints(string filePath)` — `ProductFileControl/ProductFileRecordManager.cs:509`
  - `void FlushSeamTraceY()` — `ProductFileControl/ProductFileRecordManager.cs:515`
  - `void EndSeamTraceYSession()` — `ProductFileControl/ProductFileRecordManager.cs:521`
  - `void AddFrame(PointCloudData pointCloud)` — `ProductFileControl/ProductFileRecordManager.cs:528`
  - `void AddFrame(PointCloudData pointCloud, double robotX)` — `ProductFileControl/ProductFileRecordManager.cs:537`
  - `void RecordWeldResult(string sn, DateTime startTime, string status, string result, string info)` — `ProductFileControl/ProductFileRecordManager.cs:549`
  - `System.Data.DataTable SelectProductRecords(DateTime date)` — `ProductFileControl/ProductFileRecordManager.cs:567`
  - `System.Data.DataTable SelectProductRecords(DateTime start, DateTime end)` — `ProductFileControl/ProductFileRecordManager.cs:576`
  - `void RecordJobSwitch(int jobId, double robotX, double robotY)` — `ProductFileControl/ProductFileRecordManager.cs:586`
  - `void NormalizeDirectoryPath(string configuredPath, string defaultPath, string displayName)` — `ProductFileControl/ProductFileRecordManager.cs:620`
  - `void LoadConfigFromIni()` — `ProductFileControl/ProductFileRecordManager.cs:632`
  - `void SaveConfigToIni()` — `ProductFileControl/ProductFileRecordManager.cs:650`
  - `string GetDateRecordDirectoryPath(DateTime date)` — `ProductFileControl/ProductFileRecordManager.cs:663`
  - `List<string> SaveRecord(string fileName)` — `ProductFileControl/ProductFileRecordManager.cs:675`
  - `List<RecordFrame> GetAllFrames()` — `ProductFileControl/ProductFileRecordManager.cs:682`
  - `List<WeldActionRecord> GetAllActions()` — `ProductFileControl/ProductFileRecordManager.cs:689`
  - ` GetFramePointCloud(int frameIndex)` — `ProductFileControl/ProductFileRecordManager.cs:697`
  - `bool ParseFromTempFile(string tempFilePath)` — `ProductFileControl/ProductFileRecordManager.cs:705`
  - `List<string> ConvertTempToNormal(string tempFilePath, string outputName)` — `ProductFileControl/ProductFileRecordManager.cs:714`
  - `List<WeldActionRecord> ParsePDatRecords(string filePath)` — `ProductFileControl/ProductFileRecordManager.cs:722`
  - `string ReadPDatFile(string filePath)` — `ProductFileControl/ProductFileRecordManager.cs:730`
  - `List<string> GetTempFiles()` — `ProductFileControl/ProductFileRecordManager.cs:737`
  - `void CleanupExpiredRecords()` — `ProductFileControl/ProductFileRecordManager.cs:743`
  - `List<string> GetRecordFiles()` — `ProductFileControl/ProductFileRecordManager.cs:751`
  - `List<string> GetWeldActionRecordFiles()` — `ProductFileControl/ProductFileRecordManager.cs:758`
  - `List<string> GetWeldActionRecordFiles(DateTime date)` — `ProductFileControl/ProductFileRecordManager.cs:766`
  - `void Dispose()` — `ProductFileControl/ProductFileRecordManager.cs:774`
- 构造（1）：
  - `ProductFileRecordManager()` — `ProductFileControl/ProductFileRecordManager.cs:188`
- 属性（15）：
  - `ProductFileRecordManager Instance { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:31`
  - `bool IsRecording { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:83`
  - `int CurrentFrameIndex { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:89`
  - `int CachedFrameCount { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:95`
  - `string RecordDirectory { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:101`
  - `string TempDirectory { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:120`
  - `string PathFallbackMessage { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:135`
  - `bool UseObfuscation { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:138`
  - `int RetentionDays { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:152`
  - `bool RecordEveryFrame { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:159`
  - `string RecordNamePrefix { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:165`
  - `INIFile ConfigFile { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:172`
  - `string SessionBaseName { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:305`
  - `string ProductSn { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:311`
  - `string SessionStatus { get; set; }` — `ProductFileControl/ProductFileRecordManager.cs:317`

## ProductRecordBase

- 签名：`public abstract class ProductRecordBase : IDisposable`
- 位置：`ProductFileControl/Abstractions/ProductRecordBase.cs:111`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 方法（13）：
  - `void Log(string message, MessageLevel level)` — `ProductFileControl/Abstractions/ProductRecordBase.cs:144`
  - `void EnsureWorker()` — `ProductFileControl/Abstractions/ProductRecordBase.cs:150`
  - `void WorkerLoop()` — `ProductFileControl/Abstractions/ProductRecordBase.cs:166`
  - `void FlushPending()` — `ProductFileControl/Abstractions/ProductRecordBase.cs:187`
  - `void Start()` — `ProductFileControl/Abstractions/ProductRecordBase.cs:212`
  - `void Stop()` — `ProductFileControl/Abstractions/ProductRecordBase.cs:225`
  - `void Abort()` — `ProductFileControl/Abstractions/ProductRecordBase.cs:238`
  - `void Enqueue(RecordItem item)` — `ProductFileControl/Abstractions/ProductRecordBase.cs:252`
  - `void Persist(RecordItem item)` — `ProductFileControl/Abstractions/ProductRecordBase.cs:264`
  - `void OnStart()` — `ProductFileControl/Abstractions/ProductRecordBase.cs:267`
  - `void OnStop()` — `ProductFileControl/Abstractions/ProductRecordBase.cs:272`
  - `void OnAbort()` — `ProductFileControl/Abstractions/ProductRecordBase.cs:277`
  - `void Dispose()` — `ProductFileControl/Abstractions/ProductRecordBase.cs:282`
- 属性（4）：
  - `int FlushTimeoutMs { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:123`
  - `string Name { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:126`
  - `bool IsRecording { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:129`
  - `int PendingCount { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:136`

## RecordFileStore

- 签名：`internal sealed class RecordFileStore`
- 位置：`ProductFileControl/Records/RecordFileStore.cs:26`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 方法（35）：
  - `void EnsureDateRecordDirectory(DateTime date)` — `ProductFileControl/Records/RecordFileStore.cs:112`
  - `void EnsureSessionDirectory(string dateDir, string baseName)` — `ProductFileControl/Records/RecordFileStore.cs:124`
  - `void EnsureDirectoriesExist()` — `ProductFileControl/Records/RecordFileStore.cs:132`
  - `string GetDateRecordDirectoryPath(DateTime date)` — `ProductFileControl/Records/RecordFileStore.cs:147`
  - `void StartSession()` — `ProductFileControl/Records/RecordFileStore.cs:157`
  - `void StopSession()` — `ProductFileControl/Records/RecordFileStore.cs:175`
  - `void AbortSession()` — `ProductFileControl/Records/RecordFileStore.cs:201`
  - `void AddRecord(WeldActionRecord record)` — `ProductFileControl/Records/RecordFileStore.cs:223`
  - `void AddFrame(PointCloudData pointCloud, = 0.0)` — `ProductFileControl/Records/RecordFileStore.cs:236`
  - `void AddProcessRecord(double robotX, double robotY, double robotZ, double robotSpeed, double feedSpeed, double laserPower, double weldWidth, int jobId, double seamPointY, double seamPointZ, = 0.0, = 0.0, = 0.0, = 0, = 0.0)` — `ProductFileControl/Records/RecordFileStore.cs:272`
  - `void AddAdjustRecord(double robotX, double robotY, double robotZ, double robotSpeed, double feedSpeed, double laserPower, double weldWidth, int jobId, double seamPointY, double seamPointZ, string adjustData)` — `ProductFileControl/Records/RecordFileStore.cs:312`
  - `void AddJobSwitchRecord(double robotX, double robotY, double robotZ, double robotSpeed, double feedSpeed, double laserPower, double weldWidth, int jobId, double seamPointY, double seamPointZ, string adjustData)` — `ProductFileControl/Records/RecordFileStore.cs:355`
  - `void SaveFramesToPly(string filePath)` — `ProductFileControl/Records/RecordFileStore.cs:385`
  - `void SaveActionsToPDat(string filePath)` — `ProductFileControl/Records/RecordFileStore.cs:410`
  - `List<string> SaveRecord(string fileName)` — `ProductFileControl/Records/RecordFileStore.cs:440`
  - `void SaveTempFileInternal()` — `ProductFileControl/Records/RecordFileStore.cs:478`
  - `void AppendToTempFile(RecordFrame frame)` — `ProductFileControl/Records/RecordFileStore.cs:516`
  - `bool ParseFromTempFile(string tempFilePath)` — `ProductFileControl/Records/RecordFileStore.cs:549`
  - `List<string> ConvertTempToNormal(string tempFilePath, string outputName)` — `ProductFileControl/Records/RecordFileStore.cs:616`
  - `void WritePointCloudToStream(BinaryWriter writer, PointCloudData data)` — `ProductFileControl/Records/RecordFileStore.cs:648`
  - `void ReadPointCloudFromStream(BinaryReader reader)` — `ProductFileControl/Records/RecordFileStore.cs:681`
  - `void WriteActionToStream(BinaryWriter writer, WeldActionRecord action)` — `ProductFileControl/Records/RecordFileStore.cs:718`
  - `void ReadActionFromStream(BinaryReader reader, int version)` — `ProductFileControl/Records/RecordFileStore.cs:747`
  - `void ClonePointCloud(PointCloudData source, double xOffset)` — `ProductFileControl/Records/RecordFileStore.cs:786`
  - `List<RecordFrame> GetAllFrames()` — `ProductFileControl/Records/RecordFileStore.cs:810`
  - `List<WeldActionRecord> GetAllActions()` — `ProductFileControl/Records/RecordFileStore.cs:825`
  - ` GetFramePointCloud(int frameIndex)` — `ProductFileControl/Records/RecordFileStore.cs:853`
  - `void ObfuscateBytes(byte[] data)` — `ProductFileControl/Records/RecordFileStore.cs:868`
  - `string ReadPDatFile(string filePath)` — `ProductFileControl/Records/RecordFileStore.cs:883`
  - `List<WeldActionRecord> ParsePDatRecords(string filePath)` — `ProductFileControl/Records/RecordFileStore.cs:910`
  - `List<string> GetTempFiles()` — `ProductFileControl/Records/RecordFileStore.cs:975`
  - `List<string> GetRecordFiles()` — `ProductFileControl/Records/RecordFileStore.cs:987`
  - `List<string> GetWeldActionRecordFiles()` — `ProductFileControl/Records/RecordFileStore.cs:999`
  - `List<string> GetWeldActionRecordFiles(DateTime date)` — `ProductFileControl/Records/RecordFileStore.cs:1012`
  - `int CleanupExpiredRecords(int retainDays)` — `ProductFileControl/Records/RecordFileStore.cs:1024`
- 构造（1）：
  - `RecordFileStore(string recordDirectory, string tempDirectory, bool useObfuscation)` — `ProductFileControl/Records/RecordFileStore.cs:51`
- 属性（6）：
  - `bool IsSessionOpen { get; set; }` — `ProductFileControl/Records/RecordFileStore.cs:61`
  - `int CurrentFrameIndex { get; set; }` — `ProductFileControl/Records/RecordFileStore.cs:67`
  - `int CachedFrameCount { get; set; }` — `ProductFileControl/Records/RecordFileStore.cs:73`
  - `string RecordDirectory { get; set; }` — `ProductFileControl/Records/RecordFileStore.cs:85`
  - `string TempDirectory { get; set; }` — `ProductFileControl/Records/RecordFileStore.cs:92`
  - `bool UseObfuscation { get; set; }` — `ProductFileControl/Records/RecordFileStore.cs:99`

## RecordFrame

- 签名：`public class RecordFrame`
- 位置：`ProductFileControl/Records/RecordFileStore.cs:13`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 属性（3）：
  - `int Index { get; set; }` — `ProductFileControl/Records/RecordFileStore.cs:16`
  - `DateTime Timestamp { get; set; }` — `ProductFileControl/Records/RecordFileStore.cs:19`
  - `PointCloudData PointCloud { get; set; }` — `ProductFileControl/Records/RecordFileStore.cs:22`

## RecordItem

- 签名：`public abstract class RecordItem`
- 位置：`ProductFileControl/Abstractions/ProductRecordBase.cs:11`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 构造（1）：
  - `RecordItem()` — `ProductFileControl/Abstractions/ProductRecordBase.cs:17`
- 属性（1）：
  - `DateTime Timestamp { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:14`

## SeamTraceYPoint

- 签名：`public class SeamTraceYPoint`
- 位置：`ProductFileControl/Records/SeamTraceYRecord.cs:10`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 属性（5）：
  - `double RobotX { get; set; }` — `ProductFileControl/Records/SeamTraceYRecord.cs:13`
  - `double MapKeyX { get; set; }` — `ProductFileControl/Records/SeamTraceYRecord.cs:16`
  - `double CspInYt { get; set; }` — `ProductFileControl/Records/SeamTraceYRecord.cs:19`
  - `double CspOutY { get; set; }` — `ProductFileControl/Records/SeamTraceYRecord.cs:22`
  - `double AxisY { get; set; }` — `ProductFileControl/Records/SeamTraceYRecord.cs:25`

## SeamTraceYRecord

- 签名：`public sealed class SeamTraceYRecord`
- 位置：`ProductFileControl/Records/SeamTraceYRecord.cs:29`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 方法（5）：
  - `bool BeginSession(string sessionBaseName)` — `ProductFileControl/Records/SeamTraceYRecord.cs:75`
  - `void RecordPoint(double robotX, double mapKeyX, double cspInYt, double cspOutY, double axisY)` — `ProductFileControl/Records/SeamTraceYRecord.cs:119`
  - `void FlushToFile()` — `ProductFileControl/Records/SeamTraceYRecord.cs:132`
  - `void EndSession()` — `ProductFileControl/Records/SeamTraceYRecord.cs:155`
  - `List<SeamTraceYPoint> ParseFile(string filePath)` — `ProductFileControl/Records/SeamTraceYRecord.cs:170`
- 构造（1）：
  - `SeamTraceYRecord(string recordDirectory)` — `ProductFileControl/Records/SeamTraceYRecord.cs:63`
- 属性（3）：
  - `string RecordDirectory { get; set; }` — `ProductFileControl/Records/SeamTraceYRecord.cs:43`
  - `int BufferedCount { get; set; }` — `ProductFileControl/Records/SeamTraceYRecord.cs:50`
  - `bool IsSessionActive { get; set; }` — `ProductFileControl/Records/SeamTraceYRecord.cs:56`

## WeldActionRecord

- 签名：`public class WeldActionRecord`
- 位置：`ProductFileControl/Records/WeldParamControlRecord.cs:118`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 属性（20）：
  - `int FrameIndex { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:121`
  - `DateTime Timestamp { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:124`
  - `string ActionType { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:127`
  - `double RobotX { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:130`
  - `double RobotY { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:133`
  - `double RobotZ { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:136`
  - `double RobotSpeed { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:139`
  - `double FeedSpeed { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:142`
  - `double LaserPower { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:145`
  - `double WeldWidth { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:148`
  - `int JobId { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:151`
  - `double SeamPointY { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:154`
  - `double SeamPointZ { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:159`
  - `double TaPositionMm { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:162`
  - `double LaPositionMm { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:165`
  - `double GalvoAmplitudeMm { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:168`
  - `int GalvoPatternId { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:171`
  - `double HeadTempC { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:174`
  - `bool AdjustExecuted { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:177`
  - `string AdjustData { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:180`

## WeldParamAdjustItem

- 签名：`public class WeldParamAdjustItem : RecordItem`
- 位置：`ProductFileControl/Abstractions/ProductRecordBase.cs:34`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 属性（18）：
  - `double RobotX { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:37`
  - `double RobotY { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:40`
  - `double RobotZ { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:43`
  - `double RobotSpeed { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:46`
  - `double FeedSpeed { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:49`
  - `double LaserPower { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:52`
  - `double WeldWidth { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:55`
  - `string ActionType { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:58`
  - `int JobId { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:61`
  - `bool AdjustExecuted { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:64`
  - `string AdjustData { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:67`
  - `double SeamPointY { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:70`
  - `double SeamPointZ { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:73`
  - `double TaPositionMm { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:76`
  - `double LaPositionMm { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:79`
  - `double GalvoAmplitudeMm { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:82`
  - `int GalvoPatternId { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:85`
  - `double HeadTempC { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:88`

## WeldParamControlRecord

- 签名：`public class WeldParamControlRecord : ProductRecordBase`
- 位置：`ProductFileControl/Records/WeldParamControlRecord.cs:9`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 方法（5）：
  - `void RecordProcessFrame(WeldParamAdjustItem item)` — `ProductFileControl/Records/WeldParamControlRecord.cs:39`
  - `void RecordAdjustment(WeldParamAdjustItem item)` — `ProductFileControl/Records/WeldParamControlRecord.cs:52`
  - `void RecordJobSwitch(WeldParamAdjustItem item)` — `ProductFileControl/Records/WeldParamControlRecord.cs:66`
  - `void Persist(RecordItem item)` — `ProductFileControl/Records/WeldParamControlRecord.cs:80`
  - `List<WeldActionRecord> GetAllActions()` — `ProductFileControl/Records/WeldParamControlRecord.cs:111`
- 构造（1）：
  - `WeldParamControlRecord(RecordFileStore store)` — `ProductFileControl/Records/WeldParamControlRecord.cs:30`
- 属性（1）：
  - `string Name { get; set; }` — `ProductFileControl/Records/WeldParamControlRecord.cs:23`

## WeldResultItem

- 签名：`public class WeldResultItem : RecordItem`
- 位置：`ProductFileControl/Abstractions/ProductRecordBase.cs:92`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 属性（5）：
  - `string Sn { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:95`
  - `DateTime StartTime { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:98`
  - `string Status { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:101`
  - `string Result { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:104`
  - `string Info { get; set; }` — `ProductFileControl/Abstractions/ProductRecordBase.cs:107`

## WeldResultRecord

- 签名：`public class WeldResultRecord : ProductRecordBase`
- 位置：`ProductFileControl/Records/WeldResultRecord.cs:11`
- 命名空间：`AdaWeldSystem.ProductFileControl`
- 方法（8）：
  - `void Log(string message, MessageLevel level)` — `ProductFileControl/Records/WeldResultRecord.cs:22`
  - `void RecordResult(WeldResultItem item)` — `ProductFileControl/Records/WeldResultRecord.cs:29`
  - `void RecordResult(WeldResultItem item)` — `ProductFileControl/Records/WeldResultRecord.cs:30`
  - `void Persist(RecordItem item)` — `ProductFileControl/Records/WeldResultRecord.cs:37`
  - `void SelectResultTable(DateTime date)` — `ProductFileControl/Records/WeldResultRecord.cs:63`
  - `System.Data.DataTable SelectResultTable(DateTime date)` — `ProductFileControl/Records/WeldResultRecord.cs:64`
  - `void SelectResultTable(DateTime start, DateTime end)` — `ProductFileControl/Records/WeldResultRecord.cs:80`
  - `System.Data.DataTable SelectResultTable(DateTime start, DateTime end)` — `ProductFileControl/Records/WeldResultRecord.cs:81`
- 属性（1）：
  - `string Name { get; set; }` — `ProductFileControl/Records/WeldResultRecord.cs:14`

## 相关页面

- [[architecture/CodeMap]]
