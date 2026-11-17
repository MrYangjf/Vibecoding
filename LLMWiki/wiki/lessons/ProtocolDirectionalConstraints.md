---
title: 协议方向性硬约束：RSI 的 SEND 段禁 STRING，写入关键词不可上行
date: 2026-10-21
updated: 2026-10-30
tags: [lessons, 协议, RSI, KUKA, 上行, 下行, 关键词, 文档驱动, ADR-026]
status: active
source: robot-comm-spec/WeldControlConfig.xml + KST_RSI_33_zh.pdf V4 §7.4.2/§7.4.3/§7.4.5/§7.4.6
---

# 协议方向性硬约束：RSI 的 SEND 段禁 STRING，写入关键词不可上行

## 现象

2026-10-20 的 RSI 统一通讯方案把**上行指令**设计成走 Rob 包 `DEF_EStr` 字符串通道
（`<Estr>RX_WELD_STOP_POSE,1520.5</Estr>`），理由是「`DEF_EStr` 是关键词表里唯一的 STRING 载体」。

2026-10-21 逐条核对 KST RSI 3.3（V4 / 2016-06-16）原文后发现该设计**不成立**。

## 根因：把「关键词表里有」误当成「可用于这个方向」

手册 §7.4 关键词表是**一张平铺表**，不区分方向；而 §7.4.2/§7.4.3/§7.4.5/§7.4.6 是**按方向分节**的：

| 位置 | 约束 |
|---|---|
| §7.4.2 SEND 段（机器人→上位机） | `TYPE` 仅 `BOOL` / `DOUBLE` / `LONG` —— **不含 `STRING`** |
| §7.4.3 RECEIVE 段（上位机→机器人） | 普通元素 `TYPE` 同样仅 `BOOL` / `DOUBLE` / `LONG` |
| §7.4.5 读取关键词 | `DEF_RIst`/`DEF_RSol`/`DEF_AIPos`/`DEF_ASPos`/`DEF_EIPos`/`DEF_ESPos`/`DEF_MACur`/`DEF_MECur`/`DEF_Delay` —— **只读，只能用于 SEND** |
| §7.4.6 写入关键词 | `DEF_Tech.C1..C6`/`DEF_Tech.T1..T6`/`DEF_EStr` —— **只写，只能用于 RECEIVE** |

⛔ `DEF_EStr` 出现在 §7.4.6（写入）里 ⇒ **它是「上位机写给机器人」的通道，不是上行通道**。
把它放进 SEND 段，机器人侧 RSI 编辑器**不会生成对应信号**，运行时静默无输出。

## 正解

| 方向 | 承载方式 |
|---|---|
| 上行 RX 指令 | 自定义具名元素 `RxCmd`(LONG) + `RxPayload`(DOUBLE) |
| 下行 TX 指令 | 自定义具名元素 `TxCmd`(LONG) + `TxPayload`(DOUBLE) + `TxSeq`(LONG) |
| 焊接参数 | 具名元素 `WeldPower`/`WireSpeed`/`CutWire`/`WeldSpeed`/`WeaveAmp` |

另两条手册规则必须一起记住（§7.4.4 XML 图规则）：

- TAG **含 `.`** → 属性书写形式 `<Tool X="1" Y="2" Z="3"/>`；
- TAG **不含 `.`** → 元素书写形式 `<RxCmd>4</RxCmd>`。

## 附带推翻：不要用 `DEF_Tech.T11~T110` 当自定义字段

`DEF_Tech.C1..C6` / `T1..T6` 是 RSI 内部的**固定编号语义**（C=主进、T=预进）。占用后：
无自定义命名空间、契约不自解释、且随 RSI 版本调整而失效。
⇒ 自定义业务字段一律用**具名元素**（`WeldPower`…`TxSeq`），在 RSI 信号图里直接映射到 KRL 变量。

## 可推广的判据

> ⛔ **凡「协议里某个东西存在」⇒「它能用于这个方向」，中间隔着一个方向性判据。**
> 查协议文档必须**按方向分节查**，不能只扫关键词总表。
> 同型高危：读写关键词混用、客户端/服务端语义混用、单向/双向接口混用。
>
> ⛔ 配套自检：**写协议方案时，每个元素都要能回答「它属于读还是写方向、TYPE 是否被该方向允许」。**
> 回答不上来 ⇒ 方案不可交付。

## 同类问题（未处置）

- `api/KUKARobot.md` §7.3 的 SEND 段关键词表里列了 `DEF_Tech.C1~C6` / `DEF_Tech.T1~T6` / `DEF_EStr`
  —— 已随 2026-10-21 KRL 文档清理整节改写，但**读关键词 / 写关键词的归属表**尚未单独成节，存在同类复发面。

## 相关

- [[decisions/ADR-026-RsiSemanticRewriteAndDualChannel]]（决策 2 的 2026-10-21 修正）
- [[api/KUKARobot]]（§6.5 RSI 单一通道与硬约束）
- 交付目录 `robot-comm-spec/`（`WeldControlConfig.xml` + 信号流三件套 / 通讯指令表 xlsx / `RSI部署与联调测试手册.html`）
## 相关页面

- [[index/index]]
