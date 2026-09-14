---
title: UIDesign 模块 — UI界面
date: 2026-07-01
updated: 2026-08-28
tags: [模块, UI, WinForms, AntdUI]
source: raw/skills/02-Development/UISpecialist.md
---

# UIDesign 模块 — UI界面

> 全部用户界面的设计与实现。基于 WinForms + **AntdUI（MIT 许可）**，25 组页面/弹窗，三级导航结构。
> UI 框架已于 2026-07-28 从 SunnyUI 全量迁移至 AntdUI（25/25 文件），见 [[decisions/ADR-015-UIFrameworkMigration]]。
> **开发范式唯一权威**：[[guides/AntdUI-Reference]]（布局/事件/Table/Chart/Designer.cs 铁律；原 `新WIKI/UI/AntdUI-DesignParadigm.md` 已并入）。

## 核心文件

UIDesign/
├── MainWindow/                  ← 原 ParentUI/（2026-08-05 重命名）
│   ├── FormMain.cs              ← 主窗口（PageHeader + Segmented + Tabs 导航框架；构造函数同步初始化：配置加载 + 子页面全量实例化 + 设备初始化）
│   ├── FormMain.Designer.cs
│   └── FormMain.resx
├── ControlPage/                 ← 原 Sub1UI/（2026-08-05 重命名）
│   ├── MainPage.cs              ← 首页/仪表盘（**整页 AntdUI.GridPanel 三层嵌套**：外层 uiGridPanelMain「上 68% 顶端分栏 / 下 32% 日志 panelLog（AntdUI.Panel 包裹 AntdUI.Input）」；内层 uiGridPanel1「左 40% / 右 60%」，Padding=5；右格内层 uiGridPanel2「2×2 GridPanel 承载 4 个 AntdUI.Panel（panelChart2/3/4/5），每个 Panel 包裹一张 Chart（圆润边角+白底+阴影动画），Padding=5」；5 张 Chart 均嵌入 Panel（Dock=Fill 充满 Panel），后由 Panel 嵌入 GridPanel（Dock=Fill 充满单元格）；日志由 RichTextBox 改为 **AntdUI.Input**（Multiline+AutoScroll+ReadOnly）；全部不可拖动）；**英莱线激光轮廓（formsPlot1）ScottPlot Signal 模式**（2026-08-18，详见 [[decisions/ADR-035-LineLaserResponsibilitySplit]]）：固定 `double[1920]` 数组（`_contourSignalXs`=X/`_contourSignalData`=Y）+ `AddSignalXY` + `Refresh()`，订阅英莱相机 `ContourDataReady` 事件（`InvokeRequired` 跨线程封送），60Hz 全帧率刷新不节流；**2026-08-26 修复**：① FormMain.LoadNavAndPages 中显式调用 mainPage.AddContourLineChart() + AddNewDataLineChart() 初始化图表与事件订阅（此前方法定义但从未调用导致主界面轮廓空白）；② **X 轴用 `_contourSignalXs`（= 沿激光线物理坐标 Y，非等距）由 `AddSignalXY` 显式传入**，不再用 `SampleRate`/`OffsetX`（见 [[lessons/IntelligentLaser-Pitfalls]] §5.16）；③ **轴范围由校准框（四边基准）确定**（从 `CalibrationInfo` 四角点计算 Y/Z mm 范围，含负值，加 5% 边距，连接时锁定一次），无校准框时回退默认值；④ **叠加特征点散点**（AddScatter，红色实心圆 markerSize=8，HasValidResult 时显示 FeatureY/FeatureZ）；⑤ **锁定轴缩放平移**（Configuration 禁滚轮/拖拽 + 每帧 SetAxisLimits 双保险）
│   ├── NavPage.cs               ← 统一导航页面（替代 ImagePage/ParamPage，通过 LoadTabs() 接受不同子页配置，实例化两次分别作为参数界面和图形界面；左侧垂直 AntdUI.Menu 导航 + 右侧 Tabs 内容区，TabMenuVisible=false；Vertical 模式，BackActive=White，BackHover=Gray，Round=false）
│   └── DataReviewerPage.cs        ← 数据回顾页面（原 DataReview.cs，**2026-08-05 布局重构，2026-08-07 分页控件升级**：外层 uiTableLayoutPanel1（AntdUI.GridPanel）「左 25% panelLeft / 右 75% panelRight」；panelLeft 内嵌 uiGridPanelLeft「35px 日历 / fill 表格 / fill Pagination 分页 / 30px 页脚」；panelRight 内嵌 uiGridPanelRight「35px 复选框流式布局 / fill 图表 / 20px 进度标签 / 40px 滑块」；全部 GroupBox 替换为 AntdUI.Panel（白底+灰边框+阴影动画）；btnRenerView 以 Modal.open 弹窗展示 HelixRenderForm）
├── TabPage/                     ← 原 Sub2UI/（2026-08-05 重命名）
│   ├── ILCamPage.cs             ← **线激光/英莱相机工作页面（核心，已替代 LLCamWorkJob）**（完全使用英莱，替代线激光页面挂载；TableLayoutPanel + AntdUI.Panel/Button/Label/Select + Emgu ImageBox 显示轮廓 Mat；IP 输入(初始化读本地配置 `LoadSavedIp`) + 扫描按钮 + 连接 + 开激光/开相机 toggle + JOB select + 算法编辑按钮 + 参数编辑按钮 + 轮廓点/分析结果；**2026-08-17 新增「自动显示」AntdUI.Switch（默认关闭）**：用状态机 `LineLaserWorkflow.State` 判断自动运行中→禁用全部手动按钮、switch 控制轮廓刷新，空闲→恢复按钮；事件订阅放代码后置）；**2026-08-24 UI 状态刷新统一入口重构**：原 `UpdateConnectionUi`/`UpdateModeUi`/`SyncFromHardwareAfterConnect` 三碎片入口内联为 private `*Core` 方法，统一收敛到单入口 `RefreshUi(RefreshUiScope scope)`（`[Flags]` 枚举 Connection/Mode/Hardware 可组合，内置 InvokeRequired 封送），构造函数/btnConnect/工作流态回调/状态机态回调全部只调 `RefreshUi`；**2026-08-24 传感器控制精简**：启停传感器改用 `SetSensor`、弃 `SetCaptureCamera`（非线激光方式），激光/传感器按钮 text 与 `ExtraMouseDown` 收敛到单一 `UpdateLaserSensorUi()`（基于 `IsLaserOn()`/`IsCameraOn()` 真相源，移除 `_isLaserOn`/`_isCameraOn` 本地副本），消除 btnLaser/btnCaptureCamera/SyncFromHardware/UpdateConnectionUi 四处重复 set text
│   ├── ParamConfigPage.cs       ← **2026-08-07 GridPanel+FlowPanel改造**：两列布局（42% / 58%），左列5行（参数列表+焊丝参数+板材焊缝类型+操作按钮），右列2行（基础参数+公式设置），全部 AntdUI.Panel 包裹；6 个表单区 TableLayoutPanel 已替换为 AntdUI.FlowPanel（label+input 自动流式排列，Gap=8，左对齐）
│   ├── FileEditorPage.cs        ← **2026-08-07 GridPanel改造 + 重命名**（原 XMLEditor）：两行布局（35px状态栏 / fill内容区），内容区左右分栏（320px文件树 / fill编辑器），文件树区含45px工具栏
│   ├── CommPage.cs              ← 合并通讯页面（三选一模式：机器人/通用/PLC，GridPanel 四行布局：Radio→Tabs→Checkbox→Input，见下方 CommPage 章节）
│   ├── MonitorCamPage.cs        ← 监控相机页面（焊前对中/焊中质检 + 右侧内联算法参数）
│   └── MotionControlPage.cs     ← **2026-08-07 GridPanel+FlowPanel改造**：两行布局（65% / 35%），上行两列（标定参数面板+模拟测试面板），下行运动轴参数面板；3 个表单区 TableLayoutPanel 已替换为 AntdUI.FlowPanel（label+input 自动流式排列，Gap=8，左对齐）
└── SubDialog/                   ← 对话窗（Modal 承载的 UserControl，见 [[decisions/ADR-016-DialogWindowToModalUserControl]]）
                                   **2026-09-07 目录重构**：原扁平 `SubView/`（含 ViewPage/ 前身）按**业务域**拆分为 5 个子目录，
                                   同批 8 个类型改名（见文末「2026-09-07 目录与命名对照」）。**命名空间已于 2026-09-14 随目录对齐（ADR-048）**：`ControlPage` / `TabPage` / `MainWindow` / `SubDialog.<业务域>` 各自独立命名空间。
    ├── DataReviewerDialog/      ← 数据回溯域（命名空间 AdaWeldSystem.UIDesign.SubDialog.DataReviewerDialog）
    │   ├── FileTraceForm.cs     ← 文件追踪弹窗（UserControl；2026-08-14 由 GroupBox+ListBox 改为 Label+AntdUI.Table：两个 Label 显示原 groupbox 标题「正常记录文件/临时文件（异常保留）」，表头 No.+选取(ColumnCheck 单选)+文件名；单选互斥范式见 [[guides/AntdUI-Reference]]）
    │   ├── HelixRenderForm.cs   ← Helix 3D 渲染子视图（原 TabPage/Helix3Drender，2026-08-07 迁入并改名；ElementHost 嵌 WPF 点云渲染；2026-08-13 移除「记录配置」按钮 `btnRecordConfig`，该入口迁至 DataReviewerPage.BtnRecordSetting）
    │   ├── RecordConfigForm.cs  ← 记录配置弹窗（UserControl）
    │   └── RenderParamForm.cs   ← 渲染参数弹窗（UserControl）
    ├── FormMainDialog/          ← 主窗口域（命名空间 AdaWeldSystem.UIDesign.SubDialog.FormMainDialog）
    │   └── InitWaitingForm.cs   ← 初始化等待面板（原 `InitWaitingPanel`，2026-09-07 改名；FormMain 初始化期间以 Modal 展示，事件触发自动关闭）
    ├── IntelligentLaserDialog/  ← 英莱线激光域（命名空间 AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog）
    │   ├── ILAlgoForm.cs        ← **英莱算法参数编辑子页**（原 `ILAlgoPage`，2026-09-07 改名；UserControl，由 ILAlgorithmEditForm 承载；2026-08-07 GridPanel改造：三行布局（45px工具栏 / fill参数区 / fill结果区），左右分栏（左参数面板350px / 右结果区），结果区40px标题栏+fill图像区；**2026-08-24 状态精简**：删除 `_ilConnected` 本地缓存，连接判断与标签统一直读 `_ilCamera.IsConnected` 真相源；**2026-08-24 Job 流面板重构**：顶部 JOB 按钮流+切换/新建/删除操作+参数表+接头类型显示）
    │   ├── ILAlgorithmEditForm.cs ← 算法编辑弹窗（原 `AlgorithmEditForm`，2026-09-07 改名；UserControl + AntdUI.Tabs + UserControl 子页，Modal 承载；见 [[api/ILAlgorithmEditForm]]）
    │   ├── ILParamForm.cs       ← **英莱相机参数编辑页**（原 `ILParamPage`，2026-09-07 改名；UserControl + AntdUI.Table 单元格编辑，Modal 承载；表头 参数名/当前值(SetEditable+DoubleClick)/单位/说明；编辑**相机参数**：曝光/激光强度/抗弧光，复用 [[api/IntelligentLaserCam]] 的 FetchCameraParams/ApplyCameraParams；**与 Job 参数（算法参数）分离**）；**2026-08-24 状态精简**：删除 `_ilConnected` 本地缓存，`UpdateConnLabel`/`LoadParams`/按钮守卫统一直读 `IsConnected` 真相源
    │   └── ILScanForm.cs        ← **英莱相机扫描结果弹窗**（原 `ILScanDialog`，2026-09-07 改名；UserControl + AntdUI.Table，Modal 承载；表头 No.+选取(ColumnCheck 单选互斥)+IP+序列号+软件版本+传感器类型；`SelectedIp` 属性 + 确定回填；见 [[guides/AntdUI-Reference]]）
    ├── ParamContolDialog/       ← 参数控制域（命名空间 AdaWeldSystem.UIDesign.SubDialog.ParamContolDialog）
    │   ├── AutoParamForm.cs     ← 自动参数弹窗（UserControl）
    │   └── ConfigForm.cs        ← 系统配置弹窗（UserControl + AntdUI.Table + AntdUI.Pagination，Modal 承载；2026-08-12 InitTableColumns 设 `AutoSizeColumnsMode=ColumnsMode.Fill` 列宽填满区域）
    └── UserManagerDialog/       ← 用户管理域
        ├── LoginForm.cs         ← 登录弹窗（原 `FormLogin`，2026-09-07 改名；UserControl，Modal 承载；命名空间 AdaWeldSystem.UIDesign.SubDialog.UserManagerDialog；见 [[guides/AntdUI-Reference]]）
        └── UserEditForm.cs      ← 用户编辑弹窗（原 `UserEdit`，2026-09-07 改名；UserControl + AntdUI.Table；命名空间 AdaWeldSystem.UIDesign.SubDialog.UserManagerDialog）

> ❌ **已从本目录移除（仅沿革）**：`EmguAlgoPage.cs`（原项目算法 EmguALG 编辑子页，职责并入 `ILAlgoForm.cs`，ILAlgorithmEditForm 当前只挂 ILAlgoForm）、`LLCameraSetting.cs`（原线激光相机设置，职责现由 `ILParamForm.cs` 承担）。

## 页面继承关系（AntdUI 迁移后）

| 层级 | 基类 | 用途 |
|------|------|------|
| ControlPage / TabPage 页面 | `UserControl` | 功能页面（由 FormMain 的 AntdUI.Tabs 承载，`AddTabSelect`） |
| SubDialog 对话窗（13 个，散布于 5 个业务子目录） | `UserControl` | **Modal 承载的对话窗**（无 PageHeader）；由调用点 `AntdUI.Modal.open(new Modal.Config(owner,标题,form,TType.Info){CloseIcon=true,BtnHeight=0})` 弹出；命名空间已随目录对齐为 `AdaWeldSystem.UIDesign.SubDialog.<业务域>`（ADR-048），见 [[decisions/ADR-016-DialogWindowToModalUserControl]]、[[guides/AntdUI-Reference]]。内部以注入的 `private readonly Window Window`（`XxxForm(Window _window)` 构造，复刻 AntdUI demo SystemSet 模式）作 `Message`/嵌套 `Modal` 的 owner（不用 `this.FindForm()`），关闭仍用 `this.FindForm().DialogResult` |
| FormMain | `AntdUI.Window` | 主窗口（PageHeader + Segmented + Tabs 导航框架，Segmented 替换原 Menu） |
| 算法编辑子页 EmguAlgoPage（已移除）/ ILAlgoForm | `UserControl` | 由 ILAlgorithmEditForm（SubDialog/IntelligentLaserDialog，Modal 承载）的 AntdUI.Tabs 承载 |

## 常用控件对照（迁移后现状）

| 用途 | 控件 | 说明 |
|------|------|------|
| 文本输入 | `AntdUI.Input` | 原 UITextBox/UIIPTextBox |
| 下拉选择 | `AntdUI.Select` | `SelectedIndexChanged` → `IntEventArgs` |
| 复选/开关 | `AntdUI.Checkbox` / `AntdUI.Switch` | `CheckedChanged` → `BoolEventArgs` |
| 数据表格 | `AntdUI.Table` + `AntList<T>` | 见 [[guides/AntdUI-Reference]]；禁用 DataGridView |
| 状态灯 | `AntdUI.Signal` | 原 UILight（[[project/SunnyUI-Legacy]] 已被取代） |
| 日期选择 | `AntdUI.DatePicker` | 原 UICalendar |
| 图表 | `ScottPlot.FormsPlot`（4.1.74） | **2026-08-12 由 `AntdUI.Chart` 全面替换**；**2026-08-13 上午升级 5.1.59、下午回退 4.1.74**（5.x 基于 SkiaSharp 对 .NET 4.8 设计器不友好），4.1 语法 `Plot.AddScatter(xs, ys, ...)`/`AxisAuto()`/`SetAxisLimits()`/`Legend()`/`Refresh()`；`Configuration.DpiStretch=false` 防高 DPI 字体锯齿；**无需 SkiaSharp/OpenTK/System.ValueTuple**（见 [[guides/Project-Tools]]） |
| 网格布局（可选） | `AntdUI.GridPanel` | **可选布局容器**（[[decisions/ADR-019-LayoutContainerFreedom]] 解除强制使用，因会强制排序）；按需选用。若使用：`Span` 定义行列（值仅 `fill`/`%`/整数/浮点，`px`/`auto` 非法），子控件单参数 `Controls.Add` 且按**逆序**入格；见 [[guides/AntdUI-Reference]]、[[guides/AntdUI-Reference]] |
| 流式布局（可选） | `AntdUI.FlowPanel` | **可选布局容器**（[[decisions/ADR-019-LayoutContainerFreedom]] 解除强制使用，因会强制排序）；按需选用。若使用：`Align=TAlignFlow.Left` 左对齐 + `Gap=N` 控件间距 + `Padding` 内边距 + `AutoScroll` 自动滚动；`TAlignFlow` 枚举：Left/LeftCenter/Center/RightCenter/Right；子控件通过 `Controls.Add` 按顺序添加，自动从左到右排列并换行；表单布局统一 label 宽 140px + input 宽 160px + 行间距由 Gap 控制；见 [[guides/AntdUI-Reference#flowpanel-表单布局]] |
| 消息/对话框 | `AntdUI.Message.*`（Toast，非阻塞）/ `AntdUI.Modal.open(new Modal.Config(owner,"标题","内容"){Icon=TType.*,Draggable=true})`（模态可拖拽） | 原 UIMessageBox；**`Message` 的 owner 类型为 `AntdUI.Target`**（`Window`/`Form` 类可传 `this`，`UserControl` 须传 `Form.ActiveForm`/`(Target)null`/`this.FindForm()`，不可裸 `null` 否则 CS0121）；**`Modal` 的 owner 为 `Control`/`IWin32Window`**（官方 Demo 直接 `Config(window,…)`，裸 `null` 不二义，但锚定父窗体建议 `Form.ActiveForm`/`this.FindForm()`）。详见 [[guides/AntdUI-Reference]] |
| 主题 | `AntdUI.Config.IsLight` 等 | 原 UIStyles.SetStyle(Purple)（[[project/SunnyUI-Legacy]] 已废弃） |

## 技术要点

- 控件优先在 Designer.cs 静态定义；`InitializeComponent()` 禁流程控制语句
- 所有 Workflow 事件处理必须检查 `InvokeRequired`（[[guides/WinForms-UI-Threading]]）
- 事件直接订阅 `control.Event += handler`，禁止 `new EventHandler()` 包装 AntdUI 自定义事件（范式 §二）
- 使用 AntdUI.FlowPanel 实现表单流式布局（替代 TableLayoutPanel）——**可选**，见 [[decisions/ADR-019-LayoutContainerFreedom]]
- 3D渲染通过 ElementHost 嵌入 WPF 控件
- FileEditorPage 用 `AntdUI.Select`（`_configSelector`）下拉承载全部通讯 XML 配置入口（服务器/客户端/发送/接收/RSI/EKI），不在 Designer.cs 中定义 MenuStrip；原「打开」按钮（OpenFileDialog）已弃用
- **WinForms 设计器模式保护**：构造函数访问单例/硬件/配置前先判 `LicenseManager.UsageMode == LicenseUsageMode.Designtime`，见 [[guides/WinForms-Designer]]
- 主窗口布局：`PageHeader(Dock=Top, ShowButton=true)` + `Segmented(Dock=Top, 图标+文本)` + `Tabs(Dock=Fill)`；`ControlBox=false`；按钮加到 `PageHeader.Controls`。顶部导航已由 `AntdUI.Segmented` 替代原先的 `AntdUI.Menu`，通过 `SelectIndex` 与 `Tabs.SelectedIndex` 双向联动（`bool syncing` 重入守卫）。SegmentedItem 不支持 `Visible`，权限显隐用 `Items.Remove/Add`。见 [[guides/AntdUI-Reference#Segmented-导航模式]]。
- ~~所有 `AntdUI.Window` 弹窗统一顶部 `PageHeader`~~：**已废弃**。2026-07-30 经 `ADR-019` 改为「**Modal 承载的 `UserControl`**」——8 个对话窗（原 Sub2 UserEditForm + Sub3 全部 7 个）迁入 `SubView/`，基类改 `UserControl`，取消 PageHeader，由调用点 `AntdUI.Modal.open(new Modal.Config(owner,标题,form,TType.Info){CloseIcon=true,BtnHeight=0})` 弹出。详见 [[guides/AntdUI-Reference]]（旧 PageHeader 范式见 [[guides/AntdUI-Reference]]，已标记废弃）

## 各页面要点（迁移后）

### CommPage（UIDesign.TabPage，UserControl，2026-08-06 改造，2026-08-07 顺序修复+模式增强）
合并通讯页面（三选一模式）。布局：**`AntdUI.GridPanel` 四行**（Span="fill;fill;fill;fill;-5% 30% 5% 60%"）：
- **行0（5%）**：`panelRadio` 承载三个 `AntdUI.Radio`（机器人通讯/通用通讯/PLC通讯）+ `btnKeepConfig` 保存按钮
- **行1（30%）**：`tabsSettings`（`AntdUI.Tabs`，`TabMenuVisible=false`，Size=1208×292）承载三个 TabPage（`tabRobot`/`tabGeneral`/`tabPLC`），跟随 Radio 选中自动切换
- **行2（5%）**：`chkShowCommLog`（`AntdUI.Checkbox`，INI 持久化控制 `_isLogVisible`）
- **行3（60%）**：`inputLog`（`AntdUI.Input`，Multiline+ReadOnly，5000 字符截断防溢出，自动滚动到底部）

三个 TabPage 均使用 `System.Windows.Forms.GroupBox` 组织配置字段，每个 TabPage 的内部 Panel 设置了 `AutoScroll=true`，GroupBox 设置了 `Anchor=Top|Left|Right` 水平拉伸，确保内容可滚动且自适应宽度。**TabPage Size 统一为 (1208, 292)，Panel Size 统一为 (1208, 292)，控件 X 坐标统一为 15，有效区域 1200×290**（见 [[guides/AntdUI-Reference]]）：
- **tabRobot**：`chkEnableRobot`（(15,8) 启用开关）+ `lblRobotCommMode` + `radioModeRSI`/`radioModeEKI`（通讯模式二选一，INI 持久化 `CommunicationManager.RobotCommMode`）+ `grpRobotConfig`（(15,38), Size=(1170,100) GroupBox "机器人配置"）内含类型/IP/端口字段 + RSI启动/EKI连接/断开按钮
- **tabGeneral**：`chkEnableGeneral`（(15,8) 启用开关）+ `grpServer`（(15,38), Size=(580,82) TCP服务端 IP/端口/启停按钮）+ `grpClient`（(605,38), Size=(580,82) TCP客户端 IP/端口/连接/断开按钮）+ 发送消息栏（`txtSend` (15,130), Size=(1080,29) 水平拉伸，`btnSend` (1100,128) 右对齐）
- **tabPLC**：`chkEnablePLC`（(15,8) 启用开关）+ `grpPLCConfig`（(15,38), Size=(1170,175) GroupBox "PLC 配置"）内含类型/IP/机架/插槽字段 + 连接/断开/生成GSDML按钮

三模式：机器人（KUKA RSI/EKI 二选一）、通用TCP（服务端+客户端）、PLC（S7/Profinet）。每个模式有独立的 `chkEnable*` 开关（`AntdUI.Checkbox`，INI 持久化 `CommunicationManager.IsPlcEnabled/IsRobotEnabled/IsGeneralEnabled`），启用后才能配置。Radio→Tabs 双向联动（`OnRadioModeChanged`→`tabsSettings.SelectedIndex`，`OnTabsSelectedChanged`→反写 Radio）。`DisposeComponents()` 释放 `KUKARobotManager` 和事件订阅。

**机器人通讯模式（RSI/EKI 二选一）**：`CommunicationManager.RobotCommMode`（`RobotCommModeType` 枚举：RSI=0/EKI=1）INI 持久化；`DeviceControlWork.InitializeMachine()` 根据配置模式只启动对应通道，运行线程断线重连同理。未启用机器人通讯时完全跳过初始化。

### FileEditorPage（UIDesign.TabPage，UserControl，原 XMLEditor）
文件编辑器页面（2026-08-07 由 XMLEditor 重命名）。编辑 Server/Client/Send/Recive 四种通讯 XML + KUKA RSI/EKI 配置。左侧 `AntdUI.Tree` 文件树 + 右侧 `AntdUI.Table` 属性编辑双面板（2026-08-12 由原生 WinForms PropertyGrid 改为 AntdUI.Table）。**2026-08-12 改造（两轮）**：① 配置入口由动态 MenuStrip 改为 `AntdUI.Select`（`_configSelector`，含服务器/客户端/发送/接收/RSI/EKI 六项，RSI/EKI 文件缺失时经 `KUKAXMLConfig.SaveRSIConfig/SaveEKIConfig` 生成默认配置）；② 右侧属性编辑由 `PropertyGrid` + `ICustomTypeDescriptor` 改为 **`AntdUI.Table` 单元格编辑**（`_xmlPropertyGrid`）：`InitPropertyGridTable()` 代码后置设 `EditMode=TEditMode.DoubleClick` + 双列（`Name`「属性」只读 / `Value`「值」可编辑）+ `Binding(AntList<XmlPropertyRow>)`；行模型 `XmlPropertyRow` 字段 `Name`/`Value`/`AttributeName`/`IsElementName`/`IsElementValue`/`IsReadOnly`；`LoadNodeToTable` 每行对应「元素名称/元素值/每个 XML 属性/统计（只读）」，`XmlTable_CellEndEdit` 校验后写回 XML（属性→`XAttribute.Value`、元素值→`_currentElement.Value`、元素名→非空且不以数字开头，改后经 `FindTreeNode` 刷新树节点显示文本）。**2026-08-12 二轮（本次）表格联动**：① Designer.cs 订阅 `_xmlTreeView.SelectChanged`（`AntdUI.TreeSelectEventHandler` → `XmlTreeView_SelectChanged`），点击左侧树节点即取 `_nodeToXml[e.Item]` 更新 `_currentElement` 并调 `LoadNodeToTable` 刷新右侧表格（表头=`Name` 属性、表格内=`Value` 值）；② 新增 `SelectFirstNode()`——`LoadDocument` 加载完成后自动选中根节点并加载属性，避免打开文档后表格空白；`InitPropertyGridTable` 已设 `AutoSizeColumnsMode=ColumnsMode.Fill` 使列宽填满区域。关键方法：`LoadDocument` / `LoadXdocument` / `AddNodesRecursively` / `InitConfigSelector` / `ConfigSelector_SelectedIndexChanged` / `LoadKUKARobotConfig` / `InitPropertyGridTable` / `SelectFirstNode` / `XmlTreeView_SelectChanged` / `LoadNodeToTable` / `XmlTable_CellEndEdit` / `FindTreeNode`。

### MonitorCamPage（`AdaWeldSystem.UIDesign.TabPage`，UserControl）
焊前对中/焊中质检。Live 预览（`chkLive`）、阶段选择（`cmbPhase`，`AntdUI.Select`）、单次/连续/停止按钮；状态显示 `lblStatus`（`AntdUI.Label`）+ `uiLightStatus`（**`AntdUI.Signal`**）。右侧 `panelRight` 内联算法参数（容差/合格分，`MonitorAlgorithmManager` 读写 `Config/INI/MonitorAlgorithm.ini`，见 [[decisions/ADR-012-MonitorCamPage-AlgorithmInline]]）。订阅 MonitorCameraWorkflow 五大事件全部 `InvokeRequired` 守卫；`DisposeComponents()` 模式，未重写 `Dispose(bool)`。

### DataReviewerPage（`AdaWeldSystem.UIDesign.ControlPage`，UserControl，2026-08-05 布局重构，2026-08-07 分页升级 + 3D弹窗）
离线回溯生产数据：**布局已全面标准化**——外层 `uiTableLayoutPanel1`（AntdUI.GridPanel）「左 25% `panelLeft` / 右 75% `panelRight`」；`panelLeft` 内嵌 `uiGridPanelLeft`（Span="35:fill;fill;30:fill;30:fill"）「35px `uiCalendar1`（**`AntdUI.DatePicker`**）/ fill `uiDataGridView1`（**`AntdUI.Table`**）/ fill `pagination1`（**`AntdUI.Pagination`**，2026-08-07 替换原自建 btnPrev/btnNext/lblPageInfo；PageSizeOptions=[20,50,100,200]，ShowSizeChanger=true，ValueChanged 事件驱动 FillPage 刷新表格）/ 30px `uiDataGridViewFooter1`（统计标签）」；`panelRight` 内嵌 `uiGridPanelRight`（Span="35:fill;fill;20:fill;40:fill"）「35px `uiFlowLayoutPanel1`（4 个 `AntdUI.Checkbox` 复选框）/ fill `uiLineChart2`（**`AntdUI.Chart`**）/ 20px `uiSymbolLabel1`（进度文本）/ 40px `uiTrackBar1`（**`AntdUI.Slider`**）」。全部 GroupBox 替换为 `AntdUI.Panel`（白底+灰边框 `BorderColor=217,217,217`+阴影动画 `Shadow=5,ShadowOpacity=0.2`）。`RunRecordManager` 按 `yyyyMMdd` 子目录枚举 `.pDat` → 表格列表 → 图表渲染焊缝宽度/速度/送丝/激光功率曲线 + 调整点。⚠️ Chart 数据填充逻辑当前为 TODO（等 VS 确认 AntdUI.Chart 数据 API），曲线暂无数据。目录缺失/空目录经 `AntdUI.Modal`/`Message` 提示。

**btnRenerView（3D数据回溯按钮）**：点击后以 `AntdUI.Modal.open` 弹窗形式展示 `HelixRenderForm`（Modal 承载的 `UserControl`，900×600，MaskClosable=true，CloseIcon=true）。

**BtnRecordSetting（记录设置按钮，2026-08-13 接入）**：点击后以 `AntdUI.Modal.open` 弹窗形式展示 `RecordConfigForm`（记录配置：临时/保存路径 + 混淆选项）。原 `HelixRenderForm` 的「记录配置」按钮（`btnRecordConfig`）已移除，此入口迁至本页底部按钮。

### MotionControlPage（`AdaWeldSystem.UIDesign.TabPage`，UserControl，设计器生成）
三大参数组（**AntdUI.FlowPanel** 流式布局，无 Tab）：① 标定数据（`flowPanelCalib`，6 组 label+input + 保存按钮，写 `MoveControlData.Instance`）② 模拟测试参数（`flowPanelSim`，5 组 label+控件 + checkbox + 2 按钮，写 `MotionControlWorkflow` + `VirtualCameraRun`）③ 运动轴参数（`flowPanelAxis`，2 个 label 占位）。FlowPanel 配置：`Align=TAlignFlow.Left`、`Gap=8`、`Padding=(10,4,10,4)`、`Dock=Fill`；Label 统一宽 150px+高 34px+MiddleLeft，Input 统一宽 160px+高 32px。`BtnStartSim_Click` 启停模拟流程；`OnLineLaserStateChanged` 经 `InvokeRequired` 守卫方法更新 UI。详见 [[api/MotionControlPage]]。

### ILAlgorithmEditForm（`AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog`，UserControl，Modal 承载）
算法编辑弹窗：`tabsAlgo`（**`AntdUI.Tabs`**）按 `CameraSelector.Active` 接口 `AddTabSelect` 挂载 `ILAlgoForm`（⚠️ 原 `EmguAlgoPage` 分支已随文件移除，当前仅英莱一页）（英莱 Job Parameter 编辑 + 实时识别结果只读）。接口分隔决策见 [[decisions/ADR-014-AlgorithmEditInterfaceSplit]]（框架层描述已按 AntdUI 落地）。2026-07-30 经 `ADR-019` 由 `AntdUI.Window` 改为 `UserControl` 并迁入 `SubView/`，调用点 `ILCamPage.btnEditJob_Click`（原 `LLCamWorkJob`）以 `AntdUI.Modal.open(...)` 弹出；原 `FormClosing` 停英莱页定时器逻辑改订阅 `HandleDestroyed`（不重写 `Dispose(bool)`）。详见 [[api/ILAlgorithmEditForm]]。

### ILCamPage（`AdaWeldSystem.UIDesign.TabPage`，UserControl，已替代 LLCamWorkJob）
线激光/英莱相机工作核心页：IP 输入+扫描+连接、开激光/开传感器按钮、Job 下拉+应用按钮、帧率模式下拉+应用按钮、算法编辑按钮、参数编辑按钮、轮廓画面+分析结果表。**已完全替代原 `LLCamWorkJob`**（Sub2UI 时代线激光页面，文件已改名并迁至 `UIDesign/TabPage/ILCamPage.cs`）。Workflow 事件全部 `InvokeRequired` 守卫。详见 [[lessons/IntelligentLaserSensorControl]]。

### AutoParamForm（`AdaWeldSystem.UIDesign.SubDialog.ParamContolDialog`，UserControl，Modal 承载）
自动参数弹窗（命名空间 `AdaWeldSystem.UIDesign.SubDialog.ParamContolDialog`）：表格 `uiDataGridView1`（**`AntdUI.Table`**，InitTableColumns 代码后置 + `Binding(AntList<AutoParamRow>)`）；原头部 `ToolStrip`（`labelK`/`LabelJ`/`labelM` 三标签 + `btnSave` 保存）已迁移为 `AntdUI.FlowPanel`（Dock=Top）承载 3×`AntdUI.Label` + `lblSpacer`（`Dock=Fill` 弹性占位右推）+ `AntdUI.Button`（`btnSave`，保留保存功能）；K/J/M 文本在 `LoadConfigData` 中赋值。**2026-08-12 表格可编辑 + 列宽填满**：`InitTableColumns` 设 `EditMode=TEditMode.DoubleClick`（双击进入编辑）+ 可编辑列（焊接速度/送丝速度/焊接功率）经 `.SetEditable(true)` 开启 + `AutoSizeColumnsMode=ColumnsMode.Fill` 列宽填满区域；构造函数订阅 `CellEndEdit` → `uiDataGridView1_CellEndEdit`，按 `e.Column.Key` 将编辑值写回 `AutoParamRow` 对应属性，`btnSave_Click` 经 `UpdateParamValues` 落库（`RobotSpeed`/`FeedSpeed`/`LaserPower` 用 `CultureInfo.InvariantCulture` 解析回写字典）。迁移范式见 [[guides/AntdUI-Reference]]。

### MainPage 硬件快捷开关（AntdUI ButtonShadow 常驻按钮，ADR-025；2026-08-31 风格迭代）

`MainPage` 使用 **AntdUI `ButtonShadow` 常驻按钮**（ADR-025，2026-08-31 替代已废弃的 `FloatButton` 悬浮覆盖层方案），6 个按钮在构造函数中代码后置创建（`InitDeviceSwitchButtons()`），直接 `Controls.Add` 进 **`panelfloatbutton` 面板**（MainPage 底部 54px 全宽条，tableLayoutPanel2 第 3 行）。**2026-08-31 风格迭代（形态对齐 AntdUI Demo `buttonShadow1`）**：

- 设备：焊接头 / 线激光 / 监控相机 / 运动控制器 / 机器人通讯 / PLC通讯（6 个 `ButtonShadow`，`Name=btnDev_{i}`）。
- **按钮形态（buttonShadow1 同款）**：52×52 方形阴影按钮、`BorderWidth=1F`、`IconRatio=1.2F`、`ShadowColor=黑`、**仅显示 SVG 图标无文本**（默认 poweroff 电源 SVG，与 demo 同源）。**2026-08-31 15:04 面板竖直摆放后按钮改纵向堆叠**：X=2 左对齐固定、Y 按 `btnTop + i*(btnHeight+gap)` 自上而下递增（52×52、gap=15）；**面板最上方标题 `AntdUI.Label`「子设备状态」（15:10 新增，AutoSizeMode=Width、高 24、代码后置局部变量）**，按钮起始 Y 让位标题，整体面板高度需求 428px。
- **设备名走 Tooltip**：单实例 `TooltipComponent`（微软雅黑 10F）对 6 按钮逐一 `SetTip`，`ArrowAlign = TAlign.Top`（顶部显示，TooltipDemo 范式）；`DisposeComponents()` 中释放。**Tooltip 文本含连接状态（2026-08-31 14:42 补充）**：形如「线激光：已连接/未连接」，经 `BuildDeviceTooltipText(idx, connected)` 统一构造，初始全部未连接，线激光随 `RefreshDeviceSwitchUi()` 同步重设（`SetTip` 内部 AddOrUpdate 支持原地更新）。
- **连接态走原生徽标 Badge**（AntdUI `IControl` 内建徽标属性，非子控件）：**徽标内容为内置 SVG 图标——连接=`CheckCircleFilled` 对勾 / 断开=`CloseCircleFilled` 叉号**（用户由 Outlined 手动改 Filled 并加 `BadgeSize=1.0F`），`BadgeAlign=TR` 右上角，填色经 `BadgeBack`：红=(255,77,79)=断开 / 绿=(82,196,26)=连接；按钮 `Type` 保持默认中性态，配色完全由徽标承载（**替代旧版 Type 配色方案**；初版 `Badge=""` 纯色圆点+`BadgeMode=true` 已被 SVG 徽标方案取代并删除）。
- **按钮背景随连接态（2026-08-31 14:22 补充）**：`DefaultBack` 断开=灰(158,158,158) / 连接=null（主题默认白）；`RefreshDeviceSwitchUi()` 与徽标一并刷新。
- **预留接口（public）**：`SetDeviceIconSvg(idx, svg)` 替换按钮图标 SVG（**各按钮设备指向不同**，`_deviceIconSvgs[]` 按设备逐个缓存+应用）；`SetDeviceBadgeSvg(idx, svg)` 设置徽标 SVG（AntdUI 原生 `BadgeSvg` 属性，设置后徽标以 SVG 呈现、颜色仍随 BadgeBack）。
- **为何替换 FloatButton**：`FloatButton.open()` 打开的是独立覆盖层窗口（`FormFloatButton`），页面切换/销毁需事件同步显隐、状态变色需整层重建（闪烁+复杂生命周期）；`ButtonShadow` 为常驻子控件，随宿主页面自动显隐，零事件同步。
- 刷新：单一入口 `RefreshDeviceSwitchUi()`（public），由 `FormMain.uiMillisecondTimer1_Tick` 每周期调用；连接态真相源经 `IsLineLaserRunning()` 读 `LineLaserWorkflow.Instance.Step`（Starting/Working=运行中，不读 `CameraSelector.ConnectionState`——初始化已连 socket 但激光关闭，避免误判），ADR-015 精神；**仅在线激光连接态变化时改一次 `BadgeBack`**（`_lastLlConnected` 去重），无重建无闪烁。
- **仅线激光实现真实连接/断开切换**：`ToggleLineLaserConnection()` 仅向 `LineLaserWorkflow.Instance` 发起 `Start()`(Standby→启动)/`Stop()`(运行态→停机)/`Reset()`(ManualStopped/ErrorAborted→重新初始化回 Standby)，实际连接/开激光在实例自身后台线程执行；其余 5 个硬件暂未接入，点击 `Message.info` 提示「暂未接入，无法操作」。
- 实施位置：全部在 `MainPage.cs` 代码层（构造函数调用 `InitDeviceSwitchButtons()`；按钮随宿主销毁自动释放，Tooltip 组件在 `DisposeComponents()` 显式释放）；不涉及任何 Designer.cs 修改。

### FormMain 状态栏裁剪（2026-08-27）+ 整机状态标签迁移（2026-09-08）

底部 `ToolStrip`(`toolStrip1`) 2026-08-27 裁剪后曾保留 3 项（`lbl_SystemStatus` 整机状态 + `lbl_Status` 流程状态 + `lbl_SystemTime` 系统时间），其余连接/操作级别静态标签已移除。**2026-09-08：`lbl_SystemStatus`/`sep_SystemStatus` 及 `InitializeSystemStatusLabel`/`OnMainDeviceStatusChanged`/`UpdateSystemStatusLabel` 三方法整页删除，整机状态显示迁移至 `MainPage.LabelStatus`（文本「设备状态：{状态值}」+ 设备颜色映射 Running=绿/Reseting=黄/Alarm=橙/EStop=红闪0.5s/Stop=蓝不闪/NoReset=灰，2026-09-08 二次定义，详见 [[api/MainPage]]）**；状态栏现仅保留 `lbl_Status` + `lbl_SystemTime`。

## UI 类资源释放规范（2026-08-19，ADR-001/034 落地）

> **UI 设计器类 `DisposeComponents()` 按需使用**：仅当持有「外部嵌套控件/独立资源」（设计器 `Dispose(bool)` 覆盖不到的代码 new 非容器控件、单例/静态事件订阅、外部对象生命周期）时编写，并由 `HandleDestroyed` 或父页面关闭调用；无嵌套/无独立资源则不需要。非 UI 类一律标准 `IDisposable.Dispose()`（见 [[decisions/ADR-020-DisposePatternFullCoverage]]）。

| UI 类 | 外部资源 | 释放方式 |
|-------|---------|---------|
| `CommPage` | `_robotManager`（new KUKARobotManager）+ `GlobalCommData.CommunicationCommandReceived` | `DisposeComponents()` ← `HandleDestroyed` |
| `MonitorCamPage` | `_statusTimer`（new Timer）+ MonitorCameraWorkflow×5 + FrameCompleted | `DisposeComponents()` ← `HandleDestroyed` |
| `MainPage` | `GlobalCommData.EventInfoHandler` + `_contourCamera.ContourDataReady` | `DisposeComponents()` ← `HandleDestroyed`（移除原 finalizer） |
| `HelixRenderForm` | `_viewer`（new PointCloudViewer，含 WPF Viewport3DX） | `DisposeComponents()` ← `HandleDestroyed`（Designer.cs 已还原为标准生成代码） |
| `MotionControlPage` | `LineLaserWorkflow.StateChanged` | `HandleDestroyed` 退订 + 停止/清理路径退订 |
| `FormMain` | `LineLaserWorkflow.StateChanged` | `FormClosed` 退订 |
| `ILCamPage` | `_ilCamera.ContourFrameReady` + StateChanged + `_displayedClone`（Mat） | `HandleDestroyed` 直接释放 |
| `LLCamWorkJob` | JobSwitched + StateChanged×4 + `_statusTimer` + `_displayedClone` | `HandleDestroyed` → `UnsubscribeEvents` |
| `LLCameraSetting` | 自建配置资源 | `HandleDestroyed` 直接释放 |

> **禁止行为**：修改 `*.Designer.cs` 的 `Dispose(bool)` 释放外部资源（HelixRenderForm 曾违规，已还原）；用 finalizer 退订事件（MainPage 曾用，已移除——事件源持引用时 finalizer 永不执行）。

## 关闭询问（2026-08-19 新增）

`FormMain` 订阅 `FormClosing`（代码后置订阅，不改 Designer.cs），关闭前按整机运行状态询问：

| 整机状态 | 判定 | 弹窗 |
|---------|------|------|
| 未运行 | `DeviceControlWork.Instance.IsWelding == false` | 「确认关闭」`TType.Info` —— 仅询问是否确认关闭 |
| 运行中 | `DeviceControlWork.Instance.IsWelding == true` | 「设备运行中」`TType.Error` —— 告警设备正在运行，确认强制关闭 |

- 用户取消（非 OK）→ `e.Cancel = true` 阻止关闭；确认 → 放行进入 `FormClosed` 释放链（退订 `StatusChanged`/`WeldStatusChanged` + `DeviceControlWork.Dispose()` + `CameraRun.Dispose()`）
- 运行状态单一真相源：`DeviceControlWork.IsWelding`（机器人 Go/Done 指令驱动，整机级运行标志）
- 子设备级状态另读 `Instance.WeldStatus`（焊接过程态）与 `Instance.State`（连接态），见 [[architecture/DeviceControlArchitecture]] §13
- 弹窗范式：`AntdUI.Modal.open(new Modal.Config(this, title, message, type)) == DialogResult.OK`（owner 用 this，FormMain 为 AntdUI.Window）

## 2026-09-07 目录与命名对照

> 用户于 2026-09-07 重构 `UIDesign/`：扁平的 `SubView/` 按**业务域**拆为 `SubDialog/` 下 5 个子目录，同批 8 个类型改名。**命名空间 2026-09-14 已随目录对齐**（`ControlPage` / `TabPage` / `MainWindow` / `SubDialog.<业务域>`，ADR-048）。下表供检索旧名/旧路径使用。

| 旧路径（`UIDesign/SubView/`） | 新路径（`UIDesign/SubDialog/`） | 类型改名 |
|---|---|---|
| `DataReviewPage.cs`（在 `ControlPage/`，非 SubView） | `ControlPage/DataReviewerPage.cs` | `DataReviewPage` → `DataReviewerPage` |
| `ILAlgoPage.cs` | `IntelligentLaserDialog/ILAlgoForm.cs` | `ILAlgoPage` → `ILAlgoForm` |
| `ILParamPage.cs` | `IntelligentLaserDialog/ILParamForm.cs` | `ILParamPage` → `ILParamForm` |
| `ILScanDialog.cs` | `IntelligentLaserDialog/ILScanForm.cs` | `ILScanDialog` → `ILScanForm` |
| `AlgorithmEditForm.cs` | `IntelligentLaserDialog/ILAlgorithmEditForm.cs` | `AlgorithmEditForm` → `ILAlgorithmEditForm` |
| `FormLogin.cs` | `UserManagerDialog/LoginForm.cs` | `FormLogin` → `LoginForm` |
| `UserEdit.cs` | `UserManagerDialog/UserEditForm.cs` | `UserEdit` → `UserEditForm` |
| `InitWaitingPanel.cs` | `FormMainDialog/InitWaitingForm.cs` | `InitWaitingPanel` → `InitWaitingForm` |
| `FileTraceForm.cs` / `HelixRenderForm.cs` / `RecordConfigForm.cs` / `RenderParamForm.cs` | `DataReviewerDialog/`（同名） | 无 |
| `AutoParamForm.cs` / `ConfigForm.cs` | `ParamContolDialog/`（同名） | 无 |

⚠️ **代码内残留旧标识（非阻塞，待清理）**：Designer 的 `this.Name` 仍是旧值（`DataReviewerPage.Designer.cs:336` = `"DataReviewPage"`、`ILAlgoForm.Designer.cs:197` = `"ILAlgoPage"`、`InitWaitingForm.cs:59` = `"InitWaitingPanel"`）；`ILAlgoForm.cs` 内 6 处日志标签仍写 `"AlgorithmEditForm"`；`ILAlgorithmEditForm.cs` 事件处理器名仍为 `AlgorithmEditForm_HandleDestroyed`。

## 已知问题 / 缺口

- ~~ConfigForm 分页~~：已关闭（2026-07-28 UI 整改）——`AntdUI.Pagination` 实装（Total/PageSize/ShowSizeChanger + ValueChanged lambda 切片），范式见 [[guides/AntdUI-Reference]]
- ~~`AntdUI.Chart` 数据绑定 API 未确认~~ / ~~~~`AntdUI.Chart` 已实装~~：**2026-08-12 图表全面改用 ScottPlot.FormsPlot**（MainPage 5 图 + DataReview 1 图），按 [[guides/Project-Tools]] 的 `AddScatter`/`AxisAuto`/`SetAxisLimits`/`Refresh` 实装；`AntdUI.Chart` 相关 `ChartDataset`/`AddPoint`/`AddDataset`/`RefreshChart` 全部移除；**2026-08-13 上午升级 5.1.59、下午回退 4.1.74**（5.x 对 .NET 4.8 设计器不友好），最终锁定 4.1 语法 `AddScatter`/`AxisAuto`/`SetAxisLimits`/`Legend`
- DataReview X 轴缩放窗口（原 SetRange）：**已实装**（`formsPlotData.Plot.SetAxisLimits(min, max)` + `Refresh()`，见 [[guides/Project-Tools]]）
- 变量命名遗留：`uiDataGridView1`（实为 `AntdUI.Table`）、`uiLightStatus`（实为 `AntdUI.Signal`）、`uiCalendar1`（实为 `DatePicker`）等，功能无碍
- AntdUI 控件 API 与 WinForms/SunnyUI 差异迁移坑（Select 无 DataSource / Column.Width 为 string / GridPanel 单参数 Add / Splitter 继承 SplitContainer / Table 数据一律代码后置 Binding()、Designer 内禁 DataSource+AntList / 设计器 System.Void 多为级联）：见 [[guides/AntdUI-Reference]]；MainPage 已由可拖拽 `AntdUI.Splitter` 改为**整页 AntdUI.GridPanel 嵌套固定区域**（外层 uiGridPanelMain「上 68% 顶端分栏 / 下 32% 日志信息」+ 内层 uiGridPanel1「左 40% / 右 60%」，全部不可拖动）：见 [[guides/AntdUI-Reference]]
- SunnyUI `UIMessageBox`（ShowError/ShowWarning/...）在 AntdUI 不存在 → `AntdUI.Modal.open(Modal.Config{Icon=...,Draggable=true})`（模态可拖拽）或 `AntdUI.Message.*`（Toast）；非 UI 类 owner 用 `Form.ActiveForm`/`null`，迁移后删 `using Sunny.UI`：见 [[project/SunnyUI-Legacy]]。UserControl 内 `Message`/`Modal` 的 owner 须为 `null`/`Form.ActiveForm`（`Target` 不支持 `UserControl` 隐式转换，编译报 CS1503）：见 [[guides/AntdUI-Reference]]
- [[guides/WinForms-Designer]]：Designer.cs Dispose 不可修改
- [[guides/Namespace-Compilation]]、[[guides/WinForms-Designer]]、[[guides/WinForms-Designer]]、[[guides/WinForms-Designer]]

## 相关页面

- [[decisions/ADR-015-UIFrameworkMigration]] — 迁移决策与完成状态
- [[decisions/ADR-019-LayoutContainerFreedom]] — 布局容器自由化（解除 GridPanel/FlowPanel 强制使用）
- [[guides/AntdUI-Reference]] — 开发范式（权威）
- [[guides/Project-Tools]] — 图表承载统一用 ScottPlot.FormsPlot 4.1.74（2026-08-12 替换 AntdUI.Chart，2026-08-13 升级 5.x 后回退 4.1.74）
- [[decisions/ADR-015-UIFrameworkMigration]] / [[guides/AntdUI-Reference]] — 迁移决策与追踪
- [[decisions/ADR-001-DisposePattern]]、[[decisions/ADR-002-CS73-Constraint]]

---

*来源：raw/skills/02-Development/UISpecialist.md + raw/knowledge/AdaWeldSystem_Wiki.md；2026-07-28 依 ADR-018 迁移完成状态全面改写为 AntdUI。*
