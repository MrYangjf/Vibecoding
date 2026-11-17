---
title: Comm 模块 — 通讯与全局状态
date: 2026-08-03
updated: 2026-09-16
tags: [模块, 通讯, 全局状态, TCP/IP, S7, Modbus, KUKA, Manager, 位姿快照, ADR-011, ADR-027]
source: raw/skills/02-Development/GeneralTechSpecialist.md
---

# Comm 模块 — 通讯与全局状态

> 全局数据通讯中心、统一设备通讯（S7 / KUKA RSI / KUKA EKI / 以太网 XML / Modbus）、系统状态定义、程序入口。
>
> **通讯优先级策略：** 机器人通讯为默认主通道，PLC 通讯为备用通道。系统运行时优先通过机器人通讯（KUKA RSI/EKI）获取位置信息与控制工艺参数；当机器人通讯不可用时，自动切换至 PLC 通讯（S7）作为降级通道。
>
> **2026-09-14 重构（ADR-011）**：按 [[standards/ModuleOrganizationPattern]] 重组为「抽象层 + 实现层 + Manager」。旧 `CommBase/`、`PLC/`、`Robot/KUKARobot/` 目录与 `KUKARobotManager`、`TCPIPComm`、`GSDMLGenerator` 已删除；**Profinet 封装不做**（用户裁定）。KUKA 协议知识见 [[api/KUKARobot]]（历史名称提示横幅）。

## 目录结构

```
Comm/
├── SystemComm/
│   └── SystemComm.cs                       ← 全局日志/配置/全局变量/事件（命名空间 AdaWeldSystem.Comm.SystemComm，ADR-005 起随目录对齐）
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
| `Communication/Implementations/KukaEkiComm.cs` | ⛔ **已移除**（2026-10-21 删除；ADR-026/ADR-074 通讯通道唯一为 RSI，EKI 通道整体退役） |
| `Communication/Implementations/EthernetXmlComm.cs` | **以太网标准通讯**（2026-09-14 重写）：`StartServer/StopServer/ConnectClient/DisconnectClient`；`SendXmlDocument(rootName, elements)` 收发 KUKA 风格 `<Root><Elem>value</Elem></Root>` 预定义 XML 文档；内嵌 `SstTcpServer`/`SstTcpClient` |
| `Communication/Implementations/InLaserModbusComm.cs` | Modbus TCP 主站（自实现 MBAP+PDU，FC03/FC06/FC16）；错误参数类 `ModbusErrorEventArgs`。**与英莱 SDK 互斥**（SDK=底层软件管理线激光 / Modbus=寄存器管理），裁决在 LineLaserCam 上层 |
| **`Communication/CommunicationManager.cs`** | **单例 Manager，唯一对外访问口**：持有 4 个实现实例（`EthernetComm`/`RsiComm`/`S7Comm`/`ModbusComm`）（⛔ `EkiComm` 已于 2026-10-21 随 ADR-074 退役删除）；持久化 XML + INI 开关 + `RobotCommMode`；**KUKA 门面**：`ConnectRobot()`/`DisconnectRobot()`/`SendRobotData(KUKARobotData)`/`RobotDataReceived`/`RobotConnected`（RSI 为唯一通道）；实现 `IDisposable` |
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
| 通讯 XML 结构管理 | 8 个 XML：Server/Client/Send/Recive（通用 TCP）+ RobotServer/RobotClient（机器人）+ PLC + Modbus（ADR-025（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]），仍有效） |
| 以太网通讯实例 | `CommunicationManager.EthernetComm`（`EthernetXmlComm`，Server/Client 双模式 + 预定义 XML 文档） |
| 通讯日志显示开关 | ShowCommLog / ShowRobotCommLog / ShowPlcCommLog / ShowModbusCommLog（INI 持久化） |
| 通讯启用开关 | IsRobotEnabled / IsPlcEnabled / IsGeneralEnabled（INI，`CommunicationSettings.ini` [Display] 段） |
| 机器人通讯模式 | `RobotCommMode`（`RobotCommModeType`：RSI/EKI 二选一，INI 持久化，**RSI=0 为默认值**） |
| **RSI / EKI 互斥单通道（2026-09-15 ADR-026，废止 ADR-031 双通道）** | RSI 与 EKI **互斥**，`ConnectRobot()`/`DisconnectRobot()` 只操作当前 `RobotCommMode` 对应通道（上机实证：双通道会拖 EKI 超时 20 秒且语义错误）；`SendRobotData(EStr)` 仅 EKI 模式生效，RSI 模式下无指令通道（未连接记警告并附当前模式）；机器人端 XML 归 Manager **每次启动自动生成**（`InitializeRobotComm` → `SaveRobotRsiXml()` → `Config\Comm\KUKARobot_RSI_XML\WeldControlConfig.xml`，SEND=DEF_RIst+Tool.X/Y/Z 三标量映射输入端 1/2/3（ADR-026）、RECEIVE=DEF_Tech.C1/C2，参数取 `RobotServerXdoc` 的 HOST_IP/HOST_PORT/SENTYPE） |
| **通讯配置目录（2026-09-15 ADR-026）** | 全部通讯 XML 统一落 `Config\Comm\<通道>_XML`：KUKARobot_RSI_XML（RobotServer + WeldControlConfig + WeldControlSendFormat）/ KUKARobot_EKI_XML（RobotClient）/ Tcp_XML（Server/Client/Send/Recive）/ PLC_XML / Modbus_XML / Communication_XML（主配置）；通讯 INI（`CommunicationSettings.ini`）落 `Config\Comm\Communication_INI`。`XdocumentReaderWriter` 双参构造 `(relativeDirectory, xmlName)` 是落盘目录唯一入口，单参构造已废弃、`_configDirectory` 置空；旧 `Config\XML\` 通讯文件的搬迁自 2026-09-21 起统一由 `FileOperate/ConfigPathMigrator.cs`（`Program.Main` 首步）承担，原 `MigrateLegacyCommXml()` 已删除，**迁移先于任何 Xdoc 构造** |
| **RSI 数据方向契约（2026-09-15 ADR-031/052）** | 机器人 12ms 发 `<Rob><RIst/><Tool X Y Z/><IPOC>` → 本机解析进 `RsiRobotPacket`（`RsiDataReceived` 事件，`RobotData.RIst` 同步填充供既有消费方；**ADR-026 增 ToolX/ToolY/ToolZ**——焊接时机器人基于车身坐标计算的工具位置；**ADR-026 修正发送结构**：`DEF_Tool` 非 RSI 3.3 合法关键词且一个 ELEMENT 只承载一个标量，改为 Tool.X/Y/Z 三标量映射 ETHERNET 输入端 1/2/3，机器人端 RSI 信号图接线，数据包属性书写形式 `<Tool X= Y= Z=/>`，未接线时为 0）；本机回复 `<Sen Type="SENTYPE"><Tech T11=功率 T12=送丝/><IPOC 原样回传/></Sen>`——接收线程与回复线程分离，回复值经 `UpdateRobotWeldParams(功率, 送丝)` 写入（KUKA RSI 3.3 语义，旧「上位机=传感器修正」方向接口已删除） |
| **RSI 收发格式文档驱动（2026-09-16 ADR-026）** | 收发以格式文档为准，不再硬编码：①上位机 `RobotServer.xml` 一份文档含配置 + `SEND_FORMAT`（Rob 包模板，解析依据）+ `REPLY_FORMAT`（Sen 包模板，组包依据），构造期缺失自动补内置默认节；②机器人端生成双文档——`WeldControlConfig.xml`（配置）+ `WeldControlSendFormat.xml`（收发格式定义）；③`RsiPacketFormat` 模型 + `ParseFormatSection`/`LoadPacketFormat`，`InitializeRobotComm` 装载进 `KukaRsiComm.SendPacketFormat`/`ReplyPacketFormat`——解析按格式属性顺序绑定 RIst（六属性→KUKAPosition）/Tool（三属性→ToolX/Y/Z）、IPOC 取文本，RIst 缺失返回 null；组包按占位值约定：`激光功率`/`送丝速度`=实时值、`原样回传`/`时间戳`=IPOC、其余字面量；④格式节缺失回退内置默认格式，旧静态签名保留；⑤**Tech 属性名固定 T11~T19、T110（"T1"+序号 1~10）**，禁止连号误推 T20~T109；⑥改格式文档即改收发行为（语义绑定外无需改代码） |
| **RSI 通讯周期可配置（2026-09-15）** | 实际周期由机器人 IPO 模式决定（12ms 默认 / IPO_FAST 4ms），上位机不可改变；`RobotServerXdoc` 增 `CYCLE` 元素（默认 12）为**预期周期真相源**：`FilebackupPage`「通讯周期」下拉（4/12/24 ms）→ Manager 门面 `SetRsiCycleMs()` 写 `RsiComm.CycleMs` + 持久化 Xdoc（H6/H7）；`InitializeRobotComm()` 读 CYCLE 装载。用途：接收超时判定——`KukaRsiComm` 接收套接字超时=2 周期，连续 `StallWarnCycles`(5) 周期无包告警一次（节流，恢复收包复位并记「数据流已恢复」）；尚未收到首包不判定 |
| **机器人位姿上行快照（2026-09-16 ADR-027）** | `CommunicationManager` 在 `RsiComm_DataReceived` 开头调 `UpdateRobotPose(e)`，把最新位姿落为**加锁只读快照** `RobotPoseSnapshot`（X/Y/Z/Timestamp；`e.RobotData.RIst` 为空则**保持上一帧**，不用 0 覆盖）；对外 `HasRobotPose` / `TryGetRobotPose(out RobotPoseSnapshot)`。**位姿单一真相源在通讯层**——[[api/WeldParamManager]] 订阅 `RobotDataReceived` 后只刷新 `CurrentRobotX` 并转发给 [[api/SeamMapTrackingAlgorithm]]，⛔ 不另存 `_robotPoseX/Y/Z` 副本、不加第二把锁（反模式：各层各存一份，谁先谁后不可判） |
| 机器人 XML 编辑入口（2026-09-15） | UI `FilebackupPage`「打开配置」按钮按当前模式弹出 `FileEditorForm`（ADR-027 Modal）编辑 **Manager 自持 Xdoc**：RSI → `RobotServerXdoc` / EKI → `RobotClientXdoc`——此二者为连接参数**唯一真相源**（`InitializeRobotComm()` 从中装载）；启停统一走门面 `InitializeRobotComm()`+`ConnectRobot()`/`DisconnectRobot()`，UI 不直调 RSI/EKI 实现（H6） |
| **机器人通讯（默认主通道）** | KUKA RSI/EKI —— 经 Manager 门面（`ConnectRobot`/`SendRobotData`/`RobotDataReceived`），协议知识见 [[api/KUKARobot]] |
| **PLC 通讯（备用通道）** | `S7Comm`（S7NetPlus） |
| **Modbus 通讯** | `ModbusComm`（英莱相机等，与英莱 SDK 互斥） |
| ~~Profinet~~ | ⛔ 2026-09-14 用户裁定不做封装；`GSDMLGenerator` 已删除，UI 仅保留"已移除"提示 |

## 已取消的规划（勿再当作待办）

| 规划项 | 现状 |
|--------|------|
| `NetworkPort` 统一抽象层（`INetworkPort` / `NetworkPortBase`） | **已取消**。统一抽象由 `CommChannelBase` 承接（ADR-011） |
| `RobotConnectionStateMachine`（机器人连接状态机） | **已取消**。机器人连接由 Manager 门面管控，设备连接态由三态模型承载 |

## 2026-10-21 ADR-074 落地（RSI 数值化协议 + EKI 退役）

- ✅ `KukaEkiComm.cs` **整文件删除** + csproj 退注册；`CommunicationManager.EkiComm` 属性删除；
  `RobotCommMode` 恒返回 RSI；`ConnectRobot`/`DisconnectRobot` 只操作 RSI
- ✅ `KukaRsiComm` 占位符扩 **11 项**（5 焊参 + `TxCmd`/`TxPayload`/`TxSeq` + IPOC），
  保持「格式文档驱动」架构（ADR-026 决策 7 不变）
- ✅ **修真 bug**：`SendLoop` 原调 `BuildReplyXml(...)` 内置默认 ⇒ 已装载的 `ReplyPacketFormat`
  从未被使用；改为 `BuildReplyXml(ReplyPacketFormat, ...)`
- ✅ 指令层：`CommandCore` 增数值码映射（RX 9 / TX 10）；`DeviceControlWork` 收发两侧均走数值码
- **2026-10-22 契约修订**：TX 8 由 `TX_OK` 改 **`TX_NG`**（焊接中异常通知机器人停止）、`TX_CUT_WIRE` 退映射（10=备用，剪丝仅 `CutWire` 具名元素）；机器人侧取消「焊前 OK」应答握手（发下一步指令即默认检查通过）；默认 IP 改机器人 `192.168.10.100` / 本机 `192.168.10.50`
- **2026-10-22 结构/端口对齐**：`RobotServer.xml` 连接参数统一挂 `<CONFIG>`（旧根级结构启动时自动迁移，`GetElement` 走 Descendants 兼容读取）；`HOST_PORT` 作本机监听口（缺失回落 `PORT`），`PORT` 写 `RsiComm.RobotPort`；通道开关保持 Comm INI（避免 XML/INI 双真相）
- **2026-10-22 在线判据**：RSI 为机器人主动发包模型，机器人=客户端、上位机=UDP 服务端/监听方；`RobotConnected` 仅表示监听启动，`IsRobotOnline` = 收到过包且最近一包在 `max(5×CYCLE, 500ms)` 内；心跳/主界面设备按钮/调试面板统一改用后者
- **2026-10-22 监听绑定收紧**：`KukaRsiComm.Start()` 由 `0.0.0.0` 改为绑定 `HOST_IP`；绑定前校验本机网口（IP 已分配 + Up），否则记录「本机无可用网口承载 HOST_IP …」错误日志并返回失败——避免“永远能监听、永远没数据”
- ✅ 焊参：`WeldParamControlWorkflow` 由文本协议 `"P..S..V..G.."` 改走 5 个具名元素通道
- ✅ 通讯调试面板落既有 `panelRobot`（FilebackupPage 通讯配置文件页），19 控件
- ⛔ 真编译待 Visual Studio 验证

---

## 相关文档

- [[decisions/ADR-025-CommModuleRefactor]] — 本轮重构决策（现行）
- ADR-025（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） / ADR-025（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 旧 Comm 决策（XML 分离结论仍有效）
- [[api/KUKARobot]] — KUKA 协议知识（RSI/EKI 参考手册）
- [[api/S7NetPlus]] — S7NetPlus 使用笔记
- api/ProfinetGSDML（⛔ 已废弃删除，ADR-011） — ⛔ 已废弃（Profinet 封装不做）
- [[api/GlobalCommData]] — GlobalCommData API 说明
- [[lessons/CSharp-Language-Pitfalls]] — GetElement vs GetElementValue 类型陷阱

## 协作关系

| 协作对象 | 说明 |
|----------|------|
| [[modules/DeviceControl]] | 工作流状态由三态模型承载；通讯指令通过 `BroadcastCommunicationCommand` 广播到各工作流；机器人门面消费方（心跳/重连/发令）全部走 Manager |
| [[modules/MotionControl]] | 急停信号、全局状态；焊接头从站设备归运控（2026-09-15 ADR-014） |
| [[api/KUKARobot]] | KUKA 机器人协议子模块（RSI/EKI 参考知识） |
| [[modules/LineLaserCam]] | 英莱 Modbus 与英莱 SDK 互斥的裁决归属 |

## RSI 通道运行时约束（ADR-026 / ADR-074）

| 约束 | 实现落点 |
|---|---|
| 收包解析必须使用已装载的 `SendPacketFormat` | `KukaRsiComm.ReceiveLoop` → `ParseRobotPacket(xml, SendPacketFormat)` |
| 文本节点按元素名分派语义（IPOC / RxCmd / RxPayload），禁止一律当 IPOC | `KukaRsiComm.ParseRobotPacket` |
| 一包一回：收包置位信号，回复线程取快照组包，禁 1ms 盲发 | `_replySignal` / `SendLoop` / `Stop` 唤醒 |
| `SEND_FORMAT`/`REPLY_FORMAT` 只补缺失不够，旧 Tech 契约须原地升级 | `CommunicationManager.EnsureRsiFormatSections` + `HasRequiredElements` |
| 机器人端发包端口唯一真相 = 本机监听 `PORT`（`HOST_PORT` 仅核对） | `SaveRobotRsiXml` 取 `RsiComm.LocalPort` |
| 上行指令按变化沿去重（机器人保持 ≥3 IPO 周期） | `DeviceControlWork.OnRobotDataReceived` → `_lastRxCmdCode` |
| 停用机器人通讯开关必须同时停止 RSI 监听 | `FilebackupPage.chkEnable_CheckedChanged` → `DisconnectRobot` |
| 启停失败原因集中暴露，调试页直接展示 | `KukaRsiComm.LastError`（成功清空）+ `FilebackupPage` 启停/开关日志 |
| 通讯按钮操作日志落调试页通讯日志 | `FilebackupPage` 各通讯按钮 → `AppendLog`（`inputLog`） |

> 坑点与判据见 [[lessons/FormatDrivenPacketParsingPitfalls]]（文本节点误判 / 节存在≠契约正确 / 回复盲发）。
> 启动时序门禁（静态构造重入日志 / 界面未就绪禁开 RSI）见 [[lessons/StartupInitializationOrderGates]]。

## 已知问题

- 与 [[modules/SQLiteDatabase]] 存在循环依赖

---

*来源：raw/skills/02-Development/GeneralTechSpecialist.md + ADR-011（2026-09-14 重构）*


## 2026-09-21 全盘审计修复（日志出口去重）

| # | 问题 | 修复 |
|---|---|---|
| 1 | `CommChannelBase.Tag` / `Log` 为 `private`，五个实现类**根本继承不到**，于是各抄一份相同样板（SiemensS7/KukaRsi/KukaEki/EthernetXml/InLaserModbus） | 基类改 `protected readonly string Tag` + `protected CommChannelBase(string tag)` + `protected Log(...)`；五个实现类删除自有 `Tag`/`Log`，构造函数以 `base("本类名")` 注入标签 |
| 2 | `KukaEkiComm.Send(string)` 返回 `bool`，与基类 `virtual void Send(string)` 同参不同返回类型 → 隐式隐藏（CS0108） | 补 `new` 关键字显式声明隐藏 |
| 3 | `KukaRsiComm` / `KukaEkiComm` 两个构造函数各自重复写一套默认值 | 无参构造函数改为 `: this(默认参数)` 链式调用，删除重复赋值 |

> 与 [[lessons/StepDrivenWorkflowPitfalls]] 七.3（Tag 遮蔽 / 日志出口发散）同型：基类提供能力却设为 `private`，必然逼出子类各抄一份。
