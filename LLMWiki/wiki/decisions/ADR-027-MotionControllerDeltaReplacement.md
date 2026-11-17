---
title: ADR-027 运动控制器台达 EtherCAT 现行决策（选型 · ZMotion 移除 · 全量对接；整合原 032/033）
date: 2026-09-06
updated: 2026-10-30
tags: [决策, 运控, 台达, EtherCAT, 正运动, 移除, 消费方对接, 寻址, merged, ADR-027]
status: accepted
merged_from: [ADR-032, ADR-033]
---

# ADR-027 运动控制器台达 EtherCAT 现行决策（选型 · ZMotion 移除 · 全量对接）

> 本页为整合页（2026-09-17），收拢原 ADR-021 / ADR-027 的全部现行裁定；历史时间线见「沿革」。落地规范以 [[guides/DeltaEtherCAT-DevGuide]] 为唯一准绳，焊接头从站与 CSP/PVT 等后续演进见 ADR-030（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]，本页不重复。

## 背景

本项目运动控制采用**台达（Delta）PCI-L221 EtherCAT 主站卡**。2026-09-05/06 用户明确：

1. 运动控制器即台达，**架构与实现按全新模块设计**——文档不得写成与既有实现的对比/替换/迁移叙述，目录结构与对外消费关系一律以开发指导原档为准；
2. 参考基线是**雷赛（Leadshine）** 那套架构与调用纪律，不照抄 `smc_*` API；
3. **振镜控制与自动对焦控制由焊接头连接**，不属于运动控制模块。

2026-09-07 用户下达四项执行需求：移除正运动（ZMotion）全套实现、全面编写台达模块、消费方全量对接、新建/修改代码精简与注释精简。台达 SDK 调研已完成（`EtherCAT_DLL.cs` 共 832 个 API、`EtherCAT_DLL_Err.cs` 共 336 个错误码，签名逐字核验）。

## 现行决策

### 一、选型与落地主体

| 角色 | 对象 | 用法 |
|------|------|------|
| **落地主体** | `raw/delta/运动控制模块开发文档_台达版.md`（1323 行） | 目录 / 分层 / 命名 / 消费关系 / 初始化流程 |
| **参考基线** | 雷赛 `IMotion/` + `LSnmcControler/` | 学**架构形态与调用纪律**（下表六条） |
| **API 权威** | 台达 SDK 头文件 | 最高，优先于原档与任何二手文档（原档 API 名已发现 8 处失准，均按 SDK 真名订正） |

### 二、从雷赛继承的六条纪律（台达实现必须遵守）

| # | 纪律 | 台达落地 |
|---|------|----------|
| ① | 三层分离 + 容器自注册 | `DeltaMontionControl` 持 `_axes` / `_inPuts` / `_outPuts`，轴与 IO 构造时 `Container.AddAxis(this)` / `AddIO(this)` |
| ② | **参数挂在轴上**（`Equiv` / 速度 / 加减速 / S 段 / 回零），一次配置多次调用 | `MontionAxis` 提供 `MinVel`/`MaxVel`/`AccTime`/`DecTime`/`STime`/`StopVel`/`Equiv`/`HomeMode`/`HomeDir`/`HomeMaxVel` |
| ③ | **运动前三段检查**（总线 → 轴状态 → 运动中） | 封装 `PreMotionCheck()`：`Get_Connect_Status`(OpState==8 且无报警) → 急停标志；所有运动入口首行调用 |
| ④ | **阻塞 / 非阻塞成对** | `AbsMove` / `AbsMoveNoBlock`、`Home` / `HomeNoBlock` + `WaitHomeDone`；等待用 `Thread.Sleep` + 超时（**禁用 `Application.DoEvents()`**） |
| ⑤ | **急停贯穿**（控制器 setter 广播到所有轴；等待循环每圈查急停） | `SetEmergencyStop(bool)` → 所有轴 `AxisStop(1)`；置位后 `PreMotionCheck` 全部短路 |
| ⑥ | ⚠️ **到位判定与停止原因分离（2026-09-24 勘误）** | ~~到位用 `Motion_Get_Mdone`~~ —— 勘误：台达 `Motion_Get_Mdone` 是**多值状态机**（手册 8.12：0=靜止/1=加速中/2=常態速度/3=減速中/5=通訊中），**「運動中」= `Mdone != 0`**（旧实现按雷赛 `0=运动中` 写入 ⇒ 判据取反，已由现场日志证伪并修正）。**CSP 族另有专用到位判定** `CSP_Set_SoftTargetReach` / `Get_SoftTargetReach_Status`（手册 9.1.12/9.1.13，位置窗口+条件次数）。异常原因仍查 `StatusWord` 位与 EMCY（`Slave_Get_EMCY_Data`） |

### 三、单位换算与寻址

1. **脉冲换算集中在 L3**：台达无 `SetUnits` 下写机制，位置与速度参数全是脉冲；`Equiv` 语义 = **工程单位/脉冲**（mm/pulse）——`ToPulse(v)=v/Equiv`、`ToUnit(p)=p*Equiv`；**L2 抽象层与业务层一律使用工程单位**，换算不外泄（原档 §6.2 注法与其 §7.3 公式自相矛盾，本 ADR 按「工程单位/脉冲」裁定）；
2. **时间类参数两处毫秒**：S 曲线时间（`SCurve`）、回零加速度（`Home_Config.Acceleration`）；其余加减速时间为秒；
3. **卡号与拓扑寻址**：卡号轴内统一取 `_deltaControl.CardNo` 属性（**不缓存** `_connectNo` 快照，避免初始化后失效）；`NodeId` / `SlotNo` / `BitNo` 拓扑寻址随 `DeltaAxisConfig` / `DeltaIOConfig` 配置实体注入（配置类为实例、非单例），来源经后续配置化演进落定（见 [[decisions/ADR-029-CylinderConfigAndCsvImport]]）；
5. **IO NPN 低电平有效**：`SetON()` 写 **0**、`SetOFF()` 写 **1**。

### 四、振镜与自动对焦归焊接头

| 能力 | 归属 | 说明 |
|------|------|------|
| **自动对焦** | 焊接头 `LaserWeldHead` | 契约：`ILaserWeldHeadController.SetAutoFocusPosition(double)` / `CurrentAutoFocusPosition` / `AutoFocusPositionChanged` |
| **振镜** | 焊接头 `LaserWeldHead` | 依焊接头文档落地；运动控制模块不提供振镜能力，焊缝摆动类需求走焊接头控制器，不挂运控轴 |

台达实现层不需要振镜 / 激光打标能力。

### 五、命名沿用原档

| 层 | 命名 |
|----|------|
| 抽象层 | `MontionControl` / `MontionAxis` / `MontionIO` / `InputIO` / `OutputIO`——**保留雷赛 `Montion` 拼写**，不改为 `Motion` |
| 实现层 | `DeltaMontionControl` / `DeltaMontionAxis` / `DeltaInputIO` / `DeltaOutputIO` / `DeltaSlaveScanner` |
| Native 层 | `EtherCATMasterNative` / `EtherCATMotionNative` / `EtherCATIONative` / `EtherCATAdvancedNative` / `DeltaErrorCode` 等，方法名保留台达 `CS_ECAT_*` 风格 |

> 2026-09-05 曾提议 `DeltaController` / `DeltaAxis` / `DeltaIO`，**已撤销**——原档命名优先。

### 六、分层与依赖方向铁律

| 层 | 目录 | 依赖 |
|----|------|------|
| L1 原生封装 | `DeltaEtherCAT/Native/` | 只依赖 `EtherCAT_DLL.dll` |
| L2 抽象接口 | `IMotion/` | **零外部依赖**（不引用厂商、不引用业务层、不引用 Native） |
| L3 台达实现 | `DeltaEtherCAT/` | 继承 L2，调用 L1；反向禁止 |
| 业务层 | `MontionManager` + `AxisRegistry` / `IORegistry` / `CylinderRegistry` | 只面向 L2 抽象编程；`Cylinder` 实体在 L2 |

1. Native 只被 L3 调用，业务层禁止直接调用 `CS_ECAT_*`（错误码查询除外）；
2. 业务层成员类型一律用抽象基类，不出现 `Delta*` 具体类型；
3. L3 具体类型只出现在两处：初始化时的 `new`（唯一装配点 `MontionManager`）、需要台达特有能力时的显式向下转型。

### 七、ZMotion 整体移除

| 删除对象 | 规模 | 说明 |
|----------|------|------|
| `MotionControl/ZMotion/`（10 文件） | 约 5100 行 | `ZMotionController` / `ZMotionAxis` / `ZMotionIO` / `ZMotionNative` / `ZMotionNativeLaser` / `ZMotionGalvo` / `InterpolationEngine` / `EncoderAxis` / `CamBoxTracker` / `RSIPositionBuffer` |
| `MotionControl/API/`（4 文件） | — | `IAxis` / `IIO` / `IMotionController` / `MotionControllerBase`（旧三层，已被 `IMotion/` 取代） |
| `MotionControl/MotionManager.cs` | — | 旧单例，被 `MontionManager` 取代 |
| `MotionControl/MotionConfig.cs` | 759 行 | 正运动专属配置（IP / 心跳 / BAS / CAMBOX / ATYPE25） |
| `3rdDepend/{zauxdll,zmotion,ZmotionScanLaser}.dll` | — | 正运动原生依赖（用户裁定：删除，暂不建新配置） |

**四项冲突裁定**：L2 命名基准以原档与规范页为准；正运动遗留高级组件（CamBoxTracker / EncoderAxis / InterpolationEngine / RSIPositionBuffer）**全部删除**；`MotionConfig.cs` 删除暂不建新配置；L2 中 6 个 Modbus 抽象方法**移除**（台达无 Modbus，走 PDO/SDO）。

### 八、台达模块全量落地与消费方对接

1. **21 文件落地**：L2 抽象 `IMotion/`（含 `IPVTMotion.cs`，2026-09-07 删 `IOParam.cs`、移入 `Cylinder.cs`）；L1 原生 `DeltaEtherCAT/Native/`（含 `EtherCATPVTNative` / `EtherCATEcam2Native`）；L3 实现 `DeltaEtherCAT/`（含 `DeltaMotionConfig` / `DeltaAxisConfig` / `DeltaIOConfig`）；业务层 `MontionManager`（单例聚合，持有 `MoveData`）+ 三注册表 + `MoveControlData`；
2. **初始化序列**：`Master_Open` → `Master_Initial` → 轮询 `Check_Initial_Done`（0/1/99，超时 30s）→ 扫从站；使能：先 `Set_Move_Mode(8=CSP)`，再 `Set_Svon(1)`，轮询状态字 bit2，超时 3s；
3. **消费方全量对接与精简纪律**：`MotionControlWorkflow` 全量重写（删 ZMotion 依赖，阶段枚举 `MotionControlPhase`，对外契约 `Instance`/`Start()`/`Stop(bool)`/`IsRunning`/`WeldStatus`/`StateName` **保持不变**）；`DeviceControlWork` 改持 `MontionManager`；`WeldProcess` 注释同步；`.csproj` 17 条旧编译项 → 21 条新条目，原生依赖 `zauxdll.dll` + `ZmotionScanLaser.dll` → `EtherCAT_DLL_x64.dll`；删除过程性注释，`//` 仅用于复杂逻辑；公开接口统一 `///` + `<param>`（P/Invoke `extern` 声明豁免）；日志直连 `GlobalCommData.ShowLog` 纯文本无符号；无用 using 清零。

## 约束（后续必须遵守）

- ⛔ 平台目标**禁止 AnyCPU**（必须 `x86` 或 `x64`）；`EtherCAT_DLL.dll` / `EtherCAT_DLL_x64.dll` 需复制到输出目录；
- ⛔ 业务层 / UI 禁止回流 L1/L2、禁止直呼 `CS_ECAT_*`（错误码查询除外）；
- ⛔ 新代码不引用 `ZMotion*` / `zaux*` / 正运动遗留组件（静态校验 0 残留为门禁）；
- 装配点唯一：`MontionManager` 初始化处 `new DeltaMontionControl(DevName)`。

## 沿革

- **2026-09-05/06**：裁定台达 PCI-L221 选型 + 全新模块设计（原 ADR-021 主体）；**2026-09-07**：ZMotion 整体移除 + 台达 21 文件全量落地 + 消费方全量对接（原 ADR-027），Python 静态校验 10 项全过（真编译待 Visual Studio）；
- **2026-09-07 · 同日整页删除三个旧 ADR**：正运动控制器接入架构、RSI-CAMBOX 硬件实时跟踪架构、默认初始化切正运动——三者页面已从 `decisions/` 移除，编号经全库重排后不再保留空号，映射见 [[decisions/ADR-Index]]；
- **2026-09-14/16/17 演进**：焊接头从站接入（ADR-030/051）、焊缝跟踪 PVT→CSP 换轨（ADR-027/058）、气缸配置化 CSV 导入（ADR-022）；
- **2026-09-17 · 本页整合**：ADR-027 并入本页，收拢全部现行裁定；整合后 tags 含 merged、`merged_from` 指向被并页。

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 后果

### 正面
- （待补）

### 负面
- （待补）

## 相关页面

- 落地规范：[[guides/DeltaEtherCAT-DevGuide]] · [[api/DeltaEtherCAT-Native]] · [[api/LeadshineLSnmc-Reference]]（参考基线）
- 模块：[[modules/MotionControl]]
- 后续演进：ADR-030（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） · [[decisions/ADR-030-WeldHeadSlaveDeviceUnderMotionControl]] · [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] · [[decisions/ADR-029-CylinderConfigAndCsvImport]]
- 已并入本页（纯文本存档）：ADR-027-ZMotionRemovalAndDeltaLanding
