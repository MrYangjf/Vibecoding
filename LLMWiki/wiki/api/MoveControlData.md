---
title: MoveControlData API 参考
date: 2026-07-16
tags: [API, 运控, 水平移动, 标定]
source: AdaWeldSystem/MotionControl/MoveControlData.cs
---

# MoveControlData API 参考

> 运控标定数据 + 水平移动计算 + 缓存（单例），位于 `MotionControl/MoveControlData.cs`，命名空间 `AdaWeldSystem.MotionControl`。
> 原挂载于 InteliWeld，现归独立 MotionControl 模块（见 [[decisions/ADR-012-MotionControlModule]]）。

## 单例

```csharp
public static MoveControlData Instance { get; }   // Lazy<T>
```

## 标定参数

| 属性 | 类型 | 说明 |
|------|------|------|
| `LaserFrontOffset` | `double` | 线激光相对焊枪的前装标定距离（并入缓存键） |
| `LaserToHorizontalAngleRad` | `double` | 线激光光轴与水平轴夹角（弧度） |
| `LaserToHorizontalAngleDeg` | `double` | 同上报角度（度），写时换算弧度 |
| `LaserToHorizontalScaleX` | `double` | 激光 mm ↔ 水平轴 mm 缩放标定（如 1mm=0.98mm） |
| `CalibratedCenterX/Y` | `double` | 标定工况焊缝中心点（偏差基准） |
| `ApproachThreshold` | `double` | 趋近匹配阈值（实际 robotX 落入缓存键 ± 阈值内即触发） |

> 属性于构造函数显式初始化（遵循 ADR-002）。

## 方法

| 方法 | 说明 |
|------|------|
| `double ComputeHorizontalMove(double seamX, double seamY)` | `delta = seamX − CalibratedCenterX`；`move = delta × cos(angle) × scaleX` |
| `void CacheHorizontalMove(double robotX, double move)` | 键 `robotX + LaserFrontOffset` → move（lock 保护） |
| `bool TryGetNearestHorizontalMove(double robotX, out double move, out double key)` | 阈值内找最近缓存项（趋近/近似匹配） |
| `void RemoveHorizontalMove(double key)` | 命中后移除（避免重复触发） |
| `void ClearHorizontalMoveCache()` | 清空缓存 |
| `void ComputeAndCacheHorizontalMove(SeamFeatureResult seamFeature, double robotX)` | 组合：计算+缓存+日志（**单一算法真源**，供 WeldProcess 与 MotionControlWorkflow 统一调用） |
| `void Load()` / `void Save()` | **本地持久化**：6 项标定参数读写至 `Config/INI/MoveControlData.ini`（`[Calibration]` 节）；`Save` 由 `MotionControlPage`「保存标定参数」调用，`Load` 须在启动期、创建子页面之前调用（参见 [[guides/Project-Tools]]） |

## 协作

- 被 `MotionControlWorkflow`（`MainDeviceControl/DeviceWorkflow/`）的水平移动线程消费、被 `WeldProcess`（[[modules/WeldParamControl]]）真实流程调用。
- 标定参数由 [[modules/UIDesign]] 的 `MotionControlPage`「标定数据参数」组写入。

---

*来源：AdaWeldSystem/MotionControl/MoveControlData.cs*
