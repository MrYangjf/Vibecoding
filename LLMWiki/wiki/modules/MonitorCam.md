---
title: MonitorCam 模块 — 自动焊接头监控相机
date: 2026-08-03
tags: [模块, 相机, 监控, 焊前对中, 焊中质检]
source: raw/knowledge/AdaWeldSystem_Wiki.md (新增)
---

# MonitorCam 模块 — 自动焊接头监控相机

> 新增独立监控相机模块：负责焊前激光光斑/焊丝对中检测、焊中焊接质量检测，两者均具备画面输出与结果输出。
> 设计上与 SmartRayCam / HikRobotCam / LineLaserWorkflow **完全解耦**——底层 SDK 通过 `IMonitorCameraApi` 抽象，当前实现为 `HikvisionCameraApi`（海康面阵相机，MvCameraControl.Net SDK）。

## 核心文件

| 文件 | 职责 |
|------|------|
| `MonitorCam/Api/IMonitorCameraApi.cs` | 监控相机 SDK 抽象接口（连接/采集/Live-PIL 模式/帧回调），参考 SmartRay Sensor API 风格 |
| `MonitorCam/Api/HikvisionCameraApi.cs` | **海康面阵相机真实实现**：基于 MvCameraControl.Net SDK，满足 `IMonitorCameraApi` 契约。详细用法见 [[api/HikvisionCameraSDK]] |
| `MonitorCam/MonitorCameraRun.cs` | **运行控制单例（2026-08-03 合并）**：Live/PIL 模式 + 采集完成信号，解耦具体 SDK。内含 `MonitorCameraConfig` 配置类（IP/端口/曝光/尺寸，持久化到 `Config/INI/MonitorCamera.ini`）和 `MonitorCameraFrameCompletedEventArgs` 帧完成事件参数。原独立文件 `MonitorCameraConfig.cs` 和 `MonitorCameraEventArgs.cs`（已移除） 已合并入本文件 |
| `MonitorCam/MonitorAlgorithmManager.cs` | 监控相机算法管理器（单例）：持有唯一一套可配置算法参数（对中容差/质量合格分），持久化到 `Config/INI/MonitorAlgorithm.ini`，无 JOB 切换（参见 [[api/MonitorAlgorithmManager]]） |
| `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` | **监控相机工作流单例**：采集→分析→显示→结果，复用回调等待取图（ADR-005）。继承**非泛型** `DeviceWorkflowBase`，对外暴露连接态 `SubDeviceState` + 焊接过程态 `SubDeviceWeldStatus`，内部分支用私有阶段枚举 |

> **已删除文件（勿再引用）**：`MonitorCam/Api/MonitorCameraStateMachine.cs`（现役 `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs`）（监控相机状态机）随 `DeviceStateMachine/` 目录整目录删除；`Workflow/` 目录同期删除，工作流已迁入 `MainDeviceControl/DeviceWorkflow/`。

### 重组要点

- **`MonitorCameraConfig` 和 `MonitorCameraEventArgs` 合并入 `MonitorCameraRun.cs`**：运行控制、配置、事件参数三个紧密相关的类合并为一个文件。
- **`MonitorCameraWorkflow` 迁入 `MainDeviceControl/DeviceWorkflow/`**（2026-08-28）：工作流统一由 `MainDeviceControl` 承载，`MonitorCam` 模块只保留相机硬件层和算法管理层。
- **健康巡检下沉到 `MonitorCameraRun`**：不再作为独立工作流，也不并入工作流线程；`MonitorCameraPhase` / `MonitorSupervisionState` 枚举保留在 `MonitorCam/Api/` 接口层。

## 监控相机设备状态（当前事实：三态模型）

> 独立的监控相机状态机文件**不存在**：`DeviceStateMachine/` 目录、`DeviceStateMachineBase` 基类、`MonitorCameraStateMachine` 均已删除。监控相机的状态由工作流承载——对外只暴露**连接态 `SubDeviceState`** 与**焊接过程态 `SubDeviceWeldStatus`**，内部分支用**私有阶段枚举**（7 态，已删 `Displaying`）。详见 [[architecture/DeviceControlArchitecture]]、[[modules/DeviceControl]]。

**职责分工**：

| 关注点 | 承载者 | 位置 |
|---|---|---|
| 相机运行、健康巡检、帧数据 | `MonitorCameraRun` | `MonitorCam/MonitorCameraRun.cs`（健康巡检下沉于此，非工作流） |
| 检测阶段（`MonitorCameraPhase`：Unknown / PreWeldAlignment / WeldQuality） | `MonitorCam/Api/` 接口层 | `MonitorCam/Api/IMonitorCameraApi.cs` |
| 连接态 + 焊接过程态 + 执行步 | `MonitorCameraWorkflow` | `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` |

> 私有阶段 → `SubDeviceWeldStatus` 的映射表见 [[architecture/DeviceControlArchitecture]] §6（**唯一维护点**，本页不复制，避免两处漂移）。

> **权责边界（ADR-027）**：流程只输出「进度」，图像/连接态/健康度由 `MonitorCameraRun` 输出（`FrameCompletedEvent` / `StatusChanged`），算法结果由流程以只读属性 `LastResult` 暴露。执行细则见 [[standards/WorkflowResponsibilityBoundary]]。

## 回调等待取图机制

`MonitorCameraRun.SensorRunContinue()` 触发一次采集（PIL 模式）
└── `HikvisionCameraApi.CaptureSingleFrame()` 同步返回帧
      ├── 写入 `CurrentMat`，`LastAcquisitionSuccess = true/false`
      └── `AcquisitionCompletedSignal.Set()`  // 通知 Workflow 等待线程

> Live 模式（`ChangeMode(true)`）通过 `HikvisionCameraApi` 实时采集回调持续触发 `FrameReceived` → `FrameCompletedEvent`，**不参与 Workflow 回调流程**。参见 [[guides/Project-Tools]]。

## 工作流阶段（私有，不对外）

**私有阶段枚举** `MonitorWorkflowState`，内联于 `MonitorCameraWorkflow.cs` 文件尾（**不再定义于 `Comm/SystemComm.cs`**），仅驱动 `FlowProcess()`；对外统一映射为焊接过程态 `SubDeviceWeldStatus`（映射表见 [[architecture/DeviceControlArchitecture]] §6 单一维护点）。

| 阶段 | 说明 |
|------|------|
| Uninitialized | 未初始化 |
| Standby | 待机（已连接，等待启动） |
| Acquiring | 采集中（回调等待信号） |
| Analyzing | 分析中（调用 `ImageAlgorithm` 算法） |
| Completed | 完成（单次循环结束，回到 Standby） |
| ErrorAborted | 异常终止（采集/分析失败或异常） |
| ManualStopped | 手动停止 |

> 旧 `Displaying` 态已删除——显示属 UI 职责，不在流程态中（[[standards/WorkflowResponsibilityBoundary]] R5）。

流程：`AcquireImage → AnalyzeImage → TriggerDisplay → TriggerResult`（连续模式 do-while 循环）。
检测阶段由 `MonitorCameraPhase`（Unknown / PreWeldAlignment / WeldQuality）区分。

## 关键属性（MonitorCameraRun）

| 属性 | 类型 | 说明 |
|------|------|------|
| AcquisitionCompletedSignal | AutoResetEvent（readonly） | Workflow 等待的回调信号 |
| CurrentMat | Mat | 当前帧（lock 保护） |
| LastAcquisitionSuccess | bool | 最近一次采集是否成功 |
| IsLiveMode | bool | 是否实时预览模式 |
| ConnectionState | MonitorCameraConnectionState | 连接状态 |
| Config | MonitorCameraConfig | 配置（IP/端口/曝光/尺寸/算法阈值）— 内嵌于本文件 |

## 与外部模块关系

- **算法**：调用 [[modules/EmguALG]] 的 `ImageAlgorithm.DetectPreWeldAlignment` / `DetectWeldQuality`（位于文件第 8 区，符合 [[decisions/ADR-003-SingleAlgorithmFile]]）
- **算法参数管理**：`MonitorCameraWorkflow.AnalyzeImage()` 统一从 `MonitorAlgorithmManager.Instance` 读取 `AlignmentConfig` / `QualityConfig`（单一可配置算法，持久化到 `Config/INI/MonitorAlgorithm.ini`，无 JOB 切换），实现算法配置与相机硬件配置分离（参见 [[api/MonitorAlgorithmManager]]）
- **UI**：由 [[modules/UIDesign]] 的 `Sub2UI/MonitorCamPage` 页面驱动与展示
- **解耦**：不引用 SmartRayCam / HikRobotCam / LineLaserWorkflow，单向依赖 `Comm`（枚举/事件参数）与 `EmguALG`
- **并行工作流**：与 [[modules/DeviceControl]] 的 `LineLaserWorkflow` 同为回调等待取图模式（[[decisions/ADR-005-CallbackAcquisition]]），但完全解耦；状态机对比见 [[api/MonitorCameraWorkflow]]
- **配置**：INI 落盘遵循 [[decisions/ADR-007-ConfigLayout]]（路径 `Config/INI/MonitorCamera.ini`）

## 设计决策

- [[decisions/ADR-009-MonitorCameraModule]]：监控相机模块架构（SDK 抽象、完全解耦、Live/PIL 双模式）
- [[decisions/ADR-005-CallbackAcquisition]]：复用回调等待取图模式
- [[decisions/ADR-003-SingleAlgorithmFile]]：算法集中在 ImageAlgorithm.cs
- [[decisions/ADR-007-ConfigLayout]]：配置文件归入 Config/INI/
- [[api/MonitorAlgorithmManager]]：监控相机算法管理器（单一可配置算法，持久化，无 JOB 切换，分离算法与相机配置）

## 相机实现（HikvisionCameraApi）

SDK 已确定（海康 MvCameraControl.Net）。`MonitorCameraRun` 构造函数直接实例化 `HikvisionCameraApi` 作为唯一底层实现，业务/Workflow/UI 代码零改动（契约一致）。实现要点：

1. `Connect(ip,port)`：枚举设备 → 按 GigE `nCurrentIp` 匹配 IP → `CreateDevice` → `OpenDevice` → GigE 探测最优包大小 → 连续采集 + 关触发。
2. Live 模式：`RegisterImageCallBackEx_NET` + `StartGrabbing`，回调中 `Clone` 出独立 `Mat` 经 `FrameReceived` 上行。
3. 单帧（PIL）：`GetImageBuffer_NET` + `FreeImageBuffer_NET`，按需临时启停抓取。
4. 依赖：托管 `MvCameraControl.Net.dll`（已复制到 `Libs/MvCameraControl/`，CopyLocal）；原生 `MvCameraControl.dll` 由 MVS 运行时提供（见 [[guides/Project-Tools]]）。
5. 完整 API 用法/像素格式转换/参数设置见 [[api/HikvisionCameraSDK]]。

> 历史说明：早期曾以 `MonitorCameraSimulator` 占位生成合成帧用于离线联调与 UI 演示；SDK 确定后已删除整个模拟部分（模拟器类、`SimParams`/`UseRealCamera` 配置、UI 模拟调试区），仅保留真实相机实现。

## 相关教训

- [[guides/Namespace-Compilation]]：6 个 MonitorCam 文件已注册到 .csproj
- [[guides/WinForms-UI-Threading]]：UI 事件处理均检查 InvokeRequired
- [[guides/Project-Tools]]：Live 模式不触发 AcquisitionCompletedSignal
- [[guides/WinForms-Designer]]：MonitorCamPage 使用 `DisposeComponents()`，未重写 `Dispose(bool)`
- [[guides/Project-Tools]]：托管 DLL 引用可编译，但原生 MvCameraControl.dll 须由 MVS 运行时提供（PATH/输出目录），Dev 包不含原生 DLL

---

*来源：用户需求「自动焊接头监控模块」+ 本模块源码（AdaWeldSystem/MonitorCam/）*