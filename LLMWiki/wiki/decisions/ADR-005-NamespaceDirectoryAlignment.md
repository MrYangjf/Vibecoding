---
title: ADR-005 命名空间与目录严格对齐（namespace = AdaWeldSystem + 目录路径）
date: 2026-09-14
updated: 2026-10-30
tags: [决策, 命名空间, 目录对齐, 重构, 代码规范, ADR-005]
status: accepted
---

# ADR-005 命名空间与目录严格对齐

## 状态

已采纳（2026-09-14）。

## 背景

项目历经多轮目录重命名（`UIDesign/ParentUI/`→`MainWindow/`、`Sub1UI/`→`ControlPage/`、`Sub2UI/`→`TabPage/`、`SubView/`→`SubDialog/`，以及 `Comm/`、`MainDeviceControl/`、`SQLiteDBControl/` 多次整改）与模块重构（ADR-011 / ADR-031 / ADR-031），出现两类历史包袱：

1. **命名空间滞后于目录**：为规避「改命名空间 → 全项目 `using` 连锁改动」，历次重构多次**刻意保留旧命名空间**（ADR-027 §3、ADR-023、ADR-033 §7、ADR-011 §4 均有「命名空间不动」的明文条款）。累积后同一物理目录下的文件分属互不相干的命名空间（如 `DeviceStateApiCore/` 内并存 `...DeviceState` 与 `...FlowState`）。
2. **目录名与命名空间不同形**：`SQLiteDBControl/` 目录配 `AdaWeldSystem.SQLiteDatabase` 命名空间；`PCLOperate/3DModel/` 等目录与命名空间无派生关系。

用户 2026-09-14 指令：「检测项目代码文件层级对齐知识库……很多代码的命名空间和文件名、类名因为反复修改存在混乱层级和重复的问题，请按照各个文件夹层级、命名空间、类名、函数名层级和引用进行修复。」

### 用户裁定（三选三定）

| 议题 | 裁定 |
|---|---|
| 对齐强度 | **严格对齐**——命名空间 = `AdaWeldSystem` + 目录路径，全部错位一次改齐 |
| 冲突时谁让位 | **命名空间跟随目录**（不以命名空间为准改目录） |
| 第三方代码 | **所有第三方原厂 SDK 和参照都不要修改** |

## 决策

### 1. 判据（唯一规则）

```
namespace == "AdaWeldSystem" + 相对 AdaWeldSystem/ 的目录路径（点分隔）
```

- `AdaWeldSystem/Program.cs` → `AdaWeldSystem`（代码根，无目录段）
- 目录段一律用点连接；目录名**原样保留**（含既有拼写，如 `ParamContolDialog`，不在本 ADR 内顺手改名）

### 2. 例外一：厂商 SDK / 参照原样不动

`MonitorCam/MecaVisionCam/Native/MVSDK.cs` 等第三方原厂 SDK 文件**不参与对齐**，命名空间与文件内容保持原状（本轮 md5 未变）。此类文件在厂商 SDK 目录内自洽，改动会破坏与厂商后续版本的对照关系。

### 3. 例外二：扁平裁定目录不产生子命名空间

`ProductFileControl/` 为 ADR-031/047 确立的**扁平结构**：`Abstractions/` 与 `Records/` 两个子目录**不产生子命名空间**，全部归 `AdaWeldSystem.ProductFileControl`。

> 理由：这两个子目录是「记录基类 / 记录实现类」的**分类桶**，不是独立功能族；拆出子命名空间会使 Manager 与记录类之间凭空多出 `using`，且与 ADR-006「实现层必须继承抽象层」的同族语义相悖。

### 4. 本轮落地映射（代码侧 68 文件）

| 目录（`AdaWeldSystem/` 下） | 旧命名空间 | 新命名空间 |
|---|---|---|
| `UIDesign/MainWindow/` | `Sub3UI` 系 | `AdaWeldSystem.UIDesign.MainWindow` |
| `UIDesign/ControlPage/` | `Sub1UI` | `AdaWeldSystem.UIDesign.ControlPage` |
| `UIDesign/TabPage/` | `Sub2UI` | `AdaWeldSystem.UIDesign.TabPage` |
| `UIDesign/SubDialog/<业务域>/` | `Sub1UI` / `Sub2UI` / `Sub3UI` | `AdaWeldSystem.UIDesign.SubDialog.<业务域>` |
| `MainDeviceControl/`（根两管控类） | `...MainDeviceControl.DeviceWorkflow` | `AdaWeldSystem.MainDeviceControl` |
| `MainDeviceControl/DeviceStateApiCore/` | `...DeviceState` / `...FlowState` | `AdaWeldSystem.MainDeviceControl.DeviceStateApiCore` |
| `Comm/SystemComm/` | `AdaWeldSystem.Comm` | `AdaWeldSystem.Comm.SystemComm` |
| `Comm/Communication/Abstractions/` | `AdaWeldSystem.Comm.Communication` | `AdaWeldSystem.Comm.Communication.Abstractions` |
| `Comm/Communication/Implementations/` | `AdaWeldSystem.Comm.Communication` | `AdaWeldSystem.Comm.Communication.Implementations` |
| `SQLiteDBControl/` 及三子目录 | `AdaWeldSystem.SQLiteDatabase` | `AdaWeldSystem.SQLiteDBControl[.SQLiteCore\|.ISQLiteHelper\|.Helpers]` |
| `PCLOperate/Models/` | （同上，仅目录改名） | `AdaWeldSystem.PCLOperate.Models` |

同批处理**失效 `using`**：删除 57 文件 83 条旧命名空间引用，补入 70 文件 133 条新引用；`DeviceState` 枚举曾与父作用域子命名空间同名的 **CS0118 遮蔽问题随之消解**，全库 `using DeviceState = ...` 别名已清除（旧写法见 [[guides/Namespace-Compilation]] §2 补充案例，现已标记沿革）。

### 5. 对被废止条款的处置

本 ADR 生效后，以下历次决策中的「命名空间保持不变」条款**一律废止**（各页已加沿革横幅）：

| 来源 | 被废止条款 |
|---|---|
| [[decisions/ADR-009-DialogWindowToModalUserControl]] §3 | 对话窗命名空间仍 `AdaWeldSystem.Sub3UI` / `AdaWeldSystem.Sub2UI` |
| [[decisions/ADR-013-ThreeStateModelRefactor]] | 表内 `...MainDeviceControl.DeviceState`、§3 `...MainDeviceControl.FlowState` |
| [[decisions/ADR-022-EmguALGThreeLayer]] | `Core/AlgorithmOperations.cs` 写作 `AdaWeldSystem.EmguALG` 命名空间 |
| ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） §7 | 「`ProductFileControl/` 目录名与 `AdaWeldSystem.ProductFileManager` 命名空间暂不一致」（已由 ADR-031 + 本 ADR 闭环） |
| [[decisions/ADR-025-CommModuleRefactor]] §4 | `SystemComm.cs`「命名空间仍 `AdaWeldSystem.Comm`」 |

其余 ADR 页中「当时文件位于 `Sub2UI/` 等」一类**历史叙述**不改写——ADR 是决策时点的记录，检索时的换算以 [[decisions/ADR-Index]] 与本 ADR 为准。

### 6. 例外登记（供后续对齐审查沿用）

| 例外对象 | 内容 | 依据 |
|---|---|---|
| `MonitorCam/MecaVisionCam/Native/MVSDK.cs` | 厂商 SDK，命名空间与内容原样 | 本 ADR §2 + 用户裁定 |
| `ProductFileControl/Abstractions`、`ProductFileControl/Records` | 子目录不产生子命名空间（扁平） | 本 ADR §3 + ADR-031/047 |
| `Properties/AssemblyInfo.cs` | 无 `namespace` 声明（程序集特性文件） | .NET 惯例 |

## 校验与验收

- **无 C# 编译器**：以 Python 静态校验替代，全仓 143 个 `.cs`（不含 `.Designer.cs` 与厂商目录）逐文件比对 `namespace` 与目录路径 → **真实不一致 0**，仅 4 例为 §3 扁平裁定、1 例为 §6 无命名空间文件。
- 不可见引用 0、真实类型歧义 0、重复 `using` 0、括号平衡、旧命名空间残留 0。
- `.csproj` 双向核验：注册路径缺失 0、磁盘文件未注册 0（168 = 168）。
- 行尾/编码：CRLF 存量保持，未新增裸 LF、CRCRLF 0；新建 ADR 页 LF noBOM。
- ⚠️ **真编译待 Visual Studio**（沙盒无 C# 编译器）。

## 后果

### 正面

- 「看目录即知命名空间」，检索与新增文件不再需要查表；`using` 推导单一化。
- 消解 `DeviceState` 枚举同名遮蔽（CS0118）一类历史陷阱，命名空间内 `using` 别名写法可彻底弃用。
- 后续目录重命名只要同步命名空间 + `.csproj`，不再累积「目录 ≠ 命名空间」的欠账。

### 负面 / 成本

- 一次性大范围改动（68 文件命名空间 + 140 处 `using` 增删），**必须整批同步**，中途半成品状态无法编译。
- 与「避免连锁改动」的历史取向相反；本 ADR 以「一次性付清」取代「每次重构都欠一点」。
- 非本 ADR 范围内的遗留（**2026-10-26 复核**）：`UIDesign/SubDialog/MotionControlDialog/` **已非空占位**（现有 `AxisConfigForm` / `IoConfigForm` / `CylinderConfigForm` 3 文件 477 行）；`EmguALG` 与 `LineLaserCam` 的 `LineLaserConfig` 跨命名空间重名**仍然存在**（潜伏 CS0104）——唯一双 `using` 文件 `ILCamPage.cs`（同时 `using AdaWeldSystem.EmguALG.Core;` 与 `using AdaWeldSystem.LineLaserCam;`）**未引用该类型**，故当前不触发；EmguALG 侧该类仅被自身 `PreprocessConfig.LineLaser` 字段引用（0 外部消费者），处置建议为改名 `LineLaserPreprocessConfig`（改名零风险），**待业主裁决**。

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[decisions/ADR-Index]] — 编号总表（现行 001~049）
- [[decisions/ADR-006-ModuleOrganizationPatternStandard]] — 模块组织范式（命名空间是族边界的表达）
- [[decisions/ADR-025-CommModuleRefactor]]、ADR-031（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 本轮对齐的两个上游重构
- [[guides/Namespace-Compilation]] — 命名空间与编译错误指南（CS0118 案例已标记沿革）
- [[modules/UIDesign]]、[[modules/DeviceControl]]、[[modules/Comm]]、[[modules/SQLiteDatabase]]、[[modules/PointCloudData]] — 各页目录/命名空间表已同步
