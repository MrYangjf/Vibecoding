---
title: AntdUI 完整开发参考
date: 2026-08-18
tags: [指导, UI, AntdUI, 参考手册, 汇总]
---

# AntdUI 完整开发参考
> **章节导航**（本页 1069 行，超长页请先按章节定位再读）：
>
> - [1. 设计范式总览](#1-设计范式总览)
> - [2. 布局系统](#2-布局系统)
> - [3. 导航与菜单](#3-导航与菜单)
> - [4. 表格控件](#4-表格控件)
> - [5. 对话框与消息](#5-对话框与消息)
> - [6. 命名空间与类型冲突（CS0104）](#6-命名空间与类型冲突cs0104)
> - [7. 迁移 API 差异](#7-迁移-api-差异)
> - [8. 迁移状态追踪（简要版）](#8-迁移状态追踪简要版)
> - [来源](#来源)


> **位置说明（2026-09-01）**：本页自 `wiki/lessons/` 迁入 `wiki/guides/`。
> 分类判据：**`guides/` = 「怎么做」的操作型指导与参考手册**；`lessons/` = 「踩过什么坑」的教训门禁；`standards/` = 「必须遵守」的强制规范。
> 页面内的历史 lessons 链接已同步更新为 guides 路径。


> 本文档是 AntdUI 开发的综合参考手册，聚合了所有专项 lessons 的技术要点、代码示例与踩坑记录，作为一站式查阅入口。各主题的原始权威页仍以单独 lesson 形式存在。

---

## 1. 设计范式总览

> 本页是 AntdUI 固定 UI 设计范式的统一枢纽入口，聚合所有范式要点并链接到对应专项内容。

### 1.1 范式速查（按主题）

| 主题 | 关键铁律 |
|------|----------|
| 控件 API 差异（Select/Column.Width/InputNumber.Value 为 decimal/CellClick 自定义委托/Step→Increment/Pagination 4 参/Table 无 ReadOnly） | Designer.cs 内禁 `DataSource`+`AntList`，数据一律代码后置 `Binding()` |
| Table 列与数据绑定（Designer 序列化坑） | Columns/DataSource 禁入 Designer；三段式 `InitTableColumns()`→`new AntList<T>()`→`table.Binding(list)` |
| GridPanel.Span 语法 | 值仅 `fill`/%/整数/浮点；`px`/`auto` 非法；Controls.Add **逆序**入格 |
| Message / Modal 的 owner 类型 | `Message` owner=Target（UserControl 须 `Form.ActiveForm`/`(Target)null`/`this.FindForm()`）；`Modal` owner=Control，裸 `null` 不二义。**坑**：`Modal.Config` 第三参数（content）若是未定义标识符会级联误报"Form→Target"，见 [[lessons/AntdUI-Modal-Config-Overload-Cascade]] |
| Menu + Tabs 导航 | `menu.Items.Add(new MenuItem{Text,Tag})`；`SelectIndex(idx,true)` 触发 `SelectChanged`；`_syncing` 重入守卫；`AddTabSelect(TabPage)` 非 UserControl |
| 命名空间遮蔽（CS0104） | `FolderBrowserDialog` 等须全限定 `AntdUI.FolderBrowserDialog` |
| 数据表格选型 | 一律 `AntdUI.Table` + `AntList<T>`，禁用 `DataGridView` |
| 设计器 resx 孤儿类型引用（System.Void 级联） | 基类迁移后须清理 resx `$this.Type`，并 XML 校验 well-formed |
| ToolStrip → FlowPanel/Label/Button | 头部工具条改用 `AntdUI.FlowPanel` + `Label` + `Button` |
| 对话窗承载方式（Modal 承载 UserControl） | 对话窗基类改 `UserControl`，`AntdUI.Modal.open(Config(...))` 弹出；关闭用 `FindForm().DialogResult` |
| Tabs 添加 TabPage | 必须同时使用 `Controls.Add` + `Pages.Add` |
| **TooltipComponent 文字提示（2026-08-31）** | TooltipDemo 范式：单实例 `new AntdUI.TooltipComponent{ Font=..., ArrowAlign=TAlign.Top }` 可对**多控件**逐一 `SetTip(ctrl, text)`；方位 12 值=TAlign（Top/Bottom/Left/Right/TL/TR/BL/BR/LT/LB/RT/RB）；组件为 IDisposable，页面释放时须 `Dispose()`（入 `DisposeComponents()`） |
| **Button/IControl 原生徽标 Badge（2026-08-31）** | AntdUI `IControl`（含 Button/ButtonShadow 等）**内建徽标属性**，无需挂子控件：`Badge`（内容，**空串=纯色圆点**）、`BadgeSvg`（SVG 徽标，颜色随 `BadgeBack ?? 红`）、`BadgeAlign`（默认 TR）、`BadgeMode`（true=镂空环）、`BadgeBack`/`BadgeFore`/`BadgeBorderColor`/`BadgeOffsetX/Y`；渲染逻辑 `Helper.GDI.PaintBadge`（`BadgeBack ?? Colour.Error` 兜底）；连接态红/绿直接改 `BadgeBack`（O(1) 属性赋值，免重建） |
| **AntdUI 内置 SVG 图标名仅基础集** | `SvgDb.cs` 仅 ~24 个基础图标（ArrowLeftOutlined/CheckOutlined 等），**无** VideoCamera/Robot/Api 等业务图标；业务图标须自备 SVG 字符串赋 `IconSvg`/`BadgeSvg` |
| **ButtonShadow 阴影按钮范式（2026-08-31）** | 形态对齐官方 Demo `buttonShadow1`：50×50、`BorderWidth=1F`、`IconRatio=1.2F`、`IconSvg`=SVG 字符串（demo 经 resx 资源）、`ShadowColor=黑`、`Badge=""`+`BadgeMode=true`；仅显示图标无文本时信息走 TooltipComponent |

### 1.2 Designer.cs 铁律（贯穿所有页面）

- **禁止**在 `.cs`（非 Designer.cs）重写 `Dispose(bool)`——用 `DisposeComponents()`。
- `InitializeComponent()` 内**禁**流程控制（`for`/`while`/`if`/`switch`/`foreach`），循环须展开为逐条语句。
- 自定义事件**直接订阅** `control.Event += handler`，**禁** `new EventHandler()` 包装 AntdUI 自定义委托（handler 签名 `EventArgs`→`AntdUI.BoolEventArgs`/`IntEventArgs` 等）。
- 控件须先 `new` 实例化再加入 `Controls.Add`。

### 1.3 通用约定

- 所有 Workflow 事件处理必须 `InvokeRequired`/`BeginInvoke` 守卫。
- 主题：`AntdUI.Config.IsLight`（原 SunnyUI `UIStyles.SetStyle(Purple)` 已废弃）。
- 状态灯：`AntdUI.Signal`（原 `UILight` 已取代）。
- C# 7.3 语法约束（禁 `init`/`record`/可空引用/`using` 声明/冒号格式化插值等）。

### 1.4 FlowPanel 表单布局范式（TableLayoutPanel 替代，可选）

> **注意（ADR-031）**：本范式由"强制迁移"降级为**可选范式**。`FlowPanel`/`GridPanel` 会强制排序子控件，不再强制使用。表单布局可选用 `FlowPanel`、`Panel` 绝对定位、`Dock`/`Anchor` 或 WinForms 原生容器等任一方式按需实现。以下为**若选用 FlowPanel 时的**规范。

**适用场景**：参数配置页中的 label+input 表单区域，替代 WinForms 原生 `TableLayoutPanel`，实现自动流式排列。

**核心配置**：
- `Align = TAlignFlow.Left` — 左对齐流式排列（`TAlignFlow` 枚举：Left/LeftCenter/Center/RightCenter/Right）
- `Gap = 8` — 控件间距（像素），控制同排控件之间的水平间距
- `Padding = new Padding(10, 4, 10, 4)` — 内边距
- `Dock = DockStyle.Fill` — 充满父容器
- `AutoScroll = true`（可选）— 内容超出时显示滚动条

**控件尺寸规范**：

| 控件类型 | 尺寸 | 说明 |
|----------|------|------|
| Label（表单项标题） | `Size=(140, 34)` 或 `(150, 34)` | `TextAlign=MiddleLeft`，删除 `Dock=Fill` 和 `MinimumSize` |
| Input（文本输入） | `Size=(160, 32)` | 删除 `Dock=Left`、`Margin`、`MinimumSize` |
| InputNumber（数值输入） | `Size=(160, 32)` | 同上 |
| Select（下拉选择） | `Size=(160, 32)` | 同上 |
| Checkbox | 保持原尺寸 | 删除 `Dock`、`MinimumSize` |
| Button | 保持原尺寸 | 删除 `Dock`、`MinimumSize` |

**Controls.Add 顺序**：按「label → input」成对依次添加，FlowPanel 自动从左到右排列，排满自动换行。多列表单按行优先排列（先第一行所有列，再第二行所有列...）。

**对比 GridPanel**：GridPanel 用于**大区域比例分割**（左右列、上下行），FlowPanel 用于**表单级细粒度流式排列**（label+input 成对）。项目标准结构为 `GridPanel(外层分区) → Panel(卡片) → GridPanel(标题+内容) → FlowPanel(表单)`。

**迁移 Checklist**：
- [ ] 删除 `ColumnCount`/`ColumnStyles`/`RowCount`/`RowStyles`
- [ ] 删除所有 `SetColumnSpan` 调用
- [ ] 删除子控件 `Dock`/`Margin`/`MinimumSize`
- [ ] Label 设置 `Size` + `TextAlign=MiddleLeft`
- [ ] Input/Select 设置统一 `Size`
- [ ] `Controls.Add(control, col, row)` → `Controls.Add(control)`（按顺序）
- [ ] 底部字段声明 `TableLayoutPanel` → `AntdUI.FlowPanel`
- [ ] SuspendLayout/ResumeLayout 同步替换

---

## 2. 布局系统

### 2.1 ADR-031：布局容器自由化（解除 GridPanel/FlowPanel 强制使用）

#### 背景

此前的 UI 设计与范式形成了一条**硬约束**：所有 UI 容器"必须使用 `AntdUI.GridPanel`"（大区域分割）与 `AntdUI.FlowPanel`（表单流式排列）。这两类容器存在**强制排序**行为，给布局带来不便：

- `GridPanel` 的子控件按 `Controls.Add` 的**逆序**入格，Designer 中必须把 Add 顺序写成期望格子顺序的倒序，易错且反直觉。
- `FlowPanel` 按 `Controls.Add` 顺序自动从左到右流式排列并自动换行，无法精确控制每个控件的绝对位置。

用户（2026-08-12）明确要求：**不再强行使用 GridPanel 和 FlowPanel，因为它们会强行排序**。

#### 决策

1. **解除 `GridPanel`/`FlowPanel` 的强制使用约束**，布局容器改为**按需自由选择**。开发时可根据具体布局需求选用 `GridPanel`、`FlowPanel`、`Panel` 绝对定位、`Dock`/`Anchor` 或 WinForms 原生布局容器等任一方式。
2. **保留 AntdUI 整体风格**：项目 UI 主体仍为 AntdUI 风格（框架约束不因本 ADR 改变）。
3. **控件回退规则**：AntdUI 缺失的控件，允许使用 **WinForms 原生控件**作为回退。
4. **SunnyUI 控件一律禁止**使用（GPL 许可约束）。
5. **不重写已有页面**：已用 `GridPanel`/`FlowPanel` 实现的页面功能正常，**不强制重写**。
6. **若仍使用 `GridPanel`/`FlowPanel`**，必须遵守其各自的布局规则（`GridPanel` 逆序入格、`FlowPanel` Align=Left+Gap+顺序 Add）——这些规则是「使用该容器时的技术知识」，而非「强制使用该容器的理由」。

#### 后果

**正面**：布局方式回归自由，消除 GridPanel 逆序入格、FlowPanel 自动换行的强排序心智负担；AntdUI 无所需控件时可用原生控件兜底。

**负面**：布局风格可能在页面间不一致，需代码审查时人工把握统一性；新页面若用其他容器，GridPanel 相关规则不再自动适用。

---

### 2.2 GridPanel.Span 完整语法（源码确证）

> 本节为**若选用 GridPanel 时**必须遵守的语法与入格规则（技术知识）。

#### Span 语法（权威）

```
Span = "行1定义;行2定义;...[-全局行高表]"
行定义 = [高度:]列宽1 列宽2 ...
```

#### 结构解析（`-` 分隔符核心意义）

`-` 是**分隔符**，将 Span 分为两段：

| 段 | 位置 | 含义 | 分隔方式 |
|----|------|------|---------|
| 前半段 | `-` 之前 | 每行的**列定义**（由 `;` 分隔，每段代表一行，段内空格分隔代表该行各列） | `;` 分行 |
| 后半段 | `-` 之后 | 每行的**高度定义**（由空格分隔，按行序对应，第 N 个值 = 第 N 行的高度） | 空格分高 |

**关键理解**：`-` 之前每个 `;` 段内的**值数量**决定了该行有多少列。例如：
- `fill` → 该行 1 列，列宽 `fill`
- `fill fill` → 该行 2 列，列宽均为 `fill`
- `10% 20% 10% 60%` → 该行 4 列，列宽分别为 10%、20%、10%、60%

**实例**：`"fill;fill;fill;fill;-10% 20% 10% 60%"`
- 前半段：4 个 `;` 段，每段 `fill` → **4 行 × 1 列**
- 后半段（`-` 之后）：4 个值 → **行高依次为 10%、20%、10%、60%**

#### 规则详解

1. **`;` 分行**：每组代表一行，行内列宽以**空格**分隔。
2. **行高来源优先级**：行内 `高度:` 前缀（**`:` 合法**）＞ `-` 之后的全局行高表（空格分隔，按行序对应）＞ 默认 `fill`。`-` 只按**第一个**出现位置切分一次。
3. **合法值仅 4 种**（`ParseDimension`）：
   - `fill`：均分剩余空间（大小写不敏感）
   - `N%`：先扣除固定值后，占剩余空间的百分比
   - 整数：固定尺寸，**×DPI 缩放**（`100` 在 125% DPI 下=125px）
   - 浮点数：直接使用（不乘 DPI）
4. **`_N` 后缀 = 空占位**（合法）：该格保留尺寸但不放控件（`IsEmpty`），可用于留边距。
5. **任何其它 token 都非法**：`100px`、`auto`、`60:100%_2` 中的 `_2` 等——`int/float.TryParse` 失败 → 尺寸 0 → 非空占位强制 1px → **白板/控件不可见**。解析异常时整体返回空矩形数组，全部子控件不布局。

官方 Demo 示例：`"50% 50%;20% 80%;150 200;-20% 30% 50%"`（3 行，`-` 后为 3 个全局行高）；`"64:80 100%;40:80 100%;40:100%;100%:100%"`（4 行全部内联行高）。

#### 子控件入格顺序（最大暗坑）

`SyncMap` 遍历 `Controls` 时倒插 + 按序号升序排——**单元格按 `Controls.Add` 的逆序分配**：

- `Controls.Add(A); Add(B); Add(C)` → 格子顺序（行优先）= **C, B, A**。
- 官方 Demo 在每次 `Add` 后调 `control.BringToFront()` 把顺序翻转回自然序——Designer.cs 中没有这一步，**Add 顺序必须写成期望格子顺序的倒序**。
- 或用扩展属性 `gridPanel.SetIndex(ctrl, n)` 显式指定序号（n 越小越靠前的格子）。
- 隐藏（`Visible=false`）的控件不参与分格；控件多于格子时多余控件被移出可视区。

#### 其它要点

- `Gap`（int）：格内四周间距，×DPI；与 `control.Margin` 叠加。
- 子控件的 `Dock`/`Anchor`/`Location` 对 GridPanel 无效（LayoutEngine 直接设 `Bounds`），子控件自动充满所在格。
- 设计期（无子控件时）GridPanel 会绘制 `列:行` 网格预览。

---

### 2.3 Panel 样式标准

所有 GridPanel 单元格内的控件建议使用 `AntdUI.Panel` 包裹，统一视觉风格：

```csharp
// 标准面板样式
panel.Back = Color.White;                                              // 白色背景
panel.BorderColor = Color.FromArgb(217, 217, 217);                     // 灰色边框（Ant Design 标准灰）
panel.Shadow = 5;                                                      // 阴影半径 5px
panel.ShadowColor = Color.Black;                                       // 黑色阴影
panel.ShadowOpacity = 0.2F;                                            // 阴影透明度 20%
panel.ShadowOpacityAnimation = true;                                   // 阴影动画（悬停增强）
panel.Padding = new Padding(3);                                        // 内边距 3px
panel.Dock = DockStyle.Fill;                                           // 充满 GridPanel 单元格
```

#### 实施要点

1. **必须实例化**：Designer.cs 中声明的 Panel 必须在 `InitializeComponent()` 内 `new AntdUI.Panel()`，否则运行时 `NullReferenceException`。
2. **Chart 包裹**：所有 Chart 控件必须先放入 Panel，再由 Panel 放入 GridPanel，实现圆润边角+阴影效果。
3. **Dock 优先级**：Panel 内嵌控件使用 `Dock=Fill` 充满 Panel，不使用 `Anchor`（避免布局计算冲突）。
4. **逆序 Add**：GridPanel 的 `Controls.Add()` 按逆序分配格子，Panel 亦遵循此规则。

---

### 2.4 Splitter → GridPanel 固定区域（历史改造记录）

> 本小节是 MainPage 的历史改造记录，描述当时"Splitter→GridPanel"的决策。布局容器现已自由化，`GridPanel` 不再被强制要求。

#### 背景

MainPage（首页/仪表盘）顶部原用 `AntdUI.Splitter`（继承 WinForms `SplitContainer`），左 `Panel1` + 右 `Panel2`，`SplitterDistance=500` 可拖动分隔。用户要求改为「固定区域」——即不可拖动的固定布局。

> 注：AntdUI.Splitter 继承 WinForms `SplitContainer`，`Panel1`/`Panel2`/`SplitterDistance`/`ISupportInitialize` 全部合法——**不要把 Splitter 的宿主 API 当编译错误乱删**。

#### 实现要点（Designer.cs）

```csharp
this.uiGridPanel1 = new AntdUI.GridPanel();
// 单行两列固定区域：左 40% panel1 | 右 60% uiGridPanel2，不可拖动
this.uiGridPanel1.Controls.Add(this.uiGridPanel2);    // 先加 → 逆序 → 落入右格(60%)
this.uiGridPanel1.Controls.Add(this.panel1);          // 后加 → 逆序 → 落入左格(40%)
this.uiGridPanel1.Dock = DockStyle.Fill;
this.uiGridPanel1.Span = "40% 60%";
this.uiGridPanel1.TabIndex = 1;
// 移除 Splitter 宿主代码：Panel1/Panel2/SplitterDistance/SplitterWidth/((ISupportInitialize)).BeginInit/EndInit
```

**关键**：
1. **逆序入格**：期望单元格顺序 `[panel1(左), uiGridPanel2(右)]`，`Controls.Add` 必须写成**倒序** `Add(uiGridPanel2)` → `Add(panel1)`。
2. **Span 合法值**：`"40% 60%"`（`%` 合法）；**禁用 `px`/`auto`**（解析为 0 → 1px 白板）。
3. **移除 SplitContainer 专属代码**：`Panel1/Panel2` 不再存在；`((ISupportInitialize)(...)).BeginInit/EndInit` 对 `GridPanel` 不适用。

#### 嵌套 GridPanel 要点

1. **`Span` 多行必须 `;` 分行，行高用 `高度:` 前缀**（或 `-` 全局行高表）。写成 `"fill;180"` 是错的——`180` 无 `:` 前缀会被当成**列宽**而非行高。正确 `"68%:fill;32%:fill"`（或 `"fill;180:fill"`）。
2. **嵌套 GridPanel 的 `Dock`/`Location`/`Size` 被外层忽略**（LayoutEngine 直接设 Bounds），属正常。
3. **逆序入格规则对每一层 GridPanel 各自独立**生效：外层 2 子控件逆序、内层 2 子控件逆序，互不影响。

---

## 3. 导航与菜单

### 3.1 Menu + Tabs 导航模式

#### Menu.Mode（inline 模式核心）

- `Menu.Mode` 属性类型 `TMenuMode`，**默认 `Inline`**（侧边垂直菜单）；枚举成员：`Inline`、`InlineNoText`、`Horizontal`、`Horizontal_Arrow`、`Vertical`。
- 侧边导航用 `TMenuMode.Inline`（垂直侧栏），顶部横条用 `TMenuMode.Horizontal`。

#### Menu 菜单项

- 用 `menu.Items.Add(...)`，不是 `menu.Add(...)`（`Items` 是 Menu 的菜单项集合）。
- `MenuItem` 用对象初始化器 `new AntdUI.MenuItem { Text = "...", Tag = "..." }`，**不要用字符串构造 `new MenuItem("文本")`**。

#### Menu 选中事件

- 事件名是 **`SelectChanged`**（不是 `SelectedChanged`）。
- 回调参数 `MenuSelectEventArgs e`，选中项通过 **`e.Value.Tag`** 取关联键。**不要用 `menu.SelectedTag`**（Menu 无此属性）。

#### Tabs 内容页

- `AntdUI.Tabs.AddTabSelect` 接收 **`AntdUI.TabPage`**（不是直接传 UserControl）。
- 标准模式：

```csharp
AntdUI.TabPage tabPage = new AntdUI.TabPage { Text = name, Tag = key };
control.Dock = DockStyle.Fill;
tabPage.Controls.Add(control);   // control 为 UserControl 子页
tabs.AddTabSelect(tabPage);
```

#### Tabs 切换事件

- 事件名是 **`SelectedIndexChanged`**（不是 `SelectedChanged`）。

#### 双向联动（Menu ↔ Tabs）

- Menu 选中 → `tabs.SelectedIndex = 映射索引`（或 `tabs.SelectedTab = 目标TabPage`）。
- Tabs 切换 → 反写菜单：**`Menu` 没有 `SelectedIndex` 属性**，单层/扁平菜单用 `menu.SelectIndex(idx, true)`；多层级树菜单用 `menu.SelectIndex(root, sub, true)`。
- **⚠ 重要**：`SelectIndex` 会**同步触发 `SelectChanged`**。因此 `Menu→Tab` 与 `Tab→Menu` 两个方向联动时，**必须加 `bool _syncing` 重入守卫**，否则 `SelectIndex→SelectChanged→SelectByTag→SelectIndex` 无限重入 → `StackOverflowException`。

#### 重入守卫范式（必需）

```csharp
private bool _syncing;                       // 重入守卫（必需）
private void SelectByTag(object tag)
{
    if (tag == null || _syncing) return;
    int idx = Convert.ToInt32(tag);
    _syncing = true;
    try
    {
        uiTabControl1.SelectedIndex = idx;   // Menu → Tabs
        uiNavBar1.SelectIndex(idx, true);
        uiNavMenu1.SelectIndex(idx, true);
    }
    finally { _syncing = false; }
}
private void SyncMenus(int idx)              // Tabs → Menu 回写
{
    if (_syncing) return;                    // SelectIndex 会触发 SelectChanged，守卫阻断回环
    _syncing = true;
    try
    {
        uiNavBar1.SelectIndex(idx, true);
        uiNavMenu1.SelectIndex(idx, true);
    }
    finally { _syncing = false; }
}
```

#### 菜单项显隐 / 权限控制

- `menu.Items[index].Visible` 可用；重置选中用 `menu.SelectIndex(0, true)`（`Menu` 无 `SelectedIndex` 属性）。

#### 易错点速查

| 错误用法 | 正确写法 |
| --- | --- |
| `menu.Add(new MenuItem("x"))` | `menu.Items.Add(new MenuItem { Text = "x", Tag = "k" })` |
| `menu.SelectedChanged` 事件 | `menu.SelectChanged` |
| `menu.SelectedTag` | `e.Value.Tag`（MenuSelectEventArgs） |
| `tabs.AddTabSelect(userControl)` | `tabs.AddTabSelect(new TabPage { Text, Tag }.Controls.Add(userControl))` |
| `tabs.SelectedChanged` 事件 | `tabs.SelectedIndexChanged` |
| `menu.SelectedIndex = idx`（Menu 无此属性，CS1061） | `menu.SelectIndex(idx, true)`（扁平菜单选 root）；多层级 `menu.SelectIndex(root, sub, true)` |

---

### 3.2 Segmented 导航模式

> 当主窗口导航层级较浅（扁平结构，无嵌套子菜单），可用 `AntdUI.Segmented` 替代 `AntdUI.Menu` 实现紧凑顶部导航。

#### 适用场景

- 主窗口顶部导航（4~6 个一级页面，无子菜单）
- 需要紧凑的顶部导航条（比 Menu 占用更少的高度空间）
- 导航项为扁平的图标+文本组合

#### 正确写法

```csharp
// 1. Designer.cs 声明 Segmented 控件（与 Tabs 并列，Dock=Top）
this.segmentedMain = new AntdUI.Segmented();
this.segmentedMain.BackActive = Color.FromArgb(40, 22, 119, 255); // 半透明选中色
this.segmentedMain.Dock = DockStyle.Top;
this.segmentedMain.Font = new Font("宋体", 12F);
this.segmentedMain.Size = new Size(1252, 70);

// 2. 初始化 Segmented 项（图标+文本）
segmentedMain.Items.Clear();
segmentedMain.Items.Add(new AntdUI.SegmentedItem { Text = "主页面", IconSvg = "HomeOutlined" });
segmentedMain.Items.Add(new AntdUI.SegmentedItem { Text = "参数界面", IconSvg = "SettingOutlined" });
segmentedMain.Items.Add(new AntdUI.SegmentedItem { Text = "图形界面", IconSvg = "PictureOutlined" });
segmentedMain.Items.Add(new AntdUI.SegmentedItem { Text = "生产界面", IconSvg = "BarChartOutlined" });
```

#### Segmented ↔ Tabs 双向联动（重入守卫）

```csharp
bool syncing = false;

// Segmented 选中 → 切换 Tab
segmentedMain.SelectIndexChanged += (s, e) =>
{
    if (syncing) return;
    syncing = true;
    try { tabsMain.SelectedIndex = segmentedMain.SelectIndex; }
    finally { syncing = false; }
};

// Tab 切换 → 反写 Segmented 选中
tabsMain.SelectedIndexChanged += (s, e) =>
{
    if (syncing) return;
    int idx = tabsMain.SelectedIndex;
    if (idx >= 0 && idx < segmentedMain.Items.Count)
    {
        syncing = true;
        try { segmentedMain.SelectIndex = idx; }
        finally { syncing = false; }
    }
};
```

> **关键**：`Segmented.SelectIndex` 赋值会同步触发 `SelectIndexChanged`，因此必须 `bool syncing` 守卫防止回环 → `StackOverflowException`。

#### 权限控制（SegmentedItem 显隐）

**SegmentedItem 不支持 `Visible` 属性**（它是数据类，非 Control），需用 `Items.Remove/Add` 实现：

```csharp
// 保存隐藏项的引用
AntdUI.SegmentedItem _hiddenItem1, _hiddenItem2, _hiddenItem3;
_hiddenItem1 = segmentedMain.Items[1] as AntdUI.SegmentedItem;

// 隐藏
void HideTreeNode()
{
    segmentedMain.SelectIndex = 0;       // 先切回首页
    segmentedMain.Items.Remove(_hiddenItem3);
    segmentedMain.Items.Remove(_hiddenItem2);
    segmentedMain.Items.Remove(_hiddenItem1);
    HidePage = true;
}

// 恢复
void ShowTreeNode()
{
    segmentedMain.Items.Add(_hiddenItem1); // 按原始顺序重新 Add
    segmentedMain.Items.Add(_hiddenItem2);
    segmentedMain.Items.Add(_hiddenItem3);
    HidePage = false;
}
```

> **注意**：`Items.Add` 恢复的顺序必须与原始 `Items` 中的顺序一致，否则索引会错乱。

---

### 3.3 Tabs 添加 TabPage 必须 Controls.Add + Pages.Add

#### 背景

AntdUI 的 `Tabs` 控件与 WinForms 原生 `TabControl` 不同，添加 TabPage 需要**两行**代码。只写 `Controls.Add` 缺少 `Pages.Add`，会导致 TabPage 在视觉树中存在但未注册到 AntdUI Tabs 的 Pages 集合，页面无法正常显示内容。

#### 正确写法

```csharp
// 第1行：添加到控件树（Controls 集合）
this.tabsSettings.Controls.Add(this.tabGeneral);
// 第2行：注册到标签页集合（Pages 集合）
this.tabsSettings.Pages.Add(this.tabGeneral);
```

#### 原因

AntdUI Tabs 的 `Pages` 集合是独立的标签页管理集合，与 WinForms 的 `Controls` 集合分离。`Controls.Add` 仅将 TabPage 加入控件树（视觉容器），而 `Pages.Add` 才是真正注册为 Tabs 的标签页（驱动 Tab 标签头的显示和切换）。

---

## 4. 表格控件

### 4.1 Table Columns 与 DataSource 均不得进 Designer.cs

#### 高频坑：`Column(key, title)` 参数顺序不能写反

**症状**：Table 表头正常、行数正常（分页/Total 也对），但**每个单元格全空**；表头显示的是英文属性名。

**根因**：`Column(string key, string title)` — 第 1 参 = 行模型的属性名（绑定名称），第 2 参 = 表头文字（显示文字）。Table 渲染时用 `Key` 去行对象上反射取属性值，**取不到就渲染空白**，不会报错、不会抛异常。

```csharp
// ✘ 错误（中文写在前面，key 找不到 SeamWidth 属性 → 全空 + 表头显示 "SeamWidth"）
new AntdUI.Column("焊缝宽度", "SeamWidth") { Width = "150" }
// ✔ 正确
new AntdUI.Column("SeamWidth", "焊缝宽度") { Width = "150" }
```

**自检口诀**：第 1 个参数必须能在行模型 `class XxxRow` 里找到同名 `public` 属性（大小写敏感，`"No."` ≠ `No`）；第 2 个参数才是给人看的中文。

#### 两次设计器报错（同一根因族）

| 日期 | Designer.cs 中的违规写法 | 设计器报错 |
|------|--------------------------|-----------|
| 2026-07-29 | `xxx.Columns = new AntdUI.ColumnCollection { ... }` | 「设计器无法分析方法 InitializeComponent」/ System.Void 级联 |
| 2026-07-30 | `xxx.DataSource = new AntdUI.AntList<T>()`（含局部变量形式） | **「未能找到类型 "AntdUI.AntList`1"」** |

#### 根因（AntdUI 源码确证）

1. **`Table.DataSource` 带 `[Browsable(false)]`**——官方从一开始就不打算让设计器序列化该属性。CodeDom 反序列化 `AntdUI.AntList<T>` 泛型实例化语句时无法解析泛型类型。
2. **`Columns`（`ColumnCollection`）是集合属性**，设计器只认 `Add/AddRange` 增量模式，无法回合 `= new CollectionType { ... }` 整体赋值。
3. 官方 Demo 铁证：**Designer.cs 里 Table 只有外观属性**（Dock/Gap/Radius/EmptyHeader/AutoSizeColumnsMode）与事件订阅；`Columns` 赋值与数据加载全部在构造函数代码后置。

#### 固定方法范式（唯一正确写法）

**Designer.cs（`InitializeComponent` 内）——只允许出现：**

```csharp
// 实例化 + 外观 + 事件，仅此三类
this.table1 = new AntdUI.Table();
this.table1.Dock = System.Windows.Forms.DockStyle.Fill;
this.table1.Gap = 12;                    // 外观属性 OK
this.table1.CellClick += this.table1_CellClick;  // 事件订阅 OK
// ✘ 禁止：Columns = ...、DataSource = ...、Binding(...)、任何 AntList<T> 字样
```

**.cs 代码后置（构造函数）——三段式固定顺序：**

```csharp
private AntdUI.AntList<MyRow> _rows;   // ① 类级持有绑定列表（字段声明处不带初始化器）

public MyForm()
{
    InitializeComponent();
    InitTableColumns();                 // ② 先列
    _rows = new AntdUI.AntList<MyRow>();
    table1.Binding(_rows);              // ③ 后数据（一次 Binding，之后只操作 _rows）
}

private void InitTableColumns()
{
    table1.Columns = new AntdUI.ColumnCollection
    {
        new AntdUI.Column("SeamWidth", "焊缝宽度") { Width = "150" },  // Width 是 string
        new AntdUI.Column("RobotSpeed", "焊接速度") { Width = "150" },
    };
}
```

**动态刷新数据（Binding 之后不再重新赋 DataSource）：**

```csharp
// 增/删/清空 直接操作已绑定的 AntList<T>，Table 自动刷新
_rows.Clear();
foreach (var x in data) _rows.Add(new MyRow { ... });
// 整批替换列表实例时才需要重新 Binding：
table1.Binding(newList);
```

要点：
- `Binding<T>(AntList<T>)` 为官方动态加载入口；`AntList<T>` 版支持 add/edit/del 增量刷新，性能优于整表重绑。
- 运行时 `table1.DataSource = list;` 虽能编译运行，但**统一用 `Binding()`**——语义明确、走增量刷新路径。
- 行数据类 `T` 用普通 property 即可；需要单元格级双向刷新才继承 `NotifyProperty`。
- 取选中行：`CellClick` 事件 `e.Record as MyRow`（Table 无 SelectedItem）。

#### 补充范式：可编辑表格 + 列宽填满

**① 让表格可编辑（双击进入编辑）**：`EditMode=TEditMode.DoubleClick` + 目标列 `.SetEditable(true)` + 订阅 `CellEndEdit` 写回行对象。

```csharp
// InitTableColumns 中
table1.EditMode = AntdUI.TEditMode.DoubleClick;
table1.Columns = new AntdUI.ColumnCollection
{
    // 只读列不调 SetEditable；可编辑列调之
    new AntdUI.Column("SeamWidth", "焊缝宽度") { Width = "150" },
    new AntdUI.Column("RobotSpeed", "焊接速度") { Width = "150" }.SetEditable(true),
};

// 构造函数订阅写回
table1.CellEndEdit += table1_CellEndEdit;

private bool table1_CellEndEdit(object sender, AntdUI.TableEndEditEventArgs e)
{
    MyRow row = e.Record as MyRow;
    if (row == null || e.Value == null) return true;
    switch (e.Column.Key)          // e.Column.Key 是列绑定属性名
    {
        case "RobotSpeed": row.RobotSpeed = e.Value; break;
    }
    return true;
}
```

要点：`CellEndEdit` 签名返回 `bool`；`e.Column.Key` 才是列绑定属性名（非表头中文）。

**② 列宽填满表格区域（不留下空白）**：统一设 `AutoSizeColumnsMode = AntdUI.ColumnsMode.Fill`。`ColumnsMode.Fill` 使各列按设定 `Width` 的相对权重拉伸填满整个 Table 宽度；凡有 Table 的窗体一律加此设置，`Width` 值仍须保留（作为最小宽度与权重基准）。

#### 禁止行为清单

- Designer.cs 内写 `Columns = new ColumnCollection{...}`、`DataSource = new AntList<T>()`、`DataSource = 局部AntList变量`、`Binding(...)` 中的任意一种。
- `InitializeComponent` 内声明 `AntdUI.AntList<T>` 局部变量。
- 运行时用 `DataSource =` 替代 `Binding()`（能跑但违反本项目统一范式）。

---

### 4.2 Table 用 ColumnCheck 实现单选互斥

#### 问题

需要一张表格，表头为 `No. | 选取 | 文件名`，其中「选取」列要 **checkbox 外观（方框勾选）**，但行为是**单选互斥**——一次只能选中一行，选中另一行后前一行自动取消。

AntdUI 内置的 `ColumnRadio` 能自动单选互斥，但渲染成 **radio 圆点**，不是用户要的 checkbox 方框；`ColumnCheck` 渲染成 checkbox 方框，但默认是**多选**（可勾选多行），需手动实现互斥。

#### 关键结论（源码确证）

1. **`ColumnCheck` 单参 vs 双参的表头差异**：
   - `ColumnCheck(key)`（单参）→ 内部 `NoTitle=true` → 表头渲染**全选 checkbox**，点击表头触发 `CheckAll` 全选。
   - `ColumnCheck(key, title)`（双参）→ `NoTitle=false` → 表头渲染**纯文字 title**，**无全选 checkbox**，点击表头不触发全选。
   - 结论：要「表头显示文字 + 无全选」，用**双参** `ColumnCheck("Selected","选取")`。

2. **`SetAutoCheck(false)` 关闭单元格自动 toggle**：
   - 默认 `AutoCheck=true` 时，点击 checkbox 单元格会自动 toggle 行值，与手动互斥逻辑叠加会产生闪烁/竞态。
   - 置 `false` 后点击不自动 toggle，改由 `CellClick` 统一控制单选，逻辑集中、无竞态。

3. **行模型继承 `AntdUI.NotifyProperty` 才能驱动刷新**：
   - Table 对 `INotifyPropertyChanged` 行对象挂 `Notify_PropertyChanged`，属性变更时经 `RefreshItem` 同步 checkbox 单元格。
   - 行模型 `Selected` 属性 setter 里调 `OnPropertyChanged()`，代码里改 `row.Selected` 即刷新复选框。

4. **`CellClick` 在任意单元格（含 checkbox 列）点击后触发**，可统一做互斥。

#### 固定范式

**Designer.cs**（只留外观 + 事件订阅，禁 Columns/Binding/AntList）：
```csharp
this.uiTableRecord = new AntdUI.Table();
this.uiTableRecord.Dock = System.Windows.Forms.DockStyle.Fill;
this.uiTableRecord.Font = new System.Drawing.Font("宋体", 12F);
this.uiTableRecord.Gap = 12;
this.uiTableRecord.CellClick += this.uiTableRecord_CellClick;  // 方法组订阅
```

**.cs 代码后置**（三段式 + 单选互斥）：
```csharp
private AntdUI.AntList<FileTraceRow> _recordRows;   // 字段不带初始化器
private FileTraceRow _selectedRecord;

public XxxForm(Window _window)
{
    Window = _window;
    InitializeComponent();
    InitTableColumns();
    _recordRows = new AntdUI.AntList<FileTraceRow>();
    uiTableRecord.Binding(_recordRows);
}

private void InitTableColumns()
{
    uiTableRecord.Columns = new AntdUI.ColumnCollection
    {
        new AntdUI.Column("No", "No.") { Width = "60" },
        // 双参 = 表头「选取」无全选；SetAutoCheck(false) 关闭自动 toggle
        new AntdUI.ColumnCheck("Selected", "选取") { Width = "80" }.SetAutoCheck(false),
        new AntdUI.Column("FileName", "文件名") { Width = "400" }
    };
    uiTableRecord.AutoSizeColumnsMode = AntdUI.ColumnsMode.Fill;
}

private void uiTableRecord_CellClick(object sender, AntdUI.TableClickEventArgs e)
{
    var row = e.Record as FileTraceRow;   // 点击表头时 e.Record 不是行对象，as 得 null 跳过
    if (row == null) return;
    _selectedRecord = row;
    foreach (var r in _recordRows)
        r.Selected = (r == row);           // 单选互斥：只当前行 true
}

// 行模型：Selected 继承 NotifyProperty 驱动刷新
private class FileTraceRow : AntdUI.NotifyProperty
{
    public int No { get; set; }
    private bool _selected;
    public bool Selected
    {
        get { return _selected; }
        set { if (_selected == value) return; _selected = value; OnPropertyChanged(); }
    }
    public string FileName { get; set; }
    public string FilePath { get; set; }
}
```

要点：
- 点击已选中行不会取消（单选语义下「保持至少一项选中」）；若要允许取消，改 `r.Selected = (r == row && !row.Selected)`。
- `SetAutoCheck` 返回基类 `Column`，链式调用后不能再调 `ColumnCheck` 独有方法。
- `e.Record as FileTraceRow` 判空即防御表头/汇总行点击。

---

## 5. 对话框与消息

### 5.1 Modal 承载 UserControl（对话窗范式）

#### 背景

AntdUI **不**推荐为每个对话窗新开 `AntdUI.Window`，而是把对话内容做成 `UserControl`，用 `AntdUI.Modal.open` 承载。本范式由 ADR-022 采纳，取代旧的 `Window+PageHeader` 范式。

#### 调用点标准写法

```csharp
// UserControl 内调用（owner 用 this.FindForm()）
using (var form = new XxxForm())
{
    AntdUI.Modal.open(new AntdUI.Modal.Config(this.FindForm(), "标题", form, TType.Info)
    {
        CloseIcon = true,   // 右上角关闭 X
        BtnHeight = 0       // 不显示 Modal 自带底部按钮（对话窗自带内部按钮）
    });
}

// Window / Form 内调用（owner 用 this）
using (var form = new UserEdit())
{
    AntdUI.Modal.open(new AntdUI.Modal.Config(this, "用户管理", form, TType.Info)
    {
        CloseIcon = true,
        BtnHeight = 0
    });
}
```

`Modal.open` **阻塞并返回 `DialogResult`**。

#### 注入父 Window（复刻 AntdUI demo SystemSet 模式）

每个对话 `UserControl` 通过构造函数注入父 `AntdUI.Window` 并存储为 `private readonly Window Window`，内部方法（`Message` / 嵌套 `Modal`）统一以 `this.Window` 作 owner，而非 `this.FindForm()`。

##### 对话窗标准结构

```csharp
public partial class XxxForm : UserControl
{
    // 注入的父窗口（demo SystemSet 模式）
    private readonly Window Window;

    // 设计时 / 无父窗口：链到带参构造，Window=null（设计器需要无参构造）
    public XxxForm() : this(null) { }

    // 运行时：调用点传入父 Window
    public XxxForm(Window _window)
    {
        Window = _window;
        InitializeComponent();
        // ... 事件订阅 / 初始化
    }

    void SomeHandler(object sender, EventArgs e)
    {
        // 内部消息：owner 用 this.Window（指向主窗口），不用 this.FindForm()
        AntdUI.Message.success(this.Window, "完成");
        // 嵌套确认 Modal：owner 同样用 this.Window
        AntdUI.Modal.open(new AntdUI.Modal.Config(this.Window, "确认", "?", TType.Info));
        // 关闭仍用 this.FindForm().DialogResult（Modal 宿主窗体，切勿用 this.Window）
        var host = this.FindForm();
        if (host != null) host.DialogResult = DialogResult.OK;
    }
}
```

##### 调用点标准写法

- `Window`/`Form` 内调用（如 `FormMain`）：直接传 `this`
  ```csharp
  using (var form = new XxxForm(this)) { AntdUI.Modal.open(new AntdUI.Modal.Config(this, "标题", form, TType.Info) { CloseIcon = true, BtnHeight = 0 }); }
  ```
- `UserControl` 页内调用：`this` 是 UserControl 非 Window，须传父窗口 `this.FindForm() as AntdUI.Window`
  ```csharp
  using (var form = new XxxForm(this.FindForm() as AntdUI.Window)) { AntdUI.Modal.open(new AntdUI.Modal.Config(this.FindForm(), "标题", form, TType.Info) { CloseIcon = true, BtnHeight = 0 }); }
  ```

##### 易错点

1. **`readonly Window` 字段必须在带参构造赋值**：保留 `public XxxForm() : this(null)` 链到带参构造，否则设计器无法实例化（CS0171 / 设计器报错）。
2. **内部 owner 用 `this.Window` 不用 `this.FindForm()`**：`FindForm()` 返回的是 Modal 宿主窗体；`Window` 才是真正的父主窗口，消息锚定更正确。
3. **关闭必须用 `this.FindForm().DialogResult`**：`this.Window` 是主窗口，设其 `DialogResult` 不会关闭当前 Modal。
4. **`Window` 即 `AntdUI.Window` 类型**：`UserControl` 调用点需 `this.FindForm() as AntdUI.Window` 转换。

#### UserControl 对话窗的改造要点

1. **基类 `AntdUI.Window` → `System.Windows.Forms.UserControl`**。
2. **取消 PageHeader**：删除 Designer.cs 中 `pageHeader1` 的实例化/属性块/字段/`Controls.Add`，以及 `ControlBox`/`MaximizeBox`/`MinimizeBox`/`ShowIcon`/`ShowInTaskbar` 等窗体专属属性；`ClientSize`→`Size`。
3. **关闭 / 返回值**（UserControl 无 `DialogResult`/`Close`）：
   ```csharp
   private void btnOK_Click(object sender, EventArgs e)
   {
       var host = this.FindForm();
       if (host != null) host.DialogResult = DialogResult.OK;
   }
   private void btnCancel_Click(object sender, EventArgs e)
   {
       var host = this.FindForm();
       if (host != null) host.DialogResult = DialogResult.Cancel;
   }
   ```
   > 原理：`AntdUI.Modal` 内部把内容 `UserControl` 放进一个 `Form` 并以 `ShowDialog` 方式呈现；`FindForm()` 从该 `UserControl` 向上取到这个 Modal 宿主 `Form`。设其 `DialogResult` 即触发关闭，`Modal.open` 返回该值。
4. **`Message.*(this,…)` → `Message.*(this.FindForm(),…)`**：`UserControl` 不能隐式转 `AntdUI.Target`（CS1503）。
5. **`FormClosing` → `HandleDestroyed`**：UserControl 无 `FormClosing`；原 `FormClosing` 里做的资源回收（如停定时器）改订阅 `this.HandleDestroyed`。不重写 `Dispose(bool)`。
6. **resx 根类型引用**：若 resx 的 `$this.Type` 仍指向 `AntdUI.Window`，须改为 `System.Windows.Forms.UserControl`。
7. **内部再弹确认 Modal**：对话窗内部如需二次确认，可 `new Modal.Config(this, "确认删除", msg, TType.Info)`（`this` 即对话 UserControl，作 `Control` owner 合法）独立嵌套。

#### 易错点

1. **`Modal.open` 是阻塞的**：必须在 UI 线程调用（按钮事件里即可）；不要在 Workflow/后台线程弹。
2. **关闭不能用 `this.Close()`**：UserControl 无此方法，编译失败；必须用 `FindForm().DialogResult`。
3. **`FindForm()` 可能为 null**（设计器预览/未挂载时）：设 `DialogResult` 前判空。
4. **`using` 块**：`Modal.open` 返回后（模态已关闭）才退出 `using` 释放 `UserControl`；在 `using` 块内（Modal 关闭后）读取 `form.PublicProperty` 安全。

---

### 5.2 Message/Modal 的 owner 类型

#### 背景

`AntdUI.Message.*(owner, text)` 的第一个参数（owner）类型为 **`AntdUI.Target`**（引用类型）；而 `AntdUI.Modal.open(new Modal.Config(owner, …))` 的 owner 类型为 **`Control`/`IWin32Window`**。**两者 owner 类型不同**。

`AntdUI.Target` 只对**顶层窗口**提供隐式转换：
- `AntdUI.Window` → ✅ 可隐式转换为 `Target`
- `System.Windows.Forms.Form` → ✅ 可隐式转换
- `System.Windows.Forms.UserControl`（以及一般 `Control`）→ ❌ **不可隐式转换**

因此，在 `: AntdUI.Window` / `: Form` 类里写 `AntdUI.Message.warn(this, …)` 能编译；在 `: UserControl` 类里写同样的 `this` 会报 **CS1503「参数 1: 无法从 Xxx(UserControl) 转换为 AntdUI.Target」**。

#### 新坑：裸 null 的 CS0121 二义

`AntdUI.Message.*` 同时提供 `(AntdUI.Target, …)` 与 `(System.Windows.Forms.Form, …)` 两个重载。裸 `null` 对**两个引用类型重载都可用** → 编译器报 **CS0121「以下方法或属性之间的调用具有二义性」**。故 **UserControl 内禁止裸传 `null`**。

#### 正确写法

**方案 A（推荐，UserControl 内首选）：owner 传 `System.Windows.Forms.Form.ActiveForm`**

```csharp
AntdUI.Message.warn(System.Windows.Forms.Form.ActiveForm, "未找到生产数据文件夹");
AntdUI.Message.error(System.Windows.Forms.Form.ActiveForm, "已存在当前命名配置");
```

**方案 B（确需裸 null owner 时）：显式强转 `Target` 消歧**

```csharp
AntdUI.Message.warn((AntdUI.Target)null, "未找到生产数据文件夹");
```

**方案 C（UserControl 想锚定自身父窗体）：`this.FindForm()`**

```csharp
AntdUI.Message.warn(this.FindForm(), "提示");
```

> ⚠️ `new AntdUI.Target(this)`（以 UserControl 构造 Target）**不可行**：`Target` 仅接受 Window/Form 隐式转换，UserControl 无法转换。

**`Modal.open` 的 owner 是 `Control`/`IWin32Window`**：裸 `null` 对 `Modal.Config` **不二义**（无 `Target`/`Form` 双重载），可编译；但为锚定正确父窗体，非 UI 类与 UserControl 内仍用 `System.Windows.Forms.Form.ActiveForm`（或 `this.FindForm()`）；`Window`/`Form` 类内用 `this` 即可。

#### 判定要点

| 调用者基类 | `Message.*(this,…)` / `Modal(open(Config(this,…)))` | 说明 |
|-----------|------------------------------------------------------|------|
| `: AntdUI.Window` 或 `: Form` | ✅ 编译通过 | `this` 即顶层窗口，精确绑定 `Form` 重载，无二义 |
| `: UserControl` | `Message.*(this,…)` ❌ CS1503；`Message.*(null)` ❌ CS0121 二义；`Modal(Config(this,…))` ✅ 可编译 | `Message` 必须改 `Form.ActiveForm` / `(AntdUI.Target)null` / `this.FindForm()`；`Modal` 用 `this.FindForm()` 或 `Form.ActiveForm` 锚定更准 |
| 非 UI 类（无 `this` 控件） | ❌ 无 Control | 用 `Form.ActiveForm` 或 `(AntdUI.Target)null` |

---

### 5.3 Window-PageHeader 旧范式（历史参考，已废弃）

> ⚠️ **本文已废弃**：2026-07-30 经 ADR-022 采纳 AntdUI 官方 Demo 范式——对话窗改为 **Modal 承载的 `UserControl`**（取消 PageHeader），本「Window + PageHeader」方案被取代。保留作历史参考。

#### 旧范式要点

项目内所有继承 `AntdUI.Window` 的窗体须遵循统一 AntdUI 设计方式：顶部放置 `AntdUI.PageHeader` 作为标题栏，并由 PageHeader 提供最小化/关闭按钮（`ShowButton=true`），同时关闭 WinForms 原生标题栏按钮（`ControlBox=false`），避免双标题栏。

#### 布局重排规则（关键坑）

| 原内容布局方式 | PageHeader 插入后处理 |
|---|---|
| `Dock=Fill` / `Dock=Top`（在 PageHeader 之后 Add） | 自动重排，**无需改动** |
| `Anchor` 绝对定位 | **手工整体下移 36px**，且 `ClientSize.Height += 36` |
| 浮动控件（如 ToolStrip，非 Dock） | 视觉对齐微调（35→36） |

#### 踩过的坑

1. **脚本批量插入须幂等**：批量脚本跑完必须用计数验证兜底。
2. **老代码缩进不一致导致 anchor 失配**：缩进匹配 0 次被幂等逻辑静默跳过。
3. **ControlBox=false 必须同步设置**：只加 PageHeader 不关 ControlBox 会出现双标题栏。

---

## 6. 命名空间与类型冲突（CS0104）

### 6.1 问题描述

`using AntdUI;` 与 `using System.Windows.Forms;` 同时存在于一个文件时，若二者都导出了**同名类型**，则该类型裸用会触发 **CS0104「XXX 是 Y 和 Z 之间的不明确引用」**。

本项目实测暴露的同名冲突类型：

| 类型名 | 候选 A | 候选 B | 触发文件 |
|--------|--------|--------|----------|
| `FolderBrowserDialog` | `AntdUI.FolderBrowserDialog`（`.DirectoryPath`） | `System.Windows.Forms.FolderBrowserDialog`（`.SelectedPath`） | RecordConfigForm.cs |
| `Message` | `AntdUI.Message`（静态类） | —（与 Windows 消息 API 易混，且 `Message.*` 自身含 `Target`/`Form` 双重载） | 见 Message/Modal owner 章节 |
| `MenuItem` | `AntdUI.MenuItem`（`.Text`/`.Tag`，用于 `Menu.Add`） | `System.Windows.Forms.MenuItem`（旧 WinForms 菜单项） | ImagePage.cs、ParamPage.cs |

### 6.2 为什么发生

SunnyUI→AntdUI 迁移后，几乎所有 UI 文件都保留 `using System.Windows.Forms;`（WinForms 基类、DialogResult、FolderBrowserDialog 等仍来自 BCL），同时新增 `using AntdUI;`。AntdUI 重新实现了若干 WinForms 同名控件/对话框（如 `FolderBrowserDialog`、`Message`），于是裸写 `new FolderBrowserDialog()` 落入两个候选，编译器无法抉择。

### 6.3 正确做法（修复模式）

**全限定类型名**，明确指定想要的那一个。

> **项目约定**：本项目统一采用 `AntdUI.FolderBrowserDialog` + `.DirectoryPath` 属性（AntdUI 版路径属性名为 `DirectoryPath`，与 WinForms 版的 `SelectedPath` **不同**）。后续凡涉及 `FolderBrowserDialog`，一律按此写法。

> **项目约定**：凡文件同时含 `using AntdUI;` 与 `using System.Windows.Forms;`，**所有 `MenuItem` 一律强制用 `AntdUI.` 前缀限定**（`AntdUI.MenuItem`），消除 CS0104。

```csharp
// 项目约定写法：AntdUI.FolderBrowserDialog + DirectoryPath
AntdUI.FolderBrowserDialog folderDialog = new AntdUI.FolderBrowserDialog();
...
folderDialog.DirectoryPath = txtRecordPath.Text;
if (folderDialog.ShowDialog() == DialogResult.OK)
    txtRecordPath.Text = folderDialog.DirectoryPath;
```

- 若特殊场景确需 WinForms 原生对话框，则全限定 `System.Windows.Forms.FolderBrowserDialog` 且用 `.SelectedPath`（属性名不同，勿混用）。
- 不要为消歧而**删除** `using System.Windows.Forms;`（文件里 `DialogResult`、`EventArgs`、基类 `Form` 等都依赖它）；全限定是最小变更。

### 6.4 禁止行为

- 因 `using System.Windows.Forms;` 导致歧义就直接删掉它（会连带破坏 `DialogResult`/`Form`/`EventArgs` 等引用）。
- 在同时 `using AntdUI;` 与 `using System.Windows.Forms;` 的文件里裸写 `MenuItem`（必 CS0104）；须 `AntdUI.MenuItem` 全限定。
- 用 `var` 却不在 `new` 处消歧（裸 `var x = new FolderBrowserDialog()` 同样 CS0104）。
- 把 `AntdUI.FolderBrowserDialog` 当 WinForms 版用 `.SelectedPath`（AntdUI 版路径属性是 `.DirectoryPath`，混用会 CS1061）。

---

## 7. 迁移 API 差异

### 7.1 控件 API 差异总览

以下为 SunnyUI/WinForms 控件迁移到 AntdUI 后，常见的 API 差异与迁移坑：

| # | 问题 | 现象 | 修复 |
|---|------|------|------|
| 1 | `AntdUI.Select` 无 `DataSource` | CS1061「"Select"未包含"DataSource"的定义」 | 直接删除 `DataSource = null` 行 |
| 2 | `AntdUI.Column.Width` 是 `string` | 「无法将类型"int"隐式转换为"string"」 | `Width = "120"`（字符串） |
| 3 | `GridPanel.Controls.Add` 仅单参数 | WinForms 3 参 `Add(ctrl,col,row)` 不支持 | 改为 `Controls.Add(ctrl)`，布局由 `Span`/`SetColumnSpan` 承担 |
| 4 | `AntdUI.Splitter` 继承 WinForms `SplitContainer` | — | `Panel1`/`Panel2`/`SplitterDistance` 全部合法，勿当错误乱删 |
| 5 | `Table.DataSource` 仅运行时合法，Designer 禁写 | 设计器报「未能找到类型 AntdUI.AntList\`1」 | 删除 Designer 内全部 `DataSource`/`AntList`；统一用 `table.Binding(antList)` |
| 6 | 设计器"System.Void"多为项目级联编译错误 | 报错窗体自身 Designer.cs 可能干净 | 先修复全项目其它编译错误 |
| 7 | `InputNumber.Value` 是 `decimal` | double/float 字段互赋报隐式转换错误 | 双向显式强制转换：`= (decimal)字段` / `字段 = (double)ctrl.Value` |
| 8 | `Table.CellClick` 用自定义委托 | `new System.EventHandler<TableClickEventArgs>` 报隐式转换错误 | 方法组订阅 `+= this.handlerName;` 或 `new AntdUI.Table.ClickEventHandler(...)` |
| 9 | `InputNumber` 无 `Step` 属性 | CS1061「"InputNumber"未包含"Step"的定义」 | 用 `Increment`（decimal 字面量 `M` 后缀） |
| 10 | `Tabs.AddTabSelect` 收 `TabPage` 非 `UserControl` | CS1503「无法从 XxxPage 转换为 AntdUI.TabPage」 | UserControl 先包进 `TabPage.Controls` 再传 |
| 11 | `InputNumber` 字面量须用 `M` 后缀 | `10D`/`0.5D` 报 double→decimal 转换错误 | 全量 `D`→`M`（`10M`/`0.5M`）；decimal→int 存回须 `(int)ctrl.Value` |
| 12 | `Modal.Config` 必须用 4 参构造 | 「"open"方法没有采用 1 个参数的重载」 | `new Modal.Config(owner, title, content, TType.Info)` |
| 13 | `Table` 没有 `ReadOnly` 属性 | CS1061「"Table"未包含"ReadOnly"的定义」 | 直接删除（表格默认只读，`EditMode=None`）；列级用 `Column.SetReadOnly(true)` |
| 14 | `GridPanel.Span` 语法须以源码为准 | 布局异常、白板、区域不可见 | 按权威语法书写；禁用 `px`/`auto`；子控件逆序入格 |

### 7.2 详细说明（高频坑）

#### ① Select 无 DataSource

AntdUI.Select 用 `.Items`（`AntdUI.SelectItem`）填充，无 WinForms `ComboBox.DataSource`。修复：直接删除 `DataSource = null` 行（设计器原多写此行初始化，迁移后非法）。

#### ② Column.Width 是 string

`new AntdUI.Column("X","Y") { Width = 120 }` 报错。修复：`Width = "120"`。

#### ⑦ InputNumber.Value 是 decimal

`AntdUI.InputNumber.Value` 是 `decimal`（非 SunnyUI 的 `double`/`float`）。双向显式强制转换：
- 加载到界面：`ctrl.Value = (decimal)param.DoubleField;` / `(decimal)renderConfig.FloatField;`
- 从界面存回：`param.DoubleField = (double)ctrl.Value;` / `renderConfig.FloatField = (float)ctrl.Value;`

`.Value` 为非可空 `decimal`，`(float)ctrl.Value`/`(double)ctrl.Value` 直接强转即可。

#### ⑧ Table.CellClick 自定义委托

`AntdUI.Table.CellClick` 用自定义委托 `AntdUI.Table.ClickEventHandler`（非 `System.EventHandler<AntdUI.TableClickEventArgs>`）。

修复：改为方法组订阅 `this.table1.CellClick += this.table1_CellClick;`（最简洁），或显式 `new AntdUI.Table.ClickEventHandler(this.table1_CellClick)`。

处理器签名：`void table1_CellClick(object sender, AntdUI.TableClickEventArgs e)`；选中行用 `e.Record as TRow`。

#### ⑨ InputNumber 步进量用 Increment

从 React antd 误带过来的写法 `inputNumber.Step = 0.5D;` 报错。AntdUI `InputNumber` 步进量属性名为 **`Increment`**（`public decimal Increment { get; set; } = 1;`）。

修复：`this.PointSize.Increment = 0.5M;`（用 `decimal` 字面量 `M` 后缀）；整数步进 `this.WireDiameter.Increment = 1M;`。

#### ⑩ Tabs.AddTabSelect 收 TabPage

把 `UserControl` 子页直接 `tabs.AddTabSelect(userControl)` 报 CS1503。根因：`Tabs.AddTabSelect(TabPage)` 的形参是 `AntdUI.TabPage`（承载容器），不是 `UserControl`。

修复范式：
```csharp
_ilPage = new ILAlgoPage(_ilCamera);
_ilPage.Dock = DockStyle.Fill;
AntdUI.TabPage ilTab = new AntdUI.TabPage { Text = "英莱算法", Tag = _ilPage };
ilTab.Controls.Add(_ilPage);
tabsAlgo.AddTabSelect(ilTab);
```

#### ⑪ InputNumber 十进制字面量 M 后缀

设计器里 `Maximum = 10D;`/`Minimum = 0.5D;`/`Value = 2D;` 报「无法将类型"double"隐式转换为"decimal?"/"decimal"」。`D` 是 `double` 后缀，`M` 才是 `decimal` 后缀。

修复：全量 `D`→`M`（`10D`→`10M`、`0.5D`→`0.5M`、`0D`→`0M`）。

同时，`RenderConfig` 部分字段声明为 `int`，`ctrl.Value`(decimal)→`int` 字段**不能**隐式转换，存回必须 `(int)ctrl.Value`。

#### ⑫ Modal.Config 4 参构造

本地 AntdUI 的 `Config` 构造函数缺 3 参 `(Form,string,string)`。根因不是 `open` 缺重载——1 参 `open(this Config)` 存在——而是 `Config` 构造函数缺 3 参。

修复：把 `Icon` 从对象初始化器移入第 4 个构造参数——`new Modal.Config(this, "确认", "是否注销权限？", TType.Info)`。

> ⚠️ AntdUI 经 NuGet 还原、csproj 未钉版本，不同版本 `Config` 构造器签名可能不同；升级后若出现此错，优先核查 `Config` 构造器的参数个数/类型（4 参带 `TType icon` 最稳）。

#### ⑬ Table 无 ReadOnly

`AntdUI.Table` 没有 `ReadOnly` 属性（表格默认只读，`EditMode=None`）。整表级没有 `ReadOnly` 属性；仅 `Column` 级有 `Column.ReadOnly`/`SetReadOnly(true)`。

修复：直接删除 `*.ReadOnly = ...` 这些无效赋值（表格本就只读）。若确需行内编辑，改用 `table.EditMode = AntdUI.TEditMode.Cell`（并配合列 `Column.SetEditable(true)`）。

> ⚠️ 区分：`AntdUI.Input`（`TextBox` 类）**有** `ReadOnly` 属性，勿误删。

#### ⑭ GridPanel.Span 语法

`;` 分行；每行可用 `高度:列1 列2` 内联行高前缀（`:` 合法）；`-` 后接全局行高表（空格分隔）；合法值仅 `fill` / `N%` / 整数（×DPI 像素）/ 浮点数；`_N` 后缀=空占位（合法）。真正的非法 token 是 **`100px`、`auto`**——解析失败返回 0 → 强制 1px 宽 → 白板/不可见。

另一关键坑：**单元格按 `Controls.Add` 的逆序分配给子控件**（`SyncMap` 倒插+排序），Designer 里 Add 顺序必须写成期望单元格顺序的**倒序**。

完整语法参见第 2.2 节「GridPanel.Span 完整语法」。

### 7.3 禁止行为清单

- 给 `AntdUI.Select` 写 `DataSource`（含 `= null`）。
- 在 `*.Designer.cs` 内写 `Table.DataSource = ...` 或声明 `AntdUI.AntList<T>` 局部变量。
- `AntdUI.Column.Width` 写 int。
- 给 `AntdUI.GridPanel` 写 3 参数 `Controls.Add(ctrl,col,row)`。
- 把 `AntdUI.InputNumber.Value` 当 `double`/`float` 直接赋值给 `double`/`float` 字段而不显式强转。
- 给 `AntdUI.InputNumber` 写 `.Step`（用 `Increment`）。
- 给 `AntdUI.Tabs.AddTabSelect` 直接传 `UserControl`（应包进 `AntdUI.TabPage` 再传）。
- 给 `AntdUI.InputNumber` 的 `Value`/`Minimum`/`Maximum` 用 `D`（double）字面量后缀（须 `M`）。
- 把 `AntdUI.InputNumber` 的 `decimal` 值直接赋给 `int` 字段而不 `(int)` 强转。
- 给 `AntdUI.Table.CellClick` 写 `new System.EventHandler<AntdUI.TableClickEventArgs>(...)` 包装。
- 给 `AntdUI.Modal.Config` 用 3 参构造（本地 AntdUI 缺该重载，须 4 参带 `TType` icon）。
- 给 `AntdUI.Table` 写 `ReadOnly`（不存在；仅 `Input`/`TextBox` 有 `ReadOnly`，列级才用 `Column.ReadOnly`/`SetReadOnly`）。
- 在 `AntdUI.GridPanel.Span` 中使用 `px`/`auto` 等带字母单位（解析为 0→1px 白板）。
- 假设 GridPanel 子控件按 `Controls.Add` 顺序入格——实际是**逆序**。
- 在 `RichTextBox` → `AntdUI.Input` 迁移后仍使用 `SelectionColor`（`AntdUI.Input` 基于 TextBox，无彩色文本能力）。

---

## 8. 迁移状态追踪（简要版）

### 总体状态

**25/25 UI 文件全部完成从 SunnyUI → AntdUI 迁移**（Designer.cs + .cs 代码后置）。全量 Grep 确认：
- `using Sunny.UI;` = 0 命中（所有 .cs）
- `private Sunny.UI` / `new Sunny.UI` = 0 命中（所有 .Designer.cs）
- `UIMessageBox`（代码）= 0 命中（仅注释残留）
- `System.Windows.Forms.DataGridView` = 0 命中（全部为 `AntdUI.Table` + `AntList<T>`）

### 缺口 / 待验证项

| 项 | 状态 | 说明 |
|----|------|------|
| Chart 数据绑定 API（`ChartDataset`/`AddPoint`/`AddDataset`/`RefreshChart`） | 🟡 待验证 | MainPage/DataReview 已按真实 API 实装，待 VS x64 确认项目 AntdUI.dll 版本含这些成员 |
| DataReview X 轴缩放（`SetRange` 替代方案） | 🟡 待验证 | 待 VS 验证 `XMin`/`XMax` 赋值 + `RefreshChart` 方案 |
| 变量命名遗留（`uiDataGridView1` 实为 `AntdUI.Table` 等） | 🟢 功能无碍 | 仅命名习惯，建议后续清理 |

> **完整的 SunnyUI → AntdUI 迁移追踪、决策与历史记录** 见 SunnyUI 归档文档。本文档聚焦 AntdUI 开发 API 参考，不重复 SunnyUI 迁移的历史细节。

---

## 来源

本文档由以下专项 lessons 与决策文档合并整理而成：

1. `AntdUI-DesignParadigm.md` — 设计范式枢纽页（第 1 节）
2. `AntdUI-GridPanel-Span-Syntax.md` — GridPanel.Span 语法（第 2.2 节）
3. `AntdUI-SplitterToGridPanel-FixedRegion.md` — Splitter→GridPanel 改造（第 2.4 节）
4. `decisions/ADR-031-LayoutContainerFreedom.md` — 布局容器自由化决策（第 2.1 节）
5. `AntdUI-Menu-Tabs-Navigation.md` — Menu + Tabs 导航（第 3.1 节）
6. `AntdUI-Tabs-ControlsAndPages.md` — Tabs Controls.Add + Pages.Add（第 3.3 节）
7. `AntdUI-TableColumns-DesignerSerialization.md` — Table 列与数据绑定（第 4.1 节）
8. `AntdUI-Table-ColumnCheck-SingleSelect.md` — ColumnCheck 单选互斥（第 4.2 节）
9. `AntdUI-Modal-UserControl-Dialog.md` — Modal 承载 UserControl（第 5.1 节）
10. `AntdUI-MessageOwner-Target.md` — Message/Modal owner 类型（第 5.2 节）
11. `AntdUI-Window-PageHeader-Top.md` — Window+PageHeader 旧范式（第 5.3 节，历史参考）
12. `AntdUI-NamespaceTypeCollision-CS0104.md` — 命名空间类型冲突（第 6 节）
13. `AntdUI-ControlAPI-MigrationPitfalls.md` — 控件 API 迁移坑（第 7 节）
14. `AntdUI-MigrationTracker.md` — 迁移追踪表（第 8 节，简要版）

