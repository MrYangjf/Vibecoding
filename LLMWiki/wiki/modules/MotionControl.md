---
title: MotionControl 模块 — 运控调整
date: 2026-07-31
tags: [模块, 运控, 水平移动, 模拟测试, 运动轴, 状态机, 台达, EtherCAT]
source: AdaWeldSystem/MotionControl/ 模块源码
---

# MotionControl 模块 — 运控调整

> **2026-09-07 控制器整体换轨**：正运动（ZMotion）全套实现**已从代码库删除**，运动控制改由**台达 PCI-L221 EtherCAT 主站卡**承接（程序不再使用任何正运动设置）。差异对照见 §控制器换轨沿革。决策记录：[[decisions/ADR-033-ZMotionRemovalAndDeltaLanding]]。

独立运控模块（不再挂载于 InteliWeld），负责：

1. 线激光前装标定的水平移动距离计算与缓存（`MoveControlData`）；
2. **运动控制三层架构**（`IMotion/` 抽象 + `DeltaEtherCAT/` 台达实现 + `DeltaEtherCAT/Native/` 原生封装）；
3. 业务聚合（`MontionManager` 单例 + `Cylinder` 气缸）；
4. 运控工作流（`MotionControlWorkflow`，位于 `MainDeviceControl/DeviceWorkflow/`）。

设计遵循 ADR-009 的「独立模块 + Run/Workflow 分离」范式与 [[decisions/ADR-010-MotionControlModule]]、[[decisions/ADR-032-MotionControllerDeltaReplacement]]。

## 目录结构（2026-09-07 现行）

```
MotionControl/
├── IMotion/                           ← L2 抽象层（零外部依赖）
│   ├── Type.cs                        ← ControlType/ManufacturerType/IOType/MoveMode/HomingMode/StopMode/AxisState/InterpolationType/PVTTimeMode/Ecam*
│   ├── MontionControl.cs              ← 控制器抽象基类（管理轴/IO 列表）
│   ├── MontionAxis.cs                 ← 轴抽象基类（默认实现 IPVTMotion）
│   ├── MontionIO.cs                   ← IO 抽象基类
│   ├── InputIO.cs / OutputIO.cs       ← 输入/输出特化
│   ├── Cylinder.cs                    ← 气缸实体（多 IO 复合，Builder 链式装配）
│   ├── IPVTMotion.cs                  ← PVT 能力契约 + PVTPoint + PVTInformation + PVTResult
│   └── InterpolationMontionParam.cs   ← 插补参数（多轴直线/圆弧/螺旋）
├── DeltaEtherCAT/                     ← L3 台达实现
│   ├── DeltaMontionControl.cs         ← 台达控制器（开卡→初始化→轮询→扫从站）
│   ├── DeltaMontionAxis.cs            ← 台达轴（CSP/CSV/CST/回零/软限位）
│   ├── DeltaInputIO.cs / DeltaOutputIO.cs
│   ├── DeltaSlaveScanner.cs           ← 从站扫描与识别（VendorID 匹配）
│   ├── DeltaMotionConfig.cs           ← 配置实例类（主站/轴/输入/输出/PVT/跟踪/标定，XMLfile 读写）
│   ├── DeltaAxisConfig.cs             ← 单轴配置实体（NodeId+SlotNo 寻址，无 AxisNo）
│   └── DeltaIOConfig.cs               ← 单路 IO 配置实体（NodeId+SlotNo+BitNo）
│   └── Native/                        ← L1 原生 P/Invoke
│       ├── EtherCATMasterNative.cs    ← 主站管理（Open/Initial/Reset/Close/链路健康）
│       ├── EtherCATMotionNative.cs    ← 运动（模式/使能/停止/位置速度/回零）
│       ├── EtherCATIONative.cs        ← DIO 读写（全量 + 单路）
│       ├── EtherCATAdvancedNative.cs  ← 插补/同步/龙门/TouchProbe/虚拟坐标偏移
│       ├── EtherCATPVTNative.cs       ← PVT A 套（int 脉冲）+ B 套（double 流式）
│       ├── EtherCATEcam2Native.cs     ← ECAM2 建表/啮合/调整/飞剪/状态
│       └── DeltaErrorCode.cs          ← 错误码常量 + GetMessage
├── AxisRegistry.cs                    ← 轴注册表（按名登记 + 回灌进控制器）
├── IORegistry.cs                      ← IO 注册表（输入/输出分表）
├── CylinderRegistry.cs                ← 气缸注册表（把气缸占用 IO 注册进控制器）
├── MontionManager.cs                  ← 业务层单例（唯一装配点，持有三张注册表 + MoveData）
└── MoveControlData.cs                 ← 标定转发 + 计算 + 缓存（持有 DeltaMotionConfig 实例）
```

> **实例化链（2026-09-07）**：`MontionManager`（单例）→ `new MoveControlData()` → `new DeltaMotionConfig()`。
> 三者均为「上层持有下层实例」，`DeltaMotionConfig` 与 `MoveControlData` **不再是单例**，全系统入口只有 `MontionManager.Instance.MoveData`。

> **命名空间**：`IMotion/` → `AdaWeldSystem.MotionControl.IMotion`；`DeltaEtherCAT/` → `AdaWeldSystem.MotionControl.DeltaEtherCAT`；`Native/` → `...DeltaEtherCAT.Native`；根目录 → `AdaWeldSystem.MotionControl`。
>
> **已删除目录**：`API/`（IAxis/IIO/IMotionController/MotionControllerBase）、`ZMotion/`（10 文件）。已删除文件：`MotionManager.cs`、`MotionConfig.cs`、`IMotion/IOParam.cs`（无引用空壳）。
>
> **2026-09-07 结构调整**：`Cylinder` 实体由模块根移入 `IMotion/`（与 `MontionAxis` / `MontionIO` 同为抽象层实体），模块根新增 `AxisRegistry` / `IORegistry` / `CylinderRegistry` 三张注册表；`IPvtMotion.cs` / `PvtPoint.cs` / `PvtInformation.cs` 三文件合并为 `IPVTMotion.cs`，命名统一全大写 PVT。

## 台达 EtherCAT 运动控制（现行）

> 本模块为**全新设计**：目录结构与对外消费关系以用户提供的开发指导原档为准，决策见 [[decisions/ADR-032-MotionControllerDeltaReplacement]]。

### 三层 + 业务层依赖铁律

```
        业务层  MontionManager + AxisRegistry·IORegistry·CylinderRegistry  ← 只面向 L2 抽象
                        ↓
        L2      IMotion/  MontionControl·MontionAxis·MontionIO·InputIO·OutputIO·Cylinder
                        ↑ 零依赖（不得出现 Delta/CS_ECAT/DllImport）
        L3      DeltaEtherCAT/  DeltaMontionControl·DeltaMontionAxis·Delta*IO
                        ↓
        L1      Native/  CS_ECAT_* P/Invoke（只被 L3 调用）
```

| 铁律 | 内容 |
|------|------|
| L2 零依赖 | `IMotion/` 内不得出现厂商名、`CS_ECAT_*`、`DllImport` |
| L3 调 L1 | 原生 API 只允许在 `DeltaEtherCAT/` 内调用 |
| 业务层只认抽象 | `Delta*` 具体类型**仅**在 `MontionManager.Initialization()` 中 `new` 一次 |
| Native 不外泄 | L1 不得被业务层或 UI 直接引用 |

> 校验结果（2026-09-07 静态扫描）：L2 回流 0 处、业务层/UI 回流 0 处、厂商类型越界 0 处（仅 `MontionManager.cs:96` 一处 `new DeltaMontionControl`，属合规装配点）。

### 关键机制（易错点）

| 机制 | 说明 |
|------|------|
| **单位换算** | 台达 API 全脉冲。`Equiv` = **工程单位/脉冲**（mm/pulse）；`ToPulse(v)=v/Equiv`、`ToUnit(p)=p*Equiv`。换算**只在 L3** |
| **初始化异步** | `Master_Open` → `Master_Initial` → 轮询 `Check_Initial_Done`（0 完成 / 1 进行中 / 99 失败），超时 30s → 再扫从站 |
| **伺服使能** | 必须先 `Set_Move_Mode(8=CSP)`，再 `Set_Svon(1)`，然后轮询状态字 bit2（Operation Enabled），超时 3s；使能前查 bit3 报警 |
| **IO 极性** | 台达为 **NPN 低电平有效**：`SetON()` 写 **0**、`SetOFF()` 写 **1** |
| **寻址** | 四元组 `CardNo + NodeId + SlotNo + BitNo`（非正运动的手柄 + 轴号） |
| **无 Modbus** | 台达无 Modbus 通道，寄存器访问走 **PDO/SDO**（`Slave_SDO_*` / `Slave_PDO_*`） |
| **时间单位** | S 曲线时间与回零加速度为 **ms**，其余速度/加减速时间为 **s** |
| **运动前置检查** | 所有运动入口统一 `PreMotionCheck`（急停 → 总线就绪 → 报警） |

### 注册表机制（2026-09-07 新增）

模块根的三张注册表取代原先 `MontionManager` 内部四个裸字典，职责是「按名登记 + 保证已注册进控制器」。

```
业务代码 ──AddAxis(name,axis)──→ MontionManager ──→ AxisRegistry.Register()
                                                 └→ MontionControl.AddAxis(axis)   ← 真正进控制器
                                                        （Initialization 后再 AttachAll 幂等回灌）

                                AddCylinder ──→ CylinderRegistry.Register()
                                              └→ 逐个 cylinder.GetAllIO() → MontionControl.AddIO()
```

| 注册表 | 承载 | 关键成员 |
|--------|------|----------|
| `AxisRegistry` | `Dictionary<string, MontionAxis>` | `Register` / `Get` / `GetAll` / `GetNames` / `Count` / `AttachAll(control)` |
| `IORegistry` | 输入、输出**分表**存放（键名空间独立，允许同名） | `RegisterInput` / `GetInput` / `RegisterOutput` / `GetOutput` / `InputCount` / `OutputCount` / `AttachAll` |
| `CylinderRegistry` | `Dictionary<string, Cylinder>` | `Register` / `Get` / `GetAll` / `Count` / `AttachAll`（把气缸占用的全部 IO 注册进控制器） |

要点：

- `MontionAxis` / `MontionIO` 构造时已向所属控制器**自注册**（`container.AddAxis(this)` / `AddIO(this)`），`AttachAll` 是幂等回灌，用于校验注册表与控制器集合一致。
- 气缸是**多 IO 复合体**（2 输入 + 2 输出 + 可选中间位），`Cylinder.GetAllIO()` 是新增的枚举入口，`CylinderRegistry.AttachAll` 靠它一次性登记，避免逐个手工 `AddIO`。
- `MontionManager` 对外 API（`AddAxis` / `GetAxis` / `AddInputIO` / `GetInputIO` / `AddOutputIO` / `GetOutputIO` / `AddCylinder` / `GetCylinder`）**名字与签名不变**，消费方零改动。
- 三张注册表以属性暴露：`MontionManager.Instance.{Axes / IOs / Cylinders}`。

### PVT 能力契约（2026-09-07）

`IMotion/IPVTMotion.cs` 一个文件承载四件事，命名统一全大写 PVT（与台达 SDK 一致）：

| 成员 | 说明 |
|------|------|
| `interface IPVTMotion` | `BeginMove` / `ContinueMove` / `GetInformation` / `CycleStart` |
| `struct PVTPoint` | `Pos` / `Time` / `Vel`，工程单位 + 秒 |
| `struct PVTInformation` | `TotalCount` / `DoneCount` / `RemainBufferSize` / `Status` / `RemainCount` |
| `static class PVTResult` | `OK = 0` / `NotSupported = 0xFFFF` |

`MontionAxis` 默认实现 `IPVTMotion`，四个入口均为 `virtual` 且返回 `PVTResult.NotSupported` + 一条告警日志；具备该能力的厂商轴（台达）重写即可，**未重写不影响编译**。
调用前置条件：轴已切 **CSP 模式**且伺服使能，接口本身不负责模式切换。

### 消费方（模块外引用点）

| 消费方 | 引用形式 |
|--------|----------|
| `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` | `MontionManager.Instance.{Initialization/Close/ServoOnAll/ServoOffAll/SetEmergencyStop}` + `MontionControl.GetAxes()` |
| `MainDeviceControl/DeviceControlWork.cs` | `private MontionManager Motion`（L193）+ `Motion = MontionManager.Instance`（L367） |
| `WeldParamControl/WeldProcess.cs` | 仅注释说明（L785），实际计算委派 `MoveControlData` |
| `UIDesign/TabPage/MotionControlPage.cs` | 只用 `MotionControlWorkflow.Instance.{Start/Stop/WeldStatus}`，**不接触运控类型** |

### 部署依赖

- **原生 DLL**：`3rdDepend\EtherCAT_DLL_x64.dll`（161 MB，来自台达 SDK `dll/` 目录）
- **平台目标**：`PlatformTarget=x64`（**禁 AnyCPU**——x86 版库名为 `EtherCAT_DLL.dll`，本项目按 x64 构建）
- **构建拷贝**：`CopyNative3rdDependToOutput` 目标在构建后拷至输出目录
- **已移除**：`zauxdll.dll` / `zmotion.dll` / `ZmotionScanLaser.dll`

### 相关页面

- **完整规范**：[[guides/DeltaEtherCAT-DevGuide]]（目录结构、对外消费契约、初始化序列、单位换算、示例、API 核验门禁、落地清单）
- **原生 API 速查**：[[api/DeltaEtherCAT-Native]]（832 个 API，签名由 SDK 头文件 `inc/C#/EtherCAT_DLL.cs` 逐字抽取核验）
- **业务层入口**：[[api/MontionManager]]
- **雷赛参考基线**：[[api/LeadshineLSnmc-Reference]]
- **原档归档**：`raw/delta/运动控制模块开发文档_台达版.md`

> **边界**：振镜与自动对焦**不在本模块**，由焊接头承接——对焦已在 `ILaserWeldHeadController.SetAutoFocusPosition`，振镜接口待焊接头文档定义。

## MoveControlData（标定 + 计算 + 缓存）

- 标定参数（**转发属性**，无本地副本）：`LaserFrontOffset` / `LaserToHorizontalAngleRad`(弧度) + `LaserToHorizontalAngleDeg`(度，写时换算) / `LaserToHorizontalScaleX` / `CalibratedCenterX,Y` / `ApproachThreshold`；全部读写落到 `MotionConfig` 的 `CALIBRATION` 节。
- 持有 `DeltaMotionConfig MotionConfig`（`Axes` 轴表 / `Inputs` 输入表 / `Outputs` 输出表 / PVT 段 / 跟踪段），**注册的轴与 IO 的配置均从此对象读取**。
- **本地持久化**：`Load()`/`Save()` 委托 `MotionConfig.LoadConfig()`/`SaveConfig()`，读写 `Config/XML/DeltaMotionConfig.xml`；`Save` 由 `MotionControlPage`「保存标定参数」触发，`Load` 在 `MontionManager` 构造时自动执行（原 `Config/INI/MoveControlData.ini` 已弃用）。
- 访问路径：`MontionManager.Instance.MoveData`（`MoveControlData.Instance` 已移除）。
- 计算：`ComputeHorizontalMove(seamX, seamY) = (seamX − CalibratedCenterX) × cos(LaserToHorizontalAngleRad) × LaserToHorizontalScaleX`。
- 缓存：以 `robotX + LaserFrontOffset` 为键写入；`CacheHorizontalMove` / `TryGetNearestHorizontalMove`（阈值匹配，解决 cache X ≠ 实际 X）/ `RemoveHorizontalMove` / `ClearHorizontalMoveCache`。
- 组合：`ComputeAndCacheHorizontalMove(SeamFeatureResult, robotX)`（计算+缓存+日志），供 `WeldProcess` 真实流程与 `MotionControlWorkflow` 模拟流程统一调用，**单一算法真源**（避免逻辑分散）。

> 易误判点：`MoveControlData` 是**标定与缓存**，与硬件跟踪链路是并存关系而非替代关系，换轨台达后保持不变。

## MotionControlWorkflow（位于 `MainDeviceControl/DeviceWorkflow/`）

> ⚠️ **2026-07-20 架构纠正**：`MotionControlWorkflow` **不再持有独立模拟线程**。模拟模式（共享 robotX / A·B·C 模式 / 参数）统一由 [[api/DeviceControlWork]] 提供；本工作流仅：① 水平移动后台线程消费 `MoveControlData` 缓存；② 订阅 `PipelineManager.AlgorithmCompleted` 将线激光每帧焊缝特征缓存为水平移动距离。

- **状态模型（ADR-028 三态）**：连接态 `SubDeviceState` 与焊接过程态 `SubDeviceWeldStatus` 由基类 `DeviceStateBase` 承载，状态写入唯一入口为 `SetState`/`SetWeldStatus`，禁手工赋值。
- **2026-09-07 换轨改造**：删除全部 `ZMotion` 依赖（`CamBoxTracker` / `EncoderAxis` / `RSIPositionBuffer` / `InterpolationEngine`），私有阶段枚举改名 **`MotionControlPhase`**（`Idle` / `Initializing` / `Ready` / `Stopping` / `Error`），执行步位 `StepServoOn=10` / `StepReady=20` / `StepStopping=700`；初始化入口改为 `MontionManager.Instance.Initialization("台达运控", ref msg)`。
- **对外契约不变**：`Instance` / `Start()` / `Stop(bool)` / `IsRunning` / `WeldStatus` / `StateName`。
- 资源释放：非 UI 类统一标准 `IDisposable.Dispose()`（[[decisions/ADR-001-DisposePattern]]），**禁 `DisposeComponents()`**（仅限 UI 设计器类）。

## A / B / C 模拟测试模式

| 模式 | 相机 | 计算 | 记录 | 运动执行 |
|------|------|------|------|----------|
| A | 虚拟调试相机（`VirtualCameraRun`） | ✅ | ✅ | ❌ |
| B | 虚拟调试相机 | ✅ | ✅ | ✅（`MontionManager.GetAxis("水平轴").AbsMove`） |
| C | 真实相机（`CameraRun`） | ✅ | ✅ | ❌ |

> 水平移动后台线程由「开启模拟」按钮统一启动（见 [[api/DeviceControlWork]]）；模拟模式与参数统一归 [[api/DeviceControlWork]]，不再内嵌于本工作流。

## 控制器换轨沿革（2026-09-07）

> 2026-09-07 起运动控制**仅使用台达 PCI-L221 EtherCAT 主站**；此前基于正运动（ZMotion）的实现及其知识页已全部删除，详见 [[decisions/ADR-033-ZMotionRemovalAndDeltaLanding]]。

| 维度 | 正运动（已移除） | 台达（现行） |
|---|---|---|
| 连接 | 以太网 + 句柄 | PCI 主站卡（`CardNo` + `NodeId` + `SlotNo` + `BitNo`） |
| 初始化 | 同步 | **异步**：`Master_Initial` 后轮询 `Check_Initial_Done`(0/1/99) |
| 使能 | 直接使能 | 先 `Set_Move_Mode(8=CSP)`，再 `Set_Svon(1)`，轮询状态字 bit2 |
| IO 电平 | — | **NPN 低电平有效**（`SetON` 写 0） |
| 配置 | `MotionConfig`（IP/心跳/BAS/CAMBOX/ATYPE25） | 无独立配置文件（OPEN） |
| 振镜 / 对焦 | 占用 2 个轴 | 归焊接头（ADR-036 D5） |
| 心跳 / BAS 保护 | 应用层心跳 + BAS | **无**（WKC 看门狗由主站卡硬件维护，见 [[guides/DeltaEtherCAT-UIDesign]] §2） |
| 焊缝跟踪 | CAMBOX（ATYPE=25 通讯编码器主轴 AXIS8 + 从轴 AXIS0） | **方案未定（OPEN）**，见下节 |

## 高级运动能力（PVT / 电子凸轮）

> 完整规范见 [[guides/DeltaEtherCAT-AdvancedMotion]]；UI 见 [[guides/DeltaEtherCAT-UIDesign]]。

**PVT 多段插值**：A 套（`PVT_Move` / `PVTComplete_*` / `PVT_Config` / `PVT_Sync_Move` / `PVT_Get_NowMotCount`，int 脉冲，上限 **8000** 点）+ B 套（`PVT_Begin_Move` / `PVT_Continue_Move` / `PVT_CycleStart` / `PVT_Get_Information`，double 工程单位、**可流式续喂**、带 `RemainBufSize` 水位）。

**电子凸轮**：ECAM2 为首选（`Profile_Data` 建表 / `Profile_CamIn` 啮合 / `Profile_Modify` 改点 / `Phasing` 相位 / `Get_PreviewTable` 试算）；ECAM 一代仅兼容保留。
⚠️ **主轴来源 `SourceType` 只有 0（真实从站）与 1（轴卡板载脉冲输入）两个值——不存在「虚拟轴」**，台达的 `Virtual_Set_Enable/Command` 是坐标平移功能而非虚拟主轴。

**焊缝跟踪（机器人 X → Y 轴纠偏）方案裁决**：

| 方案 | 可行性 |
|---|---|
| ECAM2 + 虚拟轴主轴（二手文档推荐 ⭐⭐⭐⭐⭐） | ⛔ **不成立**：无虚拟轴 API、`SourceType=2` 不存在 |
| ECAM2 + 板载脉冲输入（`SourceType=1`） | ⚠️ 取决于现场是否有脉冲/编码器硬件信号 |
| **PVT 实时点序列（B 套流式）** | ✅ **推荐**：`Begin_Move` + `Continue_Move` + `Get_Information.RemainBufSize` 闭环 |
| CSP 周期同步位置 | ✅ 备选（平滑度依赖上位机节拍） |

X 坐标来源**已具备**：`Comm/Robot/KUKARobot/RSICommunication.cs`（RSI UDP 1~12ms）+ `EKICommunication.cs`，`WeldProcess.CurrentRobotX` 提供真实机器人 X。正运动删除后遗留的 **RSI 位置时序缓冲（`RSIPositionBuffer`）尚无继任者**，需随跟踪方案一同重建。

**能力现状**：`Native/EtherCATAdvancedNative.cs` 现仅 16 个 extern（ECAM2 覆盖 4、PVT 覆盖 2），落地前需补约 32 个声明（清单见规范页 §6）。

## 设计决策

- 运控数据/工作流**从 InteliWeld / Workflow 迁出**，归独立 `MotionControl` 模块。
- 运动控制采用**三层架构**（L1 Native / L2 `IMotion/` / L3 `DeltaEtherCAT/`）+ 业务层 `MontionManager`；业务层只面向 L2 抽象编程。
- **2026-09-07 控制器换轨**：移除正运动全套，全面落台达 EtherCAT；消费方全量对接 `MontionManager`。
- **2026-09-07 高级运动能力入档**：PVT 与 ECAM/ECAM2 的使用方式、API 真值核验、焊缝跟踪方案裁决，见 [[guides/DeltaEtherCAT-AdvancedMotion]]；配套 UI 设计见 [[guides/DeltaEtherCAT-UIDesign]]。
- 详阅 [[decisions/ADR-032-MotionControllerDeltaReplacement]]、[[decisions/ADR-033-ZMotionRemovalAndDeltaLanding]]、[[guides/DeltaEtherCAT-DevGuide]]、[[guides/DeltaEtherCAT-Deployment]]。

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| [[modules/DeviceControl]] | `MotionControlWorkflow` 承载运控启停编排；私有阶段枚举经 `MapWeldStatus` 映射为焊接过程态 `SubDeviceWeldStatus` |
| [[modules/WeldParamControl]] | `WeldProcess.ComputeAndCacheHorizontalMove` 委派至 `MoveControlData`；`WeldProcess.CurrentRobotX` 供真实机器人X读取 |
| [[modules/LineLaserCam]] | 共享 `ICameraRun`（`CameraRun` 真实相机）；`Comm/SystemComm` 枚举 |
| [[modules/EmguALG]] | `PipelineManager.AlgorithmCompleted` / `SeamFeatureResult` |
| [[modules/Comm]] | `GlobalCommData.ShowLog` 日志（L2 不使用，仅 L3/业务层） |
| [[modules/UIDesign]] | `MotionControlPage`（标定/模拟/参数写入，位于 Sub2UI） |

---

*来源：AdaWeldSystem/MotionControl/ 模块源码*
