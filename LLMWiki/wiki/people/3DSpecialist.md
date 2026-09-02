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

PointCloudData/
├── 3DModel.cs
├── DataIO.cs
├── Render.cs
├── RunFileRecord/RunRecordManager.cs
├── File3DManager.cs
├── PointCloudFilter.cs
├── MeshBuilder.cs
├── ColorMapper.cs
├── CoordinateTransformer.cs
└── BoundingBoxCalculator.cs

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
