---
title: "ADR-038: 机器人指令驱动步骤流（子流程禁自迁步）"
date: 2026-09-20
updated: 2026-10-30
tags: [主控, 步骤驱动, 命令表, 模拟仿真器]
status: accepted
---

# ADR-038: 机器人指令驱动步骤流（子流程禁自迁步）

## 裁定

本设备下挂机器人，主要工作由机器人指令调度。步骤迁移的唯一驱动源 = **设备主控（DeviceControlWork）消费命令**，子流程（5 个 DeviceWorkflow）**禁止自行迁移执行步跨阶段**。

## 命令驱动范式（唯一合法链路）

```
机器人指令 / IO / UI
 → ExecuteIo(IoSubPrework / IoSubWork / IoSubStop / IoSubManualStop / IoSubAlarmStop)
 → DoSubPrework / DoSubWork / DoSubStop / …
 → CascadeWeldStatus(PreWork / Working / Stopping / …)
 → 子流程 RequestWeldStatus → OnWeldStatusChanged 钩子 → AdvanceStep(阶段入口)
```

时序语义（用户裁定 2026-09-20）：
1. 机器人发 PreWork 指令 → 主控切线激光等子流程 RunStep 到 PreWork；
2. 子流程执行完成 → **写完成反馈状态**（如线激光 `IsPreWorkFeedbackDone`：数据稳定 + 进入等待步）→ 停在等待步；
3. 主控收到完成判断结果 → 反馈机器人 → **等待下一条指令**；
4. 机器人发 Work 指令 → 主控才切子流程 RunStep 到 Working。

## 红线

- **子流程不自迁步**：阶段内子步链（如 PreWork 内部 10→20→30→31）允许，跨阶段迁移（31→100、100→700）只允许由 WeldStatus 命令钩子触发。
- **行程判断唯一归属主控**（`CheckWeldProgress`）：子流程 DoWorking 不判行程、不自置 Stopping。
 - 模拟：目标 = 随机 1500~2000mm（`_simWeldLengthMm`，每次开启模拟重取），起点/目标在 Working 命令下发时锚定；
 - 真实：机器人决定焊接停止 X，协议细化后由 Work 指令携带目标（todo），现以线激光 `MaxWeldLengthMm` 配置兜底；
 - 到程 → 主控走 `DoSubStop()` 命令链下发焊接完成（原因含「焊缝行程完成」），UI 据此联动收尾。
- **WeldParam / Monitor 开始与结束由主控控制**：微周期（计算→下发 / 采集→分析）保留为其本职，但触发挂 `WeldStatus == Working` 门禁；焊接头/监控等不参与模拟的子设备由模拟停驱（IsEnable=false）。
- **模拟 = 主控内置机器人仿真器**：`SimScheduleTick` 状态机（等线激光 PreWork → 等完成反馈 → 下发 Working），由模拟测试线程每拍驱动；不一次性连发、不越权直驱子流程步骤。模拟用真实线激光但未连接时由 `StartSimulationLineLaser` 自动连接（连接失败报错退出）。
- **模拟必须走主控命令面 `DoSubWork`，禁止对子流程直发 `RequestWeldStatus(Working)`**：`DoSubWork` 内 `CascadeWeldStatus(Working)` + `BeginWeldMonitor()` + `BeginProductSession()` 三者必须同生共死。若仿真器绕过 `DoSubWork` 直驱子流程 → `BeginWeldMonitor` 不启动（行程到程永不触发 `CheckWeldProgress`/`DoSubStop`，模拟卡死）且生产会话不开（不记录）。**生产会话只能随 Working 命令开**：`StartSimulation()` 不得提前 `BeginProductSession`（否则与 `DoSubWork` 双开、且违背 ADR-037 会话随 Working 启停）。

## 违规清理记录（2026-09-20）

| 原违规 | 位置 | 处置 |
|---|---|---|
| DoWorking 判行程并自动 AdvanceStep(StepStopping) | LineLaserWorkflow | 删 `IsWeldLengthReached`/`StopByWeldLengthReached`，DoWorking 改 void；Stopping 仅经 WeldStatusTrans |
| 模拟旁路直接 AdvanceStep(StepWorking)+自置 Working | LineLaserWorkflow / MotionControlWorkflow | 收窄为命令门控（WeldStatus==Working 才迁移步），不自置 WeldStatus |
| SimAutoStartSubflows 不等反馈连发 PreWork+Working | DeviceControlWork | 改 `SimScheduleTick` 反馈驱动状态机 |
| 行程目标用线激光配置 MaxWeldLength（1000） | DeviceControlWork | 模拟改随机 1500~2000mm；真实沿用配置兜底 + 机器人协议 todo |
| 模拟 `SimScheduleTick` 直发 `RequestWeldStatus(Working)` 绕过 `DoSubWork` + `StartSimulation` 提前 `BeginProductSession` | DeviceControlWork | 仿真器收反馈后改调 `DoSubWork()`（与真实 `ExecuteIo(IoSubWork)` 等价）；删 `StartSimulation` 提前开会话，会话统一随 Working 命令开 |

## 三阶段命令驱动与阶段应答（2026-11-23 演进）

> **背景**：业主重做整机流程为「主控纯被动接受机器人命令 → 完成阶段工作后回复 → 机器人据此给下一步指令」。
> 原裁定只有「PreWork → Working 由指令驱动」一条，未定义 Home/复位阶段，也未定义「回复」这一环。

### 机器人作业循环全景（业主口径，2026-11-23 核对）

```
Home → 过渡点(可省略，本侧无动作) → 焊前请求 → 到达焊前位
     → 达到焊接点(出光) → 焊接结束点 → 焊接安全离开过渡点 → 机器人 Home →（循环）
```

| 循环节点 | 协议指令 | 主控映射 | 主控动作 |
|---|---|---|---|
| Home | `RX_HOME_POSE` | `IoReset` | 设备复位链（TA 回零+工作零位 / Y 工作零位 / 焊接头回零） |
| 过渡点（可省略） | `RX_START_SAFE_POSE` | null（坐标类仅记录） | 无动作 |
| 焊前请求 | `RX_PRE_WELD_REQUEST` | `IoStart` + `IoSubPrework` | 整机启动 + 焊前准备（TA/LA/振镜进工作模式，Y 焊前寻位） |
| 到达焊前位 | `RX_PRE_WELD_POSE` | null（载荷首个数 = 焊前位 X） | 仅记录 X（寻位到位判据） |
| 达到焊接点（出光） | `RX_WELD_START_POSE` | `IoSubWork` | 焊接启动（出光与送丝实际点由机器人控制） |
| 焊接结束点 | `RX_WELD_STOP_POSE` | null（载荷首个数 = 停止位 X） | 仅记录 X；行程监视到程后主控下发 `DoSubStop`（线激光按 `lead` 前置量提前收工 = 预停位语义） |
| 焊接安全离开过渡点 | `RX_STOP_SAFE_POSE` | `IoStop` | 整机停机 + 4 设备级联断连 |
| 回到 Home | `RX_HOME_POSE` | `IoReset` | 复位链重启（`ConnectOff` 不清 `_initialized`/`Manager.IsInitialized`，第二轮复位仍可受理） |

**闭环判据**：第二轮 Home 的复位可执行——`ConnectOff` 只置子流程 `Disconnected`，**不调 `InitializeOff`**（`Manager.Close()` 只在程序关闭时执行）⇒ 运控 `_initialized` 与 `Manager.IsInitialized` 保持 ⇒ `EnsureResetReadiness` 仍通过。

### 阶段划分与命令映射

| 阶段 | 机器人命令 | 主控动作 | 阶段完成判据 | 应答 |
|---|---|---|---|---|
| A 复位 | `RX_HOME_POSE`（到归零位） | 设备复位链 `DoResetMachine`：TA 按 `TaHomed` 区分首次回零+工作位/已回零仅工作位；Y 回工作零位；焊接头回零（LA/振镜**待实现**） | 复位链 `accepted` → 整机 `Stop` | `IsResetCompleted` |
| B 焊前准备 | `RX_PRE_WELD_REQUEST`（请求进入焊前）→ `RX_PRE_WELD_POSE`（到焊前位，带 X） | `RX_PRE_WELD_REQUEST` 同时置 `IoStart` + `IoSubPrework`：整机启动 + 焊前检查（TA/LA/振镜进工作模式，Y 焊前寻位到焊缝焊接点，ADR-114） | 寻位完成（X 到位且 Y 在容差内）→ 运控 `IsCalibrationYReady` | `IsPreWorkCompleted` |
| C 焊接 | `RX_WELD_START_POSE`（完成从焊前位到焊接起始位的移动） | 焊接启动 `DoSubWork` | 焊接启动已下发 | `IsWeldStartAcknowledged` |

### 决策

- **D1 映射**：`MapCommandToIo` 补齐三阶段映射——`RxHomePose`→`IoReset`（**原为 `IoStop` 停机，本轮改为触发设备复位**）、`RxWeldStartPose`→`IoSubWork`（**原为坐标类仅记录**）；`RxPreWeldPose`→**仍为坐标类仅记录**（载荷首个数 = 焊前位 X，仅作寻位到位判据）；`RxStopSafePose`→`IoStop` 保持不变；`RxPreWeldRequest`→`IoStart` 并**额外置 `IoSubPrework`**。
- **D1.1 PreWork 启动时机（审查修正）**：⛔ **不得**把 `RxPreWeldPose`（到达焊前位）映射为 `IoSubPrework`。寻位要「X 移动中边走边建图」（ADR-114），等机器人**到达**才下发 PreWork 则 X 已停 ⇒ 地图建不起 ⇒ 寻位 60s 超时必失败。故 PreWork 由 `RxPreWeldRequest`（请求进入焊前）启动——机器人随后才开始移动，时序正确。
- **D2 应答载体**：阶段完成以**内部应答态**（`_resetAckPending` / `_preWorkAckPending` / `_weldStartAckPending`）表达，供机器人判下一步。⛔ **对外回复指令本轮不接线**——协议码待与机器人侧确认后统一补齐（复用现有 `CommandCore.Tx*` 或新增）。
- **D3 主控不监控机器人**：到位判据一律取**机器人上报的命令**（`RxPreWeldPose` 载荷首个数 = 焊前位 X），⛔ 禁止主控轮询机器人位置推断阶段。
- **D4 真正工作自 PreWork 起**：PreWork 阶段即完成 TA/LA/振镜进工作模式与 Y 焊前寻位；`Working` 是正式出光闭环（出光与送丝实际点由机器人控制，不在主控侧）。
- **D5 自动模式动作入口**：PreWork 属自动流程，主控派发的动作是**流程组成而非手动干预**，故新增流程内入口（`MotionControlWorkflow.TaExecuteAuto` / `LaserWeldHeadWorkflow.LaAutoAuto` / `GalvoWeaveStartAuto`），⛔ 不复用手动入口（手动入口受「自动焊接中禁手动动作」门禁，PreWork 态会被拒）。
- **D6 单动作锁与运行态未就绪都不丢指令**：
  - `DispatchAction` 前一动作未结束时改为**保留 IO 供下拍重试**（原为直接丢弃）——TA 力矩建立是有限阻塞，前序动作未结束不应吞掉后续阶段命令。
  - `ScanPulseIo` 的 `requireRunning` 未满足时改为**保留 IO 供下拍重试**（原为取走后丢弃）——`IoStart` 是异步派发，紧随其后的 `IoSubPrework` 若在 Running 前到达被丢弃即断链。
  - `IsCommandPreconditionMet` 对 `IoSubPrework`/`IoSubWork` **不拒收**（原为拒收）——命令处理线程与 Running 建立之间存在时差，拒收即丢指令；运行态判据交由扫描线程的重试机制处理。
- **D7 模拟等价**：仿真器扮演机器人角色，**注入 Rx 命令到真实指令队列**（`InjectSimRobotCommand`），与真实指令同队列同处理链；⛔ 禁旁路直调 `DoSubPrework`/`DoSubWork`。
- **D8 运控步机由主控启动（审查修正）**：真实流程中 `MotionControlWorkflow.Start()` **此前无任何调用方**（唯一调用点是模拟侧），运控 `RunStep` 停在初值 0、步机空转 ⇒ 焊前寻位不可达。故 `DoStartMachine`（整机启动）统一启动运控步机（使能 → 回归标定位 → 焊前寻位 → 就绪），真实与模拟同一条路径；`Start()` 非幂等，模拟侧不再重复调用。
- **D9 运行中禁止复位**：`DoResetMachine` 补「Running 态拒绝」校验（与 `ResetMachine` 一致）——`ClearMachine` 的 `Running→NoReset` 迁移会被状态机拒绝，直接清会造成「子流程已清、整机态未变」的不一致。模拟启动链同样先停机再清态。

### 遗留

- 焊接头 **LA 机械回零未实现**：`LaserWeldHeadWorkflow.ResetProcess` 本轮只把振镜退回逻辑零位并记录待办，⛔ 不臆造 LA 回零实现。
- **对外回复指令未接线**：应答态已就位，待协议确定后补 `SendRobotCommand` 调用。

### 2026-11-23 现场复测修正（三处，模拟跑通验证）

现场日志实证「模拟注入机器人指令反复重发」，追出三处缺陷（均为「PreWork 阶段工作实际未发生」所致）：

- **D10 喂帧门禁不能只看起焊沿开关**：`_seamTrackingActive` 是**起焊沿开关**（控制 `OnSeamTrackingStart/Stop`），PreWork 阶段为 false ⇒ `OnSeamResultReady` 的 `if (!_seamTrackingActive) return;` 把**每帧都丢弃** ⇒ 地图恒空（现场「地图点 0 / 平滑跳过持续递增」）⇒ Y 拿不到焊接点目标 ⇒ 焊前寻位 60s 超时。**修**：`OnSeamResultReady` 门禁改为 `!_seamTrackingActive && !_cspPreWorkTracking`（PreWork 跟踪已建立时同样放行帧）。
- **D11 起焊沿不得清空 PreWork 建好的地图**：`OnSeamTrackingStart` 原调 `ResetTrackingForWeldStart()`（清地图 + 位姿基准），把 PreWork 期间建的引导点全丢 ⇒ 起焊瞬间地图又空，而 X 已在高速移动，来不及重建 ⇒ 跟踪失效，直接推翻 ADR-114「PreWork 提前扫后跟踪」的前提。**修**：`_cspPreWorkTracking` 为真时**不复位**跟踪算法（复用 PreWork 的地图与基准）。
- **D12 模拟不得自行启动整机**：`EnsureRunningForSimulation`/调度步 6 自行 `DoStartMachine()` 进 Running ⇒ 随后注入的 `RX_PRE_WELD_REQUEST`（映射 `IoStart`，前置要求 Stop 态）被**拒收** ⇒ 命令从未入队 ⇒ 连带 `IoSubPrework` 也未置位 ⇒ PreWork 工作从未下发（现场「拒收 整机非 Stop 态 当前 Running」每秒一次）。**修**：① 模拟步 6 不自行启动，整机启动交给注入的 `RX_PRE_WELD_REQUEST`（真实/模拟同一条命令链）；② `IoStart` 前置放宽为「Stop 或 Running 均放行」（`DoStartMachine` 已幂等，重复置位无害；真实流程里整机可能已启动）。
- **D13 焊前准备幂等守卫用运控态**：同一会话内 `RX_PRE_WELD_REQUEST` 可能被重复派发（限频重试兜底），`DoSubPrework` 须幂等——重复执行会清地图、打断寻位、重复切 TA 力矩模式。判据取**运控已在 PreWork 态**（`DoSubPrework` 的 `CascadeWeldStatus` 会切它）；⛔ 不用线激光态：模拟侧子流程会提前把线激光切到 PreWork，拿它当判据会让焊前准备被误跳过。
- **D14 模拟步序重排**：`5`（注入 Home）→ `6`（等复位完成，启动位姿时钟 + 子流程）→ `7`（注入 `RX_PRE_WELD_REQUEST`，同步启动寻位段 X 推进）→ `8`（等整机 Running + 线激光 PreWork）→ `20`（等 PreWork 反馈）→ `21`（注入 `RX_PRE_WELD_POSE` 记录 X）→ `22`…→ `25`（等焊接启动应答）→ `30`。


## 关联

- 步骤驱动机制基座：[[decisions/ADR-035-RawDesignRefinement20260903]]（C6：RunStep + bool 推进）
- 模拟红线沿革：[[decisions/ADR-032-SimulationTestRedesign]]（ADR-038 修订其「模拟跳过 PreWork」：线激光现走真实 PreWork 链路 + 自动连接）
- 记录生命周期：[[decisions/ADR-037-ProductProductionRecordLifecycle]]

## 背景

（待补：本决策要解决什么问题）

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 后果

### 正面
- （待补）

### 负面
- （待补）

## 相关页面

- [[decisions/ADR-Index]]
