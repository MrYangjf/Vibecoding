---
title: ADR-024 线激光模块现行决策（三层结构 · 职责分工 · Manager 单一入口；整合原 034/035/036）
date: 2026-09-08
updated: 2026-11-09
tags: [决策, 线激光, 相机, 三层架构, 管理器, 职责分层, 单一入口, 移除, merged, ADR-024]
status: accepted
merged_from: [ADR-034, ADR-035, ADR-036]
---

# ADR-024 线激光模块现行决策（三层结构 · 职责分工 · Manager 单一入口）

> 本页为整合页（2026-09-17），收拢原 ADR-003 / ADR-032 / ADR-033 的全部现行裁定；被后续演进推翻的中间态见「被推翻的中间态」与「沿革」。焊缝跟踪 Y 轴现行方案见 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] 与 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]，本页不重复。

## 背景

线激光族原为「`Api/ICameraRun` 接口 + 多套实现（SmartRay / 海康 3D / 英莱 / 虚拟）+ `CameraSelector` 静态选择器」结构，存在四类问题：

1. **实际只跑一条链路**：程序只使用英莱（真实）与虚拟（调试）两类相机，SmartRay 与海康 3D 属历史遗留，长期 0 使用却持续占据编译与维护成本；
2. **装配散落**：`CameraSelector` 是静态类，相机实例、连接态、IP 持久化三处逻辑分散在静态字段、INI 文件与具体相机类中；
3. **业务留在实现层**：英莱 `MillionOutlineCallback` 一个回调里同时干六件事——建点云、捕获算法结果、按 `_isManualMode` 分支生成 Mat、写产品记录、抛 `ContourDataReady`、抛 `ContourFrameReady`；换相机即重抄全部业务，且数据/显示双事件通道是 [[decisions/ADR-016-WorkflowResponsibilityBoundary]] 治理过的反例复现；
4. **与运控范式不一致**：[[modules/MotionControl]] 已确立「抽象层 + 厂商实现 + 业务层管理器」的三层范式，线激光未对齐；且多处绕过管理器直接持有/转型厂商实例。

## 现行决策

### 一、三层结构（仿运控）

| 层 | 目录 | 内容 |
|---|---|---|
| L2 抽象 | `LineLaserCam/ILineLaser/` | `LineLaserType.cs`（`LineLaserKind` / `LineLaserConnectionState`）、`LineLaserEventArgs.cs`、`LineLaserCameraBase.cs` |
| L3 实现 | `IntelligentLaserCam/`、`VirtualCam/` | 英莱与虚拟相机，均继承 `LineLaserCameraBase` |
| 业务层 | 模块根 | `LineLaserManager.cs`（单例）+ `CameraRegistry.cs` + `LineLaserConfig.cs` |

采用**抽象基类而非接口**（沿用运控 `MontionControl` 范式）：相机键名、连接态派生、中性事件与日志出口上提基类；派生类不得感知厂商类型以外的业务。

### 二、抽象层契约（全部中性，业务层不感知厂商类型）

1. **派生类禁私有 `Tag` / `Log`**：事件与日志出口上提基类后，派生类不得再声明私有 `Tag` / `Log`（避免 CS0108 遮蔽，见 [[lessons/StepDrivenWorkflowPitfalls]]（七.3）坑一）；
2. **中性事件**：基类承载 `ResultReady` / `ProfileReady` 与对应 `Raise*Ready` 保护方法；实现层删除 `ContourDataReady` / `ContourFrameReady` 双通道与 `ContourDataEventArgs`；
3. **中性结构**：`LineLaserSeamResult`（焊缝结果）与 `LineLaserCalibration`（校准数据）承载跨层数据，厂商结构体 `IlInspectResult` / `IlCalibrationInfo` 删除；校准数据仍由英莱在 SDK 回调中捕获存储，经 `Calibration` 属性供业务层读取；
4. **外设虚契约**：基类新增 7 个 `public virtual` 默认实现——`ConnectManual` / `DisconnectManual` / `ConfigureDefaultCommPeriod` / `IsCameraOn` / `IsLaserOn` / `SetSensor` / `SetLaser`；默认实现为「不支持则告警返回 false / 空操作 / 返回 true」，英莱与虚拟各自 `override`。**新增相机能力优先加在抽象层并给默认实现，派生类可暂不实现**。

### 三、Manager 单一入口（实例唯一持有者 + 外设代理）

1. **相机实例唯一持有者 = `LineLaserManager`**：管理器提供按类型访问器 `IntelligentLaser` / `VirtualCamera`，首次访问时创建 + `Register` 登记 + 套用配置；**厂商实现层不对外暴露实例**；
2. **外设操作由管理器代理**：对外提供 `Connect` / `Disconnect` / `ConfigureDefaultCommPeriod` / `IsCameraOn` / `IsLaserOn` / `SetSensor` / `SetLaser` / `ShutdownPeripherals` 八个代理方法；**工作流与流程层不再接触相机对象**，相机生命周期归管理器（工作流 `Dispose` 不再 `Dispose` 相机）；
3. **Manager 同时承担**：注册与选中、事件订阅与转发、连接态派生、配置持久化、采集启停（`StartAcquisition`）；
4. **消费方一律写 `LineLaserManager.Instance.X`**：原 `CameraSelector` 与 `ICameraRun` 一并删除（[[decisions/ADR-021-CameraConnectionStateDecoupled]] 的连接态解耦结论仍有效，承载者改为 `LineLaserManager`）。

### 四、职责分工（实现层只回调触发，业务上移 Manager）

1. **实现层只做回调触发**：英莱与虚拟相机产帧回调末尾**只做两件事**——`RaiseResultReady(...)` + `RaiseProfileReady(...)`；Mat 生成、产品记录、模式分支、UI 事件一律移出（删除 `_isManualMode` 与约 250 行 GDI 绘制代码）；
2. **Manager 承担业务处理**：`ProfileReady` → 产品记录 → 更新点缓冲 → 按需生成 Mat → 转发 `MatUpdated`；结果侧的后续消费见现行焊缝跟踪决策（沿革见下）；
3. **绘制归算法/渲染侧**：Mat 绘制统一走渲染器（画布一次分配、每帧 Clear 后重绘），不回挂实现层；
4. **显示默认关闭、接口先行**：`SetDisplayOptions(enabled, fps, convertMat)` + `Config.DisplayEnabled/DisplayFps/ConvertMatEnabled`——UI 显示不必跟随相机帧率；
5. **主页面轮询、手动页订阅**：`MainPage` 起独立线程按 33ms 节拍读 `Profile` 快照，用**版本号**判新、仅变化时刷新 ScottPlot（⚠️ 有意推翻 [[lessons/IntelligentLaser-Pitfalls]]「回调驱动显示非轮询」——相机 60~120Hz 而屏幕只需 30Hz，回调驱动会淹没 UI 线程）；`ILCamPage` 订阅 `MatUpdated`，不再订阅相机私有事件；页面销毁时 `StopProfilePolling()` 回收线程。

### 五、SmartRay / 海康 3D 移除，英莱接入

1. **删除**：`LineLaserCam/SmartRayCam/`（10 文件）、`LineLaserCam/HikRobotCam/`（3 文件）、`LineLaserCam/Api/`（2 文件），并移除 csproj 的 `Mv3dLpNet` 引用（海康 3D SDK）；
2. **保留链路的沿革**：`SmartRayConverter.cs` 与 `AddSmartRayFrame` 曾裁定保留（属产品记录链路），**2026-09-14 已被 ADR-031（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） 整链删除**（0 消费死代码）；
3. **消费方全量对接**：`LineLaserWorkflow`、`DeviceControlWork`、`ILCamPage`、`MainPage`、`ILAlgorithmEditForm` 五处由 `CameraSelector.X` / `Active as 厂商类型` 改为 `LineLaserManager.Instance.X`。

### 六、配置与命名

1. **配置改为 XML**：`LineLaserConfig`（`Config/XML/LineLaserConfig.xml`，走 `FileOperate/XMLfile.cs`，`LoadConfig()` / `SaveConfig()` 无参，遵循 [[decisions/ADR-035-RawDesignRefinement20260903]] 配置范式）；英莱 IP 由 `Config.SensorIp` 下发，原 `LoadSavedIp()` / `SaveSensorIp()` 与 `Config/INI/IntelligentLaser.ini` 弃用（**2026-09-21 演进**：`LineLaserConfig.xml` 现落 `Config\LineLaser\LineLaser_XML`；`IntelligentLaser.ini` 现落 `Config\IntelligentLaserCam\Camera_INI`）；
2. **命名采用规范拼写**：管理器为 `LineLaserManager`（非 `LinelaserMananger`），与既有 `MontionManager` 历史拼写不再对齐——新模块一律规范命名；英莱实现类 `IntelligentLaserCameraRun` → `IntelligentLaserCam`，类名回归文件名与目录名（虚拟侧 `VirtualCam` 同）。

### 七、单活约束（2026-11-09 增补 · 业主要求）

> **强制约束**：同一时刻只允许**一种**线激光相机在工作——真实英莱相机与虚拟相机**不得同时连接 / 采集**。执行方 = `LineLaserCam/LineLaserManager.cs`。

**改造前是设计约定而非代码保证**：`SetActive` 只改活动引用、不释放旧相机；两台相机经 `Register` 都订阅了 `ProfileReady`；`IntelligentLaserCam.DisconnectManual` 不等待在途回调（`WaitForCallbacksToFinish` 只在 `Dispose` 里调），`VirtualCam.SensorStop` 的 `Timer.Dispose()` 也不等待在途 tick。故断开瞬间仍可能再抛一帧，写坏 Manager 级共享的 `_ysBuffer` / `_zsBuffer`（窗口极小但非零）。

现由三道代码防线封死：

| 防线 | 代码位置 | 行为 |
|---|---|---|
| ① 切换即释放 | `SetActive` → `ReleaseCamera` | 切换活动相机时对上一台 `SensorStop()` + `DisconnectManual()` 并记 Info；单体异常只告警不中断切换 |
| ② 连接前置拒绝 | `Connect()` → `FindOtherRunningCamera()` | 除当前相机外仍有 `IsRunning` 的已登记相机时**拒绝连接**，记 Error（含占用方键名），不静默返回 |
| ③ 发送方身份校验 | `OnCameraProfileReady` / `OnCameraResultReady` → `IsActiveSender()` | 非活动相机的帧 / 结果**直接丢弃**；累计计数 + 5 秒限流记一条 Warning；热路径仅两次 `Interlocked` + 一次 `Volatile.Read`，无分配、无锁 |

- 防线① 先写 `_active` 再释放上一台：释放过程中的在途帧必然被判为「非活动发送方」而被防线③丢弃，因此释放窗口不污染共享点缓冲；
- 防线② 只判 `IsRunning`（采集态）不判 `IsConnected`：`VirtualCam.IsConnected` 恒为 true，用连接态会把虚拟相机误判为永久占用；
- 防线③ 是最后一道闸：将来若出现绕过 `SetActive` 的直连路径，单活语义仍成立；
- 正常单活运行下防线③ 零命中、零日志，不产生噪音。

## 约束（后续必须遵守）

- ⛔ **单活**：真实英莱相机与虚拟相机不得同时连接 / 采集；切换、连接、事件接收三处必须保持本章「七」的三道防线不被移除（H10，[[standards/ModuleOrganizationPattern]]）；
- ⛔ 业务与流程层**禁止**出现 `IntelligentLaserCam` / `VirtualCam` 的 `new` 与 `as` 转型（含 `Active as IntelligentLaserCam`）；
- ⛔ 派生类不得声明私有 `Tag` / `Log`；
- ⛔ 实现层不得重新引入业务分支、Mat 生成、产品记录或厂商类型外泄（中性事件是唯一出口）；
- ⛔ 数据/显示不得再开双事件通道（ADR-027 单通道结论）；
- 新增相机能力优先加在**抽象层**用 `public virtual` 给默认实现；
- 只有一个消费者的辅助类不单独立文件，与消费者同文件但保持独立类。

## 后果

- 正面：换相机只需实现两个 Raise 中性回调；业务集中在 Manager，显示链路可独立开关；绕过管理器的路径全部封死，抽象层互换性兑现；
- 负面 / 注意：`LineLaserCameraBase.CurrentMat` 语义变为「由业务层回写的最近显示帧」，实现层不再主动生成；`AcquisitionCompletedSignal` 仍由实现层 Set，契约不变；MainPage 常驻轮询线程须随页面销毁回收。

## 落地清单（三页并集）

| 项 | 状态 |
|---|---|
| L2 抽象（`LineLaserType` / `LineLaserEventArgs` / `LineLaserCameraBase`）+ 中性类型（`LineLaserSeamResult` / `LineLaserCalibration` / `LineLaserMatEventArgs`） | ✅ |
| 英莱 / 虚拟改继承基类（含 `Raise*Ready` 埋点），英莱回调瘦身（删 GDI 250 行 / 产品记录 / 模式分支 / 双通道事件） | ✅ |
| `CameraRegistry` / `LineLaserConfig` / `LineLaserManager`（类型访问器 + 外设代理 + 业务处理） | ✅ |
| 删除 SmartRayCam / HikRobotCam / Api + `Mv3dLpNet` 引用；csproj 删 15 项 / 增 6 项 | ✅ |
| 消费方改造（工作流 / `DeviceControlWork` / MainPage 轮询 / ILCamPage 订阅 / 算法编辑窗，21 处调用点） | ✅ |
| 缺陷修复（`HasValidResult`→`Result.Valid`、补 `StartAcquisition`、虚拟相机 33ms 模拟节拍） | ✅ |
| Python 静态校验（18 项 + 50 项） | ✅ 全过 |
| **真编译** | ⏳ **待 Visual Studio**（沙箱无 C# 编译器） |

## 后果

- 正面：换相机只需实现两个 Raise 中性回调；业务集中在 Manager，显示链路可独立开关；绕过管理器的路径全部封死，抽象层互换性兑现；
- 负面 / 注意：`LineLaserCameraBase.CurrentMat` 语义变为「由业务层回写的最近显示帧」，实现层不再主动生成；`AcquisitionCompletedSignal` 仍由实现层 Set，契约不变；MainPage 常驻轮询线程须随页面销毁回收。

## 被推翻的中间态

- **Y 轴 PVT 注入链（原 ADR-032 D6/D7）已废止**：`LineLaserManager.AttachYAxis(IPVTMotion)` / `SeamPvtFeeder` / 结果侧直写 PVT 的流式下载方案，已被 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] 推翻——`SeamPvtFeeder` 与 `AttachYAxis` 整类删除，Y 轴轨迹构造经 SeamTrajectoryBuilder（⛔ 已废弃，ADR-037 deprecated）演进为 `SeamTrackingAlgorithm`，现行实时方案见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]；
- **三辅助类独立保留结论已演进**：`ProfileSnapshot` / `ProfileMatRenderer` / `SeamPvtFeeder` 曾裁定「独立类并入 `LineLaserManager.cs` 同文件」（单消费者不立文件），其中 `SeamPvtFeeder` 已随 ADR-008 删除，其余两类的归属随后续线激光/焊参算法演进（ADR-028/041）调整，以 [[modules/LineLaserCam]] 现行页为准。

## 沿革

- **2026-09-08**：ADR-003 三层重构 + SmartRay/海康 3D 移除落地（L2 三文件、Manager/Registry/Config、csproj 删 15 增 6、消费方 5 文件 21 处调用点、Python 静态校验 18 项全过）；
- **2026-09-08（同日）**：ADR-032 职责再分工落地（实现层 1746→1324 行，删 GDI 250 行；中性事件与结构；Manager 两业务处理；MainPage 轮询）；ADR-033 单一入口落地（实例收口 + 外设代理 + 修 `HasValidResult` 编译错 + 补 `StartAcquisition` + 虚拟相机 33ms 模拟节拍定时器——此前 `PreWork` 凑不满 5 帧稳定判据必然超时）；
- **2026-09-11**：ADR-037 deprecated，PVT 注入链被 ADR-008 取代；
- **2026-09-14**：SmartRayConverter 链被 ADR-031 整链删除（推翻本页曾裁定保留的结论）；
- **2026-09-17 · 本页整合**：ADR-032/036 并入本页，删除被推翻的中间态表述，收拢全部现行裁定；整合后 status: accepted、tags 含 merged、`merged_from` 指向两个被并页；
- **2026-11-09**：新增「七、单活约束」——把「一次只能连一种线激光或虚拟相机」从调用约定升为代码保证（切换即释放 / 连接前置拒绝 / 事件发送方身份校验 + 限流日志），同步 [[standards/ModuleOrganizationPattern]] H10。

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- 模块：[[modules/LineLaserCam]] · [[api/LineLaserManager]] · [[api/IntelligentLaserCam]] · [[api/VirtualCam]]
- 上游范式：[[modules/MotionControl]] · [[decisions/ADR-016-WorkflowResponsibilityBoundary]] · [[decisions/ADR-021-CameraConnectionStateDecoupled]]（结论仍有效）· [[decisions/ADR-035-RawDesignRefinement20260903]]（配置范式）
- 下游演进：[[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] · [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] · [[decisions/ADR-032-SimulationTestRedesign]]
- 教训：[[lessons/StepDrivenWorkflowPitfalls]]（七.3）· [[lessons/IntelligentLaser-Pitfalls]]（D5 有意推翻处）
- 已并入本页（纯文本存档）：ADR-032-LineLaserResponsibilitySplit · ADR-033-LineLaserManagerSingleEntry
