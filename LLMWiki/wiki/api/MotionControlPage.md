---
title: MotionControlPage 运控调整参数页
date: 2026-07-17
tags: [API, UI, 运控, 参数页, NavPage]
source: AdaWeldSystem/UIDesign/TabPage/MotionControlPage.cs + .Designer.cs
---

# MotionControlPage — 运控调整参数页

> 运控调整的人机参数入口，作为 `NavPage`（参数界面实例）的**工艺配置**子页挂载。2026-07-17 由 `Sub3UI/MotionControlParamForm`（误置弹窗目录、代码内构建）迁入 `Sub2UI` 并改为**设计器生成**（`.Designer.cs` 布局），符合 NavPage 子页均位于 Sub2UI 的既有约定。

## 基本信息

| 项 | 值 |
|----|----|
| 类 | `AdaWeldSystem.Sub2UI.MotionControlPage` |
| 基类 | `UserControl`（AntdUI 无 UIPage 基类，页面以 `UserControl` 承载，由 NavPage 的 `AntdUI.Tabs` 挂载；容器标题由 `GroupBox.Text` 承载） |
| 文件 | `UIDesign/TabPage/MotionControlPage.cs` + `.Designer.cs` |
| 挂载 | `ControlPage/NavPage.cs`：经 NavPage.LoadTabs() 挂载（`uiTabControl1.AddTabSelect(tab)`），节点归参数界面「工艺配置」父节点 |
| 命名空间依赖 | `AdaWeldSystem.Comm`、`AdaWeldSystem.VirtualCam`、`AdaWeldSystem.MotionControl` |

## 界面构成（设计器生成，`.Designer.cs`）

> 2026-08-07 GridPanel+FlowPanel 改造：外层 `gridMain`（`AntdUI.GridPanel`，Span="65%:fill;35%:fill"）两行布局；上行 `gridRow0`（Span="50% 50%"）两列分别放置标定参数面板和模拟测试面板；下行跨列放置运动轴参数面板。每个面板为 `AntdUI.Panel`（白底+灰边+阴影动画），内嵌 `gridXxxInner`（Span="32:fill;fill"，标题行+内容行），内容行使用 **`AntdUI.FlowPanel`** 流式排列 label+input（替代 TableLayoutPanel）。

| Panel 面板 | FlowPanel | 关键控件 | 用途 |
|-----------|-----------|----------|------|
| `panelCalib` 标定数据参数 | `flowPanelCalib` | `txtFrontOffset` / `txtAngle` / `txtScaleX` / `txtCenterX` / `txtCenterY` / `txtApproach`（`AntdUI.Input`）、`btnSaveCalib`（`AntdUI.Button`） | 写入 `MontionManager.Instance.MoveData`（见 [[api/MoveControlData]]） |
| `panelSim` 模拟测试参数 | `flowPanelSim` | `cmbProfile`（`AntdUI.Select`：V型/U型/平直/随机）、`chkRandom`（`AntdUI.Checkbox`）、`cmbSimMode`（`AntdUI.Select`：关闭/A/B/C）、`txtStartX` / `txtSpeed` / `txtTargetDist`（`AntdUI.Input`）、`btnSaveSim` / `btnStartSim`（`AntdUI.Button`） | 写入 `DeviceControlWork`（`SimStartX`/`SimSpeed`/`SimTargetDistance`/`CurrentMode`，[[api/DeviceControlWork]]）并套用至 `VirtualCameraRun`（`CameraSelector.Active as VirtualCameraRun`，[[api/VirtualCam]]） |
| `panelAxis` 运动轴参数 | `flowPanelAxis` | `lblAxisTitle` / `lblAxisNote`（`AntdUI.Label`，占位） | 预留（待对接真实运动控制器，通过 [[api/MontionManager]] 管理） |

**FlowPanel 配置规范**：`Align=TAlignFlow.Left`（左对齐流式）、`Gap=8`（控件间距）、`Padding=(10,4,10,4)`（内边距）、`Dock=Fill`；Label 统一尺寸 `Size=(150, 34)` + `TextAlign=MiddleLeft`；Input/Select 统一尺寸 `Size=(160, 32)`；Controls.Add 按「label→input」顺序成对添加，自动从左到右排列并换行。

下拉项由 `PopulateComboBoxItems()` 在 `InitializeComponent()` 之后填充；`cmbSimMode` 的「关闭」对应 `SimTestMode.None`（[[modules/Comm]]）。

## 关键方法

| 方法 | 说明 |
|------|------|
| `PopulateComboBoxItems()` | ctor 中填充 `cmbProfile` / `cmbSimMode` 下拉项 |
| `LoadFromModel()` | 开启时从 `MontionManager.Instance.MoveData` / `DeviceControlWork`（模拟参数）/ `VirtualCameraRun` 回填各控件 |
| `BtnSaveCalib_Click(object, EventArgs)` | 写回 `MontionManager.Instance.MoveData` 六项标定参数并调用 `Save()` 落盘至 `Config/XML/DeltaMotionConfig.xml` 的 `CALIBRATION` 节，`Message.success(this, ...)` 提示 |
| `BtnSaveSim_Click(object, EventArgs)` | 写回 `DeviceControlWork` 模拟参数（含 SeamProfile/RandomMode 持久化代理）+ 应用 `VirtualCameraRun` 轮廓/随机设置，并调用 `DeviceControlWork.Instance.SaveSimulation()` 落盘至 `Config/INI/SimulationController.ini` |
| `BtnStartSim_Click(object, EventArgs)` | 模拟流程启停总入口：开启时 `EnableSimulation(mode)` → 订阅线激光状态 → `StartLineLaserWithPending()` → 运控跟踪工作流（`MotionControlWorkflow`）→ 按钮转「停止」；**启动任一步骤异常**由 `ShowSimErrorDialog` 将按钮转红色「清理异常」并弹 Modal，后续步骤以 `_simError` 短路；停止时**先退订事件再**反向停止三套流程（避免 `Stop` 触发 `StateChanged` 异步回调二次进入停止路径）→ `Disable()` → `ShowSimStopMessage`(Message 弹窗) + `LogSimStopSummary`(清晰停止原因) → 按钮恢复「开启模拟流程」。**清理分支兜底**：`_simError \|\| LineLaserWorkflow.State==ErrorAborted` 任一成立即进 `CleanupSimError()`（防异步事件使 `_simError` 错位导致不恢复） |
| `SetSimButtonMode(SimButtonMode)` | 模拟按钮三态控制：Start(空闲/幽灵按钮Primary) / Stop(运行中/实心红背景Error) / Cleanup(异常终止/实心红背景Error)；通过 `Ghost + Type` 组合实现背景色切换（`Ghost=false` 时 `Type=Error` 才是红色实心背景） |
| `CleanupSimError()` | **2026-08-27 修复**：清理异常并复位。各后端调用（`StopSimulationFlows`/`Reset`/`Disable`）各自独立 try/catch 记录，按钮复位 `SetSimButtonMode(Start)` 与 `ShowSimStopMessage`/`LogSimStopSummary` 均置于 **`finally`**，确保无论后端是否抛异常按钮**必定恢复默认态**且必出停止确认（解决「点击清理异常后无反应/不恢复」+「停止无清晰原因/无弹窗」） |
| `ShowSimErrorDialog(string)` | **2026-08-27 新增/修正（13:47 修复）**：模拟异常统一提示（**需用户确认**）= `GlobalCommData.ShowLog` + `AntdUI.Modal.open(TType.Error)` 弹窗 + 按钮转红色「清理异常」（`ShowSimErrorButton`）；`InvokeRequired` 时 `BeginInvoke` 封送（异步，不阻塞工作流线程，见 [[guides/WinForms-UI-Threading]]）。区别于正常停止用 `AntdUI.Message`(无需确认)。**2026-08-27 13:47 修复**：`else`（UI 线程）分支 content 原误用未定义 `m`，已改为方法参数 `msg`；`Form.ActiveForm` 作 owner 合法，级联误报"Form→Target"消失，见 [[lessons/AntdUI-Modal-Config-Overload-Cascade]] |
| `ShowSimStopMessage(string)` | **2026-08-27 新增**：正常停止提示（**无需确认**）= `GlobalCommData.ShowLog` + `AntdUI.Message.info` 弹窗（原因文本如「用户停止指令/焊缝行程完成/异常清理恢复」）；`InvokeRequired` 封送 |
| `LogSimStopSummary(string)` | **2026-08-27 新增**：停止原因确认信息 = 汇总 `LineLaserWorkflow.WeldStatus` / `MotionControlWorkflow.WeldStatus` / `MonitorCameraWorkflow.WeldStatus` / `DeviceControlWork` 模拟模式态，输出「人话」式停止原因（区别于底层「状态迁移」调试日志） |
| `ParseDouble(AntdUI.Input, double)` | 静态解析辅助，失败回退默认值 |

> 事件绑定在设计器生成代码内：`btnSaveCalib.Click` / `btnSaveSim.Click` / `btnStartSim.Click` → 对应 handler。

## 设计约束

- [[decisions/ADR-001-DisposePattern]]：`.Designer.cs` 标准 `Dispose`，`.cs` 未重写 `Dispose(bool)`。
- [[guides/WinForms-Designer]]：控件声明与布局全部位于 `.Designer.cs`；`InitializeComponent()` 不含 `for`/`if`/`while` 等流程控制。
- [[guides/Namespace-Compilation]]：`.cs` + `.Designer.cs` 已注册至 `.csproj`。
- [[guides/Namespace-Compilation]]：`.cs` 引用的控件名（`txtFrontOffset` 等）与 `.Designer.cs` 声明严格一致。

## 协作

- 上游：标定数据 → [[api/MoveControlData]]；模拟/轮廓 → [[api/DeviceControlWork]] + [[api/VirtualCam]]。
- 容器：[[modules/UIDesign]] 的 `NavPage` 参数界面实例（ControlPage）。

---

*来源：AdaWeldSystem/UIDesign/Sub2UI/MotionControlPage.cs + .Designer.cs*
