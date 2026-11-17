---
title: ADR-094 同类指令单一入口与形态一致
date: 2026-11-09
updated: 2026-11-09
tags: [决策]
status: accepted
---

# ADR-094 同类指令单一入口与形态一致

> **决策一句话**：同类指令单一入口与形态一致

## 背景

TA 族逐条指令各有一个公开方法，调用方与 UI 需要按指令名分支；ZeroPose 历史上因 UI 忙等遗留了异步 worker，与其它 TA 指令形态不一致

## 决策

1. 同一设备族同类指令只保留一个公开入口，指令类型用枚举表达，内部 switch 分派
2. 全族形态一致：阻塞到结果，异步需求须全族一起改，不得单条特例
3. 阻塞只允许发生在后台指令执行体，UI 不等待循环
4. 自动流程对设备族只调用自动指令并等待完成信号

## 备选方案

- 保留每条指令一个公开方法，仅抽取共用底层步骤：调用方仍需按指令名分支，新增指令继续扩散公开面（否决）。
- 统一入口 + 内部按指令各写一个实现方法：入口层反而变成转发表，未减少公开面（否决）。
- ZeroPose 保留异步 worker 特例：全族形态不一致，UI 仍需结果等待通道（否决，2026-11-09 业主裁定统一为阻塞）。

## 后果

### 正面
- 公开面从 7 个 TA 方法收敛为 1 个入口，UI 只改传参；新增指令只加枚举值与分支。
- 全族阻塞到结果，自动流程「完成后才继续」天然成立，不再依赖状态轮询或超时蒙混。
- 删除 ZeroPose 异步 worker 与 UI 侧 70s 事件等待，等待逻辑只剩一处。

### 负面
- 阻塞期间单飞登记一直被持有，原「新指令抢占零位运动」路径事实失效（由单飞拒绝替代）；~~`CancelTaZeroPose` 仅保留为防御性路径~~ → 2026-11-09 该接口已整个删除，见 D4。
- 初始化自检的 ZeroPose 与手动 ZeroPose 共用阻塞语义，thIOWork 在该步被占用至到位或超时（与改造前的 `RunTaZeroPoseSync` 行为一致）。

## 演进记录

| 编号 | 日期 | 决策 | 落点 |
|---|---|---|---|
| D1 | 2026-11-09 | TA_ZeroPose 四态（运行 / 跑过 / 到位 / 失败）与 `TaZeroPoseStageChanged` 事件归属流程层；硬件层只保留 `SetTaZeroPoseGate(done, reason)` 供流程层写入结果 | `MotionControlWorkflow` 持有四态字段与事件；`MontionManager` 只做门禁判定 |
| D2 | 2026-11-09 | `DescribeAxisDiagnosis` **不迁**，保留在 `MontionManager`（偏离业主清单） | 纯硬件只读快照，被 `YGateReason` / `GetAxisGateReason` / `EnableAxesAfterInit` 三处依赖；迁走会造成流程层向上依赖或诊断退化 |
| D3 | 2026-11-09 | `BuildMachineInitSummary` / `LogAxisGateReport` 迁流程层 | 整机初始化叙述属编排，硬件层只给状态字/位置/模式原始快照 |
| D4 | 2026-11-09 | `CancelTaZeroPose` 整个删除，⛔ 不设「取消指令」专用函数接口 | TA 指令只响应急停 / 停止两类外部终止：急停 `CancelAllAxisInstructions`、停止 `StopAxis` 内单轴取消；阻塞等待的 `token` 立即返回，`finally` 照常释放单飞 |
| D5 | 2026-11-09 | **不引入** `IMotion.MontionAxis` 通用抽象，继续用具体 `DeltaMontionAxis` | TA 与 Y 均为台达轴、不会更换；通用抽象轴能力未写全。同时纠正事实：**送丝就是 TA，不存在第三个轴** —— `SetWireFeedTorque*` 本质是 TA 力矩成员，已更名 `SetTaTorque*` 归流程层，⛔ 不再造「送丝轴」概念、⛔ 不按三轴口径描述 |
| D6 | 2026-11-09 | ZeroPose 双实现合并 | `WaitTaZeroPose` + `RunTaZeroPoseSync` 删除，手动与初始化共用 `ExecuteTaZeroPose`，唯一 `finally` 释放运行态与单飞 |

## 相关页面

- [[decisions/ADR-Index]]
- [[standards/CodeSimplification]] §一之二⑥
- [[api/MotionControlWorkflow]]
