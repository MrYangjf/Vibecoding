---
title: API — ProfileMatRenderer 轮廓 Mat 渲染器
date: 2026-09-08
tags: [API, 相机, 线激光, 渲染, GDI, 业务层, ADR-039]
source: AdaWeldSystem/LineLaserCam/LineLaserManager.cs
---

# API — ProfileMatRenderer 轮廓 Mat 渲染器

> **2026-09-08 归并（ADR-040）**：本类不再单独立文件，与 `LineLaserManager` 同驻 `LineLaserCam/LineLaserManager.cs`。
> **位置**：`LineLaserCam/LineLaserManager.cs`（命名空间 `AdaWeldSystem.LineLaserCam`）
> **2026-09-08 新增（ADR-039）**：由英莱实现层私有方法 `ConvertContourToMatDemo` **上提至业务层**而来。
> 原实现约 250 行 GDI+ 绘制，依赖英莱私有校准数据，导致实现层既做采集又做显示；上提后实现层**只存校准数据**（`LineLaserCalibration`），绘制由本类按需执行。
> **调用方**：只有 `LineLaserManager`（`DisplayEnabled` 为真时才调 `Render`），UI 不直接持有本类。

## 公共 API

| 成员 | 签名 | 说明 |
|------|------|------|
| `Render` | `Mat (PointCloudData cloud, LineLaserCalibration calib, LineLaserSeamResult result)` | 把一帧轮廓渲染为 Mat。`cloud` 为空只清屏；`calib.HasData==false` 时按轮廓范围自动缩放；`result.Valid` 时绘制特征点。已释放返回 `null`。**返回的 Mat 是内部持久实例**，调用方须 `Clone()` 后跨帧/跨线程持有 |
| `LastMat` | `Mat { get; }` | 最近一次渲染结果（`lock` 保护读取），同样须 `Clone()` |
| `Dispose` | `void ()` | 幂等释放 `Graphics` / `Bitmap` / `Mat`，日志标签「线激光渲染器」（遵循 [[decisions/ADR-001-DisposePattern]]，未重写 `Dispose(bool)`） |

## 绘制内容（沿用英莱官方 demo 的 resetInnerData / TransPoint / Paint 算法）

- **画布**：834×554，一次分配终身复用；每帧 `Clear(30,30,30)` 后重绘，`SmoothingMode.AntiAlias`。`Bitmap.ToMat()` 首帧新建 Mat、后续 `CopyTo` 原地复用（Emgu.CV 4.x 确定性 API）。
- **有校准数据**（`calib.HasData`）：
  - 比例 `rate = min((W-2M)/cornerW, (H-2M)/cornerH)`，`M = 30`。
  - 四角 `center ± |corner*rate|`；⚠️ **`center` 取图像中心 `(W/2, H/2)`**——原 demo 用 `fPersent/dwOffset` 推导导致十字架不居中，本版已修正。
  - 变换 `trans(y,z) = (center.X + y*rate, center.Y - z*rate)`，mm 原点在图像中心。
  - 校准框：`FillPolygon` 深灰 `0x3B3B3B` + `DrawPolygon` 黄色 2px。
  - 大十字架：水平/垂直线经 `CalcTwoLineCrossPoint` 与校准框四边求交后 `DrawLine` 浅灰 2px（平行返回 `(-1,-1)` 则跳过该线）。
  - 角点与中心点：浅绿实心圆 6px；特征点 `result.Valid` 时红色 8px 方块。
  - 轮廓折线：`DrawLines` 绿色 `0x00FF80` 1.5px，最多 `ProfileSnapshot.MaxPoints`（2048）点。
  - mm 虚线刻度栅格：`stepMm = max(1, round(40/rate))`，垂直线 `sx = center.X + mm*rate`、水平线 `sy = center.Y - mm*rate`，底部/左侧 8.5px 宋体灰字标注。
- **无校准数据**（回退）：按本帧 min/max 自动缩放 + 8×8 深灰网格 + 底部 `Y:a~b mm` 与左侧竖排 `Z:a~b mm` 标签。

## 关键设计

- **零 GC 抖动**：`Bitmap`/`Graphics`/`Mat` 各只分配一次；`Pen`/`Brush`/`Font` 每帧 `using` 即时释放。整段绘制在 `lock(_lock)` 内，与 `LastMat` getter 互斥，也避免回调并发重入。
- **线程**：不自带线程，由调用方（`LineLaserManager.OnCameraProfileReady`）在 SDK 原生线程上调用；结果经 `UpdateDisplayMat` 回写基类后再由 `MatUpdated` 事件封送到 UI。
- **纯文本日志**：仅 `Dispose` 输出一条「轮廓渲染器已释放」（[[standards/CodeSimplification]]）。

## 使用模式

```csharp
// LineLaserManager 内部（简化）
Mat mat = _renderer.Render(e.Cloud, Active.Calibration, _lastResult);
if (mat != null) Active.UpdateDisplayMat(mat);
RaiseMatUpdated(mat);
```

## 关联

- 决策：[[decisions/ADR-035-LineLaserResponsibilitySplit]]
- 调用方：[[api/LineLaserManager]]、[[modules/LineLaserCam]]
- 校准数据结构：`LineLaserCam/ILineLaser/LineLaserCalibration.cs`
- 原实现出处：[[api/IntelligentLaserCam]]（⛔ `ConvertContourToMatDemo` 已于 2026-09-08 从该文件删除）

---

*来源：AdaWeldSystem/LineLaserCam/LineLaserManager.cs*
