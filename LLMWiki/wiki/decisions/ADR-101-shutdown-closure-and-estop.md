---
title: ADR-101 关闭闭环与急停只停机不断设备
date: 2026-11-17
updated: 2026-11-17
tags: [决策, 生命周期, 关闭, 急停, 线程]
status: accepted
---

# ADR-101 关闭闭环与急停只停机不断设备

> **决策一句话**：关闭走唯一顺序且有 30 s 预算与逐台确认；急停只做「停运动 → 停线程 → 置失能」，不断设备。

## 背景

总纲 N05/N06 要求关闭可证明、急停可恢复。现状缺陷：`DisposeComponents` 无幂等守卫与预算（D10）；`CascadeDisconnect` 受理即返回后直接打印关闭完成（D05）；模组线程与通讯线程共用 `IsCloseWork`（D07）；关闭期 `thIOWork` 仍推进初始化与对齐 tick（D11）；`DoEstopMachine` 在急停末尾断开全部设备（D02）；`MontionManager.Close()` 由 `InitializeOff` 与 `DisposeManaged` 双路径调用（D04）；线激光连接/断开线程无句柄无 Join（D13）；模拟线程只置标志（D15）；退出链未释放监控相机/线激光/通讯 SDK（D19）。

## 决策

1. 关闭顺序固定为：清虚拟 IO → 模组线程 → 通讯线程 → 状态/动作线程 → 模拟线程 → 逐台断设备（每台等 5 s）→ 关机器人通道；总预算 30 s。
2. `DisposeComponents` 以 `_disposed` 幂等、`_shuttingDown` 拒绝新业务；每步前检查预算，超时打印「强制退出 原因 … 步骤 … 时点 …」。
3. 关闭汇总一条：`关闭完成 线程 n/11 设备 m/4 用时 xms`；11 条口径 = 5 模组 + 2 通讯 + 3 状态 + 1 动作。
4. `CascadeDisconnect` 改为「受理 + 轮询等待 `Disconnected` + 单台超时」，超时只记 Warning 不中断后续设备；`DisposeComponents` 与 `DoStopMachine` 共用。
5. 线程退出标志拆分：模组沿用 `IsCloseWork`，通讯改用 `_commCloseWork`，由 `MachineCommandWorkClose` 独立关闭；停模组不再连带停心跳/指令线程。
6. 关闭期 `IOWork` 只保活，不再推进 `ScanRunningIo`/`ConsistencyTick`/`InitializeMachineTick`/`MonitorAlignTick`。
7. 急停顺序固定：`EmergencyStop`（TX_ABORT + 轴急停）→ 置 `EStop` → 停模组线程并 Join → `ServoOffAll`；**不调用 `CascadeDisconnect`**，T09~T11 保持运行，解除走既有 `EstopCancel → NoReset`。
8. 运控关闭唯一入口为 `MotionControlWorkflow.InitializeOff()`；`DisposeManaged` 委派该入口；`MontionManager.Close()` 增加幂等守卫。
9. 线激光连接/断开线程保存句柄并纳入线程登记，`DisposeManaged` Join；模拟线程关闭时 Join 并复位句柄。
10. 退出链在 `FormMain_FormClosed` 追加释放 `MonitorCamManager`、`LineLaserManager`、`CommunicationManager` 的 SDK 资源。

## 备选方案

- 关闭改为独立后台线程统一编排 → 与「禁止新线程、既有链扩展」冲突，弃。
- 设备断开使用 `Thread.Abort` 强制终止 → 总纲明令禁止，弃。
- 急停保留断设备以便彻底断电 → 解除后无法读状态与复位，且业主已裁定只停机，弃。
- 为通讯线程另建一套线程管理器 → 与既有登记表形成两个真相源，弃。

## 后果

### 正面
- 关闭过程逐步可观测，超时有原因与时点，重复退出无副作用。
- 急停后设备仍在线，L1~L4 失效但可查询，恢复路径最短。
- 停模组不再误停心跳，报警与在线显示不被连带破坏。

### 负面
- 关闭最坏路径按预算可能被强制截断，需现场核对未断设备并手工处理。
- 逐台等待使退出耗时上限由 5 s/台决定，30 s 预算需现场验证。
- 急停后伺服使能关闭，恢复必须人工复位。

## 落地

- `DeviceControlWork.DisposeComponents` / `ShutdownBudgetExceeded` / `GetWorkThreadExitSummary`
- `DeviceControlWork.CascadeDisconnectWithWait` / `WaitChildDisconnected`
- `DeviceControlWork.MachineCommandWorkClose` / `_commCloseWork`
- `DeviceControlWork.DoEstopMachine` / `CloseRobotChannel`
- `DeviceStatusWork.IOWork`：`IsShuttingDown` 保活分支
- `MotionControlWorkflow.InitializeOff` / `DisposeManaged`
- `MontionManager.Close`：幂等守卫
- `LineLaserWorkflow.ConnectOn/ConnectOff/DisposeManaged`
- `FormMain.FormMain_FormClosed`：管理器释放

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-092-ExceptionLoggingAndShellRemoval]]
- [[decisions/ADR-098-readiness-layering-axis-capability]]
- [[decisions/ADR-099-init-reset-separation]]
- [[decisions/ADR-100-state-union-and-action-gate]]
- [[api/DeviceControlWork]]
- [[api/DeviceStatusWork]]
- [[api/MotionControlWorkflow]]
- [[modules/DeviceControl]]
