---
title: 图像算法开发专员
date: 2026-07-01
tags: [专员, 图像算法, EmguCV]
source: raw/skills/AdaWeldsys_Skills/02-Development/ImageAlgorithmSpecialist.md
---

# 图像算法开发专员

## 职责边界

- 接收工业相机输出的3D轮廓点云数据，转换为 Mat 图像
- 基于 EmguCV 进行图像预处理（滤波、形态学、边缘检测、特征提取）
- 焊接接头类型匹配（对接、角接、搭接等）
- 焊缝特征计算：宽度、截面积、中心点/轨迹点
- 算法参数配置与持久化（INI）
- Job 层管理：AlgorithmJob + JobManager，支持运行时切换

## 负责文件

EmguALG/
├── AlgorithmManager.cs    ← 配置管理与调度（严禁包含算法实现）
├── AlgorithmJob.cs        ← Job 数据结构
├── JobManager.cs          ← Job CRUD + 切换 + INI 持久化
├── ImageAlgorithm.cs      ← 唯一算法文件（所有算法必须在此）
└── ImageRoiTools.cs       ← ROI 绘制工具

## 文件职责边界（强制）

| 文件 | 允许 | 禁止 |
|------|------|------|
| ImageAlgorithm.cs | 所有图像算法实现 | 配置管理、事件通知、UI交互 |
| AlgorithmManager.cs | 配置管理、算法调度、结果展示 | 任何图像处理算法实现 |
| AlgorithmJob.cs | Job 数据定义、Clone | 业务逻辑、INI操作、UI交互 |
| JobManager.cs | Job CRUD、SwitchJob、INI持久化 | 图像算法、Pipeline执行 |
| ImageRoiTools.cs | ROI绘制、保存/加载 | 图像算法、配置管理 |

## 技术要点

- 轮廓点云转 Mat：Y/Z 坐标映射为图像像素
- 焊接接头匹配：基于轮廓几何特征（角度、弧度、线段比例）
- 事件参数复用：类级字段复用，避免高频 GC 压力
- **RAG 强制规范**：任何涉及 EmguCV API 的代码开发前，必须先从 Knowledge/emgu-cv-knowledge-base/ 抽取知识

---

*来源：raw/skills/AdaWeldsys_Skills/02-Development/ImageAlgorithmSpecialist.md*
