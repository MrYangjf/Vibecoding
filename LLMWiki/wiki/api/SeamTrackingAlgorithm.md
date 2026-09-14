---
title: API — SeamTrackingAlgorithm 线激光焊缝几何轨迹跟踪算法
date: 2026-09-14
tags: [API, 线激光, Y轴, PVT, 焊缝跟踪, 轨迹跟踪, 配置合一, WeldParamControl, ADR-041, ADR-044]
source: AdaWeldSystem/WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs
---

# API — SeamTrackingAlgorithm 线激光焊缝几何轨迹跟踪算法

> **位置**：`WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs`（命名空间 `AdaWeldSystem.WeldParamControl.Algorithms`）
> **2026-09-14 新增（ADR-041）**：取代 ~~`SeamTrajectoryBuilder`~~ ——
> 线激光结果不再直写 PVT，而是经本类做滤波、超限剔除、单调约束与标定转换后**输出 PVT 点数组**，
> 由 [[api/MotionControlWorkflow]] 负责写入控制器。
> **定位**：焊接参数模块的「结果 → 运动」算法实现（非单例）。输入线激光结果 + 机器人坐标 + 时间戳，
> 输出 Y 轴 PVT 运动目标；**只计算轨迹点，不直接操作 `IPVTMotion`**。

---

## 公共 API

| 成员 | 签名 | 说明 |
|------|------|------|
| `Name` | `string { get; }` | 算法名称（「线激光焊缝几何轨迹跟踪」） |
| `IsReady` | `bool { get; }` | 配置是否已载入 |
| `Config` | `WeldAlgorithmsConfig { get; }` | 当前配置（标定与修正参数；两节合一，ADR-044） |
| `SetConfig` | `void (WeldAlgorithmsConfig)` | 替换配置 |
| `LoadConfig` | `void (object)` | 抽象基类实现，内部调用 `SetConfig` |
| `Feed` | `PVTPoint[] (LineLaserSeamResult, double measuredFps, double axisCurrentPos)` | 喂入一帧结果；达到 `BatchSize` 时返回点数组 |
| `Tick` | `PVTPoint[] ()` | 按 `MaxOutputIntervalMs` 强制返回一段轨迹点 |
| `Drain` | `PVTPoint[] ()` | 排空剩余待下发点 |
| `Reset` | `void ()` | 开始新一段跟踪：清空状态与报警 |
| `HasFault` / `FaultReason` | `bool` / `string { get; }` | 无有效结果超限报警标志与原因 |
| `LastDeviation` / `LastTargetPos` | `double { get; }` | 最近偏差 / 运动目标，供界面观测 |

---

## 修正与转换（核心）

```
偏差 = (特征Y − LaserZeroMm) × AxisMmPerLaserMm × GuideSign
运动目标 = 轴当前值（axisCurrentPos） + 偏差
```

| 环节 | 行为 | 参数 |
|---|---|---|
| **无值容差** | 机器人行程内无有效结果 → 偏差记 0 继续移动；累计行程超限 → `HasFault` | `NoValueToleranceMm` |
| **超限剔除** | 相邻偏差跳变超过阈值 → 该点不归入轨迹计算，保持上一有效偏差 | `OutlierLimitMm` |
| **单调约束** | 行程窗口内只朝一个方向移动，反向抖动抑制为保持 | `MonotonicWindowMm` / `MonotonicDeadbandMm` |
| **标定转换** | 线激光毫米坐标 → 轴毫米运动目标 | `AxisMmPerLaserMm` / `LaserZeroMm` / `GuideSign` |

> 单调约束专治线激光数值抖动（如 `2.55 2.57 2.56 2.58 2.55 2.58 2.59 2.56 2.59 2.59 2.57`）——
> 窗口内输出为单调阶梯，轴不会产生微小回调。

---

## 输出节拍

| 项 | 默认 | 说明 |
|---|---|---|
| `BatchSize` | 4 | 攒够即返回 |
| `MaxOutputIntervalMs` | 250 | **最长输出间隔**：无论攒批是否够都必须输出一段（与相机前置 50mm / 500ms 滞后匹配） |
| `MinRemainBuffer` | 200 | 续喂水位下限，由 MotionControlWorkflow 在写入前检查 |
| `MaxPendingPoints` | 8000 | 待下发点上限，超出丢弃最旧点 |
| `DefaultFrameSeconds` | 1/60 | 实测帧率不可用时的默认帧间隔 |
| 速度 | — | 位置一阶差分；时间取相邻帧实测间隔（相对时间模式） |

---

## 使用模式（由 MotionControlWorkflow 驱动）

```csharp
// 1. 装配：运控初始化成功后订阅线激光结果（配置已由 WeldParamManager 构造时自载，无需再 push）
LineLaserManager.Instance.ResultReady += OnSeamResultReady;

// 2. 起止沿：线激光进入 Working 时 Reset 起段，离开时 Drain 收尾
if (active) WeldParamManager.Instance.ResetSeamTracking();
else EnqueueAndWrite(WeldParamManager.Instance.DrainSeamTracking(), isFinal: true);

// 3. 逐帧喂入（相机 SDK 回调线程）
PVTPoint[] points = WeldParamManager.Instance.FeedSeamTracking(
    e.Result, e.MeasuredFps, seamAxis.GetPosition());
Enqueue(points);

// 4. 周期节拍与报警（设备流程线程 StepReady）
PVTPoint[] tickPoints = WeldParamManager.Instance.TickSeamTracking();
Enqueue(tickPoints);
WriteToControllerWhenReady();
if (WeldParamManager.Instance.SeamTrackingHasFault)
    Fail(WeldParamManager.Instance.SeamTrackingFaultReason);
```

---

## 边界与约束

- **不持有 `IPVTMotion`**：算法只输出 `PVTPoint[]`，写入控制器由 [[api/MotionControlWorkflow]] 负责。
- 相机 SDK 回调线程与设备流程线程并发访问，内部统一加锁；`Feed` / `Tick` / `Drain` 不得在锁外触碰 `_pending`。
- 配置运行期只读，禁止在回调线程改动；变更走 `WeldParamManager.Instance.SaveAlgorithmsConfig()`（写自有 `Config/XML/WeldParamControl.xml`）→ `LoadAlgorithmsConfig()`。⛔ 外部不得 `new WeldAlgorithmsConfig()` 回灌。
- 日志直连 `GlobalCommData.ShowLog`，标签「线激光焊缝跟踪」，纯文本无符号。
- ⚠️ 单调窗口与死区为现场标定项，焊缝在窗口内反向拐弯时需实测调整。

---

## 关联

- 决策：[[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]]
- 前身决策：~~[[decisions/ADR-040-SeamGuideTrajectoryBuilder]]~~（已演进为本页）
- 模块：[[modules/WeldParamControl]]、[[modules/LineLaserCam]]、[[modules/MotionControl]]
- 调用方：[[api/MotionControlWorkflow]]
- 配置提供方：[[api/WeldParamManager]]（自持 `WeldAlgorithmsConfig` 实例 + 自有 `Config/XML/WeldParamControl.xml`，`LoadAlgorithmsConfig()` / `SaveAlgorithmsConfig()`；ADR-044）
- 配置合一：[[decisions/ADR-044-WeldAlgorithmsConfigMerge]]
- 被取代：[[api/SeamTrajectoryBuilder]]（⛔ 已废弃）
- 运控侧：[[api/MontionManager]]
