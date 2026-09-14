---
title: ADR-033 移除正运动（ZMotion）并全面落地台达 EtherCAT + 消费方全量对接
date: 2026-09-07
tags: [决策, 运控, 台达, EtherCAT, 正运动, 移除, 消费方对接, 代码精简]
status: accepted
---

# ADR-033 移除正运动（ZMotion）并全面落地台达 EtherCAT + 消费方全量对接

## 背景

[[decisions/ADR-032-MotionControllerDeltaReplacement]] 已裁定运动控制器采用**台达 PCI-L221 EtherCAT 主站卡**，并明确按**全新模块**设计（目录结构与对外消费关系以原档为准，不写「与既有实现对比/替换/迁移」）。

2026-09-07 用户下达四项执行需求：

1. **移除 Zmotion**（正运动）运动控制全套实现；
2. **全面编写台达的运动控制**模块；
3. **台达消费方全量对接**（所有引用方切换到新抽象）；
4. 新建代码和修改代码的**精简和注释精简**。

本 ADR 记录执行结果、冲突裁定与遗留 OPEN。

## 决议

### R1 正运动全套删除（含依赖与遗留组件）

| 删除对象 | 规模 | 说明 |
|----------|------|------|
| `MotionControl/ZMotion/`（10 文件） | 约 5100 行 | `ZMotionController` / `ZMotionAxis` / `ZMotionIO` / `ZMotionNative` / `ZMotionNativeLaser` / `ZMotionGalvo` / `InterpolationEngine` / `EncoderAxis` / `CamBoxTracker` / `RSIPositionBuffer` |
| `MotionControl/API/`（4 文件） | — | `IAxis` / `IIO` / `IMotionController` / `MotionControllerBase`（旧三层，已被 `IMotion/` 取代） |
| `MotionControl/MotionManager.cs` | — | 旧单例，被 `MontionManager` 取代 |
| `MotionControl/MotionConfig.cs` | 759 行 | 正运动专属配置（IP / 心跳 / BAS / CAMBOX / ATYPE25） |
| `3rdDepend/{zauxdll,zmotion,ZmotionScanLaser}.dll` | — | 正运动原生依赖（**用户裁定：删除，暂不建新配置**） |

**用户裁定（4 项冲突点）**：

| 冲突点 | 裁定 |
|--------|------|
| L2 抽象层命名基准 | **以原档与规范页为准**（雷赛仅作参考，不是当前实现） |
| 正运动遗留高级组件（CamBoxTracker / EncoderAxis / InterpolationEngine / RSIPositionBuffer） | **全部删除**；台达侧用哪种高级运动承接焊缝跟踪**暂不确认** |
| `MotionConfig.cs`（759 行） | **删除，暂不建新配置** |
| L2 中 6 个 Modbus 抽象方法 | **从 L2 移除**（台达无 Modbus，走 PDO/SDO） |

### R2 台达模块全面落地（21 文件）

| 层 | 目录 | 文件 |
|----|------|------|
| L2 抽象 | `IMotion/`（8） | `Type.cs` / `MontionControl.cs` / `MontionAxis.cs` / `MontionIO.cs` / `InputIO.cs` / `OutputIO.cs` / `Cylinder.cs` / `IPVTMotion.cs` / `InterpolationMontionParam.cs`（2026-09-07 删 `IOParam.cs`、移入 `Cylinder.cs`、新增 `IPVTMotion.cs`） |
| L1 原生 | `DeltaEtherCAT/Native/`（7） | `EtherCATMasterNative.cs` / `EtherCATMotionNative.cs` / `EtherCATIONative.cs` / `EtherCATAdvancedNative.cs` / `EtherCATPVTNative.cs` / `EtherCATEcam2Native.cs` / `DeltaErrorCode.cs` |
| L3 实现 | `DeltaEtherCAT/`（8） | `DeltaMontionControl.cs` / `DeltaMontionAxis.cs` / `DeltaInputIO.cs` / `DeltaOutputIO.cs` / `DeltaSlaveScanner.cs` / `DeltaMotionConfig.cs` / `DeltaAxisConfig.cs` / `DeltaIOConfig.cs`（2026-09-07 新增 IO 配置实体；配置类同步去掉单例改实例） |
| 业务层 | 模块根（5） | `MontionManager.cs`（单例聚合，持有 `MoveData`）/ `MoveControlData.cs`（实例类，持有配置）/ `AxisRegistry.cs` / `IORegistry.cs` / `CylinderRegistry.cs` |

**命名**：沿用原档 `Montion*` 拼写（对齐雷赛基线）+ `Delta*` 前缀 → `DeltaMontionControl` / `DeltaMontionAxis` / `DeltaInputIO` / `DeltaOutputIO` / `DeltaSlaveScanner`；Native 保留 `CS_ECAT_*`。

**关键实现约束**（详见 [[guides/DeltaEtherCAT-DevGuide]]）：

- `Equiv` = **工程单位/脉冲**（mm/pulse）；`ToPulse(v)=v/Equiv`、`ToUnit(p)=p*Equiv`，换算**只在 L3**。
- 初始化：`Master_Open` → `Master_Initial` → 轮询 `Check_Initial_Done`（0/1/99，超时 30s）→ 扫从站。
- 使能：先 `Set_Move_Mode(8=CSP)`，再 `Set_Svon(1)`，轮询状态字 bit2，超时 3s。
- IO **NPN 低电平有效**：`SetON()` 写 **0**、`SetOFF()` 写 **1**。
- 卡号来源：轴内统一取 `_deltaControl.CardNo` 属性（**不缓存** `_connectNo` 快照，避免初始化后失效）。

### R3 消费方全量对接

| 消费方 | 改造 |
|--------|------|
| `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` | 全量重写：删 ZMotion 依赖；私有阶段枚举改 `MotionControlPhase`（`Idle`/`Initializing`/`Ready`/`Stopping`/`Error`）；步位 `StepServoOn=10`/`StepReady=20`/`StepStopping=700`；初始化改 `MontionManager.Instance.Initialization("台达运控", ref msg)`；对外契约（`Instance`/`Start()`/`Stop(bool)`/`IsRunning`/`WeldStatus`/`StateName`）**保持不变** |
| `MainDeviceControl/DeviceControlWork.cs` | L193 `private MotionManager Motion` → `private MontionManager Motion`；L367 赋值改 `MontionManager.Instance` |
| `WeldParamControl/WeldProcess.cs` | L785 注释更新（`MotionManager` → `MontionManager`、「正运动控制器对接后」→「台达总线就绪后」）；实际计算仍委派 `MoveControlData` |
| `UIDesign/TabPage/MotionControlPage.cs` | **无需改动**（只用 `MotionControlWorkflow.Instance`） |
| `UIDesign/MainWindow/FormMain.cs` | 仅清 1 处无用 `using AdaWeldSystem.MotionControl;` |

`.csproj`：17 条旧 `<Compile Include>` → 21 条新条目；原生依赖段 `zauxdll.dll` + `ZmotionScanLaser.dll` → `EtherCAT_DLL_x64.dll`。

### R4 精简与注释精简

- 删除过程性/同义注释；`//` 仅用于复杂逻辑（如单位换算、NPN 极性）。
- 公开接口统一 `///` + `<param>`；**P/Invoke `extern` 声明豁免**（经核验本仓既有 `SensorHelper.cs` / `Program.cs` 的 `static extern` 均无 XML 注释，遵循既有约定）。
- 日志直连 `GlobalCommData.ShowLog`，**纯文本无符号**。
- 无用 using 清零（基于全仓类型索引精确检测）。

## 校验结果（2026-09-07）

无 C# 编译器，采用 Python 静态校验替代，**真编译待 Visual Studio 执行**。

| 检查项 | 结果 |
|--------|------|
| 抽象方法实现完整性（4 个 L3 类的基类链） | ✅ 全部落地 |
| 分层铁律：L2 零依赖 | ✅ 0 违规（`EtherCATMaster` 为协议枚举非厂商名，合规） |
| 分层铁律：业务层/UI 不回流 L1/L2 | ✅ 0 违规 |
| 厂商类型越界 | ✅ 仅 `MontionManager.cs:96` 一处 `new DeltaMontionControl`（唯一装配点） |
| C# 7.3 禁用语法（ADR-002） | ✅ 0 命中 |
| 无用 using（全仓类型索引） | ✅ 0 处 |
| 跨文件符号解析（消费方 → 被调方 API） | ✅ 缺失 0 |
| 正运动残留（`ZMotion\|zaux\|CamBoxTracker\|...`） | ✅ 0 |
| 日志符号（ADR-032 禁） | ✅ 0 |
| `Dispose(bool)`（ADR-001/025 禁） | ✅ 0 |

## 规范页失准订正（第 7~8 处）

[[guides/DeltaEtherCAT-DevGuide]] 相对台达 SDK 头文件存在失准，本次按 **SDK 真名**落地：

| # | 规范页写法 | SDK 真名 |
|---|-----------|----------|
| 7 | `CS_ECAT_Slave_ECAM2_*` | `CS_ECAT_Slave_CSP_Start_ECAM2_*`（37 个） |
| 8 | Gantry / TouchProbe 名 | `CS_ECAT_Slave_CSP_Gantry_Enable` / `CS_ECAT_Slave_Motion_Set_TouchProbe_Config` |

错误码 `0x1002`：规范页注「从站初始化失败」，SDK 实为 `ERR_ECAT_MODE_CHANGE_FAILED`（**模式切换失败**），已按真值写为 `MODE_CHANGE_FAILED`。

## 遗留 OPEN

| # | 事项 | 说明 |
|---|------|------|
| 1 | **焊缝跟踪高级运动方案未定** | 用户明确「台达用哪个高级运动作为焊缝跟踪控制方法暂不确认」。候选：ECAM2（SDK 实证 24 API）/ 虚拟轴 + GearIn / PVT |
| 2 | 心跳与通信中断保护 | 正运动的 BAS 保护无台达对应；改用 PDO/SDO 轮询或 `Record_*` 族 |
| 3 | 主动/周期上报 | `BASE_REPORT`/`ON_REPORT` 无对应，待评估 |
| 4 | 台达侧配置体系 | `MotionConfig` 已删且暂不新建，轴参数/IO 映射当前如何注入待定 |
| 5 | 169 MB `EtherCAT_DLL_x64.dll` 部署策略 | 已入 `3rdDepend/`（该目录被 `.gitignore` 忽略，不入版本库）；备份体积随之增大 |
| 6 | `bin/Debug` 残留正运动 DLL | `zauxdll.dll` / `zmotion.dll` / `ZmotionScanLaser.dll` 仍在构建输出，需手工清理 |
| 7 | 真编译验证 | 本机无 C# 编译器，需 Visual Studio 打开 `AdaWeldSystem.csproj` 实测 |

## 关联

- 前置：[[decisions/ADR-032-MotionControllerDeltaReplacement]]（选型与全新模块裁定）
- 落地规范：[[guides/DeltaEtherCAT-DevGuide]]
- 模块现状：[[modules/MotionControl]]
- ⛔ 已被本 ADR 取代并整页删除：正运动控制器接入架构（原 ADR-022）、RSI-CAMBOX 硬件实时跟踪架构（原 ADR-023）、默认初始化切正运动（原 ADR-027）。三者页面已从 `decisions/` 移除，编号经 2026-09-07 全库重排后不再保留空号，映射见 [[decisions/ADR-Index]]。
