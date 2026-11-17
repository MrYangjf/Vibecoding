---
title: ADR-014 主设备状态机语义修正与初始化时序重构
date: 2026-09-04
updated: 2026-10-30
tags: [决策, 状态机, 初始化, 时序, 报警语义]
status: accepted
---

# ADR-014 主设备状态机语义修正与初始化时序重构

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

- [[decisions/ADR-013-ThreeStateModelRefactor]]（三态模型本体）
- [[decisions/ADR-015-ErrorReportingHierarchy]]（报错分层）
- OPEN-ClearAlarmSemantics（已裁定关闭并入 ADR-020，2026-09-17 删除；映射见 [[decisions/ADR-Index]]）（已由 D1 关闭）

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 后果

### 正面
- （待补）

### 负面
- （待补）

## 演进记录

### 2026-11-03 · 决策 D3 · UI 连接态判定时机

- **变更**：UI 的连接态判定改到运控初始化结束回调（`DeviceControlWork.InitializationCompleted`）与连接态切换事件（`MotionControlWorkflow.StateSwitched`）之后统一执行一次；刷新计时器不再判定连接态。
- **理由**：运控初始化在 IO 工作线程执行，初始化期间 `MontionManager.IsInitialized` 恒为 false；UI 500ms 计时器在主站打开窗口内照常 Tick，会把「初始化中」误判为「未连接」，提前把自动刷新开关退回关闭并记日志。
- **影响**：`SystemControlPage` 计时器只跳过刷新；新增订阅上述两个既有事件，经 `InvokeRequired` 封送后走统一判定入口；连接流程与建轴/IO/气缸逻辑零改动。
- **判据**：只有初始化链结束或连接态切换后运控仍非就绪，才允许退回开关并记「未连接」日志；已连接成功路径不得出现该日志。

## 相关页面

- [[decisions/ADR-Index]]
