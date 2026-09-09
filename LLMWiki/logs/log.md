## [2026-09-09 16:35:51] ingest+governance | 全库知识治理：判废 4 ADR + 重排 001~038 + 合并重复页 + 精简文档 + 废料清理

**来源**：用户指令「对知识库做全库知识检查，合并重复项，删除废除项，精简文档，整理序号」（/vibeCoding 全流程）。

**前置**：两仓库先提交上次会话遗留改动（AdaWeldSystem 441ba86 / Vicoding b885f31），LLMWiki 备份 LLMWiki_backup_20260909_154700.tar.gz（64MB 含 raw）。

**操作**：
1. 判废删除 4 项整页失效 ADR：原 003 单算法文件（被 ADR-042 三层改造推翻）、原 004 Step 状态机（步驱动机制 09-03 清除）、原 016 CameraSelector 上提（载体已删）、原 026 英莱数据流（CamRun 已删 + 显示范式被推翻）；去向登记于 ADR-Index 删除对照表。
2. 全库重排 ADR 001~042 → 001~038 连续：38 文件改名 + slug 权威映射改写（wiki 45 页 + logs 239 处 + skills 两副本 + 代码注释 27 文件 44 处）；previous_id 字段全部移除（两代重排后歧义）；wiki 老散文中的裸编号按项目既有容忍口径未盲改，以 ADR-Index 为换算准绳。
3. ADR-Index.md 重建：09-09 重排映射 + 09-07 历史映射 + 两段删除对照（共 7 项）+ 全部 38 条现行编号总表。
4. index.md 大修：头部更新至 2026-09-09、目录计数修正（模块 16 / API 35 / lessons 19 / guides 12 / ADR 38）、§7 重整（ADR-037/038 入 7.1，OPEN-ClearAlarmSemantics 标注已由 ADR-030 裁定关闭，7.3 补删除说明）、路由表/模块行/API 行约 110 处裸编号对齐现行编号。
5. 合并重复：modules/VirtualCam（含 33ms 模拟节拍要点）并入 api/VirtualCam，全库 8 处改链；Config-Data-Tools 重复条目经评估保留（指针型引用，无整段重复）。
6. 判废标注：Tier-2 沿革横幅 ×4（ADR-007/010/013/021）；ADR-008/011 frontmatter 改 superseded（部分）；lessons Tier-3 ⛔ 机制失效标注 ×2（SimulationC-Mode-Interruption / StateMachine-DoubleTransition，思想保留）。
7. 精简：guides/Project-Tools §1 已废弃代码图谱章节 247 行压缩为 7 行墓碑（991→751 行），原始内容随 git 历史留存。
8. 废料清理：_trash_20260908（5 墓碑）与根部空 LLMWiki/ 目录骨架删除（内容 git 历史 + 备份包双留存）。
9. 事故记录：重排脚本首版 slug+裸编号两段式替换产生双重映射（ADR-005-Callback → 003 → 裸映射 038），靠 git checkout 基线回滚后改单遍联合正则重放；教训：编号映射必须单遍 re.sub 回调一次成型，禁止顺序多趟。

**新增 Wiki 页面**：无
**删除 Wiki 页面**：decisions/ADR-003-SingleAlgorithmFile、decisions/ADR-004-WorkflowStepEnum、decisions/ADR-016-CameraSelectorUnifiedToApi、decisions/ADR-026-YinglaiDataFlow、modules/VirtualCam（并入 api/VirtualCam）
**更新 Wiki 页面**：index/index、decisions/ADR-Index（重建）+ 全部 38 ADR（改名/改链/横幅）+ 约 45 页 slug 改链 + guides/Project-Tools（§1 墓碑）+ lessons 2 页标注 + wiki 全库裸编号对齐
**代码文件**：27 个 .cs 注释内 ADR 编号同步新编号（无逻辑改动，真编译待 VS）
**矛盾检测**：无（ADR-Index 为编号唯一准绳；历史日志原文按项目惯例未改写，检索靠映射表换算）
**健康检查**：wiki_audit 红链 0 / 孤儿 0 / 索引重复 0 / 编号 1~38 连续 / 内容重复 0；lint_scan 四项 0；drift_scan 待修正 0。

---

## [2026-09-09 14:05:40] coding | 修复 MvApi.CameraSdkInit NullReferenceException：MVSDK 原生 DLL 未部署到输出目录

**来源**：用户 VS 运行报 `MvApi.CameraSdkInit(0)` NullReferenceException。

**根因**：`MVSDK.cs` 无 DllImport，`MvApi.CameraSdkInit` 是 static 委托字段，由静态构造 `LoadLibrary("MVCAMSDK_X64.dll")` + `GetProcAddress` 填充；LoadLibrary 失败不抛异常静默返回 IntPtr.Zero，全部委托为 null。DLL 已落 `3rdDepend/MecaVision/` 但 csproj `CopyNative3rdDependToOutput` 漏列 → 输出目录无 DLL → 首次调用即 NRE。

**修复**：① csproj 拷贝清单补 4 文件（MVCAMSDK_X64.dll / MVImageProcess_X64.DLL / GiGeCamera_X64.Interface / Usb3Camera0_X64.Interface）；② MVSDK.cs 静态构造加 2 道守卫（hSdkDll==Zero → DllNotFoundException；CameraSdkInit==null → EntryPointNotFoundException，防误部署例程 bin 旧互操作组件）；③ MecaVisionCam.Connect catch 日志改取内层异常（TypeInitializationException 包装致外层 Message 无诊断价值）。

**校验**：Python 静态校验 11/11 PASS（守卫 4 要素 / 花括号平衡 / 内层异常日志 / csproj 4 项 / MvApi 消费方仅 MecaVisionCam）；**真编译待 Visual Studio**。备份 `AdaWeldSystem_backup_20260909_135845.tar.gz`。

**知识沉淀**：新增 `lessons/MecaVision-NativeDllLoadNRE`；更新 `guides/MecaVision-DevGuide` §2.4 部署增补；index.md 教训表 +1（16→17）。

---

## [2026-09-09 13:42:19] coding | 真编译修复：算子枚举漏迁（EmguALG）+ CS0118 命名空间/类名同形（MonitorCam）

**来源**：用户 VS 编译报 4 个错误——`MorphologyOperation`/`FilterOperation`/`FeatureExtractionOperation`（编译器顺序截断，实际含 `EdgeDetectionOperation` 共 4 枚举）找不到 + `MecaVisionCam` 命名空间被当类型使用。

**根因 1（枚举漏迁）**：4 个算子枚举原定义在已删的 `EmguConfiger/AlgorithmManager.cs`（PipelineManager 文件）命名空间级，ADR-038 删文件时未清单化迁移；Python 静态校验按符号点查抓不住「类型定义整体丢失」。修复：恢复至新文件 `EmguALG/Core/AlgorithmOperations.cs`（命名空间 `AdaWeldSystem.EmguALG`——Stages 与 Core/* 直接可见，零 using 变更，ADR-017 单一定义点），csproj 注册。
**根因 2（CS0118）**：实现层命名空间 `AdaWeldSystem.MonitorCam.MecaVisionCam` 与类名同形，`MonitorCamManager:154` 裸名 `new MecaVisionCam()` 被解析为子命名空间。修复：`new MecaVisionCam.MecaVisionCam()`（线激光 `new IntelligentLaserCam.IntelligentLaserCam()` 先例同构写法）。

**校验**：git 基线差集法（HEAD 有定义、现役无定义的 54 类型逐一查引用）——仅 `ConnectionState`/`PointCloud` 两项命中且均为成员名误报（非类型引用），已删类型零类型位残留。

**教训（记入 ADR-038 补注 + modules/MonitorCam 规约）**：① 删除代码文件前必须清单化其全部命名空间级类型（class/enum/struct/delegate）逐一迁移或确认消亡，枚举最易漏；② 命名空间与类名同形时实例化必须「命名空间.类名」限定。

---
## [2026-09-09 11:40:05] doc | 工艺控制模块（WeldParamControl）数据流与处理逻辑可视化 HTML

**来源**：用户 @skill:vibecoding-llmwiki 要求「将工艺控制模块设计一版 Html，能直观看到数据结构和数据流向、处理逻辑」。

**产出**：`AdaWeldSystem_工艺控制模块_数据流与处理逻辑.html`（workspace 根，自包含单文件，Ant 蓝浅色风格与既有流程图 HTML 一致）。8 个章节：①模块地图（三命名空间五文件）②数据结构（AutoParam/WeldParamOutput/RobotWeldData/SeamCalData/ChartVar 字段级）③数据流向全景 ④AutoAction 自适应决策分支图 ⑤RunStep 步控 0/10/20/800/900 + 相位映射 ⑥持久化装配（INI/Config.db/AutoParamValue.db/XML）⑦ADR 硬约束 + OPEN 清单 ⑧源码定位速查表（精确到 文件:行号）。

**核验亮点**：以源码为准（引用精确到行号），纠正 wiki 旧链路（PipelineManager→OnAlgorithmCompleted 已随 ADR-035/042 删除，现行触发=LineLaserManager.ResultReady→ManagerResultReady）；**发现 6 项 OPEN 现状断点**——①RobotWeldData.PosX 无写入者（真机 X 恒 0）②_lastRobotX 无赋值点 ③SeamCalData.AddSeamWidth 全库无调用方（AutoAction 恒走基准分支，突变触发/查表更新不生效）④CalcGalvoAmplitude TODO 恒 0 ⑤MainPage 曲线喂入源待复核 ⑥ConsecutiveFailureCount 递增点待确认。未改任何 C# / wiki 页面（纯文档交付，无备份与 .csproj 需求）。

---
## [2026-09-08 21:14:21] code+wiki | MonitorCam 三层重构 + 切换麦格威（ADR-037 accepted）+ EmguALG 三层改造（ADR-038）——Phase 2 编码落地

**来源**：用户要求按既定 PLAN 执行 Phase 2 编码（MonitorCam 层级改为 IMonitorCam / MecaVisionCam / MonitorCamManager 参照 MotionControl；EmguALG 算法改造方案一并实施）。

**Stage A：MonitorCam 三层重构（ADR-037 proposed → accepted）**
- 新建 `MonitorCam/IMonitorCam/`（MonitorCamType / MonitorCamEventArgs / IMonitorCamApi）+ `MonitorCam/MecaVisionCam/`（MecaVisionCam 实现 + Native/MVSDK.cs 官方 6885 行原样拷入）+ `MonitorCam/MonitorCamManager.cs`（原 MonitorCameraRun 改名承接，Lazy 单例业务中枢）。
- 实现：Live=`SetCallbackFunction`+`Play`（回调 Clone Mat 后 `FrameReceived` 上行）；PIL=`GetImageBuffer`+`ImageProcess`+`Release`；断联回调→普通 Alarm（非急停）。
- 删除 `Api/HikvisionCameraApi.cs`（280 行）+ `Api/IMonitorCameraApi.cs`（迁走）+ `MonitorCameraRun.cs`；csproj 移除 `MvCameraControl.Net` 引用；原生 DLL 部署 `3rdDepend/MecaVision/`（x64：MVCAMSDK_X64/MVImageProcess_X64/两份 .Interface）。
- 消费方改写：`MonitorCameraWorkflow`（~15 处）+ `MonitorCamPage` + `FormMain`（sed 批量改名 + using 更新）。

**Stage B：EmguALG 三层改造（新 ADR-038 accepted）**
- 新建 `Abstractions/`（IAlgorithm / IConfigurableAlgorithm / IResultStore）+ `WireFeedDistance/` + `WeldQuality/`（算法类包装 ImageAlgorithm 第 8 区算子，强类型 Config/Result 从 ImageAlgorithm 外迁）+ `Manager/`（AlgorithmManager 统一调度 + AlgorithmResultStore 池化快照版本号 + AlgorithmCompletedEventArgs）。
- 删除：`EmguConfiger/AlgorithmManager.cs`（类名 PipelineManager）/ `JobManager.cs` / `AlgorithmJob.cs` / `Core/ProfileTransform.cs` / `SeamRecognition/` 整目录；`ImageAlgorithm` 中 PreWeldAlignment/WeldQuality 四类型外迁（改名 WireFeed*）；`AlgorithmBase` 点云 mm↔px 段删除。
- **焊缝特征上报链整删（用户裁定：焊缝特征由线激光直接获取）**：`LineLaserWorkflow` ReportExternalResult 上报段 + `WeldProcess` `_lastSeamFeature`/`_lastRobotX`/`OnAlgorithmCompleted` 订阅/`ComputeAndCacheHorizontalMove` 委派 + `MoveControlData.ComputeAndCacheHorizontalMove(SeamFeatureResult,...)` + 相关 using 全部清理。
- 保留裁决：`RealtimeMonitor/RealtimeMonitorAlgorithm.cs`（0 消费方，迁移源留档不删）、`Stages.cs`（PipelineConfig 供 ILAlgorithmEditForm 占位）。
- 消费方改写：`MonitorCameraWorkflow` 改调 `AlgorithmManager.DetectWireFeed/DetectWeldQuality`；`MonitorCamPage`/`FormMain` 配置面板对接新 Manager。

**校验**：Stage A 静态校验 14/14 通过；Stage B 校验通过（旧符号零残留/委托持引用防 GC/Dispose 规约）。**真编译待 Visual Studio**。

**Wiki 回灌**：ADR-037 修订为三层落地版（accepted）+ 新建 ADR-038；`modules/MonitorCam` 重写、`modules/EmguALG` 重写；新增 `api/MonitorCamManager`（继任 MonitorCameraRun 页）+ `api/AlgorithmManager`（继任 MonitorAlgorithmManager 页）；删除 `api/MonitorCameraRun` / `api/MonitorAlgorithmManager` / `api/HikvisionCameraSDK`（海康代码已删，按规范整页删除）；全库链接替换（12 文件）；index.md 更新 8 处；`guides/MecaVision-DevGuide` §3/§9 改落地实录；drift REMOVED 登记 10 个删除文件。

---
## [2026-09-08 18:17:24] wiki | 麦格威 MecaVision SDK 核验沉淀到知识库 + 监控相机切换实施 plan（ADR-037 proposed）

**来源**：用户提供 MecaVision SDK 包（`M4/7_MecaVision_SDK例程及说明文档.zip`）+ 两份二手指导文档（放入 `raw/knowledge/`），要求理解资料、沉淀知识库、形成代码实施 plan。

**核验（vendor-sdk-wiki-ingest 流程，脚本化）**：SDK 原档解压归档 `raw/mecavision/`（Demo×12 语言 / SDK+SDK/X64 原生 DLL / Document CHM / Drivers）。真相源 = `Demo/C#/MVSDK/MVSDK.cs`（**6885 行**，静态类 `MvApi`，**无 DllImport**——`IntPtr.Size==8` 动态加载 `MVCAMSDK_X64.dll`/`MVCAMSDK.dll`）。比对结果：二手文档 33 个 API 名 / 13 个错误码**数值** / 9 结构体 / 4 回调委托**全部与原文一致，零臆造**（区别于台达原档 6 个臆造名的教训）。⚠️ 例程 bin 的 `MVSDK.dll`（107KB, 2019）为旧版互操作组件，禁用。

**关键裁决**：二手文档按「另一项目」风格设计平行架构（新建 `MonitorCamera/` + `IVisionCamera` + `MonitorCameraManager` + `CameraFrameStore`），与 ADR-007 现状（`MonitorCam/` + `IMonitorCameraApi` + `MonitorCameraRun` + `MonitorCameraWorkflow`）冲突——**不照抄**，改为 `MecaVisionCameraApi` 实现现有契约，`MonitorCameraRun` 构造处切换，业务/UI 零改动；线程模型/帧缓存/踩坑结论保留复用。

**新增 Wiki 页面**：`api/MecaVisionMVSDK-Native`（33 API 速查 + 加载机制 + 错误码真值 + 核验配方）、`guides/MecaVision-DevGuide`（SDK 资产/工程配置/例程实录流程/**二手文档订正表 8 条**/契约适配映射/踩坑 11 条/**落地 9 步实施 plan**/OPEN 5 项）、`decisions/ADR-037-MecaVisionMonitorCamera`（**proposed，待用户确认 plan 后转 accepted**）。

**更新 Wiki 页面**：`modules/MonitorCam`（新增麦格威接入规划章节）、`index`（路由行 + MonitorCam 摘要 + API 行 + guides 行 + ADR-037 行 + 来源索引 2 行；⚠️ 同文件并行 Edit 再现互相覆盖/EBUSY，7 处分 3 轮串行补齐并逐项 Grep 核实）。

**未改代码**：本任务只做知识沉淀与 plan，Phase 2 编码待用户确认。

**OPEN**：① GigE IP 枚举期不可查（`tSdkCameraDevInfo` 无 IP 字段，init 后 `CameraGigeGetIp` 比对或改 SN 匹配）② 平台目标 x86/x64 待核对 ③ 连接形态 USB3/GigE 待确认 ④ PixelMmScale 标定联动 ⑤ 管理员权限 manifest 实测。

---


## [2026-09-08 17:34:03] code+wiki | 线激光三层职责二次分工：实现层只发回调、Manager 做业务、Y 轴只注入 IPVTMotion（ADR-035）

**起因（用户）**：①英莱实现层只做回调触发，不做业务处理——轮廓回调中触发「结果处理」与「轮廓处理」；②Manager 做业务：一个事件算 Y 轴 PVT 点下载，一个事件做 UI 显示 Mat / ScottPlot 最后帧（**可配置帧率与是否转换，先预留接口**）；③主页面 ScottPlot **线程轮询**取点，手动 UI 页订阅 Manager 的 Mat 更新事件；④问「Manager 需要持有 Y 轴吗？PVT 链路怎么走？需要就用依赖注入，不要整个台达控制器引用」。

**三项裁定**（AskUserQuestion）：校准数据**存英莱实现层**，Manager 生成 Mat 时读取；轮询接口用**池化快照 + 版本号**；PVT 走**B 套流式**。

**需求②判断结论**：Manager **需要**持有 Y 轴，但**只注入 `IPVTMotion`**（L2 能力抽象）。理由：PVT 下载只需 `BeginMove`/`ContinueMove`/`GetInformation` 三个入口；`MontionAxis : IPVTMotion` 的四入口是 `virtual` 默认实现，未实现轴返回 `PVTResult.NotSupported` 不抛异常、不连坐编译；注入 `MontionManager`（业务层）或 `DeltaMontionControl`（L3）违反 ADR-034「业务层只认抽象」。装配点 `MotionControlWorkflow.InitializeOn` 成功后 `AttachSeamTrackAxis()`（轴名取 `Config.SeamTrackAxisName`，默认「Y轴」）。

**代码改动**：新建 4 文件——`ILineLaser/LineLaserCalibration.cs`（中性校准载体）、`LineLaserCam/ProfileSnapshot.cs`（双缓冲 + `Version`，`MaxPoints=2048`）、`ProfileMatRenderer.cs`（英莱 250 行 GDI 绘制上提，画布一次分配终身复用）、`SeamPvtFeeder.cs`（B 套流式下载，攒批 16 点 + 查 `RemainBufferSize` 水位 + `MaxPending=8000` 防膨胀）。重写 `ILineLaser/LineLaserEventArgs.cs`（删 `LineLaserFrameEventArgs`，新增中性 `LineLaserSeamResult` struct 与三个事件参数）；`LineLaserCameraBase` 承载 `ResultReady`/`ProfileReady` 与 `CurrentMat`/`UpdateDisplayMat`。英莱 `IntelligentLaserCameraRun` 删 `IlInspectResult`/`IlCalibrationInfo`/`ContourDataReady`/`ContourFrameReady`/`IsManualMode`/GDI 全部（**1746 → 1324 行**），回调尾部只留 `RaiseResultReady` + `RaiseProfileReady`；虚拟相机同构改造。`LineLaserManager` 升为业务中枢（`OnCameraResultReady` → PVT 下载 + 转发；`OnCameraProfileReady` → 记录 + 快照 + 按需 Mat）；新增 `AttachYAxis`/`SetDisplayOptions`/`Profile`/`LastResult`/`MatUpdated`。`LineLaserConfig` 增 `PVT` 与 `DISPLAY` 两节 6 项。消费方：`LineLaserWorkflow` 订阅 `Manager.ResultReady`、`MainPage` 改 33ms 轮询线程 + 版本号、`ILCamPage` 订阅 `MatUpdated`。

**校验**：Python 静态校验 **50 项全 PASS**（实现层无业务残留 / 两个回调各 1 处 / Manager 两条业务链 / 注入面最小 / csproj 注册 / C# 8+ 语法 0 / 无 `Dispose(bool)` / 无用 using 0）。**真编译待 VS。**

**wiki**：新建 `decisions/ADR-035-LineLaserResponsibilitySplit`、`api/ProfileMatRenderer`、`api/SeamPvtFeeder`；重写 `api/LineLaserManager`；更新 `modules/LineLaserCam`、`modules/IntelligentLaserCam`、`api/IntelligentLaserCam`、`decisions/ADR-Index`（扩至 001~039）、`index`（新增 2 个 API 行 + ADR-035 行 + 路由行）、`lessons/IntelligentLaser-Pitfalls` §3.1（**标注「回调驱动显示非轮询」仅适用于低频手动页，主页面改轮询快照**）。备份 `AdaWeldSystem_backup_20260908_164907.tar.gz`。

**待办**：PVT 时间基准（相邻帧实测间隔）与速度前馈（位置一阶差分）**需现场实测标定**；配置项已预留（`PVT/FRAME_SECONDS` 等）。

## [2026-09-08 15:41:44] code+wiki | 线激光三层重构（ILineLaser + LineLaserManager）+ 移除 SmartRay/海康 3D（ADR-034）

**起因（用户）**：要求仿照 MotionControl 的目录方式重排 LineLaserCam——抽象接口 `ILineLaser`、`IntelligentLaserCam`（英莱）、`VirtualCam`（虚拟）、`LinelaserMananger.cs`（管理器：注册选中相机、订阅事件管理、状态管理、配置持久化，对外唯一入口）；删除 SmartRay 与 HikRobot 实现。三项待决经确认：管理器用规范拼写 `LineLaserManager`、配置走 XML（仿 `DeltaMotionConfig`）、`Mv3dLpNet` 引用一并移除。

**代码改动**：新建 6 文件——`ILineLaser/LineLaserType.cs`（`LineLaserKind` / `LineLaserConnectionState`）、`ILineLaser/LineLaserEventArgs.cs`、`ILineLaser/LineLaserCameraBase.cs`（抽象基类：键名 + 连接态派生 + `FrameReady`/`StateChanged` + `RaiseFrameReady`/`RaiseStateChanged`/`Log`）、`CameraRegistry.cs`、`LineLaserConfig.cs`（`Config/XML/LineLaserConfig.xml`，无参 `LoadConfig`/`SaveConfig`）、`LineLaserManager.cs`（Lazy 单例 + 注册即订阅转发 + `SetWorking` + `Select*` + `Dispose`）。英莱与虚拟改为继承基类（删派生类私有 `Tag`/`Log` 防 CS0108），埋 `RaiseFrameReady`/`RaiseStateChanged`；英莱 `LoadSavedIp`/`SaveSensorIp` 移除，改 `SensorIp` 属性由配置下发。删除 `SmartRayCam/`10 + `HikRobotCam/`3 + `Api/`2 文件与 `Mv3dLpNet` 引用；csproj 删 15 项增 6 项；消费方 5 文件 21 处 `CameraSelector.X` → `LineLaserManager.Instance.X`。

**校验**：Python 静态校验 18 项全过（旧符号残留 0 / 抽象成员覆盖完整 / 派生类无 Tag·Log 遮蔽 / 抽象层零厂商依赖 / 具体类型只在 Manager new / csproj 双向一致）。**真编译待 VS。** 备份 `AdaWeldSystem_backup_20260908_151317.tar.gz`。

**wiki**：重写 `modules/LineLaserCam`、`modules/VirtualCam`，更新 `modules/IntelligentLaserCam`、`api/VirtualCameraRun`、`api/IntelligentLaserCam`、`project/overview`、`index`；新建 `api/LineLaserManager`、`decisions/ADR-034-LineLaserThreeLayerRefactor`；删除 5 页（`modules/SmartRayCam`、`modules/HikRobotCam`、`api/CameraRun`、`api/ICameraRun`、`api/CameraSelector`，移入 `_trash_20260908/`）并全库改链；`ADR-Index` 扩至 001~038。

## [2026-09-07 19:49:33] code+wiki | 启动日志四项缺陷修复（参考 HonorMachineTest 的 IO 模式）：连接结果可表达 / IO 取走即记日志 / 动作剥离 IO 线程 / 运控报错去重

**起因（用户）**：贴出 06:17 启动日志提三个问题——①相机连接已失败返回却仍等满超时；②`Init_IO` 命中后未消除（用户指出「IO 只能触发一次动作，进入动作后 IO 要取消掉」）；③运控失败同类报错连报三次。另追加④初始化链同步阻塞 IO 线程 20 秒。并要求先参考 `E:\SoftwareGit\HonorMachineTest\PcomDeviceInterface` 的 IO 方式。

**参考基线结论**（`Work/MachineStatusWork.cs` + `MachineControlWork.cs`）：三线程（EMG 全速 / IO 30ms / 三色灯）+ 每工位独立线程；耗时动作 `new Task().Start()` 异步拉起；触发闭锁两种（边沿标志+长按计时 / 一次性 `EMGshow`）。已新建 [[api/HonorMachineTest-IOReference]] 沉淀。

**关键更正**：问题②**归因需修正**——`TakeVirtualIo` 内部即 `HashSet.Remove`，IO 在动作前已消除；日志显示「06:17:01 置位 → 06:17:21 命中」是因 `ExecuteIo` 同步阻塞了 IO 线程 20 秒，日志打在动作之后。**修 ④ 即解 ②**，另补日志前置。

**改动**：`DeviceStateBase` 加 `ConnectSettled`/`ConnectResult`/`BeginConnectAttempt()`/`MarkConnectFailed()`（连接结果独立于两值 `State` 表达）；`WaitChildConnected` 改出结果即退出并区分「已失败」与「无反馈超时」；4 个工作流失败分支接 `MarkConnectFailed`；`DeviceStatusWork` 加 `DispatchAction` + `thAction`（`_actionBusy` 单动作保护，急停仍同步例外）；删 `MontionManager` 与 `MotionControlWorkflow` 的复述日志（ADR-031 D1，根因只留 `DeltaMontionControl` 一条 Error）。顺手补 `MonitorResult` 6 个属性 XML 注释。

**校验**：括号平衡 ✅ / C# 7.3 禁语法 0 / XML 注释 0 缺 / csproj 双向一致 0。三扫描全绿（147 页）。wiki 同步 3 页 + 新建 1 页。**真编译待 VS。**

**未落地（参考项目有、本项目无）**：`DoResetMachine` 缺复位中止检测（每步后检查状态是否仍为 Reseting）。

## [2026-09-07 18:12:51] code+wiki | 配置体系去单例：DeltaMotionConfig / MoveControlData 改实例类，MontionManager 成唯一对接点

**起因（用户）**：「DeltaMotionConfig 改为和 DeltaAxisConfig 一样的非实例对象类。他们都被 MoveControlData 引用，MoveControlData 也做成非实例对象类。MoveControlData 在 MontionManager 中实例化，注册的轴和 IO 的配置从 MoveControlData 对象中读取，MontionManager 实例将作为唯一的对接台达控制器的对象」。
**三个决策**（用户打断提问后按推荐推进）：持久化统一到一个 XML（弃 INI）；新增 `DeltaIOConfig` 输入/输出分表；消费方一并改走 `MontionManager.Instance.MoveData`。
**代码**：`DeltaMotionConfig` 去 `Lazy` 单例改 public 构造，新增 `Inputs`/`Outputs` 两张 IO 表 + `CALIBRATION` 节（6 项标定）+ `GetInput`/`GetOutput`/`ReadIO`/`WriteIO`；新建 `DeltaIOConfig.cs`（NodeId/SlotNo/BitNo/Enabled/Remark）；`MoveControlData` 去单例，标定参数改**转发属性**到 `MotionConfig`（零副本），`Load`/`Save` 委托；`MontionManager` 持有 `MoveData` 并在构造时 `Load`，`Initialization` 新增 `CreateAxesFromConfig`/`CreateIOsFromConfig` 按配置表建轴与 IO 并套用 Equiv/速度/回零参数。消费方 FormMain.cs:52、MotionControlPage.cs:77/112、WeldProcess.cs:790 三处改路径。
**校验**：括号平衡 / C# 7.3 禁语法 0 / 本轮 5 文件 XML 注释 0 缺 / csproj 双向一致；三扫描全绿（死链 0 孤儿 0 ADR 冲突 0，drift 待修正 0）。**真编译待 VS**。
**⚠️ 关键约束**：`SaveConfig` 会 `NewXdocument` 重建整篇，禁止对 `DeltaMotionConfig.xml` 开第二个 `XdocumentReaderWriter`。

## [2026-09-07 16:57:41] code+wiki | MotionControl 四项结构修正：PVT 合并大写 / IMotion 接入 IPVTMotion / 三张注册表 / 删 IOParam

**起因（用户）**：「1、层级文件修改：PVTInformation 和 PVTPoints 都并入 IPVTMotion（PVT 台达那边都使用大写，请修正）；2、IMotion 层文件完成对 IPVTMotion 的使用；3、MotionControl 下的 Cylinder 改为 CylinderRegistry，增加 AxisRegistry 和 IORegistry 将使用的 IO 和 Axis 注册进控制器；4、IMotion 下的 IOParam 没有任何作用，请清理掉。先修复这些，追踪链路和 UI 窗口我还需要思考下」。走 `@skill:vibecoding-llmwiki` Phase 0~4 全闭环，备份 `AdaWeldSystem_backup_20260907_*.tar.gz`。

**代码变更（4 项）**：

1. **PVT 合并 + 全大写**：`IPvtMotion.cs` / `PvtPoint.cs` / `PvtInformation.cs` 三文件 → 合并为 `IMotion/IPVTMotion.cs`，含 `IPVTMotion` + `PVTPoint` + `PVTInformation` + 新增 `PVTResult`（`OK=0` / `NotSupported=0xFFFF`）；`Type.cs` 的 `PvtTimeMode` → `PVTTimeMode`；`DeltaMotionConfig` 四个属性同步改为 `PVT*` 前缀（构造中枚举引用改为全限定名，规避 Color-Color 解析歧义）。
2. **L2 接入**：`MontionAxis` 改为 `abstract class MontionAxis : IPVTMotion`，四个 PVT 入口用 `public virtual` 默认实现，返回 `PVTResult.NotSupported` + 一条告警日志 —— **未重写的厂商轴（台达）不影响编译**，待 Step 2.3 重写。
3. **注册表重构**：`MotionControl/Cylinder.cs` → `IMotion/Cylinder.cs`（实体下沉 L2，新增 `GetAllIO()` 枚举占用点位）；模块根新增 `AxisRegistry.cs`（123 行）/ `IORegistry.cs`（151 行，输入·输出分表）/ `CylinderRegistry.cs`（128 行）；`MontionManager` 删除四个裸字典改持三张注册表，对外 API 名与签名**零变化**（消费方无需改动），`Initialization` 成功后自动 `AttachAll()` 回灌控制器，`AddCylinder` 同步登记气缸占用 IO。
4. **清理**：删 `IMotion/IOParam.cs`（业务层与 L3 均无引用）。

**校验**：Python 静态校验（无 C# 编译器，真编译待 VS）括号平衡 ✅ / C# 7.3 禁语法 0 / public 成员 XML 注释 0 缺 / 已删符号残留 0 / csproj 与实际文件双向一致（未注册 0、幽灵 0）。三扫描全绿：lint 死链 0 孤儿 0 ADR 冲突 0 外链 0（146 页）；drift 待修正 0；audit 红链 0 重复行 0 二级子目录 0 过小分类 0。

**wiki 同步**：改 `modules/MotionControl.md`（目录树 + 新增「注册表机制」「PVT 能力契约」两节）、`api/MontionManager.md`、`guides/DeltaEtherCAT-DevGuide.md`（目录树/映射表/消费图/§6/§7）、`decisions/ADR-032`、ADR-033、`architecture/DeviceControlArchitecture.md`；`tools/drift_scan_precise.py` REMOVED 表登记 `IOParam.cs` / `IPvtMotion.cs` / `PvtPoint.cs` / `PvtInformation.cs`。

**挂起**：Step 2.3（`DeltaMontionAxis` 重写 PVT 四入口）、Step 2.5（UI 弹窗与状态条）、Step 2.6（焊缝跟踪链路）—— 用户明确「还需思考」。

---

## [2026-09-07 14:58:44] wiki | 沉淀《台达 EtherCAT PVT 与电子凸轮运动开发指南》：高级运动规范 + UI 设计规范（含原档 6 处失准订正）

**起因（用户）**：「结合着项目，把台达运动控制器的使用方式和 UI 设计，沉淀到知识库，我看看你的理解和 vibecoding Plan 后决定如何编程」。原档 `D:\飞书文档\台达EtherCAT_PVT与电子凸轮运动开发指南 (1).md`（2215 行 / 92KB，v1.3，四部分：PVT / ECAM·ECAM2 / 机器人X驱动Y轴跟随 / UI层设计）。走 `@skill:vibecoding-llmwiki` Phase 0 + 1 + 3 + 4（Phase 2 编码待用户拍板）。

**入库**：`raw/delta/台达EtherCAT_PVT与电子凸轮运动开发指南.md`（去掉文件名 `(1)` 后缀）。

**核验方法（ADR-035 纪律：厂商 API 名以 SDK 头文件为准）**：用 Python 把原档全部 49 个 API 名对照 SDK 头文件（`EtherCAT_DLL_x64.cs`，832 个 `CS_ECAT_*` 符号）+ 官方编程手册 `DELTA_IA-GMC_EtherCAT_PM_TC_20250428.pdf`（1018 页，繁体）逐条核验。**命中 46 / 缺失 3**。

**⚠️ 原档 6 处失准（延续 DevGuide 已记录的 8 处，编号 #9~#13）**：
1. **#9 虚拟轴 API 三个名字全部不存在**——`CS_ECAT_Slave_CSP_Set_Virtual_Axis_Position/_Velocity/_Get_...` 在 SDK 中查无此符号（全文无 `Virtual_Axis`）。
2. **#10 虚拟轴语义误解**——SDK 仅有的虚拟相关 API 是 `Master_Virtual_NodeID_Alias_Enable` / `Slave_CSP_Virtual_Set_Enable` / `Slave_CSP_Virtual_Set_Command`；PM 手册 p.257-259 明载其语义是**坐标系平移/零点偏移**（启用后 `Get_Position` 返补偿值、`Get_Actual_Position` 才返马达真值），**不是创建虚拟主轴**。
3. **#11 `SourceType` 枚举值编造**——原档 2.1 称 0=实际轴/1=指令轴/2=虚拟轴/3=外部编码器；PM p.554（ECAM2_Profile_CamIn）真值**只有 0（远端脉波模块或伺服驱动器）与 1（轴卡板载脉冲输入接口）两个值**，不存在 2/3；「外部编码器」实际对应 `SourceType=1`。另 **#11b**：ECAM 一代 `Set_Engage_Parameters` 的同名参数是**啮合触发信号来源**（0=远端模块DI、4=伺服TouchProbe），语义完全不同，勿混用。
4. **#12 PVT 点数上限 256 → 实际 8000**（PM p.339 `DataCount` 最大 8000 笔）。
5. **#13 原档完全未提 PVT B 套流式 API**——`PVT_Begin_Move`(double 工程单位 + `TimeAbsMode`/`Finial`/`Retain`/`SdStopTime`) / `PVT_Continue_Move` / `PVT_CycleStart` / `PVT_Get_Information`(含 `RemainBufSize` 缓冲水位)。这 4 个 API **在 2025-04 版 PM 手册中也查不到**（手册滞后于 SDK），仅存在于头文件，须现场实测。
6. **存疑**：`TargetTime` 是相对间隔还是绝对时间序列——PM 示例 `{0,100,200,300,400}` 两解皆通，但 `PVT_Begin_Move` 有 `TimeAbsMode` 参数说明两种模式可选，待实测。
7. 附带发现：SDK 头文件中 `PVT_Continue_Move` 的 `EntryPoint` 写作**无下划线前缀**的 `CS_ECAT_...`（同族其它均为 `_ECAT_...`），疑厂商笔误，本仓先照抄、运行时若 `EntryPointNotFoundException` 再改。

**⭐ 关键裁决（推翻原档推荐）**：原档方案一「ECAM2 虚拟轴主轴」标 ⭐⭐⭐⭐⭐，但**在 PCI-L221 上不成立**（无虚拟轴 API + 无 SourceType=2）。本项目焊缝跟踪（机器人 X → Y 轴纠偏）推荐改为 **PVT B 套流式**（`Begin_Move` + `Continue_Move` + `Get_Information.RemainBufSize` 闭环），备选 CSP 周期同步；ECAM2 仅在现场具备脉冲/编码器主轴（`SourceType=1`）时复活。X 坐标来源本项目**已具备**（`Comm/Robot/KUKARobot/RSICommunication.cs` RSI 1~12ms + EKI + `WeldProcess.CurrentRobotX`），原档 3.3 全节示例代码**不落地**。

**UI 设计的关键洞察**：原档第四部分是**按另一个项目写的**（`MasonMotionControl` 命名空间、`IUpdate` 接口、`AxisControl`/`MachineInputIO`/`CylinderControl` 控件、`DataGridView`、`Label.BackColor` 状态灯、`Form` 弹窗、`XmlSerializer`）——**这些在本项目全部不存在**。本页给出到 AdaWeldSystem 的翻译对照表 14 项：`DataGridView`→`AntdUI.Table`、`Label.BackColor`→`AntdUI.Signal`、`Form`→UserControl+`Modal.open`（ADR-016）、`IUpdate`→单入口 `RefreshUi(scope)`、`XmlSerializer`→`FileOperate/XMLfile.cs`、`GetMotionManager()`→`MontionManager.Instance`；目录走用户 2026-09-07 新建的 `UIDesign/SubDialog/MotionDialog/`，命名用 `XxxForm` 后缀。

**产出**：新建 [[guides/DeltaEtherCAT-AdvancedMotion]]（7 节：权威顺序 / 失准订正表 / PVT A·B 两套 / ECAM·ECAM2 / 跟随选型裁决 / 待补 Native 声明 32 个 / OPEN 6 项）、新建 [[guides/DeltaEtherCAT-UIDesign]]（7 节：翻译对照表 / 无心跳与 7 项状态 API / MotionControlPage 改造 / 5 个新增弹窗 / 刷新机制 / 持久化 / 10 项检查清单）；更新 [[modules/MotionControl]]（换轨沿革表加心跳与焊缝跟踪两行 + 新增「高级运动能力」节 + 设计决策）、index 加 2 行。

**能力缺口**：`Native/EtherCATAdvancedNative.cs` 现仅 16 个 extern（ECAM2 只覆盖 4 个、PVT 只覆盖 2 个），落地前需补约 32 个声明。

**未做 Phase 2 编码**——等用户看完理解与 Plan 后决定。

## [2026-09-07 14:41:25] wiki | 对照代码修正知识库：UIDesign 目录重构（SubView/ → SubDialog/ 五业务域）+ 8 个类型改名

**起因（用户）**：「由于我修改了程序代码的项目文件名称和位置，你先对照代码修正知识库后再做这个任务」——用户重构了 `UIDesign/`，知识库全部旧路径/旧类名失效。走 `@skill:vibecoding-llmwiki`。

**代码侧实测（`git status` + `ls`）**：`UIDesign/SubView/` 整个目录删除（16 组文件），新建 `UIDesign/SubDialog/` 下 5 个业务域子目录共 25 个 `.cs`；`UIDesign/ControlPage/DataReviewPage.*` → `DataReviewerPage.*`；`AdaWeldSystem.csproj` 已由用户同步更新（`Compile` + `EmbeddedResource` 全部指向新路径）。

**新目录结构**：`SubDialog/` = `DataReviewerDialog/`（FileTraceForm / HelixRenderForm / RecordConfigForm / RenderParamForm）+ `FormMainDialog/`（InitWaitingForm）+ `IntelligentLaserDialog/`（ILAlgoForm / ILAlgorithmEditForm / ILParamForm / ILScanForm）+ `ParamContolDialog/`（AutoParamForm / ConfigForm）+ `UserManagerDialog/`（LoginForm / UserEditForm）。**命名空间未随目录变更**（仍 Sub3UI/Sub2UI/Sub1UI）。

**8 个类型改名**：`DataReviewPage`→`DataReviewerPage`、`ILAlgoPage`→`ILAlgoForm`、`ILParamPage`→`ILParamForm`、`ILScanDialog`→`ILScanForm`、`AlgorithmEditForm`→`ILAlgorithmEditForm`、`FormLogin`→`LoginForm`、`UserEdit`→`UserEditForm`、`InitWaitingPanel`→`InitWaitingForm`。

**知识库修正 26 文件 144 处**：精确路径 20 条规则 + 目录泛化 2 条 + 裸类名正则 8 条（带自引用护栏：`AlgorithmEditForm` 排除已含 `IL` 前缀与 `AlgorithmEditForm_HandleDestroyed` 方法名；`UserEdit` 排除 `UserEditForm`）。改最多的是 `modules/UIDesign.md`(21) / `modules/IntelligentLaserCam.md`(19) / `api/ILAlgorithmEditForm.md`(14) / `people/UISpecialist.md`(11)。

**手工重建 3 处目录树 + 1 处技能文档**：`modules/UIDesign.md`（新增 §「2026-09-07 目录与命名对照」10 行映射表）、`people/UISpecialist.md`、`project/overview.md`、`raw/skills/.../UISpecialist.md`。`api/AlgorithmEditForm.md` 改名 `api/ILAlgorithmEditForm.md`（含 `tags` 的 SubView→SubDialog），全库 `[[api/AlgorithmEditForm]]` 链接同步。

**drift 工具同步**：`drift_scan_precise.py` 的 REMOVED 表新增 8 条改名登记（供历史日志/未来页面检索旧名），RENAMED 表内 3 条旧「现役路径」自动跟进到 `SubDialog/` 新路径。

**代码残留（非阻塞，未改）**：Designer `this.Name` 仍为旧值 3 处（`DataReviewerPage.Designer.cs:336` / `ILAlgoForm.Designer.cs:197` / `InitWaitingForm.cs:59`）；`ILAlgoForm.cs` 内 6 处日志标签仍写 `"AlgorithmEditForm"`；`ILAlgorithmEditForm.cs` 事件处理器名仍为 `AlgorithmEditForm_HandleDestroyed`。已记入 `modules/UIDesign.md` 待清理清单。

**三扫描全绿**：drift 待修正 0（修正前 11）、lint 死链 0 / 孤儿 0 / ADR 冲突 0 / 外链 0、wiki_audit 红链 0 / 孤儿 0 / 重复行 0 / 二级子目录 0 / 过小分类 0。行尾经 `core.autocrlf=true` 归一化无污染。备份 `LLMWiki_backup_20260907_143453.tar.gz`。

## [2026-09-07 13:45:53] wiki | 知识库整理：清理正运动内容 + ADR 全库重排 + 台达部署规范（ADR 全库编号体系）

**起因（用户）**：① 清理掉正运动相关的内容，程序不再使用正运动设置 ② 重新整合知识库文档的标号和内容关联 ③ 台达部署参考官方安装程序与指导文档，把 DLL 复制到项目内。走 `@skill:vibecoding-llmwiki` Phase 0~4。

**用户三项裁定**：① 正运动专属页（3 ADR + 8 API 页）**全部删除**（不再保留 deprecated 横幅）② 标号**重排全库编号体系**（不保留空号）③ DLL **仅 x64 版，输出 bin**（现状，补部署规范页）。

**删除 11 页**：`decisions/` 的 ADR-022-ZMotionControllerIntegration / ADR-023-RSICamBoxTrackingArchitecture / ADR-027-DefaultInitZMotion；`api/` 的 ZMotionController / CamBoxTracker / EncoderAxis / RSIPositionBuffer / IMotionController / MotionManager / IAxis / IIO。

**ADR 全库重排 001~037**：删除 3 项后后续编号前移（024→022 … 040→037，共 16 个文件改名）。引用重映射覆盖 **wiki 全库 + logs/log.md + tools/ + raw/skills/ + AdaWeldSystem 代码注释 + 用户 skills 两副本**，合计约 800 处。可追溯性三件套：① 新建 `decisions/ADR-Index` 编号总表（旧→新映射 + 已删且编号被占用的三项对照）② 每页 frontmatter 加 `previous_id` ③ 页内 `title`/一级标题编号与文件名对齐（**顺带修掉历史遗留的 34 处「编号与主题名不匹配」**）。

**内容关联整合**：写 `ADR-032/037` 名实不符自动校正脚本，按**主题名反查真文件**修正编号错链 **103 处**；已删 api 页链接按映射重指向现行页 **9 处**；手工修 23 处（KUKARobot / 架构页 / MotionControlWorkflow / MontionManager / ADR-033 等）；index 删 11 条已删页索引行、ADR 表按编号升序重排、新增 §7.0 编号总表路由。

**架构页第 10 章整章改写**：原「CAMBOX 硬件级实时跟踪」（正运动 ATYPE=25 / Z-BASIC 初始化 / `ZAux_CamBox_AddPoint`）→「台达 EtherCAT 主站」：四元组寻址表、初始化与使能序列（`Set_Move_Mode(8)`→`Set_Svon(1)`→轮询 bit2）、三层职责划分表。另把架构页模板代码中的 `MotionManager` 全改 `MontionManager`（`GetMotionManager()` → `Instance`）。

**重写 `api/MotionControlWorkflow`**（整页仍是旧 CAMBOX 内容）：改为台达版——`MotionControlPhase` 相位表、步段 10/20/700/900、方法表、OPEN 说明（跟踪高级运动方案未定）。

**台达部署规范 `guides/DeltaEtherCAT-Deployment`（新建）**：依据官方 `manual/API/DELTA EtherCAT UserGuild.pdf` 第 1 章 + 安装程序 `EtherCAT\CopyCmdx64.bat` / `CopyCmdx86.bat` / `sample\C#\Copy.bat`。官方三步法：① 设备管理器装驱动（指向 `EtherCAT\driver`）② 系统级 DLL（`x64`→`System32`、`x86`→`SysWOW64`、带 `msvcr100`）③ `C:\EtherCAT\`（ESI/AutoConf/Config）。项目内做法：`3rdDepend\EtherCAT_DLL_x64.dll`（168,744,448 B）→ csproj `CopyNative3rdDependToOutput`（第 737 行）→ `bin`。含 `#if X86` 条件编译约定（官方也用 `X86` 常量切命名空间；本项目仅 x64 配置，恒走 x64 分支）、9 项部署校验清单、6 类故障定位。**目标机实测**：`C:\EtherCAT` ✅、`System32\EtherCAT_DLL_x64.dll` ✅、`SysWOW64\EtherCat_DLL.dll` ✅、`msvcr100.dll` ✅；⚠️ 驱动 sys 未落 `System32\drivers`，需设备管理器确认。

**踩坑**：① 重排脚本 `os.path.relpath` 跨盘（C: vs D:）抛 `ValueError` → 打印语句需 try 保护，替换本身已完成 ② 删除 ADR 后残留 `[[decisions/ADR-023-RSICamBoxTrackingArchitecture]]` 在重排后**指向了完全不同的页面**（新 023 = Dispose 全覆盖），必须先按名修链再排查 ③ `grep -c $'\r'` 在 Git Bash 下不可靠，行尾须用 Python 按字节判 ④ 批量重排必须「先改名/后标注」且操作幂等（`previous_id` 判重 + 名字索引），否则二次运行会串号。

**校验（三扫描全绿）**：wiki_audit 红链 0 / 孤儿 0 / index 重复 0 / **ADR 编号 1~37 连续无空洞** / 二级子目录 0 / 过小分类 0；lint_scan 死链 0（修掉 3 处无 `decisions/` 前缀的历史链接）/ 孤儿 0 / ADR 冲突 0 / 外链 0；drift_scan 待修正 0。行尾 `core.autocrlf=true` 归一化后入库一致，无全文件重写。

**备份**：`LLMWiki_backup_20260907_132516.tar.gz`（198 文件）、`AdaWeldSystem_backup_20260907_132516.tar.gz`（386 文件）。

**OPEN**：真编译待 VS；`bin/Debug` 残留 3 个正运动 DLL 待手工清理；驱动安装状态需现场确认；台达侧焊缝跟踪高级运动方案未定。


## [2026-09-07 11:52:13] coding | 移除正运动（ZMotion）+ 全面落地台达 EtherCAT + 消费方全量对接（ADR-030）

**起因（用户）**：四项需求——① 移除 Zmotion ② 全面编写台达的运动控制 ③ 台达消费方全量对接 ④ 新建与修改代码的精简和注释精简。走 `@skill:vibecoding-llmwiki` Phase 0~4。

**用户四项冲突裁定**：① L2 抽象层命名**以原档与规范页为准**（雷赛仅参考，不是当前实现）；② 正运动遗留高级组件 `CamBoxTracker`/`EncoderAxis`/`InterpolationEngine`/`RSIPositionBuffer` **全部删除**，台达用哪种高级运动承接焊缝跟踪**暂不确认**；③ `MotionConfig.cs`(759 行) **删除且暂不建新配置**；④ L2 中 6 个 Modbus 抽象方法**移除**（台达无 Modbus，走 PDO/SDO）。

**删除**：`ZMotion/` 10 文件（约 5100 行）+ `API/` 4 文件 + `MotionManager.cs` + `MotionConfig.cs` + `3rdDepend/{zauxdll,zmotion,ZmotionScanLaser}.dll`。

**新建 21 文件**：L2 `IMotion/` 8（Type/MontionControl/MontionAxis/MontionIO/InputIO/OutputIO/IOParam/InterpolationMontionParam）；L1 `DeltaEtherCAT/Native/` 5（Master/Motion/IO/Advanced/ErrorCode）；L3 `DeltaEtherCAT/` 5（DeltaMontionControl/DeltaMontionAxis/DeltaInputIO/DeltaOutputIO/DeltaSlaveScanner）；业务层 `MontionManager.cs` + `Cylinder.cs`。命名沿用原档 `Montion*` + `Delta*` 前缀。

**踩坑与订正**：① 高级功能 API 真名与规范页不符——ECAM2 实为 `CS_ECAT_Slave_CSP_Start_ECAM2_*`（37 个，非 `Slave_ECAM2_*`）、Gantry 实为 `CSP_Gantry_Enable`、TouchProbe 实为 `Motion_Set_TouchProbe_Config`（**规范页第 7~8 处失准**）；② 错误码 `0x1002` 规范页注「从站初始化失败」，SDK 实为 `ERR_ECAT_MODE_CHANGE_FAILED`（模式切换失败）；③ `DeltaMontionAxis` 内 `_connectNo` 是初始化期快照会过期，24 处统一改为实时取 `CardNo` 属性；④ csproj 更新脚本 `nl` 用 bytes 导致 `join` 报 TypeError，改 str 后通过；⑤ 原生 DLL 部署段是 6 空格缩进（非 4），首轮匹配失败。

**消费方对接**：`MotionControlWorkflow.cs` 全量重写（删 ZMotion 依赖、阶段枚举改 `MotionControlPhase`、步位 10/20/700、初始化改 `MontionManager.Instance.Initialization("台达运控", ref msg)`，对外契约不变）；`DeviceControlWork.cs` L193/L367 类型改 `MontionManager`；`WeldProcess.cs` 注释更新；`MotionControlPage.cs` 无需改动（只用 Workflow）；`FormMain.cs` 清 1 处无用 using。csproj：17 条旧 Compile → 21 条新条目，原生依赖改 `EtherCAT_DLL_x64.dll`（161MB，已从台达 SDK 复制；`3rdDepend/` 被 gitignore 不入版本库）。

**校验（无 C# 编译器，Python 静态校验替代，真编译待 VS）**：抽象方法实现完整性 ✅4/4；L2 零依赖 ✅（注：`EtherCATMaster` 是协议枚举非厂商名，脚本误报需人工甄别）；业务层/UI 不回流 ✅；厂商类型越界 ✅仅 `MontionManager.cs:96` 一处装配点；C# 7.3 禁用语法 ✅0；无用 using ✅0（经全仓类型索引精确检测，首轮按命名空间末段匹配的 27 条全为误报）；跨文件符号解析 ✅缺失 0；正运动残留 ✅0；日志符号 ✅0；`Dispose(bool)` ✅0。

**规范缺口（待补 standards/CodeSimplification）**：本仓既有 P/Invoke `static extern`（`SensorHelper.cs`/`Program.cs`）**均无 XML 注释**，与「public 必 XML」规则冲突。本次按既有约定豁免 Native 层 64 条 extern 声明，规则需在规范页显式写明豁免。

**产出**：重写 [[modules/MotionControl]]（台达现行 + ⛔ 正运动沿革分节）；新建 [[decisions/ADR-033-ZMotionRemovalAndDeltaLanding]]、[[api/MontionManager]]；⛔ 标记废弃 11 页（ADR-019/023/027 + api 的 ZMotionController/CamBoxTracker/EncoderAxis/RSIPositionBuffer/IMotionController/MotionManager/IAxis/IIO）；index 更新 8 处。

**OPEN**：焊缝跟踪高级运动方案未定（ECAM2 / 虚拟轴+GearIn / PVT）；心跳与 BAS 保护无台达对应；主动/周期上报无对应；台达配置体系未定；161MB DLL 部署策略；`bin/Debug` 残留 3 个正运动 DLL 需手工清理；**真编译待 Visual Studio**。


## [2026-09-05 22:26:22] docs | 台达 EtherCAT 运动控制器开发文档沉淀（替换正运动调研）

用户提供《运动控制模块开发文档（台达 EtherCAT 版）》原档（1323 行），要求结合本机台达 SDK 源码沉淀知识库。

**核验优先（原档不盲信）**：从 SDK 头文件 `inc/C#/EtherCAT_DLL.cs` 自动抽取 832 个 P/Invoke 声明，与原档声称的 61 个 API 逐一比对——**发现 6 处 API 名在 SDK 中不存在**（照抄编译不过）：`Get_Card_Seq`→`Get_CardSeq`、`Get_Slave_Num`→`Get_SlaveNum`、`Get_Initial_Error_Code`→`Get_Initial_ErrorCode`、`Motion_Get/Set_Move_Mode`→`Get/Set_MoveMode`、`CSP_Start_VMove`→`CSP_Start_V_Move`、`CSP_Target_Pos_Change`→`CSP_TargetPos_Change`；另 2 处签名细节差异。错误码 336 个经核对基本正确，仅 `0x1002` 标注有误（实为 `MODE_CHANGE_FAILED`）。

**关键改写**：原档迁移基线是**雷赛**（`MontionControl`/`MontionAxis`/`int SetON()`），与本项目**正运动 ZMotion**（`API/IAxis.cs` 用 mm、`IIO` 为 void）完全不同，已按本项目结构重做映射。

**技术要点**：① 单位换算陷阱——正运动用 `ZAux_Direct_SetUnits` 在**控制器侧**换算（故源码无乘除代码），台达无此机制、**必须 PC 侧实现层乘除**；② IO 推荐**全局位软元件**（`Read_InBit`/`Write_OutBit` + `Get_InBit_Info` 反查），契合 `IIO` 契约，优于原档的 NodeID+SlotNo 方案；③ **CAMBOX 可由「虚拟轴 `CSP_Virtual_Set_Command` + GearIn + ECAM2（`Profile_Data`/`Profile_CamIn`/`Profile_CamOut`）」承接**，SDK 实证 ECAM2 有 24 个 API；④ 初始化官方实证序列 Open→Get_CardSeq→Initial→轮询 `Check_Initial_Done`（0 完成/1 进行中/99 失败），退出 Reset+Close。

**产出**：新建 [[guides/DeltaEtherCAT-DevGuide]]（14 章，含 CAMBOX→ECAM2 专题、6 处订正表、13 项踩坑、9 步落地清单、6 项 OPEN）、[[api/DeltaEtherCAT-Native]]（832 API 全量速查，脚本生成）；原档与核验产物归档 `raw/delta/`；`modules/MotionControl.md` 增台达章节；index 三处登记。

**遗留 OPEN**：**振镜**（`ZMotionGalvo` + `ZmotionScanLaser.dll`）台达侧无直接对应（最需关注）、激光 PWM 验证、自动上报改 `Record_*` 族、急停通道、169MB DLL 部署策略、是否保留 ZMotion 双轨。

## [2026-09-04 18:04:24] coding | 启动日志 8 项问题修复：状态机语义 + 初始化时序 + 报错分层（ADR-027/038）

**起因（用户）**：提供程序启动日志，指出 8 项问题——FormMain 越权打印初始化完成 / Stop→Alarm 违反设计 / 故障恢复模块来路不明 / 子设备初始化时序颠倒 / 子设备初始态出现 Standby / 清状态在未连接时误触发 / 同一错误重复记录 3~4 层 / 心跳未开启也无限刷报警。

**用户三项评审裁定**：① 故障恢复模块整体删除；② 初始化连接失败置 Alarm、清除报警后回 NoReset；③ AntdUI Modal 非阻塞等待。

**代码修复（9 文件 + 2 删除 + 1 新增）**：
- `DeviceControlWork`：初始态 Stop→NoReset；`DoInitializeMachine` 删 ClearMachine、通讯提为第 0 步、焊接头/运控 Initialize 失败不再误置 Connected；`EvaluateInitializationResult` 全部就绪保持 NoReset；`DoClearAlarm` 一律回 NoReset（关闭 OPEN-ClearAlarmSemantics）；心跳线程重写（通讯开启成功才检测，失效停检+重连 3 次）；新增 `InitializationCompleted` 事件；删 RecordFault。
- `DeviceStatusWork`：删 RecordFault/状态反射日志。`DeviceStateBase`：删连接态/焊接过程态切换日志（事件保留）。
- `MotionControlWorkflow`：ClearStatus 不再经 SetPhase(Idle) 映射出中间 Standby；删重复报错。4 个工作流删 FaultRecord 调用。
- `FormMain`：删越权日志；初始化移至 Shown + Modal 等待（新 `InitWaitingPanel`，事件自动关闭）。
- 删除 `ProductFileManager/FaultRecoveryManager.cs`、`SqlLiteDatabase/FaultRecordManager.cs`（csproj 同步）。

**校验**：旧符号残留 0、花括号配平 0 差、BOM/CRLF 与备份一致（备份 `AdaWeldSystem_backup_20260904_174325.tar.gz`）；真编译待 Visual Studio。

**Ingest**：新增 ADR-027 / ADR-028；架构页 §9 三处 + TOC 更新；api/FaultRecoveryManager、api/FaultRecordManager 挂 ⛔ 废弃横幅；api/DeviceStatusWork、api/LineLaserWorkflow 同步；OPEN-ClearAlarmSemantics 关闭；index 决策表加 2 行。

## [2026-09-04 15:21:47] coding | /// 注释精简轮：MainDeviceControl 10 文件长篇 XML 注释瘦身

**起因（用户）**：上一轮（14:54）把类注释改成「单行 summary + remarks」后用户指出 summary/remarks 都属于 /// 注释，仍存在大量长篇大论——remarks 搬家不等于精简。

**规范依据**：standards/CodeSimplification 二.②（summary 20 字内单行；类 summary 一行完成；过程/由来归 LLMWiki 不进代码）+ RefFileOrganization §3。

**本轮裁定（已回灌规范页）**：类头 remarks 至多 1~2 行只写「为什么」级个性约束（R0xx 差异化职责、数据/权责边界）；子类与基类共性（线程归属/推进模型/对外态承载）只在基类写一次；枚举值清单、执行步段位清单、数据流向分步、「用户 2026-09-04 裁定」类由来叙述全删（由 wiki/OPEN 决议页承载，DoClearAlarm 保留 C3 待决指针一行）。

**改动**：10 文件（DeviceControlWork / DeviceStatusWork / DeviceStateBase×4 / DeviceWorkflowBase / CommandCore / 5 workflow）——类头 10 处（最长 27 行 remarks → 1 行）、多行成员 summary 5 处单行化、成员级 3 行以上 remarks 19 处压缩。多行 summary 残留 0、多行 remarks 残留 0。

**校验（Step 2.6）**：Python 对照 15:08 备份（AdaWeldSystem_backup_20260904_150857.tar.gz）逐文件 diff——差异全部为 /// 注释行、BOM+CRLF 全保持。**真编译待 Visual Studio**。

**新踩坑**：同一文件的多个 Edit 放同一并行批次存在竞态（DeviceStateBase 三个枚举编辑仅最后一个落盘）——同文件多处编辑必须串行执行。

**wiki 同步**：standards/CodeSimplification.md 二.② 追加 remarks 篇幅细则。

## [2026-09-04 14:54:09] docs | ADR-026 术语与类注释收尾（9 文件，仅注释变更）

**范围**：MainDeviceControl 9 个 .cs —— DeviceStateBase / CommandCore / DeviceWorkflowBase / LineLaserWorkflow / DeviceStatusWork / LaserWeldHeadWorkflow / MonitorCameraWorkflow / MotionControlWorkflow / WeldParamControlWorkflow（DeviceControlWork 类头已合规，免改）。Step 2.1 备份 `AdaWeldSystem_backup_20260904_143222.tar.gz`。

**内容**：
1. 类级 XML 注释统一为「单行 `<summary>` + `<remarks>`」结构。其中 MonitorCameraWorkflow 原类头**标签损坏**（`<summary>` 无闭合、`</remarks>` 孤悬），本轮修复；WeldParamControlWorkflow 27 行巨型单块 summary 拆分，`**…**` markdown 星号统一为 `<b>` XML 标签。
2. 残留旧术语清理：WorkStep / GoStep / SetStep / IsRunLoopActive / StartRunLoop / ADR-047 等表述统一为现行口径（RunStep bool 驱动 / 17 项契约 / 子流程不自带线程）；过程性表述（如"不再用 WaitOne(5000)"）改现状描述。
3. LineLaserWorkflow 删除未使用历史常量 `PreWorkWaitTimeoutSeconds`（13:59 纪录标注的清理候选；`PreWorkWaitTimeoutSeconds` / `PreWorkWaitTimeout` 双模式 Grep 零引用确认后删除）。
4. 类头「差异化职责」表述与 wiki api 页对齐（MonitorCamera R010 轴控制行为 + 送丝距离合规检查）。

**校验（Step 2.6）**：Python 校验器对照 14:32 备份逐文件 diff —— 差异仅 `///` 注释行（唯一例外即上述常量删除）、字节风格全部 BOM+CRLF 保持、`<summary>`/`<remarks>`/`<param>`/`<returns>` 开闭配对全过。**真编译待 Visual Studio**。临时脚本 4 个已清理。

**wiki 同步**：api/LineLaserWorkflow.md 的「清理候选」注记改为已删除。

## [2026-09-04 13:59:16] docs | 五个子工作流 API 页整页重写对齐现行代码

**起因**：2026-09-04 13:43 轮 DeviceLog 移除 + 残留审计后，五个 api 子工作流页（LaserWeldHeadWorkflow / LineLaserWorkflow / MonitorCameraWorkflow / MotionControlWorkflow / WeldParamControlWorkflow）仍为「改造前 API 存档 + ⏳ 整页重写待办」横幅。本轮整页重写，剔除 GoStep/WorkStep/Starting/StartRunLoop/ManualOn/命令三槽 等已清除机制描述，改为现行代码 + 架构页 §4/§5/§16 口径。

**每页落地要点**（以各 .cs 现行源码为准逐项核对）：
- LineLaserWorkflow：执行步段位 10→20→30→31→100→700（基类 0/800/900）；DoPreWorkWaitWork 超时 30s → Fail（模拟模式在步 31 自驱动）；数据稳定 5 帧；失败计数 5s 窗口 + MaxConsecutiveFailures=5；OnWeldStatusChanged 复位表 + ReleaseCameraBinding；WeldStatusTrans 三分支；BeginWorking 现仓库内无调用方；连接/断开后台线程 _isConnecting 防重入
- MonitorCameraWorkflow：私有相位 MonitorWorkflowState 映射（Acquiring/Analyzing/Completed→Working，Uninitialized→NoReset）；WaitOne(0) 非阻塞探测 + 超时 5s；WireStickoutDeviation（2026-09-04 裁定，供机器人调送丝）；OffsetX/OffsetY 供振镜（§7.4.5）；健康巡检归 MonitorCameraRun
- MotionControlWorkflow：相位 LaserCamBoxWorkflowState 映射表；步 10/20/30/100/110/700/900；IsRunning=Tracking|WaitingForMaster；Initialize 三参数；StepTracking 内 ApplySpotAlignCompensation 消费 DeviceControlWork.AlignDatum（todo 振镜摆幅）
- LaserWeldHeadWorkflow：骨架期（相位 0~3，无业务执行步）；温度阈值监控（原档 R009 / 批次 4.1）todo；FlowProcess 空转
- WeldParamControlWorkflow：相位 0~6 映射（默认→Working）；StepIdle 消费 _pendingCompute；LoadParameters/ComputeAndOutput/Complete/SwitchParameter；ConsecutiveFailureCount 直通 WeldProcess；CalcGalvoAmplitude TODO 占位 0

**字节风格保持**：LineLaser BOM+CRLF / MotionControl BOM+CRLF / MonitorCamera BOM+LF / LaserWeldHead noBOM+LF / WeldParam noBOM+LF（逐文件还原，避免无谓 diff）。

**模块页同步**：modules/DeviceControl.md「各工作流」表 7 行修正——LineLaser 步号去 11、MotionControl 去 BeatMs=20、LaserWeldHead 去 IsRunLoopActive、DeviceControlWork 去「三槽命令变量」、DeviceStatusWork 行与节改 thIOWork/thEMGWork/thLightStatusWork + EstopMachine/EstopCancel/MachineIOWorkOpen/MachineIOWorkClose 新名。

**遗留观察**：LineLaserWorkflow.cs:34 PreWorkWaitTimeoutSeconds 为未使用历史常量（清理候选）；五个相位枚举为同文件公共枚举但仅内部 _phase/_flowState 驱动（与「私有相位」描述等价）。

**体检**：wiki_audit（红链 0 / 孤儿 0 / 重复 0 / ADR 1~36 连续）/ lint_scan（死链 0）/ drift_scan_precise（待修正 0）三项全绿。真编译待 Visual Studio。

## [2026-09-04 13:43:25] fix | 移除残留设计 DeviceLog + MainDeviceControl 知识库残留比对审计

**起因（用户裁定）**：用户指出 DeviceLog 属**残留设计**——新架构（主控设计.xlsx + 激光焊接系统业务流程图 20260904.md + 用户逐条裁定）从未要求该中间层。追溯：2026-09-03 00:54 轮次（设备日志统一出口 feat）AI 在处理「63 处 ShowLog 标签发散」时自创 DeviceLog.cs 静态类并写入架构页 §2/§16.6、新建 api/DeviceLog.md 制度化；用户裁定 C7 仅限 `SubDeviceLog()` public + 各子流程各自重写，与整机出口无关。

**代码侧**：删 `MainDeviceControl/DeviceLog.cs`（os.remove）+ `.csproj` 摘登记；11 处调用改直连 `GlobalCommData.ShowLog`（DeviceStateBase 3 / DeviceWorkflowBase 1 / DeviceControlWork 6 / DeviceStatusWork 1）。`SubDeviceLog`（C7 契约）保留。

**wiki 侧**：删 `api/DeviceLog.md`；9 页 35 处替换（`[[api/DeviceLog]]`→`[[api/GlobalCommData]]`、DeviceLog 类描述改直连、lessons/CodeSimplification/index/ADR-026/modules/vibecoding-workflow/架构页 §2 目录+§16.6 映射）。架构页 §16.6 映射修正：参考 `CommenData.ShowLog`→`Comm/GlobalCommData.ShowLog`、`CommenData.MachineLog`→`Comm/GlobalCommData.MachineLog`（原误映射到 DeviceLog）。

**残留比对审计发现（批次 A~F 落地后知识库同步遗漏）**：
1. 5 个 api 子工作流页（LaserWeldHead/LineLaser/MonitorCamera/MotionControl/WeldParam）仍为**改造前 API 存档**且横幅称「改码尚未开工」（已过时）→ 横幅纠错 + 标注「⏳ 整页重写待办」（正文 GoStep/Starting/WorkStep 等旧名，均已在代码清除）
2. `modules/DeviceControl.md` 旧 DeviceControlWork 存档节（BeatMs=10/_workStep/命令三槽）→ 整节重写为 7 线程现行 + ⛔ 存档标注；「等价最小改写（GoStep）」节 → 现行范式（RunStep/AdvanceStep）
3. 架构页 §13 与 api/FormMain.md `SubDeviceWeldStatus` 枚举仍列已删 `Starting` → 改 NoReset 开头 7 态
4. `modules/Safety.md` 「IsRobotPoseSafe pose 语义并入监控循环」措辞 → 修正为 C3 已删、IsSafe=本机安全 IO

**体检**：wiki_audit / lint_scan / drift_scan_precise 三项全绿。真编译待 Visual Studio。

## 2026-09-04 12:18:32 — 新增原档 md 版 + IO 统一触发架构落地（批次 A/B/C/D/E/F）

**原档变更**：新增 `raw/architecture/激光焊接系统业务流程图20260904.md`（706 行，人工全量转写）。
**该 md 版取代 PDF 成为业务流原档主源**，PDF 降级为图形备份。ADR-025 登记由 2 份修订为 3 份，
已同步架构页 §5 / §959、`index.md`、`ADR-026`（共 6 处）。

**补齐内容**：md 版比 pypdf 提取的 928 字多出 10 项，其中最重要的是
**§2 IO 统一触发架构整章**（PDF 文本层完全丢失）与 **§10 共 21 条机器人命令设计表**。

**七项冲突裁定**：C1 完整落地 IO 中转 / C2 是数据流非归属 / C3 暂维持旧文档回 Stop 并标记
/ C4 以代码 `Standby` 为准 / C5 子设备级命令不新增公共 API / C6 查询+参数 8 条全落地 / C7 本轮做。

**用户硬约束（务必牢记）**：
1. **不新建 .cs 文件** —— 虚拟 IO 常量与置位表定义在 `DeviceControlWork.cs` 内部。
2. **不新建扫描线程** —— `thEMGWork`（急停，单线程）+ `thIOWork`（Running+Alarm，一个线程），
   两者**同时监控虚拟 IO 与物理 IO**，物理 IO 由控制器给出。
3. **机器人通讯必须转到 IO** —— 坐标类解析 string 仅记录，动作类机器人直接写 IO 量，
   两条路径都收敛到虚拟 IO 层。

**改码**（批次 B/C/D/E，静态校验全绿，**真编译待 Visual Studio**）：
- `DeviceControlWork.cs`：新增虚拟 IO 常量 13 条 + 置位表 + 6 个操作 API + `ExecuteIo` 分派；
  5 个系统级命令改为置位（`DoXxx` 为执行体）；`DispatchCommand` → `MapCommandToIo`（机器人通讯转 IO）；
  8 条查询/参数命令；`CheckPreworkFailed` 预检通路；`AlignDatum` 偏差中枢
- `DeviceStatusWork.cs`：`thEMGWork` 物理+虚拟急停统一扫描；`thIOWork` 增 `ScanRunningIo` + `CheckPreworkFailed`；
  新增 `ReadPhysicalEmg` / `ScanPulseIo`
- `DeviceWorkflowBase.cs`：新增**非抽象** `RequestWeldStatus`（不破坏 17 项抽象契约）
- `MonitorCameraWorkflow.cs`：`MonitorResult` 补 `WireStickoutDeviation`
- `MotionControlWorkflow.cs`：`StepTracking` 阶段消费光斑偏差 `ApplySpotAlignCompensation`

**知识库**：新建 `decisions/OPEN-ClearAlarmSemantics`（C3 待决标记，含用户焊接工艺 reasoning）；
架构页新增 **§7.9 IO 统一触发架构**（100 行）；`api/DeviceControlWork` 新增 5 个章节。
三项扫描全绿（红链 0 / 孤儿 0 / 死链 0 / drift 待修正 0）。

# Wiki Log — 变更日志

> 时间导向的追加日志。每条记录以 `## [日期时间] 操作类型 | 描述` 开头。
> 时间戳获取方式：执行 PowerShell 命令 `Get-Date -Format "yyyy-MM-dd HH:mm:ss"` 获取准确时间。
> 若无法执行命令，标记为 `[No.]`，**严禁猜测填写**。

---

> ⚠️ **2026-09-03 ADR 连续重编号 —— 本日志中的旧编号一律保留原貌**
> 即日起 ADR 已重排为 **001~036 连续编号**（原 41 条中 5 条决策页按用户裁定删除：旧 017 / 025 / 040 / 047 / 048）。
> **本日志是追加式历史流水，不改号** —— 改号会破坏可追溯性。文中旧编号按下列规则解读：
> - **旧→新（31 条）**：007→006、008→007、010→008、011→009、012→010、013→011、014→012、015→013、016→014、018→015、019→016、020→017、021→018、022→019、026→020、028→021、029→022、030→023、031→024、034→025、035→026、037→027、038→028、039→029、043→030、044→031、045→032、046→033、049→034、050→035、051→036；001~005 不变。
> - **已删除、编号不再存在（15 条）**：旧 006、009、017、023、024、025、027、032、033、036、040、041、042、047、048。
>   ⚠️ 其中 006 / 017 / 025 / 033 / 036 等编号**已被新决策复用** —— **同名并非同一决策，切勿混淆**。
> 检索一律以 [[index/index]] §7 的现行有效表为唯一准绳。

## [2026-09-04 10:00:25] ingest | ADR-026 批次 0~3 + 4.4 落地：MainDeviceControl 按新主控设计重构

- **触发**：用户指令「按照全新构架设计 MainDeviceControl 代码修正方案，然后改造代码」（`@skill:vibecoding-llmwiki`，Phase 0~4）。三项范围裁定：① 覆盖批次 0+1+2+3 + 4.4（业务行为补全 4.1/4.2/4.3/4.5/4.6 留 `// todo`）；② `CommandCore` 指令常量按旧 `DeviceCommand` 语义落字符串；③ **模拟测试模式保留在 `DeviceControlWork`，并新增一条后台线程承载**（用户原话：「我决定在 DeviceControlWork.cs 文件中做一个后台线程来跑模拟测试。后面我将修正模拟测试的其他设计内容，暂时先按原逻辑落位到这」）。
- **Phase 0 侦察结论**：代码库 **100% 旧设计**，ADR-026 落地率 0%。影响半径 = `MainDeviceControl/` 9 文件 + UI 3 文件（`FormMain`/`ILCamPage`/`MonitorCamPage`，均只命中 `SubDeviceWeldStatus.Starting`）+ 1 行 `.csproj`。两组不同 grep pattern 交叉验证，计数吻合。
- **Phase 2 改码（9 个文件）**：
  - **批次 0**：`SubDeviceWeldStatus` 改 7 态（删 `Starting`、加 `NoReset`(0)）；UI 三处中文映射同步；`CommandTable.cs` → `CommandCore.cs`（const string，`.csproj` 同步登记，旧文件用 `os.remove` 删除——**本仓库禁用 `git rm`**）。
  - **批次 1**：`DeviceWorkflowBase` 全面重写，删常驻监听线程机制（`StartRunLoop`/`BeatMs`/`RunLoopPriority`）、`GoStep`/`FailFlow`/`FailReason`/`FailStep`；`WorkStep`→`RunStep`、`WorkStartTime`→`StepWorkTime`(TimeSpan)、`_timeoutMs`(ms)→`TimeOutSeconds`(秒)；新增 17 项契约（5 属性 + 阻塞 10 + 非阻塞 2）；补 `ReadInt`/`ReadDouble`（原 `.ToInt()` 扩展在项目里根本不存在）。5 个子类全部重写/改造落地。
  - **批次 2**：`DeviceControlWork` 重写为 7 常驻线程 + §7.5 九方法；命令三槽 + `IsRobotPoseSafe` + 内部执行步机制整体删除，改 `Queue<string>` + `CommandCore`；新增 `Current`/`Last` 双快照 + `IsReseting`/`IsWorking`/`IsAlarmstop`/`IsCloseWork`；新增模拟后台线程 `thSimTestWork`。
  - **批次 3**：`DeviceStatusWork` 三线程改名 `thIOWork`/`thEMGWork`/`thLightStatusWork` + 三标志位 + `MachineIOWorkOpen()`/`MachineIOWorkClose()`；`EStopMachine`→`EstopMachine`、`EStopCancel`→`EstopCancel` 同步改名。
  - **批次 4.4**：`WeldParamControlWorkflow` 无实体设备，`ConnectOn/Off` 简化为 `_paramReady` bool。
- **踩坑与规避**：① `LineLaserWorkflow.RunStep(Func<bool>)` 与新增 `RunStep` 属性 **CS0102** → 先改名 `RunStepAction`；② `Config.GetElementValue(...).ToInt()` 不存在 → 基类补 `ReadInt`/`ReadDouble`；③ `MonitorCameraWorkflow`/`WeldParamControlWorkflow` 批量插入后残留**悬挂 `#endregion`**（region depth = -1），`GetStepName` 被留在区域外 → 按 `MotionControlWorkflow` 的干净布局复位；④ `CommandCore.cs` 行尾 LF 与同目录其余 CRLF 不一致 → 统一 CRLF 并保留 BOM。
- **Step 2.6 正确性验证**：沙盒无 C# 编译器，用 Python 静态校验器（掩码字符串/注释后）检查 5 类——括号配平 / region 配对 / 基类抽象契约覆盖（13 抽象 + 5 子类全实现）/ 跨类符号存在性 / 禁用符号残留，**全部通过**。**⚠️ 真编译待 Visual Studio。**
- **Phase 3 知识库同步**：重写 [[api/DeviceControlWork]]（7 线程 + 九方法 + 迁移校验 + 遗留待办表）；更新 [[api/DeviceStatusWork]]（线程改名 + `MachineIOWorkOpen/Close` + 三标志位）；**新增 [[api/CommandCore]]**；[[architecture/DeviceControlArchitecture]] §15.2 增「落地状态总表」；`index/index.md` 三条 API 行改写 + 修正过时的 7 态枚举列表（补 `NoReset`、删 `Starting`）。
- **遗留 `// todo`**（属批次 4 未落地）：Preworking 五项检查（4.5）、Working 四路子流程（4.6）、机器人心跳报文、指令交互闭环、温度阈值（4.1）、相机轴控（4.2）、送丝位置检测（4.3）、模拟设计其余内容。清单见 [[api/DeviceControlWork]]「遗留待办」。
- **备份**：改码前打 `AdaWeldSystem_backup_20260904_092111.tar.gz`（96 MB，排除 `bin`/`obj`）。

## [2026-09-03 18:59:16] ingest | 废弃 ADR 页删除 + 全库 ADR 连续重编号 001~036

- **触发**：用户指令「检查知识库，确认废弃的知识库体系文件是删除的，不会再影响我现行的设计。ADR 文件需要重新整理排序数字，不要跳过隔断再编排序号」。三条用户裁定：① 幽灵 ADR → **彻底清除引用，不留墓碑**；② 废弃 ADR 占位 → **移出并删除**；③ 代码注释 → **同步改号**。
- **Phase 0 侦察结论**：41 个 ADR（accepted 36 / deprecated 4 / rejected 1），断号 7 处共 10 个空洞。发现**致命冲突源「幽灵 ADR」**——6 个编号（006/009/033/036/041/042）页早已删除，但全库仍引用 56 处；若直接重排，原 ADR-051→新 041 会与幽灵 041 撞号，产生错误指向。据此锁定**强制执行顺序：清幽灵 → 删废弃页 → 重编号**（顺序不可颠倒）。
- **批次 A+B（wiki 引用清理，110 处）**：6 个幽灵编号 + 5 个待删编号在 wiki 内的全部引用改语义文字，不留可点击墓碑。含 `index/index.md` 14 行超长表格行与 `guides/Project-Tools.md` 3 行；对描述已废机制的片段同步补注「2026-09-03 已清除」，避免误导现行设计。
- **批次 C（删除 5 个废弃 ADR 页）**：`ADR-014 模拟模式贯穿三大流程`、`ADR-020 代码知识图谱辅助代码审查`、`ADR-030 渐进式启动与子页懒加载`、`ADR-047 步骤驱动工作流模型`、`ADR-048 自动运行/手动连接模型`。删页前逐页抢救有效结论：
  - ADR-014 核心理念「模拟是 MODE 不是线程」→ 已由 `guides/Project-Tools.md` 沿革横幅承接；
  - ADR-020「禁用 code-review-graph、回归 Grep」→ 已由 `project/vibecoding-workflow.md` 与 `guides/Project-Tools.md` §1 承接；
  - **ADR-030 新发现**：其声称「保留」的 CameraSelector 简化**确已落地**（代码事实：`CameraSelector.cs` 仅剩 `SelectVirtual()` / `SelectIntelligentLaser()`），但 `api/CameraSelector.md`（date 2026-07-16，早于该决策）**仍记录着 4 个已删方法**，属既有 drift。已在该页顶部加过期横幅承接结论并标注待重写章节；
  - ADR-047/048 机制整体已废，迁移对照保留于 `standards/StepDrivenWorkflow.md`（66 行，11 条对照表）。
- **批次 B3（代码注释，28 处）**：AdaWeldSystem 12 个 .cs 文件的注释引用清理。ADR-038 的 R1~R4 条款统一改称「权责边界」（结论已由现 ADR-023 承接），ADR-037/047/048 编号按语义改写或删除，全部位于注释、不影响逻辑。
- **批次 D（连续重编号）**：36 个 ADR 重排为 **001~036 无断号**。实现要点——① 文件重命名按 old **升序**执行（因 new ≤ old 且映射单调，目标位必定空闲，无需临时名）；② 全库文本替换用 `re.sub` + 函数**一次遍历**（不回溯，杜绝新旧号冲突）。共替换 785 处 / 146 文件；用户级 `~/.workbuddy/skills/vibecoding-llmwiki/SKILL.md` 同步 35 处。
- **批次 B4（补救，关键）**：重编号后校验发现 `skills/SKILL.md` 中**旧幽灵号被"洗白"成合法新号**——旧 006/017/025 的引用（原本指向已删页）经映射后错误指向新的 ADR-004/017/025（实为原 ADR-005/020/034）。已逐条改为语义文字，并删除两条描述已废机制的速查表行（ADR-004 UILight、ADR-047 步骤驱动）；`tools/drift_scan_precise.py` 同步 1 处。两份 SKILL.md 副本均同步。
- **批次 H（index 重排）**：§7 编号说明重写为「001~036 连续」并列出 15 个已失效旧编号（⚠️ 注明 006/017/025/033/036 等编号已被新决策复用，同名不同决策）；§7.1 现行有效表 34 行**按新编号升序重排**（010/013 在 §7.3 部分失效表，符合既有分类）。
- **历史豁免决策**：`logs/log.md`（174 处）与 `raw/`（原档）**不改号** —— 改号破坏可追溯性。改为在 log.md 顶部加「旧→新」对照横幅，并把两处 17 条指向已删页的 `[[链接]]` 转为反引号代码体（保信息、消红链）。
- **Phase 4 Lint（全绿）**：`wiki_audit.py` 红链 0 / 孤儿 0 / 重复 0 / ADR 连续 1~36 无空洞 / 全部已登记 index / 二级子目录 0 / 超大页均带 TOC；`lint_scan.py` 死链 0 / 孤儿 0 / ADR 编号冲突 0 / 外部链接失效 0；`drift_scan_precise.py` 待修正 0 处（16 处 informational 已标注）。
- **⚠️ 本轮重大事故与恢复（须记取）**：执行 `git rm` 删除 5 个 ADR 页时，因 **git 仓库根位于上级目录 `Vicoding管理平台/`，而传入的是相对路径 `wiki/decisions/...`，路径被误解析，导致 `LLMWiki/wiki/` 下 149 个文件被整体删除**。且 `git checkout HEAD` 只能恢复到「最后一次提交」状态，会丢失此前所有**未提交**改动（架构页 1551 行重写、StepDrivenWorkflow 整页废弃、本轮 110 处清理等）。最终用 18:22 创建的 `ADR_renum_backup_20260903_182224.tar.gz`（Python `tarfile` 解压，绕开 Git Bash `tar` 把 `D:` 判为远程主机的陷阱）精确覆盖恢复，核验 ADR 41 / 架构页 1551 行 / StepDrivenWorkflow 66 行全部一致。**教训：本仓库一律不用 git rm 删文件，改用脚本按绝对路径 `os.remove()`；Git Bash 下含盘符的 tar 路径必须换 Python `tarfile`。**

---

## [2026-09-03 17:53:47] ingest | D1/D2 裁定 + 旧指导完完全全清除、ADR 与教训重排（未改码）
- 触发：用户一句三指令——「D1.使用本项目的 XML 文档的写法。子设备 workflow 中增加路径。D2.暂不保留-这部分需要结合 ProductFile 来写，暂时为空，先不实现。你把总结的新架构文档最为唯一架构指导，旧指导请完完全全清除，并重新排知识库的 ADR 和教训、决定。」
- **D1 裁定落地**：勘察源码确认本项目落点是 `AdaWeldSystem/FileOperate/XMLfile.cs` 的 `XdocumentReaderWriter`（`XDocument` / LINQ to XML，默认目录 `BaseDirectory + "Config\XML\"`，`CheckFile` 自动建目录建文件，API 有 `NewXdocument` / `SaveXdocument` / `GetElementValue(name, default)` / `SetElementValue`）；与参考项目 `StationProcess.cs` 的 `XmlReader`/`XmlWriter` 流式 API 是**两套体系**。据此：`LoadConfig`/`SaveConfig` 一律**无参**，**配置路径下沉到各子设备 workflow**（基类只声明契约不持有路径）。架构页新增 **§4.6 子设备配置路径约定** 与 **§16.8 D1 落地模板**（含 `ConfigFileName` 虚属性 + `Config` 惰性属性 + 四条铁律：`SaveConfig()` 末尾必须 `SaveXdocument()`、路径只在子设备内定义、读值走带默认值重载、`XdocumentReaderWriter` 非线程安全故运行期禁止在 `FlowProcess()` 内读写配置）；§4.2 契约表改无参；§16.2 剔除带参重载；§16.7 差异表两项由「待裁定」转「✅ 已裁定」。
- **D2 裁定落地**：`ClearProduct()` **不入基类契约**，5 个子类均不新增该成员，避免空实现污染；待 `ProductFile` 方案确定后另立 ADR。ADR-051 新增 **§6 D1/D2 裁定**章节。
- **旧指导清除（规模）**：脚本扫描 22 个旧设计符号（`GoStep`/`SetStep`/`StartRunLoop`/`BeatMs`/`RunLoopPriority`/`CommandTable`/`_pendingPose`/`_pendingCommand`/`_pendingAbort`/`WorkStep`/`WorkStartTime`/`_timeoutMs`/`ManualOn`/`ManualOff`/`FailFlow`/`FailReason`/`FailStep`/`SimulationWorkflow`/`MapToDeviceState`/`IsRobotPoseSafe` 等），命中 33~34 页，逐页处置：
  - **ADR 转 deprecated（3 个）**：ADR-014（`SimulationWorkflow.cs` 已删，结论失去载体）、ADR-047（`GoStep` 步骤驱动机制整页废止）、ADR-048（`ManualOn/Off` 废止、唯一执行器表述错误、阻塞/非阻塞未区分、`SimulationWorkflow` 前提消失）。三页均加 ⛔ 整页废弃横幅 + 「旧机制 → 处置 → 现行做法」对照表。
  - **ADR 加术语横幅（3 个）**：ADR-044（`IsRobotPoseSafe` 已移除 C3、改态废止 C6）、ADR-049、ADR-003（旧标准引用改指架构页）。
  - **ADR 结论校订（1 个）**：ADR-027 第 3 条「保留 `SimulationWorkflow`」与「后果·负面」末条**已失效**——该类后续已删除，加 ⛔ 注记；其余三条继续有效。
  - **规范页整页废弃（1 页）**：`standards/StepDrivenWorkflow.md` 461 行 → 66 行重写为废弃页，`status: deprecated`，含 11 条「本页旧规定 → 现行做法」对照表 + 「仍然有效的部分」索引指向架构页章节。
  - **规范页加机制横幅（1 页）**：`standards/WorkflowResponsibilityBoundary.md`——R1~R5 与「数据是设备的，进度是流程的」判据继续有效，仅 4 项术语改判（`WorkStep`/`WorkStartTime`/`_timeoutMs`→`RunStep`/`StepWorkTime`/`TimeOutSeconds`(秒)；`GoStep` 删除；子流程不自带线程；私有 `SetStep` 剥离改执行步职责）。
  - **教训页逐坑判定（4 页）**：`StepDrivenWorkflowPitfalls.md` 六坑逐一标注（坑一 ⛔ 机制删除但保留「改步后立即退出本步」思想、坑二 ✅、坑三 ✅ 且风险更高因契约扩到 17 项、坑四 ⛔ 但保留「指令取值全局唯一」思想、坑五 ✅、坑六 ⚠️ 需重新表述）；`StepMemberNameCollision.md` 新增 🔥 实战案例（`LineLaserWorkflow.cs` 已有 `private bool RunStep(Func<bool>, string, string)`，新增 `RunStep` 属性直接触发 **CS0102**，批次 1 第一步必须先改名）；`DeviceControlWorkInheritanceBypass.md`、`DeviceWorkflowDualFlowCallerGate.md` 加机制变更横幅（红线本身继续有效）。
  - **模块/API 页标注（9 页）**：`modules/DeviceControl.md` 执行步层整节改「⛔ 代码现状 vs 新（改码目标）」6 行对照表、`CommandTable.cs` 与 `DeviceWorkflowBase.cs` 节加旧机制横幅、`IsRobotPoseSafe` 门控改删除线；`modules/Safety.md` 门控接入改「直接读 `DeviceStatusWork.Instance.IsSafe`」；`modules/LaserWeldHead.md` `SetStep` 映射更正为 `MapWeldStatus(phase)`；`api/` 5 个子工作流页注入「改造前现状」横幅；`api/DeviceLog.md` 示例 `FailReason` 改 `Alarm(ex)`；`api/DeviceStatusWork.md` 消费方描述更正；`project/overview.md` 目录树标注 `CommandTable.cs → CommandCore.cs`（C3）。
  - **零散历史引用（4 页）**：`guides/Project-Tools.md`（模拟模式章节加 ADR-014/048 已 deprecated 注记）、`guides/Namespace-Compilation.md`（`MapToDeviceState`/`SetStep` 案例加符号沿革注记，根因与检测方法有效）、`lessons/SimulationC-Mode-Interruption.md`（加 `Starting` 已删 + `NoReset`(0) 新增的枚举沿革注记）、`decisions/ADR-013`/`ADR-016`（`SimulationWorkflow` 加删除线注记）。
  - **全库链接清理**：`[[standards/StepDrivenWorkflow]]` 引用统一改为「删除线 + 指向架构页」，共 24 处替换；因两轮替换产生**嵌套删除线自引用**（`~~~~`...`~~ → `...`~~`）23 处，写 `_fix_nested.py` 用 21 条精确子串 PAIRS 定点还原，并顺带纠正失效的旧章节号（§2.2/§五/§七/§九/§十一/第五章/红线 6 → 架构页 §5/§7.2/§15/§16）；余 1 处 MISS（`api/DeviceControlWork.md:127`）用定点 replace 补完并 assert 校验。
- **index 重排**：速查路由「流程怎么推进」改指架构页 §5 + §16.3 并删 `GoStep` 提法；「新增或修改一个工作流」整体重写为指架构页 §4 + §16（列出 17 项契约要点、双流程、阻塞/非阻塞两组、各子流程重写 `SubDeviceLog()`、配置读写无参走 `XdocumentReaderWriter`）；§四规范表 `StepDrivenWorkflow` 标 ⛔ 已整页废弃；§7.1 现行有效表**删 3 行**（ADR-014/047/048）→ §7.3 已废弃表**插 3 行**；修正 ADR-044/049/051 三条摘要。
- **踩坑 2 条**：① Edit 工具报 "File has been modified since read" —— 前一步脚本写入后需重新 Read 再 Edit；② 验证 markdown 引用块时用 `grep -n "^> \*\*..."` 得 0 命中，因 `\>` 在 BRE 中是词尾锚点不是字面量，须改 `grep -nF` 固定串匹配。
- **行尾/BOM 保护（Key Rule 13）**：批量脚本一律按字节读写并保留原 BOM/行尾；Edit 工具实测**能正确保持 CRLF**（核验 6 个文件 CRLF/LF 计数无污染：DeviceLog 91/0、SimulationC 98/0、StepDrivenWorkflowPitfalls 227/0 BOM、Safety 119/0 BOM、WorkflowResponsibilityBoundary 227/0、StepDrivenWorkflow 0/66）。
- **Phase 4 三脚本全绿**：`drift_scan_precise.py` 待修正 0（已标注 16 informational）；`lint_scan.py` 死链 0 / 孤儿 0 / ADR 编号冲突 0 / 外部失效 0（149 页）；`wiki_audit.py` 红链 0 / 孤儿 0 / 重复条目 0 / 二级子目录 0 / 5 个超大页全部带 TOC ✅（架构页 1551 行）。
- 已清理全部临时脚本（`_scan_*.py` / `_patch_*.py` / `_fix_nested.py`）。**未改任何产品代码**（D1/D2 虽已裁定，改码批次未启动；启动前须按 ADR-050 打 `tar.gz` 备份）。

---

## [2026-09-03 17:17:19] ingest | 原档参考实现提取：架构页新增 §16「参考实现与代码模板」（未改码）
- 触发：用户要求「实现代码时须以我给你的代码参考为模板，按其设计重构方案」，并指出**参考文件路径写在 xlsx 里**。
- **我此前的疏漏**：上一轮 dump xlsx 时被 `head -80` 截断，且未注意 R007~R014「主要内容描述」列首行的 `E:\SoftwareGit\...` 路径，**完全没发现原档逐类标注了参考实现**。教训：原档 dump 不可截断，须全量读后再判。
- **原档参考映射（8 个目标类 / 5 个参考文件，全在 `E:\SoftwareGit\HonorMachineTest\PcomDeviceInterface\Work\`）**：`DeviceWorkflowBase.cs`←`Process/StationProcess.cs`（12KB）；`LineLaser`/`LaserWeldHead`/`MonitorCamera`/`WeldParamControl` Workflow ← `Process/RollPressProcess.cs`（103KB）；`MotionControlWorkflow`←`Process/AssemblyProcess.cs`（227KB）；`DeviceControlWork.cs`←`Work/MachineControlWork.cs`（18KB）；`DeviceStatusWork.cs`←`Work/MachineStatusWork.cs`（29KB）。
- 架构页 1035 → **1489 行**，新增 **§16 参考实现与代码模板（改码前必读）**：§16.1 映射表 · §16.2 基类模板 · §16.3 子流程模板 · §16.4 编排层模板 · §16.5 状态层模板 · §16.6 `CommenData`→本项目对应物 · §16.7 参考 vs 原档差异。并在 §4/§5/§7/§9 章首与 §15.2 前加交叉引用。
- **提炼的强制范式**：子流程 **S1~S8**（启用门控 → `switch(RunStep)` → 每 case bool 推进 → **改步必同步刷新步骤计时** → 原语 false 停本步重试 → `ResetProcess()` 为线性阻塞链非步控）；编排 **M1~M9**（线程体五段式 `while(!IsClose)`→非 Running 分支 `Sleep(100)`+`ResetWorkTime()`+`continue`→`FlowProcess()`→`Sleep(10)`；复位走一次性 `Task`+两步机；`StartMachine()` 只切状态）；状态 **T1~T6**（线程进出成对维护标志位、急停边沿触发、三色灯 `switch(CurrentStatus)`）。
- **关键印证**：参考 `CommenData.CurrentStatus` 的 setter 自动把旧值存入 `LastStatus` —— 正好是原档「私用的 Current 和 Last 的 `MainDeviceStatus`」的代码模板；参考超时用全局 `CommenData.CylinderMoveTimeOut`(ms)，原档提升为基类属性 `TimeOutSeconds`(**秒**)，存在单位换算风险。
- **新增待裁定 D1/D2**：D1 `LoadConfig`/`SaveConfig` 是否带 `XmlReader`/`XmlWriter`（参考带参、原档无参）；D2 是否保留 `ClearProduct()` 清料抽象成员（参考有、原档未列，保留则 5 子类各多一实现）。
- 同步：ADR-051 新增**决策条目 5**（参考实现模板）+ D1/D2 登记；index 架构页摘要加 §16（行数 1035→约 1490）。
- Phase 4 三脚本全绿：drift 待修正 0（已标注 16 informational）/ lint_scan 四项 0 / wiki_audit 架构页 1488 行已带 TOC。行尾 LF 未污染。**反查**：新增约 25 个参考文件名全部包在反引号内，裸漏 .cs 引用 0，未掩盖真实漂移。
- 未改任何代码。

---

## [2026-09-03 16:47:39] ingest | ADR-051 裁定落地：架构页按「完全重构」整体重写（未改码）
- 触发：用户对 C1~C7 逐条裁定，并确立**元原则**——「新结构文档为全新设计和细化，不要带入老旧文档的设计思维，不是对旧文档的补充，是完全的重构」。
- C4 纠错：我此前把 `InitializeOn/InitializeOff` 与 `ConnectOn/ConnectOff` 判为「4 个入口语义重叠」是**读档不透**。原档 R007 明确分两组——**全阻塞流程**（`InitializeOn` 同步等待 / `InitializeOff` 异步等待）与**非阻塞流程**（`ConnectOn`/`ConnectOff` 非常驻后台线程、动作即退出释放）。二者**并存不重叠**：前者用于初始化/停机要确认成败，后者用于运行期重连不阻塞编排线程。
- 架构页整体重写（990 → 1035 行）：页首新增「已清除的旧设计 → 取代它的新设计」索引表；§1 三态枚举按原档真值（`MainDeviceStatus` 值由原档显式给定，非隐式推导）；§2 目录 + 继承链 + **每个子流程各自重写 `SubDeviceLog()`**；§3.1 `CommandCore` const string + **不再监控 pose**；§4 基类契约由「6 项」改为 **17 项**（5 属性 + 10 阻塞 + 2 非阻塞）+ **§4.4 阻塞/非阻塞职责边界**；§5 由 ADR-047 的 `GoStep` 改为 **`RunStep` bool 推进 + `ResetWorkTime` 超时**；§6.2 五子工作流差异化职责；§7.2 **7 条常驻线程**（5 子设备 + 2 通讯，含 `Sleep(10)`/`Sleep(100)` 防空转）；§7.4 Comm 与 ControlWork 职责边界；§7.5 九个公共方法；§15 由「冲突裁定表」改为**落地清单（五批次改码 Plan）**。
- 连带修正 §8~§14 中三处与新裁定冲突的残留：`IsRobotPoseSafe()` 移除（改直接读 `DeviceStatusWork.Instance.IsSafe`，`IsSafe` 是本机安全 IO 与 pose 无关）、`EvaluateInitializationResult()` 初始化链改为原档三步、§12 Comm 行改为「提供方法和管理 / ControlWork 是使用方」、`DeviceStatusWork` 命名对照由「待统一」改为「已裁定」、§14 删除「代码与本页冲突时以代码为准」（违反 ADR-050 原档优先）。
- ADR-051 由 proposed 转 **accepted**，写入七条裁定 + 元原则 + 受影响 ADR 处置（ADR-047 部分再被取代 / ADR-048 表述修正 / ADR-049 枚举更新）。
- 三个 ADR 加取代横幅；`modules/DeviceControl.md`、`api/DeviceControlWork.md`、`api/DeviceStatusWork.md` 横幅改「已裁定」并补成员清单；`index/index.md` ADR-051 由 §7.2 待决移入 §7.1 现行有效，§7.2 复位为「当前无待决 ADR」。
- 未改任何产品代码。改码需按 §15.2 五批次推进，批次 1 与批次 2 必须同批（删基类线程与加编排线程不能留中间态）。

## [2026-09-03 16:06:14] lint | Phase 4 收尾：修复 drift_scan_precise.py 双重缺陷，三脚本全绿（待修正 9 → 0）
- 触发：Phase 0 沉淀后在架构页 §15 冲突表写入原档命名，Phase 4 扫描报出「待修正 9 处」。
- 诊断一（掩码缺失）：坑五修的 `mask_code()` 只加进了 `wiki_audit.py` / `lint_scan.py`，
  `drift_scan_precise.py` **从未实现**。三个脚本各自实现链接解析，修的时候漏了一个。
  → 移植同一份 `mask_code()`，扫描改为 `cs_ref_re.finditer(mask_code(line))`。
- 诊断二（前缀只匹配一级目录）：`any(p + fname in line for p in EXTERNAL_PREFIXES)`
  对 `PcomDeviceInterface/Work/Process/RollPressProcess.cs` 失效（中间还有两级目录）。
  → 新增 `is_external_ref()`，先取紧邻文件名的完整路径前缀再判 `startswith`。
- 诊断三（原档命名无归属）：新增第四类分诊 `RAW_SPEC_NAMES`
  （`CommandCore.cs` / `RollPressProcess.cs` / `AssemblyProcess.cs` / `DeviceStateMachineBase.cs`），
  作为正文裸写原档名时的兜底豁免。脚本 docstring 同步补第 4 类口径说明。
- **安全网验证**（防「待修正 0 处」只是把问题藏起来）：已标注数 119 → 16，
  反查被掩码的名字——反引号内引用 .cs 名去重 181 个，代码库不存在的 62 个，
  逐个人工分类确认全部属于「历史名（已登记且页面已加注）/ 占位名（`X.cs`、`XxxWorkflow.cs`、
  `Designer.cs`）/ 外部 SDK（`Zmcaux.cs`、`MVCamera.cs`、`Form1.cs`）/ 原档命名」四类，
  **无真实漂移被掩盖**。
- 沉淀：`lessons/WikiDriftCorrectionPitfalls.md` 新增「坑六」，含双重修复代码、
  外部前缀 bug 修法，以及「掩码是安全网不是免检证」的反向抽查要求。
- 三脚本终态：`wiki_audit.py` 红链 0 / 孤儿页 0 / 重复 0 / 无二级子目录 / 5 个超大页均已加 TOC；
  `lint_scan.py` 四项全 0；`drift_scan_precise.py` 待修正 0 处 -> 通过。
- 未改任何产品代码（ADR-050 §3：冲突未裁定前 AI 不得单方改码）。

## [2026-09-03 15:58:57] ingest | 原档 9-03 细化沉淀：架构原档 3→2、基类 13 契约、Preworking/Working 检查清单，产出 7 冲突 + 15 待实现（ADR-051 proposed）
- 来源：用户指令「在知识库 Raw 的构架文件夹下，我放入今天新细化的构架方案，你查看这两份文件，沉淀到知识生成新架构文档然后做代码修改 Plan」（VibeCoding Phase 0 + Phase 3 前置 + Phase 1）
- **原档变更事实核对**（`git status` + 与 HEAD 版逐单元格 diff）：
  1. `主控设计.xlsx` **修改**（15:37）：Sheet 由 `Sheet1` 改名 `主控程序文件层级设计`，列「内容/备注」→「主要内容描述/实现」，行数 13→14
  2. `激光焊接系统业务流程图.pdf` **新增**（15:32，226 KB，**含文本层**，单页 928 字）
  3. 删除：`焊接设备工作流程图.pdf`、`焊接系统工作流程业务流向图.pdf`、`page_0.png`、`业务流向图_overview.png`、`业务流向图_page0.png`
  4. **原档集合收敛 3 → 2**（ADR-050 §1 同步更新）
- **原档一 `主控设计.xlsx` 提取结论**：
  - 新增 `CommandCore`（`ReciveCommand` 接受指令 / `SendCommand` 发送指令，**const string** 固定，不允许自定义赋值）
  - `SubDeviceWeldStatus` **删 `Starting`、新增 `NoReset`**（值 0，余值顺延）；原档拼写 `Stanby` 按正确英文落地
  - `DeviceWorkflowBase` 由 6 抽象契约**扩为 13 项**：属性 `Tag`/`IsEnable`/`RunStep`/`StepWorkTime`/`TimeOutSeconds` + 新增 `InitializeOn`(同步)/`InitializeOff`(异步)/`SubDeviceLog`/`LoadConfig`/`SaveConfig`/`WledStatusTrans`；`ConnectOff` 返回值 void→bool
  - 5 子工作流**差异化职责**：焊接头=温度阈值 / 监控=轴控制 / 运控=送丝位置+焊接质量阈值 / 工艺=无实体设备、连接断开走 bool 变量
  - `DeviceControlWork` **5 子设备线程 + 2 通讯线程（心跳/指令）** + `MachineFlowWorkOpen`/`MachineCommandWorkOpen`/`ClearMachine`/`MachineStatusTrans`/`WeldStatusTrans`/`CommWork`/`OnCommRecived`/`CommCommandWork`
  - `DeviceStatusWork` 三线程 `thIOWork`/`thEMGWork`/`thLightStatusWork` + `MachineIOWorkOpen` + 三循环标志位
- **原档二 `激光焊接系统业务流程图.pdf` 提取结论**（pypdf 全文提取，无需渲染）：业务主链 = 上电（5×Connect On + 通讯 Open + Running/Alarm IO Work + 机器人服务器 Command）→ 三失败分支（Initialize/Reset/Pre-Working Fail，均→Alarm）→ ResetMachine → Preworking 五项运行检查 → Working 四路焊接子流程 → 三终止分支（手动终止→Stop / 异常终止→Robot Alarm / 焊接完成→StopMachine:Complete）→ 报警判断（故障树和代码）；旁路 EMG STOP → 子设备停机锁止
- **更新 Wiki 页面**：
  1. `architecture/DeviceControlArchitecture.md`（约 950 行）：页头原档 3→2 与分工表；§1.2 枚举 `Starting`→`NoReset`；**新增 §3.1 机器人指令表**；§4.1 改为「现行 6 项 / 原档 13 项」落地对照表；**新增 §6.1 五子工作流差异化职责**；**新增 §7.3.1 原档 5+2 线程模型（含与 ADR-047 冲突说明）**；§7.6 按新原档重写业务主链；**新增 §7.7 Preworking 五项运行检查**、**§7.8 Working 四路焊接子流程**；§9 补 `DeviceStatusWork` 原档命名对照；**新增 §15 待落地项与冲突裁定（C1~C7 + P1~P15）**；§14 补原档驱动流程
  2. `decisions/ADR-028-ArchitectureRawSource.md`：原档 3→2、判读方式改为 pypdf 文本提取、同步流程加入「冲突交用户裁定」环节
  3. **新增 `decisions/ADR-029-RawDesignRefinement20260903.md`**（status: proposed）
  4. `modules/DeviceControl.md`、`api/DeviceControlWork.md`、`api/DeviceStatusWork.md`：补原档细化指引
  5. `index/index.md`：页头原档说明、§十来源索引（3 行→2 行）、§七 ADR 表新增 7.2 待决条目、目录计数 40→41、架构页摘要、新增速查路由行
  6. **勘误**：`api/DeviceControlWork.md` 位置由 `MainDeviceControl/DeviceWorkflow/DeviceControlWork.cs` 更正为 `MainDeviceControl/DeviceControlWork.cs`
- **7 项冲突待用户裁定（未裁定不得改码）**：C1 子设备 `FlowProcess` 驱动线程归属（原档主控 5 线程 vs ADR-047 基类监听线程）· C2 `Starting`→`NoReset`（10 处引用）· C3 `CommandCore` const string vs `CommandTable` const int · C4 `InitializeOn/Off` 与 `Initialize/ConnectOn/Off` 职责重叠 · C5 通讯连接是否纳入 `InitializeMachine` · C6 `RunStep` 命名（与 `LineLaserWorkflow.RunStep()` 私有方法 CS0102 冲突）· C7 `private abstract void SubDeviceLog()` 语法不可实现
- **15 项无冲突待实现**（P1~P15，架构页 §15.2）：`ClearMachine`/`WeldStatusTrans`/`MachineStatusTrans`/`MachineFlowWorkOpen`/`MachineCommandWorkOpen`/心跳线程/状态快照/`LoadConfig`+`SaveConfig`/`ConnectOff` 改 bool/焊接头温度阈值/监控轴控制/运控送丝位置+焊接质量阈值/工艺流 bool 简化/**Preworking 五项检查**/**Working 四路子流程补全**
- **未改任何代码**：按 ADR-050 §3 原档与代码冲突须用户裁定，AI 不单方改码；代码修改 Plan 已产出待确认
- 矛盾检测：无新增矛盾（原档变更均登记为「待落地」而非「已生效」，架构页 §15 为唯一登记处）

---

## [2026-09-02 22:41:12] cleanup | 旧架构清零：删 8 页旧架构文档 + 全库改链 + 现行页旧术语清理（ADR-049 三态模型为真源）
- 来源：用户指令「先去检查知识库的代码架构要求，把指向旧架构内容删掉，只保留新架构设计」+「对于新架构我原先的要求是通过 raw 抽象出你理解的架构设计到知识库架构设计中。删掉旧架构，只保留新架构的理解」
- **事实基线确认**（代码为准）：`MainDeviceControl/` 现为 10 个 `.cs`——`DeviceControlWork.cs` / `DeviceStatusWork.cs` / `DeviceStateApiCore/{CommandTable,DeviceStateBase,DeviceWorkflowBase}.cs` / `DeviceWorkflow/{LineLaser,MonitorCamera,MotionControl,WeldParamControl,LaserWeldHead}Workflow.cs`。旧符号（`WorkflowStateBase` / `MainDeviceWorkflow` / `SafetyWorkflow` / `SimulationWorkflow` / `DeviceStateMachine` / `SafetyFlow` / `SafetyInterlock` / `MotionControlStateMachine` / `LaserCamBoxTrackingWorkflow` / 泛型 `WorkflowStepChangedEventArgs<TStep>`）代码内 0 命中。架构页 §1/§3/§4 与 `raw/architecture/主控设计.xlsx` 已一致，**无架构内容改写，纯旧架构删除**
- **删除 8 页**（移至 `LLMWiki/_trash_20260902/`，移出 `wiki/` 扫描树）：
  1. 旧架构 ADR 6 条：027-WorkflowStateFileConsolidation / 032-UnifiedInitStateMachine / 033-V3SystemArchitecture / 036-SafetyModuleConsolidation / 041-MainDeviceControlArchitecture / 042-WorkflowStateBaseGeneric
  2. 占位页 2 个：`api/SimulationWorkflow.md`（墓碑，入链 15）、`modules/Workflow.md`（重定向存根，入链 27）
  - `index.md` §7.1/§7.3 同步删行，编号说明区标注 6 条空洞「编号不再回收，非缺失」，仍有效结论并入 ADR-049 + `architecture/DeviceControlArchitecture`
- **重命名 2 个 API 页**：`api/MainDeviceWorkflow.md` → `api/DeviceControlWork.md`、`api/SafetyWorkflow.md` → `api/DeviceStatusWork.md`（内容本就述新类，仅文件名对齐）
- **全库改链 52 处**（括号内为命中文件数）：api/MainDeviceWorkflow → api/DeviceControlWork（13）、api/SafetyWorkflow → api/DeviceStatusWork（7）、api/SimulationWorkflow → api/DeviceControlWork（8）、modules/Workflow → modules/DeviceControl（24）；已删 ADR 链接降级为纯文本（ADR-037 ×11 / 042 ×6 / 036 ×2）避免红链。**红链 0**
- **现行页旧架构术语清理**（100+ 处，逐处人工判读，非盲替换）：
  - `architecture/DeviceControlArchitecture.md`：删 `SafetyWorkflow` 更名叙事；`MainDeviceWorkflow`→`DeviceControlWork`；依赖环说明 `FaultRecord.State` 四态→`SubDeviceWeldStatus` 七态；模块表「设备态/流程态基类 + 7 个工作流」→「三态基类 + 5 子工作流 + 2 管控类」；UI 接入行→三态属性
  - `api/FaultRecoveryManager.md` + `modules/ProductFileManager.md`：`DeviceState`（四态）→ `SubDeviceWeldStatus`（七态），默认值 `Disconnect`→`Standby`；消费方名单 `SafetyWorkflow`/`MainDeviceWorkflow` → `DeviceStatusWork`/`DeviceControlWork`
  - `api/GlobalCommData.md`：**删代码块中已不存在的 `LineLaserWorkflowState` / `WorkflowSignalCode` / 泛型 `WorkflowStepChangedEventArgs<TStep>`**（实测 `Comm/SystemComm.cs` 现仅 `MessageType`/`MessageLevel`/`OperateLevel`/`MessageArgs`）；三处「系统状态由 LineLaserWorkflowState 管理」→ 三态模型
  - `modules/MotionControl.md`：继承改**非泛型** `DeviceWorkflowBase`；`MapToDeviceState` 四态→`MapWeldStatus` 七态；删除 `MotionControlWorkflowState`/`MotionControlStateChangedEventArgs`（实测代码中不存在）；`SimulationWorkflow`→`DeviceControlWork`；`LaserCamBoxTrackingWorkflow`→`MotionControlWorkflow`
  - `modules/MonitorCam.md` + `modules/WeldParamControl.md`：阶段枚举改「私有、内联本文件、经 MapWeldStatus 映射」，映射表指向 `architecture/DeviceControlArchitecture` §6 单一维护点；`MonitorCam` 删已删的 `Displaying` 态
  - `modules/DeviceControl.md` / `modules/Safety.md` / `project/overview.md`：目录树与统计对齐三态模型
  - `modules/UIDesign.md` + `modules/Comm.md` + `api/MainPage.md`：`MainDeviceThread`→`DeviceControlWork`；已删目录依赖（`Workflow`/`DeviceStateMachine.API`）→ `MainDeviceControl.DeviceWorkflow` / `.DeviceState`
  - `standards/WorkflowResponsibilityBoundary.md`：**整页术语对齐 ADR-049**——白名单第 4 条改「推进私有阶段」；R3 重写为三态事件契约（`WeldStatusChanged`/`StateSwitched`/`StatusChanged` + 参数字段名 `OldStatus`/`NewStatus`）；R5 改「私有阶段枚举」；审查清单新增「禁手工 `WeldStatus=`/`State=`/`Status=` 赋值」；UI 范式示例改用 `WeldStatusChangedEventArgs`
  - `people/MotionControlSpecialist.md` + `people/GeneralTechSpecialist.md`：目录树/职责中的 `DeviceStateMachine` → `DeviceStateBase` 三态
  - `guides/Namespace-Compilation.md`：**更正 using 对照表**（旧 `DeviceState`→`AdaWeldSystem.DeviceStateMachine` 已失效，改为三态枚举 + 事件参数 + `DeviceWorkflowBase` 的现行命名空间，并显式标注「物理目录 `DeviceStateApiCore/` ≠ 命名空间」）；工作流实测清单 7→5 子工作流 + 2 管控类
  - `guides/Project-Tools.md` / `guides/WinForms-UI-Threading.md`：`SimulationWorkflow`→`DeviceControlWork` 现行 API 名；`State == LineLaserWorkflowState.Standby` 示例→`WeldStatus == SubDeviceWeldStatus.Standby`；UI 订阅入口补三态契约
- **历史页处理原则**：`decisions/` ADR 保留原文（决策史不可篡改），在页顶加「已被 ADR-049 取代 + 现行类名」注记——ADR-014 / 037 / 043 / 044 / 046 / 048；`lessons/` 同样加注记（StepDrivenWorkflowPitfalls / SimulationC-Mode-Interruption / StepMemberNameCollision / StateMachine-DoubleTransition / FaultRecoveryDeviceKey / CSharp-Language-Pitfalls），保留通用教训并说明在新模型下是否仍成立
- **路径勘误**：`DeviceStatusWork.cs` 实际位于 `MainDeviceControl/` 根（**不在 `DeviceWorkflow/`**），5 个 wiki 页 + 1 个 log 行已批量修正；命名空间仍为 `AdaWeldSystem.MainDeviceControl.DeviceWorkflow`（目录 ≠ 命名空间）
- **代码侧**：`AdaWeldSystem.csproj` 第 352-354 行注释更新（`MainDeviceControl\DeviceWorkflow\SafetyWorkflow.cs` → `MainDeviceControl\DeviceStatusWork.cs` 三线程 + `DeviceControlWork.cs` 整机主控），与 csproj 实际 Compile 条目（147-156 行）一致
- 备份：`LLMWiki_backup_20260902_221241.tar.gz`（518,156 bytes，含 `wiki/` 全量 + `AGENTS.md`）
- 验证：`tools/wiki_audit.py` 全绿（红链 0 / 孤儿页 0 / index 重复行 0）

---

## [2026-09-02 20:43:06] ingest | 业务流向图原档沉淀（ADR-050 原档 2→3）+ 架构页业务状态流章节 + ResetMachine/StopMachine 级联代码修正
- 来源：用户指令「沉淀焊接系统工作流程业务流向图.pdf 到知识库。全盘理解三份架构图模式。然后修正知识库：全量删除旧结构，新架构兼容并蓄的整合。然后对代码进行修正」
- 原档：`raw/architecture/` 新增 `焊接系统工作流程业务流向图.pdf`（业务状态流：NoReset→Reseting→Reset OK→Running→PreWorking/WeldWorking→Stop/Alarm 主链 + 通讯/命令-IO-Pose/EMG-故障树三条横向通道）+ 渲染辅助 `业务流向图_overview.png`；清理临时 tile PNG；ADR-050 原档清单 2→3
- 架构页：页头新增三份原档分工表（xlsx=名词 / 流程图=动词 / 业务流向图=剧本）；§7.5 契约表对齐代码（ResetMachine=在位检测阻断+级联 ResetProcess×5；StopMachine=级联 ClearStatus×5；ClearAlarm=仅清标志无级联）；新增 §7.6 业务状态流主链与两条语义映射（Reset OK≡Stop、Running 业务语义分层）+ StartMachine 疑似级联存疑记录
- 代码（DeviceControlWork.cs，已提交 f51ce43 待推）：新增 IsRobotReachable / CascadeResetProcess / CascadeClearStatus；ResetMachine 在位检测不通过→Alarm+RecordFault(ROBOT_OFFLINE)+阻断；StopMachine 停线程后级联 ClearStatus 再断开。csharp_review 0 error（剩 2 处 Thread.Sleep 豁免）
- 用户决策：在位检测失败→阻断复位；StartMachine 疑似级联→暂不实现仅记录；StopMachine 级联→实现
- 待办：推送 GitHub 挂起（本机 TLS 劫持 + SSH 公钥未注册，等用户注册后走 ssh.github.com:443）

---

## [2026-09-02 17:07:03] ingest | KB 冲突/遗留/重复清理 + MainDeviceControl 代码精简（ADR-028/049 复检）
- 来源：用户指令「检查知识库消除冲突、删除遗留、合并重复；复检 MainDeviceControl 实现是否符合最新架构并精简代码和注释」
- KB 清理（12 页，历史语境 decisions/ 与墓碑页按约定保留）：
  1. `architecture/DeviceControlArchitecture.md`：§11.4 调用链修正（模拟链 → `DeviceControlWork.SimTestMode`；初始化链 → `InitializeMachine()`；删 `MainDeviceWorkflow.InitializeAllSubDevices`）+ §13 UI 接入重写为三态模型（删「四态 DeviceState」表述）
  2. `api/FormMain.md`：关键方法表整段对齐真实代码（`StatusChanged`/`MainDeviceStatus`/`WeldStatusChanged`/`SubDeviceWeldStatus`，删 `MainDeviceFlowState`/`MainStateMachine`/`MainDeviceThread` 残留；依赖列表删已删命名空间）
  3. `guides/WinForms-UI-Threading.md`：FormMain 集成示例改 `InitializeMachine()`/`StartMachine()`，约束段同步
  4. `lessons/DeviceWorkflowDualFlowCallerGate.md`：整页重写，入口契约 `ManualOn/ManualOff` → `ConnectOn()/ConnectOff()`（ADR-049）
  5. `modules/Comm.md`：四态表述 → 三态模型
  6. `modules/LaserWeldHead.md`：级联调用方 → `DeviceControlWork.InitializeMachine()`；状态表述 → 三态
  7. `api/FaultRecoveryManager.md` + `lessons/FaultRecoveryDeviceKey.md`：消费方名单对齐现状（`DeviceStatusWork`/`DeviceControlWork`）
  8. `lessons/StepMemberNameCollision.md` + `StepDrivenWorkflowPitfalls.md`：实例类名 → `DeviceControlWork`（原 MainDeviceWorkflow 注记）
  9. `index/index.md`：DualFlowCallerGate 摘要更新为 ConnectOn/ConnectOff
  10. `api/SimulationWorkflow.md`：墓碑页现行真相源 → `DeviceControlWork`（ADR-049）
  11. `api/LineLaserWorkflow.md` + `api/MonitorCameraWorkflow.md`：删除 5 个已删死属性代码行
  12. `modules/DeviceControl.md`：补 2026-09-02 代码精简注记
- 勘误：前轮判定 AGENTS.md「4 段乱码」经字节级 UTF-8 解码复检为**误报**（解码通过、无替换符），未做改动
- 代码精简（MainDeviceControl 10 文件，备份 `AdaWeldSystem_backup_20260902_164353.tar.gz`）：
  1. 删 5 死属性（外部全库 grep + 文件内字段级 grep 双确认；字段 `_maxConsecutiveFailures` 等内部在用保留）
  2. 31 处 summary 精简（≤20 字只说做什么）+ 5 处补 `<param>`/`<returns>`
  3. 成员顺序修正 3 文件（DeviceControlWork：`_simLineLaserPending`/`OnSimLineLaserStateChanged`/`WaitChildConnected`/`EvaluateInitializationResult` 归位私有区；LineLaser：`ConnectWorker`/`DisconnectWorker`）
  4. csharp_review.py 终扫：10 文件 **0 error**，警告 35+ → **6 处 Thread.Sleep 全部豁免**（RunLoop×2/IOWork/EMGWork/StatusWork 常驻轮询节拍属 ADR-047 设计本意 + WaitChildConnected 有界等待）——**非归零，是豁免归零**
- 待办移交：本环境无法编译，最终以 VS 编译为准；`modules/WeldParamControl.md` 的 `MaxConsecutiveFailures` 属 `WeldProcess` 真实成员，非死属性

---

## [2026-09-02 16:31:02] feature | 架构原档沉淀 raw/architecture + ADR-050 + 代码引用静态检测收口
- 来源：用户指令「将架构设计 xlsx 和 pdf 沉淀到知识库原档，后续只改这两份文件更新架构」+「检测代码文件位置修改后的内部引用缺失」
- 原档沉淀（ADR-050）：
  1. `raw/architecture/` 新建：`主控设计.xlsx`（自工作区根复制）+ `焊接设备工作流程图.pdf`（自 `D:\飞书文档\` 复制）+ `page_0.png`（pymupdf 150dpi 渲染辅助图，PDF 无文本层）
  2. `decisions/ADR-028-ArchitectureRawSource.md`（新建）：原档 = 架构唯一修改入口；更新流程 = 改原档 → AI 同步架构页 → wiki_audit；冲突裁决 = 原档 > 架构页 > 源码注释
  3. `architecture/DeviceControlArchitecture.md`：页头 source 字段 + 原档入口声明（正文三态模型重写本轮确认完整：§1 三态 / §2 目录树与 xlsx+磁盘一致 / §3 三态基座 / §4 六抽象契约 / §7 DeviceControlWork / §9 DeviceStatusWork 三线程）
  4. `index/index.md`：最后更新行 + raw 原档区 2 行 + ADR-050 入 §7.1 表 + 编号说明 001~050 共 46 条
- ADR 语义修正：
  - `ADR-049` frontmatter `supersedes: [041,042,047,048]`→`[041,042]`，tags 去取代 047/048；头部改注「ADR-047 步骤驱动沿用（三件套由新基类承载）/ ADR-048 部分取代（ConnectOn/ConnectOff 取代 ManualOn/ManualOff）」
  - `index` ADR-048 行加 ⚠️ 部分取代横幅；L64 工作流路由注记对齐
- 代码引用检测（用户已自行修正文件位置，本轮静态复核 8 项全过）：csproj↔磁盘 150/150、HintPath 59/59、using 有效性 0 无效、四态 DeviceState 删净、三态枚举在位、5 workflow 抽象契约 35/35、Instance 成员对账 0 缺失、无重复类定义；**本环境无法编译，最终以 VS 编译为准**
- 备份：`LLMWiki_backup_20260902_*.tar.gz`（改动前）

- 来源：用户确认「全部补齐 4 项」（前轮纯 KB 修正计划残余）
- 修改 KB 页：
  1. `standards/StepDrivenWorkflow.md`：三层融合表「设备四态 DeviceState / 各工作流 TStep」→「连接态 SubDeviceState / 焊接过程态 SubDeviceWeldStatus / 主设备运行态 MainDeviceStatus / 执行步」四层；§1.1 痛点示例 MainDeviceFlowState→旧枚举、MainDeviceWorkflow→DeviceControlWork 前身；红线 2「设备四态+MapToDeviceState」→「三态+SetState/SetWeldStatus/SetStatus，MapToDeviceState 已废弃」；范式 B/§十二反例 SetStep(Alarm)→SetWeldStatus(SubDeviceWeldStatus.ErrorAborted)；落地清单 MainDeviceWorkflow.cs→DeviceControlWork.cs、SafetyWorkflow.cs→DeviceStatusWork.cs（三线程非步骤驱动）；审查清单「四态映射」→「状态映射」
  2. `api/LaserWeldHeadWorkflow.md`（新建）：对齐 LaserWeldHeadWorkflow.cs 真实 API——非泛型 DeviceWorkflowBase、单例、骨架期 IsRunLoopActive=false、私有 _phase→SetWeldStatus(MapWeldStatus)、连接契约 ConnectOn/ConnectOff/ResetProcess/ClearStatus
  3. `api/MainDeviceWorkflow.md`：已于前轮重写为 DeviceControlWork 公开面（本会话确认无需改动）
  4. `index/index.md`：清除四态/泛型/MainDeviceWorkflow/SafetyWorkflow 残留（architecture/modules/DeviceControl/modules/Safety/api/*/lessons/*/standards 摘要同步三态+非泛型）；新增 [[api/LaserWeldHeadWorkflow]] 链接；ADR-049 补入 7.1（原仅引用未入表），ADR-037/042 加 ⚠️ 取代横幅（核心四态+泛型已被 ADR-049 取代），ADR-044/047 同步三态命名；表头「取代 ADR-037/042/047/048」修正为「取代 ADR-037/042」（步骤驱动 ADR-047 / 自动手动 ADR-048 仍现行有效）
- 顺带修复：`modules/DeviceControl.md` 红链 `ADR-028-DisposeFullCoverage`→`ADR-020-DisposePatternFullCoverage`；孤儿页 `lessons/DeviceWorkflowDualFlowCallerGate` 补入 index lessons 表（内容仍含 MainDeviceWorkflow/设备四态旧词，待后续刷新）
- 矛盾检测：无（旧 SafetyWorkflow/MonitorLoop/四态描述已全部替换或加取代横幅）
- wiki_audit.py 全绿（红链 0 · 孤儿页 0 · 重复行 0 · ADR 1~49 连续、空洞 [6,9,23,24] · 无二级子目录 · 无过小分类 · 架构页 623 行已含 TOC）

---

## [2026-09-02 12:43:30] feature | DeviceStatusWork 三线程重设计（按 xlsx + PDF 架构图，代码重设计轮次）
- 来源：用户重定向（纠正前轮「IOWork/EMGWork/StatusWork 仅 PDF 概念标签、代码无需改」误判）+ 最终指令「舍弃旧方法，完全按 xlsx 要求和 PDF 架构图去设计」
- 权威 spec：主控设计.xlsx Sheet1（DeviceStatusWork.cs = 安全/IO/状态管控，参考 E:\SoftwareGit\HonorMachineTest\PcomDeviceInterface\MachineStatusWork.cs）+ PDF 架构图 DeviceStatusWork 泳道三标签
- 代码：DeviceStatusWork.cs 由 MonitorLoop/StartMonitor 单线程模型重写为 IOWork(AboveNormal,互锁检查→Alarm) + EMGWork(Highest,急停→EStop) + StatusWork(Normal,反射三色灯) 三线程；SafetyFlow 新增三色灯 StatusLamp* 地址；SafetyInterlockChecker.CheckPlc 移除急停位（急停专责移交 EMGWork，避免 Alarm/EStop 互翻）
- 接线：DeviceControlWork.StartMachine() 拉起 DeviceStatusWork.Instance.StartWork()；StopMachine()/Dispose() 调 CloseWork()；IsSafe 仍仅 IsRobotPoseSafe(L535) 消费
- 权责边界（ADR-043）：安全类不自治设备态，统一经 DeviceControlWork.ReportAlarm/EStopMachine/EStopCancel/ReportAlarmCleared 变更主设备态
- 修改代码文件：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/DeviceStatusWork.cs、DeviceControlWork.cs
- 更新 Wiki 页面：architecture/DeviceControlArchitecture.md（§9.1 整段重写 + 目录树 + §7 + 安全链）、api/SafetyWorkflow.md（全量重写三线程）、modules/Safety.md、modules/DeviceControl.md
- 交叉验证：grep 无 MonitorLoop/StartMonitor/StopMonitor 残留；region 配平 11/11 与 9/9；csharp_review.py 两文件均 0 错误
- 矛盾检测：无（旧 SafetyWorkflow/MonitorLoop 描述已全部替换）
- wiki_audit.py 全绿（ADR 1~49 连续、架构页 623 行已含 TOC、无重复/子目录/过小分类）

---

## [2026-09-02 02:33:23] fix | 修复 MainPage 线激光设备开关按钮越权直驱 Start/Stop/Reset
- 来源：Bug 修复（用户指出界面线激光开关按钮调 ToggleLineLaserConnection 完全错误）
- 问题：MainPage.cs 的 ToggleLineLaserConnection() 直接调 LineLaserWorkflow.Instance 的 Start()/Stop()/Reset() 子类便捷方法，三重违规：
  1. 调子类便捷方法而非 ManualOn/ManualOff（入口红线）
  2. 语义错误——Start/Stop 是「开激光跑焊接流程」，非「连接设备」（与设备开关与流程无关的约定矛盾）
  3. MainPage 属主设备边界，线激光非其所属设备，越权直驱
- 修复：
  1. ToggleLineLaserConnection() 改为基于设备四态 DeviceState 判断：Disconnect→ManualOn，Connect/Work→ManualOff，Alarm→提示复位
  2. IsLineLaserRunning()（徽标判定）从 Step==Starting/Working 改为 State==Connect/Work（连接语义）
  3. MainPage.cs 新增 using AdaWeldSystem.MainDeviceControl.DeviceState
- 交叉验证：LineLaserWorkflow.Instance.Start/Stop/Reset/Initialize 全仓 UI 层残留 = 0；_lineLaser.Start/Stop/Reset 仅 MainDeviceWorkflow 内部级联（合法，主设备是线激光归属工作流）
- 修改代码文件：AdaWeldSystem/UIDesign/ControlPage/MainPage.cs
- 更新 Wiki 页面：lessons/DeviceWorkflowDualFlowCallerGate.md（补 MainPage 越权踩坑实录）
- 矛盾检测：无
- wiki_audit.py 全绿

---
- 来源：用户需求（纠正「线程套线程、流程套流程」错误）
- 操作：
  1. `DeviceWorkflowBase.cs`：删除 `ManualStart()`/`ManualStop()`、`ManualConnectThreadBody`、`_manualConnectThread`、`IsManualConnectRunning`、`ManualConnectTimeoutMs`；`ManualOn()`/`ManualOff()` 由 `protected abstract` 升为 **`public abstract`**（UI 开关按钮直调）。
  2. 7 子类 `ManualOn`/`ManualOff` 改 `public override`，内部 `new Thread(...)` 自起后台线程 + `_manualBusy`/`IsManualConnecting` 防重入。LineLaser `ManualOn` 直接 `ConnectManual` 置 Standby（快速连接，不跑 InitializeFlow 四步）。
  3. UI：`ILCamPage`/`FormMain` 的 `ManualStart()/ManualStop()` → `ManualOn()/ManualOff()`；`MainDeviceWorkflow.CascadeDisconnect` 里 `ManualStop()`→`ManualOff()`；`SafetyWorkflow.Start/Stop` 改为直接 `StartMonitor/StopMonitor`。
- 影响：手动连接/断开与流程无关，UI 按钮直调 `ManualOn/ManualOff`；`_runMode` 恒 None（`CanAcceptExternalCommand` 恒 true，正确新语义），`WorkflowRunMode` 机制过时待后续清理。

## [2026-09-02 01:46:55] fix | 删除「手动初始化/反初始化」，改为「手动连接/断开」（ADR-048 二轮修订）
- 来源：用户需求（修正错误设定）
- 操作：
  1. `AdaWeldSystem/MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs`：删除抽象 `BeginManualInit()`/`BeginManualUnInit()`；`ManualOn()`/`ManualOff()` 升为抽象（手动连接/断开唯一契约）；`ManualStart()` 语义改为「手动连接」= 非阻塞起线程调 `ManualOn()` + 超时看门狗（超时反馈 `ShowLog(Info)`「连接超时」，**不置 Alarm**）；`ManualStop()` = 调 `ManualOff()` + 置 Disconnect；字段/方法改名 `_manualInitThread→_manualConnectThread`、`IsManualInitRunning→IsManualConnectRunning`、`ManualInitTimeoutMs→ManualConnectTimeoutMs`、`ManualInitThreadBody→ManualConnectThreadBody`。
  2. 7 个子类（MainDevice/LineLaser/MonitorCamera/MotionControl/WeldParamControl/Safety/LaserWeldHead）删除 `BeginManualInit`/`BeginManualUnInit` 覆盖，实现 `ManualOn`/`ManualOff`（连接/断开）。
  3. `FormMain.cs` 注释修正（手动运行入口→手动连接入口）。
- 新增代码文件：无
- 修改代码文件：DeviceWorkflowBase.cs、7 个子类、FormMain.cs
- 新增 Wiki 页面：无
- 矛盾检测：无（6 抽象方法在 7 子类全部覆盖；wiki_audit 全绿：无红链/孤儿/ADR 连续 1~48）

## [2026-09-01 22:47:47] fix | MotionControlPage 越权直驱非所属设备（线激光）收口：线激光模拟生命周期上收至 MainDeviceWorkflow，UI 页只触发+消费结果（ADR-048 设备归属边界）
- 来源：用户需求（修正）
- 操作：
  1. `AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MainDeviceWorkflow.cs`：新增 `StartSimulationLineLaser()`/`StopSimulationLineLaser()`/`ResetSimulationLineLaser()`（含 Initialize 后台线程转 Standby 的异步挂起编排），统一承载线激光模拟生命周期（线激光是主设备级联子设备）。
  2. `AdaWeldSystem/UIDesign/TabPage/MotionControlPage.cs`：删除对 `LineLaserWorkflow.Instance.Initialize/Start/Stop/Reset` 的越权直驱，改为调 `MainDeviceWorkflow` 三个新方法；删除挂起机制（`_pendingSimStart`/`StartLineLaserWithPending`/`StartPendingLineLaser`/`ClearPendingSimStart`）；保留对 `LineLaserWorkflow` 的 `Step` 读取与 `StateChanged` 事件订阅（结果消费）；保留对自身设备 `MotionControlWorkflow` 的 `Start()`/`Stop()`。
  3. 更新 `wiki/lessons/DeviceWorkflowDualFlowCallerGate.md`：补「第二条红线：UI 页设备归属边界」，更正 ILCamPage 为正确调用。
  4. 更新 `wiki/api/MainDeviceWorkflow.md`：模拟 API 表新增三个编排方法说明。
- 新增代码文件：无
- 修改代码文件：MainDeviceWorkflow.cs、MotionControlPage.cs
- 新增 Wiki 页面：无
- 矛盾检测：无（ILCamPage 经核查本就合规，此前「待统一修正」记录已更正）

## [2026-09-01 22:17:37] audit | 审计 MainDeviceWorkflow 双流程合规：类本身严格合规（7 抽象契约全实现、无自建手动），但调用方 FormMain.cs 绕过基类入口；已修正为 Initialize()+ManualStart()，并补 lessons/DeviceWorkflowDualFlowCallerGate

## [2026-09-01 21:47:31] fix | 线激光工作流（LineLaserWorkflow）删除自建手动流程，严格继承基类 ManualStart/ManualStop 双流程（ADR-048）
- 来源：用户需求（修正）
- 操作：
  1. `AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs`：删除 `_isManualMode` 字段、`IsManualMode` 属性、`StartManualMode()`、`StopManualMode()`（死代码，外部零调用）；`DoWorking()` 移除 `if(!_isManualMode)` 守卫；`CanAcceptExternalCommand` 改为基于基类 `RunMode != WorkflowRunMode.Manual`。
  2. 更新 `wiki/api/LineLaserWorkflow.md`：移除自建手动方法、补充 2026-09-01 修正说明。
  3. 更新 `wiki/index/index.md` LineLaserWorkflow 摘要。
- 新增代码文件：无
- 修改代码文件：LineLaserWorkflow.cs
- 新增 Wiki 页面：无
- 更新 Wiki 页面：api/LineLaserWorkflow.md、index/index.md
- 矛盾检测：无

## [2026-09-01 20:48:45] verify | AdaWeldSystem 备份链路离线复验：本地仓库健康、脚本降级路径正确、KB/自动化齐备；GitHub 出站网络仍不可达

**背景**：接续 20:36:39 的 infra 落地，执行"联网端到端复验"。

**复验结果（本地侧，全部通过）**：
- 本地仓库干净：`git status` 未提交改动=0，分支 main，HEAD `ac502e5`；`3rdDepend/` 误跟踪=0（`.gitignore` 生效）。
- 脚本离线降级正确：`ada_backup.sh status` 在无法获取远端 HEAD 时如实报告本地状态（HEAD/未提交/误跟踪）并退出码 1，不伪装"一致"。
- KB 页面齐全：`guides/SourceBackup-GitHub.md`(3910B)、`lessons/GitHubSyncPitfalls.md`(2949B) 均在。
- 每日自动化 `automation-1788266666622` 状态 ACTIVE，rrule `FREQ=DAILY;INTERVAL=1`。

**阻塞项**：`git ls-remote origin` 仍报 `curl 28 Failed to connect to github.com:443 ... Could not connect to server`（TCP 连接失败，非认证错误）。连续两轮会话 GitHub 出站均超时，判定为本环境网络临时/间歇不可达，非脚本缺陷。待网络恢复后执行 `bash ada_backup.sh status`（应 ahead=behind=dirty=误跟踪=0 退出 0）与 `bash ada_backup.sh push` 做在线幂等验证。

**待办（用户侧，与网络无关）**：PAT `ghp_...WOl` 曾在对话明文出现，强烈建议 GitHub → Settings → Developer settings 撤销重发，并更新 `~/.git-credentials` 对应行。

## [2026-09-01 20:36:39] infra | AdaWeldSystem 云端源码备份（GitHub）链路打通 + 确定性同步脚本 ada_backup.sh + 本地/远端一致性校验机制

**触发**：用户要求把 GitHub 云端备份沉淀进 LLMWiki 知识库，并将推送/拉取/校验锁成不会出错的确定性执行语句，且时刻检验本地文件夹是否与远端匹配。

**落地（基础设施，非 C# 代码）**：
- 仓库 `AdaWeldSystem` 已 `git init`（分支 main），remote `origin`=https://github.com/MrYangjf/AdaWeldSys.git；凭据 PAT 存于 `~/.git-credentials`（HTTPS 免密）。
- `.gitignore` 忽略 `3rdDepend/`、`bin/`、`obj/`、`.vs/`、`.code-review-graph/`、`*.user`；首次提交 247 文件已推送到远端 main，3rdDepend 误跟踪=0。
- 新建确定性脚本 `C:/Users/MrYang/ada_backup.sh`：子命令 `push`(add→commit→push，冲突自动 fetch+rebase)/`pull`(fetch+rebase)/`status`(单命令内 fetch 后比对 ahead/behind/dirty/3rdDepend 误跟踪)。所有 git 操作同进程内完成 fetch，规避沙箱 origin/main 跨命令不落盘问题。

**KB 同步（Phase 3）**：新建 [[guides/SourceBackup-GitHub]]（云端备份操作手册：初始化/忽略规则/凭据/确定性脚本/校验/排错）；新建 [[lessons/GitHubSyncPitfalls]]（同步陷阱：远程跟踪引用不落盘、3rdDepend 体积、PAT 明文、non-fast-forward）；[[index/index]] 场景路由 + guides 表 + lessons 表同步；本条目。

**待办**：PAT 曾在对话明文出现，建议 GitHub 撤销重发并更新 `~/.git-credentials`；可建每日自动化运行 `ada_backup.sh status` 持续校验。


## [2026-09-01 17:58:10] feat | 基类自动/手动双流程模型（ADR-048）+ SimulationWorkflow 删除归并主设备

**触发**：用户 `@skill:vibecoding-llmwiki` 四条改造——①基类具备自动/手动两套运行逻辑流程（自动=后台阻塞式，手动=后台非阻塞式）②主设备初始化等流程回归基类契约 ③模拟 workflow 归并主设备 workflow ④全部子流程同样双流程。Phase 1 裁决：子流程自动深度=「真实序列一步到位」；模拟 API=「直接挂主设备单例，不留兼容门面」。

**代码（Phase 2）**：
- `DeviceWorkflowBase.cs`（321→453 行）：新增 `WorkflowRunMode{None/Auto/Manual}`；`AutoRun()` 幂等起后台一次性线程跑阻塞式 `AutoRunFlow()`；`_autoAbortRequested` volatile + `IsAutoAbortRequested` + `RequestAutoAbort()`；`AutoWait(Func<bool>, timeoutMs)` 有界等待助手；`ManualStop()` 先 `Join(2000)` 自动线程；`Dispose()` 先 abort+Join(1000)；`EmergencyStop()` 重写联动中止；新增 `public Reset()` 模板 + `protected abstract ResetFlow()`。
- 7 子类一次性补齐 `ResetFlow()`（3 处既有 public `Reset()` 改 override，调用点零破坏）+ 阻塞式 `AutoRunFlow()` 真实序列（LineLaser 全序列含 `SafeAbortStop()`；MainDevice 含级联 Disconnect；MotionControl/Monitor/WeldParam 按各自语义；Safety 周期节拍型注释说明不占自动线程；LaserWeldHead 骨架空实现）。
- `SimulationWorkflow.cs` 删除（csproj 同步注销），成员全量并入 `MainDeviceWorkflow`：API 更名 `IsSimulationEnabled/EnableSimulation/DisableSimulation/LoadSimulation/SaveSimulation`，`SimTestMode` 迁文件尾；消费方替换 `MotionControlPage.cs` 9 处 + `FormMain.cs:52`。
- 关键裁定（实现期确立）：**FlowProcess 是执行器、自动线程是排程器，职责正交**——RunLoop 在 Auto/Manual 两模式下都驱动 FlowProcess（保 Safety/WeldParam 周期节拍）；ADR-047 红线 3 只约束 FlowProcess/执行步。
- 已知限制：监听线程不活跃时 FailFlow 900 步无人消费，3 处前置失败改仅记日志返回。
- 修复：`AutoWait(IsPreWorkDone,...)` 属性不能隐式转 Func → lambda 化；MonitorCamera ResetFlow 严格校验拒绝 → 检查 SetStep 返回值容错；Safety ResetFlow 改 `if(_running)` 条件版。

**验证**：静态自审全过——SimulationWorkflow 代码级零残留（仅注释）；`.IsEnabled/.Enable(/.Disable(` 零残留；ResetFlow 8 处（abstract 1 + override 7）；9 文件 region 配对平衡；基类 453 行回读完整。项目无法本机编译（.NET 4.8/MSBuild v4.0），以 Grep 交叉验证替代。

**KB 同步（Phase 3）**：新建 `decisions/ADR-048-AutoManualDualWorkflow`；ADR-014 加「⚠️ 部分取代」横幅；[[api/DeviceControlWork]] 改墓碑页（含新旧 API 对照表）；[[api/DeviceControlWork]] 增补双流程生命周期 + 模拟 API 两节；[[modules/DeviceControl]] 新增「双流程层」小节 + 目录树/生命周期表更新（8→7 工作流文件）；[[standards/StepDrivenWorkflow]] 红线 3 补 ADR-048 边界注记；[[index/index]] 场景路由 + API 表 + ADR 表 + 编号说明（44 条）同步。

**待办**：Phase 4 Lint（wiki_audit.py）；`ManualStop` Join(2000) 超时场景需人工验证自动脚本中止响应性；前置失败与流程中失败的收尾通道待统一。


## [2026-09-01 17:01:31] refactor | MainDeviceControl 基类契约审查（new Initialize 反模式修复）+ 全目录代码注释精简

**触发**：用户 `@skill:vibecoding-llmwiki 再次检查MainDeviceControl：1、主流程和子流程对基类的实现，是否初始化、自动流程使用了基类，还是复杂的自建流程。请检查修复 2、对MainDeviceControl下的所有文件做一遍代码和注释精简`。

**需求① 基类契约审查**：8 工作流全量核对——7/8 正确走基类（四抽象生命周期 + FlowProcess + 监听线程）；唯一反模式 `MonitorCameraWorkflow.public new bool Initialize()` 隐藏基类生命周期 → 修复：连接检测体移入 `InitializeFlow()`、`ManualOn()` 改调 `InitializeFlow()`、删 `new` 方法；调用方（MainDevice:585 / MonitorCamPage:147）自动走基类包装器，基类置位与 MapToDeviceState 同值无重复事件。LineLaser `_initThread` 为文档化异步初始化设计，保留。

**需求② 全目录精简（12 文件）**：
- `DeviceStateBase.cs`：重排为 私有变量/公共变量/公共函数 标准 region（`_isAlarm` 上移）；事件参数 4 属性补 summary；CheckDeviceIOSafe/OnStateSwitched 注释收敛 + 补 param/returns。
- `WorkflowStateBase.cs`：`_stepArgs`（私有）移到 `_step`（protected=公共层级）之前；事件参数补 summary；SetStep/ValidateTransition/OnStepChanged summary 收敛。
- `SimulationWorkflow.cs`：`_configFile`/`_legacyConfigFile` 从方法后 region 上移至私有变量区；公共属性 region 移到构造函数前并更名公共变量；Enable/GetEffectiveRobotX/Load/Save 注释收敛。
- `CommandTable.cs`：GetCommand/IsValidPose 补 param/returns。
- 其余 7 workflow 文件上轮已清零，本轮仅复核。

**工具链修复（csharp_review.py 三轮）**：① get/set 访问器体不屏蔽 → setter 局部变量误判字段；② 表达式体成员被 FIELD_RE 误匹配；③ 方法组引用（new Thread(RunLoop)）不算调用。细则见 [[guides/Project-Tools]] §3。

**事故与恢复**：SimulationWorkflow 批量重排脚本 find() 闭包引用旧列表 → 索引错位 → 文件损坏；从 `AdaWeldSystem_backup_20260901_163718.tar.gz` 单文件还原后重写脚本（查找函数带列表参数）。

**验证**：12 文件警告 22→1（保留 ADR-047 节拍 Thread.Sleep 例外）；静态自检大括号/region 全平衡；new 隐藏清零；Monitor 调用方影响追溯干净。

**KB 同步**：[[modules/DeviceControl]]（反模式清零注记）、[[api/MonitorCameraWorkflow]]（Initialize 契约修正）、[[guides/Project-Tools]]（§3 批量脚本两坑）、[[index/index]]。


## [2026-09-01 15:51:51] fix | 失败收尾步 FaultRecord.State 类型错配（CS0029）修复

**触发**：用户编译报错「无法将类型 string 隐式转换为 AdaWeldSystem.MainDeviceControl.DeviceState.DeviceState」。
**根因**：`FaultRecord.State` 是强类型 `DeviceState`（ADR-046 归口后收紧），而 4 个 workflow 的 `DoFinishFail()` 故障快照写 `State = _step.ToString()`（string → DeviceState）。本项目无法在本环境编译，类型错配静态自检查不出。
**修复**：LineLaser / MonitorCamera / MotionControl / WeldParam 四处统一改 `State = MapToDeviceState(_step)`（ErrorAborted/Error → Alarm，与 ADR-037「禁手工 State= 赋值」同口径）。
**排查**：全仓 `State = ...ToString` 仅此 4 处；无字符串与 `FaultRecord.State` 比较点；`FaultCategory.Process/Device` 枚举成员核对无误；`MainDevice`/`Safety` 的 `State = State` 类型正确不需改。
**KB 同步**：[[lessons/StepDrivenWorkflowPitfalls]] 五坑→六坑（新增坑六）+ 顺手修页内 `StepAlarm()` → `DoAlarm()` 方法名漂移；[[index/index]] 教训表同步。
**验证**：csharp_review.py 4 文件 0 错误 0 警告。


## [2026-09-01 15:43:32] refactor | MainDeviceControl 子流程精简审查：步号常量与单步方法同名（CS0102）修复 + FailFlow 下沉

**触发**：用户 `@skill:vibecoding-llmwiki 重新检查MainDeviceControl下子流程，步骤与方法名重复。使用精简代码的方式重新审查这些子流程`。
**用户决策（AskUserQuestion ×3）**：① **方法改 Do 前缀**（`case StepXxx: DoXxx(); break;`）② **步号常量 + FailFlow 全套下沉基类** ③ **LineLaser 7 处 lock(this) 改私有锁对象**。

**改动（8 文件）**：
- `DeviceStateApiCore/DeviceWorkflowBase.cs`：下沉 `protected const StepIdle=0 / StepFinishOk=800 / StepFinishFail=900`、`FailReason`/`FailStep` 属性、`FailFlow(reason)`；成员顺序归位（BeatMs/RunLoopPriority/IsRunLoopActive 入公共变量区）。
- `MainDeviceWorkflow.cs`：**反向改造**——原 0 个步号常量全魔法数字，补 7 个私有常量（StepPreworkConnect/StepWaitPreWeldPose/StepYAxisTracking/StepWaitWeldStart/StepStartWelding/StepWelding/StepStopping）；删自有双参 FailFlow；10 个方法 Step→Do。
- `LineLaserWorkflow.cs`：删 3 个重复常量 + FailFlow；9 方法 Step→Do；7 处 `lock(this)` → `lock(_syncRoot)`。
- `MonitorCameraWorkflow.cs`：删 3 重复常量；5 方法 Step→Do。`MotionControlWorkflow.cs`：删 2 重复常量；**删除死函数 StepTracking()**（跟踪步 100 由 CAMBOX 完成，default 空转覆盖）。`SafetyWorkflow.cs`：`StepAlarm=900` 合并为基类 `StepFinishFail`（方法名 DoAlarm 保留）。`WeldParamControlWorkflow.cs`：删 3 重复常量；4 方法 Step→Do。`LaserWeldHeadWorkflow.cs`：删常量 region。
- 全目录 74 处多行 summary 收敛为单行 + remarks；补齐 param/returns；删同义行内注释。

**工具链修复**：`scripts/csharp_review.py` 解析误报修复（形参表 / 对象初始化器被误判为字段 → 成员顺序假警告）。

**验证**：静态自检 0 同名冲突 / region 全配对 / 无 lock(this) / 无 GoStep(数字) 魔法数字 / 大括号平衡；csharp_review.py 7/8 文件 0 警告（基类仅剩 ADR-047 节拍 Thread.Sleep 有意例外）；全仓确认 FailFlow/FailReason/FailStep 无 MainDeviceControl 外部引用。

**KB 同步**：[[modules/DeviceControl]]（基类成员表）、[[standards/StepDrivenWorkflow]]（命名约定小节）、**新建 [[lessons/StepMemberNameCollision]]**、6 个 API 页（Safety/WeldParam 执行步表改 Do 方法名；MainDevice/LineLaser/Monitor/Motion 加命名注记）、[[index/index]]（路由表 + 教训表）。


## [2026-09-01 14:54:05] refactor | MainDeviceControl 目录收敛：DeviceState/ + FlowState/ → DeviceStateApiCore/（含 .csproj 漂移修复）

**触发**：用户 `@skill:vibecoding-llmwiki 我将MainDeviceControl文件夹层级修改了，你检查下归集到知识库`。
**用户决策（AskUserQuestion ×2）**：① `.csproj` 由我修复 ② **不新建 ADR**，仅就地更新各处目录/路径描述。

**代码侧实测变更**：
- `MainDeviceControl/DeviceState/`（DeviceStateBase.cs / WorkflowStateBase.cs / CommandTable.cs）与 `MainDeviceControl/FlowState/`（DeviceWorkflowBase.cs）**合并为 `MainDeviceControl/DeviceStateApiCore/`**（4 文件原地迁移，无增删，共 706 行完整）。
- **命名空间刻意不变**：前 3 文件为 `...MainDeviceControl.DeviceState`，DeviceWorkflowBase.cs 为 `...MainDeviceControl.FlowState`。
- `MainDeviceControl/DeviceWorkflow/` 8 个工作流不变。

**发现并修复的阻塞问题**：`AdaWeldSystem.csproj` 第 148–150、158 行仍指向已删除的 `DeviceState\` / `FlowState\` 路径 → **整项目编译失败**。已改为 `DeviceStateApiCore\`。
- 校验：csproj 全部 Compile Include 路径在磁盘存在（0 缺失）；磁盘全部 .cs 均已注册（0 未注册）。

**顺带校正的知识库漂移**（原记录过时）：
- `guides/Namespace-Compilation` §命名空间别名清单由「7 个（`SafetyInterlock.cs` + 5 工作流 + DeviceWorkflowBase）」校正为**实测 8 个**（7 个工作流 + `DeviceStateApiCore/DeviceWorkflowBase.cs`）；`SafetyInterlock.cs` 已于 2026-08-31 合并为 `SafetyWorkflow.cs`，且漏记 `LaserWeldHeadWorkflow.cs`。

**新增知识**：`guides/Namespace-Compilation` §1.1.1 —— **移动/重命名/合并目录同样必须同步 `.csproj`**（新增时大家记得注册，移动时最易漏；且只移目录不动命名空间并不省掉这一步），附两条自检命令与 `grep -qF` 反斜坑。

**修改代码文件**：`AdaWeldSystem.csproj`（4 条路径）
**备份**：`AdaWeldSystem_backup_20260901_144712.tar.gz`
**更新 Wiki 页面**：`architecture/DeviceControlArchitecture`（§2 目录树 + 已删除目录 + 命名空间约定「目录 ≠ 命名空间」横幅）、`modules/DeviceControl`（目录树 + 4 个小节标题 + 命名空间说明）、`project/overview`（项目树）、`index/index`（架构页与 DeviceControl 摘要）、`decisions/ADR-037`（加目录后续收敛说明）、`decisions/ADR-047`、`standards/StepDrivenWorkflow`、`lessons/StepDrivenWorkflowPitfalls`（3 处路径改 DeviceStateApiCore）、`guides/Namespace-Compilation`（路径 + 清单校正 + §1.1.1）、`logs/log.md`
**矛盾检测**：无。`logs/log.md` L276 的历史路径记录按约定不改。

---

## [2026-09-01 14:02:09] refactor | FaultRecoveryManager 归口 ProductFileManager（ADR-046 §3 落地）

**触发**：用户 `@skill:vibecoding-llmwiki FaultRecoveryManager 的按要求已经拆解方法归为 sqlitedatabase 下，消费方归为具体业务的。我目前看还在我的项目文件夹下`。
**用户决策（AskUserQuestion ×2）**：① **由 `ProductFileManager` 作为使用方承接**（而非新建独立故障恢复目录）② `FaultRecord.State` **保留强类型 `DeviceState` 枚举**，接受 ProductFileManager ↔ MainDeviceControl 枚举级循环依赖 ③ ADR 落法 = **修订 ADR-046 追加 §3**（不新建 ADR-048）④ 同步改写 ProductFileManager 职责边界表。
**备份**：`AdaWeldSystem_backup_20260901_134635.tar.gz`（工作区根，排除 bin/obj）。

**一、代码改造（8 个文件）**

| 动作 | 文件 | 说明 |
|---|---|---|
| 迁移 | `MainDeviceControl/DeviceWorkflow/FaultRecoveryManager.cs` → `ProductFileManager/FaultRecoveryManager.cs` | 命名空间 `AdaWeldSystem.MainDeviceControl.DeviceWorkflow` → `AdaWeldSystem.ProductFileManager`；含 `FaultCategory` / `FaultRecord`，整体迁移不拆文件；公共 API 零变化 |
| 补 using ×6 | `SafetyWorkflow.cs` / `MainDeviceWorkflow.cs` / `LineLaserWorkflow.cs` / `MonitorCameraWorkflow.cs` / `MotionControlWorkflow.cs` / `WeldParamControlWorkflow.cs` | 消费方实际为 **6 处**（初查 Grep 结果截断仅得 2 处，Step 2.5 二次追溯补齐，见 §四） |
| 注册 | `AdaWeldSystem.csproj` | 142 行新增 `ProductFileManager\FaultRecoveryManager.cs`（聚合到 ProductFileManager 组）；删除 156 行旧条目；356 行注释更新 |
| 注释订正 | `SqlLiteDatabase/FaultRecordManager.cs` | 类注释中「领域载体定义于 MainDeviceControl.DeviceWorkflow」→ ProductFileManager；同步 summary≤20 字规范 |

**二、ADR-028 顺带合规（迁移文件内）**：成员顺序重排为 私有变量→公共变量→构造→私有函数→公共函数（原为公共函数在前）；`#region` 由单一 `SQLite 持久化` 改为按类型五分（私有变量/公共变量/构造函数/私有函数/公共函数）；类级注释改 `summary` 一行 + `remarks`；private 方法 summary 收敛到 ≤20 字。

**三、Wiki 更新（10 页）**
- 更新：`modules/ProductFileManager`、`modules/Safety`、`modules/DeviceControl`、`modules/SqlLiteDatabase`、`api/FaultRecoveryManager`、`api/FaultRecordManager`、`architecture/DeviceControlArchitecture`（§2 目录树 + §9 + §11.3 循环依赖 4→5）、`project/overview`（文件数 DeviceControl 13→12、ProductFileManager 4→5）、`index/index.md`（4 处摘要）
- 新增章节：`decisions/ADR-046 §3`（含备选方案与后果）、`guides/Project-Tools §1.2`（Grep 结果截断教训）
- 订正：`lessons/FaultRecoveryDeviceKey`（相关文件路径 `Workflow/FaultRecoveryManager.cs` 已失效两代）

**四、矛盾检测**：无。但有两点需记录——
1. **Grep 结果截断（本次最大风险点）**：首次 `Grep("FaultRecoveryManager|FaultRecordManager|FaultCategory|FaultRecord")` 只返回 2 个消费方，实际 6 个。改用 `FaultRecord\b` 加词边界后命中齐全。**教训已沉淀为 [[guides/Project-Tools]] §1.2：影响半径类检索必须两次独立检索交叉验证。**
2. **循环依赖增量**：`ProductFileManager` ↔ `MainDeviceControl` 为架构页 11.3 新增第 5 组环，已在 ADR-046 §3 与架构页显式标注为**有意设计**（仅限一个枚举类型），非待清理项。

---

## [2026-09-01 13:59:17] refactor | ADR-047 步骤驱动全量落地：基类 + 7 个工作流改造（proposed → accepted）

**触发**：用户 `@skill:vibecoding-llmwiki 依照最新的流程基类和实现要求来修正当前项目的流程基类和各设备的实现`。
**用户决策（AskUserQuestion）**：① 范围 = **全量 P0+P1+P2**（8 个文件一次到位，ADR-047 转 accepted）② 执行步写入方式 = **强制 `GoStep(n)` 方法**（基类提供，成对刷新步号+时间戳+记日志）。
**备份**：`AdaWeldSystem_backup_20260901_132116.tar.gz`（93.7MB，工作区根，排除 bin/obj）。

**一、代码改造（8 个文件，`MainDeviceControl/`）**

| 优先级 | 文件 | 执行步 | 关键行为变化 |
|---|---|---|---|
| P0 | `FlowState/DeviceWorkflowBase.cs` | — | 新增 `WorkStep`/`WorkStartTime`/`StepElapsedMs`/`WorkStepName`/`StepStatusText`、抽象 `FlowProcess()`+`GetStepName(int)`、`GoStep(n)`、`ResetStepTime()`、`IsStepTimeout(ms)`、`RunLoop()` 常驻线程、`StartRunLoop`/`StopRunLoop`、`BeatMs`(10)/`RunLoopPriority`、`Dispose()` 模板方法 + `DisposeManaged()` 钩子 |
| P0 | `DeviceWorkflow/MainDeviceWorkflow.cs` | 0/10/11/20/21/30/31/40/800/900 | Pose 链路改命令变量；**三槽分存**（`_pendingAbort` > `_pendingCommand` > `_pendingPose`），修复 Pose/Command 编码区间重叠丢指令缺陷 |
| P1 | `DeviceWorkflow/LineLaserWorkflow.cs` | 0/10/11/20/30/31/100/700/800/900 | 删 `SpinWait`（while+Sleep 轮询）与 `_workThread`；失败计数改时长判据（原 25ms 打满阈值） |
| P1 | `DeviceWorkflow/MonitorCameraWorkflow.cs` | 0/10/20/30/800/900 | `WaitOne(5000)` → `WaitOne(0)` 非阻塞探测，超时跳 900；删自建线程 |
| P2 | `DeviceWorkflow/MotionControlWorkflow.cs` | 0/10/20/30/100/110/700/900 | `MonitorLoop`(50Hz) 并入基类线程（`BeatMs=20`）；`Start()` 由「同步完成动作」改「受理指令」；等主轴由无限等待改 120s 超时 |
| P2 | `DeviceWorkflow/WeldParamControlWorkflow.cs` | 0/10/20/800/900 | `ComputeAndOutput()` 改命令变量模式（只置 `_pendingCompute`）；⚠️ 返回值语义变为「上一轮是否成功」 |
| P2 | `DeviceWorkflow/LaserWeldHeadWorkflow.cs` | 0（骨架） | 补空 `FlowProcess()`/`GetStepName()`；`IsRunLoopActive=false`（骨架期不起空转线程） |
| P2 | `DeviceWorkflow/SafetyWorkflow.cs` | 0/10/900 | `MonitorLoop` 并入基类线程（`BeatMs=50` + `ThreadPriority.Highest`）；900 持续检查至恢复 |

统一约定：**`GoStep(n)` 是唯一改步入口** · `OnStepChanged` 复位执行步（`FlowProcess` 内 `SetStep` 后**必须立即 return**）· 8 个子类 `Dispose()` 全部上移为基类模板方法 + `DisposeManaged()`（无一处 `Dispose(bool)` 重写，守 ADR-001）。

**二、知识库同步**

| 页面 | 变更 |
|---|---|
| `decisions/ADR-047-StepDrivenWorkflow.md` | `proposed` → **`accepted`**；新增落地清单完成情况表（8/8 ✅）、3 条落地后新约定、**3 条已知待办**、4 条风险的缓解措施 |
| `modules/DeviceControl.md` | 「第三层：执行步」由规划改已实施；基类成员表重写；7 个工作流表加「执行步」列；UI 接入由两个属性升级为三个 |
| `api/MainDeviceWorkflow.md` | 加执行步表 + 三槽命令变量表 + Pose/Command 编码重叠缺陷说明 |
| `api/LineLaserWorkflow.md` | 加执行步表 + 「行为变化（重要）」四条 |
| `api/MonitorCameraWorkflow.md` | 加执行步表 + 工作循环段重写（WaitOne(0) 探测） |
| `api/MotionControlWorkflow.md` | 加执行步表 + Start/Stop 语义变更说明 |
| `api/WeldParamControlWorkflow.md` | 加执行步表 + `ComputeAndOutput` 返回值语义变化警示 |
| `api/SafetyWorkflow.md` | 加执行步表 + 周期节拍例外说明（50ms 不属红线 3） |
| `lessons/StepDrivenWorkflowPitfalls.md` | **新建**：五坑（执行步复位覆盖 / 步内阻塞冻结超时与急停 / 抽象成员级联编译 / 命令槽碰撞 / 失败计数爆表） |
| `index/index.md` | ADR-047 由 7.2 待决移入 7.1 现行有效；新增 lessons 行；7 个 API/modules/standards 行加执行步摘要；lessons 计数 12→13 |

**三、已知待办（已登记 ADR-047）**
1. 基类 `Initialize()/ManualStart()/ManualStop()/AutoRun()` 的 `State =` 兜底赋值与红线 2 存在张力 —— **暂保留**（移除会让 `LineLaserWorkflow` 异步初始化期间 State 显示 Work，主设备 `IsChildConnected` 误判已连接）；
2. `BeginStarting()`/`BeginWorking()` 当前无主设备调用方 → 行为变为「30s 超时 → ErrorAborted」，UI 单独调试线激光时建议启用模拟模式自驱动；
3. PLC 未连接时安全监控必报警（继承自 ADR-044 既有待办）。

**四、验证**：本项目无法在本环境编译，已做静态自检 —— `MainDeviceControl` 下 13 个 .cs 的 `#region`/`#endregion` 全部配对、`FlowProcess`/`GetStepName` 实现数 7/7、无残留 `Dispose(bool)`/`SpinWait`/子类 `Thread.Sleep`；Grep 追溯 `FormMain`/`MotionControlPage`/`MonitorCamPage`/`ILCamPage`/`MainPage` 调用点签名全部兼容（`MotionControlWorkflow.Start()` 返回值无调用方使用）。

---

## [2026-09-01 10:57:12] restructure | standards/ 扁平化：撤销 references/ 子目录，确立「wiki/ 禁止二级子目录」

**触发**：用户要求「standards 下还有一个文件夹，请修改去掉子文件夹，都以文件展示，并且能正确关联」。备份：`LLMWiki_backup_20260901_105310.tar.gz`（工作区根）。

**一、文件搬迁（4 页，`standards/references/` → `standards/` 平铺）**

| 原路径 | 新路径 | 行数 |
|---|---|---|
| `standards/references/rules-file-organization.md` | `standards/CodeSimplification-RefFileOrganization.md` | 174→176 |
| `standards/references/rules-logic-simplification.md` | `standards/CodeSimplification-RefLogicSimplification.md` | 228→230 |
| `standards/references/rules-function-simplification.md` | `standards/CodeSimplification-RefFunctionSimplification.md` | 251→253 |
| `standards/references/csharp-vibecoding-review-workflow.md` | `standards/CodeSimplification-ReviewWorkflow.md` | 101→103 |

命名判据：**`父页名-用途` 前缀成组**，列表里天然相邻，grep `CodeSimplification-` 即得全组；不使用 `Ref` 之外的缩写，避免与 `standards/StepDrivenWorkflow` 等平级页混淆。`references/` 空目录已删除。

**二、关联修复（成组三件套：命名前缀 + 索引分组 + 页首横幅回链父页）**
1. 4 个页面页首统一加归属横幅，回链 [[standards/CodeSimplification]]，并声明「standards/ 全库禁止子目录」。
2. 全库批量改链 16 处：`standards/CodeSimplification.md` 11 处（维度说明 + 附录索引）、`index/index.md` 4 处（§4.1 子表）、`decisions/ADR-028` 1 处（正文路径描述）。
3. `CodeSimplification-ReviewWorkflow` 页内 3 个**相对文件链接**（`[references/xxx.md](references/xxx.md)`）改为 wiki 链接（`standards/CodeSimplification-RefFileOrganization` 等 3 个）——原相对路径在扁平化后必然失效，属本次隐藏最深的断链点。
4. `index/index.md` §4.1 标题由「（standards/references/）」改为「（standards/ 平铺，无子目录）」并加扁平化说明行。

**三、硬规则落地（防止回潮）**
- `AGENTS.md`「目录结构」块新增：`wiki/` 下各分类一律平铺为 `.md`，**不再新建任何子目录**；成组靠「文件名前缀 + 索引分组 + 横幅回链父页」三件套。
- `tools/wiki_audit.py` 新增**第 9 项「二级子目录检测」**：一级分类目录（11 个）允许，二级目录应为 0（实现坑：初版用 `os.walk(WIKI)` 把 11 个一级分类全误报为子目录，改为逐分类下探二级）。
- 顺带清零 1 处历史红链：日志正文里对「已修复错链」的描述文本 `wiki/index/index.md` 原写作 wiki 链接形式，改为代码体路径，不再被体检脚本判红。（**教训**：日志里复述错误链接时必须用代码体，否则体检脚本把「被修复的对象」又判成新的红链。）

**四、复检（wiki_audit.py）**：红链 **0**（占位符 4 处白名单单列）· 孤儿页 **0** · 二级子目录 **0** · 内容重复 **0** · 4 个新页入链 3/3/3/2 均非孤儿。

---

## [2026-09-01 10:47:48] lint+restructure | 知识库全库治理：消除冲突 / 合并重复 / 调整指导文件位置 / 提升检索

**触发**：用户要求「对知识库进行检查，消除冲突，合并重复，调整不合理的指导文件位置，提升检索速度和准度」。备份：`LLMWiki_backup_20260901_102925.tar.gz`（工作区根）。

**一、新增体检脚本 `tools/wiki_audit.py`（只读扫描）**
输出 8 项：红链 / 孤儿页 / index 重复行与结构 / ADR 编号空洞与登记缺失 / 页面体积分布（含 TOC 检测）/ 内容重复度（12-gram 相似度）/ lessons 错放检测 / standards 入链统计。含**示例占位符白名单**（``XXX``、``引用页面``、``lessons/...`` 等不算红链）。运行方式：在 `LLMWiki/` 下 `python tools/wiki_audit.py`。

**二、新建 `wiki/guides/` 分类（本次最大结构调整）**
- **判据确立**：`standards/` = 必须遵守的强制规范（由路由触发）；`lessons/` = 踩过什么坑（门禁）；**`guides/` = 怎么做（操作手册/参考手册/工具用法）**。已写入 `AGENTS.md` 目录结构与 index 顶部。
- **从 `lessons/` 迁出 6 页**（共 3237 行）：`AntdUI-Complete-Reference`→`guides/AntdUI-Reference`、`Project-Tools-Guide`→`guides/Project-Tools`、`Config-Data-Tools-Guide`→`guides/Config-Data-Tools`、`Namespace-Compilation-Guide`→`guides/Namespace-Compilation`、`WinForms-Designer-Guide`→`guides/WinForms-Designer`、`WinForms-UI-Threading-Guide`→`guides/WinForms-UI-Threading`。
- 全库批量重写链接，**51 个文件**更新；6 个新页加「位置说明」横幅并把 frontmatter tags 从 `教训` 改 `指导`。
- `lessons/` 由 18 页收敛为 12 页，回归纯教训定位。

**三、合并重复 / 消除孤儿**
- index 删重复行 3 处：`api/SimulationWorkflow` ×2→1、`ADR-038` ×2→1、`ADR-043` ×3→1。
- index「代码精简与权责规范」分类原为 **4 个碎片表格**，合并为 1 个主表 + 1 个 references 子表。
- 孤儿页归零：`standards/CodeSimplification-progress`（2026-08-26 进度快照，非规范）→ 归档为 `archive/CodeSimplification-Progress-20260826` 并由 `standards/CodeSimplification` 反向引用；`lessons/CodeSimplification-Scope-DesignerOnly`（范围裁定，有价）→ 由 `standards/CodeSimplification` 引用 + 登记进 index。
- index 补登此前未入索引的 5 页：4 个 `standards/references/*`、新归档页、以及**漏登记的 ADR-034**。

**四、消除冲突 / 标注过期（8 处）**
给 6 个 ADR 加统一格式「已被取代」横幅并分组到 index §7.3：
`ADR-010`（仅归属目录失效，双记录设计仍有效 → ProductFileManager）、`ADR-011`（结论不变，仅目录迁 MainDeviceControl）、`ADR-013`（中枢目录 + MonitorSupervisionWorkflow 双失效）、`ADR-035`（状态机体系随 DeviceStateMachine/ 删除）、`ADR-023`（V3 架构描述废弃，「不引入 Stateless」仍有效）、`ADR-026`（Safety 目标目录 + 文件划分双失效）。
**裁定 ADR-003 与 ADR-047 的表面冲突**：ADR-003 取图 `WaitOne(上限 5000ms)` **不违反** ADR-047「单步禁阻塞等待」红线 —— 判据「**有界 + 可失败 = 合法；无界 + 静默 = 违规**」，已双向写入 `ADR-003` 与 `standards/StepDrivenWorkflow` 红线 3。
ADR 表由平铺改为**三组**：现行有效(35) / 待决 proposed(1) / 已废弃·已被取代(8)，并加编号空洞说明（006、009 属 SunnyUI 已废弃；023、024 属 V2 已归档，不再回收）。

**五、红链归零（7 处）**
`AGENTS.md` 两处死链改指：`lessons/Log-Append-Position`→`guides/Project-Tools` §2.1、`lessons/CodeProjectRegistration`→`guides/Namespace-Compilation` §1.1（该页本就不存在，规则一直在 Namespace-Compilation 里）；同步修正 `skills/vibecoding-llmwiki/SKILL.md` 两处（**注意：该 SKILL 在 `~/.workbuddy/skills/` 与 `LLMWiki/skills/` 各有一份副本，两处都要改**）。`ADR-030` 错链 `ADR-029-IntelligentLaserDefault`→`ADR-021-LineLaserWorkflowRefactor`；`logs/log.md` 三处（`api/SimulationController`→`api/SimulationWorkflow`、`ADR-032-CodeSimplification`→代码体、`wiki/index/index.md` 的 wiki 链接→路径文本）；`archive/CodeSimplification-Progress-20260826` 两处脚本路径改代码体。

**六、检索提速**
- index 顶部新增 **⚡ 场景速查路由表**（20 行：任务 → 直接读 1~3 页 + 硬约束提示），命中即可开工，无需扫 11 张分类表。
- index 新增「目录」跳转表 + 各章节锚点。
- 6 个超大页（>600 行）加**章节导航 TOC**：`lessons/IntelligentLaser-Pitfalls`(1229)、`guides/AntdUI-Reference`(1080)、`guides/Project-Tools`(949)、`archive/V2-Architecture-Legacy`(673)、`api/ZMotionController`(625)、`modules/KUKARobot`(580)。
- index 末尾加「维护说明」：体检脚本路径 + 健康判据 + 三层分类判据。

**Phase 4 Lint 复检**：红链 **0**（占位符已白名单并单列）、孤儿页 **0**、index 重复行 **0**、ADR 登记缺失 **0**、内容重复 **0**、超大页 TOC 覆盖率 **6/6**。目录页数 152 页 / 23249 行（均值 152 行）。矛盾检测：ADR-003↔047 已显式裁定；ADR-004↔047 于 ADR-047 中裁定为补充关系。代码漂移：**本次未改代码**，`standards/StepDrivenWorkflow`（ADR-047）仍为 proposed，落地清单待用户确认。

---

## [2026-08-31 15:11:50] coding | 快捷开关面板顶部新增标题 Label「子设备状态」（ADR-045 迭代续）
- 来源：用户需求（"在panelfloatbutton最上方放入一个AntdUI.label。text为子设备状态"）
- 操作：
  1. `MainPage.cs` `InitDeviceSwitchButtons()`：面板顶部代码后置创建 `AntdUI.Label`（Text="子设备状态"、AutoSizeMode=Width、Size(100,24)、Location(2,2)，局部变量随面板销毁）；按钮起始 Y 下移 `btnTop = top + 24 + gap` 让位标题；保留用户参数 52×52/gap=15/left=2/top=2（整体面板高度需求 428px）
- 新增代码文件：无
- 修改代码文件：`AdaWeldSystem/UIDesign/ControlPage/MainPage.cs`（InitDeviceSwitchButtons 增标题创建 + 按钮 Y 起点调整）
- 新增 Wiki 页面：无
- 更新 Wiki 页面：`wiki/decisions/ADR-025-ButtonShadowDeviceSwitch.md`、`wiki/modules/UIDesign.md`、`wiki/api/MainPage.md`
- 矛盾检测：无
- 备份：`AdaWeldSystem_backup_20260831_151106.tar.gz`

---

## [2026-08-31 15:06:51] coding | 快捷开关按钮随面板竖直摆放改纵向堆叠（ADR-045 迭代续）
- 来源：用户需求（"我把panelfloatbutton竖直摆放了，按钮请按照竖直方向排列"）
- 操作：
  1. `MainPage.cs` `InitDeviceSwitchButtons()`：按钮 Location 由横向（`left + i*(btnWidth+gap), top`）改为纵向（`left, top + i*(btnHeight+gap)`）；保留用户手调参数 52×52/gap=15/left=15/top=2（6 按钮总高 389px，面板需相应拉高）；Tooltip 方位保持 Top
- 新增代码文件：无
- 修改代码文件：`AdaWeldSystem/UIDesign/ControlPage/MainPage.cs`（仅按钮 Location 计算与注释）
- 新增 Wiki 页面：无
- 更新 Wiki 页面：`wiki/decisions/ADR-025-ButtonShadowDeviceSwitch.md`、`wiki/modules/UIDesign.md`、`wiki/api/MainPage.md`
- 矛盾检测：无（workspace 内 Designer.cs 中 panelfloatbutton 仍为横向布局快照，以用户本机最新设计为准；代码布局计算已适配竖向）
- 备份：`AdaWeldSystem_backup_20260831_150556.tar.gz`

---

## [2026-08-31 14:43:38] coding | 快捷开关 Tooltip 增加连接状态文本（ADR-045 迭代续）
- 来源：用户需求（"按钮的tooltip需要写明状态。已连接/未连接"）
- 操作：
  1. 核对 TooltipComponent.SetTip 源码：内部字典 `AddOrUpdate`，重复 SetTip 支持原地更新文本（悬停实时读取）
  2. `MainPage.cs`：新增 `BuildDeviceTooltipText(idx, connected)`（设备名 + 「：已连接/：未连接」）；`InitDeviceSwitchButtons()` 初始 SetTip 全部为未连接；`RefreshDeviceSwitchUi()` 线激光状态变化时 `SetTip` 原地更新 Tooltip 文本
  3. 保留用户手动改动：按钮 58×58、gap=15、徽标 Filled 图标名、BadgeSize=1.0F
- 新增代码文件：无
- 修改代码文件：`AdaWeldSystem/UIDesign/ControlPage/MainPage.cs`（初始化 SetTip 文本 + 新增 BuildDeviceTooltipText + 刷新处同步 Tooltip）
- 新增 Wiki 页面：无
- 更新 Wiki 页面：`wiki/decisions/ADR-025-ButtonShadowDeviceSwitch.md`、`wiki/api/MainPage.md`、`wiki/modules/UIDesign.md`
- 矛盾检测：无
- 备份：`AdaWeldSystem_backup_20260831_144247.tar.gz`

---

## [2026-08-31 14:25:46] coding | 快捷开关：图标按设备预留接口化 + DefaultBack 连接态底色（ADR-045 迭代续）
- 来源：用户需求（①预留接口修改 IconSvg——每个按钮的设备指向不一样；②按钮 DefaultBack 未连接=灰(158,158,158)、连接=默认白色）
- 操作：
  1. 检测到用户手动改动：徽标图标 CheckOutlined/CloseOutlined→CheckCircleFilled/CloseCircleFilled + `BadgeSize=1.0F`（保留并验证 DLL 内置名存在）
  2. `MainPage.cs`：新增 `_deviceIconSvgs[]`（各设备图标 SVG 缓存，非 readonly——避免 CS0191）+ `DeviceBackDisconnected`（static readonly 灰 158,158,158）；`InitDeviceSwitchButtons()` 图标改从数组取值 + 按钮 `DefaultBack=灰`；`SetDeviceIconSvg()` 同步写数组+按钮；`RefreshDeviceSwitchUi()` 增加 `DefaultBack`（连接=null 主题默认白 / 断开=灰）
- 新增代码文件：无
- 修改代码文件：`AdaWeldSystem/UIDesign/ControlPage/MainPage.cs`（字段区 +2 成员；初始化/刷新/预留接口三处）
- 新增 Wiki 页面：无
- 更新 Wiki 页面：`wiki/decisions/ADR-025-ButtonShadowDeviceSwitch.md`、`wiki/api/MainPage.md`、`wiki/modules/UIDesign.md`
- 矛盾检测：无（用户手动 Filled 图标名与 BadgeSize 已同步入 Wiki；Outlined 记录被覆盖更新）
- 备份：`AdaWeldSystem_backup_20260831_142335.tar.gz`

---

## [2026-08-31 14:06:21] coding | 快捷开关徽标 SVG 化：CheckOutlined=连接 / CloseOutlined=断开（ADR-045 迭代续）
- 来源：用户需求（"连接的badgesvg：CheckOutlined。断开的徽标：CloseOutlined"）
- 操作：
  1. 验证 `CheckOutlined`/`CloseOutlined` 为 AntdUI SvgDb 内置图标名且本地 AntdUI.dll 元数据存在
  2. `MainPage.cs`：新增 const `ConnectedBadgeSvg="CheckOutlined"`/`DisconnectedBadgeSvg="CloseOutlined"`；`InitDeviceSwitchButtons()` 徽标由 `Badge=""`+`BadgeMode=true` 圆点改为 `BadgeSvg=DisconnectedBadgeSvg`（删 Badge/BadgeMode——BadgeMode 仅作用于圆点渲染路径）；`RefreshDeviceSwitchUi()` 同步改 `BadgeSvg`+`BadgeBack`（对勾/叉号 + 绿/红）
- 新增代码文件：无
- 修改代码文件：`AdaWeldSystem/UIDesign/ControlPage/MainPage.cs`（字段区 +2 const；快捷开关 region 徽标初始化与刷新两处）
- 新增 Wiki 页面：无
- 更新 Wiki 页面：`wiki/decisions/ADR-025-ButtonShadowDeviceSwitch.md`、`wiki/api/MainPage.md`、`wiki/modules/UIDesign.md`
- 矛盾检测：无（初版圆点+BadgeMode 描述已原地更新并标注被取代）
- 备份：`AdaWeldSystem_backup_20260831_140527.tar.gz`

---

## [2026-08-31 13:58:42] coding | MainPage 硬件快捷开关 ButtonShadow 风格迭代（buttonShadow1 形态 + Tooltip + 原生徽标）
- 来源：用户需求（按钮形态参考 AntdUI Demo ButtonDemo 的 buttonShadow1；设备名经 TooltipComponent 顶部显示；断开红色 badge/连接绿色 badge；预留按钮图标 SVG 与 badge SVG 接口）
- 操作：
  1. Phase 0 检索：ADR-045 初版（96×34 文本按钮 + Type 配色）为本次迭代基线；形态参考经用户指认为本地 `M3/AntdUI使用demo/AntdUI-Demo-main/Views/ButtonDemo.Designer.cs` 的 `buttonShadow1`（50×50、BorderWidth=1F、IconRatio=1.2F、IconSvg=poweroff 电源 SVG（resx 提取）、ShadowColor=黑、Badge=""、BadgeMode=true）；本地 `AntdUI-main` 源码确认 `IControl` 内建徽标属性（Badge/BadgeSvg/BadgeAlign/BadgeMode/BadgeBack 等）与 `Helper.GDI.PaintBadge` 渲染逻辑（BadgeBack ?? 红 兜底）；TooltipComponent 范式取自 TooltipDemo（单实例多控件 SetTip、ArrowAlign=TAlign.Top）
  2. 本地 `3rdDepend/AntdUI.dll` 字符串表验证：BadgeBack/BadgeSvg/BadgeMode/BadgeAlign/IconRatio/SetTip/TooltipComponent 元数据均存在，无需升级 DLL
  3. 重写 `MainPage.InitDeviceSwitchButtons()`：50×50 仅 SVG 图标按钮（默认 poweroff SVG）、`_tooltip`（微软雅黑 10F，ArrowAlign=Top）逐按钮 SetTip 设备名、原生徽标 Badge=""+BadgeMode=true+BadgeAlign=TR+BadgeBack 红；删 Type 配色与 Text
  4. `RefreshDeviceSwitchUi()` 改为仅改线激光按钮 `BadgeBack`（绿(82,196,26)=连接/红(255,77,79)=断开）；新增 public 预留接口 `SetDeviceIconSvg(idx, svg)`/`SetDeviceBadgeSvg(idx, svg)`（映射原生 BadgeSvg）；`DisposeComponents()` 增加 `_tooltip` 释放
  5. Phase 2 自审：无 Dispose(bool) 重写、Designer.cs 未动、region 配对完整、C# 7.3 合规、闭包拷贝循环变量；影响追溯：RefreshDeviceSwitchUi 唯一外部调用方 FormMain.cs:377 签名未变，无断裂
- 新增代码文件：无
- 修改代码文件：`AdaWeldSystem/UIDesign/ControlPage/MainPage.cs`（字段区 +3：_tooltip/DeviceBadgeRed+Green/DefaultDeviceIconSvg；硬件快捷开关 region 重写；DisposeComponents 增释放）
- 新增 Wiki 页面：无
- 更新 Wiki 页面：`wiki/modules/UIDesign.md`（快捷开关章节重写）、`wiki/api/MainPage.md`（关键方法表 + region 结构 + 设计约束）、`wiki/decisions/ADR-025-ButtonShadowDeviceSwitch.md`（追加风格迭代章节，负面项解除）、`wiki/lessons/AntdUI-Complete-Reference.md`（TooltipComponent/原生徽标/SvgDb 基础集/ButtonShadow 范式 4 条）、`wiki/index/index.md`（ADR-045 摘要更新）
- 矛盾检测：无（ADR-045 初版"纯文本+Type 配色"描述已在原页面原地更新，负面项"无 Tooltip/无图标"标注解除）

---

## [2026-08-31 11:47:19] coding | MainPage 硬件快捷开关 FloatButton→ButtonShadow（ADR-045）
- 来源：用户需求（用户指出"现在使用 floatbutton 的方式不合适，因为切换页面按钮的显示和关闭，需要事件触发，会做的很复杂。替换掉 floatbutton 使用 buttonshadow 来实现"）
- 操作：
  1. Phase 0 检索：确认 `MainPage.cs` 中 FloatButton 整块区域已被用户手动注释停用（字段残留），`FormMain.uiMillisecondTimer1_Tick` 中 `RefreshDeviceSwitchUi()` 调用同被注释；`panelfloatbutton` 面板在 Designer.cs 中仍存在；AntdUI.dll 元数据确认含 `ButtonShadow` 类型（`ButtonShadow : Button`，内建阴影）
  2. Phase 2 代码：`MainPage.cs` 删 `_floatButtonForm`/`_deviceSwitchIcons` 字段与整块注释遗骸（147 行）；新增 `_deviceButtons` 数组 + `InitDeviceSwitchButtons()`（构造函数创建 6 个 `AntdUI.ButtonShadow` 常驻 `panelfloatbutton` 面板，96×34、Y=13 居中、Round=true、默认 TTypeMini.Error）；恢复 `IsLineLaserRunning()`/`ToggleLineLaserConnection()` 为真实方法；重写 `RefreshDeviceSwitchUi()`（仅改线激光按钮 `Type` 属性，`_lastLlConnected` 去重）；`FormMain.cs` 取消定时器中 `RefreshDeviceSwitchUi()` 调用注释并更新注释文字
  3. 自审：FloatButton 残留 0、`Dispose(bool)` 重写 0、region 配对 6/6、闭包循环变量已拷贝、无 Designer.cs 修改、无新增文件（无需 .csproj 注册）
- 修改代码文件：`UIDesign/ControlPage/MainPage.cs`、`UIDesign/MainWindow/FormMain.cs`
- 新增 Wiki 页面：`decisions/ADR-025-ButtonShadowDeviceSwitch.md`
- 更新 Wiki 页面：`modules/UIDesign.md`（MainPage 快捷开关章节改写）、`wiki/index/index.md`（ADR 表新增 ADR-045 行）
- 矛盾检测：无（原 FloatButton 方案描述已在模块文档中替换为 ButtonShadow 现状，历史方案由 ADR-045 备选方案章节承载）

---

## [2026-08-31 11:06:50] refactor | 安全检查三文件合并为单一安全检查流程（ADR-044）
- 来源：用户需求（用户指出"用于安全检查的三个文件应该是合并的：安全变量值和检查地址 / 安全锁检查 / 安全流程，其实应该合并为一个安全检查流程"）
- 操作：
  1. Phase 0 检索：定位三文件 `SafetyFlow.cs`(52 行，阈值+PLC 地址) / `SafetyInterlock.cs`(212 行，FaultCategory+FaultRecord+SafetyInterlockResult+Checker) / `SafetyWorkflow.cs`(104 行，MonitorOnce 为 TODO 空桩)；**关键发现：三者零外部消费方，且 SafetyWorkflow 未继承 DeviceWorkflowBase（违反 ADR-038）**
  2. Phase 1 产出合并方案，用户拍板 4 项：配置类保留为同文件独立 `SafetyFlow` / 检查器保留为同文件工具类由流程调用 / `FaultRecord`+`FaultCategory` 迁入 `FaultRecoveryManager.cs` / `SafetyWorkflow` 继承泛型基类并接入
  3. Phase 2 代码：三文件合并为 `SafetyWorkflow.cs`（520 行，含 `SafetyWorkflowState` 枚举 + SafetyWorkflow + SafetyFlow + SafetyInterlockResult + SafetyInterlockChecker）；`SafetyWorkflow` 继承 `DeviceWorkflowBase<SafetyWorkflowState>`，重写 `MapToDeviceState`/`InitializeFlow`/`ManualOn`/`ManualOff`/`AutoRunFlow`/`CheckDeviceIOSafe`；`MonitorOnce` 由空桩实现为真实互锁检查，失败走 `EmergencyStop()` + `FaultRecoveryManager.RecordFault("Safety", ...)`；`MainDeviceWorkflow.IsRobotPoseSafe` 由 `return true` 接入 `IsSafe`；删伪异步 `CheckAsync`（Grep 确认零引用）
  4. 精简：脚本告警 42 → 1（补 `<param>/<returns>`、summary 压到 20 字内、清成员顺序、删伪异步；唯一残留 `MonitorLoop` 的 `Thread.Sleep` 属周期轮询有意例外）
  5. 顺带修复 `scripts/csharp_review.py` 本体缺陷：属性注释检查块被误置于 `_check_method_doc_quality()` 内，扫描含返回值方法的文件时抛 `NameError: name 'source' is not defined` 导致整文件扫描失败（已移回 `check_doc_comments()`）
- 删除代码文件：`MainDeviceControl/DeviceWorkflow/SafetyFlow.cs`、`MainDeviceControl/DeviceWorkflow/SafetyInterlock.cs`（csproj 同步移除 2 条，目录 11 → 9 文件）
- 修改代码文件：`MainDeviceControl/DeviceWorkflow/SafetyWorkflow.cs`（重写）、`MainDeviceControl/DeviceWorkflow/FaultRecoveryManager.cs`（迁入 FaultCategory+FaultRecord，补 `using DeviceState =` 别名）、`MainDeviceControl/DeviceWorkflow/MainDeviceWorkflow.cs`（IsRobotPoseSafe 接入）、`AdaWeldSystem.csproj`
- 修改脚本：`Vicoding管理平台/LLMWiki/scripts/csharp_review.py`
- 新增 Wiki 页面：`decisions/ADR-024-SafetyCheckConsolidation.md`、`api/SafetyWorkflow.md`
- 更新 Wiki 页面：`modules/Safety.md`（重写，原页面路径与 Standby 状态名均已过期）、`modules/DeviceControl.md`、`index/index.md`（补 ADR-043/044 与 api/SafetyWorkflow 索引条目）、`standards/CodeSimplification.md`（成员顺序 protected 判定口径 + Thread.Sleep 周期轮询例外 + 脚本缺陷说明）
- 备份：`AdaWeldSystem_backup_20260831_104743.tar.gz`
- 自查：括号 82/82、region 10/10 全配对；无新增 `Dispose(bool)`（ADR-001）；`CheckAsync` 全项目零残留；被改文件 `FaultRecoveryManager.cs` 告警数与改动前持平（8 项，均为既有）
- 矛盾检测：无。ADR-043 已被今日「权责边界治理」占用，本次沿用 **ADR-044**；ADR-026 的「三文件并存」结论已被 ADR-044 取代（其"迁 Workflow 不建子文件夹"部分仍有效）
- 待用户决策：①安全监控是否纳入上电初始化级联 ②PLC 点位现场标定 ③`_pollIntervalMs = 50`（20Hz 轮询）是否调为 200ms

---

## [2026-08-31 10:46:46] refactor | 权责边界治理：流程不再产出数据（ADR-043）
- 来源：用户需求（用户审查 `MonitorCameraWorkflow` 时发现"流程下很多完成事件"，质疑流程与子设备对象权责不清；要求排查全部子流程并沉淀知识库）
- 操作：
  1. Phase 0 全量核查 6 个子流程的自定义事件，定位 **11 处越权 + 1 处流程态越权 + 1 处依赖倒置**（其中 5 个事件零订阅属死代码，`DisplayEvent` 与 `MonitorCameraRun.FrameCompletedEvent` 构成双通道）
  2. Phase 1 产出五条权责规则 R1~R5 与治理方案，用户确认「全量治理 + 健康巡检下沉 `MonitorCameraRun`」
  3. Phase 2 代码治理：`MonitorCameraWorkflow` 删 5 事件 + 5 参数类 + 健康巡检块 + `Displaying` 态（**665→435 行**）；`MotionControlWorkflow` 删 2 转发事件 + `LaserCamBoxTrackingErrorEventArgs`；`WeldParamControlWorkflow` 删 `ParamOutputReady`；`MainDeviceWorkflow` 删 `FlowStateSwitched`（含 `OnStepChanged` 重写）与 `PowerOnInitializeCompleted`；`MonitorCameraRun` 承接健康巡检；`MonitorCameraPhase`/`MonitorSupervisionState` 下沉 `MonitorCam/Api`（**解除子设备对流程层的反向依赖**）
  4. UI 平移：`MonitorCamPage` 改「推状态 + 拉数据」范式（图像←`MonitorCameraRun.FrameCompletedEvent`，进度←基类 `StateChanged`，结果←`LastResult`/`LastOverlay`）；`FormMain` 的 `FlowStateSwitched` → `StateChanged`（回调更名 `OnMainDeviceStepChanged`）
  5. Phase 3 沉淀：新建 ADR-043 + `standards/WorkflowResponsibilityBoundary.md`（index 路由，免重复输入），重写 `api/MonitorCameraWorkflow.md` 并同步 8 个关联页面
- 修改代码文件：`MainDeviceControl/DeviceWorkflow/{MonitorCameraWorkflow,MotionControlWorkflow,MainDeviceWorkflow,WeldParamControlWorkflow}.cs`、`MainDeviceControl/DeviceState/WorkflowStateBase.cs`（注释）、`MonitorCam/MonitorCameraRun.cs`、`MonitorCam/Api/IMonitorCameraApi.cs`、`UIDesign/TabPage/MonitorCamPage.cs`、`UIDesign/MainWindow/FormMain.cs`
- 新增 Wiki 页面：`decisions/ADR-023-WorkflowResponsibilityBoundary.md`、`standards/WorkflowResponsibilityBoundary.md`
- 更新 Wiki 页面：`index/index.md`、`api/MonitorCameraWorkflow.md`、`api/MonitorCameraRun.md`、`api/MotionControlWorkflow.md`、`api/WeldParamControlWorkflow.md`、`api/MainDeviceWorkflow.md`、`api/FormMain.md`、`modules/DeviceControl.md`、`architecture/DeviceControlArchitecture.md`、`decisions/ADR-042-WorkflowStateBaseGeneric.md`（标注其 `FlowStateSwitched` 条款已被推翻）
- 备份：`AdaWeldSystem_backup_20260831_103455.tar.gz`
- 自查：括号 8/8 文件全平衡、region 全配对（修复 `WeldParamControlWorkflow` 删事件时 region 失衡 1 处）、已删符号全项目零残留、无新增 `Dispose(bool)`（ADR-001）
- 矛盾检测：无。**注意**：ADR-038 编号已被今日「WorkflowStateBase 泛型化」占用，本次改用 **ADR-043**；ADR-038 中 `FlowStateSwitched` 相关 3 处条款已标注为被推翻

---

## [2026-08-31 10:30:08] refactor+ingest | WorkflowStateBase 泛型化：流程态机制下沉基类，机器人侧整机流程态下沉主设备（ADR-038）
- 来源：用户审查指出两个继承失效问题——①子流程（线激光等）整套自建流程态机制，`SetStep`/`MapToDeviceState`/`Step`/`StateChanged`/自有 EventArgs 五类成员在 4 个子工作流重复实现；②`WorkflowStateBase` 中的 `DeviceFlowState` 是机器人侧状态照抄，子流程语义对不上被迫新建方法。约定：共通能力继承、独有内容自建。
- **代码改动（12 文件，无新增/删除文件，csproj 无需变更）**：
  - `DeviceState/WorkflowStateBase.cs` 重写为 `WorkflowStateBase<TStep> where TStep : struct`：`Step` 属性 + `SetStep(newStep, reason)` 统一转换入口（校验→更新→四态映射→事件→日志）+ `MapToDeviceState` 抽象方法 + `ValidateTransition` 虚方法 + `OnStepChanged` 钩子 + `StateChanged` 事件；新增通用 `WorkflowStepChangedEventArgs<TStep>`。
  - `FlowState/DeviceWorkflowBase.cs` 改为 `DeviceWorkflowBase<TStep>`（四抽象生命周期 + 四公开编排不变，构造函数传初始流程态）。
  - `MainDeviceWorkflow`：继承 `DeviceWorkflowBase<MainDeviceFlowState>`；`DeviceFlowState` **更名 `MainDeviceFlowState`** 并定义于本文件；`FlowState => Step`；`FlowStateSwitched` 改由 `OnStepChanged` 转发；`IsRobotPoseSafe` 下沉为私有方法；`CheckSafetyFlow` 无调用方按死代码删除；新增整机 `MapToDeviceState`。
  - 5 个子工作流（LineLaser/Monitor/MotionControl/WeldParam/LaserWeldHead）删除重复的 `_step`/`Step`/`SetStep`/`TransitionTo`/自有 EventArgs，`MapToDeviceState` 改 `protected override`；Monitor 的 `IsValidTransition` 改为 `ValidateTransition` 重写；LaserWeldHead 补自有最小枚举。
  - UI 4 文件（FormMain/ILCamPage/MonitorCamPage/MotionControlPage）：事件处理签名替换为 `WorkflowStepChangedEventArgs<TStep>`；MonitorCamPage/MotionControlPage 补 `using ...DeviceState;`。
- **附带修复（既有编译缺陷）**：`MainDeviceWorkflow` 中 `_initializing` 字段与 `RobotManager` 属性被使用但从未声明（ADR-037 遗留），已补齐；`SafetyInterlock.CheckDevice` 参数由非泛型 `DeviceWorkflowBase` 改 `DeviceStateBase`。
- **编译反馈修复**：`OnRobotDataReceived` 签名按 `EventHandler<KUKADataReceivedEventArgs>` 改为 `(object, KUKADataReceivedEventArgs)`，指令串取 `e.RobotData.EStr`；Dispose 补 `RobotManager.DataReceived` 退订。
- **已知取舍**：泛型基类 `_step` 不能标 `volatile`（CS0677），原各子类 volatile 语义降级；`MotionControlWorkflow.Dispose` 中原 `StateChanged = null` 清空订阅改为删除（基类事件派生类不可赋值）。
- 新增 Wiki 页面：`decisions/ADR-042-WorkflowStateBaseGeneric`。
- 更新 Wiki 页面：`architecture/DeviceControlArchitecture`（第 2/4/5/12/13 节）、`modules/DeviceControl`、`api/MainDeviceWorkflow`、`api/LineLaserWorkflow`、`api/MonitorCameraWorkflow`、`api/MotionControlWorkflow`、`api/WeldParamControlWorkflow`、`api/FormMain`、`api/GlobalCommData`、`index/index.md`。
- 矛盾检测：无（`DeviceFlowState` 全仓已清零，`AdaWeldSystem.Workflow` 命名空间仍不存在）。

---

## [2026-08-28 16:06:58] refactor+ingest | 设备控制架构重构收尾：代码核对 + 知识库沉淀（只保留当前架构，废止 V2/V3 版本化描述）
- 来源：用户要求「整合所有修改要求 → 核对修改项是否遗漏 → 沉淀知识库，并删除原架构描述只保留最新架构」。
- **阶段一：需求整合**。将整轮对话的修改要求归并为 7 组最终要求版本：①目录与文件重构 ②设备态四态语义 ③映射规则与禁手工赋值 ④WeldParamControlWorkflow 定位 ⑤焊缝数据链路 ⑥PowerOnInitialize 与级联 ⑦UI 重映射与残留清理。
- **阶段二：代码核对（12 项全 PASS）**。静态自检：关键类型解析 14/14、csproj 无缺失无重复（条目154）、无未注册孤儿、无 `Dispose(bool)` 违规（ADR-001）、继承链完整、设备四态正确、映射覆盖 4/4、工艺不入级联、UI using 5/5、旧符号清零、新代码无 V2/V3 表述、旧目录已删。
- **核对中发现并修复的真实缺陷**：
  - **csproj 3 条失效条目**（`Workflow\Safety\SafetyFlow.cs` / `SafetyInterlock.cs` / `FaultRecoveryManager.cs`）——文件已迁至 `MainDeviceControl\DeviceWorkflow\Safety\` 但旧条目未删，会导致构建失败。已删除，并清理 8 行「V2 架构新增文件」孤儿注释。
  - 代码注释中 3 处**架构语义错误**：`MainDeviceWorkflow` 聚合判定注释残留旧 11 态（Standby/InitializationFailed）；`WeldParamControlWorkflow` 数据流向注释误写为「英莱→EmguALG 算法」（正确：**焊缝信息即英莱线激光结果**，回调直接含 FeatureY/FeatureZ + Width0/Width1）；`CalcGalvoAmplitude` 注释引用已归档的 V2 规划文档。
  - 18 处 **V2/V3 版本化表述**（代码注释 + region 名 + 日志文本）：按用户「不再描述 V2/V3」要求全部清除，改为当前架构表述；6 处旧命名引用（`MainDeviceThread`/`LaserCamBoxTrackingWorkflow`）一并清除。
- **阶段三：知识库沉淀（删除版本化描述，只保留当前架构）**：
  - 新建 `wiki/architecture/DeviceControlArchitecture.md` — **设备控制架构唯一规范页**（13 章）：设备态四态/流程态分离 + 映射规则、三层目录、继承链、各工作流映射表、上电初始化 5 步、焊接工艺数据链路、安全互锁/故障恢复、运动控制 CAMBOX、UI 接入约定（`Step` vs `State`）。
  - 新建 `wiki/decisions/ADR-041-MainDeviceControlArchitecture.md` — 含**用户对三处架构语义的纠正记录**（设备态四态而非三态 / WeldParamControl 非设备而是工艺流程 / 焊缝信息即英莱结果）+ 4 条反例警示（勿给 `TriggerAdjustment()` 加参数、勿自创摆幅公式、基类成员勿误判为缺陷、`State`/`Step` 勿一刀切）。
  - 新建 `wiki/modules/DeviceControl.md`（替代原 DeviceStateMachine.md）；重写 `modules/Workflow.md`（职责收窄为状态契约+模拟控制）、`modules/WeldParamControl.md`。
  - 新建 API 页 3 个：`api/MainDeviceWorkflow.md`、`api/MotionControlWorkflow.md`、`api/WeldParamControlWorkflow.md`；重写 `api/LineLaserWorkflow.md`、`api/MonitorCameraWorkflow.md`。
  - **归档 6 个废弃页**至 `archive/`（均加废弃声明横幅）：DeviceStateMachine-Legacy、DeviceStateMachineAPI-Legacy、DataModels-Legacy、V3-Architecture-Legacy、V3-MotionControlArchitecture-Legacy、LaserCamBoxTrackingWorkflow-Legacy。
  - **链接修复**：19 个文件的失效链接批量重定向到新页（V3 架构页→DeviceControlArchitecture、DeviceStateMachine→DeviceControl、DataModels→LaserWeldHead、LaserCamBoxTrackingWorkflow→MotionControlWorkflow）；归档页内链接同步修复。全量红链检测：仅剩 5 处历史遗留（占位符 `XXX`、anchor 锚点、脚本路径），非本次引入。
  - 更新 `index/index.md`：架构区合并为 1 条（原 V3 两条）、新增 ADR-037、模块/API 条目重写（6 条）、归档区新增 6 条、头部新增「设备控制架构必读」导航块（含设备态四态规则与两条易误判提示）。
- 备份：`AdaWeldSystem_backup_20260828_155639.tar.gz`（代码）、`wiki_backup_20260828_155657/`（知识库）。
- 结论：Phase 2 代码核对完毕（12/12 PASS）、Phase 3 知识沉淀完毕。本环境无编译器，待 VS 实构建验证。

## [2026-08-28 10:36:04] maintenance | 代码↔Wiki 漂移修正（底部状态栏 + FloatButton 三页对齐）
- 来源：用户审查反馈——近期底部状态栏裁剪 + 新增 FloatButton 虽已 log（08-27 18:29 / 08-28 09:40 / 08-28 10:05 三条），但三次快速迭代后 Wiki 页面停在中间态，与当前代码漂移。
- 操作（仅 Wiki，无代码改动）：
  - `wiki/api/MainPage.md`：统一方法名 `IsLineLaserConnected`→`IsLineLaserRunning`；`Align` BR→LB；连接态真相源 `CameraSelector.ConnectionState`→`LineLaserWorkflow.Instance.State`；切换机制 `ConnectManual/StateMachine.TryTransition`→`wf.Start()/Stop()/Reset()`；顶部摘要 panelfloatbutton「已移除」→「锚定 panelfloatbutton 底部 60px 条」。
  - `wiki/modules/UIDesign.md`：MainPage 硬件开关小节同步 Align/真相源/切换机制；frontmatter `updated: 2026-08-07`→`2026-08-28`。
  - `wiki/api/FormMain.md`：删除已删方法 `UpdateDeviceStatus`（原误列"好范式保留"）；`InitializeSystemStatusLabel` 锚点 `toolStripSeparator2`→`Items.Insert(0,…)`；补状态栏裁剪说明（整机/流程/系统时间三项）；协作状态源更新。
- 备份：`AdaWeldSystem_backup_20260828_103614.tar.gz`（补全 08-28 两次改动缺失的压缩包备份，满足统一备份规范）。
- 矛盾检测：修正后三页与当前代码一致（Align=TAlign.LB、真相源=LineLaserWorkflow.Instance.State、toggle=Start/Stop/Reset、panelfloatbutton 已恢复）。

## [2026-08-27 18:29:40] coding | 主界面硬件快捷开关面板 + 状态栏裁剪（FloatButton 风格 6 开关 + 仅整机/流程/系统时间）
- 来源：用户需求——`MainPage.panelfloatbutton` 内以 AntdUI FloatButton 风格实现 6 个硬件快捷开关（焊接头/线激光/监控相机/运动控制器/机器人通讯/PLC通讯），红=断开 绿=连接、Tooltip=名称、图标预留接口，线激光先实现真实连接/断开判断；底部状态栏仅保留整机状态+流程状态+系统时间。
- 决策澄清（AskUserQuestion）：① 面板内 Button 方案（FloatButton 为锚定 Window 的覆盖层 Form，无法入 Panel）；② 状态栏=整机+流程+系统时间，floatbutton 仅表征硬件态。
- 操作：
  - `FormMain.Designer.cs`：删除已移除设备/操作级别标签的属性块与字段声明（toolStripLabel1/2/5/6/7、lbl_OperateLevel、lbl_LineLaserConn、lbl_MonitorConn、lbl_MotionCtrl、toolStripSeparator1/2/3）；`toolStripLabel3.Text` 由「设备状态：」改为「流程状态：」。
  - `FormMain.cs`：`InitializeSystemStatusLabel` 锚点由已删 `toolStripSeparator2` 改为 `toolStrip1.Items.Insert(0,…)`；`OperateLevelControl` 移除 `lbl_OperateLevel.Text`；删除 `UpdateDeviceStatus`（写已删标签），`uiMillisecondTimer1_Tick` 改调 `mainPage.RefreshDeviceSwitchUi()`。
  - `MainPage.cs`：新增 `using Workflow`/`DeviceStateMachine.API`；字段 `_deviceSwitchBtns`/`_deviceTooltip`/`_deviceSwitchNames`/`_deviceSwitchIcons`/`LineLaserSwitchIndex`；`InitDeviceSwitchButtons()`（FlowLayoutPanel 入 `panelfloatbutton` + 6 圆角按钮 + Tooltip）、`RefreshDeviceSwitchUi()`(public 单一刷新入口，读 `CameraSelector.ConnectionState`)、`OnDeviceSwitchClick`/`ToggleLineLaserConnection`（线激光 `ConnectManual(LoadSavedIp)`/`DisconnectManual` + `LineLaserWorkflow.StateMachine.TryTransition`，ADR-025）；构造函数调用初始化。
  - 备份：`AdaWeldSystem_backup_20260827_181458.tar.gz`。
- 知识沉淀：`wiki/api/MainPage.md`（依赖/#region/关键方法/设计约束/协作 五项对齐）、`wiki/modules/UIDesign.md`（新增硬件开关面板 + 状态栏裁剪两小节）。
- 编译安全自检：无遗留对已删控件引用（Grep 全仓 0 命中）；`TTypeMini.Success/Error`、`TooltipComponent.SetTip`、`LineLaserWorkflow.StateMachine`、`IntelligentLaserCameraRun.ConnectManual/DisconnectManual/LoadSavedIp` 均经 demo/源码核对存在；`AntdUI.In.Panel` 作为容器（Dock/Size/Text 可配、被 TableLayoutPanel 承载）`Controls` 集合有效。
- 结论：Phase 2 编码完成，Phase 3 知识沉淀完成；本环境无法编译，待 VS 实构建验证（其余 5 硬件开关为占位，仅线激光真实可测）。
---

## [2026-08-28 10:05:00] coding | 悬浮按钮锚定改为 panelfloatbutton 面板（恢复底部 60px 条）
- 来源：用户要求——悬浮按钮区域应放在之前 `panelfloatbutton` 的位置，`Config(xxx, btns, call)` 的 `xxx` 换成该面板（确认 `FloatButton` 可锚定任意 `Control`，非仅 `Form/Window`）。
- 操作：
  - `MainPage.Designer.cs`：恢复 `panelfloatbutton`（`AntdUI.In.Panel`）——`tableLayoutPanel2` RowCount 改回 3、新增第 3 行 `Absolute 60F`、`SetColumnSpan(panelfloatbutton,4)` 置于 (0,2) 全宽底部条、补字段声明、Text 置空（仅作锚定区）。
  - `MainPage.cs`：`BuildFloatButtonConfig` 锚点 `panelIO`→`panelfloatbutton`（`Config(panelfloatbutton, btns, OnDeviceFloatButtonClick)`），`MarginX/Y` 微调为 16/8 使 44px 按钮落入 60px 条内；注释更新。
- 知识沉淀：`wiki/api/MainPage.md`、`wiki/modules/UIDesign.md`（锚定对象改回 `panelfloatbutton` 面板）、本日志。
- 编译安全自检：`csharp_review.py` 对 `MainPage.cs` 0 error/1 warn（预存 `UpdateChartUI` 摘要）；无 `panelfloatbutton` 残留引用。
- 结论：悬浮开关锚定至 `panelfloatbutton` 底部条；本环境无法编译，待 VS 实构建确认按钮落位与线激光红绿切换。

## [2026-08-28 09:40:34] coding | 主界面硬件快捷开关改为真·FloatButton 悬浮覆盖层（锚定 MainPage 控件）
- 来源：用户纠正——应使用 AntdUI 真·`FloatButton` 悬浮覆盖层（参照 demo `FloatButtonDemo` 底层 `Config(Control control, ConfigBtn[] btns, Action<ConfigBtn> call)`），可锚定 Control（非仅 Window）；取消面板内 Button 方案，移除 `panelfloatbutton` 面板。
- 操作：
  - `MainPage.cs`：`InitDeviceSwitchButtons`/面板 FlowLayoutPanel 方案 → `BuildFloatButtonConfig`(构建 `ConfigBtn[]`，`Round=true` 圆形、`Type`=线激光按 `CameraSelector.ConnectionState` 定 `Success`(绿)/其余 `Error`(红)、`Tooltip`=设备名、`IconSvg` 预留接口) + `InitDeviceFloatButton`(`FloatButton.open(Config(this, btns, OnDeviceFloatButtonClick){Align=TAlign.BR})`，`MainPage_Shown` 调用) + `OnDeviceFloatButtonClick`(按 `btn.Name` 分发) + `IsLineLaserConnected`/`ToggleLineLaserConnection`(线激光 `ConnectManual/DisconnectManual` + 状态机，ADR-025) + `RefreshDeviceSwitchUi`(public，状态未变跳过，变化才 `RebuildFloatButton` 重建覆盖层) + `Rebuild/CloseDeviceFloatButton`；`DisposeComponents` 释放悬浮覆盖层。
  - `MainPage.Designer.cs`：移除 `panelfloatbutton`（`AntdUI.In.Panel`）实例化/布局/字段声明及 tableLayoutPanel2 第 3 行 60px 行（RowCount 改为 2 行），底部空间回收给图表。
- 知识沉淀：`wiki/api/MainPage.md`、`wiki/modules/UIDesign.md`（硬件开关改为悬浮 FloatButton 覆盖层、panelfloatbutton 已移除）、本日志。
- 编译安全自检：`csharp_review.py` 修复 `_check_method_doc_quality` 未传 `cls` 导致的 `NameError`（凡方法带 `///` 即崩溃），现 MainPage.cs 0 error/1 warn（预存 `UpdateChartUI` 摘要过长，非本次引入）/FormMain.cs 0 error；脚本修复属项目工具修正。
- 结论：真·FloatButton 悬浮开关落地（锚定 MainPage 控件）；本环境无法编译，待 VS 实构建 + 真机验证线激光红绿切换。

## [2026-08-27 17:43:16] coding | 主界面 ScottPlot 终版修正（轴范围回退校准框 / 渲染索引 / 删诊断）
- 来源：用户最新 4 点要求：①XY 轴范围回退「连接相机时用回调确认轴的限度（相机最大最小值，含负值，不实时规划上下限/左右限）」；②用 MinRenderIndex/MaxRenderIndex 控制本帧有效点范围；③删 BUG 测试代码；④澄清 ImageBox(30Hz)/ScottPlot(60Hz) 频率差异（ContourFrameReady 手动+16ms节流+重绘 vs ContourDataReady 无节流全量）。
- 操作（仅 `UIDesign/ControlPage/MainPage.cs`）：
  1. 轴范围锁定时 X(=数据Y)/Y(=数据Z) 一律用 `CalibrationInfo` 四角点 min/max（含负值）+ 5% 边距，连接时锁定一次；移除「纵轴 Z 用数据实际范围」临时方案（§5.15 已标记回退）。
  2. `UpdateChartUI` 以 `MinRenderIndex=0` + `MaxRenderIndex=_snapPointCount-1` 限定本帧有效点，替代清除多余点数据。
  3. 删除诊断代码：`_contourDiagEnabled`/`_diagFrameCounter` 字段及打印块；移除已废弃的 `_snapSampleRate`/`_snapOffsetX`。
  4. `AddContourLineChart` 由 `AddSignal` 改为 `AddSignalXY(_contourSignalXs,_contourSignalData)`（X 非等距用 SignalXY 保留高性能，字段类型 `SignalPlotXY`）。
  5. 备份：`AdaWeldSystem_backup_20260827_173415.tar.gz`（排除 bin/obj）。
- 知识沉淀：`lessons/IntelligentLaser-Pitfalls.md` §5.11 终版（校准框量程锁定）、§5.14 删诊断门控、§5.15 改写为回退说明；`api/MainPage.md` 私有变量/AddContourLineChart/IlCamera_ContourDataReady 三项对齐。
- 结论：Phase 2 编码完成，Phase 3 知识沉淀完成；待 VS x64 实构建验证。

## [2026-08-27 15:41:15] coding | 主界面 ScottPlot 直线 bug 修复（纵轴 Z 改用数据范围锁定）
- 来源：用户对比 ImageBox（可见起伏）与 ScottPlot（平线）截图，确认 Bug1 根因 = 纵轴 Z 锁定用校准框范围（±几 mm）远大于实际焊缝 Z 起伏（0.0x~0.x mm），轮廓被压成平线。
- 操作（仅 `UIDesign/ControlPage/MainPage.cs` 首帧轴锁定逻辑）：
  - 纵轴 Z 由「校准框四角点范围」改为「本帧数据实际 min/max + 10% 边距」（Z 范围 <1e-4 时给 ±0.5 兜底防零范围报错）。
  - 横轴 Y（沿激光线）仍用校准框范围，校准框未到则回退本帧数据 Y 范围。
  - 仍只锁定一次（`_contourAxisLocked`），满足「连接后固定视图」。
  - 备份：`AdaWeldSystem_backup_20260827_153922.tar.gz`（排除 bin/obj）。
- 知识沉淀：`lessons/IntelligentLaser-Pitfalls.md` §5.11 补正 + §5.14 直线根因定论 + 新增 §5.15；`api/MainPage.md` 回调描述补充轴锁定细节。
- 结论：Bug1（直线）/ Bug2（内存↑）/ Bug3（卡死）三处 ScottPlot 问题已全部修复；待 VS x64 实构建验证。

## [2026-08-27 15:04:52] coding | 主界面 ScottPlot 三 bug 修复（内存↑/卡死/直线）
- 来源：用户需求（①signal 显示成直线 ②程序内存持续上涨 ③主页面卡死只此表动）
- 操作（仅 `UIDesign/ControlPage/MainPage.cs`）：
  1. 删除 `IlCamera_ContourDataReady` 开头的临时调试 `return;` 桩，恢复回调工作。
  2. 重构为「生产者线程预拷贝 + 合并派发」：回调线程立即把 `points[i].Z`/Y 映射/特征点/首帧校准拷入复用数组与快照字段；用 `volatile bool _uiUpdatePending` 保证 BeginInvoke 队列最多 1 个待处理，根治逐事件派发导致的队列堆积（内存↑/卡死，Bug2/3 共因）。
  3. 新增 `UpdateChartUI()`（UI 线程）只做轻量：应用轴锁定一次 + MaxRenderIndex/SampleRate/OffsetX + 特征点显隐 + Refresh，`finally` 复位 `_uiUpdatePending`；ScottPlot 属性仅 UI 线程触碰。
  4. 新增 Bug1 诊断门控 `_contourDiagEnabled`（默认 false）：置 true 后每 ~30 帧打印 Z 数据范围与锁定轴范围，区分 轴范围过宽(a)/数据本身平(b)/字段错(c)；生产者预拷贝同时消除「延迟读被回收缓冲」候选(b)。
- 根因：`ContourDataReady` 在相机回调内无条件高频触发（对比 `NotifyFrameReady` 有 16ms 节流）；旧逻辑用 `BeginInvoke` 逐事件把重活封送 UI，相机帧率高于 UI 刷新能力时队列无界堆积 → 内存↑+卡死。
- 备份：`AdaWeldSystem_backup_20260827_145730.tar.gz`（排除 bin/obj）
- 待用户验证：Bug1 最终轴处理待诊断日志确认；VS x64 实构建确认（本环境无法编译）。
- 修改 Wiki 页面：`wiki/lessons/IntelligentLaser-Pitfalls.md`（新增 §5.14）、`wiki/api/MainPage.md`（私有变量/方法/回调描述更新）
- 矛盾检测：无

## [2026-08-27 14:15:23] maintenance | 知识库健康检查与瘦身（Issue 1/2/3 收尾）
- 来源：用户需求（知识库检查：①思考过程层级乱 ②引用 md 增多信息重复需瘦身 ③backup 文件夹/bak 文件杂用，统一仅压缩方式）
- 操作：
  1. **Issue 1 层级修复（本会话前已完成，本次复核）**：`vibecoding-workflow.md` Step 0.7/0.8 合并为 Step 0.7（Grep 定位+按行号精确读取）；SKILL.md 三处 `Step 0.8`→`Step 0.7`；`index.md` 去除"Step 0.8 图谱"废弃措辞；`AGENTS.md`"四阶段"→"五阶段速查"。
  2. **Issue 3 统一备份（本会话前已执行删除）**：彻底删除非压缩备份——`LLMWiki/logs/backup/`、`LLMWiki/raw/backup/`、`LLMWiki_backup_20260818_145339/`、`skills/.../SKILL_20260804_备份前.md`、`SKILL_v1.3.0_20260811.md`；误放的 `AdaWeldSystem_backup_20260827_134124.tar.gz` 归位项目根。
  3. **Issue 2 去重瘦身（本会话前已执行）**：`index.md` 顶部 14k 字符内联日志替换为单行"近期变更以 logs/log.md 为准"；经核查 `standards/references/` 与 `CodeSimplification`、`architecture/` 与 `project/architecture.md` 为互补非重复，保留不合并。
  4. **本次收尾（文档漂移修复）**：`vibecoding-workflow.md` Step 3.6 由"截断与按日期备份"改写为"截断（旧条目直接丢弃，不再归档）"，移除全部 `logs/backup/` 引用（目录已废弃）；同步 `AGENTS.md` 日志截断策略移除 `logs/backup/log_YYYY-MM-DD.md` 归档说明。
- 备份状态：项目根 3 份 `AdaWeldSystem_backup_*.tar.gz`（105840 / 134124 / 134602）；`logs/backup/` 已不存在（NO）。
- 修改 Wiki 页面：`wiki/project/vibecoding-workflow.md`、`AGENTS.md`、`wiki/index/index.md`（前序）、`skills/vibecoding-llmwiki/SKILL.md`（前序）
- 矛盾检测：无

## [2026-08-27 13:47:22] fix | MotionControlPage.ShowSimErrorDialog 编译错误修复（m→msg 标识符级联误报）
- 来源：用户需求 / Bug 修复（编译期 CS 错误：①上下文不存在名称"m" ②"Form 无法转换为 Target"）
- 操作：
  1. 定位 `UIDesign/TabPage/MotionControlPage.cs:340`（`ShowSimErrorDialog` 的 `else` 分支）第三参数误用未定义 `m`
  2. 修正为方法参数 `msg`（字符串内容）；`BeginInvoke` 分支的 `m` 为合法 lambda 形参，保持不变
  3. 确认 ② 为重载解析级联误报：`Form.ActiveForm` 作为 Modal owner 合法（Modal owner=Control），`XMLfile.cs` 同款写法可编译
  4. 项目备份 `AdaWeldSystem_backup_20260827_134602.tar.gz`
- 修改代码文件：`UIDesign/TabPage/MotionControlPage.cs`（1 处标识符修正）
- 新增 Wiki 页面：`lessons/AntdUI-Modal-Config-Overload-Cascade.md`
- 更新 Wiki 页面：`api/MotionControlPage.md`、`wiki/index/index.md`、`lessons/AntdUI-Complete-Reference.md`
- 矛盾检测：无

## [2026-08-27 11:12:36] coding | 模拟停止反馈修复（去重/清晰停止原因/按钮态/弹窗类型）
- 来源：用户需求（停止日志不体现原因且重复；异常无红色按钮+无弹窗；明确两类弹窗：无需确认用 Message、需确认用 Modal）
- 修改代码文件：`UIDesign/TabPage/MotionControlPage.cs`、`Workflow/Device/SimulationController.cs`
  - `SimulationController.Disable()` 幂等化：仅当由开启→关闭才记「模拟模式关闭」，消除重复日志
  - 新增 `LogSimStopSummary(reason)`：汇总线激光/V3跟踪/监控/模拟模式态，输出「人话」式停止原因
  - 新增 `ShowSimStopMessage(reason)`：正常停止用 `AntdUI.Message.info`（无需确认）
  - `ShowSimErrorDialog` 由 `Message.error` 改为 `AntdUI.Modal.open(TType.Error)`（需确认）+ 按钮转红色「清理异常」；启动任一步骤异常均经其置红，后续步骤 `_simError` 短路
  - 停止分支先退订事件再 `StopSimulationFlows`，避免异步回调二次进入停止路径；`CleanupSimError`/`StopSimOnWeldComplete`/停止分支均补 `ShowSimStopMessage`+`LogSimStopSummary`
- 知识沉淀：[[api/MotionControlPage]]、[[api/DeviceControlWork]]（当次记录原名 `api/SimulationController`，2026-08-28 更名）、[[lessons/SimulationC-Mode-Interruption]]、[[guides/WinForms-UI-Threading]]、[[index/index]]

## [2026-08-27 10:04:53] coding | 模拟按钮清理恢复 + 启动异常弹窗
- 来源：用户需求（点击开启测试异常后点清理异常按钮无反应不恢复；启动模拟测试异常除 log 外需弹对话框）
- 修改代码文件：`UIDesign/TabPage/MotionControlPage.cs`
  - `CleanupSimError()` 重构：`StopSimulationFlows`/`Reset`/`Disable` 各自独立 try/catch，`SetSimButtonMode(Start)` 移入 `finally`（按钮复位必定执行）
  - `BtnStartSim_Click` 入口加 `_simError || LineLaserWorkflow.Instance.State == ErrorAborted` 兜底判定
  - 新增 `ShowSimErrorDialog(string)`：`ShowLog` + `AntdUI.Message.error`，`InvokeRequired` 时 `BeginInvoke` 封送
  - 启动路径四处 catch（预启动 Reset / StartLineLaserWithPending / V3跟踪 Start / 异步挂起 Start）替换为 `ShowSimErrorDialog`
- 更新 Wiki：`api/MotionControlPage.md`（清理恢复 + 启动弹窗 + 路径漂移 Sub2UI→TabPage 修正）、`lessons/SimulationC-Mode-Interruption.md`（新增清理恢复/启动弹窗陷阱）、`index/index.md`（近期变更）、本日志
- 矛盾检测：无；备份 `AdaWeldSystem_backup_20260827_0953_simbtn/`

## [2026-08-27 09:47:17] coding | 主界面轮廓 Signal 初始不可见（修复未连相机显示假轮廓）
- 来源：用户需求（程序启动未连接相机时显示了一段奇怪的轮廓点，要求初始化不显示无关点）
- 修改内容：
  1. `MainPage.AddContourLineChart`：`AddSignal` 后立即 `_contourSignalPlot.IsVisible = false`（避免全 0 数组渲染 Z=0 平直假轮廓线）
  2. `MainPage.IlCamera_ContourDataReady`：确认 `pointCount > 0` 后首帧置 `_contourSignalPlot.IsVisible = true`
  3. `MainPage.SubscribeContourCamera`：重订阅/重连时复位 `_contourSignalPlot.IsVisible = false`（null 守卫）防残留
  4. 默认轴范围 `SetAxisLimits` 保留，呈现空坐标 + 标签无数据态，不显示无关点
- 修改代码文件：AdaWeldSystem/UIDesign/ControlPage/MainPage.cs
- 更新 Wiki 页面：modules/IntelligentLaserCam、decisions/ADR-035-LineLaserResponsibilitySplit、lessons/IntelligentLaser-Pitfalls（§5.13）、wiki/index/index.md
- 矛盾检测：无（与 §5.9 每帧 Refresh、§5.11 轴锁定、§5.12 信号映射均一致）

---

## [2026-08-26 17:38:13] coding | 主界面轮廓图 V2：校准框定轴范围 + 特征点散点叠加
- 来源：用户需求（轴范围由四边基准校准框确定，显示轮廓点和特征点，不转 pixel，直接 mm 坐标系）
- 修改内容：
  1. MainPage.AddContourLineChart：新增 AddScatter 特征点散点（红色实心圆，markerSize=8），初始空数组
  2. MainPage.IlCamera_ContourDataReady：①每帧从 CalibrationInfo 四角点计算 Y/Z 轴范围（mm，+5% 边距），作为 SetAxisLimits 真相源；② 轮廓线 Signal 保持 SampleRate+OffsetX 映射 mm；③ HasValidResult 时更新特征点坐标（FeatureY/FeatureZ），无效则清空；④ 每帧 SetAxisLimits 双保险锁定范围
  3. 轴范围从 const 改为字段变量，支持校准框动态更新；无校准框时回退默认值（Y:±30, Z:-10~50）
- 影响模块：UIDesign/MainPage
- 相关 Wiki：[[modules/UIDesign]]（MainPage 描述更新）

## [2026-08-27 09:18:00] coding | 主界面轮廓 Signal 轴映射核对（Y→X / Z→Y + 首末点锚定防镜像）
- 来源：用户需求（检查 ScottPlot 信号是否正确：Point3D 的 Y 和 Z，Y 做 X 轴、Z 做 Y 轴）
- 修改内容：
  1. MainPage.IlCamera_ContourDataReady：确认 `_contourSignalData[i]=points[i].Z`（Z→Y 轴）、`SampleRate/OffsetX` 由 `points[i].Y` 推导（Y→X 轴）、特征点 `FeatureY→X`、`FeatureZ→Y`，映射正确
  2. 将 `OffsetX/SampleRate` 由「全局 Y 极值」改为锚定「首末点真实 Y」：英莱点默认按 Y 由小到大排列（首末=min/max，零回归），且若点序变化（大→小）也不会把 X 轴左右镜像（避免与 imageBox 朝向相反、轮廓显示不对）
- 影响模块：UIDesign/MainPage
- 相关 Wiki：[[lessons/IntelligentLaser-Pitfalls]] §5.12、`decisions/ADR-035-LineLaserResponsibilitySplit`

## [2026-08-27 09:28:00] coding | imageBox/ScottPlot 坐标系区分澄清 + 英莱点 Y 排序确认
- 来源：用户澄清（imageBox 因像素只取正值需 center+y*rate 平移；ScottPlot 直接绘原始坐标、负值如实显示，两者不必一致；英莱轮廓点默认按 Y 由小到大排列）
- 修改内容：
  1. MainPage 注释补充：ScottPlot 绘原始坐标（负值如实显示）、不做 imageBox 式平移；两者仅朝向一致、视图不重合属预期
  2. 确认英莱轮廓点默认按 Y 由小到大排列，首末锚定 = min/max
- 影响模块：UIDesign/MainPage（注释）、LLMWiki 知识库
- 相关 Wiki：[[lessons/IntelligentLaser-Pitfalls]] §5.12、[[modules/IntelligentLaserCam]]、`decisions/ADR-035-LineLaserResponsibilitySplit`

## [2026-08-26 17:25:48] coding | 主界面轮廓图修复：X轴mm映射 + 固定轴范围 + 锁定缩放平移
- 来源：用户需求（相机连接后回调反馈范围适用于主页面 ScottPlot，显示不全/横纵轴数据错误；固定轴范围不允许缩放）
- 修改内容：
  1. MainPage.AddContourLineChart：X 轴标签改"Y 轴（沿激光线，mm）"；新增 Configuration 禁用滚轮缩放/左拖平移/右拖缩放/中拖缩放；初始轴范围 SetAxisLimits(-30,30,-10,50) mm
  2. MainPage.IlCamera_ContourDataReady：每帧从轮廓点云计算 Ymin/Ymax，设置 SignalPlot.SampleRate=(Ymax-Ymin)/(N-1) + OffsetX=Ymin，将 X 轴从点索引映射到物理 mm 坐标；每帧重置 SetAxisLimits 双保险固定范围；移除 AxisAutoY() 自适应
  3. 新增 4 个常量 ContourYMin/ContourYMax/ContourZMin/ContourZMax 统一管理固定轴范围
- 影响模块：UIDesign/MainPage
- 相关 Wiki：[[guides/Project-Tools]]（SignalPlot mm 映射 + 锁轴技巧）、[[modules/UIDesign]]（MainPage 描述更新）

## [2026-08-26 17:01:46] coding | 模拟流程4项修复：按钮背景色、停止恢复、去日志、主界面轮廓传导
- 来源：用户需求
- 修改内容：
  1. MotionControlPage.SetSimButtonMode：运行中/异常态 Ghost=false 实现红色实心背景（原为 Ghost=true 只改文字色），停止态 Ghost=true+Type=Primary 恢复幽灵按钮初始样式
  2. MoveControlData.ComputeAndCacheHorizontalMove：移除「水平移动缓存 键」过频日志行（符合代码精简规范）
  3. FormMain.LoadNavAndPages：显式调用 mainPage.AddContourLineChart() + AddNewDataLineChart()，修复主界面轮廓图未初始化、英莱相机 ContourDataReady 事件未订阅导致轮廓空白的问题
- 影响模块：UIDesign/MotionControlPage、MotionControl/MoveControlData、UIDesign/FormMain
- 相关 Wiki：[[lessons/SimulationC-Mode-Interruption]]、[[api/MotionControlPage]]、[[modules/UIDesign]]

## [2026-08-26 16:33:08] standard | 注释规范调整：取消私有方法禁 /// 要求，改为注释标准化
- 来源：用户需求（不再强制要求私有方法不使用 ///，改为注释要求标准化）
- 修改内容：
  1. **主规范**（`wiki/standards/CodeSimplification.md`）：
     - 规则②标题从「公共必须，私有不写」改为「标准化，不限公私」
     - 公共/受保护方法「建议写」，私有方法「可选」
     - 无论公私，只要写了 `///` 就必须符合 XML 注释规范（summary 20字 + param/returns 完整）
     - 检查清单同步更新
  2. **引用规范**（`wiki/standards/references/rules-file-organization.md`）：
     - 常见问题从「AI 把私有方法也写满 ///」改为「AI 给私有方法写的 /// 不规范」
  3. **检查脚本**（`scripts/csharp_review.py`）：
     - 移除「私有方法不应有 /// 注释」的检查项
     - 新增 `_check_method_doc_quality()` 辅助函数，提取公共注释质量检查逻辑
     - 私有方法有 `///` 时同样执行标准化检查（summary/param/returns）
  4. **进度文档**（`wiki/standards/CodeSimplification-progress.md`）：
     - A 类修复约束从「删私有方法多余 ///」改为「/// 注释标准化」
- 影响：之前被标记为 info 的"私有方法不需要 ///"问题不再报告；但私有方法若写了不规范的 ///（缺 param、summary 超长等）会报告 warn

## [2026-08-26 16:27:01] revert | 回退渐进式启动与子页懒加载，恢复同步全量初始化
- 原因：用户反馈未感知到加速效果，反而出现显示比例问题
- 操作：
  1. **FormMain 回退**（`UIDesign/MainWindow/FormMain.cs`）：
     - 恢复构造函数同步初始化（`PowerOnInitialize()` + `Start()`）
     - 移除 Shown 事件与 `InitializeDevicesAsync()` 异步逻辑
     - 子页面恢复全量实例化（MainPage/navPageParam/navPageImage/dataPage 全部在构造函数中 new）
     - `LoadNavAndPages` 恢复全量添加 Tab，移除懒加载 `EnsurePageLoaded`
     - 移除 `_lazyPages`/`_pagesInitialized`/`_deviceInitStarted` 字段
  2. **NavPage 调用回退**：`LoadTabsLazy()` → `LoadTabs()`（全量加载）
  3. **保留项**（不受回退影响）：
     - CameraSelector 简化（删 Load/Save/DetectConnection/SelectReal，默认英莱一步到达）
     - JobManager 移除（英莱自带 Job 系统）
- Wiki 更新：
  - `wiki/decisions/ADR-034-ProgressiveStartup.md`：status 改为 rejected，加回退说明
  - `wiki/modules/UIDesign.md`：FormMain/NavPage 描述回退
  - `wiki/index/index.md`：ADR-030 条目标记「已回退」

## [2026-08-26 16:16:21] refactor | 渐进式启动优化 + CameraSelector 简化 + 子页懒加载
- 来源：用户需求（程序加载慢、FormMain 先显示父窗口再加载子页面）
- 操作：
  1. **CameraSelector 简化**（`LineLaserCam/Api/CameraSelector.cs`）：
     - 删除 `Load()`/`Save()`/`DetectConnection()`/`SelectReal()`
     - 默认直接使用英莱线激光相机，一步到达
     - 保留 `SelectVirtual()`/`SelectIntelligentLaser()`/`Active`/`Kind`/`ConnectionState`/`SetWorking()` 运行时接口
  2. **FormMain 渐进式启动**（`UIDesign/MainWindow/FormMain.cs`）：
     - 构造函数瘦身：移除 `JobManager.Initialize()`/`CameraSelector.Load()`/`CameraSelector.DetectConnection()`
     - 新增 `Shown` 事件：`Task.Run` 异步执行 `PowerOnInitialize()` + `Start()`
     - 子页面 Tab 懒加载：`DataReviewPage` 选中时才实例化
     - `LoadNavAndPages` 重构：首页面立即加载，其余占位
  3. **NavPage 懒加载**（`UIDesign/ControlPage/NavPage.cs`）：
     - 新增 `LoadTabsLazy()`：接收 `Func<UserControl>` 工厂函数
     - Tab 首次选中时才实例化子页，首页面立即加载
     - 旧 `LoadTabs()` 签名保留，向后兼容
  4. **SimulationController 修复**（`Workflow/Device/SimulationController.cs`）：
     - `SelectReal()` → `SelectIntelligentLaser()`
- Wiki 沉淀：
  - 新建：`wiki/decisions/ADR-034-ProgressiveStartup.md`
  - 更新：`wiki/modules/UIDesign.md`（FormMain/NavPage 描述）
  - 更新：`wiki/index/index.md`（决策记录 + API 索引）

## [2026-08-26 15:07:40] refactor | 英莱线激光 IntelligentLaserCameraRun + 3 个 UI 类全量代码精简（注释+逻辑）
- 来源：用户需求（类级 summary 一行 20 字约束 + 英莱全类代码精简）
- 操作：
  1. **标准更新**：`standards/CodeSimplification.md` 补充类/结构体/枚举/接口级 `/// <summary>` 一行 20 字约束
  2. **注释精简**（4 个文件，合计 ~327 行）：
     - `IntelligentLaserCameraRun.cs`：类级 10 处、public 属性/事件 17 处、private 方法 19 处、public 字段 36 处
     - `ILCamPage.cs`：类级 1 处、private 方法 23 处
     - `ILAlgoPage.cs`：类级 2 处、private 方法 18 处
     - `ILParamPage.cs`：类级 2 处、private 方法 7 处
  3. **代码逻辑精简**（4 个文件，合计 ~68 行）：
     - `IntelligentLaserCameraRun.cs`：删除 `Read64Bytes` 死包装、统一 `Log()` 调用、`MillionOutlineCallback` 去重（手动/自动模式共有逻辑外提）、`ConvertContourToMatDemo` 消除回退分支重复计算
     - `ILCamPage.cs`：内联 3 个一次性临时变量、提取 btnApplyJob/btnApplyFps 共用刷新逻辑、`UpdateApplyButtonsState` 展平嵌套 if
     - `ILAlgoPage.cs`：内联 4 个临时变量 + 去冗余 null 检查、`LoadIlParamsToGrid` 调用 `FormatCellValue` 去重、2 处嵌套 if 展平、5 处字符串拼接转 `string.Format`
     - `ILParamPage.cs`：8 处变量内联（out var + `?.` 回退）、提取 `FormatRange` 共用方法、`UpdateConnLabel` 三元简化、去冗余 null 检查
- 编译验证：Debug 构建通过，0 错误
- 约束遵守：ADR-001 Dispose 模式无违规、ADR-002 C# 7.3 语法合规、公共 API 签名零变更、业务逻辑等价
- 总效果：4 文件合计减少约 395 行（~327 行注释 + ~68 行逻辑）

---
## [2026-08-26 15:30:00] fix | 英莱相机释放流程优化：消除重复 WaitForCallbacksToFinish + 缩短超时
- 来源：用户反馈（程序关闭释放缓慢）
- 操作：
  - `IntelligentLaserCameraRun.cs` — `ShutdownPeripherals()` 中移除 `WaitForCallbacksToFinish()` 调用，消除与 `ReleaseNativeResources()` 中的重复等待（之前两次等待合计最多 1000ms）
  - `IntelligentLaserCameraRun.cs` — `ReleaseNativeResources()` 中仅在 `UnInitSDK()` 后统一调用一次 `WaitForCallbacksToFinish()`，移除 `Thread.Sleep(20)`
  - `IntelligentLaserCameraRun.cs` — `CallbackWaitTimeoutMs` 从 500 缩短到 200ms（UnInitSDK 后在途回调应快速归零）
  - 更新相关注释说明释放流程优化
- 影响：英莱相机释放总等待时间从最多 1020ms 降至最多 200ms，显著加速程序关闭

---
## [2026-08-25 17:42:34] fix | 英莱 JOB 参数过滤全空修复 + JOB 切换同步主 UI
- 来源：用户反馈（Job 参数全被过滤掉 / job 切换需同步主 UI）
- 操作：
  1. `ILAlgoPage.cs`：`IsDisplayParam` 匹配策略修正——display 键带 `params_` 前缀而 SDK 参数名不带（`inspect_`/`baseline_`/`segment_`/`camera_` 前缀，由 `GetParamGroup` 佐证），改为词级匹配（去前缀相等 + 词级后缀/前缀）；**过滤后为空回退全显**（display 与 SDK 参数名格式不匹配时保底，避免参数表空白）
  2. `ILCamPage.cs`：订阅 `_ilCamera.JobParamsChanged`（构造订阅 + HandleDestroyed 退订），新增 `OnIlJobParamsChanged` 处理器——切 JOB/改参数（ILAlgoPage 或工作流触发）后封送 UI 线程刷新 `cmbJob` 下拉 + 应用按钮态（job 切换同步主 UI）
- 修改代码文件：`UIDesign/SubView/ILAlgoPage.cs`、`UIDesign/TabPage/ILCamPage.cs`
- 更新 Wiki 页面：`modules/IntelligentLaserCam.md`
- 矛盾检测：无（与 2026-08-25 主变更一致，为后续修正）

---
## [2026-08-25 17:26:41] coding | 英莱三态精简 + 模拟C模式修复 + JOB参数过滤 + 弹窗修复（5 项需求）
- 来源：用户需求（英莱新创job弹窗空白 / 传感器激光按钮逻辑 / JOB参数过滤 / 模拟按钮样式 / 模拟C模式中断）
- 操作：
  1. `IntelligentLaserCameraRun.cs`：状态精简为三态 isConnected/isLaserOn/isCameraOn——删 `_isRunning`/`_isOpened` 字段、`IlHardwareStatus` 类、`DetectHardwareStatus()`（更名 `SyncHardwareStatus()`，无快照直同步本地字段+`_scanRateHz`）；`IsRunning` 派生 `_isCameraOn`；`IsLaserOn()`/`IsCameraOn()` 改本地状态读取（连接时同步一次"第一次正确"、`SetLaser`/`SetSensor` 成功后本地更新）；用户澄清 `StCtrl.DwCameraEnable` 由 `SetSensor(bool)` 控制；`IlJointTypeInfo` 新增 `DisplayKeys`（jointtypelist.json display 键集）+ `GetJointTypeDisplayKeys(int)` API；`OpenSensor`/`SensorRunContinue`/`SensorStop`/`ScanSensors`/`FetchAllJobParams`/`ApplyJobParams` 的 `_isOpened` 守卫改 `_isConnected`
  2. `ILCamPage.cs`：连接态改 `_ilCamera.IsConnected` 为真相源（独立调试页不再依赖 LineLaserWorkflow 状态机）；构造函数初始化同步条件改相机已连接判断；`SyncFromHardwareCore` 调 `SyncHardwareStatus()`；按钮 text/ExtraMouseDown 读本地状态（点击立即生效）
  3. `ILAlgoPage.cs`：新建 JOB 弹窗空白修复——`AntdUI.FlowPanel{Dock=Fill}` 改 `FlowLayoutPanel`（明确 Width=300/Height=360/AutoScroll）+ `Modal.Config(TType.Info){Width=320}`（参照 ShowInputStringDialog 范式）；`RefreshJobParams` 按当前 Job 接头类型 display 键集过滤参数表（`params_` 前缀兼容匹配，display 缺失回退全显）
  4. `MotionControlPage.cs`：`SetSimButtonMode(Stop)` 按钮 Type 改 `TTypeMini.Error`（运行中红色激活态），Start 恢复 `_btnDefaultType`
  5. `LineLaserWorkflow.cs`：模拟模式自驱动——`InitializeWorker` 开头 C 模式显式 `SelectIntelligentLaser()`（根因：Enable(C) 的 SelectReal() 选 SmartRay 占位）；`ExecutePreWork` 完成模拟分支自驱动转 Starting；`ExecuteStarting` 虚拟相机（`_ilCamera==null`）跳过开外设、数据稳定默认通过、模拟分支自驱动转 Working；`ExecuteWorking` 虚拟相机识别有效性默认通过不累计失败
- 修改代码文件：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`、`UIDesign/TabPage/ILCamPage.cs`、`UIDesign/SubView/ILAlgoPage.cs`、`UIDesign/TabPage/MotionControlPage.cs`、`Workflow/Device/LineLaserWorkflow.cs`
- 新增 Wiki 页面：`lessons/SimulationC-Mode-Interruption.md`
- 更新 Wiki 页面：`modules/IntelligentLaserCam.md`、`modules/Workflow.md`、`api/IntelligentLaserCam.md`、`lessons/IntelligentLaser-JobFlowPanel.md`、`wiki/index/index.md`
- 备份：`AdaWeldSystem_backup_20260825_172135.tar.gz`
- 矛盾检测：无（三态精简与 2026-08-24 UiStateSimplification 案例一致；`IsCameraOn`=DwCameraEnable 语义按用户澄清保留）

---
## [2026-08-25 15:57:09] maintenance | 每周日志截断（保留最新 50 条）

- **触发条件**：条目数 90 > 50 阈值
- **截断前条目数**：90
- **截断后条目数**：50
- **备份条目数**：40
- **备份文件**：`logs/backup/log_2026-08-25.md`（已新建）
- **执行方式**：Python 脚本直写文件系统

## [2026-08-25 15:57:09] audit | 每周 LLMWiki 例行维护（知识库自检 + 代码漂移检测 + 日志截断）

- **维护类型**：每周例行 Phase 4 Lint 健康检查
- **第一部分 - 知识库全量自检**：
  1. 矛盾检测：发现 1 处 ADR 编号冲突（ADR-035 重复）—— `ADR-026-V3-Yinglai-DataFlow.md` 与 `ADR-026-UnifiedInitStateMachine.md` 编号冲突；已将前者重编号为 ADR-029（YinglaiDataFlow）并更新全部 6 处引用
  2. 孤儿页面检测：发现 1 个孤儿页面（`decisions/ADR-026-V3-Yinglai-DataFlow.md`）—— 重编号为 ADR-029 后已补入 index.md 索引
  3. 红链检测：发现 1 处红链（`lessons/IntelligentLaserSensorControl.md` 中 `decisions/ADR-032-CodeSimplification` 缺少 Standard 后缀）—— 已修复为 `decisions/ADR-022-CodeSimplificationStandard`（本行原写作 `...` 会被审计脚本误判为红链，2026-09-01 改为代码体）
  4. 外链完整性：扫描发现约 119 处路径引用过时/缺失（Comm S7 路径、Workflow 二级子目录、UI ViewPage→SubView、命名空间漂移等）
- **第二部分 - 代码漂移检测（Grep 方式）**：
  1. 检测到 14 项漂移（8 项文件路径/目录结构、4 项命名空间、2 项类名）
  2. 已修复 6 个 wiki 页面中的关键漂移：Comm S7 路径（`CommBase/S7Net/`→`PLC/Siemens/`）、Workflow 目录结构（Device/+Safety/）、UIDesign ViewPage→SubView、线激光相机命名空间（`LineLaserCam.` 前缀）、LLCamWorkJob→ILCamPage
  3. 剩余路径漂移为非关键引用，待后续逐步清理
- **第三部分 - 日志截断与备份**：见本次截断记录条目
- **修复统计**：修复 ADR 编号冲突 1 处、孤儿页面 1 个、红链 1 处、路径/命名空间漂移约 22 处（覆盖 6 个 wiki 页面）
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`decisions/ADR-035-LineLaserResponsibilitySplit.md`（重命名）、`index/index.md`（新增 ADR-029 条目）、`api/LineLaserWorkflow.md`、`modules/Workflow.md`、`modules/UIDesign.md`、`modules/IntelligentLaserCam.md`、`api/IntelligentLaserCam.md`、`lessons/IntelligentLaserSensorControl.md`、`modules/Comm.md`、`modules/SmartRayCam.md`
- **矛盾检测**：修复后复检无新增矛盾
- **代码漂移**：关键漂移已修复，非关键漂移待后续迭代

## [2026-08-24 13:55:04] refactor | UI 状态判断精简策略总结 + ILAlgoPage/ILParamPage 冗余修复

- **策略总结**：扫描全 `UIDesign/`，整理 UI 状态精简四原则（真相源唯一/单一控制函数/统一刷新入口/集中状态标签）为新建标准页 `wiki/standards/UiStateSimplification.md`（补 ADR-028 排除的 UI 层），并在 `index.md` 代码精简规范区路由、ADR-028 相关页交叉引用。
- **冗余扫描结论**：`ILCamPage` 上轮已修；`ILAlgoPage`/`ILParamPage` 同存 `_ilConnected` 本地缓存（脱离 `IsConnected` 真相源）需修；`MotionControlPage.SetSimButtonMode`/`FormMain.UpdateDeviceStatus` 已是好范式引用；`MonitorCamPage._isMonitoring` 等本地活动标志合理保留。
- **修复**（`ILAlgoPage.cs` / `ILParamPage.cs`）：删除 `_ilConnected` 字段，连接判断与标签统一直读 `_ilCamera.IsConnected`（InitIlModule/UpdateConnLabel/LoadParams/按钮守卫），消除 stale 缓存。
- **Wiki 同步**：新建 `standards/UiStateSimplification.md`、`index.md` 路由、`ADR-028` 交叉引用、`modules/UIDesign.md` ILAlgoPage/ILParamPage 行、本日志。
- **自检**：两文件 `_ilConnected` 全清除、无外部引用；C# 7.3 合规、未新增 Dispose(bool)；备份 `AdaWeldSystem_backup_20260824_135206.tar.gz`。未在 VS 实编。

## [2026-08-24 13:37:45] refactor | ILCamPage 传感器控制精简 + 激光/传感器按钮 text 统一

- **需求（用户澄清）**：① 传感器是否启动必须用 `StCtrl.DwCameraEnable`（=`IsCameraOn()`）判断；② `SetSensor()` 才是线激光启停传感器的方式，`SetCaptureCamera()` 非线激光工作方式、舍弃；③ btnLaser/btnCaptureCamera/SyncFromHardwareCore/UpdateConnectionUiCore 在 text 与状态判断上重复多块，需精简为一个函数控制按钮状态与 text。
- **改动**（`UIDesign/TabPage/ILCamPage.cs`）：移除本地 `_isLaserOn`/`_isCameraOn` 副本（改由 `IsLaserOn()`/`IsCameraOn()` 真相源）；`btnCaptureCamera_Click` 改用 `SetSensor(!IsCameraOn())`、删 `SetCaptureCamera` 调用；`btnLaser_Click` 改用 `SetLaser(!IsLaserOn())`；`SyncFromHardwareCore`、`UpdateConnectionUiCore` 断开分支的重复 text 块收敛到新增单一函数 `UpdateLaserSensorUi()`（基于硬件真相源统一设置 btnLaser/btnCaptureCamera 的 text 与 ExtraMouseDown）。
- **Wiki**：`api/IntelligentLaserCam.md` 修正 `SetSensor/SetCaptureCamera` 说明 + `DetectHardwareStatus` 返回字段（`SensorRunning` 已注释移除）；新建 `lessons/IntelligentLaserSensorControl.md`；`index.md` 教训表 + `modules/UIDesign.md` ILCamPage 行 + 本日志同步。
- **自检**：5 个受影响符号全在 ILCamPage.cs，无外部调用；`SetCaptureCamera` 仅从页面移除、后端 `LineLaserWorkflow` 仍保留合法使用；C# 7.3 合规；备份 `AdaWeldSystem_backup_20260824_133438.tar.gz`。未在 VS 实编（本环境无法编译）。

## [2026-08-24 10:39:22] refactor | ILCamPage UI 状态刷新统一入口

- 来源：用户需求（在线激光页面三个状态变更函数疑似迭代重复写，统一为一个接口）
- 依据：`decisions/ADR-021-LineLaserWorkflowRefactor`（状态标签唯一刷新）、`decisions/ADR-022-CodeSimplificationStandard`（代码精简）、[[guides/WinForms-UI-Threading]]（InvokeRequired 封送）
- 操作：
  1. 在 `AdaWeldSystem/UIDesign/TabPage/ILCamPage.cs` 新增 `[Flags] enum RefreshUiScope { Connection=1, Mode=2, Hardware=4 }` 与单入口 `RefreshUi(RefreshUiScope scope)`（内置 InvokeRequired 封送）
  2. 原 `UpdateConnectionUi` / `UpdateModeUi` / `SyncFromHardwareAfterConnect` 重命名为 private `UpdateConnectionUiCore` / `UpdateModeUiCore` / `SyncFromHardwareCore`，仅由 `RefreshUi` 调用；删除 `UpdateModeUi` 内联 `UpdateConnectionUi` 的嵌套
  3. 调用方收敛：构造函数 `RefreshUi(Connection|Mode)` + Standby 时 `RefreshUi(Hardware)`；`btnConnect_Click` `RefreshUi(Hardware)` + `RefreshUi(Connection|Mode)`；`OnWorkflowStateChanged` `RefreshUi(Mode|Connection)`；`OnIlStateChanged` `RefreshUi(Connection)` + Standby 时 `RefreshUi(Hardware)`
  4. 备份：`AdaWeldSystem_backup_20260824_103514.tar.gz`
- 影响：5 个刷新相关函数全部局限于 ILCamPage.cs，无外部调用方，编译安全自检通过（无新增 Dispose(bool)、C# 7.3 合规）
- 知识沉淀：[[modules/UIDesign]]（ILCamPage 说明）+ 新建 [[lessons/UiRefreshUnifiedEntry]] + [[index/index]] 教训表新增条目

## [2026-08-21 15:46:30] refactor | 代码精简第三轮（EmguALG/MotionControl/WeldParam/SqlLite + Workflow残留）

- 来源：用户需求（按 vibecoding-llmwiki 流程做一次代码/日志/注释精简）
- 依据：[[standards/CodeSimplification]]（四维度代码 + 三规则注释 + 日志去符号）
- 操作：
  1. **EmguALG**（注释精简为主）：
     - `JobManager.cs`：类/方法注释多行合并为单行，补全 `param`/`returns`，删除过程性步骤注释
     - `AlgorithmManager.cs`（PipelineManager）：类/方法注释精简，删除 Execute 内阶段标题注释和 CalculateSeamFeatures 内步骤注释，补全参数文档
     - 日志已合规（归集 + 无符号），未改动
  2. **MotionControl**：
     - `MoveControlData.cs`：新增 `Log()` 辅助方法，将直调 `GlobalCommData.ShowLog` 改为类内归集；修复 `"水平移动距离缓存: 键={0} -> 移动={1}"` 符号日志 → ` "水平移动缓存 键 {0} 移动 {1}"`；类/方法注释大幅精简
     - `ZMotionAxis.cs`：类注释 + 构造函数 + MoveTo 方法注释精简，删除"设置速度"/"启动绝对运动"等过程注释
  3. **WeldParamControl**：
     - `WeldProcess.cs`：新增 `Log()` 辅助方法，将 6 处 `GlobalCommData.ShowLog(_tag, ...)` 统一归集；修复 `=` / `：` 符号日志 3 处；类注释精简
     - `WeldDataManager.cs`：修复 2 处异常消息全角冒号 `：` → 空格分隔
  4. **SqlLiteDatabase**：
     - `SQLiteDataBase.cs`：修复 6 处异常消息符号（`SqlString=` / `异常信息：` / `创建表失败：`）→ 纯文字空格分隔
  5. **Workflow 残留符号补漏**：
     - `LaserCamBoxTrackingWorkflow.cs`：`"状态迁移: {0} → {1} ({2})"` → `"状态迁移 {0} 到 {1} 原因 {2}"`
     - `LineLaserWorkflow.cs`：3 处 `"非法状态转换: {0} -> {1}"` → `"非法状态转换 {0} 到 {1}"`；2 处 `BeginStarting 忽略：` → 空格；1 处 `"工作流异常终止 - 原因: {0} 终止码: {1}"` → 空格分隔
     - `MonitorCameraWorkflow.cs`：`"非法状态转换: {0} → {1}，已忽略"` → 去符号；`"模拟模式：监控相机选择不工作"` → 空格
  6. **IntelligentLaserCam 漏网补漏**（Phase 4 发现）：
     - `IntelligentLaserCameraRun.cs`：修复 6 处符号日志（`IP=` / `帧率=` / `model=` / `SendCycle=` / `ret=` / `已配置:` / `异常:`）→ 纯文字空格分隔
  7. **编译验证**：MSBuild Debug|AnyCPU 构建成功，无新增错误/警告
- 新增代码文件：无
- 修改代码文件：`EmguALG/EmguConfiger/JobManager.cs`、`EmguALG/EmguConfiger/AlgorithmManager.cs`、`MotionControl/MoveControlData.cs`、`MotionControl/ZMotion/ZMotionAxis.cs`、`WeldParamControl/WeldProcess.cs`、`WeldParamControl/WeldDataManager.cs`、`SqlLiteDatabase/SQLiteDataBase.cs`、`Workflow/Device/LaserCamBoxTrackingWorkflow.cs`、`Workflow/Device/LineLaserWorkflow.cs`、`Workflow/Device/MonitorCameraWorkflow.cs`、`LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`
- 新增 Wiki 页面：无
- 更新 Wiki 页面：`wiki/standards/CodeSimplification.md`（追加第三轮覆盖记录表格）
- 矛盾检测：无
- ADR/Lessons 违规检查：无（Dispose 全部在 Designer.cs，无新增公共签名变更）
- 遗留：SmartRay/HikRobot `ApiCore/` 为厂商 SDK 原生代码，不在项目精简范围

---

## [2026-08-21 14:42:19] audit | 注释全量精简检测（R1~R4 + 规则③，只检不改）
- 来源：用户需求（对注释做一次全量精简检测）
- 操作：
  1. **检测范围**：113 个非 UI .cs 文件（排除 UIDesign/Properties/3rdDepend/bin/obj），39,018 行；依据 [[standards/CodeSimplification]] 注释三规则 + 日志去符号细则④
  2. **合规结论**：R2 同义注释 0 处；R3 公共接口缺 `<param>` 0 处（抽查 IMotionController/IDeviceStateMachine 确认）；`//` 行注释 1,460 行均为步骤/原因说明，规则③无违规；注释密度 Top 文件（WeldActionRecord 60.3% / IMotionController 52.2%）均为接口与数据模型类，属规范要求
  3. **R1 过程性注释残留 9 处**：需求引用 3 处（CameraSelector:237 / IntelligentLaserCameraRun:1225 / MoveControlData:92 含 `键 = ` 符号）；TODO 4 处（CameraSelector:224/230 疑似重复 / WeldProcess:737 / SystemComm:165）；旧版兼容 2 处（RunRecordManager:632 / SimulationController:260 可保留）
  4. **日志/文本符号残留 ~20 处**：A 类设备日志 13 处（LineLaserWorkflow:474/480 跨行 ShowLog 漏检、XMLfile:158/176/194/216、LaserWeldHeadController:332、MotionConfig:640/737、DeviceStateMachineBase:46/78 含 `->`、SimulationController:195、FaultRecoveryManager:68）；B 类故障/提示文本 8 处（SafetyInterlock:111/142/148/154/160/174/204 FailedItems 7 处 + RunRecordManager:158）；C 类图像叠加/异常消息 10 处（ImageAlgorithm×8、ImageRoiTools:130、WeldDataManager:186/228）
  5. **检测方法学发现（重要）**：单行 Log 正则检测存在跨行调用盲区；FailedItems/异常消息/图像叠加文本等非 ShowLog 通道漏检 → 应改用全量字符串冒号 grep（`"[^"]*[：:][^"]*"`）甄别
- 新增代码文件：无（本次为检测任务，产出检测报告 HTML）
- 修改代码文件：无
- 新增 Wiki 页面：无
- 更新 Wiki 页面：无（检测发现已在本日志沉淀，整改待用户确认后执行）
- 矛盾检测：无
- 遗留：~20 处符号残留与 9 处过程性注释待用户确认整改批次（P1 设备日志 13 处 / P2 故障提示 8 处 / P3 图像文本 10 处）

---

## [2026-08-21 14:41:39] refactor | 日志深度检测 + HikCameraDevice 日志通道归集
- 来源：用户需求（对日志再仔细检测一下）
- 操作：
  1. **多维度深度检测**（脚本 ×3 + 人工核实）：
     - string.Format 占位符/实参数量匹配 → 5 处疑似全部为脚本正则误报（实参含方法调用括号被截断），实际全部匹配正常
     - Console/Debug/Trace 遗漏通道 → 定位 HikCameraDevice.cs 13 处中文错误日志未走统一日志通道
     - 隐藏符号扫描（Unicode 分隔符/全角标点）→ 无违规（中文逗号/感叹号属中文内容非键值分隔）
     - 空消息日志 → 无
  2. **HikCameraDevice.cs 日志通道归集**：类内新增私有 `Log(string, MessageLevel)` 辅助方法（标签固定 HikCameraDevice），13 处 `Console.WriteLine` 中文日志归集为 Log（注册/注销回调失败、显示图像失败、图像处理异常、断线事件、关闭设备、重连成功/失败/尝试、图像回调异常、设备异常、异常回调处理失败），去冒号改纯文字，并按语义分配 Error/Warning/Info 等级
  3. **判定保留项**：HikCameraManager.cs:357 与 HikCameraDevice.cs:1198 的 `Console.WriteLine` 为 ShowLog 异常兜底（保留）；Sensor.cs 进度点 `Console.Write(".")`（SDK 采集指示非日志）、SensorHelper.cs/SensorManager.cs/SensorPointCloud.cs 的 Console（厂商 SDK 封装层调试通道，带 TraceOutput 开关）—— 属标准「不触厂商 SDK 原生部分」边界，保留
- 新增代码文件：无
- 修改代码文件：LineLaserCam/HikRobotCam/ApiCore/HikCameraDevice.cs（13 处归集 + 1 个私有 Log 方法）
- 新增 Wiki 页面：无
- 更新 Wiki 页面：无（本次为检测+小修复，标准页细则已覆盖「日志统一通道」要求）
- 矛盾检测：无
- 自检：region 配对 16/16 通过、嵌套回调类 device.Log 合法（C# 嵌套类可访问外部类私有成员）、公共签名零变更、Designer.cs 未动

---

## [2026-08-21 14:27:40] refactor | 代码精简第二轮：日志符号漏网全量清理 + SpinWait 归集
- 来源：用户需求（代码/日志/注释精简再做一次）
- 操作：
  1. **日志去符号漏网全量清理（64 处脚本替换 + 手工 20+ 处）**：`异常/失败/错误: "` → 去冒号；`InitSDK 失败, ret={0}` → `ret {0}`；`RSI 错误: [{0}] {1}` → 去冒号括号；`机器人通讯模式: RSI, 连接结果={0}` → 纯文字；`线激光识别失败（ParseRes != 1）` → `ParseRes 非 1`；`函数[{0}]:创建日志目录失败:{1}` → 纯文字；`初始化步骤 1/4: 连接设备` → 去冒号；`EKI/RSI 已连接: IP={0}, Port={1}` → 纯文字；`送丝电机位置: {0:F2} mm, 力矩限制:` → 去冒号逗号；`添加轴: {0} (编号={1})` → 纯文字；`GSDML 文件已生成:` / `自动对焦位置超限:` / `EKI 收到数据:` → 去冒号；`ROI initialized from INI: (x, y)` 等英文日志中文化
  2. **SpinWait 归集（维度④）**：LineLaserWorkflow 3 处重复「自旋等待+超时」循环（PreWork 等待 Starting / Starting 等待数据稳定 / 数据稳定后等待 Working）归集为类内私有方法 `SpinWait(Func<bool>, int, string)`，超时日志 `（30s）`→`30秒`
  3. **注释精简**：SafetyFlow.cs 删除更名过程注释（`原名 SafetyThresholds，2026-08-21 整合时更名`）；CameraRun.cs 删除废弃 Image 字段注释
- 新增代码文件：无
- 修改代码文件：Workflow(LineLaserWorkflow/MainDeviceThread/MonitorCameraWorkflow/LaserCamBoxTrackingWorkflow/FaultRecoveryManager/SafetyFlow)、Comm(CommunicationManager/S7PLC/EKI/RSI/KUKARobotManager/GSDMLGenerator)、LineLaserCam(IntelligentLaser×17/Hik×7/SmartRay CameraRun×7+SensorManager/VirtualCam)、PCLOperate(RenderConfig)、FileOperate(Log)、LaserWeldHead、MotionControl(MotionControllerBase)、DeviceStateMachine(DeviceInitializationStateMachineBase)
- 新增 Wiki 页面：无
- 更新 Wiki 页面：`standards/CodeSimplification.md`（新增④去符号执行细则）、`index/index.md`（标准页摘要更新）
- 矛盾检测：无
- 自检：region 配对通过、Dispose 未动（仅 Designer.cs 存在标准 Dispose）、静态类 Log 定义齐、SpinWait 私有方法仅本类 3 处调用、公共签名零变更
- 遗留：枚举/事件跨文件合并（JointType/SeamJointType/SeamType 三者语义明确不同，注释已声明解耦，不合并）；变量→私有成员提升待用户指定重点文件夹后执行

---

## [2026-08-21 13:58:33] refactor | 代码精简规范沉淀 + 非 UI 日志归集落地（ADR-028）
- 来源：用户需求（代码精简/注释精简/设备与通讯日志规范，并要求沉淀知识库、由 index 路由，免重复输入）
- 操作：
  1. 新建标准页 `wiki/standards/CodeSimplification.md`（唯一标准源）：四维度精简（变量→私有成员/枚举事件去重/逻辑去冗余去互锁/辅助函数归集）+ 注释三规则 + 设备/通讯日志规范
  2. 新建 `decisions/ADR-022-CodeSimplificationStandard.md`，并在 `index/index.md` 新增「代码精简规范」分类路由（免重复输入精简需求）
  3. 代码执行（非 UI，跳过 UIDesign/3rdDepend/*.bak）：全量日志调用点收敛为类内 `Log()` 私有辅助方法（241 处调用点、27 个文件），日志字符串去符号改纯文字（失败/异常/错误码/间隔/地址等）
  4. 双类/静态类文件（TCPIPComm、MotionConfig、ZMotionIO、GSDMLGenerator、RenderConfig）补/改 Log 方法，已做编译安全校验（无 Log 调用缺定义、静态类无实例方法）
- 新增代码文件：无（仅 Wiki 2 个新页面）
- 修改代码文件：MotionControl(MotionManager/ZMotion×8/MotionConfig/MotionControllerBase)、Comm(CommunicationManager/TCPIPComm/Modbus/GSDML/S7PLC/EKI/KUKARobotManager/RSI)、Workflow(MainDeviceThread/LineLaserWorkflow/LaserCamBoxTrackingWorkflow/MonitorCameraWorkflow/SimulationController/FaultRecoveryManager)、LineLaserCam×8、EmguALG、LaserWeldHead、PCLOperate、WeldParamControl、SqlLiteDatabase、DeviceStateMachine
- 新增 Wiki 页面：`standards/CodeSimplification.md`、`decisions/ADR-022-CodeSimplificationStandard.md`
- 更新 Wiki 页面：`index/index.md`（新增分类+ADR-028 行+最后更新说明）
- 矛盾检测：无
- 遗留（后续批次，需编译验证）：① 变量→私有成员提升、② 枚举/事件跨文件合并、③ 调用处冗余逻辑删除（深重构维度）；本轮聚焦④ 辅助函数归集+注释+日志（低风险行为等价变更）

---

## [2026-08-21 11:19:37] refactor | 默认初始化切正运动 + 删 Null 控制器（ADR-027）
- 来源：用户需求（初始化控制器选择需为正运动；删除不需要的控制器；加入Y轴；做CAMBOX跟踪）
- 操作：
  1. `MotionManager.Initialize()` 默认初始化正运动(ZMotion)控制器（IP 取 MotionConfigManager.Config.IpAddress，默认 192.168.0.11），不再创建空控制器
  2. 删除 `MotionControl/NullMotionController.cs` 及 csproj 注册（含 NullAxis/NullIO）；保留 SimulationController 模拟子系统
  3. `InitializeWithZMotion(ip)` 失败分支改为清空并记告警，不再回退 Null
  4. CAMBOX 跟踪随正运动句柄自动初始化（Y轴=从轴axis0，主轴=虚拟编码器轴axis8 由 KUKA PDO 驱动）
- 关联：`decisions/ADR-031-DefaultInitZMotion`、[[modules/MotionControl]]、[[modules/DeviceControl]]

## [2026-08-21 10:12:27] refactor | Safety 模块整合进 Workflow（ADR-026）
- 来源：用户需求（safety 文件夹整合）
- 操作：
  1. 合并 `FaultRecord` + `SafetyInterlockResult` + `SafetyInterlockChecker` 为 `Workflow/SafetyInterlock.cs`（命名空间 AdaWeldSystem.Workflow）
  2. `SafetyThresholds` 更名 `SafetyFlow` → `Workflow/SafetyFlow.cs`
  3. `FaultRecoveryManager` 作为对外配置管理器 → `Workflow/FaultRecoveryManager.cs`
  4. 删除原 `AdaWeldSystem/Safety/` 文件夹 5 文件，三文件直接落 `Workflow/`（不建独立文件夹）
  5. `AdaWeldSystem.csproj`：5 个 `Safety\*.cs` 替换为 3 个 `Workflow\*.cs`
  6. `Workflow/MainDeviceThread.cs` 移除 `using AdaWeldSystem.Safety;`（同命名空间直接可见）
- 新增代码文件：Workflow/SafetyInterlock.cs、Workflow/SafetyFlow.cs
- 修改代码文件：Workflow/FaultRecoveryManager.cs（迁移）、Workflow/MainDeviceThread.cs（去 using）、AdaWeldSystem.csproj
- 删除：AdaWeldSystem/Safety/（5 文件）
- 新增 Wiki：decisions/ADR-030-SafetyModuleConsolidation.md
- 更新 Wiki：modules/Workflow.md（新增安全 flow 小节 + 核心文件）、modules/Safety.md（标注整合）、wiki/index/index.md（模块行 + ADR 行）
- 矛盾检测：无（ADR-026 记录整合，与 ADR-023 阶段B/C 内容一致，仅代码位置/命名空间变更）

## [2026-08-20 16:17:13] refactor | 回调GC根治 + CommPeriod初始化专属 + 线激光工作流分步重构

**修复1：CallbackOnCollectedDelegate 根治**
- 回调委托改为「只注册一次、全程存活不释放」，与英莱 demo 做法一致
- 新增 `_sdkInitialized` 标志：首次连接才 InitSDK + RegisterCallbacks，重连仅 ConnectToSensor
- `DisconnectManual` 不再 UnInitSDK / FreeCallbackHandles / Free hostHandle，仅关外设+断连
- 仅 Dispose 时做完整释放（ReleaseNativeResources）
- 从根本上避免频繁开关相机导致的委托 GC 回收问题

**修复2：SetSensorCommPeriod 初始化专属配置**
- 新增 `ConfigureDefaultCommPeriod()` 公共方法 + `_commPeriodConfigured` 标志
- 仅在初始化连接成功后调用一次（LineLaserWorkflow.InitializeWorker 中）
- 手动连接/重连不重复配置，保持 SDK 当前值
- 配置参数：DwSendCycle=10ms, DwBufferDuration=1000ms（英莱技术支持建议）

**修复3：线激光工作流分步重构（switch-case + step）**
- 状态枚举从 7 态扩展为 9 态：新增 PreWork / Working / Stopping
- 工作循环从单 while 循环改为 switch-case + step 分步结构
- 状态流转：Standby → PreWork → Starting → Working → Stopping → Standby
- 由主设备分步驱动：PreWork 完成 → BeginStarting → 数据稳定 → BeginWorking
- 待机状态传感器/激光均关闭（安全默认态），Starting 阶段才开启
- 新增公共方法：BeginStarting() / BeginWorking() / IsPreWorkDone / IsDataStable
- Starting 阶段连续有效帧达标（默认 5 帧）后置数据稳定标志
- MainDeviceThread 线激光启动改为三步协同（PreWork等待 → Starting → Working等待）
- UI 层状态显示同步更新（ILCamPage / FormMain / LLCamWorkJob / MotionControlPage）
- 新增 `decisions/ADR-021-LineLaserWorkflowRefactor` 记录线激光工作流重构决策

- **回调重构**：`MillionOutlineCallback` 重构为「第一步拿数据 → 第二步模式分支」的两步结构
  - 第一步（所有模式共用）：原生数据读取、轮廓点计数、实测 FPS 计算、传感器 FPS 刷新（500ms 节流）、PointCloudData 构建、InspectResult 捕获
  - 第二步（模式分支）：手动模式生成 Mat + 换帧 + 触发 ContourFrameReady UI 事件；自动/其他模式仅外传 ContourDataReady 事件，不生成 Mat、不触发 UI
- **新增 `IsManualMode` 属性**：默认 true，控制回调模式切换；`ILCamPage.UpdateModeUi` 中根据工作流状态自动设置
- **减少临时变量**：移除 `var contour` 中间引用，`newMat` 仅在手动模式分支内分配，降低 GC 压力
- **传感器帧率标签修复**：`ILCamPage.RefreshDisplay` 中轮廓点 + 传感器帧率 + 回调帧率三个状态标签的更新移到模式判断之前，自动模式下也能实时显示帧率
- **SetSensorCommPeriod 默认配置**：`ConnectCore` 连接成功后调用 `SetSensorCommPeriod`（英莱技术支持建议）
  - `DwSendCycle = 10ms`（发送周期）
  - `DwBufferDuration = 1000ms`（缓冲时长）
  - 失败仅记 warning 日志，不影响连接结果
- **影响文件**：
  - `IntelligentLaserCameraRun.cs`：回调重构 + IsManualMode 属性 + SetSensorCommPeriod 配置
  - `ILCamPage.cs`：IsManualMode 设置 + RefreshDisplay 帧率标签前置
- **Wiki 更新**：modules/IntelligentLaserCam.md、api/IntelligentLaserCam.md、lessons/IntelligentLaser-Pitfalls.md（新增 §3.7 回调周期、§5.8 回调模式分流）

## [2026-08-20 13:45:49] fix | 英莱 SDK dwInstanceId 参数统一修复（0u→1u），解决帧率读取失败问题

- **来源**：用户反馈 3 项：① `FetchSensorFpsModel` 失败 ret=16777216，日志 4 次；② 采集帧率没有值显示；③ 实测回调帧率接近 30，怀疑有限制
- **根因**：英莱 SDK 所有函数的 `dwInstanceId` 参数默认值为 **1**（第一个传感器实例），但代码中 5 处显式传了 `0u`，导致 SDK 返回 `INTELLIGENT_E_UNINIT (0x1000000 = 16777216)` 错误码（实例 0 未初始化）
- **修复范围**：`IntelligentLaserCameraRun.cs` 中 5 处 SDK 调用全部改为 `1u`：
  - `DetectHardwareStatus` 内 `FetchSensorInfo(info, 0u)` → `1u`
  - `IsSensorRunning` 内 `FetchSensorFps(ref fps, 0u)` → `1u`
  - `FetchFpsModel` 内 `FetchSensorFpsModel(ref model, 0u)` → `1u`
  - `DetectHardwareStatus` 内 `FetchSensorFps(ref fps, 0u)` → `1u`
  - `MillionOutlineCallback` 内 `FetchSensorFps(ref hwFps, 0u)` → `1u`
- **修复后预期**：① 帧率下拉能正确显示当前档位；② 传感器帧率实时显示硬件输出值；③ `IsSensorRunning` 能正确判断传感器状态
- **关于回调帧率 ~30fps**：需待 dwInstanceId 修复后，通过正确读取的 `ScanRateHz` 判断传感器实际运行帧率，再进一步排查（若传感器帧率也 ~30 则是档位未切换成功，若传感器帧率远高于 30 则是回调/网络/处理瓶颈）
- **修改代码文件**：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`（新增 dwInstanceId 修复记录）、`api/IntelligentLaserCam.md`（ScanRateHz 补充 dwInstanceId 注意事项）、`lessons/IntelligentLaser-Pitfalls.md`（新增 §5.7 dwInstanceId 参数陷阱）
- **矛盾检测**：无

---

## [2026-08-20 13:29:47] fix | 英莱传感器帧率运行时实时刷新 + FetchFpsModel 失败日志

- **来源**：用户反馈 2 项：① 传感器帧率（lblSenorfps）不刷新，应运行时实时获取；② 已设最高帧率但下拉仍显示标准模式
- **修复 1（传感器帧率实时刷新）**：`MillionOutlineCallback` 中新增节流式 `FetchSensorFps` 调用，每 500ms 读取一次硬件实际帧率并更新 `_scanRateHz`，使 `ScanRateHz` 属性反映运行时实时值；新增字段 `_lastSensorFpsUpdateTime` + 常量 `SensorFpsUpdateIntervalMs = 500`；UI 层 `ILCamPage.RefreshDisplay` 已读取 `ScanRateHz`，无需修改
- **修复 2（FetchFpsModel 日志）**：`FetchFpsModel()` 从静默失败（`catch { }`）改为输出 warning 日志，记录 SDK 返回码和异常信息，方便排查「帧率下拉显示不对」的根因
- **修改代码文件**：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`、`api/IntelligentLaserCam.md`（ScanRateHz 说明更新）、`lessons/IntelligentLaser-Pitfalls.md`（§5.6 补充运行时刷新策略）
- **矛盾检测**：无

---

## [2026-08-20 13:10:10] ui | 英莱相机页面 UI 细化调整（双帧率显示 + swDisplay 语义 + 列宽缩短 + 按钮文字统一）

- **来源**：用户 5 项 UI 调整需求
- **调整 1（双帧率显示）**：新增 `lblSenorfps`（传感器帧率，`ScanRateHz`）放在结果面板中间列；右侧 `lblMeasuredFps` 文本改为"回调帧率"；左列保持"轮廓点"。Designer 中 `label1` 重命名为 `lblSenorfps`
- **调整 2（swDisplay 语义）**：从「自动模式自动显示开关」改为「手动模式是否绘制 Mat 的开关」——手动模式勾选显示画面、取消只看结果表；自动模式下禁用；标签文字"自动显示"→"显示画面"
- **调整 3（结果表列宽）**：`dgvResult` 列宽从 200/300/120 缩短为 120/160/70（字段/值/单位）
- **调整 4（按钮文字）**：`btnCaptureCamera` 文字"开启相机/关闭相机"→"开启传感器/关闭传感器"；断开连接重置文字、帧率切换保护提示同步更新
- **修改代码文件**：`UIDesign/TabPage/ILCamPage.cs`、`UIDesign/TabPage/ILCamPage.Designer.cs`
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`、`lessons/IntelligentLaser-Pitfalls.md`（新增 §5.6）
- **矛盾检测**：无

---

## [2026-08-20 11:41:58] fix | 英莱相机按钮语义修正 + 连接后帧率同步 + 手动自动数据流分离

- **来源**：用户反馈 3 项问题：① 连接后帧率显示不对（已设最高档仍显示标准值）；② 开启激光相机也开了、关闭相机仍有回调；③ 手动模式才应回调绘制 Mat 和结果表，其余模式数据外传
- **修复 1（帧率显示）**：`DetectHardwareStatus()` 读取硬件 FPS 后同步更新 `_scanRateHz`，解决 `ScanRateHz` 连接后仍为默认 60Hz 的问题
- **修复 2（按钮语义）**：「开启相机」按钮从 `SetCaptureCamera` 改为 `SetSensor`（传感器使能=回调源头），开启时顺带确保采集相机上电；移除连接后自动 `SetSensor(true)`，由用户手动控制；帧率切换保护改用 `IsSensorRunning()`；变量 `_isCaptureCameraOn` → `_isCameraOn`
- **修复 3（数据流分离）**：`ILCamPage.RefreshDisplay()` 仅手动/空闲模式下绘制 Mat+结果表；自动模式直接返回，数据通过 `ContourDataReady` 外传（ScottPlot + 自动调整）；移除 `swDisplay` Switch 及相关逻辑
- **修改代码文件**：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`、`UIDesign/TabPage/ILCamPage.cs`
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`、`api/IntelligentLaserCam.md`、`lessons/IntelligentLaser-Pitfalls.md`（新增 §3.5 §3.6 §5.5）、`wiki/index/index.md`
- **矛盾检测**：无

---

## [2026-08-20 11:12:38] fix | 线激光初始化状态校验简化 + 安全默认态（关激光关相机）

- **来源**：用户反馈第 4 步「状态信号校验」失败，但线激光实际已连接正常
- **根因**：`verifyHardwareStatus` 检查项过多（连接 + 传感器运行 + 校准数据等3秒），校准数据通过异步回调到达且时机不确定，导致初始化阻塞在校准数据等待上最终失败
- **修复**：① **校验简化**：第 4 步 `verifyHardwareStatus` 仅校验 `IsConnected`——连接上就是正常的。校准数据、激光/相机开关属运行时状态，不阻塞初始化。② **安全默认态**：校验通过后立即关激光（`SetLaser(false)`）、关相机（`SetCaptureCamera(false)`），确保硬件进入安全待机态；传感器保持运行（接收轮廓回调，画面才能正常显示）。
- **修改代码文件**：`Workflow/LineLaserWorkflow.cs`（`InitializeWorker` 的英莱分支 `verifyHardwareStatus` 重写）
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`（同步初始化条目扩展为 6 项，新增「初始化校验简化」和「安全默认态」）
- **矛盾检测**：无

---

## [2026-08-20 11:05:08] fix | 线激光初始化失败根因：状态机重复转换（Initializing→Initializing）

- **来源**：用户反馈线激光初始化失败，日志显示 `非法状态转换: Initializing -> Initializing`
- **根因**：`LineLaserWorkflow.Initialize()` / `InitializeSync()` 中手动调用了 `_deviceStateMachine.TryTransition(DeviceState.Initializing, "线激光相机初始化开始")`，而 `_deviceStateMachine.Initialize()` 模板方法内部第一步也会调用 `TryTransition(Initializing)`，造成两次转换同一状态 → 第二次命中"非法状态转换"守卫 → `Initialize()` 直接返回 false → 初始化失败。
- **修复**：移除工作流层的重复 `TryTransition(Initializing)` 调用。设备状态机的 `Initializing → 四步初始化 → Standby/Alarm` 完整流程统一由 `DeviceInitializationStateMachineBase.Initialize()` 模板方法负责，工作流层只管自己的工作流状态（`LineLaserWorkflowState`）。
- **教训沉淀**：新增 [[lessons/StateMachine-DoubleTransition]]，记录"工作流层不要越俎代庖操作设备状态机初始化转换"的架构分层原则。
- **修改代码文件**：`Workflow/LineLaserWorkflow.cs`（删除 2 行重复转换）
- **新增 Wiki 页面**：`lessons/StateMachine-DoubleTransition.md`
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`（新增第 ⑤ 条重复状态转换修复）、`wiki/index/index.md`（新增教训页索引）
- **矛盾检测**：无

---

## [2026-08-20 10:59:19] fix | 同步初始化 + 日志净化 + 校准数据时序修复 + 去重复初始化（4 项）

- **来源**：用户反馈 3 个问题：① 日志不要用 `-`/`=` 符号分割 ② 初始化执行了两遍（上电失败后又开始）③ 线激光初始化完 UI 仍显示未连接
- **问题 1 — 日志符号分割**：去除所有 `----` / `====` / `---` 符号分割线，改用纯文本描述（`子设备初始化开始` / `[N/5] 设备名初始化开始/完成/失败` / `初始化全部完成（整设备待机）`），日志风格统一简洁。
- **问题 2 — 重复初始化**：`Start()` 中 `IsPowerOnInitialized` 为 false 时自动重跑 `PowerOnInitialize()`，在线激光异步初始化场景下导致二次执行（用户看到"上电失败，执行Power..."后又初始化）。修复：`Start()` 未初始化时仅记录警告并返回（不再自动重跑），初始化统一由 FormMain 显式调用 `PowerOnInitialize()` 一次完成。
- **问题 3 — 线激光初始化失败 UI 显示未连接（根因：校准数据时序）**：`readConfiguration` 步骤检查 `CalibrationInfo != null`，但校准数据通过 `InternalRefCornerPts` 异步回调到达，且传感器在第 3 步 `resetDevice` 才启动 → 第 2 步检查时必然为 null → 初始化失败 → 状态机 Alarm → UI 显示未连接。修复：`readConfiguration` 改为直接通过（英莱相机配置由 SDK 连接时自动加载），校准数据等待移到第 4 步 `verifyHardwareStatus` 中（传感器启动后等待 3s，每 100ms 轮询校准回调数据），确保初始化能正确进入 Standby。
- **问题 4 — 异步初始化改同步**：5 个子设备改为同步顺序执行（焊接头→运动控制→线激光→监控相机→机器人），一个完成才开始下一个。线激光工作流新增 `InitializeSync()` 同步方法；移除 `WaitForAllReady` 异步等待线程和 `_awaitingReady` 标志；`EvaluateInitializationResult` 直接判定最终结果。同时"阶段二"改名为"子设备初始化"。
- **UI 同步完善**：移除 `ILCamPage` 构造函数中强制跳转状态机的逻辑（`Uninitialized→Initializing→Standby` 两跳会干扰正式初始化流程）。改为：初始化过程中由 `OnIlStateChanged` 监听 `Initializing→Standby` 转换并调 `SyncFromHardwareAfterConnect()`；若页面在初始化完成后才打开（状态已 Standby），构造函数直接调 `SyncFromHardwareAfterConnect()` 做一次性同步。
- **修改代码文件**：`DeviceStateMachine/API/DeviceInitializationStateMachineBase.cs`、`Workflow/MainDeviceThread.cs`、`Workflow/LineLaserWorkflow.cs`、`UIDesign/TabPage/ILCamPage.cs`、`UIDesign/MainWindow/FormMain.cs`（注释）
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`modules/DeviceStateMachine.md`（新增同步初始化+日志净化+去重复初始化+校准数据时序条目）、`modules/IntelligentLaserCam.md`（新增同步初始化+校准数据时机修复+日志净化+UI 同步完善条目）、`api/DeviceStateMachine.md`（同步初始化 + 步骤日志净化 + 状态汇总日志更新）
- **矛盾检测**：无

---

## [2026-08-20 10:34:50] fix | 初始化日志结构化 + 自动初始化 UI 状态同步（2 项）

- **来源**：用户反馈 2 个问题：① 初始化日志东一块西一块，不按顺序 ② 线激光相机初始化完成后状态未同步到 UI
- **问题 1 — 初始化日志散乱**：`DeviceInitializationStateMachineBase.RunStep()` 成功时不打日志，仅失败/异常才记；且线激光异步初始化导致日志与其他设备交错。修复：① 模板基类 `Initialize()` 四步增加步骤级日志（`---- 初始化步骤 N/4: 步骤名 ----` 开始 + `[步骤名] 成功/失败/异常/跳过` 结果 + `==== 初始化全部完成 ====` 收尾）；② `MainDeviceThread.PowerOnInitialize()` 改为 5 步结构化序号日志（`--- [1/5] 焊接头` → `[2/5] 运动控制` → `[3/5] 线激光` → `[4/5] 监控相机` → `[5/5] 机器人通讯 ---`），每步有开始/完成/失败/跳过标记；③ 新增 `GetDeviceStatusSummary()` 输出各子设备状态汇总，`EvaluateInitializationResult` / `WaitForAllReady` 输出状态明细与等待耗时。
- **问题 2 — 自动初始化 UI 不同步**：线激光状态机转 `Standby`（初始化完成）时，`OnIlStateChanged` 仅调 `UpdateConnectionUi()`（只更连接态标签+按钮使能），未同步硬件实际状态（激光/相机开关、Job 列表、帧率选择、传感器使能）。修复：`OnIlStateChanged` 中当 `OldState==Initializing && NewState==Standby` 时调用 `SyncFromHardwareAfterConnect()`，完整同步 UI 到硬件实际状态。
- **修改代码文件**：`DeviceStateMachine/API/DeviceInitializationStateMachineBase.cs`、`Workflow/MainDeviceThread.cs`、`UIDesign/TabPage/ILCamPage.cs`
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`modules/DeviceStateMachine.md`（新增 2026-08-20 日志增强条目）、`modules/IntelligentLaserCam.md`（新增自动初始化 UI 同步 + 日志增强条目）、`api/DeviceStateMachine.md`（新增步骤级日志 + 状态汇总日志条目）
- **矛盾检测**：无

---

## [2026-08-20 10:15:19] fix | 英莱相机 UI 同步 + 应用按钮 + 回调释放竞态修复（3 项）

- **来源**：用户反馈 3 个问题：① 初始化连接后 UI 仍显示未连接 ② Job/帧率缺确认按钮 ③ 帧率切换后断开重连复现 CallbackOnCollectedDelegate
- **问题 1 — 初始化 UI 不同步**：`DetectConnection` 早于页面创建时已连接相机，页面构造函数仅同步状态机未同步硬件状态/Job/帧率。修复：提取 `SyncFromHardwareAfterConnect()`（硬件状态检测→按钮文本 + 开传感器 + 刷新 Job/帧率 + 更新按钮态），供 `btnConnect_Click` 成功分支与构造函数初始化同步两处复用。
- **问题 2 — Job/帧率应用按钮**：`cmbJob` / `cmbFps` 下拉选择不再直接切换，改为仅更新应用按钮可用态（选中项与当前一致则禁用）；新增 `btnApplyJob` / `btnApplyFps` 确认按钮，点击才执行实际切换；断开连接时清除 Job 下拉项 + 帧率选中项，禁用应用按钮；自动模式下同步禁用应用按钮。新增 `UpdateApplyButtonsState()` 统一管理应用按钮可用态。
- **问题 3 — 回调释放竞态（第四层防御）**：新增 `_activeCallbacks` 引用计数器（`Interlocked.Increment/Decrement` + `try/finally`），三个回调均参与计数；新增 `WaitForCallbacksToFinish()` 自旋等待归零（超时 2s，超时记警告仍继续释放避免死锁）；`DisconnectManual` / `ReleaseNativeResources` 在关传感器+反初始化 SDK 后、释放委托 GCHandle 前等待回调归零 + `Thread.Sleep(50)`。根治「关传感器→释放委托」之间在途回调触发 CallbackOnCollectedDelegate 的竞态窗口（高帧率下更易复现）。
- **修改代码文件**：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`、`UIDesign/TabPage/ILCamPage.cs`、`UIDesign/TabPage/ILCamPage.Designer.cs`
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`（新增 UI 同步+应用按钮+回调竞态修复条目）、`api/IntelligentLaserCam.md`（新增第四层防御条目）、`lessons/IntelligentLaser-Pitfalls.md`（第 6 章新增 6.6 释放竞态小节）
- **矛盾检测**：无

---

## [2026-08-20 09:40:10] fix | 修复英莱相机 CallbackOnCollectedDelegate MDA 错误

- **来源**：用户反馈托管调试助手 `CallbackOnCollectedDelegate` 报错——对 `IntelligentMillionOutlineInspectCallBack::Invoke` 类型的已垃圾回收委托进行了回调
- **根因**：
  1. 三个 SDK 回调委托仅通过 `_hostHandle` 钉住 `this` 间接保活，无独立 GCHandle 钉住委托本身——非托管侧函数指针不被 GC 视为根引用，委托可能被回收
  2. `ConnectCore` 失败路径与 `DisconnectManual` 未释放 `_hostHandle`，GCHandle 泄漏
- **修复（三层防御）**：
  1. **核心修复**：每个委托新增独立 `GCHandle`（`_hCbMillionOutline` / `_hCbInitJobParams` / `_hCbCalibration`），注册时 `GCHandle.Alloc(delegate)` 直接钉住委托
  2. **JIT 防御**：`MillionOutlineCallback` / `CalibrationCallback` / `InitJobParamsCallback` 三个回调方法末尾加 `GC.KeepAlive(this)`
  3. **释放全覆盖**：`ConnectCore` 失败路径补 `FreeCallbackHandles()` + `_hostHandle.Free()`；`DisconnectManual` 同步补全；新增 `FreeCallbackHandles()` 私有方法统一释放三个委托句柄
- **修改代码文件**：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`（新增 CallbackOnCollectedDelegate 修复条目）、`lessons/IntelligentLaser-Pitfalls.md`（新增第 6 章「委托 GC 保护与 CallbackOnCollectedDelegate」）
- **矛盾检测**：无

---

## [2026-08-19 17:19:41] code_review_fix | V3 状态机/故障恢复/UI 状态标签 6 项问题全部修复

- **来源**：代码审查（用户要求检测 V3 整机/子设备状态机、流程、状态标签刷新的代码实现错误）
- **P0 严重 — FaultRecoveryManager 设备名不匹配**：`SubscribeFault` 用 `src.StateName`（中文名）记录 Device，`RegisterRecoveryStrategy` 用英文 key 注册，`ResolveKey` 的 `IndexOf` 子串匹配永远失败，自动恢复策略永不触发。修复：`RecordFault` 新增 `deviceKey` 参数，`SubscribeFault` 传入英文 `deviceKey`，精确匹配优先，回退到 Device 名解析。
- **P1 高 — 整机状态机未接入 UI 状态栏**：V3 核心的整设备聚合状态未在 FormMain 显示。修复：`FormMain` 动态添加 `lbl_SystemStatus` 标签，订阅 `MainDeviceThread.Instance.MainStateMachine.StateChanged`，按状态显示不同文本与颜色（灰/橙/绿/红），`FormClosed` 中退订。
- **P2 中 — 故障恢复同步阻塞**：`TryRecover()` 内含 `Thread.Sleep(5000)` × 最多 3 次，同步调用阻塞 `TryTransition(Alarm)` 执行链。修复：自动恢复改用 `ThreadPool.QueueUserWorkItem` 异步执行。
- **P3 低 — Offline 枚举注释矛盾**：`DeviceState.Offline` 注释写「机器人连接专用」，但 V3 中线激光等设备也复用 Offline。修复：更新枚举注释，明确 Offline 语义扩展为「设备离线/断开」。
- **P3 低 — MotionControlStateMachine 冗余 Uninitialized→Alarm 转换**：唯独 MotionControl 声明了此转换，其他 3 个子设备均无，且无实际调用路径。修复：移除此冗余转换。
- **P3 低 — MainDeviceStateMachine 死转换 Standby→InitializationFailed**：ValidTransitions 声明了此转换，但 Standby 下故障实际走 Alarm，无代码路径。修复：移除此死转换。
- **文档位置验证**：V3 架构文档位于 `wiki/architecture/V3-Architecture.md`，位置正确，索引/ADR/模块文档双向链接完整。
- **修改代码文件**：`Safety/FaultRecoveryManager.cs`、`Workflow/MainDeviceThread.cs`、`UIDesign/MainWindow/FormMain.cs`、`DeviceStateMachine/API/IDeviceStateMachine.cs`、`DeviceStateMachine/MotionControlStateMachine.cs`、`DeviceStateMachine/MainDeviceStateMachine.cs`
- **更新 Wiki 页面**：`architecture/V3-Architecture.md`（新增修订记录章节）、`modules/Safety.md`（更新故障恢复 API 说明）、`wiki/index/index.md`（新增 Lesson 索引条目+近期变更）
- **新增 Wiki 页面**：`lessons/FaultRecoveryDeviceKey.md`（故障恢复设备键名匹配陷阱）
- **编译验证**：MSBuild Rebuild 通过，0 错误
- **矛盾检测**：无（所有修改均为 bug 修复，不改变架构设计；新增 `RecordFault` 重载保持向后兼容）

---

## [2026-08-19 14:50:45] coding | FormMain 关闭询问：未运行→确认关闭；运行中→告警强制关闭

- **来源**：用户需求（程序关闭询问：整机未进入运行状态只询问确认关闭；整机运行中告警设备正在运行，确认强制关闭）
- **操作**：
  1. `UIDesign/MainWindow/FormMain.cs` 构造函数运行时分支新增 `this.FormClosing += FormMain_FormClosing;`（代码后置订阅，不改 Designer.cs）
  2. 新增 `FormMain_FormClosing`：判定 `MainDeviceThread.Instance.IsWelding`（整机运行单一真相源，Go/Done 指令驱动）——未运行弹「确认关闭」`TType.Info`；运行中弹「设备运行中」`TType.Error` 告警强制关闭；用户取消 → `e.Cancel = true`
  3. 弹窗范式 `AntdUI.Modal.open(new Modal.Config(this, title, message, type)) == DialogResult.OK`（owner 用 this，FormMain 为 AntdUI.Window；与 ConfigForm/FormLogin 既有确认范式一致）
- **修改代码文件**：`UIDesign/MainWindow/FormMain.cs`
- **更新 Wiki 页面**：`modules/UIDesign`（新增「关闭询问」章节）
- **矛盾检测**：无（复用既有 IsWelding 运行标志，未引入新状态；FormClosed 释放链不变）

---

## [2026-08-19 14:17:12] coding | UI 类 DisposeComponents() 按需使用落地（还原 Designer.cs / 移除 finalizer / 补齐释放链）

- **来源**：用户澄清（`DisposeComponents()` 仅当 UI 设计器类持有「外部嵌套控件/资源」时才需要；无嵌套/无独立资源则不需要；禁止改 Designer.cs 的 Dispose(bool)；finalizer 退订事件无效）
- **决策**：`decisions/ADR-020-DisposePatternFullCoverage` 补充「UI 类按需使用判定规则」；[[decisions/ADR-001-DisposePattern]] 补充 UI 按需语义
- **操作**：
  1. `HelixRenderForm`：还原被手动修改的 `Designer.cs`（移除 `_viewer?.Dispose()`/`elementHost1.Dispose()`/`CurrentData?.Clear()` 注入），新增 `DisposeComponents()`（释放外部 `_viewer` PointCloudViewer）+ `HandleDestroyed` 触发
  2. `MainPage`：移除无效 `~MainPage()` finalizer（事件源持引用时永不执行），新增 `DisposeComponents()`（退订 `GlobalCommData.EventInfoHandler` + `_contourCamera.ContourDataReady`）+ `HandleDestroyed` 触发
  3. `CommPage`：新增 `HandleDestroyed` → `DisposeComponents()`（修复原无调用者的释放泄漏）
  4. `MonitorCamPage`：`HandleDestroyed` 改调完整 `DisposeComponents()`（含 SensorStop/Stop）
  5. `MotionControlPage`：新增 `HandleDestroyed` → 退订 `LineLaserWorkflow.StateChanged`（修复页面销毁泄漏）
  6. `FormMain`：`FormClosed` 补退订 `LineLaserWorkflow.StateChanged`
- **保留现状**：`ILCamPage`/`LLCamWorkJob`/`LLCameraSetting` 用 HandleDestroyed 直接释放（等效正确位置，最小变更）；`ILAlgoPage`/`AlgorithmEditForm`/`ILParamPage` 等仅外部注入引用无需释放
- **修改代码文件**：`UIDesign/SubView/HelixRenderForm.cs`、`UIDesign/SubView/HelixRenderForm.Designer.cs`、`UIDesign/ControlPage/MainPage.cs`、`UIDesign/TabPage/CommPage.cs`、`UIDesign/TabPage/MonitorCamPage.cs`、`UIDesign/TabPage/MotionControlPage.cs`、`UIDesign/MainWindow/FormMain.cs`
- **更新 Wiki 页面**：`decisions/ADR-020-DisposePatternFullCoverage`、`decisions/ADR-001-DisposePattern`、`lessons/WinForms-Designer-Guide`、`modules/UIDesign`、`index`
- **矛盾检测**：无（与上一轮 ADR-024 非 UI 类迁移互补，UI 类按需使用规则明确）

---

## [2026-08-19 14:03:21] coding | Dispose 模式全覆盖：非 UI 类统一标准 IDisposable.Dispose()，DisposeComponents() 仅限 UI 设计器类

- **来源**：用户反馈（ADR-001 的 DisposeComponents() 被误用于非 UI 类，导致按 IDisposable 释放时资源不释放）
- **决策**：新增 `decisions/ADR-020-DisposePatternFullCoverage`；修订 [[decisions/ADR-001-DisposePattern]]（澄清适用 UI 设计器类）
- **操作**：
  1. **非 UI 类 `DisposeComponents()` → 标准 `IDisposable.Dispose()` 迁移**：`Workflow/MainDeviceThread`（+级联释放通讯管理器）、`Workflow/LineLaserWorkflow`（+释放 `_ilCamera`）、`Workflow/MonitorCameraWorkflow`（+释放 Mat）、`Workflow/LaserCamBoxTrackingWorkflow`（子组件改 `.Dispose()`）；`MotionControl/ZMotion/CamBoxTracker`、`EncoderAxis`、`RSIPositionBuffer`（合并为单一 Dispose）；`MotionControl/ZMotion/ZMotionController`（新增 Dispose：停心跳/周期/上报线程 + 释放 GCHandle + Close）
  2. **补释放入口**：`Comm/CommunicationManager`（新增 IDisposable + Dispose 释放 TcpIpComm/RobotManager/PlcManager/ModbusManager）；`Comm/CommBase/Ethernet/TcpIpComm`、`SstTcpServer`、`SstTcpClient`（新增 IDisposable + Dispose）
  3. **调用链同步**：`UIDesign/MainWindow/FormMain.cs` `MainDeviceThread.Instance.DisposeComponents()` → `.Dispose()`（唯一调用点，被调方接口变更必要联动）
  4. **保留**：UI 类 `CommPage`/`MonitorCamPage` 的 `DisposeComponents()`（合规）
  5. 释放完整性抽查：Modbus/S7/KUKA(RobotManager/RSI/EKI)/LaserWeldHead/SQLite/SensorManager/HikCameraDevice 均已有完整标准 Dispose，未改动
- **修改代码文件**：`Comm/CommunicationManager.cs`、`Comm/CommBase/Ethernet/TCPIPComm.cs`、`Workflow/MainDeviceThread.cs`、`Workflow/LineLaserWorkflow.cs`、`Workflow/MonitorCameraWorkflow.cs`、`Workflow/LaserCamBoxTrackingWorkflow.cs`、`MotionControl/ZMotion/ZMotionController.cs`、`MotionControl/ZMotion/CamBoxTracker.cs`、`MotionControl/ZMotion/EncoderAxis.cs`、`MotionControl/ZMotion/RSIPositionBuffer.cs`、`UIDesign/MainWindow/FormMain.cs`
- **新增 Wiki 页面**：`decisions/ADR-020-DisposePatternFullCoverage.md`
- **更新 Wiki 页面**：`decisions/ADR-001-DisposePattern`、`modules/Comm`、`modules/Workflow`、`modules/MotionControl`、`lessons/WinForms-Designer-Guide`、`index`
- **备份**：`AdaWeldSystem_backup_20260819_134841.tar.gz`
- **矛盾检测**：无（ADR-001 语义澄清 + ADR-024 全覆盖，与既有代码现状一致）

---

## [2026-08-19 13:18:35] fix | IDeviceStateMachine 接口补充 FaultOccurred 事件声明（修复 CS1061 编译错误）

- **来源**：Bug 修复（用户反馈编译错误）
- **操作**：
  1. Phase 0 定位根因：`FaultOccurred` 事件（V3 阶段C 故障恢复入口）仅声明于 `DeviceStateMachineBase` 基类，接口 `IDeviceStateMachine` 漏声明；`MainDeviceThread.SubscribeFault(IDeviceStateMachine sm)` 中 `sm.FaultOccurred += ...` 编译报 CS1061。
  2. Phase 2 修复：`DeviceStateMachine/API/IDeviceStateMachine.cs` 接口补充 `event EventHandler<DeviceStateChangedEventArgs> FaultOccurred;`（与基类签名一致，零破坏）。
  3. 影响半径验证：唯一直接实现者为 `DeviceStateMachineBase`，5 个派生状态机 + `MainDeviceStateMachine` 均经继承链自动满足接口。
- **修改代码文件**：`DeviceStateMachine/API/IDeviceStateMachine.cs`（+1 事件声明）
- **更新 Wiki 页面**：`modules/DeviceStateMachine`、`api/DeviceStateMachine`、`lessons/CSharp-Language-Pitfalls`（新增 §3.3 接口与基类成员不同步 → CS1061）、`index`
- **矛盾检测**：无（ADR-023 阶段C 事件入口契约补全，与既有文档一致）

---

## [2026-08-19 11:47:41] revert | 废弃 code-review-graph 代码图谱工具链（ADR-020 deprecated），回归 Grep 默认方式

- **来源**：用户反馈（code review 不好用——执行失败频繁、耗时久、经常误判）
- **决策**：`decisions/ADR-023-CodeGraphForCodeReview` 状态改为 `deprecated`。工作流中 Phase 0（Step 0.7/0.8）、Phase 2（Step 2.5）、Phase 4（代码漂移）的图谱强制集成全部移除，回归图谱引入前的默认方式：**Grep 定位符号 + 按行号精确读取（Read offset/limit）+ 人工多级调用追溯**。
- **操作**：
  1. `~/.workbuddy/skills/vibecoding-llmwiki/SKILL.md` 与 `LLMWiki/skills/vibecoding-llmwiki/SKILL.md`（两副本同步）：移除 Code Graph mandatory 规则，Step 0.7/0.8 改 Grep 符号定位与 Grep 引导读取，Step 2.5 改 Grep 多级追溯，Phase 4 漂移检测改 Grep 抽查，Prohibited Behaviors 第 10 条改为禁止重新引入图谱工具。
  2. `wiki/project/vibecoding-workflow.md`：Step 0.7/0.8/2.5 与 Phase 4 同步改为 Grep 默认方式，移除 Python/conda/crg_build 执行须知。
  3. `wiki/decisions/ADR-023-CodeGraphForCodeReview.md`：status accepted → deprecated，新增废弃声明。
  4. `wiki/lessons/Project-Tools-Guide.md`：§1 代码图谱整节加废弃横幅（历史参考）。
  5. `wiki/lessons/CSharp-Language-Pitfalls.md`：枚举重复定义教训中"code-review-graph 死代码误判"更新为含废弃注记。
  6. `wiki/index/index.md`：ADR-020 与两条 lessons 摘要更新为已废弃。
- **保留**：`raw/skills/AdaWeldsys_Skills/05-Tools/CodeGraph.md`（调研文档）、`raw/tools/crg_build.py`（包装脚本）作为历史参考，不再使用。
- **修改 Wiki 页面**：`decisions/ADR-023-CodeGraphForCodeReview`、`project/vibecoding-workflow`、`lessons/Project-Tools-Guide`、`lessons/CSharp-Language-Pitfalls`、`index`、`logs`。
- **修改 Skill 文件**：`vibecoding-llmwiki/SKILL.md`（双副本）。
- **矛盾检测**：无（ADR-020 已同步标废弃，所有强制引用已移除）。

---

## [2026-08-19 11:33:26] feat | Stateless 5.20.1 本地化（ADR-020）+ V3 阶段B/C 落地（安全互锁 + 故障恢复）

- **来源**：用户需求（T1 Stateless NuGet 本地化 / T2 设备状态流程更新到 V3 全目标能力）
- **T1 内容**：Stateless 5.20.1 走 ADR-020 本地化——`Stateless.dll`（167KB，纯托管 netstandard2.0，无原生/卫星依赖）拷入 `3rdDepend/`，csproj 中违规 `<PackageReference Include="Stateless">` 改为本地 `<Reference>`，清理 `obj/` NuGet 产物（project.assets.json/nuget.g.props/nuget.g.targets/dgspec.json 等）。
- **T1 决策**：按用户拍板**修改 ADR-023**——Stateless 完成离线打包（ADR-020 合规），但**不绑定任何消费代码**，「保持自定义状态机」主决策不变，作为未来评估的离线前置。
- **T2 内容**：设备状态/流程更新至 V3 完整目标能力。
  - **收口状态机迁移**：移除 `MainDeviceThread._powerOnInitialized` 布尔残余（3 处赋值 + 1 处读取），`IsPowerOnInitialized` 改读 `MainStateMachine.CurrentState == DeviceState.Standby`。
  - **阶段B 安全互锁**：新增 `Safety/SafetyThresholds.cs`（PLC 阈值/使能开关/安全门位）、`Safety/SafetyInterlockResult.cs`（聚合结果+未通过原因列表）、`Safety/SafetyInterlockChecker.cs`（读 PLC S7 ReadBit/Read\<ushort\> + 设备就绪 + 门控信号，聚合判定）；`MainDeviceThread.OnWeldingStartCommand` 焊接门控接入互锁检查，未通过禁止焊接并记日志。
  - **阶段C 故障恢复**：新增 `Safety/FaultRecord.cs`（故障记录模型）、`Safety/FaultRecoveryManager.cs`（SQLite 持久化 + 自动重连/重测重试策略）；`DeviceStateMachineBase` 新增 `FaultOccurred` 事件（Alarm 转换时触发），`MainDeviceThread` 订阅并注册恢复策略。
- **修改代码文件**：
  - `AdaWeldSystem.csproj`（PackageReference→Reference + Safety 5 文件注册）
  - `3rdDepend/Stateless.dll`（新增）
  - `Workflow/MainDeviceThread.cs`（收口 + 互锁门 + 故障订阅）
  - `DeviceStateMachine/API/DeviceStateMachineBase.cs`（FaultOccurred 事件）
  - `Safety/`（5 个新文件）
- **Wiki 更新**：ADR-023 更新（Stateless 本地化落地备注）、`architecture/V3-Architecture` 路线图阶段B/C 勾选、`modules/DeviceStateMachine`、`api/DeviceStateMachine`、`index`。
- **备份**：`AdaWeldSystem_backup_20260819_0926.tar.gz`（bin/obj 排除）。
- **编译验证**：待用户 VS2026 构建确认（本环境无 MSBuild 直接调用验证）。

---

## [2026-08-18 18:28:20] fix | 修复编译错误：ScottPlot.Plottable.Signal 类型不存在

- **来源**：编译报错（用户反馈）
- **问题**：`MainPage.cs` 中 `private ScottPlot.Plottable.Signal _contourSignalPlot;` → CS0234「命名空间"ScottPlot.Plottable"中不存在类型或命名空间名"Signal"」。
- **根因**：ScottPlot 4.1.74 中 Signal 图的类型名为 `ScottPlot.Plottable.SignalPlot`（含 Plot 后缀），而非 `ScottPlot.Plottable.Signal`。`AddSignal()` 方法返回值即为 `SignalPlot`。
- **修复**：将 `ScottPlot.Plottable.Signal` 更正为 `ScottPlot.Plottable.SignalPlot`（仅 1 处字段声明）。
- **修改代码文件**：`UIDesign/ControlPage/MainPage.cs`
- **Wiki 更新**：[[guides/Project-Tools]] §3 新增 AddSignal 用法说明 + 类型名易错点；核心对象模型表述同步修正；禁止行为新增一条。
- **编译验证**：MSBuild 构建成功（0 错误，仅原有警告）。

---

## [2026-08-18 16:19:38] fix | 修复编译错误：_measuredFps 字段 volatile double 不支持

- **来源**：编译报错（用户反馈）
- **问题**：`IntelligentLaserCameraRun._measuredFps` 声明为 `volatile double` → CS0677「可变字段的类型不能是 double」。C# `volatile` 仅支持引用类型、整型（含 bool/IntPtr/UIntPtr），不支持浮点类型。
- **修复**：移除 `volatile` 关键字。该字段仅用于 UI 显示实测 FPS，轻微陈旧可接受；x64 平台下 double 读写是原子的（8 字节对齐），回调线程写、UI 线程读无撕裂风险。
- **修改代码文件**：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`

---

## [2026-08-18 16:08:08] coding | 英莱相机：硬件状态检测 + 帧率切换保护 + 实测 FPS + UI 层去 SDK + 算法页实时参数

- **来源**：用户需求（5 项）
- **需求 1 — 初始化后检测硬件状态**：`IntelligentLaserCameraRun` 新增 `DetectHardwareStatus()` + `IlHardwareStatus` 快照（LaserOn/CaptureCameraOn/SensorRunning/FpsModel/CurrentFps），新增 `IsCaptureCameraOn()`（`FetchSensorInfo`→`DwCaptureCameraEnable`）、`IsSensorRunning()`（`FetchSensorFps`>0 判断）、`FetchFpsModel()` 三个状态查询方法；`ILCamPage` 连接后调用同步 UI 状态（激光按钮文本、相机按钮文本、帧率下拉选中项、帧率下拉使能），解决「上次异常退出未关相机/激光，重连后状态不一致」问题。
- **需求 2 — 相机开启时禁用帧率切换**：`ILCamPage` 新增 `UpdateFpsDropdownState()` 辅助方法，`IsCaptureCameraOn()` 为 true 时 `cmbFps.Enabled=false`；`cmbFps_SelectedIndexChanged` 二次校验，相机开启时弹警告并 `RefreshFpsSelect()` 回滚；`UpdateConnectionUi` 与 `UpdateModeUi` 空闲分支均调用 `UpdateFpsDropdownState()` 统一管理。
- **需求 3 — UI 层不直引 SDK 原生类型**：新增托管枚举 `IlFpsModel`（STANDERD=1/FAST_SPEED=2/HIGH_SPEED=3），`ApplyFrameRateModel(IlFpsModel)` 公共重载做 UI 层入口，SDK 原生枚举版本降为 `private`；`ILCamPage.cs` 移除 `using IntelligentLaser_CSharp;`，全 UIDesign 目录零 SDK 引用（grep 验证）。
- **需求 4 — 实测 FPS 标签（首帧剔除）**：`MillionOutlineCallback` 内用 `1000ms/帧间隔(ms)` 计算实时帧率，`_firstFrameSkipped` 标志控制首帧剔除；`ResetMeasuredFps()` 重置计数器，`SetSensor(true)` 自动调用；`MeasuredFps` 公共属性供读取；`ILCamPage.Designer.cs` 新增 `lblMeasuredFps` 标签（轮廓点右侧，12px 宋体），`RefreshDisplay()` 每帧更新显示（保留 1 位小数）。
- **需求 5 — 算法编辑页展开当前 Job 实时参数**：`ILAlgoPage.InitIlModule` 连接时优先 `FetchAllJobParams()` 从设备拉取当前 JOB 实时参数，失败才回退 `LoadOfflineCache()` 离线缓存；旧逻辑相反（优先离线缓存），可能显示过时/默认参数。
- **修改代码文件**：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`、`UIDesign/TabPage/ILCamPage.cs`、`UIDesign/TabPage/ILCamPage.Designer.cs`、`UIDesign/ViewPage/ILAlgoPage.cs`
- **Wiki 更新**：[[modules/IntelligentLaserCam]] 关键事实补一条；[[api/IntelligentLaserCam]] 成员表增 7 项；[[lessons/IntelligentLaser-Pitfalls]] 新增 §5 UI 与状态管理（4 条教训）；`wiki/index/index.md` 模块与 API 条目更新摘要。
- **ADR 检查**：无新决策，遵循 ADR-001（Dispose 模式）、ADR-002（C#7.3）、ADR-016（命名空间解耦）。

---

## [2026-08-18 14:55:00] wiki-slimming | 知识库瘦身：64个lessons合并为8个综合指南 + SunnyUI/V2架构内容归档

- Lessons 从 64 个合并为 8 个综合指南文档
- SunnyUI 历史内容归档至 archive/SunnyUI-Legacy.md
- V2 废弃架构内容归档至 archive/V2-Architecture-Legacy.md
- 删除废弃文件 74 个（63 lessons + 11 废弃ADR/API/模块/架构）
- 总文件数从 168 减至 104（减少 38%）

---

## [2026-08-18 14:14:10] fix | 修复 ILCamPage 两处编译错误：EmIntelligentFpsModel 命名空间 + IntEventArgs 属性

- **来源**：编译报错（用户反馈）
- **问题 1**：`ILCamPage.cs` 使用 `EmIntelligentFpsModel` 枚举但缺少 `using IntelligentLaser_CSharp;` 指令 → CS0246
- **问题 2**：`cmbJob_SelectedIndexChanged` / `cmbFps_SelectedIndexChanged` 误用 `e.SelectedIndex`，`AntdUI.IntEventArgs` 无此属性 → CS1061
- **修复**：① 添加 `using IntelligentLaser_CSharp;`；② 改用控件自身属性 `cmbJob.SelectedIndex` / `cmbFps.SelectedIndex`（与项目中其他 Select 用法一致）
- **修改代码文件**：`UIDesign/TabPage/ILCamPage.cs`
- **矛盾检测**：无

---

## [2026-08-18 14:08:23] coding | 英莱相机：帧率设置 + JOB 切换补全 + 重连回调修复 + 结果显示合并

- **来源**：用户需求（4 项）
- **操作**：
  1. `IntelligentLaserCameraRun` 新增 `ApplyFrameRateModel(EmIntelligentFpsModel)` 公共方法，封装 `SetSensorFpsModel` + `FetchSensorFps`，设置成功后刷新 `ScanRateHz`
  2. `ILCamPage` 新增帧率模式下拉（STANDERD / FAST_SPEED / HIGH_SPEED 三档），连接后自动填充并选中当前档位
  3. `ILCamPage` 补全 `cmbJob_SelectedIndexChanged` JOB 切换逻辑，失败回滚显示
  4. 修复重连无回调：`ILCamPage.btnConnect_Click` 在 `ConnectManual` 成功后自动 `SetSensor(true)` 恢复传感器使能
  5. 结果显示合并：移除 `ILAlgoPage` 的结果面板及回调，`ILCamPage` 结果从纯文本 Label 升级为 `AntdUI.Table` 表格形式
- **修改代码文件**：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`、`UIDesign/TabPage/ILCamPage.cs`、`UIDesign/TabPage/ILCamPage.Designer.cs`、`UIDesign/ViewPage/ILAlgoPage.cs`、`UIDesign/ViewPage/ILAlgoPage.Designer.cs`
- **新增 Wiki 页面**：`lessons/IntelligentLaser-ReconnectCallback.md`
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`、`api/IntelligentLaserCam.md`、`wiki/index/index.md`
- **矛盾检测**：无

---

## [2026-08-18 11:52:08] lint | 每周例行维护：Phase 4 Lint 健康检查 + 代码漂移修复 + 日志截断备份

**来源**：每周例行维护任务（LLMWiki 知识库全量自检 + 代码漂移检测 + 日志截断）。

**Phase 4 Lint 健康检查**：
- 矛盾检测：通过（ADR-020 双文件为有意历史保留设计，旧文件 status=deprecated + superseded_by 明确指向新文件）
- 孤儿页面：0 个（全部 167 页均被 index.md 索引）
- 死链：8 处均为 `vibecoding-workflow.md` 模板示例（代码块内），非真实红链，无需修复
- 外链完整性：0 个失效

**代码漂移检测**（code-review-graph + Grep 比对）：
- 图谱状态正常（2224 节点/10487 边/162 文件，2026-08-17 更新）
- 修复 `api/NetworkPort.md`：`INetworkPort`/`NetworkPortBase` 为 V2 规划未实装（代码中不存在），页面原描述为实际接口，已标注「V2 规划，未实装」与 [[modules/Comm]] 一致
- 修复 `wiki/index/index.md`：Comm 模块摘要由旧 `NetworkPort/` 四层结构更新为实际 `CommBase/` 结构；NetworkPort API 摘要标注「V2 规划，未实装」
- 其余 191 处文件引用差异均为误报（历史引用/官方 SDK 引用/设计器文件，文档已正确标注合并或迁移）

**日志截断与备份**（每周任务）：
- log.md 条目数 83 → 50（保留最新 50 条）
- 33 条旧记录备份至 `logs/backup/log_2026-08-18.md`（新建）
- 本次维护不修改任何代码程序

**新增工具脚本**：`tools/lint_scan.py`、`tools/check_adr_status.py`、`tools/drift_scan.py`、`tools/drift_scan_precise.py`、`tools/truncate_log.py`

---
## [2026-08-18 11:39:26] knowledge | 英莱传感器/回调/激光三层控制解耦澄清

**来源**：用户澄清——图像在英莱相机使能后即可采集到回调数据，激光开启仅控制物理照射，与图像回调无关。

**知识沉淀**：
- `lessons/IntelligentLaser-SensorCallback-LaserIndependence.md`：新建——传感器使能=回调触发源头，激光=仅照射控制，三层完全解耦
- `modules/IntelligentLaserCam.md`：新增关键事实条目
- `api/IntelligentLaserCam.md`：数据链路末补充解耦说明
- `wiki/index/index.md`：新增 lesson 索引条目 + 近期变更行

**代码状态**：无需修改——当前代码已正确反映此逻辑（`OpenSensor` 中 `SetSensor/SetLaser/SetCaptureCamera` 为独立并列调用，`MillionOutlineCallback` 内不检查激光状态）

## [2026-08-18 11:31:44] coding | 终版：恢复demo原版公式，仅改center为图像中心

**前三轮全错**（矩形折叠/originX间接/halfExtent自创），用户驳回。**终版：demo 原版公式 `center ± |corner*rate|` + `trans = center + mm*rate`，仅改 `center = (w/2, h/2)`**（弃用 demo 的 `fPersent/dwOffset`）。mm 栅格原点(0,0) 在图像中心。

**根因**：demo 的角点/trans 公式本身正确，只是 `center` 的 `fPersent/dwOffset` 计算使十字未对齐图像中心。**不要自创公式——demo 是对的**。

**Wiki 更新**：API/Module/Lesson/Index 全部修正为终版方案；log 记录四轮迭代。

## [2026-08-18 11:20:17] coding | 修复rate计算：按最大半幅而非框架尺寸，解决框架偏移溢出

**BUG**：第三轮 `calib.Center` 直接映射到图像中心正确，但 `rate = min((w-2m)/cornerW, (h-2m)/cornerH)` 只算了框架尺寸（7×4mm），没算框架相对中心的偏移（8mm）。例：`Center=(8,5)`，`rate=100`，左边缘 `w/2-8*100=-400px` 溢出画面，只有右半边可见。

**修复**：`rate = min((w-2m)/(2*halfExtentX), (h-2m)/(2*halfExtentZ))`，其中 `halfExtentX/Z = max(|corner[i] - Center|)` 为各角点到标定中心的最大半幅。截图数据验证：`halfExtentX=8, halfExtentZ=5`，新 `rate=43.75`，框架四角全在 margin 内，十字交叉在画面中心相交。

**Wiki 更新**：API 比例换算段、Lesson 终版方案+第三轮弯路、log。

## [2026-08-18 11:14:18] coding | 英莱校准框终版修复：calib.Center直接映射到图像中心，mm栅格对齐真实值

**前两轮均被驳回**：第一轮矩形折叠（丢梯形），第二轮 `originX/originY` 间接映射（仍以 mm 原点(0,0) 为基准，负值 mm 仍溢出）。

**终版方案**（`IntelligentLaserCameraRun.cs` `ConvertContourToMatDemo`）：
- **恢复原始 `cornerW/cornerH` 计算**（两角点差，非四角包围盒）
- **`calib.Center` 直接映射到图像中心**：`center = (w/2, h/2)`，十字交叉在此
- **所有点相对 Center 偏移**：`screen = center + (mm - Center) * rate`（Y 轴屏幕向上为负）
  - 角点：`(center.X + (corner[i][0] - Center[0]) * rate, center.Y - (corner[i][1] - Center[1]) * rate)`
  - 轮廓：`trans(y,z) = (center.X + (y - Center[0]) * rate, center.Y - (z - Center[1]) * rate)`
- **mm 虚线栅格**：以 `calib.Center` 为原点，`stepMm=max(1,round(40/rate))`，画面可见 mm 范围 `[Center-w/(2r), Center+w/(2r)]`，垂直/水平网格线 + 底部/左侧 mm 标注
- 关键：**不再以 mm 原点(0,0) 为参考，而是以 `calib.Center` 为基准做相对偏移**。轮廓 mm 有负值时自动向图像中心两侧展开，不会溢出。

**自审**：清除旧符号 `originX/originY/halfW/halfH/fPersent/dwOffset`；无公共接口/Designer/Dispose/.csproj 变更；`DashStyle` 依赖 `using System.Drawing.Drawing2D`（已存在）。

**Wiki 更新**：API/Module/Lesson/Index 全部修正为终版方案；log 记录三轮迭代。

## [2026-08-18 10:57:25] coding | 英莱校准框改为保留梯形形状+仅平移居中，并新增mm虚线刻度栅格

**背景**：上一轮把校准框折叠成半宽/半高对称矩形（`center±(halfW,halfH)`）虽保证居中，但**丢失了真实梯形形状**，用户驳回归还：只要求居中显示、不得改形。

**本轮修复**（`IntelligentLaserCameraRun.cs` `ConvertContourToMatDemo`）：
- **保留梯形**：取 4 角点 mm 包围盒求统一比例 `rate=min((w-2m)/cornerW,(h-2m)/cornerH)`；四角点用**真实 mm 坐标经同一仿射** `屏幕(x,z)=(originX+x*rate, originY-z*rate)` 映射，形状保真。
- **仅平移居中**：新增映射原点 `originX=w/2-CalibrationInfo.Center[0]*rate`、`originY=h/2+CalibrationInfo.Center[1]*rate`，使标定中心点 `Center` 恰好映射到画面中心（十字交叉居中）。轮廓折线 `trans` 改用它，与校准框保持对齐。
- **mm 虚线刻度栅格**（校准模式，画最上层）：`stepMm=max(1, round(40/rate))` 取整 mm → 垂直网格线（Y 横向）`x=originX+k*stepMm*rate`、水平网格线（Z 高度）`y=originY-k*stepMm*rate`，仅绘落到画面内的线，底部/左侧 8.5px 灰色宋体标注对应 mm 值（`0x80` 虚线 / `0xAA` 文字）。

**自审**：清除旧符号 `halfW/halfH/fPersent/dwOffsetX/dwOffsetY/offsetCenterH`；`DashStyle` 依赖 `using System.Drawing.Drawing2D`（已存在）；仅改私有绘制方法，唯一调用 `IntelligentLaserCameraRun.cs:903`，无公共接口/Designer/Dispose/.csproj 变更。

**Wiki 更新**：API `IntelligentLaserCameraRun.md` 绘制段 & 演进记录；module 校准框条目；lesson 终版方案+「居中≠改形状」弯路；index 条目与近期变更；本条日志。

## [2026-08-18 10:37:44] coding | 修复英莱相机显示画面四边框缺失/顶部被裁/十字不居中

**问题现象**：`ConvertContourToMatDemo` 校准模式下校准框四边框缺失、上半部分被裁，十字交叉不居中。

**根因**：照搬官方 demo `resetInnerData` 的角点公式 `center ± |corner*rate|`，隐含「校准原点在画面中心」（`Center≈(0,0)`）；真机 `Center[1]`（高度 mm）非零时角点按绝对 mm×rate 偏移，顶边随 `Center[1]` 上移被裁、十字偏离中心（复现：`LeftTopCorner[1]=50`、`Center[1]=15`、`rate≈7` → `topEdge.Y=-45`）。

**修复**（`IntelligentLaserCameraRun.cs` `ConvertContourToMatDemo` `hasCalib` 分支）：
- 弃用 `offsetCenterH/fPersent/dwOffsetX/dwOffsetY` 与 `calib.Center` 参与框定位
- 改按校准矩形**半宽/半高对称居中**：`center=(w/2,h/2)`，`halfW=cornerW/2*rate`、`halfH=cornerH/2*rate`，四角 = `center ± (halfW,halfH)`
- 因 `rate=min((w-2m)/cornerW,(h-2m)/cornerH)`，四边框必落在边距内不裁切，十字交叉居中；轮廓 `trans` 仍以同一 `center` 为原点与框对齐

**自审**：仅改私有绘制方法，唯一调用处 `IntelligentLaserCameraRun.cs:903`（MillionOutline 回调内），爆炸半径隔离本文件；无公共接口/Designer/Dispose/.csproj 变更；ADR-001/002 与 Lessons 门禁无违反。备份 `AdaWeldSystem_backup_20260818_103630.zip`。

**Wiki 更新**：
- `api/IntelligentLaserCam.md`：绘图段更新居中方式
- `modules/IntelligentLaserCam.md`：校准框条目补 02-18 居中修正
- `lessons/IntelligentLaser-DemoCenterOriginAssumption.md`：新建教训
- `index/index.md`：新增索引条目+近期变更行
- `logs/log.md`：本条日志

## [2026-08-18 09:54:16] coding | 修复英莱相机回调注册顺序——校准框不显示 + 参数页面无数据

**根因**：`ConnectCore` 中 `RegisterCallbacks()` 在 `ConnectToSensor` **之后**调用，但 SDK 连接完成时会**一次性触发** `InternalRefCornerPts`（校准框角点）和 `RecvInitJobParamsInfo`（Job 参数元数据）回调，注册晚了两个回调都丢失。

**修复**：
- `ConnectCore`：`RegisterCallbacks()` 从 `ConnectToSensor` 之后移到**之前**（InitSDK 成功后立即注册）
- `RegisterCallbacks`：新增 `if (_hostHandle.IsAllocated) _hostHandle.Free();` 防止连接重试时 GCHandle 泄漏

**影响范围**：
- 校准框/十字架显示正常（`CalibrationCallback` 在连接时触发，`_calibration.HasData=true`）
- 参数页面正常显示（`InitJobParamsCallback` 在连接时触发，`_jobParams` 缓存填充）

**Wiki 更新**：
- `api/IntelligentLaserCam.md`：更新 `ConnectCore` 描述与关键设计节
- `modules/IntelligentLaserCam.md`：新增回调注册顺序修正条目
- `lessons/IntelligentLaser-OneTimeCallbackOrder.md`：新建教训文件
- `index/index.md`：新增索引条目+近期变更行
- `logs/log.md`：本条日志

## [2026-08-17 16:59:23] coding | 英莱相机显示画面（校准框+大十字架）+ 相机参数编辑补全（含上下限）+ Job 参数分组

**变更文件**：
- `IntelligentLaserCameraRun.cs`：新增 `IlCalibrationInfo` 托管快照类（中心点+4角点，mm）；注册 `IntelligentRegisterCallBack_InternalRefCornerPts` 校准回调（`CalibrationCallback` 捕获校准数据）；新增 `CalibrationInfo` 属性；`ConvertContourToMatDemo` 改为实例方法，有校准数据时绘制黄色校准框（矩形区域，填充深色背景）+ 浅灰大十字架（过中心点裁剪到四边）+ 浅绿角点/中心点 + 红色特征点（参照官方 demo resetInnerData/TransPoint/Paint），无校准数据回退原自动缩放画法；新增 `CalcTwoLineCrossPoint` 线段交点辅助方法
- `ILParamPage.cs`：相机参数补全为 8 项（曝光时间/激光强度/抗弧光 + 提取算法/上/下/左/右边界），新增「范围」列（Min~Max，参照 demo 参数列表 DataGridView），保存时按范围校验并分别下发相机基础参数（SetSensorBaseParam）与提取算法/边界 Job 参数（SetJobParamter）
- `ILAlgoPage.cs`：Job 参数表新增「分组」列（按名前缀：相机/基线提取/分段/检测/结果处理/其他），结果处理参数 after_inspect_* 单独成组

**Wiki 更新**：
- `modules/IntelligentLaserCam.md`：校准回调 + 校准框/十字架绘制
- `api/IntelligentLaserCam.md`：IlCalibrationInfo/CalibrationInfo/CalibrationCallback

## [2026-08-17 16:24:17] fix | 编译修复：PointCloudData 无参构造 + EmguCV BitmapToMat

**修复**：
- `PointCloudData.cs`：添加显式无参构造函数。C# 规则：一旦定义任意构造函数（含拷贝构造），编译器不再自动生成默认无参构造，导致 `new PointCloudData()` 编译失败
- `IntelligentLaserCameraRun.cs`：`CvInvoke.CvMatFromBitmap` 不存在，改为 `bmp.ToMat()`（Emgu.CV 标准扩展方法），添加 `using Emgu.CV;`

**Wiki 新增**：
- `lessons/CSharp-CopyConstructorRemovesDefaultCtor.md`：C# 拷贝构造函数导致无参构造消失
- `lessons/EmguCV-BitmapToMat-Method.md`：EmguCV Bitmap→Mat 正确方法

## [2026-08-17 16:15:32] coding | 英莱相机 60FPS + demo 轮廓画法 + 连接状态显示修复 + 按钮布局修正

**变更文件**：
- `IntelligentLaserCameraRun.cs`：帧率 `HIGH_SPEED`→`STANDERD`(60Hz)，`_scanRateHz`=60，节流 16ms；`ConvertContourToMatDemo`(GDI+ 折线画法) 替代 `ImageAlgorithm.ConvertContourToMat`；移除 `_lastContourCloud` 暴露
- `ILCamPage.cs`：`UpdateModeUi` 自动/空闲时均从 `_ilCamera.IsConnected` 同步 `_isConnected`；回退 DrawContourPolyline，恢复 ShowMat 体系入口
- `ILCamPage.Designer.cs`：`btnCaptureCamera`(12,132) 左 / `btnLaser`(182,132) 右
- `PointCloudData.cs`：新增拷贝构造函数

**Wiki 更新**：
- `modules/IntelligentLaserCam.md`：数据链路 + 回调节流 + 新增 60FPS/demo画法/布局修正条目
- `api/IntelligentLaserCam.md`：数据链路流程图 + ScanRateHz/OpenSensor 描述

---

## [2026-08-17 14:29:11] fix | 英莱画面显示由轮询改为回调驱动（ContourFrameReady）
- 来源：用户审查代码发现——英莱页面用轮询刷新显示，与官方 demo 严重不符；demo 用回调更新画面，轮询只用于查激光/相机开关状态（本项目未用监控相机故无该状态）
- 操作：
  1. `LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`：新增 `event EventHandler ContourFrameReady` + 节流字段 `_lastFrameNotifyTime`；`MillionOutline` 回调成功换帧后调 `NotifyFrameReady()`（50ms 节流 ≈20fps，与 demo 一致）触发事件
  2. `UIDesign/TabPage/ILCamPage.cs`：删除 `_refreshTimer`（50ms 轮询），改订阅 `ContourFrameReady`，处理器 `OnContourFrameReady` 经 `InvokeRequired` 封送 UI 线程刷新轮廓画面/轮廓点数/分析结果；`HandleDestroyed` 退订
  3. `UIDesign/ViewPage/ILAlgoPage.cs`：删除 `_refreshTimer`（150ms 轮询），改订阅 `ContourFrameReady` 刷新实时识别结果表；`StopTimer()` 改名 `StopRefresh()`（退订事件）
  4. `UIDesign/SubView/AlgorithmEditForm.cs`：`HandleDestroyed` 调 `_ilPage.StopRefresh()`（原 StopTimer）
- 修改代码文件：IntelligentLaserCameraRun.cs、ILCamPage.cs、ILAlgoPage.cs、AlgorithmEditForm.cs
- 更新 Wiki 页面：api/IntelligentLaserCam、modules/IntelligentLaserCam、wiki/index/index.md
- 新增 Wiki 页面：lessons/IntelligentLaser-CallbackDisplay-NotPolling
- 矛盾检测：无

---

## [2026-08-17 09:31:53] coding | 英莱手动/自动统一封装 + 自动显示 switch
- 来源：用户需求——手动/自动用一套函数（手动多扫描IP），手动按钮执行+窗口显示轮廓；自动流程使用；自动模式页面 switch 控制显示（默认关闭），用状态机判断（不新增 bool）
- 操作：
  1. `LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`：提取私有 `ConnectCore(ip)`（InitSDK→ConnectToSensor→Core 校验→注册回调），`OpenSensor` 与 `ConnectManual` 均复用；`OpenSensor` 开外设复用 `SetLaser`/`SetCaptureCamera`/`SetSensor` 封装（不再直调 SDK），实现手动/自动一套函数
  2. `UIDesign/TabPage/ILCamPage.cs`：新增「自动显示」`AntdUI.Switch` 逻辑——订阅 `LineLaserWorkflow.StateChanged`，用状态机 `State` 判断自动运行中（Starting/Acquiring/Analyzing/Display/Adjusting/Completed）；运行中禁用全部手动按钮 + switch 控制 imageBox 轮廓刷新；空闲恢复按钮；`InvokeRequired` 守卫
  3. `UIDesign/TabPage/ILCamPage.Designer.cs`：新增 `swDisplay`/`lblAutoDisplay` 控件；顺带修复 `btnParamEdit` 缺 `new` 实例化的既有 bug（对应 lesson DesignerCs-ControlInstantiation）
- 修改代码文件：IntelligentLaserCameraRun.cs、ILCamPage.cs、ILCamPage.Designer.cs
- 更新 Wiki 页面：api/IntelligentLaserCam、modules/IntelligentLaserCam、modules/UIDesign、wiki/index/index.md
- 新增 Wiki 页面：无
- 矛盾检测：无

---

## [2026-08-15 11:46:16] fix | 复检四需求+相机参数分离，修复 btnScan 未加入面板
- 来源：用户要求用 vibeCoding skill 流复检
- 复检结论：需求①②③④ + 相机参数分离均已正确实现（csproj 注册、using、ADR-001 合规、事件订阅代码后置、Table 范式均通过）
- 修复：`UIDesign/TabPage/ILCamPage.Designer.cs` — `btnScan` 此前只 new+初始化+声明字段，**未 `panelControl.Controls.Add`**，导致「扫描」按钮不显示；补 `Controls.Add(this.btnScan)`（置于 txtIP 后）
- 红链检查：新 lesson 引用的 4 页面均存在；新符号（IlSensorInfo/IlCameraParam/FetchCameraParams/ApplyCameraParams/ScanSensors）均有引用，无死代码
- 修改代码文件：ILCamPage.Designer.cs

---

## [2026-08-15 01:58:53] fix | 相机参数与 Job 参数分离（ILParamPage 改编辑相机参数：曝光/激光强度/抗弧光）
- 来源：用户澄清——相机参数（曝光/激光强度/抗弧光）≠ Job 参数（算法：焊缝接头种类/特征点/向量），两套需分隔
- 操作：
  1. `LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs` — 新增 `IlCameraParam` 托管类（Exposure/Gamma/LaserPower）+ `FetchCameraParams()`/`ApplyCameraParams()`（走 `FetchSensorBaseParam`/`SetSensorBaseParam`→`IntelligentSensorBaseParams`，字段 Exptime/Gama/Power，⚠️ QA P0）
  2. `UIDesign/SubView/ILParamPage.cs` — 重写：由「Job Parameter 编辑」改为「相机参数编辑」，Table 三行（曝光时间/激光强度/抗弧光）+ 名称/当前值/单位/说明列，SetEditable+DoubleClick+CellEndEdit 校验（抗弧光 float，曝光/强度 uint），复用 FetchCameraParams/ApplyCameraParams
- 关键确证（dnfile 反编译 DLL）：相机参数结构 `IntelligentSensorBaseParams`（Exptime=曝光 uint / Gama=伽马·抗弧光 float / Power=激光强度 uint / FTempCpu=温度只读），方法 `FetchSensorBaseParam`/`SetSensorBaseParam`；Job 参数结构 `TIntelligentJobParam`（FetchJobParamter/SetJobParamter）——两套独立 API
- 修改代码文件：IntelligentLaserCameraRun.cs、ILParamPage.cs
- 更新 Wiki 页面：api/IntelligentLaserCam（新增相机参数 vs Job 参数对比表）、modules/IntelligentLaserCam、modules/UIDesign
- 矛盾检测：无（修正了原「Job Parameter 含曝光」的错误表述）

---
## [2026-08-26 10:57:43] standards | 升级代码精简规范为详尽版并沉淀检查脚本
- 将用户新建的 C# 代码审查规范（文件书写整理 / 逻辑精简 9 类 / 函数精简 + `csharp_review.py` 单文件扫描器）并入 [[standards/CodeSimplification]]，原四维度扩展为五维度，保留项目特有设备日志规范（去符号/始末/通讯全记录）。
- 归档 `scripts/csharp_review.py`（已 py_compile 校验通过）与 `wiki/standards/references/` 下 3 个规则文件 + 工作流说明（csharp-vibecoding-review-workflow.md）。
- 更新 index「代码精简规范」分类摘要、`decisions/ADR-022-CodeSimplificationStandard` 加注升级记录。
- 触发约定不变：用户说"代码精简/注释精简/日志规范"即读取本页执行，无需重复输入。

---

## [2026-08-27 13:32:26] simplify | FormMain/MainPage 注释与代码精简（五维度）
- 来源：用户需求——`@skill:vibecoding-llmwiki 对formmain mainpage 做一下注释和代码精简`；范围裁定：用户明确"强制排除的是 Designer.cs"——`*.Designer.cs` 才跳过，`UIDesign/` 下非设计器 `.cs`（FormMain.cs/MainPage.cs）同样适用五维度（纠正 [[standards/CodeSimplification]]/`decisions/ADR-022-CodeSimplificationStandard` 原"UIDesign 除外"误读）。
- 操作（FormMain.cs）：① 新增 3 个 #region 配对（私有变量/构造函数/私有函数），成员顺序规范；② 删除死函数 `HideTreeNode()`（仅被已注释掉的 `//HideTreeNode();` 调用，Grep 全量确认零引用），并删除该注释调用；③ 7 个私有方法 XML 注释精简为 ≤20 字 summary + `<param>`：FormMain_FormClosing/InitializeSystemStatusLabel/OnMainDeviceStateChanged/UpdateSystemStatusLabel/OnWorkflowStateChanged/UpdateStatusLabel/UpdateDeviceStatus。
- 操作（MainPage.cs）：① 删除 4 个未使用字段（robotDataRefresh/laserDataRefresh/ClinkTimes/StartTest，Grep 零引用）；② 删除死函数 `ResetChartLineData()`（零调用者）；③ 内联 `LoadComponent()`（仅订阅 `GlobalCommData.EventInfoHandler`）到构造函数并删除该方法；④ 新增 5 个 #region 配对（公共变量/私有变量/构造函数/私有函数/公共函数），将 4 个 public 方法（DisposeComponents/AddContourLineChart/AddNewDataLineChart/LogAppend）归集到末尾 `公共函数` region；⑤ public + private 方法 XML 注释补全（summary + param）。
- 约束合规：未引入/重写 `Dispose(bool)`（ADR-001）；FormMain 关闭链 `FormMain_FormClosed` 显式退订单例事件 + MainDeviceThread.Dispose + LineLaserWorkflow.Dispose；MainPage 用 `DisposeComponents()` + HandleDestroyed 触发（UI 类按需，ADR-001/034）；C# 7.3 语法不变（ADR-002）。
- 检查：`scripts/csharp_review.py` 复跑——FormMain 17→5 项（0 error/0 warn/5 info），MainPage 23→2 项（0 error/0 warn/2 info）；剩余 info 为设计器绑定 handler/空 region 提示，非问题。Grep 自审：region 配对、无悬挂删除符号引用、公共签名未变。
- 修改代码文件：FormMain.cs、MainPage.cs
- 更新 Wiki 页面：standards/CodeSimplification、decisions/ADR-022-CodeSimplificationStandard、index/index.md、api/FormMain、api/MainPage
- 新增 Wiki 页面：api/FormMain、api/MainPage、lessons/CodeSimplification-Scope-DesignerOnly
- 矛盾检测：无（已同步更正标准页"UIDesign 除外"误写为"仅 *.Designer.cs 除外"）
[2026-08-28 16:38:12] lint — Phase 4 健康检查完成。修复：①7 处把架构页错标为「V3 运动控制架构」的链接描述改为「设备控制架构规范页」；②10 处正文 V3 表述去代际化（CamBoxTracker/EncoderAxis/RSIPositionBuffer/KUKARobot/LaserCamBoxTrackingWorkflow-Legacy）；③3 处陈旧状态机描述（LaserWeldHead/MotionControl/Comm）改为 MapToDeviceState 四态口径；④MonitorCam/LineLaserCam 增插 ADR-037 更新说明；⑤project/overview 目录树删除已删的 DataModels/DeviceStateMachine，改为 MainDeviceControl（15 文件），模块总数 18→17。校验：红链 5→3（余为历史占位符）、孤儿页 2（历史页）、核心 10 页双向链接全覆盖、代码漂移 0（四态枚举/4 映射/TriggerAdjustment 无参/枚举 9-8-7/工艺不入级联/Dispose(bool) 0）。
[2026-08-28 17:09:57] fix+ingest — 命名空间与 using 全量体检（vibecoding Phase 0~4）：①修复 6 个文件缺失 `using AdaWeldSystem.MainDeviceControl.DeviceState;`（DeviceWorkflow 4 个工作流 + FlowState/DeviceWorkflowBase + ILCamPage）——根因：DeviceState 枚举与子命名空间同名，兄弟命名空间内裸类型用法解析为命名空间报 CS0118；②残留清理：csproj.bak_20260828_153931 移出项目树至工作区根（Workflow/Device 仅留 SimulationController+WeldActionRecord 属 ADR-037 有意保留，非残留）；③csproj 注册 0 孤儿 0 幽灵，失效 using 0；④教训页 Namespace-Compilation-Guide 第 2 节补录 CS0118 案例与规避约定；⑤备份 AdaWeldSystem_backup_20260828_170757.tar.gz。
[2026-08-28 17:16:04] fix+lint — 体检追加发现并修复：LineLaserWorkflow.cs 行173-184 孤儿残留代码块（SetStep 事件触发片段被误留至 MapToDeviceState 后，类级别引用不存在的 oldStep 致 CS0103，末尾多余 } 提前关闭类，后续 700 行落命名空间级）——删除后词法级全项目 130 文件大括号平衡通过（GSDMLGenerator/EKICommunication/XMLfile 三处经词法状态机与人工核验均为正则剥离误报）；教训页补录「孤儿代码块检测方法：词法状态机 + region 锚点深度拓扑」。
[2026-08-28 17:29:00] refactor+ingest — Workflow/ 目录归零：①SimulationController.cs 迁入 MainDeviceControl/DeviceWorkflow/ 并更名 SimulationWorkflow（namespace→AdaWeldSystem.MainDeviceControl.DeviceWorkflow，补 using AdaWeldSystem.Workflow 取 SimTestMode；INI 文件名沿用 SimulationController.ini 保用户配置兼容）；②WeldActionRecord.cs 迁入 PCLOperate/RunFileRecord/（namespace→AdaWeldSystem.PCLOperate.RunFileRecord，与消费方 RunRecordManager 同命名空间）；③全局更名 22 处引用（LineLaser/MonitorCamera/FormMain/MotionControlPage）；④清除 2 个死 using（RunRecordManager/DataReviewPage 原经 AdaWeldSystem.Workflow 访问 WeldActionRecord）；⑤csproj 条目替换，目录 Workflow/ 删除；⑥wiki：ADR-037 增补修订记录、api/SimulationController.md 更名 SimulationWorkflow.md、modules/Workflow 第3节改写、modules/DeviceControl 目录树补入、index/ADR-014/ADR-027/MotionControl/architecture 等现在时引用更新（历史决策叙述按约定保留原名）。备份 AdaWeldSystem_backup_20260828_172346.tar.gz。
[2026-08-28 17:51:14] refactor+ingest — MainDeviceControl 二次收敛（应用户两项要求）：①Safety 解散：Safety/ 子目录删除，SafetyFlow/SafetyInterlock/FaultRecoveryManager 平铺至 DeviceWorkflow/（namespace 统一 ...DeviceWorkflow），SafetyMonitorThread 更名 SafetyWorkflow（流程一律命名 Workflow 不用 Thread，该类无外部引用更名零风险）；②WorkflowState.cs 删除：状态契约按归属内联（线激光2类型→LineLaserWorkflow.cs、监控10类型→MonitorCameraWorkflow.cs、CAMBOX3类型→MotionControlWorkflow.cs、SimTestMode→SimulationWorkflow.cs，namespace 统一 ...DeviceWorkflow）；删除零消费类型 WorkflowSignalCode/WorkflowCompletedEventArgs/WorkflowErrorAbortedEventArgs/WorkflowManualStoppedEventArgs；AdaWeldSystem.Workflow 命名空间不复存在，11 处 using 清理（10 删 1 替换）。修复过程：首版切片脚本产生重复插入与括号失衡，改用「备份还原 + 括号计数法提取 + 单次插入」重建 4 文件。终检：类型唯一定义 0 重复、词法括号全平衡（XMLfile.cs 为 verbatim 误报）、region 配对与锚点深度全通过、csproj 0 孤儿 0 幽灵。wiki：ADR-037 二次修订、ADR-023 废止横幅、modules/Workflow 墓碑页、DeviceControl 树/Safety/架构页/index 同步。备份 AdaWeldSystem_backup_20260828_174104.tar.gz。
[2026-08-31 09:11:08] fix+ingest — LineLaserWorkflow 语法错误修复（用户 VS 编译反馈）：根因=8/28 二次收敛时契约块提取器缺陷——括号深度从声明行起算，声明行无大括号致提前终止，16 个类型全部截断成无体声明（波及 LineLaser/MonitorCamera/MotionControl/SimulationWorkflow 四文件，括号平衡检查无法发现此类损伤）。修复=修正提取器（跳过声明行、首个大括号起计数加块内成员断言）后从备份 174104 整体重建四文件，恢复 UTF-8 BOM。终检：类型唯一定义零重复、枚举成员 9/8/7/4 全数核对、region 与锚点全通过、死类型零残留。教训页补录提取器两陷阱与 BOM 约定。现场备份 AdaWeldSystem_broken_20260831_090705.tar.gz。
[2026-08-31 09:35:38] fix+ingest — DeviceState 命名空间遮蔽修复（用户 VS 编译反馈 CS0118）：MainDeviceControl 子树内 7 文件（6 工作流 + FlowState/DeviceWorkflowBase）的裸 DeviceState 被同名子命名空间遮蔽，8/28 补 using 的修法对子树内文件无效（C# 解析向外走在父层先命中子命名空间即停，using 轮不到）。修复=各文件命名空间声明内部注入 using DeviceState 别名（本级优先于向外走）。子树外 UI 文件普通 using 有效不受影响。全项目冲突扫描确认 DeviceState 为唯一类型名/命名空间段名碰撞。教训页 8/28 案例已修订（子树内别名 vs 子树外 using 的区分），ADR-037 增 0831 补充。备份 AdaWeldSystem_backup_20260831_093314.tar.gz。
[2026-08-31 17:46:43] refactor+ingest — 产品生命周期记录归口（ADR-046）：①`PCLOperate/RunFileRecord/` 4 文件（RunRecordManager/RecordFrame/WeldActionRecord/SmartRayConverter）迁入用户新建的 `ProductFileManager/`，namespace→AdaWeldSystem.ProductFileManager，类名与公共 API 不变，8 消费方（WeldProcess/CameraRun/IntelligentLaserCameraRun/AlgorithmManager/DataReviewPage/FileTraceForm/HelixRenderForm/RecordConfigForm）仅改 using；PCLOperate 仅余 3DModel/DataIO/Render；csproj 4 条改路径 + 删 VS 孤儿 Folder 条目。②新建 `SqlLiteDatabase/FaultRecordManager.cs`（继承 DatabaseManagerBase，DB 迁 DataBase\FaultRecord.db，string[] 写入契约不依赖领域类型，管理器内不做 try/catch 日志对齐 ProductDatabaseManager 范式）；FaultRecoveryManager 278→231 行：删 #region SQLite 持久化（EnsureDb/_db/_dbLock/_tableReady），Persist 保留为领域侧映射+截断+失败日志，FaultCategory/FaultRecord 数据载体留原文件（ADR-044 维持）。注意：用户在 AI 实施间隙已手动在 VS 完成目录移动（mv 报 cannot stat 暴露），按「重读文件、保留用户改动」惯例接手收尾。wiki：新建 ADR-046/modules/ProductFileManager/api/FaultRecordManager，更新 modules/Safety、SqlLiteDatabase（补 SqliteCore/ 子目录实况）、PointCloudData（RunFileRecord 迁出）、api/FaultRecoveryManager、index。备份 AdaWeldSystem_backup_20260831_173658.tar.gz。
[2026-09-01 10:21:10] ingest+standards — 步骤驱动工作流标准沉淀（ADR-047，status: proposed，仅知识库，未改代码）：用户提供外部参考实现 `HonorMachineTest/PcomDeviceInterface/Work/Process/`（`StationProcess.cs` 抽象基类 + `AssemblyProcess.cs` 实现约 3000 行 100+ 步 + `MachineControlWork.cs` 常驻线程），要求研究其写法并沉淀为标准 workflow 知识库。①新建 [[standards/StepDrivenWorkflow]]：三件套（命令变量 Slot / 常驻监听线程 `while`+节拍调 `FlowProcess()` / int 执行步 `WorkStep`+`WorkStartTime`）、**三层融合表**（设备四态 ADR-037 / 阶段态枚举 `SetStep` ADR-038 / 执行步 int 新增，**阶段态是对外名片、执行步是内部游标**）、基类 6+1 契约映射到本地命名、步骤号段位规范（0/10-99/100-199/700-799/800-899/900-999）+ 步号中文映射表强制登记、单步三范式（瞬时动作/等待完成/分支派发）、失败重试零代码（`if(!…) break;` 步号不变下拍重入）、超时三步走（Alarm+记故障+跳 9xx）、可观测性排故判据表、8 条红线。②新建 `decisions/ADR-047-StepDrivenWorkflow`：背景=现主流程事件驱动无线程、只能看"在哪一态"看不到"卡在哪一步/卡了多久"；与既有 ADR 关系表（**补充而非推翻 ADR-004**——ADR-004 反对顺序直写、确立 switch 分派，本 ADR 仅细化分派键并补时间维度；ADR-037/042/043/044 维持）；备选方案 4 项取舍。③两处对参考实现的**明确偏离**已写入红线：单步内禁阻塞等待（`CylinderStretch` 内 while 轮询、`case 17` 的 `Thread.Sleep(500)` 本地不引入，阻塞会同时冻结超时判据与指令响应）、不引入 `LoadConfig(XmlReader)/SaveConfig(XmlWriter)`（沿用项目既有 INI 持久化）。④更新 index（「代码精简与权责规范」分类新增触发说明 + 标准页行、决策表新增 ADR-047 行）、modules/DeviceControl（「核心语义」章新增「第三层：执行步」三层表）、api/MainDeviceWorkflow（顶部加 2026-09-01 规划变更横幅，标注接收 RobotPose 链路将由「回调→直接处理」改为「回调→写命令变量→线程→执行步推进」）。⑤用户核心收益已落标准页第八章：主程序加载流程后仅凭 `WorkStep` + `(DateTime.Now - WorkStartTime)` 两个变量即可完全监控流程状态。矛盾检测：ADR-004 已在 ADR-047「与既有 ADR 的关系」显式裁定为补充关系，非冲突。孤儿页检测：新标准页由 index + ADR-047 + modules/DeviceControl + api/MainDeviceWorkflow 4 处 inbound，ADR-047 由 index + 标准页 2 处 inbound。红链：全部 ``...`` 指向已存在页面（standards/WorkflowResponsibilityBoundary、standards/CodeSimplification、standards/UiStateSimplification、architecture/DeviceControlArchitecture、modules/DeviceControl、api/*、lessons/*、decisions/ADR-004/041/042/043/044）。代码漂移：本次未改代码，落地清单（标准页第十章）待评审确认后实施，P0=DeviceWorkflowBase + MainDeviceWorkflow。

[2026-09-01 11:27:44] refactor+ingest — 历史架构清除与 V1/V2/V3 表述去代际化（用户要求「去掉历史架构，只保留最新架构需求，不再区分 V1 V2 V3 这样的迭代需求」）：
- 范围（经 AskUserQuestion 确认）：删 7 个历史架构/模块归档页 + 现行页残留 V2/V3 表述一并改写为最新事实。
- ①删除 `archive/` 7 页（共 2306 行）：`V2-Architecture-Legacy`(673)、`V3-Architecture-Legacy`(383)、`V3-MotionControlArchitecture-Legacy`(429)、`DataModels-Legacy`(93)、`DeviceStateMachine-Legacy`(204)、`DeviceStateMachineAPI-Legacy`(114)、`LaserCamBoxTrackingWorkflow-Legacy`(102)。archive/ 由 9 页收敛为 2 页（保留 `SunnyUI-Legacy`、`CodeSimplification-Progress-20260826`，均非架构内容）。**删页不丢要求**：V3 安全互锁清单、故障恢复策略表、CAMBOX 全链路（数据流/轴定义/Z-BASIC 初始化/KUKA RSI 配置/时序对齐公式/异常保护表）已并入架构页第 9、10 章。
- ②架构页 `architecture/DeviceControlArchitecture.md` 305→446 行：第 9 章安全互锁与故障恢复整章重写（文件归属表 + 检查清单 + 恢复策略表 + `_alarmRecorded` + `RecordFault` 英文 key 坑），第 10 章运动控制整章重写，第 13 章由「历史变更」改为「维护约定」三条。页首加「唯一规范页、不按代际描述」横幅。
- ③`project/architecture.md` 完全重写：原页为 2026-07-20 人工审计版，依赖图含 `Workflow`/`DataModels`/`DeviceStateMachine`/`PointCloudData`/`InteliWeld` 五个**已删除模块**节点。改为扫描 `AdaWeldSystem/` 127 个 .cs 的 `using` 语句**静态推导**（13 顶层模块 + mermaid 依赖图 + 4 组循环依赖 + 7 条核心调用链 + 5 层分层约定），frontmatter 标注推导方法便于重跑。
- ④内容性错误修复（**经 find 核实代码实况后修正，非文字替换**）：
  - `modules/MotionControl.md`「V3 废弃内容」表把**现役** `MotionControlWorkflow`（`MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` 确认存在）列为已废弃并称「已从 .csproj 移除」——与代码相反。改为「已废弃内容与现存边界」表 + 易误判点注解（`MoveControlData` 仍保留、与 CAMBOX 是并存非替代关系；`MotionControlWorkflow` 是现役，仅内部软件逐帧调整职责被 CAMBOX 接管）。同页修复 `Workflow/` 过期路径、§V3 整章去代际化为「CAMBOX 硬件级实时跟踪架构」。
  - `modules/MonitorCam.md` 引用已删除的 `MonitorCam/Api/MonitorCameraStateMachine.cs`（find 确认不存在）；`Workflow/MonitorCameraWorkflow.cs` 路径过期；第 21 行「健康巡检并入工作流线程」与第 32/38 行「健康巡检下沉 MonitorCameraRun」自相矛盾。三处一并修正。
  - `modules/Comm.md` 删除「V2 架构规划：NetworkPort 层（未实装）」「V2 新增：机器人连接状态机」两整节（`INetworkPort`/`NetworkPortBase`/`RobotConnectionStateMachine` 均 find 确认不存在），压缩为「已取消的规划（勿再当作待办）」表。
  - `modules/KUKARobot.md` §7 整章去代际化；「V3 代码实现将在后续阶段执行」改为实装状态说明；§7.7 按 find 实况修正（`RSICommunication`/`EKICommunication`/`KUKADataTypes` 三文件**均存在**，「RSICommunication 已降级删除」为误述）。
  - `api/CamBoxTracker`/`api/EncoderAxis`/`api/RSIPositionBuffer`/`api/LaserWeldHeadController`/`modules/LaserWeldHead` tags 与页首「架构版本 V2/V3」去代际化；`api/IntelligentLaserCam`、`modules/IntelligentLaserCam`、`modules/UIDesign`（英莱轮廓误标 V3，实为 ADR-029 数据流）同步。
  - `guides/WinForms-UI-Threading.md` §3 去代际化，并把 `MainDeviceThread.DisposeComponents()` 更新为 `MainDeviceWorkflow.Dispose()`（ADR-037 更名 + ADR-001 释放入口）。
  - `decisions/`：ADR-023 加「当前状态 有效 + 命名澄清」横幅（本 ADR 描述的 CAMBOX 就是**当前架构本身**，V3 仅为当时叫法，防后人去找已删的 V3 架构页）；ADR-027/ADR-023/ADR-020 修正引用已删除实体的表述。
- ⑤`modules/Workflow.md` 由已废弃模块页改为 `status: deleted-placeholder` 重定向存根（含「内容去向」表 + 三个「请改读」链接），避免 26 处入链变红链。
- ⑥`index/index.md`：§一项目知识区三行摘要重写、§7.3 废止表去归档链接、§八归档文档删 7 行条目加清理说明横幅、模块摘要 3 处「V2 新增」与 `#V2` tag 清除。
- **故意不改**（误报排除）：`standards/CodeSimplification-*.md` 的「去 V2/Ex/With 后缀」是**方法名归一化规则**非架构代际；`api/IntelligentLaserSDK_CSharp_DevManual.md` 的 V1.5.827 是 SDK 版本号；`project/skill-evolution.md` 的 GeneralTech V2/V3 是**技能版本**演进；`lessons/SimulationC-Mode-Interruption.md` 的「V3 跟踪工作流已停止」是**日志原文引用**（改写即伪造引用）；ADR 正文的代际叙述按既有约定保留（ADR 记「为什么」，规范页只给结论），仅修正其中指向已删实体的事实错误。
- 校验：`tools/wiki_audit.py` 全绿——红链 0、孤儿页 0、index 重复行 0、内容重复页 0、无二级子目录。剩余 `V[123]` 命中均为上述**声明性表述**（「不按 V1/V2/V3 代际描述」）与 ADR 历史叙述，符合预期。
- 备份：`LLMWiki_backup_20260901_110330.tar.gz`（工作区根）。

[2026-09-01 11:49:24] refactor+ingest — 分类目录合并：`archive/` 取消 + 第二个架构页收口（用户要求「有 architecture和archive，我的要求是合并消除一个」）：
- **决策依据（实测数据）**：`architecture/` 1 页 446 行 **53 处入链**（现行、活跃）；`archive/` 2 页 454 行 22 处入链（其中 7 处是页内自引用，外部仅 15 处）。两者是全库最小的两个分类且名字相近易混。`archive/` 是「归档」语义，不能承载现行架构规范页，故**保留 `architecture/`，取消 `archive/`**。
- ①`archive/` 2 页迁入 `project/`（内容一字未改，仅位置变更）：`SunnyUI-Legacy.md`(401 行，UI 框架迁移史) → `project/SunnyUI-Legacy.md`；`CodeSimplification-Progress-20260826.md`(53 行，过期进度快照) → `project/CodeSimplification-Progress-20260826.md`。`archive/` 目录已删除，wiki 一级分类 11 → 10 个。
- ②**顺带收口第二个架构页**（上一轮遗留的不一致）：上一轮确立了「`architecture/DeviceControlArchitecture` 是架构唯一真相源」，但 `project/architecture.md`（模块依赖图，150 行，3 处入链）仍是一个平行架构页，违背该原则。其全部内容（13 顶层模块表 + mermaid 依赖图 + 4 组循环依赖 + 7 条核心调用链 + 5 层分层约定 + 静态推导方法）并入架构页**新增 §11「模块依赖与调用链（代码层事实）」**，原 §11/§12/§13 顺延为 §12/§13/§14，该页删除。全库自此**只保留一个架构页**。
- ③链接改写（11 个文件 25 处）：``archive/SunnyUI-Legacy``→`[[project/SunnyUI-Legacy]]`(15)、``archive/CodeSimplification-Progress-20260826``→`[[project/CodeSimplification-Progress-20260826]]`(4)、``project/architecture``→`[[architecture/DeviceControlArchitecture]]`(3)，以及 1 处错引修正。
  > **注（2026-09-01 补记）**：左侧为**已失效的旧路径**，按「失效路径改代码体」约定不再保留 wiki 链接语法，避免体检脚本误报红链。
- ④**修 1 处上一轮遗留错引**：`lessons/FaultRecoveryDeviceKey.md:41` 写「架构规范页（第 11 章 安全互锁与故障恢复）」，但重排后安全互锁是 **§9**（§11 当时是「与其他模块的关系」）。改为第 9 章。**教训：重排章节后必须全库回扫章节号引用，否则静默错引。**
- ⑤消除 `SunnyUI-Legacy.md` 的 **7 处页内自引用**（``archive/SunnyUI-Legacy`` 指向自己，源自早期合并遗留的「原文档：XXX」写法），改为本页章节锚点（§2.1 / §2.2 / §3.1）。页首加「归属变更」横幅说明 `archive/` 取消原因。
- ⑥架构页加**目录表**（14 章速查）——该页 598 行为全库第 5 大页，此前无 TOC，不利于检索。
- ⑦`tools/wiki_audit.py` **新增第 10 项检测「小分类检测」**：页数 ≤2 的一级分类提示合并（正是本次问题的根因，脚本此前无法自动发现）。豁免名单 `index/`（单页全库索引）与 `architecture/`（虽 1 页但是架构唯一真相源、598 行 53 处入链，独立分类便于检索，**勿合并**）。
- ⑧`index/index.md`：删除因 ② 产生的重复行（74/75 行同时指向架构页），把「模块依赖」信息并入架构页摘要；§八「归档文档」改为「历史归档（现归 project/）」并写明目录合并与架构页收口。
- 校验：`tools/wiki_audit.py` **10 项全绿**——红链 0 / 孤儿页 0 / index 重复行 0 / 内容重复 0 / 二级子目录 0 / 小分类 0。144 页 21322 行（删 1 页）。全库 `archive` 字样仅剩 1 处（新加的说明性横幅）。
- 备份：`LLMWiki_backup_20260901_114500.tar.gz`（工作区根）。

## [2026-09-02 02:22:00] fix | 删除 WorkflowRunMode 死代码，ManualOn/Off 与运行模式解耦

- 用户约定：ManualOn/ManualOff 不再决定 WorkflowRunMode 模式（它只与设备连接/断开相关），模式接入口后续另定。
- 删除：WorkflowRunMode 枚举、_runMode 字段、RunMode 属性（DeviceWorkflowBase.cs）；LineLaserWorkflow 的 CanAcceptExternalCommand 属性及其 OnCommunicationCommandReceived 调用点。
- 全仓交叉验证：WorkflowRunMode/_runMode/RunMode/CanAcceptExternalCommand 残留 = 0。
- Wiki 同步：DeviceControl.md、LineLaserWorkflow.md、ADR-048（追加四度修订缘由 + §7 已知限制改为「模式接入口待定」）。
- wiki_audit.py 全绿。

## [2026-09-02 02:35:00] feat | 初始化职责拆分 + 新增 ClearAlarmFlow 清除报警契约

- 需求：消除 InitializeFlow 中的复位职责（复位统一归 ResetFlow）；新增 ClearAlarmFlow 作为清除报警动作（仅建契约不实现逻辑）。
- 基类 DeviceWorkflowBase.cs：新增 protected abstract ClearAlarmFlow() 抽象方法 + public ClearAlarm() 模板（记日志→调 ClearAlarmFlow，与 Reset 对称）；初始化语义注释去「复位」；抽象契约 6→7。
- LineLaserWorkflow：InitializeInternal 四步改三步（删 resetDevice 关激光/关传感器）；ResetFlow 加入 SafeShutdownPeripherals() 关外设（复位职责归位）；InitializeFlow/ManualOn 注释同步。
- 其余 6 子类（MainDevice/Safety/MonitorCamera/MotionControl/WeldParamControl/LaserWeldHead）补 ClearAlarmFlow override（空实现/TODO）。
- 交叉验证：ClearAlarmFlow 7 子类全覆盖 + 基类 1 抽象声明；resetDevice 符号残留 = 0。
- Wiki 同步：ADR-048（五度修订缘由 + 契约表 + §4 复位/清除报警收敛 + 后果 6→7）、modules/DeviceControl、architecture/DeviceControlArchitecture、api/LineLaserWorkflow、api/MainDeviceWorkflow、index。
- wiki_audit.py 全绿。

## [2026-09-03 00:54:37] feat+fix | 设备日志统一出口 DeviceLog + 独立管控类 5 类 BUG 修复

- **用户裁定（本轮两个关键决策）**：
  ① `Tag` 不是死成员——「每个流程应该还需要增加 log 的统一写法，**tag 是给 log 用的**；另外两个主设备 StartWork 也需要有统一的 log；log 写法是**将 comm 的 ShowLog 封装**」。故 `Tag` 保留并收紧（不删）。**判据沉淀：0 消费 ≠ 死成员**——若它是横切关注点的载体（日志标签/序列化键/权限标识），或 raw 原档将其列为契约成员，须先确认设计意图再下结论。
  ② 其余 0 消费死成员（`CheckDeviceIOSafe()` / `IsStepTimeout()` 无参重载 / `StepStatusText` / `WorkElapsedMs`）**一律保留不删，只修 BUG**。
- **新增** `AdaWeldSystem/MainDeviceControl/DeviceLog.cs`（静态类，命名空间 `AdaWeldSystem.MainDeviceControl`）：封装 `GlobalCommData.ShowLog`，提供 `Write/Info/Warn/Error`。已手工登记进 `AdaWeldSystem.csproj`（旧式 csproj 无通配，新文件必须显式加 `<Compile Include>`）。
- **日志收敛（63 处 → 1 个出口）**：`MainDeviceControl/` 下 `ShowLog` 直调清零。标签约定=子工作流用基类 `Tag`（`object`→`string`，setter 降 `protected`）+ 基类 `protected Log(...)`；`DeviceControlWork`/`DeviceStatusWork` 用私有 `_tag` + 本类 `Log(...)`；`DeviceStateBase` 用 `StateName`；模拟模式用 `_simTag`。通讯收发报文仍走 `ShowCommunicationLog`，不混用。
- **BUG 1（CS0108）**：`MotionControlWorkflow` 的 `private const string Tag` 遮蔽基类 `public object Tag`（`string`/`object` 类型对撞）→ 删遮蔽声明，5 个子工作流改在构造函数首行赋 `Tag`。
- **BUG 2（非原子）**：`_workStartTicks`（long）裸读写 → `Interlocked.Exchange` / `Interlocked.Read`（32 位平台 64 位读写非原子，读到撕裂值会使 `IsStepTimeout` 误判）。
- **BUG 3（绕过锁，8 处）**：`DeviceControlWork` 里 `DoIdle`/`OnPoseArrived`/`StartMachine` 等直接读 `_status`，绕过 `Status` 属性的 `_statusLock` → 全部改走 `Status`。保留白名单 5 处（字段声明 / 锁对象 / getter / `SetStatus` 锁内块 / `ClearAlarm` 的 check-and-set 必须同锁内，拆开即 TOCTOU）。
- **BUG 4（停机重启误判超时，最严重）**：`DeviceControlWork` 不继承基类却自抄一套私有步机制，**漏抄基类「非运行态刷新时间戳」分支** → `RunLoop` 补 `else { ResetStepTime(); }`，`StartMachine()` 内补 `GoStep(StepIdle)`。原故障现象：**停机超 `PoseWaitTimeoutMs`（60s）后再开机，首拍即用停机时刻时间戳判超时，直接跳 900 失败收尾**。
- **BUG 5（失效 using）**：移除 `LaserWeldHeadWorkflow.cs` 中因改造而失效的 `using AdaWeldSystem.Comm;`。
- **编译验证受阻**：沙箱安全策略拒绝 `dotnet` / `msbuild` / C# 编译器（Known Windows LOLBin），且本机无 `C:\Program Files\Microsoft Visual Studio`。改用 Python 精确静态校验脚本替代（去注释后判 `Tag` 遮蔽 / `_tag` 残留 / `ShowLog` 回流 / 失效 using），**全部通过**。临时脚本 4 个已删除。**遗留：真编译验证待用户在 VS 内完成。**
- **工具修复（顺手，重要）**：`tools/` 下 5 个脚本硬编码旧机器绝对路径 `D:\A-A-项目类\04_研发项目\...`，迁移后 **静默失效**（`drift_scan` 恒扫 0 文件、`lint_scan` 直接 FileNotFoundError）。已全部改为按 `__file__` 推导（与 `wiki_audit.py` 同款）：`lint_scan.py` / `drift_scan.py` / `drift_scan_precise.py` / `check_adr_status.py` / `truncate_log.py`。修后 `drift_scan_precise` 报 **25 处真实漂移**（历史遗留：已删文件 `SafetyFlow.cs`/`SafetyInterlock.cs`/`SafetyWorkflow.cs`/`SimulationWorkflow.cs`/`MainDeviceWorkflow.cs`/`WorkflowStateBase.cs`、外部参考实现 `StationProcess.cs`/`AssemblyProcess.cs`、`designer.cs` 大小写误报）——本次改动引入 **0 漂移**。**该 25 处构成新的清理待办。**
- **Wiki 同步（+2 页 / 改 6 页）**：新增 `[[api/DeviceLog]]`、`[[lessons/DeviceControlWorkInheritanceBypass]]`（一句话根因=**不继承基类、另起炉灶抄一份私有实现，基类后补的正确性保障永远传导不过去**）；改 `standards/CodeSimplification`（§三新增 ⑤ 日志出口统一）、`standards/StepDrivenWorkflow`（§2.2 明确对独立管控类强制 + 审查清单加 2 条）、`architecture/DeviceControlArchitecture`（§2 目录加 `DeviceLog.cs` + 两个新小节）、`api/DeviceControlWork`（状态读取红线 + 步时间不变量表）、`api/DeviceStatusWork`、`index/index`（+2 行 + 3 条摘要修订 + 速查路由新增「写日志」条目）。
- 校验：`tools/wiki_audit.py` **10 项全绿**——红链 0 / 孤儿页 0 / index 重复行 0 / 内容重复 0 / 二级子目录 0 / 小分类 0。147 页 22718 行（+2 页）。`lint_scan.py` 147 页、死链 8 处全为 `project/vibecoding-workflow.md` 里的模板占位符（`modules/XXX` 等，已白名单）、孤儿页 0、ADR 冲突 0。

## [2026-09-03 01:00:53] backup | 推送 GitHub 云端备份（commit 4ac3f76）
- 走 `ada_backup.sh push`，一次性提交 11 项工作区改动（10 改 + 1 新增 `MainDeviceControl/DeviceLog.cs`），推送到 `origin/main`。
- 提交信息：`refactor(MainDeviceControl): ADR-049 三态模型落地，新增 DeviceLog 设备日志模块`。
- 推送前 `status`：本地 HEAD `f51ce43` = 远端 HEAD，ahead 0 / behind 0，工作区未提交 11 项，`3rdDepend` 误跟踪 0。
- 推送后 `status`：本地 HEAD `4ac3f76` = 远端 HEAD，ahead 0 / behind 0，工作区未提交 0，`3rdDepend` 误跟踪 0 —— 本地与远端完全一致，工作区干净。
- 无 rebase、无冲突，未使用 `--force`。

## [2026-09-03 10:40:32] sync | 从 GitHub 同步本地（双仓库 fast-forward）
- 背景：用户反馈本地（代码 + 知识库）落后于 GitHub。两仓库此前本地 HEAD 均落后远端 1 个提交、本地无未推送提交、工作区干净，具备 fast-forward 条件。
- **前置备份**（tar.gz，排除 bin/obj）：`AdaWeldSystem_backup_20260903_103519.tar.gz`（92M）、`LLMWiki_backup_20260903_103519.tar.gz`（22M）。
- **代码仓 `AdaWeldSystem/`**（`MrYangjf/AdaWeldSys.git`）：`f51ce43` → `4ac3f76`（ADR-049 三态模型落地 + 新增 `MainDeviceControl/DeviceLog.cs`），11 文件 +197/-124。已确认 `DeviceLog.cs` 登记进 `AdaWeldSystem.csproj` 第 148 行，且被 5 个文件引用（DeviceControlWork / DeviceStatusWork / DeviceStateBase / DeviceWorkflowBase）。
- **知识库仓 `Vicoding管理平台/`**（`MrYangjf/Vibecoding.git`）：`16caa5d` → `5eed14d`，75 文件 +1236/-873。要点：api 页 `MainDeviceWorkflow` 改名 `api/DeviceControlWork`、`SafetyWorkflow` 改名 `api/DeviceStatusWork`、新增 `api/DeviceLog`、删除 `api/SimulationWorkflow` 与 `modules/Workflow`；删除 ADR-023 / 032 / 033 / 036 / 041 / 042 共 6 页（引用处统一改写为「（已删除，见 ADR-049）」，无红链）；新增 `lessons/DeviceControlWorkInheritanceBypass`；`standards/WorkflowResponsibilityBoundary` 重写。
- **SKILL 双副本同步**：仓库 `LLMWiki/skills/vibecoding-llmwiki/SKILL.md` 已升 v1.5.0（27619 B），用户级 `~/.workbuddy/skills/vibecoding-llmwiki/SKILL.md` 仍为 v1.4.0（23204 B）。已覆盖同步，旧版另存 `SKILL.v1.4.0.bak.md`。v1.5.0 新增要点：Step 3.6 追加日志**必须用 Edit 而非 heredoc**（heredoc 正文触发关键字过滤会被安全策略拒绝）。
- **校验**：`tools/wiki_audit.py` 10 项——孤儿页 0 / index 重复行 0 / 内容重复 0 / 二级子目录 0 / 小分类 0；147 页 22718 行。
- **遗留待办（需用户裁定）**：体检第 1 项报 4 条红链 ``old``、``new``，全部来自 `skills/vibecoding-llmwiki/SKILL.md` 第 302 行——该行本身是**警告「不要写 ``old`→`new``」的规范条目**，示例文本自指被脚本误判为真链接（同文件名快照 `SKILL-v1.5.0-20260903-0112.md` 同理）。属远端已提交内容的自指缺陷，修复需改仓库文件并回推，本次**未擅自改动**。
  - ✅ **已解决（2026-09-03 12:08）**：`tools/wiki_audit.py` 新增 `mask_code()`，链接解析前先用等长空白替换围栏代码块与行内代码体，自指示例不再判为红链。当前体检第 1 项报「无（健康）」。

## [2026-09-03 12:08:58] docs | 修正 skill 与代码的漂移（从 GitHub 导入后全量对齐）
- 背景：项目刚从 GitHub 导入本机，SKILL.md 与 wiki 双方相对代码库均出现系统性漂移。用户确认执行**全量四包**，且**保持未提交**（不执行任何 git 写操作，叠加改动留用户自审）。
- **Step 2.1 备份**：`LLMWiki_backup_20260903_112307.tar.gz`（11 MB，排除 bin/obj）。
- **包 C（工具脚本）**：
  - `tools/drift_scan_precise.py` **完全重写**。修 4 类缺陷：① 硬编码旧机器绝对路径 → 改 `__file__` 推导（迁移后原版静默扫到 0 个文件却报「健康」）② 正则无边界断言 → `FormMain.Designer.cs` 被截成 `Designer.cs`（144 处误报）、`AdaWeldSystem.csproj` 截成 `.cs`（14 处），加双侧断言后误报归零 ③ 宽泛白名单掩盖真实漂移 → 改 `RENAMED`/`REMOVED`/`EXTERNAL`/`SPECULATIVE` 四点分诊，仅前两类计入待修正 ④ 新增 `> ⚠️ 历史名称提示` 横幅块豁免，避免映射表自伤。
  - `tools/wiki_audit.py` 新增 `mask_code()`（等长空白替换围栏块与行内代码体），消掉规范文本自指造成的 4 条红链。
- **包 B（wiki 漂移修正）**：144 处失效 `.cs` 引用全部处理完毕，`drift_scan_precise.py` **待修正 0 处 / 已标注 116 处**。策略：14 个历史 ADR 页插页首「历史名称提示」横幅（纯新增 93 行、零删除，保留决策当时旧名）；其余页保留旧名原文 + 追加「（现役 `X.cs`）」/「（已移除（原因））」注记；4 页（`modules/SmartRayCam`、`modules/UIDesign`、`people/UISpecialist`、`project/overview`）含目录树 / 行号引用 / 外部参考，机器标注不安全，改人工精确改写。
  - ⚠️ **中途返工两次，均已回退**：v1 机器直接替换产生 4 类语义破损（路径拼贴 `Sub2UI/UIDesign/TabPage/ILCamPage.cs`、外部项目 `PcomDeviceInterface/MachineStatusWork.cs` 被改、自指「ILCamPage 已完全替代原 ILCamPage.cs」、目录树塞全路径），16 页 `git checkout --` 回退后改标注式；行尾方向一度修反（误把 LF 写成 CRLF 又反向固化），最终以「与 HEAD 比对」为唯一判据纠正回 LF。
- **包 A（SKILL.md，v1.5.0 → v1.6.0，27619 → 34073 B，两副本已同步）**：修 7 项漂移 —— ① `WORKSPACE_ROOT` 从已不存在的 `D:\焊接程序开发` 改为现役工作区根，并加「会话开始先 `pwd` 校验、字面值过期就地修正」的自检规则 ② 关键 ADR 表由 6 条扩到 19 条（021/022/025/026/031/034/038/043/044/047/048/049/050）③ Lessons 表 8 个页名**全部已不存在**，逐条补「Now at」映射 + 列出现役 17 个 lesson 页 ④ 路径映射表补 `standards/`、`guides/`、`architecture/`、`tools/` 四项 ⑤ 漂移基线由「已知 25 处」改为「待修正 0 / 已标注 116」并写明四点分诊口径 ⑥ Step 2.1 备份脚本的硬编码旧根改为占位符 ⑦ 新增 Key Rule 13（LF 入库红线）、14（行区间替换 joiner 不得为空），并标注「本 Skill 领先 wiki 工作流页」。
- **包 D（wiki 回灌）**：`wiki/project/vibecoding-workflow.md` 补「核心规则（强制，不可绕过）」14 条 + **Step 2.6 正确性验证**（无 C# 编译器 → Python 静态校验 + 两轮迭代纪律 + `_tmp_*.py` 清理 + 显式声明「真编译待 Visual Studio」），补 `章节导航` TOC，目录重编号。
- **Phase 3 Ingest**：新增 `lessons/WikiDriftCorrectionPitfalls`（五坑：行尾污染 / 换行符被吃 / 机器替换语义破损 / 横幅自伤 / 正则无边界断言，含可复制收尾判据清单）；`index/index.md` 登记该教训页、更新 vibecoding-workflow 摘要、§维护说明扩为三脚本对照表 + drift 口径 + 两条脚本红线 + 链接解析豁免。
- **Phase 4 Lint**：`wiki_audit.py` 10 项全绿（红链 0 / 孤儿页 0 / 索引重复行 0 / 二级子目录 0 / 过小分类 0 / 内容重复 0）；`drift_scan_precise.py` 待修正 0。
- **未改动**：`AdaWeldSystem/` 代码仓**零改动**（本次纯文档与工具修正）。Vibecoding 仓全部改动**保持未提交**。
- **遗留**：① 本次未涉及 C# 代码，无编译验证需求 ② `project/vibecoding-workflow.md` 已达约 600 行逼近 TOC 阈值，后续扩充建议先拆分 ③ SKILL.md 两副本（`~/.workbuddy/skills/` 与 `LLMWiki/skills/`）已同步，但后者位于用户此前删除的 SKILL 快照同目录，最终保留与否请用户裁定。

## [2026-09-05 23:47:43] coding | 台达开发指导按用户裁定重写基线（雷赛参考 + 振镜归焊接头）

**触发**：用户澄清三点 —— ① 不再考虑正运动，即将使用台达作为运动控制器；② 原始项目参考的是**雷赛**（Leadshine），本来正运动也应该照雷赛写；③ **振镜控制与对焦控制将用焊接头连接**。

**Phase 0 检索**：
- 定位雷赛参考实现 `E:\SoftwareGit\HonorMachineTest\PcomDeviceInterface\MotionControl\`（`IMotion/` 抽象层 + `LSnmcControler/` 实现层 + `MontionManager` 业务层），逐文件读完 `MontionControl.cs` / `MontionAxis.cs` / `LSnmcMontionControl.cs` / `LSnmcMontionAxis.cs`（625 行）/ `LSnmcInputIO.cs`。
- 从台达 SDK `inc/C#/EtherCAT_DLL.cs` 正则抽取 **832 个真实 API 签名**，按功能域分组建雷赛→台达映射（此前已订正 6 处误名，本轮再补 `Target_Pos_Change` → `TargetPos_Change`）。
- 符号定位：振镜 `ZMotionGalvo` 绑轴 4/5、由 `ZMotionController` 持有；`ILaserWeldHeadController` **已有** `SetAutoFocusPosition`；`MotionControlWorkflow.cs:474` 留 `// todo 振镜摆动控制`。

**关键结论（写入 ADR-029）**：
- 雷赛单位换算是**控制器侧**（`smc_set_equiv` + `*_unit` 后缀 API，源码无任何乘除）；**台达无当量机制，必须 PC 侧乘除**，方向 `mm × Equiv = pulse`。这是最容易写反的一处。
- 雷赛六条可继承纪律：容器自注册 / 参数挂轴上 / **三段前置检查** / 阻塞-非阻塞成对 / 急停贯穿 / 到位与停止原因分离。
- 雷赛→台达差异处置：`smc_set_equiv`、`smc_set_pulse_outmode`、Modbus 族 **删或替换**；新增 `DeltaSlaveScanner` 与硬件急停 `GPIO_Emg_*`。

**Phase 2/3 产出（本轮纯知识库修订，C# 代码零改动）**：
- 重写 `wiki/guides/DeltaEtherCAT-DevGuide.md`（569 → 约 700 行）：基线声明置顶（正运动不再是迁移源 / 原档为落地主体 / 雷赛为参考基线 / 振镜归焊接头）；新增 §3 雷赛参考基线章节；§5.2 原档命名 ↔ 本项目命名取舍表；§14 OPEN #1 **关闭**（振镜/对焦归焊接头）。
- 新建 `wiki/api/LeadshineLSnmc-Reference.md`（雷赛参考基线：目录、抽象契约、六条调用范式、雷赛→台达 API 全对照、台达不适用项清单）。
- 新建 `wiki/decisions/ADR-032-MotionControllerDeltaReplacement.md`（D1~D7 七条决议 + 未决事项）。
- 更新 `wiki/modules/MotionControl.md`（台达章节改为「参考基线（雷赛）→ 计划（台达）」对照表，含命名取舍说明）。
- 更新 `wiki/index/index.md` 4 处（速查路由、api 区新增雷赛页、guides 条目重写、decisions 区新增 ADR-029）。

**未改动**：`AdaWeldSystem/` 代码仓**零改动**（用户明确「焊接头后面会有新的文档，现在按照不报错修改」，故振镜/对焦接口本次不重构）。

**遗留 / 待用户确认**：① 振镜在焊接头上的具体接口形态（扁平成员 vs 独立 `IGalvoScanner` 子模块）待焊接头新文档 ② 激光功率控制（台达 PWM 族 13 个）是否也归焊接头 ③ ECAM2 能否达现役 CAMBOX 硬件级同步，需实机验证 ④ Vibecoding 仓改动仍未提交。

## [2026-09-06 09:28:09] wiki | 台达运控文档改为全新模块落地规范（去现役对比）

**触发**：用户指出上一版文档仍在跟「现役」做对比，要求「全新的」——**程序文件结构与对外消费按原档**。

**Phase 0 检索**：通读原档 `raw/delta/运动控制模块开发文档_台达版.md` 全文 1323 行（含此前遗漏的 150–1113 主体段），抽取 §3 目录结构、§6 抽象层契约、§9 依赖与消费关系、§10 初始化流程；量化现文档现役对比残留 **41 处**。

**Phase 2 改写**：`wiki/guides/DeltaEtherCAT-DevGuide.md` 整页重写（669 → 1144 行），15 章：
- §2 目录结构照搬原档 §3（`IMotion/` 8 文件 + `DeltaEtherCAT/` 5 文件 + `Native/` 5 文件 + 模块根 `MontionManager.cs` / `Cylinder.cs`）
- §3 对外消费照搬原档 §9（消费关系图 + 明细表 + **依赖方向铁律 5 条**）
- §4~§7 分层设计（L1 Native / L3 台达实现 / L2 抽象层 / 业务层）
- §8 生命周期、§9 关键机制、§10 三例示例、§11 映射速查、§12 核验门禁、§14 落地清单、§15 OPEN

**命名裁定（撤销上一版）**：回归原档 `Montion*` 拼写 + `Delta*` 前缀，即 `DeltaMontionControl` / `DeltaMontionAxis` / `DeltaInputIO` / `DeltaOutputIO` / `DeltaSlaveScanner`。上一版提出的 `DeltaController` / `DeltaAxis` / `DeltaIO` **作废**。

**发现并订正原档缺陷 1 处**：原档 §6.2 把 `Equiv` 注为「脉冲/工程单位」，与其 §7.3 `ToPulse(v) = v / Equiv` 自相矛盾；正确语义为**工程单位/脉冲**（mm/pulse，与雷赛 `smc_set_equiv` 一致）。已在指导页 §9.1 与 ADR-029 D4 双处标注。

**Phase 3 回灌**：
- `wiki/modules/MotionControl.md` 台达章节去掉「替换正运动」标题与现役对照表，改为三层结构表 + 对外消费 + 关键机制 + 边界声明
- `wiki/decisions/ADR-029` 重写为「全新模块」决策（D1~D7），删去 ZMotion 处置章节，新增 D6 命名裁定、D7 分层依赖铁律
- `wiki/index/index.md` 3 处登记更新（专题导航 / guides / decisions）

**未改动**：`AdaWeldSystem/` 代码仓零改动（纯知识库修订）。

**校验结果**：现役词（现役/正运动/ZMotion/迁移/现状）**全部清零**；雷赛对照保留 15 处（原档自带基线，用户认可）；noBOM + LF 保持；三扫描待 Phase 4 复跑。

## [2026-09-07 21:56:38] coding | 状态前置问询落地：复位/初始化/启动链中止检测 + 运行态抢占即停

用户确认参考项目两项机制补齐：①复位动作前置循环问询状态；②Running 态每拍问询，被改为其他状态即停止。

**代码（2 文件，无新文件，未动 csproj）**：
- `DeviceControlWork.cs`：新增 `_driveStopped`（Interlocked 闭锁）、`IsActionAborted(expected, action)`、`IsInitAborted()` / `IsInitPreempted()`（静默版）、`StopSubDeviceDrive(flow)`。
  - `SubDeviceWork`：每拍问询 `Current`，非 Running 停止驱动并整机只记一次「子流程停止驱动」+ 级联 `CascadeWeldStatus(Stopping)`；恢复 Running 自动清标志。
  - `DoResetMachine`：EStop 前置拒绝复位；ClearMachine 后问询 NoReset；CascadeResetProcess 每步前置问询 Reseting；末步问询改 `IsActionAborted`（不覆盖被抢占后的新状态）。
  - `CascadeResetProcess`：循环内每步前置 `Current != Reseting` 即中止返回 false。
  - `DoInitializeMachine`：5 步之间每步 `IsInitAborted()` 问询；`WaitChildConnected` 等待循环每拍 `IsInitPreempted()` 提前退出。
  - `DoStartMachine`：置 Running 后问询一次，被抢占不拉起工作线程。
- `DeviceStatusWork.cs`：`ScanPulseIo` 增 `requireRunning` 参数（Sub* 五类 IO 非 Running 即丢弃记 Warning，命令类不门控）；`DispatchAction` 动作前后比对运行态，被抢占记一次变更日志。

**知识回灌**：`api/DeviceControlWork.md`（SubDeviceWork 新范式代码块、复位链 6 步门禁、初始化链问询章节、修正 2 处 drift：初始化就绪误写 SetStatus(Stop) 与残留 RecordFault）；`api/DeviceStatusWork.md`（动作线程问询 + Running IO 前置门控章节）；`api/HonorMachineTest-IOReference.md`（映射表复位中止检测 ⚠️→✅，新增运行态抢占即停行）。

**校验**：Python 静态校验括号平衡 + C#7.3 关键字 + 新符号计数全过；真编译待 VS。ADR-031 合规：中止/抢占日志均 Interlocked 或前置单点，只记一次。

## [2026-09-07 22:13:42] coding | 修订：线程只判断不执行，不修改状态（用户裁定）

用户对照参考项目再裁定：**线程（循环线程/扫描线程）发现状态不对就停止执行即可，不修改状态；状态一律由 IO 动作链（DoXxx → SetStatus）专门管理**。

- `DeviceControlWork.StopSubDeviceDrive`：**删除** `CascadeWeldStatus(Stopping)` 调用（线程层越权改焊接态）——只保留停止驱动 + 一次 Warning 日志 + 每拍清计时；`Stopping` 等迁移仍由停止命令链（`DoSubStop`）下发。
- 其余问询点自查确认合规：`IsActionAborted` / `IsInitAborted` / `IsInitPreempted` / `ScanPulseIo(requireRunning)` / `DispatchAction` 前后比对均为只读 + 日志；`DoResetMachine` / `DoStartMachine` 链内 `SetStatus` 属 IO 动作链执行体，是状态专门管理入口，非越权。
- wiki 同步：`api/DeviceControlWork.md`（SubDeviceWork 代码块与说明改「线程不改状态」）、`api/HonorMachineTest-IOReference.md`（映射表行补用户裁定）。

## 2026-09-07 23:06 线程问询范式合规核对沉淀
**范围**：对照 `HonorMachineTest/PcomDeviceInterface`（`MachineControlWork.cs` / `MachineStatusWork.cs`）只读核查 AdaWeldSystem 线程问询方式，零代码改动。
**结论**：合规范。①状态归属判断：线程只读 `Current` 决定执行/不执行，状态赋值只在 IO 动作链（参考 `ResetMachine` 的 `while(CurrentStatus==Reseting)` 门控 + WaitAll 后复查，与 `CascadeResetProcess` 每步问询同范式）；②防空调节拍：`BeatIdleMs=100`/`BeatWorkMs=10` 与参考同值，`WaitChildPollMs=100`，IO 三线程 50ms；参考 `LineWork`（无 Sleep 空转）与 `RunControl`（`while(true)`）属不借鉴项。
**wiki**：`api/HonorMachineTest-IOReference.md` 新增 §6.1 线程问询范式（两条铁律 + 逐点比对结论）。

## 2026-09-08 11:08 整机状态标签迁移（FormMain → MainPage.LabelStatus）
**范围**：`FormMain.cs` 删 `lbl_SystemStatus`/`sep_SystemStatus` 字段 + `InitializeSystemStatusLabel`/`OnMainDeviceStatusChanged`/`UpdateSystemStatusLabel` 三方法 + 构造调用 + `FormMain_FormClosed` 内残留退订（静态校验揪出，处理器已删会编译报错）；`MainPage.cs` 新增「整机状态标签」region（订阅 `StatusChanged` + `ApplyDeviceStatus` 颜色映射 + `_statusBlinkTimer` 0.5s 绿闪）。
**颜色映射（用户定义）**：Running=绿 / Reseting=黄 / Stop=绿闪(0.5s 绿↔白) / Alarm·EStop=红 / NoReset=灰；文本「设备状态：{状态值}」。
**wiki**：api/FormMain.md（删 3 方法行+迁移注记）、api/MainPage.md（新增整机状态标签章节+颜色表）、modules/UIDesign.md（状态栏裁剪节补迁移）、architecture/DeviceControlArchitecture.md（展示位置改 MainPage）、index/index.md（FormMain 摘要）。备份 AdaWeldSystem_backup_20260908_110152.tar.gz；真编译待 VS。

## 2026-09-08 11:20 修「停止驱动」启动误报
**现象（用户运行日志）**：程序启动 1 秒内打出「运行态已变更为 NoReset 子流程停止驱动」——启动默认态就是 NoReset、从未 Running，不存在状态变更，日志误导且不该展示。
**根因**：`SubDeviceWork` 首拍问询 `Current != Running` 即调 `StopSubDeviceDrive`，Interlocked 门首次放行必打日志，不区分「启动默认态」与「真实被抢占」。
**修复**：`SubDeviceWork` 加局部 `wasDriving`（上一拍是否真在 Running 驱动），仅真正跌出才调 `LogDriveStopped()`（原 `StopSubDeviceDrive` 删除，ResetWorkTime 内联至空闲分支每拍执行）；Interlocked 闭锁语义不变（整机一次/每次跌出）。
**wiki**：api/DeviceControlWork.md（范式代码块重写）、api/HonorMachineTest-IOReference.md（映射表）、modules/DeviceControl.md（线程问询范式条）。备份 AdaWeldSystem_backup_20260908_111508.tar.gz；真编译待 VS。

## 2026-09-08 13:22 运控总线监督虚拟 IO 化落地
**用户裁定（三点）**：①轮询放 EMGWork → 修正为 **EMGWork 专责急停，普通 Alarm 走 IOWork**；②询问 WKC 计数作用（见 api/MontionManager.md 新节：EtherCAT 报文 Working Counter 预期/实际不一致即丢帧，ESC 硬件维护、无应用层心跳下的最早掉线前兆；v1 因阈值需现场数据未纳入）；③报警动作链置整机 Alarm。
**代码（4 文件）**：L2 `MontionControl` 加 `virtual bool CheckBusOK(out faultDesc)`（默认未实现，IPVTMotion 契约范式）；L3 `DeltaMontionControl` 覆写（替换原无参版，0 调用方，逐从站读连接态+报警位）；`DeviceControlWork` 加 `IoMotionBusFault` 常量 + `ExecuteIo` case + `DoMotionBusFault()`（仅 SetStatus(Alarm)，同步执行白名单——报警不允许被 DispatchAction 忙丢弃）；`DeviceStatusWork` 加 `ScanMotionBusFault()`（IOWork 每 4 拍=200ms，电平闭锁：NG 期间 IO 常置不重复报，状态离开 Alarm 自动解闭锁，NG→OK 不自动消警，未初始化跳过）。
**静态校验**：4 文件括号平衡/C#8+ 0/符号计数逐点核对通过；真编译待 VS。
**wiki**：api/DeviceStatusWork.md（线程表+同步例外白名单+新节）、api/DeviceControlWork.md（常量表/电平型表/动作映射表 + 顺手修 C3 待决横幅为 ADR-030 已裁定）、api/MontionManager.md（总线健康检查契约+WKC 说明）、modules/DeviceControl.md（报警源虚拟 IO 化条）、index.md。备份 AdaWeldSystem_backup_20260908_131448.tar.gz。

## 2026-09-08 13:56 急停机制明确（无虚拟 IO）+ 状态颜色二次定义
**范围（用户裁定）**：①急停无虚拟 IO、只有物理 IO——`IoEmg` 常量/`ExecuteIo` case/映射表全部删除，`EstopMachine(reason)` 改为记录原因后**直通同步执行** `DoEstopMachine()`；机器人 `RxAbort` 在 `MapCommandToIo` 就地同步 `EstopMachine` 并返回 null（调用方补区分日志）。②`EMGWork` 重写为纯物理两段式：反逻辑（无电平信号=急停，按下/断线均信号消失，故障安全）；信号消失上升沿急停，**IO 上电（设备通知上位机安全）且处于 EStop 才 `EstopCancel`**——未检测到取消前 EStop 状态无法清除。③MainPage 颜色二次定义：EStop=红闪(0.5s 红↔白)/Alarm=橙/Stop=蓝不闪（闪烁通道由 Stop 迁至 EStop）。
**过程**：中途发现同消息多 Edit 并行仅末条落盘的老坑复发（DeviceControlWork/MainPage 各漏 2~4 处），逐项 Grep 核实后串行重做，复跑静态校验全过。
**wiki**：api/MainPage（颜色表二次定义）、api/DeviceControlWork（常量表/电平型表/映射表三处 IoEmg 清除）、api/DeviceStatusWork（线程表反逻辑/同步白名单直通/状态源）、architecture/DeviceControlArchitecture（thEMGWork 行+IO 映射表）、modules/UIDesign + modules/DeviceControl + index。备份 AdaWeldSystem_backup_20260908_134619.tar.gz；真编译待 VS。


## [2026-09-08 18:10:51] coding | ADR-036 线激光相机访问统一收口（Manager 持有实例 + 外设代理 + 三辅助类归并）

**触发**：编译报错 `LineLaserResultEventArgs 未包含 HasValidResult`；用户指出「对线激光对象的访问都应从 LineLaserManager 走」，实现层应对齐运控台达实现层（无实例、实例注册进 Manager）；并要求 `ProfileMatRenderer` / `ProfileSnapshot` / `SeamPvtFeeder` 不单独建文件、归并到 `LineLaserManager`。

**代码**：
- `ILineLaser/LineLaserCameraBase.cs`：新增「外设虚契约」7 个 `public virtual`（`ConnectManual` / `DisconnectManual` / `ConfigureDefaultCommPeriod` / `IsCameraOn` / `IsLaserOn` / `SetSensor` / `SetLaser`），默认实现按「不支持则告警 / 空操作 / 返回 true」给，派生类可暂不实现（对齐运控加契约法）。
- `IntelligentLaserCam/IntelligentLaserCam.cs`：类名 `IntelligentLaserCameraRun` → `IntelligentLaserCam`（与文件/目录同名），7 个外设方法加 `override`。
- `VirtualCam/VirtualCam.cs`：`override` 5 个外设契约；新增模拟节拍 `System.Threading.Timer`(33ms ≈ 30Hz)，`SensorRunContinue` 起表、`SensorStop`/`Dispose` 停表（此前每次调用只出一帧）。
- `LineLaserManager.cs`：内嵌 `ProfileSnapshot` / `ProfileMatRenderer` / `SeamPvtFeeder` 三类；新增 `IntelligentLaser` / `VirtualCamera` 类型访问器与 `Connect` / `Disconnect` / `ConfigureDefaultCommPeriod` / `IsCameraOn` / `IsLaserOn` / `SetSensor` / `SetLaser` / `ShutdownPeripherals` 八个外设代理；`Unregister` 同步清实例引用。
- 删除 `LineLaserCam/ProfileSnapshot.cs`、`ProfileMatRenderer.cs`、`SeamPvtFeeder.cs` 并撤下 .csproj 登记（现役 9 个 .cs）。
- `LineLaserWorkflow.cs`：删字段 `_ilCamera` 与 `using ...IntelligentLaserCam`；`InitializeInternal` 改走 `Manager.Connect/ConfigureDefaultCommPeriod`；`e.HasValidResult` → `e.Result.Valid`；**`DoPreWorkOn` 补 `StartAcquisition()`**（此前工作流从不启动采集，相机连上也不出图，PreWork 必然超时）；`SafeShutdownPeripherals` / 断开 / 初始化断开改走 Manager；`DisposeManaged` 不再自行 Dispose 相机（生命周期归 Manager）。
- `DeviceControlWork.cs`：`Active as VirtualCam` → `Instance.VirtualCamera`（并加 `IsVirtual` 门禁避免无谓创建）。
- `ILCamPage.cs` / `ILAlgorithmEditForm.cs`：`Active as IntelligentLaserCam` → `Instance.IntelligentLaser`。

**校验（无编译器，静态）**：8 个改动文件括号 / #region 平衡全 0 偏差；7 条虚契约 IL 全部 override、虚拟实现 5 条；残留符号 `HasValidResult` / `as IntelligentLaserCam` / `as VirtualCam` / `IntelligentLaserCameraRun` 全仓 0 命中；`Dispose(bool)` 仅出现在注释中（ADR-001 无违反）；csproj 与磁盘一致。**真编译待 Visual Studio 执行。**

**wiki**：新建 `decisions/ADR-036-LineLaserManagerSingleEntry`；`ADR-Index` 扩至 001~040；页面 `api/IntelligentLaserCameraRun.md` 改名 `api/IntelligentLaserCam.md` 并全库改链 19 页；`api/ProfileMatRenderer` / `api/SeamPvtFeeder` 的 source 指向 `LineLaserManager.cs` 并加归并横幅；更新 `api/LineLaserManager`（新增 8 个 API 行 + 约束条）、`modules/LineLaserCam`（目录树/铁律/职责/抽象契约表）、`modules/VirtualCam`（模拟节拍横幅）、`index`（ADR-036 行 + 类名备注）；`tools/drift_scan_precise.py` 的 REMOVED 登记 3 个归并文件并修正英莱现役路径。
