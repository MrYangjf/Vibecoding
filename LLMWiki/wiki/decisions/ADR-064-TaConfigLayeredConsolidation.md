---
title: ADR-064 TA 配置分层收口
date: 2026-10-12
updated: 2026-10-14
tags: [ADR, 配置, TA, 分层, TorqueTarget, 迁移]
status: accepted
---

# ADR-064：TA 配置分层收口（工艺值 vs 驱动器参数）

> ⚠️ **2026-10-14 推翻注记（[[decisions/ADR-066-ThreeLayerConvergence|ADR-066]]）**：本页「TAConfig 独立文件」的结论已被推翻——`TAConfig.cs` 整体合入 `WeldAlgorithmsConfig`（`TaForceN`/`TaPose1Mm`/`TaPose2Mm`，独立 INI 不再使用）；「工艺值 vs 驱动器参数分层」的语义判断仍然有效。现行配置归位以 ADR-066 为准。
> TA 相关参数原本**散在两个体系**，本 ADR 按物理语义分层：工艺调试值入 `TAConfig`，驱动器行为参数留轴配置。

## 背景

业主：「你重新梳理这个配置，这一整套配置都存入一个体系里，TAConfig。我已经不知道 TorqueTarget 是什么了」。

梳理结果（Phase 0 检索实证）：

| 参数 | 原载体 | 存储 | UI 归属 | 物理语义 |
|---|---|---|---|---|
| `TorqueTarget` | `DeltaAxisConfig` | 轴配置 XML + **CSV 导入** | 待定 | **下压力**（工艺值） |
| `TorqueSlope` | `DeltaAxisConfig` | 轴配置 XML + **CSV 导入** | 系统设置（2026-11-05 起改为 TA 轴「参数」弹窗，ADR-084） | 扭矩爬升速率（**驱动器参数**） |
| `TorqueModeEnabled` | `DeltaAxisConfig` | 轴配置 XML + **CSV 导入** | 系统设置 | 力矩模式开关（**驱动器参数**） |
| `TaPose1Mm` | `WeldAlgorithmsConfig` | 工艺 INI | 工艺设置 | Pose1 位（工艺值） |
| `TaPose2Mm` | `WeldAlgorithmsConfig` | 工艺 INI | 工艺设置 | Pose2 位（工艺值） |

**核心问题**：下压力（工艺调试值）寄居在**轴配置**（电机/软限位/回零参数）里 —— 这就是业主「不知道 TorqueTarget 是什么」的根源。
业主裁定：**扭矩爬升速率（原称「斜坡」）与力矩模式开关属系统设置，不属于工艺设置**（2026-11-05「扭矩爬升速率」迁至 TA 轴「参数」弹窗，ADR-084；力矩模式开关已删，ADR-082）。

## 决策

### 一、新建 `TAConfig`（只收工艺调试值）

```csharp
// AdaWeldSystem/WeldParamControl/TAConfig.cs
public class TAConfig {
 public double ForceN { get; set; } // 下压力 N（承接 TorqueTarget）
 public double Pose1Mm { get; set; } // Pose1 调试位
 public double Pose2Mm { get; set; } // Pose2 调试位
}
```

- 存储：**INI**（`Config\WeldParamControl\TA_INI\TAConfig.ini`，段 `TA_DEBUG`），与工艺配置同体例
- 读写：复用 `INIFile.ReadDouble` / `WriteDouble` / `SaveToFile`（不新造读写函数）
- `ForceN` 经 `SanitizeForce` 收敛到 `[0, 500]` N，防 0/负值/超限下发到驱动器

### 二、驱动器参数永久留轴配置

`TorqueModeEnabled` / `TorqueSlope` **不迁入** `TAConfig` —— 它们是台达驱动器的行为参数，归属轴配置与系统设置页。
⇒ `DeltaMotionConfig` 的 XML 三键与 `MotionConfigImporter` 的 CSV 三列**不动**（历史轴表模板不破坏）。

### 三、`TorqueTarget` 弃用 + 一次性迁移

- `DeltaAxisConfig.TorqueTarget` **保留字段**（轴表通道 + 迁移读取用），XML 注释标注「已弃用」
- ⛔ **不用 `[Obsolete]` 特性**：`DeltaAxisConfig.cs` 无 `using System`，且**项目零 Obsolete 先例** ⇒ 避免引入陌生范式
- **一次性迁移**（`WeldParamManager.MigrateLegacyTorqueTarget`）：
 仅当 `TAConfig.ini` 未写过 `FORCE_N` 键 **且** 轴配置 `TorqueTarget != 0` 时，把旧值迁入 `ForceN` 并立即落盘

### 四、消费点改读

| 方法 | 原读 | 现读 |
|---|---|---|
| `LaserWeldHeadWorkflow.TaAuto()` | `axisCfg.TorqueTarget` | `TAConfig.ForceN`（扭矩爬升速率/模式仍读轴配置） |
| `TaPose1()` / `TaPose2()` | `WeldAlgorithmsConfig.TaPose1Mm/2Mm` | `TAConfig.Pose1Mm/2Mm` |

`WeldAlgorithmsConfig` 的 `TaPose1Mm` / `TaPose2Mm` / `IniTaPose1` / `IniTaPose2` **已删除**（迁出，零外部引用）。

## 后果

- **正面**：工艺值集中一处、命名自解释（`ForceN` 而非 `TorqueTarget`）；轴表导入模板不破坏；存量配置不丢失
- **负面**：`ForceN`（N）到 `SetTorque(short targetTorque, ...)` 需强转 `short` —— 量纲转换点显式化，上限由 `SanitizeForce` 兜底
- **中性**：`WeldParamManager` 新增 `TAConfig` / `LoadTAConfig` / `SaveTAConfig` 三个成员

## 验证

- **回归**：`DeltaAxisConfig` / `WeldAlgorithmsConfig` / `LaserWeldHeadWorkflow` / `WeldParamManager` + 新增 `TAConfig.cs`
- ⚠️ **真编译待 Visual Studio**；`ForceN` 与 `TorqueTarget` 的量纲对应关系（N ↔ 台达 short 力矩单位）**待上机核对**

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[decisions/ADR-063-CommandZoneRadioExclusivity]] —— 指令区 Radio 化（TA 参数区的消费方）
- [[api/WeldParamManager]] · [[api/LaserWeldHeadWorkflow]] · [[api/ProcessControlPage]]
- [[decisions/ADR-060-P4UiLanding]] §四
