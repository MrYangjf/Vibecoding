---
title: KR-002 步骤级展示
date: 2026-10-30
updated: 2026-11-02
tags: [规则, 流程, Skill执行]
status: accepted
---

# KR-002 步骤级展示

> **一句话规则**：每个 Step 必须显式展示编号 + 名称 + 输出，禁止合并成 Phase 级摘要

## 适用范围

**适用**：所有 Phase 内含的 Step。  
**不适用**：Phase 汇总本身（汇总必须存在，但不替代 Step 展示）。

## 规则正文

1. 每个 Step 单独输出一个 `### Step X.Y: StepName` 块，块内写「读了什么 / 发现什么 / 决定什么」。
2. ⛔ **禁止**只给 Phase 级摘要；⛔ **禁止**把多个 Step 合并成一行。
3. Step 确属不适用时写明「N/A + 原因」，不得省略。
4. 一个 Phase 的全部 Step 完成后给出汇总表，**再**请求用户确认。

## 判据

- ⛔ 违反判定：输出中 `### Step X.Y` 块数 < 该 Phase 应执行 Step 数，且无「N/A + 原因」说明。
- ✅ 机器校验：报告中 `### Step ` 出现次数 == 计划 Step 数。

## 反例

| 反例（违规写法） | 正解 |
|---|---|
| 「Phase 2 完成（略）」 | 逐个 Step 展示编号 + 名称 + 输出 |
| 「Step 2.3/2.5/2.6 都过了」 | 三个 Step 各占一块，写清读了什么 / 发现什么 |

## 相关页面

- [[project/vibecoding-workflow]]
- [[rules/Rules-Index]]
