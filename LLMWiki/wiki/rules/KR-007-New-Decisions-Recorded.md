---
title: KR-007 新决策必须记录
date: 2026-10-30
updated: 2026-11-02
tags: [规则, 流程, Skill执行]
status: accepted
---

# KR-007 新决策必须记录

> **一句话规则**：涉及新架构选择必须建 ADR；同主题先合并、不新建

## 适用范围

**适用**：编码中产生新架构选择时（分层 / 归属 / 契约变更）。  
**不适用**：纯实现细节、无架构含义的改动。

## 规则正文

1. 涉及新架构选择必须在 `wiki/decisions/` 建 ADR。
2. **先合并后新建**：同主题先跑 `tools/adr_new.py check`，命中则追加既有页的「演进记录」。
3. 新号 = `ADR-Index` 的 `max+1`；⛔ 废止不回收编号，旧号用「旧」前缀消歧。
4. ADR 只写「为什么这么定」；⛔ 试错过程写 `logs/log.md`。

## 判据

- ⛔ 违反判定：出现架构级变更却无 ADR；或新建了与既有页同主题的 ADR。
- ✅ 机器校验：ADR-Index 新增一行且编号连续；新页在 index 与 ADR-Index 各登记一次。

## 反例

| 反例（违规写法） | 正解 |
|---|---|
| 「先改代码，ADR 回头补」 | 决策与实现同轮落地 ADR |
| 同主题直接新建 ADR-08X | 先 check，命中就并入既有页 |

## 相关页面

- [[decisions/ADR-Index]]
- [[standards/WikiPageFormatSpec]]
- [[rules/Rules-Index]]
