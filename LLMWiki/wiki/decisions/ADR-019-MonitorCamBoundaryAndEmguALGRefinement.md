---
title: ADR-019 监控相机与 EmguALG 现行决策（麦格威三层 · 业务边界 · 五层细化；整合原 007/037/039）
date: 2026-09-09
updated: 2026-10-30
tags: [决策, MonitorCam, EmguALG, 2D相机, 算法架构, MecaVision, merged, ADR-019]
status: accepted
merged_from: [ADR-007, ADR-037, ADR-039]
---

# ADR-019：监控相机与 EmguALG 现行决策（麦格威三层 · 业务边界 · 五层细化；整合原 007/037/039）

> 本页为承继页：整合原 ADR-007（监控相机模块架构）、ADR-034（麦格威三层重构）、ADR-028（业务边界澄清与 EmguALG 五层细化）的**现行裁定**。原两页仅作沿革档案保留，现行结论以本页为准。
> ✅ **合并来源编号已裁定（2026-11-17 治理轮）**：编号唯一准绳 [[decisions/ADR-Index]] 的 ADR-019 行记「整合原 **007/037/039**」，本页 `merged_from` 已按此更正为 `[ADR-007, ADR-037, ADR-039]`。此前正文所写「ADR-007 / ADR-034 / ADR-028」为旧稿笔误——`ADR-034` 在 09-17 表里是「旧034→新024 线激光三层」，与本页无关。

## 沿革时间线

1. **2026-07-13 · 原 ADR-007**：为「自动焊接头监控」新增独立模块 `MonitorCam`，确立独立模块 + SDK 抽象 + Run/Workflow 分离精神。~~其 SmartRay 时代监控架构（Live/PIL 双模式语义、`HikvisionCameraApi` 海康实现、`MonitorCameraRun` 平铺单例、算法集中在 `ImageAlgorithm.cs` 第 8 区）已被整体推翻~~。
2. **2026-09-08 · 原 ADR-034**：监控相机三层重构并切换麦格威（MecaVision）——目录对齐运控（ADR-033/037）与线激光（ADR-007/039）范式，删除海康实现。
3. **2026-09-09 · 原 ADR-028**：业务边界澄清——2D 面阵相机无 Live/PIL 语义；EmguALG 五层细化，RealtimeMonitor / LineLaserContour 归位。

## 背景

- 原 ADR-007 落地时具体 SDK/型号未定，且系统中已存在 SmartRayCam（3D 线激光）、HikRobotCam（2D）、LineLaserWorkflow，监控相机在业务语义上必须相互独立——「独立模块」精神沿用至今。
- 监控相机需求为**焊前**检测激光光斑与焊丝对中、**焊中**检测焊接质量，两项均要求画面输出与结果输出；实际只需要基于 EMGU 的 2D 分析，算法需求曾被过度放大。
- 前期实现引入 Live/PIL 双模式语义（`IsLiveMode`、`ChangeMode`、连续帧回调）属事实错位；EmguALG 目录亦不满足用户要求的五层划分。

## 现行裁定

### 一、监控相机三层结构（对齐运控 / 线激光范式）

```
MonitorCam/
├── IMonitorCam/ # 抽象层 L2：IMonitorCamApi + 枚举 + 事件参数
├── MecaVisionCam/ # 实现层 L3：MecaVisionCam.cs + Native/MVSDK.cs（官方原样）
└── MonitorCamManager.cs # 业务中枢（Lazy 单例），由原 MonitorCameraRun 改名承接
```

1. **麦格威切换**：监控相机 SDK 采用麦格威 MVSDK，**替代原 SmartRay 监控旧实现**；海康实现 `HikvisionCameraApi.cs` 与 csproj 中 `MvCameraControl.Net` 引用一并删除，不保留平行双实现（ADR-007 处置先例）。
2. **实现层只做回调触发**（ADR-028 准则）：`MecaVisionCam` 只负责取帧；阶段语义、健康巡检、配置持久化全归 `MonitorCamManager`。
3. **Manager 单一入口**：`MonitorCamManager` 是监控相机业务唯一入口，对外经 `_api` 转发，业务层不感知 SDK 细节；`MonitorCameraWorkflow` 负责采集 → 分析 → 显示 → 结果编排，与线激光工作流解耦。
4. **命名空间**：抽象层 `AdaWeldSystem.MonitorCam.IMonitorCam`、实现层 `AdaWeldSystem.MonitorCam.MecaVisionCam`，与线激光 `ILineLaser/`、`IntelligentLaserCam/` 命名同构。
5. **部署**：原生库在 `3rdDepend/MecaVision/`（x64 四件套）；平台目标须显式 x64/x86（禁 AnyCPU）。

### 二、2D 面阵相机：无 Live/PIL 业务模式

1. 监控相机为 **2D 面阵相机，不存在 Live/PIL 业务语义**；Live/PIL 模式切换属已废弃的 SmartRay 线激光旧实现（现线激光使用英莱相机，不需要此切换）。所有画面显示均采用「触发采集后刷新 Mat」方式（与线激光手动调试页同构，频率可控）。
2. `IMonitorCamApi` 只保留：连接、断开、单次触发取帧 `CaptureSingleFrame()`、释放。
3. 已删除：`FrameReceived` 事件（对外 API）、`StartAcquisition()` / `StopAcquisition()`、`IsLiveMode`、`ChangeMode`、`MonitorFrameEventArgs`、`FrameCompletedEventArgs.IsLive`；`MonitorCamPage` 删除 `chkLive` 实时预览复选框，画面由单次/连续检测触发后经 `FrameCompletedEvent` 刷新。
4. **取帧路径**（以麦格威官方 Basic/FirstStep 例程为实证）：Init：`CameraSdkInit` → `CameraEnumerateDevice` → `CameraGigeGetIp` 按 IP 匹配（匹配不到回退首台并记日志）→ `CameraInit` → 黑白传感器 `CameraSetIspOutFormat(MONO8)` → `CameraSetTriggerMode(0)` → 挂回调；取帧：`CameraGetImageBuffer` → `CameraImageProcess` → `CameraFlipFrameBuffer`（SDK 输出自底向上）→ 建 `Mat` 并 `Clone` 出独立副本 → **必须 `CameraReleaseImageBuffer`**。
5. **SDK 关键坑**：回调委托必须持字段引用（`_snapProc`/`_connProc`），否则 GC 后回调崩溃；`CameraHandle` 在 MVSDK.cs 中是文件级 using 别名，消费方须自行声明 `using CameraHandle = System.Int32;`。
6. 单次触发任务由 Task 自行结束，`MonitorCamManager.SensorStop()` 为空实现（保留方法仅兼容既有调用方）。

### 三、算法统一走 EmguALG，五层细化

```
EmguALG/
├── Abstractions/ # IAlgorithm / IConfigurableAlgorithm / IResultStore
├── Core/ # AlgorithmBase / AlgorithmResult / 算子枚举 / 预处理配置
├── RealtimeMonitor/ # 在线检测算法实现
│ ├── WireFeedDistance/ # 焊丝距离检测
│ └── WeldQuality/ # 焊接质量检测
├── LineLaserContour/ # 线激光轮廓 Mat 渲染（ILineLaserContourAlgorithm / LineLaserContourAlgorithm）
└── Manager/ # AlgorithmManager 统一调度入口
```

1. **算法统一入口**：所有算法调用统一走 `EmguALG.Manager.AlgorithmManager`，外部调用入口唯一；不再使用原「算法集中在 `ImageAlgorithm.cs` 第 8 区」的做法。
2. **RealtimeMonitor 归位**：监控相机的在线检测算法（焊丝距离检测 `DetectWireFeed`、焊接质量检测 `DetectWeldQuality`）实现归 `EmguALG.RealtimeMonitor/`，仅此两种 2D 分析，不复用线激光基础视觉链路。
3. **LineLaserContour 归位**：线激光轮廓 Mat 渲染从 `LineLaserManager.ProfileMatRenderer` 上提为 `EmguALG.LineLaserContour.LineLaserContourAlgorithm`，`LineLaserManager` 通过 `ILineLaserContourAlgorithm` 接口调用——显示渲染与采集/识别职责解耦（符合 ADR-007 算子库统一与职责下沉原则）。
4. **算法职责边界**：监控相机只消费 `DetectWireFeed` / `DetectWeldQuality`，不消费线激光轮廓/点云算法。
5. **配置**：监控相机配置归 `Config/INI/MonitorCamera.ini`（ADR-005）；枚举与事件参数统一放入 `Comm/SystemComm.cs`（复用全局通讯中心，避免新建冗余全局类）。（**2026-09-21 演进**：路径按 [[decisions/ADR-033-ConfigArchitectureStandard]] 三段式迁至 `Config/MonitorCam/Monitor_INI/MonitorCamera.ini`）
6. **工程约束（沿承原 007 仍有效部分）**：事件参数类级复用，高频事件避免 GC 压力（CSharpStyle）；UI 页 `Sub2UI/MonitorCamPage` 订阅 `FrameCompletedEvent` 与 Workflow 事件，全部检查 `InvokeRequired`（WinForms-UI-Threading）；资源释放用 `DisposeComponents()` 公共方法，禁止重写 `Dispose(bool)`（ADR-001）。

## 被推翻的中间态（沿革档案）

- ~~原 ADR-007 的 SmartRay 时代监控架构~~：Live/PIL 双模式语义（`IsLiveMode`/`ChangeMode`/连续帧回调）、`HikvisionCameraApi` 海康实现、`MonitorCameraRun` 平铺业务单例、算法集中在 `ImageAlgorithm.cs` 第 8 区——均已被上列现行裁定取代。
- ~~原 ADR-034 备选方案 B~~：按二手文档新建 `MonitorCamera/` 平行模块（与独立模块原则冲突，产生两套监控相机体系，否决）；~~备选方案 C~~：保留海康作为第二实现（否决）。
- ~~早期 `MonitorCameraSimulator` 合成帧占位~~：SDK 确定后已删除整个模拟部分，仅保留真实实现（无 `UseRealCamera` 开关）。

## 后果

- 正面：三层心智与运控、线激光完全一致，换厂商只动实现层目录；业务语义与 2D 面阵硬件一致，消除 SmartRay 遗留模式污染；EmguALG 外部调用入口唯一；麦格威官方 C# 封装原样复用（无需自写 DllImport），`CameraGigeGetIp` 关闭「枚举期无法按 IP 匹配」OPEN 项；抽象层零实现依赖。
- 负面 / 遗留：消费方 `MonitorCameraWorkflow`、`MonitorCamPage` 曾需同步改名（已完成）；真编译待 Visual Studio（Python 静态校验已通过：命名空间一致、csproj 注册一致、无残留 Live/PIL 业务符号）；OPEN：① 平台目标与现场相机形态（GigE/USB3）待确认 ② 曝光/增益等参数接口尚未接入 ③ `MonitorCamConfig.Port` 字段麦格威不使用，保留仅为兼容历史 INI。

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[modules/MonitorCam]]、[[modules/EmguALG]]
- [[api/MonitorCamManager]]、[[api/MonitorCameraWorkflow]]、[[api/AlgorithmManager]]
- [[api/MecaVisionMVSDK-Native]] —— 麦格威原生 API 速查
- [[guides/MecaVision-DevGuide]] —— 开发指导与实施 plan
- [[decisions/ADR-022-EmguALGThreeLayer]]、[[decisions/ADR-024-LineLaserThreeLayerRefactor]]、[[decisions/ADR-003-EnumDeduplication]]
- ADR-002（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[decisions/ADR-018-CallbackAcquisition]]、ADR-033（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）
- [[guides/Namespace-Compilation]]、[[guides/WinForms-UI-Threading]]、[[guides/WinForms-Designer]]、[[guides/Project-Tools]]
- ADR-007-MonitorCameraModule（已并入本页，沿革档案）
- ADR-034-MecaVisionMonitorCamera（已并入本页，沿革档案）
