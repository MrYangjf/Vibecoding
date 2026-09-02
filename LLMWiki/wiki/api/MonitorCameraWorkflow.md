---
title: MonitorCameraWorkflow API 参考（三态模型：SubDeviceState / SubDeviceWeldStatus）
date: 2026-09-02
updated: 2026-09-02
tags: [API, 工作流, 监控, 状态机, 权责边界, 执行步, 步骤驱动, SubDeviceWeldStatus, ADR-049]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs
---

# MonitorCameraWorkflow API 参考

> 监控相机工作流（单例）。**只负责编排**：触发采集 → 调用算法 → 读取结果 → 推进焊接过程态。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：`DeviceWorkflowBase`（非泛型，→ `DeviceStateBase`），`IDisposable` 由基类实现
>
> **✅ 2026-09-02 三态模型重构（ADR-049，accepted）**：旧「设备四态 + 流程态 `MonitorWorkflowState`」改为三态模型——连接态 `SubDeviceState` + 焊接过程态 `SubDeviceWeldStatus`；旧 `Step`(流程态枚举) 对外不再暴露，由私有 `_flowState`(`MonitorWorkflowState`) 驱动 `FlowProcess`，对外经 `WeldStatus` 承载。旧 `ManualOn`/`ManualOff` → `ConnectOn`/`ConnectOff`；`StateChanged(WorkflowStepChangedEventArgs<T>)` → `WeldStatusChanged(WeldStatusChangedEventArgs)` + `StateSwitched(SubDeviceStateChangedEventArgs)`。
> 步骤驱动规范见 [[standards/StepDrivenWorkflow]]。

## 权责边界（ADR-043）

**本流程不再产出任何数据事件**。职责划分：

| 内容 | 归属 | 通道 |
|---|---|---|
| 图像 / 实时帧 | [[api/MonitorCameraRun]] | `MonitorCameraRun.FrameCompletedEvent` |
| 相机连接态与**健康巡检** | [[api/MonitorCameraRun]] | `MonitorCameraRun.StatusChanged` + 只读属性 |
| 流程进度 | 本流程（基类提供） | `WeldStatusChanged`（`WeldStatusChangedEventArgs`） |
| 检测结果 | 本流程**只读持有** | `LastResult` / `LastOverlay` 属性，订阅方按需拉取 |

> ⚠️ 历史版本曾提供 `DisplayEvent`/`ResultEvent`/`ErrorAborted`/`ManualStopped`/`StatusChanged` 五个事件，**已全部移除**。迁移见文末「迁移对照」。

---

## 核心类

```csharp
public class MonitorCameraWorkflow : DeviceWorkflowBase
{
    // 单例访问（Lazy<T>）
    public static MonitorCameraWorkflow Instance { get; }

    // 状态（三态模型）
    public SubDeviceState State { get; }            // 连接态（2 态）
    public SubDeviceWeldStatus WeldStatus { get; }   // 焊接过程态（7 态）
    public int WorkStep { get; }                     // 执行步（内部游标）
    public string WorkStepName { get; }
    public string StepStatusText { get; }

    // 结果只读属性（流程读取算法输出后持有，不抛事件）
    public MonitorResult LastResult { get; }
    public Mat LastOverlay { get; }

    // 连接契约 + 生命周期
    public override bool ConnectOn();    // 手动连接（自起后台线程）
    public override void ConnectOff();   // 手动断开（自起后台线程）
    public void Initialize();            // 基类模板 → ConnectOn()
    public void Start(MonitorCameraPhase phase, bool continuous);
    public void Stop();
    public void Dispose();               // 基类实现（模板方法 + DisposeManaged 钩子）
}
```

---

## 执行步表（内部游标）

| 步号 | 中文名 | 内容 | 出口 |
|---|---|---|---|
| 0 | 待机 | 非运行阶段态 | — |
| 10 | 触发采集 | `SetPhase` + `Reset` 信号 + `EnsureConnected` + `SensorRunContinue` | → 20 |
| 20 | 等待采集完成信号 | `WaitOne(0)` 非阻塞探测，超时 5s；校验 `LastAcquisitionSuccess` 与 `CurrentMat` | → 30 / 900 |
| 30 | 算法分析 | `DetectPreWeldAlignment` / `DetectWeldQuality`，写 `_result` 与 `_resultMat` | → 800 / 900 |
| 800 | 成功收尾 | 连续模式 `SetWeldStatus(Acquiring)` 回 10；单轮模式 `SetWeldStatus(Standby)` | → 10 / 0 |
| 900 | 失败收尾 | `SetWeldStatus(ErrorAborted)` + `IsAlarm` + `RecordFault` | → 0 |

> **命名**：步号常量（私有）`StepAcquireTrigger=10` / `StepAcquireWait=20` / `StepAnalyze=30`；单步方法统一 `DoXxx()`（`DoAcquireTrigger` / `DoAcquireWait` / `DoAnalyze` / `DoFinishOk` / `DoFinishFail`）。

> **`Initialize()` 已回归基类模板（2026-09-01 修正）**：原 `public new bool Initialize()` 隐藏基类生命周期（ADR-042 反模式）已删除——连接检测体移入 `ConnectOn()`。调用方 `DeviceControlWork` 自动初始化与 `MonitorCamPage` 均无需改动（现调 `ConnectOn()`）。

### 事件

**仅基类事件**，无自定义事件（ADR-043 R1~R4）：

| 事件 | 来源 | 参数 |
|---|---|---|
| `WeldStatusChanged` | `DeviceStateBase` | `WeldStatusChangedEventArgs`（OldStatus/NewStatus/Reason/Timestamp） |
| `StateSwitched` | `DeviceStateBase` | `SubDeviceStateChangedEventArgs`（连接态） |
| `AlarmOccurred` | `DeviceStateBase` | `EventArgs` |

---

## 过程态与连接态映射

私有阶段枚举 `MonitorWorkflowState` 经 `MapWeldStatus(...)` 映射到对外 `SubDeviceWeldStatus`：

| 私有阶段态 `MonitorWorkflowState` | 焊接过程态 `SubDeviceWeldStatus` | 连接态 `SubDeviceState` |
|---|---|---|
| `Uninitialized` | `Standby` | `Disconnected` |
| `Standby` / `ManualStopped` | `Standby` | `Connected` |
| `Acquiring` / `Analyzing` / `Completed` | `PreWork`/`Working`（对应） | `Connected` |
| `ErrorAborted` | `ErrorAborted` | `Connected` |

映射由私有 `MapWeldStatus(step)` 承载，**禁止手工 `WeldStatus = ...` 赋值**。

### 状态转换

`Uninitialized → Standby → Acquiring → Analyzing → Completed → Standby/Acquiring`
任何状态均可经 `Stop()` 转 `ManualStopped`，经异常路径转 `ErrorAborted`。

> `Displaying` 态已于 2026-08-31 移除——**显示是 UI 职责，不属流程态**（ADR-043 R5）。

---

## 工作循环（步骤驱动化）

```
Start(phase, continuous)
  → MonitorCameraRun.StartSupervision()      // 相机健康巡检由相机自身启停
  → SetWeldStatus(Acquiring) → OnWeldStatusChanged → GoStep(10) → StartRunLoop()
  → [每拍] 10 触发采集
  →        20 WaitOne(0) 探测信号（超时 5s → 900）
  →        30 算法分析（过程态转 Working/Analyzing）
  →        800 成功收尾：连续模式回 10，单轮模式转 Standby

Stop() → MonitorCameraRun.StopSupervision() → SetWeldStatus(ManualStopped)
```

- 线程模型：**基类常驻监听线程**（`StartRunLoop`，节拍 10ms）取代原「每 `Start()` 新建一条线程」。
- 采集仍采用回调等待模式（[[decisions/ADR-005-CallbackAcquisition]]），但**阻塞 `WaitOne(5000)` 改为 `WaitOne(0)` 探测**——等待由节拍重入完成，超时统一由 `IsStepTimeout(AcquireTimeoutMs)` 判定，超时转 `ErrorAborted`。
- `IsRunLoopActive` 仅在运行阶段为 true，待机/报警时空转并持续刷新步时间戳（防恢复瞬间误判超时）。

---

## 结果类型

```csharp
public class MonitorResult
{
    public MonitorCameraPhase Phase { get; set; }
    public bool Pass { get; set; }
    public double QualityScore { get; set; }
    public double OffsetX { get; set; }
    public double OffsetY { get; set; }
    public double Angle { get; set; }
    public int DefectCount { get; set; }
    public string Message { get; set; }
    public DateTime Timestamp { get; set; }
}
```

`PreWeldAlignment`（焊前对中）填 OffsetX/OffsetY/Angle/Pass；`WeldQuality`（焊中质检）填 DefectCount/QualityScore/Pass。

---

## UI 接入（推状态 + 拉数据）

```csharp
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;
using AdaWeldSystem.MonitorCam;
using AdaWeldSystem.MonitorCam.Api;

// 1) 图像来自相机，不来自流程（R1）
MonitorCameraRun.FrameCompletedEvent += OnFrameCompleted;
// 2) 健康状态来自相机（R1）
MonitorCameraRun.Instance.StatusChanged += OnCamStatusChanged;
// 3) 流程进度来自基类（R3）
MonitorCameraWorkflow.Instance.WeldStatusChanged += OnWorkflowStatusChanged;

private void OnWorkflowStatusChanged(object sender, WeldStatusChangedEventArgs e)
{
    if (InvokeRequired) { Invoke(new Action<object, WeldStatusChangedEventArgs>(OnWorkflowStatusChanged), sender, e); return; }

    lblStatus.Text = GetStateText(e.NewStatus);
    switch (e.NewStatus)
    {
        case SubDeviceWeldStatus.Working:       // 单轮完成（连续模式恒 Working，完成经定时器 ShowResult）
            ShowResult();
            break;
        case SubDeviceWeldStatus.ErrorAborted:
            txtResult.Text = "异常: " + e.Reason;
            break;
        case SubDeviceWeldStatus.ManualStopped:
            txtResult.Text = "已停止";
            break;
    }
}

private void ShowResult()
{
    var wf = MonitorCameraWorkflow.Instance;
    Mat overlay = wf.LastOverlay;
    if (overlay != null && !overlay.IsEmpty) imageBox1.Image = overlay;
    MonitorResult r = wf.LastResult;
    txtResult.Text = string.Format("判定: {0}\r\n{1}", r.Pass ? "合格" : "不合格", r.Message);
}
```

> **连续监测模式**：连续运行（`continuous=true`）时 `WeldStatus` 恒为 `Working`，单轮完成信号不再经 `WeldStatusChanged` 透出，UI 须按 500ms 节拍在定时器内 `ShowResult()` 刷新界面（见 `MonitorCamPage.cs`）。

调用方：`MonitorCamPage.cs`、`MotionControlPage.cs`（只读 `WeldStatus`）、`DeviceStatusWork`（按 `SubDeviceState` 参与互锁判定）。

---

## 迁移对照（供旧代码定位）

| 旧成员 | 新位置 |
|---|---|
| `DisplayEvent`（Mat） | `MonitorCameraRun.FrameCompletedEvent`（图像）+ `LastOverlay`（算法叠加图） |
| `ResultEvent` | `LastResult` 只读属性，在 `WeldStatusChanged → Working`(单轮完成) 后拉取 |
| `ErrorAborted` 事件 | `WeldStatusChanged` 的 `NewStatus == ErrorAborted`，原因取 `e.Reason` |
| `ManualStopped` 事件 | `WeldStatusChanged` 的 `NewStatus == ManualStopped` |
| `StatusChanged`（健康巡检） | `MonitorCameraRun.StatusChanged` |
| `SupervisionState` / `LastHealthyTime` / `CheckIntervalMs` / `IsMonitorCameraWorking` | `MonitorCameraRun` 同名属性 |
| `MonitorWorkflowState.Displaying` | 已删除（R5） |
| `MonitorCameraPhase` | 下沉至 `MonitorCam/Api/IMonitorCameraApi.cs` |
| `MonitorSignalCode` | 已删除 |

---

## 关联

- [[standards/WorkflowResponsibilityBoundary]] — 权责执行细则
- [[decisions/ADR-043-WorkflowResponsibilityBoundary]] — 本次治理决策
- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页
- [[api/MonitorCameraRun]] — 采集运行控制与健康巡检
- [[api/MonitorAlgorithmManager]] — 算法配置管理器
- [[decisions/ADR-011-MonitorCameraModule]]、[[decisions/ADR-049-ThreeStateModelRefactor]]（现行有效）
