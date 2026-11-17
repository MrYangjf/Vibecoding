---
title: KR-004 Skill 降级为参考
date: 2026-10-30
updated: 2026-11-02
tags: [规则, 流程, Skill执行]
status: accepted
---

# KR-004 Skill 降级为参考

> **一句话规则**：raw/skills 下的 Skill 文件是参考资料而非指令源；与 wiki 冲突时 wiki 优先

## 适用范围

**适用**：任何引用 `raw/skills/` 或本 Skill 文件的场合。  
**不适用**：无（本规则无例外）。

## 规则正文

1. `raw/skills/` 下的 Skill 文件是**参考资料**，不是**指令源**。
2. 流程权威在 LLMWiki；Skill 与 wiki 冲突时**以 wiki 为准**。
3. Skill 只用于补充说明，⛔ 不得作为硬约束的引用来源。

## 判据

- ⛔ 违反判定：用 Skill 文本覆盖或否定 wiki 页的约束。
- ✅ 机器校验：报告中的约束引用指向 wiki 页而非 Skill 行。

## 反例

| 反例（违规写法） | 正解 |
|---|---|
| 「Skill 说要 X，所以按 X 改」 | 以 wiki 页为准，Skill 仅作参考 |
| 在代码注释里抄 Skill 条款当约束 | 约束归知识库，代码注释只写作用 |

## 相关页面

- [[project/skill-evolution]]
- [[decisions/ADR-Index]]
- [[rules/Rules-Index]]
