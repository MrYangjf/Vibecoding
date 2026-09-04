---
title: ADR-037 主设备状态机语义修正与初始化时序重构
date: 2026-09-04
tags: [决策, 状态机, 初始化, 时序, 报警语义]
status: accepted
---

# ADR-037 主设备状态机语义修正与初始化时序重构

## 背景

2026-09-04 程序启动日志暴露两处违反设计意图的行为：

1. **初始态错误**：`DeviceControlWork._status` 初始值为 `Stop`，上电后首次互锁检查失败即出现 `Stop → Alarm`，而设计上设备从未复位过，不应出现 Stop。
2. **初始化链混入清状态**：`DoInitializeMachine` 开头调用 `ClearMachine()`（清状态是复位前动作），且初始化完成即置 `Stop`，与「只有复位流程成功才到 Stop」矛盾。
3. **初始化时序颠倒**：机器人通讯排在子设备之后（第 5 步），违背「通讯与子设备同级且优先开启」。
4. **连接失败仍置 Connected**：焊接头/运控 `Initialize()` 失败后仍无条件 `ConnectOn()`，报错与状态自相矛盾。

## 决议（用户 2026-09-04 裁定）

### D1 主设备状态机语义

| 时机 | 主设备态 |
|---|---|
| 程序打开（构造） | `NoReset`（初始值） |
| 初始化连接失败 / 运行报错 | `Alarm`（显示错误） |
| 消除报警 | **一律 `NoReset`**（关闭 OPEN-ClearAlarmSemantics：不再区分 wasRunning 回 Stop） |
| 初始化全部就绪 | **保持 `NoReset` 待复位**（不置 Stop） |
| 复位流程执行成功 | `Stop`（唯一合法的 →Stop 入口，经 `DoResetMachine`） |

### D2 初始化时序

1. 机器人通讯与子设备**同级且优先开启**（先通讯 → 焊接头 → 运控 → 线激光 → 监控相机）。
2. 通讯开启失败仅报通讯层错误，继续子设备连接。
3. **清状态只归复位前动作**（`DoResetMachine` 链内），初始化链禁止调用 `ClearMachine()`。
4. 子设备 `Initialize()` 失败则**不调用 `ConnectOn()`**，保持 Disconnected，由聚合判定计数。
5. 子设备焊接过程态初始值严格 `NoReset`；`Standby` 只能由复位流程完成产生。
6. 心跳检测仅在机器人通讯开启成功后启动；心跳失效 → 停止检测 → 触发重连（最多 3 次），重连失败保持关闭，杜绝叠罗汉式循环报警。

## 影响

- `DeviceControlWork`：初始值、`DoInitializeMachine` 顺序、`EvaluateInitializationResult`、`DoClearAlarm`、心跳线程。
- 运控 `ClearStatus` 不再经 `SetPhase(Idle)` 映射出中间 Standby。
- UI：`FormMain` 初始化移至 `Shown` + 等待 Modal（事件 `InitializationCompleted` 关闭）。
- 状态机语义细节见 [[architecture/DeviceControlArchitecture]] §9。

## 相关

- [[ADR-034-ThreeStateModelRefactor]]（三态模型本体）
- [[ADR-038-ErrorReportingHierarchy]]（报错分层）
- [[decisions/OPEN-ClearAlarmSemantics]]（已由 D1 关闭）
