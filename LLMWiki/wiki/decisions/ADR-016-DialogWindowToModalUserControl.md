---
title: ADR-019 子对话窗承载方式：AntdUI.Window+PageHeader → Modal 承载的 UserControl
date: 2026-07-30
tags: [决策, UI, AntdUI, Modal, UserControl, 对话窗]
status: accepted
---

# ADR-019 子对话窗承载方式改为「Modal 承载的 UserControl」

## 背景

2026-07-30 上午曾落地 `lessons/AntdUI-Window-PageHeader-Top`：8 个 sub2/sub3 对话窗统一 `AntdUI.Window` + 顶部 `PageHeader`（`ControlBox=false`）。但研读 AntdUI 官方 Demo（`MainWindow.buttonSZ` → `SystemSet`）发现：AntdUI 推荐以 **`AntdUI.Modal` 承载 `UserControl`** 的方式弹出对话窗，而非新开 `AntdUI.Window`。`PageHeader` 应由 `Modal` 自带的标题栏取代，避免双标题栏与重复样板。

## 决策

1. **对话窗改为 `UserControl`**：原 8 个 `AntdUI.Window` 对话窗（LLCameraSetting / ConfigForm / AutoParamForm / FileTraceForm / RecordConfigForm / RenderParamForm / ILAlgorithmEditForm / UserEditForm）基类改为 `System.Windows.Forms.UserControl`，统一迁入 `UIDesign/SubDialog/`，**取消 PageHeader**。
2. **以 `AntdUI.Modal` 承载**：调用点改用
   ```csharp
   using (var form = new XxxForm())
   {
       AntdUI.Modal.open(new AntdUI.Modal.Config(owner, "标题", form, TType.Info)
       {
           CloseIcon = true,
           BtnHeight = 0
       });
   }
   ```
   - `owner`：`UserControl` 内调用用 `this.FindForm()`；`Window`/`Form` 内调用（如 `LoginForm`）用 `this`（Modal 的 owner 是 `Control`/`IWin32Window`，UserControl 合法）。
3. **命名空间保持不变**：仍为 `AdaWeldSystem.Sub3UI` / `AdaWeldSystem.Sub2UI`，避免全项目 `using` 连锁改动（仅 .cs 物理路径变更，故需同步更新 `.csproj` 的 `Compile`/`EmbeddedResource` 路径为 `SubView/`，并将 `SubType` 改 `UserControl`）。
4. **关闭/返回值**：`UserControl` 无 `DialogResult`/`Close`，改用 `var host = this.FindForm(); if (host != null) host.DialogResult = DialogResult.OK;`（Modal 内部即 `ShowDialog` 的 `Form`，设 `DialogResult` 即关闭并令 `Modal.open` 返回该值；Demo `TableDemo.cs` 的 `Modal.open(...)==DialogResult.OK` 证实此语义）。`Message.*(this,…)` 全部改 `Message.*(this.FindForm(),…)`（UserControl 不能隐式转 `Target`，详见 [[guides/AntdUI-Reference]]）。
5. **生命周期事件**：原 `FormClosing` 资源管理（如 ILAlgorithmEditForm 停英莱页定时器）改订阅 `HandleDestroyed`（UserControl 无 FormClosing；遵循 [[decisions/ADR-001-DisposePattern]] 不重写 `Dispose(bool)`）。

## 备选方案

| 方案 | 优点 | 缺点 | 是否采用 |
|------|------|------|---------|
| Window + PageHeader（旧） | 独立窗体、设计器直观 | 双标题栏风险、重复 PageHeader 样板、与官方 Demo 范式不一致 | 不采用（已被本 ADR 取代） |
| Modal 承载 UserControl（新） | 官方推荐范式、无双标题栏、标题由 Modal 提供、调用点统一 | UserControl 无 DialogResult/Close 需改关闭写法、需更新 .csproj 路径 | **采用** |

## 后果

### 正面
- 与 AntdUI 官方 Demo 对话窗范式一致
- 去掉 8 份 PageHeader 样板与 `ControlBox=false` 等窗体专属属性
- `Modal` 自带标题栏/关闭 X，调用点收敛为统一范式

### 负面 / 注意
- `UserControl` 无 `DialogResult`/`Close`/`FormClosing`：关闭/返回值/资源回收写法须相应改造（见上）
- `.csproj` 路径须同步更新（`SubView/` + `SubType=UserControl`），否则编译报文件缺失
- resx 中 `$this.Type` 若仍引用 `AntdUI.Window` 须改 `System.Windows.Forms.UserControl`（ConfigForm.resx 已修；其余 resx 无根类型引用则无需）

## 关键约束
- 仍须遵守 [[decisions/ADR-001-DisposePattern]]（不重写 `Dispose(bool)`，用 `DisposeComponents()`；`Dispose(bool)` 仅存在于生成态 Designer.cs）
- 仍须遵守 [[guides/Namespace-Compilation]]（新建/移动文件须注册 `.csproj`）
- `Modal` 的 owner 为 `Control`/`IWin32Window`（非 `Message` 的 `Target`）：UserControl 内用 `this.FindForm()` 锚定父窗体

## 相关页面
- [[guides/AntdUI-Reference]] —— 本决策落地范式与踩坑
- [[guides/AntdUI-Reference]] —— **已被本 ADR 取代**（2026-07-30 上午的旧范式）
- [[guides/AntdUI-Reference]] —— Modal/Message 的 owner 类型与 UserControl 锚定
- [[modules/UIDesign]] —— UI 模块结构与继承关系表
- [[decisions/ADR-015-UIFrameworkMigration]] —— AntdUI 迁移总决策
