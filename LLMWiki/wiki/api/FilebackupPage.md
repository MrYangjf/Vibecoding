---
title: FilebackupPage 文档备份设置页（原 CommPage）
date: 2026-09-29
tags: [API, UI, 文档备份, 通讯配置, 工艺配置, 系统配置, 台达控制器, 配置包, NavPage, Tabs, ADR-025, ADR-026, ADR-079]
source: AdaWeldSystem/UIDesign/TabPage/FilebackupPage.cs + .Designer.cs
---

# FilebackupPage — 文档备份设置页（两 Tab 分区）

> 🔄 **2026-09-29 更名 + Tabs 改造（业主令）**：类与文件 `CommPage` → **`FilebackupPage`**（页面显示名由「通讯设置」改为「**文档备份设置**」）。根容器 **`tabsBackup`**（`AntdUI.Tabs`，`Type = Card`，`TabMenuVisible=false`，`Dock=Fill`），~~三页：① 通讯配置文件 → ② 工艺配置文件 → ③ 系统配置文件~~ ⇒ **2026-11-03 两页**：**① 通讯配置文件**（`tabPageCommCfg`）→ **② 系统配置文件**（`tabPageSystemCfg`）。两页索引 0/1，`SelectedIndex=1`（默认系统配置文件，不越界）。
> ~~业主需求原文：工艺/系统配置文件「将……内容导出成一个打包的文件备份到本地，支持单项保存打包也支持全部参数打包」——故每类备份均提供单项复制与整目录打包（zip）两级粒度。~~ ⇒ **2026-11-03 被业主推翻**：「工艺配置文件已经失去意义删除」⇒ 删除 `tabPageProcessCfg` 整页及其单项复制/整目录打包助手，备份能力统一由 `.awcfg` 整站包承接。

## 基本信息

| 项 | 值 |
|----|----|
| 类 | `AdaWeldSystem.UIDesign.TabPage.FilebackupPage`（2026-09-29 由 `CommPage` 更名） |
| 基类 | `UserControl`（由 NavPage 的 `AntdUI.Tabs` 挂载） |
| 文件 | `UIDesign/TabPage/FilebackupPage.cs` + `.Designer.cs` + `.resx` |
| 挂载 | `UIDesign/MainWindow/FormMain.cs` → `navPageParam.LoadTabs(…, ("文档备份设置", new FilebackupPage()))` |
| 命名空间依赖 | `AdaWeldSystem.Comm.Communication`、`AdaWeldSystem.Comm.SystemComm`、`AdaWeldSystem.MotionControl`、`AdaWeldSystem.MotionControl.DeltaEtherCAT`、`AdaWeldSystem.WeldParamControl`、`AdaWeldSystem.UIDesign.SubDialog.CommConfigDialog`、`AdaWeldSystem.FileOperate` |
| 新增程序集引用 | `System.IO.Compression` + `System.IO.Compression.FileSystem`（2026-09-29 登记，供 `ZipFile.CreateFromDirectory`；2026-11-03 页面侧整目录打包已删，引用保留供 `SystemConfigPackager` 使用） |

## 界面构成（两 Tab，`AntdUI.Tabs` `tabsBackup`）

> ⚠️ `AntdUI.Tabs` 添加页必须 **`Controls.Add` + `Pages.Add` 双写**（见 [[guides/AntdUI-Reference]] §3.3）。

| Tab | 控件 | 内容 |
|---|---|---|
| ① 通讯配置文件 | `tabPageCommCfg` → `tableLayoutPanel1` | 通讯通道唯一 RSI（KUKA 机器人）；机器人 panel 内启用开关、通讯周期下拉、打开配置、启动/关闭、调试面板、日志。2026-11-03 删除空页 `tabPage2`/`tabPage3` 与只切空页的 `radioPLC`/`radioEtherNet`；2026-11-17 删除 `radioRobot → tabs` 单向联动（无多页切换需求，控件 `tabs1` 与处理器 `OnRadioModeChanged` 一并移除） |
| ~~② 工艺配置文件~~ | ~~`tabPageProcessCfg` → `panelProcessCfg`~~ | **2026-11-03 整页删除（业主令）**：备份目录选择 + 5 个备份按钮 + 提示标签全部移除 |
| ②（原③）系统配置文件 | `tabPageSystemCfg` → `panelSystemCfg` | `gridSystemRoot` 上下两段：`gridBackupOps`（配置文档目录选择，4 控件）+ `gridDeltaConfig`（四视图预览 + 重载保存 + `.awcfg` 导出/导入）。**本页只有两类职能**：① 原始配置文档 → 项目 XML（`btnDeltaGen`，按钮文案「重载保存」）；② `.awcfg` 打包/解包（配置转移） |

### ~~备份目录~~（2026-11-03 随工艺页删除）

~~`txtBackupDir`（`AntdUI.Input`）由 `btnBrowseBackup`（选择目录）经 `AntdUI.FolderBrowserDialog`（`.DirectoryPath` + `.ShowDialog()`，非 WinForms `FolderBrowserDialog`）填充；未选择时回落到 `Application.StartupPath\Backup` 并自动创建。备份产物命名统一 `{yyyyMMdd_HHmmss}_{文件名|标签}`，同名覆盖。~~ ⇒ 控件与 `EnsureBackupDir`/`BackupSingleFile`/`BackupDirectoryZip`/`DefaultBackupDirPath` 均已删除；`Config\_import` 与 `Config\_backup` 由打包器/导入链自管。

### ~~② 工艺配置文件备份（`Config\WeldParamControl`）~~（2026-11-03 整页删除）

~~`btnBackupAlgoXml`（WeldParamControl.xml）/ `btnBackupAlgoIni`（WeldParamControlAlgorithm.ini）/ `btnBackupWeldIni`（WeldData.ini）/ `btnBackupParamDb`（AutoParamValue.db）/ `btnBackupProcessAll`（整目录 zip），备份前分别经 `FlushProcessConfig()` / `SaveCurrentAutoParam()` 落盘。~~ ⇒ 上述 6 个常量、5 个 Click 处理器与 `FlushProcessConfig()` 全部删除；这些文件改由 `.awcfg` 整站导出覆盖。

### ② 系统配置文件导入导出与备份（`Config\MotionControl`）

| 按钮 | 行为 |
|---|---|
| `btnBrowseDir` | 选择配置文档目录（新链路识别源）→ `ScanDeltaDirectory(dir)` |
| `btnDeltaGen` | 原始配置文档 → 项目 XML 唯一写入口，文案「**重载保存**」：重新解析当前目录并把结果写盘（内部 `DeltaControllerConfigImporter.Generate`，分节导入 CSV + 写 `WELD_HEAD_SLAVE`/`IO_MAP`；写前备份、失败零写入、成功后自动回读与重扫） |
| `btnExportPackage` / `btnImportPackage` | `.awcfg` 打包 / 解包（配置转移） |

> **2026-11-03 职能收口（业主口径）**：「这里不需要保存 XML，因为所有改动都是上面系统设置界面做修改保存。这里只做：1、从原始配置文件生成本项目的 xml。2、将设置打包生成配置转移。」
> - 删除 `btnSaveConfig`：各系统设置页已有各自保存入口、`btnDeltaGen` 成功后自动回读，本页再放等于第二入口；底层 `MotionConfig.SaveConfig()` 未动（系统设置页仍在用）。
> - 删除 `btnReloadConfig`：`btnDeltaGen` 成功后本就自动回读 `ReloadSystemConfig()`，无独立价值场景。
> - 删除 `btnExportCsv`：属反向出表，既非职能 1 也非职能 2；`MotionConfigImporter.Export` 方法体保留（运控模块另有调用方，且它是从存量 XML 生成模板的能力）。
> - `gridBackupOps` 7 → 4 控件，`Span="40:fill;fill:160 fill 160"`（以业主手工重排版式为基准增量删除，未回滚其版式）。

> **2026-11-03 控件审计（业主裁定）**：`gridBackupOps` 由 12 控件缩为 7（`Span="44:fill;160 fill 160;fill fill fill"`）。删除 `btnImportCsv`（被「生成 XML」内部 `Import` 覆盖）、`btnBackupMotionXml` / `btnBackupMotionCsv` / `btnBackupSystemAll`（被 `.awcfg` 导出与写前自动备份覆盖）、`lblSystemBackupTip`（描述对象已删）。**其后业主手工重排版式，`Span`/`Size` 以当前 `FilebackupPage.Designer.cs` 为准；本轮再按职能收口删至 4 控件，`Span="40:fill;fill:160 fill 160"`。**

> 2026-09-29 该组按钮由 [[api/SystemControlPage]]（原 `tabPageConfigIO`「导入导出」页）**整体迁入**——业主裁定「输入IO / 输出IO / 气缸操作取消掉，后续回归为各个系统参数设置；导入导出加入文件备份设置中的系统配置文件」。

## 关键方法

| 方法 | 说明 |
|---|---|
| `FilebackupPage()` | ctor：`InitializeComponent()` → 填 `selectRsiCycle` 选项并订阅 `SelectedIndexChanged`（事件订阅放代码后置，与 `ILCamPage` 同规约）→ `LoadConfig()` → 订阅 `GlobalCommData.CommunicationCommandReceived` + `GlobalCommData.CommLogViewEvent`（2026-11-17 ADR-106）→ 挂 `HandleDestroyed`（**2026-11-03 删 `txtBackupDir` 默认目录赋值；2026-11-17 删 `radioRobot.Checked = true`（初值已在设计器设置，联动逻辑移除）**） |
| `LoadConfig()` / `SaveConfig()` | 通讯配置：机器人通讯模式（固定 RSI）+ 启用开关 + RSI 周期下拉回显 |
| `selectRsiCycle_SelectedIndexChanged` | 经 `CommunicationManager.SetRsiCycleMs()` 写入 `RsiComm.CycleMs` 并持久化 `RobotServerXdoc` 的 `CYCLE`（4/12/24 ms） |
| `btnConfig_Click` | 按当前模式弹 `FileEditorForm` 编辑 `RobotServerXdoc` / `RobotClientXdoc`（连接参数唯一真相源） |
| `btnRobotStart_Click` / `btnRobotStop_Click` | `InitializeRobotComm()` + `ConnectRobot()` / `DisconnectRobot()`（统一走 Manager 门面，UI 不直调 RSI 实现）；结果按成功/失败落调试通讯日志，失败附 `RsiComm.LastError`。**2026-11-17 ADR-107**：入口先过 `TryPassCommAction` 门控，初始化中/关闭中拒绝设备动作 |
| `TryPassCommAction(string)` | 2026-11-17 ADR-107：通讯动作两档门控（关闭中 / 初始化中），参照 `ILCamPage.TryPassPageAction`；拒绝时弹提示并写页面日志 |
| `chkEnable_CheckedChanged` | 启用开关即监听开关：取消勾选调 `DisconnectRobot()` 并记录「监听关闭成功/失败」；勾选记录「已启用」 |
| ~~`EnsureBackupDir()` / `BackupSingleFile(...)` / `BackupDirectoryZip(...)` / `FlushProcessConfig()`~~ | **2026-11-03 删（仅工艺页消费）**；备份能力由 `SystemConfigPackager.Export` 承接 |
| `ReadDirInput(Input)` | 目录输入框读取，空引用按空串处理（`txtCsvDir` 仍在用） |
| `AppendLog(string)` | 跨线程 `Invoke` 追加到 `inputLog`，超 5000 字符截断前半 |
| `GlobalCommData_CommLogViewEvent(object,string)` | 2026-11-17 ADR-106：通讯过程日志（配置/启停/收发）显示入口，`Invoke` 封送后走 `AppendLog`；页面未打开时不接收（文件端由 `ShowCommLogForView` 已写 TcpMessageLog） |
| `DisposeComponents()` | 退订 `CommunicationCommandReceived` + `CommLogViewEvent`（UI 类用 `DisposeComponents`，⛔ 不重写 `Dispose(bool)`） |
| `InitDeltaConfigPanel()` | 装载四视图 `Segmented`、`EmptyHeader=true`、**可编辑表**（`EditMode=DoubleClick` + `CellEndEdit`/`CellClick` + 右键菜单）、挂 `SelectIndexChanged`；数据由 `ApplyDeltaView` 首帧读盘装载 |
| `LoadProjectXmlRows()` | 每次调用重新读盘：`new DeltaMotionConfig().LoadConfig(false)`（静默，⛔ 不再打印旧配置结论）；焊接头直接读运行期已装载的 `MontionManager.WeldHeadConfig.PdoMap`，⛔ 不再 `LoadWeldHeadConfig()`（否则每次切视图刷一条「焊接头配置加载完成」） |
| `ApplyDeltaView(index)` / `BindDeltaView(index)` | 切视图入口：`!IsDocumentSource() && !_tableEdits` 时先 `LoadProjectXmlRows()` 重新读盘，再 `BindDeltaView` 重建列（可编辑）与绑定；**含未保存手改时只重绑不读盘**，避免切视图吞掉编辑 |
| `IsDocumentSource()` | `_lastScan` 命中任一配置文档返回 true；文档源不重复读盘 |
| `ScanDeltaDirectory(dir)` | 调 `DeltaControllerConfigImporter.Scan` → 刷新四视图预览 + 状态条；**任何写盘前先在此识别与校验**；**脏标记时先弹确认**（重新识别将用目录文档覆盖手改）；成功/失败结论只走 `ShowLog`，不写通讯日志 |
| `UpdateDeltaStatusHint(index)` | 状态栏标注当前视图行数与「双击修改 / 右键增删行 / 导出 CSV」；四视图合计有行时 `btnDeltaGen` 可用 |
| `btnDeltaGen_Click` | 唯一写入口「重载保存」：**表格 = 唯一提交源** → `ValidateCurrentTables(out hints)`（脏视图行列定位报错、未编辑视图只给 `；提示：…`，有错误则零写入）→ `WriteTableSourceDirectory()` 导出 CSV 至 `ConfigTableStaging\edit_<ts>\`（轴力矩列按既有 XML 回填）→ `DeltaControllerConfigImporter.Generate(dir, PDO 行, out msg)` → 成功 `ClearDirty()` + `ReloadDeltaConfigOnly()` + `LoadProjectXmlRows()` 各一次（⛔ 不再二次 Scan、⛔ 不再重读焊接头、⛔ 不重载工艺/通讯） |
| `ReloadDeltaConfigOnly()` | 重载保存后回读：**只** `MotionConfig.LoadConfig(false)`（台达四块）；焊接头已在 `Generate` 内存同步并落盘，不重读；结论一条「已重载台达配置（轴/IO/气缸）与焊接头从站配置」 |
| `ReloadSystemConfig(bool)` | **仅** `.awcfg` 系统设置包导入使用（全量回读：运控 + 焊接头 + 工艺 XML/INI + 通讯）；⛔ 不得被「重载保存」调用 |
| `btnExportPackage_Click` | `SystemConfigPackager.Export(path, out msg)`（`.awcfg`） |
| `btnImportPackage_Click` | `SystemConfigPackager.Import(path, out msg)`，成功后回读校验 |

## RSI 通讯调试面板（2026-10-23）

| 区块 | 控件 | 说明 |
|---|---|---|
| 状态条 | `lblRsiStat` | 监听/在线状态 + 收发包数 + 最近上行码 + IPOC |
| 下行下发 | `selectTxCmd` + `txtTxPayload` + `btnSendTx` | 写入回复缓存，下一帧生效 |
| 焊参通道 | `lblTestPower`/`lblTestWire`/`lblTestWeldSpeed`/`lblTestWeave`/`lblTestCutWire` + 5 个输入 | 每行前新增参数释义标签：激光功率(W)/送丝速度(m/min)/焊接速度(mm/s)/摆幅(mm)/剪丝信号(1=请求) |
| 收发包监视 | `txtRsiRxPacket` / `txtRsiTxPacket` | 最近一帧 Rob/Sen 原文 |

> ⛔ **上行指令本地模拟已删除（2026-10-23 业主裁定）**：调试只针对真实连接的机器人，不再提供 `selectRxCmd`/`txtRxPayload`/`btnInjectRx` 本地注入；上行指令只能由机器人经 RSI 真实上报。

## 设计约束

- [[decisions/ADR-001-CS73-Constraint]]：C# 7.3，禁 `switch` 表达式 / `??=` / `is not` / `record` / `init` / `using var` / 范围运算符；属性初值写构造函数。
- [[decisions/ADR-002-DisposePatternFullCoverage]]：`.cs` 未重写 `Dispose(bool)`；页面销毁经 `HandleDestroyed` → `DisposeComponents()`。
- [[guides/AntdUI-Reference]]：目录选择用 `AntdUI.FolderBrowserDialog`（`.DirectoryPath` + `.ShowDialog()`），⛔ 不沿用 WinForms `FolderBrowserDialog`（见 [[guides/WinForms-Designer]] 立项以来的既有踩坑）。
- ~~**备份只读不写源**：单项/整目录备份一律从源路径复制，不改写、不迁移、不删源；仅 `FlushProcessConfig()` / `SaveCurrentAutoParam()` 属显式落盘。~~ ⇒ **2026-11-03**：页面级备份助手已删，`.awcfg` 导出只读打包（`AddFile` 读字节算 SHA256，不写源）；导入才写盘（staging → 备份 → 原子替换）。
- **日志**（ADR-007，2026-11-03 修正落点）：通讯页操作仍直连 `AppendLog`（页面内 `inputLog`）；**系统配置页（识别 / 预览 / 保存 / 包导入导出）只走 `GlobalCommData.ShowLog` + `lblDeltaStatus`**，⛔ 不进通讯日志。纯文本无符号；失败路径必须给出源文件/目录全路径或「第 N 行第 M 列」定位，便于现场定位。
- **通讯按钮日志落点（2026-10-22）**：通讯页的启用开关、监听开启/关闭、打开配置、保存配置、周期切换等操作**一律写 `AppendLog`**（调试界面通讯日志），不走 `GlobalCommData.ShowLog`，便于现场在调试页直接回溯操作结果。
- **通讯日志查看通道（2026-11-17 ADR-106）**：`inputLog` 同时承载两类通讯条目——本页按钮操作的 `AppendLog` 直写，以及 Comm 层经 `CommLogViewEvent` 推送的 RSI 通讯过程日志（配置/启停/收发/重连）。后者由 `ShowCommLogForView` 写 TcpMessageLog 文件 + 发事件，页面打开才显示、不打开仅文件记录。⛔ 主系统日志只留行为结果（成败反馈），过程不入 MainPage。
- **无 C# 编译器（历史记录）**：2026-09-29 该轮改动经 Python 静态校验（csproj 203 条路径缺失 0 / Designer 引用闭环 / 事件处理器闭环 / region 配对），当时真编译待 Visual Studio。**2026-11-02 已具备真实编译环境**：`MSBuild.exe`（VS18 Insiders）`/t:Rebuild /p:Configuration=Debug` 实测 `EXIT=0`，后续改动一律以真实编译为准（[[rules/KR-010-No-Compiler-Honesty]]）。

## 2026-11-02 台达控制器配置区与系统设置整站包（ADR-079）

### 界面

| 区块 | 控件 | 说明 |
|---|---|---|
| 系统配置根 | `gridSystemRoot` / `gridBackupOps`（`AntdUI.GridPanel`） | 替换原 `tlpSystemBackup`（4 列 8 行），既有 12 个按钮功能保留，`Span` 按 12 格 `fill fill fill` ×4 排布 |
| 台达配置区 | `panelDeltaConfig` → `gridDeltaConfig` | 目录选择 + 状态条 `lblDeltaStatus` |
| 滑移视图 | `segDeltaView`（`AntdUI.Segmented`） | 四视图：轴 / IO / 气缸 / 焊接头从站（索引 0~3，`Items` 与分支同步） |
| 可编辑表 | `tableDeltaView`（`AntdUI.Table`） | 列与数据源全部代码后置；**2026-11-03 改为可编辑**：`EditMode=TEditMode.DoubleClick` + 除 `Seq` 外全列 `Editable=true`，`CellEndEdit`（`bool` 返回，恒 `true` = 接受本次编辑）写回行对象并置脏标记；行增删/CSV 反向导出/重新识别经代码后置 `ContextMenuStrip`（`System.Windows.Forms` 全限定，避免 AntdUI 同名二义性），**不新增控件、不改 Designer 版式** |
| 写入口 | `btnDeltaGen` | 唯一写入口「重载保存」；**2026-11-03 起写入源 = 当前表格内容**（不再解析目录）：页面校验（`ValidateCurrentTables(out hints)`：脏视图阻断 / 未编辑视图只提示 + 行列定位）→ 表格按项目 CSV 表头写入 `ConfigTableStaging\edit_<ts>\` → `DeltaControllerConfigImporter.Generate(dir, PDO 行, out msg)` → 成功后 `ReloadDeltaConfigOnly()` + `LoadProjectXmlRows()` 各一次 |
| 包入口 | `btnExportPackage` / `btnImportPackage` | `.awcfg` 导出 / 导入 |

### 文档 → XML 映射

| 来源文件 | 识别特征 | 落点 |
|---|---|---|
| `轴配置表.csv` | 表头含 `AXIS_NAME` | `DeltaMotionConfig.xml` 的 `ROOT/AXES` |
| `IO配置表.csv` | 表头含 `IO_TYPE` | `ROOT/INPUTS` + `ROOT/OUTPUTS` |
| `气缸配置表.csv` | 表头含 `CYLINDER_NAME` | `ROOT/CYLINDERS` |
| `Wsx_ScanCut.xml`（ESI） | 结构判据：`EtherCATInfo/Vendor/Id` 存在（子元素），且存在一个 `Type` 节点带 `ProductCode`（属性优先、子元素兜底）。⛔ **不得取「文档顺序第一个 `Type`」**：真实文件的 `Descriptions/Groups/Group/Type`（分组标签、无 `ProductCode`）排在 `Descriptions/Devices/Device/Type` 之前，会把整份 ESI 判成「存在但未识别」。适用范围：任意符合 EtherCAT ESI 结构（`Vendor/Id` + `Type@ProductCode`）的供应商文件均可通过；判据不绑定厂商号，但**不能区分设备种类**（伺服 ESI 与焊接头 ESI 同构，同目录多 XML 时取首个命中） | **台达从站配置文档**：`ROOT/WELD_HEAD_SLAVE` 的 `VENDOR_ID` / `PRODUCT_CODE` / `REVISION_NO`；身份解析供生成与焊接头视图使用（2026-11-03 不再单列「台达从站」视图） |
| `EtherCAT协议.xlsx` | 表头含 `变量` + `SDO Index` + `PDO Index` | `WeldHeadSlave.xml` 的 `ROOT/IO_MAP/IO`（10 属性）；**唯一权威源** |

### 关键行为

| 项 | 行为 |
|---|---|
| 分级 | `Invalid` / `Partial` / `Ready`；`Invalid` 禁用 `btnDeltaGen`；`Partial` 可用（缺文件按分节跳过，存在但解析失败由 `GetParseFailures` 拦下写盘） |
| 按钮判据 | **2026-11-03 根因**：原判据 `scan.Level == Ready`，而 `Ready` 要求 3 CSV + ESI + xlsx 全齐且 PDO>0，任一缺失即保持灰色；改为 `Level != Invalid && IsDocumentSource()`（有效且至少一份文档成功解析） |
| CSV 导入 | 复用 `MotionConfigImporter.Import(dir, axes, ios, cylinders, ref msg)` 分节重载，不重写；只替换有文档的节，其它节保留原值 |
| 写前备份 | `ConfigBackupHelper` 备份 `DeltaMotionConfig.xml` + `WeldHeadSlave.xml` 到 `Config\_backup\<yyyyMMdd_HHmmss>\`；备份失败零写入 |
| 焊接头 | 复用 `WeldHeadSlave.xml` + `MontionManager.SaveWeldHeadConfig()/LoadWeldHeadConfig()`，仅新增 `IO_MAP` 节 |
| xlsx | 自研 `XlsxSheetReader`（`ZipFile` + `XDocument`），10 列逐列映射；58 行 = 56 PDO + 2 SDO-only；行数/列值/索引全部来自表，无 PDO 清单或 SubIndex 常量 |
| 数据来源 | 默认读项目 XML：轴/IO/气缸 ← `DeltaMotionConfig.xml`（`AXES/INPUTS/OUTPUTS/CYLINDERS`），焊接头 ← `WeldHeadSlave.xml`（`IO_MAP`）；选中目录识别后同一表格切换为文档源；状态栏前缀显式标注「数据来源：项目 XML / 配置文档（路径）」 |
| 空态 | 列表 0 行时状态栏明示「当前视图【X】暂无数据 —— 项目 XML 的 ROOT/… 为空节点」；`EmptyHeader=true` 保留表头，不表现为「没接上」 |
| 交叉校验 | ESI 与 IO 表的对象地址缺失/变量名不一致/PDO 位置错位只写 `Warning` + 页面提示，**以表为准、不回写** |
| 可追溯 | 生成时把 IO 表文件名/修改时间/行数写入 `IO_MAP` 的 `SOURCE_FILE / SOURCE_TIME / ROW_COUNT` 并记日志 |
| 回读 | `MotionConfig.LoadConfig()` + `MontionManager.LoadWeldHeadConfig()` + `WeldParamManager.LoadAlgorithmsConfig()`（同时覆盖 `Algorithm_XML` 与 `Algorithm_INI`）+ `CommunicationManager.ReloadFromDisk()`（`CommunicationConfig.xml` + `CommunicationSettings.ini` + `RobotServer.xml`） |
| 导出（2026-11-03 反转） | `.awcfg` = `manifest.json` + `config/`；`schemaVersion=1.1`、`scope=full-settings`；**`Config/` + `DataBase/` 递归全量**，仅排除 `DataBase\Product.db`（生产记录库）、`DataBase\Auth.db`（用户库）及其 `-wal/-shm/-journal` 与 `Config\_import\*`（staging）；manifest 逐文件列 `path/length/sha256` + `excluded` 清单及理由；不加密 |
| 导入 | staging → `scope`/`schemaVersion` → 拒绝 `..`/绝对路径/盘符 → 整站范围校验（`Config\`/`DataBase\` 开头且非排除项/非 staging）→ SHA256 → 备份 → 原子替换 → 失败回滚 |
| 日志 | 系统配置页的目录识别 / 预览跳过 / 重载保存 / `.awcfg` 导出导入**一律 `GlobalCommData.ShowLog` + `lblDeltaStatus`**，⛔ 不再写调试界面通讯日志 `inputLog`（通讯日志只留通讯条目，历史文本不清空）；通讯页操作仍按 2026-10-22 口径走 `AppendLog` |

> ⚠️ xlsx 中 `StartAngle`/`EndAngle` 的 `PDO SubIndex` 写 `5`，ESI 为 `6/7`；**以供应商表为准**，ESI 差异只告警不覆盖；供应商更新表后重新导入即生效。

### 表格可编辑与校验（2026-11-03，业主令）

| 视图 | 可编辑范围 | 校验规则（失败给「第 N 行第 M 列（列名）」且零写入） |
|---|---|---|
| 轴（19 列，全列可改） | 单元格改 + 右键新增/删除行 | 轴名称非空且唯一；节点号/槽位 0~255；启用 TRUE/FALSE；回零模式/软限位模式 0~255；当量/速度/时间/限位等为合法数值；启动速度 ≤ 恒速。⛔ 力矩三列不在预览表，保存时按既有 XML 回填 |
| IO（7 列，全列可改） | 单元格改 + 右键新增/删除行 | IO 名称非空且唯一；类型必须 输入/输出（落盘转 INPUT/OUTPUT）；节点号/槽位 0~255；位号 0~15；启用 TRUE/FALSE |
| 气缸（8 列，全列可改） | 单元格改 + 右键新增/删除行 | 气缸名称非空且唯一；伸出/缩回/中间传感器必须存在于 IO 表的**输入**名；伸出/缩出输出必须存在于 IO 表的**输出**名 |
| 焊接头从站（10 列，`Seq` 只读） | 单元格改 + 右键新增/删除行 | 变量名非空；**唯一性按对象索引复合键**（`PDO Index/SubIndex` 优先，全空退 `SDO Index/SubIndex`，仅 SDO 的 2 行同此）；SDO/PDO Index/SubIndex 为十六进制（支持 `0x`）。**变量名重复不是错误**（Rx/Tx 成对属正常结构），只给一条非阻断提示 |

- **提交源**：表格 → 临时 CSV（轴/IO/气缸）+ 表格 PDO 行（焊接头）→ `Generate(dir, pdoEntries, out msg)`；目录里的 xlsx 不参与，ESI 仅用于从站身份。
- **落盘后**：`ReloadDeltaConfigOnly()`（只重载台达四块，静默读盘）+ `LoadProjectXmlRows()`（表格回读一次）；成功只打印一次新配置结论。
- **反向出表**：右键「导出当前视图 CSV（反向）」按当前表格内容写 CSV（`AntdUI.FolderBrowserDialog` 选目录），导出文件名为 `轴配置表.csv` / `IO配置表.csv` / `气缸配置表.csv` / `焊接头PDO映射.csv`。

### 校验范围 = 只校验脏视图（2026-11-03 业主令）

> 业主只改轴视图「回零方式」，却被焊接头视图的「变量重复」拦下；根因是唯一性按变量名判 + 校验跑全部四视图。

| 项 | 口径 |
|---|---|
| 脏判定 | `_viewDirty[4]`（0=轴 1=IO 2=气缸 3=焊接头）：`MarkCurrentViewDirty(segDeltaView.SelectIndex)` 在 `CellEndEdit` / `AddDeltaRow` / `RemoveDeltaRow` 置位；`ClearDirty()` 在写盘成功、`ScanDeltaDirectory`、`.awcfg` 导入后复位 |
| 分流 | `MergeView(viewErrors, viewIndex, errors, hints)`：**脏视图**的问题进 `errors`（阻断、零写入）；**未编辑视图**同一批问题降 `hints`（状态栏 `；提示：…`，不阻断） |
| `_tableEdits` | 保留原单一职责（切视图不读盘覆盖手改 / 重新识别前二次确认），⛔ 不代替分视图脏判定 |
| 焊接头唯一键 | `DeltaControllerConfigImporter.BuildPdoObjectKey`：`PDO I/S` 优先 → `SDO I/S` → 空（空键按行号占位 + 提示）；十六进制归一（去 `0x`、`uint` 解析、`X4` 定宽）后再比 |
| 变量名重复 | 汇总为一条 `hints`：`变量名重复 N 组（Rx/Tx 成对出现属正常结构，非错误）` |
| 轴 / IO / 气缸 | 判据不变（轴名唯一 / IO 名全局唯一 / 气缸名唯一 + IO 引用分组校验）；IO 全局唯一与 `MotionConfigImporter.ImportIOs` 的单个 `HashSet` 口径一致，**不放宽** |
- **反向出表**：右键「导出当前视图 CSV（反向）」按当前表格内容写 CSV（`AntdUI.FolderBrowserDialog` 选目录），导出文件名为 `轴配置表.csv` / `IO配置表.csv` / `气缸配置表.csv` / `焊接头PDO映射.csv`。

### 列宽口径（2026-11-03，`tableDeltaView` 可用宽 1283）

| 视图 | 旧宽总和 | 溢出 | 新宽总和 | 策略 |
|---|---|---|---|---|
| 轴（19 列） | 1510 | +227 | **1280** | 名称/回零速度等固定够用，其余数值列压到 50~74 |
| IO（7 列） | 780 | −503（被 Fill 拉伸 1.65×） | **1280** | 名称 300、说明 520 吃剩余空间，其余 90~100 |
| 气缸（8 列） | 950 | −333（被 Fill 拉伸 1.35×） | **1230** | 名称/传感器 150~160，动作列 200 |
| 焊接头（10 列） | 1180 | −103（被 Fill 拉伸 1.09×） | **1280** | 变量 220、说明 255，`SDO/PDO SubIndex` 各 110 保证英文表头不截断 |

- `AutoSizeColumnsMode = Fill`：总和 > 可用宽时按比例**压缩**（轴视图因此把 110/90 压到 93/76，表头被截）；总和 ≤ 可用宽时按比例**拉伸**。故策略 = 让总和贴近 1283，长文本列（名称/说明/变量）占大头做弹性。
- `DpiStretch` 未在表格上设置（该属性属绘图控件；本项目仅 5 处 FormsPlot），表格 DPI 由 AntdUI 内部处理；`FilebackupPage` 的 `AutoScaleMode=None`，字体未显式设 = 继承默认（Microsoft YaHei UI 9pt）。

## 一次重载保存的日志口径（2026-11-03 业主令）

> 业主贴出真实日志：一次保存出现 6 条「焊接头配置加载完成」、`DeltaMotionConfig.xml` 同一时间戳目录下备份两次、末尾结论打两次。

| 项 | 口径 |
|---|---|
| 行数 | 一次成功保存 5 行（首次迁移旧键名时 +1 条 Warning）：①开始（目录/识别结论/跳过清单）②③备份（每文件一行）④写入结果 ⑤回读校验 |
| 重复来源（已收敛） | `FilebackupPage.LoadProjectXmlRows`（切视图，已删 `LoadWeldHeadConfig`）、保存后旧 `ReloadSystemConfig`（现为 `ReloadDeltaConfigOnly`，只重载台达四块）、`MotionConfigImporter.Import` 成功后摘要（已删）、`Generate` 分节摘要（并入结论）、页面 `重载保存成功 + message`（仅异常时补一条） |
| 备份一次 | `Generate` 建目录并备份两个 XML → `Import(..., backupFolder)` / `SaveConfig(backupFolder)` **复用同目录、不再重复备份**，也不单独打印「配置保存完成」 |
| 同秒去重 | `GlobalCommData.ShowLog` 内 `IsDuplicateWithinSecond`：同一秒 tag+级别+文本完全一致只出一条 |
| 时间制式 | 界面 `MainPage.LogAppend` / 页面 `AppendLog` 统一 `Log.FormatTimestamp` = `yyyy-MM-dd HH:mm:ss`（24h），与目录名 `yyyyMMdd_HHmmss` 一致 |
| **作用边界（业主令）** | **重载保存 = 台达四块**：`DeltaMotionConfig.xml`（AXES/INPUTS/OUTPUTS/CYLINDERS）+ `WeldHeadSlave.xml`（含 IO_MAP）；⛔ 不含工艺设置（`WeldParamManager.LoadAlgorithmsConfig`）、系统变量、通讯配置（`ReloadFromDisk`）；上层如需通知其他模块只走既有事件，⛔ 不顺手重载 |

## 协作

- 通讯配置真相源：[[api/CommunicationManager]]（`RobotServerXdoc` / `RobotClientXdoc` / `RsiCycleMs`）；KUKA 侧语义见 [[api/KUKARobot]]。
- 运控配置导入导出：`MotionControl/DeltaEtherCAT/MotionConfigImporter.cs`（[[api/MontionManager]] 同模块）；配置 XML = `Config\MotionControl\Motion_XML\DeltaMotionConfig.xml`。
- 工艺配置：[[api/WeldParamManager]]（`WeldAlgorithmsConfig` XML + INI、AutoParam 落 `AutoParamValue.db`）。
- 迁入来源：运控导入导出区 ← [[api/SystemControlPage]]；通讯页 ← 原 `CommPage`。
- 容器：[[modules/UIDesign]] 的 `NavPage` 参数界面实例。

## 相关页面

- 模块：[[modules/UIDesign]] · [[modules/Comm]] · [[modules/MotionControl]]
- 决策：[[decisions/ADR-025-CommModuleRefactor]] · [[decisions/ADR-026-RsiSemanticRewriteAndDualChannel]] · [[decisions/ADR-079-DeltaControllerConfigAndAwcfgPackage]]
- 上游页：[[api/ProcessControlPage]]（工艺设置，本页备份其落地文件） · [[api/SystemControlPage]]（系统设置，本页备份其落地文件）

---

*来源：AdaWeldSystem/UIDesign/TabPage/FilebackupPage.cs + .Designer.cs*

## 2026-10-23 通讯调试界面盘查（ADR-076）

### 已修正

| 项 | 修正 |
|---|---|
| **焊参通道写入无提示** | 「写入焊参通道」写入的是**回复缓存**，而生产链路 `WeldParamControlWorkflow.SendToRobot` **每拍**重写同一缓存 ⇒ 调试写入仅在下一个 IPO 周期内可见 | 追加提示日志：「生产链路每拍覆盖同一通道，本写入仅下一帧有效（焊接中立即被真实工艺值覆盖）」 |

### ⛔ 死控件 / 无效选项（已盘查，**待业主裁决**，本轮未改）

| 控件 | 现象 | 建议 |
|---|---|---|
| ~~`radioPLC`「西门子PLC」/ `radioEtherNet`「以太网通讯」~~ | 2026-11-03 已删这两个 Radio 与空页 `tabPage2`/`tabPage3`（历史现象：曾由 `OnRadioModeChanged` 切 `tabs1.SelectedIndex = 1/2`）；**2026-11-17 连带删除 `OnRadioModeChanged` 方法与 `tabs1` 悬空引用、ctor 的 `radioRobot.Checked`，编译恢复** | ADR-074「通讯通道唯一为 RSI」已落地 |
| `radioModeRSI`「通讯模式：RSI」 | `radioModeRSI_CheckedChanged` 是**空方法**，纯显示死控件；且与 radioRobot/radioPLC/radioEtherNet 构成第二组 Radio（两组混排） | 建议改为只读标签，或与「KUKA机器人」合并为一组 |
| `btnKeepConfig`「保存配置」 | `SaveConfig()` 只把 `chkEnableRobot.Checked` 再写一次 `IsRobotEnabled`（该 setter 本身已即时落盘 INI）⇒ 点它没有任何新效果，只弹一行日志 | 建议改为「通讯配置已生效」状态标签，或并入启用开关的即时落盘语义 |
| `_rsiDebugTimer` | 在 `.cs` 中 `new System.Windows.Forms.Timer()` ⇒ 违反 [[lessons/UiLayoutChangeSyncPitfalls]] 坑二附二（非可视组件应声明在 Designer + `this.components` 托管），且当前是手工 `Dispose()` | 迁入 Designer 托管（属规范洁癖项，不影响功能） |

### ⛔ 调试下行指令与系统告警共用单槽

`KukaRsiComm.SendTxCommand` 写 `_txCmd` / `_txPayload` / `_txSeq`（**单槽**），而 `DeviceControlWork.ReportAlarm` / `DoMotionBusFault` 也经 `SendRobotCommand(TxNG / TxAbort)` 写同一槽 ⇒ 调试下发的指令可能被告警指令顶掉，反之亦然（无排队/隔离）。本轮只报不改。
