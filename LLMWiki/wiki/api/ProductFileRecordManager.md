---
title: ProductFileRecordManager API 参考（产品文件记录管理器 · 模块唯一对外访问口）
date: 2026-09-17
tags: [API, 产品文件, 记录, 管理器, 单例, 唯一入口, 焊缝追踪, ADR-006, ADR-033, ADR-031, ADR-031]
source: AdaWeldSystem/ProductFileControl/ProductFileRecordManager.cs
---

# ProductFileRecordManager API 参考

> ProductFileControl 模块**唯一对外访问口**（单例）：管理全部记录类实例、记录数据存储与持久化配置，并订阅算法留痕事件。
> **位置**：`AdaWeldSystem/ProductFileControl/ProductFileRecordManager.cs`
> **命名空间**：`AdaWeldSystem.ProductFileControl`
> **沿革**：ADR-033/046/047 记录落位（算法纯净性与记录隔离 → 记录模块重构 → 记录实现自包含）；2026-09-20 补齐**产品生产生命周期**（[[decisions/ADR-037-ProductProductionRecordLifecycle]]：会话基名对齐三份记录、Job 切换入档、生产记录一次性落库）。
> 模块背景见 [[modules/ProductFileManager]]。

---

## 定位

```
起焊 / 焊毕（DeviceControlWork）——生产会话开关（ADR-037）
线激光 Job 切换（LineLaserManager.SwitchJob → JobChanged）——调整的一种（ADR-037 决 5）
算法侧（WeldParamManager 持有的算法）——只发请求
  ├─ FrameRecordRequested       ┐
  ├─ AdjustmentRecordRequested  ├→ ProductFileRecordManager.Instance（唯一入口，入队 O(1) 即返回）
  └─ AbortRecordRequested       ┘         ↓ 后台异步落盘
                                     RecordFileStore（记录文件存储独占持有，Records/RecordFileStore.cs）
                                       ├─ LineLaserContourRecord（线激光轮廓记录：仅点云 → .ply，2026-09-20 由 SeamTrackRecord 更名收窄）
                                       ├─ WeldParamControlRecord（工艺控制记录：过程帧 + 参数调整 + Job 切换 → .pDat）
                                       ├─ SeamTraceYRecord       （焊缝 Y：入图/出图/轴反馈 5 列 → .csv，2026-09-24 取代 TrajectoryRecord）
                                       └─ WeldResultRecord       （产品生产生命周期记录 → ProductDatabaseHelper 落库，ADR-037）
```

四职责（ADR-006）：① 管理记录类实例 ② 管理记录数据（存储独占持有）③ 持久化配置（Record.ini）④ 唯一访问口 + 订阅 [[api/WeldParamManager]] 记录请求事件（ADR-033 订阅方闭环）。

- **单例**（`Lazy<T>`），sealed 类；实现标准 `IDisposable.Dispose()`（ADR-001）：退订三个事件 + 释放记录类。
- **订阅即闭环**：构造时订阅三个记录请求事件，把事件参数转成记录项**入队即返回（O(1)）**，落盘在后台异步完成——算法线程零磁盘等待（ADR-033）。
- **会话同步启停（2026-09-20）**：`StartRecording/StopRecording/AbortRecording` 同时作用于轮廓记录与工艺控制记录两类会话；`OnFrameRecordRequested` 改投 `WeldParamControlRecord.RecordProcessFrame`（过程帧归工艺侧），点云 `AddFrame` 归 `LineLaserContourRecord`。
- **生产会话（2026-09-20，ADR-037）**：`BeginProductSession/EndProductSession` 把「起焊 → 焊毕」封装为一次产品生产会话，缓存产品码 / 起焊时间 / 记录状态 / **会话基名**，焊毕一次性把生产记录落产品库并归档三份记录文件。

## 记录类型

| 记录类 | 记录项 | 载荷 |
|---|---|---|
| `LineLaserContourRecord` | `ContourFrameItem` | 仅点云帧（线激光轮廓；2026-09-20 起不再含工艺快照） |
| `WeldParamControlRecord` | `WeldParamAdjustItem` | 机器人 X/Y/Z + 速度 + 送丝速度 + 激光功率 + 焊缝宽度 + `AdjustExecuted` + **`ActionType`（ProcessFrame / WeldParamAdjust / JobSwitch）** + **`JobId`**（JobSwitch 时有效）（ADR-037 决 5） |
| `SeamTraceYRecord` | `SeamTraceYPoint` | **5 列** `当前RobotX,入图RobotCSPX,CSPinYt,CSPoutY,实时Y`（2026-09-24 业主定版，取代原 4 列轨迹 `RobotX/RobotY/CspY/AxisY`；工艺快照仍由 `.pDat` 独占）→ 每拍 CSV 行；落盘与 .ply/.pDat **同会话子文件夹同基名**，DB 按基名定位三份 |
| `WeldResultRecord` | `WeldResultItem` | **产品生产生命周期记录（ADR-037 决 1）**：产品码 `SN` + 起焊时间 `StartTime` + 记录状态 `Status`（模拟 / 正常生产）+ 结果 `Result`（pass / fail）+ 异常原因 `Info`（⛔ 原「检测类型 / 焊接接头形式」不再记录） |

事件参数（WeldParamControl 侧定义）：`WeldFrameRecordEventArgs`（RobotX/Y/Z、RobotSpeed、FeedSpeed、LaserPower、WeldWidth、Timestamp）、`WeldAdjustmentRecordEventArgs`（继承前者）。

## 公共成员

### 生产会话（ADR-037）

一次「起焊 → 焊毕」= 一次生产会话；会话基名 = `[模拟]产品码_yyyyMMdd_HHmmss`，是三份记录文件与生产记录的唯一关联键。

| 成员 | 签名 | 职责 | 备注 |
|---|---|---|---|
| `BeginProductSession` | `void (string sn, bool isSimulation)` | 起焊：缓存产品码 / 起焊时间 / 记录状态 + 生成会话基名，并开启记录（点云/工艺/结果）。**焊缝 Y 会话（SeamTraceY）不在此开启**——2026-09-24 起由运控在 Ready 通过后调 `BeginSeamTraceYSession` | `sn` 空缺时以 `TEST` 占位；`isSimulation` 决定文件名「模拟」前缀 |
| `EndProductSession` | `void (string result, string info)` | 焊毕：停记录 + 归档三份文件 + **一次性写产品库** | 未开会话时幂等跳过；会话曾异常中止则强制 `fail` 并用中止原因补 `info` |
| `SessionBaseName` / `ProductSn` / `SessionStatus` | `string { get; }` | 本次会话的基名 / 产品码 / 状态 | 未开会话时基名为空串 |
| `GetSessionRecordFiles` | `List<string> (DateTime startTime, string sn, string status)` | 由生产记录**纯推算**三份记录文件路径 | 顺序：`.ply` / `.pDat` / `.csv`；只推算不判存在 |
| `SelectProductRecords` | `DataTable (DateTime date)` | 查指定日期的生产记录表 | 列集 `SN/Time/Status/Result/Info`；数据库不可用返回 null |
| `SelectProductRecords` | `DataTable (DateTime start, DateTime end)` | 查**时间区间**（闭区间）的生产记录（2026-10-09 区间筛选，[[decisions/ADR-056-DataReviewRangeFilterAndModularMultiSelect]]） | 产品库按 yyyyMMdd 分表、无跨表查询，故逐日读表后合并；`start > end` 自动交换；上限 366 天；区间内无记录返回**零行的表**（列齐全），不返回 null |
| `RecordJobSwitch` | `void (int jobId, double robotX, double robotY)` | 记录一次线激光分析 Job 切换（调整的一种） | 落 `.pDat`（`ActionType=JobSwitch`）；⛔ 不写轮廓记录 |

### 记录控制

| 成员 | 签名 | 职责 | 备注 |
|---|---|---|---|
| `StartRecording` / `StopRecording` | `void ()` | 开始 / 正常结束记录会话（Stop 排空队列后**自动归档**，归档基名优先取会话基名） | |
| `AbortRecording` | `void ()` | 异常中断记录（保留临时文件以便追溯） | 由 AbortRecordRequested 触发，并留存中止原因供生产记录 `Info` |
| `IsRecording` | `bool { get; }` | 记录会话进行中 | |
| `AddFrame` | `void (PointCloudData pointCloud)` | 添加一帧点云（线激光/监控相机路径） | |
| `RecordWeldResult` | `void (string sn, DateTime startTime, string status, string result, string info)` | 记录一条生产记录（DB 落库，入队即返回） | 2026-09-20 签名由 `inspectionType/checkInfo` 改为 `status/info`（ADR-037 决 1） |
| `CurrentFrameIndex` / `CachedFrameCount` | `int { get; }` | 当前帧索引 / 已缓存帧数 | 转发 RecordFileStore |

### 焊缝 Y 记录会话（2026-09-24 起，SeamTraceY 取代轨迹会话）

| 成员 | 签名 | 职责 | 备注 |
|---|---|---|---|
| `BeginSeamTraceYSession` | `bool ()` | 开启焊缝 Y 记录会话（**由运控在 Ready 通过后调用**，2026-09-24 前在生产会话开启时调用） | **返回值 2026-09-24 起生效**：会话已开启返回 true；**会话基名未就绪（生产会话未开启/已结束）返回 false 且不建任何文件**——修复「再次启动多出 `SeamTraceY_时间戳` 孤儿文件夹」（自造基名会让 CSV 落在会话文件夹外、DB 按基名归档定位不到）；运控按拍重试。文件同 `.ply`/`.pDat` 同基名同会话子文件夹 |
| `RecordSeamTraceYPoint` | `void (double robotX, double mapKeyX, double cspInYt, double cspOutY, double axisY)` | 记录一拍焊缝 Y（热路径只入内存，逐拍全量不去重） | **5 参**；`mapKeyX`/`cspInYt` 尚无入图点时传 0；~~`RecordTrajectoryPoint`~~ 随 `TrajectoryRecord.cs` 删除 |
| `FlushSeamTraceY` | `void ()` | 批量落盘（焊接停止沿 / 模拟停止调用） | |
| `EndSeamTraceYSession` | `void ()` | 结束会话：落盘并复位（生产会话结束 / 模拟关闭兜底） | 未开会话时无害 |
| `ReadSeamTraceYPoints` | `List<SeamTraceYPoint> (string filePath)` | 读取一份焊缝 Y 记录 CSV（回溯端一次性读取；旧 4 列轨迹格式按「出图=第 3 列、轴反馈=第 4 列、入图缺省」兼容） | 文件缺失返回空列表 |

### 配置与回溯

| 成员 | 签名 | 职责 | 备注 |
|---|---|---|---|
| `RecordDirectory` / `TempDirectory` | `string { get; set; }` | 记录 / 临时目录 | setter 同步给 Store 并确保目录存在 |
| `UseObfuscation` | `bool { get; set; }` | ⚠️ 2026-09-20 关闭：pDat 始终以明文 UTF-8 落盘（现场可用记事本查看），本属性**仅保留用于兼容历史混淆文件的读取回退**（`ReadPDatFile` 对旧混淆文件自动 XOR 还原），新写不再混淆 | |
| `LoadConfigFromIni` / `SaveConfigToIni` | `void ()` | 读写 `Config/ProductFileControl/Record_INI/Record.ini`（Paths + Settings） | 空路径回退默认并记入 `PathFallbackMessage` |
| `GetDateRecordDirectoryPath` | `string (DateTime date)` | 指定日期的记录子目录（yyyyMMdd） | 供回看端按日期索引 |
| `SaveRecord` | `List<string> (string fileName)` | 保存记录到正式文件（.ply + .pDat，按日期归档） | |
| `GetAllFrames` / `GetFramePointCloud` | `List<RecordFrame> ()` / `PointCloudData (int)` | 取缓存帧 / 指定帧点云 | |
| `GetAllActions` | `List<WeldActionRecord> ()` | 全部动作记录（过程帧 + 调整记录，双记录设计 ADR-008） | |
| `ParseFromTempFile` / `ConvertTempToNormal` | `bool (string)` / `List<string> (string, string)` | 解析临时文件 / 转换为正常 PLY 与 pDat | |
| `ParsePDatRecords` / `ReadPDatFile` | `List<WeldActionRecord> (string)` / `string (string)` | 解析 pDat（自动处理混淆） | |
| `GetTempFiles` / `GetRecordFiles` / `GetWeldActionRecordFiles` | `List<string> ()` 及按日期重载 | 文件枚举（按创建时间倒序） | |

## 已知问题（2026-09-20，[[decisions/ADR-039-SimulationTestAutoTerminationAndRecordCacheRelease]]）

- `SaveRecord(fileName)`：`.ply`/`.pDat` 落盘后**必须** `_frames.Clear()` + `_actionRecords.Clear()`，否则长时模拟内存只涨不降（陷阱十二）。崩溃恢复以 `.tmp` 文件为准，无需常驻内存。
- ⚠️ **逐拍不去重（现行）**：2026-09-20 曾按连续相同 robotX 去重，2026-09-22 实测「去重后仅 47.7 行/s 而输出节拍 94.8Hz」会掩盖被写段门限跳过的拍 ⇒ 已回退为逐拍全量入档；`SeamTraceYRecord.RecordPoint` 不做任何去重。
- **pDat 关闭混淆（2026-09-20 实测）**：`SaveActionsToPDat` 始终明文 UTF-8；`ReadPDatFile` 保留旧混淆文件 XOR 兼容回退。

## 相关页面

- [[decisions/ADR-056-DataReviewRangeFilterAndModularMultiSelect]] — 数据追溯区间筛选与多选合并（区间查询契约 / 多选语义）
- [[api/DataReviewerPage]] — 区间筛选 + 多选 + 悬停读数的消费方
- [[decisions/ADR-037-ProductProductionRecordLifecycle]] — 产品生产记录生命周期（会话基名 / 三份记录对齐 / Job 切换入档）
- [[modules/ProductFileManager]] — 模块说明（记录落位与目录）
- [[api/WeldParamManager]] — 记录请求事件发布方（FrameRecordRequested 等）
- [[api/LineLaserManager]] — `SwitchJob` / `JobChanged`（Job 切换唯一入口）
- [[api/DeviceControlWork]] — 生产会话起止触发点（起焊 / 停止 / 报警）
- [[api/SQLiteDatabaseManager]] — WeldResultRecord 经 ProductDatabaseHelper 落库（列契约 `SN/Time/Status/Result/Info`）
- [[decisions/ADR-006-ModuleOrganizationPatternStandard]] — 四职责唯一入口
- ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 算法纯净性与记录隔离（订阅方闭环）
- ADR-031（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 记录模块重构
- ADR-031（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 记录实现自包含
- ADR-031（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 双记录设计（过程帧 + 调整记录）
