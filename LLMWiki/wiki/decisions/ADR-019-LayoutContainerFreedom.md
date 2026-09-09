---
title: ADR-022 布局容器自由化（解除 GridPanel/FlowPanel 强制使用）
date: 2026-08-12
tags: [决策, UI, AntdUI, GridPanel, FlowPanel, 布局]
status: accepted
---

# ADR-022 布局容器自由化（解除 GridPanel/FlowPanel 强制使用）

## 背景

此前的 UI 设计与范式 lessons 形成了一条**硬约束**：所有 UI 容器"必须使用 `AntdUI.GridPanel`"（大区域分割）与 `AntdUI.FlowPanel`（表单流式排列），甚至在 `UIDesign` 模块文档中将其列为固定布局控件、在 memory 约束中记录为 mandatory。

这两类容器存在**强制排序**行为，给布局带来不便：

- `GridPanel` 的子控件按 `Controls.Add` 的**逆序**入格（`SyncMap` 倒插+排序），Designer 中必须把 Add 顺序写成期望格子顺序的倒序，或用 `SetIndex` 显式指定序号，易错且反直觉。
- `FlowPanel` 按 `Controls.Add` 顺序自动从左到右流式排列并自动换行，无法精确控制每个控件的绝对位置。

用户（2026-08-12）明确要求：**不再强行使用 GridPanel 和 FlowPanel，因为它们会强行排序**。需要解除这一强制约束，允许按需自由选择布局方式。

## 决策

1. **解除 `GridPanel`/`FlowPanel` 的强制使用约束**，布局容器改为**按需自由选择**。开发时可根据具体布局需求选用 `GridPanel`、`FlowPanel`、`Panel` 绝对定位、`Dock`/`Anchor` 或 WinForms 原生布局容器等任一方式。
2. **保留 AntdUI 整体风格**：项目 UI 主体仍为 AntdUI 风格（[[decisions/ADR-015-UIFrameworkMigration]] 的框架约束不因本 ADR 改变）。
3. **控件回退规则**：AntdUI 缺失的控件，允许使用 **WinForms 原生控件**作为回退。
4. **SunnyUI 控件一律禁止**使用（AntdUI 迁移的底层约束，sunnyUI 为 GPL 许可，见 [[decisions/ADR-015-UIFrameworkMigration]]）。
5. **不重写已有页面**：已用 `GridPanel`/`FlowPanel` 实现的 9 个页面（MainPage / DataReviewerPage / CommPage / MotionControlPage / ParamConfigPage / ILAlgoForm / HelixRenderForm / AutoParamForm 等）功能正常，**不强制重写**，由用户自行判断是否调整。
6. **若仍使用 `GridPanel`/`FlowPanel`**，必须遵守其各自的既布局规则（`GridPanel` 逆序入格、`FlowPanel` Align=Left+Gap+顺序 Add），这些规则是「使用该容器时的技术知识」，而非「强制使用该容器的理由」——见 [[guides/AntdUI-Reference]]、[[guides/AntdUI-Reference]]。

## 备选方案

- **维持强制 GridPanel/FlowPanel 不变**：保持现状，但用户明确其排序行为造成困扰，故放弃。
- **改用单一绝对定位**：所有页面改为 `Location` 绝对定位，布局可控但失去自适应/响应式，不利于窗口缩放，故不全面采用，仅作为可选方式之一。

## 后果

### 正面
- 布局方式回归自由，开发者可按需选择最直观、最不易出错的容器。
- 消除 `GridPanel` 逆序入格、`FlowPanel` 自动换行带来的强排序心智负担。
- 约束更贴近实际：AntdUI 无所需控件时可用原生控件兜底。

### 负面
- 布局风格可能在某些页面间不一致（部分 GridPanel、部分原生/绝对定位），需在代码审查时人工把握统一性。
- 后续新页面若用了其他容器，`GridPanel` 相关 lessons 的"逆序入格"等规则不再自动适用，需按所选容器各查其规则。

## 相关页面

- [[guides/AntdUI-Reference]]
- [[guides/AntdUI-Reference]]
- [[modules/UIDesign]]
- [[decisions/ADR-015-UIFrameworkMigration]]