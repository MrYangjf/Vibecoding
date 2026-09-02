---
title: SunnyUI 历史归档
date: 2026-07-28
tags: [归档, UI, SunnyUI, 历史参考, 迁移]
status: archived
superseded_by: decisions/ADR-021-UIFrameworkMigration
---

# SunnyUI 历史归档文档

> **本文档是 SunnyUI UI 框架的历史归档，仅供历史参考。**
>
> **归属变更（2026-09-01）**：`archive/` 分类已取消（与 `architecture/` 同是全库最小分类且名字易混），本页迁入 `project/`。内容未变，仅位置变更。
>
> AdaWeldSystem 项目已于 **2026-07-28** 完成 UI 框架从 SunnyUI 到 AntdUI 的全面迁移（详见 [[decisions/ADR-021-UIFrameworkMigration]]）。迁移后项目使用 **AntdUI**（MIT 许可），SunnyUI（GPL v3 许可）相关代码已全部移除。本文档汇总了 SunnyUI 时期的设计决策、迁移教训与完成状态，留作技术追溯之用。
>
> - 当前生效框架：**AntdUI** + **ScottPlot.FormsPlot 4.1.74**（图表）
> - 迁移决策：[[decisions/ADR-021-UIFrameworkMigration]]
> - 迁移追踪：[[guides/AntdUI-Reference]]

---

## 1. 迁移总览

### 1.1 迁移背景（来自 ADR-021）

AdaWeldSystem 项目 UI 层原使用 **SunnyUI** 框架（GPL v3 许可）。因商业原因，GPL v3 许可对商业化产品有限制。**AntdUI** 采用 MIT 许可证，商业政策更宽松，适合产品级部署。

### 1.2 迁移决策（来自 ADR-021）

将项目 UI 框架从 SunnyUI 迁移至 AntdUI，分五个阶段进行：

| 阶段 | 内容 |
|------|------|
| 阶段 1 | 基础控件替换（Button / Input / Label / CheckBox / ComboBox 等） |
| 阶段 2 | 导航框架重构（UINavBar + UINavMenu + UITabControl → Menu + Tabs） |
| 阶段 3 | 数据表格迁移（UIDataGridView + DataTable → Table + AntList\<T\>） |
| 阶段 4 | 图表控件集成（UILineChart / UIDoughnutChart → ScottPlot.FormsPlot 4.1.74） |
| 阶段 5 | 主题与样式微调 |

> **图表方案变更历史**：阶段 4 起初选用 `AntdUI.Chart`，2026-08-12 用户在 MainPage 实装后改选 `ScottPlot.FormsPlot`（更轻量、高性能、实时动态数据可视化更优）；2026-08-13 升级 5.1.59 后回退 4.1.74（5.x 基于 SkiaSharp 对 .NET 4.8 设计器不友好）。

### 1.3 备选方案对比（来自 ADR-021）

| 方案 | 优点 | 缺点 | 是否采用 |
|------|------|------|---------|
| 迁移至 AntdUI（MIT 许可） | 免费商用、Ant Design 设计语言、社区活跃 | 部分控件无直接替代（图表/工业控件） | **采用** |
| 购买 SunnyUI 商业许可 | 零迁移成本、已有 ~280 个控件实例 | 持续付费、GPL v3 争议风险 | 不采用 |
| 使用标准 WinForms 控件 | 零依赖、完全自由 | 视觉效果差、开发效率低 | 不采用 |

### 1.4 迁移后果（来自 ADR-021）

**正面：**
- MIT 许可消除商业化法律风险
- AntdUI 设计语言更现代化
- SVG 图标系统更灵活
- 亮暗主题切换更便捷

**负面：**
- ~280 个控件实例需逐一迁移
- UILight / UILedBulb 等工业控件需用 AntdUI.Signal 替代（功能有差异）
- UIDataGridView 基于 DataTable，AntdUI Table 基于 AntList\<T\>，数据层需调整
- Designer.cs 文件需全部重新生成（AntdUI 控件命名空间不同）

### 1.5 关键约束（来自 ADR-021）

迁移后仍须遵守：
- [[decisions/ADR-001-DisposePattern]]（DisposeComponents 模式）
- [[guides/WinForms-Designer]]（Designer.cs 不手动修改）
- [[guides/WinForms-UI-Threading]]（Workflow 事件 InvokeRequired）
- 主题系统改用 AntdUI `Config.IsLight`（取代 SunnyUI `UIStyles.SetStyle`）

---

## 2. 已废弃的 SunnyUI 设计决策

> 以下决策均已被 ADR-021 取代，仅作**历史参考**。

### 2.1 ADR-006：UILight 属性规范（已废弃）

**状态：deprecated** — 原始文档已合并入本页（ADR-006 独立页已删除）

UILight 控件已随 UI 框架迁移由 **AntdUI.Signal** 替代（见 ADR-021 负面后果）。以下 UILight 三要素用法仅作历史参考。

#### 背景（历史参考）

SunnyUI 的 UILight 控件没有 Enabled 和 Blink 属性，但开发者误用这两个不存在的属性，导致编译错误或运行时异常。

#### 决策（历史参考）

UILight 控件必须使用 **三要素** 控制：

```csharp
uiLight.OffColor = Color.FromArgb(180, 180, 180);  // 灰暗 = 未连接
uiLight.OnColor = Color.LimeGreen;                  // 绿色 = 正常
uiLight.State = UILightState.Off;                   // 初始状态
```

#### 状态映射（历史参考）

| Workflow 状态 | UILight 状态 | 视觉 |
|-------------|-------------|------|
| Uninitialized / ErrorAborted | Off | 灰暗 |
| Initializing | On | 绿色 |
| Standby / Completed / ManualStopped | On | 绿色 |
| Starting / Acquiring / Analyzing / Adjusting | Blink | 绿色闪烁 |

#### 禁止项（历史参考）

- 禁止使用 `Enabled = true/false`
- 禁止使用 `Blink = true/false`
- 必须使用 `State = UILightState.Off / On / Blink`

---

### 2.2 ADR-009：全局 UI 风格统一为 Purple（已废弃）

**状态：deprecated** — 原始文档已合并入本页（ADR-009 独立页已删除）

全局 UI 框架已迁移至 AntdUI，主题系统改用 `AntdUI.Config.IsLight`（而非 SunnyUI `UIStyles.SetStyle(UIStyle.Purple)`）。以下 Purple 主题设定仅作历史参考。

#### 背景（历史参考）

FormMain 中通过 `UIStyles.SetStyle(UIStyle.Purple)` 设置主界面风格为 Purple。但存在以下问题导致部分 SunnyUI 控件未跟随 Purple 主题：

1. **设置时机过晚**：`UIStyles.SetStyle(UIStyle.Purple)` 原本在构造函数末尾调用（所有子页面创建之后），导致先于设置创建的页面控件可能未正确继承 Purple 主题。
2. **Designer.cs 中显式 Style 覆盖**：`FormMain.Designer.cs` 中 `uiHeaderButton6.Style = UIStyle.Custom` 和 `uiTabControl1.Style = UIStyle.Custom`，显式覆盖了全局风格，导致这两个控件不跟随 Purple。
3. **运行时显式 Style 覆盖**：`AutoParamForm.cs` 中 `uiDataGridView1.Style = UIStyle.Gray`，强制使用 Gray 风格，与全局 Purple 不一致。

#### 决策内容（历史参考）

**1. 全局风格设置时机**

`UIStyles.SetStyle(UIStyle.Purple)` 必须在**创建任何子页面/控件之前**调用，确保所有后续创建的 SunnyUI 控件自动继承 Purple 主题。

```csharp
public FormMain()
{
    InitializeComponent();

    if (LicenseManager.UsageMode == LicenseUsageMode.Designtime)
        return;

    // 全局风格必须在创建子页面之前设置
    UIStyles.SetStyle(UIStyle.Purple);

    // 覆盖 Designer.cs 中显式设置的 Custom 风格
    uiHeaderButton6.Style = UIStyle.Inherit;
    uiTabControl1.Style = UIStyle.Inherit;

    mainPage = new MainPage();
    // ... 后续页面创建 ...
}
```

**2. Designer.cs 中 Custom 风格的运行时覆盖**

不修改 Designer.cs（遵守 [[guides/WinForms-Designer]]），而是在 `.cs` 文件中将显式设置为 `UIStyle.Custom` 的控件重新设为 `UIStyle.Inherit`，使其继承全局 Purple 主题。

**3. 禁止运行时显式 Style 覆盖**

除非有明确的视觉需求，禁止在 `.cs` 文件中为 SunnyUI 控件设置 `Style = UIStyle.Gray`、`UIStyle.Blue` 等非 Inherit 值。所有 SunnyUI 控件应继承全局 Purple 主题。

**4. 非 SunnyUI 控件不强制应用 Purple**

标准 WinForms 控件（如 `MenuStrip`、`ToolStripMenuItem`、`TreeView`、`PropertyGrid`）不参与 SunnyUI 样式系统，无需强制应用 Purple 风格。

#### 适用范围（历史参考）

| 控件类型 | 是否应用 Purple | 说明 |
|---------|----------------|------|
| Sunny.UI.UIButton / UISymbolButton | 是 | 继承全局主题 |
| Sunny.UI.UITabControl / UINavBar | 是 | 继承全局主题 |
| Sunny.UI.UIDataGridView | 是 | 继承全局主题，禁止 Gray 覆盖 |
| Sunny.UI.UIPage / UIForm2 | 是 | 继承全局主题 |
| 标准 WinForms MenuStrip / ToolStripMenuItem | 否 | 非 SunnyUI 控件 |
| 标准 WinForms TreeView / PropertyGrid | 否 | 非 SunnyUI 控件 |

---

## 3. SunnyUI → AntdUI 迁移教训汇总

> 以下内容汇总了 SunnyUI 迁移到 AntdUI 过程中沉淀的核心教训，涵盖消息框、表格、工具栏、输入框等关键场景。

### 3.1 MessageBox / 消息对话框迁移

**来源**：本页 §3 迁移教训汇总（原独立文档已合并）

SunnyUI 的 `UIMessageBox.ShowError / ShowWarning / ShowInfo / ShowSuccess / Show(...)` 在 AntdUI 中**不存在**，编译报 CS0103。

#### 替代方案对照

| SunnyUI | AntdUI 替代 | 形态 |
|---------|------------|------|
| `UIMessageBox.ShowError(msg)` | `AntdUI.Modal.open(new AntdUI.Modal.Config(owner, "错误", msg) { Icon = TType.Error, Draggable = true })` | **模态对话框**（阻塞，支持拖拽） |
| `UIMessageBox.ShowWarning(msg)` | `AntdUI.Modal.open(new AntdUI.Modal.Config(owner, "警告", msg) { Icon = TType.Warn, Draggable = true })` | 同上 |
| 轻量提示（自动消失） | `AntdUI.Message.error(owner, msg)` / `AntdUI.Message.warn(owner, msg)` / `AntdUI.Message.info` / `AntdUI.Message.success` | **非模态 Toast**，不阻塞 |

#### 关键 API

```csharp
// 模态对话框（可拖拽）
AntdUI.Modal.open(new AntdUI.Modal.Config(owner, "标题", "内容")
{
    Icon = TType.Info,
    Padding = new Size(24, 20),
    Draggable = true,
    CloseIcon = true,
});

// 轻量 Toast（非模态，owner 可为 null）
AntdUI.Message.error(owner, "出错了");
```

#### 易错点

1. **owner 类型实为 `AntdUI.Target`，隐式转换规则易踩坑**：
   - 顶层窗口类（`AntdUI.Window` / `Form`）内可用 `this`
   - `UserControl` 内不可用 `this`，须传 `null` 或 `System.Windows.Forms.Form.ActiveForm`
   - 非 UI 类用 `Form.ActiveForm` 或 `null`
2. **迁移后必须移除 `using Sunny.UI;`**：否则残留 using 虽不报错，但违背迁移目标
3. **不要臆测 `Draggable` 之外的属性**：以官方 Demo 为准

---

### 3.2 数据表格选型：AntdUI.Table（不用 DataGridView）

**来源**：[[guides/AntdUI-Reference]]（SunnyUI 迁移背景部分）

迁移追踪表曾建议「按用户标准 .NET 4.8 取向统一为 `System.Windows.Forms.DataGridView`」。**用户明确否决：「不要用 DataGridView」，统一为 AntdUI.Table。**

#### 决策

本项目所有数据表格一律使用 **AntdUI.Table**（配合 `AntdUI.AntList<T>`），不使用 `System.Windows.Forms.DataGridView`（也不使用 SunnyUI `UIDataGridView`）。

#### 权威用法

- **列定义**：`table.Columns = new AntdUI.ColumnCollection(){ ... }`
  - `Columns` 的赋值必须放在 `.cs` 代码后置（构造函数 `InitializeComponent()` 之后），**不可写进 `*.Designer.cs`**
  - `DataSource` 同样不可写进 Designer.cs（`[Browsable(false)]`，设计器序列化 `AntList<T>` 报错）
- **模型类**：普通 POCO 即可（由 `AntdUI.AntList<T>` 承载增删通知）
- **绑定**：统一用 `table.Binding(antList)`（官方动态加载入口）
- **选中行**：AntdUI.Table **无 `SelectedItem` 属性**，必须用 `CellClick` 事件 + `e.Record as TRow` 取选中行

#### 注意事项

- AntdUI **无内置分页控件**：原 `UIPagination` 用占位 `Panel` + `// TODO` 替代，分页逻辑待补

---

### 3.3 ToolStrip 工具栏迁移：FlowPanel + Label + Button

**来源**：[[guides/AntdUI-Reference]]（SunnyUI 迁移背景部分）

WinForms 的 `ToolStrip` 控件族在 **AntdUI 中不存在对应控件**。ADR-021 要求 UI 全量迁移到 AntdUI，头部栏/工具栏不能再使用 `ToolStrip`。

#### 对照关系

| 原 WinForms / SunnyUI | AntdUI 等价 | 说明 |
|---|---|---|
| `ToolStrip toolStrip1` | `AntdUI.FlowPanel flowPanel1` | `Dock=Top`，子控件按 `Controls.Add` 顺序从左到右排列 |
| `ToolStripLabel` | `AntdUI.Label` | 设 `Text` / `Font` / `Size` |
| `ToolStripSeparator` | 删除 | FlowPanel 用间距或弹性占位即可 |
| `ToolStripButton` | `AntdUI.Button` | Click 为标准 `System.EventHandler` |

#### 右对齐技巧

在 FlowPanel 的 `Controls.Add` 顺序中，把按钮放在最后，并在它**前面**放一个弹性占位 `AntdUI.Label`（`lblSpacer`），设 `Dock = DockStyle.Fill`、`Text = ""`（空）。该占位撑满剩余宽度，把后续按钮推到右侧边缘。

```csharp
this.flowPanel1.Controls.Add(this.labelK);
this.flowPanel1.Controls.Add(this.LabelJ);
this.flowPanel1.Controls.Add(this.labelM);
this.flowPanel1.Controls.Add(this.lblSpacer);   // Dock=Fill 弹性占位
this.flowPanel1.Controls.Add(this.btnSave);     // 被推到右侧
```

#### 禁止行为

- 禁止在 AntdUI 工程里继续 `new System.Windows.Forms.ToolStrip()`
- 禁止给 `ToolStripButton` 用 `Alignment = ToolStripItemAlignment.Right`（AntdUI 无此属性）
- 禁止误以为 `AntdUI.Button.Click` 是 AntdUI 自定义委托（它是标准 `System.EventHandler`）

---

### 3.4 输入对话框迁移：VisualBasic.InputBox → AntdUI Modal + Input

**来源**：[[guides/AntdUI-Reference]]（SunnyUI 迁移背景部分）

`Microsoft.VisualBasic.Interaction.InputBox(...)` 依赖 `Microsoft.VisualBasic` 程序集。SunnyUI→AntdUI 迁移后若项目未引用该程序集，编译报 CS0234。AntdUI 体系下应统一用 `AntdUI.Modal` + `AntdUI.Input`。

#### 正确写法

```csharp
private bool ShowInputStringDialog(ref string value, string prompt)
{
    AntdUI.Input inputBox = new AntdUI.Input
    {
        Text = value ?? "",
        Height = 40,
        Width = 300,
        Location = new System.Drawing.Point(0, 0),
    };

    string result = value ?? "";
    var config = new AntdUI.Modal.Config(
        this.FindForm() ?? System.Windows.Forms.Form.ActiveForm,
        prompt, inputBox, AntdUI.TType.Info)
    {
        OkText = "确认",
        CancelText = "取消",
        Width = 320,
        OnOk = cfg =>
        {
            if (string.IsNullOrWhiteSpace(inputBox.Text))
                return false;
            result = inputBox.Text;
            return true;
        }
    };
    if (AntdUI.Modal.open(config) == System.Windows.Forms.DialogResult.OK && !string.IsNullOrEmpty(result))
    {
        value = result;
        return true;
    }
    return false;
}
```

#### 关键要点

- **裸 `AntdUI.Input` 默认 `Size={0,0}`**，必须显式设置 `Height`（如 40）与 `Width`（如 300）才能显示
- `Modal.Config` 支持 4 参构造 `(owner, title, Control 内容体, TType)`，第三参可传任意 `Control`
- `config.Width` 须大于 `Input.Width`，否则输入框右侧被截断
- `OnOk` 返回 `false` 可阻止关闭（做非空校验）
- `Modal.open` 阻塞 UI 线程，必须在 UI 线程调用

---

## 4. 迁移状态追踪

**来源**：[[guides/AntdUI-Reference]] + [[decisions/ADR-021-UIFrameworkMigration]]

### 4.1 总体完成状态（2026-07-28 确认）

**25/25 UI 文件全部完成从 SunnyUI → AntdUI 迁移**（Designer.cs + .cs 代码后置）。

全量 Grep 确认清零项：

| 检查项 | 结果 | 说明 |
|--------|------|------|
| `using Sunny.UI;` | 0 命中 | 所有 .cs 文件 |
| `private Sunny.UI` / `new Sunny.UI` | 0 命中 | 所有 .Designer.cs 文件 |
| `UIMessageBox`（代码） | 0 命中 | 仅注释残留 |
| `System.Windows.Forms.DataGridView` | 0 命中 | 全部替换为 `AntdUI.Table` + `AntList<T>` |

### 4.2 迁移缺口 / 待验证项（历史快照）

以下为迁移完成时的待办清单快照（截至 2026-07-31）：

| 项 | 状态 | 说明 |
|----|------|------|
| Chart 数据绑定 API（`ChartDataset` / `AddPoint` / `AddDataset` / `RefreshChart`） | 🟡 待验证 | MainPage / DataReview 已按真实 API 实装，待 VS x64 确认项目 AntdUI.dll 版本含这些成员 |
| DataReview X 轴缩放（`SetRange` 替代方案） | 🟡 待验证 | 待 VS 验证 `XMin` / `XMax` 赋值 + `RefreshChart` 方案 |
| EmguALG 调用层迁移（PipelineManager 桥接 → `SeamRecognitionAlgorithm.Instance`） | 🟡 待迁移 | 见 [[modules/EmguALG]]「过渡桥接」 |
| 变量命名遗留（`uiDataGridView1` 实为 `AntdUI.Table` 等） | 🟢 功能无碍 | 仅命名习惯，建议后续清理 |

### 4.3 迁移坑索引（已沉淀为 lessons）

| 教训文档 | 内容 |
|---------|------|
| [[guides/AntdUI-Reference]] | 控件 API 差异总集 |
| [[guides/AntdUI-Reference]] | Table 设计器序列化 |
| [[guides/AntdUI-Reference]] | GridPanel.Span 语法 |
| [[guides/AntdUI-Reference]] | Message / Modal owner 类型 |
| 本页 §3.1 | MessageBox 替代 |
| [[guides/AntdUI-Reference]] | InputBox 替代 |
| [[guides/AntdUI-Reference]] | Menu / Tabs 导航 |
| [[guides/AntdUI-Reference]] | 命名空间遮蔽 |
| [[guides/AntdUI-Reference]] | 表格选型决策 |
| [[guides/WinForms-Designer]] | resx 孤儿类型引用 |
| [[guides/AntdUI-Reference]] | ToolStrip 替代 |
| [[guides/AntdUI-Reference]] | 对话窗 Modal 承载 |
| [[decisions/ADR-022-DialogWindowToModalUserControl]] | 对话窗承载方式决策 |

---

## 相关原始文档

以下是本归档文档的信息来源，原始文档仍保留在 wiki 中：

- [[decisions/ADR-021-UIFrameworkMigration]] — UI 框架迁移决策
- 本页 §2.1 — UILight 属性规范（已废弃，ADR-006）
- 本页 §2.2 — Purple 主题决策（已废弃，ADR-009）
- [[guides/AntdUI-Reference]] — 迁移追踪表
- 本页 §3.1 — MessageBox 迁移
- [[guides/AntdUI-Reference]] — 表格选型
- [[guides/AntdUI-Reference]] — ToolStrip 迁移
- [[guides/AntdUI-Reference]] — InputBox 迁移

---

*归档整理日期：2026-07-28 | 文档状态：archived（历史参考）*
