---
title: ADR-031 产品记录模块现行决策（归口 · ProductRecordBase 抽象 · 记录类自包含；整合原 008/026/046/047）
date: 2026-08-31
updated: 2026-10-30
tags: [决策, 模块, 产品记录, ProductFileControl, ProductRecordBase, SQLite, 双记录, 文件自包含, 归口, merged, ADR-031]
status: accepted
merged_from: [ADR-008, ADR-026, ADR-046, ADR-047]
---

# ADR-031 产品记录模块现行决策（归口 · ProductRecordBase 抽象 · 记录类自包含）

> 本页为整合页（2026-09-17），收拢原 ADR-008 / ADR-017 / ADR-031 / ADR-031 的全部现行裁定；被后续演进推翻的中间态见「被推翻的中间态」与「沿革」。记录职责隔离与算法纯净性本身见 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]（原 ADR-033 已并入），本页不重复。

## 背景

1. **归口割裂（2026-08-31 原起点）**：程序整个生命周期的记录文件（过程数据、生产信息、故障恢复数据等）需要专门归口。当时两处错位——过程记录挂在 `PCLOperate/RunFileRecord/`（「运行记录」不是点云运算的子域，就近原则错位）；`FaultRecoveryManager` 内联 SQLite 实现（DB 文件落输出根目录，违背 SQLiteDatabase 模块「数据库操作归口 + `DataBase\` 子目录」范式）；
2. **单文件巨石（2026-09-14 起点）**：`ProductFileControl/RunRecordManager.cs`（1046 行）既当文件 IO 又当对外 Manager，[[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]（原 ADR-033）把算法侧记录请求改为三事件后，订阅方一直是 TODO，落盘责任没有归位；
3. **游离文件与语义错误（2026-09-14 收尾起点）**：重构落地后 `RecordFileStore.cs` / `RecordFrame.cs` / `WeldActionRecord.cs` / `SmartRayConverter.cs` 四个文件不属三层架构任一层级；且 `SeamAdjustRecord` 命名语义错误——该记录实际是**根据焊缝（宽度等特征）调整激光功率、送丝速度等焊接参数时**的记录。

用户裁定演进路径：归口 → 「抽象类 + 实现文件夹 + Manager」→ 实现类文件自包含。

## 现行决策

### 一、记录归口一处（结论持续有效）

生命周期记录（过程数据、生产信息、记录配置）**归口单一模块**，现名 `ProductFileControl/`（命名空间 `AdaWeldSystem.ProductFileControl`；目录沿革见下）。归口目标的另一半——故障记录 DB 下沉——其范式结论仍有效：数据库操作归口 SQLiteDatabase 模块、DB 文件落 `DataBase\` 子目录、DB 层以 `string[]` 为写入契约**不引用领域类型**（SQLiteDatabase 层不得反向依赖业务模块）、管理器内部不做 try/catch 日志由调用方兜底记 Warning。
> ⚠️ 沿革：承载类 `FaultRecordManager` / 业务侧 `FaultRecoveryManager` 已于 2026-09-04 随故障恢复模块**整体移除**（[[decisions/ADR-015-ErrorReportingHierarchy]] D3，架构无此定义），其 API 页已删（纯文本：api/FaultRecordManager、api/FaultRecoveryManager）；上述分层范式作为 SQLiteDatabase 模块纪律继续适用。

### 二、ProductRecordBase 抽象（三层架构：抽象层 / Records 实现层 / Manager）

1. **抽象层** `ProductFileControl/Abstractions/ProductRecordBase.cs`（零第三方依赖）：
 - 记录项基类 `RecordItem`（Timestamp）+ 三个数据结构：`SeamTrackItem`（焊缝结果 + 机器人信息：RobotX/Y/Z/Speed/FeedSpeed/LaserPower/WeldWidth/PointCloud）、`WeldParamAdjustItem`（调整信息 + 机器人信息 + AdjustData）、`WeldResultItem`（Sn/StartTime/InspectionResult/CheckInfo）；
 - `abstract class ProductRecordBase : IDisposable`：`Start()` / `Stop()` / `Abort()` / `IsRecording` / `Name`；**订阅方只做入队 O(1)**（`ConcurrentQueue` + `AutoResetEvent` 后台 WorkerLoop），落盘在后台线程调用 abstract `Persist(RecordItem)`——实现层只计算/只入队，不阻塞算法路径（H9）。
2. **三个实现类**（`ProductFileControl/Records/`，继承 `ProductRecordBase`）：

 | 实现类 | 语义 | 落盘去向 |
 |---|---|---|
 | `SeamTrackRecord` | 焊缝追踪记录（焊缝结果信息 + 机器人信息） | 自包含 `RecordFileStore`：`.pDat` 双记录 + `.ply` 点云 + `.tmp` 崩溃恢复 |
 | `WeldParamAdjustRecord` | 焊接参数调整记录（调整信息 + 机器人信息；2026-09-14 由 `SeamAdjustRecord` 改名） | 同 `.pDat`（`AddAdjustRecord`） |
 | `WeldResultRecord` | 成功/产品信息记录（由「焊接异常和失败信息记录」扩展而来，连接数据库管理） | `SQLiteDatabaseManager.Instance.ProductDatabaseHelper.AddProductInfo(...)`（按日期分表），回溯走 `SelectResultTable` |

3. **Manager 单例** `ProductFileRecordManager.cs`（唯一对外入口）：
 - **构造时订阅 `WeldParamManager.Instance` 的三个记录请求事件**（`FrameRecordRequested` / `AdjustmentRecordRequested` / `AbortRecordRequested`），事件处理器组装 item 后转发对应记录类入队——算法侧订阅 TODO 至此闭环；
 - 对外保留旧 API 全集（StartRecording/StopRecording/AbortRecording/AddFrame/RecordWeldResult/ParsePDatRecords/GetAllFrames/GetAllActions/GetRecordFiles/GetTempFiles/ConfigFile/LoadConfigFromIni/SaveConfigToIni 等）；消费方只换 `RunRecordManager.Instance` → `ProductFileRecordManager.Instance` + using。

### 三、记录实现类文件自包含

1. **同文件吸收（对外 API 零变化）**：`RecordFileStore.cs` 并入 `Records/SeamTrackRecord.cs`（internal sealed，会话/.pDat/.ply/.tmp/混淆回溯机制归焊缝追踪记录所有）；`RecordFrame.cs` 并入 `SeamTrackRecord.cs`（public 保持——`GetAllFrames()` 返回类型）；`WeldActionRecord.cs` 并入 `Records/WeldParamAdjustRecord.cs`（public 保持——DataReviewerPage 回溯消费）；
2. **SmartRay 链整删**：`SmartRayConverter.cs` + `SeamTrackRecord.AddSmartRayFrame` + `Manager.AddSmartRayFrame` 整链删除（Grep 核查模块外 0 调用，死代码）；
3. **范围外不动**：`WeldParamManager` 侧事件 `AdjustmentRecordRequested` / `WeldAdjustmentRecordEventArgs` 命名保持（跨模块最小变更）。

### 四、双记录设计（ADR-008 有效结论，持续有效）

1. **字段**：调整记录 11 字段——`FrameIndex` / `Timestamp` / `ActionType` / `RobotX,Y,Z` / `RobotSpeed` / `FeedSpeed` / `LaserPower` / `WeldWidth` / `AdjustExecuted` / `AdjustData`； ⚠️ **已被 [[decisions/ADR-052-ProductionRecordSchema]] 演进（2026-10-08 审计补注）**：`WeldActionRecord` 现行 **20 字段**（新增 `JobId` / `SeamPointY` / `SeamPointZ` / `TaPositionMm` / `LaPositionMm` / `GalvoAmplitudeMm` / `GalvoPatternId` / `HeadTempC` 等，二进制升 v4）；本条 11 字段为**历史描述**，代码实测 `WeldParamControlRecord.cs` 为 20 个属性。
2. **双记录入口**：每帧过程快照（`AdjustExecuted=false`）与调整动作记录（`AdjustExecuted=true`）**落同一 `.pDat` 文件**（version=2 二进制 + 文本回退；`.tmp` 用于崩溃恢复）；`DataReview` 回溯时用红色点标记调整记录；
3. **记录驱动源**：由算法/参数侧经事件触发（ADR-008 闭环），与工作流桩函数解耦（[[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]）。

## 目录结构（现行）

```
ProductFileControl/
├── Abstractions/
│ └── ProductRecordBase.cs ← 抽象层（RecordItem + SeamTrackItem/WeldParamAdjustItem/WeldResultItem）
├── Records/
│ ├── SeamTrackRecord.cs ← 焊缝追踪记录 + RecordFrame + RecordFileStore（自包含）
│ ├── WeldParamAdjustRecord.cs ← 焊接参数调整记录 + WeldActionRecord（自包含）★改名
│ └── WeldResultRecord.cs ← 成功/产品信息记录（数据库）
└── ProductFileRecordManager.cs ← 单例 Manager · 唯一对外入口 · 记录事件订阅方
```

## 约束（后续必须遵守）

- ⛔ 外部不得绕过 Manager 访问记录类或 RecordFileStore（H6）；
- ⛔ 记录类/Store 之外不得出现 `.pDat` / `.tmp` 落盘逻辑（H9 延伸）；
- ⛔ `Records/` 下不得再新开独立的数据结构/配置文件——数据结构并入对应实现类文件（[[decisions/ADR-006-ModuleOrganizationPatternStandard]] 实现层纪律的文件维度延伸）；
- ⛔ 算法侧仍只触发事件，不感知记录模块（ADR-008 算法纯净性）；
- ⛔ SQLiteDatabase 层不得反向依赖业务模块（DB 写入契约用 `string[]`）。

## 备选方案（已否决）

| 方案 | 放弃原因 |
|---|---|
| RunRecordManager 更名 ProductFileManager | 公共 API 零破坏优先；单例名与「记录管理器」语义仍相符，仅模块归口变化 |
| `FaultRecord.State` 改为 `string` 断依赖 | 丢失强类型校验，写库时静默接受非法值（历史方案，随故障恢复模块移除而失效） |
| `DeviceState` 枚举下沉到独立层 | 改动面远超当次归口，且需重估设备四态归属 |
| FaultRecordManager 引用 FaultRecord 类型做强类型 API | 造成 SQLiteDatabase → 业务模块反向依赖 |
| SQLite 实现搬为静态工具类 | 与模块 DatabaseHelperBase 继承范式不一致 |
| FaultRecord.db 保持输出根目录 | 与模块 `DataBase\` 惯例不一致；旧 db 文件为空转数据，无迁移价值 |
| 记录类内直接落盘（不做 Store/抽象分层） | 算法路径被 IO 阻塞，违反 H9「实现层只计算/只入队」 |

## 后果

- 正面：生命周期记录归口单一模块；记录职责三分类清晰（文件双记录 / 文件调整 / 数据库产品信息）；ADR-008 的「订阅方入队 O(1) + 后台异步落盘」正式落地；目录无游离文件，命名与配置节 `WELD_PARAM_ADJUST` 对齐；Manager 化后配置持久化唯一归口；
- 负面 / 注意：`RunRecordManager` / `SeamAdjustRecord` / `SeamAdjustItem` / `RecordFileStore.cs`（文件名）/ `RecordFrame.cs` / `WeldActionRecord.cs` / `SmartRayConverter.cs` 等旧名在历史 ADR 与日志中仍会出现，检索以本页与 [[modules/ProductFileManager]] 现行页为准（drift REMOVED/RENAMED 表已登记）；`.pDat` 双记录机制原样搬运未重设计，序列化格式零迁移。

## 落地清单（四页并集）

| 项 | 状态 |
|---|---|
| 归口迁移（PCLOperate/RunFileRecord 4 文件 → 记录模块，公共 API 零变化，消费方只改 using） | ✅ |
| `ProductRecordBase` 抽象层（RecordItem + 三 Item + 入队 O(1) + 后台 WorkerLoop） | ✅ |
| 三记录类（SeamTrack / WeldParamAdjust / WeldResult）+ `ProductFileRecordManager` 订阅三事件 | ✅ |
| 删除 `RunRecordManager.cs`（1046 行单文件）；消费方切换 `ProductFileRecordManager.Instance` | ✅ |
| 游离文件吸收（RecordFileStore/RecordFrame → SeamTrackRecord.cs；WeldActionRecord → WeldParamAdjustRecord.cs）（2026-09-20 起现役 `Records/RecordFileStore.cs` / `Records/LineLaserContourRecord.cs` / `Records/WeldParamControlRecord.cs`） | ✅ |
| `WeldParamAdjustRecord` 改名（类名/Item/Name 属性/类头注释）（现役 `WeldParamControlRecord`） | ✅ |
| SmartRay 链整删（Converter + AddSmartRayFrame 两处透传） | ✅ |
| 命名空间统一 `AdaWeldSystem.ProductFileControl`（ADR-005 登记例外） | ✅ |
| **真编译** | ⏳ 待 Visual Studio |

## 被推翻的中间态

- **ADR-008 归属目录决策已失效**：「迁移至 `Workflow/WeldActionRecord.cs`，命名空间 `AdaWeldSystem.Workflow`」——`Workflow/` 目录已解散，记录类经 `ProductFileManager/`（ADR-017 原文）迁至 `ProductFileControl/`；其 11 字段与双记录设计**仍有效**（⚠️ 字段数已被 [[decisions/ADR-052-ProductionRecordSchema]] 演进为 **20**，2026-10-08 审计补注）（已收拢至本页决策四）；
- **ADR-031 的 `RecordFileStore` 独立文件结论已被 ADR-031 推翻**：`RecordFileStore.cs` / `RecordFrame.cs` / `WeldActionRecord.cs` 独立成文件 → 并入对应实现类文件；`SmartRayConverter.cs` 由「保留」→ 整链删除（原 ADR-003 曾裁定保留，同被推翻）；
- **`RunRecordManager`（1046 行单文件）已删除**，旧名在历史 ADR 与日志中仍会出现，检索以本页与 [[modules/ProductFileManager]] 为准（drift REMOVED/RENAMED 表已登记）；
- **故障恢复消费方归口（原 ADR-017 §3）整体失效**：`FaultRecoveryManager` / `FaultCategory` / `FaultRecord` / `FaultRecordManager` 已于 2026-09-04 随故障恢复模块整体移除（ADR-008 D3），`ProductFileManager` ↔ `MainDeviceControl` 的枚举级循环依赖随之消失。

## 沿革

- **2026-07-15**：ADR-008 双记录设计（`.pDat` v2 + `.tmp` 崩溃恢复 + DataReview 红点）；
- **2026-08-31**：过程记录迁 `ProductFileManager/`（4 文件，公共 API 零变化）+ 故障记录 DB 下沉 SQLiteDatabase；**2026-09-01** 故障恢复业务消费方归口追加；
- **2026-09-14**：ADR-031 重构为 ProductRecordBase 抽象 + 三记录类 + Manager（删 RunRecordManager，订阅三事件闭环，WeldResultRecord 上数据库）；同日 ADR-031 文件自包含 + `WeldParamAdjustRecord` 改名 + SmartRay 链删除；
- **2026-09-14（ADR-005）**：命名空间统一 `AdaWeldSystem.ProductFileControl`，扁平目录登记为对齐例外；
- **2026-09-17 · 本页整合**：ADR-008/046/047 并入本页，删除被推翻的中间态表述，收拢全部现行裁定；整合后 status: accepted、tags 含 merged、`merged_from` 指向三个被并页。
- **2026-09-20 · 记录类职责拆分（用户裁定）**：`SeamTrackRecord`→`LineLaserContourRecord`（线激光轮廓记录**只保存点云**，不再承担过程帧快照与调整动作）；`WeldParamAdjustRecord`→`WeldParamControlRecord`（工艺控制记录类承接**过程帧 `RecordProcessFrame` + 调整动作 `RecordAdjustment`**，item 按 `AdjustExecuted` 分派）；`SeamTrackItem`→`ContourFrameItem`（仅点云）；`RecordFileStore`/`RecordFrame` 恢复独立 `Records/RecordFileStore.cs`（Manager 回溯转发直连 Store）；Manager 会话同步启停两类记录。本页 §实现类表中 `SeamTrackRecord`/`WeldParamAdjustRecord` 行为历史描述，现役以 `LineLaserContourRecord`/`WeldParamControlRecord` 为准。
- **2026-09-20 · 生产记录生命周期（新增 [[decisions/ADR-037-ProductProductionRecordLifecycle]]）**：`WeldResultRecord` 由「成功/产品信息记录」升格为**产品生产生命周期控制单位**（产品码 SN / 起焊时间 / 状态 模拟·正常生产 / 结果 pass·fail / 异常原因，**焊毕一次性落库**，不再记录焊接接头形式）；新增生产会话（`BeginProductSession`/`EndProductSession`）与**会话基名**三份记录文件对齐；`WeldParamControlRecord` 增第三类动作 **JobSwitch**（线激光分析工具切换，`.pDat` 动作格式升 v3 加 `JobId`），⛔ 不写入轮廓记录。本页 §二 表中 `WeldResultRecord` 行的落库字段为历史描述，现役以 ADR-037 决 1 的 5 列契约（`SN/Time/Status/Result/Info`）为准。

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- 模块：[[modules/ProductFileManager]] · [[modules/SQLiteDatabase]] · [[modules/PointCloudData]]
- 上游：[[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]（记录职责隔离/三事件，原 ADR-033）· [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] · [[decisions/ADR-017-SafetyCheckConsolidation]]（FaultCategory/FaultRecord 历史归属，已随模块移除失效）
- 范式：[[decisions/ADR-006-ModuleOrganizationPatternStandard]] · [[decisions/ADR-005-NamespaceDirectoryAlignment]]
- 教训：[[lessons/AlgorithmControlRecordIsolation]] · [[lessons/FaultRecoveryDeviceKey]]（历史）· [[guides/Config-Data-Tools]] · [[guides/Project-Tools]] §1.2
- 已并入本页（纯文本存档）：ADR-008-WeldActionRecord · ADR-031-ProductRecordModuleRefactor · ADR-031-RecordImplementationSelfContained
