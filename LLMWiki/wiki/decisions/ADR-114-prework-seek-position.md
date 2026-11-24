---
title: ADR-114 焊前寻位：PreWork 阶段 Y 轴到达焊缝焊接点
date: 2026-11-23
updated: 2026-11-23
tags: [决策, PreWork, 焊前寻位, 模拟, 运控, 跟踪]
status: accepted
---

# ADR-114 焊前寻位：PreWork 阶段 Y 轴到达焊缝焊接点

> **决策一句话**：PreWork 阶段新增「焊前寻位」步，X 移动中 Y 跟随跟踪，到达焊前位且 Y 到达焊缝焊接点即完成

## 背景

PreWork 阶段机器人移动到焊前位时，Y 轴仍停在固定标定位；起焊瞬间才随焊缝移动，首点不在焊点上。业主重做该环节为「焊前寻位」：寻位方式与焊接工作模式一致（提前扫后跟踪），PreWork 期间 X 移动中边走边建图、Y 跟随跟踪，到达焊前位且 Y 到达焊缝焊接点即完成；模拟侧需可配置该寻位起点 X。

## 决策

1. 新增 PreWork 运控步 `StepPreWorkSeek = 13`：使能 → 回归标定位 → **焊前寻位** → 就绪
2. 焊前寻位完成判据 = **X 到位**（机器人焊前位 X / 模拟设定点）**且 Y 在跟踪目标容差内**（0.1mm）；超时 60s 即 PreWork 失败报警停焊
3. PreWork 阶段**不启用缺值量测、不报 NoValueAlarm**（引导未稳属正常），仅在到达 X 时 Y 未到位才判失败
4. 机器人焊前位 X 由 `RX_PRE_WELD_POSE` 报文解析首个数记录（`ApplyRobotPreWeldPose`），到位判据取当前 X 与该值差 ≤5mm
5. 模拟侧新增可配置「焊接前寻位起点 X(mm)」（`SimulationController.ini` 的 `PreWorkStartXmm` 键 + 系统设置模拟区输入框）；模拟开启即自 X=0 移向该点，**到达即停 X 前进**，起焊段由 `StartRobotXMoving` 继续沿焊缝前进
6. 落地：`MotionControlWorkflow.DoPreWorkSeek`、`DeviceControlWork.IsPreWorkXArrived` 与 `ApplyRobotPreWeldPose`、`SimulationConfig.LoadPreWorkStartXmm` 与 `SavePreWorkStartXmm`、`SystemControlPage.numPreWorkStartX`

### 2026-11-23 增补 · Y 轴必须真实移动到焊接点，未到位报 PREWORK 错误

> **业主口径**：「我要求的动作是在寻位的时候 Y 轴真实移动到焊接位置。且如果没有移动到焊接位置还要报 PREWORK 错误。」现场现象：寻位阶段轴反馈恒 -37.000 / 命令 -37.000 / 脉冲 -37000 / 段距 0.0000 ⇒ **Y 轴根本没动**，而判据因「目标恰好≈当前位置」判成已到位。

- **决策 D7 · 到位判据须含「轴真的响应过跟踪」**：`DoPreWorkSeek` 记录寻位起始轴位置 `_preWorkSeekStartAxisPos`；到位 = 引导目标有效（`TryGetSeamTrackingTargetY` 返回 true）**且** `|targetY − axisPos| ≤ 0.1mm` **且**（目标偏离起点时）**轴累计位移 ≥ 0.002mm**。⛔ 禁止「目标≈当前位置」直接判到位。
- **决策 D8 · 未到位即报 PREWORK 错误**：寻位超时（60s）的失败原因统一为「**焊前寻位失败 PREWORK** …」并带上目标/实际/起始/累计位移/用时；`Fail()` ⇒ 运控 `ErrorAborted` ⇒ 整机报警停焊。⛔ 不得以「已在标定位」为由跳过寻位。
- **决策 D9 · Y 真动的前置（与 [[decisions/ADR-042-SeamTrackingConsolidated]] D5/D5b/D6 同源）**：⛔ **不得在建系后立即 `BufferStart`**（空缓冲先 Start ⇒ FIFO 进入已启动态 ⇒ 后续写段被拒 4610，现场实测证伪「提前激活坐标系表」假设）；正确时序 = **建系 → 写段（预载 2 段）→ Start**（台达手册 P9-146「先存指令方能执行」）。**先扫后跟**：X 未到焊前位前只扫图建库、不写段不驱轴；X 到位后才写段并启动 Y 跟随。建系前 `EnsureCspMode()` 显式确保轴在 CSP 模式。
- **决策 D10 · 寻位完成须用独立标志**：⛔ 不得用 `_calReturnReady`（它在回归标定位步就置位，早于寻位）判寻位完成——现场实测导致「寻位开始 0.147s 即报焊前阶段完成、提前发出焊接启动」。新增 `_preWorkSeekReady` / `IsPreWorkSeekReady`，主控 `CheckPreWorkCompleted` 与 `IsSubWorkGateOpen` 均改判此值。
- **决策 D11 · 寻位是会话态**：`ClearStatus()` 与 `ResetProcess()` 双清零 `_preWorkSeekStartTicks` / `_preWorkXArrived` / `_preWorkSeekReady` / `_preWorkSeekStartAxisPos`，否则真实循环第二轮沿用上一轮计时起点 ⇒ 一进寻位即超时。

## 备选方案

- **沿用固定标定位回归（不做寻位）**：Y 轴停在标定位起焊，首点不在焊点上 ⇒ 业主重做该环节的直接原因，弃。
- **起焊沿后再寻位**：与「焊接启动时 Y 第一个点就在焊点上」的目标矛盾，弃。
- **PreWork 阶段不移动 X、原地扫图**：X 不动则地图建不起（同 X 单点），Y 拿不到焊接点目标 ⇒ 无解，弃。
- **寻位失败仅告警不阻断**：起焊时 Y 不在焊点会撞偏 ⇒ 属 PreWork 失败，按业主口径报警停焊，弃。

## 后果

### 正面
- 起焊瞬间 Y 轴已在焊缝焊接点，首点即在焊点上，顺焊缝移动连续
- 寻位与焊接工作模式同机制（都是跟踪驱动），行为一致、判据可复用
- 模拟侧寻位起点可配置，模拟流程与真实流程结构对齐（机器人先到焊前位再起焊）

### 负面
- PreWork 时长增加（须等 X 到位且 Y 到位）；寻位超时 60s 即失败停焊
- 真实流程依赖机器人先移动到焊前位：机器人未动则地图建不起、Y 无目标 ⇒ 寻位超时失败
- `_calReturnReady` 语义由「标定位就绪」变为「寻位就绪」，其消费方（焊接启动门控 `IsSubWorkGateOpen`、焊缝 Y 记录开启）随之对齐

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-038-RobotCommandDrivenStepFlow]]（PreWork → Working 由指令驱动）
- [[decisions/ADR-042-SeamTrackingConsolidated]]（CSP 跟踪与坐标系统一）
- [[decisions/ADR-045-PredictiveRobotPoseSnapshot]]（位姿喂入与模拟时钟）
- [[api/MotionControlWorkflow]] · [[api/DeviceControlWork]] · [[api/SimulationConfig]]
- [[lessons/SimulationAutoBranching]]
