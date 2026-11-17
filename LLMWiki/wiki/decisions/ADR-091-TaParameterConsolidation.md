---
title: ADR-091 — TA 参数收口：工作零位复用 Pose1/2、删除软限位模式与位置越限扫描
date: 2026-11-06
updated: 2026-11-06
tags: [运动控制, TA, TA_ZeroPose, 工作零位, 软限位, 参数收口]
status: accepted
---

# ADR-091 — TA 参数收口（工作零位复用 Pose1/2 · 删除软限位模式）

## 结论

1. **TA 工作零位只剩一个可编辑项**：坐标 `TA_ZERO_POSE_MM`（工艺设置页 TA 区，与 `TA_POSE1_MM`/`TA_POSE2_MM` 同节）。
   速度 / 到位容差 / 加减速**复用 `TA_Pose1/2` 同一套来源**，⛔ 不再单独立键、不再单独立 UI。
2. **删除 `ScanTaPositionLimit`**（行程越限即 `StopTorque()` 撤力 + 报警）。业主判定：锁不住位置，且在焊接关键时刻退出力矩模式，纯属有害。
3. 本轮**不改变** TA 出力实现（CST 封存，ADR-088）。

## 业主原话

> `TA轴参数按钮弹窗中TA工作零位下的三个设置删除。TA工作零位位置在工艺设置处设置，其他配置(速度和到位)使用和TA_Pose1/2一样的，不需要单独配。另外软限位模式，并不能锁住位置，且还会退出力矩模式，纯纯多余，这个设置也删掉。`

## 决策一：工作零位速度/容差来源（复用而非新建）

**`TA_Pose1/2` 的既有来源（证据）**：

| 量 | 来源 | 证据 |
|---|---|---|
| 运行速度 | 轴配置 `AXES/AXIS/MAX_VEL` → `MontionAxis.MaxVel` | `axis.AbsMove(posMm, 1)` 内部取 `MaxVel`（`IMotion/MontionAxis.cs:32-44`） |
| 到位容差 | `MontionManager.InstructionDefaultTolMm = 0.1` | `MontionManager.cs:70` |
| 加减速 / 曲线时间 | 轴配置 `ACC_TIME` / `DEC_TIME` / `S_TIME` | 同上（构造函数默认 0.1 / 0.1 / 0.01） |

`TA_ZeroPose` 改为读同一来源：
- `MontionManager.RunTaZeroPose`：`vel = taAxis.MaxVel`（≤0 时兜底 1.0 并告警）、`tol = InstructionDefaultTolMm`；
- `DeltaMontionAxis.StartZeroPoseMove`：`AbsMoveNoBlock(target, vel, vel, vel, AccTime, DecTime, STime, 1)`（删除原硬编码 0.5/0.5/0.0）；
- `MotionControlWorkflow.TaZeroPose` 日志同步为「速度（轴运行速度 MaxVel）/ 容差（InstructionDefaultTolMm）」。

⛔ **不新造「共用键」**——Pose1/2 本身没有独立速度/容差键，直接复用轴参数与通用容差。

## 决策二：删除的配置键（Grep 0 命中）

| 项 | 删除位置 |
|---|---|
| `TA_HOME_ZERO_POSE_VEL` | `DeltaMotionConfig` 读段 + `WriteConfigNodes` 写段 + `ConfigSelfHeal` 模板 |
| `TA_HOME_ZERO_POSE_TOL_MM` | 同上 |
| `DeltaTaHomeConfig.ZeroPoseVelMmPerSec` / `ZeroPoseTolMm` | 属性 + 构造函数默认值 |
| `AxisConfigForm` 三项设置（位置只读标签 / 速度 / 容差）+ 分区标题 | 控件、字段、`LoadValues`/`Validate`/`Commit`、`ReadZeroPoseTargetMm()` |

**旧配置兼容**：现场 XML 里已存在的 `TA_HOME_ZERO_POSE_VEL` / `TA_HOME_ZERO_POSE_TOL_MM` **读出即忽略、留在文件不报错**，写侧不再生成，`ConfigSelfHeal` 也不再补。⛔ 不做删键迁移（删键风险大于收益）。

## 决策三：删除软限位模式与位置越限扫描

| 项 | 说明 |
|---|---|
| `DeviceStatusWork.ScanTaPositionLimit` | 整段删除（边界比对 + `StopTorque()` + `ReportAlarm`/`ReportAlarmCleared` + 日志） |
| `DeviceStatusWork._taLimitAlarmActive` | 边沿锁存字段删除 |
| `AxisConfigForm`「软限位模式」行 | 设置行删除（`PositiveLimit` / `NegativeLimit` 两行保留） |

**范围边界（确认只影响 TA 轴）**：
- 越限扫描只对 TA 轴跑，Y 轴/其他轴从未接入该扫描 —— 删除后他轴零影响。
- `SOFT_LIMIT_MODE` 键**保留**：CSV 导入导出（`MotionConfigImporter`，轴表 19 列）与 `DeltaAxisConfig` 仍用它，删键会破坏 CSV 往返。**只删 UI 行，不删键、不改 CSV 列**。
- `POSITIVE_LIMIT` / `NEGATIVE_LIMIT` 保留（仍参与配置与 CSV），但运行期不再有越限撤力行为。

## 后果

- 力矩模式下压不再被「到边界」打断，无「TA轴到达行程边界」日志与报警源。
- 工作零位速度随 `MAX_VEL` 全局生效（改轴速度即改 ZeroPose 速度）；容差固定 0.1mm。
- 🔴 **技术债（未变）**：CST 只约束出力不约束速度，无速度上限 —— 等台达回复，见 [ADR-088](ADR-088-TaSharedTorqueLimit.md)。
- 相关页：[[modules/MotionControl]] · [[api/MontionManager]] · [[api/MotionControlWorkflow]] · [[decisions/ADR-082-TaInitFourStepAndAvailability]]（D7 三键已收口为本页口径）
