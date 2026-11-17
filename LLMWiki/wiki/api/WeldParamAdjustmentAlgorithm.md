---
title: API — WeldParamAdjustmentAlgorithm 焊缝宽度驱动的参数调整算法
date: 2026-09-14
tags: [API, 焊接, 参数调整, 焊缝宽度, 查表, 记录隔离, 配置合一, WeldParamControl, ADR-008, ADR-033, ADR-043]
source: AdaWeldSystem/WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs
---

# API — WeldParamAdjustmentAlgorithm 焊缝宽度驱动的参数调整算法

> **位置**：`WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs`
> **命名空间**：`AdaWeldSystem.WeldParamControl.Algorithms`
> **2026-09-14 重命名**：原 `WeldSeamTrackingAlgorithm` 名实不符，改为「焊缝宽度驱动的参数调整算法」。
> **定位**：非单例算法实现，由 [[api/WeldParamManager]] 持有，消费线激光焊缝宽度序列并输出工艺参数。
> **2026-09-14 去记录化 + 配置接入（ADR-033）**：本类**只计算不落盘**——原
> `RunRecordManager.RecordProcessFrame` / `RecordAdjustment` / `AbortRecording` 三处直接落盘**已删除**，
> 改为触发记录请求事件；运行参数（阈值/分段）从构造函数硬编码外提为 `WeldAlgorithmsConfig`（Manager 独占；2026-09-14 由 `WeldParamAdjustmentConfig` 合并而来，ADR-043）。
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
| `AdjustmentRecordRequested` | `EventHandler<WeldAdjustmentRecordEventArgs>` | **调整动作记录请求**（调整成功时）。**2026-09-20**：事件参数补 `RobotSpeedOutput`——与送丝/功率一样把查表输出的机器人速度带出，供记录模块按机器人 X 对齐落盘（[[decisions/ADR-037-ProductProductionRecordLifecycle]] 决 6） |
| `AbortRecordRequested` | `EventHandler` | **记录中断请求**（连续失败超限时，无载荷） |

> ⛔ 本类**不得**出现 `RunRecordManager` / `System.IO` / `File.` / `StreamWriter` / `XmlSerializer`；
> 需要留痕只发事件，由记录模块订阅后异步落盘（ADR-033）。

---

## 运行配置（`WeldAlgorithmsConfig` · `WELD_PARAM_ADJUST` 节）

| 项 | 默认 | 说明 |
|---|---|---|
| `MaxConsecutiveFailures` | 5 | 最大允许连续失败次数，达到即触发 `AbortRecordRequested` 并转失败事件 |
| `SegmentDistanceMm` | 5.0 | 每段距离（mm，1~50）：累计 `\|ΔrobotX\|` 达此值取段内有效宽度均值查表 |
| ~~`IsCountType` / `CountNum`~~ | — | 2026-11-17 阶段 7 删除；INI 旧键仅保留读取、忽略并记一条 Info |

配置节 `WELD_PARAM_ADJUST`，与 `SEAM_GUIDE` **同属一个配置类** `WeldAlgorithmsConfig`（ADR-043），同存 `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`；
实例与读写器由 [[api/WeldParamManager]] 独占，外部只读（`Manager.AlgorithmsConfig`），改后调 `Manager.SaveAlgorithmsConfig()` 落盘。

---

## 执行流程

```
每帧调用 ExecuteAdjustment(autoParam, robotX, contourPoints)
  ↓ 连续失败 ≥ Config.MaxConsecutiveFailures ?
     是 → 触发 AbortRecordRequested + 触发失败完成事件（返回）
     否 → 继续
  ↓ 宽度来源 = 手动固定 ?
     是 → 用 ManualSeamWidthMm 查表
     否 → 按距离分段：累计 |ΔrobotX| 达 SegmentDistanceMm
          ↓ 段内有效点数 > 0 ?
             是 → 取段内均值 → WeldParamLookupAlgorithm.TryLookupWithSpot → 更新输出，Trigger=true
             否 → 不查表，保持旧输出，交缺值报警（N10）
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
- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] — 算法分层决策
- ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 算法纯净性与记录职责隔离
- ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 焊接算法配置合一（`WeldAlgorithmsConfig`）
- [[lessons/AlgorithmControlRecordIsolation]] — 对应踩坑记录
- [[modules/ProductFileManager]] — 记录订阅方（待办）


## 2026-10-19：⑤工艺输出 5 属性收编（ADR-072 §三②）

`ManualSeamWidthMm` / `SpotWidthGain` / `ParamOutputHz` / `FeedforwardSafetyFactor` / `EnableMonotonicConstraint`
——公开 get/set **转发 `_config`**（WeldAlgorithmsConfig 承载不变：前三键落 ③Adapt、后二键落 ①System，
INI/XML 键与默认值零改动，仅管理归属收编算法层）。UI 侧经 `WeldParamManager` facade 同名透传读写。

## 按距离分段补充（2026-11-17，阶段 7 / ADR-103）

- 新增 `AccumulateSeamWidth(double)`：一帧有效宽度同时进 `SeamCalData` 滑动窗与本段累加器（`_segmentWidthSum` / `_segmentWidthCount`）。
- 新增分段状态 `_segmentTravelMm` / `_lastSegmentRobotX` / `_hasSegmentAnchor`，`Reset()` 一并清零。
- `SegmentDistanceMm` 越界在配置加载时钳位到 1~50 并 Warning；旧键 `IS_COUNT_TYPE`/`COUNT_NUM` 只读忽略。
- 关联：[[decisions/ADR-103-no-value-hold-and-distance-segment]]

