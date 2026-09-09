---
title: ProductFileManager 模块 — 产品生命周期记录
date: 2026-08-31
tags: [模块, 产品记录, 过程数据, 生产信息, 文件]
---

# ProductFileManager 模块 — 产品生命周期记录

> 掌管程序整个生命周期的记录文件：过程数据（`.pDat`/`.tmp` 点云与焊接过程记录）、生产信息、**故障恢复数据**等。
> **模块位置**：`AdaWeldSystem/ProductFileManager/`
> **来源**：2026-08-31 由 `PCLOperate/RunFileRecord/` 整体迁入（ADR-027）；命名空间 `AdaWeldSystem.ProductFileManager`。
> **2026-09-01 二次归口**：`FaultRecoveryManager.cs`（含 `FaultCategory` / `FaultRecord`）自 `MainDeviceControl/DeviceWorkflow/` 迁入，补齐 ADR-027 背景中「故障恢复数据归口一处」的第三块拼图——此前只完成了 DB 实现下沉（[[modules/SqlLiteDatabase]]），业务消费方仍留在设备控制层。

## 目录结构

```
ProductFileManager/
├── RunRecordManager.cs      ← 记录管理器单例（记录控制/落盘/临时文件/混淆回溯）
├── RecordFrame.cs           ← 记录帧数据结构（点云帧）
├── WeldActionRecord.cs      ← 焊接动作/过程记录（双记录：过程帧 + 调整动作，ADR-010）
├── SmartRayConverter.cs     ← SmartRay 原始点云 → PointCloudData 转换器
└── FaultRecoveryManager.cs  ← 故障恢复管理器单例（故障恢复数据归口使用方，2026-09-01 迁入；已移除 2026-09-04，ADR-032 D3）
```

## 职责边界

| 数据类别 | 承载方 | 说明 |
|---|---|---|
| 过程数据（文件型） | `RunRecordManager`（本模块） | `.pDat` v2 序列化 + `.tmp` 崩溃恢复 + 混淆回溯 |
| 故障恢复数据（DB 型） | `FaultRecordManager`（[[modules/SqlLiteDatabase]]，持久化）+ `FaultRecoveryManager`（**本模块**，归口使用方） | `FaultRecoveryManager` 做「领域对象 → `string[]` 值数组」适配与字段截断后调 `InsertFaultRecord`；SQLite 建表/插入/查询全在 DB 层，表 `FaultRecord` |
| 生产信息 | 预留 | 后续管理器落位于本目录 |

**依赖方向**：
- → `PCLOperate.Models`（PointCloudData/Point3D）、`PCLOperate.DataIO`（点云读写）；`PCLOperate` 的 3DModel/DataIO/Render 仍留在原处——迁移只动了 RunFileRecord 子域。
- → `SqlLiteDatabase`（`FaultRecordManager` 写库）。
- → `MainDeviceControl.DeviceState`（`SubDeviceWeldStatus` 焊接过程态七态枚举，`FaultRecord.State` 字段类型）。**这是刻意保留的枚举级反向依赖**：`MainDeviceControl/DeviceWorkflow/` 下 5 个子工作流 + 2 个管控类都要引用本模块记录故障，构成模块级双向引用；替代方案（State 改 string / 枚举下沉）会牺牲强类型或扩大改动面，已评估后放弃。
- ⚠️ **分层红线**：`SqlLiteDatabase` 层**不得反向依赖**本模块的领域类型（`FaultRecord`），写入契约固定为 `string[]`（ADR-027 §2）。

## 对外契约（类名与公共 API 迁移前后不变）

- `RunRecordManager.Instance`：StartRecording / StopRecording / AbortRecording / AddFrame / AddSmartRayFrame / RecordProcessFrame / RecordAdjustment / SaveRecord / ConvertTempToNormal / ParsePDatRecords / GetAllFrames / GetAllActions / GetRecordFiles / GetTempFiles / RecordDirectory / TempDirectory / UseObfuscation / ConfigFile
- 配置 UI：`RecordConfigForm`（目录与混淆开关）、`FileTraceForm`（record/temp 文件选择）——均在 UIDesign/SubView。

## 消费方（14 处）

**过程记录 `RunRecordManager`（8 处）**：WeldProcess（过程帧+调整记录）· CameraRun(SmartRay)（AddSmartRayFrame）· IntelligentLaserCameraRun（AddFrame）· AlgorithmManager(EmguALG) · DataReviewerPage（ParsePDatRecords 回溯）· HelixRenderForm（GetAllFrames 3D 回放）· FileTraceForm · RecordConfigForm

**故障恢复 `FaultRecoveryManager`（6 处，均在 `MainDeviceControl/DeviceWorkflow/`）**：`DeviceStatusWork`（`"Safety"`）· `DeviceControlWork`（`"MainDevice"`）· `LineLaserWorkflow` · `MonitorCameraWorkflow` · `MotionControlWorkflow` · `WeldParamControlWorkflow`（后四处传 `Tag`）

> ⚠️ 6 个消费方全部需 `using AdaWeldSystem.ProductFileManager`。排查教训：初次 Grep 因结果截断只列出 2 处，差点漏改 4 个文件，详见 [[guides/Project-Tools]] §1.2。

## 相关

- [[decisions/ADR-026-ProductLifecycleRecordModule]]（含 §3 故障恢复业务消费方归口，2026-09-01 追加）
- [[api/FaultRecoveryManager]] · [[api/FaultRecordManager]]
- [[modules/SqlLiteDatabase]]（FaultRecordManager）
- [[modules/Safety]] · [[modules/DeviceControl]]（消费方所在模块）
- [[modules/PointCloudData]]（PCLOperate 余部）
- [[decisions/ADR-008-WeldActionRecord]]
- [[lessons/FaultRecoveryDeviceKey]]（策略注册与记录 key 必须同源）
