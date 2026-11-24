---
title: ADR-111 注释只写作用：禁⛔/日期/ADR等元信息，约束归 wiki（C20）
date: 2026-11-20
updated: 2026-11-20
tags: [决策, 注释规范, 代码精简, C20]
status: accepted
---

# ADR-111 注释只写作用：禁⛔/日期/ADR等元信息，约束归 wiki（C20）

> **决策一句话**：所有代码注释只写作用（≤20 汉字），禁含 ⛔ / ADR 编号 / 日期 / 业主裁定 / 改版 / 「原为 X 现为 Y」等过程性元信息；约束、历史、裁定一律由 LLMWiki 承载。

## 背景

2026-11-20 业主裁定：新增代码注释不要包含 ⛔ / 日期 / ADR 这样的内容，只需要写明作用即可。

此前 [[standards/CodeSimplification]] §二顶层裁定第 1 条已有「约束归知识库，注释只写作用」原则，且 C16/C18/C19 已把注释长度判据做实（单行 ≤20 字 / 跨行合并 / 变量注释一行）。但**内容维度无判据**：`csharp_review.py` 只查长度，含 ⛔/日期/ADR 的注释只要字数达标就不会被拦 —— 这正是连续多轮重构中防错约束被写进代码注释、注释越来越长却查不出的根因。

## 决策

1. **硬约束（C20）**：所有代码注释（`//` / `///` / 块注释）禁含 `⛔`、`ADR-\d+`、`20XX-XX` 日期、「业主裁定 / 业主实测 / 改版 / 原为 X 现为 Y」等过程性元信息，**只写作用**（做什么，≤20 汉字）。承载方 = CodeMap / api / lessons / decisions。
2. **判据落地**：`scripts/csharp_review.py` 新增 `A.注释含元信息`（`COMMENT_META_RE`，**error 级**）——新增注释违规即拦截；`simplify_selfcheck.py` 的 JUDGE 加第 27 项、标准页 need 关键字同步，落实「改标准 = 改判据」。
3. **存量一次性清零**：违规存量注释就地改写为作用描述，多行变量注释合并为单行（C19）；改写走精确整行文本映射（非正则），二进制读写保留 BOM/行尾，先在副本目录做命中数断言验证再落源码。改写前后须满足 `comment_scan long` 内容/长度双维度归零；具体数量与验证结果记入 log。
4. **与既有判据并存**：C20 管**内容**、C16/C18/C19 管**长度**，互不替代；二者同时为 0 才算注释达标。

## 备选方案

- **只保留原则、不加判据**：否决 —— 连续多轮实证「无判据即查不出」，违反「改标准 = 改判据」铁律。
- **把元信息迁进 wiki 后在代码留指路注释**：部分采纳 —— 约束确实已在 CodeMap/api/lessons 承载；本轮对纯约束注释直接压成作用描述，不再逐条留指路（避免注释再次膨胀）。
- **warn 级而非 error 级**：否决 —— 存量已清零，新增违规应硬拦截；warn 会被「存量欠账不追溯」口径吞掉。

## 后果

### 正面
- 注释回归「作用说明」本位，不再承载约束/历史/裁定；静态判据可机械拦截违规新增。
- 长度与内容双维度归零，注释审查从「逐条人肉判断」变为「判据 0 诊断」。

### 负面
- 约束的就地防错提示消失，开发者需查 wiki 才知道「为什么不能这样做」（已由 ADR/lessons/CodeMap 承载，属可接受代价）。

## 验证

- `comment_scan long`：`merged_over=0 / var_multiline=0 / legacy_line=0`
- 全库元信息注释 Grep：残留 0
- `simplify_selfcheck.py`：RESULT PASS（含新 JUDGE 第 27 项）
- 新判据阴性/阳性对照：干净注释 0 误报，⛔/日期/ADR/doc 注释各命中 1
- 真编译 errors=0 rc=0；结构守卫 175/0 PASS；200 文件 BOM/行尾零漂移

## 相关页面

- [[standards/CodeSimplification]]（§二顶层裁定 4 / C20 / 4.1 映射表行 27）
- [[decisions/ADR-007-CodeSimplificationStandard]] · [[decisions/ADR-110-yt-calib-move-to-process-page]]
- [[modules/CommentConstraintRegistry]]（迁出约束台账）
- [[lessons/CommentMetadataCleanup]]
