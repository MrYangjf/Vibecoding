---
title: ADR-066 三层架构收敛（配置层归位 / 轴定位单例化 / Manager 纪律）
date: 2026-10-14
updated: 2026-10-14
tags: [ADR, 架构收敛, 配置层, 运动控制, 单例, WeldParamControl, MontionManager]
status: accepted
---

# ADR-066：三层架构收敛（配置层归位 / 轴定位单例化 / Manager 纪律）

> 业主指出「配置这一块东一块西一块，缺整体思路」，并给出三层整体思路：
> ① `WeldParamControl` 三块职责 ② `WeldParamManager` 统一加载、配置访问唯一入口 ③ 四个运动轴的定位与控制统一路由到 `MontionManager` 单例。
> 本 ADR 落地这三层。

## 背景：收敛前的三处碎裂

### ① 配置层：四块平级，职责边界不清

| 文件 | 实际内容 | 问题 |
|---|---|---|
| `WeldAlgorithmsConfig.cs` | **65 个属性**，其中约 36 个是运动/位置参数（`SpotCalibPosMm`/`WireLockPosMm`/`LaSpot1Mm`/`TeachLockYMm`…） | 算法阈值与轴位置参数混在一起 |
| `Curves/TaLaCurveConfig.cs` / `Curves/WeaveWidthTable.cs` | TA/LA 曲线、摆动幅值表 | — |
| `TAConfig.cs`（ADR-064 新建） | `ForceN`/`Pose1Mm`/`Pose2Mm` | ⛔ 与前两者**平级分家**，成了第四块 |
| `WeldParamData.cs` / `Abstractions/WeldAlgorithmBase.cs` | 工艺数据结构 / 算法基类 | 与配置类边界不清 |

### ② 运动层：轴定位逻辑散落 7 个文件

| 文件 | 越界写法 |
|---|---|
| `ProcessControlPage.cs` | **3 个关键字数组**（`YAxisKeys`/`SpotAxisKeys`/`WireAxisKeys`）+ `FindAxisName` + `MoveAxisToTarget` |
| `SystemControlPage.cs` | 3 处 `Axes.Get(...)` |
| `MotionControlWorkflow.cs` | 5 处 `GetAxis(SeamTrackAxisName)` |
| `LaserWeldHeadWorkflow.cs` | `TaAxis`/`TaAxisConfig` 各遍历一次 `MotionConfig` |
| `DeviceStatusWork.cs` | `MotionConfig.GetAxis` + `GetAxis` 连查两遍 |
| `WeldParamManager.cs` | ⛔ **配置管理器去碰运动轴** |

**根因**：`MontionManager` 只有 `GetAxis(精确名)`/`GetDeltaAxis(精确名)`，**没有「按角色关键字定位轴」的能力** ⇒ 各模块自造轮子，且关键字表不一致。

### ③ Manager 层：✅ 本已干净

全库 8 个 Manager 全部 `Lazy<T>` 单例，无一处外造。

## 决策

### 一、轴定位收敛到 `MontionManager`（角色定位唯一入口）

```csharp
// 角色关键字表：内置为唯一权威，模块只引用，不再自建
public static readonly string[] SeamTrackYKeys = { "Y", "横梁", "跟踪" };
public static readonly string[] FocusSpotKeys = { "对焦", "焦点", "光斑", "FOCUS", "SPOT" };
public static readonly string[] WireAxisKeys = { "送丝", "WIRE", "FEED" };
public static readonly string[] TaAxisKeys = { "TA", "力矩", "TORQUE" };

// 三个公开入口 + 一个私有实现
public MontionAxis GetAxisByKeys(params string[] keys);
public DeltaMontionAxis GetDeltaAxisByKeys(params string[] keys);
public DeltaAxisConfig GetAxisConfigByKeys(params string[] keys); // 只读配置，不下发运动
private string FindAxisNameByKeys(string[] keys);
```

- ⛔ `FindAxisNameByKeys` 为 **private**：不外露，避免又出现第二个「按关键字找轴」的入口
- ✅ `GetAxisConfigByKeys` 专供「需要读轴专属配置但不下发运动」的场景（如读力矩参数）

### 二、`TAConfig` 合入 `WeldAlgorithmsConfig`（业主裁定）

`ForceN`/`Pose1Mm`/`Pose2Mm` → `TaForceN`/`TaPose1Mm`/`TaPose2Mm`，与 `LaSpot1Mm`/`LaPose1Mm` 同构：

- INI 键并入 `ProcessControlSection` 段：`TA_FORCE_N`/`TA_POSE1_MM`/`TA_POSE2_MM`
- ⛔ **删除 `TAConfig.cs` + csproj 项**，不再平级分家
- ⛔ `WeldParamManager` 删 `_taIniFile`/`_taConfig`/`LoadTAConfig`/`SaveTAConfig`（独立 INI 文件随之消失）
- ✅ 一次性迁移逻辑并入 `LoadAlgorithmsConfig()` 尾部，不再独立成 API

### 三、UI 层不再自建轴定位

`ProcessControlPage.MoveAxisToTarget` 瘦身为：

```csharp
MontionAxis axis = manager.GetAxisByKeys(keys); // 唯一入口
if (axis == null) { /* 明确提示，不静默兜底 */ return; }
if (!axis.IsServoOn()) axis.ServoOn();
bool ok = axis.AbsMove(targetMm, 1);
```

⛔ 删除：3 个关键字数组、`FindAxisName`、`MotionConfig` 空值检查、`Axes.Get` 调用。

## 未收敛项（有意保留，记录在案）

| 项 | 保留理由 |
|---|---|
| `LaserWeldHeadWorkflow.TaAxis`/`TaAxisConfig` | 用**配置里的精确名 `TaAxisName`**，比关键字匹配更可靠；改为关键字会**降低精度** |
| `DeviceStatusWork.ScanTaPositionLimit` | 同样用精确名，且 `axisName` 取一次复用，无冗余 |
| `MotionControlWorkflow` 的 5 处 `GetAxis(SeamTrackAxisName)` | 精确名调用，已是规范写法 |
| `WeldAlgorithmsConfig` 的 36 个运动参数 | ⛔ **本轮未拆分**（见下） |

## 后果

- **正面**：轴定位唯一入口、关键字表唯一权威、配置层从四块收敛为「一个配置类 + 曲线表 + 数据结构 + 变更日志」、`WeldParamManager` 不再碰运动轴
- **负面**：`WeldAlgorithmsConfig` 仍有 65 个属性（本轮只做了 TA 三项归位，未做算法/运动/开关的大拆分）
- **中性**：迁移后 `TAConfig.ini` 文件不再使用，旧文件残留在磁盘上（无害，新配置走 `WeldParamControlAlgorithm.ini` 的 `TA_*` 键）

## 验证

- **静态校验 71/71 PASS**（含 csproj 收录完整性、UI 层零自建轴定位、配置三属性的声明/初值/读/写四点闭环、Manager 单例纪律）
- **回归**：6 改 1 删（`MontionManager`/`WeldAlgorithmsConfig`/`WeldParamManager`/`ProcessControlPage`/`LaserWeldHeadWorkflow`/`csproj` + 删 `TAConfig.cs`），零越界

## 遗留（下一轮建议）

⛔ **`WeldAlgorithmsConfig` 65 属性按三类拆分**（算法阈值 / 运动位置 / 功能开关）：
```
WeldAlgorithmsConfig → 焊缝跟踪+自适应焊接算法阈值（OutlierLimitMm/MonotonicWindowMm/…）
MotionParamConfig → 轴位置参数（SpotCalibPosMm/WireLockPosMm/LaSpot1Mm/TaPose1Mm/…）
ProcessSwitchConfig → 功能开关（EnableSeamTrace/EnableWireAlign/EnableGalvoWeave/…）
```
⚠️ 需业主确认拆分粒度后再动（涉及 INI 键迁移与大量消费点）。

## 背景

（待补：本决策要解决什么问题）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- ⚠️ **2026-10-19 演进**：轴「控制」唯一入口补齐 → [[decisions/ADR-073-AxisControlUnifiedMontionManager]]
 （082 定位 `GetAxisByKeys` · 089 控制 `MoveTo/StepMove/ToggleServo/JogStart/StopAxis/HomeAxis`，成对约束：查找与控制均收敛 MontionManager，UI 禁自建匹配与直控）

- [[decisions/ADR-064-TaConfigLayeredConsolidation]] —— 本 ADR 推翻其「TAConfig 独立」的结论，改为合入工艺配置
- [[decisions/ADR-063-CommandZoneRadioExclusivity]] —— TA 参数区的消费方
- [[decisions/ADR-060-P4UiLanding]] · [[decisions/ADR-062-InpageZoneGridPanelLayout]] · [[decisions/ADR-065-EnableManagementConsolidation]]
- [[architecture/CodeMap]] · [[api/ProcessControlPage]] · [[api/LaserWeldHeadWorkflow]]