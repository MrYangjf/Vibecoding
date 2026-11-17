---
title: ADR-Index — 编号唯一准绳
date: 2026-09-17
updated: 2026-11-17
tags: [索引, 决策, ADR, 编号体系, 知识库治理]
status: accepted
---

# ADR-Index — 编号唯一准绳

> **现行编号：001~107 连续无断号**（2026-10-30 全库重编：原 068~094 段整体前移 16 位补齐 052~067 空段）。**新增 ADR 取 max+1 = 108**。
>
> **本库只保留现行编号**——历史编号段与旧号映射表已全部移除（旧决策的内容已并入对应现行页，追溯请直接读该页）。⛔ 废止号不回收、不复用（被并入他页的旧号在表中以指针行留档，并在承接页 `merged_from` 中留痕）。
>
> 任何新 ADR 必须同步本表 + `wiki/index/index.md` 对应行；两处计数不一致即治理违规。

## 全部 ADR（001~107，按主题族分组）

> **现行有效页 = 100 页**（另有 7 个旧号已并入他页，以指针行留档 —— **废止不回收编号**，旧号不重用）。

| 编号 | 页面 | 主题 | 状态 | 日期 |
|---|---|---|---|---|

**基础规约与架构**

| 001 | [[decisions/ADR-001-CS73-Constraint]] | C# 7.3 语法约束决策 | accepted | 2026-07-01
| 002 | [[decisions/ADR-002-DisposePatternFullCoverage]] | Dispose 模式现行决策（UI DisposeComponents + 非 UI 标准 IDisposable；整合原 001/020） | accepted | 2026-08-19
| 003 | [[decisions/ADR-003-EnumDeduplication]] | 枚举去重策略 — 子命名空间禁止重复定义父命名空间枚举 | accepted | 2026-08-01
| 004 | [[decisions/ADR-004-NuGetLocalization]] | NuGet 本地化 — 所有依赖 DLL 从 3rdDepend 引用 | accepted | 2026-08-06
| 005 | [[decisions/ADR-005-NamespaceDirectoryAlignment]] | 命名空间与目录严格对齐（namespace = AdaWeldSystem + 目录路径） | accepted | 2026-09-14
| 006 | [[decisions/ADR-006-ModuleOrganizationPatternStandard]] | 模块组织范式沉淀（Core + 抽象层 + 实现层 + Manager 四件套） | accepted | 2026-09-14
| 007 | [[decisions/ADR-007-CodeSimplificationStandard]] | 代码精简规范沉淀（精准执行、免重复输入） | accepted | 2026-08-21
| 034 | [[decisions/ADR-034-ArchitectureRawSource]] | 架构原档单一来源约定（raw/architecture；旧 037） | accepted | 2026-09-02
| 035 | [[decisions/ADR-035-RawDesignRefinement20260903]] | 原档 9-03 细化：主控设计完全重构与冲突裁定（旧 038） | accepted | 2026-09-03
| 066 | [[decisions/ADR-066-ThreeLayerConvergence]] | 三层架构收敛：① 轴定位唯一入口（MontionManager 新增 GetAxisByKeys/GetDeltaAxisByKeys/GetAxisConfigByKeys + 内置四类角色关键字表，FindAxisNameByKeys 为 private）；② TAConfig 合入 WeldAlgorithmsConfig（TaForceN/TaPose1Mm/TaPose2Mm，TAConfig.cs 已注明移除（2026-10-14 ADR-066 合入工艺配置并删除；独立 INI 文件不再使用））；③ WeldParamManager 不再触碰运动轴，迁移并入 LoadAlgorithmsConfig | accepted | 2026-10-14

**UI 框架 · 布局 · 控件**

| 008 | [[decisions/ADR-008-UIFrameworkMigration]] | UI 框架从 SunnyUI 迁移至 AntdUI | accepted | 2026-07-20
| 009 | [[decisions/ADR-009-DialogWindowToModalUserControl]] | 子对话窗承载方式：AntdUI.Window+PageHeader → Modal 承载的 UserControl | accepted | 2026-07-30
| 010 | [[decisions/ADR-010-LayoutContainerFreedom]] | 布局容器自由化（解除 GridPanel/FlowPanel 强制使用） | accepted | 2026-08-12
| 011 | [[decisions/ADR-011-ButtonShadowDeviceSwitch]] | MainPage 硬件快捷开关 FloatButton→ButtonShadow（⚠️ 2026-10-22 布局演进：2×2 按钮+等高 Alert，尺寸运行时核算） | accepted | 2026-08-31
| 012 | [[decisions/ADR-012-AlgorithmEditInterfaceSplit]] | 算法编辑界面按接口分隔（Tabpage / UIPage + AddPage，单独个例仅记录为当前） | accepted | 2026-07-27
| 036 | [[decisions/ADR-036-UIControlPlacementRule]] | UI 层级与控件归位规则：TabPage/ControlPage 弹出的对话框必须归入 SubDialog/&lt;业务域&gt;Dialog/（闭合 ADR-005/009；旧 039） | accepted | 2026-09-18
| 049 | [[decisions/ADR-049-MainPageDualChartAndCamPreview]] | 主界面双图化与监控相机预览接入（业主 VS 重排布局 **5 图 → 2 图** · `formsPlot2` 四合一工艺参数图 + `checkbox1~4` 显隐 · `panelCam` 预览 `imageBoxCam` **设计器声明**（含复选框文本/默认勾选态）+ 30Hz 显示刷新 · `PreviewFrameEvent`/`CurrentMat` 帧所有权分治；⚠️ **2026-10-22 演进：`panelCam`/`imageBoxCam` 与 30Hz 预览已随主界面预览移除而废止（决 2/决 3），双图化条款仍有效**） | accepted | 2026-09-29
| 051 | [[decisions/ADR-051-ILCamPageTabsConversion]] | ILCamPage Tabs 化（单页承载 + 分页预留）：根 `uiTableLayoutPanel1` 挂入 `tabsIL` → `tabPageLaserCapture`（`Controls.Add` + `Pages.Add` 双写，`tabsIL.Text="英莱相机设置"` / 页文本「线激光采集设置」）；原四行布局与内部控件零改动；只改设计器、`.cs` 零改动 | accepted | 2026-09-30
| 054 | [[decisions/ADR-054-MainPageSingleSelectionAndAlarmText]] | 主页面工艺参数曲线五项互斥单选（Checkbox + 手动互销，不用 `AntdUI.Radio`）+「焊缝宽度」文案改「接头宽」+ 送丝Z轴位置先建位不画线 + 状态栏改报警信息（去前缀、报警档给具体原因、禁枚举直出）+ 子设备 6→4 项 | accepted | 2026-10-09
| 056 | [[decisions/ADR-056-DataReviewRangeFilterAndModularMultiSelect]] | 数据追溯区间筛选（`DatePicker` → **`DatePickerRange` 闭区间** + 新增 `SelectTables` 逐日读表合并，366 天上限，旧单日链保留）+ 列表**多选列**（`AutoCheck=false` 保写入路径唯一，筛选栏全选/全取消/反选）+ **多选合并曲线**（无勾选回退单行）+ **悬停读数**（⛔ 不用未核实的 ScottPlot 坐标 API，改自算线性近似 + 60ms 节流）。⚠️ **P1 原编 071，因与子流程重构撞号改号 072** | accepted | 2026-10-09
| 060 | [[decisions/ADR-060-P4UiLanding]] | P4 UI 落地范式（TA/LA 动作双区共用 · 未就绪置灰 · 振镜图形配置化 GALVO_PATTERN · 阴影卡/三件套/BoolEventHandler 控件范式；批J 起） | accepted | 2026-10-09
| 062 | [[decisions/ADR-062-InpageZoneGridPanelLayout]] | 页内分区容器范式：嵌套 Tabs 改 GridPanel 同屏分区（7 区：快捷设置 4 + 激光工艺 3，内层 GridPanel 排 LA 区双卡片）；⛔ GridPanel 逆序入流；同父多 Dock=Fill 仅格位容器合法；ADR-051 双写仍适用外层 | accepted | 2026-10-12
| 065 | [[decisions/ADR-065-EnableManagementConsolidation]] | 启用管理收口（快捷设置页 4 列网格收 6 个工艺开关，⛔ 即改即存须补 CheckedChanged 订阅 · 振镜摆动两侧异名双向同步防 CS0101）+ 待补充区整体删除 + 快捷调试块拆分（Y轴回标定位搬 Tracking 指令区 / 光斑回标定位无指令删除 / 送丝结构锁定即 TA_Pose 删除） | accepted | 2026-10-13
| 069 | [[decisions/ADR-069-PanelInnerGridZoneCells]] | 分区容器统一（批K）：嵌套链固定「页级 GridPanel → 分区 Panel → 区内 GridPanel」；快捷设置 4 区 Panel 内 TableLayoutPanel→gridProcessDebug / 裸放→gridQuickTa/La/Tracking；⛔ 撤销反向嵌套（gridLaserLaZone 改名 panelLaserLaZone 降级 Panel 删 Span）；**二轮演进**——行高规范 60（标题）/40（控件）+ 每行四列（TA/LA 5 Radio 拆 4+1），振镜功能与图形控件自 panelLaserLa 迁入 gridLaserZones 原空白第 4 格（新增 panelLaserGalvo + gridLaserGalvo，4 格满挂；lblGalvoState 2026-10-15 业主删除）；**三轮演进**——行高规范 40（标题）/30（控件）+ 每行最多四列 + 每控件格宽 160（60/40+fill 废止）；`.cs` 零改动 | accepted | 2026-10-14
| 071 | [[decisions/ADR-071-SystemPageGridAndU4Rehome]] | 批L/批M 落地（方案 A）：① 全项目 6 个 TableLayoutPanel 转 AntdUI.GridPanel（tlpTrace/tlpLaserCalib/tbPanelAlogControl/tbPanelSimTest/tbPanelAdaparam/tbpanelweldponts → grid*，按 ADR-069 §三 40/30/160 自动分组，标题行判定=单子行+（纵向堆叠∨SetColumnSpan>1∨Dock.Fill））；② U-4 线激光十项归位工艺设置页跟踪工艺设置区（gridWeldPonts 7 行满额：迁入 标定中心Y/Z+示教Y 锁定，系统设置页 gridLaserCalib 只留角度+超时组）；③ 闭环保存入口（原 BtnSaveLaserCalib_Click 无订阅死处理器 → 新增 btnRead/btnSaveWeldPonts，保存双区落盘 Preset+System）；④ U-5/U-6 占位不动（功能搭建下轮） | accepted | 2026-10-15
| 072 | [[decisions/ADR-072-FullChainLayoutAndSplitPane]] | 全链布局修正 + 自适应页左右分栏：三子页补齐「页级Grid→卡片Panel→区内Grid→控件」链；行高弹性定理（`N:fill`=固定 Npx、裸 fill=弹性）；自适应页 `20% 80%` 左右分栏（左参数列表+三按钮，右参数设置），Columns/CellClick 后置铁律+三重删除保护；gridTrace 2×2 大分区；日志 Tag→LogTag；LA/TA 补区内 Grid；孤儿可见化（右键删除菜单）；四轮 gridAlgoControl 目标视觉序三错（段序逆/两对粘标题下/对内倒置）经五轮复正为 19 行正序。详见 ADR-072 单页 | accepted | 2026-10-15
| 075 | [[decisions/ADR-075-LaserHeadUiControlConsistency]] | 激光头系统设置控件一致性：切换类控件统一 AntdUI.Switch（温度自动刷新 / LA 对焦电机使能 / 振镜使能（2026-10-23 补 swGalvoEnable，焊接中置灰由摆幅自动控制），CheckedChanged 单点订阅 + 程序回写抑制）；TA 送丝力矩电机复刻 Y 轴控制（8 图标按钮同序同图标 + 六项状态同判据 + MontionManager 六函数 + BindEvents 后置订阅×12）；振镜卡片顺序改「状态信号→设置→按钮」（状态读 0x6010 GalvoOn/DriverAlarm，按钮末行跨宽）；页面动作按钮统一「保存模拟参数」范式（Ghost+Hand+宋体12+BackHover 3,169,244+IconSvg）（整合旧 077（激光头页自动刷新与使能改按钮）） | accepted | 2026-10-22
| 105 | [[decisions/ADR-105-page-action-workflow-and-permission-gate]] | 页面动作统一经工作流与页面级权限门控：UI 页面只查询不直连硬件，连接/断开统一走 LineLaserWorkflow；页面释放只退订事件与停本页预览、不断设备；新增 TryPassPageAction 三档拒绝（关闭中/初始化中/权限不足），手动连接工程师权限、模拟启动管理员权限；初始化期连接置灰并给原因；复用现有轴表参数按钮与 AxisConfigForm，不新增控件 | accepted | 2026-11-17
| 077 | → [[decisions/ADR-075-LaserHeadUiControlConsistency]] | 激光头页自动刷新分区分控与前置门控 · LA 四键 · 使能类控件改按钮（**部分演进 ADR-075 第一条**）：① LA 末行四键（后退/前进/移动到目标/使能）+ 新增移动目标输入框（走 WSX 从站 `0x7000`/`0x6020` 唯一 PDO 写口）② 自动刷新**分区分控 + 双层前置门控**（`CanRefreshNow = Visible && IsMotionReady()`；按内页分发；开关默认 ON；⛔ 不新增计时器）③ 使能 Switch→纯图标按钮（删 `_syncingSwitch`/`SyncGalvoSwitch` 等四成员）④ 订阅收口 `BindEvents()`（**已并入 ADR-075**，原页已删；编号不回收） | deprecated | 2026-11-17 |

**主控状态 · 流程 · 生命周期**

| 013 | [[decisions/ADR-013-ThreeStateModelRefactor]] | 主控设计三态模型重构（SubDeviceState / SubDeviceWeldStatus / MainDeviceStatus） | accepted | 2026-09-02
| 014 | [[decisions/ADR-014-MainDeviceStateSemantics]] | 主设备状态机语义修正与初始化时序重构 | accepted | 2026-09-04
| 015 | [[decisions/ADR-015-ErrorReportingHierarchy]] | 报错分层与状态切换零日志 | accepted | 2026-09-04
| 016 | [[decisions/ADR-016-WorkflowResponsibilityBoundary]] | 流程与子设备对象权责边界（R1~R5） | accepted | 2026-08-31
| 017 | [[decisions/ADR-017-SafetyCheckConsolidation]] | 安全检查三文件合并为单一安全检查流程 | accepted | 2026-08-31
| 023 | [[decisions/ADR-023-LineLaserWorkflowRefactor]] | 线激光工作流分步重构（switch-case + step） | accepted | 2026-08-20
| 024 | [[decisions/ADR-024-LineLaserThreeLayerRefactor]] | 线激光模块现行决策（三层结构 · 职责分工 · Manager 单一入口；整合原 034/035/036；**2026-11-09 增补单活约束**：一次只能连一种线激光或虚拟相机，切换即释放 / 连接前置拒绝 / 发送方身份校验） | accepted | 2026-09-08<br>2026-11-09 增补
| 032 | [[decisions/ADR-032-SimulationTestRedesign]] | 模拟测试统一化重构（平直搭接 + 连接态自动分支 + CSP 轨迹记录器；旧 035） | accepted | 2026-09-17
| 038 | [[decisions/ADR-038-RobotCommandDrivenStepFlow]] | 机器人指令驱动步骤流（子流程禁自迁步 · 行程判断归主控 · 模拟仿真器反馈驱动；旧 041） | accepted | 2026-09-20
| 039 | [[decisions/ADR-039-SimulationTestAutoTerminationAndRecordCacheRelease]] | 模拟测试自动终止契约与记录缓存释放（行程到程/子设备异常自动停模拟 · SaveRecord 落盘清缓存 · 焊缝跟踪轴名须匹配实际轴；旧 042） | accepted | 2026-09-20
| 041 | [[decisions/ADR-041-ResidentFlowNonBlockingParadigm]] | 常驻流程非阻塞范式：三层铁律（流程层常驻按拍 / 等待层轮询变量 / 命令层下发即返回）· 步号范式 · 初始化链步驱动 · 指令前置条件问询（旧 062） | accepted | 2026-09-23
| 055 | [[decisions/ADR-055-SubFlowStateEliminationAndParamClassRelocation]] | 子流程状态消解（四个自建状态枚举**全部删除**而非降私有，对外只用 `SubDeviceWeldStatus`；`MotionControl.IsRunning` 改判 `IsServoOn()`）+ 参数类归位（`WeldParamOutput` → **`WeldParamAdaptControl`** 迁 `WeldParamData.cs`，主动控制轴位置另立 `WeldParamMontionControl`；`RobotX` 从输出类移除）+ 落地 ADR-013 §A47 与 ADR-016 R1 | accepted | 2026-10-09
| 061 | [[decisions/ADR-061-WeldStatusTransCascadeWiring]] | WeldStatusTrans 编排入口接线（CascadeWeldStatus 末尾触发 · 恢复 ADR-042 停焊沿/ADR-038 Stopping 入口）与恒假判据修复（ADR-055 双源消解残留） | accepted | 2026-10-10
| 092 | [[decisions/ADR-092-ExceptionLoggingAndShellRemoval]] | 异常留痕五级分类（A 必打 / B 汇总 / C 静默-清理 / D 静默-探测 / E 静默-递归），禁在循环与日志渲染路径打日志；TA 兼容壳（`LaserWeldHeadWorkflow` 7 方法）删除，唯一入口 = `MotionControlWorkflow`；两个距离分段 TODO 保留并改写措辞 | accepted | 2026-11-06
| 098 | [[decisions/ADR-098-readiness-layering-axis-capability]] | 分层就绪 L0~L4 与轴级能力：断连/L0 已连接/L1 已使能/L2 未回零/L3 已回零/L4 已到工作零位；能力用 NeedHoming/HasAbsoluteEncoder/WorkZeroSource 描述，免回零轴使能后直接 L3；禁按轴名分支；`EnsureReadiness` 拒绝原因含当前 L/需 L | accepted | 2026-11-16
| 099 | [[decisions/ADR-099-init-reset-separation]] | 初始化与复位分离：初始化只做连接+使能，结束态固定「已连接/已使能/未回零/无运动」；机器人通讯 `Mandatory=true`；受理门禁（运行中/急停/复位中拒绝）与补连判据（全连即跳过）；初始化期 `IOWork` 不判互锁；复位门槛 L1 且按轴能力分支（需回零轴 Home→工作零位，免回零轴只去工作零位），失败停 L2/L3 可重试；回退开关 `INIT_RUN_TA_HOME` | accepted | 2026-11-16
| 100 | [[decisions/ADR-100-state-union-and-action-gate]] | 两套状态联合与动作入口双闸门：设备 6 态 × 流程 7 态矩阵；设备态不自动级联流程态；1 s 巡检挂 `thIOWork` 只纠 `Stop×Working` / `NoReset×非NoReset` / `Alarm\ | EStop×Working`（报警 3 s 宽限）；子流程 `ErrorAborted` 唯一上送 `ReportAlarm`，只升不降；设备态变化沿一条 Info（演变 ADR-015 D2）；动作入口校验设备态 `Running` + `EnsureReadiness`（自动焊接 L4、焊前检查 L0，模拟放行）；`GetStatusSnapshot` 只读统一快照；不新增流程态枚举值 | accepted | 2026-11-17
| 101 | [[decisions/ADR-101-shutdown-closure-and-estop]] | 关闭闭环与急停：唯一关闭顺序 + 30 s 预算 + 强制退出留痕 + `线程 n/11 设备 m/4` 汇总；`_disposed/_shuttingDown` 幂等与拒绝新业务；`CascadeDisconnect` 改受理+等待+单台 5 s；模组/通讯线程标志拆分；关闭期 `IOWork` 只保活；急停固定 停运动→置EStop→停线程→ServoOff，不断设备；运控 `Close` 唯一入口 `InitializeOff` 且幂等；线激光连接线程与模拟线程 Join；退出链补管理器 SDK 释放 | accepted | 2026-11-17
| 107 | [[decisions/ADR-107-init-phase-reconnect-gate]] | 初始化期禁重连与设备动作 + 机器人端 XML 写入并发保护：thCommCommandWork（含通讯层自愈重连）不在 InitializeMachine 启动，改由初始化链结束后统一开启（正常结束走 FinishInitialization、抢占中止走 InitializeMachineTick 分支，经 EnsureCommandWorkStarted 幂等入口）；初始化期禁止手动设备动作（FilebackupPage TryPassCommAction 两档门控）；SaveRobotRsiXml 写盘加 _rsiXmlLock + 临时文件 File.Replace 原子替换 + 占用退避重试 | accepted | 2026-11-17

**运动控制 · 运控 · TA 力矩**

| 027 | [[decisions/ADR-027-MotionControllerDeltaReplacement]] | 运动控制器台达 EtherCAT 现行决策（选型 · ZMotion 移除 · 全量对接；整合原 032/033） | accepted | 2026-09-06
| 028 | [[decisions/ADR-028-MotionControlModule]] | 运控调整模块架构决策 | accepted | 2026-07-16
| 030 | [[decisions/ADR-030-WeldHeadSlaveDeviceUnderMotionControl]] | 焊接头现行决策（WSX 从站挂靠台达 EtherCAT · 归运控管控；整合原 049/051） | accepted | 2026-09-15
| 044 | [[decisions/ADR-044-SeamEndSemanticsAndMotionAxisScope]] | **焊缝收尾语义与运控轴范围**（焊缝终止X · 线激光在 X−前置量 收工 · 运控只服务 Y 向焊缝跟踪轴）· **2026-09-28 就地补正**（编号不变）：回标定位小步 22 追加**位置优先短路**——轴已静止且已在 0.02mm 容差内直接转小步 23，消除「重发为空动作 ⇒ `IsMoving()` 恒假 ⇒ 空等 15s」阻塞 | accepted | 2026-09-24（09-28 补正）
| 053 | [[decisions/ADR-053-TaLaCurveAndMotorScale]] | TA/LA 标定曲线（只以采样点表表达，继承 ADR-043 红线）+ WSX 电机量纲可配置且换算单一入口 | accepted
| 057 | [[decisions/ADR-057-TaLaActionAndFollowControl]] | TA/LA 动作指令与 auto 随动（力矩下压/锁止/预设位 · 光斑-偏移双曲线随动 · 限位报警归安全线程；P3 批E F-1/F-2） | accepted | 2026-10-09
| 073 | [[decisions/ADR-073-AxisControlUnifiedMontionManager]] | 轴控制统一入口 MontionManager：六单轴函数（MoveTo 自动使能 / StepMove / ToggleServo / JogStart / StopAxis / HomeAxis，ADR-066 定位入口的控制对偶）；⛔ UI 页禁直控 MontionAxis 控制成员（AbsMove/JogMove/AxisStop/Servo*/HomeNoBlock 调用数=0 判据）；轨迹页 8 控制按钮自 tableAxis CellLink 迁出为固定按钮（19→11 列，AxisRow 9→1 CellLink，BindEvents 后置订阅×12，MouseLeave 拖离兜底）；日志/Message 留页面，Manager 只回结果 | accepted | 2026-10-19
| 081 | [[decisions/ADR-081-InitUniformServoOn]] | 初始化完成后按配置统一使能：`DeviceControlWork.InitStepEvaluate` 在子设备全就绪后调一次 `MontionManager.EnableAxesAfterInit()`（仅 `ENABLED=true` 轴，逐轴「轴名+结果+`LastCommand` 原因」）；存在失败轴 ⇒ `InitializationCompleted` 收 false，⛔ 不重试不轮询；`TA_Auto` 内部 `ServoOn` 降为兜底；原设计无「初始化自动使能」且无「等操作员确认」守卫，属缺口补齐 | accepted | 2026-11-04
| 082 | [[decisions/ADR-082-TaInitFourStepAndAvailability]] | TA 初始化四步与可用性：加载轴+默认 XML → TA 轴装配判定（2026-11-05 起不再读 P1；`TaHome` 非空 + 轴注册表命中） → 配置成功才使能 → 使能后自动 `TA_ZeroPose`（工作零位，CSP 绝对定位 ≠ 回零）；`TaAvailable` = 配置成功 ∧ 已使能 ∧ ZeroPose 到位，任一失败 ⇒ 全 TA 指令执行期拒绝（**UI 不再置灰**：连上+装载即可点，失败红底 + Tooltip，见 ADR-063 §六）；`TA_ZERO_POSE_MM/VEL/TOL_MM` 缺键默认 0/1.0/0.1 不覆盖现场（整合旧 083（TA 力矩模式门禁删除）） | accepted | 2026-11-05
| 084 | [[decisions/ADR-084-TaForceToTorqueConversion]] | TA 下压力按 100% 力量基准换算 CST 千分比：新增 `ROOT/TA_HOME/TA_FORCE_100PCT_N`（默认 37N，缺键不覆盖）；`目标‰=round(力值/基准×1000)` 保号限幅 ±1000；基准≤0/力值>基准/换算为 0 均拒绝（⛔ 不 1:1 兜底）；日志双单位；旧 `TorqueTarget` 迁移改为按基准换算。台达口头口径 PM46=额定电流、PM49=推力常数（手册未给数值定义）；线性区推导 扭矩‰≡电流‰，不含摩擦/饱和。业主口述规格 31A/1.4A/26.1N/A 乘积 36.54，未获手册证实，默认仍 37（整合旧 085（扭矩爬升速率与方向）） | accepted | 2026-11-05
| 088 | [[decisions/ADR-088-TaSharedTorqueLimit]] | CSP 推动阻抗与 CST 最大出力共用 `ROOT/TA_HOME/TA_TORQUE_LIMIT_N`（缺省 = 100% 力量基准）：`GetTorqueLimitPerMille` 唯一换算、`SetTorque` 唯一下发点钳制、`ServoOn` 在伺服 OFF 窗口写 `16#6072` 并回读；0x6072 运行期可写性手册未收录故取定值路线；日志分「被钳制/已贴边/余量≤10%/有余量」四态（整合旧 090（否决 CSP + 速度上限路线查实）） | accepted | 2026-11-06
| 091 | [[decisions/ADR-091-TaParameterConsolidation]] | TA 参数收口：工作零位只保留工艺页 `TA_ZERO_POSE_MM`，速度/容差/加减速复用 TA_Pose1/2 同源（轴 `MaxVel` + `InstructionDefaultTolMm` + `AccTime/DecTime/STime`），删 `TA_HOME_ZERO_POSE_VEL/TOL_MM` 两键；整段删除 `ScanTaPositionLimit`（越限撤力+报警，锁不住位置且打断力矩）与弹窗「软限位模式」行；`SOFT_LIMIT_MODE` 键与 CSV 列保留 | accepted | 2026-11-06
| 093 | [[decisions/ADR-093-FlowTimeoutConfigAndLayering]] | 流程等待超时全部收敛到 `DeltaMotionConfig` 的 `ROOT/FLOW_TIMEOUT`（21 键，缺省=改造前值，越界回退+告警，运行期读取免重启）；按距离分段防呆唯一入口 `EnsureSupportedSegmentation()`；消灭 `DoTaZeroPose` 70s 忙等改事件驱动；架构归属硬约束（硬件→MontionManager / 指令→Workflow / UI 不持轴不解析状态字 / 配置由配置对象持有） | accepted | 2026-11-06
| 094 | [[decisions/ADR-094-ta-single-entry]] | 同类指令单一入口 + 枚举 switch 分派（TA 族 7 方法收敛为 `TaExecute(TaCommand)`）；全族形态一致（ZeroPose 由异步 worker 改阻塞到结果）；阻塞只允许在后台指令执行体；自动流程只调自动指令并等完成信号 | accepted | 2026-11-09
| 083 | → [[decisions/ADR-082-TaInitFourStepAndAvailability]] | 取消「先开力矩模式才能用 TA_Auto」：删 `swTaTorqueMode` 与 `TaTorqueModeEnabled`/`SetTaTorqueMode`/`TaTorqueModeChanged`；可用性只由 `TaAvailable`；`TA_Auto` 自切 CST（模式字回读==10 → `CST_Start_Move` → `CST_Output_Enable(1)`，失败回 CSP）；复用三条件 AND（输出态 ∧ 模式字 ∧ 参数未变）；Break/Pose/Retract 仍撤力但不再置灰；`TORQUE_MODE` 键保留给送丝轴（**已并入 ADR-082**，原页已删；编号不回收） | deprecated | 2026-11-17 |
| 085 | → [[decisions/ADR-084-TaForceToTorqueConversion]] | 扭矩爬升速率归位 + 扭矩方向独立：`TORQUE_SLOPE` 唯一 UI 入口从系统设置页迁至 TA 轴「参数」弹窗（`AxisConfigForm`），删除旧控件/校验/回写（含未挂载孤儿 `lblOptTaSlope`），布局 `gridWireCurve` 13→11 格；读 `DeltaAxisConfig.TorqueSlope`、写回 `AXES/AXIS/TORQUE_SLOPE`（⛔ 不写 TA_HOME），校验 1~65535 零写入；新增 `ROOT/TA_HOME/TA_TORQUE_DIRECTION`（±1，默认 +1，缺键不覆盖）；工艺页 `TaForceN` 改非负大小、负号显式拒绝，`目标‰=方向×round(大小/基准×1000)`；旧负值迁移缺键则置 -1 并取绝对值、已有键以键值为准并告警双负号风险；Y 轴弹窗 19 行不变（**已并入 ADR-084**，原页已删；编号不回收） | deprecated | 2026-11-17 |
| 089 | → [[decisions/ADR-088-TaSharedTorqueLimit]] | ~~TA 扭矩方向反转两段式（穿越斜率 / 交接点 / 速度守卫）~~ → **已废弃**：业主收口「只保留一个爬升速率」，三键与两段式逻辑全部删除。⛔ 删除不解决跑飞/撞击，根因是 CST 无速度上限（**已并入 ADR-088**，原页已删；编号不回收） | deprecated | 2026-11-17 |
| 090 | → [[decisions/ADR-088-TaSharedTorqueLimit]] | ❌ **否决** TA 改「CSP 位置模式 + 力矩上限」：工艺要求恒定力持续下压且位置随工件走，CSP 必须记账指令位置 ⇒ 偏差长期存在 ⇒ 必然报警；「顶住重锚」等于锁点，违背工艺。已全部回退，TA 恢复 CST；并查实速度限制三条路线（`0x607F` 对 CST 无效 / `0x6080` 与 `DeltaServo_Set_Velocity_Limit` 手册未收录需实测 / **CSV + `0x6072` 推荐**）（**已并入 ADR-088**，原页已删；编号不回收） | deprecated | 2026-11-17 |

**相机 · 算法层 · 记录**

| 018 | [[decisions/ADR-018-CallbackAcquisition]] | 回调等待取图决策 | accepted | 2026-07-01
| 019 | [[decisions/ADR-019-MonitorCamBoundaryAndEmguALGRefinement]] | 监控相机与 EmguALG 现行决策（麦格威三层 · 业务边界 · 五层细化；整合原 007/037/039） | accepted | 2026-09-09
| 020 | [[decisions/ADR-020-MonitorCamPage-AlgorithmInline]] | 监控相机页面命名与算法参数内联 | accepted | 2026-07-17
| 021 | [[decisions/ADR-021-CameraConnectionStateDecoupled]] | 相机连接状态与工作流程状态解耦 | accepted | 2026-07-21
| 022 | [[decisions/ADR-022-EmguALGThreeLayer]] | 算法模块（EmguALG）三层改造：两检测统一调度 + 点云/焊缝上报链删除 | accepted | 2026-09-08
| 031 | [[decisions/ADR-031-ProductLifecycleRecordModule]] | 产品记录模块现行决策（归口 · ProductRecordBase 抽象 · 记录类自包含；整合原 008/026/046/047；旧 034） | accepted | 2026-08-31
| 037 | [[decisions/ADR-037-ProductProductionRecordLifecycle]] | 产品生产记录生命周期（WeldResultRecord 为生命周期单位 · 会话基名对齐三份记录文件 · 调整含 Job 切换；旧 040） | accepted | 2026-09-20
| 046 | [[decisions/ADR-046-MonitorCamIpScanAndStrictMatch]] | 监控相机 IP 扫描与严格匹配（顶栏连接入口 · `ScanDevices` 三层 · 连接 IP 落盘 · 指定 IP 不匹配即失败） | accepted | 2026-09-29
| 047 | [[decisions/ADR-047-MonitorCamSwitchToHikMvs]] | 监控相机实现切换海康 MVS（麦格威=海康魔改实证 · 实现层 HikCam · 契约不动 · 严格 IP 语义继承） | accepted | 2026-09-29
| 048 | [[decisions/ADR-048-MonitorCamTabsRecordPlayback]] | 监控相机页 Tabs 化与录像/回放能力（焊接相机设置/焊接回放双页 · 契约 +12 成员 · 单线程喂帧 · 标定 Calibration 节） | accepted | 2026-09-29
| 052 | [[decisions/ADR-052-ProductionRecordSchema]] | 生产记录 Schema 扩展：WeldActionRecord 15→20 字段 + 双写侧同批 + 既存缺陷补齐（二进制侧从未写 SeamPointY/Z）+ 列名抽常量 | accepted
| 078 | [[decisions/ADR-078-MonitorPlaybackControlBarAndDatedRecords]] | 焊接回放播放控件栏与日期目录录像列表：悬停显隐 50% 半透明双层控件栏（进度/时间 + 5 按钮居中）、帧索引进度与帧累加器倍速（0.8/0.5/0.3/0.1/1.0 · 1.5/2/2.5/3/1.0）、±5s 跳转、旧「停止回放」删除；录像落 yyyyMMdd 子目录（Manager 统一，手动/自动同口）；列表按 DatePickerRange 区间筛选（日期优先取目录名，回退修改时间）+ CellImage 缩略图后台代数加载；**2026-11-02 演进**：回放栏外层改 `gridPlayBar`（`AntdUI.GridPanel`，`Span="fill;fill;-26 fill"`，2 区域逆序入格），按钮区恢复 `tableLayoutPlayCenter`（`TableLayoutPanel`），删除 `gridPlayCenter`；倍速/前后退按钮图标化 + 新增 `lblPlaySpeed`；外层 `panelPlayBar` 改 `AntdUI.Panel`（`Back` ARGB128 + `Shadow=5`，`Padding` 校准） | accepted | 2026-10-30
| 095 | [[decisions/ADR-095-hardware-fault-tree-ownership]] | 硬件故障/报错文本只由持有该硬件的 Manager 产出；流程层只标识失败步骤与硬件对象并引用诊断，UI 只展示成品（可按宽度截断）；将 ADR-094 D2 的偏离升格为通用原则；线激光 `ret=` 与连接失败文案已按该口径下沉（第二轮） | accepted | 2026-11-09
| 097 | [[decisions/ADR-097-algorithm-layer-ownership-single-entry]] | 算法层归属与唯一入口：算法层 = `EmguALG`（EMGU 用法 + 算法配置），`AlgorithmManager` 唯一实例化/取用入口；同级 Manager 不互持算法对象（撤销 `MonitorCamManager` 包装）；回放归 `EmguALG/RealtimeMonitor/Playback`（DTO 下移、根目录注入、跨页面会话复位、页面关闭不 Dispose）；标定十字走 `DrawSpotMark`；线激光轮廓算法收口；**二次调整**：回放迁 `RealtimeMonitor/Playback` 并改名 `PlaybackAlgorithm`、ROI 重建为通用工具（按需加载）、线激光渲染 DTO 下移、焊参/监控两域无混淆登记（整合旧 096（帧载体边界）） | accepted | 2026-11-09
| 096 | → [[decisions/ADR-097-algorithm-layer-ownership-single-entry]] | 帧载体边界：`Mat` 继续作帧载体，不引入中性帧；以层间禁止项卡死（UI 禁 `new Mat`/`CvInvoke`/`VideoCapture`/逐帧解码/像素运算；帧创建/标注/编解码/释放归 Manager 与流程层，Dispose 随创建方）；**D2 回放归属 / D3 Manager 持有算法对象已被 097 取代**（**已并入 ADR-097**，原页已删；编号不回收） | deprecated | 2026-11-17 |

**线激光 · 焊缝跟踪 · 工艺**

| 042 | [[decisions/ADR-042-SeamTrackingConsolidated]] | **焊缝跟踪综合**（物理场景 · 模拟环境 · 算法实现 · 实现路径：数据源→计算→入图→CSP 运动缓冲出图·算法配置 · 接入点：Manager/启动门控/起焊沿逐拍停焊沿/PVT 备用；整合旧 033/044~055/057/058/060/063~066 共 20 页） | accepted | 2026-09-23
| 043 | [[decisions/ADR-043-WeldParamControlConsolidated]] | **焊缝参数控制综合**（使用场景 · 模拟环境 · 算法实现：分层/纯净性/查表与调整 · 本地数据库关联：分段表/载入优先级/自愈 · 实现路径：宽度来源/光斑/XL 缓存/计算公式 · 接入点：TriggerAdjustment/播种/TickXlOutput；整合旧 031/032/056/059/061/067 共 6 页） | accepted | 2026-09-23
| 045 | [[decisions/ADR-045-PredictiveRobotPoseSnapshot]] | **预测性机器人位姿快照**（真实 RSI / 模拟 SimTick 双链路按频率阶梯喂入的闭环激励 · 喂入点重锚 + 差分速度 + 读取时刻外推 · ~~地图入图保持喂入原值~~ ⇒ **2026-09-29 就地补正**：该原值原则只约束 Y；**X 写入与读出同源，入图键亦取预测值**（`UpdatePredictedRobotX`）） | accepted | 2026-09-28<br>2026-09-29 补正
| 050 | [[decisions/ADR-050-SimulationWeldCameraIntegration]] | 模拟测试接入焊接相机（自动运行模式，预览走主页）：**Ready** = 在线检查 + 打开设备（`PrepareSimulationMonitorCam`，不在线**只告警不阻断**）；**PreWork 跳过**（光丝对中未做）；**Start** = 连续采集 + 打开录像（`SimMonitorCamStartWeld` 挂 `case 22`，失败只告警不阻断焊接，帧经 `PreviewFrameEvent` → 主页 30Hz）；**焊接结束** = 关录像 + 停采集（`SimMonitorCamStopWeld` 幂等零害 = 三停止命令链 + `DisableSimulation` 兜底） | accepted | 2026-09-29
| 058 | [[decisions/ADR-058-WireAlignMillimeterAndCutWireChain]] | 光丝对中毫米化与剪丝链（两套算法合并 · Y 三级只报警 · X 补偿单点耦合 · RSI T13 回检循环；P3 批F F-7/F-8/F-9） | accepted | 2026-10-09
| 059 | [[decisions/ADR-059-P3TailGalvoAndJointParam]] | P3 尾巴落地（振镜频率第7列自适应与手动演示 · 对中→振镜补偿默认关闭门控 · 接头参数收编与 Platethickness 保留裁决；批H F-3/F-4/F-6） | accepted | 2026-10-09
| 063 | [[decisions/ADR-063-CommandZoneRadioExclusivity]] | 指令区 Radio 互斥（同父容器自动互斥 · `BoolEventHandler` 而非 `EventHandler` · 仅 value=true 触发）+ 指令与参数分离 + TA_Break 停止位只读反馈；**2026-11-05 改版**：可用性只看「`MontionManager.IsInitialized` + 该轴已装载」（⛔ 不再用 ZeroPose/力矩模式置灰）、点击先 `AntdUI.Modal` 确认、取消回退上一选中项（`_suppressActionRadio` 防递归）、执行成功 `Fill` 半透明绿 / 失败半透明红 / 未选中 `Transparent`、失败原因写 Tooltip | accepted | 2026-11-05
| 064 | [[decisions/ADR-064-TaConfigLayeredConsolidation]] | TA 配置分层收口：新建 TAConfig 只收工艺三项（ForceN/Pose1Mm/Pose2Mm，INI）；TorqueModeEnabled/TorqueSlope 永久留轴配置（驱动器参数）；TorqueTarget 弃用 + 一次性迁移 | accepted | 2026-10-12
| 067 | [[decisions/ADR-067-LATaSettingsSemanticRework]] | LA/TA 工艺语义重构：三区改名（跟踪工艺设置(Tracking Settings)/对焦工艺设置(LA Settings)/送丝下压工艺设置(TA Settings)）· LA 区动作按钮组→参数设置区（删 7 控件新增 10 控件，与 TA 同形态照 ADR-066 范式）· LA 三指令语义重写（LA_Pose 纯到位 / LA_Spot 曲线A反查定位后退出随动 / LA_Auto 定位+持续随动保光斑，联动唯一源 TaLaCurveConfig）· TA 回缩指令（快捷 Radio 第 5 项；2026-11-05 由 TA_Recheck 更名为 TA_Retract 并改为力矩反向回缩，见 082 D19~D23） | accepted | 2026-10-14
| 068 | [[decisions/ADR-068-WeldAlgorithmsConfigZoneReorg]] | WeldAlgorithmsConfig 按 UI 4 分区重组（AlgorithmsZone 四区 System/Quick/Adapt/Preset，UI 面板与配置代码块一一对应）+ 分区读写接口 LoadZoneXml/SaveZoneXml/LoadZoneIni/SaveZoneIni（总入口内部调用，净行为不变）+ SeamWidthSource 只读派生化（~~EnableSpotWidthFollow 控制~~ ⚠️ 已被 ADR-070 演进为 EnableGalvoWeave，删 SEAM_WIDTH_SOURCE 键仍有效）+ EnableGuide/EnableMonotonicConstraint 唯一入口收敛 | accepted | 2026-10-14
| 070 | [[decisions/ADR-070-GalvoWeaveAsWidthSource]] | 振镜摆动即宽度来源开关：删 EnableSpotWidthFollow/ENABLE_SPOT_WIDTH_FOLLOW/swEnableSpotWidthFollow（快捷区 6→5 开关，gridProcessDebug r2 改 2 列），SeamWidthSource 派生源改 EnableGalvoWeave（业主裁定：光斑宽度跟随与振镜摆动实为一个意思——光斑宽度不可调，真正变化的是振镜摆幅宽度形成光斑宽度变化）；RefreshSpotWidthByGain 重算职责并入振镜开关两处处理器；手动固定宽度 ManualSeamWidthMm 入振镜卡（lblManualWidth+txtManualWidth 失焦即存走 Adapt 区，与系统设置页同源双入口）+ 振镜卡开关移最后一行 + 同键双视角文案（激光卡「开启摆动/停止摆动」=运动控制开关、快捷区「振镜跟随摆动工艺」=工艺启停）；推翻 ADR-068 §三 新开关条款（只读派生与 SEAM_WIDTH_SOURCE 停用结论仍有效） | accepted | 2026-10-15
| 076 | [[decisions/ADR-076-SettingsZoneSaveWiring]] | 三界面参数读存与分区落盘接线裁定：① **分区归属随 UI 落点迁移**（`MaxMapPoints` 由 ④Preset 改 ①System，XML 键路径 `SEAM_GUIDE/MAX_MAP_POINTS` 不变、存量文件兼容、同区唯一写口）② **赋值必须先于落盘**（⑤工艺输出三项原在 Adapt 落盘之后才赋值 ⇒ 不落盘）③ **禁跨区副作用**（「保存焊参调整」原顺带落 ①System 区；系统设置页保存原顺带落 ④Preset 区 ⇒ 一并剥离）④ **禁全量保存**用于单分区项（振镜图形 / Y 指令改分区保存）⑤ **读取按钮必须真读文件**（`MontionManager.LoadWeldHeadConfig()` 此前 0 调用方 ⇒ 两页「读取参数」接线）⑥ **同一批配置项只允许一条「UI→内存」入口**（`ApplyAdaptUiToMemory` / `SaveGalvoPattern`）⑦ **数值解析口径统一**（InvariantCulture 优先 + 当前文化回落） | accepted | 2026-10-23
| 087 | [[decisions/ADR-087-TaCstEntryRampAndNoPositionResidual]] | TA 力矩进入协议：冷启动先停稳位置运动 → 切 CST → ±1‰ 方向种子 → 开输出 → 再下发目标与 slope（保证冷启动也走斜坡）；热切换直接重发目标；删除「参数未变即跳过」复用捷径；方向种子覆盖驱动器内残留反向扭矩，消除位置转力矩「先反跑」 | accepted | 2026-11-06
| 103 | [[decisions/ADR-103-no-value-hold-and-distance-segment]] | 缺值保持与自适应按距离分段：缺值期 CSP 取上次有效目标（held），仅首个有效目标前允许标定位起步；缺值或位姿 `age>2T` 暂停入图；达 `NoValueToleranceMm` 一次报警（Error + `TX_NG` + `ErrorAborted(NoValueAlarm)`，不复用 `DoStopMachine`、不清累计器）；自适应改 `SEGMENT_DISTANCE_MM`（1~50 默认 5）按段距取段内均值查表，旧键 `IS_COUNT_TYPE`/`COUNT_NUM` 只读忽略；UI 合并为「每段距离(mm)」加红色提示条；心跳 H2 接缺值超限 | accepted | 2026-11-17
| 104 | [[decisions/ADR-104-rsi-channel-payload-freeze-alarm-stop]] | 报警停焊时 RSI 通道保持与自适应载荷冻结：通道由收包信号驱动、周期不变；报警链立即 `CascadeWeldStatus(ErrorAborted)`，`FlowProcess`/`PreWork`/`MonitorAlignTick` 以 `ErrorAborted`/`IsAlarmstop` 收口，摆焊执行器非 `Working` 归零；五具名元素停止刷新即冻结；`TxNG` 锁存示警，清警 `ClearRobotCommand` 停发；清警只回 `NoReset` 不续焊 | accepted | 2026-11-17

**通讯 · 机器人 · RSI**

| 025 | [[decisions/ADR-025-CommModuleRefactor]] | Comm 模块现行决策（三层重构 · XML 按设备分离 · 通道目录；整合原 004/006/045） | accepted | 2026-09-14
| 026 | [[decisions/ADR-026-RsiSemanticRewriteAndDualChannel]] | KUKA RSI/EKI 通讯现行决策（语义重写 · 互斥单通道 · Tool 三标量 · 格式文档驱动 · 配置目录；整合原 050/052/053/054/055） | accepted | 2026-09-15
| 074 | [[decisions/ADR-074-RsiNumericProtocolImplementation]] | RSI 数值化协议落地（ADR-026 决策 2 实施）：占位符扩 11 项（5 焊参 + 3 TX + IPOC）；修「回复线程未用已装载格式文档」真 bug；CommandCore 增数值码映射（RX 9 / TX 10，反查表自动生成）；上行 RxCmd/RxPayload、下行 TxCmd/TxPayload/TxSeq；焊参走 5 具名元素通道（废止 "P..S..V..G.." 文本协议）；**EKI 通道整体退役**（KukaEkiComm.cs 已移除：整文件删 + csproj 退注册 + Manager 分支清零 + UI radio 删）；通讯调试面板落既有 panelRobot（19 控件：状态条/上行注入/下行下发/焊参注入/收发包监视）；机器人侧职责边界（⛔ 不实现振镜/LA/TA，避免双主） | accepted | 2026-10-21
| 102 | [[decisions/ADR-102-heartbeat-levels-and-comm-reconnect]] | 心跳分级与通讯层自动重连：心跳线程仅在 RSI 监听成功后创建；只做 H0/H1/H3/H4 分级与变化沿日志（H2 留阶段 7）；删除心跳内 `TryReconnectRobotComm`；通讯层 `EnsureRobotChannelHealthy` 5 s 冷却自愈，由指令线程每拍调用；新增 `NeedHeartbeat`（默认 true，只停日志不改在线显示） | accepted | 2026-11-17
| 106 | [[decisions/ADR-106-comm-log-view-channel]] | 通讯日志查看通道：新增 CommLogViewEvent + ShowCommLogForView（写 TcpMessageLog 文件 + 仅 FilebackupPage 打开时显示）；日志按行为/结果二分——行为（RSI 配置装载、线程启停、监听绑定、指令收发、重连过程）入通讯日志，结果（成败反馈：初始化/重连成败、配置加载成败、启停失败、线程异常）入主系统日志；心跳分级维持现状；修订 CodeSimplification ⑤规则4 归属口径 | accepted | 2026-11-17

**配置与键管理 · 台达硬件**

| 029 | [[decisions/ADR-029-CylinderConfigAndCsvImport]] | 气缸配置持久化与 CSV 导入通道 | accepted | 2026-09-16
| 033 | [[decisions/ADR-033-ConfigArchitectureStandard]] | 配置架构现行决策（类别文件夹 + XML/INI 分轨；整合原 005/059；旧 036）（整合旧 040（配置路径范式复正）） | accepted | 2026-09-16
| 079 | [[decisions/ADR-079-DeltaControllerConfigAndAwcfgPackage]] | 台达配置文档生成 + 系统设置整站包：五类文档识别 + 三级提示（CSV 表头签名；ESI 结构判据；xlsx 10 列 58 行=56 PDO+2 SDO-only）；ESI 即台达从站文档（列 NODE_ID/NAME/VENDOR_ID/PRODUCT_CODE/REVISION_NO/ENABLED，节点号取既有 WELD_HEAD_SLAVE/NODE_ID，缺失标待填）；xlsx 为唯一权威源、ESI 只交叉校验告警、不硬编码 PDO/SubIndex；焊接头复用 WeldHeadSlave.xml 新增 ROOT/IO_MAP（含 SOURCE_FILE/SOURCE_TIME/ROW_COUNT）；按节替换 + 时间戳备份 + 零写入；.awcfg 只含 system-settings（5 文件 + Simulation_INI），staging→scope/路径/白名单/SHA256→备份→原子替换→回滚 | accepted | 2026-11-02
| 080 | [[decisions/ADR-080-DeltaTorqueHomingSignedModeAndDetectParams]] | 台达扭矩回零 -3 经 `Home_Config` 下发（`HomeMode` 改 short，-4~35，U16 补码强转）；**2026-11-05 最终决断**：P1.087/P1.088 属伺服参数，控制器**删除全部写/读链路**（`ApplyTorqueHomeDriveParams`/`WriteCoEObject`/`ReadCoEObject`/`WaitSdoDone`/`DescribeSdoAbort` 等 + 配置/UI 两键），由驱动器默认参数决定；现场写 16#2157 回读报 `4869`（手册未收录）、台达口头结论「用默认值即可」、**现场 -3 回零已实测正常**；旧 XML 遗留键忽略不删，判据完全移交驱动器 | accepted | 2026-11-05
| 086 | [[decisions/ADR-086-ConfigSelfHeal]] | 配置自愈：`ConfigSelfHeal` 统一缺键补写（只增不改/备份+原子替换/回读校验/幂等/聚合日志），整文件缺失生成默认模板；预览与审计读零写盘；`TA_TORQUE_DIRECTION` 加载期不补 +1，必须由旧负值迁移判定后与其它缺键**合并一次写盘**，避免「补键一次+迁移一次」与方向误判；迁移只依赖已加载配置，不受 `IsInitialized` 门禁 | accepted | 2026-11-05
| 040 | → [[decisions/ADR-033-ConfigArchitectureStandard]] | 配置路径范式复正（回到 ADR-033 原式 `Config/&lt;功能类别&gt;/&lt;主题&gt;_&lt;格式&gt;/`；SeamTrackAxisName 归运控；禁跨模块读配置；取消兼容回退读；旧 043）（**已并入 ADR-033**，原页已删；编号不回收） | deprecated | 2026-11-17 |

> **维护规则**：本表是 ADR 编号的**唯一权威**。新增 ADR 取 `max+1`；废止某条 ADR 时**不回收编号**（避免与其它页引用的号撞车），改为在主题列注明「已废止并入 XXX」。
>
> **废止留档不变式（2026-11-17 治理轮）**：ADR 被并入他页时 —— ① 原页**删除**，其现行裁定并入承接页的「## 合并自 ADR-0XX」小节；② **旧号在本表保留指针行**（`| 040 | → [[decisions/ADR-033-…]] | …（已并入 ADR-033，原页已删；编号不回收） | deprecated |`），⛔ 不删行、⛔ 不重排序号（重排会改 3000+ 处引用）；③ 承接页 frontmatter 的 `merged_from` 记录被并的旧号；④ 全库指向被并页的引用（`[[…]]` / 裸号 / 相对路径链接）**一律改指承接页**，⛔ 不得残留指向已删页的链接。
>
> **相似度闸门不变式（2026-11-17 治理轮）**：新建 ADR 前**必须**跑 `tools/adr_new.py check <关键词>` —— 该命令按**落地实体符号 Jaccard**（`Class.Member` / `Method()` / `ROOT/KEY` 形态）判疑似重复，**≥0.40 即拦截新建**（退出码 2），命中时走 `adr_new.py merge` 把新决策并入既有页。⛔ 判「是否重复」不得看标题或正文措辞（同主题不同子问题的页对正文相似度可高达 0.14，而真重复的落地实体 Jaccard 显著更高）。
>
> **旧号消歧（与 [[lessons/StaticVerifier-AdrNumbering]] §8.3 同源）**：本表只登记**现行**编号；重编号/退役产生的旧号与现行号**同号不同页**时，正文裸写旧号一律带 **「旧」前缀**，「旧」号**不回收、不复用**。
