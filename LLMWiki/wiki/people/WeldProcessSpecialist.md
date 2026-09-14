---
title: 焊接工艺开发专员
date: 2026-07-01
updated: 2026-09-14
tags: [专员, 焊接, 工艺, ADR-041]
source: raw/skills/AdaWeldsys_Skills/02-Development/WeldProcessSpecialist.md
---

# 焊接工艺开发专员

> **⚠️ 2026-09-14 沿革（ADR-041）**：本页原描述的文件清单（`InteliWeld/`、`AutoAdjust.cs`、`SeamTracker.cs`、`WeldParameterCalculator.cs`、`QualityEvaluator.cs`）**从未落地或已废弃**；
> 现行代码位于 `AdaWeldSystem/WeldParamControl/`，且 ~~`WeldProcess`~~ 于 2026-09-14 拆分为「抽象基类 + 实现类 + `WeldParamManager` 唯一入口」，
> ~~`WeldDataManager`~~ 与 ~~`SeamTrajectoryBuilder`~~ 同日删除，职责/算法并入 `WeldParamManager`。
> 现行结构以 [[modules/WeldParamControl]] 为单一真相源。

## 职责边界

- 焊接工艺核心逻辑：焊接参数计算（功率 / 速度 / 送丝量）、自适应参数调整
- 焊缝宽度驱动的参数调整算法（线激光焊缝宽度 → 工艺参数）
- 线激光焊缝几何轨迹跟踪算法（线激光结果 + 机器人坐标 → Y 轴 PVT 点）
- 焊接参数查表调整与计算公式维护
- 自动参数配置与数据库持久化（由 `WeldParamManager` 统一管理）
- 焊接算法配置（`WeldAlgorithmsConfig`：线激光引导 `SEAM_GUIDE` + 参数调整 `WELD_PARAM_ADJUST` **两节合一**，由 `WeldParamManager` 独占持有，落 `Config/XML/WeldParamControl.xml`；ADR-044 前为 `SeamGuideConfig` / `WeldParamAdjustmentConfig` 两类）
- 焊缝种类定义与管理

## 负责文件（现行）

```
AdaWeldSystem/WeldParamControl/
├── WeldParamData.cs                            ← 数据类集合（RobotWeldData / AutoParam / ChartVar / ...）
├── WeldParamManager.cs                         ← 单例 · 模块唯一入口（配置 + 全部算法实现，ADR-041）
├── WeldAlgorithmsConfig.cs                     ← 焊接算法配置（两节合一，Manager 独占 + 自有 Config/XML/WeldParamControl.xml；ADR-044）
├── Abstractions/WeldAlgorithmBase.cs           ← 算法抽象基类
├── Algorithms/SeamGuideSample.cs               ← 算法私有输入结构（结果 + 机器人坐标 + 时间戳）
├── Algorithms/WeldParamLookupAlgorithm.cs      ← 参数查表调整（公式 + 三张映射表）
├── Algorithms/WeldParamAdjustmentAlgorithm.cs  ← 焊缝宽度驱动的参数调整
└── Algorithms/SeamTrackingAlgorithm.cs         ← 线激光焊缝几何轨迹跟踪（输出 PVT 点）
```

配套流程：
- `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs`（参数调整后下发机器人）
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs`（轨迹点缓冲区管理与控制器写入）

## 数据流

### 参数调整链路

```
线激光焊缝结果（焊缝宽度）+ 机器人 RobotX
                   ↓
        WeldParamControlWorkflow.ComputeAndOutput()（只置 _pendingCompute）
                   ↓
        LineLaserWorkflow 驱动 → WeldParamManager.TriggerAdjustment()【无参】
                   ↓
        WeldParamAdjustmentAlgorithm.ExecuteAdjustment（单一调整入口）
                   ↓
        ├── StoreChartData（每帧）→ RunRecordManager.RecordProcessFrame（WeldActionRecord, ProcessFrame）
        ├── if (actionSuccess) RecordActionToRunFileRecord → RecordAdjustment（WeldActionRecord, WeldParamAdjust）
        └── 触发 WeldProcessCompleted 事件 → 主界面实时折线图
```

### 轨迹跟踪链路

```
LineLaserManager.ResultReady
                   ↓
        MotionControlWorkflow.OnSeamResultReady（仅 Working 态）
                   ↓
        WeldParamManager.Instance.FeedSeamTracking(...) → PVTPoint[]
                   ↓
        MotionControlWorkflow 缓冲区 → IPVTMotion.BeginMove / ContinueMove → Y 轴
```

> 注：记录 / 调整链路由 **LineLaserWorkflow 在 Working 态统一驱动**（调用 `WeldParamManager.TriggerAdjustment()`），
> Manager 自身只做数据取用与转发，单一驱动源避免双链路并存（见 [[decisions/ADR-009-WorkflowAsAdjustmentDriver]]）。

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| 线激光专员 | 焊缝宽度 / 特征（`LineLaserSeamResult`） |
| 运动控制专员 | Y 轴 PVT 点（`SeamTrackingAlgorithm` 输出，`MotionControlWorkflow` 写入控制器，ADR-041） |
| 数据库专员 | `WeldParamManager.AutoParamHelper` / `WeldParamManager.ConfigHelper` |
| 通用技术专员 | `GlobalCommData` 日志出口 |

---

*来源：raw/skills/AdaWeldsys_Skills/02-Development/WeldProcessSpecialist.md*
