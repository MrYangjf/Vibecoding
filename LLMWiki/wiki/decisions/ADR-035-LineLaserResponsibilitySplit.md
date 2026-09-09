---
title: ADR-039 线激光职责再分工与焊缝跟踪 PVT 依赖注入
date: 2026-09-08
status: accepted
tags: [决策, 线激光, 相机, 职责分层, PVT, 依赖注入, 焊缝跟踪, ADR-039]
---

# ADR-039 线激光职责再分工与焊缝跟踪 PVT 依赖注入

## 背景

ADR-038 建成了「L2 抽象 + L3 实现 + 业务层 Manager」三层结构，但**业务仍留在实现层**：
英莱 `MillionOutlineCallback` 一个回调里同时干了六件事——建点云、捕获算法结果、按 `_isManualMode`
分支决定是否生成 Mat、`RunRecordManager.AddFrame` 写产品记录、抛 `ContourDataReady`、
抛 `ContourFrameReady`。由此产生三个问题：

1. **实现层被业务绑死**：换一家相机就得把 Mat 绘制、产品记录、模式分支全部重抄一遍；
2. **双事件通道**：`ContourDataReady`（数据）与 `ContourFrameReady`（显示）并行，
   订阅方要判断「该订哪个」，正是 [[decisions/ADR-023-WorkflowResponsibilityBoundary]] 治理过的反例复现；
3. **业务层空转**：`LineLaserManager` 只转发事件，不承担任何处理，三层结构的收益没有兑现。

同时焊缝跟踪需要在拿到线激光结果后立刻换算 Y 轴 PVT 点并下载，
需要一个明确的**注入面**——直接引用 `MontionManager`（业务层）或 `DeltaMontionControl`（L3）
都会违反 ADR-038 的「业务层只认抽象」铁律。

## 决策

**D1 实现层只做回调触发**
英莱与虚拟相机在产帧回调末尾**只做两件事**：`RaiseResultReady(...)`（结果）+ `RaiseProfileReady(...)`（轮廓）。
Mat 生成、产品记录、模式分支、UI 事件一律移出。删除 `_isManualMode`、`ContourDataReady`、
`ContourFrameReady`、`ContourDataEventArgs` 与约 250 行 GDI 绘制代码。

**D2 抽象层新增两个中性事件与校准载体**
`LineLaserCameraBase` 承载 `ResultReady` / `ProfileReady` 与对应 `Raise*Ready` 保护方法；
新增中性结构 `LineLaserSeamResult`（焊缝结果）与 `LineLaserCalibration`（校准数据），
厂商结构体 `IlInspectResult` / `IlCalibrationInfo` 一并删除——业务层不得感知厂商类型。
校准数据**仍由英莱在 SDK 回调中捕获并存储**，经 `Calibration` 属性供业务层绘制时读取。

**D3 Manager 承担两个业务处理，各自独立**
| 事件 | 处理内容 | 产出 |
|---|---|---|
| `ResultReady` | 缓存结果 → 换算 Y 轴 PVT 点 → 按水位流式下载 | 轴运动；对外转发 `ResultReady` |
| `ProfileReady` | 产品记录 → 更新点缓冲 → **按需**生成 Mat | `Profile` 快照；`MatUpdated` 事件 |

**D4 显示处理默认关闭，接口先行**
`SetDisplayOptions(enabled, fps, convertMat)` + `Config.DisplayEnabled/DisplayFps/ConvertMatEnabled` 三项配置。
理由：UI 显示不必跟随相机帧率，且手动/自动模式需求不同；先留接口，由用户决定何时开启。
Mat 绘制统一走 `ProfileMatRenderer`（画布一次分配、每帧 Clear 后重绘）。

**D5 主页面轮询、手动页订阅**
- `MainPage`：起独立线程按 33ms 节拍读 `LineLaserManager.Instance.Profile`，
  用快照**版本号**判断是否有新帧，只在版本变化时才刷新 ScottPlot——
  ⚠️ 这是对 [[lessons/IntelligentLaser-Pitfalls]]「回调驱动显示非轮询」的**有意识推翻**，
  理由是相机 60~120Hz 而屏幕只需 30Hz，回调驱动会让 UI 线程被高频事件淹没。
- `ILCamPage`：订阅 `MatUpdated` 事件，不再订阅相机私有事件。

**D6 Y 轴以 `IPVTMotion` 注入，不持有控制器**
`LineLaserManager.AttachYAxis(IPVTMotion)` 是唯一注入口，内部转交 `SeamPvtFeeder`。
选 `IPVTMotion` 而非 `MontionAxis` / `MontionManager` 的理由：
① PVT 下载只需 `BeginMove`/`ContinueMove`/`GetInformation` 三个入口；
② `MontionAxis : IPVTMotion` 已把四入口做成 `virtual` 默认实现，未实现的轴返回
`PVTResult.NotSupported`，不会连坐编译；③ 注入控制器或轴配置对象会让线激光模块反向依赖运控业务层。
依赖面是 `AdaWeldSystem.MotionControl.IMotion`（L2 抽象），不触及 L3 厂商类型。
装配点：`MotionControlWorkflow.InitializeOn` 成功后按 `Config.SeamTrackAxisName`（默认「Y轴」）取轴注入。

**D7 PVT 走 B 套流式**
`BeginMove` 起段 → 攒批 → 查 `GetInformation().RemainBufferSize` 水位 → `ContinueMove` 续喂，
结束段置 `isFinal`。依据 [[guides/DeltaEtherCAT-AdvancedMotion]] 结论③：
PCI-L221 无虚拟轴、ECAM2 `SourceType` 只有 0/1，机器人 X→Y 跟随只能走 PVT B 套。

## 备选方案

| 方案 | 放弃理由 |
|---|---|
| 保留 `ContourDataReady`，Manager 直接订阅 | 事件参数带厂商类型 `IlInspectResult`，业务层被绑死；且数据/显示仍双通道 |
| Manager 持有 `MontionManager.Instance` | 违反「业务层只认抽象」；线激光模块反向依赖运控业务层，形成模块环 |
| 注入 `MontionAxis`（含位置/速度） | 当前只需 PVT 三入口，注入面越小越好；需要前馈时再升格，不必提前付代价 |
| 回调逐帧驱动 ScottPlot | 见 D5 理由；且 ADR-027 之后 UI 已统一为「推状态 + 拉数据」范式 |
| 渲染器接口 `IProfileRenderer` 挂回英莱 | 增加一条到 L3 的回调通道，与「实现层只发事件」冲突；绘制参数已中性化为 `LineLaserCalibration` |

## 后果

### 正面
- 实现层从 1746 行降到 1324 行，删除全部 GDI 与业务分支，换相机只需实现两个 Raise；
- 业务集中在 Manager，PVT 链路与显示链路互不干扰，可独立开关；
- Y 轴可测：注入 `null` 或 NotSupported 轴即自动降级，不影响取图与分析。

### 负面 / 待办
- ⚠️ **PVT 时间基准与速度前馈为待实测参数**：当前 Time 取相邻帧实测间隔（相对时间模式）、
  Vel 取位置一阶差分，现场标定后需固化（配置已预留 `PVT/FRAME_SECONDS`）；
- ⚠️ **真编译待 Visual Studio**（沙箱无 C# 编译器）。已跑 50 项 Python 静态校验（非编译）；
- `LineLaserCameraBase.CurrentMat` 语义变为「由 Manager 回写的最近显示帧」，
  实现层不再主动生成；`AcquisitionCompletedSignal` 仍由实现层 Set，契约不变；
- MainPage 新增一条常驻轮询线程，页面销毁时 `StopProfilePolling()` 回收。

## 落地清单

| 项 | 状态 |
|---|---|
| L2 中性类型（`LineLaserSeamResult` / `LineLaserCalibration` / `LineLaserMatEventArgs`） | ✅ |
| 基类两事件 + `Calibration` + `UpdateDisplayMat`，删 `FrameReady` | ✅ |
| 英莱回调瘦身（删 GDI 250 行 / 产品记录 / 模式分支 / 两个私有事件） | ✅ |
| 虚拟相机同步触发两个中性回调 + 简易结果推算 | ✅ |
| 新增 `ProfileSnapshot` / `ProfileMatRenderer` / `SeamPvtFeeder` | ✅ |
| Manager 两个业务处理 + `AttachYAxis` + `SetDisplayOptions` | ✅ |
| 配置新增 PVT/DISPLAY 六项 + `SeamTrackAxisName` | ✅ |
| 消费方改造（工作流 / MainPage 轮询 / ILCamPage 订阅） | ✅ |
| `MotionControlWorkflow` 装配注入点 | ✅ |
| csproj 注册 4 个新文件 | ✅ |
| Python 静态校验 50 项 | ✅ 全过 |
| **真编译** | ⏳ **待 Visual Studio** |
| PVT 时间/速度现场标定 | ⏳ OPEN |

## 关联

- 模块页：[[modules/LineLaserCam]]、[[modules/IntelligentLaserCam]]、[[api/VirtualCam]]
- API 页：[[api/LineLaserManager]]、[[api/IntelligentLaserCam]]
- 上游决策：[[decisions/ADR-034-LineLaserThreeLayerRefactor]]（本 ADR 是其职责补完）、
  [[decisions/ADR-023-WorkflowResponsibilityBoundary]]、[[decisions/ADR-035-LineLaserResponsibilitySplit]]
- 指导页：[[guides/DeltaEtherCAT-AdvancedMotion]]（PVT B 套选型）
- 已推翻的旧结论：[[lessons/IntelligentLaser-Pitfalls]]「回调驱动显示非轮询」（见 D5）
