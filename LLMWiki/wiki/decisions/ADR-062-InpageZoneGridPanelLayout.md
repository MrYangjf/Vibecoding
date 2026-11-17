---
title: ADR-062 页内分区容器范式（Tabs → GridPanel 同屏分区）
date: 2026-10-12
updated: 2026-10-12
tags: [ADR, UI, 布局, GridPanel, 页内分区, P4, 工艺设置]
status: accepted
---

# ADR-062：页内分区容器范式（Tabs → GridPanel 同屏分区）

> 页内分区**不再用嵌套 Tabs**，改用 `GridPanel` + `Panel` 的**同屏分区**形态（业主 2026-10-10/12 裁定）。
> 本 ADR **不废止** [[decisions/ADR-051-ILCamPageTabsConversion]] 的 Tabs 双写铁律 —— **外层导航 Tabs 仍然双写**，只是页内分区不再走 Tabs。

## 背景

P4 落地过程中发现：页内用嵌套 Tabs（`tabsQuickSetup` 4 区、`tabsLaserProcess` 3 区）有三个问题：

1. **同屏对比缺失**：分区之间是页签关系，一次只能看一个区；「功能启用 / Tracking指令 / TA指令 / LA指令」需要来回切页签才能纵览。
2. **BUG5 的直接动因**：业主要求「tabs 子设置不再向下叠加 tabs，改为 GridPanel 分区」。
3. **与 P4 剩余批次冲突**：U-3~U-7 的控件正要往这 7 个分区里填；先换容器再填控件 = **同一批容器搬两遍**。

## 决策

### 一、页内分区 = `GridPanel`（按 Span 分行）+ 各分区内容 `Panel`

外层 Tabs 的每个 `TabPage` 内改挂一个 `AntdUI.GridPanel`，`Span` 按分区数分行：

```csharp
// 快捷设置：4 区同屏
this.gridQuickZones.Controls.Add(this.panelQuickLa); // 逆序入流：后加的在上
this.gridQuickZones.Controls.Add(this.panelQuickTa);
this.gridQuickZones.Controls.Add(this.panelQuickTracking);
this.gridQuickZones.Controls.Add(this.panelProcessDebug);
this.gridQuickZones.Span = "fill;fill;fill;fill";
```

### 二、⛔ 不新建包裹 Panel，直接复用已有内容 Panel

各分区内容 Panel **已经是 ADR-060 §四 的卡片形态**（`Back` 白 / `BorderColor` 217 / `Shadow=5` / `ShadowOpacity=0.2` / 标题 Label / `AutoScroll`）。
⇒ 分区改造**只需换它们的父容器**，不新建一层包裹 Panel，也不动 Panel 内控件布局。

### 三、两列布局（2026-10-12 业主裁定补）

分区数 ≥3 时用 **2 列**，避免单列把每个区纵向压扁：

```csharp
this.gridQuickZones.Span = "fill fill;fill fill"; // 4 区 → 2 行 × 2 列
this.gridLaserZones.Span = "fill fill;fill fill"; // 3 区 → 声明 4 格，放 3 个控件
```

实测：单列 4 行时每区仅 **160px 高**；改两列后为 **666 × 326**，高度翻倍。

> ⛔ **奇数分区必须「声明 4 格、只挂 N 个控件」**（`"fill fill;fill fill"` 配 3 个控件），
> **不可写 `"fill fill;fill"`（3 格）** —— 实测**末格会横向拉伸补满整行**（1337 宽），
> LA 区内的两个卡片反而被压扁。改前务必上探针（§7.3）实测定案，官方文档只定义语法、未说明此行为。

### 四、一区多卡片时用内层 `GridPanel` 排列

### 四、一区多卡片时用内层 `GridPanel` 排列

`LA设置` 区含两个卡片（`panelWireAlign` + `panelLaserLa`）⇒ 该区位置放一个内层 `GridPanel`（`Span="fill;fill"`）两行排列，其余区直接挂单个 Panel。

### 五、空分区用「Panel + 标题 Label」占位

原空页签（`tabQuickTracking`）转为分区 Panel，附标题 Label 标明用途（U-4 待填控件区）。

## 关键约束

| 约束 | 说明 |
|---|---|
| ⛔ **GridPanel 逆序入流** | `Controls.Add` 顺序 = 视觉顺序**倒序**；最后加的显示在最上（实测确认） |
| ⛔ **奇数分区用「声明 4 格 + 挂 N 控件」** | `"fill fill;fill"`（3 格）会让末格**横向拉伸补满整行**；必须写 `"fill fill;fill fill"` 却只挂 3 个控件 |
| ⛔ **同父多 `Dock=Fill` 只在格位容器内合法** | `GridPanel` / `TableLayoutPanel` 靠 Span/格位分配区域，同父多 Fill 正常；**普通 `Panel` 里同父多 Fill 必然重叠**（判据库 §7.3.2） |
| ⛔ **ADR-051 双写仍适用于外层 Tabs** | `tabsProcess.Pages.Add(tabPage*)` 保持不变；只有页内分区不双写（因为不用 Tabs 了） |
| ⛔ **删容器必做引用对账** | 删 `TabPage` 后须 grep 确认 `.Designer.cs` 与 `.cs` 均无残留引用（残留 = CS0103）；字段声明与实例化须一一对应（漏实例化 = CS0649） |
| ⚠️ **`Span` 的布局行为以探针为准** | 官方 `GridPanel.md` 只定义语法（`;` 分行 / 空格分列 / `fill` 均分），**未说明末格拉伸等行为** ⇒ 一律实测（§7.3） |

## 后果

- **正面**：7 个分区同屏可见（纵览无需切页签）；两列布局下每区高度从 160 翻倍到 326，控件不再被压扁；U-x 控件填入位置确定；符合业主「不叠加 tabs」要求
- **负面**：奇数分区时右下格留空；跨分区操作路径变长（但同屏可见反而更易发现）
- **中性**：`.cs` 代码后置零改动（实测嵌套容器在 `.cs` 中零引用）

## 验证

- ** 实测法**（判据库 §7.3，加载真实 `AntdUI.dll`）：
 - **两列 4 区（快捷设置）**：`Bounds` 均为 **666 × 326**，排布 `y=3/335` × `x=3/675` —— 不重叠、全 Visible
 - **两列 3 区（激光工艺）**：第 3 区正确落左半格（666 宽，**未拉伸整行**）；内层 LA 区两卡片 **660 × 157**，未被压扁
 - **反向验证**：`"fill fill;fill"`（3 格）实测末格拉伸至 **1337 宽** ⇒ 据此排除该写法

- **回归**：仅 `ProcessControlPage.Designer.cs` 变化，`.cs` 零改动

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[project/ReviewOptimization-P1-StructureDesign]] §4.2 —— 板块归属与 U-x 需求来源
- [[decisions/ADR-060-P4UiLanding]] §四 —— 卡片 Panel 控件范式（本 ADR 复用其产物）
- [[decisions/ADR-051-ILCamPageTabsConversion]] —— Tabs 双写铁律（外层仍适用）
- [[lessons/StaticVerifierJudgements]] §7.3.2 —— 布局类判据（同父多 Fill 必重叠）
- [[api/ProcessControlPage]] —— 消费方页面
