---
title: LineLaserWorkflow API 参考（三态模型：SubDeviceState / SubDeviceWeldStatus）
date: 2026-09-02
updated: 2026-09-02
tags: [API, 工作流, 状态机, 英莱, 线激光, SubDeviceWeldStatus, 执行步, 步骤驱动, ADR-049]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs
---

# LineLaserWorkflow API 参考

> 英莱线激光焊缝跟踪工作流（单例）。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：`DeviceWorkflowBase`（非泛型，→ `DeviceStateBase`），`IDisposable` 由基类实现
> 架构背景见 [[modules/DeviceControl]]、[[architecture/DeviceControlArchitecture]]
>
> **✅ 2026-09-02 三态模型重构（ADR-049，accepted）**：旧「设备四态 `DeviceState` + 流程态 `LineLaserWorkflowState`」改为三态模型——连接态 `SubDeviceState` + 焊接过程态 `SubDeviceWeldStatus`；旧 `Step`(流程态枚举) 对外不再暴露，由私有 `_phase`(`LineLaserWorkflowState`) 驱动 `FlowProcess`，对外经 `WeldStatus`(`SubDeviceWeldStatus`) 承载。旧 `ManualOn`/`ManualOff` → `ConnectOn`/`ConnectOff`；`StateChanged(WorkflowStepChangedEventArgs<T>)` → `WeldStatusChanged(WeldStatusChangedEventArgs)` + `StateSwitched(SubDeviceStateChangedEventArgs)`。
> 步骤驱动规范见 [[standards/StepDrivenWorkflow]]。

---

## 概述

两层状态：连接态 `State`(`SubDeviceState`)，由 `ConnectOn`/`ConnectOff` 联动；焊接过程态 `WeldStatus`(`SubDeviceWeldStatus`)，由流程方法经私有 `SetStep` → `SetWeldStatus(MapWeldStatus(...))` 联动；执行步 `WorkStep`（内部游标，经 `GoStep` 推进）。

`LineLaserWorkflowState` 枚举已**降级为私有字段**，内联于本文件（命名空间 `AdaWeldSystem.MainDeviceControl.DeviceWorkflow`）。

### 在工作流体系中的角色

- 由 `DeviceControlWork` 上电初始化（`InitializeMachine`）经 `ConnectOn()` 连接
- 连续成功帧达到阈值时触发 `WeldParamControlWorkflow.ComputeAndOutput()`（焊接工艺计算与下发）
- 数据流见 [[decisions/ADR-039-YinglaiDataFlow]]

---

## 核心类

```csharp
public class LineLaserWorkflow : DeviceWorkflowBase
{
    // 单例访问
    public static LineLaserWorkflow Instance { get; }

    // 状态属性（三态模型）
    public SubDeviceState State { get; }            // 连接态（2 态），基类提供
    public SubDeviceWeldStatus WeldStatus { get; }   // 焊接过程态（7 态），基类提供
    public int WorkStep { get; }                     // 执行步（内部游标）
    public string WorkStepName { get; }
    public string StepStatusText { get; }            // "step:30 / 8.2s 启动中-等待数据稳定"

    // 运行态属性
    public bool IsPreWorkDone { get; }
    public bool IsDataStable { get; }

    // 事件（基类统一提供）
    public event EventHandler<SubDeviceStateChangedEventArgs> StateSwitched;       // 连接态变更
    public event EventHandler<WeldStatusChangedEventArgs> WeldStatusChanged;        // 焊接过程态变更

    // 连接契约（基类 abstract，UI 开关按钮直调）
    public override bool ConnectOn();     // 手动连接（自起后台线程）
    public override void ConnectOff();    // 手动断开（自起后台线程）

    // 生命周期（基类模板）
    public void Initialize();             // → ConnectOn() 阻塞同步
    public void Reset();                   // → ResetProcess()
    public void ClearAlarm();              // → ClearStatus()
    public void Start();                   // → StartRunLoop()
    public void Stop();                    // → StopRunLoop()
    public void Dispose();                 // 基类实现（模板方法 + DisposeManaged 钩子）

    // 分步驱动（命令变量触发）
    public void BeginStarting();
    public void BeginWorking();
}
```

---

## 执行步表（内部游标）

| 步号 | 中文名 | 内容 | 出口 |
|---|---|---|---|
| 0 | 待机 | 非运行阶段态 | — |
| 10 | 启动前准备-清理状态与外设 | 复位计数/标志 + `SafeShutdownPeripherals()` + 置 `_preWorkDone` | → 11 |
| 11 | 启动前准备-等待进入 Starting | 等主设备 `BeginStarting()`（超时 30s）；模拟模式自驱动 | → 20 / 900 |
| 20 | 启动中-开传感器与激光 | `SetSensor(true)` + `SetLaser(true)`；虚拟相机直接判稳 | → 30 / 31 |
| 30 | 启动中-等待数据稳定 | 等相机回调查满 5 帧置 `_dataStable`（超时 10s） | → 31 / 900 |
| 31 | 启动中-等待进入 Working | 等主设备 `BeginWorking()`（超时 30s）；模拟模式自驱动 | → 100 / 900 |
| 100 | 工作中-焊接与自适应调整 | 行程达 `_maxWeldLength` → 700；`_adjustmentPending` → `RunAutoAdjust()` | → 700 |
| 700 | 停止中-关闭外设 | `SafeShutdownPeripherals()` | → 800 |
| 800 | 成功收尾 | `SetWeldStatus(Standby)` | → 0 |
| 900 | 失败收尾 | `SetWeldStatus(ErrorAborted)` + `IsAlarm` + `RecordFault` | → 0 |

**超时阈值常量**：`PreWorkWaitTimeoutMs=30000` / `DataStableTimeoutMs=10000` / `WaitWorkingTimeoutMs=30000` / `FirstResultTimeoutMs=5000`。

> **命名**：步号常量（私有）`StepPreWork=10` / `StepPreWorkWait=11` / `StepStartingOn=20` / `StepStartingStable=30` / `StepStartingWaitWork=31` / `StepWorking=100` / `StepStopping=700`；单步方法统一 `DoXxx()`。通用三常量 `StepIdle`/`StepFinishOk`/`StepFinishFail` 与 `FailFlow(reason)` 由基类下沉。

### 行为变化（重要）

- **等待主设备通知的超时语义**：改造前 PreWork / 数据稳定后为「30 秒超时后继续无限等待」，改造后为「30 秒超时 → 失败收尾 → `ErrorAborted`」（符合 ADR-047「不得留在原步死等」）。
  **⚠️ `BeginStarting()` / `BeginWorking()` 目前无主设备调用方**，UI 单独调试（`MotionControlPage` 直接 `Start()`）时 30 秒后会报警；调试请启用模拟模式自驱动或由主设备补齐分步驱动。
- **相机绑定/解绑时机**：`Start()` 内 `BindCamera()`；离开运行态时在 `OnWeldStatusChanged` 内 `ReleaseCameraBinding()`。
- **失败计数不再每拍累加**：改造前每 5ms 调一次 `HandleFailure` 会瞬间打满；改造后需持续 5s 无有效结果才计一次。

---

## 连接契约（✅ 2026-09-02 修订）

| 方法 | 说明 |
|---|---|
| `ConnectOn()` | 手动连接（`public override`，自起后台线程直接 `ConnectManual` 并置 Connected，UI 开关按钮直调） |
| `ConnectOff()` | 手动断开（`public override`，自起后台线程 `DisconnectManual` + 关外设） |
| `Initialize()` | 初始化（基类模板，内部 `ConnectOn()` 阻塞同步三步 connect→readConfiguration→verifyHardwareStatus，成功→`Connected`，失败→`Disconnected`） |

> `State` / `WeldStatus` / `StateSwitched` / `WeldStatusChanged` / `GoStep` / `FlowProcess` / `ConnectOn` / `ConnectOff` / `ResetProcess` / `ClearStatus` / `GetStepName` 均由基类提供或约束，本文件内看不到定义属正常。

---

## 过程态与连接态映射

私有阶段枚举 `LineLaserWorkflowState` 经 `MapWeldStatus(...)` 映射到对外 `SubDeviceWeldStatus`：

| 私有阶段态 `LineLaserWorkflowState` | 焊接过程态 `SubDeviceWeldStatus` | 连接态 `SubDeviceState` |
|---|---|---|
| `Uninitialized` | `Standby` | `Disconnected` |
| `Standby` / `ManualStopped` | `Standby` | `Connected` |
| `Initializing` / `PreWork` / `Starting` / `Working` / `Stopping` | `PreWork`/`Starting`/`Working`/`Stopping`（对应） | `Connected` |
| `ErrorAborted` | `ErrorAborted` | `Connected` |

> 过程态写入统一经私有 `SetStep(phase, reason)` → `SetWeldStatus(MapWeldStatus(phase), reason)`，**禁止手工 `WeldStatus = ...` 赋值**。

---

## 关键行为

### ConnectOn（手动连接，阻塞同步）

阻塞同步执行三步初始化（connect → readConfiguration → verifyHardwareStatus），成功后 `SetState(Connected)` + `SetWeldStatus(Standby)`；失败 `SetState(Disconnected)` + `SetWeldStatus(ErrorAborted)`。复位职责（关激光/关传感器）归 `ResetProcess`。

### 触发焊接工艺计算

Working 态中，当连续成功帧计数达到 `_adjustTriggerSuccessCount` 时：

```csharp
var ir = e.Inspect;                          // 英莱回调结果
var sf = new SeamFeatureResult();
sf.CenterY   = ir.FeatureY;
sf.CenterX   = ir.FeatureZ;
sf.SeamWidth = (ir.Width0 + ir.Width1) * 0.5;
sf.SeamArea  = ir.Area;
double robotX = GetCurrentRobotX();
PipelineManager.Instance.ReportExternalResult(sf, robotX, null);
_lastAdjustSuccess = WeldParamControlWorkflow.Instance.ComputeAndOutput();
```

**焊缝信息即英莱线激光的结果**——回调本就含 `FeatureY/FeatureZ`（特征点）与 `Width0/Width1`（宽度）。

### 待机安全默认态

`Standby` 时传感器与激光**均关闭**（安全默认态）。

---

## UI 接入

```csharp
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;
using AdaWeldSystem.MainDeviceControl.DeviceState;   // 读 SubDeviceState / SubDeviceWeldStatus 枚举

var wf = LineLaserWorkflow.Instance;
var status = wf.WeldStatus;   // 焊接过程态：判断是否运行、显示分步进度
var state  = wf.State;        // 连接态：判断能否操作、销毁前是否断开
```

调用方：`FormMain.cs`、`ILCamPage.cs`、`MotionControlPage.cs`、`MainPage.cs`

---

## 关联

- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页
- [[modules/WeldParamControl]] — 焊接工艺计算链路
- [[decisions/ADR-039-YinglaiDataFlow]] — 英莱数据流
- [[decisions/ADR-035-LineLaserWorkflowRefactor]] — 分步重构
- [[decisions/ADR-049-ThreeStateModelRefactor]] — 本次三态模型决策（现行有效）
