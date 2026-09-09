---
title: EmguALG 模块 — 视觉算法（三层：Abstractions / 领域算法 / Manager）
date: 2026-09-08
tags: [模块, 图像算法, EmguCV, 三层架构, 送丝距离, 焊接质量]
---

# EmguALG 模块 — 视觉算法

> 视觉算法模块。底层原子算子集中在 `ImageAlgorithm.cs`（[[decisions/ADR-038-EmguALGThreeLayer]]）。
> **2026-09-08 ADR-042 三层改造**：新增 `Abstractions/` 抽象接口、两个领域算法目录（`WireFeedDistance/`、`WeldQuality/`）、`Manager/` 统一调度；**删除** `SeamRecognition/`（外部零引用已证实）、`Core/ProfileTransform.cs`（点云换算链）、`EmguConfiger/` 三个文件（`PipelineManager`/`JobManager`/`AlgorithmJob`）、焊缝特征上报链（用户裁定：焊缝特征由线激光直接获取，`PipelineManager.ReportExternalResult`→`WeldProcess.AlgorithmCompleted` 链路整条移除）。

## 目录结构（2026-09-08 后）

| 文件夹 / 文件 | 职责 |
|------|------|
| `Abstractions/IAlgorithm.cs` | `IAlgorithm` / `IConfigurableAlgorithm`（`ApplyConfig`）/ `IResultStore` 抽象约束 |
| `Abstractions/IResultStore.cs` | 结果存储抽象（池化快照 + 版本号） |
| `Core/AlgorithmBase.cs` | 统一算法基类：`Preprocess` 编排 + 图形算子封装 + `Execute(Mat)` 模板方法 + INI 契约（点云 mm↔px 变换段已删） |
| `Core/AlgorithmResult.cs` | 算法结果基类（`Success` / `ElapsedMs` / `ErrorMessage` / `Algorithm`） |
| `Core/AlgorithmOperations.cs` | **算子域枚举（2026-09-09 真编译补充迁入）**：`FilterOperation` / `MorphologyOperation` / `EdgeDetectionOperation` / `FeatureExtractionOperation`——原在被删的 `EmguConfiger/AlgorithmManager.cs` 命名空间级，ADR-042 删文件时漏迁；命名空间取 `AdaWeldSystem.EmguALG`（Stages 与 Core/* 均直接可见，零 using，ADR-020 单一定义点） |
| `Core/PreprocessConfig.cs` | 预处理配置（Filter / Morphology / Edge / LineLaser 专用）+ INI 契约（ADR-020） |
| `Core/UnitAttribute.cs` / `Core/RangeAttribute.cs` | `[Unit("mm")]` / `[Range(min,max)]` 参数特性 |
| `WireFeedDistance/` | 送丝距离检测：`WireFeedDistanceAlgorithm`（包装 `ImageAlgorithm` 第 8 区算子）+ `WireFeedConfig` + `WireFeedResult` |
| `WeldQuality/` | 焊接质量检测：`WeldQualityAlgorithm` + `WeldQualityConfig` + `WeldQualityResult` |
| `Manager/AlgorithmManager.cs` | **统一调度入口**（单例）：检测执行 + 配置分发 + 持久化，见 [[api/AlgorithmManager]] |
| `Manager/AlgorithmResultStore.cs` | 结果存储（池化快照 + 版本号比对，消费方零 GC 读） |
| `Manager/AlgorithmCompletedEventArgs.cs` | 完成事件参数 |
| `Stages.cs` | **保留降级**：现役价值仅剩 `PipelineConfig`（`ILAlgorithmEditForm` 占位传参）；各 Stage 类不再被流程使用 |
| `RealtimeMonitor/RealtimeMonitorAlgorithm.cs` | **保留不删**（ADR-042 裁决：0 消费方，作为第 8 区迁移源留档） |
| `ImageAlgorithm.cs` | **唯一原子算子文件**（静态库）：原 `PreWeldAlignmentConfig/Result`、`WeldQualityConfig/Result` 四类型外迁至领域目录，签名改为领域类型 |
| `ImageRoiTools.cs` | ROI 绘制工具 |

## 设计约束

| 约束 | 违反后果 |
|------|---------|
| 原子算子必须在 `ImageAlgorithm.cs` 实现 | 算法分散，违反 [[decisions/ADR-038-EmguALGThreeLayer]] |
| 业务语义只在领域算法内实现，不得直调 `ImageAlgorithm` 原子算子 | 算子库被污染、无法复用 |
| 算法返回原始值不做平滑 | 平滑由 [[modules/WeldParamControl]] 处理 |
| 结果读取走 `GetLatest*(out version)` 版本比对，禁止缓存 Mat 引用 | 池化快照被复写导致脏读 |
| ADR-001：`.cs` 不重写 `Dispose(bool)`，用 `DisposeComponents()` | 设计器报错 |
| ADR-002：C# 7.3 及以下，禁 auto-property initializer / 表达式体属性 / `out var` / 元组解构 | MSBuild v4.0 CS1519 |

## 调用方式（ADR-042 后唯一路径）

- 监控相机工作流：`AlgorithmManager.Instance.DetectWireFeed(mat)` / `DetectWeldQuality(mat)`；配置面板读 `Instance.WireFeed` / `Instance.Quality`，改后 `ApplyConfig()` + `Save()`。
- 异步结果：`AlgorithmCompleted` 事件或 `GetLatestWireFeed(out int version)` 轮询比对版本号。

## 已删除链路（ADR-042，勿再引用）

| 删除项 | 原用途 | 处置 |
|---|---|---|
| `EmguConfiger/AlgorithmManager.cs`（类名 **PipelineManager**） | 管线编排 + `ReportExternalResult` 焊缝上报 | 整删；焊缝特征由线激光直接获取（用户裁定） |
| `EmguConfiger/JobManager.cs` + `AlgorithmJob.cs` | Job 切换体系 | 整删（强类型配置已由领域目录承接） |
| `SeamRecognition/`（SeamModel / SeamRecognitionAlgorithm） | 焊缝识别 | 整删（模块外引用 = 0 已 Grep 证实） |
| `Core/ProfileTransform.cs` | 点云 mm↔px 换算 | 整删（点云输入链移除；`AlgorithmBase` 点云变换段同步删除） |
| `WeldProcess._lastSeamFeature` / `AlgorithmCompleted` 订阅 / `ComputeAndCacheHorizontalMove(SeamFeatureResult,...)` | 焊缝特征消费 | 整删；[[modules/MotionControl]] `MoveControlData` 水平移动缓存同步清理 |

## 与外部模块关系

- [[modules/MonitorCam]]：`MonitorCameraWorkflow` 调 `DetectWireFeed` / `DetectWeldQuality`；相机三层见 [[api/MonitorCamManager]]
- [[modules/LineLaserCam]]：采集完成后调用 `ImageAlgorithm.DrawPointsDefaultRange`（原子算子，不变）
- [[api/ILAlgorithmEditForm]]：仍以 `Stages.PipelineConfig` 为模块 A 占位传参（后续 re-point 到领域配置）
- ~~[[modules/WeldParamControl]] 经 `PipelineManager.AlgorithmCompleted` 获取焊缝特征~~（2026-09-08 ADR-042 删除）

---

*来源：AdaWeldSystem/EmguALG/（原 `新WIKI/算法/算法架构设计.md` 已并入本模块文档）*
