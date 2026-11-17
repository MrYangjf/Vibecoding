---
title: "ADR-041 — 常驻流程非阻塞范式（三层铁律 · 步号范式 · 初始化与指令链步驱动化）"
date: 2026-09-23
updated: 2026-10-30
tags: [MainDeviceControl, DeviceWorkflowBase, 非阻塞, 步驱动, 初始化]
status: accepted
deciders: ["业主"]
---

# ADR-041 — 常驻流程非阻塞范式（三层铁律 · 步号范式 · 初始化与指令链步驱动化）

> **✅ 演进（2026-09-23 晚，业主实测反馈补充）**：FlowProcess 内的 Do 动作函数统一改写为**小步 switch-case 模板**——`switch (小步状态)` 的每个 case 即流程入点，直观可读：小步 11/12 =「下发使能 → 等完成」、小步 21/22 =「判位下发 → 等到位」（`DoServoOn` / `DoReturnToCalibration` 已落地）。配套**日志纪律**：小步判定分支是按拍反复进入的热路径，**禁止写 log**；只有**发指令拍**与**完成拍**（含超时失败拍）写 log——否则判断点 log 爆炸。首批落地 `MotionControlWorkflow`，其余 workflow 的轮询分支已核验静默合规。

## 背景（业主多轮澄清，权威）

1. **范式定性**：workflow 统一为「设备主要流程（FlowProcess、ResetProcess 等）= 常驻流程」+ 阻塞动作指令 + 非阻塞动作指令三类。阻塞/非阻塞**无包含关系**，由**消费方**决定使用哪一种。基类契约只改名不全量重构。
2. **非阻塞三层铁律**（2026-09-23 第二轮澄清定稿）：
 - ① **流程层**：FlowProcess 常驻按拍执行，无内部阻塞循环——外部一有终止命令就能中断；
 - ② **等待层**：「等待完成」= **非阻塞轮询变量**——每拍判断当前小步，`if (变量 false→true)` 跳转下一小步，直到整个动作完成跳转下一大步（置位 RunStep 后下一次直接进入下一大步）；绝不是线程等待；
 - ③ **命令层**：流程**内部执行的命令本身也必须非阻塞**（下发即返回）。非阻塞流程里调一个阻塞命令，该拍卡住出不来——等价于阻塞。
3. **步号范式**：大步骤 10/20/30，内部小步骤 +1（10→11→12…）。

## 问题（Phase 0 盘点：三层铁律违反点）

| # | 缺陷 | 位置 |
|---|---|---|
| A | **初始化链阻塞 IO 刷新**：`DoInitializeMachine` 运行在 thIOWork（IO 扫描线程）内，`WaitChildConnected` 用 `Thread.Sleep` 循环等子设备连接（最长 10s）——等待期间 IO 完全不刷新（业主：一旦阻塞 IO 就刷新不到了） | `DeviceControlWork.cs` |
| B | **命名不准**：基类契约 `#region 全阻塞流程（10 项）` 与 5 个 workflow 同名 region——FlowProcess 实际已是按拍步驱动，「全阻塞」定性错误 | `DeviceWorkflowBase.cs` + 5 workflow |
| C | **步号范式不一**：运控步号 10/15/20 混用，未按大步 10/20/30 + 小步 +1 | `MotionControlWorkflow.cs` |

## 决议

1. **命名换轨**：`#region 全阻塞流程` → `#region 常驻流程（设备主流程）`；`#region 非阻塞流程` → `#region 非阻塞动作指令`；基类与 5 个 workflow 全部同步。行为零改动。三层铁律与步号范式写入基类 region 注释。
2. **初始化链步驱动化**：`DoInitializeMachine` 改**受理制**（置首步即返回，非阻塞）；新增 `InitializeMachineTick` 由 thIOWork 每拍推进——步号 10 机器人通讯 → 12 运控 → 14 焊接头 → 20/21 线激光受理/等待 → 30/31 监控相机受理/等待 → 40 聚合判定；等待小步按拍轮询 `ConnectSettled`（false→true）或超时放行，每步前置问询 `IsInitPreempted`（原 `IsInitAborted` 语义）。⛔ `WaitChildConnected`（Sleep 轮询）删除。
3. **步号规范化（核心两件先行）**：`MotionControlWorkflow` 大步 10 = PreWork 启动段（小步 11 伺服使能 → 12 标定位回归），大步 20 = 已使能待机；`GetStepName` 同步。收尾类步号（700/900/0）为基类段位约定，保持。其余 workflow 保留现步号（后续按需换轨）。
4. **机器人指令前置条件问询**：`CommCommandWork` 指令转换后、置位前新增 `IsCommandPreconditionMet`——启动类（IoStart）要求整机 Stop 且无子设备 ErrorAborted；停止类（IoStop）要求整机 Running；不满足拒收并留痕。
5. **IO 轮询形态裁定**：`DeviceStatusWork` 三个专用线程 while+Sleep 节拍**保留**（节拍是刷新周期不是阻塞），handler 内零阻塞调用。

## 影响

- `DeviceStateApiCore/DeviceWorkflowBase.cs`：region 改名 + 三层铁律注释。
- `DeviceControlWork.cs`：+`InitializeMachineTick`/`WaitChildConnectedTick`/`AdvanceInitStep`/`IsCommandPreconditionMet`；`DoInitializeMachine` 受理制；删 `WaitChildConnected`/`IsInitAborted`/`WaitChildPollMs`。
- `DeviceStatusWork.cs`：`IOWork` 每拍接入 `InitializeMachineTick`。
- `DeviceWorkflow/` 5 文件：region 改名；`MotionControlWorkflow` 步号 10/15 → 11/12。

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

- [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（焊接启动门控——本范式第一个落地消费方）
- [[decisions/ADR-038-RobotCommandDrivenStepFlow]]（机器人指令驱动步骤流）
- [[modules/DeviceControl]]、[[api/DeviceControlWork]]
