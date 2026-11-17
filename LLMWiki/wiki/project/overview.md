---
title: AdaWeldSystem 项目概览
date: 2026-07-01
tags: [项目, 概览, 架构]
---

# AdaWeldSystem 项目概览

> 自适应焊接系统（Adaptive Welding System）是基于 .NET Framework 4.8 + WinForms + AntdUI（MIT，原 SunnyUI 已迁出，见 ADR-008）的工业控制软件。
>
> **定位**：**整个焊接激光头的全面控制软件**——13 个顶层模块，以 `MainDeviceControl` 为设备控制中枢（三态模型 + 5 个模组工作流 + 2 个整机管控类）。模块依赖见 [[architecture/DeviceControlArchitecture]]，设备控制架构见 [[architecture/DeviceControlArchitecture]]。**架构不做 V1/V2/V3 代际区分，只维护当前事实。**

## 技术栈

| 层级 | 技术 |
|------|------|
| 框架 | .NET Framework 4.8（C# 7.3 语法约束） |
| UI | WinForms + AntdUI（MIT，原 SunnyUI 已迁出，见 ADR-008） |
| 3D渲染 | HelixToolkit.Wpf.SharpDX |
| 图像算法 | Emgu.CV（OpenCV .NET 封装） |
| 工业相机 | SmartRay SRAPI + 海康 Mv3dLpNet |
| 数据库 | SQLite |
| 文件配置 | 自研 INIFile 类 |
| 设计模式 | 单例（Lazy<T>）、事件驱动、Step 状态机 |

## 目录结构（2026-08-04 更新）

> ⚠️ 历史名称提示：本树为 **2026-08-04 快照**，保留原文以留存上下文。与 2026-09-03 代码库的主要差异：
> - `UIDesign/ParentUI/` → 现役 `UIDesign/MainWindow/`；`UIDesign/Sub2UI/` → `UIDesign/TabPage/`；`UIDesign/Sub3UI/` → 并入 `UIDesign/SubDialog/`（2026-09-07 该目录再由扁平 `SubView/` 按业务域拆为 `SubDialog/` 下 5 个子目录，8 个类型改名，详见 [[modules/UIDesign]] §「2026-09-07 目录与命名对照」）
> - `EmguALG/Core/`、`EmguALG/EmguConfiger/` 等子目录下多个 Stage 文件已合并为单一 `EmguALG/Stages.cs`（详见 [[modules/EmguALG]]）
> - 各模块旧有的 StateMachine 类（`MonitorCameraStateMachine`、`MotionControlStateMachine`、`LaserWeldHeadStateMachine`）已统一迁移至 `MainDeviceControl/DeviceWorkflow/` 下的同名 Workflow 类（ADR-034）
>
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
├── Config/<模块>/<主题>_<格式>/          ← 配置文件（ADR-033 三段式，如 LineLaser/LineLaser_XML、Comm/Tcp_XML）
├── MainDeviceControl/                   ← 设备控制核心（三态模型 + 5 子工作流 + 2 管控类）
│   ├── DeviceStateApiCore/              (基类层：DeviceStateBase 三态枚举 + DeviceWorkflowBase 非泛型
│   │                                     工作流基类 + CommandTable 机器人握手协议表
│   │                                     ⛔ 2026-09-03 新架构：CommandTable.cs → CommandCore.cs
│   │                                     且常量改 const string，不再监控机器人 pose，见裁定 C3)
│   │                                    ※ 命名空间不随目录名，仍为 ...DeviceState / ...FlowState
│   │                                    ※ 以下为**改码前现状**，唯一架构指导见
│   │                                      [[architecture/DeviceControlArchitecture]] §16
│   ├── DeviceControlWork.cs             (整机运行编排：MainDeviceStatus 6 态 + 5 步上电初始化 + 机器人信号交互)
│   ├── DeviceStatusWork.cs              (安全/IO/状态管控：IOWork / EMGWork / StatusWork 三线程)
│   └── DeviceWorkflow/                  (5 个模组工作流：LineLaser / MonitorCamera / MotionControl
│                                         / WeldParamControl / LaserWeldHead)
├── EmguALG/                             ← 图像算法模块
│   ├── Core/                            (AlgorithmBase, PreprocessConfig, ...)
│   │   └── Attributes/                  (RangeAttribute, UnitAttribute)
│   ├── EmguConfiger/                    (AlgorithmJob, AlgorithmManager, JobManager)
│   ├── RealtimeMonitor/                 (RealtimeMonitorAlgorithm)
│   ├── SeamRecognition/                 (SeamModel, SeamRecognitionAlgorithm)
│   ├── ImageAlgorithm.cs
│   ├── Roi/                             (ImageRoi, ImageRoiTool — 通用 ROI，算法按需加载)
│   └── Stages.cs
├── FileOperate/                         ← 文件操作工具库
│   ├── INIFile.cs
│   ├── Log.cs
│   └── XdocumentReaderWriter.cs
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
│   ├── YAxisController.cs            ⚠️ 已移除（Y 轴专用控制器；职责现由 MotionManager.cs + ZMotion/ZMotionAxis.cs 承担）
│   └── MotionControlStateMachine.cs  ⚠️ 已迁出本模块，现役 `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs`
├── PointCloudData/                      ← 3D 点云处理
│   ├── Models/                          (Point3D, PointCloudData)
│   ├── DataIO/                          (PointCloudReader, PointCloudWriter)
│   ├── Render/                          (PointCloudViewer, RenderConfig, SurfaceTriangulator)
│   └── RunFileRecord/                   (RunRecordManager, RecordFrame, SmartRayConverter)
├── SQLiteDBControl/                    ← SQLite 数据库（命名空间 AdaWeldSystem.SQLiteDBControl）
│   ├── SQLiteCore/
│   │   └── SQLiteDataBase.cs
│   ├── ISQLiteHelper/
│   │   └── DatabaseHelperBase.cs
│   ├── Helpers/
│   │   ├── AuthHelper.cs
│   │   ├── AutoParamHelper.cs           (含 WeldAutoParamProfile 数据结构)
│   │   ├── ConfigHelper.cs
│   │   └── ProductDatabaseHelper.cs
│   └── SQLiteDatabaseManager.cs
├── UIDesign/                            ← UI 界面
│   ├── MainWindow/                      (FormMain；原 ParentUI/)
│   ├── ControlPage/                     (MainPage, NavPage×2, DataReviewerPage)
│   ├── TabPage/                         (ILCamPage, ProcessControlPage, FileEditorPage, FilebackupPage, MonitorCamPage, MotionControlPage；原 Sub2UI/)
│   └── SubDialog/                       ← 2026-09-07 由 SubView/ 按业务域拆分（命名空间 = AdaWeldSystem.UIDesign.SubDialog.<业务域>，ADR-005）
│       ├── DataReviewerDialog/          (FileTraceForm, HelixRenderForm, RecordConfigForm, RenderParamForm)
│       ├── FormMainDialog/              (InitWaitingForm)
│       ├── IntelligentLaserDialog/      (ILAlgoForm, ILAlgorithmEditForm, ILParamForm, ILScanForm)
│       ├── ParamContolDialog/           (AutoParamForm, ConfigForm)
│       └── UserManagerDialog/           (LoginForm, UserEditForm)
├── WeldParamControl/                    ← 焊接参数控制（原 InteliWeld）
│   ├── WeldParamData.cs                 (数据类集合)
│   ├── WeldParamManager.cs              (单例 · 唯一入口，2026-09-14 ADR-015)
│   ├── WeldAlgorithmsConfig.cs          (焊接算法配置，两节合一，Manager 独占 + 自带 XML 持久化；ADR-043)
│   ├── Abstractions/                    (WeldAlgorithmBase)
│   ├── Algorithms/                      (SeamGuideSample / WeldParamLookupAlgorithm / WeldParamAdjustmentAlgorithm / SeamTrackingAlgorithm)
├── Program.cs
└── AdaWeldSystem.csproj
```

## 模块清单

> 文件数为 2026-09-01 实测（`.cs` 排除 `*.Designer.cs`）。子模块缩进表示其父模块。

| 模块 | 文件数 | 职责简述 |
|------|-------|---------|
| [[modules/DeviceControl]] | 12 | **设备控制中枢 `MainDeviceControl/`**：三态模型（`SubDeviceState` / `SubDeviceWeldStatus` / `MainDeviceStatus`）+ 5 个模组工作流 + 2 个整机管控类（`DeviceControlWork` 运行编排 / `DeviceStatusWork` 安全·IO·状态）；故障恢复 2026-09-01 归口迁出至 [[modules/ProductFileManager]]（ADR-021 §3）。架构见 [[architecture/DeviceControlArchitecture]] |
| [[modules/UIDesign]] | 22 | 全部 UI 界面（AntdUI），命名空间随目录：`UIDesign.MainWindow` / `.ControlPage` / `.TabPage` / `.SubDialog.<业务域>`（ADR-005） |
| [[modules/LineLaserCam]] | 8 | **线激光相机（2026-09-08 三层重构 ADR-007）**：`ILineLaser/` 抽象 3 + 英莱 1 + 虚拟 1 + 业务层 3（`LineLaserManager` / `CameraRegistry` / `LineLaserConfig`） |
| └ [[api/IntelligentLaserCam]] | 1 | 英莱线激光相机（默认线激光，见 [[decisions/ADR-023-LineLaserWorkflowRefactor]]） |
| └ VirtualCam | 1 | 虚拟相机（模拟模式取图源） |
| ⛔ 已删除 | 15 | `SmartRayCam/`10 + `HikRobotCam/`3 + 旧 `Api/`2（`CameraSelector` / `ICameraRun`），见 [[decisions/ADR-024-LineLaserThreeLayerRefactor]] |
| [[modules/MotionControl]] | 17 | 运控：正运动 ZMotion / CAMBOX 跟踪 / `MoveControlData` / `MotionManager` |
| [[modules/EmguALG]] | 15 | 图像算法唯一入口、算法配置、Job 管理、ROI 工具、焊缝识别、实时监控 |
| [[modules/Comm]] | 12 | 全局通讯中心 `CommunicationManager`、TCP/S7/PLC/Robot（KUKA RSI+EKI）、Modbus |
| └ [[api/KUKARobot]] | 5 | KUKA 机器人通讯（原 modules/KUKARobot，2026-09-17 并入 api 页；实现居 `Comm/Communication/Implementations/`） |
| [[modules/SQLiteDatabase]] | 7 | 用户认证、配置管理、自动参数管理、产品数据持久化；目录 `SQLiteDBControl/`，对外唯一入口 `SQLiteDatabaseManager` |
| [[modules/PointCloudData]] | 7 | 3D 点云数据处理（`PCLOperate/`，模块名沿用 PointCloudData） |
| [[modules/MonitorCam]] | 4 | 监控相机：焊前对中/焊中质检，健康巡检在 `MonitorCameraRun` |
| [[modules/ProductFileManager]] | 5 | 产品生命周期记录归口：过程数据文件管理 + **故障恢复数据（`FaultRecoveryManager`，2026-09-01 自 DeviceControl 迁入）** |
| [[modules/MotionControl]] | 3 | 激光焊接头从站设备（`WeldHeadSlaveDevice`，2026-09-15 ADR-014 归运控模块：温度/气压/振镜/阈值/出光，MontionManager 装载管理） |
| [[modules/WeldParamControl]] | 8 | 焊接参数与算法（**2026-09-14 ADR-015 算法分层**：`WeldParamManager` 唯一入口 + `WeldParamLookupAlgorithm` / `WeldParamAdjustmentAlgorithm` / `SeamTrackingAlgorithm` 非单例实现 + `WeldAlgorithmBase` 抽象基类 + `WeldParamData` + `WeldAlgorithmsConfig`（两节合一，ADR-043），样本 `SeamGuideSample` 归 `Algorithms/`） |
| [[modules/FileOperate]] | 3 | INI/Log/XML 文件操作工具库 |

> **已删除模块（勿再列入清单）**：`Workflow/`、`DataModels/`、`DeviceStateMachine/`（2026-08-28 并入 `MainDeviceControl`）、`PointCloudData/`、`InteliWeld/`（能力并入 `EmguALG` / `WeldParamControl`）。

## 统计数据

| 指标 | 数值 |
|------|------|
| 顶层模块数 | **13 个**（实测顶层目录，排除 `Properties`/`Resources`/`3rdDepend`/`bin`/`obj`） |
| C# 源文件数 | **127 个**（2026-09-01 实测，排除 `*.Designer.cs`） |
| 模组工作流数 | 5 个（LineLaser / MonitorCamera / MotionControl / WeldParamControl / LaserWeldHead）+ 2 个整机管控类（`DeviceControlWork` 主控 / `DeviceStatusWork` 安全·IO·状态） |
| 设备状态模型 | **三态**：连接态 `SubDeviceState`(2 态) / 焊接过程态 `SubDeviceWeldStatus`(7 态) / 主设备运行态 `MainDeviceStatus`(6 态) |
| 开发专员数 | 10 个 |

---

*来源：raw/skills/00-Root/SkillRoot.md + Docs/AdaWeldSystem_Wiki.md*

