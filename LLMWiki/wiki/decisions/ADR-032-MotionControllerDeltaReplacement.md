---
title: ADR-036 运动控制器采用台达 EtherCAT（全新模块，结构与对外消费按原档）
date: 2026-09-06
tags: [决策, 运控, 台达, EtherCAT, 雷赛, 焊接头, 振镜, 目录结构, 对外消费]
status: accepted
---

# ADR-036 运动控制器采用台达 EtherCAT（全新模块，结构与对外消费按原档）

## 背景

本项目运动控制采用 **台达（Delta）PCI-L221 EtherCAT 主站卡**。2026-09-05/06 用户明确：

1. 运动控制器即台达，**架构与实现按全新模块设计**；
2. 参考基线是**雷赛（Leadshine）** 那套架构与调用纪律；
3. **振镜控制与自动对焦控制由焊接头连接**，不属于运动控制模块。

台达 SDK 调研已完成（`inc/C#/EtherCAT_DLL.cs` 共 832 个 API、`EtherCAT_DLL_Err.cs` 共 336 个错误码，签名逐字核验），落地规范沉淀于 [[guides/DeltaEtherCAT-DevGuide]]。

> **2026-09-06 用户补充裁定**：该模块是**全新设计**，文档不得写成与既有实现的对比/替换/迁移叙述；**目录结构与对外消费关系一律以开发指导原档为准**。

## 决议

### D1 落地主体 = 用户提供的台达开发指导原档

目录结构、文件清单、命名、对外消费关系、初始化流程，一律以 `raw/delta/运动控制模块开发文档_台达版.md`（1323 行）为准。原档 API 名有 7 处失准，以 SDK 头文件为准订正（指导页 §12.1）。

### D2 参考基线 = 雷赛 `LSnmcControler`

| 角色 | 对象 | 用法 |
|------|------|------|
| **落地主体** | `raw/delta/运动控制模块开发文档_台达版.md` | 目录 / 分层 / 命名 / 消费关系 |
| **参考基线** | `E:\SoftwareGit\HonorMachineTest\PcomDeviceInterface\MotionControl\`（`IMotion/` + `LSnmcControler/`） | 学**架构形态与调用纪律**（D3），不照抄 `smc_*` API |
| **API 权威** | 台达 SDK 头文件 | 最高，优先于原档与任何二手文档 |

### D3 从雷赛继承的六条纪律（台达实现必须遵守）

| # | 纪律 | 台达落地 |
|---|------|----------|
| ① | 三层分离 + 容器自注册（控制器持有轴/IO 列表，构造时自注册） | `DeltaMontionControl` 持 `_axes` / `_inPuts` / `_outPuts`，轴与 IO 构造时 `Container.AddAxis(this)` / `AddIO(this)` |
| ② | **参数挂在轴上**（`Equiv` / 速度 / 加减速 / S 段 / 回零），一次配置多次调用 | `MontionAxis` 提供 `MinVel`/`MaxVel`/`AccTime`/`DecTime`/`STime`/`StopVel`/`Equiv`/`HomeMode`/`HomeDir`/`HomeMaxVel` |
| ③ | **运动前三段检查**（总线 → 轴状态 → 运动中） | 封装 `PreMotionCheck()`：`Get_Connect_Status`(OpState==3 且无报警) → 急停标志；所有运动入口首行调用 |
| ④ | **阻塞 / 非阻塞成对** | `AbsMove` / `AbsMoveNoBlock`、`Home` / `HomeNoBlock` + `WaitHomeDone`；等待用 `Thread.Sleep` + 超时（**不用 `Application.DoEvents()`**） |
| ⑤ | **急停贯穿**（控制器 setter 广播到所有轴；等待循环每圈查急停） | `SetEmergencyStop(bool)` → 所有轴 `AxisStop(1)`；置位后 `PreMotionCheck` 全部短路 |
| ⑥ | **到位判定与停止原因分离** | 到位用 `Motion_Get_Mdone`；异常原因查 `StatusWord` 位与 EMCY（`Slave_Get_EMCY_Data`） |

### D4 单位换算：脉冲换算集中在 L3

- 台达**无 `SetUnits` / equiv 下写机制**，位置与速度参数**全是脉冲**，换算必须在 L3 实现层手动做。
- `Equiv` 语义 = **工程单位/脉冲**（mm/pulse），与雷赛 `smc_set_equiv` 一致。
  - 工程单位 → 脉冲：`pulse = value / Equiv`
  - 脉冲 → 工程单位：`value = pulse * Equiv`
- **L2 抽象层与业务层一律使用工程单位**，换算不外泄。
- 时间类参数有两处**毫秒**：S 曲线时间（台达 `SCurve` 参数）、回零加速度（`Home_Config` 的 `Acceleration`）；其余加减速时间为秒。

> 原档 §6.2 把 `Equiv` 注为"脉冲/工程单位"，与其 §7.3 的 `ToPulse(v)=v/Equiv` 自相矛盾。本 ADR 按**工程单位/脉冲**裁定。

### D5 振镜与自动对焦归焊接头，运控不承担

| 能力 | 归属 | 说明 |
|------|------|------|
| **自动对焦** | 焊接头 `LaserWeldHead` | 契约已存在：`ILaserWeldHeadController.SetAutoFocusPosition(double position)` / `CurrentAutoFocusPosition` / `AutoFocusPositionChanged` |
| **振镜** | 焊接头 `LaserWeldHead` | 后续依**焊接头新文档**落地接口；运动控制模块不提供振镜能力 |

因此台达实现层**不需要**振镜 / 激光打标能力；焊缝摆动类需求走焊接头控制器，不挂到运控轴。

### D6 命名沿用原档（撤销 `DeltaController` / `DeltaAxis` / `DeltaIO` 方案）

| 项 | 裁定 |
|----|------|
| 抽象层 | `MontionControl` / `MontionAxis` / `MontionIO` / `InputIO` / `OutputIO`——**保留雷赛 `Montion` 拼写**，不改为 `Motion` |
| 实现层 | `DeltaMontionControl` / `DeltaMontionAxis` / `DeltaInputIO` / `DeltaOutputIO` / `DeltaSlaveScanner` |
| Native 层 | `EtherCATMasterNative` / `EtherCATMotionNative` / `EtherCATIONative` / `EtherCATAdvancedNative` / `DeltaErrorCode`，方法名保留台达 `CS_ECAT_*` 风格 |

> 2026-09-05 曾提议与既有目录同层对称的 `DeltaController` / `DeltaAxis` / `DeltaIO`，**已撤销**——原档命名优先。

### D7 分层与依赖方向铁律

| 层 | 目录 | 依赖 |
|----|------|------|
| L1 原生封装 | `DeltaEtherCAT/Native/` | 只依赖 `EtherCAT_DLL.dll` |
| L2 抽象接口 | `IMotion/` | **零外部依赖**（不引用厂商、不引用业务层、不引用 Native） |
| L3 台达实现 | `DeltaEtherCAT/` | 继承 L2，调用 L1；反向禁止 |
| 业务层 | `MontionManager` + `AxisRegistry` / `IORegistry` / `CylinderRegistry`；`Cylinder` 实体在 L2 | 只面向 L2 抽象编程 |

1. Native 只被 L3 调用，业务层禁止直接调用 `CS_ECAT_*`（错误码查询除外）。
2. 业务层成员类型一律用抽象基类，不出现 `Delta*` 具体类型。
3. L3 具体类型只出现在两处：初始化时的 `new`、需要台达特有能力时的显式向下转型。

## 影响

| 面 | 变化 |
|----|------|
| 新增目录 | `IMotion/`（8 文件）+ `DeltaEtherCAT/`（5 文件）+ `DeltaEtherCAT/Native/`（5 文件） |
| 业务层 | `MontionManager` 初始化处 `new DeltaMontionControl(DevName)`；三张注册表把轴/IO/气缸登记进控制器；`Cylinder` 厂商无关（位于 `IMotion/`） |
| `LaserWeldHead` | 承接振镜与对焦（D5），接口依后续焊接头文档落地 |
| 平台目标 | 项目属性必须 `x86` 或 `x64`，**禁止 AnyCPU** |
| 部署 | `EtherCAT_DLL.dll` / `EtherCAT_DLL_x64.dll` 复制到输出目录 |
| 文档 | [[guides/DeltaEtherCAT-DevGuide]] 为唯一落地规范；[[api/LeadshineLSnmc-Reference]] 为参考基线；[[api/DeltaEtherCAT-Native]] 为 API 速查 |

## 未决事项

- 振镜在焊接头上的**具体接口形态**（扁平成员 vs 独立 `IGalvoScanner` 子模块）待焊接头新文档确定。
- 激光功率控制（台达 PWM 族 13 个 API）是否也归焊接头，待焊接头新文档确认。
- 轴/IO 拓扑（`nodeId` / `slotNo` / `Equiv`）由代码传入还是配置文件，待定（指导页 §15）。
- 焊缝跟踪主轴方案（虚拟轴 / 外部编码器）与 ECAM2 凸轮曲线，待工艺参数确定。
- 多卡场景的轴归属规则、AD/DA 的 OD 索引映射、高级功能（插补/龙门/PVT）一期范围，均待硬件与工艺确认。

## 相关

- [[guides/DeltaEtherCAT-DevGuide]] — 台达落地规范（目录结构、对外消费、初始化序列、单位换算、核验门禁、落地清单）
- [[api/LeadshineLSnmc-Reference]] — 雷赛参考基线（抽象契约形态与六条调用纪律）
- [[api/DeltaEtherCAT-Native]] — 台达原生 API 全量速查（832 个）
- [[modules/MotionControl]] — 运动控制模块页
- [[modules/LaserWeldHead]] — 焊接头（承接振镜与对焦）
