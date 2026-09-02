---
title: AdaWeldSystem 项目概览
date: 2026-07-01
tags: [项目, 概览, 架构]
---

# AdaWeldSystem 项目概览

> 自适应焊接系统（Adaptive Welding System）是基于 .NET Framework 4.8 + WinForms + AntdUI（MIT，原 SunnyUI 已迁出，见 ADR-021）的工业控制软件。
>
> **定位**：**整个焊接激光头的全面控制软件**——13 个顶层模块，以 `MainDeviceControl` 为设备控制中枢（设备态四态 + 流程态 + 7 个工作流）。模块依赖见 [[architecture/DeviceControlArchitecture]]，设备控制架构见 [[architecture/DeviceControlArchitecture]]。**架构不做 V1/V2/V3 代际区分，只维护当前事实。**

## 技术栈

| 层级 | 技术 |
|------|------|
| 框架 | .NET Framework 4.8（C# 7.3 语法约束） |
| UI | WinForms + AntdUI（MIT，原 SunnyUI 已迁出，见 ADR-021） |
| 3D渲染 | HelixToolkit.Wpf.SharpDX |
| 图像算法 | Emgu.CV（OpenCV .NET 封装） |
| 工业相机 | SmartRay SRAPI + 海康 Mv3dLpNet |
| 数据库 | SQLite |
| 文件配置 | 自研 INIFile 类 |
| 设计模式 | 单例（Lazy<T>）、事件驱动、Step 状态机 |

## 目录结构（2026-08-04 更新）

```
AdaWeldSystem/
├── Comm/                                ← 通讯模块
│   ├── NetworkPort/
│   │   ├── API/                         (INetworkPort, NetworkPortBase)
│   │   ├── Ethernet/                    (TCPIPComm, Profinet/GSDMLGenerator)
│   │   ├── PLC/Siemens/                 (S7PLCCommunication)
│   │   └── Robot/KUKARobot/             (KUKARobotManager, RSI/EKI, ...)
│   ├── CommunicationManager.cs
│   └── SystemComm.cs
├── Config/INI/                          ← 配置文件（INI/XML）
├── MainDeviceControl/                   ← 设备控制核心（2026-08-28 由 DataModels/DeviceStateMachine/Workflow.Device 合并而来，见 ADR-041）
│   ├── DeviceStateApiCore/              (2026-09-01 由 DeviceState/ + FlowState/ 合并：
│   │                                     设备态四态 Disconnect/Connect/Work/Alarm + 流程态基类 + 命令表 + 工作流基类)
│   │                                    ※ 目录合并但命名空间不变，仍为 ...DeviceState / ...FlowState
│   └── DeviceWorkflow/                  (8 个工作流，含 SafetyWorkflow 安全互锁与故障恢复)
├── EmguALG/                             ← 图像算法模块
│   ├── Core/                            (AlgorithmBase, PreprocessConfig, ...)
│   │   └── Attributes/                  (RangeAttribute, UnitAttribute)
│   ├── EmguConfiger/                    (AlgorithmJob, AlgorithmManager, JobManager)
│   ├── RealtimeMonitor/                 (RealtimeMonitorAlgorithm)
│   ├── SeamRecognition/                 (SeamModel, SeamRecognitionAlgorithm)
│   ├── ImageAlgorithm.cs
│   ├── ImageRoiTools.cs
│   └── Stages.cs
├── FileOperate/                         ← 文件操作工具库
│   ├── IniFile.cs
│   ├── Log.cs
│   └── XMLfile.cs
├── LaserWeldHead/                       ← 激光焊接头
│   ├── API/                             (ILaserWeldHeadController)
│   ├── LaserWeldHeadController.cs
│   └── LaserWeldHeadData.cs
├── Libs/                                ← 第三方库（IntelligentLaser, MvCameraControl）
├── LineLaserCam/                        ← 线激光相机族
│   ├── Api/                             (ICameraRun, CameraSelector, LineLaserCameraStateMachine)
│   ├── SmartRayCam/                     (CameraRun, CameraPresetManager, ApiCore/*)
│   ├── VirtualCam/                      (VirtualCameraRun)
│   ├── HikRobotCam/                     (HikCameraRun, ApiCore/*)
│   └── IntelligentLaserCam/             (IntelligentLaserCameraRun)
├── MonitorCam/                          ← 监控相机模块
│   ├── Api/                             (IMonitorCameraApi, HikvisionCameraApi, MonitorCameraStateMachine)
│   ├── MonitorAlgorithmManager.cs
│   └── MonitorCameraRun.cs
├── MotionControl/                       ← 运控调整模块
│   ├── API/                             (IAxis, IIO, IMotionController, MotionControllerBase, IMotionAxisController)
│   ├── MotionManager.cs
│   ├── MoveControlData.cs
│   ├── YAxisController.cs
│   └── MotionControlStateMachine.cs
├── PointCloudData/                      ← 3D 点云处理
│   ├── 3DModel/                         (Point3D, PointCloudData)
│   ├── DataIO/                          (PointCloudReader, PointCloudWriter)
│   ├── Render/                          (PointCloudViewer, RenderConfig, SurfaceTriangulator)
│   └── RunFileRecord/                   (RunRecordManager, RecordFrame, SmartRayConverter)
├── SqlLiteDatabase/                     ← SQLite 数据库
│   ├── SQLiteDataBase.cs
│   ├── DatabaseManagerBase.cs
│   ├── AuthManager.cs
│   ├── ConfigManager.cs
│   ├── AutoParamManager.cs
│   └── ProductDatabaseManager.cs
├── UIDesign/                            ← UI 界面
│   ├── ParentUI/                        (FormMain)
│   ├── ControlPage/                     (MainPage, NavPage×2, DataReviewPage)
│   ├── Sub2UI/                          (LLCamWorkJob, Helix3Drender, CommPages, ...)
│   ├── Sub3UI/                          (EmguAlgoPage, ILAlgoPage)
│   └── SubView/                         (AlgorithmEditForm, ConfigForm, FormLogin, ...)
├── WeldParamControl/                    ← 焊接参数控制（原 InteliWeld）
│   ├── WeldProcess.cs
│   └── WeldDataManager.cs
├── Workflow/                            ← 工作流总控
│   ├── LineLaserWorkflow.cs
│   ├── MainDeviceThread.cs
│   ├── MonitorCameraWorkflow.cs
│   ├── MotionControlWorkflow.cs
│   ├── SimulationWorkflow.cs
│   ├── WeldActionRecord.cs
│   ├── WeldProcessAdjustmentWorkflow.cs
│   └── WorkflowState.cs
├── Program.cs
└── AdaWeldSystem.csproj
```

## 模块清单

> 文件数为 2026-09-01 实测（`.cs` 排除 `*.Designer.cs`）。子模块缩进表示其父模块。

| 模块 | 文件数 | 职责简述 |
|------|-------|---------|
| [[modules/DeviceControl]] | 12 | **设备控制中枢 `MainDeviceControl/`**：设备态四态 + 流程态分离 + 7 个工作流 + 安全互锁（故障恢复 2026-09-01 归口迁出至 [[modules/ProductFileManager]]，ADR-046 §3）。架构见 [[architecture/DeviceControlArchitecture]] |
| [[modules/UIDesign]] | 22 | 全部 UI 界面（AntdUI），子命名空间 `Sub1UI` / `Sub2UI` / `Sub3UI` |
| [[modules/LineLaserCam]] | 17 | 线激光相机族父目录 |
| └ [[modules/SmartRayCam]] | 10 | SmartRay 3D 轮廓传感器 SDK 封装与运行控制 |
| └ [[modules/HikRobotCam]] | 3 | 海康机器人 **3D 线激光**相机 SDK 封装（MV3D-LP 系列） |
| └ [[modules/IntelligentLaserCam]] | 1 | 英莱线激光相机（默认线激光，见 [[decisions/ADR-035-LineLaserWorkflowRefactor]]） |
| └ VirtualCam | 1 | 虚拟相机（模拟模式取图源） |
| └ `Api/` | 2 | 相机接口层（`CameraSelector` / `ICameraRun`，命名空间 `LineLaserCamApi`） |
| [[modules/MotionControl]] | 17 | 运控：正运动 ZMotion / CAMBOX 跟踪 / `MoveControlData` / `MotionManager` |
| [[modules/EmguALG]] | 15 | 图像算法唯一入口、算法配置、Job 管理、ROI 工具、焊缝识别、实时监控 |
| [[modules/Comm]] | 12 | 全局通讯中心 `CommunicationManager`、TCP/S7/PLC/Robot（KUKA RSI+EKI）、Modbus |
| └ [[modules/KUKARobot]] | 5 | KUKA 机器人通讯（`Comm/Robot/KUKARobot/`） |
| [[modules/SqlLiteDatabase]] | 7 | 用户认证、配置管理、自动参数管理、`FaultRecord` 持久化 |
| [[modules/PointCloudData]] | 7 | 3D 点云数据处理（`PCLOperate/`，模块名沿用 PointCloudData） |
| [[modules/MonitorCam]] | 4 | 监控相机：焊前对中/焊中质检，健康巡检在 `MonitorCameraRun` |
| [[modules/ProductFileManager]] | 5 | 产品生命周期记录归口：过程数据文件管理 + **故障恢复数据（`FaultRecoveryManager`，2026-09-01 自 DeviceControl 迁入）** |
| [[modules/LaserWeldHead]] | 3 | 激光焊接头（激光器/镜片温度/对焦电机 IO/安全 IO），含数据模型 |
| [[modules/WeldParamControl]] | 2 | 焊接工艺核心逻辑（`WeldProcess` 自适应调整 + `WeldDataManager`） |
| [[modules/FileOperate]] | 3 | INI/Log/XML 文件操作工具库 |

> **已删除模块（勿再列入清单）**：`Workflow/`、`DataModels/`、`DeviceStateMachine/`（2026-08-28 并入 `MainDeviceControl`）、`PointCloudData/`、`InteliWeld/`（能力并入 `EmguALG` / `WeldParamControl`）。

## 统计数据

| 指标 | 数值 |
|------|------|
| 顶层模块数 | **13 个**（实测顶层目录，排除 `Properties`/`Resources`/`3rdDepend`/`bin`/`obj`） |
| C# 源文件数 | **127 个**（2026-09-01 实测，排除 `*.Designer.cs`） |
| 设备工作流数 | 7 个（LineLaser / MonitorCamera / MotionControl / WeldParamControl / LaserWeldHead / Safety / Simulation）+ 主控 `MainDeviceWorkflow` |
| 设备态 | 固定四态：`Disconnect` / `Connect` / `Work` / `Alarm` |
| 开发专员数 | 10 个 |

---

*来源：raw/skills/00-Root/SkillRoot.md + Docs/AdaWeldSystem_Wiki.md*

