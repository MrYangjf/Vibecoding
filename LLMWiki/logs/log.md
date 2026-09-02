# Wiki Log — 变更日志

> 时间导向的追加日志。每条记录以 `## [日期时间] 操作类型 | 描述` 开头。
> 时间戳获取方式：执行 PowerShell 命令 `Get-Date -Format "yyyy-MM-dd HH:mm:ss"` 获取准确时间。
> 若无法执行命令，标记为 `[No.]`，**严禁猜测填写**。

---

## [2026-09-02 20:43:06] ingest | 业务流向图原档沉淀（ADR-050 原档 2→3）+ 架构页业务状态流章节 + ResetMachine/StopMachine 级联代码修正
- 来源：用户指令「沉淀焊接系统工作流程业务流向图.pdf 到知识库。全盘理解三份架构图模式。然后修正知识库：全量删除旧结构，新架构兼容并蓄的整合。然后对代码进行修正」
- 原档：`raw/architecture/` 新增 `焊接系统工作流程业务流向图.pdf`（业务状态流：NoReset→Reseting→Reset OK→Running→PreWorking/WeldWorking→Stop/Alarm 主链 + 通讯/命令-IO-Pose/EMG-故障树三条横向通道）+ 渲染辅助 `业务流向图_overview.png`；清理临时 tile PNG；ADR-050 原档清单 2→3
- 架构页：页头新增三份原档分工表（xlsx=名词 / 流程图=动词 / 业务流向图=剧本）；§7.5 契约表对齐代码（ResetMachine=在位检测阻断+级联 ResetProcess×5；StopMachine=级联 ClearStatus×5；ClearAlarm=仅清标志无级联）；新增 §7.6 业务状态流主链与两条语义映射（Reset OK≡Stop、Running 业务语义分层）+ StartMachine 疑似级联存疑记录
- 代码（DeviceControlWork.cs，已提交 f51ce43 待推）：新增 IsRobotReachable / CascadeResetProcess / CascadeClearStatus；ResetMachine 在位检测不通过→Alarm+RecordFault(ROBOT_OFFLINE)+阻断；StopMachine 停线程后级联 ClearStatus 再断开。csharp_review 0 error（剩 2 处 Thread.Sleep 豁免）
- 用户决策：在位检测失败→阻断复位；StartMachine 疑似级联→暂不实现仅记录；StopMachine 级联→实现
- 待办：推送 GitHub 挂起（本机 TLS 劫持 + SSH 公钥未注册，等用户注册后走 ssh.github.com:443）

---

## [2026-09-02 17:07:03] ingest | KB 冲突/遗留/重复清理 + MainDeviceControl 代码精简（ADR-038/049 复检）
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
  2. `decisions/ADR-050-ArchitectureRawSource.md`（新建）：原档 = 架构唯一修改入口；更新流程 = 改原档 → AI 同步架构页 → wiki_audit；冲突裁决 = 原档 > 架构页 > 源码注释
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
  4. `index/index.md`：清除四态/泛型/MainDeviceWorkflow/SafetyWorkflow 残留（architecture/modules/DeviceControl/modules/Safety/api/*/lessons/*/standards 摘要同步三态+非泛型）；新增 [[api/LaserWeldHeadWorkflow]] 链接；ADR-049 补入 7.1（原仅引用未入表），ADR-041/042 加 ⚠️ 取代横幅（核心四态+泛型已被 ADR-049 取代），ADR-044/047 同步三态命名；表头「取代 ADR-041/042/047/048」修正为「取代 ADR-041/042」（步骤驱动 ADR-047 / 自动手动 ADR-048 仍现行有效）
- 顺带修复：`modules/DeviceControl.md` 红链 `ADR-034-DisposeFullCoverage`→`ADR-034-DisposePatternFullCoverage`；孤儿页 `lessons/DeviceWorkflowDualFlowCallerGate` 补入 index lessons 表（内容仍含 MainDeviceWorkflow/设备四态旧词，待后续刷新）
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

**KB 同步（Phase 3）**：新建 [[decisions/ADR-048-AutoManualDualWorkflow]]；ADR-017 加「⚠️ 部分取代」横幅；[[api/SimulationWorkflow]] 改墓碑页（含新旧 API 对照表）；[[api/MainDeviceWorkflow]] 增补双流程生命周期 + 模拟 API 两节；[[modules/DeviceControl]] 新增「双流程层」小节 + 目录树/生命周期表更新（8→7 工作流文件）；[[standards/StepDrivenWorkflow]] 红线 3 补 ADR-048 边界注记；[[index/index]] 场景路由 + API 表 + ADR 表 + 编号说明（44 条）同步。

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
**修复**：LineLaser / MonitorCamera / MotionControl / WeldParam 四处统一改 `State = MapToDeviceState(_step)`（ErrorAborted/Error → Alarm，与 ADR-041「禁手工 State= 赋值」同口径）。
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
**更新 Wiki 页面**：`architecture/DeviceControlArchitecture`（§2 目录树 + 已删除目录 + 命名空间约定「目录 ≠ 命名空间」横幅）、`modules/DeviceControl`（目录树 + 4 个小节标题 + 命名空间说明）、`project/overview`（项目树）、`index/index`（架构页与 DeviceControl 摘要）、`decisions/ADR-041`（加目录后续收敛说明）、`decisions/ADR-047`、`standards/StepDrivenWorkflow`、`lessons/StepDrivenWorkflowPitfalls`（3 处路径改 DeviceStateApiCore）、`guides/Namespace-Compilation`（路径 + 清单校正 + §1.1.1）、`logs/log.md`
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

**二、ADR-038 顺带合规（迁移文件内）**：成员顺序重排为 私有变量→公共变量→构造→私有函数→公共函数（原为公共函数在前）；`#region` 由单一 `SQLite 持久化` 改为按类型五分（私有变量/公共变量/构造函数/私有函数/公共函数）；类级注释改 `summary` 一行 + `remarks`；private 方法 summary 收敛到 ≤20 字。

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
2. 全库批量改链 16 处：`standards/CodeSimplification.md` 11 处（维度说明 + 附录索引）、`index/index.md` 4 处（§4.1 子表）、`decisions/ADR-038` 1 处（正文路径描述）。
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
输出 8 项：红链 / 孤儿页 / index 重复行与结构 / ADR 编号空洞与登记缺失 / 页面体积分布（含 TOC 检测）/ 内容重复度（12-gram 相似度）/ lessons 错放检测 / standards 入链统计。含**示例占位符白名单**（`[[XXX]]`、`[[引用页面]]`、`[[lessons/...]]` 等不算红链）。运行方式：在 `LLMWiki/` 下 `python tools/wiki_audit.py`。

**二、新建 `wiki/guides/` 分类（本次最大结构调整）**
- **判据确立**：`standards/` = 必须遵守的强制规范（由路由触发）；`lessons/` = 踩过什么坑（门禁）；**`guides/` = 怎么做（操作手册/参考手册/工具用法）**。已写入 `AGENTS.md` 目录结构与 index 顶部。
- **从 `lessons/` 迁出 6 页**（共 3237 行）：`AntdUI-Complete-Reference`→`guides/AntdUI-Reference`、`Project-Tools-Guide`→`guides/Project-Tools`、`Config-Data-Tools-Guide`→`guides/Config-Data-Tools`、`Namespace-Compilation-Guide`→`guides/Namespace-Compilation`、`WinForms-Designer-Guide`→`guides/WinForms-Designer`、`WinForms-UI-Threading-Guide`→`guides/WinForms-UI-Threading`。
- 全库批量重写链接，**51 个文件**更新；6 个新页加「位置说明」横幅并把 frontmatter tags 从 `教训` 改 `指导`。
- `lessons/` 由 18 页收敛为 12 页，回归纯教训定位。

**三、合并重复 / 消除孤儿**
- index 删重复行 3 处：`api/SimulationWorkflow` ×2→1、`ADR-042` ×2→1、`ADR-043` ×3→1。
- index「代码精简与权责规范」分类原为 **4 个碎片表格**，合并为 1 个主表 + 1 个 references 子表。
- 孤儿页归零：`standards/CodeSimplification-progress`（2026-08-26 进度快照，非规范）→ 归档为 `archive/CodeSimplification-Progress-20260826` 并由 `standards/CodeSimplification` 反向引用；`lessons/CodeSimplification-Scope-DesignerOnly`（范围裁定，有价）→ 由 `standards/CodeSimplification` 引用 + 登记进 index。
- index 补登此前未入索引的 5 页：4 个 `standards/references/*`、新归档页、以及**漏登记的 ADR-016**。

**四、消除冲突 / 标注过期（8 处）**
给 6 个 ADR 加统一格式「已被取代」横幅并分组到 index §7.3：
`ADR-012`（仅归属目录失效，双记录设计仍有效 → ProductFileManager）、`ADR-013`（结论不变，仅目录迁 MainDeviceControl）、`ADR-015`（中枢目录 + MonitorSupervisionWorkflow 双失效）、`ADR-032`（状态机体系随 DeviceStateMachine/ 删除）、`ADR-033`（V3 架构描述废弃，「不引入 Stateless」仍有效）、`ADR-036`（Safety 目标目录 + 文件划分双失效）。
**裁定 ADR-005 与 ADR-047 的表面冲突**：ADR-005 取图 `WaitOne(上限 5000ms)` **不违反** ADR-047「单步禁阻塞等待」红线 —— 判据「**有界 + 可失败 = 合法；无界 + 静默 = 违规**」，已双向写入 `ADR-005` 与 `standards/StepDrivenWorkflow` 红线 3。
ADR 表由平铺改为**三组**：现行有效(35) / 待决 proposed(1) / 已废弃·已被取代(8)，并加编号空洞说明（006、009 属 SunnyUI 已废弃；023、024 属 V2 已归档，不再回收）。

**五、红链归零（7 处）**
`AGENTS.md` 两处死链改指：`lessons/Log-Append-Position`→`guides/Project-Tools` §2.1、`lessons/CodeProjectRegistration`→`guides/Namespace-Compilation` §1.1（该页本就不存在，规则一直在 Namespace-Compilation 里）；同步修正 `skills/vibecoding-llmwiki/SKILL.md` 两处（**注意：该 SKILL 在 `~/.workbuddy/skills/` 与 `LLMWiki/skills/` 各有一份副本，两处都要改**）。`ADR-040` 错链 `ADR-035-IntelligentLaserDefault`→`ADR-035-LineLaserWorkflowRefactor`；`logs/log.md` 三处（`api/SimulationController`→`api/SimulationWorkflow`、`ADR-038-CodeSimplification`→代码体、`wiki/index/index.md` 的 wiki 链接→路径文本）；`archive/CodeSimplification-Progress-20260826` 两处脚本路径改代码体。

**六、检索提速**
- index 顶部新增 **⚡ 场景速查路由表**（20 行：任务 → 直接读 1~3 页 + 硬约束提示），命中即可开工，无需扫 11 张分类表。
- index 新增「目录」跳转表 + 各章节锚点。
- 6 个超大页（>600 行）加**章节导航 TOC**：`lessons/IntelligentLaser-Pitfalls`(1229)、`guides/AntdUI-Reference`(1080)、`guides/Project-Tools`(949)、`archive/V2-Architecture-Legacy`(673)、`api/ZMotionController`(625)、`modules/KUKARobot`(580)。
- index 末尾加「维护说明」：体检脚本路径 + 健康判据 + 三层分类判据。

**Phase 4 Lint 复检**：红链 **0**（占位符已白名单并单列）、孤儿页 **0**、index 重复行 **0**、ADR 登记缺失 **0**、内容重复 **0**、超大页 TOC 覆盖率 **6/6**。目录页数 152 页 / 23249 行（均值 152 行）。矛盾检测：ADR-005↔047 已显式裁定；ADR-004↔047 于 ADR-047 中裁定为补充关系。代码漂移：**本次未改代码**，`standards/StepDrivenWorkflow`（ADR-047）仍为 proposed，落地清单待用户确认。

---

## [2026-08-31 15:11:50] coding | 快捷开关面板顶部新增标题 Label「子设备状态」（ADR-045 迭代续）
- 来源：用户需求（"在panelfloatbutton最上方放入一个AntdUI.label。text为子设备状态"）
- 操作：
  1. `MainPage.cs` `InitDeviceSwitchButtons()`：面板顶部代码后置创建 `AntdUI.Label`（Text="子设备状态"、AutoSizeMode=Width、Size(100,24)、Location(2,2)，局部变量随面板销毁）；按钮起始 Y 下移 `btnTop = top + 24 + gap` 让位标题；保留用户参数 52×52/gap=15/left=2/top=2（整体面板高度需求 428px）
- 新增代码文件：无
- 修改代码文件：`AdaWeldSystem/UIDesign/ControlPage/MainPage.cs`（InitDeviceSwitchButtons 增标题创建 + 按钮 Y 起点调整）
- 新增 Wiki 页面：无
- 更新 Wiki 页面：`wiki/decisions/ADR-045-ButtonShadowDeviceSwitch.md`、`wiki/modules/UIDesign.md`、`wiki/api/MainPage.md`
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
- 更新 Wiki 页面：`wiki/decisions/ADR-045-ButtonShadowDeviceSwitch.md`、`wiki/modules/UIDesign.md`、`wiki/api/MainPage.md`
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
- 更新 Wiki 页面：`wiki/decisions/ADR-045-ButtonShadowDeviceSwitch.md`、`wiki/api/MainPage.md`、`wiki/modules/UIDesign.md`
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
- 更新 Wiki 页面：`wiki/decisions/ADR-045-ButtonShadowDeviceSwitch.md`、`wiki/api/MainPage.md`、`wiki/modules/UIDesign.md`
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
- 更新 Wiki 页面：`wiki/decisions/ADR-045-ButtonShadowDeviceSwitch.md`、`wiki/api/MainPage.md`、`wiki/modules/UIDesign.md`
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
- 更新 Wiki 页面：`wiki/modules/UIDesign.md`（快捷开关章节重写）、`wiki/api/MainPage.md`（关键方法表 + region 结构 + 设计约束）、`wiki/decisions/ADR-045-ButtonShadowDeviceSwitch.md`（追加风格迭代章节，负面项解除）、`wiki/lessons/AntdUI-Complete-Reference.md`（TooltipComponent/原生徽标/SvgDb 基础集/ButtonShadow 范式 4 条）、`wiki/index/index.md`（ADR-045 摘要更新）
- 矛盾检测：无（ADR-045 初版"纯文本+Type 配色"描述已在原页面原地更新，负面项"无 Tooltip/无图标"标注解除）

---

## [2026-08-31 11:47:19] coding | MainPage 硬件快捷开关 FloatButton→ButtonShadow（ADR-045）
- 来源：用户需求（用户指出"现在使用 floatbutton 的方式不合适，因为切换页面按钮的显示和关闭，需要事件触发，会做的很复杂。替换掉 floatbutton 使用 buttonshadow 来实现"）
- 操作：
  1. Phase 0 检索：确认 `MainPage.cs` 中 FloatButton 整块区域已被用户手动注释停用（字段残留），`FormMain.uiMillisecondTimer1_Tick` 中 `RefreshDeviceSwitchUi()` 调用同被注释；`panelfloatbutton` 面板在 Designer.cs 中仍存在；AntdUI.dll 元数据确认含 `ButtonShadow` 类型（`ButtonShadow : Button`，内建阴影）
  2. Phase 2 代码：`MainPage.cs` 删 `_floatButtonForm`/`_deviceSwitchIcons` 字段与整块注释遗骸（147 行）；新增 `_deviceButtons` 数组 + `InitDeviceSwitchButtons()`（构造函数创建 6 个 `AntdUI.ButtonShadow` 常驻 `panelfloatbutton` 面板，96×34、Y=13 居中、Round=true、默认 TTypeMini.Error）；恢复 `IsLineLaserRunning()`/`ToggleLineLaserConnection()` 为真实方法；重写 `RefreshDeviceSwitchUi()`（仅改线激光按钮 `Type` 属性，`_lastLlConnected` 去重）；`FormMain.cs` 取消定时器中 `RefreshDeviceSwitchUi()` 调用注释并更新注释文字
  3. 自审：FloatButton 残留 0、`Dispose(bool)` 重写 0、region 配对 6/6、闭包循环变量已拷贝、无 Designer.cs 修改、无新增文件（无需 .csproj 注册）
- 修改代码文件：`UIDesign/ControlPage/MainPage.cs`、`UIDesign/MainWindow/FormMain.cs`
- 新增 Wiki 页面：`decisions/ADR-045-ButtonShadowDeviceSwitch.md`
- 更新 Wiki 页面：`modules/UIDesign.md`（MainPage 快捷开关章节改写）、`wiki/index/index.md`（ADR 表新增 ADR-045 行）
- 矛盾检测：无（原 FloatButton 方案描述已在模块文档中替换为 ButtonShadow 现状，历史方案由 ADR-045 备选方案章节承载）

---

## [2026-08-31 11:06:50] refactor | 安全检查三文件合并为单一安全检查流程（ADR-044）
- 来源：用户需求（用户指出"用于安全检查的三个文件应该是合并的：安全变量值和检查地址 / 安全锁检查 / 安全流程，其实应该合并为一个安全检查流程"）
- 操作：
  1. Phase 0 检索：定位三文件 `SafetyFlow.cs`(52 行，阈值+PLC 地址) / `SafetyInterlock.cs`(212 行，FaultCategory+FaultRecord+SafetyInterlockResult+Checker) / `SafetyWorkflow.cs`(104 行，MonitorOnce 为 TODO 空桩)；**关键发现：三者零外部消费方，且 SafetyWorkflow 未继承 DeviceWorkflowBase（违反 ADR-042）**
  2. Phase 1 产出合并方案，用户拍板 4 项：配置类保留为同文件独立 `SafetyFlow` / 检查器保留为同文件工具类由流程调用 / `FaultRecord`+`FaultCategory` 迁入 `FaultRecoveryManager.cs` / `SafetyWorkflow` 继承泛型基类并接入
  3. Phase 2 代码：三文件合并为 `SafetyWorkflow.cs`（520 行，含 `SafetyWorkflowState` 枚举 + SafetyWorkflow + SafetyFlow + SafetyInterlockResult + SafetyInterlockChecker）；`SafetyWorkflow` 继承 `DeviceWorkflowBase<SafetyWorkflowState>`，重写 `MapToDeviceState`/`InitializeFlow`/`ManualOn`/`ManualOff`/`AutoRunFlow`/`CheckDeviceIOSafe`；`MonitorOnce` 由空桩实现为真实互锁检查，失败走 `EmergencyStop()` + `FaultRecoveryManager.RecordFault("Safety", ...)`；`MainDeviceWorkflow.IsRobotPoseSafe` 由 `return true` 接入 `IsSafe`；删伪异步 `CheckAsync`（Grep 确认零引用）
  4. 精简：脚本告警 42 → 1（补 `<param>/<returns>`、summary 压到 20 字内、清成员顺序、删伪异步；唯一残留 `MonitorLoop` 的 `Thread.Sleep` 属周期轮询有意例外）
  5. 顺带修复 `scripts/csharp_review.py` 本体缺陷：属性注释检查块被误置于 `_check_method_doc_quality()` 内，扫描含返回值方法的文件时抛 `NameError: name 'source' is not defined` 导致整文件扫描失败（已移回 `check_doc_comments()`）
- 删除代码文件：`MainDeviceControl/DeviceWorkflow/SafetyFlow.cs`、`MainDeviceControl/DeviceWorkflow/SafetyInterlock.cs`（csproj 同步移除 2 条，目录 11 → 9 文件）
- 修改代码文件：`MainDeviceControl/DeviceWorkflow/SafetyWorkflow.cs`（重写）、`MainDeviceControl/DeviceWorkflow/FaultRecoveryManager.cs`（迁入 FaultCategory+FaultRecord，补 `using DeviceState =` 别名）、`MainDeviceControl/DeviceWorkflow/MainDeviceWorkflow.cs`（IsRobotPoseSafe 接入）、`AdaWeldSystem.csproj`
- 修改脚本：`Vicoding管理平台/LLMWiki/scripts/csharp_review.py`
- 新增 Wiki 页面：`decisions/ADR-044-SafetyCheckConsolidation.md`、`api/SafetyWorkflow.md`
- 更新 Wiki 页面：`modules/Safety.md`（重写，原页面路径与 Standby 状态名均已过期）、`modules/DeviceControl.md`、`index/index.md`（补 ADR-043/044 与 api/SafetyWorkflow 索引条目）、`standards/CodeSimplification.md`（成员顺序 protected 判定口径 + Thread.Sleep 周期轮询例外 + 脚本缺陷说明）
- 备份：`AdaWeldSystem_backup_20260831_104743.tar.gz`
- 自查：括号 82/82、region 10/10 全配对；无新增 `Dispose(bool)`（ADR-001）；`CheckAsync` 全项目零残留；被改文件 `FaultRecoveryManager.cs` 告警数与改动前持平（8 项，均为既有）
- 矛盾检测：无。ADR-043 已被今日「权责边界治理」占用，本次沿用 **ADR-044**；ADR-036 的「三文件并存」结论已被 ADR-044 取代（其"迁 Workflow 不建子文件夹"部分仍有效）
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
- 新增 Wiki 页面：`decisions/ADR-043-WorkflowResponsibilityBoundary.md`、`standards/WorkflowResponsibilityBoundary.md`
- 更新 Wiki 页面：`index/index.md`、`api/MonitorCameraWorkflow.md`、`api/MonitorCameraRun.md`、`api/MotionControlWorkflow.md`、`api/WeldParamControlWorkflow.md`、`api/MainDeviceWorkflow.md`、`api/FormMain.md`、`modules/DeviceControl.md`、`architecture/DeviceControlArchitecture.md`、`decisions/ADR-042-WorkflowStateBaseGeneric.md`（标注其 `FlowStateSwitched` 条款已被推翻）
- 备份：`AdaWeldSystem_backup_20260831_103455.tar.gz`
- 自查：括号 8/8 文件全平衡、region 全配对（修复 `WeldParamControlWorkflow` 删事件时 region 失衡 1 处）、已删符号全项目零残留、无新增 `Dispose(bool)`（ADR-001）
- 矛盾检测：无。**注意**：ADR-042 编号已被今日「WorkflowStateBase 泛型化」占用，本次改用 **ADR-043**；ADR-042 中 `FlowStateSwitched` 相关 3 处条款已标注为被推翻

---

## [2026-08-31 10:30:08] refactor+ingest | WorkflowStateBase 泛型化：流程态机制下沉基类，机器人侧整机流程态下沉主设备（ADR-042）
- 来源：用户审查指出两个继承失效问题——①子流程（线激光等）整套自建流程态机制，`SetStep`/`MapToDeviceState`/`Step`/`StateChanged`/自有 EventArgs 五类成员在 4 个子工作流重复实现；②`WorkflowStateBase` 中的 `DeviceFlowState` 是机器人侧状态照抄，子流程语义对不上被迫新建方法。约定：共通能力继承、独有内容自建。
- **代码改动（12 文件，无新增/删除文件，csproj 无需变更）**：
  - `DeviceState/WorkflowStateBase.cs` 重写为 `WorkflowStateBase<TStep> where TStep : struct`：`Step` 属性 + `SetStep(newStep, reason)` 统一转换入口（校验→更新→四态映射→事件→日志）+ `MapToDeviceState` 抽象方法 + `ValidateTransition` 虚方法 + `OnStepChanged` 钩子 + `StateChanged` 事件；新增通用 `WorkflowStepChangedEventArgs<TStep>`。
  - `FlowState/DeviceWorkflowBase.cs` 改为 `DeviceWorkflowBase<TStep>`（四抽象生命周期 + 四公开编排不变，构造函数传初始流程态）。
  - `MainDeviceWorkflow`：继承 `DeviceWorkflowBase<MainDeviceFlowState>`；`DeviceFlowState` **更名 `MainDeviceFlowState`** 并定义于本文件；`FlowState => Step`；`FlowStateSwitched` 改由 `OnStepChanged` 转发；`IsRobotPoseSafe` 下沉为私有方法；`CheckSafetyFlow` 无调用方按死代码删除；新增整机 `MapToDeviceState`。
  - 5 个子工作流（LineLaser/Monitor/MotionControl/WeldParam/LaserWeldHead）删除重复的 `_step`/`Step`/`SetStep`/`TransitionTo`/自有 EventArgs，`MapToDeviceState` 改 `protected override`；Monitor 的 `IsValidTransition` 改为 `ValidateTransition` 重写；LaserWeldHead 补自有最小枚举。
  - UI 4 文件（FormMain/ILCamPage/MonitorCamPage/MotionControlPage）：事件处理签名替换为 `WorkflowStepChangedEventArgs<TStep>`；MonitorCamPage/MotionControlPage 补 `using ...DeviceState;`。
- **附带修复（既有编译缺陷）**：`MainDeviceWorkflow` 中 `_initializing` 字段与 `RobotManager` 属性被使用但从未声明（ADR-041 遗留），已补齐；`SafetyInterlock.CheckDevice` 参数由非泛型 `DeviceWorkflowBase` 改 `DeviceStateBase`。
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
  - 更新 `index/index.md`：架构区合并为 1 条（原 V3 两条）、新增 ADR-041、模块/API 条目重写（6 条）、归档区新增 6 条、头部新增「设备控制架构必读」导航块（含设备态四态规则与两条易误判提示）。
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
  - `MainPage.cs`：新增 `using Workflow`/`DeviceStateMachine.API`；字段 `_deviceSwitchBtns`/`_deviceTooltip`/`_deviceSwitchNames`/`_deviceSwitchIcons`/`LineLaserSwitchIndex`；`InitDeviceSwitchButtons()`（FlowLayoutPanel 入 `panelfloatbutton` + 6 圆角按钮 + Tooltip）、`RefreshDeviceSwitchUi()`(public 单一刷新入口，读 `CameraSelector.ConnectionState`)、`OnDeviceSwitchClick`/`ToggleLineLaserConnection`（线激光 `ConnectManual(LoadSavedIp)`/`DisconnectManual` + `LineLaserWorkflow.StateMachine.TryTransition`，ADR-035）；构造函数调用初始化。
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
  - `MainPage.cs`：`InitDeviceSwitchButtons`/面板 FlowLayoutPanel 方案 → `BuildFloatButtonConfig`(构建 `ConfigBtn[]`，`Round=true` 圆形、`Type`=线激光按 `CameraSelector.ConnectionState` 定 `Success`(绿)/其余 `Error`(红)、`Tooltip`=设备名、`IconSvg` 预留接口) + `InitDeviceFloatButton`(`FloatButton.open(Config(this, btns, OnDeviceFloatButtonClick){Align=TAlign.BR})`，`MainPage_Shown` 调用) + `OnDeviceFloatButtonClick`(按 `btn.Name` 分发) + `IsLineLaserConnected`/`ToggleLineLaserConnection`(线激光 `ConnectManual/DisconnectManual` + 状态机，ADR-035) + `RefreshDeviceSwitchUi`(public，状态未变跳过，变化才 `RebuildFloatButton` 重建覆盖层) + `Rebuild/CloseDeviceFloatButton`；`DisposeComponents` 释放悬浮覆盖层。
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
- 知识沉淀：[[api/MotionControlPage]]、[[api/SimulationWorkflow]]（当次记录原名 `api/SimulationController`，2026-08-28 更名）、[[lessons/SimulationC-Mode-Interruption]]、[[guides/WinForms-UI-Threading]]、[[index/index]]

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
- 更新 Wiki 页面：modules/IntelligentLaserCam、decisions/ADR-039-YinglaiDataFlow、lessons/IntelligentLaser-Pitfalls（§5.13）、wiki/index/index.md
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
- 相关 Wiki：[[lessons/IntelligentLaser-Pitfalls]] §5.12、[[decisions/ADR-039-YinglaiDataFlow]]

## [2026-08-27 09:28:00] coding | imageBox/ScottPlot 坐标系区分澄清 + 英莱点 Y 排序确认
- 来源：用户澄清（imageBox 因像素只取正值需 center+y*rate 平移；ScottPlot 直接绘原始坐标、负值如实显示，两者不必一致；英莱轮廓点默认按 Y 由小到大排列）
- 修改内容：
  1. MainPage 注释补充：ScottPlot 绘原始坐标（负值如实显示）、不做 imageBox 式平移；两者仅朝向一致、视图不重合属预期
  2. 确认英莱轮廓点默认按 Y 由小到大排列，首末锚定 = min/max
- 影响模块：UIDesign/MainPage（注释）、LLMWiki 知识库
- 相关 Wiki：[[lessons/IntelligentLaser-Pitfalls]] §5.12、[[modules/IntelligentLaserCam]]、[[decisions/ADR-039-YinglaiDataFlow]]

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
  - `wiki/decisions/ADR-040-ProgressiveStartup.md`：status 改为 rejected，加回退说明
  - `wiki/modules/UIDesign.md`：FormMain/NavPage 描述回退
  - `wiki/index/index.md`：ADR-040 条目标记「已回退」

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
  - 新建：`wiki/decisions/ADR-040-ProgressiveStartup.md`
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
- 更新 Wiki 页面：`modules/IntelligentLaserCam.md`、`modules/Workflow.md`、`api/IntelligentLaserCameraRun.md`、`lessons/IntelligentLaser-JobFlowPanel.md`、`wiki/index/index.md`
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
  1. 矛盾检测：发现 1 处 ADR 编号冲突（ADR-032 重复）—— `ADR-032-V3-Yinglai-DataFlow.md` 与 `ADR-032-UnifiedInitStateMachine.md` 编号冲突；已将前者重编号为 ADR-039（YinglaiDataFlow）并更新全部 6 处引用
  2. 孤儿页面检测：发现 1 个孤儿页面（`decisions/ADR-032-V3-Yinglai-DataFlow.md`）—— 重编号为 ADR-039 后已补入 index.md 索引
  3. 红链检测：发现 1 处红链（`lessons/IntelligentLaserSensorControl.md` 中 `decisions/ADR-038-CodeSimplification` 缺少 Standard 后缀）—— 已修复为 `decisions/ADR-038-CodeSimplificationStandard`（本行原写作 [[...]] 会被审计脚本误判为红链，2026-09-01 改为代码体）
  4. 外链完整性：扫描发现约 119 处路径引用过时/缺失（Comm S7 路径、Workflow 二级子目录、UI ViewPage→SubView、命名空间漂移等）
- **第二部分 - 代码漂移检测（Grep 方式）**：
  1. 检测到 14 项漂移（8 项文件路径/目录结构、4 项命名空间、2 项类名）
  2. 已修复 6 个 wiki 页面中的关键漂移：Comm S7 路径（`CommBase/S7Net/`→`PLC/Siemens/`）、Workflow 目录结构（Device/+Safety/）、UIDesign ViewPage→SubView、线激光相机命名空间（`LineLaserCam.` 前缀）、LLCamWorkJob→ILCamPage
  3. 剩余路径漂移为非关键引用，待后续逐步清理
- **第三部分 - 日志截断与备份**：见本次截断记录条目
- **修复统计**：修复 ADR 编号冲突 1 处、孤儿页面 1 个、红链 1 处、路径/命名空间漂移约 22 处（覆盖 6 个 wiki 页面）
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`decisions/ADR-039-YinglaiDataFlow.md`（重命名）、`index/index.md`（新增 ADR-039 条目）、`api/LineLaserWorkflow.md`、`modules/Workflow.md`、`modules/UIDesign.md`、`modules/IntelligentLaserCam.md`、`api/IntelligentLaserCameraRun.md`、`lessons/IntelligentLaserSensorControl.md`、`modules/Comm.md`、`modules/SmartRayCam.md`
- **矛盾检测**：修复后复检无新增矛盾
- **代码漂移**：关键漂移已修复，非关键漂移待后续迭代

## [2026-08-24 13:55:04] refactor | UI 状态判断精简策略总结 + ILAlgoPage/ILParamPage 冗余修复

- **策略总结**：扫描全 `UIDesign/`，整理 UI 状态精简四原则（真相源唯一/单一控制函数/统一刷新入口/集中状态标签）为新建标准页 `wiki/standards/UiStateSimplification.md`（补 ADR-038 排除的 UI 层），并在 `index.md` 代码精简规范区路由、ADR-038 相关页交叉引用。
- **冗余扫描结论**：`ILCamPage` 上轮已修；`ILAlgoPage`/`ILParamPage` 同存 `_ilConnected` 本地缓存（脱离 `IsConnected` 真相源）需修；`MotionControlPage.SetSimButtonMode`/`FormMain.UpdateDeviceStatus` 已是好范式引用；`MonitorCamPage._isMonitoring` 等本地活动标志合理保留。
- **修复**（`ILAlgoPage.cs` / `ILParamPage.cs`）：删除 `_ilConnected` 字段，连接判断与标签统一直读 `_ilCamera.IsConnected`（InitIlModule/UpdateConnLabel/LoadParams/按钮守卫），消除 stale 缓存。
- **Wiki 同步**：新建 `standards/UiStateSimplification.md`、`index.md` 路由、`ADR-038` 交叉引用、`modules/UIDesign.md` ILAlgoPage/ILParamPage 行、本日志。
- **自检**：两文件 `_ilConnected` 全清除、无外部引用；C# 7.3 合规、未新增 Dispose(bool)；备份 `AdaWeldSystem_backup_20260824_135206.tar.gz`。未在 VS 实编。

## [2026-08-24 13:37:45] refactor | ILCamPage 传感器控制精简 + 激光/传感器按钮 text 统一

- **需求（用户澄清）**：① 传感器是否启动必须用 `StCtrl.DwCameraEnable`（=`IsCameraOn()`）判断；② `SetSensor()` 才是线激光启停传感器的方式，`SetCaptureCamera()` 非线激光工作方式、舍弃；③ btnLaser/btnCaptureCamera/SyncFromHardwareCore/UpdateConnectionUiCore 在 text 与状态判断上重复多块，需精简为一个函数控制按钮状态与 text。
- **改动**（`UIDesign/TabPage/ILCamPage.cs`）：移除本地 `_isLaserOn`/`_isCameraOn` 副本（改由 `IsLaserOn()`/`IsCameraOn()` 真相源）；`btnCaptureCamera_Click` 改用 `SetSensor(!IsCameraOn())`、删 `SetCaptureCamera` 调用；`btnLaser_Click` 改用 `SetLaser(!IsLaserOn())`；`SyncFromHardwareCore`、`UpdateConnectionUiCore` 断开分支的重复 text 块收敛到新增单一函数 `UpdateLaserSensorUi()`（基于硬件真相源统一设置 btnLaser/btnCaptureCamera 的 text 与 ExtraMouseDown）。
- **Wiki**：`api/IntelligentLaserCameraRun.md` 修正 `SetSensor/SetCaptureCamera` 说明 + `DetectHardwareStatus` 返回字段（`SensorRunning` 已注释移除）；新建 `lessons/IntelligentLaserSensorControl.md`；`index.md` 教训表 + `modules/UIDesign.md` ILCamPage 行 + 本日志同步。
- **自检**：5 个受影响符号全在 ILCamPage.cs，无外部调用；`SetCaptureCamera` 仅从页面移除、后端 `LineLaserWorkflow` 仍保留合法使用；C# 7.3 合规；备份 `AdaWeldSystem_backup_20260824_133438.tar.gz`。未在 VS 实编（本环境无法编译）。

## [2026-08-24 10:39:22] refactor | ILCamPage UI 状态刷新统一入口

- 来源：用户需求（在线激光页面三个状态变更函数疑似迭代重复写，统一为一个接口）
- 依据：[[decisions/ADR-035-LineLaserWorkflowRefactor]]（状态标签唯一刷新）、[[decisions/ADR-038-CodeSimplificationStandard]]（代码精简）、[[guides/WinForms-UI-Threading]]（InvokeRequired 封送）
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

## [2026-08-21 13:58:33] refactor | 代码精简规范沉淀 + 非 UI 日志归集落地（ADR-038）
- 来源：用户需求（代码精简/注释精简/设备与通讯日志规范，并要求沉淀知识库、由 index 路由，免重复输入）
- 操作：
  1. 新建标准页 `wiki/standards/CodeSimplification.md`（唯一标准源）：四维度精简（变量→私有成员/枚举事件去重/逻辑去冗余去互锁/辅助函数归集）+ 注释三规则 + 设备/通讯日志规范
  2. 新建 `decisions/ADR-038-CodeSimplificationStandard.md`，并在 `index/index.md` 新增「代码精简规范」分类路由（免重复输入精简需求）
  3. 代码执行（非 UI，跳过 UIDesign/3rdDepend/*.bak）：全量日志调用点收敛为类内 `Log()` 私有辅助方法（241 处调用点、27 个文件），日志字符串去符号改纯文字（失败/异常/错误码/间隔/地址等）
  4. 双类/静态类文件（TCPIPComm、MotionConfig、ZMotionIO、GSDMLGenerator、RenderConfig）补/改 Log 方法，已做编译安全校验（无 Log 调用缺定义、静态类无实例方法）
- 新增代码文件：无（仅 Wiki 2 个新页面）
- 修改代码文件：MotionControl(MotionManager/ZMotion×8/MotionConfig/MotionControllerBase)、Comm(CommunicationManager/TCPIPComm/Modbus/GSDML/S7PLC/EKI/KUKARobotManager/RSI)、Workflow(MainDeviceThread/LineLaserWorkflow/LaserCamBoxTrackingWorkflow/MonitorCameraWorkflow/SimulationController/FaultRecoveryManager)、LineLaserCam×8、EmguALG、LaserWeldHead、PCLOperate、WeldParamControl、SqlLiteDatabase、DeviceStateMachine
- 新增 Wiki 页面：`standards/CodeSimplification.md`、`decisions/ADR-038-CodeSimplificationStandard.md`
- 更新 Wiki 页面：`index/index.md`（新增分类+ADR-038 行+最后更新说明）
- 矛盾检测：无
- 遗留（后续批次，需编译验证）：① 变量→私有成员提升、② 枚举/事件跨文件合并、③ 调用处冗余逻辑删除（深重构维度）；本轮聚焦④ 辅助函数归集+注释+日志（低风险行为等价变更）

---

## [2026-08-21 11:19:37] refactor | 默认初始化切正运动 + 删 Null 控制器（ADR-037）
- 来源：用户需求（初始化控制器选择需为正运动；删除不需要的控制器；加入Y轴；做CAMBOX跟踪）
- 操作：
  1. `MotionManager.Initialize()` 默认初始化正运动(ZMotion)控制器（IP 取 MotionConfigManager.Config.IpAddress，默认 192.168.0.11），不再创建空控制器
  2. 删除 `MotionControl/NullMotionController.cs` 及 csproj 注册（含 NullAxis/NullIO）；保留 SimulationController 模拟子系统
  3. `InitializeWithZMotion(ip)` 失败分支改为清空并记告警，不再回退 Null
  4. CAMBOX 跟踪随正运动句柄自动初始化（Y轴=从轴axis0，主轴=虚拟编码器轴axis8 由 KUKA PDO 驱动）
- 关联：[[decisions/ADR-037-DefaultInitZMotion]]、[[modules/MotionControl]]、[[modules/Workflow]]

## [2026-08-21 10:12:27] refactor | Safety 模块整合进 Workflow（ADR-036）
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
- 新增 Wiki：decisions/ADR-036-SafetyModuleConsolidation.md
- 更新 Wiki：modules/Workflow.md（新增安全 flow 小节 + 核心文件）、modules/Safety.md（标注整合）、wiki/index/index.md（模块行 + ADR 行）
- 矛盾检测：无（ADR-036 记录整合，与 ADR-033 阶段B/C 内容一致，仅代码位置/命名空间变更）

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
- 新增 [[decisions/ADR-035-LineLaserWorkflowRefactor]] 记录线激光工作流重构决策

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
- **Wiki 更新**：modules/IntelligentLaserCam.md、api/IntelligentLaserCameraRun.md、lessons/IntelligentLaser-Pitfalls.md（新增 §3.7 回调周期、§5.8 回调模式分流）

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
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`（新增 dwInstanceId 修复记录）、`api/IntelligentLaserCameraRun.md`（ScanRateHz 补充 dwInstanceId 注意事项）、`lessons/IntelligentLaser-Pitfalls.md`（新增 §5.7 dwInstanceId 参数陷阱）
- **矛盾检测**：无

---

## [2026-08-20 13:29:47] fix | 英莱传感器帧率运行时实时刷新 + FetchFpsModel 失败日志

- **来源**：用户反馈 2 项：① 传感器帧率（lblSenorfps）不刷新，应运行时实时获取；② 已设最高帧率但下拉仍显示标准模式
- **修复 1（传感器帧率实时刷新）**：`MillionOutlineCallback` 中新增节流式 `FetchSensorFps` 调用，每 500ms 读取一次硬件实际帧率并更新 `_scanRateHz`，使 `ScanRateHz` 属性反映运行时实时值；新增字段 `_lastSensorFpsUpdateTime` + 常量 `SensorFpsUpdateIntervalMs = 500`；UI 层 `ILCamPage.RefreshDisplay` 已读取 `ScanRateHz`，无需修改
- **修复 2（FetchFpsModel 日志）**：`FetchFpsModel()` 从静默失败（`catch { }`）改为输出 warning 日志，记录 SDK 返回码和异常信息，方便排查「帧率下拉显示不对」的根因
- **修改代码文件**：`LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`
- **新增 Wiki 页面**：无
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`、`api/IntelligentLaserCameraRun.md`（ScanRateHz 说明更新）、`lessons/IntelligentLaser-Pitfalls.md`（§5.6 补充运行时刷新策略）
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
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`、`api/IntelligentLaserCameraRun.md`、`lessons/IntelligentLaser-Pitfalls.md`（新增 §3.5 §3.6 §5.5）、`wiki/index/index.md`
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
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`（新增 UI 同步+应用按钮+回调竞态修复条目）、`api/IntelligentLaserCameraRun.md`（新增第四层防御条目）、`lessons/IntelligentLaser-Pitfalls.md`（第 6 章新增 6.6 释放竞态小节）
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
- **决策**：[[decisions/ADR-034-DisposePatternFullCoverage]] 补充「UI 类按需使用判定规则」；[[decisions/ADR-001-DisposePattern]] 补充 UI 按需语义
- **操作**：
  1. `HelixRenderForm`：还原被手动修改的 `Designer.cs`（移除 `_viewer?.Dispose()`/`elementHost1.Dispose()`/`CurrentData?.Clear()` 注入），新增 `DisposeComponents()`（释放外部 `_viewer` PointCloudViewer）+ `HandleDestroyed` 触发
  2. `MainPage`：移除无效 `~MainPage()` finalizer（事件源持引用时永不执行），新增 `DisposeComponents()`（退订 `GlobalCommData.EventInfoHandler` + `_contourCamera.ContourDataReady`）+ `HandleDestroyed` 触发
  3. `CommPage`：新增 `HandleDestroyed` → `DisposeComponents()`（修复原无调用者的释放泄漏）
  4. `MonitorCamPage`：`HandleDestroyed` 改调完整 `DisposeComponents()`（含 SensorStop/Stop）
  5. `MotionControlPage`：新增 `HandleDestroyed` → 退订 `LineLaserWorkflow.StateChanged`（修复页面销毁泄漏）
  6. `FormMain`：`FormClosed` 补退订 `LineLaserWorkflow.StateChanged`
- **保留现状**：`ILCamPage`/`LLCamWorkJob`/`LLCameraSetting` 用 HandleDestroyed 直接释放（等效正确位置，最小变更）；`ILAlgoPage`/`AlgorithmEditForm`/`ILParamPage` 等仅外部注入引用无需释放
- **修改代码文件**：`UIDesign/SubView/HelixRenderForm.cs`、`UIDesign/SubView/HelixRenderForm.Designer.cs`、`UIDesign/ControlPage/MainPage.cs`、`UIDesign/TabPage/CommPage.cs`、`UIDesign/TabPage/MonitorCamPage.cs`、`UIDesign/TabPage/MotionControlPage.cs`、`UIDesign/MainWindow/FormMain.cs`
- **更新 Wiki 页面**：`decisions/ADR-034-DisposePatternFullCoverage`、`decisions/ADR-001-DisposePattern`、`lessons/WinForms-Designer-Guide`、`modules/UIDesign`、`index`
- **矛盾检测**：无（与上一轮 ADR-034 非 UI 类迁移互补，UI 类按需使用规则明确）

---

## [2026-08-19 14:03:21] coding | Dispose 模式全覆盖：非 UI 类统一标准 IDisposable.Dispose()，DisposeComponents() 仅限 UI 设计器类

- **来源**：用户反馈（ADR-001 的 DisposeComponents() 被误用于非 UI 类，导致按 IDisposable 释放时资源不释放）
- **决策**：新增 [[decisions/ADR-034-DisposePatternFullCoverage]]；修订 [[decisions/ADR-001-DisposePattern]]（澄清适用 UI 设计器类）
- **操作**：
  1. **非 UI 类 `DisposeComponents()` → 标准 `IDisposable.Dispose()` 迁移**：`Workflow/MainDeviceThread`（+级联释放通讯管理器）、`Workflow/LineLaserWorkflow`（+释放 `_ilCamera`）、`Workflow/MonitorCameraWorkflow`（+释放 Mat）、`Workflow/LaserCamBoxTrackingWorkflow`（子组件改 `.Dispose()`）；`MotionControl/ZMotion/CamBoxTracker`、`EncoderAxis`、`RSIPositionBuffer`（合并为单一 Dispose）；`MotionControl/ZMotion/ZMotionController`（新增 Dispose：停心跳/周期/上报线程 + 释放 GCHandle + Close）
  2. **补释放入口**：`Comm/CommunicationManager`（新增 IDisposable + Dispose 释放 TcpIpComm/RobotManager/PlcManager/ModbusManager）；`Comm/CommBase/Ethernet/TcpIpComm`、`SstTcpServer`、`SstTcpClient`（新增 IDisposable + Dispose）
  3. **调用链同步**：`UIDesign/MainWindow/FormMain.cs` `MainDeviceThread.Instance.DisposeComponents()` → `.Dispose()`（唯一调用点，被调方接口变更必要联动）
  4. **保留**：UI 类 `CommPage`/`MonitorCamPage` 的 `DisposeComponents()`（合规）
  5. 释放完整性抽查：Modbus/S7/KUKA(RobotManager/RSI/EKI)/LaserWeldHead/SQLite/SensorManager/HikCameraDevice 均已有完整标准 Dispose，未改动
- **修改代码文件**：`Comm/CommunicationManager.cs`、`Comm/CommBase/Ethernet/TCPIPComm.cs`、`Workflow/MainDeviceThread.cs`、`Workflow/LineLaserWorkflow.cs`、`Workflow/MonitorCameraWorkflow.cs`、`Workflow/LaserCamBoxTrackingWorkflow.cs`、`MotionControl/ZMotion/ZMotionController.cs`、`MotionControl/ZMotion/CamBoxTracker.cs`、`MotionControl/ZMotion/EncoderAxis.cs`、`MotionControl/ZMotion/RSIPositionBuffer.cs`、`UIDesign/MainWindow/FormMain.cs`
- **新增 Wiki 页面**：`decisions/ADR-034-DisposePatternFullCoverage.md`
- **更新 Wiki 页面**：`decisions/ADR-001-DisposePattern`、`modules/Comm`、`modules/Workflow`、`modules/MotionControl`、`lessons/WinForms-Designer-Guide`、`index`
- **备份**：`AdaWeldSystem_backup_20260819_134841.tar.gz`
- **矛盾检测**：无（ADR-001 语义澄清 + ADR-034 全覆盖，与既有代码现状一致）

---

## [2026-08-19 13:18:35] fix | IDeviceStateMachine 接口补充 FaultOccurred 事件声明（修复 CS1061 编译错误）

- **来源**：Bug 修复（用户反馈编译错误）
- **操作**：
  1. Phase 0 定位根因：`FaultOccurred` 事件（V3 阶段C 故障恢复入口）仅声明于 `DeviceStateMachineBase` 基类，接口 `IDeviceStateMachine` 漏声明；`MainDeviceThread.SubscribeFault(IDeviceStateMachine sm)` 中 `sm.FaultOccurred += ...` 编译报 CS1061。
  2. Phase 2 修复：`DeviceStateMachine/API/IDeviceStateMachine.cs` 接口补充 `event EventHandler<DeviceStateChangedEventArgs> FaultOccurred;`（与基类签名一致，零破坏）。
  3. 影响半径验证：唯一直接实现者为 `DeviceStateMachineBase`，5 个派生状态机 + `MainDeviceStateMachine` 均经继承链自动满足接口。
- **修改代码文件**：`DeviceStateMachine/API/IDeviceStateMachine.cs`（+1 事件声明）
- **更新 Wiki 页面**：`modules/DeviceStateMachine`、`api/DeviceStateMachine`、`lessons/CSharp-Language-Pitfalls`（新增 §3.3 接口与基类成员不同步 → CS1061）、`index`
- **矛盾检测**：无（ADR-033 阶段C 事件入口契约补全，与既有文档一致）

---

## [2026-08-19 11:47:41] revert | 废弃 code-review-graph 代码图谱工具链（ADR-025 deprecated），回归 Grep 默认方式

- **来源**：用户反馈（code review 不好用——执行失败频繁、耗时久、经常误判）
- **决策**：[[decisions/ADR-025-CodeGraphForCodeReview]] 状态改为 `deprecated`。工作流中 Phase 0（Step 0.7/0.8）、Phase 2（Step 2.5）、Phase 4（代码漂移）的图谱强制集成全部移除，回归图谱引入前的默认方式：**Grep 定位符号 + 按行号精确读取（Read offset/limit）+ 人工多级调用追溯**。
- **操作**：
  1. `~/.workbuddy/skills/vibecoding-llmwiki/SKILL.md` 与 `LLMWiki/skills/vibecoding-llmwiki/SKILL.md`（两副本同步）：移除 Code Graph mandatory 规则，Step 0.7/0.8 改 Grep 符号定位与 Grep 引导读取，Step 2.5 改 Grep 多级追溯，Phase 4 漂移检测改 Grep 抽查，Prohibited Behaviors 第 10 条改为禁止重新引入图谱工具。
  2. `wiki/project/vibecoding-workflow.md`：Step 0.7/0.8/2.5 与 Phase 4 同步改为 Grep 默认方式，移除 Python/conda/crg_build 执行须知。
  3. `wiki/decisions/ADR-025-CodeGraphForCodeReview.md`：status accepted → deprecated，新增废弃声明。
  4. `wiki/lessons/Project-Tools-Guide.md`：§1 代码图谱整节加废弃横幅（历史参考）。
  5. `wiki/lessons/CSharp-Language-Pitfalls.md`：枚举重复定义教训中"code-review-graph 死代码误判"更新为含废弃注记。
  6. `wiki/index/index.md`：ADR-025 与两条 lessons 摘要更新为已废弃。
- **保留**：`raw/skills/AdaWeldsys_Skills/05-Tools/CodeGraph.md`（调研文档）、`raw/tools/crg_build.py`（包装脚本）作为历史参考，不再使用。
- **修改 Wiki 页面**：`decisions/ADR-025-CodeGraphForCodeReview`、`project/vibecoding-workflow`、`lessons/Project-Tools-Guide`、`lessons/CSharp-Language-Pitfalls`、`index`、`logs`。
- **修改 Skill 文件**：`vibecoding-llmwiki/SKILL.md`（双副本）。
- **矛盾检测**：无（ADR-025 已同步标废弃，所有强制引用已移除）。

---

## [2026-08-19 11:33:26] feat | Stateless 5.20.1 本地化（ADR-028）+ V3 阶段B/C 落地（安全互锁 + 故障恢复）

- **来源**：用户需求（T1 Stateless NuGet 本地化 / T2 设备状态流程更新到 V3 全目标能力）
- **T1 内容**：Stateless 5.20.1 走 ADR-028 本地化——`Stateless.dll`（167KB，纯托管 netstandard2.0，无原生/卫星依赖）拷入 `3rdDepend/`，csproj 中违规 `<PackageReference Include="Stateless">` 改为本地 `<Reference>`，清理 `obj/` NuGet 产物（project.assets.json/nuget.g.props/nuget.g.targets/dgspec.json 等）。
- **T1 决策**：按用户拍板**修改 ADR-033**——Stateless 完成离线打包（ADR-028 合规），但**不绑定任何消费代码**，「保持自定义状态机」主决策不变，作为未来评估的离线前置。
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
- **Wiki 更新**：ADR-033 更新（Stateless 本地化落地备注）、`architecture/V3-Architecture` 路线图阶段B/C 勾选、`modules/DeviceStateMachine`、`api/DeviceStateMachine`、`index`。
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
- **Wiki 更新**：[[modules/IntelligentLaserCam]] 关键事实补一条；[[api/IntelligentLaserCameraRun]] 成员表增 7 项；[[lessons/IntelligentLaser-Pitfalls]] 新增 §5 UI 与状态管理（4 条教训）；`wiki/index/index.md` 模块与 API 条目更新摘要。
- **ADR 检查**：无新决策，遵循 ADR-001（Dispose 模式）、ADR-002（C#7.3）、ADR-019（命名空间解耦）。

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
- **更新 Wiki 页面**：`modules/IntelligentLaserCam.md`、`api/IntelligentLaserCameraRun.md`、`wiki/index/index.md`
- **矛盾检测**：无

---

## [2026-08-18 11:52:08] lint | 每周例行维护：Phase 4 Lint 健康检查 + 代码漂移修复 + 日志截断备份

**来源**：每周例行维护任务（LLMWiki 知识库全量自检 + 代码漂移检测 + 日志截断）。

**Phase 4 Lint 健康检查**：
- 矛盾检测：通过（ADR-028 双文件为有意历史保留设计，旧文件 status=deprecated + superseded_by 明确指向新文件）
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
- `api/IntelligentLaserCameraRun.md`：数据链路末补充解耦说明
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
- `api/IntelligentLaserCameraRun.md`：绘图段更新居中方式
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
- `api/IntelligentLaserCameraRun.md`：更新 `ConnectCore` 描述与关键设计节
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
- `api/IntelligentLaserCameraRun.md`：IlCalibrationInfo/CalibrationInfo/CalibrationCallback

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
- `api/IntelligentLaserCameraRun.md`：数据链路流程图 + ScanRateHz/OpenSensor 描述

---

## [2026-08-17 14:29:11] fix | 英莱画面显示由轮询改为回调驱动（ContourFrameReady）
- 来源：用户审查代码发现——英莱页面用轮询刷新显示，与官方 demo 严重不符；demo 用回调更新画面，轮询只用于查激光/相机开关状态（本项目未用监控相机故无该状态）
- 操作：
  1. `LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`：新增 `event EventHandler ContourFrameReady` + 节流字段 `_lastFrameNotifyTime`；`MillionOutline` 回调成功换帧后调 `NotifyFrameReady()`（50ms 节流 ≈20fps，与 demo 一致）触发事件
  2. `UIDesign/TabPage/ILCamPage.cs`：删除 `_refreshTimer`（50ms 轮询），改订阅 `ContourFrameReady`，处理器 `OnContourFrameReady` 经 `InvokeRequired` 封送 UI 线程刷新轮廓画面/轮廓点数/分析结果；`HandleDestroyed` 退订
  3. `UIDesign/ViewPage/ILAlgoPage.cs`：删除 `_refreshTimer`（150ms 轮询），改订阅 `ContourFrameReady` 刷新实时识别结果表；`StopTimer()` 改名 `StopRefresh()`（退订事件）
  4. `UIDesign/SubView/AlgorithmEditForm.cs`：`HandleDestroyed` 调 `_ilPage.StopRefresh()`（原 StopTimer）
- 修改代码文件：IntelligentLaserCameraRun.cs、ILCamPage.cs、ILAlgoPage.cs、AlgorithmEditForm.cs
- 更新 Wiki 页面：api/IntelligentLaserCameraRun、modules/IntelligentLaserCam、wiki/index/index.md
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
- 更新 Wiki 页面：api/IntelligentLaserCameraRun、modules/IntelligentLaserCam、modules/UIDesign、wiki/index/index.md
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
- 更新 Wiki 页面：api/IntelligentLaserCameraRun（新增相机参数 vs Job 参数对比表）、modules/IntelligentLaserCam、modules/UIDesign
- 矛盾检测：无（修正了原「Job Parameter 含曝光」的错误表述）

---
## [2026-08-26 10:57:43] standards | 升级代码精简规范为详尽版并沉淀检查脚本
- 将用户新建的 C# 代码审查规范（文件书写整理 / 逻辑精简 9 类 / 函数精简 + `csharp_review.py` 单文件扫描器）并入 [[standards/CodeSimplification]]，原四维度扩展为五维度，保留项目特有设备日志规范（去符号/始末/通讯全记录）。
- 归档 `scripts/csharp_review.py`（已 py_compile 校验通过）与 `wiki/standards/references/` 下 3 个规则文件 + 工作流说明（csharp-vibecoding-review-workflow.md）。
- 更新 index「代码精简规范」分类摘要、[[decisions/ADR-038-CodeSimplificationStandard]] 加注升级记录。
- 触发约定不变：用户说"代码精简/注释精简/日志规范"即读取本页执行，无需重复输入。

---

## [2026-08-27 13:32:26] simplify | FormMain/MainPage 注释与代码精简（五维度）
- 来源：用户需求——`@skill:vibecoding-llmwiki 对formmain mainpage 做一下注释和代码精简`；范围裁定：用户明确"强制排除的是 Designer.cs"——`*.Designer.cs` 才跳过，`UIDesign/` 下非设计器 `.cs`（FormMain.cs/MainPage.cs）同样适用五维度（纠正 [[standards/CodeSimplification]]/[[decisions/ADR-038-CodeSimplificationStandard]] 原"UIDesign 除外"误读）。
- 操作（FormMain.cs）：① 新增 3 个 #region 配对（私有变量/构造函数/私有函数），成员顺序规范；② 删除死函数 `HideTreeNode()`（仅被已注释掉的 `//HideTreeNode();` 调用，Grep 全量确认零引用），并删除该注释调用；③ 7 个私有方法 XML 注释精简为 ≤20 字 summary + `<param>`：FormMain_FormClosing/InitializeSystemStatusLabel/OnMainDeviceStateChanged/UpdateSystemStatusLabel/OnWorkflowStateChanged/UpdateStatusLabel/UpdateDeviceStatus。
- 操作（MainPage.cs）：① 删除 4 个未使用字段（robotDataRefresh/laserDataRefresh/ClinkTimes/StartTest，Grep 零引用）；② 删除死函数 `ResetChartLineData()`（零调用者）；③ 内联 `LoadComponent()`（仅订阅 `GlobalCommData.EventInfoHandler`）到构造函数并删除该方法；④ 新增 5 个 #region 配对（公共变量/私有变量/构造函数/私有函数/公共函数），将 4 个 public 方法（DisposeComponents/AddContourLineChart/AddNewDataLineChart/LogAppend）归集到末尾 `公共函数` region；⑤ public + private 方法 XML 注释补全（summary + param）。
- 约束合规：未引入/重写 `Dispose(bool)`（ADR-001）；FormMain 关闭链 `FormMain_FormClosed` 显式退订单例事件 + MainDeviceThread.Dispose + LineLaserWorkflow.Dispose；MainPage 用 `DisposeComponents()` + HandleDestroyed 触发（UI 类按需，ADR-001/034）；C# 7.3 语法不变（ADR-002）。
- 检查：`scripts/csharp_review.py` 复跑——FormMain 17→5 项（0 error/0 warn/5 info），MainPage 23→2 项（0 error/0 warn/2 info）；剩余 info 为设计器绑定 handler/空 region 提示，非问题。Grep 自审：region 配对、无悬挂删除符号引用、公共签名未变。
- 修改代码文件：FormMain.cs、MainPage.cs
- 更新 Wiki 页面：standards/CodeSimplification、decisions/ADR-038-CodeSimplificationStandard、index/index.md、api/FormMain、api/MainPage
- 新增 Wiki 页面：api/FormMain、api/MainPage、lessons/CodeSimplification-Scope-DesignerOnly
- 矛盾检测：无（已同步更正标准页"UIDesign 除外"误写为"仅 *.Designer.cs 除外"）
[2026-08-28 16:38:12] lint — Phase 4 健康检查完成。修复：①7 处把架构页错标为「V3 运动控制架构」的链接描述改为「设备控制架构规范页」；②10 处正文 V3 表述去代际化（CamBoxTracker/EncoderAxis/RSIPositionBuffer/KUKARobot/LaserCamBoxTrackingWorkflow-Legacy）；③3 处陈旧状态机描述（LaserWeldHead/MotionControl/Comm）改为 MapToDeviceState 四态口径；④MonitorCam/LineLaserCam 增插 ADR-041 更新说明；⑤project/overview 目录树删除已删的 DataModels/DeviceStateMachine，改为 MainDeviceControl（15 文件），模块总数 18→17。校验：红链 5→3（余为历史占位符）、孤儿页 2（历史页）、核心 10 页双向链接全覆盖、代码漂移 0（四态枚举/4 映射/TriggerAdjustment 无参/枚举 9-8-7/工艺不入级联/Dispose(bool) 0）。
[2026-08-28 17:09:57] fix+ingest — 命名空间与 using 全量体检（vibecoding Phase 0~4）：①修复 6 个文件缺失 `using AdaWeldSystem.MainDeviceControl.DeviceState;`（DeviceWorkflow 4 个工作流 + FlowState/DeviceWorkflowBase + ILCamPage）——根因：DeviceState 枚举与子命名空间同名，兄弟命名空间内裸类型用法解析为命名空间报 CS0118；②残留清理：csproj.bak_20260828_153931 移出项目树至工作区根（Workflow/Device 仅留 SimulationController+WeldActionRecord 属 ADR-041 有意保留，非残留）；③csproj 注册 0 孤儿 0 幽灵，失效 using 0；④教训页 Namespace-Compilation-Guide 第 2 节补录 CS0118 案例与规避约定；⑤备份 AdaWeldSystem_backup_20260828_170757.tar.gz。
[2026-08-28 17:16:04] fix+lint — 体检追加发现并修复：LineLaserWorkflow.cs 行173-184 孤儿残留代码块（SetStep 事件触发片段被误留至 MapToDeviceState 后，类级别引用不存在的 oldStep 致 CS0103，末尾多余 } 提前关闭类，后续 700 行落命名空间级）——删除后词法级全项目 130 文件大括号平衡通过（GSDMLGenerator/EKICommunication/XMLfile 三处经词法状态机与人工核验均为正则剥离误报）；教训页补录「孤儿代码块检测方法：词法状态机 + region 锚点深度拓扑」。
[2026-08-28 17:29:00] refactor+ingest — Workflow/ 目录归零：①SimulationController.cs 迁入 MainDeviceControl/DeviceWorkflow/ 并更名 SimulationWorkflow（namespace→AdaWeldSystem.MainDeviceControl.DeviceWorkflow，补 using AdaWeldSystem.Workflow 取 SimTestMode；INI 文件名沿用 SimulationController.ini 保用户配置兼容）；②WeldActionRecord.cs 迁入 PCLOperate/RunFileRecord/（namespace→AdaWeldSystem.PCLOperate.RunFileRecord，与消费方 RunRecordManager 同命名空间）；③全局更名 22 处引用（LineLaser/MonitorCamera/FormMain/MotionControlPage）；④清除 2 个死 using（RunRecordManager/DataReviewPage 原经 AdaWeldSystem.Workflow 访问 WeldActionRecord）；⑤csproj 条目替换，目录 Workflow/ 删除；⑥wiki：ADR-041 增补修订记录、api/SimulationController.md 更名 SimulationWorkflow.md、modules/Workflow 第3节改写、modules/DeviceControl 目录树补入、index/ADR-017/ADR-037/MotionControl/architecture 等现在时引用更新（历史决策叙述按约定保留原名）。备份 AdaWeldSystem_backup_20260828_172346.tar.gz。
[2026-08-28 17:51:14] refactor+ingest — MainDeviceControl 二次收敛（应用户两项要求）：①Safety 解散：Safety/ 子目录删除，SafetyFlow/SafetyInterlock/FaultRecoveryManager 平铺至 DeviceWorkflow/（namespace 统一 ...DeviceWorkflow），SafetyMonitorThread 更名 SafetyWorkflow（流程一律命名 Workflow 不用 Thread，该类无外部引用更名零风险）；②WorkflowState.cs 删除：状态契约按归属内联（线激光2类型→LineLaserWorkflow.cs、监控10类型→MonitorCameraWorkflow.cs、CAMBOX3类型→MotionControlWorkflow.cs、SimTestMode→SimulationWorkflow.cs，namespace 统一 ...DeviceWorkflow）；删除零消费类型 WorkflowSignalCode/WorkflowCompletedEventArgs/WorkflowErrorAbortedEventArgs/WorkflowManualStoppedEventArgs；AdaWeldSystem.Workflow 命名空间不复存在，11 处 using 清理（10 删 1 替换）。修复过程：首版切片脚本产生重复插入与括号失衡，改用「备份还原 + 括号计数法提取 + 单次插入」重建 4 文件。终检：类型唯一定义 0 重复、词法括号全平衡（XMLfile.cs 为 verbatim 误报）、region 配对与锚点深度全通过、csproj 0 孤儿 0 幽灵。wiki：ADR-041 二次修订、ADR-027 废止横幅、modules/Workflow 墓碑页、DeviceControl 树/Safety/架构页/index 同步。备份 AdaWeldSystem_backup_20260828_174104.tar.gz。
[2026-08-31 09:11:08] fix+ingest — LineLaserWorkflow 语法错误修复（用户 VS 编译反馈）：根因=8/28 二次收敛时契约块提取器缺陷——括号深度从声明行起算，声明行无大括号致提前终止，16 个类型全部截断成无体声明（波及 LineLaser/MonitorCamera/MotionControl/SimulationWorkflow 四文件，括号平衡检查无法发现此类损伤）。修复=修正提取器（跳过声明行、首个大括号起计数加块内成员断言）后从备份 174104 整体重建四文件，恢复 UTF-8 BOM。终检：类型唯一定义零重复、枚举成员 9/8/7/4 全数核对、region 与锚点全通过、死类型零残留。教训页补录提取器两陷阱与 BOM 约定。现场备份 AdaWeldSystem_broken_20260831_090705.tar.gz。
[2026-08-31 09:35:38] fix+ingest — DeviceState 命名空间遮蔽修复（用户 VS 编译反馈 CS0118）：MainDeviceControl 子树内 7 文件（6 工作流 + FlowState/DeviceWorkflowBase）的裸 DeviceState 被同名子命名空间遮蔽，8/28 补 using 的修法对子树内文件无效（C# 解析向外走在父层先命中子命名空间即停，using 轮不到）。修复=各文件命名空间声明内部注入 using DeviceState 别名（本级优先于向外走）。子树外 UI 文件普通 using 有效不受影响。全项目冲突扫描确认 DeviceState 为唯一类型名/命名空间段名碰撞。教训页 8/28 案例已修订（子树内别名 vs 子树外 using 的区分），ADR-041 增 0831 补充。备份 AdaWeldSystem_backup_20260831_093314.tar.gz。
[2026-08-31 17:46:43] refactor+ingest — 产品生命周期记录归口（ADR-046）：①`PCLOperate/RunFileRecord/` 4 文件（RunRecordManager/RecordFrame/WeldActionRecord/SmartRayConverter）迁入用户新建的 `ProductFileManager/`，namespace→AdaWeldSystem.ProductFileManager，类名与公共 API 不变，8 消费方（WeldProcess/CameraRun/IntelligentLaserCameraRun/AlgorithmManager/DataReviewPage/FileTraceForm/HelixRenderForm/RecordConfigForm）仅改 using；PCLOperate 仅余 3DModel/DataIO/Render；csproj 4 条改路径 + 删 VS 孤儿 Folder 条目。②新建 `SqlLiteDatabase/FaultRecordManager.cs`（继承 DatabaseManagerBase，DB 迁 DataBase\FaultRecord.db，string[] 写入契约不依赖领域类型，管理器内不做 try/catch 日志对齐 ProductDatabaseManager 范式）；FaultRecoveryManager 278→231 行：删 #region SQLite 持久化（EnsureDb/_db/_dbLock/_tableReady），Persist 保留为领域侧映射+截断+失败日志，FaultCategory/FaultRecord 数据载体留原文件（ADR-044 维持）。注意：用户在 AI 实施间隙已手动在 VS 完成目录移动（mv 报 cannot stat 暴露），按「重读文件、保留用户改动」惯例接手收尾。wiki：新建 ADR-046/modules/ProductFileManager/api/FaultRecordManager，更新 modules/Safety、SqlLiteDatabase（补 SqliteCore/ 子目录实况）、PointCloudData（RunFileRecord 迁出）、api/FaultRecoveryManager、index。备份 AdaWeldSystem_backup_20260831_173658.tar.gz。
[2026-09-01 10:21:10] ingest+standards — 步骤驱动工作流标准沉淀（ADR-047，status: proposed，仅知识库，未改代码）：用户提供外部参考实现 `HonorMachineTest/PcomDeviceInterface/Work/Process/`（`StationProcess.cs` 抽象基类 + `AssemblyProcess.cs` 实现约 3000 行 100+ 步 + `MachineControlWork.cs` 常驻线程），要求研究其写法并沉淀为标准 workflow 知识库。①新建 [[standards/StepDrivenWorkflow]]：三件套（命令变量 Slot / 常驻监听线程 `while`+节拍调 `FlowProcess()` / int 执行步 `WorkStep`+`WorkStartTime`）、**三层融合表**（设备四态 ADR-041 / 阶段态枚举 `SetStep` ADR-042 / 执行步 int 新增，**阶段态是对外名片、执行步是内部游标**）、基类 6+1 契约映射到本地命名、步骤号段位规范（0/10-99/100-199/700-799/800-899/900-999）+ 步号中文映射表强制登记、单步三范式（瞬时动作/等待完成/分支派发）、失败重试零代码（`if(!…) break;` 步号不变下拍重入）、超时三步走（Alarm+记故障+跳 9xx）、可观测性排故判据表、8 条红线。②新建 [[decisions/ADR-047-StepDrivenWorkflow]]：背景=现主流程事件驱动无线程、只能看"在哪一态"看不到"卡在哪一步/卡了多久"；与既有 ADR 关系表（**补充而非推翻 ADR-004**——ADR-004 反对顺序直写、确立 switch 分派，本 ADR 仅细化分派键并补时间维度；ADR-041/042/043/044 维持）；备选方案 4 项取舍。③两处对参考实现的**明确偏离**已写入红线：单步内禁阻塞等待（`CylinderStretch` 内 while 轮询、`case 17` 的 `Thread.Sleep(500)` 本地不引入，阻塞会同时冻结超时判据与指令响应）、不引入 `LoadConfig(XmlReader)/SaveConfig(XmlWriter)`（沿用项目既有 INI 持久化）。④更新 index（「代码精简与权责规范」分类新增触发说明 + 标准页行、决策表新增 ADR-047 行）、modules/DeviceControl（「核心语义」章新增「第三层：执行步」三层表）、api/MainDeviceWorkflow（顶部加 2026-09-01 规划变更横幅，标注接收 RobotPose 链路将由「回调→直接处理」改为「回调→写命令变量→线程→执行步推进」）。⑤用户核心收益已落标准页第八章：主程序加载流程后仅凭 `WorkStep` + `(DateTime.Now - WorkStartTime)` 两个变量即可完全监控流程状态。矛盾检测：ADR-004 已在 ADR-047「与既有 ADR 的关系」显式裁定为补充关系，非冲突。孤儿页检测：新标准页由 index + ADR-047 + modules/DeviceControl + api/MainDeviceWorkflow 4 处 inbound，ADR-047 由 index + 标准页 2 处 inbound。红链：全部 `[[...]]` 指向已存在页面（standards/WorkflowResponsibilityBoundary、standards/CodeSimplification、standards/UiStateSimplification、architecture/DeviceControlArchitecture、modules/DeviceControl、api/*、lessons/*、decisions/ADR-004/041/042/043/044）。代码漂移：本次未改代码，落地清单（标准页第十章）待评审确认后实施，P0=DeviceWorkflowBase + MainDeviceWorkflow。

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
  - `api/CamBoxTracker`/`api/EncoderAxis`/`api/RSIPositionBuffer`/`api/LaserWeldHeadController`/`modules/LaserWeldHead` tags 与页首「架构版本 V2/V3」去代际化；`api/IntelligentLaserCameraRun`、`modules/IntelligentLaserCam`、`modules/UIDesign`（英莱轮廓误标 V3，实为 ADR-039 数据流）同步。
  - `guides/WinForms-UI-Threading.md` §3 去代际化，并把 `MainDeviceThread.DisposeComponents()` 更新为 `MainDeviceWorkflow.Dispose()`（ADR-041 更名 + ADR-001 释放入口）。
  - `decisions/`：ADR-030 加「当前状态 有效 + 命名澄清」横幅（本 ADR 描述的 CAMBOX 就是**当前架构本身**，V3 仅为当时叫法，防后人去找已删的 V3 架构页）；ADR-037/ADR-027/ADR-025 修正引用已删除实体的表述。
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
