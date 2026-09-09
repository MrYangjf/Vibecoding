---
title: ADR-001 Dispose 模式决策
date: 2026-07-01
tags: [决策, UI, 资源释放, WinForms]
status: accepted
---

# ADR-001 Dispose 模式决策

## 背景

WinForms 设计器生成的 `*.Designer.cs` 文件包含 `Dispose(bool)` 方法。需要释放自定义 IDisposable 资源（如 HelixToolkit 渲染引擎）时，直接修改 Designer.cs 会导致设计器报错。

## 决策

**适用范围（2026-08-19 澄清，见 [[decisions/ADR-020-DisposePatternFullCoverage]]）：**

- **`DisposeComponents()` 模式仅用于 UI 设计器类**（Form / UserControl 及其 `.cs` 后置代码）——因为 UI 类继承自 `Control`，重写 `Dispose(bool)` 会与设计器生成代码冲突。
- **UI 类也按需使用**：仅当持有「外部嵌套控件/独立资源」（设计器 `Dispose(bool)` 覆盖不到的对象）时才写 `DisposeComponents()`；无嵌套、无独立资源则不需要。
- **非 UI 类（后端类）不得使用 `DisposeComponents()`**，必须实现标准 `IDisposable.Dispose()` 接口并正确释放资源（2026-08-19 全项目迁移落地）。

UI 类使用 `DisposeComponents()` 公共方法模式：

1. 不在 Designer.cs 中修改 Dispose
2. **禁止在 UI 类的 `.cs` 文件中重写或新增 `Dispose(bool)` 方法**（会与 Designer.cs 生成的 Dispose 冲突，且设计器会报错）
3. 在 `.cs` 文件中定义 `DisposeComponents()` 方法
4. 父页面关闭时调用 `DisposeComponents()`

## 后果

### 正面

- 避免设计器报错
- 资源释放逻辑与业务代码在一起，便于维护
- 不影响设计器自动生成的代码
- 非 UI 类统一标准 `IDisposable.Dispose()`，调用方（按接口释放）可正确释放资源

### 负面

- 需要手动确保父页面调用 DisposeComponents
- 不如重写 Dispose 标准
- 非 UI 类需自行确保 Dispose() 被调用（调用链由父容器/主窗体关闭时级联触发，见 [[modules/DeviceControl]]）

## 相关页面

- [[decisions/ADR-020-DisposePatternFullCoverage]]
- [[guides/WinForms-Designer]]
- [[modules/UIDesign]]

