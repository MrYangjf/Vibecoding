---
title: 焊接工艺开发专员
date: 2026-07-01
tags: [专员, 焊接, 工艺]
source: raw/skills/AdaWeldsys_Skills/02-Development/WeldProcessSpecialist.md
---

# 焊接工艺开发专员

## 职责边界

- 焊接工艺核心逻辑：焊缝跟踪、自适应参数调整
- 焊接参数计算：功率/速度/送丝量
- 焊接质量评估
- 自动参数配置与数据库持久化
- 焊接接头类型定义与管理

## 负责文件

InteliWeld/
├── WeldProcess.cs              ← 焊接工艺主类（单例）
├── WeldProcessData.cs          ← 焊接数据结构
├── AutoAdjust.cs               ← 自适应调整算法（预留 TODO）
├── SeamTracker.cs              ← 焊缝跟踪器
├── WeldParameterCalculator.cs  ← 焊接参数计算器
└── QualityEvaluator.cs         ← 焊接质量评估

## 数据流

EmguALG/ImageAlgorithm.cs → PipelineManager.Instance.AlgorithmCompleted
                   ↓
            WeldProcess.OnAlgorithmCompleted（订阅者，**仅暂存**最新帧特征与 RobotX，不再每帧执行 AutoAction）
                   ↓
            （不在此处执行调整）
                   ↓
            LineLaserWorkflow.ExecuteStep_Adjust → RunAutoAdjust() → WeldProcess.TriggerAdjustment()
                   ↓
            WeldProcess.AutoAction(...)（单一调用点，由 Workflow 统一驱动）
                   ↓
            ├── StoreChartData（每帧）→ RunRecordManager.RecordProcessFrame（WeldActionRecord, ProcessFrame）
            ├── if (actionSuccess) RecordActionToRunFileRecord → RecordAdjustment（WeldActionRecord, WeldParamAdjust）
            └── 触发 WeldProcessCompleted 事件 → 主界面实时折线图

> 注：记录/调整链路由 **LineLaserWorkflow 在 Adjust 步骤统一驱动**（调用 `WeldProcess.TriggerAdjustment()`），WeldProcess 自身只暂存算法结果，单一驱动源避免双链路并存（见 [[decisions/ADR-011-WorkflowAsAdjustmentDriver]]）。

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| 图像算法专员 | SeamFeatureResult |
| 运动控制专员 | TrackSeamPos, AdjustFocus |
| 数据库专员 | AutoParamManager, ConfigManager |
| 通用技术专员 | GlobalCommData 事件总线 |

---

*来源：raw/skills/AdaWeldsys_Skills/02-Development/WeldProcessSpecialist.md*
