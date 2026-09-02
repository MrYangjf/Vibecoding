---
title: Comm 模块 — 通讯与全局状态
date: 2026-08-03
updated: 2026-08-07
tags: [模块, 通讯, 全局状态, TCP/IP, S7, Profinet, CommBase, 状态机]
source: raw/skills/02-Development/GeneralTechSpecialist.md
---

# Comm 模块 — 通讯与全局状态

> 全局数据通讯中心、统一设备通讯（TCP/IP/S7/Profinet）、系统状态定义、程序入口。
>
> **通讯优先级策略：** 机器人通讯为默认主通道，PLC 通讯为备用通道。系统运行时优先通过机器人通讯（KUKA RSI/EKI）获取位置信息与控制工艺参数；当机器人通讯不可用时，自动切换至 PLC 通讯（S7/Profinet）作为降级通道。

## 目录结构

```
Comm/
├── CommBase/                          ← 通讯实现基座（TCP/Modbus/S7/Profinet 统一归属）
│   ├── Ethernet/
│   │   └── TCPIPComm.cs               ← 通用 TCP/IP 通讯
│   ├── Modbus/
│   │   └── ModbusTCPCommunication.cs  ← Modbus TCP 主站（FC03/FC06/FC16）
│   ├── Profinet/
│   │   └── GSDMLGenerator.cs          ← Profinet GSDML 生成器
├── PLC/
│   └── Siemens/
│       └── S7PLCCommunication.cs      ← 西门子 S7 通讯
├── IntelligentLaserModbus/            ← 英莱相机 Modbus 数据模型
│   └── ILModbusData.cs                ← 英莱相机寄存器映射与数据转换
├── Robot/
│   └── KUKARobot/                     ← KUKA 机器人通讯（RSI/EKI）
│       ├── KUKARobotManager.cs
│       ├── RSICommunication.cs
│       ├── EKICommunication.cs
│       ├── KUKAXMLConfig.cs
│       └── KUKADataTypes.cs
├── CommunicationManager.cs            ← 通讯配置管理（含 Modbus）
└── SystemComm.cs                      ← 全局通讯/状态/事件定义
```

> **2026-08-07 目录结构修正**：实际代码使用 `CommBase/` 作为通讯实现基座（统一承载 TCP/Modbus/S7/Profinet），而非 Wiki 原描述的 `NetworkPort/` 四层结构。`INetworkPort.cs` 和 `NetworkPortBase.cs` 两个抽象接口/基类文件当前不存在于代码中（该规划已取消，见下文）。英莱 Modbus 的协议实现在 `CommBase/Modbus/`，数据模型在 `IntelligentLaserModbus/`。KUKA 机器人通讯位于 `Robot/KUKARobot/`（无 NetworkPort 前缀）。

| 子目录 | 命名空间 |
|--------|---------|
| `CommBase/Ethernet/` | `AdaWeldSystem.Comm.CommBase.Ethernet` |
| `CommBase/Modbus/` | `AdaWeldSystem.Comm.CommBase.Modbus` |
| `CommBase/Profinet/` | `AdaWeldSystem.Comm.CommBase.Profinet` |
| `PLC/Siemens/` | `AdaWeldSystem.Comm.PLC.Siemens` |
| `IntelligentLaserModbus/` | `AdaWeldSystem.Comm.IntelligentLaserModbus` |
| `Robot/KUKARobot/` | `AdaWeldSystem.Comm.Robot.KUKARobot` |
| `Comm/`（根目录） | `AdaWeldSystem.Comm` |

## 核心文件

| 文件 | 职责 |
|------|------|
| `CommBase/Ethernet/TCPIPComm.cs` | 通用 TCP/IP 通讯客户端/服务器，基于 `STTech.BytesIO.Tcp`，由 `CommunicationManager` 实例化并管理 |
| `CommBase/Profinet/GSDMLGenerator.cs` | Profinet GSDML 文件生成器 |
| `PLC/Siemens/S7PLCCommunication.cs` | 西门子 S7 通讯封装（备用通道，基于 S7NetPlus），独立实现 |
| `CommBase/Modbus/ModbusTCPCommunication.cs` | Modbus TCP 主站通讯，自实现 MBAP+PDU 协议（FC03/FC06/FC16），独立实现 |
| **`IntelligentLaserModbus/ILModbusData.cs`** | **英莱相机 Modbus 寄存器映射**，地址 0x00~0x28，含数据转换与检测结果模型 |
| **`Robot/KUKARobot/`** | **KUKA 机器人通讯子模块（默认主通道）** — RSI/EKI，详见 [[modules/KUKARobot]] |
| `Robot/KUKARobot/KUKARobotManager.cs` | **KUKA 机器人通讯管理器（直接暴露）**：管理 RSI/EKI 两个通讯通道 |
| CommunicationManager.cs | 通讯对象持久化配置管理（机器人(默认)/PLC(备用)/Modbus/通用 TCP），直接暴露 `KUKARobotManager`、`S7PLCCommunication` 和 `ModbusTCPCommunication` 实例。管理 8 个 XML 配置（Server/Client/Send/Recive + RobotServer/RobotClient + PLC + Modbus）。**实现 `IDisposable`，`Dispose()` 依次释放 TcpIpComm/RobotManager/PlcManager/ModbusManager（2026-08-19）** |
| SystemComm.cs | 全局通讯/状态/事件定义中心。包含 `GlobalCommData` 静态类、消息/工作流/权限枚举、事件参数类。旧版残留 `TcpMessageLevel` 枚举已清除（2026-08-01）。**2026-08-13 新增 `GlobalCommData.UIConfigSetting()`** 集中管理 AntdUI.Config（主题+文本渲染）一次性加载，原 Program.cs/FormMain 分散配置统一迁入 |
| Program.cs | 程序入口 |
| App.config | 应用配置 |

### 2026-08-19 资源释放入口（ADR-001 非 UI 类标准）

> 遵循 ADR-001：**非 UI 类不使用 `DisposeComponents()`，统一实现标准 `IDisposable.Dispose()`**；`DisposeComponents()` 仅限 UI 设计器类使用。

| 类 | 释放入口 | 释放内容 |
|----|---------|---------|
| `CommunicationManager` | `IDisposable.Dispose()` | TcpIpComm / RobotManager / PlcManager / ModbusManager |
| `TcpIpComm` | `IDisposable.Dispose()` | SstTcpServer / SstTcpClient |
| `SstTcpServer` | `IDisposable.Dispose()` | 底层 TcpServer（StopAsync + Dispose） |
| `SstTcpClient` | `IDisposable.Dispose()` | 底层 TcpClient（Disconnect + Dispose） |
| `KUKARobotManager` | `IDisposable.Dispose()` | RSI / EKI 通讯实例（先退订事件再 Dispose） |
| `RSICommunication` | `IDisposable.Dispose()` | 接收线程 Join/Abort + UdpClient |
| `EKICommunication` | `IDisposable.Dispose()` | 接收线程 Join/Abort + NetworkStream + TcpClient |
| `S7PLCCommunication` | `IDisposable.Dispose()` | PLC 连接（Disconnect → _plc.Close） |
| `ModbusTCPCommunication` | `IDisposable.Dispose()` | 关闭 NetworkStream + TcpClient |

**释放调用链**：`FormMain_FormClosed` → `MainDeviceThread.Instance.Dispose()` → 停止子线程 + 关闭机器人连接 + Shutdown 焊接头 + `GlobalCommData.mCommunicationManager.Dispose()`（2026-08-19 级联补全）。

### 2026-08-03 重构要点

- **删除 `RobotCommunicationManager.cs`**：每个机器人通讯实现不同，无法统一管理。KUKA 机器人通讯直接由 `KUKARobotManager` 管理，`CommunicationManager.RobotManager` 直接暴露。
- **删除 `PLCCommunicationManager.cs`**：同理，PLC 各家不同。西门子 S7 直接由 `S7PLCCommunication` 实现，`CommunicationManager.PlcManager` 直接暴露。
- **目录调整**：`KUKARobot/` → `Robot/KUKARobot/`；`SiemensS7/` → `PLC/Siemens/`；`Profinet/` → `CommBase/Profinet/`。

## 已取消的规划（勿再当作待办）

以下两项曾列入规划，**代码中不存在对应文件，且当前架构不再需要**，仅作澄清以免误读为遗留任务：

| 规划项 | 原设想 | 现状 |
|--------|--------|------|
| `NetworkPort` 统一抽象层（`INetworkPort` / `NetworkPortBase`） | 统一 TCP/Profinet 通讯实现，提供 `Open/Close/Send/SendString` + 4 事件 + 接收线程模板 | **未实装且已取消**。实际以 `CommBase/` 为通讯实现基座，`KUKARobotManager` / `TCPIPComm` 为独立实现，不继承统一基类 |
| `RobotConnectionStateMachine`（机器人连接状态机） | 独立于工作流管理机器人连接生命周期（Offline/Online/Working/Error） | **未实装且已取消**。机器人/PLC 连接属外部设备通讯，统一由 `CommunicationManager` 管控；设备连接态收敛为四态 `Disconnect`/`Connect`/`Work`/`Alarm`，由 `DeviceStateBase` 承载（[[architecture/DeviceControlArchitecture]]） |

## 外部依赖

| 包 | 用途 | 添加方式 |
|----|------|---------|
| S7NetPlus | 西门子 S7 通讯 | NuGet: `Install-Package S7NetPlus` 或 `dotnet add package S7NetPlus` |
| STTech.BytesIO.Tcp | 通用 TCP/IP 通讯 | NuGet: `Install-Package STTech.BytesIO.Tcp` |

## 统一设备通讯职责模型

| 职责类别 | 操作 |
|----------|------|
| 工作流程控制指令（下行） | Start / Stop / Pause / Reset |
| 设备运行状态反馈（上行） | 状态上报 / 异常错误上报 |
| 通讯指令广播 | BroadcastCommunicationCommand → Workflow 接收并记录日志 |
| 通讯配置持久化 | CommunicationManager.Load/Save/AddOrUpdate |
| 通讯 XML 结构管理 | CommunicationManager 管理 8 个 XML：Server/Client/Send/Recive（通用 TCP）+ RobotServer/RobotClient（机器人）+ PLC + Modbus |
| 通用 TCP 通讯实例 | CommunicationManager.TcpIpComm（Server/Client） |
| 通讯日志显示开关 | CommunicationManager.ShowCommLog / ShowRobotCommLog / ShowPlcCommLog / ShowModbusCommLog（INI 持久化，各通讯页面 checkbox 控制） |
| 通讯启用开关 | CommunicationManager.IsRobotEnabled / IsPlcEnabled / IsGeneralEnabled（INI 持久化，`CommunicationSettings.ini` [Display] 段；开机初始化时先判启用状态，未启用则跳过对应通道初始化） |
| 机器人通讯模式 | CommunicationManager.RobotCommMode（`RobotCommModeType` 枚举：RSI=0/EKI=1，INI 持久化；RSI 与 EKI 二选一，启动与重连均只使用选定模式） |
| **机器人通讯（默认主通道）** | KUKA RSI/EKI（见 [[modules/KUKARobot]]）— 获取机器人位置信息与控制工艺参数，由 `CommunicationManager.RobotManager` 直接暴露 |
| **PLC 通讯（备用通道）** | S7PLCCommunication（S7NetPlus）— 机器人通讯不可用时自动降级，由 `CommunicationManager.PlcManager` 直接暴露 |
| **Modbus 通讯** | ModbusTCPCommunication（自实现 Modbus TCP 协议）— 英莱相机等 Modbus 设备通讯，由 `CommunicationManager.ModbusManager` 直接暴露 |
| **网络端口统一接口（未实装）** | `INetworkPort` / `NetworkPortBase` — 统一 TCP/UDP 通讯生命周期的规划接口，当前未实装 |
| Profinet 描述 | GSDMLGenerator.Generate |

## 相关文档

- [[modules/DeviceControl]] — 设备控制模块（机器人/PLC 连接由 `CommunicationManager` 管控，工作流只做信号交互）
- [[architecture/DeviceControlArchitecture]] — 设备控制架构（唯一规范页）
- [[api/S7NetPlus]] — S7NetPlus 使用笔记
- [[api/ProfinetGSDML]] — Profinet GSDML 开发笔记
- [[api/GlobalCommData]] — GlobalCommData API 说明
- [[lessons/CSharp-Language-Pitfalls]] — GetElement vs GetElementValue 类型陷阱（CommunicationManager 修复记录）

## 协作关系

| 协作对象 | 说明 |
|----------|------|
| [[modules/Workflow]] | 工作流状态由 `LineLaserWorkflowState` 管理；通讯指令通过 `BroadcastCommunicationCommand` 广播到 Workflow |
| [[modules/MotionControl]] | 急停信号、全局状态 |
| [[modules/LaserWeldHead]] | 焊接头状态通过通讯通道上报 |
| [[modules/DeviceControl]] | 机器人/PLC 连接由顶层 Comm 管控，设备状态三态模型（连接态/焊接过程态/整机状态）见 [[modules/DeviceControl]] |
| [[modules/KUKARobot]] | KUKA 机器人通讯子模块（RSI/EKI 协议） |

## 已知问题

- 与 [[modules/SqlLiteDatabase]] 存在循环依赖

---

*来源：raw/skills/02-Development/GeneralTechSpecialist.md + raw/knowledge/AdaWeldSystem_Wiki.md*