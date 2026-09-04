---
title: EmguALG 模块 — 视觉算法
date: 2026-08-03
tags: [模块, 图像算法, EmguCV, 焊缝识别, 实时监控]
---

# EmguALG 模块 — 视觉算法

> 视觉算法模块。底层原子算子仍集中在 `ImageAlgorithm.cs`（见 [[decisions/ADR-003-SingleAlgorithmFile]]）；
> 算法调度与配置管理已拆分为「统一基类 + 两类领域算法单例」，各自承担 INI 契约。
> 详细架构见本页「核心文件（新结构）」一节（原 `新WIKI/算法/算法架构设计.md` 已并入本模块文档）。

## 核心文件（新结构）

| 文件夹 / 文件 | 职责 |
|------|------|
| `Core/AlgorithmBase.cs` | 统一算法基类：`Preprocess` 编排 + 图形算子封装 + mm↔px 变换 + `Execute(Mat)` 模板方法 + INI 契约抽象（`SaveToIni`/`LoadFromIni`/`ExecuteCore`） |
| `Core/AlgorithmResult.cs` | 算法结果基类（`Success` / `ElapsedMs` / `ErrorMessage` / `Algorithm`） |
| `Core/PreprocessConfig.cs` | 预处理配置（Filter / Morphology / Edge / LineLaser 专用）+ INI 契约。算子枚举统一引用 `EmguALG` 命名空间（ADR-020） |
| `Stages.cs` | **所有 Stage 类合并为一个文件（2026-08-03 合并）**：`StageBase`（抽象基类）+ `FilterStage` / `MorphologyStage` / `EdgeDetectionStage` / `FeatureExtractionStage` / `TemplateMatchStage` + `PipelineConfig`。原 6 个独立文件合并为 1 个。减少文件数量，降低项目文件膨胀 |
| `Core/ProfileTransform.cs` | mm↔px 唯一换算点（`FromPointCloud` / `ToPixel` / `ToMM`） |
| `Core/UnitAttribute.cs` / `Core/Attributes/RangeAttribute.cs` | `[Unit("mm")]` / `[Range(min,max)]` 参数特性（UI 提示用，不落盘） |
| `SeamRecognition/SeamModel.cs` | `ProfilePointMM` / `SeamJointType` / `SeamEdgeMM` / `SeamMatchResult`（纯几何 / 纯数据，无 EMGU） |
| `SeamRecognition/SeamRecognitionAlgorithm.cs` | 焊缝识别领域算法单例 `Instance`；`SeamRecognitionConfig`（**替代旧 `PipelineConfig`**）+ `SeamRecognitionResult` |
| `RealtimeMonitor/RealtimeMonitorAlgorithm.cs` | 实时监控领域算法单例 `Instance`（无 Job）；`MonitorConfig` + `CenteringCheckResult` / `SeamQualityResult` |
| `ImageAlgorithm.cs` | **唯一原子算子文件**（静态库，保留；新增 `ConvertContourToMat(pc, transform)` / `FitLine` 等重载） |
| `EmguConfiger/` | **配置管理文件夹（2026-08-03 新增）**： |
| `EmguConfiger/JobManager.cs` | Job CRUD + 切换 + INI 持久化（启动 `Initialize()` 加载；见 [[decisions/ADR-011-WorkflowAsAdjustmentDriver]]） |
| `EmguConfiger/AlgorithmJob.cs` | Job 数据容器，内含 `SeamRecognitionConfig` |
| `EmguConfiger/AlgorithmManager.cs` | **PipelineManager**（保留为编译桥接适配器，Workflow 和 UI 仍调用其 `Execute` / `ReportExternalResult` / `AlgorithmCompleted` 事件） |
| `ImageRoiTools.cs` | ROI 绘制工具 |

> **2026-08-03 重构说明**：Stage 类文件（`StageBase.cs` / `FilterStage.cs` / `MorphologyStage.cs` / `EdgeDetectionStage.cs` / `FeatureExtractionStage.cs` / `TemplateMatchStage.cs` / `PipelineConfig.cs`）合并为单一 `Stages.cs`，遵循"内部紧密耦合的模块不拆分"原则。新增 `EmguConfiger/` 文件夹收纳 `AlgorithmJob`、`AlgorithmManager`、`JobManager`、`PipelineConfig` 等配置管理类。

## 设计约束

| 约束 | 违反后果 |
|------|---------|
| 原子算子必须在 `ImageAlgorithm.cs` 实现 | 算法分散，违反 [[decisions/ADR-003-SingleAlgorithmFile]] |
| 业务语义只在领域算法 `ExecuteCore` 内实现，不得直调 `ImageAlgorithm` 原子算子 | 算子库被污染、无法复用 |
| 单位：几何量全程 mm，仅在 `ProfileTransform` 处转 px | 换分辨率即失效 |
| 算法返回原始值不做平滑 | 平滑由 [[modules/WeldParamControl]] 处理 |
| ADR-001：`.cs` 不重写 `Dispose(bool)`，用 `DisposeComponents()` | 设计器报错 |
| ADR-002：C# 7.3 及以下，禁 auto-property initializer / 表达式体属性 / `out var` / 元组解构 | MSBuild v4.0 CS1519 |

## 调用方式（新单例）

- 焊缝识别：`SeamRecognitionAlgorithm.Instance.SetConfig(job.Config.Clone())` 切换 Job；`Instance.Execute(pointCloud, imgW, imgH)` 返回 `SeamRecognitionResult`（几何量 mm + `Visualization` 仅可视化）。
- 实时监控（无 Job，全局）：`RealtimeMonitorAlgorithm.Instance.CheckCentering(image)` / `CheckQuality(image)`。

## 过渡桥接（PipelineManager）

`AlgorithmManager.cs`（`PipelineManager` / `PipelineConfig`）**暂保留为编译桥接适配器**：`Workflow/LineLaserWorkflow.cs`、`WeldParamControl/WeldProcess.cs`、`Workflow/MotionControlWorkflow.cs`、`JobManager.cs`、UI 配置页（`EmguAlgoPage` / `AlgorithmEditForm` / `LLCamWorkJob`）仍调用其 `Execute` / `ReportExternalResult` / `AlgorithmCompleted` / `PipelineConfig`。新 API 当前未暴露 `Execute(Mat)` 重载与结果事件，迁移上述调用点需在 VS x64 中补 API 并验证（见算法架构设计 §12）。

## 监控相机算法区（第 8 区）

> `ImageAlgorithm.cs` 末尾 `#region 8. 监控相机算法区` 供 [[modules/MonitorCam]] 调用（独立模块，与 `RealtimeMonitor` 区分；监控相机走 `MonitorAlgorithmManager`，见 [[decisions/ADR-009-MonitorCameraModule]]）。

| API | 说明 |
|-----|------|
| `DetectPreWeldAlignment(Mat, PreWeldAlignmentConfig)` | 焊前光斑 / 焊丝对中 |
| `DetectWeldQuality(Mat, WeldQualityConfig)` | 焊中质量检测 |

## 与外部模块关系

- [[modules/SmartRayCam]] 采集完成后调用 `ImageAlgorithm.DrawPointsDefaultRange`
- [[modules/WeldParamControl]] 暂经 `PipelineManager.AlgorithmCompleted` 获取焊缝特征（待迁移到 `SeamRecognitionResult`）
- [[modules/DeviceControl]] 暂经 `PipelineManager.Execute` / `ReportExternalResult`（待迁移到 `SeamRecognitionAlgorithm.Instance`）
- [[modules/MonitorCam]] 调用 `DetectPreWeldAlignment` / `DetectWeldQuality`；自身算法由 `MonitorAlgorithmManager` 管理（与 EmguALG 的 `AlgorithmManager` 不是一回事）
- [[api/AlgorithmEditForm]]（Sub3UI 弹窗）当前编辑 `PipelineConfig`（待 re-point 到 `SeamRecognitionConfig`）

---

*来源：AdaWeldSystem/EmguALG/（原 `新WIKI/算法/算法架构设计.md` 已并入本模块文档）*