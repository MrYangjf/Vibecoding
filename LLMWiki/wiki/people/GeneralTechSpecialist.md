---
title: 通用技术开发专员
date: 2026-07-01
tags: [专员, 通用技术, 通讯, 状态机]
source: raw/skills/AdaWeldsys_Skills/02-Development/GeneralTechSpecialist.md
---

# 通用技术开发专员

## 职责边界

- 文件操作工具（INI/XML/日志）
- 统一设备通讯（TCP/IP / S7 / Profinet，统一职责模型）
- 设备错误码体系（DeviceErrorCode 固定编码）
- 全局事件总线与消息/权限枚举定义（`MessageType`、`MessageLevel`、`OperateLevel`）
- 三态枚举 `SubDeviceState` / `SubDeviceWeldStatus` / `MainDeviceStatus` 与配套事件参数定义（文件 `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs`，状态写入唯一入口 `SetState`/`SetWeldStatus`/`SetStatus`，见 [[modules/DeviceControl]]）
- 程序入口与全局配置

## 负责文件

Comm/
├── SystemComm.cs              ← 全局通讯/状态/事件定义中心（GlobalCommData + 枚举/事件参数）
├── CommunicationManager.cs    ← 通讯持久化配置与通用 TCP 实例管理
├── Ethernet/TCPIPComm.cs      ← 通用 TCP 服务端/客户端   （已移除 2026-09-14，现役 Comm/Communication/Implementations/EthernetXmlComm.cs，ADR-011）
├── SiemensS7Comm.cs
├── ProfinetComm.cs
├── DeviceErrorCode.cs
├── Program.cs
└── App.config

FileOperate/
├── INIFile.cs
├── LogManager.cs
└── XMLSerializer.cs

## WorkflowState 有效状态转换矩阵

Idle        → Running, Resetting
Running     → Paused, ErrorStopped, Completed, Stop(→Idle)
Paused      → Running(恢复), Stop(→Idle), Resetting
Resetting   → Idle（复位完成）
ErrorStopped→ Resetting, Idle（手动清除错误后）
Completed   → Idle, Resetting

## 统一通讯职责模型

所有通讯通道统一承担两类职责：
- 工作流程控制指令（下行）：Start / Stop / Pause / Reset
- 设备运行状态反馈（上行）：状态上报 / 异常错误上报

---

*来源：raw/skills/AdaWeldsys_Skills/02-Development/GeneralTechSpecialist.md*
