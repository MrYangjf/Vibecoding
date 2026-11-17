---
title: ProductFileManager 模块 — 产品生命周期记录
date: 2026-08-31
updated: 2026-09-14
tags: [模块, 产品记录, 过程数据, 生产信息, 文件, 数据库, ADR-031]
---

# ProductFileManager 模块 — 产品生命周期记录

> 掌管程序整个生命周期的记录：过程数据（`.pDat`/`.tmp` 点云与焊接过程记录）、焊缝参数调整记录、成功与产品信息记录（数据库）。
> **模块目录**：`AdaWeldSystem/ProductFileControl/`；**命名空间统一为 `AdaWeldSystem.ProductFileControl`**（2026-09-14 同轮收口，目录名与命名空间一致）。
> **来源**：2026-08-31 由 `PCLOperate/RunFileRecord/` 整体迁入（ADR-021）；2026-09-14 按 [[standards/ModuleOrganizationPattern]] 重构（ADR-031（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]））。

> **✅ ADR-033 订阅方已闭环（2026-09-14）**：[[modules/WeldParamControl]] 算法触发的
> `FrameRecordRequested` / `AdjustmentRecordRequested` / `AbortRecordRequested` 三事件，
> 由 `ProductFileRecordManager` 构造时订阅——事件处理器只组装 item 并**入队（O(1)）**，
> 落盘由各记录类后台线程异步执行，**不在计算路径上同步落盘**。

## 目录结构

```
ProductFileControl/
├── Abstractions/
│   └── ProductRecordBase.cs       ← 抽象层（零第三方依赖）：Start/Stop/Abort/Enqueue(O(1))+后台 WorkerLoop→Persist
│                                    ＋ContourFrameItem（轮廓条目，仅点云）＋WeldParamAdjustItem（工艺条目，AdjustExecuted 分派）
├── Records/
│   ├── LineLaserContourRecord.cs  ← 线激光轮廓记录（2026-09-20 由 SeamTrackRecord 更名收窄）：仅点云帧 → .ply
│   ├── WeldParamControlRecord.cs  ← 工艺控制记录（2026-09-20 由 WeldParamAdjustRecord 更名扩展）：过程帧
│   │                                RecordProcessFrame + 参数调整 RecordAdjustment + Job 切换 RecordJobSwitch → .pDat ＋WeldActionRecord（ADR-008/040）
│   ├── RecordFileStore.cs         ← 记录文件存储（internal，2026-09-20 恢复独立文件）：会话/.pDat/.ply/.tmp/混淆回溯
│   ├── WeldResultRecord.cs        ← 产品生产生命周期记录（含异常失败信息）→ 数据库（按日期分表，ADR-037）
│   └── SeamTraceYRecord.cs        ← 焊缝 Y 记录（2026-09-24 取代 TrajectoryRecord）：5 列（当前RobotX/入图RobotCSPX/CSPinYt/CSPoutY/实时Y）→
│                                    Records\yyyyMMdd\<会话基名>.csv（缓存 + 终止落盘；原 MainDeviceControl/SimTrajectoryRecorder.cs 并入）
└── ProductFileRecordManager.cs    ← 单例 Manager · 唯一对外入口 · ADR-033 记录事件订阅方 · 会话同步启停两类记录
```

> ⚠️ 沿革（ADR-031，2026-09-14）：`SeamAdjustRecord`→`WeldParamAdjustRecord`、`SeamAdjustItem`→`WeldParamAdjustItem`；独立文件 `RecordFileStore.cs`/`RecordFrame.cs`/`WeldActionRecord.cs`/`SmartRayConverter.cs` 当时并入实现类文件（SmartRay 转换链 0 消费整链删除，含 `AddSmartRayFrame`）。
>
> ⚠️ **沿革（2026-09-20 记录类职责拆分，用户裁定）**：① `SeamTrackRecord`→`LineLaserContourRecord`（线激光轮廓记录**只保存线激光相关数据**，纯点云帧，不再承担过程帧快照与调整动作）；② `WeldParamAdjustRecord`→`WeldParamControlRecord`（工艺控制记录类**承接过程帧 + 调整动作**：`RecordProcessFrame`/`RecordAdjustment`，item 按 `AdjustExecuted` 分派）；③ `SeamTrackItem`→`ContourFrameItem`（仅点云，七项工艺快照字段删除）；④ `RecordFileStore`/`RecordFrame` 重新独立为 `Records/RecordFileStore.cs`（同时服务轮廓与工艺两类记录，Manager 回溯转发直连 Store）。

## 职责边界

| 数据类别 | 承载方 | 说明 |
|---|---|---|
| 线激光轮廓（文件型） | `LineLaserContourRecord`（2026-09-20 起） | 仅点云帧 → `.ply`；过程帧/调整动作/Job 切换均不在此记录 |
| 工艺过程帧 + 调整动作 + Job 切换（文件型） | `WeldParamControlRecord`（2026-09-20 起） | `.pDat` 动作格式 **v3**（新增 `JobId` 列）+ `.tmp` 崩溃恢复 + 混淆回溯（ADR-008 双记录仍有效，经共享 `RecordFileStore`；Job 切换见 ADR-037 决 5） |
| 焊缝跟踪轨迹（文件型） | `TrajectoryRecord`（2026-09-20） | **4 列** CSV（RobotX/RobotY/CspY 指令/AxisY 轴反馈，2026-09-21 增第 4 列——指令与反馈并列供判定 CSP 写入是否被驱动器执行；工艺调整快照由 `.pDat` 独占，不重复入 CSV）→ `Records\yyyyMMdd\<会话基名>.csv`；热路径只入内存、运动终止一次性落盘；连续相同 robotX 仅保留末行；**旧 3 列文件解析按 `NaN` 缺省第 4 列**，回看端曲线自动缺省 |
| 产品生产生命周期（DB 型） | `WeldResultRecord` | `SQLiteDatabaseManager.Instance.ProductDatabaseHelper`（[[modules/SQLiteDatabase]]，按日期分表，列契约 `SN/Time/Status/Result/Info`，ADR-037 决 1） |

> **2026-09-20 记录统一化（用户裁定）**：① **模拟与真实统一归口本模块**——原 `MainDeviceControl/SimTrajectoryRecorder.cs`（落 `Config/Simulation/`）删除并入 `TrajectoryRecord`，模拟文件名加「模拟」前缀（`RecordNamePrefix` 属性，`DeviceControlWork.StartSimulation/DisableSimulation` 置/清），不分模拟/真实文件夹；② **`StopRecording()` 自动归档**——停止会话排空队列后自动 `SaveRecord([前缀]Record_时间戳)` 把 `.ply`/`.pDat` 落入 `Records\yyyyMMdd\`（此前会话结束仅删临时文件、正式文件从不出现，记录链实际不可见）；③ **会话触发**：模拟 `StartSimulation`/`DisableSimulation` 与真实焊接指令 `DoSubWork`/`DoSubStop`/`DoSubAlarmStop`/`DoSubManualStop`（均幂等）；④ 混淆**已关闭**：pDat 始终以明文 UTF-8 落盘（现场可用记事本查看），`UseObfuscation` 属性仅保留用于兼容历史混淆文件的读取回退（2026-09-20 实测反馈：原 XOR 混淆导致 pDat 用 TXT 打开为乱码、无法查看，已关闭）。

> **2026-09-20 产品生产记录生命周期（用户裁定，[[decisions/ADR-037-ProductProductionRecordLifecycle]]）**：① **生产会话**——`BeginProductSession(sn, isSimulation)` / `EndProductSession(result, info)` 把「起焊 → 焊毕」封装为一次会话，缓存产品码 / 起焊时间 / 状态，并用**会话基名 `[模拟]产品码_yyyyMMdd_HHmmss`** 统一三份记录文件的命名（原本各自为政的 `Record_时间戳` / `Trajectory_时间戳` 取消）；② **焊毕一次性落库**——`WeldResultRecord` 升格为生命周期控制单位，产品库列契约收敛为 `SN/Time/Status/Result/Info`（删 `InspectionType` 焊接接头形式）；③ **Job 切换入档**——线激光分析 Job 切换属调整的一种，落 `.pDat`（`ActionType=JobSwitch`、`JobId`），⛔ 不写轮廓记录，仅焊接态由机器人指令驱动；④ **轨迹 CSV 回落 3 列**（RobotX/RobotY/CspY；工艺调整快照由 `.pDat` 独占，不再重复入 CSV）并取消 CSP 记录的模拟门禁（真实链路同样逐拍入档）；⑤ 回溯端由「记录目录文件列表」改为「产品库生产记录清单」，选中行一次性读三份文件绘图。

**依赖方向**：
- → `PCLOperate.Models`（PointCloudData/Point3D）、`PCLOperate.DataIO`（点云读写）。
- → `WeldParamControl`（只订阅 `WeldParamManager` 的三个记录请求事件，单向）。
- → `SQLiteDatabase`（`WeldResultRecord` 经 `SQLiteDatabaseManager` 写产品信息）。
- ⛔ 记录类/Store 之外不得出现 `.pDat`/`.tmp` 落盘逻辑；算法侧不感知本模块（ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]））。

## 对外契约（`ProductFileRecordManager.Instance`）

- **生产会话（2026-09-20，ADR-037）**：BeginProductSession / EndProductSession / SessionBaseName / ProductSn / SessionStatus / GetSessionRecordFiles / SelectProductRecords / RecordJobSwitch
- **会话控制**：StartRecording / StopRecording（自动归档，基名优先取会话基名）/ AbortRecording
- **轨迹会话**：BeginTrajectorySession / RecordTrajectoryPoint（4 参，2026-09-21 增 axisY）/ FlushTrajectory / EndTrajectorySession / ReadTrajectoryPoints（2026-09-20）
- **帧与记录**：AddFrame / RecordWeldResult（`sn, startTime, status, result, info`；`AddSmartRayFrame` 已随 ADR-031 删除）
- **回溯**：ParsePDatRecords / GetAllFrames / GetAllActions / SaveRecord / GetRecordFiles / GetTempFiles / GetWeldActionRecordFiles / SelectProductRecords
- **配置**：ConfigFile / LoadConfigFromIni / SaveConfigToIni / RecordDirectory / TempDirectory / UseObfuscation / RecordNamePrefix / PathFallbackMessage / GetDateRecordDirectoryPath
- 配置 UI：`RecordConfigForm`（目录与混淆开关）、`FileTraceForm`（record/temp 文件选择）——均在 UIDesign。

## 消费方

- **记录事件源**：`WeldParamManager`（`FrameRecordRequested`/`AdjustmentRecordRequested`/`AbortRecordRequested`，Manager 透传算法事件）
- **生产会话驱动方**：`DeviceControlWork`（`DoSubWork` 起焊 / `DoSubStop`·`DoSubManualStop` 记 pass / `DoSubAlarmStop` 记 fail；`StartSimulation`·模拟关闭端同源）
- **Job 切换驱动方**：`LineLaserManager.JobChanged` → `DeviceControlWork.OnLineLaserJobChanged`（仅焊接态入档）
- **直接调用方（5 处，均已迁移）**：LineLaserManager · DataReviewerPage（`SelectProductRecords` + `GetSessionRecordFiles` + `ParsePDatRecords` + `ReadTrajectoryPoints` 六系列回溯）· HelixRenderForm（GetAllFrames 3D 回放）· FileTraceForm · RecordConfigForm

## 已知问题（模拟测试，2026-09-20 / [[decisions/ADR-039-SimulationTestAutoTerminationAndRecordCacheRelease]]）

- **`RecordFileStore.SaveRecord()` 落盘后须释放内存缓存**：`.ply`/`.pDat` 持久化完成后必须 `_frames.Clear()` + `_actionRecords.Clear()`，否则长时模拟内存只涨不降（[[lessons/SimulationAutoBranching]] 陷阱十二）。崩溃恢复以 `.tmp` 文件为准，无需常驻内存。
- ⚠️ **逐拍不去重（现行，2026-09-22 回退）**：去重会把 94.8Hz 输出节拍记成 47.7 行/s、掩盖被写段门限跳过的拍；`SeamTraceYRecord.RecordPoint` 逐拍全量入档，重复 robotX 行属「机器人 X 采样慢于 CSP 拍」的真实节拍差，回看端按 RobotX 连 Y 即可。
- **pDat 关闭混淆（2026-09-20 实测）**：原 `ObfuscateBytes` 让 pDat 用 TXT 打开为乱码、现场无法查看；`SaveActionsToPDat` 始终 `File.WriteAllText(..., Encoding.UTF8)`，保留 `ReadPDatFile` 对旧混淆文件的 XOR 兼容回退（历史文件仍可读取）。

## 相关

- [[decisions/ADR-037-ProductProductionRecordLifecycle]] — 产品生产记录生命周期（会话基名 / 三份记录对齐 / Job 切换入档）
- ADR-031（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 三层结构决策（现行）
- ADR-031（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 文件自包含 + 改名 + SmartRay 链删除（现行）
- ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 记录职责隔离（订阅方已闭环）
- [[decisions/ADR-031-ProductLifecycleRecordModule]] — 产品记录归口（旧结构描述已被本轮取代）
- ADR-031（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 双记录设计（仍有效）
- [[modules/SQLiteDatabase]] — 产品信息数据库
- [[modules/WeldParamControl]] — 记录事件源
- [[lessons/AlgorithmControlRecordIsolation]] — 配套教训页
- [[modules/PointCloudData]]（PCLOperate 余部）


## 2026-09-21 全盘审计修复（记录链并发与死代码）

| # | 问题 | 修复 |
|---|---|---|
| 1 | `SeamTraceYRecord.RecordPoint` 在 `lock(_lock)` **外**读会话标志（写侧全在锁内） | 判据移入锁内；`RecordDirectory` 读写一并加锁。热路径每拍调用，可导致点写入已结束会话（撕裂值） |
| 2 | `ProductRecordBase._workerRunning` / `_disposed` / `IsRecording` 跨线程无 `volatile` | 改为 `volatile`（`IsRecording` 以 `volatile` 字段承载属性） |
| 3 | `FlushPending()` 为 `while (!_queue.IsEmpty) Thread.Sleep(10)`，无超时上限、也不判断后台线程存活 | 改为：worker 未存活直接告警返回；存活时带 5s 上限排空，超时记告警 |
| 4 | `WeldParamControlRecord.Log` 为私有零调用死成员 | 删除（落盘告警统一由基类 `ProductRecordBase.Log` 承担） |

> 判据来源：[[lessons/StepDrivenWorkflowPitfalls]] 七.3 坑四「字段有配套锁 ⇒ 该字段在锁外出现的每一处都是 BUG」。
