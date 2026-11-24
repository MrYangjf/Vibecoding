---
title: ADR-108 代码地图改为机器生成（repomap 引擎 · 分片 · 调用边自研补齐）
date: 2026-11-19
updated: 2026-11-19
tags: [决策, 代码地图, repomap, 工具链]
status: accepted
---

# ADR-108 代码地图改为机器生成（repomap 引擎 · 分片 · 调用边自研补齐）

> **决策一句话**：代码地图由官方 `coderepomap` 引擎机器生成（分片入 wiki），人工层只保留判断；官方 C# 解析缺口自研补齐。

## 背景

- 手写代码地图（逐文件详表 909 行）随改码必然漂移 ⇒ Phase 0 不敢信 ⇒ 退化为全盘 Grep ⇒ 地图失去「代码记忆」作用。
- 官方 `coderepomap`（PyPI 未发布，源码 github.com/sputnicyoji/coderepomap）提供 tree-sitter C# 解析 + PageRank 排序，产出 L1/L2/L3 三层。
- 实测官方 C# 解析器两个缺口：① `_extract_method` 有 `if 'public' in modifiers` 过滤 ⇒ 只收 public 方法（1321/2833 = 47% 覆盖），私有/内部方法与构造函数全丢；② 只发 `inherits`/`implements` 引用（114 条、零方法调用点）⇒ L3 对 C# 的影响面近乎无效。
- 官方 L2 每模块截断 20 类 / 每类 5 方法且**不带文件路径** ⇒ 无法直接当定位索引用。

## 决策

1. 生成器 = `tools/codemap_build.py`，路径全部由 `__file__` 推导；引擎复用官方 `coderepomap`（不自造类型解析器）。
2. 产物入 `wiki/architecture/`：总览 `CodeMap.md` + 符号分片 `CodeMap-Symbols-<模块>.md` + 关系分片 `CodeMap-Relations*.md`。
3. 分层纪律：**机器层禁手改**（页内标「禁手工编辑」）；**人工层只留判断**（功能域标注 · 定位陷阱 · 命名空间的模块归属与约束 ADR）。
4. 人工判断层存外部数据文件 `tools/data/namespace_meta.json`（可维护）⇒ 生成页始终可再生成。
5. 官方缺口自研补齐：成员抽取用 tree-sitter 直接取全量成员节点（方法/构造/属性/字段）；调用边自研抽取并**按置信度二分** —— 类型级（接收者是项目类型，高置信）+ 方法级（纯标识符调用，低置信）。
6. 分片纪律：符号层按模块分片（类型数 < 6 的合并为薄模块页）；关系层按调用方模块分片，行数超限才二级切分。
7. ⛔ **关系分片是候选集生成器，不是判决**：同名不同类会误连 ⇒ Step 2.5 结论仍以 Grep 为准（[[rules/KR-009-Grep-Default]]）。
8. ⛔ **手写逐文件详表退役**：旧 `CodeMap-Files.md` 仅留历史追溯，不再维护、不得作为现行定位依据。
9. 刷新入口：`python tools/codemap_build.py`（幂等）；同步校验：`python tools/codemap_build.py --check`（非零退出 = 地图已过期）。

## 备选方案

| 方案 | 放弃原因 |
|---|---|
| 继续手写逐文件详表 | 漂移必然发生，Phase 0 不敢信 ⇒ 退化为全盘 Grep（本轮要解决的原问题） |
| 直接用官方 L1/L2/L3 产物 | L2 截断且无文件路径 ⇒ 不能当定位索引；L3 对 C# 零方法调用点 ⇒ 无影响面价值 |
| 产物放 `raw/` 层 | `raw/` = 原始资料只读层；代码地图是**派生知识**，属 wiki 层（且需被 index 路由） |
| 命名空间单独建页 | 51 页 ⇒ 51 个孤儿页 + 大量重复度告警 ⇒ 合并进模块分片 |

## 后果

### 正面
- Phase 0 定位从「全盘 Grep」变为「总览 → 模块分片 → `文件:行`」三跳，命中即读代码块。
- 成员覆盖率从 47%（仅 public）提升到全量（含私有/内部方法、构造、属性、字段）。
- 影响面追踪获得候选集：类型级 598 条高置信边（如 `GlobalCommData` 被 61 个文件调用）。
- 地图随源码自动刷新，`--check` 可作为 Phase 4 漂移闸门。

### 负面
- 新增第三方依赖 `coderepomap`（PyPI 未发布 ⇒ 须从源码安装；本机源码存 `~/.coderepomap-src`）。
- 关系分片为启发式匹配（同名误连），**不可单独作为删除/改签名的依据**。
- 薄模块合并与二级切分阈值是经验值（行数估算系数），需随代码量调整。

## 相关页面

- [[architecture/CodeMap]] —— 代码地图总览（入口页）
- [[project/vibecoding-workflow]] —— Phase 0.0 / 2.5 / 3.6 的流程接线
- [[rules/KR-003-No-Skipping-Query]] · [[rules/KR-009-Grep-Default]]
- [[lessons/RepomapCSharpCallEdgeGap]] —— 官方 C# 解析缺口与补齐方式
- [[decisions/ADR-Index]]
