---
title: ADR-038 算法模块（EmguALG）三层改造：两检测统一调度 + 点云/焊缝上报链删除
date: 2026-09-08
tags: [决策, EmguALG, 算法, 三层架构, PipelineManager, ADR-003]
status: accepted
---

# ADR-038：算法模块（EmguALG）三层改造

> ℹ️ **沿革注（2026-09-14，ADR-048）**：本页「2026-09-09 真编译补充修复」条中「`Core/AlgorithmOperations.cs`（`AdaWeldSystem.EmguALG` 命名空间）」为当时写法；现役 `EmguALG/` 各子目录已随目录对齐为 `AdaWeldSystem.EmguALG.Core`（该文件所在）／`.Abstractions`／`.Manager`／`.LineLaserContour`／`.EmguConfiger`／`.RealtimeMonitor[.WeldQuality / .WireFeedDistance]`。三层结构结论不变。见 [[decisions/ADR-048-NamespaceDirectoryAlignment]]。

## 背景

`EmguALG` 原为「算子静态库 + PipelineManager 单例」结构：职责过载（配置/阶段编排/焊缝特征/点云识别）、无抽象接口、无结果缓存、无统一调度入口。二手《算法程序改造指导 v2.0》提出目标架构，但**基线为另一形态**，与代码现实存在三处错位：

| # | 文档声称 | 代码现实（2026-09-08 核验） | 处置 |
|---|---|---|---|
| 1 | 拆 `AlgorithmManager` | 该类实为 **`PipelineManager`**（位于 `EmguConfiger/AlgorithmManager.cs`） | 按现实拆解 |
| 2 | 迁移 `RealtimeMonitorAlgorithm.CheckCentering/CheckQuality` | 工作流实际调 **`ImageAlgorithm.DetectPreWeldAlignment/DetectWeldQuality`**（第 8 区，强类型配置 + INI 已有） | 迁移 = 包装，不重写 |
| 3 | 删 PipelineManager、线激光不依赖算法模块 | 存在**活跃**上报链：`LineLaserWorkflow → ReportExternalResult → WeldProcess.AlgorithmCompleted → _lastSeamFeature → MoveControlData` | 用户裁定：**整条删除**（焊缝特征由线激光直接获取） |

## 决策

1. **三层目录**（在 `EmguALG/` 内重排，不平行新建 `AlgorithmModule/`）：
   ```
   EmguALG/
   ├── Abstractions/     # IAlgorithm / IConfigurableAlgorithm / IResultStore（纯新增）
   ├── Core/             # AlgorithmBase / AlgorithmResult / PreprocessConfig 保留
   ├── WireFeedDistance/ # 送丝距离检测：算法类 + WireFeedConfig + WireFeedResult
   ├── WeldQuality/      # 焊接质量检测：算法类 + WeldQualityConfig + WeldQualityResult
   └── Manager/          # AlgorithmManager（统一调度）+ AlgorithmResultStore + AlgorithmCompletedEventArgs
   ```
2. **配置/结果类型外迁并改名**：`PreWeldAlignmentConfig/Result` → `WireFeedConfig/WireFeedResult`；`WeldQualityConfig/Result` 移入 `WeldQuality/`；二者均派生 `AlgorithmResult`（满足 `IAlgorithm<T>` 泛型约束）。
3. **算法类包装既有算子**（ADR-003：算子仍集中在 `ImageAlgorithm.cs`），只加契约、计时、防重入与异常收敛。
4. **消费方式三选一**：同步调用（`DetectWireFeed/DetectWeldQuality`）、结果缓存轮询（`GetLatestWireFeed/GetLatestQuality` + 版本号）、低频完成事件（`AlgorithmCompleted`）。
5. **删除清单**（用户裁定 + 0 消费方核验）：`SeamRecognition/` 整目录、`Core/ProfileTransform.cs`、`ImageAlgorithm` 两处 `ConvertContourToMat(PointCloudData…)` 重载、`AlgorithmBase.BuildTransform`、`PipelineManager` 及 `SeamFeatureResult`/`SeamFeatureCalculatedEventArgs`/`AlgorithmCompletedEventArgs`（旧）、`JobManager`/`AlgorithmJob`（依赖已删 PipelineManager 且 0 消费方）、`MonitorCam/MonitorAlgorithmManager.cs`（参数并入 `AlgorithmManager`）。
6. **保留**：`Stages.cs`（内含 `PipelineConfig`，IL 算法编辑页仍以它为占位传参）、`RealtimeMonitor/RealtimeMonitorAlgorithm.cs`（0 消费方但为迁移源，不主动删除）。

## 后果

### 正面
- 抽象层/实现层/Manager 边界清晰，与相机、运控、线激光同构；换算法后端只动实现层。
- 结果不再走高频事件，改为池化快照 + 版本号轮询，消除事件风暴风险。
- 焊缝上报链删除后，线激光 → 工艺的链路只剩一条（线激光 Manager 直出），消除双数据源。

### 负面 / 遗留（须现场确认）
- ⚠️ **行为变化**：删除 `PipelineManager.AlgorithmCompleted` 订阅后，`WeldProcess.TotalExecuteCount` / `ConsecutiveFailureCount` 不再自增，连续失败中止判定（阈值 5）当前不会触发——需后续按新数据源补齐（OPEN）。
- `WeldProcess.AutoAction` 去掉 `seamFeature` 形参；`MoveControlData.ComputeAndCacheHorizontalMove(SeamFeatureResult, robotX)` 删除，水平移动缓存的写入 API（`CacheHorizontalMove`）保留待新数据源接入。
- **真编译待 Visual Studio**；Python 静态校验 15/15 通过。
- **2026-09-09 真编译补充修复**：VS 编译暴露删文件时漏迁的 4 个命名空间级算子枚举（`FilterOperation`/`MorphologyOperation`/`EdgeDetectionOperation`/`FeatureExtractionOperation`）→ 恢复至 `Core/AlgorithmOperations.cs`（`AdaWeldSystem.EmguALG` 命名空间，ADR-020 单一定义点）。教训：**删除代码文件前必须清单化其全部命名空间级类型并逐一迁移**（枚举最易漏，静态校验按符号点查抓不住）。同日 MonitorCam 侧真编译暴露 CS0118：命名空间与类名同形（`MonitorCam.MecaVisionCam`）实例化必须「命名空间.类名」限定（线激光先例同构）。
- OPEN：① 送丝距离/质量配置字段沿用现实字段（文档提议的 WarnMM/FailMM/PixelMmScale 未引入，待标定方案确定）② 咬边/飞溅仍为占位逻辑 ③ Job 强类型化待 UI 需求明确后重建。

## 相关页面

- [[modules/EmguALG]] —— 算法模块现状与目录
- [[modules/MonitorCam]]、[[decisions/ADR-037-MecaVisionMonitorCamera]] —— 输入源（监控相机）
- [[decisions/ADR-038-EmguALGThreeLayer]] —— 算子库唯一文件约束（仍遵守）
- [[decisions/ADR-017-EnumDeduplication]]
