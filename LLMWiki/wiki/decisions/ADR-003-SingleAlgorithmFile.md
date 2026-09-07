---
title: ADR-003 单算法文件决策
date: 2026-07-01
tags: [决策, 算法, 规范]
status: accepted
source: raw/skills/02-Development/ImageAlgorithmSpecialist.md
---

# ADR-003 单算法文件决策

## 背景

图像算法模块早期由多个文件分散实现，导致维护困难、版本混乱。

## 决策

所有图像算法必须在 ImageAlgorithm.cs 一个文件中实现：

`
ImageAlgorithm.cs
├── 1. 点云转换区
├── 2. 预处理算法区
├── 3. 边缘检测算法区
├── 4. 特征提取算法区
└── 5. 辅助工具区
`

## 职责分离

| 文件 | 允许 | 禁止 |
|------|------|------|
| ImageAlgorithm.cs | 图像算法实现 | 配置管理、事件通知 |
| AlgorithmManager.cs | 配置管理、调度 | 任何算法实现 |

## 后果

- 算法集中，便于统一维护
- 但文件可能过大，需按区域组织

## 修订与现状（2026-07-31 知识库修复）

> **语义修订**：本 ADR 原字面"所有图像算法必须在 `ImageAlgorithm.cs` 一个文件"已不适应 2026-07 的 EmguALG 多文件重构。**本决策关于"原子算子集中于 `ImageAlgorithm.cs`"的核心约束仍然成立；"业务/领域算法也必须塞进单文件"的强约束已被取代。**

- **仍成立**：底层原子算子（点云转换 / 预处理 / 边缘检测 / 特征提取 / 辅助工具 + 监控相机算法区）必须集中在 `ImageAlgorithm.cs`（按 `#region` 分区组织），不得散落。
- **已修订**：业务/领域算法自 EmguALG 重构后拆分为「统一基类 `Core/AlgorithmBase.cs` + 两类领域算法单例 `SeamRecognition/` `RealtimeMonitor/`」，各自承载 INI 契约（见 [[modules/EmguALG]]）。领域算法在单例的 `ExecuteCore` 内实现，**禁止直调 `ImageAlgorithm` 原子算子、禁止散落进 `AlgorithmManager`/`JobManager`/配置层**。
- **初衷不变**：算法逻辑不得污染配置管理与调度层（`AlgorithmManager` 只做配置管理与调度，不实现算法）。

---

*来源：raw/skills/02-Development/ImageAlgorithmSpecialist.md*
