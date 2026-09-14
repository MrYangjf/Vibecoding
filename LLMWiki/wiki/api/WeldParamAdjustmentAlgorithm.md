---
title: API — WeldParamAdjustmentAlgorithm 焊缝宽度驱动的参数调整算法
date: 2026-09-14
tags: [API, 焊接, 参数调整, 焊缝宽度, 查表, 记录隔离, 配置合一, WeldParamControl, ADR-041, ADR-043, ADR-044]
source: AdaWeldSystem/WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs
---

# API — WeldParamAdjustmentAlgorithm 焊缝宽度驱动的参数调整算法

> **位置**：`WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs`
> **命名空间**：`AdaWeldSystem.WeldParamControl.Algorithms`
> **2026-09-14 重命名**：原 `WeldSeamTrackingAlgorithm` 名实不符，改为「焊缝宽度驱动的参数调整算法」。
> **定位**：非单例算法实现，由 [[api/WeldParamManager]] 持有，消费线激光焊缝宽度序列并输出工艺参数。
> **2026-09-14 去记录化 + 配置接入（ADR-043）**：本类**只计算不落盘**——原
> `RunRecordManager.RecordProcessFrame` / `RecordAdjustment` / `AbortRecording` 三处直接落盘**已删除**，
> 改为触发记录请求事件；运行参数（阈值/分段）从构造函数硬编码外提为 `WeldAlgorithmsConfig`（Manager 独占；2026-09-14 由 `WeldParamAdjustmentConfig` 合并而来，ADR-044）。
> 本类不再 `using AdaWeldSystem.ProductFileManager`。

---

## 公共 API

| 成员 | 签名 | 说明 |
|------|------|------|
| `Name` | `string { get; }` | 算法名称（「焊缝宽度驱动的参数调整」） |
| `IsReady` | `bool { get; }` | 查表算法就绪且配置已载入 |
| `Config` | `WeldAlgorithmsConfig { get; }` | 运行配置（只读引用，由 Manager 载入） |
| `SetConfig` | `void (WeldAlgorithmsConfig)` | 更新运行配置（`null` 忽略） |
| `LoadConfig` | `void (object)` | 载入运行配置（转型 `WeldAlgorithmsConfig`；**不再**重建查找表） |
| `Reset` | `void ()` | 复位运行期状态（保留查找表与配置） |
| `ExecuteAdjustment` | `void (AutoParam autoParam, double robotX = 0, List<Point> contourPoints = null)` | 每帧调整主流程（**已去掉 `isCountType` / `countNum` 形参**） |
| `Trigger` | `bool` | 已触发调整标志 |
| `StartRobotX` | `double` | 焊接起始机器人 X 坐标 |
| `CurrentSeamWidth` | `double` | 本轮采用的焊缝宽度 |
| `FeedSpeedOutput` | `double` | 送丝速度输出 |
| `RobotSpeedOutput` | `double` | 焊接速度输出 |
| `LaserPowerOutput` | `double` | 激光功率输出 |
| `ConsecutiveFailureCount` | `int` | 连续失败计数（只读） |
| `MaxConsecutiveFailures` | `int` | 最大允许连续失败次数（透传 `Config`） |
| `IsCountType` | `bool` | 是否按点数分段（透传 `Config`） |
| `CountNum` | `int` | 每段点数（透传 `Config`） |
| `TotalExecuteCount` | `int` | 算法执行总次数（只读） |
| `SeamCalData` | `SeamCalData` | 焊缝宽度滑动平均计算器 |
| `ContourChart` / `LaserPowerChart` / `FeedSpeedChart` / `SeamWidthChart` / `RobotSpeedChart` | `ChartVar` | 折线图数据 |
| `WeldProcessCompleted` | `EventHandler<WeldProcessCompletedEventArgs>` | 调整完成事件 |
| `FrameRecordRequested` | `EventHandler<WeldFrameRecordEventArgs>` | **过程帧记录请求**（每帧，落盘由记录模块异步执行） |
| `AdjustmentRecordRequested` | `EventHandler<WeldAdjustmentRecordEventArgs>` | **调整动作记录请求**（调整成功时） |
| `AbortRecordRequested` | `EventHandler` | **记录中断请求**（连续失败超限时，无载荷） |

> ⛔ 本类**不得**出现 `RunRecordManager` / `System.IO` / `File.` / `StreamWriter` / `XmlSerializer`；
> 需要留痕只发事件，由记录模块订阅后异步落盘（ADR-043）。

---

## 运行配置（`WeldAlgorithmsConfig` · `WELD_PARAM_ADJUST` 节）

| 项 | 默认 | 说明 |
|---|---|---|
| `MaxConsecutiveFailures` | 5 | 最大允许连续失败次数，达到即触发 `AbortRecordRequested` 并转失败事件 |
| `IsCountType` | `true` | 是否按点数分段（`false` 按距离分段仍为 TODO） |
| `CountNum` | 5 | 每段点数 |

配置节 `WELD_PARAM_ADJUST`，与 `SEAM_GUIDE` **同属一个配置类** `WeldAlgorithmsConfig`（ADR-044），同存 `Config/XML/WeldParamControl.xml`；
实例与读写器由 [[api/WeldParamManager]] 独占，外部只读（`Manager.AlgorithmsConfig`），改后调 `Manager.SaveAlgorithmsConfig()` 落盘。

---

## 执行流程

```
每帧调用 ExecuteAdjustment(autoParam, robotX, contourPoints)
  ↓ 连续失败 ≥ Config.MaxConsecutiveFailures ?
     是 → 触发 AbortRecordRequested + 触发失败完成事件（返回）
     否 → 继续
  ↓ Config.IsCountType == true ?
     是 → SeamCalData 滑动平均
       ↓ |smoothed - CurrentSeamWidth| > Sensitivity 且未 Trigger ?
          是 → WeldParamLookupAlgorithm.TryLookup → 更新输出
          否 → 保持当前输出
     否 → TODO（按距离分段）
  ↓ StoreChartData（只写 ChartVar，不落盘）
  ↓ 触发 FrameRecordRequested（落盘由记录模块异步执行）
  ↓ actionSuccess ? 触发 AdjustmentRecordRequested
  ↓ 触发 WeldProcessCompleted
```

---

## 关联

- [[api/WeldParamManager]] — 持有本算法并代理其输出、透传记录事件、独占运行配置
- `WeldParamLookupAlgorithm`（查表算法，由 [[api/WeldParamManager]] 持有）— 被本算法调用
- [[api/WeldParamControlWorkflow]] — 流程编排，触发 `TriggerAdjustment()`
- [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] — 算法分层决策
- [[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]] — 算法纯净性与记录职责隔离
- [[decisions/ADR-044-WeldAlgorithmsConfigMerge]] — 焊接算法配置合一（`WeldAlgorithmsConfig`）
- [[lessons/AlgorithmControlRecordIsolation]] — 对应踩坑记录
- [[modules/ProductFileManager]] — 记录订阅方（待办）
