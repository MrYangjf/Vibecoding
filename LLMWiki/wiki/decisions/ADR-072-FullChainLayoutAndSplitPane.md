---
title: ADR-072 全链布局修正（页级Grid→卡片Panel→区内Grid→控件）+ 自适应页数据回溯式左右分栏
date: 2026-10-15
updated: 2026-10-19
tags: [ADR, UI, 布局, GridPanel, 全链结构, 数据回溯, 左右分栏, 批L, 批M, U-3, 轴按钮, 统一读存]
status: accepted
---

# ADR-072：全链布局修正 + 自适应页左右分栏

> 业主 2026-10-15 裁定两条：
> ① **系统设置三个子页结构错误**——「先用 Grid 分大区域，再在里面的 Panel 放子 gridpanel 再放置控件，不是一上来就设置成放置子控件的模式」，参考工艺设置页；
> ② **自适应工艺设置**按业主既往要求做成「**类数据回溯界面**」——分左右两侧 GridPanel，左侧=参数列表 + 新建/删除/选择，右侧=现参数设置。

## 一、全链结构铁律（三子页修正）

**唯一合法嵌套链**（每一层都必须存在，不得跳级）：

```
TabPage → 页级 GridPanel(分区) → 卡片 Panel(ADR-060 形态) → 区内 GridPanel(控件区格) → 控件
```

| 子页 | 修正前 | 修正后 |
|---|---|---|
| ① 轨迹跟踪参数 | `gridTrace`(页级✓) → 4 个 Panel 非卡片、`flpTraceToolbar` **裸挂**、`panelTraceAxis` 直挂 table | 4 Panel 卡片化（Back白/Border217/Padding3/Shadow5/Opacity0.2）；裸 toolbar 补 `panelToolbarZone`→`gridToolbar`；`gridTraceAxis` 包 `tableAxis`。**⚠️ 2026-10-16 三轮演进（业主）**：页级 `gridTrace` 由 4 行纵向（`40:fill;1140:fill;340:fill;400:fill`）改 **2×2 大分区**（`fill fill;fill fill`，参考快捷设置等页级范式）：r0=轨迹点控制区(`panel2`→`gridAlgoControl`) + 跟踪轴控制区(`panelTraceAxis`)，r1=工具条区(`panelToolbarZone`) + 线激光标定区(`panelLaserCalibHost`)；其余两格内容业主后补 |
| ② 激光头系统参数 | Tab **直挂 2 占位 Panel，无页级 Grid** | 补 `gridLaserHead`（Span `200:fill;fill` 温控上/光丝下）→ 卡片化 → 各补 `gridTemp`/`gridOptics` |
| ③ 模拟测试 | `panel3` 直挂 Tab，非卡片 | 补页级 `gridSimTestZones`（`fill`）→ `panel3` 卡片化（`gridSimTest` 已在） |

**实测（行高弹性语义，本轮关键发现）**：
- `40:fill` = **固定 40px**（4 行 40 在 712 高容器只占 160 ⇒ 内容压扁）
- **裸 `fill` = 弹性均分**；`40:fill;fill;fill` = 标题固定 + 余下弹性；`N:fill` px 固定
- ⇒ `gridTrace` 由错误的 `40×4` 修为 **`40:fill;1140:fill;340:fill;400:fill`**（还原原 TLP 绝对行高）+ 恢复 `AutoScroll`（上轮转换剥除）。⚠️ 2026-10-16 三轮演进后 gridTrace 已再改 2×2 `fill fill;fill fill`（见 §①），本条保留为行高弹性定理的原始实证记录

**VS 设计器副产物（已核实合法）**：超长 Span 字符串被 VS 移入 `.resx`（`resources.GetString(...)`）——`SystemControlPage.resx:gridAlgoControl.Span` 键值仍在（判据须接受两种载体）；`ProcessControlPage.resx:gridAdaparam.Span` ⚠️ 2026-10-16 三轮演进后已改回 .cs 字面量（16 行，删「焊接工艺库操作」区所致，见 §二），resx 键不再被引用。

## 二、自适应页左右分栏（类数据回溯界面）

```
tabPageAdaptiveSetup → panelWeldList
 → gridWeldZones(页级, Span "20%:fill;fill" ← 2026-10-16 由 fill fill 改 左20/右80)
 ├ 左: panelConfigList(卡片) → gridConfigList(Span "40:fill;fill;30:160 160 160")
 │ r0 lblConfigListTitle「工艺参数列表」/ r1 tableConfigList(AntdUI.Table, 弹性) / r2 新建·删除·选择(三按钮 160)
 └ 右: panelAdaparam(卡片) → gridAdaparam(原 45 子原样迁入 0 改动；⚠️ 2026-10-16 删右区 5 子后 40 子 16 行，见下)
```

- **左列表** = `AntdUI.Table` 单列（No + 配置名），复用 ConfigForm/DataReviewerPage 先例：`Columns` **后置初始化**（InitConfigListColumns，Designer 铁律）、`CellClick` **后置订阅**（项目 5 先例均后置）、`Binding(AntList<ConfigListRow>)`
- **三按钮接线**：新建→复用 `btnAddNewConfig_Click`（查重+AddConfig）· 删除→ConfigForm 同款三重保护（默认配置禁删/Modal 确认/在用配置禁删）· 选择→`SwitchConfig`+`LoadParamOnForm`；刷新点=构造、页面 Shown、增删选后
- 数据源 = `ConfigHelper.GetAllConfigs()`（「标识」列）；接口 `SwitchConfig/AddConfig/DeleteConfig` 全现成

**⚠️ 2026-10-16 三轮演进（业主）**：
- **分栏比例**：`gridWeldZones.Span` 由 `fill fill`（50/50）改 20/80 —— ⛔ **四轮复正（同日，业主发现被改成上下）**：三轮误写 `"20%:fill;fill"`，`:` 前是**行高**（ADR-069 §二），故被解析成 2 行上下布局；左右两列正确写法 = 单行两列 **`"20% 80%"`**（无冒号整段即列，WinForms-Designer §2.5 先例 `Span="40% 60%"`），已修为 `"20% 80%"`（Add 序 `panelAdaparam→panelConfigList` 不变 = 右80/左20）
- **按钮合并**（右侧「焊接工艺库操作」区职责全部并入左列表三按钮，右区随之删除）：
 - 右侧 `btnAddNewConfig`（新增配置）职责 = 左 `btnConfigAddNew` → 保留左、删右；`btnAddNewConfig_Click` 处理器仍为左按钮复用目标（不删）
 - 右侧 `btnShowConfigList`（查看历史参数）**不再需要** → 删除按钮 + 整体删除 `btnShowConfigList_Click` 处理器
 - 左 `btnConfigDelete` = 原查看历史参数对话框内的删除功能（三重保护已一致，无改）
 - 右侧「焊接工艺库操作」标题行整体删除：`lblWeldListTitle` + `uiSymbolLabel12` + `mAutoParamName`（当前配置名）共 5 控件删（实例化/挂载/字段/订阅/属性块全清），`gridAdaparam` Span 由 resx 载体改字面量并由 18 行减为 **16 行**

**⚠️ 2026-10-23 演进（业主）**：左列表右键菜单由「删除」改为「选择/切换」（`DeleteConfig`→`SelectConfig`，点击走 `ConfigSelect_Click` → `SwitchConfig`+`LoadParamOnForm`；`uiContextMenuStrip1.Opening` 按 `tableConfigList.SelectedIndex` 同步目标行）；底部三按钮改为**两按钮**（新建/删除），`btnConfigSelect` 实例化/挂载/字段/属性块/处理器全删，`gridConfigList.Span` 末行 `30:80 80`。

## 三、六轮演进（2026-10-19 业主三需求 + 统一读存）

1. **轨迹点区一分为二**（业主 VS 改造）：`panel2` → `gridFitterControl`（拟合过滤/方向平滑段 + 主标题），
 `panelToolbarZone` → `gridCspControl`（CSP/折返段承接区）；页级 `gridTrace.Span` = `fill fill;fill fill;40:fill`
 （2×2 大分区 + 底部 40px 按钮行）。
2. **⑤工艺输出收编自适应调整算法（数据→UI 双迁移）**：
 - **数据**：5 变量（`ManualSeamWidthMm`/`SpotWidthGain`/`ParamOutputHz`/`FeedforwardSafetyFactor`/`EnableMonotonicConstraint`）
 收编为 `WeldParamAdjustmentAlgorithm` 属性（转发 `_config`）+ `WeldParamManager` facade；**配置兼容**——
 仍由 WeldAlgorithmsConfig 承载、原分区落盘（Adapt 三键 / System 两键）、INI/XML 键零改动。
 - **UI**：⑤区 11 控件（含 `lblParamOutTitle`）自 SystemControlPage 跨 Designer 迁入 ProcessControlPage
 `gridAdaparam`（16→**20 行 51 格零空格**；四形态含 11 行实例化）；读写链 = `LoadParamOutOnForm`（facade 读）+
 `BtnSaveAutoParam`（facade 写 + System/Adapt 双区落盘）；系统页 ⑤ 读写与 Adapt 落盘删除。
 - ⚠️ **推翻 [[decisions/ADR-068-WeldAlgorithmsConfigZoneReorg]] 的 EnableMonotonicConstraint 唯一入口行**：
 UI 入口由①系统设置迁往工艺设置页自适应区（落盘分区不变）。
3. **轴表控制列迁固定按钮** → 见 [[decisions/ADR-073-AxisControlUnifiedMontionManager]]（19→11 列、8 按钮 BindEvents 接线、
 UI 直控归零）。
4. **跟踪设置统一读存三按钮**（业主 VS 置 `flowPanel1`+`button1/2/3` 靠右于 `gridTrace` 底行）：
 **替代 3 对 6 个分区按钮**（`btnRead/SaveAlgoThresh`、`btnRead/SaveLaserCalib`、`btnRead/SaveTimeout`
 四形态删净、6 旧处理器整删）——
 - 读取本地 = 2 配置加载（`LoadAlgorithmsConfig`+`LineLaserManager.LoadConfig`）+ 3 回填全量；
 - 修改应用 = 22 项 UI→内存（轨迹点 19 + 标定角度 + 超时 3，**不落盘**）；
 - 保存参数 = `SaveAlgorithmsZone(System)` + `LineLaserManager.SaveConfig()` 双落盘（只存**已应用**配置，不隐式收集）。
 - `gridCspControl` 17→**15 格**（VS 首行 `40:fill` 调整保留、拼接形态兼容）；`gridLaserCalib` 15→**11 格**混行重排
 （标定/超时读存行整行消失，`40:fill;30:fill;30:160 160;30:fill;4列;2列`）。

**六轮校验**：118/118 PASS（正轮）+ 阴性 28/118 项数对齐；教训入 [[lessons/StaticVerifierJudgements]] §四之六
（Designer 控件删除/迁移四形态清单：实例化不带点号/声明/属性块/挂载）。

## 关键约束

**⚠️ 2026-10-16 四轮演进（业主四项）**：
1. **LA/TA Settings 区内 Grid 化**（需求 2：`panelLaserLa/Ta` 此前子控件绝对定位直挂卡片、链缺「区内 Grid」层）：新建 `gridLaserLa`（4 行 13 子：标题+Spot 行+Pose 行+Target/按钮行，各 4 列）/ `gridLaserTa`（7 行 16 子：标题+4 参数组各「标签160+输入160+单位160」3 列+Tip 整行 `30:fill`+按钮行 2 列），四件套齐（new/Suspend/Add 重排改挂/Span 块/Resume/字段），子控件补 `Dock=Fill`（grid 子惯例），卡片仅挂 grid；分组经 Step 1.5 AskUserQuestion 确认
2. **轨迹点控制+线激光标定四列化**（需求 4，标题+四列标准）：`gridLaserCalib` 7 行(两列)→**6 行**（`40:fill;40:fill;30:160×4;40:fill;30:160×4;30:160×4`，视觉序反转恰与原 Add 序全等⇒零重排）；`gridAlgoControl` 30 行→ ~~18 行~~ ⚠️ **五轮复正（同日，业主报「参数变少、倒灌进去」）**：四轮构造目标视觉序犯三错——段标题按 ⑤④③②① **逆序**列出、⑤区 Mono/OutputHz 两对误置于主标题之后、对内写成 `txt|lbl`（输入在标签前）⇒ 现 **19 行**（6 标题 `40:fill` + 11 四列 + 2 两列按钮/单参数行，54 格零空格），视觉正序 ①线激光点过滤→②方向平滑→③CSP输出→④折返监测→⑤工艺输出、段内 `标签|输入`，resx 重写 + Add 块按目标视觉反转重建；**新判据入校验器**：段标题序=语义编号序、对内 lbl 先于 txt
3. **孤儿/漏挂控件可见化**（需求 3，业主裁定「先全部找到并显示，看完再定去留」）：可达性扫描（父链断链）全 UIDesign 命中 41 个——本轮仅处置工艺/系统两页 3 个：`uiContextMenuStrip1`(+`DeleteConfig` 右键「删除」) → `tableConfigList.ContextMenuStrip`（语义吻合左列表右键删）；`lblEnableGalvoWeave`（空文本 Label 无框不可见）→ 临时挂 `panelProcessDebug` 右上+`BorderStyle.FixedSingle`+`Text="漏挂控件"`（**临时，待业主裁决**）；⚠️ RenderParamForm 38 控件（「算法参数」TLP 空表）**业主裁定暂不动**，仅列清单留档
4. **分栏复正**（需求 1）：见 §二 三轮演进的四轮复正段——`"20%:fill;fill"` 是行高语义故变上下，正确为 `"20% 80%"`

| 约束 | 说明 |
|---|---|
| ⛔ 链完整性 | 页级 Grid 的孩子只能是 Panel；卡片 Panel 的孩子只能是区内 Grid（`panelTraceAxis`→`gridTraceAxis` 单控特例不破坏） |
| ⛔ Columns/CellClick 后置 | 禁入 Designer（铁律）；Columns 未初始化前不得行绑定 |
| ⛔ 弹性行用裸 `fill` | 标题/固定块用 `N:fill`；大面积内容区绝不可用 `40:fill`（探针 A 实证压扁） |
| ⚠️ 静态校验 | 85/85 PASS（判据自修 4 处：io 文本模式吃 `\r\n`/Designer 合法 Dispose(bool)/两版 Span 载体/…）； |

## 背景

（待补：本决策要解决什么问题）

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

- [[decisions/ADR-069-PanelInnerGridZoneCells]] —— 布局规范（本 ADR 补「链完整性」与「行高弹性」两定理）
- [[decisions/ADR-071-SystemPageGridAndU4Rehome]] —— 批L/M 容器转换（本 ADR 修正其 tlpTrace 行高误判与链缺口）
- [[decisions/ADR-073-AxisControlUnifiedMontionManager]] —— 六轮演进③ 轴控制统一入口（固定按钮接线与 UI 直控归零）
- [[decisions/ADR-068-WeldAlgorithmsConfigZoneReorg]] —— 六轮演进② 推翻其 EnableMonotonicConstraint 唯一入口承载行
- [[api/SystemControlPage]] · [[api/ProcessControlPage]] · [[api/DataReviewerPage]]（左列表原型）
