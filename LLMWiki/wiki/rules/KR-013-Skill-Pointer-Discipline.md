---
title: KR-013 Skill 指向不得写死内容页
date: 2026-10-30
updated: 2026-11-02
tags: [规则, 流程, Skill执行]
status: accepted
---

# KR-013 Skill 指向不得写死内容页

> **一句话规则**：Skill 只写角色级锚点与「去哪查」的机制表述，不写死内容页名

## 适用范围

**适用**：编写 / 改写 SKILL.md 的任何场合。  
**不适用**：wiki 页之间的普通互链。

## 规则正文

1. **Skill 写「怎么查」，wiki 写「查什么」。**
2. Skill 只允许写**角色级锚点**：index · ADR-Index · CodeMap · vibecoding-workflow · WikiPageFormatSpec · ExecutionEnvironment · RawAssetCatalog。
3. ⛔ **禁止**写死具体内容页名（具体 ADR / lessons / guides / modules / api 页）—— 页会重编 / 拆分 / 合并，写死即失效，且失效后比没有更危险。
4. ⛔ **禁止**维护内容清单表（列出 N 条 ADR 约束 / N 条教训）。
5. ✅ **例外**：技术契约（C# 7.3 语法边界、`DisposeComponents()` 禁 `Dispose(bool)`、`InitializeComponent()` 禁循环等）可写死在 Skill，因其不随页重组而变。
6. **机械闸门**：`python tools/skill_pointer_check.py` —— C1 无写死内容页 · C2 无红链 · C3 工具存在 · C4 ADR 号有效 · C5 无内容清单表。

## 判据

- ⛔ 违反判定：SKILL.md 出现具体内容页名、内容清单表，或闸门脚本非零退出。
- ✅ 机器校验：`tools/skill_pointer_check.py` 两份副本均通过（退出码 0）。

## 反例

| 反例（违规写法） | 正解 |
|---|---|
| 在 Skill 里列「常用 ADR 清单」 | 写角色级锚点 + 「去哪查」的机制表述 |
| Skill 里写死 `lessons/XXX.md` | 只写 index / ADR-Index 等稳定锚点 |

## 相关页面

- [[standards/WikiPageFormatSpec]]
- [[rules/Rules-Index]]
