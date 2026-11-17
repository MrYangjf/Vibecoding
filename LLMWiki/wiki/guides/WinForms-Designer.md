---
title: WinForms 设计器开发规范与常见错误
date: 2026-08-18
tags: [指导, UI, WinForms, 设计器, 汇总]
---

# WinForms 设计器开发规范与常见错误

> **位置说明（2026-09-01）**：本页自 `wiki/lessons/` 迁入 `wiki/guides/`。
> 分类判据：**`guides/` = 「怎么做」的操作型指导与参考手册**；`lessons/` = 「踩过什么坑」的教训门禁；`standards/` = 「必须遵守」的强制规范。
> 页面内的历史 lessons 链接已同步更新为 guides 路径。


本文汇总 WinForms 设计器开发过程中的核心规范与高频错误模式，涵盖 `*.Designer.cs` 不可修改原则、控件实例化顺序、resx 孤儿类型引用、设计器模式单例陷阱四大主题。每节均包含错误现象、根因分析与修复方案，作为设计器相关问题的统一参考。

---

## 1. Designer.cs 不可修改原则

> 来源：DesignerCs-Immutable

### 1.1 错误现象

手动修改 `*.Designer.cs` 文件中的 `Dispose(bool)` 方法或在 `InitializeComponent()` 中加入 `for`/`while`/`if` 等流程控制语句后，WinForms 设计器报错，必须回滚修改才能恢复可视化编辑。

### 1.2 根因分析

`*.Designer.cs` 是 Visual Studio 设计器的自动生成文件，其代码结构有严格约定：

- `Dispose(bool)` 方法由设计器维护，手工修改会破坏设计器的序列化/反序列化逻辑
- `InitializeComponent()` 必须保持"声明式"风格，设计器无法解析流程控制语句，遇到 `if`/`for`/`while` 等会直接报错

### 1.3 修复方案

**自定义资源释放：** 在 `.cs` 文件中定义 `DisposeComponents()` 公共方法，由父页面关闭时调用。不要在 `.cs` 中重写 `Dispose(bool)`：

```csharp
public void DisposeComponents()
{
    _viewer?.Dispose();
    // 释放其他自定义 IDisposable 资源
}
```

> **⚠️ 适用范围澄清（2026-08-19，见 [[decisions/ADR-002-DisposePatternFullCoverage]]）**：
> - `DisposeComponents()` **仅限 UI 设计器类**（Form / UserControl）使用
> - **非 UI 类（后端类）禁止编写 `DisposeComponents()`**，必须实现标准 `IDisposable.Dispose()` 并正确释放资源
> - **UI 类也非必需**：仅当持有「外部嵌套控件/独立资源」（代码 new 的非容器控件、单例/静态事件订阅、外部对象生命周期）时才写；无嵌套/无独立资源则不需要
> - **禁止**修改 Designer.cs 的 `Dispose(bool)` 释放外部资源；**禁止**用 finalizer 退订事件（事件源持引用时 finalizer 永不执行）
> - 已发现并迁移的非 UI 类误用：Workflow ×4、ZMotion ×4、Comm ×4（TCPIPComm 族），见 ADR-027 落地清单
> - 已修复的 UI 类问题（2026-08-19 第二轮）：HelixRenderForm（还原被改的 Designer.cs + 补 DisposeComponents）、MainPage（移除无效 finalizer + 补 DisposeComponents）、FilebackupPage/MonitorCamPage/MotionControlPage/FormMain（补 HandleDestroyed/FormClosed 退订链）
> - 自审命令补充：`grep -rn "DisposeComponents" --include="*.cs" AdaWeldSystem/` 中，非 UIDesign/ 目录下不得出现 `DisposeComponents` 定义；`grep -rn "protected override void Dispose" --include="*.Designer.cs"` 应为标准生成代码（无 `_viewer`/`elementHost` 等业务资源注入）

**动态逻辑：** 所有条件判断、循环等流程控制逻辑必须放在 `.cs` 文件的构造函数或 `Load` 事件中，绝不能写入 `InitializeComponent()`。

### 1.4 禁止行为

- 禁止在 Designer.cs 中修改 Dispose 方法
- **禁止在 UI 类的 `.cs` 文件中重写 `Dispose(bool)` 方法**（会与设计器冲突）
- **禁止非 UI 类编写 `DisposeComponents()`**（非 UI 类必须用标准 `IDisposable.Dispose()`，见 [[decisions/ADR-002-DisposePatternFullCoverage]]）
- 禁止在 InitializeComponent 中使用 for/while/if 等流程控制语句

### 1.5 自审命令

```bash
grep -rn "protected override void Dispose" --include="*.cs" AdaWeldSystem/UIDesign
grep -rn "DisposeComponents" --include="*.cs" AdaWeldSystem/ | grep -v UIDesign/
```

- Designer.cs 中的 Dispose 必须是 Visual Studio 生成的标准代码
- UI 类 `.cs` 文件中不得出现 `Dispose(bool)` 重写
- 非 UIDesign/ 目录（非 UI 类）中不得出现 `DisposeComponents` 定义

---

## 2. 控件实例化顺序

> 来源：DesignerCs-ControlInstantiation

WinForms `Designer.cs` 的 `InitializeComponent()` 必须严格遵守 **"先实例化，后使用"** 的顺序：
1. 所有控件字段在方法开头通过 `new` 集中实例化
2. 随后设置属性、事件绑定
3. 最后加入父容器的 `Controls` 集合

手工修改 Designer.cs 时，最常见的错误是只复制了 `Controls.Add` 和属性配置段落，却遗漏了开头的 `new` 语句。以下是四种变体错误模式。

### 2.1 变体一：字段未声明 → 编译错误

**错误现象：** 在 `InitializeComponent()` 中手工添加了控件引用（如 `this.grpServer.Controls.Add(this.chkShowCommLog);`），但在方法开头缺少对应的实例化语句，也没有字段声明，导致编译错误：

```
变量"chkShowCommLog"未声明或从未赋值。
```

**根因：** 字段既未声明也未实例化，编译器无法识别。

**修复方案：** 在 `InitializeComponent()` 顶部添加实例化语句，并在类底部添加字段声明：

```csharp
private void InitializeComponent()
{
    // 1. 集中实例化所有控件
    this.tlpMain = new System.Windows.Forms.TableLayoutPanel();
    this.grpServer = new System.Windows.Forms.GroupBox();
    this.chkShowCommLog = new AntdUI.Checkbox();  // ← 必须有

    // 2. 配置属性、事件
    // ...

    // 3. 组装到容器
    this.grpServer.Controls.Add(this.chkShowCommLog);
}
```

### 2.2 变体二：new 晚于 AddRange → 运行时 ArgumentNullException

**错误现象：** 手工向状态栏新增 `ToolStripItem` 时，把多个 `ToolStripItem` 的 `new` 实例化写在了属性配置块里，而该块位于 `toolStrip1.Items.AddRange(...)` 之后。编译通过，但运行时抛出异常：

```
System.ArgumentNullException：值不能为 null。Parameter name: value
   at System.Windows.Forms.ToolStripItemCollection.AddRange(ToolStripItem[] toolStripItems)
```

**根因：** `InitializeComponent()` 自上而下执行，`AddRange` 运行时这些字段仍为 `null`。字段已声明且已 `new`，只是 `new` 的位置晚于使用点。

**修复方案：** 所有 `this.xxx = new ...()` 集中放在 `InitializeComponent()` 顶部（`SuspendLayout()` / `AddRange` 之前，按 AddRange 顺序排列）；随后每个控件用 `// 控件名` 注释头 + 纯属性配置（不含 `new`）。

### 2.3 变体三：字段已声明但无 new → 设计器"未知名称"错误

**错误现象：** `ToolStripItem` 被引用于 `Items.AddRange` 但未在方法顶部声明实例化（类底部有 `private` 字段声明），WinForms 设计器报错：

```
设计器无法处理第 37 行的未知名称"toolStripLabel2"。
方法"InitializeComponent"中的代码由设计器生成，不应手动修改。
```

此变体**编译可能通过**（如果字段在类底部有 `private` 声明），但 **VS 设计器无法解析**，导致无法可视化编辑。

**根因：** `toolStripLabel2` 的 `new` 实例化语句缺失或位置不在 `AddRange` 之前。

**修复方案：** 所有 `ToolStripItem`（`ToolStripLabel`/`ToolStripSeparator`/`ToolStripProgressBar` 等）必须在 `InitializeComponent()` 顶部集中 `new` 实例化，位于 `toolStrip1.Items.AddRange(...)` 之前。

### 2.4 变体四：字段已声明 + 属性/布局完整但无 new → 运行时 NullReferenceException

**错误现象：** 批量新增多个同类型控件（如为多张 Chart 各新增一个 Panel 包裹），完成了字段声明、`SuspendLayout`/`ResumeLayout` 配对、属性配置段、父容器挂载等所有步骤，**唯独遗漏** `InitializeComponent()` 开头的 `new` 实例化语句。

**后果：** 编译通过（字段已声明），运行时 `SuspendLayout()` 即触发 `NullReferenceException`（字段为 `null`）。

**根因：** 批量新增多个同类型控件时，注意力集中在属性配置和布局逻辑上，忽略了最基础的 `new` 实例化。

**修复方案：** 补充 `this.panelChartX = new AntdUI.Panel();` 到 `InitializeComponent()` 顶部。

> **四种变体总结：**
> ① 未声明 → 编译错误；
> ② 已声明但 new 晚于 AddRange → 运行时 ArgumentNullException；
> ③ 字段已声明但无 new → 设计器"未知名称"错误（编译可能通过）；
> ④ 字段已声明 + 属性/布局完整但无 new → 运行时 NullReferenceException（编译通过）。
> 根因均为「先实例化后使用」被破坏。

### 2.5 GridPanel 逆序入格规则

`AntdUI.GridPanel` 的 `Controls.Add` 顺序与单元格填充顺序**相反**（逆序入格）：最后 `Add` 的控件落入第一个单元格（左上角），依次向后填充。

#### 2×2 网格示例

```csharp
// 期望布局：2×2 网格
// ┌─────────┬─────────┐
// │ Chart2  │ Chart5  │  ← 第0行
// ├─────────┼─────────┤
// │ Chart3  │ Chart4  │  ← 第1行
// └─────────┴─────────┘
// 期望单元格顺序：Chart2(0,0) → Chart3(1,0) → Chart5(0,1) → Chart4(1,1)
// Controls.Add 必须写成**倒序**：
this.uiGridPanel2.Controls.Add(this.uiLineChart4);  // 先加 → 落入 (1,1) 右下
this.uiGridPanel2.Controls.Add(this.uiLineChart3);  // 次加 → 落入 (1,0) 左下
this.uiGridPanel2.Controls.Add(this.uiLineChart5);  // 再加 → 落入 (0,1) 右上
this.uiGridPanel2.Controls.Add(this.uiLineChart2);  // 后加 → 落入 (0,0) 左上
```

#### 关键要点

1. **逆序入格**：最后 `Add` 的控件落入第一个单元格（左上角），依次向后填充
2. **单行/单列布局**：`Span="40% 60%"` 表示单行两列，`Add(B)` → `Add(A)` 使 A 在左、B 在右
3. **2×2 网格**：`Span="fill fill;fill fill"` 表示两行两列，按逆序从右下到左上填充
4. **Padding 属性**：GridPanel 支持 `Padding = new Padding(5)` 设置单元格内边距
5. **子控件 Dock**：GridPanel 内的子控件应设置 `Dock = DockStyle.Fill` 充满单元格

#### 嵌套 GridPanel 的 Controls.Add 顺序

```csharp
// 外层 uiGridPanel1: Span="40% 60%"（左40% | 右60%）
this.uiGridPanel1.Controls.Add(this.uiGridPanel2);  // 先加 → 落入右格(60%)
this.uiGridPanel1.Controls.Add(this.uiLineChart1);  // 后加 → 落入左格(40%)

// 内层 uiGridPanel2: Span="fill fill;fill fill"（2×2）
this.uiGridPanel2.Controls.Add(this.uiLineChart4);  // 先加 → 落入 (1,1)
this.uiGridPanel2.Controls.Add(this.uiLineChart3);  // 次加 → 落入 (1,0)
this.uiGridPanel2.Controls.Add(this.uiLineChart5);  // 再加 → 落入 (0,1)
this.uiGridPanel2.Controls.Add(this.uiLineChart2);  // 后加 → 落入 (0,0)
```

#### 单 GridPanel 复杂布局

**需求**：5 张 Chart 放入单个 GridPanel，左侧 2 张（40% 宽度），右侧 3 张（60% 宽度，2x2 网格但只有 3 张）。

**Span 语法**：`"40% 30% 30%;40% 30% 30%-fill fill"`
- `-` 前：每行的列定义（`;` 分行）
  - Row 0: `40% 30% 30%`（3 列）
  - Row 1: `40% 30% 30%`（3 列）
- `-` 后：行高定义（空格分隔）
  - `fill fill`（2 行，各占 50%）

**Controls.Add 顺序**（逆序入格，5 个控件填入 6 个单元格，最后一个单元格空）：

```csharp
// 期望布局：
// ┌────────┬────────┬────────┐
// │ Chart1 │ Chart2 │ Chart5 │  ← Row 0
// ├────────┼────────┼────────┤
// │ Chart3 │ Chart4 │ (空)   │  ← Row 1
// └────────┴────────┴────────┘
// 单元格顺序：(0,0)→(0,1)→(0,2)→(1,0)→(1,1)→(1,2)
// Controls.Add 逆序：
this.uiGridPanel1.Controls.Add(this.uiLineChart4);  // 先加 → (1,1)
this.uiGridPanel1.Controls.Add(this.uiLineChart3);  // → (1,0)
this.uiGridPanel1.Controls.Add(this.uiLineChart5);  // → (0,2)
this.uiGridPanel1.Controls.Add(this.uiLineChart2);  // → (0,1)
this.uiGridPanel1.Controls.Add(this.uiLineChart1);  // 后加 → (0,0)
```

**方案对比：**

| 方案 | GridPanel 数量 | 控件总数 | 复杂度 |
|------|---------------|---------|--------|
| 嵌套 GridPanel | 2 个 | 5 Chart + 1 GridPanel | 高 |
| 单 GridPanel | 1 个 | 5 Chart | 低 |

**结论**：优先使用单 GridPanel + 复杂 Span（更简单、控件更少）。

#### Panel 包裹 vs 直接放入 GridPanel

| 方案 | 优点 | 缺点 |
|------|------|------|
| Panel 包裹 | 可实现圆润边角、白底、阴影动画 | 多一层嵌套，增加复杂度；易遗漏 Panel 实例化 |
| 直接放入 GridPanel | 结构简单，控件少，不易出错 | 无圆润边角效果（GridPanel 本身无圆角） |

**结论**：若无需圆角/阴影效果，优先选择直接放入 GridPanel（更简单、更不易出错）。

### 2.6 自检清单

修改或新增 Designer.cs 控件后，**必须按顺序**逐项检查：

- [ ] **① `new` 实例化**：`InitializeComponent()` 顶部是否有 `this.XXX = new XxxControl();`（**最易遗漏，编译通过但运行时 NullReferenceException**）
- [ ] ② `SuspendLayout`：实例化之后、属性配置之前是否调用
- [ ] ③ 属性配置段：`Name`/`Size`/`Location`/`Dock`/`Anchor` 等是否完整
- [ ] ④ `Controls.Add`：是否已挂载到正确的父容器
- [ ] ⑤ `ResumeLayout`：所有控件配置完成后是否调用
- [ ] ⑥ `private` 字段声明：类底部是否有对应字段声明
- [ ] ⑦ 事件绑定 `this.XXX.Event += ...` 中的 `XXX` 已实例化
- [ ] ⑧ 属性配置块中**不重复** `new`（避免双重实例化）

---

## 3. resx 孤儿类型引用

> 来源：DesignerResx-OrphanTypeRef

### 3.1 错误现象

迁移控件基类后，打开设计器报「文件中的类都不能进行设计…MainPage — 无法设计基类"System.Void"」。表面看是 MainPage 基类问题，实际根因在**被它引用的子窗体的 resx 文件**。

典型场景：`ConfigForm` 基类从 `Sunny.UI.UIForm2` 迁移到 `AntdUI.Window` 后，`ConfigForm.resx` 残留 `>>$this.Type=Sunny.UI.UIForm2` 孤儿类型引用，同时 resx 存在 XML 结构损坏（前序删除 `<data>` 开标签却遗留 `</data>` 闭合标签）。

### 3.2 根因分析

设计器加载子窗体时无法解析依赖类型（旧基类 + 损坏 XML），类型解析失败 → 回落 `System.Void`；该错误向上传导到宿主窗体（其内承载子窗体），于是宿主窗体也报 System.Void。

**System.Void 是"类型解析失败"的症状，不是某窗体基类被写成 void。**

传导路径：

```
子窗体.resx 有旧类型引用 / XML 损坏
  → 设计器解析子窗体类型失败
    → 子窗体基类回落为 System.Void
      → 宿主窗体承载子窗体时也报 System.Void
```

### 3.3 修复方案

1. 迁移基类（如 `UIForm2`→`AntdUI.Window`）后，**必须同步清理 resx 中 `$this.Type` 等旧类型引用**，或直接不再序列化 `$this.Type`（与已迁移窗体范式一致）。
2. resx 改写后必须用 XML 校验确认 well-formed（Python `xml.dom.minidom` 解析，或 VS 打开），删除孤儿开/闭标签。
3. 遇到「无法设计基类 System.Void」时，**不要只盯报错窗体**——要查它依赖/承载的所有子窗体、用户控件的 `.resx` 与 `.Designer.cs` 中的类型引用。

### 3.4 检查清单

- [ ] resx 中无 `Sunny.UI.*` / 其他已移除框架的类型残留
- [ ] `$this.Type` 不序列化，或与代码基类完全一致
- [ ] resx 经 XML 解析校验为 well-formed（无孤儿标签）
- [ ] `System.Void` 类错误优先排查"被引用窗体/resx"，而非报错窗体本身

---

## 4. 设计器模式单例陷阱

> 来源：WinForms-DesignMode-Singleton

### 4.1 错误现象

在 Visual Studio 中打开窗体的设计器视图时，报错：

> 扩展程序提供程序未能为该对象返回扩展程序。

设计器加载失败，无法继续编辑界面。

### 4.2 根因分析

窗体构造函数直接访问了 Lazy 单例（如 `LineLaserWorkflow.Instance`），首次访问触发私有构造函数，进而访问静态类（如 `GlobalCommData`），触发静态构造函数，最终创建通信管理器、加载 XML/INI 配置。设计器环境下这些运行时依赖可能不存在或不可用，导致异常被 Visual Studio 包装成"扩展程序提供程序"错误。

调用链：

```
FormMain()
  → LineLaserWorkflow.Instance
    → LineLaserWorkflow() 私有构造
      → GlobalCommData.CommunicationCommandReceived 访问
        → GlobalCommData static ctor
          → new CommunicationManager()
            → new TcpIpComm()
              → LoadConfig() 读取 XML/INI
```

### 4.3 修复方案

在窗体构造函数中加入 **设计模式守卫**，使用 `LicenseManager.UsageMode` 判断：

```csharp
using System.ComponentModel;

public FormMain()
{
    InitializeComponent();

    // 设计器模式下只完成界面初始化，不触发单例/硬件/配置文件依赖
    if (LicenseManager.UsageMode == LicenseUsageMode.Designtime)
    {
        return;
    }

    // 运行时逻辑：页面实例化、事件订阅、状态初始化...
}
```

同时，避免在字段声明处直接 `new` 可能触发运行时依赖的页面实例：

```csharp
// 不推荐
MainPage mainPage = new MainPage();

// 推荐：声明为字段，在构造函数的运行时分支中初始化
MainPage mainPage;
```

### 4.4 为什么不用 `this.DesignMode`

`this.DesignMode` 在构造函数执行期间**不可靠**。某些场景下构造函数执行时 `DesignMode` 仍为 `false`，导致设计器仍然进入运行时分支。

`LicenseManager.UsageMode == LicenseUsageMode.Designtime` 是更可靠的设计时判断方式。

### 4.5 禁止行为

- 在窗体构造函数中直接访问会触发静态构造函数的单例
- 在字段初始化器中 `new` 含有硬件/配置/数据库依赖的页面或对象
- 使用 `this.DesignMode` 作为构造函数内唯一的保护条件

### 4.6 相关风险点

以下页面在构造函数或字段初始化阶段也访问了单例/全局配置，若打开其设计器时报错，需按同样模式添加守卫：

- `LLCamWorkJob.cs`（现役 `UIDesign/TabPage/ILCamPage.cs`）：构造函数中订阅 `LineLaserWorkflow.Instance.*` 多个事件
- `CommGeneralPage.cs`（现役 `UIDesign/TabPage/FilebackupPage.cs`）：构造函数中读取 `GlobalCommData.mCommunicationManager`
- `CommRobotPage.cs`（现役 `UIDesign/TabPage/FilebackupPage.cs`）：构造函数中读取 `GlobalCommData.mCommunicationManager.ServerXdoc`
- `XMLEditor.cs`（现役 `UIDesign/TabPage/FileEditorPage.cs`）：初始化时加载 `GlobalCommData.mCommunicationManager` 中的 XML 文档

---

## 5. 既有 TableLayoutPanel 扩行/扩列 —— 四处必须同步

> 来源：2026-09-29 监控相机页顶栏改造（ADR-046）。在既有 `TableLayoutPanel`（TLP）里**新增一行**放顶栏（`MonitorCamPage` 根表由 1 行扩为 2 行：顶行连接栏 + 内容行）时，只改 `RowCount` 是**不够的**，四处必须同时改到，否则要么布局错位、要么运行时抛异常：

| # | 位置 | 漏改后果 |
|---|---|---|
| ① | `<TLP>.RowCount` / `.ColumnCount` | 子控件落在不存在的行列 → `ArgumentOutOfRangeException` |
| ② | `.RowStyles` / `.ColumnStyles` 的 `Add` 条数 | 计数 ≠ Count 时布局按默认均分，尺寸全乱 |
| ③ | 每个 `Controls.Add(ctrl, col, row)` 的**行号** | 已被移到第 1 行的子控件仍写 `row=0` → 与顶栏重叠 |
| ④ | `SuspendLayout()` / `ResumeLayout(false)` 配对 | 新容器未挂进布局期，设计器打开即报错 |

**要点**：
- 顶栏容器用 `SetColumnSpan(顶栏, 列数)` 跨满全宽；子控件一律 `Dock = Fill`，**不要**再手工写 `Location/Size`（`Dock` 会覆盖，但两处不一致会让设计器反复重排）。
- 顶栏横向控件的列宽用 `Absolute`（如 120 / 79 / 253 / 80 / 80），中间插入一列 `Percent 100F` 做弹性间隔 —— 直接照搬线激光页 `StatustabPanel` 的列定义即可。
- 改完**必须**用「`RowCount`/`ColumnCount` 与 `RowStyles`/`ColumnStyles` 的 `Add` 条数一致 + 每个 `Controls.Add` 的行列索引 < 对应 Count」重建校验（本环境无 C# 编译器，走 Python 静态校验，见 [[project/vibecoding-workflow]] Step 2.6），不要凭肉眼看。

---

## 6. 控件与组件的设计器归属 + resx 工程登记

> 来源：2026-09-30 监控相机页控件归属核查（业主口径「控件由 `*.Designer.cs` 完全设计，代码后置只做使用」）。

### 6.1 归属判据（三条）

| 内容 | 落点 |
|---|---|
| 可视控件：实例化 / 属性（`Dock`/`Size`/`FunctionalMode`…）/ 初始值（`Text`/`Checked`） | **`*.Designer.cs`** |
| **非可视组件**（`Timer` 等 `Component`）：实例化 + `Interval` + 事件订阅 | **`*.Designer.cs`**，且 `new …(this.components)` 挂容器托管；释放交 `components.Dispose()`，代码后置只 `Start()` / `Stop()` |
| 数据绑定 / 事件订阅 / 业务逻辑 / 运行期回填（配置值、连接态、帧图像） | 代码后置 |

> ⛔ **例外（不可搬）**：`AntdUI.Table` 的 `Columns = new AntdUI.ColumnCollection{…}` 与 `Binding()` **必须留在代码后置**——`InitializeComponent` 内不可赋值 `ColumnCollection`（AntdUI 约束，全库 13 处一致，Designer 中零例）。

### 6.2 五面对账（改完必跑；无编译器时用 Python 静态替代）

| # | 对账 | 判据 |
|---|---|---|
| ① | Designer 三面 | 字段声明数 == `this.X = new …` 数；可视控件均有 `Controls.Add(this.X)` |
| ② | 代码后置引用 | `.cs` 出现的控件标识符 ⊆ Designer 字段声明（差集 0） |
| ③ | 组件归属 | `.cs` 中 `new Timer()`（及任何 `Component`）== 0 |
| ④ | 事件不双写 | 同一事件 `.cs` 与 Designer 的 `+=` 计数只允许一处非 0 |
| ⑤ | **resx 工程登记** | 磁盘 `*.resx` 集合 == csproj `<EmbeddedResource>` 集合（**双向差集均须为空**） |

### 6.3 resx 漏注册（易漏项）

`*.resx` 在磁盘存在但**未登记进 csproj** 时：VS 解决方案树不把它嵌套到宿主文件下（缺 `<DependentUpon>`），设计器写入的资源无法嵌入。规范条目（照既有样板）：

```xml
<EmbeddedResource Include="UIDesign\TabPage\XxxPage.resx">
  <DependentUpon>XxxPage.cs</DependentUpon>
</EmbeddedResource>
```

2026-09-30 实测：全库 25 个 `.resx` 中 `MonitorCamPage.resx` 是**唯一**漏注册者，已补。

### 6.4 归属调整的字节安全流程

1. 先探明目标文件 **BOM / 行尾**（`raw[:3]==b'\xef\xbb\xbf'`、`raw.count(b'\r\n')` 与 `raw.count(b'\n')` 之差、`raw.count(b'\r\r\n')`）；
2. 多行锚点在 **CRLF 文件里必须用 `\r\n` 拼接**（只写 `\n` 会静默不命中，表现为「锚点命中 0 次」）；
3. **先在内存构造完整新内容 → 断言（锚点命中数 / 关键计数 / 行数增量 / 括号与 region 平衡）→ 再一次性写盘**；断言失败即未写盘（原子安全）；
4. 写盘后读回核对 BOM 原状、`\r\r\n == 0`、CRLF 行数增量符合预期。

---

## 来源

本文档由以下五篇教训记录合并整理而成：

- [[guides/WinForms-Designer]] — Designer.cs 不可修改原则
- [[guides/WinForms-Designer]] — 控件实例化顺序与 GridPanel 逆序入格规则
- [[guides/WinForms-Designer]] — resx 孤儿类型引用导致 System.Void 基类级联
- [[guides/WinForms-Designer]] — 设计器模式单例初始化陷阱
- 2026-09-30 监控相机页控件与组件归属核查（非可视组件 Timer 迁入设计器 + `.resx` 补注册 + 五面对账）
