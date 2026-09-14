---
title: ProductFileManager 模块 — 产品生命周期记录
date: 2026-08-31
updated: 2026-09-14
tags: [模块, 产品记录, 过程数据, 生产信息, 文件, 数据库, ADR-046]
---

# ProductFileManager 模块 — 产品生命周期记录

> 掌管程序整个生命周期的记录：过程数据（`.pDat`/`.tmp` 点云与焊接过程记录）、焊缝参数调整记录、成功与产品信息记录（数据库）。
> **模块目录**：`AdaWeldSystem/ProductFileControl/`；**命名空间统一为 `AdaWeldSystem.ProductFileControl`**（2026-09-14 同轮收口，目录名与命名空间一致）。
> **来源**：2026-08-31 由 `PCLOperate/RunFileRecord/` 整体迁入（ADR-027）；2026-09-14 按 [[standards/ModuleOrganizationPattern]] 重构（[[decisions/ADR-046-ProductRecordModuleRefactor]]）。

> **✅ ADR-043 订阅方已闭环（2026-09-14）**：[[modules/WeldParamControl]] 算法触发的
> `FrameRecordRequested` / `AdjustmentRecordRequested` / `AbortRecordRequested` 三事件，
> 由 `ProductFileRecordManager` 构造时订阅——事件处理器只组装 item 并**入队（O(1)）**，
> 落盘由各记录类后台线程异步执行，**不在计算路径上同步落盘**。

## 目录结构

```
ProductFileControl/
├── Abstractions/
│   └── ProductRecordBase.cs       ← 抽象层（零第三方依赖）：Start/Stop/Abort/Enqueue(O(1))+后台 WorkerLoop→Persist
├── Records/
│   ├── SeamTrackRecord.cs         ← 焊缝追踪记录：焊缝结果信息 + 机器人信息 → .pDat 双记录 + .ply 点云
│   │                                ＋RecordFrame（帧 DTO）＋RecordFileStore（internal 文件机制）★自包含（ADR-047）
│   ├── WeldParamAdjustRecord.cs   ← 焊接参数调整记录：根据焊缝调整激光功率/送丝速度等时记录 → .pDat 调整记录
│   │                                ＋WeldActionRecord（双记录数据形态，ADR-008）★自包含+改名（ADR-047）
│   └── WeldResultRecord.cs        ← 成功/产品信息记录（含异常失败信息）→ 数据库（按日期分表）★新
└── ProductFileRecordManager.cs    ← 单例 Manager · 唯一对外入口 · ADR-043 记录事件订阅方
```

> ⚠️ 沿革（ADR-047，2026-09-14）：`SeamAdjustRecord`→`WeldParamAdjustRecord`、`SeamAdjustItem`→`WeldParamAdjustItem`；独立文件 `RecordFileStore.cs`/`RecordFrame.cs`/`WeldActionRecord.cs`/`SmartRayConverter.cs` 已移除（内容并入上示实现类文件；SmartRay 转换链 0 消费整链删除，含 `AddSmartRayFrame`）。

## 职责边界

| 数据类别 | 承载方 | 说明 |
|---|---|---|
| 过程数据（文件型） | `SeamTrackRecord`（内含 `RecordFileStore`） | `.pDat` v2 序列化 + `.tmp` 崩溃恢复 + 混淆回溯 |
| 参数调整数据（文件型） | `WeldParamAdjustRecord`（落盘经共享 `RecordFileStore`） | 与过程帧同 `.pDat`（ADR-008 双记录仍有效） |
| 成功/产品信息（DB 型） | `WeldResultRecord` | `SQLiteDatabaseManager.Instance.ProductDatabaseHelper`（[[modules/SQLiteDatabase]]，按日期分表） |

**依赖方向**：
- → `PCLOperate.Models`（PointCloudData/Point3D）、`PCLOperate.DataIO`（点云读写）。
- → `WeldParamControl`（只订阅 `WeldParamManager` 的三个记录请求事件，单向）。
- → `SQLiteDatabase`（`WeldResultRecord` 经 `SQLiteDatabaseManager` 写产品信息）。
- ⛔ 记录类/Store 之外不得出现 `.pDat`/`.tmp` 落盘逻辑；算法侧不感知本模块（[[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]]）。

## 对外契约（`ProductFileRecordManager.Instance`）

- **会话控制**：StartRecording / StopRecording / AbortRecording
- **帧与记录**：AddFrame / RecordWeldResult（`AddSmartRayFrame` 已随 ADR-047 删除）
- **回溯**：ParsePDatRecords / GetAllFrames / GetAllActions / SaveRecord / GetRecordFiles / GetTempFiles / GetWeldActionRecordFiles
- **配置**：ConfigFile / LoadConfigFromIni / SaveConfigToIni / RecordDirectory / TempDirectory / UseObfuscation / PathFallbackMessage / GetDateRecordDirectoryPath
- 配置 UI：`RecordConfigForm`（目录与混淆开关）、`FileTraceForm`（record/temp 文件选择）——均在 UIDesign。

## 消费方

- **记录事件源**：`WeldParamManager`（`FrameRecordRequested`/`AdjustmentRecordRequested`/`AbortRecordRequested`，Manager 透传算法事件）
- **直接调用方（5 处，均已迁移）**：LineLaserManager · DataReviewerPage（ParsePDatRecords 回溯）· HelixRenderForm（GetAllFrames 3D 回放）· FileTraceForm · RecordConfigForm

## 相关

- [[decisions/ADR-046-ProductRecordModuleRefactor]] — 三层结构决策（现行）
- [[decisions/ADR-047-RecordImplementationSelfContained]] — 文件自包含 + 改名 + SmartRay 链删除（现行）
- [[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]] — 记录职责隔离（订阅方已闭环）
- [[decisions/ADR-026-ProductLifecycleRecordModule]] — 产品记录归口（旧结构描述已被本轮取代）
- [[decisions/ADR-008-WeldActionRecord]] — 双记录设计（仍有效）
- [[modules/SQLiteDatabase]] — 产品信息数据库
- [[modules/WeldParamControl]] — 记录事件源
- [[lessons/AlgorithmControlRecordIsolation]] — 配套教训页
- [[modules/PointCloudData]]（PCLOperate 余部）
