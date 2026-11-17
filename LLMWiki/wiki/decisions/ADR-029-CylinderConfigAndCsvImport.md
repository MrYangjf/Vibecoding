---
title: "ADR-029：气缸配置持久化与 CSV 导入通道"
date: 2026-09-16
updated: 2026-10-30
tags: [ADR, 运控, MotionControl, 配置, CSV, 气缸, DeltaMotionConfig]
status: accepted
---

# ADR-029：气缸配置持久化与 CSV 导入通道

## 状态

已采纳（2026-09-16，用户裁定：电气以固定格式 CSV 表格填写轴 / IO / 气缸配置，程序导入后自动写入本地配置，控制器加载生效）。

## 背景

ADR-021/033 台达 EtherCAT 落地后，轴与 IO 已有配置持久化：`DeltaMotionConfig` 读写 `Config/XML/DeltaMotionConfig.xml`（现 `Config/MotionControl/Motion_XML/DeltaMotionConfig.xml`）的 `AXES` / `INPUTS` / `OUTPUTS` 节，`MontionManager.Initialization` 按配置建 `DeltaMontionAxis` / `DeltaInputIO` / `DeltaOutputIO`。

缺口有二：

1. **气缸无配置化**：`IMotion/Cylinder.cs`（Builder 链式装配）只能代码手工装配，无 XML 节、无按配置装配路径；
2. **无批量导入通道**：轴 / IO / 气缸参数目前只能逐项手填，电气（现场）→ 程序（软件）之间缺一份可离线编辑、可机器解析的交接载体。

## 裁决

1. **CSV 为电气交接格式**：三张固定格式表——`轴配置表.csv` / `IO配置表.csv` / `气缸配置表.csv`，UTF-8 带 BOM（Excel 双击直开直填），列与 `DeltaAxisConfig` / `DeltaIOConfig` / `DeltaCylinderConfig` 字段一一对应；三表通过**名称**互相引用（气缸表按 IO_NAME 绑定传感器与电磁阀）。模板与填写说明沉淀于工作区 `轴IO气缸配置模板/`。
2. **气缸配置入 XML**：`DeltaMotionConfig` 新增 `DeltaCylinderConfig`（纯名称引用，8 字段全 string，空串=未配置）与 `ROOT/CYLINDERS/` 节，Load/Save 与既有节同管道（`XdocumentReaderWriter`，ADR-007 范式），**不另起配置文件**。
3. **导入 = 全量替换**：新增 `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs`（静态工具类）——解析三表 → 统一校验（表头、名称唯一、气缸引用的 IO 名存在、数值可解析）→ **全部通过后**整体替换 `Axes/Inputs/Outputs/Cylinders` 四表 → `SaveConfig()` 落盘；任一校验失败则**零写入**，全部错误一次性回传 `msg`。
4. **装配按名解析**：`MontionManager.Initialization` 在 `CreateIOsFromConfig` 之后新增 `CreateCylindersFromConfig`——按名在 IO 注册表解析后 Builder 链式装配气缸并登记 `CylinderRegistry`；引用缺失的气缸**告警跳过不阻塞**（轴 / IO 初始化优先），由 `AttachAll` 统一把气缸占用 IO 注册进控制器。
5. **导出与 UI 同期补齐（2026-09-16 同日续轮）**：

 - **导出通道**：`MotionConfigImporter.Export(dir, ref msg)` 按与 Import 侧**逐字一致的表头**反写 CSV（`轴配置表.csv` / `IO配置表.csv` 含输入段+输出段 / `气缸配置表.csv`，共 4 段），UTF-8 带 BOM，**导出产物可原样回导入**（双向闭环，便于电气在真机状态下导出基线再改）。写出侧新增私有 `CsvField`（含逗号/引号/换行时双引号包裹并转义）、`CsvBool`（TRUE/FALSE）、`CsvDouble`（固定 `InvariantCulture`）、`WriteCsv`（`File.WriteAllLines` + `new UTF8Encoding(true)`）。
 - **UI 窗体落地（2026-09-17 演进 → 迁入 `MotionControlPage.panel1`）**：原 `UIDesign/SubDialog/MotionControlDialog/MontionConfigForm`（`UserControl`，ADR-027 Modal 承载，类名按用户原样保留 `Montion` 拼写）承载 CSV 导入 / 导出按钮 + **IO 信号操作表** + **轴控配置表** + **气缸操作表** 四区合一；布局按用户硬约束：**区域控制一律 `TableLayoutPanel`（明确不用 `AntdUI.FlowPanel`）**，区域外壳 `AntdUI.Panel`，按钮 `AntdUI.Button`（`Ghost = true` + `BackHover = RGB(3,169,244)`）。三表以 `AntdUI.AntList<T>` 强类型绑定、双击进入编辑，`CellEndEdit` 校验通过后就地回写 `DeltaAxisConfig` / `DeltaIOConfig` / `DeltaCylinderConfig`，「保存表格修改到 XML」落盘 —— 即**配置编辑不再必须经过 CSV**，CSV 降为批量交换与基线交接通道。见 [[api/SystemControlPage]]（原 `MontionConfigForm` 已废弃）。
 - **入口演进（2026-09-17）**：`MotionControlPage` 现已承载运控 4 表——原 `MontionConfigForm` 内容整体迁入其 `panel1`，入口从独立弹窗改为页面内嵌，见 [[api/SystemControlPage]]。

## 影响

- 新增文件：`MotionControl/DeltaEtherCAT/MotionConfigImporter.cs`（已注册 csproj）。
- **同日续轮新增文件（2026-09-17 已随 `MontionConfigForm` 整体删除，见 [[api/SystemControlPage]]）**：`UIDesign/SubDialog/MotionControlDialog/MontionConfigForm.cs` + `.Designer.cs` + `.resx`（三件套已注册 csproj，`.cs` 带 `<SubType>UserControl</SubType>`，`.Designer.cs` 与 `.resx` 带 `<DependentUpon>`；原空目录 `<Folder Include>` 声明随之移除）。
- **同日续轮修改**：`MotionConfigImporter.cs` 补 `Export` + 4 个 CSV 写出私有方法。
- 修改：`DeltaMotionConfig.cs`（+`DeltaCylinderConfig`、CYLINDERS 节、`GetCylinder`）、`MontionManager.cs`（+`CreateCylindersFromConfig`）。
- 存量 XML 兼容：旧 `DeltaMotionConfig.xml` 无 CYLINDERS 节时 `GetChildElements` 返回空集，气缸表为空、行为与旧版一致，**零迁移**。
- 导入时机约束：`Initialization` 之前导入才对本轮启动生效（`MoveData.Load` 只在构造与 `Initialization` 开头执行）；运行期导入只改内存表 + 落盘，下次启动生效。

## 关联

- [[modules/MotionControl]]、[[api/MontionManager]]、[[api/MoveControlData]]、[[api/SystemControlPage]]（同日续轮 UI 落地，原 `MontionConfigForm` 已于 2026-09-17 废弃）
- 持久化规范：[[guides/Config-Data-Tools]]（LoadConfig/SaveConfig 与 XdocumentReaderWriter 范式）
- [[decisions/ADR-027-MotionControllerDeltaReplacement]]、ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）

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

- [[decisions/ADR-Index]]
