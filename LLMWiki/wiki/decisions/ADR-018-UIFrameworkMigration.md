---
title: ADR-018 UI 框架从 SunnyUI 迁移至 AntdUI
date: 2026-07-20
tags: [决策, UI, 迁移, SunnyUI, AntdUI]
status: accepted
---

# ADR-018：UI 框架从 SunnyUI 迁移至 AntdUI

## 背景

AdaWeldSystem 项目 UI 层使用 SunnyUI 框架（GPL v3 许可）。因商业原因，GPL v3 许可对商业化产品有限制。AntdUI 采用 MIT 许可证，商业政策更宽松，适合产品级部署。

## 决策

将项目 UI 框架从 SunnyUI 迁移至 AntdUI。迁移分阶段进行：

1. **阶段 1**：基础控件替换（Button/Input/Label/CheckBox/ComboBox 等）
2. **阶段 2**：导航框架重构（UINavBar+UINavMenu+UITabControl → Menu+Tabs）
3. **阶段 3**：数据表格迁移（UIDataGridView + DataTable → Table + AntList\<T\>）
4. **阶段 4**：图表控件集成（UILineChart/UIDoughnutChart → `ScottPlot.FormsPlot` 4.1.74，**2026-08-12 由起初的 `AntdUI.Chart` 改选，2026-08-13 升级 5.x 后回退 4.1.74**（5.x 基于 SkiaSharp 对 .NET 4.8 设计器不友好））
5. **阶段 5**：主题与样式微调

## 备选方案

| 方案 | 优点 | 缺点 | 是否采用 |
|------|------|------|---------|
| 迁移至 AntdUI（MIT 许可） | 免费商用、Ant Design 设计语言、社区活跃 | 部分控件无直接替代（图表/工业控件） | **采用** |
| 购买 SunnyUI 商业许可 | 零迁移成本、已有 ~280 个控件实例 | 持续付费、GPL v3 争议风险 | 不采用 |
| 使用标准 WinForms 控件 | 零依赖、完全自由 | 视觉效果差、开发效率低 | 不采用 |

## 后果

### 正面

- MIT 许可消除商业化法律风险
- AntdUI 设计语言更现代化
- SVG 图标系统更灵活
- 亮暗主题切换更便捷

### 负面

- ~280 个控件实例需逐一迁移
- ~~UILineChart/UIDoughnutChart 无直接替代~~ → **起初确认 AntdUI 内置 Chart 控件（`AntdUI.Chart`）可直接替代；2026-08-12 用户在 MainPage 实装后改选 `ScottPlot.FormsPlot`（更轻量、高性能、实时动态数据可视化更优），图表承载统一改用 ScottPlot，全面替换 `AntdUI.Chart`；2026-08-13 升级 5.1.59 后回退 4.1.74**（5.x 基于 SkiaSharp 对 .NET 4.8 设计器不友好）。用法见 [[guides/Project-Tools]]。
- UILight/UILedBulb 等工业控件需用 AntdUI.Signal 替代（功能有差异）
- UIDataGridView 基于 DataTable，AntdUI Table 基于 AntList\<T\>，数据层需调整
- Designer.cs 文件需全部重新生成（AntdUI 控件命名空间不同）

## 关键约束

- 迁移后仍须遵守 [[decisions/ADR-001-DisposePattern]]（DisposeComponents 模式）
- 迁移后仍须遵守 [[guides/WinForms-Designer]]（Designer.cs 不手动修改）
- 迁移后仍须遵守 [[guides/WinForms-UI-Threading]]（Workflow 事件 InvokeRequired）
- 迁移后须更新 [[project/SunnyUI-Legacy]] 中的主题系统（AntdUI 用 Config.IsLight）

## 相关页面

- [[modules/UIDesign]] -- UI 界面模块
- [[guides/AntdUI-Reference]] -- 迁移对照指南（AntdUI 控件 API 差异总集）
- [[guides/AntdUI-Reference]] -- AntdUI 固定 UI 设计范式（事件/布局/表格统一入口；**Chart 已由 ScottPlot 取代**）
- [[guides/Project-Tools]] -- 图表承载统一用 ScottPlot.FormsPlot 4.1.74（2026-08-12 替换 AntdUI.Chart，2026-08-13 升级 5.x 后回退 4.1.74）
- [[project/SunnyUI-Legacy]] -- 全局 UI 风格统一为 Purple
- [[project/SunnyUI-Legacy]] -- UILight 属性规范
- [[guides/WinForms-Designer]] -- Designer.cs 不可修改

## 迁移完成状态（2026-07-28 确认）

**25/25 文件全部完成迁移**。全量 Grep 确认：
- `using Sunny.UI;` = 0 命中（所有 .cs 文件）
- `private Sunny.UI`/`new Sunny.UI` = 0 命中（所有 .Designer.cs 文件）
- `UIMessageBox` = 0 命中（代码中，仅注释残留）
- `System.Windows.Forms.DataGridView` = 0 命中（全部替换为 AntdUI.Table + AntList\<T\>）

迁移追踪表：[[guides/AntdUI-Reference]]
