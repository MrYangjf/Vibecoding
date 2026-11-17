---
title: AntdUI 完整开发参考
date: 2026-08-18
updated: 2026-11-02
tags: [指导, UI, AntdUI, 参考手册, 汇总]
---

# AntdUI 完整开发参考

## 章节导航

- [0. ⭐ 权威源：官方 wiki 全量镜像（2026-10-09 起取代 demo 与反编译）](#0--权威源官方-wiki-全量镜像2026-10-09-起取代-demo-与反编译)
- [旧章节：控件应用参考 demo（⛔ 2026-10-09 起降级为「次级参考」）](#旧章节控件应用参考-demo-2026-10-09-起降级为次级参考)
- [2. 布局系统](#2-布局系统)
- [3. 导航与菜单](#3-导航与菜单)
- [4. 表格控件](#4-表格控件)
- [4.6 Tooltip 跟随提示（2026-10-09 实证）](#46-tooltip-跟随提示2026-10-09-实证)
- [4.11 ⭐ `Select` 下拉选择器：「安全名单」与属性边界（2026-10-09 实证）](#411--select-下拉选择器安全名单与属性边界2026-10-09-实证)
- [5. 对话框与消息](#5-对话框与消息)
- [6. 命名空间与类型冲突（CS0104）](#6-命名空间与类型冲突cs0104)
- [7. 迁移 API 差异](#7-迁移-api-差异)
- [8. 迁移状态追踪（简要版）](#8-迁移状态追踪简要版)
- [来源](#来源)

> **章节导航**（本页超长页请先按章节定位再读）：
>
> - [0. ⭐ 权威源：官方 wiki 全量镜像](#0-权威源官方-wiki-全量镜像2026-10-09-起取代-demo-与反编译)
> - [1. 设计范式总览](#1-设计范式总览)
> - [2. 布局系统](#2-布局系统)
> - [3. 导航与菜单](#3-导航与菜单)
> - [3.4 ContextMenuStrip 右键菜单](#34-contextmenustrip-右键菜单)
> - [4. 表格控件](#4-表格控件)
> - [5. 对话框与消息](#5-对话��与消息)
> - [6. 命名空间与类型冲突（CS0104）](#6-命名空间与类型冲突cs0104)
> - [7. 迁移 API 差异](#7-迁移-api-差异)
> - [8. 迁移状态追踪（简要版）](#8-迁移状态追踪简要版)
> - [来源](#来源)


> **位置说明（2026-09-01）**：本页自 `wiki/lessons/` 迁入 `wiki/guides/`。
> 分类判据：**`guides/` = 「怎么做」的操作型指导与参考手册**；`lessons/` = 「踩过什么坑」的教训门禁；`standards/` = 「必须遵守」的强制规范。
> 页面内的历史 lessons 链接已同步更新为 guides 路径。


> 本文档是 AntdUI 开发的综合参考手册，聚合了所有专项 lessons 的技术要点、代码示例与踩坑记录，作为一站式查阅入口。各主题的原始权威页仍以单独 lesson 形式存在。

---

## 0. ⭐ 权威源：官方 wiki 全量镜像（2026-10-09 起取代 demo 与反编译）

> **唯一权威 API 源**：`raw/AntdUI/wiki-zh/` —— AntdUI 官方仓库 `doc/wiki/zh` 的**全量镜像（85 篇）**，含 `Control/`（68 个控件）、`Form/`、`Config.md`、`Theme.md`、`UpdateLog.md`（变更历史，判版本行为差异的依据）。
>
> 上游地址 `https://gitee.com/AntdUI/AntdUI/tree/main/doc/wiki`（`en/` 为英文镜像，本项目只取 `zh/`）。
>
> ⛔ **规则（覆盖本页其余全部内容）**：任何 AntdUI 控件的**属性名、事件名、事件参数、方法签名、枚举成员**，一律先在此目录查证，再写代码。
> ⛔ **不再猜、不再反编译 DLL、不再依赖 demo 反推**。此前基于「DLL 已混淆 + demo 未挂事件 + 本机无编译器」而写下的「不可确定 / 用近似替代」结论，**凡与本目录冲突者一律以本目录为准**（已纠正 4 处，见 §0.3）。
> 🔴 **2026-10-10 新增第 4 处**：不是「核实不了」，而是**页内两份文档互相矛盾且都写得像结论** —— `api/DataReviewerPage` 断言「双参 ColumnCheck 表头自带全选」，
> 而本页 §4.2 源码确证「双参表头无全选」；前者据「别处 `SetAutoCheck(false)` ⇒ 反证默认带全选」这一**不成立的推理**据以删掉了功能。
> **教训**：官方文档能证明「属性/事件存在」，**不等于能证明「渲染/默认行为如何」**；后者只能靠单参/双参差异这类**结构性事实**，不能用反证法推。

### 0.1 为什么废弃反编译与 demo 反推

| 途径 | 结论 |
|---|---|
| 扫 `AntdUI.dll` 字节 | ⛔ 该 DLL 已混淆，字符串碎片化，**只能证「有某个名字」，证不出参数与返回类型** |
| `Reflection.Assembly.LoadFrom` | ⛔ 被本机安全策略拦截（报「equivalent to Add-Type」） |
| 自写 ECMA-335 元数据解析器 | ⛔ 实测踩坑未成（流偏移语义、`HeapSizes` 位、行号重读错位） |
| 从 demo 的 `.Designer.cs` 反推 | ⚠️ **只覆盖 demo 用过的属性**，未用的成员一律查不到 ⇒曾误判「`Radio` 事件名不可确定」 |
| **官方 wiki 镜像** | ✅ **属性/事件/方法/枚举成表列出，含类型与默认值** —— 本项目现役唯一权威源 |

### 0.2 已用官方源核实的关键 API（2026-10-09 复核）

以下均为 `raw/AntdUI/wiki-zh/` 原文确证，**可直接使用**：

| 控件 / 主题 | 官方确证结论 | 出处 |
|---|---|---|
| `AntdUI.Radio` | 属性 `Checked` / `AutoCheck`(默认 true) / `Fill` / `Text` / `TextAlign`；**事件只有 `CheckedChanged`** | `Control/Radio.md` |
| `AntdUI.Checkbox` | `Checked` / `CheckState` / `AutoCheck`；**事件 `CheckedChanged`** | `Control/Checkbox.md` |
| `AntdUI.Switch` | `Checked` / `CheckedText` / `UnCheckedText` / `AutoCheck` / `Loading`；**事件 `CheckedChanged`** | `Control/Switch.md` |
| `AntdUI.Slider` | `MinValue`/`MaxValue`/`Value` **全为 `int`**；`ShowValue` / `Dots` / `Marks`；事件 `ValueChanged(int)` / `ValueFormatChanged(int)`。⛔ **官方无坐标换算 API** | `Control/Slider.md` |
| `AntdUI.Table` | ⛔ **无 `CheckAll`、无 `RefreshRows`、无 `GetCoordinate`、无 `ReadOnly`**；刷新入口是 `Refresh()` 与 `Refresh<T>(AntList<T>)` | `Control/Table.md` |
| `Table` 全选 | ⛔ 无 `CheckAll()` 方法；全选 = 表头 `ColumnCheck.Checked`（`bool`）/`CheckState`，变化通知走 **事件 `CheckedOverallChanged(ColumnCheck column, CheckState value)`** | `Table.md` + `TableColumn.md` |
| `Table` 勾选变化 | 事件 **`CheckedChanged(bool value, object? record, int rowIndex, int columnIndex)`** —— 比 `CellClick` 更直接 | `Control/Table.md` |
| `ColumnCheck` | 属性 `Key` / `AutoCheck` / `Checked` / `CheckState`；**方法 `Call(Func<bool,object?,int,int,bool>)` 返回最终选中值** ⇒ **单选互斥的官方正解就是 `Call`**，无需手动遍历清 others | `Control/TableColumn.md` |
| `ColumnRadio` / `ColumnSwitch` | 同继承 `Column`，同样有 `Call` 回调 | `Control/TableColumn.md` |
| `Table.EmptyHeader` | ✅ **`bool`，语义=空数据时是否显示表头**（本页 §4.1 的旧结论被官方确认为正确） | `Control/Table.md` |
| `Table.AutoSizeColumnsMode` | 类型 `ColumnsMode`，**默认 `Auto`**；设`Fill` 使各列按 `Width` 权重拉伸填满 | `Control/Table.md` |
| `Table.EditMode` | 类型 `TEditMode`，**默认 `None`** ⇒ 表格默认只读，与「`Table` 无 `ReadOnly` 属性」一致 | `Control/Table.md` |
| `Table` 数据刷新 | MVVM 官方口径：行模型继承 `NotifyProperty` 或实现 `INotifyPropertyChanged`，`set` 中触发 `OnPropertyChanged(string)`；增删改不刷新则改用 `BindingList<T>` + `Binding(list)` | `Table.md` 末「使用之前的注意事项」 |
| `Table` 大数据量 | 属性 **`VirtualMode`**（仅渲染可见行）；另有 `ToDataTable()` 导出、`CopyData(...)`、`Sort/SortList/SetSortList`、`Filter*` 筛选、`SummaryCustomize` 汇总 | `Control/Table.md` |
| `CellButton` | 继承 `CellLink`；`Type`(`TTypeMini`) / `Shape` / `Ghost` / `ShowArrow` / `IconSvg` / `Radius` —— 本项目 `SystemControlPage` 的轴按钮列写法**与官方一致** | `Control/TableCell.md` |

### 0.3 本轮纠正的 3 处历史错误结论

| # | 旧结论（基于猜测） | 官方源结论 | 处置 |
|---|---|---|---|
| 1 | 「`AntdUI.Radio` 事件名无先例、当前不可确定；需要单选时优先用 Checkbox + 手动互销，别赌 `Radio`」 | **事件名就是 `CheckedChanged`**（`Radio.md` 首行「默认事件：CheckedChanged」） | ⛔ 该免责**撤销**。`MainPage.cs` 五项互斥仍用 `Checkbox + 手动互销`（**功能正确，不改**），但注释里「Radio 事件名不可确定 / 别赌」的理由已失效，**下轮可按官方签名改用 `Radio`**，前提是 VS 编译确认事件委托参数类型（见 §0.4） |
| 2 | 悬停读数因 `GetCoordinate` 不可核实而**自算线性近似** | 官方 `Slider.md` **根本没有坐标换算 API**，只有 `int` 的 `Value`/`MinValue`/`MaxValue` | ✅ 该「近似」**其实是唯一正解**，不是妥协。`DataReviewerPage` 现有自算写法保留，但**理由改写**为「官方无此API，自算不是降级方案」——可正名为设计决策 |
| 3 | 批量勾选因 `CheckAll`/`RefreshRows` 不可核实而**复用 `FillPage()` 重填** | 官方无 `CheckAll`；但有 `Refresh()` / `Refresh<T>(list)` 两个正规刷新入口，全选变化有 `CheckedOverallChanged` 事件 | ⚠️ 现有实现功能无碍；**下轮可改用 `Refresh()` + `CheckedOverallChanged`**，不必再靠 `FillPage()` 重填 |

### 0.4 ⛔⛔ 违规记录：官方 wiki 已就位却仍在反编译 DLL（2026-10-09，业主当面纠正）

业主原话：「**AntdUI 你应该查官方的定义，我给了你使用资源的，你怎么还是分析 DLL**」。

**事实**：这一天里我为「表格着色」「Input 报警行红色」两件事，
**反复扫 `AntdUI.dll` 字节、自写 ECMA-335 元数据解析器、还写了一个半小时的解析脚本**，
而 `raw/AntdUI/wiki-zh/`（85 篇，含 `Control/Input.md`）**早就在库里且已是 §0 明文规定的唯一权威源**。
翻 `Input.md` **一次**就拿到全部答案（见 §4.7）。

> ⛔ **判据（本页最高优先级，违反即返工）**：
> **查 AntdUI API 的动作序列只能是：① 翻 `raw/AntdUI/wiki-zh/Control/<控件名>.md` → ② 仍不确定才查 demo `.Designer.cs` → ③ 两者都没有才允许看 DLL，且看 DLL 只许确认「wiki 没写的委托类型」。**
> ⛔ **任何情况下不得跳过 ① 直接啃 DLL**；**更不得因为「核实不了」就写近似替代或免责注释** ——
> 先证明「wiki 与 demo 都没有」再说核实不了。

**本轮因此产生的两个错误结论（已撤销）**：
| 错误结论 | 官方事实 | 处置 |
|---|---|---|
| 「`AntdUI.Input` 基于 TextBox，不支持 `SelectionColor`（彩色日志），仅追加文本」 | `Input.md` 明列 **`SelectionColor`** 属性 + **`SetStyle(start,length,font,fore,back)`** 方法 + **`AppendText(text, TextOpConfig)`** 重载 | ⛔ 错判已撤销；`MainPage.LogAppend` 改为按行 `SetStyle` 上色，**报警行红色** |
| 「表格字体色只能 `SetRowStyle`+`CellStyleInfo`，且 `ForeColor` 不可核实」 | `TableCell.md` 列出 `CellText` 等**均有 `Fore`（字体颜色）** 字段；`TableColumn.md` 同理 | ⛔ 免责撤销；下轮按官方字段名实现，**不再需要反编译** |

### 0.4b ⛔ 同一违规的第三种形态：**凭空造属性**（业主编译打回）

业主原话：「`int start = inputLog.Text.Length;` 才是正确的，**你的写法又自己猜测了一部分属性**」。

我为取「本行起点」写了 `inputLog.TextLength`。核对 `Input.md` 属性表 ——
**没有 `TextLength`**，只有 `Text`（string）/ `IsTextEmpty` / `TextTotalLine` / `SelectionStart` / `SelectionLength`。
正解是 `inputLog.Text.Length`。
⛔ 且**项目内本就有同型先例**：`FilebackupPage.cs:660` 早就在写
`inputLog.SelectionStart = inputLog.Text.Length;`（同为 `AntdUI.Input`，长期在用）⇒ **连自家既有用法都没查**。

> ⛔ **判据（机械，可拦住整类问题）**：
> **凡第三方控件实例上的成员名，必须在该控件官方文档的属性表/方法表里出现过；
> 没出现 ⇒ 判为「凭空造」，不许写进代码。**
> 落地：把官方 md 用 `\*\*(\w+)\*\*` 抽成集合，与代码里 `控件名\.(\w+)` 做**差集**；
> 差集非空即违规（白名单只许放「基类提供且已实证」的成员，不许放「我以为有的」）。
> 判据细节见 [[lessons/StaticVerifierJudgements]] §4.13。
>
> **为什么单列**：「看起来很合理」的 API 名正因合理，静态校验与肉眼 review 都拦不住 ——
> 只能靠「官方文档集合做差集」这条机械判据。
> 本项目两天内已 **3 次**栽在「自己造 API」上（`SetStyle` 拖到核实后才用、
> `GetCoordinate` 拿来做近似、`TextLength` 直接凭空造），共同点全是「看起来很合理」。

### 0.5b ⚠️ 官方 wiki 也**没有**的一类信息：委托参数的具体 .NET 类型

官方事件表只给出**语义参数名与类型**（如 `CheckedChanged` → `bool value`），**不给出委托的 .NET 类型**（`AntdUI.BoolEventHandler` ? `EventHandler<bool>` ?），也不给`sender` 之外参数是否打包成 `EventArgs`。

⛔ **这类属于「语义判据」，静态校验定不了，只有编译器能定。**本项目现状：
- `FilebackupPage.OnRadioModeChanged(object sender, AntdUI.BoolEventArgs e)` 与 `AntdUI.Checkbox` 的 `CheckedChanged(object, AntdUI.BoolEventArgs)`（`AntdUI.BoolEventHandler`）**在本项目已实证可编译**（多个 `chkXxx` 长期在用）。
- 故 `Radio.CheckedChanged` **大概率同签名**，但**仍须 VS 编译确认**；**不得仅凭本页就断言「Radio 的事件参数是 `BoolEventArgs`」**。

> 记忆判据更新：MEMORY.md §0.9 里「AntdUI 侧只能靠近似、编译期不确定点无法消除」的结论，**仅对「委托参数类型」这一子项成立**；**属性名 / 事件名 / 方法名 / 方法签名 / 枚举成员已可100% 核实**。

### 0.5 用法速查（官方源对照本项目高频控件）

| 我要… | 官方写法 | 本项目现状 |
|---|---|---|
| 单选互斥（表格内） | `new AntdUI.ColumnCheck("Key","标题").SetAutoCheck(false)` + `Call((v,rec,r,c,_)=>...)` 返回最终值 | ✅ 4 处已用 `SetAutoCheck(false)` + `CellClick` 手动互斥（等价，可保留） |
| **并排多个控件** | ⛔ **不可给同级控件都设 `Dock=Fill`**（会叠成同一矩形，只看得见最上层）；正解 **`TableLayoutPanel` + `Controls.Add(ctrl, col, row)`** + `ColumnStyles` 各 `Percent` | ✅ `DataReviewerPage` 2026-10-10 已改（`tlpSelect` 1×3）；项目内 10 个窗体先例（`RecordConfigForm` 等） |
| **表头全选/全取消** | ⛔ **只能用单参 `ColumnCheck("Key")`**（表头才是全选 checkbox）；双参 `(key,title)` 表头是纯文字、**点击无反应** | ✅ `DataReviewerPage` 2026-10-10 改为「双参保留表头文字 + 筛选栏三按钮」，详见 §4.2 ⛔ 反证法警示 |
| 互斥指令组（动作位） | `AntdUI.Radio`，同父容器内**自动互斥**；事件 `CheckedChanged += new AntdUI.BoolEventHandler(h)`，⛔ **不是** `EventHandler`；**仅 `e.Value==true` 时触发**。**2026-11-05 起**：底色用 `Fill` 表达**执行结果**（成功 `ARGB(64,76,175,80)` / 失败 `ARGB(64,244,67,54)` / 未选中·未执行 `Color.Transparent`），⛔ 不再「选中即 `#52C41A`」；`AntdUI.Radio` **无 `Back`**，`BackColor` 带 Alpha 抛 `ArgumentException`（ADR-063 §二/§六） | ✅ `ProcessControlPage` 2026-10-12 起 9 个 Radio 互斥实测生效；2026-11-05 三区（Y/LA/TA）改「确认→执行→Fill 上色→切走复位」 |
| 单选互斥（页面内） | `AntdUI.Radio` + `CheckedChanged` | ⚠️ `FilebackupPage` 已用 `Radio`；`MainPage` 用 `Checkbox` 手动互销 |
| 复选 / 开关 | `Checkbox` / `Switch` + `CheckedChanged` | ✅ `Checkbox.CheckedChanged` 实证可用 |
| 表格列宽填满 | `AutoSizeColumnsMode = AntdUI.ColumnsMode.Fill` | ✅ 9 处已设 |
| 表格数据绑定 | `table.Binding(antList)`，`Columns` 只在代码后置赋值 | ✅ 全库统一 |
| 空表显示表头 | `EmptyHeader = true`（`bool`，不是string） | ✅ `SystemControlPage` 已用 |
| 消息提示 | `AntdUI.Message.warn(owner, "...")`，owner 见 §5.2 | ✅ 全库统一 |
| 模态对话 | `AntdUI.Modal.open(new AntdUI.Modal.Config(owner, title, content, TType.Info))` | ✅ 全库统一 |

---

## 旧章节：控件应用参考 demo（⛔ 2026-10-09 起降级为「次级参考」）

> ⚠️ **下列内容不再是权威源**，仅在官方 wiki 未覆盖处（如 GridPanel.Span 语法细节、Modal 承载 UserControl 的项目约定）作补充参考。
> **任何控件 API 冲突，一律以 `raw/AntdUI/wiki-zh/` 为准。**



## 2. 布局系统

### 2.1 ADR-007：布局容器自由化（解除 GridPanel/FlowPanel 强制使用）

#### 背景

此前的 UI 设计与范式形成了一条**硬约束**：所有 UI 容器"必须使用 `AntdUI.GridPanel`"（大区域分割）与 `AntdUI.FlowPanel`（表单流式排列）。这两类容器存在**强制排序**行为，给布局带来不便：

- `GridPanel` 的子控件按 `Controls.Add` 的**逆序**入格，Designer 中必须把 Add 顺序写成期望格子顺序的倒序，易错且反直觉。
- `FlowPanel` 按 `Controls.Add` **逆序**从左到右流式排列并自动换行（⚠️ 2026-10-09 运行期实证更正：早前「顺序 Add」表述有误，见 §2.x 实证表），无法精确控制每个控件的绝对位置。

用户（2026-08-12）明确要求：**不再强行使用 GridPanel 和 FlowPanel，因为它们会强行排序**。

#### 决策

1. **解除 `GridPanel`/`FlowPanel` 的强制使用约束**，布局容器改为**按需自由选择**。开发时可根据具体布局需求选用 `GridPanel`、`FlowPanel`、`Panel` 绝对定位、`Dock`/`Anchor` 或 WinForms 原生布局容器等任一方式。
2. **保留 AntdUI 整体风格**：项目 UI 主体仍为 AntdUI 风格（框架约束不因本 ADR 改变）。
3. **控件回退规则**：AntdUI 缺失的控件，允许使用 **WinForms 原生控件**作为回退。
4. **SunnyUI 控件一律禁止**使用（GPL 许可约束）。
5. **不重写已有页面**：已用 `GridPanel`/`FlowPanel` 实现的页面功能正常，**不强制重写**。
6. **若仍使用 `GridPanel`/`FlowPanel`**，必须遵守其各自的布局规则（**两者均为逆序**：`GridPanel` 逆序入格、`FlowPanel` 逆序入流，2026-10-09 运行期实证）——这些规则是「使用该容器时的技术知识」，而非「强制使用该容器的理由」。

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

#### 2.x ⭐ `GridPanel.Span` 完整语法（2026-10-09 三源交叉核实）

**权威源顺序**（勿跳过前一级）：
① **官方 demo 自带说明** `M3/AntdUI使用demo/AntdUI-Demo-main/Views/GridPanelDemo.Designer.cs:72`
（控件里`label1.Text` 就是语法说明原文，最可信）
② `raw/AntdUI/wiki-zh/Control/GridPanel.md`
③ DLL `#US` 堆的 `Span fill _N : Vertical` 字面量串（补wiki 未写的关键字）。

##### 语法结构

```
Span = "行1:列宽1 列宽2;行2:列宽1 …;-全局行高1 行高2 …"
       ↑ `-` 前：每行 = 行高:该行列宽列表（空格分列，; 分行）
                `-` 后：全行行高（个数须与行数对应）
```

官方 demo 原文（`GridPanelDemo.Designer.cs:72`，逐字）：

> Span：以-符号分界。-前为列宽属性，列宽以 ; 分组，每一组代表一行。
> -后为行高属性。行高属性个数要与行数对应，每个数之间用空格间隔

##### 关键字（wiki 未写，从 demo + DLL + **2026-10-09 运行期实证**补齐）

| 字面量 | 含义 | 证据 |
|---|---|---|
| `fill` | 该行**单列**填满整行（列位=剩余宽） | demo `FlowPanelDemo`/`PanelDemo`/`MenuDemo` 全部用它作第2 列 |
| `_N` | ⛔ **不可用**（见下）——数字后缀把该格宽打成 1px、运行期 0px；字面 `_N` 置 `IsEmpty=True` | 2026-10-09 `ConvertToRects` + 布局实测 |
| `%` | 百分比 | 官方demo `"50% 50%;20% 80%;150 200;-20% 30% 50%"` |
| 纯数字 | 像素 | 同上（`150 200` 两列） |

⛔ **`_N` 跨行/跨列合并——实证结论「不可用」（2026-10-09 收口）**：
`100%_2`/`100%_3`/`80_3`/`fill_3` 全部把被标记格的宽/高打成 **1px（解析层）/0px（运行层）**，其下各行**不发生合并**；
`100%_N`（字面 N）解析为 `IsEmpty=True` 的占位空格。⇒ **凡需跨行/跨列合并（原 `SetRowSpan`/`SetColumnSpan`），
一律用多层 GridPanel 表达**（外层一格装内层整网格），⛔ 禁写 `_N`。

##### ⚠️ 从 `TableLayoutPanel` 换到 `GridPanel` 的对照表

| TableLayoutPanel | GridPanel 等价 |
|---|---|
| `ColumnCount` / `RowCount` | ⛔ **无此属性** ⇒ 由 `Span` 隐含（数`;` 与空格） |
| `ColumnStyles.Add(SizeType.Absolute/Percent, w)` | 写成 `Span` 里的列宽（`100` 像素 / `50%` 百分比） |
| `RowStyles.Add(SizeType.Absolute/Percent, h)` | 写在每行 `:` 前，或 `-` 后的全局行高表（**两者择一，⛔ 禁混用**） |
| `Controls.Add(ctrl, col, row)` | ⛔ **只接受单参** `Controls.Add(ctrl)` + **逆序入格** |
| `SetRowSpan(ctrl, n)` / `SetColumnSpan(ctrl, n)` | ⛔ 无这两方法且 `_N` 不可用 ⇒ **多层 GridPanel**（合并区拆成子网格） |
| 子控件 `Margin=3`（默认） | 相同；⚠️ **嵌套包装 GridPanel 必须 `Margin=new Padding(0)`**（否则每层叠加 +3 偏移，A/B 实测 M0=零偏差 / M3=偏 +3~6） |

##### ⭐ 运行期实证方法（2026-10-09 建立，取代「无编译器无法核实」）

沙盒无 C# 编译器但有 PowerShell 5.1（.NET 4.8 运行时）⇒ **可直接加载项目 `3rdDepend\AntdUI.dll` 实测布局语义**：

```powershell
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
[void][System.Reflection.Assembly]::LoadFrom("$PWD\AdaWeldSystem\3rdDepend\AntdUI.dll")
# 布局须有真实句柄：屏幕外 Form.Show() 触发（PerformLayout 单独调用不动布局引擎）
# Span 解析层直接读：GridPanel.ConvertToRects(Rectangle, String) → 格子矩形（反射调用）
```

要点：① `Form.Show()` 才会建句柄触发布局（`CreateControl()` 对不可见控件是空操作）；
② `ConvertToRects` 返回 `Rects[]`（含 `x/y/Rect/IsEmpty` backing field），PowerShell 访问成员会因 `X/x` 大小写重名报 CLS 错——
用 `GetField('x').GetValue()` 反射取值；③ **每段探针开新进程跑**（同会话反复建 Form 会间歇性 `New-Object` 返 null）；
④ `FlowPanel.Controls` 就是标准 `Control.ControlCollection`（`Add(Control)`/`Remove(Control)`/`SetChildIndex` 语义如常）；
⑤ `SetIndex(ctrl, n)` 可显式指定格序（与默认逆序矛盾时 SetIndex 获胜），可作 Designer 重排保险。

##### 本项目实证 Span（多层 GridPanel，2026-10-09 修复仪表盘乱排）

```csharp
// DataReviewerPage.uiGridPanelRight（3 行，右侧图表区）
// ⚠️ 2026-11-02：「按 X 范围显示区域」模块整体移除，滑块行并入底行 ⇒ 4 行改 3 行
//    旧：fill;fill;fill;fill 120;-35 fill 35 35
Span = "fill;fill;fill 120;-35 fill 35"

// MainPage 仪表盘：原 TableLayoutPanel(4列×13行+合并) → 5 层 GridPanel（各层 Add 逆序入格）
Span = "fill 20 100"                                                   // 外层 [gridLeftBlock][divider1][gridRightBlock]
// gridLeftBlock:  "fill;133 fill;133 fill;133 fill;133 fill;133 fill;-40 30 30 30 120 120"
// gridRightBlock: "fill;fill;-40 100%"
// gridRobotVals:  "fill;fill;fill;fill;-30 30 30 30"（gridHeadVals 同形）
//   A/B 运行期对照：20/20 控件与原 TableLayoutPanel 几何全等（逐格 rect 零偏差）
```

⚠️ **`Span` 写法错误无编译期保护**（它是 `string` 属性，写错只是布局不对，不会报错）⇒
新增/修改 `Span` 后**必须目视验证**，静态校验只能断言字符串形态（行数 / 列数 / 行高个数 / 关键列宽值）。

##### ⛔ 两个必须自查的坑

1. **子控件数与 Span 格数不匹配**：`Controls.Add` 是**逆序入格**，所以**子控件总数必须等于 Span 展开的格子总数**。
   少一个 ⇒ 最后一格空着（控件挤在前面的格子里）；多一个 ⇒ 多出来的控件直接不显示。
2. **行高机制混用**：`高度:` 每行前缀 与 `-` 全局行高表**只用一种**。2026-10-09 乱排根因之一即两者同时出现
   （`"40:…;30:…;…;-40 30 …"`）——解析行为未定义，⛔ 禁混用。

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

### 3.4 ContextMenuStrip 右键菜单（Table / Panel 等）

#### 背景

WinForms 的 `ContextMenuStrip` 是**组件**，靠 `control.ContextMenuStrip = xxx` 挂接、右键任意位置（含子控件）自动弹出。AntdUI **没有** `Control.ContextMenuStrip` 属性——右键菜单必须用**静态方法** `AntdUI.ContextMenuStrip.open(...)` **编程式弹出**。本项目 `DataReviewerPage` 已落地此模式（2026-09-18）。

#### API（反射确证 · AntdUI 2.4.3.0 / `3rdDepend/AntdUI.dll`）

```csharp
// 静态方法：在 control 上弹出菜单；点击某项回调 call；items 为菜单项数组
public static Form open(
    Control control,
    Action<AntdUI.IContextMenuStrip> call,      // ⛔ 回调载荷是 IContextMenuStrip，不是 IContextMenuStripItem
    AntdUI.IContextMenuStripItem[] items,
    int sleep = 0);

// 重载（带托盘图标）
public static Form open(
    Control control, NotifyIcon notifyIcon,
    Action<AntdUI.IContextMenuStrip> call,
    AntdUI.IContextMenuStripItem[] items, int sleep = 0);

// 重载（配置对象）
public static Form open(AntdUI.ContextMenuStrip.Config config);

// 菜单项（构造：文本, 可选子文本）
new AntdUI.ContextMenuStripItem("显示数据", "Ctrl+N");
new AntdUI.ContextMenuStripItemDivider();            // 分隔线
// 链式：.SetID("id") / .SetIcon("SvgName") / .SetEnabled(false) / .SetChecked(true)
//       /.SetSub(IContextMenuStripItem[]) 子菜单
```

##### ⚠️ 两个接口别搞混（真实编译错误来源）

| 类型 | 角色 | 成员 |
|---|---|---|
| `IContextMenuStrip` | **回调载荷类型** —— `open()` 的 `call` 形参类型 | `ID` / `Text` / `Enabled` / `Icon` / `IconSvg` / `Checked` / `Tag` |
| `IContextMenuStripItem` | **数组元素基类** —— `items` 的元素类型 | 仅 `ParentItem`（**没有** `ID` / `Text`） |

同一个 `ContextMenuStripItem` 实例（继承 `IContextMenuStripItem`、实现 `IContextMenuStrip`）进数组时**当 Item**，回调时**当 Strip 传回**。
⛔ 因此回调形参**必须**声明为 `Action<AntdUI.IContextMenuStrip>` —— 写成 `Action<AntdUI.IContextMenuStripItem>` 会直接编译失败：

| 错误 | 症状 |
|---|---|
| **CS1503** | `无法从 Action<IContextMenuStripItem> 转换为 Action<IContextMenuStrip>` —— `open()` 第二参类型不匹配 |
| **CS1061 ×2** | `'IContextMenuStripItem' 未包含 "ID" 的定义` / `'…未包含 "Text" 的定义'` —— 回调体里读 `it.ID` / `it.Text` 失败 |

✅ 正确写法（回调里访问 `it.ID` / `it.Text`）：

```csharp
private void OnConfigMenuClick(AntdUI.IContextMenuStrip it)   // ⛔ 不是 IContextMenuStripItem
{
    if (it.ID == "Select") SelectConfig();
    else if (it.Text == "删除配置") DeleteConfig();
}
```

> **交叉验证**：官方 wiki 镜像 `raw/AntdUI/wiki-zh/Control/ContextMenuStrip.md` 的 `Call` 一栏写作 `Action<ContextMenuStripItem>`，示例也是 `open(this, it => … it.Text …, menulist)`；**镜像文字与 2.4.3.0 实际反射签名不一致**，实反射为 `Action<IContextMenuStrip>`。以反射为准。

回调里用 `it.ID`（先 `SetID`）或 `it.Text` 区分多项；**单项菜单直接动作即可**。

#### 右键触发（无 ContextMenuStrip 属性，必须手动挂事件）

| 控件 | 触发事件 | 判定 | 说明 |
|------|----------|------|------|
| `AntdUI.Table` | `CellClick`（已有订阅） | `e.Button == MouseButtons.Right`（`TableClickEventArgs` 含 `Button`） | 右键行时 `e.Record` 已为该行，**自动以右键行作为选中行**，比 WinForms 更准；空白处右键不触发 CellClick |
| `AntdUI.Panel` / 其他 `IControl` 派生控件 | `MouseDown` | `e.Button == MouseButtons.Right` | `AntdUI.Panel : IControl(Control 派生)`，MouseDown/MouseUp 可用且会触发（AntdUI issue 实例中 `table.MouseUp +=` 即佐证） |

```csharp
// Table：在既有 CellClick 处理器内
private void uiDataGridView1_CellClick(object sender, AntdUI.TableClickEventArgs e)
{
    _selectedRow = e.Record as DataReviewRow;
    if (e.Button == MouseButtons.Right)
        AntdUI.ContextMenuStrip.open(uiDataGridView1, it => Datashow(),   // it 的类型是 IContextMenuStrip
            new AntdUI.IContextMenuStripItem[] { new AntdUI.ContextMenuStripItem("显示数据") });
}

// Panel：构造函数订阅 + 处理器
panelRight.MouseDown += panelRight_MouseDown;
private void panelRight_MouseDown(object sender, MouseEventArgs e)
{
    if (e.Button == MouseButtons.Right)
        AntdUI.ContextMenuStrip.open(panelRight, it => { },
            new AntdUI.IContextMenuStripItem[] { new AntdUI.ContextMenuStripItem("设置显示区间") });
}

// 多项分派：回调形参声明为 IContextMenuStrip，才能读 it.ID / it.Text
AntdUI.ContextMenuStrip.open(uiDataGridView1, OnConfigMenuClick, new AntdUI.IContextMenuStripItem[]
{
    new AntdUI.ContextMenuStripItem("切换配置").SetID("Select"),
    new AntdUI.ContextMenuStripItem("删除配置").SetID("Delete")
});
private void OnConfigMenuClick(AntdUI.IContextMenuStrip it)
{
    if (it.ID == "Select") SelectConfig();
    else if (it.ID == "Delete") DeleteConfig();
}
```

#### ⚠ 行为差异（与原 WinForms 对比）

- WinForms `Control.ContextMenuStrip` 会向**子控件冒泡**（右键空白/子控件都弹）；AntdUI 编程式 `open()` 只在**订阅事件的那个控件自身**触发。Panel 内嵌套的图表/按钮等子控件被右键时**不会**触发 Panel 的 `MouseDown`（WinForms 鼠标事件不冒泡）。需要完全还原冒泡须递归给各子控件挂 `MouseDown`——通常无必要（子控件菜单多为空实现）。
- **CS0104 命名空间冲突**：文件同时 `using AntdUI;` 与 `using System.Windows.Forms;` 时，`ContextMenuStrip` 两命名空间都有 → 裸写必报二义。**必须全限定 `AntdUI.ContextMenuStrip.open(...)`**（不要用 `var` 也不裸写 `ContextMenuStrip`）。

#### 迁移 Checklist（WinForms ContextMenuStrip → AntdUI）

- [ ] Designer.cs：删 `new System.Windows.Forms.ContextMenuStrip(this.components)` 实例化 + 两个 `ToolStripMenuItem` 字段
- [ ] Designer.cs：删 `xxx.SuspendLayout()` / `xxx.ResumeLayout(false)`（menu 相关）
- [ ] Designer.cs：删 `uiContextMenuStripX.BackColor/Font/...` 外观块 + `Items.AddRange(...)` + `ToolStripMenuItem` 的 `.Text`/`.Click +=` 块
- [ ] Designer.cs：删 `control.ContextMenuStrip = this.uiContextMenuStripX;` 赋值
- [ ] Designer.cs：删字段声明 `private System.Windows.Forms.ContextMenuStrip uiContextMenuStripX;` / `private System.Windows.Forms.ToolStripMenuItem Xxx;`
- [ ] .cs：删原 `ToolStripMenuItem.Click` 处理器方法（`ShowData_Click`/`SetRange_Click` 等）；右键逻辑并入 `CellClick` / `MouseDown` 处理器
- [ ] .resx：删 `<metadata name="uiContextMenuStripX.TrayLocation" ...>` 两条（保持 well-formed）
- [ ] 右键逻辑改用 `AntdUI.ContextMenuStrip.open(...)`（全限定）

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
   - ⚠️ **`EmptyHeader` 是 `bool` 属性，语义为"空数据时是否显示表头"**（默认 false 会隐藏表头），**不是字符串也不可赋 `string.Empty`**——运行态强制空表显示表头须写 `EmptyHeader = true;`（配 `VisibleHeader = true;`）。切勿仅凭"外观属性"归类推断其类型。

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
- **`AntList<T>` 是自定义集合，不暴露泛型 `IEnumerable<T>`**：反射只得到非泛型 `IEnumerable` + 索引器 + `Add/Clear/CopyTo`。⛔ 不能直接喂给 `List<T>` 的 `IEnumerable<T>` 构造器（编译不过）；需要快照或跨线程取行时按索引复制：`for (i = 0; i < antList.Count; i++) list.Add(antList[i]);`（2026-10-30 ADR-078 实测命中，已落 `MonitorCamPage.StartThumbnailLoader`）。
- **行模型属性返回 `ICell` 即渲染富单元格**：`PlaybackRow.Preview` 返回 `AntdUI.CellImage(bitmap, 6) { Size = new Size(96, 54), ImageFit = AntdUI.TFit.Contain }` 即渲染缩略图（未就绪时返回 `new CellText("加载中…")`）；`Table.RowHeight` 须同步设足（如 64）否则图片被裁；异步回填后调 `table.Refresh()`（后台线程须 `BeginInvoke` 封送）。

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
   - 结论：要「表头显示文字 + 无全选」，用**双参** `ColumnCheck("Selected","选取")`；要「表头自带全选框」，只能用**单参**（但表头就没有 title 文字）。

   🔴 **⛔ 反证法在此不成立（2026-10-10 上机实测踩坑，必读）**：
   曾据「本项目 3 处单选场景都显式 `.SetAutoCheck(false)`」**反证**「默认形态带表头全选」，
   据此删掉了 `DataReviewerPage` 的全选/全取消/反选三按钮，改依赖表头 ⇒ **上机表头点击无反应，功能真空**。
   **错在哪**：`AutoCheck` 管的是**单元格点击自动 toggle**，与表头是否渲染全选框是**两个独立机制**，
   单选场景关掉 `AutoCheck` 与「表头有无全选框」无因果关系。
   **正确姿势**：`AutoCheck` 只在「要手动接管勾选逻辑」时才关；**表头有无全选框只看构造函数的单/双参**。
   ⚠️ 官方文档只能证明「表头全选**态**存在」（`TableColumn.md` ColumnCheck 的「全选」分组 `Checked`/`CheckState` + 事件 `CheckedOverallChanged`），
   **不能证明双参会把它渲染出来** —— 别拿事件/属性的存在去推渲染行为。
   ⚠️ **若既想表头文字又想全选，唯一正解是「单参表头全选框 + 页面另建筛选栏三按钮」**（= `DataReviewerPage` 2026-10-10 现行形态）。
   ⚠️ 行模型必须 `AntdUI.NotifyProperty` + `set` 中 `OnPropertyChanged()`（官方 `Table.md:192` 明文要求），
   否则**代码改 `Selected` 而复选框不刷新**；同型先例 `FileTraceForm.cs:213`。

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

### 4.7 ⭐ Input 按行着色：**报警行红色**（2026-10-09 官方源 `Control/Input.md` 确证）

**背景**：原 `MainPage.LogAppend(Color color, string strMsg)` 收到颜色参数却直接丢弃，
注释写「`AntdUI.Input` 基于 TextBox，不支持 `SelectionColor`」—— **该结论是错的**，
官方 `Input.md` 属性表明确列出 **`SelectionColor`（选中颜色）**。

**官方给出的三个可用入口**：

| 入口 | 签名（官方原文） | 用途 |
|---|---|---|
| **按区间上色** ✅ 本处采用 | `SetStyle(int start, int length, Font? font, Color? fore, Color? back)` | **报警行整行变红** |
| 追加带配置 | `AppendText(string text, TextOpConfig config)` | 追加时携带文本配置（`TextOpConfig` 字段 wiki 未公开）|
| 插入带配置 | `InsertText(int startIndex, string text, TextOpConfig config)` | 同上 |

**颜色链已就绪**（`Comm/SystemComm/SystemComm.cs` 的 `ShowLog` 按 `MessageLevel` 映射）：

| MessageLevel | `MessageShowColor` |
|---|---|
| `Info` | `Color.Black` |
| `Warning` | `Color.Blue` |
| **`Error`** | **`Color.Red`** ← 报警行红 |
| `Debug` | `Color.Gray` |
| 通讯日志（`ShowCommunicationLog`）| `Color.DarkGreen` |

**实现要点**（`MainPage.cs`，⛔ 顺序不可颠倒）：

```csharp
int start = inputLog.TextLength;                     // 1. 记下本行起点
string line = string.Format("{0}-{1}\n", ..., strMsg);
inputLog.AppendText(line);                          // 2. 先落地文本（保证日志不丢）
ApplyLineColor(start, line.Length, color);          // 3. 再按区间上色
```

着色是「锦上添花」，文本落地是「必须有」——
`ApplyLineColor` 独立成方法且自带 `try/catch` ⇒ 即使 `SetStyle` 签名与官方不符，
也只是少颜色，**不会连日志一起吞掉**（原实现 `try{}catch{}` 包裹整个方法，一旦抛错整行丢失）。

⚠️ **待实机确认一项**：`SetStyle` 的 `length` 是**闭区间**还是**半开**（wiki 未明示）。
当前按「整行全长」传（宁多不少，多覆盖一个换行符视觉无差别）；确认为半开则减 1。

### 4.8 Input 校验态：`Status`（`TType`）—— 整框变色，别与 4.7 混用

官方 `Input.md` 属性表：**`Status` | 设置校验状态 | `TType` | None**。
demo 实证：`Views/SubView/UserEdit.cs:37-41`（先置 `None`，校验不过置 `Error` + `Message.warn`）、
`Views/InputDemo.cs:39`。Designer 也直接配过：`input15.Status = TType.Warn`、`input12.Status = TType.Success`。

> ⚠️ **与 §4.7 的区别**：`Status` 让**整个输入框**边框/外观变红（表单校验语义）；
> `SetStyle` 只给**指定字符区间**上色（多行只读日志场景）。
> 日志框「只有报警行红」⇒ 用 `SetStyle`；⛔ 不用 `Status`（整框红，与诉求冲突）。

### 4.9 表格按行着色：`SetRowStyle` + `CellStyleInfo`（2026-10-09 实证）

**入口**：`Table.SetRowStyle` 事件 + 返回 `Table.CellStyleInfo`。范式：demo `Views/TableDemo.cs:135`。

```csharp
private AntdUI.Table.CellStyleInfo Table_SetRowStyle(object sender, AntdUI.TableSetRowStyleEventArgs e)
{
    if (e.RowIndex % 2 == 0)
    {
        return new AntdUI.Table.CellStyleInfo
        {
            BackColor = AntdUI.Style.Db.ErrorBg,   // demo 只示范了 BackColor（行底色）
        };
    }
    return null;
}
```

⚠️ demo **只示范了 `BackColor`**。单元格**字体色**的官方途径是
`raw/AntdUI/wiki-zh/Control/TableCell.md` 里各 Cell 类型的 **`Fore`（字体颜色）** 字段
（`CellText` / `CellTag` / `CellBadge` 均标注 `**Fore** | 字体颜色`），列级属性见 `TableColumn.md`
—— ⛔ **不要**再为此反编译 DLL（见 §0.4 违规记录）。

### 4.10 ColumnCheck：单参 vs 双参 ⇒ 表头全选开关（2026-10-09 反证结论）

本项目 **3 处单选场景**（`FileTraceForm.cs:59` / `ILScanForm.cs:84` / `MonitorCamScanForm.cs:85`）
统一写法是：

```csharp
new AntdUI.ColumnCheck("Selected", "选取") { Width = "80" }.SetAutoCheck(false)
// 注释明写：表头无全选，配合 CellClick 实现单选互斥
```

> ⭐ **反证结论**：这三处**必须显式关掉**表头全选 ⇒ **默认形态（不关）就是带表头全选的**。
> 需要「点表头即全选/全取消」时，**双参 + 不调 `SetAutoCheck(false)`** 即可，
> ⛔ 不需要另加「全选 / 全取消」按钮（业主 2026-10-09 口径：表头即可，节省两个按钮）。
> 落地例：`DataReviewerPage.InitTableColumns` 的 `ColumnCheck("Selected", "选取")`。

⚠️ 单参 `ColumnCheck(key)` 与双参的确切差异**无直接实证**，依据是上述反证。
若 VS 上发现表头未出现全选框，改回双参 + 显式 `SetAutoCheck(true)` 即可。

---

## 4.6 Tooltip 跟随提示（2026-10-09 实证）

```csharp
private AntdUI.TooltipComponent _tooltip;   // 单实例，可对多控件反复 SetTip

_tooltip = new AntdUI.TooltipComponent
{
    Font = new System.Drawing.Font("微软雅黑", 9.75F),
    ArrowAlign = AntdUI.TAlign.Top,
};
_tooltip.SetTip(someControl, "提示文本");   // ⛔ 只用两参重载（项目实证形态）
```

- ⛔ **三参带位置的变体 `SetTip(control, text, location)` 未经实证，不要用。**
- `SetTip` 对同一控件**支持原地更新**（重复挂同一控件即刷新文本）。
- 范式来源：`MainPage.InitDeviceSwitchButtons`。
- 用途：图表悬停读数（`DataReviewerPage` 用它在指针靠近数据点时显示该点 X/Y）。

---

## 4.11 ⭐ `Select` 下拉选择器：「安全名单」与属性边界（2026-10-09 实证）

权威源：`raw/AntdUI/wiki-zh/Control/Select.md`（**25 个属性**）+ `DropdownStyles.md`（`SelectItem` 结构）。
范式来源：`FilebackupPage.cs:78`（`Items.Add(string)` + `SelectedIndex`）/ `ProcessControlPage.cs:174`。

**基本形态**（本项目 6 处 `Select` 统一写法）：

```csharp
// 初始化（先赋值再订阅，避免初始化即触发回调）
selXxx.Items.Clear();
selXxx.Items.Add("选项文本");          // 官方 demo 也用 string直传
selXxx.SelectedIndex = 0;
selXxx.SelectedIndexChanged += selXxx_SelectedIndexChanged;   // 签名：(object, AntdUI.IntEventArgs)

// 读选中项
int idx = selXxx.SelectedIndex;         // -1 表示未选
```

### ⭐ 安全名单（本项目 4 处既有 `Select` 实际只用的 9 个属性）

写新 `Select` 时**照抄这几个最安全**，全部有项目实证：

| 属性 | 出处 |
|---|---|
| `Dock` / `Location` / `Name` / `Size` / `TabIndex` / `Font` / `Margin` | WinForms 基类 |
| `MinimumSize` | `cmbJob` / `cmbFps` / `selectRsiCycle` |
| `PlaceholderText` | `cmbJob` / `selFlowEnableGuide` |

### ⛔ 已确认**不存在**的属性（曾因此编译打回）

| 我写的 | 结论 |
|---|---|
| `Select.ShowSearch` | ❌ **不在 `Select.md` 的 25 个属性里，也不在 `Input.md` 的 97 个里** —— 不属于任何 AntdUI 控件，纯属想当然 |

> ⚠️ 本项目**两天内已 4 次**栽在「凭空造 API」上（`GetCoordinate` / `SetStyle` / `TextLength` / `ShowSearch`），
> 共同点全是**「看起来很合理」的 API 名**。判据见 [[lessons/StaticVerifierJudgements]] §4.13。

### ⚠️ 官方有但项目未实证：`DropDownArrow`

`Select.md:21` 明列（默认 `false`）。本项目 4 处 `Select` **无一使用**。
`DataReviewerPage.selSeriesGroup` 首次启用它⇒ **若上机表现异常，删掉这一行即回默认（无箭头）**。

### 事件签名

| 事件 | 委托 | 备注 |
|---|---|---|
| `SelectedIndexChanged` | `(object sender, int index)` | 本项目统一写 `AntdUI.IntEventArgs e` |

⚠️ 官方事件表只给**语义参数**（`int index`），**不给 .NET 委托类型名** ⇒
`IntEventArgs` 是**项目实证**（6 处 Select 全用它），不是文档给的。

### 富样式项`SelectItem`

```csharp
selXxx.Items.AddRange(new object[] {
    new SelectItem("带图标") { IconSvg = "<svg .../>" },
    new SelectItem("禁用")   { Enable = false },
    new SelectItem("子菜单") { Sub = new List<object> { new SelectItem("子项1") } },
    new DividerSelectItem(),// 分割线
});
```
来源：`AntdUIDemo/Views/SelectDemo.cs:18`。⛔ `SelectItem` 的 `Text` / `Tag` 是**必填**。

---

## 5. 对话框与消息

### 5.1 Modal 承载 UserControl（对话窗范式）

#### 背景

AntdUI **不**推荐为每个对话窗新开 `AntdUI.Window`，而是把对话内容做成 `UserControl`，用 `AntdUI.Modal.open` 承载。本范式由 ADR-034 采纳，取代旧的 `Window+PageHeader` 范式。

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
using (var form = new UserEditForm())
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

> ⚠️ **本文已废弃**：2026-07-30 经 ADR-034 采纳 AntdUI 官方 Demo 范式——对话窗改为 **Modal 承载的 `UserControl`**（取消 PageHeader），本「Window + PageHeader」方案被取代。保留作历史参考。

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
| `MenuItem` | `AntdUI.MenuItem`（`.Text`/`.Tag`，用于 `Menu.Add`） | `System.Windows.Forms.MenuItem`（旧 WinForms 菜单项） | ImagePage.cs（现役 `UIDesign/TabPage/MonitorCamPage.cs`）、ParamPage.cs（现役 `UIDesign/TabPage/ProcessControlPage.cs`） |

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
| 15 | WinForms `ContextMenuStrip` 组件 → AntdUI 静态 `open()` | 右键菜单不弹 / CS0104 二义 | 删 Designer 内 WinForms `ContextMenuStrip` 组件（实例化/`Suspend`/`Resume`/`Items`/`ToolStripMenuItem`/`.ContextMenuStrip=`/字段），resx 删 `TrayLocation`；改 `AntdUI.ContextMenuStrip.open(ctrl, cb, items[])`（**全限定**避 CS0104）；右键触发：Table 用 `CellClick` 的 `e.Button==MouseButtons.Right`，Panel 等用 `MouseDown` 的 `e.Button==MouseButtons.Right`（详见 §3.4） |
| 16 | `open()` 回调载荷是 `IContextMenuStrip`，不是 `IContextMenuStripItem` | **CS1503**（`Action<IContextMenuStripItem>` 无法转 `Action<IContextMenuStrip>`）+ **CS1061 ×2**（`it.ID` / `it.Text` 未定义） | 回调形参声明 `Action<AntdUI.IContextMenuStrip>`；`IContextMenuStripItem` 只是数组元素基类，仅有 `ParentItem`（详见 §3.4） |

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
_ilPage = new ILAlgoForm(_ilCamera);
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
- 把 `AntdUI.ContextMenuStrip.open()` 的回调形参声明成 `IContextMenuStripItem`（必须是 `IContextMenuStrip`，否则 CS1503 + CS1061 ×2）。

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
4. `decisions/ADR-010-LayoutContainerFreedom.md` — 布局容器自由化决策（第 2.1 节）
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

