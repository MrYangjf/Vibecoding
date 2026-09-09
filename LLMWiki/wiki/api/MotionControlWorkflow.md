---
title: MotionControlWorkflow API 参考（台达 EtherCAT 运控 · 三态模型）
date: 2026-09-02
updated: 2026-09-07
tags: [API, 工作流, 运控, 台达, EtherCAT, RunStep, SubDeviceWeldStatus, DeviceWorkflowBase, ADR-031, ADR-033, ADR-036, ADR-037]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs
---

# MotionControlWorkflow API 参考

> 运控工作流（单例）：台达 EtherCAT 总线的**启停编排器**——只做设备初始化、伺服使能、停止收尾，不参与实时运动控制。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：非泛型 `DeviceWorkflowBase`（17 项契约）→ `DeviceStateBase`；`IDisposable` 由基类实现。
> 设计依据 [[decisions/ADR-032-MotionControllerDeltaReplacement]]、[[decisions/ADR-033-ZMotionRemovalAndDeltaLanding]]。

> **✅ 2026-09-07 控制器换轨改造**：删除全部正运动（ZMotion）依赖（原 `CamBoxTracker` / `EncoderAxis` / `RSIPositionBuffer` / `InterpolationEngine` 及其 `Tracker` 属性），相位枚举由 `LaserCamBoxWorkflowState` 改为 **`MotionControlPhase`**，初始化改走 `MontionManager.Instance.Initialization("台达运控", ref msg)`。**对外契约（`Instance` / `Start()` / `Stop(bool)` / `IsRunning` / `WeldStatus` / `StateName`）保持不变**，UI 侧 [[api/MotionControlPage]] 无需改动。
> ⚠️ **OPEN**：焊缝跟踪的高级运动方案未定（候选 ECAM2 电子凸轮 / 虚拟主轴 + GearIn / PVT），因此本类当前**只到「伺服使能 + 就绪」**，不含轨迹跟踪步骤。
> 步骤驱动规范见 [[architecture/DeviceControlArchitecture]] §4（17 契约）· §5（`RunStep` 驱动）· §16（代码模板）。

---

## 定位

- **运控编排归本类**：台达总线的打开/初始化/关闭、全体轴伺服使能、急停下发，统一由本类编排；实时跟随由硬件总线完成。
- **不产出设备数据**（[[decisions/ADR-023-WorkflowResponsibilityBoundary]]）：轴/IO/气缸对象由 [[api/MontionManager]] 持有与注册，本类只调用其批量接口。
- **厂商隔离**：本类不出现任何 `Delta*` 类型——台达装配发生在 `MontionManager.Initialization()` 内（唯一装配点）。
- 差异化职责（原档 R011）：**检测送丝位置和焊接质量阈值**——`SubDeviceLog()` 内 `// todo`，待硬件点位明确后落地。

---

## 公共成员

| 成员 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static MotionControlWorkflow` | `Lazy<T>` 单例 |
| `StateName` | `override string` | 对外名片名，返回 `Tag`（日志/事件标识） |
| `IsRunning` | `bool` | 是否处于 `Ready` 相位 |
| `IsInitialized` | `bool` | 台达总线是否初始化成功 |
| `State` / `WeldStatus` | 基类属性 | 连接态（`SubDeviceState`）/ 焊接过程态（`SubDeviceWeldStatus`） |
| `RunStep` / `StepWorkTime` / `WorkStepName` / `StepStatusText` | 基类属性 | 执行步 / 步骤用时 / 步中文名 / 可观测摘要 |
| `ConfigFileName` | `protected override string` | `"MotionControlWorkflow"`，配置落在 `Config/XML/` 下 |

---

## 相位枚举 `MotionControlPhase`（同文件公共枚举）

`_phase`（默认 `Idle`）驱动 `FlowProcess` 与可观测性，对外经 `SetWeldStatus(MapWeldStatus(phase))` 映射：

| 取值 | 含义 | 映射 `SubDeviceWeldStatus` | 执行步复位 |
|---|---|---|---|
| `Idle` | 空闲（初始化完成或未启动） | `Standby` | `StepIdle` |
| `Initializing` | 正在打开并初始化台达总线 | `PreWork` | `StepIdle` |
| `Ready` | 已受理启动指令，等待伺服使能完成 | `Standby` | `StepServoOn`(10) |
| `Stopping` | 停止中（伺服下使能） | `Stopping` | `StepStopping`(700) |
| `Error` | 初始化失败或流程异常 | `ErrorAborted` | `StepIdle` |

> `SetPhase()` 三件事：写 `_phase` → 映射 `WeldStatus` → 把 `RunStep` 复位到该阶段入口步。

---

## 执行步段

| 步号 | 常量 | 动作 | 推进 |
|---|---|---|---|
| 10 | `StepServoOn` | `DoServoOn()`：首次进入下发 `MontionManager.Instance.ServoOnAll()`，随后轮询 `IsAllServoOn()`（遍历 `MontionControl.GetAxes()` 判 `IsServoOn()`）；`ServoOnTimeoutSeconds = 10` 超时 → `Fail()` | → 20 |
| 20 | `StepReady` | 已使能待机；空转等待，靠相位切换把执行步复位到停止或失败收尾 | — |
| 700 | `StepStopping` | `DoStopping()`：`MontionManager.Instance.ServoOffAll()` | → `StepIdle` |
| 900 | `StepFinishFail` | `DoFinishFail()`：记录失败原因与失败步号 | → `StepIdle` |

> 步段位沿用 [[architecture/DeviceControlArchitecture]] §5 约定（10/20 业务段 · 700 停止 · 900 失败收尾）。

---

## 主要方法

| 方法 | 说明 |
|---|---|
| `Start()` | 受理启动指令：未初始化则记 Warning 返回 false；否则置 `Ready` 相位（执行步复位到 10）。**只受理不阻塞** |
| `Stop(bool immediate = false)` | 受理停止指令：`immediate=true` 先下发 `MontionManager.Instance.SetEmergencyStop(true)`；`Idle`/`Error` 相位直接返回；否则置 `Stopping` |
| `FlowProcess()` | 每拍由 `DeviceControlWork` 子设备线程驱动；`IsEnable` 门控后按 `RunStep` 分派 |
| `ResetProcess()` | 解除急停（`SetEmergencyStop(false)`）、清 `_servoOnIssued`、回 `Idle` 并置 `Standby` |
| `ClearStatus()` | 清报警/失败原因/`_servoOnIssued`，**直接置 `_phase` 不经映射**，`WeldStatus` 强制 `NoReset` |
| `ResetWorkTime()` | 调基类 `ResetStepTime()`，防止停止期时间计入步骤时长导致误超时 |
| `InitializeOn()` | 阻塞初始化：调 `MontionManager.Instance.Initialization("台达运控", ref msg)`；失败置 `Error` + `Disconnected`，成功置 `Idle` + `Connected` + `NoReset`（等待复位） |
| `ConnectOff()` | 阻塞断开：关闭台达总线，调用方阻塞至完成 |

---

## 关联

- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（§4 契约 · §5 RunStep 驱动 · §10 运动控制 · §16 模板）
- [[api/MontionManager]] — 运控业务层单例（轴/IO/气缸注册与查询，台达装配点）
- [[api/DeltaEtherCAT-Native]] — 台达 EtherCAT 原生 API 速查
- [[modules/MotionControl]] — 运控硬件层（三层架构与铁律）
- [[guides/DeltaEtherCAT-DevGuide]] — 台达落地规范
- [[decisions/ADR-032-MotionControllerDeltaReplacement]] — 台达替换决策
- [[decisions/ADR-033-ZMotionRemovalAndDeltaLanding]] — 正运动移除与台达落地
- [[decisions/ADR-027-ThreeStateModelRefactor]]、[[decisions/ADR-029-RawDesignRefinement20260903]] — 三态模型与原档细化裁定
