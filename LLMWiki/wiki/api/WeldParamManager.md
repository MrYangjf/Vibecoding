---
title: WeldParamManager API 参考（焊接参数管理器 · 模块唯一入口）
date: 2026-09-14
updated: 2026-09-14
tags: [API, 焊接, 参数, 算法, 管理器, 单例, 唯一入口, 配置合一, ADR-041, ADR-043, ADR-044]
source: AdaWeldSystem/WeldParamControl/WeldParamManager.cs
---

# WeldParamManager API 参考

> WeldParamControl 模块**唯一外部访问入口**（单例）：集中持有焊接参数配置、全部算法实现与配置持久化。
> **位置**：`AdaWeldSystem/WeldParamControl/WeldParamManager.cs`
> **命名空间**：`AdaWeldSystem.WeldParamControl`
> **取代**：~~`WeldProcess`~~（单例，2026-09-14 ADR-041 删除）、~~`WeldDataManager`~~（同日并入本类）
> 模块背景见 [[modules/WeldParamControl]]，决策依据见 [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]]。

---

## 定位

```
外部（WeldParamControlWorkflow / MotionControlWorkflow / AutoParamForm / ConfigForm / ParamConfigPage / LineLaserWorkflow）
  ↓ 只认 WeldParamManager.Instance
WeldParamManager（配置 + 算法实现持有者 + 配置持久化）
  ├─ WeldParamLookupAlgorithm      （非单例）参数查表调整
  ├─ WeldParamAdjustmentAlgorithm  （非单例）焊缝宽度驱动的参数调整
  └─ SeamTrackingAlgorithm         （非单例）线激光焊缝几何轨迹跟踪
```

- **单例**（`Lazy<T>`，线程安全），构造时创建三个算法实现，并初始化配置持久化。
- **不承载流程**：参数调整编排在 [[api/WeldParamControlWorkflow]]，轨迹点写入在 [[api/MotionControlWorkflow]]。
- ⛔ 外部不得绕过 Manager 直接访问算法实现实例。

---

## 公共成员

### 配置与持久化

| 成员 | 类型 | 说明 |
|---|---|---|
| `CurrentAutoParam` | `AutoParam` | 当前自动参数配置（null 时无法计算） |
| `ConfigHelper` | `ConfigHelper` | 自动调整参数配置管理器（基础配置与 JSON 映射） |
| `AutoParamHelper` | `AutoParamHelper` | 自动调整参数值管理器（分段数据表） |
| `CurrentAutoParamId` | `string` | 当前配置标识（INI 持久化，private setter） |
| `IsCountType` | `bool` | 是否按点数分段计算（透传 `AlgorithmsConfig`，默认 `true`） |
| `CountNum` | `int` | 每段点数（透传 `AlgorithmsConfig`，默认 `5`） |
| `CurrentRobotX` | `double` | 机器人 X 坐标（读写；内部即 `RobotWeldData.PosX`，当前恒为 0，见遗留项） |
| `RobotWeldData` | `RobotWeldData` | 机器人焊接数据（只读引用） |
| `AlgorithmsConfig` | `WeldAlgorithmsConfig` | **焊接算法配置（只读引用，Manager 独占实例，两节合一）**：线激光引导（`SEAM_GUIDE`）+ 参数调整（`WELD_PARAM_ADJUST`），运行期只读 ★ADR-044（取代原 `SeamGuideConfig` / `AdjustmentConfig` 两属性） |

### 输出（透传 `WeldParamAdjustmentAlgorithm`）

| 成员 | 类型 | 说明 |
|---|---|---|
| `LaserPowerOutput` | `double` | 激光功率输出（最近一次调整结果） |
| `FeedSpeedOutput` | `double` | 送丝速度输出 |
| `RobotSpeedOutput` | `double` | 焊接速度输出 |
| `CurrentSeamWidth` | `double` | 本轮采用的焊缝宽度（平滑后） |
| `ConsecutiveFailureCount` | `int` | 连续失败计数（只读） |
| `MaxConsecutiveFailures` | `int` | 最大允许连续失败次数（读写，默认 5） |
| `TotalExecuteCount` | `int` | 算法执行总次数（只读） |

### 查找表（透传 `WeldParamLookupAlgorithm`）

| 成员 | 类型 | 说明 |
|---|---|---|
| `SeamWidthList` | `List<double>` | 焊缝宽度列表（查找表键） |
| `LaserPowerDic` | `Dictionary<double,double>` | 焊缝宽度 → 激光功率 |
| `FeedSpeedDic` | `Dictionary<double,double>` | 焊缝宽度 → 送丝速度 |
| `RobotSpeedDic` | `Dictionary<double,double>` | 焊缝宽度 → 焊接速度 |

### 折线图数据（透传 `WeldParamAdjustmentAlgorithm`，只读）

`ContourChart` / `LaserPowerChart` / `FeedSpeedChart` / `SeamWidthChart` / `RobotSpeedChart`（均 `ChartVar`，基于 RobotX 坐标）。

### 事件

| 成员 | 说明 |
|---|---|
| `WeldProcessCompleted` | 焊接工艺调整完成事件（`EventHandler<WeldProcessCompletedEventArgs>`），显式 `add`/`remove` 透传参数调整算法 |
| `FrameRecordRequested` | **过程帧记录请求**（`EventHandler<WeldFrameRecordEventArgs>`），透传参数调整算法；落盘由记录模块异步执行（ADR-043） |
| `AdjustmentRecordRequested` | **调整动作记录请求**（`EventHandler<WeldAdjustmentRecordEventArgs>`），同上 |
| `AbortRecordRequested` | **记录中断请求**（`EventHandler`，无载荷），同上 |

> ⛔ 外部不得绕过本管理器直取算法实例订阅这些事件（[[standards/ModuleOrganizationPattern]] H6）。
> 记录订阅方由 [[modules/ProductFileManager]] 承担，**当前为 TODO**（见该模块页）。

### 配置管理方法

| 方法 | 签名 | 说明 |
|---|---|---|
| `SwitchConfig` | `void (string configId)` | 切换到指定配置 |
| `AddConfig` | `AutoParam (string configId)` | 新增配置并切换 |
| `DeleteConfig` | `bool (string configId)` | 删除非默认/非当前配置 |
| `SaveCurrentAutoParam` | `void ()` | 保存当前 AutoParam 到 ConfigHelper |
| `SaveCurrentProfile` | `void ()` | 保存当前分段参数到 SQLite |
| `ReloadCurrentParamValues` | `void ()` | 重新载入当前配置并重建查找表 |
| `LoadProfileIntoLookupTable` | `void (string identityInfo)` | 从 SQLite 读分段数据写入查找表 |
| `LoadAlgorithmsConfig` | `void ()` | **无参**：从自有 `Config/XML/WeldParamControl.xml` 载入 `SEAM_GUIDE` + `WELD_PARAM_ADJUST` 两节，并把同一个实例分发给两个算法（构造时自动调用一次）★ADR-044 |
| `SaveAlgorithmsConfig` | `void ()` | **无参**：把当前焊接算法配置两节一并写回自有配置文件，末尾 `SaveXdocument()` 落盘 ★ADR-044 |

> **配置由本管理器独占**（ADR-041 第三次修订 + ADR-043 + ADR-044）：唯一实例由 `AlgorithmsConfig` 只读属性暴露
> （类型 `WeldAlgorithmsConfig`，**两节合一**），持久化共用**同一个**读写器与文件 `Config/XML/WeldParamControl.xml`（`SEAM_GUIDE` + `WELD_PARAM_ADJUST` 两节并存）。
> ⛔ 外部不得 `new WeldAlgorithmsConfig()`、不得持有或回灌实例；原 `LoadSeamGuideConfig(SeamGuideConfig)` 重载、`WeldParamControlWorkflow.SeamGuide` 属性与 `SaveSeamGuide()` 方法均已删除。
> ~~`SeamGuideConfig`~~ / ~~`WeldParamAdjustmentConfig`~~ 两类与 ~~`LoadAdjustmentConfig`~~ / ~~`SaveAdjustmentConfig`~~ / ~~`LoadSeamGuideConfig`~~ / ~~`SaveSeamGuideConfig`~~ 四方法于 2026-09-14 合并为上述一对（ADR-044）。

### 算法方法

| 方法 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static WeldParamManager` | `Lazy<T>` 单例 |
| `TriggerAdjustment` | `void ()` | **无参**触发一次参数调整（ADR-009）；分段与阈值取自 `AlgorithmsConfig`，不再作为形参传递（ADR-043） |
| `BuildLookupTable` | `void (AutoParam)` | 生成查找表 |
| `TryLookup` | `bool (double, out double, out double, out double)` | 按焊缝宽度匹配参数 |
| `Reset` | `void ()` | 复位全部算法状态 |
| `FeedSeamTracking` | `PVTPoint[] (LineLaserSeamResult, double measuredFps, double axisCurrentPos)` | 喂入一帧线激光结果，返回 PVT 点数组 |
| `TickSeamTracking` | `PVTPoint[] ()` | 按最长间隔强制输出 PVT 点 |
| `DrainSeamTracking` | `PVTPoint[] ()` | 排空轨迹算法剩余点 |
| `ResetSeamTracking` | `void ()` | 复位轨迹跟踪算法 |

### 轨迹跟踪可观测性

| 成员 | 类型 | 说明 |
|---|---|---|
| `SeamTrackingHasFault` | `bool` | 轨迹算法是否报警 |
| `SeamTrackingFaultReason` | `string` | 报警原因 |
| `SeamTrackingLastDeviation` | `double` | 最近一次偏差 |
| `SeamTrackingLastTargetPos` | `double` | 最近一次目标位置 |

---

## 调用方与迁移对照

| 调用方 | 原调用 | 现调用 |
|---|---|---|
| `WeldParamControlWorkflow` | `WeldProcess.Instance.TriggerAdjustment()` | `WeldParamManager.Instance.TriggerAdjustment()` |
| `WeldParamControlWorkflow` | `WeldProcess.Instance.{LaserPowerOutput, FeedSpeedOutput, RobotSpeedOutput, CurrentSeamWidth, CurrentRobotX}` | `WeldParamManager.Instance.*` |
| `LineLaserWorkflow` | `WeldProcess.Instance.CurrentRobotX` | `WeldParamManager.Instance.CurrentRobotX` |
| `AutoParamForm` | `WeldProcess.Instance.{SeamWidthList, RobotSpeedDic, FeedSpeedDic, LaserPowerDic}` | `WeldParamManager.Instance.*` |
| `AutoParamForm` | `WeldDataManager.Instance.LoadProfileIntoLookupTable(...)` | `WeldParamManager.Instance.LoadProfileIntoLookupTable(...)` |
| `AutoParamForm` | `WeldDataManager.Instance.SaveCurrentProfile()` | `WeldParamManager.Instance.SaveCurrentProfile()` |
| `ConfigForm` | `WeldDataManager.Instance.mConfigManager.*` | `WeldParamManager.Instance.ConfigHelper.*` |
| `ConfigForm` | `WeldDataManager.Instance.SwitchConfig(...)` | `WeldParamManager.Instance.SwitchConfig(...)` |
| `ConfigForm` | `WeldDataManager.Instance.DeleteConfig(...)` | `WeldParamManager.Instance.DeleteConfig(...)` |
| `ParamConfigPage` | `WeldDataManager.Instance.mAutoParam` | `WeldParamManager.Instance.CurrentAutoParam` |
| `ParamConfigPage` | `WeldDataManager.Instance.mConfigManager.*` | `WeldParamManager.Instance.ConfigHelper.*` |
| `ParamConfigPage` | `WeldDataManager.Instance.AddConfig(...)` | `WeldParamManager.Instance.AddConfig(...)` |
| `MotionControlWorkflow` | `SeamTrajectoryBuilder.Instance.*` | `WeldParamManager.Instance.{FeedSeamTracking, TickSeamTracking, ResetSeamTracking, AlgorithmsConfig.MinRemainBuffer / DefaultFrameSeconds, ...}`（原 `SeamGuideConfig.*` → `AlgorithmsConfig.*`，ADR-044） |
| `WeldParamControlWorkflow` | `WeldParamManager.Instance.LoadSeamGuideConfig(_seamGuide)`（自持实例回灌） | ⛔ 已删除；配置由 Manager 自持自载，工作流不再接触 |
| `WeldParamAdjustmentAlgorithm` | `RunRecordManager.Instance.RecordProcessFrame / RecordAdjustment / AbortRecording`（算法内直连落盘） | ⛔ 已删除；改触发事件经本管理器透传，落盘由 [[modules/ProductFileManager]] 异步执行（ADR-043） |
| `WeldParamAdjustmentAlgorithm` | `ExecuteAdjustment(autoParam, isCountType, countNum, robotX)` | `ExecuteAdjustment(autoParam, robotX, contourPoints)`：分段与阈值改读 `AlgorithmsConfig`（ADR-043） |
| `SeamGuideConfig` / `WeldParamAdjustmentConfig`（两配置类） | 各自 `LoadConfig(reader)` / `SaveConfig(reader)`，Manager 用 4 个方法分别载入 | ⛔ 已删除；2026-09-14 合并为单一 `WeldAlgorithmsConfig`（两节合一）+ Manager 一对 `LoadAlgorithmsConfig()` / `SaveAlgorithmsConfig()`（ADR-044） |

---

## 算法实现类（非单例，由 Manager 持有）

| 类 | 位置 | 职责 |
|---|---|---|
| `WeldAlgorithmBase` | `Abstractions/WeldAlgorithmBase.cs` | 抽象基类：`Name` / `IsReady` / `LoadConfig(object)` / `Reset()` |
| `WeldParamLookupAlgorithm` | `Algorithms/WeldParamLookupAlgorithm.cs` | 查找表生成与匹配、`FeedSpeedCal` / `LaserPowerCal` 公式 |
| `WeldParamAdjustmentAlgorithm` | `Algorithms/WeldParamAdjustmentAlgorithm.cs` | 滑动平滑、突变判定、调用查表、输出/图表/失败计数/事件；**只计算不落盘**，记录走事件（ADR-043） |
| `SeamTrackingAlgorithm` | `Algorithms/SeamTrackingAlgorithm.cs` | 线激光结果 → Y 轴 PVT 轨迹点（只计算，不写入控制器） |

---

## 遗留项

| 项 | 说明 |
|---|---|
| `CurrentRobotX` 恒为 0 | `RobotWeldData.PosX` 无写入方；待通信层对接 KUKA 真实坐标（ADR-009 遗留项） |
| `WeldProcessCompletedEventArgs` / `WeldProcessCompleted` 命名 | 保留历史命名，未随类名改造 |
| 振镜摆幅 | `WeldParamControlWorkflow.CalcGalvoAmplitude` 占位返回 0，待 `WeaveWidth` 分段查找表落地 |
| **记录订阅方未实现（TODO）** | 三个记录请求事件已就绪但**无消费者**，过程记录暂缺；待 [[modules/ProductFileManager]] 结构优化后接入，须入队后异步落盘（ADR-043） |

---

## 关联

- [[modules/WeldParamControl]] — 模块说明（架构总览 · 数据链路）
- [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] — 算法分层决策
- [[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]] — 算法纯净性与记录职责隔离
- [[decisions/ADR-044-WeldAlgorithmsConfigMerge]] — 焊接算法配置合一（`WeldAlgorithmsConfig`）
- [[lessons/AlgorithmControlRecordIsolation]] — 对应踩坑记录
- [[api/WeldParamAdjustmentAlgorithm]] — 参数调整算法 API
- [[api/SeamTrackingAlgorithm]] — 焊缝几何轨迹跟踪算法 API
- [[api/WeldParamControlWorkflow]] — 流程编排（`TriggerAdjustment` 唯一触发方）
- [[api/MotionControlWorkflow]] — 轨迹点消费与控制器写入
- [[decisions/ADR-009-WorkflowAsAdjustmentDriver]] — `TriggerAdjustment` 无参硬约束
- [[modules/ProductFileManager]] — 记录模块（订阅方待办）
