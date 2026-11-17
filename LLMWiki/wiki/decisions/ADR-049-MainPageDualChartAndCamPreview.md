---
title: ADR-049 主界面双图化与监控相机预览接入
date: 2026-09-29
updated: 2026-10-30
tags: [决策, UI, MainPage, ScottPlot, 监控相机, 预览, 30Hz, 设计器]
status: accepted
---

# ADR-049：主界面双图化与监控相机预览接入

> **2026-09-29 同日修订**：决 1 的复选框文本/默认勾选态、决 2 的预览 `ImageBox`，由「代码后置创建 / 回填」改为**设计器声明**。业主口径：**控件要能在设计器上看到，不接受全部动态加载**。首版的两种代码后置做法保留在「备选方案」中存沿革，正文按现行事实描述。**同日二次修订**：图表容器 `tableLayoutPanel2`（WinForms TableLayoutPanel）→ `gridPanel2`（`AntdUI.GridPanel`，`Span` 布局），见决 1。**同日三次修订**：复选框对齐 [[modules/UIDesign]] 范式——设计器语义化命名 + 代码后置直接引用（删平行数组装配法），见决 1。

## 背景

主页面 `MainPage` 原为 **5 张 ScottPlot 图**：1 张线激光轮廓图（`formsPlot1`）+ 4 张各自独立的工艺参数图（焊缝宽度 / 机器人运动速度 / 送丝速度 / 激光功率，分别占 `formsPlot2/3/4/5` 与 `panelChart2/3/4/5`）。

业主于 2026-09-29 在 Visual Studio 中**重排主界面布局**（设计器已定稿）：5 张图精简为 **2 张**——

1. 线激光轮廓图不变（`formsPlot1`，位于 `panel1`）；
2. 其余四路数据集合到**一张图**（`formsPlot2`，位于 `panelChart2`），并在图上新增 **4 个显隐复选框**（`checkbox1~4`，位于 `flowLayoutPanel1`，容器为 `gridPanel2` 行 1）；
3. 新增 `panelCam` 面板（`tableLayoutPanel3` 第 2 列第 0 行），用于**监控相机预览**，要求 **30Hz 显示刷新**并接入实时画面；
4. 顶层容器由 `uiGridPanel1/uiGridPanelMain` 改为 `tableLayoutPanel3`（6 列 × 2 行），`panelChart3/4/5` 与 `formsPlot3/4/5` 已从设计器删除（`uiGridPanel` 亦删除）。

**该布局改版同时暴露一处一致性缺口**：`MainPage.cs`（代码后置）仍引用已被删除的 `formsPlot3/4/5`（`RefreshParamCharts` / `AfterInitializeUI`），属**编译阻断**（CS0103 名称不存在），必须在同一轮内收敛。该缺口已沉淀为教训页 [[lessons/UiLayoutChangeSyncPitfalls]]。

## 决策

### 决 1 — 四路工艺参数合并为「四合一图」，共用单套坐标轴

`formsPlot2` 承载 4 条系列（焊缝宽度 / 运动速度 / 送丝速度 / 激光功率），**沿用 [[modules/UIDesign]] 的既有范式**：

- ScottPlot 4.1 **无逐系列 `Visible` 属性** ⇒ 勾选变化与数据到达时 `Plot.Clear()` → 按勾选态 `AddScatter` 重建 plottable → `AxisAuto()` → `Legend()` → `Refresh()`；
- 删去原多图专用的 `BindChartVar(chart, name, data)`，改为 `AddSeries(chart, name, data, color)`（不含 `Refresh`，由外层统一刷新一次）；
- 图表标题/轴标签由新增的 `SetupMergedChart(formsPlot2)` 承担（标题「工艺参数实时曲线」，X=机器人 X 轴，Y=参数值）；
- 4 个复选框由**设计器声明**（2026-09-29 三次修订起语义化命名）：其 `Text`（`chkSeamWidth`=焊缝宽度 / `chkRobotSpeed`=运动速度 / `chkFeedSpeed`=送丝速度 / `chkLaserPower`=激光功率）与 `Checked = true`（默认全选）**均写入 `MainPage.Designer.cs`**；代码后置**构造函数逐个订阅** `ChkSeries_CheckedChanged`，重建图表时按 `chk*.Checked` **直接引用**（系列名/色板常量与 [[modules/UIDesign]] 同源，无平行数组）；
 - 因事件订阅发生在 `InitializeComponent()` **之后**，设计器回填的勾选态**不会**触发处理器，故**不再需要**抑制标志（首版的 `_loadingSeriesToggles` 已删）；
 - 勾选事件**只在代码后置订阅一处**（构造函数逐个订阅，每个复选框 `MainPage.cs` ×1 / `MainPage.Designer.cs` ×0），杜绝「一次操作触发两次」；
- 系列配色沿用 Ant Design 标准色板（与 `DataReviewerPage` 同源）：焊缝宽度 `(24,144,255)` / 运动速度 `(114,46,209)` / 送丝速度 `(82,196,26)` / 激光功率 `(250,173,20)`。
- 图表容器 `tableLayoutPanel2`（WinForms `TableLayoutPanel`，ColumnStyles/RowStyles 布局）→ **`gridPanel2`**（`AntdUI.GridPanel`，`Span = "fill;fill-40 100%"`：`-` 后为全局行高表——行 1 高 40 固定承载 `flowLayoutPanel1`，行 2 高 100% 承载 `formsPlot2`；语法见 [[guides/AntdUI-Reference]] §2.2）。
 - **逆序入格**：期望格子顺序为行 1=`flowLayoutPanel1`、行 2=`formsPlot2`，故 `Controls.Add` 必须写倒序（先 `formsPlot2` 后 `flowLayoutPanel1`）。
 - 命名同步由 `tableLayoutPanel2` 改为 `gridPanel2`（类型/名称不错位；代码后置与 resx 对该名零引用，重命名无涟漪）。

> ⚠️ **2026-11-10 布局演进（决 1 仍有效，容器形态更新）**：业主弃用 `flowLayoutPanel1` 与 `gridPanel2`，5 个复选框（新增 `chkWireZ`）改为**悬浮在 `formsPlot2` 右上角**（`Anchor=Top|Right`、`BackColor=White`；`panelChart2.Padding` 复位为 `(2)`，绘图区不再被挤窄；z 序由 `KeepSeriesTogglesOnTop()` 校正）。上两行的 `flowLayoutPanel1`/`gridPanel2` 结构保留为历史记录。

**未采用多 Y 轴**（`Plot.AddAxis(Edge.Right, n)` + `plottable.YAxisIndex = n` 分别承载不同量纲）：一方面 `DataReviewerPage` 已就「七系列混合量纲共用单轴」定型，本页与之保持同范式；另一方面多轴 API 在本沙盒**无 C# 编译器**的环境中无法真编译验证（见 rules/KR-010），不宜在本轮引入未经验证的 API。

### 决 2 — `panelCam` 预览：ImageBox 设计器声明 + 30Hz 显示节拍

> ⛔ **2026-10-22 演进：本决已废止** —— 业主需求「监控画面不输出到主界面」，`panelCam` / `imageBoxCam` 与 30Hz 节拍、帧所有权代码已从 `MainPage` 全部删除（行 0 重排为 `panel1` span3 + `PanelDashborad` span3）。下方内容保留为历史；现行预览唯一承载页 = [[modules/MonitorCam]]（`PreviewFrameEvent` 订阅方）。

- 预览控件 `imageBoxCam`（**`Emgu.CV.UI.ImageBox`**，`Dock=Fill`）**声明于 `MainPage.Designer.cs`**，由设计器挂入 `panelCam.Controls`。设计器装配四件套：`new` 实例化 + 属性块 + `panelCam.Controls.Add(this.imageBoxCam)` + 私有成员声明。
- **设计器必需配套（缺一即报错）**：
 - `ImageBox` 实现 `ISupportInitialize` ⇒ 必须成对写 `((System.ComponentModel.ISupportInitialize)(this.imageBoxCam)).BeginInit()` / `EndInit()`；
 - `panelCam` 首次承载子控件 ⇒ 必须成对补 `this.panelCam.SuspendLayout()` / `ResumeLayout(false)`；
 - 属性块需含 `FunctionalMode = ImageBox.FunctionalModeOption.RightClickMenu` 与 `SizeMode = StretchImage`（与 [[modules/MonitorCam]] 的 `imageBox1` 同范式）。
- **业主口径（2026-09-29）**：新增控件须**在设计器可见**，**不接受**「全部动态加载」；故本轮把 `ImageBox` 从代码后置创建**迁回**设计器。落地方式为**字节安全脚本**改 `MainPage.Designer.cs`（保持纯 CRLF、无 BOM，本轮净增 20 行；参见 [[guides/WinForms-Designer]]）。
- **帧源** = `MonitorCamManager.Instance.PreviewFrameEvent`（连续取流时逐帧抛出；2026-09-29 同日二次修订：**每订阅方独立副本**，订阅方收到即拥有并负责释放，见 [[decisions/ADR-048-MonitorCamTabsRecordPlayback]] 三次补充节）；软触发单帧（`TriggerSingleShot`）不经该事件。**双订阅方模式（业主确认）**：主页 = 运行时自动模式预览，调试页（MonitorCamPage）= 点采集手动模式预览。
- **显示刷新 30Hz 且与相机帧率解耦**：相机线程回调**只入待显示槽**（`Interlocked.Exchange`），UI 侧 `_camPreviewTimer`（`Interval=33ms`，常量 `CamPreviewIntervalMs`）按节拍取帧上屏。理由与轮廓轮询（`ProfilePollIntervalMs=33`）同源：**显示频率由主界面统一决定**，不跟随相机帧率。
- **回退路径**：无新预览帧时显示 `MonitorCamManager.Instance.CurrentMat`（单次采集写入的当前帧），覆盖「软触发 / 工作流采集」场景。
- 页面不可见（切到其它标签页）时丢弃待显示帧，不做无谓的位图转换。

### 决 3 — 预览帧的「所有权与释放」约定

> ⛔ **2026-10-22 演进：本决随主界面预览移除一并废止**（`MainPage` 不再订阅 `PreviewFrameEvent`、不再持有 `Mat` 副本）。帧所有权契约本身仍适用于 [[modules/MonitorCam]]。

| 帧来源 | 所有权 | 释放责任 |
|---|---|---|
| `PreviewFrameEvent` 抛出的副本（**每订阅方独立副本**，2026-09-29 二次修订） | **本页** | 上屏后被新帧替换时、被新帧顶替而未上屏时、页面销毁时 `Dispose()` |
| `MonitorCamManager.CurrentMat` | **相机管理器** | 本页**只读不释放**（用 `_displayedFrameOwned` 标志区分） |

上屏时序：`imageBoxCam.Image = next`（`ImageBox` 继承 `PictureBox`，赋值即转位图）→ 记录新旧所有权 → 释放上一帧（仅当其为自有副本且与当前帧非同一实例）。

## 备选方案

| 方案 | 放弃原因 |
|---|---|
| 保留 4 张独立图 | 与业主已定稿的新布局冲突（`formsPlot3/4/5` 已删除） |
| 四系列共用多 Y 轴（量纲分离） | 与 `DataReviewerPage` 单轴范式不一致；无编译器环境引入未验证 API 风险偏高 |
| ~~`ImageBox` 由代码后置创建（2026-09-29 首版做法）~~ | 业主裁定控件须在设计器可见、不接受全部动态加载。原顾虑是「改动刚定稿的 Designer 风险高」，实测经字节安全脚本改动量仅 20 行、BOM/CRLF 无损，风险可接受 |
| ~~复选框文本/默认勾选态在代码后置回填（首版做法）~~ | 同上。且回填发生在事件订阅之前时本就无需抑制标志，为回填专门保留一个抑制状态反成易被误删的负担 |
| 预览帧到达即直接上屏（事件驱动） | 刷新率被相机帧率绑架，与「显示频率由主界面统一决定」既定原则相悖 |

## 后果

### 正面

- 主界面图表数量 5 → 2，布局与业主定稿一致，四路参数曲线同屏可比、可逐个显隐。
- 主界面具备监控相机**实时预览**能力（30Hz），无需切到「相机设置」页即可观察焊接画面。
- 数据源（`WeldParamManager` 的四个 `ChartVar`）与轮询链路**零改动**：仅显示侧由「4 图」改为「1 图 4 系列」。
- 代码后置残留引用（`formsPlot3/4/5`）在同一轮内收敛，编译阻断解除。
- 预览控件与复选框在**设计器即可见**，布局评审不必依赖运行期观察；`MainPage.cs` 侧亦不再持有控件创建代码。

### 负面 / 约束

- 四系列量纲不同（mm / mm·s⁻¹ / m·min⁻¹ / W）共用单轴，小量程系列在自动缩放下可能被压扁；需要分别读数时用复选框单独勾选。
- 复选框勾选变化走「清空重建 plottable」路径，系列点数大时可感知一次重绘开销（与 `DataReviewerPage` 同等代价，量级可接受）。
- 预览为「显示侧节流」：相机帧率高于 30Hz 时只显示约 1/3 的帧，**不影响**分析链路（分析走 `FrameCompletedEvent`，与本预览互不相干）。
- `MainPage.Designer.cs` 现已含 `Emgu.CV.UI.ImageBox` ⇒ 该页设计器**依赖 `Emgu.CV.UI` 程序集引用**（csproj 已含，与 [[modules/MonitorCam]] 同源）；打开设计器需能解析该控件类型。
- 设计器文件后续任何修改须走**字节安全流程**（保持纯 CRLF、无 BOM、`\r\r\n` 为 0），否则 `git diff` 会整篇膨胀。

## 相关页面

- [[api/MainPage]] — 主页面 API（本轮字段/方法/释放清单同步更新）
- [[modules/UIDesign]] — UI 模块页
- [[api/MonitorCamManager]] — 预览帧源（`PreviewFrameEvent` / `CurrentMat`）
- [[modules/UIDesign]] — 多系列共图 + 复选框显隐的既有范式来源
- [[guides/WinForms-Designer]] — 设计器文件修改规范与 `Dispose(bool)` 禁令
- [[guides/AntdUI-Reference]] — GridPanel.Span 语法与逆序入格规则（§2.2）
- [[decisions/ADR-011-ButtonShadowDeviceSwitch]] — 同文件「运行期生成动态控件集合」的既有先例（`ButtonShadow` 常驻按钮；本轮预览控件未采用此法）
- [[decisions/ADR-048-MonitorCamTabsRecordPlayback]] — 连续取流与 `PreviewFrameEvent` 契约来源
- [[lessons/UiLayoutChangeSyncPitfalls]] — 本轮踩坑与门禁
- [[lessons/UiRefreshUnifiedEntry]] — UI 刷新单一入口原则
- ⚠️ **2026-10-22 演进**：决 2 / 决 3 已废止（主界面预览移除）；决 1「双图化」仍有效。落地页 [[api/MainPage]]
