---
title: KR-008 时间戳取用
date: 2026-10-30
updated: 2026-11-03
tags: [规则, 流程, Skill执行, 日志]
status: accepted
---

# KR-008 时间戳取用

> **一句话规则**：日志时间戳由脚本取，禁止估算或手填；程序日志的显示格式一律 24 小时制

## 适用范围

**适用**：Phase 3 追加 `logs/log.md` 的每一次写入；程序侧所有时间戳格式化（界面日志、日志文件、导出目录名）。  
**不适用**：无（写入 log 或输出时间即适用）。

## 规则正文

1. 时间戳必须由脚本取（`tools/wiki_log.py append` 自动取当前系统时间）。
2. ⛔ 禁止估算、猜测、手填或复用历史时间。
3. 无法执行时标 `[No.]`，⛔ 不猜。
4. **程序日志时间一律 24 小时制**：格式串只能用 `HH:mm:ss`，⛔ 禁 `hh`（12 小时制）、`tt`（AM/PM）、`ToString("T")`、`ToShortTimeString` 等本地化格式。
5. 统一入口：界面侧 `GlobalCommData.ShowLog` → `MainPage.LogAppend`/页面 `AppendLog` 一律走 `FileOperate.Log.FormatTimestamp`；日志文件侧 `Log.GetNowToString()`。两侧格式必须一致，⛔ 不得在各调用点各自格式化。

## 判据

- ⛔ 违反判定：log 时间戳与系统时间不符，或为整点 / 整分的估算值；程序日志出现 `03:22:08` 与目录名 `edit_20261103_152208`（15:22:08）对不上。
- ✅ 机器校验：时间戳格式为 `YYYY-MM-DD HH:MM:SS` 且接近本轮操作时刻；同一操作（保存）产出的日志时间与目录名小时一致。

## 反例

| 反例（违规写法） | 正解 |
|---|---|
| 手填「2026-11-02 09:00」 | 跑 wiki_log.py append 由脚本取时 |
| 沿用上一条的时间戳 | 每次 append 独立取时 |
| `DateTime.Now.ToString("yyyy-MM-dd hh:mm:ss")` | `Log.FormatTimestamp(DateTime.Now)` → `yyyy-MM-dd HH:mm:ss` |

## 相关页面

- [[rules/Rules-Index]]
- [[rules/KR-011-Backup-Output-Timing]]
- [[standards/MessageLogResponsibility]]
