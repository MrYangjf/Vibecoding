---
title: UIDesign 模块 — UI界面
date: 2026-07-01
updated: 2026-11-02
tags: [模块, UI, WinForms, AntdUI]
source: raw/skills/02-Development/UISpecialist.md
---

# UIDesign 模块 — UI界面

> 全部用户界面的设计与实现。基于 WinForms + **AntdUI（MIT 许可）**，25 组页面/弹窗，三级导航结构。
> UI 框架已于 2026-07-28 从 SunnyUI 全量迁移至 AntdUI（25/25 文件），见 [[decisions/ADR-008-UIFrameworkMigration]]。
> **开发范式唯一权威**：[[guides/AntdUI-Reference]]（布局/事件/Table/Chart/Designer.cs 铁律；原 `新WIKI/UI/AntdUI-DesignParadigm.md` 已并入）。

## 核心文件

UIDesign/
├── MainWindow/                  ← 原 ParentUI/（2026-08-05 重命名）
│   ├── FormMain.cs              ← 主窗口（PageHeader + Segmented + Tabs 导航框架；构造函数同步初始化：配置加载 + 子页面全量实例化 + 设备初始化）
│   ├── FormMain.Designer.cs
│   └── FormMain.resx
├── ControlPage/                 ← 原 Sub1UI/（2026-08-05 重命名）
│   ├── MainPage.cs              ← 首页/仪表盘（**整页 AntdUI.GridPanel 三层嵌套**：外层 uiGridPanelMain「上 68% 顶端分栏 / 下 32% 日志 panelLog（AntdUI.Panel 包裹 AntdUI.Input）」；内层 uiGridPanel1「左 40% / 右 60%」，Padding=5；右格内层 uiGridPanel2「2×2 GridPanel 承载 4 个 AntdUI.Panel（panelChart2/3/4/5），每个 Panel 包裹一张 Chart（圆润边角+白底+阴影动画），Padding=5」；5 张 Chart 均嵌入 Panel（Dock=Fill 充满 Panel），后由 Panel 嵌入 GridPanel（Dock=Fill 充满单元格）；日志由 RichTextBox 改为 **AntdUI.Input**（Multiline+AutoScroll+ReadOnly）；全部不可拖动）；**英莱线激光轮廓（formsPlot1）ScottPlot Signal 模式**（2026-08-18，详见 ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]））：固定 `double[1920]` 数组（`_contourSignalXs`=X/`_contourSignalData`=Y）+ `AddSignalXY` + `Refresh()`，订阅英莱相机 `ContourDataReady` 事件（`InvokeRequired` 跨线程封送），60Hz 全帧率刷新不节流；**2026-08-26 修复**：① FormMain.LoadNavAndPages 中显式调用 mainPage.AddContourLineChart() + AddNewDataLineChart() 初始化图表与事件订阅（此前方法定义但从未调用导致主界面轮廓空白）；② **X 轴用 `_contourSignalXs`（= 沿激光线物理坐标 Y，非等距）由 `AddSignalXY` 显式传入**，不再用 `SampleRate`/`OffsetX`（见 [[lessons/IntelligentLaser-Pitfalls]] §5.16）；③ **轴范围由校准框（四边基准）确定**（从 `CalibrationInfo` 四角点计算 Y/Z mm 范围，含负值，加 5% 边距，连接时锁定一次），无校准框时回退默认值；④ **叠加特征点散点**（AddScatter，红色实心圆 markerSize=8，HasValidResult 时显示 FeatureY/FeatureZ）；⑤ **锁定轴缩放平移**（Configuration 禁滚轮/拖拽 + 每帧 SetAxisLimits 双保险）⚠️ **沿革：本行结构描述停在 2026-08**（`uiGridPanelMain/uiGridPanel1/2×2 Chart` 已废）——2026-09-29 ADR-049 双图化 + 相机预览、2026-10-09 ADR-054 五项单选/状态栏/模组、同日仪表盘容器多层 GridPanel 化后，**以 [[api/MainPage]] 为准**
│   ├── NavPage.cs               ← 统一导航页面（替代 ImagePage/ParamPage，通过 LoadTabs() 接受不同子页配置，实例化两次分别作为参数界面和图形界面；左侧垂直 AntdUI.Menu 导航 + 右侧 Tabs 内容区，TabMenuVisible=false；Vertical 模式，BackActive=White，BackHover=Gray，Round=false）
│   └── DataReviewerPage.cs        ← 数据回顾页面（原 DataReview.cs，**2026-08-05 布局重构，2026-08-07 分页控件升级**：外层 uiTableLayoutPanel1（AntdUI.GridPanel）「左 25% panelLeft / 右 75% panelRight」；panelLeft 内嵌 uiGridPanelLeft「35px 日历 / fill 表格 / fill Pagination 分页 / 30px 页脚」；panelRight 内嵌 uiGridPanelRight「35px 复选框流式布局 / fill 图表 / 20px 进度标签 / 40px 滑块 → **2026-11-02 滑块行移除，底行合并**」；全部 GroupBox 替换为 AntdUI.Panel（白底+灰边框+阴影动画）；btnRenerView 以 Modal.open 弹窗展示 HelixRenderForm）
├── TabPage/                     ← 原 Sub2UI/（2026-08-05 重命名）
│   ├── ILCamPage.cs             ← **线激光/英莱相机工作页面（核心，已替代 LLCamWorkJob）**（完全使用英莱，替代线激光页面挂载；TableLayoutPanel + AntdUI.Panel/Button/Label/Select + Emgu ImageBox 显示轮廓 Mat；IP 输入(初始化读本地配置 `LoadSavedIp`) + 扫描按钮 + 连接 + 开激光/开相机 toggle + JOB select + 算法编辑按钮 + 参数编辑按钮 + 轮廓点/分析结果；**2026-08-17 新增「自动显示」AntdUI.Switch（默认关闭）**：用状态机 `LineLaserWorkflow.State` 判断自动运行中→禁用全部手动按钮、switch 控制轮廓刷新，空闲→恢复按钮；事件订阅放代码后置）；**2026-08-24 UI 状态刷新统一入口重构**：原 `UpdateConnectionUi`/`UpdateModeUi`/`SyncFromHardwareAfterConnect` 三碎片入口内联为 private `*Core` 方法，统一收敛到单入口 `RefreshUi(RefreshUiScope scope)`（`[Flags]` 枚举 Connection/Mode/Hardware 可组合，内置 InvokeRequired 封送），构造函数/btnConnect/工作流态回调/状态机态回调全部只调 `RefreshUi`；**2026-08-24 传感器控制精简**：启停传感器改用 `SetSensor`、弃 `SetCaptureCamera`（非线激光方式），激光/传感器按钮 text 与 `ExtraMouseDown` 收敛到单一 `UpdateLaserSensorUi()`（基于 `IsLaserOn()`/`IsCameraOn()` 真相源，移除 `_isLaserOn`/`_isCameraOn` 本地副本），消除 btnLaser/btnCaptureCamera/SyncFromHardware/UpdateConnectionUi 四处重复 set text
│   ├── ProcessControlPage.cs     ←— **焊接工艺参数配置页（2026-09-17 面板重组，ADR-032；2026-09-22 二度重组 ADR-031）**：根容器 `tabsConfig`（`AntdUI.Tabs`，2026-09-29 由 `tableLayoutPanel7` 2×2 网格改造）四 Tab 分区承载 4 面板——「焊参调整」`tabPageAdaptiveSetup`→`panelWeldList`→`tbPanelAdaparam`（「焊接工艺自适应调参模型」工艺自适应调参；2026-09-17 新增「焊参调整」段：EnableGuide/MaxConsecutiveFailures/IsCountType/CountNum 由轨迹滤波算法面板迁入）、「线激光标定」`tabPageLaserProcess`→`panel1`→`tbpanelweldponts`（**线激光标定：2026-09-22 ADR-031 收窄为纯标定 5 项——线激光-水平轴角度 / 标定中心Z / 标定中心点Y / 示教Y轴锁定坐标 / 趋近阈值，6 列 × 5 行；跟踪几何 9 项已迁出至轨迹点控制面板**，原 `tlPanelWeldPoints` 改名）、「轨迹点控制」`tabPageAlgoControl`→`panel2`→`tbPanelAlogControl`（**「轨迹点控制」：2026-09-22 ADR-031 由「轨迹滤波算法」改名重排，**4 列 × 35 行（2026-09-22 ADR-030 增「最终目标最大突变(mm)」）**，按 ① 线激光点过滤 ② 方向平滑 ③ CSP 输出 ④ 折返监测 ⑤ 跟踪几何 五组分区；PVT 参数 11 个控件真删、5 项停止持久化**；详见 [[api/ProcessControlPage]]）、「模拟测试」`tabPageSimTest`→`panel3`→`tbPanelSimTest`（模拟测试：由 `SystemControlPage`（原 `MotionControlPage`）整体迁入 `cmbFreq`/`btnSaveSim`/`btnStartSim` + `lblSimTestTitle`，见 [[api/ProcessControlPage]]）；线激光标定与轨迹点控制模型参数经 `WeldParamManager.Instance.SaveAlgorithmsConfig()` 落盘，模拟方法 `BtnStartSim_Click` 等随控件迁入代码后置。**2026-09-29 更名 + 重排**：`tabsConfig` → `tabsProcess`，四页改为 工艺调试快捷设定 / 自适应调整工艺设置 / 线激光追踪工艺设置 / 光丝对中工艺设置，**轨迹点控制与模拟测试迁出至 `SystemControlPage`**，详见 [[api/ProcessControlPage]]；**2026-11-02（[[decisions/ADR-063-CommandZoneRadioExclusivity|ADR-063]] 分组互斥演进）**：LA 指令区两套独立电机分组——对焦组 5 项（`LA_Auto`~`LA_Pose2`）挂 `gridQuickLaFocus`、振镜组 4 项（`LA_GalvoCircle`~`LA_GalvoArc`）挂 `gridQuickLaGalvo`，外层 `gridQuickLa` 改 4 格（`Span="40:fill;60:fill;30:fill;30:fill"`）；组内互斥由容器天然成立、跨组可同时各选一个（此前 9 项同挂 `gridQuickLa` 导致整区互斥）；同轮三指令区默认 Auto + 连机置灰（`RefreshActionStates` 唯一入口）+ TA_Auto 力矩门控；**2026-11-03**：TA_Auto 启动置灰修复——清残留选中仅限 `taReady && !taTorqueMode`（未就绪保留默认 Auto），TA 轴判定改用 `GetAxisByKeys(TaAxisKeys)` 与力矩位同路径，新增 `DeviceControlWork.InitializationCompleted` 首填 + `MontionManager.TaTorqueModeChanged` 跨页回填与 Tooltip/日志原因提示，详见 [[api/ProcessControlPage]]
│   ├── FilebackupPage.cs              ← 合并通讯页面（三选一模式：机器人/通用/PLC，GridPanel 四行布局：Radio→Tabs→Checkbox→Input；2026-09-15 重做：radio→tabs 单向联动、启停合并走 CommunicationManager 门面 ConnectRobot/DisconnectRobot、启用开关即时写 IsRobotEnabled、「打开配置」按模式弹 FileEditorForm 编辑 Manager 自持 RobotServerXdoc/RobotClientXdoc，见下方 FilebackupPage 章节与 [[modules/Comm]]）；**2026-09-29 更名为 `FilebackupPage`（显示名「文档备份设置」）并新增 `tabsBackup` 三分区：通讯配置文件（本页原内容零改动）/ 工艺配置文件 / 系统配置文件（承接 `SystemControlPage` 迁出的 CSV/XML 导入导出）**；**2026-11-03 职能收口（业主口径）**：`tabPageSystemCfg` 只承担两件事——① 原始配置文档 → 项目 XML（`btnDeltaGen` 链路）、② `.awcfg` 打包/解包（配置转移）；删除二次保存入口 `btnSaveConfig`、「XML→运行时」`btnReloadConfig`、反向出表 `btnExportCsv`，`gridBackupOps` 缩为 4 控件（`Span="40:fill;fill:160 fill 160"`，以业主手工版式为基准），见 [[api/FilebackupPage]]（2026-11-03 ESI 判据修正：取带 `ProductCode` 的 `Type`，⛔ 不取文档首个 `Type`））
│   ├── MonitorCamPage.cs        ← 监控相机页面（Tabs：焊接相机设置 / 焊接回放，ADR-048/094）
│   └── SystemControlPage.cs     ← **2026-09-29 更名 + Tabs 改造（原 `MotionControlPage`）**：`panel1` 内 `tabsSystem`（`AntdUI.Tabs`，`TabMenuVisible=false`）五分区承载 输入IO / 输出IO / 轴控配置 / 气缸操作 四张 `AntdUI.Table` + 「导入导出」页（`flpToolbar` 独占，文件导入导出 + 自动刷新 / 刷新IO；顶栏已取消）；原 `panelInner`（`TableLayoutPanel` 1 列 × 5 行 + 整页 `AutoScroll`）已删除；**2026-10-22 激光头页控件一致性（[[decisions/ADR-075-LaserHeadUiControlConsistency]]）**：切换类控件改 `AntdUI.Switch`、TA 8 图标按钮复刻 Y 轴、振镜卡片改「状态→设置→按钮」、动作按钮统一「保存模拟参数」样式；**2026-11-02**：TA 力矩模式开关 `swTaTorqueMode`（语义 = TA 轴当前模式状态位：只读 `MontionManager`、随 `timerRefresh` 回填、未连机禁用；使能/前进/后退等手动轴操作由 Manager 统一置关，TA_Auto 随之不可用）；详见 [[api/SystemControlPage]]
└── SubDialog/                   ← 对话窗（Modal 承载的 UserControl，见 [[decisions/ADR-009-DialogWindowToModalUserControl]]）
                                   **2026-09-07 目录重构**：原扁平 `SubView/`（含 ViewPage/ 前身）按**业务域**拆为 7 个子目录（`CommConfigDialog` / `DataReviewerDialog` / `FormMainDialog` / `IntelligentLaserDialog` / `MotionControlDialog` / `ParamContolDialog` / `UserManagerDialog`），
                                   同批 8 个类型改名（见文末「2026-09-07 目录与命名对照」）。**命名空间已于 2026-09-14 随目录对齐（ADR-005）**：`ControlPage` / `TabPage` / `MainWindow` / `SubDialog.<业务域>` 各自独立命名空间。
    ├── CommConfigDialog/        ← 通讯配置域（命名空间 AdaWeldSystem.UIDesign.SubDialog.CommConfigDialog）
    │   └── FileEditorForm.cs   ← 通讯 XML 树形编辑器（UserControl，Modal 承载；左侧 Tree + 右侧 AntdUI.Table 属性编辑，元素名/值/属性可编辑、保存走 `XdocumentReaderWriter.SaveXdocument()`；公开入口 `OpenDocument(doc, docType)`——2026-09-15 起 FilebackupPage「打开配置」按机器人模式传入 Manager 自持 RobotServerXdoc（RSI）/ RobotClientXdoc（EKI），连接参数单一真相源）
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
    ├── MotionControlDialog/     ← 运控配置域（命名空间 AdaWeldSystem.UIDesign.SubDialog.MotionControlDialog）
    │   ├── AxisConfigForm.cs     ← **2026-09-18 由 `TabPage/MotionConfigEditors/AxisConfigEditor` 迁入并改名**（ADR-036 归位）：轴参数编辑对话窗（UserControl，Modal 承载，owner `this.FindForm()`），`(DeltaAxisConfig config)` 构造，`Commit()` 写回配置；详见 [[api/SystemControlPage]]
    │   ├── IoConfigForm.cs        ← 同上（`IoConfigEditor`→`IoConfigForm`，`(DeltaIOConfig config)`）
    │   └── CylinderConfigForm.cs ← 同上（`CylinderConfigEditor`→`CylinderConfigForm`，`(DeltaCylinderConfig config)`）
    ├── ParamContolDialog/       ← 参数控制域（命名空间 AdaWeldSystem.UIDesign.SubDialog.ParamContolDialog）
    │   ├── AutoParamForm.cs     ← 自动参数弹窗（UserControl）
    │   └── ConfigForm.cs        ← 系统配置弹窗（UserControl + AntdUI.Table + AntdUI.Pagination，Modal 承载；2026-08-12 InitTableColumns 设 `AutoSizeColumnsMode=ColumnsMode.Fill` 列宽填满区域）
    └── UserManagerDialog/       ← 用户管理域
        ├── LoginForm.cs         ← 登录弹窗（原 `FormLogin`，2026-09-07 改名；UserControl，Modal 承载；命名空间 AdaWeldSystem.UIDesign.SubDialog.UserManagerDialog；见 [[guides/AntdUI-Reference]]）
        └── UserEditForm.cs      ← 用户编辑弹窗（原 `UserEdit`，2026-09-07 改名；UserControl + AntdUI.Table；命名空间 AdaWeldSystem.UIDesign.SubDialog.UserManagerDialog）

> ❌ **已从本目录移除（仅沿革）**：`EmguAlgoPage.cs`（原项目算法 EmguALG 编辑子页，职责并入 `ILAlgoForm.cs`，ILAlgorithmEditForm 当前只挂 ILAlgoForm）、`LLCameraSetting.cs`（原线激光相机设置，职责现由 `ILParamForm.cs` 承担）。

## UI 层级与控件归位规则（ADR-036）

`UIDesign/` 四级目录各自承载固定层级，控件归属按下表归位（与 [[decisions/ADR-036-UIControlPlacementRule]] 一致）：

| 层级目录 | 承载 | 基类 | 命名空间 | 典型成员 |
|----------|------|------|----------|----------|
| `MainWindow/` | 主窗口（唯一） | `AntdUI.Window` | `AdaWeldSystem.UIDesign.MainWindow` | `FormMain` |
| `ControlPage/` | 页面级 UserControl（由 FormMain 的 Tabs 承载） | `UserControl` | `AdaWeldSystem.UIDesign.ControlPage` | `MainPage` / `NavPage` / `DataReviewerPage` |
| `TabPage/` | 页面级 UserControl（功能分页） | `UserControl` | `AdaWeldSystem.UIDesign.TabPage` | `ILCamPage` / `ProcessControlPage` / `FilebackupPage` / `MonitorCamPage` / `SystemControlPage` |
| `SubDialog/<业务域>Dialog/` | **Modal 承载的对话窗 UserControl**（由调用点 `AntdUI.Modal.open` 弹出） | `UserControl` | `AdaWeldSystem.UIDesign.SubDialog.<业务域>` | `MotionControlDialog/{AxisConfigForm,IoConfigForm,CylinderConfigForm}` 等 |

**归位红线（硬约束）**：
- **任何由 `TabPage/` 或 `ControlPage/` 页面点击弹出的对话框，必须归入 `SubDialog/<业务域>Dialog/`**，不得停留在 `TabPage/` 或 `ControlPage/` 下（见 [[decisions/ADR-009-DialogWindowToModalUserControl]] 承载方式 + [[decisions/ADR-005-NamespaceDirectoryAlignment]] 命名空间随目录）。
- 对话窗一律 `UserControl` + `AntdUI.Modal.open` 承载，禁 `AntdUI.Window`+PageHeader（ADR-009）。
- 命名空间严格等于 `AdaWeldSystem` + 目录点路径；移动文件须同步 `.csproj` 的 `<Compile Include>`（[[guides/Namespace-Compilation]]）。

## 页面继承关系（AntdUI 迁移后）

| 层级 | 基类 | 用途 |
|------|------|------|
| ControlPage / TabPage 页面 | `UserControl` | 功能页面（由 FormMain 的 AntdUI.Tabs 承载，`AddTabSelect`） |
| SubDialog 对话窗（15 个，散布于 7 个业务子目录） | `UserControl` | **Modal 承载的对话窗**（无 PageHeader）；由调用点 `AntdUI.Modal.open(new Modal.Config(owner,标题,form,TType.Info){CloseIcon=true,BtnHeight=0})` 弹出；命名空间已随目录对齐为 `AdaWeldSystem.UIDesign.SubDialog.<业务域>`（ADR-005），见 [[decisions/ADR-009-DialogWindowToModalUserControl]]、[[guides/AntdUI-Reference]]。owner 两种写法**并存于本库**：① 注入 `private readonly Window Window`（`XxxForm(Window _window)` 构造，复刻 AntdUI demo SystemSet 模式）——`RecordConfigForm`/`ConfigForm`/`LoginForm`；② 直接 `this.FindForm()`——`ILParamForm`/`ILCamPage`/`HelixRenderForm`。`AntdUI.Message.*(Form,…)` 与 `AntdUI.Modal.Config(Form,…)` 均接受 `Form`，写法① 非强制；关闭仍用 `this.FindForm().DialogResult` |
| FormMain | `AntdUI.Window` | 主窗口（PageHeader + Segmented + Tabs 导航框架，Segmented 替换原 Menu） |
| 算法编辑子页 EmguAlgoPage（已移除）/ ILAlgoForm | `UserControl` | 由 ILAlgorithmEditForm（SubDialog/IntelligentLaserDialog，Modal 承载）的 AntdUI.Tabs 承载 |

## 常用控件对照（迁移后现状）

| 用途 | 控件 | 说明 |
|------|------|------|
| 文本输入 | `AntdUI.Input` | 原 UITextBox/UIIPTextBox |
| 下拉选择 | `AntdUI.Select` | `SelectedIndexChanged` → `IntEventArgs` |
| 复选/开关 | `AntdUI.Checkbox` / `AntdUI.Switch` | `CheckedChanged` → `BoolEventArgs` |
| 数据表格 | `AntdUI.Table` + `AntList<T>` | 见 [[guides/AntdUI-Reference]]；禁用 DataGridView |
| 状态灯 | `AntdUI.Signal` | 原 UILight（project/SunnyUI-Legacy（归档页 2026-09-17 删除，迁移史见 [[decisions/ADR-008-UIFrameworkMigration]]） 已被取代） |
| 日期选择 | `AntdUI.DatePicker` | 原 UICalendar |
| 图表 | `ScottPlot.FormsPlot`（4.1.74） | **2026-08-12 由 `AntdUI.Chart` 全面替换**；**2026-08-13 上午升级 5.1.59、下午回退 4.1.74**（5.x 基于 SkiaSharp 对 .NET 4.8 设计器不友好），4.1 语法 `Plot.AddScatter(xs, ys, ...)`/`AxisAuto()`/`SetAxisLimits()`/`Legend()`/`Refresh()`；`Configuration.DpiStretch=false` 防高 DPI 字体锯齿；**无需 SkiaSharp/OpenTK/System.ValueTuple**（见 [[guides/Project-Tools]]） |
| 网格布局（可选） | `AntdUI.GridPanel` | **可选布局容器**（[[decisions/ADR-010-LayoutContainerFreedom]] 解除强制使用，因会强制排序）；按需选用。若使用：`Span` 定义行列（值仅 `fill`/`%`/整数/浮点，`px`/`auto` 非法），子控件单参数 `Controls.Add` 且按**逆序**入格；见 [[guides/AntdUI-Reference]]、[[guides/AntdUI-Reference]] |
| 流式布局（可选） | `AntdUI.FlowPanel` | **可选布局容器**（[[decisions/ADR-010-LayoutContainerFreedom]] 解除强制使用，因会强制排序）；按需选用。若使用：`Align=TAlignFlow.Left` 左对齐 + `Gap=N` 控件间距 + `Padding` 内边距 + `AutoScroll` 自动滚动；`TAlignFlow` 枚举：Left/LeftCenter/Center/RightCenter/Right；子控件通过 `Controls.Add` 按顺序添加，自动从左到右排列并换行；表单布局统一 label 宽 140px + input 宽 160px + 行间距由 Gap 控制；见 [[guides/AntdUI-Reference#flowpanel-表单布局]] |
| 消息/对话框 | `AntdUI.Message.*`（Toast，非阻塞）/ `AntdUI.Modal.open(new Modal.Config(owner,"标题","内容"){Icon=TType.*,Draggable=true})`（模态可拖拽） | 原 UIMessageBox；**`Message` 的 owner 类型为 `AntdUI.Target`**（`Window`/`Form` 类可传 `this`，`UserControl` 须传 `Form.ActiveForm`/`(Target)null`/`this.FindForm()`，不可裸 `null` 否则 CS0121）；**`Modal` 的 owner 为 `Control`/`IWin32Window`**（官方 Demo 直接 `Config(window,…)`，裸 `null` 不二义，但锚定父窗体建议 `Form.ActiveForm`/`this.FindForm()`）。详见 [[guides/AntdUI-Reference]] |
| 主题 | `AntdUI.Config.IsLight` 等 | 原 UIStyles.SetStyle(Purple)（project/SunnyUI-Legacy（归档页 2026-09-17 删除，迁移史见 [[decisions/ADR-008-UIFrameworkMigration]]） 已废弃） |

## 技术要点

- 控件优先在 Designer.cs 静态定义；`InitializeComponent()` 禁流程控制语句
- **显示字体统一 `Microsoft YaHei UI`**（2026-10-30 业主裁定）：所有 `new Font("族名", …)` 的族名必须是 `Microsoft YaHei UI`，字号/样式不限；判据 `A.字体规范`（warn，**Designer.cs 同样扫描**），入口 `scripts/simplify_run.py` 第 2 关聚合、`scripts/simplify_selfcheck.py` C3 自证
- 所有 Workflow 事件处理必须检查 `InvokeRequired`（[[guides/WinForms-UI-Threading]]）
- 事件直接订阅 `control.Event += handler`，禁止 `new EventHandler()` 包装 AntdUI 自定义事件（范式 §二）
- 使用 AntdUI.FlowPanel 实现表单流式布局（替代 TableLayoutPanel）——**可选**，见 [[decisions/ADR-010-LayoutContainerFreedom]]
- 3D渲染通过 ElementHost 嵌入 WPF 控件
- FileEditorPage 用 `AntdUI.Select`（`_configSelector`）下拉承载全部通讯 XML 配置入口（服务器/客户端/发送/接收/RSI/EKI），不在 Designer.cs 中定义 MenuStrip；原「打开」按钮（OpenFileDialog）已弃用
- **WinForms 设计器模式保护**：构造函数访问单例/硬件/配置前先判 `LicenseManager.UsageMode == LicenseUsageMode.Designtime`，见 [[guides/WinForms-Designer]]
- 主窗口布局：`PageHeader(Dock=Top, ShowButton=true)` + `Segmented(Dock=Top, 图标+文本)` + `Tabs(Dock=Fill)`；`ControlBox=false`；按钮加到 `PageHeader.Controls`。顶部导航已由 `AntdUI.Segmented` 替代原先的 `AntdUI.Menu`，通过 `SelectIndex` 与 `Tabs.SelectedIndex` 双向联动（`bool syncing` 重入守卫）。SegmentedItem 不支持 `Visible`，权限显隐用 `Items.Remove/Add`。见 [[guides/AntdUI-Reference#Segmented-导航模式]]。
- ~~所有 `AntdUI.Window` 弹窗统一顶部 `PageHeader`~~：**已废弃**。2026-07-30 经 `ADR-028` 改为「**Modal 承载的 `UserControl`**」——8 个对话窗（原 Sub2 UserEditForm + Sub3 全部 7 个）迁入 `SubView/`，基类改 `UserControl`，取消 PageHeader，由调用点 `AntdUI.Modal.open(new Modal.Config(owner,标题,form,TType.Info){CloseIcon=true,BtnHeight=0})` 弹出。详见 [[guides/AntdUI-Reference]]（旧 PageHeader 范式见 [[guides/AntdUI-Reference]]，已标记废弃）

## 各页面要点（迁移后）

### FilebackupPage（UIDesign.TabPage，UserControl；2026-11-03 职能收口）
~~三页签~~ ⇒ **2026-11-03 两页签** `tabsBackup`（`TabMenuVisible=false`）= 通讯配置文件 / 系统配置文件（`SelectedIndex=1` 指向系统页）。通讯通道唯一 RSI（[[decisions/ADR-025-CommModuleRefactor]]）：
- **通讯页**：`tableLayoutPanel1` + `radioRobot`（KUKA 机器人）→ `tabs1` 单向联动；`tabs1` 现仅 `tabPage1`（RSI 面板：启用开关 / 通讯周期 / 打开配置 / 启动·关闭 / 调试面板 / `inputLog` 日志）
- ~~**工艺页**：`tlpProcessBackup`（4 列 8 行，9 控件）~~ ⇒ **2026-11-03 整页删除（业主令「工艺配置文件已经失去意义删除」）**：`tabPageProcessCfg`/`panelProcessCfg`/`tlpProcessBackup` 及 9 个控件、`txtBackupDir`、`EnsureBackupDir`/`BackupSingleFile`/`BackupDirectoryZip` 全部移除；两页最大索引 1，无越界。**2026-11-03 二次修正**：四视图表列宽按可用宽 1283 重配（轴 1510→1280、IO 780→1280、气缸 950→1230、焊接头 1180→1280，长文本列吃剩余空间，表头不截断）；`btnDeltaGen` 文案「生成 XML」→「重载保存」，可用判据由 `Level==Ready` 放宽为 `Level!=Invalid && IsDocumentSource()`（目录有效且至少解析出一份文档），`Partial` 也可保存、缺文件节跳过、内容不符由 `GetParseFailures` 拦下。
- **系统页**：`panelSystemCfg` → `gridSystemRoot`（`Span="160:fill;fill"`，业主手工版式）= `gridBackupOps`（`Span="40:fill;fill:160 fill 160"`，**4 控件**：标题 / 配置文档目录标签 / 目录输入 / 选择目录）+ `gridDeltaConfig`（五段：标题 / `Segmented` **四视图**（轴/IO/气缸/焊接头从站）/ **可编辑 `Table`** / 状态条 / 三按钮）。**本页只有两类职能**：① 原始配置文档 → 项目 XML（`btnDeltaGen`）；② `.awcfg` 打包/解包。表格默认从项目 XML 装载（打开即有数据），选目录后切换为文档源，状态栏标注来源与空态；**项目 XML 源每次切视图重新读盘**（2026-11-03 业主裁定：不复用内存快照）。**2026-11-03 表格可编辑并生效**：双击改单元格（`CellEndEdit` 返回 `bool`，恒 `true`）+ 右键增删行 / 反向导出 CSV / 重新识别（代码后置 `System.Windows.Forms.ContextMenuStrip`，不新增控件）；「重载保存」以**当前表格为唯一提交源**（导出 CSV 至 `ConfigTableStaging` + 表格 PDO 行直传 `Generate`），校验失败按「第 N 行第 M 列」定位且零写入，成功后只回读一次；系统配置页日志只走 `ShowLog` + 状态条，⛔ 不进通讯日志。

**2026-11-03 职能收口（业主口径）**：「这里不需要保存 XML，因为所有改动都是上面系统设置界面做修改保存。这里只做：1、从原始配置文件生成本项目的 xml。2、将设置打包生成配置转移。」⇒ 删除 `btnSaveConfig`（第二保存入口）、`btnReloadConfig`（`btnDeltaGen` 成功后自动回读）、`btnExportCsv`（反向出表不属两类职能）；`MotionConfigImporter.Export` 方法体保留。`gridBackupOps` 7 → 4 控件，以业主手工版式为基准增量删除。

**2026-11-03 审计删除（占位 / 重复，业主裁定）**：`btnImportCsv`（被 `btnDeltaGen` 内部 `Import` 覆盖）、`btnBackupMotionXml` / `btnBackupMotionCsv` / `btnBackupSystemAll`（被 `.awcfg` 导出 + 写前自动备份覆盖）、`lblSystemBackupTip`（描述对象已删）、`tabPage2` / `tabPage3`（空 `TabPage`）、`radioPLC` / `radioEtherNet`（只切空页，通讯模块无此实现）。详见 [[decisions/ADR-079-DeltaControllerConfigAndAwcfgPackage]] 演进记录。

### FileEditorPage（UIDesign.TabPage，UserControl，原 XMLEditor）
文件编辑器页面（2026-08-07 由 XMLEditor 重命名）。编辑 Server/Client/Send/Recive 四种通讯 XML + KUKA RSI/EKI 配置。左侧 `AntdUI.Tree` 文件树 + 右侧 `AntdUI.Table` 属性编辑双面板（2026-08-12 由原生 WinForms PropertyGrid 改为 AntdUI.Table）。**2026-08-12 改造（两轮）**：① 配置入口由动态 MenuStrip 改为 `AntdUI.Select`（`_configSelector`，含服务器/客户端/发送/接收/RSI/EKI 六项，RSI/EKI 文件缺失时经 `KUKAXMLConfig.SaveRSIConfig/SaveEKIConfig` 生成默认配置）；② 右侧属性编辑由 `PropertyGrid` + `ICustomTypeDescriptor` 改为 **`AntdUI.Table` 单元格编辑**（`_xmlPropertyGrid`）：`InitPropertyGridTable()` 代码后置设 `EditMode=TEditMode.DoubleClick` + 双列（`Name`「属性」只读 / `Value`「值」可编辑）+ `Binding(AntList<XmlPropertyRow>)`；行模型 `XmlPropertyRow` 字段 `Name`/`Value`/`AttributeName`/`IsElementName`/`IsElementValue`/`IsReadOnly`；`LoadNodeToTable` 每行对应「元素名称/元素值/每个 XML 属性/统计（只读）」，`XmlTable_CellEndEdit` 校验后写回 XML（属性→`XAttribute.Value`、元素值→`_currentElement.Value`、元素名→非空且不以数字开头，改后经 `FindTreeNode` 刷新树节点显示文本）。**2026-08-12 二轮（本次）表格联动**：① Designer.cs 订阅 `_xmlTreeView.SelectChanged`（`AntdUI.TreeSelectEventHandler` → `XmlTreeView_SelectChanged`），点击左侧树节点即取 `_nodeToXml[e.Item]` 更新 `_currentElement` 并调 `LoadNodeToTable` 刷新右侧表格（表头=`Name` 属性、表格内=`Value` 值）；② 新增 `SelectFirstNode()`——`LoadDocument` 加载完成后自动选中根节点并加载属性，避免打开文档后表格空白；`InitPropertyGridTable` 已设 `AutoSizeColumnsMode=ColumnsMode.Fill` 使列宽填满区域。关键方法：`LoadDocument` / `LoadXdocument` / `AddNodesRecursively` / `InitConfigSelector` / `ConfigSelector_SelectedIndexChanged` / `LoadKUKARobotConfig` / `InitPropertyGridTable` / `SelectFirstNode` / `XmlTreeView_SelectChanged` / `LoadNodeToTable` / `XmlTable_CellEndEdit` / `FindTreeNode`。

### MonitorCamPage（`AdaWeldSystem.UIDesign.TabPage`，UserControl）
焊前对中/焊中质检页，**2026-09-29 ADR-048 起为 `tabsMonitor` 双页**：页1「焊接相机设置」= 顶栏连接区（ADR-046：连接态 Alert + 相机IP + 扫描 + 连接/断开）+ `imageBox1` + 右侧栏四组（采集/录像/参数/标定，录像目录可改）；页2「焊接回放」= 顶栏 `uiPlayDateRange`（`DatePickerRange`，默认今天~今天）+「刷新列表」+ 左侧 `imageBoxPlay` + 右侧 `playTable`（`AntList<PlaybackRow>`，列 = 预览图 `CellImage` / 文件名 / 修改时间 / 大小，`CellClick` 右键「回放」）。**2026-10-30 ADR-078 回放强化**：`panelPlayBar` 作为 `imageBoxPlay` 子控件，底部 96px 热区悬停显隐、`FromArgb(128,0,0,0)` 50% 半透明——上层 `sliderPlay` + `lblPlayTime`（当前/总时长），下层 5 按钮居中（慢放/后退5s/播放暂停/前进5s/快放，`TooltipComponent` 提供中文提示）；进度以 `CapProp.PosFrames` 为唯一轴、帧累加器实现倍速；旧 `flowPlayBar`/`btnStopPlay` 删除；缩略图后台线程解码首帧（代数计数取消 + `BeginInvoke` 刷新），列表先出占位。`DisposeComponents()` 模式（含 `_playTooltip` 与缩略图释放），未重写 `Dispose(bool)`；控件全部由 Designer 声明（ADR-048 四次补充口径），`Table.Columns`/`Binding` 留代码后置。**2026-11-02 版式修正**：回放栏外层 `gridPlayBar`（`AntdUI.GridPanel`，`Span="fill;fill;-26 fill"`，2 区域逆序入格：第 1 格 `gridPlayTime`（`AntdUI.GridPanel`，`Span="fill 90 128"`）/ 第 2 格 `flowPlayButtons`（`AntdUI.FlowPanel`，`Align=Center`）），**回放区零原生布局容器**（页级 `tableLayoutPanelPlay` → `gridPlayPage`（`Span="fill 400;fill 400;-45 fill"`）与 `tableLayoutPlayFilter` → `gridPlayFilter`（`Span="fill 105"`），栏内 `tableLayoutPlayTime` / `tableLayoutPlayCenter` / 原生 `FlowLayoutPanel` 全删）；新增速度标签 `lblPlaySpeed`、倍速/前后退按钮图标化。回放栏外层 `panelPlayBar` 改 `AntdUI.Panel`（`Back` ARGB 128 承载 50% 黑，`Shadow=5` / `ShadowColor=Black` / `BorderColor=RGB(217,217,217)`，`BorderWidth` 默认 0；`Padding` 校准为 (3,0,3,0) 抵消阴影 5px 内缩），悬停显隐仍用 `Visible` + `RectangleToScreen`。**2026-11-09 对中阈值迁入**：右侧栏「参数」组 `grpParam` 的 `tableLayoutParam` 由 3 行扩为 **5 行**（曝光/增益/**警告(mm)**/**报警(mm)**/按钮行），新增 `lblAlignWarn`+`txtAlignWarn`、`lblAlignFail`+`txtAlignFail` 与 `btnSaveAlign`（「保存阈值」）；读写 `AlgorithmManager.Instance.WireFeed.CenterWarnMm/CenterFailMm`（`WARN_MM`/`FAIL_MM` 键不变），校验 `0 < 警告 < 报警`；沿用原激光头页「仅 Admin 可写」口径（`ApplyAlignPermission` + 保存前二次校验）。

### DataReviewerPage（`AdaWeldSystem.UIDesign.ControlPage`，UserControl，2026-08-05 布局重构，2026-08-07 分页升级 + 3D弹窗，**2026-09-20 数据源与图表重构**，2026-09-21 刷新按钮 + 轴实际Y系列）
离线回溯生产数据（**2026-09-20 重构，[[decisions/ADR-037-ProductProductionRecordLifecycle]] 决 4**）：**表格 = 产品库当日生产记录**（`ProductFileRecordManager.SelectProductRecords(date)`，列 `No./产品码/起焊时间/状态/结果/异常原因`；**一次性读取，分页仅做内存切片，不轮询、不重新查询**），选中行 → `GetSessionRecordFiles(startTime, sn, status)` 推算该会话三份记录文件 → **一次性读取**（`.pDat` → 焊缝宽度 / 送丝速度 / 激光功率（均为工艺查表输出值）/ 机器人运动速度 / 调整动作点；`.csv` → CSP 运动 Y 轴指令值 / 机器人 Y 轴 / 焊缝跟踪轴实际反馈位置）→ `ScottPlot.FormsPlot` 以**机器人 X 轴**为横轴绘八系列，**各系列均可选显示**（7 个 `AntdUI.Checkbox` + 调整点恒显红色），线色用 Ant Design 标准色板区分。**首次进入才加载当日生产记录**（2026-09-20 修复「直接打开表格为空」；**2026-11-09 二次修正触发时机**：加载入口收敛为 `EnsureLoaded()`，只由用户交互（导航/页签切换、刷新、改区间）触发，页面**不再订阅 `VisibleChanged`**；门槛改用 `GlobalCommData.IsAppRunning`（初始化结束后由 `FormMain` 置位）—— 实测 AntdUI 非当前 `TabPage` 恒为 `Visible=true`、窗体 `Show` 时全部子页 `VisibleChanged` 都会触发，可见性判据已被证伪；启动/初始化零查询、零空态，未加载与已查询为空两态文案分离；`_firstShownLoaded` 保证反复切页不重查。见 [[decisions/ADR-078-MonitorPlaybackControlBarAndDatedRecords]]「通用化」与 [[standards/ModuleOrganizationPattern]] H11）。**调整点** = `.pDat` 中 `AdjustExecuted=true` 的全部动作（参数调整 **+ 线激光 Job 切换**），纵轴取调整时刻焊缝宽度；`uiSymbolLabel1` 显示产品码 / 起焊时间 / 结果 / 调整次数与逐条明细。

**2026-09-21 变更**：① **日期栏刷新按钮 `btnRefreshDate`**——`panelLeft` 顶部改为 `panelDateBar`（Dock=Top）承载 `uiCalendar1`（Dock=Fill）+ `btnRefreshDate`（Dock=Right 44px，图标 `ReloadOutlined`），点击按当前日历日期重载 `InitPCLDir`，**当日产生新记录后无需切换日期即可刷新列表**（顺带清掉 Designer 从未挂接的孤儿处理器 `btn_LoadFile_Click`）；② **「轴实际Y」系列 `chkAxisY`**（品红 `(235,47,150)`）——绘制轨迹 CSV 第 4 列 `AxisY_mm`（跟踪轴实际反馈），与「CSP运动Y轴」指令曲线并看即可判定 CSP 写入是否生效（分离 = 写入未生效，重合 = 写入正常）；旧 3 列轨迹文件无第 4 列（解析为 `NaN`），该系列自动无数据。

外层布局：`tableLayoutPanel2`（左 20% `panelLeft` = `panelDateBar`（Dock=Top，2026-09-21：`uiCalendar1`（DatePicker，Dock=Fill）+ `btnRefreshDate`（Dock=Right，`ReloadOutlined` 图标））+ `uiDataGridView1`（Table）+ `pagination1`（Pagination，`PageSizeOptions=[20,50,100,200]`，`ValueChanged` 驱动 `FillPage` 切片；右 80% `panelRight` = `uiGridPanelRight` 承载 `uiFlowLayoutPanel1`（7 个 Checkbox，2026-09-21 增 `chkAxisY`）+ `formsPlotData`（FormsPlot）+ `uiSymbolLabel1` + `btnRenerView`）。色彩规范：选中态 `#1677FF` 文本/图标 + 浅灰底（AntdUI 默认主题）。

> ⛔ **2026-11-02「按 X 范围显示区域」模块整体移除**：原 `uiTrackBar1`（`AntdUI.Slider`，按机器人 X 分段设 `SetAxisLimits`）**已从 Designer 移除**（控件本体 / `Controls.Add` / 属性块 / 字段声明），底行 GridPanel `Span` 由 4 行改为 **3 行 `"fill;fill;fill 120;-35 fill 35"`**（滑块行并入底行，图表 +35px、按钮保持原位）。连带专属字段 `TrackbarRate` 与判据 `HasEnoughSeamWidthPoints` 一并删除。⛔ 悬停读数用的 `MinValueRobotX` / `MaxValueRobotX` **保留**（与滑块无关）。详见 [[api/DataReviewerPage]] 与 [[lessons/UiModuleRemovalCleanup]]。

> ⚠️ 沿革（2026-09-20 之前的描述已被取代）：旧版为 `uiTableLayoutPanel1` + `uiGridPanelLeft` + `uiDataGridViewFooter1` + `uiLineChart2`（`AntdUI.Chart`，数据填充曾为 TODO）承载，数据源为 `RunRecordManager` 按 `yyyyMMdd` 枚举 `.pDat` 文件列表；现行已改为 ScottPlot 绘图 + 产品库生产记录数据源。

**btnRenerView（3D数据回溯按钮）**：点击后以 `AntdUI.Modal.open` 弹窗形式展示 `HelixRenderForm`（Modal 承载的 `UserControl`，900×600，MaskClosable=true，CloseIcon=true）。

**BtnRecordSetting（记录设置按钮，2026-08-13 接入）**：点击后以 `AntdUI.Modal.open` 弹窗形式展示 `RecordConfigForm`（记录配置：临时/保存路径 + 混淆选项）。原 `HelixRenderForm` 的「记录配置」按钮（`btnRecordConfig`）已移除，此入口迁至本页底部按钮。

### SystemControlPage（原 `MotionControlPage`，`AdaWeldSystem.UIDesign.TabPage`，UserControl，设计器生成，**2026-09-17 迁入运控 4 表 / 2026-09-29 更名 + Tabs 四分区**）
**2026-09-17 重构**：① 标定数据参数**已迁出**——归工艺配置页 `ProcessControlPage` 的 `tbpanelweldponts`「线激光标定」段；② **模拟测试全部控件与逻辑整体迁至 `ProcessControlPage.tbPanelSimTest`**（`cmbFreq`/`btnSaveSim`/`btnStartSim` 及 `BtnStartSim_Click` 等，见 [[api/ProcessControlPage]]）；③ **原 `MontionConfigForm`（已废弃）的运控功能整体迁入本页 `panel1`**——`panel1`（`AntdUI.Panel`，`AutoScroll`）+ `tabsSystem`（`AntdUI.Tabs`，五页 = 输入IO / 输出IO / 轴控配置 / 气缸操作 / 导入导出；2026-09-29 取代原 `panelInner`）承载 4 张 `AntdUI.Table`，`flpToolbar`（CSV/XML 工具栏 + 自动刷新 / 刷新IO）**独占「导入导出」页**（`Dock=Fill`，不再占顶栏）（输入/输出 IO、轴、气缸，信号灯 `CellBadge`、操作/参数按钮 `CellButton`）+ `timerRefresh`（500ms）；3 个参数编辑器 `UserControl`（`AxisConfigForm`/`IoConfigForm`/`CylinderConfigForm`，已 2026-09-18 按 ADR-036 迁至 `SubDialog/MotionControlDialog/`）经 `Modal.open` 弹窗编辑 `Delta*Config`。**2026-09-29 二次重构**：显示名「运控设置」→「**系统设置**」，`tabsSystem` 五页 → **四页（跟踪系统参数 / 光丝系统参数 / 温控系统参数 / 模拟测试）**，⛔ 输入IO·输出IO·气缸操作三表取消、⛔ `flpToolbar` 导入导出区迁出至 `FilebackupPage`「系统配置文件」页，🔄 轨迹点设定与模拟测试自 `ProcessControlPage` 迁入，⚠️ 轴表只渲染 Y 轴。详见 [[api/SystemControlPage]]。**2026-10-22/23 电机区落地（[[decisions/ADR-075-LaserHeadUiControlConsistency|ADR-075]]）**：`gridTemp` 温压（`swTempRefresh` Switch）/ `gridOptics` 振镜（状态→设置→~~`swGalvoEnable`~~ 回零）/ `gridLa`（原 `gridTaLa`）LA 对焦+光丝对中（~~`swLaMotorEnable`~~）/ `gridWireCurve` TA 送丝力矩电机（8 图标按钮**与①跟踪轴同构**：NegBack/StepBack/Stop/StepFwd/NegFwd/MoveTo/Home/Servo），底部 `flowPanel2` 读取·修改·保存；TA 目标力归工艺参数，TA 轴走 `MontionManager`（ADR-073），详见 api 页。⚠️ **2026-10-26 演进（[[decisions/ADR-075-LaserHeadUiControlConsistency]]）**：两个**使能** Switch 改纯图标按钮（`btnOptMotorEnable` / `btnOptGalvoEnable`，状态由 `lblOptMotorState` / `lblOptGalvoEnableValue` 承载）；`gridLa` 末行改**四键一行**（后退/前进/移动到目标/使能）+ 新增 `txtOptMotorTarget`；TA/LA/振镜/温度四区「自动刷新」开关（Designer 默认 ON）由**唯一计时器 `timerRefresh` 分区分控**（⛔ 不新增计时器），且**两个前置条件分治**（实机复查修订）：未连接 ⇒ **五个**开关（四区 + 轨迹页轴表，见下）**自动回退 `Checked=false`**、重连自动恢复默认 ON；未切到本页 ⇒ **仅跳过刷新、保留开关状态**；未连接时手动开启会被拒绝；程序回写经 `_syncingRefreshSwitch` 抑制（⛔ 不得把两个前置条件合并进同一个提前返回）。**2026-10-26 §六 适用面扩展**：轨迹页 `flpTraceToolbar` 的 `btnAutoRefresh` 由 Button 改 **`swAutoRefresh`（Switch，默认 ON）**并纳入同一套约束，冗余的「刷新轴状态」**`btnAxisRefresh` 已删除**（删除前核验 `LoadAxisRows()` 仍余 2 处消费者）；`TimerRefresh_Tick` 改为按内页**精确匹配**（`LaserHeadTabIndex=1` / `TraceTabIndex=0`，⛔ 无 `else` 兜底）。
**2026-11-02 TA 力矩模式开关（[[decisions/ADR-057-TaLaActionAndFollowControl|ADR-057]] 语义对齐）**：`swTaTorqueMode` 不是独立功能开关，而是 **TA 轴当前模式的状态位**——单一真相源在 `MontionManager.TaTorqueModeEnabled`（该位由 `SetTaTorqueMode` 唯一写入：使能/前进/后退/回零等手动轴操作与 `Break`/`Pose`/`Retract` 指令都会置关；`TA_Auto` 执行期间为开）；本页只做呈现与意图下发，`TimerRefresh_Tick` 每拍只读回填 `Checked`、`Enabled` 跟随运控连接，⛔ 不另存 bool、不落盘；默认值来自轴配置 XML（`TORQUE_MODE`，力矩类轴缺省 TRUE），⛔ 非 UI 初始化硬赋。

**2026-11-09 刷新策略修订（推翻上段「默认 ON / 重连自动恢复 ON」）**：五个「自动刷新」开关 Designer 默认改 **OFF**，启动后不自动刷新，只有调试时手动打开才按周期执行。开关可用性改为**按设备粒度就绪门禁**——轴表看运控初始化完成、LA / 振镜 / 温度看焊接头从站就绪、TA 看运控完成且 TA 轴已装载；未就绪 `Enabled=false` 置灰不可点（不给「点了才报错」的机会），就绪只解冻不自动开启。门禁在**运控状态切换 / 初始化结束 / 初始化汇总 / 轴就绪变化**四处事件统一重算（`ApplyRefreshSwitchGate`）。定时刷新改**后台采集快照 + `BeginInvoke` 应用**（`_refreshBusy` 单飞），不卡 UI 线程。规则见 [[standards/DeviceInitializationDependency]] §四。

### ILAlgorithmEditForm（`AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog`，UserControl，Modal 承载）
算法编辑弹窗：`tabsAlgo`（**`AntdUI.Tabs`**）按 `CameraSelector.Active` 接口 `AddTabSelect` 挂载 `ILAlgoForm`（⚠️ 原 `EmguAlgoPage` 分支已随文件移除，当前仅英莱一页）（英莱 Job Parameter 编辑 + 实时识别结果只读）。接口分隔决策见 [[decisions/ADR-012-AlgorithmEditInterfaceSplit]]（框架层描述已按 AntdUI 落地）。2026-07-30 经 `ADR-028` 由 `AntdUI.Window` 改为 `UserControl` 并迁入 `SubView/`，调用点 `ILCamPage.btnEditJob_Click`（原 `LLCamWorkJob`）以 `AntdUI.Modal.open(...)` 弹出；原 `FormClosing` 停英莱页定时器逻辑改订阅 `HandleDestroyed`（不重写 `Dispose(bool)`）。详见 [[api/ILAlgorithmEditForm]]。

### ILCamPage（`AdaWeldSystem.UIDesign.TabPage`，UserControl，已替代 LLCamWorkJob）
线激光/英莱相机工作核心页：IP 输入+扫描+连接、开激光/开传感器按钮、Job 下拉+应用按钮、帧率模式下拉+应用按钮、算法编辑按钮、参数编辑按钮、轮廓画面+分析结果表。**已完全替代原 `LLCamWorkJob`**（Sub2UI 时代线激光页面，文件已改名并迁至 `UIDesign/TabPage/ILCamPage.cs`）。Workflow 事件全部 `InvokeRequired` 守卫。详见 [[lessons/IntelligentLaser-Pitfalls]]（§5.17，原 IntelligentLaserSensorControl 页 2026-09-17 并入）。
**2026-09-30 Tabs 化（[[decisions/ADR-051-ILCamPageTabsConversion]]）**：根容器由 `uiTableLayoutPanel1` 直挂改为 `tabsIL`（`AntdUI.Tabs`，`Dock=Fill`）→ `tabPageLaserCapture`（`Text="线激光采集设置"`）→ `uiTableLayoutPanel1`（原四行布局与内部控件零改动）；**`Controls.Add` + `Pages.Add` 双写**；`tabsIL.Text="线激光设置"`（= NavPage 名，2026-11-13 随页面并入系统参数设置改名）；**只改设计器，`.cs` 零改动**（该页 `.cs` 对控件仅「只使用」）。控件与组件全归设计器（字段 29→31，Tabs/TabPage 三项齐备）。⚠️ 遗留待裁定：`uiTableLayoutPanel1` 的 `RowCount=4` 而 `RowStyles` 5 条（业主 VS 中间态，未改）。

### AutoParamForm（`AdaWeldSystem.UIDesign.SubDialog.ParamContolDialog`，UserControl，Modal 承载）
自动参数弹窗（命名空间 `AdaWeldSystem.UIDesign.SubDialog.ParamContolDialog`）：表格 `uiDataGridView1`（**`AntdUI.Table`**，InitTableColumns 代码后置 + `Binding(AntList<AutoParamRow>)`）；原头部 `ToolStrip`（`labelK`/`LabelJ`/`labelM` 三标签 + `btnSave` 保存）已迁移为 `AntdUI.FlowPanel`（Dock=Top）承载 3×`AntdUI.Label` + `lblSpacer`（`Dock=Fill` 弹性占位右推）+ `AntdUI.Button`（`btnSave`，保留保存功能）；K/J/M 文本在 `LoadConfigData` 中赋值。**2026-08-12 表格可编辑 + 列宽填满**：`InitTableColumns` 设 `EditMode=TEditMode.DoubleClick`（双击进入编辑）+ 可编辑列（焊接速度/送丝速度/焊接功率）经 `.SetEditable(true)` 开启 + `AutoSizeColumnsMode=ColumnsMode.Fill` 列宽填满区域；构造函数订阅 `CellEndEdit` → `uiDataGridView1_CellEndEdit`，按 `e.Column.Key` 将编辑值写回 `AutoParamRow` 对应属性，`btnSave_Click` 经 `UpdateParamValues` 落库（`RobotSpeed`/`FeedSpeed`/`LaserPower` 用 `CultureInfo.InvariantCulture` 解析回写字典）。迁移范式见 [[guides/AntdUI-Reference]]。

### MainPage 硬件快捷开关（AntdUI ButtonShadow 常驻按钮，ADR-011；2026-08-31 风格迭代）

`MainPage` 使用 **AntdUI `ButtonShadow` 常驻按钮**（ADR-011，2026-08-31 替代已废弃的 `FloatButton` 悬浮覆盖层方案），设备按钮在构造函数中代码后置创建（`InitDeviceSwitchButtons()`；**2026-10-22 起 4 组「按钮 + 等高 Alert」2×2 区域**），直接 `Controls.Add` 进 **`panelfloatbutton` 面板**（MainPage 底部 54px 全宽条，`PanelDashborad` 内 `tableLayoutPanel1`）。**2026-08-31 风格迭代（形态对齐 AntdUI Demo `buttonShadow1`）**：

- 设备（现行 **4 个**，[[decisions/ADR-054-MainPageSingleSelectionAndAlarmText]]）：线激光 / 监控相机 / 控制器 / 机器人（`Name=btnDev_{i}`）；~~原 6 个（焊接头/线激光/监控相机/运动控制器/机器人通讯/PLC通讯）~~已于 2026-10-09 收敛为 4。
- **按钮形态与布局（2026-10-22 现行）**：按钮保持 buttonShadow1 同款（`BorderWidth=1F`、`IconRatio=1.2F`、`ShadowColor=黑`、**仅显示 SVG 图标无文本**）；`panelfloatbutton` 内改 **2×2 四区域**，每区「方按钮 + 等高 `AntdUI.Alert`（设备名）」，按钮边长=Alert 高度=`cellHeight`、区内间隔 1px、区域间隔 8px、外边距 4px；尺寸不写死，由 `LayoutDeviceSwitchAreas()` 按面板 `ClientSize` 运行时核算，`SizeChanged` 与页面显示后各重排一次。~~2026-08-31 15:04 纵向堆叠 52×52/gap15 + 顶部标题「模组状态」~~（已被本轮取代，标题不在现役代码中）。
- **设备名走 Tooltip**：单实例 `TooltipComponent`（微软雅黑 10F）对 4 按钮逐一 `SetTip`，`ArrowAlign = TAlign.Top`（顶部显示，TooltipDemo 范式）；`DisposeComponents()` 中释放。**Tooltip 文本含连接状态（2026-08-31 14:42 补充）**：形如「线激光：已连接/未连接」，经 `BuildDeviceTooltipText(idx, connected)` 统一构造，初始全部未连接，线激光随 `RefreshDeviceSwitchUi()` 同步重设（`SetTip` 内部 AddOrUpdate 支持原地更新）。
- **连接态走原生徽标 Badge**（AntdUI `IControl` 内建徽标属性，非子控件）：**徽标内容为内置 SVG 图标——连接=`CheckCircleFilled` 对勾 / 断开=`CloseCircleFilled` 叉号**（用户由 Outlined 手动改 Filled 并加 `BadgeSize=1.0F`），`BadgeAlign=TR` 右上角，填色经 `BadgeBack`：红=(255,77,79)=断开 / 绿=(82,196,26)=连接；按钮 `Type` 保持默认中性态，配色完全由徽标承载（**替代旧版 Type 配色方案**；初版 `Badge=""` 纯色圆点+`BadgeMode=true` 已被 SVG 徽标方案取代并删除）。
- **每区 Alert（2026-10-22 新增）**：`Text`=设备名、`TextAlign=MiddleCenter`，连接态经 `Icon`（`TType.Success`/`Error`）与 `TextColor`（绿(0,128,0)/红(192,0,0)）表达，由 `RefreshDeviceSwitchUi()` 随徽标一并刷新；原全局通讯 Alert `_alertConnStatus` 与 `_lastAlertConnected` 已删除（通讯状态由 4 个设备 Alert 各自表达）。
- **按钮背景随连接态（2026-08-31 14:22 补充）**：`DefaultBack` 断开=灰(158,158,158) / 连接=null（主题默认白）；`RefreshDeviceSwitchUi()` 与徽标一并刷新。
- **预留接口（public）**：`SetDeviceIconSvg(idx, svg)` 替换按钮图标 SVG（**各按钮设备指向不同**，`_deviceIconSvgs[]` 按设备逐个缓存+应用）；`SetDeviceBadgeSvg(idx, svg)` 设置徽标 SVG（AntdUI 原生 `BadgeSvg` 属性，设置后徽标以 SVG 呈现、颜色仍随 BadgeBack）。
- **为何替换 FloatButton**：`FloatButton.open()` 打开的是独立覆盖层窗口（`FormFloatButton`），页面切换/销毁需事件同步显隐、状态变色需整层重建（闪烁+复杂生命周期）；`ButtonShadow` 为常驻子控件，随宿主页面自动显隐，零事件同步。
- 刷新：单一入口 `RefreshDeviceSwitchUi()`（public），由 `FormMain.uiMillisecondTimer1_Tick` 每周期调用；连接态真相源经 `IsLineLaserRunning()` 读 `LineLaserWorkflow.Instance.Step`（Starting/Working=运行中，不读 `CameraSelector.ConnectionState`——初始化已连 socket 但激光关闭，避免误判），ADR-008 精神；**仅在线激光连接态变化时改一次 `BadgeBack`**（`_lastLlConnected` 去重），无重建无闪烁。
- **仅线激光实现真实连接/断开切换**：`ToggleLineLaserConnection()` 仅向 `LineLaserWorkflow.Instance` 发起 `Start()`(Standby→启动)/`Stop()`(运行态→停机)/`Reset()`(ManualStopped/ErrorAborted→重新初始化回 Standby)，实际连接/开激光在实例自身后台线程执行；其余 5 个硬件暂未接入，点击 `Message.info` 提示「暂未接入，无法操作」。
- 实施位置：全部在 `MainPage.cs` 代码层（构造函数调用 `InitDeviceSwitchButtons()`；`LayoutDeviceSwitchAreas()` 运行时核算 2×2，`panelfloatbutton.SizeChanged` 订阅在 `DisposeComponents()` 退订；按钮/Alert 随宿主销毁自动释放，Tooltip 组件在 `DisposeComponents()` 显式释放）；不涉及任何 Designer.cs 修改。

### MainPage 焊接流程步骤条（`steps1`，2026-10-22；2026-11-10 删除后补回、同日改横排）

- 控件：设计器 `steps1`（`AntdUI.Steps`，**`Vertical=false` 横排**，`gridTopBlock` 第 2 行格）——控件本体由 Designer 声明，代码后置只做 Items 装配与状态联动。2026-11-10 业主改版曾删除，同日按业主指示补回；容器 `gridTopBlock.Span = "60:fill;80:fill;fill"`（行 1 高 60 = `LabelStatus`，行 2 高 80 = `steps1`，行 3 fill 空置）。
- 几何：`GridPanel` 运行期按格重排子控件，`Location/Size` 只是设计期快照——实测 `steps1` 实际为 (3,63) 442×74，`LabelStatus` 为 (3,3) 442×54；容器有 2 个子控件，格序按 `Controls` 索引**倒序**分配（索引大者取第 1 格）。
- 横排容量（2026-11-10 方案 B 离屏实测，`Gap=8`，5 项只写 `Title`）：AntdUI 横排**按内容紧排、剩余宽度摊到项间**（非等分）——442×74 下 YaHei 10pt 各步占用 **91/105/78/78/78px**（文字 40/54/27/27/27px、图标 27px），项间矩形间距仅 **2px**（视觉墨迹间隙 8~9px，**不再重叠**）；继承字体（宋体 9pt）占用 82/94/70/70/70px、间距 11px；YaHei 9pt 间距 8px。副标题/描述**不再渲染**，标题字号保持 10F 未降（业主未批字号变更）。
- 悬停提示（2026-11-10）：AntdUI 2.4.3 `Steps` **无逐项 Tooltip 承载位、无公开 hover 索引**，故用原生 `System.Windows.Forms.ToolTip` + `steps1.MouseMove`/`MouseLeave`；逐项文本（`SubTitle+"\n"+Description`，逐字沿用）按 `Items` 同序存于 `_weldFlowStepTips`，命中矩形读 AntdUI 自身布局结果 `StepsItem.rect`（内部属性，反射读取），**不自算坐标、不做 x 等分换算**。提示内容挂在步骤项自身而非按 `Current` 取，故不会出现「已到焊接、提示还说安全位」的错位；`InitialDelay/ReshowDelay=0`、`AutoPopDelay=20000`、`ShowAlways=true`。
- 数据：五步文案与顺序唯一来源 `WeldParamControl/WeldParamData.cs` 的 `WeldFlowSteps.All`：安全位（焊接准备）→ 焊前检查（PreWork）→ 起焊（焊接启动）→ 焊接（自适应跟踪）→ 结束（停止流程）。
- 联动三源：机器人指令（`RX_START_SAFE_POSE` / `RX_PRE_WELD_REQUEST` / `RX_WELD_START_POSE` / `RX_WELD_STOP_POSE` / `RX_STOP_SAFE_POSE`）+ 整机 `MainDeviceStatus`（Running/Stop/Reseting/NoReset/Alarm/EStop）+ `WeldParamControlWorkflow.WeldStatusChanged` 兜底；进度默认只前进，仅 `Reseting/NoReset` 回退；后台事件经 `BeginInvoke` 封送。
- 释放：`DisposeComponents()` 退订 `WeldParamControlWorkflow.WeldStatusChanged`；`MainPage_HandleDestroyed` 释放 `_weldFlowToolTip`（`Dispose()` 后置 null）。

### MainPage 主界面双图化 + 监控相机预览（[[decisions/ADR-049-MainPageDualChartAndCamPreview]]，2026-09-29；⚠️ 2026-10-22 预览条款废止）

`MainPage` 由业主在 VS 重排布局后，代码后置配套落地：**5 张 ScottPlot 图 → 2 张**。

| 区域 | 控件 | 内容 |
|---|---|---|
| `tableLayoutPanel3`（顶层，6 列 × 2 行） | — | 取代原 `uiGridPanelMain` + `uiGridPanel1`（均已删除） |
| (0,0) colspan 3 | `panel1` → `formsPlot1` | **线激光轮廓图**（未变）：`AddSignalXY` 1920 点 + 特征点散点 + 首帧轴范围锁定 |
| ~~(2,0)~~ | ~~`panelCam` → `imageBoxCam`~~ | ⛔ **2026-10-22 已删除**（业主需求：监控画面不输出到主界面）：控件三处 + `ISupportInitialize` + Suspend/Resume + 30Hz 节拍与帧所有权全清；行 0 重排为 `panel1`(0,0,span3) + `PanelDashborad`(3,0,span3)。预览现仅由 [[modules/MonitorCam]] 承载 |
| (3,1) colspan 1 | `panelChart2`（`AntdUI.Panel`，`Padding=(2)`）→ `formsPlot2`（Dock=Fill，占满客户区）+ **悬浮**在图表右上角的 5 个 CheckBox（`Anchor=Top|Right`，右对齐右边距 12px，行高 44 / 间距 56，`BackColor=White`） | **四合一工艺参数图**：接头宽 / 运动速度 / 送丝速度 / 激光功率 / 送丝Z轴位置同图，5 个复选框切换显隐（文本/默认勾选态/字体由设计器声明）。⚠️ 2026-11-10：`gridPanel2`/`flowLayoutPanel1` 已删；**复选框改为不占布局的悬浮层**（不再用 Padding/列宽让位），绘图区宽度与无勾选框时一致；z 序由 `KeepSeriesTogglesOnTop()` 校正 |
| (3,0) colspan 3 | `PanelDashborad` → `tableLayoutPanel1` | 模组状态面板（`LabelStatus` + 各状态 `label`）+ `panelfloatbutton` 硬件快捷开关（ADR-011） |
| (0,1) colspan 3 | `inputLog` | 全局日志框 |

- **四合一图**：`RefreshParamCharts()` 走「`Plot.Clear()` → 按勾选态 `AddSeries`（Ant Design 四色）→ `AxisAuto` + `Legend` + `Refresh`」——**ScottPlot 4.1 无逐系列 `Visible`**，与 `DataReviewerPage` 同范式；复选框文本（接头宽/运动速度/送丝速度/激光功率/送丝Z轴位置）与默认全选（`Checked = true`）**由设计器声明**，字体统一 `Microsoft YaHei UI` 10F；`InitSeriesToggles()` 只做系列数组装配与勾选事件订阅（订阅晚于 `InitializeComponent()`，故设计器回填不触发，**无需抑制标志**）。
- ~~**预览**：帧源 `MonitorCamManager.Instance.PreviewFrameEvent`（连续取流逐帧独立副本）→ 相机线程只入待显示槽 → UI 侧 `_camPreviewTimer`（33ms）按节拍上屏；无新帧时回退 `CurrentMat`（单次采集，只读不释放）；页面不可见时丢弃待显示帧。**帧所有权**：自有副本在新帧替换时 `Dispose()`，`CurrentMat` 永不释放。~~（⛔ 2026-10-22 已删除：主界面不再显示监控画面，现行预览承载页 = [[modules/MonitorCam]]）
- **实施位置**：`MainPage.Designer.cs` 承载 **`checkbox1~4` 的文本/勾选态**（2026-09-29 按业主口径由代码后置迁回设计器，改法走字节安全流程；⛔ 2026-10-22 起 `imageBoxCam` 已随预览移除）；`MainPage.cs` 只承载**数据绑定/事件订阅**；同轮删除多图专用的 `BindChartVar`（由 `AddSeries` 接管）并收敛对已删 `formsPlot3/4/5` 的残留引用（原编译阻断，见 [[lessons/UiLayoutChangeSyncPitfalls]]）。

### FormMain 状态栏裁剪（2026-08-27）+ 整机状态标签迁移（2026-09-08）

底部 `ToolStrip`(`toolStrip1`) 2026-08-27 裁剪后曾保留 3 项（`lbl_SystemStatus` 整机状态 + `lbl_Status` 流程状态 + `lbl_SystemTime` 系统时间），其余连接/操作级别静态标签已移除。**2026-09-08：`lbl_SystemStatus`/`sep_SystemStatus` 及 `InitializeSystemStatusLabel`/`OnMainDeviceStatusChanged`/`UpdateSystemStatusLabel` 三方法整页删除，整机状态显示迁移至 `MainPage.LabelStatus`（文本「设备状态：{状态值}」+ 设备颜色映射 Running=绿/Reseting=黄/Alarm=橙/EStop=红闪0.5s/Stop=蓝不闪/NoReset=灰，2026-09-08 二次定义，详见 [[api/MainPage]]）**；状态栏现仅保留 `lbl_Status` + `lbl_SystemTime`。

## UI 类资源释放规范（2026-08-19，ADR-001/034 落地）

> **UI 设计器类 `DisposeComponents()` 按需使用**：仅当持有「外部嵌套控件/独立资源」（设计器 `Dispose(bool)` 覆盖不到的代码 new 非容器控件、单例/静态事件订阅、外部对象生命周期）时编写，并由 `HandleDestroyed` 或父页面关闭调用；无嵌套/无独立资源则不需要。非 UI 类一律标准 `IDisposable.Dispose()`（见 [[decisions/ADR-002-DisposePatternFullCoverage]]）。

| UI 类 | 外部资源 | 释放方式 |
|-------|---------|---------|
| `FilebackupPage` | `_robotManager`（new KUKARobotManager）+ `GlobalCommData.CommunicationCommandReceived` | `DisposeComponents()` ← `HandleDestroyed` |
| `MonitorCamPage` | `timerStatus`/`timerPlay`（Designer 组件）+ `PreviewFrameEvent` + 回放缩略图后台线程（代数取消） | `DisposeComponents()` ← `HandleDestroyed`（`_playTooltip` 与缩略图一并释放） |
| `MainPage` | `GlobalCommData.EventInfoHandler` + `DeviceControlWork.StatusChanged` + `_statusBlinkTimer` + `_tooltip` + 轮廓轮询线程 + **2026-09-29 新增**：`checkbox1~4.CheckedChanged` + `MonitorCamManager.PreviewFrameEvent` + `_camPreviewTimer` + 自制帧副本（`Mat`） | `DisposeComponents()` ← `HandleDestroyed`（移除原 finalizer；`CurrentMat` 归相机管理器不释放） |
| `HelixRenderForm` | `_viewer`（new PointCloudViewer，含 WPF Viewport3DX） | `DisposeComponents()` ← `HandleDestroyed`（Designer.cs 已还原为标准生成代码） |
| `SystemControlPage`（原 `MotionControlPage`） | `LineLaserWorkflow.StateChanged` | `HandleDestroyed` 退订 + 停止/清理路径退订 |
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
- 模组级状态另读 `Instance.WeldStatus`（焊接过程态）与 `Instance.State`（连接态），见 [[architecture/DeviceControlArchitecture]] §13
- 弹窗范式：`AntdUI.Modal.open(new Modal.Config(this, title, message, type)) == DialogResult.OK`（owner 用 this，FormMain 为 AntdUI.Window）

## 2026-09-07 目录与命名对照

> 用户于 2026-09-07 重构 `UIDesign/`：扁平的 `SubView/` 按**业务域**拆为 `SubDialog/` 下 5 个子目录，同批 8 个类型改名。**命名空间 2026-09-14 已随目录对齐**（`ControlPage` / `TabPage` / `MainWindow` / `SubDialog.<业务域>`，ADR-005）。下表供检索旧名/旧路径使用。

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

## 三界面参数读存一致性（2026-10-23，ADR-076）

> 覆盖**系统设置页 / 工艺设置页 / 通讯调试页（文档备份设置页）**的参数与按钮一致性盘查。
> 决策与修法见 [[decisions/ADR-076-SettingsZoneSaveWiring]]，判据见 [[lessons/ConfigZoneSaveWiring]]。

### 三页面读存语义统一（不变）

| 语义 | 含义 | 是否落盘 |
|---|---|---|
| **读取** | 文件 → UI | ✗ |
| **修改** | UI → 内存 | ✗ |
| **保存** | 内存 → 文件（**只落本 UI 归属的分区**） | ✓ |

### 本轮修好的接线缺口（9 项）

| 缺口 | 归属页 | 修法 |
|---|---|---|
| ⑤工艺输出三项不落盘（赋值晚于落盘 + 落错区） | 工艺设置页 | 统一 `ApplyAdaptUiToMemory()` → 先赋值 → 再落 **③Adapt** 区 |
| 焊缝地图点数上限不落盘（UI 在系统设置页、配置归 ④Preset） | 系统设置页 | 配置项分区随 UI 落点迁移 → **①System**（XML 键路径不变） |
| 「保存焊参调整」顺带落 ①System 区（跨页副作用） | 工艺设置页 | 剥离 |
| 系统设置页「保存参数」顺带落 ④Preset 区（跨页副作用） | 系统设置页 | 剥离 |
| 振镜图形 / Y 指令用**全量** `SaveAlgorithmsConfig()` | 工艺设置页 | 改落 **④Preset / ②Quick** 分区 |
| 「读取参数」只读内存（`LoadWeldHeadConfig` 0 调用方） | 两页 | 补文件重载入口 |
| 「修改参数」与「保存焊参调整」重复写同一批 6 项 | 工艺设置页 | 收口为单一 `ApplyAdaptUiToMemory()` |
| 两页数值解析口径不一（当前文化 vs 不变文化） | 两页 | 统一 InvariantCulture 优先 + 当前文化回落 |
| 轴表刷新/编辑后清空已填「步距 / 移动目标」 | 系统设置页 | `LoadAxisRows()` 按轴名快照回填 |

### ⛔ 待业主裁决（已盘查，本轮只报不改）

| 项 | 症状 |
|---|---|
| 振镜宽/长/频三项 | 与生产链路同源（工作流每拍写 `Width=Length=amplitude`、`Frequency=查表频率`）⇒ **运行期被覆盖，界面改了不生效**；落盘值亦为死值 |
| 振镜中心 X/Y | 与光丝对中「中心补偿单写口」（ADR-059）争用 ⇒ 运行期被覆盖 |
| 通讯调试页 PLC / 以太网 Radio | 指向**空占位页**（`tabPage2`/`tabPage3`）⇒ 死选项 |
| `radioModeRSI` | 空处理器 ⇒ 纯显示死控件 |
| `btnKeepConfig`「保存配置」 | 无实效（启用开关已即时落盘） |
| 调试 Tx 单槽 | 与系统告警指令（`TxNG`/`TxAbort`）争用同一 `_txCmd` 槽 |

## 页面动作与权限边界（2026-11-17，ADR-105）

| 约定 | 内容 |
|---|---|
| 只查询不直连 | 页面不调相机/轴硬件连接方法，连接类动作统一经工作流后台线程 |
| 连接态真相源 | `ILCamPage` 以 `LineLaserWorkflow.State` 判定，硬件回填由 `StateSwitched` 边沿触发 |
| 释放不断设备 | `HandleDestroyed` 只退订事件、释放预览；设备断开归主设备关闭链 |
| 动作门控 | 关闭中 / 初始化中 / 权限不足三档拒绝并给原因；线激光手动连接需工程师及以上 |
| 模拟测试 | 启动仅管理员（`EnsureAdminForWrite`），停止与清理不受限；默认关闭、不落盘 |
| 参数显示 | 复用轴表「参数」按钮与 `AxisConfigForm`；Y 取 `ROOT/AXES/AXIS`、TA 取 `ROOT/TA_HOME`，原值显示不折算 |

## 已知问题 / 缺口

- ~~ConfigForm 分页~~：已关闭（2026-07-28 UI 整改）——`AntdUI.Pagination` 实装（Total/PageSize/ShowSizeChanger + ValueChanged lambda 切片），范式见 [[guides/AntdUI-Reference]]
- ~~`AntdUI.Chart` 数据绑定 API 未确认~~ / ~~~~`AntdUI.Chart` 已实装~~：**2026-08-12 图表全面改用 ScottPlot.FormsPlot**（MainPage **现为 2 图**：轮廓图 + 四合一工艺参数图，2026-09-29 双图化前为 5 图，见 [[decisions/ADR-049-MainPageDualChartAndCamPreview]]；DataReview 1 图），按 [[guides/Project-Tools]] 的 `AddScatter`/`AxisAuto`/`SetAxisLimits`/`Refresh` 实装；`AntdUI.Chart` 相关 `ChartDataset`/`AddPoint`/`AddDataset`/`RefreshChart` 全部移除；**2026-08-13 上午升级 5.1.59、下午回退 4.1.74**（5.x 对 .NET 4.8 设计器不友好），最终锁定 4.1 语法 `AddScatter`/`AxisAuto`/`SetAxisLimits`/`Legend`
- ~~DataReview X 轴缩放窗口（原 SetRange）~~：**已实装**（`formsPlotData.Plot.SetAxisLimits(min, max)` + `Refresh()`，见 [[guides/Project-Tools]]）→ ⚠️ **2026-11-02 该入口随「按 X 范围显示区域」模块整体移除**（滑块 `uiTrackBar1` 已删，`DataReviewerPage` 不再有 X 轴范围缩放入口）；`SetAxisLimits` API 本身在 `MainPage` 轮廓图仍在用
- 变量命名遗留：`uiDataGridView1`（实为 `AntdUI.Table`）、`uiLightStatus`（实为 `AntdUI.Signal`）、`uiCalendar1`（实为 `DatePicker`）等，功能无碍
- AntdUI 控件 API 与 WinForms/SunnyUI 差异迁移坑（Select 无 DataSource / Column.Width 为 string / GridPanel 单参数 Add / Splitter 继承 SplitContainer / Table 数据一律代码后置 Binding()、Designer 内禁 DataSource+AntList / 设计器 System.Void 多为级联）：见 [[guides/AntdUI-Reference]]；MainPage 已由可拖拽 `AntdUI.Splitter` 改为**整页 AntdUI.GridPanel 嵌套固定区域**（外层 uiGridPanelMain「上 68% 顶端分栏 / 下 32% 日志信息」+ 内层 uiGridPanel1「左 40% / 右 60%」，全部不可拖动）：见 [[guides/AntdUI-Reference]]。⚠️ **2026-09-29 顶层容器再改为 `tableLayoutPanel3`（6 列 × 2 行），`uiGridPanelMain`/`uiGridPanel1` 已自设计器删除**：见 [[decisions/ADR-049-MainPageDualChartAndCamPreview]]
- SunnyUI `UIMessageBox`（ShowError/ShowWarning/...）在 AntdUI 不存在 → `AntdUI.Modal.open(Modal.Config{Icon=...,Draggable=true})`（模态可拖拽）或 `AntdUI.Message.*`（Toast）；非 UI 类 owner 用 `Form.ActiveForm`/`null`，迁移后删 `using Sunny.UI`：见 project/SunnyUI-Legacy（归档页 2026-09-17 删除，迁移史见 [[decisions/ADR-008-UIFrameworkMigration]]）。UserControl 内 `Message`/`Modal` 的 owner 须为 `null`/`Form.ActiveForm`（`Target` 不支持 `UserControl` 隐式转换，编译报 CS1503）：见 [[guides/AntdUI-Reference]]
- [[guides/WinForms-Designer]]：Designer.cs Dispose 不可修改
- [[guides/Namespace-Compilation]]、[[guides/WinForms-Designer]]、[[guides/WinForms-Designer]]、[[guides/WinForms-Designer]]

## 相关页面

- [[decisions/ADR-008-UIFrameworkMigration]] — 迁移决策与完成状态
- [[decisions/ADR-010-LayoutContainerFreedom]] — 布局容器自由化（解除 GridPanel/FlowPanel 强制使用）
- [[guides/AntdUI-Reference]] — 开发范式（权威）
- [[guides/Project-Tools]] — 图表承载统一用 ScottPlot.FormsPlot 4.1.74（2026-08-12 替换 AntdUI.Chart，2026-08-13 升级 5.x 后回退 4.1.74）
- [[decisions/ADR-008-UIFrameworkMigration]] / [[guides/AntdUI-Reference]] — 迁移决策与追踪
- ADR-002（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[decisions/ADR-001-CS73-Constraint]]

---

*来源：raw/skills/02-Development/UISpecialist.md + raw/knowledge/AdaWeldSystem_Wiki.md；2026-07-28 依 ADR-004 迁移完成状态全面改写为 AntdUI。*
