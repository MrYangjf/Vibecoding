---
title: SimulationWorkflow API 参考（已删除 · 墓碑）
date: 2026-07-20
tags: [API, 模拟, 工作流, 模式, 已删除, 墓碑]
source: （源文件已删除：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/SimulationWorkflow.cs）
---

# SimulationWorkflow API 参考（已删除 · 墓碑）

> **⛔ 本类已删除（2026-09-01，ADR-048）**：`SimulationWorkflow.cs` 已从代码库移除，csproj 同步注销。本页仅作历史追溯，**编码前不得引用**。

## 现行真相源

模拟模式全部成员现位于 **`DeviceControlWork`**（原 `MainDeviceWorkflow`，ADR-049 三态模型重构更名，直接挂主设备单例，不留兼容门面），API 更名对照：

| 旧 API（SimulationWorkflow.Instance） | 新 API（DeviceControlWork.Instance） |
|---|---|
| `IsEnabled` | `IsSimulationEnabled` |
| `Enable(mode)` | `EnableSimulation(mode)` |
| `Disable()` | `DisableSimulation()` |
| `Load()` | `LoadSimulation()` |
| `Save()` | `SaveSimulation()` |
| `GetEffectiveRobotX()` / `StartRobotXSimulation()` / `StopRobotXSimulation()` / 9 个属性 | 同名保留于 `DeviceControlWork` |
| `SimTestMode` 枚举 | 迁至 `DeviceControlWork.cs` 文件尾 |

消费方替换已完成：`MotionControlPage.cs`（9 处）、`FormMain.cs`（`LoadSimulation()`）。

## 设计理念（继续有效）

「模拟是 **MODE** 不是独立线程」——开启后三大流程（线激光/运控/监控）照常打开但使用模拟数据，该精神由 [[decisions/ADR-017-SimulationModeThroughThreeWorkflows]] 确立、[[decisions/ADR-048-AutoManualDualWorkflow]] §4 继承。

## 历史

- 2026-07-20：ADR-017 引入，原 `MotionControlWorkflow` 内独立模拟线程移除。
- 2026-08-28：自 `Workflow/Device/` 迁入 `MainDeviceControl/DeviceWorkflow/` 并更名（原 SimulationController）。
- 2026-09-01：**删除归并**至 `MainDeviceWorkflow`（[[decisions/ADR-048-AutoManualDualWorkflow]]）。
