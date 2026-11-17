---
title: ADR-104 报警停焊时 RSI 通道保持与自适应载荷冻结
date: 2026-11-17
updated: 2026-11-17
tags: [决策, 报警, RSI, 自适应, 载荷冻结]
status: accepted
---

# ADR-104 报警停焊时 RSI 通道保持与自适应载荷冻结

> **决策一句话**：报警停焊后自适应各输出通道全部停止、机器人载荷冻结为报警时刻值，RSI 收发通道与周期保持不变，清警只撤报警标志不恢复刷新也不续焊。

## 背景

业主确认报警停焊后自适应参数须停止输出，且需先核清 RSI 收发事实再定方案。核实结论：机器人按 IPO 周期（`CycleMs`，默认 12 ms）主动发 XML，本机每收一帧回一帧（同 IPOC），通道由收包信号驱动并与载荷解耦；自适应参数经 `SendToRobot` → `UpdateRobotWeldParams` → `SetReplyValues` 只写回复缓存（五个具名元素），下一帧组包发出，因此不写缓存即载荷冻结而通道不断。

原实现的缺口：`ReportAlarm` 只置 `Alarm`，五路流程要等 `AlarmFlowGraceSeconds` 宽限才收束；`WeldParamControlWorkflow` 的 `StepCompute`/`StepOutput` 不受 `WeldStatus` 门禁，报警落在半途会再下发并把 `Working` 拉回；`MonitorAlignTick` 剪丝回检超时会覆盖冻结载荷并写振镜中心补偿；`TxNG` 锁存后无任何清除入口，清警后机器人仍持续看到报警态。

## 决策

1. 通道不动：RSI 周期与回写路径不改，不新增线程、定时器或第二套停止通道。
2. 载荷冻结：报警停焊后不再调用任何 `SetReplyValues` 路径，`WeldPower/WireSpeed/CutWire/WeldSpeed/WeaveAmp` 保持报警时刻值。
3. 停止动作挂既有报警链：`ReportAlarm` 内立即 `CascadeWeldStatus(ErrorAborted)`，各通道随各自 `WeldStatus` 停输出，不等宽限。
4. `FlowProcess` 与 `PreWork` 以 `ErrorAborted` / `IsAlarmstop` 收口，杜绝半途再下发与 `Working` 回拉。
5. `MonitorAlignTick` 报警期停走并把剪丝相位归零，避免覆盖冻结载荷与写振镜中心补偿。
6. 摆焊执行器非 `Working` 时幅值归零（执行器停摆），RSI 载荷仍为冻结值。
7. 报警态继续用 `TxNG` 锁存重发，机器人每帧可见报警态；清警走 `ClearRobotCommand` → `ClearTxCommand` 停发。
8. 清警只回 `NoReset`，不改任何 `WeldStatus`；载荷恢复刷新只在下次焊接进入 `Working`，不自行续焊。

## 备选方案

- 报警期停发 RSI 报文 → 机器人会判通讯超时且破坏同周期回写契约，弃。
- 报警期把五个元素清 0 → 属改值而非冻结，机器人侧会看到非报警时刻的工艺值，弃。
- 新增独立「自适应暂停」线程/定时器统一收口 → 并行机制，弃；停止动作统一挂既有报警链。
- 依赖 `AlarmFlowGraceSeconds` 宽限自然收束 → 存在数秒继续下发窗口，与「停焊即停」冲突，弃。

## 后果

### 正面
- 报警停焊后无任何自适应旧值继续下发，现场无「停机后仍在变参」现象。
- 通道不中断，机器人不会误判断联，报警态与清警态都可被机器人逐帧观测。

### 负面
- 冻结值为报警时刻值，若该值本身不合理，需人工清警后重新起焊，不能在线修正。
- 清警后载荷仍为旧值，直到下次焊接才刷新，调试页的手工注入是唯一例外（非自适应链）。

## 落地

- `DeviceControlWork.ReportAlarm` / `DoClearAlarm` / `ReportAlarmCleared` / `MonitorAlignTick` / `ClearRobotCommand`
- `WeldParamControlWorkflow.FlowProcess` / `PreWork`
- `LaserWeldHeadWorkflow.ApplyGalvoAmplitude`
- `CommunicationManager.ClearRobotCommand` → `KukaRsiComm.ClearTxCommand`

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-103-no-value-hold-and-distance-segment]]
- [[api/DeviceControlWork]]
- [[api/WeldParamControlWorkflow]]
- [[api/CommunicationManager]]
- [[api/LaserWeldHeadWorkflow]]
