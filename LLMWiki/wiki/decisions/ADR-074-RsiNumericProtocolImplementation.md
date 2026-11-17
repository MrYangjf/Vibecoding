---
title: ADR-074 RSI 数值化协议落地（占位符扩展 11 项 · 数值码指令层 · 通道唯一化 · 通讯调试面板）
date: 2026-10-21
updated: 2026-10-21
tags: [决策, 通讯, KUKA, RSI, 数值化, 指令层, 调试面板, ADR-026, ADR-011]
status: accepted
---

# ADR-074：RSI 数值化协议落地

> 本页是 [[decisions/ADR-026-RsiSemanticRewriteAndDualChannel|ADR-026]] 决策 2 的**实施落地**记录（预留条款 → 已实施），
> 不推翻 ADR-026 的任何裁定，只补齐「协议契约已定 ⇒ 代码侧如何落地」这一段。

## 背景

ADR-026 于 2026-10-21 裁定：通讯通道唯一为 RSI；上行指令数值化 `RxCmd`(LONG)/`RxPayload`(DOUBLE)；
下行改用具名元素 `TxCmd`/`TxPayload`/`TxSeq` + 5 个焊参具名元素。
但**上位机代码侧仍是旧协议**（`KukaRsiComm` 只解析 RIst+Tool+IPOC；回复走 `Tech T11~T110`；
焊参走文本 `"P.. S.. V.. G.."`），且 EKI 通道代码仍在。

## 决策

### 1. 保持「格式文档驱动」架构，扩展占位符体系（不推翻硬编码）

ADR-026 决策 7 定的是「收发不得硬编码」。故**不**改为硬编码组包，而是把
`RsiPacketFormat` 的占位符从 5 项扩到 **11 项**：

| 占位名 | 载体元素 | 类型 |
|---|---|---|
| `激光功率` / `送丝速度` / `剪丝信号` / `焊接速度` / `振镜摆幅` | `WeldPower` / `WireSpeed` / `CutWire` / `WeldSpeed` / `WeaveAmp` | DOUBLE |
| `TX指令码` / `TX指令载荷` / `TX指令序号` | `TxCmd` / `TxPayload` / `TxSeq` | LONG / DOUBLE / LONG |
| `原样回传` / `时间戳` | `IPOC` | 文本 |
| （解析侧）`上行指令码` / `上行指令载荷` | `RxCmd` / `RxPayload` | LONG / DOUBLE |

⭐ **TAG 含 `.` → 属性形式（`Tool.X`）；不含 `.` → 元素形式（`RxCmd`）**（手册 §7.4.4）。

### 2. 修一个既有真 bug：回复线程未使用已装载的格式文档

`SendLoop` 原先调用 `BuildReplyXml(laserPower, ...)`（**内置默认**），
而 `ReplyPacketFormat`（从 `RobotServer.xml` 的 `REPLY_FORMAT` 装载）**从未被使用**
⇒ 格式驱动架构在运行时是失效的。本轮改为 `BuildReplyXml(ReplyPacketFormat, ...)`。

### 3. 指令层新增数值码映射，字符串常量保留

`CommandCore` 新增三组 API（ADR-026 枚举去重原则，映射表为**唯一权威**）：
- `RxCodeToCommandName(int)` / `TxCodeToCommandName(int)`：码 → 指令常量名
- `CommandToTxCodeValue(string)`：指令常量名 → 下行数值码
- `DescribeRxCode(int)` / `DescribeTxCode(int)`：码 → 中文释意（调试面板用）

⛔ 反查表 `CommandToTxCode` 由 `TxCodeToCommand` **反向生成**（不两处手写，防不同步）。
原 19 条字符串常量（`RX_*` / `TX_*`）**保留**：它们是日志与 UI 显示的载体，且
`CommandDescriptions` 释意字典仍以它们为键。

### 4. 收发方向各自明确

| 方向 | 承载 | 触发 |
|---|---|---|
| 上行（机器人→上位机） | `RxCmd` + `RxPayload` | 机器人置码后保持 ≥3 个 IPO 周期；上位机按变化沿 + 滑窗去重 |
| 下行（上位机→机器人） | `TxCmd` + `TxPayload` + `TxSeq` | 上位机每条指令递增 `TxSeq`；机器人按「`TxSeq` 变化 且 `TxCmd≠0`」沿触发，执行后清 `TxCmd` |

⛔ **RSI 是机器人主动发包、上位机被动回复模型** ⇒ 上位机**无法**主动发起单发。
下行指令只写回复缓存，实际发出发生在收到机器人包的**下一个回复周期**（一个 IPO 周期）。
调试面板的按钮文案因此标注「下一帧生效」。

### 5. 焊参走 5 个具名元素通道，废止文本协议

`WeldParamControlWorkflow.SendToRobot` 由 `"P{0} S{1} V{2} G{3}"` 文本协议改为
`UpdateRobotWeldParams(功率, 送丝, 剪丝, 速度, 摆幅)`（对应输出端 1~5）。

### 6. EKI 通道整体退役（执行 ADR-026 决策 2 的清理范围）

- `KukaEkiComm.cs` **已移除**（整文件删除）+ csproj 退注册
- `CommunicationManager`：`EkiComm` 属性删除、`RobotCommMode` 固定返回 RSI、
 `ConnectRobot`/`DisconnectRobot` 只操作 RSI、`RobotClientXdoc` 保留但不再初始化
- UI：删除 `radioModeEKI` 控件与两个互斥处理器
- `FileEditorForm`：删 EKI 分支（`SaveEKIConfig` / `GetKUKAEKIPath`）

⛔ **保留**（不删）：`CommunicationType.KUKA_EKI` 与 `RobotCommModeType.EKI` 枚举成员
（历史 INI `RobotCommMode=1` 仍可读）、`KUKAConnectionEventArgs.IsEKIConnected`（恒 false，零消费者）。

### 7. 通讯调试面板落在既有 `panelRobot`（FilebackupPage 通讯配置文件页）

⛔ **不新建页面**：`panelRobot` 本就是机器人通讯面板，在其上扩调试能力。
`inputLog`（通讯 log）保持原位与原机制（订阅 `GlobalCommData.CommunicationCommandReceived`）。

新增 `tlpRobotDebug`（TableLayoutPanel，`Dock=Bottom`，与既有绝对定位控件不重叠）：

| 区 | 控件 | 能力 |
|---|---|---|
| 状态条 | `lblRsiStat` | 连接状态 / 收包数 / 发包数 / 上行码释意 / IPOC（500ms 定时刷新） |
| ~~上行~~ | ~~`selectRxCmd` + `txtRxPayload` + `btnInjectRx`~~ | ⛔ **2026-10-23 业主裁定删除**：调试只针对真实机器人连接，不做本地模拟注入 |
| 下行 | `selectTxCmd` + `txtTxPayload` + `btnSendTx` | 按数值码下发（含 TxSeq 自增） |
| 焊参 | 5 个输入 + `btnInjectWeldParams` | 写入 5 个焊参通道 |
| 监视 | `txtRsiRxPacket` + `txtRsiTxPacket` | 最近一帧 Rob 包 / Sen 包原文 |

⚠️ `panelRobot` 高度 114→422px、`tableLayoutPanel1` row1 120→430px（给调试区让位）。

### 8. RSI 启动时序门控（2026-10-21 追加）

**背景**：初始化链曾出现「界面尚未生成就打开 RSI」导致 UI 控件为空、程序在构造函数阶段崩溃。

**决策（双层门控，缺一不可）**：

| 门 | 规则 | 落点 |
|---|---|---|
| ① 静态构造零重入 | `GlobalCommData` 静态构造期间可被 `CommunicationManager` 构造重入 `ShowLog`（格式契约升级告警）；`_logArgs` 必须**先于** `mCommunicationManager` 赋值，且 `ShowLog` 对 `_logArgs` / `MachineLog` 做空保护 | `SystemComm.cs` 静态构造 + `ShowLog` |
| ② 界面就绪门控 | 全部子页面实例化完成后才 `GlobalCommData.MarkUiReady()`；机器人通讯步检查 `IsUiReady`，未就绪则**留在本步、IOWork 下一拍重试**（ADR-041 非阻塞），不得 Sleep 等 UI | `FormMain`（`LoadNavAndPages` 后）+ `DeviceControlWork.InitializeMachineTick` |

配套 UI 防御：`FilebackupPage` 刷新计时器改在 `HandleCreated` 后启动；计时器/通讯日志/`AppendLog` 一律先判 `IsHandleCreated && !IsDisposed && !Disposing`；`MainPage` 日志回调同判据。

**后果**：RSI 不可能先于界面开启；即使未来有其它入口提前触发初始化，也会自动等待而不是崩溃。

## 机器人侧职责边界（本 ADR 配套交付）

`robot-comm-spec/机器人侧_焊接主程序.src` 严格限定在 RSI 通道内：
位姿移动（置目标位分离模式）+ 上下行指令 + 5 焊参通道。

⛔ **机器人程序不实现振镜摆动 / LA 对焦随动 / TA 力矩** —— 那些是上位机 EtherCAT 从站
（`WeldHeadSlaveDevice`，PDO 0x7010/0x7000/0x6000）的职责；两侧同时写振镜 ⇒ 双主冲突。
⛔ 运动类指令禁止在 IPO 周期任务内直接 `PTP`（看门狗超时）⇒ 置目标位 + 独立运动程序。
⛔ 激光器与送丝机调用为**注释占位**（`【现场改写】` 标注），现场按实际接口改写。

## 落地复核（2026-10-21 二次审计）

首轮落地只验证了「组包侧」改对，运行时链路仍存在 6 处实现级缺陷，本轮逐项修正：

| # | 缺陷 | 修正 |
|---|---|---|
| 1 | `ParseRobotPacket` 把**任意文本节点都写 `Ipoc` 后 `continue`**，`RxCmd`/`RxPayload` 分支不可达 ⇒ 真机上行指令恒为 0 | 文本节点按元素名分派：`IPOC` / `RxCmd` / `RxPayload` |
| 2 | `ReceiveLoop` 调 `ParseRobotPacket(xml)` 未传 `SendPacketFormat` ⇒ 解析侧仍走内置默认，决策 1「格式文档驱动」名存实亡 | 改为 `ParseRobotPacket(xml, SendPacketFormat)` |
| 3 | `SendLoop` 每 `Sleep(1)` 盲发，约 1000 包/秒重复 IPOC 洪泛机器人 | 改「一包一回」：`_replySignal`（AutoResetEvent）由收包置位，回复线程取缓存组包；`Stop` 置位唤醒退出 |
| 4 | 上行指令未做变化沿去重，机器人保持 ≥3 个 IPO 周期导致同一指令执行多次 | `DeviceControlWork.OnRobotDataReceived` 增 `_lastRxCmdCode` 变化沿判据（`0` 复位） |
| 5 | `EnsureRsiFormatSections` 只在「节缺失」时补默认，现场旧 Tech 节（缺 `RxCmd`/`WeldPower`）永不升级 | 增 `HasRequiredElements` 契约校验，旧节原地 `ReplaceWith` 重建并告警 |
| 6 | 机器人端 XML 端口取 `HOST_PORT`，本机监听取 `PORT`，二者可漂移 | `SaveRobotRsiXml` 以 `RsiComm.LocalPort` 为唯一真相，不一致时告警 |

附带修正：`ConnectRobot`/`DisconnectRobot` 复位 `HasRobotPose`（断链后不再消费陈旧位姿）；`Start()` 清零收发计数与最近包原文；`CommWork` 订阅改「先退订再订阅」防重复入队；UI 停用开关同时停监听、装载期屏蔽控件事件回写、`lblRsiStat` 跨 4 列；`CommCommandWork` 对 Tx 指令不再误记「坐标上报类」。

**2026-10-22 补充（启停可观测性）**：①监听失败原因只给结论——IP 未分配写 `本机未找到该 IP`，网口非 Up 写 `网口 X 状态 Down（未启用/未连接）`，不罗列本机全部 IPv4；②失败原因统一落 `KukaRsiComm.LastError`（Start/Stop 入口清空、各失败分支写入）；③`CommunicationManager.DisconnectRobot()` 由 `void` 改为 `bool`，回传 `Stop()` 结果；④调试界面通讯按钮（启用开关 / 监听开启 / 监听关闭 / 打开配置 / 保存配置 / 周期切换）操作结果一律 `AppendLog` 到页面通讯日志，开/关均记录成功或失败，失败附 `LastError`。

**判据自证**：静态校验 29/29 通过；镜像副本注入 4 处旧行为后 4 项全部 FAIL（判据有区分度）。⚠️ 真编译待 Visual Studio，DEMO 联调仍需现场验证 IPOC 回传与沿触发。

## 后果

- ✅ 上位机代码与交付目录 `robot-comm-spec/` 的协议契约**逐项一致**
- ✅ EKI 通道代码面清零（`KukaEkiComm.cs` 963 行 + Manager 分支 + UI radio）
- ✅ 静态校验 47/47 通过；基线副本 22 项 FAIL（判据有区分度）
- ⚠️ **真编译待 Visual Studio 验证**（本机无编译器）
- ⚠️ `10:1` 量纲、`0x7000` 读写、CST `Curve_Mode` 语义仍待上机实测
- ⚠️ 机器人侧 KRL 为**参考实现**，点位名 / IO 号 / 激光器接口须现场改写

## 契约演进（2026-10-22，机器人侧减指令）

- `TX_OK(8)` 废止 → **`TX_NG(8)`（焊接中异常，通知机器人停止动作）**；机器人侧不再等待「焊前检查 OK」应答，发下一步指令即默认检查通过。
- `TX_CUT_WIRE(10)` 废止（`TxCmd=10` 备用）；剪丝唯一通道 = `CutWire` 具名元素（输出端 3）。
- `CommandCore.TxCodeToCommand`：1~7 位姿 + 8 `TxNG` + 9 `TxAbort`；`CommandDescriptions` 9 Rx + 9 Tx = 18 条。
- 下发点：`ReportAlarm` / `DoMotionBusFault` 在 `IsWelding` 时下发 `TX_NG`；急停仍下发 `TX_ABORT`。
- IP：机器人 KLI `192.168.10.100` / 上位机 `192.168.10.50`（代码默认值、运行配置与交付 XML 同步）。
- **RobotServer 结构**：连接参数统一挂 `<CONFIG>`（旧根级结构在 `InitializeCommunication` 自动迁移）；`HOST_PORT` 是本机监听口（缺失回落 `PORT`），`PORT` 是机器人发送口；通道开关（`RobotEnabled` / `RobotCommMode`）保持 Comm INI，不进 XML。
- **在线判据（2026-10-22）**：RSI 机器人=客户端/主动发包，上位机=UDP 服务端/监听方；`RobotConnected` 仅表示监听启动，新增 `KukaRsiComm.IsRobotOnline`（收到过包 + 最近包在 `max(5×CYCLE, 500ms)` 内），心跳、`DeviceControlWork.IsRobotOnline`、主界面设备按钮与调试面板统一改用该判据。
- **监听绑定（2026-10-22）**：`KukaRsiComm.Start()` 绑定 `HOST_IP` 具体地址（原 `0.0.0.0` 可无网口假监听）；启动前枚举网口校验 IP 已分配且 Up，失败写明确错误日志并返回 false。

## 相关

- [[decisions/ADR-026-RsiSemanticRewriteAndDualChannel]]（上位决策）
- [[lessons/ProtocolDirectionalConstraints]]（SEND 段禁 STRING / 写入关键词不可上行）
- [[lessons/StartupInitializationOrderGates]]（决策 8 的坑点判据：静态构造重入 / UI 就绪门控 / 句柄守卫）
- [[api/CommunicationManager]] · [[api/CommandCore]] · [[api/KUKARobot]] · [[modules/Comm]]
- [[architecture/CodeMap]]（代码地图）
- 交付目录 `robot-comm-spec/`（机器人端 5 件套 + 指令表 + 部署手册 HTML + 机器人主程序）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[decisions/ADR-Index]]
