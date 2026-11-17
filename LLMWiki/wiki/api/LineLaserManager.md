---
title: API — LineLaserManager 线激光管理器（业务层单例 + 结果/轮廓业务处理点）
date: 2026-09-08
updated: 2026-11-09
tags: [API, 相机, 线激光, 管理器, 单例, 业务层, 依赖注入, ADR-003, ADR-032, ADR-037]
source: AdaWeldSystem/LineLaserCam/LineLaserManager.cs
---

# API — LineLaserManager 线激光管理器

> **位置**：`LineLaserCam/LineLaserManager.cs`（命名空间 `AdaWeldSystem.LineLaserCam`）
> **2026-09-08 新增**：取代已删除的 `CameraSelector`（见 [[decisions/ADR-024-LineLaserThreeLayerRefactor]]）。
> **2026-09-08 二次分工（ADR-032）**：从「只转发事件」升级为**业务处理中枢**——结果侧算 Y 轴 PVT 点并下载，
> 轮廓侧做产品记录、点缓冲与按需 Mat 生成；实现层只发 `ResultReady` / `ProfileReady` 两个回调。
> **2026-09-11 三次分工（ADR-037，⛔ 推翻「结果侧写 PVT」）**：结果侧**只缓存并转发** `ResultReady`，
> `AttachYAxis` 与内嵌 `SeamPvtFeeder` 删除；Y 轴轨迹构造迁至 api/SeamTrajectoryBuilder（⛔ 已废弃删除，ADR-008 起由 [[api/SeamTrackingAlgorithm]] 承接）（WeldParamControl 模块）。
> **定位**：业务层唯一装配点。面向 L2 抽象 `LineLaserCameraBase` 编程；具体相机类型 `IntelligentLaserCam` / `VirtualCam` **仅在本文件的惰性创建处出现**。
> **职责**：相机注册与选中、结果转发与轮廓处理、连接态派生、显示开关、配置持久化。
> **轮廓帧 X 来源（ADR-045 演进）**：`ProductFileRecordManager.AddFrame` 的第二参数直读 `WeldParamManager.Instance.CurrentRobotX`。模拟路由（`SimTick → UpdateRobotPose`）与真实路由（RSI `OnRobotDataReceived`）两条写入链都汇入该属性，⛔ 不得改为按运行模式分支取数；本文件不再依赖 `MainDeviceControl` 命名空间。

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
| `Connect` / `Disconnect` | `bool ()` / `void ()` | 连接 / 断开当前相机（`Connect` 已连接时直接返回 true）。**2026-11-09 增补**：连接前若其他已登记相机仍在采集，拒连并记 Error（单活约束，ADR-024「七」） |
| `ConfigureDefaultCommPeriod` | `bool ()` | 配置当前相机默认回调周期 |
| `DescribeLastError` | `string (LineLaserErrorContext)` | 当前相机最近一次失败的成品描述（连接 / 初始化 / 识别 / 指令返回码）；未选相机时返回明确的未提供说明。⛔ UI 与工作流只读，不自行拼 `ret=` |
| `IsCameraOn` / `IsLaserOn` | `bool ()` | 传感器 / 激光是否开启 |
| `SetSensor` / `SetLaser` | `void (bool enable)` | 开关传感器 / 激光 |
| `ShutdownPeripherals` | `void ()` | 停采集 → 关激光 → 关传感器，吞掉单体异常，用于停机与异常收尾 |
| `LoadConfig` / `SaveConfig` | `void ()` | 重新加载 / 落盘 `Config/LineLaser/LineLaser_XML/LineLaserConfig.xml` |
| `Dispose` | `void ()` | 非 UI 类标准释放（ADR-002（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）），退订并释放全部相机与渲染器 |

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
| `SwitchJob` | `int (int jobId)` | **线激光分析 Job 切换的唯一入口**（转发相机）；成功（`ret==0`）时触发 `JobChanged`。UI 调试界面与机器人指令均须经此入口，方可自动入档（[[decisions/ADR-037-ProductProductionRecordLifecycle]] 决 5） |
| `FetchCurrentJobId` | `int ()` | 读当前 Job 编号（转发相机） |
| `JobChanged` | `event EventHandler<int>` | **Job 切换成功事件**（2026-09-20 新增）：切换属调整的一种，订阅方 `DeviceControlWork.OnLineLaserJobChanged` 仅在**焊接态**（线激光子流程 `Working`）把切换点写入 `.pDat`（`ActionType=JobSwitch`）；⛔ 不入轮廓记录 |

> ⛔ **2026-09-11 删除（ADR-037）**：`AttachYAxis(IPVTMotion)` 已移除，本管理器不再注入运动能力、不写 PVT。
> Y 轴装配与轨迹写入改由 [[api/MotionControlWorkflow]] 驱动 api/SeamTrajectoryBuilder（⛔ 已废弃删除，ADR-008 起由 [[api/SeamTrackingAlgorithm]] 承接）。

> ⛔ 已删除：`FrameReady`（Mat 帧事件）由 `MatUpdated` 取代，避免数据/显示双通道（ADR-023 反例）。

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

// 4. Y 轴装配改由运控工作流完成（ADR-037）：轴注入 SeamTrajectoryBuilder，不注入本管理器
MontionAxis yAxis = MontionManager.Instance.GetAxis(MontionManager.Instance.MoveData.MotionConfig.SeamTrackAxisName);  // 焊缝跟踪轴名 2026-09-20 起归运控 DeltaMotionConfig（ADR-033），不再取自 LineLaserManager.Config
SeamTrajectoryBuilder.Instance.AttachAxis(yAxis);   // 见 api/SeamTrajectoryBuilder

// 5. 按需开启显示处理（UI 决定时机）
LineLaserManager.Instance.SetDisplayOptions(true, 15.0, true);
```

## 协作者

| 类 | 文件 | 职责 |
|---|---|---|
| `LineLaserContourAlgorithm` | `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` | 轮廓 → Mat（画布一次分配、每帧 Clear 重绘；校准框/十字架/mm 刻度/特征点）。沿革：原 LineLaserManager 内嵌 `ProfileMatRenderer`，2026-09-09 ADR-028 上提，见 [[api/LineLaserContourAlgorithm]] |
| `ProfileSnapshot` | `LineLaserCam/LineLaserManager.cs`（同文件内嵌类） | 轮廓点双缓冲快照，`MaxPoints = 2048`，带递增 `Version` |

## 约束

- ⛔ **单活（强制，2026-11-09）**：一次只允许一种线激光或虚拟相机在连接/采集，由本类三段代码执行——`SetActive`→`ReleaseCamera`（切换即停采集+断开上一台）、`Connect`→`FindOtherRunningCamera`（他台在采集则拒绝并记 Error）、`OnCameraProfileReady`/`OnCameraResultReady`→`IsActiveSender`（非活动发送方帧丢弃，累计计数 + 5 秒限流 Warning，热路径无分配无锁）。⛔ 不得移除或放宽为仅靠调用顺序（[[decisions/ADR-024-LineLaserThreeLayerRefactor]]「七」/ [[standards/ModuleOrganizationPattern]] H10）。
- **禁止**在业务代码 `new IntelligentLaserCam` / `new VirtualCam`；需厂商特化能力时经 `Instance.IntelligentLaser` 取实例（如 `ILCamPage` / `ILParamForm` 调 `FetchCameraParams`），**禁止**写 `Active as IntelligentLaserCam`（ADR-037）。
- **外设一律代理**：工作流与流程层不得直接调用相机对象的连接 / 激光 / 传感器方法，改走 `Connect` / `SetLaser` / `SetSensor` / `ShutdownPeripherals`（ADR-037）。
- **本管理器不碰运动**：⛔ 不得持有 `IPVTMotion` / `MontionManager` / `MontionControl` / `Delta*`；结果侧只转发 `ResultReady`，Y 轴轨迹构造归 api/SeamTrajectoryBuilder（⛔ 已废弃删除，ADR-008 起由 [[api/SeamTrackingAlgorithm]] 承接）（ADR-037）。
- 事件在 SDK 原生线程触发，UI 订阅方须自行 `InvokeRequired` 封送（[[guides/WinForms-UI-Threading]]）。
- 基类事件只能在声明类内部赋值；派生类与外部一律 `+=` / `-=`（[[lessons/CSharp-Language-Pitfalls]] §3.4）。
- `MatUpdated` 携带的 Mat 与相机 `CurrentMat` **共享同一实例**，订阅方必须 `Clone()` 后再跨帧持有。
- 日志直连 `GlobalCommData.ShowLog`，标签为「线激光管理器」/ 相机键名，纯文本无符号（[[standards/CodeSimplification]]）。⛔ 原「焊缝跟踪」标签随 `SeamPvtFeeder` 删除。
- `SetWorking` 属状态切换，按 ADR-008 **不输出日志**。
- ⚠️ PVT 时间基准与速度前馈已随 PVT 写入迁至 [[api/SeamTrackingAlgorithm]]（由 [[api/WeldParamManager]] 持有，待现场实测），本页不再涉及。

## CameraRegistry（相机注册表）

> 2026-09-17 补记（源码核对：`LineLaserCam/CameraRegistry.cs`）。

统一管理业务层用到的全部线激光相机，按键名登记并保证同一键名只有一个实例（`Dictionary<string, LineLaserCameraBase>`）。**本表只做索引与枚举**；登记与退订由 [[api/LineLaserManager]] 负责——**登记即订阅事件**，与「LineLaserManager 是模块唯一入口」（ADR-033）一致，外部不得绕过 Manager 直接操作注册表内的相机对象。

| 成员 | 签名 | 职责 |
|---|---|---|
| `Register` | `void (string name, LineLaserCameraBase camera)` | 登记相机，同名覆盖（null / 空名忽略） |
| `Get` | `LineLaserCameraBase (string name)` | 按键名取相机，未找到返回 `null` |
| `Contains` | `bool (string name)` | 判断是否已登记 |
| `GetAll` / `GetNames` | `List<LineLaserCameraBase> ()` / `List<string> ()` | 取全部相机 / 全部键名 |
| `Remove` / `Clear` | `void (string name)` / `void ()` | 移除单个 / 清空 |
| `Count` | `int { get; }` | 已登记数量 |

## 关联

- 三层架构与铁律：[[modules/LineLaserCam]]
- 抽象基类：`LineLaserCam/ILineLaser/LineLaserCameraBase.cs`
- 决策：~~ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）~~ → [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]、ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[decisions/ADR-024-LineLaserThreeLayerRefactor]]、[[decisions/ADR-021-CameraConnectionStateDecoupled]]
- 实现：[[api/IntelligentLaserCam]]、[[api/VirtualCam]]
- Y 轴轨迹构造：[[api/SeamTrackingAlgorithm]]（WeldParamControl 模块）
- 运控侧：[[api/MontionManager]]、[[guides/DeltaEtherCAT-AdvancedMotion]]
