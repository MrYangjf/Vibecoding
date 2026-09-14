---
title: ADR-004 Comm 模块重构决策
date: 2026-07-02
tags: [决策, 通讯, 状态管理, 重构]
status: accepted
---

> ⚠️ 历史名称提示：本页为**历史决策记录**，正文中的下列文件名为决策当时的旧名，
> 保留原文以留存上下文，现役对应如下：
>
> - `GlobalCommData.cs` → 现役 `Comm/SystemComm/SystemComm.cs`
> - `SystemStatus.cs` → 已移除（已并入 Comm/SystemComm/SystemComm.cs）
>
> **沿革横幅（2026-09-14）**：本页裁定的 Comm 结构（`CommBase/` / `PLC/` / `Robot/KUKARobot/` 平铺 + KUKARobotManager 门面）**已被 [[decisions/ADR-045-CommModuleRefactor]] 整体取代**（抽象层 + 实现层 + Manager；KUKARobotManager/TCPIPComm/GSDMLGenerator 删除、Profinet 封装不做）。状态管理结论由三态模型承接（ADR-027）。

# ADR-004 Comm 模块重构决策

## 背景

随着线激光工作流状态机 `LineLaserWorkflowState` 的引入，原 `GlobalCommData` 中的 `MachineStatus` 状态管理逐渐闲置，造成状态分散（`GlobalCommData.CurrentStatus` 与 `LineLaserWorkflow.State` 并存）。

同时，`SystemStatus.cs` 仅存放枚举/事件参数类，`GlobalCommData.cs` 存放全局通讯数据中心，两者高度相关却分属两个文件，维护成本较高。通用 TCP 实例 `TCPIPComm` 原由 `GlobalCommData` 直接持有，但其配置实际来自 `CommunicationManager` 的 XML 结构，存在职责错位。

## 决策

1. **合并文件**：将 `GlobalCommData.cs` 与 `SystemStatus.cs` 合并为单一文件 `Comm/SystemComm.cs`，统一存放全局通讯类、消息/权限/工作流枚举、事件参数类。
2. **移除废弃状态管理**：删除 `MachineStatus` 枚举、`MachineStatusMessageArgs`、`EventStatusHandler`、`CurrentStatus`、`LastStatus`。系统状态统一由 [[modules/DeviceControl]] 的 `LineLaserWorkflowState` 管理。
3. **TCPIPComm 纳入 CommunicationManager**：`TcpIpComm` 实例由 `CommunicationManager` 在构造函数中创建并持有，访问路径统一为 `GlobalCommData.mCommunicationManager.TcpIpComm`。
4. **避免循环依赖**：`TcpIpComm` 构造函数接收 `CommunicationManager` 引用，直接使用该引用读取 XML 配置，不再依赖 `GlobalCommData.mCommunicationManager` 静态字段。

## 后果

### 正面

- 状态单一来源：UI 统一订阅 `LineLaserWorkflow.Instance.StateChanged`，避免状态不一致。
- 职责清晰：`CommunicationManager` 负责通讯配置与通用 TCP 实例生命周期；`GlobalCommData` 负责事件总线与日志。
- 文件数量减少，相关定义集中，便于查找和维护。

### 负面

- `CommunicationManager` 与 `TcpIpComm` 形成循环引用（持有彼此），但在同一线程生命周期内无释放风险。
- `FormMain` 等 UI 代码需要从 `GlobalCommData.EventStatusHandler` 迁移到 `LineLaserWorkflow.StateChanged`。

## 相关页面

- [[modules/Comm]]
- [[api/GlobalCommData]]
- [[api/LineLaserWorkflow]]
- [[modules/DeviceControl]]
