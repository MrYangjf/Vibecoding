---
title: ADR-026 KUKA RSI 单一通道通讯现行决策（语义重写 · 数值化指令承载 · Tool 三标量 · 格式文档驱动 · 配置目录；整合原 050/052/053/054/055）
date: 2026-09-15
updated: 2026-10-21
tags: [决策, 通讯, KUKA, RSI, 单一通道, 数值化指令, 格式驱动, merged, ADR-026]
status: accepted
merged_from: [ADR-050, ADR-052, ADR-053, ADR-054, ADR-055]
---

# ADR-026：KUKA RSI 单一通道通讯现行决策（语义重写 · 数值化指令承载 · Tool 三标量 · 格式文档驱动 · 配置目录）

> 本页为整合页（2026-09-17），吸收并取代原 ADR-026 / ADR-026 / ADR-026 / ADR-026，消除其中被推翻的中间态。历史时间线见「沿革」。

## 现行决策

### 1. RSI 数据方向按 KUKA RSI 3.3 官方语义重写（12ms 收发、双线程）

[[decisions/ADR-025-CommModuleRefactor]] 落地后的 `KukaRsiComm` 原本保留「上位机=传感器」旧修正模型（上位机组 `<Rob>` 包、解析 `<RKorr>` 修正），与官方语义方向相反，已重写：

- 机器人以 IPO 周期（12ms/4ms）UDP 发送 `<Rob TYPE="KUKA"><RIst X..C/><IPOC/></Rob>`；
- 上位机解析进 `RsiRobotPacket`（RIst + IPOC + ToolX/Y/Z），触发 `RsiDataReceived`（`RobotData.RIst` 同步填充，既有消费方兼容）；
- 上位机回复 `<Sen Type="SENTYPE"><Tech .../><IPOC 原样回传/></Sen>`，回复包发往**收包远端端点**（机器人主动发包、本机被动回复；`RobotIP/RobotPort` 仅作参考信息）；
- **接收线程（RSI-Receive）与回复线程（RSI-Send）分离**（均 Highest 优先级）：回复线程轮询缓存独立发送，业务计算偶发超时也能用上一帧有效值回复（配合机器人端 HOLDON=1）；
 - ⚠️ **2026-10-21 实现校正**：~~回复线程按固定 `Sleep(1)` 自驱轮询~~ → **收包信号驱动的一包一回**（`AutoResetEvent`：收包置位、回复线程取缓存组包、`Stop` 唤醒退出）。理由是机器人主动发包模型下盲发会把重复 IPOC 洪泛给机器人；「回复线程独立取缓存值」这一语义不变，见 [[decisions/ADR-074-RsiNumericProtocolImplementation]]「落地复核」§1/§3 与 [[lessons/FormatDrivenPacketParsingPitfalls]]。
- 旧修正语义接口删除（`SendRobotData`/`ReceiveCorrectionData`/`TryReceiveCorrectionData`/`SerializeRobotData`/`DeserializeCorrectionData`，外部消费者 0）；`KUKACorrectionData` 类型保留仅供事件参数兼容。

### 2. RSI 与 EKI 互斥单通道（推翻 050 初版双通道）

用户上机实测证实：**RSI 与 EKI 是互斥关系，不可能同时打开**（机器人通讯设置面板本就有互斥 radio，默认 RSI-12ms；RSI 已启动后 EKI 连接超时 20 秒才报失败，拖慢初始化且语义错误）。

- `ConnectRobot()`/`DisconnectRobot()` 只操作当前 `RobotCommMode` 对应的通道，删除 RSI 分支中的 EKI 辅助通道打开/关闭；
- `SendRobotData`（指令文本）仅在 EKI 模式生效；RSI 模式下无指令通道（未连接时记警告并附当前模式）；
- `DeviceControlWork` 侧 `OnRobotDataReceived` 已加 EStr 空串守卫（RSI 坐标包不进指令解析），握手链路在 RSI 默认模式下不依赖 EKI、零改动；
- 如未来需要在 RSI 模式下发指令，须经机器人端 Tech 字段扩展，**不恢复双通道**；
 - ⚠️ **2026-10-20 预留条款已执行**（业主裁定「统一使用 RSI，EKI 不再默认」）：按本条款规划 RSI 统一通讯方案——上行 RX 指令走 Rob 包 `DEF_EStr`（关键词表唯一 STRING 载体），下行 TX 指令编码数值走 Sen 包 Tech T16~T18（指令码/载荷/序号），焊接参数 T11~T15，EKI/EthernetKRL 降为备用（RobotCommMode=1 非默认）；控制链（CommandCore→虚拟IO→状态机）零改动。方案文档、机器人控制侧可部署配置文件（`rsi.Xml`，2026-10-21 已更名为 `WeldControlConfig.xml`；与格式文档 1:1 对应）与双端配置 XML 见交付目录 `robot-comm-spec/`（代码改造清单 7 项待实施）。
- `RobotCommModeType.RSI = 0` 维持默认。

> ⛔ **2026-10-21 裁定升级为「RSI 唯一通道」**（业主指令「清理 KRL 的相关文档，项目要求使用的是 RSI」）：
> ~~RSI/EKI 互斥二选一~~ → **只保留 RSI**。EKI / EthernetKRL 通道**整体退役**，代码侧清理范围：
> `KukaEkiComm` / `EthernetXmlComm` 机器人分支 / `RobotCommMode` 二选一逻辑（固定为 0）/
> UI 通讯页 EKI radio 与 `IsEKIConnected` 判定 / `Config\Comm\KUKARobot_EKI_XML\` 目录。
> 文档侧同步清理：`api/KUKARobot.md` 的 EKI 章节（§3 EKICommunication、§4.4~4.6 EKI 配置与数据类型、
> EKI 数据交换示例、§6.5 EKI XML 交换机制详解、§6.6 RSI vs EKI 对比）**整节删除**，
> `modules/KUKARobot.md` 与 `wiki/index/index.md` 的 EKI 表述同步修订。
>
> ⛔ **2026-10-21 上行指令承载方式修正（推翻 2026-10-20 预留条款中的 `DEF_EStr` 方案）**：
> 对照 KST_RSI_33_zh.pdf V4 §7.4.2 核实——**SEND 段 `TYPE` 仅 `BOOL`/`DOUBLE`/`LONG`，不含 `STRING`**；
> 且 §7.4.6 中 `DEF_EStr` 属**写入**关键词（只能用于 RECEIVE 侧），**不是上行通道**。
> ⇒ ~~上行 RX 指令走 Rob 包 `DEF_EStr` 字符串~~ **不成立**，机器人侧 RSI 编辑器不会生成对应信号。
> ⇒ 现行裁定：**上行 RX 指令数值化** `RxCmd`(LONG, INDX=4) + `RxPayload`(DOUBLE, INDX=5)；
> **下行 TX 指令改用具名元素** `TxCmd`(LONG, INDX=6) / `TxPayload`(DOUBLE, INDX=7) / `TxSeq`(LONG, INDX=8)，
> **不再使用 `DEF_Tech.T11~T110` 内部编号**（Tech 编号为 RSI 固定语义，无自定义命名空间、版本敏感）。
> 焊接参数同样由具名元素承载：`WeldPower`(1) / `WireSpeed`(2) / `CutWire`(3) / `WeldSpeed`(4) / `WeaveAmp`(5)。
>
> ⚠️ 上述修正**推翻** 2026-10-20 执行注记中「上行走 `DEF_EStr`、下行 Tech T16~T18」的部分，
> 但**保留**其「通讯通道统一 RSI、EKI 不再默认」的裁定方向。
>
> **交付物（本轮）**（目录 `robot-comm-spec/`）：
> `WeldControlConfig.xml`（机器人端以太网连接 XML，可部署运行文件）+ 信号流三件套 `WeldControl.rsi` / `WeldControl.rsi.xml` / `WeldControl.rsi.diagram` / `配置_机器人(KUKA)_RSI统一通道WeldControl.xml`（变量说明版）/
> `配置_本机(上位机)_RSI统一通讯配置.xml` / `机器人通讯指令表.xlsx`（双向包解析 + RX/TX 编码表 + 双端 XML 清单）/
> `RSI部署与联调测试手册.html`（含 5 件套清单 + 接线清单 + 14 项联调验收判据 + 代码侧 6 项待落地，已合并原接线清单与方案设计内容）。

### 3. 回复值线程安全写入与 Manager 门面（SetReplyValues / UpdateRobotWeldParams）

- 回复值经线程安全 `SetReplyValues(激光功率, 送丝速度)` 写入回复线程缓存；
- Manager 门面 `UpdateRobotWeldParams(功率, 送丝)` 供上层调用，内部走 `SetReplyValues`。

### 4. 机器人端 XML 每次启动自动生成

ADR-026 发现 `SaveRobotRsiXml()` 全库零调用点，机器人端配置文档从未生成。现行裁定：

- `InitializeRobotComm` 装载 RSI 配置（含 CYCLE、收发格式节）后调用 `SaveRobotRsiXml()`，每次启动自动生成；
- 输出 `Config\Comm\KUKARobot_RSI_XML\WeldControlConfig.xml`（CONFIG：HOST_IP/HOST_PORT/SENTYPE + SEND：`DEF_RIst` + Tool 三标量 + RECEIVE：`DEF_Tech.C1`/`DEF_Tech.C2` HOLDON=1，全部 `INDX="INTERNAL"` 或输入端编号）+ `WeldControlSendFormat.xml`（见决策 7），二者一并拷贝到机器人控制器 `C:\KRC\ROBOTER\Config\User\Common\SensorInterface\` 使用；
- 生成参数取 Manager 自持 `RobotServerXdoc`（ADR-006 H7：HOST_IP/HOST_PORT/SENTYPE/CYCLE 等同居该 Xdoc）。

### 5. Tool.X/Y/Z 三标量 INDX 连续编号（推翻 052 的 DEF_Tool 方案）

对照 KST_RSI_33_zh.pdf §7.4.5/7.4.6 核实：`DEF_Tool` **不是合法关键词**（关键词表只有 DEF_RIst/DEF_RSol/DEF_AIPos/DEF_ASPos/DEF_EIPos/DEF_ESPos/DEF_MACur/DEF_MECur/DEF_Delay/DEF_Tech.C1~C6/DEF_Tech.T1~T6/DEF_EStr，加载会被控制器拒绝），且**一个 ELEMENT 只承载一个标量**（ETHERNET 输入端 INDX=1…64 须连续编号，手册示例 FTC.Fx~FTC.Mz 正是每分量一个 ELEMENT）。现行裁定：

- SEND 节配置 `Tool.X` / `Tool.Y` / `Tool.Z`（TYPE=DOUBLE）分别映射 ETHERNET 输入端 **1 / 2 / 3**（INDX 连续编号）；`DEF_RIst` 保留 INDX="INTERNAL"；RECEIVE 节 DEF_Tech.C1/C2 均为合法写入关键词不受影响：

```xml
<SEND>
 <ELEMENTS>
 <ELEMENT TAG="DEF_RIst" TYPE="DOUBLE" INDX="INTERNAL" />
 <ELEMENT TAG="Tool.X" TYPE="DOUBLE" INDX="1" />
 <ELEMENT TAG="Tool.Y" TYPE="DOUBLE" INDX="2" />
 <ELEMENT TAG="Tool.Z" TYPE="DOUBLE" INDX="3" />
 </ELEMENTS>
</SEND>
```

- 按手册「TAG 含点分组的属性书写形式」规则（示例 TAG=`FTC.Fx` → `<FTC Fx=.../>`），TAG=`Tool.X/Y/Z` 生成 `<Tool X="..." Y="..." Z="..."/>`；
- 上位机 `RsiRobotPacket` 增 `ToolX/ToolY/ToolZ`，解析 `//Tool` 节点属性 X/Y/Z（节点缺失保持 0 容错）；RIst 主定位元素缺失仍返回 null；数据经 `LatestPacket` 与 `RsiDataReceived` 事件透出；
- **机器人端接线责任**：机器人工程师在 WorkVisual RSI 信号图中，把焊接时基于车身坐标计算的工具 X/Y/Z 信号接到 ETHERNET 输入端 1/2/3；上位机无法通过 XML 强制机器人发送什么，只能约定结构与输入端编号。未接线时 ToolX/Y/Z 恒为 0（容错不报错）；
- 输入端编号 1/2/3 被工具坐标占用，后续 SEND 节新增自由元素须从 INDX=4 连续编起。

### 6. RSI 通讯周期 CycleMs 可配置（超时 = 2×CycleMs、5 周期节流告警）

- **语义**：实际通讯周期由机器人控制器 IPO 模式决定（IPO=12ms / IPO_FAST=4ms），上位机不可改变；上位机侧 `CycleMs` 是**预期周期**，仅用于接收超时判定，须与机器人端实际周期一致；
- **真相源**：`RobotServerXdoc` 增 `CYCLE` 元素（默认 12），与 HOST_IP/HOST_PORT/SENTYPE 同居 Manager 自持 Xdoc（H7）；
- **链路**：`CommPage`「通讯周期」下拉（4/12/24 ms，AntdUI.Select）→ Manager 门面 `SetRsiCycleMs(int)`（写 `RsiComm.CycleMs` + `SetElementValue("CYCLE")` + `SaveXdocument()`）；`InitializeRobotComm()` 读 CYCLE 装载；
- **超时判定**：`Start()` 设接收套接字 `ReceiveTimeout = 2×CycleMs`；`ReceiveLoop` 对 `SocketError.TimedOut` 分流到 `CheckReceiveStall()`——连续 `StallWarnCycles`(5) 周期无包告警一次（节流），恢复收包复位并记「RSI 数据流已恢复」；尚未收到首包不判定；
- **不做**：不往机器人端 `WeldControlConfig.xml` 写周期字段（KUKA RSI 配置 XML 无此契约元素）。

### 7. 收发格式文档驱动（SEND_FORMAT / REPLY_FORMAT、WeldControlSendFormat.xml）

> ⚠️ **2026-10-21 更新**：本节约定的 **Tech 属性名 `T11~T19`/`T110` 已被具名元素取代**（`WeldPower`/`WireSpeed`/`CutWire`/`WeldSpeed`/`WeaveAmp`/`TxCmd`/`TxPayload`/`TxSeq`），理由见决策 2 的 2026-10-21 修正。格式文档驱动**机制本身不变**（改文档即改收发行为）。

用户裁定：收发不得依赖代码内硬编码字符串，机器人与上位机都以 XML 固定格式收发，双方持有的文档须明确定义该格式，默认组包与解析都以格式文档内容为准。

- **上位机一份文档**：`RobotServer.xml` 扩展 `SEND_FORMAT`（机器人发送 Rob 包模板，解析依据）与 `REPLY_FORMAT`（上位机回复 Sen 包模板，组包依据）两节；构造期 `EnsureRsiFormatSections` 缺失即补内置默认。节下首个子元素为包根（Rob/Sen），其属性为类型标识，子节点定义包结构；无属性无子元素的节点为文本节点形式（IPOC），占位值存于元素文本；
- **机器人端两份文档**：`SaveRobotRsiXml` 在 `WeldControlConfig.xml`（配置）之外增生成 **`WeldControlSendFormat.xml`**（格式契约，SEND_FORMAT + REPLY_FORMAT 同构），二者一并拷贝到机器人侧；
- **格式驱动收发**：新增 `RsiPacketFormat` / `RsiFormatElement` / `RsiFormatAttribute` 模型与 `KUKAXMLConfig.ParseFormatSection` / `LoadPacketFormat`；`KukaRsiComm.SendPacketFormat` / `ReplyPacketFormat` 由 `InitializeRobotComm` 从 RobotServer.xml 装载——
 - 解析 `ParseRobotPacket(xml, sendFormat)`：按格式元素遍历取节点，RIst/Tool 按格式**属性顺序**绑定数值，IPOC 取文本；RIst 主定位元素缺失返回 null；
 - 组包 `BuildReplyXml(replyFormat, …)`：按格式模板 StringBuilder 拼接，**属性占位值约定**：`激光功率`=实时激光功率、`送丝速度`=实时送丝速度、`原样回传`/`时间戳`=IPOC、其余按字面量输出；根 Type 属性值缺省时用 SENTYPE；
 - 格式节缺失或解析失败回退内置默认格式（`CreateDefaultSendFormat` / `CreateDefaultReplyFormat`），旧静态签名保留为薄包装，零破坏；
- **Tech 属性名约定**：Tech XML 对象属性固定 10 个——T11~T19、T110（"T1"+序号 1~10），T11=激光功率、T12=送丝速度；default 构造禁止 `T13…T110` 连号误推（会生成 T20~T109 非法属性名）；
- **改格式即改行为**：用户编辑 RobotServer.xml 格式节（或 CommPage「打开配置」）后，下次 `InitializeRobotComm` 重新装载生效，无需改代码；格式变更超出语义绑定时（新增元素消费）才需登记代码；
- **约束**：语义绑定（RIst/Tool/IPOC/占位值关键字）仍由代码登记，纯改文档只能调整「结构与字面量」；解析按属性顺序绑定，格式文档中属性顺序不可随意调换（RIst 六属性、Tool 三属性）。`WeldControlConfig.xml` 内的格式注释保留（人读冗余，机器忽略）。

### 8. 通讯配置目录统一 Config\Comm\<通道>_XML\ 与旧路径幂等迁移

`XdocumentReaderWriter` 原硬编码 `BaseDirectory\Config\XML\`，通讯与非通讯配置混放。现行裁定：全部通讯 XML 落 `Config\Comm\<通道>_XML\`（相对程序基目录）：

| 通道 | 目录 | 文件 |
|---|---|---|
| 机器人 RSI | `Config\Comm\KUKARobot_RSI_XML\` | RobotServer.xml、WeldControlConfig.xml、WeldControlSendFormat.xml（机器人端） |
| 通用 TCP | `Config\Comm\Tcp_XML\` | Server.xml、Client.xml、Send.xml、Recive.xml |
| PLC | `Config\Comm\PLC_XML\` | PLC.xml |
| Modbus | `Config\Comm\Modbus_XML\` | Modbus.xml |
| 本 Manager 主配置 | `Config\Comm\Communication_XML\` | CommunicationConfig.xml |

- `XdocumentReaderWriter` 新增双参构造 `(string relativeDirectory, string xmlName)`（相对基目录，自动建目录），单参构造委托化、行为不变——**双参构造是子目录的唯一入口**；
- 非通讯配置（DeltaMotionConfig / WeldHeadSlave / WeldParamControl 等）继续留在 `Config\XML\`，不在本 ADR 范围；⚠️ **2026-09-21 更新**：该「继续留在 `Config\XML\`」的裁定已废止——非通讯配置同样按 [[decisions/ADR-033-ConfigArchitectureStandard]] 三段式落位（见 [[decisions/ADR-033-ConfigArchitectureStandard]]）；
- **旧路径迁移**：`CommunicationManager.MigrateLegacyCommXml()` 启动时幂等迁移——旧 `Config\XML\` 下 10 个通讯文件 `File.Move` 到新目录；目标已存在时仅删除旧文件；失败仅告警不阻塞；对全新环境无副作用（**2026-09-21 演进**：`MigrateLegacyCommXml()` 已删除，通讯与非通讯的历史搬迁统一收口为 `FileOperate/ConfigPathMigrator.cs`，由 `Program.Main` 首步调用）；
- **迁移必须先于任何 Xdoc 构造**（构造会在新路径自动创建默认模板，抢先会吞掉旧文件里的用户配置）。

### 9. 设置与启停解耦

- 模式 radio / 通讯周期下拉 / 打开配置始终可用（未启用机器人通讯也应能预配置）；仅「连接 / 断开」按钮跟随启用开关；
- `SetPanelEnabled` 辅助方法删除（仅 `CommPage.ApplyEnableState` 一处使用）。

### 10. RobotServer.xml 字段语义

| 字段 | 含义 | 用途 |
|---|---|---|
| `IP` | 机器人 KLI 地址（参考） | RSI 模式仅作参考信息（机器人主动发包，目标为 HOST_IP） |
| `PORT` | 本机 RSI 监听端口 | RSI UDP 绑定端口（默认 49152） |
| `HOST_IP` | 上位机本机 IP | 写入机器人端 XML CONFIG 节，机器人据此发送 RSI 包；**须与机器人同一网段，仅末位不同**（占位值 192.168.1.10/192.168.1.5 部署前按实网替换） |
| `HOST_PORT` | 上位机监听端口 | 与 PORT 配套，机器人发包目标端口 |
| `SENTYPE` | 传感器系统标识 | 须与机器人端信号图 SENTYPE 一致（WeldControl） |
| `CYCLE` | RSI 预期周期 ms | 与机器人 IPO 模式一致（12/4），用于接收超时判定 |

## 被推翻的中间态

- ~~**ADR-024 初版：RSI 主 + EKI 辅双通道**（RSI 模式下尽力打开 EKI 作指令通道，双通道一并开闭）~~ → 由 ADR-026 推翻：RSI 与 EKI 互斥不可能同时打开，改为互斥单通道，不恢复双通道。
- ~~**2026-10-20 预留条款：上行 RX 指令走 `DEF_EStr` 字符串通道 / 下行走 Tech T16~T18**~~ → 由 2026-10-21 修正推翻：SEND 段禁 STRING（§7.4.2），`DEF_EStr` 属写入关键词（§7.4.6）不可上行；改为 `RxCmd`/`RxPayload` 数值化上行 + 具名元素下行。
- ~~**ADR-026：机器人端 SEND 节增 `DEF_Tool` 元素**（意图一个 TAG 发送工具 X/Y/Z）~~ → 由 ADR-026 推翻：`DEF_Tool` 非合法关键词且一个 ELEMENT 只承载一个标量，改为 Tool.X/Y/Z 三标量映射输入端 1/2/3。

## 沿革

- **2026-09-15 · ADR-024 初版**：用户裁定「以 RSI 为主要模式」+「机器人坐标发送给我，我发给机器人送丝速度和激光功率」；`KukaRsiComm` 按 RSI 3.3 官方语义重写，设计 RSI 主 + EKI 辅双通道（后被推翻），机器人端 XML 归 Manager 生成，监听端口语义修正（PORT=本机监听）；同日增补 CycleMs 可配置。
- **2026-09-15 · ADR-026**：通讯配置目录统一 `Config\Comm\<通道>_XML\` 与幂等迁移；RSI Tool 上行初版用 `DEF_Tool`（后被推翻），上位机解析 `//Tool` 容错 0。
- **2026-09-15 · ADR-026**：用户上机实测后裁定 RSI 与 EKI 互斥单通道，推翻 050 双通道；机器人端 XML 改为每次启动自动生成；设置与启停解耦；澄清 RobotServer.xml 字段语义。
- **2026-09-15 · ADR-026**：对照 RSI 3.3 手册核实 `DEF_Tool` 非法，改为 Tool.X/Y/Z 三标量 INDX 1/2/3 连续编号；解析侧零改动；明确机器人端接线责任与未接线恒 0 容错。
- **2026-09-16 · ADR-026**：收发格式文档驱动——RobotServer.xml 增 SEND_FORMAT/REPLY_FORMAT，机器人端增 WeldControlSendFormat.xml，组包/解析由格式文档驱动，Tech 属性名约定修正为 T11~T19+T110。
- **2026-10-21 · RSI 唯一通道 + 指令数值化**：业主指令「清理 KRL 的相关文档，项目要求使用的是 RSI」⇒ 通讯通道由「RSI/EKI 互斥二选一」升级为「RSI 唯一通道」，EKI/EthernetKRL 代码与文档整体退役；同时对照 KST RSI 3.3 §7.4.2/§7.4.6 推翻 2026-10-20 的 `DEF_EStr` 上行方案，改为 `RxCmd`/`RxPayload` 数值化上行 + `TxCmd`/`TxPayload`/`TxSeq` 具名元素下行；产出 `robot-comm-spec/` 全套交付物（**2026-10-21 补齐为机器人端 5 件套**：信号流三件套 + 以太网连接 XML + 机器人程序示例；含通讯指令表 xlsx、部署联调手册 HTML）。
- **2026-09-17 · 本页整合**：ADR-026/053/054/055 并入本页，删除被推翻的中间态表述，收拢全部现行裁定；整合后 status: accepted、tags 含 merged、`merged_from` 指向四个被并页。

## 后果小结

- 正面：RSI 链路与 KUKA 官方契约一致可联调；机器人端配置与格式文档一键生成且每次启动同步；通讯配置按通道分目录隔离；格式单一真相源落在文档里，现场改文档即可调整收发结构；初始化不再被 EKI 超时拖 20 秒。
- 约束（2026-10-21 更新）：RSI 模式下**已有**上下行指令通道（数值码 `RxCmd`/`TxCmd`），不再需要 EKI；机器人端需部署 RSI 三件套（`.rsi` / `.rsi.xml` / `.rsi.diagram`）、完成输入端 1/2/3 与输出端 1~8 接线并同步两份 XML；上机联调时验证 IPOC 回传、HOLDON 行为与指令沿触发去重；EKI 退役需同步清理代码侧引用（§决策 2 清理范围）。

## 背景

（待补：本决策要解决什么问题）

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 后果

### 正面
- （待补）

### 负面
- （待补）

## 相关页面

- [[decisions/ADR-025-CommModuleRefactor]]（三层结构前提）
- [[decisions/ADR-006-ModuleOrganizationPatternStandard]]（H6/H7）
- [[decisions/ADR-030-WeldHeadSlaveDeviceUnderMotionControl]]
- [[modules/Comm]] / [[modules/KUKARobot]] / [[api/KUKARobot]]
- 原档：`raw/knowledge/KUKA_OPT/KST_RSI_33_zh.pdf`、用户开发指南《KUKA_RSI通讯开发指南.md》（D:/飞书文档/）
- 交付物目录：`robot-comm-spec/`（机器人端 5 件套 `WeldControl.rsi` / `.rsi.xml` / `.rsi.diagram` / `WeldControlConfig.xml` / `.src` + 双端配置 XML + 通讯指令表 xlsx + `RSI部署与联调测试手册.html`）
- 已并入本页（纯文本存档）：ADR-026-CommConfigDirectoryAndRsiToolUplink、ADR-026-RsiEkiExclusiveChannel、ADR-026-RsiToolXYZScalarIndx、ADR-026-RsiFormatDrivenPackets
