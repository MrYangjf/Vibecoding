---
title: Comm 模块 — 通讯与全局状态
date: 2026-08-03
updated: 2026-09-14
tags: [模块, 通讯, 全局状态, TCP/IP, S7, Modbus, KUKA, Manager, ADR-045]
source: raw/skills/02-Development/GeneralTechSpecialist.md
---

# Comm 模块 — 通讯与全局状态

> 全局数据通讯中心、统一设备通讯（S7 / KUKA RSI / KUKA EKI / 以太网 XML / Modbus）、系统状态定义、程序入口。
>
> **通讯优先级策略：** 机器人通讯为默认主通道，PLC 通讯为备用通道。系统运行时优先通过机器人通讯（KUKA RSI/EKI）获取位置信息与控制工艺参数；当机器人通讯不可用时，自动切换至 PLC 通讯（S7）作为降级通道。
>
> **2026-09-14 重构（ADR-045）**：按 [[standards/ModuleOrganizationPattern]] 重组为「抽象层 + 实现层 + Manager」。旧 `CommBase/`、`PLC/`、`Robot/KUKARobot/` 目录与 `KUKARobotManager`、`TCPIPComm`、`GSDMLGenerator` 已删除；**Profinet 封装不做**（用户裁定）。KUKA 协议知识见 [[modules/KUKARobot]]（历史名称提示横幅）。

## 目录结构

```
Comm/
├── SystemComm/
│   └── SystemComm.cs                       ← 全局日志/配置/全局变量/事件（命名空间 AdaWeldSystem.Comm.SystemComm，ADR-048 起随目录对齐）
└── Communication/
    ├── Abstractions/
    │   └── CommChannelBase.cs              ← 对外抽象层（零第三方依赖）：Name/IsConnected/Connect/Disconnect/Send/DataReceived/Dispose
    ├── Implementations/
    │   ├── SiemensS7Comm.cs                ← 西门子 S7（原 S7PLCCommunication）
    │   ├── KukaRsiComm.cs                  ← KUKA RSI（UDP，原 RSICommunication）+ RSI 数据结构/RSIConfig/RSI 半边 KUKAXMLConfig（partial）
    │   ├── KukaEkiComm.cs                  ← KUKA EKI（TCP/XML，原 EKICommunication）+ EKI 数据结构/EKIConfig/EKI 半边 KUKAXMLConfig（partial）
    │   ├── EthernetXmlComm.cs              ← 以太网标准通讯（STTech.BytesIO Server/Client + KUKA 风格预定义 XML）★重写
    │   └── InLaserModbusComm.cs            ← 英莱 Modbus（原 ModbusTCPCommunication；与英莱 SDK 互斥）+ ILModbusData 寄存器映射（0x00~0x28）
    └── CommunicationManager.cs             ← 单例 Manager · 唯一对外访问口
```

| 子目录/文件 | 命名空间 |
|--------|---------|
| `SystemComm/SystemComm.cs` | `AdaWeldSystem.Comm.SystemComm` |
| `Communication/CommunicationManager.cs` | `AdaWeldSystem.Comm.Communication` |
| `Communication/Abstractions/` | `AdaWeldSystem.Comm.Communication.Abstractions` |
| `Communication/Implementations/` | `AdaWeldSystem.Comm.Communication.Implementations` |
| 顶层 `Program.cs`（代码根） | `AdaWeldSystem` |

## 核心文件

| 文件 | 职责 |
|------|------|
| `Communication/Abstractions/CommChannelBase.cs` | 通讯通道抽象基类：abstract `Name`/`IsConnected`/`Connect()`/`Disconnect()`/`Dispose()`；virtual `Send(byte[])`/`Send(string)`（UTF-8）；`DataReceived` 事件（`CommDataEventArgs`：Data/Text/Timestamp）；`LastErrorMessage`。**零第三方依赖** |
| `Communication/Implementations/SiemensS7Comm.cs` | 西门子 S7 通讯封装（S7NetPlus，备用通道） |
| `Communication/Implementations/KukaRsiComm.cs` | KUKA RSI UDP 实时通讯；类型化事件 `RsiDataReceived`（不与基类 `DataReceived` 同名，防 CS0108 遮蔽） |
| `Communication/Implementations/KukaEkiComm.cs` | KUKA EKI TCP/XML 通讯；类型化事件 `XmlDataReceived` |
| `Communication/Implementations/EthernetXmlComm.cs` | **以太网标准通讯**（2026-09-14 重写）：`StartServer/StopServer/ConnectClient/DisconnectClient`；`SendXmlDocument(rootName, elements)` 收发 KUKA 风格 `<Root><Elem>value</Elem></Root>` 预定义 XML 文档；内嵌 `SstTcpServer`/`SstTcpClient` |
| `Communication/Implementations/InLaserModbusComm.cs` | Modbus TCP 主站（自实现 MBAP+PDU，FC03/FC06/FC16）；错误参数类 `ModbusErrorEventArgs`。**与英莱 SDK 互斥**（SDK=底层软件管理线激光 / Modbus=寄存器管理），裁决在 LineLaserCam 上层 |
| **`Communication/CommunicationManager.cs`** | **单例 Manager，唯一对外访问口**：持有 5 个实现实例（`EthernetComm`/`RsiComm`/`EkiComm`/`S7Comm`/`ModbusComm`）；持久化 8 个 XML（Server/Client/Send/Recive + RobotServer/RobotClient + PLC + Modbus）+ INI 开关 + `RobotCommMode`；**KUKA 门面**：`ConnectRobot()`/`DisconnectRobot()`/`SendRobotData(KUKARobotData)`/`RobotDataReceived`/`RobotConnected`（按 `RobotCommModeType` RSI/EKI 二选一路由）；实现 `IDisposable` |
| `SystemComm/SystemComm.cs` | 全局通讯/状态/事件定义中心：`GlobalCommData` 静态类（ShowLog/ShowCommunicationLog/BroadcastCommunicationCommand/UIConfigSetting/mCommunicationManager）、消息/工作流/权限枚举、事件参数类 |
| Program.cs | 程序入口 |
| App.config | 应用配置 |

### 资源释放入口（ADR-001 非 UI 类标准）

| 类 | 释放入口 | 释放内容 |
|----|---------|---------|
| `CommunicationManager` | `IDisposable.Dispose()` | 5 个实现实例（含机器人门面退订） |
| `CommChannelBase` 及各实现 | `IDisposable.Dispose()` | 各自底层连接（RSI：接收线程 + UdpClient；EKI：接收线程 + NetworkStream + TcpClient；S7：`_plc.Close`；Modbus：NetworkStream + TcpClient；EthernetXmlComm：SstTcpServer/SstTcpClient） |

**释放调用链**：`FormMain_FormClosed` → `DeviceControlWork.Instance.Dispose()` → 停止运行线程 + 关闭机器人连接（`comm.DisconnectRobot()`）+ Shutdown 焊接头 + `GlobalCommData.mCommunicationManager.Dispose()`。

## 外部依赖

| 包 | 用途 | 添加方式 |
|----|------|---------|
| S7NetPlus | 西门子 S7 通讯 | NuGet: `Install-Package S7NetPlus` |
| STTech.BytesIO.Tcp | 以太网标准通讯（EthernetXmlComm） | NuGet: `Install-Package STTech.BytesIO.Tcp` |

## 统一设备通讯职责模型

| 职责类别 | 操作 |
|----------|------|
| 工作流程控制指令（下行） | Start / Stop / Pause / Reset |
| 设备运行状态反馈（上行） | 状态上报 / 异常错误上报 |
| 通讯指令广播 | BroadcastCommunicationCommand → Workflow 接收并记录日志 |
| 通讯配置持久化 | CommunicationManager.Load/Save/AddOrUpdate（H7：持久化只归 Manager） |
| 通讯 XML 结构管理 | 8 个 XML：Server/Client/Send/Recive（通用 TCP）+ RobotServer/RobotClient（机器人）+ PLC + Modbus（[[decisions/ADR-006-CommXmlSeparation]]，仍有效） |
| 以太网通讯实例 | `CommunicationManager.EthernetComm`（`EthernetXmlComm`，Server/Client 双模式 + 预定义 XML 文档） |
| 通讯日志显示开关 | ShowCommLog / ShowRobotCommLog / ShowPlcCommLog / ShowModbusCommLog（INI 持久化） |
| 通讯启用开关 | IsRobotEnabled / IsPlcEnabled / IsGeneralEnabled（INI，`CommunicationSettings.ini` [Display] 段） |
| 机器人通讯模式 | `RobotCommMode`（`RobotCommModeType`：RSI/EKI 二选一，INI 持久化） |
| **机器人通讯（默认主通道）** | KUKA RSI/EKI —— 经 Manager 门面（`ConnectRobot`/`SendRobotData`/`RobotDataReceived`），协议知识见 [[modules/KUKARobot]] |
| **PLC 通讯（备用通道）** | `S7Comm`（S7NetPlus） |
| **Modbus 通讯** | `ModbusComm`（英莱相机等，与英莱 SDK 互斥） |
| ~~Profinet~~ | ⛔ 2026-09-14 用户裁定不做封装；`GSDMLGenerator` 已删除，UI 仅保留"已移除"提示 |

## 已取消的规划（勿再当作待办）

| 规划项 | 现状 |
|--------|------|
| `NetworkPort` 统一抽象层（`INetworkPort` / `NetworkPortBase`） | **已取消**。统一抽象由 `CommChannelBase` 承接（ADR-045） |
| `RobotConnectionStateMachine`（机器人连接状态机） | **已取消**。机器人连接由 Manager 门面管控，设备连接态由三态模型承载 |

## 相关文档

- [[decisions/ADR-045-CommModuleRefactor]] — 本轮重构决策（现行）
- [[decisions/ADR-004-CommRefactor]] / [[decisions/ADR-006-CommXmlSeparation]] — 旧 Comm 决策（XML 分离结论仍有效）
- [[modules/KUKARobot]] — KUKA 协议知识（RSI/EKI 参考手册）
- [[api/S7NetPlus]] — S7NetPlus 使用笔记
- [[api/ProfinetGSDML]] — ⛔ 已废弃（Profinet 封装不做）
- [[api/GlobalCommData]] — GlobalCommData API 说明
- [[lessons/CSharp-Language-Pitfalls]] — GetElement vs GetElementValue 类型陷阱

## 协作关系

| 协作对象 | 说明 |
|----------|------|
| [[modules/DeviceControl]] | 工作流状态由三态模型承载；通讯指令通过 `BroadcastCommunicationCommand` 广播到各工作流；机器人门面消费方（心跳/重连/发令）全部走 Manager |
| [[modules/MotionControl]] | 急停信号、全局状态 |
| [[modules/LaserWeldHead]] | 焊接头状态通过通讯通道上报 |
| [[modules/KUKARobot]] | KUKA 机器人协议子模块（RSI/EKI 参考知识） |
| [[modules/LineLaserCam]] | 英莱 Modbus 与英莱 SDK 互斥的裁决归属 |

## 已知问题

- 与 [[modules/SQLiteDatabase]] 存在循环依赖

---

*来源：raw/skills/02-Development/GeneralTechSpecialist.md + ADR-045（2026-09-14 重构）*
