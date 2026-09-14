---
title: ADR-014 算法编辑界面按接口分隔（Tabpage / UIPage + AddPage，单独个例仅记录为当前）
status: accepted
date: 2026-07-27
tags: [决策, UI, 算法编辑, 接口分隔, 英莱, Tabpage, SunnyUI, UIPage, AntdUI(迁移后)]
source: 用户需求「将我自有算法和英莱的相机算法分隔开，使用不同的接口」+「在算法编辑界面根据不同的接口判断界面样式，使用对应的算法编辑页面（使用Tabpage方法，根据选择隐藏不使用的那一个）」
---

> ⚠️ 历史名称提示：本页为**历史决策记录**，正文中的下列文件名为决策当时的旧名，
> 保留原文以留存上下文，现役对应如下：
>
> - `ImagePage.cs` → 现役 `UIDesign/TabPage/MonitorCamPage.cs`
> - `ParamPage.cs` → 现役 `UIDesign/TabPage/ParamConfigPage.cs`
>

# ADR-014 算法编辑界面按接口分隔（Tabpage / UIPage + AddPage，单独个例仅记录为当前）

> 📌 **界面框架描述已随 [[decisions/ADR-015-UIFrameworkMigration]] 更新**：本 ADR 撰写时 UI 框架为 SunnyUI，故描述「`UITabControl` + `UIPage` + `AddPage`」。迁移后实际为 **`AntdUI.Tabs` + `UserControl` + `AddTabSelect(UserControl)`**（见 `ILAlgorithmEditForm.Designer.cs`）。**接口分隔的核心决策（自有算法与英莱相机算法分两个页）不变**。

## 背景（Context）

- 算法编辑窗体 `ILAlgorithmEditForm`（`UIDesign/Sub3UI/`）原本只服务**项目自有算法 (EmguALG)**：配置 `PipelineConfig` 的 5 个阶段（滤波/形态学/边缘检测/特征提取/模板匹配）的方法与参数。
- 新增 **英莱相机 (IntelligentLaser)** 后，英莱 SDK 自带算法路线（消费 `InspectResult` + 配置 Job Parameter），与 EmguALG 是**两套完全不同的接口**，不应混在同一组控件里编辑。
- 用户要求**用 Tabpage**，按当前激活相机接口**只显示对应编辑页、隐藏另一页**。
- ⚠️ **关键事实纠正**：SunnyUI 命名空间**不存在 `UITabPage` 类型**（原 2026-07-17「弃 Tab」惯例正是因此）。本项目真实的 Tab 机制是 `UITabControl.AddPage(UIPage)`——`ParamPage.cs`/`ImagePage.cs`/`FormMain.cs` 均以 `uiTabControl1.AddPage(某 UIPage 实例)` 挂载标签页。本 ADR 严格采用该真实机制，不臆造不存在的类型。
- 同时与新 WIKI\算法 的迁移要求对齐：自有算法与相机算法走**不同接口**，UI 据此切换页。

## 决策（Decision）

1. **界面框架：SunnyUI `UITabControl` + 两个 `UIPage` 子页**（**纠正**：无 `UITabPage`；用 `AddPage(UIPage)`）。本窗体作为**单独个例**采用 Tabpage；**不推翻** 2026-07-17 项目级「弃 Tab」惯例，仅作当前特例记录，其他页面仍维持无 Tab 约定。
   - `EmguAlgoPage : UIPage` = "项目算法 (EmguALG)"，承载模块 A（阶段/方法/启用/参数网格）。
   - `ILAlgoForm : UIPage` = "英莱相机算法 (IntelligentLaser)"，承载模块 B（连接态标签、从设备读取/下发按钮、Job 参数网格、实时识别结果只读网格）。`UIPage.Text` 即标签页标题。
   - 底部 `tableLayoutPanelButtons`（确定/取消）**常驻可见**，置于 `UITabControl` 之外，不随页切换。
2. **按接口判定显示哪一页（条件 AddPage）**：构造期 `_ilCamera = CameraSelector.Active as IntelligentLaserCameraRun;` 之后，**仅 `AddPage` 对应那一页**：
   - `_ilCamera != null`（当前激活相机为英莱）→ `new ILAlgoForm(_ilCamera)` 并 `uiTabControl1.AddPage(_ilPage)`；
   - 否则（EmguALG / SmartRay / 虚拟等）→ `new EmguAlgoPage(_config)` 并 `uiTabControl1.AddPage(_emguPage)`。
   - **另一页根本不创建、不 AddPage** → 自然「隐藏不使用的那一个」。这比运行时 `RemovePage`/`SelectedTab` 更稳，且完全规避了不存在的 `UITabPage`/`TabPages.Remove` API。
3. **接口隔离维持既有边界**：模块 B 仍经 `IntelligentLaserCameraRun.IlJobParamInfo` / `FetchAllJobParams` / `ApplyJobParams` / `IlInspectResult` 等既有接口读写英莱参数，**UI 绝不直连 `IntelligentLaser_export`**（见 SDK 开发手册 §7）。模块 A 仍只编辑 `PipelineConfig`，与英莱零耦合。
4. **分阶段落地（本 ADR 范围）**：本会话只做「接口分隔 + Tabpage UI（UIPage + AddPage）+ 两个编辑页」，EmguALG 既有 `PipelineConfig` 算法**不做深度重写**；新 WIKI\算法 提出的 `AlgorithmBase`/`SeamRecognition`/`RealtimeMonitor`/`ProfileTransform` 多文件架构**延后到下一阶段**（保留 [[decisions/ADR-038-EmguALGThreeLayer]] 现状）。

## 关键设计

- 构造期只 `AddPage` 一页；窗口生命周期内激活相机不变，故无需运行时动态切换页。
- 设计器 `InitializeComponent()` 仍零流程控制：两个子页各自为独立 `UIPage`（各带 `.Designer.cs`），宿主窗体 `ILAlgorithmEditForm.Designer.cs` 仅声明 `UITabControl` + 底部按钮，不含子页控件。
- 新增 2 个 `.cs` + 2 个 `.Designer.cs`（`EmguAlgoPage` / `ILAlgoForm`），已在 `AdaWeldSystem.csproj` 登记 `Compile`（含 `<DependentUpon>`）。
- 生产蓝图：`deliverables/gstack/il-algo-ui-tabpage-blueprint-2026-07-27.html`（注意：该蓝图标注用了 `UITabPage`，已被本 ADR 的真实 `UIPage + AddPage` 实现取代，蓝图仅作视觉参考）。

## 后果（Consequences）

- ✅ 自有算法与英莱相机算法在 UI 层彻底分隔，按接口自动呈现对应编辑页，满足用户「不同接口用不同算法编辑页」诉求。
- ✅ 本窗体作为**单独个例**采用 `UIPage + AddPage` 的 Tabpage，已在本文记录为「当前特例」；**不视为项目级惯例反转**，其他页面仍维持无 Tab 约定（除非另有 ADR）。
- ✅ 复用已有 `IntelligentLaserCameraRun` 接口，未引入新耦合；模块 A/B 逻辑各自独立、互不干扰。
- ⚠️ 单页剩余时 `UITabControl` 仍显示该页标签条（仅一个标签），属预期；若后续希望完全隐藏标签条，可追加 `uiTabControl1.TabVisible = false`（但会失去接口提示，本 ADR 保留标签条）。
- ⚠️ 英莱 Job Parameter 结构体的 CppSharp 生成成员名（`TIntelligentJobParam.CurValue` 联合成员、`TIntelligentJobParamsGroup` 成员）仍须用户在 VS x64「转到定义」确认后编译验证（见 QA P0，非本 ADR 范围）。
- ℹ️ 配套修复：csproj 中英莱原生 DLL 原用 `<Link>` 导致「无法将链接添加到文件…在项目目录树内」编译错误，已改为 `<Target AfterBuild>` 把 `Libs\IntelligentLaser\*.dll` 与 `native\*.dll` 扁平拷贝到输出根（详见落地报告）。

## 涉及约束

- [[decisions/ADR-001-DisposePattern]] ✅（页类不重写 Dispose，仅 `StopTimer()` 停定时器）
- [[decisions/ADR-002-CS73-Constraint]] ✅
- [[decisions/ADR-038-EmguALGThreeLayer]] ✅（本阶段不动 EmguALG 单文件）
- [[project/SunnyUI-Legacy]] ✅（SunnyUI 紫主题）
- [[decisions/ADR-012-MonitorCamPage-AlgorithmInline]] ⚠️（本窗体作为单独个例采用 `UIPage + AddPage` 的 Tabpage，不推翻其项目级「弃 Tab」惯例）
- [[decisions/ADR-034-LineLaserThreeLayerRefactor]]（CameraSelector.Active 判定接口来源）
- [[guides/WinForms-Designer]] ✅（InitializeComponent 无流程控制）
- [[guides/WinForms-UI-Threading]] ✅（结果刷新用 UI 线程 Timer，无需 BeginInvoke）
- [[guides/Namespace-Compilation]] ✅（新增 `EmguAlgoPage`/`ILAlgoForm` 两个 UIPage 子页的 `.cs` + `.Designer.cs`，已登记 csproj Compile）

## 相关

- [[api/ILAlgorithmEditForm]]（本窗体接口与页切换说明）
- [[modules/EmguALG]]（模块 A 算法，PipelineConfig）
- [[modules/IntelligentLaserCam]]（模块 B 相机与接口）
- [[api/IntelligentLaserCam]]（IlJobParamInfo / IlInspectResult 接口）
- [[decisions/ADR-034-LineLaserThreeLayerRefactor]]（CameraSelector.Active 判定接口来源）
- [[guides/WinForms-UI-Threading]]（定时器刷新结果）
