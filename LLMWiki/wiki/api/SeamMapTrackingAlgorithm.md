---
title: API — SeamMapTrackingAlgorithm 焊缝目标地图算法（前置量对齐 + 测量时刻轴值基准）
date: 2026-09-16
tags: [API, 线激光, Y轴, CSP, 焊缝跟踪, 空间地图, 前置量, 标定对, 测量时刻轴值, 机器人Y, X单调化, 高斯平滑, 野值剔除, 方向平滑, 脉冲域, WeldParamControl, ADR-006, ADR-033, ADR-042, ADR-042, ADR-043, ADR-042, ADR-042, ADR-042, ADR-042]
source: AdaWeldSystem/WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs
---

# API — SeamMapTrackingAlgorithm 焊缝目标地图算法（前置量对齐 + 测量时刻轴值基准）

> **位置**：`WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs`（命名空间 `AdaWeldSystem.WeldParamControl.Algorithms`）
> **2026-09-16 新增（ADR-042）**：焊缝跟踪「**CSP 实时目标**」模式的算法实现（非单例），
> 与 [[api/SeamTrackingAlgorithm]]（PVT 流式段）**双模式并存**，由 `SEAM_GUIDE/TRACKING_MODE` 二选一。
> **2026-09-17 模型变更（ADR-043）**：地图由「焊缝**绝对 Y**」改为「**Y 轴目标空间地图 / 示教锚定**」——
> 目标参考值 = 示教 Y 轴锁定坐标 `TeachLockYMm` + 滤波 dY；**2026-09-21 ADR-042**：最终目标再加**路径 Y 相对增量**
> （实时滤波机器人 Y − 起焊基准，示教路径 Y 逐点变化时跟随），机器人实时 Y 以**相对量**回归目标反算，
> `InstallOffsetY` 绝对标定仍不需要（**2026-09-24 经业主令整体删除**）。
> **2026-09-21 ADR-042**：`TeachLockYMm` 退出目标计算、改作 PreWork 标定位；本类产出统称 **`CorrectionMm` 修正量**（含特征偏差项 + `ROBOT_Y_GAIN`×机器人Y漂移项），**不含任何基准**——基准由运控侧叠加。
> **2026-09-22 ADR-042**：运控侧基准由「轴实际反馈」换轨为「**起焊锚点**」；本类新增**突变剔除三重护栏**（首帧种子闸门 / 连续拒绝重新种子 / 拒绝分源计数）与**方向锁迟滞释放**（`ApplyMonotonic` 重写）。`ProcessLaserResult` 定为 8 步。
> **2026-09-22 ADR-042（本页现行口径）**：⚠️ **ADR-042 决 1 的「起焊锚点」基准与「机器人 Y 取测量时刻」两项均被取代** ——
> 地图键改为「测量机器人 X + `LeadDistanceMm`」= 用户口径的 **RobotXL**（前置量入键，相位归零）；地图值改为**绝对 Y 轴目标**
> `TeachLockYMm + dY`（基准 = 标定对轴侧）；机器人 Y 差分移到**写入时刻**由运控传入并按 `RobotYGain` **反向抵消**
> （`SeamMapPoint` 随点记 `RobotY`）；X 单调化吞掉抖动回退。新增公开入口 **`TryGetTargetY(robotX, robotY, out targetY)`**。
> **2026-09-24 诊断量扩充 + 记录列换轨（业主令）**：新增公开诊断属性 **`LastMapEntryKeyX`**（最近入图键 = 测量 X + 前置量）与 **`HasLastMapEntry`**（是否已有入图点），与既有 `LastAcceptedTargetY` 共同构成 **CSPinY** 记录源；
> `MotionControlWorkflow` 的 **CspChain 写入数据链记录器整体移除**，换为 **SeamY 记录器**（`Records\SeamY\SeamYTrace_*.csv`，5 列 `当前RobotX,入图RobotCSPX,CSPinYt,CSPoutY,实时Y`（03:00 业主定版）：CSPinYt = 最近入图值（键 入图RobotCSPX = 测量 X + 前置量）、CSPoutY = 本拍查图输出（查图 X 未及地图首键时 = 标定轴值原值不变）、实时Y = 轴反馈）——业主据「CSPinY 对 KeyX / CSPoutY 对 RobotX 两线差」直读查图与跟随误差。
> **定位**：输入「线激光结果 + 机器人位姿」，输出**绝对 Y 轴目标**（经 `TryGetTargetY` 按当拍机器人位姿查询）——
> **不产出 `PVTPoint[]`**，也**不写控制器**；写轴由 [[api/MotionControlWorkflow]] 的 CSP 步骤按流程节拍（10ms/100Hz）承担（ADR-042）。
> **2026-09-22 ADR-042（本页现行口径，取代上条决 2）**：⚠️ **ADR-042 的「基准 = 标定轴值 `TeachLockYMm`」被取代** ——
> 地图值改为**测量时刻轴实际值 Ya1 + dY**（`Yt = Ya1 + d`；Ya1 是**变量**，随轴移动而变），
> 理由是线激光随轴移动、偏差 d 已「吃掉」轴位移，常量基准使 −ΔYa 无人抵消 → **正反馈积分器**。
> 本页确立**结构不变式**：**Yt 表达式内不得出现可被自身执行改变的轴状态量**。
> 新增**最终目标突变护栏** `MaxTargetStepMm`（默认 5.0mm）与 `TargetStepRejectCount` 观测，`ProcessLaserResult` 由 8 步变 **9 步**。
> ADR-042 的**前置量入键、对称查图窗、写入时刻机器人 Y 差分、按 X 键查询、X 单调化、前置段兜底**六项继续有效。
> **2026-09-23 低通整项移除（本页现行）**：⚠️ 上文「低通」口径已作废 —— 低通对象取偏差或取合成目标都会引入 ±τ 级误差（滤 d ⇒ `τ·(ẏ_轴−v_缝)` 环内自激、滤合成 ⇒ `−τ·v_缝` 斜段恒滞后），且都不是必需；业主裁定「**计算用原值，不做滤波**」。故 `ProcessLaserResult` 只保留 ④ 合成 `Yt = Ya1 + rawDy`（**9 步 → 8 步**），`DyFilterAlpha` 配置项与界面「dY低通系数」控件一并删除；抑噪由查图侧零相位空间高斯与 ③/⑤/⑦ 三道突变闸门承担。

---

## 公共 API

| 成员 | 签名 | 说明 |
|------|------|------|
| `Name` | `string { get; }` | 算法名称（「线激光焊缝地图跟踪」） |
| `IsReady` | `bool { get; }` | 配置是否已载入 |
| `Config` | `WeldAlgorithmsConfig { get; }` | 当前配置（`SEAM_GUIDE` 节内跟踪参数；ADR-042 起含 `MonotonicReleaseMm` / `ConsecutiveRejectFrames`，ADR-042 起 `LeadDistanceMm` 兼作**键平移量**、`RobotYGain` 改为**反向差分**系数、`ReverseDeadbandMm` 默认 0.1；ADR-042 起含 `MaxTargetStepMm`（默认 5.0，INI 键 `MAX_TARGET_STEP_MM`）；只读，ADR-043） |
| `SetConfig` / `LoadConfig` | `void (WeldAlgorithmsConfig)` / `void (object)` | 替换 / 抽象基类载入配置 |
| `OnLaserResult` | `void (LineLaserSeamResult result, double axisPosMm)` | **签名变更（ADR-042）**：喂入一帧线激光结果 + **测量时刻跟踪轴实际位置**（相机 SDK 回调线程，60Hz；运控侧取 `_seamAxis.GetPosition()`） |
| `OnRsiPose` | `void (double robotX, double robotY, double robotZ)` | 喂入一帧机器人位姿（RSI 接收线程，~83Hz） |
| `BeginCorrection` | `void ()` | 起焊沿激活目标查询；前置量段内尚无地图点 → `TryGetTargetY` 返回 false → 运控保持标定轴值（轴本就在该位，天然零跳变） |
| `TryGetTargetY` | `bool (double robotX, double robotY, out double targetY)` | **2026-09-22 ADR-042 新增**：按**当拍**机器人位姿取绝对 Y 轴目标（运控写入时刻调用）。查图中心 = 当拍 RobotX；单调约束与输出死区在内部施加；机器人 Y 差分按当拍值**反向抵消**；地图值语义见 ADR-042（= **Ya1 + d**） |
| `TryGetRequiredAxisVelocityMmPerS` | `bool (double robotVxMmPerS, out double requiredVelMmPerS)` | **2026-09-23 ADR-042 新增（速度前馈算法口）**：需求 = \|地图尾部局部斜率（≥2mm 基线割线，钳 ±5mm/mm + EMA 0.2）× 机器人 X 速度\|；运控据此抬速度/加速度上限，只抬上限不产生位移 |
| `Reset` | `void ()` | 复位地图与全部计数（**保留配置**）。**2026-09-22 ADR-042**：末尾补 `ClearAlarm()`——原实现只清 `_weldDirection`/`_reverseTravelMm`/`_reverseWarned`，**漏清 `_hasAlarm`**，导致复位后"已在报警态"分支恒返回、上层「模组报警」长期为真（二次模拟启动即报警且清不掉的根因之一） |
| `ClearAlarmState` | `void ()` | **2026-09-22 ADR-042 新增**：清除折返报警态（`lock(_lock){ ClearAlarm(); }`）。**仅供 `WeldParamManager` 转发**，业务侧不得直接调用算法实例；只清报警态、不清地图与位姿基准（整轮复位用 `Reset`） |
| `TrackingAlarmRequested` | `event EventHandler<TrackingAlarmEventArgs>` | X 折返超限报警（**锁外**触发） |

### 可观测性（全部 `lock` 保护读）

| 成员 | 说明 |
|---|---|
| `IsTracking` | 是否已进入跟踪（收到首帧位姿后为 true） |
| `CorrectionMm` / `HasCorrection` | **语义收窄（ADR-042 → ADR-042）**：最近一次查询的修正量（ADR-042 起 = 绝对目标 − **测量时刻轴值**），仅作诊断 / 是否已产出首帧 |
| `HasAlarm` / `AlarmReason` | 报警标志与原因 |
| `RobotX` / `RobotY` | 当前机器人 X / **滤波后**机器人 Y |
| `PathYOffset` | **语义变更（ADR-042）**：机器人 Y 差分（写入时刻机器人Y − 地图点测量时刻机器人Y，未查询为 0）；原 ADR-042「− 起焊基准」口径已废止 |
| `JitterRejectCount` | **2026-09-22 新增（ADR-042）**：累计吞掉的抖动级 X 回退帧数（不进地图、不累计路径、不报警），用于现场判断 `ReverseDeadbandMm` 是否合适 |
| `PathDistance` | 累积三维路径距离（**诊断字段**，已降级） |
| `MapPointCount` | 空间地图点数 |
| `OutlierCount` / `InvalidFrameCount` / `SmoothSkipCount` | 野值剔除数 / 无效帧数 / 平滑跳过数 |
| `TimeRejectCount` / `SpaceRejectCount` | **2026-09-22 新增（ADR-042）**：拒绝**分源**计数——时间域（首帧种子闸门 + 单帧最大变化）/ 空间域（3σ + 斜率超限），便于日志定位拒绝来源 |
| `TargetStepRejectCount` | **2026-09-22 新增（ADR-042）**：**最终目标突变**拒绝计数（相邻帧绝对目标变化超 `MaxTargetStepMm`）。长期应为 0 —— 上涨即提示识别异常或 `MaxTargetStepMm` 设得过小 |
| `AxisAtMeasureMm` | **2026-09-22 新增（ADR-042）**：最近一帧测量时刻的跟踪轴实际位置（= 参与 `Yt = Ya1 + d` 的 Ya1），供现场核对基准是否随轴移动 |
| `LastAcceptedTargetY` | **2026-09-22 新增（ADR-042）**：最近一次被接受的绝对目标 Yt（突变护栏的比较基准） |
| `LastDy` / `LastCorrectionMm` / `LastFeatureY` | 最近一次 dY / 最近一帧特征偏差修正量 / 最近一帧线激光特征点 Y（诊断用） |

### 数据结构

```csharp
public struct SeamMapPoint              // 空间地图点（只读值对象，ADR-042 起 5 参）
{
    double RobotX { get; }              // 键：焊枪到达该处时的机器人 X = 测量机器人X + LeadDistanceMm（升序）
    double TargetY { get; }             // 该 X 处的绝对 Y 轴目标 = 测量时刻轴值 Ya1 + dY（2026-09-23：时间域低通已移除）
    double RobotY { get; }              // 测量时刻的机器人 Y（滤波后），供写入时刻做差分补偿
    double PathDistance { get; }        // 累积路径距离（诊断）
    long   Timestamp { get; }
}

public class TrackingAlarmEventArgs : EventArgs
{
    string Reason { get; }              // 报警原因（纯文本无符号）
}
```

---

## 核心算法

### 一、目标地图（键 = 焊枪到达该处的机器人 X）

```
偏差 dY    = (实时特征Y − CalibratedCenterY) × AxisMmPerLaserMm × GuideSign
地图键     = _monotonicRobotX + LeadDistanceMm          // = RobotXL，前置量入键（ADR-042）
地图点值   = 测量时刻轴实际值 Ya1 + dY                          // 绝对 Y 轴目标（2026-09-23：不做任何时间域低通，用原值）
地图点附记 = 测量时刻的滤波机器人 Y                      // 供写入时刻做差
```

> 🔄 **2026-09-22 ADR-042 换轨**：原键 `measureX = _robotX`（**测量时刻**的 X）**已废止** ——
> 激光在焊枪前方 60mm，当拍测到的是**前方**焊缝，按测量时刻 X 入图会使运控在焊枪走到该 X 时
> 取到再往前一个前置量的数据，**整条修正轨迹前移 60mm 施加**。键平移后相位归零。
> 原值「滤波 dY（不含基准）」**已废止** —— 值域改为绝对 Y 轴目标，基准取标定对的轴侧 `TeachLockYMm`（2026-09-23 再修：地图值时间域低通已整项移除）。

> **2026-09-17 模型变更（ADR-043）**：原「焊缝绝对 Y = 机器人Y(滤波后) + 轴当前位置 + 滤波dY + InstallOffsetY」
> 及其反算已**废止**——机器人实时 Y 与 `InstallOffsetY` 不再参与目标反算，转而以**标定中心为特征基准、
> 示教 Y 锁为轴锚点**。详见 ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。

- **键 = 焊枪到达该处时的机器人 X**（⛔ 不是累积弧长，也不是测量时刻的 X）：地图按 `RobotX` 升序存储，查图与平滑按 X 窗口。
- **键单调（ADR-042）**：`CachePose` 对 X 做单调化——抖动级回退（≤ `ReverseDeadbandMm`）**吞掉**（不推进键、不累计路径、不入图），真实回退同样不让键倒退（回退点不属于本遍焊缝），只走方向监测累计报警。
- **为何弃用累积弧长**：① 丢一包即**永久少算**；② 数值抖动即**虚增**；③ 误差**无法自愈**。X 绝对坐标恒等可复现。
- `PathDistance` 保留但**降级为诊断字段**（三维路径累积，含 Y/Z 分量）。
- `InsertMapPoint`：前进场景从尾部向前定位插入位，**O(1) 摊还**；超过 `MaxMapPoints`（默认 2000）裁剪最旧点。

### 二、突变剔除与野值剔除（双判据 + 三重护栏）

**双判据，满足其一即剔除**（剔除点不入图，`OutlierCount++`）：

| 判据 | 条件 | 参数 |
|---|---|---|
| 时间域：单帧最大变化 | `\|rawDy − 上一接受点 rawDy\| > MaxStepChangeMm`（线激光边缘连续，单帧不可能跳变几十丝） | `MaxStepChangeMm` = 0.5mm |
| 空间域：3σ 统计异常 | 窗口样本 ≥ `MinOutlierPoints`(3) 且 `std > MinOutlierStd`(0.05) 且 `\|new − mean\| > OutlierSigmaK × σ` | `OutlierSigmaK` = 3.0 |
| 空间域：切线连续性违约（ADR-042） | 尾部两点切线外推到 arriveX，`\|new − predicted\| > TangentFloorMm(0.2) + OutlierSlopeLimitMmPerMm × gap`；连续曲线（弧/直线/S 形）沿切向永不误杀，只拦孤立飞点 | `OutlierSlopeLimitMmPerMm`（切向偏差系数，键值不变） |

> 实现上**手工遍历窗口**求 mean/std，不用 LINQ —— 避免每帧在回调线程上产生枚举器与闭包分配。

**三重护栏（2026-09-22 ADR-042 补齐）**——单纯「超限即拒」会让真实台阶把地图永久冻死：

| 护栏 | 参数 | 作用 |
|---|---|---|
| ① 首帧种子闸门 | `MaxSeedDeviationMm = 10.0`（类内常量） | 首帧无前值可比，原始偏差超物理可能范围即判识别失败，**既不入图也不建立种子** |
| ② 连续拒绝重新种子 | `ConsecutiveRejectFrames`（默认 20 帧） | 时间域连续被拒达上限 → 判**真实台阶**（起焊/收弧/错边）放行，接受新水平并置 `_dySeeded = false` 重置低通种子；未达上限则继续拒绝 |
| ③ 拒绝分源计数 | `TimeRejectCount` / `SpaceRejectCount` | 时间域与空间域分开计数，日志可直接定位拒绝来源 |

> ⚠️ 上表三层护栏判的是**特征偏差 rawDy**。**合成后的绝对目标 Yt 另有一层独立护栏** `MaxTargetStepMm`（ADR-042，见下「五」）——
> 两者对象不同：`MaxStepChangeMm = 0.5` 拦**单点野值**（用户举例的 `{0.3 0.3 1.0 …}`，跳变 0.7mm > 0.5mm），
> `MaxTargetStepMm = 5.0` 拦**成品突变**（用户口径的「突然变化 5mm」）。合层会同时失去单点野值拦截能力，故分置。

**`ProcessLaserResult` 8 步**（一帧线激光结果的完整处理）：

```
① 特征偏差换算   rawDy = (featureY − CalibratedCenterY) × AxisMmPerLaserMm × GuideSign
② 首帧种子闸门   无前值且 |rawDy| > MaxSeedDeviationMm → 丢弃（不入图、不建种子）
③ 时间域突变剔除 + 连续拒绝护栏  超 MaxStepChangeMm → 计数并（未达 ConsecutiveRejectFrames）返回
④ 合成绝对目标   targetY = ya1 + rawDy（⛔ 不做任何时间域低通：滤 d 或滤合成都引 ±τ 级误差并破坏相消，用原值）
⑤ 最终目标突变    |targetY − 上一接受目标| > MaxTargetStepMm(5.0) → 拒帧（未达 ConsecutiveRejectFrames 直接返回）
⑥ 取查图键       arriveX = _monotonicRobotX + LeadDistanceMm（= RobotXL）
⑦ 空间域野值     IsOutlier(targetY, arriveX)（切线连续性 / 3σ；连续拒 20 帧放行真实台阶）→ 丢弃
⑧ 存图           InsertMapPoint(arriveX, targetY, _filteredRobotY, ...)，并更新 _lastAcceptedRawDy / _lastAcceptedTargetY / 重置连续拒绝计数
```

> ~~⚠️ **低通首帧直取实测值**（ADR-042 三跑实测的修正）~~ **2026-09-23 低通整项移除**（业主裁定低通非必需，用原值计算）；原「首帧直取、不爬升」的坑随低通一并消失。历史留痕：低通从 0 爬升会让爬升期窗口内出现大落差，被斜率判据整段当炸点丢弃 → 地图长期不足 → 修正量恒 0。

### 三、方向平滑（方向锁 + 迟滞释放，2026-09-22 ADR-042 重写）

`ApplyMonotonic(rawValue, robotX)`：**锁向取极值后不再按行程窗口周期性重置**，只有两类事件会「重新种子」：

| 事件 | 触发条件 | 行为 |
|---|---|---|
| 未锁态判定方向 | `\|rawValue − 种子值\| ≥ MonotonicDeadbandMm`(0.05) | 按其符号锁向（正→取 `Math.Max`，负→取 `Math.Min`）；未达死区则原样跟随、不锁 |
| **真实反弯解锁** | 反向偏离 > `MonotonicReleaseMm`（默认 **0.30mm**） | `ReseedMonotonic`：以当前值为新参考并清除锁定态 |
| 持距兜底 | `\|robotX − 锁定起点X\| ≥ MonotonicWindowMm`（默认 **200mm**） | 同上重新种子（防一次错误锁定绑架整条焊缝） |

> 🔄 **演进理由**：原实现按 `MonotonicWindowMm`（用户 2026-09-22 重构时由 50 降为 **2.0mm**）周期性重置方向锁，相对 1883mm 行程会触发约 **940 次重置**，每次重置都以当时的极值为新种子 → 形成**逐窗单向累积的棘轮效应**，正是「点来回、方向反复」的病根。改为迟滞释放后，`MonotonicWindowMm` 语义**退化为持距兜底上限**。
> **效果验证（用户举例序列）**：`{1.005 1.009 1.050 1.090 1.060 1.100 1.150 1.130 1.160}` → 输出单调爬升至 **1.160**（中间 1.060 / 1.130 两处回撤均小于 0.30mm，不触发解锁）。

### 四、查询与零相位高斯空间平滑（`QueryTargetY`）

```
QueryTargetY(robotX, out targetY, out pointRobotY)            // ADR-042 取代 SmoothByRobotX
窗口 = [robotX − GaussianHalfWindowMm, robotX + GaussianHalfWindowMm]     // 对称窗
权重 = exp(−d² / (2σ²))，σ = GaussianSigmaMm（默认 12mm）
```

- **窗口对称（ADR-042）**：键已含前置量平移，查询中心即当前焊枪 X，无需再做单边平移。
  原 `[X − LeadDistanceMm, X + GaussianHalfWindowMm]`（`backWindow = max(Lead, halfWindow)`）是为补偿未平移的键而设，**已废止** —— 它只把窗口向后扩，权重峰仍在 δ=0，并未真正对齐。
- 对称窗用到已测的邻近点，属**正确的空间平滑**；未测位置没有键，天然不会被取到。
- 同时输出窗口内**加权平均的测量时刻机器人 Y**（`pointRobotY`），供运控做机器人 Y 差分。
- 有效点不足 `MinSmoothPoints`(3) 时返回 false 并 `SmoothSkipCount++`；运控据此保持标定轴值，轴停在标定位。

### 五、目标查询与限幅（不加任何基准，运控直取绝对目标）

```
TryGetTargetY(robotX, robotY, out targetY):                    // 运控每拍调用，ADR-042
    smoothedTarget = QueryTargetY(robotX) 的加权平均绝对目标   // 图值 = Ya1 + dY（2026-09-23：无时间域低通）
    smoothedTarget = ApplyMonotonic(smoothedTarget, robotX)     // 方向锁 + 迟滞释放
    ΔR             = robotY(当拍) − pointRobotY(该点测量时刻)
    targetY        = smoothedTarget − RobotYGain × ΔR           // 机器人 Y 反向抵消
    targetY        = 输出死区(targetY, _lastOutputCorrection, OutputDeadbandMm = 0.05)

运控侧：Y轴目标 = 行程限幅(ready ? targetY : TeachLockYMm)      // MotionControlWorkflow.RunCspTick（ADR-042：删「减基准再加回」折算）
```

> 🔄 **2026-09-22 ADR-042 二次换轨**：
> ① 基准由 ADR-042 的**起焊锚点 `_cspAnchorPos`**（运行时轴位置）改为 **标定轴值 `TeachLockYMm`**（标定对轴侧，常量）；`_cspAnchorPos` / `_simAnchorPos` 已删除。
> ② 机器人 Y 项由「测量时刻算 `RobotYGain ×(实时Y − 起焊基准)` 并固化入图」改为「**写入时刻**算 `RobotYGain ×(当拍Y − 该点测量时刻Y)` 并**反向抵消**」—— 测量到写入隔一个前置量行程，那段机器人 Y 变化原先无人补偿。
> ③ 原「本算法只产修正量、不含基准」的 ADR-033 纯净性口径**部分调整**：地图值含标定基准（绝对目标），但**仍不含任何运行时基准**，也不写轴 —— 限幅与写段仍全在运控侧。
> ④ 原式 `Y轴目标 = 轴实际反馈 + 限幅(ΔY)` 的废止理由（正反馈积分器）**继续成立**，不再重复。

> **常量基准的用意**：`TeachLockYMm` 是标定对的轴侧，PreWork（`DoReturnToCalibration`）保证起焊前轴已停在该位；
> ~~用常量作基准使目标绝对有界，且轴的零点映射误差天然抵消 —— 不再依赖「起焊那一刻轴恰好在哪」。~~
> ⚠️ **2026-09-22 ADR-042 取代「常量基准」**：轴一旦离开标定位（它**必须**离开才能跟随焊缝），`TeachLockYMm` 就不再等于 Ya1，
> 算出的差值恰为「轴已移动的那一段」→ −ΔYa 无人抵消 → **自激**。故基准改为**测量时刻轴实际值 Ya1**。
> **结构不变式**：`Yt` 表达式内不得出现可被自身执行改变的轴状态量（`d` 的 −ΔYa 与 `Ya1` 的 +ΔYa 必须相消）。
> **最终目标突变护栏**：`|Yt − 上一接受 Yt| > MaxTargetStepMm`（默认 5.0，可调更小）即**拒帧**（非截断——截断会造出现实中不存在的虚假目标）；
> 连续拒绝达 `ConsecutiveRejectFrames`(20) 判**真实台阶**放行并重置低通种子；独立计数 `TargetStepRejectCount`。
> 与 `MaxStepChangeMm=0.5` 的分工：后者判**特征偏差 rawDy 单分量**（拦用户举例的 `{0.3 0.3 1.0 …}`），本条判**合成后绝对目标**（拦「突然变化 5mm」）。

### 六、X 折返处置（两档）

机器人 X 只应**一直前进**（不复焊）。防误判三要素：

| 机制 | 参数 | 行为 |
|---|---|---|
| 方向锁定 | — | 首段 `dx` 定 `_direction`（`dx` 取真实位移，`_lastRobotX` 跟随真值 → 持续偏置只计一次差） |
| 回退死区 | `ReverseDeadbandMm` = **0.1mm**（ADR-042 由 0.01 提高） | 单包位移小于死区**不计入方向判定**，键也不因它倒退。原 1 丝几乎等于无死区，抖动会被当回退累计，存在累积到 `ReverseAlarmMm` 误报警的路径 |
| 键单调化 | `_monotonicRobotX` | 键只取历史最大：抖动吞掉（`JitterRejectCount++`）、真实回退同样不倒退（回退点不属于本遍焊缝） |
| 偶发折返 | `ReverseAlarmMm` = 1.0mm | 累计折返 ≤ 阈值 → **仅警告一次**（`_reverseWarned`）并继续 |
| 连续折返 | 同上 | 累计折返 > 阈值 → `TrackingAlarmRequested` → 流程线程停机 |

---

## 线程模型与并发

```
线激光 SDK 回调线程（60Hz）──OnLaserResult──┐
                                          ├─→ lock(_lock) 保护 _seamMap / 全部状态
RSI 接收线程（~83Hz）────────OnRsiPose─────┘
                                          ↓
设备流程线程（10ms/100Hz，CSP 步骤）──调── TryGetTargetY(robotX, robotY, out targetY)（内部 lock）
```

- `double` **非原子**：所有共享状态一律 `lock` 保护，读侧经属性内 `lock` 返回快照。
- **报警事件在锁外触发**（`RaiseAlarmRequest`）：先算好原因、置标志，退出 `lock` 后再 `Invoke`——
  避免订阅方（流程线程）回调重入造成死锁。
- ⛔ 订阅方**不得**在事件处理器里直接推进执行步（见下「边界与约束」）。

---

## 边界与约束

- **算法纯净（ADR-033）**：只计算——⛔ 不持 `ICspMotion`、不调 `SetCspTargetPosition`、不落盘、不推进执行步。
- **不产 PVT 点**：本类与 `PVTPoint[]` / `IPVTMotion` **完全无关**；写轴归 [[api/MotionControlWorkflow]]。
- **跨线程不推进执行步**：`TrackingAlarmRequested` 的订阅方 `MotionControlWorkflow` 只置
  `volatile _seamAlarmPending`，由**流程线程**在 `UpdateSeamTracking()` 内 `Fail()`——保证状态单次转换。
- **位姿单一真相源**：`robotX/Y/Z` 由 [[api/WeldParamManager]] 经 `OnRsiPose` 转发，源头是
  [[modules/Comm]] 的 `RobotPoseSnapshot`；⛔ 本类不自行订阅通讯事件、不轮询。
- 配置运行期**只读**，变更走 `WeldParamManager.Instance.SaveAlgorithmsConfig()`（写自有 `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`）→ `LoadAlgorithmsConfig()`。⛔ 外部不得 `new WeldAlgorithmsConfig()` 回灌。
- 日志直连 `GlobalCommData.ShowLog`，标签「焊缝地图跟踪」，**纯文本无符号**，仅在函数起止/结果处记录。
- ⚠️ **无记录事件**：本类当前未定义记录请求事件，折返报警只走控制语义的 `TrackingAlarmRequested`，**无痕迹留存**（接入记录订阅方时需一并规划）。

---

## 职责收敛（2026-09-22 ADR-042）

`ProcessRsiPose` 进一步收敛为**只维护空间基准与安全监测**：`FilterRobotY(robotY)`（Y 低通）、
`CachePose(...)`（缓存位姿 + **X 单调化**，首帧返回 true）、`TrackPathDistance(...)`（路径距离 + 方向锁定/折返监测）。
平滑反算、单调约束、机器人 Y 差分、输出死区全部移入 **`TryGetTargetY`** —— 位姿帧不再产目标，
目标只在运控**写入时刻**按当拍位姿算出。

## 关联

- 决策：**[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（绝对目标基准 = 测量时刻轴值 Ya1 + 最终目标突变护栏，现行）** · [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（前置量入键 + 对称查图窗 + 写入时刻机器人 Y 差分 + X 单调化 + 前置段兜底六项继续有效；其**决 2 基准经 ADR-030 取代**） · [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] · [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] · [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（突变剔除三重护栏 + 方向锁迟滞释放继续有效；基准与机器人 Y 时点经 ADR-005 取代）、ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）
- 同族算法：[[api/SeamTrackingAlgorithm]]（PVT 模式专属，本页的并行实现）
- 模块：[[modules/WeldParamControl]]、[[modules/MotionControl]]、[[modules/Comm]]
- 调用方（订阅方）：[[api/MotionControlWorkflow]]（CSP 步骤按拍读取目标，ADR-042）
- 配置提供方与位姿转发：[[api/WeldParamManager]]
- 位姿源头：[[modules/Comm]]（`RobotPoseSnapshot` / `TryGetRobotPose`）
- 能力契约：api/ICspMotion
- 范式：[[standards/ModuleOrganizationPattern]] · [[decisions/ADR-006-ModuleOrganizationPatternStandard]]

## 暂停入图（2026-11-17，阶段 7 / ADR-103）

- `PauseIngest`（`volatile` 字段 + 属性）：置位期间 `OnLaserResult` 只累加 `_invalidFrameCount` 并返回，不入地图，防缺值或位姿超龄造成的错键。
- 置位判据在 [[api/WeldParamManager]] `IsIngestPaused()`：缺值累计 > 0 或 `PoseAgeMs > 2 × NoValueRsiCycleMs`；有效帧到达即解除。
- `ResetTracking()` 清零该开关，避免跨会话残留。
- 关联：[[decisions/ADR-103-no-value-hold-and-distance-segment]]
