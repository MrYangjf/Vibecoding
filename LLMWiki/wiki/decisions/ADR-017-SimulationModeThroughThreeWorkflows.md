---
title: ADR-017 模拟模式贯穿三大流程（取代独立模拟线程）
date: 2026-07-20
tags: [决策, 模拟, 工作流, 架构纠正]
status: accepted
---

# ADR-017：模拟模式贯穿三大流程（取代独立模拟线程）

> **⚠️ 部分取代（2026-09-01，ADR-048；2026-09-02，ADR-049）**：本文的**核心理念「模拟是 MODE 不是线程」继续有效**；但「独立 `SimulationWorkflow` 文件承载」的形态已被取代——`SimulationWorkflow.cs` 已删除，全部成员归并**整机主控 `DeviceControlWork`**（API 更名 `*Simulation`），对外直接挂主设备单例。现行真相源见 [[decisions/ADR-048-AutoManualDualWorkflow]] §4 与 [[api/DeviceControlWork]]。
>
> **类名注记**：文中 `MainDeviceWorkflow` 现为 `DeviceControlWork`；`Workflow/` 目录、`DeviceStateMachine/` 目录均已删除。

## 背景

原有 `MotionControlWorkflow` 内实现了一条独立模拟线程（`SimulationLoop` + `StartSimulation`/`StopSimulation`），它自行选相机、自行取图（`AcquireAndAnalyze`）、自行算机器人X（`SimStartX + SimSpeed × elapsed`）、自行调用 `PipelineManager.Execute` 做分析——等于在**运控模块里重造了一条线激光流程**，与 `LineLaserWorkflow` 完全重复。

用户明确指出：模拟测试**不应单独做一个线程来模拟**，而应在原有的工作流程中「判断为模拟测试后执行模拟数据」。开启模拟后，正常的三套流程都应打开：
1. **线激光流程**：判断相机/相机类型/机器人坐标均为模拟数据，保证数据流跑通（虚拟相机初始化 → 模拟线激光采集轮廓与输出 → 线激光分析 → 执行调整）；
2. **运控流程**：根据线激光流程给出的信号和模拟模式切换不同输出；
3. **监控流程**：判断为模拟流程时选择不工作。

## 决策

引入 `SimulationWorkflow`（单例，`Workflow/SimulationWorkflow.cs`）作为贯穿三大流程的「模拟模式」**唯一真相源**：
- 持有模拟模式（A/B/C：None=关闭）、模拟参数（起点/速度/目标距离/轮廓/随机）、以及共享模拟 robotX（`SimStartX + SimSpeed × elapsed`）。
- 提供 `Enable(mode)`/`Disable()`/`GetEffectiveRobotX()`/`IsEnabled`/`ShouldUseVirtualCamera`/`ShouldMoveAxis`。
- 移除 `MotionControlWorkflow` 内的独立模拟线程，改为：
  - **LineLaserWorkflow**：`Start()` 按 `ShouldUseVirtualCamera` 选相机；`GetCurrentRobotX()` 在 `IsEnabled` 时返共享模拟 robotX；`Initialize()` 对虚拟相机同步转 Standby（便于一键开启）。
  - **MotionControlWorkflow**：仅保留水平移动后台线程（读 `GetEffectiveRobotX()`）+ 订阅 `PipelineManager.AlgorithmCompleted` 缓存水平移动；按 `ShouldMoveAxis`（B 运动、A/C 仅记录）切换输出。
  - **MonitorCameraWorkflow（含 MonitorSupervision 健康巡检功能）**：`IsEnabled` 时返回「模拟模式不工作」。
- UI：`MotionControlPage`「开启模拟流程」按钮一键联动——`Enable` 后启动 LineLaserWorkflow + 水平移动 + MonitorCameraWorkflow（含 MonitorSupervision 健康巡检功能）；关闭时反向停止三套。

## 备选方案

- **保留 MotionControlWorkflow 内独立模拟线程**：被否决。重复线激光流水线、模拟数据不与其他流程共享、监控流程无法感知模拟态。
- **将共享模拟状态置于 MotionControlWorkflow**：被否决（仅作备选）。会造成 LineLaser/Monitor 反向依赖 MotionControl，耦合更紧；独立 `SimulationWorkflow` 解耦最干净。

## 后果

### 正面
- 模拟数据在三大流程间真正共享（同一份 robotX、同一套 A/B/C 语义），数据流可端到端跑通。
- 消除运控内重复的取图/分析逻辑，单一算法真源（[[api/MoveControlData]] + [[modules/EmguALG]]）。
- 监控流程能正确感知模拟态并「选择不工作」，符合用户预期。

### 负面
- 新增一个 `.cs`（`SimulationWorkflow`），需注册 csproj（遵循 [[guides/Namespace-Compilation]]）。
- `SimTestMode` 枚举语义从「运控内部模式」升格为「全局模拟模式」，需在文档中明确归属。

## 相关页面

- [[modules/DeviceControl]] / [[modules/MotionControl]] / [[modules/MonitorCam]]
- [[api/DeviceControlWork]] / [[architecture/DeviceControlArchitecture]]
- [[decisions/ADR-015-WorkflowAsHub]]（Workflow 作为流程管理中枢）
- [[decisions/ADR-011-MonitorCameraModule]]
