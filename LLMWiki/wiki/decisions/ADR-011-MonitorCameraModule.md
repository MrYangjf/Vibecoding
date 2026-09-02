---
title: ADR-011 监控相机模块架构决策
date: 2026-07-13
tags: [决策, 相机, 监控, 解耦, SDK抽象]
status: accepted
source: 用户需求「自动焊接头监控模块」+ 本模块设计
---

# ADR-011：监控相机模块架构决策

## 背景

新增「自动焊接头监控」功能，需在**焊前**检测激光光斑与焊丝对中、**焊中**检测焊接质量，两项均要求**画面输出**与**结果输出**。
此时具体监控相机 SDK/型号尚未确定，且系统中已存在 SmartRayCam（3D 线激光）、HikRobotCam（2D）、LineLaserWorkflow（线激光工作流），监控相机在业务语义上相互独立。

## 决策

1. **新增独立模块 `MonitorCam`**，不直接挂载到既有 SmartRayCam / HikRobotCam / LineLaserWorkflow。
2. **SDK 抽象为 `IMonitorCameraApi` 接口**（位于 `MonitorCam/Api/`），参考 SmartRay Sensor API 风格（连接 / 采集 / Live-PIL 模式 / 帧回调）。当前实现为 `HikvisionCameraApi`（海康面阵相机 MvCameraControl.Net SDK）；如需更换相机厂商，新增实现该接口的类并在 `MonitorCameraRun` 中替换底层实例即可，业务代码零改动。
3. **运行控制与业务流分离**：
   - `MonitorCameraRun`（单例，IDisposable）：仅负责设备连接、Live/PIL 模式、采集完成信号（`AcquisitionCompletedSignal`，AutoResetEvent），复用 [[decisions/ADR-005-CallbackAcquisition]] 回调等待模式。
   - `MonitorCameraWorkflow`（单例，状态机）：负责 采集 → 分析 → 显示 → 结果 编排，与 `LineLaserWorkflow` 完全解耦。
4. **算法集中在 `EmguALG/ImageAlgorithm.cs` 第 8 区**（焊前对中 `DetectPreWeldAlignment`、焊中质检 `DetectWeldQuality`），遵循 [[decisions/ADR-003-SingleAlgorithmFile]]。
5. **配置归入 `Config/INI/MonitorCamera.ini`**，遵循 [[decisions/ADR-008-ConfigLayout]]。
6. **枚举与事件参数统一放入 `Comm/SystemComm.cs`**（复用既有全局通讯中心，避免新建冗余全局类）。

## 关键设计

- `MonitorCameraRun` 持有 `private readonly IMonitorCameraApi _api = new HikvisionCameraApi();`，所有对外方法经 `_api` 转发，业务层不感知 SDK 细节。
- `MonitorCameraWorkflow.Start(phase, continuous)`：`continuous=true` 走 do-while 连续循环；`AcquireImage` 通过 `AcquisitionCompletedSignal.WaitOne(5000)` 等待回调（Live 模式不触发信号，见 [[guides/Project-Tools]]）。
- 事件参数类级复用，高频事件避免 GC 压力（遵循 CSharpStyle）。
- UI 页 `Sub2UI/MonitorCamPage` 订阅 `FrameCompletedEvent` 与 Workflow 五大事件，全部检查 `InvokeRequired`（见 [[guides/WinForms-UI-Threading]]）。
- 资源释放使用 `DisposeComponents()` 公共方法，禁止重写 `Dispose(bool)`（见 [[decisions/ADR-001-DisposePattern]] 与 [[guides/WinForms-Designer]]）。

## 后果

- 优点：监控相机功能完全独立，不影响既有相机/工作流；SDK 替换成本低（仅新增实现类并在 `MonitorCameraRun` 切换）。
- 代价：多一层抽象与单例状态管理；真实 SDK 接入需补充帧格式适配与参数映射（已通过 `HikvisionCameraApi` 完成）。
- 历史：早期以 `MonitorCameraSimulator` 占位生成合成帧用于离线联调；SDK 确定后已删除整个模拟部分，仅保留 `HikvisionCameraApi` 真实实现（无 `UseRealCamera` 开关）。

## 涉及约束

- [[decisions/ADR-001-DisposePattern]] ✅
- [[decisions/ADR-003-SingleAlgorithmFile]] ✅
- [[decisions/ADR-005-CallbackAcquisition]] ✅
- [[decisions/ADR-008-ConfigLayout]] ✅
- [[guides/Namespace-Compilation]] ✅（6 个文件已注册 .csproj）
- [[guides/WinForms-UI-Threading]] ✅
- [[guides/Project-Tools]] ✅
- [[guides/WinForms-Designer]] ✅

---

*来源：AdaWeldSystem/MonitorCam/ 模块源码 + 用户需求文档*
