---
title: ADR-027 默认初始化切到正运动控制器 + 删除 Null 空控制器
date: 2026-08-21
tags: [决策, V3, 运动控制, 正运动, 控制器初始化, CAMBOX, 模块清理]
status: accepted
---

> ⚠️ 历史名称提示：本页为**历史决策记录**，正文中的下列文件名为决策当时的旧名，
> 保留原文以留存上下文，现役对应如下：
>
> - `NullMotionController.cs` → 已移除（ADR-027 删除空控制器）
>

# ADR-027：默认初始化切到正运动控制器 + 删除 Null 空控制器

> **类名沿革注记（2026-09-02，ADR-034）**：本文中的 `MainDeviceThread` → `MainDeviceWorkflow` → **现为 `DeviceControlWork`**；`LaserCamBoxTrackingWorkflow` 已删除，现由 `MotionControlWorkflow` 承载 CAMBOX 启停编排；`SimulationWorkflow` 已删除，成员全部归并 `DeviceControlWork`。读取本页时请按现行类名理解，决策结论本身仍有效。

## 背景

`MotionManager.Initialize()` 原默认创建 `NullMotionController`（空实现），仅建 `Y轴`/`水平轴` 两个 `NullAxis`，不连接任何硬件、所有操作只记日志。而真正能驱动硬件的正运动控制器 `ZMotionController` 仅存在于**未被正常流程调用的** `InitializeWithZMotion(ip)` 工厂方法中。

后果：`MainDeviceThread` 初始化调 `MotionManager.Initialize()` → 得到空控制器 → 其 `DefaultController as ZMotionController` 永远为 `null` → 本应在 `[2/5] 运动控制器初始化` 阶段初始化的 CAMBOX 焊缝跟踪工作流（`LaserCamBoxTrackingWorkflow`，该工作流已于 2026-08-28 架构整合中删除，现由 `MotionControlWorkflow` 承载启停编排）因拿不到正运动句柄而**从不初始化**，CAMBOX 跟踪链路形同瘫痪。

用户要求："初始化时控制器选择需要是正运动控制器，其他不需要的控制器删除；加入 Y 轴；做 CAMBOX 跟踪工作。"

## 决策

将默认初始化链路直接切到正运动（ZMotion）控制器，并删除不再需要的空实现：

1. **`MotionManager.Initialize()` 默认初始化正运动控制器**：`connect` 回调内读取 `MotionConfigManager.Config.IpAddress`（默认 `192.168.0.11`），`new ZMotionController("正运动控制器")` → `SetIpAddress` → `RegisterController` → `zmController.Initialize()`；返回 `ZMotionController.Initialize()` 的结果供 `DeviceInitializationStateMachineBase` 决定能否进入 `Standby`。连接失败不再回退空控制器，仅记告警。
2. **删除 `NullMotionController`**：`MotionControl/NullMotionController.cs` 文件删除，并从 `.csproj` 移除 `<Compile Include="MotionControl\NullMotionController.cs" />`。其内含的 `NullMotionController` / `NullAxis` / `NullInputIO` / `NullOutputIO` 一并移除（全代码树无其他引用）。
3. **保留 `SimulationWorkflow`**：经核查其为焊接仿真子系统（虚拟相机 / 焊缝轮廓模拟，被 `FormMain` / `LineLaserWorkflow` / `MonitorCameraWorkflow` / `MotionControlPage` 实际引用），属"做模拟测试用"，按用户规则**不删除**。
   > ⛔ **本条已失效（2026-09-03）**：`SimulationWorkflow.cs` 后续**已删除**，成员（`IsEnabled`→`IsSimulationEnabled`、`Enable`→`EnableSimulation`）全部归并 `DeviceControlWork`；相关模拟模式决策亦已废弃删除。本 ADR 其余三条（默认切正运动 / 删 `NullMotionController` / Y 轴与 CAMBOX 映射不变）**继续有效**。
4. **Y 轴 / CAMBOX 从轴映射保持不变**：CAMBOX 配置 `SlaveAxisIndex=0` 即 Y 纠偏伺服从轴（已在默认轴字典 `Y轴`/axis0）；主轴为虚拟通讯编码器轴 `axis 8`（ATYPE=25，由 KUKA 机器人 EtherCAT PDO 推送 ToolRelX）。因此"加入 Y 轴 + 做 CAMBOX 跟踪"本质由"修好初始化链路"自动打通——`DefaultController` 现为正运动控制器，`MainDeviceThread` 中的 `LaserCamBoxTrackingWorkflow.Instance.Initialize(config.CamBoxTracking, config.EncoderAxis, zmController.GetHandle())` 即可正常执行。

## 备选方案

- **保留 `NullMotionController` 仅作失败兜底**：放弃。用户明确"其他不需要的控制器删除"；且空控制器会再次误导 `DefaultController as ZMotionController` 判定，是本次 Bug 根因。
- **保留 `InitializeWithZMotion` 失败回退 Null**：放弃，理由同上；`InitializeWithZMotion(ip)` 仍保留作为显式 IP 覆盖入口，仅其失败分支改为清空并记告警。
- **Y 轴重新新增独立物理轴**：放弃。Y 轴（axis0）已作为 CAMBOX 从轴存在于默认轴配置与 `ZMotionController.InitializeAxes()`，无需重复新增。

## 后果

### 正面
- 初始化控制器选择回归正运动硬件，与 V3「实时链路 100% 硬件总线化」架构（[[decisions/ADR-023-RSICamBoxTrackingArchitecture]]）一致。
- CAMBOX 跟踪工作流随正运动句柄自动初始化，V3 焊缝跟踪能力端到端可用（前提是控制器在 `192.168.0.11` 可达）。
- 代码树减少一个"永远不该被选为默认"的误导入口，消除 `DefaultController as ZMotionController` 永为 `null` 的隐式陷阱。

### 负面 / 注意
- 无正运动硬件（或 IP 不可达）时，`MotionManager.Initialize()` 失败、`IsInitialized=false`；如确需纯软件联调，需另行提供仿真/离线控制器，而非恢复 Null 空实现。
- ~~`SimulationWorkflow` 模拟子系统与运动控制器解耦，仍独立可用（虚拟相机/焊缝轮廓）。~~ → ⛔ 已于 2026-09-03 随 `SimulationWorkflow.cs` 删除失效，模拟能力现由 `DeviceControlWork` 承载（见 [[architecture/DeviceControlArchitecture]]）。

## 关联

- [[modules/MotionControl]] — 运动控制器架构与默认初始化变更说明
- [[modules/DeviceControl]] — `MainDeviceThread` 初始化入口、`LaserCamBoxTrackingWorkflow` CAMBOX 跟踪编排
- [[decisions/ADR-023-RSICamBoxTrackingArchitecture]] — V3 CAMBOX 硬件级实时跟踪架构依据
- [[decisions/ADR-022-ZMotionControllerIntegration]] — 正运动控制器对接
