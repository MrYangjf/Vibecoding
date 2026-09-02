---
title: DeviceControlWork API 参考（整机主控 · 主设备运行态 MainDeviceStatus）
date: 2026-09-02
tags: [API, 工作流, 主控, 上电初始化, 机器人交互, 主设备运行态, 模拟, DeviceControlWork, ADR-049]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/DeviceControlWork.cs
---

# DeviceControlWork API 参考

> **本页述 `DeviceControlWork`（单例，整机运行主控）**，见 [[decisions/ADR-049-ThreeStateModelRefactor]]。
> 主设备对外状态为 **运行态 `MainDeviceStatus`**（6 态：Running/Alarm/EStop/Stop/NoReset/Reseting），由 `SetStatus(...)` 单一入口写入，禁手工赋值。
>
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/DeviceControlWork.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：**独立管控类，不继承 `DeviceWorkflowBase`/`DeviceStateBase`**；自带运行线程（节拍 `BeatMs=10`）与内部执行步（`_workStep` + `GetStepName`）。
> 架构背景见 [[architecture/DeviceControlArchitecture]] 第 7 章。

---

## 核心类

```csharp
public class DeviceControlWork
{
    // 单例访问（Lazy<T>）
    public static DeviceControlWork Instance { get; }

    // 主设备运行态（6 态，过程状态）
    public MainDeviceStatus Status { get; }                 // Running/Alarm/EStop/Stop/NoReset/Reseting
    public event EventHandler<MainDeviceStatusChangedEventArgs> StatusChanged;  // OldStatus/NewStatus/Reason/Timestamp

    // 内部执行步（可观测）
    public int WorkStep { get; }
    public string WorkStepName { get; }
    public bool IsWelding { get; }          // 焊接中

    // 命令变量入口（回调只赋值不做业务）
    public void ReceiveRobotPose(RobotPose pose);
    public void ReceiveRobotCommand(RobotCommand cmd);

    // 对外操作契约（基类无，本类直供）
    public bool InitializeMachine();        // 上电初始化级联 5 步
    public bool StartMachine();             // 拉起 DeviceStatusWork + RunLoop，置 Stop（就绪，幂等）
    public void StopMachine();              // 停线程 → 级联 ClearStatus×5 → CascadeDisconnect → CloseWork → 置 Stop
    public bool ResetMachine();             // 在位检测(阻断) → 清命令变量 → Reseting → 级联 ResetProcess×5 → Stop
    public bool ClearAlarm();               // 仅清报警标志：Alarm → NoReset
    public void EStopMachine(string reason);// → SetStatus(EStop)
    public void EStopCancel();              // → SetStatus(NoReset)
    public void EmergencyStop();
    public void ReportAlarm(string reason);
    public void ReportAlarmCleared();

    // 模拟模式（原 SimulationWorkflow 归并，ADR-048/049）
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

    public void Dispose();
}
```

> **日志出口（2026-09-03 统一）**：本类全部日志经私有 `Log(...)` → `DeviceLog.Write(_tag, ...)`；
> 模拟模式相关另用 `_simTag` → `DeviceLog.Write(_simTag, ...)`。
> **禁止**在 `MainDeviceControl/` 下直接调 `GlobalCommData.ShowLog`。见 [[api/DeviceLog]]。

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

唯一写入入口：`private void SetStatus(MainDeviceStatus newStatus, string reason)`（触发 `StatusChanged` 并记日志）。

### 状态读取红线（2026-09-03 修复，强制）

`_status` 由 `_statusLock` 保护，**任何业务读取必须走 `Status` 属性**，禁止裸读 `_status`——
加锁与不加锁的读混用，等于没加锁。

```csharp
if (Status != MainDeviceStatus.Stop) ...     // 正确
if (_status != MainDeviceStatus.Stop) ...    // 错误：绕过锁
```

**合法裸读仅 5 处**（审计残留白名单）：字段声明、`_statusLock` 声明、`Status` getter 内、`SetStatus` 锁内写块、
`ClearAlarm` 内的 check-and-set（必须与写入同处一把锁内，拆开会产生 TOCTOU）。

### 步时间与超时不变量（2026-09-03 修复）

本类**不继承 `DeviceWorkflowBase`**，自带私有步机制，须与基类保持同源不变量：

| 不变量 | 实现 | 违反后果 |
|---|---|---|
| 步号与时间成对刷新 | `GoStep(n)`：`_workStep = n;` + `Interlocked.Exchange(ref _workStartTicks, ...)` | 超时判定基准错乱 |
| 非运行态持续刷新时间戳 | `RunLoop()` 的 `else { ResetStepTime(); }` 分支 | **停机超 60s 后再开机，首拍即误判超时跳 900 失败收尾** |
| 重启复位步 | `StartMachine()` 内 `GoStep(StepIdle)` | 沿用停机时刻的步号与时间戳，同样误判 |
| 64 位字段原子读写 | `Interlocked.Exchange` / `Interlocked.Read` | 32 位平台读到撕裂值，`DateTime` 构造出荒谬时间 |

> ⚠️ 本类曾因漏抄基类「非运行态刷新」分支而出现停机久后开机即报超时。
> 详见 [[lessons/DeviceControlWorkInheritanceBypass]] 坑三/坑五，规范见 [[standards/StepDrivenWorkflow]] §2.2。

---

## 上电初始化：5 步同步顺序执行

```csharp
DeviceControlWork.Instance.InitializeMachine();   // 上电初始化入口（阻塞同步 5 步级联）
```

| 步骤 | 内容 | 调用 |
|---|---|---|
| `[1/5]` | 焊接头 | `LaserWeldHeadController.Instance.ConnectOn()` |
| `[2/5]` | 运动控制器 + CAMBOX 跟踪 | `MotionManager.Initialize()` + `MotionControlWorkflow.ConnectOn()` |
| `[3/5]` | 线激光相机 | `LineLaserWorkflow.ConnectOn()` |
| `[4/5]` | 监控相机 | `MonitorCameraWorkflow.ConnectOn()` |
| `[5/5]` | 机器人通讯 | RSI / EKI 二选一 |

末步执行 `EvaluateInitializationResult()` 聚合判定：子设备全 `Connected` → `SetStatus(Stop)`（整机就绪）；否则 → `SetStatus(Alarm)`。

### 聚合判定口径

子设备连接态 `SubDeviceState.Connected` 视为正常；其余（`Disconnected`）计为未就绪。

---

## 关键边界：机器人/PLC 连接不属于本工作流

机器人和 PLC 的连接是外部设备通讯，由顶层 `Comm`（`CommunicationManager`）管控。本工作流只做**信号交互**：

| 方向 | 内容 |
|---|---|
| 接收 | `RobotPose`（机器人状态上报），经 `GlobalCommData.CommunicationCommandReceived` 到达 |
| 下发 | `DeviceCommand`（`CmdGoXxx` 对齐 Pose + `CmdOK` + `CmdAbort`），经 `GlobalCommData.mCommunicationManager.RobotManager.SendRobotData(...)` |

不直接持有连接、不直接操作 socket。详见 [[modules/Comm]]。

> **命令变量三槽（关键）**：接收侧回调**只写命令变量**（`ReceiveRobotPose` / `ReceiveRobotCommand`），不做业务；`ConsumeCommand()` 在运行线程内按「Abort → Command → Pose」顺序取快照并清零，避免重入。
> ⚠️ `RobotCommand.PreWeldRequest = 1` 与 `RobotPose.StartSafePose = 1` **编码区间重叠**，故 Pose / Command 必须分槽存放，单槽会丢指令。

---

## 级联范围

自动初始化（`InitializeMachine`）级联的子设备：**焊接头、运控、线激光、监控相机、机器人通讯**（5 项），经各子设备 `ConnectOn()` 受理式连接。

> **不含 `WeldParamControlWorkflow`**——焊接工艺控制流程由 `LineLaserWorkflow` 在连续成功帧达阈值时触发，保持单一驱动源（[[decisions/ADR-013-WorkflowAsAdjustmentDriver]]）。

---

## 模拟模式 API（原 SimulationWorkflow 已删除归并）

原 `SimulationWorkflow.cs` 已删除（ADR-048），全部成员并入本类，**模拟模式真相源 = 本类单例**：

| 成员 | 说明 |
|---|---|
| `bool IsSimulationEnabled` | 模拟是否开启 |
| `void EnableSimulation(SimTestMode mode)` / `void DisableSimulation()` | 开/关模拟（Disable 幂等） |
| `void LoadSimulation()` / `void SaveSimulation()` | INI 双文件持久化 |
| `double GetEffectiveRobotX()` | 模拟开启返 `SimStartX + SimSpeed × elapsed`，否则 0 |
| `void StartRobotXSimulation()` / `void StopRobotXSimulation()` | 共享模拟 robotX 时钟启停 |
| `void StartSimulationLineLaser()` / `void StopSimulationLineLaser()` / `void ResetSimulationLineLaser()` | 线激光模拟生命周期编排入口（UI 只经这些方法触发） |
| `SimTestMode CurrentMode` / `SelectedMode`、`ShouldUseVirtualCamera`、`ShouldMoveAxis`、`SimStartX`、`SimSpeed`、`SimTargetDistance`、`SeamProfile`、`RandomMode` | 9 个属性原样并入；`SimTestMode` 枚举定义于本文件尾 |

消费方：`MotionControlPage`（开启模拟一键联动）、`FormMain`（启动加载）。「模拟是 MODE 不是线程」理念承袭 ADR-017（部分取代），见 [[decisions/ADR-048-AutoManualDualWorkflow]] §4。

---

## UI 接入

```csharp
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;

var main = DeviceControlWork.Instance;
main.StatusChanged += OnMainDeviceStatusChanged;   // 统一入口：Stop 即整机就绪，Running 即焊接中
bool welding = main.IsWelding;

// 现场排故：卡在哪个子步、卡了多久
string status = "step:" + main.WorkStep + " " + main.WorkStepName;
```

> **红线**：UI 线程禁止直接驱动内部运行线程。驱动主设备工作流**必须**走 `InitializeMachine()` / `StartMachine()` / `StopMachine()` / `ResetMachine()` / `ClearAlarm()` / `EStopMachine()` 等对外契约；禁止直接调内部编排方法。

调用方：`FormMain.cs`（构造/启动/关闭）

---

## 关联

- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页
- [[modules/Comm]] — 机器人/PLC 连接归属地
- [[modules/Safety]] — `DeviceStatusWork.IsSafe` 门控接入
- [[decisions/ADR-049-ThreeStateModelRefactor]] — 本次归并重命名决策（现行有效）
- ADR-041（已删除，见 ADR-049） — 已被取代（历史参考）
- [[decisions/ADR-048-AutoManualDualWorkflow]] — 双流程模型 + 模拟归并决策
- [[api/DeviceLog]] — 日志统一出口（本类 `_tag` / `_simTag` 的落地）
- [[lessons/DeviceControlWorkInheritanceBypass]] — 状态直读 / 时间戳非原子 / 停机重启误判超时 三类 BUG 根因
- [[api/DeviceControlWork]] — 墓碑（已删除，真相源=本页）
