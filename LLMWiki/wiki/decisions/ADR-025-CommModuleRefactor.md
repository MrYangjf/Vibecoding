---
title: ADR-025 Comm 模块现行决策（三层重构 · XML 按设备分离 · 通道目录；整合原 004/006/045）
date: 2026-09-14
updated: 2026-10-30
tags: [决策, 通讯, Comm, 模块组织, Manager, XML, 配置管理, merged, ADR-025]
status: accepted
merged_from: [ADR-004, ADR-006, ADR-045]
---

# ADR-025 Comm 模块现行决策（三层重构 · XML 按设备分离 · 通道目录）

> 本页为整合页（2026-09-17），就地吸收并取代原 ADR-004 / ADR-006 / ADR-011 三页，收拢 Comm 模块全部现行裁定。沿革与被取代内容见文末。

## 背景

2026-07 初版（ADR-004 / ADR-006）：合并 `GlobalCommData.cs` + `SystemStatus.cs` 为单一 SystemComm、移除废弃的 `MachineStatus` 状态管理、`CommunicationManager` 按设备类型分离通讯 XML 配置。彼时结构为 `CommBase/`（TCP/Modbus/Profinet）、`PLC/Siemens/`、`Robot/KUKARobot/` 平铺在 `Comm/` 下，五类通讯各自独立实现、无统一抽象，`KUKARobotManager` 作为第二个 Manager 与 `CommunicationManager` 并存（门面分裂）。

用户 2026-09-14 裁定：**丢弃全部原结构设定**，不需要对以太网、Profinet 做封装，按 [[decisions/ADR-006-ModuleOrganizationPatternStandard]] 范式重组为「抽象层 + 实现层 + Manager」。三项子裁定：以太网废弃重写为 `EthernetXmlComm`；同轮整体切换不留平行双实现（H4）；KUKA 门面并入 Manager。

## 现行决策

### 1. 三层结构（ADR-006 范式，场景 A 薄封装形态 3：实现类内部封装第三方调用，不单独建 Core/）

- **抽象层** `Comm/Communication/Abstractions/CommChannelBase.cs`：对外抽象层，**零第三方依赖**。定义 `Name` / `IsConnected` / `Connect()` / `Disconnect()` / `Send(byte[])` / `Send(string)` / `DataReceived` 事件 / `Dispose()`。
- **实现层** `Comm/Communication/Implementations/`，**只允许出现厂商/协议类型**：

| 实现类 | 通道 | 说明 |
|---|---|---|
| `SiemensS7Comm` | 西门子 S7 | 原 S7PLCCommunication |
| `KukaRsiComm` | KUKA RSI（UDP） | 原 RSICommunication |
| `KukaEkiComm` | KUKA EKI（TCP/XML） | 原 EKICommunication |
| `EthernetXmlComm` | 以太网标准通讯 | **全新重写**（STTech.BytesIO Server/Client 双模式 + KUKA 风格预定义 XML 文档收发） |
| `InLaserModbusComm` | 英莱 Modbus | 原 ModbusTCPCommunication |

- **Manager** `Comm/Communication/CommunicationManager.cs`：单例，**唯一对外访问口**——持有全部实现实例、8 个 XML 配置 + INI 开关的持久化、`RobotCommModeType` 路由。

### 2. KUKA 门面并入 Manager

删除 `KUKARobotManager.cs`：`ConnectRobot()` / `DisconnectRobot()` / `SendRobotData()` / `RobotDataReceived` / `RobotConnected` 由 Manager 按 `RobotCommMode`（RSI/EKI 二选一）路由到对应实现。消费方（`DeviceControlWork` 心跳/重连/上电/发令）全部改走 Manager 门面。

### 3. 配置范式：XdocumentReaderWriter 无参 Load/Save（裁定 D1）

- 配置读写方法 **无参**：`LoadConfig()` / `SaveConfig()`，内部走本项目 `FileOperate/XdocumentReaderWriter`；**不引入** `XmlReader`/`XmlWriter` 流式 API（参考写法，本项目不采用）。
- `SaveConfig()` **末尾必须调用 `Config.SaveXdocument()` 落盘**——`SetElementValue` 只改内存中的 `XDocument`，不落盘。
- 每个 workflow / 实现类自带一个配置路径成员（子设备各自持有配置路径）。
- 范式细则见 [[architecture/DeviceControlArchitecture]]（裁定 D1，§16.8）。

### 4. 通讯 XML 按设备类型分离（ADR-006 结论仍有效，承载者已迁至现行 Manager）

`CommunicationManager` 按设备类型分离 XML 配置，**禁止跨类型复用**（机器人页曾错误复用通用 `ServerXdoc` 读 IP/Port、PLC 页曾硬编码 `192.168.0.1`）：

| XML 文件 | 字段名 | 用途 | 节点结构 |
|----------|--------|------|----------|
| RobotServer.xml | `RobotServerXdoc` | 机器人通讯服务端配置（RSI UDP / EKI Server） | `<Root><IP><PORT></Root>` |
| RobotClient.xml | `RobotClientXdoc` | 机器人 EKI 客户端配置 | `<Root><IP><PORT></Root>` |
| PLC.xml | `PlcXdoc` | PLC 通讯配置 | `<Root><IP><PORT><Rack><Slot></Root>` |

- 配套 INI 持久化开关：`ShowRobotCommLog` / `ShowPlcCommLog`（各设备类型日志显示独立控制）。
- 初始化保障：`EnsureElementExists()` 在 `InitializeXmlDocuments()` 中对新 XML 调用、确保节点存在——`SetElementValue` 仅在元素已存在时更新值，必须先初始化。
- 页面侧：订阅 `EventInfoHandler` 事件、`InvokeRequired` 保证线程安全、卸载时按 [[decisions/ADR-002-DisposePatternFullCoverage]] 退订。

### 5. 通道目录 `Config\Comm\<通道>_XML\`

通讯配置按「类别 + 类型 + 格式」嵌套存放于 `Config\Comm\<通道>_XML\`；目录结构与命名细则以 [[decisions/ADR-026-RsiSemanticRewriteAndDualChannel]] 整合页为准，此处不复制。

### 6. Profinet 封装不做（用户裁定）

不做 Profinet 封装：`GSDMLGenerator.cs` 删除、`CommunicationType.Profinet` 枚举成员同轮清除，UI 仅保留「已移除」提示文案（api/ProfinetGSDML 已废弃，Tier 1）。

### 7. 访问与持久化约束

- ⛔ **外部不得绕过 Manager 直接 new 实现类**（H6）。
- ⛔ **配置持久化只归 Manager**（H7）。
- ⛔ **英莱 Modbus 与英莱 SDK 不得同时接管线激光**（互斥约束，裁决归 LineLaserCam 上层；SDK=底层软件管理线激光 / Modbus=寄存器管理）。

### 8. SystemComm 归位

`SystemComm.cs` 位于 `Comm/SystemComm/`，现役命名空间为 `AdaWeldSystem.Comm.SystemComm`（ADR-005「目录即命名空间」对齐，原「命名空间保留 `AdaWeldSystem.Comm`」条款已废止；同批 `Communication/Abstractions/` → `...Comm.Communication.Abstractions`、`Communication/Implementations/` → `...Comm.Communication.Implementations`，三层结构与删除项结论不变）。承担日志、配置开关、全局变量（各模块 Manager 化后全局变量需求已收敛）。

### 9. 事件命名防遮蔽（CS0108）

类型化接收事件不与基类 `DataReceived` 同名：RSI 用 `RsiDataReceived`、EKI 用 `XmlDataReceived`、Modbus 错误参数改 `ModbusErrorEventArgs`。

## 目录结构（现行）

```
Comm/
├── SystemComm/
│ └── SystemComm.cs ← 全局日志/配置/全局变量（命名空间 AdaWeldSystem.Comm.SystemComm）
└── Communication/
 ├── Abstractions/
 │ └── CommChannelBase.cs ← 对外抽象层（零第三方依赖）
 ├── Implementations/
 │ ├── SiemensS7Comm.cs ← 西门子 S7
 │ ├── KukaRsiComm.cs ← KUKA RSI + RSI 数据结构/RSIConfig/RSI 半边 KUKAXMLConfig（partial）
 │ ├── KukaEkiComm.cs ← KUKA EKI + EKI 数据结构/EKIConfig/EKI 半边 KUKAXMLConfig（partial）
 │ ├── EthernetXmlComm.cs ← 以太网标准通讯（BytesIO + 预定义 XML）
 │ └── InLaserModbusComm.cs ← 英莱 Modbus（与 SDK 互斥）+ ILModbusData 寄存器映射
 └── CommunicationManager.cs ← 单例 Manager · 唯一对外访问口（含 KUKADataReceivedEventArgs 等管理层事件参数）
```

## 后果

- 正面：五通道统一在 `CommChannelBase` 契约下；对外只剩 Manager 一个访问口；Profinet/GSDML 死代码与双门面分裂清除；XML 按设备类型分离 + 通道目录让配置归属清晰。
- 负面 / 沿革：`S7PLCCommunication` / `RSICommunication` / `EKICommunication` / `ModbusTCPCommunication` / `TCPIPComm` / `KUKARobotManager` 等旧名在历史 ADR / 模块页中仍会出现，检索以本页与 [[modules/Comm]] 现行页为准（已登记 drift 扫描器 RENAMED/REMOVED 表）。

## 沿革

- 2026-07-02 ADR-004 初版：合并 SystemComm 文件、移除 `MachineStatus` 状态管理（该结论由三态模型承接，[[decisions/ADR-013-ThreeStateModelRefactor]]）、`TcpIpComm` 纳入 Manager（该类后被 045 重构删除，由 `EthernetXmlComm` 取代）。
- 2026-07-03 ADR-006 初版：通讯 XML 按设备类型分离（结论仍有效，本页决策 4；页面旧名 `CommRobotPage` 现为 `CommPage`）。
- 2026-09-14 ADR-011 重构：三层归位取代 004/006 的平铺结构与双门面；本页（2026-09-17）整合三者，004/006 就此并入。

## 相关

- [[decisions/ADR-006-ModuleOrganizationPatternStandard]] — 模块组织范式（本决策是其通讯域落地）
- [[decisions/ADR-026-RsiSemanticRewriteAndDualChannel]] — RSI/EKI 现行决策 + 通道配置目录细则（整合页）
- [[decisions/ADR-005-NamespaceDirectoryAlignment]] — 命名空间与目录对齐
- [[decisions/ADR-002-DisposePatternFullCoverage]] — Dispose 约束
- [[modules/Comm]] / [[modules/KUKARobot]] — 模块说明
- [[api/GlobalCommData]] — 全局通讯配置入口

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[decisions/ADR-Index]]
