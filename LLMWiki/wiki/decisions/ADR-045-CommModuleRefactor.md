---
title: ADR-045 Comm 模块重构（抽象层 + 实现层 + Manager 三层归位）
date: 2026-09-14
tags: [决策, 通讯, Comm, 模块组织, Manager, ADR-045]
status: accepted
---

# ADR-045 Comm 模块重构（抽象层 + 实现层 + Manager 三层归位）

> ⚠️ **沿革横幅（2026-09-14，ADR-048）**：决策 **§4「`SystemComm.cs` 移入 `Comm/SystemComm/`（命名空间仍 `AdaWeldSystem.Comm`）」的「命名空间保留」条款已废止**——现役为 `AdaWeldSystem.Comm.SystemComm`；同批 `Communication/Abstractions/` → `...Comm.Communication.Abstractions`、`Communication/Implementations/` → `...Comm.Communication.Implementations`。三层结构与删除项结论不变。见 [[decisions/ADR-048-NamespaceDirectoryAlignment]]。

## 状态

已采纳（2026-09-14）。

## 背景

旧 `Comm/` 结构是 2026-08-03 重构的产物（[[decisions/ADR-004-CommRefactor]] / [[decisions/ADR-006-CommXmlSeparation]]）：`CommBase/`（TCP/Modbus/Profinet）、`PLC/Siemens/`、`Robot/KUKARobot/`、`CommunicationManager.cs`、`SystemComm.cs` 平铺在 `Comm/` 下，五类通讯各自独立实现、无统一抽象，`KUKARobotManager` 作为第二个 Manager 与 `CommunicationManager` 并存（门面分裂）。

用户 2026-09-14 裁定：**丢弃全部原设定**，不需要对以太网、Profinet 做封装，按 [[decisions/ADR-042-ModuleOrganizationPatternStandard]] 范式重组为「抽象层 + 实现层 + Manager」。三项子裁定：以太网废弃重写为 `EthernetXmlComm`；同轮整体切换不留平行双实现（H4）；KUKA 门面并入 Manager。

## 决策

1. **三层结构**（ADR-042 范式，场景 A 薄封装形态 3：实现类内部封装第三方调用，不单独建 Core/）：
   - `Comm/Communication/Abstractions/CommChannelBase.cs`：对外抽象层，**零第三方依赖**。定义 `Name` / `IsConnected` / `Connect()` / `Disconnect()` / `Send(byte[])` / `Send(string)` / `DataReceived` 事件 / `Dispose()`。
   - `Comm/Communication/Implementations/`：五个实现，**只允许出现厂商/协议类型**：
     | 实现类 | 通道 | 说明 |
     |---|---|---|
     | `SiemensS7Comm` | 西门子 S7 | 原 S7PLCCommunication |
     | `KukaRsiComm` | KUKA RSI（UDP） | 原 RSICommunication |
     | `KukaEkiComm` | KUKA EKI（TCP/XML） | 原 EKICommunication |
     | `EthernetXmlComm` | 以太网标准通讯 | **全新重写**（STTech.BytesIO Server/Client 双模式 + KUKA 风格预定义 XML 文档收发） |
     | `InLaserModbusComm` | 英莱 Modbus | 原 ModbusTCPCommunication；**与英莱 SDK 互斥**（SDK=底层软件管理线激光 / Modbus=寄存器管理），裁决在上层 LineLaserCam |
   - `Comm/Communication/CommunicationManager.cs`：单例 Manager，**唯一对外访问口**——持有全部实现实例、8 个 XML 配置 + INI 开关的持久化、`RobotCommModeType` 路由。

2. **KUKA 门面并入 Manager**：删除 `KUKARobotManager.cs`，`ConnectRobot()` / `DisconnectRobot()` / `SendRobotData()` / `RobotDataReceived` / `RobotConnected` 由 Manager 按 `RobotCommMode`（RSI/EKI 二选一）路由到对应实现。消费方（`DeviceControlWork` 心跳/重连/上电/发令）全部改走 Manager 门面。

3. **删除项**：`TCPIPComm.cs`（被 `EthernetXmlComm` 取代）、`GSDMLGenerator.cs`（Profinet 封装不做，`CommunicationType.Profinet` 枚举成员同轮清除，UI 仅保留"已移除"提示文案）。

4. **SystemComm 归位**：`SystemComm.cs` 移入 `Comm/SystemComm/`（命名空间仍 `AdaWeldSystem.Comm`），承担日志、配置开关、全局变量（各模块 Manager 化后全局变量需求已收敛）。

5. **事件命名防遮蔽（CS0108）**：类型化接收事件不与基类 `DataReceived` 同名——RSI 用 `RsiDataReceived`、EKI 用 `XmlDataReceived`、Modbus 错误参数改 `ModbusErrorEventArgs`。

## 目录结构（变更后）

```
Comm/
├── SystemComm/
│   └── SystemComm.cs                     ← 全局日志/配置/全局变量（命名空间仍 AdaWeldSystem.Comm）
└── Communication/
    ├── Abstractions/
    │   └── CommChannelBase.cs            ← 对外抽象层（零第三方依赖）
    ├── Implementations/
    │   ├── SiemensS7Comm.cs              ← 西门子 S7
    │   ├── KukaRsiComm.cs                ← KUKA RSI + RSI 数据结构/RSIConfig/RSI 半边 KUKAXMLConfig（partial）
    │   ├── KukaEkiComm.cs                ← KUKA EKI + EKI 数据结构/EKIConfig/EKI 半边 KUKAXMLConfig（partial）
    │   ├── EthernetXmlComm.cs            ← 以太网标准通讯（BytesIO + 预定义 XML）★新写
    │   └── InLaserModbusComm.cs          ← 英莱 Modbus（与 SDK 互斥）+ ILModbusData 寄存器映射
    └── CommunicationManager.cs           ← 单例 Manager · 唯一对外访问口（含 KUKADataReceivedEventArgs 等管理层事件参数）
```

## 后果

- 正面：五通道统一在 `CommChannelBase` 契约下；对外只剩 Manager 一个访问口；Profinet/GSDML 死代码与双门面分裂清除。
- 负面 / 沿革：`S7PLCCommunication` / `RSICommunication` / `EKICommunication` / `ModbusTCPCommunication` / `TCPIPComm` / `KUKARobotManager` 等旧名在历史 ADR / 模块页中仍会出现，检索以本条与 [[modules/Comm]] 现行页为准（已登记 drift 扫描器 RENAMED/REMOVED 表）。
- 约束：
  - ⛔ 外部不得绕过 Manager 直接 new 实现类（H6）；
  - ⛔ 配置持久化只归 Manager（H7）；
  - ⛔ 英莱 Modbus 与英莱 SDK 不得同时接管线激光（互斥约束，裁决归 LineLaserCam 上层）。

## 相关

- [[decisions/ADR-042-ModuleOrganizationPatternStandard]] — 模块组织范式（本决策是其通讯域落地）
- [[decisions/ADR-004-CommRefactor]] / [[decisions/ADR-006-CommXmlSeparation]] — 旧 Comm 决策（结构已被本轮取代，XML 分离结论仍有效）
- [[modules/Comm]] / [[modules/KUKARobot]] — 模块说明
- [[api/GlobalCommData]] — 全局通讯配置入口
- [[api/ProfinetGSDML]] — 已废弃（Tier 1）
