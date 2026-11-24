---
title: MainPage 主页面
date: 2026-08-27
tags: [API, UI, 主页面, ScottPlot, 英莱, 轮廓, 实时曲线]
source: AdaWeldSystem/UIDesign/ControlPage/MainPage.cs + .Designer.cs
---

# MainPage — 主页面

> 🔄 **2026-11-23 轮廓门禁改写**：`ProfilePollLoop` 的轮廓显示判据由 `RunMode != Manual` 改为 `dc.IsAutoWeldingRunning || dc.IsSimulationEnabled`——模拟启动时 UI 把线激光流程置 `Manual`，旧判据会误挡模拟轮廓；手动调试切回主页面则调 `HideContourForManual` 隐藏轮廓线与特征点并清零版本（切回自动/模拟按最新帧恢复）。工艺曲线轮询不受影响。见 [[decisions/ADR-100-state-union-and-action-gate]] D30 · [[lessons/SimulationAutoBranching]] 陷阱二十二。
>
> 🔄 **2026-11-20 两处显示修复**：① **轮廓显示仅自动模式**：`ProfilePollLoop` 在消费 `LineLaserManager.Profile` 前判 `LineLaserWorkflow.Instance.RunMode != Manual`（判据来自 [[api/DeviceStateApiCore]] 的 `WorkflowRunMode`，手动调试由 `LineLaserCamPage`/主页快捷开关置 Manual，自动流程由 `DeviceControlWork` 置回 Auto）；手动时主页不显示轮廓、线激光调试页照常显示，工艺曲线轮询不受影响。② **SignalXY 单调化**：`ApplyProfileSnapshot` 拷入 `_contourSignalXs` 时剔除 X（物理 Y）回退点（仅 `x > lastX` 才写 X/Z 对），消除换新相机后 `formsPlot1.Refresh()` 的 `xs must not descend` 异常；渲染点数取实际写入数。见 [[lessons/ScottPlotSignalXyMonotonicPitfall]]。
>
> 主显示页面（`AdaWeldSystem.UIDesign.ControlPage` `UserControl`），承载英莱线激光轮廓 ScottPlot Signal 图 + 4 条实时数据曲线（焊缝宽度/机器人运动速度/送丝速度/激光功率）+ 全局日志框。2026-08-27 经五维度代码精简（删未用字段/死函数、内联 LoadComponent、补 5 #region、public 方法归集、XML 注释补全）。2026-08-31 改用 **AntdUI `ButtonShadow` 常驻按钮**（[[decisions/ADR-011-ButtonShadowDeviceSwitch]]，替代已废弃的 FloatButton 覆盖层方案）：6 个硬件快捷开关（焊接头/线激光/监控相机/运动控制器/机器人通讯/PLC通讯；徽标红=断开 绿=连接；仅线激光实现真实连接/断开切换，其余硬件暂未接入，点击提示「暂未接入」），构造函数中代码后置创建并直接放入 **`panelfloatbutton` 面板**（MainPage 底部 54px 全宽条，`PanelDashborad` 内 `tableLayoutPanel1`），随页面显隐自动生效。**同日风格迭代（形态对齐 AntdUI Demo `buttonShadow1`）**：50×50 阴影按钮**仅显示 SVG 图标**（默认 poweroff 电源 SVG）、设备名经 **`TooltipComponent` 顶部提示**（`ArrowAlign=TAlign.Top`）、连接态由**原生徽标属性** `Badge=""`+`BadgeMode=true`+`BadgeBack` 红/绿承载；预留接口 `SetDeviceIconSvg`/`SetDeviceBadgeSvg`。
>
> **2026-09-29 主界面双图化 + 监控相机预览（[[decisions/ADR-049-MainPageDualChartAndCamPreview]]）**：业主于 VS 重排布局，**5 张图精简为 2 张**——①线激光轮廓图 `formsPlot1`（`panel1`）不变；②其余四路数据（焊缝宽度/运动速度/送丝速度/激光功率）**合并到 `formsPlot2`（`panelChart2`）一张图**，图上新增 **4 个显隐复选框**（`chkSeamWidth/chkRobotSpeed/chkFeedSpeed/chkLaserPower`，位于 `flowLayoutPanel1`（`gridPanel2` 行 1））；③新增 **`panelCam`** 面板承载**监控相机预览**（`Emgu.CV.UI.ImageBox`，**30Hz 显示刷新**）；④顶层容器 `uiGridPanel1`/`uiGridPanelMain` → **`tableLayoutPanel3`**（6 列 × 2 行），`panelChart3/4/5`、`formsPlot3/4/5` 与 `uiGridPanel*` 已自设计器删除。同轮收敛代码后置对已删控件的残留引用（原为编译阻断，见 [[lessons/UiLayoutChangeSyncPitfalls]] 坑一）。**2026-09-29 同日修订**：预览 `ImageBox`（`imageBoxCam`）与 `checkbox1~4` 的文本/默认勾选态**改由 `MainPage.Designer.cs` 声明**（业主口径：控件须在设计器可见，不接受全部动态加载）；代码后置只保留数据绑定与事件订阅，首版的动态创建与 `_loadingSeriesToggles` 回填抑制已删除。**同日二次修订**：图表容器 `tableLayoutPanel2`（WinForms TLP）→ **`gridPanel2`**（`AntdUI.GridPanel`，`Span="fill;fill-40 100%"`＝行 1 高 40 承载 `flowLayoutPanel1`、行 2 100% 承载 `formsPlot2`，逆序入格），命名同步修正（[[decisions/ADR-049-MainPageDualChartAndCamPreview]]）。**同日三次修订**：复选框对齐 [[modules/UIDesign]] 范式——设计器**语义化命名**（`chkSeamWidth/chkRobotSpeed/chkFeedSpeed/chkLaserPower`），代码后置删 `_seriesToggles` 等四个平行数组与 `InitSeriesToggles`，改为构造函数逐个订阅 + 重建按 `Checked` 直接引用（`IsDisposed` 销毁守卫）。

> **2026-10-22 主界面监控预览移除（⚠️ 覆盖下方 2026-09-29 / 2026-10-10 预览条款）**：按业主需求「监控画面不输出到主界面」，设计器删除 `panelCam` + `imageBoxCam`（控件实例化 / 属性块 / `Controls.Add` / 字段声明 / `ISupportInitialize` / Suspend-Resume 全清），行 0 重排为 `panel1`(0,0,`SetColumnSpan=3`) + `PanelDashborad`(3,0,`SetColumnSpan=3`)；代码后置删除 `InitCameraPreview` / `OnMonitorPreviewFrame` / `CamPreviewTimer_Tick` 与 `_camPreviewTimer` / `CamPreviewIntervalMs` / `_pendingPreviewFrame` / `_displayedFrame` / `_displayedFrameOwned`，并移除 `using AdaWeldSystem.MonitorCam` / `using Emgu.CV`。预览帧源与调试页预览**不变**（[[modules/MonitorCam]] 仍订阅 `PreviewFrameEvent`）。决策演进见 [[decisions/ADR-049-MainPageDualChartAndCamPreview]]（决 2 / 决 3 废止，决 1 双图化仍有效）。

> **2026-11-10 业主界面改版（覆盖上文的复选框容器与统计显示条款）**：①设计器删除 `flowLayoutPanel1` 与 `gridPanel2`，5 个复选框（`chkSeamWidth/chkWireZ/chkLaserPower/chkFeedSpeed/chkRobotSpeed`）作为 `panelChart2` 子控件**悬浮在 `formsPlot2` 右上角内侧**（`Anchor=Top|Right`，行高 44 / 间距 56，`BackColor=White` 与图表同色；`panelChart2.Padding=(2)` 复位，`formsPlot2` Dock=Fill 拿回完整绘图区；z 序由 `KeepSeriesTogglesOnTop()` 在构造与每次刷新后校正）；②设计器删除统计 label `label3/4`（运行时长）、`label5/6`（焊接数量）、`label7/8`（完成数量）、`label11`+`lblRobotCommand`（机器人指令）；`RefreshDashboard`/`_dashTickCounter` 及全部控件引用已删，统计值现无显示出口（待业主定）；③流程步骤条 `steps1` 经业主指示**已补回**（见下条现状说明），`gridLeftBlock` 由 `label3~label8` 等长表改为两行串格 `"120:fill;fill"`：`LabelStatus`（120px）+ `steps1`（fill）。

## 🔄 ADR-054 变更（2026-10-09 accepted）

| 项 | 变更 |
|---|---|
| **工艺参数曲线** | 4 Checkbox **改五项互斥单选**（接头宽 / 运动速度 / 送丝速度 / 激光功率 / 送丝Z轴位置）。控件形态用 **Checkbox + `ApplySeriesSingleSelection` 手动互销**（⛔ 不用 `AntdUI.Radio`：类名是 `Radio` 非 `RadioButton`，其事件名无先例且 DLL 混淆扫不出）。新增 `_suppressSeriesEvent` 防互销重入；取消勾选时**不互销**（允许取消到最后一项） |
| **文案** | 「焊缝宽度」→「**接头宽**」（控件 `Text` + 图例常量 `NameSeamWidth`）。⛔ 字段名与数据源 `SeamWidth` **不改**（牵连 `WeldParamOutput`/`ChartVar`/记录 Schema） |
| **送丝Z轴位置** | `chkWireZ` + `WireZ`（`ChartVar`）已建并接入 `RefreshParamCharts`，但后端 `TaPositionMm` 未落地 ⇒ 序列保持空，`AddSeries` 直接 return。⛔ **禁画恒 0 假曲线** |
| **状态栏** | 去「设备状态：」前缀；报警/急停档改调 `BuildAlarmText`（温控 → 从站报警位 → 兜底「请检查设备」）；未知态**禁 `state.ToString()` 直出**，枚举名只进日志 |
| **模组** | 名表 6 → **4 项**（线激光/监控相机/控制器/机器人）。⚠️ `LineLaserSwitchIndex` 同步 **1 → 0**（改名表必须同步改本值，否则操作错设备）。**2026-10-10：4 项状态全部接实际设备**（线激光/监控相机/控制器=各自工作流 `SubDeviceState.Connected`，机器人=`IsRobotOnline`），`RefreshDeviceSwitchUi` 改 `bool[] _lastDeviceConnected` 逐设备快照——此前仅线激光联动，监控相机/控制器已连接仍显示红叉（上机实测报障） |

详见 [[decisions/ADR-054-MainPageSingleSelectionAndAlarmText]]。

## 🔄 仪表盘容器多层 GridPanel 化（2026-10-09 修复乱排）

`PanelDashborad` 内 `tableLayoutPanel1`：原 `TableLayoutPanel`（4 列×13 行 + `SetRowSpan`×4 + `SetColumnSpan`×1）
2026-10-09 首轮换 `AntdUI.GridPanel` 时**平铺 52 格 vs 20 控件 + 合并未表达 + 行高机制混用** ⇒ 乱排。
本轮按**多层 GridPanel**（业主裁定）忠实还原，**A/B 运行期对照 20/20 控件与原版几何全等**：

| 层 | 控件 | Span | 格序（行主序） |
|---|---|---|---|
| 外层 | `tableLayoutPanel1` | `fill 20 100`（resx） | [gridLeftBlock][divider1][gridRightBlock] |
| 左块 | `gridLeftBlock` | `fill;133 fill;133 fill;133 fill;133 fill;133 fill;-40 30 30 30 120 120` | [LabelStatus] [label3|label4] [label5|label6] [label7|label8] [label11|gridRobotVals] [label9|gridHeadVals] |
| 右块 | `gridRightBlock` | `fill;fill;-40 100%` | [label2][panelfloatbutton] |
| 机器人值栈 | `gridRobotVals` | `fill;fill;fill;fill;-30 30 30 30` | [label13][label15][label1][label17] |
| 焊接头值栈 | `gridHeadVals` | `fill;fill;fill;fill;-30 30 30 30` | [label10][label12][label18][label19] |

> ⚠️ **2026-11-10 业主改版后现状（上表为 2026-10-09 历史快照）**：`label3/4`、`label5/6`、`label7/8`、`label11`+`lblRobotCommand`、`gridHeadVals`、`pictureBox1`、`gridPanel2`、`flowLayoutPanel1` 均已从设计器删除；`steps1` 已按业主指示补回并改为**横排**（`Vertical=false`）。容器为 `gridTopBlock.Span = "60:fill;80:fill;fill"`（行 1 高 60 = `LabelStatus`，行 2 高 80 = `steps1`，行 3 fill 空置），2 个子控件对 2 格、格序按 `Controls` 索引倒序分配，无空洞格。

**三条落地要领**（实证见 [[guides/AntdUI-Reference]] §2.x）：
1. **逆序入格**：每层 `Controls.Add` 顺序 = 格序倒序（代码内有注释锚点）；
2. **包装 GridPanel 一律 `Margin = new Padding(0)`**——嵌套层默认 Margin=3 会叠加出 +3/+6 偏移（A/B 实测 M0=零偏差，M3=偏移）；
3. 跨行/跨列合并（原 `SetRowSpan`/`SetColumnSpan`）**只能靠嵌套**表达——`_N` 语法在本 DLL 实测把合并格打成 1px/0px，⛔ 不可用。

## 基本信息

| 项 | 值 |
|----|----|
| 类 | `AdaWeldSystem.UIDesign.ControlPage.MainPage` |
| 基类 | `System.Windows.Forms.UserControl` |
| 文件 | `UIDesign/ControlPage/MainPage.cs` + `.Designer.cs` |
| 命名空间 | `AdaWeldSystem.UIDesign.ControlPage` |
| 依赖 | `AdaWeldSystem.Comm.SystemComm`、`WeldParamControl`、`LineLaserCam`、`LineLaserCam.IntelligentLaserCam`、`PCLOperate.Models`、`MainDeviceControl.DeviceWorkflow`(LineLaserWorkflow / MonitorCameraWorkflow)、`MainDeviceControl.DeviceStateApiCore`(三态枚举)、`ScottPlot`、`Emgu.CV.UI`(`imb_WeldViewer`)、`Emgu.CV`(`Mat`)；⛔ 代码后置**不依赖 `MonitorCam`(`MonitorCamManager`)**——预览帧经 `MonitorCameraWorkflow.WeldPreviewFrame` 取得，不直连管理器 |

## #region 结构（2026-08-27 精简后）

| Region | 成员 |
|--------|------|
| 公共变量 | `LogAppendDelegate(Color, string)`（委托类型） |
| 私有变量 | `SeamWidth`/`robotSpeed`/`LaserPower`/`FeedSpeed`（ChartVar）、`_contourSignalData`/`_contourSignalXs`/`_contourSignalPlot`(SignalPlotXY)/`_featurePointPlot`/`_featureXs`/`_featureYs`/`_contourCamera`（轮廓图）、`_contourYMin/Max`/`_contourZMin/Max`/`_contourAxisLocked`（轴范围默认回退，含负值）、`_uiUpdatePending`/`_snapPointCount`/`_snapHasResult`/`_snapFeatureY`/`_snapFeatureZ`/`_pendingAxisLock`（合并派发+快照）；**硬件开关**：`_deviceButtons`(AntdUI.ButtonShadow[] 4 常驻按钮)/`_deviceAlerts`(AntdUI.Alert[] 4 区域设备名 Alert，**2026-10-22 新增**，与按钮等高、Success/Error 表示连接态)/`_tooltip`(TooltipComponent 顶部提示)/`_deviceIconSvgs`(各设备图标 SVG 缓存，设备指向不同)/`_lastDeviceConnected`(bool[] 各设备连接态快照，2026-10-10 取代单值 `_lastLlConnected`)/`_deviceSwitchNames`(4 设备名：线激光/监控相机/控制器/机器人)/`LineLaserSwitchIndex=0`/`DeviceBadgeRed`+`DeviceBadgeGreen`+`DeviceBackDisconnected`(static readonly 徽标与底色配色)/`ConnectedBadgeSvg`="CheckCircleFilled"+`DisconnectedBadgeSvg`="CloseCircleFilled"(const 徽标图标)/`DefaultDeviceIconSvg`(const poweroff SVG 默认图标)；**焊接预览**：`_weldPreviewFrame`(Mat，当前上屏帧，本页拥有并释放) |
| 构造函数 | `MainPage()` |
| 私有函数 | `MainPage_HandleDestroyed`/`SubscribeContourCamera`/`IlCamera_ContourDataReady`/`UpdateChartUI`/`BindChartVar`/`AfterInitializeUI`/`CommenData_EventInfoHandler`/`inputLog_TextChanged`/`MainPage_Shown`/`OnWeldPreviewFrame`/`ShowWeldPreviewFrame`/`DisposePreviewFrame`（后三者为 2026-11-11 焊接预览） |
| 公共函数 | `DisposeComponents`/`AddContourLineChart`/`AddNewDataLineChart`/`LogAppend` |
| 硬件快捷开关（AntdUI ButtonShadow，ADR-011） | `InitDeviceSwitchButtons`(构造函数创建 4 组「ButtonShadow + 等高 Alert」常驻 `panelfloatbutton` 面板，**2026-10-22 起 2×2 区域布局**)/`LayoutDeviceSwitchAreas`(按面板 ClientSize 核算 2×2：按钮与 Alert 等高、区内 1px、区间 8px，**2026-10-22 新增**)/`OnPanelFloatButtonSizeChanged`(面板尺寸变化重排，2026-10-22 新增)/`OnDeviceSwitchClick`(点击分发)/`IsLineLaserRunning`(依 `LineLaserWorkflow.Instance.State == Connected` 判定连接态)/`ToggleLineLaserConnection`(线激光 ConnectOn/ConnectOff 切换)/`RefreshDeviceSwitchUi`(public 单一刷新入口，**2026-10-10 起 4 设备各自快照逐个刷新**，见下方关键方法行)/`SetDeviceIconSvg`(public 预留接口：替换按钮图标 SVG)/`SetDeviceBadgeSvg`(public 预留接口：设置徽标 SVG) |
| 焊接流程步骤条（`steps1`，2026-10-22；2026-11-10 删除后补回、同日改横排只显示标题） | `InitWeldFlowSteps`(按 `WeldFlowSteps` 建 5 项 + 初始安全位 + 建悬停提示文本)/`SetWeldFlowStep`(只前进守卫 + 变更日志 + 写 `Current/Status`)/`ResetWeldFlow`(复位回安全位)/`ApplyWeldFlowDeviceStatus`(整机态联动)/`OnWeldParamWeldStatusChanged`(焊接态事件封送)/`ApplyWeldFlowWeldStatus`(焊接态兜底联动)/`AdvanceWeldFlowByCommand`(机器人指令推进)/`OnWeldFlowStepsMouseMove`(按 `StepsItem.rect` 命中步骤并弹提示)/`OnWeldFlowStepsMouseLeave`(隐藏提示) |

> 2026-08-27 将 4 个 public 方法由散落位置归集到末尾 `公共函数` region，强制成员顺序：私有变量→公共变量→构造函数→私有函数→公共函数。
>
> **演进（2026-09-20）**：①轮廓显示已由 `IlCamera_ContourDataReady` 回调改为 `ProfilePollLoop` 独立线程轮询（`SubscribeContourCamera`/`IlCamera_ContourDataReady` 已删除，本表相关行沿革保留）；②工艺曲线喂数已由 `WeldProcessCompleted` 事件订阅改为同一轮询循环按版本号增量拉取（构造函数不再订阅、`DisposeComponents` 不再退订该事件）。

### 2026-09-29 双图化新增成员（[[decisions/ADR-049-MainPageDualChartAndCamPreview]]）

| Region | 成员 |
|--------|------|
| 私有变量（新增） | **四合一图**：系列名/色板常量（`NameSeamWidth/NameRobotSpeed/NameFeedSpeed/NameLaserPower` + `Color*`，与 [[modules/UIDesign]] 同源；2026-09-29 三次修订删平行数组）；~~**预览**：`_camPreviewTimer`(System.Windows.Forms.Timer) / `CamPreviewIntervalMs=33`(const) / `_pendingPreviewFrame`(Mat) / `_displayedFrame`(Mat) / `_displayedFrameOwned`(bool)~~（⛔ 2026-10-22 已删）；**设计器声明（非本类字段）**：~~`imageBoxCam`(Emgu.CV.UI.ImageBox)~~（⛔ 2026-10-22 已删）与 `checkbox1~4`(文本/默认勾选态) — 见 `MainPage.Designer.cs` |
| 四合一工艺参数图（复选框显隐） | `ChkSeries_CheckedChanged`（构造函数逐个订阅；订阅点唯一） |
| ~~监控相机预览（panelCam，30Hz）~~ | ⛔ **2026-10-22 已删除（主界面不再输出监控画面）**：~~`InitCameraPreview`（起 30Hz 表 + 订阅预览帧；`ImageBox` 由设计器声明）/ `OnMonitorPreviewFrame` / `CamPreviewTimer_Tick`~~ → 预览改由 [[modules/MonitorCam]] 承载 |
| 构造函数（新增调用） | 4 × `chk*.CheckedChanged += ChkSeries_CheckedChanged`（逐个订阅）；~~`InitCameraPreview()`（紧随 `InitDeviceSwitchButtons()`）~~（⛔ 2026-10-22 已删） |

### 2026-11-11 监控预览接回（经工作流 30Hz）

- 控件：`PanelDashborad` → `StatusGridPanel` → `gridTopBlock`（`Span = "60:fill;20:fill;80:fill;20:fill;fill"`）第 5 行、`divider3`（「监控画面」）之下 `imb_WeldViewer`（`Emgu.CV.UI.ImageBox`，`Dock=Fill`、`SizeMode=StretchImage`、`FunctionalMode=RightClickMenu`、`BackColor=Silver`，设计期 442×175）。
- **帧源改为工作流**（业主口径：主页面预览属焊接过程，与调试页「不是一个路数」）：本页订阅 `MonitorCameraWorkflow.Instance.WeldPreviewFrame`，**不碰 `MonitorCamManager.PreviewFrameEvent`**。开关（随焊接启停）与 30Hz 节流全在工作流，本页只上屏。
- 链路：`OnWeldPreviewFrame`（判空 + 销毁/句柄守卫 + `InvokeRequired → BeginInvoke`，封送失败即释放本帧）→ `ShowWeldPreviewFrame`（赋 `imb_WeldViewer.Image`，成功后**显式释放上一帧**；赋值异常则回滚并释放本帧）→ `DisposePreviewFrame`。
- 释放语义选**显式释放上一帧**（`_weldPreviewFrame` 持有当前帧）：帧是管理器逐订阅方 `Clone()` 的 `Mat`，显式释放确定，不依赖 `Emgu.CV.UI.ImageBox` 版本相关的隐式行为。
- `DisposeComponents()` 退订 `WeldPreviewFrame`，并先 `imb_WeldViewer.Image = null` 再释放末帧。
- 调试页 `MonitorCamPage` **未改动**，仍直连管理器事件逐帧直刷；两条通道互不影响。
- 边界见 [[standards/WorkflowResponsibilityBoundary]] §八；UI 只做上屏赋值（[[decisions/ADR-097-algorithm-layer-ownership-single-entry]] D2）。

## 关键方法

| 方法 | 说明 |
|------|------|
| `MainPage()` | 设计器初始化后字段实例化（4×ChartVar、`_contourSignalData` 1920 点）；内联原 `LoadComponent()`——订阅 `GlobalCommData.EventInfoHandler`；`HandleDestroyed` 挂 `MainPage_HandleDestroyed`（→`DisposeComponents`） |
| `AddContourLineChart()` | 初始化焊缝轮廓 ScottPlot（`AddSignalXY(_contourSignalXs, _contourSignalData)`，1920 点固定数组，目标 60Hz）；锁定轴缩放/平移；加特征点散点（红实心圆，初始 IsVisible=false）；初始 `_contourSignalPlot.IsVisible=false`（防全 0 假轮廓）；末调 `SubscribeContourCamera()`。⭐ **plot1 的唯一构建路径**：`Plot.Clear()` → 建两个系列 → 设标题/轴 → **建图例** → `SetAxisLimits`。图例只在此处创建（`Plot.Legend()` 是**方法**，每次调用新建一个 Legend renderable 并注册进 plot，别处再建会叠加成两份条目） |
| `AddNewDataLineChart()` | 初始绑定 4 条实时曲线（焊缝宽度/运动速度/送丝速度/激光功率）；2026-09-20 起与轮询刷新共用同一重绑路径 `RefreshParamCharts()`（ADR-035 合并，消除双份 BindChartVar 调用）。⭐ **2026-10-21：初始化期不再构图**——本方法**不调用** `RefreshParamCharts()`。原因：构造期算法输出缓存尚无点，此时 `Clear+AddSeries` 画的是一张**空图**，紧接着轮询线程首帧检测到版本变化又会 Clear 重建一次 ⇒ 同一张图初始化期被构建两遍，前一次纯浪费（Clear+AddSeries+Legend+Refresh 全套开销）。现改为：首帧构图由轮询线程**首次数据到达**触发（此时有数据、有图例，一次到位）。代价：算法首次执行（起焊/有机器人位置）前 plot2 只有坐标轴、无数据线与图例 |
| `ProfilePollLoop()` | **轮询主循环（UI 显示频率由主界面统一决定，33ms ≈ 30Hz）**：①轮廓——`LineLaserManager.Instance.Profile` 快照版本变化时 `ApplyProfileSnapshot`；②工艺曲线——`WeldParamManager.AdjustmentOutputVersion` 变化时 `AppendNewPoints` 增量拷入新原始点 ×4 曲线 + 合并派发一次 `RefreshParamChartsUi`（`_paramUiUpdatePending` 保证 BeginInvoke 队列最多 1 个待处理）。**取代 WeldProcessCompleted 事件逐次驱动 UI**（内部数据快、事件驱动易卡界面）；UI 只显示不加工（不改点值/点数/不平滑），保存与算法缓存的原始点数不受显示影响 |
| `AppendNewPoints(ChartVar, ChartVar, ref int)` | 把算法侧原始点缓存中自上次消费后的新点拷入显示序列（UI 只读消费算法缓存）；算法复位（`OutputVersion` 推进 + 缓存清空）时同步清空显示序列重新跟随；与生产者并发时个别点滞后一轮自愈 |
| `RefreshParamChartsUi()` / `RefreshParamCharts()` | UI 线程重绑**四合一图**并刷新：`Plot.Clear()` → **重设标题/轴标签** → 按勾选态逐系列 `AddSeries`（Ant Design 四色）→ `AxisAuto` + `Legend` + `Refresh`（ScottPlot 4.1 无逐系列 `Visible`，与 [[modules/UIDesign]] 同范式）；`finally` 复位 `_paramUiUpdatePending`；由轮询端新点到达**或复选框勾选变化**触发；按 `chk*.Checked` **直接引用**重建（同 `RebuildChartDatasets` 范式）；入口首行 `IsDisposed` 守卫（销毁后残留的排队回调直接返回）；「接头宽」分支内叠加 `AddSeamWidthLimitLines` **焊缝宽度上下限参考线**（**2026-10-21 起仅焊接开启后绘制**）。⭐ 本方法是 **plot2 图例的唯一来源**（`Plot.Clear()` 先清空上一轮全部 renderable，含图例）——其它路径不得再建图例，否则同一份条目被渲染两遍。⚠️ **`Plot.Clear()` 会连同标题/轴标签一起清掉**（运行期实测：Clear 前后渲染位图 8324→6256 字节；"有标题/无标题"两张图位图不同 ⇒ 标题确实参与渲染），故每次重建后**必须重设标题/轴**，否则首帧之后图表标题会消失 |
| `SubscribeContourCamera()` | 订阅 `CameraSelector.Active as IntelligentLaserCameraRun` 的 `ContourDataReady`；重连复位 `_contourAxisLocked=false` + 轮廓线 IsVisible=false；先退订旧相机防重复 |
| `IlCamera_ContourDataReady(object, ContourDataEventArgs)` | 英莱轮廓回调（**生产者线程预拷贝 + 合并派发**）：先判空；**立即**把 `points[i].Z`、`points[i].Y`（X 轴）、特征点、首帧校准判定拷入复用数组与快照字段（消除延迟读被回收缓冲）；用 `volatile _uiUpdatePending` 保证 BeginInvoke 队列最多 1 个待处理（根治内存↑/卡死）；`UpdateChartUI()` 在 UI 线程应用轴锁定（`_pendingAxisLock`，**横轴 X(=数据Y)与纵轴 Y(=数据Z)均用校准框四角点 min/max（含负值）+5% 边距，连接时锁定一次**，详见 §5.11）+ `MinRenderIndex`(固定0)/`MaxRenderIndex`(=本帧有效点数 `_snapPointCount-1`，替代清除多余点) + 特征点显隐 + `Refresh()`，`finally` 复位标志 |
| ~~`BindChartVar(ScottPlot.FormsPlot, string, ChartVar)`~~ | ⛔ 2026-09-29 已删除（多图专用，逐图 `AxisAuto`+`Refresh` 开销重复）；由下方 `AddSeries` 接管 |
| `AddSeries(ScottPlot.FormsPlot, string, ChartVar, Color)` | **2026-09-29 新增**：把 `ChartVar` 坐标序列以折线加入图表（`TrySnapshot` 配对取 X/Y + `AddScatter` 指定线色与图例名）；**不含 `Refresh`**，由 `RefreshParamCharts` 统一刷新一次 |
| `AddSeamWidthLimitLines(ScottPlot.FormsPlot)` | 把自适应参数的焊缝宽度上下限画成**水平参考线**（`Plot.AddHorizontalLine`，**红色**虚线 `ColorSeamWidthLimit(255,77,79)`，图例「焊缝宽度上限/下限」，与 [[api/ProcessControlPage]] 自适应参数区 UI 标签同词）；限值取 `WeldParamManager.Instance.CurrentAutoParam.SeamWidthMax/SeamWidthMin`（真实配置非假数据，符合 ADR-054 禁假曲线）；**门禁**：`CurrentAutoParam` 判空 + `SeamWidthMax <= SeamWidthMin`（含默认 0/0 未配置**与上下限填写颠倒**）不画，判据与 `WeldParamLookupAlgorithm` 有效性一致，防未配置/错配限值线拉低纵轴；仅「接头宽」勾选分支调用，随勾选切换自动显隐。**变更留痕**：绘制/跳过状态变化时记一条 `ShowLog`（已画=打限值 / 未画=打原因与实际值），状态不变不刷屏——现场「不画线」可直接从日志区分填写错误与未配置；⚠️ 限值修改后图随下一次 `RefreshParamCharts`（新点到达或勾选变化）生效，无独立刷新触发<br>**2026-10-21 增「焊接开启」门控**：入口先判 `IsWeldModeActive`（整机 `Running`＝真焊+模拟，与相机预览门控同源）——**未起焊不画参考线**（上下限依配置设定、起焊前可能仍在调整，且初始化期画出会叠加图例条目）；起焊后随每轮 `RefreshParamCharts` 按当前配置**重画**（`Plot.Clear()` 已清理前一批 renderable）；新增日志状态 `skip-not-welding`（Info 级，非异常）区分「未起焊」与「未配置/填空」 |
| `SetupMergedChart(ScottPlot.FormsPlot)` | **2026-09-29 新增**：初始化四合一工艺参数图（`DpiStretch=false` 高 DPI 修复 + 标题「工艺参数实时曲线」+ X=机器人 X 轴 / Y=参数值）；**2026-10-21 起不再建 `Legend`**——图例统一由 `RefreshParamCharts` 路径创建（该路径先 `Plot.Clear()` 再重建，每轮刷新只留一个图例）。⛔ 此前本路径**不 Clear 又建一次图例**，与刷新路径的图例叠加成两个 Legend 实例，同一份系列/参考线条目被渲染两遍（右下角出现重复 txt 记录）。⭐ **2026-10-21 再降级为纯兜底**：本路径现**只设一次标题/轴**（首帧数据到达前的空白期显示用），不建图例；后续每次重建由 `RefreshParamCharts` 接管（含重设标题/轴 + 建图例） |
| `ChkSeries_CheckedChanged(object, AntdUI.BoolEventArgs)` | **2026-09-29 新增（同日三次修订对齐 [[modules/UIDesign]] 范式）**：勾选变化即 `RefreshParamCharts()` 重建；勾选态由复选框自身维护，本页不缓存；构造函数逐个订阅（每个复选框订阅点唯一：`MainPage.cs` ×1 / Designer ×0）；~~`InitSeriesToggles` 平行数组装配法~~已删 |
| ~~`SetupChart(ScottPlot.FormsPlot, string, string)`~~ | ⛔ **2026-10-21 已删除**（0 调用者）。原职责「初始化单图表标题/X/Y 标签/图例」与各图的**唯一构建路径**重复：plot1 已在 `AddContourLineChart` 内设过标题/轴，plot2 在 `RefreshParamCharts` 内设过；其 `Plot.Legend()` 还会在不 Clear 的路径上叠出第二个图例实例 |
| `AfterInitializeUI()` | `MainPage_Shown` 后**只做 plot2 的标题/轴兜底设置**（`SetupMergedChart(formsPlot2)`）。⭐ **2026-10-21**：①移除 `SetupChart(formsPlot1,…)`（plot1 已在 `AddContourLineChart` 完成 Clear+建系列+设轴+建图例，此处重复设置属初始化期重复显示）；②`SetupMergedChart` 降为**纯兜底**（不建图例）——plot2 的图例唯一来源为 `RefreshParamCharts`。2026-09-29 前为 5 图 |
| ~~`InitCameraPreview()`~~ | ⛔ **2026-10-22 已删除（主界面预览移除）**。原职责（2026-09-29）：起 `_camPreviewTimer`（33ms ≈ 30Hz）+ 订阅 `MonitorCamManager.Instance.PreviewFrameEvent`；预览控件 `imageBoxCam` 由设计器声明 |
| ~~`OnMonitorPreviewFrame(Mat)`~~ | ⛔ **2026-10-22 已删除（主界面预览移除）**。原职责（2026-09-29 / 2026-10-10）：相机取流线程回调，`IsWeldModeActive` 门控后把帧放入待显示槽 |
| ~~`CamPreviewTimer_Tick(object, EventArgs)`~~ | ⛔ **2026-10-22 已删除（主界面预览移除）**。原职责（2026-09-29 / 2026-10-10）：30Hz 上屏节拍 + `CurrentMat` 回退 + `imageBoxCam.Image` 赋值与上一帧释放 |
| `IsWeldModeActive`（属性） | **2026-10-10 新增；2026-10-22 保留并移出预览 region**：`_currentStatus == MainDeviceStatus.Running` —— 真实焊接与模拟测试同走 Running 运行态，故该判据即「测试环境生效」；`_currentStatus` 由 `ApplyDeviceStatus` 经 `StatusChanged` 维护。现唯一消费方为 `AddSeamWidthLimitLines`（焊缝宽度上下限参考线门控），属性已归入「私有函数」region |
| `InitWeldFlowSteps()` / `SetWeldFlowStep(step, state, allowBack)` | **2026-10-22 新增；2026-11-10 设计器删除后按业主指示补回、同日改横排方案 B**：5 步文案来自 `WeldParamData.WeldFlowSteps`（安全位 / 焊前检查 / 起焊 / 焊接 / 结束），`InitWeldFlowSteps` 装配 `steps1.Items`（**只写 Title**，副标题/描述按 Items 同序存入 `_weldFlowStepTips`）并停在安全位；`SetWeldFlowStep` 默认**只前进**（`next < current` 直接返回，防迟到事件拉回），步骤或状态变化写一条 `Log` 并同步 `steps1.Current/Status` |
| `OnWeldFlowStepsMouseMove` / `OnWeldFlowStepsMouseLeave` | **2026-11-10 新增（方案 B 悬停提示）**：AntdUI 2.4.3 的 `Steps` 无逐项 Tooltip 承载位、`TooltipComponent` 只能按控件绑定，故用原生 `ToolTip`，在 `MouseMove` 中读取 `StepsItem.rect`（AntdUI 内部布局结果，反射读取，不自算坐标）命中步骤，按索引显示 `_weldFlowStepTips[i]`（`SubTitle + "\n" + Description` 原文）；提示与 `Current` 无关，逐项各持文本，故不会错位；索引未变化不重弹，移出控件隐藏 |
| `ApplyWeldFlowDeviceStatus(previous, state)` / `OnWeldParamWeldStatusChanged` / `ApplyWeldFlowWeldStatus` / `AdvanceWeldFlowByCommand(message)` | **2026-10-22 新增，三源联动**：①整机态——`Running`→焊前检查、`Stop`（自 Running）→结束 `Finish`、`Reseting/NoReset`→复位安全位、`Alarm/EStop`→当前步标 `Error`；②`WeldParamControlWorkflow.WeldStatusChanged` 兜底——`PreWork`→焊前检查、`Working`→焊接、`Stopping/ManualStopped`→结束、`ErrorAborted`→结束 `Error`（后台线程经 `BeginInvoke` 封送）；③机器人指令——`RxStartSafePose/RxHomePose`→安全位（允许回退）、`RxPreWeldRequest/RxPreWeldPose`→焊前检查、`RxWeldStartPose`→起焊、`RxPreStopPose/RxWeldStopPose`→结束、`RxStopSafePose`→结束 `Finish` |
| `LogAppend(Color, string)` | 追加日志文本（AntdUI.Input 不支持彩色，仅文本）；`CommenData_EventInfoHandler` 经 `BeginInvoke` 异步封送调用 |
| `OnWeldPreviewFrame(Mat)` | **2026-11-11 新增**：工作流 `WeldPreviewFrame` 回调（已 30Hz 节流）。判空 → `IsDisposed/Disposing/!IsHandleCreated` 守卫（丢弃即释放本帧）→ `InvokeRequired` 则 `BeginInvoke`（封送异常即释放本帧）→ UI 线程调 `ShowWeldPreviewFrame`。**本方法不做任何帧转换/像素运算** |
| `ShowWeldPreviewFrame(Mat)` | **2026-11-11 新增**：赋 `imb_WeldViewer.Image`；成功后**显式释放上一帧**（`_weldPreviewFrame` 换手）；赋值异常回滚字段并释放本帧 |
| `DisposePreviewFrame(Mat)` | **2026-11-11 新增**：`try { frame.Dispose(); } catch { }` ——释放路径失败不影响上屏 |
| `DisposeComponents()` | **释放资源**（← `HandleDestroyed`）：退订 `GlobalCommData.EventInfoHandler` + 退订 `DeviceControlWork.StatusChanged` + 退订 `WeldParamControlWorkflow.WeldStatusChanged`（步骤条联动源，2026-10-22）+ 停/释放 `_statusBlinkTimer` + `StopProfilePolling()` + 释放 `_tooltip` + 释放 `_weldFlowToolTip`（步骤悬停提示）+ **2026-09-29 新增**：逐个退订 4 个复选框 `CheckedChanged`（防残留排队回调）；~~退订 `MonitorCamManager.PreviewFrameEvent` → 停/释放 `_camPreviewTimer` → 释放待显示帧与已上屏帧 → `imageBoxCam.Image = null`~~（⛔ 2026-10-22 已随预览移除）；**2026-11-11 新增**：退订 `MonitorCameraWorkflow.WeldPreviewFrame` → `imb_WeldViewer.Image = null`（先解引用）→ 释放 `_weldPreviewFrame` 并置空；UI 类按需释放（ADR-001，不在 `.cs` 重写 `Dispose(bool)`） |
| `InitDeviceSwitchButtons()` | **2026-10-22 起 2×2 区域布局**：构造函数创建 `TooltipComponent`（微软雅黑 10F，`ArrowAlign=TAlign.Top`）+ **4 组「`AntdUI.ButtonShadow` + 等高 `AntdUI.Alert`」**：Alert `Text`=设备名、`TextAlign=MiddleCenter`、`Icon=TType.Error`（初始未连接）、`TextColor` 红(192,0,0)；按钮保持 buttonShadow1 形态（`BorderWidth=1F`/`IconRatio=1.2F`/`ShadowColor=黑`/`IconSvg=_deviceIconSvgs[i]`/`DefaultBack=DeviceBackDisconnected`/`BadgeSvg=CloseCircleFilled`/`BadgeAlign=TR`/`BadgeBack=红`/`BadgeSize=1.0F`）；逐按钮 `_tooltip.SetTip(btn, BuildDeviceTooltipText(i,false))`（初始未连接，随后由 `RefreshDeviceSwitchUi` 随态刷新），闭包拷贝索引挂 `Click`→`OnDeviceSwitchClick(idx)`；尺寸/位置**不写死**，末尾订阅 `panelfloatbutton.SizeChanged` 并调用 `LayoutDeviceSwitchAreas()` 按面板实际 ClientSize 核算（`Controls.Add` 常驻面板，随页面显隐自动生效） |
| `LayoutDeviceSwitchAreas()` / `OnPanelFloatButtonSizeChanged` | **2026-10-22 新增**：按 `panelfloatbutton.ClientSize` 核算 2×2——外边距 4、区域间隔 8、区内间隔 1；`cellWidth=(W-2*4-8)/2`、`cellHeight=(H-2*4-8)/2`，**按钮边长=Alert 高度=cellHeight**，Alert 宽=`cellWidth-btnSide-1`；第 i 区 `col=i%2 / row=i/2`。442×81 设计尺寸下实测核算：cell=213×32、按钮 32×32、Alert 180×32。面板过小（btnSide<16 或 Alert 宽<10）跳过，等下次 SizeChanged；`AfterInitializeUI`（页面显示后）再补排一次 |
| `BuildDeviceTooltipText(int idx, bool connected)` | 构建设备按钮 Tooltip 文本：`设备名 + 「：已连接/：未连接」`；初始化与状态刷新共用，保证格式一致 |
| `OnDeviceSwitchClick(int idx)` | 线激光（`LineLaserSwitchIndex`）→`ToggleLineLaserConnection()`；其余→`Message.info` 提示「暂未接入，无法操作」；徽标/背景刷新由定时器驱动，点击后不立即变色 |
| `RefreshDeviceSwitchUi()` | **public 单一刷新入口；2026-10-10 改 4 设备各自快照**：`HandleCreated/控件空` 守卫后按索引读实际状态——`[0]` 线激光 `IsLineLaserRunning()`（`LineLaserWorkflow.State == Connected`）、`[1]` 监控相机 `MonitorCameraWorkflow.Instance.State == Connected`、`[2]` 控制器 `MotionControlWorkflow.Instance.State == Connected`、`[3]` 机器人 `DeviceControlWork.Instance.IsRobotOnline`；与 `_lastDeviceConnected[i]` 相同则跳过该按钮，变化才改 `BadgeSvg`（对勾/叉号）+ `BadgeBack`（绿(82,196,26)/红(255,77,79)）+ `DefaultBack`（连接=null 主题默认白 / 断开=灰(200,200,200)）+ Tooltip（`SetTip` 原地更新）+ **每区 Alert（2026-10-22 新增）**：`Icon`=`TType.Success/Error`、`TextColor` 绿(0,128,0)/红(192,0,0) 随该设备连接态；原全局通讯 Alert `_alertConnStatus` 与 `_lastAlertConnected` 已删除（通讯状态由 4 个设备 Alert 各自表达）；免重建免闪烁；由 `FormMain.uiMillisecondTimer1_Tick` 每周期调用。⚠️ 修复前仅刷线激光且以单值 `_lastLlConnected` 提前 return，**监控相机/控制器按钮永远停在初始红叉**（本次上机实测报障） |
| `SetDeviceIconSvg(int idx, string iconSvg)` | **public 预留接口**：替换指定设备按钮的 `IconSvg` 并同步 `_deviceIconSvgs[idx]` 缓存（各按钮设备指向不同，逐个设置；越界/未初始化静默忽略） |
| `SetDeviceBadgeSvg(int idx, string badgeSvg)` | **public 预留接口**：设置指定设备按钮的 `BadgeSvg`（AntdUI 原生徽标 SVG 属性，设置后徽标以 SVG 呈现、颜色仍随 BadgeBack 红/绿） |
| `ToggleLineLaserConnection()` | 线激光连接切换（`SubDeviceState` 连接/断开语义，**非焊接流程启停**）：报警态提示先复位；`State==Connected` → `ConnectOff()`（后台线程回 Standby→Disconnected），否则 → `ConnectOn()`（后台线程置 Standby→Connected）；不直驱子类 Start/Stop/Reset |

> 事件绑定在设计器生成代码内：`uiMillisecondTimer1.Tick`/`buttonSZ.Click`/`inputLog.TextChanged`/`MainPage.Shown`/`FormMain.FormClosed` 等（脚本标记的"疑似死函数"为误报，Grep 确认非零引用）。

## 设计约束

- **2026-09-29 主界面双图化**（[[decisions/ADR-049-MainPageDualChartAndCamPreview]]）：①图表只允许 **2 张**——轮廓图（`formsPlot1`）+ 四合一工艺参数图（`formsPlot2`）；四路参数曲线共用单套坐标轴，逐系列显隐由 `chkSeamWidth/chkRobotSpeed/chkFeedSpeed/chkLaserPower` 控制（**ScottPlot 4.1 无逐系列 `Visible`，一律「清空重建 plottable」**，与 [[modules/UIDesign]] 同范式）；②~~预览控件 `imageBoxCam`（`Emgu.CV.UI.ImageBox`）与~~ 4 个复选框的文本/默认勾选态**由 `MainPage.Designer.cs` 声明**（业主口径：控件须在设计器可见，不接受全部动态加载；设计器改动走字节安全流程，见 [[guides/WinForms-Designer]]）；③~~预览**显示刷新固定 30Hz**（`CamPreviewIntervalMs=33`），与相机帧率、与 `FrameCompletedEvent` 分析链路均解耦~~；④~~预览帧所有权：`PreviewFrameEvent` 副本归本页（须释放）、`CurrentMat` 归相机管理器（只读不释放）~~。**⛔ 2026-10-22：②中的预览控件③④ 预览条款已随主界面预览移除一并废止（①② 的四合一图/设计器声明仍有效）**。
- ~~**2026-10-10 预览焊接模式门控（上机实测报障修复）**~~：⛔ **2026-10-22 废止（主界面预览已移除；`IsWeldModeActive` 保留供焊缝宽度参考线门控）**。原条款：主页面板相机预览**仅焊接模式生效**——`IsWeldModeActive`（整机 `Running`，真实焊接与模拟测试同走）门控帧回调（非焊接模式丢弃并释放副本）与 30Hz 节拍（非焊接模式丢帧返回、**保留最后一次焊接末帧**）。根因：手动调试页 `StartCapture`/单帧采集的帧与 `CurrentMat` 回退**无门控**，切回主页面即串页上屏。
- **2026-11-11 焊接预览边界**（[[standards/WorkflowResponsibilityBoundary]] §八）：帧只从 `MonitorCameraWorkflow.WeldPreviewFrame` 来；本页**不判断「该不该显示」、不定时、不限速、不直连 `MonitorCamManager`**。UI 线程只做 `BeginInvoke` + `imb_WeldViewer.Image` 赋值 + 换手释放，不做转换、像素运算、`new Mat`；`DisposeComponents()` 必须退订并释放末帧。
- **UI 布局改版必须做「控件引用对账」**：设计器删控件后代码后置的残留引用是编译阻断（CS0103），见 [[lessons/UiLayoutChangeSyncPitfalls]] 坑一。同页坑二（控件落地位置：设计器可见优先）、坑三（回填 `Checked` 触发事件 / 事件订阅不得双写）与坑四（跨线程帧所有权）亦为同类任务门禁。
- ADR-002（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） / [[decisions/ADR-002-DisposePatternFullCoverage]]：UI 类按需 `DisposeComponents()`，未重写 `Dispose(bool)`；`HandleDestroyed` 触发。
- [[decisions/ADR-001-CS73-Constraint]]：字段声明处不初始化（统一 ctor 内），无 switch 表达式等。
- ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）：英莱数据流（CamRun 分发 + Signal 高性能显示）+ imageBox/ScottPlot 坐标系区分（两者仅朝向一致，ScottPlot 直绘原始坐标不平移）。
- 2026-08-27 代码精简：删 4 未用字段（robotDataRefresh/laserDataRefresh/ClinkTimes/StartTest）+ 死函数 `ResetChartLineData()` + 内联 `LoadComponent()`；补 5 `#region`；public 方法归集；XML 注释补全。`csharp_review.py` 扫描 23→2 项（0 error/0 warn/2 info）。
- 2026-08-31 硬件快捷开关由 FloatButton 覆盖层改为 **AntdUI `ButtonShadow` 常驻按钮**（[[decisions/ADR-011-ButtonShadowDeviceSwitch]]）：构造函数代码后置创建 6 个按钮直接放入 `panelfloatbutton` 面板，随页面显隐自动生效；线激光连接态真相源统一走 `LineLaserWorkflow.Instance.Step`（经 `IsLineLaserRunning()` 判定 Starting/Working，不读 `CameraSelector.ConnectionState`——初始化已连 socket 但激光关闭，避免误判，ADR-008 精神），线激光手动 Start/Stop/Reset 同步驱动 `LineLaserWorkflow` 状态机，不本地缓存连接布尔。**同日风格迭代（buttonShadow1 形态）**：删按钮 Text 改 50×50 仅 SVG 图标（默认 poweroff 电源 SVG），设备名经 `TooltipComponent`（`ArrowAlign=TAlign.Top`）顶部提示，连接态配色由 `Type`（TTypeMini）改为**原生徽标** `Badge=""`+`BadgeMode=true`+`BadgeBack` 红/绿（按钮保持中性态）；新增预留接口 `SetDeviceIconSvg`/`SetDeviceBadgeSvg`；`DisposeComponents()` 增加 `_tooltip` 释放。
- **2026-10-22 panelfloatbutton 2×2 区域布局**（[[decisions/ADR-011-ButtonShadowDeviceSwitch]]）：4 组「`ButtonShadow` + 等高 `AntdUI.Alert`」由 `LayoutDeviceSwitchAreas()` 按面板 `ClientSize` 运行时核算（外边距 4 / 区域间隔 8 / 区内间隔 1），按钮边长 = Alert 高度 = `cellHeight`；`panelfloatbutton.SizeChanged` 与 `AfterInitializeUI`（页面显示后）各重排一次；原全局通讯 Alert `_alertConnStatus` / `_lastAlertConnected` 删除，连接态改由每区 Alert 表达。~~50×50 横排 + 右侧 Alert~~ / ~~52×52 纵向堆叠 + 顶部标题「模组状态」~~ 均已废止。
- **2026-10-22 焊接流程步骤条（steps1；2026-11-10 删除后补回）**：五步文案与顺序的**唯一来源** = `WeldParamControl/WeldParamData.cs` 的 `WeldFlowSteps`（安全位→焊前检查→起焊→焊接→结束）；联动三源 = 机器人指令（主）+ 整机 `MainDeviceStatus` + `WeldParamControlWorkflow.WeldStatusChanged`（兜底）；进度默认只前进，仅 `Reseting/NoReset` 回退；后台事件经 `BeginInvoke` 封送；不新增计时器。

## 协作

- 上游：`CameraSelector.Active`（英莱 `IntelligentLaserCameraRun`，[[api/IntelligentLaserCam]]）、`GlobalCommData`（日志事件）、`ChartVar`（实时数据，WeldParamControl）。
- **预览上游（2026-11-11 改为经工作流）**：`MonitorCameraWorkflow.Instance.WeldPreviewFrame`（[[api/MonitorCameraWorkflow]]）——工作流订阅 `MonitorCamManager.PreviewFrameEvent` 后按 30Hz 节流再交付，开关随焊接启停。⛔ 本页**不订阅** `MonitorCamManager.PreviewFrameEvent`、不读 `CurrentMat`（2026-10-22 删除后于 2026-11-11 以新通道接回，旧直连路径不复原）；预览**不参与**分析链路（分析走 `FrameCompletedEvent`）。
- 承载：由 `FormMain.LoadNavAndPages()` 实例化并 `AddTabSelect` 到 Tab0。
- 状态联动：硬件开关 UI 由 `FormMain.uiMillisecondTimer1_Tick` 每周期调 `RefreshDeviceSwitchUi()` 刷新；流程状态/系统时间由 `FormMain` 状态栏承载；**整机状态由本页 `LabelStatus` 承载**（2026-09-08 自 FormMain 左下角迁移，原 `lbl_SystemStatus` 删除）。

## 整机状态标签（LabelStatus，2026-09-08 迁移）

订阅 `DeviceControlWork.Instance.StatusChanged`（ADR-034 三态模型整机状态）+ 构造时初渲染 `ApplyDeviceStatus(Instance.Status)`。文本固定为 **「设备状态：{状态值}」**，背景色按设备颜色映射（2026-09-08 用户二次定义）：

| MainDeviceStatus | 文本 | 背景色 | 前景色 |
|---|---|---|---|
| `Running` | 设备状态：运行中 | 绿 `Green` | 白 |
| `Reseting` | 设备状态：复位中 | 黄 `Yellow` | 黑 |
| `Alarm` | 设备状态：报警 | 橙 `Orange` | 黑 |
| `EStop`（急停） | 设备状态：急停 | **红闪**（0.5s 红↔白翻转，`_uiTimer` WinForms Timer 内判断） | 白 |
| `Stop` | 设备状态：已停止 | 蓝 `Blue`（不闪） | 白 |
| `NoReset` | 设备状态：未复位 | 灰 `Gray` | 白 |

- 成员：`OnMainDeviceStatusChanged`（回调，`LabelStatus.InvokeRequired` → `BeginInvoke` 封送，UI 线程安全项目惯例）→ `ApplyDeviceStatus(state)`（查表映射 + EStop 相位复位）→ `UiTimer_Tick`（EStop 态翻转 `_blinkOn` 相位）。
- 私有字段：`_uiTimer`/`_blinkOn`/`_currentStatus`（ADR-001：统一构造函数初始化）。
- `DisposeComponents()`：退订 `StatusChanged` + 停表并 `Dispose()` `_uiTimer`（原 FormMain 侧退订随迁移移入）。

## UI 统一定时器（_uiTimer，2026-10-19 两表合一）

管理 UI 定时器收敛（业主要求「不希望有太多计时器在管理 UI」）：原 `_statusBlinkTimer`（500ms 闪烁）与 `_dashTimer`（1000ms Dash 刷新）**合并为单表 `_uiTimer`**（500ms 常驻，构造启动、不随状态启停）：

- **EStop 红闪**：`UiTimer_Tick` 内判 `_currentStatus == EStop` 才翻相位；非 EStop 态不动色（`ApplyDeviceStatus` 已设固定底色）。
- **⛔ 2026-11-10 起定时器只做 EStop 红闪**：业主删除「运行时长 / 焊接数量 / 完成数量」三个统计 label 后，Dash 分频刷新（`_dashTickCounter` + `RefreshDashboard`）已整段移除，`_uiTimer` 不再承担任何数据刷新。
- **统计数据现状**：`GlobalCommData.SoftwareStartTime` 保留（运行时长计算仍在、主界面无显示出口，业主未提）；`WeldCount` / `CompleteCount` 已于 **2026-11-10 按业主裁定从代码中整体删除**（属性声明 + 静态构造复位 + `RxWeldStartPose` 自增 + `CheckWeldProgress` 自增），查证无记录文件/追溯页/PLC/Modbus/RSI/Config 消费；⛔ 不得自行补回控件或计数。
- **机器人指令行**：`lblRobotCommand` 已随改版删除，`OnRobotCommandReceived` 只保留「封送 → `AdvanceWeldFlowByCommand(message)`」；`CommandCore.TranslateCommand` 不再参与主界面显示。
- ~~**保留独立表**：`_camPreviewTimer`（33ms/30Hz 监控相机取帧数据泵）职责与频率不同，不并入~~：⛔ 2026-10-22 已随主界面预览删除；2026-11-11 接回时**不再建表**——节流已在 `MonitorCameraWorkflow` 内做，本页零定时器。
- `DisposeComponents()` 统一释放 `_uiTimer`（Stop → Tick 退订 → Dispose → null）。

---

*来源：AdaWeldSystem/UIDesign/ControlPage/MainPage.cs + .Designer.cs*
