---
title: ADR-016 监控相机页面命名与算法参数内联
date: 2026-07-17
tags: [决策, 监控相机, UI, 命名, 算法编辑]
status: accepted
source: 用户需求「MonitorCamWorkJob 命名修改，没有 workjob」「界面修改：没有贴合算法的流程，直接将监控算法编辑放在右侧」
---

# ADR-016：监控相机页面命名与算法参数内联

> 📌 **实现控件已随 [[decisions/ADR-021-UIFrameworkMigration]] 迁移为 AntdUI**：本文描述的 `UIGroupBox`/`UIPanel` 等容器现对应 `System.Windows.Forms.GroupBox`；状态指示改用 `AntdUI.Signal`（原 UILight）。本 ADR 的**命名与「算法参数内联于右侧面板」决策精神不变**。

## 背景

原监控相机 UI 页命名为 `MonitorCamWorkJob`，但监控相机只做焊缝检查、无多种类、也没有 JOB 切换概念（算法配置已由 [[api/MonitorAlgorithmManager]] 单一可配置 Profile 承担，见 [[decisions/ADR-015-WorkflowAsHub]]）。`WorkJob` 后缀与项目 `Sub2UI` 既有的 `XxxPage` 命名约定（`MotionControlPage` / `ParamConfigPage` / `CommPLCPage`）不符，且语义误导。

同时，监控算法仅有 4 个参数（对中容差 X / Y / 角度、质量合格分），内容少、无需独立编辑弹窗。用户要求去掉贴合算法的流程与独立编辑界面，将算法编辑直接放在右侧 `panelRight`。

## 决策

1. **页面重命名 `MonitorCamWorkJob` → `MonitorCamPage`**（位于 `UIDesign/Sub2UI/`，继承 `UIPage`，由 `Sub1UI/ImagePage.cs`「监控画面」节点承载）。与 `Sub2UI` 的 `XxxPage` 约定一致，明确「这是监控相机页面、非作业」。
2. **算法参数内联于右侧 `panelRight`**：新增 `UIGroupBox uiGroupBoxAlgorithm`（标题「算法参数」）→ 嵌套 `TableLayoutPanel`，4 行「标签 + `UITextBox`」承载 `AlignmentConfig.ToleranceX/Y/Angle` 与 `QualityConfig.PassScore`，底部「保存算法参数」按钮（`btnSaveAlgorithm`）写回 [[api/MonitorAlgorithmManager]] 单例并调用 `Save()` 持久化到 `Config/INI/MonitorAlgorithm.ini`。**不引入独立算法编辑弹窗**。

## 关键设计

- 页面构造期从 `MonitorAlgorithmManager.Instance` 读取并填充 4 个文本框（单例 `Load()` 已在 `FormMain` 启动期调用，页面只读取，参见 [[guides/Project-Tools]]）。
- 「保存算法参数」为显式按钮（非实时自动保存），与 `MotionControlPage` 的显式保存范式一致，避免误改误存；解析失败回退原值，不破坏既有配置。
- 右侧面板依旧是绝对定位的 `UIPanel`：`uiGroupBoxAlgorithm` 置于 `txtResult` 下方（10,205 / 292×195），`chkLive` 下移到 (10,410) 避免重叠；布局变更不引入 `InitializeComponent` 内的流程控制语句（遵循 CSharpStyle 与 Designer 约定）。
- 重命名为纯重命名，行为不变；同步更新 `.cs` / `.Designer.cs` / `.csproj`（Compile + DependentUpon）/ `ImagePage.cs` 引用四处，无新增文件。

## 后果

- 优点：命名与项目约定统一、无误导性语义；算法编辑零跳转、所见即所得，符合「内容少就内联」的轻量交互。
- 代价：无新增文件/弹窗，维护面更小；`panelRight` 控件密度略增（仍在 590 高度内）。

## 涉及约束

- [[decisions/ADR-001-DisposePattern]] ✅（DisposeComponents，不重写 Dispose）
- [[decisions/ADR-002-CS73-Constraint]] ✅
- [[decisions/ADR-008-ConfigLayout]] ✅（算法 INI 归 Config/INI）
- [[decisions/ADR-011-MonitorCameraModule]] ✅（Run/Workflow 分离保留）
- [[decisions/ADR-015-WorkflowAsHub]] ✅（算法管理器单一 Profile 复用）
- [[guides/Namespace-Compilation]] ✅（改名即重注册 .csproj）
- [[guides/WinForms-Designer]] ✅（仅 Designer 生成 Dispose）
- [[guides/Project-Tools]] ✅（先 Load 后取/存）
- [[guides/WinForms-UI-Threading]] ✅（事件处理检查 InvokeRequired）

---

*来源：AdaWeldSystem/UIDesign/Sub2UI/MonitorCamPage.cs(.Designer.cs) + 用户需求*
