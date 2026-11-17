---
title: LineLaserContourAlgorithm API 参考（线激光轮廓 Mat 渲染算法）
date: 2026-09-17
tags: [API, 线激光, 算法, EmguALG, 渲染, Mat, ADR-007, ADR-028]
source: AdaWeldSystem/EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs
---

# LineLaserContourAlgorithm API 参考

> 线激光轮廓 Mat 渲染算法实现：把一帧轮廓点云 + 校准数据 + 焊缝识别结果渲染为供 UI 显示的 Emgu Mat。
> **位置**：`AdaWeldSystem/EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs`（接口 `ILineLaserContourAlgorithm.cs` 同目录）
> **命名空间**：`AdaWeldSystem.EmguALG.LineLaserContour`
> **沿革**：2026-09-09 从 LineLaserManager.ProfileMatRenderer 上提为独立算法（本页即 ProfileMatRenderer 的现役承继）。线激光模块只负责采集/识别，显示渲染归 EmguALG.LineLaserContour（[[decisions/ADR-022-EmguALGThreeLayer]] / [[decisions/ADR-019-MonitorCamBoundaryAndEmguALGRefinement]]）。

---

## 定位

```
LineLaserManager（采集/识别）
  ↓ 每帧调用 Render(cloud, calib, result)
LineLaserContourAlgorithm : ILineLaserContourAlgorithm（画布渲染）
  → 返回 Mat（LastMat），调用方 Clone 后跨线程使用 / UI 显示
```

- **单例持有**：实现类由 `AlgorithmManager.LineLaserContour` 惰性创建并持有（2026-11-09 ADR-097），全仓无第二处 `new LineLaserContourAlgorithm()`；`LineLaserManager` 只取用与不释放。
- **数据契约在算法层**：`Render` 只收算法层 DTO（`LineLaserProfileData` / `LineLaserCalibrationData` / `LineLaserSeamFeature`），硬件层 `LineLaserManager` 负责把 PCL 点云与相机标定转换后传入，算法层不引用 `LineLaserCam` / `PCLOperate`。
- **资源零抖动**：画布 Bitmap + Graphics + Mat 一次分配后终身复用，每帧只 Clear 后重绘；Mat 首帧 `_canvasBmp.ToMat()` 新建、后续 `CopyTo` 原地复用。

## 关键成员

| 成员 | 签名 | 职责 |
|---|---|---|
| `Render` | `Mat (LineLaserProfileData profile, LineLaserCalibrationData calib, LineLaserSeamFeature result)` | 把一帧轮廓渲染为 Mat（锁内执行） |
| `LastMat` | `Mat { get; }` | 最近一次渲染结果，**调用方须自行 Clone 后使用** |
| `Dispose` | `void ()` | 释放画布、Graphics 与 Mat |

## 输入 / 输出

| 项 | 类型 | 说明 |
|---|---|---|
| 输入 `profile` | `LineLaserProfileData` | 轮廓点集（`Ys` / `Zs` + `Count`，与硬件缓冲共用），为空时只清屏 |
| 输入 `calib` | `LineLaserCalibrationData` | 标定数据：`HasData` 为 true 时按四角标定框绘制校准框/十字架/mm 刻度栅格；false 时按轮廓范围自动缩放并绘制网格与 Y/Z 范围标注 |
| 输入 `result` | `LineLaserSeamFeature` | 焊缝特征点，`Valid` 时绘制红色特征点 |
| 输出 | `Mat`（834×554 画布） | 渲染结果（轮廓绿线 + 特征点 + 校准框 + 毫米刻度），返回共享实例 |

## 渲染要点（源码确认）

- 画布常量：`CanvasW = 834`、`CanvasH = 554`、`Margin = 30f`。
- 缩放率：校准模式按四角尺寸与画布内边距取 `min(rateX, rateY)`；回退模式按轮廓 Y/Z 范围自动缩放。
- 坐标变换：校准模式 `center + 物理值×rate`（原点对齐图像中心）；回退模式按 min 值平移。
- mm 刻度步长自适应：`stepMm = max(1, round(40 / rate))`。
- 轮廓点上限取 `LineLaserProfileData.MaxPoints`（2048）。
- 十字架与四角交点由 `CalcTwoLineCrossPoint` 求两直线交点（平行返回 (-1,-1)）。

## 内部结构（2026-09-22 精简）

`Render` 由 200 行 / 35 局部变量收敛为 27 行骨架 + 6 个静态绘制方法，几何量集中于私有嵌套类 `ViewGeometry`（缩放 / 中心 / 角点 / 十字交点 / 回退范围）：

| 成员 | 职责 |
|---|---|
| `BuildViewGeometry(calib, hasCalib, profile, count)` | 一次算全视图几何（校准按角点定标，回退按轮廓范围缩放） |
| `DrawFallbackGrid` / `DrawCalibrationBackdrop` | 回退参考网格 / 校准标定框 + 十字 + 中心点 |
| `DrawProfile(g, profile, count, view, hasCalib, result)` | 轮廓折线 + 特征点（坐标变换委托在本段内构建） |
| `DrawMillimeterGrid` / `DrawRangeLabels` | 毫米刻度栅格 / 回退模式 Y-Z 范围标注 |

## 相关页面

- [[api/LineLaserManager]] — 唯一调用方（每帧转换 DTO 后调用 Render，Mat 经 MatUpdated 透出）
- [[api/AlgorithmManager]] — 算法层唯一入口（`LineLaserContour` 惰性持有本算法，2026-11-09 ADR-097）
- [[modules/EmguALG]] — 算法模块说明
- [[modules/LineLaserCam]] — 线激光采集模块
- [[decisions/ADR-022-EmguALGThreeLayer]] — EmguALG 三层架构
- [[decisions/ADR-019-MonitorCamBoundaryAndEmguALGRefinement]] — 监控相机边界与 EmguALG 精化
