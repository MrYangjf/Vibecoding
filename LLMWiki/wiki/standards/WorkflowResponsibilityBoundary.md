---
title: 流程与子设备对象权责边界标准
date: 2026-09-02
tags: [规范, 权责边界, 工作流, 子设备, 事件, ADR-043, ADR-049]
---

# 流程与子设备对象权责边界标准（WorkflowResponsibilityBoundary）

> **触发**：用户提出「流程与xx设备权责不清 / 流程里怎么这么多事件 / 这个事件该不该放流程」等权责类问题时，AI **直接读取本页执行**，无需用户重复输入权责要求。决策见 [[decisions/ADR-043-WorkflowResponsibilityBoundary]]。
>
> **适用范围**：`MainDeviceControl/DeviceWorkflow/` 下全部子设备工作流 + `DeviceControlWork` / `DeviceStatusWork` 两个整机管控类，以及所有被流程调用的子设备对象（相机 Run、运动控制器、跟踪引擎、焊接头等）。
>
> **2026-09-02（ADR-049 三态模型）术语对齐**：本页原有「流程态对外枚举 + `MapToDeviceState` 四态映射」表述已废止。现行形态为——各工作流持**私有阶段枚举**（`_phase`/`_flowState`，不对外），经 `MapWeldStatus(phase)` 映射为对外**焊接过程态** `SubDeviceWeldStatus`；连接态另有 `SubDeviceState`；整机运行态为 `MainDeviceStatus`。本页「流程态」一词一律指**私有阶段枚举**。

---

## 一、一句话判据

> **数据是设备的，进度是流程的。**

流程可以**读**数据、可以**叫设备干活**，但不能**替设备发数据**、不能**替设备喊健康**、不能**把设备的事件再喊一遍**。

## 二、流程的合法职责（白名单）

流程只做这五件事，超出即越权：

1. **触发** —— 调用子设备的动作方法（如 `SensorRunContinue()`、`StartAcquisition()`）
2. **调用** —— 调用算法/服务（如 `ImageAlgorithm.DetectWeldQuality(...)`）
3. **读取结果** —— 拿到返回值后暂存为只读属性
4. **推进私有阶段** —— 经私有 `SetStep(phase, reason)` 推进，由 `MapWeldStatus(phase)` 映射为对外焊接过程态 `SubDeviceWeldStatus`
5. **执行动作** —— 把结果用出去（如把工艺参数下发给机器人）

## 三、五条硬规则

### R1 数据产出归属：谁产生数据，谁输出事件

| 数据类型 | 归属 | 输出通道 |
|---|---|---|
| 图像 / 帧 | 相机对象（`MonitorCameraRun` 等） | `FrameCompletedEvent` |
| 连接态 / 健康度 | 设备对象自身 | 设备对象的 `StatusChanged` 或轮询只读属性 |
| 算法结果（判定/评分/偏移） | 算法层产出；流程读取后以**只读属性**持有 | 不抛事件 |
| 轨迹点 / 跟踪异常 | 跟踪引擎（`CamBoxTracker`） | 直接订阅引擎事件 |

**禁止**：流程内出现 `event EventHandler<...Mat...>`、`event EventHandler<...Result...>`、`event EventHandler<...SupervisionStatus...>`。

**替代范式**：结果放只读属性，UI 在 `WeldStatusChanged` 转 `Working`/`Standby` 后拉取。

```csharp
// 正例：流程持有结果，只读暴露
public MonitorResult LastResult { get { lock (_resultLock) { return _result.Clone(); } } }
public Mat LastOverlay { get { lock (_resultLock) { return _resultMat; } } }

// 反例：流程抛结果事件
public event EventHandler<MonitorResultEventArgs> ResultEvent;   // 违反 R1
```

### R2 禁止转发子设备事件

流程**不得**把子设备已公开的事件再抛一遍。订阅方直接订阅子设备对象；流程只负责暴露子设备属性。

```csharp
// 反例：纯转发，零业务加工
_tracker.PointAdded += OnTrackerPointAdded;
private void OnTrackerPointAdded(object sender, CamBoxPointEventArgs e)
{
    PointAdded?.Invoke(this, e);         // 违反 R2
}

// 正例：流程只暴露子设备，订阅方自取
public CamBoxTracker Tracker { get { return _tracker; } }
// 调用方：MotionControlWorkflow.Instance.Tracker.PointAdded += ...
```

**例外**：子设备事件需驱动私有阶段变化时可以订阅，但用途是「推进私有阶段 / 记日志」，不是「换个名字再抛」。

### R3 状态通知统一

启动 / 停止 / 终止 / 完成，一律由基类承载（ADR-049 三态）：

```csharp
// 基类 DeviceStateBase 提供（非泛型 DeviceWorkflowBase 继承而来）
public event EventHandler<WeldStatusChangedEventArgs> WeldStatusChanged;  // 焊接过程态
//   参数：OldStatus / NewStatus / Reason / Timestamp
public event EventHandler<SubDeviceStateChangedEventArgs> StateSwitched;  // 连接态
public SubDeviceWeldStatus WeldStatus { get; }   // 只读，写入唯一入口 SetWeldStatus(...)
public SubDeviceState State { get; }             // 只读，写入唯一入口 SetState(...)

// 整机另由 DeviceControlWork 提供
public event EventHandler<MainDeviceStatusChangedEventArgs> StatusChanged;  // 主设备运行态
```

**禁止**自造 `XxxCompleted` / `ErrorAborted` / `ManualStopped` / `FlowStateSwitched` 事件及配套 `EventArgs` 类。

**禁止**在私有 `SetStep(phase, reason)` 里把基类 `WeldStatusChanged` 再转发为工作流专属事件。

```csharp
// 反例：私有阶段刷新后，另抛一个同义事件
private void SetStep(MonitorWorkflowState step, string reason)
{
    _flowState = step;
    SetWeldStatus(MapWeldStatus(step), reason);
    PhaseSwitched?.Invoke(this, step);   // 违反 R3
}

// 正例：只映射、不转发；订阅方按需订阅对应层级
MonitorCameraWorkflow.Instance.WeldStatusChanged += OnMonitorWeldStatusChanged;   // 子设备
DeviceControlWork.Instance.StatusChanged         += OnMainDeviceStatusChanged;    // 整机
```

### R4 流程做动作，而非抛事件等订阅

流程的职责是**执行动作**；结果数据对外以**只读属性**暴露，不抛事件。

```csharp
// 反例：算完抛事件，等别人订阅去做事
_output.Success = sent;
ParamOutputReady?.Invoke(this, _output);   // 违反 R4（且零订阅）

// 正例：流程自己做动作，结果放只读属性
bool sent = SendToRobot(_output);
_output.Success = sent;
// 订阅方：读 WeldParamControlWorkflow.Instance.LastOutput
```

> **零订阅事件 = 死代码**：新加事件前先确认有真实订阅方。加之前问一句"这件事是该流程做的动作，还是该等别人订阅？"

### R5 私有阶段枚举只描述流程

私有阶段枚举**只描述流程进度**，不得包含 UI/显示等外部职责态。

```csharp
// 反例
public enum MonitorWorkflowState { ..., Analyzing, Displaying, Completed, ... }
//                                              ^^^^^^^^^^ 显示是 UI 职责

// 正例：7 态，全是流程进度（内联于 MonitorCameraWorkflow.cs，不对外暴露）
public enum MonitorWorkflowState
{ Uninitialized, Standby, Acquiring, Analyzing, Completed, ErrorAborted, ManualStopped }
```

> 阶段枚举可 `public` 声明（便于 `MapWeldStatus` 与日志可读），但**不随 `WeldStatus` 对外暴露**——对外真相源只有 `SubDeviceWeldStatus` 七态。

### 附：依赖方向（R1 的推论）

**子设备对象不得依赖流程层**。子设备需要的枚举/契约放子设备自己的 `Api/` 层。

```csharp
// 反例：子设备反向依赖流程命名空间
// MonitorCam/MonitorCameraRun.cs
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;   // 只为拿 MonitorCameraPhase

// 正例：枚举下沉到子设备 Api 层
// MonitorCam/Api/IMonitorCameraApi.cs
public enum MonitorCameraPhase { Unknown, PreWeldAlignment, WeldQuality }
```

---

## 四、审查清单（改任何 Workflow 前逐条过）

- [ ] **R1**：本流程是否抛出了携带 Mat / 算法结果 / 设备健康状态的事件？
- [ ] **R2**：本流程是否把子设备事件换个名字再抛一遍？（搜 `?.Invoke(this, e)` 转发）
- [ ] **R3**：本流程是否自造了 Completed / ErrorAborted / ManualStopped 事件？私有 `SetStep` 里是否在转发基类 `WeldStatusChanged`？
- [ ] **R4**：本流程是否有零订阅事件？该动作能否由流程直接执行、结果放只读属性？
- [ ] **R5**：私有阶段枚举里是否有 Displaying / Saving / Uploading 等外部职责态？
- [ ] **ADR-049**：是否有手工 `WeldStatus = ...` / `State = ...` / `Status = ...` 赋值？（必须走 `SetWeldStatus` / `SetState` / `SetStatus`）
- [ ] **依赖**：子设备文件是否 `using` 了 `...MainDeviceControl.DeviceWorkflow`？
- [ ] **死代码**：删事件时，配套 `EventArgs` 类、`private readonly XxxArgs _xxxArgs` 字段、Dispose 里的 `= null` 是否一并清理？
- [ ] **region**：删除事件 region 后 `#region`/`#endregion` 是否仍配对？（易踩坑：连带删除 `#region` 行导致失衡）

## 五、合规 / 违规范式对照

| 流程 | 状态 | 说明 |
|---|---|---|
| `LineLaserWorkflow` | ✅ 合规范式 | 零自定义事件，全部走基类 `WeldStatusChanged` / `StateSwitched` |
| `LaserWeldHeadWorkflow` | ✅ 合规范式 | 同上 |
| `MonitorCameraWorkflow` | ✅ 已治理（2026-08-31） | 删 5 事件 + 健康巡检下沉 + 删 `Displaying` 态 |
| `MotionControlWorkflow` | ✅ 已治理（2026-08-31） | 删 2 个转发事件；`Tracker` 属性直供订阅 |
| `WeldParamControlWorkflow` | ✅ 已治理（2026-08-31） | 删 `ParamOutputReady`，结果走 `LastOutput` |
| `DeviceControlWork` | ✅ 已治理（2026-09-02） | 删 `FlowStateSwitched` / `PowerOnInitializeCompleted`；对外仅 `StatusChanged`（`MainDeviceStatus`） |

## 六、UI 侧配套范式

流程不再是数据推送方后，UI 采用 **「推状态 + 拉数据」**：

```csharp
// 1) 图像：订阅设备对象（R1）
MonitorCameraRun.FrameCompletedEvent += OnFrameCompleted;

// 2) 流程进度：订阅基类统一事件（R3，ADR-049 三态）
MonitorCameraWorkflow.Instance.WeldStatusChanged += OnWeldStatusChanged;   // 焊接过程态
MonitorCameraWorkflow.Instance.StateSwitched     += OnConnStateSwitched;   // 连接态
DeviceControlWork.Instance.StatusChanged         += OnMainStatusChanged;   // 整机运行态

// 3) 结果：进入 Working 后拉取只读属性（R4）
private void OnWeldStatusChanged(object sender, WeldStatusChangedEventArgs e)
{
    if (InvokeRequired) { Invoke(...); return; }
    lblStatus.Text = GetStatusText(e.NewStatus);
    if (e.NewStatus == SubDeviceWeldStatus.Working) ShowResult();   // 拉取
}
```

> 私有阶段枚举（如 `MonitorWorkflowState`）**不出现在 UI 代码中**——UI 只认 `SubDeviceWeldStatus` 七态。需要更细进度时读 `WorkStep` / `WorkStartTime`（ADR-047 步骤驱动）。

配套：[[standards/UiStateSimplification]]（真相源唯一、刷新入口统一）、[[guides/WinForms-UI-Threading]]（`InvokeRequired` 封送）。

---

## 关联

- 决策：[[decisions/ADR-043-WorkflowResponsibilityBoundary]]
- 架构：[[architecture/DeviceControlArchitecture]]
- 模块：[[modules/DeviceControl]]、[[modules/MonitorCam]]
- API：[[api/MonitorCameraWorkflow]]、[[api/MonitorCameraRun]]、[[api/MotionControlWorkflow]]、[[api/WeldParamControlWorkflow]]、[[api/DeviceControlWork]]
- 互补：[[standards/CodeSimplification]]、[[standards/UiStateSimplification]]
