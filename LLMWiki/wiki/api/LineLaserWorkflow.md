---
title: LineLaserWorkflow API 参考（三态模型：SubDeviceState / SubDeviceWeldStatus）
date: 2026-09-02
updated: 2026-09-04
tags: [API, 工作流, 英莱, 线激光, SubDeviceWeldStatus, DeviceWorkflowBase, RunStep, ADR-028, ADR-030]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs
---

# LineLaserWorkflow API 参考

> 英莱线激光焊缝跟踪工作流（单例，三态模型 + `RunStep` bool 驱动）。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：非泛型 `DeviceWorkflowBase`（17 项契约）→ `DeviceStateBase`；`IDisposable` 由基类实现。
> 架构背景见 [[modules/DeviceControl]]、[[architecture/DeviceControlArchitecture]]。

> **✅ 2026-09-04 已落地（ADR-030 批次 0~4.4）**：本类已按新架构改码——无自带线程（由 `DeviceControlWork` 子设备线程驱动 `FlowProcess()`）、`RunStep` 每 case 靠 bool 推进、连接态 `State` / 焊接过程态 `WeldStatus` 由基类承载。旧 `GoStep`/`SetStep`/`WorkStep`/`StartRunLoop`/`ManualOn`/`ManualOff`/命令三槽等机制已全部清除，不得据旧内容改码。真编译待 VS（静态自检已通过）。
> 步骤驱动规范见 [[architecture/DeviceControlArchitecture]] §4（17 契约）· §5（`RunStep` 驱动）· §16（代码模板）。

---

## 概述

两层状态：连接态 `State`（`SubDeviceState`，2 态），由 `ConnectOn`/`ConnectOff` 联动；焊接过程态 `WeldStatus`（`SubDeviceWeldStatus`，7 态），由流程方法（`Start`/`Stop`/`BeginWorking`/各执行步）联动。执行步 `RunStep`（int 游标，由每个 `case` 内 bool 判定推进）驱动 `FlowProcess()`。

**执行步段位**：10 PreWork 清理 → 20 开传感器/激光 → 30 等数据稳定 → 31 等主设备通知 Working → 100 焊接工作 → 700 停止清料 → 800 成功收尾 / 900 失败收尾 → 0 待机。

### 在工作流体系中的角色

- 由 `DeviceControlWork` 上电初始化（`InitializeOn`）与整机编排驱动 `FlowProcess()`。
- 模拟模式由 `DeviceControlWork.StartSimulationLineLaser()` 触发 `Start()`（经 `StateSwitched` 事件等连接完成后自启）。
- Working 态焊缝结果（`ContourDataReady` 回调）→ 上报 `PipelineManager` + 触发 `WeldParamControlWorkflow.ComputeAndOutput()`（见下文「触发焊接工艺计算」）。

---

## 公共成员

| 成员 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static LineLaserWorkflow` | `Lazy<T>` 单例 |
| `StateName` | `override string` | 对外名片名，返回 `Tag`（日志/事件标识） |
| `IsPreWorkDone` | `bool` | PreWork 是否完成（主设备轮询判断，完成后可进入 Working） |
| `IsDataStable` | `bool` | 轮廓数据是否稳定有效（主设备轮询判断） |
| `State` / `WeldStatus` | 基类属性 | 连接态（`SubDeviceState`）/ 焊接过程态（`SubDeviceWeldStatus`） |
| `RunStep` / `StepWorkTime` / `WorkStepName` / `StepStatusText` | 基类属性 | 执行步 / 步骤用时 / 步中文名 / 可观测摘要（"step:30 / 8.2s …"） |
| `Start()` | `void` | 启动工作流：Standby → PreWork（要求当前 `WeldStatus == Standby`，否则抛 `InvalidOperationException`） |
| `Stop()` | `void` | 手动停止：PreWork/Working/Stopping → `ManualStopped`；其他状态忽略并记 Warning |
| `BeginWorking()` | `void` | 主设备通知进入 Working（要求 PreWork + `_preWorkDone` + `_dataStable` 三条件） |

> 执行步段位常量 `StepPreWork=10` / `StepPreWorkOn=20` / `StepPreWorkStable=30` / `StepPreWorkWaitWork=31` / `StepWorking=100` / `StepStopping=700`（私有）；通用三常量 `StepIdle=0` / `StepFinishOk=800` / `StepFinishFail=900` 由基类提供，子类不得重复定义。

---

## 执行步表（`RunStep` 驱动）

| 步号 | 常量 | 中文名 | 内容 | 出口 |
|---|---|---|---|---|
| 0 | `StepIdle`（基类） | 待机 | 非运行阶段态 | — |
| 10 | `StepPreWork` | 焊接前-清理状态与外设 | 复位失败计数/成功计数/稳定帧计数 + `SafeShutdownPeripherals()` + 置 `_preWorkDone` | → 20 |
| 20 | `StepPreWorkOn` | 焊接前-开传感器与激光 | `SetSensor(true)` + `SetLaser(true)`；虚拟相机（`_ilCamera==null`）直接置 `_dataStable` | → 30 |
| 30 | `StepPreWorkStable` | 焊接前-等待数据稳定 | 相机回调查满 `DataStableFrameCount`(5) 帧置 `_dataStable`；超时 10s → `HandleFailure`（重置计时留在原步） | → 31 |
| 31 | `StepPreWorkWaitWork` | 焊接前-等待进入Working | 模拟模式自驱动 `SetWeldStatus(Working)`；等主设备 `BeginWorking()`（超时 30s → `Fail`） | → 100（状态切换触发） |
| 100 | `StepWorking` | 工作中-焊接与自适应调整 | 行程达 `_maxWeldLength` → `StopByWeldLengthReached`（置 Stopping）；`_adjustmentPending` → `RunAutoAdjust()`；有效结果缺失满 5s 窗口 → `HandleFailure` | → 700 |
| 700 | `StepStopping` | 停止中-关闭外设 | `SafeShutdownPeripherals()` | → 800 |
| 800 | `StepFinishOk` | 成功收尾 | Stopping 完成 `SetWeldStatus(Standby)` | → 0 |
| 900 | `StepFinishFail` | 失败收尾 | `SetWeldStatus(ErrorAborted)` + `IsAlarm` | → 0 |

**超时/计数常量**（秒）：`DataStableTimeoutSeconds=10` / `WaitWorkingTimeoutSeconds=30` / `FirstResultTimeoutSeconds=5` / `DataStableFrameCount=5`。`MaxConsecutiveFailures`（默认 5，可配）达上限才转失败收尾。

> ✅ `PreWorkWaitTimeoutSeconds` 已于 2026-09-04 注释收尾轮删除（双模式 Grep 确认零引用）；等待 Working 超时用 `WaitWorkingTimeoutSeconds`。
> ⚠️ 等待类执行步**不再无限等待**：超时 → 失败收尾 → `ErrorAborted`（符合「不得留在原步死等」约定）。真实焊接链路中 `BeginWorking()` 目前仓库内**无调用方**——若主设备未在 30s 内通知，工作流将报警；模拟模式在步 31 内自驱动，无需 `BeginWorking`。

---

## 状态联动

### `OnWeldStatusChanged`（把执行步复位到该阶段入口；离开运行态解绑相机）

| 新焊接过程态 | 动作 |
|---|---|
| `PreWork` | `AdvanceStep(StepPreWork)`（10） |
| `Working` | `AdvanceStep(StepWorking)`（100） |
| `Stopping` | `AdvanceStep(StepStopping)`（700） |
| 其他（`Standby`/`NoReset`/`ManualStopped`/`ErrorAborted`） | `AdvanceStep(StepIdle)` + `ReleaseCameraBinding()`（退订事件、关外设、`CameraSelector.SetWorking(false)`） |

> `AdvanceStep` 内部**改步 + 刷新计时成对出现**（基类机制），防止把停留时长带入下一步误判超时。

### `WeldStatusTrans()`（整机下发迁移的本地适配）

| 当前焊接过程态 | 动作 |
|---|---|
| `NoReset` | return（不动作） |
| `Stopping` | `AdvanceStep(StepStopping)`（执行停止清料） |
| `ManualStopped` / `ErrorAborted` | `AdvanceStep(StepIdle)` |

### `FlowProcess()` switch 骨架

```
if (!IsEnable) return;
switch (RunStep) {
    case 10:  if (DoPreWork())      AdvanceStep(20);  break;
    case 20:  if (DoPreWorkOn())    AdvanceStep(30);  break;
    case 30:  if (DoPreWorkStable())AdvanceStep(31);  break;
    case 31:  if (DoPreWorkWaitWork()) AdvanceStep(100); break;
    case 100: if (DoWorking())      AdvanceStep(700); break;
    case 700: if (DoStopping())     AdvanceStep(800); break;
    case 800: if (DoFinishOk())     AdvanceStep(0);   break;
    case 900: if (DoFinishFail())   AdvanceStep(0);   break;
    default:  break;   // StepIdle 与未登记步：空转，靠状态切换复位到阶段入口
}
```

> ⛔ 全部 case 无 `Thread.Sleep` / `while` 轮询：等待靠「外部线程重入 + `IsTimeout(seconds)`」判定超时。

---

## 关键行为

### Start()（Standby → PreWork）

`lock(_syncRoot)` 内要求 `WeldStatus == Standby`（否则抛异常）→ 复位计数、清 `_preWorkDone`/`_dataStable` → `SetWeldStatus(PreWork)`。随后按模式选择相机：模拟+虚拟相机 → `CameraSelector.SelectVirtual()`，否则 `SelectIntelligentLaser()`；`CameraSelector.SetWorking(true)`；`BindCamera()` 订阅轮廓事件。相机绑定仅在运行期存在，离开运行态由 `OnWeldStatusChanged` 触发 `ReleaseCameraBinding()`。

### 数据稳定判定（PreWork 阶段）

`IlCamera_ContourDataReady` 回调中，若处于 `PreWork` 且结果有效，`_startingValidFrameCount` 累加，连续满 5 帧（`DataStableFrameCount`）置 `_dataStable = true`；任一帧无效则清零重计。

### 触发焊接工艺计算

回调中连续成功帧达 `_adjustTriggerSuccessCount`（默认 1，可配）时置 `_adjustmentPending`；`FlowProcess` 步 100 消费后调用 `RunAutoAdjust()`：

```csharp
// 硬件 CAMBOX 跟踪运行期间跳过软件离散调整
if (MotionControlWorkflow.Instance.IsRunning) { _lastAdjustSuccess = true; return; }
_lastAdjustSuccess = WeldParamControlWorkflow.Instance.ComputeAndOutput();   // 焊接工艺计算与下发
```

> 焊缝特征与机器人 X 由 `WeldProcess` 在 `PipelineManager.AlgorithmCompleted` 中暂存，工艺工作流统一计算下发，此处无需传参。

### 失败计数语义

- 有效结果缺失需**持续满 5s 超时窗口**才计一次失败（`FirstResultTimeoutSeconds`），且每次计时后 `ResetWorkTime()`——避免每拍累加瞬间打满。
- `HandleFailure` 连续失败达 `_maxConsecutiveFailures`（默认 5）→ `Fail(reason)`：记录 `_failStep`/`_failReason` 后 `AdvanceStep(900)`。
- 步 900 失败收尾：`SetWeldStatus(ErrorAborted)` + `IsAlarm=true` → 回 0 待机，等待人工复位。（故障落库已随模块移除删除，ADR-032）

### 待机安全默认态

`Standby` 时传感器与激光均关闭（安全默认态）；`SafeShutdownPeripherals()` 由步 10/700、`ResetProcess`、`ReleaseCameraBinding` 多处保证。

---

## 连接 / 生命周期契约

| 方法 | 语义 | 状态联动 |
|---|---|---|
| `InitializeOn()` | 阻塞连接（上电初始化用）：`InitializeInternal`（connect→readConfiguration→verifyHardwareStatus，走 `RunStepAction` 三步模板）；失败 `SetWeldStatus(ErrorAborted)` 返回 false | 成功：`State=Connected` + `WeldStatus=NoReset` |
| `InitializeOff()` | 阻塞断开：断开相机、`SafeShutdownPeripherals` + `ReleaseCameraBinding` | `State=Disconnected` + `WeldStatus=NoReset` |
| `ConnectOn()` | 非阻塞：自起后台线程 `ConnectWorker` 执行连接（`_isConnecting` 防重入，已连接直接 true） | 成功 `State=Connected`；失败 `WeldStatus=ErrorAborted` |
| `ConnectOff()` | 非阻塞：自起后台线程 `DisconnectWorker` 断开 | `State=Disconnected` |
| `ResetProcess()` | 线性阻塞链：未连接拒绝（false）；关外设 + 复位失败计数 | `WeldStatus=Standby` |
| `ClearStatus()` | 复位前状态清理：清报警与标志位、`AdvanceStep(0)` | `WeldStatus=NoReset` |
| `ResetWorkTime()` | `ResetStepTime()`（基类） | — |

> 连接初始化模拟相关：模拟开启且非虚拟相机时先 `CameraSelector.SelectIntelligentLaser()`；`CameraSelector.IsVirtual` 时三步直通返回 true。

---

## 配置项（`ConfigFileName = "LineLaserWorkflow"`）

| 配置元素 | 默认值 | 说明 |
|---|---|---|
| `TimeOutSeconds` | 30 | 基类超时阈值（秒） |
| `MaxConsecutiveFailures` | 5 | 连续失败上限，达上限转失败收尾 |
| `MaxWeldLength` | 1000.0 | 焊缝最大行程（mm），达行程自动 Stopping |
| `AdjustTriggerSuccessCount` | 1 | 连续成功帧触发工艺计算的阈值 |

`LoadConfig` / `SaveConfig` **无参**，走 `XdocumentReaderWriter`（XML 文件 `Config/XML/LineLaserWorkflow.xml`）；`SaveConfig()` 末尾 `Config.SaveXdocument()` 落盘（裁定 D1）。配置非线程安全，运行期禁止在 `FlowProcess()` 内读写。

---

## 事件与生命周期

- 构造函数订阅 `GlobalCommData.CommunicationCommandReceived += OnCommunicationCommandReceived`（回调统一 `ShowCommunicationLog(Tag, message)` 记通信收发日志）。
- `DisposeManaged()`（基类 `Dispose()` 钩子，ADR-023）：退订全局事件 → 退订相机事件 → `_ilCamera.Dispose()` → `CameraSelector.SetWorking(false)`。
- 连接/断开线程（`ConnectWorker`/`DisconnectWorker`）为后台线程，`_isConnecting` 标志防重入。

---

## 可观测性

`GetStepName` 映射：`0 待机` / `10 焊接前-清理状态与外设` / `20 焊接前-开传感器与激光` / `30 焊接前-等待数据稳定` / `31 焊接前-等待进入Working` / `100 工作中-焊接与自适应调整` / `700 停止中-关闭外设` / `800 成功收尾` / `900 失败收尾` / 其余 `未登记步(N)`。

`SubDeviceLog()`（C7 契约，各子流程自写日志）：输出连接态 / 焊接过程态 / 步骤名 / 有效结果 / 实测帧率 / 稳定帧计数。

---

## 调用方与 UI 接入

```csharp
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;
using AdaWeldSystem.MainDeviceControl.DeviceState;   // 读 SubDeviceState / SubDeviceWeldStatus 枚举

var wf = LineLaserWorkflow.Instance;
var status = wf.WeldStatus;   // 焊接过程态：判断是否运行、显示分步进度
var state  = wf.State;        // 连接态：判断能否操作、销毁前是否断开
var step   = wf.StepStatusText;  // "step:100 / 3.4s 工作中-焊接与自适应调整"
```

- 编排调用方：`DeviceControlWork`（`InitializeOn`/`InitializeOff` 级联；模拟：`StartSimulationLineLaser`/`StopSimulationLineLaser`/`ResetSimulationLineLaser` + `OnSimLineLaserStateChanged` 回调）。
- UI 读态：`FormMain.cs`、`ILCamPage.cs`、`MotionControlPage.cs`、`MainPage.cs`（只读 `WeldStatus`/`State`/`StepStatusText`）。
- ⚠️ UI/外部**不得越权直驱**线激光 `Start`（模拟流程由 `DeviceControlWork` 统一编排，见 `StartSimulationLineLaser` 注释）。

---

## 关联

- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（§4 契约 · §5 RunStep 驱动 · §16 模板）
- [[lessons/StepMemberNameCollision]] — `RunStepAction` 命名避让基类 `RunStep` 属性的 CS0102 教训
- [[modules/WeldParamControl]] / [[api/WeldParamControlWorkflow]] — 焊接工艺计算链路
- [[api/MotionControlWorkflow]] — CAMBOX 硬件跟踪运行期间跳过软件调整
- [[api/GlobalCommData]] — 日志与通讯底层出口
- [[decisions/ADR-026-YinglaiDataFlow]] — 英莱数据流
- [[decisions/ADR-031-ThreeStateModelRefactor]] — 三态模型决策
- [[decisions/ADR-033-RawDesignRefinement20260903]] — 原档细化与完全重构裁定
