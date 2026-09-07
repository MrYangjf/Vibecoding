---
title: 模拟 C 模式进不到测试阶段（根因与修复）
date: 2026-08-25
tags: [教训, 模拟, 线激光, 工作流, 状态机]
source: AdaWeldSystem/Workflow/Device/LineLaserWorkflow.cs, AdaWeldSystem/UIDesign/TabPage/MotionControlPage.cs
---

# 模拟 C 模式进不到测试阶段（根因与修复）

> **类名注记（2026-09-02）**：文中的 `SimulationWorkflow` **已删除**，全部成员归并整机主控 `DeviceControlWork`（`IsEnabled`→`IsSimulationEnabled`、`Enable`→`EnableSimulation`、`Disable`→`DisableSimulation`）；`LaserCamBoxTrackingWorkflow` 已删除，现由 `MotionControlWorkflow` 承载；工作流 `State` 对外改由 `WeldStatus`（`SubDeviceWeldStatus`）承载。三条根因的排查思路继续有效。
>
> **枚举沿革注记（2026-09-03，ADR-030 裁定 C2）**：正文中的阶段名 `PreWork` / `Starting` / `Working` 属**旧取值**。`Starting` 已**删除**（不再作为独立阶段），并新增 `NoReset`(0) 置于 `Standby`(1) 之前。读取本页时请按新枚举理解；本页真正有效的是**三条根因的排查思路**（无人驱动状态机 / 虚拟相机空引用 / 清理时序错误），与具体枚举取值无关。
>
> ⛔ **原双流程决策已整页废弃并删除**（2026-09-03），本页 `SimulationWorkflow` 相关表述仅作历史记录，现行架构以 [[architecture/DeviceControlArchitecture]] 为唯一指导。

## 现象

模拟测试选 C 模式（真实相机+计算+记录）后，`MotionControlPage` 的模拟按钮变红「清理异常」，工作流进入 ErrorAborted，**进不到 PreWork/Starting/Working 测试阶段**。

## 根因（三个叠加）

### 1. InitializeWorker 读到 SmartRay 占位 → 初始化直接失败（P0）
`SimulationController.Enable(C)` 调 `CameraSelector.SelectReal()`（选中 **SmartRay** 占位），而 `LineLaserWorkflow.InitializeWorker` 在 `Start()` **之前**执行（Start 才 `SelectIntelligentLaser()`），此时 `CameraSelector.Active` 是 SmartRay → 走「其他相机类型」分支 → `ErrorAborted "线激光相机未正确选择/未连接，初始化失败"`。
**A/B 模式无此问题**：`Enable(A/B)` 选虚拟相机，InitializeWorker 走 `IsVirtual` 分支四步全 true。

### 2. 模拟流程无人驱动 PreWork→Starting→Working（P0）
`BeginStarting()`/`BeginWorking()` 只有 `MainDeviceThread.StartAllSubThreads()` 调用；模拟流程（`MotionControlPage`）只调 `LineLaserWorkflow.Start()` → **所有模拟模式（A/B/C）卡死在 PreWork**（`ExecutePreWork` 自旋 30s 超时后循环重进）。

### 3. 虚拟相机无回调 → Working 连续失败中断（P1）
虚拟相机（A/B）`_ilCamera == null`：`ExecuteStarting` 开头直接 return（数据永不稳定）；`ExecuteWorking` 中 `_lastResultValid` 恒 false → `HandleFailure` 累计 5 次 → ErrorAborted。

## 修复（2026-08-25 落地）

| 位置 | 改动 |
|------|------|
| `LineLaserWorkflow.InitializeWorker` | 开头：模拟 C 模式（`IsEnabled && !ShouldUseVirtualCamera`）时显式 `CameraSelector.SelectIntelligentLaser()`（与 `Start()` 相机选择一致） |
| `ExecutePreWork` | 完成后若 `SimulationWorkflow.Instance.IsEnabled` → 自驱动 `TryTransitionTo(Starting)`（生产模式仍等主设备 `BeginStarting`） |
| `ExecuteStarting` | 虚拟相机（`_ilCamera == null`）跳过开外设、`_dataStable = true` 默认通过；数据稳定后模拟模式自驱动 `TryTransitionTo(Working)` |
| `ExecuteWorking` | `_ilCamera == null`（虚拟相机模拟）时识别有效性默认通过，不累计失败 |

## 关联

- 模拟驱动：[[api/DeviceControlWork]]
- 工作流分步：[[modules/DeviceControl]] / [[decisions/ADR-024-LineLaserWorkflowRefactor]]
- 相机选择：[[api/CameraSelector]]（`SelectReal()` 选 SmartRay 占位、`SelectIntelligentLaser()` 选英莱）
- 主界面轮廓显示：[[modules/UIDesign]] MainPage（`AddContourLineChart()` 须在 FormMain 初始化时显式调用，订阅英莱相机 `ContourDataReady` 事件）

## 延伸：主界面轮廓未传导（2026-08-26）

### 现象
模拟C模式（真实英莱相机）运行中，线激光工作流正常，但主界面 `formsPlot1` 轮廓图始终空白。

### 根因
`MainPage.AddContourLineChart()` 方法（初始化 ScottPlot Signal 图 + 订阅英莱相机 `ContourDataReady`）定义完成但**从未被调用**。`FormMain` 只 `new MainPage()` 并加入 Tab，未触发图表初始化。

### 修复
`FormMain.LoadNavAndPages()` 中，mainPage 添加到 Tab 后显式调用：
```csharp
mainPage.AddContourLineChart();
mainPage.AddNewDataLineChart();
```

## 延伸：清理异常按钮不恢复 + 启动异常仅静默记录（2026-08-27）

### 现象
1. 模拟流程运行期异常终止（ErrorAborted）→ 按钮转红「清理异常」→ **点击清理异常后按钮无反应、未恢复默认态**（仍卡红/无变化）。
2. 点击「开启模拟流程」启动期间（预启动 `Reset` / `StartLineLaserWithPending` / V3跟踪 `Start` / 异步挂起 `Start`）若抛异常，仅 `GlobalCommData.ShowLog` 记录，**不弹窗**，用户无感知。

### 根因
1. `CleanupSimError()` 原实现把 `SetSimButtonMode(Start)`（按钮复位）写在 `try/catch` **之外**、且位于 `SimulationWorkflow.Instance.Disable()` 之后。`Reset()`/`Disable()` 在异常态下可能抛异常且不被该局部 catch 覆盖 → `SetSimButtonMode(Start)` 永不执行 → 按钮卡死。
2. 启动路径四处 catch 仅 `ShowLog`，无 UI 反馈。

### 修复（[[api/MotionControlPage]]）
1. `CleanupSimError()`：各后端调用拆为独立 `try/catch` 记录，**按钮复位 `SetSimButtonMode(Start)` 移入 `finally`** —— 无论后端是否抛异常，按钮必定恢复默认态。
2. `BtnStartSim_Click` 入口加兜底：`if (_simError || LineLaserWorkflow.Instance.State == LineAborted)` 任一成立即进清理分支，防异步 `BeginInvoke(ShowSimErrorButton)` 与点击事件竞争导致 `_simError` 错位。
3. 新增 `ShowSimErrorDialog(string)`：`ShowLog` + `AntdUI.Message.error` 弹窗，`InvokeRequired` 时 `BeginInvoke` 封送（后台线程安全，见 [[guides/WinForms-UI-Threading]]）；替换启动路径四处「仅 log」catch。

### 教训
- **按钮状态复位必须放在 `finally`**：凡「清理异常/复位界面」类操作，复位 UI 状态（text/Ghost/Type）切勿依赖后端调用成功，必须 `finally` 保证执行。
- **启动异常要给 UI 反馈**：模拟/流程启动路径的 catch 不应只 log，至少 `Message.error` 弹窗，否则用户误以为启动成功实则已失败。

## 延伸：停止反馈不清晰 + 重复日志 + 弹窗类型（2026-08-27）

### 现象（用户实测反馈）
点击「开始模拟测试」后日志为：`状态迁移 Idle 到 Stopping 原因 停止指令` / `状态迁移 Stopping 到 Idle 原因 已停止` / `V3 跟踪工作流已停止` / `模拟模式关闭` ×2。用户指出：① 底层「状态迁移」不是「确认信息」，停止原因应说清「什么设备态如何、什么流程怎么样」；② `模拟模式关闭` 重复记录；③ 异常时无红色「清理异常」按钮态、无弹窗。并明确两类弹窗约定：**无需确认用 `AntdUI.Message`，需确认用 `AntdUI.Modal`**。

### 根因
1. `SimulationController.Disable()` 非幂等：每次调用都记「模拟模式关闭」；停止分支 `StopSimulationFlows()` 在 `UnsubscribeLineLaserEvents()` **之前**执行，`LineLaserWorkflow.Stop()` 触发仍订阅的 `StateChanged` 异步回调二次进入停止路径 → `Disable()` 被调两次 → 重复日志。
2. 启动异常路径（`BtnStartSim_Click` 末尾无条件 `SetSimButtonMode(Stop)`）使按钮停在「停止」而非红色「清理异常」，与 ErrorAborted 路径不一致。
3. 原 `ShowSimErrorDialog` 用 `AntdUI.Message.error`（无需确认），与用户「需确认用 Modal」约定不符。

### 修复（[[api/MotionControlPage]] / [[api/DeviceControlWork]]）
1. `Disable()` 幂等化：仅当 `_currentMode != None`（开启→关闭）才记录并停止 robotX，已关闭直接 return → 重复日志消除。
2. 新增 `LogSimStopSummary(reason)`：汇总 `LineLaserWorkflow.State` / `LaserCamBoxTrackingWorkflow.State` / `MonitorCameraWorkflow.State` / `SimulationWorkflow` 模拟模式态，输出「人话」式停止原因，区别于底层「状态迁移」调试日志。
3. 新增 `ShowSimStopMessage(reason)`：正常停止（用户停止指令/焊缝完成/异常清理恢复）用 `AntdUI.Message.info` 弹窗（无需确认）。
4. `ShowSimErrorDialog` 由 `Message.error` 改为 `AntdUI.Modal.open(TType.Error)`（需确认）+ 按钮转红色「清理异常」（`ShowSimErrorButton`）；启动任一步骤异常经其置红，`BtnStartSim_Click` 以 `_simError` 短路后续启动步骤。
5. 停止分支先 `UnsubscribeLineLaserEvents()` 再 `StopSimulationFlows()`，避免异步回调二次进入；`CleanupSimError`/`StopSimOnWeldComplete`/停止分支均补 `ShowSimStopMessage`+`LogSimStopSummary`（置于 `finally`）。

### 教训
- **停止反馈分两层**：底层「状态迁移」调试日志保留，但业务层必须额外输出「人话」式停止确认（设备态+流程态+原因），且正常停止用 `Message`、异常用 `Modal`（需确认）按用户约定区分。
- **`Disable`/停流程类操作要幂等**：同一停止动作可能被多条路径触发，记录/动作须以状态变化为前置条件，避免重复日志与重复副作用。
- **异常路径按钮态必须统一**：凡异常（启动失败 / 运行期 ErrorAborted）一律经同一 `ShowSimErrorDialog` 将按钮转红色「清理异常」，启动路径末尾不得无条件置「停止」覆盖。
