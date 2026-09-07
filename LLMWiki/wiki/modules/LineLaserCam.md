---
title: LineLaserCam 模块组 — 线激光相机族
date: 2026-07-21
tags: [模块, 相机, 线激光, 目录]
source: AdaWeldSystem/LineLaserCam/ 模块源码
---

# LineLaserCam 模块组 — 线激光相机族

> 2026-07-21 将三个同类线激光相机模块统一归入 `AdaWeldSystem/LineLaserCam/` 父目录，使目录层级更准确。
> 三个子模块均为 **3D 线激光（轮廓）相机**，共享 `ICameraRun` 抽象契约（位于 `LineLaserCam/Api/ICameraRun.cs`，即线激光相机族的**统一对外接口**），工作流与界面仅依赖接口，不关心具体相机实现。

## 子模块

| 子模块 | 位置 | 相机类型 | SDK |
|--------|------|----------|-----|
| [[modules/SmartRayCam]] | `LineLaserCam/SmartRayCam/` | SmartRay 工业3D线激光 | SmartRay SRAPI |
| [[modules/VirtualCam]] | `LineLaserCam/VirtualCam/` | 虚拟调试相机（模拟 SmartRay 线激光） | 自生成轮廓（无外部 SDK） |
| [[modules/HikRobotCam]] | `LineLaserCam/HikRobotCam/` | 海康机器人3D线激光 | Mv3dLpNet（MV3D-LP） |
| [[modules/IntelligentLaserCam]] | `LineLaserCam/IntelligentLaserCam/` | 英莱(IntelligentLaser) 工业3D线激光 | IntelligentLaser_CSharp（CppSharp 生成，.Net Framework） |

## 设计要点

- 命名空间：**Api 层统一对外接口**（`ICameraRun.cs` 与 `CameraSelector.cs`）命名空间为 `AdaWeldSystem.LineLaserCamApi`（与目录对齐）；其余子模块保留原命名空间：`AdaWeldSystem.SmartRayCameraRun`（CameraRun/CameraPresetManager，位于 SmartRayCam）、`AdaWeldSystem.VirtualCam`（VirtualCameraRun，位于 VirtualCam）、`AdaWeldSystem.HikRobotCam` / `Smartray.Sample`（ApiCore）。
- `CameraSelector`（`LineLaserCam/Api/CameraSelector.cs`，与 `ICameraRun` 同处统一对外接口层）在真实(SmartRay)/虚拟/Hik 三套相机间切换并聚合连接态模型；`ICameraRun` 使三者可互换。
- **统一对外接口目录 `LineLaserCam/Api/`**：`ICameraRun.cs` 与 `CameraSelector.cs` 共同构成线激光相机族统一对外接口层。2026-07-21 将 `ICameraRun` 由 `SmartRayCam/Api/`、`CameraSelector` 由 `VirtualCam/` 上提至此目录，二者命名空间**统一为 `AdaWeldSystem.LineLaserCamApi`**（与 Api 目录对齐，不再遵循「命名空间与目录解耦」惯例）；`ICameraRun` 由 `CameraRun`（SmartRayCam，命名空间 `AdaWeldSystem.SmartRayCameraRun`）与 `VirtualCameraRun`（VirtualCam，命名空间 `AdaWeldSystem.VirtualCam`）实现。详见 [[decisions/ADR-016-CameraSelectorUnifiedToApi]]。
- 与 [[modules/MonitorCam]]（监控 2D 相机）区分：MonitorCam 不参与线激光工作流，独立模块。

## 线激光设备状态（当前事实：三态模型）

> 独立的线激光相机状态机文件**不存在**：`DeviceStateMachine/` 目录、`DeviceStateMachineBase` 基类、`LineLaserCameraStateMachine` 均已删除。线激光的状态由工作流承载——对外只暴露**连接态 `SubDeviceState`** 与**焊接过程态 `SubDeviceWeldStatus`**，内部分支用**私有阶段枚举**（不对外）。详见 [[architecture/DeviceControlArchitecture]]、[[modules/DeviceControl]]。

**职责分工**：

| 关注点 | 承载者 | 位置 |
|---|---|---|
| 相机种类选择与连接态 | `CameraSelector` | `LineLaserCam/Api/CameraSelector.cs`（[[decisions/ADR-015-CameraConnectionStateDecoupled]]） |
| 连接态 + 焊接过程态 + 执行步 | `LineLaserWorkflow`（继承**非泛型** `DeviceWorkflowBase`） | `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` |

**内部执行流（私有阶段枚举，不对外）**：

```
Uninitialized → Initializing → Standby(待机，传感器/激光均关闭)
Standby → PreWork(启动前准备) → Starting(开激光+开传感器+等待数据稳定) → Working
Working → Stopping(关激光+关传感器+清理) → Standby
任意态 → ErrorAborted(异常终止) / ManualStopped(手动停止)
```

> 私有阶段 → `SubDeviceWeldStatus` 的映射表见 [[architecture/DeviceControlArchitecture]] §6（**唯一维护点**，本页不复制，避免两处漂移）。

> **易误判点**：`LineLaserWorkflow` 文件里 grep 不到 `State` / `SetState` / `WeldStatus` / `SetWeldStatus` / `StateSwitched` / `WeldStatusChanged` 是正常的，它们由基类 `DeviceStateBase` 提供。

## 状态标签规范（2026-08-19，ADR-022）

> 设备状态标签统一规范：**子设备（线激光）是状态主体，厂商硬件（英莱/SmartRay 等）是实例化实现**。详见 [[modules/DeviceControl]]。

- **线激光默认使用英莱相机**（`CameraSelector._kind` 默认 `IntelligentLaser`；`Active` 未显式选择时惰性 `SelectIntelligentLaser()`；`Load()` 无配置/异常回退英莱）。
- **英莱手动连接/断开同步驱动线激光状态机**：连接发起 → `Initializing`；成功 → `Standby`；失败/断开 → `Offline`（ILCamPage.btnConnect_Click 两跳转换）。
- **UI 状态标签只从线激光状态机识别**（`LineLaserWorkflow.Instance.StateMachine`），单函数 `UpdateConnectionUi()` 刷新，订阅 `StateMachine.StateChanged` 外发驱动（ILCamPage 已落地）。
- 自动流程状态由 `LineLaserWorkflow` 驱动状态机（Initializing/Working/Standby/Alarm），与手动连接共用同一状态机。

## 相机连接状态模型（2026-07-21 新增）

> 线激光相机自身状态（连接 / 断开 / 工作中）**与工作流程状态相互独立**，由 `CameraSelector` 聚合派生。详见 [[decisions/ADR-015-CameraConnectionStateDecoupled]]。

- 枚举定义于统一对外接口文件 `LineLaserCam/Api/ICameraRun.cs`（与 `ICameraRun` 同文件）：
  - `LineLaserCameraConnectionState { Disconnected, Connected, Working }` — 相机自身三态。
  - `CameraKind { None=0, SmartRay=1, Hik=2, Virtual=3, IntelligentLaser=4 }` — 当前配置的相机种类（用于启动检测与状态显示）。
- `CameraSelector`（[[api/CameraSelector]]）新增：
  - `Kind`：当前相机种类。
  - `ConnectionState`：派生连接态——`_working==true`→`Working`（仅由工作流 `SetWorking` 驱动）；否则按 `Kind` 派生（Virtual 恒 `Connected`、SmartRay 按 `CameraRun.Instance.IsConnected`、Hik 按 `HikCameraRun.Instance.IsCameraInitialized`、IntelligentLaser 按 `_intelligentInstance.IsConnected`、None→`Disconnected`）。
  - `SetWorking(bool)`：工作流 `Start()` 置 true、`WorkflowLoopWorker.finally` 置 false，驱动「工作中」态。
  - `DetectConnection()`：启动后按上次配置做连通性检测（Virtual/None 跳过；SmartRay→`OpenSensor("192.168.178.200","40")`；Hik→`OpenSensorByIP("192.168.178.201")`，IP 待从 `CameraPresets.ini` 读取；IntelligentLaser→`OpenSensor("192.168.178.210")`，IP 同样待从 `CameraPresets.ini` 读取）。

## 迁移背景

- 初版将 `VirtualCameraRun`/`CameraSelector` 误挂 `SmartRayCam/` 下，2026-07-16 抽出为平级 `VirtualCam`（见 [[decisions/ADR-012-MotionControlModule]]）。
- 2026-07-21 将 SmartRayCam / VirtualCam / HikRobotCam 三者统一迁入 `LineLaserCam/` 父目录（仅移动物理目录，命名空间与 `.csproj` Compile 路径同步更新，无语义改动）。

---

*来源：AdaWeldSystem/LineLaserCam/ 模块源码*
