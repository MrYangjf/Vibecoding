---
title: DeviceControlWork API 参考（整机主控 · 主设备运行态 MainDeviceStatus）
date: 2026-09-04
tags: [API, 工作流, 主控, 上电初始化, 机器人交互, 主设备运行态, 模拟, DeviceControlWork, ADR-034, ADR-020, ADR-032]
source: AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs
---

# DeviceControlWork API 参考

> **本页述 `DeviceControlWork`（单例，整机运行主控）**，见 [[decisions/ADR-013-ThreeStateModelRefactor]]。
> 主设备对外状态为 **运行态 `MainDeviceStatus`**（6 态：Running/Alarm/EStop/Stop/NoReset/Reseting），由 `SetStatus(...)` 单一入口写入，禁手工赋值。
>
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs`（**直接挂在 `MainDeviceControl/` 下，不在 `DeviceWorkflow/` 子目录**）
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：**独立管控类，不继承 `DeviceWorkflowBase`/`DeviceStateBase`**（原档明确）。
> 架构背景见 [[architecture/DeviceControlArchitecture]] 第 7 章。

## 章节导航

- [落地状态（ADR-020 批次 0~3 + 4.4）](#-2026-09-04-落地状态adr-020-批次-03--44)
- [2026-09-23 更新（ADR-041/063）](#-2026-09-23-更新adr-041063初始化步驱动--焊接启动门控--指令前置条件)
- [光丝对中消费与剪丝回检](#-2026-10-09-光丝对中消费与剪丝回检f-7f-8f-9--decisionsadr-058-wirealignmillimeterandcutwirechain)
- [核心类](#核心类)
- [常驻线程（7 条 + 1 条按需模拟线程）](#常驻线程7-条--1-条按需模拟线程)
- [主设备运行态 MainDeviceStatus（6 态）](#主设备运行态-maindevicestatus6-态)
- [上电初始化：5 步同步顺序执行](#上电初始化5-步同步顺序执行)
- [关键边界：机器人/PLC 连接不属于本类](#关键边界机器人plc-连接不属于本类)
- [级联范围](#级联范围)
- [模拟模式 API](#模拟模式-api原-simulationworkflow-已删除归并2026-09-17-adr-032-统一化)
- [模拟测试自动终止契约](#模拟测试自动终止契约2026-09-20decisionsadr-039-simulationtestautoterminationandrecordcacherelease)
- [生产会话与产品记录](#生产会话与产品记录2026-09-20-新增decisionsadr-037-productproductionrecordlifecycle)
- [模拟轨迹记录器（已删除）](#模拟轨迹记录器-simtrajectoryrecorder--2026-09-20-已删除并入记录模块)
- [遗留待办（批次 4）](#遗留待办-todo-占位属批次-4-未落地部分)
- [UI 接入](#ui-接入)
- [虚拟 IO 层](#虚拟-io-层2026-09-04-新增原档20260904-2)
- [查询与参数命令](#查询与参数命令2026-09-04-新增原档-104--105)
- [预检失败整机通路](#预检失败整机通路2026-09-04-新增原档-42--9)
- [对中偏差数据中枢](#对中偏差数据中枢2026-09-04-新增原档-745)
- [遗留待办（todo 清单）](#遗留待办todo-清单)
- [模拟启动结构](#模拟启动结构2026-09-22-精简)
- [关联](#关联)
- [初始化完成统一使能接入](#初始化完成统一使能接入2026-11-04)
- [初始化第3步修正](#初始化第3步修正2026-11-05adr-082-演进)

## ✅ 2026-09-04 落地状态（ADR-020 批次 0~3 + 4.4）

原档 `主控设计.xlsx` R013 定义的 **7 条常驻线程 + 9 个公共方法 + 11 类私有方法已全部落地**：

| 落地项 | 内容 |
|---|---|
| 7 条常驻线程 | 5 条模组工作线程 + `thHeartInspectWork`（心跳）+ `thCommCommandWork`（指令交互） |
| 9 个公共方法 | `MachineFlowWorkOpen` / `MachineCommandWorkOpen` / `InitializeMachine` / `ClearMachine` / `ResetMachine` / `StartMachine` / `ClearAlarm` / `EstopMachine` / `EstopCancel` |
| 私有方法 | `CommWork` / `OnCommRecived` / `CommCommandWork` / `MachineStatusTrans` / `WeldStatusTrans` + 5 个 `XxxWork()` 循环体 |
| 双份状态快照 | 私有 `Current` / `Last`；公共只读 `Status` 返回 `Current` |
| 四个标志位 | `IsReseting` / `IsWorking` / `IsAlarmstop`(public) / `IsCloseWork` |

**已清除的旧机制**（grep 全项目 0 残留）：

- ❌ 内部执行步机制 `_workStep` / `WorkStep` / `WorkStepName` / `GoStep` / `FailFlow` / `GetStepName` —— 按 §2「独立管控类的步机制同源约束」**禁止**自建与基类 `RunStep` 平行的步机制，业务状态链改由 `MainDeviceStatus` 表达
- ❌ 命令三槽 `_pendingPose` / `_pendingCommand` / `_pendingAbort` → ✅ `Queue<string>` + `CommandCore` const string
- ❌ `IsRobotPoseSafe` → ✅ 直接读 `DeviceStatusWork.Instance.IsSafe`
- ❌ `RobotPose` / `RobotCommand` / `DeviceCommand` / `SignalCode` 枚举 → ✅ [[api/CommandCore]]
- ❌ 单条 `RunLoop` / `BeatMs`

> ⚠️ **真编译待 Visual Studio**：沙盒无 C# 编译器，以上为静态自检结论（括号配对 / region 配对 / 抽象契约覆盖 / 跨类符号存在性 / 禁用符号残留，5 项全绿）。
> 剩余 `// todo` 见文末「遗留待办」。

## ✅ 2026-09-23 更新（ADR-041/063：初始化步驱动 + 焊接启动门控 + 指令前置条件）

| 变更 | 内容 |
|---|---|
| `DoInitializeMachine` | 线性阻塞链 → **受理制**（置首步 `_initStep=10` 即返回，非阻塞）；步驱动由 `InitializeMachineTick` 承担（IOWork 每拍调用）：10 机器人通讯 → 12 运控 → 14 焊接头 → 20/21 线激光受理/等待 → 30/31 监控相机受理/等待 → 40 聚合判定；等待小步按拍轮询 `ConnectSettled`（false→true）或超时放行（10s，步进入时刻起算） |
| ⛔ 已删除 | `WaitChildConnected`（`Thread.Sleep` 轮询等连接——曾阻塞 thIOWork 致 IO 刷新停摆）、`IsInitAborted`（被 `IsInitPreempted`+就地日志取代）、`WaitChildPollMs` |
| `DoSubWork`（焊接启动） | **受理制门控**：`IsSubWorkGateOpen()`（仅「运控 PreWork 且 `!IsCalibrationYReady`」关门）不过 → `_subWorkPending` 挂起；`CheckSubWorkPending` 由 5 条模组线程每拍锁内幂等问询，就绪补执行 / ErrorAborted 弃单 / 停止·急停·清状态链清挂起标志；等待期 2s 限频告警 |
| `SimScheduleTick`（模拟） | 步号 0/1 → **10/20/21/22/30** 与主设备同构（⚠️ 2026-09-23 ADR-043 补下发参数步）：10 等线激光进 PreWork → 20 等反馈（变量 false→true）→ 21 门控等待（与真实 `IoSubWork` 同一扇门），门开先 `DoSubPrework()`（级联 PreWork + 焊前预置播种 = 预焊接点，真实 `IoSubPrework` 同构）→ 22 `DoSubWork()`（start，生产会话开启）→ 30 焊接中；`EnableSimulation` 复位 `_simSchedStep=10` |
| `CommCommandWork` | 指令转换后置位前增 **`IsCommandPreconditionMet`** 前置条件问询：`IoStart` 需整机 Stop 且无模组 ErrorAborted；`IoStop` 需整机 Running；不满足拒收留痕 |

---

## ✅ 2026-10-09 光丝对中消费与剪丝回检（F-7/F-8/F-9 · [[decisions/ADR-058-WireAlignMillimeterAndCutWireChain]]）

| 成员 | 签名 | 说明 |
|---|---|---|
| `MonitorAlignTick()` | `void` | 由 `DeviceStatusWork.IOWork` 每拍调用（ADR-041 非阻塞）：Y 向三级报警（黄灯限频 / 红灯 `ReportAlarm` 边沿、回限内 `ReportAlarmCleared`）+ X 补偿刷新 + 剪丝回检循环 |
| `ComposeWireFeedSpeed(double)` | `double` | **送丝指令唯一组装点**（F-9 耦合防冲突）：工艺速度 + X 补偿 ×`WIRE_FEED_COMP_GAIN`，钳 ≥0（送丝机只前进）；`SendToRobot` 与剪丝 T12 同点消费 |
| `WireFeedCompensation` | `double`（只读） | 当前 X 向送丝补偿量（mm） |
| `SendCutWireRequest(bool)` | `private` | RSI `CutWire` 元素置位/复位（经 `CommunicationManager.UpdateRobotWeldParams`，唯一路径） |
| `ApplySpotAlignCompensation()` | `void` | 光丝对中偏差→振镜中心微调（F-4；**默认关闭** `GALVO_AUTO_CENTER_COMP=false` 满足需求 34 仅监控；开启后 `OffsetX/Y × PixelMmScale × 增益` 交 `ApplyGalvoCenterOffset` 单写口，[[decisions/ADR-059-P3TailGalvoAndJointParam]]） |

- 剪丝回检循环：异常（`MonitorResult.WireAnomalyDetected`）→ T13 置位 → **200 拍（10s）超时兜底复位** → 回逻辑1 重检 → 仍在异常进入下一循环；**上限 3 次**降级报警转人工（`_cutWireDegraded` 锁存，异常清除复位）。
- 数据源：`AlignDatum`（= `MonitorCameraWorkflow.LastResult`，含 `Grade`/`LateralDevMm`/`WireStickoutDeviation`/`WireAnomaly*`）。

## 核心类

```csharp
public class DeviceControlWork : IDisposable
{
    // 单例访问（Lazy<T>）
    public static DeviceControlWork Instance { get; }

    // 主设备运行态（6 态，过程状态）
    public MainDeviceStatus Status { get; }                 // = 私有 Current 快照
    public event EventHandler<MainDeviceStatusChangedEventArgs> StatusChanged;  // OldStatus/NewStatus/Reason/Timestamp

    // 可观测
    public bool IsWelding { get; }            // Status == Running && IsWorking
    public bool IsAlarmstop { get; set; }     // 供状态层读写（沿用参考实现 MachineStatusWork）
    public bool IsRobotOnline { get; }        // 由心跳线程刷新
    public RobotHeartbeatLevel HeartbeatLevel { get; }  // H0~H4，阶段 6
    public bool IsShuttingDown { get; }       // 关闭进行中（阶段 5 / ADR-101）

    // ---- §7.5 九个公共方法 ----
    public void MachineFlowWorkOpen();        // 实例化 5 条模组线程并 Start（幂等）
    public void MachineCommandWorkOpen();     // 实例化 2 条通讯线程并 Start（幂等）
    public void MachineFlowWorkClose();       // 只置 IsCloseWork，不 Abort 线程
    public void MachineCommandWorkClose();    // 只置 _commCloseWork，停通讯不连停模组（ADR-101）
    public bool InitializeMachine();          // 置 _initAccepted + 拉起 IO 线程 + 置 IoInit；模组/指令线程延后到初始化出结果（ADR-107 演进）
    public void ClearMachine();                // 全部 ClearStatus + 强制 NoReset
    public bool ResetMachine();               // 单次 Task：NoReset → Reseting → Stop
    public bool StartMachine();               // 只切 Stop → Running（真正执行靠常驻线程）
    public void StopMachine();
    public bool ClearAlarm();                 // 依 Last 回落 Stop / NoReset
    public void EstopMachine(string reason);  // ⚠️ 旧名 EStopMachine 已改名
    public void EstopCancel();                // ⚠️ 旧名 EStopCancel 已改名
    public void EmergencyStop();
    public void ReportAlarm(string reason);
    public void ReportAlarmCleared();

    // 模拟模式（原 SimulationWorkflow 归并，见 ADR-034；2026-09-17 ADR-032 取消 A/B/C 模式与派生参数）
    public void StartSimulation();            // 单一开关，按设备连接态自动分支选相机/是否写轴
    public void DisableSimulation(string reason = "用户手动停止", bool hasError = false, bool isAuto = false);
    // 幂等；结束轨迹记录会话并落盘；末尾统一触发 SimulationStopped 事件
    public event EventHandler<SimulationStoppedEventArgs> SimulationStopped;
    // 模拟停止事件（所有停止路径统一触发，UI 层订阅后统一复位按钮状态）
    public void LoadSimulation();
    public void SaveSimulation();
    public void StartSimulationLineLaser();
    public void StopSimulationLineLaser();
    public void ResetSimulationLineLaser();
    public void StartRobotXSimulation();
    public void StopRobotXSimulation();
    public double GetEffectiveRobotX();
    public bool IsSimulationEnabled { get; }         // = 私有 _simulationRunning
    public int SimLaserFrequencyHz { get; set; }     // 线激光数据频率 30/60/80/120
    public bool ShouldUseVirtualCamera { get; }      // 模拟中且线激光未连接 → 用虚拟相机
    public bool ShouldMoveAxis { get; }              // 非模拟恒 true；模拟中取运控 Connected

    public void Dispose();                    // → DisposeComponents()（ADR-001，不重写 Dispose(bool)）
}
```

> **日志出口（2026-09-04 回归直连）**：本类全部日志经私有 `Log(...)` → `GlobalCommData.ShowLog(_tag, ...)`；
> 模拟模式相关另用 `_simTag` → `GlobalCommData.ShowLog(_simTag, ...)`。
> 标签写法约定见 [[standards/CodeSimplification]] §三；底层出口见 [[api/GlobalCommData]]。

---

## 常驻线程（7 条 + 1 条按需模拟线程）

| 线程 | 类别 | 驱动对象 | 节拍 |
|---|---|---|---|
| `thLaserHeadWork` | 模组 | `LaserWeldHeadWorkflow.FlowProcess()` | 运行态 10ms / 非运行态 100ms |
| `thLineLaserWork` | 模组 | `LineLaserWorkflow.FlowProcess()` | 同上 |
| `thMonitorCamWork` | 模组 | `MonitorCameraWorkflow.FlowProcess()` | 同上 |
| `thMotionControlWork` | 模组 | `MotionControlWorkflow.FlowProcess()` | 同上 |
| `thWeldParamControlWork` | 模组 | `WeldParamControlWorkflow.FlowProcess()` | 同上 |
| `thHeartInspectWork` | 通讯 | 机器人通讯**心跳分级**（只检测不收发）；**2026-11-17 阶段 6**：仅在 `ConnectRobot` 成功后由 `EnsureHeartbeatThread` 创建；只报 H0/H1/H3/H4 变化沿，不重连、不退出；`NeedHeartbeat=false` 只停日志 | 1000ms |
| `thCommCommandWork` | 通讯 | 机器人**指令交互**（队列消费 + 分派）；**2026-11-17 阶段 6**：每拍先调 `comm.EnsureRobotChannelHealthy()` 做通讯层自愈 | 空闲 100ms |
| `thSimTestWork` | 模拟（按需） | `SimTick()` 发布模拟 robotX | 20ms |

**5 条模组线程共用**私有体 `SubDeviceWork(flow, name)`，严格执行五段式（范式 M1），**每拍前置问询运行态**（范式 M5，2026-09-07；2026-09-08 加 `wasDriving` 门控）：

```csharp
bool wasDriving = false;            // 上一拍是否处于 Running 驱动中
while (!IsCloseWork)
{
    if (Current != MainDeviceStatus.Running)
    {
        flow.ResetWorkTime();       // 清步骤计时，防暂停时长被计入超时（每拍执行）
        if (wasDriving) LogDriveStopped();  // 仅从 Running 真正跌出才记日志
        wasDriving = false;
        Thread.Sleep(100);          // 非运行态：慢节拍
        continue;
    }
    if (_driveStopped != 0) Interlocked.Exchange(ref _driveStopped, 0);
    wasDriving = true;
    flow.FlowProcess();             // 运行态：驱动一步
    Thread.Sleep(10);               // 运行态：快节拍防空转
}
```

> `LogDriveStopped()` 内 `Interlocked.CompareExchange(_driveStopped, 1, 0)` 闭锁：运行态从 Running **真正跌出**时
> **整机只记一次**「子流程停止驱动」；**线程不修改任何状态**——
> 参考基线裁定（HonorMachineTest）：线程只判断「状态不对就不执行」，
> 状态一律由 IO 动作链（`DoXxx → SetStatus`）专门管理，`Stopping` 等焊接态迁移由停止命令链下发。
> **启动默认态不打此日志**（2026-09-08 用户裁定）：程序打开即 NoReset、从未 Running，`wasDriving` 恒 false，
> 不存在「状态变更」，不该出现「运行态已变更为 NoReset」的误导信息。
> 单拍异常只记日志不退出，避免整条流程永久停摆。线程一律 `IsBackground = true`（M2）；
> `MachineFlowWorkClose()` **只置 `IsCloseWork = true`，不 Abort 线程**（M3）。

⚠️ **`thSimTestWork` 是第 8 条线程，不在 §7.2 的 7 条常驻线程内**：2026-09-04 用户裁定「在 DeviceControlWork 中做一条后台线程跑模拟测试」，
随 `EnableSimulation` / `DisableSimulation` 启停，非常驻。模拟设计的其余部分待用户修正后补全。

---

## 主设备运行态 MainDeviceStatus（6 态）

| 取值 | 含义 |
|---|---|
| `Running`(0) | 运行中（焊接中） |
| `Alarm`(1) | 报警（安全互锁失败 / 模组异常） |
| `EStop`(2) | 急停 |
| `Stop`(3) | 停止（整机就绪待机） |
| `NoReset`(4) | 报警/急停已清除，待复位 |
| `Reseting`(5) | 复位中 |

唯一写入入口：`private void SetStatus(MainDeviceStatus newStatus, string reason)`（经 `MachineStatusTrans` 校验后触发 `StatusChanged` 并记日志）。

### 状态迁移合法性 `MachineStatusTrans`

`SetStatus` 内**先校验后写入**，非法迁移只记 Warning 日志、不改状态：

| 规则 | 说明 |
|---|---|
| 急停优先 | `EStop` 只能经 `EstopCancel` 解除（`EStop → NoReset`），其余迁移一律拒绝 |
| 启动门槛 | 只有 `Stop` 才允许直接 `→ Running`（范式 M6 的门控） |
| 禁止直落 | `Running` 不允许直接 `→ NoReset`，须先 `Stop` |

### 状态读取红线（强制）

`_status` / `_lastStatus` 由 `_statusLock` 保护，**任何业务读取必须走 `Status` 属性或私有 `Current` / `Last`**，禁止裸读字段——
加锁与不加锁的读混用，等于没加锁。

```csharp
if (Status != MainDeviceStatus.Stop) ...     // 正确
if (_status != MainDeviceStatus.Stop) ...    // 错误：绕过锁
```

---

## 上电初始化：5 步同步顺序执行

```csharp
DeviceControlWork.Instance.InitializeMachine();   // 上电初始化入口（阻塞同步 5 步级联）
```

| 步骤 | 内容 | 调用 |
|---|---|---|
| 前置 | 清状态并强制 `NoReset` | `ClearMachine()` |
| `[1/5]` | 焊接头 | `LaserWeldHeadController.Instance.Initialize()` + `_weldHead.ConnectOn()` |
| `[2/5]` | 运动控制器 + CAMBOX 跟踪 | `_motion.InitializeOn()`（已下沉至 workflow）+ `_motion.ConnectOn()` |
| `[3/5]` | 线激光相机 | `_lineLaser.ConnectOn()` + `WaitChildConnected` |
| `[4/5]` | 监控相机 | `_monitorCam.ConnectOn()` + `WaitChildConnected` |
| `[5/5]` | 机器人通讯 | `CommWork()` → 调 `Comm` 提供的 RSI 方法（§7.4 裁定 C5） |
| 入口 | `InitializeMachine()` 先置 `_initAccepted`、拉起 IO 线程、置 `IoInit`；**模组线程与指令线程均不在入口启动** | IO 线程必须在场推进 `InitializeMachineTick`；`_initAccepted` 封堵 IO_INIT→受理的首拍竞态 |
| 收尾 | **5 模组线程 + 通讯线程统一延后到初始化出结果**（正常 Finish / 抢占中止 / 拒绝跳过三出口） | `FinishInitialization` / 抢占分支 / `EndInitWithoutChain` 三处调 `MachineFlowWorkOpen()` + `EnsureCommandWorkStarted()`；初始化期 IOWork 只推进连接链、冻结全部状态变更巡检（ADR-107 演进：原仅延后指令线程，现覆盖模组线程与 IOWork 状态变更）|

末步执行 `EvaluateInitializationResult()` 聚合判定：模组全 `Connected` → **保持 `NoReset` 待复位**（ADR-003 D1：只有复位流程成功才到 `Stop`）；否则 → `SetStatus(Alarm)`。

### 聚合判定口径

模组连接态 `SubDeviceState.Connected` 视为正常；其余（`Disconnected`）计为未就绪。

### 复位链路 `ResetMachine()`

`NoReset → Reseting → Stop`，**单次执行 `new Task(...)`**（范式 M4），不走常驻线程，**每步前置问询运行态**（范式 M5，2026-09-07）：

1. **急停态直接拒绝复位**（`EStop` 前置门禁，须先解除急停）
2. `ClearMachine()` 强制 `NoReset` → **问询仍为 `NoReset`**（`IsActionAborted`，被互锁报警抢占即中止）
3. `MachineStatusTrans(Reseting)` 校验后 `SetStatus(Reseting)`
4. `CascadeResetProcess()` 级联 5 个子流程 `ResetProcess()`，**每步前置问询仍为 `Reseting`**，被抢占立即中止
5. **再次问询仍为 `Reseting`**（被急停/报警改写即判「复位链被中止」并退出，不覆盖新状态）
6. 成功 → `Stop`，失败 → `Alarm`

前置门禁：运行中拒绝；`IsRobotReachable()` 不通过 → `Alarm` 并阻断（错误归口设备对象层，主设备层不复述，ADR-032）。

### 初始化链前置问询 `DoInitializeMachine()`

2026-09-07 补齐：初始化 5 步（机器人通讯 → 焊接头 → 运控 → 线激光 → 监控相机）**每步之间调用
`IsInitAborted()`**——初始化期间合法运行态只有 `NoReset` 与 `Alarm`，出现 `EStop / Reseting / Running`
即判被抢占，中止后续步骤与聚合判定（中止日志只记一次）；`WaitChildConnected` 等待循环每拍
`IsInitPreempted()`（静默版）问询，被抢占立即退出等待。启动链 `DoStartMachine` 置 `Running` 后同样问询一次。

---

## 关键边界：机器人/PLC 连接不属于本类

机器人和 PLC 的连接是外部设备通讯，由顶层 `Comm`（`CommunicationManager`）管控。本类只是**使用方**（§7.4 裁定 C5）：

| 方向 | 内容 |
|---|---|
| 接收 | `GlobalCommData.CommunicationCommandReceived` → `OnCommRecived()` 只做 `CommandCore.Normalize` + 入队，**不做业务** |
| 下发 | `SendRobotCommand(CommandCore.Tx*)` → `comm.RobotManager.SendRobotData(...)` |

不直接持有连接、不直接操作 socket。详见 [[modules/Comm]]。

### 指令队列（取代旧命令三槽）

ADR-020 裁定 C3：**不再监控机器人 pose**，`RobotPose` / `RobotCommand` / `DeviceCommand` 枚举全部删除，
指令一律以 `const string` 解析（[[api/CommandCore]]）。

```
通讯回调 OnCommRecived(msg)
   → CommandCore.Normalize(msg)
   → IsKnownCommand? 否 → Warning 丢弃
   → lock(_commLock) _commCommandQueue.Enqueue(cmd)
                                   ↓
CommCommandWork 线程：DequeueCommand() → MapCommandToIo(cmd) → IsCommandPreconditionMet → SetVirtualIo(ioName)
```

`MapCommandToIo` 现状：动作类指令写虚拟 IO（由 thIOWork 统一扫描），坐标类仅记录；`RxAbort` 记 Error 日志、
`RxWeldStopPose` 缓存停止位。~~`DispatchCommand` + 其后的 `WeldStatusTrans()`~~ ⚠️ **2026-10-10 勘误**：
`DispatchCommand` 已在指令驱动重构中消失，`WeldStatusTrans()` 的调用随之丢失（整条委托链曾长期零调用方）；
**现调用点 = `CascadeWeldStatus()` 末尾**（[[decisions/ADR-061-WeldStatusTransCascadeWiring]]）。

---

## 级联范围

| 级联动作 | 覆盖 |
|---|---|
| **上电连接** `CascadeConnect()` | 焊接头、运控、线激光、监控相机（**不含** `WeldParamControlWorkflow`，§8.3 无实体设备） |
| **上电断开** `CascadeDisconnect()` | 同上 |
| **复位** `CascadeResetProcess()` | 上述 4 个 + 焊接工艺（5 个，流程动作非连接动作） |
| **清状态** `CascadeClearStatus()` | 同上 5 个 |
| **焊接工作态迁移** `WeldStatusTrans()` | 同 5 个，各自调自己的 `WeldStatusTrans()`；**触发点 = `CascadeWeldStatus()` 末尾**（2026-10-10 接线，[[decisions/ADR-061-WeldStatusTransCascadeWiring]]）：5 次 `RequestWeldStatus` 写完目标态 + 日志后立即委托；5 个调用方 = DoSubPrework(PreWork) / DoSubWork(Working) / DoSubStop(Stopping) / DoSubManualStop(ManualStopped) / DoSubAlarmStop(ErrorAborted) |

> ⚠️ 子流程的 `WeldStatus` 写入口是 `protected`，整机层**无法直接赋值**，
> 故 `WeldStatusTrans()` 是「委托各子流程自行迁移」的编排入口，不是赋值入口。
> ⛔ **不接在 `CommCommandWork`**（`DispatchCommand` 已不存在），**不接在 `DisableSimulation` 的散装 Standby 复位**（已自带逐流程补偿）——见 ADR-061。

---

## 模拟模式 API（原 SimulationWorkflow 已删除归并；2026-09-17 ADR-032 统一化）

原 `SimulationWorkflow.cs` 已删除，全部成员并入本类，**模拟模式真相源 = 本类单例**。ADR-032 取消 A/B/C 模式，改为**单一开关 + 按设备连接态自动分支**：

| 成员 | 说明 |
|---|---|
| `bool IsSimulationEnabled` | 模拟是否开启（= 私有 `_simulationRunning` 单标志） |
| `void StartSimulation()` / `void DisableSimulation()` | 开/关模拟（Disable 幂等）。开启时**按连接态自动选相机**（`ShouldUseVirtualCamera` 为真 → `SelectVirtual()`，否则 `SelectIntelligentLaser()`）+ 套用 `SimLaserFrequencyHz` 至虚拟相机 `FrameRateHz` + `StartRobotXSimulation()` + `SimTestWorkOpen()` + **生产会话**（**2026-09-20 起走 `ProductFileRecordManager.BeginProductSession(CurrentProductSn, true)`**：状态记「模拟」、会话基名带「模拟」前缀）；关闭时停线程并 `EndProductSession("pass", "")`（归档三份记录文件 + 生产记录落库） |
| `void LoadSimulation()` / `void SaveSimulation()` | INI 持久化（仅 `Simulation/LineLaserDataFrequencyHz`；⛔ 旧 `MotionControlWorkflow.ini` 回退迁移与 5 个旧键已删） |
| `double GetEffectiveRobotX()` | 读模拟线程按节拍发布的 `_simRobotX`；未开启返回 0 |
| `void StartRobotXSimulation()` / `void StopRobotXSimulation()` | 共享模拟 robotX 时钟启停（起点**随机 0~20**，速度内部常量 `SimDefaultSpeedMmPerS = 60.0`） |
| `void StartSimulationLineLaser()` / `void StopSimulationLineLaser()` / `void ResetSimulationLineLaser()` | 线激光模拟生命周期编排入口（UI 只经这些方法触发） |
| `int SimLaserFrequencyHz`（get/set） | 线激光数据频率 30/60/80/120Hz（`_robotXLock` 保护） |
| `bool ShouldUseVirtualCamera` | 模拟中且 `_lineLaser.State != Connected` → true（自动用虚拟相机） |
| `bool ShouldMoveAxis` | 非模拟恒 true；模拟中取 `_motion.State == Connected`（未连接 → false，只记录不写轴） |

⛔ **ADR-032 已删除**：`SimTestMode` 枚举、`EnableSimulation(SimTestMode)`、`CurrentMode` / `SelectedMode`、`SimStartX` / `SimSpeed` / `SimTargetDistance` / `SeamProfile` / `RandomMode`（全库 0 残留）。

消费方：[[api/SystemControlPage]]（开启模拟一键联动）、`FormMain`（启动加载）、[[api/LineLaserWorkflow]]（读 `IsSimulationEnabled` / `ShouldUseVirtualCamera` / `GetEffectiveRobotX`）、[[api/MotionControlWorkflow]]（读 `ShouldMoveAxis` 决定写轴或只记录）。

> ⚠️ **2026-09-04 用户裁定（现行仍有效）**：模拟测试由本类内按需线程 `thSimTestWork` 承载（20ms 节拍跑 `SimTick()` 虚拟 XYZ 位姿并经 `WeldParamManager.UpdateRobotPose` 单入口喂入），即 **MODE + 按需线程**；模组工作流不自起线程（ADR-042/ADR-032）。
> **ADR-032 已闭环**原「模拟设计的其余内容待修正」：虚拟相机喂数、坐标下发运控、无运控轨迹记录均已落地。
>
> **2026-09-22 模拟位姿单源收口**：`SimTick()` 统一虚拟 XYZ（X 随节拍推进、Y/Z 恒 0），经 `WeldParamManager.UpdateRobotPose(x,y,z)` **单入口**喂入——置位算法 `_hasRobotY` 放开特征帧拦截，并刷新 `CurrentRobotX/Y/Z`；`GetEffectiveRobotX()` 改读 `WeldParamManager.CurrentRobotX`（删除对本地 `_simRobotX` 字段的直接读取），杜绝「生成侧直写 + 消费侧直读」双源。详见 [[lessons/SimulationAutoBranching]] 陷阱十七。

## 模拟测试自动终止契约（2026-09-20，[[decisions/ADR-039-SimulationTestAutoTerminationAndRecordCacheRelease]]）

- `CheckWeldProgress()`：行程到程须调 `DisableSimulation()`（停 robotX 时钟 + 落盘），不能只 `DoSubStop()` 级联模组 Stop（陷阱九）。
- `SimScheduleTick()`：顶部守卫——`Current == Alarm || Current == EStop` 或任一模组 `WeldStatus == ErrorAborted` 时，立即 `EndProductSessionSafely("fail", …)` + `DisableSimulation()` 后 return（陷阱十三）。
- **2026-09-24 焊缝收尾语义（业主口径，见 [[decisions/ADR-044-SeamEndSemanticsAndMotionAxisScope]]）**：`BeginWeldMonitor` 的 `_weldTargetMm = 焊缝终止行程`（⛔ **不叠加前置量**）；另设 `_laserStopStrokeMm = max(0, 终止行程 − 前置量)`。`CheckWeldProgress` 先判**线激光收工行程**（命中即 `LineLaserWorkflow.Instance.FinishMeasureByStroke()`：关外设 + 停入图，**但不改线激光 `WeldStatus`**），再判**终止行程**（命中才 `DoSubStop`）——**机器人必须实际走到焊缝终止 X 才停止**。语义：线激光装在焊枪前方一个前置量上，机器人到 (终止X − 前置量) 时激光恰好扫过焊缝末端；末端这段内高斯窗仍有点（`MinSmoothPoints = 3`）⇒ 查图不回落、轴目标不跳变。
- **两条独立时间线（关键口径）**：收工后 ① **入图结束**——无数据帧 ⇒ 入图键 (X+前置距离) 与 CSPinY **冻结**；② **焊接继续**——线激光流程态保持 `Working` ⇒ 运控继续出图，`CSPoutY`／`实时Y`／SeamTraceY 记录**一路到焊缝行程结束**（机器人走到终止 X），届时主控 `DoSubStop` 统一收口。⛔ 早期把「收工」做成「焊接结束」会让运控停在段未走完时清缓冲（`4359` + 坐标系残留 ⇒ 下次启动标定位回归超时）。
- **2026-09-24 终止位来源**：优先机器人上报停止位 X（`RX_WELD_STOP_POSE` 经 `CommandCore.TrySplitPayload` 拆「指令名 + 载荷」，首个数值即停止位 X → `ApplyRobotStopPose(X)` 缓存 `_robotStopPoseX/_hasRobotStopPose`，监视激活时即时改写终止行程）；模拟测试的停止状态同样由机器人发来，兜底取 `_simWeldLengthMm`；**真实模式现为占位空缺**（无上报 → 不做线激光收工判断，日志标注「真实占位空缺(待机器人下发)」，协议细化后由机器人下发终止 X 取代）。

## 生产会话与产品记录（2026-09-20 新增，[[decisions/ADR-037-ProductProductionRecordLifecycle]]）

本类是**产品生产会话的驱动方**：起焊与停机命令同时开启/结束一次生产会话，会话结束即把一条生产记录落产品库。

| 触发点 | 调用 | 结果 |
|---|---|---|
| `DoSubWork`（模组焊接启动） | `BeginProductSession(CurrentProductSn, IsSimulationEnabled)` | 缓存产品码 / 起焊时间 / 状态 + 会话基名，开启记录与轨迹会话 |
| `DoSubStop`（模组停止流程） | `EndProductSessionSafely("pass", "")` | 停记录 + 归档三份文件 + 落库 `pass` |
| `DoSubManualStop`（模组手动停止） | `EndProductSessionSafely("pass", "")` | 同上（人工正常收尾记 `pass`） |
| `DoSubAlarmStop`（模组报警停止） | `EndProductSessionSafely("fail", "模组报警停止")` | 落库 `fail` + 异常原因 |
| `StartSimulation` / 模拟关闭端 | `BeginProductSession(CurrentProductSn, true)` / `EndProductSessionSafely("pass", "")` | 模拟会话（状态记「模拟」） |

- **`string CurrentProductSn`**（get/set）：产品码（产品名）。`// todo 产品码待机器人传输指令协议细化`——协议落地前可外部赋值；空缺时 Manager 以 `TEST` 占位。
- **`EndProductSessionSafely(result, info)`**（private）：包一层 try-catch 的生产会话收尾出口；未开会话时幂等跳过。
- **Job 切换入档**：构造时订阅 `LineLaserManager.JobChanged += OnLineLaserJobChanged`（`Dispose`/`DisposeComponents` 退订）；回调内 `_lineLaser.WeldStatus != Working` 时直接返回（只记焊接态切换），否则 `ProductFileRecordManager.RecordJobSwitch(jobId, GetEffectiveRobotX(), WeldParamManager.CurrentRobotY)`。
- ⛔ `StopRecordingSafely()` 已删除（2026-09-20）：原 4 处调用点全部改走生产会话收尾，避免「只停记录、不写生产记录」的中间态。

## ~~模拟轨迹记录器 `SimTrajectoryRecorder`~~（⛔ 2026-09-20 已删除，并入记录模块）

> **2026-09-20 演进（用户裁定）**：记录统一归口 [[modules/ProductFileManager]] 的 `ProductFileRecordManager`，模拟测试同样走该入口、不自开通道。原静态类 `SimTrajectoryRecorder`（`Config/Simulation/` 落盘）删除，改由 `ProductFileControl/Records/TrajectoryRecord.cs` 承载（缓存 + 终止落盘语义原样保留），落盘位置 = `Records\yyyyMMdd\[前缀]Trajectory_*.csv`，模拟会话文件名带「模拟」前缀（`RecordNamePrefix`），模拟与真实记录不分文件夹。`StartSimulation` 现调用 `ProductFileRecordManager.Instance.RecordNamePrefix="模拟"` + `StartRecording()` + `BeginTrajectorySession()`；`DisableSimulation` 调 `EndTrajectorySession()` + `StopRecording()`（自动归档 .ply/.pDat）+ 清前缀。写入方 API：`RecordTrajectoryPoint(...)` / `FlushTrajectory()` / `EndTrajectorySession()`。
> 另：`SimTick()` 现统一喂数——模拟 X 同步写 `WeldParamManager.CurrentRobotX`（真实链路仍由 RSI 回包刷新）；焊接启动命令 `DoSubWork` 开记录会话、`DoSubStop`/`DoSubAlarmStop`/`DoSubManualStop` 停止并自动归档（模拟/真实同通道）。
>
> 历史成员表（2026-09-17 ADR-032，仅供追溯）：

| ~~成员~~ | ~~说明~~ |
|---|---|
| ~~`BeginSession()`~~ | ~~开模拟会话：创建 `Config/Simulation/SimTrajectory_*.csv` + 表头，清缓存~~ |
| ~~`RecordPoint(...)`~~ | ~~每拍入缓存（`lock` 保护）；会话未开始静默丢弃~~ |
| ~~`FlushToFile()`~~ | ~~缓存追加落盘并清缓存；失败仅告警、缓存保留重试~~ |
| ~~`EndSession()`~~ | ~~落盘 + 复位会话~~ |
| ~~`BufferedCount`~~ | ~~未落盘点数（调试查询）~~ |

> ~~写入方~~：现写入方为 [[api/MotionControlWorkflow]] 的 `OutputCspTick()`（有轴）与 `RecordOnlyTick()`（无轴）→ `RecordCspPoint()` → `ProductFileRecordManager.RecordTrajectoryPoint(robotX, robotY, cspY)`（**3 参**）。⚠️ 工艺调整快照（FeedSpeed / RobotSpeed / LaserPower / SeamWidth）**不再经轨迹 CSV 传递**——由 `.pDat`（`WeldParamControlRecord`）独占记录（ADR-037 决 6 的 7 列条款 2026-09-20 经实测反馈废止，轨迹 CSV 回落 3 列）。

---

## 遗留待办（`// todo` 占位，属批次 4 未落地部分）

| # | 待办 | 位置 | 批次 |
|---|---|---|---|
| 1 | Preworking 五项设备运行检查（§7.7） | 5 个子工作流 + `DispatchCommand` 的 `RxPreWeldRequest` 分支 | 4.5 |
| 2 | Working 四路焊接子流程（§7.8） | Motion ②④⑤ / WeldParamControl 摆幅中点 | 4.6 |
| 3 | 机器人心跳**报文**下发 | `HeartInspectWork`（待 `CommandCore` 补心跳常量） | — |
| 4 | 指令交互闭环「等待子流程完成 → 反馈机器人」 | `CommCommandWork` | 4.5/4.6 之后 |
| 5 | 焊接头温度阈值监控 | `LaserWeldHeadWorkflow` | 4.1 |
| 6 | 监控相机轴控制行为 | `MonitorCameraWorkflow` | 4.2 |
| 7 | 运控送丝位置 + 焊接质量阈值检测 | `MotionControlWorkflow` | 4.3 |
| ~~8~~ | ~~模拟测试设计的其余内容~~ ✅ **2026-09-17 ADR-032 已闭环** | `StartSimulation()` / `SimTrajectoryRecorder` | — |

见 [[architecture/DeviceControlArchitecture]] §15.2。

---

## UI 接入

```csharp
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;

var main = DeviceControlWork.Instance;
main.StatusChanged += OnMainDeviceStatusChanged;   // 统一入口：Stop 即整机就绪，Running 即焊接中
bool welding = main.IsWelding;
bool robotOnline = main.IsRobotOnline;
```

> **红线**：UI 线程禁止直接驱动内部运行线程。驱动主设备**必须**走
> `InitializeMachine()` / `StartMachine()` / `StopMachine()` / `ResetMachine()` / `ClearAlarm()` / `EstopMachine(reason)` / `EstopCancel()`；
> 禁止直接调内部编排方法（`MachineFlowWorkOpen` 等）。

调用方：`FormMain.cs`（构造/启动/关闭）、`SystemControlPage.cs`（模拟参数）。

---

---

## 虚拟 IO 层（2026-09-04 新增，原档20260904 §2）

> **背景**：用户补充原档 `raw/architecture/激光焊接系统业务流程图20260904.md` 后裁定
> 「完整落地 IO 中转」，并给出硬约束——**不新建 .cs 文件、不新建扫描线程**。
> 虚拟 IO 常量与置位表定义在 `DeviceControlWork.cs` 内部，扫描由 `DeviceStatusWork` 现有两线程承担。

### 虚拟 IO 操作 API

| 成员 | 签名 | 说明 |
|---|---|---|
| `IoInit` / `IoReset` / `IoStart` / `IoStop` / `IoClearAlarm` | `public const string` | 系统级 5 条（原档 §2.4；`IoEmg` 急停已删除——急停无虚拟 IO，2026-09-08 裁定） |
| `IoMotionBusFault` | `public const string` | 运控总线故障（电平型报警源，2026-09-08；由 IOWork 总线监督置位，`DoMotionBusFault` 置 Alarm） |
| `IoSubConnect` … `IoSubAlarmStop` | `public const string` | 模组级 7 条（原档 §10.3） |
| `SetVirtualIo(ioName)` | `void` | **三种触发源统一置位入口** |
| `ClearVirtualIo(ioName)` | `void` | 清单个位 |
| `IsVirtualIoSet(ioName)` | `bool` | 电平型查询，不清位（急停用） |
| `TakeVirtualIo(ioName)` | `bool` | 脉冲型取走并清位，保证每条命令只执行一次 |
| `ClearAllVirtualIo()` | `void` | 全清（`DisposeComponents` 调用） |
| `SnapshotVirtualIo()` | `string[]` | 全量快照，供 `GetIOState` |
| `ExecuteIo(ioName)` | `bool` | **扫描器唯一执行入口**，分派到 `DoXxx` |

### IO 两类语义与「只触发一次」硬特性（2026-09-07 补）

虚拟 IO 分**脉冲型**与**电平型**两类，语义不同、不得混用：

| 类型 | 查询方式 | 消除时机 | 适用 |
|---|---|---|---|
| 脉冲型（命令） | `TakeVirtualIo` | **取走即清位**，动作执行前已完成 | `IoInit`/`IoReset`/`IoStart`/`IoStop`/`IoClearAlarm`/`IoSub*` |
| 电平型（状态） | `IsVirtualIoSet` | 由触发方主动 `ClearVirtualIo` | `IoMotionBusFault` 运控总线故障（IOWork 监督：状态离开 Alarm 自动解闭锁，NG 持续则重触发） |

> **「IO 只能触发一次动作，进入动作后 IO 必须取消掉」**——这是虚拟 IO 的硬特性。
> 脉冲型命令若不在动作开始前消除，扫描器下一拍会再次命中并重复进入动作，形成无限动作循环。
> 实现上由 `TakeVirtualIo` 保证（内部为 `HashSet.Remove`，命中同时清位）。

**动作不得占用 IO 扫描线程**：`ExecuteIo` 分派的 `DoXxx` 可能耗时数十秒（初始化链要连 4 个模组）。
扫描器**取走 IO → 记日志 → 拉起独立动作线程 → 立即返回**，IO 在动作开始前即已消除。

```
扫描线程:  TakeVirtualIo(IoInit) → Log"命中" → DispatchAction → 继续扫描
                                                    ↓
动作线程:                              ExecuteIo → DoInitializeMachine（20s）
```

若动作被同步执行，会出现「日志里 IO 命中打在动作结束后」的假象，看起来像 IO 未消除——
实为扫描线程被独占，不是 IO 滞留（2026-09-07 日志排查结论）。

### 命令方法（置位）与执行体（扫描执行）对照

> 公共方法**只置位不执行**；真正执行体为 `DoXxx`，由 `thIOWork` / `thEMGWork` 扫描驱动。

| 公共方法（置位） | 置位 IO | 执行体 | 原档 |
|---|---|---|---|
| `InitializeMachine()` | `IoInit` | `DoInitializeMachine()` | §10.2-1 |
| `ResetMachine()` | `IoReset` | `DoResetMachine()` | §10.2-2 |
| `StartMachine()` | `IoStart` | `DoStartMachine()` | §10.2-3 |
| `StopMachine()` | `IoStop` | `DoStopMachine()` | §10.2-4 |
| `ClearAlarm()` | `IoClearAlarm` | `DoClearAlarm()` | §10.2-5 |
| `EstopMachine(reason)` | ——（无虚拟 IO） | `DoEstopMachine()` 直通同步执行（触发源：EMGWork 物理信号边沿 / 机器人 `RxAbort` 指令；急停必须立即生效，同属同步白名单，2026-09-08 裁定：急停无虚拟 IO、只有物理 IO） | §10.2-6 |
| （无公共置位方法，IOWork 监督自动触发） | `IoMotionBusFault` | `DoMotionBusFault()`（2026-09-08，置 Alarm） | —— |

**两条易错约束**：

1. `InitializeMachine()` 必须先拉起线程（`MachineFlowWorkOpen` / `MachineCommandWorkOpen` /
   `DeviceStatusWork.MachineIOWorkOpen`）再置位——否则扫描器未起，`IoInit` 无人消费。
2. `DoStopMachine()` **不关闭 `thIOWork`**（扫描器不能自杀），
   仅在 `DisposeComponents` 调 `MachineIOWorkClose()` + `ClearAllVirtualIo()`。

### 关闭链（2026-11-17 阶段 5 / ADR-101 收口）

> **⛔ 关闭路径不得依赖脉冲型虚拟 IO 的异步消费者**：`StopMachine()` 按原档语义只置位 `Stop_IO`，执行体由 `thIOWork` 扫描消费；而关闭链会紧接着关闭扫描线程并清位 ⇒ 置位的脉冲永远无人消费，级联断开从未执行。

| 环节 | 现行行为 |
|---|---|
| `DisposeComponents()` | `_disposed` 幂等、`_shuttingDown` 拒绝新业务 → `ClearAllVirtualIo()` → `MachineFlowWorkClose` + `JoinModuleWorkThreads` → `MachineCommandWorkClose`（含 Join）→ `MachineIOWorkClose`（含 `thAction`）→ `SimTestWorkClose`（含 Join）→ `CascadeDisconnectWithWait` → `CloseRobotChannel` → 退订三事件 → 汇总一条 |
| 预算 | `ShutdownBudgetMs=30000`；每步前检查，超时记 `强制退出 原因 关闭预算超时 步骤 {step} 时点 yyyy-MM-dd HH:mm:ss` |
| 汇总 | `关闭完成 线程 n/11 设备 m/4 用时 xms`；11 = 5 模组 + 2 通讯 + 3 状态 + 1 动作；未全退或未全断记 Warning |
| `CascadeDisconnectWithWait()` | 依次 `ConnectOff()` 四个模组：**焊接头从站 → 运动控制器 → 线激光相机 → 监控相机**；逐台轮询 `Disconnected`，单台上限 5 s，超时 Warning 不中断后续；结束一条 `级联断开完成 设备 m/4` |
| `CascadeDisconnect()` | 兼容入口，内部转调 `CascadeDisconnectWithWait()` |
| 硬件持有者释放 | `FormMain_FormClosed` 依次 `Dispose` 三个工作流后，再释放 `MonitorCamManager` · `LineLaserManager` · `CommunicationManager` 的 SDK 资源（各自 try/catch） |
| `DoStopMachine()` 在关闭路径 | **不走**（其状态迁移 `SetStatus` 会向正在销毁的窗体派发事件） |
| 关闭期巡检 | `DeviceStatusWork.IOWork` 读到 `IsShuttingDown` 只保活，不推进扫描/巡检/初始化/对齐 |

> 教训见 [[lessons/StartupInitializationOrderGates]] 坑 6。

### 模组级命令（原档 §10.3）

`DoSubPrework` / `DoSubWork` / `DoSubStop` / `DoSubManualStop` / `DoSubAlarmStop`
统一经 `CascadeWeldStatus(target, reason)` 向 5 个模组下发
（走基类 `DeviceWorkflowBase.RequestWeldStatus`，因 `SetWeldStatus` 是 protected）。
`IoSubConnect` / `IoSubReset` 属初始化 / 复位内部自动调用，不单独走扫描。

> **2026-09-23 ADR-043 演进**：`DoSubPrework` 头部新增 `WeldParamManager.ResetSeamTracking("焊前检查会话复位")`（播种之前）——工艺调整（采用宽度/四条工艺曲线）的会话清空责任由起焊沿移至焊前检查（业主裁定：参数管控和记录自「下发参数后进入 start」即播种后才开始，窗口外清零不产生变动观测）；起焊沿 `OnSeamTrackingStart` 改调 `WeldParamManager.ResetTrackingForWeldStart` 只清跟踪（PVT+地图）、不清工艺调整。见 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]。

---

## 查询与参数命令（2026-09-04 新增，原档 §10.4 / §10.5）

| 命令 | 签名 | 原档 | 说明 |
|---|---|---|---|
| `GetMainDeviceStatus` | `MainDeviceStatus` | §10.4-14 | 只读，返回 `Current` |
| `GetSubDeviceStatus(tag)` | `SubDeviceWeldStatus` | §10.4-15 | 按模组 `Tag` 查；未命中返回 `NoReset` |
| `GetAllSubDeviceStatus()` | `Dictionary<string, SubDeviceWeldStatus>` | §10.4-16 | 5 个模组（4 实体 + 1 虚拟） |
| `GetAlarmInfo()` | `MachineAlarmInfo` | §10.4-17 | 故障代码 / 描述 / 发生时间；数据源 `_lastAlarm` |
| `GetIOState()` | `string[]` | §10.4-18 | 调试用，返回已置位虚拟 IO |
| `GetWeldParam()` | `WeldParamOutput` | §10.5-20 | 只读，返回 `_weldParam.LastOutput` |
| `SetWeldParam(param)` | `bool` | §10.5-19 | 前置：M3 停止；**运行中禁止修改**，违反返回 false |
| `SetRobotCoord(x, y, z)` | `bool` | §10.5-21 | 前置条件同上 |
| `GetRobotCoord(out x, out y, out z)` | `void` | — | 配套读取 |

`MachineAlarmInfo` 为 2026-09-04 新增的数据载体（与 `MainDeviceStatusChangedEventArgs` 同文件，未新建 .cs）。

---

## 预检失败整机通路（2026-09-04 新增，原档 §4.2 / §9）

`CheckPreworkFailed()` —— 由 `DeviceStatusWork.IOWork` 在 Running IO 扫描后逐拍调用。

**原档规则**：`Pre-Working Fail` **不进入报警态 M5**，而是 M4→M3、S3→S2（不报警，可重新发起）。

**判定依据**：整机处于 `Running` 但 `_everWorking == false`（从未真正进入 `Working`）时，
若有任一模组处于 `Standby`（即从 PreWork 退回），判定预检失败，整机回落 `Stop`。
`_everWorking` 在 `DoStartMachine` 中重置。

---

## 对中偏差数据中枢（2026-09-04 新增，原档 §7.4.5）

`AlignDatum`（只读属性）→ `MonitorCameraWorkflow.LastResult`。

用户裁定原话：**监控相机只能给结果**（对中 OK/NG），NG 时给出两个数据：

| 字段 | 消费方 | 用途 |
|---|---|---|
| `OffsetX` / `OffsetY` | **控制器** `MotionControlWorkflow` | 驱动振镜摆动光斑（`ApplySpotAlignCompensation`，`StepTracking` 阶段） |
| `WireStickoutDeviation` | **机器人** | 调整送丝距离 |

振镜摆动控制本身仍为 `// todo`（依赖运控振镜轴指令与 `WeldParamOutput.GalvoAmplitude` 摆幅基准落地）。

---

## 遗留待办（`// todo` 清单）

| # | 位置 | 内容 |
|---|---|---|
| 1 | `MapCommandToIo` 调用后 | 指令闭环反馈机器人执行结果（待批次 4.5 / 4.6） |
| 2 | `ApplySpotAlignCompensation` | 振镜摆动控制（待振镜轴指令 + 摆幅基准） |
| ~~3~~ | `StartSimulation` / `SimTrajectoryRecorder` | ~~模拟测试设计其余内容~~ ✅ **2026-09-17 ADR-032 已闭环** |
| 4 | `DoSubPrework` 链路 | Preworking 五项检查实值判定（批次 4.5） |
| 5 | Working 四路子流程 | 工艺参数闭环（批次 4.6） |

> ✅ **C3 已由 [[decisions/ADR-014-MainDeviceStateSemantics]] D1 裁定关闭（2026-09-04）**：
> `DoClearAlarm()` 消报**一律回落 `NoReset`**（不再区分 wasRunning 回 Stop），现行代码即此实现。
> 沿革见 OPEN-ClearAlarmSemantics（已裁定关闭并入 ADR-020，2026-09-17 删除；映射见 [[decisions/ADR-Index]]）（已关闭）。

## 模拟启动结构（2026-09-22 精简）

`StartSimulation()` 由 64 行收敛为 32 行骨架：`PrepareSimulationCamera()`（选相机 + 虚拟相机数据频率）、`SuspendRealHardwareForSimulation()`（焊接头/监控相机停驱并记录原使能）、`EnsureRunningForSimulation()`（清残留报警 + 进 Running）、`LogSimulationStarted()`（启动日志）。**时序不变**：清警/进 Running 先于 `SimTestWorkOpen()`（ADR-039 要求）。

### 启停两侧的跨会话残留清理（2026-09-22 ADR-042）

二次模拟「启动即报警、清不掉」实测根因是**跨会话残留**，修复落在三处（详见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] 决 3 与 [[lessons/SimulationAutoBranching]] 陷阱二十）：

| 位置 | 新增动作 | 解决的问题 |
|---|---|---|
| `StartSimulation()` 开头 | `_motion.ClearSeamAlarm()`；`_motion.WeldStatus == ErrorAborted` 时 `_motion.ResetProcess()` | 启动侧兜底——异常退出路径未必经过 `DisableSimulation` |
| `StartRobotXSimulation()` 喂新起点前 | `ResetSeamTracking()` + `UpdateRobotPose(_simStartX, 0, 0)` | 上一会话 robotX 已走到 1704mm、新起点随机回 0~20，不复位则首帧即判「X 折返 1704mm 疑似复焊」 |
| `DisableSimulation()` | `_motion.Stop()` + `_motion.ClearSeamAlarm()` + `_motion.RequestWeldStatus(Standby)`；`_weldHead.RequestWeldStatus(Standby)`（均包 try/catch） | 补齐 ADR-039 决 5「对称复位」的缺口——原只复位线激光/焊参/监控，**遗漏运控与焊接头** → 停止汇总恒显 `V3跟踪：ErrorAborted` |

> ⚠️ 判据：**状态位的「置位」与「清除」必须成对出现在启、停两个入口**；级联到几个模组，停止就复位几个。

## 关联

- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（§7 为本类规范，§15.2 为落地批次）
- [[api/CommandCore]] — 机器人指令协议（const string，取代 CommandTable）
- [[api/DeviceStatusWork]] — 安全/IO/状态管控：`IsSafe` 门控 + `MachineIOWorkOpen/Close`
- [[modules/Comm]] — 机器人/PLC 连接归属地
- [[decisions/ADR-013-ThreeStateModelRefactor]] — 三态模型决策
- [[decisions/ADR-035-RawDesignRefinement20260903]] — 本次重构依据（7 线程 + 9 方法 + 裁定 C1~C7）
- [[decisions/ADR-032-SimulationTestRedesign]] — 模拟测试统一化（取消 A/B/C 模式、连接态自动分支、`SimTrajectoryRecorder`）
- [[api/GlobalCommData]] — 通讯与日志底层出口（本类 `_tag` / `_simTag` 的直连落地）

## 初始化完成统一使能接入（2026-11-04）

| 项 | 结论 |
|---|---|
| 落点 | `InitStepEvaluate`（小步 40）：`bool allReady = EvaluateInitializationResult();` → `bool servoReady = allReady && EnableAxesAfterInit();` → `InitializationCompleted?.Invoke(allReady && servoReady)` |
| 私有包装 | `EnableAxesAfterInit()`：`Motion == null \|\| !Motion.IsInitialized` → `Warning` + false；否则调 `Motion.EnableAxesAfterInit()` 并把结果写日志（`Info`/`Error`），异常吞口改为 `Error` + false |
| 语义 | 使能失败 ⇒ `InitializationCompleted(false)`，⛔ 不把流程判为成功；一次性执行，无定时重试 |
| 原设计 | `MontionManager.Initialization()` 只建轴不使能；`DoResetMachine()` / `CascadeResetProcess()` 链路无 `ServoOn` ⇒ 属缺口补齐，非策略收窄 |
| 关联 | [[decisions/ADR-081-InitUniformServoOn]] · [[api/MontionManager]] |

## 初始化第3步修正（2026-11-05，ADR-082 演进）

- `InitStepEvaluate` 收尾不再写 `allReady && EnableAxesAfterInit()`：使能 `try/catch` 无条件执行，日志 `初始化第3步 开始使能（逐轴）` 由 `EnableAxesAfterInit` 打印一次。
- `initSucceeded = allReady && enableOk`；随后 `MontionManager.Instance.MarkInitCompleted(initSucceeded)` 打开唯一闸门，并打印 `初始化第3步 结论 模组就绪 X 使能成功 Y → 整机初始化成功/失败`。
- **2026-11-11 时序修正**：`MarkInitCompleted` 前移到使能阶段结束处，**先开闸再判轴**；自动 ZeroPose 与 `LogAxisGateReport` 排在其后。否则 `TaMotionReady` 首条 `!_initCompleted` 恒 false，自动回零被静默跳过（见 [[lessons/StartupInitializationOrderGates]] 坑 4）。
- 仅当 `enableOk && taConfigOk && TaMotionReady` 时调 `RunTaHomeThenZeroPose()`（**2026-11-11**：先满扭矩回零、确认到位，再走 ZeroPose）；否则打印「跳过 TA_ZeroPose；TA 功能降级 原因 …」。
- `InitializationCompleted` 事件参数改为 `initSucceeded`（模组就绪 ∧ 全部轴使能成功）。

## 初始化与复位分离（2026-11-16，阶段 3 / ADR-099）

| 项 | 现行行为 |
|---|---|
| 初始化范围 | 只做连接 + 使能；`FinishInitialization` 不再调用 `RunTaHomeThenZeroPose()`，改为 `_motion.RunInitAutoHomeIfEnabled()`（配置 `INIT_RUN_TA_HOME=1` 才恢复旧行为，仅作回退路径） |
| 结束态 | 固定「已连接 / 已使能 / 未回零 / 无运动 / 待复位」；成功打 `Info`，失败打 `Error` 并注明「已连接设备保留 未连设备可再次初始化补连」 |
| 机器人通讯 | 初始化节点 `RobotComm` 的 `Mandatory` 由 `false` 改为 `true`；真实模式未连机器人即初始化失败并给原因；模拟流程由 `EnsureRunningForSimulation` 旁路，不受阻塞 |
| 受理门禁 | `DoInitializeMachine` 拒绝三类重复初始化：`_initializing` 进行中、`Current == Running`、`Current == EStop \|\| Reseting`；日志给对应原因 |
| 补连判据 | 新增 `AllInitTargetsConnected()`：规划内模组全部 `SubDeviceState.Connected` 且机器人在位时直接返回 true 并打「初始化跳过 模组均已连接 无需补连」，不重复连接 |
| 复位链 | 沿用既有链路：`ResetMachine()` → `IoReset` → `DoResetMachine()` 复位线程 → `CascadeResetProcess()`（焊接头/线激光/监控相机/运控/焊接工艺）→ 各子流程 `ResetProcess()`；⛔ 不新增第二套复位入口 |
| 运控复位 | 保留在级联内，由 `MotionControlWorkflow.ResetProcess()` 承担门槛 L1 与按轴能力分支，动作落到 `MontionManager`；失败由级联记「运控 流程复位未受理」并使整机转 `Alarm` |
| 复位移位 | 模拟模式下 `DoResetMachine` 的机器人在位门禁旁路（`!IsRobotReachable() && !IsSimulationEnabled`），否则模拟页无法复位 |
| 互锁旁路 | 新增只读属性 `IsInitializing`，供 `DeviceStatusWork.IOWork` 在初始化期跳过安全互锁门控（D16） |
| 关联 | [[decisions/ADR-099-init-reset-separation]] · [[api/MotionControlWorkflow]] · [[api/DeviceStatusWork]] |

## 两套状态联合与双闸门（2026-11-17，阶段 4 / ADR-100）

| 项 | 现行行为 |
|---|---|
| 设备态日志 | `SetStatus` 合法迁移后一条 `Info`「设备状态 旧 转 新 原因 …」；非法迁移仍一条 `Warning`；流程态级联一条，子流程零日志 |
| 联合矩阵 | 设备 6 态 × 流程 7 态；设备态变化不自动级联流程态，流程态仍只由 `CascadeWeldStatus` 写入 |
| 1 s 巡检 | `ConsistencyTick()` 由 `DeviceStatusWork.IOWork` 每拍调用、内部 1 s 节流；模拟与初始化期不参与 |
| 非法纠偏 | `Stop × Working` → `Standby`；`NoReset × 非 NoReset` → `NoReset`；`Alarm/EStop × Working` → `ErrorAborted`（`Alarm` 进入后 3 s 宽限） |
| 报警上送 | `Running`/`Stop` 时发现任一流程 `ErrorAborted` → 一条 `Error` + `ReportAlarm`；已是 `Alarm/EStop` 不重复上报 |
| 动作双闸门 | `CheckActionGate`：设备态须 `Running` 且 `EnsureReadiness` 达标；`DoSubWork` 需 L4，`DoSubPrework` 需 L0；模拟放行 |
| 统一快照 | `GetStatusSnapshot()` → `MachineStatusSnapshot`：设备态/上一态/5 流程态/运控就绪/线程登记/五个标志/报警/时间戳 |
| 关联 | [[decisions/ADR-100-state-union-and-action-gate]] · [[api/DeviceStatusWork]] |

## 心跳 H2 接入缺值超限（2026-11-17，阶段 7 / ADR-103）

| 项 | 契约 |
|---|---|
| 判据 | `EvaluateHeartbeatLevel` 在 H3 之后、H1 之前判 `IsNoValueOverLimit()`：`NoValueDistanceMm >= NoValueToleranceMm` 返回 H2 |
| 日志 | `LogHeartbeatEdge` 对 H2 输出 `Debug`「引导缺值超阈值 已由缺值报警停焊处置」，避免与报警 Error 重复记同一事实 |
| 唯一上报 | 报警由 [[api/MotionControlWorkflow]] `RaiseNoValueAlarm` 单点发出（一条 Error + `TX_NG` + `ErrorAborted`） |
| 关联 | [[decisions/ADR-103-no-value-hold-and-distance-segment]] · [[api/WeldParamManager]] |

## 报警停焊载荷冻结与清警（2026-11-17，阶段 7 / ADR-104）

| 项 | 契约 |
|---|---|
| 报警即停 | `ReportAlarm` 在焊接中先 `SendRobotCommand(TxNG)`，再 `SetStatus(Alarm)`，随后立即 `CascadeWeldStatus(ErrorAborted, "报警停焊接管流程")`，不等 `AlarmFlowGraceSeconds` 宽限 |
| 载荷冻结 | 五路流程转 `ErrorAborted` 后，任何 `UpdateRobotWeldParams` 路径不再被调用；RSI 回复缓存保持报警时刻值，通道与周期不变 |
| 对中与剪丝 | `MonitorAlignTick` 入口判 `IsAlarmstop` 直接返回，并把 `_cutWirePhase`/`_cutWireBeat` 归零；不覆盖冻结载荷、不写振镜中心补偿 |
| 报警可视 | `TxNG`（数值码 8）经 `TxCmd/TxPayload/TxSeq` 锁存重发，机器人每帧可见报警态 |
| 清警 | `DoClearAlarm` / `ReportAlarmCleared` 调 `ClearRobotCommand()` → `RsiComm.ClearTxCommand()`，`TxCmd` 归 0；只回 `NoReset`，不改任何 `WeldStatus` |
| 恢复边界 | 载荷恢复刷新只在下次焊接进入 `Working`；清警不自行续焊，处置固定「清警 → 回起始位 → 从头重焊」 |
| 关联 | [[decisions/ADR-104-rsi-channel-payload-freeze-alarm-stop]] · [[api/CommunicationManager]] · [[api/WeldParamControlWorkflow]] |

## 自动焊接流程判据 `IsAutoWeldingRunning`（2026-11-17，ADR-100 D29）

| 成员 | 语义 | 用途 |
|---|---|---|
| `IsAutoWeldingRunning` | 自动焊接流程是否在运行中（线激光焊接过程态 ∈ `PreWork` / `Working` / `Stopping`） | **UI 手动操作的唯一禁入判据** |

- ⛔ **不复用 `IsWelding`**：后者 = `Current == Running && IsWorking`，覆盖整段开机期，过宽会把「机器已启动但没在焊」的正常调试一并禁掉。
- 焊接主流程 = 线激光流程（焊缝跟踪 + 焊接），其焊接过程态是权威来源；判据挂在主设备级，供运控与焊接头两条流程共用。
- 拒绝落在**流程层**（ADR-105：页面动作统一经工作流门控）：`MotionControlWorkflow`（轴手动操作 / 绝对移动 / 回零 / TA 指令）+ `LaserWeldHeadWorkflow`（LA 对焦 / GA 振镜）。
- ⛔ **停止类动作永远放行**（`Stop` / `JogStop`）：安全操作必须随时可中断在途运动。
- 关联：[[decisions/ADR-100-state-union-and-action-gate]] · [[api/MotionControlWorkflow]]
