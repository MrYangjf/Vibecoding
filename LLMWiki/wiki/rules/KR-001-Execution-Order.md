---
title: KR-001 强制执行顺序
date: 2026-10-30
updated: 2026-11-02
tags: [规则, 流程, Skill执行]
status: accepted
---

# KR-001 强制执行顺序

> **一句话规则**：接到开发类任务必须按「读工作流规范 → 读 AGENTS.md → 执行 Phase 0~4」三步走，不得直接动手

## 适用范围

**适用**：所有开发类任务（编码 / 改码 / 重构 / 答疑式改码）。  
**不适用**：只读检索与纯问答请求（只查不写）。

## 规则正文

1. **第一步**：读 `wiki/project/vibecoding-workflow.md` 全文 —— Phase 0~4 的唯一规范；读不到即报错停止。
2. **第二步**：读 `AGENTS.md` 的 `/vibeCoding Workflow (LLMWiki Native)` 节，取补充规则与硬约束。
3. **第三步**：按 Phase 0 → 1 → 2 → 3 → 4 顺序执行；每个 Phase 结束向用户汇报并取得确认再进入下一 Phase。
4. **任务跟踪**：每个 Phase 建一条任务条目 —— 开始置 in_progress、完成置 completed。

## 判据

- ⛔ 违反判定：开工前未读工作流规范即动手改码；或未取得用户确认就跨 Phase。
- ✅ 机器校验：任务列表中 5 个 Phase 条目状态完整（无 long-running 残留）。

## 反例

| 反例（违规写法） | 正解 |
|---|---|
| 先改代码，流程回头再补 | 先读工作流规范与 AGENTS.md，再动手 |
| 一口气做完 Phase 0~4 再统一汇报 | 每个 Phase 结束汇报并取得确认 |

## 相关页面

- [[project/vibecoding-workflow]]
- [[rules/Rules-Index]]
