---
title: ADR 编号总表（现行编号 / 旧编号映射）
date: 2026-09-07
updated: 2026-09-14
status: accepted
tags: [索引, 决策, ADR, 编号体系, 知识库治理]
---

# ADR 编号总表

> **现行编号：001~048 连续无断号**（2026-09-09 全库知识治理重排后，续增 ADR-039/040/041/042/043/044/045/046/047/048）。本表是编号换算的**唯一准绳**。
>
> **编号沿革（两度重排）**：
> - **2026-09-07**：删除正运动（ZMotion）三项决策后前移，得 001~037；
> - **2026-09-08**：新增 ADR-038/039/040（线激光三层）、041（麦格威监控相机）、042（EmguALG 三层），达 001~042；
> - **2026-09-09**：删除四项整页失效决策（原 003/004/016/026）后再次前移，得 **001~038**；
> - **2026-09-09 / 09-11**：续增 ADR-039（监控相机边界澄清 + EmguALG 五层细化）与 ADR-040（线激光引导 Y 轴轨迹构造）。
> - **2026-09-14**：续增 ADR-041（WeldParamControl 算法分层：抽象基类 + 实现类 + Manager 唯一入口），现行 **001~041 连续无断号**。
> - **2026-09-14（同日续增）**：续增 ADR-042（模块组织范式沉淀：Core + 抽象层 + 实现层 + Manager 四件套，标准页 [[standards/ModuleOrganizationPattern]]），现行 **001~042 连续无断号**。
> - **2026-09-14（同日续增·本轮）**：续增 ADR-043（算法纯净性与记录职责隔离：算法**只计算不落盘**、记录请求走事件、落盘归 `ProductFileControl` 异步执行；配套 [[standards/ModuleOrganizationPattern]] 新增 **H9**「实现层只计算」+ 教训页 [[lessons/AlgorithmControlRecordIsolation]]），现行 **001~043 连续无断号**。
> - **2026-09-14（同日续增·配置合一）**：续增 ADR-044（焊接算法配置合一：~~`SeamGuideConfig`~~ + ~~`WeldParamAdjustmentConfig`~~ → 单一 `WeldAlgorithmsConfig`，XML 两节名与文件路径不变、存量配置零迁移；Manager 收敛为一实例 `AlgorithmsConfig` + 一对 `LoadAlgorithmsConfig()` / `SaveAlgorithmsConfig()`），现行 **001~044 连续无断号**。
> - **2026-09-14（ADR-040 废弃）**：ADR-040「线激光引导 Y 轴轨迹构造」演进为 ADR-041 中的 `SeamTrackingAlgorithm`（`WeldParamManager` 统一管理、算法与控制器分离），状态由 accepted 改为 **deprecated**，不回收编号。
> - **2026-09-14（同日续增·双模块重构）**：续增 ADR-045（Comm 模块重构：抽象层 CommChannelBase + 5 实现 + Manager 唯一口，KUKA 门面并入、Profinet/GSDML 删除、以太网重写 EthernetXmlComm）与 ADR-046（产品记录模块重构：ProductRecordBase 抽象 + 三记录类 + ProductFileRecordManager，ADR-043 订阅方 TODO 闭环），现行 **001~046 连续无断号**。
> - **2026-09-14（同日续增·记录类文件自包含）**：续增 ADR-047（RecordFileStore/RecordFrame 并入 SeamTrackRecord.cs、WeldActionRecord 并入 WeldParamAdjustRecord.cs、SmartRayConverter 整链删除、SeamAdjustRecord→WeldParamAdjustRecord 改名），现行 **001~047 连续无断号**。
> - **2026-09-14（同日续增·命名空间对齐）**：续增 ADR-048（命名空间与目录严格对齐：`namespace = AdaWeldSystem + 目录路径`，覆盖 UIDesign/MainDeviceControl/Comm/SQLiteDBControl 四组错位共 68 文件；厂商 SDK 与 ProductFileControl 扁平目录为登记例外），现行 **001~048 连续无断号**。同批废止 ADR-016 §3 / ADR-027 / ADR-038 / ADR-043 §7 / ADR-045 §4 的「命名空间保持不变」条款（各页已加沿革横幅）。
> - **2026-09-11（补齐）**：40 个 ADR 页 frontmatter `title` / H1 / `tags` 的**自引用编号已逐页订正为现行编号**——此前 35 页仍停留在 09-08 时代编号（如 `ADR-003-CallbackAcquisition.md` 页内写 `ADR-005`），并清理编号 `041~044` 的失效活引用（→037/038）。正文的历史叙述与交叉引用保留原文。
> - 各 ADR 页 frontmatter 的 `previous_id` 字段已移除（两代重排后编号歧义，沿革以本表为准）。
> - `logs/` 工作日志、`AdaWeldSystem/**/*.cs` 代码注释与 skills 副本中的编号**已按 09-09 映射同步**；
>   更早期归档文本中的裸编号可能仍属旧编号体系，检索时按本表换算（历史日志原文未改写，以当时语境为准）。

## 2026-09-09 重排映射（09-08 时代编号 → 现行编号，仅列变动者）

| 旧 → 新 | 旧 → 新 | 旧 → 新 | 旧 → 新 |
|---|---|---|---|
| 005 → 003 | 006 → 004 | 007 → 005 | 008 → 006 |
| 009 → 007 | 010 → 008 | 011 → 009 | 012 → 010 |
| 013 → 011 | 014 → 012 | 015 → 013 | 017 → 014 |
| 018 → 015 | 019 → 016 | 020 → 017 | 021 → 018 |
| 022 → 019 | 023 → 020 | 024 → 021 | 025 → 022 |
| 027 → 023 | 028 → 024 | 029 → 025 | 030 → 026 |
| 031 → 027 | 032 → 028 | 033 → 029 | 034 → 030 |
| 035 → 031 | 036 → 032 | 037 → 033 | 038 → 034 |
| 039 → 035 | 040 → 036 | 041 → 037 | 042 → 038 |

**已删除且不再保留编号的决策（2026-09-09，整页失效四项）**：

| 旧编号 | 主题 | 删除原因 | 去向 |
|---|---|---|---|
| ADR-003 | 单算法文件决策（ImageAlgorithm.cs 唯一） | 算子集中结论被 ADR-038 三层改造部分推翻，单文件决策作为规范已失效（算子仍集中，但算法架构已三层化） | [[decisions/ADR-038-EmguALGThreeLayer]] |
| ADR-004 | Step 状态机决策（7 Step 枚举） | `WorkflowStep` 枚举与步骤驱动机制已于 2026-09-03 整体清除，改 `RunStep` bool 驱动 | [[architecture/DeviceControlArchitecture]] §5 |
| ADR-016 | CameraSelector 上提至 LineLaserCam/Api | `CameraSelector`/`ICameraRun` 已随 ADR-038 物理删除，整页结论失效 | [[decisions/ADR-034-LineLaserThreeLayerRefactor]] |
| ADR-026 | 英莱线激光数据流（CamRun 分发 + Running 单态监听） | `CamRun` 已删除；「回调驱动显示」被 ADR-035 推翻（主页面改线程轮询） | [[decisions/ADR-035-LineLaserResponsibilitySplit]] |

> ⚠️ 上述四个旧编号在重排后**已被其它决策占用**（003=回调等待取图、004=Comm 重构、016=Modal 承载对话窗、026=产品记录归口），
> 检索历史文本时务必区分，避免张冠李戴。

## 2026-09-07 重排映射（历史，编号为 09-08 时代之前的旧体系）

| 旧 → 新 | 旧 → 新 | 旧 → 新 | 旧 → 新 |
|---|---|---|---|
| 024 → 022 | 025 → 023 | 026 → 024 | 028 → 025 |
| 029 → 026 | 030 → 027 | 031 → 028 | 032 → 029 |
| 033 → 030 | 034 → 031 | 035 → 032 | 036 → 033 |
| 037 → 034 | 038 → 035 | 039 → 036 | 040 → 037 |

**已删除（2026-09-07，正运动专属三项）**：

| 旧编号 | 主题 | 处置 |
|---|---|---|
| ADR-022 | 正运动控制器接入架构 | 整页删除，结论由 ADR-033（现行，ZMotionRemoval）取代 |
| ADR-023 | RSI-CAMBOX 硬件级实时焊缝跟踪架构 | 整页删除；台达侧承接方案 OPEN（PVT B 套流式已落地于 ADR-035） |
| ADR-027 | 默认初始化切到正运动控制器 | 整页删除；初始化改走 `MontionManager.Initialization()` |

> 检索 2026-09-07 之前的文本：先按本表查得 09-08 时代编号，再按上节 09-09 映射换算为现行编号。

## 全部 ADR（001~048）

| 现行编号 | 09-08 时代编号 | 主题 | 状态 | 日期 |
|---|---|---|---|---|
| [[decisions/ADR-001-DisposePattern]] | 001 | ADR-001 Dispose 模式决策 | accepted | 2026-07-01 |
| [[decisions/ADR-002-CS73-Constraint]] | 002 | ADR-002 C# 7.3 语法约束决策 | accepted | 2026-07-01 |
| [[decisions/ADR-003-CallbackAcquisition]] | 005 | ADR-003 回调等待取图决策（有界等待合法） | accepted | 2026-07-01 |
| [[decisions/ADR-004-CommRefactor]] | 006 | ADR-004 Comm 模块重构决策 | accepted | 2026-07-02 |
| [[decisions/ADR-005-ConfigLayout]] | 007 | ADR-005 Config 文件夹分层决策 | accepted | 2026-07-03 |
| [[decisions/ADR-006-CommXmlSeparation]] | 008 | ADR-006 通讯 XML 配置按设备类型分离 | accepted | 2026-07-03 |
| [[decisions/ADR-007-MonitorCameraModule]] | 009 | ADR-007 监控相机模块架构决策（独立模块 + SDK 抽象；海康实现已由 ADR-037 换麦格威） | accepted | 2026-07-13 |
| [[decisions/ADR-008-WeldActionRecord]] | 010 | ADR-008 WeldActionRecord 归属与双记录设计（归属目录已迁，双记录仍有效） | superseded（部分） | 2026-07-15 |
| [[decisions/ADR-009-WorkflowAsAdjustmentDriver]] | 011 | ADR-009 工作流作为焊接调整主驱动 | accepted | 2026-07-15 |
| [[decisions/ADR-010-MotionControlModule]] | 012 | ADR-010 运控调整模块架构决策（历史，控制器已换台达） | accepted（沿革） | 2026-07-16 |
| [[decisions/ADR-011-WorkflowAsHub]] | 013 | ADR-011 Workflow 模块作为流程管理中枢（中枢目录与监督机制均已变更） | superseded（部分） | 2026-07-17 |
| [[decisions/ADR-012-MonitorCamPage-AlgorithmInline]] | 014 | ADR-012 监控相机页面命名与算法参数内联 | accepted | 2026-07-17 |
| [[decisions/ADR-013-CameraConnectionStateDecoupled]] | 015 | ADR-013 相机连接状态与工作流程状态解耦（结论有效，承载者已改 LineLaserManager） | accepted（沿革） | 2026-07-21 |
| [[decisions/ADR-014-AlgorithmEditInterfaceSplit]] | 017 | ADR-014 算法编辑界面按接口分隔 | accepted | 2026-07-27 |
| [[decisions/ADR-015-UIFrameworkMigration]] | 018 | ADR-015 UI 框架从 SunnyUI 迁移至 AntdUI | accepted | 2026-07-20 |
| [[decisions/ADR-016-DialogWindowToModalUserControl]] | 019 | ADR-016 子对话窗承载方式：Modal 承载的 UserControl | accepted | 2026-07-30 |
| [[decisions/ADR-017-EnumDeduplication]] | 020 | ADR-017 枚举去重策略 | accepted | 2026-08-01 |
| [[decisions/ADR-018-NuGetLocalization]] | 021 | ADR-018 NuGet 本地化（3rdDepend 本地引用） | accepted | 2026-08-06 |
| [[decisions/ADR-019-LayoutContainerFreedom]] | 022 | ADR-019 布局容器自由化 | accepted | 2026-08-12 |
| [[decisions/ADR-020-DisposePatternFullCoverage]] | 023 | ADR-020 Dispose 模式全覆盖 | accepted | 2026-08-19 |
| [[decisions/ADR-021-LineLaserWorkflowRefactor]] | 024 | ADR-021 线激光工作流分步重构（9 态；步驱动机制已由 ADR-029 清除） | accepted（沿革） | 2026-08-20 |
| [[decisions/ADR-022-CodeSimplificationStandard]] | 025 | ADR-022 代码精简规范沉淀 | accepted | 2026-08-21 |
| [[decisions/ADR-023-WorkflowResponsibilityBoundary]] | 027 | ADR-023 流程与子设备对象权责边界（R1~R5） | accepted | 2026-08-31 |
| [[decisions/ADR-024-SafetyCheckConsolidation]] | 028 | ADR-024 安全检查三文件合并为 DeviceStatusWork 三线程 | accepted | 2026-08-31 |
| [[decisions/ADR-025-ButtonShadowDeviceSwitch]] | 029 | ADR-025 MainPage 硬件快捷开关 FloatButton→ButtonShadow | accepted | 2026-08-31 |
| [[decisions/ADR-026-ProductLifecycleRecordModule]] | 030 | ADR-026 产品生命周期记录模块与故障记录归口 | accepted | 2026-08-31 |
| [[decisions/ADR-027-ThreeStateModelRefactor]] | 031 | ADR-027 三态模型重构（SubDeviceState / SubDeviceWeldStatus / MainDeviceStatus） | accepted | 2026-09-02 |
| [[decisions/ADR-028-ArchitectureRawSource]] | 032 | ADR-028 架构原档单一来源约定（raw/architecture） | accepted | 2026-09-02 |
| [[decisions/ADR-029-RawDesignRefinement20260903]] | 033 | ADR-029 原档 9-03 细化：主控设计完全重构与冲突裁定（C1~C7） | accepted | 2026-09-03 |
| [[decisions/ADR-030-MainDeviceStateSemantics]] | 034 | ADR-030 主设备状态机语义修正与初始化时序重构 | accepted | 2026-09-04 |
| [[decisions/ADR-031-ErrorReportingHierarchy]] | 035 | ADR-031 报错分层与状态切换零日志 | accepted | 2026-09-04 |
| [[decisions/ADR-032-MotionControllerDeltaReplacement]] | 036 | ADR-032 运动控制器采用台达 EtherCAT（全新模块） | accepted | 2026-09-06 |
| [[decisions/ADR-033-ZMotionRemovalAndDeltaLanding]] | 037 | ADR-033 移除正运动并全面落地台达 EtherCAT + 消费方对接 | accepted | 2026-09-07 |
| [[decisions/ADR-034-LineLaserThreeLayerRefactor]] | 038 | ADR-034 线激光三层重构与 SmartRay/海康 3D 移除 | accepted | 2026-09-08 |
| [[decisions/ADR-035-LineLaserResponsibilitySplit]] | 039 | ADR-035 线激光职责再分工（实现层只回调 · Manager 做业务 · PVT 以 IPVTMotion 注入） | accepted | 2026-09-08 |
| [[decisions/ADR-036-LineLaserManagerSingleEntry]] | 040 | ADR-036 线激光相机访问统一收口（Manager 持有实例 + 外设代理） | accepted | 2026-09-08 |
| [[decisions/ADR-037-MecaVisionMonitorCamera]] | 041 | ADR-037 监控相机三层重构并切换麦格威 MVSDK | accepted | 2026-09-08 |
| [[decisions/ADR-038-EmguALGThreeLayer]] | 042 | ADR-038 EmguALG 三层改造（Abstractions + 领域算法 + AlgorithmManager） | accepted | 2026-09-08 |
| [[decisions/ADR-039-MonitorCamBoundaryAndEmguALGRefinement]] | 043 | ADR-039 监控相机边界澄清与 EmguALG 五层细化 | accepted | 2026-09-09 |
| ~~[[decisions/ADR-040-SeamGuideTrajectoryBuilder]]~~ → [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] | 044 | ADR-040 线激光引导 Y 轴轨迹构造（PVT 写入权移交 WeldParamControl） | **deprecated**（2026-09-14 由 ADR-041 取代） | 2026-09-11 |
| [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] | — | ADR-041 焊接参数控制算法分层（抽象基类 + 实现类 + Manager 唯一入口） | accepted | 2026-09-14 |
| [[decisions/ADR-042-ModuleOrganizationPatternStandard]] | — | ADR-042 模块组织范式沉淀（Core + 抽象层 + 实现层 + Manager 四件套；第三方库场景 Core 必需，纯自研场景 Core 按需） | accepted | 2026-09-14 |
| [[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]] | — | ADR-043 算法纯净性与记录职责隔离（算法只计算 · 记录归 ProductFileControl · 异步不阻塞） | accepted | 2026-09-14 |
| [[decisions/ADR-044-WeldAlgorithmsConfigMerge]] | — | ADR-044 焊接算法配置合一（SeamGuideConfig + WeldParamAdjustmentConfig → WeldAlgorithmsConfig） | accepted | 2026-09-14 |
| [[decisions/ADR-045-CommModuleRefactor]] | — | ADR-045 Comm 模块重构（CommChannelBase 抽象 + 5 实现 + Manager 唯一口；KUKA 门面并入；Profinet/GSDML 删除；EthernetXmlComm 重写） | accepted | 2026-09-14 |
| [[decisions/ADR-046-ProductRecordModuleRefactor]] | — | ADR-046 产品记录模块重构（ProductRecordBase + 三记录类 + ProductFileRecordManager，ADR-043 订阅方闭环；记录类自包含化见 ADR-047 沿革） | accepted | 2026-09-14 |
| [[decisions/ADR-047-RecordImplementationSelfContained]] | — | ADR-047 记录实现类文件自包含（RecordFileStore/RecordFrame/WeldActionRecord 吸收 + SmartRayConverter 链删除 + SeamAdjustRecord→WeldParamAdjustRecord 改名） | accepted | 2026-09-14 |
| [[decisions/ADR-048-NamespaceDirectoryAlignment]] | — | ADR-048 命名空间与目录严格对齐（namespace = AdaWeldSystem + 目录路径；厂商 SDK 与 ProductFileControl 扁平目录为登记例外） | accepted | 2026-09-14 |

> 另有 [[decisions/OPEN-ClearAlarmSemantics]]（**已裁定关闭**：消报语义由 ADR-030 裁定「消除报警一律回 NoReset」），
> 不占 ADR 编号。

## 关联

- [[index/index]] — 知识库总索引（§7 设计决策，按状态分类）
- [[decisions/ADR-033-ZMotionRemovalAndDeltaLanding]] — 09-07 重排的触发决策
- [[guides/DeltaEtherCAT-Deployment]] — 台达部署规范（驱动 · 原生库 · 项目内落地）
