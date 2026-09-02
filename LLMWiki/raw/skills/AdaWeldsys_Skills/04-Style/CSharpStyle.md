---
name: "AdaWeldSystem C# 代码风格规范"
version: "V2.260624.1024"
description: "为 AdaWeldSystem 项目编写 C# 代码时必须遵循的风格规范。涵盖命名约定、代码结构、注释规范、异常处理、UI设计、运动控制、C# 7.3 语言约束等。适用于 .NET Framework 4.8 + WinForms + SunnyUI + HelixToolkit + 雷赛控制卡技术栈。"
---

# AdaWeldSystem C# 代码风格规范

## 描述

本 Skill 定义了 AdaWeldSystem 项目的完整 C# 编码规范。当你被要求为该项目编写 C# 代码时，必须严格遵循以下所有规则，确保代码风格与现有项目保持一致。

## 版本变更记录

| 版本 | 更新时间 | 变更级别 | 变更索引 | 变更内容 |
|------|---------|---------|---------|---------|
| V1.0 | 2026-06-12 | - | - | 初始版本。暂无修改记录。 |
| V1.260612.15 | 2026-06-12 | 文档级 | 版本记录 | 执行 /updateskill 流程，同步版本记录 |
| V1.260615.17 | 2026-06-15 | 文档级 | 字符串插值 | 新增"字符串插值中的格式化陷阱"强制规则 |
| V1.260615.18 | 2026-06-15 | 文档级 | 字符串插值 | 修正格式化陷阱的错误原因描述：非冒号语法问题，而是编译器SDK版本兼容性缺陷 |
| V1.260615.19 | 2026-06-15 | 文档级 | using顺序/LINQ引用 | 新增LINQ强制引用规则；description增加版本号显示 |
| V1.260615.1815 | 2026-06-15 | 文档级 | /updateskill流程 | 更新/updateskill步骤3，添加强制版本号生成公式和校验清单，确保每次更新正确应用yyMMdd.HHmm格式 |
| V1.260616.1510 | 2026-06-16 | 文档级 | UI参数配置页规范 | 新增ParamConfigPage参数配置页面UI风格规范：GroupBox内嵌TableLayoutPanel、SymbolLabel+输入控件并排、统一Margin/Padding |
| V1.260618.1151 | 2026-06-18 | 文档级 | 事件参数对象复用 | 新增"事件参数对象复用（强制）"规则：高频触发的事件参数必须声明为类级字段而非方法内局部变量，避免GC压力 |
| V2.260619.1015 | 2026-06-19 | 结构级 | 运动控制规范 | 新增"运动控制代码规范"完整章节：运动控制函数命名、设备运行状态枚举、轴控制参数结构、运动控制事件模式、雷赛控制卡API封装规范 |
| V2.260623.1744 | 2026-06-23 | 结构级 | 文件位置 | 从 trae 技能系统迁移到项目 Skills/04-Style/ 文件夹，作为子 skill 被根 skill 动态引用 |
| V2.260624.1024 | 2026-06-24 | 文档级 | UI设计器兼容性 | 新增"WinForms设计器兼容性规范"：InitializeComponent中禁止使用for/while/if等流程控制语句，必须展开为独立语句 |

### 版本命名规则

- 格式：`V{大版本}.{小版本}`
- **大版本**：int从1开始递增，结构级修改时+1
- **小版本**：日期格式`yyMMdd.HHmm`（如260612.1430表示2026年6月12日14时30分），文件级/文档级修改时更新

### 变更记录格式

`修改级别 | 修改对象 | 修改事项`

| 修改级别 | 修改对象 | 示例 |
|---------|---------|------|
| 结构级 | 目录/整体架构 | 结构级 \| 整体架构 \| 重构为多分支工作流 |
| 文件级 | 文件名 | 文件级 \| 命名规范表 \| 新增控件前缀 |
| 文档级 | 文件内表格/条目 | 文档级 \| C# 7.3 约束表 \| 补充禁止语法 |

## 使用场景

- 为 AdaWeldSystem 项目编写新的 C# 类、方法、属性
- 创建 WinForms UI 页面（.cs + .Designer.cs + .resx）
- 编写 HelixToolkit 3D 渲染相关代码
- 编写 EmguCV 图像算法代码
- 编写配置文件读写、日志、通信等通用代码
- 编写运动控制代码（雷赛控制卡轴控制、设备流程控制）
- 任何涉及该项目的 C# 代码生成任务

## 多分支工作流

### 唤醒词结构

| 唤醒词 | 工作分支 | 用途 |
|--------|---------|------|
| `/updateskill` | Skill 自更新 | 根据用户反馈自动更新 skill 规范并同步至 trae 技能系统 |

**使用方式**：用户输入 `/updateskill` 或明确表达"优化 skill"、"更新 skill"、"修改 skill 规范"等意图时触发对应分支。

---

## /updateskill：Skill 自更新工作流

### 工作流说明

本分支用于根据用户反馈自动更新 skill 规范，并将更新后的 skill 文件同步保存到用户工作文件夹，无需用户手动替换 trae 技能系统中的 skill 文件。

### 唤醒方式

用户输入 `/updateskill` 或明确表达"优化 skill"、"更新 skill"、"修改 skill 规范"等意图时触发。

### 执行步骤

#### 步骤1：读取当前 skill 文件

读取 `d:\AdaWeldSystem0623\AdaWeldSystem\Skills\04-Style\CSharpStyle.md` 的当前内容。

#### 步骤2：根据用户反馈确定更新内容

用户可能提出的更新类型：
- **命名规范更新**：如新增控件命名前缀、调整类/方法命名规则
- **代码结构更新**：如类成员顺序、文件组织方式调整
- **UI 规范更新**：如控件尺寸、字体、布局模式调整
- **语言约束更新**：如新增/移除 C# 7.3 禁止语法项
- **运动控制规范更新**：如新增轴控制函数命名、状态机模式、运动控制事件规范
- **内容补充**：如新增技术栈规范、补充示例代码等

#### 步骤3：在最新版本上修改 skill

**重要原则**：
- **必须在最新版本上修改**，不能拿旧版本覆盖
- 每次修改前读取当前 skill 文件，确保基于最新状态
- **版本号生成公式（强制执行）**：
  ```
  小版本 = 执行 PowerShell 命令 Get-Date -Format "yyMMdd.HHmm" 获取的当前系统时间
  ```
  **执行方式**：在 TRAE 沙盒中运行 `Get-Date -Format "yyMMdd.HHmm"`，将返回结果直接作为小版本号。严禁估算或手动填写。例如：2026年6月15日18时30分 → 260615.1830
  ```
  - **绝对禁止**在旧版本号上+1（如 V1.260615.19 → V1.260615.20 是错误的）
  - **必须**基于当前系统时间重新生成（如 V1.260615.19 → V1.260615.1830）
- 修改后版本号按规则递增：
  - 结构级修改：大版本+1，小版本=当前日期时间(yyMMdd.HHmm)
  - 文件级/文档级修改：大版本不变，小版本=当前日期时间(yyMMdd.HHmm)
- **版本号校验清单（必须执行）**：
  - [ ] 读取当前 skill 文件中的 version 字段
  - [ ] 获取当前系统时间（年-月-日 时:分）
  - [ ] 格式化小版本：yyMMdd.HHmm（如260615.1830）
  - [ ] 组合新版本号：V{大版本}.{小版本}
  - [ ] 验证：小版本必须包含当前日期，且与当前时间匹配
  - [ ] 验证：新版本号 ≠ 旧版本号+1（禁止简单递增）

#### 步骤4：保存 skill 备份到用户文件夹

保存路径：`d:\AdaWeldSystem0623\AdaWeldSystem\Backup\Skills\CSharpStyle_V{版本号}.md`

**命名规则**：`{skill_name}_V{版本号}.md`

#### 步骤5：同步更新 trae 技能系统

将修改后的 skill 文件写回 trae 技能系统路径：
```
C:\Users\27720\.trae-cn\skills\adaweldsystem-c-代码风格规范\SKILL.md
```

**注意**：直接覆盖原文件，无需用户手动操作。

#### 步骤6：向用户汇报变更

汇报内容：
- 更新后的版本号
- 变更级别、变更索引、变更内容
- 备份文件路径
- 已自动同步至 trae 技能系统

---

## 项目基本信息

- **语言版本**: C# 7.3（.NET Framework 4.8，不支持 C# 8.0+ 语法）
- **目标框架**: .NET Framework 4.8（传统 .NET Framework，非 .NET Core / .NET 5+）
- **平台目标**: x64
- **UI框架**: WinForms + SunnyUI + HelixToolkit.Wpf.SharpDX
- **图像处理**: EmguCV
- **数据库**: SQLite
- **运动控制**: 雷赛控制卡（Leadshine）
- **项目类型**: 工业视觉/焊接自动化桌面应用程序（WinExe）

## 命名规范

### 命名空间
- 使用 `AdaWeldSystem.{功能模块}` 或 `{LibraryName}.{子模块}` 格式
- 示例: `AdaWeldSystem.Comm`, `AdaWeldSystem.UIDesign.Sub2UI`, `PointCloudLibrary.Models`
- **运动控制模块**: `AdaWeldSystem.MotionControl`

### 类/结构体
- **PascalCase**，描述性名词或名词短语
- 示例: `PointCloudData`, `PointCloudViewer`, `SurfaceTriangulator`, `AlgorithmManager`
- **运动控制类**: `MotionController`, `AxisManager`, `DeviceStateMachine`

### 接口
- **PascalCase**，以 `I` 前缀开头

### 方法
- **PascalCase**，动词或动词短语
- 示例: `LoadPointCloud()`, `GenerateSurface()`, `ClearAll()`, `GetBounds()`
- **运动控制方法**: `MoveAbsolute()`, `MoveRelative()`, `HomeAxis()`, `StopAxis()`, `JogAxis()`

### 属性
- **PascalCase**
- 示例: `public PointCloudData CurrentData => _currentData;`

### 字段
- **私有字段**: 下划线前缀 + camelCase，如 `_currentData`, `_pointModel`, `_displayRatio`
- **公共字段**: 尽量避免，使用属性替代

### 局部变量/参数
- **camelCase**
- 示例: `pointSize`, `searchRadius`, `minX`, `filePath`

### 常量
- **PascalCase** 或 **全大写下划线分隔**
- 示例: `DEFAULT_IP_ADR`, `DEFAULT_PORT_NUM`

### 事件/委托
- 事件名: **PascalCase**
- 事件参数类: 继承 `EventArgs`，以 `EventArgs` 结尾
- 示例: `public static event EventHandler<MachineStatusMessageArgs> EevetStatusHandler;`

### 枚举
- 枚举名: **PascalCase**
- 枚举值: **PascalCase**
- 示例: `FilterOperation { GaussianBlur, MedianBlur, MeanBlur }`

## 代码结构规范

### 文件组织
- 每个文件一个类（主类），允许包含相关的小结构体/枚举
- 使用 `#region` 对代码块进行逻辑分组

### 类成员顺序
1. 常量/静态字段
2. 实例字段（私有）
3. 构造函数/析构函数
4. 公共属性
5. 公共方法（按功能分组）
6. 私有方法
7. 嵌套类/结构体

### 访问修饰符
- 显式声明访问修饰符，不使用默认访问级别
- 优先使用 `private`，需要时提升为 `public`/`protected`/`internal`

### 属性写法
- 优先使用自动属性或表达式主体属性
- 完整属性使用 backing field:
```csharp
private float _pointSize = 2f;
public float PointSize
{
    get => _pointSize;
    set
    {
        _pointSize = value;
        _viewer?.SetPointSize(value);
    }
}
```

### 构造函数与析构函数
- 析构函数用于资源清理:
```csharp
~PointCloudData()
{
    Clear();
}
```
- 实现 `IDisposable` 时提供 `Dispose()` 方法:
```csharp
public void Dispose()
{
    ClearAll();
}
```

## 注释规范

### XML文档注释（强制）
- **所有公共成员必须使用 XML 文档注释**
- 使用中文注释
- 格式:
```csharp
/// <summary>
/// 3D点云查看器 - 基于HelixToolkit.Wpf.SharpDX
/// 显示逻辑：
/// 1. 导入文件后加载原始点云显示
/// 2. 减点显示：清除原有点云，显示减点后的点云
/// 3. 表面渲染：按最新点云生成表面，清除点云，显示表面
/// 4. 清除显示：清理所有点云和模型
/// </summary>
```

### 方法参数注释
- 使用 `<param>` 标签说明参数含义
- 使用 `<returns>` 标签说明返回值
```csharp
/// <summary>
/// 减点显示：清除界面上原始点的显示后显示减点后的点云
/// </summary>
/// <param name="ratio">显示比例（0.01-1.0），如0.5表示显示一半点数</param>
public void ReducePointCloud(float ratio)
```

### 行内注释
- 使用 `//` 进行简短说明
- 复杂算法步骤前添加注释说明逻辑

## 异常处理

### 参数验证
- 使用 `ArgumentNullException` 验证空引用:
```csharp
public PointCloudViewer(Viewport3DX viewport)
{
    _viewport = viewport ?? throw new ArgumentNullException(nameof(viewport));
    InitializeViewport();
}
```

### 异常捕获
- UI事件中使用 try-catch 并显示用户友好的错误消息:
```csharp
try
{
    LoadPointCloud(openFileDialog1.FileName);
}
catch (Exception ex)
{
    MessageBox.Show($"加载文件失败:\n{ex.Message}", "错误",
        MessageBoxButtons.OK, MessageBoxIcon.Error);
}
```

### 静默处理
- 非关键错误可静默处理，但保留注释说明:
```csharp
try
{
    mXdocument.Descendants("ConfigName").FirstOrDefault().Value = Name;
    SaveXdocument();
}
catch
{
    // 静默处理配置保存失败
}
```

## C# 7.3 语言约束（必须严格遵守）

### 禁止使用的 C# 8.0+ 语法

| 禁止语法 | 说明 | 替代写法 |
|----------|------|----------|
| `switch` 表达式 | `var result = x switch { ... }` | 使用传统 `switch` 语句 |
| 属性模式匹配 | `if (obj is { Name: "xxx" })` | 使用 `if (obj.Name == "xxx")` |
| `using` 声明 | `using var stream = ...` | 使用 `using (var stream = ...) { }` 块 |
| 可空引用类型 | `string?`, `#nullable enable` | 不使用，保持传统写法 |
| 默认接口方法 | 接口中不能有实现 | 接口只声明，在类中实现 |
| 异步流 | `async IAsyncEnumerable<T>` | 返回 `Task<List<T>>` |
| 异步 using | `await using` | 使用 `try-finally` + `Dispose()` |
| 范围运算符 | `array[1..3]` | 使用 `array.Skip(1).Take(2)` |
| `init` 访问器 | `public int X { get; init; }` | 使用 `public int X { get; set; }` |
| `record` 类型 | `record Point(int X, int Y)` | 使用 `class` 或 `struct` |
| 模式匹配增强 | `if (x is > 0 and < 10)` | 使用 `if (x > 0 && x < 10)` |
| `$@""` 插值 | `$@"Hello {name}"` | 使用 `$"Hello {name}"` 或 `@"..."` + 拼接 |
| `nint`/`nuint` | 原生整数 | 使用 `int` |
| 函数指针 | `delegate*` | 使用 `delegate` |

### 允许使用的 C# 7.3 语法

| 允许语法 | 示例 |
|----------|------|
| `out var` 内联声明 | `int.TryParse(s, out int result)` |
| 元组 | `(float x, float y, float z) GetCenter()` |
| 值元组返回 | `return (x, y, z)` |
| `nameof()` | `nameof(viewport)` |
| 字符串插值 `$""` | `$"文件未找到: {filePath}"` |
| `??` 空合并运算符 | `data ?? throw new ArgumentNullException(...)` |
| `?.` 空条件运算符 | `_viewer?.SetPointSize(value)` |
| `=>` 表达式主体成员 | `public int Count => _points.Count;` |
| `[CallerMemberName]` | `protected void OnPropertyChanged([CallerMemberName] string name = null)` |
| `readonly struct` | `public readonly struct Point3D` |
| `unsafe` 代码块 | 项目已启用 `<AllowUnsafeBlocks>true</AllowUnsafeBlocks>` |
| 局部函数 | `int LocalFunc() { ... }` |
| `async`/`await` | `public async Task LoadAsync()` |

## UI 控件文件结构

**每个 UI 控件/页面必须包含三个文件**：

```
UIDesign/Sub1UI/
├── MainPage.cs              ← 业务逻辑代码（partial class）
├── MainPage.Designer.cs      ← 设计器生成的控件初始化代码（partial class）
└── MainPage.resx             ← 资源文件（图标、字符串等本地化资源）
```

- **`.cs` 文件**: 包含事件处理、业务逻辑、公共方法、属性定义
  - 类声明使用 `partial class`
  - 示例: `public partial class MainPage : UIPage`
- **`.Designer.cs` 文件**: 包含 `InitializeComponent()` 方法和控件字段声明
  - 类声明使用 `partial class`
  - 包含 `#region 组件设计器生成的代码`
  - 包含 `components` 字段、`Dispose(bool)` 方法、`InitializeComponent()` 方法
  - 控件字段声明在 `#endregion` 之后
- **`.resx` 文件**: 嵌入式资源

**非 UI 类只需单文件**。

## UI 界面设计规范

### 页面基类
- 所有页面继承 `Sunny.UI.UIPage`
- 命名空间格式: `AdaWeldSystem.Sub{层级}UI`
- 页面类名使用 `Page`/`Form` 后缀

### 控件命名规范

| 控件类型 | 命名前缀 | 示例 |
|----------|----------|------|
| UIButton | `btn` + 功能名 | `btnLoadPCL`, `btnSurface`, `btnClearData` |
| UISymbolButton | `btn` + 功能名 | `btnRotate`, `btnMove`, `btnRound` |
| UIPanel | `uiPanel` + 序号 | `uiPanel1`, `uiPanel2` |
| UITitlePanel | `uiTitlePanel` + 序号 | `uiTitlePanel1`, `uiTitlePanel2` |
| UIGroupBox | `uiGroupBox` + 序号 | `uiGroupBox1`, `uiGroupBox3` |
| UILabel | `uiLabel` + 序号 | `uiLabel1`, `uiLabel2` |
| UISymbolLabel | `uiSymbolLabel` + 序号 | `uiSymbolLabel1`, `uiSymbolLabel16` |
| UITextBox | 功能名/直接命名 | `mAutoParamName`, `WireType`, `PlateType` |
| UIDoubleUpDown | 功能名 | `LaserPower`, `FeedSpeed`, `WireDiameter` |
| UIIntegerUpDown | `uiIntegerUpDown` + 序号 | `uiIntegerUpDown1` |
| UIComboBox | `uiComboBox` + 序号 | `uiComboBox1` |
| UICheckBox | 功能名 | `EnableLive` |
| UIDataGridView | `uiDataGridView` + 序号 | `uiDataGridView1` |
| UIPagination | `uiPagination` + 序号 | `uiPagination1` |
| UIRichTextBox | `rtb_` + 功能名 | `rtb_Log` |
| UILineChart | `uiLineChart` + 序号 | `uiLineChart1`, `uiLineChart5` |
| UISplitContainer | `uiSplitContainer` + 序号 | `uiSplitContainer1` |
| UINavBar | `uiNavBar` + 序号 | `uiNavBar1` |
| UINavMenu | `uiNavMenu` + 序号 | `uiNavMenu1` |
| UITabControl | `uiTabControl` + 序号 | `uiTabControl1` |
| UIContextMenuStrip | `uiContextMenuStrip` + 序号 | `uiContextMenuStrip1` |
| UIToolTip | `uiToolTip` + 序号 | `uiToolTip1` |
| UIImageButton | `uiImageButton` + 序号 | `uiImageButton1` |
| ElementHost | `elementHost` + 序号 | `elementHost1` |
| OpenFileDialog | `openFileDialog` + 序号 | `openFileDialog1` |
| PropertyGrid | `propertyGrid` + 序号 | `propertyGrid1` |
| ImageBox (EmguCV) | `imageBox` + 序号 | `imageBox1` |
| DataGridViewColumn | `Column` + 序号 | `Column1`, `Column2` |
| ToolStripMenuItem | 功能名 | `SelectConfig`, `DeleteConfig` |

### 布局模式

#### 主布局容器
- 使用 `TableLayoutPanel` 或 `UITableLayoutPanel` 作为主布局容器
- 典型结构:
```csharp
this.tableLayoutPanel1.ColumnCount = 2;
this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));
this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 450F));
this.tableLayoutPanel1.Dock = System.Windows.Forms.DockStyle.Fill;
```

#### 面板嵌套
- 使用 `UIPanel` 或 `UITitlePanel` 作为功能分组容器
- `UITitlePanel` 用于带标题的功能区域:
```csharp
this.uiTitlePanel1.Text = "日志信息";
this.uiTitlePanel1.TextAlignment = System.Drawing.ContentAlignment.MiddleLeft;
this.uiTitlePanel1.Padding = new System.Windows.Forms.Padding(1, 35, 1, 1);
this.uiTitlePanel1.ShowText = false;
```

#### 参数分组
- 使用 `UIGroupBox` 对参数进行逻辑分组:
```csharp
this.uiGroupBox1.Text = "焊丝参数设定";
this.uiGroupBox1.TextAlignment = System.Drawing.ContentAlignment.MiddleLeft;
this.uiGroupBox1.Padding = new System.Windows.Forms.Padding(0, 32, 0, 0);
```

### 控件通用属性设置

#### 字体设置
- **所有SunnyUI控件统一使用宋体12号**:
```csharp
this.btnLoadPCL.Font = new System.Drawing.Font("宋体", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
```
- TipsFont 使用宋体9号:
```csharp
this.btnLoadPCL.TipsFont = new System.Drawing.Font("宋体", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
```

#### 按钮标准尺寸
- 标准按钮: `Size = new System.Drawing.Size(140, 35)`
- 小按钮: `Size = new System.Drawing.Size(100, 35)`
- Symbol按钮: `Size = new System.Drawing.Size(86, 35)`
- 所有按钮设置: `MinimumSize = new System.Drawing.Size(1, 1)`
- 所有按钮设置: `Cursor = System.Windows.Forms.Cursors.Hand`

#### 输入控件标准尺寸
- UIDoubleUpDown: `Size = new System.Drawing.Size(150, 29)`, `MinimumSize = new System.Drawing.Size(100, 0)`
- UITextBox: `Size = new System.Drawing.Size(150, 29)`, `MinimumSize = new System.Drawing.Size(1, 16)`
- UIComboBox: `Size = new System.Drawing.Size(150, 29)`

#### SymbolLabel标准尺寸
- `Size = new System.Drawing.Size(170, 35)` 或 `Size = new System.Drawing.Size(181, 35)`
- `MinimumSize = new System.Drawing.Size(1, 1)`

### 事件绑定规范

#### 按钮点击事件
```csharp
this.btnLoadPCL.Click += new System.EventHandler(this.btnLoadPCL_Click);
this.btnRotate.Click += new System.EventHandler(this.btnRotate_Click);
```

#### 复选框事件
```csharp
this.EnableLive.CheckedChanged += new System.EventHandler(this.EnableLive_CheckedChanged);
```

#### 分页事件
```csharp
this.uiPagination1.PageChanged += new Sunny.UI.UIPagination.OnPageChangeEventHandler(this.uiPagination1_PageChanged);
```

#### 属性网格事件
```csharp
this.propertyGrid1.PropertyValueChanged += new System.Windows.Forms.PropertyValueChangedEventHandler(this.propertyGrid1_PropertyValueChanged);
```

#### 页面生命周期事件
```csharp
this.Shown += new System.EventHandler(this.ParamAutoPage_Shown);
this.AfterShown += new System.EventHandler(this.MainPage_AfterShown);
```

### 事件处理方法命名
- 格式: `控件名_事件名`
- 示例:
  - `btnLoadPCL_Click`, `btnSurface_Click`, `btnClearData_Click`
  - `uiPagination1_PageChanged`
  - `propertyGrid1_PropertyValueChanged`
  - `ParamAutoPage_Shown`, `MainPage_AfterShown`

### 页面标准属性
```csharp
this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.None;
this.ClientSize = new System.Drawing.Size(宽度, 高度);
this.Name = "页面类名";
this.Text = "页面显示标题";
```

### 控件声明顺序
在 `#endregion` 后的声明区域按以下顺序:
1. 布局容器 (TableLayoutPanel, SplitContainer)
2. 面板 (UIPanel, UITitlePanel, UIGroupBox)
3. 数据显示控件 (UIDataGridView, UIRichTextBox, UILineChart)
4. 输入控件 (UITextBox, UIDoubleUpDown, UIIntegerUpDown, UIComboBox, UICheckBox)
5. 标签 (UILabel, UISymbolLabel)
6. 按钮 (UIButton, UISymbolButton, UIImageButton)
7. 对话框 (OpenFileDialog)
8. 菜单 (UIContextMenuStrip, ToolStripMenuItem)
9. 其他辅助控件 (UIToolTip, ElementHost, PropertyGrid)

### 参数配置页面特殊规范（ParamConfigPage 风格）

基于 `ParamConfigPage` 实际 UI 实现归纳的规范，适用于参数配置类页面：

#### 布局结构
- **外层**：使用 `TableLayoutPanel` 作为主布局容器，按功能区域分栏
- **内层**：每个 `UIGroupBox` 内部嵌套独立的 `TableLayoutPanel`，实现标签与输入控件的整齐排列
- **底部**：按钮区使用独立的 `TableLayoutPanel`，按钮居中或右对齐

#### GroupBox 内嵌 TableLayoutPanel 规范
```csharp
// GroupBox 作为功能分区容器
this.uiGroupBox1.Text = "焊丝参数设定";
this.uiGroupBox1.TextAlignment = System.Drawing.ContentAlignment.MiddleLeft;
this.uiGroupBox1.Padding = new System.Windows.Forms.Padding(0, 32, 0, 0);

// 内部 TableLayoutPanel 实现标签+输入控件并排
this.tableLayoutPanelGroup1.ColumnCount = 2;
this.tableLayoutPanelGroup1.ColumnStyles.Add(
    new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 120F)); // SymbolLabel 固定宽度
this.tableLayoutPanelGroup1.ColumnStyles.Add(
    new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));  // 输入控件自适应
this.tableLayoutPanelGroup1.Dock = System.Windows.Forms.DockStyle.Fill;
```

#### SymbolLabel + 输入控件并排规范
- **每行一个参数**：左侧 `UISymbolLabel`（固定宽度 120px），右侧输入控件（自适应填充）
- **垂直间距**：通过 `TableLayoutPanel` 的 `RowStyle` 控制，或设置控件 `Margin = new Padding(0, 5, 0, 5)`
- **水平对齐**：`SymbolLabel` 左对齐，`输入控件` 左对齐填充

```csharp
// SymbolLabel 设置
this.uiSymbolLabel1.Text = "焊丝材质";
this.uiSymbolLabel1.Symbol = 62142; // 可选图标
this.uiSymbolLabel1.Size = new System.Drawing.Size(120, 29);
this.uiSymbolLabel1.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;

// 输入控件设置（以 UITextBox 为例）
this.WireType.Dock = System.Windows.Forms.DockStyle.Fill;
this.WireType.Margin = new System.Windows.Forms.Padding(5, 3, 5, 3);
```

#### 统一 Margin / Padding 规范
- **GroupBox 内边距**：`Padding = new Padding(0, 32, 0, 0)`（为标题留出空间）
- **TableLayoutPanel 单元格边距**：`Margin = new Padding(5, 3, 5, 3)`
- **GroupBox 之间间距**：通过外层 TableLayoutPanel 的 `RowStyle` 控制，或设置 `Margin = new Padding(5)`
- **按钮间距**：相邻按钮之间 `Margin = new Padding(5, 0, 5, 0)`

#### 参数配置页面典型布局示例
```csharp
// 外层主布局：2列（左参数区 + 右参数区），多行
this.tableLayoutPanelMain.ColumnCount = 2;
this.tableLayoutPanelMain.ColumnStyles.Add(
    new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50F));
this.tableLayoutPanelMain.ColumnStyles.Add(
    new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50F));
this.tableLayoutPanelMain.RowCount = 3; // 多行放置不同 GroupBox
this.tableLayoutPanelMain.Dock = System.Windows.Forms.DockStyle.Fill;

// 左侧 GroupBox：焊丝参数
this.uiGroupBox1.Text = "焊丝参数设定";
this.tableLayoutPanelMain.Controls.Add(this.uiGroupBox1, 0, 0);

// 右侧 GroupBox：焊接板材
this.uiGroupBox2.Text = "焊接板材设定";
this.tableLayoutPanelMain.Controls.Add(this.uiGroupBox2, 1, 0);

// 底部按钮区
this.tableLayoutPanelButtons.ColumnCount = 3;
this.tableLayoutPanelButtons.ColumnStyles.Add(
    new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 33.33F));
this.tableLayoutPanelButtons.ColumnStyles.Add(
    new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 33.33F));
this.tableLayoutPanelButtons.ColumnStyles.Add(
    new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 33.33F));
this.tableLayoutPanelMain.Controls.Add(this.tableLayoutPanelButtons, 0, 2);
this.tableLayoutPanelMain.SetColumnSpan(this.tableLayoutPanelButtons, 2);
```

### WinForms设计器兼容性规范（强制）

**`InitializeComponent()` 方法中禁止使用 `for`、`while`、`if`、`switch`、`foreach` 等流程控制语句。**

**错误原因**：Visual Studio WinForms 设计器（以及 SunnyUI 设计器）解析 `InitializeComponent()` 的能力极其有限，只能理解简单的属性赋值、对象创建和控件添加语句。任何流程控制语句（循环、条件分支）都会导致设计器无法解析代码，报错"设计器无法处理第 X 行的代码"，并强制要求取消更改。

**错误示例**：
```csharp
// 错误写法 - 设计器无法解析 for 循环
_paramPanel.RowCount = 4;
for (int i = 0; i < 4; i++)
{
    _paramPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 40F));
}
```

**正确写法**：将循环展开为独立的顺序语句
```csharp
// 正确写法 - 设计器可正常解析
_paramPanel.RowCount = 4;
_paramPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 40F));
_paramPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 40F));
_paramPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 40F));
_paramPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 40F));
```

**设计器兼容的语句类型**：
- 变量声明与赋值：`Type name = new Type();`
- 属性赋值：`obj.Property = value;`
- 方法调用（简单）：`list.Add(item);`
- 事件绑定：`obj.Event += Handler;`
- 控件添加：`parent.Controls.Add(child, column, row);`

**设计器不兼容的语句类型（禁止在InitializeComponent中使用）**：
- 循环语句：`for`、`while`、`do-while`、`foreach`
- 条件语句：`if`、`else`、`switch`、`?:` 三元运算符
- 异常处理：`try-catch-finally`
- 局部方法调用：调用自定义方法（如 `InitializeParamControls()` 应在 `InitializeComponent()` 外部调用）
- LINQ 查询表达式
- 复杂表达式：包含多个运算符的复合表达式

**解决方案**：
1. **循环展开**：将固定次数的循环手动展开为独立语句
2. **条件外移**：将条件判断逻辑移到 `InitializeComponent()` 调用之前或之后
3. **方法外移**：将复杂初始化逻辑拆分到单独的私有方法中，在构造函数中于 `InitializeComponent()` 之后调用
4. **动态初始化**：如需动态生成控件，在 `Load` 或 `Shown` 事件中进行

```csharp
// 推荐模式：构造函数中分层初始化
public RenderParamForm()
{
    InitializeComponent();     // 仅包含设计器兼容的简单语句
    InitializeParamControls(); // 复杂逻辑移到这里
    LoadConfigValues();        // 数据加载移到这里
}
```

### 3D渲染页面特殊规范
- 使用 `ElementHost` 承载WPF 3D视口:
```csharp
this.elementHost1 = new System.Windows.Forms.Integration.ElementHost();
this.elementHost1.Dock = System.Windows.Forms.DockStyle.Fill;
this.elementHost1.Child = null;  // 在代码中动态设置
```
- 右侧工具面板使用 `UIPanel` + `UISymbolButton` 组合
- SymbolButton 使用 `Symbol` 属性设置图标编号
- 使用 `UIToolTip` 为SymbolButton添加提示:
```csharp
this.uiToolTip1.SetToolTip(this.btnRotate, "旋转");
```

### 数据表格页面特殊规范
- 使用 `UIDataGridView` + `UIPagination` 组合
- 列使用 `DataGridViewTextBoxColumn`
- 设置交替行颜色:
```csharp
dataGridViewCellStyle1.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(243)))), ((int)(((byte)(249)))), ((int)(((byte)(255)))));
this.uiDataGridView1.AlternatingRowsDefaultCellStyle = dataGridViewCellStyle1;
```
- 表头样式:
```csharp
dataGridViewCellStyle2.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(80)))), ((int)(((byte)(160)))), ((int)(((byte)(255)))));
dataGridViewCellStyle2.ForeColor = System.Drawing.Color.White;
```

## 运动控制代码规范（新增）

### 适用范围
- 雷赛控制卡（Leadshine）运动控制代码
- 焊缝跟踪算法结果引导运动轴移动
- 自动对焦算法结果引导Z轴移动
- 设备运行流程与状态控制

### 命名空间
- 运动控制模块命名空间: `AdaWeldSystem.MotionControl`

### 运动控制类命名规范

| 类类型 | 命名规则 | 示例 |
|--------|---------|------|
| 运动控制器主类 | `MotionController` 或 `AxisController` | `MotionController` |
| 轴管理器 | `AxisManager` | `AxisManager` |
| 单轴控制 | `AxisControl` + 轴名 | `AxisControlX`, `AxisControlY`, `AxisControlZ` |
| 设备状态机 | `DeviceStateMachine` | `DeviceStateMachine` |
| 运动参数配置 | `MotionConfig` | `MotionConfig` |
| 轴参数结构 | `AxisParameter` | `AxisParameter` |
| 运动控制事件参数 | `MotionEventArgs` | `MotionCompletedEventArgs` |

### 运动控制函数命名规范

| 功能类型 | 命名规则 | 示例 |
|----------|---------|------|
| 绝对定位运动 | `MoveAbsolute` | `MoveAbsolute(int axis, double position, double speed)` |
| 相对定位运动 | `MoveRelative` | `MoveRelative(int axis, double distance, double speed)` |
| 回零运动 | `HomeAxis` | `HomeAxis(int axis)` |
| 点动运动 | `JogAxis` | `JogAxis(int axis, bool direction, double speed)` |
| 停止轴运动 | `StopAxis` | `StopAxis(int axis)` |
| 紧急停止 | `EmergencyStop` | `EmergencyStop()` |
| 获取轴当前位置 | `GetAxisPosition` | `GetAxisPosition(int axis)` |
| 获取轴状态 | `GetAxisStatus` | `GetAxisStatus(int axis)` |
| 设置轴参数 | `SetAxisParameter` | `SetAxisParameter(int axis, AxisParameter param)` |
| 等待运动完成 | `WaitForMotionComplete` | `WaitForMotionComplete(int axis, int timeoutMs)` |
| 多轴直线插补 | `MoveLinear` | `MoveLinear(int[] axes, double[] positions, double speed)` |

### 设备运行状态枚举规范

```csharp
/// <summary>
/// 设备运行状态枚举
/// </summary>
public enum DeviceRunningState
{
    /// <summary>设备未初始化</summary>
    Uninitialized,
    /// <summary>设备初始化中</summary>
    Initializing,
    /// <summary>设备就绪待机</summary>
    Ready,
    /// <summary>设备运行中</summary>
    Running,
    /// <summary>设备暂停</summary>
    Paused,
    /// <summary>设备报警</summary>
    Alarm,
    /// <summary>设备急停</summary>
    EmergencyStop,
    /// <summary>设备正在回零</summary>
    Homing,
    /// <summary>设备正在关机</summary>
    ShuttingDown
}
```

### 轴状态枚举规范

```csharp
/// <summary>
/// 单轴运行状态枚举
/// </summary>
public enum AxisState
{
    /// <summary>轴未使能</summary>
    Disabled,
    /// <summary>轴已使能待机</summary>
    Standby,
    /// <summary>轴正在运动</summary>
    Moving,
    /// <summary>轴回零中</summary>
    Homing,
    /// <summary>轴报警</summary>
    Alarm,
    /// <summary>轴正限位触发</summary>
    PositiveLimit,
    /// <summary>轴负限位触发</summary>
    NegativeLimit,
    /// <summary>轴回零完成</summary>
    HomeDone
}
```

### 轴控制参数结构规范

```csharp
/// <summary>
/// 单轴控制参数
/// </summary>
public struct AxisParameter
{
    /// <summary>轴号</summary>
    public int AxisId;
    /// <summary>轴名称</summary>
    public string AxisName;
    /// <summary>脉冲当量（mm/pulse）</summary>
    public double PulseEquivalent;
    /// <summary>最大速度（mm/s）</summary>
    public double MaxSpeed;
    /// <summary>加速度（mm/s²）</summary>
    public double Acceleration;
    /// <summary>减速度（mm/s²）</summary>
    public double Deceleration;
    /// <summary>回零速度（mm/s）</summary>
    public double HomeSpeed;
    /// <summary>回零偏移量（mm）</summary>
    public double HomeOffset;
    /// <summary>正软限位（mm）</summary>
    public double PositiveSoftLimit;
    /// <summary>负软限位（mm）</summary>
    public double NegativeSoftLimit;
    /// <summary>是否使能软限位</summary>
    public bool EnableSoftLimit;
}
```

### 运动控制事件规范

```csharp
/// <summary>
/// 运动完成事件参数
/// </summary>
public class MotionCompletedEventArgs : EventArgs
{
    /// <summary>轴号</summary>
    public int AxisId { get; set; }
    /// <summary>目标位置</summary>
    public double TargetPosition { get; set; }
    /// <summary>实际位置</summary>
    public double ActualPosition { get; set; }
    /// <summary>是否成功完成</summary>
    public bool Success { get; set; }
    /// <summary>错误信息</summary>
    public string ErrorMessage { get; set; }
    /// <summary>完成时间戳</summary>
    public DateTime Timestamp { get; set; }
}

/// <summary>
/// 设备状态变更事件参数
/// </summary>
public class DeviceStateChangedEventArgs : EventArgs
{
    /// <summary>上一状态</summary>
    public DeviceRunningState PreviousState { get; set; }
    /// <summary>当前状态</summary>
    public DeviceRunningState CurrentState { get; set; }
    /// <summary>状态变更原因</summary>
    public string Reason { get; set; }
    /// <summary>变更时间戳</summary>
    public DateTime Timestamp { get; set; }
}
```

### 雷赛控制卡API封装规范

#### 封装原则
- 所有雷赛控制卡原生API调用必须封装在 `MotionController` 类中
- 禁止在业务逻辑层直接调用雷赛DLL的P/Invoke方法
- 封装层负责错误码转换和异常处理

#### 错误码处理规范
```csharp
/// <summary>
/// 雷赛控制卡错误码转换
/// </summary>
private void CheckErrorCode(int errorCode, string operation)
{
    if (errorCode != 0)
    {
        string errorMessage = TranslateLeadshineError(errorCode);
        throw new MotionControlException($"运动控制操作失败 [{operation}]: {errorMessage} (错误码: {errorCode})");
    }
}
```

#### 轴使能与禁用规范
```csharp
/// <summary>
/// 使能指定轴
/// </summary>
public void EnableAxis(int axis)
{
    CheckErrorCode(LeadshineAPI.dmc_write_sevon_pin(_cardId, axis, 1), $"使能轴{axis}");
    _axisStates[axis] = AxisState.Standby;
}

/// <summary>
/// 禁用指定轴
/// </summary>
public void DisableAxis(int axis)
{
    CheckErrorCode(LeadshineAPI.dmc_write_sevon_pin(_cardId, axis, 0), $"禁用轴{axis}");
    _axisStates[axis] = AxisState.Disabled;
}
```

### 运动控制安全规范

#### 软限位检查
```csharp
/// <summary>
/// 运动前软限位检查
/// </summary>
private bool CheckSoftLimit(int axis, double targetPosition)
{
    var param = _axisParameters[axis];
    if (!param.EnableSoftLimit) return true;
    
    if (targetPosition > param.PositiveSoftLimit || targetPosition < param.NegativeSoftLimit)
    {
        OnMotionError?.Invoke(this, new MotionErrorEventArgs
        {
            AxisId = axis,
            ErrorMessage = $"目标位置 {targetPosition} 超出软限位范围 [{param.NegativeSoftLimit}, {param.PositiveSoftLimit}]"
        });
        return false;
    }
    return true;
}
```

#### 急停处理
```csharp
/// <summary>
/// 紧急停止所有轴
/// </summary>
public void EmergencyStop()
{
    // 立即发送急停指令
    LeadshineAPI.dmc_emg_stop(_cardId);
    
    // 更新所有轴状态
    for (int i = 0; i < _axisCount; i++)
    {
        _axisStates[i] = AxisState.Alarm;
    }
    
    // 更新设备状态
    ChangeDeviceState(DeviceRunningState.EmergencyStop, "触发急停按钮");
}
```

### 焊缝跟踪与自动对焦运动控制规范

#### 焊缝跟踪运动接口
```csharp
/// <summary>
/// 根据焊缝算法结果引导运动轴移动
/// </summary>
/// <param name="seamOffsetX">焊缝X方向偏移量（mm）</param>
/// <param name="seamOffsetY">焊缝Y方向偏移量（mm）</param>
/// <param name="trackingSpeed">跟踪速度（mm/s）</param>
public void TrackSeamPosition(double seamOffsetX, double seamOffsetY, double trackingSpeed)
{
    // 软限位检查
    double targetX = GetAxisPosition(0) + seamOffsetX;
    double targetY = GetAxisPosition(1) + seamOffsetY;
    
    if (!CheckSoftLimit(0, targetX) || !CheckSoftLimit(1, targetY))
        return;
    
    // 执行XY轴同步移动
    MoveLinear(new[] { 0, 1 }, new[] { targetX, targetY }, trackingSpeed);
}
```

#### 自动对焦运动接口
```csharp
/// <summary>
/// 根据自动对焦算法结果引导Z轴移动
/// </summary>
/// <param name="focusOffsetZ">Z方向对焦偏移量（mm）</param>
/// <param name="focusSpeed">对焦移动速度（mm/s）</param>
public void AdjustFocus(double focusOffsetZ, double focusSpeed)
{
    double targetZ = GetAxisPosition(2) + focusOffsetZ;
    
    if (!CheckSoftLimit(2, targetZ))
        return;
    
    MoveRelative(2, focusOffsetZ, focusSpeed);
}
```

### 设备流程控制规范

#### 状态机模式
```csharp
/// <summary>
/// 设备状态机 - 管理设备整体运行流程
/// </summary>
public class DeviceStateMachine
{
    private DeviceRunningState _currentState = DeviceRunningState.Uninitialized;
    
    /// <summary>设备状态变更事件</summary>
    public event EventHandler<DeviceStateChangedEventArgs> StateChanged;
    
    /// <summary>
    /// 状态转移
    /// </summary>
    public bool TransitionTo(DeviceRunningState newState, string reason = null)
    {
        if (!IsValidTransition(_currentState, newState))
            return false;
        
        var previousState = _currentState;
        _currentState = newState;
        
        StateChanged?.Invoke(this, new DeviceStateChangedEventArgs
        {
            PreviousState = previousState,
            CurrentState = newState,
            Reason = reason,
            Timestamp = DateTime.Now
        });
        
        return true;
    }
    
    /// <summary>
    /// 验证状态转移是否合法
    /// </summary>
    private bool IsValidTransition(DeviceRunningState from, DeviceRunningState to)
    {
        // 定义合法的状态转移矩阵
        switch (from)
        {
            case DeviceRunningState.Uninitialized:
                return to == DeviceRunningState.Initializing;
            case DeviceRunningState.Initializing:
                return to == DeviceRunningState.Ready || to == DeviceRunningState.Alarm;
            case DeviceRunningState.Ready:
                return to == DeviceRunningState.Running || to == DeviceRunningState.Homing || to == DeviceRunningState.ShuttingDown;
            case DeviceRunningState.Running:
                return to == DeviceRunningState.Paused || to == DeviceRunningState.Ready || to == DeviceRunningState.Alarm || to == DeviceRunningState.EmergencyStop;
            case DeviceRunningState.Paused:
                return to == DeviceRunningState.Running || to == DeviceRunningState.Ready || to == DeviceRunningState.Alarm;
            case DeviceRunningState.Alarm:
                return to == DeviceRunningState.Ready || to == DeviceRunningState.ShuttingDown;
            case DeviceRunningState.EmergencyStop:
                return to == DeviceRunningState.Uninitialized || to == DeviceRunningState.ShuttingDown;
            default:
                return false;
        }
    }
}
```

## 配置与数据管理

### 配置文件路径
- 使用 `AppDomain.CurrentDomain.BaseDirectory + @"\Config\"` 作为配置目录
- XML配置文件存放在 `Config` 文件夹下
- **运动控制配置文件**: `Config\MotionConfig.ini`

### 全局数据管理
- 使用静态类/单例模式管理全局状态和配置
- 示例:
```csharp
public sealed class PipelineManager
{
    private static readonly Lazy<PipelineManager> _instance = new Lazy<PipelineManager>(() => new PipelineManager());
    public static PipelineManager Instance => _instance.Value;
}
```

### 参数类设计模式
- 使用属性变更通知 `INotifyPropertyChanged`:
```csharp
public abstract class StageBase : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler PropertyChanged;
    protected void OnPropertyChanged([CallerMemberName] string name = null) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}
```
- 使用 `[Category]`, `[Description]`, `[DisplayName]` 等特性支持属性网格

## 特定技术栈规范

### HelixToolkit 3D渲染
- 使用 `HelixToolkit.SharpDX` 和 `HelixToolkit.Wpf.SharpDX` 命名空间
- 几何体类型: `PointGeometry3D`, `MeshGeometry3D`
- 模型类型: `PointGeometryModel3D`, `MeshGeometryModel3D`
- 使用 `Vector3Collection`, `Color4Collection`, `IntCollection`

### EmguCV 图像处理
- 使用 `Emgu.CV` 命名空间
- 图像类型: `Mat`
- 枚举映射到自定义处理逻辑

### SunnyUI
- WinForms 使用 `Sunny.UI.UIPage` 作为页面基类
- 控件命名保持简洁

### 雷赛控制卡运动控制
- 使用 `Leadshine` 命名空间或自定义封装层
- 运动控制API封装在 `MotionController` 类中
- 禁止业务层直接调用P/Invoke

## 代码格式细节

### 花括号
- K&R 风格（开括号在同一行）:
```csharp
public void LoadPointCloud(PointCloudData data, float pointSize = 2f)
{
    ClearAll();
    _currentData = data ?? throw new ArgumentNullException(nameof(data));
}
```

### 缩进
- 使用 4 个空格缩进

### 空行
- 方法之间保留一个空行
- 逻辑分组之间保留空行

### 类型别名
- 需要时使用 `using` 别名解决命名冲突:
```csharp
using MediaColor = System.Windows.Media.Color;
using WpfSize = System.Windows.Size;
```

### 字符串插值
- 优先使用 `$""` 字符串插值:
```csharp
throw new FileNotFoundException($"文件未找到: {filePath}");
```

#### 字符串插值中的格式化陷阱（强制）

**禁止**在 `$""` 插值表达式中使用冒号 `:` 进行 DateTime、TimeSpan 或数值格式化（如 `{expr:format}`），即使该语法在 C# 6.0+ 规范中是合法的。

**错误原因**：本项目使用较新的 .NET SDK 编译器编译 .NET Framework 4.8 目标，编译器会尝试使用 `DefaultInterpolatedStringHandler`（.NET 6+ 类型），但运行时目标框架中不存在该类型，导致回退机制异常，产生编译错误 CS1739（`AppendFormatted` 的最佳重载没有名为 `format` 的参数）。该问题是否触发取决于表达式复杂度和格式串内容，具有不确定性。

```csharp
// 错误写法 - 可能触发 CS1739 编译错误
string display = $"[{File.GetCreationTime(file):yyyy-MM-dd HH:mm:ss}] {fileName}";
string outputName = $"Recovered_{DateTime.Now:yyyyMMdd_HHmmss}";
```

**正确写法**：先将格式化结果提取为局部变量，再参与插值：

```csharp
// 正确写法
string timeStr = File.GetCreationTime(file).ToString("yyyy-MM-dd HH:mm:ss");
string display = $"[{timeStr}] {fileName}";

string timeTag = DateTime.Now.ToString("yyyyMMdd_HHmmss");
string outputName = $"Recovered_{timeTag}";
```

此规则适用于所有需要在插值内使用 `{expr:format}` 语法的场景，包括 `DateTime`、`TimeSpan`、数值等类型。

## 设计模式偏好

### 单例模式
- 使用 `Lazy<T>` 实现线程安全单例

### 静态工具类
- 纯工具方法使用 `static class`

### 流水线/阶段模式
- 使用阶段基类 + 具体阶段类的继承结构
- 每个阶段包含 `Enabled`, `Operation`, `Parameters` 属性

### 事件驱动
- 使用 `EventHandler<TEventArgs>` 模式进行模块间通信

#### 事件参数对象复用（强制）

**高频触发的事件参数（如每帧回调），必须在构造函数中创建并声明为类级字段，方法内只做属性赋值和事件触发，禁止在方法内 new 新对象。**

**原因**：事件参数对象在每次触发时 `new` 会产生不必要的 GC 压力，尤其在图像处理、点云采集等高频场景（每秒数十帧）中，频繁分配和回收 EventArgs 对象会显著影响性能。

```csharp
// 错误写法 - 每次调用都分配新对象，高频场景下产生大量GC压力
public Mat Execute(Mat src, double robotX = 0)
{
    // ... 处理逻辑 ...
    var completedArgs = new AlgorithmCompletedEventArgs(
        current, elapsedMs, success, errorMessage, stageResults, seamFeature)
    {
        RobotX = robotX
    };
    AlgorithmCompleted?.Invoke(this, completedArgs);
    return current;
}
```

```csharp
// 正确写法 - 构造函数中创建，Execute中只做属性赋值和事件触发
public class PipelineManager
{
    /// <summary>
    /// 算法完成事件参数（类级复用，避免每次Execute分配新对象）
    /// </summary>
    private AlgorithmCompletedEventArgs _completedArgs;

    private PipelineManager()
    {
        Config = new PipelineConfig();
        _completedArgs = new AlgorithmCompletedEventArgs();
    }

    public Mat Execute(Mat src, double robotX = 0)
    {
        // ... 处理逻辑 ...
        // 只做属性赋值，不创建新对象
        _completedArgs.ResultImage = current;
        _completedArgs.ElapsedMilliseconds = stopwatch.ElapsedMilliseconds;
        _completedArgs.Success = success;
        _completedArgs.ErrorMessage = errorMessage;
        _completedArgs.StageResults = stageResults;
        _completedArgs.SeamFeature = seamFeature;
        _completedArgs.RobotX = robotX;
        AlgorithmCompleted?.Invoke(this, _completedArgs);
        return current;
    }
}
```

**适用场景**：
- 图像算法每帧回调的 `EventArgs`
- 点云采集每帧回调的 `EventArgs`
- 焊接工艺每帧调整的 `EventArgs`
- 运动控制每帧位置反馈的 `EventArgs`
- 任何在循环或高频定时器中触发的事件参数

**不适用场景**：
- 低频事件（如按钮点击、配置变更）可使用局部变量
- 事件参数需要在多线程中同时传递时（每个线程需要独立实例）

## 文件头与using顺序

### using顺序
1. 系统命名空间
2. 第三方库命名空间
3. 项目内部命名空间

### 示例
```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using HelixToolkit.SharpDX;
using HelixToolkit.Wpf.SharpDX;
using PointCloudLibrary.Models;
using PointCloudLibrary.Rendering;
```

### LINQ 扩展方法强制引用（强制）

**所有使用 LINQ 扩展方法（如 `ToArray()`、`ToList()`、`FirstOrDefault()`、`Select()` 等）的文件，必须显式引用 `using System.Linq;`**。

**错误原因**：`IReadOnlyList<T>`、`IEnumerable<T>` 等接口本身不包含 `ToArray()` 等方法定义，这些方法由 `System.Linq.Enumerable` 提供为扩展方法。若缺少 `using System.Linq;`，编译器报错：

```
IReadOnlyList<Point3D> 未包含 ToArray 的定义，并且找不到可接受第一个 IReadOnlyList<Point3D> 类型参数的可访问扩展方法 ToArray（是否缺少 using 指令或程序集引用？）
```

**正确写法**：

```csharp
using System;
using System.Collections.Generic;
using System.Linq;  // 强制：使用 LINQ 扩展方法时必须引用

public static class SmartRayConverter
{
    public static Smartray.Api.Point3d[] ToSmartRayPoints(PointCloudData data, float transportResolution)
    {
        if (data == null)
            throw new ArgumentNullException(nameof(data));

        int count = data.PointCount;
        var points = new Smartray.Api.Point3d[count];

        // data.Points 为 IReadOnlyList<Point3D>，使用索引器访问无需 LINQ
        // 如需 ToArray()，则必须引用 System.Linq
        for (int i = 0; i < count; i++)
        {
            var pt = data.Points[i];
            points[i] = new Smartray.Api.Point3d { X = pt.X, Y = pt.Y, Z = pt.Z };
        }

        return points;
    }
}
```

**规则总结**：
- 生成代码时，若涉及 `ToArray()`、`ToList()`、`Where()`、`Select()`、`FirstOrDefault()` 等 LINQ 方法，**必须自动添加 `using System.Linq;`**
- 优先使用索引器访问 `IReadOnlyList<T>`（如 `data.Points[i]`），避免不必要的 `ToArray()` 调用
- `using System.Linq;` 属于**系统命名空间**，应排在 `using System;` 之后、第三方库之前

## 数值与数学运算

### 浮点比较
- 使用容差比较而非直接相等:
```csharp
if (normal.LengthSquared() < 0.0001f) continue;
if (zRange > 0.001f) { /* ... */ }
```

### 数学计算
- 使用 `System.Numerics.Vector3` 进行3D数学运算
- 自定义数学辅助类使用 `private static class` 嵌套

## 注意事项

1. **永远不要使用 C# 8.0+ 语法**，项目严格限制在 C# 7.3
2. **UI 页面必须三文件结构**（.cs + .Designer.cs + .resx）
3. **所有公共成员必须有中文 XML 文档注释**
4. **所有 SunnyUI 控件必须使用宋体 12 号字体**
5. **控件命名必须遵循前缀规范表**
6. **布局必须使用 TableLayoutPanel 实现自适应**
7. **事件处理方法命名必须为 `控件名_事件名` 格式**
8. **using 顺序：系统 → 第三方 → 项目内部**
9. **私有字段必须使用 `_camelCase` 命名**
10. **参数验证优先使用 `?? throw new ArgumentNullException(nameof(...))`**
11. **如需更新本 skill 规范，使用 `/updateskill` 唤醒自更新工作流**，系统将自动完成版本递增、备份保存和 trae 技能系统同步
12. **禁止在 `$""` 插值中使用冒号格式化**（如 `{dt:yyyy-MM-dd}`），该语法虽合法但在本项目编译环境下可能触发 CS1739 错误，必须先提取为局部变量再插值