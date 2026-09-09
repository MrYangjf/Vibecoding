---
title: MonitorCam 模块 — 自动焊接头监控相机（三层：IMonitorCam / MecaVisionCam / MonitorCamManager）
date: 2026-08-03
tags: [模块, 相机, 监控, 焊前对中, 焊中质检, MecaVision, 三层架构]
source: raw/knowledge/AdaWeldSystem_Wiki.md (新增)
---

# MonitorCam 模块 — 自动焊接头监控相机

> 独立监控相机模块：负责焊前激光光斑/焊丝对中检测、焊中焊接质量检测，两者均具备画面输出与结果输出。
> **2026-09-08 三层重构 + 厂商切换（ADR-041 accepted）**：抽象层 `IMonitorCam/`、实现层 `MecaVisionCam/`（麦格威 MVCAMSDK）、业务中枢 `MonitorCamManager.cs`，参照 MotionControl 与线激光范式；**海康实现已删除**。

## 核心文件（三层目录）

| 层 | 文件 | 职责 |
|---|---|---|
| 抽象层 | `MonitorCam/IMonitorCam/IMonitorCamApi.cs` | 相机契约（连接/采集/Live-PIL/帧回调） |
| 抽象层 | `MonitorCam/IMonitorCam/MonitorCamType.cs` | 3 枚举：`MonitorCameraConnectionState` / `MonitorCameraPhase` / `MonitorSupervisionState` |
| 抽象层 | `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs` | 3 事件参数：监督状态变更 / 帧 / 帧完成 |
| 实现层 | `MonitorCam/MecaVisionCam/MecaVisionCam.cs` | **麦格威实现**：只取帧并抛 `FrameReceived`，不做业务判断 |
| 实现层 | `MonitorCam/MecaVisionCam/Native/MVSDK.cs` | 官方原样封装（6885 行静态类 `MvApi`，按进程位数动态加载原生库） |
| 业务层 | `MonitorCam/MonitorCamManager.cs` | **对外唯一入口（Lazy 单例）**：连接编排、模式切换、帧分发、健康巡检 |
| 配置 | `MonitorCam/MonitorCamConfig.cs` | 硬件配置（IP/端口/曝光/尺寸），持久化 `Config/INI/MonitorCamera.ini` |
| 工作流 | `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` | 采集→分析→显示→结果，继承 `DeviceWorkflowBase` |

> **已删除文件（勿再引用）**：`MonitorCam/Api/IMonitorCameraApi.cs`（现役 `IMonitorCam/IMonitorCamApi.cs`）、`MonitorCam/Api/HikvisionCameraApi.cs`（海康实现删除）、`MonitorCam/MonitorCameraRun.cs`（改名承接为 `MonitorCamManager.cs`）、`MonitorCam/AlgorithmManager.cs`（算法参数并入 `EmguALG/Manager/AlgorithmManager.cs`）。
>
> ⚠️ **命名空间=类名同形规约（2026-09-09，CS0118 真编译暴露）**：实现层命名空间 `AdaWeldSystem.MonitorCam.MecaVisionCam` 与类名 `MecaVisionCam` 同形（线激光 `LineLaserCam.IntelligentLaserCam` 先例同构）。**实例化必须写 `new MecaVisionCam.MecaVisionCam()`（命名空间.类名限定）**，裸名会被解析为子命名空间报 CS0118。

## 职责分工

| 关注点 | 承载者 | 位置 |
|---|---|---|
| 连接编排、帧分发、健康巡检、配置 | `MonitorCamManager` | `MonitorCam/MonitorCamManager.cs` |
| 取帧与回调触发（Live/PIL） | `MecaVisionCam` | `MonitorCam/MecaVisionCam/MecaVisionCam.cs` |
| 检测阶段枚举 | `MonitorCamPhase` | `MonitorCam/IMonitorCam/MonitorCamType.cs` |
| 连接态 + 焊接过程态 + 执行步 | `MonitorCameraWorkflow` | `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` |

> **权责边界（ADR-027）**：流程只输出「进度」，图像/连接态/健康度由 `MonitorCamManager` 输出（`FrameCompletedEvent` / `StatusChanged`），算法结果由流程以只读属性暴露。细则见 [[standards/WorkflowResponsibilityBoundary]]。

## 回调等待取图机制

`MonitorCamManager.SensorRunContinue()` 触发一次采集（PIL 模式）
└── `MecaVisionCam.CaptureSingleFrame()` 同步返回帧（`CameraGetImageBuffer` → `CameraImageProcess` → `CameraFlipFrameBuffer` → 建 Mat → `CameraReleaseImageBuffer`）
      ├── 写入 `CurrentMat`，`LastAcquisitionSuccess = true/false`
      └── `AcquisitionCompletedSignal.Set()`  // 通知 Workflow 等待线程

> Live 模式（`ChangeMode(true)`）经 `CameraSetCallbackFunction` + `CameraPlay` 持续触发 `FrameReceived` → `FrameCompletedEvent`，**不参与 Workflow 回调流程**。

## 关键属性（MonitorCamManager）

| 属性 | 类型 | 说明 |
|------|------|------|
| AcquisitionCompletedSignal | AutoResetEvent（readonly） | Workflow 等待的回调信号 |
| CurrentMat | Mat | 当前帧（lock 保护） |
| LastAcquisitionSuccess | bool | 最近一次采集是否成功 |
| IsLiveMode | bool | 是否实时预览模式 |
| ConnectionState | MonitorCameraConnectionState | 连接状态 |
| SupervisionState | MonitorSupervisionState | 健康巡检状态（Idle/Checking/Healthy/Degraded/Error） |
| Config | MonitorCamConfig | 硬件配置（IP/端口/曝光/尺寸） |

## 与外部模块关系

- **算法**：经 [[modules/EmguALG]] 的 `AlgorithmManager.Instance.DetectWireFeed/DetectWeldQuality` 调用（原为直调 `ImageAlgorithm`，ADR-042 后统一走 Manager）
- **算法参数**：由 `EmguALG/Manager/AlgorithmManager` 持有强类型配置（`WireFeedConfig` / `WeldQualityConfig`），持久化 `Config/INI/MonitorAlgorithm.ini`
- **UI**：由 [[modules/UIDesign]] 的 `Sub2UI/MonitorCamPage` 页面驱动与展示（27 处引用点已同步改名）
- **解耦**：单向依赖 `Comm`（日志）与 `EmguALG`；不反向依赖工作流
- **配置**：INI 落盘遵循 [[decisions/ADR-007-ConfigLayout]]

## 相机实现（MecaVisionCam）— 2026-09-08 落地

麦格威 MVCAMSDK（C# 封装 `MvApi` 动态加载原生 `MVCAMSDK.dll` / `MVCAMSDK_X64.dll`）。实现要点（均以官方 Basic/FirstStep 例程为实证）：

1. `Connect(ip,port)`：`CameraSdkInit` → `CameraEnumerateDevice` → **`CameraGigeGetIp` 按 IP 匹配**（未匹配回退首台并记日志）→ `CameraInit` → 黑白传感器设 `CameraSetIspOutFormat(MONO8)` → `CameraSetTriggerMode(0)` 连续采集 → 挂断联回调。
2. Live：`CameraSetCallbackFunction` + `CameraPlay`；回调内 `CameraFlipFrameBuffer`（SDK 输出自底向上）→ 建 Mat → `Clone` 独立副本 → 抛 `FrameReceived`。
3. PIL：`CameraGetImageBuffer` → `CameraImageProcess` → `CameraFlipFrameBuffer` → 建图 → **必须 `CameraReleaseImageBuffer`**。
4. 坑位：回调委托必须持引用防 GC；`CameraHandle` 在 MVSDK.cs 是**文件级 using 别名**，消费方须自行声明。
5. 部署：原生库已拷入 `3rdDepend/MecaVision/`（x64 四件套）；平台目标须显式 x64/x86。
6. 完整 API/错误码/取帧配方见 [[api/MecaVisionMVSDK-Native]] 与 [[guides/MecaVision-DevGuide]]。

> 历史：早期曾用 `MonitorCameraSimulator` 占位、随后为海康 `HikvisionCameraApi`；2026-09-08 切麦格威并删除海康实现与 `MvCameraControl.Net` 引用。

## 设计决策

- [[decisions/ADR-041-MecaVisionMonitorCamera]]：**三层重构 + 切换麦格威 + 删除海康**（accepted）
- [[decisions/ADR-042-EmguALGThreeLayer]]：算法模块三层改造（输入源即本模块）
- [[decisions/ADR-009-MonitorCameraModule]]：SDK 抽象、完全解耦、Live/PIL 双模式
- [[decisions/ADR-005-CallbackAcquisition]]：复用回调等待取图模式
- [[decisions/ADR-007-ConfigLayout]]：配置文件归入 Config/INI/

## 相关教训

- [[guides/Namespace-Compilation]]：7 个 MonitorCam 文件已注册到 .csproj
- [[guides/WinForms-UI-Threading]]：UI 事件处理均检查 InvokeRequired
- 真编译待 Visual Studio（本环境无 C# 编译器），改动以 Python 静态校验（14/14）替代

---

*来源：用户需求「自动焊接头监控模块」+ 本模块源码（AdaWeldSystem/MonitorCam/）*
