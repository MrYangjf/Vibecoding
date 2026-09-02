---
title: ADR-042 — WorkflowStateBase 泛型化：通用流程态机制下沉基类，机器人侧整机流程态下沉主设备
date: 2026-08-31
tags: [决策, 架构, 设备控制, 流程态, 泛型基类, 模板方法, MainDeviceControl]
status: accepted
---

> ⚠️ **已被取代（2026-09-02）**：本 ADR 的「泛型 `WorkflowStateBase<TStep>` 流程态机制」被新主控设计非泛型 `DeviceWorkflowBase` + 三态模型取代，详见 [[decisions/ADR-049-ThreeStateModelRefactor]]。本页保留作历史参考，不再作为现行约束。

# ADR-042 — WorkflowStateBase 泛型化：通用流程态机制下沉基类

## 背景

ADR-041 落地后用户审查发现两个继承失效问题：

1. **子流程整套自建流程态机制**：`WorkflowStateBase` 只提供了 `DeviceFlowState` 枚举 + `FlowState` 属性 + 机器人 Pose 安全门控，**没有提供通用流程态机制**。4 个子工作流（线激光/监控/运控/工艺）各自重复实现了 `_step` 字段、`Step` 属性、`SetStep`/`TransitionTo` 转换方法（更新→四态映射→触发事件）、`MapToDeviceState`（内容几乎相同）、自有 `XxxStateChangedEventArgs`——共通能力没有继承，只有独有内容也整套装。
2. **机器人侧状态占用基类**：`DeviceFlowState`（Idle/SafePose/Preworking/PreWeldPose/Working/Stopping/Stopped/Alarm）是**机器人 Pose 握手驱动的整机状态**（用户提供的机器人侧状态表），却被放进通用基类。子流程语义对不上→无法使用→只能新建大量方法。

用户明确约定：**不是不允许子流程新增内容，而是共通常用的都应继承而来，只有独特的才新建**。

## 决策

### 1. `WorkflowStateBase<TStep>` 泛型化（C# 7.3 支持）

```
DeviceStateBase（设备态四态 + 设备安全）
    ↓
WorkflowStateBase<TStep> where TStep : struct（流程态 + 状态转换 + 映射契约 + 事件）
    ↓
DeviceWorkflowBase<TStep>（四抽象生命周期 + 四公开编排）
    ↓
具体 Workflow（各自传自有流程态枚举）
```

基类统一承载：
- `Step` 属性（读取）+ `protected _step` 字段（写入仅经 SetStep）
- `SetStep(newStep, reason)` 统一转换入口：`ValidateTransition` 校验 → 更新 `_step` → `State = MapToDeviceState(newStep)` → 触发 `StateChanged` → `OnStepChanged` 钩子 → 记录流程态切换日志
- `protected abstract DeviceState MapToDeviceState(TStep step)` —— ADR-041 映射规则的唯一子类承载点
- `protected virtual bool ValidateTransition(from, to)` —— 默认放行（线激光/运控/工艺沿用），严格时序工作流重写（监控相机）
- `public event EventHandler<WorkflowStepChangedEventArgs<TStep>> StateChanged` —— 统一事件参数（OldState/NewState/Reason/Timestamp），**替代 4 个工作流各自的自有 EventArgs 类**（用户裁定：彻底去重，UI 同步改签名）
- `protected virtual void OnStepChanged(e)` —— 变更后钩子

构造函数 `protected WorkflowStateBase(TStep initialStep)`，各工作流传入自有枚举初始值（Uninitialized/Idle 等）。

### 2. 机器人侧整机流程态下沉 `MainDeviceWorkflow`

- `DeviceFlowState` 更名 **`MainDeviceFlowState`**（枚举值不变），连同语义迁入 `MainDeviceWorkflow.cs`（与"状态契约内联各工作流文件"约定一致）
- `FlowState` 属性保留为 `MainDeviceWorkflow.FlowState => Step`（UI 兼容）
- ~~`FlowStateSwitched` 事件改为由 `OnStepChanged` 重写转发~~ **⚠️ 已被 2026-08-31 后续决策推翻**：该转发违反权责规则 R3，已连同 `PowerOnInitializeCompleted` 一并删除，订阅方统一订阅基类 `StateChanged`。详见 [[decisions/ADR-043-WorkflowResponsibilityBoundary]]。
- `IsRobotPoseSafe` 下沉为 MainDeviceWorkflow 私有方法（当前恒安全，后续接 SafetyFlow）；`CheckSafetyFlow` 无任何调用方，**按死代码删除**（ADR-038）

### 3. 子工作流收敛（删除全部重复机制）

| 删除成员（每文件） | 保留成员（独有内容） |
|---|---|
| `_step` 字段声明、`Step` 属性、`SetStep`/`TransitionTo` 方法、自有 `XxxStateChangedEventArgs`、`MapToDeviceState` 改为 `protected override`、`StateChanged` 事件声明 | 自有流程态枚举、`MapToDeviceState` 实现（MotionControl 保留 `_initialized` 两义区分）、Monitor 的 `ValidateTransition` 重写、全部业务方法 |

转换调用点机械替换：`TransitionTo(x, r)` → `SetStep(x, r)`（签名兼容，业务方法零改动）。

### 4. UI 消费方签名替换（4 文件）

`Instance.Step` 读取**不变**；事件处理签名 `XxxWorkflowStateChangedEventArgs` → `WorkflowStepChangedEventArgs<TStep>`（字段名不变）：
- `FormMain.cs`（LineLaser StateChanged + MainDevice StateChanged；原 MainDevice 侧走 `FlowStateSwitched`，2026-08-31 起改为基类 `StateChanged`，ADR-043）
- `ILCamPage.cs`、`MotionControlPage.cs`（LineLaser）
- `MonitorCamPage.cs`（Monitor；补 `using ...DeviceState;`）

## 附带修复（同日发现的既有编译缺陷）

`MainDeviceWorkflow` 中 `_initializing` 字段与 `RobotManager` 属性**被使用但从未声明**（ADR-041 重构遗留），本次补齐声明。

## 备选方案（被放弃）

| 方案 | 放弃原因 |
|---|---|
| 各工作流保留自有 EventArgs 继承公共基类（UI 零改动） | 每文件仍留 1 事件 + 1 参数类，去重不彻底；用户裁定选彻底统一 |
| 非泛型基类 + `object` 装箱承载流程态 | 类型安全差，子类到处强转，反而更糟 |
| 流程态机制放 `DeviceWorkflowBase`（不放 WorkflowStateBase） | 违反"流程态属流程基类"的分层语义（用户原始定义） |

## 后果

### 正面
- 子工作流每文件净删 ~40-70 行重复机制代码；新增工作流只需：枚举 + MapToDeviceState + 业务方法
- 流程态转换单点收口（SetStep），天然满足 ADR-041"禁手工 State= 赋值"与 StateMachine-DoubleTransition 教训
- 所有工作流统一获得转换合法性校验钩子与统一日志格式

### 负面 / 已知取舍
- **泛型基类 `_step` 无法标 `volatile`**（C# 禁止对泛型参数用 volatile，CS0677）；原各子类 `_step` 均为 volatile。枚举读写原子、读取均跨方法边界，实际风险极低；若未来出现自旋轮询读 `Step` 的场景，须先拷贝到局部变量
- `MotionControlWorkflow.Dispose` 中原 `StateChanged = null`（清空订阅）改为删除：事件属基类，派生类不可赋值；工作流为单例，订阅方各自在 Dispose 中退订
- 事件为统一契约后，各工作流不再自造流程态事件；**后续 ADR-043 进一步禁止**工作流自造 `XxxCompleted`/`ErrorAborted` 与转发子设备事件，订阅方一律订阅基类 `StateChanged`（MainDevice 侧 `FlowStateSwitched` 已删除）

## 修正记录（用户纠正）

1. **流程态基类职责**：用户指出"WorkflowStateBase 是流程基类，应设置流程状态、状态转换、写基本流程函数供子类重写"——初版实现把基类做成了"仅整机专用"，属职责错位。
2. **机器人侧状态归属**：用户指出"我提供的那些是机器人侧的状态，设备的状态需要你理解优化，完全照抄导致子流程没法用"——本次将整机 Pose 驱动态识别为 MainDeviceWorkflow 独有内容并下沉。

## 关联

- 前置：[[decisions/ADR-041-MainDeviceControlArchitecture]]、[[decisions/ADR-026-EnumDeduplication]]、[[decisions/ADR-038-CodeSimplificationStandard]]
- 架构页：[[architecture/DeviceControlArchitecture]]；模块页：[[modules/DeviceControl]]
- 教训：[[lessons/StateMachine-DoubleTransition]]（转换单点收口）
