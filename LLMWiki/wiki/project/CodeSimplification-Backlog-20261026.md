---
title: CodeSimplification-Backlog 代码精简待完成事项台账（2026-10-26）
date: 2026-10-26
tags: [台账, 代码精简, 待办, 判据, 工具]
status: active
---

# CodeSimplification-Backlog —— 代码精简待完成事项台账

> **用途**：本轮（2026-10-26 全库治理 + 精简）之后**尚未闭合**的全部事项，按「判据来源 → 阻塞条件 → 建议批次」编排，供后续逐批偿还。
> **配套**：`standards/CodeSimplification`（标准正文 + §4.1 口径-判据映射表）· `standards/CodeSimplification-Tooling`（固定脚本 + 禁区清单）· `architecture/CodeMap` §5.7（约束台账）· `lessons/StaticVerifierJudgements` §9.9~§9.15（失效模式实录）。

## 一、闭合状态总览

| 维度 | 本轮前 | 当前 | 判据 |
|---|---|---|---|
| 扫描器 warn 总数 | 1,256 | **0** | `csharp_review.py` |
| 扫描器 error | — | **0** | 同上 |
| 结构守卫 | — | **PASS**（154 文件 0 fail；含 namespace 级结构 / region 配对） | `simplify_guard.py` |
| 口径-判据一致性 | 无机制 | **8/8 一致**（四重自证 PASS） | `simplify_selfcheck.py` |
| 真编译 | 无编译器（旧前提） | **errors=0**（MSBuild /t:Rebuild） | `simplify_run.py` |
| ① 成员顺序（**region 内口径**） | 133 处 | **0 处 / 0 文件** | `A.文件整理 / 成员顺序错误` |
| ② 注释质量（XML 规范） | 1,145 处 | **0 warn**（294 info 存量不追溯） | `A.注释规范` warn |
| ③ 枚举事件去重 | 0 | **0** | `A.文件整理` |
| ④ 逻辑去冗余（9 类） | 12 处 | **0** | `B.过度等待` 等 |
| ⑤ 辅助函数归集 | 18 处 | **0 warn**（3 处同名重载已登记豁免） | `C.功能重叠` |
| ⑥ 多层锁检测（2026-10-27 新增） | 未覆盖 | **0 处** | `B.多层锁` |

## 二、待完成事项（按处置难度排序）

### B-1 ① 成员顺序 0 处 / 0 文件 —— 已清零（2026-10-29）

**判据（2026-10-26 修订）**：`A.文件整理 / 成员顺序错误`，范围 = **每个 `#region` 段内；跨 region 不比较**。
**清偿轨迹**：全局口径 93 处 → 安全批次 83 → 口径修订 26 → 自动 + 定点批次 **0 处 / 0 文件**。

**本轮定点批次（5 文件，全部编译通过）**：
| 文件 | 前 → 后 | 方式 |
|---|---|---|
| `PCLOperate/Render/SurfaceTriangulator.cs` | 4 → 0 | `--fix-victims` |
| `ProductFileControl/ProductFileRecordManager.cs` | 2 → 0 | `--fix-victims` + 手工确认 |
| `UIDesign/ControlPage/DataReviewerPage.cs` | 2 → 0 | 手工搬移公共字段 / `--fix-victims` |
| `Comm/Communication/CommunicationManager.cs` | 1 → 0 | 手工搬移锁/常量 |
| `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` | 4 → 0 | `--fix-victims` |

**判据修正（避免假违规/假阳性，2026-10-29）**：
1. `csharp_review.parse_file` 现在会**收录嵌套类型**；外层类不再把嵌套类方法算作自身成员
2. 析构函数 `~ClassName()` 不再被当成构造函数（不参与成员顺序）
3. 字段只认**类体深度 0**；方法内局部变量（如 `for (int i...)`）不再被误判为字段
4. `simplify_apply_member_order.py --fix-victims`：只把违规成员段搬到本 region **最早**的更高层级成员之前；适用于 overlap / 堆叠注释 / 嵌套类型文件

**复现/复核**：`python scripts/simplify_apply_member_order.py --report` → `violations=0 files=0`。
**剩余**：无真实成员顺序欠账；`C.功能重叠` 3 处仍为有意保留（B-2）。

### B-2 ⑤ 功能重叠 3 处 —— 已登记为「有意保留」（2026-10-29）

| 位置 | 相似度 | 保留理由 |
|---|---|---|
| `FileOperate/XdocumentReaderWriter.GetXmlStrValue` | 83% | 3 参取**属性**值 / 2 参取**元素**值，语义不同；仅前 2 行「载入 XML」重复 |
| `SQLiteDBControl/SQLiteCore/SQLiteDataBase.CreateTable` | 90% | 两版**列长**与 `IsExistTable` 守卫不同（3 参版无守卫） |
| `ProductFileControl/ProductFileRecordManager.AddFrame` | 75% | 两版各 1 行，已是薄包装（转发 `_contourRecord.AddPointCloud`） |

**已登记豁免**：3 处均为**同名重载**，`csharp_review._check_overlapping_methods` 已增加「同名重载不参与功能重叠判定」；扫描器 `C.功能重叠` warn 归零，不再每轮重复报警。

### B-3 info 级 1,508 项（warn 0） —— 按标准多为「按需处理」，不设清零目标

| 类别 | 量（2026-10-29 实测） | 性质 | 建议 |
|---|---|---|---|
| `B.过度属性` | 984 | 属性 get 含逻辑 / public set 可改只读 | **抽样**处理（多数为 DTO 载体与有意设计，逐一改风险高） |
| `C.疑似死函数` | 111 | 108 条 LIVE 假阳性（Designer/委托）+ 1 条待接线（`UpdateParamValues`）+ Main | ⛔ **只报不删**；真死 16 个已在批次 A 删除；⚠️ 2026-11-02 起原第 2 条待接线 `SeamWidthShowRange` 已废弃并删除 |
| `C.嵌套内联` | 35 | private 单调用表达式短函数 | ✅ 2026-10-29 判据收紧 **96→58**，四轮内联 **24** 条；语法简化后复测 **35**（新增 `FileEditorForm.ClearXmlAllInfo` 已登记保留）；余 35 条已逐条裁定保留（见 B-6） |
| `B.无意义Null检查` | 21 | 冗余 null 判断 | 真冗余 2 个已在批次 C 删除；余 21 条为边界/防御性，保留 |
| `B.过度等待/延迟` | 19 | 周期轮询 `Thread.Sleep` | ✅ 已按标准 §四「有意例外」降为 info，**无需处理** |
| `B.多层锁` | **0** | 嵌套锁 / 锁顺序反转 / 锁字符串 / 锁局部对象 | ✅ 2026-10-27 新增判据；实测无命中 |
| `B.无意义锁` | 13 info | lock 内含 IO | 均为串行化写入（日志/SQLite/INI），**有意保留**；1 处锁字段非 readonly 已修（Log.m_lock） |
| `B.临时变量滥用` | 11 | 单次使用的局部变量 | 与标准②「单次使用的局部变量保留」口径冲突 ⇒ **判据应收窄** |
| `B.过度资源管理` | 3 | using 嵌套 4~6 层 | 逐个拆分（低风险） |
| `B.冗余赋值传递` | 3 | 近义参数改名 | 逐条确认后改 |
| `A.注释规范` | 294 info | public 缺 `///` | ✅ M1 存量不追溯；**51 warn 已于 2026-10-29 由 `simplify_apply_docs.py` 清零**（trim 30 / param 16 / returns 6） |
| `系统` | 5 | 文件内无 class 定义（类型在别处） | 登记为「按设计如此」 |
| `C.功能重叠` | **0** | 语义不同的相似函数 | ✅ 3 处同名重载已登记豁免（B-2），判据不再报警 |
| `D.语法简化（IDE 五则）` | **0** | IDE0017/0018/0019/0031/0059 | ✅ 2026-10-29 新增第 5 关门禁并批改 **216→0**，2026-10-30 增补 IDE0059 **9→0**（合计 **225**，B-7）；判据 = `dotnet format --verify-no-changes` |
| `A.字体规范` | **0** | `new Font("族名", …)` 非 `Microsoft YaHei UI` | ✅ 2026-10-30 统一 **564→0**（23 文件，B-8）；判据 = `csharp_review.check_font_family`（含 Designer.cs） |

> **三类剩余项归属分析与执行（2026-10-29）**：死函数 121 → **111**（已删 **16** = 13 名单 + 3 级联；余 108 LIVE + 2 待接线 + Main）；内联 95 → **35**（判据收紧为「1 个调用表达式」：96→58，四轮内联 **24** 条；原 33 中 15 条实为多调用点，保留）；Null 23 → **21**（已删 2 冗余，余 21 边界/防御性）。完整判定与证据见工作区根 `精简剩余项分析-20261029.md`。
>
> **⚠️ 现状更新（2026-11-02）**：上段 2 条待接线中，`DataReviewerPage.SeamWidthShowRange` **已废弃并删除** ⇒ 现为 **1 条待接线**（`AutoParamForm.UpdateParamValues`）。连带 `DataReviewerPage.HasEnoughSeamWidthPoints` 原为 0 引用，业主**已裁定一并删除**（随「按 X 范围显示区域」模块整体移除，见 [[lessons/UiModuleRemovalCleanup]]）⇒ **已删除（2026-11-02，随模块整体移除）**。上段其余计数均为 2026-10-29 历史快照，不因本次变更改写。

### B-5 批次 A+C 执行结果（2026-10-29）

| 批次 | 动作 | 结果 |
|---|---|---|
| A | 删除真死 **16** 个 | 13 名单 + 级联 `FileEditorForm.FindTreeNode` / `LoadXdocument` / `AddNodesRecursively` |
| C | 删除冗余 Null **2** 个 | `LineLaserWorkflow.RunStepAction`、`RecordFileStore.AddRecord` |
| 保留 | 1 个待接线业务逻辑 | `AutoParamForm.UpdateParamValues`（原事件包装已删，逻辑保留） |
| 废弃 | `DataReviewerPage.SeamWidthShowRange` | **已废弃并删除（2026-11-02）** —— 原列于「2 个待接线业务逻辑」，随 B-5 保留项一并移除；连带 `DataReviewerPage.HasEnoughSeamWidthPoints` 的唯一调用方消失 ⇒ 业主**已裁定一并删除**，**已删除（2026-11-02，随「按 X 范围显示区域」模块整体移除）**（判据见 [[lessons/UiModuleRemovalCleanup]]） |
| 验证 | guard / 扫描器 / 自检 / 真编译 | PASS · errors=0 / warns=0 · PASS · errors=0 |

### B-6 内联四轮执行结果（2026-10-29）

| 轮次 | 范围 | 数量 | 结果 |
|---|---|---|---|
| 判据 | `_check_inline_candidates` 改为按**调用表达式**计数 | 96→58 | 排除原 33 中 15 条多调用点格式化器（`Text`(19)/`CsvDouble`(13)/`WeldHeadText`(13) 等） |
| 第 1 轮 | 格式化/转换/单转发 | **7** | `LineLaserConfig.Text` / `MotorCountToMm` / `ToDeviation` / `EffectiveSwingGain` / `Clamp` / `DeobfuscateBytes` / `ClearTableData` |
| 第 2 轮 | UI 单调用点包装 | **7** | `MonitorCamPage` 5 个（订阅/退订/计时器/录像区）+ `SystemControlPage.MakeBtn` / `LoadAll` |
| 第 3 轮 | 无线语义的薄封装（无分支/无锁外语义） | **6** | `KukaRsiComm.GetAttr` / `DatabaseHelperBase.InitializeDatabase` / `DataReviewerPage.PageBangdingIni` / `ILAlgoForm.JobButton_Click` / `MonitorCamManager.MarkHealthy` / `HelixRenderForm.CreatCamereDir` |
| 第 4 轮 | 刷新/复位动作封装 | **4** | `ProductDatabaseHelper.InitializeTodayTable` / `ProcessControlPage.RefreshParam` / `MainPage.ResetWeldFlow` / `SystemControlPage.RefreshMotorStatus` |
| 保留 | 5 个 `Log` 包装 | 5 | Tag 载体（原 rules/KR-011（已并入 lessons/StaticVerifier-Wiring-Integrity）），不内联 |
| 剩余 | 34 条 | 34 | 已逐条裁定保留，见下方分类 |

**剩余 34 条保留分类**（判据：含分支/锁/事件/解析/领域语义，或内联后引入重复长表达式）：

| 类别 | 条数 | 代表 | 保留依据 |
|---|---|---|---|
| `Log` 包装（Tag 载体） | 6 | `LineLaserManager` / `AxisRegistry` / `CylinderRegistry` / `IORegistry` / `SeamTrackingAlgorithm` / `WeldParamLookupAlgorithm` | 原 rules/KR-011（已并入 lessons/StaticVerifier-Wiring-Integrity） 横切载体，非纯转发 |
| 快捷区指令分发 | 10 | `DoTaAuto`…`DoLaPose2` | 内联后 10 处重复全限定名 `AdaWeldSystem.MainDeviceControl.DeviceWorkflow.LaserWeldHeadWorkflow.Instance`，且名称=指令映射概念 |
| 解析/校验 | 5 | `GetElementBool` / `ReadDouble` / `ParseStep` / `ParseTarget` / `LoadLaserCalibOnForm` | 含区域性/默认值/失败告警，表达独立概念 |
| 卫语句/前置判断 | 4 | `GetTaAxisQuiet` / `LogDriveStopped` / `DoPreWorkWaitWork` / `ClearHoverTip` | 内联会把守卫散到调用方，降低可读性 |
| 流程步骤/状态机 | 5 | `DoStopping` / `ProcessRsiPose` / `HandleEmptyFrame` / `ClearFault` / `AddPoint` | 步骤语义与 `SetFault` 对称；`AddPoint` 含滑窗容量逻辑 |
| 初始化序列 / 几何工具 | 3 | `AfterInitializeUI` / `SubscribeLineLaserEvents` / `ProjectToPlane` | 初始化顺序、事件去重订阅、几何运算 |
| 事件抛出 | 1 | `RaiseAbortRecord` | 标准 `handler != null` 事件模式 |

| 验证 | guard / 扫描器 / 自检 / 真编译 | — | PASS · errors=0 / warns=0 · PASS · errors=0 |

### B-7 语法简化五则执行结果（2026-10-29 → 2026-10-30）

| 项 | 内容 |
|---|---|
| 来源 | 业主指令：`IDE0017` 初始化器简化 / `IDE0018` 内联变量声明 / `IDE0031` null 检查简化 / `IDE0019` 模式匹配；**2026-10-30 追加 `IDE0059` 不必要赋值** |
| 判据 | 标准 §二④「语法简化五则」+ 映射表行 **10**；判据 = 官方 `dotnet format style --verify-no-changes --diagnostics IDE0017/0018/0019/0031/0059 --severity info`（0 诊断 = 通过） |
| 批改 | 官方 Roslyn 修复器 `dotnet format style <csproj> --diagnostics … --severity info --no-restore` |
| 结果 | **225 条 → 0**：IDE0017 **75** / IDE0018 **93** / IDE0019 **9** / IDE0031 **39** / IDE0059 **9**；语法简化共 **78** 文件（2026-10-29 72 + 2026-10-30 6） |
| IDE0059 明细 | `out var num`×2（`SystemControlPage` 表格校验）、`out string payload`（`MainPage`）→ `out _`；`Mat copy = null`（`MonitorCamManager`）、`List<IlJobParamInfo> jobParams = null`（`ILParamForm`）删初值；`double pattern = 0`（`WeldHeadSlaveDevice`）改首个 `out double pattern`；`TemplateMatch` 三个初值删除（`ImageAlgorithm`）；另人工删 `ReadScaledWithIndex` 的 `value = 0;`（三元两分支均以 `out` 赋值；同库 10 处同类初值为早退路径所必需，保留） |
| 典型收益 | 线程创建 5 处转初始化器；`out` 局部声明 93 处内联；`if (x != null) x.M()` 39 处转 `x?.M()`；`as`+判空 9 处转 `is T x`；9 处无用赋值/弃元 |
| 门禁 | `simplify_run.py` 第 **5** 关（`--skip-ide` 可跳过，无 SDK 自动 SKIP）；`simplify_selfcheck.py` 校验「五则 ↔ 门禁」一致性 |
| 坑 | ① 原 LF 文件被修复器写成混行尾（2026-10-29 共 10 文件 `eol-mixed`）→ 按原行尾整文件归一后复跑；② 多语句单行需手工拆行；③ **IDE0059 对非字面量初值会退化为 `_ = new Point(...)` 死语句**，须人工删除 |
| 验证 | guard 154 PASS · 扫描器 errors=0 / warns=0 · selfcheck PASS · MSBuild errors=0 · IDE 门禁 remaining=0 |
| C# 7.3 | 五处修复产物均为 C# 6/7 语法（`?.`、`out var` / `out _`、`is T x`、初始化器），未引入 C# 8+（ADR-001 合规） |

### B-8 显示字体统一（2026-10-30）

| 项 | 内容 |
|---|---|
| 来源 | 业主指令「做显示字体检查：Microsoft YaHei UI 为项目默认字体」 |
| 判据 | `csharp_review.check_font_family` → `A.字体规范`（warn；**Designer.cs 只扫此项**）；`simplify_selfcheck` **C3** 自证（非默认必报、默认不报） |
| 范围 | 全库 `new Font("族名", …)`：`宋体` **548** / `微软雅黑` **15** / `Microsoft YaHei` **1** = **564**（23 文件；其中 3 处在非 UI 的 GDI 绘图） |
| 处置 | 字节级替换为 `Microsoft YaHei UI`，字号/样式/BOM/行尾全部保留；Designer.cs 一并替换 |
| 非 UI 3 处 | `ImageRoiTools`（ROI 标注文字）、`LineLaserContourAlgorithm` 2 处（轮廓画布刻度/标签）一并统一 |
| 结果 | `A.字体规范` **564 → 0** |
| 验证 | guard 154 PASS · 扫描器 errors=0 / warns=0 · selfcheck PASS（含 C3） · MSBuild errors=0 · IDE remaining=0 |

### B-4 现场验证

| 事项 | 说明 |
|---|---|
| **真编译** | ✅ 本机 MSBuild 可用（VS18 Insiders）；`simplify_run.py` 已执行 `/t:Rebuild`，**errors=0**。静态校验仍是第一道关，但每批必须再过真编译 |
| **配置核对** | 本轮无配置项新增/改名/改默认值 ⇒ 现场无需人工核对 XML |
| **回退基准** | `tools/backup_adaweld.py --output` 每次生成定稿现场包；本轮出包 `AdaWeldSystem_output_20261026_175231.tar.gz` |

## 三、脚本使用速查

| 场景 | 命令 |
|---|---|
| 每轮收尾总巡检 | `python scripts/simplify_run.py` |
| 改码前后结构守卫 | `python scripts/simplify_guard.py`（带 `--baseline <快照目录>` 可比对成员集合/行尾） |
| 成员顺序重排 | `python scripts/simplify_apply_member_order.py --all`（先 `--dry-run` 看跳过原因） |
| 成员顺序剩余清单 | `python scripts/simplify_apply_member_order.py --report`（文件/类/成员/行/region） |
| 批次间真编译快验 | `python scripts/simplify_run.py --build-only` |
| 注释补全/压缩 | `python scripts/simplify_apply_docs.py --all` |
| 改标准/改判据后 | `python scripts/simplify_selfcheck.py` |
| 单文件扫描 | `python scripts/csharp_review.py <file.cs> --json` |

**解释器**：`D:\ProgramData\miniconda3\envs\myenv\python.exe`（PATH 上的 `python` 是 0 字节 Store 占位符，不可用）。
**批改纪律（四关）**：先 `--dry-run` → 落盘（候选守卫 + 写后守卫）→ `simplify_run.py --build-only` 真编译 0 错误 → `simplify_guard.py --baseline` 全绿；任关失败用脚本自带的 `_simplify_snapshot/` 回退。详见 [[standards/CodeSimplification-Tooling]]。

## 三之二、B-8 存量三类逐项定性（业主裁定：判据治理 + 台账定性）

> 业主口径：不按字面「补齐/内联/改写」，而是逐一审查后区分「判据过报」「存量欠账」「有意保留」，
> 清理对象是**判据噪声与台账**，不是业务代码。

### B-8.1 过度属性

| 阶段 | 条数 | 定性 |
|---|---|---|
| 旧判据 | 1184 | `len(body_text) > 20` 把所有带 body 的 getter 判成「含逻辑」；`public set` 无跨文件消费分析能力也一律上报 ⇒ 几乎全为噪声 |
| 一次收紧 | 99 | 只认循环 / `try` / IO / 日志 / 有效行 > 5 |
| 二次收紧 | 19 | 豁免 `lock` 快照读取（跨线程共享字段强制范式）与 `new` 返回集合副本（不返回内部可变引用） |
| 剩余 19 条 | 19 | **逐条审查全部定性为有意保留**：`Stages.Operation` / `ApproximationMethod` 为属性变更通知 setter；`MontionManager.TaMotionReady` / `TaDegradedReason` / `YGateReason` / `LaGateReason` 为规范推荐的判断辅助只读属性；`WeldParamManager.LastSeamPointY/Z` / `CurrentLaserJobId` 为 try/catch 兜底跨 Manager 快照；`TaLaCurveConfig.AnchorSpotMm` / `DataReviewerPage.PointCount` / `AutoParamHelper.HasAnyValue` 为无副作用聚合计算；`Stages` 系列为 setter 联动；`MonitorCamManager.RecordDirectory` / `MonitorCameraWorkflow.LastResult` / `InLaserModbusComm.IsConnected` 为带校验或兜底的只读属性 |

⛔ 不改代码：改属性为方法会动公共 API；这些写法均符合规范 §一④-6 的「只读 / 无外部副作用」意图。

### B-8.2 注释规范存量欠账

| 项 | 结论 |
|---|---|
| 645 条 info | 顶层裁定 3 明确「public 新增/改动必写，存量欠账不追溯、不设全库清零目标」；判据自身已标注「存量欠账不追溯」 |
| 处置 | 默认不进清单（`csharp_review.py` 的 `INCLUDE_LEGACY`），`--verbose` 可查全量，按文件夹渐进偿还 |
| ⛔ 不做 | 全量补 `///` 会净增约 645 行注释，与「注释精简 / 单条 ≤20 汉字」方向直接冲突 |

### B-8.3 嵌套内联

| 项 | 结论 |
|---|---|
| 49 条 | 台账 B-6 已对 34 条逐条给出 7 类保留理由；本轮复核剩余 15 条同属这些类别 |
| 分类 | Log 包装(Tag 载体) · 快捷区指令分发 `DoTa*`/`DoLa*` · 解析校验 `Parse*`/`Read*`/`Normalize*`/`ToHome*` · 卫语句 `Wait*`/`Handle*` · 流程步骤/状态机 `DoStopping`/`ProcessRsiPose`/`ClearFault`/`AddPoint` · 初始化与几何 `After*`/`Subscribe*`/`Project*` · 事件抛出 `Raise*` |
| 处置 | 判据按语义前缀豁免（`inline_keep_prefixes`），新出现的纯薄转发仍会被检出 |

⛔ 不做批量内联：内联会把守卫与语义散到调用方，且 `DoTa*` 内联会产生 10 处重复的冗长全限定名。

## 四、相关页面

- [[standards/CodeSimplification]] —— 标准正文（唯一标准源）
- [[standards/CodeSimplification-Tooling]] —— 固定工具集 + 禁区清单
- [[project/CodeSimplification-Progress-20260826]] —— 上一轮进度快照（历史）
- [[architecture/CodeMap]] §5.7 —— 约束台账
