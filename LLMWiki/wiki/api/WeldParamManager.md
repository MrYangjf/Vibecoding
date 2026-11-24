---
title: WeldParamManager API 参考（焊接参数管理器 · 模块唯一入口）
date: 2026-09-14
updated: 2026-10-19
tags: [API, 焊接, 参数, 算法, 管理器, 单例, 唯一入口, 配置合一, 焊缝跟踪, CSP, 双模式, 步骤输出, ADR-008, ADR-033, ADR-043, ADR-042, ADR-042, ADR-033, ADR-043, ADR-042, ADR-042, ADR-042, ADR-042]
source: AdaWeldSystem/WeldParamControl/WeldParamManager.cs
---

# WeldParamManager API 参考

> WeldParamControl 模块**唯一外部访问入口**（单例）：集中持有焊接参数配置、全部算法实现与配置持久化。
> **位置**：`AdaWeldSystem/WeldParamControl/WeldParamManager.cs`
> **命名空间**：`AdaWeldSystem.WeldParamControl`
> **取代**：~~`WeldProcess`~~（单例，2026-09-14 ADR-008 删除）、~~`WeldDataManager`~~（同日并入本类）
> 模块背景见 [[modules/WeldParamControl]]，决策依据见 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]。

---

## 定位

```
外部（WeldParamControlWorkflow / MotionControlWorkflow / AutoParamForm / ConfigForm / ProcessControlPage / LineLaserWorkflow）
  ↓ 只认 WeldParamManager.Instance
WeldParamManager（配置 + 算法实现持有者 + 配置持久化 + 机器人位姿消费入口）
  ├─ WeldParamLookupAlgorithm      （非单例）参数查表调整
  ├─ WeldParamAdjustmentAlgorithm  （非单例）焊缝宽度驱动的参数调整
  ├─ SeamTrackingAlgorithm         （非单例）线激光焊缝几何轨迹跟踪（PVT 流式段）
  └─ SeamMapTrackingAlgorithm      （非单例）焊缝绝对目标地图（测量时刻轴值基准）+ 特征点锁定闭环（ADR-042 / ADR-042 / ADR-042 / ADR-042 / ADR-042）
  ↑ 机器人位姿：真实 = CommunicationManager.RobotDataReceived → OnRsiPose；模拟 = DeviceControlWork.SimTick → UpdateRobotPose(x,y,z)★09-22（单入口喂入，不另存副本）
```

- **单例**（`Lazy<T>`，线程安全），构造时创建**四个**算法实现、订阅机器人位姿通道，并初始化配置持久化。
- **不承载流程**：参数调整编排在 [[api/WeldParamControlWorkflow]]，轨迹点写入在 [[api/MotionControlWorkflow]]。
- **焊缝跟踪双模式**（ADR-042）：`TrackingMode` 二选一（`CspRealtime` 默认 / `PvtStream`），两套算法实例**同时存在**，按模式分派使用。
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
| `CurrentRobotX` | `double` | 机器人 X 坐标（读写；内部即 `RobotWeldData.PosX`）。真实链路由 RSI 回包刷新；**模拟态由 `SimTick → UpdateRobotPose` 喂入**（2026-09-22 单源收口）。**2026-09-28 ADR-045**：预测器激活时（真实 RSI / 模拟节拍两条喂入链路同机制）getter 返回**读取时刻外推值**（喂入锚点 + 相邻差分速度 × 时间差，失效间隔 1s 清速、外推 200ms 钳位），消除喂入固定频率阶梯；未激活返回喂入原值 |
| `CurrentRobotY` | `double` | **机器人 Y 坐标**（2026-09-20 新增，读写；内部即 `RobotWeldData.PosY`，由 `OnRobotDataReceived` 在机器人数据回调中同步），（2026-09-24：焊缝 Y 记录改 5 列后不再入档机器人 Y，本属性仍供算法机器人 Y 差分与诊断使用；[[decisions/ADR-037-ProductProductionRecordLifecycle]] 决 6）。**2026-09-28 ADR-045**：预测语义与 `CurrentRobotX` 相同——写入时刻机器人 Y 差分（ADR-042 §1.2 的 Yb2）由阶梯变连续，消除 CSPinY 与实时Y 的喂入同频周期波动 |
| `RobotWeldData` | `RobotWeldData` | 机器人焊接数据（只读引用） |
| `AlgorithmsConfig` | `WeldAlgorithmsConfig` | **焊接算法配置（只读引用，Manager 独占实例，XML+INI 双后端）**：**合计 37 项**（`SEAM_GUIDE` 几何/安装常量 13 项 + 流程阈值/开关/节拍 17 项 + `WELD_PARAM_ADJUST` 3 项 + `LASER_CALIBRATION` 线激光标定 4 项；含新增 `TeachLockYMm`（示教 Y 轴锁定坐标，XML `SEAM_GUIDE/TEACH_LOCK_Y_MM`）；**全部由 `ProcessControlPage` 显式配置与显示**），运行期只读 ★ADR-043 / ADR-042 / ADR-043（取代原 `SeamGuideConfig` / `AdjustmentConfig` 两属性） |
| `TaLaCurve` | `TaLaCurveConfig` | **TA/LA 标定曲线（只读引用，Manager 独占实例）**：曲线A（LA 位置↔光斑大小）/ 曲线B（TA 位置→LA 偏移补偿）。外部只读消费，⛔ 不得 `new` / 持有回灌 ★ADR-053 |
| `AnchorSpotMm` | `double` | **曲线A 锚点光斑（毫米）**：LA=0 处的最聚焦光斑，取自曲线A 采样点表的 X=0 锚点（随标定数据变化），无 X=0 点时回退内置默认值 0.6mm。**外部唯一读取口**——⛔ 外部不得直读 `TaLaCurveConfig` 的锚点常量（配置访问唯一入口，ADR-066）★2026-10-21 新增 |
| `TrackingMode` | `SeamTrackingMode` | **焊缝跟踪模式**（读 `SEAM_GUIDE/TRACKING_MODE`，空配置回退 `CspRealtime`）★ADR-042 |
| `IsCspTrackingMode` | `bool` | 便捷判定：`TrackingMode == CspRealtime` ★ADR-042 |
| `HasRobotPose` | `bool` | **是否已有机器人位姿**——转发通讯层快照 ★ADR-042 |
| `TryGetRobotPose` / `TryGetSeamTrackingCorrectionMm` | `bool (out double …)` | 取机器人位姿 X/Y/Z / 取当前**修正量**（ADR-042 起语义收窄为「绝对目标 − 测量时刻轴值」；**运控已不再消费**，改走下行 `TryGetSeamTrackingTargetY`，本项仅作界面/诊断观测）★ADR-042 / ADR-042 / ADR-042 |
| `TryGetSeamTrackingTargetY` | `bool (double robotX, double robotY, out double targetY)` | **2026-09-22 ADR-042 新增、ADR-042 换基准**：按**当拍机器人位姿**取**绝对 Y 轴目标**（CSP 步骤每拍调用）；`false` = 前置量段内尚无地图点，调用方保持标定轴值 ★ADR-042 / ADR-042 |
| `TryGetSeamTrackingRequiredVelocityMmPerS` | `bool (double robotVxMmPerS, out double requiredVelMmPerS)` | **2026-09-23 ADR-042 新增**：透传算法口 `TryGetRequiredAxisVelocityMmPerS`，返回 Y 轴跟踪速度需求（= \|局部斜率×vX\|），运控作速度前馈 ★ADR-042 |

### 输出（透传 `WeldParamAdjustmentAlgorithm`）

| 成员 | 类型 | 说明 |
|---|---|---|
| `LaserPowerOutput` | `double` | 激光功率输出（最近一次调整结果） |
| `SpotWidthOutput` | `double` | **光斑宽度输出**（= 采用焊缝宽度 × 系数 W，ADR-043 新增；暂不下发机器人，后续供振镜摆幅用） |
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
| `SpotWidthDic` | `Dictionary<double,double>` | **焊缝宽度 → 光斑宽度**（= 焊缝宽度 × W；ADR-043 新增，DB 分段表第 5 列「光斑宽度」） |
| `SwingWidthDic` | `Dictionary<double,double>` | **焊缝宽度 → 摆幅宽度**（2026-10-20 新增；公式初值 = 光斑摆幅系数 × 焊缝宽，可经表格手动修正，输出用查表值；落 DB 分段表第 6 列「振镜摆幅」）。语义：单一配置内光斑大小不变，随焊缝变化的是振镜摆动宽度 |
| `SwingFrequencyDic` | `Dictionary<double,int>` | **焊缝宽度 → 摆幅频率 Hz**（2026-10-21 新增；公式初值由该档摆幅宽度按基准点反算——摆幅越大频率越低，默认 2mm→500Hz、10mm→200Hz；可经表格手动核对，输出用查表值；落 DB 分段表第 7 列「摆幅频率」） |

### 折线图数据（透传 `WeldParamAdjustmentAlgorithm`，只读）

`ContourChart` / `LaserPowerChart` / `FeedSpeedChart` / `SeamWidthChart` / `RobotSpeedChart`（均 `ChartVar`，基于 RobotX 坐标）。

`AdjustmentOutputVersion`（`long`，透传算法 `OutputVersion`）：输出缓存版本号，算法每次执行调整或复位时 `Interlocked.Increment` 自增。**主界面按自身节拍（33ms 轮询）读此号判重**，变化才增量消费缓存新原始点——生产者只写缓存不驱动界面，写入频次由主界面决定（同线激光写 CSP 的"生产在缓存、消费频次由线程决定"范式）。

### 事件

| 成员 | 说明 |
|---|---|
| `WeldProcessCompleted` | 焊接工艺调整完成事件（`EventHandler<WeldProcessCompletedEventArgs>`），显式 `add`/`remove` 透传参数调整算法 |
| `FrameRecordRequested` | **过程帧记录请求**（`EventHandler<WeldFrameRecordEventArgs>`），透传参数调整算法；落盘由记录模块异步执行（ADR-033） |
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
| `LoadProfileIntoLookupTable` | `void (string identityInfo)` | 从 SQLite 读分段数据写入查找表（空集合不覆盖内存；载入次序=基准兜底在前、本方法覆盖在后，ADR-043） |
| `LoadAlgorithmsConfig` | `void ()` | **无参**：从双后端载入——XML `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`（`SEAM_GUIDE` 几何段 + `LASER_CALIBRATION`，**轨迹跟踪 TabPage 独占**）+ **INI 四文件**（见下表），同一实例分发给算法（构造时自动调用一次）★ADR-043 / ADR-033 / ADR-076 D8 |
| `SaveAlgorithmsConfig` | `void ()` | **无参**：把当前焊接算法配置写回双后端（XML 节 `SaveXdocument()` 落盘 + INI `SaveToFile()` 落盘）★ADR-043 / ADR-033 |

> **配置由本管理器独占**（ADR-008 第三次修订 + ADR-033 + ADR-043 + ADR-033）：唯一实例由 `AlgorithmsConfig` 只读属性暴露
> （类型 `WeldAlgorithmsConfig`，XML+INI 双后端），持久化由 Manager 独占五套读写器——XML `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`（`SEAM_GUIDE` 几何段 + `LASER_CALIBRATION`，**轨迹跟踪 TabPage 独占**）+ **INI 按 TabPage 四文件**（`Config/WeldParamControl/Algorithm_INI/`）：

| 文件 | 归属 TabPage | section |
|---|---|---|
| `WeldParamControlAlgorithm.ini` | 工艺·激光工艺设置 | `PROCESS_CONTROL`（Preset 12 + `LOCK_Y_CALIB`） |
| `WeldParamControlAlgorithmAdaptive.ini` | 工艺·自适应工艺参数设置 | `WELD_PARAM_ADJUST` |
| `WeldParamControlAlgorithmFlow.ini` | 系统·流程控制与测试 | `PROCESS_CONTROL`（4 开关）+ `SEAM_GUIDE`/`ENABLE_GUIDE` |
| `WeldParamControlAlgorithmTrajectory.ini` | 系统·轨迹跟踪参数设置 | `SEAM_GUIDE`（19 跟踪阈值） |

——外部只读 `AlgorithmsConfig`。⭐ **2026-11-19 ADR-076 D8**：INI 由单文件拆为 4 文件 ⇒ 页面保存只重写自己的文件，不再覆盖其它页面未保存的值（`INIFile.SaveToFile()` 是整文件重写，是覆盖的根因）。zone → 文件路由见 `WeldAlgorithmsConfig.AlgorithmIniSet.FileFor(zone)`。
> ⛔ 外部不得 `new WeldAlgorithmsConfig()`、不得持有或回灌实例；原 `LoadSeamGuideConfig(SeamGuideConfig)` 重载、`WeldParamControlWorkflow.SeamGuide` 属性与 `SaveSeamGuide()` 方法均已删除。
> ~~`SeamGuideConfig`~~ / ~~`WeldParamAdjustmentConfig`~~ 两类与 ~~`LoadAdjustmentConfig`~~ / ~~`SaveAdjustmentConfig`~~ / ~~`LoadSeamGuideConfig`~~ / ~~`SaveSeamGuideConfig`~~ 四方法于 2026-09-14 合并为上述一对（ADR-043）。

### 算法方法

| 方法 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static WeldParamManager` | `Lazy<T>` 单例 |
| `TriggerAdjustment` | `void ()` | **无参**触发一次参数调整（ADR-013）；分段与阈值取自 `AlgorithmsConfig`，不再作为形参传递（ADR-033）。**2026-09-20 起触发前经 `FeedLatestSeamWidth()` 喂入线激光最近一帧焊缝宽度**（`LineLaserManager.LastResult` 的 Width0/Width1 均值 → `SeamCalData.AddSeamWidth`，宽度序列唯一喂数入口）——序列攒够 `CountNum` 后按平滑宽度查表，查表计算按实测宽度驱动的关键链路。⚠️ **2026-09-23（ADR-043）演进**：`SEAM_WIDTH_SOURCE = Manual` 时**跳过线激光喂入**（固定宽度不被实测序列污染，算法内部直查表）；~~执行后喂入 XL 缓存~~（**同日经 ADR-043 决 6 下沉进 `ExecuteAdjustment` 内部**，仅 Laser 源入缓存，Manager 不再代喂） |
| `BuildLookupTable` | `void (AutoParam)` | 生成查找表（基准公式；仅首建兜底与修正基准使用，重建会覆盖分段手工修正，ADR-043） |
| `RefreshSpotWidthByGain` | `void ()` | 按当前系数 W 重算光斑宽度列（宽度档与分段修正不变，ADR-043） |
| `TryLookup` | `bool (double, out double, out double, out double)` | 按焊缝宽度匹配参数（签名不变） |
| `TryLookupSwingWidth` | `bool (double seamWidth, out double swingWidth)` | **2026-10-20 新增**：按焊缝宽度查摆幅宽度（最近档，容差 100 同 `TryLookup` 口径）；`false` = 无该档记录，调用方按公式「光斑摆幅系数 × 焊缝宽」兜底 |
| `TryLookupSwingFrequency` | `bool (double seamWidth, out int frequencyHz)` | **2026-10-21 新增**：按焊缝宽度查摆幅频率 Hz（最近档，容差 100 同口径）；`false` = 无该档记录，调用方按 `AutoParam.CalSwingFrequency(该档摆幅宽度)` 兜底 |
| `TryGetParamOutputAt` | `bool (double robotX, out laserPower, out feedSpeed, out robotSpeed, out spotWidth, out seamWidth)` | **ADR-043 新增**：按当拍机器人 X 取「已到达的最邻近 XL」的缓存工艺参数（~~`WeldParamXLCacheAlgorithm` 透传~~ **同日经 ADR-043 决 6 改为 `_paramAdjustmentAlgorithm.TryGetOutputAt` 透传**；XL 输出支路每拍调用）；`false` = 前置量段内尚无缓存点 |
| `ParamCacheCount` | `int` | **ADR-043 新增**：工艺参数 XL 缓存点数（观测用：判断缓存链路是否活跃；ADR-043 决 6 起透传调整算法 `XlCacheCount`） |
| `Reset` | `void ()` | 复位全部算法状态 |
| `FeedSeamTracking` | `PVTPoint[] (LineLaserSeamResult, double measuredFps, double axisCurrentPos)` | 喂入一帧线激光结果，返回 PVT 点数组 |
| `TickSeamTracking` | `PVTPoint[] ()` | 按最长间隔强制输出 PVT 点 |
| `DrainSeamTracking` | `PVTPoint[] ()` | 排空轨迹算法剩余点 |
| `ResetSeamTracking` | `void (reason = "")` | 复位轨迹跟踪算法（**CSP 与 PVT 两个实现一并复位）并级联复位工艺调整运行期状态**（宽度/四曲线/输出缓存版本号）；⚠️ 2026-09-23 ADR-043 起调用点 = **会话边界**（点击模拟测试 / 焊前检查 `DoSubPrework` 播种之前），起焊沿不再调用本方法。**2026-11-23**：同时调 `ResetNoValueDistance()` 清缺值累计距离与位姿锚点 —— 否则上一轮的缺值累计会被下一轮 PreWork 首拍继承，直接判超阈值报警停焊 |
| `ResetTrackingForWeldStart` | `void (reason = "")` | **2026-09-23 ADR-043 新增**：起焊沿复位——只复位跟踪算法（PVT + 焊缝地图），**不清工艺调整**（起焊沿已处于播种后的管控窗口内，清参数会产生 1.2→0→1.2 闪断）；由 `MotionControlWorkflow.OnSeamTrackingStart` 调用 |
| `ClearSeamTrackingAlarm` | `void ()` | **2026-09-22 ADR-042 新增**：清除焊缝跟踪折返报警态，转发至 `_seamMapTrackingAlgorithm.ClearAlarmState()`。只清报警态、**不清地图与位姿基准**（整轮复位用 `ResetSeamTracking`）；由 `MotionControlWorkflow.ClearSeamAlarm()` 在模拟启停两侧调用 |
| `OnSeamLaserResult` | `void (LineLaserSeamResult, double axisPosMm)` | **CSP 模式**：喂入一帧线激光结果 + **测量时刻跟踪轴实际位置**（ADR-042 起签名加参，运控侧传 `_seamAxis.GetPosition()`），更新**绝对目标地图**（ADR-042 / ADR-042 / ADR-042 / ADR-042）。**2026-11-16**：有效帧到达顺手清零缺值累计距离 |
| `BeginSeamTrackingForPreWork` | `void ()` | **PreWork 激活地图跟踪（2026-11-23 新增）**：只调 `_seamMapTrackingAlgorithm.BeginCorrection()` 放开跟踪门禁（否则 `TryGetTargetY` 恒返回 false、目标回标定位无跟踪修正），⛔ **不开缺值量测**、⛔ 不清零缺值距离——PreWork 引导未稳，量测若开必误累计并触发 `NoValueAlarm` 停焊；缺值量测仍留到起焊沿 `BeginSeamTrackingCorrection` 启用 |
| `BeginSeamTrackingCorrection` | `void ()` | **CSP 模式**：起焊沿激活目标输出（ADR-042 起基准为**测量时刻轴值**：前置量段内无地图点 → `TryGetTargetY` 返回 `false` → 运控回落标定轴值，轴本就在该位，天然零跳变）★ADR-042 / ADR-042。**2026-11-16**：清零并开启缺值量测窗口，Info 日志打印生效阈值 |
| `UpdateRobotPose` | `void (double x, double y, double z)` | **模拟态喂入机器人位姿（等效 RSI 回包）**：写 `RobotWeldData.PosX/Y/Z` + `SeamMapTrackingAlgorithm.OnRsiPose`，置位算法 `_hasRobotY` 放开特征帧拦截。**模拟位姿唯一喂入口**（真实链路走 `OnRobotDataReceived`，两条来源互不覆盖）★2026-09-22。**2026-09-28 ADR-045**：喂入即**喂入位姿预测器**（模拟与真实同为按节拍采样喂入、同为阶梯，业主裁定同病同修；`UpdatePosePredictor`） |

### 轨迹跟踪可观测性

| 成员 | 类型 | 说明 |
|---|---|---|
| `SeamTrackingHasFault` | `bool` | 轨迹算法是否报警（**PVT 模式**） |
| `SeamTrackingFaultReason` | `string` | 报警原因（**PVT 模式**） |
| `SeamTrackingLastDeviation` | `double` | 最近一次偏差（**PVT 模式**） |
| `SeamTrackingLastTargetPos` | `double` | 最近一次目标位置（**PVT 模式**） |
| `SeamTrackingCorrectionMm` | `double` | **CSP 模式**：当前修正量（ADR-042 起 = 绝对目标 − **测量时刻轴值**，仅诊断）★ADR-042 / ADR-042 |
| `SeamTrackingLastCorrectionMm` / `SeamTrackingLastFeatureY` / `SeamTrackingPathYOffset` | `double` | **2026-09-21 新增（ADR-042 三跑诊断）**：最近一帧特征偏差修正量 / 最近一帧线激光特征点 Y / 机器人 Y 漂移补偿项（未乘系数） |
| `SeamTrackingHasAlarm` / `SeamTrackingAlarmReason` | `bool` / `string` | **CSP 模式**：折返超限报警标志与原因 ★ADR-042 |
| `NoValueDistanceMm` | `double` | **2026-11-16 新增**：缺值累计行进距离（毫米，只读观测值）。起焊沿清零并开窗，停焊沿关窗；激光有效帧到达清零；**2026-11-23**：会话复位（`ResetSeamTracking` / `ResetTrackingForWeldStart`）同样清零，且**数值与位姿锚点同清**（只清数值会按旧锚点补出整段跨会话位移）。位姿有效按 `|ΔX|` 累计，位姿停滞（间隔 > 2×RSI 周期）按 `v_weld×Δt` 推定，推定速度钳位 100 mm/s；本阶段只观测不触发动作 ★ADR-042 |
| `NoValueSource` | `string` | **2026-11-16 新增**：缺值距离尺源（`实测` / `推定`），只供日志标注 |
| `SeamTrackingMapPointCount` / `SeamTrackingOutlierCount` / `SeamTrackingInvalidFrameCount` / `SeamTrackingSmoothSkipCount` | `int` | **CSP 模式**：地图点数 / 野值剔除数 / 无效帧数 / 平滑跳过数 ★ADR-042 |
| `SeamTrackingRobotX` | `double` | **CSP 模式**：最近一次机器人 X 坐标（观测用：判断机器人位姿回调链路是否活跃）★2026-09-22 |
| `SeamTrackingTargetStepRejectCount` | `int` | **2026-09-22 新增（ADR-042）**：累计因**最终目标突变**被拒的帧数（长期应为 0）★2026-09-22 |
| `SeamTrackingAxisAtMeasureMm` | `double` | **2026-09-22 新增（ADR-042）**：最近一帧测量时刻的跟踪轴实际位置（`Yt = Ya1 + d` 的 Ya1）★2026-09-22 |

### 事件（CSP，ADR-042）

| 成员 | 说明 |
|---|---|
| `SeamTrackingAlarmRequested` | **折返超限报警**（`EventHandler<TrackingAlarmEventArgs>`），透传 `SeamMapTrackingAlgorithm`；⛔ 订阅方（[[api/MotionControlWorkflow]]）只置标志位，`Fail()` 由流程线程执行 |

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
| `ProcessControlPage` | `WeldDataManager.Instance.mAutoParam` | `WeldParamManager.Instance.CurrentAutoParam` |
| `ProcessControlPage` | `WeldDataManager.Instance.mConfigManager.*` | `WeldParamManager.Instance.ConfigHelper.*` |
| `ProcessControlPage` | `WeldDataManager.Instance.AddConfig(...)` | `WeldParamManager.Instance.AddConfig(...)` |
| `MotionControlWorkflow` | `SeamTrajectoryBuilder.Instance.*` | `WeldParamManager.Instance.{FeedSeamTracking, TickSeamTracking, ResetSeamTracking, AlgorithmsConfig.MinRemainBuffer / DefaultFrameSeconds, ...}`（原 `SeamGuideConfig.*` → `AlgorithmsConfig.*`，ADR-043） |
| `WeldParamControlWorkflow` | `WeldParamManager.Instance.LoadSeamGuideConfig(_seamGuide)`（自持实例回灌） | ⛔ 已删除；配置由 Manager 自持自载，工作流不再接触 |
| `WeldParamAdjustmentAlgorithm` | `RunRecordManager.Instance.RecordProcessFrame / RecordAdjustment / AbortRecording`（算法内直连落盘） | ⛔ 已删除；改触发事件经本管理器透传，落盘由 [[modules/ProductFileManager]] 异步执行（ADR-033） |
| `WeldParamAdjustmentAlgorithm` | `ExecuteAdjustment(autoParam, isCountType, countNum, robotX)` | `ExecuteAdjustment(autoParam, robotX, contourPoints)`：分段与阈值改读 `AlgorithmsConfig`（ADR-033） |
| `SeamGuideConfig` / `WeldParamAdjustmentConfig`（两配置类） | 各自 `LoadConfig(reader)` / `SaveConfig(reader)`，Manager 用 4 个方法分别载入 | ⛔ 已删除；2026-09-14 合并为单一 `WeldAlgorithmsConfig`（两节合一）+ Manager 一对 `LoadAlgorithmsConfig()` / `SaveAlgorithmsConfig()`（ADR-043） |

---

## 算法实现类（非单例，由 Manager 持有）

| 类 | 位置 | 职责 |
|---|---|---|
| `WeldAlgorithmBase` | `Abstractions/WeldAlgorithmBase.cs` | 抽象基类：`Name` / `IsReady` / `LoadConfig(object)` / `Reset()` |
| `WeldParamLookupAlgorithm` | `Algorithms/WeldParamLookupAlgorithm.cs` | 查找表生成与匹配、`FeedSpeedCal` / `LaserPowerCal` 公式 |
| `WeldParamAdjustmentAlgorithm` | `Algorithms/WeldParamAdjustmentAlgorithm.cs` | 滑动平滑、突变判定、调用查表、输出/图表/失败计数/事件；**只计算不落盘**，记录走事件（ADR-033） |
| `SeamTrackingAlgorithm` | `Algorithms/SeamTrackingAlgorithm.cs` | 线激光结果 → Y 轴 PVT 轨迹点（**PVT 模式专属**；只计算，不写入控制器） |
| `SeamMapTrackingAlgorithm` | `Algorithms/SeamMapTrackingAlgorithm.cs` | 线激光结果 + 机器人位姿 → **绝对目标地图 → `TryGetTargetY` 绝对 Y 轴目标**（**CSP 模式专属**；只计算、不写控制器；地图值含**测量时刻轴值**基准，**不含运行时基准**）★ADR-042 / ADR-042 / ADR-042 / ADR-042 |

---

## 遗留项

| 项 | 说明 |
|---|---|
| ~~`CurrentRobotX` 恒为 0~~ ✅ **2026-09-22 已不成立** | 真实链路 `OnRobotDataReceived` 写 `CurrentRobotX`；模拟态 `SimTick → UpdateRobotPose` 写 `CurrentRobotX/Y/Z`——两路均有写入方。~~待通信层对接 KUKA 真实坐标~~（ADR-013 遗留项部分闭环） |
| `WeldProcessCompletedEventArgs` / `WeldProcessCompleted` 命名 | 保留历史命名，未随类名改造 |
| ~~振镜摆幅（占位返回 0）~~ ✅ **2026-10-20 已实现** | `WeldParamControlWorkflow.CalcGalvoAmplitude` 现按「固定输出光斑模式返 0 / 非固定模式查表 → 公式兜底」输出摆幅宽度，振镜下发链 `ApplyGalvoAmplitude` 消费 `LastOutput.GalvoAmplitude`。详见 [[modules/WeldParamControl]] 「振镜摆幅：已实现」 |
| ~~旧摆幅取值通道休眠~~ ✅ **2026-10-21 已删除** | `WeldAlgorithmsConfig.WeaveAmplitudeK`（INI `WEAVE_AMPLITUDE_K`，公式 `宽×(1+k)`）与 `Curves/WeaveWidthTable`（`GetAmplitudeMm`/`LoadCalibration`/`TryGetFrequencyHz`）**无使用方**，业主裁定删除（csproj 已退注册，drift REMOVED 已登记）。摆幅宽度/摆幅频率改由 `AutoParam.SpotSwingGain` + `AutoParam.CalSwingFrequency` + `SwingWidthDic`/`SwingFrequencyDic` 承载；`WeldParamManager.WeaveTable` 持有同时移除。⚠️ DB 旧第 7 列「振镜频率」为历史遗留（读取方已废止）保留不删，新数据写第 7 列「摆幅频率」 |
| `SpotWidthGain`（W）保留 | 光斑宽度 W 通道（`宽×W`）保留不动，与摆幅宽度/频率链路互不干涉 |
| **记录订阅方未实现（TODO）** | 三个记录请求事件已就绪但**无消费者**，过程记录暂缺；待 [[modules/ProductFileManager]] 结构优化后接入，须入队后异步落盘（ADR-033）。⚠️ **CSP 跟踪链路目前连记录请求事件都未定义**，折返报警只走 `SeamTrackingAlarmRequested`（控制语义），**无痕迹留存**（ADR-042） |
| 步骤节拍精度待上机验证 | CSP 输出随 `FlowProcess` 节拍推进（运行态基线 10ms/100Hz），`timeBeginPeriod(1)` 只在起焊沿至停焊沿区间生效；Windows 非实时 OS，**实机节拍精度需现场实测**。限幅器按**实测 dt** 折算量纲，节拍抖动或改节拍均**无需重算限幅参数**（原 `CycleTimeMs` 配置项已删除，ADR-042） |
| 位姿通道降级 | `AttachRobotPoseChannel()` 取 `GlobalCommData.mCommunicationManager` 为 null 时**只告警不中断**——此时 CSP 模式拿不到位姿，Y 轴目标不会推进（安全侧表现） |

## WeldParamData（焊参数据模型）

> 2026-09-17 补记（源码核对：`WeldParamControl/WeldParamData.cs`）。该文件是 WeldParamControl 的**数据模型族**（无 `WeldParamData` 类名，文件即名）。

### 数据模型构成

| 类 | 职责 |
|---|---|
| `RobotWeldData` | 机器人焊接数据：`PosX/PosY/PosZ/Speed/StartX/EndX/EndDelayDistance`（公共字段）；Manager 以 `RobotWeldData` 属性持有 |
| `SeamCalData` | 焊缝宽度滑动平均（默认窗口 10）：`AddSeamWidth` / `SeamWidthCal` |
| `AutoParam` | 自动参数配置（焊丝/板厚/功率等 + `CalVar()` 计算 KVar/JVar）；Manager 以 `CurrentAutoParam` 持有 |
| `ChartVar` | 折线坐标（X/Y 列表），主界面表格折线图勾画 |
| `WeldFrameRecordEventArgs` / `WeldAdjustmentRecordEventArgs` | 过程帧 / 调整动作**记录请求**事件参数（算法只发请求，落盘由 [[modules/ProductFileManager]] 执行，ADR-008/043） |
| `WeldProcessCompletedEventArgs` | 焊接工艺调整完成事件参数（RobotX + ContourData + 输出值） |
| `SeamType` | 焊缝种类枚举（None/VType/TType） |

### 载体角色

`RobotWeldData` / `AutoParam` 由 Manager 持有，是**算法↔工作流之间的参数载体**：`WeldParamControlWorkflow` 经 Manager 写入配置，`WeldParamAdjustmentAlgorithm` / `SeamTrackingAlgorithm` 等算法实现读取计算；记录请求事件参数把过程快照从算法侧搬运到 [[api/ProductFileRecordManager]]（订阅方闭环）。

### ⚠️ 设计预留（2026-09-17 审计）

`RobotWeldData` 的 `SetStartX` / `SetEndX` / `SetEndDelayDistance` / `SetWeldRange` / `IsInWeldArea` / `IsBeyondEnd` / `SetRobot` / `EffectiveEndX` 等 **8 个写入口/判定口当前为设计预留、消费者 0（2026-09-17 审计）**，删除与否待裁定——删除前请先全库检索复核。

---

## 关联

- [[modules/WeldParamControl]] — 模块说明（架构总览 · 数据链路）
- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] — 算法分层决策
- ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 算法纯净性与记录职责隔离
- ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 焊接算法配置合一（`WeldAlgorithmsConfig`）
- [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — 焊缝跟踪 CSP 实时目标 + 双模式并存（现行）
- [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] / [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — 闭环基准两次换轨（起焊锚点 → 标定轴值 → **测量时刻轴值 Ya1**）+ 最终目标突变护栏 + 脉冲域量化（现行）
- [[decisions/ADR-045-PredictiveRobotPoseSnapshot]] — 预测性机器人位姿快照（`CurrentRobotX/Y` 读取时刻外推；模拟链路喂入即失效；地图入图保持上报原值）（现行）
- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] — 焊缝宽度来源选择 + 光斑宽度 + XL 缓存输出链路（现行）
- ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — CSP 输出并入 FlowProcess 步骤驱动（撤销独立 1ms 线程）
- [[decisions/ADR-033-ConfigArchitectureStandard]] — 配置架构标准（类别/类型/格式三段式 + XML/INI 分轨；首个落地 WeldAlgorithmsConfig 拆分；含 ADR-027 设备数据边界例外）

- [[lessons/AlgorithmControlRecordIsolation]] — 对应踩坑记录
- [[lessons/StepDrivenWorkflowPitfalls]]（七.5）— 1ms 调度（**2026-09-16 起随独立线程移除而失效**，页内已加沿革处置）
- [[lessons/StepDrivenWorkflowPitfalls]]（七.2）— 跨线程不推进执行步
- [[api/WeldParamAdjustmentAlgorithm]] — 参数调整算法 API
- [[api/SeamTrackingAlgorithm]] — 焊缝几何轨迹跟踪算法 API（PVT 模式专属）
- [[api/SeamMapTrackingAlgorithm]] — 焊缝修正量地图 + 特征点锁定闭环算法 API（CSP 模式专属）
- [[api/WeldParamControlWorkflow]] — 流程编排（`TriggerAdjustment` 唯一触发方）
- [[api/MotionControlWorkflow]] — 轨迹点/CSP 目标消费与控制器写入
- [[modules/Comm]] — 机器人位姿上行快照（`RobotPoseSnapshot`）
- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] — `TriggerAdjustment` 无参硬约束
- [[modules/ProductFileManager]] — 记录模块（订阅方待办）


## 2026-10-19：⑤工艺输出 5 facade（透传参数调整算法）

`ManualSeamWidthMm` / `SpotWidthGain` / `ParamOutputHz` / `FeedforwardSafetyFactor` / `EnableMonotonicConstraint`
——get/set 透传 `_paramAdjustmentAlgorithm` 同名属性（算法转发 `_config`，配置实例由 Manager 独占持有、
`LoadAlgorithmsConfig` 同实例分发，落盘仍走 `SaveAlgorithmsZone`）。消费方：ProcessControlPage
`LoadParamOutOnForm`/`BtnSaveAutoParam`（UI 读写唯一入口 = 参数调整算法管理）。

## 缺值观测与按距离分段（2026-11-17，阶段 7 / ADR-103）

- `PoseAgeMs`：最近一帧机器人位姿距今毫秒（锁内只读取 `Stopwatch` 差；未收到位姿返回 `double.MaxValue`）。
- `OnSeamLaserResult`：喂入激光结果前先设 `_seamMapTrackingAlgorithm.PauseIngest = IsIngestPaused()`，判据「缺值累计 > 0 或 `PoseAgeMs > 2 × NoValueRsiCycleMs`」，有效帧到达即自动解除。
- `SegmentDistanceMm`：透传 `WeldParamAdjustmentAlgorithm.Config`；`IsCountType`/`CountNum` facade 随配置项一并删除。
- `FeedLatestSeamWidth` 改调 `AccumulateSeamWidth`，同一帧宽度同时进滑动窗与段内累计。
- 关联：[[decisions/ADR-103-no-value-hold-and-distance-segment]] · [[api/WeldParamAdjustmentAlgorithm]]

