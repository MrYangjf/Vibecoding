---
title: CodeMap-Symbols-PCLOperate — 代码地图·符号签名层·PCLOperate（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-PCLOperate — PCLOperate 的类型与签名

> **一句话**：模块 `PCLOperate` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> PLC 交互
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.PCLOperate.Render` | 3 | 5 | 点云 · 三维渲染与曲面重建 | [[modules/Comm]] | ADR-035 |
| `AdaWeldSystem.PCLOperate.DataIO` | 2 | 2 | 点云 · 读写 | [[modules/Comm]] | ADR-035 |
| `AdaWeldSystem.PCLOperate.Models` | 1 | 1 | PLC · 数据模型 | （无专属模块页，见功能描述） | ADR-025 |

| 项 | 值 |
|---|---|
| 类型数 | 8 |
| 方法数 | 128 |

## 章节导航

- [PointCloudData](#PointCloudData)
- [PointCloudReader](#PointCloudReader)
- [PointCloudViewer](#PointCloudViewer)
- [PointCloudWriter](#PointCloudWriter)
- [RenderConfig](#RenderConfig)
- [SpatialIndex](#SpatialIndex)
- [SurfaceTriangulator](#SurfaceTriangulator)
- [VectorMath](#VectorMath)

## PointCloudData

- 签名：`public class PointCloudData`
- 位置：`PCLOperate/Models/PointCloudData.cs:8`
- 命名空间：`AdaWeldSystem.PCLOperate.Models`
- 方法（16）：
  - `void AddPoint(float x, float y, float z)` — `PCLOperate/Models/PointCloudData.cs:43`
  - `void AddPoint(float x, float y, float z)` — `PCLOperate/Models/PointCloudData.cs:44`
  - `void AddPoint(float x, float y, float z, byte r, byte g, byte b, byte a)` — `PCLOperate/Models/PointCloudData.cs:49`
  - `void AddPoint(float x, float y, float z, byte r, byte g, byte b, = 255)` — `PCLOperate/Models/PointCloudData.cs:50`
  - `void AddPoint(Point3D point)` — `PCLOperate/Models/PointCloudData.cs:55`
  - `void AddPoint(Point3D point)` — `PCLOperate/Models/PointCloudData.cs:56`
  - `void AddPoint(Point3DColor point)` — `PCLOperate/Models/PointCloudData.cs:61`
  - `void AddPoint(Point3DColor point)` — `PCLOperate/Models/PointCloudData.cs:62`
  - `void Clear()` — `PCLOperate/Models/PointCloudData.cs:67`
  - `void Clear()` — `PCLOperate/Models/PointCloudData.cs:68`
  - `void GetBounds(float minX, float minY, float minZ, float maxX, float maxY, float maxZ)` — `PCLOperate/Models/PointCloudData.cs:74`
  - `void GetBounds(float minX, float minY, float minZ, float maxX, float maxY, float maxZ)` — `PCLOperate/Models/PointCloudData.cs:75`
  - `void GetCenter()` — `PCLOperate/Models/PointCloudData.cs:113`
  - ` GetCenter()` — `PCLOperate/Models/PointCloudData.cs:114`
  - `void ToColoredPoints(byte defaultR, byte defaultG, byte defaultB)` — `PCLOperate/Models/PointCloudData.cs:122`
  - `List<Point3DColor> ToColoredPoints(= 255, = 255, = 255)` — `PCLOperate/Models/PointCloudData.cs:123`
- 构造（2）：
  - `PointCloudData()` — `PCLOperate/Models/PointCloudData.cs:13`
  - `PointCloudData(PointCloudData other)` — `PCLOperate/Models/PointCloudData.cs:21`
- 属性（4）：
  - `IReadOnlyList<Point3D> Points { get; set; }` — `PCLOperate/Models/PointCloudData.cs:31`
  - `IReadOnlyList<Point3DColor> ColoredPoints { get; set; }` — `PCLOperate/Models/PointCloudData.cs:34`
  - `bool HasColor { get; set; }` — `PCLOperate/Models/PointCloudData.cs:37`
  - `int PointCount { get; set; }` — `PCLOperate/Models/PointCloudData.cs:40`

## PointCloudReader

- 签名：`public static class PointCloudReader`
- 位置：`PCLOperate/DataIO/PointCloudReader.cs:11`
- 命名空间：`AdaWeldSystem.PCLOperate.DataIO`
- 方法（8）：
  - `void TraverseSceneNode(SceneNode node, PointCloudData data)` — `PCLOperate/DataIO/PointCloudReader.cs:15`
  - `void GetPropertyIndex(int x, int y, int z, int r, int g, int b)` — `PCLOperate/DataIO/PointCloudReader.cs:59`
  - ` LoadFromFile(string filePath)` — `PCLOperate/DataIO/PointCloudReader.cs:73`
  - ` LoadFromTxt(string filePath, = false)` — `PCLOperate/DataIO/PointCloudReader.cs:104`
  - ` LoadFromPly(string filePath)` — `PCLOperate/DataIO/PointCloudReader.cs:145`
  - ` LoadFromObj(string filePath)` — `PCLOperate/DataIO/PointCloudReader.cs:260`
  - ` LoadSceneFromFile(string filePath)` — `PCLOperate/DataIO/PointCloudReader.cs:305`
  - ` LoadFromPlyWithAssimp(string filePath)` — `PCLOperate/DataIO/PointCloudReader.cs:325`

## PointCloudViewer

- 签名：`public class PointCloudViewer : IDisposable`
- 位置：`PCLOperate/Render/PointCloudViewer.cs:15`
- 命名空间：`AdaWeldSystem.PCLOperate.Render`
- 方法（28）：
  - `void InitializeViewport()` — `PCLOperate/Render/PointCloudViewer.cs:78`
  - `void FitViewToPointCloud()` — `PCLOperate/Render/PointCloudViewer.cs:102`
  - `void BuildAndShowPointCloud(float pointSize)` — `PCLOperate/Render/PointCloudViewer.cs:179`
  - `void ClearPointCloud()` — `PCLOperate/Render/PointCloudViewer.cs:284`
  - `void ShowSurfaceMesh(HelixToolkit.SharpDX.MeshGeometry3D meshGeometry, MediaColor color)` — `PCLOperate/Render/PointCloudViewer.cs:294`
  - `void ClearSurface()` — `PCLOperate/Render/PointCloudViewer.cs:318`
  - `void ClearScene()` — `PCLOperate/Render/PointCloudViewer.cs:328`
  - `void FitViewToScene(SceneNode rootNode)` — `PCLOperate/Render/PointCloudViewer.cs:338`
  - `void JetColorMap(float t)` — `PCLOperate/Render/PointCloudViewer.cs:446`
  - `void InitializeCamera()` — `PCLOperate/Render/PointCloudViewer.cs:480`
  - `void LoadPointCloud(PointCloudData data, = 2f)` — `PCLOperate/Render/PointCloudViewer.cs:506`
  - `void ReducePointCloud(float ratio, = 2f)` — `PCLOperate/Render/PointCloudViewer.cs:529`
  - `void GenerateSurface(= 0.5f, = 30, = 1)` — `PCLOperate/Render/PointCloudViewer.cs:549`
  - `void GenerateSurfaceBallPivoting(= 0.5f, = 1, = 20)` — `PCLOperate/Render/PointCloudViewer.cs:568`
  - `void GenerateAlphaShape(= 1.0f, = 1, = 15)` — `PCLOperate/Render/PointCloudViewer.cs:588`
  - `void GenerateDelaunay(= 0.3f, = 5f, = 1, = 15)` — `PCLOperate/Render/PointCloudViewer.cs:609`
  - `void GeneratePoisson(= 8, = 1.0f, = 0)` — `PCLOperate/Render/PointCloudViewer.cs:629`
  - `void GenerateMLS(= 0.5f, = 1, = 12)` — `PCLOperate/Render/PointCloudViewer.cs:649`
  - `void ClearAll()` — `PCLOperate/Render/PointCloudViewer.cs:665`
  - `void SetPointSize(float pointSize)` — `PCLOperate/Render/PointCloudViewer.cs:684`
  - `void SetZColorEnabled(bool enabled, = 2f)` — `PCLOperate/Render/PointCloudViewer.cs:694`
  - `void LoadScene(HelixToolkitScene scene)` — `PCLOperate/Render/PointCloudViewer.cs:707`
  - `void SetPointColor(MediaColor color)` — `PCLOperate/Render/PointCloudViewer.cs:731`
  - `void SetSurfaceColor(MediaColor color)` — `PCLOperate/Render/PointCloudViewer.cs:749`
  - `void SetCameraMode(CameraControlMode mode)` — `PCLOperate/Render/PointCloudViewer.cs:759`
  - `void ResetCameraToCenter()` — `PCLOperate/Render/PointCloudViewer.cs:795`
  - `System.Numerics.Vector3 GetModelCenter()` — `PCLOperate/Render/PointCloudViewer.cs:940`
  - `void Dispose()` — `PCLOperate/Render/PointCloudViewer.cs:979`
- 构造（2）：
  - `PointCloudViewer()` — `PCLOperate/Render/PointCloudViewer.cs:47`
  - `PointCloudViewer(Viewport3DX viewport)` — `PCLOperate/Render/PointCloudViewer.cs:55`
- 属性（4）：
  - `Viewport3DX Viewport { get; set; }` — `PCLOperate/Render/PointCloudViewer.cs:62`
  - `PointCloudData CurrentData { get; set; }` — `PCLOperate/Render/PointCloudViewer.cs:70`
  - `bool IsSurfaceVisible { get; set; }` — `PCLOperate/Render/PointCloudViewer.cs:73`
  - `bool IsPointCloudVisible { get; set; }` — `PCLOperate/Render/PointCloudViewer.cs:76`

## PointCloudWriter

- 签名：`public static class PointCloudWriter`
- 位置：`PCLOperate/DataIO/PointCloudWriter.cs:11`
- 命名空间：`AdaWeldSystem.PCLOperate.DataIO`
- 方法（4）：
  - `void SaveToFile(PointCloudData data, string filePath)` — `PCLOperate/DataIO/PointCloudWriter.cs:16`
  - `void SaveToTxt(PointCloudData data, string filePath, = true)` — `PCLOperate/DataIO/PointCloudWriter.cs:40`
  - `void SaveToPly(PointCloudData data, string filePath)` — `PCLOperate/DataIO/PointCloudWriter.cs:72`
  - `void SaveToObj(PointCloudData data, string filePath)` — `PCLOperate/DataIO/PointCloudWriter.cs:120`

## RenderConfig

- 签名：`public static class RenderConfig`
- 位置：`PCLOperate/Render/RenderConfig.cs:27`
- 命名空间：`AdaWeldSystem.PCLOperate.Render`
- 方法（7）：
  - `void Log(string message, MessageLevel level)` — `PCLOperate/Render/RenderConfig.cs:34`
  - `void EnsureInitialized()` — `PCLOperate/Render/RenderConfig.cs:92`
  - `void LoadFromIniInternal()` — `PCLOperate/Render/RenderConfig.cs:209`
  - `void LoadFromIni()` — `PCLOperate/Render/RenderConfig.cs:254`
  - `void SaveToIni()` — `PCLOperate/Render/RenderConfig.cs:276`
  - `string GetAlgorithmName(SurfaceRenderAlgorithm algorithm)` — `PCLOperate/Render/RenderConfig.cs:346`
  - `void ResetToDefaults()` — `PCLOperate/Render/RenderConfig.cs:368`
- 构造（1）：
  - `RenderConfig()` — `PCLOperate/Render/RenderConfig.cs:62`
- 属性（23）：
  - `SurfaceRenderAlgorithm SelectedAlgorithm { get; set; }` — `PCLOperate/Render/RenderConfig.cs:131`
  - `float NeighborSearchRadius { get; set; }` — `PCLOperate/Render/RenderConfig.cs:137`
  - `int NeighborMaxNeighbors { get; set; }` — `PCLOperate/Render/RenderConfig.cs:139`
  - `int NeighborSampleStep { get; set; }` — `PCLOperate/Render/RenderConfig.cs:141`
  - `float BallPivotingRadius { get; set; }` — `PCLOperate/Render/RenderConfig.cs:147`
  - `int BallPivotingSampleStep { get; set; }` — `PCLOperate/Render/RenderConfig.cs:149`
  - `int BallPivotingMaxNeighbors { get; set; }` — `PCLOperate/Render/RenderConfig.cs:151`
  - `float AlphaShapeAlpha { get; set; }` — `PCLOperate/Render/RenderConfig.cs:157`
  - `int AlphaShapeSampleStep { get; set; }` — `PCLOperate/Render/RenderConfig.cs:159`
  - `int AlphaShapeMaxNeighbors { get; set; }` — `PCLOperate/Render/RenderConfig.cs:161`
  - `float DelaunayQualityThreshold { get; set; }` — `PCLOperate/Render/RenderConfig.cs:167`
  - `float DelaunaySearchRadiusMultiplier { get; set; }` — `PCLOperate/Render/RenderConfig.cs:169`
  - `int DelaunaySampleStep { get; set; }` — `PCLOperate/Render/RenderConfig.cs:171`
  - `int DelaunayMaxNeighbors { get; set; }` — `PCLOperate/Render/RenderConfig.cs:173`
  - `int PoissonDepth { get; set; }` — `PCLOperate/Render/RenderConfig.cs:179`
  - `int PoissonSamplesPerNode { get; set; }` — `PCLOperate/Render/RenderConfig.cs:181`
  - `int PoissonMaxCells { get; set; }` — `PCLOperate/Render/RenderConfig.cs:183`
  - `float MlsSearchRadius { get; set; }` — `PCLOperate/Render/RenderConfig.cs:189`
  - `int MlsSampleStep { get; set; }` — `PCLOperate/Render/RenderConfig.cs:191`
  - `int MlsMaxNeighbors { get; set; }` — `PCLOperate/Render/RenderConfig.cs:193`
  - `float PointSize { get; set; }` — `PCLOperate/Render/RenderConfig.cs:199`
  - `bool ZColorEnabled { get; set; }` — `PCLOperate/Render/RenderConfig.cs:201`
  - `float DisplayRatio { get; set; }` — `PCLOperate/Render/RenderConfig.cs:203`

## SpatialIndex

- 签名：`private class SpatialIndex`
- 位置：`PCLOperate/Render/SurfaceTriangulator.cs:833`
- 命名空间：`AdaWeldSystem.PCLOperate.Render`
- 方法（3）：
  - `void GetCell(Vector3 p)` — `PCLOperate/Render/SurfaceTriangulator.cs:874`
  - `List<int> FindNeighbors(int pointIndex, float radius, int maxCount)` — `PCLOperate/Render/SurfaceTriangulator.cs:879`
  - `List<int> FindNeighborsInRadius(Vector3 center, float radius, List<Vector3> allPoints)` — `PCLOperate/Render/SurfaceTriangulator.cs:919`
- 构造（1）：
  - `SpatialIndex(List<Vector3> points, float cellSize)` — `PCLOperate/Render/SurfaceTriangulator.cs:839`

## SurfaceTriangulator

- 签名：`public static class SurfaceTriangulator`
- 位置：`PCLOperate/Render/SurfaceTriangulator.cs:10`
- 命名空间：`AdaWeldSystem.PCLOperate.Render`
- 方法（20）：
  - `HelixToolkit.SharpDX.MeshGeometry3D GenerateSurface(PointCloudData data, = 0.5f, = 30, = 1)` — `PCLOperate/Render/SurfaceTriangulator.cs:20`
  - `HelixToolkit.SharpDX.MeshGeometry3D GenerateSurfaceBallPivoting(PointCloudData data, = 0.5f, = 1, = 20)` — `PCLOperate/Render/SurfaceTriangulator.cs:104`
  - `void IsAlphaShapeValidFast(Vector3 p1, Vector3 p2, Vector3 p3, float alphaSquared)` — `PCLOperate/Render/SurfaceTriangulator.cs:178`
  - `HelixToolkit.SharpDX.MeshGeometry3D GenerateAlphaShape(PointCloudData data, = 1.0f, = 1, = 15)` — `PCLOperate/Render/SurfaceTriangulator.cs:201`
  - `void IsDelaunayValidFast(Vector3 p1, Vector3 p2, Vector3 p3, List<Vector3> allPoints, SpatialIndex spatialIndex)` — `PCLOperate/Render/SurfaceTriangulator.cs:275`
  - `void ComputeTriangleQuality(Vector3 p1, Vector3 p2, Vector3 p3)` — `PCLOperate/Render/SurfaceTriangulator.cs:299`
  - `HelixToolkit.SharpDX.MeshGeometry3D GenerateDelaunay3D(PointCloudData data, = 0.3f, = 5f, = 1, = 15)` — `PCLOperate/Render/SurfaceTriangulator.cs:320`
  - `void EstimateNormalsFast(List<Vector3> points, SpatialIndex spatialIndex)` — `PCLOperate/Render/SurfaceTriangulator.cs:398`
  - `void EstimateNormalFast(List<Vector3> points, int index, List<int> neighbors)` — `PCLOperate/Render/SurfaceTriangulator.cs:411`
  - `HelixToolkit.SharpDX.MeshGeometry3D GeneratePoissonSurface(PointCloudData data, = 8, = 1.0f, = 0)` — `PCLOperate/Render/SurfaceTriangulator.cs:432`
  - `void GenerateLocalSurfacePatch(List<(Vector3 point, Vector3 normal)> localPoints)` — `PCLOperate/Render/SurfaceTriangulator.cs:508`
  - `void GetGridCell(Vector3 p, float minX, float minY, float minZ, float cellSize)` — `PCLOperate/Render/SurfaceTriangulator.cs:576`
  - `void ProjectToPlane(Vector3 point, Vector3 planePoint, Vector3 planeNormal)` — `PCLOperate/Render/SurfaceTriangulator.cs:589`
  - `HelixToolkit.SharpDX.MeshGeometry3D GenerateMLSSurface(PointCloudData data, = 0.5f, = 1, = 12)` — `PCLOperate/Render/SurfaceTriangulator.cs:601`
  - `void FitWeightedPlaneFast(List<Vector3> points, List<float> weights)` — `PCLOperate/Render/SurfaceTriangulator.cs:700`
  - `void ToVector3List(PointCloudData data)` — `PCLOperate/Render/SurfaceTriangulator.cs:727`
  - `void ComputeNormal(Vector3 p1, Vector3 p2, Vector3 p3)` — `PCLOperate/Render/SurfaceTriangulator.cs:734`
  - `void GetTriangleKey(int i, int j, int k)` — `PCLOperate/Render/SurfaceTriangulator.cs:741`
  - `void CanFormTriangle(Vector3 p1, Vector3 p2, Vector3 p3, float ballRadius)` — `PCLOperate/Render/SurfaceTriangulator.cs:747`
  - `void ComputeAverageSpacing(List<Vector3> points)` — `PCLOperate/Render/SurfaceTriangulator.cs:763`

## VectorMath

- 签名：`private static class VectorMath`
- 位置：`PCLOperate/Render/SurfaceTriangulator.cs:789`
- 命名空间：`AdaWeldSystem.PCLOperate.Render`
- 方法（5）：
  - `float Distance(Vector3 a, Vector3 b)` — `PCLOperate/Render/SurfaceTriangulator.cs:791`
  - `float DistanceSquared(Vector3 a, Vector3 b)` — `PCLOperate/Render/SurfaceTriangulator.cs:799`
  - `float Dot(Vector3 a, Vector3 b)` — `PCLOperate/Render/SurfaceTriangulator.cs:807`
  - ` Cross(Vector3 a, Vector3 b)` — `PCLOperate/Render/SurfaceTriangulator.cs:812`
  - ` Normalize(Vector3 v)` — `PCLOperate/Render/SurfaceTriangulator.cs:820`

## 相关页面

- [[architecture/CodeMap]]
