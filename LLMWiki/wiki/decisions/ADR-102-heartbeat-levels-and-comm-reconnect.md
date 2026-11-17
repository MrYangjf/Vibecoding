---
title: ADR-102 心跳分级与通讯层自动重连
date: 2026-11-17
updated: 2026-11-17
tags: [决策, 通讯, 心跳, 重连, 线程]
status: accepted
---

# ADR-102 心跳分级与通讯层自动重连

> **决策一句话**：心跳线程只在机器人通道监听成功后启动，只做 H0~H4 分级上报；重连归通讯层，由指令线程按 5 s 冷却触发。

## 背景

N07 要求「未连接不存在心跳线程；H3/H4 由通讯层自动重连；`NeedHeartbeat=false` 只停心跳日志与分级，界面仍显示在线/离线」。原实现 `MachineCommandWorkOpen` 无条件创建心跳线程；收到断链后心跳线程自行 `TryReconnectRobotComm()`，失败 3 次即 `return`，线程永久退出而 `_commStarted` 仍为 true，无法再拉起（D09）。

## 决策

1. `MachineCommandWorkOpen` 仅启动 `thCommCommandWork`；`EnsureHeartbeatThread()` 在 `CommWork()` 的 `ConnectRobot()` 成功后调用，未连接不创建心跳线程。
2. 心跳线程按最近收包间隔分级：H4 通道未运行；H3 断流 >500 ms 或从未收包；H1 >2×RSI 周期且 ≤500 ms；H0 正常；H2 留给阶段 7 缺值距离。
3. 分级只记变化沿：H4 Error、H3 Warning、H1 Debug、H0 Info；`NeedHeartbeat=false` 时四级日志全停，但 `_robotOnline` 仍按 `IsRobotOnline` 刷新。
4. 删除心跳线程内 `TryReconnectRobotComm` 与 `HeartReconnectIntervalMs`；心跳线程不再 `return`。
5. `CommunicationManager.EnsureRobotChannelHealthy()` 为通讯层自愈入口：通道未监听时按 5 s 冷却执行 `InitializeRobotComm + ConnectRobot`，成功/失败各一条日志；由 `CommCommandWork` 每拍调用。
6. 新增 INI 键 `NeedHeartbeat`（默认 true）并纳入 `HealCommunicationIni` 只增补键。

## 备选方案

- 心跳线程内做重连 → 职责混层且失败即退出（D09 根因），弃。
- 为通讯层新增独立重连线程/定时器 → 增加并行机制，弃。
- 用 `NeedHeartbeat=false` 同时关闭在线显示 → 违反 N07，弃。

## 后果

### 正面
- 未连接阶段不存在心跳线程，线程清单与实际一致。
- 断流只报一条 H3，恢复报一条 H0；重连不会让心跳线程永久消失。
- 在线显示与心跳日志解耦，关日志不影响 UI。

### 负面
- 通道重启存在最长 5 s 冷却窗口，期间 H4 持续。
- UDP 断流本身无需重建套接字，H3→H0 主要靠收包恢复，现场需实测确认。

## 落地

- `DeviceControlWork.MachineCommandWorkOpen` / `EnsureHeartbeatThread`
- `DeviceControlWork.HeartInspectWork` / `EvaluateHeartbeatLevel` / `LogHeartbeatEdge`
- `DeviceControlWork.CommCommandWork`：每拍 `EnsureRobotChannelHealthy`
- `CommunicationManager.EnsureRobotChannelHealthy` / `NeedHeartbeat` / `IniKeyNeedHeartbeat`

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-101-shutdown-closure-and-estop]]
- [[decisions/ADR-103-no-value-hold-and-distance-segment]]（H2 已接入缺值超限）
- [[api/DeviceControlWork]]
- [[api/CommunicationManager]]
- [[modules/DeviceControl]]
