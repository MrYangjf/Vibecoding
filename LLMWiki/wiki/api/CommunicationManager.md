---
title: CommunicationManager API 参考（通讯管理器 · 模块唯一门面）
date: 2026-09-17
tags: [API, 通讯, 管理器, 门面, KUKA, RSI, S7, Modbus, 单例, ADR-011, ADR-026, ADR-026, ADR-026]
source: AdaWeldSystem/Comm/Communication/CommunicationManager.cs
---

# CommunicationManager API 参考

> Comm 模块**唯一对外门面**：统一持有五类通讯通道实例，管理通讯配置持久化与机器人 RSI 门面。
> ⛔ **2026-10-21 ADR-074**：机器人通讯通道**唯一为 RSI**，`KukaEkiComm` 整文件已删除（ADR-026 决策 2 的实施）。
> **位置**：`AdaWeldSystem/Comm/Communication/CommunicationManager.cs`
> **命名空间**：`AdaWeldSystem.Comm.Communication`
> **沿革**：2026-09-14 Comm 重构后成为通讯唯一门面（原 KUKARobotManager / TCPIPComm 门面并入，[[decisions/ADR-025-CommModuleRefactor]]）。
> 模块背景见 [[modules/Comm]]，指令与协议底层见 [[api/CommandCore]]。

---

## 定位

```
外部（各工作流 / UI 页 / WeldParamManager 位姿消费）
  ↓ 只认 GlobalCommData.mCommunicationManager（静态字段持有，SystemComm 初始化时创建）
CommunicationManager（通道持有者 + 配置持久化 + 机器人门面）
  ├─ EthernetComm   （EthernetXmlComm，通用 TCP，XML 文档交互）
  ├─ RsiComm        （KukaRsiComm，KUKA RSI UDP 实时通道，**唯一机器人通道**）
  ├─ S7Comm         （SiemensS7Comm，西门子 S7 备用降级通道，延迟初始化）
  └─ ModbusComm     （InLaserModbusComm，英莱 Modbus，延迟初始化，与英莱 SDK 互斥）
```

- **实例持有方式**：本类**非单例**，构造函数 public；唯一实例由 `GlobalCommData.mCommunicationManager` 静态字段持有（`Comm/SystemComm/SystemComm.cs` 创建）。
- **RSI 单一通道**（ADR-026 → 2026-10-21 ADR-074）：`RobotCommMode` 恒返回 RSI（setter 也只落 RSI 值），门面方法只操作 RSI 通道。
- **实现标准 `IDisposable.Dispose()`**（ADR-001/020），依次释放五个通道实例。
- 机器人位姿归通讯层持有：RSI 接收线程写 `RobotPoseSnapshot` 快照，消费方（焊缝跟踪侧）只读。

## 公共成员

### 机器人门面（RSI 单一通道）

| 成员 | 签名 | 职责 |
|---|---|---|
| `RobotDataReceived` | `event EventHandler<KUKADataReceivedEventArgs>` | RSI 数据统一透出事件 |
| `ConnectRobot` | `bool ()` | 连接机器人 RSI 通道（`Start()`）；成功即清位姿有效标志，首包到达前不消费旧快照 |
| `DisconnectRobot` | `bool ()` | 断开机器人 RSI 通道并返回关闭结果（供调试界面记录成功/失败）；同时把 `HasRobotPose` 置 false |
| `SendRobotData` | `void (KUKARobotData data)` | 下发机器人指令（取 `EStr` 字段作指令常量名，内部转数值码） |
| `SendRobotCommand` | `void (int txCmd, double txPayload = 0.0)` | **按数值码下发下行指令**（`TxCmd` + `TxSeq` 自增），只写回复缓存，下一帧生效 |
| `SendRobotCommandByName` | `bool (string command)` | 按指令常量名下发（内部查 `CommandCore.CommandToTxCodeValue`） |
| `RobotConnected` | `bool { get; }` | **监听态**：RSI 监听已启动（≠机器人在线） |
| `IsRobotOnline` | `bool { get; }` | **在线态（2026-10-22）**：以实际收包为准（收到过包 + 最近包未超时） |
| `RsiComm.LocalIp` | `string` | 本机监听 IP，`InitializeRobotComm` 从 `HOST_IP` 注入；`Start` 绑定该地址并在无对应网口时写错误日志 |
| `RsiComm.LastError` | `string { get; }` | 最近一次启停失败原因（成功时清空）；调试界面启停日志与状态标签直接展示 |
| `LastRobotReceiveTime` | `DateTime { get; }` | 最近一次收到机器人包的时间（未收到过为 `DateTime.MinValue`） |
| `HasRobotPose` | `bool { get; }` | 是否已收到机器人位姿（锁保护） |
| `TryGetRobotPose` | `bool (out RobotPoseSnapshot pose)` | 取最近一帧位姿快照（未收到过返回 false） |
| `UpdateRobotWeldParams` | `void (double laserPower, double wireSpeed, double cutWireSignal = 0.0, double weldSpeed = 0.0, double weaveAmp = 0.0)` | 写入回复给机器人的焊接参数（**5 个具名元素通道**：WeldPower/WireSpeed/CutWire/WeldSpeed/WeaveAmp） |
| `SetRsiCycleMs` | `void (int cycleMs)` | 设置 RSI 通讯周期并持久化到 RobotServer Xdoc（12=IPO / 4=IPO_FAST / 24=IPO×2） |
| `RsiCycleMs` | `int { get; }` | 当前 RSI 通讯周期（毫秒），供 UI 展示 |
| `NeedHeartbeat` | `bool { get; }` | **2026-11-17 阶段 6**：是否启用分级心跳日志（INI `NeedHeartbeat`，默认 true）；关闭只停日志与分级，`IsRobotOnline` 与界面显示不变 |
| `EnsureRobotChannelHealthy` | `bool ()` | **2026-11-17 阶段 6**：通讯层自愈入口。`IsRobotEnabled` 且 RSI 未监听时，按 5 s 冷却执行 `InitializeRobotComm + ConnectRobot`，成功/失败各一条日志；由指令线程每拍调用。**2026-11-17 ADR-107**：指令线程（含本自愈）改在初始化链结束后才启动，初始化期间不会有自愈重连 |

> **2026-10-22 默认 IP**：RSI 默认机器人 KLI = `192.168.10.100`、本机 = `192.168.10.50`（`KukaRsiComm` 构造默认 + `CommunicationManager` `EnsureConfigElementExists` 默认 + 交付 XML 三处同步）。

> **2026-10-22 结构/端口语义**：RobotServer 连接参数统一挂 `<CONFIG>`（旧根级结构在 `InitializeCommunication` 时由 `EnsureRobotServerConfigSection` 自动迁移）；`HOST_PORT` = 本机监听口（缺失回落 `PORT`），`PORT` = 机器人发送口并写入 `RsiComm.RobotPort`；通道开关（`RobotEnabled`/`RobotCommMode`）仍归 Comm INI，不在 XML。

### 通道管理

| 成员 | 类型 | 职责 |
|---|---|---|
| `EthernetComm` | `EthernetXmlComm { get; }` | 通用 TCP 以太网通讯（从 Server/Client Xdoc 装载连接参数） |
| `RsiComm` | `KukaRsiComm { get; }` | KUKA RSI 通道实例（构造即创建并订阅数据事件） |
| `S7Comm` | `SiemensS7Comm { get; }` | S7 备用降级通道，由 `InitializePlcComm()` 按配置创建 |
| `ModbusComm` | `InLaserModbusComm { get; }` | 英莱 Modbus 通道，由 `InitializeModbusComm()` 按配置创建 |
| `InitializeRobotComm` | `void ()` | 从 XML 装载 RSI 参数；装载前先校验 `SEND_FORMAT`/`REPLY_FORMAT` 契约（旧版 Tech 节原地升级，ADR-026 → ADR-074），再生成机器人端 RSI XML |
| `InitializePlcComm` / `InitializeModbusComm` | `void ()` | 从 PLC_XML / Modbus_XML 读 IP/Rack/Slot 等并创建实例 |

### 配置与持久化

| 成员 | 签名 | 职责 |
|---|---|---|
| `Load` / `Save` | `void ()` | 读写 `Config/Comm/Communication_XML/CommunicationConfig.xml`（`CommunicationConfig` 列表） |
| `AddOrUpdate` | `void (CommunicationConfig config)` | 按名添加或覆盖配置并落盘 |
| `Remove` | `void (string name)` | 按名移除配置并落盘 |
| `GetByName` / `GetByType` | `CommunicationConfig (string)` / `List<CommunicationConfig> (CommunicationType)` | 按名 / 按类型查询 |
| `Configs` | `List<CommunicationConfig> { get; }` | 全部配置（只读副本） |
| `SaveRobotRsiXml` | `string ()` | 生成机器人端 RSI 配置与收发格式文档（WeldControlConfig.xml，**SEND=DEF_RIst+Tool.X/Y/Z+RxCmd+RxPayload / RECEIVE=8 具名元素**，拷贝到控制器使用）；CONFIG.PORT 取本机监听口 `RsiComm.LocalPort`，`HOST_PORT` 仅作核对并告警不一致。**2026-11-17 ADR-107**：写盘加 `_rsiXmlLock` 互斥锁，锁内写同目录临时文件后 `File.Replace` 原子替换，瞬态占用做 5 次 × 60ms 退避重试（`WriteXmlWithRetry`）|
| 8 个 `XdocumentReaderWriter` | `ServerXdoc` / `ClientXdoc` / `SendXdoc` / `ReciveXdoc` / `RobotServerXdoc` / `RobotClientXdoc` / `PlcXdoc` / `ModbusXdoc` | 各通道 XML 配置读写器（`Config/Comm/<通道>_XML/`） |

- `CommunicationType` 枚举：`GeneralTcp` / `SiemensS7` / `KUKA_RSI` / `KUKA_EKI`（✅ 已退役，枚举值保留供历史配置读取）/ `ModbusTcp`。
- INI 开关（`Config/Comm/Communication_INI/CommunicationSettings.ini`，Display 节）：`ShowCommLog` / `ShowRobotCommLog` / `ShowPlcCommLog` / `ShowModbusCommLog` / `IsPlcEnabled` / `IsRobotEnabled` / `IsGeneralEnabled` / `RobotCommMode`。
- **路径迁移**：全部通讯 XML 落 `Config\Comm\<通道>_XML`（2026-09-15）。历史平铺 `Config\XML\`、`Config\INI\` 的搬迁自 2026-09-21 起统一由 `FileOperate/ConfigPathMigrator.cs`（`Program.Main` 首步）承担，原 `MigrateLegacyCommXml()` 已删除，**迁移先于任何 Xdoc 构造**。

## 机器人指令与焊参下发（2026-11-17，阶段 7 / ADR-104）

| 成员 | 行为 |
|---|---|
| `SendRobotCommand(int txCmd, double txPayload)` | 转 `RsiComm.SendTxCommand`，只写下行缓存并自增 `TxSeq`；下一帧由回复线程发出，缓存值不清则持续重发 |
| `ClearRobotCommand()` | 转 `RsiComm.ClearTxCommand()`，把 `TxCmd/TxPayload` 归 0；只撤报警标志，不触碰焊参缓存与收发周期 |
| `UpdateRobotWeldParams(...)` | 转 `RsiComm.SetReplyValues`，只写 5 个具名元素缓存；不调用即载荷冻结，通道仍按 `CycleMs` 回写 |
| 通道与载荷 | 回写由机器人收包信号驱动（一包一回），与载荷是否更新解耦，**不存在**「不发值即断联」路径 |

- 关联：[[decisions/ADR-104-rsi-channel-payload-freeze-alarm-stop]] · [[api/DeviceControlWork]] · [[modules/Comm]]

## 约束

- ⛔ 外部不得绕过门面直接持有/操作通道实例。
- 位姿快照只读：`RobotPoseSnapshot` 为只读值对象，消费方不反向写入。
- 构造阶段日志系统未就绪，迁移失败静默重试，禁止在迁移路径调 `Log`。

---

## 相关页面

- [[modules/Comm]] — 模块说明（五通道架构与沿革）
- [[api/CommandCore]] — 指令与协议底层
- [[decisions/ADR-025-CommModuleRefactor]] — Comm 重构（唯一门面）
- ADR-026（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 多通道互斥双通道（2026-10-21 升级为 RSI 单一通道）
- ADR-026（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 格式驱动收发（SEND_FORMAT/REPLY_FORMAT）
- [[api/KUKARobot]] — KUKA 数据载体与历史沿革
- [[api/S7NetPlus]] — S7 底层库参考
