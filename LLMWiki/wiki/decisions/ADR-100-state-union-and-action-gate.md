---
title: ADR-100 两套状态联合与动作入口双闸门
date: 2026-11-17
updated: 2026-11-17
tags: [决策, 状态机, 一致性, 就绪]
status: accepted
---

# ADR-100 两套状态联合与动作入口双闸门

> **决策一句话**：设备态与流程态联合约束，动作入口同时校验设备态与就绪层

## 背景

`MainDeviceStatus` 6 态与 `SubDeviceWeldStatus` 7 态各自演进，组合无约束：设备 `Stop` 时流程仍可 `Working`，设备 `NoReset` 时流程可停在任意态，报警/急停与 `Working` 长期并存也无人纠正。D20 记录了状态分散在私有字段、无统一快照；动作入口只有连接二值判据，无法回答「为何拒绝」。

阶段 3 已把复位挂回既有链，`EnsureReadiness`（ADR-098）已实现但零调用；本阶段只做联合约束与接线。

## 决策

1. 联合约束采用「设备态 × 流程态」矩阵，逐格口径见总纲 §4.1.3；流程态 7 值以代码枚举为准，总纲表中的 `End` 当前由 `Standby` 承载，不新增枚举值
2. 设备态变化不自动级联流程态；流程态迁移仍只走 `CascadeWeldStatus → WeldStatusTrans`
3. 1 s 一致性巡检挂在既有 `thIOWork` 内（`ConsistencyTick`），不新建线程；只纠三类非法组合：
   - `Stop × Working` → `Standby`
   - `NoReset × 非 NoReset` → `NoReset`
   - `Alarm/EStop × Working` → `ErrorAborted`，`Alarm` 自进入起给 3 s 宽限，放行报警停焊瞬时组合
4. 子流程报警上送唯一通道：设备态 `Running` 或 `Stop` 时巡检发现 `ErrorAborted` → `ReportAlarm`；已是 `Alarm/EStop` 不重复上报（只升不降）
5. 日志口径：设备态变化沿一条 `Info`（演变 [[decisions/ADR-015-ErrorReportingHierarchy]] D2，仅限主设备态）；流程态级联一条；子流程 `OnWeldStatusChanged` 保持零日志
6. 动作入口双闸门：设备态必须 `Running`，且 `EnsureReadiness` 达门槛（自动焊接 L4、焊前检查 L0）；模拟模式沿用既有旁路放行；就绪拒绝日志只由工作流层记一次
7. 统一快照 `GetStatusSnapshot()` 只读聚合设备态/上一态/5 个流程态/运控就绪/线程登记/标志/报警，不持有状态
8. 巡检与闸门不改变复位链、急停链、心跳链的既有顺序与职责

## 备选方案

- 设备态变化自动级联流程态 → 双向耦合易震荡，且与「先停线程再断设备」冲突，弃
- 每个动作入口各写一套判断 → 判据分散、口径漂移，弃
- 为流程态另建状态机类 → 与原枚举形成两个真相源，弃
- 巡检独立线程 → 与 17 条常驻线程的关闭闭环冲突，弃
- 全矩阵逐格强制 → `Alarm × Standby` 等过渡态会被反复纠偏，现场噪声大，弃（只纠三类明确非法组合）

## 后果

### 正面
- 非法组合 1 s 内被纠正且留一条 `Warning`，可追溯
- 未复位即自动焊接会得到「当前 L / 需 L / 动作」的可读拒绝
- 设备态与流程态一次读出，UI 与日志共用同一快照
- 子流程失败不再静默，统一经 `ReportAlarm` 上升为设备 `Alarm`

### 负面
- 巡检存在最长 1 s 延迟，属安全网而非实时互锁
- `Alarm × Working` 宽限 3 s 为经验值，需现场按报警链耗时复核
- `NoReset` 下若有流程自行进入 `Standby`（如参数装载），会在 1 s 内被纠回 `NoReset`，属矩阵要求的行为

## 落地

- `DeviceControlWork.SetStatus`：变化沿一条 `Info`，进入 `Alarm` 刷新宽限
- `DeviceControlWork.ConsistencyTick` / `CorrectIllegalCombination`：巡检与纠偏
- `DeviceControlWork.CheckActionGate`：`DoSubWork`（L4）与 `DoSubPrework`（L0）接入
- `DeviceControlWork.GetStatusSnapshot` / `MachineStatusSnapshot`：统一快照
- `DeviceStatusWork.IOWork`：每拍调用 `ConsistencyTick`（内部 1 s 节流）

### 2026-11-17 · 决策 D29 · 动作入口双闸门补反向闸门：自动焊接流程在跑则禁一切 UI 手动动作
- **变更**：动作入口双闸门补反向闸门：自动焊接流程在跑则禁一切 UI 手动动作
- **理由**：手动与生产流程同时驱动同一根轴会互相打架；IsWelding 过宽会连正常调试一起禁掉
- **影响**：新增 DeviceControlWork.IsAutoWeldingRunning（焊接过程态 PreWork/Working/Stopping）为主设备级权威判据；轴与焊接头手动入口各自前置拒绝，停

### 2026-11-23 · 决策 D30 · 主页面轮廓显示门禁（手动模式隐藏）
- **决策**：`MainPage.ProfilePollLoop` 的轮廓显示门禁由 `RunMode != Manual` 改为 `IsAutoWeldingRunning || IsSimulationEnabled`；手动调试时 `HideContourForManual` 隐藏轮廓线与特征点并清零版本，切回自动/模拟按最新帧恢复。工艺曲线轮询不受影响。
- **理由**：① 模拟启动时 UI 把线激光流程置 `Manual`（界面动作语义），旧判据会把模拟轮廓误挡；② 手动调试切回主页面仍见轮廓（旧判据只不推进版本、不清空显示）。
- **影响**：沿用 D29 的 `IsAutoWeldingRunning` 为「手动 vs 生产」权威判据，不新增状态字段；⛔ 不用 `RunMode` 判主页显示（模拟态会被误挡）。

### 2026-11-23 · 决策 D31 · 动作入口按「手动 / 自动流程」分家：D29 门禁只约束手动入口
- **决策**：D29 的「自动焊接流程进行中 ⇒ 禁手动动作」门禁**只作用于 UI 手动入口**（`MotionControlWorkflow.TaExecute` / `LaserWeldHeadWorkflow.LaAuto` / `GalvoManualStart` 等）。主控在自动流程内部派发的动作属**流程组成**，不视为手动干预，故新增流程内自动入口：`MotionControlWorkflow.TaExecuteAuto()`、`LaserWeldHeadWorkflow.LaAutoAuto()`、`LaserWeldHeadWorkflow.GalvoWeaveStartAuto()`，三者⛔ 不做 D29 门禁检查。
- **理由**：焊前阶段（PreWork）已属自动流程（`IsAutoWeldingRunning` 在 PreWork 态为真），若复用手动入口会被 D29 全量拒绝，导致「真正工作自 PreWork 起」无法落地（TA/LA/振镜无法进工作模式）。
- **影响**：手动入口行为**不变**（D29 仍然生效，正常调试不被误伤）；自动入口仅由主控流程调用，⛔ 不暴露给 UI。见 [[decisions/ADR-038-RobotCommandDrivenStepFlow]] 三阶段章节 D5。

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-013-ThreeStateModelRefactor]]
- [[decisions/ADR-014-MainDeviceStateSemantics]]
- [[decisions/ADR-015-ErrorReportingHierarchy]]
- [[decisions/ADR-098-readiness-layering-axis-capability]]
- [[decisions/ADR-099-init-reset-separation]]
- [[api/DeviceControlWork]]
- [[api/DeviceStatusWork]]
- [[modules/DeviceControl]]
