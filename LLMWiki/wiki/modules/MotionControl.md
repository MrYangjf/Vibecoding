---
title: MotionControl 模块 — 运控调整
date: 2026-07-31
tags: [模块, 运控, 水平移动, 模拟测试, 运动轴, 状态机]
source: AdaWeldSystem/MotionControl/ 模块源码
---

# MotionControl 模块 — 运控调整

> 独立运控调整模块（**不再挂载于 InteliWeld**），负责：① 线激光前装标定的水平移动距离计算与缓存（`MoveControlData`）；② **运动控制器架构（`IMotionController` + `MotionControllerBase` + `IAxis` + `IIO` + `MotionManager`）**；③ 正运动4轴硬件实现（`ZMotion/` 子目录）；④ 运控调整工作流（`MotionControlWorkflow` 状态机：水平移动后台线程；模拟 A/B/C 与共享 robotX 由 [[api/DeviceControlWork]] 统一驱动）。
> 设计遵循 ADR-009 的「独立模块 + Run/Workflow 分离」范式与 ADR-012。

## 目录结构

```
MotionControl/
├── API/
│   ├── IAxis.cs                       ← 运动轴接口
│   ├── IIO.cs                         ← IO 接口
│   ├── IMotionController.cs           ← 运动控制器接口
│   └── MotionControllerBase.cs        ← 运动控制器抽象基类
├── ZMotion/                           ← 正运动控制器实现
│   ├── ZMotionNative.cs               ← 原生 DLL P/Invoke 封装
│   ├── ZMotionNativeLaser.cs          ← 激光振镜 DLL P/Invoke 封装（2026-08-11，依赖 ZmotionScanLaser.dll）
│   ├── ZMotionGalvo.cs                ← 振镜控制高级封装（2026-08-11）
│   ├── ZMotionAxis.cs                 ← 正运动轴实现（IAxis）
│   ├── ZMotionIO.cs                   ← 正运动 IO 实现（IInputIO/IOutputIO）
│   ├── ZMotionController.cs           ← 正运动控制器（继承 MotionControllerBase）
│   ├── EncoderAxis.cs               ← 通讯编码器轴封装（ATYPE=25）
│   ├── CamBoxTracker.cs             ← CAMBOX 跟踪引擎
│   ├── InterpolationEngine.cs       ← 连续插补引擎（封装 ZAux 多轴插补）
│   └── RSIPositionBuffer.cs         ← RSI 位置时间戳环形缓冲
├── MotionManager.cs                   ← 运动管理器（单例，默认初始化正运动 ZMotion 控制器）
└── MoveControlData.cs                 ← 标定 + 计算 + 缓存
```

> **2026-08-04 层级更新**：接口与基类文件统一归入 `API/` 子目录。
>
> **2026-08-04 命名空间规范化**：`API/` 子目录命名空间为 `AdaWeldSystem.MotionControl.API`，根目录为 `AdaWeldSystem.MotionControl`。
>
> **状态机已消失（2026-08-28 起）**：`MotionControlStateMachine.cs`（现役 `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs`） 与 `DeviceStateMachine/` 目录**均已删除**；运控不再持有独立状态机实例，状态由 `MotionControlWorkflow` 经基类 `DeviceStateBase` 承载（三态模型，2026-09-02 ADR-034）。

## 核心文件

| 文件 | 职责 |
|------|------|
| `API/IMotionController.cs` | **运动控制器接口（2026-08-03 新增）**：管理轴和IO的控制器抽象，参考 PcomDeviceInterface 设计模式 |
| `API/MotionControllerBase.cs` | **运动控制器抽象基类（2026-08-03 新增）**：实现轴列表/IO列表管理，子类实现硬件连接/断开/急停 |
| `API/IAxis.cs` | **运动轴接口（2026-08-03 新增）**：定义单轴运动控制操作（MoveTo/MoveRelative/Stop/ServoOn/Home/Jog） |
| `API/IIO.cs` | **IO接口（2026-08-03 新增）**：`IIO`/`IInputIO`/`IOutputIO` 输入输出IO泛化接口 |
| MotionManager.cs | **运动控制器管理器（2026-08-03 新增）**：单例，统筹所有控制器/轴/IO的创建与管理；`Initialize()` 默认初始化正运动(ZMotion)控制器（2026-08-21 起，见 [[decisions/ADR-027-DefaultInitZMotion]]） |
| MoveControlData.cs | 运控标定数据 + 水平移动计算 + 水平移动缓存（单例） |
| **ZMotion/ZMotionController.cs** | **正运动控制器实现（2026-08-10 新增）**：继承 MotionControllerBase，以太网连接正运动控制器，管理4轴+8IO |
| **ZMotion/ZMotionAxis.cs** | **正运动轴实现（2026-08-10 新增）**：实现 IAxis 接口，封装单轴运动/回零/点动/速度参数设置 |
| **ZMotion/ZMotionIO.cs** | **正运动IO实现（2026-08-10 新增）**：ZMotionInputIO / ZMotionOutputIO，实现输入输出IO操作 |
| **ZMotion/ZMotionNative.cs** | **正运动原生API封装（2026-08-10 新增）**：基于官方 Zmcaux.cs 精简，仅封装项目所需函数，依赖 zauxdll.dll |
| **ZMotion/ZMotionNativeLaser.cs** | **激光振镜原生API封装（2026-08-11 新增）**：基于 Demo5 的 ZmotionScanLaser.dll，覆盖基础配置/工艺参数/图形打标/填充/三次文件/平台联动 |
| **ZMotion/ZMotionGalvo.cs** | **振镜控制高级封装（2026-08-11 新增）**：面向业务的振镜/激光打标接口，集成于 ZMotionController.Initialize() |
| **ZMotion/InterpolationEngine.cs** | **连续插补引擎（2026-08-11 迁入 ZMotion/）**：封装 ZAux 多轴连续插补（MERGE/拐角/MultiMoveAbs/直线缓冲区流控），强耦合正运动硬件 |

> **工作流归属**：`MotionControlWorkflow` 现位于 `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs`（2026-08-28 由 `Workflow/` 迁入），继承**非泛型** `DeviceWorkflowBase`，命名空间 `AdaWeldSystem.MainDeviceControl.DeviceWorkflow`。
> **状态模型（2026-09-02 ADR-034 三态）**：连接态 `SubDeviceState` 与焊接过程态 `SubDeviceWeldStatus` 由基类 `DeviceStateBase` 承载，状态写入唯一入口为 `SetState`/`SetWeldStatus`，禁手工赋值。`MotionControlWorkflow` 只保留**私有**阶段枚举（`LaserCamBoxWorkflowState`）+ `MapWeldStatus(step)` 映射，不对外暴露，不再持有独立状态机实例（原 `DeviceStateMachine/` 目录已删除）。

## MoveControlData（标定 + 计算 + 缓存）

- 标定参数（单例，`Instance`）：`LaserFrontOffset` / `LaserToHorizontalAngleRad`(弧度) + `LaserToHorizontalAngleDeg`(度，写时换算) / `LaserToHorizontalScaleX` / `CalibratedCenterX,Y` / `ApproachThreshold`。
- **本地持久化**：`Load()`/`Save()` 读写 6 项标定参数至 `Config/INI/MoveControlData.ini`（`[Calibration]` 节）；`Save` 由 `MotionControlPage`「保存标定参数」触发，`Load` 在 `FormMain` 启动期、创建子页面前调用（参见 [[guides/Project-Tools]]）。
- 计算：`ComputeHorizontalMove(seamX, seamY) = (seamX − CalibratedCenterX) × cos(LaserToHorizontalAngleRad) × LaserToHorizontalScaleX`。
- 缓存：以 `robotX + LaserFrontOffset` 为键写入；`CacheHorizontalMove` / `TryGetNearestHorizontalMove`（阈值匹配，解决 cache X ≠ 实际 X）/ `RemoveHorizontalMove` / `ClearHorizontalMoveCache`。
- 组合：`ComputeAndCacheHorizontalMove(SeamFeatureResult, robotX)`（计算+缓存+日志），供 `WeldProcess` 真实流程与 `MotionControlWorkflow` 模拟流程统一调用，**单一算法真源**（避免逻辑分散）。

## MotionControlWorkflow（位于 `MainDeviceControl/DeviceWorkflow/`）

> ⚠️ **2026-07-20 架构纠正**：`MotionControlWorkflow` **不再持有独立模拟线程**。模拟模式（共享 robotX / A·B·C 模式 / 参数）统一由 [[api/DeviceControlWork]] 提供；本工作流仅：① 水平移动后台线程消费 `MoveControlData` 缓存；② 订阅 `PipelineManager.AlgorithmCompleted` 将线激光每帧焊缝特征缓存为水平移动距离。模拟开启时，运控按 `DeviceControlWork.ShouldMoveAxis`（B 运动、A/C 仅记录）切换输出。

- **私有**阶段枚举（内联本文件，不对外）：`LaserCamBoxWorkflowState { Idle, Initializing, WaitingForMaster, Tracking, Paused, Stopping, Error }`，经 `MapWeldStatus(step)` 映射到对外 `SubDeviceWeldStatus`；映射表单一维护点见 [[architecture/DeviceControlArchitecture]] §6。模拟模式枚举 `SimTestMode { None, ModeA, ModeB, ModeC }` 由 [[api/DeviceControlWork]] 持有（归并自原 SimulationWorkflow）。
- 水平移动后台线程 `HorizontalMoveWorker()`：消费 `MoveControlData` 缓存，`GetEffectiveRobotX()` 读取机器人X（模拟时返共享模拟 robotX，否则返真实），`TryGetNearestHorizontalMove` 命中阈值且 `DeviceControlWork.ShouldMoveAxis` 为真时 `MotionController.MoveHorizontal(move)` → `RemoveHorizontalMove(key)`；A/C 模式仅记录不运动。
- 焊缝特征缓存：订阅 `PipelineManager.AlgorithmCompleted`，将线激光流程（模拟时即虚拟相机）每帧 `SeamFeatureResult` + 当前有效 robotX 经 `MoveControlData.ComputeAndCacheHorizontalMove` 落缓存。
- 资源释放：~~`DisposeComponents()`~~（**2026-08-19 已废弃**——非 UI 类统一使用标准 `IDisposable.Dispose()`，见 [[decisions/ADR-001-DisposePattern]]）

## A / B / C 模拟测试模式

| 模式 | 相机 | 计算 | 记录 | 运动执行 |
|------|------|------|------|----------|
| A | 虚拟调试相机（`VirtualCameraRun`） | ✅ | ✅ | ❌ |
| B | 虚拟调试相机 | ✅ | ✅ | ✅（`MotionManager.GetAxis("水平轴").MoveTo`） |
| C | 真实相机（`CameraRun`） | ✅ | ✅ | ❌ |

> 水平移动后台线程由「开启模拟」按钮统一启动（见 [[api/DeviceControlWork]]）；B 模式经 `MotionController.MoveHorizontal` 实际运动，A/C 仅记录（由 `DeviceControlWork.ShouldMoveAxis` 控制）。模拟模式与参数统一归 [[api/DeviceControlWork]]，不再内嵌于本工作流。

## 运动控制器架构（2026-08-03 新增）

> 参考 PcomDeviceInterface 的 `MontionControl` 设计模式，实现「控制器基类 → 实例化（含多轴+多IO）→ 工作流控制轴和IO」的三层架构。

### 架构分层

```
┌─────────────────────────────────────────────────────────┐
│  MotionManager（单例管理器）                               │
│  统筹所有控制器/轴/IO的创建、注册、查询                    │
│  MotionManager.Instance.GetAxis("水平轴") → IAxis        │
│  MotionManager.Instance.GetOutputIO("焊枪启动") → IOutputIO│
├─────────────────────────────────────────────────────────┤
│  IMotionController 接口 / MotionControllerBase 抽象基类     │
│  管理轴列表(_axes) + IO列表(_inputIOs/_outputIOs)         │
│  AddAxis/RemoveAxis/GetAxis/AddIO/RemoveIO/GetInput/Output │
├─────────────────────────────────────────────────────────┤
│  IAxis 接口        │  IIO/IInputIO/IOutputIO 接口         │
│  MoveTo/MoveRelative │  GetIOStatus/SetON/SetOFF          │
│  Stop/ServoOn/Home │  EmergencyStopOff                    │
└─────────────────────┴───────────────────────────────────┘
```

### 核心接口

| 接口 | 职责 | 关键方法 |
|------|------|---------|
| `IMotionController` | 控制器抽象：管理轴和IO生命周期 | `Initialize()`/`Close()`/`AddAxis()`/`GetAxis()`/`AddIO()`/`GetOutput()`/`SetEmergencyStop()` |
| `IAxis` | 单轴运动控制 | `MoveTo()`/`MoveRelative()`/`Stop()`/`ServoOn()`/`ServoOff()`/`Home()`/`JogMove()`/`WaitMoveDone()` |
| `IInputIO` | 输入IO | `GetIOStatus()`/`IsEnabled` |
| `IOutputIO` | 输出IO | `SetON()`/`SetOFF()`/`EmergencyStopOff` |

### 默认初始化控制器（2026-08-21 起为正运动 ZMotion）

> **2026-08-21 架构调整（[[decisions/ADR-027-DefaultInitZMotion]]）**：默认初始化不再使用空实现（`NullMotionController` 已删除）。`MotionManager.Initialize()` 现在直接初始化正运动（ZMotion）控制器——读 `MotionConfigManager.Config.IpAddress`（默认 `192.168.0.11`），以太网连接硬件，按配置创建 Y轴/振镜轴/送丝伸缩臂轴/Z轴自动对焦轴 与 IO。CAMBOX 跟踪编排（`MotionControlWorkflow`）依赖该句柄，因此随正运动初始化自动就绪。
>
> 模拟模式（虚拟相机/焊缝轮廓模拟）由 `DeviceControlWork` 承载（[[api/DeviceControlWork]]），与运动控制器解耦。

### 使用模式

```csharp
// 1. 初始化控制器管理器（默认初始化正运动 ZMotion 控制器，按配置建轴/IO）
MotionManager.Instance.Initialize();

// 2. 工作流中按名称获取轴并控制
IAxis yAxis = MotionManager.Instance.GetAxis("Y轴");
yAxis.MoveTo(100.0, 20.0);  // 绝对运动到100mm，速度20mm/s

// 3. 获取输出IO并控制
IOutputIO weldStart = MotionManager.Instance.GetOutputIO("焊枪启动");
weldStart.SetON();

// 4. 对接真实硬件时替换控制器实现
// var realController = new RealMotionController("伺服控制器");
// MotionManager.Instance.RegisterController(realController);
```

## 正运动控制器实现（ZMotion）

> **2026-08-10 新增**：基于正运动（ZMotion）技术的运动控制器硬件对接实现，位于 `MotionControl/ZMotion/` 子目录。
> 设计遵循 [[decisions/ADR-022-ZMotionControllerIntegration]]。

### 4轴定义

| 轴号 | 轴名称 | 控制来源 | 说明 |
|------|--------|---------|------|
| 0 | Y轴 | 线激光焊缝焊接点引导 | 焊缝跟踪Y向修正，由线激光分析结果驱动 |
| 1 | 振镜轴 | 线激光焊缝宽度 | 设置摆动幅度和中心位置，配合焊接工艺摆动 |
| 2 | 送丝伸缩臂轴 | 外部压力信号 | 送丝臂伸缩控制，根据压力反馈调节伸出长度 |
| 3 | Z轴自动对焦轴 | 送丝臂位置传感器 | 自动对焦调整，跟随送丝臂位置变化 |

### 架构分层

```
ZMotionController（继承 MotionControllerBase）
├── 连接管理：ZAux_OpenEth / ZAux_Close（以太网）
├── 轴管理：4个 ZMotionAxis（实现 IAxis）
│   ├── 运动控制：Single_Move / MoveAbs / Vmove / Cancel
│   ├── 参数设置：SetSpeed / SetAccel / SetDecel / SetSramp
│   └── 状态读取：GetDpos / GetIfIdle / GetAxisEnable
└── IO管理：ZMotionInputIO / ZMotionOutputIO
    ├── 输入：ZAux_Direct_GetIn
    └── 输出：ZAux_Direct_SetOp / GetOp
```

### 使用方式

```csharp
// 使用正运动控制器初始化（默认 Initialize() 即走此路径；此方法提供显式 IP 覆盖）
bool success = MotionManager.Instance.InitializeWithZMotion("192.168.0.11");

// 获取Y轴并控制
IAxis yAxis = MotionManager.Instance.GetAxis("Y轴");
yAxis.MoveTo(5.0, 30.0);  // 绝对运动到5mm，速度30mm/s

// 获取振镜轴并控制
IAxis galvoAxis = MotionManager.Instance.GetAxis("振镜轴");
galvoAxis.MoveRelative(2.0, 100.0);  // 相对移动2mm

// 获取送丝伸缩臂轴
IAxis wireAxis = MotionManager.Instance.GetAxis("送丝伸缩臂轴");

// 获取Z轴自动对焦轴
IAxis zAxis = MotionManager.Instance.GetAxis("Z轴自动对焦轴");

// 控制IO
IOutputIO weldStart = MotionManager.Instance.GetOutputIO("焊枪启动");
weldStart.SetON();
```

### 部署依赖

- **原生 DLL**：`zauxdll.dll`（64位）源文件放于项目根 `3rdDepend\` 目录
- **构建拷贝**：通过 `CopyNative3rdDependToOutput` 构建目标在构建后自动拷贝到输出目录（`bin\Debug\` 或 `bin\Release\`）
- **运行时加载**：`DllImport` 从程序输出目录加载 DLL
- **来源**：正运动官方开发包 `64位库文件/zauxdll.dll`
- 详见 [[api/ZMotionController]]

## 正运动扩展功能架构（第2轮迭代）

> 2026-08-11 第二轮迭代，在基础4轴运动之上扩展高级运动控制功能和系统运维能力。

### 统一配置文件 MotionConfig.cs

**背景**：初期轴参数硬编码在 `ZMotionController.InitializeAxes()` 中，IO映射分散在多处，心跳参数无统一配置，存在三个独立的配置来源。

**解决方案**：创建 `MotionControl/Config/MotionConfig.cs` 统一配置类，将所有运动相关参数集中管理。

```
MotionConfig（统一配置类）
├── ControllerIp            ← 控制器IP地址
├── AxisConfigs             ← List<AxisConfig> 各轴参数
│   ├── Name / AxisNumber
│   ├── Units / LSpeed / Speed
│   └── Accel / Decel / Sramp
├── InputIOMap              ← Dictionary<string, int> 输入IO名称→索引
├── OutputIOMap             ← Dictionary<string, int> 输出IO名称→索引
├── HeartbeatIntervalMs     ← 心跳间隔
└── HeartbeatTimeoutCount   ← 心跳超时次数
```

- **替代三个独立config**：轴参数config + IO映射config + 心跳参数config → 统一为 `MotionConfig`
- **持久化格式**：INI 文件，存储于 `Config/INI/MotionConfig.ini`
- **加载/保存**：`MotionConfig.LoadConfig(path)` / `config.SaveConfig(path)`
- **默认回退**：加载失败时使用硬编码默认值，保证系统可启动

### 轴字典 / IO 字典设计模式

**设计模式**：在 `MotionControllerBase` 中引入字典查找机制，替代传统的按索引遍历。

```csharp
// 基类内部维护三个字典
protected Dictionary<string, IAxis> _axisDict;
protected Dictionary<string, IInputIO> _inputIODict;
protected Dictionary<string, IOutputIO> _outputIODict;

// 对外暴露统一查询接口
public IAxis GetAxis(string name);
public IInputIO GetInputIO(string name);
public IOutputIO GetOutputIO(string name);
```

**设计优势**：
- **语义化访问**：`GetAxis("Y轴")` 比 `GetAxis(0)` 更易读，减少索引硬编码
- **名称不敏感**：内部做大小写不敏感匹配，避免大小写导致的查找失败
- **空值安全**：名称不存在时返回 `null`，调用方需判空（避免 KeyNotFoundException）
- **集中映射**：IO名称与硬件索引的映射由 `MotionConfig.OutputIOMap` 统一配置
- **扩展友好**：新增轴/IO只需在配置中加一项，无需修改查询代码

### InterpolationEngine 连续插补引擎

**用途**：实现多段轨迹的连续无缝插补，适用于焊接、切割等需要平滑连续轨迹的工艺。

```
InterpolationEngine（位于 ZMotion/InterpolationEngine.cs）
├── 缓冲区管理：Queue<InterpSegment> 运动段队列
├── 前瞻机制：当前段运动时预写下一段，减少段间停顿
├── MoveSegment(axes, positions, speed, accel)  ← 追加运动段
├── Start() / Stop() / Pause() / Resume()       ← 引擎控制
└── IsRunning / CurrentSegmentIndex             ← 状态查询
```

**关键特性**：
- 支持 2~4 轴直线插补
- 前瞻缓冲：至少预存 2 段，保证运动连续性
- 动态追加：运行中可继续追加新段（流式插补）
- 与正运动控制器 BASIC 程序缓冲区协同工作

### 电子凸轮 CAMBOX 与追剪模式

**电子凸轮（CAMBOX）**：从轴按照凸轮表定义的非线性曲线跟随主轴运动，是实现复杂同步运动的核心机制。

```
电子凸轮架构
├── WriteCamTable(camIndex, table, count)  ← 写入凸轮表（主轴→从轴映射）
├── StartCambox(master, slave, camIndex)   ← 启动 CAMBOX 模式
├── StopCambox(slave)                      ← 停止 CAMBOX 模式
├── Movelink(master, slave, ratio)         ← 线性电子齿轮
└── Moveslink(master, slave, ratio, sramp) ← S曲线电子齿轮
```

**追剪模式**：追剪（飞剪）是电子凸轮的典型应用——主轴连续运动，从轴在一个周期内完成「加速同步→同步剪切→减速返回」的完整动作。

- 凸轮表设计：一个主轴周期对应从轴的完整追剪轨迹
- 同步精度：取决于凸轮表数据点密度和控制器插补精度
- 应用场景：定长剪切、飞锯、包装生产线等

### PTPVT 自定义曲线运动

**PTPVT（Point-To-Point Velocity Time）**：用户自定义「位置-速度-时间」序列，控制器自动样条插值生成平滑轨迹。

```
PTPVT 工作流程
1. PTPVT_Move(axis, pos, vel, time)   ← 逐个追加数据点（写入缓冲区）
2. PTPVT_Start(axis)                  ← 启动运动，按序列执行
3. PTPVT_Stop(axis)                   ← 停止并清空缓冲区
```

**适用场景**：
- 焊接工艺中的特殊速度曲线（如起弧慢、收弧慢、中间快）
- 振动抑制：自定义加减速曲线减小机械冲击
- 凸轮曲线生成：离线计算后通过 PTPVT 下发，替代 CAMBOX 方案

### 主动上报与周期上报机制

**两种上报模式**：

| 模式 | 触发方式 | 适用场景 | 底层命令 |
|------|---------|---------|---------|
| 主动上报（AutoReport） | 状态变化时触发 | 离散事件监控（IO变化、轴状态变化） | `BASE_REPORT` + `ON_REPORT` |
| 周期上报（CycleReport） | 定时采样触发 | 连续数据采集（位置、速度监控） | `REPORT` |

**架构设计**：

```
上报机制
├── StartAutoReport(item, index) / StopAutoReport
├── StartCycleReport(item, index, cycleMs) / StopCycleReport
├── OnReportData 事件            ← 统一的上报数据回调
└── 内部解析：将控制器上报的字符串解析为结构化数据
```

**优势**：相比上位机轮询，上报模式大幅减少以太网通信量，降低延迟，提高实时性。

### 心跳检测与 BAS 保护

**心跳检测**：监控上位机与控制器的通信链路健康状态。

```
心跳检测架构
├── StartHeartbeat(intervalMs, timeoutCount)  ← 启动后台心跳线程
├── StopHeartbeat()                           ← 停止心跳
├── CheckHeartbeat()                          ← 手动同步检测
├── OnHeartbeatLost 事件                      ← 心跳丢失触发
└── OnHeartbeatRestored 事件                  ← 心跳恢复触发
```

**BAS 保护（通信中断保护）**：
- 心跳连续丢失达到阈值时，触发 BAS 保护逻辑
- 保护动作：停止所有轴运动 → 关闭关键输出IO → 触发系统报警
- 遵循「故障安全」原则：通信中断时设备进入安全状态，而非继续运动
- 与 `SetEmergencyStop` 机制联动，但触发源不同（通信中断 vs 人工急停）

## CAMBOX 硬件级实时跟踪架构

> **核心理念**：运动实时链路 100% 硬件总线化，PC 退化为非实时轨迹规划器
> **决策依据**：[[decisions/ADR-023-RSICamBoxTrackingArchitecture]]
> **详细设计（全链路技术规范）**：[[architecture/DeviceControlArchitecture]] 第 10 章

### 架构要点

| 维度 | 实现 |
|------|------|
| 调整驱动 | EtherCAT 硬件 + CAMBOX 电子凸轮 |
| 实时性 | 亚 ms 级，零抖动 |
| PC 角色 | 仅轨迹规划 + 数据写入（非实时） |
| 焊缝保真 | 100% 原始焊缝（无平滑滤波） |
| 主轴来源 | ATYPE=25 通讯编码器轴（硬件同步） |

### 数据流（全链路无遗漏）

```
KUKA 机器人运动内核（RSI FastIPO 4ms 硬实时）
    ↓ EtherCAT PDO 周期推送（硬件级 4ms）
正运动 ZMC 控制器 EtherCAT 主站
    ↓ 映射至【ATYPE=25 通讯编码器轴】（硬件自动刷新位置）
CAMBOX 电子凸轮主轴 = 通讯编码器轴
    ↓ 硬件周期查表插值
Y 伺服从轴实时纠偏运动
    ↑
    │ ZAux_CamBox_AddPoint（PC 写入原始焊缝轨迹）
    │
上位机 PC（仅做三件事：时序缓存 / 插值对齐 / 写凸轮表）
```

### 核心组件

| 组件 | 文件路径 | 职责 |
|------|---------|------|
| **EncoderAxis** | `ZMotion/EncoderAxis.cs` | ATYPE=25 通讯编码器轴封装（主轴位置读取、清零、单位设置） |
| **CamBoxTracker** | `ZMotion/CamBoxTracker.cs` | CAMBOX 轨迹跟踪引擎（轨迹点追加、前置补偿、启停控制、超偏保护） |
| **RSIPositionBuffer** | `ZMotion/RSIPositionBuffer.cs` | RSI 位置+时间戳环形缓冲，激光帧时间插值对齐 |

### 轴定义

| 轴号 | ATYPE | 名称 | 角色 | 状态 |
|------|-------|------|------|------|
| AXIS 8 | **25** | 通讯编码器主轴 | KUKA 机器人进给主轴（CAMBOX 主轴） | 已实装 |
| AXIS 0 | 0 | Y 纠偏伺服从轴 | 焊缝横向纠偏（CAMBOX 从轴） | 已实装 |
| AXIS 1 | 0 | 振镜轴 | 焊缝宽度摆幅+中心 | 待实装 |
| AXIS 2 | 0 | 送丝伸缩臂轴 | 外部压力信号 | 待实装 |
| AXIS 3 | 0 | Z 轴自动对焦轴 | 送丝臂位置传感器 | 待实装 |

### 配置扩展（MotionConfig）

CAMBOX 跟踪配置段：

```
MotionConfig
├── ... （基础配置）
└── CamBoxTrackingConfig
    ├── MasterAxisIndex            ← 主轴轴号（默认 8）
    ├── SlaveAxisIndex             ← 从轴轴号（默认 0）
    ├── CamIndex                   ← CAMBOX 通道号
    ├── LaserFrontOffset           ← 激光前置距离（mm，默认 50.0）
    ├── MaxDeviation               ← 最大纠偏量（mm，默认 5.0）
    ├── TableLength                ← 凸轮表长度（点数，默认 10000）
    ├── Mode                       ← 跟随模式（位置跟随 / 速度跟随）
    ├── Direction                  ← 跟随方向（仅正向 / 双向）
    └── LaserTimeoutMs             ← 激光帧超时（ms，默认 200）
```

### PC 端工作逻辑（极简）

PC **不再驱动运动、不再滤波、不再参与实时链路**。仅做三件事：

1. **时序缓存**：接收机器人 ECAT 时间戳 + 主轴位置 S，建立时序环形缓冲（`RSIPositionBuffer`）
2. **插值对齐**：接收激光帧 (Y_offset, T_laser)，通过时间戳插值算出激光真实采集时刻的机器人位置 S_meas
3. **写入凸轮**：前置补偿 `Cam_Key = S_meas + LaserFrontOffset`，调用 `ZAux_CamBox_AddPoint` 写入 CAMBOX 表

### 异常保护体系

| 异常类型 | 保护动作 |
|----------|---------|
| EtherCAT 断连 | CAMBOX 立即停止，Y 轴锁止，报警停机 |
| 机器人停止运动 | Y 轴保持当前位置，不晃动 |
| 激光丢帧/无轮廓 | 停止加点，延续原有轨迹，不突变 |
| 超偏 | 超最大纠偏范围丢弃当前点，保护设备 |
| 时序异常 | 插值失败自动丢帧，不影响整体跟踪 |

### 已废弃内容与现存边界

| 内容 | 状态 | 说明 |
|------|------|------|
| 软件离散调整（`MoveAbsolute` 逐帧纠偏模式） | **已废弃，无 fallback** | 被 CAMBOX 硬件跟随完全取代；代码库不保留任何模式判断分支 |
| `LaserCamBoxTrackingWorkflow` | **已删除** | 曾经的 CAMBOX 编排工作流；2026-08-28 架构整合后由 `MotionControlWorkflow` 承载启停编排 |
| `WeldProcessAdjustmentWorkflow` | **已删除** | 无对应文件 |

> **易误判点**：①`MoveControlData` **仍然保留**——它负责标定参数持久化与水平移动计算/缓存，与 CAMBOX 硬件跟踪是并存关系而非替代关系；②`MotionControlWorkflow` **是现役工作流**（`MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs`），不是被废弃的旧组件，仅其内部的「软件逐帧调整」职责由 CAMBOX 接管，工作流本身负责 CAMBOX 的启停编排与设备态映射。

## 设计决策

- 运控数据/工作流**从 InteliWeld / Workflow 迁出**，归独立 `MotionControl` 模块（用户明确要求「控制流程的 UI 和数据需要遵循流程开发」、虚拟相机与 SmartRay 同级）。
- 运动轴控制采用三层架构：`IMotionController`(控制器级) + `IAxis`(轴级) + `IIO`(IO级)，通过 `MotionManager` 统一管理。
- 运动轴控制经 `IMotionController` 接口插拔；默认初始化直接使用正运动（ZMotion）控制器（2026-08-21 起，`NullMotionController` 空实现已删除，见 [[decisions/ADR-027-DefaultInitZMotion]]）。
- **正运动控制器对接（2026-08-10 新增）**：新增 `ZMotion/` 子目录实现正运动硬件对接，4轴（Y轴/振镜/送丝臂/Z对焦）+ 8IO；`MotionManager.Initialize()` 默认初始化正运动控制器（IP 取自 `MotionConfig`），`InitializeWithZMotion(ip)` 提供显式 IP 覆盖入口，连接失败不再回退到空控制器、仅记录告警。
- CAMBOX 硬件级实时跟踪（主轴 `ATYPE=25` 通讯编码器轴 AXIS8、从轴 Y 轴 AXIS0、时序插值对齐、异常保护）见 [[architecture/DeviceControlArchitecture]] 第 10 章；启停编排由 `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` 承载。
- 详见 [[decisions/ADR-012-MotionControlModule]]、[[decisions/ADR-022-ZMotionControllerIntegration]]、[[decisions/ADR-023-RSICamBoxTrackingArchitecture]]、[[api/IMotionController]]、[[api/MotionManager]]、[[api/ZMotionController]]、[[api/MoveControlData]]、[[api/CamBoxTracker]]、[[api/EncoderAxis]]、[[api/RSIPositionBuffer]]。

## 资源释放入口（2026-08-19，ADR-001 非 UI 类标准）

> 遵循 ADR-001：**非 UI 类统一实现标准 `IDisposable.Dispose()`，不使用 `DisposeComponents()`**（该命名仅限 UI 设计器类）。

| 类 | 释放入口 | 释放内容 |
|----|---------|---------|
| `ZMotionController` | `IDisposable.Dispose()` | StopHeartbeat（心跳线程 Join/Abort）→ DisableCycleReport（周期上报线程 Join/Abort）→ DisableAutoReport → 释放 GCHandle → Close()（停轴/关IO/ZAux_Close）→ 事件清空 |
| `InterpolationEngine` | `IDisposable.Dispose()` | `Stop()` 停止插补发送线程 |
| `CamBoxTracker` | `IDisposable.Dispose()` | `ZAux_Direct_CamStop` 停止 CAMBOX → 状态复位 → 句柄/配置置空 → 事件清空 |
| `EncoderAxis` | `IDisposable.Dispose()` | 状态/句柄/配置复位 → 事件清空 |
| `RSIPositionBuffer` | `IDisposable.Dispose()` | 环形缓冲数组清空 + 计数/写索引复位（托管资源） |

> **历史迁移说明（2026-08-19）**：以上类原使用 `DisposeComponents()` 命名，已统一迁移为标准 `IDisposable.Dispose()`（`DisposeComponents()` 仅保留给 UI 设计器类使用，见 [[decisions/ADR-001-DisposePattern]]）。

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| [[modules/DeviceControl]] | `MotionControlWorkflow` 承载 CAMBOX 启停编排，通过 `MotionManager.Instance.GetAxis(...)` 取轴控制；私有阶段枚举经 `MapWeldStatus` 映射为焊接过程态 `SubDeviceWeldStatus` |
| [[modules/WeldParamControl]] | `WeldProcess.ComputeAndCacheHorizontalMove` 委派至 `MoveControlData`；`WeldProcess.CurrentRobotX` 供真实机器人X读取 |
| [[modules/VirtualCam]] | `MotionControlWorkflow` 取图（`CameraSelector.Active`）+ 模拟轮廓驱动 |
| [[modules/SmartRayCam]] | 共享 `ICameraRun`（`CameraRun` 真实相机）；`Comm/SystemComm` 枚举 |
| [[modules/EmguALG]] | `PipelineManager.AlgorithmCompleted` / `SeamFeatureResult` |
| [[modules/Comm]] | `GlobalCommData` 日志 / `SimTestMode` 等枚举 |
| [[modules/UIDesign]] | `MotionControlPage`（标定/模拟/运动轴参数写入，位于 Sub2UI，接入 NavPage（参数界面）工艺配置节点） |
| [[modules/DeviceControl]] | 焊接过程态由 `MotionControlWorkflow.MapWeldStatus` 映射为 `SubDeviceWeldStatus`（七态） |

---

*来源：AdaWeldSystem/MotionControl/ 模块源码*