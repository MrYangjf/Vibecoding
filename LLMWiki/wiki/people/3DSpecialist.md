---
title: 3D开发专员
date: 2026-07-01
tags: [专员, 3D, HelixToolkit]
source: raw/skills/AdaWeldsys_Skills/02-Development/3DSpecialist.md
---

# 3D开发专员

## 职责边界

- 3D点云数据文件读写（导入/导出/格式转换）
- 3D实时渲染引擎（HelixToolkit.Wpf.SharpDX）
- 点云滤波与后处理
- 运行记录管理（时间戳、批次、参数快照）
- 自动对焦算法：Z轴偏移量计算

## 负责文件

PCLOperate/                            ← 点云模块（目录 = 命名空间 = AdaWeldSystem.PCLOperate）
├── Models/                            Point3D, PointCloudData                ns ...PCLOperate.Models
├── DataIO/                            PointCloudReader, PointCloudWriter     ns ...PCLOperate.DataIO
└── Render/                            PointCloudViewer, RenderConfig, SurfaceTriangulator   ns ...PCLOperate.Render

> **2026-09-14 目录对齐（ADR-048）**：原 `3DModel/` → `Models/`；模块目录名 `PointCloudData/` → `PCLOperate/`（wiki 页名仍为 [[modules/PointCloudData]]）。原列出的 `File3DManager` / `PointCloudFilter` / `MeshBuilder` / `ColorMapper` / `CoordinateTransformer` / `BoundingBoxCalculator` 在现仓库中**不存在**（历史规划，已并入上述三目录）。

## 技术要点

- HelixToolkit.Wpf.SharpDX 渲染引擎
- Assimp 模型导入：必须整体添加 scene.Root
- Bounds 哨兵值处理：Minimum>=Maximum 时跳过
- 颜色映射：高度/强度 → 颜色渐变

## 协作关系

| 协作对象 | 协作内容 |
|----------|----------|
| 工业相机专员 | 接收原始点云数据 |
| 图像算法专员 | 提供处理后的深度图 |
| UI开发专员 | 3D渲染页面集成 |
| 运动控制专员 | 提供自动对焦Z轴偏移量 |

---

*来源：raw/skills/AdaWeldsys_Skills/02-Development/3DSpecialist.md*
