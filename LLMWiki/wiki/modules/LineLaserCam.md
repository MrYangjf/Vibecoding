---
title: LineLaserCam 模块 — 线激光相机
date: 2026-09-08
tags: [模块, 相机, 线激光, 三层架构, 管理器, ADR-038]
source: AdaWeldSystem/LineLaserCam/ 模块源码
---

# LineLaserCam 模块 — 线激光相机

> **2026-09-08 三层重构（ADR-038）**：线激光族仿照 [[modules/MotionControl]] 的三层范式重排——
> L2 抽象 `ILineLaser/` + L3 实现（`IntelligentLaserCam/` 英莱、`VirtualCam/` 虚拟）+ 业务层 `LineLaserManager` 单例。
> 同时**删除 SmartRay 与海康机器人 3D 两套不再使用的实现**（`SmartRayCam/` 10 文件、`HikRobotCam/` 3 文件、旧 `Api/` 2 文件），
> 并移除 `Mv3dLpNet` 引用；`CameraSelector` 与 `ICameraRun` 由 `LineLaserManager` 与 `LineLaserCameraBase` 取代。
> 决策记录：[[decisions/ADR-034-LineLaserThreeLayerRefactor]]。
>
> **2026-09-08 二次分工（ADR-035）**：三层结构建成后业务仍留在实现层，故再次切分——
> **实现层只做回调触发**（`RaiseResultReady` + `RaiseProfileReady`），
> **业务全部上提 `LineLaserManager`**（结果侧算 Y 轴 PVT 点并下载、轮廓侧做产品记录/点缓冲/按需生成 Mat）。
> 决策记录：[[decisions/ADR-035-LineLaserResponsibilitySplit]]。
>
> **2026-09-11 三次分工（ADR-040，⛔ 已演进为 ADR-041）**：线激光结果**不再直写 PVT**——
> `SeamPvtFeeder` 与 `AttachYAxis` 整类/整方法删除，**结果侧只缓存并转发 `ResultReady`**；
> 「滤波 / 超限剔除 / 单调约束 / 标定转换」与 PVT 点计算迁至 [[modules/WeldParamControl]] 的
> [[api/SeamTrackingAlgorithm]]（非单例、只输出 `PVTPoint[]`、不直接写控制器），由 [[api/WeldParamManager]] 持有，
> [[api/MotionControlWorkflow]] 写入控制器。
> 决策记录：~~[[decisions/ADR-040-SeamGuideTrajectoryBuilder]]~~ → [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]]。

## 目录结构（2026-09-08 现行）

```
LineLaserCam/
├── ILineLaser/                        ← L2 抽象层（零厂商依赖）
│   ├── LineLaserType.cs               ← LineLaserKind / LineLaserConnectionState 枚举
│   ├── LineLaserCalibration.cs        ← LineLaserCalibration 中性校准数据（2026-09-08 新增）
│   ├── LineLaserEventArgs.cs          ← LineLaserSeamResult / Result / Profile / Mat / State 事件参数
│   └── LineLaserCameraBase.cs         ← 相机抽象基类（键名 + 连接态派生 + 三个事件 + 日志出口）
├── IntelligentLaserCam/               ← L3 英莱实现（只做回调触发）
│   └── IntelligentLaserCam.cs   ← 英莱 SDK 封装（继承 LineLaserCameraBase）
├── VirtualCam/                        ← L3 虚拟实现（只做回调触发）
│   └── VirtualCam.cs            ← 自生成轮廓（继承 LineLaserCameraBase）
├── CameraRegistry.cs                  ← 相机注册表（按名登记与查询）
├── LineLaserConfig.cs                 ← 配置实体（Config/XML/LineLaserConfig.xml）
└── LineLaserManager.cs                ← 业务层单例（对外唯一入口 + 结果/轮廓业务处理）
       ├─ 同文件内嵌 ProfileSnapshot / ProfileMatRenderer
       └─ ⛔ SeamPvtFeeder 已于 2026-09-11 删除（ADR-040，PVT 写入迁至 WeldParamControl）
```

> **命名空间**：`ILineLaser/` → `AdaWeldSystem.LineLaserCam.ILineLaser`；
> `IntelligentLaserCam/` → `AdaWeldSystem.LineLaserCam.IntelligentLaserCam`；
> `VirtualCam/` → `AdaWeldSystem.LineLaserCam.VirtualCam`；模块根 → `AdaWeldSystem.LineLaserCam`。
> ⛔ 已删除命名空间 `AdaWeldSystem.LineLaserCamApi`（旧 `Api/` 层）。

## 依赖铁律（仿运控）

| 铁律 | 内容 |
|------|------|
| L2 零依赖 | `ILineLaser/` 内不得出现 `IntelligentLaser_export`、`SmartRayCam`、`DllImport` 等厂商类型 |
| L3 实现抽象 | 英莱与虚拟均继承 `LineLaserCameraBase`，硬件 SDK 调用只出现在 L3 |
| **L3 只做回调触发** | 产帧回调末尾只调 `RaiseResultReady` + `RaiseProfileReady`，不得生成 Mat、写产品记录、按模式分支（ADR-039 D1） |
| 业务层只认抽象 | 具体类型（`IntelligentLaserCam` / `VirtualCam`）仅在 `LineLaserManager` 内 `new` 一次 |
| **取实例一律走管理器** | 需要厂商特化能力时取 `Instance.IntelligentLaser` / `Instance.VirtualCamera`，**禁止** `Active as Xxx` 转型（ADR-040） |
| **外设经管理器代理** | 连接 / 激光 / 传感器开关一律 `LineLaserManager.Connect/SetLaser/SetSensor/ShutdownPeripherals`，工作流不持有相机对象（ADR-040） |
| **不再持有运动能力** | 结果侧只转发 `ResultReady`，**不注入 `IPVTMotion`、不写 PVT**；Y 轴轨迹构造归 [[modules/WeldParamControl]]（ADR-040，取代 ADR-035 的原注入面） |
| 唯一入口 | 工作流与 UI 一律经 `LineLaserManager.Instance`，禁止直接持有相机实例做装配 |

## 抽象层契约 `LineLaserCameraBase`

| 成员 | 类型 | 说明 |
|------|------|------|
| `CameraName` | 具体属性 | 相机键名，同时作为日志标签（英莱=「英莱线激光」、虚拟=「虚拟线激光」） |
| `Kind` / `IsConnected` / `IsRunning` | 抽象属性 | 种类与运行态 |
| `LastAcquisitionSuccess` / `ScanRateHz` | 抽象属性 | 取帧契约 |
| `CurrentMat` | 具体属性 | 最近显示帧；由业务层生成后经 `UpdateDisplayMat` 回写，实现层不主动生成 |
| `AcquisitionCompletedSignal` | 抽象属性 | 回调等待信号（ADR-005） |
| `Calibration` | 虚属性 | 中性校准数据，厂商实现层捕获存储，业务层绘制时读取 |
| `ConnectionState` | 具体属性 | 由 `IsConnected` 派生「已连接 / 未连接」（「工作中」由管理器派生） |
| `ResultReady` / `ProfileReady` / `StateChanged` | 事件 | 派生类产帧 / 状态变化时调用 `RaiseResultReady` / `RaiseProfileReady` / `RaiseStateChanged` |
| `SensorRunContinue` / `SensorStop` / `Dispose` / `UpdateDisplayMat` | 方法 | 采集、释放、显示帧回写 |
| `ConnectManual` / `DisconnectManual` / `ConfigureDefaultCommPeriod` | 虚方法 | 连接类外设契约，基类给默认实现（不支持则告警返回 false / 空操作 / 返回 true），派生类按需 `override` |
| `IsCameraOn` / `IsLaserOn` / `SetSensor` / `SetLaser` | 虚方法 | 激光与传感器开关，基类给默认实现；英莱与虚拟各自 `override`（ADR-040） |

> 事件声明在基类 → 派生类只能 `+=` / `-=`，不可赋值清空（[[lessons/CSharp-Language-Pitfalls]] §3.4）。
> 派生类**不得**再声明私有 `Tag` / `Log`（会遮蔽基类成员触发 CS0108，见 [[lessons/DeviceControlWorkInheritanceBypass]] 坑一）。

## 业务层入口 `LineLaserManager`

见 [[api/LineLaserManager]]。要点：

- 单例（`Lazy<T>`），持有 `Cameras`（`CameraRegistry`）+ `Config`（`LineLaserConfig`）；
- `Register(name, camera)` 登记即订阅 `ResultReady` / `ProfileReady` / `StateChanged` 并**就地做业务处理**；
- **结果处理**（`OnCameraResultReady`）：缓存中性结果 → 对外转发 `ResultReady`（**不写 PVT**，ADR-040）；
- **轮廓处理**（`OnCameraProfileReady`）：产品记录 `RunRecordManager.AddFrame` → 更新 `ProfileSnapshot` 点缓冲 → 按开关生成 Mat 并触发 `MatUpdated`；
- 显示处理默认关闭，接口先行：`SetDisplayOptions(enabled, fps, convertMat)` + `Config.DisplayEnabled/DisplayFps/ConvertMatEnabled`；
- 焊缝跟踪轴名 `Config.SeamTrackAxisName` 仍由本模块配置承载，但轴装配与 PVT 写入归 [[api/MotionControlWorkflow]] + [[api/SeamTrajectoryBuilder]]（ADR-040，本类不再有 `AttachYAxis`）；
- `SelectIntelligentLaser()` / `SelectVirtual()` / `Select(name)` 切换当前相机，`Active` 惰性按 `Config.DefaultKind` 创建；
- `ConnectionState` 由 `_working`（工作流经 `SetWorking` 驱动）+ 选中相机派生，延续 ADR-015 的「相机态与流程态解耦」；`SetWorking` 现只驱动连接态派生（⛔ 不再起止 PVT 段，ADR-040）；
- 配置由 `Config`（XML）承载：`DefaultKind` / `AutoConnectOnStart` / `SensorIp` / 虚拟模拟参数 / **`SeamTrackAxisName`** / **DISPLAY 三项**；`LoadConfig` / `SaveConfig` 无参。

## 两条数据链路（ADR-035 + ADR-040）

```
英莱/虚拟 SDK 回调
   ├─ RaiseResultReady(LineLaserSeamResult) ──► Manager 结果处理
   │        └─ 缓存 → 转发 ResultReady
   │              ├─ LineLaserWorkflow（触发焊接工艺计算）
   │              └─ MotionControlWorkflow → SeamTrajectoryBuilder.Feed
   │                     （滤波/超限剔除/单调约束/标定转换 → Y 轴 PVT，ADR-040）
   └─ RaiseProfileReady(PointCloudData) ────► Manager 轮廓处理
            ├─ RunRecordManager.AddFrame（产品记录）
            ├─ ProfileSnapshot 双缓冲 → MainPage 轮询（版本号比对）
            └─ 显示开关开启时 → ProfileMatRenderer.Render → MatUpdated → ILCamPage
```

## 线激光设备状态（三态模型）

> 独立的线激光相机状态机文件**不存在**：状态由工作流承载——对外只暴露连接态 `SubDeviceState` 与焊接过程态 `SubDeviceWeldStatus`，内部分支用私有阶段枚举。详见 [[architecture/DeviceControlArchitecture]]、[[modules/DeviceControl]]。

| 关注点 | 承载者 | 位置 |
|---|---|---|
| 相机注册 / 选中 / 连接态派生 / 配置 | `LineLaserManager` | `LineLaserCam/LineLaserManager.cs` |
| 结果 → Y 轴轨迹计算与 PVT 写入 | `SeamTrackingAlgorithm`（算点）+ `MotionControlWorkflow`（写控制器） | `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` · `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` |
| 轮廓 → 产品记录 / 点缓冲 / Mat 生成 | `LineLaserManager` + `ProfileMatRenderer` | `LineLaserCam/LineLaserManager.cs`（同文件内嵌类） |
| 连接态 + 焊接过程态 + 执行步 | `LineLaserWorkflow`（继承非泛型 `DeviceWorkflowBase`） | `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` |
| 焊缝跟踪轴装配（按 `SeamTrackAxisName` 取轴 + 订阅 `ResultReady`）+ 结果驱动 | `MotionControlWorkflow` | `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` |

## 设计决策

- 线激光族采用**抽象层 + 实现层 + 业务层**三层，业务层只面向抽象编程（仿 [[modules/MotionControl]] 的 L1/L2/L3 铁律，本模块无 Native 层）。
- 相机选择、事件订阅、连接态与配置统一归口 `LineLaserManager`，`CameraSelector` 随之删除。
- **业务一律归业务层**：实现层只发两个中性回调（ADR-035）。
- **不持有运动语义**：结果侧只转发，Y 轴轨迹构造与 PVT 写入归 [[modules/WeldParamControl]]，本模块不注入运动能力（ADR-041）。
- 详阅 [[decisions/ADR-034-LineLaserThreeLayerRefactor]]、[[decisions/ADR-035-LineLaserResponsibilitySplit]]、~~[[decisions/ADR-040-SeamGuideTrajectoryBuilder]]~~ → [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]]、[[decisions/ADR-013-CameraConnectionStateDecoupled]]（最后一条为历史决策）。

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| [[modules/DeviceControl]] | `LineLaserWorkflow` 经 `LineLaserManager.Instance` 订阅 `ResultReady`、驱动 `SetWorking` |
| [[modules/MotionControl]] | `MoveControlData` 消费线激光特征；模拟模式共用虚拟相机；**Y 轴轨迹由运控工作流驱动 `SeamTrajectoryBuilder` 生成**（轴名取自本模块配置 `SeamTrackAxisName`） |
| [[modules/WeldParamControl]] | `SeamTrajectoryBuilder` 消费本模块 `ResultReady`（经 `MotionControlWorkflow` 转发喂入） |
| [[modules/EmguALG]] | 轮廓 Mat 渲染走 `EmguALG/LineLaserContour/`（ADR-039）；⛔ 原 `PipelineManager` 与 `ConvertContourToMat(PointCloudData…)` 已随 ADR-038 删除 |
| [[modules/UIDesign]] | `ILCamPage`（英莱相机页）、`MainPage`（轮廓曲线）经管理器取相机 |
| [[modules/Comm]] | `GlobalCommData.ShowLog` 日志（抽象层与业务层共用） |

> **参照范式**：本模块是 [[standards/ModuleOrganizationPattern]] 的**场景 A（基于第三方库英莱 SDK）**样本——`ILineLaser/LineLaserCameraBase` 抽象 + 英莱/虚拟双实现 + `LineLaserManager` 唯一入口（相机实例唯一持有者）。

---

*来源：AdaWeldSystem/LineLaserCam/ 模块源码*
