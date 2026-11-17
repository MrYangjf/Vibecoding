---
title: ADR-056 数据追溯区间筛选与多选合并
date: 2026-10-09
updated: 2026-11-02
tags: [ADR, 数据追溯, 区间筛选, 多选, 悬停读数, AntdUI, UI, P3]
status: accepted
---

# ADR-056 数据追溯区间筛选与多选合并

> **需求来源**：第一次评审优化需求 No.6~12（P1 §4.4）· **实施批次**：P3 批 C（2026-10-09）
> **状态**：accepted

> **⚠️ 后续变更（2026-11-02）**：本 ADR 正文提及的 `DataReviewerPage.SeamWidthShowRange`（下方「演进记录」2026-10-10 行）已**废弃并删除**（业主决定，非本 ADR 决策变更）。本 ADR 的决策本身（区间筛选 / 多选合并 / 多会话独立折线 / 五大类模组化）**继续有效**；删除的只是该页面内一个未被接入的轴显示区间方法。
>
> **⚠️ 后续变更（2026-11-02，第二次）**：业主已裁定**一并删除** `DataReviewerPage.HasEnoughSeamWidthPoints`（原为 `SeamWidthShowRange` 的唯一调用方，删除后转 0 引用），并把 `DataReviewerPage` 的**「按 X 范围显示区域」功能模块整体移除** —— 滑块控件 `uiTrackBar1`（`AntdUI.Slider`）已从 `DataReviewerPage.Designer.cs` 移除（实例化 / `Controls.Add` / 属性块 / 字段声明），专属字段 `TrackbarRate` 已删，底行 GridPanel `Span` 由 4 行改为 `"fill;fill;fill 120;-35 fill 35"`（滑块行并入底行）。⚠️ **悬停读数所用的 `MinValueRobotX` / `MaxValueRobotX` 保留**（与滑块无关）—— ⛔ 勿因滑块删除而误删。本 ADR 的决策仍然**继续有效**；移除的只是 X 轴范围缩放这一 UI 入口，区间筛选 / 多选 / 多会话并列折线 / 五大类模组化均不受影响。判据与教训见 [[lessons/UiModuleRemovalCleanup]]。

---

## 背景

数据追溯页（`DataReviewerPage`）原为「**日历天 + 单选 + 7 平铺曲线**」：

| 现状 | 问题 |
|---|---|
| `AntdUI.DatePicker uiCalendar1` 只能选一天 | 跨日排查必须逐日切换、逐次翻页 |
| 列表单选（`_selectedRow`） | 一次只能回溯一条会话，无法横向比较多条焊缝 |
| 7 个 Checkbox 平铺 | 系列归属不明（哪个是接头、哪个是激光头） |

产品库按 `yyyyMMdd` **分表**存储（`ProductDatabaseHelper`），**没有跨表查询** ⇒ 区间筛选必须新建查询能力。

---

## 裁定

### 1. 区间筛选：逐日读表合并（业主 2026-10-09 裁定）

- **控件**：`AntdUI.DatePicker` → **`AntdUI.DatePickerRange`**（`Value` 为 `DateTime[]` 两元素，闭区间）。
 范式来源：AntdUI 官方 demo `Views/DatePickerRangeDemo.cs`（`Value = new DateTime[]{start, end}` + `PresetsClickChanged`）。
- **查询**：新增 `ProductDatabaseHelper.SelectTables(start, end)` —— **逐日** `Database.Select(TyyyyMMdd)` 后
 按业务列名克隆行合并为一张表。
- **契约**：
 | 项 | 约定 |
 |---|---|
 | 区间方向 | `start > end` **自动交换**（不报错、不返回空） |
 | 单日无表 | `Database.Select` 返回 null ⇒ **跳过该日**，不中断整段 |
 | 空结果 | 返回**零行的表**（列齐全），⛔ **不返回 null** —— 与单日版语义不同，需在 API 页显式标注 |
 | 上限 | **366 天**（一年）。跨年区间逐日读表会退化上千次查询，故设硬上限 |
- **旧链保留**：`SelectTable(date)` / `SelectResultTable(date)` / `SelectProductRecords(date)` **一律保留**，
 区间版是**并列重载**（参数个数不同，无歧义）。

### 2. 多选：列表多选列，**表头自带全选/全关**（业主 2026-10-09 二次裁定）

> ⚠️ **本条已被业主当日修正**，原「筛选栏全选/全取消/反选三按钮 + `AutoCheck=false`」方案**已废止**。

- **正确范式（本项目已有 3 处先例）**：
 `FileTraceForm.cs:59` / `ILScanForm.cs:84` / `MonitorCamScanForm.cs:85` 三处均写：
 ```csharp
 new AntdUI.ColumnCheck("Selected", "选取") { Width = "80" }.SetAutoCheck(false)
 ```
 注释明写「**表头无全选**」⇒ **反证 `ColumnCheck(key, title)` 双参 + `SetAutoCheck(false)` 是「关掉表头全选」的写法**。
- **本页取法**：`new AntdUI.ColumnCheck("Selected", "选取") { Width = "60", Fixed = true }`，
 ⛔ **不调 `SetAutoCheck(false)`** ⇒ 保留 AntdUI 默认的**表头全选 / 全取消**。
- **收益**：省掉 3 个按钮（`panelSelectBar` + 全选 + 全取消 + 反选），少 4 个事件处理器与 1 个面板控件；
 业主口径：「表头可以设置全选和全关，这样节省两个按钮」。
- ⛔ **`SetAutoCheck` 与 `AutoCheck` 都是 AntdUI 真实 API**（DLL 中 `get_AutoCheck`/`set_AutoCheck`/`SetAutoCheck`
 三处并存），本条不是编造 —— 但**单参 vs 双参的确切差异本项目无先例可循**，
 依据的是「三处单选场景都显式关掉它」这一**反证**，落地后建议在 VS 上目视确认表头确为全选态。

### 3. 多选语义：合并曲线（业主 2026-10-09 裁定「批量多选 + 合并曲线」）

- `CollectSelectedRows()`：**优先**取 `_allRows` 中勾选行；**无勾选回退 `_selectedRow`**
 （保持原右键「显示数据」单条回溯行为不变）。
- 合并方式：同系列点**依次追加**到同一 `ChartVar`，横轴仍是各自的机器人 X
 （⛔ 不做时间轴对齐 —— 各会话起点不同，按 X 合并才是回溯的本意）。
- 逐会话读三份记录文件；缺失**只计数**（`missingFiles`），**不中断整批**；
 全部缺失才告警并返回。
- 汇总文本按会话数分流：1 条 → 产品码/起焊/结果；N 条 → 「已选 N 条会话」。

### 4. 悬停显示数值：**读「点」值，命中才显示**（业主 2026-10-09 二次裁定）

> ⚠️ **本条已被业主当日修正**。原实现是「鼠标移动到哪个 X 区间就持续显示该 X 附近各系列的值」，
> 业主口径：**「鼠标移动到 ScottPlot 的点上可以读出 Y 值，不是鼠标移动区域一直显示值」**。

**修正后语义**：
| 项 | 修正后 |
|---|---|
| 触发 | **指针进入某个数据点的像素容差内**才显示（`HoverPixelRadius = 18` px） |
| 读数内容 | 该点的 **系列名 + X + Y**（`系列名　X=xx.x　Y=xx.xxx`） |
| 移开 | **立即清除**（`ClearHoverTip()`），底部标签恢复成回溯汇总文本 |
| 命中算法 | `Math.Sqrt(dx*dx + dy*dy)` **二维像素距离**（不是「按 X 找最近」） |
| 搜索范围 | 只遍历**当前勾选显示**的系列（`VisibleSeries()`）—— 与图上实际画出来的线一致 |
| 呈现 | `AntdUI.TooltipComponent`（⛔ 只用**两参** `SetTip(control, string)`，本项目 `MainPage` 已实证）+ 底部标签同步 |

⚠️ **上一轮记的「不依赖未核实 API」结论依然成立**，但**做法要改**：
上一轮把「悬停」实现成了「按 X 近似换算 + 持续显示」—— 那是**回避**核实换算 API 的产物，
功能语义与业主要的不一致。正确做法是**换个已实证的呈现通道**（`TooltipComponent`），
而不是改变功能语义来回避技术难度。

### 5. 右侧图表五大类模组化（2026-10-09 三次裁定，P1 §4.4 落地）

> 本条是 P1 §4.4 的收口项：右侧 7 平铺 Checkbox → **`Select` 选模组 + 每模组独立 Checkbox 多选**。

**结构**：`uiFlowLayoutPanel1`（原放 7 个平铺 Checkbox 的 FlowPanel，现实名 `SelectFlowPanel`）内部改为
~~`selSeriesGroup`（`AntdUI.Select`，Dock=Left 宽 170）+ `panelSeriesHost`（Dock=Fill，内含 5 个 `AntdUI.FlowPanel`）~~
→ ⚠️ **2026-10-09 三次裁定演进**：现行结构 = `selSeriesGroup` + **13 个 Checkbox 直接挂 `SelectFlowPanel`**（无中间宿主，切换即挂卸，见下方演进记录）。
**不改 `uiGridPanelRight.Span`** —— 布局风险最小化。

**五大类与成员**（P1 §4.4 规格；⛔ **不含 RobotX**，它是全部曲线的横轴，画出来是 45° 直线）：

| # | 模组 | 曲线项 |
|---|---|---|
| 0 | **接头** | 焊缝宽度 |
| 1 | **激光头** | CSPoutY(出图) · CSPinY(入图) · AxisY(轴反馈) · LA对焦位置 · 振镜摆幅 · 头部温度 |
| 2 | **机器人** | 机器人Y坐标 · 机器人Z坐标 · 机器人运动速度 |
| 3 | **送丝机** | 送丝速度 · TA送丝Z位置 |
| 4 | **激光器功率** | 激光功率 |

⇒ 曲线从 7 条增到 **13 条可选 + 1 条调整点**。后 6 路（LA位置/ 摆幅 / 温度 / 机器人Y / 机器人Z / TA位置）
数据源**早已在 `.pDat` v4**（[[decisions/ADR-052-ProductionRecordSchema]]），本轮**只加读取后的填充，不改记录层**。

**关键裁定**：

| 项 | 裁定 | 理由 |
|---|---|---|
| **Checkbox 建在哪里** | **代码后置动态创建**，Designer 只留容器 | 13 个平铺控件会让设计器文件膨胀且难维护；范式同 `MainPage.InitDeviceSwitchButtons`（本项目已实证） |
| ~~**模组面板建在哪里**~~ | ~~**同样代码后置动态创建**（`GroupHost(index)` 懒加载），Designer **零预建** `flowGroup*`~~ ⚠️ **2026-10-09 三次裁定演进：模组面板整层删除**——Checkbox 直接挂 `SelectFlowPanel`，Select 切换 = 移除旧组 + 加入新组（`ShowGroupOnly`），无任何中间宿主 | 业主 2026-10-09 三次裁定「`panelSeriesHost` 承载 checkbox 没有必要」。5 个同构 `FlowPanel` + 宿主 Panel 三层容器只为换可见性，挂卸 Checkbox 更直接 |
| ~~**懒加载语义**~~ | ~~首次 `GroupHost(index)` 时 `new` + 挂 `panelSeriesHost`，回写 `_groupHosts[index]` 缓存~~ ⚠️ **随三次裁定删除**（`GroupHost`/`_groupHosts`/`SeriesGroup.Host` 全部移除；`SeriesGroup` 现为 `{ Title, Items }` | — |
| ~~**命名**~~ | ~~`flowGroup_<index>`（下划线 + 序号）~~ ⚠️ **随三次裁定删除**（模组面板已不存在） | — |
| **只画当前模组** | `RebuildChartDatasets()`只取 `_groups[SelectedIndex]`，**不跨模组混装** | 模组化的目的就是同量纲对比；温度(℃) 与功率(W) 压在同一 Y 轴会各自成平线 |
| **调整点归属** | **不属于任何模组**，无条件 `AddSeries` | 它标的是「哪个 X 发生了调整」，与量纲模组正交；且是跨模组的定位锚 |
| **抑制标志位** | `ShowGroupOnly()` 用 `_suppressSeriesEvent` + `try/finally` 包住 Checkbox 挂卸动作 | 挂卸/回填会连带触发 `CheckedChanged`；漏了会按尚未就位的 `ChartVar` 重建图表 |
| **初始化顺序** | `SelectedIndex = 0` **先于** `SelectedIndexChanged +=` | 否则构造期即触发回调，对全空 `ChartVar` 重建图表 |
| **越界护栏** | `ShowGroupOnly(index)` 越界直接返回、`VisibleSeries()` 越界 `yield break` | 布局调整后索引失配不应整页崩 |
| **默认勾选态** | 每个 Checkbox 创建时 `Checked = true` | 与改造前 7 个 Checkbox 的默认态一致（不改变既有观感） |
| **Checkbox 宽度** | 按文本长度**估算**（`EstimateBoxWidth`） | ⛔ `AntdUI.Checkbox` 的 `AutoSizeMode`/`PreferredWidth` 未在官方 wiki 明列，不写未核实成员 |

⛔ **同一 Y 轴混装 mm / mm·s⁻¹ / W / ℃的问题沿用现状，本轮不处理**（业主裁定）——
这在模组化之后**已大幅缓解**：每个模组内部量纲基本同族（激光头全是 mm + 1 条温度例外）。
真要彻底解决需多 Y 轴或曲线分区，超出 P1 §4.4 范围，须另开一轮。

### 6. 日期基准：按行解析而非按区间起点回退

区间合并后一行可能来自非首日。`StartTime` 解析失败时回退到 **`Time` 列前 8 位**（`yyyyMMdd`）
而非区间起始日 —— 否则跨日区间里非首日的记录会被算到错误的会话文件夹，回溯找不到记录文件。

---

## 编号说明（⚠️ 重要）

P1 §5.1 原把「数据追溯区间筛选与模组化多选」编为 **ADR-055**，
但 **071 已于 2026-10-09 被「子流程状态消解与参数类归位」占用**
（[[decisions/ADR-055-SubFlowStateEliminationAndParamClassRelocation]]）。
按「编号唯一准绳 = [[decisions/ADR-Index]]」裁定，**本 ADR 取 072**。
后续 P1 规划的 072/073/074 顺延为 073/074/075。

**✅ P1 §4.4 已全部落地**：区间筛选 ✅ ·列表多选 ✅ ·悬停读点值 ✅ · **五大类模组化 ✅**
> 🔴 **2026-10-10 订正**：原写「列表多选（**表头全选**）」。实际 P1 §4.4 的原文要求是「**筛选栏 新增 全选 / 全取消 / 反选**」三按钮；
> 表头全选在双参 `ColumnCheck` 下**不存在**，故 10-09 误以「表头全选」替代并删掉按钮，10-10 已恢复三按钮（详见演进记录）。

---

## 影响

| 文件 | 改动 |
|---|---|
| `UIDesign/ControlPage/DataReviewerPage.cs` / `.Designer.cs` | 区间控件 + 多选列（表头全选）+ 悬停读点值 + 合并回溯 + **五大类模组（`Select` + 13 个动态 Checkbox）** |
| `ProductFileControl/ProductFileRecordManager.cs` | 加 `SelectProductRecords(start, end)` |
| `ProductFileControl/Records/WeldResultRecord.cs` | 加 `SelectResultTable(start, end)` |
| `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs` | 加 `SelectTables(start, end)` + `CreateEmptyProductTable` + `AppendRows` |

## 演进记录

| 日期 | 变更 | 原因 |
|---|---|---|
| 2026-10-09 初版 | 筛选栏三按钮（`ApplySelection(0/1/2)`）+ `AutoCheck=false` | 误判「点表头不整列全选」 |
| 2026-10-09 修正 | **删三按钮，改用表头自带的全选/全关** | 业主指正：`ColumnCheck` 表头本就能全选/全关，多余 |
| 2026-10-09 修正 | 悬停从「按 X 持续显示」改为 **「命中点才显示该点 Y 值，移开即清」** | 业主指正：原实现是回避技术难度的妥协，功能语义不符 |
| 2026-10-09 落地 | P1 §4.4 五大类模组化（`Select` 分选 + 每模组 Checkbox 多选 + 6 路新曲线） | P1 §4.4 收口项；RobotX 不作系列（它是横轴） |
| 2026-10-09 二次 | **5 个模组 `FlowPanel` 也改为代码后置动态创建**（Designer 零预建） | 业主裁定「不在 designer 中默认生成」；同质属性块零信息量 |
| 2026-10-09 落地 | 顺带删除 `Datashow()` 上方**重复的 `<summary>/<remarks>` 段**（旧版残留 + 新版并存） | 重复 XML 文档块有 CS1587 风险，属Step 2.5 换pattern 复查抓到 |
| 2026-10-09 三次 | **`panelSeriesHost` 中间宿主删除**：`GroupHost`/`_groupHosts`/`SeriesGroup.Host`/5 个懒加载 `FlowPanel` 全删；Checkbox **直接挂 `SelectFlowPanel`**，Select 切换 = 移除旧组 + 加入新组（`ShowGroupOnly`）；`selSeriesGroup` 每次加回集合末位保持最左（`FlowPanel` 逆序入流，实证见 [[guides/AntdUI-Reference]] §2.x）；未挂载组 Checkbox 由 `DataReviewerPage_Disposed` 显式释放 | 业主裁定「`panelSeriesHost` 承载 checkbox 没有必要」；三层容器只为换可见性，挂卸更直接 |
| **2026-10-10 上机实测回滚 10-09「删三按钮」裁定** | ① **恢复** `panelSelectBar` + `btnSelectAll`/`btnSelectNone`/`btnSelectInvert`（`ApplySelection(bool? value, bool invert = false)`，作用于 `_allRows` 全集 + `uiDataGridView1.Refresh()`）；② `DataReviewRow` 改继承 `AntdUI.NotifyProperty`，`Selected` setter 调 `OnPropertyChanged()` | **10-09 删按钮的理由不成立**：双参 `ColumnCheck(key,title)` 的表头是纯文字、**不渲染全选 checkbox**（`guides/AntdUI-Reference` §4.2 源码确证；单参才有）。10-09 据「别处 `SetAutoCheck(false)` ⇒ 反证默认带表头全选」这一**无效反证**删掉按钮 ⇒ 上机表头点击无反应、功能真空。**官方能证明「全选态存在」（`Checked`/`CheckState` + `CheckedOverallChanged`），不能证明双参会把它渲染出来** |
| **2026-10-10 多会话曲线语义翻转** | 14 个单份 `ChartVar` 字段 → **`SessionCharts`（一生产会话一份，按系列名索引）**；`RebuildChartDatasets`/`VisibleSeries` 逐会话各 `AddScatter` 一次；`SessionLabel()` 多会话加 `#序号`；`PointCount==0` 的空会话不入图；`SeamWidthShowRange`/`BuildSummaryText` 的单份假设改为跨会话判据 | 10-09「勾选多行**合并** N 条会话（同系列依次追加到同一 `ChartVar`）」在图上表现为**会话之间被直线硬连**，业主上机判定不可接受。**新语义：合并 = 并列对比，不是首尾相接**；横轴仍是各自的机器人 X（不做时间轴对齐，保持原口径） |

### 2026-10-10 附：本次一并纠正的连带隐患

| 项 | 问题 | 处置 |
|---|---|---|
| `DataReviewRow` 行模型契约 | 原为普通 class + 自动属性 `Selected`，**代码改值而复选框不刷新**（官方 `Table.md:192` 要求继承 `NotifyProperty` 或 `INotifyPropertyChanged`） | 改继承 `AntdUI.NotifyProperty`，setter 调 `OnPropertyChanged()`；同型先例 `FileTraceForm.cs:213` |
| `api/DataReviewerPage.md` 与本 ADR 的记载冲突 | api 页断言「双参 ⇒ 表头自带全选」，与 `guides/AntdUI-Reference` §4.2 源码确证冲突，**两处都写得像结论** | 同轮勘误 api 页并撤销其「反证」依据；`guides/AntdUI-Reference` §4.2 补 ⛔ 反证法警示 + §0 计数 3→4 |
| ADR 编号 | 是否为「多会话独立折线」新建 ADR-062 | **不新建** —— 属 ADR-056「多选合并」的实现纠偏而非新架构决策，就地演进成本更低且可追溯 |

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 后果

### 正面
- （待补）

### 负面
- （待补）

## 相关页面

- [[project/ReviewOptimization-P1-StructureDesign]] §4.4 —— 本 ADR 的需求来源
- [[api/DataReviewerPage]] —— 消费方页面
- [[api/ProductFileRecordManager]] —— 区间查询契约
- [[decisions/ADR-052-ProductionRecordSchema]] —— 五大类模组化的数据源
- [[decisions/ADR-Index]] —— 编号唯一准绳
