---
title: ADR-032 统一初始化状态机继承 + 整设备聚合判定
date: 2026-08-19
tags: [决策, 状态机, 初始化, 设备, 重构, 模板方法]
status: accepted
---

# ADR-032：统一初始化状态机继承 + 整设备聚合判定

## 状态
已采纳（2026-08-19）｜**已被取代（2026-09-01 治理标注）**

> **⚠️ 已被取代 —— 载体已删除**
> 本 ADR 建立的 `DeviceStateMachineBase` / `DeviceInitializationStateMachineBase` / `MainDeviceStateMachine` 三级继承体系，连同 `DeviceState.InitializationFailed = 10` 枚举，已随 `DeviceStateMachine/` 目录整体删除——见 [[decisions/ADR-041-MainDeviceControlArchitecture]]。
> - ❌ **失效**：11 态 `DeviceState` 枚举、模板方法初始化、整机聚合状态机。原历史归档页已于 2026-09-01 删除——**项目不再保留历史架构页，需要历史脉络请读本 ADR 与 [[decisions/ADR-041-MainDeviceControlArchitecture]]**。
> - ✅ **精神保留**：「任一子设备初始化失败则整设备不得宣称就绪」的聚合判定思想，由上电初始化 5 步序列承接。
> - **当前真相源**：[[architecture/DeviceControlArchitecture]]（设备态固定四态 Disconnect/Connect/Work/Alarm + 流程态分离）、[[modules/DeviceControl]]。

## 背景

设备初始化存在两类 Bug（2026-08-19 用户报告）：

1. **线激光「未连接也算初始化成功」**：`LineLaserWorkflow.InitializeWorker()` 连接后不校验 `IsConnected` 直接 `TryTransition(Standby)`；`SensorRunContinue()` 未连接时静默 return，掩盖未连接事实。
2. **整设备「无条件置就绪」**：`MainDeviceThread` 末尾无条件 `_powerOnInitialized = true`，缺失对 5 个子设备状态的聚合判定——任一子设备初始化失败时，整设备仍对外宣称就绪。

根因是旧架构中：

- `DeviceStateMachineBase` 仅做「状态容器 + 合法性校验」，5 个状态机只是定义 `ValidTransitions` 的空壳；
- 初始化编排（连接 / 读配置 / 状态信号 / 复位）散落各 Workflow 各自手工拼 `TryTransition`，**重复且易漏校验步骤**；
- 整设备无统一的聚合判定出口。

用户新增需求：「子设备的状态机其实可以使用一个状态类来继承」——用统一继承式状态基类承载初始化流转。

## 决策

1. **两层继承体系**：
   - 第一层 `DeviceStateMachineBase`：保留为纯状态容器（校验 + 安全转换 + 事件），不承载业务编排。
   - 第二层 `DeviceInitializationStateMachineBase`（新增，`DeviceStateMachine/API/`）：固化子设备初始化**模板方法** `Initialize(connect, readConfiguration, resetDevice, verifyHardwareStatus)`，顺序执行四步、全 true 方进入 `Standby`，任一 false/异常自动 `Alarm` 并中止；`null` 委托视为「该设备无需此步」直接通过。
2. **4 个子设备状态机统一继承 `DeviceInitializationStateMachineBase`**：`LaserWeldHeadStateMachine`、`LineLaserCameraStateMachine`、`MonitorCameraStateMachine`、`MotionControlStateMachine`。各 Workflow / Controller 通过**委托注入**设备特有校验逻辑，不再自行拼装流转。
3. **机器人连接态特例**：`RobotConnectionStateMachine` 使用 `Online/Offline/Error` 特例态，不参与 Standby 初始化模板 → 维持直接继承 `DeviceStateMachineBase`，不继承初始化模板（语义正确，避免强套）。
4. **新增 `DeviceState.InitializationFailed = 10`**：表征「初始化失败」终态，等待 `Resetting` 重入。（已排查全项目无对 `DeviceState` 的 switch/case 穷举，加值安全。）
5. **新增整设备聚合状态机 `MainDeviceStateMachine`**（继承 `DeviceStateMachineBase`）：承载整机聚合判定，转换规则 `Initializing→Standby/InitializationFailed`、`Standby→Working/Alarm/InitializationFailed`、`InitializationFailed→Resetting/Initializing` 等。
6. **`MainDeviceThread` 聚合判定**：移除无条件 `_powerOnInitialized = true`，改为 `EvaluateInitializationResult()`——全子设备 `Standby`→整设备 `Standby`；有失败→`InitializationFailed`；初始化中→启动 `WaitForAllReady` 轮询线程（200ms、30s 超时），超时或失败→`InitializationFailed`。`AreAllSubDevicesReady()` 中机器人未启用视为 OK。开头以 `_initializing` 防重入。

## 备选方案

- **维持各 Workflow 各自拼 TryTransition**：最小改动，但无法根治漏校验，且机器人/虚拟相机等分支仍可能漏步，放弃。
- **把机器人也强套初始化模板**：语义冲突（机器人用 Online/Offline 而非 Standby），放弃，采用特例直接继承基类。
- **整设备用 bool 标志位替代状态机**：信息量低、无法表达 `InitializationFailed` 终态与重入，放弃，采用独立 `MainDeviceStateMachine`。

## 后果

### 正面
- 「连接 + 读配置 + 状态信号 + 复位」四步校验被强制固化在基类模板，**任一子设备未连接/未就绪都无法进入 Standby**，根治线激光未连接算成功。
- 初始化编排收敛到单一模板方法，消除各 Workflow 重复拼装、漏步、静默 return 掩盖问题。
- 整设备状态由「无条件置 true」变为「聚合判定 + 失败终态 + 重入」的清晰状态机，待机流程只在全子设备 Standby 后才启动。
- 委托注入使各设备校验逻辑与公共流转解耦，后续新增子设备只需实现 4 个 `Func<bool>`。

### 负面 / 风险
- 基类 `Initialize` 的 `RunStep` 在委托抛异常时仅记日志并 `Alarm`，需在 VS 环境确认各 Workflow 的委托确实覆盖真实硬件失败路径。
- 本环境为 .NET Framework v4.8 老 csproj（`dotnet build` 不支持、`msbuild` 被安全策略拦截），**无法在本环境编译验证**，需在 Visual Studio 中编译确认（委托签名、命名空间、枚举加值）。
- 模板方法固定了四步顺序，若未来某设备需不同初始化顺序，需在模板基类扩展可选步骤或重载。

## 相关页面

- [[modules/DeviceControl]]
- [[modules/DeviceControl]]
- [[modules/Workflow]]（MainDeviceThread 聚合判定）
- [[modules/LaserWeldHead]]（LaserWeldHeadController.Initialize 委托注入）
- [[modules/LineLaserCam]]（LineLaserWorkflow.InitializeWorker 委托注入）
- [[modules/MonitorCam]]（MonitorCameraWorkflow.Initialize 委托注入）
- [[modules/MotionControl]]（MotionManager.Initialize 委托注入）
