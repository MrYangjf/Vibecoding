---
title: API — SeamTrajectoryBuilder 线激光引导轨迹构造器（已废弃）
date: 2026-09-11
updated: 2026-09-14
tags: [API, 线激光, Y轴, PVT, 焊缝跟踪, 轨迹构造, 已废弃, ADR-041]
source: AdaWeldSystem/WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs
---

# API — SeamTrajectoryBuilder 线激光引导轨迹构造器（已废弃）

> ⛔ **本类已删除**（2026-09-14 ADR-041 第二次修订）。
> 原 `SeamTrajectoryBuilder` / `ISeamTrajectoryBuilder` 已演进为继承 `WeldAlgorithmBase` 的非单例实现
> [[api/SeamTrackingAlgorithm]]，直接写 `IPVTMotion` 的控制器写入职责移交 [[api/MotionControlWorkflow]]。
> 本页仅作沿革与迁移参考。

---

## 沿革

| 时间 | 状态 | 说明 |
|---|---|---|
| 2026-09-11 | 创建（ADR-040） | 作为 `WeldParamControl.SeamGuide` 子目录下的单例轨迹构造器，内部直接写 PVT |
| 2026-09-14 | 删除 | 算法模块不应直接操作控制器；改为 `SeamTrackingAlgorithm` 只输出 PVT 点，由运控工作流写入 |

---

## 迁移对照

| 原 `SeamTrajectoryBuilder` 调用 | 现调用 |
|---|---|
| `SeamTrajectoryBuilder.Instance.SetConfig(config)` | ⛔ 已删除（2026-09-14）：配置由 `WeldParamManager` 自持自载，走无参 `LoadSeamGuideConfig()`，外部不再传入实例 |
| `SeamTrajectoryBuilder.Instance.AttachAxis(axis)` | 由 `MotionControlWorkflow` 直接持有轴引用 |
| `SeamTrajectoryBuilder.Instance.Feed(...)` | `WeldParamManager.Instance.FeedSeamTracking(...)` |
| `SeamTrajectoryBuilder.Instance.Tick()` | `WeldParamManager.Instance.TickSeamTracking()` |
| `SeamTrajectoryBuilder.Instance.Finish()` | `WeldParamManager.Instance.DrainSeamTracking()` + `MotionControlWorkflow` 写入最后一段 |
| `SeamTrajectoryBuilder.Instance.Reset()` | `WeldParamManager.Instance.ResetSeamTracking()` |
| `SeamTrajectoryBuilder.Instance.HasFault` | `WeldParamManager.Instance.SeamTrackingHasFault` |
| `SeamTrajectoryBuilder.Instance.FaultReason` | `WeldParamManager.Instance.SeamTrackingFaultReason` |
| `SeamTrajectoryBuilder.Instance.LastDeviation` | `WeldParamManager.Instance.SeamTrackingLastDeviation` |
| `SeamTrajectoryBuilder.Instance.LastTargetPos` | `WeldParamManager.Instance.SeamTrackingLastTargetPos` |

---

## 相关页面

- [[api/SeamTrackingAlgorithm]] — 替代本类的现行算法 API
- [[api/MotionControlWorkflow]] — 轨迹点消费与控制器写入方
- [[api/WeldParamManager]] — 模块唯一入口，代理轨迹算法
- [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] — 演进决策
- [[decisions/ADR-040-SeamGuideTrajectoryBuilder]] — 原始轨迹构造决策
