---
title: ADR-079 台达控制器配置文档生成与系统设置整站配置包
date: 2026-11-02
updated: 2026-11-03
tags: [决策, 系统设置, 台达EtherCAT, 焊接头从站, 配置备份, 配置包, 文档识别]
status: accepted
---

# ADR-079 台达控制器配置文档生成与系统设置整站配置包

> **决策一句话**：配置文档按内容特征识别并生成项目 XML，系统设置页提供 `.awcfg` 整站导出/导入；复用既有导入与焊接头读写，不造第二套。

## 背景

业主在「文档备份设置 → 系统配置文件」页提出两项能力：

1. **配置文档 → 项目 XML**：`轴IO气缸配置模板/` 实为 6 个文件——`轴配置表.csv`、`IO配置表.csv`、`气缸配置表.csv`、`填写说明.md`、`填写说明.pdf`，以及**焊接头从站两份文件**：`Wsx_ScanCut.xml`（ESI，91994B）与 `EtherCAT协议.xlsx`（16824B）。业主明确这两份即焊接头文件。
2. **系统设置一键导出/导入**：~~导出只含系统设置（系统设置三页对应配置 + 台达控制器配置），不含工艺设置、不含数据库、不加密。~~ ⇒ **2026-11-03 口径反转**：除生产记录库 `Product.db` 与用户库 `Auth.db` 外，`Config/` 与 `DataBase/` 全部导出（`scope=full-settings`），不加密；详见「演进记录」。

关键事实（按真实文件核实）：

| 来源 | 真实结构 |
|---|---|
| `Wsx_ScanCut.xml` | `EtherCATInfo/Vendor/Id = #xE0000002`（WSX）；`Device/Type` 属性 `ProductCode=#x26483052`、`RevisionNo=#x00000006`；VendorId **不在 Type 属性上** |
| `Wsx_ScanCut.xml` | 6 个 PDO：Rx `#x1600/#x1601/#x1602`、Tx `#x1A00/#x1A01/#x1A02`，共 56 条有效条目（另 6 条占位 padding） |
| `EtherCAT协议.xlsx` | sheet 仅「扫描切」有数据；10 列：序号/变量/名称/数据类型/SDO Index/SDO SubIndex/Access/PDO Index/PDO SubIndex/说明；59 行 = 1 表头 + 58 数据 |
| `EtherCAT协议.xlsx` | 58 行中 **56 行有 PDO Index**，另 2 行（MCUVersion / MotorMCUVersion）仅 SDO（`0x2004`），无 PDO |
| 台达从站配置文档 | **即 `Wsx_ScanCut.xml`**（业主口径：台达主站下挂各轴，唯一额外从站 = 焊接头）；ESI 提供 Vendor/ProductCode/RevisionNo；节点号 ESI 无，取既有配置 |

## 决策

1. **五类文档内容特征识别 + 分级提示**
 - CSV 三表不只看文件名：`轴配置表.csv` 表头须含 `AXIS_NAME`、`IO配置表.csv` 须含 `IO_TYPE`、`气缸配置表.csv` 须含 `CYLINDER_NAME`，内容不符按「缺文件或内容不符」提示，⛔ 不得静默视为就绪。
 - ESI 按结构识别：`Vendor/Id` 存在（子元素），且存在一个 `Type` 节点带 `ProductCode`（属性优先、子元素兜底，命中后回溯 `Device` 取 `Name`）；⛔ 不绑定具体厂商号，⛔ 不取「文档顺序第一个 `Type`」（`Descriptions/Groups/Group/Type` 是分组标签且无 `ProductCode`）。xlsx 按表头含 `变量` + `SDO Index` + `PDO Index` 才认作焊接头 IO 表。
 - 分级：`Invalid`（非配置目录，禁生成）/ `Partial`（缺文件或内容不符：**按钮可用**，缺文件按节跳过并保留原配置，存在但解析失败由 `GetParseFailures` 整次拦下、零写入）/ `Ready`（三表 + ESI + IO 表齐备且 PDO 非空）。
 - **ESI 即台达从站文档**：ESI 存在即「台达从站」就绪，缺失清单只含三张 CSV 与焊接头 IO 表，⛔ 不再列「台达从站配置文档待补」。
 - ~~五视图「台达从站」由 ESI 驱动，列 `NODE_ID / NAME / VENDOR_ID / PRODUCT_CODE / REVISION_NO / ENABLED`，默认仅焊接头一行。~~ ⇒ **2026-11-03 删除该视图段**：台达下挂额外从站只有焊接头，已被「焊接头从站」视图覆盖，保留即为重复；ESI 身份解析保留（供生成 `WELD_HEAD_SLAVE` 与焊接头视图使用），`Segmented` 五 → 四视图，索引 0~3 与 `Items` 同步，无越界/错位。
2. **复用既有 CSV 导入，不重写**
 - 生成时轴/IO/气缸仍调 `MotionConfigImporter.Import(dir, ref msg)`（系统配置页「导入」按钮 `btnImportCsv_Click` 的既有能力）。
 - 替换语义 = **本次解析到的节整节替换**：内存 `clear + add` 后由 `DeltaMotionConfig.SaveConfig()` 落盘，`MASTER` / `WELD_HEAD_SLAVE` / `SEAM_TRACK` / `TA` / `PVT` 等其它节保留。
 - 旧 CSV 行为不变：`Import` / `Export` 方法签名与字段解析未改。
3. **焊接头复用既有 XML 与读写入口**
 - 现有 `Config\MotionControl\WeldHead_XML\WeldHeadSlave.xml` 与 `MontionManager.SaveWeldHeadConfig()/LoadWeldHeadConfig()` 即唯一读写路径；本次仅新增 `ROOT/IO_MAP/IO` 节承载 PDO 映射，⛔ 未新建第二套文件或读写器。
 - `WeldHeadSlave.xml` 结构：`ROOT/THRESHOLD`（温度/温升/气压阈值与延时）、`ROOT/GALVO`（默认振镜参数）、`ROOT/MOTOR/PULSE_PER_MM`、新增 `ROOT/IO_MAP/IO`（10 属性 `SEQ/VAR/NAME/TYPE/SDO_INDEX/SDO_SUB/ACCESS/PDO_INDEX/PDO_SUB/DESC`）。
 - 从站身份（`VENDOR_ID` / `PRODUCT_CODE` / `REVISION_NO`）沿用既有 `DeltaMotionConfig.xml` 的 `ROOT/WELD_HEAD_SLAVE` 节，经同一 `SaveConfig()` 落盘。
 - ESI 厂商号一律取 `EtherCATInfo/Vendor/Id`，不读 `Device/Type` 的 VendorId（该属性不存在）。
 - **节点号不在 ESI 里，不得编造**：优先取既有 `ROOT/WELD_HEAD_SLAVE/NODE_ID`（实际为子元素，不是属性），取不到或为 0 时表内标「待填」；生成沿用旧值，不写空值。
 - 从站 `ENABLED` 同样取既有 `ROOT/WELD_HEAD_SLAVE/ENABLED`，取不到标「待填」，不参与生成写入。
4. **xlsx 自研解析（无第三方库）**
 - **`EtherCAT协议.xlsx` = 唯一权威源**（供应商发来的参考文档，后续可能再变）：行数、列值、SDO/PDO 索引全部以表为准；ESI 仅作交叉校验（对象地址缺失、变量名不一致、PDO 位置与 ESI 顺序错位），**只写 `Warning` 日志并在页面提示，⛔ 不回写、不覆盖表值**。
 - ⛔ 不硬编码 PDO 清单与任何 SubIndex：代码中不出现 `0x7010/6` 这类字面量；供应商更新表后重新导入即生效。
 - 可追溯：生成时把 IO 表来源文件名、修改时间、数据行数写入 `WeldHeadSlave.xml` 的 `IO_MAP` 属性并记日志，供日后核对表版本。
 - `XlsxSheetReader` 用 `System.IO.Compression.ZipFile` + `XDocument` 解析 `sharedStrings.xml` / `sheet1.xml` / `mergeCells`，只读第一张表；⛔ 不引入第三方 xlsx 库、不加 `PackageReference`；解析器内不含任何列语义或协议常量。
 - `EtherCAT协议.xlsx` 10 列表头逐列映射到 `WeldHeadPdoEntry` 10 字段，列名大小写与空格归一化后匹配，缺列不猜测。
 - 58 行全量入 `IO_MAP`：56 条 PDO + 2 条 SDO-only（`PDO Index`/`PDO SubIndex` 为空，如实保留）。
 - **原表差异以表为准**：xlsx 中 `StartAngle`/`EndAngle` 的 `PDO SubIndex` 均写 `5`，ESI 为 `6/7`；生成侧按表值透传，ESI 差异只提示不覆盖，不再等待口径确认（业主已拍板以供应商表为准）。
5. **生成策略：按节替换 + 写前备份 + 校验失败零写入**
 - `Scan` 非 `Ready` 直接中止；写前 `ConfigBackupHelper.CreateBackupFolder()` 备份 `DeltaMotionConfig.xml` 与 `WeldHeadSlave.xml` 到 `Config\_backup\<yyyyMMdd_HHmmss>\`。
 - 备份失败即中止；`MotionConfigImporter.Import` 失败即中止；任何失败均不产生半截写入。
6. **`SaveConfig` 键名维持现状 + 旧键改名日志**
 - 写新键名不变（`STR_VEL`/`CONST_VEL`/`END_VEL`/`HOME_FIRST_VEL`/`HOME_SECOND_VEL`/`HOME_ACC`）。
 - 保存前 `LogLegacyKeyRename()` 统计旧键 `MIN_VEL`/`MAX_VEL`/`STOP_VEL`/`HOME_MAX_VEL` 并写 `Warning` 日志，⛔ 不静默改名。
7. **`.awcfg` 整站配置包（2026-11-03 起为 `full-settings` 全量设置）**
 - 包结构：单文件 zip，内部 `manifest.json` + `config/` 目录树；`manifest` 写 `schemaVersion=1.1`、~~`scope=system-settings`~~ ⇒ `scope=full-settings`、`machineModel`、`appVersion`、`exportedAt`、逐文件 `path/sha256/length`，以及 `excluded` 排除清单（逐项写明理由）。
 - **导出 = 目录递归，不是固定文件列表**：`Config/` 与 `DataBase/` 全量收集（`Directory.GetFiles(..., AllDirectories)`），按路径排序；跳过 `IsExcluded`（`Product.db` / `Auth.db` 及其 `-wal/-shm/-journal` 伴生文件）与 `IsStagingPath`（`Config\_import\*`）。
 - ~~导出白名单 **9 文件**（逐项，含两个 INI）：`Config\MotionControl\Motion_XML\DeltaMotionConfig.xml`、`Config\MotionControl\WeldHead_XML\WeldHeadSlave.xml`、`Config\WeldParamControl\Algorithm_XML\WeldParamControl.xml`、`Config\WeldParamControl\Algorithm_INI\WeldParamControlAlgorithm.ini`、`Config\WeldParamControl\Algorithm_XML\TaLaCurve.xml`、`Config\LineLaser\LineLaser_XML\LineLaserConfig.xml`、`Config\Comm\Communication_XML\CommunicationConfig.xml`、`Config\Comm\Communication_INI\CommunicationSettings.ini`、`Config\Comm\KUKARobot_RSI_XML\RobotServer.xml`；外加目录白名单 `Config\MainDeviceControl\Simulation_INI\*.ini`。~~ ⇒ **2026-11-03 被业主口径推翻**：旧白名单漏掉全部工艺配置/参数与系统参数，已改为整站递归。
 - 跟踪参数是 **XML + INI 双后端**：`WeldParamControl.xml` 与 `WeldParamControlAlgorithm.ini` 必须同时在包内，否则跨机导入后参数不一致。
 - manifest 逐文件列 `path` + `length` + `sha256`（大写十六进制），供导入前核对；缺失文件在导出处跳过并记 Warning，不进 manifest。
 - ~~⛔ 不含 `WeldData.ini`（工艺）、不含数据库、不加密；`scope` 字段防后续误扩大。~~ ⇒ **2026-11-03 反转**：`WeldData.ini`、`WeldParamControlWorkflow.xml`、焊接工艺库等工艺配置/参数全部纳入；仍排除生产记录库与用户库，不加密。
 - 导入链：staging 落盘 → `scope`/`schemaVersion` 校验 → 拒绝 `..`/绝对路径/盘符 → 整站范围校验（`Config\`/`DataBase\` 开头且非排除项/非 staging）→ SHA256 → 写前备份 → 原子替换 → 失败按备份回滚。
8. **UI：AntdUI.GridPanel + Segmented 四视图**
 - `tlpSystemBackup`（4 列 8 行）换 `AntdUI.GridPanel`；2026-11-03 控件审计后再删 5 个重复/占位控件（见「演进记录」）。
 - 新增台达控制器配置区：`AntdUI.Segmented` 四视图（轴/IO/气缸/焊接头从站）+ 只读 `Table`；列与数据源一律代码后置，Designer 只声明控件与挂事件。**2026-11-03 删「台达从站」段**（重复覆盖，见 §7 修订）。
 - **数据来源（2026-11-03）**：初始化即从项目 XML 装载（`DeltaMotionConfig.xml` 的 `AXES/INPUTS/OUTPUTS/CYLINDERS` + `WeldHeadSlave.xml` 的 `IO_MAP`），打开页面即有数据；选中目录识别后同一表格切换为文档源，状态栏显式标注「数据来源：项目 XML / 配置文档」，避免两源混淆。空节点视图明示「暂无数据」而非空白。
 - **读取时机（2026-11-03 业主裁定）**：项目 XML 源改为**每次切视图重新读盘**（`ApplyDeltaView` 内 `new DeltaMotionConfig().LoadConfig()` + `MontionManager.LoadWeldHeadConfig()`），不复用启动期内存快照；业主抱怨「看不到最新数据」，一次文件读取成本可接受。文档源（已选目录）不重复读盘。
 - 唯一写入口「生成 XML」；「导出/导入」为包级入口；表格本身不可编辑。
9. **回读校验走系统设置页既有路径**
 - 生成/导入后执行 `MotionConfig.LoadConfig()` + `MontionManager.LoadWeldHeadConfig()` + `WeldParamManager.LoadAlgorithmsConfig()` + `CommunicationManager.ReloadFromDisk()`。
 - `LoadAlgorithmsConfig()` 内部同时 `LoadConfig()`（`Algorithm_XML`）与 `LoadProcessIni()`（`Algorithm_INI`），**双后端一次回读**；`ReloadFromDisk()` 覆盖 `CommunicationConfig.xml` + `CommunicationSettings.ini` + `RobotServer.xml`，导入后无需重启。
 - 未写工艺分区，故不调 `LoadAlgorithmsZone(zone)`；全量 `LoadAlgorithmsConfig()` 已覆盖四分区，语义与系统设置页既有读取一致。

## 演进记录

- **2026-11-03 控件审计（业主裁定）**：系统配置页删除 `btnImportCsv`（`btnDeltaGen` 内部已复用 `Import` 并补写 `WELD_HEAD_SLAVE`/`IO_MAP`）、`btnBackupMotionXml` / `btnBackupMotionCsv` / `btnBackupSystemAll`（被 `.awcfg` 导出与写前自动备份覆盖）、`lblSystemBackupTip`（描述对象已删）。`gridBackupOps` 由 12 控件缩为 7，`Span="44:fill;160 fill 160;fill fill fill"`。
- ~~**保留判据**：`btnExportCsv` 是唯一「XML → CSV」反向能力（新链路无等价）；`btnSaveConfig` / `btnReloadConfig` 是运行时 ↔ XML 入口，与「文档 → XML」方向不同。~~ ⇒ **2026-11-03 被业主口径推翻**：反向出表与运行时↔XML 均不属本页两类职能，三键已删（见下条）；`MotionConfigImporter.Export` 方法体仍保留。
- **2026-11-03 空页清理**：`tabs1` 下 `tabPage2` / `tabPage3` 无子控件，连同只切空页的 `radioPLC` / `radioEtherNet` 一并删除；通讯通道唯一 RSI，`radioRobot` 保留。
- **2026-11-03 本页职能收口（业主口径）**：「这里不需要保存 XML，因为所有改动都是上面系统设置界面做修改保存。这里只做：1、从原始配置文件生成本项目的 xml。2、将设置打包生成配置转移。」⇒ `tabPageSystemCfg` **只有两类职能**：① 原始配置文档 → 项目 XML（`btnDeltaGen`）；② `.awcfg` 打包/解包。据此删除 `btnSaveConfig`（各系统设置页已有保存入口，属第二入口）、`btnReloadConfig`（`btnDeltaGen` 成功后自动回读，无独立价值）、`btnExportCsv`（反向出表不属两类职能；`MotionConfigImporter.Export` 方法体保留供运控模块其它调用方）。`gridBackupOps` 7 → 4 控件，以业主手工版式为基准增量删除。
- **2026-11-03 导出白名单补齐**：系统设置三页实际读写文件核查后，补入 `Config\WeldParamControl\Algorithm_XML\TaLaCurve.xml`（激光头控制曲线）、`Config\Comm\Communication_XML\CommunicationConfig.xml`、`Config\Comm\Communication_INI\CommunicationSettings.ini`、`Config\Comm\KUKARobot_RSI_XML\RobotServer.xml`（通讯三件）；白名单 5 → 9 文件 + `Simulation_INI/*.ini`。
- **2026-11-03 导入回读补通讯**：`CommunicationManager.ReloadFromDisk()` 新增（`Load()` + `INIFile.Reload()` + `RobotServerXdoc.LoadFromFilePath`），`FilebackupPage.ReloadSystemConfig()` 调用它，`.awcfg` 导入后通讯配置即时生效。
- **2026-11-03 删「台达从站」视图 + 表格对接项目 XML**：业主口径「台达下挂额外从站只有焊接头，已被焊接头从站视图覆盖」⇒ `Segmented` 5→4（轴/IO/气缸/焊接头从站），删除 `DeltaViewDeltaSlave`、`_deltaSlaveRows`、`BuildDeltaSlaveRows`、`DeltaSlaveRow`，索引 0~3 与 `Items` 同步；ESI 解析保留。根因：原只在 `ScanDeltaDirectory` 成功后填表，未选目录永远空、目录无效也不回落 ⇒ 新增 `LoadProjectXmlRows()`（INIT 即从 `DeltaMotionConfig.xml` 与 `WeldHeadSlave.xml` 装载）、`UpdateDeltaStatusHint()`（标注来源 + 行数/空态）。
- **2026-11-03 导出范围反转（业主原话）**：「一键导出功能我想的是将程序中除了生产记录数据库和用户数据库，生产记录除外的其他内容(各工艺配置、工艺参数、系统配置、系统参数)全部导出。」⇒ `SystemConfigPackager` 由 9 文件白名单改为 `Config/`+`DataBase/` 递归全量；`SchemaVersion=1.1`、`scope=full-settings`；manifest 新增 `excluded`（`Product.db`/`Auth.db`/`Config\_import\*` 及理由）；导入端 `IsWhitelisted`→`IsAllowedTarget`（保留 `..`/绝对路径/盘符拒绝）。排除项判定见下表。
- **2026-11-03 库文件归属判定**：`DataBase\Product.db` = 生产记录库（排除）；`DataBase\Auth.db` = 用户库（排除）；`DataBase\Config.db`、`AutoParamValue.db`、`FaultRecord.db` 均属设置/参数/故障记录，按「其余全部导出」纳入（未发现 `Product.db`/`Auth.db` 之外的生产记录库）。
- **2026-11-03 删除「工艺配置文件」页（业主原话）**：「工艺配置文件已经失去意义删除。」⇒ `tabsBackup` 三页 → 两页（0=通讯配置文件、1=系统配置文件），删除 `tabPageProcessCfg` 整页（`panelProcessCfg`/`tlpProcessBackup`/9 按钮/提示标签），连带删除仅该页消费的 `txtBackupDir`、`EnsureBackupDir`、`BackupSingleFile`、`BackupDirectoryZip`、`DefaultBackupDirPath` 及 6 个工艺路径常量；`SelectedIndex=1` 顺延指向系统配置文件（两页最大索引 1，不越界）。
- **2026-11-03 四视图列宽重配（业主原话）**：「表头文字字距/列宽不对，多个列被截断看不全。」根因：`AutoSizeColumnsMode=Fill` 且列宽总和 > 表格可用宽 1283（轴 1510，溢出 227px）时按比例压缩，窄语义列被压到 76~93px 致表头截断。⇒ 四视图改为「总和贴近 1283 + 名称/说明列吃剩余空间」：轴 1280、IO 1280、气缸 1230、焊接头 1280；焊接头 `SDO/PDO SubIndex` 各 110px 保英文表头完整。未引入横向滚动，未改业主版式。
- **2026-11-03 「生成 XML」→「重载保存」+ 判据放宽（业主原话）**：「选中目录后会自动加载，生成xml的按钮依然不可用……按钮名称修改为重载保存。」根因：`btnDeltaGen.Enabled = scan.Level == ConfigDirectoryLevel.Ready`，`Ready` 要求 3 CSV + ESI + xlsx 全齐且 PDO>0，任一缺失即灰色。⇒ 判据改 `Level != Invalid && IsDocumentSource()`（有效且至少一份文档解析成功）；按钮语义 = 重新解析当前目录并写盘为项目 XML；缺文件按分节跳过并保留原配置（`MotionConfigImporter` 增分节重载），存在但解析失败由 `GetParseFailures` 整次拦下、零写入。状态栏对 `Partial` 显式「已加载，可保存（缺文件节跳过）」/「已加载，保存被拦截」。
- **2026-11-03 送丝电机力矩模式（CST）**：`DeltaMontionAxis.SetTorque` 由「只调 `CST_Start_Move`」补齐为「置 CST 模式 → 下发目标扭矩/扭矩爬升速率 → 开扭矩输出」；`StopTorque` 为「关输出 → 切回 CSP」；任何一步失败 `RestoreCspMode()` 回滚，杜绝半使能。`MontionManager` 新增送丝轴唯一写口 `WireFeedTorqueModeEnabled`/`GetWireFeedAxis`/`GetWireFeedAxisConfig`/`SetWireFeedTorqueMode`/`SetWireFeedTorque`/`StopWireFeedTorque`，键表 `WireAxisKeys`，形态与 TA 一致；`DeltaAxisConfig.TorqueModeEnabled` 仍由轴配置 XML `TORQUE_MODE` 驱动。
- **2026-11-03 ESI 判据修正（`Wsx_ScanCut.xml 存在但未识别`）**：真实文件 `Descriptions/Groups/Group/Type`（`WSX_Cut`，无 `ProductCode`）在文档顺序上早于 `Descriptions/Devices/Device/Type`，而 `TryParseEsi` 取「首个 `LocalName==Type`」，导致 `ProductCode` 读空、整份 ESI 判未识别，`Generate` 被 `GetParseFailures` 拦下（按钮可用但保存被拦截）。⇒ 改为取「首个带 `ProductCode` 的 `Type`」（属性优先、子元素兜底，命中后回溯 `Device` 父节点取 `Name`），`RevisionNo` 同样双形态兜底；判据仍为结构判据（`Vendor/Id` + 某 `Type` 带 `ProductCode`），⛔ 不绑定厂商号。适用范围：任意符合 EtherCAT ESI 结构的供应商文件均可通过；但**不区分设备种类**（伺服与焊接头 ESI 同构，同目录多 XML 取首个命中）。

## 备选方案

| 方案 | 结论 |
|---|---|
| 新建第二套焊接头配置 XML/读写器 | 放弃：既有 `WeldHeadSlave.xml` + `Save/LoadWeldHeadConfig` 已覆盖阈值/振镜/电机，扩展 `IO_MAP` 即可 |
| 重写 CSV 导入器 | 放弃：`MotionConfigImporter.Import` 是系统配置页既有「导入」能力，重写会破坏旧行为 |
| 引入第三方 xlsx 库（EPPlus/NPOI） | 放弃：业主明确自研 `ZipFile`+`XDocument`，不加依赖 |
| 整文件覆盖 `DeltaMotionConfig.xml` | 放弃：会丢失 `MASTER`/`SEAM_TRACK`/`TA`/`PVT` 等未解析节，违背「按节替换」 |
| ~~导出包含工艺设置或数据库~~ | ~~放弃：业主明确只含系统设置，`scope` 固化防止误扩大~~ ⇒ **2026-11-03 被业主推翻**：改为整站导出，只排除生产记录库/用户库 |
| 静默忽略台达从站（ESI）缺失 | 放弃：ESI 即台达从站文档，缺失必须分级提示、禁生成 |
| 改写 xlsx 中 `StartAngle/EndAngle` 的 PDO SubIndex | 放弃：不得自行编造列语义，先透传并标注差异，待业主确认 |

## 实施约束

- [[decisions/ADR-001-CS73-Constraint]]：C# 7.3；⛔ `switch` 表达式 / `??=` / `is not` / `record` / 范围运算符。
- [[decisions/ADR-005-NamespaceDirectoryAlignment]]：新类落 `MotionControl\DeltaEtherCAT` 与 `FileOperate`，命名空间随目录。
- [[decisions/ADR-033-ConfigArchitectureStandard]]：备份目录固定 `Config\_backup\<yyyyMMdd_HHmmss>\`，配置路径不跨模块。
- [[decisions/ADR-071-SystemPageGridAndU4Rehome]]：分格一律 `AntdUI.GridPanel`；[[decisions/ADR-062-InpageZoneGridPanelLayout]]：GridPanel 逆序入格。
- [[decisions/ADR-036-UIControlPlacementRule]]：新控件由 `FilebackupPage.Designer.cs` 声明，`resx`/`csproj` 三处同步。
- 日志统一 `GlobalCommData.ShowLog`，时间戳为真实执行时间；⛔ 页面不得静默吞异常。
- 导入路径安全：拒绝 `..`、绝对路径、盘符；校验失败零写入。

## 后果

### 正面

- 配置文档到项目 XML 的链路可复现、可预览、可回读，且旧 CSV 导入行为不变；台达从站由 ESI 直接驱动，无需第二份从站文档。
- 焊接头 PDO 映射进入既有 `WeldHeadSlave.xml`，不分裂配置源。
- `.awcfg` 整站包把工艺配置、工艺参数、系统配置、系统参数一次带走（`full-settings`），跨机迁移不再漏项。
- 送丝轴力矩走与 TA 同一形态，单一写口 + 失败回滚 CSP，UI 不另存状态位。
- 写前备份 + 零写入 + 回滚，现场误操作可恢复。

### 负面

- `IO_MAP` 的 58 条含 2 条 SDO-only，命名上需在说明中区分；后续消费方须以 `PDO_INDEX` 空值判断。
- xlsx 与 ESI 的 `StartAngle/EndAngle` PDO SubIndex 不一致：以表为准、仅告警；供应商再发表时以新表重新导入即可。
- 台达从站节点号在 ESI 中不存在，只能沿用既有配置；未配置时显示「待填」，需现场扫描后回填。
- 每次 `SaveConfig` 均产生一份时间戳备份目录，长期运行需定期清理（未纳入本轮自动清理）。
- 整站导出会把 `DataBase\Config.db` 等库文件一并打包；库在运行中被占用时 `File` 读取可能失败（`AddFile` 记 Warning 跳过），导出前建议停在非写入态。
- 每次切视图重新读盘会多一次 XML 解析；预览读盘已改 `LoadConfig(false)` 静默，不再反复打印旧配置结论。

## 演进记录（2026-11-03）：表格可编辑 + 表格 = 唯一提交源 + 日志落点

### 业主诉求

1. 「系统文件内展示配置的 Table 是可编辑并且能生效（导入后发现问题直接改 table，点保存重载生效）」。
2. 「我导入新表时日志不需要在通讯日志显示」。
3. 首次导入时旧配置结论（`[台达运控] 配置加载完成 卡号 0 轴 4 个 输入 0 个…`）重复刷屏，之后才打印新识别结果。

### 决策

| 项 | 决策 |
|---|---|
| 可编辑 | `tableDeltaView.EditMode = TEditMode.DoubleClick`；除 `Seq` 外全列 `Editable=true`；`CellEndEdit` 返回 `bool`（恒 `true` = 接受编辑）并写回行对象；行增删 / 反向导出 / 重新识别经代码后置 `System.Windows.Forms.ContextMenuStrip`（全限定避免 AntdUI 同名二义性），不新增控件、不改 Designer 版式 |
| 脏标记 | `_tableEdits`：切视图只重绑不读盘；重新识别/`.awcfg` 导入前弹确认，明示会覆盖手改 |
| 提交源 | 「重载保存」不再解析原目录：页面校验（「第 N 行第 M 列（列名）」定位，失败零写入）→ 当前表格导出 CSV 到 `ConfigTableStaging\edit_<ts>\`（**不落 `Config\_import`**，该目录被整站包排除且整页替换会清空）→ `Generate(dir, pdoEntries, out msg)`；焊接头 PDO 直接取表格行，ESI 仅提供从站身份；轴 `TORQUE_*` 按既有 XML 回填 |
| 回读 | 成功后 `ReloadSystemConfig()` + `LoadProjectXmlRows()` **各一次**，⛔ 不再二次 `ScanDeltaDirectory`（旧实现会重复打印识别结论） |
| 旧配置刷屏根因 | `LoadProjectXmlRows()` 每次切视图 `new DeltaMotionConfig().LoadConfig()` → 该方法无条件打印「配置加载完成」；四视图切换 + 页面构造叠加 `FormMain.cs` / `MontionManager` 启动期 `MoveData.Load()` ⇒ 旧值多遍。改为 `LoadConfig(bool writeLog)`，预览传 `false` |
| 日志落点 | 系统配置页识别 / 预览 / 保存 / 包导入导出全部改为 `GlobalCommData.ShowLog` + `lblDeltaStatus`，⛔ 不进调试界面通讯日志 `inputLog`；通讯页条目与历史文本保持原样 |
| ESI 差异 | 口径不变：仅告警不覆盖，逐条列出对象地址与「表值/ESI 值」，以 IO 表为准 |

### 后果

- 业主可直接在表内改错并保存生效，避免「改 CSV 再重导」的往返。
- 保存链路只回读一次，日志不再出现旧配置刷屏。
- 表格全部行被删除时按「缺节跳过」处理（不写该 CSV），不会把旧节误清空。

## 演进记录（2026-11-03 第二段）：一次重载保存的日志收敛 + 24 小时制

### 业主日志证据

一次保存出现 6 条「焊接头配置加载完成」；`DeltaMotionConfig.xml` 在同一时间戳备份目录里被备份两次；末尾「重载保存完成」打两次；日志 `03:22:08` 与目录名 `edit_20261103_152208`（15:22:08）对不上。

### 决策

| 项 | 决策 |
|---|---|
| 6 次来源 | `MontionManager.cs:90`（构造）、`FilebackupPage.cs` 旧 `LoadProjectXmlRows`（切视图，已删调用）、`FilebackupPage.ReloadSystemConfig`（保存后，已改 `false`）、`SystemControlPage.cs:1493` / `ProcessControlPage.cs:496`（各自页面初始化，不同操作，保留） |
| 预览 | `LoadProjectXmlRows()` 焊接头直接读运行期 `WeldHeadConfig.PdoMap`，⛔ 不再 `LoadWeldHeadConfig()` |
| 回读 | 保存后 `ReloadSystemConfig(false)`：`MotionConfig.LoadConfig(false)` 静默；焊接头已在 `Generate` 内存同步并落盘，不重读；结论只留一条「回读校验完成」 |
| 备份一次 | `Generate` 建目录并备份两个 XML → `MotionConfigImporter.Import(..., backupFolder)` → `DeltaMotionConfig.SaveConfig(backupFolder)`：**非空 backupFolder = 批量保存，跳过本类备份与完成日志**；空 = 系统设置页单存，仍自行备份并打印 |
| 结论单条 | `Import` 摘要改为仅随 `msg` 上抛（`Debug` 也会进界面日志，故不降级而是不再打印）；`Generate` 分节明细并入末尾「重载保存完成」；页面仅在异常路径补「重载保存失败」 |
| 同秒去重 | `GlobalCommData.ShowLog` 增 `IsDuplicateWithinSecond`：同一秒 tag+级别+文本完全一致只输出一次，不同文本不合并 |
| 24 小时制 | 新增 `FileOperate.Log.FormatTimestamp(DateTime)` = `yyyy-MM-dd HH:mm:ss`；`MainPage.LogAppend` 与页面 `AppendLog` 统一调用，⛔ 不再各点写 `hh` |

### 后果

- 一次成功保存固定 5 行（①开始 ②③备份 ④写入结论 ⑤回读校验），首次旧键名迁移多 1 条 Warning。
- 同一份 XML 一次操作只备份一次、只打印一条「已备份」。
- 日志与目录名时间制式一致（实测 `LOG=2026-11-03 15:22:08` / `DIRNAME=edit_20261103_152208`）。

## 演进记录（2026-11-03 第三段）：明确「重载保存」作用边界

### 业主原话

「系统配置文件中重载保存是对导入的台达配置（轴/IO/气缸/焊接头从站的保存重载）。不是对系统变量和工艺设置那些进行重载保存。」

### 决策

| 项 | 决策 |
|---|---|
| 作用范围 | **仅台达四块**：`DeltaMotionConfig.xml`（AXES/INPUTS/OUTPUTS/CYLINDERS）+ `WeldHeadSlave.xml`（含 IO_MAP） |
| 超范围调用（已移除） | `FilebackupPage.ReloadSystemConfig(bool)` 内的 `WeldParamManager.LoadAlgorithmsConfig()`（工艺 XML+INI）、`CommunicationManager.ReloadFromDisk()`（通讯 XML/INI/RSI）、`MontionManager.LoadWeldHeadConfig()`（已落盘同步，无需重读） |
| 收窄实现 | 新增 `FilebackupPage.ReloadDeltaConfigOnly()`：只 `MotionConfig.LoadConfig(false)`，一条结论「已重载台达配置（轴/IO/气缸）与焊接头从站配置」 |
| 全量回读保留 | `ReloadSystemConfig(bool)` 仅 `.awcfg` 系统设置包导入使用（该操作本身含工艺/通讯文件，属包导入而非重载保存） |
| 事件通知 | 其他模块如需感知新配置，只走既有事件；⛔ 不顺手重载其配置 |
| 无副作用 | 保存路径不再出现 `WeldParamManager` / `CommunicationManager` / `LoadWeldHeadConfig` 调用，工艺参数、系统参数、通讯配置的内存值不被本操作改动 |

### 后果

- 一次重载保存日志收敛为：开始 → 备份（两行）→ 写入结论（含备份路径）→ 一条台达配置重载结论。
- 状态栏文案 = 结论原文（不再重复「重载保存成功：重载保存完成：」）。

## 演进记录（2026-11-03 第四段）：焊接头唯一性 = 复合键 + 只校验脏视图

### 业主证据

只改轴视图「回零方式」，点「重载保存」却被焊接头视图拦下：第 36~58 行「变量重复 Pattern / Frequency / Width / …」。

### 决策

| 项 | 决策 |
|---|---|
| 焊接头唯一键 | **复合键** `DeltaControllerConfigImporter.BuildPdoObjectKey`：`PDO Index/SubIndex` 优先，两者全空时退 `SDO Index/SubIndex`；十六进制先归一（去 `0x`、`uint` 解析、`X4` 定宽）再比 |
| 仅 SDO 行 | 2 行无 PDO 的按 `(SDO Index, SDO SubIndex)` 唯一；两列全空才算「无键」，以行号占位并给出提示 |
| 变量名重复 | **不是错误**：同一变量在 Rx（`0x1600+`）与 Tx（`0x1A00+`）成对出现是 ESI/IO 表正常结构，只汇总成一条非阻断提示（`变量名重复 N 组`） |
| ⛔ 反例 | 不得仅按 `VarName` 判唯一（旧实现即此，必然整片误报，且与用户改哪个视图无关） |
| 脏判定口径 | `_viewDirty[4]`（0=轴 1=IO 2=气缸 3=焊接头），由 `MarkCurrentViewDirty(segDeltaView.SelectIndex)` 在 `CellEndEdit` / `AddDeltaRow` / `RemoveDeltaRow` 置位；`ClearDirty()` 在写盘成功、`ScanDeltaDirectory`、`.awcfg` 包导入后复位 |
| 分流规则 | `MergeView`：脏视图的问题进 `errors`（阻断）；未编辑视图同一批问题降 `hints`（仅状态栏 `；提示：…`，不阻断） |
| `_tableEdits` | 保留原单一职责（切视图不读盘覆盖手改 + 重新识别前二次确认）；与 `_viewDirty` 由 `MarkCurrentViewDirty` / `ClearDirty` 同步维护，⛔ 不用它替代分视图脏判定 |
| 轴唯一性 | 按 `AXIS_NAME` 唯一 —— 保持（轴名是现场寻址键） |
| IO 唯一性 | 按 `IO_NAME` **全局**唯一 —— 保持，不放宽：`MotionConfigImporter.ImportIOs` 用**单个** `HashSet` 覆盖输入+输出两类行（`IO_TYPE` 不同也判重），页面口径与导入器一致；同名跨类型会让气缸的输入/输出引用产生歧义（`CheckIORef` 分两组取名） |
| 气缸唯一性 | 按 `CYLINDER_NAME` 唯一 + 五个 IO 引用按输入/输出分组校验 —— 保持 |
| 作用边界 | 仍**仅台达配置**（轴/IO/气缸/焊接头从站），与工艺设置、系统变量、通讯配置无关；日志文案「重载保存完成：仅重载台达配置（…）」 |

### 后果

- 现场 58 行焊接头数据 + 只改轴 `HOME_MODE` 的场景可正常保存：阻断错误 0，状态栏附一条「变量名重复 28 组（Rx/Tx 成对出现属正常结构，非错误）」。
- 真正的对象索引重复（如两行同 `PDO 1600/0001`）在焊接头视图为脏时仍被拦下（`对象索引重复 PDO …`），未放宽实质校验。

## 相关页面

- [[api/FilebackupPage]] —— 系统配置页 UI 与生成/导出/导入入口
- [[modules/MotionControl]] —— 运控配置、焊接头从站与 CSV 导入
- [[decisions/ADR-027-MotionControllerDeltaReplacement]] · [[decisions/ADR-029-CylinderConfigAndCsvImport]] · [[decisions/ADR-030-WeldHeadSlaveDeviceUnderMotionControl]]
- [[decisions/ADR-033-ConfigArchitectureStandard]] · [[decisions/ADR-076-SettingsZoneSaveWiring]]
- [[architecture/CodeMap]] —— 代码落点
