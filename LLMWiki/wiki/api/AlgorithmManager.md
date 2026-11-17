---
title: AlgorithmManager — EmguALG 统一调度入口（承接原 AlgorithmManager 与 PipelineManager 可复用职责）
date: 2026-09-08
updated: 2026-11-09
tags: [API, 算法, 管理器, EmguALG, 配置]
source: AdaWeldSystem/EmguALG/Manager/AlgorithmManager.cs
---

# AlgorithmManager — EmguALG 统一调度入口

> `AdaWeldSystem.EmguALG.Manager.AlgorithmManager`（`EmguALG/Manager/AlgorithmManager.cs`）。
> **2026-09-08 ADR-007** 三层改造产物：统一调度两个检测（送丝距离/焊接质量），承接原 `MonitorCam/AlgorithmManager`（已删除）的参数持久化职责；原 `EmguConfiger/PipelineManager` 删除（配置/阶段编排/焊缝上报职责随之移除，见 ADR-007）。
> **2026-09-09 ADR-028**：领域算法命名空间迁入 `EmguALG.RealtimeMonitor.WireFeedDistance` / `EmguALG.RealtimeMonitor.WeldQuality`，公共 API 签名不变。
> **2026-11-09 ADR-097**：本类是算法层**唯一实例化与取用入口**——外部不得自己 `new` 算法类，同级硬件 Manager 不互持算法对象；回放与线激光轮廓算法也由本类惰性持有。

## 入口与配置

| 成员 | 说明 |
|---|---|
| `static AlgorithmManager Instance` | 单例（算法层唯一入口） |
| `WireFeedConfig WireFeed` | 送丝距离检测配置（强类型） |
| `WeldQualityConfig Quality` | 焊接质量检测配置（强类型） |
| `PlaybackAlgorithm Playback` | **2026-11-09** 回放算法（`EmguALG.RealtimeMonitor.Playback`，惰性创建，所有页面共用同一实例） |
| `ILineLaserContourAlgorithm LineLaserContour` | **2026-11-09** 线激光轮廓渲染算法（惰性创建，无可配置状态） |
| `int WireFeedVersion` / `int QualityVersion` | 配置版本号（消费方比对此值刷新） |
| `void ApplyConfig()` | 配置变更后分发至算法 |
| `PipelineConfig CreateEmptyPipelineConfig()` | 创建空白算法管线配置。UI 不再自行 `new PipelineConfig`，配置实例所有权归 Manager |
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
| `void DrawSpotMark(Mat frame, int x, int y)` | **2026-11-09** 光斑点十字标注（绿色 `(0,255,0)`、半长 20px、线宽 1；坐标非正或越界不画），坐标由调用方从硬件配置取出 |

## 事件

| 成员 | 说明 |
|---|---|
| `event EventHandler<AlgorithmCompletedEventArgs> AlgorithmCompleted` | 检测完成事件（**仅监控相机链路**；原焊缝特征上报链已按用户裁定整条删除——焊缝特征由线激光直接获取，见 ADR-007） |

## 关联

- 模块页：[[modules/EmguALG]]；决策：[[decisions/ADR-022-EmguALGThreeLayer]]、[[decisions/ADR-019-MonitorCamBoundaryAndEmguALGRefinement]]、[[decisions/ADR-097-algorithm-layer-ownership-single-entry]]
- 消费方：`MonitorCameraWorkflow`（检测执行 + 回放门面）、`LineLaserManager`（轮廓渲染）、`MonitorCamPage` / `FormMain`（配置面板，原 `AlgorithmManager.Load()` 调用点改此）
- 相机侧：[[api/MonitorCamManager]]
