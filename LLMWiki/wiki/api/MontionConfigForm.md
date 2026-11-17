---
title: MontionConfigForm 运控配置窗体（已废弃）
date: 2026-09-16
updated: 2026-09-17
status: deprecated
tags: [API, UI, 运控, 配置, CSV, 气缸, SubDialog, TableLayoutPanel, AntdUI]
source: AdaWeldSystem/UIDesign/SubDialog/MotionControlDialog/MontionConfigForm.cs + .Designer.cs
---

> ⛔ **本页已废弃（2026-09-17）**：其全部功能（4 区合一 运控配置窗——CSV 导入/导出 + 输入/输出 IO 表 + 轴控表 + 气缸表 + 参数编辑器弹窗）已**整体迁移至 `SystemControlPage.panel1`**（见 [[api/SystemControlPage]]）。原 `MontionConfigForm.cs` + `.Designer.cs` + `.resx` 三件套已删除，仅保留本页作历史参考。
> **旧机制 → 处置 → 现行**：独立 `SubDialog` 弹窗 → 已删除 → 改为 `SystemControlPage`（`UIDesign.TabPage`，设计器生成）`panel1` 承载的 4 表 + CSV/XML 工具栏 + 参数编辑器 `Modal` 弹窗。
> ⚠️ 历史名称提示：本页记录已删除的 `MontionConfigForm.cs` / `.Designer.cs` / `.resx` 三件套（2026-09-17 整体迁入 `SystemControlPage.panel1`），下列文件名仅作历史参考。

# MontionConfigForm — 运控配置窗体（已废弃，仅作历史）

> **2026-09-16 新增**（ADR-022 落地轮）：台达运控的**离线配置编辑窗**——CSV 导入 / 导出、IO 信号操作、轴控配置、气缸操作四区合一，把 ADR-022 立下的「CSV 为电气交接格式」从工具类抬到可用界面。
>
> 类名按用户原样保留 **`Montion`**（与既有 `MontionManager` / `MontionAxis` 同款拼写），路径与命名空间用规范拼写 `MotionControlDialog`。

## 基本信息

| 项 | 值 |
|----|----|
| 类 | `AdaWeldSystem.UIDesign.SubDialog.MotionControlDialog.MontionConfigForm` |
| 基类 | `UserControl`（[[decisions/ADR-009-DialogWindowToModalUserControl]]：AntdUI 无 UIPage 基类，弹窗一律 UserControl + `AntdUI.Modal` 承载） |
| 文件 | `UIDesign/SubDialog/MotionControlDialog/MontionConfigForm.cs` + `.Designer.cs` + `.resx` |
| 挂载 | **本轮不挂入口**（`SystemControlPage` 未改动），仅落窗体本身；入口按钮后续按 VibeCoding 流程单独走 |
| 命名空间依赖 | `AdaWeldSystem.Comm.SystemComm`、`AdaWeldSystem.MotionControl`、`.MotionControl.IMotion`、`.MotionControl.DeltaEtherCAT` |

> ⚠️ **`using AntdUI;` 刻意不写**：本文件同时用到 `AntdUI.Message` 与 `System.Windows.Forms.Message`（`DialogResult` 语境），引入 `using AntdUI` 会造成 `Message` 二义性（CS0104）。全文一律 `AntdUI.` 显式限定。

## 界面构成（TableLayoutPanel 区域控制）

> 布局硬约束（用户指定）：**区域控制一律 `System.Windows.Forms.TableLayoutPanel`，禁用 `AntdUI.FlowPanel`**；每区外壳为 `AntdUI.Panel`；按钮一律 `AntdUI.Button`（`Ghost = true` + `BackHover = RGB(3,169,244)`）。

```
tableLayoutPanelRoot  (Dock=Fill, 1 列 × 4 行: 108F / 36% / 34% / 30%)
├── panelCsv        ← 行 0：CSV 通道区
│     └── tableLayoutPanelCsv (3 行: 30F 标题 / 42F 按钮栏 / fill 目录行)
├── panelIO         ← 行 1：IO 信号操作表
│     └── tableLayoutPanelIO  (3 行: 30F 标题 / 42F 按钮栏 / fill tableIO)
├── panelAxis       ← 行 2：轴控配置表
│     └── tableLayoutPanelAxis (3 行: 30F 标题 / 42F 按钮栏 / fill tableAxis)
└── panelCylinder   ← 行 3：气缸操作表
      └── tableLayoutPanelCylinder (3 行: 30F 标题 / 42F 按钮栏 / fill tableCylinder)
```

**区域 Panel 视觉范式**（逐字对齐 [[api/SystemControlPage]]）：`Back = White`、`BorderColor = RGB(217,217,217)`、`Shadow = 5`、`ShadowColor = Black`、`ShadowOpacity = 0.2F`、`ShadowOpacityAnimation = true`。

**CSV 区行 0 为 5 列**（`120F / 100% / 140F / 190F / 190F`）：`lblCsvDir` + `txtCsvDir`（`AntdUI.Input`，占列 1，**不跨列**）+ `btnBrowseDir`（列 2）；列 3/4 在行 0 留空，按钮栏落在行 1（`btnImportCsv` 跨 2 列 / `btnExportCsv` / `btnSaveConfig` / `btnReloadConfig`）。首版曾将 `txtCsvDir` 设 `ColumnSpan=3` 与 `btnBrowseDir` 的 `(2,0)` 冲突造成单元格重叠，已修正为「不跨列」。

## 三张表与行模型

三张表均 `AntdUI.Table` + `AntdUI.AntList<T>` 强类型绑定（禁用 DataGridView），列定义**在代码后置 `InitTables()` 内写入**（不在 `InitializeComponent()` 内赋 `ColumnCollection`，见 [[guides/AntdUI-Reference]]）。

| 表 | 行模型 | 列数 | 可编辑列 | 只读列 |
|----|--------|------|----------|--------|
| `tableIO` | `IORow` | 8 | Name / NodeId / SlotNo / BitNo / Enabled / Remark | Type、Status（实时电平） |
| `tableAxis` | `AxisRow` | 19 | 16 个配置列（AxisName…NegativeLimit） | Servo、Position、Speed（运行状态） |
| `tableCylinder` | `CylinderRow` | 9 | 8 个名称列（CylinderName…RetractAction） | Status（实时位置） |

**行模型三原则**：

1. **全 `string` 属性**——`AntdUI.Table` 单元格编辑回传的是文本，行模型属性一律 `string`，避免「编辑了但不落」的隐式转换陷阱；
2. **携带回写目标**——每行带 `DeltaAxisConfig` / `DeltaIOConfig` / `DeltaCylinderConfig` 的 **`Config` 引用**（`IORow` 另有 `IsInput`），`CellEndEdit` 校验通过后直接写回配置实例（ADR-022 的单一真相源）；
3. **配置列与运行列分离**——配置列取自 `DeltaMotionConfig.Axes/Inputs/Outputs/Cylinders`（离线可编可存盘），运行列取自 `MontionManager.Instance.Axes/IOs/Cylinders` 的**运行时对象**（只读秒级刷新），两者**不共用字段**（`DeltaAxisConfig.NodeId` 是配置项，`MontionAxis` 上根本没有 `NodeId`——只有 `AxisNo`）。

表设置：`EditMode = AntdUI.TEditMode.DoubleClick`（双击进入编辑）+ `列.SetEditable(true)` 逐列开启 + `AutoSizeColumnsMode = AntdUI.ColumnsMode.Fill`，与 [[modules/UIDesign]] 记载的 `ILParamForm.cs` / `AutoParamForm.cs` 同款范式。

## 关键方法

| 方法 | 说明 |
|------|------|
| `MontionConfigForm()` | ctor：`InitializeComponent()` → `InitTables()`（列定义 + Binding）→ `BindEvents()` → `LoadAll()` |
| `InitTables()` | 三表列定义（`new AntdUI.Column(key, 标题) { Width = "…" }.SetEditable(true)`）+ `EditMode` / `AutoSizeColumnsMode` + `Binding(_xxRows)` |
| `BindEvents()` | **事件一律代码后置订阅**（`Designer.cs` 手写订阅会被设计器重新序列化时丢失，范式见 [[modules/UIDesign]] 的 `ILParamForm.cs` 条目）：3× `CellClick` + 3× `CellEndEdit` + 19× `Click` + `timerRefresh.Tick` |
| `LoadAll()` | 顺序重载三表：`LoadIORows()` → `LoadAxisRows()` → `LoadCylinderRows()` |
| `GetConfig()` | `MontionManager.Instance.MoveData.MotionConfig`，`manager == null \|\| MoveData == null` 时返回 `null`（不抛） |
| `IsMotionReady()` | `MontionManager.Instance != null && IsInitialized`——**所有运行态读取与操作按钮的前置门控** |
| `TableIO_CellEndEdit` / `TableAxis_CellEndEdit` / `TableCylinder_CellEndEdit` | 按 `e.Column.Key` 分发校验，通过则写回行模型 + `Config`，**返回 `false` 拒绝提交**；签名与 `ILParamForm.cs` / `AutoParamForm.cs` 同款 `bool (object, AntdUI.TableEndEditEventArgs)`（见 [[modules/UIDesign]]） |
| `TableIO_CellClick` / `TableAxis_CellClick` / `TableCylinder_CellClick` | `AntdUI.Table` **无 `SelectedItem`**，以 `e.Record` 捕获选中行（[[guides/AntdUI-Reference]] 既实证范式） |
| `BtnImportCsv_Click` | 确认弹窗（`Confirm`，`AntdUI.Modal.open`）→ `MotionConfigImporter.Import(dir, ref msg)` |
| `BtnExportCsv_Click` | `MotionConfigImporter.Export(dir, ref msg)` |
| `BtnSaveConfig_Click` | `GetConfig().SaveConfig()` → `Config/MotionControl/Motion_XML/DeltaMotionConfig.xml` |
| `BtnReloadConfig_Click` | `GetConfig().LoadConfig()` → 重载后 `LoadAll()` |
| `BtnAutoRefresh_Click` | 切换 `_autoRefresh` + `timerRefresh.Start()/Stop()`（`Interval = 500`），按钮 `Text` 与 `Type` 同步（`AntdUI` 三态按钮范式） |
| `RefreshRuntime()` | 重建三表状态列后重绑——**只刷运行列**，不动配置列 |
| `ReadIOStatus` / `FillAxisRuntime` / `ReadCylinderStatus` | 逐行读取运行态，全部 `try/catch` 兜底为「读取失败」文本（UI 不得因单点读取异常整体崩） |

## 校验规则（编辑回写前置）

| 列 | 规则 | 拒绝后行为 |
|----|------|-----------|
| `Name`（IO） | 非空 + 同类 IO 表内唯一（`IsIONameFree`，编辑时 `ReferenceEquals` 排除自身） | `Message.warn` + `return false`（单元格保持编辑态） |
| `NodeId` / `SlotNo` / `BitNo` | `ushort`（0–65535）；`BitNo` 另限 **0–15**（ADR-022：台达位号 0–15） | 同上 |
| `Enabled` | 接受 `是/否`、`TRUE/FALSE`、`1/0`、空（`TryParseYesNo`） | 同上 |
| `Equiv` / 速度 / 时间类 | `double` + `CultureInfo.InvariantCulture` | 同上 |
| `MinVel` vs `MaxVel` | `MinVel > MaxVel` 拦截 | 同上 |
| 气缸 8 个名称列 | IO 引用必须在本轮配置的输入/输出表中存在（`CylinderIORefExists`） | 同上 |

## 运行操作（需运控已初始化）

| 按钮 | 前置 | 动作 |
|------|------|------|
| 选中输出置位 ON / 复位 OFF / 全部输出复位 OFF | 已初始化 + 选中行须为**输出**（选中输入时明确提示「选中的是输入信号，不能置位」） | `OutputIO.SetON()` / `SetOFF()` |
| 选中轴伺服使能 / 关闭 / 回零 / 停止 / 复位报警 | 已初始化 + 选中轴已在 `AxisRegistry` 装配 | `ServoOn()` / `ServoOff()` / `HomeNoBlock()` / `AxisStop((ushort)StopMode.Deceleration)` / `ResetAlarm()` |
| 选中气缸伸出 / 缩回 | 已初始化 + 选中气缸已在 `CylinderRegistry` 装配 | `Cylinder.Stretch()` / `Retract()` |

> **`Cylinder` 传感器语义陷阱**：`Cylinder.IsInStretch()` / `IsInRetract()` / `IsInCenter()` 对**未配置传感器**一律返回 `true`（源码 `return InXxxSensor == null || InXxxSensor.IsON();`）。故 `ReadCylinderStatus` 必须**先判传感器是否存在**再判到位，否则未接传感器的气缸会谎报「已伸出」：
> ```csharp
> bool hasSensor = cylinder.InStretchSensor != null
>     || cylinder.InRetractSensor != null
>     || cylinder.InCenterSensor != null;
> if (!hasSensor) return "无传感器";
> ```

## 设计约束

- ADR-002（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）：`.Designer.cs` 保留 1 处生成态 `protected override void Dispose(bool disposing)`；`.cs` 未重写。
- [[decisions/ADR-001-CS73-Constraint]]：无 `switch` 表达式 / `??=` / `is not` / `record` / `init` / `using var` / 范围运算符；属性初值写构造函数。
- [[guides/WinForms-Designer]]：控件声明与布局全在 `.Designer.cs`；`InitializeComponent()` 内**无控制流**。
- [[guides/Namespace-Compilation]]：命名空间 `AdaWeldSystem.UIDesign.SubDialog.MotionControlDialog` 随目录对齐（ADR-005）；三件套已注册 csproj（`.cs` 带 `<SubType>UserControl</SubType>`、`.Designer.cs` 与 `.resx` 带 `<DependentUpon>`）。
- **Message / Modal owner**：本文件用 `this.FindForm()`（与 `ILParamForm.cs`、`ILCamPage.cs`、`HelixRenderForm.cs` 等既有先例一致，见 [[modules/UIDesign]]），**未**采用部分 SubDialog 窗体的「注入 `private readonly Window Window`」写法——`AntdUI.Message.*(Form, string)` 与 `AntdUI.Modal.Config(Form, …)` 均接受 `Form`，两种写法并存于本项目。⚠️ [[modules/UIDesign]] 的「不用 `this.FindForm()`」表述与实际代码库不完全一致，取用时以本页为准。
- **日志**（ADR-007）：`Tag = "运控配置"`，直连 `GlobalCommData.ShowLog`，纯文本无符号，操作起止/结果处记录。

## 协作

- 导入 / 导出通道：`MotionControl/DeltaEtherCAT/MotionConfigImporter.cs`（[[api/MontionManager]] 同模块，ADR-022）。
- 配置真相源：`DeltaMotionConfig`（`Config/MotionControl/Motion_XML/DeltaMotionConfig.xml`，由 `MoveControlData` 持、[[api/MontionManager]] 单点对外）。
- 运行态：`AxisRegistry` / `IORegistry` / `CylinderRegistry`。
- 容器：[[modules/UIDesign]] 的 `SubDialog/MotionControlDialog/`。

---

*来源：AdaWeldSystem/UIDesign/SubDialog/MotionControlDialog/MontionConfigForm.cs + .Designer.cs*
