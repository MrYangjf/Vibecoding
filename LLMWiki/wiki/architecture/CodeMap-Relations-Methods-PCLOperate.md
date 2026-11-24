---
title: CodeMap-Relations-Methods-PCLOperate — 代码地图·方法级影响面·PCLOperate（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-PCLOperate — 方法级影响面（低置信 · 调用方在 PCLOperate）

> **一句话**：**调用方位于 `PCLOperate` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 42 |
| 调用点数 | 42 |

## 章节导航

- [BuildAndShowPointCloud](#BuildAndShowPointCloud)
- [CanFormTriangle](#CanFormTriangle)
- [Clear](#Clear)
- [ClearAll](#ClearAll)
- [ClearPointCloud](#ClearPointCloud)
- [ClearScene](#ClearScene)
- [ClearSurface](#ClearSurface)
- [ComputeAverageSpacing](#ComputeAverageSpacing)
- [ComputeNormal](#ComputeNormal)
- [ComputeTriangleQuality](#ComputeTriangleQuality)
- [EnsureInitialized](#EnsureInitialized)
- [EstimateNormalFast](#EstimateNormalFast)
- [EstimateNormalsFast](#EstimateNormalsFast)
- [FitViewToPointCloud](#FitViewToPointCloud)
- [FitViewToScene](#FitViewToScene)
- [FitWeightedPlaneFast](#FitWeightedPlaneFast)
- [GenerateLocalSurfacePatch](#GenerateLocalSurfacePatch)
- [GetBounds](#GetBounds)
- [GetCell](#GetCell)
- [GetGridCell](#GetGridCell)
- [GetModelCenter](#GetModelCenter)
- [GetPropertyIndex](#GetPropertyIndex)
- [GetTriangleKey](#GetTriangleKey)
- [InitializeCamera](#InitializeCamera)
- [InitializeViewport](#InitializeViewport)
- [IsAlphaShapeValidFast](#IsAlphaShapeValidFast)
- [IsDelaunayValidFast](#IsDelaunayValidFast)
- [JetColorMap](#JetColorMap)
- [LoadFromIniInternal](#LoadFromIniInternal)
- [LoadFromObj](#LoadFromObj)
- [LoadFromPly](#LoadFromPly)
- [LoadFromTxt](#LoadFromTxt)
- [Log](#Log)
- [ProjectToPlane](#ProjectToPlane)
- [ResetCameraToCenter](#ResetCameraToCenter)
- [SaveToIni](#SaveToIni)
- [SaveToObj](#SaveToObj)
- [SaveToPly](#SaveToPly)
- [SaveToTxt](#SaveToTxt)
- [ShowSurfaceMesh](#ShowSurfaceMesh)
- [ToVector3List](#ToVector3List)
- [TraverseSceneNode](#TraverseSceneNode)

## BuildAndShowPointCloud

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [700, 541, 517]

## CanFormTriangle

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [139]

## Clear

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Models/PointCloudData.cs` — 行 [19]

## ClearAll

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [981, 713, 509, 66]

## ClearPointCloud

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [668, 654, 634, 614, 593, 573, 554, 184]

## ClearScene

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [674]

## ClearSurface

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [671, 534, 297]

## ComputeAverageSpacing

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [401, 333]

## ComputeNormal

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [756, 668, 361, 305, 238, 189, 141, 63]

## ComputeTriangleQuality

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [358]

## EnsureInitialized

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/RenderConfig.cs` — 行 [88]

## EstimateNormalFast

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [406]

## EstimateNormalsFast

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [439]

## FitViewToPointCloud

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [520]

## FitViewToScene

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [727]

## FitWeightedPlaneFast

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [625]

## GenerateLocalSurfacePatch

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [477]

## GetBounds

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Models/PointCloudData.cs` — 行 [115]

## GetCell

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [886, 864]

## GetGridCell

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [460]

## GetModelCenter

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [797]

## GetPropertyIndex

> 1 处调用 / 1 个调用方文件

- `PCLOperate/DataIO/PointCloudReader.cs` — 行 [199, 193, 187, 182, 179, 176]

## GetTriangleKey

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [654, 349, 229, 132, 46]

## InitializeCamera

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [51]

## InitializeViewport

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [58, 50]

## IsAlphaShapeValidFast

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [236]

## IsDelaunayValidFast

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [356]

## JetColorMap

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [250, 228]

## LoadFromIniInternal

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/RenderConfig.cs` — 行 [266, 112]

## LoadFromObj

> 1 处调用 / 1 个调用方文件

- `PCLOperate/DataIO/PointCloudReader.cs` — 行 [93]

## LoadFromPly

> 1 处调用 / 1 个调用方文件

- `PCLOperate/DataIO/PointCloudReader.cs` — 行 [90]

## LoadFromTxt

> 1 处调用 / 1 个调用方文件

- `PCLOperate/DataIO/PointCloudReader.cs` — 行 [87]

## Log

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/RenderConfig.cs` — 行 [334, 270, 119]

## ProjectToPlane

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [627]

## ResetCameraToCenter

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [523]

## SaveToIni

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/RenderConfig.cs` — 行 [262, 107]

## SaveToObj

> 1 处调用 / 1 个调用方文件

- `PCLOperate/DataIO/PointCloudWriter.cs` — 行 [30]

## SaveToPly

> 1 处调用 / 1 个调用方文件

- `PCLOperate/DataIO/PointCloudWriter.cs` — 行 [27]

## SaveToTxt

> 1 处调用 / 1 个调用方文件

- `PCLOperate/DataIO/PointCloudWriter.cs` — 行 [24]

## ShowSurfaceMesh

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/PointCloudViewer.cs` — 行 [660, 640, 620, 599, 579, 560]

## ToVector3List

> 1 处调用 / 1 个调用方文件

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 [606, 436, 325, 206, 109, 25]

## TraverseSceneNode

> 1 处调用 / 1 个调用方文件

- `PCLOperate/DataIO/PointCloudReader.cs` — 行 [344, 54]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
