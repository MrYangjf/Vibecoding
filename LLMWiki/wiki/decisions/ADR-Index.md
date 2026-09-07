---
title: ADR 编号总表（现行编号 / 旧编号映射）
date: 2026-09-07
updated: 2026-09-07
status: accepted
tags: [索引, 决策, ADR, 编号体系, 知识库治理]
---

# ADR 编号总表

> **2026-09-07 全库重排**：删除正运动（ZMotion）三项决策后，为保持编号连续，后续 ADR 编号整体前移，
> 现为 **001~037 连续无断号**。本表是编号换算的**唯一准绳**。
>
> - 各 ADR 页 frontmatter 保留 `previous_id` 字段，页面内标题编号已与文件名对齐。
> - `logs/` 工作日志、`raw/` 原档与 `AdaWeldSystem/**/*.cs` 代码注释中的编号**已同步为新编号**。
> - 检索 2026-09-07 之前的归档文本时，按本表「旧编号」列换算。

## 重排映射（仅列出编号变动者）

| 旧 → 新 | 旧 → 新 | 旧 → 新 | 旧 → 新 |
|---|---|---|---|
| 024 → 022 | 025 → 023 | 026 → 024 | 028 → 025 |
| 029 → 026 | 030 → 027 | 031 → 028 | 032 → 029 |
| 033 → 030 | 034 → 031 | 035 → 032 | 036 → 033 |
| 037 → 034 | 038 → 035 | 039 → 036 | 040 → 037 |

**已删除且不再保留编号的决策**（正运动专属，结论由 [[decisions/ADR-037-ZMotionRemovalAndDeltaLanding]] 取代）：

| 旧编号 | 主题 | 处置 |
|---|---|---|
| ADR-022 | 正运动控制器接入架构 | 整页删除，结论由 ADR-037 取代 |
| ADR-023 | RSI-CAMBOX 硬件级实时焊缝跟踪架构 | 整页删除；台达侧承接方案 OPEN |
| ADR-027 | 默认初始化切到正运动控制器 | 整页删除；初始化改走 `MontionManager.Initialization()` |

> ⚠️ 上表三个旧编号在重排后**已被其它决策占用**（022=布局容器自由化、023=Dispose 全覆盖、027=权责边界），
> 检索历史文本时务必区分，避免张冠李戴。

## 全部 ADR（001~037）

| 现行编号 | 旧编号 | 主题 | 状态 | 日期 |
|---|---|---|---|---|
| [[decisions/ADR-001-DisposePattern]] | —（沿用） | ADR-001 Dispose 模式决策 | accepted | 2026-07-01 |
| [[decisions/ADR-002-CS73-Constraint]] | —（沿用） | ADR-002 C# 7.3 语法约束决策 | accepted | 2026-07-01 |
| [[decisions/ADR-003-SingleAlgorithmFile]] | —（沿用） | ADR-003 单算法文件决策 | accepted | 2026-07-01 |
| [[decisions/ADR-004-WorkflowStepEnum]] | —（沿用） | ADR-004 Step 状态机决策 | accepted | 2026-07-01 |
| [[decisions/ADR-005-CallbackAcquisition]] | —（沿用） | ADR-005 回调等待取图决策 | accepted | 2026-07-01 |
| [[decisions/ADR-006-CommRefactor]] | —（沿用） | ADR-006 Comm 模块重构决策 | accepted | 2026-07-02 |
| [[decisions/ADR-007-ConfigLayout]] | —（沿用） | ADR-007 Config 文件夹分层决策 | accepted | 2026-07-03 |
| [[decisions/ADR-008-CommXmlSeparation]] | —（沿用） | ADR-008 通讯 XML 配置按设备类型分离 | accepted | 2026-07-03 |
| [[decisions/ADR-009-MonitorCameraModule]] | —（沿用） | ADR-009 监控相机模块架构决策 | accepted | 2026-07-13 |
| [[decisions/ADR-010-WeldActionRecord]] | —（沿用） | ADR-010 WeldActionRecord 归属与双记录设计 | accepted | 2026-07-15 |
| [[decisions/ADR-011-WorkflowAsAdjustmentDriver]] | —（沿用） | ADR-011 工作流作为焊接调整主驱动 | accepted | 2026-07-15 |
| [[decisions/ADR-012-MotionControlModule]] | —（沿用） | ADR-012 运控调整模块架构决策 | accepted | 2026-07-16 |
| [[decisions/ADR-013-WorkflowAsHub]] | —（沿用） | ADR-013 Workflow 模块作为流程管理中枢 | accepted | 2026-07-17 |
| [[decisions/ADR-014-MonitorCamPage-AlgorithmInline]] | —（沿用） | ADR-014 监控相机页面命名与算法参数内联 | accepted | 2026-07-17 |
| [[decisions/ADR-015-CameraConnectionStateDecoupled]] | —（沿用） | ADR-015 相机连接状态与工作流程状态解耦 | accepted | 2026-07-21 |
| [[decisions/ADR-016-CameraSelectorUnifiedToApi]] | —（沿用） | ADR-016 CameraSelector 上提至 LineLaserCam/Api 统一对外接口层 | accepted | 2026-07-21 |
| [[decisions/ADR-017-AlgorithmEditInterfaceSplit]] | —（沿用） | ADR-017 算法编辑界面按接口分隔（Tabpage / UIPage + AddPage，单独个例仅记录为当前） | accepted | 2026-07-27 |
| [[decisions/ADR-018-UIFrameworkMigration]] | —（沿用） | ADR-018 UI 框架从 SunnyUI 迁移至 AntdUI | accepted | 2026-07-20 |
| [[decisions/ADR-019-DialogWindowToModalUserControl]] | —（沿用） | ADR-019 子对话窗承载方式：AntdUI.Window+PageHeader → Modal 承载的 UserControl | accepted | 2026-07-30 |
| [[decisions/ADR-020-EnumDeduplication]] | —（沿用） | ADR-020 枚举去重策略 — 子命名空间禁止重复定义父命名空间枚举 | accepted | 2026-08-01 |
| [[decisions/ADR-021-NuGetLocalization]] | —（沿用） | ADR-021 NuGet 本地化 — 所有依赖 DLL 从 3rdDepend 引用 | accepted | 2026-08-06 |
| [[decisions/ADR-022-LayoutContainerFreedom]] | 024 | ADR-022 布局容器自由化（解除 GridPanel/FlowPanel 强制使用） | accepted | 2026-08-12 |
| [[decisions/ADR-023-DisposePatternFullCoverage]] | 025 | ADR-023 Dispose 模式全覆盖 — 非 UI 类统一标准 IDisposable | accepted | 2026-08-19 |
| [[decisions/ADR-024-LineLaserWorkflowRefactor]] | 026 | ADR-024 线激光工作流分步重构（switch-case + step） | accepted | 2026-08-20 |
| [[decisions/ADR-025-CodeSimplificationStandard]] | 028 | ADR-025 代码精简规范沉淀（精准执行、免重复输入） | accepted | 2026-08-21 |
| [[decisions/ADR-026-YinglaiDataFlow]] | 029 | ADR-026 英莱线激光数据流架构 — CamRun 分发 + Running 单态监听调整 | accepted | 2026-08-18 |
| [[decisions/ADR-027-WorkflowResponsibilityBoundary]] | 030 | ADR-027 流程与子设备对象权责边界（R1~R5） | accepted | 2026-08-31 |
| [[decisions/ADR-028-SafetyCheckConsolidation]] | 031 | ADR-028 安全检查三文件合并为单一安全检查流程 | accepted | 2026-08-31 |
| [[decisions/ADR-029-ButtonShadowDeviceSwitch]] | 032 | ADR-029 MainPage 硬件快捷开关 FloatButton→ButtonShadow | accepted | 2026-08-31 |
| [[decisions/ADR-030-ProductLifecycleRecordModule]] | 033 | ADR-030 产品生命周期记录模块与故障记录归口（DB 下沉 + 消费方归位） | accepted | 2026-08-31 |
| [[decisions/ADR-031-ThreeStateModelRefactor]] | 034 | ADR-031 主控设计三态模型重构（SubDeviceState / SubDeviceWeldStatus / MainDeviceStatus） | accepted | 2026-09-02 |
| [[decisions/ADR-032-ArchitectureRawSource]] | 035 | ADR-032 架构原档单一来源约定（raw/architecture） | accepted | 2026-09-02 |
| [[decisions/ADR-033-RawDesignRefinement20260903]] | 036 | ADR-033 原档 9-03 细化：主控设计完全重构与冲突裁定 | accepted | 2026-09-03 |
| [[decisions/ADR-034-MainDeviceStateSemantics]] | 037 | ADR-034 主设备状态机语义修正与初始化时序重构 | accepted | 2026-09-04 |
| [[decisions/ADR-035-ErrorReportingHierarchy]] | 038 | ADR-035 报错分层与状态切换零日志 | accepted | 2026-09-04 |
| [[decisions/ADR-036-MotionControllerDeltaReplacement]] | 039 | ADR-036 运动控制器采用台达 EtherCAT（全新模块，结构与对外消费按原档） | accepted | 2026-09-06 |
| [[decisions/ADR-037-ZMotionRemovalAndDeltaLanding]] | 040 | ADR-037 移除正运动（ZMotion）并全面落地台达 EtherCAT + 消费方全量对接 | accepted | 2026-09-07 |

---

## 关联

- [[index/index]] — 知识库总索引（§7 设计决策，按状态分类）
- [[decisions/ADR-037-ZMotionRemovalAndDeltaLanding]] — 本次重排的触发决策
- [[guides/DeltaEtherCAT-Deployment]] — 台达部署规范（驱动 · 原生库 · 项目内落地）
