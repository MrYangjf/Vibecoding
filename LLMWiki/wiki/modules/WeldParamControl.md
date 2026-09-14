---
title: WeldParamControl 模块 — 焊接参数控制与工艺计算
date: 2026-08-28
updated: 2026-09-14
tags: [模块, 焊接, 工艺, 自适应, 功率, 送丝, 振镜, 焊缝, 算法分层, Manager, 记录隔离, 配置合一, ADR-041, ADR-043, ADR-044]
source: AdaWeldSystem/WeldParamControl/ + MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs
---

# WeldParamControl 模块 — 焊接参数控制与工艺计算

> 目录 `AdaWeldSystem/WeldParamControl/`，命名空间 `AdaWeldSystem.WeldParamControl`。
> **定位**：**管理所有焊接参数与焊接算法** —— 提供计算公式、接口与配置。
> ⛔ **本模块不单独开流程**；编排只在 [[api/WeldParamControlWorkflow]]。

> **2026-09-14 架构纠偏（ADR-041）**：~~`WeldProcess`~~ 单例已删除，模块改为
> 「**抽象基类 + 若干非单例实现类 + Manager 唯一入口**」；外部一律经 [[api/WeldParamManager]] 访问。
> 数据结构迁入 `WeldParamData.cs`；~~`WeldDataManager`~~ 已并入 `WeldParamManager`；
> ~~`SeamTrajectoryBuilder`~~ 已演进为 `SeamTrackingAlgorithm`。
> **线激光引导配置（`SeamGuideConfig`）由 Manager 独占持有与持久化**（自有 `Config/XML/WeldParamControl.xml`），
> 原 `WeldParamControlWorkflow.SeamGuide` / `SaveSeamGuide()` 已删除；`SeamGuideSample` 归入 `Algorithms/`。
> 详见 [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]]。

> **2026-09-14 算法纯净性与记录隔离（ADR-043）**：算法**只计算、不落盘**——`WeldParamAdjustmentAlgorithm` 内
> 原 `RunRecordManager.RecordProcessFrame` / `RecordAdjustment` / `AbortRecording` 三处直接落盘**已删除**，
> 改为触发记录请求事件（`FrameRecordRequested` / `AdjustmentRecordRequested` / `AbortRecordRequested`），
> 经 Manager 透传，由记录模块订阅后**异步**落盘；本模块**不再依赖** [[modules/ProductFileManager]]。
> 同时新增 `WeldParamAdjustmentConfig`（节 `WELD_PARAM_ADJUST`），运行参数由 Manager 独占持有；
> `ExecuteAdjustment` 去掉 `isCountType` / `countNum` 形参。详见 [[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]]。

> **2026-09-14 配置合一（ADR-044）**：~~`SeamGuideConfig`~~ 与 ~~`WeldParamAdjustmentConfig`~~ **两个配置类已合并**为单一
> `WeldAlgorithmsConfig`（**同文件、同节名不变**：仍为 `SEAM_GUIDE` + `WELD_PARAM_ADJUST` 两节，落在 `Config/XML/WeldParamControl.xml`，
> 存量配置文件**无需迁移**）。Manager 改为**一个配置实例**（只读属性 `AlgorithmsConfig`）+ **一对**无参
> `LoadAlgorithmsConfig()` / `SaveAlgorithmsConfig()`；~~`LoadAdjustmentConfig`~~ / ~~`SaveAdjustmentConfig`~~ /
> ~~`LoadSeamGuideConfig`~~ / ~~`SaveSeamGuideConfig`~~ 已删除。详见 [[decisions/ADR-044-WeldAlgorithmsConfigMerge]]。

---

## 一、架构总览

```
WeldParamControl/
├── WeldParamData.cs                     数据类集合（含记录请求事件参数）
├── WeldParamManager.cs                  单例 · 唯一外部访问入口（配置 + 全部算法实现 + 记录事件透传）
├── WeldAlgorithmsConfig.cs              焊接算法配置（SEAM_GUIDE + WELD_PARAM_ADJUST 两节合一，Manager 独占；ADR-044）
├── Abstractions/
│   └── WeldAlgorithmBase.cs             抽象基类：Name / IsReady / LoadConfig(object) / Reset
└── Algorithms/
    ├── SeamGuideSample.cs               算法私有输入结构（结果 + 机器人坐标 + 时间戳）
    ├── WeldParamLookupAlgorithm.cs      实现 a：焊接参数查表调整
    ├── WeldParamAdjustmentAlgorithm.cs  实现 b：焊缝宽度驱动的参数调整（只计算 + 发记录请求事件）
    └── SeamTrackingAlgorithm.cs         实现 c：线激光焊缝几何轨迹跟踪（输出 PVT 点）
```

> 两节**同属一个配置类** `WeldAlgorithmsConfig`，共用同一份配置文件与同一个读写器：`Config/XML/WeldParamControl.xml`（ADR-043 / ADR-044）。

| 层 | 类型 | 是否单例 | 职责 |
|---|---|---|---|
| 入口 | `WeldParamManager` | ✅ 单例 | 持有配置与算法实现，透传输出/查找表/事件，无参触发调整，统一管理配置持久化 |
| 抽象 | `WeldAlgorithmBase` | 抽象类 | 定义算法对外公共属性与函数接口 |
| 实现 | `WeldParamLookupAlgorithm` | ❌ 非单例 | 查找表生成、焊缝宽度匹配、送丝/功率计算公式 |
| 实现 | `WeldParamAdjustmentAlgorithm` | ❌ 非单例 | 滑动平滑、突变判定、调查表、输出/图表/失败计数/事件 |
| 实现 | `SeamTrackingAlgorithm` | ❌ 非单例 | 线激光结果 + 机器人坐标 → Y 轴 PVT 轨迹点（只计算，不写入控制器） |

> ⛔ 不得再向 Manager 或算法实现类里加入流程编排；⛔ 不得恢复 `WeldProcess` / `WeldDataManager` / `SeamTrajectoryBuilder`。

---

## 二、算法抽象层（ADR-041）

### 抽象基类 `WeldAlgorithmBase`（`Abstractions/`）

```csharp
public abstract class WeldAlgorithmBase
{
    string Name { get; }                       // 算法名称（日志/可观测性标识）
    bool   IsReady { get; }                    // 配置是否已载入
    void   LoadConfig(object config);          // 载入算法专属配置
    void   Reset();                            // 复位运行期状态（保留配置）
}
```

实现类按自身类型转换 `config`：参数类算法用 `AutoParam`，轨迹跟踪用 `WeldAlgorithmsConfig`。

### 实现 a：`WeldParamLookupAlgorithm` —— 焊接参数查表调整

维护四份查找结构：`SeamWidthList`（键）+ `LaserPowerDic` / `FeedSpeedDic` / `RobotSpeedDic`。

- `BuildLookupTable(AutoParam)`：按焊缝宽度范围与灵敏度生成映射。
- `TryLookup(seamWidth, out laserPower, out feedSpeed, out robotSpeed)`：按焊缝宽度匹配最近一档。
- 公式（静态）：
  - `FeedSpeedCal` = `60 × KVar × SeamWidth × PlateThickness × RobotSpeed / (π/4 × WireDiameter²)`
  - `LaserPowerCal` = `JVar × (π/4 × WireDiameter² × FeedSpeed/60) / MVar`

### 实现 b：`WeldParamAdjustmentAlgorithm` —— 焊缝宽度驱动的参数调整

- `ExecuteAdjustment(autoParam, robotX, contourPoints)`：每帧调用。连续失败超阈值 → 触发 `AbortRecordRequested` 与失败完成事件；否则按 `Config.IsCountType` 分段做滑动平均（`SeamCalData`），突变超过 `Sensitivity` 且未处于 `Trigger` 时调 `WeldParamLookupAlgorithm.TryLookup` 更新三路输出。
- 持有 `ChartVar` ×5（轮廓/功率/送丝/缝宽/速度）、`ConsecutiveFailureCount` / `MaxConsecutiveFailures` / `TotalExecuteCount`、`WeldProcessCompleted` 事件。
- 运行参数取自 `Config`（`WeldAlgorithmsConfig`，Manager 独占）：`MaxConsecutiveFailures` / `IsCountType` / `CountNum`。
- **不落盘**：每帧触发 `FrameRecordRequested`，命中调整时触发 `AdjustmentRecordRequested`，超阈值时触发 `AbortRecordRequested`；落盘由记录模块异步执行（ADR-043）。
- `isCountType == false`（按距离分段）仍为 TODO 未实现。

### 实现 c：`SeamTrackingAlgorithm` —— 线激光焊缝几何轨迹跟踪

输入线激光结果 + 机器人坐标 + 引导轴当前位置，经三级修正后输出 `PVTPoint[]`：

- `Feed(result, measuredFps, axisCurrentPos)`：喂入一帧结果，达到 `BatchSize` 时返回点数组。
- `Tick()`：按 `MaxOutputIntervalMs` 强制返回一段点。
- `Drain()`：排空剩余点。
- `Reset()`：清空状态。
- 可观测性：`HasFault` / `FaultReason` / `LastDeviation` / `LastTargetPos`。

> **边界**：本算法只负责计算轨迹点，**不持有 `IPVTMotion`**，也不调用 `BeginMove` / `ContinueMove`；点集由 [[api/MotionControlWorkflow]] 批量写入控制器。

---

## 三、Manager 唯一入口（ADR-041）

`WeldParamManager.Instance` 是模块**唯一外部访问点**，构造时 `new` 出三个算法实现并持有，同时初始化配置持久化（INI / ConfigHelper / AutoParamHelper）。

### 配置与运行期

| 分类 | 成员 | 说明 |
|---|---|---|
| 配置 | `CurrentAutoParam` | 当前自动参数配置（null 时无法计算） |
| 配置 | `ConfigHelper` | 自动调整参数配置管理器（基础配置与 JSON 映射） |
| 配置 | `AutoParamHelper` | 自动调整参数值管理器（分段数据表） |
| 配置 | `CurrentAutoParamId` | 当前配置标识（INI 持久化） |
| 配置 | `IsCountType` / `CountNum` / `MaxConsecutiveFailures` | 参数调整运行配置（透传，源 `AlgorithmsConfig`） |
| 配置 | `AlgorithmsConfig` | **Manager 独占的配置实例**（只读引用；`WeldAlgorithmsConfig`，两节合一；ADR-041 / ADR-043 / ADR-044） |
| 配置 | `CurrentRobotX` | 机器人 X 坐标（读写；内部即 `RobotWeldData.PosX`） |
| 输出 | `LaserPowerOutput` / `FeedSpeedOutput` / `RobotSpeedOutput` | 最近一次调整结果 |
| 输出 | `CurrentSeamWidth` | 本轮采用的焊缝宽度（平滑后） |
| 计数 | `ConsecutiveFailureCount` / `MaxConsecutiveFailures` / `TotalExecuteCount` | 失败与执行计数 |
| 查找表 | `SeamWidthList` / `LaserPowerDic` / `FeedSpeedDic` / `RobotSpeedDic` | 可读写透传 |
| 图表 | `ContourChart` / `LaserPowerChart` / `FeedSpeedChart` / `SeamWidthChart` / `RobotSpeedChart` | 折线图数据（只读） |
| 事件 | `WeldProcessCompleted` | 透传参数调整算法的完成事件 |
| 事件 | `FrameRecordRequested` / `AdjustmentRecordRequested` / `AbortRecordRequested` | **记录请求透传**（落盘由记录模块异步执行，ADR-043） |

### 配置管理方法

| 方法 | 说明 |
|---|---|
| `SwitchConfig(configId)` | 切换到指定配置 |
| `AddConfig(configId)` | 新增配置并切换 |
| `DeleteConfig(configId)` | 删除非默认/非当前配置 |
| `SaveCurrentAutoParam()` | 保存当前 AutoParam 到 ConfigHelper |
| `SaveCurrentProfile()` | 保存当前分段参数到 SQLite |
| `ReloadCurrentParamValues()` | 重新载入当前配置并重建查找表 |
| `LoadProfileIntoLookupTable(identityInfo)` | 从 SQLite 读分段数据写入查找表 |
| `LoadAlgorithmsConfig()` | **无参**从自有 `Config/XML/WeldParamControl.xml` 载入 `SEAM_GUIDE` + `WELD_PARAM_ADJUST` 两节，并**分发给两个算法**（构造时自动调用一次；ADR-044） |
| `SaveAlgorithmsConfig()` | 把当前焊接算法配置两节一并写回自有配置文件，末尾 `SaveXdocument()` 落盘（ADR-044） |

> **配置由 Manager 独占**：构造时 `LoadAlgorithmsConfig()` 一次载入两节，共用同一个 `XdocumentReaderWriter`（`Config/XML/WeldParamControl.xml`，两节并存），并把**同一个配置实例**分发给 `WeldParamAdjustmentAlgorithm` 与 `SeamTrackingAlgorithm` 只读消费。⛔ 外部不得 `new WeldAlgorithmsConfig()`、不得持有或回灌实例——原 `WeldParamControlWorkflow.SeamGuide` / `SaveSeamGuide()` / `_seamGuide` 已删除（ADR-041 第三次修订）；参数调整三项运行参数亦从算法硬编码外提（ADR-043）；~~`SeamGuideConfig`~~ / ~~`WeldParamAdjustmentConfig`~~ 两类于 2026-09-14 合并为 `WeldAlgorithmsConfig`（ADR-044）。

### 算法方法

| 方法 | 说明 |
|---|---|
| `TriggerAdjustment()` | **无参**触发一次参数调整（ADR-009） |
| `BuildLookupTable(AutoParam)` | 生成查找表 |
| `TryLookup(...)` | 按焊缝宽度匹配参数 |
| `Reset()` | 复位全部算法状态 |
| `FeedSeamTracking(...)` | 喂入一帧线激光结果，返回 PVT 点数组 |
| `TickSeamTracking()` | 强制输出一段 PVT 点 |
| `DrainSeamTracking()` | 排空剩余 PVT 点 |
| `ResetSeamTracking()` | 复位轨迹跟踪算法 |

> `WeldProcessCompletedEventArgs` 与事件名保留历史命名，未随类名改造。

---

## 四、数据类集合（`WeldParamData.cs`）

| 类/结构 | 职责 |
|---|---|
| `RobotWeldData` | 机器人焊接数据（坐标、速度、焊接区域判定） |
| `SeamCalData` | 焊缝宽度滑动平均计算器 |
| `AutoParam` | 自动参数配置（含 `CalVar` 计算 KVar/JVar） |
| `ChartVar` | 折线图坐标数据 |
| `WeldProcessCompletedEventArgs` | 焊接工艺调整完成事件参数 |
| `WeldFrameRecordEventArgs` | 过程帧记录请求事件参数（过程快照 7 项，不含帧索引） |
| `WeldAdjustmentRecordEventArgs` | 调整动作记录请求事件参数（继承 `WeldFrameRecordEventArgs`） |
| `SeamType` | 焊缝种类枚举（None/VType/TType） |

---

## 五、触发接口：`TriggerAdjustment`（无参）

```csharp
// WeldParamManager
public void TriggerAdjustment()
{
    if (CurrentAutoParam != null)
        _paramAdjustmentAlgorithm.ExecuteAdjustment(CurrentAutoParam, CurrentRobotX);
}
```

> **重要**：`TriggerAdjustment()` 是**无参**方法（[[decisions/ADR-009-WorkflowAsAdjustmentDriver]] 硬约束）。特征与配置已由 Manager 内部取用。⛔ **不要给它加参数**。
> 分段方式与失败阈值取自 `AlgorithmsConfig`，不再作为 `ExecuteAdjustment` 形参传递（ADR-043）。

---

## 六、焊接工艺控制流程（WeldParamControlWorkflow）

位于 `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs`，详见 [[api/WeldParamControlWorkflow]] 与 [[modules/DeviceControl]]。

### 数据链路

```
线激光结果（焊缝宽度）+ 机器人 RobotX
  ↓ WeldParamControlWorkflow.ComputeAndOutput()（只置 _pendingCompute）
WeldParamControlWorkflow.DoCompute()（执行步 10）
  ↓ WeldParamManager.Instance.TriggerAdjustment()  【无参】
WeldParamAdjustmentAlgorithm.ExecuteAdjustment → WeldParamLookupAlgorithm.TryLookup
  ↓ FillOutput（读 Manager 输出属性）
WeldParamOutput（功率/送丝/速度/摆幅）→ SendToRobot 下发机器人（执行步 20）
```

---

## 七、线激光引导 Y 轴轨迹跟踪（SeamTrackingAlgorithm，ADR-041 演进）

**定位**：本模块的「结果 → 运动」算法面。线激光结果**不再由线激光管理器直写 PVT**，
而是经 `SeamTrackingAlgorithm` 做修正与标定转换后**输出 PVT 点数组**，
由 [[api/MotionControlWorkflow]] 负责缓冲区管理与写入控制器。

### 偏差模型与三级修正

```
偏差 = (特征Y − LaserZeroMm) × AxisMmPerLaserMm × GuideSign
运动目标 = 轴当前值 + 偏差
```

| 环节 | 行为 | 参数 |
|---|---|---|
| **无值容差** | 机器人行程内无有效结果 → 偏差记 0 继续移动；累计行程超限 → `HasFault` 报警 | `NoValueToleranceMm` |
| **超限剔除** | 相邻偏差跳变超过阈值 → 不归入轨迹计算，保持上一有效偏差 | `OutlierLimitMm` |
| **单调约束** | 行程窗口内只朝一个方向移动，反向抖动抑制为保持 | `MonotonicWindowMm` / `MonotonicDeadbandMm` |

### 数据链路

```
LineLaserManager.ResultReady
  ↓ MotionControlWorkflow 订阅（仅 Working 态喂入）
WeldParamManager.Instance.FeedSeamTracking(结果, 实测帧率, 轴当前位置)
  ↓ SeamTrackingAlgorithm 搓合 SeamGuideSample（+ 机器人 X + 时间戳）
滤波 / 超限剔除 / 单调约束 / 标定转换
  ↓ 返回 PVTPoint[]（攒够 BatchSize 或 Tick 强制）
MotionControlWorkflow 缓冲区 → IPVTMotion.BeginMove / ContinueMove → Y 轴
```

> ⚠️ `SeamTrackingAlgorithm` 内部读 `WeldParamManager.Instance.CurrentRobotX` 作为机器人 X（当前恒为 0，见第八节遗留项）。

---

## 八、遗留项

### 记录订阅方待落地（TODO，ADR-043）

算法已改为只发记录请求事件，但**订阅方尚未实现**——`ProductFileControl` 结构待一并优化后再接入。
接入前：`FrameRecordRequested` / `AdjustmentRecordRequested` / `AbortRecordRequested` **无消费者**，
过程记录（`RunRecordManager.RecordProcessFrame` / `RecordAdjustment` / `AbortRecording`）**暂缺**。
接入要求：订阅方只做入队（O(1)），落盘在后台异步执行，不得在计算路径上同步落盘。

### 振镜摆幅：待实现（查表项，非公式）

`WeldParamControlWorkflow.CalcGalvoAmplitude` 当前 TODO 占位返回 `0.0`。

### 机器人 X 坐标无真实来源

`WeldParamManager.CurrentRobotX` 内部读 `RobotWeldData.PosX`，该字段**从未被任何代码写入**，故恒为 0。
影响：`SeamTrackingAlgorithm` 的行程判定与 `LineLaserWorkflow` 的焊缝长度保护实际失效。
处置：待通信层对接 KUKA 真实坐标（ADR-009 遗留项，本次架构纠偏**保持兼容未改**）。

---

## 关联

- [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] — 本次算法分层决策
- [[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]] — 算法纯净性与记录职责隔离
- [[lessons/AlgorithmControlRecordIsolation]] — 对应踩坑记录
- [[standards/ModuleOrganizationPattern]] — 模块组织范式标准
- [[api/WeldParamManager]] — Manager 唯一入口 API
- [[api/WeldParamAdjustmentAlgorithm]] — 参数调整算法 API
- [[api/SeamTrackingAlgorithm]] — 焊缝几何轨迹跟踪算法 API
- [[api/WeldParamControlWorkflow]] — 流程编排（计算后下发机器人）
- [[api/MotionControlWorkflow]] — 轨迹点消费与控制器写入
- [[modules/DeviceControl]] — `WeldParamControlWorkflow` 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（含完整数据链路）
- [[decisions/ADR-040-SeamGuideTrajectoryBuilder]] — 轨迹构造原始决策（已演进）
- [[decisions/ADR-009-WorkflowAsAdjustmentDriver]] — 工作流作为调整主驱动
- [[modules/LineLaserCam]] — 英莱线激光，焊缝信息源头
