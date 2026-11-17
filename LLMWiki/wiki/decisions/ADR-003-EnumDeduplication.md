---
title: ADR-003 枚举去重策略 — 子命名空间禁止重复定义父命名空间枚举
date: 2026-08-01
updated: 2026-10-30
tags: [决策, 枚举, 命名空间, 代码质量]
status: accepted
---

# ADR-003 枚举去重策略 — 子命名空间禁止重复定义父命名空间枚举

## 背景

`EmguALG/Core/PreprocessConfig.cs`（命名空间 `AdaWeldSystem.EmguALG.Core`）中曾定义了 3 个与 `EmguALG/AlgorithmManager.cs`（命名空间 `AdaWeldSystem.EmguALG`）完全相同的枚举：

- `FilterOperation`
- `MorphologyOperation`
- `EdgeDetectionOperation`

这导致 C# 编译器在解析同命名空间中的引用时优先使用 `Core` 下的版本，而其他文件（如 `AlgorithmBase.cs`）也位于 `Core` 下但 `using AdaWeldSystem.EmguALG`，造成枚举解析歧义风险。同时，两份定义必须手动保持同步，违反 DRY 原则。

## 决策

**子命名空间禁止重复定义父命名空间中已存在的枚举。** C# 编译器在类型查找时会自动搜索父命名空间，因此子命名空间中的代码可以直接引用父命名空间中的类型，无需重复定义。

具体执行：
- 从 `PreprocessConfig.cs` 删除 `FilterOperation`、`MorphologyOperation`、`EdgeDetectionOperation` 的重复定义
- 保留 `AlgorithmManager.cs` 中的统一定义作为唯一真相源
- `PreprocessConfig.cs` 中的 `FilterConfig`、`MorphologyConfig`、`EdgeConfig` 类通过 C# 父命名空间自动解析引用父命名空间中的枚举

## 备选方案

1. **使用 `using` 显式引用** — 可行但冗余，C# 已自动搜索父命名空间
2. **将枚举移到 `Core` 命名空间** — 会破坏 `EmguALG` 命名空间下其他文件的引用
3. **保持两份定义** — 违反 DRY，同步风险高

## 后果

### 正面
- 消除枚举解析歧义
- 减少代码重复（删除 27 行冗余定义）
- 统一枚举管理入口

### 负面
- 无

## 相关页面

- [[modules/EmguALG]]
- [[lessons/CSharp-Language-Pitfalls]]
- [[decisions/ADR-001-CS73-Constraint]]
