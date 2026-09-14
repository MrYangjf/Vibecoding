---
title: API — LineLaserManager 线激光管理器（业务层单例 + 结果/轮廓业务处理点）
date: 2026-09-08
updated: 2026-09-11
tags: [API, 相机, 线激光, 管理器, 单例, 业务层, 依赖注入, ADR-034, ADR-035, ADR-040]
source: AdaWeldSystem/LineLaserCam/LineLaserManager.cs
---

# API — LineLaserManager 线激光管理器

> **位置**：`LineLaserCam/LineLaserManager.cs`（命名空间 `AdaWeldSystem.LineLaserCam`）
> **2026-09-08 新增**：取代已删除的 `CameraSelector`（见 [[decisions/ADR-034-LineLaserThreeLayerRefactor]]）。
> **2026-09-08 二次分工（ADR-035）**：从「只转发事件」升级为**业务处理中枢**——结果侧算 Y 轴 PVT 点并下载，
> 轮廓侧做产品记录、点缓冲与按需 Mat 生成；实现层只发 `ResultReady` / `ProfileReady` 两个回调。
> **2026-09-11 三次分工（ADR-040，⛔ 推翻「结果侧写 PVT」）**：结果侧**只缓存并转发** `ResultReady`，
> `AttachYAxis` 与内嵌 `SeamPvtFeeder` 删除；Y 轴轨迹构造迁至 [[api/SeamTrajectoryBuilder]]（WeldParamControl 模块）。
> **定位**：业务层唯一装配点。面向 L2 抽象 `LineLaserCameraBase` 编程；具体相机类型 `IntelligentLaserCam` / `VirtualCam` **仅在本文件的惰性创建处出现**。
> **职责**：相机注册与选中、结果转发与轮廓处理、连接态派生、显示开关、配置持久化。

## 公共 API

### 注册与选中

| 成员 | 签名 | 说明 |
|------|------|------|
| `Instance` | `static LineLaserManager` | 单例（`Lazy<T>`） |
| `Cameras` | `CameraRegistry { get; private set; }` | 相机注册表（按名登记与查询） |
| `Config` | `LineLaserConfig { get; private set; }` | 配置实体，构造时创建并加载 |
| `Active` | `LineLaserCameraBase { get; }` | 当前相机；未显式选择时按 `Config.DefaultKind` 惰性创建 |
| `ActiveName` | `string { get; }` | 当前相机键名，无相机时为 `""` |
| `Kind` | `LineLaserKind { get; }` | 当前相机种类（`None` / `IntelligentLaser` / `Virtual`） |
| `IsVirtual` | `bool { get; }` | 是否为虚拟调试相机 |
| `IsWorking` | `bool { get; }` | 工作流是否正在驱动相机出图 |
| `ConnectionState` | `LineLaserConnectionState { get; }` | 连接态派生：`Working` / `Connected` / `Disconnected` |
| `Register` / `Unregister` / `Get` | — | 登记（即订阅三个事件）/ 退订 / 按名取相机 |
| `SelectIntelligentLaser` / `SelectVirtual` / `Select` | — | 创建（首次）并选中对应相机，随后套用配置 |
| `StartAcquisition` / `StopAcquisition` | `void ()` | 当前相机的启动/停止采集便捷入口 |
| `IntelligentLaser` | `IntelligentLaserCam { get; }` | **英莱相机实例**（管理器持有，首次访问创建并登记），厂商专属页经此取实例 |
| `VirtualCamera` | `VirtualCam { get; }` | **虚拟相机实例**，同上 |
| `Connect` / `Disconnect` | `bool ()` / `void ()` | 连接 / 断开当前相机（`Connect` 已连接时直接返回 true） |
| `ConfigureDefaultCommPeriod` | `bool ()` | 配置当前相机默认回调周期 |
| `IsCameraOn` / `IsLaserOn` | `bool ()` | 传感器 / 激光是否开启 |
| `SetSensor` / `SetLaser` | `void (bool enable)` | 开关传感器 / 激光 |
| `ShutdownPeripherals` | `void ()` | 停采集 → 关激光 → 关传感器，吞掉单体异常，用于停机与异常收尾 |
| `LoadConfig` / `SaveConfig` | `void ()` | 重新加载 / 落盘 `Config/XML/LineLaserConfig.xml` |
| `Dispose` | `void ()` | 非 UI 类标准释放（[[decisions/ADR-001-DisposePattern]]），退订并释放全部相机与渲染器 |

### 业务产出（2026-09-08 新增）

| 成员 | 签名 | 说明 |
|------|------|------|
| `Profile` | `ProfileSnapshot { get; }` | **轮廓帧快照**（双缓冲 + 版本号），供主页面线程按节拍轮询刷新 ScottPlot；只读约定，勿跨帧持有数组 |
| `LastResult` | `LineLaserSeamResult { get; }` | 最近一次焊缝识别结果 |
| `ResultReady` | `event EventHandler<LineLaserResultEventArgs>` | 识别结果就绪事件，转发自相机；`LineLaserWorkflow` 订阅触发焊接工艺计算，`MotionControlWorkflow` 订阅驱动 Y 轴轨迹构造 |
| `MatUpdated` | `event EventHandler<LineLaserMatEventArgs>` | 轮廓 Mat 更新事件，**仅显示处理开启时触发**；订阅方须自行 `Clone()` |
| `CameraStateChanged` | `event EventHandler<LineLaserStateEventArgs>` | 相机状态变化事件，转发自已登记相机 |
| `SetDisplayOptions` | `void (bool enabled, double fps, bool convertMat)` | 显示处理开关：是否开启 / 目标帧率 / 是否生成 Mat |
| `DisplayEnabled` / `DisplayFps` / `ConvertMatEnabled` | 只读属性 | 当前显示处理参数（默认 `false` / `15` / `true`） |
| `SetWorking` | `void (bool working)` | 工作流采集开始/结束时调用，只驱动「工作中」连接态派生 |

> ⛔ **2026-09-11 删除（ADR-040）**：`AttachYAxis(IPVTMotion)` 已移除，本管理器不再注入运动能力、不写 PVT。
> Y 轴装配与轨迹写入改由 [[api/MotionControlWorkflow]] 驱动 [[api/SeamTrajectoryBuilder]]。

> ⛔ 已删除：`FrameReady`（Mat 帧事件）由 `MatUpdated` 取代，避免数据/显示双通道（ADR-027 反例）。

## 使用模式

```csharp
// 1. 选中相机（首次访问 Active 会按配置默认种类自动创建英莱相机）
LineLaserManager.Instance.SelectIntelligentLaser();
LineLaserCameraBase camera = LineLaserManager.Instance.Active;

// 2. 订阅结果事件（工作流/业务方）与 Mat 更新事件（手动调试页面）
LineLaserManager.Instance.ResultReady += OnResultReady;
LineLaserManager.Instance.MatUpdated += OnMatUpdated;

// 3. 主页面轮询取点（独立线程，版本号未变则跳过）
ProfileSnapshot snap = LineLaserManager.Instance.Profile;
if (snap.Version != _lastVersion)
{
    _lastVersion = snap.Version;
    // snap.Ys / snap.Zs / snap.Count / snap.HasResult / snap.FeatureY / snap.FeatureZ
}

// 4. Y 轴装配改由运控工作流完成（ADR-040）：轴注入 SeamTrajectoryBuilder，不注入本管理器
MontionAxis yAxis = MontionManager.Instance.GetAxis(LineLaserManager.Instance.Config.SeamTrackAxisName);
SeamTrajectoryBuilder.Instance.AttachAxis(yAxis);   // 见 api/SeamTrajectoryBuilder

// 5. 按需开启显示处理（UI 决定时机）
LineLaserManager.Instance.SetDisplayOptions(true, 15.0, true);
```

## 协作者

| 类 | 文件 | 职责 |
|---|---|---|
| `ProfileMatRenderer` | `LineLaserCam/LineLaserManager.cs`（同文件内嵌类） | 轮廓 → Mat（画布一次分配、每帧 Clear 重绘；校准框/十字架/mm 刻度/特征点） |
| `ProfileSnapshot` | `LineLaserCam/LineLaserManager.cs`（同文件内嵌类） | 轮廓点双缓冲快照，`MaxPoints = 2048`，带递增 `Version` |

## 约束

- **禁止**在业务代码 `new IntelligentLaserCam` / `new VirtualCam`；需厂商特化能力时经 `Instance.IntelligentLaser` 取实例（如 `ILCamPage` / `ILParamForm` 调 `FetchCameraParams`），**禁止**写 `Active as IntelligentLaserCam`（ADR-040）。
- **外设一律代理**：工作流与流程层不得直接调用相机对象的连接 / 激光 / 传感器方法，改走 `Connect` / `SetLaser` / `SetSensor` / `ShutdownPeripherals`（ADR-040）。
- **本管理器不碰运动**：⛔ 不得持有 `IPVTMotion` / `MontionManager` / `MontionControl` / `Delta*`；结果侧只转发 `ResultReady`，Y 轴轨迹构造归 [[api/SeamTrajectoryBuilder]]（ADR-040）。
- 事件在 SDK 原生线程触发，UI 订阅方须自行 `InvokeRequired` 封送（[[guides/WinForms-UI-Threading]]）。
- 基类事件只能在声明类内部赋值；派生类与外部一律 `+=` / `-=`（[[lessons/CSharp-Language-Pitfalls]] §3.4）。
- `MatUpdated` 携带的 Mat 与相机 `CurrentMat` **共享同一实例**，订阅方必须 `Clone()` 后再跨帧持有。
- 日志直连 `GlobalCommData.ShowLog`，标签为「线激光管理器」/ 相机键名，纯文本无符号（[[standards/CodeSimplification]]）。⛔ 原「焊缝跟踪」标签随 `SeamPvtFeeder` 删除。
- `SetWorking` 属状态切换，按 ADR-031 **不输出日志**。
- ⚠️ PVT 时间基准与速度前馈已随 PVT 写入迁至 [[api/SeamTrackingAlgorithm]]（由 [[api/WeldParamManager]] 持有，待现场实测），本页不再涉及。

## 关联

- 三层架构与铁律：[[modules/LineLaserCam]]
- 抽象基类：`LineLaserCam/ILineLaser/LineLaserCameraBase.cs`
- 决策：~~[[decisions/ADR-040-SeamGuideTrajectoryBuilder]]~~ → [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]]、[[decisions/ADR-035-LineLaserResponsibilitySplit]]、[[decisions/ADR-034-LineLaserThreeLayerRefactor]]、[[decisions/ADR-013-CameraConnectionStateDecoupled]]
- 实现：[[api/IntelligentLaserCam]]、[[api/VirtualCam]]
- Y 轴轨迹构造：[[api/SeamTrackingAlgorithm]]（WeldParamControl 模块）
- 运控侧：[[api/MontionManager]]、[[guides/DeltaEtherCAT-AdvancedMotion]]
