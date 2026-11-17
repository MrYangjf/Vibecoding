---
title: "ADR-043 焊缝参数控制综合（使用场景 · 模拟环境 · 算法实现 · 数据库关联 · 实现路径 · 接入点；整合原 031/032/056/059/061/067）"
date: 2026-09-23
updated: 2026-10-30
tags: [ADR, 焊接参数, 工艺参数, 查表, 光斑宽度, XL缓存, 数据库, AutoParam, WeldParamControl, merged]
status: accepted
merged_from: [ADR-031, ADR-032, ADR-056, ADR-059, ADR-061, ADR-067]
---

# ADR-043 焊缝参数控制综合（使用场景 · 模拟环境 · 算法实现 · 数据库关联 · 实现路径 · 接入点）

> 本页为焊接参数控制主题的**唯一现行决策页**（2026-09-23 精简合并），收拢原 031/032/056/059/061/067 共 6 页（重排前编号，见 [[decisions/ADR-Index]] 删除对照表）的全部现行裁定。
> 「旧ADR-0XX」均指 **2026-09-23 重排前编号**。焊缝跟踪（CSP / 闭环 / 出图）不在本页，见 [[decisions/ADR-042-SeamTrackingConsolidated]]。

## 一、实际使用场景（业主口径，权威）

- **生产时按焊缝宽度实时输出工艺参数**（查表输出四组工艺曲线 + 光斑宽度），经 XL 缓存在机器人到达后按固定频率下发。
- **两套数据**（ADR-043 业主原始设计）：
 1. **配置记录**（面板新增配置 / 查看历史配置）——记录**参数基准**；
 2. **工艺参数查表模型**（输入焊缝宽度 → 输出参数）。
- **创立流程**：先建立配置 → 基准公式算得基准表格 → 配置与表格各存各表 → **实际生产只与分段表有关**。基准参数不够准确适配，需**分段逐档手工修改——这正是表存在的意义**。
- **切换 / 修正**：查找配置定位参数表；第一次创建用基准建表；**修正基准 = 表格恢复默认**（重算工艺库）。
- **宽度来源二选一**（`SEAM_WIDTH_SOURCE`）：`Manual`（默认，固定 1.2mm）/ `Laser`（线激光实测滑动平均）。
- **输出频率**：60 / 30 / 10 Hz 下拉选项（默认 60，禁手填——手填误值会引发线程扫描灾难）。
- **光斑宽度** = 焊缝宽度 × `SPOT_WIDTH_GAIN`(W，默认 1.0)，随查表输出（**暂不下发机器人**，协议串 `P/S/V/G` 不变，占位供后续振镜摆幅控制）。
- 无机器人通讯时输出链路自降级为**仅记录**；工艺控制**不单独开流程**，编排归 `WeldParamControlWorkflow`。

## 二、模拟测试环境

- **零新增代码触发**：模拟态复用同一条链路——SimTick 推进机器人 X + 虚拟相机产帧触发计算入缓存 + StepIdle `TickXlOutput` 按拍输出（模拟红线：不下发真实机器人，只更新 `LastOutput` 供观测与记录）。
- **管控窗口起点 = 播种后**（ADR-043 业主时序澄清）：PreWork 起点 = **预焊接点**，Start（连续）= **真正焊接起点**；焊接参数管控和记录从**下发参数后进入 start** 才开始工作。
 - 点击模拟测试 → `ResetSeamTracking("模拟启动重置")` 全清（宽度显示 0 = 未开始，正确状态）；
 - 焊前检查步 `DoSubPrework()` → 播种（宽度 1.2）；
 - start（`DoSubWork`）后恒 1.2，**全程无 1.2→0→1.2 闪断**。
- 模拟状态机步号 **10/20/21/22/30** 与真实 `IoSubPrework → IoSubWork` 同构（21 门开 → 22 播种 → 30 start）。

## 三、算法实现（ADR-031 分层架构 + 后续演进）

### 3.1 分层结构（现行）

```
WeldParamControl/
├── WeldParamData.cs 数据类集合（记录事件载荷等）
├── WeldParamManager.cs 单例 · 唯一外部入口（配置 + 全部算法 + 记录事件透传）
├── WeldAlgorithmsConfig.cs 焊接算法配置（43 项，Manager 独占）
├── Abstractions/WeldAlgorithmBase.cs 抽象基类：Name / IsReady / LoadConfig(object) / Reset()
└── Algorithms/
 ├── SeamGuideSample.cs 算法私有输入结构
 ├── WeldParamLookupAlgorithm.cs 实现 a：参数查表（公式 + 三张表 + 光斑列）
 ├── WeldParamAdjustmentAlgorithm.cs 实现 b：宽度驱动参数调整 + XL 缓存（工艺控制唯一载体）
 ├── SeamTrackingAlgorithm.cs 实现 c：PVT 流式段跟踪（备用，见 ADR-042 §5.4）
 └── SeamMapTrackingAlgorithm.cs 实现 d：CSP 焊缝跟踪（见 ADR-042）
```

- 实现类全部**非单例**；`WeldProcess` / `WeldDataManager` / `SeamTrajectoryBuilder` 已删除。
- **Manager 唯一入口**：持有全部算法实现、统一配置持久化（`CurrentAutoParamId` / `ConfigHelper` / `AutoParamHelper` / `SwitchConfig` / `AddConfig`）、代理算法公共入口；⛔ 外部不得绕过 Manager 访问算法或订阅算法事件（记录事件由 Manager 显式 add/remove 透传）；⛔ 不得向 Manager 或算法加流程编排逻辑。
- **`TriggerAdjustment()` 必须无参**（ADR-043：工作流是调整唯一主驱动）；运行参数从 Config 内部读取。

### 3.2 算法纯净性红线

- ⛔ 算法实现类内不得出现 `RunRecordManager` / `System.IO` / `File.` / `StreamWriter` / `XmlSerializer` 等任何记录持久化符号——**算法只计算，不落盘不记录**；不得在计算路径上同步落盘（保存可能耗时，但不能影响功能实现）。
- **留痕只触发事件**：`FrameRecordRequested`（每帧，7 项过程快照）/ `AdjustmentRecordRequested`（调整成功，契约独立演进）/ `AbortRecordRequested`（连续失败超限）；订阅方（ProductFileControl）**只做 O(1) 入队**，后台异步落盘；算法不感知记录侧状态。
- ⛔ 算法只读消费配置（私有 `_config` + `LoadConfig(object)`）；控制器写入职责归运控工作流。

### 3.3 两个核心算法

**WeldParamAdjustmentAlgorithm（调整 + XL 缓存一体，工艺控制唯一载体）**

- **Laser 源**：宽度滑动平均 → 突变判定 → 查表 → 输出工艺参数 + 图表 + 事件；`ExecuteAdjustment` 末尾喂入 XL 缓存（**仅 Laser 源**——Manual 每拍直查表，缓存无消费方）。
- **Manual 源**：绕过滑动平均与突变判定，以 `ManualSeamWidthMm` 直接查表——输出全程恒定，不依赖线激光帧喂入（`FeedLatestSeamWidth` 在 Manual 模式跳过，线激光序列不被固定值污染）；Manual 模式跳过调整留痕，过程帧留痕照常。
- XL 缓存为**私有嵌套类 `XLPoint`** 成员（独立实现类 `WeldParamXLCacheAlgorithm` 已并入删除）：键 = `RobotXL = 测量X + LeadDistanceMm`（与焊缝跟踪前置量入键同语义），X 单调化（回退吞抖动、同键覆盖、超限丢最旧）；`TryGetOutputAt(robotXNow)` 二分取已到达的最邻近 XL。
- `Reset()` **无条件清零**（含 Manual 宽度——复位只发生在会话边界窗口外，见 §二）；复位原因与宽度变化留痕（old→new 限频 1s + 起焊沿计数 `_seamTrackingStartCount`）。

**WeldParamLookupAlgorithm（查表）**

- 维护焊缝宽度查找表（三张工艺映射表）+ `SpotWidthDic`（光斑列）；`TryLookupWithSpot` 为现行消费口（`TryLookup` 原签名保留兼容）。
- `BuildLookupTable` 基准公式：**防呆**——`Sensitivity ≤ 0` 或范围倒置告警并直接返回（不再产出无声空表）。
- `RefreshSpotWidthDic`：宽度来源切换只刷光斑列，不重建整表。
- 基准公式**仅两处使用**：首建兜底、修正基准（恢复默认）。

## 四、当前算法与本地数据库如何关联（ADR-043）

### 4.1 存储结构

- SQLite（`SQLiteDBControl/` 三层：Core + ISQLiteHelper 基类 + Helpers + Manager 单例；禁外部 new Helper）；工艺库 `AutoParamValue.db`，经 `AutoParamHelper` 读写。
- **一配置一表一行不变式**：每个配置对应一张分段参数表，表内**一行**保存该配置当前生效参数。
- 分段表 **第 5 列「光斑宽度」**（`WeldAutoParamProfile.SpotWidthJson`）；旧表经 `EnsureSpotWidthColumn`（`ALTER TABLE ADD COLUMN`，重复补列静默忽略）**自动迁移**，旧行空值由读取侧公式（宽度 × W）现算兜底——无需人工迁移。

### 4.2 载入优先级（换轨后现行）

```
LoadCurrentConfig：基准兜底在前（首建 / 无表场景）→ DB 分段表覆盖在后（手工修正生效）
LoadAlgorithmsConfig（启动）：分段表优先回灌；仅 !IsReady 才基准公式重建
```

- 分段手工修正**重启 / 切换配置不再被基准冲掉**（修复前每次启动被 `BuildLookupTable` 整表重建覆盖）。
- `SaveProfile` 写入前清空旧行（清行 + 插入）；`UpdateProfile` 检测行数为 0 自动转插入（**空表首存自愈**，修复"新建参数库查不到数据 / 首存丢失"）；新增 `GetRowCount` / `ClearTableData`。
- `ReloadCurrentParamValues` = 修正基准恢复默认；`Manager.BuildLookupTable` 公共包装保留（0 消费 ≠ 删除）。

## 五、当前算法实现路径（数据源来入和出 + 计算公式）

### 5.1 来入

| 源 | 通路 |
|---|---|
| Manual 宽度 | `ManualSeamWidthMm`（默认 1.2）恒值直入 |
| Laser 宽度 | 线激光实测 → `FeedLatestSeamWidth()` 滑动平均序列（Manual 模式跳过喂入） |
| 机器人位姿 | `WeldParamManager.CurrentRobotX`（RSI 快照，测量 X 用于 XL 键） |
| 配置基准 | 面板配置记录 → 基准公式首建兜底 / 修正基准 |

### 5.2 计算公式

- 特征（Laser 源）：`宽度 → 滑动平均 → 突变判定`（连续失败超限 → `AbortRecordRequested`）。
- 查表：`TryLookupWithSpot(宽度) → (电流, 电压, 焊速, 摆频…) + 光斑 = 宽度 × W`（分段表逐档手工修正优先于基准公式）。
- XL 键：`RobotXL = 测量X + LeadDistanceMm`；输出查询：机器人到达 XL 后按 `TryGetOutputAt(当拍X)` 二分取最邻近已到达点。

### 5.3 出

- `WeldParamControlWorkflow.FlowProcess` StepIdle 内 `TickXlOutput()`（仅 `WeldStatus == Working`）：
 - **Manual 源**：每拍 `TriggerAdjustment()` + `FillOutput()`（固定宽度直查表，链路自驱）；
 - **Laser 源**：按当拍机器人 X 取已到达 XL 缓存 `FillXlOutput()`（无命中保持上一输出）；
 - 频率按 `PARAM_OUTPUT_HZ` 节流（`Environment.TickCount` 差值，对回绕免疫）。
- 下发统一 `SendToRobot`：无通讯自降级仅记录；模拟只更新 `LastOutput`。
- 留痕：过程帧逐帧事件（Manual 60Hz 留痕）；调整成功事件（Manual 跳过）；工艺调整记录并入生产记录生命周期（**Job 切换属调整的一种**、调整值与 RobotX 同帧对齐）。

## 六、算法接入点（内部流程如何调用消费）

| 接入点 | 说明 |
|---|---|
| **调整主驱动** | `LineLaserWorkflow.ExecuteStep_Adjust → RunAutoAdjust() → WeldParamManager.TriggerAdjustment()`（无参，唯一调用点）；手动模式在 Display 步直接跳 Complete **天然跳过调整**（仅分析+显示）；持续运行：Completed → Acquiring 立即开下一轮直至手动/信号停止 |
| **播种（焊前预置）** | `DoSubPrework()`（真实）/ `SimScheduleTick` 步 22（模拟）→ 焊前检查会话边界复位 → `WeldParamControlWorkflow.PreWork → TriggerAdjustment` 播种 = **管控窗口开启事件**；窗口内（播种→收尾）任何路径不得清工艺调整 |
| **输出支路** | `WeldParamControlWorkflow.StepIdle → TickXlOutput()`（60/30/10Hz）；`SendToRobot` 下发或降级记录 |
| **查询透传** | Manager：`TryGetParamOutputAt` / `ParamCacheCount` / `CurrentSeamWidth` / `CurrentRobotX` 等 |
| **配置读写** | `Manager.LoadAlgorithmsConfig()` / `SaveAlgorithmsConfig()` 无参方法对 + 只读属性 `AlgorithmsConfig`；`_algorithmsConfig` 一实例一次载入分发给各算法；外部禁 new / 回灌；`SEAM_GUIDE` / `WELD_PARAM_ADJUST` 节名与键不变 |
| **记录订阅** | 三事件经 Manager 透传，`ProductFileControl` 订阅异步落盘（生产只读分段表语义下，调整留痕仍是过程证据） |

## 沿革（被合并页演进链摘要）

- **ADR-043**（09-14，整合原 041/043/044）：删除 `WeldProcess` 单例 → 抽象基类 + 四实现 + Manager 唯一入口；算法去记录化（三处直接落盘改事件）；配置合一 `WeldAlgorithmsConfig`（当时 37 项，Manager 一实例一属性一对方法）。
- **ADR-043**（07-15）：`LineLaserWorkflow` 为调整唯一主驱动、`TriggerAdjustment` 无参、手动模式跳过调整（结论有效，目录/符号已迁移改名）。
- **ADR-043**（09-23）：宽度来源配置化（Manual 1.2 默认）+ 光斑宽度列 + XL 缓存输出（独立实现类同日并入调整算法删除）+ StepIdle 60Hz 支路。
- **ADR-043**（09-23）：趋近阈值根除（部分撤销 055）+ PVT 临时禁切 + 频率选项化 + 宽度来源 Select 零尺寸修复 + 面板补前馈安全系数/单调方向锁。
- **ADR-043**（09-23）：生产只读分段表——载入优先级换轨 + 空表首存自愈 + 切换只刷光斑列 + 基准防呆。
- **ADR-043**（09-23）：管控窗口起点 = 播种后——复位分层（会话边界全清 / 起焊沿只清跟踪）+ 模拟状态机补下发参数步 + `Reset()` 恢复无条件清零（撤销 066 Manual 不清零）。

## 背景

（待补：本决策要解决什么问题）

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 后果

### 正面
- （待补）

### 负面
- （待补）

## 相关页面

- 焊缝跟踪侧：[[decisions/ADR-042-SeamTrackingConsolidated]]
- 模块/API：[[modules/WeldParamControl]] · [[modules/ProductFileManager]] · [[modules/SQLiteDatabase]] · [[api/WeldParamManager]] · [[api/WeldParamAdjustmentAlgorithm]] · `WeldParamLookupAlgorithm`（查表实现，无独立 API 页） · [[api/WeldParamControlWorkflow]] · [[api/LineLaserWorkflow]] · [[api/SQLiteDatabaseManager]] · [[api/ProcessControlPage]]
- 记录/流程：[[decisions/ADR-031-ProductLifecycleRecordModule]] · [[decisions/ADR-037-ProductProductionRecordLifecycle]] · [[decisions/ADR-016-WorkflowResponsibilityBoundary]] · [[decisions/ADR-006-ModuleOrganizationPatternStandard]] · [[decisions/ADR-033-ConfigArchitectureStandard]] · [[decisions/ADR-041-ResidentFlowNonBlockingParadigm]]
- 教训：[[lessons/AlgorithmControlRecordIsolation]]
