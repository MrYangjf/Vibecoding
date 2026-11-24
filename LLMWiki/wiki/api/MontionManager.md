---
title: API — MontionManager 运动管理器（业务层单例，取代已废弃的 MotionManager）
date: 2026-09-07
updated: 2026-11-05
tags: [API, 运控, 台达, EtherCAT, 管理器, 单例, 业务层, CSP, ADR-027, ADR-042]
source: AdaWeldSystem/MotionControl/MontionManager.cs
---

# API — MontionManager 运动管理器

> 🔄 **2026-11-20 回零完成判据变更**：`WaitAxisHomed` 改为以 `HomeVerified && Home_Status==0 && 速度稳定` 为达成权威；位置与 `HomeOffset` 不符时只记 Warning 不阻断（扭矩回零 -3 下驱动器把 offset 反向应用，填 +1.0mm 终位 -1.0mm，旧位置硬门误判 NOT_REACHED）。见 [[decisions/ADR-080-DeltaTorqueHomingSignedModeAndDetectParams]] 演进记录。
>
> **位置**：`MotionControl/MontionManager.cs`（命名空间 `AdaWeldSystem.MotionControl`）
> **2026-09-07 新增**：取代已删除的 `MotionManager`（见 ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]））。
> **定位**：业务层唯一装配点。面向 [[modules/MotionControl]] 的 L2 抽象（`IMotion/`）编程；厂商具体类型 `Delta*` **仅在本文件 `Initialization()` 中出现一次**。
> **2026-09-07 重构**：内部四个裸字典已由三张注册表（`AxisRegistry` / `IORegistry` / `CylinderRegistry`）取代，对外 API 名字与签名**保持不变**。
> **同日追加**：持有 `MoveControlData MoveData`（构造时 `new` 并 `Load`），成为**唯一对接台达控制器的对象**；轴与 IO 在 `Initialization` 中按 `MoveData.MotionConfig` 的配置表创建。

## 职责

1. 单例持有当前控制器（`MontionControl`）；
2. 持有并暴露 `MoveData`（`MoveControlData`），标定与轴/IO 配置的唯一对外入口；
3. 持有三张注册表，按名注册与查询轴 / 输入 / 输出 / 气缸，并在注册与初始化时把对象登记进控制器；
4. `Initialization` 按配置表建轴与 IO：`MotionConfig.Axes` → `DeltaMontionAxis`、`Inputs` → `DeltaInputIO`、`Outputs` → `DeltaOutputIO`，并套用 `Equiv`/速度/回零参数；随后按 `Cylinders` 表**按名装配气缸**（2026-09-16 ADR-022 `CreateCylindersFromConfig`，引用的 IO 名未注册则告警跳过该气缸）；
5. 批量操作（全轴使能 / 下电 / 回零、全局急停）与关闭清理。

## 公共 API

| 成员 | 签名 | 说明 |
|------|------|------|
| `Instance` | `static MontionManager` | 单例（`Lazy<T>` 实现） |
| `MontionControl` | `MontionControl { get; private set; }` | 当前控制器，未初始化时为 `null` |
| `IsInitialized` | `bool { get; private set; }` | 是否已初始化；**仅在 `Initialization` 完成「控制器初始化 → 建轴/IO/气缸/焊接头」后置 `true`**（`Close` 置 `false`）。⚠️ 初始化进行中恒为 `false`，UI 不得据此判定「未连接」（见 [[api/SystemControlPage]] 2026-11-03 节、[[lessons/StartupInitializationOrderGates]] 坑 1） |
| `MoveData` | `MoveControlData { get; private set; }` | 运控数据（标定转发 + 持有 `DeltaMotionConfig`），构造时创建并加载 |
| `Axes` | `AxisRegistry { get; private set; }` | 轴注册表 |
| `IOs` | `IORegistry { get; private set; }` | IO 注册表（输入 / 输出分表） |
| `Cylinders` | `CylinderRegistry { get; private set; }` | 气缸注册表 |
| `Initialization` | `bool (string devName, ref string msg)` | 固定顺序：`MoveData.Load()` → 装配 `DeltaMontionControl` 并 `Initialization`（开卡→主站初始化→扫从站）→ `CreateAxesFromConfig` → `CreateIOsFromConfig` → `CreateCylindersFromConfig` → `CreateWeldHeadFromConfig` → `IsInitialized = true` → `AttachAll()`；失败回写 `msg` |
| `AttachAll` | `void ()` | 把三张注册表的全部对象回灌注册进当前控制器（幂等） |
| `Close` | `void ()` | 急停 → 关控制器 → 清空三张注册表 → 释放焊接头从站 → `IsInitialized=false` |
| `WeldHead` / `WeldHeadConfig` | `WeldHeadSlaveDevice` / `WeldHeadConfig` | 焊接头从站设备（随 `Initialization` 按 `MotionConfig.WeldHeadSlave` 装载，未启用为 null）与其配置（实例归 Manager 独占，`Config\MotionControl\WeldHead_XML\WeldHeadSlave.xml`，2026-09-20 按 ADR-033 迁移） |
| `LoadWeldHeadConfig` / `SaveWeldHeadConfig` | `void ()` | 焊接头配置读写（阈值 + 振镜默认参数 + **电机量纲 `MOTOR/PULSE_PER_MM`**），Save 末尾落盘（2026-09-15 ADR-012；2026-10-08 增量纲键） |
| ⭐ `WeldHeadConfig.DefaultMotorPulsePerMm` | `const double = 10.0` | **2026-10-08 新增**：电机脉冲当量默认值（10 计数 = 1mm，业主确认）。**声明在 `WeldHeadConfig` 而非设备类** —— 该类已集中持有全部配置默认值，默认值知识单一来源；`WeldHeadSlaveDevice` 构造经 `WeldHeadConfig.DefaultMotorPulsePerMm` 限定引用（⛔ 不可把常量放回设备类：`WeldHeadConfig` 是**同级类**，引不到设备类的 private 成员 ⇒ CS0103） |
| ⭐ 装载时下发 | — | **2026-10-08 变更**：`CreateWeldHeadFromConfig` 初始化序列由「下发振镜默认参数 `DefaultGalvo`」改为「① 赋电机量纲 `WeldHead.MotorPulsePerMm = WeldHeadConfig.MotorPulsePerMm` ② 下发**振镜逻辑零位** `GalvoParams.CreateLogicalHome()`（直线+最小摆幅+不使能）」，日志追加量纲值（便于判定配置是否生效） |
| ⭐ LA 走从站 | — | **2026-10-08 结构性变更**（ADR-030 就地补正）：对焦轴 LA **不再走运控轴**，改用 WSX 从站电机对象 `0x7000`（RxPDO，写 Sub1 目标位置/Sub2 使能）+ `0x6020`（TxPDO，读 Sub2 状态/Sub3 当前位置/Sub4 就绪）。API = `SetMotorPosEnable(mm, enable)` / `ReadMotorStatus()` / `StopMotor()` + `MotorRunState` 枚举 / `MotorState` **struct**（C# 7.3 无可空引用类型，故用 struct + `Nullable<T>`）。⚠️ 量纲换算**单一入口** `MmToMotorCount` / `MotorCountToMm`，改量纲只改这两行。轴表行 `Z向对焦电机` / `振镜控制` 已删除，`AxisRegistry` 由 4 条降为 2 条 |
| `AddAxis` / `GetAxis` | `void (string, DeltaMontionAxis)` / `MontionAxis (string)` | 轴注册与查询，注册时同步进控制器；**2026-11-10 起注册侧收紧为台达具体轴**（ADR-027 后仅台达一家实现） |
| `GetDeltaAxis` | `DeltaMontionAxis (string)` | 取台达具体轴。CSP 等台达专属能力由本方法下发；**2026-11-10 起 `AxisRegistry` 元素类型已收紧为 `DeltaMontionAxis`，本方法直接返回注册表结果，全库不再有 `as` 下转型**；未注册返回 `null` |
| `DeltaMotionConfig CreatePreviewMotionConfig()` | 创建与运行期隔离的运控配置预览副本（内部封装 `new` + `LoadConfig(false)`）。UI 预览/导出不再自行 `new DeltaMotionConfig` |
| `AddInputIO` / `GetInputIO` | `void (string, InputIO)` / `InputIO (string)` | 输入注册与查询 |
| `AddOutputIO` / `GetOutputIO` | `void (string, OutputIO)` / `OutputIO (string)` | 输出注册与查询 |
| `AddCylinder` / `GetCylinder` | `void (string, Cylinder)` / `Cylinder (string)` | 气缸注册与查询，注册时把其占用 IO 同步进控制器 |
| `RegisterCylinderIO` | `void (Cylinder, MontionControl)` | 把单个气缸占用的全部 IO 注册进指定控制器 |
| `ServoOnAll` / `ServoOffAll` | `void ()` | 全轴伺服使能 / 下电。⚠️ **2026-09-24 起运控侧不再调用**（[[decisions/ADR-044-SeamEndSemanticsAndMotionAxisScope]]：运控只服务 Y 向焊缝跟踪轴）；保留为 Manager 全轴通用能力（多轴场景 / 维护用）。现场实证：全轴下电会打到送丝力矩电机并报「伺服下电失败 错误码 256」 |
| `ResetAlarmAll` | `void ()` | 全轴复位驱动器报警（逐轴 `MontionAxis.ResetAlarm()`）。⚠️ 同上：运控侧已改为只对焊缝跟踪轴 `ResetAlarm()`；本方法保留供全轴维护场景 |
| `HomeAll` | `bool ()` | 全轴回零，任一失败返回 `false` |
| `SetEmergencyStop` | `void (bool)` | 全局急停（`true` 急停） |

## 主站初始化失败归因（2026-11-13 修正）

> **⛔ 原生 API 失败码不得被吞成超时**：`CS_ECAT_Master_Initial` 返回非 0 时，旧实现把卡号记为哨兵 `99` 后继续轮询 `Check_Initial_Done`，必然在 30s 后报「主站初始化超时」——**超时是最容易被误读为「时间不够」的错误码**，真实原因（厂商返回码）被完全掩盖。

| 环节 | 现行行为 |
|---|---|
| `Master_Open` 失败 | 回写「主站打开失败 错误码 {X} 描述 {Y}」，Error 日志，**不进入后续步骤** |
| `Master_Open` 成功但未检出板卡 | 回写「主站打开成功但未检测到板卡」，Error 日志 |
| `Master_Get_CardSeq` 失败 | 回写「读取板卡序号失败 序号 {n} 错误码 {X} 描述 {Y}」，Error 日志 |
| `Master_Initial` 返回非 0 | **立即失败**：回写「主站初始化失败 卡号 {n} 错误码 {X} 描述 {Y}」，Error 日志；该卡号记哨兵 `99`（关闭时跳过 `Master_Reset`）；**首卡失败直接返回**，不再空等超时 |
| `Master_Initial` 成功 | 记录真实卡号；随后 `WaitInitialDone` 轮询 `Check_Initial_Done`，超时上限取 `FlowTimeoutSettings.Current.MasterInitSeconds`（配置 `ROOT/FLOW_TIMEOUT/MASTER_INIT_SECONDS`，缺省 30s，值域 [5,300]，可在系统设置页「流程与设备等待超时」卡片调整） |
| 主站已打开但初始化失败 | `_masterOpened = true` ⇒ `Close()` 仍会执行 `Master_Reset`（跳过哨兵卡）+ `Master_Close`，**主站不残留** |

> ⚠️ 调大「主站初始化超时」**不能**修复初始化失败：厂商调用返回错误码时已立即失败并上报。只有厂商调用确实长时间未完成时，超时才是原因。
> 教训见 [[lessons/StartupInitializationOrderGates]] 坑 6。

## 使用模式

```csharp
// 1. 初始化（唯一出现厂商具体类型的地方在 MontionManager 内部）
string msg = string.Empty;
if (!MontionManager.Instance.Initialization("台达运控", ref msg))
{
    // 处理失败
}

// 2. 按名取轴并运动（面向 L2 抽象，单位=工程单位 mm）
MontionAxis axis = MontionManager.Instance.GetAxis("水平轴");
axis.ServoOn();
axis.AbsMove(100.0, 20.0);   // 绝对运动到 100mm，速度 20mm/s

// 3. 输出 IO
OutputIO weldStart = MontionManager.Instance.GetOutputIO("焊枪启动");
weldStart.SetON();           // 台达 NPN 低电平有效，内部写 0

// 4. 关闭
MontionManager.Instance.Close();
```

## 约束

- **禁止**在业务层 `new DeltaMontionControl` / `DeltaMontionAxis` / `Delta*IO`——如需按厂商特化能力，显式转型后调用，且不得扩散到业务代码。
- 轴/IO 由控制器持有列表并**构造时自注册**（`Container.AddAxis(this)` / `AddIO(this)`）；注册表是**业务侧按名索引表 + 注册保障**，需调用方显式 `Add*`。
- 气缸由 `IMotion/Cylinder.cs` 承载（Builder 链式装配），`Cylinder.GetAllIO()` 枚举其占用的全部 IO。
- 日志直连 `GlobalCommData.ShowLog`，标签为「运动管理器」，纯文本无符号（[[standards/CodeSimplification]]）。

## 总线健康检查契约（2026-09-08）

`MontionControl.CheckBusOK(out string faultDesc)`（**L2 virtual 默认实现**，沿 IPVTMotion 契约范式：未覆写返回 false +「未实现」描述）；
L3 `DeltaMontionControl` 覆写：逐从站读 `CS_ECAT_Slave_Get_Connect_Status`（opState + 报警位，共享内存级非阻塞），
首个非就绪从站给出「从站 N 非运行态或存在报警」。消费方：`DeviceStatusWork.ScanMotionBusFault()`
（IOWork 每 200ms 监督，OK→NG 置 `IoMotionBusFault` 电平型虚拟 IO → `DoMotionBusFault` 置 Alarm，详见 [[api/DeviceStatusWork]]）。

> **WKC 计数说明**（v1 未纳入，预留观测点）：EtherCAT 每个报文经从站处理后递增 Working Counter，
> 主站比对「预期 vs 实际」不一致即丢帧——`CS_ECAT_Master_Get_Working_Counter_ErrorCounter` 读累计错误数。
> 台达无应用层心跳，WKC 由 ESC 硬件维护，是**最早的掉线前兆**（先于 opState 变化）；因阈值与启动期噪声特性
> 需现场数据标定，v1 只做连接态检查，WKC 计数可在同一监督点后续增量纳入。

## CSP 实时目标入口（2026-09-16 ADR-027）

本管理器**不新增 CSP 专属 API**——CSP 写目标能力挂在轴对象上（api/ICspMotion 契约）：

```csharp
// 2026-09-21 起：CSP 焊缝跟踪轴由 Manager 直接下发具体类型，流程层不再自行转型
DeltaMontionAxis axis = MontionManager.Instance.GetDeltaAxis("焊缝跟踪轴");
if (axis != null)
{
    axis.StartCspMove(axis.GetPosition());           // 先进入周期同步运动
    axis.SetCspTargetPosition(targetMm);             // 之后每拍写目标（OD 607Ah）
}
```

| 用法 | 说明 |
|---|---|
| 取轴 | 通用运动用 `GetAxis(name)`（`MontionAxis`）；**台达专属 CSP 轴用 `GetDeltaAxis(name)`**（`DeltaMontionAxis`）。注册表已按具体类型持有，⛔ 业务层禁止 `as` 下转型 |
| 写目标 | `ICspMotion.SetCspTargetPosition(posMm)`——热路径，按流程节拍（运行态 10ms/100Hz）调用，⛔ 实现层不打日志（ADR-042） |
| 软限位 | `ICspMotion.SetCspSoftLimit(minMm, maxMm)`——非热路径 |
| 急停门控 | `MontionControl.EmergencyStop`——[[api/MotionControlWorkflow]] 的 CSP 步骤**按拍检查**，置位即停写目标（避免在驱动器停机后重新驱动轴）；编排层 `Current != Running` 门控另作双保险（ADR-042） |

> 前置条件：轴已 `Set_Move_Mode(8=CSP)` 且伺服使能——由 `ServoOnAll()` 与 `Initialization()` 保证，接口本身不做模式切换。
> 当前唯一消费方是 [[api/MotionControlWorkflow]] 的 CSP 步骤（按拍输出，ADR-042）；[[api/WeldParamManager]] **不直接引用运控类型**，
> 只暴露目标值供其读取（单向依赖）。

## 轴/IO/气缸注册表（MontionAxis / DeltaMontionAxis / AxisRegistry / CylinderRegistry / IORegistry）

> 2026-09-17 补记（源码核对）：注册表体系位于 `MotionControl/AxisRegistry.cs`、`IORegistry.cs`、`CylinderRegistry.cs`；轴抽象在 `IMotion/MontionAxis.cs`，台达实现在 `DeltaEtherCAT/DeltaMontionAxis.cs`。

### 运行时链 vs 配置链（两链不可混用）

| 链 | 入口 | 返回类型 | 承载内容 |
|---|---|---|---|
| **运行时链** | `MontionManager.Instance.GetAxis(name)` / `Axes.Get(name)`（`AxisRegistry`） | `MontionAxis`（L2 抽象） | `AxisNo`、`Container`（所属控制器，构造时 `_connectNo = container.ConnectNo` 并 `container.AddAxis(this)` 自注册）、`Equiv`/速度/回零参数 + 全部运动方法 |
| **配置链** | `DeltaMotionConfig.GetAxis(axisName)`（`DeltaEtherCAT/DeltaMotionConfig.cs`） | `DeltaAxisConfig`（纯配置） | `NodeId`（站点号）、`SlotNo`（槽号）、`Enabled`、`PositiveLimit` / `NegativeLimit`（正负软限位）+ 与轴同名的参数字段；**无 AxisNo**（台达按卡号+站点号+槽号三级寻址） |

### TA 送丝Z轴 · CST 力矩（2026-10-08 ADR-042 落地）

`DeltaAxisConfig` 由 19 属性增至 **22**（轴表 CSV 表头同步 19 → 22 列，XML `AXIS` 段同步读写）：

| 字段 | 类型 | XML 键 | 含义 |
|---|---|---|---|
| `TorqueModeEnabled` | bool | `TORQUE_MODE` | 是否走 CST 力矩模式（false 走常规 CSP 位置模式）。**2026-11-05 起仅送丝轴消费**；TA 侧不再读写该位（缺键默认 FALSE，旧 XML 可正常加载，ADR-082 D7） |
| `TorqueTarget` | short | `TORQUE_TARGET` | 目标力矩（额定千分比） |
| `TorqueSlope` | uint | `TORQUE_SLOPE` | 扭矩爬升速率（0.1%/s，1~65535；**UI 唯一入口 = TA 轴「参数」弹窗 `AxisConfigForm`**，2026-11-05 自系统设置页迁入） |

`DeltaMontionAxis` 新增两方法（`GetCurrentTorque` 早已存在，本轮未重复实现）：

| 方法 | 落到厂商 API |
|---|---|
| `SetTorque(short, uint)` | ~~`CS_ECAT_Slave_CST_Start_Move`~~ ⇒ **2026-11-03 补全为三步**：`Motion_Set_MoveMode(CST=10)` → `CST_Start_Move(目标扭矩, 扭矩爬升速率, 曲线模式)` → `CST_Output_Enable(1)`；任一步非 `NO_ERROR` 即 `RestoreCspMode()` 回滚。下发前逐项拦截：目标扭矩 ∈ ±1000 且 ≠0、扭矩爬升速率 ≠0、`PreMotionCheck`、状态字 bit2/bit3、`Home_Status≠1`、`Get_MoveMode` 回读须为 10，失败均打印中文原因（2026-11-03 现场 `4609`） |
| `GetMoveMode()` / `GetHomeStatus()` | 新增只读探针（2026-11-03）：`Motion_Get_MoveMode` / `Home_Status`，用于模式切换回读与回零流程判定 |
| `StopTorque()` | `CST_Output_Enable(0)` → `Motion_Set_MoveMode(CSP=8)`（先撤输出再切模式） |
| `RestoreCspMode()`（私有） | `Motion_Set_MoveMode(CSP)`，失败路径唯一出口，防「半使能」 |

⚠️ **撤力矩用 `CST_Output_Enable` 不用运动减速** —— 送丝下压力要求立即撤除，缓减速会使丝继续下压。

⚠️ **`Curve_Mode` 语义未在 DLL 清单给出** ⇒ 暂固定传具名常量 `TorqueCurveModeTrapezoid = 0`，并在注释标注「现场须回台达手册核实」。⚠️ 遵守 ADR-027：**厂商 API 语义回原厂手册核取值，勿信常量名/旧注释**。

⚠️ **`4609` = `0x1201 ERR_ECAT_API_PARAMETER`**（本地 `raw/delta/EtherCAT_DLL_Err.cs`）—— 现场由 `CST_Start_Move` 的目标扭矩/扭矩爬升速率为 0 触发（`TA_FORCE_N=0`、`TORQUE_SLOPE=0`），**不是回零未完成或模式冲突**；回零类错误是 `0x1106 NEED_HOMECONFIG` 与 `0x1209 HOME_MODE`。

✅ **2026-10-09 批E（F-1，[[decisions/ADR-057-TaLaActionAndFollowControl]]）已接消费方**：`SetTorque` / `StopTorque` 由 `LaserWeldHeadWorkflow.TaAuto()`（设下压力）/ `TaBreak()`（当前位置锁止，仅 auto 态）消费，轴名走 `DeltaMotionConfig.TaAxisName` 配置键。`TaAuto` 实传 `TaForceN`（**力的大小，非负**）+ `TaHomeConfig.TorqueDirection`（±1）+ `TorqueSlope`（轴配置），为零/负值/越界时先行拦截并提示（2026-11-05）。9 个 TA/LA 动作方法的 UI 绑定留 P4（U-1/U-2/U-5 按钮组）。

⛔ **CS1061 坑**：`MontionAxis` **没有** `NodeId` / `SlotNo` / `Enabled` / 正负限位成员（这些只在配置类 `DeltaAxisConfig` 上）；`DeltaMontionAxis` 的 `NodeId` / `SlotNo` 是只读属性（构造时传入）。把配置链当运行时链（或反之）直接编译报错。已在 [[api/SystemControlPage]] 页记载（原 `MontionConfigForm` 已于 2026-09-17 废弃并迁入该页 `panel1`），两页互链。

### 三张注册表（统一形态：Register / Get / Contains / GetAll / GetNames / Remove / Clear）

| 注册表 | 元素类型 | 要点 |
|---|---|---|
| `AxisRegistry`（`MontionManager.Instance.Axes`） | `DeltaMontionAxis` | **2026-11-10 收紧**：字典 / `Register` / `Get` / `GetAll` 均按台达具体轴声明（ADR-027 后无其它实现）；`Get(name)` 返回 `DeltaMontionAxis`，可隐式转 `MontionAxis` 供通用运动使用；`AttachAll(MontionControl)` 幂等回灌控制器 |
| `IORegistry`（`MontionManager.Instance.IOs`） | `InputIO` / `OutputIO` | 输入与输出**分表存放**（`_inputs` / `_outputs`），键名空间独立、允许同名；`InputCount` / `OutputCount` |
| `CylinderRegistry`（`MontionManager.Instance.Cylinders`） | `Cylinder` | 气缸由到位传感器 + 电磁阀复合；`AttachAll` 把每个气缸占用的全部 IO 逐个注册进控制器 |

- 轴对象**构造时已向所属控制器自注册**（`MontionAxis(container, aName)` 构造内 `container.AddAxis(this)`），`AttachAll` 是第二次幂等回灌，用于校验注册表与控制器集合一致。
- `DeltaMontionAxis(MontionControl mControl, string aName, ushort nodeId, ushort slotNo = 0)`：`NodeId` / `SlotNo` 构造后只读；卡号实时取自控制器（`_deltaControl.CardNo`）。

### 流程等待超时（2026-11-06 ADR-093）

`FlowTimeouts`（`DeltaMotionConfig.FlowTimeouts`，落盘 `ROOT/FLOW_TIMEOUT`，**26 键**）是运控侧等待超时的唯一真相源。

| 成员 | 语义 |
|---|---|
| `MontionManager.Instance.FlowTimeouts` | 配置对象读写入口；界面「修改参数」直接改字段 |
| `MontionManager.Instance.ApplyFlowTimeouts()` | 值域校验 → 发布运行期快照 → 落盘；非法值回退缺省并告警 |
| `FlowTimeoutSettings.Current` | 运控侧运行期只读快照；各等待点每次进入时读取，改配置后无需重启 |
| `Comm.SystemComm.DeviceWaitSettings` | 设备侧等待五项只读镜像（相机/落盘/线激光回调/Modbus 连接/读写），避免底层反向依赖运控命名空间 |
| `TryGetAxisReadout(axisName, out pos, out lastCommand, out servoOn, out fault)` | UI 只读摘要；不暴露轴对象、不解析状态字位 |

- 缺省值 = 改造前硬编码值（指令检测 5s / 采样 20ms / 运动到位 60s / 回零 120s / 伺服 3s / TA 零位 10~60s / 相机 5s / 落盘 5s / 线激光回调 200ms / Modbus 连接 3000ms / 读写 5000ms）。
- `InstructionDetectTimeoutSeconds` 等公开常量**仅作缺省值与文档引用**，运行期一律用内部 `Effective*` 属性。
- ⛔ 流程代码禁止新增固定秒数；新增等待必须在 `FlowTimeoutConfig` 补键 + 系统设置页补输入。

## 关联

- 三层架构与铁律：[[modules/MotionControl]] §台达 EtherCAT 运动控制（现行）
- 落地规范：[[guides/DeltaEtherCAT-DevGuide]]
- 决策：[[decisions/ADR-027-MotionControllerDeltaReplacement]]、ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[decisions/ADR-029-CylinderConfigAndCsvImport]]（气缸配置化 + CSV 导入）
- CSP 能力契约：api/ICspMotion（层归属决策 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]、ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]））
- CSP 消费方：[[api/MotionControlWorkflow]]（CSP 步骤按拍输出）
- ⛔ 已废弃前身：旧 `MotionManager.cs` 单例（正运动专属，2026-09-07 随正运动一并删除，见 ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]））


## 轴控制统一入口六函数（2026-10-19，ADR-073）

| 函数 | 签名 | 语义 |
|---|---|---|
| `MoveTo` | `bool MoveTo(MontionAxis axis, double target)` | 绝对定位（posMode=1），**伺服未使能自动使能** |
| `StepMove` | `bool StepMove(MontionAxis axis, double delta)` | 相对步进（posMode=0，delta 可负） |
| `ToggleServo` | `bool ToggleServo(MontionAxis axis)` | 使能翻转，返回翻转后状态 |
| `JogStart` | `void JogStart(MontionAxis axis, ushort dir)` | 连续点动（1=负向 0=正向） |
| `StopAxis` | `void StopAxis(MontionAxis axis)` | 减速停止（点动松开与停止按钮共用） |
| `HomeAxis` | `void HomeAxis(MontionAxis axis)` | 非阻塞回零 |

约束（ADR-073）：null 轴一律不下发（前三者回 false）；**UI 页禁直控 `MontionAxis` 控制成员**

（`AbsMove/JogMove/AxisStop/ServoOn/ServoOff/HomeNoBlock` 调用数=0 判据）；日志/Message 留页面（ADR-016）；
查找沿 `GetAxisByKeys`（ADR-066 定位 · 089 控制成对）。消费方：SystemControlPage 固定按钮与 `Do*` 日志包装、
ProcessControlPage `MoveAxisToTarget`。

> **2026-11-08（ADR-093 决策七）**：按轴角色的手动操作分发 `TryManualAxisOperation` 已迁至 `MotionControlWorkflow`，本类不再提供；UI 调 `MotionControlWorkflow.Instance.TryManualAxisOperation`。上表六函数保留为**单轴基础指令**（无角色/工艺语义）。

## TA 力矩输出与可用性（2026-11-05 收敛版，ADR-082）

| 成员 | 签名 | 语义 |
|---|---|---|
| `TaAvailable` | `bool`（只读） | **TA 指令可执行** = `TaMotionReady && TaHomed`（⛔ **2026-11-17 改版（ADR-082 D26/D30）**：去掉 `_taZeroPoseGate`，工作零位到位拆为 `TaAtWorkZero` 只读观测位，不再是 TA 指令门禁）；⛔ 与「是否处于力矩输出」无关 |
| `ExitTaTorqueMode`（私有） | `void ExitTaTorqueMode(MontionAxis axis, string action)` | 六个轴控制函数（`MoveTo`/`StepMove`/`ToggleServo`/`JogStart`/`StopAxis`/`HomeAxis`）动作前调用：命中 TA 轴且 `TorqueOutputEnabled` 时 `StopTorque()` + 日志「先停 TA 力矩输出并回 CSP」 |
| `SetTaZeroPoseGate(bool done, string reason)` | `void` | **2026-11-09 新增**：TA 工作零位门禁写入口，由 [[api/MotionControlWorkflow]] 判定结果后写入；本类只做门禁判定，⛔ 不持有 TA 角色语义 |

> **2026-11-09（ADR-094 D1/D3）**：`ExitTaTorque` / `SetTaTorqueMode` / `SetTaTorque` / `StopTaTorque`（原 `SetWireFeedTorque*`）、`TaZeroPoseStageChanged` 事件与四态属性、`BuildMachineInitSummary` / `LogAxisGateReport` 均已迁至 [[api/MotionControlWorkflow]]。本类只保留硬件层职责：按配置实例化轴、按轴门禁、单飞登记、到位等待、原始状态摘要。
> `DescribeAxisDiagnosis` **按 ADR-094 D2 保留在本类**（纯硬件只读快照，被 `YGateReason` / `GetAxisGateReason` / `EnableAxesAfterInit` 依赖）。

- **删除**（2026-11-05）：`TaTorqueModeEnabled`、`SetTaTorqueMode`、`TaTorqueModeChanged` —— 三者把「运行期模式」与「功能可用性」混成一个 bool，导致 Break/Pose/Retract 后 Auto 永久置灰（见 [[lessons/TorqueModeAsUiGate]]）。
- **力矩输出态**唯一来源 = `DeltaMontionAxis.TorqueOutputEnabled`（`SetTorque` 三步全成功后置 true；`StopTorque`/`RestoreCspMode` 置 false）。
- **复用判定**（`DeltaMontionAxis.SetTorque`）：~~`_torqueOutputEnabled` ∧ `GetMoveMode()==CST` ∧ 目标扭矩/扭矩爬升速率 == 上次成功值，三者 AND 才跳过切模式~~ → **2026-11-06 已删除**（ADR-087）：任何进入力矩出力的路径都重新下发目标与 slope，避免 `TORQUE_SLOPE` 改小后被旧斜率沿用。
- **CST 进入协议（2026-11-06，ADR-087）**：冷启动（输出关或非 CST）= `IsMoving` 停稳（3s 超时即拒绝）→ `Set_MoveMode(CST)` 且回读 == 10 → `CST_Start_Move(±1‰ 方向种子)` → `CST_Output_Enable(1)` → `CST_Start_Move(目标, slope)`；热切换（输出开且 CST）= 直接 `CST_Start_Move(目标, slope)`。最后一次目标下发必须在输出开启之后，冷启动才经历斜坡；方向种子与目标同号，覆盖驱动器内残留的反向扭矩指令。
- **XML 键 `TORQUE_MODE` / `DeltaAxisConfig.TorqueModeEnabled` 保留**：TA（送丝即 TA）力矩模式仍消费该位，CSV（`MotionConfigImporter`）与现场既有 XML 依赖该键；`ChildValueAny` 缺键默认 FALSE，旧文件可正常加载。TA 侧不再读写该位（⛔ 不是死配置）。
- UI 页不得直接读写 `DeltaAxisConfig`；系统设置页已无「力矩模式」开关。


### TA 回零四参（2026-11-04 扩充，ADR-080；2026-11-05 删除 P1.087/P1.088 两项 → 六参变四参）

| 参数 | 参数组属性（`DeltaTaHomeConfig.TaHome`） | 台达对象 | UI 入口 |
|---|---|---|---|
| 回零模式 | `HomeMode`（**short**，-4~35） | 16#6098:00（U16 强转） | TA 表「参数」弹窗 |
| 回零高速 | `HomeFirstVel`（**rpm**） | 16#6099:01 | 同上 |
| 回零低速 | `HomeSecondVel`（**rpm**） | 16#6099:02 | 同上 |
| 回零加速时间 | `HomeAcc`（毫秒，0→3000rpm 时间） | 16#609A:00 | 同上 |

> ⛔ **P1.087 / P1.088 已于 2026-11-05 整体废弃**：`DetectTorquePercent` / `StopArrivalMs` 属性、XML 键 `TA_HOME_DETECT_TORQUE` / `TA_HOME_STOP_ARRIVAL_MS`（及 `AXIS` 的 `HOME_DETECT_TORQUE` / `HOME_STOP_ARRIVAL_MS`）、弹窗两行字段与校验、全部写/读链路均已删除。**勿再尝试 SDO 写 16#2157 / 16#2158**（现场写后回读报 `4869`，手册未收录；台达结论：伺服参数用驱动器默认值即可）。旧 XML 中若仍有这两键 = **遗留键，不再生效**，加载忽略、不报错、不删除。详见 [[decisions/ADR-080-DeltaTorqueHomingSignedModeAndDetectParams]] §D6。

- 落盘：**`DeltaMotionConfig.TaHome` → `ROOT/TA_HOME`**（`TA_HOME_MODE / TA_HOME_FIRST_VEL / TA_HOME_SECOND_VEL / TA_HOME_ACC`；2026-11-05 起不再写 `TA_HOME_DETECT_TORQUE` / `TA_HOME_STOP_ARRIVAL_MS`），单一真相源；旧文件缺节点时从 TA 的 `AXIS` 既有回零值 seed，保存时镜像回 TA 节点（**Y 轴 AXIS 零改动**）；⛔ 不进 `WeldParamManager`。
- `TaHomeConfig`：只读属性，供弹窗显示；修改必须走 `SaveTaHomeConfig()`。
- `TaAxisConfig`：只读属性（2026-11-04 二次修订新增），返回 TA 自己的 `AXIS` 配置实例，供弹窗预填**通用区**；⛔ 弹窗不直接 `new` 或自行遍历 `MotionConfig`。
- `SaveTaHomeConfig(DeltaTaHomeConfig)`：TA 回零参数**统一保存入口** → 写入 TaHome → `SaveConfig()` → `ApplyTaAxisRuntimeConfig()`；生效时机为**下次回零**（无需重新使能/重连）。弹窗「通用区」改动写入 `TaAxisConfig` 实例后同样经本方法落盘（`SaveConfig` 一并写 AXES）。（~~`ApplyTaTorqueHomeDriveParams()`~~ 2026-11-05 已删）
- `ApplyTaAxisRuntimeConfig()`：先 `ApplyAxisConfig` 再用 `TaHome` 覆盖四参（模式/两档速度/加速）；UI 不直接触碰轴对象。
- `ApplyTaHomeOnLoad(DeltaAxisConfig, MontionAxis)`（私有）：`CreateAxesFromConfig` 装载每轴后调用，仅 `AXIS_NAME == TA_AXIS_NAME` 命中时覆盖回零四参并打印日志；**Y 轴不命中、读取路径零改动**；缺 `TA_HOME` 时覆盖值等于 AXIS seed/镜像值。
- ~~`ApplyTaTorqueHomeDriveParams()` / `WriteAndVerifyServoParameter` / `WriteCoEObject` / `ReadCoEObject` / `WaitSdoDone` / `DescribeSdoAbort` / `_torqueHomeCoEObjectMissing` / 使能前预写~~：**2026-11-05 随 P1.087/P1.088 废弃整体删除**（含 `EtherCATMasterNative` 新增的 3 个 SDO P/Invoke；`SDO_Quick_Send_Message`/`Check_Done` 因 `DeltaSlaveDevice` 仍在用而保留）。现场证据 = 写 16#2157 后回读报 `4869`（手册未收录/未确证）；台达结论 = 伺服参数用驱动器默认值即可。
- **负值模式（-3）路径（单主路径）**：台达 2026-11-04 正式确认 `Home_Config` 的 `Mode` 为 **U16**、负值只需底层强转 ⇒ 正负值**统一走 `CS_ECAT_Slave_Home_Config`**，换算 `ToHomeModeWord(short) = (ushort)(mode & 0xFFFF)`（`-3 → 65533`）；写后 SDO 回读 `16#6098` 并按 `ToHomeModeLogical(byte)` 反解打印两端值。~~原 CoE 写 16#6098/6099/609A 分支~~ **已删除**（避免双主路径漂移）；现场口述「-2→65533」判定为举例笔误。详见 [[guides/DeltaEtherCAT-DevGuide]] §15.5.1 与 [[decisions/ADR-080-DeltaTorqueHomingSignedModeAndDetectParams]]。
- **回零到位判据（2026-11-05 移交驱动器）**：`-3` 扭矩回零的「扭力达到阈值 + 持续到达时间」判据由**驱动器默认 P1.087/P1.088** 决定，控制器不再写、不再读这两个伺服参数；`StartHome` 不再有「先补写侦测参数」步骤。**现场已验证**：-3 回零正常（回零成功、table 有反馈），默认参数对该机构够用。
- 单位依据（2026-11-04 官方手册）：`16#6099:01/02` = **rpm**、`16#609A` = **毫秒**（《EtherCAT 程式開發手冊》§12.1 P636）；此前按「工程单位/秒 → ToPulse」换算是错的，已改为 rpm/ms 直写。


## ~~送丝轴力矩模式运行期接口~~ ⚠️ 2026-11-09 整体迁至 [[api/MotionControlWorkflow]]（ADR-094 D5）

> **事实纠正**：**送丝就是 TA，不存在第三个轴** —— 只有 TA、Y 两个台达轴。原 `WireAxisKeys = { "送丝", "WIRE", "FEED" }` 与 `GetWireFeedAxis()` / `GetWireFeedAxisConfig()` / `WireFeedTorqueModeEnabled` / `SetWireFeedTorqueMode` / `SetWireFeedTorque` / `StopWireFeedTorque` 已全部删除。
> TA 角色级力矩动作现为 Workflow 的 `SetTaTorqueMode` / `SetTaTorque` / `StopTaTorque`，统一走 `TaAxis` / `TaAxisConfig`；⛔ 不再造「送丝轴」概念、⛔ 不按三轴口径描述。

**安全边界（不变）**：力矩未使能 / 轴未伺服使能一律拒绝下发（日志明示原因）；`DeltaMontionAxis.SetTorque` 内部任一步失败都 `RestoreCspMode()`，⛔ 不留半使能状态。

## CST 调用序列依据（2026-11-03 核实分级）

| 结论 | 分级 | 出处 |
|---|---|---|
| `CS_ECAT_Slave_CST_Start_Move` / `CS_ECAT_Slave_CST_Output_Enable` 真实存在 | **代码中确有该 API** | `MotionControl/DeltaEtherCAT/EtherCATMotionNative.cs` 的 `DllImport`；`Vicoding管理平台/LLMWiki/raw/delta/EtherCAT_DLL_API清单.txt` 声明 |
| 厂商封装步骤 = 「Start_Move 设扭矩参数 → Output_Enable 开输出」 | **已核实（厂商开发文档示例）** | `raw/delta/运动控制模块开发文档_台达版.md` §CST 示例（非 CiA402 对象字典页码） |
| `MoveMode.CST = 10` | **代码已确认** | `MotionControl/IMotion/Type.cs` L54 |
| 台达手册对 `0x6060=10` / `0x6071` / `0x6040` 使能位序的原文说明 | **未找到依据** | 本地 `raw/delta/` 仅有 DLL API 清单与厂商调用示例，无 CiA402 对象字典章节；通用 CiA402 知识未冒充手册结论 |
| 进出顺序（进：模式→参数→输出；出：输出→模式） | **工程约束（依据厂商封装语义）** | 先置模式再给扭矩，避免旧模式残值；开输出即力矩生效，必须先撤输出再切回 CSP，否则切换瞬间残余扭矩会冲击送丝机构 |

## 初始化统一使能 `EnableAxesAfterInit()`（2026-11-04）

| 成员 | 签名 | 语义 |
|---|---|---|
| `EnableAxesAfterInit()` | `bool`（`public`） | 初始化完成后按配置**一次性**统一使能；返回「无失败轴」 |

- **轴范围**：`Axes.GetAll()` —— 只含 `ENABLED=true` 的轴（`CreateAxesFromConfig()` 已 `if (!cfg.Enabled) continue;` 筛除），无需二次过滤。
- **前置门**：`IsInitialized && MontionControl != null`，否则 `Warning` 日志并返回 false。
- **单轴流程**：`IsServoOn()` 已使能 → 记「跳过」计成功；否则 `ServoOn()`（内部先 `Ralm` 清 fault → 切 CSP → `Set_Svon(1)` → 轮询 `IsServoOn`）→ 复核 `IsServoOn()`。
- **留痕**：`初始化使能 <轴名> 成功` / `初始化使能 <轴名> 失败 原因 <LastCommand>`（`Error`）/ 末尾汇总 `初始化使能完成 成功 N 轴 失败 M 轴`。
- **失败原因来源**：`MontionAxis.LastCommand`（`Set_Svon(1) 超时 错误码 4080` / 急停 / 非 OP / 报警等）。
- ⛔ **不重试、不轮询、不改写轴状态**；`failCount == 0` 才返回 true，调用方据此把初始化判为未完成。
- **兜底关系**：`ServoOnAll()` 仍为 0 调用方的死 API（不删，见预留清单）；`LaserWeldHeadWorkflow.TaAuto` 内部唯一一次 `ServoOn` 保留作兜底，但不再是唯一入口。
- 决策依据见 [[decisions/ADR-081-InitUniformServoOn]]。

## TA 轴初始化四步与工作零位（2026-11-05，ADR-082）

| 步骤 | 入口 | 产出 / 失败后果 |
|---|---|---|
| 第1步 加载轴与默认 XML | `MontionManager` 构造 / `Initialization`：`MoveData.Load()` → `CreateAxesFromConfig()`（`ApplyAxisConfig` + `ApplyTaHomeOnLoad`） | 轴注册表就绪；`_taConfigLoadOk=false`、`SetTaZeroPoseGate(false, null)`（TA 先降级） |
| 第2步 TA 配置加载（装载判定） | `DeviceControlWork.InitStepEvaluate` → `LoadTaAxisConfig()` | 只做**装载判定**（`MoveData.MotionConfig.TaHome` 非空 + `GetDeltaAxisByKeys(TaAxisKeys)` 命中），**不读不写 P1.087/P1.088**（2026-11-05 删链）；失败 → `_taConfigLoadOk=false` + `TaDegradedReason`「TA 轴未装配」 |
| 第3步 配置成功才使能 | `EnableAxesAfterInit()`；TA 轴在内部按 `_taConfigLoadOk` 门禁 | 配置失败 → TA 轴跳过使能、不计入 `failCount`，日志「被拒 原因 TA 轴配置加载失败」 |
| 第3步下半段 TA_ZeroPose | **2026-11-09 起由 [[api/MotionControlWorkflow]] `RunTaZeroPoseAfterInit` 发起**，本类只收结果：`SetTaZeroPoseGate(done, reason)` | 走 CSP 绝对定位到 `TaZeroPoseTargetMm`（**2026-11-06 起唯一来源 = 工艺设置页 `TA_ZERO_POSE_MM`**，不是 `TA_HOME_ZERO_POSE_MM`）；到位写门禁 true；失败写门禁 false + 原因 |
| 第4步 降级/反馈 | `TaAvailable` / `TaDegradedReason` → `LaserWeldHeadWorkflow.CheckTaAvailable`；`ProcessControlPage` **不再置灰**（2026-11-05 改口径） | 降级时指令照常可点，执行前 `CheckTaAvailable` 拒绝 → radio 标红 + Tooltip 写原因 + 日志 |

| 成员 | 签名 | 语义 |
|---|---|---|
| `TaAvailable` | `bool`（只读） | **TA 指令可执行** = `TaMotionReady && TaHomed`（⛔ 2026-11-17：去掉 `_taZeroPoseGate`） |
| `TaDegradedReason` | `string`（只读） | 逐层给出首个不满足条件的原因：未初始化 / 轴未装配 / 配置失败 / 未使能 / ZeroPose 未到位 |
| `TaMotionReady` | `bool`（只读） | 配置已加载 + 已使能（**不含**回零与工作零位到位）；⛔ 2026-11-17 起**不再**作为 TA 指令放行依据（TA_Zero 与其它 TA 指令同口径要求已回零） |
| `LoadTaAxisConfig()` | `bool` | 初始化第2步**装载判定**（配置节点 + 轴注册表），不再做 SDO 读-比对-写（2026-11-05）；成功置 `_taConfigLoadOk`，失败写 `TaDegradedReason` |
| `SetTaZeroPoseGate(bool, string)` | `void` | **2026-11-09 新增（ADR-094 D1）**：工作零位门禁写入口，由 Workflow 判定后调用；本类不产生判定 |

### TA_ZeroPose（工作零位，⛔ 不是回零 Home）

**2026-11-08（ADR-093 决策八）**：轴类 `DeltaMontionAxis` 的 `StartZeroPoseMove` / `WaitZeroPose` / `RunZeroPose` / `StopZeroPoseMotion` / `TaZeroPoseTag` **已全部删除**；编排归 `MotionControlWorkflow`，本类只提供中性基础能力：

| 成员 | 语义 |
|---|---|
| `TryMoveAbsoluteNoBlock(axis, targetMm, velMmPerSec, tolMm, out alreadyInPosition, out rejectReason)` | 参数校验（轴空 / `vel≤0` / `tol<0`）→ `|当前−目标| ≤ 容差` 直通并置 `alreadyInPosition` → 否则 `axis.AbsMoveNoBlock(target, vel, vel, vel, AccTime, DecTime, STime, 1)`（伺服/急停/总线/报警门禁在 `StartMove` 内建，未删） |
| `WaitAxisAtTarget(axis, targetMm, tolMm, cancelRequested, out evidence)` | 5 参重载：容差带 ∧ 速度 ≤0.05mm/s 连续 3 次 ∧ 无报警；超时 `INSTRUCTION_DETECT_SECONDS`（5s） |
| `WaitAxisAtTarget(axis, targetMm, tolMm, timeoutSeconds, noChangeSeconds, cancelRequested, out evidence)` | **2026-11-08 新增 7 参重载**：显式超时 + 位置无变化早停（`noChangeSeconds>0`），免速度稳定判据；供零位类"长行程、慢到位"场景 |
| `TryGetAxisNameByKeys(keys, out axisName)` | 只读轴名解析（`FindAxisNameByKeys` 的 bool 包装），UI 不持轴对象 |

配置键（`Config/MotionControl/Motion_XML/DeltaMotionConfig.xml` → `ROOT/TA_HOME`，`DeltaTaHomeConfig`）：

| 键 | 属性 | 默认 | 单位 | UI |
|---|---|---|---|---|
| `TA_HOME_ZERO_POSE_MM` | `WorkOriginMm`（原 `ZeroPoseMm`，2026-11-08 改名） | 0 | mm（CSP 绝对坐标） | ~~系统设置 → TA 轴「参数」弹窗~~ **2026-11-06 起不再可编辑、不再运行期读取、弹窗也不再展示**：仅作一次性迁移来源（ADR-091） |
| `TA_FORCE_100PCT_N` | `Force100PctN` | **37** | N | 同上（「力—力矩换算」区） |
| `TA_TORQUE_LIMIT_N` | `TorqueLimitN` | **37**（= 100% 力量基准，不降额） | N | 同上（「力矩输出」区，紧邻扭矩爬升速率）；CSP 推动阻抗与 CST 最大出力共用，值域 1N~100% 基准且须 ≥ 当前 `TA_FORCE_N` |
| `TA_TORQUE_DIRECTION` | `TorqueDirection` | **+1** | 无符号（+1 正向 / -1 反向） | 同上（「力矩输出」区，紧邻扭矩爬升速率）；缺键按 +1，⛔ 不新增 `TA_HOME` 之外键 |

⛔ 缺键保留默认、不覆盖现场现值；⛔ 初始化链无 `Home_Config`/`Home_Move`，6098/6099/609A 链路零改动。

**工作零位坐标单一数据源（2026-11-06）**：`TaZeroPoseTargetMm`（只读属性）= `WeldParamManager.Instance.AlgorithmsConfig.TaZeroPoseMm`
（工艺 INI `TA_ZERO_POSE_MM`，与 `TA_POSE1_MM` / `TA_POSE2_MM` 同节同命名风格）；`MotionControlWorkflow.RunTaZeroPoseAfterInit` 只读该属性。
配置未就绪时回退 `DeltaTaHomeConfig.WorkOriginMm`（仅兜底显示/执行，不写回）。速度与容差**复用 TA_Pose1/2 同源**（ADR-091）：
`taAxis.MaxVel`（≤0 兜底 1.0 并告警）+ `InstructionDefaultTolMm`（0.1mm）+ `AccTime/DecTime/STime`，⛔ 无 `TA_HOME_ZERO_POSE_VEL/TOL_MM` 独立键。

## TA 力值 → CST 千分比换算（2026-11-05，ADR-084）

- 基准来源：`TaHomeConfig.Force100PctN`（`ROOT/TA_HOME/TA_FORCE_100PCT_N`，默认 37N = 业主口述 1.4A × 26.1N/A = 36.54 的取整；31A 规格书未到位，默认暂不改 36.54）。⛔ 不在运行时读 PM46/PM49（手册未给数值定义；台达口头口径为 额定电流×推力常数，实现以配置值为准）。
- 换算依据：推力 = 电流 × 推力常数 ⇒ 电流百分比与推力百分比同刻度；额定区扭矩 ∝ 电流 ⇒ CST 千分比与电流千分比同比例。仅在线性区（无弱磁/无饱和）、不含摩擦时成立。
- 换算下沉在 `LaserWeldHeadWorkflow.TaAuto`：`目标‰ = 方向(+1/-1) × round(力大小 / 基准 × 1000)`（`AwayFromZero`），限幅 ±1000；`力大小` 为负 → 显式拒绝并提示方向改到弹窗（⛔ 不静默取绝对值）、`力大小 > 基准` 拒绝、换算后为 0 拒绝、基准 ≤0 拒绝（⛔ 不 1:1 兜底）。
- `SaveTaHomeConfig` 日志已带 `100%力量基准 X N`、`扭矩爬升速率 Y（0.1%/s）`与落盘/推回运行期状态，便于现场对账。
- 旧值迁移（2026-11-05）：`WeldParamManager` 一次性迁移由 `TaForceN = TorqueTarget`(‰) 改为 `TorqueTarget × 基准 / 1000`；随后 `NormalizeTaForceDirection` 把旧负值转「大小 + 方向」——`TA_TORQUE_DIRECTION` 缺键 ⇒ 置 -1 并取绝对值（逐条日志「旧力值 -5.0 方向推断为 -」）；键已存在 ⇒ **以键值为准不覆盖**，仅取绝对值并 Warning 提示核对双负号翻转风险。

## 初始化闸门与指令状态检测（2026-11-05，ADR-082 演进）

| 成员 | 语义 |
|---|---|
| `IsInitCompleted` / `IsInitSucceeded` | 整机初始化唯一闸门 / 初始化结果；由 `MarkInitCompleted(bool)` 在 `DeviceControlWork.InitStepEvaluate` 收尾时置位一次 |
| `MarkInitCompleted(bool allAxesReady)` | 只记整机汇总结果供展示（`IsInitSucceeded`）；⛔ 不再取消各轴单飞登记、⛔ 不再充当各轴指令总闸 |
| `TaAvailable` / `TaMotionReady` | 均在 `_initCompleted=false` 时返回 false；`TaDegradedReason` 首条为「初始化未完成（初始化第3步尚未结束）」 |
| `EnableAxesAfterInit()` | 逐轴使能并打「初始化第3步 开始使能 / 成功 / 失败（含 `LastCommand` 与状态字）/ 使能完成 成功 N 轴 失败 M 轴」；⛔ 内部不再调用 ZeroPose |
| `RunTaZeroPoseAfterInit()` | **2026-11-08 已迁至 `MotionControlWorkflow`**（门禁 + 使能 + 配置 + `TaMotionReady` 全满足才执行一次零位定位）；本类不再提供 |
| `SetTaZeroPoseGate(bool, string)` | **2026-11-09（ADR-094 D1）**：零位门禁唯一写入口，由 Workflow 判定后调用；本类只做判定读取 |
| `TryBeginAxisInstruction(axisName, instruction, out token, out reason)` | 同轴单飞登记；被拒时 `reason` 为「正在执行 X（已 Y.Ys），暂不接受新指令」 |
| `EndAxisInstruction(axisName)` | 释放单飞登记（调用方必须放在 `finally`） |
| `CancelAllAxisInstructions(reason)` | 初始化失败 / 急停 / 页面销毁时请求取消全部检测 |
| `CancelAxisInstruction(axisName)`（私有） | **2026-11-09 新增（ADR-094 D4）**：取消单轴在途检测，供 `StopAxis` 与急停共用；使阻塞等待的 `token` 立即返回 |
| `WaitAxisAtTarget(axis, targetMm, tolMm, token, out evidence)` | 位置进入容差带 ∧ 速度 ≤0.05mm/s 连续 3 次 ∧ 无报警；超时 5s，`evidence` 含「超时 5.0s 未到位 当前 X 目标 Y」 |
| `WaitAxisAtTarget(axis, targetMm, tolMm, timeoutSeconds, noChangeSeconds, cancelRequested, out evidence)` | **2026-11-08 新增**：显式超时 + 位置无变化早停（`noChangeSeconds>0` 时启用），免速度稳定判据；内核与 5 参重载同一份 |
| `TryMoveAbsoluteNoBlock(...)` | **2026-11-08 新增**：中性绝对定位下发 + 已在位直通（见上节 TA_ZeroPose 表） |
| `TryGetAxisNameByKeys(keys, out axisName)` | **2026-11-08 新增**：只读轴名解析 |
| `WaitAxisHomed(axis, token, out evidence)` | `Home_Status==0` ∧ 位置在原点 0.1mm 内 ∧ 无报警；`Home_Status==3` 立即判失败 |
| `WaitTaTorqueOn(axis, token, out evidence)` | `TorqueOutputEnabled` ∧ 模式字 CST(10) ∧ 状态字 Operation Enabled(bit3) ∧ 无报警；确认窗 2 次采样 |
| `WaitTaTorqueOff(axis, holdMm, tolMm, token, out evidence)` | 输出位 0 ∧ 模式回 CSP(8) ∧ 位置保持在锁存点容差内 |
| `WaitLaMotorAtTarget(targetMm, token, out evidence)` | LA 无速度反馈，判据为 `ReadMotorStatus().CurrentPositionMm` 入容差带且位置稳定 |

常量：`InstructionDetectTimeoutSeconds=5.0`、`InstructionSampleIntervalMs=20`、`InstructionStableSampleCount=3`、`InstructionDefaultTolMm=0.1`、`InstructionStableSpeedMmPerSec=0.05`。

## 按轴门禁与设备层边界（2026-11-05，ADR-082 演进）

| 成员 | 语义 |
|---|---|
| `YReady` / `YGateReason` | Y 轴（`SeamTrackYKeys`）：已装载 ∧ 已使能 ∧ 配置就绪 / 不可用原因 |
| `TaAvailable` / `TaMotionReady` / `TaDegradedReason` | TA 指令可执行（已使能+已回零）/ 可动（仅配置+使能）/ 降级原因 |
| `LaReady` / `LaGateReason` | 焊接头从站（对焦电机 + 振镜）就绪 / 原因 |
| `GetAxisGateReason(axis)` | 任意轴单点门禁（UI 的 Home/ToTarget 等直接轴指令用） |
| `DescribeAxisDiagnosis(axis, phase, withBus)` | 失败诊断串：总线状态含义 / 报警码 / `ServoOn` 返回码与 `LastCommand` / 从站是否发现 / 一句人话结论（未确证项标「未确证」）；**ADR-094 D2 保留本类**（纯硬件只读快照） |
| `DescribeAxisStatusWord(axis)` | **硬件故障文本唯一产出点**（ADR-095）：`状态字 0x…`，取不到写「未取到」 |
| `DescribeAxisCspRuntime(axis)` | CSP 缓冲运行证据：`总线状态 … 报警状态 … 缓冲状态 … 块数 …`，非台达轴/读失败写「未取到」 |
| `DescribeAxisCommandReturnCode(code)` | `返回码 0x…`（PVT 等指令返回码） |
| `DescribeAxisRetractFailure(code)` | `撤力失败（错误码 N）`（TA 撤力失败） |
| `IsNodeDetected(ushort nodeId)` | 从站扫描结果查询 |
| `AxisReadinessChanged(string axisName)` | **轴就绪变化事件**（"Y"/"TA"/"LA"/"ALL"）；两 workflow 转发为 `AxisReadyChanged`，UI 收到即刷新 |

> **2026-11-09（ADR-094 D1/D3）**：`BuildMachineInitSummary` / `LogAxisGateReport` / `TaZeroPoseStageChanged` / `MarkTaZeroPose*` / 四个 `IsTaZeroPose*` 属性已迁至 [[api/MotionControlWorkflow]]；本类不再讲整机初始化故事、不再持有 TA 角色语义。

- **设备层职责边界**：本类是**硬件/连接层**唯一归属 —— 轴对象、轴配置、使能、SDO、回零状态、单飞登记、状态检测族都在此；
  **流程层**（哪条指令做什么、按什么判据放行）归 [[api/MotionControlWorkflow]]（Y/TA）与 [[api/LaserWeldHeadWorkflow]]（LA）。
- **全局安全 vs 按轴功能**：急停、总线非 OP、驱动器报警属**全局安全**，任何轴一律拒绝；使能失败 / ZeroPose 未到位 / 单轴报警属**按轴功能**，只关该轴闸门。
- `MarkInitCompleted(allAxesReady)` 只落整机汇总供展示，`InitializationCompleted` 订阅方不得再当作各轴总闸。

## ~~手动 ZeroPose 重试闭环与失败上色~~ ⚠️ 2026-11-09 迁至 [[api/MotionControlWorkflow]]（ADR-094 D1）

- 四态（运行 / 跑过 / 到位 / 失败）、`TaZeroPoseStageChanged` 事件与 `MarkTaZeroPose*` 已全部迁出；本类只保留 `SetTaZeroPoseGate(done, reason)` 作为门禁写入口。
- **单飞逾期释放**：TryBeginAxisInstruction 对占用超过 AxisInstructionLeaseSeconds（600s）的登记项自动移除并告警，防异常路径漏 EndAxisInstruction 导致该轴永久 BUSY；拒绝文案未变。

## TA 回零满扭矩与 TaHomed 门禁（2026-11-11）

| 项 | 变化 |
|---|---|
| 回零扭矩 | `DeltaMontionAxis.FullTorqueOnEnable`（TA 轴置真）→ 使能时 `16#6072 = TorqueRatedPermille`（满量程）；CST 目标仍按 `TorqueLimitPerMille` 软件钳制，下压力不受影响 |
| 生效时点 | `16#6072` 只能在伺服 OFF 窗口写，故随每次使能写入；`_appliedDriveTorqueLimit` 缓存遇到满扭矩会重写 |
| 回零到位判据 | `WaitAxisHomed` 改为 `|pos − HomeOffset| ≤ InstructionDefaultTolMm`，不再一律拿 0 当原点（`HomeOffset≠0` 时旧判据永不通过） |
| 收尾复核 | 判稳通过后再读一次位置，偏差超容差打「回零后位置漂移」日志，不静默接受 |
| 回零结论 | `TaHomed`：本次上电是否已回零；`WaitAxisHomed` 成功置位，`MarkInitCompleted(false)` 清零 |
| 门禁 | ⛔ **2026-11-17 改版（ADR-082 D26）**：原式 `TaAvailable = TaMotionReady ∧ TaHomed ∧ _taZeroPoseGate` 改为 **`TaAvailable = TaMotionReady ∧ TaHomed`**（工作零位到位拆为 `TaAtWorkZero` 观测位，不再是 TA 指令门禁）；`TaDegradedReason` 文案改为「TA 未回零（…须先完成回零：手动回零或复位回零均可）」，`TA_Auto`/`TA_Pose`/`TA_Break`/`TA_Retract` 在**已回零**后放行 |

- 稳定性采样仍为 `InstructionStableSamples × InstructionSampleMs`（默认 3×16ms ≈ 48ms），未改动；回零另由收尾复核兜底，现场可用配置调大采样数。
- 上电位置不可信的依据与规则见 [[standards/DeviceInitializationDependency]] §七。

## TA 门禁语义拆分与手动轴操作非阻塞（2026-11-17，ADR-082 D26 / ADR-073 D25）

| 成员 | 现行语义 | 备注 |
|---|---|---|
| `TaAvailable` | **TA 指令可执行** = `TaMotionReady && TaHomed` | 已使能 + 已回零；⛔ 不再要求「已到工作零位」 |
| `TaAtWorkZero` | 工作零位是否到位（L4 只读观测位） | 不参与 TA 指令门禁 |
| `TaZeroPoseReason` | 工作零位未到位原因（观测用） | 附在 TA 拒绝原因尾部 |
| `TaDegradedReason` | 不可执行原因（可读文本） | 「TA 未回零（…手动回零或复位回零均可）」 |

- **回零结论唯一置位点**：`TaHomed` 只在 `WaitAxisHomed` 成功时置位 ⇒ 手动回零必须走 `MotionControlWorkflow.TryHomeAxisWithWait`（与复位回零同一实现），否则「已回零」结论不成立，TA 指令全被拒。
- **手动轴操作非阻塞**：新增 `MoveToNoBlock` / `StepMoveNoBlock`（走 `AbsMoveNoBlock`，只下发不等到位）；⛔ `MoveTo` / `StepMove` 阻塞等到位，禁在 UI 线程调用。
- **已删除**：`HomeAxis`（非阻塞回零）与 `AxisManualOperation.Home` —— 回零统一走 `TryHomeAxisWithWait`。
- 关联：[[decisions/ADR-082-TaInitFourStepAndAvailability]] · [[decisions/ADR-073-AxisControlUnifiedMontionManager]]
