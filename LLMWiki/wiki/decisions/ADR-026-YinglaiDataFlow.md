---
title: ADR-026 英莱线激光数据流架构 — CamRun 分发 + Running 单态监听调整
date: 2026-08-18
tags: [决策, 线激光, 英莱, 数据流, ScottPlot, Running态]
status: accepted
previous_id: ADR-029
---

# ADR-026 英莱线激光数据流架构 — CamRun 数据分发 + Running 单态监听调整

> **架构**：纯英莱线激光架构（SmartRay V2 已完全舍弃，旧版本见 backup）
> **核心变革**：CamRun 层成为数据分发中心，工作流 Running 单态内完成监听+调整

## 背景

V2 架构基于 SmartRay 相机，采用 **工作流驱动的取图→分析→调整循环**：

```
工作流线程 → AcquireImage(WaitOne 等帧) → AnalyzeImage(算法) → Display → Adjust → Completed → 下一轮
```

切换到英莱线激光相机后，SDK 的 MillionOutline 回调模式为**持续回调**——相机打开后一直输出轮廓+算法结果，工作流不再需要主动取图和分析。V2 的「主动取图→等帧→算法分析」流程与英莱相机的工作方式不匹配。

因此，V2 架构已完全舍弃（旧版本通过 backup 留存），代码库只保留英莱架构实现。

同时，主页面轮廓 ScottPlot 显示和数据记录也需要重新设计：
- 轮廓显示应直接由 CamRun 回调驱动（事件+跨线程），而非走工作流显示事件
- 数据记录应直接在 CamRun 回调中接入，跟随回调帧率不做锁帧

## 决策

### 决策1：CamRun 层为数据分发中心

**选择**：`IntelligentLaserCameraRun` 在 MillionOutline 回调中完成数据产出后，直接分发给两个出口：
1. **UI 显示**：触发 `ContourDataReady` 事件（携带 PointCloudData + IlInspectResult + 帧率）
2. **数据记录**：调用 `RunRecordManager.Instance.AddFrame(cloud)`

**帧率策略**：完全跟随英莱回调（默认 ~60Hz），不做节流/锁帧。AddFrame 内部 `_isRecording=false` 时零开销。

**理由**：
- 数据分发是传感器层的职责，不应由工作流中转
- 显示和记录是独立数据流，解耦后可独立演进
- 回调线程是数据的第一接触点，延迟最低

### 决策2：Running 单态 — 监听 + 调整一体化

**选择**：工作流只有 **Running 一个运行态**，Running 内部同时完成「监听结果码 + 执行自动调整」：

```
Starting → Running（后台线程 + SDK回调线程 双线程协作）
  ├─ 回调线程：ContourDataReady → ParseRes==1 → 上报SeamFeature → 置位调整请求
  ├─ 工作线程：轮询调整请求 → 执行RunAutoAdjust → 继续监听
  ├─ 连续失败超限 → ErrorAborted
  └─ 行程结束 → ManualStopped（触发WorkflowCompleted事件）
```

**关键设计**：
- **调整是 Running 内部动作，不发生状态跳转**（不再 Running↔Adjusting↔Completed 循环）
- 回调线程仅更新线程安全字段 + 置位标志，不直接操作工作流状态
- 工作流线程轮询标志 + 执行调整，保证状态操作单线程化

**理由**：
- 英莱 SDK 内置算法，工作流不需要也不应该再跑图像分析
- 工作流的核心职责是结果判定+调整执行，而非数据获取与分析
- 单 Running 态更符合「线激光一直运行」的物理语义，状态机更简洁
- 调整动作是高频事件（每帧有效都触发），作为独立状态不合理

### 决策3：ScottPlot Signal 模式高性能轮廓显示

**选择**：主页面轮廓图采用 ScottPlot 4.1.74 Signal 模式：
- 固定 `double[1920]` 数组存 Z 值（高度），Signal 图直接引用该数组
- 每帧原地修改数组内容 → `Refresh()` 重绘，零内存分配
- 事件触发 + `InvokeRequired` 跨线程封送（项目一贯做法）
- 60Hz 全帧率刷新，不做节流

**Signal vs Scatter**：Signal 采用 Min/Max 降采样渲染，比 Scatter 快 5-20 倍，1920 点 60fps 远低于性能上限。

**理由**：
- 用户明确要求 Signal 模式 + 固定数组 + 60Hz
- Signal 模式是 ScottPlot 实时信号显示的最佳实践
- 与 Emgu ImageBox 对比：Signal 模式渲染纯数学曲线无像素化开销，刷新率更高更稳

## 三层架构图

```
┌─────────────────────────────────────────────────┐
│  UI 层 (MainPage)                               │
│  ScottPlot Signal 轮廓显示                      │
│  (事件订阅 + InvokeRequired + 60Hz 全帧率)      │
└───────────────▲─────────────────────────────────┘
                │ ContourDataReady 事件
┌───────────────┴─────────────────────────────────┐
│  CamRun 层 (IntelligentLaserCameraRun)          │
│  MillionOutline 回调 → 数据分发中心              │
│  ├─→ ContourDataReady 事件 (UI 显示)            │
│  └─→ RunRecordManager.AddFrame (数据记录)       │
│  (完全跟随回调帧率，不锁帧)                      │
└───────────────▲─────────────────────────────────┘
                │ ParseRes 结果码监听
┌───────────────┴─────────────────────────────────┐
│  工作流层 (LineLaserWorkflow)                   │
│  Running 单态：监听 + 调整                       │
│  ├─ 回调线程：更新结果 + 置位调整请求            │
│  └─ 工作线程：轮询请求 + 执行调整 + 失败检测      │
└─────────────────────────────────────────────────┘
```

## 状态机精简

```
Uninitialized → Initializing → Standby → Starting → Running
                                                    ↓
                                              ErrorAborted
                                              ManualStopped → Standby
```

**删除的状态（V2 遗留）**：Acquiring / Analyzing / Display / Adjusting / Completed
- V2 的「取图→分析→显示→调整→完成」五段式循环完全不适用英莱架构
- 调整动作并入 Running 内部，Completed 语义由 ManualStopped + WorkflowCompleted 事件替代

## 后果

### 正面
- **架构清晰**：三层职责分明（数据产出/显示/决策执行），符合单一职责
- **性能更优**：Signal 模式 60Hz 流畅显示，记录帧率跟随回调无丢帧
- **状态机简洁**：Running 单运行态，物理语义明确
- **线程安全**：回调线程仅置标志，状态转换在工作流线程执行
- **代码纯净**：无 V2/V3 模式判断，代码库只保留英莱实现

### 负面
- LLCamWorkJob（SmartRay 旧页面）成为历史遗留，功能失效但页面框架保留

### 需注意
- `ContourDataReady` 事件在 SDK 原生线程触发，订阅方必须 `InvokeRequired` 封送
- AddFrame 内部已有 `ClonePointCloud` + `lock`，`_isRecording=false` 时直接返回，空闲零开销
- `_adjustmentPending` / `_lastResultValid` 使用 `volatile` 保证跨线程可见性
- 事件订阅生命周期：`WorkflowLoopWorker` 入口订阅，`finally` 块取消订阅
- 主界面 ScottPlot 的 `Refresh()` 必须与数据更新处于**同一控制流、每帧执行**（2026-08-26 修复：曾误将 `SetAxisLimits`+`Refresh()` 置于「无有效焊缝结果」分支，识别焊缝时整帧不刷新导致轮廓永久冻结）。Signal 模式「每帧原地改数组 → Refresh」的约定不可在分支内打断
- **轴范围「连接时锁定、每帧只刷新数据」**（2026-08-27 细化）：相机连接后校准数据（`CalibrationInfo`）只更新一次，故 `MainPage.IlCamera_ContourDataReady` 的轴范围（`SetAxisLimits`）仅在首次有效校准时执行一次并置 `_contourAxisLocked`，之后（未重连）恒定不变；每帧只 `Refresh()` 重绘轮廓与特征点，不再每帧重设轴范围。`SubscribeContourCamera()` 重订阅时复位锁定标志，重连后重新锁定。与决策3「每帧 60Hz 刷新」不冲突（刷新照常，仅轴范围从每帧重设改为一次锁定）
- **主界面轮廓 Signal 轴映射（Y→X、Z→Y）且 ScottPlot 不平移**（2026-08-27 核对+用户澄清，终版 2026-08-27 改用 AddSignalXY）：`points[i].Z` 作 Signal Y 数据、`points[i].Y` 经 `AddSignalXY` 显式数组（`_contourSignalXs`，非等距）作 X 轴（取代 `SampleRate`/`OffsetX`，后者会隐含等距假设、点序倒序时镜像，见 [[lessons/IntelligentLaser-Pitfalls]] §5.16）；特征点 `_featureXs=FeatureY`、`_featureYs=FeatureZ`。ScottPlot 直接绘原始坐标（负值如实显示），**不做 imageBox 式 `center + y*rate` 平移**（屏幕像素只能取正值才需平移）；两者仅朝向一致、视图不重合属预期。
- **主界面轮廓 Signal 初始不可见（不渲染 Z=0 假轮廓）**（2026-08-27 修复）：`_contourSignalData` 为 `new double[1920]` 全 0，若直接渲染会画出一条 Z=0 的平直假轮廓横跨 X 轴（程序启动未连相机时的「奇怪轮廓」）。故 `AddContourLineChart` 中 `AddSignalXY` 后立即 `_contourSignalPlot.IsVisible = false`；`IlCamera_ContourDataReady` 确认 `pointCount>0` 后首帧置 `true`；`SubscribeContourCamera()` 重订阅/重连复位 `false` 防残留。默认轴范围仍保留呈现「空坐标 + 标签」无数据态（见 [[lessons/IntelligentLaser-Pitfalls]] §5.13）。

## 参考

- [[modules/IntelligentLaserCam]] — 英莱相机模块
- [[modules/DeviceControl]] — 线激光工作流
- [[modules/UIDesign]] — 主页面 ScottPlot
- [[api/IntelligentLaserCam]] — ContourDataReady 事件
- [[api/LineLaserWorkflow]] — Running 单态工作流 API
- [[guides/WinForms-UI-Threading]] — 跨线程 UI 更新规范
- [[guides/Project-Tools]] — ScottPlot.FormsPlot 用法
