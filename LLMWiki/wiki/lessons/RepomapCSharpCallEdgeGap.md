---
title: repomap 官方 C# 解析器缺口（只收 public 方法 · 零方法调用点）与补齐方式
date: 2026-11-19
updated: 2026-11-19
tags: [教训, 代码地图, repomap, tree-sitter, C#]
status: accepted
---

# repomap 官方 C# 解析器缺口（只收 public 方法 · 零方法调用点）与补齐方式

> **一句话**：官方 C# 解析器只收 public 方法（实测 1321/2833 = 47% 覆盖）且**零方法调用点**，成员与影响面大面积缺失，须自研补齐。

## 现象

- 用官方 `coderepomap` 生成代码地图后，`ProcessControlPage` 只列出 **5** 个方法，而该类实际有 **109** 个方法。
- L3 关系层只有 **114** 条边，且**全是** `inherits` / `implements`，一条方法调用边都没有 ⇒ 影响面追踪完全失效。
- 统计 tree-sitter 原始节点：`method_declaration` 2833 · `constructor_declaration` 194 · `property_declaration` 1440 · `field_declaration` 1919。

## 根因

- `coderepomap/csharp/parser.py` 的 `_extract_method` 末尾有 `if name and 'public' in modifiers:` ⇒ **非 public 方法（private/protected/internal）与构造函数全部丢弃**。
- 其引用抽取只从**类型声明**产出 `inherits` / `implements`，**不解析方法体调用点** ⇒ C# 的 L3 天然只有继承图。
- 官方 L2 另有渲染层截断（每模块 20 类 / 每类 5 方法）且**不输出文件路径** ⇒ 直接当定位索引用不了。

## 判据

- 覆盖率核验：`官方符号数 ÷ tree-sitter 成员节点数`；本项目 = 1321/2833 = 47% ⇒ 低于 80% 即判定「官方解析器对本项目不可直接用」。
- 边类型核验：L3 边若**全部**是 `inherits`/`implements` ⇒ 判定「无方法调用点」。
- 补齐后核验：私有方法能被列出（例：`ProcessControlPage` 方法数 ≥ 100）；类型级调用边能给出跨模块调用方（例：`GlobalCommData` 被 61 个文件调用）。
- ⛔ 置信度判据：接收者是项目内**类型** ⇒ 高置信；纯标识符调用（`Log(...)`）⇒ 低置信（同名不同类会误连）。

## 预防

- 用第三方代码地图引擎前，**先做覆盖率抽样**：取 1~2 个大类比对方法数，别直接信「已生成 3000+ 符号」。
- 成员抽取改用 tree-sitter 直接取节点（`method_declaration` / `constructor_declaration` / `property_declaration` / `field_declaration`），不依赖引擎的修饰符过滤。
- 调用边抽取用 `invocation_expression` 节点，`member_access_expression` 取 `expression` + `name` 两个字段分别拿接收者与方法名。
- 调用边**按置信度二分**（类型级 / 方法级）分别成页 ⇒ 页面既可控又不误导。
- ⛔ **关系页永远只是候选集**：结论仍须 Grep 确认（见 [[rules/KR-009-Grep-Default]]）。
- 剔除 BCL 噪声：按**方法名**全收会把 `List.Add` / `ToString` / `Path.Combine` 收进来（实测 4454 条里绝大多数是这类）⇒ 必须用「接收者是否项目类型」过滤。

## 相关页面

- [[architecture/CodeMap]] · [[architecture/CodeMap-Relations]]
- [[decisions/ADR-108-codemap-machine-generation]]
- [[rules/KR-009-Grep-Default]]
- [[index/index]]
