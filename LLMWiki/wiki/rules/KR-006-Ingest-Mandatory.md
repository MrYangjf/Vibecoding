---
title: KR-006 Ingest 强制
date: 2026-10-30
updated: 2026-11-02
tags: [规则, 流程, Skill执行]
status: accepted
---

# KR-006 Ingest 强制

> **一句话规则**：编码后必须做 Phase 3 知识沉淀，未沉淀视为未完成

## 适用范围

**适用**：任何产生代码或配置改动的任务收尾阶段。  
**不适用**：纯查询任务（无改动则无沉淀对象）。

## 规则正文

1. Phase 3 Ingest **不是可选步骤**；未沉淀的编码视为未完成。
2. 沉淀范围按改动性质落到 `modules/` / `api/` / `decisions/` / `lessons/` 的对应页；⛔ 不新建重复页（先合并后新建）。
3. 沉淀后必须跑 `tools/wiki_index_build.py` 重建 index，并用 `tools/wiki_log.py append` 追加 log。
4. log 时间戳由脚本取，⛔ 禁止手填（见 [[rules/KR-008-Timestamp-Rule]]）。

## 判据

- ⛔ 违反判定：改完代码无 Ingest 记录，或 index / log 未随本轮更新。
- ✅ 机器校验：`logs/log.md` 顶部条目时间晚于本轮改动；index 含本轮新增 / 修改页。

## 反例

| 反例（违规写法） | 正解 |
|---|---|
| 「代码改好了，知识库下次再说」 | 本轮内完成 Ingest 才算做完 |
| 手工在 index 里加一行表 | 跑 wiki_index_build.py 重建 |

## 相关页面

- [[project/vibecoding-workflow]]
- [[rules/Rules-Index]]
