---
title: ADR-030 产品生命周期记录模块与故障记录归口（DB 下沉 + 消费方归位）
date: 2026-08-31
tags: [决策, 模块, 产品记录, 故障恢复, SQLite, 文件迁移, 归口]
status: accepted
previous_id: ADR-033
---

# ADR-030 ProductFileManager 产品生命周期记录模块 + FaultRecord DB 实现下沉

> **类名注记（2026-09-02，ADR-028）**：本文消费方清单中的 `SafetyWorkflow` **现为 `DeviceStatusWork`**、`MainDeviceWorkflow` **现为 `DeviceControlWork`**；`FaultRecord.State` 字段类型由旧四态 `DeviceState` 改为 `SubDeviceWeldStatus`（焊接过程态七态）。枚举级反向依赖的结论继续有效。

## 状态
已采纳（2026-08-31）

## 背景
用户审视项目结构后裁定：程序整个生命周期的记录文件（过程数据、生产信息、故障恢复数据等）需要一个专门的地方归口。现状两处割裂：

1. **过程记录挂在 PCLOperate 下**：`PCLOperate/RunFileRecord/`（RunRecordManager 1046 行 + RecordFrame + WeldActionRecord + SmartRayConverter）——「运行记录」是产品全生命周期数据，不是点云运算（PCLOperate）的子域，就近原则错位。
2. **FaultRecoveryManager 内联 SQLite 实现**：`MainDeviceControl/DeviceWorkflow/FaultRecoveryManager.cs` 的 `#region SQLite 持久化` 直接持有 `SQLiteDataBase`，DB 文件落在输出根目录 `FaultRecord.db`——违背 SqlLiteDatabase 模块「数据库操作归口 + `DataBase\` 子目录」的既有范式（AuthManager/ConfigManager/AutoParamManager/ProductDatabaseManager 均在模块内）。

用户已手动新建空目录 `ProductFileManager/` 并迁移 4 文件（AI 实施时检测到物理移动已完成，按「重读文件、保留用户改动」惯例接手收尾）。

## 决策

### 1. 过程记录迁入 ProductFileManager
- `PCLOperate/RunFileRecord/` 4 文件 → `ProductFileManager/`，目录 4→0 并删除；`PCLOperate` 仅余 3DModel/DataIO/Render（点云本域）。
- 命名空间 `AdaWeldSystem.PCLOperate.RunFileRecord` → `AdaWeldSystem.ProductFileManager`（目录对齐，沿 ADR-016 精神）。
- **类名与公共 API 全部不变**（`RunRecordManager.Instance` 等），8 个消费方只改 using：WeldProcess、CameraRun(SmartRay)、IntelligentLaserCameraRun、AlgorithmManager、DataReviewerPage、FileTraceForm、HelixRenderForm、RecordConfigForm。
- 跨目录引用保留：`AdaWeldSystem.PCLOperate.Models`（PointCloudData/Point3D）、`PCLOperate.DataIO`。
- csproj：4 条 Compile 改路径；删除 VS 生成的 `<Folder Include="ProductFileManager\" />` 孤儿条目。

### 2. 故障记录 DB 实现下沉 SqlLiteDatabase
- 新建 `SqlLiteDatabase/FaultRecordManager.cs`：继承 `DatabaseManagerBase`（构造传 `"FaultRecord.db"`，对齐 ProductDatabaseManager 范式），承载建表/插入/查询；DB 文件随之迁到 **`DataBase\FaultRecord.db`**。
- `FaultRecoveryManager` 删除 `#region SQLite 持久化`（EnsureDb/内联 Persist/`_db`/`_dbLock`/`_tableReady`），`Persist` 保留为「FaultRecord → string[] 映射 + 截断 + 失败日志」的领域侧适配，写入调用 `FaultRecordManager.Instance.InsertFaultRecord(values)`。
- **分层约束**：FaultRecordManager 以 `string[]` 为写入契约，**不引用领域类型**——SqlLiteDatabase 层不得反向依赖 MainDeviceControl。
- **FaultCategory/FaultRecord 数据载体留在 FaultRecoveryManager.cs**（ADR-025 决策维持；FaultRecoveryManager.cs 已于 2026-09-04 整体移除，ADR-032 D3）：它们是故障恢复闭环的领域载体，非 DB 实现。
- 管理器内部不做 try/catch 日志（对齐模块范式），由调用方兜底记 Warning。

### 3. 故障恢复业务消费方归口 ProductFileManager（2026-09-01 追加）

> **补充而非推翻**本节前两条：DB 实现下沉（§2）与业务消费方归口（§3）是同一归口目标的两个半步。

**背景**：§1 的决策背景写明归口范围是「过程数据、生产信息、**故障恢复数据**」，但 2026-08-31 只落了两件事——过程记录迁 `ProductFileManager/`、DB 实现下沉 `SqlLiteDatabase/`。故障恢复的**业务消费方** `FaultRecoveryManager.cs`（含 `FaultCategory`/`FaultRecord`）仍留在 `MainDeviceControl/DeviceWorkflow/`，归口未闭合。用户 2026-09-01 裁定：由 `ProductFileManager` 作为使用方承接。

**决策**：
- `MainDeviceControl/DeviceWorkflow/FaultRecoveryManager.cs` → `ProductFileManager/FaultRecoveryManager.cs`，命名空间 `AdaWeldSystem.MainDeviceControl.DeviceWorkflow` → `AdaWeldSystem.ProductFileManager`。整体迁移，不拆文件。
- **公共 API 零变化**（`Instance` / `RegisterRecoveryStrategy` / `RecordFault` 签名不变），6 个消费方只补 `using AdaWeldSystem.ProductFileManager`。
- 消费方：`SafetyWorkflow`（`"Safety"`）、`MainDeviceWorkflow`（`"MainDevice"`）、`LineLaserWorkflow`、`MonitorCameraWorkflow`、`MotionControlWorkflow`、`WeldParamControlWorkflow`。
- csproj：Compile 条目从 `MainDeviceControl\DeviceWorkflow\` 组移至 `ProductFileManager\` 组聚合。

**保留 `FaultRecord.State` 的强类型枚举（枚举级反向依赖）**：迁入后 `ProductFileManager` 需 `using DeviceState = AdaWeldSystem.MainDeviceControl.DeviceState.DeviceState`，与 `DeviceWorkflow/` 的正向引用构成模块级双向引用（架构页 11.3 环数 4→5）。

| 备选方案 | 放弃原因 |
|---|---|
| `State` 改为 `string` 断依赖 | 丢失强类型校验，写库时静默接受非法值 |
| `DeviceState` 枚举下沉到独立层 | 改动面远超本次归口，且需重估设备四态的归属 |

判定：反向依赖**仅限一个枚举类型**，不涉及工作流层，风险可控，维持强类型优先。

**`Persist` 的归属再澄清**：`FaultRecoveryManager.Persist` 只做「`FaultRecord` → `string[]` 映射 + 按列宽截断 + 失败记 Warning」，**不含 SQLite 代码**。它留在业务侧是 §2 分层约束的必然结果——若搬进 DB 层就要引用领域类型，触发反向依赖红线。原文件中名为 `#region SQLite 持久化` 的 region 因此易被误读为「SQLite 实现未下沉」，本次迁移已按 ADR-023 按成员类型重排 region，该命名歧义随之消除。

## 被放弃的备选方案

| 方案 | 放弃原因 |
|---|---|
| RunRecordManager 更名 ProductFileManager | 公共 API 零破坏优先；单例名与「记录管理器」语义仍相符，仅模块归口变化 |
| FaultRecordManager 引用 FaultRecord 类型做强类型 API | 造成 SqlLiteDatabase → MainDeviceControl 反向依赖 |
| SQLite 实现搬为静态工具类 | 与模块 DatabaseManagerBase 继承范式不一致 |
| FaultRecord.db 保持根目录 | 与模块 `DataBase\` 惯例不一致；旧 db 文件为空转数据，无迁移价值（PLC 未标定环境尚未投产） |

## 后果
- 正面：生命周期记录归口单一模块；数据库操作全部收敛 SqlLiteDatabase；FaultRecoveryManager 278→231 行、职责纯化为恢复闭环。
- 负面/注意：历史 `FaultRecord.db`（根目录）不再被读取；WeldProcess 私有方法名 `RecordActionToRunFileRecord` 与少量概念性注释保留旧称呼（指记录概念本身，非模块路径，后续触及再改）。

### §3 的后果（2026-09-01）
- 正面：故障恢复数据（业务消费方 + DB 实现 + 过程文件）三块拼图全部归口，ADR-027 背景声明的范围闭合；`DeviceWorkflow/` 目录由 9 文件收敛为 8 文件，纯工作流实现。
- 负面/注意：`ProductFileManager` ↔ `MainDeviceControl` 新增一组枚举级循环依赖（架构页 11.3 环数 4→5），已评估为可接受；6 个消费方均需补 using，遗漏即编译失败。

## 相关
- 前置：[[decisions/ADR-028-SafetyCheckConsolidation]]（FaultCategory/FaultRecord 归属）、[[decisions/ADR-010-WeldActionRecord]]（双记录设计）
- 模块：[[modules/ProductFileManager]]、[[modules/SqlLiteDatabase]]、[[modules/Safety]]、[[modules/DeviceControl]]、[[modules/PointCloudData]]
- API：[[api/FaultRecordManager]]、[[api/FaultRecoveryManager]]
- 教训：[[lessons/FaultRecoveryDeviceKey]]、[[guides/Config-Data-Tools]]
- 工具：[[guides/Project-Tools]] §1.2（Grep 结果截断导致消费方漏统计的排查教训）
