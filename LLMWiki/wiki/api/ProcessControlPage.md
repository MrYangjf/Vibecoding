---
title: ProcessControlPage 工艺设置页（原 ParamConfigPage）
date: 2026-09-17
updated: 2026-11-18
tags: [API, UI, 工艺设置, 工艺调试快捷设定, 线激光标定, 光丝对中, NavPage, ADR-032, ADR-042, ADR-042, ADR-042, ADR-066, ADR-067, ADR-068, GA设置区, 控件删除]
source: AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs + .Designer.cs
---

# ProcessControlPage — 工艺设置页（四 Tab 分区）

> 🔄 **2026-09-29 更名 + 分区重构（业主令）**：类与文件 `ParamConfigPage` → **`ProcessControlPage`**（页面显示名「**工艺设置**」；`csproj` 六处条目、`FormMain.cs` 实例化、`drift_scan_precise.py` RENAMED 同步）。根容器 `AntdUI.Tabs` 由 `tabsConfig` 改名 **`tabsProcess`**，四页重排为：**① 工艺调试快捷设定**（`tabPageQuickSetup`，新增）→ **② 自适应调整工艺设置**（`tabPageAdaptiveSetup`，原「焊参调整」改名）→ **③ 线激光追踪工艺设置**（`tabPageLaserProcess`，原「线激光标定」改名）→ **④ 光丝对中工艺设置**（`tabPageLaserProcessLa`，新增占位）。**原「轨迹点控制」与「模拟测试」两页整体迁出**至 [[api/SystemControlPage]]（分别归「跟踪系统参数」与「模拟测试」页）。历史沿革中的 `ParamConfigPage` / `tabsConfig` / `tbPanelAlogControl` / `tbPanelSimTest` 等旧名沿用叙事，现役名以本框为准。

> 焊接工艺参数的人机配置入口，作为 `NavPage`（参数界面实例）的**工艺设置**子页挂载。
> **2026-09-29 Tabs 改造（业主令）**：根容器由 `tableLayoutPanel7`（2 列 × 3 行）改为 **`AntdUI.Tabs`（`tabsConfig`，`Dock=Fill`，`TabMenuVisible=false`）**——四个面板各占一个 `AntdUI.TabPage`：「**焊参调整**」`tabPageAdaptiveSetup`→`panelWeldList` / 「**线激光标定**」`tabPageLaserProcess`→`panel1` / 「**轨迹点控制**」`tabPageAlgoControl`→`panel2` / 「**模拟测试**」`tabPageSimTest`→`panel3`，**面板外壳与内层 TLP/控件零改动**，根除「参数过长需整页下拉」。沿革（2026-09-17 面板重组）四个面板——`tbPanelAdaparam`（焊接工艺自适应调参模型）、`tbpanelweldponts`（线激光标定）、`tbPanelAlogControl`（轨迹滤波算法）、`tbPanelSimTest`（模拟测试，由 `MotionControlPage` 整体迁入）；其中线激光标定/轨迹滤波/模拟测试三项为本轮回填新增或迁入，焊接工艺自适应调参模型 `tbPanelAdaparam` 为既有面板。
> **2026-09-22 二度重组（[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]）**：① `tbPanelAlogControl` 由「轨迹滤波算法」改名 **「轨迹点控制」**（标题控件 `lblAlgoThreshTitle` 文本同步为「轨迹点控制」），**4 列 × 35 行（2026-09-22 ADR-042 在 ② 方向平滑组增「最终目标最大突变(mm)」）**，按 ① 线激光点过滤 / ② 方向平滑 / ③ CSP 输出 / ④ 折返监测 / ⑤ 跟踪几何 **五组**重排；② `tbpanelweldponts` 收窄为**纯标定 5 项**（**6 列 × 5 行**），跟踪几何 9 项迁入轨迹点控制面板；③ **PVT 参数 11 个控件真删**（不再 `Visible = false` 占位）；④ 按钮文本改为「保存/读取轨迹点参数」。

> **2026-10-08 业主新方案落地（S-10 第二轮）**：`tabsProcess` **4 页 → 3 页** —— `tabPageQuickSetup`（**快捷设置**，页内 `tabsQuickSetup` 4 区：功能启用 / Tracking指令 / TA指令 / LA指令）· `tabPageAdaptiveSetup`（**自适应工艺参数设置**）· `tabPageLaserProcess`（**激光工艺设置**，页内 `tabsLaserProcess` 3 区：Tracking设置 / TA设置 / LA设置）。**光丝对中页（`tabPageWireAlign`）已并入 LA 设置区**（`panelWireAlign` + `lblWireAlignTip` 占位随之迁入）。**线激光标定组（中心 Y/Z + 示教 Y 锁定 + 水平轴角度 + 读取/保存按钮，共 12 控件）连同 `LoadLaserCalibOnForm` / `BtnSaveLaserCalib_Click` / `BtnReadLaserCalib_Click` 三个方法已迁至 [[api/SystemControlPage]] 的轨迹跟踪参数设置页**。⚠️ TA指令 / TA设置 / LA设置 / LA设置 四区本轮**只建空骨架**，控件待 P3 后端接口（`SetTorque`/`StopTorque`/`SetMotorPosEnable`）接入后填。

## 章节导航

- [基本信息](#基本信息)
- [界面构成（四 Tab 分区）](#界面构成四-tab-分区antduitabs-tabsprocess)
- [关键方法（参数保存/读取）](#关键方法参数保存读取2026-09-18-拆分)
- [设计约束](#设计约束)
- [指令区 Radio 化与 TA 参数区](#指令区-radio-化与-ta-参数区2026-10-12-adr-063080)
- [LA 参数区与 TA_Retract](#la-参数区与-ta_retract2026-10-14-adr-0672026-11-05-更名)
- [初始化闸门与指令状态检测](#初始化闸门与指令状态检测2026-11-05adr-082063-演进)
- [相关页面](#相关页面)

## 基本信息

| 项 | 值 |
|----|----|
| 类 | `AdaWeldSystem.UIDesign.TabPage.ProcessControlPage`（2026-09-29 由 `ParamConfigPage` 更名） |
| 基类 | `UserControl`（由 NavPage 的 `AntdUI.Tabs` 挂载） |
| 文件 | `UIDesign/TabPage/ProcessControlPage.cs` + `.Designer.cs` + `.resx` |
| 挂载 | `UIDesign/MainWindow/FormMain.cs` → `navPageParam.LoadTabs(("工艺设置", new ProcessControlPage()), …)` |
| 命名空间依赖 | `AdaWeldSystem.WeldParamControl`、`AdaWeldSystem.MotionControl`、`AdaWeldSystem.Comm.SystemComm`、`AdaWeldSystem.MainDeviceControl` |

## 界面构成（四 Tab 分区，`AntdUI.Tabs` `tabsProcess`）

> 根容器 `tabsProcess`（`AntdUI.Tabs`，`Dock=Fill`，`Type = AntdUI.TabType.Card`，`TabMenuVisible=false`，2026-09-29 由 `tabsConfig` 改名）：

| Tab | 控件 | 内容 | 去向 |
|---|---|---|---|
| ① 工艺调试快捷设定 | `tabPageQuickSetup` → `panelProcessDebug` → `tlpProcessDebug`（11 行 × 2 列） | 4 组工艺启用 `Switch` + 3 个快捷锁定 `Checkbox` + 保存/读取 | **2026-09-29 新增；同日二次改为 Switch/Checkbox** |
| ② 自适应调整工艺设置 | `tabPageAdaptiveSetup` → `panelWeldList` → `gridWeldZones`（左参数列表 + 右设置，ADR-072 见文末） | 焊接工艺自适应调参模型（原「焊参调整」） | 改名 + 2026-10-15 左右分栏重构 |
| ③ 线激光追踪工艺设置 | `tabPageLaserProcess` → `panel1` | 线激光标定（原「线激光标定」） | 改名，内容零改动 |
| ④ 光丝对中工艺设置 | `tabPageLaserProcessLa` → `panelWireAlign` | 占位 `lblWireAlignTip` | **2026-09-29 新增占位** |

### ① 工艺调试快捷设定（2026-09-29 新增）

> 业主口径：本页承载「各个控制工艺是否启用 + 快捷调试设定」。
> **2026-09-29 二次裁定（现行）**：① 启用/停用改用 **`AntdUI.Switch`**（原 `AntdUI.Select` 下拉已废）；② 三个快捷项是**指令**而非一次性动作，改用 **`AntdUI.Checkbox`**——**勾选＝把对应轴移到标定/锁定位置并保持锁定，取消勾选＝解除锁定**（运控层 `MontionAxis` 无锁定 API，故锁定只表达为**配置标志**，供后续工艺逻辑消费）。

| 控件 | 类型 | 绑定 | 说明 |
|---|---|---|---|
| `swEnableAdapt` | `AntdUI.Switch` | `WeldAlgorithmsConfig.EnableGuide` | 自适应调整工艺启用（共用 EnableGuide） |
| `swEnableSeamTrace` / `swEnableWireAlign` / `swEnableTempCtrl` | `AntdUI.Switch` | `EnableSeamTrace` / `EnableWireAlign` / `EnableTempCtrl` | 线激光追踪 / 光丝对中 / 温控 三路工艺启用开关 |
| `chkLockYCalib` | `AntdUI.Checkbox` | `LockYCalib` | 「Y轴回标定位置」：勾选移到 `TeachLockYMm` 并锁定；取消解除锁定（不移动） |
| `chkLockSpotCalib` | `AntdUI.Checkbox` | `LockSpotCalib` | 「光斑回标定位置」：勾选移到 `SpotCalibPosMm` 并锁定 |
| `chkLockWirePos` | `AntdUI.Checkbox` | `LockWirePos` | 「送丝结构锁定位置」：勾选移到 `WireLockPosMm` 并锁定 |
| `btnSaveProcessDebug` / `btnReadProcessDebug` | `AntdUI.Button`（Success/Default） | — | 保存 / 读取本页 4 开关 + 3 锁定态 |
| `lblQuickDebugTip` | `AntdUI.Label` | — | 提示文本 |

**锁定语义（业主裁定）**：`ApplyLockState(box, keys, targetMm, actionName, setFlag)` 统一处理——勾选时置标志 + `AbsMove` 到目标位，取消时清标志且**不下发运动**；两者均立即 `SaveAlgorithmsConfig()` 落盘。

> ⛔ **回填抑制**：`LoadProcessDebugOnForm()` 设置 `Checked` 会触发 `CheckedChanged`（Designer 已绑定），故用 `_loadingProcessDebug` 标志位包住回填，**避免页面加载即误下发运动指令**。

**轴查找约定**：三个锁定项经 `MontionManager.Instance` 按**关键字匹配**轴名（`YAxisKeys = { "Y", "横梁", "跟踪" }` / `SpotAxisKeys = { "对焦", "焦点", "光斑", "FOCUS", "SPOT" }` / `WireAxisKeys = { "送丝", "WIRE", "FEED" }`）→ `axis.AbsMove(targetMm, 1)`；⛔ **未找到对应轴时给出明确提示，不静默兜底**（配置未就绪时宁可不动）。

> 后端共 8 项（`WeldAlgorithmsConfig`，INI 段 `PROCESS_CONTROL`）：`ENABLE_SEAM_TRACE` / `ENABLE_WIRE_ALIGN` / `ENABLE_TEMP_CTRL` / `SPOT_CALIB_POS_MM` / `WIRE_LOCK_POS_MM` + **2026-09-29 二次新增 `LOCK_Y_CALIB` / `LOCK_SPOT_CALIB` / `LOCK_WIRE_POS`**，读写闭环在 `LoadProcessIni` / `SaveProcessIni`。

### ④ 光丝对中工艺设置（占位）

业主规划后续填入：送丝压力值、对焦光斑大小设定、送丝轴位置锁定、对焦轴位置锁定等；当前仅 `lblWireAlignTip` 占位，无业务逻辑。

### `tbPanelAdaparam`（焊接工艺自适应调参模型，既有面板）
左上 `panelWeldList` 内承载，标题 `label1`（「焊接工艺自适应调参模型」）。承载工艺自适应调参：焊丝/板材/工艺类参数（`WireType` / `WireDiameter` / `PlateType` / `Platethickness` / `LaserPower` / `FeedSpeed` / `RobotSpeed` / `Sensitivity` / `LaserDiameter` / `SeamWidth` / `MaxSeamWidth` / `MinSeamWidth` 等，数值项均 `AntdUI.Input`，2026-09-18 由 `InputNumber` 改，防鼠标滚轮误改值）+ 配置列表操作（`btnAddNewConfig` / `btnShowConfigList` / `btnShowAutoParam` / `btnCorAutoParam` / `mAutoParamName` / `uiComboBox1`）+ 标题 `lblWeldListTitle` / `lblWireTitle` / `lblBaseTitle`；**焊参调整（WeldParamAdjustment，2026-09-17 由轨迹滤波算法面板迁入，标题 `lblWeldAdjTitle`）**：`lblFlowEnableGuide`+`selFlowEnableGuide`（线激光引导启用）、`lblFlowMaxConsecFail`+`txtFlowMaxConsecFail`（最大连续失败次数）、`lblFlowIsCountType`+`selFlowIsCountType`（是否按点数分段）、`lblFlowCountNum`+`txtFlowCountNum`（每段点数）——四项同属 `WeldParamAdjustmentAlgorithm`/全局开关，与轨迹 CSP/PVT 两内核正交。**本面板保存/读取（2026-09-18 拆分，与算法阈值/线激光解耦）**：`btnSaveAutoParam`（「保存焊参调整」→ `BtnSaveAutoParam_Click`：`CollectParamFromForm()` + `WeldParamManager.Instance.SaveCurrentAutoParam()` + 四点流程开关经 `WeldParamManager.Instance.SaveAlgorithmsConfig()` 落盘，**不触发工艺库重算**）/ `btnReadAutoParam`（「读取焊参调整」→ 从内存模型恢复 AutoParam + 从文件重载回填四个流程开关）；`btnCorAutoParam`（「修正基准」）保留为**独立危险操作**（= 保存 + `WeldParamManager.Instance.ReloadCurrentParamValues()` 重算整个焊接工艺库），**不与焊参调整保存混用**。→ ⚠️ 2026-10-20 演进：修正基准恢复为独立按钮 `btnCorBaseline`（自适应参数表旁），`btnCorAutoParam` 改持「修改参数」并收窄为仅底部 INI 区，详见「三按钮统一收口」节。

### `tbpanelweldponts`（线激光标定参数，本轮回填，原 `tlPanelWeldPoints` 改名）
> 🔄 **2026-09-23 ADR-043**：趋近阈值项**根除**（业主判定趋近算法失效，部分撤销 ADR-042 决 1）；「焊缝跟踪模式」下拉删除（PVT 未验证临时禁切，加载期强制 CspRealtime，算法保留）；几何区重排——`YAxisMin`/`YAxisMax` 移至行 7 同行，行 8 右侧留空。
右上 `panel1` 内承载，标题 `label2`（「线激光标定」）；**6 列 × 8 行**（2026-09-22 ADR-042 回迁几何后，ADR-042 时为 6 列 × 5 行）。**承载「标定 2 项 + 跟踪几何 8 项」共 10 项**（LASER_CALIBRATION 段 + SEAM_GUIDE 几何段，均为 XML）：

| 行 | 控件 | 参数 | 标签 |
|---|---|---|---|
| r1 | `lblCalibCenterY`+`txtCalibCenterY` | `CalibratedCenterY` | 标定中心点Y(mm) |
| r1 | `lblTeachLockY`+`txtTeachLockY` | `TeachLockYMm` | 示教Y轴锁定坐标(mm) |
| r2 | `lblGeoSecTitle`（跨 6 列） | — | **跟踪几何** |
| r3 | `lblGeoAxisPerLaser`+`txtGeoAxisPerLaser` | `AxisMmPerLaserMm` | 轴/激光比例系数 |
| r3 | `lblGeoGuideSign`+`selGeoGuideSign` | `GuideSign` | 偏差方向 |
| r4 | `lblGeoLeadDistance`+`txtGeoLeadDistance` | `LeadDistanceMm` | 激光超前量(mm) |
| r4 | `lblGeoRobotYGain`+`txtGeoRobotYGain` | `RobotYGain` | 机器人Y补偿系数 |
| r5 | `lblGeoTrackingMode`+`selGeoTrackingMode` | `TrackingMode` | 焊缝跟踪模式 |
| r5 | `lblGeoYAxisMin`+`txtGeoYAxisMin` | `YAxisMinMm` | Y轴行程下限(mm) |
| r6 | `lblGeoYAxisMax`+`txtGeoYAxisMax` | `YAxisMaxMm` | Y轴行程上限(mm) |
| r6 | `lblGeoMaxMapPoints`+`txtGeoMaxMapPoints` | `MaxMapPoints` | 焊缝地图点数上限 |
| r7 | `btnReadLaserCalib` / `btnSaveLaserCalib` | — | 「读取线激光参数」/「保存线激光参数」 |

> 🔄 **2026-09-22 ADR-042 回迁**：跟踪几何 8 项（`AxisMmPerLaserMm` / `GuideSign` / `LeadDistanceMm` / `RobotYGain` / `TrackingMode` / `YAxisMinMm` / `YAxisMaxMm` / `MaxMapPoints`）**归位本面板**——几何与标定是同一物理语义（传感器 ↔ 轴的对应关系），放在标定页才能「标定完顺手改几何」。`BtnSaveLaserCalib_Click` 写回项数 5 → **10**（2026-09-24 删 `InstallOffsetY` 后 **9**）。
> ⚠️ **`InstallOffsetY`（「安装偏移Y(mm)」）2026-09-24 经业主令真删**（控件四件套 + 配置项 + XML 读写）：ADR-042 起 0 消费（ADR-042 曾删、ADR-042 作标定记录项恢复），且 Load 读 `SEAM_GUIDE` / Save 写 `LASER_CALIBRATION` 读写错位双重失效。
> 🔄 **2026-09-22 三度重组（[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]）**：`tbpanelweldponts` 由「纯标定 5 项」扩为 **6 列 × 8 行**——**跟踪几何组回迁本面板**（`lblGeoSecTitle` 组标题，文本由「⑤ 跟踪几何」去序号为「**跟踪几何**」，`SetColumnSpan(…, 6)`），结构变为 **标定 2 项 + 几何 8 项 + 按钮行**；`tbPanelAlogControl` 相应由 35 行收为 **25 行、四组**。同时 **4 项零消费残骸真删**（`InstallOffsetY` / `LaserToHorizontalAngleDeg` / `CalibratedCenterX` / `ApproachThreshold`），`WeldAlgorithmsConfig` 配置项 **45 → 41**。
> ⚠️ ~~`lblCalibCenterX` 控件名后缀为 X，但标签文本与绑定参数均为 Z~~ **2026-09-22 已随 `CalibratedCenterX` 一并真删**（该参数全项目零算法消费，属既有命名遗留）。

### ~~`tbPanelAlogControl`（轨迹点控制）~~ ⛔ 2026-09-29 已整体迁出
> 🔄 **迁出至 [[api/SystemControlPage]]「跟踪系统参数」页**（业主裁定：轨迹点设定属跟踪系统参数，与 Y 向电机轴配置同页）。原 4 列 × 25 行 TLP（`panel2` 闭包，65 个控件）**整块迁入** `SystemControlPage` 的 `tabPageTrajectoryParam`，代码后置 `LoadAlgoThreshOnForm` / `BtnSaveAlgoThresh_Click` / `BtnReadAlgoThresh_Click` 随之迁移。以下历史描述仅供沿革追溯，**现役位置见 [[api/SystemControlPage]]**。

> 🔄 **2026-09-22 ADR-042 由「轨迹滤波算法」改名重排；ADR-042 增 1 项至 35 行，ADR-042 几何迁出后收为 4 列 × 25 行**
> 🔄 **2026-09-23 ADR-043**：新增行 30「前馈安全系数」(`FeedforwardSafetyFactor`)、行 31「单调方向锁」(`EnableMonotonicConstraint` 启用/停用)；行 29 工艺输出频率改 **60/30/10Hz 下拉**（`selParamOutputHz`，禁手填）；行 26 宽度来源 Select 尺寸 (0,0)→(174,29) 修复。RowCount 30→32。
左下 `panel2` 内承载，标题 `lblAlgoThreshTitle`（**「轨迹点控制」**，原「轨迹滤波算法」）；**4 列 × 25 行**（AutoScroll，含底部保存/读取按钮行；ADR-042 时 35 行，ADR-042 随几何组迁出删 10 行、按钮行 34→24），列宽 40/180/180/40，列 X = 3/43/223/403。每行一个参数（标签列 `col1` + 输入列 `col2`），**按四大功能组分区**（① 点过滤 / ② 方向平滑 / ③ CSP 输出 / ④ 折返监测），组标题跨 4 列（`SetColumnSpan(…, 4)`），互不混放。**保存/读取按钮**：`btnSaveAlgoThresh`（「**保存轨迹点参数**」→ `BtnSaveAlgoThresh_Click` 写回 **19 项**经 `WeldParamManager.Instance.SaveAlgorithmsConfig()` 落盘）/ `btnReadAlgoThresh`（「**读取轨迹点参数**」→ 从文件重载 `LoadAlgoThreshOnForm()` 仅回填本面板）；数值项均 `AntdUI.Input`。

| 组 | 标题控件（行） | 参数项 | 消费方 |
|---|---|---|---|
| **① 线激光点过滤** | `lblCspKernelTitle`（r1） | `RobotYFilterAlpha`（一阶低通；`DyFilterAlpha` 低通项已于 2026-09-23 随地图值低通移除）、`GaussianSigmaMm` / `GaussianHalfWindowMm`（高斯平滑）、`NearbyWindowMm`（野值邻域窗口）、`OutlierSigmaK`（野值3σ倍数）、`OutlierSlopeLimitMmPerMm`（野值切向偏差系数，ADR-042）、`MaxStepChangeMm`（**单帧最大变化**）、`ConsecutiveRejectFrames`（**连续拒绝帧数**）——共 8 项 | `SeamMapTrackingAlgorithm` |
| **② 方向平滑** | `lblPvtKernelTitle`（r10，2026-09-23 行号 −1） | `MonotonicDeadbandMm`（方向判定死区）、`MonotonicReleaseMm`（**方向释放阈值**）、`MonotonicWindowMm`（方向锁最大持距）、**`MaxTargetStepMm`（最终目标最大突变，ADR-042 新增）**——共 4 项 | `SeamMapTrackingAlgorithm.ApplyMonotonic` / `ProcessLaserResult` 突变护栏 |
| **③ CSP 输出** | `lblCspParamTitle`（r15） | `OutputDeadbandMm`（**输出死区**）、`MaxVelMmPerS`（CSP最大速度）、`MaxAccMmPerS2`（CSP最大加速度）、`CspMinSegMm`（**最小有效段距**）——共 4 项 | `MotionControlWorkflow` CSP 写段 |
| **④ 折返监测** | `lblFlowReverseTitle`（r20） | `ReverseAlarmMm`（折返报警里程）、`ReverseDeadbandMm`（折返判定死区）——共 2 项 | `SeamMapTrackingAlgorithm.UpdateDirection` |

> 🔄 **2026-09-22 ADR-042**：~~⑤ 跟踪几何 9 项~~ 已整体回迁 [[#tbpanelweldponts]]（线激光标定），本面板收为**四组 18 项**（2026-09-23 删 `DyFilterAlpha` 后为 18）；`InstallOffsetY` 随组一并删除。

> 🔄 **2026-09-22 重排要点**：① 组标题由「CSP内核 / PVT内核」改为**按处理阶段命名**（点过滤 / 方向平滑），② 原「② 焊缝段跟踪算法 · PVT内核」的两项（`NoValueToleranceMm` / `OutlierLimitMm`）**退出界面**（仅剩 PVT 回退路径 `SeamTrackingAlgorithm` 消费），③ 4 个控件**语义错配改名**：`txtFlowNoValueTol`→`txtFlowOutDeadband`（原标签「无值容差」实绑 `OutputDeadbandMm`）、`txtFlowOutlierLimit`→`txtFlowMaxStepChange`，④ 新增 3 项（`ConsecutiveRejectFrames` / `MonotonicReleaseMm` / `CspMinSegMm`）。

> ⚠️ **2026-09-22 ADR-042 追加（本面板现行）**：② 方向平滑组新增「**最终目标最大突变(mm)**」（控件 `lblFlowMaxTargetStep` / `txtFlowMaxTargetStep`，绑 `WeldAlgorithmsConfig.MaxTargetStepMm`，INI 键 `MAX_TARGET_STEP_MM`，默认 **5.0**，可调更小）——
> 判的是**合成后的绝对目标 Yt** 的帧间跳变（用户口径「突然变化 5mm」），与 ① 组的 `MaxStepChangeMm = 0.5`（判特征偏差 `rawDy` 单分量、拦用户举例的 `{0.3 0.3 1.0 …}`）**分工互补**。`tbPanelAlogControl` 由 34 行扩为 **35 行**，
> 同时顺带修正 ADR-042 遗留：`tbPanelAlogControl` 的 `ColumnStyles` 多出第 5 条空列（原 5 条 ↔ `ColumnCount = 4`）**已删除**，恢复 `Controls.Add` 条数 / `ColumnCount` / `ColumnStyles` 的**三元匹配**。
>
> ⚠️ **PVT 参数已彻底退场（2026-09-22 ADR-042）**：原 `lblPvtParamTitle` 组下的 **11 个控件真删**（`lblFlowBatchSize`/`txtFlowBatchSize`、`lblFlowMinRemainBuf`/`txtFlowMinRemainBuf`、`lblFlowFrameSec`/`txtFlowFrameSec`、`lblFlowMaxOutInt`/`txtFlowMaxOutInt`、`lblFlowMaxPending`/`txtFlowMaxPending` + 组标题）——含实例化行、成员声明行、`SetColumnSpan`；对应的 `BatchSize` / `MinRemainBuffer` / `DefaultFrameSeconds` / `MaxOutputIntervalMs` / `MaxPendingPoints` 5 项**已停止 INI 持久化与界面调配**（仅保留构造函数默认值供 PVT 回退路径使用）。

> ⚠️ 焊参调整四项（`EnableGuide` / `MaxConsecutiveFailures` / `IsCountType` / `CountNum`）已于 2026-09-17 迁至 [[#tbPanelAdaparam]]（焊接工艺自适应调参模型）的「焊参调整」段，与轨迹 CSP/PVT 两内核正交，不在本面板。

### ~~`tbPanelSimTest`（模拟测试）~~ ⛔ 2026-09-29 已整体迁出
> 🔄 **迁出至 [[api/SystemControlPage]]，单开一页 Tab「模拟测试」**（业主裁定）。原 `panel3` 闭包连同代码后置全套（`SimButtonMode` / `BtnStartSim_Click` / `OnSimulationStopped` / `OnLineLaserStateChanged` / `OnMainDeviceStatusChanged` / `ShowSimErrorDialog` / `CleanupSimError`）一并迁入。以下历史描述仅供沿革追溯。

| 方法 | 说明 |
|------|------|
| `PopulateComboBoxItems()` | ctor 中填充 `cmbFreq`（30/60/80/120 Hz） |
| `LoadFromModel()` | 从 `DeviceControlWork.Instance.SimLaserFrequencyHz` 回填 `cmbFreq`（`FrequencyToIndex`） |
| `FrequencyToIndex(int)` / `IndexToFrequency(int)` | 频率 ↔ 下拉索引映射（默认 30Hz） |
| `SyncSimParamsToController()` | 把 `cmbFreq` 索引经 `IndexToFrequency` 写回 `DeviceControlWork.SimLaserFrequencyHz`（不落盘） |
| `BtnSaveSim_Click(object, EventArgs)` | `SyncSimParamsToController()` → `DeviceControlWork.Instance.SaveSimulation()` 落盘 → `Message.success` |
| `BtnStartSim_Click(object, EventArgs)` | 模拟流程启停总入口（开启→`StartSimulation()` 按连接态自动选相机/是否写轴→订阅线激光状态→复位 Standby→`StartSimulationLineLaser()`→`MotionControlWorkflow.Start()`→按钮转「停止」；停止→退订→反向停三套流程→`DisableSimulation()`；**清理分支**=`_simError \|\| (模拟运行中 && 线激光 ErrorAborted) \|\| (模拟运行中 && 整机 Alarm)`→`CleanupSimError()`（含 `ClearAlarm`+复位+关闭模拟），保证「测试报警→清除报警」单键可达（2026-09-22 守卫扩第三条件）） |
| `OnLineLaserStateChanged(...)` / `OnMainDeviceStatusChanged(...)` / `ShowSimErrorDialog` / `ShowSimStopMessage` / `LogSimStopSummary` / `SetSimButtonMode` / `CleanupSimError` / `SubscribeLineLaserEvents` / `UnsubscribeLineLaserEvents` | 同原 `MotionControlPage` 实现（2026-09-17 随控件整体迁入本页）；`OnMainDeviceStatusChanged` 为 2026-09-22 新增（模拟运行中整机 Alarm→按钮显式变红字「清理异常」） |

> 构造函数同时接线：`PopulateComboBoxItems()` + `LoadFromModel()` + `HandleDestroyed` 退订；`ParamConfigPage_HandleDestroyed` 负责资源释放。

## 关键方法（参数保存/读取，2026-09-18 拆分）

> 原共用 `BtnSaveAlgoConfig_Click`（一次性写回全部 `WeldAlgorithmsConfig`）按面板拆为三套独立「保存 + 读取」；`LoadAlgoConfigOnForm` 拆为 `LoadLaserCalibOnForm` / `LoadAlgoThreshOnForm` / `LoadFlowSwitchOnForm`（ctor 与 `ParamAutoPage_Shown` 仍经组合入口 `LoadAlgoConfigOnForm` 调用）。读取按钮仅从文件/内存重载并回填**本面板**，不波及其他面板、不重算工艺库。

| 方法 | 面板 | 说明 |
|------|------|------|
| `BtnSaveLaserCalib_Click(object, EventArgs)` | `tbpanelweldponts` | 写回 **10 项**（标定 2：`CalibratedCenterY` / `TeachLockYMm`；几何 8：`AxisMmPerLaserMm` / `GuideSign` / `LeadDistanceMm` / `RobotYGain` / `TrackingMode` / `YAxisMinMm` / `YAxisMaxMm` / `MaxMapPoints`） → `WeldParamManager.Instance.SaveAlgorithmsConfig()` |
| `BtnReadLaserCalib_Click(object, EventArgs)` | `tbpanelweldponts` | `LoadAlgorithmsConfig()` → `LoadLaserCalibOnForm()` 仅回填本面板 |
| ~~`BtnSaveAlgoThresh_Click`~~ / ~~`BtnReadAlgoThresh_Click`~~ | ⛔ **2026-09-29 已迁 [[api/SystemControlPage]]** | 原写回 **19 项**（四组：点过滤 9 + 方向平滑 4 + CSP 输出 4 + 折返 2） → `SaveAlgorithmsConfig()` |
| `BtnSaveAutoParam_Click(object, EventArgs)` | `tbPanelAdaparam` | `CollectParamFromForm()` + `SaveCurrentAutoParam()` + 四点流程开关 `SaveAlgorithmsConfig()`（**不重算工艺库**） |
| `BtnReadAutoParam_Click(object, EventArgs)` | `tbPanelAdaparam` | `LoadAlgorithmsConfig()` → `LoadFlowSwitchOnForm()` + `LoadParamOnForm()` 从内存恢复 |

## 设计约束

- `.Designer.cs` 标准 `Dispose(bool)`，`.cs` 未重写 `Dispose(bool)`（页面销毁经 `HandleDestroyed` 退订线激光事件）。
- 控件名（`cmbFreq` / `btnSaveSim` / `btnStartSim` / `lblSimTestTitle` / `tbpanelweldponts` / `tbPanelAlogControl` / `tbPanelSimTest`）与 `.Designer.cs` 声明严格一致（⚠️ `lblSimTestTitle` 曾因与 `tbPanelAdaparam.label1` 重名 `label1` 触发 CS0102，已改名）。
- **2026-09-22 面板重构范式（Designer 字节安全改写）**：`ProcessControlPage.Designer.cs` 为**无 BOM + 纯 CRLF**，重构须「读字节 → 按字节 split → 改 → 按字节 join → 写回」，**禁整篇 `Write` 覆写**（否则行尾/BOM 漂移）。TLP 重排须守**三件套一致性**：`Controls.Add(this.x, col, row)` 条数 + `RowCount` + `RowStyles.Add` 条数三者匹配；组标题跨列用 `SetColumnSpan(…, N)`（每标题恰 1 次）。删除控件须**同时清三处**：属性块 + 实例化行（`this.x = new …`）+ 成员声明行（`private AntdUI.X x;`），仅设 `Visible = false` 不算删除。
- **控件改名须与 code-behind 同步**：`ProcessControlPage.cs` 中对改名控件的引用（`Load*OnForm` / `Btn*_Click`）必须一并更新，否则编译失败（CS0103）。
- 焊接工艺自适应调参模型 `tbPanelAdaparam` 持久化经 `WeldParamManager.Instance.SaveCurrentAutoParam()`（AutoParam 标量）+ `WeldParamManager.Instance.SaveAlgorithmsConfig()`（四点流程开关）；`btnSaveAutoParam` **仅落盘、不重算工艺库**——重算工艺库是 `btnCorBaseline`（修正基准，2026-10-20 自 `btnCorAutoParam` 恢复为独立按钮）的独立危险职责，二者不可混用。

## 协作

- 上游：模拟开关与频率 → [[api/DeviceControlWork]]；虚拟相机产帧频率 → [[api/LineLaserManager]] → [[api/VirtualCam]]；轨迹落盘 → `ProductFileRecordManager`（2026-09-20 归口记录模块，原 `SimTrajectoryRecorder` 已删除）。
- 线激光标定参数 → [[api/WeldParamManager]]；轨迹点控制参数 → [[api/SeamMapTrackingAlgorithm]]（消费四组）与 [[api/MotionControlWorkflow]]（消费 ③ CSP 输出组）；**跟踪几何 8 项**归标定页写回，消费方为 `SeamMapTrackingAlgorithm` + `MotionControlWorkflow`。
- 容器：[[modules/UIDesign]] 的 `NavPage` 参数界面实例（ControlPage）。
- ⛔ **2026-09-29 迁出**：模拟测试全套 + 轨迹点控制（19 项阈值）→ [[api/SystemControlPage]]（模拟测试单开一页 Tab；轨迹点归「跟踪系统参数」页与 Y 轴表同页）；运控 CSV/XML 导入导出 → [[api/FilebackupPage]]「系统配置文件」页。
- 更名沿革：`ParamConfigPage` → `ProcessControlPage`（2026-09-29，页面显示名「工艺设置」）。


## 2026-10-19 六轮演进（⑤工艺输出迁入 + MoveAxisToTarget 归 Manager）

1. **⑤工艺输出 11 控件迁入**（自 SystemControlPage 跨 Designer，四形态含 11 行实例化）：
   `gridAdaparam` 16→**20 行 51 格零空格**——尾部新增 4 行：`40:fill`(lblParamOutTitle「⑤工艺输出」) +
   手动宽度/光斑系数 4 列 + 输出频率/前馈安全 4 列 + 单调锁 2 列。
2. **读写链走 facade（算法管理）**：`LoadAlgoConfigOnForm` 组合入口含 **`LoadParamOutOnForm`**
   （`mgr.FeedforwardSafetyFactor/EnableMonotonicConstraint/ManualSeamWidthMm/SpotWidthGain/ParamOutputHz` 5 读）；
   `BtnSaveAutoParam_Click` 追加 5 项收集 + **`SaveAlgorithmsZone(System)`**（前馈/单调锁=System 区；Adapt 区原已有）；
   `BtnReadAutoParam_Click` 补 `LoadParamOutOnForm()`。
3. **MoveAxisToTarget 归 Manager**：`ServoOn+AbsMove` 直控 → `manager.MoveTo`（自动使能，ADR-073）。
4. 注释同步：`LoadProcessEnableOnForm` 单调锁入口注记（ADR-068 演进）；`txtManualWidth_Leave` 同源注释改
   「与本页 ⑤工艺输出区 txtParamManualWidth 同源（同页两入口）」；req4 `out var` 精简（p1/p2 ×2 + Parse 区）。

## 相关页面

- 决策：[[decisions/ADR-032-SimulationTestRedesign]] · [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（轨迹点控制面板重排与 PVT 退场） · [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（新增「最终目标最大突变(mm)」项 + `ColumnStyles` 三元匹配修正） · [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（4 项零消费残骸真删 + 几何组回迁标定页）
- 模块：[[modules/UIDesign]] · [[modules/WeldParamControl]]
- 文档备份设置（2026-09-29 由 `CommPage` 更名，承载通讯/工艺/系统三类配置文件备份与导入导出）：[[api/FilebackupPage]]
- 系统设置页（2026-09-29 四分区：跟踪系统参数 / 光丝系统参数 / 温控系统参数 / 模拟测试；轴表只渲染 Y 轴）：[[api/SystemControlPage]]

---

*来源：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs + .Designer.cs*

## 页内分区容器（2026-10-12 批次K，ADR-062）

> 页内分区由**嵌套 Tabs** 改为 **GridPanel 同屏分区**（业主裁定「tabs 不再向下叠加」）。

| 页 | 容器 | 分区（Span 行数） |
|---|---|---|
| `tabPageQuickSetup`（快捷设置） | `gridQuickZones` | **两列 2×2**：`panelProcessDebug`（功能启用）/ `panelQuickTracking`（Tracking指令，U-4 待填）/ `panelQuickTa`（TA指令）/ `panelQuickLa`（LA指令） |
| `tabPageLaserProcess`（激光工艺设置） | `gridLaserZones` | **两列 2×2 满格**：`panel1`（Tracking设置）/ `panelLaserTa`（TA设置）/ `panelLaserLaZone`（**Panel** 承载 `panelLaserLa` 卡片）/ **`panelLaserGalvo`（振镜功能与图形卡片，2026-10-14 二轮迁入原空白第 4 格，见 ADR-069 §四）** |

**关键约束**

- ⛔ **不新建包裹 Panel**：各分区内容 Panel 本就是 ADR-060 §四 卡片形态（Shadow 5 / BorderColor 217 / 标题 Label），**只换父容器**
- ⛔ **两列布局**：`Span="fill fill;fill fill"`（2 行 × 2 列）⇒ 每区 666×326，比单列 160 高翻倍
- ⛔ **奇数分区必须「声明 4 格只挂 3 控件」**：写 `"fill fill;fill"`（3 格）实测末格**横向拉伸补满整行**（1337 宽），LA 区两卡片反被压扁
- ⛔ **GridPanel 逆序入流**（`Controls.Add` 顺序 = 视觉顺序倒序）
- ⛔ **同父多 `Dock=Fill` 仅在格位容器内合法**（GridPanel/TableLayoutPanel 靠 Span 分配）；普通 Panel 内必重叠
- ⛔ **嵌套方向 = Panel 卡片在内、GridPanel 分区在 Panel 内**（2026-10-14 批K 修正）：正确链 `GridPanel(页级) → Panel(卡片) → GridPanel(区内控件)`；**禁止 GridPanel 套 GridPanel 再放 Panel**（`gridLaserLaZone` 单子网格已撤销，见 [[decisions/ADR-069-PanelInnerGridZoneCells]]）
- ⛔ 已删容器（`tabsQuickSetup` / `tabsLaserProcess` 及 7 个 `AntdUI.TabPage`）**不得再引用**
- ✅ 外层 `tabsProcess` 仍用 Tabs，**ADR-051 双写铁律继续适用**
- ✅ **代码后置 `.cs` 零改动**（嵌套容器在 `.cs` 中零引用，改动全在 Designer）

## 指令区 Radio 化与 TA 参数区（2026-10-12 ADR-063/080）

### 快捷设置页（只有指令，无参数）

| 区 | 控件 | 说明 |
|---|---|---|
| `panelQuickTa` | `radioQuickTaAuto/Break/Pose1/Pose2/Retract` | TA 5 项互斥指令。**2026-10-14 ADR-067 重排一行 + 增第 5 项**：`Auto(20,60,150×45)` / `Retract(176,60,130×45)`「TA_Retract 回缩」 / `Break(312,60,130×45)` / `Pose1(442,60,100×45)` / `Pose2(548,60,100×45)`。**2026-11-05**：第 5 项由 `TA_Recheck` 更名 `TA_Retract`，语义改力矩反向回缩 |
| `panelQuickLa` | `radioQuickLaAuto/Spot1/Spot2/Pose1/Pose2` | LA 5 项互斥指令，宽 118、右边缘 658 ≤ 666 |

- 事件：`CheckedChanged += new AntdUI.BoolEventHandler(handler)`，⛔ **不是** `EventHandler`
- 触发：**仅 `e.Value == true`**（从未选中变为选中）时执行；取消选中是别的 Radio 被选中，不重复触发
- 处理器：一组一个（`radioQuickTa_CheckedChanged` / `radioQuickLa_CheckedChanged`），按 `radio.Name` 分发
- 选中态：`ForeColor = Color.Black` + `Fill = #52C41A`；未选中：灰字 + 透明

### 激光工艺设置页（TA 区只有参数，无指令）

| 控件 | 性质 | 数据源 |
|---|---|---|
| `txtTaForce` + `lblTaForceUnit`(N) | 可编辑 | `WeldAlgorithmsConfig.TaForceN`（**力的大小、非负**；方向另存 `ROOT/TA_HOME/TA_TORQUE_DIRECTION`，ADR-084） |
| `txtTaBreakPos` + `lblTaBreakPosUnit`(mm) | **只读**（`ReadOnly = true`） | `LaserWeldHeadWorkflow.TaBreakHoldMm`（未触发显示 `--`） |
| `txtTaPose1` + `lblTaPose1Unit`(mm) | 可编辑 | `WeldAlgorithmsConfig.TaPose1Mm`（ADR-066 合入） |
| `txtTaPose2` + `lblTaPose2Unit`(mm) | 可编辑 | `WeldAlgorithmsConfig.TaPose2Mm`（ADR-066 合入） |
| `txtTaZeroPose` + `lblTaZeroPoseUnit`(mm) | 可编辑 | `WeldAlgorithmsConfig.TaZeroPoseMm`（工艺 INI `TA_ZERO_POSE_MM`，**2026-11-06 新增，TA 工作零位坐标的唯一可编辑源**） |
| `btnSaveTaParam` / `btnReadTaParam` | 按钮 | 保存/读取（ADR-066 后走 `WeldAlgorithmsConfig` 通道，`TAConfig.ini` 独立文件不再使用） |

**TA 工作零位坐标单一数据源（2026-11-06）**：`TA_ZeroPose` 目标坐标只在工艺设置页这一行编辑，
写法 / 校验 / 提交时机 / 静默保留旧值的非法值口径与 `TA_Pose1` / `TA_Pose2` **完全同构**（`ApplyTaToConfig`
统一解析，`BtnSaveLaserZone_Click` → `SaveAlgorithmsZone(Preset)` + `SaveAlgorithmsZone(System)` 落盘）。
系统设置 → TA 轴「参数」弹窗里原 `TA_HOME_ZERO_POSE_MM` 只读展示行**已整体删除**（连同「TA 工作零位」分区与
速度/容差两项，ADR-091）：`AxisConfigForm` 不再有 `ReadZeroPoseTargetMm()`，弹窗与本页零耦合。
旧键 `TA_HOME_ZERO_POSE_MM` 只在 `WeldParamManager.MigrateLegacyTaZeroPoseMm` 中做一次性迁移，之后不再读取；
`TA_HOME_ZERO_POSE_VEL` / `TA_HOME_ZERO_POSE_TOL_MM` 两键已从代码全链路移除（旧文件里存在也读出即忽略）。

⚠️ **TA_Break 无设定值**：停止位由 `TaBreak()` 成功时锁存轴反馈位置（`TaBreakHoldValid` 区分「未触发」与「锁存在 0 位」），只读展示、不落配置。

## 启用管理区与待补充区清理（2026-10-13 ADR-065）

### 启用管理区（快捷设置页 · 4 列网格）

`gridProcessDebug`（2026-10-14 批K 由 `tlpProcessDebug` TableLayoutPanel 改为 AntdUI.GridPanel；三轮现行 Span `40:fill;30:160 160 160 160;30:160 160;30:160 160 160 160;30:fill`，见「分区容器统一」节）：4 列 160 宽，**2026-10-15 [[decisions/ADR-070-GalvoWeaveAsWidthSource|ADR-070]] 起 6→5 个工艺开关**（光斑宽度跟随已并入振镜摆动，r2 仅 2 列），末行 Tip 占满：

| 开关 | 配置 | 处理器 |
|---|---|---|
| `swEnableSeamTrace` | `EnableSeamTrace` | `swEnableSeamTrace_CheckedChanged` |
| `swEnableGalvoWeaveQuick` | `EnableGalvoWeave` | `swEnableGalvoWeaveQuick_CheckedChanged`（与激光工艺页 `swEnableGalvoWeave` 双向同步）。**2026-10-15 标签改「振镜跟随摆动工艺」**——工艺启停开关：控制自适应过程中是否启用振镜跟随焊缝摆动（ADR-070 同键双视角文案） |
| `swEnableAdapt` | `EnableGuide` | `swEnableAdapt_CheckedChanged` |
| `swEnableMonotonic` | `EnableMonotonicConstraint` | `swEnableMonotonic_CheckedChanged`（⚠️ **2026-10-14 [[decisions/ADR-068-WeldAlgorithmsConfigZoneReorg|ADR-068]] 控件删除**——该开关唯一入口归系统设置页，本行仅为沿革留痕） |
| `swEnableWireAlign` | `EnableWireAlign` | `swEnableWireAlign_CheckedChanged` |
| `swEnableTempCtrl` | `EnableTempCtrl` | `swEnableTempCtrl_CheckedChanged` |
| ~~`swEnableSpotWidthFollow`~~ | ~~`EnableSpotWidthFollow`~~ | ⚠️ **2026-10-15 ADR-070 控件与配置项删除**（`decisions/ADR-070-GalvoWeaveAsWidthSource`）——与振镜摆动实为一个意思（光斑宽度不可调，真正变化的是振镜摆幅宽度形成光斑宽度变化），`SeamWidthSource` 派生改由 `EnableGalvoWeave` 决定；`RefreshSpotWidthByGain()` 重算并入振镜开关处理器。本行仅为沿革留痕 |

- ⛔ **即改即存**：每个开关都订阅 `CheckedChanged` 并调 `SaveProcessEnable()`（INI 落盘）；
  回填期用 `_loadingProcessEnable` 静默防误触发
- ⛔ **振镜摆动 = 振镜摆动门控 + 焊缝宽度来源开关**（ADR-070）：开 → `SeamWidthSource.Laser`（实测宽度驱动摆幅），关 → `Manual`（手动固定宽度）
- ⛔ **不建重复开关**：`swEnableAdapt` 即 `EnableGuide`；自适应工艺页的 `selFlowEnableGuide` 是既有第二入口
- 读写入口：`LoadProcessEnableOnForm()` / `SaveProcessEnable()` / `ReadProcessEnable()`

### Tracking 指令区（`panelQuickTracking`）

- `chkLockYCalib`（Y轴回标定位置）：从原快捷调试块**搬入**本区
- `lblQuickTracking`：区标题（静态 `Tracking Setting`；2026-11-13 去掉原名 `Tip` 后缀，⛔ 不再承载等待/不可用原因文案）
- 2026-10-14 批K：区内容由裸放改为 `gridQuickTracking`（Span `40:fill;fill`：标题行 + 内容行）

### 已删除（ADR-065）

| 控件 | 原因 |
|---|---|
| `panelWireAlign` + `lblWireAlignTip` | 「待补充」占位区整体删除，转 wiki 跟踪（范围已在 P1 §4.2 划定） |
| `chkLockSpotCalib` | 光斑回标定位**无此指令** |
| `chkLockWirePos` | 送丝结构锁定**即 TA_Pose**（TA 参数区已有 `TA_Pose1/Pose2`） |
| `lblQuickDebugTitle` / `lblQuickDebugTip` | 快捷调试块已拆分 |
| `btnSaveProcessDebug` / `btnReadProcessDebug` | 改为即改即存 |

⚠️ **配置项保留**：`LockYCalib` / `LockSpotCalib` / `LockWirePos` 仍在 `WeldAlgorithmsConfig`（删 UI 不删配置）。

## 分区容器统一（2026-10-14 批K，ADR-069）

快捷设置 4 区的**区内控件挂载形态**统一为「Panel 卡片 → GridPanel 分区」。
**三轮演进（2026-10-15 业主裁定，ADR-069 §三）**：区内 GridPanel 一律 **标题行高 40、控件行高 30、每行最多四列、每控件格宽 160**（标题/Tip 行整行 `fill` 单列例外；行数按需增加）：

| 分区 Panel | 区内 GridPanel | Span（现行 40/30 + 160） | 结构 |
|---|---|---|---|
| `panelProcessDebug` | `gridProcessDebug` | `40:fill;30:160 160 160 160;30:160 160;30:160 160 160 160;30:fill` | 5 开关：r1 四列 / r2 两列 / r3 四列 / Tip 整行 |
| `panelQuickTa` | `gridQuickTa` | `40:fill;30:160 160 160 160;30:160;30:fill` | 5 Radio 拆 4+1 |
| `panelQuickLa` | `gridQuickLa` | `40:fill;30:160 160 160 160;30:160;30:fill` | 同上 |
| `panelQuickTracking` | `gridQuickTracking` | `40:fill;30:160` | 标题 + 单内容行 |

> ~~60/40 行高（2026-10-14 二轮）~~ ⚠️ 已被 2026-10-15 三轮演进废止（历史 Span 见 ADR-069 §三删除线）。

- ⛔ **`SetColumnSpan` 无 GridPanel 等价**（`_N` 不可用）⇒ 标题/Tip 行改用**整行 `fill` 单列**表达
- ✅ 事件订阅、控件名、`.cs` 代码后置**零改动**（纯 Designer 容器替换）

### 振镜块迁位（二轮，ADR-069 §四）

- 「振镜（功能与图形）」控件 **自 `panelLaserLa` 迁出**，迁入新卡片 `panelLaserGalvo`（`gridLaserZones` 原空白第 4 格）→ 区内 `gridLaserGalvo`
  - 初版 10 控件：`lblGalvoTitle` + 6 按钮（Circle/Eight/Line/Arc/Demo/Home）+ `swEnableGalvoWeave` + `lblGalvoWeave` + ~~`lblGalvoState`~~（**2026-10-15 业主 VS 删除**——图形状态由按钮选中态与 `RefreshActionStates` 承担，`.cs` 刷新行同步移除，现 9 控件）
- LA 参数区只剩 LA 参数 6 行 + 保存/读取按钮，拥挤解除
- `gridLaserZones` 4 格满挂（原「声明 4 格只挂 3 控件」条款对本页失效）

### 振镜卡行序与文案（2026-10-15 三轮，ADR-069 §三 + ADR-070 补）

`gridLaserGalvo` Span `40:fill;30:160 160 160 160;30:160 160;30:160 160;30:160 160`，行序（上→下）：

| 行 | 内容 | 说明 |
|---|---|---|
| r0 标题 40 | `lblGalvoTitle`「振镜（功能与图形）」 | 整行 fill |
| r1 控件 30 | 圆 / 八字 / 直线 / 圆弧（4 图形按钮，四列） | |
| r2 控件 30 | 手动演示 / 回到零位（两格 160，右侧留空） | |
| r3 控件 30 | 手动焊缝宽度(mm) 标签 + 输入（160 160，右侧留空） | ADR-070 ⛔ **2026-11-18 已删**（改由 GA 档宽度承担） |
| r4 控件 30 | **开启摆动/停止摆动 + 开关（最后一行）** | 业主裁定：开关移至最后一行 |

- **文案修正**：`lblGalvoWeave`「振镜摆动启用」→ **「开启摆动/停止摆动」**（运动控制开关，直接启停摆动）；快捷区 `lblEnableGalvoWeaveQuick`「振镜摆动」→ **「振镜跟随摆动工艺」**（工艺启停：自适应过程中是否启用振镜跟随焊缝摆动）；两控件同绑 `EnableGalvoWeave`，文案为同一开关的两个操作视角
- `lblProcessEnableTip` 补「振镜跟随摆动工艺控制自适应过程中是否启用振镜跟随焊缝摆动」

### 手动焊缝宽度入振镜卡（2026-10-15 ADR-070）· ⛔ 2026-11-18 已废

> 本小节为**历史演进记录**。2026-11-18 业主裁定：手动宽度「完全不需要，外面 GA 设置也有一个」⇒
> `ManualSeamWidthMm` 配置项、GA 卡 `txtManualWidth`/`lblManualWidth`、轨迹点区 `txtParamManualWidth` **全部删除**，
> Manual 源的恒定宽度改取 **GA 档宽度**（见文末「GA 按图形分档 + 手动/自动两套模式」节与 [[decisions/ADR-076-SettingsZoneSaveWiring]] 决策 D5）。

- 新增 `lblManualWidth`（「手动焊缝宽度(mm)」）+ `txtManualWidth`（`AntdUI.Input`），挂 `gridLaserGalvo` 第 4 行（`30:160 160`，见上方行序表；首轮为 `40:165 120`，三轮改 160/30）
- **失焦即存**：`txtManualWidth_Leave` → 正数校验（≤0/解析失败**还原原值** + warn）→ 写 `ManualSeamWidthMm` → `SaveAlgorithmsZone(Adapt)` → Manual 源且有当前参数时 `RefreshSpotWidthByGain()`
- 回填：`LoadGalvoActionUi()` 一并回填 `cfg.ManualSeamWidthMm`
- **双入口同源**：与系统设置页 `txtParamManualWidth` 读写同一配置项 `ManualSeamWidthMm`，两页互不联动（后操作者生效，INI 为单一真相源）
- 语义边界：手动宽度只在**振镜摆动关闭**（Manual 源）时作为查表输入生效；振镜摆动开启时宽度由实测焊缝宽度驱动摆幅

## U-4 线激光十项归位 + 批M 容器统一（2026-10-15 ADR-071）

### `tbpanelweldponts` → `gridWeldPonts`（跟踪工艺设置区，7 行满额）

- **容器**：TableLayoutPanel 6×6 → `AntdUI.GridPanel`，Span `40:fill;30:160×4;30:160×4;30:160×4;30:160×4;30:160×4;30:160 160`
- **十项清单**（U-4 满额）：

| 行 | 控件 |
|---|---|
| r0 | 标题「跟踪工艺设置(Tracking Settings)」 |
| r1 | 轴/激光比例系数、偏差方向 |
| r2 | 激光超前量(mm)、机器人Y补偿系数 |
| r3 | Y轴行程下限/上限(mm) |
| r4 | **示教Y轴锁定坐标(mm)**（迁入）+ 焊缝地图点数上限 |
| r5 | **标定中心点Y(mm)** + **标定中心点Z(mm)**（迁入） |
| r6 | **读取**（`btnReadWeldPonts`）+ **保存**（`btnSaveWeldPonts`）——新增，闭环保存入口 |

- **读写链**：`LoadLaserCalibOnForm`（10 项回填，构造经 `LoadAlgoConfigOnForm` 调用）· `BtnSaveLaserCalib_Click`（写回 + **双区落盘** `AlgorithmsZone.Preset`（几何 7 项）+ `AlgorithmsZone.System`（标定 3 项））· `BtnReadWeldPonts_Click`（全量重载回填）
- **迁出方**：`SystemControlPage` `gridLaserCalib` 只留线激光角度 + 读取/保存（System 区）+ 超时组；`.cs` 残留 0

### `tbPanelAdaparam` → `gridAdaparam`（自适应工艺参数页，批M U-3）

- 6×19, 45 子 → 18 行（5 分区标题 `40:fill`）：焊接工艺库操作 / 焊丝工艺参数 / 基准工艺参数 / 焊参调整（WeldParamAdjustment）；Span `40:fill;40:fill;30:160×4;40:fill;…`
- 控件与读写链零改动（纯容器转换）
- ⚠️ **2026-10-16 三轮演进（业主）**：「焊接工艺库操作」分区整体删除（标题行 `lblWeldListTitle` + `uiSymbolLabel12` + `mAutoParamName`「当前配置名」+ 按钮 `btnAddNewConfig` + `btnShowConfigList` 共 5 控件，实例化/挂载/字段/订阅/属性块全清）⇒ Span 由 resx 载体改**字面量**并 18→**16 行**（`40:fill;40:fill;30:160 160 160 160;30:160 160 160 160;30:160 160;40:fill;30:160 160;30:160 160 160 160;30:160 160 160 160;30:160 160;30:160 160 160 160;30:160 160;40:fill;30:160 160;30:160 160 160 160;30:160 160`）

## 自适应页左右分栏（2026-10-15 ADR-072「类数据回溯界面」）

```
tabPageAdaptiveSetup → panelWeldList → gridWeldZones(Span "20% 80%" ← 2026-10-16 四轮复正：三轮误写 `20%:fill;fill`（: 前=行高⇒变上下），左右两列正确写法=无冒号单段，先例 WinForms-Designer §2.5 `Span="40% 60%"`)
    ├ 左: panelConfigList(卡片) → gridConfigList("40:fill;fill;30:80 80")
    │      r0 lblConfigListTitle「工艺参数列表」 / r1 tableConfigList(AntdUI.Table) / r2 btnConfigAddNew·btnConfigDelete
    └ 右: panelAdaparam(卡片) → gridAdaparam(16 行，「焊接工艺库操作」区已删)
```

- **表格两铁律后置**：`InitConfigListColumns()`（Columns=ColumnCollection No+配置名、AutoSizeColumnsMode=Fill、`Binding(AntList<ConfigListRow>)`、`CellClick` 订阅）在构造函数 `InitializeComponent()` 之后调用——Designer 内禁止 Columns 赋值；`CellClick` 后置（项目 5 先例均后置）
- **按钮与选择入口（2026-10-23 演进）**：底部两按钮 = 新建（复用 `btnAddNewConfig_Click`）+ 删除（ConfigForm 同款三重保护：默认配置禁删 / Modal 确认 / 在用配置禁删 → `WeldParamManager.DeleteConfig`）；**选择/切换改由表格右键菜单**（`SelectConfig`「选择/切换」→ `ConfigSelect_Click` → `SwitchConfig` + `LoadParamOnForm`），原底部 `btnConfigSelect` 已删除；刷新点=构造 / `ParamAutoPage_Shown` / 增删选后（`LoadConfigList`）
- 数据源 `ConfigHelper.GetAllConfigs()`（「标识」列）；行模型 `ConfigListRow{No,Id}`
- **⚠️ 2026-10-16 三轮演进（业主按钮合并）**——原右区「焊接工艺库操作」职责全部并入左三按钮：
  - 右 `btnAddNewConfig`「新增配置」= 左 `btnConfigAddNew` → 删右保左（`btnConfigAddNew_Click` 内仍调用 `btnAddNewConfig_Click` 处理器，处理器**不删**）；`mAutoParamName.Text` 回填行同步删
  - 右 `btnShowConfigList`「查看历史参数」不再需要 → 控件删 + `btnShowConfigList_Click` 处理器**整体删除**
  - 左 `btnConfigDelete` = 原查看历史参数对话框内的删除功能（三重保护原已一致，零改动）
  - 右侧标题行 `lblWeldListTitle`「焊接工艺库操作」+ `uiSymbolLabel12` + `mAutoParamName`「当前配置名」删
- **⚠️ 2026-10-16 四轮演进（业主四项，ADR-072）**：
  1. 分栏复正：`gridWeldZones.Span` `"20%:fill;fill"`（行高语义⇒上下）→ **`"20% 80%"`**（单行两列左20/右80）
  2. **LA/TA Settings 区内 Grid 化**：`panelLaserLa`/`panelLaserTa` 子控件原绝对定位直挂（链缺区内 Grid）⇒ 新建 `gridLaserLa`（4 行 13 子：`40:fill;30:160×4;30:160×4;30:160×4`）/ `gridLaserTa`（7 行 16 子：`40:fill;30:160×3;30:160×3;30:160×3;30:160×3;30:fill;30:160 160`），四件套+子 Dock=Fill，卡片仅挂 grid，Add 序=视觉序反转
  3. **孤儿控件可见化（临时，待业主裁决）**：① `uiContextMenuStrip1`(含右键「删除」项，原 `ContextMenuStrip` 属性从未赋值=死菜单) → `tableConfigList.ContextMenuStrip`（左列表右键删除激活）；② `lblEnableGalvoWeave`（空文本无框不可见）→ 挂 `panelProcessDebug` 右上 + FixedSingle 边框 + Text「漏挂控件」

- **⚠️ 2026-10-23 演进（业主）**：① 表格右键由「删除」改为「选择/切换」（`DeleteConfig`→`SelectConfig`，`ConfigSelect_Click`；`uiContextMenuStrip1.Opening` 时按 `tableConfigList.SelectedIndex` 同步目标行）；② 底部三按钮改为两按钮（新建/删除），`btnConfigSelect` 实例化/挂载/字段/属性块/处理器全删，`gridConfigList.Span` 末行 `30:80 80`

## LA 参数区与 TA_Retract（2026-10-14 ADR-067，2026-11-05 更名）

> 详见 [[decisions/ADR-067-LATaSettingsSemanticRework|ADR-067]]；指令语义实现在 [[api/LaserWeldHeadWorkflow]]。

### 三区改名（仅 Designer 文本）

| 控件 | 新文本 |
|---|---|
| `lblGeoSecTitle` | 跟踪工艺设置(Tracking Settings) |
| `lblLaserLaTitle` | 对焦工艺设置(LA Settings) |
| `lblLaserTaTitle` | 送丝下压工艺设置(TA Settings) |

### LA 区形态重构：动作按钮组 → 参数设置区（与 TA 同形态）

- **删 7 控件**：`btnLaAuto` / `btnLaSpot1` / `btnLaSpot2` / `btnLaPose1` / `btnLaPose2` / `lblLaState` / `btnApplySpotTarget`（实例化 + Controls.Add + 属性块 + Click 订阅 + 字段声明全删）。
- **新 10 控件**（照 ADR-066 TA 参数区范式）：

| 控件 | 位置/尺寸 | 绑定 |
|---|---|---|
| `lblLaSpot1`(20,57) + `txtLaSpot1`(195,50,110×29) | 「LA Spot1 光斑(mm)」 | `WeldAlgorithmsConfig.LaSpot1Mm` |
| `lblLaSpot2`(330,57) + `txtLaSpot2`(505,50) | 同行右列 | `LaSpot2Mm` |
| `lblLaPose1`(20,102) + `txtLaPose1`(195,95) | 「LA Pose1 位(mm)」 | `LaPose1Mm` |
| `lblLaPose2`(330,102) + `txtLaPose2`(505,95) | 同行右列 | `LaPose2Mm`（**2026-11-18 改名** `lblLaDefaultFocus` / `txtLaDefaultFocus` / `LaDefaultFocusMm`，见文末节） |
| `lblSpotTarget`(20,147) + `txtLaSpotTarget`(215,140) | 「目标光斑(mm)·auto用」 | `LaSpotTargetMm` |

> ⚠️ 2026-10-19 起 `btnSaveLaParam`/`btnReadLaParam`/`btnApplyLaParam`（及 TA 三键、Tracking 三键）**已删除**，统一收口到 flowPanel2 三按钮，见下节。

- `panelLaserLa.Size` (660,157) → **(660,360)**；振镜块整体上移（lblGalvoTitle y=195、6 个 btnGalvo y=235、swEnableGalvoWeave/lblGalvoWeave y=295、lblGalvoState y=340）。
- **快捷 Radio 指令链 `radioQuickLa*` 5 项保留不变**（指令与参数分离，ADR-063 语义延续）。

### 参数读写（`.cs`）

- 新增 `LoadLaParamUi` / `BtnSaveLaParam_Click` / `BtnReadLaParam_Click`：Spot1/Spot2/Target 必须 **>0** 校验、Pose1/2 解析失败保旧值、`SaveAlgorithmsZone(AlgorithmsZone.Preset)` 分区落盘（ADR-068 接口）。
- `LoadGalvoActionUi` 移除 `txtLaSpotTarget` 回填（归属移交 LA 参数区）；`LoadAlgoConfigOnForm` 增 `LoadLaParamUi()`；删 5 个 `btnLa*_Click` + `btnApplySpotTarget_Click`。
- **业主裁定**：LA_Spot 与 LA_Pose 都会退出 LA_Auto；「应用目标光斑」按钮并入保存按钮。

### TA_Retract（快捷 Radio 第 5 项，原 TA_Recheck）

- Designer：`radioQuickTaRetract`(176,60,130×45)「`TA_Retract`」，`AntdUI.BoolEventHandler` 订阅 `radioQuickTa_CheckedChanged`；原 4 Radio 重排一行（见上表）。
- `.cs`：`DoTaRetract()` + `case "radioQuickTaRetract"`。~~`RefreshActionStates` 加 `radioQuickTaRetract.Enabled = taReady`~~ → **2026-11-10 起 TA 六项统一不置灰**（就绪判定归执行段，见下文「2026-11-10 TA 指令区去禁用」）。
- Tooltip：`TA_Retract：力矩反向出力（与 TA_Auto 方向相反），保持出力不定位`；确认弹窗「力矩反向出力（与 TA_Auto 方向相反，保持出力不定位）」。
- 工作流：`MotionControlWorkflow.TaTorque(TaTorqueCommand.Retract)`——**`TA_Auto` 方向取反的纯力矩输出**（切 CST → 开输出 → 保持出力返回）；
  ⛔ 不是 `TaMoveTo(0.0)` 的 CSP 绝对定位，也⛔ 无位置终点、⛔ 不撤力、⛔ 不回 CSP、⛔ 不 `AbsMove` 锁位。口径见 [[api/MotionControlWorkflow]]「TA_Retract（回缩）」与 ADR-082 D24~D29。

## 配置分区归位（2026-10-14 ADR-068）

- 本页 `swEnableMonotonic`（`EnableMonotonicConstraint`）控件删除——**唯一入口归系统设置页**（同 ADR-065 的 `EnableGuide` 反向收敛：`EnableGuide` 唯一入口保留在本页快捷设置区）。
- 本页所有工艺设置保存按钮改走 `SaveAlgorithmsZone(AlgorithmsZone)` 分区落盘（新增接口，总入口签名不变净行为不变）；配置代码块按 UI 4 分区重排详见 [[decisions/ADR-068-WeldAlgorithmsConfigZoneReorg|ADR-068]] 与 [[modules/WeldParamControl]]。

## 三按钮统一收口（2026-10-19）

### flowPanel2（激光工艺设置区，9 → 3）

原 Tracking/LA/TA 三子区各带读取/修改/保存共 9 按钮收敛为 **flowPanel2 单行 3 按钮**（Align=RightCenter，顺序固定 读取→修改→保存）：

| 按钮 | Text | Click handler | 语义 |
|---|---|---|---|
| `btnReadWeldPonts` | 读取参数 | `BtnReadLaserZone_Click` | 文件→UI：`LoadAlgorithmsConfig` + `LoadLaserCalibOnForm` + `LoadLaParamUi` + `LoadTaParamUi` |
| `btnApplyLaserCalib` | 修改参数 | `BtnModifyLaserZone_Click` | **UI→内存（不落盘）**：`ApplyTaToConfig`（force 校验）→ `ApplyLaToConfig`（Spot/Target>0 校验）→ `ApplyTrackingGeomToConfig` |
| `btnSaveWeldPonts` | 保存参数 | `BtnSaveLaserZone_Click` | UI→内存→文件：三 Apply + `SaveAlgorithmsZone(Preset)` + `SaveAlgorithmsZone(System)` 双区落盘 + 回读 `LoadLaParamUi`/`LoadTaParamUi` |

- **删除** 6 按钮（`btnRead/Save/ApplyLaParam`、`btnRead/Save/ApplyTaParam`，四形态：实例化/属性块/Controls.Add/字段）+ 旧 9 handler；`Apply*ToConfig`/`Load*Ui` 底座函数保留复用（校验失败返回 false 中止整个链条）。
- **三按钮语义基准** = 系统设置页轨迹跟踪设置 flowPanel1（[[api/SystemControlPage]] button1/2/3）：读取=文件→UI、修改=UI→内存、保存=UI→内存→文件。

### flowPanel1（自适应调整算法区）修正基准/修改参数分离（2026-10-20 演进）

> ⚠️ 2026-10-19 记的「`btnCorAutoParam_Click` 改纯内存 `CollectParamFromForm()+RefreshParam()`」已被 **2026-10-20 业主裁定推翻**——当日把「修正基准」按钮改名「修改参数」属两语义混同，现恢复分离。

| 按钮 | Text | handler | 语义 |
|---|---|---|---|
| `btnCorBaseline`（新增，`gridAdaparam` 中 `btnShowAutoParam` 旁；Span 行 12 扩 `30:160 160 160`，Controls 逆序插入于 `lblWeldAdjTitle` 与 `btnShowAutoParam` 之间） | 修正基准 | `btnCorBaseline_Click` | **采集→落 DB→按公式重算**：`CollectParamFromForm()` + `SaveCurrentAutoParam()` + `RefreshParam()`（原 `btnCorAutoParam` 三连逐语句恢复，backup 取证），重算工艺库的独立危险职责 |
| `btnCorAutoParam`（flowPanel1 中键，原修正基准按钮位） | 修改参数 | `btnCorAutoParam_Click` | **仅底部 INI 区 UI→内存（不落盘、不采集上部基准）**：流程开关 3 项（`MaxConsecutiveFailures`/`IsCountType`/`CountNum`）+ 工艺输出 3 项（`ManualSeamWidthMm`/`SpotWidthGain`/`ParamOutputHz`），提示「点保存焊参调整落盘」 |

- **分界依据**：上部「基准工艺参数/焊丝工艺参数」为 DB+公式派生（`ReloadCurrentParamValues` 从 DB 回读并重建分段表），其唯一改动入口 = 修正基准；底部焊参调整区落盘由 `btnSaveAutoParam`（保存焊参调整，UI→内存→文件）承担。
- `SaveCurrentAutoParam` 合法调用方变更为 3 个：`BtnSaveAutoParam_Click`、`btnCorBaseline_Click`、`FilebackupPage`。

## 2026-10-23 指令区与振镜工艺重排

| 项 | 现行实现 |
|---|---|
| Tracking 指令 | `gridQuickTracking` 三项 Radio：`Y_AutoTracking`（默认，清 `LockYCalib`、Y 轴跟随线激光）/ `Y_ForceCalibPose`（移到 `TeachLockYMm` 并置 `LockYCalib`）/ `Y_ForceHome`（`MontionManager.HomeAxis` 强制回零）；原 `chkLockYCalib` 删除 |
| 指令文本 | 三个指令区 Radio 一律 `XXX_XXX` 短文本（`Y_*` / `LA_*` / `TA_*`），中文释义全部放 `TooltipComponent` 悬停提示 |
| LA 图形组 | `LA_GalvoCircle/Eight/Line/Arc` 与 `LA_Auto/Spot1/Spot2/Pose1/Pose2` **分属两个独立容器**（`gridQuickLa` / `tlPLASetting`）：组内互斥、跨组独立（可同时各选一个）；`_syncingLaRadios` 已随图形 Select 删除而移除（2026-11-18），Radio 同父容器自动互斥 + `_loadingGalvoUi` 单标志即可覆盖回填抑制 |
| 振镜工艺设置 | 原 4 个图形按钮删除 → `selGalvoPattern`（4 项 Select，与 `LA_Galvo*` 图形 Radio 双向同步）→ **2026-11-18 随 GA 设置区控件整体删除**（见文末节）；`txtGalvoWidth/txtGalvoLength/txtGalvoFreq`（自系统设置页迁入）保留；`swEnableGalvoWeave` 与 `lblGalvoWeave` 删除（硬件使能归系统设置 ~~`swGalvoEnable`~~ **`btnOptGalvoEnable`（2026-10-26 由 Switch 改按钮，见 [[decisions/ADR-075-LaserHeadUiControlConsistency]]）**，工艺摆动入口保留快捷区 `swEnableGalvoWeaveQuick`） |
| 地图上限 | `焊缝地图点数上限`（`MaxMapPoints`）自本页 `gridWeldPonts` 迁至系统设置页 `gridFitterControl` 的「线激光点过滤」区 |

> 读改存：`BtnReadLaserZone_Click` 增 `LoadGalvoActionUi()`；`BtnModifyLaserZone_Click` / `BtnSaveLaserZone_Click` 增 `ApplyGalvoParamsToHead()`（宽/长/频/图形 → `WeldHeadConfig.DefaultGalvo`），保存时 `SaveWeldHeadConfig()` + `SetGalvoParams()` 下发设备。

## 2026-10-23 参数读存与分区落盘接线修正（ADR-076）

> 本轮为**盘查 ⇒ 修复**：读/改/存按钮响应、后端配置分区落盘、同一参数多入口三类问题。

| 缺陷 | 现象 | 修正 |
|---|---|---|
| **⑤工艺输出三项不落盘** | `BtnSaveAutoParam_Click` 弹「已保存」，重启后 `ManualSeamWidthMm`/`SpotWidthGain`/`ParamOutputHz` 回旧值 | 三项按 ADR-068 归 **③Adapt 区**，但代码**在 Adapt 落盘之后**才赋值，且随后调的是 `SaveAlgorithmsZone(System)`（不含这三个键）⇒ 改为：先赋值 → 再落 **Adapt** 区 |
| **跨页副作用** | 系统设置页「仅修改未保存」的参数被本页「保存焊参调整」顺带写盘 | 「保存焊参调整」**不再落 ①System 区**（本按钮不写前馈安全/单调锁，该两项归系统设置页） |
| **振镜图形全量保存污染** | 选一次图形连带重写 XML + 全部 INI 段 | 新增唯一入口 `SaveGalvoPattern()` → 落 **④Preset 区**；`SetGalvoPattern` 与 `selGalvoPattern_SelectedIndexChanged` 共用（**2026-11-18**：后者随 Select 删除而移除，现仅 `SetGalvoPattern` 一处） |
| **Y 指令全量保存污染** | 选一次 Y 指令连带重写全部配置 | `radioQuickY_CheckedChanged` 三处改落 **②Quick 区**（`LockYCalib` 归属） |
| **「读取参数」名不副实** | 振镜宽/长/频取的是内存旧值（`MontionManager` 初始化时只读过一次文件） | `BtnReadLaserZone_Click` 先调 `MontionManager.Instance.LoadWeldHeadConfig()`；并补 `LoadFlowSwitchOnForm()` + `LoadParamOutOnForm()` 两区回填 |
| **重复接线** | 「修改参数」与「保存焊参调整」各写一遍同一批 6 项 | 收口为 `ApplyAdaptUiToMemory()`（UI→内存，不落盘），两按钮共用 |
| **解析口径不一** | 同页 `ParseCalibDouble` 用当前文化、`TryReadDouble` 用不变文化 | 两页统一为 **InvariantCulture 优先 → 当前文化回落 → 失败保留原值** |

**修正后的三按钮语义（不变）**

| 按钮 | 语义 | 落盘分区 |
|---|---|---|
| 读取参数（`BtnReadLaserZone_Click`） | 文件 → UI（算法配置 + 焊接头配置双重重载，五区回填） | 不落盘 |
| 修改参数（`BtnModifyLaserZone_Click`） | UI → 内存（TA / LA / 振镜 / Tracking 几何，含校验） | 不落盘 |
| 保存参数（`BtnSaveLaserZone_Click`） | UI → 内存 → 文件 | ④Preset + ①System（双区） |

**修正后的「保存焊参调整 / 修改参数」**

| 按钮 | 语义 | 落盘分区 |
|---|---|---|
| 修改参数（`btnCorAutoParam_Click`） | UI → 内存（焊参调整 3 项 + ⑤工艺输出 3 项） | 不落盘 |
| 保存焊参调整（`BtnSaveAutoParam_Click`） | 采集 AutoParam 标量落 DB + UI → 内存 → 文件 | **③Adapt**（不再落 ①System） |

> ⚠️ **仍待业主裁决**：振镜宽/长/频三项写入的协议字段（`galvo.Width`/`Length`/`Frequency`）与生产链路同源 —— `LaserWeldHeadWorkflow.ApplyGalvoAmplitude` 每拍写 `Width=Length=amplitude`、`Frequency=查表频率` ⇒ **三项运行期被覆盖，界面改了不生效**；落盘值 `GALVO/WIDTH|LENGTH|FREQUENCY` 亦为死值。详见 [[decisions/ADR-076-SettingsZoneSaveWiring]] 与 [[lessons/ConfigZoneSaveWiring]]。

## 2026-11-02 演进：工艺启用文案 · 指令区默认 Auto 与连机同步

| 项 | 结论 | 约束 |
|---|---|---|
| 工艺启用 Switch 文案 | 区域首个 Switch `swEnableSeamTrace` 的范式 = **Switch 自带 `CheckedText="启用"` / `UnCheckedText="未启用"`**（非旁挂 label）；按同范式补齐 `swEnableTempCtrl` / `swEnableWireAlign` / `swEnableGalvoWeaveQuick`，`swEnableAdapt` 原已有同款文案 | 文案随 `Checked` 自动切换，⛔ 不在代码里另赋 `Text`；状态回填仍只走唯一入口 `LoadProcessEnableOnForm()`（`_loadingProcessEnable` 抑制） |
| 三区默认 Auto | 构造期 `ApplyDefaultCommandModes()` 统一把 `radioQuickYAuto` / `radioQuickLaAuto` / `radioQuickTaAuto` 置选中（LA 对焦组与振镜组已在独立容器内，二者可同时选中，振镜默认项由 `LoadGalvoActionUi()` 落定）；`LockYCalib` 运行期内存置 false（不落盘） | 抑制标志 `_loadingProcessEnable` 包住，避免加载即下发运动指令；TA / LA 处理器入口补 `_loadingProcessEnable` 守卫 |
| 连机实时同步 | 订阅 `MotionControlWorkflow.Instance.StateSwitched`、`DeviceControlWork.Instance.InitializationCompleted`、`MontionManager.Instance.TaTorqueModeChanged`（`HandleDestroyed` 全部退订），回调经 `InvokeRequired` / `BeginInvoke` 转 UI 线程后统一调 `RefreshActionStates()` | 判据只读 `MontionManager.Instance`：LA = `IsInitialized && WeldHead != null`；Y = `IsInitialized && GetAxisByKeys(SeamTrackYKeys) != null`；TA = `IsInitialized && GetAxisByKeys(TaAxisKeys) != null`（2026-11-03 起与力矩位同一解析路径）；⛔ 禁另造连接判据 |
| 禁用语义 | 只改 `Enabled`，⛔ 不改 `Checked` —— 禁用期间已选中项保持原值 | 恢复连接后由同一 `RefreshActionStates()` 放开 |

> ⚠️ 关联：[[decisions/ADR-063-CommandZoneRadioExclusivity]]「演进（2026-11-02）」。

## 2026-11-02 补充演进：TA_Auto 力矩门控 · LA 双组容器分离

| 项 | 结论 | 约束 |
|---|---|---|
| TA_Auto 可用性 | ~~`taTorqueMode = taReady && manager.TaTorqueModeEnabled`~~ **2026-11-05 废止（ADR-082）**；~~`radioQuickTaAuto.Enabled = taReady`~~ **2026-11-10 废止**：TA 六项均不再置灰，就绪判定归执行段（ADR-082 D30） | 界面不设状态标签（2026-11-13 删除）；被拒原因由执行段 `CheckTaAvailable` / `CheckTaMotionReady` 给日志 + 失败红底 |
| TA_Auto 拦截 | ~~`DoTaAuto()` 先读 `TaTorqueModeEnabled`~~ **2026-11-05 删除**：`DoTaAuto()` 直接调 `TaTorque(TaTorqueCommand.Auto)` 再 `RefreshActionStates()`，无前置拦截 | 模式切换由合并入口自身完成 |
| LA 互斥根因 | **AntdUI/WinForms 同父容器天然互斥**：9 个 LA Radio 此前全部 `Controls.Add` 到 `gridQuickLa` ⇒ 整区被当成一组，选振镜会取消对焦 | 不是手工 `foreach` 强制取消；`RestoreLa*` 只是事后补救（已删除） |
| LA 分离方案 | `gridQuickLa.Span` 改为 `"40:fill;60:fill;30:fill;30:fill"`（标题/对焦组/振镜组/提示），新增 `gridQuickLaFocus`（5 对焦 Radio，`Span="30:160 160 160 160;30:160"`）与 `gridQuickLaGalvo`（4 振镜 Radio，`Span="30:160 160 160 160"`）；外层按逆序入格挂 4 控件 | 组内互斥由容器天然成立；跨组可同时选中「一个对焦模式 + 一个振镜模式」；保留 Select↔Radio 双向同步、默认态、连机禁用只改 `Enabled` |
| 底层双维度 | 工作流**本就没有「LA 单一当前模式」字段**：对焦侧 `LaAuto/LaSpot/LaPose` 操作 LA 轴 + `_laFollowActive`，振镜侧 `GalvoDemo/GalvoHome` 只操作焊接头从站参数 ⇒ 天然两维度并存，无需改指令解析 | 唯一交集 = `LoadConfig()` 的 `EnableGalvoWeave` / `GalvoPattern` 工艺开关，属生产链路，不受本次 UI 分组影响 |

> ⚠️ 关联：[[decisions/ADR-063-CommandZoneRadioExclusivity]] §五（LA 分组 vs TA 整区互斥）。

## 2026-11-03 修复：启动后 TA_Auto 置灰 / 未选中

> 业主报告「送丝力矩轴已确认连接上，但进入程序后 TA_Auto 不可用」。证据链与结论：

| 判据（`RefreshActionStates`） | 本机实际值 | 判定位置 |
|---|---|---|
| `manager.IsInitialized` | 构造函数 / `Load` 时 **false**（初始化线程尚未跑完）；`StateSwitched` 连机后 true | `MontionManager.Initialization` → `ProcessControlPage.RefreshActionStates` |
| `MoveData.MotionConfig.TaAxisName` | `送丝力矩电机`（默认值，XML 无 `<TA>` 段） | `DeltaMotionConfig.TaAxisName` |
| TA 轴对象存在 | 探针：`GetAxis(送丝力矩电机)` 命中，`Enabled=True` | 真实 `DeltaMotionConfig.xml` |
| `TaTorqueModeEnabled` | ~~探针：`Torque=True`~~ **2026-11-05 删除（ADR-082）**：不再作为判据 | `MontionManager.TaAvailable` |

**结论**：送丝力矩轴 **就是** TA 轴（`TaAxisKeys` 含「力矩」→ 同一根 `送丝力矩电机`）；置灰/未选中根因是
**首填时序**——构造期与 `Load` 均早于初始化，`!taTorqueReady` 把 `radioQuickTaAuto.Checked` 清掉；
运控连上后 `Enabled` 虽放开，Auto 仍处未选中（灰），且页面此前没有「初始化完成」首填入口。

| 修正 | 实现 | 判据 |
|---|---|---|
| 未就绪不清选中 | ~~清残留条件改为 `taReady && !taTorqueMode && Checked`~~ **2026-11-05 起**：只按 `taReady` 置灰，不再清选中 | 初始化完成后 `InitializationCompleted` 首填 → `Enabled=true` 且 Auto 仍选中 |
| TA 就绪判据统一 | `taReady = manager.TaAvailable`（单一真相源，见 [[api/MontionManager]]） | 与 `LaserWeldHeadWorkflow.CheckTaAvailable` 同一口径 |
| 初始化首填 | 构造订阅 `DeviceControlWork.Instance.InitializationCompleted`（`HandleDestroyed` 退订）→ `RefreshActionStates()` | 不再依赖「用户操作 / 状态事件」 |
| 模式变更跨页同步 | ~~`TaTorqueModeChanged` 订阅回填~~ **2026-11-05 删除（ADR-082）**：不再有模式事件；置灰只随 `TaAvailable` 变化 | Break/Pose/Retract 退出力矩后 Auto 仍可用 |
| 原因提示 | `UpdateTaAutoGateHint(bool taReady, string degradedReason)` 两态：可用 → tip「进入时自动切 CST，无需先开力矩模式」；不可用 → tip 带 `TaDegradedReason`，门状态变化 `ShowLog("工艺设置", ...)` | 不再出现「因已退出力矩模式不可用」 |
| 安全门 | `IsInitialized=false` 或 TA 轴对象缺失 → 仍置灰（`UpdateTaAutoGateHint` gate=0） | ⛔ 不放宽未连接/无轴门 |

## 2026-11-04 修复：TA 工艺参数首开不显示（组合入口漏分组 + 幂等补载）

| 项 | 结论 |
|---|---|
| 现象 | 启动后进入工艺设置页，TA 参数区（`txtTaForce` / `txtTaBreakPos` / `txtTaPose1` / `txtTaPose2`）为空或 0，点「读取参数」才出现正确值 |
| 根因 | 组合加载入口 `LoadAlgoConfigOnForm()` 只调 `LoadLaserCalibOnForm` / `LoadFlowSwitchOnForm` / `LoadParamOutOnForm` / `LoadGalvoActionUi` / `LoadLaParamUi`，**独缺 `LoadTaParamUi()`** ⇒ TA 区在构造与页面显示两条路径上从未回填 |
| 数据源 | `WeldParamManager.Instance.AlgorithmsConfig`（`WeldParamManager` 构造期即 `LoadAlgorithmsConfig()`，先于页面构造；配置未就绪时由补载守卫再兜一次） |
| 修复 | ① 组合入口补 `LoadTaParamUi()`；② 新增 `EnsureTaParamFilled()`（`_taParamFilled` 一次性守卫），构造函数末尾与 `OnMachineInitializationCompleted` 各调一次 ⇒ 初始化事件早到/晚到均覆盖；⛔ 不用定时器轮刷 |
| 与「读取」不冲突 | `BtnReadLaserZone_Click` 仍为 `LoadAlgorithmsConfig()`（含 `Reload()` 读盘）+ `LoadTaParamUi()`；补载守卫只在首次未回填时执行，不覆盖用户编辑 |
| 关联 | [[decisions/ADR-076-SettingsZoneSaveWiring]] 决策 D2 · [[lessons/ConfigZoneSaveWiring]] 坑 2 |

## 2026-11-04 修复：TA_Force 负值放开（符号=反向出力）+ 整型截断前置拦截

> 业主现场核实：`TA_FORCE_N` 的**负号就是反向出力**（不是「非法值」）。

| 项 | 结论 |
|---|---|
| 现象 | TA 下压力输入框填 `-50` 保存被拒，弹「请输入有效的下压力(N)」⇒ 反向出力无法设置 |
| 根因 | `ApplyTaToConfig` 旧校验 `force < 0.0` 一律判非法，与「负号=反向」语义冲突 |
| 第二处坑 | UI 输小数、底层 `(short)TaForceN` **向零取整**：`-0.5`/`0.5` 静默变 `0`，再由 `TA_Auto`（`==0` 拒）与 `SetTorque`（`targetTorque==0` 拒）判非法，现场只看到「没出力」 |
| 修复 | 合法区间改 **−1000 ≤ force ≤ 1000**；`0` 与「非零但截断为 0」（绝对值<1）在界面层按 `(short)` 同一规则拦下并弹窗（越界提示写明合法范围与「负值=反向」） |
| 三层口径 | 界面（本页）−1000~1000（排除 0 / 非零绝对值<1）· `LaserWeldHeadWorkflow.TaAuto` 门禁（`==0` / `>1000 \|\| <-1000`）· `DeltaMontionAxis.SetTorque`（±1000 对称）——**后两层未改动**，不出现「界面放行、门禁拦」错位 |
| 回填 | `LoadTaParamUi` 仍 `TaForceN.ToString("F1")`，负号保留 |
| 文案 | 输入框旁 `lblTaParamTip`：合法 −1000~1000、负值为反向出力、0 与绝对值<1 非法 |
| 关联 | [[decisions/ADR-080-DeltaTorqueHomingSignedModeAndDetectParams]] 决策 D4 · [[lessons/ConfigZoneSaveWiring]] 坑 3 |

## 2026-11-05 修复：删除力矩模式门禁，TA_Auto 自切 CST（ADR-082）

> 业主报告「用了 Break/Pose/Retract 之后 TA_Auto 变灰不可用」。根因不是 Radio 互斥残留，而是可用性被绑到了力矩模式开关。

| 项 | 结论 |
|---|---|
| 根因 | `RefreshActionStates` 用 `taReady && manager.TaTorqueModeEnabled` 作 `radioQuickTaAuto.Enabled`；Break/Pose/Retract/ZeroPose 与六个手动轴操作都 `SetTaTorqueMode(false)` ⇒ Auto 被置灰并清选中；`TaAuto`/`DoTaAuto` 另有两次同样拦截（共三处门禁） |
| 修复 | 删除 `TaTorqueModeEnabled`/`SetTaTorqueMode`/`TaTorqueModeChanged`；`radioQuickTaAuto.Enabled = taReady`（`taReady` 取自 `MontionManager.TaAvailable`）；`DoTaAuto()` 直接调 `TaAuto()` |
| 提示 | `UpdateTaAutoGateHint` 只保留「可用 / 不可用+降级原因」两态；可用时 showlog「TA_Auto 已恢复可用：TA_Auto 进入时会自动切 CST 并开启输出」 |
| 互斥 | 进 `TA_Auto` 时若 ZeroPose 仍在执行，由单飞登记拒绝（2026-11-09 删除 `CancelTaZeroPose`，ADR-094 D4）；切走 Auto 由 `ExitTaTorque` 撤扭矩（`DeltaMontionAxis.TorqueOutputEnabled` 判定，未输出不重复下发） |
| 关联 | [[decisions/ADR-082-TaInitFourStepAndAvailability]] · [[lessons/TorqueModeAsUiGate]] |

## 2026-11-05 修复 → 再演进：TA 下压力只填大小，方向独立配置（ADR-084 / ADR-084）

> 上一版把 `TaForceN` 当「额定千分比」校验（−1000~1000），但字段语义是牛顿；按台达口径 37N 峰值应 = 1000‰，直发只有 3.7%。随后业主裁定「工艺页只表达力的大小，方向属出厂标定」⇒ 本页输入语义改为**非负大小**。

| 项 | 结论 |
|---|---|
| 校验口径 | **`0 < 力大小 ≤ Force100PctN`**；**负号显式拒绝**（提示「此处只填力的大小，方向在『系统设置 → TA 电机 → 参数 → 扭矩方向』设置」），⛔ 不静默取绝对值；`0` 拒绝；`力大小 > 基准` 拒绝（越界）；`方向 × round(大小/基准×1000) == 0` 拒绝（低于 1‰ 分辨率 0.037N@37N） |
| 基准来源 | `MontionManager.TaHomeConfig.Force100PctN`（`ROOT/TA_HOME/TA_FORCE_100PCT_N`，默认 37N）；≤0/未配置 → 弹窗提示去系统设置填写，⛔ 不 1:1 兜底 |
| 方向来源 | `MontionManager.TaHomeConfig.TorqueDirection`（`ROOT/TA_HOME/TA_TORQUE_DIRECTION`，±1，默认 +1），**只读**；本页不提供方向入口 |
| 文案 | `lblTaForce` 改为「TA_Force 下压力大小(N)：」；`lblTaParamTip` 说明「只填大小、必须 >0 且 ≤基准，方向在系统设置 → TA 电机 → 参数 → 扭矩方向 设置」 |
| 回填 | `txtTaForce` 一律 `Math.Abs(TaForceN).ToString("F1")`，界面不出现 `-5.0` |
| 存储 | 仍写 `WeldAlgorithmsConfig.TaForceN`（INI `TA_FORCE_N`，**仅大小、≥0**），⛔ 不写 XML、不覆盖现场其它键 |
| 关联 | [[decisions/ADR-084-TaForceToTorqueConversion]] · [[decisions/ADR-084-TaForceToTorqueConversion]] · [[api/MontionManager]] |

## 2026-11-05 改版：指令区可用性口径 + 点击确认 + 执行上色（ADR-063 §六）

> 现场反馈「配置加载后指令区全部不可使用」；业主新口径：**控制器连上并装载该轴后指令区即可设置**，点 Radio 先弹窗确认，执行结果用底色表达，未选中/未执行为 Transparent。

| 项 | 实现 | 判据/说明 |
|---|---|---|
| 可用性口径 | `RefreshActionStates()`：`yReady = manager.IsInitialized && GetAxisByKeys(SeamTrackYKeys) != null`；`laReady = manager.IsInitialized && manager.WeldHead != null`；`taReady = manager.IsInitialized && GetDeltaAxisByKeys(TaAxisKeys) != null` | ⛔ 移除 `taMotionReady` 与 ZeroPose/力矩模式前置；`IsInitialized` 即「已连上 + 装载成功」唯一来源 |
| 点击确认 | 三区 `CheckedChanged`（`e.Value==true`）统一走 `RunInstruction(radio, axisName, detail, exec, ref lastRadio)` → `ConfirmInstruction` 弹 `AntdUI.Modal`（标题「指令确认」，正文=指令名+所属轴+关键参数） | 取消 → `_suppressActionRadio=true` 回填上一项（`ApplyDefaultCommandModes` 已把 `_last*Radio` 记为各自的 Auto 项，故必有上一项），不执行任何指令 |
| 防递归 | 三个 handler 首句 `if (_suppressActionRadio) return;`；回填只改 `Checked` | 避免「回退选中」再次触发 `CheckedChanged` 造成二次弹窗/执行 |
| 上色 | **2026-11-05 修订**：`ApplyActionBack` 用不透明 `BackColor`（成功 76,175,80 / 失败 244,67,54）；执行中先置中性灰 189,189,189；`ResetActionBack` → White；构造期 `SetStyle(AllPaintingInWmPaint,false)` + `Fill=Transparent` 使 `BackColor` 可见（⛔ 不再用 `Fill` 表达结果） | 实测见 [[decisions/ADR-063-CommandZoneRadioExclusivity]] §演进记录 |
| 失败可见 | 原因取 `LaserWeldHeadWorkflow.LastActionMessage`（`DeviceWorkflowBase.Log` 记录末条）→ `_tooltip.SetTip(radio, "…：执行失败 — 原因")` | 颜色之外必须留日志 + Tooltip |
| TA 特殊 | **2026-11-10 起 TA 六项全部允许点击**：`TaAvailable` 不满足 → 确认后被 `RunInstruction` 门禁拦下（**保持选中态** + 标红 + Tooltip + 日志，⛔ 2026-11-17 起不再回退选中态）；`TA_ZeroPose` 与其它 TA 指令同口径要求已回零 | 与 `CheckTaAvailable` 的可读原因一致；⛔ 不靠按钮置灰表达不可用 |
| 不加计时器 | 颜色只在「切换」「执行完成」两事件改 | ⛔ 禁止每拍重绘 |
| 关联 | [[decisions/ADR-063-CommandZoneRadioExclusivity]] §二/§六 · [[lessons/TorqueModeAsUiGate]] · `DeviceWorkflowBase.LastActionMessage`（`MainDeviceControl/DeviceStateApiCore/`） |

## 初始化闸门与指令状态检测（2026-11-05，ADR-082/063 演进）

- `RefreshActionStates()` **2026-11-05 按轴修订**：取 `MotionControlWorkflow` 的 `YReady`/`TaAvailable`/`TaMotionReady` 与 `LaserWeldHeadWorkflow` 的 `LaReady`，逐区 `Enabled`（**TA 区自 2026-11-10 起不写 `Enabled`；2026-11-13 起也不再维护状态文案/状态标签**）；初始化链未完成由各流程 getter 自己返回「初始化未完成」，⛔ 页面不再拿整机布尔一刀切。
- **撤力失败文案（2026-11-09；2026-11-13 废止）**：原本由 `lblQuickTaTip` 覆盖为「TA 力矩撤力失败（错误码 X）：力矩可能仍在输出…」；该状态标签已删除，撤力失败改由流程日志 + 按钮红底表达——只读流程 getter，⛔ 页面不自行推导力矩状态（ADR-087）。
- **刷新触发点（2026-11-05 补齐）**：构造、`VisibleChanged`（首次可见兜底）、`StateSwitched`、`InitializationCompleted`、**`AxisReadyChanged`（两 workflow 转发，逐轴使能 / ZeroPose 完成/失败即时）**、**`MotionControlWorkflow.TaZeroPoseStageChanged`（2026-11-09 事件源迁至 Workflow；选中态与四态结果色：从未执行不介入 / 运行灰 / 成功绿 / 失败红+原因）**、`InstructionWorker` 执行完成。⛔ 不用轮询 Timer。
- **刷新幂等**：只改 `Enabled`/文案/`Tooltip`/`BackColor`，不改任何 Radio 的 `Checked`；程序赋值走 `_suppressActionRadio`。
- **TA 区选中态**：不再预选 `TA_Auto`；初始化内部 `TA_ZeroPose` 开始时由 `ApplyTaZeroPoseStage` 选中 `radioQuickTaZeroPose`（抑制事件），完成/失败按 `IsTaZeroPoseDone` 上色，之后操作员可自由改选。
- `RunInstruction(radio, axisName, detail, exec, ref last)` 顺序：初始化闸门 → 同轴单飞预检（`TryBeginAxisInstruction` 已在执行中的提示在**弹确认框之前**给出）→ `ConfirmInstruction` → `ApplyActionRunning`（中性灰）→ 后台线程执行 → `BeginInvoke` 上红/绿 + `RefreshActionStates`。
- 执行与检测在后台线程：`InstructionWorker` 捕获 `exec()` 结果（异常写 `Error` 日志）并上红/绿底；UI 提示统一走 `UiMessage(bool, string)`（`InvokeRequired` 时 `BeginInvoke`）。
- `DoTaZeroPose` 等后台工作线程结束（`IsTaZeroPoseRunning=false`）后才返回，⛔ 不提前上绿；兜底 70s。
- 上色实现：`PrepareActionRadioBackColor()` 对每个指令 Radio 调 `SetStyle(ControlStyles.AllPaintingInWmPaint,false)` 并 `Fill=Transparent`；`ApplyActionBack` 只写不透明 `BackColor`。
- 页面销毁（`HandleDestroyed`）调 `CancelAllAxisInstructions("工艺设置页销毁/切页")`。

## TA 指令区去禁用（2026-11-10，ADR-082 D30~D32）

- **为什么**：初始化结果会过期——初始化时没连上、之后手动连上，UI 没有事件能实时得知，按钮只会一直灰着（业主口径「点了没反应」）。
- **改法**：`RefreshActionStates()` 不再写 TA 六个 Radio 的 `Enabled`；就绪判定唯一权威移入执行段（`CheckTaAvailable` / `TryBeginAxisInstruction`；⛔ `CheckTaMotionReady` 已于 2026-11-17 删除）。
- **不可用怎么让业主知道**（2026-11-13 收敛为三处，状态标签全部删除）：① 点击时 `RunInstruction` 的按轴门禁先做「早失败」——写 `Warning` 日志 + 回退选中态 + 红底，不弹确认框；② 仍被下发到执行段时，拒绝理由由执行段写日志，`ApplyActionBack` 上红底；③ 初始化未完成 / Y、LA 未就绪由对应 Radio 置灰可见。~~悬停 Tooltip 与 `lblQuickTaTip` 原因文案~~ 已删除。
- **保留的禁用**：`IsAxisInstructionBusy` / `TryBeginAxisInstruction` 的「同轴指令执行中」照旧拒绝（防重入）；Y、LA 两区的 `Enabled` 照旧。
- **判定去重（⛔ 2026-11-17 改版）**：`MontionManager.TaAvailable` 收敛为 `TaMotionReady && TaHomed`（不再复述同一串初始化/装配/使能判断）；`RunTaZeroPoseAfterInit` 直接委托 `ExecuteTaZeroPose`，删去与本方法内 `CheckTaMotionReady` 重复的初始化闸门与可动判断。

## 轴对象清零（2026-11-08，ADR-093 决策八）

- **本页不再出现任何 `MontionAxis` / `DeltaMontionAxis` 类型**（含局部变量与字段）；也不再调 `axis.AxisStop(...)`。
- `ResolveInstructionAxisKey`（原 4 处轴对象之一）改为 `MontionManager.TryGetAxisNameByKeys(TaAxisKeys / SeamTrackYKeys, out axisName)`，只取轴名。
- `MoveAxisHome` / `MoveAxisToTarget` 改为 `MotionControlWorkflow.TryHomeAxisWithWait` / `TryMoveAxisToTarget`：
  门禁（已初始化 / 角色轴已装配 / `GetAxisGateReason` / `TryBeginAxisInstruction` / 指令超时 / 失败减速停止）全部在 Workflow 内，与原 UI 实现等价。
- 本页只按 `rejectCode`（`AxisReject*`）分支还原文案与日志；`NOT_REACHED` 分支打印 Workflow 返回的 `evidence`。
- ⚠️ 时序变化（文本不变）：原「已下发，进入状态检测」打在「下发后、等待前」，现改为 Workflow 返回后补打。

## TA_ZeroPose 指令底色四态（2026-11-09，ADR-093 决策九）

- 落色判据：running → 中性灰；done → 绿；failed → 红（Tooltip 带 TaDegradedReason）；attempted 但既未到位也未失败（被其它 TA 指令切换中止）→ 复位底色，⛔ 不算失败。
- 「从未执行」（attempted=false）不介入：不抢占选中态、不上色。
- IsTaZeroPoseAborted 使被中止的 ZeroPose 执行线程跳过 ApplyActionBack，避免误上红。

## 刷新收敛与点击不刷新（2026-11-11）

- **唯一刷新入口**：`_actionTimer`（`System.Windows.Forms.Timer`，`Interval = FlowTimeoutSettings.UiRefreshMs`，缺省 33ms ≈ 30Hz）→ `ActionRefresh_Tick`。
- **采集与上屏分离**：`ActionRefresh_Tick` 只 `Task.Run(CollectGateSnapshot)` 后台取硬件（`IsServoOn` / `GetStatusWord` 全在这里），`BeginInvoke` 回 UI 只做赋值；`_gateBusy` 单飞，上一拍没回就跳过本拍。
- **UI 线程直读权威源（⛔ 2026-11-17 改版）**：门禁快照 `ActionGateSnapshot` 已整体退场，`ResolveAxisGateReason` 改为点击时直读 `TaAvailable` / `YReady` / `LaReady` / `TaDegradedReason`（快照会过期，直读才是真相源）。
- **差分上屏**：`SetControlEnabled` / `SetText` 先比较再赋值，值没变一个字节都不碰；上色（`ApplyActionBack` / `ApplyActionRunning` / `ResetActionBack`）同理，同色不重绘。
- **Tooltip 只讲按钮作用**：18 个指令按钮在 `InitCommandTooltips()` 构造时 `SetTip` 一次，此后任何刷新、任何状态变化都不碰；⛔ 不承载状态（无「不可用/原因/仅某指令可重试」类文案），悬停也不再重算文案。
- **状态表达渠道**（唯一三处）：按钮**底色**（灰=执行中 / 绿=成功 / 红=失败）、轴表的**指示灯与实时状态码**、**日志**（被拒原因、忙、取消、执行异常）。⛔ 2026-11-13 起不再有状态标签，⛔ 不得把状态塞回 Tooltip。
- **点击只派发**：`radioQuickTa_CheckedChanged` → `RunInstruction` 只做「读缓存闸门 → 确认 → 置运行态 → 起后台线程」，**不刷新、不循环、不等结果、不取硬件**；权威判定留执行段，结果由完成回调置脏标记。
- **事件只置位**：`OnMotionStateSwitched` / `OnAxisReadyChanged` / `OnTaZeroPoseStageChanged` / 初始化完成 / 可见性变化，一律 `RequestActionRefresh()`（`volatile` 脏标记 + 跨线程 `PostToUi`）。
- **非当前页不采**：`ActionRefresh_Tick` 在 `!Visible` 时直接返回且保留脏标记，切回本页再刷。
- **节拍不混用**：`FlowTimeoutSettings.PollIntervalMs=16` 只属执行侧轮询/等待；UI 刷屏一律取 `UiRefreshMs`（配置 `ROOT/FLOW_TIMEOUT/UI_REFRESH_MS`）。
- **诊断**：`点击诊断 …入口到线程启动 Nms`、`刷新诊断 耗时 Nms 重绘 N 次` 均为 `MessageLevel.Debug`，不改日志级别即不输出。
- **销毁收口**：`ProcessControlPage_HandleDestroyed` → `DisposeActionTimer()` 停表退订。

## 分段口径改按距离（2026-11-17，阶段 7 / ADR-103）

- 焊参调整面板删除「分段方式」下拉（`selFlowIsCountType`）与「每段点数」标签，输入框 `txtFlowCountNum` 保留、文案改「每段距离(mm)」。
- `ApplyAdaptUiToMemory` 读 `cfg.SegmentDistanceMm`，空值回填原值，越界钳位 1~50；`LoadFlowSwitchOnForm` 以 `F1` 回显。
- 新增红色提示条 `lblNoValueAlarmHint`：「缺值达到阈值即报警停焊：清警后回起始位从头重焊，不支持断点续焊。」
- ⛔ 不加续焊/断点接续按钮（N11）。
- 关联：[[decisions/ADR-103-no-value-hold-and-distance-segment]] · [[api/WeldParamAdjustmentAlgorithm]]

## 门禁直读 + TA 单色互斥 + 页内独立定时器（2026-11-17，ADR-063 D28 / ADR-082 D26）

- ⛔ **门禁快照整体退场**（`ActionGateSnapshot` / `_gateSnapshot` / `_actionDirty` / `_gateBusy` 全删）：按 UI 状态规范「真相源唯一」，`ResolveAxisGateReason` 改为**点击时直读** `MotionControlWorkflow.TaAvailable` / `YReady` / `LaReady` —— 快照会过期，直读才是真相源。
- **TA 区互斥单色**：`radioQuickTa_CheckedChanged` 选中新指令时复位**同组其它** Radio 底色 ⇒ 任何时刻最多一个有色；被拒只标红当前项，旧色不残留（消除「点一下多一个红」）。
- **TA 门禁口径**：⛔ 2026-11-17 起 **TA_Zero 与其它 TA 指令同口径** —— 一律要求「已使能 + 已回零」（`TaAvailable`），⛔ 不要求工作零位到位。
- **显示信息刷新**：本页 `timerRefresh`（Designer 托管）只刷新 TA Break 停止位；⛔ 不做按钮管控与状态判定。
- **按钮管控**：`RefreshActionStates()` 改事件驱动（连机切换 / 初始化完成 / 轴就绪变化 / 操作完成）同步直读权威源。
- **定时器**：本页 `timerRefresh` 由本 Designer 托管（`components` 容器），**页内唯一实例**，⛔ 不与系统设置页共用。
- 关联：[[decisions/ADR-063-CommandZoneRadioExclusivity]] · [[decisions/ADR-082-TaInitFourStepAndAvailability]]

## 指令区不变量 + TA_Zero 同口径 + 确认在前（2026-11-17，ADR-063 D31 / ADR-082 D30）

**指令区不变量**（Y 组 / TA 组 / LA 对焦组 / GA 振镜组，按容器作用域分组）：
> 任一时刻每组**最多一个** Radio 带底色，且**带底色者 = 该组当前选中者**。

- `RunInstruction` 链路改为 **点击 → 确认 → 门禁 → 单飞 → 执行 → 上色**：
  - ⛔ **确认在前** —— 执行动作必须等用户点确定才生效；门禁判定放在确认之后（用户点确认但被拦截时给出明确反馈）。
  - 门禁 / 单飞被拒：**保持当前选中态**并标红 + 清同组旧底色（不再回退选中态 ⇒ 消除「TA_Zero 被选中、TA_Auto 是红的」）。
  - 取消确认：回退选中态到上一项，并复位本次的旧底色。
- 自动 `TA_ZeroPose` **不抢用户选中态、不占用指令区底色**；只有当用户自己正选中 `TA_Zero` 时才把结果色落在它身上。
- `ResetOtherRadioBacks` / `RadioGroupOf` 取代原先只管 TA 组的复位逻辑，三区统一。

**TA 门禁**：`TA_Zero` 与其它 TA 指令**同口径** —— 一律要求「已使能 + 已回零」（`TaAvailable`）；「已回零」不区分来源。

- 关联：[[decisions/ADR-063-CommandZoneRadioExclusivity]] · [[decisions/ADR-082-TaInitFourStepAndAvailability]]

## GA 设置区控件删除与代码后置收敛（2026-11-18）

> 业主在设计器删除「GA 设置区」与 GA 指令 / 系统设置重叠的 4 个控件，AI 负责代码后置收敛 + 编译修复。

**删除的控件（Designer 层已清空，代码后置已同步收敛）**

| 控件 | 类型 | 职责 | 重叠对象 |
|---|---|---|---|
| `selGalvoPattern` | `AntdUI.Select` | 振镜图形下拉（4 项） | GA 指令区 `radioQuickLaGalvo*` 图形 Radio |
| `lblGalvoPattern` | `AntdUI.Label` | 「振镜图形」标题标签 | 同上 |
| `btnGalvoDemo` | `AntdUI.Button` | 振镜演示 | GA 指令区图形组 |
| `btnGalvoHome` | `AntdUI.Button` | 振镜回零位 | 系统设置页 `btnOptGalvoHome` |

**代码后置收敛（`ProcessControlPage.cs`）**

- ⛔ 删 `selGalvoPattern_SelectedIndexChanged` —— 控件已删 ⇒ 事件永不可能触发；方法内含 CS0103。
- ⛔ `SetGalvoPattern` 去掉回写 Select 的赋值 ⇒ 落盘仍走 `SaveGalvoPattern`（④Preset 区），**图形落盘入口仍唯一**（ADR-076 §四 不变）。
- ⛔ 删 `btnGalvoDemo_Click` / `btnGalvoHome_Click` —— 订阅点随控件删除，方法不可达。
- ✅ **保留** workflow 层 `LaserWeldHeadWorkflow.GalvoDemo()` / `GalvoHome()`：`GalvoHome` 被系统设置页 `BtnOptGalvoHome_Click` 消费；`GalvoDemo` 虽 UI 侧唯一入口被删，但属 workflow 公共 API（[[api/LaserWeldHeadWorkflow]] 契约），删除属架构变更 ⇒ **本轮不动**，留待业主裁定。

**布局同步（Designer）**

- GA 图形 Radio 由第 1 行移至第 2 行，新增分组标题 `label7`「GA指令」/ `label8`「GA设置」（`AntdUI.Label`，`SetColumnSpan` 4 列）；`gridQuickLa` `RowCount` 10 → 11。
- ⛔ `gridQuickLa` 为 `TableLayoutPanel`（非 `GridPanel`）⇒ 无 `Span` 串同步问题；`RowCount == RowStyles` / `ColumnCount == ColumnStyles` / 无格位冲突已机检通过。
- 关联：[[lessons/UiModuleRemovalCleanup]] · [[lessons/UiLayoutChangeSyncPitfalls]] · [[decisions/ADR-076-SettingsZoneSaveWiring]]

## GA 图形语义收敛 + 冗余清理（2026-11-18）

> 业主裁定（完整链路）：「**没有开启振镜自动运行时是没有图形的；当配置启用了振镜功能，那么必须有一个图形，如果有设置就用设置，如果没有就落回默认 Line**」+「初始使用读取，未读到默认没有图形，图形始终以实际为准」。

**三层语义（ADR-076 D3 + D4）**

| 层 | 载体 | 语义 |
|---|---|---|
| 配置 | `WeldAlgorithmsConfig.GalvoPattern`（int） | `0` = 未设置（无图形）；`1..4` = 圆/八字/直线/圆弧；INI 越界 ⇒ 归 0 + 记 Warning（⛔ 不再静默回退 3） |
| UI 选态 | GA 指令区 `radioQuickLaGalvo*` | **振镜未启用 ⇒ 没有图形**（清空整组选中 + 整组置灰）；**已启用 ⇒ 必有图形**（有设置用设置；无设置 ⇒ 落回 `Line` 并落盘） |
| 设备下发 | `LaserWeldHeadWorkflow.ResolveGalvoPattern(int)` | `0`/越界 ⇒ **逻辑零位的直线**（协议枚举 `WsgGalvoPattern` 为 1..4 **无 0**，⛔ 禁下发非法值到 0x7010 子索引 1） |

**振镜启用态的唯一真相源**：`LaserWeldHeadWorkflow.IsGalvoWeaveEnabled()` —— 实时读 `cfg.EnableGalvoWeave`（系统设置页 `swEnableGalvoWeaveQuick` 的落点）。⛔ 原 `LoadConfig()` 期快照字段 `_galvoWeaveEnabled` 已删（运行期改开关不刷新），现与 `WeldParamControlWorkflow.GetAmplitudeMm` 同口径。

**跨页联动路径**：系统设置页切开关 → 落 ②Quick 区 → 切回工艺设置页触发 `ParamAutoPage_Shown` → `LoadAlgoConfigOnForm` → `LoadGalvoActionUi` → 图形选态与置灰自动收敛。

**本轮精简（`ProcessControlPage.cs`）**

- ⛔ **删 `_syncingLaRadios`** —— 原为「Radio↔Select 双向同步抑制」，Select 删除后职责消失；其赋值窗口与 `_loadingGalvoUi` **完全同生命周期**，且 Radio 同父容器自动互斥（置 `Checked=true` 只让同组其它变 false，`e.Value == false` 被首行守卫拦掉）⇒ `_loadingGalvoUi` 单标志已足够。
- ⛔ **删字段 `_galvoPatternSelected`** —— 原为图形 Select 时代的双向同步缓存；Select 删除后其写点（`SetGalvoPattern`）**再无读者** ⇒ 图形状态不再缓存于 UI 字段，唯一真相源 = `WeldAlgorithmsConfig.GalvoPattern`（**以实际为准**）。
- ⛔ `RadioToGalvoPattern` / `GalvoPatternToRadio` 的 `default` 由**静默兜底直线**改为**返回 null**；前者不匹配时记 Warning（防止新增图形 Radio 后被静默落成直线）。
- ✅ **保留** `_loadingGalvoUi`（回填 `Checked` 会触发 `CheckedChanged`，见 [[lessons/UiLayoutChangeSyncPitfalls]] 坑三）、`SaveGalvoPattern` / `GalvoPatternText`。
- ⚠️ **执行顺序**：清选中在 `RefreshActionStates()`（置灰）**之前**（避免对 Disabled 控件改 `Checked`）；清选中触发的 `CheckedChanged` 由 `_loadingGalvoUi` 抑制（⛔ 不误落盘）。
- 关联：[[decisions/ADR-076-SettingsZoneSaveWiring]] · [[api/LaserWeldHeadWorkflow]] · [[lessons/UiModuleRemovalCleanup]]

## GA 按图形分档 + 手动/自动两套模式（2026-11-18）

> 业主裁定三条：① **图形设置完全由指令区接管**；② **GA 设置的宽度/长度/频率按每种图形各存一档**（没有配置时默认加载 Line 档）；③ **GA 设置就是「自适应参数没有输出时的宽度」** —— 手动模式的恒定宽度改由 GA 档承担。
> 依据：[[decisions/ADR-070-GalvoWeaveAsWidthSource]] 演进节 · [[decisions/ADR-076-SettingsZoneSaveWiring]] 决策 D5 · [[decisions/ADR-103-no-value-hold-and-distance-segment]] 落地演进。

### 一、GA 图形参数分 4 档

| 项 | 载体 |
|---|---|
| 存储 | `WeldHeadConfig.GalvoShapePresets`（`Dictionary<WsgGalvoPattern, GalvoShapeParams>`，每图形一份宽/长/频） |
| 持久化 | `WeldHeadSlave.xml` 的 `GALVO/<CIRCLE\|EIGHT\|LINE\|ARC>/WIDTH\|LENGTH\|FREQUENCY`；顶层 `GALVO/WIDTH\|LENGTH\|FREQUENCY` 保留为**存量迁移基准** |
| 缺档回退 | 指定图形缺档 ⇒ 回退 **Line 档**（`GetGalvoShape`）；存量 XML 只有顶层一份 ⇒ 各档缺省取该旧单档值（读侧 `legacyWidth/legacyLength/legacyFrequency` 承接，不丢现场配置） |
| 全局项 | 角度/起止角/中心/压缩/目标尺寸/斜椭校正仍属 `DefaultGalvo`（各图形共用），**只有宽/长/频分档** |

**UI 联动**：`radioQuickLa_CheckedChanged` 的 GA 分支 ⇒ `SetGalvoPattern`（落盘图形值）+ `LoadGalvoShapeToInputs()`（载入该图形档）；`ApplyGalvoParamsToHead()`（保存）⇒ 写回**当前图形档**。

**`DefaultGalvo` = 当前生效参数集合**：`WeldHeadConfig.SyncDefaultGalvoFromShape(pattern)` 把当前档镜像进 `DefaultGalvo`（图形 + 宽/长/频），三处调用点（页面加载 / 切换图形 / 保存档）。⛔ 原因：GA 分档后 `DefaultGalvo` 的宽/长/频不再被 UI 直接编辑，而「全量下发 `DefaultGalvo`」的路径仍在（工艺页保存、系统设置页保存）⇒ 不同步会把设备刷成陈旧旧值。

### 二、手动 / 自动两套模式（互斥）

| | 自动模式 | 手动模式 |
|---|---|---|
| 触发 | 自动焊接 / 自适应工艺启动 | UI 手动调试（GA 区「**手动下发 / 关闭退出**」按钮组 `btnGalvoManualStart/Stop`） |
| 振镜下发 | `ApplyGalvoAmplitude` 每拍随动 | **输出一次**（`LaserWeldHeadWorkflow.GalvoManualStart`），不进随动循环 |
| 宽度来源 | Laser（线激光实测） | Manual（恒定，取 **GA 档宽度**） |
| 互斥 | ⛔ 自动模式下 UI 手动按钮不生效 | ⛔ 手动动作与生产流程互斥 |

- 门禁复用 `LaserWeldHeadWorkflow.EnsureManualWeldHeadActionAllowed`（`IsAutoWeldingRunning` 时拒绝）——与既有手动动作同口径，不另立门禁。
- UI 置灰：`btnGalvoManualStart/Stop` ← `laReady && !IsAutoWeldingRunning`；⛔ **不按振镜启用态禁用**（手动调试的目的正是「振镜未启用时也能下发看效果」）。
- ⛔ 删 `GalvoDemo()`（零调用方 + UI 入口已删）⇒ 替代 API：`GalvoManualStart(pattern, shape)` / `GalvoManualStop()`。

### 三、③自适应区瘦身后的宽度来源

- ⛔ **删 `ManualSeamWidthMm`**（与 GA 设置区的手动宽度重复）⇒ Manual 源宽度 = `WeldParamAdjustmentAlgorithm.ManualFixedWidthMm()` ⇒ `GetGalvoShape(pattern).Width`；振镜未启用 ⇒ 没有图形 ⇒ 图形取配置（`ResolveGalvoPattern` 0/越界 ⇒ Line）⇒ 回退 **Line 档宽度**。
- ⛔ **删 `SpotWidthGain`**（含查表算法 3 处乘算 + `RefreshSpotWidthDic`/`RefreshSpotWidthByGain` 四链）⇒ 查表光斑宽 = 焊缝宽（乘 1.0 恒等，**行为等价**）。
- ⛔ **删 `ParamOutputHz`** ⇒ 工艺参数输出触发改**按段落长度**（`TickXlOutput` 时间维节流 → 距离维节流，阈值复用 `SegmentDistanceMm`，⛔ 不另设配置项、不新增变量）。
- ⛔ **删 GA 卡 `txtManualWidth`/`lblManualWidth`** 与轨迹点区 `txtParamManualWidth`/`txtParamSpotGain`/`selParamOutputHz` 等 6 个控件（四落点 + 事件 + 专属字段 + 容器占位一并清）。
- ⛔ **模拟基准宽度收敛为常量**：`VirtualCam.BaseSeamWidth` / `BaseSeamDepth` 改 `const`（无可设入口）⇒「模拟测试启用自适应调整时持续输入恒定基准宽度」。`VirtualCam.FrameRateHz` 有外部写入（系统设置页「线激光数据频率」）⇒ **不动**。
- 关联：[[decisions/ADR-076-SettingsZoneSaveWiring]] D5 · [[decisions/ADR-070-GalvoWeaveAsWidthSource]] · [[decisions/ADR-103-no-value-hold-and-distance-segment]] · [[api/LaserWeldHeadWorkflow]] · [[lessons/UiModuleRemovalCleanup]]

## 读/改/存三按钮的 TabPage 边界（2026-11-19 ADR-076 D9）

| 按钮 | 所在 TabPage | 刷新区 | 回填控件 |
|---|---|---|---|
| `BtnReadAutoParam`（读取焊参调整） | 自适应工艺参数设置 | `Adapt` | 本 TabPage 的两个距离输入 + 焊参表 |
| `BtnSaveAutoParam`（保存焊参调整） | 自适应工艺参数设置 | `Adapt`（落盘） | — |
| `BtnReadLaserZone`（读取激光工艺参数） | 激光工艺设置 | `Preset` + `Quick` | GA / LA / TA 参数 + Y 指令 radio |
| `BtnModifyLaserZone`（修改应用参数） | 激光工艺设置 | 只写内存 | — |
| `BtnSaveLaserZone`（保存参数） | 激光工艺设置 | `Preset`（落盘） | — |
| `BtnReadLaserZone` 附带 | — | 焊接头独立载体 `WeldHeadSlave.xml` | 振镜宽/长/频 + 阈值 |

⛔ **「读取」只写回现有配置对象**（`LoadAlgorithmsZone` 先 `Reload()` 载体再读指定 zone，**不 new、不替换** `_algorithmsConfig`）⇒ 其它 TabPage 已「修改参数」但未保存的内存改动**不会被丢弃**。

⛔ **跨 TabPage 回填已移除**：自适应区的读取不再刷新激光工艺区的 Y 指令 radio；激光工艺区的读取不再刷新自适应区的距离输入框。被移走的控件由**页面构造**时的批量回填（`LoadXxxOnForm`）与本 TabPage 自己的入口负责。

- 关联：[[decisions/ADR-076-SettingsZoneSaveWiring]] D9 · [[lessons/UiButtonZoneBoundary]] · [[api/WeldParamManager]]

## 默认长宽频清理 + LA 默认焦平面（2026-11-18）

> 业主裁定三条：① **GA 分档后，原来没有按照图形区分的默认长宽频需要清理掉，不再任何地方起作用**；
> ② **LA_Pose2 修改为 LA_DefaultFocus**，意为默认焦平面 LA 的位置，不再是随意设置 LA_POSE；
> ③ 接入焊接头后（初始化连接结束）LA 自动回到该位置（LA 无轴 Home ⇒「回零」= 回工作位）。
> 依据：[[decisions/ADR-070-GalvoWeaveAsWidthSource]] §五 · [[decisions/ADR-067-LATaSettingsSemanticRework]] 演进记录。

### 一、默认长宽频清理（物理删除，非标记弃用）

| 项 | 旧 | 新 |
|---|---|---|
| `WeldHeadConfig.DefaultGalvo` 类型 | `GalvoParams`（协议结构，含图形/宽/长/频） | **`GalvoGlobalParams`**（只含 10 个全局项）⇒ 该实例上**物理不存在**图形与宽/长/频 |
| 振镜下发 | `head.SetGalvoParams(headCfg.DefaultGalvo)` | `head.SetGalvoParams(headCfg.BuildGalvoParamsFor(pattern))`（全局项取 DefaultGalvo + 图形/宽长频取该档） |
| XML 顶层 | 写 + 读 `GALVO/WIDTH\|LENGTH\|FREQUENCY` | **不再写、不再读进 DefaultGalvo**；宽长频一律落 `GALVO/<图形>/` |
| 存量迁移 | — | 老 XML 顶层三键读一次作各档缺省值（缺省 = 协议默认 宽 1.0 / 长 1.0 / 频 50） |

- ⛔ 禁直接下发 `DefaultGalvo`（会带出无来源的空位）。
- ⛔ 上一轮的「镜像」方案（`SyncDefaultGalvoFromShape` / `SyncCurrentGalvoToDefault`）已随之删除 —— 镜像仍让 `DefaultGalvo` 保留无来源字段，与「清理掉」冲突。
- `GalvoParams` 的图形/宽/长/频字段**保留**（协议下发要用），但注释已注明「配置路径已无来源，仅协议组装时由档填充」。

### 二、LA 默认焦平面（语义改名 + 初始化回工作位）

| 项 | 旧 | 新 |
|---|---|---|
| Radio | `radioQuickLaPose2` / Text `LA_Pose2` | `radioQuickLaDefaultFocus` / Text `LA_DefaultFocus` |
| 参数区 | `lblLaPose2` / `txtLaPose2` | `lblLaDefaultFocus`（"LA 默认焦平面(mm)"）/ `txtLaDefaultFocus` |
| 配置项 | `LaPose2Mm` | `LaDefaultFocusMm` |
| INI 键 | `LA_POSE2_MM` | `LA_DEFAULT_FOCUS_MM`（旧键一次性迁移 + 记 Info，之后停写） |
| workflow | `LaPose2()` | `LaDefaultFocus()` |
| UI 处理器 | `DoLaPose2()` | `DoLaDefaultFocus()` |

- **动作语义不变**（仍是「直接移到配置的 LA 电机绝对位置」，与 `Spot*` 的「设光斑 + 按 TA 推算」相对）；变化的是业务含义 —— 从"调试位"升为"默认工作位"。
- `LA_Pose1` 保留（另一个调试位）；**TA 侧 Pose1/Pose2 不动**（另一条链路）。
- **初始化后自动就位**：`LaserWeldHeadWorkflow.MoveToDefaultFocus()`（非阻塞下发、不等到位、不走手动门禁），由 `DeviceControlWork` 初始化收尾处**主动调用**。
  - ⛔ **不在 workflow 构造期订阅 `DeviceControlWork.InitializationCompleted`** —— `DeviceControlWork` 的 `readonly _weldHead = LaserWeldHeadWorkflow.Instance` 会在其构造期创建 workflow，此时读 `DeviceControlWork.Instance` 会触发整机初始化。
  - ⛔ 不属 ADR-099「初始化只连接使能」范畴（LA 无轴 Home，此处是**移到工作位**而非轴回零）。

- 关联：[[decisions/ADR-070-GalvoWeaveAsWidthSource]] · [[decisions/ADR-067-LATaSettingsSemanticRework]] · [[api/LaserWeldHeadWorkflow]] · [[lessons/ConfigKeyRemovalAndTruthSourceMigration]]

## 配置文件按 TabPage 拆分（2026-11-19 ADR-076 D8）

> 业主裁定：「完成逐项逐文件迁移」—— 配置文档按 TabPage 分割成不同文件，页面保存/修改不影响其它页面的值。

### 一、实测修正了 D6 方案表（三处偏差）

| D6 原表 | 实测真相 |
|---|---|
| ②Quick 开关归工艺页 | ❌ 5 个 Enable 开关在**系统页·流程控制与测试**（`tLPFlowSetting`） |
| ④Preset 归工艺页 | ✅ 但**同 zone 内部跨 TabPage**：`LockYCalib` 在工艺页、Enable 开关在系统页 |
| XML 拆 3 文件 | ❌ XML 只有 ①System 一区，拆不了；要拆的是 INI |

⇒ **zone 粒度不足以表达 TabPage 归属** ⇒ 新增 `AlgorithmsZone.Flow`（②′）。

### 二、本页（工艺页）的落盘归属

| TabPage | INI 文件 | section | 项 |
|---|---|---|---|
| 激光工艺设置 | `WeldParamControlAlgorithm.ini` | `PROCESS_CONTROL` | Preset 12 项（LA/TA/GA 预设）+ `LOCK_Y_CALIB` |
| 自适应工艺参数设置 | `WeldParamControlAlgorithmAdaptive.ini` | `WELD_PARAM_ADJUST` | `SEGMENT_DISTANCE_MM` + `MAX_CONSECUTIVE_FAILURES` |

- 本页 `SaveAlgorithmsZone(Preset)` / `(Quick)` / `(Adapt)` **各自只落自己的文件** ⇒ 不再覆盖系统页未保存的值。
- ⛔ 4 个零引用死配置已物理删除：`LockSpotCalib` / `LockWirePos` / `SpotCalibPosMm` / `WireLockPosMm`（全仓引用 0，无 UI 落点）。

- 关联：[[decisions/ADR-076-SettingsZoneSaveWiring]] D8 · [[lessons/ConfigFileSplitByTabPage]]

## 跟踪几何项迁出 + 配置文件按 TabPage 分割（2026-11-18）

> 业主裁定：① **YT 设置下的轴/激光比例系数、偏差方向、激光超前量(mm)、机器人Y补偿系数**等跟踪几何项，**迁到系统设置页·轨迹跟踪参数设置·标定参数区**；② **取消 Y 轴行程上限/下限**（Y 轴点击设置里已有）；③ 配置文件**按 TabPage 分割成不同文件**，保存/修改时不影响其他页面的值。

**一、UI 迁移（7 项几何 + 标定项 → 系统设置页「标定参数」区）**

| 项 | 旧位置 | 新位置 |
|---|---|---|
| 轴/激光比例系数 · 偏差方向 | 工艺页·YT 设置（`gridQuickTracking` 行 4） | 系统页·轨迹跟踪·标定参数区（`gridLaserCalib` 行 3） |
| 激光超前量 · 机器人Y补偿系数 | 工艺页·YT 设置（行 5） | 同上（行 4） |
| 示教Y锁定坐标 · 标定中心点Y/Z | 工艺页·YT 设置（行 7/8） | 同上（行 5/6） |
| Y 轴行程下限/上限 | 工艺页·YT 设置（行 6） | ⛔ **删除**（改用轴软限位） |

- 落盘入口随之迁移：系统页 `button2`「修改参数」写内存 → `button3`「保存参数」落 ①System 区（XML）。
- ⛔ 工艺设置页**不再落 ①System 区** ⇒ XML 文件成为「轨迹跟踪 TabPage」独占文件。

**二、Y 轴行程上下限取消（重复性核查结论）**

两套配置**并存但判断不重复**：轴软限位（`DeltaMotionConfig` 的 `POSITIVE_LIMIT`/`NEGATIVE_LIMIT`，UI 在轴配置弹窗）**仅存储不下发**（`SoftLimitMode` 无下发路径），未参与任何运行时判断；工艺侧 `YAxisMinMm`/`YAxisMaxMm` 是 `MotionControlWorkflow` 唯一做限幅与越界判据的地方。
⇒ 删工艺侧两项，限幅改接**轴软限位**（`TryGetSeamAxisSoftLimit`；0 = 不启用 ⇒ 不限幅）。
⚠️ **行为变化**：原区间 `[-15,+15]`；改接后取轴软限位（现场实测 正 20 / 负 **-1**，负值疑为占位值）⇒ 区间变 `[-1,20]`，**需现场把 Y 轴正/负软限位配成真实行程**。

**三、配置文件按 TabPage 分割（ADR-076 D6，本轮落地第一步）**

- XML 侧：`SEAM_GUIDE` 几何 4 项由 ④Preset 区**迁入 ①System 区** ⇒ `LoadZoneXmlPreset`/`SaveZoneXmlPreset` 整体删除 ⇒ **section 名不变 ⇒ 存量文件零迁移**。
- ⛔ **zone ≠ TabPage**：分区落盘只保证 zone 之间互不写，跨 TabPage 隔离**必须靠物理分文件**。INI 侧拆文件（工艺设置页两个 TabPage 各自一套）与存量逐键迁移列为下一轮任务。
- 关联：[[decisions/ADR-076-SettingsZoneSaveWiring]] D6/D7 · [[api/SystemControlPage]] · [[api/MotionControlWorkflow]] · [[lessons/PythonEditByteSafety]]
