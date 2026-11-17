---
title: FormMain 主窗口
date: 2026-08-27
tags: [API, UI, 主窗口, 导航, 状态标签, AntdUI]
source: AdaWeldSystem/UIDesign/MainWindow/FormMain.cs + .Designer.cs
---

# FormMain — 主窗口

> 应用程序主窗口（AntdUI `Window`），承载顶部 Segmented 导航 + Tabs 内容区，加载 4 个子页面，统管整机状态标签、线激光/设备连接态刷新、关闭前询问与单例资源级联释放。2026-08-27 经五维度代码精简（删死函数、补 #region、XML 注释精简）；**同日状态栏裁剪：仅保留整机状态/流程状态/系统时间三项，设备级连接标签移除并改由 MainPage `ButtonShadow` 常驻按钮表征（2026-08-31 由 FloatButton 替换而来，ADR-011）**。

## 基本信息

| 项 | 值 |
|----|----|
| 类 | `AdaWeldSystem.FormMain` |
| 基类 | `AntdUI.Window`（主窗体） |
| 文件 | `UIDesign/MainWindow/FormMain.cs` + `.Designer.cs` |
| 命名空间 | `AdaWeldSystem` |
| 依赖 | `AdaWeldSystem.Comm.SystemComm`、`AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`、`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`、`AdaWeldSystem.UIDesign.ControlPage`、`AdaWeldSystem.UIDesign.TabPage`、`MonitorCam`、`MotionControl`、`LineLaserCam` |

## #region 结构（2026-08-27 精简后）

| Region | 成员 |
|--------|------|
| 私有变量 | `mainPage`/`navPageParam`/`dataPage`（子页面）、`HidePage`、`_hiddenItem1~3`（SegmentedItem 引用）、`_initWaiting`（初始化等待面板） |
| 构造函数 | `FormMain()` |
| 私有函数 | `FormMain_FormClosing`/`LoadNavAndPages`/`OnWorkflowStateChanged`/`UpdateStatusLabel`/`ShowStatus`/`OperateLevelControl`/`ShowTreeNode`/`HideTreeNode`/`OnOperateLevelChanged`/`uiMillisecondTimer1_Tick`/`FormMain_FormClosed`/`buttonSZ_Click` |

## 关键方法

| 方法 | 说明 |
|------|------|
| `FormMain()` | 设计器模式早退；加载配置（MontionManager.Instance.MoveData/SimulationController/MonitorAlgorithmManager）→ UI 主题 → 实例化 3 子页 → `LoadNavAndPages()` → 订阅线激光状态、关闭前询问、设备初始化（`DeviceControlWork.Instance.InitializeMachine()` + `StartMachine()`，ADR-034） |
| `LoadNavAndPages()` | 构建顶部 4 项 Segmented（主页面/设备监控/系统参数设置/数据追溯）+ 4 个 Tabs，建立 Segmented↔Tabs 双向联动（重入守卫 `syncing`），并把默认索引显式置 0（主页面）；两处联动末尾在目标为「数据追溯」(index 3) 时调 `dataPage.EnsureLoaded()` —— 这是**用户交互**触发点，页面内部再以运行态标志硬闸（H11）；Tab0 主页面内 `AddContourLineChart()`/`AddNewDataLineChart()` 初始化图表并订阅英莱轮廓事件；**Tab1「设备监控」为空占位页**（无控件、无类，后续在 Designer 补内容）；Tab2 承载 `navPageParam`（5 个子页：工艺设置/系统设置/线激光设置/监控相机设置/文档备份设置，ADR-051 演进） |
| ~~`InitializeSystemStatusLabel`/`OnMainDeviceStatusChanged`/`UpdateSystemStatusLabel`~~ | **2026-09-08 整页删除**：整机状态显示迁移至 `MainPage.LabelStatus`（文本「设备状态：{状态值}」+ 设备颜色映射，见 [[api/MainPage]]） |
| `OnWorkflowStateChanged(object, WeldStatusChangedEventArgs)` | 线激光焊接过程态变更回调（订阅 `LineLaserWorkflow.Instance.WeldStatusChanged`，ADR-034），`BeginInvoke` 封送后调 `UpdateStatusLabel` |
| `UpdateStatusLabel(SubDeviceWeldStatus)` | 线激光焊接过程态映射为状态栏文本（NoReset/Standby/PreWork/Working/Stopping/ErrorAborted/ManualStopped） |
| `uiMillisecondTimer1_Tick` | 每周期驱动顶部状态刷新：`ShowStatus()` 更新整机/流程/系统时间标签，并调 `mainPage.RefreshDeviceSwitchUi()` 刷新 MainPage 硬件快捷开关（`UpdateDeviceStatus()` 旧方法已于 2026-08-27 状态栏裁剪时删除，设备级连接标签改由 MainPage `ButtonShadow` 常驻按钮表征，ADR-011） |
| `FormMain_FormClosed(object, FormClosedEventArgs)` | 退订单例事件（`LineLaserWorkflow.WeldStatusChanged`）+ `DeviceControlWork.Instance.Dispose()` + `LineLaserWorkflow.Instance.Dispose()`（设计器 Dispose 不覆盖单例事件订阅，须显式退订；整机状态订阅退订已随迁移移入 `MainPage.DisposeComponents()`） |
| `FormMain_FormClosing(object, FormClosingEventArgs)` | 关闭前询问：运行中设备确认强制关闭，否则确认退出；`AntdUI.Modal.open` 非 OK 则 `e.Cancel=true` |
| `buttonSZ_Click(object, EventArgs)` | 登录按钮：弹 `LoginForm` 模态 |

## 权限门控（2026-10-08 S-11 落地）

程序启动默认 **管理员**（调试期裁定）；在登录窗点「注销」降为 **操作员**，以下三处即时生效（经 `GlobalCommData.OperateLevelChanged` 广播）：

| 载体 | 行为 | 实现 |
|---|---|---|
| **状态栏权限标签** | `lbl_OperateLevel`（右对齐）显示「权限：管理员 / 工程师 / 操作员」，随 `uiMillisecondTimer1_Tick` → `OperateLevelControl()` 每周期刷新 | `FormMain.Designer` 新增标签 + `OperateLevelControl()` |
| **顶部导航显隐** | 工程师及以上 → `ShowTreeNode()` 恢复「设备监控/系统参数设置/数据追溯」；**操作员 → `HideTreeNode()` 移除三项**并回退到「主页面」 | `HidePage` 标志双向维护 + 三项引用非空守卫 |
| **系统设置·激光头页** | 非管理员整页隐藏 + 两面板禁用 + 切页二次校验 | `SystemControlPage.ApplyPermissionGate`（见 [[api/SystemControlPage]]） |
| **权限来源** | `GlobalCommData.SetOperateLevel` 唯一写入口 + `OperateLevelChanged` 广播，职责集中在 `PermissionLevel`（见 [[api/GlobalCommData]]） |

> ⛔ **2026-10-08 修复的既有缺陷**：`OperateLevelControl()` 原先只有 `ShowTreeNode()`（恢复可见）**没有隐藏分支**，
> `case OperateLevel.Operator: break;` 是空分支 ⇒ `HidePage` 永远为 `false`，**降权时导航项实际一个都没藏**。
> 本轮补 `HideTreeNode()` 后才真正生效。旧代码注释「操作级别标签已从状态栏移除」同期废止 —— 权限标签已恢复。

> 事件绑定在设计器生成代码内：`uiMillisecondTimer1.Tick` / `buttonSZ.Click` / `inputLog.TextChanged` / `MainPage.Shown` / `FormMain.FormClosed` → 对应 handler（脚本标记的"疑似死函数"为误报，Grep 确认非零引用）。

## 设计约束

- ADR-002（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）：`.Designer.cs` 标准 `Dispose`，`.cs` 未重写 `Dispose(bool)`；单例事件退订与 Dispose 级联在 `FormMain_FormClosed` 显式完成。
- [[guides/WinForms-Designer]]：控件声明与布局全部位于 `.Designer.cs`。
- 2026-08-27 代码精简：删死函数 `HideTreeNode()`（仅被注释调用）；补 3 `#region` 配对；7 私有方法 XML 注释精简（`///` summary ≤20 字 + `<param>`）。`csharp_review.py` 扫描 17→5 项（0 error/0 warn/5 info）。

## 协作

- 子页面：`MainPage` / `NavPage` / `DataReviewerPage`（均 `AdaWeldSystem.UIDesign.ControlPage`）。
- 状态源：`DeviceControlWork`（整机状态 `MainDeviceStatus`，ADR-034 三态模型）、`LineLaserWorkflow`（焊接过程态 `SubDeviceWeldStatus`）；设备连接态现由 `MainPage` `ButtonShadow` 常驻按钮表征（ADR-011），状态栏仅承载流程状态/系统时间两项；整机状态显示已迁移至 `MainPage.LabelStatus`（2026-09-08，`lbl_SystemStatus` 删除）。

---

*来源：AdaWeldSystem/UIDesign/MainWindow/FormMain.cs + .Designer.cs*
