---
title: DeviceControlWork API 参考（整机主控 · 主设备运行态 MainDeviceStatus）
date: 2026-09-04
tags: [API, 工作流, 主控, 上电初始化, 机器人交互, 主设备运行态, 模拟, DeviceControlWork, ADR-028, ADR-030]
source: AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs
---

# DeviceControlWork API 参考

> **本页述 `DeviceControlWork`（单例，整机运行主控）**，见 [[decisions/ADR-027-ThreeStateModelRefactor]]。
> 主设备对外状态为 **运行态 `MainDeviceStatus`**（6 态：Running/Alarm/EStop/Stop/NoReset/Reseting），由 `SetStatus(...)` 单一入口写入，禁手工赋值。
>
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs`（**直接挂在 `MainDeviceControl/` 下，不在 `DeviceWorkflow/` 子目录**）
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：**独立管控类，不继承 `DeviceWorkflowBase`/`DeviceStateBase`**（原档明确）。
> 架构背景见 [[architecture/DeviceControlArchitecture]] 第 7 章。

## ✅ 2026-09-04 落地状态（ADR-030 批次 0~3 + 4.4）

原档 `主控设计.xlsx` R013 定义的 **7 条常驻线程 + 9 个公共方法 + 11 类私有方法已全部落地**：

| 落地项 | 内容 |
|---|---|
| 7 条常驻线程 | 5 条子设备工作线程 + `thHeartInspectWork`（心跳）+ `thCommCommandWork`（指令交互） |
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

---

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

    // ---- §7.5 九个公共方法 ----
    public void MachineFlowWorkOpen();        // 实例化 5 条子设备线程并 Start（幂等）
    public void MachineCommandWorkOpen();     // 实例化 2 条通讯线程并 Start（幂等）
    public void MachineFlowWorkClose();       // 只置 IsCloseWork，不 Abort 线程
    public bool InitializeMachine();          // 子设备实例化 → 连接 → 开启通讯 → 拉起线程
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

    // 模拟模式（原 SimulationWorkflow 归并，见 ADR-028）
    public void EnableSimulation(SimTestMode mode);
    public void DisableSimulation();
    public void LoadSimulation();
    public void SaveSimulation();
    public void StartSimulationLineLaser();
    public void StopSimulationLineLaser();
    public void ResetSimulationLineLaser();
    public void StartRobotXSimulation();
    public void StopRobotXSimulation();
    public double GetEffectiveRobotX();
    public bool IsSimulationEnabled { get; }
    public SimTestMode CurrentMode { get; }
    public SimTestMode SelectedMode { get; }
    public bool ShouldUseVirtualCamera { get; }
    public bool ShouldMoveAxis { get; }
    public double SimStartX { get; }
    public double SimSpeed { get; }
    public double SimTargetDistance { get; }
    public SimSeamProfile SeamProfile { get; }
    public bool RandomMode { get; }

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
| `thLaserHeadWork` | 子设备 | `LaserWeldHeadWorkflow.FlowProcess()` | 运行态 10ms / 非运行态 100ms |
| `thLineLaserWork` | 子设备 | `LineLaserWorkflow.FlowProcess()` | 同上 |
| `thMonitorCamWork` | 子设备 | `MonitorCameraWorkflow.FlowProcess()` | 同上 |
| `thMotionControlWork` | 子设备 | `MotionControlWorkflow.FlowProcess()` | 同上 |
| `thWeldParamControlWork` | 子设备 | `WeldParamControlWorkflow.FlowProcess()` | 同上 |
| `thHeartInspectWork` | 通讯 | 机器人通讯**心跳检测**（只检测不收发） | 1000ms |
| `thCommCommandWork` | 通讯 | 机器人**指令交互**（队列消费 + 分派） | 空闲 100ms |
| `thSimTestWork` | 模拟（按需） | `SimTick()` 发布模拟 robotX | 20ms |

**5 条子设备线程共用**私有体 `SubDeviceWork(flow, name)`，严格执行五段式（范式 M1），**每拍前置问询运行态**（范式 M5，2026-09-07；2026-09-08 加 `wasDriving` 门控）：

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
| `Alarm`(1) | 报警（安全互锁失败 / 子设备异常） |
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
| `[5/5]` | 机器人通讯 | `CommWork()` → 调 `Comm` 提供的 RSI / EKI 方法（§7.4 裁定 C5） |
| 收尾 | 拉起全部常驻线程 | `MachineFlowWorkOpen()` + `MachineCommandWorkOpen()` + `DeviceStatusWork.Instance.MachineIOWorkOpen()` |

末步执行 `EvaluateInitializationResult()` 聚合判定：子设备全 `Connected` → **保持 `NoReset` 待复位**（ADR-034 D1：只有复位流程成功才到 `Stop`）；否则 → `SetStatus(Alarm)`。

### 聚合判定口径

子设备连接态 `SubDeviceState.Connected` 视为正常；其余（`Disconnected`）计为未就绪。

### 复位链路 `ResetMachine()`

`NoReset → Reseting → Stop`，**单次执行 `new Task(...)`**（范式 M4），不走常驻线程，**每步前置问询运行态**（范式 M5，2026-09-07）：

1. **急停态直接拒绝复位**（`EStop` 前置门禁，须先解除急停）
2. `ClearMachine()` 强制 `NoReset` → **问询仍为 `NoReset`**（`IsActionAborted`，被互锁报警抢占即中止）
3. `MachineStatusTrans(Reseting)` 校验后 `SetStatus(Reseting)`
4. `CascadeResetProcess()` 级联 5 个子流程 `ResetProcess()`，**每步前置问询仍为 `Reseting`**，被抢占立即中止
5. **再次问询仍为 `Reseting`**（被急停/报警改写即判「复位链被中止」并退出，不覆盖新状态）
6. 成功 → `Stop`，失败 → `Alarm`

前置门禁：运行中拒绝；`IsRobotReachable()` 不通过 → `Alarm` 并阻断（错误归口设备对象层，主设备层不复述，ADR-035）。

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

ADR-030 裁定 C3：**不再监控机器人 pose**，`RobotPose` / `RobotCommand` / `DeviceCommand` 枚举全部删除，
指令一律以 `const string` 解析（[[api/CommandCore]]）。

```
通讯回调 OnCommRecived(msg)
   → CommandCore.Normalize(msg)
   → IsKnownCommand? 否 → Warning 丢弃
   → lock(_commLock) _commCommandQueue.Enqueue(cmd)
                                   ↓
CommCommandWork 线程：DequeueCommand() → DispatchCommand(cmd) → WeldStatusTrans()
```

`DispatchCommand` 现状：`RxAbort` → `EstopMachine`；其余位姿/请求**仅记录**（位姿不再驱动流程），
`RxPreWeldRequest` 待批次 4.5 落地后接入。

---

## 级联范围

| 级联动作 | 覆盖 |
|---|---|
| **上电连接** `CascadeConnect()` | 焊接头、运控、线激光、监控相机（**不含** `WeldParamControlWorkflow`，§8.3 无实体设备） |
| **上电断开** `CascadeDisconnect()` | 同上 |
| **复位** `CascadeResetProcess()` | 上述 4 个 + 焊接工艺（5 个，流程动作非连接动作） |
| **清状态** `CascadeClearStatus()` | 同上 5 个 |
| **焊接工作态迁移** `WeldStatusTrans()` | 同 5 个，各自调自己的 `WeldStatusTrans()` |

> ⚠️ 子流程的 `WeldStatus` 写入口是 `protected`，整机层**无法直接赋值**，
> 故 `WeldStatusTrans()` 是「委托各子流程自行迁移」的编排入口，不是赋值入口。

---

## 模拟模式 API（原 SimulationWorkflow 已删除归并）

原 `SimulationWorkflow.cs` 已删除，全部成员并入本类，**模拟模式真相源 = 本类单例**：

| 成员 | 说明 |
|---|---|
| `bool IsSimulationEnabled` | 模拟是否开启 |
| `void EnableSimulation(SimTestMode mode)` / `void DisableSimulation()` | 开/关模拟（Disable 幂等）；开启时一并拉起 `thSimTestWork`，关闭时置标志位令其自行退出 |
| `void LoadSimulation()` / `void SaveSimulation()` | INI 双文件持久化（新 `SimulationController.ini` + 旧 `MotionControlWorkflow.ini` 回退迁移） |
| `double GetEffectiveRobotX()` | 读模拟线程按节拍发布的 `_simRobotX`；未开启返回 0 |
| `void StartRobotXSimulation()` / `void StopRobotXSimulation()` | 共享模拟 robotX 时钟启停（开启时把起点写入 `_simRobotX`） |
| `void StartSimulationLineLaser()` / `void StopSimulationLineLaser()` / `void ResetSimulationLineLaser()` | 线激光模拟生命周期编排入口（UI 只经这些方法触发） |
| `SimTestMode CurrentMode` / `SelectedMode`、`ShouldUseVirtualCamera`、`ShouldMoveAxis`、`SimStartX`、`SimSpeed`、`SimTargetDistance`、`SeamProfile`、`RandomMode` | 9 个属性原样并入；`SimTestMode` 枚举定义于本文件尾 |

消费方：`MotionControlPage`（开启模拟一键联动）、`FormMain`（启动加载）、`LineLaserWorkflow`（读 `IsSimulationEnabled` / `ShouldUseVirtualCamera` / `GetEffectiveRobotX`）。

> ⚠️ **2026-09-04 用户裁定**：模拟测试改由 `DeviceControlWork` 内的后台线程 `thSimTestWork` 承载（20ms 节拍跑 `SimTick()`），
> 「模拟是 MODE 不是线程」的旧表述**仅对原设计成立**，现行实现为 **MODE + 按需线程**。
> 模拟设计的其余内容（虚拟相机喂数 / 坐标下发运控 / 轨迹注入）待用户修正后补全，当前以 `// todo` 占位。

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
| 8 | 模拟测试设计的其余内容 | `SimTick()` | 用户后续修正 |

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

调用方：`FormMain.cs`（构造/启动/关闭）、`MotionControlPage.cs`（模拟参数）。

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
| `IoSubConnect` … `IoSubAlarmStop` | `public const string` | 子设备级 7 条（原档 §10.3） |
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

**动作不得占用 IO 扫描线程**：`ExecuteIo` 分派的 `DoXxx` 可能耗时数十秒（初始化链要连 4 个子设备）。
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

### 子设备级命令（原档 §10.3）

`DoSubPrework` / `DoSubWork` / `DoSubStop` / `DoSubManualStop` / `DoSubAlarmStop`
统一经 `CascadeWeldStatus(target, reason)` 向 5 个子设备下发
（走基类 `DeviceWorkflowBase.RequestWeldStatus`，因 `SetWeldStatus` 是 protected）。
`IoSubConnect` / `IoSubReset` 属初始化 / 复位内部自动调用，不单独走扫描。

---

## 查询与参数命令（2026-09-04 新增，原档 §10.4 / §10.5）

| 命令 | 签名 | 原档 | 说明 |
|---|---|---|---|
| `GetMainDeviceStatus` | `MainDeviceStatus` | §10.4-14 | 只读，返回 `Current` |
| `GetSubDeviceStatus(tag)` | `SubDeviceWeldStatus` | §10.4-15 | 按子设备 `Tag` 查；未命中返回 `NoReset` |
| `GetAllSubDeviceStatus()` | `Dictionary<string, SubDeviceWeldStatus>` | §10.4-16 | 5 个子设备（4 实体 + 1 虚拟） |
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
若有任一子设备处于 `Standby`（即从 PreWork 退回），判定预检失败，整机回落 `Stop`。
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
| 3 | `SimTick` | 模拟测试设计其余内容（用户后续修正） |
| 4 | `DoSubPrework` 链路 | Preworking 五项检查实值判定（批次 4.5） |
| 5 | Working 四路子流程 | 工艺参数闭环（批次 4.6） |

> ✅ **C3 已由 [[decisions/ADR-030-MainDeviceStateSemantics]] D1 裁定关闭（2026-09-04）**：
> `DoClearAlarm()` 消报**一律回落 `NoReset`**（不再区分 wasRunning 回 Stop），现行代码即此实现。
> 沿革见 [[decisions/OPEN-ClearAlarmSemantics]]（已关闭）。

## 关联

- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（§7 为本类规范，§15.2 为落地批次）
- [[api/CommandCore]] — 机器人指令协议（const string，取代 CommandTable）
- [[api/DeviceStatusWork]] — 安全/IO/状态管控：`IsSafe` 门控 + `MachineIOWorkOpen/Close`
- [[modules/Comm]] — 机器人/PLC 连接归属地
- [[decisions/ADR-027-ThreeStateModelRefactor]] — 三态模型决策
- [[decisions/ADR-029-RawDesignRefinement20260903]] — 本次重构依据（7 线程 + 9 方法 + 裁定 C1~C7）
- [[api/GlobalCommData]] — 通讯与日志底层出口（本类 `_tag` / `_simTag` 的直连落地）
