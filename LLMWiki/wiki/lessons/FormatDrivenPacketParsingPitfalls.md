---
title: 格式驱动收发的运行时陷阱：文本节点误判 / 节存在≠契约正确 / 回复盲发
date: 2026-10-21
updated: 2026-10-30
tags: [lessons, RSI, 格式驱动, XML, 解析, 回复, ADR-026, ADR-074]
status: active
source: AdaWeldSystem/Comm/Communication/Implementations/KukaRsiComm.cs + CommunicationManager.cs
---

# 格式驱动收发的运行时陷阱

## 现象

RSI 数值化协议（ADR-026 / ADR-074）首轮落地后，组包侧与文档侧都对，但真机链路上：

- 机器人发来的 `RxCmd` 恒为 0，所有上行指令（到焊前位 / 焊接起始位等）全部失效；
- 上位机回复包约 1000 包/秒发往机器人，同一 IPOC 被重复回传；
- 现场 `RobotServer.xml` 里的 `SEND_FORMAT`/`REPLY_FORMAT` 仍是旧 Tech 契约，升级程序后协议静默不生效。

## 根因（三类）

### 1. 文本节点被当成单一语义吞掉

`ParseRobotPacket` 遍历格式元素时写了：

```csharp
if (elem.IsTextNode)
{
    packet.Ipoc = node.InnerText;   // ⛔ 任何文本节点都写 Ipoc
    continue;                        // ⛔ 后面的 RxCmd/RxPayload 分支永远到不了
}
```

`RxCmd`/`RxPayload` 在新契约里正是**文本节点形式**（`<RxCmd>4</RxCmd>`）。
⇒ 数值分支成了死代码，且 `Ipoc` 被前序节点覆盖（仅因 IPOC 恰好排在最后才碰巧正确）。

**正解**：`IsTextNode` 只说明「值在元素文本里」，语义必须再按**元素名**分派：

```csharp
if (elem.IsTextNode)
{
    if (tag == "IPOC") packet.Ipoc = node.InnerText;
    else if (tag == "RxCmd") packet.RxCmd = (int)ParseDouble(node.InnerText);
    else if (tag == "RxPayload") packet.RxPayload = ParseDouble(node.InnerText);
    continue;
}
```

### 2. 「格式节存在」不等于「格式节是现行契约」

`EnsureRsiFormatSections` 原先只在**节缺失**时补默认：

```csharp
if (doc.Root.Element("SEND_FORMAT") == null) { doc.Root.Add(BuildSendFormatElement()); }
```

旧版本写下的节一直存在，于是新元素（`RxCmd`/`RxPayload`/`WeldPower`/`TxCmd`）永远不会出现，
`LoadPacketFormat` 读到的是「合法的旧契约」，运行时不报错、功能全废。

**正解**：补齐后仍须**校验必备元素齐备性**，不齐备则原地 `ReplaceWith` 重建并告警；
判据只看「契约元素在不在」，不比对字面量与顺序，保留现场对占位文案的自定义。

### 3. 回复线程按固定 Sleep 盲发

```csharp
_thread.Sleep(1);   // ⛔ 约 1000 包/秒
```

RSI 是**机器人主动发包、上位机被动回复**模型：一帧 Rob 包应回一帧 Sen 包，且 IPOC 必须同帧。
盲发会把同一个 IPOC 重复回传，既占带宽又可能被机器人判为无效包。

**正解**：收包线程置位 `AutoResetEvent`，回复线程 `WaitOne(周期×5)` 醒来后取回复缓存组包；
`Stop()` 必须 `Set()` 一次唤醒等待线程，`Dispose()` 再释放信号。

## 可推广判据

> ⛔ **判据一：凡是「按节点类型分类」的解析，分类之后必须再按业务键分派。**
> `IsTextNode` / `IsAttribute` / `NodeType.Element` 都只是**语法形态**，不是业务语义；
> 一个形态对应多个语义时，统一赋值必然吞掉其余语义，且往往表现为「字段恒默认值」而非异常。

> ⛔ **判据二：配置节「存在性检查」不能替代「契约完整性检查」。**
> 版本升级新增必填键时，只补缺失节会让旧配置永久停留在旧契约；
> 必须按**必备键集合**校验，不齐备就升级，并留下告警日志。

> ⛔ **判据三：请求-应答型协议的发送节奏由对端触发，不由本地定时器决定。**
> 只要协议规定「收到一帧回一帧」，本地就不得用固定 `Sleep` 自驱；
> 用收包信号驱动，并在停止路径显式唤醒，否则 Stop/Join 会挂在等待上。

## 附带教训（同轮修正）

- 上行指令「机器人保持 ≥3 个 IPO 周期」⇒ 上位机必须按**变化沿**去重，否则一条指令执行多次；
- 机器人端 XML 的发包端口必须取**本机实际监听口**，不能取旁路配置键（`HOST_PORT`），否则漂移后静默收不到包；
- 重复初始化必须「先退订再订阅」，`+=` 单独使用会让回调随初始化次数累加。

## 相关

- [[decisions/ADR-026-RsiSemanticRewriteAndDualChannel]]（格式文档驱动 · 数值化承载）
- [[decisions/ADR-074-RsiNumericProtocolImplementation]]（落地复核 6 项）
- [[lessons/ProtocolDirectionalConstraints]]（SEND 禁 STRING / 读写关键词方向）
- [[api/KUKARobot]]（运行时行为表）· [[modules/Comm]]（RSI 运行时约束）
## 相关页面

- [[index/index]]
