---
title: PointCloudData 模块 — 3D点云数据处理
date: 2026-07-01
updated: 2026-08-07
tags: [模块, 3D, 点云, HelixToolkit]
source: raw/knowledge/AdaWeldSystem_Wiki.md
---

# PointCloudData 模块 — 3D点云数据处理

> 负责3D点云数据的存储、文件读写、实时渲染和运行记录管理。基于 HelixToolkit.Wpf.SharpDX 渲染引擎。
> **模块位置**：`AdaWeldSystem/PCLOperate/`（目录名为 PCLOperate，模块名仍为 PointCloudData）

## 目录结构

```
PCLOperate/
├── Models/
│   ├── Point3D.cs                       ← 3D 点数据结构
│   └── PointCloudData.cs               ← 点云数据集
├── DataIO/
│   ├── PointCloudReader.cs             ← 点云文件读取
│   └── PointCloudWriter.cs             ← 点云文件写入
├── Render/
│   ├── PointCloudViewer.cs             ← 3D 渲染引擎核心
│   ├── RenderConfig.cs                 ← 渲染配置
│   └── SurfaceTriangulator.cs          ← 点云表面三角化
└── （RunFileRecord/ 已迁出 → [[modules/ProductFileManager]]，2026-08-31 ADR-021）
```

> **2026-08-07 目录名修正**：实际代码目录名为 `PCLOperate/`（而非 `PointCloudData/`），内部子结构完全一致。模块名仍沿用 `PointCloudData`。
> **2026-08-31 RunFileRecord 迁出（ADR-021）**：过程记录 4 文件（RunRecordManager/RecordFrame/WeldActionRecord/SmartRayConverter）迁入 `ProductFileManager/`，命名空间改 `AdaWeldSystem.ProductFileManager`；本模块仅余点云本域（Models/DataIO/Render），RunRecordManager 仍引用本模块 Models/DataIO。

## 核心文件

| 文件 | 职责 |
|------|------|
| `Models/Point3D.cs` | 3D 点数据结构（X/Y/Z/强度） |
| Models/PointCloudData.cs | 点云数据集（点列表 + 元数据） |
| DataIO/PointCloudReader.cs | 点云数据文件读取（导入/格式转换） |
| DataIO/PointCloudWriter.cs | 点云数据文件写入（导出） |
| Render/PointCloudViewer.cs | 3D渲染引擎核心（HelixToolkit 封装） |
| Render/RenderConfig.cs | 渲染配置（颜色/视角/光照） |
| Render/SurfaceTriangulator.cs | 点云表面三角化 |

> 原 `RunFileRecord/` 三行（RunRecordManager/RecordFrame/SmartRayConverter）已迁出，职责描述见 [[modules/ProductFileManager]]。

## 渲染引擎架构

PointCloudViewer.cs (HelixToolkit.Wpf.SharpDX)
├── Viewport3DX 视口管理
├── PointGeometryModel3D 点云渲染
├── MeshGeometryModel3D 网格渲染
├── LineGeometryModel3D 线框渲染
└── EffectsManager 效果管理

## 关键约束

| 约束 | 说明 |
|------|------|
| Assimp 导入必须整体添加 Root | 禁止逐个 AddChildNode，必须使用 scene.Root 整体加入 |
| Bounds 哨兵值 | Minimum>=Maximum 时必须跳过，Infinity/NaN 数据必须过滤，否则黑屏 |

## 协作关系

- [[modules/LineLaserCam]] → 提供原始点云数据
- [[modules/EmguALG]] → 接收处理后的深度图用于图像算法
- [[modules/WeldParamControl]]（WeldProcess）→ 调用 `RunRecordManager` 记录 WeldActionRecord（见 [[modules/DeviceControl]]）
- [[modules/UIDesign]]/Helix3Drender → 3D可视化界面
- [[modules/UIDesign]]（DataReview）→ 读取 `.pDat` 记录文件离线回溯

---

*来源：raw/knowledge/AdaWeldSystem_Wiki.md + raw/skills/02-Development/3DSpecialist.md*
