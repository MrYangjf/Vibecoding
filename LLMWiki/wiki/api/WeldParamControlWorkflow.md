---
title: WeldParamControlWorkflow API 参考（焊接工艺控制流程 · 三态模型）
date: 2026-09-02
updated: 2026-09-02
tags: [API, 工作流, 焊接, 工艺, 功率, 送丝, 振镜, SubDeviceWeldStatus, 执行步, 步骤驱动, ADR-049]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs
---

# WeldParamControlWorkflow API 参考

> **✅ 2026-09-02 三态模型重构（ADR-049，accepted）**：旧「设备四态 `DeviceState` + 流程态 `WeldParamControlWorkflowState`」改为三态模型——连接态 `SubDeviceState` + 焊接过程态 `SubDeviceWeldStatus`；旧 `Step`(流程态枚举) 对外不再暴露，由私有 `_phase`(`WeldParamControlWorkflowState`) 驱动 `FlowProcess`，对外经 `WeldStatus` 承载。旧 `ManualOn`/`ManualOff` → `ConnectOn`/`ConnectOff`（此处 `Connect` 表示「工艺参数就绪」）；`StateChanged(WorkflowStepChangedEventArgs<T>)` → `WeldStatusChanged(WeldStatusChangedEventArgs)` + `StateSwitched(SubDeviceStateChangedEventArgs)`。
> 步骤驱动规范见 [[standards/StepDrivenWorkflow]]。

> 焊接工艺控制流程（单例）。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：`DeviceWorkflowBase`（非泛型，→ `DeviceStateBase`）。`IDisposable` 由基类实现。
> 模块背景见 [[modules/WeldParamControl]]

---

## 定位（易错，务必注意）

**不是有连接动作的设备**，而是**设备内部控制焊接工艺的一个流程**。

```
输入：机器人信息 + 线激光结果信息
  ↓ 分析计算
输出：焊接功率 / 送丝速度 / 振镜摆幅 / 焊接速度
  ↓
下发：发送给机器人
```

因此**没有物理连接/断开动作**，也不纳入 `DeviceControlWork.InitializeMachine()` 级联；`ConnectOn()` 在此语义为「工艺参数就绪」（置 `Connected` + `Standby`）。

---

## 核心类

```csharp
public class WeldParamControlWorkflow : DeviceWorkflowBase
{
    // 单例访问（Lazy<T>）
    public static WeldParamControlWorkflow Instance { get; }

    // 状态（三态模型）
    public SubDeviceState State { get; }            // 连接态（Connect = 工艺参数就绪）
    public SubDeviceWeldStatus WeldStatus { get; }   // 焊接过程态（7 态）
    public int WorkStep { get; }                     // 执行步（内部游标）
    public string WorkStepName { get; }
    public string StepStatusText { get; }
    public double StepElapsedMs { get; }

    // 事件（基类统一提供）
    public event EventHandler<SubDeviceStateChangedEventArgs> StateSwitched;
    public event EventHandler<WeldStatusChangedEventArgs> WeldStatusChanged;

    // 核心方法：只置命令变量 + 唤起监听线程，不再同步计算
    public bool ComputeAndOutput();

    // 结果（只读属性，ADR-043 R4）
    public WeldParamOutput LastOutput { get; }

    // 连接契约（Connect = 工艺参数就绪）
    public override bool ConnectOn();
    public override void ConnectOff();
    public void Initialize();    // 基类模板 → ConnectOn()
    public void Reset();         // → ResetProcess()
    public void ClearAlarm();    // → ClearStatus()
    public void Dispose();
}
```

### 执行步表（内部游标，段位遵循 [[standards/StepDrivenWorkflow]]）

| 步号 | 常量 | 单步方法 | 中文名 | 行为 | 出口 |
|---|---|---|---|---|---|
| `0` | `StepIdle`（基类） | — | 待机 | 空转，等待 `ConsumeCommand()` 受理 `_pendingCompute` | 由命令变量 → 10 |
| `10` | `StepCompute` | `DoCompute()` | 工艺计算 | 置 `Computing` → 校验 `CurrentAutoParam`（空则 `FailFlow`）→ 连续失败达阈值置 `Holding` 并 `GoStep(0)` → `TriggerAdjustment()` + `FillOutput()` → `SetWeldStatus(Outputting)` 后 **立即 return** | → 20 |
| `20` | `StepOutput` | `DoOutput()` | 下发机器人 | `SendToRobot(_output)` 成功 → 800，失败 → 900 | → 800 / 900 |
| `800` | `StepFinishOk`（基类） | `DoFinishOk()` | 成功收尾 | 置 `Standby` | → 0 |
| `900` | `StepFinishFail`（基类） | `DoFinishFail()` | 失败收尾 | `SetWeldStatus(ErrorAborted)` + `IsAlarm` + `FaultRecoveryManager.RecordFault(FaultCategory.Process, "WeldParamStepFail")` | → 0 |

> **命令变量**：`private volatile bool _pendingCompute;`。`ConsumeCommand()` 中若 `WorkStep == StepIdle` 才 `GoStep(StepCompute)`——**上一轮未跑完时新触发被丢弃**，天然节流，不会堆积。

> **失败原因**：原私有字段 `_failReason` / `_failStep` 与自造 `FailFlow()` 已下沉基类，本类改读基类只读属性 `FailReason` / `FailStep`，失败收尾调基类 `FailFlow(reason)`。

### WeldParamOutput（输出类）

| 字段 | 类型 | 说明 |
|---|---|---|
| `LaserPower` | double | 焊接功率 |
| `FeedSpeed` | double | 送丝速度 |
| `RobotSpeed` | double | 焊接速度（机器人移动速度） |
| `GalvoAmplitude` | double | 振镜摆幅（**当前 TODO，返回 0**） |
| `SeamWidth` | double | 本轮采用的焊缝宽度（平滑后） |
| `RobotX` | double | 当前机器人 X 坐标 |
| `Success` | bool | 计算是否成功 |
| `Timestamp` | DateTime | 时间戳 |

---

## 过程态与连接态映射

私有阶段枚举 `WeldParamControlWorkflowState` 经 `MapWeldStatus(...)` 映射到对外 `SubDeviceWeldStatus`：

| 私有阶段态 `WeldParamControlWorkflowState` | 焊接过程态 `SubDeviceWeldStatus` | 连接态 `SubDeviceState` |
|---|---|---|
| `Uninitialized` | `Standby` | `Disconnected` |
| `Standby` | `Standby` | `Connected` |
| `Initializing` / `Computing` / `Outputting` / `Holding` | `PreWork`/`Working`（对应） | `Connected` |
| `ErrorAborted` | `ErrorAborted` | `Connected` |

---

## ComputeAndOutput（无参）—— 命令变量模式

```csharp
public bool ComputeAndOutput()
{
    _pendingCompute = true;   // 只置命令变量，不做业务
    StartRunLoop();           // 唤起基类常驻监听线程
    return _output.Success;   // 返回的是「上一轮」结果
}
```

**⚠️ 返回值语义已变（重要）**：改造后因为计算被挪到监听线程，**返回的是上一轮 `_output.Success`**。调用方若需本轮结果，请在 `WeldStatusChanged` 收到 `Standby`/`ErrorAborted` 后读 `LastOutput.Success`（ADR-043 R4 的「推状态 + 拉数据」范式）。当前唯一调用方 `LineLaserWorkflow` 不使用返回值，无兼容问题。

**关键**：`WeldProcess.TriggerAdjustment()` 是**无参**方法，内部用 `OnAlgorithmCompleted` 暂存的 `_lastSeamFeature` / `_lastRobotX`。**不要给它加参数**。

**失败路径**：`FailFlow(reason)` 统一走「置 `ErrorAborted`（经 `SetWeldStatus`）→ 记日志 → `RecordFault` → `GoStep(900)`」，不原地重试；下一拍回到 0 待机，等下一次 `ComputeAndOutput()` 触发。

---

## 数据链路：焊缝信息即英莱线激光的结果

```
英莱线激光取像
  ↓ IlInspectResult 回调：FeatureY/FeatureZ（特征点）、Width0/Width1（宽度）
LineLaserWorkflow.OnContourFrameReady
  ↓ sf.CenterY=ir.FeatureY, sf.CenterX=ir.FeatureZ
    sf.SeamWidth=(ir.Width0+ir.Width1)*0.5, sf.SeamArea=ir.Area
PipelineManager.ReportExternalResult(sf, robotX, null)
  ↓
WeldProcess.OnAlgorithmCompleted → 暂存 _lastSeamFeature / _lastRobotX
  ↓
WeldParamControlWorkflow.ComputeAndOutput()   ← 只置 _pendingCompute
  ↓ 基类监听线程 ConsumeCommand() → GoStep(10)
DoCompute()(10): SetWeldStatus(Computing) + TriggerAdjustment()【无参】→ 平滑 + 查表 + 灵敏度判定
  ↓ FillOutput
DoOutput()(20): SendToRobot → 机器人 → GoStep(800)
```

**英莱回调本就含特征点与宽度，链路本就通**。本工作流补的是「计算后下发到机器人」这一环。

---

## 振镜摆幅：TODO（查表项，非公式）

`CalcGalvoAmplitude` 当前占位返回 `0.0`（不摆动），不影响其余三项工艺参数下发。

`WeaveWidth` 规划为 `AutoParamManager` 中的**分段查找表**（与焊缝宽度关联），与送丝速度/焊接速度/激光功率三张表同样的匹配方式。

> **反例警示**：不要用自创公式（如 `(SeamWidth - LaserDiameter) / 2`）——那是未经验证的推导，不是项目既定的匹配方式。

---

## 触发时机

由 `LineLaserWorkflow` 在 Working 态、连续成功帧达到阈值时调用。**不入上电级联**，保持单一驱动源（[[decisions/ADR-013-WorkflowAsAdjustmentDriver]]）。

---

## 下发通道

`SendToRobot` 经顶层 `Comm` 的机器人通讯下发 `KUKARobotData{EStr="P.. S.. V.. G.."}`。机器人未启用时返回 `true`（不视为失败）。

连接本身由 `CommunicationManager` 管控，本类只做数据下发。

---

## 关联

- [[modules/WeldParamControl]] — 模块说明（含完整数据链路）
- [[modules/DeviceControl]] — 所属架构（执行步层说明）
- [[standards/StepDrivenWorkflow]] — 步骤驱动规范（段位/超时/红线）
- [[architecture/DeviceControlArchitecture]] — 架构规范页（第 8 章）
- [[api/WeldDataManager]] — 焊接数据管理器
- [[decisions/ADR-013-WorkflowAsAdjustmentDriver]] — 单一驱动源决策
- [[decisions/ADR-049-ThreeStateModelRefactor]] — 本次三态模型决策（现行有效）
