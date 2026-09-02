---
title: Lesson - 故障恢复设备键名必须与策略注册 key 精确匹配
date: 2026-08-19
tags: [陷阱, Safety, 故障恢复, 状态机, 命名约定]
severity: critical
---

# Lesson - 故障恢复设备键名必须与策略注册 key 精确匹配

## 现象

`FaultRecoveryManager.RegisterRecoveryStrategy` 用英文 key（如 `"LineLaser"`、`"MotionControl"`）注册恢复策略，但故障记录时 `Device` 字段存的是中文设备名（如 `"线激光"`、`"运动控制"`），导致 `ResolveKey()` 用 `IndexOf` 子串匹配永远失败，**自动恢复策略注册了但永远不会被调用**。

## 根因

两层命名体系不一致：
- **策略注册层**：用英文设备 key（`LineLaser` / `MotionControl` / `Monitor` / `LaserWeldHead`）
- **故障记录层**：用 `IDeviceStateMachine.StateName`（中文显示名：`"线激光"` / `"运动控制"` / ...）

`ResolveKey` 做的是 `device.IndexOf(k)` 子串匹配——中文名里不可能包含英文字符串，匹配永远失败。

## 修复方案

`RecordFault` 新增 `deviceKey` 参数，调用方（如 `MainDeviceThread.SubscribeFault`）直接传入与策略注册一致的英文 `deviceKey`。`RecordFault` 内部优先用 `deviceKey` 精确匹配策略，找不到时再回退到按 `Device` 中文名解析（兼容旧调用）。

## 防范规则

1. **注册 key 和记录 key 必须同源**：策略注册和故障记录必须使用同一套命名体系，禁止一边用英文 key 一边用中文显示名。
2. **优先精确匹配，慎用模糊匹配**：`IndexOf` 子串匹配在多语言/多命名体系下极不可靠，应使用精确字典查找。
3. **新增 `RecordFault(deviceKey, record)` 重载**：新代码必须传 `deviceKey`，旧重载保留兼容但标注为不推荐。

## 相关文件

- `ProductFileManager/FaultRecoveryManager.cs` — `RecordFault` / `RegisterRecoveryStrategy` / `ResolveKey`（2026-09-01 自 `MainDeviceControl/DeviceWorkflow/` 迁入，ADR-046 §3；历史路径 `Workflow/` → `MainDeviceControl/DeviceWorkflow/` 均已失效）
- 消费方：`MainDeviceControl/` 下 6 处（`DeviceStatusWork`（安全互锁）/ `DeviceControlWork`（`"MainDevice"`）/ `LineLaserWorkflow` / `MonitorCameraWorkflow` / `MotionControlWorkflow` / `WeldParamControlWorkflow`）；历史载体 `MainDeviceThread.cs` → `MainDeviceWorkflow.cs` → `DeviceControlWork.cs`（ADR-049）

## 相关页面

- [[modules/Safety]] — Safety 模块文档
- [[modules/DeviceControl]] — 状态机模块
- [[architecture/DeviceControlArchitecture]] — 设备控制架构规范页（第 9 章 安全互锁与故障恢复）
