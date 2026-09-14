---
title: ADR-006 通讯 XML 配置按设备类型分离
date: 2026-07-03
tags: [决策, 通讯, XML, 配置管理]
status: accepted
---

# ADR-006 通讯 XML 配置按设备类型分离

> 状态：已采纳
> 日期：2026-07-03
>
> **沿革横幅（2026-09-14）**：XML 按设备类型分离的**结论仍有效**（8 个 XML 配置由 `CommunicationManager` 持有）；但承载者已随 [[decisions/ADR-045-CommModuleRefactor]] 迁移——`CommunicationManager.cs` 现位于 `Comm/Communication/`，机器人 XML 消费方 `CommRobotPage` 现为 `CommPage`。

## 背景

在 [[decisions/ADR-004-CommRefactor]] 重构后，`CommunicationManager` 持有 4 个通用 TCP XML 配置（Server/Client/Send/Recive）。但机器人通讯页面（`CommRobotPage`）和 PLC 通讯页面（`CommPLCPage`）没有独立的 XML 配置：

- `CommRobotPage` **错误地复用** `ServerXdoc` 读取机器人 IP/Port，导致通用 TCP 与机器人配置耦合
- `CommPLCPage` **完全没有 XML 持久化**，使用硬编码默认值（`192.168.0.1` / `0` / `1`）
- 三个通讯页面的日志显示开关只有一个 `ShowCommLog`，无法独立控制各设备类型的日志

## 决策

在 `CommunicationManager` 中按设备类型分离 XML 配置：

### 新增 XML 配置

| XML 文件 | 字段名 | 用途 | 节点结构 |
|----------|--------|------|----------|
| RobotServer.xml | `RobotServerXdoc` | 机器人通讯服务端配置（RSI UDP / EKI Server） | `<Root><IP><PORT></Root>` |
| RobotClient.xml | `RobotClientXdoc` | 机器人 EKI 客户端配置 | `<Root><IP><PORT></Root>` |
| PLC.xml | `PlcXdoc` | PLC 通讯配置 | `<Root><IP><PORT><Rack><Slot></Root>` |

### 新增 INI 持久化开关

| 属性 | INI Key | 用途 |
|------|---------|------|
| `ShowRobotCommLog` | `ShowRobotCommLog` | 机器人通讯日志显示开关 |
| `ShowPlcCommLog` | `ShowPlcCommLog` | PLC 通讯日志显示开关 |

### 初始化保障

新增 `EnsureElementExists()` 辅助方法，在 `InitializeXmlDocuments()` 中对新 XML 调用，确保节点存在后才可供页面读取。

## 页面改造

| 页面 | 改动 |
|------|------|
| CommGeneralPage | 新增"保存配置"按钮；订阅 `EventInfoHandler` 事件；`SaveConfig()` 写回 ServerXdoc/ClientXdoc |
| CommRobotPage | 改用 `RobotServerXdoc`（不再复用 `ServerXdoc`）；新增"保存配置"按钮 + `chkShowCommLog`；订阅事件 |
| CommPLCPage | 改用 `PlcXdoc`（不再硬编码）；新增"保存配置"按钮 + `chkShowCommLog`；订阅事件 |

## 约束

- 三个页面均使用 `DisposeComponents()` 取消订阅 `EventInfoHandler`（遵循 [[decisions/ADR-001-DisposePattern]]）
- 事件处理使用 `InvokeRequired` 保证线程安全（遵循 [[guides/WinForms-UI-Threading]]）
- `SetElementValue` 仅在元素已存在时更新值，因此 `EnsureElementExists` 必须在初始化时调用

## 相关

- [[decisions/ADR-004-CommRefactor]] —— Comm 模块重构基础
- [[modules/Comm]] —— 通讯模块架构
- [[api/GlobalCommData]] —— GlobalCommData API（含 XML 字段说明）
- [[decisions/ADR-001-DisposePattern]] —— Dispose 模式约束
