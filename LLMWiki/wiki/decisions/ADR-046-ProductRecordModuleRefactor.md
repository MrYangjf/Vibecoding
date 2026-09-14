---
title: ADR-046 产品记录模块重构（ProductRecordBase 抽象 + 三记录类 + Manager，ADR-043 订阅方闭环）
date: 2026-09-14
tags: [决策, 产品记录, ProductFileControl, Manager, 数据库, ADR-046]
status: accepted
---

# ADR-046 产品记录模块重构（ProductRecordBase 抽象 + 三记录类 + Manager）

> ⚠️ **沿革（2026-09-14 同日增补，见 [[decisions/ADR-047-RecordImplementationSelfContained]]）**：
> - `SeamAdjustRecord` → **`WeldParamAdjustRecord`**、`SeamAdjustItem` → **`WeldParamAdjustItem`**（语义纠正：焊缝驱动的焊接参数调整记录）；
> - `RecordFileStore.cs` / `RecordFrame.cs` 并入 `SeamTrackRecord.cs`，`WeldActionRecord.cs` 并入 `WeldParamAdjustRecord.cs`，`SmartRayConverter.cs` 及 `AddSmartRayFrame` 链删除——下文目录结构中这 4 个游离文件已不存在；
> - 对外 API 与双记录 `.pDat` 机制不变。

## 状态

已采纳（2026-09-14）。

## 背景

[[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]] 将算法侧记录请求改为三个事件（`FrameRecordRequested` / `AdjustmentRecordRequested` / `AbortRecordRequested`），但订阅方一直是 **TODO**——`ProductFileControl/RunRecordManager.cs`（1046 行单文件）既当文件 IO 又当对外 Manager，落盘责任没有归位。

用户 2026-09-14 裁定重构为「抽象类 + 实现文件夹 + Manager」，并补充：**焊接异常和失败信息记录扩展为成功与产品信息记录（连接数据库管理）**；焊缝追踪记录 = 焊缝结果信息 + 机器人信息；焊缝参数调整记录 = 焊缝调整信息 + 机器人信息。命名空间同轮统一为 `AdaWeldSystem.ProductFileControl`。

## 决策

1. **抽象层** `ProductFileControl/Abstractions/ProductRecordBase.cs`（零第三方依赖）：
   - 记录项基类 `RecordItem`（Timestamp）+ 三个数据结构：`SeamTrackItem`（焊缝结果 + 机器人信息：RobotX/Y/Z/Speed/FeedSpeed/LaserPower/WeldWidth/PointCloud）、`SeamAdjustItem`（调整信息 + 机器人信息 + AdjustData）、`WeldResultItem`（Sn/StartTime/InspectionType/Result/CheckInfo）。
   - `abstract class ProductRecordBase : IDisposable`：`Start()` / `Stop()` / `Abort()` / `IsRecording` / `Name`；**订阅方只做入队 O(1)**（`ConcurrentQueue` + `AutoResetEvent` 后台 WorkerLoop），落盘在后台线程调用 abstract `Persist(RecordItem)`（H9：实现层只计算/只入队，不阻塞算法路径）。

2. **三个实现类**（`ProductFileControl/Records/`，继承 `ProductRecordBase`）：
   | 实现类 | 落盘去向 |
   |---|---|
   | `SeamTrackRecord` | `RecordFileStore`：`.pDat` 双记录（ADR-008 结论仍有效）+ `.ply` 点云 + `.tmp` 崩溃恢复 |
   | `SeamAdjustRecord` | `RecordFileStore.AddAdjustRecord`（同 `.pDat`） |
   | `WeldResultRecord` | **数据库**：`SQLiteDatabaseManager.Instance.ProductDatabaseHelper.AddProductInfo(...)`（按日期分表），回溯走 `SelectResultTable` |

3. **文件机制下放**：`RecordFileStore.cs`（internal sealed）承接原 `RunRecordManager` 全部 IO（StartSession/StopSession/AbortSession、帧索引自取 `_frameIndex`、混淆回溯、Parse/Convert 等），构造注入目录与混淆开关——**记录类自身不碰文件系统**。

4. **Manager 单例** `ProductFileRecordManager.cs`：持有 store + 三记录类；**构造时订阅 `WeldParamManager.Instance` 的三个记录请求事件**（ADR-043 TODO 闭环），事件处理器组装 item 后转发对应记录类入队；对外保留旧 API 全集（StartRecording/StopRecording/AbortRecording/AddFrame/AddSmartRayFrame/RecordWeldResult/ParsePDatRecords/GetAllFrames/GetAllActions/GetRecordFiles/GetTempFiles/ConfigFile/LoadConfigFromIni/SaveConfigToIni 等），五个消费方只换 `RunRecordManager.Instance` → `ProductFileRecordManager.Instance` + using。

5. **删除** `RunRecordManager.cs`；命名空间统一 `AdaWeldSystem.ProductFileControl`。

## 目录结构（变更后）

```
ProductFileControl/
├── Abstractions/
│   └── ProductRecordBase.cs        ← 抽象层（入队 O(1) + 后台落盘模板）
├── Records/
│   ├── SeamTrackRecord.cs          ← 焊缝追踪记录（结果 + 机器人信息）
│   ├── SeamAdjustRecord.cs         ← 焊缝参数调整记录（调整 + 机器人信息）
│   └── WeldResultRecord.cs         ← 成功/产品信息记录（数据库）★新
├── RecordFileStore.cs              ← internal 文件机制（.pDat/.ply/.tmp/混淆回溯）
├── ProductFileRecordManager.cs     ← 单例 Manager · 唯一对外入口 · 记录事件订阅方
├── RecordFrame.cs / WeldActionRecord.cs / SmartRayConverter.cs
```

## 后果

- 正面：ADR-043 的「订阅方入队 O(1) + 后台异步落盘」正式落地；记录职责三分类（文件双记录 / 文件调整 / 数据库产品信息）；Manager 化后配置持久化唯一归口。
- 负面 / 沿革：`RunRecordManager` 旧名在历史 ADR（ADR-026/008/043）与日志中仍会出现，检索以本条与 [[modules/ProductFileManager]] 现行页为准（已登记 drift 扫描器 REMOVED 表）。
- 约束：
  - ⛔ 外部不得绕过 Manager 访问记录类或 RecordFileStore（H6）；
  - ⛔ 记录类/Store 之外不得出现 `.pDat`/`.tmp` 落盘逻辑（H9 延伸）；
  - ⛔ 算法侧仍只触发事件，不感知记录模块（ADR-043）。

## 相关

- [[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]] — 记录职责隔离（本决策闭环其订阅方 TODO）
- [[decisions/ADR-008-WeldActionRecord]] — 双记录设计（`.pDat` 内过程帧 + 调整动作，仍有效）
- [[decisions/ADR-026-ProductLifecycleRecordModule]] — 产品记录归口（结构已被本轮取代）
- [[decisions/ADR-042-ModuleOrganizationPatternStandard]] — 模块组织范式
- [[modules/ProductFileManager]] / [[modules/SQLiteDatabase]] — 模块说明
- [[lessons/AlgorithmControlRecordIsolation]] — 配套教训页（订阅方已落地）
