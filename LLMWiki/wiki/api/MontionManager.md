---
title: API — MontionManager 运动管理器（业务层单例，取代已废弃的 MotionManager）
date: 2026-09-07
tags: [API, 运控, 台达, EtherCAT, 管理器, 单例, 业务层]
source: AdaWeldSystem/MotionControl/MontionManager.cs
---

# API — MontionManager 运动管理器

> **位置**：`MotionControl/MontionManager.cs`（命名空间 `AdaWeldSystem.MotionControl`）
> **2026-09-07 新增**：取代已删除的 `MotionManager`（见 [[decisions/ADR-037-ZMotionRemovalAndDeltaLanding]]）。
> **定位**：业务层唯一装配点。面向 [[modules/MotionControl]] 的 L2 抽象（`IMotion/`）编程；厂商具体类型 `Delta*` **仅在本文件 `Initialization()` 中出现一次**。
> **2026-09-07 重构**：内部四个裸字典已由三张注册表（`AxisRegistry` / `IORegistry` / `CylinderRegistry`）取代，对外 API 名字与签名**保持不变**。
> **同日追加**：持有 `MoveControlData MoveData`（构造时 `new` 并 `Load`），成为**唯一对接台达控制器的对象**；轴与 IO 在 `Initialization` 中按 `MoveData.MotionConfig` 的配置表创建。

## 职责

1. 单例持有当前控制器（`MontionControl`）；
2. 持有并暴露 `MoveData`（`MoveControlData`），标定与轴/IO 配置的唯一对外入口；
3. 持有三张注册表，按名注册与查询轴 / 输入 / 输出 / 气缸，并在注册与初始化时把对象登记进控制器；
4. `Initialization` 按配置表建轴与 IO：`MotionConfig.Axes` → `DeltaMontionAxis`、`Inputs` → `DeltaInputIO`、`Outputs` → `DeltaOutputIO`，并套用 `Equiv`/速度/回零参数；
5. 批量操作（全轴使能 / 下电 / 回零、全局急停）与关闭清理。

## 公共 API

| 成员 | 签名 | 说明 |
|------|------|------|
| `Instance` | `static MontionManager` | 单例（`Lazy<T>` 实现） |
| `MontionControl` | `MontionControl { get; private set; }` | 当前控制器，未初始化时为 `null` |
| `IsInitialized` | `bool { get; private set; }` | 是否已初始化 |
| `MoveData` | `MoveControlData { get; private set; }` | 运控数据（标定转发 + 持有 `DeltaMotionConfig`），构造时创建并加载 |
| `Axes` | `AxisRegistry { get; private set; }` | 轴注册表 |
| `IOs` | `IORegistry { get; private set; }` | IO 注册表（输入 / 输出分表） |
| `Cylinders` | `CylinderRegistry { get; private set; }` | 气缸注册表 |
| `Initialization` | `bool (string devName, ref string msg)` | 先 `MoveData.Load()`，再装配 `DeltaMontionControl` 并初始化，随后按配置建轴与 IO，最后 `AttachAll`；失败回写 `msg` |
| `AttachAll` | `void ()` | 把三张注册表的全部对象回灌注册进当前控制器（幂等） |
| `Close` | `void ()` | 急停 → 关控制器 → 清空三张注册表 → `IsInitialized=false` |
| `AddAxis` / `GetAxis` | `void (string, MontionAxis)` / `MontionAxis (string)` | 轴注册与查询，注册时同步进控制器 |
| `AddInputIO` / `GetInputIO` | `void (string, InputIO)` / `InputIO (string)` | 输入注册与查询 |
| `AddOutputIO` / `GetOutputIO` | `void (string, OutputIO)` / `OutputIO (string)` | 输出注册与查询 |
| `AddCylinder` / `GetCylinder` | `void (string, Cylinder)` / `Cylinder (string)` | 气缸注册与查询，注册时把其占用 IO 同步进控制器 |
| `RegisterCylinderIO` | `void (Cylinder, MontionControl)` | 把单个气缸占用的全部 IO 注册进指定控制器 |
| `ServoOnAll` / `ServoOffAll` | `void ()` | 全轴伺服使能 / 下电 |
| `HomeAll` | `bool ()` | 全轴回零，任一失败返回 `false` |
| `SetEmergencyStop` | `void (bool)` | 全局急停（`true` 急停） |

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

## 关联

- 三层架构与铁律：[[modules/MotionControl]] §台达 EtherCAT 运动控制（现行）
- 落地规范：[[guides/DeltaEtherCAT-DevGuide]]
- 决策：[[decisions/ADR-036-MotionControllerDeltaReplacement]]、[[decisions/ADR-037-ZMotionRemovalAndDeltaLanding]]
- ⛔ 已废弃前身：旧 `MotionManager.cs` 单例（正运动专属，2026-09-07 随正运动一并删除，见 [[decisions/ADR-037-ZMotionRemovalAndDeltaLanding]]）
