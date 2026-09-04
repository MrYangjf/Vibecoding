---
title: MotionControlWorkflow API 参考（CAMBOX 硬件实时焊缝跟踪 · 三态模型）
date: 2026-09-02
updated: 2026-09-04
tags: [API, 工作流, 运控, CAMBOX, 正运动, RSI, 实时跟踪, RunStep, SubDeviceWeldStatus, DeviceWorkflowBase, ADR-034, ADR-036]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs
---

# MotionControlWorkflow API 参考

> 运动控制工作流（单例），承载 **CAMBOX 硬件级实时焊缝跟踪**（启动/停止编排器，不参与实时运动控制）。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：非泛型 `DeviceWorkflowBase`（17 项契约）→ `DeviceStateBase`；`IDisposable` 由基类实现。
> 设计依据见 [[decisions/ADR-023-RSICamBoxTrackingArchitecture]]。

> **✅ 2026-09-04 已落地（ADR-036 批次 0~4.4）**：本类已按新架构改码——无自带线程（由 `DeviceControlWork` 子设备线程驱动 `FlowProcess()`，每拍开头刷跟踪状态）、`RunStep` 每 case 靠 bool 推进、跟踪引擎异常只记日志不上抛（订阅方直订 `Tracker.TrackingError`）。旧 `GoStep`/`SetStep`/`WorkStep`/`StartRunLoop`/`BeatMs`/`ManualOn`/`ManualOff`/命令三槽等机制已全部清除，不得据旧内容改码。真编译待 VS（静态自检已通过）。
> 步骤驱动规范见 [[architecture/DeviceControlArchitecture]] §4（17 契约）· §5（`RunStep` 驱动）· §16（代码模板）。

---

## 定位

- **CAMBOX 跟踪归入运控**，由本类统一承载；电子凸轮由**硬件总线**完成实时跟随，PC 侧仅做启停编排与轨迹规划。
- 主轴：虚拟编码器轴 axis8（`ATYPE=25`，KUKA PDO 驱动）；从轴：Y 轴 axis0。
- 本类**不产出设备数据**；跟踪点/跟踪异常的订阅方直接订阅 `Tracker` 属性暴露的 `CamBoxTracker`（权责边界，ADR-030 R2）。
- 差异化职责（原档 R011）：**检测送丝位置和焊接质量阈值**——`SubDeviceLog()` 内 `// todo`，待硬件点位明确后落地。

---

## 公共成员

| 成员 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static MotionControlWorkflow` | `Lazy<T>` 单例 |
| `StateName` | `override string` | 对外名片名，返回 `Tag`（日志/事件标识） |
| `Tracker` | `CamBoxTracker` | CAMBOX 跟踪引擎（跟踪点/异常事件直订源） |
| `EncoderAxis` | `EncoderAxis` | 通讯编码器主轴（axis8，ATYPE=25） |
| `PositionBuffer` | `RSIPositionBuffer` | RSI 位置时间戳环形缓冲 |
| `IsRunning` | `bool` | 是否正在运行（`Tracking` 或 `WaitingForMaster`） |
| `State` / `WeldStatus` | 基类属性 | 连接态（`SubDeviceState`）/ 焊接过程态（`SubDeviceWeldStatus`） |
| `RunStep` / `StepWorkTime` / `WorkStepName` / `StepStatusText` | 基类属性 | 执行步 / 步骤用时 / 步中文名 / 可观测摘要 |

> `ConfigFileName = "MotionControlWorkflow"`（protected override，配置落在 `Config/XML/` 下）。
> **枚举命名提示**：相位枚举名为 `LaserCamBoxWorkflowState`（历史命名，与实现类 `MotionControlWorkflow` 不同名，非缺陷）。

---

## 私有相位 `LaserCamBoxWorkflowState`（同文件公共枚举）

`_phase`（默认 `Idle`）仅驱动 `FlowProcess` 与可观测性，对外经 `SetWeldStatus(MapWeldStatus(phase))` 映射：

| 取值 | 含义 | 映射 `SubDeviceWeldStatus` |
|---|---|---|
| `Idle` | 空闲（未启动） | `Standby` |
| `Initializing` | 初始化中（配置三组件） | `PreWork` |
| `WaitingForMaster` | 等待主轴运动（机器人开始进给） | `Working` |
| `Tracking` | 正常跟踪中（硬件 CAMBOX 实时跟随） | `Working` |
| `Paused` | 临时暂停（激光丢帧等可恢复中断） | `Working` |
| `Stopping` | 停止中 | `Stopping` |
| `Error` | 异常（EtherCAT 断连等严重错误） | `ErrorAborted` |

> `SetPhase(phase, reason)` 是相位唯一写入口：刷新 `_phase` → `SetWeldStatus(MapWeldStatus(phase), reason)` → 把执行步复位到该阶段入口（`WaitingForMaster`→10、`Tracking`→100、`Paused`→110、`Stopping`→700、其余→0）。
> ⛔ 禁止手工 `WeldStatus = ...` / `State = ...` 赋值。

---

## 执行步表（`RunStep` 驱动）

| 步号 | 常量 | 中文名 | 内容 | 出口 |
|---|---|---|---|---|
| 0 | `StepIdle`（基类） | 空闲待机 | 非运行阶段态 | — |
| 10 | `StepResetEncoder` | 启动-清零编码器轴 | `_encoderAxis.Reset()`（必须在 CAMBOX 启动前） | → 20 |
| 20 | `StepStartCamBox` | 启动-启动CAMBOX | `_tracker.Start()`；失败留原步重入，超时 5s → `Fail("CAMBOX 启动超时")` | → 30 / 900 |
| 30 | `StepWaitMaster` | 启动-等待主轴运动 | 等 `SyncPhaseFromTracker` 转 `Tracking`；超时 120s → `Fail` | → 100 / 900 |
| 100 | `StepTracking` | 跟踪中 | `ApplySpotAlignCompensation()`（消费光斑对准偏差驱动振镜，`// todo` 摆幅落地） | — |
| 110 | `StepPaused` | 暂停中-等待恢复 | 等 `SyncPhaseFromTracker` 回 `Tracking`；超时 30s → `Fail` | → 100 / 900 |
| 700 | `StepStopping` | 停止收尾 | `_tracker.Stop(false)` + `_encoderAxis.Reset()` + `_positionBuffer.Clear()` → `SetPhase(Idle)` | → 0 |
| 900 | `StepFinishFail`（基类常量） | 失败收尾 | `SetPhase(Error)` + `IsAlarm` + `RecordFault`（`MotionStepFail`） | → 0 |

**超时/常量**（秒）：`CamBoxStartTimeoutSeconds=5` / `MasterWaitTimeoutSeconds=120` / `PausedTimeoutSeconds=30`。

### `FlowProcess()` switch 骨架（每拍先刷状态）

```
if (!IsEnable) return;
UpdateTrackerStatus();          // _tracker.UpdateStatus + _encoderAxis.UpdateStatus + SyncPhaseFromTracker
switch (RunStep) {
    case 10:  if (DoResetEncoder()) AdvanceStep(20);   break;
    case 20:  if (DoStartCamBox())  AdvanceStep(30);   break;
    case 30:  if (DoWaitMaster())   AdvanceStep(100);  break;
    case 110: if (DoPaused())       AdvanceStep(100);  break;
    case 700: if (DoStopping())     AdvanceStep(0);    break;
    case 900: if (DoFinishFail())   AdvanceStep(0);    break;
    case 100: ApplySpotAlignCompensation();            break;  // 跟踪中：消费光斑对准偏差
    default:  break;   // StepIdle 与未登记步：空转，靠相位切换复位
}
```

> ⛔ 全部 case 无 `Thread.Sleep` / `while` 轮询：等待靠「外部线程重入 + `IsTimeout(seconds)`」判定。
> `SyncPhaseFromTracker()` 把 `CamBoxTracker.State` 同步到工作流相位：`Tracking` → `SetPhase(Tracking)`、`Paused` → `SetPhase(Paused,"激光丢帧暂停")`、`Error` → `Fail("跟踪引擎异常")`。

---

## 关键行为

### Initialize（三参数，公共）

```csharp
public bool Initialize(CamBoxTrackingConfig trackingConfig, EncoderAxisConfig encoderConfig, IntPtr controllerHandle)
```

`controllerHandle == IntPtr.Zero` → 失败。流程（`lock(_lock)`）：`SetPhase(Initializing)` → ① `_encoderAxis.Initialize(encoderConfig, handle)` ② `_tracker.Initialize(trackingConfig, handle, _positionBuffer)` ③ `_positionBuffer.Clear()`；任一步失败 → `SetPhase(Error)` + `State=Disconnected` + false。成功 → `_initialized=true` + `SetPhase(Idle)` + `State=Connected` + `WeldStatus=NoReset`。

### Start / Stop（受理式）

- `Start()`：要求已初始化（`_tracker`/`_encoderAxis` 非空，否则 false）→ `SetPhase(WaitingForMaster)`（执行步 10 起，由编排线程完成后续清零/启 CAMBOX/等主轴）。**受理即返回**，硬件启动结果读 `WeldStatus`。
- `Stop(bool immediate = false)`：`immediate=true` 先 `_tracker.Stop(true)`；`Idle`/`Error` 态忽略；否则 `SetPhase(Stopping)`（执行步 700 完成停 CAMBOX 与复位）。

### 轨迹写入（非实时）

- `AddTrajectoryPoint(double laserOffset, DateTime laserTimestamp)` → `_tracker.AddTrajectoryPointWithTimestamp(...)`（时间戳插值 + 前置补偿 + 写入，最常用方法）。
- `AddRSIPositionSample(long timestamp, double position, double velocity = 0)` → `_positionBuffer.AddSample(...)`。
- `BeginYAxisTracking()`：焊前阶段由主设备调用；当前为**骨架实现，恒返回 true**（`// TODO` 基于机器人焊前位执行 Y 轴偏移跟踪并回报结果）。

### 光斑对准偏差消费（原档20260904 §7.4.5 / §7.5.2 步骤⑤）

`StepTracking` 内 `ApplySpotAlignCompensation()`：读 `DeviceControlWork.Instance.AlignDatum` 只读中枢（ADR-030：产出方持有、消费方取用），把 `OffsetX`/`OffsetY` 存入私有 `_lastSpotOffsetX/Y`（供振镜补偿与调试观测）；`// todo` 振镜摆动控制待 `WeldParamControlWorkflow.LastOutput.GalvoAmplitude` 摆幅基准落地后实现。

> 用户 2026-09-04 裁定：监控相机**只给结果**（对中 OK/NG + 偏差值），光斑对准偏差由**控制器**消费以驱动振镜摆动光斑，相机不自行补偿。

### 跟踪引擎异常

`_tracker.TrackingError += OnTrackerError`（构造函数订阅）→ 仅 `Log` 错误，不上抛为工作流事件（订阅方直接订阅 Tracker）。

---

## 连接 / 生命周期契约

| 方法 | 语义 | 状态联动 |
|---|---|---|
| `InitializeOn()` | 阻塞连接：`MotionManager.Initialize()`；无正运动控制器（`DefaultController` 非 `ZMotionController`）→ 记 Warning + `State=Connected`（无 CAMBOX）跳过；否则取 `MotionConfigManager.Config` 三参数 `Initialize(...)` | 成功 `State=Connected`；失败 `State=Disconnected` |
| `InitializeOff()` | 阻塞断开：`_tracker.Stop(true)` + 复位编码器 + 清缓冲 → `SetPhase(Idle)` | `State=Disconnected` + `WeldStatus=NoReset` |
| `ConnectOn()` | 非阻塞：要求 `_initialized`（否则 false） | `State=Connected` |
| `ConnectOff()` | 非阻塞：`Stop(false)` | `State=Disconnected` |
| `ResetProcess()` | 线性阻塞链：清凸轮表（`_tracker.Reset()`）+ 清缓冲 + 复位编码器 → `SetPhase(Idle)` | `WeldStatus=Standby` |
| `ClearStatus()` | 复位前状态清理 | `WeldStatus=NoReset` |
| `ResetWorkTime()` | `ResetStepTime()`（基类） | — |
| `WeldStatusTrans()` | `NoReset` return；`Stopping` 且相位非 Stopping → `SetPhase(Stopping)`；`ManualStopped`/`ErrorAborted` 且相位非 Idle → `SetPhase(Idle)` | — |

---

## 配置项（`ConfigFileName = "MotionControlWorkflow"`）

| 配置元素 | 默认值 | 说明 |
|---|---|---|
| `TimeOutSeconds` | 30 | 基类超时阈值（秒） |

`LoadConfig` / `SaveConfig` **无参**，走 `XdocumentReaderWriter`（XML 文件 `Config/XML/MotionControlWorkflow.xml`）；`SaveConfig()` 末尾 `Config.SaveXdocument()` 落盘（裁定 D1）。各步超时用私有常量判定，与 `TimeOutSeconds` 相互独立。

---

## 可观测性与释放

`GetStepName` 映射：`0 空闲待机` / `10 启动-清零编码器轴` / `20 启动-启动CAMBOX` / `30 启动-等待主轴运动` / `100 跟踪中` / `110 暂停中-等待恢复` / `700 停止收尾` / `900 失败收尾` / 其余 `未登记步(N)`。

`SubDeviceLog()`（C7 契约）：输出连接态 / 焊接过程态 / 相位 / 步骤名 / 已初始化标志（送丝/质量阈值日志 todo）。

`DisposeManaged()`（基类 `Dispose()` 钩子，ADR-025）：退订 `TrackingError` → 释放 `_tracker`/`_encoderAxis`/`_positionBuffer`（置 null、`_initialized=false`）→ `State=Disconnected` + `SetPhase(Idle)`。

---

## UI 接入

```csharp
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;

var wf = MotionControlWorkflow.Instance;
var status = wf.WeldStatus;   // 焊接过程态
var running = wf.IsRunning;   // Tracking 或 WaitingForMaster
// 启停（受理式，硬件结果读 WeldStatus）
wf.Start();
wf.Stop();
```

调用方：`MotionControlPage.cs`（启停按钮）、`FormMain.cs`、`DeviceControlWork`（初始化级联 + `AlignDatum` 消费侧）。`LineLaserWorkflow.RunAutoAdjust` 以 `MotionControlWorkflow.Instance.IsRunning` 判断 CAMBOX 硬件跟踪运行期间跳过软件离散调整。

---

## 关联

- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（§4 契约 · §5 RunStep 驱动 · §16 模板）
- [[api/CamBoxTracker]] — CAMBOX 跟踪引擎（跟踪点/异常直订源）
- [[api/EncoderAxis]] — ATYPE=25 通讯编码器轴
- [[api/RSIPositionBuffer]] — RSI 位置时间戳环形缓冲
- [[api/MotionManager]] / [[api/ZMotionController]] — 正运动控制器入口与句柄
- [[modules/MotionControl]] — 运控硬件层
- [[decisions/ADR-023-RSICamBoxTrackingArchitecture]] — CAMBOX 架构决策
- [[decisions/ADR-034-ThreeStateModelRefactor]]、[[decisions/ADR-036-RawDesignRefinement20260903]] — 三态模型与原档细化裁定
