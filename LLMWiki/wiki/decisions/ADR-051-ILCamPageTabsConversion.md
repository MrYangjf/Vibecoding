---
title: ADR-051 ILCamPage Tabs 化（单页承载 + 分页预留）
date: 2026-09-30
updated: 2026-10-30
tags: [决策, UI, ILCamPage, Tabs, 英莱相机, 线激光, Designer, ADR-048]
status: accepted
---

# ADR-051：ILCamPage Tabs 化（单页承载 + 分页预留）

## 背景

业主需求（2026-09-30）：「ILCamPage 也和 MonitorCamPage 一样，做成 tabs。只不过当前 ILCamPage 只有一页线激光采集设置。」

即：把英莱相机调试页按 [[decisions/ADR-048-MonitorCamTabsRecordPlayback]] 的同代范式改为 `AntdUI.Tabs` 承载；当前**只挂一页**「线激光采集设置」，为后续分页（回放 / 标定 / 算法等）预留结构位。

## 决策

1. **根容器 Tabs 化**：`ILCamPage` 根由 `uiTableLayoutPanel1` 直挂 `this.Controls` 改为
 `tabsIL`（`AntdUI.Tabs`，`Dock=Fill`）→ `tabPageLaserCapture`（`AntdUI.TabPage`，`Text="线激光采集设置"`）→ `uiTableLayoutPanel1`（**原四行布局与内部控件零改动**，仅换挂载父级）。
2. **双写铁律**（沿 [[decisions/ADR-048-MonitorCamTabsRecordPlayback]] / SystemControlPage 同代约定）：`this.tabsIL.Controls.Add(this.tabPageLaserCapture)` **与** `this.tabsIL.Pages.Add(this.tabPageLaserCapture)` 两者都要写 —— 只写前者页面不显示。
3. **命名与文案**：`tabsIL` / `tabPageLaserCapture`（照 `tabsMonitor` / `tabPageCamSetting` 同代风格）；`tabsIL.Text = "英莱相机设置"`（与 `FormMain` NavPage 名一致）、`tabPageLaserCapture.Text = "线激光采集设置"`（业主口径）。
4. **只改设计器、代码后置零改动**：`ILCamPage.cs` 对控件仅「只使用」（零 `new` 控件、零 `Controls.Add`、零 `uiTableLayoutPanel1` 引用），故 `.cs` **一行未动**（md5 与改动前一致）。
5. **单页承载不引入页签副作用**：单页常驻可见，`RefreshDisplay()` 的「手动/空闲才绘 Mat」判据不受页签可见性影响，无需新增 `SelectingChanged` 分支。

## 备选方案

| 方案 | 结论 |
|---|---|
| 不包 Tabs，保持根容器直挂 | 放弃：业主明确要求与 ADR-048 同构，为后续分页预留 |
| 包 Tabs 但沿用 `uiTableLayoutPanel*` 式命名 | 放弃：须与同代范式一致，避免「名叫 TLP 的 Tabs」错位 |
| 顺带把右侧栏改 GridPanel / 直接拆多页 | 放弃：超出本次请求范围；业主正在 VS 内自行打磨风格（见「当日实况」） |

## 后果

### 正面

- 与监控相机页同构：后续加页只需新增 `TabPage` + 双写，无需再动根容器。
- 原 `uiTableLayoutPanel1` 的布局与内部控件**零改动**，风险面仅限「父级换挂」。
- `.cs` 未改动 ⇒ 无业务逻辑回归面。

### 负面

- 多一层容器，设计器内多一组 `Suspend/Resume` 配对；改根布局须同时照顾 Tabs 层。
- `tabsIL.Text` 与 NavPage 名重复（同为「英莱相机设置」），单页场景下该标题不显示，属预留位。

## 当日实况（2026-09-30 并发协作记录）

- AI 落地 Tabs 包裹后，**业主同时在 Visual Studio 内继续打磨该页**并两次保存（09:46 / 09:49）：顶栏行高 30→45、各控件高 24/30→39/45、`divider1` 的 `Dock` 由 `Top` 改 `Bottom`、内部行高 55/200→64/191、`panel1`/`imageBox`/`panelResult` 高度重算；并为 Tabs 追加 `Cursor=Hand`、`Type = AntdUI.TabType.Card`、`Style = styleCard1`（`AntdUI.Tabs.StyleCard` 局部变量，声明由 VS 生成于 `InitializeComponent` 首部）。AI 的 Tabs 结构在 VS 重新序列化后**完整保留**。
- ⚠️ **遗留待裁定**：`uiTableLayoutPanel1` 的 `RowCount = 4` 而 `RowStyles` 有 **5** 条（末条 `Absolute 20F` 被忽略）——属业主 VS 编辑中间态，AI **未改动**，待业主确认「补 `RowCount=5`」还是「删多余样式」。
- ⚠️ **协作风险门禁**：业主在 VS 中打开该文件时，AI 的落盘会被 VS 保存覆盖（反向亦然）。本次靠「VS 检测到外部改动并重新加载」化解；后续同页改动建议先让 VS 关闭或重新加载后再落盘。

## 演进记录

- **2026-11-13 导航归并**：`ILCamPage` 由独立顶部「相机设置」页迁入「系统参数设置」NavPage 第 3 项；NavPage 名与 `tabsIL.Text` 同步改为「线激光设置」，内页签「线激光采集设置」不变。Tabs 结构、`Controls.Add`+`Pages.Add` 双写铁律、单页标题不显示的结论继续有效。

## 相关页面

- [[decisions/ADR-048-MonitorCamTabsRecordPlayback]] —— 同代 Tabs 范式来源（双写铁律 + 多页组织）
- [[modules/UIDesign]] —— `ILCamPage` 结构小节
- [[api/IntelligentLaserCam]] —— 英莱相机模块要点（UI 层事实汇总）
- [[guides/WinForms-Designer]] —— 设计器字节安全编辑与归属门禁（§6）
- [[lessons/UiLayoutChangeSyncPitfalls]] —— 布局改版同步与所有权门禁
- [[decisions/ADR-036-UIControlPlacementRule]] —— TabPage/ControlPage 的对话框归位规则
