---
title: SystemControlPage 系统设置页（原 MotionControlPage）
date: 2026-09-17
updated: 2026-11-17
tags: [API, UI, 系统设置, 运控, 参数页, 跟踪系统, 光丝系统, 温控系统, 模拟测试, 轴, NavPage, Tabs, ADR-010, ADR-035, ADR-105]
source: AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs + .Designer.cs + SubDialog/MotionControlDialog/{AxisConfigForm,IoConfigForm,CylinderConfigForm}.cs
---

# SystemControlPage — 系统设置页（四 Tab 分区）

> 🔄 **2026-11-20 温度显示迁出（ADR-112 演进）**：激光头页温控区 `panelTempSys`→`gridTemp` 的**实时温度显示**（保护镜/腔体/温升/切割气压 4 项 + 报警状态 `lblTempState`）与采集链 `CollectTemperature`/`ApplyTemperature`/`TemperatureSnapshot` 已迁至 [[api/DeviceMonitorPage]]（由新页自有 500ms Timer 驱动）。本页温控区**只保留**：① 焊接头节点设置（`swWeldHeadEnable` + `numWeldHeadNode`，在 `flowPanel3` 内）② 6 项阈值（温度警告/报警、温升警告/报警、气压报警/延时，由 `LoadTempFromConfig` 回填、`ApplyLaserHeadOnForm` 写回）。温度自动刷新开关 **`swTempRefresh` 已删除**（显示迁走后无刷新对象），其容器 `flowPanel3` 保留（承载焊接头启用开关）；`_tempAutoRefresh` 与 `RefreshSnapshot.Temp/Temperature` 分发分支同步清零，其余四刷新开关（TA/LA/振镜/轴表）机制不变。

> 🔄 **2026-09-29 二次重构（业主令，现行）**：页面显示名由「运控设置」改为「**系统设置**」；`tabsSystem` 由五分区（输入IO / 输出IO / 轴控配置 / 气缸操作 / 导入导出）**整体重排为四分区**——**① 跟踪系统参数**（`tabPageTrajectoryParam`：**轨迹点设定**（自 [[api/ProcessControlPage]] 迁入）+ **Y 向电机轴配置**（`tableAxis`））→ **② 光丝系统参数**（`tabPageLaserHeadParam`，占位）→ **③ 温控系统参数**（`tabPageLaserHeadParam`，占位）→ **④ 模拟测试**（`tabPageSimTest`，自 `ProcessControlPage` 迁入，单开一页）。⛔ **输入IO / 输出IO / 气缸操作三表取消**（`tableInputIO` / `tableOutputIO` / `tableCylinder` + `IORow` / `CylinderRow` 行模型一并删除；业主裁定「后续回归为各个系统参数设置」）；⛔ **CSV/XML 导入导出区（`flpToolbar` 整条：目录选择 + 导入/导出 + 保存/重载 XML + 自动刷新 / 刷新轴）迁出至 [[api/FilebackupPage]]「系统配置文件」页**。⚠️ **轴表只渲染 Y 轴**（业主裁定「只显示 Y 轴，因为它属于跟踪系统的轴」）——`LoadAxisRows()` 经 `IsTraceAxis()` 按关键字 `{ "Y", "横梁", "跟踪" }` 过滤，其余轴不进表；**轴表 19 列操作（JOG / 回零 / 使能 / 绝对移动等）与 `AxisRow` 行模型零改动**。下述「五分区」已被本次重构取代。

> 🔄 **2026-09-29 更名 + Tabs 改造（业主令）**：类与文件 `MotionControlPage` → **`SystemControlPage`**（`csproj` 四处条目、`FormMain.cs` 实例化同步）；`panel1` 内的 `panelInner`（`TableLayoutPanel` 1 列 × 5 行）**删除**，改由 `tabsSystem`（`AntdUI.Tabs`）+ 4 个 `AntdUI.TabPage` 承载四张表，`flpToolbar` 由 `Dock=Fill` 改 `Dock=Top`（高 76，两行按钮不裁切）——⛔ 该项于**同日 14:32 二次调整中被取代**（见本框末句）。目的：**四表纵向堆叠须整页下拉**（`AutoScroll`）→ Tab 分区消除页面级滚动。**表数据链路/行模型/事件派发零改动**，仅容器更替（布局容器自由化 [[decisions/ADR-010-LayoutContainerFreedom|ADR-010]]，无新 ADR）。**同日 14:32 二次调整（业主令）**：`flpToolbar`（文件导入导出区 + 自动刷新 / 刷新IO）**不再置于 `panel1` 顶栏**，移入**独立 `AntdUI.TabPage` `tabPageConfigIO`「导入导出」**（`Dock=Fill`）；`panel1` 只挂 `tabsSystem`（`Dock=Fill`），`tabsSystem` 由 4 分区扩为 **5 分区**。各 Tab 内容分配由业主持续进行。

> 运控调整的人机参数入口，作为 `NavPage`（参数界面实例）的**工艺配置**子页挂载。**2026-09-17 由 `MontionConfigForm`（已废弃，见 [[api/MontionConfigForm]]）整体迁入 `panel1`**：原独立 `SubDialog` 弹窗的「CSV 导入/导出 + 输入/输出 IO 表 + 轴控表 + 气缸表 + 参数编辑器弹窗」四区合一功能，改为本页 `panel1` 内的 4 张 `AntdUI.Table` + 顶部 CSV/XML 工具栏承载（用户决策：信号灯→`CellBadge` 徽标、配置编辑→全加「参数」按钮弹 Modal 编辑 `Delta*Config`、布局→`Panel` 内嵌 `TableLayoutPanel` 并开 `AutoScroll`）。
> 标定参数已迁 `ProcessControlPage.tbpanelweldponts`（⚠️ 2026-10-15 [[decisions/ADR-071-SystemPageGridAndU4Rehome|ADR-071]] 复正：**线激光标定中心 Y/Z、示教 Y 锁定**本轮才迁 `ProcessControlPage.gridWeldPonts`；本页 `gridLaserCalib` 保留线激光角度 + 超时组）；模拟测试已迁 `ProcessControlPage`（ADR-032）；**本页只承载运控 IO/轴/气缸 操作**，不接触 `DeltaMotionConfig` 之外的业务类型。

> **2026-10-08 业主新方案落地（S-10 第二轮）**：`tabsSystem` **4 页 → 3 页** —— `tabPageTrajectoryParam`（**轨迹跟踪参数设置**）· `tabPageLaserHeadParam`（**激光头系统参数设置**）· `tabPageSimTest`（模拟测试）。**温度监测单页已删除**，`panelTempSys`（Dock=Top，高 200）并入激光头页与 `panelOpticsSys`（Dock=Fill）共存。**新增 `panelLaserCalibHost` + `tlpLaserCalib`**（6 列 × 5 行）承载从工艺设置迁入的**线激光标定组 12 控件**（标定中心 Y/Z · 示教 Y 锁定 · 水平轴角度 · 读取/保存按钮），挂在 `tlpTrace` 第 4 行（`RowCount` 3→4）；对应绑定方法 `LoadLaserCalibOnForm` / `BtnSaveLaserCalib_Click` / `BtnReadLaserCalib_Click` 已迁入本页。⚠️ 「激光头系统参数设置」两面板当前**均为占位**（各只 1 个提示标签），TA/LA 电机参数面板待 P3 填。
>
> ⚠️ **2026-10-15 ADR-071 演进**：`tlpTrace`→`gridTrace`（4 行 → 40:fill 各行）、`tlpLaserCalib`→`gridLaserCalib`（**12→9 控件**：标定中心 Y/Z + 示教 Y 锁定 6 件迁工艺设置页 `gridWeldPonts`，本页只留线激光角度 + 读取/保存 + 超时组）、`tbPanelAlogControl`→`gridAlgoControl`、`tbPanelSimTest`→`gridSimTest`；`LoadLaserCalibOnForm` 只回填角度、`BtnSaveLaserCalib_Click` 只写角度（System 区）。
>
> 🔗 **2026-10-15 ADR-072 全链修正**（业主：「先用 Grid 分大区域，再在里面的 Panel 放子 gridpanel 再放置控件」）——三子页统一为 `TabPage→页级Grid→卡片Panel→区内Grid→控件`：
> - **① 轨迹页**：`gridTrace`（`40:fill;1140:fill;340:fill;400:fill` + AutoScroll，行高按原 TLP 绝对值；⚠️ ADR-071 误转 40×4 已修——探针实证 `N:fill`=固定 Npx、裸 `fill`=弹性）→ 4 卡片 `panelToolbarZone`（新，包裸 toolbar→`gridToolbar`）/ `panel2`（→`gridAlgoControl`）/ `panelTraceAxis`（→`gridTraceAxis`→`tableAxis`）/ `panelLaserCalibHost`（→`gridLaserCalib`）；**⚠️ 2026-10-16 三轮演进（业主）**：`gridTrace` 再改 **2×2 大分区 `fill fill;fill fill`**（参考快捷设置等页级范式）——r0 = 轨迹点控制区（`panel2`→`gridAlgoControl`）+ 跟踪轴控制区（`panelTraceAxis`），r1 = 工具条区（`panelToolbarZone`）+ 线激光标定区（`panelLaserCalibHost`），挂载顺序随之重排，**其余两格内容业主后补**
> - **② 激光头页**：新页级 `gridLaserHead`（`200:fill;fill`）→ 卡片 `panelTempSys`（→`gridTemp`）上 / `panelOpticsSys`（→`gridOptics`）下（两占位 Panel 各补区内 Grid，为 U-5/U-6 预留）
> - **③ 模拟测试页**：新页级 `gridSimTestZones`（`fill`）→ 卡片 `panel3`（→`gridSimTest`）

> ⚠️ **2026-10-16 日志常量改名（业主）**：`.cs` 中 `private const string Tag = "系统设置";` 与基类 `UserControl.Tag` 同名导致继承成员被隐藏（CS0108 歧义）⇒ 改名 **`LogTag`**（2 处 `GlobalCommData.ShowLog(LogTag,…)` 同步；`MainPage.LogTag` 同名先例）。

> ⚠️ **2026-10-16 四轮演进（业主：轨迹点控制与线激光标定改「标题+四列」标准，ADR-072/087）**：
> - **`gridAlgoControl`（轨迹点控制区）**：30 行双列 → ~~**18 行**~~ ⚠️ **五轮复正（同日，业主报「参数变少、倒灌进去」）**：四轮目标视觉序三错（段标题逆序 ⑤→① / ⑤区 Mono、OutputHz 两对粘主标题下 / 对内 `txt|lbl` 倒置）⇒ 现 **19 行**（6 分区标题 `40:fill` 单列 + 11 内容四列 + 2 两列[按钮行/单参数行]，54 格零空格），视觉正序 ①线激光点过滤→②方向平滑→③CSP输出→④折返监测→⑤工艺输出、段内 `标签|输入`——resx `gridAlgoControl.Span` 重写 + `Controls.Add` 块 54 行按目标视觉反转重建；校验新判据：段标题序=语义编号序、对内 lbl 先于 txt
> - **`gridLaserCalib`（线激光标定区）**：7 行（角度组两列）→ **6 行** `40:fill;40:fill;30:160×4;40:fill;30:160×4;30:160×4`——视觉序反转恰与原 Add 序**全等** ⇒ 零重排只改 Span；子控件补 `Dock=Fill`

> 🛠 **2026-10-08 缺陷修复（同一轮）**：S-10 第二轮生成 `SystemControlPage.Designer.cs` 的迁移块时，脚本把 **238 行追加到了文件末尾** —— 即「`    }` 类闭合 + `}` 命名空间闭合」**之后**，导致整块代码落在类型之外（CS1022 / CS0116 一片红）。已按语义锚点回填进类体（`new` 区 · `SuspendLayout` 组 · 属性块区 · `ResumeLayout` 组 · 声明区），并一并修掉同轮引入的 4 处缺陷：① `panelLaserCalibHost = new AntdUI.Panel();` 缺失（运行时 NRE）② 其 `Name` 串误写为 `"panel2"` ③ 2 处指向**源页**容器的 `tbpanelweldponts.SetColumnSpan(this.label2/label3, 6)`（CS0103，应为 `tlpLaserCalib` —— 正确行已在 `tlpLaserCalib` 块内）④ `tlpTrace.Controls.Add(this.panelTraceAxis, 0, 2)` 被误搬走。另删 2 段孤立注释（`// lblGeoSecTitle` / `// tabPageWireAlign`）、补 `panelLaserCalibHost.SuspendLayout()`（原有 `ResumeLayout` 无 `Suspend`）。行数 1526 → 1506。判据已入 [[lessons/StaticVerifierJudgements]] §4.7（**生成式改码的落点判据：脚本插入必须锚定在类型体内**）。

## 基本信息

| 项 | 值 |
|----|----|
| 类 | `AdaWeldSystem.UIDesign.TabPage.SystemControlPage`（2026-09-29 由 `MotionControlPage` 更名） |
| 基类 | `UserControl`（AntdUI 无 UIPage 基类，页面以 `UserControl` 承载，由 NavPage 的 `AntdUI.Tabs` 挂载） |
| 文件 | `UIDesign/TabPage/SystemControlPage.cs` + `.Designer.cs`；参数编辑器 `UIDesign/SubDialog/MotionControlDialog/{AxisConfigForm,IoConfigForm,CylinderConfigForm}.cs` |
| 挂载 | `ControlPage/NavPage.cs`：经 NavPage.LoadTabs() 挂载（`uiTabControl1.AddTabSelect(tab)`），节点归参数界面「工艺配置」父节点 |
| 命名空间依赖 | `AdaWeldSystem.MotionControl`、`AdaWeldSystem.MotionControl.IMotion`、`AdaWeldSystem.MotionControl.DeltaEtherCAT`（运行态读取经 `MontionManager.Instance`）；参数编辑器 `AdaWeldSystem.UIDesign.SubDialog.MotionControlDialog` |

## 界面构成（设计器生成，`.Designer.cs`）

> **2026-09-29 四分区（现行）**：`panel1`（`AntdUI.Panel`，`AutoScroll=true`，`Dock=Fill`，`Padding=6`）内 `Controls` **只有 `tabsSystem`**（`Dock=Fill`）。`tabsSystem`（`AntdUI.Tabs`，`Dock=Fill`，`Type = AntdUI.TabType.Card` + `Tabs.StyleCard`，`TabMenuVisible=false`）**四个 `AntdUI.TabPage`**：

| Tab | 控件 | 内容 |
|---|---|---|
| ① 跟踪系统参数 | `tabPageTrajectoryParam` → `gridTrace`（**2026-10-16 三轮演进：2×2 大分区 `fill fill;fill fill`**——r0 轨迹点控制区 `panel2`→`gridAlgoControl` + 跟踪轴控制区 `panelTraceAxis`，r1 工具条区 `panelToolbarZone`→`gridToolbar` + 线激光标定区 `panelLaserCalibHost`→`gridLaserCalib`；原 4 行 `40:fill;1140:fill;340:fill;400:fill`+AutoScroll 已被取代，**其余两格业主后补**；卡片内链 `gridAlgoControl`/`gridTraceAxis`→`tableAxis`/`gridLaserCalib` 不变）；**⚠️ 2026-10-16 四轮：r0/r2 两区改「标题+四列」**（`gridAlgoControl` ~~18 行~~ 19 行（五轮复正）、`gridLaserCalib` 6 行，见上方四轮演进框） | `flpTraceToolbar`（**2026-10-26：`swAutoRefresh`** Switch「自动刷新：开/关」，原 `btnAutoRefresh` Button 已改；⛔ 「刷新轴状态」`btnAxisRefresh` 已整体删除）+ **轨迹点设定**（6 分区）+ **`tableAxis`（只渲染 Y 轴）** + **线激光角度 + 超时组**（标定中心 Y/Z 与示教 Y 已迁工艺设置页，ADR-071） |
| ② 激光头系统参数设置 | `tabPageLaserHeadParam` → `gridLaserHead`（`fill fill;fill fill;40:fill`）→ 4 卡片 + 底部操作条 | **四区（2026-10-21，2026-10-22 控件一致性改造，2026-10-23 振镜使能开关，2026-10-26 ADR-075 LA 四键 + 使能改按钮）**：① `panelTempSys`→`gridTemp`（9 行 24 格，温压+阈值+`swTempRefresh` 刷新开关）· ② `panelOpticsSys`→`gridOptics`（**10 行 32 格**：状态信号 2 行→振镜 9 参（角度/起止角/中心/压缩/目标尺寸/斜椭校正）→末行 **`btnOptGalvoEnable`**（2026-10-26 由 `swGalvoEnable` Switch 改纯图标按钮）+ 回零按钮；图形/宽度/长度/频率 2026-10-23 迁至工艺设置页振镜区）· ③ `panel1`→`gridLa`（原 `gridTaLa`；**2026-11-09 起 8 行 23 格**：LA 状态 → 步距 / **移动目标(mm)（新增输入框）** → 量纲 / 占位 → **末行四键 `btnOptMotorBack`·`btnOptMotorFwd`·`btnOptMotorMoveTo`·`btnOptMotorEnable`（高 44，与 TA 按钮行同高）** → 曲线导入（`btnOptImportCurve` + 点数/说明；**光丝对中警告/报警阈值 2026-11-09 迁至监控相机页参数区**）；原 `swLaMotorEnable` Switch 已删）· ④ `panel4`→`gridWireCurve`（**2026-11-05 起 8 行 32 格**，TA 送丝力矩电机**与①跟踪轴同构**：六项状态 + 移动目标/步距 + 8 图标按钮 NegBack/StepBack/Stop/StepFwd/NegFwd/MoveTo/Home/Servo；**扭矩爬升速率已迁出本页**，见下方「2026-11-05 迁移」节）；底部 `flowPanel2` = 读取参数 / 修改参数 / 保存参数 |
| ③ 模拟测试 | `tabPageSimTest` → `gridSimTestZones`（`fill`）→ 卡片 `panel3` → `gridSimTest` | 自 `ProcessControlPage` 整体迁入的模拟测试（`cmbFreq` / `btnSaveSim` / `btnStartSim`） |

`timerRefresh`（`Interval=500`）为**唯一 UI 计时器**且**常驻不启停**（⛔ 不新增独立温度/电机计时器）；2026-10-26 起其节拍**按内页精确分发**（[[decisions/ADR-075-LaserHeadUiControlConsistency]]）：**前置条件①** `IsMotionReady()` 不满足 ⇒ 五个刷新开关自动回退 `Checked=false`（重连恢复默认 ON）；**前置条件②** `IsRefreshPageVisible()`（`Visible`）不满足 ⇒ 只跳过刷新；两者均通过后 —— 激光头页（`LaserHeadTabIndex=1`）按四区开关分别刷 振镜/LA/TA/温度，轨迹页（`TraceTabIndex=0`）按 `_autoRefresh` 刷轴表；⛔ 不用 `else` 兜底（模拟测试页不属于任何刷新区）。~~原 `CanRefreshNow() = 未 Dispose && this.Visible && IsMotionReady()` 三条件合并式~~ 已按 §五 修订废除。

## 权限门控（S-11，2026-10-08 落地）

| Tab | 可见性 | 写权限 |
|---|---|---|
| ① 轨迹跟踪参数设置 | 所有人 | 所有人 |
| **② 激光头系统参数设置**（`panelOpticsSys` + `panelTempSys` 同页） | **仅 `OperateLevel.Admin`** | **仅 Admin** |
| ③ 模拟测试 | 所有人 | 所有人 |

三层防线（**隐藏 ≠ 禁用**，P1 §4.3）：

| 层 | 实现 | 防的是 |
|---|---|---|
| 显示层 | `ApplyPermissionGate()`：`tabPageLaserHeadParam.Visible = admin` + `panelOpticsSys/panelTempSys.Enabled = admin` | 非管理员看到已回填的敏感值 |
| 进入层 | `tabsSystem_SelectedIndexChanged` → `EnsureAdminForWrite("进入激光头系统参数设置页")`，拦下即回退 `SelectedIndex = 0` | `Visible=false` 后仍靠索引停在该页 |
| 写入层 | `EnsureAdminForWrite(action)`：`AntdUI.Message.warn` + `权限拒绝：` 日志（`MessageLevel.Warning`） | 绕过 UI 直接改配置 |

门控在两时机重算：构造函数末尾（首次打开）+ `GlobalCommData.OperateLevelChanged`（登录/注销即时生效）。⛔ 订阅在 `DisposeComponents()` 显式退订。权限来源与等级职责见 [[api/GlobalCommData]]，导航项显隐与状态栏标签见 [[api/FormMain]]。

> ✅ **2026-11-17 模拟测试启动加管理员门控（ADR-105，阶段 8）**：`BtnStartSim_Click` 在「停止 / 清理异常」分支之后、`StartSimulation()` 之前插入 `EnsureAdminForWrite("开启模拟测试")`——**启动仅管理员**；停止与清理属安全动作，不加门控。模拟状态为运行期瞬态（不落盘），重启后默认关闭，无需新增配置键。

> ✅ **2026-10-21 电机区落地后**：底部三按钮 = 读取参数（配置→界面）/ 修改参数（界面→内存，不落盘不下发）/ 保存参数（内存→落盘+下发设备）；
> 写/动作入口接 `EnsureAdminForWrite`：修改、保存、LA 使能、LA 步进、**LA 移动到目标**、TA 使能/移动到/步进/点动/回零、**振镜使能/撤销使能**、振镜回零、曲线导入；**TA 停止为安全操作不门控**，读取与五个「自动刷新」开关（四区 + 轨迹页轴表）不门控（开关只切刷新节拍）。
> TA 控制与①跟踪轴一致：`BtnTaMoveTo_Click`→`DoAbsolute`、`BtnTaStepBack/Fwd_Click`→`StepTa`→`DoRelative`；状态判据同 `FillAxisRuntime`（`GetStatusWord` 0x0004/0x0008、软限位、`|pos|≤ε`、`LastCommand`）。
> ⚠️ `BtnSaveLaserCalib_Click` / `BtnSaveAlgoThresh_Click` 属**①轨迹页**（所有人可写），⛔ 不得误加 Admin 门控。

> ⛔ **已删除的旧容器/控件（2026-09-29）**：`panelInner`（`TableLayoutPanel` 1 列 × 5 行）；`tabPageInputIO` / `tableInputIO`、`tabPageOutputIO` / `tableOutputIO`、`tabPageCylinder` / `tableCylinder`、`tabPageConfigIO` / `flpToolbar`（含 `txtCsvDir` / `btnBrowseDir` / `btnImportCsv` / `btnExportCsv` / `btnSaveConfig` / `btnReloadConfig`）、独立 `tabPageAxis`。`btnIORefresh` → **`btnAxisRefresh`（Text「刷新轴状态」）** → ⛔ **2026-10-26 该按钮整体删除**（业主裁定：已有自动刷新启停，手动刷新冗余；见 [[decisions/ADR-075-LaserHeadUiControlConsistency]] §六）。

> ⚠️ **配置列与运行列分离**（沿用 [[api/MontionConfigForm]] 既有原则，已随迁移一并迁入）：配置列取自 `DeltaMotionConfig.Axes/Inputs/Outputs/Cylinders`（离线可编可存盘）；运行列取自 `MontionManager.Instance.Axes/IOs/Cylinders`（运行时对象，只读秒级刷新）。`DeltaAxisConfig.NodeId/SlotNo/Enabled/PositiveLimit/NegativeLimit` 是配置项，`MontionAxis` 上根本没有这些字段——只有 `AxisNo`。混用两链会 CS1061（见 [[api/MontionManager]]）。

## 轴表与行模型（2026-09-29 后仅存 Y 轴表）

> ⛔ **IO / 气缸三表已于 2026-09-29 取消**（业主裁定「后续回归为各个系统参数设置」），行模型 `IORow` / `CylinderRow` 已删；IO/气缸配置仍由 `DeltaMotionConfig` 承载并可经 [[api/FilebackupPage]] 的 CSV 导入导出维护。

`tableAxis`（`AntdUI.Table` + `AntdUI.AntList<AxisRow>` 强类型绑定，禁用 DataGridView），列定义在代码后置 `InitTables()` 内写入（`Designer.cs` 不赋 `ColumnCollection`）。

| 表 | 行模型 | 列数 | 关键列 | 信号灯(CellBadge) | 按钮(CellButton) |
|----|--------|------|--------|-------------------|------------------|
| `tableAxis` | `AxisRow` | 19 | AxisName/Position/6×信号灯/8×按钮/步距(可编辑)/TargetPos(可编辑)/ParamBtn | PositiveLight/NegativeLight/OriginLight/AlarmLight/ServoLight（未连接=TState.Default灰） | StepBack/StepFwd/负向/正向/MoveTo/Home/Stop/Servo/ParamBtn（按钮去文字，占位符号，待示例定稿；负向/正向为按住连续JOG，按步距后退/前进为单击离散点动） |

**只渲染 Y 轴（2026-09-29，业主裁定）**：
```csharp
private static readonly string[] TraceAxisKeys = { "Y", "横梁", "跟踪" };
// LoadAxisRows() 内逐轴 IsTraceAxis(cfg) 过滤，未命中关键字的轴不进表
```
> 语义：Y 轴属**跟踪系统的轴**（焊缝跟踪闭环的执行轴），故与轨迹点设定同处「跟踪系统参数」页；送丝 / 对焦等轴后续归「光丝系统参数」页，不在本表渲染。

**行模型三原则**：
1. **信号/按钮用 AntdUI 内建单元格类型**——信号灯属性为 `CellBadge`：连接后有信号=`TState.Success`绿 / 无信号=`TState.Error`红 / **未连接·未装配·未配置=`TState.Default`灰**；按钮列属性为 `CellLink[]` 内嵌 `CellButton(Guid, text, TTypeMini)`，当前 `text` 为**去文字的占位符号**（◀ ▶ « » ⊙ ⌂ ■ ⏻ ⚙ ● ○ → ←，派发仍按 `e.Btn.Text` 匹配），待用户示例定稿后替换为正式图标；点击统一走 `CellButtonClick`，按 `e.Btn.Text` + `e.Record`（cast 行模型）派发。**负向(«)/正向(») 为按住连续 JOG**：`CellButtonDown` 启动 `JogMove(dir)`、松开 `CellButtonUp` 或表内 `MouseUp` 经 `StopJog()`→`AxisStop((ushort)StopMode.Deceleration)` 停止；点动期间不触发 `CellButtonClick`（派发中已移除这两个符号的 Click 分支）。
> 🔄 **2026-09-29 起仅 `AxisRow` 适用**；`IORow` / `CylinderRow` 随三表一并删除（IO/气缸配置仍经 CSV 导入导出维护，入口见 [[api/FilebackupPage]]）。
2. **携带回写目标**——`AxisRow` 带 `DeltaAxisConfig`；`CellEndEdit`（可编辑列 步距 / TargetPos）校验通过后直接写回配置实例（ADR-022 单一真相源）。
3. **配置列与运行列分离**（见上）。

表设置：`EditMode = AntdUI.TEditMode.DoubleClick` + 可编辑列 `.SetEditable(true)` + `AutoSizeColumnsMode = AntdUI.ColumnsMode.Fill`，与 [[modules/UIDesign]] 记载的 `ILParamForm.cs` / `AutoParamForm.cs` 同款范式。

> ⚠️ **空态必须强制显式表头**（2026-09-18 14:21:23 修正）：AntdUI `Table` 绑定**空** `AntList<T>` 时走空态覆盖层并**隐藏列头**（"列定义常驻即渲染表头"为误判）。IO/气缸表无导入配置即空态，故每个 `Binding(list)` 之后必须 `EmptyHeader = true; VisibleHeader = true;`。`RefreshRuntime()` 中 500ms 定时器每次重绑后也再次断言该两属性，否则表头会被重绑重新隐藏。

## 关键方法

| 方法 | 说明 |
|------|------|
| `SystemControlPage()` | ctor：`InitializeComponent()` → `InitTables()`（`tableAxis` 列定义 + Binding）→ `BindEvents()` → `LoadAll()` |
| `InitTables()` | 轴表列定义（`new AntdUI.Column(key, 标题) { Width = "…" }` + 可编辑列 `.SetEditable(true)`）+ `EditMode` / `AutoSizeColumnsMode` + `Binding(_axisRows)`；**`Binding` 后立即追加 `EmptyHeader = true; VisibleHeader = true;`** |
| `BindEvents()` | 事件**代码后置订阅**（⛔ 不在 Designer 重复绑定，否则一次点击触发两次）：`tableAxis`→`TableAxis_CellButtonClick`；`CellButtonDown`/`CellButtonUp`/`MouseUp`；**五个刷新开关的 `CheckedChanged`**（四区 + `swAutoRefresh`，并同步标志初值）+ `timerRefresh.Tick` |
| `LoadAll()` | 顺序重载：`LoadAlgoThreshOnForm()`（轨迹点设定）→ `LoadAxisRows()`（**只渲染 Y 轴**） |
| `IsTraceAxis(DeltaAxisConfig)` | 轴名关键字过滤 `{ "Y", "横梁", "跟踪" }`（大小写不敏感），未命中不进表 |
| `FillIoLight(IORow)` / `FillAxisRuntime(AxisRow)` / `FillCylinderRuntime(CylinderRow)` | 逐行读取运行态写入 CellBadge，全部 `try/catch` 兜底为「读取失败」（UI 不得因单点读取异常整体崩） |
| `TableIO_CellButtonClick` | 输入/输出 IO 共用：`OnButton`/`OffButton`→`OutputIO.SetON()/SetOFF()`（选中输入时提示「选中的是输入信号，不能置位」）；`参数`→`OpenIoEditor(row)` |
| `TableAxis_CellButtonClick` | `StepBack`/`StepFwd`→`DoRelative(axis, ±step)`（单击离散点动，按步距移动一次）；`MoveTo`→`DoAbsolute(axis, pos)`；`Home`→`HomeNoBlock()`；`Stop`→`AxisStop((ushort)StopMode.Deceleration)`；`Servo`→`ToggleServo(axis)`；`参数`→`OpenAxisEditor(row)` |
| `TableAxis_CellButtonDown` / `TableAxis_CellButtonUp` / `TableAxis_MouseUp` | 轴 JOG（按住连续移动，松开停止）：Down 命中 `负向(«,dir=1)`/`正向(»,dir=0)`→`JogMove(dir)` 启动并置 `_jogging`/`_jogAxis`；Up 或表内 `MouseUp`→`StopJog()`→`AxisStop((ushort)StopMode.Deceleration)` 停止并复位状态（`BindEvents` 已订阅 `CellButtonDown`/`CellButtonUp`/`MouseUp`） |
| `TableCylinder_CellButtonClick` | `Stretch`→`Cylinder.Stretch()`；`Retract`→`Cylinder.Retract()`（⚠️ 传感器语义陷阱见下）；`参数`→`OpenCylinderEditor(row)` |
| `OpenAxisEditor` / `OpenIoEditor` / `OpenCylinderEditor` | `AntdUI.Modal.open(new AntdUI.Modal.Config(this.FindForm(), title, control, TType.Info))` 弹参数编辑器（`AxisConfigForm`/`IoConfigForm`/`CylinderConfigForm`，命名空间 `AdaWeldSystem.UIDesign.SubDialog.MotionControlDialog`）。**2026-11-17 起**：轴参数弹窗的写回由弹窗内「确定」完成，宿主按 `editor.Committed` 落盘（⛔ 不用 `Modal.open` 返回值判定）；IO/气缸编辑器仍为 OK 则 `Commit()` + 重载对应表 |
| `SwAutoRefresh_CheckedChanged` / `TimerRefresh_Tick` | 轨迹页轴表自动刷新（原 `BtnAutoRefresh_Click`，**2026-10-26 由 `Click` 改 `CheckedChanged`**、载体 Button→Switch）：只写 `_autoRefresh` 标志并立即刷一次；**⛔ 不再调用 `timerRefresh.Start()/Stop()`** —— 计时器常驻，启停由标志控制（与四区同范式）。`TimerRefresh_Tick` 在轨迹页精确匹配下走 `RefreshRuntime()` 重建轴表运行列后重绑（只刷运行列，不动配置列） |
| `ApplyRefreshSwitchGate()` / `GateRefreshSwitch(toggle, ref flag, ready)` | **2026-11-09 新增**：五个刷新开关的**唯一门禁入口**，按设备粒度判就绪——轴表看 `IsMotionZoneReady()`、LA/振镜/温度看 `IsLaZoneReady()`（`MotionControlWorkflow.LaReady`）、TA 看 `IsTaRefreshReady()`（运控完成 + TA 轴已装载）。未就绪 `Enabled=false` 且强制 `Checked=false`；就绪只解冻、⛔ 不自动开启（默认关闭）。触发点：`OnMotionStateSwitched` / `OnInitializationCompleted` / `OnInitializationSummaryReady` / `OnAxisReadyChanged` |
| `CollectRefreshSnapshot` / `ApplyRefreshSnapshot` | **2026-11-09 新增**：定时刷新改为「后台线程采集纯数据快照 → `BeginInvoke` 回 UI 线程赋值」，`_refreshBusy` 单飞防任务堆积；`RefreshTemperatureValues` / `RefreshGalvoStatus` / `RefreshLaMotorStatus` / `FillAxisRuntime` 全部改为 `Collect*` + `Apply*` 两段，同一套逻辑供同步入口与定时刷新复用 |
| `OnInitializationSummaryReady(object, DeviceInitSummaryEventArgs)` | **2026-11-09 新增**：订阅 `DeviceControlWork.InitializationSummaryReady`，刷新开关门禁重算；有 `SkippedCount > 0` 时 `Warn` 逐个列出「被谁挡住、未发起连接」，提示先修上级 |
| ~~`BtnAxisRefresh_Click`~~ | ⛔ **2026-10-26 删除**（业主裁定：已有自动刷新启停，手动刷新冗余）。删除后 `LoadAxisRows()` 仍余 2 处消费者：构造函数 `LoadAll()` + `OpenAxisEditor` 保存后重载 ⇒ 配置编辑后仍会重建行 |
| `LoadAlgoThreshOnForm()` / `BtnSaveAlgoThresh_Click` / `BtnReadAlgoThresh_Click` | **2026-09-29 自 `ProcessControlPage` 迁入的轨迹点设定**（19 项阈值：点过滤 9 / 方向平滑 4 / CSP 输出 4 / 折返 2），保存走 `WeldParamManager.Instance.SaveAlgorithmsConfig()`，读取仅回填本区 |
| `BtnStartSim_Click` / `OnSimulationStopped` / `OnMainDeviceStatusChanged` / `CleanupSimError` … | **2026-09-29 自 `ProcessControlPage` 迁入的模拟测试全套**（语义零改动，见 [[decisions/ADR-032-SimulationTestRedesign]]） |

> ⛔ **2026-09-29 已迁出至 [[api/FilebackupPage]]「系统配置文件」页**：`BtnImportCsv_Click` / `BtnExportCsv_Click`（`MotionConfigImporter`）与 `BtnSaveConfig_Click` / `BtnReloadConfig_Click`（`DeltaMotionConfig.SaveConfig()` / `LoadConfig()`）。

## 超时设置卡片（`panelTimeout` / `tLPTimeout`，2026-11-13 落地）

**位置**：系统设置页 →「流程控制与测试」页签 → `panelTimeout` 卡片 → `tLPTimeout`（4 列 × 12 行 `TableLayoutPanel`，列宽 Absolute 160，末尾 AutoSize 空行吸收余高）。
**标题**：`lblTimeoutTitle` =「流程与设备等待超时」；两段分组：`lblGroupFlowWait`「流程等待」/ `lblGroupDeviceWait`「设备侧等待」。

| 分组 | 字段（控件名 → 配置项） |
|---|---|
| 流程等待 | `txtInstrDetect`→`InstructionDetectSeconds` · `txtInstrSample`→`InstructionSampleMs` · `txtMoveDone`→`MoveDoneSeconds` · `txtHomeDone`→`HomeDoneSeconds` · `txtServoOn`→`ServoOnSeconds` · `txtZeroPoseWait`→`PositionReachResultWaitSeconds` · **`txtMasterInit`→`MasterInitSeconds`（2026-11-13 新增）** |
| 设备侧等待 | `txtDataStable` / `txtWaitWorking` / `txtFirstResult`（`LineLaserConfig` 三项）· `txtCameraAcquire`→`CameraAcquireSeconds` · `txtRecordFlush`→`RecordFlushSeconds` · `txtLineLaserCallback`→`LineLaserCallbackMs` · `txtModbusConnect`→`ModbusConnectMs` · `txtModbusRW`→`ModbusReadWriteMs` |

**接线（三段式，与 ADR-076 一致）**：
- **读取**：`LoadTimeoutOnForm()` 回填 UI（构造期与「读取参数」按钮各调一次）；
- **修改**：`BtnApplyParams_Click` 写 `MontionManager.Instance.FlowTimeouts` 内存对象（**不落盘**）；
- **保存**：`BtnSaveLocal_Click` → `MontionManager.ApplyFlowTimeouts()` → `Normalize` 值域校验 → `FlowTimeoutSettings.Publish` 运行期快照生效 → `config.SaveConfig()` 落盘 `ROOT/FLOW_TIMEOUT/*`。

> **`MasterInitSeconds`（主站初始化超时，秒）**：2026-11-13 新增暴露。消费者 `DeltaMontionControl.InitialTimeoutSeconds`（读 `FlowTimeoutSettings.Current`），用于 `WaitInitialDone` 的主站初始化等待上限；值域 `[5,300]`，缺省 30，配置键 `ROOT/FLOW_TIMEOUT/MASTER_INIT_SECONDS`。
> ⚠️ 调大此值**不能**修复主站初始化失败：`CS_ECAT_Master_Initial` 返回非 0 时已立即失败并上报返回码（2026-11-13 修正），超时只在厂商调用确实长时间未完成时才是原因。

## 轴 JOG（按住连续移动，松开停止）

轴表方向控制分两类运动模式（**2026-11-08 起经 `MotionControlWorkflow.TryManualAxisOperation` 分发**，UI 不持轴对象）：

- **单击离散点动**：`按步距后退(◀)` / `按步距前进(▶)` → `CellButtonClick` 派发 → `DoRelative(±步距)` → `AxisManualOperation.StepMove`。
- **按住连续 JOG**：`负向(NEGATIVE, «)` / `正向(POSITIVE, »)` → `CellButtonDown` → `AxisManualOperation.JogStart`，`CellButtonUp` 或表内 `MouseUp` → `AxisManualOperation.JogStop`。

> **行为语义**（用户 2026-09-18 澄清）："轴有 NEGATIVE 负向和 POSITIVE 正向移动——点击对应按钮轴移动（按下不抬起），抬起后轴运动停止"。
> **安全网**：`_jogging` 记录点动态（`_jogAxis` 已删除）；表内 `MouseUp` 兜底处理"按下后拖离按钮再释放"；`停止(■)` 始终可强制停止。

## 轴状态字与信号灯推导

- **UI 不再解析状态字**（2026-11-08，ADR-093 决策七）：`RefreshAxisRow` 调 `MontionManager.TryGetAxisReadout(axisName, out pos, out lastCommand, out servo, out fault)`，只消费 `servo/fault` 布尔摘要。
- `MontionAxis` **无独立正/负限位/原点位**——`FillAxisRuntime` 由「当前位置 `pos` vs 配置软限位 `DeltaAxisConfig.PositiveLimit/NegativeLimit`」推导；原点 = `|pos| ≤ ε`。
- 信号灯一律 `CellBadge`：`ServoLight` 取 `servo`；`AlarmLight` 取 `fault`；`PositiveLight/NegativeLight` 取位置是否越/达软限位；`OriginLight` 取原点判据。**三表统一**：未连接 / 轴未装配 / 气缸未配置传感器时，对应信号灯一律置 `TState.Default` 灰（不再误显红）。

## ⚠️ Cylinder 传感器语义陷阱

`Cylinder.IsInStretch()` / `IsInRetract()` / `IsInCenter()` 对**未配置传感器**一律返回 `true`（源码 `return InXxxSensor == null || InXxxSensor.IsON();`）。故 `FillCylinderRuntime` 必须**先判传感器是否存在**再判到位，否则未接传感器的气缸会谎报「已伸出」：
```csharp
bool hasSensor = cylinder.InStretchSensor != null
    || cylinder.InRetractSensor != null
    || cylinder.InCenterSensor != null;
if (!hasSensor) { StretchLight/CenterLight/RetractLight = 灰/未知; return; }
```

## 参数编辑器（3 个 UserControl，纯代码构建）

| 编辑器 | 命名空间 | 构造 | 字段 | `Commit()` |
|--------|---------|------|------|-----------|
| `AxisConfigForm` | `AdaWeldSystem.UIDesign.SubDialog.MotionControlDialog` | `(DeltaAxisConfig config)` | AxisName(只读)+NodeId/SlotNo/Enabled(CheckBox)/Equiv/MinVel/MaxVel/AccTime/DecTime/STime/StopVel/HomeMode/HomeDir/HomeMaxVel/PositiveLimit/NegativeLimit | ushort/double 解析失败保留原值（`CultureInfo.InvariantCulture`） |
| `IoConfigForm` | 同上 | `(DeltaIOConfig config)` | IOName(只读)+NodeId/SlotNo/BitNo/Enabled(CheckBox)/Remark | 同上 |
| `CylinderConfigForm` | 同上 | `(DeltaCylinderConfig config)` | CylinderName(只读)+StretchSensorName/RetractSensorName/CenterSensorName/StretchOutputName/RetractOutputName/StretchActionName/RetractActionName | `TrimOrEmpty` 写回（空串=未配置点位） |

三编辑器均**无 Designer**，纯代码 `TableLayoutPanel`(2 列) + 文本控件构建；`Commit()` 把文本写回传入的 `*Config` 引用。

> ⚠️ **2026-11-17 修复**：`AxisConfigForm.Commit()` **必须由弹窗内部「确定」按钮触发**（控件存活期），宿主 `OpenAxisEditor`/`OpenTaAxisEditor` 只按 `editor.Committed` 标志决定是否落盘。
> ⛔ 不得把 `Commit()` 放在 `Modal.open(...)` 返回之后：AntdUI `LayeredFormModal.DestroyHandle()` 会 `config.Content.Dispose()`，内容控件连同 TextBox 已销毁，再读 `_txtXXX.Text` 只会得到旧值（写回等于没改），且 `== DialogResult.OK` 判定失败会整段跳过落盘。详见 [[lessons/AntdUI-Modal-Content-Disposed-Before-Commit]]。

## 设计约束

- ADR-002（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）：`.Designer.cs` 标准 `Dispose(bool)`（经 `DisposeComponents()` 释放 `timerRefresh`/事件订阅），`.cs` 未重写 `Dispose(bool)`。
- [[decisions/ADR-001-CS73-Constraint]]：无 `switch` 表达式 / `??=` / `is not` / `record` / `init` / `using var` / 范围运算符；属性初值写构造函数。
- [[guides/WinForms-Designer]]：控件声明与布局全在 `.Designer.cs`；`InitializeComponent()` 内**无控制流**。
- [[guides/Namespace-Compilation]]：命名空间随目录对齐（ADR-005）；`SystemControlPage.cs` 命名空间 `AdaWeldSystem.UIDesign.TabPage`；3 个编辑器命名空间 `AdaWeldSystem.UIDesign.SubDialog.MotionControlDialog`，均在 csproj 登记 `<Compile Include>`。
- **Modal owner**：用 `this.FindForm()`（与 `ILParamForm.cs`/`ILCamPage.cs`/`HelixRenderForm.cs` 既有先例一致），`AntdUI.Modal.Config(Form, …)` 接受 `Form`。
- **日志**（ADR-007）：`Tag = "运控配置"`，直连 `GlobalCommData.ShowLog`，纯文本无符号，操作起止/结果处记录。

## 协作

- 导入 / 导出通道：`MotionControl/DeltaEtherCAT/MotionConfigImporter.cs`（[[api/MontionManager]] 同模块，ADR-022/038）。
- 配置真相源：`DeltaMotionConfig`（`Config/MotionControl/Motion_XML/DeltaMotionConfig.xml`，由 `MoveControlData` 持、[[api/MontionManager]] 单点对外）。
- 运行态：`MontionManager.Instance` → `Axes`/`IOs`/`Cylinders` 注册表（`AxisRegistry`/`IORegistry`/`CylinderRegistry`）。
- 容器：[[modules/UIDesign]] 的 `NavPage` 参数界面实例（ControlPage）。
- ⛔ **2026-09-29 迁出**：CSV/XML 导入导出区（`flpToolbar` 整条）→ [[api/FilebackupPage]]「系统配置文件」页；IO / 气缸三表取消（待回归各系统参数页）。
- 🔄 **2026-09-29 迁入**：轨迹点设定（19 项阈值）← [[api/ProcessControlPage]]；模拟测试全套 ← `ProcessControlPage`。
- 更名沿革：`MotionControlPage` → `SystemControlPage`（2026-09-29，仅更名 + Tabs 分区，业务零改动）
- 前身（已废弃）：[[api/MontionConfigForm]]（2026-09-17 内容整体迁入本页 `panel1`）。

---

*来源：AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs + .Designer.cs + SubDialog/MotionControlDialog/{AxisConfigForm,IoConfigForm,CylinderConfigForm}.cs*


## 2026-10-19 六轮演进（⑤迁出 · 轴按钮迁出 · 统一读存 · out var 精简）

⚠️ 本框内容**取代**下方界面构成中「tableAxis 19 列控制列」「轨迹点设定区读取/保存按钮」「⑤工艺输出」相关描述：

1. **⑤工艺输出 11 控件迁出**（数据收编 WeldParamAdjustmentAlgorithm + WeldParamManager facade，UI 迁
   ProcessControlPage 自适应区）：`LoadAlgoThreshOnForm/BtnSaveAlgoThresh` 的 ⑤ 读写与 Adapt 落盘删除，
   `BtnSaveAlgoThresh/BtnReadAlgoThresh` 处理器整体删除（ADR-072 §三②）。
2. **轴表 19→11 列**：8 控制列（步距后退/前进·负向/正向·移动·回零/停止/使能）自 `tableAxis` CellLink 迁出为
   `gridTraceAxis` 固定按钮（`ServoBtn/HomeBtn/MoveToBtn/NegFwdBtn/StepFwdBtn/StopBtn/StepBackBtn/NegBackBtn`，
   `BindEvents` 后置订阅×12，Jog `MouseLeave` 拖离兜底）；`AxisRow` 9→1 `CellLink`；`Sym*` 9→1（仅 SymParam）；
   `TableAxis_CellButtonClick` 仅剩参数列 → `OpenAxisEditor`；控制全走 MontionManager 六函数（ADR-073），
   本页固定轴 = `GetAxisByKeys(TraceAxisKeys)`，步距/目标取首行 `GetFixedRow()`。
3. **统一读存三按钮**：`button1/2/3`（`BindEvents` 订阅 `BtnReadLocal_Click/BtnApplyParams_Click/BtnSaveLocal_Click`）
   替代 3 对 6 个分区按钮（`btnRead/SaveAlgoThresh`、`btnRead/SaveLaserCalib`、`btnRead/SaveTimeout`
   四形态删净、6 旧处理器整删）——读取=双加载三回填；应用=22 项 UI→内存**不落盘**；保存=
   `SaveAlgorithmsZone(System)` + `LineLaserManager.SaveConfig()` 双落盘（只存已应用配置）。
   `gridCspControl` 17→15 格、`gridLaserCalib` 15→11 格（混行重排，挂载=格数零空格）。
4. **req4 精简**：`ParseStep/ParseTarget/ParseCalibDouble/ParseInt/CellEndEdit` 预声明 → `out var`。

## 2026-10-22 激光头页控件一致性（ADR-075）

| 项 | 现行实现 |
|---|---|
| 切换类控件 | ~~`swTempRefresh`（温度自动刷新）/ `swLaMotorEnable`（LA 对焦电机使能）/ `swGalvoEnable`（振镜使能）均为 `AntdUI.Switch`；`CheckedChanged` 在 Designer 单点订阅；程序回写经 `_syncingSwitch` 抑制（防 500ms 刷新触发设备动作），失败/无权限回退原状态~~ ⚠️ **2026-10-26 经 [[decisions/ADR-075-LaserHeadUiControlConsistency]] 演进**：本行仅 `swTempRefresh` 继续有效；两个**使能**开关改按钮（`btnOptMotorEnable`/`btnOptGalvoEnable`），订阅移至 `BindEvents()`，`_syncingSwitch` 整组删除 —— 现行实现见本页末「2026-10-26」节 |
| TA 送丝力矩电机 | `gridWireCurve` 8 图标按钮（TaNegBack/TaStepBack/TaStop/TaStepFwd/TaNegFwd/TaMoveTo/TaHome/TaServo）与 Y 轴同序同图标；六项状态同 `FillAxisRuntime` 判据；控制走 `MontionManager` 六函数；`BindEvents` 后置订阅×12 + Tooltip |
| 振镜卡片 | 顺序=标题→状态信号（振镜使能/驱动板）→设置→按钮；状态读 `WeldHeadSlaveDevice.ReadAlarmStatus()`（0x6010 `GalvoOn`/`DriverAlarm`），随刷新节拍刷新；末行两列 = ~~`swGalvoEnable`（振镜使能 Switch）~~ ⚠️ **2026-10-26 改 `btnOptGalvoEnable`（纯图标按钮）** + `btnOptGalvoHome`；焊接中按钮置灰，非焊接时读当前 `GalvoParams` 后只翻转 `GalvoEnable` 写回 |
| 按钮样式 | LA/振镜/底部三按钮/TA 8 键统一：`Ghost=true` + `Cursor=Hand` + 宋体 12F + `BackHover(3,169,244)` + `IconSvg`，不再用 `Type=TTypeMini.Primary` |
| 线激光点过滤（2026-10-23） | `gridFitterControl` 线激光点过滤组新增「焊缝地图点数上限」`txtGeoMaxMapPoints`（自工艺设置页 `gridWeldPonts` 迁入，读写 `WeldAlgorithmsConfig.MaxMapPoints`） |

> 决策与备选方案见 [[decisions/ADR-075-LaserHeadUiControlConsistency]]；轴控制入口沿用 [[decisions/ADR-073-AxisControlUnifiedMontionManager]]。

**2026-10-19 七轮演进（GetFixedAxis 语义修正 + Tooltip）**：
- `GetFixedAxis(string action)` 重命名为 **`GetTraceAxis(string actionLabel)`**：旧参数名 `action`（"切换伺服"/"回零"/"点动" 等**动作名**）完全误导——函数实际按页角色关键字 `TraceAxisKeys` 查轴，`action` 仅拼接警告文案。返回类型从基类 `MontionAxis` 改为 **`DeltaMontionAxis`**（Y 轴 + 送丝轴均为台达实现，取具体类型；MontionManager 六函数参数是基类，子类隐式转换兼容）。内部调用从 `GetAxisByKeys` 改为 **`GetDeltaAxisByKeys`**（ADR-066 台达轴查找入口早已就绪）。
- 6 调用点（Servo/Home/Stop/MoveTo/Step/Jog）同步：`MontionAxis axis = GetFixedAxis("xxx")` → `DeltaMontionAxis axis = GetTraceAxis("xxx")`。
- 8 固定按钮（ServoBtn/HomeBtn/MoveToBtn/NegFwdBtn/StepFwdBtn/StopBtn/StepBackBtn/NegBackBtn）补齐 ToolTip：沿用项目已验证的 **`AntdUI.TooltipComponent` 单实例 + `SetTip(control, text)` 两参重载**（范式见 MainPage/DataReviewerPage）；TooltipComponent 在 `DisposeComponents()` 内 Dispose。

## 2026-10-23 参数读存与分区落盘接线修正（ADR-076）

| 缺陷 | 现象 | 修正 |
|---|---|---|
| **焊缝地图点数上限不落盘** | `BtnApplyParams_Click` 把 `MaxMapPoints` 写进内存（控件 `txtGeoMaxMapPoints` 在 `gridFitterControl`「线激光点过滤」组），但 `BtnSaveLocal_Click` 只落 **①System 区**，而该项 XML 归属 **④Preset 区**（`SEAM_GUIDE/MAX_MAP_POINTS`）⇒ 点「保存参数」弹「已保存」，重启回旧值 | **配置项分区归属随 UI 落点迁移**：该项由 ④Preset 改 **①System**（XML 键路径不变、存量文件兼容），Preset 区不再写该键 |
| **「读取参数」名不副实** | `BtnLhRead_Click` 只读**内存**（`WeldHeadConfig` / `DeltaAxisConfig` / `WireFeedConfig`），`MontionManager.LoadWeldHeadConfig()` **0 调用方** ⇒ 现场改了文件看不到效果 | `BtnLhRead_Click` 先调 `MontionManager.Instance.LoadWeldHeadConfig()` 再回填 |
| **跨页副作用** | 系统设置页「保存参数」顺带落 **④Preset 区**（工艺设置页的区：Tracking 几何 / LA·TA 预设 / 振镜图形）⇒ 把工艺设置页「仅修改未保存」的值提前写盘 | `SaveLaserHead()` **不再落 ④Preset 区**（本按钮只写 `WeldHeadSlave.xml` + 运控轴配置） |
| **解析口径不一** | 同页 `ParseCalibDouble`（当前文化）与 `TryReadDouble`（不变文化）并存 | `ParseCalibDouble`/`ParseInt` 改为复用 `TryReadDouble`/`TryReadInt`，口径统一为 **InvariantCulture 优先 → 当前文化回落 → 失败保留原值**（与工艺设置页一致） |
| **轴表刷新清空用户输入** | 点「刷新轴状态」或编辑完轴参数回来，已填的「步距 / 移动目标」被静默清零（`LoadAxisRows()` 重建行时写死 `"1"`/`"0"`） | `LoadAxisRows()` 按轴名快照并回填旧行的 `LayoutValue`/`TargetPos` |

**三按钮语义（不变）**：读取（文件 → UI，含 `LoadAlgorithmsConfig` + `LoadWeldHeadConfig` + 线激光 `LoadConfig`）/ 修改（UI → 内存，不落盘）/ 保存（内存 → 文件，**①System 区** + 线激光配置）。

> ℹ️ **2026-11-19 ADR-076 D8**：本页「流程控制与测试」TabPage 的 5 个工艺启用开关（`swEnableAdapt` / `swEnableGalvoWeaveQuick` / `swEnableSeamTrace` / `swEnableWireAlign` / `swEnableTempCtrl`）已拆为独立的 **②′ Flow 区**（`AlgorithmsZone.Flow`），落盘走**独立 INI 文件** `WeldParamControlAlgorithmFlow.ini` ⇒ 与工艺页共用 `PROCESS_CONTROL` section 的键互不覆盖；本页「轨迹跟踪参数设置」TabPage 的跟踪阈值归 `WeldParamControlAlgorithmTrajectory.ini`。
>
> ℹ️ **2026-11-18**：`headCfg.DefaultGalvo` 类型由 `GalvoParams` 改为 **`GalvoGlobalParams`**（只含全局项；图形与宽/长/频已清理掉，见 [[decisions/ADR-070-GalvoWeaveAsWidthSource]] §五）—— 本条描述的 `DefaultGalvo.XCenter/YCenter` 字段名不变，结论不受影响。
>
> ⚠️ **仍待业主裁决**：**振镜中心 X/Y**（`txtOptGalvoXCenter`/`txtOptGalvoYCenter`）写入 `headCfg.DefaultGalvo.XCenter/YCenter`，而生产链路 `LaserWeldHeadWorkflow.ApplyGalvoAmplitude` 每拍写 `galvo.XCenter = _galvoCenterXmm`（光丝对中中心补偿**单写口**，ADR-059）⇒ **运行期被覆盖，界面改了不生效**。详见 [[decisions/ADR-076-SettingsZoneSaveWiring]]。

## 2026-10-26 自动刷新分区门控 · LA 四键 · 使能改按钮（ADR-075）

| 项 | 现行实现 |
|---|---|
| LA 控制键 | `gridLa` 末行 **四键一行**（高 44）：`btnOptMotorBack`（后退）· `btnOptMotorFwd`（前进）· `btnOptMotorMoveTo`（移动到目标，带文字 + `AimOutlined`）· `btnOptMotorEnable`（纯图标 `CheckSquareOutlined` + Tooltip）；新增 `lblOptMotorTarget` + `txtOptMotorTarget`（默认 `0`，与「步距」「量纲」同列布局） |
| LA 控制口径 | 四键全走 `WeldHeadSlaveDevice`（LA = WSX 从站 `0x7000`/`0x6020`，**非 MontionAxis**，不适用 ADR-073 的 MontionManager 六函数）：`ReadMotorStatus()` 取 `CurrentPositionMm`/`IsReady` → `SetMotorPosEnable(目标mm, 使能)` 是唯一 PDO 写口。**使能按钮为动作型**：读当前 `IsReady` 后取反再写；**移动到目标**要求已使能（与步进同判据） |
| 使能控件形态 | `swLaMotorEnable` / `swGalvoEnable` 两个 Switch **已删**，改为 `btnOptMotorEnable` / `btnOptGalvoEnable`（同 `TaServoBtn` 范式：`Ghost` + `Cursor=Hand` + 宋体 12F + `BackHover(3,169,244)` + `IconSvg`，**纯图标 + Tooltip**）。**状态由标签承载**：LA → `lblOptMotorState`；振镜 → `lblOptGalvoEnableValue`（0x6010 `GalvoOn`）。振镜「焊接中置灰」门控保留（载体由 Switch 改 `Button.Enabled`） |
| 自动刷新开关 | ~~**五个** Switch~~ ⇒ **2026-11-20 起四个**：`swTARefresh` / `swLARefresh` / `swGalvoRefresh`（激光头三区）+ `swAutoRefresh`（轨迹页轴表）；~~`swTempRefresh` 已删（温度显示迁 DeviceMonitorPage）~~，标志 `_tempAutoRefresh` 同步删除；**Designer 全部默认 `Checked = true`**；标志初值在 `BindEvents()` 内从设计器 `Checked` 同步；开启时立即刷一次本区/本页 |
| 刷新门控（**2026-10-26 已按实机复查修订 + 适用面扩展**，见 [[decisions/ADR-075-LaserHeadUiControlConsistency]] §五/§六；**2026-11-03 判定时机再修正**，见本节末） | **两个前置条件分治，⛔ 不得合并进同一个提前返回**：① 连接态判定**已移至事件回调**（`MotionControlWorkflow.StateSwitched` / `DeviceControlWork.InitializationCompleted` → `ApplyRefreshSwitchesByMotionState()`）：`IsMotionReady()` 不满足 ⇒ `SuspendRefreshSwitchesByDisconnect()` **把五个开关（四区 + 轨迹页轴表）自动回退 `Checked = false`** 并清五标志（`_refreshSuspendedByDisconnect` 幂等标记，仅回退一次 + 一条告警日志），**连接恢复后 `ResumeRefreshSwitchesAfterConnect()` 自动恢复到默认 ON**；② `IsRefreshPageVisible()`（原 `CanRefreshNow`，只判 `Visible`）不满足 ⇒ **只跳过刷新、开关状态原样保留**。两判据通过后按 `tabsSystem.SelectedIndex` **精确分发**（`LaserHeadTabIndex=1` ⇒ 四区 / `TraceTabIndex=0` ⇒ 轴表；⛔ 不用 `else` 兜底 —— 模拟测试页不属于任何刷新区） |
| 刷新开关前置校验 | 未连接时用户手动拨到 ON 会被 `AcceptRefreshSwitchOn(toggle, zoneName)` **拒绝并立即回退**（否则开关会在 ON/OFF 间反复跳）；程序回写 `Checked` 一律经 `_syncingRefreshSwitch` 抑制（回写点 2 处：`AcceptRefreshSwitchOn` / `SetRefreshSwitches` 批量 5 开关），五个处理器首行守卫均为 `if (… \|\| _syncingRefreshSwitch) return;` |
| 刷新开关作用范围 | **五个**「自动刷新」Switch：`swTARefresh` / `swLARefresh` / `swGalvoRefresh` / `swTempRefresh`（激光头四区）+ `swAutoRefresh`（轨迹页轴表，**2026-10-26 由 `btnAutoRefresh` Button 改 Switch、默认 ON**）。⚠️ ~~轨迹页 `btnAutoRefresh`（`_autoRefresh`）未纳入自动回退/恢复~~ → **已纳入**；配套**删除**轨迹页「刷新轴状态」按钮 `btnAxisRefresh`（配置编辑后的重载走 `OpenAxisEditor`，运行态由开关按拍刷新；删除后 `LoadAxisRows()` 仍余 2 处消费者） |
| 订阅位置 | **五个刷新开关** + 三个新增按钮的 `+=` **全部在 `BindEvents()`**；⛔ Designer 不订阅任何刷新开关的 `CheckedChanged`；`btnOptMotorBack/Fwd` 仍由 Designer 订阅（`.cs` 不重复绑定） |
| 已删除成员 | `_syncingSwitch`（使能 Switch 的回写抑制标志）· `_motorEnabled`（使能缓存）· `SyncGalvoSwitch` · `SyncLaMotorSwitch` —— 使能控件化为按钮后无勾选态可回写，整组退场；`UpdateMotorStateLabel` / `RefreshLaMotorStatus` 内联原本地变量。⚠️ **注意区分**：`_syncingRefreshSwitch` 是**另一件事**（五个刷新 Switch 的回写抑制），由同日 §五 修订按需**新建**，勿与已删的 `_syncingSwitch` 混为一谈 |

> ⚠️ **本轮只报不改的既有状态**（已与改码前备份逐项比对）：`gridTemp` Span **24 格 / 23 挂载**；`lblOptSpacer3` 已声明并实例化但**未挂入任何容器**。
> ✅ **2026-11-05**：同类未挂载的 `lblOptTaSlope`（文本「扭矩爬升速率」原子控件）随 `TORQUE_SLOPE` 迁出而**整体删除**（字段/实例化/属性块，全文件 0 残留）。

## ~~2026-11-02 演进：TA 力矩模式开关（`swTaTorqueMode`）~~ → 2026-11-05 已删除

> **2026-11-05（ADR-082）**：整个「力矩模式」开关已从本页移除 —— Designer 的 `swTaTorqueMode` 字段/实例化/`flowPanel5` 挂载/属性块，
> 代码的 `_syncingTaTorqueMode`、`LoadTaTorqueMode()`、`RefreshTaTorqueModeAvailability()`、`SwTaTorqueMode_CheckedChanged`、
> `BindEvents()` 接线、构造函数调用、`TimerRefresh_Tick` 每拍调用全部删除。TA 操作条只保留「自动刷新」开关。

| 项 | 历史结论（已废止，仅存档） |
|---|---|
| 控件 | ~~`flowPanel5` 内 `swTaTorqueMode`（150×30，TabIndex 8）~~ 已删除 |
| 语义 | ~~TA 轴当前模式的状态位~~ 由 `DeltaMontionAxis.TorqueOutputEnabled`（设备真实态）取代，UI 不再显示该位 |
| 默认态/跟随同步 | ~~`LoadTaTorqueMode` / `RefreshTaTorqueModeAvailability`~~ 已删除 |
| 手动操作 | `MontionManager.ExitTaTorqueMode` 仍撤 CST 回 CSP，但**只改设备态、不置灰任何指令** |
| 接口 | ~~`TaTorqueModeEnabled` / `SetTaTorqueMode`~~ 已删除；替代见 [[api/MontionManager]] |
| 持久化 | XML `TORQUE_MODE` 保留给送丝轴消费，TA 侧不再读写；⛔ 仍不走 `WeldParamManager` |

> ⚠️ 关联：[[decisions/ADR-082-TaInitFourStepAndAvailability]] · [[lessons/TorqueModeAsUiGate]]

## 2026-11-03 自动刷新开关判定时机修正

> **结论**：连接态判定只在初始化结束/连接态切换后做一次；500ms `timerRefresh` 不再判定连接态。

| 项 | 结论 |
|---|---|
| 判定入口 | `ApplyRefreshSwitchesByMotionState()`（唯一入口）：`IsMotionReady()` 为真时仅在 `_refreshSuspendedByDisconnect` 成立才 `ResumeRefreshSwitchesAfterConnect()`；为假时 `SuspendRefreshSwitchesByDisconnect()` |
| 触发点① | `MotionControlWorkflow.Instance.StateSwitched` —— 运控已连接/已断开切换时判定 |
| 触发点② | `DeviceControlWork.Instance.InitializationCompleted` —— 整机初始化链结束（成功/失败均触发）；覆盖「初始化失败但连接态仍停在 `Disconnected`、不产生状态切换事件」的路径 |
| 线程模型 | 两事件均在 IO 工作线程触发 ⇒ 入口先 `InvokeRequired` → `BeginInvoke` 封送 UI 线程 |
| 计时器职责 | `TimerRefresh_Tick` 保留 `!IsMotionReady() ⇒ return`（只跳过刷新）；⛔ 不再回退/恢复开关、不再记「未连接」日志 |
| 退订 | `DisposeComponents()` 中 `-=` 两个订阅 |
| 判据 | 初始化进行中不得出现「运控未连接，自动刷新开关已自动退回关闭」；只有初始化链结束时运控仍非就绪才允许出现；已连接成功路径不得出现 |
| 关联 | [[decisions/ADR-014-MainDeviceStateSemantics]] 演进 D3 · [[lessons/StartupInitializationOrderGates]] 坑 1 |

## 2026-11-04 演进：TA 回零参数扩至六项（**2026-11-05 已回退为四项，本段仅存档**）

| 项 | 结论 |
|---|---|
| ~~新增控件~~ | `txtTaTorquePercent` / `txtTaStopArrivalMs` 与「扭矩侦测」相关行 **2026-11-05 全部删除**（全仓 0 残留），TA 回零参数回到四项（模式/两档速度/加速） |
| ~~初值回填~~ | 不再读 `HomeDetectTorquePercent` / `HomeStopArrivalMs`（属性本身已删除） |
| 校验（现行） | 模式 `-4~35`（负值=台达扭矩回零，例如 -3；手册 §12 仅列 1~35，负值依 OD 表）；速度 rpm、加速 ms（§12.1 P636）；非法值给出中文原因并拒绝保存。~~P1.087 0~1000 / P1.088 0~60000ms~~ 已随字段删除 |
| 保存链（现行） | **2026-11-17**：弹窗内「确定」→ `AxisConfigForm.Commit()` 写回 `TaHome`（控件存活期）→ 宿主按 `editor.Committed` → `MontionManager.SaveTaHomeConfig()` → `SaveConfig()` → `ApplyTaAxisRuntimeConfig()`（下次回零生效）。~~`ApplyTaTorqueHomeDriveParams()`（写 P1 并回读）~~ **2026-11-05 删除** |
| 生效判据（现行） | P1.087/P1.088 **不再由控制器配置**（驱动器默认参数决定；现场 -3 回零已实测正常）。本页不再有任何 P1 写读回执 |
| 关联 | [[decisions/ADR-080-DeltaTorqueHomingSignedModeAndDetectParams]] §D6 · [[guides/DeltaEtherCAT-DevGuide]] §15.7 |

## 2026-11-05 迁移：扭矩爬升速率（`TORQUE_SLOPE`）移至 TA 轴「参数」弹窗

> **单一来源**：本页 `gridWireCurve` 内的输入框、标签与校验/回写全部删除；唯一入口改为 `SystemControlPage` 参数表 → TA 行「参数」按钮 → `AxisConfigForm`（[[decisions/ADR-084-TaForceToTorqueConversion]]）。

| 项 | 结论 |
|---|---|
| 删除控件 | `txtOptTaSlope`（输入框）与 `lblTaSlopeCaption` / `lblOptTaSlope`（标签，其中 `lblOptTaSlope` 为历史未挂载孤儿）—— Designer 的字段/实例化/`Controls.Add`/属性块全部移除，全仓 0 残留 |
| 删除逻辑 | `LoadOpticsFromConfig()` 的扭矩爬升速率读取块；`ApplyLaserHeadOnForm()` 的 `TryReadInt` 1~65535 校验、`GetConfig()`/`GetAxis(cfg.TaAxisName)` 轴定位、`taAxis.TorqueSlope = (uint)slope` 回写 —— 一并清理，本页不再校验/回写该值 |
| 布局 | `gridWireCurve.Span` 由 `40:fill;35:fill;150:fill;30:160 160;30:160 160 160 160;30:160 160 160 160`（13 格）改为 `…;30:160 160 160 160;30:160 160 160 160`（**11 格**），与剩余 11 个挂载控件（1 表 + 3 面板标题 + 8 按钮）逐格对应，无空洞、无重叠 |
| 应用回执 | `BtnLhApply_Click` 的「扭矩爬升速率 X」字样同步删除，只报「激光头参数已应用到内存」 |
| 落点不变 | `TORQUE_SLOPE` 仍属 `DeltaAxisConfig` ↔ XML `AXES/AXIS/TORQUE_SLOPE`（U16，1~65535），**不写 `TA_HOME`**；落盘仍由 `DeltaMotionConfig.SaveConfig()` |
| 关联 | [[decisions/ADR-084-TaForceToTorqueConversion]] · [[decisions/ADR-080-DeltaTorqueHomingSignedModeAndDetectParams]] D3 · [[decisions/ADR-076-SettingsZoneSaveWiring]] D2 |

### 历史（2026-11-04 修复，已随迁移报废）

| 项 | 历史结论 |
|---|---|
| 现象 | 激光头区改「扭矩爬升速率」→ 点「修改参数」无效果 → 再点「读取参数」仍显示 0 |
| 绑定 | ~~控件 `txtOptTaSlope` ↔ `DeltaAxisConfig.TorqueSlope` ↔ `AXES/AXIS/TORQUE_SLOPE`~~（控件已于 2026-11-05 删除） |
| 根因① | 旧校验 `TryReadDouble + slope < 0` 放行小数，写入端 `(uint)slope` 强转 ⇒ 0.5 → 0；该缺陷在新入口改由整数 `TryReadInt` 1~65535 杜绝 |
| 根因② | 旧写入 `if (taAxis != null)` 在轴未命中时静默跳过；新入口直接编辑 `DeltaAxisConfig` 实例，不存在「轴未装配即跳过」 |
| 根因③ | 旧 `taAxis == null ? "0"` 无法区分「轴缺失」与「配置确为 0」 |
| 根因④ | 旧修改成功无可见回执 ⇒ 用户无从判断是否生效 |

## 刷新节拍（2026-11-11）

- `timerRefresh.Interval` 由 `FlowTimeoutSettings.PollIntervalMs`（16ms）改为 `FlowTimeoutSettings.UiRefreshMs`（缺省 33ms ≈ 30Hz，配置 `ROOT/FLOW_TIMEOUT/UI_REFRESH_MS`）。
- 16ms 只属执行侧轮询/等待节拍（`Wait*` 系列），⛔ 不再驱动 UI 刷屏；`TimerRefresh_Tick` 每拍自校正间隔，配置晚到也生效。
- 刷屏仍为单飞（`_refreshBusy`）+ 后台采集，`IsRefreshPageVisible()` 为假时不取数。

## 模拟清理显式复位（2026-11-16，阶段 3 / ADR-099）

- `CleanupSimError` 在清警成功后追加 `DeviceControlWork.Instance.ResetMachine()`，日志「已下发设备复位 回工作零位」。
- 依据：初始化不再做回零（ADR-099），复位必须有显式调用点；称重/模拟页复用既有「清理异常」按钮，⛔ 不新增控件。
- 复位为异步 IO 受理，本页只下指令不等待；失败原因由主设备状态与日志呈现。
- 关联：[[decisions/ADR-099-init-reset-separation]] · [[api/DeviceControlWork]]

## 手动操作后台化 + 刷新职责收窄（2026-11-17，ADR-075 D24 / ADR-073 D25）

**手动操作执行器**（`StartManualOperation` / `FinishManualOperation`）：
点击 → 按钮立即置不可用（代表执行中）→ 后台线程执行 → **执行消息**回 UI 线程 → 恢复按钮 + 刷新显示 + 写日志 + 提示。

- 覆盖：Y 轴 8 键 / TA 轴 8 键 / LA 对焦电机 4 键 / GA 振镜 2 键。
- ⛔ 后台线程禁弹模态框（会阻塞工作流线程）：拒绝与失败原因经执行结果回 UI 线程再提示。
- ⛔ **停止键永远可用**（安全操作）；点动键不进执行器（禁用会丢 `MouseUp` ⇒ 点动停不掉）。
- 回零键走 `TryHomeAxisWithWait`（后台阻塞）⇒ 手动回零与复位回零同一实现，`TaHomed` 结论一致。
- 步进统一换算为绝对目标（当前位置 + delta）走 `TryMoveAxisToTarget`；⛔ 不再用会阻塞的 `StepMove`。
- 防呆：`_manualOpBusy` 在途标记 + 按钮禁用；点动进行中拒绝其它操作。

**刷新职责收窄**（`timerRefresh`）：

- ⛔ 删除 `Task.Run` + `BeginInvoke` 跨线程刷新（卡顿与显示异常根因）；采集与贴值改 UI 线程同步。
- 职责只剩**显示信息刷新**（温度 / 振镜 / LA / 轴表读数）；⛔ 不做按钮管控与状态判定。
- 轴表改**差分才重绑**（读数签名比对），不再每拍整表 `Binding`。
- 按钮可用性统一由 `RefreshActionButtonStates()` 算（单一控制函数），由连机 / 初始化 / 焊接状态 / 操作完成等事件驱动；振镜按钮「焊接中禁手动切换」由整机状态事件驱动。
- ⛔ `FixedStop_Click` / `TaStop_Click` 只下发一次停止（原实现叠加 `StopJog` 的二次停止 ⇒ 重复生效）。

**定时器**：本页 `timerRefresh` 由本 Designer 托管（`components` 容器），**页内唯一实例**，⛔ 不与工艺设置页共用。

- 关联：[[decisions/ADR-075-LaserHeadUiControlConsistency]] · [[decisions/ADR-073-AxisControlUnifiedMontionManager]]

## 按钮禁用按电机分组 + 自动焊接禁手动（2026-11-17，ADR-075 D32 / ADR-100 D29）

**按钮禁用按电机分组**（`ManualOpGroup` 四组独立）：

| 组 | 电机 | 覆盖按钮 |
|---|---|---|
| `Trace` | Y 跟踪轴 | 伺服 / 回零 / 移动到 / 步进 ×2 / 点动 ×2 |
| `Ta` | TA 送丝力矩轴 | 同上 8 键 |
| `La` | LA 对焦电机 | 使能 / 后退 / 前进 / 移动到 |
| `Galvo` | GA 振镜电机 | 使能 / 回零 |

- ⛔ **一个电机的操作只禁用它自己那组按钮** —— Y 轴回零不得让 TA / LA / GA 一起变灰（此前是全局单一忙标志）。
- 防呆（同一组不重复下发）与点动互斥同样按组隔离。
- ⛔ 停止键永远可用（安全操作）；点动键不进「按钮禁用」模型（禁用会丢 `MouseUp` ⇒ 点动停不掉）。

**自动焊接中禁手动**：

- 按钮可用性由 `_manualActionAllowed` 决定，值由**焊接状态事件**驱动刷新（⛔ 构造期不读 `DeviceControlWork` 单例，避免触发主控初始化）。
- 真正的拒绝主防线在**流程层**门禁（`MotionControlWorkflow` / `LaserWeldHeadWorkflow`），按钮置灰只是辅助提示。

- 关联：[[decisions/ADR-075-LaserHeadUiControlConsistency]] · [[decisions/ADR-100-state-union-and-action-gate]]

## 标定参数区接收跟踪几何项（2026-11-18）

> 业主裁定：工艺设置页「YT 设置」下的跟踪几何项**迁到本页「轨迹跟踪参数设置」TabPage 的标定参数区**（`gridLaserCalib`），且**取消 Y 轴行程上下限**（该设置在 Y 轴点击设置里已有）。

- **标定参数区现有项**：线激光-水平轴角度（原有）+ 跟踪几何 7 项（轴/激光比例系数 · 偏差方向 · 激光超前量 · 机器人Y补偿系数 · 示教Y锁定坐标 · 标定中心点Y/Z）。
- **落盘链路**：本页 `button1`「读取参数」→ `LoadLaserCalibOnForm()` 回填；`button2`「修改参数」→ `BtnApplyParams_Click()` 写内存；`button3`「保存参数」→ `BtnSaveLocal_Click()` 落 ①System 区（XML `WeldParamControl.xml`）。
- ⛔ **本页 XML 独占**：工艺设置页已不再落 ①System 区 ⇒ XML 文件成为「轨迹跟踪 TabPage」独占文件，跨 TabPage 保存不再互相覆盖（INI 侧拆分见 ADR-076 D6 遗留项）。
- **Y 轴行程上下限**：本页不提供该设置；限幅与越界判据改取**轴软限位**（轴配置弹窗「正向/负向软限位」，`PositiveLimit`/`NegativeLimit`，0 = 不启用）。
- 关联：[[decisions/ADR-076-SettingsZoneSaveWiring]] D6/D7 · [[api/ProcessControlPage]] · [[api/MotionControlWorkflow]]

## 读/改/存三按钮的 TabPage 边界（2026-11-19 ADR-076 D9）

| 按钮 | 所在 TabPage | 刷新区 | 说明 |
|---|---|---|---|
| `BtnReadLocal`（读取本地参数） | 轨迹跟踪参数设置 | `System`（XML 几何/标定 + INI 阈值） | 只回填本 TabPage 的轨迹点/标定/超时控件 |
| `BtnApplyParams`（修改应用参数） | 轨迹跟踪参数设置 | 只写内存（29 项） | 弹提示「尚未落盘」 |
| `BtnSaveLocal`（保存参数） | 轨迹跟踪参数设置 | `System`（落盘） | 另落线激光配置 + 流程超时快照 |
| 5 个 Enable 开关 | 流程控制与测试 | `Flow`（改即存） | `SaveProcessEnable` 逐开关落盘 |

⛔ **「读取」只写回现有配置对象**（`LoadAlgorithmsZone` 先 `Reload()` 再读指定 zone，不替换实例）⇒ 其它 TabPage 未保存的内存改动不会被丢弃。

⛔ **跨 TabPage 回填已移除**：`BtnReadLocal` 不再刷新流程控制 TabPage 的 5 个 Enable 开关（它们由页面构造时的批量回填与本 TabPage 自己的入口负责）。

- 关联：[[decisions/ADR-076-SettingsZoneSaveWiring]] D9 · [[lessons/UiButtonZoneBoundary]] · [[api/WeldParamManager]]

## 标定参数区布局（2026-11-19 业主裁定）

「线激光辅助参数 → 标定参数」区（`gridLaserCalib`，5 列 × 10 行）：

| 行 | 列 0/1 | 列 2/3 |
|---|---|---|
| 0 | 线激光辅助参数（标题） | — |
| 1 | 标定参数（标题） | — |
| 2 | 标定角度(mm) | — |
| 3 | 轴/激光比例系数 | 偏差方向 |
| 4 | 激光超前量(mm) | 机器人Y补偿系数 |
| 5 | **标定中心点Y(mm)** | **标定中心点Z(mm)** |
| 6 | **示教Y轴锁定坐标(mm)** | — |

- 三个标定项与四个几何项同为 **XML `System` 区**（`SEAM_GUIDE` + `LASER_CALIBRATION`）⇒ 由「读取本地参数」/`BtnReadLocal` 刷 System 区回填，由「修改应用参数」/`BtnApplyParams` 写内存，由「保存参数」/`BtnSaveLocal` 落盘。
- ⛔ **工艺设置页「YT 设置」区不再含标定/几何项**（2026-11-18 迁出）—— 该区现只剩 Y 指令三选项（`radioQuickYAuto` / `radioQuickYForceCalibPose` / `radioQuickYForceHome`）。

- 关联：[[decisions/ADR-109-UiButtonTabPageBoundary]] · [[lessons/MigrationCompletenessAudit]]
