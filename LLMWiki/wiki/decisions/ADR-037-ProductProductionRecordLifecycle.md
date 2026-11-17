---
title: ADR-037 产品生产记录生命周期（WeldResultRecord 为生命周期单位 · 会话基名对齐三份记录文件 · 调整含 Job 切换）
date: 2026-09-20
updated: 2026-10-30
tags: [决策, 产品记录, 生产记录, 生命周期, 数据回溯, SQLite, 线激光Job, 调整记录, ADR-031, ADR-043, ADR-027]
status: accepted
---

# ADR-037 产品生产记录生命周期（生产记录 = 回溯入口）

> **闭合关系**：本 ADR 是 [[decisions/ADR-031-ProductLifecycleRecordModule]]（产品记录模块归口与四类记录）在 **「产品生产生命周期」语义**上的补齐：ADR-031 规定「哪些记录类归口 ProductFileControl」，本 ADR 进一步规定**「一次产品生产从起焊到焊毕的完整证据链如何组织、如何按产品码回查」**——即 `WeldResultRecord` 从「结果记录」升格为**生命周期控制单位**，与三份过程记录文件（`.ply`/`.pDat`/`.csv`）按**会话基名**对齐。
>
> 与 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]（算法纯净性：调整只发事件不留痕）与 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（CSP 每拍输出）配套：本 ADR 规定这两条链路产出的数据**如何被一条生产记录串联起来**。

## 背景

2026-09-20 用户提出两点回顾性诉求，暴露出记录链「有数据、无索引」的结构性缺口：

1. **生产记录本身不被填**：`WeldResultRecord` 的 `RecordWeldResult` 全库 0 调用，产品库（`Product.db` 按日期分表）**永远是空表**；而产品库本该承担「生产记录清单」的角色——回溯端（`DataReviewerPage`）此前的表格数据源却是**记录目录里的 .pDat 文件列表**（`GetWeldActionRecordFiles`），与产品库脱节，等于「有文件、无生产记录」。
2. **三份记录文件无法按生产记录定位**：一次生产会话会产出 `.ply`（线激光轮廓）/ `.pDat`（工艺控制）/ `.csv`（轨迹）三份文件，但三者的命名各自为政（`Record_时间戳`、`Trajectory_时间戳`），**没有任何字段能把它们与产品库里的一条生产记录关联起来**，回溯端只能按文件名猜测。
3. **调整记录缺少 Job 切换与 X 对齐**：线激光分析工具（Job）的切换**在语义上属于工艺调整的一种**（换了分析工具即换了标定与算法参数），但切换事实此前完全未入档；同时调整值虽已记录，但用户明确要求「与线激光引导 Y 一样，必须同时记录 X，保证调整是按机器人的 X 对齐的」。

## 决策

### 决 1 — `WeldResultRecord` 是产品生产的**生命周期控制单位**

一次「起焊 → 焊毕」= 一条 `WeldResultRecord`，字段契约固定为 **5 列**（落产品库按日期分表 `TyyyyMMdd`）：

| 列 | 含义 | 说明 |
|---|---|---|
| `SN` | 产品码 | 由机器人传输指令下发；**空缺时以 `TEST` 占位**（会话基名同为 TEST） |
| `Time` | 开始时间 | 起焊时刻，落库格式 `yyyyMMddHHmmss`（= 回溯端推算会话基名的键） |
| `Status` | 记录状态 | **模拟 / 正常生产**（二值，由是否模拟会话决定） |
| `Result` | 结果 | 正常焊接完成为 `pass`，异常焊接为 `fail` |
| `Info` | 异常原因 | `Result=fail` 时填写；若会话曾因连续失败超限异常中止，以中止原因补位 |

**⛔ 不再记录焊接接头形式**（原 `InspectionType` 列删除）：该信息不属于生命周期控制单位的语义范围，另外记录。表格列契约由 `ProductDatabaseHelper._productColumns` 单一持有，并在 `EnsureTableSchema` 中校验——**当天表列集与现行契约不符时重建**（仅当天表；历史日期表原样保留，不做破坏性重建）。

### 决 2 — 写入时机：**焊毕一次性写入**（起焊缓存）

- 起焊（`BeginProductSession`）：缓存 `SN` / 起焊时间 / `Status` / 会话基名，并同步开启记录与轨迹会话。
- 焊毕（`EndProductSession`）：结束并归档三份记录文件，然后把一条生产记录**一次性落库**。
- 理由：起焊时 `Result` 未知；若起焊先写一行、焊毕再 update，会引入「表里存在半成品行」的中间态，回查端需额外过滤。

**结果判定入口**（`DeviceControlWork`）：

| 触发 | Result | Info |
|---|---|---|
| `DoSubStop`（子设备停止流程）/ `DoSubManualStop`（手动停止） | `pass` | — |
| `DoSubAlarmStop`（子设备报警停止） | `fail` | 子设备报警停止 |
| 记录会话异常中止（`AbortRecordRequested` 连续失败超限） | `fail`（覆盖调用方传入值） | 记录会话异常中止原因 |

### 决 3 — **会话基名**是三份记录文件与生产记录的**唯一关联键**

```
会话基名 = [模拟]产品码_yyyyMMdd_HHmmss
 ↑ 模拟会话加前缀 ↑ 起焊时间（= 生产记录 Time 列）
```

- 三份记录文件**同名、扩展名区分**：`<基名>.ply` / `<基名>.pDat` / `<基名>.csv`。
- ~~同落 `Records\yyyyMMdd\`。~~ ⚠️ **已演进（2026-09-21）**：一次会话的三份文件归入**以基名（含时间戳）命名的会话子文件夹** `Records\yyyyMMdd\<基名>\`，文件仍为 `<基名>.ply/.pDat/.csv`。回溯 `GetSessionRecordFiles` 优先查子文件夹，缺则回退旧平铺路径（兼容历史数据）；新增 `Settings/RetentionDays`（默认 30，0=永久），启动与配置保存时按文件夹创建时间自动清理过期会话文件夹。
- 回溯端由生产记录的 `Time` + `SN` + `Status` **纯推算**出三份文件路径（`GetSessionRecordFiles`），无需任何额外索引文件。
- 推论：`Time` 列必须落**到秒**且与文件名的 `yyyyMMdd_HHmmss` 同源，否则关联断裂。

### 决 4 — 回溯端：表格 = 生产记录清单，**一次性读三份文件绘图**

`DataReviewerPage` 的两条硬约束：

1. **表格数据源 = 产品库当日分表**（`SelectProductRecords(date)`），**不是**记录目录的文件列表；表格列 = `No. / 产品码 / 起焊时间 / 状态 / 结果 / 异常原因`。
 - **不轮询**：仅日历切日或点「加载」时一次性读取当日全部生产记录，分页只做内存切片，不重新查询。
2. **选中行 → 一次性读该会话的三份记录文件**，统一以**机器人 X 轴为横轴**绘图，系列**均可选显示**：

| 系列 | 数据来源 | 说明 |
|---|---|---|
| 焊缝宽度 | `.pDat` 过程帧 `WeldWidth` | 线激光分析结果 |
| 送丝速度 | `.pDat` 过程帧 `FeedSpeed` | **工艺查表输出值** |
| 激光功率 | `.pDat` 过程帧 `LaserPower` | **工艺查表输出值** |
| 机器人运动速度 | `.pDat` 过程帧 `RobotSpeed` | |
| 调整动作点 | `.pDat` 调整动作（`AdjustExecuted=true`） | **含参数调整与 Job 切换**，纵轴取调整时刻焊缝宽度，固定红色 |
| CSP 运动 Y 轴值 | `.csv` 轨迹 `CspY` | 每拍下发目标 |
| 机器人 Y 轴 | `.csv` 轨迹 `RobotY` | |

### 决 5 — **Job 切换属调整的一种**，落工艺控制记录（`.pDat`），**不落线激光轮廓记录**

- 动作类型扩为三类：`ProcessFrame`（过程帧）/ `WeldParamAdjust`（参数调整）/ **`JobSwitch`（分析工具切换）**。
- `.pDat` 二进制动作记录格式版本 **3**（新增 `JobId` 列，13 列文本格式同步），历史版本按版本号兼容读取（`JobId=0`）。
- ⛔ **Job 切换不写入 `.ply` 线激光轮廓记录**，也不写入 `.csv` 轨迹记录——轮廓记录只存线激光相关数据（ADR-031 沿革）。
- **入档范围收窄**：只记录**焊接过程中**（线激光子流程处于 `Working`）的切换；调试期在 `ILCamPage` 上的切换不入档，避免污染生产记录。
- **切换的唯一入口是 `LineLaserManager.SwitchJob`**（含 `JobChanged` 事件）；UI 调试界面与机器人指令都必须经此入口，方可自动入档。

> **遗留（协议缺口）**：机器人指令表中尚无「Job 切换」指令常量（`CommandCore` 现 18 条指令无此项）。本期处理 = **预留指令位 + 修通记录端**：`DeviceControlWork.OnLineLaserJobChanged` 已就位并留 `// todo`，待协议细化后在指令分发处调用 `LineLaserManager.SwitchJob` 即自动入档，记录端无需再改。

### 决 6 — 调整值必须**携带 RobotX**

- 所有调整记录（参数调整、Job 切换）与线激光引导 Y 一样，与**机器人 X 同帧落盘**，保证「这条调整发生在焊缝的哪个位置」可判定。
- ~~对应的轨迹 CSV 同步扩为 7 列：`RobotX_mm, RobotY_mm, CspY_mm, FeedSpeed, RobotSpeed, LaserPower, SeamWidth`。~~ ⚠️ **已废止（2026-09-20 实测反馈，同日经 ADR-037 演进）**：工艺调整快照（送丝速度 / 机器人速度 / 激光功率 / 焊缝宽度）由 `.pDat`（`WeldParamControlRecord`）独占记录已久，轨迹 `.csv` 无需重复承载；现回落为 **3 列** `RobotX_mm,RobotY_mm,CspY_mm`，列序与 `TrajectoryRecord.RecordPoint` 写入、`ParseFile` 解析三方一致。去重：CSP 拍快于机器人 X 采样时，`TrajectoryRecord` 对**连续相同 robotX（容差 1e-6）仅保留末行**，避免回溯折线在 Y 轴跳变（见 [[modules/ProductFileManager]] / [[api/ProductFileRecordManager]]）。
- 推论：仿真态**机器人 X 必须有真实来源**（模拟时钟），否则调整点全部堆在 X=0；机器人 Y 由 `WeldParamManager.CurrentRobotY` 在机器人数据回调中同步（模拟态复用同一载体）。
- CSP 每拍记录（`OutputCspTick`）**取消模拟门禁**：真实链路与模拟链路一样逐拍入档，否则真实生产无法回溯 CSP/机器人 Y 曲线。

## 备选方案

| 决策点 | 方案 | 结论 |
|---|---|---|
| SN 来源 | 机器人指令下发 / 空缺以 `TEST` + 时间后缀 | **同时支持**：有则用，无则 `TEST` 占位（不阻塞模拟与调试） |
| DB 写入时机 | 起焊写 + 焊毕更新 / 焊毕一次性写 | **焊毕一次性写**（无中间态，回查简单） |
| 文件与记录的对齐方式 | 额外索引文件 / **会话基名约定** | **会话基名**（零额外文件，可由生产记录纯推算） |
| 回溯表格数据源 | 记录目录文件列表 / **产品库生产记录** | **产品库生产记录**（文件列表无法表达 pass/fail 与 SN） |
| Job 切换落哪份记录 | 线激光轮廓记录 / **工艺控制记录** | **工艺控制记录**（切换是工艺调整的一种，非轮廓数据） |

## 后果

### 正面
- 产品库不再空表：一次生产 = 一行记录，`pass`/`fail` 与 SN 可查。
- 三份记录文件与生产记录**零额外索引**对齐，回溯端从「猜文件名」变为「按记录推算」。
- 调整（含 Job 切换）可按机器人 X 定位，工艺调整的地点与效果可对准同一横轴复盘。
- `Result=fail` 时 `Info` 强制有原因（报警停止 / 连续失败超限），异常可归因。

### 负面 / 注意
- **`Time` 列精度成为硬约束**：起焊时间必须落到秒，且与文件名同源。
- 历史数据不迁移：旧表列集不符时**仅当天表**重建，历史日期表保留（列集不同，回查端需容忍缺列——读取侧已按列名安全取值）。
- 会话未开启就停机（如未走起焊指令直接停机）时 `EndProductSession` 幂等跳过，不写记录。
- 真编译需在 Visual Studio 验证（本环境治理无 C# 编译器，仅做静态校验）。

### 实现红线（2026-09-20 修复，回溯表格与归档缺失的根因）

- **结果记录随生产会话启停（否则表格永远空表）**：`WeldResultRecord` 继承 `ProductRecordBase`，`Enqueue` 在非 `IsRecording` 态静默丢弃；`BeginProductSession` 必须调 `_resultRecord.Start()`、`EndProductSession` 在 `RecordWeldResult` 之后调 `_resultRecord.Stop()` 排空落库。漏掉则产品库按日期分表恒为空、回溯表格无记录（含模拟）。
- **归档顺序红线（否则 `.pDat` ActionCount 恒 0）**：`StopRecording` 必须先 `_adjustRecord.Stop()` 排空工艺控制（PDA/调整）队列，再 `_contourRecord.Stop()` 关闭共享 `RecordFileStore` 会话；反之 `AddRecord` 因 `_isSessionOpen=false` 丢弃全部动作记录。
- **轮廓 X 对齐机器人 X**：`LineLaserManager.OnCameraProfileReady` 传 `GetEffectiveRobotX()`（模拟态为模拟机器人 X）给 `AddFrame`，`RecordFileStore` 落盘时按该值偏移点云 X，使 `.ply` 轮廓沿机器人行走轴对齐（ADR-027 横轴统一）。
- **模拟轨迹记录依赖运动工作流跑通 `UpdateSeamTracking`**：`MotionControlWorkflow.FlowProcess` 模拟态放开 `IsEnable` 门禁（真实态保留），否则模拟无运控时 `FlowProcess` 早退、`UpdateSeamTracking` 不执行、轨迹 CSV 仅表头（无运控仍记录见 ADR-032 原裁定）。

## 关键约束

- 归口 [[decisions/ADR-031-ProductLifecycleRecordModule]]：记录类与 Store 仅由 `ProductFileRecordManager` 独占持有，外部不得绕过 Manager（含回溯读取）。
- 算法纯净 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]：Job 切换与参数调整只**发事件**，落盘在 Manager 侧；算法不落盘、不构造格式化字符串。
- 步骤驱动 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]：CSP 每拍记录在工站节拍内写入，不自起线程。
- 模拟红线 [[decisions/ADR-032-SimulationTestRedesign]]：模拟与真实统一走同一套记录链，仅文件名加「模拟」前缀、`Status` 记「模拟」。
- 配置与持久化走 `FileOperate`（ADR-033），不私设路径。

> ⚠️ **演进（2026-09-20，同日经实测反馈）**：决 6 中「轨迹 CSV 扩 7 列（含工艺调整快照）」条款已废止——工艺调整快照（送丝速度 / 机器人速度 / 激光功率 / 焊缝宽度）由 `.pDat`（`WeldParamControlRecord`）独占记录，轨迹 CSV 回落 **3 列**（RobotX / RobotY / CspY），且对连续相同 robotX 去重；其余条款（调整值携带 RobotX、机器人 X/Y 真实来源、CSP 每拍取消模拟门禁）仍然有效。详见 [[modules/ProductFileManager]] / [[api/ProductFileRecordManager]]。

## 相关页面
- [[decisions/ADR-031-ProductLifecycleRecordModule]] — 产品记录模块归口与记录类自包含（本 ADR 的上位页）
- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] — 算法纯净性：调整只发事件
- [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — CSP 每拍输出与步骤驱动
- [[decisions/ADR-032-SimulationTestRedesign]] — 模拟与真实统一记录链
- [[modules/ProductFileManager]] — 模块目录与四类记录职责
- [[api/ProductFileRecordManager]] — 生产会话 / 回溯 / Job 切换记录的全部入口
- [[api/SQLiteDatabaseManager]] — 产品库列契约与按日期分表
- [[modules/UIDesign]] — `DataReviewerPage` 回溯端（表格 = 生产记录、六系列绘图）
- [[api/DeviceControlWork]] — 生产会话的起止触发点（起焊 / 停止 / 报警）
- [[api/LineLaserManager]] — `SwitchJob` 与 `JobChanged`（Job 切换唯一入口）
