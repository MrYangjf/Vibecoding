---
title: LineLaserCam 模块 — 线激光相机
date: 2026-09-08
tags: [模块, 相机, 线激光, 三层架构, 管理器, ADR-007, ADR-032]
source: AdaWeldSystem/LineLaserCam/ 模块源码
---

# LineLaserCam 模块 — 线激光相机

> **2026-09-08 三层重构（ADR-007）**：线激光族仿照 [[modules/MotionControl]] 的三层范式重排——
> L2 抽象 `ILineLaser/` + L3 实现（`IntelligentLaserCam/` 英莱、`VirtualCam/` 虚拟）+ 业务层 `LineLaserManager` 单例。
> 同时**删除 SmartRay 与海康机器人 3D 两套不再使用的实现**（`SmartRayCam/` 10 文件、`HikRobotCam/` 3 文件、旧 `Api/` 2 文件），
> 并移除 `Mv3dLpNet` 引用；`CameraSelector` 与 `ICameraRun` 由 `LineLaserManager` 与 `LineLaserCameraBase` 取代。
> 决策记录：[[decisions/ADR-024-LineLaserThreeLayerRefactor]]。
>
> **2026-09-17（ADR-032）模拟统一化**：虚拟相机改为**平直搭接轮廓（基准 1000 点 + 中心焊缝点）**、频率由 `LineLaserConfig.LineLaserDataFrequencyHz`（30/60/80/120Hz）经 `ApplyConfig()` 套用至 `FrameRateHz`；⛔ 虚拟模拟参数（轮廓/随机/目标距离/基准宽深）全删。相机选择由 `DeviceControlWork.ShouldUseVirtualCamera` 自动判定（取消 A/B/C 模式）。
>
> **2026-09-08 二次分工（ADR-032）**：三层结构建成后业务仍留在实现层，故再次切分——
> **实现层只做回调触发**（`RaiseResultReady` + `RaiseProfileReady`），
> **业务全部上提 `LineLaserManager`**（结果侧算 Y 轴 PVT 点并下载、轮廓侧做产品记录/点缓冲/按需生成 Mat）。
> 决策记录：ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。
>
> **2026-09-11 三次分工（ADR-037，⛔ 已演进为 ADR-015）**：线激光结果**不再直写 PVT**——
> `SeamPvtFeeder` 与 `AttachYAxis` 整类/整方法删除，**结果侧只缓存并转发 `ResultReady`**；
> 「滤波 / 超限剔除 / 单调约束 / 标定转换」与 PVT 点计算迁至 [[modules/WeldParamControl]] 的
> [[api/SeamTrackingAlgorithm]]（非单例、只输出 `PVTPoint[]`、不直接写控制器），由 [[api/WeldParamManager]] 持有，
> [[api/MotionControlWorkflow]] 写入控制器。
> 决策记录：~~ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）~~ → [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]。

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
│   └── VirtualCam.cs            ← 自生成平直搭接轮廓（基准 1000 点 + 频率可配，继承 LineLaserCameraBase）
├── CameraRegistry.cs                  ← 相机注册表（按名登记与查询）
├── LineLaserConfig.cs                 ← 配置实体（Config\LineLaser\LineLaser_XML\LineLaserConfig.xml；模拟参数仅 LineLaserDataFrequencyHz；⛔ SeamTrackAxisName 已迁出至运控 DeltaMotionConfig，ADR-033）
└── LineLaserManager.cs                ← 业务层单例（对外唯一入口 + 结果/轮廓业务处理）
       ├─ 同文件内嵌 ProfileSnapshot（双缓冲快照，现役）；~~ProfileMatRenderer~~ 已于 2026-09-09 上提为 [[api/LineLaserContourAlgorithm]]（ADR-010）
       └─ ⛔ SeamPvtFeeder 已于 2026-09-11 删除（ADR-037，PVT 写入迁至 WeldParamControl）
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
| **L3 只做回调触发** | 产帧回调末尾只调 `RaiseResultReady` + `RaiseProfileReady`，不得生成 Mat、写产品记录、按模式分支（ADR-010 D1） |
| 业务层只认抽象 | 具体类型（`IntelligentLaserCam` / `VirtualCam`）仅在 `LineLaserManager` 内 `new` 一次 |
| **取实例一律走管理器** | 需要厂商特化能力时取 `Instance.IntelligentLaser` / `Instance.VirtualCamera`，**禁止** `Active as Xxx` 转型（ADR-037） |
| **外设经管理器代理** | 连接 / 激光 / 传感器开关一律 `LineLaserManager.Connect/SetLaser/SetSensor/ShutdownPeripherals`，工作流不持有相机对象（ADR-037） |
| **不再持有运动能力** | 结果侧只转发 `ResultReady`，**不注入 `IPVTMotion`、不写 PVT**；Y 轴轨迹构造归 [[modules/WeldParamControl]]（ADR-037，取代 ADR-032 的原注入面） |
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
| `IsCameraOn` / `IsLaserOn` / `SetSensor` / `SetLaser` | 虚方法 | 激光与传感器开关，基类给默认实现；英莱与虚拟各自 `override`（ADR-037） |
| `DescribeLastError` | 虚方法 | 只读诊断契约（ADR-095）：厂商返回码 → 成品文本。基类默认明确返回「未提供返回码」；英莱按语境映射，虚拟明确未提供。UI 与流程只读，不自行拼 `ret=` |

> 事件声明在基类 → 派生类只能 `+=` / `-=`，不可赋值清空（[[lessons/CSharp-Language-Pitfalls]] §3.4）。
> 派生类**不得**再声明私有 `Tag` / `Log`（会遮蔽基类成员触发 CS0108，见 [[lessons/StepDrivenWorkflowPitfalls]]（七.3）坑一）。

## 业务层入口 `LineLaserManager`

见 [[api/LineLaserManager]]。要点：

- 单例（`Lazy<T>`），持有 `Cameras`（`CameraRegistry`）+ `Config`（`LineLaserConfig`）；
- `Register(name, camera)` 登记即订阅 `ResultReady` / `ProfileReady` / `StateChanged` 并**就地做业务处理**；
- **结果处理**（`OnCameraResultReady`）：缓存中性结果 → 对外转发 `ResultReady`（**不写 PVT**，ADR-037）；
- **轮廓处理**（`OnCameraProfileReady`）：产品记录 `RunRecordManager.AddFrame` → 更新 `ProfileSnapshot` 点缓冲 → 按开关生成 Mat 并触发 `MatUpdated`；
- 显示处理默认关闭，接口先行：`SetDisplayOptions(enabled, fps, convertMat)` + `Config.DisplayEnabled/DisplayFps/ConvertMatEnabled`；
- ⛔ **焊缝跟踪轴名已迁出（2026-09-20 ADR-033）**：`SeamTrackAxisName` **不再**由本模块配置承载，改归运控 `DeltaMotionConfig`（`ROOT/SEAM_TRACK` 段）；轴装配与 PVT/CSP 写入归 [[api/MotionControlWorkflow]] + [[api/SeamTrackingAlgorithm]]（ADR-037/ADR-015）。本类仅保留相机参数（DefaultKind / AutoConnectOnStart / SensorIp / LineLaserDataFrequencyHz / DISPLAY 三项），不再有 `SeamTrackAxisName` 或 `AttachYAxis`；
- `SelectIntelligentLaser()` / `SelectVirtual()` / `Select(name)` 切换当前相机，`Active` 惰性按 `Config.DefaultKind` 创建；
- ⛔ **单活约束（强制，2026-11-09）**：一次只允许一种线激光或虚拟相机在连接/采集。三道代码防线全在 Manager 内——`SetActive` 切换即 `ReleaseCamera`（`SensorStop` + `DisconnectManual`）、`Connect` 前 `FindOtherRunningCamera` 命中则拒绝并记 Error、`OnCameraProfileReady` / `OnCameraResultReady` 首行 `IsActiveSender` 校验发送方（非活动帧丢弃 + 累计计数 + 5 秒限流 Warning）。**不得移除**，详见 [[decisions/ADR-024-LineLaserThreeLayerRefactor]]「七」与 [[standards/ModuleOrganizationPattern]] H10；
- `ConnectionState` 由 `_working`（工作流经 `SetWorking` 驱动）+ 选中相机派生，延续 ADR-008 的「相机态与流程态解耦」；`SetWorking` 现只驱动连接态派生（⛔ 不再起止 PVT 段，ADR-037）；
- 配置由 `Config`（XML，路径 `Config\LineLaser\LineLaser_XML\LineLaserConfig.xml`，ADR-033）承载：`DefaultKind` / `AutoConnectOnStart` / `SensorIp` / **`LineLaserDataFrequencyHz`**（线激光数据频率 30/60/80/120Hz，ADR-032；`ROOT/SIMULATION/DATA_FREQUENCY_HZ`） / **DISPLAY 三项**；⛔ **`SeamTrackAxisName` 已迁出**（2026-09-20 ADR-033，改归运控 `DeltaMotionConfig`）；`LoadConfig` / `SaveConfig` 无参。
  - ⛔ **ADR-032 已删**虚拟模拟参数：`SimSeamProfile` / `SimRandomMode` / `SimTargetDistance` / `SimBaseSeamWidth` / `SimBaseSeamDepth`（`PROFILE` / `RANDOM_MODE` / `TARGET_DISTANCE` / `BASE_SEAM_WIDTH` / `BASE_SEAM_DEPTH` 节点消失，存量配置零迁移）。
  - `ApplyConfig()` 把 `LineLaserDataFrequencyHz` 套用至虚拟相机 `FrameRateHz`（决定出图节拍 `1000/Hz` ms 与 `ScanRateHz`）。

## 两条数据链路（ADR-032 + ADR-037）

```
英莱/虚拟 SDK 回调
   ├─ RaiseResultReady(LineLaserSeamResult) ──► Manager 结果处理
   │        └─ 缓存 → 转发 ResultReady
   │              ├─ LineLaserWorkflow（触发焊接工艺计算）
   │              └─ MotionControlWorkflow → SeamTrackingAlgorithm.Feed（ADR-015；~~SeamTrajectoryBuilder~~ 已删）
   │                     （滤波/超限剔除/单调约束/标定转换 → Y 轴，ADR-037 沿革）
   └─ RaiseProfileReady(PointCloudData) ────► Manager 轮廓处理
            ├─ ~~RunRecordManager.AddFrame~~（⛔ 类已删，ADR-033/047——现役记录链见 [[api/ProductFileRecordManager]]）
            ├─ ProfileSnapshot 双缓冲 → MainPage 轮询（版本号比对，现役）
            └─ 显示开关开启时 → LineLaserContourAlgorithm.Render（ADR-010 上提）→ MatUpdated → ILCamPage
```

## 线激光设备状态（三态模型）

> 独立的线激光相机状态机文件**不存在**：状态由工作流承载——对外只暴露连接态 `SubDeviceState` 与焊接过程态 `SubDeviceWeldStatus`，内部分支用私有阶段枚举。详见 [[architecture/DeviceControlArchitecture]]、[[modules/DeviceControl]]。

| 关注点 | 承载者 | 位置 |
|---|---|---|
| 相机注册 / 选中 / 连接态派生 / 配置 | `LineLaserManager` | `LineLaserCam/LineLaserManager.cs` |
| 结果 → Y 轴轨迹计算与 PVT 写入 | `SeamTrackingAlgorithm`（算点）+ `MotionControlWorkflow`（写控制器） | `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` · `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` |
| 轮廓 → 点缓冲 / Mat 生成 | `LineLaserManager` + `LineLaserContourAlgorithm` | `LineLaserCam/LineLaserManager.cs` + `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs`（ADR-010 上提） |
| 连接态 + 焊接过程态 + 执行步 | `LineLaserWorkflow`（继承非泛型 `DeviceWorkflowBase`） | `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` |
| 焊缝跟踪轴装配（按 `SeamTrackAxisName` 取轴 + 订阅 `ResultReady`）+ 结果驱动 | `MotionControlWorkflow` | `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` |

## 已知问题（模拟测试，2026-09-20 / [[decisions/ADR-039-SimulationTestAutoTerminationAndRecordCacheRelease]]）

- **焊缝跟踪轴名须匹配实际轴**：运控 `DeltaMotionConfig.xml` 的 `ROOT/SEAM_TRACK/SEAM_TRACK_AXIS`（经 `MontionManager.Instance.MoveData.MotionConfig.SeamTrackAxisName` 读取，ADR-033）默认值须为真实存在的轴名（现行 `"Y向电机"`），否则 `MotionControlWorkflow` 解析 `_seamAxis` 为 `null` → 轨迹/工艺记录全空（[[lessons/SimulationAutoBranching]] 陷阱十）。
- 虚拟相机分支须触发 `WeldParamControlWorkflow.ComputeAndOutput()`，否则 `.pDat` 工艺过程帧空（[[lessons/SimulationAutoBranching]] 陷阱十一）。

## 设计决策

- 线激光族采用**抽象层 + 实现层 + 业务层**三层，业务层只面向抽象编程（仿 [[modules/MotionControl]] 的 L1/L2/L3 铁律，本模块无 Native 层）。
- 相机选择、事件订阅、连接态与配置统一归口 `LineLaserManager`，`CameraSelector` 随之删除。
- **业务一律归业务层**：实现层只发两个中性回调（ADR-032）。
- **不持有运动语义**：结果侧只转发，Y 轴轨迹构造与 PVT 写入归 [[modules/WeldParamControl]]，本模块不注入运动能力（ADR-015）。
- 详阅 [[decisions/ADR-024-LineLaserThreeLayerRefactor]]、ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、~~ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）~~ → [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]、[[decisions/ADR-021-CameraConnectionStateDecoupled]]（最后一条为历史决策）。

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| [[modules/DeviceControl]] | `LineLaserWorkflow` 经 `LineLaserManager.Instance` 订阅 `ResultReady`、驱动 `SetWorking` |
| [[modules/MotionControl]] | `MoveControlData` 消费线激光特征；模拟模式共用虚拟相机；**Y 轴轨迹由运控工作流驱动生成**（焊缝跟踪轴名取自运控 `DeltaMotionConfig` 的 `SeamTrackAxisName`，ADR-033 已迁出本模块） |
| [[modules/WeldParamControl]] | `SeamTrajectoryBuilder` 消费本模块 `ResultReady`（经 `MotionControlWorkflow` 转发喂入） |
| [[modules/EmguALG]] | 轮廓 Mat 渲染走 `EmguALG/LineLaserContour/`（ADR-010）；⛔ 原 `PipelineManager` 与 `ConvertContourToMat(PointCloudData…)` 已随 ADR-007 删除 |
| [[modules/UIDesign]] | `ILCamPage`（英莱相机页）、`MainPage`（轮廓曲线）经管理器取相机 |
| [[modules/Comm]] | `GlobalCommData.ShowLog` 日志（抽象层与业务层共用） |

> **参照范式**：本模块是 [[standards/ModuleOrganizationPattern]] 的**场景 A（基于第三方库英莱 SDK）**样本——`ILineLaser/LineLaserCameraBase` 抽象 + 英莱/虚拟双实现 + `LineLaserManager` 唯一入口（相机实例唯一持有者）。

---

*来源：AdaWeldSystem/LineLaserCam/ 模块源码*
