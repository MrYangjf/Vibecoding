---
title: MoveControlData API 参考
date: 2026-07-16
tags: [API, 运控, 水平移动, 标定]
source: AdaWeldSystem/MotionControl/MoveControlData.cs
---

# MoveControlData API 参考

> **台达运控配置持有者**（纯 `DeltaMotionConfig` holder），位于 `MotionControl/MoveControlData.cs`，命名空间 `AdaWeldSystem.MotionControl`。
> 原挂载于 InteliWeld，现归独立 MotionControl 模块（见 [[decisions/ADR-028-MotionControlModule]]）。
>
> **2026-09-07 改造**：去掉 `Lazy<T>` 单例，改为普通实例类。
> **2026-09-17 重写（ADR-042）**：删水平移动缓存子系统与全部标定包装属性，类收敛为纯 `DeltaMotionConfig` 持有者（230 → 85 行）——
> 标定 / 几何 / 安装参数一律经 `WeldParamManager.Instance.AlgorithmsConfig` 读取，消除双份数据源。详见 ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。

## 实例化关系

```csharp
public MoveControlData MoveData { get; private set; }   // MontionManager 构造时 new 并 Load
```

- 唯一持有者为 [[api/MontionManager]]，对外入口**仅** `MontionManager.Instance.MoveData`；
- `MoveControlData.Instance` / `DeltaMotionConfig.Instance` **已移除**，禁止再使用；
- 构造时创建 `DeltaMotionConfig`（`MotionConfig` 属性），台达运控参数经该实例落盘；标定参数**不再**经本类转发（ADR-042）。

## 运控配置

| 属性 | 类型 | 说明 |
|------|------|------|
| `MotionConfig` | `DeltaMotionConfig` | 台达运控配置实例：主站参数 / `Axes` 轴表 / `Inputs` 输入表 / `Outputs` 输出表 / `Cylinders` 气缸表（ADR-022）/ PVT 段 / 跟踪段 / 标定段 |

`MontionManager.Initialization` 从 `MotionConfig.Axes` 建台达轴、从 `Inputs`/`Outputs` 建台达 IO，即**注册的轴与 IO 的配置全部从 MoveControlData 对象读取**。

## 方法

| 方法 | 说明 |
|------|------|
| `void Load()` / `void Save()` | **本地持久化**：委托 `MotionConfig.LoadConfig()` / `SaveConfig()`，读写 `Config/MotionControl/Motion_XML/DeltaMotionConfig.xml`；`Load` 在 `MontionManager` 构造时自动执行一次，日志「运控配置已加载」（ADR-042） |

> ⚠️ **配置源唯一**：原 `Config/INI/MoveControlData.ini` 弃用。禁止再对同一文件开第二个 `XdocumentReaderWriter`——`SaveConfig` 会 `NewXdocument` 重建整篇，并发写会互相覆盖。

## 协作

- 唯一入口 `MontionManager.Instance.MoveData`：`MontionManager.Initialization` 从本对象的 `MotionConfig` 读取轴 / IO / 气缸的注册配置。
- 标定 / 几何 / 安装参数**不再经本类写入**——现由 [[modules/UIDesign]] 的 `ProcessControlPage`「线激光」段经 `WeldParamManager.Instance.AlgorithmsConfig` 读写（ADR-042）。
- `MontionManager` 是唯一对接台达控制器的对象；`MoveControlData` 只提供配置数据，不碰硬件，亦不做任何运动计算。

## 已删除（2026-09-17，ADR-042）

以下成员**已从代码删除**，本页此前记载的内容不再适用：

- **水平移动缓存子系统**：5 方法 `ComputeHorizontalMove` / `CacheHorizontalMove` / `TryGetNearestHorizontalMove` / `RemoveHorizontalMove` / `ClearHorizontalMoveCache` + 字段 `_horizontalMoveCache` / `_cacheLock`（自 ADR-027 换台达后全库零调用）。
- **全部标定包装属性**：`LaserFrontOffset` / `LaserToHorizontalAngleRad` / `LaserToHorizontalAngleDeg` / `LaserToHorizontalScaleX` / `CalibratedCenterX` / `CalibratedCenterY` / `ApproachThreshold`，以及私有属性 `CalibConfig`。
- 同时移除 `using System.Collections.Generic` / `using AdaWeldSystem.WeldParamControl`。

> 决策依据：ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）（标定数据源唯一化；上一节「易误判点」所述水平移动缓存不再存在）。

---

*来源：AdaWeldSystem/MotionControl/MoveControlData.cs*
