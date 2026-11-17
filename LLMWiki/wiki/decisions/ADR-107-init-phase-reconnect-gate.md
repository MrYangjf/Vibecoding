---
title: ADR-107 初始化期禁重连与设备动作 + 机器人端 XML 写入并发保护
date: 2026-11-17
updated: 2026-11-17
tags: [决策, 初始化, 通讯, 并发, RSI]
status: accepted
---

# ADR-107 初始化期禁重连与设备动作 + 机器人端 XML 写入并发保护

> **决策一句话**：初始化动作结束拿到结果前，不启动重连线程、不允许手动设备动作；机器人端 XML 写入加锁 + 原子替换 + 占用重试。

## 背景

机器人端 RSI XML（`WeldControlConfig.xml`）在初始化期间报「正由另一进程使用」而写入失败。

根因：`SaveRobotRsiXml()` 无任何并发保护，而三条调用路径会并发到达同一文件：

1. 初始化链 `CommWork()` → `InitializeRobotComm()`；
2. 通讯层自愈 `EnsureRobotChannelHealthy()` → `InitializeRobotComm()`（ADR-102 引入，`thCommCommandWork` 每拍调用，且 `_lastRobotReconnectMs` 首拍为 0 故必然进入）；
3. UI 手动点「开启监听」→ `InitializeRobotComm()`。

线程启动顺序造成竞争：`InitializeMachine()` 先启动 `thCommCommandWork`（含自愈重连），随后初始化链才执行 `CommWork()`，两线程同时写同一 XML 触发 `IOException`。

业主强制要求：**初始化动作时任何重连线程和动作都不开启，必须等初始化结束、拿到结果才能重连或做其他动作。**

## 决策

1. `thCommCommandWork`（含通讯层自动重连）**不在 `InitializeMachine()` 中启动**，改由初始化链结束后统一开启：正常结束走 `FinishInitialization()` 末尾，抢占中止走 `InitializeMachineTick` 的抢占分支，两处统一调 `EnsureCommandWorkStarted()`（幂等；`MachineCommandWorkOpen` 自带 `_commStarted` 守卫）。
2. 初始化期间禁止手动设备动作：`FilebackupPage` 新增 `TryPassCommAction` 两档门控（关闭中 / 初始化中），「开启监听」与「关闭监听」入口均校验，参照 `ILCamPage` 的 `TryPassPageAction` 模式。
3. `SaveRobotRsiXml()` 写盘加 `_rsiXmlLock` 互斥锁；锁内先写同目录临时文件，再用 `File.Replace` 原子替换，并对瞬态占用做 5 次 × 60ms 退避重试（`WriteXmlWithRetry`）；格式文档同法写入。
4. 心跳线程维持原状（只检测分级不重连，初始化成功后由 `CommWork` 的 `EnsureHeartbeatThread` 惰性创建），不受本次门控影响。

## 备选方案

- 仅加写锁不动线程时序 → 初始化期仍有自愈线程抢跑，治标不治本，且违背业主强制要求，弃。
- 仅延后线程不加锁 → 初始化后手动连接与自愈仍可能撞车，弃。
- 用 `File.Replace` 单独解决占用 → 目标被占用时 `File.Replace` 同样抛异常，不能替代锁，弃。

## 后果

### 正面
- 初始化期机器人端 XML 只有初始化链一个写者，「文件正由另一进程使用」不再出现。
- 初始化期间无自愈重连抢跑，符合「初始化结束拿到结果才允许重连」的强制要求。
- 写盘加锁 + 原子替换 + 重试，残余并发场景下也能自愈。

### 负面
- 初始化期间机器人指令线程不启动，指令下发能力延后到初始化链结束（初始化期本就无通道可用，影响有限）。
- 抢占中止路径也需开启指令线程，两处出口都要维护（已用 `EnsureCommandWorkStarted` 统一）。
- 写锁为进程内互斥，跨进程占用（多实例）仍依赖退避重试，无法根治。

## 落地

- `MainDeviceControl/DeviceControlWork.cs`：`InitializeMachine` 去掉 `MachineCommandWorkOpen`；`FinishInitialization` 与抢占分支调 `EnsureCommandWorkStarted`
- `Comm/Communication/CommunicationManager.cs`：`_rsiXmlLock`、`WriteXmlWithRetry`、`TryDeleteTempFile`
- `UIDesign/TabPage/FilebackupPage.cs`：`TryPassCommAction` 门控

### 2026-11-17 · 决策 D107 · 扩展初始化期线程门控：5 条模组工作线程延后到 FinishInitialization（含拒绝/全连跳过出口 EndI
- **变更**：扩展初始化期线程门控：5 条模组工作线程延后到 FinishInitialization（含拒绝/全连跳过出口 EndInitWithoutChain）；IOWork 初始化期只推进连接链、冻结全部状
- **理由**：现场日志显示初始化未完成时 IO 监控线程已跑互锁并置 NoReset 转 Alarm、且配置被读两次——ADR-107 原仅收口指令线程，未覆盖模组线程与 IOWork 状态变更；业主明令初始化连接
- **影响**：InitializeMachine 不再开模组线程；FinishInitialization/抢占中止/拒绝跳过三出口统一开线程；IOWork 初始化分支仅保留 InitializeMachineTi

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-102-heartbeat-levels-and-comm-reconnect]]
- [[decisions/ADR-099-init-reset-separation]]
- [[api/CommunicationManager]]
- [[api/DeviceControlWork]]
- [[api/FilebackupPage]]
- [[standards/CodeSimplification]]
