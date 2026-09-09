---
title: ADR-035 报错分层与状态切换零日志
date: 2026-09-04
tags: [决策, 日志, 报错, 分层]
status: accepted
---

# ADR-035 报错分层与状态切换零日志

## 背景

2026-09-04 启动日志中同一错误被记录 3~4 次（如控制器连接失败：`ZMotionController 连接失败` → `MotionManager 初始化失败` → `运控初始化连接失败`×2 → `主设备 运动控制器初始化未通过`），且 `SetStatus` / `SetState` / `SetWeldStatus` / 三色灯反射每次状态迁移都打 Info 日志，淹没有效信息。

## 决议（用户 2026-09-04 裁定）

### D1 报错三层归口（同一错误只由归口层记录一次）

| 层 | 归口范围 | 示例 |
|---|---|---|
| **设备对象层**（Controller / Run / Manager） | 硬件与连接错误——连接不上、握手失败、采集异常 | `连接失败 错误码 20008` |
| **工作流层**（5 个 Workflow） | 流程错误——PreWork 失败、复位失败、流程异常终止 | `运控流程异常终止 原因 X` |
| **主设备层**（DeviceControlWork / DeviceStatusWork） | 设备级流程聚合——初始化失败 N 个子设备未连接、复位阻断、急停 | `子设备初始化失败 存在 2 个子设备未连接` |

上层收到下层已报的错误时**不得复述**，只做状态推进与聚合计数。

### D2 状态切换零日志

以下日志全部移除（事件保留，供 UI 订阅呈现）：
- 主设备 `运行态切换 X -> Y`
- 子设备 `连接态切换 X -> Y` / `焊接过程态切换 X -> Y`
- 三色灯 `状态反射 X`

状态对外呈现途径：状态栏、三色灯动作、UI 订阅事件。

### D3 重复报错触发面清理

- 删除主设备层对子设备已报错误的逐条复述（如 `运动控制器初始化未通过`）。
- 焊接头/运控初始化失败不再误置 Connected（ADR-031 D2-4）。
- 故障恢复模块（FaultRecoveryManager / FaultRecordManager）整体移除——架构无此定义（用户裁定），RecordFault 调用面全部删除。

## 相关

- [[decisions/ADR-030-MainDeviceStateSemantics]]（状态机语义）
- [[standards/CodeSimplification]]（注释与日志规范）
