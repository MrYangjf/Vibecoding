---
title: ADR-081 初始化完成后按配置统一使能轴
date: 2026-11-04
updated: 2026-11-04
tags: [决策]
status: accepted
---

# ADR-081 初始化完成后按配置统一使能轴

> **决策一句话**：初始化完成（子设备就绪）后，按配置对所有 `ENABLED=true` 轴执行**一次**统一使能，逐轴留痕，失败即初始化判为未完成。

## 背景

启动装载轴并完成初始化后，TA 轴未使能（驱动器未 OperationEnabled），只有点 `TA_Auto` 时才在内部补一次 `ServoOn`。取证结论：

- `MontionManager.Initialization()` 只调 `CreateAxesFromConfig()` 建轴，**不使能**；
- `MontionManager.ServoOnAll()` 全项目**零调用方**（死公共 API）；
- `DeviceControlWork.DoResetMachine()` / `CascadeResetProcess()` 链路内无 `ServoOn`；
- Y 轴等其他轴同样不自动使能 ⇒ **属全局设计缺口，不是 TA 独有**。

原设计并无明文「初始化后自动使能」策略，也没有「等操作员确认再使能」的显式守卫——只是缺这一步。

## 决策

1. 初始化完成（`EvaluateInitializationResult()` 为 true，即子设备全部 Connected）后，对轴注册表（仅含 `ENABLED=true` 轴，`CreateAxesFromConfig` 已筛除禁用轴）执行**一次**统一使能。
2. 逐轴留痕：`轴名 + 结果 + 失败原因`；失败原因取自 `MontionAxis.LastCommand`（急停 / 总线未 OP / 报警未清 / `Set_Svon(1)` 超时）。
3. 任一轴使能失败 ⇒ `InitializationCompleted` 收到 `false`，⛔ 不把流程判为成功；不重试、不改写轴状态。
4. `TA_Auto` 内部的 `SingleServoOn` 兜底保留，但**不再是唯一使能入口**。
5. ⛔ 不做定时轮询重新使能（不用轮询掩盖失败）。

## 安全策略说明（变更前 → 变更后）

| 项 | 变更前 | 变更后 |
|---|---|---|
| 初始化后轴状态 | 全部未使能，等指令入口临时补 | 全部 `ENABLED=true` 轴统一使能，逐轴日志 |
| 安全门 | `DeltaMontionAxis.PreMotionCheck` 拦截急停 / 非 OP / 报警 | **不变**（同一道门，使能前先过） |
| 失败可见性 | 仅在 `TA_Auto` 时报错 | 初始化阶段即报错并判初始化未完成 |

> ⚠️ 这是在原设计缺口上**新增**的行为，非既有安全策略的收窄；急停/报警/总线未 OP 一律使能失败，不会被绕过。

## 实现落点

| 内容 | 文件 | 要点 |
|---|---|---|
| 统一使能 | `MotionControl/MontionManager.cs` `EnableAxesAfterInit()` | 前置 `IsInitialized && MontionControl != null`；`IsServoOn()` 已使能则跳过；否则 `ServoOn()` 后复核；`failCount == 0` 才返回 true |
| 调用点 | `MainDeviceControl/DeviceControlWork.cs` `InitStepEvaluate` | `allReady && EnableAxesAfterInit()` → `InitializationCompleted?.Invoke(allReady && servoReady)` |
| 日志关键字 | 同上 | `初始化使能 <轴名> 成功` / `初始化使能 <轴名> 失败 原因 <LastCommand>` / `初始化使能完成 成功 N 轴 失败 M 轴` |

## 备选方案

- **A. 保持现状（只在指令入口补使能）**：否决——每加一个指令入口就要补一次，漏一处即「轴没使能」；现场表现具有迷惑性（点 `TA_Auto` 才发现）。
- **B. 定时轮询重新使能**：否决——会把真实失败（急停 / 报警 / 总线掉线）掩盖成「过一会儿自己好了」。
- **C. 初始化后仅使能 TA 轴**：否决——Y 轴同样缺口，只修 TA 会造成「Y 能动、TA 不动」的新不对称。

## 后果

### 正面

- 启动后所有启用轴即为 OperationEnabled，手动/自动指令不再依赖入口补使能。
- 使能失败在初始化阶段暴露，日志可直接定位到具体轴与原因。

### 负面

- 初始化完成后驱动器处于使能态（原为失能态），**现场上电即出力**风险前移：须确认机械无障碍、无明显外力后再执行初始化。
- 使能失败会阻断「初始化成功」，现场需先清报警/急停再重试。

## 相关页面

- [[decisions/ADR-Index]]
- [[api/MontionManager]] · [[api/DeviceControlWork]]
- [[lessons/ConfigZoneSaveWiring]] 坑 3（初始化不主动使能同类缺口）
- [[decisions/ADR-041-ResidentFlowNonBlockingParadigm]]（初始化链步驱动范式）
