## [2026-11-17 21:01:58] fix | 工具与全量资产纳入 git 管控（Vicoding 4 提交 + AdaWeldSystem 2 提交，双仓库未跟踪清零）
- 来源：业主指令「工具纳入管控」；实际排查发现范围远超工具：Vicoding 仓库 209 项未跟踪（含 167 wiki 页 / 22 工具 / 7 脚本 / 8 raw / 4 logs），AdaWeldSystem 仓库 41 项未跟踪 + 143 项已修改未提交 —— 本轮两轮的核心代码改动（ProcessControlPage/SystemControlPage/MontionManager 等）全部不在版本控制内
- 操作：
  1. 提交前验证：csproj Compile 声明 193 项与磁盘 .cs 193 项完全一致（反斜杠路径导致的假阳性已排除）；真编译 Rebuild errors=0 rc=0；bin/obj/3rdDepend 未误纳入
- 变更文件：Vicoding管理平台/LLMWiki/tools/（29 个新跟踪）; Vicoding管理平台/LLMWiki/scripts/（7 个新跟踪）; Vicoding管理平台/LLMWiki/wiki/（313 文件变更）; Vicoding管理平台/LLMWiki/raw/（118 文件）; Vicoding管理平台/LLMWiki/logs/（23 文件）; Vicoding管理平台/.gitignore; Vicoding管理平台/LLMWiki/AGENTS.md; Vicoding管理平台/LLMWiki/skills/vibecoding-llmwiki/SKILL.md; AdaWeldSystem/（208 文件变更）; AdaWeldSystem/.gitignore
- 结论 / 遗留：终态：双仓库未跟踪 0 / 未提交 0；Vicoding 仓库 93MB，AdaWeldSystem 仓库 7.2MB。门禁复跑全绿：八闸门 exit=0（死链 0 / 孤儿 0 / ADR 冲突 0 / 外部链接失效 0 / 编号空洞 0，7 个废止留档号单列）；simplify_guard 168 文件 fail=0；simplify_selfcheck PASS。教训沉淀：① 判「删除是否丢内容」不能用逐字比对（承接是改写浓缩，逐字必假阴性）——须用 merged_from 关联 + 特征句检索 + 核心判据逐条落地三重证据；② 页面改名/拆分类重构的特征名会变（类名不同），判据须回落到「控件/成员是否保留」；③ .gitignore 须覆盖 output 定稿包（每轮 Phase 3 重新生成，不应入库）。遗留：① 本轮未做 git push（两仓库均在 main，本地已完整入库，推送与否待业主定）；② 仓库无 LFS，raw/delta 两份台达 PDF 共 17.2MB 直接入 blob，若后续 raw 资产继续增长需评估 LFS；③ 工作区根仍有 3 个 output 包（仓库外，未污染版本控制）

## [2026-11-17 18:49:07] fix | 治理工具常态化：新增 tools/adr_merge.py（整页合并助手 plan/apply/audit）+ WikiPageFormatSpec §3.1.3 合并路径契约 + lessons 两坑沉淀
- 来源：承接 ADR 治理轮：把一次性合并脚本沉淀为常态化工具，并把合并契约与两条新坑写入规范/教训页
- 操作：
  1. lessons/StaticVerifier-Batch-Script-Traps §四之十四 增两坑：坑⑦ 治理脚本写死绝对路径致「副本试跑」实际改了源目录（含 md5 前后比对断言与只读解锁要求）；坑⑧ 治理脚本非幂等致二次执行累积污染（表格行分隔符累积 / 空 blocks 仍插入 / 段落起点漂移三类根因）
- 变更文件：Vicoding管理平台/LLMWiki/tools/adr_merge.py; Vicoding管理平台/LLMWiki/wiki/standards/WikiPageFormatSpec.md; Vicoding管理平台/LLMWiki/wiki/lessons/StaticVerifier-Batch-Script-Traps.md
- 结论 / 遗留：工具验证（副本目录，源目录 md5 前后一致 = 零误改）：plan 零写盘 ✓ · apply 真实合并 99 页 + 三类残留引用 0 + 指针留档 1 行 ✓ · 幂等二次执行 0 变化 ✓ · wiki_format/wiki_audit/lint_scan/rules_check 四闸门 exit=0 ✓（wiki_format 唯一违规为 log 51 条超限，已 truncate 归档 1 条至 logs/backup/log_2026-11-10.md）。终态：八闸门全绿、死链 0、孤儿 0、ADR 编号冲突 0、外部链接失效 0、编号空洞 0（7 个废止留档号单列）、ADR 有效页 100。

## [2026-11-17 18:45:46] fix | ADR 库治理轮：相似度闸门止血 + 碎片合并 7 页 + 废弃清理 + 索引按主题族重排 + 引用与旧判据清零
- 来源：业主指令四项：① 加相似度阈值止血 ② 修 merge 截断 ③ 合并碎片重复、删除废弃 ④ index 处重新排序并检查 ADR 引用、不允许残留旧 ADR 判据（前置：2026-11-17 18:05 全库审计结论 = 无真重复，真问题是碎片化 + 合并机制形同虚设）
- 操作：
  1. 旧判据清零：全库指向已删页的 wikilink/裸号/相对路径链接均归零（此前 3 处相对路径链接漏改，已修正）；代码侧 DeltaAxisConfig.cs 的 ADR-090 注释改指 ADR-088；wiki_audit 的 ADR 判据修正（编号空洞须排除废止留档号；登记检查应查 ADR-Index 而非 index.md）
- 变更文件：Vicoding管理平台/LLMWiki/tools/adr_new.py; Vicoding管理平台/LLMWiki/tools/wiki_audit.py; Vicoding管理平台/LLMWiki/tools/wiki_index_build.py; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-Index.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-033-ConfigArchitectureStandard.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-075-LaserHeadUiControlConsistency.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-082-TaInitFourStepAndAvailability.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-084-TaForceToTorqueConversion.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-088-TaSharedTorqueLimit.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-097-algorithm-layer-ownership-single-entry.md; Vicoding管理平台/LLMWiki/wiki/standards/WikiPageFormatSpec.md; Vicoding管理平台/LLMWiki/wiki/lessons/StaticVerifier-Batch-Script-Traps.md; Vicoding管理平台/LLMWiki/wiki/architecture/CodeMap.md; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs
- 结论 / 遗留：门禁：八闸门全绿（wiki_audit/lint_scan/drift_scan_precise/ingest_purity_scan/wiki_format/rules_check/skill_pointer_check/raw_asset_check 均 exit=0）；死链 0、孤儿 0、ADR 编号冲突 0、编号空洞 0（7 个废止留档号单列）；ADR 重复自检 100 页 4950 页对仅 1 对 ≥0.40（ADR-106↔107 共现仅 2 个文件名，实为不同子问题，提示级）。治理脚本阴性对照 4/4 通过（注入对照命中 ADR-088 J=0.857 拒绝 rc=2 + 全新主题放行 + 只读命令零副作用 + 决策号无 DD 前缀）。教训沉淀 2 条新坑（脚本写死绝对路径致副本试跑反改源目录 / 治理脚本非幂等致二次执行累积污染）。遗留：① 本轮只合并有明确自述取代关系的 7 组，其余同族页（如配置/键管理 11 页、状态机 9 页）落地实体不重叠，属主题相邻而非重复，未合；② ADR-089 指针行主题里保留了原页的删除线表述，后续可在标题列加「原页已删」以免与「已废弃」连读歧义；③ 合并执行脚本为一次性工具，落地后应把「承接 + 引用改写 + 索引重排」固化进 wiki_index_build 或新建 adr_merge.py 常态化入口

## [2026-11-17 18:23:19] fix | 焊接头节点号固定第三站 NodeId=2 + 节点号撞号校验 + UI 编辑入口
- 来源：现场日志 20261117_智能填丝焊接系统日志.log
- 操作：
  1. Phase0 检索 CodeMap/index/ADR-030/lessons
  2. Phase1 计划
  3. Phase2 改码 5 文件
  4. Phase2.6 静态校验 24 项通过 + 真编译 errors=0 rc=0
  5. Phase3 Ingest
- 变更文件：AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs, AdaWeldSystem/MotionControl/MontionManager.cs, AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMontionControl.cs, AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs, AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs, AdaWeldSystem/bin/Debug/Config/MotionControl/Motion_XML/DeltaMotionConfig.xml
- 结论 / 遗留：根因: 焊接头 NODE_ID=0 与 Y 轴 NODE_ID=0 撞号, 握手 SDO 打到 Y 轴伺服读 0x2004 得 abort 0x1302; 教学页 lessons/NodeAddressCollision; ADR-030 演进记录 D030

## [2026-11-17 17:51:13] fix | 自动焊接禁 UI 手动操作 · TA_Zero 同口径要求已回零 · 指令区选中态与结果色一致 · 按钮禁用按电机分组
- 来源：业主现场反馈四项：① 焊接过程中设置界面手动操作都不允许（UI 动作一律手动模式，自动焊接中不可执行）② TA_Zero 与其它指令一样也须回零才能执行 ③ TA 指令区 radio 确认后选中态就变了，出现「TA_Zero 被选中、TA_Auto 是红色」的自相矛盾状态 ④ 按回零导致其它电机按钮也不可用（应各管各的）
- 操作：
  1. DeviceControlWork：新增 IsAutoWeldingRunning（线激光焊接过程态 ∈ PreWork/Working/Stopping）作手动动作唯一禁入判据；⛔ 不复用 IsWelding（覆盖整段开机期、过宽会连正常调试一起禁掉）
  2. MotionControlWorkflow：新增 AxisRejectAutoWelding；TryManualAxisOperation/TryMoveAxisToTarget/TryHomeAxisWithWait/TaExecute 增自动焊接禁入门禁（⛔ Stop/JogStop 永远放行）；ExecuteTaZeroPose 前置改 CheckTaAvailable（TA_Zero 同口径要求已回零）；删 CheckTaMotionReady 与「未回零只告警」块；GetTaGateReason 的 allowZeroPose 不再放宽
  3. LaserWeldHeadWorkflow：新增 EnsureManualWeldHeadActionAllowed 统一门禁，LaAuto/LaSpot1/LaSpot2/LaPose1/LaPose2/GalvoHome/GalvoDemo 全部接入；GalvoDemo 原用过宽的 IsWelding 判定一并改用该门禁
  4. ProcessControlPage：RunInstruction 链路改为「确认→门禁→单飞→执行→上色」（执行必须等用户点确定才生效）；门禁/单飞被拒保持当前选中态并标红 + 清同组旧底色；取消确认回退选中并复位自己底色；自动 TA_ZeroPose 不再抢用户选中态、不占指令区结果色；底色复位按容器作用域泛化到 Y/TA/LA/GA 四组；TA 门禁统一用 TaAvailable（含 TA_Zero）
  5. SystemControlPage：全局忙标志拆为 ManualOpGroup 四组独立标志（Trace/Ta/La/Galvo），一个电机的操作只禁用自己那组按钮；自动焊接中禁手动（_manualActionAllowed 由焊接状态事件驱动，⛔ 构造期不读 DeviceControlWork 单例避免触发主控初始化）
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs
- 结论 / 遗留：真编译 Rebuild errors=0 rc=0 + simplify_guard 168 文件 fail=0。沉淀：按先合并后新建未新建 ADR —— ADR-100/082/063/075 各追加 2026-11-17 演进记录（D29~D32）；api/DeviceControlWork·MotionControlWorkflow·LaserWeldHeadWorkflow·SystemControlPage·ProcessControlPage 各追加改版段；lessons/TorqueModeAsUiGate（选中态与结果色必须是同一控件）与 UiRefreshUnifiedEntry（按钮管控作用域按设备隔离）各合并一条新坑；CodeMap 卡3/卡6 与 CodeMap-Files 同步；index 重建 165 条无重复。遗留：① 手动动作禁入的判据取焊接过程态 PreWork/Working/Stopping，是否还需把焊前准备段（对齐/光丝对中）纳入待业主确认；② 振镜按钮焊接中禁切换改由整机焊接状态事件驱动，焊接起止沿须现场验证；③ TA_Zero 现要求已回零 ⇒ 初始化后必须先回零才能用 TA 指令（含 TA_Zero），首台现场须确认操作顺序

## [2026-11-17 17:30:48] lint | Phase 4 健康检查与知识库卫生（刷新与手动操作链路重构轮 收尾）
- 来源：Phase 4 Lint 八闸门 + 人工矛盾扫描 + 卫生巡检
- 操作：
  1. 矛盾扫描修正两处现行描述旧门禁语义：standards/DeviceInitializationDependency §七 与 api/MontionManager 回零结论行（ADR 决策原文不改，改版只在演进记录）
  2. log 卫生：修正一条历史条目格式（修复 … | --src → fix | …）+ 按 wiki_log.py truncate 归档 2 条至 logs/backup/log_2026-11-10.md（保留最新 50 条，归档非丢弃）
  3. index 重建（165 条无重复，project 8 页归属完整）
- 变更文件：Vicoding管理平台/LLMWiki/wiki/standards/DeviceInitializationDependency.md; Vicoding管理平台/LLMWiki/wiki/api/MontionManager.md; Vicoding管理平台/LLMWiki/logs/log.md; Vicoding管理平台/LLMWiki/logs/backup/log_2026-11-10.md; Vicoding管理平台/LLMWiki/logs/INDEX.md
- 结论 / 遗留：最终真编译 Rebuild errors=0 rc=0 + simplify_guard 168 文件 fail=0 + simplify_selfcheck PASS（注入对照与零变化一致性均通过，守卫非空过）。定稿 output 包 = AdaWeldSystem_output_20261117_173041.tar.gz（3.1 MB）。遗留同上一条：① AntdUI Table 差分重绘须上机实测；② 振镜按钮焊接中禁切换改事件驱动须现场验证；③ TA 绝对定位以「已回零」为位置可信依据须首次上机实测定位基准

## [2026-11-17 17:26:56] fix | 系统设置/工艺设置页刷新与手动操作链路重构（轴按钮卡顿与重复生效 · TA 指令区状态逻辑 · 去跨线程刷新）
- 来源：业主需求 1 轴运动按钮卡顿与重复生效 / 2 TA 指令区状态逻辑（TA未回零 + 点一下多一个红）/ 3 取消 UI 线程刷新、轴操作防呆、确认后执行 + 执行消息通知；补充约束：两页各自建立定时器不共用
- 操作：
  1. MontionManager：TaAvailable 改为「已使能+已回零」，拆出 TaAtWorkZero/TaZeroPoseReason 观测位；新增 MoveToNoBlock/StepMoveNoBlock；删除 HomeAxis 与 AxisManualOperation.Home
  2. MotionControlWorkflow：TryManualAxisOperation 的 MoveTo/StepMove 改非阻塞、移除 Home 分支；GetTaGateReason 附工作零位未到位观测
  3. LaserWeldHeadWorkflow：IsAtWorkZero 改读 TaAtWorkZero（L4 与指令可执行解耦）
  4. SystemControlPage：新增手动操作执行器（按钮禁用=执行中 → 后台执行 → 执行消息回 UI）；刷新去跨线程采集回贴、差分才重绑、按钮管控改事件驱动；停止键去重（只下发一次）
  5. ProcessControlPage：删除门禁快照（ActionGateSnapshot/_gateSnapshot/_actionDirty/_gateBusy），门禁改点击时直读权威源；TA 区互斥单色（最多一个有色）；本页 timerRefresh 移入 Designer 托管（页内唯一实例）
- 变更文件：AdaWeldSystem/MotionControl/MontionManager.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.Designer.cs
- 结论 / 遗留：真编译 Rebuild errors=0 rc=0（VS18 Insiders 工具链）+ simplify_guard 168 文件 fail=0 + simplify_selfcheck PASS（含注入对照与零变化一致性）。沉淀：ADR-063/073/077/082/099 各追加 2026-11-17 演进记录（按先合并后新建，未新建 ADR）；api 四页各追加改版段；lessons/UiRefreshUnifiedEntry 与 TorqueModeAsUiGate 各合并一条新坑；CodeMap 卡3/卡6 与 CodeMap-Files 同步；index 重建 165 条无重复。遗留：① AntdUI Table 差分重绑依赖重绘语义，须上机实测位置与灯变化可见；② 振镜按钮「焊接中禁切换」改由整机状态事件驱动，焊接起止沿需现场验证；③ TA_Break/Pose 绝对定位改以「已回零」为位置可信依据，首次上机需实测定位基准；④ 两页定时器均为页内独立实例，刷新节拍沿用 FLOW_TIMEOUT/UI_REFRESH_MS 未改

## [2026-11-17 15:31:38] fix | 系统设置页 Y轴/TA轴 参数弹窗改值不生效（写回移到弹窗内确定按钮）
- 来源：-
- 操作：-
- 变更文件：-
- 结论 / 遗留：-

## [2026-11-17 14:38:07] fix | 修复启动期配置重复读取与初始化未完成即变更设备状态
- 来源：现场日志 2026-11-17 14:09（用户报障）
- 操作：
  1. DeltaMotionConfig 四处日志加 writeLog 门控,预览读静默
  2. InitializeMachine 改置 _initAccepted+仅开 IO 线程,5 模组与指令线程延后到初始化出结果三出口
  3. IOWork 初始化在途只推进连接链冻结全部状态变更巡检
  4. ADR-107 追加演进记录
  5. StartupInitializationOrderGates 追加坑 8
  6. 更新 api/DeviceControlWork 与 CodeMap-Files
- 变更文件：AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs;AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs;AdaWeldSystem/MainDeviceControl/DeviceStatusWork.cs
- 结论 / 遗留：静态校验 34/34 通过(含阴性对照);真编译 errors=0 rc=0;output=AdaWeldSystem_output_20261117_143741.tar.gz;遗留:预览读仍会发布流程超时快照(同文件故当前无害,后续可评估隔离);真实模式现场需确认全连跳过路径指令线程正常

## [2026-11-17 14:24:42] governance | CodeMap 重构为代码记忆总览 + 详表分页
- 来源：业主反馈：CodeMap 利用率低，反复全盘扫描使其失去代码记忆作用
- 操作：
  1. CodeMap.md 瘦身为总览(6张功能域记忆卡含主干依附+需求速查+陷阱，无沿革)
  2. 新建 CodeMap-Files.md 承原49命名空间166文件表+工程约束+分层判据(沿革存档保留)
  3. 沿革从总览移出(详情仍在详表存档与ADR/log)
  4. 新增只读工具 codemap_deps.py
  5. KR-003/KR-009 加 Grep 时机硬判据
  6. 工作流 Step0.0 与三份Skill副本同步
- 变更文件：wiki/architecture/CodeMap.md,wiki/architecture/CodeMap-Files.md,wiki/rules/KR-003-No-Skipping-Query.md,wiki/rules/KR-009-Grep-Default.md,wiki/project/vibecoding-workflow.md,tools/codemap_deps.py,tools/data/routes.tsv
- 结论 / 遗留：八闸门全绿；CodeMap.md 从1006行瘦到约180行；主干依附经 codemap_deps.py 与 ADR-093/094 交叉验证；原文件备份 CodeMap.md.bak-pre-split 供回滚

## [2026-11-17 14:05:17] fix | 初始化期禁重连与设备动作 + 机器人端 XML 写入并发保护（ADR-107）
- 来源：业主强制要求：初始化动作时任何重连线程和动作都不要开启，必须等初始化结束拿到结果才能重连；现场报错 WeldControlConfig.xml 正由另一进程使用
- 操作：
  1. 排查根因:SaveRobotRsiXml无并发保护,三条路径并发到达同一文件(初始化链/自愈重连/手动开启),自愈线程在InitializeMachine中先启动形成竞争
  2. 修复:thCommCommandWork延后到初始化链结束经EnsureCommandWorkStarted开启(正常结束+抢占中止两出口)
  3. FilebackupPage新增TryPassCommAction两档门控拒绝初始化期手动设备动作
  4. SaveRobotRsiXml加_rsiXmlLock+临时文件File.Replace原子替换+5x60ms占用退避重试
  5. 新建ADR-107
- 变更文件：MainDeviceControl/DeviceControlWork.cs,Comm/Communication/CommunicationManager.cs,UIDesign/TabPage/FilebackupPage.cs,wiki/decisions/ADR-107-init-phase-reconnect-gate.md
- 结论 / 遗留：真编译 errors=0 rc=0; 心跳线程维持原状只检测不重连; output=AdaWeldSystem_output_20261117_140458.tar.gz

## [2026-11-17 13:33:36] fix | 自动重连轮询结果日志降级 Debug（ADR-106 演进 D1）
- 来源：业主纠正：轮询结果不在主系统显示，只记录降级Debug；边界限定为自动重连自愈循环
- 操作：
  1. CommManager L794 重连成功 Info→Debug
  2. KukaRsiComm L597/605/619/666 启动失败 Warning→Debug(撤销上轮错误提级)
  3. 保留配置加载/线程异常/停止异常/初始化汇总在主系统
  4. ADR-106 追加演进 D1
  5. 修订 CodeSimplification 规则4 与 api/GlobalCommData 降噪约定
- 变更文件：Comm/Communication/CommunicationManager.cs,Comm/Communication/Implementations/KukaRsiComm.cs,wiki/decisions/ADR-106-comm-log-view-channel.md
- 结论 / 遗留：真编译 errors=0 rc=0; 5处字节级替换行尾守恒; output=AdaWeldSystem_output_20261117_133316.tar.gz; 用户观察日志含 XML 文件被占用(疑似多实例)，非本轮范围

## [2026-11-17 13:21:59] coding | 通讯日志查看通道：行为入通讯日志、结果入主系统（ADR-106）
- 来源：业主多轮澄清：通讯日志记录RSI配置/启停/交互，FilebackupPage打开才显示；主系统只留行为反馈结果
- 操作：
  1. 新增 CommLogViewEvent + ShowCommLogForView（写TcpMessageLog+仅FilebackupPage显示）
  2. 日志按行为/结果二分:行为21处转通讯通道,结果类保留ShowLog
  3. 启动停止失败Debug提Warning
  4. FilebackupPage订阅/退订/handler
  5. 新建ADR-106
  6. 修订CodeSimplification⑤规则4
  7. 同步api/GlobalCommData与api/FilebackupPage与CodeMap
- 变更文件：Comm/SystemComm/SystemComm.cs,Comm/Communication/CommunicationManager.cs,Comm/Communication/Implementations/KukaRsiComm.cs,UIDesign/TabPage/FilebackupPage.cs,wiki/decisions/ADR-106-comm-log-view-channel.md
- 结论 / 遗留：真编译errors=0 rc=0; 事件闭环完整; 未复用CommunicationCommandReceived避免污染4订阅者含2 Workflow; output=AdaWeldSystem_output_20261117_132142.tar.gz

## [2026-11-17 11:23:24] fix | 删除 FilebackupPage 通讯页签切换残留 恢复编译
- 来源：业主指令：删除设计器 tabs/tabpage 后清理关联代码，保证编译 ok
- 操作：
  1. 定位 CS0103 根因 tabs1 全项目仅 L242 引用无定义
  2. 删除 OnRadioModeChanged 方法(radio→tabs 联动空壳)
  3. 删除 Designer radioRobot.CheckedChanged 订阅
  4. 删除 ctor 冗余 radioRobot.Checked 赋值
  5. 保留 radioModeRSI_CheckedChanged(设计器仍订阅)
  6. 同步 api/FilebackupPage.md 4 处 stale
- 变更文件：UIDesign/TabPage/FilebackupPage.cs,UIDesign/TabPage/FilebackupPage.Designer.cs,wiki/api/FilebackupPage.md
- 结论 / 遗留：真编译 errors=0 rc=0; tabs1/OnRadioModeChanged 全项目零命中; 行尾守恒; output=AdaWeldSystem_output_20261117_112314.tar.gz; 并发改动时间线 11:17:03 已核实

## [2026-11-17 11:15:59] coding | 机器人重连链路轮询日志降级为 Debug
- 来源：业主指令：轮询级别 log 降 debug 不在 loginput 显示，连接成功保留一次
- 操作：
  1. CommunicationManager.EnsureRobotChannelHealthy 未监听/重连失败/重连异常 3处降 Debug，重连成功保留 Info
  2. KukaRsiComm 接收线程启动/回复线程启动/监听已绑定 3处降 Debug
  3. 复用既有 MessageLevel.Debug + ShowDebugToUi 机制未新增机制
  4. 同步 api/GlobalCommData.md 枚举四档与级别映射表
- 变更文件：Comm/Communication/CommunicationManager.cs,Comm/Communication/Implementations/KukaRsiComm.cs,wiki/api/GlobalCommData.md
- 结论 / 遗留：真编译 errors=0 rc=0; 静态 8/8; 行尾守恒; output=AdaWeldSystem_output_20261117_111531.tar.gz; 未改配置默认值; 首连成功可见性由 RecordInitOutcome 保留

## [2026-11-17 10:51:48] fix | 阶段9收口 补 ADR-105 登记与总纲 S9 并入
- 来源：业主检查指令：核对阶段0~9完成情况与架构一致性
- 操作：
  1. 真编译 errors=0 rc=0
  2. 八扫描器 rc=0 但 lint_scan 报 ADR-105 孤儿
  3. ADR-Index 补第105行并同步计数说明
  4. 总纲 v1.0→v1.1 补 S9(N23~N25)与 V18
  5. 重建索引路由
- 变更文件：wiki/decisions/ADR-Index.md,.trae/documents/MRDF-2608-设备与线程全生命周期改造总纲.md
- 结论 / 遗留：代码层面阶段0~8全部落地且无架构偏离；修复两处文档收口遗漏；孤儿页与S9追溯缺口消除；实机项仍待现场确认

## [2026-11-17 09:21:46] update | 阶段8 页面动作统一经工作流与权限门控
- 来源：ADR-105
- 操作：-
- 变更文件：AdaWeldSystem/UIDesign/TabPage/ILCamPage.cs,AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs
- 结论 / 遗留：ILCamPage 连接断开改走 LineLaserWorkflow，删 UI 线程直连；页面释放不断设备；手动连接工程师权限、模拟启动管理员权限；初始化期连接置灰并给原因；回写 ADR-105 与 api/modules/CodeMap

## [2026-11-17 08:58:17] update | 阶段7 报警停焊自适应输出全停与 RSI 载荷冻结
- 来源：设备与线程全生命周期改造总纲
- 操作：-
- 变更文件：DeviceControlWork.cs,WeldParamControlWorkflow.cs,LaserWeldHeadWorkflow.cs,CommunicationManager.cs
- 结论 / 遗留：ReportAlarm 同拍级联 ErrorAborted；FlowProcess/PreWork/MonitorAlignTick 加报警门禁；摆焊执行器非 Working 归零；新增 ClearRobotCommand 清警停发 TX_NG；新建 ADR-104 且 api/modules/CodeMap 同步

## [2026-11-17 05:16:26] update | 阶段 7 缺值策略与自适应按距离
- 来源：MRDF-2608 总纲 N08/N09/N10/N11/N15
- 操作：-
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs,AdaWeldSystem/WeldParamControl/WeldParamManager.cs,AdaWeldSystem/WeldParamControl/WeldAlgorithmsConfig.cs,AdaWeldSystem/WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs,AdaWeldSystem/WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs,AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs,AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs,AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.Designer.cs
- 结论 / 遗留：缺值期 CSP 取 held 不回落标定位；达阈值一次报警停焊（TX_NG+ErrorAborted，不复用 DoStopMachine，不清累计器）；缺值或位姿 age>2T 暂停入图；自适应改 SEGMENT_DISTANCE_MM 按段距取段内均值查表，旧键只读忽略；UI 合并每段距离并加红色提示；心跳 H2 接缺值超限

## [2026-11-17 05:01:05] update | 阶段6 心跳分级与通讯层重连落地
- 来源：MRDF-2608 总纲 N07 / D09
- 操作：-
- 变更文件：decisions/ADR-102-heartbeat-levels-and-comm-reconnect,api/DeviceControlWork,api/CommunicationManager,architecture/CodeMap
- 结论 / 遗留：心跳线程连接成功后惰性创建；H0/H1/H3/H4 变化沿；移除线程内重连；EnsureRobotChannelHealthy 5s 冷却；新增 NeedHeartbeat 配置

## [2026-11-17 04:52:40] update | 阶段5 关闭闭环与急停落地
- 来源：MRDF-2608 总纲 N05/N06
- 操作：-
- 变更文件：decisions/ADR-101-shutdown-closure-and-estop,api/DeviceControlWork,api/DeviceStatusWork,api/MotionControlWorkflow,modules/DeviceControl,architecture/CodeMap
- 结论 / 遗留：DisposeComponents 幂等+30s预算；CascadeDisconnect 等待；通讯线程标志拆分；急停不断设备；运控关闭唯一入口；线激光/模拟线程 Join；FormMain 补管理器释放

## [2026-11-17 00:23:03] update | 阶段 4 两套状态联合与动作双闸门（ADR-100）
- 来源：总纲 §4.1.1-4.1.5 / D20 / V8
- 操作：-
- 变更文件：DeviceControlWork.cs,DeviceStatusWork.cs,ADR-100-state-union-and-action-gate.md,ADR-Index.md,api/DeviceControlWork.md,api/DeviceStatusWork.md,modules/DeviceControl.md,architecture/CodeMap.md
- 结论 / 遗留：设备6态×流程7态矩阵；1s巡检挂thIOWork只纠三类非法组合；ErrorAborted只经ReportAlarm上升；SetStatus变化沿一条Info；CheckActionGate接DoSubWork L4与DoSubPrework L0；GetStatusSnapshot统一快照

## [2026-11-16 21:20:12] update | 阶段3 返工 复位挂回既有复位链（ADR-099 修订）
- 来源：业主返工指令
- 操作：-
- 变更文件：MotionControlWorkflow.cs; DeviceControlWork.cs; ADR-099; api/*; modules/DeviceControl; CodeMap
- 结论 / 遗留：撤销 ResetToWorkZero 独立入口；ResetProcess 内做门槛L1与能力分支并落到管理器动作；初始化只连接使能不变

## [2026-11-16 18:21:31] update | 阶段3 初始化与复位分离（ADR-099）
- 来源：业主推进 阶段3
- 操作：-
- 变更文件：DeviceControlWork.cs; MotionControlWorkflow.cs; DeviceStatusWork.cs; SystemControlPage.cs; ADR-099; api/*; CodeMap
- 结论 / 遗留：初始化只连接使能；机器人通讯强制；受理门禁与补连；初始化期不判互锁；复位门槛L1按轴能力；回退开关INIT_RUN_TA_HOME

## [2026-11-16 18:11:20] coding | 阶段2 分层就绪L0~L4与轴级能力
- 来源：总纲v1.0 阶段2（业主授权自主推进）
- 操作：
  1. DeviceWorkflowBase 新增 ReadinessStage 枚举与就绪分层 region：IsConnected/IsEnabled/IsHomed/IsAtWorkZero/NeedHoming/HasAbsoluteEncoder/WorkZeroSource/ReadinessStage/EnsureReadiness
  2. MotionControlWorkflow 覆盖 Y 轴就绪（绝对编码器使能即 Homed，工作零位取 TeachLockYMm）
  3. LaserWeldHeadWorkflow 覆盖 TA 轴就绪（TaMotionReady/TaHomed/TaAvailable）
  4. 新建 ADR-098 并登记 ADR-Index；api/modules/CodeMap 同步
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; wiki/decisions/ADR-098-readiness-layering-axis-capability.md; wiki/decisions/ADR-Index.md; wiki/api/MotionControlWorkflow.md; wiki/api/LaserWeldHeadWorkflow.md; wiki/modules/DeviceControl.md; wiki/architecture/CodeMap.md
- 结论 / 遗留：Rebuild 0错0警；simplify_run PASS（EOL 修复后）；comment_scan 全 0。L4 容差复用 CalReturnToleranceMm，未新增常量。阶段3 起 Home/GotoWorkZero 按轴实现可直接消费本层能力声明。

## [2026-11-16 17:59:07] coding | 阶段1 缺值距离量测与CSP查图同源
- 来源：总纲v1.0 阶段1（业主授权自主推进）
- 操作：
  1. RunCspTick查图X改取WeldParamManager.CurrentRobotX（D21，保留回退开关）
  2. WeldParamManager新增缺值累计距离NoValueDistanceMm/NoValueSource（起焊沿开窗、激光帧清零、|dX|与停滞推定）
  3. NO_VALUE_TOLERANCE_MM默认5.0并载入钳位1~50mm
  4. 轴组与TA_HOME增已配置/未配置Debug日志
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/WeldParamControl/WeldParamManager.cs; AdaWeldSystem/WeldParamControl/WeldAlgorithmsConfig.cs; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs
- 结论 / 遗留：编译0错0警; simplify_run PASS remaining=0; comment_scan 全0; 阶段1只观测不触发停焊（动作在阶段7）; 存量INI若仍为2.0则生效值仍2.0（起焊沿Info日志自证生效阈值）

## [2026-11-16 11:45:09] 修改 | 界面触发的指令统一置手动模式，振镜与运控动作日志按模式甄别
- 来源：业主复核 RunMode 用法
- 操作：
  1. LaserWeldHeadWorkflow 振镜回零与演示日志改 LogAction
  2. ProcessControlPage/SystemControlPage/MonitorCamPage 界面入口置手动；模拟启停改由界面置手动；删除 DeviceControlWork 模拟分支的自动置位
- 变更文件：LaserWeldHeadWorkflow.cs; ProcessControlPage.cs; SystemControlPage.cs; MonitorCamPage.cs; DeviceControlWork.cs
- 结论 / 遗留：Rebuild 0/0；simplify PASS；comment_scan 三项 0；八扫描器 rc=0

## [2026-11-16 10:24:29] 修改 | 工作流基类新增运行模式（自动/手动），动作日志按模式甄别，消除初始化打印手动连接的歧义
- 来源：现场日志 20261113 初始化段
- 操作：
  1. 基类新增 WorkflowRunMode 与 RunMode/SetRunMode/ModeName/ModeText/LogAction
  2. 监控相机与线激光连接/断开日志改由模式生成
  3. 初始化/编排/关停入口置自动，界面按钮置手动
- 变更文件：DeviceWorkflowBase.cs; MonitorCameraWorkflow.cs; LineLaserWorkflow.cs; DeviceControlWork.cs; MainPage.cs; ILCamPage.cs
- 结论 / 遗留：Rebuild 0/0；simplify PASS；comment_scan 三项 0；八扫描器 rc=0

## [2026-11-13 22:02:56] 修复 | 现场日志9项整改：运控配置单次加载与关停顺序反转
- 来源：现场日志 20261113_17:22
- 操作：
  1. 移除重复运控配置加载
  2. 日志文案通顺化
  3. 删除噪声日志
  4. 关停改为线程→设备→主站
  5. 主站正常关闭不触发急停
  6. 健康巡检同因去重
- 变更文件：MotionControl/MontionManager.cs; UIDesign/MainWindow/FormMain.cs; LineLaserCam/LineLaserConfig.cs; UIDesign/TabPage/SystemControlPage.cs; UIDesign/ControlPage/MainPage.cs; MainDeviceControl/DeviceControlWork.cs; MainDeviceControl/DeviceStatusWork.cs; Comm/Communication/Implementations/KukaRsiComm.cs; MonitorCam/MonitorCamManager.cs
- 结论 / 遗留：启动日志运控配置由3次降为1次；退出顺序固定为先停线程再断设备；Rebuild 0/0、simplify PASS、八扫描器全绿

## [2026-11-13 17:26:56] governance | 日志截断：51→50 条，归档 1 条
- 来源：每周 Phase 4 Lint 例行截断
- 操作：
  1. wiki_log.py truncate 保留最新 50 条
  2. 归档 1 条旧条目到 logs/backup/
  3. 重建 logs/INDEX.md（58 行）
- 变更文件：logs/log.md; logs/INDEX.md; logs/backup/
- 结论 / 遗留：截断前 51 条 → 截断后 50 条; 归档 1 条; INDEX.md 已同步重建

## [2026-11-13 17:25:44] governance | 每周例行维护：知识库自检+代码漂移+日志截断
- 来源：定时任务（每周 Phase 4 Lint）
- 操作：
  1. 修复 logs/backup/log_2026-11-02.md 中 3 处模板占位符红链（去链接化）
  2. api/DeviceControlWork.md 补章节导航（604→631 行）
  3. 5 个 IntelligentLaser 拆分页页头去重（消除 0.69/0.72 内容重复）
  4. 代码漂移抽查 CodeMap 222 路径仅 2 处已标注移除
  5. 清理 14 个 _tmp_*.txt 与 4 个 .pyc 缓存
- 变更文件：logs/backup/log_2026-11-02.md; wiki/api/DeviceControlWork.md; wiki/lessons/IntelligentLaser-Delegate-Gc.md; wiki/lessons/IntelligentLaser-Sdk-Interop.md; wiki/lessons/IntelligentLaser-Callback-Mechanism.md; wiki/lessons/IntelligentLaser-Job-System.md; wiki/lessons/IntelligentLaser-Ui-State.md
- 结论 / 遗留：八扫描器全绿（exit=0）; 代码漂移待修正 0; ADR 编号 1~97 连续无空洞; 孤儿页 0; 红链 0; 日志截断前 50 条

## [2026-11-13 16:31:29] refactor | 主页面导航重组：相机设置并入系统参数设置 + 设备监控空页
- 来源：业主界面优化五项（跨会话转入）
- 操作：
  1. 删除顶部「相机设置」页及 navPageImage；参数设置改名系统参数设置；系统参数设置 NavPage 扩为 5 子页（工艺/系统/线激光/监控相机/文档备份）；新增空 TabPage「设备监控」于主页面之后；ILCamPage tabsIL.Text 改线激光设置；MonitorCamPage 原样不动
- 变更文件：AdaWeldSystem/UIDesign/MainWindow/FormMain.cs；AdaWeldSystem/UIDesign/TabPage/ILCamPage.Designer.cs；LLMWiki/wiki/api/FormMain.md；LLMWiki/wiki/architecture/CodeMap.md；LLMWiki/wiki/modules/UIDesign.md；LLMWiki/wiki/decisions/ADR-051-ILCamPageTabsConversion.md
- 结论 / 遗留：顶部四页=主页面/设备监控(空)/系统参数设置/数据追溯，dataPage 仍 index 3、_hiddenItem1~3 仍三项；字号未动（另开一轮）；Config 未覆盖：本轮无新增/无覆盖配置键；遗留：设备监控内容待后续在 Designer 补

## [2026-11-13 16:15:17] fix | 追溯页诊断撤除+首进不弹窗；主站初始化超时暴露与失败码上报；关闭链同步级联断开与硬件释放
- 来源：业主现场日志四问（追溯页报错/30s超时设置/关闭只见线激光断开）
- 操作：
  1. DataReviewerPage 撤除正常路径 DiagLog（残留脚手架），InitPCLDir 增 userInitiated，首进 0 行只更新中性文案不弹窗
  2. SystemControlPage tLPTimeout 新增 主站初始化(秒) 控件 txtMasterInit + 读改存三段式接线
  3. DeltaMontionControl Master_Initial/Get_CardSeq 失败码如实上报（不再记哨兵卡号99空等超时），新增 _masterOpened 标志
  4. DeviceControlWork 关闭链改同步 CascadeDisconnect（不再置位脉冲型 Stop_IO 指望扫描线程消费），逐模组补 模组断开 已受理 日志
  5. FormMain_FormClosed 补释放运控工作流（关台达主站）与监控相机工作流（停监督释放Mat）
- 变更文件：AdaWeldSystem/UIDesign/ControlPage/DataReviewerPage.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMontionControl.cs; AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/UIDesign/MainWindow/FormMain.cs; Vicoding管理平台/LLMWiki/wiki/api/DataReviewerPage.md; Vicoding管理平台/LLMWiki/wiki/api/SystemControlPage.md; Vicoding管理平台/LLMWiki/wiki/api/DeviceControlWork.md; Vicoding管理平台/LLMWiki/wiki/api/MontionManager.md; Vicoding管理平台/LLMWiki/wiki/modules/MotionControl.md; Vicoding管理平台/LLMWiki/wiki/lessons/StartupInitializationOrderGates.md; Vicoding管理平台/LLMWiki/wiki/architecture/CodeMap.md
- 结论 / 遗留：MSBuild /t:Rebuild 0 error 0 warning；静态自检 14/14 PASS（Designer三面/TLP扩行四处同步/InitPCLDir调用点/关闭链接线/csproj完整性）；output 包 AdaWeldSystem_output_20261113_161504.tar.gz（3.1MB）；教训页合并追加 坑6（不新建）；遗留：现场需实测台达主站初始化失败的真实厂商返回码（此前被超时掩盖），本轮只保证不再掩盖

## [2026-11-13 13:52:19] refactor | 工艺设置页 lblQuickTrackingTip 改名 + 指令区状态标签清零
- 来源：业主两项要求（跨会话转入）
- 操作：
  1. lblQuickTrackingTip→lblQuickTracking（Designer 16 处）；删除 UpdateCommandAreaTips 及其调用；ApplyActionBack 去掉无消费者 reason 形参；InstructionWorker 执行异常补 Error 日志；wiki api 页与 ADR-082 同步
- 变更文件：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.Designer.cs；AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs；Vicoding管理平台/LLMWiki/wiki/api/ProcessControlPage.md；Vicoding管理平台/LLMWiki/wiki/decisions/ADR-082-TaInitFourStepAndAvailability.md
- 结论 / 遗留：lblQuickTrackingTip 全仓 0 命中；lblQuickTaTip/lblQuickLaTip 代码中本就不存在（仅历史文档残留）；状态出口=按钮底色+轴表灯/状态码+日志

## [2026-11-13 10:35:50] refactor | 系统设置页新增 tLPFlowSetting/tLPTimeout 两区：工艺启用开关跨页迁移 + 两页字号行高统一
- 来源：业主三项要求（MRDF-2608：开关迁移 / 等待超时迁移 / 两页字体高度严格统一，样本 gridFitterControl）
- 操作：
  1. 1. 新建 gridSimTestZones 卡片 panelFlowSetting+panelTimeout；tLPFlowSetting 收 5 组工艺启用（标签+开关，4 列自然换行，1 组/2 列，3 行）
  2. 2. 5 个 CheckedChanged 处理器与 SaveProcessEnable 由 ProcessControlPage 迁至 SystemControlPage，新增 _loadingProcessEnable 守卫与 LoadProcessEnableOnForm 回填（构造 + 读取按钮）
  3. 3. 状态字段仍为 WeldParamManager.AlgorithmsConfig（共享单例，非页面私有），写回仍落 AlgorithmsZone.Quick，行为不变
  4. 4. gridLaserCalib 的流程等待/设备侧等待两段（2 小标题 + 14 字段）迁入 tLPTimeout，gridLaserCalib 收缩为 标题/小标题/标定角度 4 行
  5. 5. 两页全部 TLP 单元格控件字号高度归一：title 12pt/35（Bold）、段内小标题 10pt/30、label/Input/Select/Radio/Button/Switch 9pt/28，显式 Microsoft YaHei UI，行样式同步
  6. 6. gridProcessDebug 按业主要求保留空容器，2x2 框架与 gridQuickZones 行列定义未动
- 变更文件：AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.Designer.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; AdaWeldSystem/WeldParamControl/WeldAlgorithmsConfig.cs
- 结论 / 遗留：MSBuild /t:Rebuild 0 error 0 warning；simplify_run --skip-build PASS（guard 168/0、ide remaining=0）；comment_scan 三项 0；八扫描器 rc=0；包 AdaWeldSystem_output_20261113_103528.tar.gz（356 项，两页 GridPanel=0、.Span=0，tLPFlowSetting 11 项 / tLPTimeout 31 项在包内）；自检脚本 312 个单元格控件字号+行高偏差 0（title 14 / 小标题 10 / label 122 / input·select·radio·button 161 / switch 5）；各 TLP 固定行高合计均未超卡片可用高（gridQuickLa 440→320，余 76）；无新增配置键；Designer 时间戳 10:28 晚于出包前写入、包后无回退；遗留待业主裁定：删空 gridProcessDebug 并让其余三格上移（本轮按要求未重排）

## [2026-11-12 18:37:12] refactor | 两页布局返工：28 个 GridPanel 拆平为单层 TableLayoutPanel（一行四列 160x32 / 标题跨4行高40）
- 来源：业主否定上一轮「外层单列+嵌套 TLP」方案：TLP 不需要多层，一个区域一个 TLP，显式坐标落格
- 操作：
  1. 每区域仅一个 TLP（Dock=Fill 放入 panel），4 列；字段区 Absolute 160、容器区 Percent 25（gridWeldZones 16/28/28/28 复刻 260+fill）
  2. 一律 Controls.Add(child,col,row) 带坐标，标题占第 0 列并 SetColumnSpan(4)，禁止无坐标顺序 Add
  3. 行高：标题 Absolute 40、字段行 Absolute 32，末尾补一行 AutoSize 空行吸收余高
  4. 子控件：字段/标题 Anchor=Left|Top + Size 160x32（标题 640x40）+ Margin=0；结构子控件 Dock=Fill
  5. 纯纵向堆叠的内层网格并入外层并删除容器（gridQuickLaFocus/gridQuickLaGalvo/gridLaserLa/gridLaserGalvo/gridLaserTa/gridWeldPonts），原无 Dock 的 4 个网格补 Dock=Fill
  6. ShadowOpacityAnimation 全 false（SCP 9 / PCP 8，含 panelProcessDebug 补写）
- 变更文件：AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.Designer.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs
- 结论 / 遗留：MSBuild /t:Rebuild 0 警告 0 错误（真编译已跑，非 skip）；simplify_run --skip-build ide remaining=0；comment_scan 三项 0；八扫描器 rc=0；包 AdaWeldSystem_output_20261112_184108.tar.gz（356 项，包内 GridPanel=0 / Span=0 / Shadow=true=0 / TLP 12+10 且每个 4 列样式 + 尾行 AutoSize）；几何自检 347 子控件全部带坐标、行列不越界；仅剩 gridPanelRight 一层嵌套（右栏需再上下二分，结构必需）；gridQuickLa 固定行合计 440 > 卡片可用约 394，底部约 1 行会被裁

## [2026-11-12 16:11:29] uifont | SystemControlPage/ProcessControlPage 全量 GridPanel 换 TableLayoutPanel 且面板阴影动画关闭
- 来源：业主需求（MRDF-2608 双页布局治理）
- 操作：
  1. 17 个 Panel 的 ShadowOpacityAnimation 置 false（含补写 panelProcessDebug）
  2. 28 个 GridPanel 换 TableLayoutPanel（12+16）
  3. AntdUI 忽略 Dock，112 个单元格子控件补/改 Dock=Fill 以保持铺满几何
  4. 网格内多列行用嵌套 TableLayoutPanel（SCP 17 组 / PCP 14 组）还原逐行独立列宽
- 变更文件：AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.Designer.cs
- 结论 / 遗留：MSBuild /t:Rebuild 0 警告 0 错误；simplify_run ide remaining=0；comment_scan 三项 0；八扫描器 rc=0；包 AdaWeldSystem_output_20261112_161043.tar.gz 356 条目，包内 ShadowOpacityAnimation=true 0 处、GridPanel 0 处；子控件落格与控件集合经脚本核对全等；业务逻辑/事件/配置键/命名未动

## [2026-11-12 13:45:33] 变更 | 工艺设置页合并：激光页并入快捷页 2x2
- 来源：-
- 操作：
  1. 删除 tabPageLaserProcess；三区参数并入 gridQuickTracking/gridQuickTa/gridQuickLa；GA 指令标识改 GA_*；清理引用不存在标签的遗留编译错误
- 变更文件：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.Designer.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs
- 结论 / 遗留：2x2 框架未动，功能零丢失，配置键未改

## [2026-11-12 09:39:13] 新增 | 系统设置温控区增加焊接头从站启用开关
- 来源：-
- 操作：-
- 变更文件：AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs
- 结论 / 遗留：开关随保存写 ROOT/WELD_HEAD_SLAVE/ENABLED，读取按钮回填，不即时下发

## [2026-11-11 16:17:29] 修订 | 从站在线判定分层
- 来源：-
- 操作：-
- 变更文件：AdaWeldSystem/MotionControl/MontionManager.cs; AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMontionControl.cs
- 结论 / 遗留：焊接头未配置/未启用/未连接三态；Y 轴与焊接头未上总线报从站未连接，不再读状态字 0x0000

## [2026-11-11 15:27:21] 修复 | 日志显示端按级别过滤 + 初始化赘述裁剪 + 焊接头从站计跳过
- 来源：现场日志 2026-11-11 14:56:32（业主：分级日志全部显示）
- 操作：
  1. ShowLog 的 Debug 分支默认不触发界面事件，文件仍全量；新增 [Display] ShowDebugLog 开关
  2. RSI/线激光/台达轴/运动管理器初始化配置回显统一降 Debug，RSI 与他人失败原因去路径与嵌套括号
  3. TA ZeroPose/轴闸门/TA_Auto 去变量名括号与解释尾巴；回零仅保留初始化回零一条 Info
  4. 焊接头从站未启用改为规划期跳过，汇总只统计真实失败
- 变更文件：Comm/SystemComm/SystemComm.cs; Comm/Communication/CommunicationManager.cs; Comm/Communication/Implementations/KukaRsiComm.cs; LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs; MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs; MotionControl/MontionManager.cs; MotionControl/AxisRegistry.cs; MotionControl/IORegistry.cs; MotionControl/CylinderRegistry.cs; MotionControl/MoveControlData.cs; MotionControl/DeltaEtherCAT/DeltaMontionControl.cs; MainDeviceControl/DeviceControlWork.cs; MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; UIDesign/TabPage/ProcessControlPage.cs; wiki/standards/InitializationLogSpec.md
- 结论 / 遗留：Rebuild 0 error 0 warning；simplify_run PASS（guard 168/0、ide remaining=0）；comment_scan 三项 0；八扫描器 rc=0；同场景 91 条/3459 字符 → 28 条/596 字符（-69.8% 条数、-82.8% 字符）；接口区分：16#60E0/E1 探测成功、0x6072 回落成功，暂不切 60E0/E1 方案，待现场复核

## [2026-11-11 14:53:05] fix | 回零门禁解环 / TA 指令改 Click 派发 / 初始化日志极简重写
- 来源：现场：回零被 TaHomed 挡住；TA 点第二下无反应；初始化日志废话过多
- 操作：
  1. 新增 GetAxisHomingGateReason 摘掉 TaHomed 依赖，TryHomeAxisWithWait 改用它
  2. 新增 HomeEvidence 全链路证据，失败不再空证据
  3. TA 六个 Radio 改 Click 派发，CheckedChanged 只清底色
  4. 门禁被拒补按钮变红
  5. 初始化日志按极简密度重写，明细降 Debug
  6. InitializationLogSpec 新增第六节
- 变更文件：AdaWeldSystem/MotionControl/MontionManager.cs; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; wiki/standards/InitializationLogSpec.md; scripts/csharp_review.py
- 结论 / 遗留：循环依赖：TryHomeAxisWithWait 用 GetAxisGateReason，TA 分支读 TaHomed。点击不响应：挂 CheckedChanged，已选中再点不触发。日志样例 11 行 631 字 → 10 行 197 字。

## [2026-11-11 14:23:12] fix | 行尾统一为 CRLF（DeltaMontionAxis / ProcessControlPage）并补齐 WaitAxisHomed 判据注释
- 来源：simplify_guard 结构守卫 eol-mixed fail=2
- 操作：
  1. DeltaMontionAxis.cs 20 处独立 LF 归一为 CRLF
  2. ProcessControlPage.cs 5 处独立 LF 归一为 CRLF
  3. WaitAxisHomed remarks 改为须驱动器确认完成；BOM 保持
- 变更文件：AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; AdaWeldSystem/MotionControl/MontionManager.cs
- 结论 / 遗留：guard files=168 fail=0 PASS；仅行尾与注释，无逻辑改动；simplify_run --skip-build PASS rc=0。

## [2026-11-11 14:10:31] fix | TA 回零误判修复：必须看驱动器 Home_Status 1→0；回零后扭矩上限在线回落
- 来源：现场：回零没顶到极限位就被置 0 / 业主：不能只在回零的时候满扭矩
- 操作：
  1. WaitHomeDone 重写为必须观察 Home_Status 1→0，2s 内始终 0 判未启动失败
  2. 新增 HomeVerified 与 StartHome 复位；WaitAxisHomed 完成条件加权威信号
  3. 新增 HomeAxisAndWait 阻塞入口，TryHomeAxisWithWait 失败即停轴中止、不进 ZeroPose
  4. 新增 RestoreTorqueLimitAfterHome，回零确认后在线写回 TorqueLimitPerMille 并回读
  5. 新增 16#60E0/16#60E1 只读探测（每进程一次）取证
- 变更文件：AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs; AdaWeldSystem/MotionControl/MontionManager.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs; wiki/decisions/ADR-088-TaSharedTorqueLimit.md; wiki/lessons/StartupInitializationOrderGates.md
- 结论 / 遗留：根因三条叠加：初始化走 HomeNoBlock 从不查 Home_Status；Home_Status==0 兼作未启动与已完成；HomeOffset 缺省 0 + 增量编码器上电≈0 使判据 t=0 成立、3 拍封完成。0x6072 在线可写性仍未获手册确证，回落走在线写 + 回读，失败只告警不加 OFF/ON 循环（须业主拍板）。HomeMode=-3 语义本机资料无法确证，待现场回读 16#6098。

## [2026-11-11 13:36:45] refactor | 指令按钮 Tooltip 全部收敛为静态功能说明
- 来源：业主令：Tooltip 不写状态，只介绍按钮作用
- 操作：
  1. InitCommandTooltips 仅构造时 SetTip 一次；删除 ApplyHoverTip/RestoreBaseTip/AttachHoverTips 与 _baseTips/_diagTooltip；清掉执行成功/失败/执行中/不可执行/忙/已取消 六类状态文案；失败原因改写 lblQuickTaTip
- 变更文件：UIDesign/TabPage/ProcessControlPage.cs; wiki/api/ProcessControlPage.md
- 结论 / 遗留：状态渠道收敛为底色+轴表指示灯与状态码+状态标签+日志；刷新与悬停均不再碰 Tooltip

## [2026-11-11 13:24:41] fix | TA 控制按钮卡顿改控件层：后台采集+差分上屏+Tooltip 悬停
- 来源：业主澄清：卡的是 TA 控制按钮控件层本身
- 操作：
  1. ActionRefresh_Tick 改 Task.Run 采集门禁快照并单飞；RefreshActionStates 只读快照并差分赋值；Tooltip 改 MouseEnter/MouseLeave 驱动；点击路径改读快照不再取硬件；非当前页不采
- 变更文件：UIDesign/TabPage/ProcessControlPage.cs; wiki/api/ProcessControlPage.md
- 结论 / 遗留：刷新原生状态字 5→0 次/拍，Tooltip 6→0 次/拍；上色同色不重绘；诊断日志走 Debug 级

## [2026-11-11 12:02:00] feature | TA 按钮卡顿治理 + 回零满扭矩 + 初始化先回零后 TA_Auto
- 来源：业主：TA 指令 UI 点击会卡；按钮点击不能刷新/循环，刷新统一单线程 30Hz（缺省 33ms）；TA 回零用满扭矩；初始化应先回零再 TA_Auto，伺服下电位置会变
- 操作：
  1. C: 新增配置 UI_REFRESH_MS（缺省 33ms）进 FlowTimeoutConfig；SystemControlPage.timerRefresh 由 PollIntervalMs(16ms) 改 UiRefreshMs 并逐拍自校正；ProcessControlPage 增 _actionTimer + _actionDirty，13 处 RefreshActionStates 直调改 RequestActionRefresh 置脏，唯一刷新入口 ActionRefresh_Tick，销毁 DisposeActionTimer
  2. A: DeltaMontionAxis 增 FullTorqueOnEnable，使能时 16#6072 写满量程；TA 轴置真；WaitAxisHomed 判据改按 HomeOffset 比对并加回零后复读校验
  3. B: MontionManager 增 TaHomed，TaAvailable 纳入门禁，TaDegradedReason 增未回零原因，MarkInitCompleted(false) 清零；MotionControlWorkflow 增 RunTaHomeThenZeroPose，初始化链改调；ExecuteTaZeroPose 未回零告警
- 变更文件：UIDesign/TabPage/ProcessControlPage.cs;UIDesign/TabPage/SystemControlPage.cs;MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs;MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs;MotionControl/MontionManager.cs;MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs;MainDeviceControl/DeviceControlWork.cs;wiki/standards/DeviceInitializationDependency.md;wiki/api/MontionManager.md;wiki/api/MotionControlWorkflow.md;wiki/api/ProcessControlPage.md;wiki/api/SystemControlPage.md;wiki/api/DeviceControlWork.md;wiki/decisions/ADR-093-FlowTimeoutConfigAndLayering.md
- 结论 / 遗留：Rebuild 0 警告 0 错误；simplify_run ide: remaining=0；comment_scan merged_over/var_multiline/legacy_line 三项 0。回零稳定性采样未改（3×16ms≈48ms），另加收尾复核日志；满扭矩仅抬驱动侧 6072，CST 目标仍按软件钳制。

## [2026-11-11 11:39:13] feature | 主页面焊接预览改经监控相机工作流（30Hz 节流 + 随焊接启停开关）
- 来源：业主口径：主页面预览属焊接过程，与调试页不是一个路数；显示节流 30Hz
- 操作：
  1. MonitorCameraWorkflow 新增 WeldPreviewHz=30 / StartWeldPreview / StopWeldPreview / OnManagerPreviewFrame / DisposeFrame，DisposeManaged 首行退订
  2. DeviceControlWork.SimMonitorCamStartWeld 采集成功后开启预览；SimMonitorCamStopWeld 首行关闭预览
  3. MainPage 订阅 WeldPreviewFrame，BeginInvoke 后赋 imb_WeldViewer.Image，显式释放上一帧；DisposeComponents 退订并释放末帧
  4. WorkflowResponsibilityBoundary 新增 §八 双通道并存；ADR-016 追加演进记录；MonitorCameraWorkflow / MainPage / MonitorCam / ADR-050 同步
- 变更文件：MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs;MainDeviceControl/DeviceControlWork.cs;UIDesign/ControlPage/MainPage.cs;wiki/standards/WorkflowResponsibilityBoundary.md;wiki/decisions/ADR-016-WorkflowResponsibilityBoundary.md;wiki/decisions/ADR-050-SimulationWeldCameraIntegration.md;wiki/api/MonitorCameraWorkflow.md;wiki/api/MainPage.md;wiki/modules/MonitorCam.md
- 结论 / 遗留：Rebuild 0 警告 0 错误（产物 bin\\Release\\AdaWeldSystem.exe）；simplify_run ide: remaining=0；comment_scan limit=20 merged_over=0 var_multiline=0 legacy_line=0。调试页未改动（仍直连 PreviewFrameEvent）；RelayPreviewFrame 的 Clone/释放契约与 DrawSpotMark 未动。

## [2026-11-11 11:15:41] fix | 初始化收尾先开闸再判轴，恢复自动 TA_ZeroPose
- 来源：现场日志 2026-11-11 10:42:17（TA 使能成功但无 ZeroPose 记录）
- 操作：
  1. FinishInitialization 顺序改为 使能→MarkInitCompleted→按轴判定→自动ZeroPose→轴闸门报告
  2. else if(!taConfigOk) 改 else，未就绪不再静默
  3. 更新 lessons 坑4 / modules/DeviceControl / api/DeviceControlWork / api/MainPage
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; Vicoding管理平台/LLMWiki/wiki/lessons/StartupInitializationOrderGates.md; Vicoding管理平台/LLMWiki/wiki/modules/DeviceControl.md; Vicoding管理平台/LLMWiki/wiki/api/DeviceControlWork.md; Vicoding管理平台/LLMWiki/wiki/api/MainPage.md
- 结论 / 遗留：根因 TaMotionReady 首条 !_initCompleted，而 MarkInitCompleted 排在自动回零之后；门禁 Rebuild 0/0、simplify_run ide:remaining=0、comment_scan 0

## [2026-11-11 00:50:03] refactor | P0 双路X反依赖消除 / P1 配置所有权收归Manager / P2 名称启发式误报判据删除
- 来源：业主三项裁决：LineLaserManager获取X有模拟X与真实X两条路不可断；配置整理到Manager禁止外部NEW且UI经Manager路由；功能重叠删除
- 操作：
  1. P0: LineLaserManager删using MainDeviceControl,454行改读WeldParamManager.Instance.CurrentRobotX
  2. 模拟路由SimTick→UpdateRobotPose与真实路由RSI→OnRobotDataReceived两条写入链原样保留,GetEffectiveRobotX另8处模拟行程判定不动,真实态轮廓帧X由0变真值(业主批准)
  3. P1: MontionManager新增CreatePreviewMotionConfig()(封装new+LoadConfig(false)),AlgorithmManager新增CreateEmptyPipelineConfig(),FilebackupPage两处与ILCamPage一处改经Manager路由,SystemControlPage本就走MontionManager.Instance
  4. P2: 取证发现ConfigSelfHeal.Backup有2处调用(207/248)、WeldHeadSlaveDevice.DescribeTemperatureThreshold有2处调用(LaserWeldHeadWorkflow 195/201),业主裁定不删方法,删除csharp_review.py名称暗示旧版本残留启发式子判据
  5. 同步ADR-045演进记录、4个API页、CodeMap、判据库坑10、报告待裁决节
- 变更文件：AdaWeldSystem/LineLaserCam/LineLaserManager.cs; AdaWeldSystem/MotionControl/MontionManager.cs; AdaWeldSystem/EmguALG/Manager/AlgorithmManager.cs; AdaWeldSystem/UIDesign/TabPage/FilebackupPage.cs; AdaWeldSystem/UIDesign/TabPage/ILCamPage.cs; LLMWiki/scripts/csharp_review.py; LLMWiki/scripts/arch_boundary_scan.py; wiki/decisions/ADR-045; wiki/api/LineLaserManager.md; wiki/api/AlgorithmManager.md; wiki/api/MontionManager.md; wiki/architecture/CodeMap.md; wiki/lessons/StaticVerifier-Checker-FailureModes.md
- 结论 / 遗留：三批复核：批次1/2 各 build errors=0 rc=0; 最终全套 guard files=168 fail=0、全库warn/error=0、selfcheck四重自证PASS、真编译errors=0 rc=0、ide remaining=0、simplify_run PASS。重扫标记239→233(架构9→5:A2归零/A5 4→1,C.功能重叠2→0)。遗留：A5剩1条DeviceControlWork.SimulationConfig(类注释明确由DeviceControlWork单例持有,已裁定设计); C.疑似死函数101/平行指令4/跨层候选14仍待逐案裁决
