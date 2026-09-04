---
title: MotionControlWorkflow API 参考（CAMBOX 硬件实时焊缝跟踪 · 三态模型）
date: 2026-09-02
updated: 2026-09-02
tags: [API, 工作流, 运控, CAMBOX, 正运动, RSI, EtherCAT, 实时跟踪, SubDeviceWeldStatus, 执行步, 步骤驱动, ADR-034]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs
---

# MotionControlWorkflow API 参考

> **⚠️ 2026-09-03 架构重构（ADR-036 已裁定，用户定性「完全重构」）**：本页描述的是**改造前**的 API 现状，改码尚未开工。
> 下列机制**已裁定清除，不得据本页改码**：`GoStep`/`SetStep` 改步 · `WorkStep`/`WorkStartTime` · 基类常驻监听线程（`StartRunLoop`/`BeatMs`） · `ManualOn`/`ManualOff` · 命令三槽与机器人 pose 监控 · const int 指令表。
> **现行规范唯一出处**：[[architecture/DeviceControlArchitecture]]（§4 基类 17 项契约 · §5 `RunStep` 驱动 · §7 7 线程编排 · §16 代码模板）。
> 本页将在 [[architecture/DeviceControlArchitecture]] §15 的改码批次完成后同步重写。

> 运控工作流（单例），承载 **CAMBOX 硬件级实时焊缝跟踪**。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：`DeviceWorkflowBase`（非泛型，→ `DeviceStateBase`），`IDisposable` 由基类实现
> 设计依据见 [[decisions/ADR-023-RSICamBoxTrackingArchitecture]]
>
> **✅ 2026-09-02 三态模型重构（ADR-034，accepted）**：旧「设备四态 `DeviceState` + 流程态 `LaserCamBoxWorkflowState`」改为三态模型——连接态 `SubDeviceState` + 焊接过程态 `SubDeviceWeldStatus`；旧 `Step`(流程态枚举) 对外不再暴露，由私有 `_phase`(`LaserCamBoxWorkflowState`) 驱动 `FlowProcess`，对外经 `WeldStatus` 承载。旧 `ManualOn`/`ManualOff` → `ConnectOn`/`ConnectOff`；`StateChanged(WorkflowStepChangedEventArgs<T>)` → `WeldStatusChanged(WeldStatusChangedEventArgs)` + `StateSwitched(SubDeviceStateChangedEventArgs)`。

---

## 定位

- **CAMBOX 跟踪归入运控**，由本类统一承载
- 电子凸轮由**硬件总线**完成实时跟随；PC 侧仅做**启停编排与轨迹规划**，不参与实时运动控制
- 主轴：虚拟编码器轴 axis8（`ATYPE=25`，KUKA PDO 驱动）；从轴：Y 轴 axis0

---

## 核心类

```csharp
public class MotionControlWorkflow : DeviceWorkflowBase
{
    // 单例访问（Lazy<T>）
    public static MotionControlWorkflow Instance { get; }

    // 状态（三态模型）
    public SubDeviceState State { get; }            // 连接态（2 态）
    public SubDeviceWeldStatus WeldStatus { get; }   // 焊接过程态（7 态）
    public bool IsRunning { get; }
    public int WorkStep { get; }
    public string WorkStepName { get; }
    public string StepStatusText { get; }

    // 组件访问
    public CamBoxTracker Tracker { get; }
    public EncoderAxis EncoderAxis { get; }
    public RSIPositionBuffer PositionBuffer { get; }

    // 事件（基类统一提供）
    public event EventHandler<SubDeviceStateChangedEventArgs> StateSwitched;
    public event EventHandler<WeldStatusChangedEventArgs> WeldStatusChanged;
    // 注：TrackingError / PointAdded 已于 2026-08-31 移除（违反 ADR-030 R2）

    // 连接契约 + 生命周期
    public override bool ConnectOn();    // 手动连接（自起后台线程）
    public override void ConnectOff();   // 手动断开（自起后台线程）
    public void Initialize();            // 基类模板 → ConnectOn()
    public void Reset();                  // → ResetProcess()
    public void ClearAlarm();             // → ClearStatus()

    // 运行控制（命令变量受理式）
    public bool Start();                  // 受理启动 → SetWeldStatus(PreWork) → 执行步 10
    public void Stop(bool immediate = false);  // 受理停止 → SetWeldStatus(Stopping) → 执行步 700
    public void Reset();

    // 轨迹与位置
    public bool AddTrajectoryPoint(double laserOffset, DateTime laserTimestamp);
    public void AddRSIPositionSample(long timestamp, double position, double velocity = 0);
    public bool BeginYAxisTracking();

    public void Dispose();
}
```

> **枚举命名提示**：私有阶段枚举名为 `LaserCamBoxWorkflowState`（历史命名，内联于本文件），实现类名已统一为 `MotionControlWorkflow`。二者不同名是历史原因，非缺陷。

---

## 过程态与连接态映射

私有阶段枚举 `LaserCamBoxWorkflowState` 经 `MapWeldStatus(...)` 映射到对外 `SubDeviceWeldStatus`：

| 私有阶段态 `LaserCamBoxWorkflowState` | 焊接过程态 `SubDeviceWeldStatus` | 连接态 `SubDeviceState` |
|---|---|---|
| `Idle`（未初始化） | `Standby` | `Disconnected` |
| `Idle`（已初始化） | `Standby` | `Connected` |
| `Initializing` / `WaitingForMaster` / `Tracking` / `Paused` / `Stopping` | `PreWork`/`Starting`/`Working`/`Stopping`（对应） | `Connected` |
| `Error` | `ErrorAborted` | `Connected` |

### Idle 一态两义（特殊处理）

`Idle` 既可能是"未连接就绪"也可能是"已连接就绪"，按初始化标记区分：

```csharp
case ...:  return SubDeviceWeldStatus.Working;   // 跟踪中
case Error: return SubDeviceWeldStatus.ErrorAborted;
default:   // Idle
    return _initialized ? SubDeviceState.Connected : SubDeviceState.Disconnected;
```

---

## 关键行为

### ConnectOn（自动初始化，受理式）

配置 `CamBoxTracker`、`EncoderAxis`、`RSIPositionBuffer` 三组件并绑定正运动控制器句柄。由 `DeviceControlWork` 自动初始化（`InitializeMachine`）第 2 步调用（`ConnectOn()`），句柄取自 `zmController.GetHandle()`。未检测到正运动控制器时跳过。

### 后台监控（基类监听线程）

`FlowProcess()` **每拍开头**调 `UpdateTrackerStatus()`（`_tracker.UpdateStatus()` + `_encoderAxis.UpdateStatus()` + `SyncStateFromTracker()`），节拍 `BeatMs = 20`（50Hz，与原设计一致）。

---

## 执行步表（内部游标）

| 步号 | 中文名 | 内容 | 出口 |
|---|---|---|---|
| 0 | 空闲待机 | 非运行阶段态 | — |
| 10 | 启动-清零编码器轴 | `_encoderAxis.Reset()`（必须在 CAMBOX 启动前） | → 20 |
| 20 | 启动-启动 CAMBOX | `_tracker.Start()`；失败留原步重入重试，超时 5s | → 30 / 900 |
| 30 | 启动-等待主轴运动 | 等 `SyncStateFromTracker` 转 `Tracking`（超时 120s） | → 100 / 900 |
| 100 | 跟踪中 | 空转（周期状态刷新已在每拍开头完成） | — |
| 110 | 暂停中-等待恢复 | 激光丢帧暂停，恢复回 100；超时 30s | → 100 / 900 |
| 700 | 停止收尾 | `tracker.Stop(false)` + `encoderAxis.Reset()` + `buffer.Clear()` → `SetWeldStatus(Standby)` | → 0 |
| 900 | 失败收尾 | `SetWeldStatus(ErrorAborted)` + `IsAlarm` + `RecordFault` | → 0 |

**超时阈值常量**：`CamBoxStartTimeoutMs=5000` / `MasterWaitTimeoutMs=120000` / `PausedTimeoutMs=30000`。

> **行为变化**：`Start()` 由「同步完成清零编码器 + 启动 CAMBOX 后返回」改为「**受理指令**后返回，实际动作由监听线程按执行步完成」。返回值语义变为「指令是否受理」，硬件启动结果请读 `WeldStatus`（`PreWork`/`Working`）。调用方 `MotionControlPage.cs` 经 `WeldStatus` 观察状态，兼容。

### 轨迹点追加

`AddTrajectoryPoint(laserOffset, laserTimestamp)` — 追加激光偏移轨迹点，内部与 `RSIPositionBuffer` 中的位置序列做时间戳插值对齐。

---

## UI 接入

```csharp
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;

var wf = MotionControlWorkflow.Instance;
var status = wf.WeldStatus;   // 焊接过程态
// 启停
wf.Start();
wf.Stop();
```

调用方：`MotionControlPage.cs`（启停按钮）、`FormMain.cs`

---

## 关联

- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（第 10 章 运动控制）
- [[api/CamBoxTracker]] — CAMBOX 跟踪引擎
- [[api/EncoderAxis]] — ATYPE=25 通讯编码器轴
- [[api/RSIPositionBuffer]] — RSI 位置时间戳环形缓冲
- [[modules/MotionControl]] — 运控硬件层
- [[decisions/ADR-023-RSICamBoxTrackingArchitecture]] — CAMBOX 架构决策
- [[decisions/ADR-034-ThreeStateModelRefactor]] — 本次三态模型决策（现行有效）
