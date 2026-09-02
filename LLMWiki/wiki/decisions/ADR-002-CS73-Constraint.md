---
title: ADR-002 C# 7.3 语法约束决策
date: 2026-07-01
tags: [决策, 语法, 编译器, MSBuild]
status: accepted
source: history.md [44]
---

# ADR-002：C# 7.3 语法约束决策

## 背景

项目使用 .NET Framework 4.8，但 MSBuild 工具链版本为 v4.0（随 Visual Studio 2015 或旧版 MSBuild 安装）。部分 C# 7.0+ 语法在 MSBuild v4.0 编译器中会报 CS1519 错误。

## 决策

限制代码使用 **C# 7.3 及以下** 语法，并明确以下禁止项：

| 禁止语法 | 错误示例 | 正确写法 |
|----------|---------|---------|
| auto-property initializer | public int X { get; set; } = 1; | 在构造函数中初始化 |
| 表达式体属性 | public int X => _x; | public int X { get { return _x; } } |
| out var | Method(out var x); | int x; Method(out x); |
| 元组解构 | (int x, int y) = tuple; | 单独赋值 |

## 后果

- 确保 MSBuild v4.0 编译通过
- 代码兼容性更广
- 牺牲部分现代 C# 语法糖

---

*来源：raw/history/history.md [44]*
