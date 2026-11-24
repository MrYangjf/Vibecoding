# Wiki Index — AdaWeldSystem 知识库索引

> 内容导向路由索引。AI 回答查询前先读本文件定位相关页面，再读目标页。
> **最后更新：2026-10-30（全库治理轮：ADR 编号重编为 001~078 连续；本文件由 `tools/wiki_index_build.py` 生成，勿手工编辑分类表）**
>
> **格式契约**：见 [[standards/WikiPageFormatSpec]]——各页结构、字段、增长规则与脚本工具链的唯一规范。
> **详细叙事一律在 `logs/log.md`**，本页只做路由。

---

## ⚡ 场景速查路由（首选入口 —— 命中即可开工，无需扫全表）

> 用法：接到任务后先在下表命中一行，直接读右列页面。未命中再往下翻分类表。

| 你要做的事 | 直接读这 1~3 页 | 硬约束提示 |
|---|---|---|
| 不知道某功能在哪块代码 / 代码依附关系 / 要不要全盘扫代码 | [[architecture/CodeMap]]（总览·模块骨架+定位陷阱） | ⛔ Phase0 先读总览定位模块，再读对应符号分片；命中即读代码块；禁一上来全库 Grep |
| 第一次评审优化（41 条需求）在做什么 / 改动落在哪 | [[project/ReviewOptimization-P1-StructureDesign]] + [[architecture/CodeMap]] | P1 五份产物；⛔ P2 落地后结构冻结，只可追加不可挪位 |
| 代码精简 / 注释精简 / 日志规范 | [[standards/CodeSimplification]] | 强制排除仅 `*.Designer.cs`；约束归知识库，0 消费预留成员禁删 |
| UI 状态判断 / 按钮 text / 连接态刷新 | [[standards/UiStateSimplification]] | 与 CodeSimplification 互补，二者都要看 |
| 流程与子设备权责 / 这个事件该不该放流程 | [[standards/WorkflowResponsibilityBoundary]] | 判据「数据是设备的，进度是流程的」，R1~R5 |
| 新增/改造一个模块 / 抽象层·实现层·Manager 怎么摆 | [[standards/ModuleOrganizationPattern]] | 判据「抽象层+实现层+Manager 三件套」；Manager 唯一对外访问口 |
| 流程怎么推进 / 步骤编号 / 卡在哪一步 / 超时判定 | [[architecture/DeviceControlArchitecture]] §5 + §16.3 | 现行 `RunStep` 由每个 `case` 内 bool 判定推进，无 `GoStep` 入口 |
| 写日志 / 日志标签怎么定 / `Tag` 有什么用 | [[api/GlobalCommData]] + [[standards/CodeSimplification]] §三 | `Tag` 是日志标签非死成员；设备日志直连 `ShowLog` |
| 用户改了 `raw/architecture/` 原档，要同步架构 | [[architecture/DeviceControlArchitecture]] §15 + [[decisions/ADR-035-RawDesignRefinement20260903]] | 原档 > 架构页 > 源码注释；冲突须用户裁定后按 §15.2 推进 |
| 设备状态 / 工作流 / 上电初始化 / 状态机 | [[architecture/DeviceControlArchitecture]] → [[modules/DeviceControl]] | 三态模型；状态写入唯一入口 `SetState`/`SetWeldStatus`/`SetStatus` |
| 新增或修改一个工作流 | [[architecture/DeviceControlArchitecture]] §4 + §16 + [[modules/DeviceControl]] | ⚠️ 改码前必读 §16；现行契约 17 项，配置读写无参，子设备各自持有配置路径 |
| 安全检查 / 安全互锁 / 故障恢复 | [[api/DeviceStatusWork]] + [[modules/ProductFileManager]] | 故障恢复已归口产品记录模块；记录 key 与注册 key 必须同源 |
| 线激光相机（族总览 / 取相机 / 切模拟） | [[modules/LineLaserCam]] + [[api/LineLaserManager]] | 三层：`ILineLaser/` 抽象 + 英莱/虚拟实现，Manager 唯一入口 |
| 线激光结果怎么用 / Y 轴轨迹 / 主页面取点 | [[decisions/ADR-042-SeamTrackingConsolidated]] + [[api/SeamMapTrackingAlgorithm]] + [[api/MotionControlWorkflow]] | 结果侧只转发 `ResultReady`；CSP 默认、PVT 备用，主页面轮询快照 |
| 英莱相机参数 / Job / 传感器 | [[api/IntelligentLaserCam]] + [[lessons/IntelligentLaser-Pitfalls]] | 参数以设备为唯一真相源，禁离线缓存 |
| 监控相机 / 焊中质检 | [[modules/MonitorCam]] + [[api/MonitorCamManager]] | 巡检在 Manager 不在工作流；实现层海康 MVS；页 Tabs 化（设置/回放） |
| 监控相机换麦格威（MecaVision MVSDK） | [[guides/MecaVision-DevGuide]] + [[api/MecaVisionMVSDK-Native]] | ⛔ 载体已退役：现行实现走海康 MVS，见 [[api/HikCam]] |
| EmguALG 算法三层改造 | [[modules/EmguALG]] + [[api/AlgorithmManager]] | 三层 Abstractions + 实时监测 + Manager 统一调度 |
| 运控（台达 EtherCAT） | [[modules/MotionControl]] + [[api/MontionManager]] + [[guides/DeltaEtherCAT-DevGuide]] | ⛔ 正运动已移除；三层 Native/IMotion/DeltaEtherCAT + Manager 业务层 |
| 台达 EtherCAT 运动控制模块（全新设计） | [[guides/DeltaEtherCAT-DevGuide]] + [[api/DeltaEtherCAT-Native]] | 目录结构与对外消费按原档；API 名以 SDK 头文件为准 |
| 焊接工艺计算 / 功率送丝摆幅 | [[modules/WeldParamControl]] + [[api/WeldParamManager]] + [[api/WeldParamControlWorkflow]] | `TriggerAdjustment()` 无参；算法分层 + 去记录化 + 配置合一 |
| AntdUI 控件用法 / 迁移 / 设计范式 | [[guides/AntdUI-Reference]] | 禁用 SunnyUI |
| WinForms 设计器报错 / 控件不显示 | [[guides/WinForms-Designer]] | Designer.cs 不可手改 |
| 跨线程更新 UI / InvokeRequired | [[guides/WinForms-UI-Threading]] | 后台线程禁止模态弹窗 |
| 编译错误 / 命名空间 / 新文件不参与编译 | [[guides/Namespace-Compilation]] | 新建 .cs 必须注册 .csproj（§1.1） |
| 日志追加位置 / 批量重命名 / .csproj / VibeCoding | [[guides/Project-Tools]] | 日志须追加到文件顶部；见 [[standards/WikiPageFormatSpec]] §2.5 |
| 源码/知识库云端备份 / 推送拉取 GitHub | [[guides/SourceBackup-GitHub]] | 双仓（代码 + LLMWiki）；SSH over 443；忽略 3rdDepend |
| INI / SQLite / XML 配置读写 | [[guides/Config-Data-Tools]] | 配置读写与工具手册 |
| 产品记录 / 过程数据归档 | [[modules/ProductFileManager]] | 三记录类 + Manager；订阅方已闭环 |
| 改任何 C# 代码前的通用门禁 | [[lessons/CSharp-Language-Pitfalls]] | C# 7.3，禁 C# 8+ 语法（ADR-001） |
| 写/改静态校验脚本 / 编译错误根因排查 | [[lessons/StaticVerifierJudgements]] + [[lessons/StaticCheckSemanticBlindSpots]] + [[lessons/SignatureAndWiringConsistency]] | 判据全文库九章；绿灯≠构建过（语义错误只有编译器能定） |
| 判据不生效 / 阈值自锁 / 改配置默认值没生效排查 | [[lessons/JudgementThresholdScaleMismatch]] + [[lessons/AlgorithmControlRecordIsolation]] | 阈值须大于信号量子；配置默认值≠生效值（现场 INI 会覆盖） |
| 改 UI 布局 / 设计器删控件 / 图表重排后编译报错 | [[lessons/UiLayoutChangeSyncPitfalls]] + [[lessons/UiRefreshUnifiedEntry]] | 改版后全量 Grep 后置引用逐条收敛；状态刷新走 `RefreshUi` 单入口 |
| 删一个 UI 功能模块 / 控件本体与专属字段怎么连带清理 | [[lessons/UiModuleRemovalCleanup]] + [[guides/AntdUI-Reference]] | 控件 4 落点+专属字段+Span 占位同批清；零引用≠死成员，须查读取点 |
| 启动即崩 / 界面未生成就开硬件 / UI 回调空引用 | [[lessons/StartupInitializationOrderGates]] | 静态构造禁重入日志；`IsUiReady` 门控按拍重试；回调判句柄状态 |
| 查 AntdUI 控件 / 设备 SDK 用法 | [[lessons/DocDemoDllLookupOrder]] | 顺序不可跳级：源码文档 → 官方 demo → DLL 侦查（设备 SDK 先厂商 demo） |
| AntdUI Modal.Config 编译报错（Form→Target 误报） | [[lessons/AntdUI-Modal-Config-Overload-Cascade]] | 第三参数未定义触发重载解析级联；owner 用 `Form.ActiveForm` |
| 模拟测试 / 虚拟相机 / 轨迹记录 | [[lessons/SimulationAutoBranching]] | 连接态纯计算派生不缓存；记录模式另开一路防早退丢轨迹 |
| 第三方原生 DLL 报 NullReferenceException | [[lessons/MecaVision-NativeDllLoadNRE]] | 静态构造 LoadLibrary 失败静默返回 Zero；3rdDepend 落文件≠部署完成 |
| GitHub 推送拉取失败 / Wiki 批量改页脚本 | [[lessons/GitHubSyncPitfalls]] + [[lessons/WikiDriftCorrectionPitfalls]] | 推送前四查；wiki 页 LF 入库，脚本按字节读写原样回写 |
| 流程规则 / 编码前要过哪些门禁 | [[rules/Rules-Index]]（编号唯一权威） | ⛔ rules/ 只收流程执行类；index 第十二节 → Rules-Index → 规则页 |
| 批量改 wiki 页 / 行尾乱了 / diff 变整文件 | [[lessons/WikiDriftCorrectionPitfalls]] | ⛔ 按字节读写；joiner 必须与 splitter 匹配；整文件 diff 先归因 |
| 批量替换脚本 / 锚点命中 0 / 替换串含被替换串 | [[lessons/StaticVerifier-Batch-Script-Traps]] | ⛔ 先干跑校验全部锚点；失败集可二分即先自审判据 |
| 新增规则 / 规则要演进 / KR 编号怎么分配 | [[rules/Rules-Index]] + [[standards/WikiPageFormatSpec]] §三 | ⛔ 先合并后新建；新号 = max+1；废止不回收编号 |
| 出包 / 备份包 / output 与 backup 的区别 | [[rules/KR-011-Backup-Output-Timing]] | ⛔ backup 在改码前、output 在定稿后；时机不可互换 |
| 无编译器 / 静态检查能不能算通过 | [[rules/KR-010-No-Compiler-Honesty]] | ⛔ 静态检查 ≠ 构建通过；语义缺陷只有编译器能定 |
| Skill 与 wiki 冲突 / 该信哪个 | [[rules/KR-004-Skill-Demoted]] + [[rules/KR-013-Skill-Pointer-Discipline]] | ⛔ wiki 优先；Skill 只写机制，不写死内容页名 |
| 页面格式 / 摘要多长 / 这页该不该拆 / 能不能新建页 | [[standards/WikiPageFormatSpec]] | ⛔ index 摘要 ≤120 字符；ADR/教训/规则一律先合并后新建 |
| 规则归哪类 / 内容类规则能不能进 rules | [[standards/WikiPageFormatSpec]] §2.4b | ⛔ rules/ 只收流程执行类；内容类归 lessons/standards/decisions |
| 硬件故障文案写在哪 / 流程层能不能拼状态字报警码 | [[architecture/DeviceControlArchitecture]] §10.8 + [[decisions/ADR-095-hardware-fault-tree-ownership]] | ⛔ 故障文本只由硬件 Manager 产出；流程只附诊断引用，UI 只展示成品 |

---

## 目录

| 章节 | 内容 | 何时看 |
|---|---|---|
| [一、项目总览](#一项目总览) | 3 个页面 · 概览 / 架构 / 工作流规范 | 概览 / 架构 / 工作流规范 |
| [二、模块详解](#二模块详解) | 16 个页面 · 模块边界与协作 | 模块边界与协作 |
| [三、API 参考](#三api参考) | 50 个页面 · 公共契约（调用前查） | 公共契约（调用前查） |
| [四、规范标准](#四规范标准) | 13 个页面 · 强制遵守（违反即不合格） | 强制遵守（违反即不合格） |
| [五、历史教训](#五历史教训) | 60 个页面 · 60 条坑 · 编码前门禁（逐条规避） | 编码前门禁（逐条规避） |
| [六、操作指导](#六操作指导) | 14 个页面 · 怎么做（查阅型） | 怎么做（查阅型） |
| [五、历史教训 lessons](#五历史教训) | 60 条坑 | 编码前门禁 |
| [七、设计决策 ADR](#七设计决策) | 107 条（001~114 连续，另 7 个旧号并入他页） | 理解「为什么」/ 查约束 |
| [八、历史归档](#八历史归档现归-project) | 5 个页面 · 项目级台账与审计 | 追溯，不引用 |
| [九、专员职责](#九专员职责) | 10 个角色 | 分派任务 |
| [十、来源索引](#十来源索引) | raw/ 映射 | 溯源 |
| [十二、流程规则](#十二流程规则) | 13 条（KR-001~KR-013） | Skill 流程执行强制规则 |

## 一、项目总览

| 页面 | 摘要 | 标签 |
|---|---|---|
| [[project/overview]] | AdaWeldSystem 项目概览 | #项目 #概览 #架构 |
| [[project/skill-evolution]] | Skill 体系演进历史 | #项目 #Skill #演进 |
| [[project/vibecoding-workflow]] | VibeCoding 工作流 — LLMWiki 原生版 | #工作流 #VibeCoding #开发流程 |

## 二、模块详解

| 页面 | 摘要 | 标签 |
|---|---|---|
| [[modules/Comm]] | Comm 模块 — 通讯与全局状态 | #通讯 #全局状态 #TCP/IP #S7 |
| [[modules/CommentConstraintRegistry-CrossLine]] | 注释跨行合并迁出台账 | #注释 #迁移 #工程约束 #C18 |
| [[modules/CommentConstraintRegistry]] | 注释迁出约束台账 | #注释 #迁移 #工程约束 #C16 |
| [[modules/DeviceControl]] | DeviceControl 模块 — 设备控制（三态模型：SubDeviceState / SubDeviceWeldStatus / MainDeviceStatus | #设备控制 #状态机 #连接态 #焊接过程态 |
| [[modules/EmguALG]] | EmguALG 模块 — 视觉算法（五层：Abstractions / Core / RealtimeMonitor / LineLaserContour / Manager | #图像算法 #EmguCV #五层架构 #送丝距离 |
| [[modules/FileOperate]] | FileOperate 模块 — 文件操作工具库 | #工具 #文件 #INI #XML |
| [[modules/KUKARobot]] | KUKARobot 模块（已并入 api/KUKARobot | #KUKA #机器人 #通讯 #RSI |
| [[modules/LineLaserCam]] | LineLaserCam 模块 — 线激光相机 | #相机 #线激光 #三层架构 #管理器 |
| [[modules/MonitorCam]] | MonitorCam 模块 — 自动焊接头监控相机（三层：IMonitorCam / HikCam / MonitorCamManager | #相机 #监控 #焊前对中 #焊中质检 |
| [[modules/MotionControl]] | MotionControl 模块 — 运控调整 | #运控 #水平移动 #模拟测试 #运动轴 |
| [[modules/PointCloudData]] | PointCloudData 模块 — 3D点云数据处理 | #3D #点云 #HelixToolkit |
| [[modules/ProductFileManager]] | ProductFileManager 模块 — 产品生命周期记录 | #产品记录 #过程数据 #生产信息 #文件 |
| [[modules/SQLiteDatabase]] | SQLiteDatabase 模块 — SQLite数据库 | #数据库 #SQLite #权限 #配置 |
| [[modules/Safety]] | Safety 模块 — 安全检查流程（DeviceStatusWork）+ 故障恢复 | #安全互锁 #安全检查 #故障恢复 #状态机 |
| [[modules/UIDesign]] | UIDesign 模块 — UI界面 | #UI #WinForms #AntdUI |
| [[modules/WeldParamControl]] | WeldParamControl 模块 — 焊接参数控制与工艺计算 | #焊接 #工艺 #自适应 #功率 |

## 三、API 参考

| 页面 | 摘要 | 标签 |
|---|---|---|
| [[api/AlgorithmManager]] | AlgorithmManager — EmguALG 统一调度入口（承接原 AlgorithmManager 与 PipelineManager 可复用职责 | #算法 #管理器 #EmguALG #配置 |
| [[api/CommSettingPage]] | CommSettingPage 通讯设置页 | #UI #通讯设置 #RSI #调试面板 |
| [[api/CommandCore]] | API — CommandCore 机器人指令协议（const string，取代 CommandTable | #指令协议 #机器人 #主控 #CommandCore |
| [[api/CommunicationManager]] | CommunicationManager API 参考（通讯管理器 · 模块唯一门面 | #通讯 #管理器 #门面 #KUKA |
| [[api/ConfigFileManager]] | API · ConfigFileManager（全局配置文档总管 | #配置 #Manager #ConfigFileControl #抽象层 |
| [[api/ConfigSelfHeal]] | ConfigSelfHeal 配置自愈 API | #配置 #自愈 |
| [[api/ConfigSnapshot]] | API · ConfigSnapshot（配置快照与差异审计 | #配置 #快照 #差异审计 #ConfigFileControl |
| [[api/DataReviewerPage]] | DataReviewerPage API 参考（数据追溯页 · 区间筛选 + 多选合并 + 悬停读数 | #数据追溯 #区间筛选 #多选 #悬停读数 |
| [[api/DeltaEtherCAT-Native]] | 台达 EtherCAT 原生 API 速查（EtherCAT_DLL | #运控 #台达 #EtherCAT #P/Invoke |
| [[api/DeviceControlWork]] | DeviceControlWork API 参考（整机主控 · 主设备运行态 MainDeviceStatus | #工作流 #主控 #上电初始化 #机器人交互 |
| [[api/DeviceMonitorPage]] | DeviceMonitorPage 设备监控页 | #UI #设备监控 #温度显示 #焊接头 |
| [[api/DeviceStateApiCore]] | DeviceStateApiCore API 参考（设备状态核心 · DeviceStateBase / DeviceWorkflowBase | #主设备控制 #状态机 #流程基类 #契约 |
| [[api/DeviceStatusWork]] | API — DeviceStatusWork 安全/IO/状态管控（+ SafetyFlow / SafetyInterlockChecker | #安全检查 #安全互锁 #工作流 #PLC |
| [[api/FilebackupPage]] | FilebackupPage 文档备份设置页（原 CommPage | #UI #文档备份 #通讯配置 #工艺配置 |
| [[api/FormMain]] | FormMain 主窗口 | #UI #主窗口 #导航 #状态标签 |
| [[api/GlobalCommData]] | GlobalCommData API 参考 | #通讯 #全局状态 #事件总线 |
| [[api/HikCam]] | HikCam — 监控相机海康 MVS 实现类（IMonitorCamApi 落地 | #相机 #监控 #海康 #MVS |
| [[api/HonorMachineTest-IOReference]] | HonorMachineTest IO 监控与执行参考基线 | #IO #线程模型 #参考基线 #DeviceStatusWork |
| [[api/ILAlgorithmEditForm]] | ILAlgorithmEditForm 算法编辑弹窗 | #UI #算法 #配置 #SubDialog |
| [[api/IntelligentLaserCam]] | IntelligentLaserCam API 参考 | #相机 #英莱 #线激光 #ADR-007 |
| [[api/IntelligentLaserSDK_CSharp_DevManual]] | IntelligentLaser SDK（C# 版）开发手册 |  |
| [[api/KUKARobot]] | KUKARobot API 参考（KUKA 机器人通讯 · RSI 单一通道现行契约与协议知识 | #KUKA #机器人 #通讯 #RSI |
| [[api/LaserWeldHeadWorkflow]] | LaserWeldHeadWorkflow API 参考（焊接头工作流 · 骨架期 | #工作流 #焊接头 #RunStep #SubDeviceWeldStatus |
| [[api/LeadshineLSnmc-Reference]] | 雷赛 LSnmcControler 参考基线 | #运控 #雷赛 #Leadshine #参考基线 |
| [[api/LineLaserCamPage]] | LineLaserCamPage 英莱线激光相机页 | #UI #线激光 #英莱 #权限 |
| [[api/LineLaserContourAlgorithm]] | LineLaserContourAlgorithm API 参考（线激光轮廓 Mat 渲染算法 | #线激光 #算法 #EmguALG #渲染 |
| [[api/LineLaserManager]] | API — LineLaserManager 线激光管理器（业务层单例 + 结果/轮廓业务处理点 | #相机 #线激光 #管理器 #单例 |
| [[api/LineLaserWorkflow]] | LineLaserWorkflow API 参考（三态模型：SubDeviceState / SubDeviceWeldStatus | #工作流 #英莱 #线激光 #SubDeviceWeldStatus |
| [[api/MainPage]] | MainPage 主页面 | #UI #主页面 #ScottPlot #英莱 |
| [[api/MecaVisionMVSDK-Native]] | MecaVision MVSDK 原生 API 速查 | #相机 #监控相机 #MecaVision #MVSDK |
| [[api/MonitorCamManager]] | MonitorCamManager — 监控相机业务中枢（原 MonitorCamManager，ADR-034 三层重构后改名承接 | #相机 #监控 #管理器 #健康巡检 |
| [[api/MonitorCameraWorkflow]] | MonitorCameraWorkflow API 参考（三态模型：SubDeviceState / SubDeviceWeldStatus | #工作流 #监控 #权责边界 #RunStep |
| [[api/MontionConfigForm]] | MontionConfigForm 运控配置窗体（已废弃 | #UI #运控 #配置 #CSV |
| [[api/MontionManager]] | API — MontionManager 运动管理器（业务层单例，取代已废弃的 MotionManager | #运控 #台达 #EtherCAT #管理器 |
| [[api/MotionControlWorkflow]] | MotionControlWorkflow API 参考（台达 EtherCAT 运控 · 三态模型 | #工作流 #运控 #台达 #EtherCAT |
| [[api/MoveControlData]] | MoveControlData API 参考 | #运控 #水平移动 #标定 |
| [[api/PlaybackAlgorithm]] | PlaybackAlgorithm — 监控相机回放算法（算法层 | #监控相机 #回放 #算法层 #EmguALG |
| [[api/PointCloudViewer]] | PointCloudViewer API 参考 | #3D #渲染 #HelixToolkit #点云 |
| [[api/ProcessControlPage]] | ProcessControlPage 工艺设置页（原 ParamConfigPage | #UI #工艺设置 #工艺调试快捷设定 #线激光标定 |
| [[api/ProductFileRecordManager]] | ProductFileRecordManager API 参考（产品文件记录管理器 · 模块唯一对外访问口 | #产品文件 #记录 #管理器 #单例 |
| [[api/S7NetPlus]] | S7NetPlus / S7.Net 使用笔记 | #PLC #西门子 #S7 #通讯 |
| [[api/SQLiteDatabaseManager]] | SQLiteDatabaseManager API 参考（SQLite 数据库管理器 · 模块唯一入口 | #数据库 #SQLite #管理器 #单例 |
| [[api/SeamMapTrackingAlgorithm]] | API — SeamMapTrackingAlgorithm 焊缝目标地图算法（前置量对齐 + 测量时刻轴值基准 | #线激光 #Y轴 #CSP #焊缝跟踪 |
| [[api/SeamTrackingAlgorithm]] | API — SeamTrackingAlgorithm 线激光焊缝几何轨迹跟踪算法 | #线激光 #Y轴 #PVT #焊缝跟踪 |
| [[api/SimulationConfig]] | SimulationConfig 模拟参数配置 API | #模拟测试 #配置 #MainDeviceControl |
| [[api/SystemControlPage]] | SystemControlPage 系统设置页（原 MotionControlPage | #UI #系统设置 #运控 #参数页 |
| [[api/VirtualCam]] | VirtualCam API 参考（虚拟调试相机 | #相机 #虚拟 #模拟 #ADR-003 |
| [[api/WeldParamAdjustmentAlgorithm]] | API — WeldParamAdjustmentAlgorithm 焊缝宽度驱动的参数调整算法 | #焊接 #参数调整 #焊缝宽度 #查表 |
| [[api/WeldParamControlWorkflow]] | WeldParamControlWorkflow API 参考（焊接工艺控制流程 · 三态模型 | #工作流 #焊接 #工艺 #功率 |
| [[api/WeldParamManager]] | WeldParamManager API 参考（焊接参数管理器 · 模块唯一入口 | #焊接 #参数 #算法 #管理器 |

## 四、规范标准

| 页面 | 摘要 | 标签 |
|---|---|---|
| [[standards/CodeSimplification-RefFileOrganization]] | 文件书写整理规则 |  |
| [[standards/CodeSimplification-RefFunctionSimplification]] | 函数精简规则 |  |
| [[standards/CodeSimplification-RefLogicSimplification]] | 代码逻辑精简规则 |  |
| [[standards/CodeSimplification-ReviewWorkflow]] | C# Vibecoding 代码审查 |  |
| [[standards/CodeSimplification-Tooling]] | CodeSimplification-Tooling 代码精简固定工具集 | #代码精简 #工具 #检查脚本 #批改脚本 |
| [[standards/CodeSimplification]] | 代码精简规范（精简代码区域 · 详尽版 | #代码精简 #注释规范 #日志规范 #重构 |
| [[standards/DeviceInitializationDependency]] | 设备初始化依赖层级与刷新门禁标准 | #设备初始化 #依赖层级 #三态 #自动刷新 |
| [[standards/InitializationLogSpec]] | 初始化日志规格（四段式 · 模组命名 · 阶段分离 | #日志 #初始化 #模组 #阶段分离 |
| [[standards/MessageLogResponsibility]] | 提示与日志职责分离（弹窗只报结果 · BUG 归 LOG | #标准 #UI #日志 #提示 |
| [[standards/ModuleOrganizationPattern]] | 模块组织范式标准（Core · 抽象层 · 实现层 · Manager | #模块组织 #分层架构 #抽象层 #实现层 |
| [[standards/UiStateSimplification]] | UI 状态判断与控制精简规范 | #UI #代码精简 #状态管理 #真相源 |
| [[standards/WikiPageFormatSpec]] | Wiki 页面格式规范（强制）—— 各页类别的结构定义、字段契约与增长规则 | #格式 #结构化 #自动化 #脚本化 |
| [[standards/WorkflowResponsibilityBoundary]] | 流程与模组对象权责边界标准 | #权责边界 #工作流 #模组 #事件 |

## 五、历史教训

| 页面 | 摘要 | 标签 |
|---|---|---|
| [[lessons/AlgorithmControlRecordIsolation]] | 算法纯净性与记录职责隔离 | #算法分层 #记录隔离 #事件驱动 #配置合一 |
| [[lessons/AntdUI-Modal-Config-Overload-Cascade]] | AntdUI Modal.Config 第三参数未定义 → 级联误报"Form 无法转换为 Target" | #UI #AntdUI #Modal #编译错误 |
| [[lessons/AntdUI-Modal-Content-Disposed-Before-Commit]] | AntdUI Modal 内容控件在 open 返回前已被销毁 → 弹窗内改的参数不生效、再开复原 |  |
| [[lessons/CSharp-Language-Pitfalls]] | C# 语言与编译常见陷阱汇总 | #C# #编译错误 #汇总 |
| [[lessons/CodeSimplification-Scope-DesignerOnly]] | 代码精简范围裁定：强制排除仅 Designer.cs | #代码精简 #范围 #Designer.cs #UIDesign |
| [[lessons/CommentMetadataCleanup]] | 注释元信息清零：内容判据补齐 + 精确整行批改 |  |
| [[lessons/CommentSimplificationBatchPitfalls]] | 批量注释/逻辑精简的三个坑 | #代码精简 #注释 #BOM #XML注释 |
| [[lessons/CommentStripToolchain]] | 全库注释瘦身工具链的四个坑 | #注释 #批量改造 #行尾 #BOM |
| [[lessons/ConfigFileSplitByTabPage]] | 配置文件按 TabPage 拆分的迁移与隔离判据 | #配置 #拆分 #TabPage #INI |
| [[lessons/ConfigHealDirectionOrdering]] | 配置自愈补出的默认值不是现场值：方向键必须后补 | #配置 #迁移 #幂等 |
| [[lessons/ConfigKeyRemovalAndTruthSourceMigration]] | 配置键删除与真相源迁移的连带门禁 | #配置 #真相源 #删除配置项 #镜像同步 |
| [[lessons/ConfigOwnershipByManager]] | 配置所有权归 Manager 与跨页写入粒度 | #配置 #Manager #写入粒度 #键级写入 |
| [[lessons/ConfigZoneSaveWiring]] | "配置分区落盘接线：改了不生效 / 保存了没落盘 / 落到了别人的区" | #配置架构 #分区落盘 #AlgorithmsZone #接线完整性 |
| [[lessons/DocDemoDllLookupOrder]] | 控件与 SDK 用法参考顺序：文档 → demo → DLL | #AntdUI #英莱 #监控相机 #demo |
| [[lessons/FaultRecoveryDeviceKey]] | Lesson - 故障恢复设备键名必须与策略注册 key 精确匹配 | #陷阱 #Safety #故障恢复 #状态机 |
| [[lessons/FormatDrivenPacketParsingPitfalls]] | 格式驱动收发的运行时陷阱：文本节点误判 / 节存在≠契约正确 / 回复盲发 | #lessons #RSI #格式驱动 #XML |
| [[lessons/GitHubSyncPitfalls]] | GitHub 云端同步陷阱（AdaWeldSystem / LLMWiki |  |
| [[lessons/HomeStatusAuthorityPitfall]] | 拿位置硬门覆盖驱动器回零完成信号的现场坑 | #运控 #回零 #台达 |
| [[lessons/IntelligentLaser-Callback-Mechanism]] | IntelligentLaser-Callback-Mechanism | #相机 #英莱 #IntelligentLaser #汇总 |
| [[lessons/IntelligentLaser-Delegate-Gc]] | IntelligentLaser-Delegate-Gc | #相机 #英莱 #IntelligentLaser #汇总 |
| [[lessons/IntelligentLaser-Job-System]] | IntelligentLaser-Job-System | #相机 #英莱 #IntelligentLaser #汇总 |
| [[lessons/IntelligentLaser-Pitfalls]] | 英莱（IntelligentLaser）相机开发教训汇总 | #相机 #英莱 #IntelligentLaser #汇总 |
| [[lessons/IntelligentLaser-Sdk-Interop]] | IntelligentLaser-Sdk-Interop | #相机 #英莱 #IntelligentLaser #汇总 |
| [[lessons/IntelligentLaser-Ui-State]] | IntelligentLaser-Ui-State | #相机 #英莱 #IntelligentLaser #汇总 |
| [[lessons/JudgementDimensionGap]] | 判据维度缺失：查「存在性」不等于查「唯一性」 | #lessons #判据 #静态校验 #幂等 |
| [[lessons/JudgementThresholdScaleMismatch]] | 判据阈值与信号尺度失配 — 四类「改对了却没生效/生效了却更糟」的坑 | #阈值 #尺度失配 #自锁 #配置覆盖 |
| [[lessons/LargeUserControlSplitPitfalls]] | 大类 UserControl 拆分的两类编译坑 | #UI #页面拆分 #Designer #编译错误 |
| [[lessons/MecaVision-NativeDllLoadNRE]] | 麦格威 MVSDK 原生 DLL 未部署导致 NullReferenceException | #麦格威 #MecaVision #MVSDK #DLL部署 |
| [[lessons/MigrationCompletenessAudit]] | 跨页迁移的完整性核查与编译结论时效性 | #迁移 #完整性核查 #控件 #编译 |
| [[lessons/NodeAddressCollision]] | 节点号撞号：配置声明的设备不在总线上，握手打到他人节点 |  |
| [[lessons/ProtocolDirectionalConstraints]] | 协议方向性硬约束：RSI 的 SEND 段禁 STRING，写入关键词不可上行 | #lessons #协议 #RSI #KUKA |
| [[lessons/PythonEditByteSafety]] | Python 脚本改 .cs 的字节安全三坑 | #工具坑 #Python #字节安全 #BOM |
| [[lessons/RefactorPostChecklist]] | 大动作收归后的四项核查清单 | #重构 #收归 #核查 #死代码 |
| [[lessons/RepomapCSharpCallEdgeGap]] | repomap 官方 C# 解析器缺口（只收 public 方法 · 零方法调用点）与补齐方式 | #代码地图 #repomap #tree-sitter #C# |
| [[lessons/ScottPlotSignalXyMonotonicPitfall]] | ScottPlot SignalXY 的 X 单调约束与显示层回退剔除 | #UI #ScottPlot #SignalXY #单调 |
| [[lessons/SignatureAndWiringConsistency]] | "签名-调用点一致性（改签名必查调用点，否则「全绿却编译不过」）" | #编译错误 #签名 #调用点 #静态校验 |
| [[lessons/SimulationAutoBranching]] | 模拟测试按设备连接态自动分支（取消模式选择 | #模拟 #线激光 #运控 #工作流 |
| [[lessons/StartupInitializationOrderGates]] | 启动初始化时序门禁：静态构造重入日志 / 界面未就绪开硬件 / UI 回调未判句柄 | #lessons #启动 #初始化 #静态构造 |
| [[lessons/StaticCheckSemanticBlindSpots]] | 静态校验的两类编译级盲区 — 可空引用类型与标识符定义域 | #静态校验 #编译错误 #C#7.3 #可空引用类型 |
| [[lessons/StaticVerifier-AdrNumbering]] | StaticVerifier-AdrNumbering | #静态校验 #编译错误 #Step2.6 #判据库 |
| [[lessons/StaticVerifier-Batch-Script-Traps]] | StaticVerifier-Batch-Script-Traps | #静态校验 #编译错误 #Step2.6 #判据库 |
| [[lessons/StaticVerifier-CSharp-Scoping]] | StaticVerifier-CSharp-Scoping | #静态校验 #编译错误 #Step2.6 #判据库 |
| [[lessons/StaticVerifier-Checker-FailureModes]] | StaticVerifier-Checker-FailureModes | #静态校验 #编译错误 #Step2.6 #判据库 |
| [[lessons/StaticVerifier-RecentJudgements]] | StaticVerifier-RecentJudgements | #静态校验 #编译错误 #Step2.6 #判据库 |
| [[lessons/StaticVerifier-Tooling-Substitutes]] | StaticVerifier-Tooling-Substitutes | #静态校验 #编译错误 #Step2.6 #判据库 |
| [[lessons/StaticVerifier-Wiring-Integrity]] | StaticVerifier-Wiring-Integrity | #静态校验 #编译错误 #Step2.6 #判据库 |
| [[lessons/StaticVerifierJudgements]] | 静态校验判据库（Step 2.6 的判据全文 · 编码错误教训沉淀 | #静态校验 #编译错误 #Step2.6 #判据库 |
| [[lessons/StepDriven-DeviceControl-Lessons]] | StepDriven-DeviceControl-Lessons | #步骤驱动 #执行步 #DeviceWorkflowBase #并发 |
| [[lessons/StepDriven-SixPitfalls]] | StepDriven-SixPitfalls | #步骤驱动 #执行步 #DeviceWorkflowBase #并发 |
| [[lessons/StepDrivenWorkflowPitfalls]] | 设备控制与步骤驱动教训汇总 | #步骤驱动 #执行步 #DeviceWorkflowBase #并发 |
| [[lessons/TaCstEntryRampAndResidualMotion]] | TA 力矩冷启动不走斜坡与位置转力矩先反跑 |  |
| [[lessons/TaSharedTorqueLimit]] | 扭矩上限不是「越小越丝滑」——CSP/CST 共用一个值 |  |
| [[lessons/TorqueActionNoPositionEndpoint]] | 力矩类指令不要自造位置终点判据 | #TA #力矩 #CST #位置判据 |
| [[lessons/TorqueModeAsUiGate]] | UI 开关兼任可用性门禁会导致操作后不可恢复 | #UI门控 #Radio #Fill |
| [[lessons/UiButtonZoneBoundary]] | UI 读改存按钮的分区边界与零调用甄别 | #UI #分区 #TabPage #零调用 |
| [[lessons/UiLayoutChangeSyncPitfalls]] | UI 布局改版的同步与所有权门禁 | #UI #Designer #事件订阅 #跨线程 |
| [[lessons/UiModuleRemovalCleanup]] | UI 功能模块删除的连带清理门禁 | #UI #Designer #模块删除 #控件清理 |
| [[lessons/UiRefreshUnifiedEntry]] | UI 状态刷新统一入口 | #UI #状态刷新 #代码精简 #重构 |
| [[lessons/WikiDriftCorrectionPitfalls]] | Wiki 批量漂移修正十一坑 | #LLMWiki #漂移 #工具脚本 #Python |
| [[lessons/WikiGovernanceBatchingPitfalls]] | 批量治理与脚本化改写的事故清单（ADR 重编 / 页面瘦身 / 格式规范化 | #批量改写 #脚本化 #编号重编 #行尾 |

## 六、操作指导

| 页面 | 摘要 | 标签 |
|---|---|---|
| [[guides/AntdUI-Reference]] | AntdUI 完整开发参考 | #UI #AntdUI #参考手册 #汇总 |
| [[guides/Config-Data-Tools]] | 配置与数据工具使用指南 | #工具 #配置 #数据库 #汇总 |
| [[guides/DeltaEtherCAT-AdvancedMotion]] | 台达 EtherCAT 高级运动（PVT / 电子凸轮）使用规范 | #指南 #运控 #台达 #EtherCAT |
| [[guides/DeltaEtherCAT-Deployment]] | 台达 EtherCAT 部署规范（驱动 · 原生库 · 项目内落地 | #指南 #运控 #台达 #EtherCAT |
| [[guides/DeltaEtherCAT-DevGuide]] | 台达 EtherCAT 运动控制模块落地规范 | #运控 #台达 #EtherCAT #雷赛基线 |
| [[guides/DeltaEtherCAT-UIDesign]] | 台达 EtherCAT UI 设计规范（AntdUI 版 | #指南 #运控 #台达 #UI |
| [[guides/ExecutionEnvironment]] | 执行环境事实（Windows + PowerShell + Python + Git）—— 每次动手前必读 | #环境 #工具链 #Python #PowerShell |
| [[guides/MecaVision-DevGuide]] | MecaVision 监控相机开发指导 | #相机 #监控相机 #MecaVision #MVSDK |
| [[guides/Namespace-Compilation]] | 命名空间与编译错误综合指南 | #编译错误 #命名空间 #汇总 |
| [[guides/Project-Tools]] | 项目工具、规范与常见问题汇总 | #工具 #模拟 #汇总 |
| [[guides/RawAssetCatalog]] | 原始资产检索表（raw/）—— 编写前必查的官方文档与 demo 入口 | #原始资料 #官方文档 #demo #检索表 |
| [[guides/SourceBackup-GitHub]] | AdaWeldSystem / LLMWiki 云端源码备份（GitHub）操作手册 |  |
| [[guides/WinForms-Designer]] | WinForms 设计器开发规范与常见错误 | #UI #WinForms #设计器 #汇总 |
| [[guides/WinForms-UI-Threading]] | WinForms UI 线程安全与初始化指南 | #UI #线程安全 #初始化 #汇总 |

## 七、设计决策

> **全量登记表唯一权威 = [[decisions/ADR-Index]]**（001~114 连续无断号，含每条的主题/状态/日期；7 个旧号已并入他页，以指针行留档）。本页不重复该表。
> 新增决策前先跑 `tools/adr_new.py check <关键词>`——命中同主题则**合并**进既有页，不新建页；`check` 会按**落地实体符号 Jaccard** 判疑似重复（≥0.40 即拦截新建），命中即走 `adr_new.py merge`（规则见 [[standards/WikiPageFormatSpec]] §三）。

## 八、历史归档（现归 project/）

> 项目级过程台账、审计报告与进度快照；**不作为编码约束**，追溯用。
> ⛔ 与 §一「项目总览」**互斥**：每个 project 页只出现在其中一节（归属规则见生成器 `ARCHIVE_PROJECT`）。

| 页面 | 摘要 | 标签 |
|---|---|---|
| [[project/AdrConsistencyAudit-20261008]] | ADR 一致性审计— 全库 ADR 及其引用处的逻辑缺陷与历史遗留 | #审计 #编号体系 #一致性 #历史遗留 |
| [[project/CodeSimplification-Backlog-20261026]] | CodeSimplification-Backlog 代码精简待完成事项台账 | #台账 #代码精简 #待办 #判据 |
| [[project/CodeSimplification-Progress-20260826]] | 代码精简修复进度表（新版标准 |  |
| [[project/RequirementsCoverage]] | 需求覆盖与实现状态（AdaWeldSystem |  |
| [[project/ReviewOptimization-P1-StructureDesign]] | P1 结构设计定稿 — 第一次评审优化（五份产物 | #结构设计 #冻结点 #第一次评审 #硬件归属 |

## 九、专员职责

| 页面 | 摘要 | 标签 |
|---|---|---|
| [[people/3DSpecialist]] | 3D开发专员 | #专员 #3D #HelixToolkit |
| [[people/Architect]] | 架构开发员 | #专员 #架构 |
| [[people/CameraSpecialist]] | 工业相机开发专员 | #专员 #相机 |
| [[people/DatabaseSpecialist]] | 数据库开发专员 | #专员 #数据库 #SQLite |
| [[people/GeneralTechSpecialist]] | 通用技术开发专员 | #专员 #通用技术 #通讯 #状态机 |
| [[people/ImageAlgorithmSpecialist]] | 图像算法开发专员 | #专员 #图像算法 #EmguCV |
| [[people/MotionControlSpecialist]] | 运动控制开发专员 | #专员 #运动控制 #台达 |
| [[people/QASpecialist]] | QA/测试专员 | #专员 #QA #测试 |
| [[people/UISpecialist]] | UI 开发专员 | #专员 #UI #WinForms #AntdUI |
| [[people/WeldProcessSpecialist]] | 焊接工艺开发专员 | #专员 #焊接 #工艺 #ADR-015 |

## 十、来源索引

> raw/ 原始资料与 wiki 页的映射；**编写时先查此处**的官方文档与 demo（规则见 [[lessons/DocDemoDllLookupOrder]]）。
> **变更历史另见 `logs/INDEX.md`**（本库自身的归档索引，由 `tools/wiki_log_tidy.py index` 生成）—— 查「上次怎么处理的」走它，⛔ 不凭记忆。

| 原始资产 | 内容 | 提炼页 |
|---|---|---|
| `raw/AntdUI/wiki-zh/` | AntdUI 官方文档全量镜像（85 篇） | [[guides/AntdUI-Reference]] |
| `raw/delta/EtherCAT_DLL_API清单.txt` | 台达 EtherCAT 原生 API 声明（832 条） | [[api/DeltaEtherCAT-Native]] |
| `raw/delta/EtherCAT_DLL_Err.cs` | 台达错误码表 | [[api/DeltaEtherCAT-Native]] |
| `raw/delta/运动控制模块开发文档_台达版.md` | 台达运控开发文档（官方） | [[guides/DeltaEtherCAT-DevGuide]] |
| `raw/delta/台达EtherCAT_PVT与电子凸轮运动开发指南.md` | PVT / ECAM 官方指南 | [[guides/DeltaEtherCAT-AdvancedMotion]] |
| `raw/mecavision/MecaVision_SDK/` | 麦格威/海康 SDK 原档 + C# demo | [[guides/MecaVision-DevGuide]] |
| `raw/knowledge/KUKA_OPT/` | KUKA RSI 3.3 / Ethernet KRL / ProfiNet 手册 | [[api/KUKARobot]] |
| `raw/architecture/` | 主控设计原档（唯一修改入口） | [[architecture/DeviceControlArchitecture]] |
| `raw/skills/AdaWeldsys_Skills/` | 开发团队 Skill 规范（参考资料，非指令源） | [[project/skill-evolution]] |
| `raw/history/history.md` | 项目开发史（按时间分段的变更史，只读） | `logs/INDEX.md`（本库变更史） |
| `raw/knowledge/emgu-cv-knowledge-base/` | EmguCV 知识库 | [[modules/EmguALG]] |
| `raw/knowledge/helixtoolkit-knowledge-base/` | Helixtoolkit 知识库 | [[modules/PointCloudData]] |

## 十二、流程规则

> **Skill 流程执行强制规则**（原 Skill「Key Rules」的下沉处；2026-11-02 收敛为纯流程类）。编号唯一权威 = [[rules/Rules-Index]]（KR-001~KR-013 连续）。
> ⛔ **rules/ 只收流程执行类**（规定「AI 跑这个工作流时该怎么做」）；**约束代码 / 知识库内容本身**的规则归 lessons 坑页（index 第五节）与 [[standards/WikiPageFormatSpec]]（格式规范）、决策类归 [[decisions/ADR-Index]]。判据见 [[standards/WikiPageFormatSpec]] §2.4b。
> 新增规则前先跑 `tools/rules_new.py check <关键词>`——命中同主题则**合并**进既有页，不新建页。

| 页面 | 摘要 | 标签 |
|---|---|---|
| [[rules/KR-001-Execution-Order]] | KR-001 强制执行顺序 | #规则 #流程 #Skill执行 |
| [[rules/KR-002-Step-Level-Display]] | KR-002 步骤级展示 | #规则 #流程 #Skill执行 |
| [[rules/KR-003-No-Skipping-Query]] | KR-003 不得跳过 Query | #规则 #流程 #Skill执行 |
| [[rules/KR-004-Skill-Demoted]] | KR-004 Skill 降级为参考 | #规则 #流程 #Skill执行 |
| [[rules/KR-005-Adr-Lessons-Gates]] | KR-005 ADR 与教训是编码前门禁 | #规则 #流程 #Skill执行 |
| [[rules/KR-006-Ingest-Mandatory]] | KR-006 Ingest 强制 | #规则 #流程 #Skill执行 |
| [[rules/KR-007-New-Decisions-Recorded]] | KR-007 新决策必须记录 | #规则 #流程 #Skill执行 |
| [[rules/KR-008-Timestamp-Rule]] | KR-008 时间戳取用 | #规则 #流程 #Skill执行 #日志 |
| [[rules/KR-009-Grep-Default]] | KR-009 Grep 是默认定位法 | #规则 #流程 #Skill执行 |
| [[rules/KR-010-No-Compiler-Honesty]] | KR-010 编译结论必须以真编译为准 | #规则 #流程 #Skill执行 |
| [[rules/KR-011-Backup-Output-Timing]] | KR-011 backup 与 output 时机 | #规则 #流程 #Skill执行 |
| [[rules/KR-012-Skill-Dual-Copy]] | KR-012 Skill 双副本同步 | #规则 #流程 #Skill执行 |
| [[rules/KR-013-Skill-Pointer-Discipline]] | KR-013 Skill 指向不得写死内容页 | #规则 #流程 #Skill执行 |

## 维护说明

| 工具 | 用途 |
|---|---|
| `tools/wiki_format.py` | **格式校验器**（WikiPageFormatSpec 的机械判据，Phase 4 必跑） |
| `tools/wiki_index_build.py` | **index.md 重建**（本文件由它生成） |
| `tools/wiki_log.py` | log 条目写入 + **log 截断唯一入口**（truncate → 按日归档 + 重建 INDEX.md） |
| `tools/adr_new.py` | ADR 合并检查 / 演进记录追加 / 新号分配 |
| `tools/lesson_new.py` | 教训合并检查 / 追加条目 / 三处计数同步 |
| `tools/rules_new.py` | 流程规则合并检查 / 演进记录追加 / 新号分配 / 索引登记 |
| `tools/rules_check.py` | **流程规则页校验**（编号连续 / 结构契约 / 索引一致 / 判据非空） |
| `tools/skill_pointer_check.py` | **Skill 指向防漂移闸门**（⛔ 不得写死内容页名） |
| `tools/wiki_audit.py` | 11 项体检：红链 / 孤儿 / 索引重复 / ADR 空洞 / 体积 / 重复度 / 错放 / 入链 / 子目录 / 过小分类 / lessons 三处一致 |
| `tools/lint_scan.py` | 死链 / 孤儿 / ADR 编号冲突 / 外链失效 |
| `tools/drift_scan_precise.py` | wiki 引用的 .cs 是否仍存在 |
| `tools/ingest_purity_scan.py` | 沉淀纯度：禁验证叙事 / 日期沿革 / 日志体回灌 |

**执行方式**：在 `Vicoding管理平台/LLMWiki/` 下运行 `python tools/<script>.py`。

**健康判据**：红链 0 · 孤儿 0 · 索引重复行 0 · 二级子目录 0 · 过小分类 0 · lessons 三处一致 · drift 待修正 0 · 纯度违规 0 · **格式违规 0**。
