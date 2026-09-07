---
title: 台达 EtherCAT UI 设计规范（AntdUI 版）
date: 2026-09-07
status: active
tags: [指南, 运控, 台达, UI, AntdUI, 监控]
---

# 台达 EtherCAT UI 设计规范（AntdUI 版）

> **定位**：台达运控在 **AdaWeldSystem** 的界面落地规范——主页面分区、新增弹窗清单、状态刷新机制、配色与控件映射。
> 原档 `raw/delta/台达EtherCAT_PVT与电子凸轮运动开发指南.md` 第四部分是**按另一个项目（`MasonMotionControl` 命名空间、WinForms 原生控件、`IUpdate` 接口）写的**，本页是其**到 AdaWeldSystem 的翻译层**，不是照抄。
> 前置：[[guides/DeltaEtherCAT-DevGuide]]（能力）、[[guides/DeltaEtherCAT-AdvancedMotion]]（PVT/ECAM2）、[[decisions/ADR-018-UIFrameworkMigration]]、[[decisions/ADR-019-DialogWindowToModalUserControl]]、[[modules/UIDesign]]。

## 章节导航

| 节 | 内容 |
|---|---|
| [§1 风格翻译对照表](#1-风格翻译对照表必读) | 原档 → 本项目，逐项映射 |
| [§2 在线与状态检查](#2-在线与状态检查无应用层心跳) | 7 项状态 API 与判定 |
| [§3 主页面设计](#3-motioncontrolpage-主页面改造) | 分区与新增入口 |
| [§4 新增弹窗清单](#4-新增弹窗清单subdialogmotiondialog) | 5 个弹窗与职责 |
| [§5 刷新机制](#5-刷新机制回调更新画面轮询只查状态) | 与既有教训对齐 |
| [§6 配置持久化](#6-配置持久化) | 走 FileOperate/XMLfile |
| [§7 落地检查清单](#7-落地检查清单) | 编码前逐项确认 |

---

## 1. 风格翻译对照表（必读）

> ⛔ **原档第四部分不可直接落地**：它假设的 `AxisControl` / `MachineInputIO` / `CylinderControl` / `IUpdate` **在本项目不存在**（属 `MasonMotionControl` 参考项目）。本项目的运控 UI 只有 `UIDesign/TabPage/MotionControlPage.cs` 一个页面。

| 维度 | 原档（MasonMotionControl） | **AdaWeldSystem 落地** |
|---|---|---|
| 命名空间 | `MasonMotionControl` | `AdaWeldSystem.Sub2UI`（TabPage 页）/ `AdaWeldSystem.Sub3UI`（SubDialog 弹窗） |
| 目录 | `MotionControl/UIControl/` | 页面 `UIDesign/TabPage/`；弹窗 `UIDesign/SubDialog/MotionDialog/`（**遵循 2026-09-07 按业务域拆分**） |
| 弹窗基类 | `System.Windows.Forms.Form` | `UserControl` + `AntdUI.Modal.open`（ADR-019，**禁** `AntdUI.Window`） |
| 文件命名 | `XxxDialog` / `XxxControl` | **`XxxForm`**（对齐用户 2026-09-07 改名：`ILScanDialog`→`ILScanForm`、`FormLogin`→`LoginForm`） |
| 表格 | `DataGridView` | **`AntdUI.Table` + `AntList<T>`**（禁用 DataGridView，见 [[modules/UIDesign]]） |
| 状态灯 | `Label.BackColor = Color.DarkGreen/Red` | **`AntdUI.Signal` / `AntdUI.Badge`**（原 UILight 已被取代，见 [[project/SunnyUI-Legacy]]） |
| 页签 | `TabControl` | `AntdUI.Tabs`（本项目惯例：**弃 Tab**，见 ADR-017；仅算法编辑为登记在案的特例） |
| 消息 | `MessageBox.Show` | `AntdUI.Message.*`（Toast）/`AntdUI.Modal.open`（模态）；**owner 用 `Form.ActiveForm`**（`UserControl` 不可隐式转 `Target`） |
| 布局 | 手工定位 / FlowLayoutPanel | `AntdUI.GridPanel` 或 `AntdUI.FlowPanel`（ADR-022 自由选择，非强制） |
| 配色 | `Color.DarkGreen/Red/Orange/Silver` | AntdUI 主题色；**选中态 #1677FF 文本/图标 + 浅灰底，禁自定义紫**（ADR-018） |
| 刷新接口 | `IUpdate` + `UpdateStatus()`/`ShowStatus()` | 本项目**无 IUpdate 接口**；用状态回调 + 单入口 `RefreshUi(scope)`（ILCamPage 范式，见 [[standards/UiStateSimplification]]） |
| 运控入口 | `MotionManager.GetMotionManager()` | **`MontionManager.Instance`**（本项目单例属性，非工厂方法） |
| 轴遍历 | `mgr.GetAxes()` | `MontionManager.Instance.MontionControl.GetAxes()` |
| 异步 | `Task` 起后台 | 长操作走工作流/后台线程；**UI 线程不阻塞**；`InvokeRequired` 封送（[[guides/WinForms-UI-Threading]]） |
| 持久化 | `XmlSerializer` 序列化配置类 | **`FileOperate/XMLfile.cs`**（ADR-036：无参 `LoadConfig`/`SaveConfig`，末尾必 `SaveXdocument()`） |

---

## 2. 在线与状态检查（无应用层心跳）

> 原档 4.2 结论正确：**PCI-L221 不需要应用层心跳**。EtherCAT 的 Working Counter（WKC）看门狗由主站卡硬件维护。上位机只读状态，不做心跳收发。
> ⚠️ 这与正运动的「心跳 + BAS 保护」不同——正运动删除后**不要**在台达侧复刻心跳线程。

| 状态维度 | API（`EtherCATMasterNative` / `EtherCATMotionNative`） | 判定 |
|---|---|---|
| 主站连接 | `CS_ECAT_Master_Get_Connect_Status` | `Status == 0` 正常 |
| WKC 看门狗 | `CS_ECAT_Master_Check_Working_Counter` | `Abnormal_Flag == 0` 且 `Working_Slave_Cnt == 期望从站数` |
| WKC 错误计数 | `CS_ECAT_Master_Get_Working_Counter_ErrorCounter` | 持续增长 = 通信质量差 |
| 帧计数 | `CS_ECAT_Master_Get_Frame_Counter` | `Frame_Error_Cnt` 持续增长 = 丢帧 |
| 周期耗时 | `CS_ECAT_Master_Get_Cycle_SpendTime` | 最大耗时超周期 = 延迟告警 |
| 从站连接 | `CS_ECAT_Slave_Get_Connect_Status` | `OpState == 3`(OP) 且 `AlarmStatus == 0` |
| 轴状态字 | `CS_ECAT_Slave_Motion_Get_StatusWord` | bit2(0x04)=使能；bit3(0x08)=故障 |

**OpState 色标**（沿用原档，映射到 AntdUI 语义色）：

| OpState | 含义 | 颜色 |
|---|---|---|
| 0 | Init | 灰（禁用/未知） |
| 1 | Pre-Operational | 黄（警告） |
| 2 | Safe-Operational | 橙（警告） |
| 3 | Operational | 绿（正常） |

⚠️ 上述 5 个 Master 级 API **尚未在本仓 `Native/EtherCATMasterNative.cs` 声明**，落地前需补（见 [[guides/DeltaEtherCAT-AdvancedMotion]] §6）。

---

## 3. MotionControlPage 主页面改造

**现状**（`UIDesign/TabPage/MotionControlPage.cs` 408 行 + Designer 630 行）：ADR-022 布局为「两行 65%/35%」——上行两列（标定参数面板 + 模拟测试面板），下行运动轴参数面板；已用 `AntdUI.Input` / `Message.success` / `Modal.open`；订阅 `LineLaserStateChanged`。

**目标分区**（保持既有三面板，新增顶部状态条与操作入口）：

```
┌──────────────────────────────────────────────────────────────┐
│ 【新增·顶部状态条】 台达主站 卡号:0 │ ●已连接 │ ●WKC正常 3/3 │
│                     帧错误 0 (0.000%) │ 周期 0.31/0.52ms       │
│                     [扫描总线] [总线诊断] [凸轮/PVT 配置]      │
├──────────────────────────────────────────────────────────────┤
│ 标定参数面板（保留）        │ 模拟测试面板（保留）             │
├──────────────────────────────────────────────────────────────┤
│ 运动轴参数面板（保留 + 每轴增「使能/报警」状态灯）             │
└──────────────────────────────────────────────────────────────┘
```

- 顶部状态条用 `AntdUI.GridPanel` 单行多列（对齐 ADR-022：值仅 `fill`/`%`/整数/浮点）
- 状态灯用 `AntdUI.Signal`（`OnColor`/`OffColor`/`State`，**大小写敏感 "On"**）
- 三个新按钮弹 `SubDialog/MotionDialog/` 下的 UserControl（Modal 承载）
- **模拟测试面板保留**：台达硬件未到位时仍需 SimulationC 模式（见 [[lessons/SimulationC-Mode-Interruption]]）

---

## 4. 新增弹窗清单（SubDialog/MotionDialog/）

> 目录遵循用户 2026-09-07 重构：`UIDesign/SubDialog/<业务域>Dialog/`。运控域命名为 `MotionDialog`。

| 文件 | 类型 | 职责 | 主要 API |
|---|---|---|---|
| `DeltaSlaveListForm.cs` | UserControl + Modal | 从站列表：序号/NodeId/名称/厂商ID/产品码/OpState/Alarm；`AntdUI.Table`；告警行标红 | `CS_ECAT_Slave_Get_Connect_Status` + `DeltaSlaveScanner` |
| `DeltaAxisConfigForm.cs` | UserControl + Modal | 轴参数：脉冲当量/最大速度/加减速/正负软限位/电子齿轮比 | `axis.Equiv/MaxVel/...` + `CS_ECAT_Slave_CSP_Set_Softlimit`、`CSP_Set_Gear` |
| `DeltaHomeConfigForm.cs` | UserControl + Modal | 回零参数：模式/方向/速度/偏移/加速时间（**ms**） | `Home_Config` 族 |
| `DeltaCamConfigForm.cs` | UserControl + Modal | 凸轮表：`AntdUI.Table` 编辑主/从位置点 + 曲线类型；生成正弦/梯形曲线；下载/啮合/脱离 | `ECAM2_Profile_Data` / `Profile_CamIn` / `Profile_CamOut` |
| `DeltaPVTConfigForm.cs` | UserControl + Modal | PVT 轨迹：点表（位置/速度/时间）+ 下载/启动/停止 + 进度与缓冲水位 | `PVT_Begin_Move` / `PVT_Continue_Move` / `PVT_Get_Information` |

**统一实现模式**（对齐 [[modules/UIDesign]] 与 AntdUI 范式）：

```
UserControl + Modal 承载（ADR-019）
  构造：XxxForm(业务对象) → InitializeComponent + 赋值（构造注入）
  私有字段：缓存当前状态（对齐 CurrentPos/IsServoON 模式）
  RefreshUi(scope)：单入口读状态 → InvokeRequired 封送 → 更新控件
  操作按钮：① 急停检查 ② 安全检查 ③ 长操作走后台线程，禁阻塞 UI 线程
  状态表示：AntdUI.Signal / Badge（绿=正常、红=报警、橙=警告、灰=无效）
```

⚠️ **Designer 约束**：`InitializeComponent()` 不得含 `for`/`while`/`if`/`switch`/`foreach`（[[guides/WinForms-Designer]]）；**不重写 `Dispose(bool)`**，非 UI 类用 `Dispose()` + `DisposeComponents()`（ADR-001/023）。

---

## 5. 刷新机制（回调更新画面，轮询只查状态）

> 沿用 [[lessons/IntelligentLaser-Pitfalls]] 的教训：**画面用回调/事件驱动刷新，轮询只用于查状态**，禁止用高频 `Timer` 轮询刷画面。

| 数据 | 机制 | 建议周期 |
|---|---|---|
| 主站连接 / WKC / 帧错误 / 周期耗时 | **轮询查状态**（`System.Windows.Forms.Timer`） | 500ms ~ 1s |
| 轴位置 / 速度 / 使能 | 跟随既有工作流状态回调；无回调时轮询 | 200~500ms |
| 报警 / 故障 | **事件驱动**（工作流状态变更） | 即时 |
| 凸轮/PVT 进度 | 弹窗打开期间轮询 | 200ms |

- 跨线程一律 `InvokeRequired` + `BeginInvoke`（[[guides/WinForms-UI-Threading]]）
- 不要在刷新回调里做 P/Invoke 重活；先读到字段再封送（对齐 `UpdateStatus()` → `ShowStatus()` 的两段式）

---

## 6. 配置持久化

⚠️ **不用 `XmlSerializer`**（原档做法）；本项目统一走 `FileOperate/XMLfile.cs`：

- 配置类提供**无参** `LoadConfig()` / `SaveConfig()`
- 写入末尾**必须**调用 `SaveXdocument()`
- 台达配置项：主站卡号、期望从站数、轴表（NodeId/SlotNo/Equiv/速度/软限位）、IO 映射、凸轮表、PVT 轨迹
- 当前状态：**台达配置体系尚未建立**（正运动 `MotionConfig.cs` 已删且未建替代），本项随弹窗一并落地

---

## 7. 落地检查清单

- [ ] 补 `EtherCATMasterNative` 的 5 个状态 API 声明（§2）
- [ ] 新建文件全部登记到 `AdaWeldSystem.csproj`（`Compile` + `EmbeddedResource` + `DependentUpon`）
- [ ] 弹窗用 `UserControl` + `AntdUI.Modal.open`，**禁** `AntdUI.Window`（ADR-019）
- [ ] 表格用 `AntdUI.Table`，禁 `DataGridView`
- [ ] 状态灯用 `AntdUI.Signal`，禁 `Label.BackColor`
- [ ] 无 `Dispose(bool)`；`InitializeComponent` 无流程控制
- [ ] `public` 成员带 XML 注释；日志纯文本无符号（[[standards/CodeSimplification]]）
- [ ] C# 7.3 语法（ADR-002）：禁 switch 表达式 / `init` / `record` / 可空引用
- [ ] 运控类型只经 `MontionManager.Instance`，UI 层**不出现任何 `Delta*` 类型**（ADR-039 分层铁律）
- [ ] 真编译待 Visual Studio（本沙箱无 C# 编译器）

---

## 相关页面

- [[guides/DeltaEtherCAT-AdvancedMotion]] — PVT / ECAM2 使用规范
- [[guides/DeltaEtherCAT-DevGuide]] — 台达模块落地规范
- [[guides/DeltaEtherCAT-Deployment]] — DLL 部署
- [[modules/UIDesign]] — UI 模块（含 2026-09-07 目录与命名对照）
- [[guides/AntdUI-Reference]] — AntdUI 开发范式（权威）
- [[decisions/ADR-018-UIFrameworkMigration]]、[[decisions/ADR-019-DialogWindowToModalUserControl]]、[[decisions/ADR-022-LayoutContainerFreedom]]

*来源：raw/delta/台达EtherCAT_PVT与电子凸轮运动开发指南.md 第四部分（原对齐 MasonMotionControl 风格），2026-09-07 翻译到 AdaWeldSystem / AntdUI 体系。*
