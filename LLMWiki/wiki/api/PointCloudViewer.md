---
title: PointCloudViewer API 参考
date: 2026-07-01
tags: [API, 3D, 渲染, HelixToolkit, 点云]
source: AdaWeldSystem/3DView/PointCloudViewer.cs
module: PointCloudData
---

# PointCloudViewer API 参考

> **所属模块**：[[modules/PointCloudData]] — 3D渲染引擎公共接口，基于 HelixToolkit 实现点云可视化。

## 核心类

`csharp
public class PointCloudViewer : IDisposable
{
    // 初始化
    public void Initialize(Viewport3DX viewport);
    
    // 数据加载
    public void LoadPointCloud(PointCloudData data);
    public void LoadMesh(MeshGeometry3D mesh);
    public void LoadFromFile(string filePath);
    
    // 显示控制
    public void ResetView();
    public void FitToView();
    public void SetBackgroundColor(Color color);
    
    // 渲染选项
    public bool ShowPointCloud { get; set; }
    public bool ShowMesh { get; set; }
    public bool ShowCoordinateSystem { get; set; }
    public double PointSize { get; set; }
    
    // 颜色映射
    public void SetColorMap(ColorMapType type, double min, double max);
    
    // 事件
    public event EventHandler<PointSelectedEventArgs> PointSelected;
    public event EventHandler<ViewChangedEventArgs> ViewChanged;
}
`

## ColorMapType 枚举

`csharp
public enum ColorMapType
{
    Height,     // 高度映射
    Intensity,  // 强度映射
    ZValue,     // Z值映射
    Custom      // 自定义映射
}
`

## 关键约束

- Bounds 必须有效（Minimum < Maximum），否则可能导致黑屏
- 数据中的 Infinity/NaN 必须在加载前过滤
- Assimp 导入必须使用 scene.Root 整体加入

---

*来源：raw/knowledge/AdaWeldSystem_Wiki.md + raw/skills/02-Development/3DSpecialist.md*
