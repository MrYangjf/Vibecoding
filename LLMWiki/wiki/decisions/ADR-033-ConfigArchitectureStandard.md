---
title: "ADR-033 配置架构现行决策（类别文件夹 + XML/INI 分轨；整合原 005/059）（整合旧 040（配置路径范式复正））"
date: 2026-09-16
updated: 2026-11-17
tags: [决策, 配置, 文件结构, XML, INI, 规范, 配置架构, merged, ADR-033]
status: accepted
merged_from: [ADR-005, ADR-059, ADR-040]
---

# ADR-033 配置架构现行决策（类别文件夹 + XML/INI 分轨）

> 本页为整合页（2026-09-17），就地吸收并取代原 ADR-005 / ADR-033 两页，收拢配置架构全部现行裁定。沿革见文末。

## 背景

`Config/` 位于运行时目录（`AppDomain.CurrentDomain.BaseDirectory + "Config\"`），存放全部 INI 配置、XML 通讯结构、GSDML 设备描述文件。ADR-005（2026-07-03）先按**文件类型**平铺分层（`Config/INI/`、`Config/XML/`、`Config/GSDML/`）；文件一多仍难定位「属于哪个模块/设备族、承载哪类配置」，且**设备几何/标定与流程阈值混放、XML 与 INI 的适用边界从未显式裁定**。Comm 已率先在 ADR-026 落地 `Config\Comm\<通道>_XML\` 的「类别 + 类型 + 格式」嵌套先例。ADR-033（2026-09-16）将其上升为全项目统一标准，并裁定 XML/INI 分轨。

## 现行决策

### 1. 路径范式：`Config/<类别>/<类型>_<格式>/<文件>.<扩展名>`

| 段 | 含义 | 示例 |
|---|---|---|
| 类别 category | 模块 / 设备族 | `WeldParamControl`、`Comm` |
| 类型 type | 该类别下的配置主题 | `Algorithm`、`<通道>` |
| 格式 format | `XML` 或 `INI` | `XML`、`INI` |

完整示例：

- `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`
- `Config/WeldParamControl/Algorithm_INI/WeldParamControlAlgorithm.ini`
- `Config/Comm/<通道>_XML/`（目录细则见 [[decisions/ADR-026-RsiSemanticRewriteAndDualChannel]] 整合页）

### 2. XML / INI 分轨规则（核心裁决）

| 格式 | 适用 | 理由 |
|---|---|---|
| **XML** | **设备 / 子设备的默认参数配置**——轴参数配置、通讯文档配置、相机标定、设备几何 / 安装常量、容量等 | 结构嵌套、可带单位与注释、与厂商 SDK / 设备描述文件（GSDML）同源，便于表达复杂对象 |
| **INI** | **流程类的上下限阈值 / 开关 / 节拍 / 模拟测试**——流程循环节拍、是否启用、超限阈值、模拟测试标志等 | 扁平键值、易手编、天然无单位歧义（纯数值 / 布尔），便于运维现场微调 |

### 3. 兼容性

- ADR-005 的 `Config/INI/`、`Config/XML/`、`Config/GSDML/` 平铺布局原本只保留给历史存量文件；**2026-09-21 起废止**——`Config\XML\`、`Config\INI\` 已由 `FileOperate/ConfigPathMigrator.cs` 一次性搬迁到三段式路径后整体删除（磁盘实测目录已消失），新配置一律走三段式范式。
- **新配置一律走新范式**；INI / XML / GSDML 三类格式的类型区分本身仍有效。
- 既有先例：`Config/Jobs/`（业务数据，原 `EmguALG/JobManager.cs` 时代）——2026-09-21 起按三段式归 `Config/Jobs/Job_INI/`。
- **控制器配置迁移落地（2026-09-20 → 2026-09-21 收口）**：运控两份 XML 从旧平铺 `Config\XML\` 迁入三段式范式——`Config/MotionControl/Motion_XML/DeltaMotionConfig.xml`（轴/IO/气缸/主站设备参数，XML 轨）+ `Config/MotionControl/WeldHead_XML/WeldHeadSlave.xml`（焊接头阈值/振镜）。迁移先由 `MontionManager.MigrateLegacyControllerXml()` 承担，2026-09-21 起**统一收口**为 `FileOperate/ConfigPathMigrator.cs`（`Program.Main` 首步调用，覆盖全部历史与过渡布局），范式同 `CommunicationManager` 的 Comm 迁移先例。
> ⚠️ **2026-09-21 复正（ADR-033）**：2026-09-20 本节的迁移目标一度被写成 `Config/XML/MotionControl/...`——ADR-033 初版把一级目录定为**格式**，与本节「类别 = 模块/设备族、格式作目录名后缀」相反。同日已回正为 `Config/MotionControl/...`，并同步取消兼容回退读（旧路径一次性搬迁后废弃）。见 [[decisions/ADR-033-ConfigArchitectureStandard]]。

### 4. 配置类划分判据：跟随「谁写盘」

配置类划分跟随「**谁写盘**」而非「字段分几组」——同一写盘方（同一 Manager / 同一后端）承载的配置字段归入同一配置类，不按字段主题强行拆分（判据固化于 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] / ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]））。

### 5. 首个落地实例：`WeldAlgorithmsConfig` 双后端拆分

`WeldParamControl` 模块焊接算法配置按 XML/INI 分轨边界**拆双后端**，由 `WeldParamManager` 单例独占持有两套读写器（`XdocumentReaderWriter` + `INIFile`），`LoadAlgorithmsConfig()` / `SaveAlgorithmsConfig()` 分别读写：

| 后端 | 路径 | 承载 |
|---|---|---|
| **XML** | `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml` | 设备几何 / 安装常量 / 模式 / 容量 / **线激光标定**（`SEAM_GUIDE` 几何段 + `LASER_CALIBRATION` 段） |
| **INI** | `Config/WeldParamControl/Algorithm_INI/WeldParamControlAlgorithm.ini` | 流程阈值（`SEAM_GUIDE` 阈值段：`NoValueToleranceMm` / `OutlierLimitMm` / `Monotonic*` / `BatchSize` / `MinRemainBuffer` / `DefaultFrameSeconds` / `MaxOutputIntervalMs` / `MaxPendingPoints` / `OutlierSigmaK` / `ReverseAlarmMm` 等）+ 调整参数（`WELD_PARAM_ADJUST`：`MaxConsecutiveFailures` / `CountNum`） |

- 外部**只读** `WeldParamManager.Instance.AlgorithmsConfig`；⛔ 不得 `new`、不得持有或回灌实例。
- **ADR-027 例外登记**：线激光标定参数（原属运控 `DeltaMotionConfig` 的设备几何）字面并入 `WeldParamControl` 的 `WeldAlgorithmsConfig`（归 XML 的 `LASER_CALIBRATION` 段），打破了 ADR-027「数据产出归属设备模块」的边界（2026-09-14 已裁定登记；标定参数需随焊接算法配置一并 UI 配置与落盘，归口 `WeldParamControl`）。**后续新建设备几何数据仍优先留在所属设备模块**，仅确有跨模块配置聚合需求时经评审开放例外。

## 备选方案（已弃）

| 方案 | 放弃原因 |
|---|---|
| 维持 ADR-005 纯类型平铺（`Config/XML/`、`Config/INI/`） | 文件多后难辨归属；未裁定 XML/INI 适用边界 |
| 按模块单文件夹（`Config/WeldParamControl/`）不分子类型 | XML 与 INI 混放，无格式边界；与 Comm 已落地的 `<通道>_XML/` 不一致 |
| 当前方案（类别 / 类型 / 格式三层嵌套 + XML·INI 分轨） | ✅ 采纳：归属清晰、与 Comm 既定范式一致、格式边界显式 |

## 后果

### 正面

- 配置归属一目了然（类别 → 类型 → 格式）
- XML/INI 适用边界显式裁定，设备几何与流程阈值不再混放
- 与 Comm 既定范式统一，新增配置有章可循

### 负面

- 新配置文件需遵循三段式路径命名，命名约定略增
- 历史存量文件仍处平铺布局，存在两套并存（存量不强制迁移）

## 沿革

- 2026-07-03 ADR-005 初版：`Config/` 按文件类型平铺分层（`INI/` / `XML/` / `GSDML/`），解决根目录全部平铺的查找混乱。
- 2026-09-16 ADR-033：升级为「类别 / 类型 / 格式」三段式嵌套 + XML/INI 分轨标准；平铺布局仅保留给存量。本页（2026-09-17）整合两者，005 就此并入。
- 2026-09-21 复正：三段式范式落实为**全项目唯一路径范式**——`Config\XML\`、`Config\INI\` 存量一次性搬迁后目录整体删除（`FileOperate/ConfigPathMigrator.cs`），不再保留平铺兼容；同日 ADR-033 决 1 从「按格式分层」回正为本节原式。

## 关联

- [[decisions/ADR-016-WorkflowResponsibilityBoundary]] — 设备数据边界（本页登记标定并入例外）
- ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 焊接算法配置合一（本页在其之上拆分双后端）
- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] — 「谁写盘」判据来源之一
- [[decisions/ADR-026-RsiSemanticRewriteAndDualChannel]] — 通讯配置目录范式（类别/类型/格式先例，整合页）
- [[modules/WeldParamControl]] / [[api/WeldParamManager]] — 模块说明与 Manager 唯一入口（双后端读写）
- [[modules/FileOperate]] — INIFile / XdocumentReaderWriter 工具库

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 合并自 ADR-040 · 配置路径范式复正（回到 ADR-033 原式：Config/<功能类别>/<主题>_<格式>/；SeamTrackAxisName 归运控；禁跨模块读配置）

> 2026-11-17 治理轮合并：原页为独立 ADR-033，其现行裁定收归本页；原页文件已删除（**编号不回收**，废止号不复用）。原页的验证过程叙事已按格式契约 R2 剥离至 `logs/log.md`。

**原页决策一句话**：`bin/Debug/Config/XML/` 实际为平铺，未按要求按功能建立多级目录；`SeamTrackAxisName` 错误放在 `LineLaserConfig.xml`（属线激光模块）却被运控 `MotionControlWorkflow` 跨模块读取。

### 原页决策条目

1. （待补）

### 原页背景

（待补：本决策要解决什么问题）

### 原页后果

### 正面
- （待补）

### 负面
- （待补）


## 相关页面

- [[decisions/ADR-Index]]
