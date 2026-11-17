---
title: LaserWeldHeadWorkflow API 参考（焊接头工作流 · 骨架期）
date: 2026-09-02
updated: 2026-10-16
tags: [API, 工作流, 焊接头, RunStep, SubDeviceWeldStatus, DeviceWorkflowBase, ADR-034, ADR-020, ADR-057, ADR-067]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs
---

# LaserWeldHeadWorkflow API 参考

> 焊接头工作流（单例，**骨架期**：私有相位驱动 + 差异化职责待落地）。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：非泛型 `DeviceWorkflowBase`（17 项契约）→ `DeviceStateBase`；`IDisposable` 由基类实现。

> **✅ 2026-09-04 已落地（ADR-020 批次 0~4.4）**：本类已按新架构改码——无自带线程、`RunStep` 驱动范式就位（骨架期无业务执行步）、对外焊接过程态统一经 `SetWeldStatus` 承载。旧 `GoStep`/`SetStep`/`WorkStep`/`StartRunLoop`/`ManualOn`/`ManualOff`/命令三槽等机制已全部清除，不得据旧内容改码。真编译待 VS（静态自检已通过）。
> 步骤驱动规范见 [[architecture/DeviceControlArchitecture]] §4（17 契约）· §5（`RunStep` 驱动）· §16（代码模板）。

---

## 🔄 温控闭环接线（2026-10-09 P3 批 A）

| 项 | 说明 |
|---|---|
| **订阅** | 构造函数订阅 `WeldHeadSlaveDevice.TemperatureAlarm` / `AlarmTriggered`（此前**两事件 0 订阅方**，从站报警升起后无人接收）；`DisposeManaged()` 退订 |
| **本侧二次判阈** | `OnWeldHeadTemperatureAlarm` 读 `WeldHeadConfig.TempWarnThreshold`/`TempAlarmThreshold`，超限入日志 + `SetState(SubDeviceState.Alarm, ...)`。⚠️ 从站侧已在 `0x7020` 独立报警，此为软件兜底双保险 |
| **报警位转文本** | `DescribeAlarm` 把 `HeadAlarmStatus` 四个位转可读文本（保护镜温度/温升/切割气压/驱动器） |
| **只读属性** | `LastTemperature` / `LastAlarmStatus` / `IsTemperatureAlarm`（供 ADR-054 状态栏与温度监测 UI（U-6）读取；温控 ADR 待建，原预测编号 074 已被光丝对中占用） |
| **todo 落地** | `SubDeviceLog` 的「todo 温度阈值监控」已落地（汇总输出温度与报警态） |

> ⛔ **阈值不双写**：`SetAlarmThresholds` 仍只在 `MontionManager:257` 初始化时下发（单一入口），本工作流**不重复下发**。
> ⚠️ 已知可疑点待上机核实：`SetAlarmThresholds` 第 5 参（气压报警）用了 `ScaleTemp` 做缩放，与温度同量纲存疑。

## 🎛 TA/LA 动作指令与 auto 随动（2026-10-09 P3 批E · F-1/F-2 · [[decisions/ADR-057-TaLaActionAndFollowControl]]）

> 需求 38/41「激光头工作流&TA和LA算法」落地：9 个动作方法在「非阻塞动作指令」region，P4（U-1/U-2/U-5）只绑按钮。

| 动作方法 | 行为 | 需求 |
|---|---|---|
| `TaAuto()` | 下压力：入口只判 `TaAvailable`；先 `CancelTaZeroPose` 停 ZeroPose → 伺服使能兜底 → **力大小/方向分离**（负值/0 拒绝 → `目标‰ = 方向(±1) × round(力大小 / TA_FORCE_100PCT_N × 1000)`，`力大小>基准`/换算为 0/基准≤0 均拒绝）→ `SetTorque(目标‰, TorqueSlope)`（内部自切 `Set_MoveMode(CST=10)` 回读→`CST_Start_Move`→`CST_Output_Enable(1)`，失败回滚 CSP）。成功日志含「力值 N / 方向 +/− / 目标‰ / 扭矩爬升速率」。⛔ 无「力矩模式开关」前置（ADR-082）；⛔ 不把牛顿当千分比直发（ADR-084）；⛔ 不静默取绝对值（ADR-084） | 17/38 |
| `TaBreak()` | 停止并锁存位置（业主 2026-10-09 裁定）：仅 `TorqueOutputEnabled` 时生效 → 先锁存反馈位 → `StopTorque()` 撤 CST → `AbsMove(锁存位)` 位置保持，**撤掉工件轴不移动** | 17/18 |
| `TaPose1()` / `TaPose2()` | 入口 `ExitTaTorqueMode`（撤 CST 输出回 CSP，仅设备态变化）→ `AbsMove` 到预设调试位；⛔ 不影响 Auto 可用性 | 19 |
| `LaAuto()` | 开随动：按拍 `LA = QueryLaPositionMm(目标光斑) + QueryLaOffsetMm(TA位置)`（0.01mm 死区防刷总线） | 20/21 逻辑2 |
| `LaSpot1()` / `LaSpot2()` | 设目标光斑 → 曲线A 反查基准 → **按当前 TA 位置推算**下发（TA=0 退化纯曲线A） | 21 逻辑1/22 |
| `LaPose1()` / `LaPose2()` | 直达预设位，不经曲线，退出随动 | 22 |
| `GalvoHome()` | 回逻辑零位（直线+最小摆幅+不使能），中心补偿状态清零（F-4「回到零位」） | 23 |
| `GalvoDemo(pattern)` | 手动演示（圆/八字/直线/圆弧）：一次性下发（摆幅 1.0mm），`IsWelding` 时拒绝（与生产互斥），停止=回零位（F-3） | 23 |
| `ApplyGalvoCenterOffset(xMm, yMm)` | 光丝对中→振镜中心补偿**单写口**（只改状态，随动步合并下发防互覆；F-4，默认门控见 ADR-059） | 23 |

- **状态标志**（bool，无枚举·ADR-055）：`TaTorqueActive`（转发 `DeltaMontionAxis.TorqueOutputEnabled`，设备真实态）/ `LaFollowActive` / `TargetSpotMm`（只读，供 UI 显示动作位）
- **目标光斑初值口径（2026-10-21）**：`_targetSpotMm` 在**构造期**取 `WeldParamManager.Instance.AnchorSpotMm`（曲线A 的 LA=0 锚点光斑）——⛔ 不得直读 `TaLaCurveConfig` 的锚点常量（配置读取唯一入口，ADR-053/ADR-066）。`LoadConfig()` 仍可用工艺配置 `LA_SPOT_TARGET_MM` 覆盖（键存在且 >0 时）。
- **随动步**：`FlowProcess` 三步环（待机→振镜下发→`StepLaFollow` LA 随动→待机）；随动日志静默防刷屏
- **预设值**：`WeldAlgorithmsConfig` PROCESS_CONTROL 7 键（`LA_SPOT_TARGET_MM`/`LA_SPOT1_MM`/`LA_SPOT2_MM`/`TA_POSE1_MM`/`TA_POSE2_MM`/`LA_POSE1_MM`/`LA_POSE2_MM`）
- ~~**TA 限位报警（全模式）**不在本类 —— 归 `DeviceStatusWork.ScanTaPositionLimit`（复用轴软限位，边沿 `ReportAlarm`/`ReportAlarmCleared`）~~ → **2026-11-06 该扫描整段删除（ADR-091）**：越限撤力会打断力矩下压，现无 TA 位置越限报警源
- **曲线修复**（S-5 骨架缺陷，消费前必修）：`TaLaCurveConfig.Interpolate` 反查 lo/hi 颠倒、正查域上界取错、Clamp 双端同返首点三处已修；单点默认组按「1:1 线性外延」

## 🔁 LA 三指令语义重写 + TA_Retract（2026-10-14 · [[decisions/ADR-067-LATaSettingsSemanticRework|ADR-067]]）

> 历史标注：本节 2026-10-14 原文中的 `TA_Recheck`（CSP 直接回零）已于 2026-11-05 更名为 **`TA_Retract`（CST 力矩反向出力）**，
> 下列回零实现为历史记录、已废止；当前口径见 [[api/MotionControlWorkflow]]「TA_Retract（回缩）」与 ADR-082 D24~D29。

> 业主口径：**LA 工艺设置是配置项不是指令动作**（UI 侧 LA 参数区重构见 [[api/ProcessControlPage]]）；LA 三指令语义换轨如下（上表批E 行中 `LaSpot1()/LaSpot2()` 的「按钮直发」形态随 UI 按钮删除而退场，快捷 Radio 指令链保留）。

| 指令 | 新语义 | 实现要点 |
|---|---|---|
| **LA_Pose** | **纯到位**——仅 LA 轴移动到指定位置，**与其他逻辑无关联** | `LaMoveToPose`；`_laFollowActive=false` |
| **LA_Spot** | **设定光斑**——目标光斑经**曲线 A**（`QueryLaPositionMm`）反查 LA 基准位 → 定位 → `ApplyLaFollow` 单次偏移补偿；成功后 `_laFollowActive=false` **退出随动** | `LaApplySpot` |
| **LA_Auto** | **模式开关**——`LaSpotTargetMm>0` 时先 `LaApplySpot` 定位（**失败 return false 不进随动**）；成功后 `_laFollowActive=true; _lastLaTargetMm=NaN` 进入**持续随动**：运行期 TA 实时位 → **曲线 B**（`QueryLaOffsetMm`）补偿实时修 LA，保持光斑恒定 | `LaAuto` 重写 |

- **联动唯一数据源**：系统设置下 **TaLaCurveConfig** 标定曲线（曲线 A 基准反查 + 曲线 B TA 偏移，[[decisions/ADR-053-TaLaCurveAndMotorScale|ADR-053]]），LA/TA 内部联动、无外部指令耦合。
- **退出随动入口**（业主裁定）：LA_Spot 成功即退出；LA_Pose 执行即退出。
- **删除死代码** `LaApplyTargetSpot()`。
- **TA 回缩指令（历史）**：当时名为 `TA_Recheck`——`ExitTaTorqueMode` → `TaMoveTo(0.0)` 直接回零；2026-11-05 更名为 `TA_Retract`
  （CST 反向出力；2026-11-06 定稿为「Auto 反向的纯力矩保持」，无位置终点、不撤力），
  UI 侧 `radioQuickTaRetract`（仅 `TaAvailable` 未就绪时置灰，ADR-082）。

## 公共成员

| 成员 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static LaserWeldHeadWorkflow` | `Lazy<T>` 单例 |
| `StateName` | `override string` | 对外名片名，返回 `Tag`（日志/事件标识） |
| `State` / `WeldStatus` | 基类属性 | 连接态（`SubDeviceState`）/ 焊接过程态（`SubDeviceWeldStatus`） |
| `RunStep` / `StepWorkTime` / `WorkStepName` / `StepStatusText` | 基类属性 | 执行步 / 步骤用时 / 步中文名 / 可观测摘要 |

> `ConfigFileName = "LaserWeldHeadWorkflow"`（protected override，配置落在 `Config/LaserWeldHead/Workflow_XML/` 下）。

---

## 私有相位 `LaserWeldHeadWorkflowState`（骨架期最小集，同文件公共枚举）

`_phase`（默认 `Uninitialized`）仅驱动 `FlowProcess` 与可观测性，对外统一经 `SetWeldStatus(MapWeldStatus(phase))` 映射：

| 取值 | 含义 | 映射 `SubDeviceWeldStatus` |
|---|---|---|
| `Uninitialized`(0) | 未初始化 | `NoReset` |
| `Standby`(1) | 待机（已连接就绪） | `Standby` |
| `Working`(2) | 工作中 | `Working` |
| `ErrorAborted`(3) | 异常终止 | `ErrorAborted` |

> `SetPhase(phase, reason)` 是相位唯一写入口：刷新 `_phase` → `SetWeldStatus(MapWeldStatus(phase), reason)`。映射由私有 `MapWeldStatus(phase)` 承载，其余相位一律回落 `NoReset`。
> ⛔ 禁止手工 `WeldStatus = ...` / `State = ...` 赋值。

---

## 差异化职责（原档 R009）

**① 振镜参数运行期下发**（2026-10-08 ADR-042 落地）——补消费方，取代原「只有初始化下发」的骨架状态：

```
焊缝识别宽度 → CalcGalvoAmplitude（查表优先 / 公式兜底）
  → WeldParamOutput.GalvoAmplitude
  → LastOutput（LastOutput 属性）
  → ApplyGalvoAmplitude（本工作流 StepGalvo 步）
  → WeldHeadSlaveDevice.SetGalvoParams
  → WSX RxPDO 0x7010
```

| 环节 | 落点 |
|---|---|
| 执行步 | `StepIdle = 0` → `StepGalvo = 10` → 回 `StepIdle`（`AdvanceStep` 推进）——⚠️ **2026-10-16 修复（业主）**：本类原私有重写 `private const int StepIdle = 0;` 与基类 `DeviceWorkflowBase` 同名常量冲突（CS0108 隐藏继承成员），已**删除私有定义**，现行 `StepIdle` 全部解析自基类（`StepGalvo=10`/`StepLaFollow=20` 保留私有）；[[api/DeviceStateApiCore]]「子类不得重复定义」条款由此对本类生效 |
| 消费方法 | `ApplyGalvoAmplitude()`：从 `WeldParamControlWorkflow.Instance.LastOutput.GalvoAmplitude` 取摆幅 |
| 下发内容 | `GalvoParams.CreateLogicalHome()` 为基底，只改 `Width` / `Length` / `GalvoEnable`；⛔ 局部变量**不可命名 `params`**（C# 关键字），本类统一用 `galvo` |
| 降抖 | `_lastGalvoAmplitudeMm` 记住上次值，变化 < 0.01mm 直接跳过（不逐帧刷 EtherCAT 总线） |
| 关闭摆动 | `_galvoWeaveEnabled`（`LoadConfig` 从 `WeldAlgorithmsConfig.EnableGalvoWeave` 取）false ⇒ 下发摆幅 0 + 不使能，而非保持上次摆幅 |
| 失败处理 | `SetGalvoParams` 返回 false 时**不更新** `_lastGalvoAmplitudeMm`，下拍重试 |

⚠️ **中心偏移不由本链路写**：`XCenter/YCenter` 归光丝对中补偿链路（`ApplySpotAlignCompensation`，P3 待实现）。两条链路都碰中心偏移，**必须各自单一写入口**，否则互相覆盖（P1 §1.6 结构冲突项）。

⛔ `FlowProcess` 的 case 内禁 `Thread.Sleep` / `while`（ADR-038）。

**② 温度阈值监控**（原档 R009）——待硬件温度点位明确后落地。当前留痕位置：

- `SubDeviceLog()`：`// todo` 温度与阈值日志，暂输出 相位/连接态/焊接过程态。

> 骨架期私有逻辑一律在 `switch(RunStep)` 内新增执行步，每 case 靠 bool 判定推进、推进前刷新计时（§5 范式），新相位一律经 `SetWeldStatus` 映射。

---

## 连接 / 生命周期契约（骨架期无实体设备，置标志位即返回）

| 方法 | 语义 | 状态联动 |
|---|---|---|
| `InitializeOn()` | 阻塞连接：置 `_initialized=true` | `State=Connected` + `SetPhase(Standby)` |
| `InitializeOff()` | 阻塞断开：清 `_initialized` | `State=Disconnected` + `SetPhase(Uninitialized)` |
| `ConnectOn()` | 非阻塞：置 `_initialized=true` | `State=Connected` |
| `ConnectOff()` | 非阻塞：清 `_initialized` | `State=Disconnected` |
| `ResetProcess()` | 线性阻塞链：`ClearStatus()` → 置相位 Standby | `WeldStatus=Standby` |
| `ClearStatus()` | 状态清理：清标志位 + `AdvanceStep(StepIdle)` | `WeldStatus=NoReset` |
| `ResetWorkTime()` | `ResetStepTime()`（基类） | — |
| `WeldStatusTrans()` | `WeldStatus==NoReset` return；否则 `SetWeldStatus(MapWeldStatus(_phase))` | — |

---

## 配置项（`ConfigFileName = "LaserWeldHeadWorkflow"`）

| 配置元素 | 默认值 | 说明 |
|---|---|---|
| `TimeOutSeconds` | 30 | 基类超时阈值（秒） |

`LoadConfig` / `SaveConfig` **无参**，走 `XdocumentReaderWriter`（XML 文件 `Config/LaserWeldHead/Workflow_XML/LaserWeldHeadWorkflow.xml`）；`SaveConfig()` 末尾 `Config.SaveXdocument()` 落盘（裁定 D1）。温度阈值等参数待落地后逐项读取/保存（`// todo`）。

---

## 可观测性

`GetStepName` 按**私有相位**（非执行步号）返回：`待机` / `工作中` / `异常终止` / 其余 `未初始化`——骨架期执行步不推进，可观测性以相位为准。

`SubDeviceLog()`（C7 契约）：输出 相位/连接态/焊接过程态（温度日志 todo）。

---

## 在工作流体系中的角色

- 由 `DeviceControlWork` 上电初始化（`InitializeOn`）与整机编排驱动 `FlowProcess()`。
- 连接态经 `SubDeviceState`（2 态）承载；本工作流**无主设备运行态**（`MainDeviceStatus` 仅 `DeviceControlWork` 持有）。
- 硬件（`ILaserWeldHeadController`）接入后落地 R009 温度阈值监控与真实连接/断开逻辑。

---

## 用法示例

```csharp
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;

var head = LaserWeldHeadWorkflow.Instance;
head.ConnectOn();                              // 受理连接（上电初始化由 DeviceControlWork 级联）
SubDeviceWeldStatus s = head.WeldStatus;       // 焊接过程态（对外只读）
string status = head.StateName + " / " + head.WorkStepName;
```

---

## 关联

- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（§4 契约 · §5 RunStep 驱动 · §16 模板）
- [[modules/MotionControl]] — 焊接头从站设备 `WeldHeadSlaveDevice`（ADR-012 起归运控模块）
- [[decisions/ADR-030-WeldHeadSlaveDeviceUnderMotionControl]] — 焊接头从站设备裁定
- [[decisions/ADR-013-ThreeStateModelRefactor]] — 三态模型（现行有效）
- [[decisions/ADR-035-RawDesignRefinement20260903]] — 原档细化与完全重构裁定

## 设备归属与流程归属修正（2026-11-05，ADR-082/063 演进）

> **归属裁定**：焊接头从站（自动对焦电机 + 振镜）流程归本类；**TA（送丝即 TA）与 Y 轴**流程归 [[api/MotionControlWorkflow]]（仅两轴，⛔ 无第三个「送丝轴」）。
> 硬件连接、轴对象、配置、使能、SDO、回零状态一律在 [[api/MontionManager]]（含焊接头从站设备 `WeldHeadSlaveDevice`）。

| 指令 / 成员 | 2026-11-05 前所在 | 现在所在 | 处理方式 |
|---|---|---|---|
| `TaAuto` / `TaBreak` / `TaPose1` / `TaPose2` / `TaRetract` / `TaZeroPose` | 本类实现 | `MotionControlWorkflow` 实现 | **2026-11-06 薄转发壳已整体删除（ADR-092）**：本类不再有同名方法，全库唯一入口 = `MotionControlWorkflow`（`TaRecheck` 早已更名 `TaRetract`） |
| ~~`CancelTaZeroPose`~~ | 本类实现 | 已于 2026-11-09 **整个删除** | 全库无此接口（ADR-094 D4）；TA 指令只响应急停 / 停止两类外部终止，ZeroPose 等待由 `StopAxis` 的单轴取消打断 |
| `TaTorqueActive` / `TaBreakHoldMm` / `TaBreakHoldValid` | 本类 | `MotionControlWorkflow` | 已移除本类成员，UI 改读流程层 |
| `LaAuto` / `LaSpot1` / `LaSpot2` / `LaPose1` / `LaPose2` / `LaMoveTo*` | 本类 | 本类（不变） | 直接保留 |
| `GalvoHome` / `GalvoDemo` / `ApplyGalvoCenterOffset` / `ApplyGalvoAmplitude` | 本类 | 本类（不变） | 直接保留 |
| 焊接头从站温度 / IO / 报警（`LastTemperature` / `LastAlarmStatus` / `IsTemperatureAlarm`） | 本类 | 本类（设备层，不随 TA 迁移） | 直接保留 |
| `LaReady` / `LaGateReason` | — | 本类新增（委托 `MontionManager` 从站状态） | UI 三区取值来源之一 |
| `IsEnabled` / `IsHomed` / `IsAtWorkZero` | — | **ADR-098**：TA 轴分层就绪——使能 = `TaMotionReady`；回零 = `TaHomed`；工作零位 = `TaAtWorkZero`（⛔ 2026-11-17 改版：原误用 `TaAvailable`，L4 与「指令可执行」已解耦） | 需回零轴，使能后 L2、回零后 L3 |

- **LA 随动补偿**改为读 `MotionControlWorkflow.Instance.TaPositionMm`（不再持私有 `TaAxis`），TA 位置语义只由流程层暴露。
- **⛔ 单实现纪律**：本类不得再出现 TA 的 `CheckTaAvailable` / `TaMoveTo` / `TaZeroPoseWorker` 等实现体。

## 摆焊输出门禁（2026-11-17，阶段 7 / ADR-104）

| 项 | 契约 |
|---|---|
| 门禁 | `ApplyGalvoAmplitude` 只在 `WeldStatus == Working` 时读 `WeldParamControlWorkflow.LastOutput`，否则视为无输出 |
| 报警停焊 | 非焊接态（含 `ErrorAborted`）幅值归零、`GalvoEnable = false`，执行器停摆，不沿用旧自适应摆幅 |
| 载荷关系 | 本类只停本地执行器；RSI 的 `WeaveAmp` 载荷由 [[api/WeldParamControlWorkflow]] 停止刷新即冻结，二者不互相覆盖 |
| 下发频次 | 幅值/频率/中心变化才重发，避免逐拍刷从站总线 |
| 关联 | [[decisions/ADR-104-rsi-channel-payload-freeze-alarm-stop]] · [[api/WeldParamControlWorkflow]] |

## 焊接头手动动作统一门禁（2026-11-17，ADR-100 D29）

**新增** `EnsureManualWeldHeadActionAllowed(string actionName, out string reason)`：

- 判据唯一来源 = `DeviceControlWork.Instance.IsAutoWeldingRunning`（主设备级权威）。
- 自动焊接流程进行中 ⇒ **拒绝**一切焊接头手动动作（LA 对焦电机 / GA 振镜），拒绝原因同时进日志。
- 覆盖入口：`LaAuto` / `LaSpot1` / `LaSpot2` / `LaPose1` / `LaPose2` / `GalvoHome` / `GalvoDemo`。
- ⛔ `GalvoDemo` 原用 `DeviceControlWork.IsWelding` 判定（覆盖整段开机期、过宽）⇒ 改用统一门禁。
- 系统设置页直接写从站的 LA/GA 操作（电机使能 / 位置下发 / 振镜使能 / 振镜回零）也必须先过本门禁。
- 关联：[[decisions/ADR-100-state-union-and-action-gate]] · [[api/SystemControlPage]]
