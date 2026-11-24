﻿﻿﻿﻿﻿﻿﻿﻿﻿---
title: MotionControlWorkflow API 参考（台达 EtherCAT 运控 · 三态模型）
date: 2026-09-02
updated: 2026-09-22
tags: [API, 工作流, 运控, 台达, EtherCAT, RunStep, SubDeviceWeldStatus, DeviceWorkflowBase, CSP, 步骤输出, 模拟, 记录, 脉冲域, ADR-008, ADR-042, ADR-033, ADR-034, ADR-042, ADR-042, ADR-032, ADR-042, ADR-042, ADR-042, ADR-042]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs
---

# MotionControlWorkflow API 参考

> 🔄 **2026-11-23 焊前寻位：全程一条 CSP 缓冲流（最新）**：① 焊前寻位**要求 Y 轴真实移动到焊接点**——到位判据加「轴累计位移 ≥ `PreWorkSeekMinMoveMm = 0.002mm`」（目标偏离起点时），⛔ 禁止「目标≈当前位置」假到位；超时失败原因统一为「**焊前寻位失败 PREWORK** …」。② **CSP 全程连续**：`TryStartPreWorkTracking` 在 PreWork 启动即建系（`TryStartPreWorkCsp`）并**立即开始写段**，Y 边扫边跟；**⛔ 到达焊前 X 处不停启**，起焊沿走复用分支（不重建系、不收尾），仅停焊沿 `StopCspOutput` 收尾。③ **建系必须紧贴首次写缓存**（台达坐标系表闲置会失效 ⇒ 4610；原始代码是「建系→下一拍即写段」≈10ms）。④ **4610 按返回码分级降级**：`CspResult.EcatSlaveType`（4610）⇒ **Debug 级日志、不计故障、不重试、不阻断流程**（本拍不写段，下一拍按门限自然再写；挂起重试遇 4610 即作废挂起段）；**其余非 0 码仍按故障**（挂起重写，达 3 次 `Fail`）。Start 阈值始终用**成功段数**；空拍 60 拍判缓存耗尽 → 置假 → 下次写段成功后重新 `BufferStart`（不重建坐标系）。⑤ **寻位完成用独立标志** `IsPreWorkSeekReady`，⛔ 不得复用 `IsCalibrationYReady`。⑥ `StopCspOutput` 的 `BufferStop` 成功后同步清 `_cspBufferStartedOnce`（否则重复 Stop ⇒ 4352 假报错）。见 [[decisions/ADR-042-SeamTrackingConsolidated]] D5~D10 · [[decisions/ADR-114-prework-seek-position]] D7~D11。

> 🔄 **2026-11-23 自动模式 TA 入口**：新增 `bool TaExecuteAuto()`——TA 自动模式（`TaCommand.Auto`）的**流程内入口**，⛔ 不做「自动焊接中禁手动动作」门禁检查（焊前阶段属自动流程，主控派发的动作是流程组成而非手动干预）。手动入口 `TaExecute(TaCommand)` 行为不变（门禁仍生效）。见 [[decisions/ADR-100-state-union-and-action-gate]] D31 · [[decisions/ADR-038-RobotCommandDrivenStepFlow]] 三阶段章节 D5。

> 🔄 **2026-11-20 回零失败分支去 Stop**：`TryHomeAxisWithWait` 的两处失败分支（HomeAxisAndWait 失败 / WaitAxisHomed 失败）删除 `Manager.StopAxis(axis)`——回零已由 Home_Status 确认完成时再发停止会报 4866（无描述码）。见 [[lessons/HomeStatusAuthorityPitfall]]。
>
> 运控工作流（单例）：台达 EtherCAT 总线的**启停编排器**——只做设备初始化、伺服使能、停止收尾，不参与实时运动控制。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs`
> **2026-09-17（ADR-032）无轴记录模式**：模拟测试且运控未连接时 `_seamAxis == null`，`UpdateSeamTracking` **不再整体早退**——CSP 分支改调 `RecordOnlyTick()`（虚拟位置 `_simAxisPos` 平滑 + 轨迹点与工艺调整记录，**不写轴**）；`StepCspTarget` 首参由 `MontionAxis` 解耦为 `double current`。**2026-09-20 演进**：轨迹记录归口 `ProductFileRecordManager`；**2026-09-24 演进**：改由 `RecordSeamTraceYPoint`（`SeamTraceYRecord` 5 列：当前RobotX/入图RobotCSPX/CSPinYt/CSPoutY/实时Y），~~`SimTrajectoryRecorder`~~ 已删除。**2026-09-24 记录起点改 Ready 通过**：`UpdateSeamTracking` 开头每拍调 `TryStartSeamTraceYOnReady()`（`_calReturnReady && LineLaserManager.Instance.Profile.HasResult` 即一次性 `BeginSeamTraceYSession()`），生产会话开启不再立即开会话——避免会话开启到 Ready 之间记入图键与入图 Yt 全 0 的空行。
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：非泛型 `DeviceWorkflowBase`（17 项契约）→ `DeviceStateBase`；`IDisposable` 由基类实现。
> 设计依据 [[decisions/ADR-027-MotionControllerDeltaReplacement]]、ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。

> **✅ 2026-09-07 控制器换轨改造**：删除全部正运动（ZMotion）依赖（原 `CamBoxTracker` / `EncoderAxis` / `RSIPositionBuffer` / `InterpolationEngine` 及其 `Tracker` 属性），相位枚举由 `LaserCamBoxWorkflowState` 改为 **`MotionControlPhase`**，初始化改走 `MontionManager.Instance.Initialization("台达运控", ref msg)`。**对外契约（`Instance` / `Start()` / `Stop(bool)` / `IsRunning` / `WeldStatus` / `StateName`）保持不变**，UI 侧 [[api/SystemControlPage]] 无需改动。
> **✅ 2026-09-11 线激光引导接入（ADR-037）**：焊缝跟踪方案落定为 **PVT B 套流式**（相机前置 50mm，见 [[modules/LineLaserCam]]）。
> **✅ 2026-09-14 演进（ADR-008）**：`SeamTrajectoryBuilder` 已改为 `SeamTrackingAlgorithm` 并纳入 `WeldParamManager` 管理；
> 本类只负责**轨迹点缓冲区管理**与**控制器写入**（`BeginMove` / `ContinueMove`），算法计算由 [[api/WeldParamManager]] 代理。
> 本类在 `Ready` 相位周期驱动：订阅 `LineLaserManager.ResultReady`、`LineLaserWorkflow` 进入 `Working` 时 `ResetSeamTracking()` 起段并逐帧 `FeedSeamTracking`、
> `TickSeamTracking()` 保证 ≤250ms 输出一段轨迹、`SeamTrackingHasFault` 触发 `Fail`。⛔ 不再由 `LineLaserManager` 直写 PVT。
> ⚠️ 原「ECAM2 / 虚拟主轴 + GearIn」候选方案因台达无虚拟轴已排除（详见 [[guides/DeltaEtherCAT-AdvancedMotion]]）。
> 步骤驱动规范见 [[architecture/DeviceControlArchitecture]] §4（17 契约）· §5（`RunStep` 驱动）· §16（代码模板）。

> **✅ 2026-09-16 CSP 实时目标换轨（ADR-042）**：焊缝跟踪主方案由 **PVT 流式段**换轨为 **CSP 周期同步位置**；
> PVT 链路**原样保留**，由 `WeldParamManager.Instance.TrackingMode`（`CspRealtime` 默认 / `PvtStream`）分派。
> 换轨根因：PVT 点表**预下载后无法回撤**，局部修正量与机器人位姿实时变化、只能等水位排空才生效 → **结构性滞后**；
> CSP 把插补交给驱动器，上位机只给目标位置、可随时改写。详见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]。

> **✅ 2026-09-21 CSP 写入方式演进（ADR-042）**：607A 逐拍改目标实测不生效 → 改为**运动缓冲流式段写入**（`Set_Crd` → `Line_MultiAxis2` → `Start`，断流写 1 段即重启）。
> **✅ 2026-09-22 目标基准换轨（[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]）**：原 `target = axisNow + 限幅(ΔY)`（ADR-042 轴实际反馈基准）实测成为**正反馈积分器**——轴净位移 6.43mm 超 `MaxCorrectionMm` 限幅、211 次方向反转。现改为**锚点式**：`target = ClampToStroke(_cspAnchorPos + clamped)`，锚点在 `StartCspOutput()` 一次性固化（`_cspAnchorPos`），**轴反馈降级为纯观测量**；同时把**平滑基准与段距差分统一到段队列末端指令位置**（`command = StepCspTarget(_cspLastQueuedPos, …)` / `segMm = command − _cspLastQueuedPos`），消除两套基准冲突；`CspMinSegMm` 由硬编码常量改为 `WeldAlgorithmsConfig` 配置驱动（默认 0.005mm）。
>
> **✅ 2026-09-22 目标基准再换轨（[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] + [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]）**：本类 CSP 单拍闭环的**基准换算全面拆除** ——
> ① `RunCspTick` 由带参改**无参**，目标改为 `ClampToStroke(ready ? targetY : TeachLockYMm, config)`：算法 `WeldParamManager.TryGetSeamTrackingTargetY(robotX, robotY, out targetY)` 直接给**绝对 Y 轴目标**，本类**不再做「减基准再加回」折算**（该折算让基准在链路里出现两次、掩盖算法侧语义）；
> ② **`ClampCorrection` 与常量 `MaxCorrectionMm = 5.0` 一并删除**（另删孤儿字段 `_cspLastCorrectionWarnTime`）—— 幅值的真实物理边界是**机械行程**，由 `ClampToStroke(YAxisMinMm/YAxisMaxMm)` 唯一承担；突变的边界归算法层 `MaxTargetStepMm`，职责单一无冗余护栏；
> ③ 新增 `DefaultAxisEquivMm = 0.001` / `AxisEquivMm`（取 `_seamAxis.Equiv`，轴未连接或当量非法时回缺省，保证不除零）/ `ToPulseMm()`（`(int)(mm / Equiv)`，与驱动器 `ToPulse` **同口径截断**），~~段距判定改为 `Math.Abs(segMm) < Math.Max(config.CspMinSegMm, AxisEquivMm)`（**防零位移段塞满缓冲**）~~ ⚠️ **2026-09-22 末次演进**：段距判据已**硬编为单脉冲当量 `minSegMm = AxisEquivMm`**（`QueueCspSegment`），不再引用 `config.CspMinSegMm`（后者降级为 INI/界面留痕项，见 [[modules/WeldParamControl]] 2026-09-23 标注与 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]）；诊断日志补 `commandPulse` 字段；
> ④ **`_cspAnchorPos` / `_simAnchorPos` 删除**：`StartCspOutput` 只置 `_cspLastQueuedPos`，无轴记录模式改以 `_simAxisPos` 为平滑基准、目标与有轴同源；
> ⑤ 相机回调喂帧改传**测量时刻轴实际值**：`WeldParamManager.Instance.OnSeamLaserResult(e.Result, _seamAxis.GetPosition())`（ADR-042 遗漏的轴位置通路在 ADR-042 补齐）。
>
> **✅ 2026-09-16 CSP 输出并入流程步骤（ADR-042，同日二次裁定）**：CSP 目标写入**不再由独立 1ms 线程承担**，
> 改为**由 `FlowProcess` 的 CSP 分支按拍推进**（`#region CSP 步骤输出`）——起焊启用 → 逐拍写入 → 报警处置 → 停焊收口
> 全部落在同一执行步序列内，消除模组工作流**自起线程**与本工作流 `case` 内 `while`/`Sleep` 两处契约违规
> （红线见 [[architecture/DeviceControlArchitecture]] §5）。节拍改为随流程（运行态 10ms/100Hz），限幅器按**实测 dt** 折算；
> `SEAM_GUIDE/CYCLE_TIME_MS` 配置项删除。详见 ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。

---

## 定位

- **运控编排归本类**：台达总线的打开/初始化/关闭、全体轴伺服使能、急停下发，统一由本类编排；实时跟随由硬件总线完成。
- **不产出设备数据**（[[decisions/ADR-016-WorkflowResponsibilityBoundary]]）：轴/IO/气缸对象由 [[api/MontionManager]] 持有与注册，本类只调用其批量接口。
- **厂商隔离**：本类不出现任何 `Delta*` 类型——台达装配发生在 `MontionManager.Initialization()` 内（唯一装配点）。
- 差异化职责（原档 R011）：**检测送丝位置和焊接质量阈值**——`SubDeviceLog()` 内 `// todo`，待硬件点位明确后落地。

---

## 公共成员

| 成员 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static MotionControlWorkflow` | `Lazy<T>` 单例 |
| `StateName` | `override string` | 对外名片名，返回 `Tag`（日志/事件标识） |
| `IsRunning` | `bool` | 是否处于 `Ready` 相位 |
| `IsInitialized` | `bool` | 台达总线是否初始化成功 |
| `IsCalibrationYReady` | `bool` | **2026-09-21 新增（ADR-042）**：焊缝跟踪轴是否已停在 Y 轴标定位（PreWork 回归完成），供观测与起焊防呆 |
| `IsEnabled` / `IsHomed` / `IsAtWorkZero` | `bool` | **ADR-098**：Y 轴分层就绪——`IsEnabled=YReady`；绝对编码器免回零，使能即 `IsHomed`；距标定位 ≤0.02 mm 为 `IsAtWorkZero` |
| `ReadinessStage` / `MinReadinessStage` | `ReadinessStage` | **ADR-098**：L0 已连接 / L1 已使能 / L3 已回零（Y 免回零直达）/ L4 已到工作零位；运控最低门槛 L3 |
| `ReadinessReason` / `WorkZeroSource` | `string` | **ADR-098**：不可用原因取 `YGateReason`；工作零位来源 = `TeachLockYMm`（标定位即工作零位） |
| `State` / `WeldStatus` | 基类属性 | 连接态（`SubDeviceState`）/ 焊接过程态（`SubDeviceWeldStatus`） |
| `RunStep` / `StepWorkTime` / `WorkStepName` / `StepStatusText` | 基类属性 | 执行步 / 步骤用时 / 步中文名 / 可观测摘要 |
| `ConfigFileName` | `protected override string` | `"MotionControlWorkflow"`，配置落在 `Config/MotionControl/Workflow_XML/` 下 |
| `TryManualAxisOperation` | `bool (string[] roleKeys, AxisManualOperation op, double value, ushort dir, out string axisName, out bool servoOn, out bool commandOk, out string rejectReason)` | **2026-11-08 迁入（ADR-093 决策七）**：UI 手动轴操作唯一入口；门禁 = 已初始化 + 角色轴已装配，其余保护在 Manager 基础指令与轴类内 |
| `TryHomeAxisWithWait` | `bool (string[] roleKeys, string actionName, out string axisName, out string rejectCode, out string rejectDetail, out string evidence)` | **2026-11-08 新增（决策八）**：UI 回零动作唯一入口；门禁顺序 已初始化 → 角色轴已装配 → `GetAxisGateReason` → `TryBeginAxisInstruction` → 下发 + `WaitAxisHomed` + 单飞释放 |
| `TryMoveAxisToTarget` | `bool (string[] roleKeys, double targetMm, string actionName, out string axisName, out string rejectCode, out string rejectDetail, out string evidence)` | **2026-11-08 新增（决策八）**：UI 绝对移动动作唯一入口；同上门禁，下发后 `WaitAxisAtTarget`（5s），超时/异常走 `mgr.StopAxis` + `NOT_REACHED` |
| `RunTaZeroPoseAfterInit` | `bool ()` | **2026-11-08 自 `MontionManager` 迁入（决策八）**：直接委托 `ExecuteTaZeroPose()`；**2026-11-10 起删去本方法内的初始化闸门与 `TaMotionReady` 判定**（与 `CheckTaMotionReady` 重复） |
| `AxisReject*`（6 常量） | `const string` | **2026-11-08 新增**：`NOT_INITIALIZED` / `AXIS_NOT_ASSIGNED` / `AXIS_NOT_READY` / `BUSY` / `COMMAND_FAILED` / `NOT_REACHED`；UI 按码分支还原文案，⛔ 不再自判门禁 |
| `ExitTaTorque` / `SetTaTorqueMode` / `SetTaTorque` / `StopTaTorque` | `bool (…)` | **2026-11-09 自 `MontionManager` 迁入**：TA 角色级力矩动作（原 `SetWireFeedTorque*` 更名 —— **送丝即 TA，无第三个轴**），⛔ Manager 不再持有 TA 角色语义 |
| `BuildMachineInitSummary` / `LogAxisGateReport` | `string ()` / `void ()` | **2026-11-09 自 `MontionManager` 迁入**：整机初始化叙述归流程层；Manager 只提供原始状态快照 |
| `TaZeroPoseStageChanged` + `IsTaZeroPoseRunning` / `Attempted` / `Done` / `Failed` | `event Action` + 4 个 `bool` | **2026-11-09 自 `MontionManager` 迁入（ADR-094 D1）**：UI 四态上色唯一来源；`ProcessControlPage` 订阅本类事件 |

---

## ~~相位枚举 `MotionControlPhase`~~ ⚠️ 已被 [[decisions/ADR-055-SubFlowStateEliminationAndParamClassRelocation]] 整个删除（2026-10-10 沿革补标）

> ⚠️ **本节为历史沿革**：`MotionControlPhase` 枚举、`_phase` 字段与 `SetPhase`/`MapWeldStatus` 中间层
> 已于 2026-10-09 ADR-055 **整个删除**（⛔ 不是降私有），状态只剩基类 `WeldStatus` 单源；
> `SetPhase` 的步号副作用改由私有 `EnterWeldStatus(status, reason, enterServoStep)` 承载。
> 下表仅作历史对照，**不得据本节改码**。

历史（已删）：`_phase`（默认 `Idle`）驱动 `FlowProcess` 与可观测性，对外经 `SetWeldStatus(MapWeldStatus(phase))` 映射：

| 取值（已删） | 含义 | 映射 `SubDeviceWeldStatus` | 执行步复位 |
|---|---|---|---|
| `Idle` | 空闲（初始化完成或未启动） | `Standby` | `StepIdle` |
| `Initializing` | 正在打开并初始化台达总线 | `PreWork` | `StepIdle` |
| `Ready` | 已受理启动指令，等待伺服使能完成（含 PreWork 标定位回归） | `Standby` | `StepServoOn`(10) |
| `Stopping` | 停止中（伺服下使能） | `Stopping` | `StepStopping`(700) |
| `Error` | 初始化失败或流程异常 | `ErrorAborted` | `StepIdle` |

> 历史语义（已删）：`SetPhase()` 三件事——写 `_phase` → 映射 `WeldStatus` → 把 `RunStep` 复位到该阶段入口步。
> 现行等价物 = `EnterWeldStatus(...)`（`SetWeldStatus` + 步号复位副作用保留）。

---

## 执行步段

| 步号 | 常量 | 动作 | 推进 |
|---|---|---|---|
| 10 | `StepServoOn` | `DoServoOn()`：小步 11 **先复位报警再使能 Y 向焊缝跟踪轴**（`ResetAlarm()` → `ServoOn()`；模拟取 `GetAxis(SeamTrackAxisName)`，真实取 `_seamAxis`）——⚠️ 顺序不可颠倒：上一场残留报警会让直接使能被拒不生效、随后点位指令也不响应（2026-09-24 实测二跑 15s 超时，手动点「清理报警」后即可）。小步 12 使能完成后、**移动前**再调 `ResetSeamAxisBufferBeforeMove()`（清残留缓冲与坐标系）。2026-09-24 业主口径：运控只负责 Y 向轴，⛔ 不再调 `ServoOnAll()`——实测全轴操作会打到送丝力矩电机并报错误码 256。`ServoOnTimeoutSeconds = 10` 超时 → `Fail()` | → 15 |
| 15 | `StepReturnToCal` | `DoReturnToCalibration()`（**2026-09-21 ADR-042 新增**）：PreWork 把焊缝跟踪轴回归 **Y 轴标定位**（`TeachLockYMm`）。**2026-09-24 业主口径改四步小步流（Y 轴为 CSP 运动模式，[[decisions/ADR-044-SeamEndSemanticsAndMotionAxisScope]]）**：小步 21 判位与下发——先 `ConfigureSoftTargetReachWindow()` 配置 **CSP 族软到位窗口**（台达手册 9.1.12：`PositionWindow` = 脈波數，取 `CalReturnToleranceMm / AxisEquivMm` = 20 脈波；`WindowTime` = 條件成立次數），再 `AbsMoveNoBlock(calY)`（已在位跳过、无跟踪轴直接放行）→ 小步 22 **等轴运动停止**（`IsMoving()` 翻假）。⚠️ **根因 2026-09-24 定位为「判据取反」**：台达 `Motion_Get_Mdone` 在 CSP 下是**多值状态机**（手册 8.12 / P8-18：`0`=靜止 / `1`=加速中 / `2`=常態速度 / `3`=減速中 / `5`=通訊中），**「運動中」= `Mdone != 0`**；旧实现按雷赛语义写 `Mdone == 0` ⇒ 指令下发（`Mdone=1`）被判「已停止」而当拍跳位置判定、反复重发（日志 L10→L11），本位静止（`0`）反被判「仍在運動」而等停 15s 超时（日志 L40）。已修正 `IsMoving()`；**两段判**（`_calMotionStarted`：先等「运动已启动」再等「已停止」）保留为防「下发到启动」空窗的双保险，超时未见启动则转小步 23 按位置判定并记 Warning；超时 `CalReturnTimeoutSeconds = 15s` **每次下发后重新计时**（局部起点 `_calStopWaitStart`）→ `Fail` 报「运动停止超时」→ 小步 23 **判到位偏差**（≤ `CalReturnToleranceMm = 0.02`（原 0.05）即完成并置 `_calReturnReady`，同时读 `GetSoftTargetReachStatus()` 留痕——手册 9.1.13：`0` = 未到達窗口 / `1` = 到達；未到位则**重发移动指令**重试，`_calRetryCount` 超 `CalReturnMaxRetry = 3` 次 → `Fail` 报「未到位且重试已超限」）；**全程非阻塞按拍推进**（⛔ 禁 while/Sleep，ADR-042），重试计数在小步 11（伺服使能下发）复位。**2026-09-24 移动门禁换口径**：下发移动只判「标定目标与轴当前位置是否都在 Y 轴行程上下限 `[YAxisMinMm, YAxisMaxMm]` 内」（`IsWithinYStroke`）——在限内即放行、多远都移动，**不再以固定距离作移动门槛**；任一端越界即 `Fail` 报「Y 轴回归标定位越界」。**2026-09-28 真机实测补正**：小步 22 前半段（`!_calMotionStarted`）追加**位置优先短路**——「轴已静止（`!IsMoving()`）**且** `|TeachLockYMm − 轴位| ≤ CalReturnToleranceMm`」即直接转小步 23 复核（Info 日志「已静止且在标定位容差内 转到位判定」），消除「重发为空动作 ⇒ `IsMoving()` 恒假 ⇒ 空等 15s 兜底」的回标定位 15s 阻塞；⛔ 仍以「已静止」为前置（不代替运动停止判定），短路分支不置 `_calReturnReady`（到位结论仍由小步 23 单一给出） | → 20 |
| 13 | `StepPreWorkSeek` | **焊前寻位（2026-11-23 新增，[[decisions/ADR-114-prework-seek-position]]）**：`DoPreWorkSeek()`——寻位方式与焊接工作模式一致（提前扫后跟踪）：首次进入起计时并调 `UpdateSeamTracking()` 驱动跟踪（此时 `TryStartPreWorkTracking` 建系 + `BeginSeamTrackingForPreWork` 激活地图跟踪，**⛔ 不开缺值量测**）；**完成判据 = X 到位（`DeviceControlWork.IsPreWorkXArrived`：真实＝当前 X 与 `RX_PRE_WELD_POSE` 记录的焊前位 X 差 ≤5mm，模拟＝已到设定点）且 Y 到位**（取 `TryGetSeamTrackingTargetY` 目标，轴反馈偏差 ≤`PreWorkSeekToleranceMm=0.1`）；两者满足即置 `_calReturnReady`（语义由「标定位就绪」变为「寻位就绪」）完成；超时 `PreWorkSeekTimeoutSeconds=60s` 即 `Fail` 报「焊前寻位超时」→ PreWork 失败报警停焊 | → 20 |
| 20 | `StepReady` | 已使能待机：调 `UpdateSeamTracking()` 逐拍驱动焊缝跟踪。**CSP 模式（默认）**：起焊沿 `ResetTrackingForWeldStart()`（⚠️ 2026-09-23 ADR-043 换轨，原 `ResetSeamTracking()`——起焊沿只清跟踪 PVT+地图、不清工艺调整，工艺调整的会话清空移至焊前检查播种之前） → `BeginSeamTrackingCorrection()` → 速度归零 → `StartCspOutput()`；运行中每拍 `OutputCspTick()`（门控 → 读**绝对目标** `TryGetSeamTrackingTargetY` → `RunCspTick` 单拍闭环：行程限幅 → 三段整形 → **段距护栏** → `QueueCspSegment` 写段）；报警拍先 `Fail()` 并 return、该拍不写段；停焊沿 `StopCspOutput()`。**PVT 模式**：原逻辑不变——`ResetTrackingForWeldStart`/`DrainSeamTracking`、`TickSeamTracking` 强制输出、`SeamTrackingHasFault` → `Fail` | — |
| 700 | `StepStopping` | `DoStopping()` **两阶段收尾**（2026-09-24）：首次进入只 `StopSeamTrackingOutput()`（`StopCspOutput()` + `FlushSeamBuffer(true)` + 复位跟踪态与报警标志）+ 置 `_stopTeardownStarted`；随后**按拍等轴停稳**（`IsSeamAxisSettled()`：无轴 / `!IsMoving()` / `!IsServoOn()` 放行，超时 `StoppingSettleSeconds = 5s`）——未停稳即 `return false` 由 `FlowProcess` 下一拍重入（⛔ 禁 while/Sleep）；停稳后 `ResetSeamAxisBufferBeforeMove()`（**仅 `_cspBufferStartedOnce` 时清**，未建系则跳过并记日志，避免 4352）→ 复位 `_calSubStep/_calReturnReady/_seamTraceYReadyStarted` → `ShutdownSeamAxis()`（**按需**：无报警保持使能直接回初始状态；检出报警才 `ServoOff()` → `ResetAlarm()` → `ServoOn()`）→ `SetPhase(Idle)`。⚠️ 为何必须等停稳：`BufferStop(Smooth)` 是**异步减速停**，紧跟清空必报 **4359 = `ERR_ECAT_NEED_STOP`（0x1107 需要先停止）**、紧跟下电会让驱动器报伺服类报警 ⇒ 二次启动使能不上、标定位回归 15s 超时 | → `StepIdle` |
| 900 | `StepFinishFail` | `DoFinishFail()`：**2026-09-24 与步 700 同构的两阶段收尾**——首次进入 `StopSeamTrackingOutput()` + 置 `_failTeardownStarted`；按拍等轴停稳（`IsSeamAxisSettled()`，超时 5s）→ `ResetSeamAxisBufferBeforeMove()`（同上，`_cspBufferStartedOnce` 门控）→ 复位 `_calSubStep/_calReturnReady/_seamTraceYReadyStarted` → `ShutdownSeamAxis()`（按需：无报警不动伺服，检出报警才清报警并重新失能/使能）→ `SetPhase(Error)` + `IsAlarm = true`；异常终止后轴可再次启动 | → `StepIdle` |

> 步段位沿用 [[architecture/DeviceControlArchitecture]] §5 约定（10/20 业务段 · 700 停止 · 900 失败收尾）。

---

## 主要方法

| 方法 | 说明 |
|---|---|
| `Start()` | 受理启动指令：未初始化则记 Warning 返回 false；否则置 `Ready` 相位（执行步复位到 10）。**只受理不阻塞** |
| `Stop(bool immediate = false)` | 受理停止指令：`immediate=true` 先下发 `MontionManager.Instance.SetEmergencyStop(true)`；`Idle`/`Error` 相位直接返回；否则置 `Stopping` |
| `FlowProcess()` | 每拍由 `DeviceControlWork` 模组线程驱动；`IsEnable` 门控后按 `RunStep` 分派 |
| `ResetProcess()` | 解除急停（`SetEmergencyStop(false)`）、清 `_servoOnIssued`、回 `Idle` 并置 `Standby` |
| `ClearSeamAlarm()` | **2026-09-22 ADR-042 新增**：清除焊缝跟踪折返报警——清 `_seamAlarmPending` 待处置标志 + 经 `WeldParamManager.Instance.ClearSeamTrackingAlarm()` 转发清算法侧 `_hasAlarm`。**会话切换与异常清理必调**：残留标志会让下一会话首拍即被 `CspTick` 的报警分支拦截（`if (_seamAlarmPending) { …; Fail(…); return; }`），表现为「启动就报警、清不掉」 |
| `ClearStatus()` | 清报警/失败原因/`_servoOnIssued`，**直接置 `_phase` 不经映射**，`WeldStatus` 强制 `NoReset` |
| `ResetWorkTime()` | 调基类 `ResetStepTime()`，防止停止期时间计入步骤时长导致误超时 |
| `InitializeOn()` | 阻塞初始化：调 `MontionManager.Instance.Initialization("台达运控", ref msg)`；失败置 `Error` + `Disconnected`，成功置 `Idle` + `Connected` + `NoReset`（等待复位）并 `AttachSeamTrackAxis()` 装配焊缝跟踪 |
| `ConnectOff()` | 阻塞断开：关闭台达总线，调用方阻塞至完成 |
| `WeldStatusTrans()` | **2026-10-10 ADR-061 修复后形状**：`NoReset` return；`Stopping` ⇒ `StopSeamTrackingOutput()` + `EnterWeldStatus(Stopping,…)`（进 StepStopping，**ADR-042 停焊沿确定性入口**）；`ManualStopped/ErrorAborted` ⇒ `StopSeamTrackingOutput()` + `EnterWeldStatus(Standby,…)`。⚠️ 曾为恒假条件 `WeldStatus==Stopping && WeldStatus!=Stopping`（ADR-055 删 `_phase` 后的机械改写残留，分支永不执行）；触发点 = `CascadeWeldStatus()` 末尾 |
| `SubDeviceLog()` | 输出「运控 连接态 / 焊接过程态 / 步骤 / 已初始化」4 项。⚠️ 2026-10-10 修复：格式串曾 5 占位符 4 实参（调用即 `FormatException`），并删 ADR-055 后陈旧的「相位」标签；契约零调用方状态维持（原 rules/KR-011（已并入 lessons/StaticVerifier-Wiring-Integrity） 可观测性契约不删） |

### 判断辅助属性（2026-09-22 精简）

> 把散落在方法内的重复判断收敛为具名私有属性（ADR-007 ②/④：调用处不再重复写同一套判定），语义单一、无副作用：

| 属性 | 说明 |
|---|---|
| `IsSimulation` | 是否已启用模拟模式（替换 8 处直接读 `DeviceControlWork.Instance.IsSimulationEnabled`） |
| `IsSimRecordOnly` | 模拟且不驱动实轴（无轴仍须采样记录，用于 `UpdateSeamTracking` 早退判据） |
| `SeamAxisPosMm` | **2026-09-22 新增**：闭环基准位置（毫米）——有轴取 `_seamAxis.GetPosition()`、无轴记录模式取虚拟轴 `_simAxisPos`；把「测量时刻轴值 Ya1」（ADR-042）的取数集中到一处，使两种模式喂入同构、消除 `_seamAxis == null` 三元散写（ADR-032 决 6 回归修复，见陷阱十九） |
| `SeamTrackAxisName` / `HasSeamTrackAxis` | 跟踪轴名 / 是否已装配（替换 3 处跨模块读取与轴存在性判断） |
| `IsSeamWelding` / `IsCspMode` | 线激光是否处于 `Working` / 是否 CSP 实时目标模式（替换 `UpdateSeamTracking` 局部变量与 `OnSeamResultReady`、`OnSeamTrackingStart` 的重复判断） |

### 焊缝跟踪装配（ADR-037 / ADR-008）

| 方法 | 说明 |
|---|---|
| `AttachSeamTrackAxis()` | 按私有属性 `SeamTrackAxisName`（运控配置，2026-09-20 ADR-033 已迁出线激光）取轴——`MontionManager.GetDeltaAxis` 直接下发台达轴具体类型，流程层**不再自行 `as` 转型**（2026-09-22 精简）→ 订阅 `LineLaserManager.ResultReady`；未找到轴只记 Warning 不影响初始化（**2026-09-14：不再 push 配置**，线激光引导配置由 `WeldParamManager` 自持自载） |
| `OnSeamResultReady()` | 相机 SDK 回调线程：**仅此处是算法地图的唯一喂入点**（全库 1 个调用方）。三条早退：`!_seamTrackingActive && !_cspPreWorkTracking` → return；`_seamAxis == null && !IsSimRecordOnly` → return；`_seamAxis == null && !IsCspMode` → return（PVT 点下发依赖实轴，无轴静默以避空引用）。随后**按模式分派**——CSP → `WeldParamManager.Instance.OnSeamLaserResult(result, SeamAxisPosMm)` 后 **return**（不产 PVT 点）；PVT → `FeedSeamTracking(..., SeamAxisPosMm)` 并把返回点加入 `_seamBuffer`（ADR-042）。**2026-09-22 修复**：判轴早退原为无条件 `_seamAxis == null` → 无轴记录模式永不喂入、地图恒空；现放宽为「无轴且（模拟记录 + CSP）」才继续，以虚拟轴位置顶替 Ya1。**2026-11-23 修复**：喂帧早退原为只看 `!_seamTrackingActive`（它是**起焊沿开关**，PreWork 阶段为 false）⇒ PreWork 每帧被丢 ⇒ 地图恒空、焊前寻位 60s 超时；现加 `&& !_cspPreWorkTracking`（PreWork 跟踪已建立时同样放行帧） |
| `UpdateSeamTracking()` | 设备流程线程：Working 起止沿按模式走 CSP/PVT 分支（见上表行 20）；**CSP 分支**——若 `_seamAlarmPending` 则 `Fail(...)` 并 return（该拍不写目标），否则按轴有无分派：有轴 `OutputCspTick()`、无轴 `RecordOnlyTick()`（ADR-042/ADR-032）；**无轴记录模式（ADR-032）**：模拟中且运控未连接（`_seamAxis == null && ShouldMoveAxis == false`）时**不再整体早退**，起焊沿以虚拟位置 `_simAxisPos` 播种、停焊沿 `SimTrajectoryRecorder.FlushToFile()` 落盘。**2026-09-22 补两道门槛**（缺任一则地图恒空、`RecordOnlyTick` 取不到目标）：① 喂入通路见 `OnSeamResultReady`；② `OnSeamTrackingStart` 内 `BeginSeamTrackingCorrection()` 须**先于** `if (!cspMode || _seamAxis == null) return;` 执行——算法 `_isTracking` 门禁不放开，位姿与特征帧会被整帧丢弃 |
| `TryFlushSeamBuffer(isFinal)` | 按 `RemainBufferSize` 水位与节拍条件触发 `FlushSeamBuffer`（**PVT 模式专用**） |
| `FlushSeamBuffer(isFinal)` | 把 `_seamBuffer` 中 PVT 点通过 `BeginMove` / `ContinueMove` 写入 `_seamAxis`（**PVT 模式专用**） |
| `DetachSeamTrackAxis()` | 退订结果、`StopCspOutput()`、`FlushSeamBuffer(true)` 收尾、清空缓冲区、复位状态（`InitializeOff` / `DisposeManaged` 调用） |

### CSP 缓冲流式输出（ADR-042 → ADR-042，`#region CSP 步骤输出`）

> ⛔ **2026-09-21 ADR-042 演进**：~~607A 逐拍改目标（`SetCspTargetPosition` / `CSP_Start_Move`）~~ **实测写入不生效，废止**；现行 = 台达**运动缓冲流式段写入**——`Set_Crd_Parameters` 建坐标系 → `Line_MultiAxis2` 逐段写入 → `MotionBuffer_Start` 启动；动作 = 一直写 buffer，缓冲段被消耗完即停，须重写段后再 Start。

CSP 段写入**就地落在 `FlowProcess` 的 CSP 分支内按拍推进**，**不自起线程**（原 1ms 后台线程 `CspOutputLoop()` 已删除）：

| 成员 | 说明 |
|---|---|
| `StartCspOutput()` | 起焊沿**启用**：`TimeBeginPeriod(1)` 提频 → `_seamAxis.StartCrdBuffer(MaxVel, MaxAcc)` 建单轴坐标系（TableNo=0、**SetOriginFlag=0 不设原点**——首跑实测设原点会使绝对目标再叠加起点偏移导致轴跑飞；**S 曲线取轴配置 STime**——2026-09-29 曾改常量 10ms 不读配置，A/B 复测与 S_TIME=0 效果基本一致、过冲/锯齿另有成因，当日回退配置驱动，见 ADR-042 §2.8 演进）→ 复位段队列状态 → `_cspLastQueuedPos = axis.GetPosition()`（**2026-09-22 ADR-042 起不再固化起焊锚点** —— `_cspAnchorPos` 已删除，闭环基准归到算法侧「测量时刻轴值 Ya1」）；记日志「缓冲闭环输出已启用 轴起点 标定位 预载 N 段」；**防呆（ADR-042）**：轴起点与 Y 轴标定位 `TeachLockYMm` 偏差 >5mm 打 Warning（提示起焊前轴未停在标定位、标定对不成立）。**2026-09-22 ADR-042 建系容错**：建系失败不再直接放弃——先 `BufferStop(Smooth)` + `BufferClear()` 收尾，**再重试一次**（上一会话异常终止时残留的坐标系/缓冲会让本次建系失败，实测错误码 **4627**），仍失败才记 Error 不输出并打 Warning「缓冲坐标系已清残留后重建成功」 |
| `TryStartPreWorkTracking()` | **PreWork 起跟踪（2026-11-23）**：判据 = `_calReturnReady`（Y 轴已到标定位）+ `LineLaserManager.Instance.Profile.HasResult`（线激光已有数据）⇒ `BuildCspCoordinateSystem` 建系 + `WeldParamManager.BeginSeamTrackingForPreWork()` 激活地图跟踪（⛔ **不开缺值量测**，PreWork 引导未稳，量测开启必误累计触发 NoValueAlarm）+ 置 `_cspOutputRunning`/`_cspPreWorkTracking`。PreWork 期间 `UpdateSeamTracking` 在 `StepReady` 阶段即驱动 `OutputCspTick()`，无引导则目标恒标定位、不写段 ⇒ 不触发建系未就绪的写段失败 |
| `BuildCspCoordinateSystem(config)` | 建系唯一入口（2026-11-23 自 `StartCspOutput` 抽出，供 PreWork 与写段重试共用）：`StartCrdBuffer` 失败 ⇒ `BufferStop(Mode1)` 收尾（+ Stop 失败才 `BufferClear`）后重试一次，仍失败记 Error 返回 false（4627 残留口径不变） |
| `StopCspOutput()` | 清启用/缓冲标志 → `TimeEndPeriod(1)` 配对归还定时器精度 → **仅 `_cspBufferStartedOnce` 时** `BufferStop(BufferStopModeSmooth = 1)`（**Mode 1 = 平滑停止：控制器清除 FIFO 並解除座標系**，手册 9.7.16）→ **Stop 成功即视为收尾完成，不再追加 `BufferClear()`**（旧实现传 Mode 0＝Feedhold 暂停、什么都没清，再调 Clear 必被拒——现场「每次清空失败报警」的由来；仅当 Stop 自身失败才兜底 Clear 并计入失败计数）→ 复位平滑速度与错误码。**2026-11-23 增**：清挂起段 `_cspPendingSegCommand`（未入 FIFO，写了会串场）+ 复位 `_cspWriteFailCount` / `_cspPreWorkTracking` |
| `OutputCspTick()` | **单拍门控（2026-09-22 精简）**：`_cspOutputRunning` 门控 → 急停判据（置位即 `StopCspOutput()` 并记 Warning）→ 读**绝对目标** `TryGetSeamTrackingTargetY(robotX, robotY, out targetY)`（ADR-042），就绪即交 `RunCspTick()`（**已无参**）；**未就绪**输出限频 Debug 行（区分「未置位跟踪」与「目标恒 0」）。轴非空由调用方 `CspTick` 保证，本方法不再重复判空 |
| `RunCspTick()` | **单拍闭环（ADR-042 锚点式 → ADR-042/049 直取绝对目标，方法已无参）**：~~基准 = 轴实际反馈~~ ~~基准 = 起焊锚点 `_cspAnchorPos`~~ → 现为 **取算法绝对目标** `TryGetSeamTrackingTargetY(robotX, robotY, out targetY)`（`ready=false` = 前置量段内尚无地图点 → 回落 `TeachLockYMm`，而轴本就被 PreWork 回归该位，故首段零跳变）：`target = ClampToStroke(ready ? targetY : TeachLockYMm, config)`（**绝对量直传**，本类不做任何基准换算、无幅值截断）；`command = StepCspTarget(target, 实测节拍)`（**ADR-042 起二参**，跟随器位置 `_cspFollowPos` 由本方法内部持有并每拍推进）、`segMm = command − _cspLastQueuedPos` → **平滑基准与段距差分统一到段队列末端指令位置**（保证上段末端即下段开端；原「目标基准用 `axisNow`、差分用 `_cspLastQueuedPos`」两套基准冲突是 211 次方向反转的成因）→ `QueueCspSegment(...)` 写段 → 未运行且攒够阈值（首启 10 段 / 耗尽重启 1 段）即 `BufferStart`（**写段成功后不再回写 `_cspLastQueuedPos = axisNow`**）→ **ADR-042 起每拍 `_cspTickCount++` + `RecordCspPoint(command, axisNow)` 逐拍记录**（原「写段分支内记录 + 100ms 静止补记」两处已删）→ 限频诊断（5s 缓冲诊断 + 500ms 两行 Debug）；`axisNow = _seamAxis.GetPosition()` **降级为纯观测量**（仅入 Debug 行）。整段 try/catch 记「缓冲输出异常」。**2026-11-16**：查图 `robotX` 改取 `WeldParamManager.Instance.CurrentRobotX`，与入图键同源（原取 `GetEffectiveRobotX()`，真实模式恒 0 ⇒ 查图无点、回落标定值）；保留 `_cspQueryXFromWeldParam` 静态开关可回退 |
| `QueueCspSegment(command, segMm, config, axisNowMm)` | **写段或静止处置**（2026-09-29 起增第四参 `axisNowMm`：队列积压反馈输入）。**2026-11-23 增写段失败处置**：写段返回非 0（4610 = `ERR_ECAT_SLAVE_TYPE`「此模块不支持此 API」，多为台达侧状态未就绪）⇒ **不推进** `_cspLastQueuedPos` / 段计数（原实现无条件推进 ⇒ 软件账本与 FIFO 账实不符），段**挂起**待延时 `CspWriteRetryDelaySeconds = 0.05s` **跨拍**重写（⛔ 同拍立即重试无效，状态不会因同拍就绪）；连续失败达 `CspWriteFailMaxRetry = 3` ⇒ `Fail()` 报警停焊暴露原因；会话收尾清挂起段。**写段判据 2026-09-29 改双门限**：段距 ≥ `max(CspMinWriteSegMm, 单脉冲半值)` **OR**（距上次写段 ≥ `CspWriteIntervalMaxSeconds=0.15s` 且已攒够 1 个整脉冲）——防止低速下写段间隔被拉长到时基上限 0.25s 之外致段速高估、轴停走（ADR-042 起去掉 `tickSeconds` 形参）：段距 ≥ **单脉冲当量 `AxisEquivMm`（ADR-042 硬编）**（⛔ ~~`Math.Max(config.CspMinSegMm, AxisEquivMm)`~~：现场 INI 的 `CSP_MIN_SEG_MM=0.005` 覆盖代码默认值，会把写段节拍由 100Hz 砍到约 44Hz、实测占空比仅 **7~8%** ⇒ 轴停走；`CspMinSegMm` 自此**退出运控侧判定**，仅保留 INI 键与界面控件兼容。`mm→脉冲` 为**截断取整**，不足 1 脉冲会写入零位移段并塞满缓冲） 时按 **自上次写段的实测间隔** 折算速度（`_cspLastSegTimestamp`，钳 `[CspMinTickSeconds, CspMaxSegSeconds]`、上限钳 `MaxVelMmPerS`、下限保底 `AxisEquivMm`）调 `BufferLineTo(command, vel, vel, MaxAcc)` 写段、清零空闲拍（**轨迹记录已移出本方法，改由 `RunCspTick` 逐拍记录**）；否则累计静止拍，达 `BufferIdleTicksToDrain` 置 `_cspBufferRunning=false`（⛔ 原 `BufferIdleRecordIntervalMs` 静止补记已删） |
| `ClampToStroke(value, config)` | 按 `YAxisMin/Max` 行程限幅（静态方法） |
| ~~`ClampCorrection(ΔY)`~~ | ⛔ **2026-09-22 ADR-042 删除**：幅值的真实物理边界是**机械行程**（`ClampToStroke` 唯一承担），突变的边界在算法层 `MaxTargetStepMm`；连带删除常量 `MaxCorrectionMm = 5.0` 与孤儿字段 `_cspLastCorrectionWarnTime` |
| `AxisEquivMm` | **2026-09-22 ADR-042 新增**：跟踪轴工程单位当量（取 `_seamAxis.Equiv`；轴未连接或当量非法时回 `DefaultAxisEquivMm = 0.001`），保证脉冲换算不除零 |
| `ToPulseMm(valueMm)` | **2026-09-22 ADR-042 新增**：毫米 → 脉冲（`(int)(valueMm / AxisEquivMm)`，**截断取整**，与驱动器 `ToPulse` 同口径），供段距护栏与诊断日志使用 |
| `IsElapsed(lastTime, intervalMs)` / `TakeElapsed(ref lastTime, intervalMs)` | **限频判定统一入口（2026-09-22）**：前者只判定、后者命中即推进时刻；日志限频共用，替换原 5 处手写 `(DateTime.Now − …).TotalMilliseconds >= …` |
| `LogCspBufferDiagnostics()` / `LogCspCorrectionDebug(config, correction)` / `LogCspMotionDebug(...)` | 观测出口拆分：5s「缓冲诊断」（运行态/空闲拍/两查询原值）+ `CspDebugLogIntervalMs`(500ms) 两行 Debug（算法分量 / 运控写段）；均由 `TakeElapsed` 限频。**2026-09-28 B1 起「调试运控」增 段时基/几何段速/段速 三字段**（`_cspLastSegSeconds`/`_cspLastGeomVelMmPerS`/`_cspLastSegVelMmPerS`，此前只写不读），供段级取证 |
| `ResetToIdle(reason)` | 模拟态回待机：清报警与失败原因后 `SetPhase(Idle, reason)`（`Stop()` 错误分支与 `ResetProcess()` 共用，2026-09-22 归集） |
| `RecordOnlyTick()` | **无轴记录模式单拍（ADR-032）**：运控未连接时不写轴，目标与有轴模式**同源** —— `TryGetSeamTrackingTargetY(robotX, robotY, out targetY)` → `target = ClampToStroke(ready ? targetY : TeachLockYMm, config)`；以**虚拟轴 `_simAxisPos`**（`OnSeamTrackingStart` 置为 `TeachLockYMm`）为平滑基准：`command = StepCspTarget(target, 实测节拍)`（**ADR-042 起改二参**：逐拍先把 `_simAxisPos` 带入跟随器 `_cspFollowPos`，两模式共用同一整形器） → `_simAxisPos = command` → `RecordCspPoint(command, command)`（`_simAnchorPos` 已删；与有轴路径同构） |
| `RecordCspPoint(cspY, axisY)` | **调用点 3 处（ADR-042；ADR-042 起逐拍且不去重）**：`RunCspTick` 每拍 + `RecordOnlyTick`（无轴记录模式）+ `PvtTick`（PVT 路径）；不再在写段分支内调用。取 `DeviceControlWork.GetEffectiveRobotX()` + `WeldParamManager.CurrentRobotY` → `ProductFileRecordManager.RecordSeamTraceYPoint(robotX, mapKeyX, cspInYt, cspOutY, axisY)`（**5 参，2026-09-24 换轨**：`mapKeyX`/`cspInYt` 取算法诊断源 `SeamTrackingLastMapKeyX`/`SeamTrackingLastAcceptedTargetY`（尚无入图点时传 0）；~~`RecordTrajectoryPoint` 4 参~~ 已随 `TrajectoryRecord` 删除。⚠️ 工艺调整快照（FeedSpeed / RobotSpeed / LaserPower / SeamWidth）由 `.pDat`（`WeldParamControlRecord`）独占记录） |
| `TryStartSeamTraceYOnReady()` | **2026-09-24 新增**：Ready 检查通过后一次性开启焊缝 Y 记录会话——`_calReturnReady`（轴已回归标定位）+ `LineLaserManager.Instance.Profile.HasResult`（线激光反馈有数据）两者同时成立才调 `BeginSeamTraceYSession()`；由 `UpdateSeamTracking` 开头每拍尝试、早于任何按模式早退（保证无轴记录模式同样生效）。生产会话开启（`BeginProductSession`）**不再**立即开会话；会话复位（进入 Ready 相位 / `DoStopping`）清零 `_seamTraceYReadyStarted`。**2026-09-24 修**：以 `BeginSeamTraceYSession()` 的返回值为准——返回 false（生产会话基名未就绪）时**不置标志、按拍重试**并限频留痕（`SeamTraceYWaitLogIntervalMs = 2000`），避免自造 `SeamTraceY_时间戳` 孤儿文件夹 |
| `ShutdownSeamAxis()` | **2026-09-24 按需处理（业主收尾链末段口径）**：先查 `MontionAxis.IsAlarm()`（状态字 Fault 位 `0x0008`）——**无报警则保持使能直接回初始状态**（⛔ 不再无条件下电）；**检出报警才** `ServoOff()` → `ResetAlarm()` → `ServoOn()`。运控只为 Y 向轴服务（全轴会打到送丝力矩电机、实测错误码 256）；含重新上电是为避免轴停在断电态导致二次启动不响应指令 |
| `ResetSeamAxisBufferBeforeMove()` | **2026-09-24 新增**（**仅收尾侧使用**）= `BufferStop(Smooth)` + `BufferClear()`，清掉本会话已建的缓冲段与坐标系；成功则复位 `_cspBufferStartedOnce`。调用点 2 处：步 700 停稳后、步 900 停稳后。⚠️ **`_cspBufferStartedOnce` 门控**：本会话未建系时直接跳过并记日志——此时清空必报 **4352 = `ERR_ECAT_NEED_INITIAL`**（11:06 日志 L7/L38 实证）且无残留可清。⛔ **不得在 PreWork 移动前调用**（设备刚启动时缓冲尚未建立，业主点名「大可不必」）；`BufferClear` 报 4359 = `ERR_ECAT_NEED_STOP`（0x1107）⇒ 必须在轴停稳态执行 |
| `IsSeamAxisSettled()` | **2026-09-24 新增**：收尾等待判据——无轴 / `!IsMoving()` / `!IsServoOn()`（未使能的轴不可能再动，避免 Mdone 恒 0 白等）三者之一即放行；否则等至超时 `StoppingSettleSeconds = 5s` 按当前状态继续。未停稳时调用方 `return false`，由 `FlowProcess` 下一拍重入（⛔ 禁 while/Sleep，步骤驱动红线）。⚠️ 本判据只用于**收尾**（此时轴已在运动中或已停，无「未启动」竞态）；**回标定位侧必须两段判**（先等启动再等停止） |
| `TakeCspElapsedSeconds()` | 取本拍与上一拍实际间隔（`Stopwatch` 计数），两端钳位 `[CspMinTickSeconds = 0.001, CspMaxTickSeconds = 0.1]`（秒） |
| `IsEmergencyStop()` | `MontionManager.Instance.MontionControl.EmergencyStop`——**按拍检查**；置位即 `StopCspOutput()` 停写段并记 Warning |
| `StepCspTarget(target, tickSeconds, minVelocityMmPerS)` | **ADR-042 起改三参（前馈速度下限，0=无前馈）**：速度上限抬 max(MaxVel, 下限)、加速度上限抬 max(MaxAcc, 下限/τ)；**ADR-042 一阶跟随**：整形器**自持位置量 `_cspFollowPos`**（每拍推进，与「末段写入位置」解耦——若以 `_cspLastQueuedPos` 为基准，未写段的拍其位移会被丢弃、输出被钳在单拍最大位移内）。~~首参 `double current`（ADR-032 解耦轴读取；ADR-042/047 起有轴传 `_cspLastQueuedPos` 以保证段连续性）~~ 随二参化退场；段连续性改由 `segMm = command − _cspLastQueuedPos` 单独保证。⛔ **已废除的两种整形**：位置贴齐（ADR-042/053——窗口远大于每拍步长 ⇒ 每拍命中、限幅链旁路）与按剩余距离限速（ADR-042 决 二——剩余量取「已含本拍行程的输出」，限幅不生效时恒为 0 ⇒ 自锁，实测段距恰 0 占 85.5%、命令平台 441ms）。**现行 = 一阶跟随 → 速度限幅 → 加速度限幅** |
| `ReportCspResult(ret)` | **同错误码 1s 限频**记录（`CspErrorLogIntervalMs`，判定经 `IsElapsed`；2026-09-22 统一助手，2026-09-21 文案改「CSP 缓冲写入失败」） |
| `OnSeamTrackingAlarmRequested(sender, e)` | 只置 `volatile _seamAlarmPending`，**不推进执行步** |

**输出侧三段整形**（`StepCspTarget`，**ADR-042 现行**）：

| 阶段 | 规则 | 参数 |
|---|---|---|
| 一阶跟随 | `残差 = target − _cspFollowPos`（残差不足 1 脉冲即视为到位）→ `期望速度 = 残差 / τ` | `CspFollowTauSeconds` = 0.150 s |
| 速度限幅 | 期望速度超限则钳到上限；**相位滞后上界 = MaxVel × τ = 0.15mm** | `MaxVelMmPerS` = 50 mm/s（现场 1） |
| 加速度限幅 | `MaxAccMmPerS2 × tickSeconds` 即跨拍速度增量上限 | `MaxAccMmPerS2` = 500 mm/s²（现场 10） |
| 积分 | `_cspSmoothedVelocity += Δv` → `_cspFollowPos += v × tickSeconds` → 返回 `_cspFollowPos` | — |

> **结构不变式（ADR-042）**：整形环节的**残差必须取自「跟随器当前位置 → 目标」**，**绝不可取自「本拍输出 → 目标」**——后者含本拍行程，在加速度限幅不生效（常态）时恒为 0 ⇒ `√(2a·0) = 0` ⇒ 速度被清零、命令冻结。
> ⛔ ~~防过冲「位置贴齐」（ADR-042/053）~~ 与 ~~防过冲「减速限幅 √(2a·剩余)」（ADR-042 决 二）~~ 均已废除，见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]。

> **2026-09-22 ADR-042 演进（输出整形换轨，取代 ADR-042 决 二/决 三）**：① `StepCspTarget` 由「位置贴齐 → 减速限幅」两代整形统一换为**一阶跟随**（残差取「跟随器位置 → 目标」，τ=150ms；`_cspFollowPos` 每拍推进且与末段写入位置解耦；无轴分支逐拍把 `_simAxisPos` 带入）；② 写段门限**硬编为单脉冲当量** `AxisEquivMm`，`config.CspMinSegMm` 退出判定（现场 INI 的 0.005 会把占空比砍到 7~8%）；③ `OutputDeadbandMm` 默认 0.05→**0.01** 且**加载期上界 0.02**（INI 会保存旧值 0.05 ⇒ 只改默认值不生效）；④ `BufferIdleTicksToDrain` 20→**60**（须大于目标台阶间隔）；⑤ `TrajectoryRecord.RecordPoint` 去掉 robotX 去重（回看行数 47.7/s vs 输出节拍 94.8Hz）；⑥ 「缓冲闭环输出已启用」行扩为**生效配置整行自证**（增打印 τ / 门限 / 死区 / 耗干拍）。
> **2026-09-23 ADR-042 演进（速度前馈）**：`RunCspTick` 由 `GetEffectiveRobotX` 逐拍差分推算 X 向速度（钳位 + EMA），经 `WeldParamManager.TryGetSeamTrackingRequiredVelocityMmPerS` 取「地图局部斜率×vX」需求（尾部 ≥2mm 基线割线 + EMA），乘 `FeedforwardSafetyFactor`(3.0) 作为 `StepCspTarget` 第三参——速度/加速度上限动态抬升。**前馈只抬上限不产生位移，失真仅回退既有行为**；调试运控行增 `前馈` 字段。详见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]。
> **2026-09-23 ADR-042 演进（段速度连续化）**：`QueueCspSegment` 的段速度由「每段独立 `段距/间隔`」改为 **EMA(0.3) 跨段连续化** 后再钳限（端点平滑 ≠ 速度平滑——段间速度跳变即伺服速度轮廓台阶，是「入图平滑、出图顿挫」的主因）；段速时基上限 `CspMaxSegSeconds`(0.5s) 删除、改 `CspSegSecondsCap`(0.05s)；`StopCspOutput` 统计缓冲收尾失败连续场数（≥3 Warning）；调试行增 `累计段`。详见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]。
> **2026-09-23 ADR-042 演进 + 勘误（段距门限 / S 曲线时间）**：`QueueCspSegment` 写段门限由单脉冲当量换轨为 `max(CspMinWriteSegMm=0.01mm, 单脉冲半值)`（未写段拍段距照常累计，几何速度不失真）；`BufferPreloadSegments` 10→3；新增 `CspWriteChainEnabled` 写入数据链（17 列含 `CmdPosMm`）。**勘误**：S 曲线时间按台达建议取 **10ms**（`S_TIME=0.01` 秒，`ReadAxis` 兜底与 `MontionAxis` 默认同步 0.01，`AxisConfigForm` 标签单位 ms→**s**）——此前叙述的「STime=0.05s」是构造默认值假象，运行配置实际 S_TIME=0。详见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]。

> **2026-09-28 B1 核查（MIN_VEL / 段速下限）**：配置 `DeltaMotionConfig.xml` Y 轴 `MIN_VEL=1`（mm/s）解析为 `StrVel` → `axis.MinVel`，只作 `AbsMove`/`AbsMoveNoBlock`/`JogMove` 起始速度实参；**不进缓冲链路**——`BufferLineTo` 段速由 `QueueCspSegment` 几何折算显式传入（钳位 [0.85,1.0]×几何速度、下限 `AxisEquivMm`），故「降 MIN_VEL」不治跟踪锯齿，配置不改。剩余疑点（驱动器固件最小执行速度）由「调试运控」新增 段时基/几何段速/段速 三字段 + CSV `实时Y` 一次现场定性；判读口径与处置去向见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] §2.5。

> **2026-09-29 演进（队列积压反馈 · 消除实时轴落后命令）**：`QueueCspSegment` 在几何钳位之后、MaxVel 钳位之前叠加积压反馈 `vel += clamp((积压 − 死区) × 增益, 0, 上限)`，积压 = `(_cspLastQueuedPos − axisNow) × sign(segMm)`。**成因**：`sv≤gv` 上带使任何执行亏空永久残留（实测 gap 中 99% 为积压、随行程单调增长 0.13→0.67mm，而每段执行比中位数已 1.000）。**自限性**：积压趋近死区时增量趋 0，自动退回断供安全行为——区别于旧「上带 1.5 恒定提速 ⇒ FIFO 抽空回退」。只改写入段速，目标 `Yt` 与跟随器不受影响；「调试运控」行增 **积压 / 提速** 两字段观测。详见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] §2.6。

> **2026-09-22 ADR-042 演进（写段节拍与输出整形）**（决 二/决 三 已由 ADR-042 取代，决 一/四/五 继续有效）：① `QueueCspSegment` 段速度时基由**单拍**改**自上次写段的实测间隔**（段距是跨多拍累计的位移，按单拍折算会使每段时长仅约 1 拍而下段要等约 2.3 拍 ⇒ 实测写段 43.6 段/s、占空比约 44% ⇒ 驱动器缓冲跑空、轴停走）；② `StepCspTarget` 防过冲由「位置贴齐」改「减速限幅」（贴齐命中率实测 29%~94%，会把限幅链整体旁路）；③ `CspMinSegMm` 默认 0.005→0.001；④ 轨迹记录改 **`RunCspTick` 逐拍**（删除「写段分支内记录 + 100ms 静止补记」两处），回看曲线点距才反映真实 100Hz 命令流；⑤ `LogCspBufferDiagnostics` 增 **`写段占空比 {P0}({写段数}/{拍数})`** 观测（随该 5s 日志清零）。

**常量**：`CspWriteIntervalMaxSeconds = 0.15`（**2026-09-29** 写段时间门限；须 &lt; `CspSegSecondsCap=0.25` 才能保证时基不被截断；时间侧附加「≥1 整脉冲」）/ `CspBacklogVelGainPerS = 0.5`（队列积压反馈增益 1/秒，**2026-09-29**，段速增量 = 增益 ×（积压 − 死区）） / `CspBacklogVelCapMmPerS = 0.5`（增量上限，防起步大步阶被一次性拉高） / `CspBacklogDeadbandMm = 0.02`（死区，避开 ±1~3 脉冲量化抖动被放大） / ~~`CspOvershootWindowMm = 0.02`~~（⛔ ADR-042 删除，随位置贴齐退场） / **`CspFollowTauSeconds = 0.150`（一阶跟随时间常数，ADR-042）** / `CspErrorLogIntervalMs = 1000` / `HighResolutionTimerPeriodMs = 1` / `CspMinTickSeconds = 0.001` / `CspMaxTickSeconds = 0.1` / **`CspMaxSegSeconds = 0.5`（段速度折算的间隔上限，ADR-042）** / ~~**`CspSnapAfterStaticTicks = 5`（防过冲贴齐的静止拍门控，ADR-042）**~~（⛔ ADR-042 删除：阈值 1μm 小于每拍目标位移 ⇒ 判据恒真） / `BufferPreloadSegments = 10` / `BufferIdleTicksToDrain = 60`（耗尽推断；**ADR-042 由 20 放宽**——阈值须大于目标台阶间隔，实测平台 441ms） / ~~`BufferIdleRecordIntervalMs = 100`（静止补记）~~（⛔ 2026-09-22 ADR-042 删除，轨迹记录改逐拍） / ~~`MaxCorrectionMm = 5.0`~~（⛔ 2026-09-22 ADR-042 删除，幅值边界归 `ClampToStroke`） / `DefaultAxisEquivMm = 0.001`（单脉冲当量兜底，ADR-042） / `CspTeachDeviationWarnMm = 5.0`（标定位防呆） / `BufferStopModeSmooth = 0` / `CspDebugLogIntervalMs = 500`（[DEBUG-REMOVE] 验证期 Debug 行限频） / `CspBufferDiagIntervalMs = 5000`（缓冲诊断限频）。（~~`BufferRunDepth` / `CrdBufferCapacity`~~ 2026-09-21 二跑后随水位判据一并删除；~~`CspMinSegMm = 0.001`~~ **2026-09-22 ADR-042 删除，改由 `WeldAlgorithmsConfig.CspMinSegMm` 驱动**）

> **节拍来源（ADR-042）**：每拍间隔由编排层模组线程决定——`DeviceControlWork.SubDeviceWork()` 在 `MainDeviceStatus.Running` 时
> 调 `flow.FlowProcess()` 后 `Sleep(BeatWorkMs = 10)`，即**运行态基线 10ms/100Hz**；非运行态静默期 `ResetWorkTime()` + `Sleep(BeatIdleMs = 100)`。
> `timeBeginPeriod(1)` 经 `DllImport("winmm.dll")` 声明（`TimeBeginPeriod` / `TimeEndPeriod`），**起焊沿调用、停焊沿配对归还**。
> ⚠️ 步骤节拍的**实际精度需上机验证**——Windows 非实时 OS，10ms 只是基线，抖动由**实测 dt** 吸收（限幅器按实测值折算量纲，故改节拍无需重算限幅参数）。
> ✅ **急停双保险**：① `SubDeviceWork` 的 `Current != Running` 门控使急停后不再调 `FlowProcess`；② `OutputCspTick()` 内仍保留 `IsEmergencyStop()` 判据。
> ℹ️ **带宽核算**：数据源线激光 60Hz(16.7ms) / RSI 位姿 83Hz(12ms) 均慢于 100Hz 写入节拍，**并入步骤不构成带宽瓶颈**；原 1ms 线程在 1000 次中约 900 次写的是同一目标。

> **跨线程不推进执行步（ADR-042）**：折返报警在 **RSI 接收线程**触发，
> `OnSeamTrackingAlarmRequested` 只置标志位；`Fail()` 由**流程线程**在 `UpdateSeamTracking()` 内调用——
> 保证状态单次转换，规避并发双转换（详见 [[lessons/StepDrivenWorkflowPitfalls]]（七.2））。

---

## 关联

- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（§4 契约 · §5 RunStep 驱动 · §10 运动控制 · §16 模板）
- [[api/WeldParamManager]] — 模块唯一入口，代理 `SeamMapTrackingAlgorithm`（CSP）与 `SeamTrackingAlgorithm`（PVT）
- [[api/SeamMapTrackingAlgorithm]] — **CSP 模式**目标值来源（CSP 步骤每拍消费）
- [[api/SeamTrackingAlgorithm]] — 线激光引导轨迹算法（**PVT 模式**的点来源）
- ~~api/ICspMotion~~ — ⛔ 2026-09-21 删除（607A 契约随缓冲流式废止，CspResult 迁 `MontionAxis.cs`）
- [[api/WeldParamControlWorkflow]] — 焊缝跟踪工作态（`Working`）的判定来源；**不再提供标定配置**（2026-09-14 起由 [[api/WeldParamManager]] 自持）
- [[api/MontionManager]] — 运控业务层单例（轴/IO/气缸注册与查询，台达装配点）
- [[api/DeltaEtherCAT-Native]] — 台达 EtherCAT 原生 API 速查
- [[modules/MotionControl]] — 运控硬件层（三层架构与铁律）
- [[modules/Comm]] — 机器人位姿上行快照（CSP 模式的机器人 X/Y 来源）
- [[guides/DeltaEtherCAT-DevGuide]] — 台达落地规范
- [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — CSP 实时目标换轨决策（现行）
- [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — 运动缓冲流式段写入（本类 CSP 写入机制）
- [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — 闭环基准换轨（基准 = 轴实际反馈，**已经 ADR-042 演进**）
- [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — **目标基准换轨为起焊锚点 + 段端点基准统一 + 段距配置化**（基准条款已经 ADR-042/049 取代，其余机制沿用）
- [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] + [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — **目标基准两次换轨（起焊锚点 → 标定轴值 → 测量时刻轴值）+ 拆除「减基准再加回」折算 + 删 `ClampCorrection`/`MaxCorrectionMm` + 脉冲域段距护栏**（**本类 CSP 单拍闭环现行依据**）
- ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — CSP 输出并入 FlowProcess 步骤驱动（撤销独立 1ms 线程）
- [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]] — **输出整形现行决策**（一阶跟随 / 门限硬编 / 死区上界 / 耗干阈值 / 逐拍不去重）
- [[decisions/ADR-032-SimulationTestRedesign]] — 模拟统一化（无轴记录模式 `RecordOnlyTick` / `StepCspTarget` 解耦 / `SimTrajectoryRecorder`）
- [[lessons/StepDrivenWorkflowPitfalls]]（七.5）— 1ms 调度（TimeBeginPeriod / 绝对时刻校正 / 日志限频）；**2026-09-16 起随独立线程移除而失效**，页内已加沿革处置
- [[lessons/StepDrivenWorkflowPitfalls]]（七.2）— 跨线程不推进执行步（`_seamAlarmPending` 标志范式）
- [[decisions/ADR-027-MotionControllerDeltaReplacement]] — 台达替换决策
- ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 正运动移除与台达落地
- [[decisions/ADR-013-ThreeStateModelRefactor]]、[[decisions/ADR-035-RawDesignRefinement20260903]] — 三态模型与原档细化裁定

## Y / TA 流程归属与按轴门禁（2026-11-05）

> **归属裁定**：台达控制器上的 Y 轴与送丝轴（TA）在**硬件层**统一归 `MontionManager`；在**流程层**（指令编排、判据、状态检测）归本类。
> 自动对焦电机与振镜属焊接头从站，流程归 [[api/LaserWeldHeadWorkflow]]。本类不再承载 LA 指令。

| 成员 | 语义 |
|---|---|
| `YReady` / `YGateReason` | Y 轴流程层就绪 / 不可用原因（委托 `MontionManager` 的轴状态，按轴独立） |
| `TaAvailable` / `TaMotionReady` / `TaDegradedReason` | TA 指令可执行（已使能+已回零）/ 可动（仅配置+使能）/ 降级原因 |
| `GetTaGateReason(bool allowZeroPose)` | UI 单点门禁：⛔ 2026-11-17 起 `allowZeroPose` **不再放宽**（TA_Zero 与其它 TA 同口径要求已回零）；初始化链未完成统一拒绝 |
| `TaExecute(TaCommand)` | **TA 指令唯一公开入口（2026-11-09）**：枚举 `Auto` / `Retract` / `Break` / `Pose1` / `Pose2` / `ZeroPose`，内部 `switch` 转调三组实现（力矩 / CSP 定位 / 零位定位）。原 `TaAuto()` / `TaRetract()` / `TaTorque()` / `TaBreak()` / `TaPose1()` / `TaPose2()` / `TaZeroPose()` 全部删除（原在 `LaserWeldHeadWorkflow`，2026-11-05 迁入）。**全族阻塞到结果**，调用方（后台指令执行体）只改传参。⛔ **手动入口**：含「自动焊接流程进行中禁手动动作」门禁（`CheckAutoWeldingConflict`），PreWork 态会被拒 ⇒ 流程内调用须用 `TaExecuteAuto()` |
| `TaExecuteAuto()` | **TA 自动模式的流程内入口（2026-11-23）**：仅执行 `TaCommand.Auto`（按设定下压力自动压紧），⛔ **不做**「自动焊接中禁手动动作」门禁检查——焊前阶段属自动流程，主控派发的动作是流程组成而非手动干预。⛔ 仍受 `CheckTaAvailable` 前置约束（`Manager.TaAvailable` = `TaMotionReady && TaHomed`，复位链完成后成立）。被 `DeviceControlWork.EnterPreWorkWorkingModes()` 调用。见 [[decisions/ADR-100-state-union-and-action-gate]] D31 · [[decisions/ADR-038-RobotCommandDrivenStepFlow]] D5 |
| `RunTaZeroPoseAfterInit` | **2026-11-08（决策八）自 `MontionManager` 迁入**：直接委托 `ExecuteTaZeroPose()`；手动与初始化共用同一实现，⛔ 不保留两份等待逻辑。**2026-11-10 起不再自带前置判定** —— 初始化闸门、轴可动、并发全由 `ExecuteTaZeroPose`→`CheckTaAvailable` / `TryBeginAxisInstruction` 判一次 |
| `ExecuteTaZeroPose`（私有） | 阻塞到结果：单飞登记 → `ExitTaTorque` 撤力（按 `TorqueOutputEnabled` 判定）→ `TryMoveAbsoluteNoBlock` → 已在位直通 / `WaitAxisAtTarget`（超时按行程/速度×3 估算，上下限取 `PositionReachMin/MaxSeconds`，无变化早停 `PositionReachNoChangeSeconds`）→ 成功 `MarkTaZeroPoseSucceeded` / 失败 `StopAxis` + `MarkTaZeroPoseFailed`；`finally` 唯一释放运行态与单飞 |
| `ExitTaTorque` / `SetTaTorqueMode` / `SetTaTorque` / `StopTaTorque` | **2026-11-09 自 `MontionManager` 迁入**：TA 角色级力矩动作（原 `SetWireFeedTorque*` 更名）；**送丝即 TA**，⛔ 不再造「送丝轴」概念、⛔ 不按三轴口径描述 |
| `TaTorqueActive` / `TaTorqueRetractFailed` / `TaTorqueRetractFailCode` / `TaBreakHoldMm` / `TaBreakHoldValid` / `TaPositionMm` | TA 运行期只读态（UI 显示 + LA 随动补偿取 TA 位置）；`TaTorqueRetractFailed` 区分「正常出力中」与「撤力失败残留出力」，UI ⛔ 不得自行推导（ADR-087 决策） |
| `TaTorqueRetractFailureText` | TA 撤力失败**成品文案**：硬件错误码措辞由 `MontionManager.DescribeAxisRetractFailure` 产出，本属性只拼「TA 力矩」与重试指引；UI 直显不拼接（ADR-095） |

- **单飞**：仍由硬件层 `MontionManager.TryBeginAxisInstruction(axisName, …)` 按**轴名**登记 —— 跨流程互斥的保证是「同一物理轴只有一份轴名登记」，
  Y 与 TA 共用同一控制器但轴名不同、可并行；TA 与 LA 若同轴则会互斥（当前不共用轴）。
- **安全全局 / 功能按轴**：急停、总线非 OP、驱动器报警 —— 所有轴一律拒绝（硬件层）；使能失败、ZeroPose 未到位 —— 只关该轴闸门。
- **兼容壳**：[[api/LaserWeldHeadWorkflow]] 保留同名 TA 方法薄转发（只转调本类，⛔ 无第二份实现），新调用方应直接调本类。

### TA_Retract（回缩，2026-11-06 定稿：Auto 反向 · 纯力矩保持）

| 项 | 口径 |
|---|---|
| 语义 | **`TA_Auto` 方向取反**的纯力矩输出：切 CST → 开输出 → 按反向目标力矩**持续出力并保持返回** |
| 力值 | 大小 = `WeldAlgorithmsConfig.TaForceN`；方向 = `TA_TORQUE_DIRECTION` 取反；千分比换算沿用 `TA_FORCE_100PCT_N`（与 Auto 共用 `TryResolveTaTorque`）；目标超 `TA_TORQUE_LIMIT_N` 时按上限下发（ADR-088，日志「目标 X‰ 超出扭矩上限 Y‰」） |
| 终点 / 到位判定 | **无**：⛔ 不设终点、⛔ 不判位置容差、⛔ 不做「回缩到位」 |
| 撤力 / 锁位 | **无**：⛔ 不调 `StopTorque`、⛔ 不回 CSP、⛔ 不 `AbsMove` 锁位；退出与 `TA_Auto` 相同（后续指令 / `ExitTaTorqueMode` / 急停等既有路径） |
| 日志 | 「TA Retract 力矩回缩中 起点 … 目标力矩 … 爬升速率 …」/「TA Retract 力矩生效达成」；⛔ 无「到位撤力」「撤力回 CSP」，⛔ 无每秒进度 |
| 超时 | 仅「力矩生效检测」固定 5s（`WaitTaTorqueOn`，`InstructionDetectTimeoutSeconds`）；⛔ 无按行程放宽的动态超时 |
| 停机条件 | 只保留 `SetTorque` 既有软限位前置检查 + 状态字/报警判定；⛔ 无反向回升保护 |
| 单飞 | `TryBeginAxisInstruction("TA_Retract")`，`finally EndAxisInstruction`，与 Auto 一致 |
| 与 Auto 的唯一差异 | 出力方向符号（`reverse: true`）、章节日志文案，以及 Retract 独有「先读起点位置并写进成功日志」；其余逐行对齐 |

> **2026-11-09 合并（第二轮）**：`TaAuto()` / `TaRetract()` / `TaTorque()` / `TaBreak()` / `TaPose1()` / `TaPose2()` / `TaZeroPose()` 已全部删除，
> 统一入口 `bool TaExecute(TaCommand command)`；内部按语义分三组：力矩（Auto/Retract）、CSP 定位（Break/Pose1/Pose2）、零位定位（ZeroPose）。
> `switch` 只决定单飞登记名、出力方向、取消 ZeroPose 的文案名与逐字日志；可用性判定、力值解析、
> 伺服使能、5s 生效检测、失败 `StopTorque`、`finally EndAxisInstruction` 完全共用。UI 调用方只改传参。

- **单一斜率（2026-11-06 收口，ADR-088）**：`TaTorque` 的 Auto / Retract 两支都调 `axis.SetTorque(torque, axisCfg.TorqueSlope)`；
  同号调力与符号翻转共用 `TORQUE_SLOPE` 一条路径，⛔ 不存在第二套斜率/交接点/速度守卫参数。
  ⚠️ 该斜率只决定「力建立多快」，**不能**限制速度，也治不了跑飞与撞击（根因 = CST 无速度上限）。

> ⚠️ 2026-11-05 版「位置终点 + 到位撤力 + CSP 锁位 + 行程动态超时 + 反向 1mm 保护」已被 2026-11-06 现场日志否证并全部删除
> （`WaitTaRetractReach` / `CutTaTorqueAndLock` / `InstructionRetractReverseGuardMm`），历史见 ADR-082「2026-11-05」节。

## TA_ZeroPose 手动重试闭环（2026-11-09，ADR-093 决策九 · ADR-094 D1/D4 演进）

- **四态归属本类**：`TaZeroPoseStageChanged` 事件与 `IsTaZeroPoseRunning` / `Attempted` / `Done` / `Failed` 四态已由 `MontionManager` 迁入本类；Manager 只保留 `SetTaZeroPoseGate` 供本类写入判定结果。
- `TaExecute(ZeroPose)` 进入即以 `MarkTaZeroPoseRunning(true)` 上报开始态：**已在位直通分支同样产出「开始 → 结束」序列**（⛔ 不再空等结果超时）。
- **2026-11-09 形态统一**：异步 worker 已删除，改为与 `Pose1/Pose2` 同形态**阻塞到到位/失败/超时**；调用点均在后台指令执行体（`InstructionWorker` / `thIOWork`），⛔ 不卡 UI。
- 两条成功分支（已在位直通 / 阻塞等待到位）都调 `MarkTaZeroPoseSucceeded()`：TaAvailable 恢复、TA_Auto 与 TA 指令立即可点。
- 失败分支调 `MarkTaZeroPoseFailed(reason)` 后再清运行态，UI 收到「结束」事件时结果已就位（不出现先红后绿/先绿后红）；`Attempted=false` 的「从未执行」不上色，保持白色。
- `_taZeroPoseRunning` 的清除只有一处：`ExecuteTaZeroPose` 的 `finally`（手动与初始化共用），单飞登记同点释放。
- **取消（ADR-094 D4）**：`CancelTaZeroPose` 已整个删除，⛔ 不设「取消指令」专用接口；TA 指令只响应急停与停止两类外部终止 —— 急停走 `MontionManager.CancelAllAxisInstructions`，停止走 `StopAxis` 内的单轴取消，两者都使 `WaitAxisAtTarget` 的 `token` 立即返回，`finally` 照常释放单飞。
- 分层归属：本页为流程层唯一实现，UI（`ProcessControlPage`）只调 `TaExecute` 并订阅本类事件；四层边界与待收敛清单见 [[architecture/CodeMap]]「四层边界现状 / 待收敛清单」。

## 初始化收尾：RunTaHomeThenZeroPose（2026-11-11）

- 新增 `public bool RunTaHomeThenZeroPose()`：`TryHomeAxisWithWait(TA, "初始化回零")` → 成功才 `ExecuteTaZeroPose()`；回零失败即打「初始化回零失败 轴 … 原因 … 证据 …」并直接返回 false，**不继续定位**。
- `RunTaZeroPoseAfterInit()` 保留（只走 ZeroPose），初始化链改调新方法。
- `ExecuteTaZeroPose` 入口在 `!Manager.TaHomed` 时打「TA ZeroPose 告警 本次上电尚未回零 位置可能不可信」，供手动重试场景留痕。
- 顺序依据：上电后位置寄存器不可信（[[standards/DeviceInitializationDependency]] §七）。

## 复位挂回既有复位链（2026-11-16，阶段 3 / ADR-099）

- 复位入口不变：`DeviceControlWork.ResetMachine()`（开启复位动作）→ `thIOWork` 扫 `IoReset` → `DoResetMachine()` 复位线程 → `CascadeResetProcess()` → 本流程 `ResetProcess()`；⛔ 不新增第二套复位通道。
- `ResetProcess()` 在锁内完成：模拟态早退；`_initialized` 前提；`EnsureResetReadiness()` 门槛 L1；清急停、进 `Standby`。轴动作在锁外由 `ResetAxesToWorkZero()` 执行，避免阻塞流程线程。
- 门槛 L1：`HasHomingRequiredAxis` 看 `Manager.TaMotionReady`、`HasFreeHomingAxis` 看 `Manager.YReady`；不满足打「复位未执行 就绪不足 当前 L0 需 L1 原因 …」并返回 false。
- 按轴能力分支（⛔ 不按轴名特判），动作落到管理器：
  - 需回零轴：`Manager.TaHomed == false` 时先经 `MontionManager.HomeAxisAndWait` 回零，失败打「停在 L2 可重试」；成功再 `ExecuteTaZeroPose()`，未到位打「停在 L3 可重试」。
  - 免回零轴（绝对编码器）：跳过 `Home()`，经 `MontionManager` 定位动作直达工作零位（目标 `TeachLockYMm`）。
- 两条能力判据 `HasHomingRequiredAxis` / `HasFreeHomingAxis` 为私有只读属性，新增轴只改能力不改分支。
- 新增 `public bool RunInitAutoHomeIfEnabled()`：`INIT_RUN_TA_HOME=1` 时打「回退开关…」并按旧行为调用 `RunTaHomeThenZeroPose()`；默认关闭即初始化不做任何运动。
- 关联：[[decisions/ADR-099-init-reset-separation]] · [[decisions/ADR-098-readiness-layering-axis-capability]]

## 运控关闭唯一入口（2026-11-17，阶段 5 / ADR-101）

- `InitializeOff()` 首部幂等：`State == Disconnected && !_initialized` 直接返回 true，避免重复断开与重复日志。
- `DisposeManaged()` 不再独立调 `Manager.Close()`，改为委派 `InitializeOff()`；`MontionManager.Close()` 自身也加幂等守卫（未初始化且无控制器对象即返回）。
- 目的：关闭台达主站只有一条路径，级联断开与工作流释放不会二次关闭总线。
- 关联：[[decisions/ADR-101-shutdown-closure-and-estop]]

## 缺值保持与报警停焊（2026-11-17，阶段 7 / ADR-103）

- `RunCspTick` 新增 `_cspHasHeldTarget` / `_cspHeldTargetY`：有效目标即刷新 held；缺值期取 held 继续按拍下发，禁止回落 `TeachLockYMm`；仅首个有效目标前允许以标定位起步（`StartCspOutput` 复位）。
- 缺值累计达 `NoValueToleranceMm` 时 `RaiseNoValueAlarm`：一条 `Error` → `ReportAlarm`（内含 `TX_NG`）→ `StopCspOutput` → `Fail("NoValueAlarm …")`，流程收尾到 `ErrorAborted`；`_noValueAlarmRaised` 保证一次焊段只报一次。
- ⛔ 不复用 `DoStopMachine`：不断设备、不关模组线程、不清缺值累计器；报警后连接与就绪分层保持可读。
- 关联：[[decisions/ADR-103-no-value-hold-and-distance-segment]] · [[api/WeldParamManager]]

## 手动轴操作改非阻塞 + 回零统一入口（2026-11-17，ADR-073 D25 / ADR-099 D27）

| 入口 | 用途 | 是否阻塞 |
|---|---|---|
| `TryManualAxisOperation` | 伺服 / 停止 / 点动 / **非阻塞**移动下发 | MoveTo / StepMove 改走 `MoveToNoBlock` / `StepMoveNoBlock`，**不等到位** |
| `TryMoveAxisToTarget` | 绝对移动并等待到位（UI 绝对移动唯一入口） | 是 ⇒ 须在后台线程调用 |
| `TryHomeAxisWithWait` | 回零并等驱动器确认（**手动回零与复位回零唯一共用入口**） | 是 ⇒ 须在后台线程调用 |

- ⛔ `TryManualAxisOperation` 已移除 `Home` 分支 ⇒ 手动回零与复位回零走同一实现，`TaHomed` 结论一致、不区分来源。
- `GetTaGateReason(false)` 拒绝原因尾部附「工作零位未到位：xxx」观测事实（**不阻断**）。
- `CheckTaAvailable` 拒绝文案改为「TA 指令不可执行（未使能或未回零）」；`MarkTaZeroPoseFailed` 日志改为「工作零位未到位（不阻断 TA 指令，仅观测）」。
- 关联：[[decisions/ADR-073-AxisControlUnifiedMontionManager]] · [[decisions/ADR-099-init-reset-separation]]

## 自动焊接禁入手动动作 + TA_Zero 门禁改「已回零」（2026-11-17，ADR-100 D29 / ADR-082 D30）

**新增拒绝码**：`AxisRejectAutoWelding = "AUTO_WELDING"`。

**手动轴动作门禁**（`DeviceControlWork.IsAutoWeldingRunning` 为真 ⇒ 拒绝）：

| 入口 | 门禁 | 说明 |
|---|---|---|
| `TryManualAxisOperation` | 有（**`Stop` / `JogStop` 除外**） | 伺服切换 / 点动 / 移动在焊接中一律拒绝 |
| `TryMoveAxisToTarget` | 有 | UI 绝对移动（Y / TA / 步进换算） |
| `TryHomeAxisWithWait` | 有 | 回零 |
| `TaExecute` | 有 | TA 六指令统一入口 |

**TA_Zero 门禁改口径**（ADR-082 D30）：

- `ExecuteTaZeroPose` 前置由 `CheckTaMotionReady`（仅已使能）改为 **`CheckTaAvailable`（已使能 + 已回零）** —— 未回零时位置不可信，工作零位定位同样不可信。
- ⛔ 仍**不受「工作零位已到位」限制**（否则降级后无法重试）；「工作零位到位」只是观测事实（`TaAtWorkZero`）。
- 删除 `CheckTaMotionReady`（改后零消费）与「未回零只告警」块（已成死代码）。
- `GetTaGateReason(bool allowZeroPose)`：`allowZeroPose` **不再放宽**（签名保留以免破坏外部调用，语义在注释中说明）。

- 关联：[[decisions/ADR-100-state-union-and-action-gate]] · [[decisions/ADR-082-TaInitFourStepAndAvailability]]
