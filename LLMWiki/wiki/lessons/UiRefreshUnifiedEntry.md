---
title: UI 状态刷新统一入口
date: 2026-08-24
tags: [教训, UI, 状态刷新, 代码精简, 重构]
source: AdaWeldSystem/UIDesign/TabPage/ILCamPage.cs
---

# UI 状态刷新统一入口（ILCamPage 实践）

> 迭代中按"场景补函数"容易在页面里散落多个状态变更入口（连接态/模式/硬件同步各写一个），
> 调用关系互相嵌套、刷新顺序不统一，后续改动极易漏刷某块 UI。

## 反模式（踩坑）

`ILCamPage` 曾同时存在三个"状态变更"函数：

- `UpdateConnectionUi()` — 连接态标签/按钮唯一刷新（ADR-022 状态标签规范）
- `UpdateModeUi()` — 工作流态→手动按钮可用性 + 设 `IsManualMode`；**内部又调 `UpdateConnectionUi()`**
- `SyncFromHardwareAfterConnect()` — 连接后从硬件同步激光/相机/Job/帧率

三者的调用方分散在：构造函数、`btnConnect_Click`、工作流 `StateChanged` 回调（`OnWorkflowStateChanged`）、
状态机 `StateChanged` 回调（`OnIlStateChanged`）。`UpdateModeUi→UpdateConnectionUi` 嵌套 + 各回调又各调一遍，
造成"谁该调谁"职责不清、刷新顺序依赖隐式约定。

## 统一方案（推荐范式）

引入单入口 + `[Flags]` 范围枚举，把碎片函数降级为 private 实现：

```csharp
[Flags]
private enum RefreshUiScope
{
    Connection = 1,  // 原 UpdateConnectionUi
    Mode      = 2,  // 原 UpdateModeUi
    Hardware  = 4   // 原 SyncFromHardwareAfterConnect
}

private void RefreshUi(RefreshUiScope scope)
{
    if (IsDisposed || Disposing) return;
    if (InvokeRequired) { BeginInvoke(new Action(() => RefreshUi(scope))); return; }
    if ((scope & RefreshUiScope.Connection) != 0) UpdateConnectionUiCore();
    if ((scope & RefreshUiScope.Mode)      != 0) UpdateModeUiCore();
    if ((scope & RefreshUiScope.Hardware)  != 0) SyncFromHardwareCore();
}
```

- 旧三函数重命名为 `UpdateConnectionUiCore` / `UpdateModeUiCore` / `SyncFromHardwareCore`，
  **仅被 `RefreshUi` 调用**，删除它们之间的互相嵌套（如 `UpdateModeUi` 不再内联 `UpdateConnectionUi`，由调用方显式 `Mode | Connection` 组合）。
- 所有对外调用点（构造函数 / 按钮 / 两类 `StateChanged` 回调）统一改为 `RefreshUi(scope)`，
  范围按需按位或组合（如 `Connection | Mode`、`Mode | Connection`、`Hardware`）。
- `RefreshUi` 内置 `InvokeRequired` 封送，后台线程回调无需各自再写一遍（但仍保留调用方自身的 `IsDisposed` 守卫习惯亦可）。

## 适用原则

- UI 页面凡有多于 1 个"刷新状态"的函数，先判断是否可归并为一个 `RefreshXxx(scope)` 入口。
- `scope` 用 `[Flags]` 枚举，避免"全量刷新"浪费（如仅连接态变更也去读硬件帧率）。
- 调用方决定"刷新什么"（组合 scope），实现方决定"怎么刷"（*Core 内部），职责清晰、无隐式嵌套。
- 与 ADR-022（状态标签唯一刷新）、ADR-023（代码精简）一致。

## 关联

- [[modules/UIDesign]] — ILCamPage 状态刷新说明
- [[decisions/ADR-021-LineLaserWorkflowRefactor]] — 状态机外发驱动刷新
- [[guides/WinForms-UI-Threading]] — InvokeRequired 封送
