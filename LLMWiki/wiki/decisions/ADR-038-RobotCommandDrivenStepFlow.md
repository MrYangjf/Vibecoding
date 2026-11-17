---
title: "ADR-038: 机器人指令驱动步骤流（子流程禁自迁步）"
date: 2026-09-20
updated: 2026-10-30
tags: [主控, 步骤驱动, 命令表, 模拟仿真器]
status: accepted
---

# ADR-038: 机器人指令驱动步骤流（子流程禁自迁步）

## 裁定

本设备下挂机器人，主要工作由机器人指令调度。步骤迁移的唯一驱动源 = **设备主控（DeviceControlWork）消费命令**，子流程（5 个 DeviceWorkflow）**禁止自行迁移执行步跨阶段**。

## 命令驱动范式（唯一合法链路）

```
机器人指令 / IO / UI
 → ExecuteIo(IoSubPrework / IoSubWork / IoSubStop / IoSubManualStop / IoSubAlarmStop)
 → DoSubPrework / DoSubWork / DoSubStop / …
 → CascadeWeldStatus(PreWork / Working / Stopping / …)
 → 子流程 RequestWeldStatus → OnWeldStatusChanged 钩子 → AdvanceStep(阶段入口)
```

时序语义（用户裁定 2026-09-20）：
1. 机器人发 PreWork 指令 → 主控切线激光等子流程 RunStep 到 PreWork；
2. 子流程执行完成 → **写完成反馈状态**（如线激光 `IsPreWorkFeedbackDone`：数据稳定 + 进入等待步）→ 停在等待步；
3. 主控收到完成判断结果 → 反馈机器人 → **等待下一条指令**；
4. 机器人发 Work 指令 → 主控才切子流程 RunStep 到 Working。

## 红线

- **子流程不自迁步**：阶段内子步链（如 PreWork 内部 10→20→30→31）允许，跨阶段迁移（31→100、100→700）只允许由 WeldStatus 命令钩子触发。
- **行程判断唯一归属主控**（`CheckWeldProgress`）：子流程 DoWorking 不判行程、不自置 Stopping。
 - 模拟：目标 = 随机 1500~2000mm（`_simWeldLengthMm`，每次开启模拟重取），起点/目标在 Working 命令下发时锚定；
 - 真实：机器人决定焊接停止 X，协议细化后由 Work 指令携带目标（todo），现以线激光 `MaxWeldLengthMm` 配置兜底；
 - 到程 → 主控走 `DoSubStop()` 命令链下发焊接完成（原因含「焊缝行程完成」），UI 据此联动收尾。
- **WeldParam / Monitor 开始与结束由主控控制**：微周期（计算→下发 / 采集→分析）保留为其本职，但触发挂 `WeldStatus == Working` 门禁；焊接头/监控等不参与模拟的子设备由模拟停驱（IsEnable=false）。
- **模拟 = 主控内置机器人仿真器**：`SimScheduleTick` 状态机（等线激光 PreWork → 等完成反馈 → 下发 Working），由模拟测试线程每拍驱动；不一次性连发、不越权直驱子流程步骤。模拟用真实线激光但未连接时由 `StartSimulationLineLaser` 自动连接（连接失败报错退出）。
- **模拟必须走主控命令面 `DoSubWork`，禁止对子流程直发 `RequestWeldStatus(Working)`**：`DoSubWork` 内 `CascadeWeldStatus(Working)` + `BeginWeldMonitor()` + `BeginProductSession()` 三者必须同生共死。若仿真器绕过 `DoSubWork` 直驱子流程 → `BeginWeldMonitor` 不启动（行程到程永不触发 `CheckWeldProgress`/`DoSubStop`，模拟卡死）且生产会话不开（不记录）。**生产会话只能随 Working 命令开**：`StartSimulation()` 不得提前 `BeginProductSession`（否则与 `DoSubWork` 双开、且违背 ADR-037 会话随 Working 启停）。

## 违规清理记录（2026-09-20）

| 原违规 | 位置 | 处置 |
|---|---|---|
| DoWorking 判行程并自动 AdvanceStep(StepStopping) | LineLaserWorkflow | 删 `IsWeldLengthReached`/`StopByWeldLengthReached`，DoWorking 改 void；Stopping 仅经 WeldStatusTrans |
| 模拟旁路直接 AdvanceStep(StepWorking)+自置 Working | LineLaserWorkflow / MotionControlWorkflow | 收窄为命令门控（WeldStatus==Working 才迁移步），不自置 WeldStatus |
| SimAutoStartSubflows 不等反馈连发 PreWork+Working | DeviceControlWork | 改 `SimScheduleTick` 反馈驱动状态机 |
| 行程目标用线激光配置 MaxWeldLength（1000） | DeviceControlWork | 模拟改随机 1500~2000mm；真实沿用配置兜底 + 机器人协议 todo |
| 模拟 `SimScheduleTick` 直发 `RequestWeldStatus(Working)` 绕过 `DoSubWork` + `StartSimulation` 提前 `BeginProductSession` | DeviceControlWork | 仿真器收反馈后改调 `DoSubWork()`（与真实 `ExecuteIo(IoSubWork)` 等价）；删 `StartSimulation` 提前开会话，会话统一随 Working 命令开 |

## 关联

- 步骤驱动机制基座：[[decisions/ADR-035-RawDesignRefinement20260903]]（C6：RunStep + bool 推进）
- 模拟红线沿革：[[decisions/ADR-032-SimulationTestRedesign]]（ADR-038 修订其「模拟跳过 PreWork」：线激光现走真实 PreWork 链路 + 自动连接）
- 记录生命周期：[[decisions/ADR-037-ProductProductionRecordLifecycle]]

## 背景

（待补：本决策要解决什么问题）

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 后果

### 正面
- （待补）

### 负面
- （待补）

## 相关页面

- [[decisions/ADR-Index]]
