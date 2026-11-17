---
title: DataReviewerPage API 参考（数据追溯页 · 区间筛选 + 多选合并 + 悬停读数）
date: 2026-10-09
tags: [API, 数据追溯, 区间筛选, 多选, 悬停读数, ADR-056, AntdUI, UI]
source: AdaWeldSystem/UIDesign/ControlPage/DataReviewerPage.cs
status: accepted
---

# DataReviewerPage API 参考

> 生产数据回溯界面：左侧「时间区间 + 筛选栏 + 记录表」，右侧「过程曲线」。
> **位置**：`AdaWeldSystem/UIDesign/ControlPage/DataReviewerPage.cs`（代码后置）
> ＋ `DataReviewerPage.Designer.cs`（控件树）
> **命名空间**：`AdaWeldSystem.UIDesign.ControlPage`
> **本页变更**：2026-10-09 P3 批 C —— 日历天改**时间区间**、列表加**多选列**、新增**悬停读数**。
> 裁定见 [[decisions/ADR-056-DataReviewRangeFilterAndModularMultiSelect]]。

---

## 2026-10-09 改造要点（P3 批 C，含当日二次修正）

| 项 | 初版做法 | **现行做法（业主修正后）** |
|---|---|---|
| 时间筛选 | `AntdUI.DatePicker uiCalendar1`（单日） | **`AntdUI.DatePickerRange uiDateRange`**（闭区间，`Value` 为 `DateTime[]` 两元素） |
| 列表选择 | 单选（`_selectedRow`） | **多选列 `ColumnCheck("Selected","选取")`，表头自带全选/全关**；~~筛选栏三按钮已于 2026-10-09 删除~~ |
| 回溯行为 | 一次只画一条会话 | **勾选 N 条 ⇒ 合并 N 条会话的曲线**；无勾选时回退单行 |
| 图表交互 | ~~仅滑块定位~~（该路径**已于 2026-11-02 随「按 X 范围显示区域」模块整体移除**） | **悬停读「点」值**：指针进入某点 18px 内显示该点 X/Y，移开即清 |

### 区间契约（三层贯通）

```
DatePickerRange.Value → InitPCLDir(start, end)
  → LoadProductRecords(start, end)
    → ProductFileRecordManager.SelectProductRecords(start, end)
      → WeldResultRecord.SelectResultTable(start, end)
        → ProductDatabaseHelper.SelectTables(start, end)   ← 逐日读表合并
```

⛔ **单日旧链保留**：`SelectProductRecords(DateTime)` / `SelectResultTable(DateTime)` / `SelectTable(DateTime)`
**未被替换**（按日查看等调用方仍在用），区间版是**并列重载**而非替换 —— 两者参数个数不同，无重载歧义。

### 查询触发时机（2026-11-09 修正 · ADR-078 通用化 / H11）

| 场景 | 行为 |
|---|---|
| 启动 / 初始化 / 页面预创建 / 窗体 `Show` | ⛔ **零查询、零空态**。AntdUI 非当前 `TabPage` 恒为 `Visible=true`，窗体 Show 时全部子页都会收到 `VisibleChanged`；判据因此不用可见性，而是 `GlobalCommData.IsAppRunning`（初始化结束后由 `FormMain` 置位） |
| 用户首次进入「数据追溯」页（点导航项/页签） | `EnsureLoaded()` 放行 → 按当前区间（默认今天~今天）查一次；`_firstShownLoaded` 置位 |
| 反复切走再切回 | 只重建界面（`AfterInitializeUI`），**不重查**（已加载标记） |
| 用户点刷新 / 改时间区间 | 让 `InitPCLDir` 按新条件重查（用户主动） |
| 查询返回 0 行 | **主动查询**（刷新 / 改区间）才显示 `AntdUI.Message.warn("{start} 至 {end} 没有生产记录。")`；首次进入的自动加载**只更新底部中性文案、不弹窗**（见 §空态两态与诊断口径） |
| 未加载 | 底部标签为中性文案「尚未加载生产记录（选择日期区间后点刷新）」，不出现「没有记录」结论 |

> 单一入口 = `DataReviewerPage.EnsureLoaded()`，只由 `FormMain` 的导航/页签切换调用；⛔ 页面不再订阅 `VisibleChanged`（在 AntdUI 下它无法区分「用户进入」与「窗体 Show」）。`InitPCLDir` 入口再做一次运行态硬闸，拒绝时写 `DataReviewDiag` 限流 Warning（≤5 条/进程，含完整堆栈）后直接返回，不查库、不扫记录、不弹空态。

### 空态两态与诊断口径（2026-11-13 修正）

| 项 | 口径 |
|---|---|
| `InitPCLDir(start, end, userInitiated)` | 第三参 `userInitiated` 区分触发来源：`true` = 用户主动（刷新 / 改区间），`false` = 进入页面自动加载 |
| 0 行 · `userInitiated=true` | 底部文案「所选区间无生产记录」+ `AntdUI.Message.warn` 空态弹窗 |
| 0 行 · `userInitiated=false` | 底部文案「所选区间无生产记录」，**⛔ 不弹窗**（用户未主动查询，不以弹窗打扰） |
| `DataReviewDiag` 诊断 | **仅门拒绝路径**（运行态未就绪却发起了查询）调用；⛔ 正常查询路径不再打「查询入口 / 弹窗入口」诊断 |

> ⚠️ 撤除正常路径诊断的原因：残留 `DiagLog` 在**每次用户点开追溯页**时输出 2 条带完整 `StackTrace` 的 Warning，界面日志区读起来像报错，掩盖真正的异常。该诊断是 2026-11-09 排查「启动即查库」时的临时脚手架（坑已闭环，见 [[lessons/StartupInitializationOrderGates]] 坑 3），撤除。

### 提示与日志职责（2026-10-10 上机实测修复，见 [[standards/MessageLogResponsibility]]）

| 环节 | 规则 |
|---|---|
| `LoadProductRecords` catch | ~~`AntdUI.Message.warn("读取生产记录失败：" + ex.Message)`~~ → **`GlobalCommData.ShowLog("DataReviewerPage", …, Error)`**，按零行返回；`ex.Message` 只进 LOG 不进弹窗 |
| `InitPCLDir` 零行 | **唯一结果提示**：`AntdUI.Message.warn("{start} 至 {end} 没有生产记录。")`（区间文案，结果反馈职责） |
| 区间读取整段失败根因 | `ProductDatabaseHelper.SelectTables` 曾对缺表日期直调 `Database.Select` → `GetDataSet` 抛 `SQLiteException` 上抛 → 区间**全部**读不到；现 `IsExistTable` 跳过缺表 + 单日异常 `ShowLog` 后跳过当日（详见 [[api/SQLiteDatabaseManager]] / modules 页） |

### 多选语义

> 🔴 **2026-10-10 勘误：本节原「表头全选」两条是错的**（上机实测表头点击无反应）。原因见下方⛔。

| 环节 | 规则 |
|---|---|
| 列定义 | `new AntdUI.ColumnCheck("Selected", "选取") { Width = "60", Fixed = true }` |
| 表头全选 | ⛔ **双参 `ColumnCheck(key, title)` 的表头是纯文字 title，不渲染全选 checkbox，点击表头不触发全选**（`guides/AntdUI-Reference` §4.2 源码确证：单参才带表头全选）。**本页不再依赖表头全选** |
| 全选/全取消/反选 | 筛选栏 `panelSelectBar` 三按钮（`btnSelectAll` / `btnSelectNone` / `btnSelectInvert`）——P1 §4.4 原文要求，2026-10-09 曾被整体删除，2026-10-10 恢复 |
| 作用范围 | `ApplySelection` 作用于 **`_allRows` 全集**（跨分页），末尾 `uiDataGridView1.Refresh()` |
| 行模型契约 | `DataReviewRow : AntdUI.NotifyProperty`，`Selected` setter 调 `OnPropertyChanged()`——**否则代码改值而复选框不刷新**（官方 `Table.md:192` 明文要求；同型先例 `FileTraceForm.cs:213`） |
| 回溯取值 | `CollectSelectedRows()`：优先取 `_allRows` 中勾选行；**无勾选回退 `_selectedRow`** |
| 多会话合并 | ⛔ **不是**追加进同一 `ChartVar`：每个会话装在独立 `SessionCharts` 内，**各自成一条折线、互不相连**（旧实现把 N 会话依次 Add 进同一 `ChartVar`，会话间被直线硬连 —— 2026-10-10 上机实测缺陷） |
| 图例 | 多会话时 `SessionLabel()` 加 `#序号` 后缀（`焊缝宽度#1` / `#2`…）；单会话不加 |
| 缺失文件 | 逐会话统计 `missingFiles`，**不中断整批**；全部缺失才告警并返回 |
| 空会话 | `session.PointCount == 0` 的会话**不入 `_sessions`**（否则占用图例序号） |

> ⛔ **原「依据」已撤销**：「本项目 3 处单选场景都显式 `SetAutoCheck(false)` ⇒ 反证默认形态带表头全选」——**该反证不成立**。`AutoCheck` 管的是**单元格点击自动 toggle**，与表头是否渲染全选框是两个独立机制；§4.2 已明确双参无表头全选。**官方文档能证明「表头全选态存在」（`TableColumn.md` ColumnCheck 的「全选」分组 `Checked`/`CheckState` + 事件 `CheckedOverallChanged`），但不能证明双参会把它渲染出来。**

### 悬停读点值

| 项 | 实现 |
|---|---|
| 事件 | `formsPlotData.MouseMove += formsPlotData_MouseMove` |
| 节流 | `HoverThrottleMs = 60` |
| 命中半径 | `HoverPixelRadius = 18`（**像素**，随缩放自动收紧） |
| 命中算法 | `FindNearestPoint(x, y)`：遍历 `VisibleSeries()`（只含勾选的 Checkbox），取**二维像素距离**最近点 |
| 命中呈现 | `AntdUI.TooltipComponent` ⛔ **只用两参 `SetTip(control, string)`**（范式见 `MainPage.InitDeviceSwitchButtons`），文本 = `系列名　X=xx.x　Y=xx.xxx` |
| 未命中 | `ClearHoverTip()` —— Tooltip 清空 + 底部标签恢复 `_lastSummaryText` |
| 底部标签 | `_lastSummaryText` 由 `Datashow` 写入，悬停清除后回填（避免被读数覆盖后永久丢失） |
| 数据窗口 | `GetPlotWindow()`：X 用 `Min/MaxValueRobotX`，Y 用**可见数据的极值 ±10% 留白** |

> ⚠️ **换算仍是线性近似**：不依赖 ScottPlot 的像素↔坐标 API（签名属语义判据，本机无编译器 + 反射被拦截）。
> 近似只影响「命中判定的手感」，不影响读出的数值 —— 读数取自数据源本身，不是换算出来的。

---

## 控件清单

| 控件 | 类型 | 位置 | 说明 |
|---|---|---|---|
| `uiDateRange` | `AntdUI.DatePickerRange` | `panelDateBar` | `Format="yyyy-MM-dd"`、`InteractiveReset=false`；`Presets` 未设 |
| `btnRefreshDate` | `AntdUI.Button` | `panelDateBar`（右） | 按当前区间重载 |
| `panelSelectBar` | `AntdUI.Panel` | `panelLeft`（Top，区间栏下方） | **勾选操作栏**，内含 `tlpSelect` 承载全选/全取消/反选三按钮 |
| `tlpSelect` | `TableLayoutPanel` | `panelSelectBar`（Fill） | **1 行 3 列**，三按钮各占一格。⛔ 不可把三个按钮直接挂 `panelSelectBar` 并同设 `Dock=Fill` —— 同父同 Dock 会叠成同一矩形、只看得见最上层（2026-10-10 上机打回，详见 [[lessons/StaticVerifierJudgements]] §7.3.2） |
| `btnSelectAll` | `AntdUI.Button` | `panelSelectBar` | 全选当前区间全部记录（`_allRows` 全集，跨分页） |
| `btnSelectNone` | `AntdUI.Button` | `panelSelectBar` | 全取消 |
| `btnSelectInvert` | `AntdUI.Button` | `panelSelectBar` | 反选 |
| `selSeriesGroup` | `AntdUI.Select` | `SelectFlowPanel`（`uiGridPanelRight` 第 1 行） | **曲线模组选择器**，5 个选项：接头 / 激光头 / 机器人 / 送丝机 / 激光器功率 |
| （模组 Checkbox） | `AntdUI.Checkbox` ×13 | `SelectFlowPanel`（运行期随 Select 切换挂卸） | **代码后置动态创建**，只挂**当前模组**的 Checkbox；Select 切换 = 移除旧组 + 加入新组 |
| `formsPlotData` | `ScottPlot.FormsPlot` | `uiGridPanelRight` | 单折线图（悬停读数挂在此控件上） |
| ~~`uiTrackBar1`~~ | ~~`AntdUI.Slider`~~ | ~~`uiGridPanelRight`~~ | **已删除（2026-11-02，「按 X 范围显示区域」模块整体移除）** —— 控件本体（Designer 实例化 / `Controls.Add` / 属性块 / 字段声明）已从 `DataReviewerPage.Designer.cs` 移除；原「按机器人 X 分段定位」路径不再存在 |

> ⛔ **2026-11-02 模块整体移除**：「按 X 范围显示区域」功能模块（滑块定位 + 专属字段 `TrackbarRate` + 判据 `HasEnoughSeamWidthPoints`）**已整体删除**，本页不再有对应控件与入口。
> 悬停读数（`MinValueRobotX` / `MaxValueRobotX` 线性近似）**保留且仍在**，与滑块无关 —— ⛔ 勿因滑块删除而误删这两个字段。
> 底行 GridPanel `Span` 同步改为 `"fill;fill;fill 120;-35 fill 35"`（滑块行并入底行）。
> 判据与教训见 [[lessons/UiModuleRemovalCleanup]]。

> ⚠️ **2026-10-09 已删除 → 2026-10-10 已恢复**：`panelSelectBar` + `btnSelectAll` + `btnSelectNone` + `btnSelectInvert`。
> 删除理由（「表头自带全选/全关，按钮冗余」）**基于错误认知**：双参 `ColumnCheck` 的表头并不渲染全选 checkbox，
> 上机实测表头点击无反应 ⇒ 2026-10-10 按 P1 §4.4 原文恢复三按钮，`ApplySelection(bool? value, bool invert = false)` 改为作用于 `_allRows` 全集。
>
> ⚠️ **2026-10-09 已删除**：`chkSeamWidth` / `chkRobotSpeed` / `chkFeedSpeed` / `chkLaserPower` /
> `chkCspY` / `chkRobotY` / `chkAxisY` 这 7 个平铺 Checkbox（P1 §4.4 五大类模组化）。
>
> ⚠️ **2026-10-09 二次删除**：`flowGroupJoint` / `flowGroupLaser` / `flowGroupRobot` /
> `flowGroupWire` / `flowGroupPower` 这 **5 个模组 `FlowPanel` 也不再在 Designer 里预建**
> （业主裁定「不在 designer 中默认生成」）⇒ 当时 Designer 只剩 `selSeriesGroup` + `panelSeriesHost` 两个容器，
> 5 个面板由 `GroupHost(int index)` 懒加载创建并挂到 `panelSeriesHost`，命名 `flowGroup_<index>`。
>
> ⚠️ **2026-10-09 三次删除（现行）**：`panelSeriesHost` 中间宿主也**移除**（业主裁定「没有必要」）——
> `GroupHost()` / `_groupHosts` / `SeriesGroup.Host` / 5 个懒加载 `FlowPanel` 全部随之删除。
> **Checkbox 直接挂 `SelectFlowPanel`**：Select 切换 = `ShowGroupOnly(index)` 移除旧组 Checkbox + 加入新组 Checkbox。
> `FlowPanel` 逆序入流（后加入者靠左）⇒ `selSeriesGroup` 每次重新加回集合末位保持最左，
> Checkbox 按 Items 顺序加入（显示顺序与改造前一致）。未挂载模组的 Checkbox 不在控件树内，
> 页面 `Disposed` 时显式 `Dispose`（`DataReviewerPage_Disposed`）。

## 曲线五大类模组（P1 §4.4，2026-10-09 落地）

**结构**：`selSeriesGroup` 选模组 → 只显示该模组的 Checkbox 面板 → `RebuildChartDatasets()`
**只画该模组内勾选的线** + 始终显示的调整点。

| # | 模组 | 曲线项 | 数据来源 |
|---|---|---|---|
| 0 | **接头** | 焊缝宽度 | `.pDat` `WeldWidth` |
| 1 | **激光头** | CSPoutY(出图) · CSPinY(入图) · AxisY(轴反馈) | `.csv` `CspOutY` / `CspInYt` / `AxisY` |
| | | LA对焦位置 · 振镜摆幅 · 头部温度 | `.pDat` `LaPositionMm` / `GalvoAmplitudeMm` / `HeadTempC` |
| 2 | **机器人** | 机器人Y坐标 · 机器人Z坐标 · 机器人运动速度 | `.pDat` `RobotY` / `RobotZ` / `RobotSpeed` |
| 3 | **送丝机** | 送丝速度 · TA送丝Z位置 | `.pDat` `FeedSpeed` / `TaPositionMm` |
| 4 | **激光器功率** | 激光功率 | `.pDat` `LaserPower` |
| — | （不归模组） | **调整点**（始终显示） | `AdjustChartVar`，标注「哪个 X 发生了调整」 |

⛔ **不含 RobotX** —— 它是全部曲线的**横轴**，画出来是 45°直线。

### 关键实现约定

| 项 | 约定 |
|---|---|
| **Checkbox 建在哪里** | **代码后置动态创建**（`BuildGroup` + `MakeItem`），Designer 只留 `selSeriesGroup` 下拉。范式同`MainPage.InitDeviceSwitchButtons` |
| **Checkbox 挂在哪里** | **直接挂 `SelectFlowPanel`**（业主 2026-10-09 三次裁定，无中间宿主）：`ShowGroupOnly(index)` 移除旧组 + 加入新组；`selSeriesGroup` 重新加回集合末位保持最左（`FlowPanel` 逆序入流） |
| **系列描述** | 内部类 `SeriesItem { Box, Text, Name, Color, GetChart }`；`GetChart` 是 **`Func<ChartVar>`**（lambda 取当前字段值，`Datashow` 重建后自动指向新对象） |
| **模组描述** | 内部类 `SeriesGroup { Title, Items }`（2026-10-09 三次删除后**无 `Host`**） |
| **初始化顺序** | `selSeriesGroup.SelectedIndex = 0` **先于** `SelectedIndexChanged +=`（否则构造期对空 `ChartVar` 重建图表） |
| **抑制标志位** | `_suppressSeriesEvent` + `try/finally` 包住 `ShowGroupOnly()` 的挂卸动作，防`CheckedChanged` 连带触发 |
| **越界护栏** | `ShowGroupOnly(index)` 越界直接返回；`VisibleSeries()` 越界 `yield break` |
| **释放链** | 未挂载模组的 Checkbox 不在控件树内 ⇒ 页面 `Disposed` 时 `DataReviewerPage_Disposed` 显式 `Dispose` 全部 `Box` |
| **Checkbox 宽度** | `EstimateBoxWidth(text)` 按字符宽度估算（⛔ `AntdUI.Checkbox` 的 `AutoSizeMode`/`PreferredWidth` 未在官方 wiki 明列，不写未核实成员） |
| **悬停一致性** | `VisibleSeries()` 与 `RebuildChartDatasets()` 取**同一模组、同一勾选判定** —— 读数不会命中看不见的线 |

> ⚠️ **量纲说明**：同一 Y 轴仍会混装 mm / mm·s⁻¹ / W / ℃（业主裁定沿用现状）。
> 模组化后已大幅缓解 —— 每个模组内部量纲基本同族。
> 真要彻底解决需多 Y 轴或曲线分区，**超出 P1 §4.4 范围**。

## 数据行 `DataReviewRow`

| 字段 | 类型 | 说明 |
|---|---|---|
| `Selected` | `bool` | 多选勾选态（对应 `ColumnCheck("Selected")`） |
| `No` / `Sn` / `Time` / `Status` / `Result` / `Info` | `int` / `string`×5 | 表格显示列 |
| `StartTime` | `DateTime` | 起焊时间原值，**不入表**，供推算会话基名 |

> ⚠️ **区间合并后的日期基准**：`StartTime` 由 `Time` 列（`yyyyMMddHHmmss`）解析，
> 解析失败时回退到**该行前 8 位**（`yyyyMMdd`）而非区间起始日 ——
> 否则跨日区间里非首日的记录会被算到错误的会话文件夹，导致回溯找不到记录文件。

## 相关页面

- [[decisions/ADR-056-DataReviewRangeFilterAndModularMultiSelect]] — 本页改造的裁定来源
- [[api/ProductFileRecordManager]] — 区间查询与记录读取的上游
- [[architecture/CodeMap]] — 按文件定位
- [[lessons/StaticVerifierJudgements]] — 「语义判据只有编译器能定」的判据库

## 遗留（未实施）

- ⛔ **P1 §4.4 的「右侧图表按五大类模组化」（接头 / 激光头 / 机器人 / 送丝机 / 激光器功率）尚未实施**：
  当前仍是 **7 个平铺 Checkbox**。数据源已就绪（`.pDat` v4 含 `TaPositionMm`/`LaPositionMm`/`GalvoAmplitudeMm`/`HeadTempC`），
  待下一轮按模组重组。
- ⛔ **真编译待 Visual Studio**：本轮所有静态校验通过 ≠ 构建通过。
