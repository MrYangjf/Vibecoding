---
title: ADR-036 UI 层级与控件归位规则（TabPage/ControlPage 弹窗必须归入 SubDialog）
date: 2026-09-18
updated: 2026-10-30
tags: [决策, UI, UIDesign, 目录结构, SubDialog, ADR-005, ADR-009]
status: accepted
---

# ADR-036 UI 层级与控件归位规则（对话窗必须归入 SubDialog）

> **闭合关系**：本 ADR 是 [[decisions/ADR-005-NamespaceDirectoryAlignment]]（命名空间随目录）与 [[decisions/ADR-009-DialogWindowToModalUserControl]]（对话窗 = Modal 承载的 UserControl）在 **UIDesign 目录层级**上的落地细则。ADR-005 规定「namespace = AdaWeldSystem + 目录路径」、ADR-009 规定「对话窗一律 Modal 承载的 UserControl」，本 ADR 进一步明确「哪些控件该放在哪一层目录」，把二者从原则变为可执行的归位红线。

## 背景

`UIDesign/` 经 2026-08-05（`Sub2UI/`→`TabPage/` 等）、2026-09-07（`SubView/` 按业务域拆为 `SubDialog/` 下 7 个子目录）两次重构，形成「`MainWindow/` · `ControlPage/` · `TabPage/` · `SubDialog/<业务域>Dialog/`」四级结构。

但 2026-09-17 的 `MontionConfigForm` 整体迁入 `MotionControlPage.panel1` 之后，3 个运控参数编辑器（`AxisConfigEditor`/`IoConfigEditor`/`CylinderConfigEditor`）仍**错误地留在 `TabPage/MotionConfigEditors/`** 下——它们虽已是 Modal 承载的 UserControl（符合 ADR-009），却违反了「页面弹出的对话框归 SubDialog」的层级契约，造成 `TabPage` 同时承载「页面」与「对话窗」两类控件、命名空间归属含糊。

2026-09-18 已将这 3 个编辑器迁至 `SubDialog/MotionControlDialog/` 并改名为 `XxxConfigForm`（ADR-005 命名空间随之对齐）。本 ADR 把该次修正**固化为硬约束**，防止回归。

## 决策

### 四级目录职责（固定）

| 层级目录 | 承载 | 基类 | 命名空间 | 示例 |
|----------|------|------|----------|------|
| `MainWindow/` | 主窗口（唯一） | `AntdUI.Window` | `AdaWeldSystem.UIDesign.MainWindow` | `FormMain` |
| `ControlPage/` | 页面级 UserControl（FormMain 的 Tabs 承载） | `UserControl` | `AdaWeldSystem.UIDesign.ControlPage` | `MainPage` / `NavPage` / `DataReviewerPage` |
| `TabPage/` | 页面级 UserControl（功能分页） | `UserControl` | `AdaWeldSystem.UIDesign.TabPage` | `ILCamPage` / `ParamConfigPage`（现役 `ProcessControlPage.cs`） / `CommPage`（现役 `FilebackupPage.cs`） / `MonitorCamPage` / `MotionControlPage`（现役 `SystemControlPage.cs`） |
| `SubDialog/<业务域>Dialog/` | Modal 承载的对话窗 UserControl | `UserControl` | `AdaWeldSystem.UIDesign.SubDialog.<业务域>` | `MotionControlDialog/{AxisConfigForm,IoConfigForm,CylinderConfigForm}` 等 |

### 归位红线（硬约束）

1. **页面与对话窗分离**：`TabPage/` 与 `ControlPage/` 只放「页面级 UserControl」（由 FormMain 的 `AntdUI.Tabs` 承载的功能页）；**任何由这些页面点击弹出的对话框，必须归入 `SubDialog/<业务域>Dialog/`**，不得停留在 `TabPage/` 或 `ControlPage/` 下。
2. **对话窗承载方式**（继承 ADR-009）：一律 `UserControl` + `AntdUI.Modal.open(new Modal.Config(owner, 标题, form, TType.Info){CloseIcon=true,BtnHeight=0})` 弹出，禁 `AntdUI.Window`+PageHeader。
3. **命名空间随目录**（继承 ADR-005）：对话窗命名空间 = `AdaWeldSystem.UIDesign.SubDialog.<业务域>Dialog`；移动/新建对话窗须同步 `.csproj` 的 `<Compile Include>`（[[guides/Namespace-Compilation]]）。
4. **业务域对齐**：对话窗按业务归属 `SubDialog/` 下对应 `<业务域>Dialog/` 子目录（运控→`MotionControlDialog/`、通讯→`CommConfigDialog/`、英莱→`IntelligentLaserDialog/` 等），与 2026-09-07 目录重构保持一致。

### 反模式（禁止）

- ❌ 在 `TabPage/MotionConfigEditors/` 之类子目录下放对话窗（2026-09-18 前 `AxisConfigEditor` 等的历史错误）。
- ❌ 用 `AntdUI.Window` + PageHeader 承载对话窗（ADR-009 已废止）。
- ❌ 对话窗命名空间写成 `AdaWeldSystem.UIDesign.TabPage.Xxx`（层级与目录不符，ADR-005 违规）。

## 备选方案

| 方案 | 优点 | 缺点 | 是否采用 |
|------|------|------|---------|
| 对话窗留在 TabPage/（旧） | 调用点 using 距离近 | 页面/对话窗混放、命名空间含糊、破坏四级契约 | 不采用 |
| 对话窗统一归入 SubDialog/<业务域>Dialog/（新） | 层级清晰、命名空间自洽、与 ADR-005/009 一致 | 调用点需改 using + csproj 路径 | **采用** |

## 后果

### 正面
- `TabPage/` 重新只承载页面，四级目录职责单一、可读。
- 对话窗命名空间与磁盘路径严格一致（ADR-005 零欠账）。
- 新增对话窗有确定归宿，不再临时塞进页面目录。

### 负面 / 注意
- 移动对话窗须同步 `.csproj` 的 `<Compile Include>` 与调用点 `using`（已纳入 [[guides/Namespace-Compilation]] 流程）。
- 真编译需在 Visual Studio 验证（本环境治理无 C# 编译器，仅做静态校验）。

## 关键约束
- 继承 [[decisions/ADR-005-NamespaceDirectoryAlignment]]：命名空间 = AdaWeldSystem + 目录路径。
- 继承 [[decisions/ADR-009-DialogWindowToModalUserControl]]：对话窗 = Modal 承载的 UserControl。
- 遵守 [[guides/Namespace-Compilation]]：移动文件须登记 `.csproj`。
- 不重写 `Dispose(bool)`（ADR-002）：对话窗 UserControl 用 `DisposeComponents()`（如持有外部资源）。

## 相关页面
- [[decisions/ADR-005-NamespaceDirectoryAlignment]] — 命名空间与目录严格对齐
- [[decisions/ADR-009-DialogWindowToModalUserControl]] — 对话窗承载方式
- [[modules/UIDesign]] — UI 模块结构与「UI 层级与控件归位规则」小节
- [[guides/Namespace-Compilation]] — 命名空间与编译错误（CS0118 等）、.csproj 注册
- [[api/SystemControlPage]] — 本次归位的 3 个 `XxxConfigForm` 调用点
