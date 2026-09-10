---
title: AlgorithmManager — EmguALG 统一调度入口（承接原 AlgorithmManager 与 PipelineManager 可复用职责）
date: 2026-09-08
updated: 2026-09-09
tags: [API, 算法, 管理器, EmguALG, 配置]
source: AdaWeldSystem/EmguALG/Manager/AlgorithmManager.cs
---

# AlgorithmManager — EmguALG 统一调度入口

> `AdaWeldSystem.EmguALG.Manager.AlgorithmManager`（`EmguALG/Manager/AlgorithmManager.cs`）。
> **2026-09-08 ADR-038** 三层改造产物：统一调度两个检测（送丝距离/焊接质量），承接原 `MonitorCam/AlgorithmManager`（已删除）的参数持久化职责；原 `EmguConfiger/PipelineManager` 删除（配置/阶段编排/焊缝上报职责随之移除，见 ADR-038）。
> **2026-09-09 ADR-039**：领域算法命名空间迁入 `EmguALG.RealtimeMonitor.WireFeedDistance` / `EmguALG.RealtimeMonitor.WeldQuality`，公共 API 签名不变。

## 入口与配置

| 成员 | 说明 |
|---|---|
| `static AlgorithmManager Instance` | 单例 |
| `WireFeedConfig WireFeed` | 送丝距离检测配置（强类型） |
| `WeldQualityConfig Quality` | 焊接质量检测配置（强类型） |
| `int WireFeedVersion` / `int QualityVersion` | 配置版本号（消费方比对此值刷新） |
| `void ApplyConfig()` | 配置变更后分发至算法 |
| `void Load()` / `void Save()` | 配置持久化 |

> 配置类型命名空间：
> - `AdaWeldSystem.EmguALG.RealtimeMonitor.WireFeedDistance.WireFeedConfig`
> - `AdaWeldSystem.EmguALG.RealtimeMonitor.WeldQuality.WeldQualityConfig`

## 检测执行

| 成员 | 说明 |
|---|---|
| `WireFeedResult DetectWireFeed(Mat image)` | 送丝距离检测（包装 `ImageAlgorithm` 第 8 区算子） |
| `WeldQualityResult DetectWeldQuality(Mat image)` | 焊接质量检测（同上） |
| `WireFeedResult GetLatestWireFeed(out int version)` | 取最近结果快照（结果池化 + 版本号，零 GC 读） |
| `WeldQualityResult GetLatestQuality(out int version)` | 同上（质量侧） |

## 事件

| 成员 | 说明 |
|---|---|
| `event EventHandler<AlgorithmCompletedEventArgs> AlgorithmCompleted` | 检测完成事件（**仅监控相机链路**；原焊缝特征上报链已按用户裁定整条删除——焊缝特征由线激光直接获取，见 ADR-038） |

## 关联

- 模块页：[[modules/EmguALG]]；决策：[[decisions/ADR-038-EmguALGThreeLayer]]、[[decisions/ADR-039-MonitorCamBoundaryAndEmguALGRefinement]]
- 消费方：`MonitorCameraWorkflow`（检测执行）、`MonitorCamPage` / `FormMain`（配置面板，原 `AlgorithmManager.Load()` 调用点改此）
- 相机侧：[[api/MonitorCamManager]]
