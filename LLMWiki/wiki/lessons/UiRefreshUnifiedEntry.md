---
title: UI 状态刷新统一入口
date: 2026-08-24
updated: 2026-11-23
tags: [教训, UI, 状态刷新, 代码精简, 重构]
status: active
source: AdaWeldSystem/UIDesign/TabPage/LineLaserCamPage.cs
---

# UI 状态刷新统一入口（LineLaserCamPage 实践）

> 迭代中按"场景补函数"容易在页面里散落多个状态变更入口（连接态/模式/硬件同步各写一个），
> 调用关系互相嵌套、刷新顺序不统一，后续改动极易漏刷某块 UI。

## 反模式（踩坑）

`LineLaserCamPage` 曾同时存在三个"状态变更"函数：

- `UpdateConnectionUi()` — 连接态标签/按钮唯一刷新（ADR-007 状态标签规范）
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
- 与 ADR-007（状态标签唯一刷新）、ADR-009（代码精简）一致。

## 关联

- [[modules/UIDesign]] — LineLaserCamPage 状态刷新说明
- [[decisions/ADR-023-LineLaserWorkflowRefactor]] — 状态机外发驱动刷新
- [[guides/WinForms-UI-Threading]] — InvokeRequired 封送
## 2026-11-17 补充：跨线程刷新 + 每拍整表重绑 = 卡顿与显示异常根因

- **现象**：系统设置页点轴运动按钮后界面卡顿、显示跳变；工艺设置页 TA 指令区状态显示混乱。
- **根因**：① 刷新节拍用 `Task.Run` 采集 + `BeginInvoke` 回贴（跨线程封送竞态）；② 每拍 `table.Binding(...)` 整表重绑（UI 线程全量重建）；③ 点击路径又同步调 `RefreshRuntime()` 再整表重绑 ⇒ 两路争抢同一批控件。
- **判据**：刷新节拍含 `Task.Run` / `BeginInvoke` ⇒ 命中；每拍无条件整表 `Binding` ⇒ 命中；UI 线程调用会阻塞等硬件的轴方法（如 `AbsMove`）⇒ 命中。
- **预防**：
  - ⛔ UI 刷新禁跨线程：采集与贴值都在 UI 线程同步完成（只读硬件摘要，微秒级）。
  - ⛔ 表格改**差分才重绑**：读数签名比对，值不变不 `Binding`。
  - ⛔ 刷新只做**显示信息**；按钮管控与状态判定改事件驱动，由单一控制函数统一算（见 [[standards/UiStateSimplification]]）。
  - ⛔ UI 线程禁调阻塞等硬件的轴方法：手动移动走非阻塞下发，等待到位交后台线程 + 执行消息。

## 2026-11-17 补充：按钮管控的作用域必须按设备/电机隔离

- **现象**：系统设置页点「TA 回零」，Y 轴 / LA / GA 的按钮也一起变灰。
- **根因**：页面用一个**全局**忙标志推导全部按钮的可用性 ⇒ 一个电机的在途操作牵连了其它电机。
- **判据**：按钮可用性由单个全局标志统一推导 ⇒ 命中（跨设备/跨电机场景必现误禁）。
- **预防**：
  - 按钮管控按**电机/设备分组**各自独立：一个电机的在途操作只禁用它自己那组按钮。
  - ⛔ 例外不可分组：**停止类必须永远可用**（安全操作要能随时中断）；**点动键不进「禁用」模型**（禁用会丢 `MouseUp` ⇒ 点动停不掉）。
  - ⛔ 构造期**不读主控单例**（`DeviceControlWork.Instance` 会触发整机初始化）；运行期判据用事件驱动缓存，流程层门禁作主防线。

## 相关页面

- [[index/index]]
