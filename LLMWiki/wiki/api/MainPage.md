---
title: MainPage 主页面
date: 2026-08-27
tags: [API, UI, 主页面, ScottPlot, 英莱, 轮廓, 实时曲线]
source: AdaWeldSystem/UIDesign/ControlPage/MainPage.cs + .Designer.cs
---

# MainPage — 主页面

> 主显示页面（Sub1UI `UserControl`），承载英莱线激光轮廓 ScottPlot Signal 图 + 4 条实时数据曲线（焊缝宽度/机器人运动速度/送丝速度/激光功率）+ 全局日志框。2026-08-27 经五维度代码精简（删未用字段/死函数、内联 LoadComponent、补 5 #region、public 方法归集、XML 注释补全）。2026-08-31 改用 **AntdUI `ButtonShadow` 常驻按钮**（[[decisions/ADR-045-ButtonShadowDeviceSwitch]]，替代已废弃的 FloatButton 覆盖层方案）：6 个硬件快捷开关（焊接头/线激光/监控相机/运动控制器/机器人通讯/PLC通讯；徽标红=断开 绿=连接；仅线激光实现真实连接/断开切换，其余硬件暂未接入，点击提示「暂未接入」），构造函数中代码后置创建并直接放入 **`panelfloatbutton` 面板**（MainPage 底部 54px 全宽条，tableLayoutPanel2 第 3 行），随页面显隐自动生效。**同日风格迭代（形态对齐 AntdUI Demo `buttonShadow1`）**：50×50 阴影按钮**仅显示 SVG 图标**（默认 poweroff 电源 SVG）、设备名经 **`TooltipComponent` 顶部提示**（`ArrowAlign=TAlign.Top`）、连接态由**原生徽标属性** `Badge=""`+`BadgeMode=true`+`BadgeBack` 红/绿承载；预留接口 `SetDeviceIconSvg`/`SetDeviceBadgeSvg`。

## 基本信息

| 项 | 值 |
|----|----|
| 类 | `AdaWeldSystem.Sub1UI.MainPage` |
| 基类 | `System.Windows.Forms.UserControl` |
| 文件 | `UIDesign/ControlPage/MainPage.cs` + `.Designer.cs` |
| 命名空间 | `AdaWeldSystem.Sub1UI` |
| 依赖 | `AdaWeldSystem.Comm`、`WeldParamControl`、`LineLaserCamApi`、`LineLaserCam.IntelligentLaserCam`、`PCLOperate.Models`、`Workflow`(LineLaserWorkflow)、`DeviceStateMachine.API`(DeviceState)、`ScottPlot` |

## #region 结构（2026-08-27 精简后）

| Region | 成员 |
|--------|------|
| 公共变量 | `LogAppendDelegate(Color, string)`（委托类型） |
| 私有变量 | `SeamWidth`/`robotSpeed`/`LaserPower`/`FeedSpeed`（ChartVar）、`_contourSignalData`/`_contourSignalXs`/`_contourSignalPlot`(SignalPlotXY)/`_featurePointPlot`/`_featureXs`/`_featureYs`/`_contourCamera`（轮廓图）、`_contourYMin/Max`/`_contourZMin/Max`/`_contourAxisLocked`（轴范围默认回退，含负值）、`_uiUpdatePending`/`_snapPointCount`/`_snapHasResult`/`_snapFeatureY`/`_snapFeatureZ`/`_pendingAxisLock`（合并派发+快照）；**硬件开关**：`_deviceButtons`(AntdUI.ButtonShadow[] 6 常驻按钮)/`_tooltip`(TooltipComponent 顶部提示)/`_deviceIconSvgs`(各设备图标 SVG 缓存，设备指向不同)/`_lastLlConnected`(缓存线激光连接态)/`_deviceSwitchNames`(6 设备名，作 Tooltip 文本)/`LineLaserSwitchIndex=1`/`DeviceBadgeRed`+`DeviceBadgeGreen`+`DeviceBackDisconnected`(static readonly 徽标与底色配色)/`ConnectedBadgeSvg`="CheckCircleFilled"+`DisconnectedBadgeSvg`="CloseCircleFilled"(const 徽标图标)/`DefaultDeviceIconSvg`(const poweroff SVG 默认图标) |
| 构造函数 | `MainPage()` |
| 私有函数 | `MainPage_HandleDestroyed`/`SubscribeContourCamera`/`IlCamera_ContourDataReady`/`UpdateChartUI`/`BindChartVar`/`AfterInitializeUI`/`SetupChart`/`CommenData_EventInfoHandler`/`inputLog_TextChanged`/`MainPage_Shown` |
| 公共函数 | `DisposeComponents`/`AddContourLineChart`/`AddNewDataLineChart`/`LogAppend` |
| 硬件快捷开关（AntdUI ButtonShadow，ADR-045） | `InitDeviceSwitchButtons`(构造函数创建 6 个 ButtonShadow 常驻 `panelfloatbutton` 面板，50×50 仅 SVG 图标 + Tooltip + 原生徽标)/`OnDeviceSwitchClick`(点击分发)/`IsLineLaserRunning`(依 `LineLaserWorkflow.Instance.Step` 判定 Starting/Working 运行中)/`ToggleLineLaserConnection`(线激光 Start/Stop/Reset，驱动 LineLaserWorkflow 状态机)/`RefreshDeviceSwitchUi`(public 单一刷新入口，仅改线激光按钮 BadgeBack 属性)/`SetDeviceIconSvg`(public 预留接口：替换按钮图标 SVG)/`SetDeviceBadgeSvg`(public 预留接口：设置徽标 SVG) |

> 2026-08-27 将 4 个 public 方法由散落位置归集到末尾 `公共函数` region，强制成员顺序：私有变量→公共变量→构造函数→私有函数→公共函数。

## 关键方法

| 方法 | 说明 |
|------|------|
| `MainPage()` | 设计器初始化后字段实例化（4×ChartVar、`_contourSignalData` 1920 点）；内联原 `LoadComponent()`——订阅 `GlobalCommData.EventInfoHandler`；`HandleDestroyed` 挂 `MainPage_HandleDestroyed`（→`DisposeComponents`） |
| `AddContourLineChart()` | 初始化焊缝轮廓 ScottPlot（`AddSignalXY(_contourSignalXs, _contourSignalData)`，1920 点固定数组，目标 60Hz）；锁定轴缩放/平移；加特征点散点（红实心圆，初始 IsVisible=false）；初始 `_contourSignalPlot.IsVisible=false`（防全 0 假轮廓）；末调 `SubscribeContourCamera()` |
| `AddNewDataLineChart()` | 以 `ChartVar` 全量重建并绑定 4 条实时曲线（焊缝宽度/运动速度/送丝速度/激光功率） |
| `SubscribeContourCamera()` | 订阅 `CameraSelector.Active as IntelligentLaserCameraRun` 的 `ContourDataReady`；重连复位 `_contourAxisLocked=false` + 轮廓线 IsVisible=false；先退订旧相机防重复 |
| `IlCamera_ContourDataReady(object, ContourDataEventArgs)` | 英莱轮廓回调（**生产者线程预拷贝 + 合并派发**）：先判空；**立即**把 `points[i].Z`、`points[i].Y`（X 轴）、特征点、首帧校准判定拷入复用数组与快照字段（消除延迟读被回收缓冲）；用 `volatile _uiUpdatePending` 保证 BeginInvoke 队列最多 1 个待处理（根治内存↑/卡死）；`UpdateChartUI()` 在 UI 线程应用轴锁定（`_pendingAxisLock`，**横轴 X(=数据Y)与纵轴 Y(=数据Z)均用校准框四角点 min/max（含负值）+5% 边距，连接时锁定一次**，详见 §5.11）+ `MinRenderIndex`(固定0)/`MaxRenderIndex`(=本帧有效点数 `_snapPointCount-1`，替代清除多余点) + 特征点显隐 + `Refresh()`，`finally` 复位标志 |
| `BindChartVar(ScottPlot.FormsPlot, string, ChartVar)` | 清空并 `AddScatter` 绑定单条曲线 + `AxisAuto` + `Refresh` |
| `SetupChart(ScottPlot.FormsPlot, string, string)` | 初始化单图表标题/X/Y 标签/图例，`DpiStretch=false` 修复高 DPI 锯齿 |
| `AfterInitializeUI()` | `MainPage_Shown` 后初始化 5 个图表（轮廓+4 曲线） |
| `LogAppend(Color, string)` | 追加日志文本（AntdUI.Input 不支持彩色，仅文本）；`CommenData_EventInfoHandler` 经 `BeginInvoke` 异步封送调用 |
| `DisposeComponents()` | **释放资源**：退订 `GlobalCommData.EventInfoHandler` + 取消英莱相机轮廓事件订阅（防内存泄漏）+ 释放 `_tooltip`（TooltipComponent）；UI 类按需释放（ADR-001，不在 .cs 重写 `Dispose(bool)`） |
| `InitDeviceSwitchButtons()` | 构造函数调用：创建 `TooltipComponent`（微软雅黑 10F，`ArrowAlign=TAlign.Top`，Tooltip 文本=设备名+连接状态）+ 面板顶部标题 `AntdUI.Label`「子设备状态」（AutoSizeMode=Width、高 24）+ 6 个 `AntdUI.ButtonShadow`（52×52，面板竖直摆放**纵向堆叠**：X=2 左对齐、Y=`btnTop(=top+24+gap)+i*(52+15)` 让位标题自上而下，总高 428px；`BorderWidth=1F`、`IconRatio=1.2F`、`ShadowColor=黑`、`IconSvg=_deviceIconSvgs[i]`（默认 poweroff 电源 SVG，各设备可不同）、`DefaultBack=灰(158,158,158)` 断开底色、`BadgeSvg=CloseCircleFilled` 断开叉号 + `BadgeAlign=TR` + `BadgeBack=红` + `BadgeSize=1.0F`，形态对齐 AntdUI Demo buttonShadow1），逐按钮 `_tooltip.SetTip(btn, BuildDeviceTooltipText(i,false))`（初始未连接），闭包拷贝索引挂 `Click`→`OnDeviceSwitchClick(idx)`，`panelfloatbutton.Controls.Add` 常驻面板（随页面显隐自动生效，无需 open/close） |
| `BuildDeviceTooltipText(int idx, bool connected)` | 构建设备按钮 Tooltip 文本：`设备名 + 「：已连接/：未连接」`；初始化与状态刷新共用，保证格式一致 |
| `OnDeviceSwitchClick(int idx)` | 线激光（`LineLaserSwitchIndex`）→`ToggleLineLaserConnection()`；其余→`Message.info` 提示「暂未接入，无法操作」；徽标/背景刷新由定时器驱动，点击后不立即变色 |
| `RefreshDeviceSwitchUi()` | **public 单一刷新入口**：经 `IsLineLaserRunning()` 读 `LineLaserWorkflow.Instance.Step`（Starting/Working=运行中）；连接态与 `_lastLlConnected` 相同则跳过，变化同步改线激光按钮 `BadgeSvg`（`CheckCircleFilled` 对勾=连接 / `CloseCircleFilled` 叉号=断开）+ `BadgeBack`（绿(82,196,26)/红(255,77,79)）+ `DefaultBack`（连接=null 主题默认白 / 断开=灰(158,158,158)）+ Tooltip 状态文本（`SetTip` 原地更新「设备名：已连接/未连接」），免重建免闪烁；由 `FormMain.uiMillisecondTimer1_Tick` 每周期调用 |
| `SetDeviceIconSvg(int idx, string iconSvg)` | **public 预留接口**：替换指定设备按钮的 `IconSvg` 并同步 `_deviceIconSvgs[idx]` 缓存（各按钮设备指向不同，逐个设置；越界/未初始化静默忽略） |
| `SetDeviceBadgeSvg(int idx, string badgeSvg)` | **public 预留接口**：设置指定设备按钮的 `BadgeSvg`（AntdUI 原生徽标 SVG 属性，设置后徽标以 SVG 呈现、颜色仍随 BadgeBack 红/绿） |
| `ToggleLineLaserConnection()` | 线激光断开/连接切换：仅向 `LineLaserWorkflow.Instance` 发起 `Start()`(Standby→启动)/`Stop()`(运行态→停机)/`Reset()`(ManualStopped/ErrorAborted→重新初始化回 Standby)，实际连接/开激光在实例自身后台线程执行 |

> 事件绑定在设计器生成代码内：`uiMillisecondTimer1.Tick`/`buttonSZ.Click`/`inputLog.TextChanged`/`MainPage.Shown`/`FormMain.FormClosed` 等（脚本标记的"疑似死函数"为误报，Grep 确认非零引用）。

## 设计约束

- [[decisions/ADR-001-DisposePattern]] / [[decisions/ADR-034-DisposePatternFullCoverage]]：UI 类按需 `DisposeComponents()`，未重写 `Dispose(bool)`；`HandleDestroyed` 触发。
- [[decisions/ADR-002-CS73-Constraint]]：字段声明处不初始化（统一 ctor 内），无 switch 表达式等。
- [[decisions/ADR-039-YinglaiDataFlow]]：英莱数据流（CamRun 分发 + Signal 高性能显示）+ imageBox/ScottPlot 坐标系区分（两者仅朝向一致，ScottPlot 直绘原始坐标不平移）。
- 2026-08-27 代码精简：删 4 未用字段（robotDataRefresh/laserDataRefresh/ClinkTimes/StartTest）+ 死函数 `ResetChartLineData()` + 内联 `LoadComponent()`；补 5 `#region`；public 方法归集；XML 注释补全。`csharp_review.py` 扫描 23→2 项（0 error/0 warn/2 info）。
- 2026-08-31 硬件快捷开关由 FloatButton 覆盖层改为 **AntdUI `ButtonShadow` 常驻按钮**（[[decisions/ADR-045-ButtonShadowDeviceSwitch]]）：构造函数代码后置创建 6 个按钮直接放入 `panelfloatbutton` 面板，随页面显隐自动生效；线激光连接态真相源统一走 `LineLaserWorkflow.Instance.Step`（经 `IsLineLaserRunning()` 判定 Starting/Working，不读 `CameraSelector.ConnectionState`——初始化已连 socket 但激光关闭，避免误判，ADR-018 精神），线激光手动 Start/Stop/Reset 同步驱动 `LineLaserWorkflow` 状态机，不本地缓存连接布尔。**同日风格迭代（buttonShadow1 形态）**：删按钮 Text 改 50×50 仅 SVG 图标（默认 poweroff 电源 SVG），设备名经 `TooltipComponent`（`ArrowAlign=TAlign.Top`）顶部提示，连接态配色由 `Type`（TTypeMini）改为**原生徽标** `Badge=""`+`BadgeMode=true`+`BadgeBack` 红/绿（按钮保持中性态）；新增预留接口 `SetDeviceIconSvg`/`SetDeviceBadgeSvg`；`DisposeComponents()` 增加 `_tooltip` 释放。

## 协作

- 上游：`CameraSelector.Active`（英莱 `IntelligentLaserCameraRun`，[[modules/IntelligentLaserCam]]）、`GlobalCommData`（日志事件）、`ChartVar`（实时数据，WeldParamControl）。
- 承载：由 `FormMain.LoadNavAndPages()` 实例化并 `AddTabSelect` 到 Tab0。
- 状态联动：硬件开关 UI 由 `FormMain.uiMillisecondTimer1_Tick` 每周期调 `RefreshDeviceSwitchUi()` 刷新；整机状态/流程状态/系统时间由 `FormMain` 状态栏承载（底部状态栏已裁剪，仅保留此三项，设备级连接标签已移除）。

---

*来源：AdaWeldSystem/UIDesign/ControlPage/MainPage.cs + .Designer.cs*
