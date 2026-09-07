---
name: "AdaWeldSystem UI开发专员"
version: "V6.260807.1034"
description: "负责所有用户界面的设计与实现（WinForms + AntdUI）、页面导航结构搭建、为各模块提供可视化交互界面。"
---

# UI 开发专员 Skill

## 描述

本 Skill 定义了 AdaWeldSystem 项目 UI 开发专员的职责边界、负责文件清单、技术要点和交付标准。

## 版本变更记录

| 版本 | 更新时间 | 变更级别 | 变更内容 |
|------|---------|---------|---------|
| V1.0 | 2026-06-23 | - | 初始版本。从原团队架构 skill 拆分独立。 |
| V2.260624.1450 | 2026-06-24 | 文件级 | 技术要点：新增"Dispose 方法唯一性检查"规范；交付标准：新增 Dispose 检查项 |
| V3.260624.1500 | 2026-06-24 | 文件级 | **修正 Dispose 规范**：明确 Designer.cs 的 Dispose() 不可修改；新增 DisposeComponents() 正确模式 |
| V4.260628.1542 | 2026-06-28 | 结构级 | 新增 ParamLaserPage 参数配置页面；LineLaserPage 职责调整为纯算法显示页面；ImagePage Tab 结构更新；新增页面拆分规范 |
| V5.260629.1614 | 2026-06-29 | 文件级 | **文件清单同步**：LineLaserPage → LLCamWorkJob，ParamLaserPage → LLCameraSetting（并迁移至 Sub3UI）；同步页面拆分规范、交付标准、协作关系中的文件引用 |
| V5.260630.1754 | 2026-06-30 | 文件级 | **新增控件生成方式规范**：明确 Designer.cs 静态定义与代码动态生成两种模式均合法；同步导航结构描述（相机设置按钮由 LLCamWorkJob 静态定义） |
| V5.260701.0930 | 2026-07-01 | 文档级 | **新增 UILight 控件使用规范**：明确 OnColor/OffColor/State 三要素，禁止误用 Enabled/Blink 等不存在属性 |
| V6.260807.1034 | 2026-08-07 | 结构级 | **UI 框架全面更新为 AntdUI**（与 ADR-021 同步）：技术栈 SunnyUI→AntdUI、页面基类 UIPage/UIForm→UserControl/AntdUI.Window、控件全面替换（Input/Table/Signal/GridPanel/Modal 等）；详见 LLMWiki wiki/modules/UIDesign.md 和 lessons/AntdUI-* 系列 |

### 版本命名规则

- 格式：`V{大版本}.{小版本}`
- **大版本**：结构级修改时+1
- **小版本**：日期格式`yyMMdd.HHmm`

---

## /updateskill：Skill 自更新工作流

### 执行步骤

#### 步骤1：读取当前 skill 文件

读取 `d:\AdaWeldSystem0623\AdaWeldSystem\Skills\UISpecialist.md` 的当前内容。

#### 步骤2：根据用户反馈确定更新内容

#### 步骤3：在最新版本上修改 skill

**重要原则**：
- 必须在最新版本上修改
- **版本号生成公式（强制执行）**：
  ```
  小版本 = 执行 PowerShell 命令 Get-Date -Format "yyMMdd.HHmm" 获取的当前系统时间
  ```
  **执行方式**：在 TRAE 沙盒中运行 `Get-Date -Format "yyMMdd.HHmm"`，将返回结果直接作为小版本号。严禁估算或手动填写。
- 修改后版本号按规则递增

#### 步骤4：保存 skill 备份

保存路径：`d:\AdaWeldSystem0623\AdaWeldSystem\Backup\Skills\UISpecialist_V{版本号}.md`

#### 步骤5：通知用户变更

---

## 核心职责

- 所有用户界面的设计与实现（WinForms + AntdUI，原 SunnyUI 已迁出，见 ADR-021）
- 页面导航结构搭建（MainWindow → ControlPage → TabPage → SubView，三级导航）
- 为算法/3D/相机/运动控制等模块提供可视化交互界面
- 控件布局、事件绑定、数据绑定
- 3D渲染区域集成（ElementHost + HelixToolkit）
- 响应式设计（GridPanel + Dock/Anchor 自适应布局）

## 负责文件清单

> **2026-08-07 更新**：UI 框架已从 SunnyUI 全面迁移至 AntdUI（ADR-021），目录结构和控件体系已全面变化。
> 完整最新文件清单和页面详情参见 LLMWiki `wiki/modules/UIDesign.md`，本处仅列核心文件。

```
UIDesign/
├── MainWindow/                      ← 主窗口
│   ├── FormMain.cs                  ← 主窗口（PageHeader + Menu + Tabs 导航框架）
│   ├── FormMain.Designer.cs
│   └── FormMain.resx
│
├── ControlPage/                     ← 控制页面
│   ├── MainPage.cs                  ← 首页/仪表盘（GridPanel 嵌套布局）
│   ├── NavPage.cs                   ← 统一导航页面（Menu + Tabs，实例化两次）
│   └── DataReviewerPage.cs            ← 数据回顾页面
│
├── TabPage/                         ← 功能 Tab 页
│   ├── LLCamWorkJob.cs              ← 线激光工作页面（核心）
│   ├── Helix3Drender.cs             ← 3D渲染页面（ElementHost 嵌 WPF）
│   ├── ParamConfigPage.cs           ← 参数配置页面
│   ├── XMLEditor.cs                 ← XML编辑器
│   ├── CommPage.cs                  ← 合并通讯页面（三选一模式）
│   ├── MonitorCamPage.cs            ← 监控相机页面
│   └── MotionControlPage.cs         ← 运控调整参数页
│
├── ViewPage/                        ← 视图子页
│   ├── EmguAlgoPage.cs              ← Emgu 算法编辑子页（UserControl）
│   └── ILAlgoForm.cs                ← 英莱算法编辑子页（UserControl）
│
└── SubDialog/                       ← 对话窗（Modal 承载的 UserControl）
                                      2026-09-07 由扁平 SubView/ 按业务域拆分为 5 个子目录，8 个类型改名；
                                      完整旧→新对照见 wiki/modules/UIDesign §「2026-09-07 目录与命名对照」
    ├── DataReviewerDialog/          ← 数据回溯域（FileTraceForm / HelixRenderForm / RecordConfigForm / RenderParamForm）
    ├── FormMainDialog/              ← 主窗口域（InitWaitingForm ← 原 InitWaitingPanel）
    ├── IntelligentLaserDialog/      ← 英莱域（ILAlgoForm / ILAlgorithmEditForm / ILParamForm / ILScanForm）
    ├── ParamContolDialog/           ← 参数控制域（AutoParamForm / ConfigForm）
    └── UserManagerDialog/           ← 用户管理域（LoginForm ← 原 FormLogin / UserEditForm ← 原 UserEdit）
```

## 技术要点

- 页面基类: `UserControl`（Tab 页/功能页）, `AntdUI.Window`（主窗口）, `AntdUI.Modal`（弹窗承载）
- 命名空间: `AdaWeldSystem.UIDesign.*`
- 布局: `AntdUI.GridPanel`（固定区域布局，替代可拖拽 Splitter）+ `Dock/Anchor` 自适应
- 控件: `AntdUI.Input`（文本输入）、`AntdUI.Table`（数据表格，代码后置 Binding）、`AntdUI.Signal`（状态灯）、`AntdUI.Checkbox/Switch`（复选/开关）
- 导航: `AntdUI.Menu`（左侧垂直导航）+ `AntdUI.Tabs`（Tab 内容区），通过 `SelectIndex` 双向联动
- 弹窗: `AntdUI.Modal.open(new Modal.Config(owner, title, form, TType.Info){...})` 承载 UserControl
- 3D 集成: `ElementHost` 承载 WPF `Viewport3DX`
- 设计器模式保护: 构造函数访问单例/硬件前先判 `LicenseManager.UsageMode == LicenseUsageMode.Designtime`

> **完整 AntdUI 开发范式**参见 LLMWiki `wiki/lessons/AntdUI-DesignParadigm.md`（布局/事件/Table/Designer.cs 铁律）。
> **迁移细节**参见 `decisions/ADR-021-UIFrameworkMigration` 和 `wiki/lessons/AntdUI-MigrationTracker.md`。

### 页面职责规范（LLCamWorkJob / LLCameraSetting）

**拆分原则**：算法作业显示与相机参数配置分离，职责单一。LLCameraSetting 为独立弹窗（SubView），不再与 LLCamWorkJob 共享 Tab 页。

| 页面 | 允许内容 | 禁止内容 |
|------|---------|---------|
| LLCamWorkJob（TabPage） | 图像显示框、手动分析按钮、Job号选择/CRUD、算法配置摘要、手动运行/停止按钮、工作流状态显示（Signal 状态灯） | 相机控制按钮、IP/Port输入、相机类型选择（相机设置由弹窗承载） |
| LLCameraSetting（SubView弹窗） | 左侧图像显示、右侧参数面板（相机类型/IP/Port/曝光/激光强度/激光模式）、10组预设加载/保存/切换、Open/ROI按钮 | — |

> 详细页面职责和开发范式参见 LLMWiki `wiki/modules/UIDesign.md`。

### 控件生成方式规范

**原则**：UI 控件的生成方式没有绝对限制，**Designer.cs 静态定义**与**代码动态生成**两种模式均合法，应根据具体场景选择最合适的方式。

| 生成方式 | 适用场景 | 优点 | 注意事项 |
|---------|---------|------|---------|
| **Designer.cs 静态定义**（推荐） | 布局固定、控件数量确定的页面 | 可视化设计、属性集中管理、设计器支持 | 必须确保 5 环节完整（字段→实例化→属性→事件→父容器） |
| **代码动态生成**（允许） | 运行时根据条件创建控件、列表项动态增减、跨页面注入共享控件 | 灵活性高、可根据运行时状态决定控件数量和内容 | 必须手动完成 5 环节等效操作，确保资源释放 |

**重要说明**：
1. **不禁止动态生成控件**：代码中通过 `new UIButton()` 等方式动态创建控件是完全允许的，尤其在需要运行时决定控件数量或内容的场景下
2. **跨页面控件注入允许但需谨慎**：如 [41] 中 ImagePage 向 LLCamWorkJob.panelRight 动态注入按钮的模式是合法的，但应评估是否会导致页面间耦合过高。如控件属于被注入页面的固有功能，优先在该页面自身的 Designer.cs 中静态定义
3. **动态生成的控件必须遵循相同的属性规范**：Cursor.Hand、MinSize=(1,1)、宋体12F 等标准同样适用于动态控件
4. **资源释放责任**：动态生成的控件如持有 IDisposable 资源（如 ImageBox、定时器等），必须在页面关闭或控件移除时显式释放

### 状态灯使用规范（AntdUI.Signal）

> **2026-08-07 更新**：原 SunnyUI `UILight` 已替换为 `AntdUI.Signal`（见 ADR-021、ADR-006 已 deprecated）。

`AntdUI.Signal` 为状态指示灯控件，用法与原 UILight 不同：

| 属性/方法 | 含义 | 典型值 |
|----------|------|--------|
| `Theme` | 灯的颜色主题 | `TType.Success`（绿色=正常）/ `TType.Error`（红色=错误）/ `TType.Info`（蓝色）等 |
| `Spin` | 是否闪烁 | `true` / `false` |

> 详细用法参见 LLMWiki `wiki/lessons/UILight-Property.md`（SunnyUI 时代旧规范）和 `wiki/modules/UIDesign.md`（AntdUI 现用法）。

### UI 控件完整性检查

新增或修改 UI 控件时，必须确认以下 **5 个环节**完整无缺：

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. 字段声明  │ → │  2. 实例化   │ → │  3. 属性设置  │ → │  4. 事件绑定  │
│  (Designer)  │    │(Designer.cs)│    │(Designer.cs)│    │ (Designer.cs) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
         ↑                                              ↓
         └──────────── 5. 加入父容器 ────────────────────┘
              (Designer.cs InitializeComponent)
```

### Dispose 方法规范（强制）

**背景**：WinForms 的 `partial class` 分为 `.cs`（业务逻辑）和 `.Designer.cs`（设计器生成）两个文件。`Dispose(bool)` 方法由设计器在 `.Designer.cs` 中自动生成。

**⚠️ 重要教训**：**Designer.cs 的 `Dispose(bool)` 不可修改**！修改后会导致 WinForms 设计器报错、界面显示异常。原始版本如下，必须保持原样：

```csharp
// Designer.cs 中的 Dispose —— 禁止修改！保持设计器生成的原始代码
protected override void Dispose(bool disposing)
{
    if (disposing && (components != null))
    {
        components.Dispose();
    }
    base.Dispose(disposing);
}
```

**检查规则**：
1. **Designer.cs 的 Dispose(bool) 禁止修改** —— 修改会导致 WinForms 设计器错误
2. **禁止在 .cs 业务逻辑文件中定义 `Dispose(bool)` 或 `Dispose()`** —— 会导致编译错误"类型已定义了一个名为 Dispose 的具有相同参数类型的成员"
3. **如需释放自定义资源**（如 IDisposable 字段：Viewport3DX、PointCloudViewer 等），必须在 `.cs` 中定义 `DisposeComponents()` 公共方法，由页面关闭时调用
4. **代码审查时必须检查**：
   - 搜索 `.cs` 文件中是否包含 `protected override void Dispose` 或 `public void Dispose`（禁止）
   - 确认 `.Designer.cs` 的 `Dispose(bool)` 未被修改（必须保持设计器原始代码）
   - 确认 `.cs` 中有 `DisposeComponents()` 方法释放自定义资源

**正确示例**（.cs 中的 DisposeComponents）：
```csharp
// .cs 业务逻辑文件中定义 DisposeComponents，由父页面关闭时调用
public void DisposeComponents()
{
    CurrentData?.Clear();
    _viewer?.Dispose();
    _viewport3DX?.Dispose();
    var effectsManager = _viewport3DX?.EffectsManager;
    if (effectsManager is IDisposable disposableEffectsManager)
    {
        disposableEffectsManager.Dispose();
    }
    _viewport3DX.EffectsManager = null;
    _viewport3DX?.Items?.Clear();
    elementHost1.Child = null;
    elementHost1.Dispose();
}
```

**错误示例 1**（修改 Designer.cs 的 Dispose —— 禁止）：
```csharp
// 禁止修改 Designer.cs 中的 Dispose！会导致设计器报错
protected override void Dispose(bool disposing)
{
    if (disposing)
    {
        _pointCloudViewer?.Dispose();  // ❌ 禁止在此处添加自定义释放逻辑
        _viewport3DX?.Dispose();       // ❌ 禁止修改 Designer.cs 的 Dispose
        components?.Dispose();
    }
    base.Dispose(disposing);
}
```

**错误示例 2**（在 .cs 中定义 Dispose —— 禁止）：
```csharp
// 禁止在 .cs 中定义 Dispose！会导致编译错误
protected override void Dispose(bool disposing)
{
    if (disposing)
    {
        _pointCloudViewer?.Dispose();
    }
    base.Dispose(disposing);
}
```

## 交付标准

- [ ] 所有页面继承正确的基类（UserControl / AntdUI.Window）
- [ ] 三文件结构完整（.cs / .Designer.cs / .resx）
- [ ] 控件命名符合规范
- [ ] 布局自适应（GridPanel + Dock/Anchor）
- [ ] 事件处理方法命名规范（控件名_事件名）
- [ ] 算法参数页面可正确绑定数据
- [ ] 3D页面正确集成 ElementHost + HelixToolkit
- [ ] 运动控制页面正确显示轴状态和参数
- [ ] **Designer.cs Dispose 不可修改**：必须保持设计器生成的原始代码，禁止添加自定义释放逻辑
- [ ] **.cs 中无 Dispose 定义**：禁止在业务逻辑文件中定义 Dispose(bool) 或 Dispose()
- [ ] **DisposeComponents 资源释放**：.cs 中必须定义 DisposeComponents() 公共方法，释放所有自定义 IDisposable 字段
- [ ] **AntdUI Table 代码后置**：Table 列定义和数据绑定在 .cs 中通过 Binding 实现，Designer.cs 只留外观和事件
- [ ] **Modal 弹窗模式**：对话框通过 `AntdUI.Modal.open(...)` 承载 UserControl，不用 Window 基类
- [ ] **Workflow 事件 InvokeRequired**：所有工作流事件处理必须检查 InvokeRequired

> 完整交付标准和开发铁律参见 LLMWiki `wiki/lessons/AntdUI-DesignParadigm.md`。

## 协作关系

| 协作对象 | 协作内容 | 数据接口 |
|----------|----------|----------|
| **图像算法专员** | 算法参数配置界面（LLCameraSetting）、算法效果预览（LLCamWorkJob）、Job 切换 UI | `PipelineManager.Instance`, `JobManager.Instance`, `AlgorithmManager` |
| **3D开发专员** | 3D点云/模型显示页面、交互控制 | `PointCloudViewer`, `PointCloudData` |
| **工业相机专员** | 相机连接状态显示、实时图像预览 | `CameraRun`, `SensorManager` |
| **运动控制专员** | 轴参数配置界面、运动状态显示 | `MotionController.Instance`, `DeviceStateMachine` |
| **通用技术专员** | 系统日志显示、TCP状态监控 | `GlobalCommData`, `Log` |
| **数据库专员** | 参数列表管理、权限登录界面 | `AuthManage`, `ConfigManage` |
| **架构开发员** | 页面结构设计、导航层级定义 | — |