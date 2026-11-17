---
title: WeldParamControl 模块 — 焊接参数控制与工艺计算
date: 2026-08-28
updated: 2026-11-02
tags: [模块, 焊接, 工艺, 自适应, 功率, 送丝, 振镜, 焊缝, 算法分层, Manager, 记录隔离, 配置合一, 焊缝跟踪, CSP, 双模式, 步骤输出, ADR-015, ADR-033, ADR-043, ADR-042, ADR-042, ADR-033, ADR-042, ADR-042, ADR-042, ADR-042, ADR-067, ADR-068]
source: AdaWeldSystem/WeldParamControl/ + MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs
---

# WeldParamControl 模块 — 焊接参数控制与工艺计算

> 目录 `AdaWeldSystem/WeldParamControl/`，命名空间 `AdaWeldSystem.WeldParamControl`。
> **定位**：**管理所有焊接参数与焊接算法** —— 提供计算公式、接口与配置。
> ⛔ **本模块不单独开流程**；编排只在 [[api/WeldParamControlWorkflow]]。

> **2026-09-14 架构纠偏（ADR-015）**：~~`WeldProcess`~~ 单例已删除，模块改为
> 「**抽象基类 + 若干非单例实现类 + Manager 唯一入口**」；外部一律经 [[api/WeldParamManager]] 访问。
> 数据结构迁入 `WeldParamData.cs`；~~`WeldDataManager`~~ 已并入 `WeldParamManager`；
> ~~`SeamTrajectoryBuilder`~~ 已演进为 `SeamTrackingAlgorithm`。
> **线激光引导配置（`SeamGuideConfig`）由 Manager 独占持有与持久化**（自有 `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`），
> 原 `WeldParamControlWorkflow.SeamGuide` / `SaveSeamGuide()` 已删除；`SeamGuideSample` 归入 `Algorithms/`。
> 详见 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]。

> **2026-09-14 算法纯净性与记录隔离（ADR-033）**：算法**只计算、不落盘**——`WeldParamAdjustmentAlgorithm` 内
> 原 `RunRecordManager.RecordProcessFrame` / `RecordAdjustment` / `AbortRecording` 三处直接落盘**已删除**，
> 改为触发记录请求事件（`FrameRecordRequested` / `AdjustmentRecordRequested` / `AbortRecordRequested`），
> 经 Manager 透传，由记录模块订阅后**异步**落盘；本模块**不再依赖** [[modules/ProductFileManager]]。
> 同时新增 `WeldParamAdjustmentConfig`（节 `WELD_PARAM_ADJUST`），运行参数由 Manager 独占持有；
> `ExecuteAdjustment` 去掉 `isCountType` / `countNum` 形参。详见 ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。

> **2026-09-14 配置合一（ADR-043）**：~~`SeamGuideConfig`~~ 与 ~~`WeldParamAdjustmentConfig`~~ **两个配置类已合并**为单一
> `WeldAlgorithmsConfig`（**同文件、同节名不变**：仍为 `SEAM_GUIDE` + `WELD_PARAM_ADJUST` 两节，落在 `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`，
> 存量配置文件**无需迁移**）。Manager 改为**一个配置实例**（只读属性 `AlgorithmsConfig`）+ **一对**无参
> `LoadAlgorithmsConfig()` / `SaveAlgorithmsConfig()`；~~`LoadAdjustmentConfig`~~ / ~~`SaveAdjustmentConfig`~~ /
> ~~`LoadSeamGuideConfig`~~ / ~~`SaveSeamGuideConfig`~~ 已删除。详见 ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。

> **2026-09-16 焊缝跟踪双模式（ADR-042 / ADR-042）**：运行参数与线激光引导参数**同属 `SEAM_GUIDE` 节**（ADR-043 已合一的 `WeldAlgorithmsConfig`），
> 本轮在该节内**新增焊缝跟踪参数**（`TRACKING_MODE` 等）。跟踪算法新增第四个实现类
> **`SeamMapTrackingAlgorithm`（CSP 实时目标）**，与既有 `SeamTrackingAlgorithm`（PVT 流式段）**双模式并存**、由
> `TRACKING_MODE` 开关二选一（默认 `CspRealtime`）：CSP 模式下线激光结果只更新「焊缝绝对 Y 空间地图」（⛔ 2026-09-17 经 ADR-043 演进为示教锚定 Y 空间地图、**2026-09-21 ADR-042 再换轨为特征点锁定闭环**；**2026-09-22 经 ADR-042 → ADR-042 → ADR-042 三次换轨，地图语义定为「前置量对齐的绝对 Y 轴目标地图」，基准最终为测量时刻轴值 Ya1**），
> **不产出 `PVTPoint[]`**，Y 轴目标由 [[api/MotionControlWorkflow]] 的 **CSP 步骤按拍**写
> [[api/DeltaEtherCAT-Native]] 的 CSP 目标位置（对象字典 607Ah）；⚠️ **2026-09-22 ADR-042 起 PVT 参数退场**——界面 11 个控件真删、`BatchSize` / `MinRemainBuffer` / `DefaultFrameSeconds` / `MaxOutputIntervalMs` / `MaxPendingPoints` **停止 INI 持久化与界面调配**（仅保留构造函数默认值供 PVT 回退路径使用），PVT **链路本身仍原样保留**。
> 机器人位姿上行归通讯层（[[modules/Comm]] `TryGetRobotPose`），本模块只经 Manager 读取，不另存副本。
> **写入节拍由流程决定、不设独立线程**（ADR-042）；原 `SEAM_GUIDE/CYCLE_TIME_MS` 配置项**已删除**，dt 全取实测。
> 详见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]、ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。
- [[decisions/ADR-033-ConfigArchitectureStandard]] — 配置架构标准（类别/类型/格式三段式 + XML/INI 分轨；首个落地 WeldAlgorithmsConfig 拆分；含 ADR-009 设备数据边界例外）

> **2026-09-16 配置架构标准（ADR-033）**：焊接算法配置按「类别/类型/格式」范式拆双后端——
> **XML** `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`（设备几何/标定，`SEAM_GUIDE` 几何段 + `LASER_CALIBRATION`）+ 
> **INI** `Config/WeldParamControl/Algorithm_INI/WeldParamControlAlgorithm.ini`（流程阈值，`SEAM_GUIDE` 阈值段 + `WELD_PARAM_ADJUST`）；
> 设备默认参数归 XML、流程阈值/开关/节拍归 INI（ADR-033 全项目标准）。线激光标定经本 ADR 例外并入（ADR-009 边界例外登记）。详见 [[decisions/ADR-033-ConfigArchitectureStandard]]。

> **2026-11-09 两域边界登记（ADR-097 D8）**：焊接参数四算法（查表/调节/焊缝/焊缝地图）与 `Config/WeldParamControl/Algorithm_INI/WeldParamControlAlgorithm.ini` 属本模块自有域，由 `WeldParamManager` 自持自读；与监控侧 [[api/AlgorithmManager]] / `Config/EmguALG/Algorithm_INI/MonitorAlgorithm.ini` 互不引用、无键重叠、无共用可变 DTO。命名相邻（`WeldQualityAlgorithm` vs `SeamTracking*`）但无数据通路，属**有意分域，不合并**；UI 亦不同页、不同调用链。

> **2026-09-17 示教锚定标定模型与线激光配置归并（ADR-043）**：焊接算法配置**删 3 项冗余**（`LaserFrontOffset` / `LaserToHorizontalScaleX` / `LaserZeroMm`），
> **新增 `TeachLockYMm`（示教 Y 轴锁定坐标，XML `SEAM_GUIDE/TEACH_LOCK_Y_MM`，默认 0.0）**，参数项 **39 → 37**
> （`SEAM_GUIDE` 几何/安装 13 项 + 流程阈值/开关/节拍 17 项 + `WELD_PARAM_ADJUST` 3 项 + `LASER_CALIBRATION` 4 项）；
> **标定语义裁定**：`CalibratedCenterY` = 示教时线激光识别到的焊缝特征点 Y（YL1），`TeachLockYMm` = 示教时轴锁定位置（Y1）；
> 目标改为**示教锚定**——`目标 = TeachLockYMm + (实时特征Y − CalibratedCenterY) × AxisMmPerLaserMm × GuideSign`，**起焊种子 = `TeachLockYMm`**；
> 机器人实时 Y 与安装偏移 `InstallOffsetY` **不再参与**目标反算（`RobotYFilterAlpha` 仅保留供 `RobotY` 观测，`InstallOffsetY` 成为纯配置项）；**2026-09-24 业主令**：`InstallOffsetY` **整体删除**（配置项 + XML 读写 + UI 控件四件套；该参数自本裁定时已 0 消费，且 Load 读 `SEAM_GUIDE` / Save 写 `LASER_CALIBRATION` 读写错位双重失效）。同日运控侧 **CspChain 写入数据链记录器移除**，换 **SeamY 记录器**（5 列 `当前RobotX,入图RobotCSPX,CSPinYt,CSPoutY,实时Y`，业主直读误差用）。

> **2026-09-22 突变剔除三重护栏 + 方向平滑补强（[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]）**：配置新增 3 项（INI `SEAM_GUIDE`：`MONOTONIC_RELEASE_MM`=0.30 / `CONSECUTIVE_REJECT_FRAMES`=20 / `CSP_MIN_SEG_MM`=0.005），`MonotonicWindowMm` 语义改为**持距兜底上限**（默认 200mm）、`MonotonicDeadbandMm` 默认 0.05；
> ~~`BatchSize` / `MinRemainBuffer` / `DefaultFrameSeconds` / `MaxOutputIntervalMs` / `MaxPendingPoints`~~ **停止 INI 读写与界面调配**（PVT 回退路径仍消费其构造函数默认值）；
> ⚠️ `NoValueToleranceMm` / `OutlierLimitMm` 同步**退出界面**（仅剩 PVT 回退路径 [[api/SeamTrackingAlgorithm]] 消费）；
> `SeamMapTrackingAlgorithm` 侧补齐**三重护栏**（首帧种子闸门 `MaxSeedDeviationMm=10` / 连续拒绝重新种子 / 拒绝分源 `TimeRejectCount`·`SpaceRejectCount`）并把 `ApplyMonotonic` 重写为**方向锁 + 迟滞释放**。
>
> **2026-09-22 绝对目标基准换轨 + 最终目标突变护栏（[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] + [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]）**：配置新增 1 项（INI `SEAM_GUIDE`：`MAX_TARGET_STEP_MM` = 5.0，界面「最终目标最大突变(mm)」，四点闭环），`CspMinSegMm` 钳位下限由 0 提到 **0.001**（单脉冲当量）；`SeamMapTrackingAlgorithm` 地图值基准由**标定轴值**换轨为**测量时刻轴实际值 Ya1**（`Yt = Ya1 + 滤波dY`；结构不变式「Yt 表达式内不得出现可被自身执行改变的轴状态量」）+ 新增**最终目标突变护栏**与 `TargetStepRejectCount`（`ProcessLaserResult` 8 → **9 步**）；运控侧拆除「减基准再加回」折算并**删除 `ClampCorrection` / `MaxCorrectionMm`**，新增 `AxisEquivMm` / `ToPulseMm` 与**脉冲域段距护栏** `max(CspMinSegMm, AxisEquivMm)`。
> ~~⚠️ 运控侧硬编码常量 `CspMinSegMm = 0.001` **已删除**，改由本模块 `WeldAlgorithmsConfig.CspMinSegMm` 驱动 —— 即「CSP 最小有效段距」的**唯一配置源在本模块**。~~ ⚠️ **2026-09-22 末次演进（ADR-042/054）**：写段门限已**硬编为单脉冲当量 `AxisEquivMm`（= 0.001mm）**（`MotionControlWorkflow.QueueCspSegment` 取 `minSegMm = AxisEquivMm`），`WeldAlgorithmsConfig.CspMinSegMm` 降级为 **INI/界面留痕项**（默认 0.001，取值不再影响写段节拍）；判据量统一为命令侧单脉冲当量，与残差一阶跟随器（`StepCspTarget`，τ=150ms）协同消除「轴停走、写段占空比掉到 7%」现场问题。详见 [[api/MotionControlWorkflow]] ③ 与 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]。
> UI 段位归并与 `MoveControlData` 死代码清理见 [[modules/UIDesign]] / [[api/MoveControlData]]。详见 ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。

> **2026-09-23 焊缝宽度来源选择与工艺参数 XL 输出链路（[[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]）**：配置新增 4 项（INI `WELD_PARAM_ADJUST`：`SEAM_WIDTH_SOURCE`=Manual/Laser 默认 Manual、`MANUAL_SEAM_WIDTH_MM`=1.2、`SPOT_WIDTH_GAIN`=1.0、`PARAM_OUTPUT_HZ`=60），配置 **45 → 49 项**；~~算法新增第五个实现类 `WeldParamXLCacheAlgorithm`~~（⚠️ **同日经 ADR-043 决 6 并入 `WeldParamAdjustmentAlgorithm` 并删除**——XL 缓存改由调整算法私有承载，键 = 测量 X + `LeadDistanceMm`，与 ADR-042 前置量入键同语义，X 单调化 + 二分取「已到达的最邻近 XL」，仅 Laser 源入缓存）；查表算法新增 `SpotWidthDic`（光斑宽度 = 焊缝宽度 × W）与 `TryLookupWithSpot()`（原 `TryLookup` 签名不变）；`WeldParamAdjustmentAlgorithm` 在 Manual 源下**绕过滑动平均与突变判定**直查表（输出恒定、跳过调整留痕）；数据库 `AutoParamValue.db` 分段参数表新增第 5 列 **「光斑宽度」**（旧表 `ALTER TABLE` 自动迁移）；[[api/WeldParamControlWorkflow]] StepIdle 新增 **60Hz XL 输出支路**（Manual=每拍直查表 / Laser=取已到达 XL 缓存；无机器人通讯仅记录；模拟零新增代码触发）。详见 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]。

> **2026-09-23 地图值时间域低通彻底移除（[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]）**：算法侧 `ProcessLaserResult` 只保留「合成绝对目标 `Yt = Ya1 + d_raw`」，**低通整项删除**（滤 d ⇒ `τ·(ẏ_轴−v_缝)` 环内自激、滤合成 ⇒ `−τ·v_缝` 斜段恒滞后，两者都是 ±τ 级误差且不必要；业主口径「计算用原值，滤波不做」）；连带删除 `DyFilterAlpha` 属性（XML 键 `DY_FILTER_ALPHA` 不再读/写）与界面「dY低通系数」控件（配置 **49 → 48 项**，SEAM_GUIDE 几何 **15 → 14**）；`tbPanelAlogControl` 删该行后**行号整体上移 1**（RowCount **32 → 31**，面板参数 **19 → 18 项**）；抑噪职责转由查图侧零相位空间高斯（σ=12mm）与 ③/⑤/⑦ 三道突变闸门承担。

> **2026-09-23 工艺参数调整链路载入优先级换轨（[[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]）**：生产只读分段表——基准公式仅用于首建兜底与修正基准；`AutoParamHelper` 一配置一表一行、空表首存自愈；宽度来源切换只刷光斑宽度列。

> **2026-09-22/23 输出整形换轨 + Y 轴速度前馈 + 面板选项化落地（[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] / [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] / [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]）**：本轮为 ADR-042/058/059 的代码落地，配置面新增/改义项已随 ADR-042/056/058/059 收口（合计 **49 项**：SEAM_GUIDE 几何 15 + INI 阈值 23 + LASER_CALIBRATION 7 + ADR-042 标定 3 + ADR-043 宽度来源 4 + ADR-042 前馈 1，ADR-043 面板项复用既有键）；核心变更：
> - **写段门限硬编单脉冲当量**（见上条 `CspMinSegMm` 演进）；段速度时基取「自上次写段实测间隔」（`CspMinTickSeconds`/`CspMaxSegSeconds` 钳位），段距下限由 `max(CspMinSegMm, Equiv)` 收敛为纯 `Equiv`，保底 1 脉冲/秒防 `ToPulse` 截断成 0。
> - **输出死区收敛**：`OutputDeadbandMm` 默认 **0.05 → 0.01**，加载期**上界 0.02**（旧 INI 0.05 会被加载期强制压回）；残差必须取「跟随器位置 → 目标」、轨迹逐拍不去重——死区自身不再是台阶发生器（0.05mm 在 0.09mm/s 慢速下使轴停走）。
> - **Y 轴速度前馈（ADR-042）**：新增 `FeedforwardSafetyFactor`（默认 3.0，INI `FEEDFORWARD_SAFETY_FACTOR`），运控速度上限抬到 `max(MaxVel, 系数 × |机器人X速度 × 地图局部斜率|)`、加速度上限抬到 `max(MaxAcc, 前馈下限/τ)`；**只抬上限、不产生位移**，估计失真仅回退既有行为。`EstimateRobotVelocityX` 取尾部 ≥2mm 基线割线 + EMA（`FeedforwardVxAlpha=0.2`，`FeedforwardVxSaneLimitMmPerS=500`  sanity 上限）。
> - **PVT 流式模式强制禁用（ADR-043）**：加载期 `TrackingMode` 一律强制 `CspRealtime`（面板已移除模式下拉）；`ApproachThreshold` 全链删除（部分撤销 ADR-042 决 1）；输出频率 60/30/10Hz 下拉（`selParamOutputHz`）；面板新增 `FeedforwardSafetyFactor` / `EnableMonotonicConstraint`。
> - **可观测性（ADR-042/052）**：新增 `_cspTickCount`/`_cspWriteCount`（写段占空比 = 写段数/输出拍数）、`DetectCspExecutionStall`（轴反馈位移观测，区分「驱动停止/报警/反馈断链」）、`ReportStrokeClamp`（行程限幅告警）、`BufferStartMaxFailures=3` 缓冲启动失败次数上限；热点路径失败收敛为「限率日志 + 限幅告警」而非静默。
> - **光斑宽度链路（ADR-043）**：`WeldParamManager.SpotWidthOutput` / `SpotWidthDic`（焊缝宽度 × W）已随 ADR-043 收口；`WeldParamAdjustmentAlgorithm` 在 Manual 源下绕过滑动平均与突变判定直查表。

> **2026-10-14 WeldAlgorithmsConfig 按 UI 4 分区重组（[[decisions/ADR-068-WeldAlgorithmsConfigZoneReorg|ADR-068]]）**：配置代码块按 **UI 4 分区**重排（`AlgorithmsZone` 四区：①System 系统设置 / ②Quick 工艺快捷 / ③Adapt 自适应 / ④Preset 工艺设定值），**UI 面板与配置代码块一一对应**（只动代码块顺序与注释，属性名/INI/XML 键/默认值零改动，净行为不变）；
> 新增**分区粒度读写接口** `LoadZoneXml`/`SaveZoneXml`/`LoadZoneIni`/`SaveZoneIni`（总入口 `LoadConfig`/`SaveConfig`/`LoadProcessIni`/`SaveProcessIni` 内部按区调用，签名不变）；[[api/WeldParamManager]] 新增 `SaveAlgorithmsZone(AlgorithmsZone)` 分区落盘透传；
> **`SeamWidthSource` 改只读派生属性**——~~值由新开关 `EnableSpotWidthFollow`（UI 唯一入口=系统设置页）决定~~ ⚠️ **2026-10-15 ADR-070 演进**：`EnableSpotWidthFollow` 已删，派生源改 `EnableGalvoWeave`（振镜摆动即宽度来源开关，光斑宽度跟随与振镜摆动实为一个意思）；（`Laser`/`Manual` 二值），⛔ INI 键 `SEAM_WIDTH_SOURCE` 读写逻辑删除（2026-09-23 宽度来源 4 项中该项退场，ManualSeamWidthMm/SpotWidthGain/ParamOutputHz 归③自适应区）；
> **唯一入口收敛**：`EnableGuide` 归②快捷设置页（系统设置页控件删除）、`EnableMonotonicConstraint` 归①系统设置页（快捷设置页开关删除）。必要说明：`BtnSaveAlgoThresh` 双区落盘为兼容编辑范围的必要处理；4 处即改即存路径暂保留全量保存待迭代。静态校验 **33/33 PASS**。

> **2026-10-14 LA/TA 工艺语义重构（[[decisions/ADR-067-LATaSettingsSemanticRework|ADR-067]]，同日姊妹轮）**：激光工艺设置三区改名——**跟踪工艺设置(Tracking Settings) / 对焦工艺设置(LA Settings) / 送丝下压工艺设置(TA Settings)**；
> **LA 区形态重构**：动作按钮组（7 控件）→ **参数设置区**（10 控件：Spot1/Spot2/Pose1/Pose2/目标光斑 五组输入 + 保存/读取，照 ADR-066 TA 参数区范式，`SaveAlgorithmsZone(AlgorithmsZone.Preset)` 落盘）；LA 三指令语义重写——**LA_Pose 纯到位**（与其他逻辑无关联）/ **LA_Spot 设定光斑**（[[decisions/ADR-053-TaLaCurveAndMotorScale|ADR-053]] 曲线 A 反查 LA 基准位→定位→单次补偿后**退出随动**）/ **LA_Auto 模式开关**（先定位失败即止，成功后持续随动：TA 实时位→曲线 B 补偿保光斑恒定）；**联动关系唯一数据源 = 系统设置下 TaLaCurveConfig 标定曲线**（内部联动）；
> **TA 回缩指令**：现名 `TA_Retract`（2026-11-05 由 `TA_Recheck` 更名并改为 CST 力矩反向出力，CSP 绝对定位回零方案已废止；**2026-11-06 定稿 = `TA_Auto` 反向的纯力矩保持，无位置终点、不撤力、不回 CSP**），快捷 Radio 第 5 项 `radioQuickTaRetract`（未就绪置灰）。**2026-11-02 语义对齐**：`TaBreak` / `TaPose1` / `TaPose2` 同样入口即退出力矩模式，`TaAuto` 以 `MontionManager.TaTorqueModeEnabled` 为门（非力矩模式拒绝执行）。详见 [[api/ProcessControlPage]] / [[api/LaserWeldHeadWorkflow]]。静态校验 **57/57 PASS**。

> **2026-10-21 曲线锚点读取收口（配置读取唯一入口）**：曲线A 的**锚点光斑**（LA=0 处最聚焦光斑）原为 `TaLaCurveConfig` 的**编译期常量** `AnchorSpotMm = 0.6`，被模块外（`LaserWeldHeadWorkflow`）直写引用——⛔ 违反「配置读取经 `WeldParamManager` 唯一入口」（ADR-053 曲线实例归 Manager 独占 / ADR-066 Manager 纪律），且该直写在文件内**无 `using ...Curves;`** 时连编译都过不了。
> 现状：`TaLaCurveConfig.AnchorSpotMm` 改为**实例属性**（从曲线A 采样点表取 X=0 锚点，随标定数据变化；无 X=0 点时回退内置常量 `DefaultAnchorSpotMm = 0.6`）；[[api/WeldParamManager]] 增 facade `AnchorSpotMm` 作为外部唯一读取口。静态校验 **21/21 PASS**（含「int 方法直返 double 常量」CS0266 防线）。


---

## 一、架构总览

```
WeldParamControl/
├── WeldParamData.cs                     数据类集合（含记录请求事件参数）
├── WeldParamManager.cs                  单例 · 唯一外部访问入口（配置 + 全部算法实现 + 记录事件透传 + 机器人位姿消费）
├── WeldAlgorithmsConfig.cs              焊接算法配置（XML+INI 双后端：SEAM_GUIDE 几何段 + LASER_CALIBRATION 归 XML、SEAM_GUIDE 阈值段 + WELD_PARAM_ADJUST 归 INI，Manager 独占；ADR-043/056/059）
├── Abstractions/
│   └── WeldAlgorithmBase.cs             抽象基类：Name / IsReady / LoadConfig(object) / Reset
└── Algorithms/
    ├── SeamGuideSample.cs               算法私有输入结构（结果 + 机器人坐标 + 时间戳）
    ├── WeldParamLookupAlgorithm.cs      实现 a：焊接参数查表调整
    ├── WeldParamAdjustmentAlgorithm.cs  实现 b：焊缝宽度驱动的参数调整（只计算 + 发记录请求事件；ADR-043 决 6 起兼承载工艺参数 XL 缓存——键 = 测量 X + LeadDistanceMm，机器人到达后输出，仅 Laser 源入缓存）
    ├── SeamTrackingAlgorithm.cs         实现 c：线激光焊缝几何轨迹跟踪（PVT 流式段专属，输出 PVT 点）
    └── SeamMapTrackingAlgorithm.cs      实现 d：焊缝绝对 Y 轴目标地图 + 特征点锁定闭环（输出绝对目标 Yt = 测量时刻轴值 Ya1 + dY（2026-09-23：地图值时间域低通已整项移除，用原值计算），CorrectionMm 收窄为诊断；不产 PVT 点；含突变剔除三重护栏、方向锁迟滞释放与最终目标突变护栏；ADR-042 / ADR-042 / ADR-042 / ADR-042 / ADR-042）
```

> 配置分双后端（ADR-033）：`WeldAlgorithmsConfig` 由 Manager 独占双读写器——XML `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`（设备几何/标定，`SEAM_GUIDE` 几何段 + `LASER_CALIBRATION`）+ INI `Config/WeldParamControl/Algorithm_INI/WeldParamControlAlgorithm.ini`（流程阈值，`SEAM_GUIDE` 阈值段 + `WELD_PARAM_ADJUST`）（ADR-033 / ADR-043 / ADR-033）。

| 层 | 类型 | 是否单例 | 职责 |
|---|---|---|---|
| 入口 | `WeldParamManager` | ✅ 单例 | 持有配置与算法实现，透传输出/查找表/事件，无参触发调整，统一管理配置持久化，消费机器人位姿快照 |
| 抽象 | `WeldAlgorithmBase` | 抽象类 | 定义算法对外公共属性与函数接口 |
| 实现 | `WeldParamLookupAlgorithm` | ❌ 非单例 | 查找表生成、焊缝宽度匹配、送丝/功率计算公式 |
| 实现 | `WeldParamAdjustmentAlgorithm` | ❌ 非单例 | 滑动平滑、突变判定、调查表、输出/图表/失败计数/事件 |
| 实现 | `SeamTrackingAlgorithm` | ❌ 非单例 | 线激光结果 + 机器人坐标 → Y 轴 PVT 轨迹点（**PVT 模式专属**；只计算，不写入控制器） |
| 实现 | `SeamMapTrackingAlgorithm` | ❌ 非单例 | **绝对 Y 轴目标地图**（键 = RobotXL = 测量X + `LeadDistanceMm`；值 = **测量时刻轴值 Ya1 + dY**）+ 高斯平滑 + 方向锁 + `TryGetTargetY(robotX, robotY)` 绝对目标（**CSP 模式专属**；只计算，不写控制器；ADR-042 / ADR-042 / ADR-042 / ADR-042） |
| 实现 | `WeldParamAdjustmentAlgorithm` | ❌ 非单例 | **焊缝宽度驱动的参数调整**（滑动平均 + 突变判定 + 查表输出；Manual 源直查表快路径）+ **工艺参数 XL 缓存**（ADR-043 决 6 并入：键 = RobotXL，值 = 该处工艺参数组；X 单调化 + 二分查询；供 60Hz XL 输出支路消费；只计算，不落盘） |

> ⛔ 不得再向 Manager 或算法实现类里加入流程编排；⛔ 不得恢复 `WeldProcess` / `WeldDataManager` / `SeamTrajectoryBuilder`。

---

## 二、算法抽象层（ADR-015）

### 抽象基类 `WeldAlgorithmBase`（`Abstractions/`）

```csharp
public abstract class WeldAlgorithmBase
{
    string Name { get; }                       // 算法名称（日志/可观测性标识）
    bool   IsReady { get; }                    // 配置是否已载入
    void   LoadConfig(object config);          // 载入算法专属配置
    void   Reset();                            // 复位运行期状态（保留配置）
}
```

实现类按自身类型转换 `config`：参数类算法用 `AutoParam`，轨迹跟踪用 `WeldAlgorithmsConfig`。

### 实现 a：`WeldParamLookupAlgorithm` —— 焊接参数查表调整

维护四份查找结构：`SeamWidthList`（键）+ `LaserPowerDic` / `FeedSpeedDic` / `RobotSpeedDic`。

- `BuildLookupTable(AutoParam)`：按焊缝宽度范围与灵敏度生成映射。
- `TryLookup(seamWidth, out laserPower, out feedSpeed, out robotSpeed)`：按焊缝宽度匹配最近一档。
- 公式（静态）：
  - `FeedSpeedCal` = `60 × KVar × SeamWidth × PlateThickness × RobotSpeed / (π/4 × WireDiameter²)`
  - `LaserPowerCal` = `JVar × (π/4 × WireDiameter² × FeedSpeed/60) / MVar`

### 实现 b：`WeldParamAdjustmentAlgorithm` —— 焊缝宽度驱动的参数调整

- `ExecuteAdjustment(autoParam, robotX, contourPoints)`：每帧调用。连续失败超阈值 → 触发 `AbortRecordRequested` 与失败完成事件；否则按 `Config.IsCountType` 分段做滑动平均（`SeamCalData`），突变超过 `Sensitivity` 且未处于 `Trigger` 时调 `WeldParamLookupAlgorithm.TryLookup` 更新三路输出。
- 持有 `ChartVar` ×5（轮廓/功率/送丝/缝宽/速度）、`ConsecutiveFailureCount` / `MaxConsecutiveFailures` / `TotalExecuteCount`、`WeldProcessCompleted` 事件。
- 运行参数取自 `Config`（`WeldAlgorithmsConfig`，Manager 独占）：`MaxConsecutiveFailures` / `IsCountType` / `CountNum`。
- **不落盘**：每帧触发 `FrameRecordRequested`，命中调整时触发 `AdjustmentRecordRequested`，超阈值时触发 `AbortRecordRequested`；落盘由记录模块异步执行（ADR-033）。
- `isCountType == false`（按距离分段）仍为 TODO 未实现。

### 实现 c：`SeamTrackingAlgorithm` —— 线激光焊缝几何轨迹跟踪（PVT 模式专属）

> **模式归属（ADR-042）**：本实现只在 `TRACKING_MODE = PvtStream` 时被调用；`CspRealtime` 模式走实现 d，本类**不参与**。

输入线激光结果 + 机器人坐标 + 引导轴当前位置，经三级修正后输出 `PVTPoint[]`：

- `Feed(result, measuredFps, axisCurrentPos)`：喂入一帧结果，达到 `BatchSize` 时返回点数组。
- `Tick()`：按 `MaxOutputIntervalMs` 强制返回一段点。
- `Drain()`：排空剩余点。
- `Reset()`：清空状态。
- 可观测性：`HasFault` / `FaultReason` / `LastDeviation` / `LastTargetPos`。

> **边界**：本算法只负责计算轨迹点，**不持有 `IPVTMotion`**，也不调用 `BeginMove` / `ContinueMove`；点集由 [[api/MotionControlWorkflow]] 批量写入控制器。

### 实现 d：`SeamMapTrackingAlgorithm` —— 绝对 Y 轴目标地图 + CSP 实时目标（CSP 模式专属，ADR-042 / ADR-042 / ADR-042 / ADR-042）

> **模式归属**：只在 `TRACKING_MODE = CspRealtime`（默认）时被调用；**输出不是 `PVTPoint[]`，而是按当拍位姿查图得到的绝对 Y 轴目标**（`TryGetTargetY(robotX, robotY, out targetY)`）。

三条异步通道（线激光 60Hz / RSI 位姿 ~83Hz / 流程节拍 100Hz）在此解耦：算法只负责「**结果 + 位姿 → Y 轴目标**」，写控制器由 [[api/MotionControlWorkflow]] 的 CSP 步骤按拍承担。

**前置量对齐的绝对 Y 轴目标地图**（ADR-042 键平移 + ADR-042 测量时刻轴值基准）：

```
偏差 dY = (实时特征Y − CalibratedCenterY) × AxisMmPerLaserMm × GuideSign
地图键   = 测量机器人 X + LeadDistanceMm（= RobotXL，前置量入键）
地图点值 TargetY = 测量时刻轴实际值 Ya1 + dY（2026-09-23 裁定：地图值**不做任何时间域低通**——滤 d 会经 τ·(ẏ_轴−v_缝) 自激、滤合成会 −τ·v_缝 斜段滞后，用原值）
```

- 地图按 `RobotX` 升序存储（`SeamMapPoint`：`RobotX`（键 = 测量X + `LeadDistanceMm`）/ `TargetY`（**绝对 Y 轴目标** = Ya1 + 滤波dY）/ `RobotY`（测量时刻滤波机器人 Y，供**写入时刻**差分反向抵消）/ `PathDistance`（降级为诊断字段）/ `Timestamp`），查图与平滑按**对称 X 窗口** `[X − GaussianHalfWindowMm, X + GaussianHalfWindowMm]`；X **单调化** —— 抖动级回退（≤ `ReverseDeadbandMm`）**吞掉**（`JitterRejectCount++`，不推进键、不入图）。
- **为何弃用累积弧长**：丢一包即永久少算、抖动即虚增、误差无法自愈；X 绝对坐标恒等可复现。
- **模型沿革**：原「焊缝绝对Y = 机器人Y + 轴当前位置 + 滤波dY + InstallOffsetY」已废止（ADR-043）→ 示教锚定 Y 空间地图 → 特征点锁定闭环 / 修正量地图（ADR-042）→ **绝对 Y 轴目标地图（ADR-042/049，现行）**。**基准演进链：轴实际反馈 → 起焊锚点 → 标定轴值 → 测量时刻轴值 Ya1。**

**野值剔除（炸点）**（ADR-042 换轨）：切线连续性违约——尾部两点切线外推，`|new − predicted| > TangentFloorMm(0.2) + OutlierSlopeLimitMmPerMm × gap`——**或** 3σ 统计异常（`std > 0.05` 且 `|new − mean| > OutlierSigmaK×σ`）→ 丢弃并 `OutlierCount++`。连续曲线（弧/直线/S 形）沿切向永不误杀；连续拒 20 帧判真实台阶放行。

**零相位高斯空间平滑**：**对称窗** `[X − GaussianHalfWindowMm, X + GaussianHalfWindowMm]`（键已含前置量平移，查询中心即当前焊枪 X，无需单边平移）、`σ = GaussianSigmaMm`（默认 12mm）；未测位置没有键，天然不会被取到。

**Y 轴目标反算**：

```
TryGetTargetY(robotX, robotY)：平滑绝对目标 − RobotYGain×(当拍机器人Y − 该点测量时刻机器人Y) → 输出死区 0.05mm → 运控侧行程限幅 [YAxisMinMm, YAxisMaxMm]
```

**X 折返处置（两档）**：机器人 X 只应前进、不复焊。首段 `dx` 锁定方向 `_direction`；单包位移小于 `ReverseDeadbandMm`（ADR-042 起默认 **0.1mm**）不计入方向判定（防 RSI 原位噪声误判）；累计折返 ≤ `ReverseAlarmMm`（默认 1.0mm）**仅警告一次**并继续；连续折返超阈值 → 触发 **`TrackingAlarmRequested`**（算法只发事件，不推进流程）。

| 成员 | 说明 |
|---|---|
| `OnLaserResult(result, axisPosMm)` | 喂入一帧线激光结果 + **测量时刻跟踪轴实际位置**（SDK 回调线程；ADR-042） |
| `OnRsiPose(robotX, robotY, robotZ)` | 喂入一帧机器人位姿（RSI 接收线程） |
| `TryGetTargetY(robotX, robotY, out targetY)` | **按当拍机器人位姿取绝对 Y 轴目标**（运控写入时刻调用）；`false` = 前置量段内无地图点（ADR-042） |
| ~~`SeedYAxisTarget(seedMm)`~~ | ⛔ 已删除（示教锚定 / 起焊锚点播种随基准换轨退场） |
| `Reset()` | 复位地图与全部计数（保留配置） |
| `TrackingAlarmRequested` | 折返超限报警事件（**锁外**触发，防订阅方重入死锁） |
| `YAxisTarget` / `HasYAxisTarget` | 当前 Y 轴目标 / 是否已产出首帧 |
| `MapPointCount` / `OutlierCount` / `InvalidFrameCount` / `SmoothSkipCount` / `LastDy` / `LastSeamY` | 可观测性计数与诊断值 |

> **边界（ADR-006 / ADR-033）**：实现层只计算——⛔ 不持 `ICspMotion`、不调 `SetCspTargetPosition`、不落盘、不推进执行步；只在计算路径上更新内存状态与触发事件。
> ⚠️ 首段平滑窗口内 `SeamMapPoint` 不足时按当前唯一有效点输出并计 `SmoothSkipCount`；起焊沿已 `SeedYAxisTarget` 兜底，地图未成形期间 Y 轴保持不动。

---

## 三、Manager 唯一入口（ADR-015）

`WeldParamManager.Instance` 是模块**唯一外部访问点**，构造时 `new` 出三个算法实现并持有，同时初始化配置持久化（INI / ConfigHelper / AutoParamHelper）。

### 配置与运行期

| 分类 | 成员 | 说明 |
|---|---|---|
| 配置 | `CurrentAutoParam` | 当前自动参数配置（null 时无法计算） |
| 配置 | `ConfigHelper` | 自动调整参数配置管理器（基础配置与 JSON 映射） |
| 配置 | `AutoParamHelper` | 自动调整参数值管理器（分段数据表） |
| 配置 | `CurrentAutoParamId` | 当前配置标识（INI 持久化） |
| 配置 | `IsCountType` / `CountNum` / `MaxConsecutiveFailures` | 参数调整运行配置（透传，源 `AlgorithmsConfig`） |
| 配置 | `AlgorithmsConfig` | **Manager 独占的配置实例**（只读引用；`WeldAlgorithmsConfig`，XML+INI 双后端；ADR-015 / ADR-033 / ADR-043 / ADR-033） |
| 配置 | `CurrentRobotX` | 机器人 X 坐标（读写；内部即 `RobotWeldData.PosX`） |
| 配置 | `TrackingMode` / `IsCspTrackingMode` | 焊缝跟踪模式（读 `SEAM_GUIDE/TRACKING_MODE`，空配置回退 `CspRealtime`）/ 便捷布尔判定（ADR-042） |
| 位姿 | `HasRobotPose` / `TryGetRobotPose(out x, out y, out z)` | **机器人位姿唯一消费入口**——转发通讯层快照（[[modules/Comm]]），⛔ 本模块不另存副本（ADR-042） |
| 输出 | `LaserPowerOutput` / `FeedSpeedOutput` / `RobotSpeedOutput` | 最近一次调整结果 |
| 输出 | `CurrentSeamWidth` | 本轮采用的焊缝宽度（平滑后） |
| 计数 | `ConsecutiveFailureCount` / `MaxConsecutiveFailures` / `TotalExecuteCount` | 失败与执行计数 |
| 查找表 | `SeamWidthList` / `LaserPowerDic` / `FeedSpeedDic` / `RobotSpeedDic` | 可读写透传 |
| 图表 | `ContourChart` / `LaserPowerChart` / `FeedSpeedChart` / `SeamWidthChart` / `RobotSpeedChart` | 折线图数据（只读） |
| 事件 | `WeldProcessCompleted` | 透传参数调整算法的完成事件 |
| 事件 | `FrameRecordRequested` / `AdjustmentRecordRequested` / `AbortRecordRequested` | **记录请求透传**（落盘由记录模块异步执行，ADR-033） |

### 配置管理方法

| 方法 | 说明 |
|---|---|
| `SwitchConfig(configId)` | 切换到指定配置 |
| `AddConfig(configId)` | 新增配置并切换 |
| `DeleteConfig(configId)` | 删除非默认/非当前配置 |
| `SaveCurrentAutoParam()` | 保存当前 AutoParam 到 ConfigHelper |
| `SaveCurrentProfile()` | 保存当前分段参数到 SQLite |
| `ReloadCurrentParamValues()` | 重新载入当前配置并按基准重建查找表（修正基准=恢复默认，落盘覆盖分段表，ADR-043） |
| `LoadProfileIntoLookupTable(identityInfo)` | 从 SQLite 读分段数据写入查找表（空集合不覆盖内存；次序=基准兜底后覆盖，ADR-043） |
| `LoadAlgorithmsConfig()` | **无参**从双后端载入——XML `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`（`SEAM_GUIDE` 几何段 + `LASER_CALIBRATION`）+ INI `Config/WeldParamControl/Algorithm_INI/WeldParamControlAlgorithm.ini`（`SEAM_GUIDE` 阈值段 + `WELD_PARAM_ADJUST`），并**分发给算法**（构造时自动调用一次；ADR-043 / ADR-033） |
| `SaveAlgorithmsConfig()` | 把当前焊接算法配置写回双后端（XML 节 `SaveXdocument()` 落盘 + INI `SaveToFile()` 落盘）（ADR-043 / ADR-033） |

> **配置由 Manager 独占**：构造时 `LoadAlgorithmsConfig()` 一次载入两节，独占双读写器——XML `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`（`SEAM_GUIDE` 几何段 + `LASER_CALIBRATION`）+ INI `Config/WeldParamControl/Algorithm_INI/WeldParamControlAlgorithm.ini`（`SEAM_GUIDE` 阈值段 + `WELD_PARAM_ADJUST`），并把**同一个配置实例**分发给 `WeldParamAdjustmentAlgorithm` / `SeamTrackingAlgorithm` / `SeamMapTrackingAlgorithm` **三个实现类**只读消费。⛔ 外部不得 `new WeldAlgorithmsConfig()`、不得持有或回灌实例——原 `WeldParamControlWorkflow.SeamGuide` / `SaveSeamGuide()` / `_seamGuide` 已删除（ADR-015 第三次修订）；参数调整三项运行参数亦从算法硬编码外提（ADR-033）；~~`SeamGuideConfig`~~ / ~~`WeldParamAdjustmentConfig`~~ 两类于 2026-09-14 合并为 `WeldAlgorithmsConfig`（ADR-043）；焊缝跟踪 18 项运行参数于 2026-09-16 并入 **`SEAM_GUIDE` 节**（`TRACKING_MODE` 等），未新建节、存量 XML 无需迁移（ADR-042）。

### 工艺 INI 的 TA 键与一次性迁移（2026-11-06）

| 键（`ProcessControlSection`） | 属性 | 可编辑位置 |
|---|---|---|
| `TA_FORCE_N` | `TaForceN` | 工艺设置页 TA 区「下压力」 |
| `TA_POSE1_MM` / `TA_POSE2_MM` | `TaPose1Mm` / `TaPose2Mm` | 工艺设置页 TA 区 |
| `TA_ZERO_POSE_MM` | `TaZeroPoseMm` | 工艺设置页 TA 区（**TA 工作零位坐标唯一可编辑源**，2026-11-06 新增） |

- **旧值迁移**：`ReloadConfig` 内 `MigrateLegacyTaZeroPoseMm(_algorithmsConfig)` 把 `ROOT/TA_HOME/TA_HOME_ZERO_POSE_MM`
  迁到 `TA_ZERO_POSE_MM`，**幂等**（工艺 INI 已存在该键即跳过，⛔ 不覆盖工艺页现值），只改内存、由随后补键链路落盘；
  旧键保留在 `TA_HOME` 中不删、不再被读取。
- **顺序硬约束（ADR-086 D8）**：迁移必须早于 `HealAlgorithmsConfigKeys` —— 补键会写出默认值 `0`，一旦先补键，
  `KeyExists` 恒为真，现场旧值会被误判为「工艺页已设定」而永久丢失。
- **自愈**：新键随 `WeldAlgorithmsConfig.SaveProcessIni()` 的模板镜像纳入补键（只增不改、无缺键零写盘）。

### 算法方法

| 方法 | 说明 |
|---|---|
| `TriggerAdjustment()` | **无参**触发一次参数调整（ADR-027） |
| `BuildLookupTable(AutoParam)` | 生成查找表（基准公式；仅首建兜底与修正基准使用，ADR-043） |
| `RefreshSpotWidthByGain()` | 按当前系数 W 重算光斑宽度列（宽度档与分段修正不变，ADR-043） |
| `TryLookup(...)` | 按焊缝宽度匹配参数 |
| `Reset()` | 复位全部算法状态 |
| `FeedSeamTracking(...)` | 喂入一帧线激光结果，返回 PVT 点数组 |
| `TickSeamTracking()` | 强制输出一段 PVT 点 |
| `DrainSeamTracking()` | 排空剩余 PVT 点 |
| `ResetSeamTracking()` | 复位轨迹跟踪算法（**同时复位 PVT 与 CSP 两个实现**） |
| `OnSeamLaserResult(result)` | **CSP 模式**：喂入一帧线激光结果，更新示教锚定 Y 空间地图（ADR-042 / ADR-043） |
| `SeedSeamTrackingYAxisTarget(seedMm)` | **CSP 模式**：以示教 Y 轴锁定坐标（`TeachLockYMm`）播种起焊种子，保证零跳变（ADR-042 / ADR-043） |
| `TryGetSeamTrackingCorrectionMm(out target)` | **CSP 模式**：取当前 Y 轴实时目标（CSP 步骤每拍调用）（ADR-042 / ADR-042） |
| `SeamTrackingYAxisTarget` / `SeamTrackingHasAlarm` / `SeamTrackingAlarmReason` | **CSP 模式**：目标值与报警可观测性（ADR-042） |
| `SeamTrackingMapPointCount` / `SeamTrackingOutlierCount` / `SeamTrackingInvalidFrameCount` / `SeamTrackingSmoothSkipCount` / `SeamTrackingRobotX` | **CSP 模式**：诊断计数 + 最近机器人 X（ADR-042 / 2026-09-22） |
| `SeamTrackingAlarmRequested` | **CSP 模式**：折返超限报警事件透传（订阅方在流程线程处置）（ADR-042） |

> `WeldProcessCompletedEventArgs` 与事件名保留历史命名，未随类名改造。

---

## 四、数据类集合（`WeldParamData.cs`）

| 类/结构 | 职责 |
|---|---|
| `RobotWeldData` | 机器人焊接数据（坐标、速度、焊接区域判定） |
| `SeamCalData` | 焊缝宽度滑动平均计算器 |
| `AutoParam` | 自动参数配置（含 `CalVar` 计算 KVar/JVar） |
| `ChartVar` | 折线图坐标数据 |
| `WeldProcessCompletedEventArgs` | 焊接工艺调整完成事件参数 |
| `WeldFrameRecordEventArgs` | 过程帧记录请求事件参数（过程快照 7 项，不含帧索引） |
| `WeldAdjustmentRecordEventArgs` | 调整动作记录请求事件参数（继承 `WeldFrameRecordEventArgs`） |
| `SeamType` | 焊缝种类枚举（None/VType/TType） |
| `WeldFlowStep` / `WeldFlowStepInfo` / `WeldFlowSteps` | **2026-10-22 新增**：焊接流程步骤枚举、步骤信息（Title/SubTitle/Description）与五步总表（安全位→焊前检查→起焊→焊接→结束）。主界面 `steps1` 步骤条的唯一数据源（2026-11-10 设计器删除后已按业主指示补回） |

---

## 五、触发接口：`TriggerAdjustment`（无参）

```csharp
// WeldParamManager
public void TriggerAdjustment()
{
    if (CurrentAutoParam != null)
        _paramAdjustmentAlgorithm.ExecuteAdjustment(CurrentAutoParam, CurrentRobotX);
}
```

> **重要**：`TriggerAdjustment()` 是**无参**方法（[[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] 硬约束）。特征与配置已由 Manager 内部取用。⛔ **不要给它加参数**。
> 分段方式与失败阈值取自 `AlgorithmsConfig`，不再作为 `ExecuteAdjustment` 形参传递（ADR-033）。

---

## 六、焊接工艺控制流程（WeldParamControlWorkflow）

位于 `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs`，详见 [[api/WeldParamControlWorkflow]] 与 [[modules/DeviceControl]]。

### 数据链路

```
线激光结果（焊缝宽度）+ 机器人 RobotX
  ↓ WeldParamControlWorkflow.ComputeAndOutput()（只置 _pendingCompute）
WeldParamControlWorkflow.DoCompute()（执行步 10）
  ↓ WeldParamManager.Instance.TriggerAdjustment()  【无参】
WeldParamAdjustmentAlgorithm.ExecuteAdjustment → WeldParamLookupAlgorithm.TryLookup
  ↓ FillOutput（读 Manager 输出属性）
WeldParamOutput（功率/送丝/速度/摆幅）→ SendToRobot 下发机器人（执行步 20）
```

---

## 七、线激光引导 Y 轴轨迹跟踪（双模式并存，ADR-015 → ADR-042）

**定位**：本模块的「结果 → 运动」算法面。线激光结果**不再由线激光管理器直写控制器**，
而是经本模块算法做修正/建图后输出**运动目标**，由 [[api/MotionControlWorkflow]] 负责写入。

**模式由 `SEAM_GUIDE/TRACKING_MODE` 二选一（ADR-042）**：

| 模式 | 算法实现 | 输出 | 写入方式 |
|---|---|---|---|
| `CspRealtime`（默认） | `SeamMapTrackingAlgorithm`（实现 d） | **绝对 Y 轴目标**（`Yt = 测量时刻轴值 Ya1 + dY − 机器人 Y 差分`） | 流程步骤按拍 `RunCspTick()` → 台达**运动缓冲流式段写入**（`Set_Crd` → `Line_MultiAxis2` → `BufferStart`；10ms/100Hz，ADR-043 / ADR-042） |
| `PvtStream`（保留） | `SeamTrackingAlgorithm`（实现 c） | `PVTPoint[]` 点数组 | 缓冲 + `IPVTMotion.BeginMove` / `ContinueMove` 预下载点表 |

> ⛔ **两模式互斥**：`MotionControlWorkflow.OnSeamResultReady` 按模式分派，CSP 分支喂入后**直接 return**，不再走 PVT 链路。

### 模式一：CSP 实时目标（现行默认，ADR-042）

**需求根因**：PVT 点表把「时间轴」交给控制器，而焊缝前瞻与机器人位姿是实时变化的；一旦局部修正量变化，已预下载的点表无法回撤，只能等水位排空，形成**结构性滞后**。CSP 把插补交给驱动器，上位机每周期只给**目标位置**，可随时改。

```
线激光结果 + 测量时刻轴值（60Hz）──→ SeamMapTrackingAlgorithm.OnLaserResult(result, axisPosMm)
机器人位姿（RSI ~83Hz）──→ WeldParamManager.OnRobotDataReceived（订阅 CommunicationManager.RobotDataReceived）
                              ↓  UpdatePosePredictor（ADR-045：喂入点重锚 + 相邻差分速度，CurrentRobotX/Y 读取时刻外推；模拟 SimTick 喂入 UpdateRobotPose 同经此预测器，双链路同机制）
                              ↓  OnRsiPose(robotX, robotY, robotZ)（~~保持喂入原值~~ ⚠️ 2026-09-29 补正：原值原则只约束 Y；入图键另由 UpdatePredictedRobotX(CurrentRobotX) 刷为预测值，写入/读出同源）
                     ┌──────────────────────────────────────┐
                     │ 地图值 = 测量时刻轴值 Ya1 + dY（无低通）          │
                     │ 按 RobotXL = 测量X+LeadDistanceMm 插查        │
                     │ 双判据野值 + 最终目标突变护栏                     │
                     │ 零相位对称窗高斯平滑（σ=12mm）             │
                     │ Y轴目标 = 平滑绝对目标（Ya1+d）                       │
                     │ 行程限幅 [YAxisMinMm, YAxisMaxMm]          │
                     └──────────────────────────────────────┘
                              ↓  YAxisTarget（double，lock 保护）
MotionControlWorkflow 的 CSP 分支按拍推进（OutputCspTick，10ms/100Hz 随流程）
                              ↓  实测 dt → 速度限幅 50mm/s → 加速度限幅 500mm/s² → 防过冲 (0.02mm)
                     ICspMotion.SetCspTargetPosition(目标) → EtherCAT PDO → 驱动器内部插补
```

**两层解耦**：① **目标更新频率**（线激光 60Hz / RSI 位姿 ~83Hz）与**写入节拍**（100Hz）无关——写入侧按拍取「当前目标」重算整形，RSI 抖动不直通轴端；② **写入节拍**与**起焊 / 停焊 / 报警处置**同属一个 `FlowProcess` 步序列，控制闭环不再跨线程（ADR-042）。

**缺值量测（阶段 1）**：`WeldParamManager` 新增只读 `NoValueDistanceMm` / `NoValueSource`。起焊沿开窗清零、停焊沿关窗；激光有效帧到达清零。位姿有效按 `|ΔX|` 累计；位姿停顿（间隔 > 2×RSI 周期 12ms）按 `v_weld×Δt` 推定、速度钳位 100 mm/s，日志以「尺源=推定」区分。阈值 `NO_VALUE_TOLERANCE_MM` 默认 5.0 mm、读入钳位 1~50 mm、越界记一条 Warning。**本阶段只观测，不触发停焊动作**（动作在阶段 7）。

**X 折返处置（两档）**：偶发折返（累计 ≤ `ReverseAlarmMm`）**仅警告一次并继续**；连续折返超阈值 → `WeldParamManager.SeamTrackingAlarmRequested` → [[api/MotionControlWorkflow]] 在**流程线程** `Fail()` 停机（跨线程不推进执行步）。

### 模式二：PVT 流式段（保留，ADR-015 原方案）

线激光结果经 `SeamTrackingAlgorithm` 做修正与标定转换后**输出 PVT 点数组**，
由 [[api/MotionControlWorkflow]] 负责缓冲区管理与写入控制器。

#### 偏差模型与三级修正

```
偏差 = (特征Y − CalibratedCenterY) × AxisMmPerLaserMm × GuideSign
运动目标 = 轴当前值 + 偏差
```

| 环节 | 行为 | 参数 |
|---|---|---|
| **无值容差** | 机器人行程内无有效结果 → 偏差记 0 继续移动；累计行程超限 → `HasFault` 报警 | `NoValueToleranceMm` |
| **超限剔除** | 相邻偏差跳变超过阈值 → 不归入轨迹计算，保持上一有效偏差 | `OutlierLimitMm` |
| **单调约束** | 行程窗口内只朝一个方向移动，反向抖动抑制为保持 | `MonotonicWindowMm` / `MonotonicDeadbandMm` |

> ⚠️ **2026-09-22 影响面（ADR-042）**：上表参数**同属 `WeldAlgorithmsConfig`**（与 CSP 路径共用），其中 `MonotonicWindowMm` 默认值已由 2.0 改为 **200.0** 且语义定义为「持距兜底上限」—— **本 PVT 路径仍按「按行程窗口重置」消费该值**（L163，**未同步** ADR-042 的方向锁迟滞释放改造），故其方向锁实际持续时间由 2mm 变为 200mm；`NoValueToleranceMm` / `OutlierLimitMm` 已**退出界面**，仅本路径消费。
> 🔧 **待补齐项**：PVT 回退路径的 `ApplyMonotonic` 语义**未与 CSP 路径对齐**（CSP = 方向锁 + 迟滞释放 `MonotonicReleaseMm`；PVT = 窗口重置）。若后续仍保留 PVT 链路，建议同步换为迟滞释放，或为两路径拆分独立参数。

#### 数据链路

```
LineLaserManager.ResultReady
  ↓ MotionControlWorkflow 订阅（仅 Working 态喂入，且 TRACKING_MODE = PvtStream）
WeldParamManager.Instance.FeedSeamTracking(结果, 实测帧率, 轴当前位置)
  ↓ SeamTrackingAlgorithm 搓合 SeamGuideSample（+ 机器人 X + 时间戳）
滤波 / 超限剔除 / 单调约束 / 标定转换
  ↓ 返回 PVTPoint[]（攒够 BatchSize 或 Tick 强制）
MotionControlWorkflow 缓冲区 → IPVTMotion.BeginMove / ContinueMove → Y 轴
```

> ⚠️ `SeamTrackingAlgorithm` 内部读 `WeldParamManager.Instance.CurrentRobotX` 作为机器人 X。
> ⛔ ~~该 `RobotWeldData.PosX` 字段仍无人写入（恒为 0），故 PVT 模式的行程判定实质失效~~——**2026-09-17 复核已接通**：RSI 链路写入 `RobotWeldData.PosX`（`WeldParamManager.cs:160` setter、`:459` `CurrentRobotX = position.X`），PVT 行程判定恢复有效（见第八节沿革标注）。
> ✅ **CSP 模式绕开了该缺陷**：`SeamMapTrackingAlgorithm` 的机器人位姿来自 RSI 上行快照（`OnRsiPose`），不依赖 `CurrentRobotX`。

---

## 八、遗留项

### 记录订阅方待落地（TODO，ADR-033）

算法已改为只发记录请求事件，但**订阅方尚未实现**——`ProductFileControl` 结构待一并优化后再接入。
接入前：`FrameRecordRequested` / `AdjustmentRecordRequested` / `AbortRecordRequested` **无消费者**，
过程记录（`RunRecordManager.RecordProcessFrame` / `RecordAdjustment` / `AbortRecording`）**暂缺**。
接入要求：订阅方只做入队（O(1)），落盘在后台异步执行，不得在计算路径上同步落盘。

> ⚠️ 同一问题**同样适用于 CSP 模式**：`SeamMapTrackingAlgorithm` 目前连记录请求事件都未定义，
> 折返报警只走 `TrackingAlarmRequested`（控制语义），**无痕迹留存**。接入记录订阅方时需一并规划。

### 振镜摆幅：已实现（摆幅宽度/摆幅频率查表 + 公式兜底）

> **2026-10-20 实现摆幅宽度**（业主需求「AutoParam 增光斑摆幅系数/摆幅宽度、公式、表格加列、非固定输出光斑模式按焊缝宽查表输出摆幅给振镜电机」）；
> **2026-10-21 增摆幅频率**（业主需求「摆幅频率与摆幅成反相关，基准 2mm→500Hz、10mm→200Hz，据此构造基准公式；DB 增摆幅频率列，公式初值入表 → 表格手动核对 → 焊接时查表输出」），
> **同日删除旧摆幅通道**（业主裁定「旧思路没有使用方，需要删掉以免干扰」：`WeldAlgorithmsConfig.WeaveAmplitudeK`(k) + `Curves/WeaveWidthTable` 整类）。
> 语义澄清：**单一焊接配置内光斑大小不变**（对焦/送丝标定的初始默认光斑），随焊缝宽度变化的是**振镜摆动宽度**——故新增参数为「**摆幅宽度**」而非光斑宽度。

| 环节 | 落点 | 口径 |
|---|---|---|
| 参数与公式 | `AutoParam.SpotSwingGain`（光斑摆幅系数，默认 1.2）/ `AutoParam.SwingWidth`（摆幅宽度） | `CalVar()` 内 `SwingWidth = SpotSwingGain × SeamWidth`；系数非正自愈为 `DefaultSpotSwingGain`（旧 JSON 缺字段自愈） |
| 频率基准 | `AutoParam.SwingFreqRefWidth1/2` + `SwingFreqHz1/2`（默认 2mm→500Hz、10mm→200Hz） | `AutoParam.CalSwingFrequency(摆幅宽度)` 两点线性反相关：`f = h1 + (h2−h1)×(w−w1)/(w2−w1)`，外段按端点钳位，再钳协议 [10,500]Hz；两基准点宽度重合时退化为点②频率（不除零）。**2026-10-21**：两个频率**默认常量** `DefaultSwingFreqHz1/Hz2` 由 `const double` 改为 **`const int`**（协议侧频率本为整型 10~500Hz 精度 1，与 `GalvoFrequencyMinHz/MaxHz` 一致）；实例字段 `SwingFreqHz1/2` 仍为 `double`（JSON 反序列化需浮点，插值计算在 double 域内完成） |
| 公式初值入表 | `WeldParamLookupAlgorithm.SwingWidthDic`（宽→摆幅宽）/ `SwingFrequencyDic`（宽→频率 Hz） | 逐档写入：摆幅宽 = `宽 × SpotSwingGain`；频率 = `CalSwingFrequency(该档摆幅宽)`；重建整表会用公式初值覆盖手工修正（与三张工艺表同口径） |
| 手动修正/核对 | `AutoParamForm` 表格「摆幅宽度」「摆幅频率」两列（均可编辑）→ 写回查表 → `SaveCurrentProfile()` | 两列**各自独立修正、互不自动联动**（频率初值按公式算出的摆幅宽度，非手动修正后的值） |
| 落库 | DB 分段表第 6 列「振镜摆幅」= 摆幅宽度字典；**第 7 列「摆幅频率」= 频率字典**（`WeldAutoParamProfile.SwingWidthJson` / `SwingFrequencyJson`） | 7 列读写闭环；旧第 7 列「振镜频率」为历史遗留（读取方已废止）保留不删，新列名与旧列并存 |
| 运行期取值 | `WeldParamControlWorkflow.CalcGalvoAmplitude` / `CalcGalvoFrequency` | 固定输出光斑模式（`EnableGalvoWeave=false`）摆幅返 0 不驱动振镜；非固定模式①查表（最近档，容差 100）→②公式兜底 |
| 输出载体 | `WeldParamAdaptControl.GalvoAmplitude` / `GalvoFrequency` | 主支路与 XL 支路**同源填充**（避免两条下发路径不一致） |
| 振镜下发 | `LaserWeldHeadWorkflow.ApplyGalvoAmplitude` | 摆幅取 `LastOutput.GalvoAmplitude`、频率取 `LastOutput.GalvoFrequency`（唯一下发口，三量合并，任一变化才重发）；振镜初始设定仍来自工艺设置·振镜控制设置，焊接过程中由查表值逐拍修改 |

> 摆幅宽度公式**唯一来源**为 `AutoParam.SpotSwingGain`（初值/兜底/表格展示三处同源）；摆幅频率公式**唯一来源**为 `AutoParam.CalSwingFrequency`（锚点=摆幅宽度，业主口径）。
> **已删除的旧通道**：`WeldAlgorithmsConfig.WeaveAmplitudeK`（INI `WEAVE_AMPLITUDE_K`，公式 `宽×(1+k)`，k 默认 0.2）、`Curves/WeaveWidthTable` 整类（`GetAmplitudeMm` / `LoadCalibration` / `TryGetFrequencyHz`）、`WeldParamManager.WeaveTable` 持有、`WeldAlgorithmsConfig` 中该 INI 键的四点闭环——均无使用方，2026-10-21 业主裁定删除（csproj 已退注册，drift REMOVED 已登记）。
> `SpotWidthGain`（W，光斑宽度 W 通道）保留不动。

### ~~机器人 X 坐标无真实来源~~（✅ 2026-09-17 已解决，沿革保留）

`WeldParamManager.CurrentRobotX` 内部读写 `RobotWeldData.PosX`。~~该字段从未被任何代码写入、恒为 0~~ →
**2026-09-17 复核已接通**：RSI 链路写入 `RobotWeldData.PosX`（`WeldParamManager.cs:160` setter、`:459`
`CurrentRobotX = position.X`），PVT 模式的行程判定与焊缝长度保护恢复有效。
（沿革记载：原处置为「待通信层对接 KUKA 真实坐标，ADR-027 遗留项」。CSP 模式本不受此限——其位姿经
`WeldParamManager.OnRobotDataReceived` → `SeamMapTrackingAlgorithm.OnRsiPose` 直取 RSI 上行，ADR-042。）

---

## 关联

- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] — 本次算法分层决策
- ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 算法纯净性与记录职责隔离
- [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — 焊缝跟踪 CSP 实时目标方案与双模式并存（现行默认）
- ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — CSP 输出并入 FlowProcess 步骤驱动（撤销独立 1ms 线程）
- ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 焊缝跟踪示教锚定标定模型与线激光配置归并（标定中心=示教特征点 Y + `TeachLockYMm`；配置 39→37）
- [[lessons/AlgorithmControlRecordIsolation]] — 对应踩坑记录
- [[lessons/StepDrivenWorkflowPitfalls]]（七.5）— 1ms 线程调度（**2026-09-16 起随独立线程移除而失效**，页内已加沿革处置）
- [[lessons/StepDrivenWorkflowPitfalls]]（七.2）— 跨线程不推进执行步
- [[standards/ModuleOrganizationPattern]] — 模块组织范式标准
- [[api/WeldParamManager]] — Manager 唯一入口 API
- [[api/WeldParamAdjustmentAlgorithm]] — 参数调整算法 API
- [[api/SeamTrackingAlgorithm]] — 焊缝几何轨迹跟踪算法 API（PVT 模式专属）
- [[api/SeamMapTrackingAlgorithm]] — 绝对 Y 轴目标地图 + CSP 实时目标算法 API（CSP 模式专属）
- [[api/WeldParamControlWorkflow]] — 流程编排（计算后下发机器人；ADR-043 起含 60Hz XL 输出支路）
- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] — 焊缝宽度来源选择与工艺参数 XL 输出链路（现行）
- [[api/MotionControlWorkflow]] — 轨迹点消费与控制器写入
- [[modules/DeviceControl]] — `WeldParamControlWorkflow` 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（含完整数据链路）
- ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 轨迹构造原始决策（已演进）
- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] — 工作流作为调整主驱动
- [[modules/LineLaserCam]] — 英莱线激光，焊缝信息源头

## 阶段 7：缺值策略与按距离分段（2026-11-17 / ADR-103）

- 缺值累计（`WeldParamManager.NoValueDistanceMm`，阶段 2 落地）在本阶段成为唯一消费源：CSP 保持、入图暂停、报警停焊、心跳 H2 均读同一值。
- 自适应分段统一为「每段距离 mm」（`SEGMENT_DISTANCE_MM`，1~50 默认 5），旧键只读忽略；段内无有效点不查表，由缺值报警兜底。
- UI 只保留一个输入框与一条红色提示，不提供续焊入口。
- 关联：[[decisions/ADR-103-no-value-hold-and-distance-segment]] · [[api/WeldParamManager]] · [[api/WeldParamAdjustmentAlgorithm]]

## 阶段 7 补充：报警停焊载荷冻结（2026-11-17 / ADR-104）

- 报警停焊链在 `ReportAlarm` 同拍级联 `ErrorAborted`，本模块随之停止计算与下发，`LastOutput` 保持报警时刻值。
- `FlowProcess` 与 `PreWork` 增加报警门禁，杜绝半途 `StepOutput` 再下发与 `Working` 回拉；`MonitorAlignTick` 报警期停走，剪丝回检不再覆盖载荷。
- RSI 五具名元素停止刷新即冻结，通道与周期不变；`TxNG` 示警，清警经 `ClearRobotCommand` 停发，恢复刷新只在下次焊接进入 `Working`。
- 关联：[[decisions/ADR-104-rsi-channel-payload-freeze-alarm-stop]] · [[api/WeldParamControlWorkflow]] · [[api/CommunicationManager]]
