---
title: MoveControlData API 参考
date: 2026-07-16
tags: [API, 运控, 水平移动, 标定]
source: AdaWeldSystem/MotionControl/MoveControlData.cs
---

# MoveControlData API 参考

> 运控标定数据 + 水平移动计算 + 缓存，位于 `MotionControl/MoveControlData.cs`，命名空间 `AdaWeldSystem.MotionControl`。
> 原挂载于 InteliWeld，现归独立 MotionControl 模块（见 [[decisions/ADR-010-MotionControlModule]]）。
>
> **2026-09-07 改造**：去掉 `Lazy<T>` 单例，改为普通实例类；6 项标定参数不再自存副本，一律转发到 `MotionConfig` 的 `CALIBRATION` 节。

## 实例化关系

```csharp
public MoveControlData MoveData { get; private set; }   // MontionManager 构造时 new 并 Load
```

- 唯一持有者为 [[api/MontionManager]]，对外入口**仅** `MontionManager.Instance.MoveData`；
- `MoveControlData.Instance` / `DeltaMotionConfig.Instance` **已移除**，禁止再使用；
- 构造时创建 `DeltaMotionConfig`（`MotionConfig` 属性），标定参数经该实例落盘。

## 标定参数（转发到 MotionConfig）

| 属性 | 类型 | 说明 |
|------|------|------|
| `LaserFrontOffset` | `double` | 线激光相对焊枪的前装标定距离（并入缓存键） |
| `LaserToHorizontalAngleRad` | `double` | 线激光光轴与水平轴夹角（弧度） |
| `LaserToHorizontalAngleDeg` | `double` | 同上报角度（度），写时换算弧度 |
| `LaserToHorizontalScaleX` | `double` | 激光 mm ↔ 水平轴 mm 缩放标定（如 1mm=0.98mm） |
| `CalibratedCenterX/Y` | `double` | 标定工况焊缝中心点（偏差基准） |
| `ApproachThreshold` | `double` | 趋近匹配阈值（实际 robotX 落入缓存键 ± 阈值内即触发） |

> 属性为转发属性，读写直接落到 `MotionConfig` 对应字段，无第二份副本；默认值由 `DeltaMotionConfig` 构造函数给出（遵循 ADR-002 不用 auto-property initializer）。

## 运控配置

| 属性 | 类型 | 说明 |
|------|------|------|
| `MotionConfig` | `DeltaMotionConfig` | 台达运控配置实例：主站参数 / `Axes` 轴表 / `Inputs` 输入表 / `Outputs` 输出表 / PVT 段 / 跟踪段 / 标定段 |

`MontionManager.Initialization` 从 `MotionConfig.Axes` 建台达轴、从 `Inputs`/`Outputs` 建台达 IO，即**注册的轴与 IO 的配置全部从 MoveControlData 对象读取**。

## 方法

| 方法 | 说明 |
|------|------|
| `double ComputeHorizontalMove(double seamX, double seamY)` | `delta = seamX − CalibratedCenterX`；`move = delta × cos(angle) × scaleX` |
| `void CacheHorizontalMove(double robotX, double move)` | 键 `robotX + LaserFrontOffset` → move（lock 保护） |
| `bool TryGetNearestHorizontalMove(double robotX, out double move, out double key)` | 阈值内找最近缓存项（趋近/近似匹配） |
| `void RemoveHorizontalMove(double key)` | 命中后移除（避免重复触发） |
| `void ClearHorizontalMoveCache()` | 清空缓存 |
| `void ComputeAndCacheHorizontalMove(SeamFeatureResult seamFeature, double robotX)` | 组合：计算+缓存+日志（**单一算法真源**，供 WeldProcess 与 MotionControlWorkflow 统一调用） |
| `void Load()` / `void Save()` | **本地持久化**：委托 `MotionConfig.LoadConfig()` / `SaveConfig()`，读写 `Config/XML/DeltaMotionConfig.xml` 的 `CALIBRATION` 节；`Save` 由 `MotionControlPage`「保存标定参数」调用，`Load` 在 `MontionManager` 构造时自动执行一次（参见 [[guides/Project-Tools]]） |

> ⚠️ **配置源已统一**：原 `Config/INI/MoveControlData.ini` 弃用，标定与台达运控参数同处一个 XML。禁止再对同一文件开第二个 `XdocumentReaderWriter`——`SaveConfig` 会 `NewXdocument` 重建整篇，并发写会互相覆盖。

## 协作

- 被 `MotionControlWorkflow`（`MainDeviceControl/DeviceWorkflow/`）的水平移动线程消费、被 `WeldProcess`（[[modules/WeldParamControl]]）真实流程调用，两处均经 `MontionManager.Instance.MoveData` 访问。
- 标定参数由 [[modules/UIDesign]] 的 `MotionControlPage`「标定数据参数」组写入。
- `MontionManager` 是唯一对接台达控制器的对象；`MoveControlData` 只提供配置数据，不碰硬件。

---

*来源：AdaWeldSystem/MotionControl/MoveControlData.cs*
