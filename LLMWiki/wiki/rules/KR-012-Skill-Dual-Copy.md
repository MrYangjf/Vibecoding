---
title: KR-012 Skill 双副本同步
date: 2026-10-30
updated: 2026-11-02
tags: [规则, 流程, Skill执行]
status: accepted
---

# KR-012 Skill 双副本同步

> **一句话规则**：Skill 双副本同步前探行尾；仓库版规范化为 LF；同步后报告 numstat

## 适用范围

**适用**：任何改动 `SKILL.md` 的场合（仓库版与用户级两份都要同步）。  
**不适用**：不涉及 Skill 文件的改动。  
**历史副本（2026-11-02 起）**：`~/.workbuddy/skills/vibecoding-llmwiki/SKILL.md` 已降级为**历史留存** —— 文件保留但**不再同步、不参与一致性比对、不由 `skill_pointer_check.py` 校验**，⛔ 不得当作现行规范来源。

## 规则正文

1. 仓库版 `LLMWiki/skills/vibecoding-llmwiki/SKILL.md` 与用户级 `~/.trae-cn/skills/vibecoding-llmwiki/SKILL.md` 必须**内容一致**（行尾同为 LF）。
2. 同步**不是**字节覆盖：先探两份的 CRLF / loneLF / CRCRLF / BOM 计数。
3. 仓库版规范化为 LF；⛔ 不用整文件 Write（会吞 BOM、改行尾）。
4. 同步后 `git -c core.autocrlf=false diff --numstat` 复核行数变化量；⛔ 顺手「修」用户级副本的行尾。

## 判据

- ⛔ 违反判定：两份 SKILL 内容不一致；或仓库版出现整文件级 diff（说明 BOM / 行尾被改写）。
- ✅ 机器校验：`tools/skill_pointer_check.py` 双份通过；numstat 变化量与实际改动相符。

## 反例

| 反例（违规写法） | 正解 |
|---|---|
| 只改用户级副本，忘了仓库版 | 改完两份同步并 diff 校验 |
| 直接整文件 Write 覆盖仓库版 | 按字节读改写、保留 BOM 与 LF |

## 相关页面

- [[guides/ExecutionEnvironment]]
- [[standards/WikiPageFormatSpec]]
- [[rules/Rules-Index]]
