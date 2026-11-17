---
title: "ADR-055 子流程状态消解与参数类归位"
date: 2026-10-09
updated: 2026-10-30
tags: [决策, 架构, DeviceControl, 工作流, 三态模型, 参数类, 重构]
status: accepted
---

# ADR-055 子流程状态消解与参数类归位

> 业主 2026-10-09 指令：「`SubDeviceWeldStatus` 是子设备的状态，不用每个子流程建立一个状态。其他的 workflow 请参考 `LineLaserWorkflow`，将自建的子设备状态消解」
> + 「子流程不要自建参数类」+「Y轴和 Z轴等属于主动控制，不是根据算法自适应控制，需要新建 `WeldParamMontionControl` 管理」
> 本 ADR **落地 ADR-013 §A47 与 ADR-016 R1 的既定裁定**，不是新架构决策。

## 背景

ADR-013（2026-09）已裁定「各工作流自有流程态枚举降为私有 `_phase`/`_flowState`，对外状态经 `SubDeviceWeldStatus` 承载」，
但**落地只做了一半**：四个 workflow 的枚举仍是 `public`，且 `LineLaserWorkflow` 已进一步做到**连枚举与字段一并删除**。

实测（`LineLaserWorkflow.cs` 968 行全文）：

```csharp
SetWeldStatus(SubDeviceWeldStatus.PreWork, "工作流启动，进入 PreWork"); // 状态：直接用基类抽象状态
switch (RunStep) { case StepPreWork: if (DoPreWork()) AdvanceStep(...); } // 进度：步号
```

**零状态枚举、零私有状态字段**。其余四个 workflow 则是「`switch (RunStep)` 已用步号驱动 + 仍保留一个自建枚举当中间层」，
自建枚举成了**纯冗余**（只在 `MapWeldStatus` 映射与日志里用）。

## 决策

### 决 1 — 四个自建状态枚举全部删除，对外只用 `SubDeviceWeldStatus`

| Workflow | 删除的枚举 | 值的个数 |
|---|---|---|
| `LaserWeldHeadWorkflow` | `LaserWeldHeadWorkflowState` | 4 |
| `MonitorCameraWorkflow` | `MonitorWorkflowState` | 7 |
| `WeldParamControlWorkflow` | `WeldParamControlWorkflowState` | 7 |
| `MotionControlWorkflow` | `MotionControlPhase` | 5 |

配套删除私有字段 `_phase` / `_flowState`，`SetPhase` / `MapWeldStatus` 中间层改为**直调 `SetWeldStatus`**。

> ⛔ **不是把枚举改成 `private`**，而是**整个删掉** —— 与 `LineLaserWorkflow` 完全对齐。
> 半吊子的「降为私有」正是 ADR-013 §A47 与代码现状长期不符等的原因。

> ⚠️ **`SetPhase` 不可简单删平**：它除映射外还有**步号复位副作用**
> （`MonitorCameraWorkflow` 的 `AdvanceStep(StepAcquireTrigger/StepAnalyze)`、
> `MotionControlWorkflow` 的 `AdvanceStep(StepServoOn/StepStopping)`）。
> 故重写为 `EnterWeldStatus(SubDeviceWeldStatus, string reason[, bool enterServoStep])`，
> **副作用保留在方法内**，调用方只表达目标状态。

### 决 2 — `MotionControlWorkflow.IsRunning` 改判实际使能信号

原判 `_phase == MotionControlPhase.Ready`。删除枚举后 `Ready` 与 `Idle` 都映射到 `SubDeviceWeldStatus.Standby`、**不可区分**。

**正解**：改判 `MontionAxis.IsServoOn()`（基类抽象方法，`DeltaMontionAxis:248` 已实现）——
先判 `WeldStatus == Standby`，再判跟踪轴已使能。

> ⛔ **不保留任何替代枚举或布尔标志**（如 `_servoOned`）：状态只允许一个来源（ADR-013）。
> 本类已有同源用法可循（轴配置校验 `:554`、回标就绪判据 `:571`）。

### 决 3 — `MonitorCameraWorkflow` 的 `_phase` **保留**

该类有两个同名不同义的字段，本 ADR **只删状态那个**：

| 字段 | 类型 | 处置 |
|---|---|---|
| `_flowState`（已删） | `MonitorWorkflowState` | 设备状态 → 已消解 |
| **`_phase`（保留）** | **`MonitorCameraPhase`** | **算法相位**（`PreWeldAlignment`/`WeldQuality`），是 `MonitorResult.Phase` 的数据源 |

> ⛔ **同名不同义是判据陷阱**：按名字判「`_phase` 必须清零」会误删算法相位。
> 判据必须**按类型区分**（`MonitorCameraPhase _phase` 保留 / 其他 `_phase` 零）。

### 决 4 — 参数类归位到 `WeldParamData.cs` 并改名消歧

| 类 | 原位置 | 新位置 | 职责 |
|---|---|---|---|
| ~~`WeldParamOutput`~~ | ⛔ 定义在 `WeldParamControlWorkflow.cs`（流程文件内） | ✅ **`WeldParamData.cs`** | **自适应算法算出来**的量 |
| `WeldParamMontionControl` | —— | ✅ **新建于 `WeldParamData.cs`** | **上位机/运控主动给定**的轴位置 |

**改名理由**（业主裁定）：`WeldParamOutput` 易与「主动控制的运动参数」混淆。

**字段归属**：

| 类 | 字段 |
|---|---|
| `WeldParamAdaptControl` | `LaserPower` / `FeedSpeed` / `RobotSpeed` / `GalvoAmplitude` / `SpotWidth` / `SeamWidth` / `Success` / `Timestamp` |
| `WeldParamMontionControl` | `AxisYPositionMm`（Y 轴位置）/ `WireZPositionMm`（送丝 Z 轴 = TA 力矩电机位置）/ `Timestamp` / `Reset()` |

> ⛔ **`RobotX` 已从自适应输出类移除** —— 它是**真实坐标读数**（算法输入），不是算法输出。
> 旧类把它当输出字段是错的。

> 依据 **ADR-016 R1**「数据是设备的，进度是流程的」：流程不得定义设备数据。
> 参数类与 `RobotWeldData` / `AutoParam` / `ChartVar` 同属 `WeldParamData.cs` 这个数据定义域。

### 决 5 — 可观测性：本轮核实**代码侧已合规，无需改动**

实测五个 workflow **全部**已覆写 `GetStepName(int step)` 且**全部按 `switch (step)` 判步号**
（`LineLaser` / `MonitorCamera` / `WeldParam` / `LaserWeldHead` / `MotionCtrl`）。

> ⚠️ 本轮初判「只有 `LineLaserWorkflow` 覆写了`GetStepName`」是**我的 Grep 正则假阳性**（漏了 `protected`）。
> 已记入 lessons：判据出现「全库只有 1 处」时，先手工抽验 2~3 条再下结论。

## 后果

| 文件 | 变化 |
|---|---|
| `LaserWeldHeadWorkflow.cs` | 405 → 370 行（枚举 8 + SetPhase 8 + MapWeldStatus 13 + `_phase` 引用清零） |
| `MonitorCameraWorkflow.cs` | 640 → 603 行（枚举 11 + SetPhase/MapWeldStatus 20 + `_flowState` 清零）；顺带修掉既有 19 个孤立 LF |
| `WeldParamControlWorkflow.cs` | 687 → 599 行（枚举 12 + 旧参数类 30 + MapWeldStatus/SetPhase） |
| `MotionControlWorkflow.cs` | 2235 → 2214 行（枚举 14 + MapWeldStatus 17 + SetPhase 残余 20 + `_phase` 清零） |
| `WeldParamData.cs` | 475 → 543 行（两个新类） |
| `DeviceControlWork.cs` / `MainPage.cs` | 类型名同步 / `WireZ` 注释指向新类 |

**净效果**：对外状态入口只剩 `SubDeviceState` + `SubDeviceWeldStatus` + `MainDeviceStatus`（ADR-013 三态），
进度只剩 `RunStep` + `WorkStepName` / `StepStatusText` / `WorkElapsedMs`（ADR-041 可观测性）。

## 遗留

- ⏳ `WeldParamMontionControl` **0 消费方**（`MainPage.chkWireZ` 的 `ChartVar WireZ` 序列保持空，
 等后端 `TaPositionMm` 接线后 `Add(x, y)`）
- ⏳ P1 §4.4 的「Y轴位置」曲线项（`MainPage` 五项里的第 4 项）尚未建 Checkbox

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[decisions/ADR-013-ThreeStateModelRefactor]] — 三态模型（本 ADR 落地其 §A47）
- [[decisions/ADR-016-WorkflowResponsibilityBoundary]] — R1 数据归属（本 ADR 落地其参数类条款）
- [[decisions/ADR-041-ResidentFlowNonBlockingParadigm]] — 步号范式与可观测性
- [[architecture/DeviceControlArchitecture]] — §1 三态模型 / §4 流程基类 / §6 五个子工作流
- [[lessons/StaticVerifierJudgements]] — §4.9 委托与 static 上下文陷阱（本轮同批新增）