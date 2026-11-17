---
title: 力矩类指令不要自造位置终点判据
date: 2026-11-06
updated: 2026-11-06
tags: [教训, TA, 力矩, CST, 位置判据, 现场否证]
status: active
---

# 力矩类指令不要自造位置终点判据

> **一句话**：力矩类指令（CST）只负责持续出力，终止条件必须由既有路径决定，⛔ 不要为了「看起来完整」而自造位置终点 + 撤力 + 锁位。

## 现象

`TA_Retract`（回缩）第一版被实现成「力矩出力 → 监视位置 → 进入零位容差 → 撤力 → 回 CSP 锁位」，现场日志为：

```
TA Retract 到位撤力 到位 当前 0.032mm … 用时 3.0s
TA Retract 撤力回 CSP 锁位 锁存位置 0.032mm
TA Retract 撤力回 CSP 达成 输出位 0 模式 CSP(8) 当前 0.025mm 锁存 0.032mm
```

业主否定：**不该有位置到位判定、不该撤力、不该回 CSP 锁位**。

## 根因

把「`TA_Retract` = `TA_Auto` 把方向反过来」误读成「反向回缩到零位」。前者是：
`切 CST → 开输出 → 按反向目标力矩持续出力 → 保持出力返回`；
后者（错误版）追加了 Auto 完全没有的三件事：位置终点判据、到位撤力、CSP 锁位。
连带衍生出四项无据设施：`WaitTaRetractReach`（位置终点等待）、`CutTaTorqueAndLock`（撤力+锁位）、
`InstructionRetractReverseGuardMm`（反向回升保护）、按行程动态放宽到 21s/60s 的超时。

## 判据

- 一旦为某条力矩指令引入「位置终点」，就必须同时回答：超时怎么定、方向配反怎么判、到位后是否撤力——
  这三个问题 Auto 都没有，说明该判据本身不属于力矩指令的语义。
- 「保持出力」类动作的正确返回值是**受理并生效**，不是**到达某个位置**。

## 预防

- 新增「X 的反向动作」类指令时，先逐行抄写 X 的实现，再只改方向符号与日志文案；
  出现第二个 `Wait*Reach` / 位置容差 / `StopTorque` 分支即视为偏离。
- 力矩生效检测固定 `InstructionDetectTimeoutSeconds`（5s），⛔ 不做按行程放宽的动态超时。
- 退出统一走既有路径：后续指令 / `ExitTaTorqueMode` / 急停，⛔ 不给单条指令造退出逻辑。

## 相关页面

- [[decisions/ADR-082-TaInitFourStepAndAvailability]]（D20/D21/D23 已作废，D24~D29 定稿）
- [[api/MotionControlWorkflow]]
- [[lessons/TorqueModeAsUiGate]]
