---
title: CodeMap — 代码地图总览（代码记忆 + 主干依附）
date: 2026-10-08
updated: 2026-11-17
tags: [代码地图, 索引, 架构, Phase0, 代码记忆, 依附关系]
status: accepted
---

# CodeMap — 代码地图总览

> **一句话**：本页 = **一页可读的代码记忆**。先读这里的「功能域记忆卡」建立代码与依附的心智模型；要逐文件定位再查 [[architecture/CodeMap-Files]]（详表，166 文件 / 49 命名空间）。
> **使用纪律（强制）**：Phase 0 先读本页定位，**命中即直接读对应代码块**（Step 0.7），⛔ **不得一上来全项目 Grep**。只有进入 Phase 2 编码、需要确认具体调用点时，才扫对应文件/目录。详见 [[rules/KR-003-No-Skipping-Query]] 与 [[rules/KR-009-Grep-Default]]。
> **裁决顺序**：原档 > 架构页 > 源码注释；本表是导航层，不覆盖 ADR 结论。

## 章节导航

- [全局统计](#全局统计)
- [一、代码记忆卡（按功能域，含主干依附）](#一代码记忆卡按功能域含主干依附)
- [二、需求 → 代码落点速查](#二需求--代码落点速查)
- [三、易踩的定位陷阱](#三易踩的定位陷阱)
- [四、逐文件详表指针](#四逐文件详表指针)

---

## 全局统计

- 源码文件（`.cs`，不含 Designer）：**166** 个 / 49 命名空间（详表见 [[architecture/CodeMap-Files]]）
- 图例：`⛔` 死代码/无调用方 · `⚠️` 占位/待扩展 · `📄` 同文件多职责
- **0 消费者 ≠ 死成员**：标注 ⛔ 时删除前仍须确认非横切载体（日志标签/序列化键/权限标识/DI 钩子）

---

## 一、代码记忆卡（按功能域，含主干依附）

> **怎么读**：每卡一行「入口 → 流程 → Manager → 设备」= 主干调用方向（箭头 = 调用/依赖）。
> 这些是当前源码事实（经 ADR-093/094 分层裁定 + Grep 实证），不是推测。**改代码前先确认本卡，改完若主干变了须同步更新本页**（Phase 3.6）。
> **不记全部调用**——只记主干；逐文件/完整依赖查 [[architecture/CodeMap-Files]] 与 Step 0.7 Grep。

### 卡 1 · 设备初始化与状态机（整机编排）

```
FormMain.Show (UI)
  → DeviceControlWork.InitializeMachine / InitializeMachineTick   [主控编排]
    → 5 模组 workflow.ConnectOn (激光头/运控/线激光/监控/机器人)
    → CommWork → CommunicationManager.InitializeRobotComm + ConnectRobot
    → FinishInitialization → EnsureCommandWorkStarted（初始化结束后才启通讯线程）
  → DeviceStatusWork（IO 轮询 / 急停 / 状态反射）→ 每拍调 DeviceControlWork.Tick 族
状态写入唯一口：SetState / SetWeldStatus / SetStatus；汇总 = RecordInitOutcome
```
- 入口文件：`MainDeviceControl/DeviceControlWork.cs` · `DeviceStatusWork.cs`
- Wiki：[[api/DeviceControlWork]] · [[modules/DeviceControl]] · [[decisions/ADR-099-init-reset-separation]] · [[decisions/ADR-107-init-phase-reconnect-gate]]

### 卡 2 · 通讯（RSI 唯一机器人通道 + 日志双通道）

```
指令线程 CommCommandWork → CommunicationManager.EnsureRobotChannelHealthy（自愈重连，初始化后才启）
  → KukaRsiComm.Start（UDP 监听 + 收/发线程）→ RsiComm_DataReceived
    → CommunicationManager.RobotDataReceived → DeviceControlWork.OnRobotDataReceived（位姿/指令）
下行：DeviceControlWork.SendRobotCommand → CommunicationManager.SendRobotCommand → RsiComm.SetTxCommand
日志：ShowLog→MachineLog(系统日志)；ShowCommLogForView→TcpMessageLog+FilebackupPage；ShowCommunicationLog→报文
```
- 入口文件：`Comm/Communication/CommunicationManager.cs` · `Implementations/KukaRsiComm.cs` · `Comm/SystemComm/SystemComm.cs`
- Wiki：[[api/CommunicationManager]] · [[api/GlobalCommData]] · [[decisions/ADR-074-RsiNumericProtocolImplementation]] · [[decisions/ADR-106-comm-log-view-channel]]

### 卡 3 · 运控（Y / TA 两轴，无 LA 轴）

```
UI ProcessControlPage → MotionControlWorkflow（应用层动作唯一实现，六指令 + 门禁）
  → MontionManager（持轴对象 / 按轴门禁 / 单飞 / 到位等待 / 原始状态摘要）
    → DeltaMontionAxis（使能/移动/回零/扭矩/状态字）→ Native/ EtherCAT_DLL（P/Invoke）
UI SystemControlPage → MotionControlWorkflow 三入口（手动轴操作，后台执行 + 执行消息）
  → TryManualAxisOperation（非阻塞下发）· TryMoveAxisToTarget（绝对移动等到位）· TryHomeAxisWithWait（回零等确认）
LA 对焦 ≠ 运控轴：走 WeldHeadSlaveDevice 从站 OD（0x7000/0x6020）
```
- 入口文件：`MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` · `MotionControl/MontionManager.cs` · `DeltaEtherCAT/DeltaMontionAxis.cs` · `UIDesign/TabPage/SystemControlPage.cs`
- Wiki：[[api/MotionControlWorkflow]] · [[api/MontionManager]] · [[decisions/ADR-093-FlowTimeoutConfigAndLayering]]（架构归属硬约束） · [[decisions/ADR-094-ta-single-entry]]（TA 单入口） · [[decisions/ADR-073-AxisControlUnifiedMontionManager]]（手动轴操作唯一入口）
- ⛔ 手动回零与复位回零共用 `TryHomeAxisWithWait`（「已回零」结论**不区分来源**）
- ⛔ 手动移动禁走阻塞版 `MoveTo`/`StepMove`（UI 线程会冻结）→ 走 `MoveToNoBlock`/`StepMoveNoBlock`
- ⛔ **手动动作禁入闸门**：自动焊接流程在跑（`DeviceControlWork.IsAutoWeldingRunning`）⇒ 拒绝轴/焊接头一切手动动作；⛔ 停止类永远放行

### 卡 4 · 焊接工艺参数与自适应

```
LineLaserWorkflow（缝宽/特征点）→ WeldParamManager（工艺真相源 + 位姿喂入）
  → WeldParamControlWorkflow（功率/送丝/速度/摆幅计算）→ WeldAlgorithmsConfig + 分段表(AutoParamHelper)
    → CommunicationManager.UpdateRobotWeldParams → RSI 回复具名元素
焊参源：WeldParamManager.CurrentRobotX 与入图键同源（CSP 查图 X，D21）
```
- 入口文件：`WeldParamControl/WeldParamManager.cs` · `DeviceWorkflow/WeldParamControlWorkflow.cs`
- Wiki：[[api/WeldParamManager]] · [[modules/WeldParamControl]] · [[decisions/ADR-042-SeamTrackingConsolidated]]

### 卡 5 · 视觉算法（EmguALG 五层）

```
Workflow 检测直调 AlgorithmManager.Instance.Detect*（对中/质量/线激光轮廓）
  → EmguALG.Core / RealtimeMonitor(WireFeedDistance, WeldQuality) / LineLaserContour
    → 结果走 IResultStore 轮询（UI 取缓存），事件只低频状态灯
相机硬件：LineLaserManager / MonitorCamManager（Manager 唯一入口）→ 英莱/海康实现
```
- 入口文件：`EmguALG/Manager/AlgorithmManager.cs` · `LineLaserCam/LineLaserManager.cs` · `MonitorCam/MonitorCamManager.cs`
- Wiki：[[api/AlgorithmManager]] · [[modules/EmguALG]] · [[modules/LineLaserCam]] · [[modules/MonitorCam]]

### 卡 6 · UI 页面与权限

```
MainPage（主界面日志/状态/曲线）· ProcessControlPage / SystemControlPage（工艺/系统设置）
  · FilebackupPage（通讯配置+调试，含 CommLogViewEvent 显示）· DataReviewerPage（追溯）
UI 只查询/发起调用，不持轴对象、不直连硬件；连接/断开经 workflow 门控 TryPassPageAction
权限：PermissionLevel.GetDisplayName/IsEngineerOrAbove；SetOperateLevel 唯一写入口 + 广播
刷新纪律：⛔ 禁跨线程刷新（Task.Run+BeginInvoke）· ⛔ 禁每拍整表 Binding · 刷新只做显示信息，按钮管控与状态判定事件驱动（ADR-075 D24）
按钮管控作用域：⛔ 按钮禁用按**电机/设备分组**各自独立（一个电机的在途操作不得牵连其它电机）· ⛔ 停止键永远可用 · ⛔ 点动键不进禁用模型（ADR-075 D32）
决策治理：新建 ADR 前必过 `tools/adr_new.py check`（落地实体符号 Jaccard ≥0.40 即拦截）· 同主题走 merge 不新建 · ADR 被并入他页时旧号在 ADR-Index 留指针行不重排（ADR-Index 废止留档不变式）
```
- 入口文件：`UIDesign/ControlPage/MainPage.cs` · `UIDesign/TabPage/*.cs` · `Comm/SystemComm/PermissionLevel.cs`
- Wiki：[[api/FormMain]] · [[api/FilebackupPage]] · [[decisions/ADR-105-page-action-workflow-and-permission-gate]]

### 分层依附铁律（跨卡通用）

| 层 | 可依赖 | ⛔ 禁止 |
|---|---|---|
| 轴类 `DeltaEtherCAT/` | Native / IMotion | 工艺语义（Auto/Break/Pose） |
| `MontionManager` | 轴类 + 配置 | 角色级动作分发、整机初始化叙述 |
| `*_Workflow` | Manager + 轴类（应用层封装） | 绕过轴类的寄存器时序 |
| UI | Workflow / Manager（发起+读摘要） | 持轴对象、解析状态字 |
| Comm / ProductFile | 中立配置快照 `DeviceWaitSettings` | 反向依赖运控命名空间（ADR-093） |

---

## 二、需求 → 代码落点速查

> Phase 1 规划时先查此表；详细逐文件定位见 [[architecture/CodeMap-Files]]。现行状态以代码为准，历史沿革见 `LLMWiki/logs/INDEX.md` 与各 ADR 页。

| 需求域 | 代码落点 | Wiki |
|---|---|---|
| 主页面 折线图/状态栏/模组 | `UIDesign/ControlPage/MainPage.cs`（RefreshParamCharts / ApplyDeviceStatus / RefreshDeviceSwitchUi） | [[api/MainPage]] |
| 数据追溯 列表/图表 | `UIDesign/ControlPage/DataReviewerPage.cs`（InitSeriesGroups / RebuildChartDatasets / Datashow） | [[api/DataReviewerPage]] |
| 工艺设置 / 系统设置 | `UIDesign/TabPage/ProcessControlPage.cs` · `SystemControlPage.cs`（各 3 个内联 TabPage） | [[api/ProcessControlPage]] · [[api/SystemControlPage]] |
| TA 力矩 / LA 对焦 / 振镜 | `DeltaMontionAxis.SetTorque` · `WeldHeadSlaveDevice.cs`（0x7000/0x6020 / 0x7010）· `LaserWeldHeadWorkflow` | [[modules/MotionControl]] |
| 光丝对中 / 剪丝 | `EmguALG/Core/ImageAlgorithm.DetectPreWeldAlignment` · `WireFeedDistance/` · `CommandCore.TxCutWire` | [[api/AlgorithmManager]] |
| 焊接回放 | `MonitorCamPage.cs`（LoadPlaybackRange / PlayTimer_Tick）· `MonitorCamManager.StartRecord` | [[modules/MonitorCam]] |
| 温控 | `WeldHeadSlaveDevice.ReadTemperature` · `LaserWeldHeadWorkflow` 订阅 | [[api/LaserWeldHeadWorkflow]] |
| 接头 20 类 / 摆幅表 | `IntelligentLaserCam.cs` · `WeldParamData.AutoParam` · `AutoParamHelper`（七列） | [[api/IntelligentLaserCam]] |
| 记录 Schema / 曲线导入 | `WeldParamControlRecord.cs`（20 字段）· `RecordFileStore.cs` · `TaLaCurveConfig.ImportFromCsv` | [[api/ProductFileRecordManager]] |
| 配置读写 / 权限 | `FileOperate/XdocumentReaderWriter.cs` · `INIFile.cs` · `PermissionLevel.cs` | [[guides/Config-Data-Tools]] · [[api/GlobalCommData]] |
| 通讯日志双通道 | `SystemComm.ShowLog` / `ShowCommLogForView` / `ShowCommunicationLog` · `FilebackupPage` 订阅 | [[decisions/ADR-106-comm-log-view-channel]] |

---

## 三、易踩的定位陷阱

| 错误判断 | 实际 | 教训 |
|---|---|---|
| `LineLaserSeamResult` 0 命中=缺失 | 存在，是 `struct`（`LineLaserCam/ILineLaser/LineLaserEventArgs.cs`） | Grep `class\s+X` 漏 struct；先分 class/struct/interface |
| `MontionConfigForm` 不存在 | 轴配置 UI 是 `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs`（UserControl） | 找 UI 扫 `UIDesign/` 全部子目录 |
| 「光丝对中未实现」 | 有两套：在用套出像素、另一套出 mm 无消费者 | 区分「无代码」与「有代码未接线」 |
| workflow 的 UI 在 `MainDeviceControl` | 业务在 `MainDeviceControl/DeviceWorkflow/`，UI 在 `UIDesign/TabPage/` | 业务逻辑与 UI 分目录 |
| 振镜走运控轴 | 走从站 OD（0x7010），ADR-030 已裁定 | 硬件归属先查 ADR |
| `MotorState?` 违反 ADR-001 | `MotorState` 是 struct，`?` = Nullable，C# 7.3 合法 | 判可空前先分 class/struct |
| `ProductFileControl/Records/*` 命名空间违规 | ADR-005 §3 例外二：该目录扁平 | 查命名空间先读 ADR-005 例外表 |
| UI 直调 `MoveTo`/`HomeAxis` 违规 | `MontionManager.Instance.MoveTo` 等正是规定路径 | 区分 `axis.AbsMove()` 与 Manager 门面 |

---

## 四、逐文件详表指针

- [[architecture/CodeMap-Files]] —— 49 命名空间 / 166 文件的完整表（职责一句话 + 状态标记 + 沿革存档 + 工程约束 + 分层判据）。
- 本页不重复逐文件信息；需要「某文件在哪个命名空间、职责、是否 ⛔/⚠️」时查详表。
- 详表路径失效 = 知识漂移：Phase 4.2 按 `os.path.exists` 逐条抽查（非文件名 grep）。

## 相关页面

- [[architecture/CodeMap-Files]]
- [[architecture/DeviceControlArchitecture]]
- [[project/vibecoding-workflow]]
- [[rules/KR-003-No-Skipping-Query]] · [[rules/KR-009-Grep-Default]]
