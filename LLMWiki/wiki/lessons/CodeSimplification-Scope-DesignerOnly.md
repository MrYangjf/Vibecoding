---
title: 代码精简范围裁定：强制排除仅 Designer.cs
date: 2026-08-27
tags: [教训, 代码精简, 范围, Designer.cs, UIDesign, 误解]
---

# 代码精简范围裁定：强制排除仅 Designer.cs（P1 易误读）

> ADR-023/[[standards/CodeSimplification]] 早期表述"除 UI 外的全部代码（即 `UIDesign/` 除外）"易被误读为 **UIDesign 整个目录都不做五维度精简**。2026-08-27 用户明确裁定：**强制排除的只有 `*.Designer.cs`（设计器自动生成文件），`UIDesign/` 下的非设计器 `.cs`（如 `FormMain.cs`/`MainPage.cs`）同样适用五维度**（成员排序/变量/枚举事件/逻辑/辅助函数 + XML 注释），仅状态判断与控制细则由 [[standards/UiStateSimplification]] 互补。

## 误读根因

- 标准页原文"适用范围：除 UI 外的全部代码（`UIDesign/` 除外）"与"强制排除 `*.Designer.cs`"两句话并存，UI 边界表述不一致，导致 AI 触发精简时把整个 `UIDesign/` 跳过。
- `csharp_review.py` 的跳过规则本就只针对 `*.designer.cs`，与"UIDesign 除外"形成张力。

## 正确边界

| 文件 | 是否五维度精简 |
|------|----------------|
| `*.Designer.cs`（任意目录） | ❌ 跳过（设计器生成，ADR-018/设计器约束） |
| `UIDesign/` 下非设计器 `.cs` | ✅ 适用五维度（状态控制细则见 UiStateSimplification） |
| 厂商 SDK 原生代码 / `3rdDepend/` | ❌ 跳过 |
| 其余业务源码 | ✅ 适用五维度 |

## 已更正位置（2026-08-27）

- [[standards/CodeSimplification]] 适用范围/扫描范围/边界表/执行清单/未覆盖段全部改为"仅 `*.Designer.cs` 除外"，`UIDesign/` 非设计器 `.cs` 纳入。
- [[decisions/ADR-022-CodeSimplificationStandard]] 相关页面描述同步更正。
- [[index/index]]「代码精简规范」分类摘要加注裁定。

## 影响案例

- `FormMain.cs`/`MainPage.cs`（2026-08-27）按五维度完整精简：删死函数/未用字段、补 #region、XML 注释补全，`csharp_review.py` warn/error 清零。

---

*来源：2026-08-27 用户裁定「强制排除的是 Designer.cs」*
