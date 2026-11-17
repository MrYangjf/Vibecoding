---
title: "ADR-057 TA/LA 动作指令与 auto 随动（力矩下压/锁止/预设位 · 光斑-偏移双曲线随动 · 限位报警归安全线程）"
date: 2026-10-09
updated: 2026-10-14
tags: [ADR, TA, LA, 力矩, 随动, 光斑, 激光头工作流, MotionControl, P3]
status: accepted
---

# ADR-057：TA/LA 动作指令与 auto 随动

> ⚠️ **2026-10-14 部分换轨（[[decisions/ADR-067-LATaSettingsSemanticRework|ADR-067]]）**：LA 三指令语义已重写——LA_Pose 纯到位 / LA_Spot 设定光斑（曲线A 反查定位后**退出随动**）/ LA_Auto 先定位再持续随动（失败即止）；本页「LaSpot1/LaSpot2 按钮直发 + Auto 按拍随动」的动作按钮形态随 LA 参数区重构退场（快捷 Radio 指令链保留），TA 侧语义不变。现行语义以 ADR-067 为准。
> P3 功能实现批E（F-1 TA 力矩控制与动作指令 + F-2 LA 动作与 auto 随动）的落地裁定。
> ⚠️ **编号注记**：P1 §4.3 曾预测「需求 33（光丝对中阈值）归 ADR-057」——实际 073 由本页占用（编号以 [[decisions/ADR-Index]] 为唯一准绳），需求 33 的 ADR 顺延取号；温控占位 **ADR-058** 不变。

## 演进

- **2026-11-02 TA 力矩模式运行期开关**：系统设置页 TA 区新增 `swTaTorqueMode`（默认开，文案「力矩模式：开/关」），
  状态落到既有门 `DeltaAxisConfig.TorqueModeEnabled`（`TaAuto` 判据），页面统一经
  `MontionManager.TaTorqueModeEnabled` / `SetTaTorqueMode(bool)` 读写（页内不写轴控制代码）；
  **仅运行期态不落盘**（避免与轴配置 XML `TORQUE_MODE` 双真相源，并保证「加载后默认开启」）；
  可用性随 `IsMotionReady() + TA 轴存在` 由 `timerRefresh` 统一同步，未连接置灰、已选值保留。
- **2026-11-02 晚 力矩模式语义对齐（业主澄清，覆盖上条的「独立开关」语义）**：
  **力矩模式 = 由指令决定的轴模式**，不是可长期独立保持的开关。
  - 轴默认配置 = 力矩控制模式（对应进入 `TA_Auto`）；`TA_Auto` 执行期间即力矩生效。
  - 系统设置页 **使能 / 前进 / 后退** 等手动轴操作 = 电机退出力矩控制 ⇒ 自动置关，且 `TA_Auto` **不可用**（置灰 + 拦截，有明确日志）。
  - **Break / Pose1 / Pose2 / Retract** 等其它 TA 指令 = 其它模式 ⇒ 同样置关。
  - 单一真相源 = `MontionManager.TaTorqueModeEnabled`（读）/ `SetTaTorqueMode(bool, reason)`（唯一写口），落 `DeltaAxisConfig.TorqueModeEnabled`；
    **手动操作在 `MontionManager` 六个轴控制函数内统一 `ExitTaTorqueMode`**；非 Auto 指令在 `LaserWeldHeadWorkflow` 各入口统一退出；
    `TaAuto()` 的门与 UI 可用性读**同一状态位**（避免 UI 可点、底层必败）。
  - 默认值来源 = 轴配置 XML `TORQUE_MODE`（`DeltaMotionConfig.ReadAxis` 对力矩类轴缺省 TRUE），⛔ **不由 UI 初始化硬赋**。
- **2026-11-03 「启动后 TA_Auto 灰」可用性修复（业主报告）**：
  **根因 = UI 首填时序，不是力矩位/轴对象丢失**。`ProcessControlPage` 构造函数与 `Load` 事件均早于
  `DeviceControlWork` 的初始化线程，`RefreshActionStates()` 在 `MontionManager.IsInitialized=false` 时把
  `taTorqueReady` 判假并清掉 `ApplyDefaultCommandModes()` 刚设的 `radioQuickTaAuto.Checked`；
  运控连上后即使 `Enabled` 放开，Auto 仍显示未选中（灰），且页面无「初始化完成」首填入口。
  运行期探针（真实 XML）证明配置侧全部正常：`TaAxisName=送丝力矩电机`、该轴 `Enabled=True`、`Torque=True`
  ⇒ **送丝力矩轴就是 TA 轴**，`TaTorqueModeEnabled`/TA 轴判定均解析到同一根轴。
  - 修正 1：`RefreshActionStates` 只在 `taReady && !taTorqueMode` 时清残留选中态；未就绪期保留默认 Auto 选中。
  - 修正 2：`taReady` 改用 `GetAxisByKeys(TaAxisKeys)`，与 `TaTorqueModeEnabled` 同一解析路径。
  - 修正 3：订阅 `DeviceControlWork.Instance.InitializationCompleted` 做**初始化完成后首填**；订阅
    `MontionManager.TaTorqueModeChanged` 做运行期跨页同步（系统设置手动轴操作/Break·Pose 置关立即传导）。
  - 修正 4：`TA_Auto` 门状态变化更新 Tooltip 并 `ShowLog`：「因已退出力矩模式，TA_Auto 不可用」；恢复力矩模式时同样提示。
  - 安全门不放宽：`IsInitialized=false`（未连接）或 TA 轴对象缺失时仍必须置灰。

## 背景

需求 15/17/18/19/20/21/22/38/41（第一次评审 41 条）要求：
**TA**（送丝Z轴，台达伺服力矩模式）四类功能——auto 设下压力、位置设置、当前位置锁止、位置上下限报警（全模式）；
**LA**（焊接头从站步进电机）三类功能——光斑大小设置、位置设置、auto 随动；
两组动作指令（TA auto/break/Pose1/Pose2；LA auto/Spot1/Spot2/Pose1/Pose2）。
S-4/S-5 已铺好底层（`SetTorque`/`StopTorque` 0 消费者；`TaLaCurveConfig` 采样点表），缺动作入口、随动消费链与报警链路。

## 决策

### 一、动作指令承载 = 激光头工作流（非阻塞动作指令区）

需求 38/41 明确「**激光头工作流&TA和LA算法**」⇒ 9 个动作方法落
`MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` 的「非阻塞动作指令」region（ADR-041 范式），
P4（U-1/U-2/U-5 按钮组）只做 UI 绑定。动作模式用 **bool 标志**（`_taTorqueActive`/`_laFollowActive`）表达，
⛔ 不建动作模式枚举（ADR-055「工作流零自建状态枚举」）；只读属性 `TaTorqueActive`/`LaFollowActive`/`TargetSpotMm` 供 UI 显示。

### 二、TA 力矩语义

| 动作 | 实现 | 依据 |
|---|---|---|
| **TA auto（设下压力）** | `SetTorque(TaForceN→额定千分比, TorqueSlope)` → 三步 CST（`Set_MoveMode(10)`→`CST_Start_Move`→`CST_Output_Enable(1)`）；2026-11-03 起参数取工艺 `TaForceN` + 轴 `TORQUE_SLOPE`，下发前拦截 0/越界/伺服未就绪/回零进行中/模式回读失败；`MontionManager.TaTorqueModeEnabled=false`（非力矩模式）拒绝执行 | 需求 38「力矩模式控制向下的压力」 |
| **TA break（停止并锁存位置）** | **业主 2026-10-09 裁定**：手动力矩调试中（工件推轴回退 / 力矩压轴前进）点 break，轴**停止并保持在发命令时刻的位置，撤掉工件轴不会移动** ⇒ 实现 = 锁存当前反馈位 → `StopTorque()`（撤 CST 输出）→ `AbsMove(锁存位)`（CSP 位置保持）；**仅 auto 力矩输出态生效**；2026-11-02 起入口先 `SetTaTorqueMode(false)`（视作其它模式） | 需求 17/18 + 业主裁定 |
| **TA Pose1/Pose2（位置设置）** | `AbsMove(posMm)` 位置模式直达（同时退出力矩态）；2026-11-02 起入口先 `SetTaTorqueMode(false)` | 需求 19「锁定 TA 在一个位置观察光斑和丝」 |

✅ **原真机验证项 ① 已解决（2026-10-09 业主裁定）**：break 语义 = **停止 + 位置保持**（不是自由浮动、不是纯撤力矩）。
~~原实现仅 `StopTorque()`（备选：`SetTorque(0, Slope)` 平滑归零 / 切 CSP 保持）~~ 已改为「锁存位置 + 撤力矩 + 位置保持」双动作。
> ⚠️ 上机核实点并入验证项 ②：`StopTorque` 与 `AbsMove` 连用时 CST→CSP 模式切换是否需显式 `Motion_Set_MoveMode`。
⚠️ **真机验证项 ②**：CST 与 CSP 之间切换是否需显式 `Motion_Set_MoveMode`（API 清单 :87）——现按
`CST_Start_Move`/`AbsMove` 各自入口隐含切换实现，上机核实。

#### 2026-11-03 现场修订：4609 与回零前置

- **现象**：`17:24:46 送丝力矩电机 扭矩参数下发 失败 错误码 4609 描述（空）` + `TA auto 力矩指令下发失败`。
- **定性**：`4609 = 0x1201 ERR_ECAT_API_PARAMETER`（本地 `raw/delta/EtherCAT_DLL_Err.cs`），由 `CST_Start_Move` 参数非法触发，**不是回零/模式冲突**。现场证据：运行期 `TA_FORCE_N=0`（`WeldParamControlAlgorithm.ini`）与 `TORQUE_SLOPE=0`（`DeltaMotionConfig.xml`），二者同时为 0 直送接口。
- **处置**：① CST 下发前三步前置（参数/伺服状态/回零 active/模式回读），失败打印中文原因并 `RestoreCspMode()`；② `StartHome` 补伺服已使能、`Home_Status≠1`、速度与加速度 > 0 三项前置，并在日志打印模式/偏移/双速/加速度实际值；③ 单位口径保留「力值直送额定千分比」，待力→扭矩换算依据补齐（见 [[guides/DeltaEtherCAT-DevGuide#待补清单本地原始手册缺失项]]）。
- **未解决（不得默认正确）**：回零模式 4 的 DI/index/超时要求、`Curve_Mode` 取值、CST 扭矩量纲，本地无台达手册原文，均已登记待补。

### 三、LA 随动与光斑（双曲线合成，无自创公式）

统一公式（需求 41 两条逻辑的合并表达）：

```
LA目标 = QueryLaPositionMm(目标光斑) ← 曲线A 反查（TA=0 时的基准位）
 + QueryLaOffsetMm(TA当前位置) ← 曲线B 正查（随动偏移补偿）
```

| 动作 | 行为 |
|---|---|
| **LA auto（随动）** | 按拍读 TA 反馈位置 → 上式 → `SetMotorPosEnable(target, true)`；**0.01mm 死区**才下发（防逐拍刷从站总线），随动步不逐次记日志（防刷屏） |
| **LA Spot1/Spot2（设光斑）** | 更新目标光斑（预设键）→ 曲线A 反查基准 → **按当前 TA 位置推算并下发**（需求 22） |
| **LA Pose1/Pose2（位置设置）** | 直达毫米位，不经曲线，退出随动 |

- **TA=0 时偏移为 0**（曲线B 锚点），公式退化为纯曲线A 反查 —— 需求 41 逻辑2 自动满足。
- 曲线实例只经 `WeldParamManager.TaLaCurve` 唯一口（ADR-053）；⛔ 无解析式推导。
- 随动步挂入 `FlowProcess` 三步环（待机→振镜下发→LA 随动→待机），case 内无阻塞（ADR-041）。

### 四、TA 位置上下限报警（全模式）归安全线程

`DeviceStatusWork.IOWork` 新增 `ScanTaPositionLimit()`（仿 `ScanMotionBusFault` 边沿范式）：
限值**复用轴配置软限位** `PositiveLimit`/`NegativeLimit`（0=不启用，不另设报警键）；
超限升沿 → `DeviceControlWork.ReportAlarm(reason)`，回限内降沿 → `ReportAlarmCleared()`。
落安全线程的两个理由：① ADR-017「Safety/IO/status 归 DeviceStatusWork 三线程」；② 工作流 `FlowProcess` 受 `IsEnable` 门控，
不满足需求 18「**所有模式下均触发**」，而 IO 线程无条件常驻。

### 五、轴名配置键（防硬编码）

`DeltaMotionConfig.TaAxisName`（四点闭环：属性/默认/Load/Save，`ROOT/TA/TA_AXIS_NAME`，默认 `"送丝力矩电机"`）——
沿 `SeamTrackAxisName` 范式。依据 [[lessons/SimulationAutoBranching]]：轴名硬编码曾致功能静默失效。

### 六、动作预设值归工艺配置

7 键入 `WeldAlgorithmsConfig` PROCESS_CONTROL 段（INI 四点闭环）：
`LA_SPOT_TARGET_MM`（0.6，补 P1 §3.2 规划欠账）· `LA_SPOT1_MM`（0.6）/`LA_SPOT2_MM`（1.0）
`TA_POSE1_MM`/`TA_POSE2_MM`/`LA_POSE1_MM`/`LA_POSE2_MM`（默认 0，现场示教后经 UI 保存）。
与 `SPOT_CALIB_POS_MM` 等快捷调试目标位同段同范式。⚠️ Pose 默认 0、Spot2 默认 1.0 为占位初值，待现场标定。

### 七、S-5 曲线骨架缺陷同批修复（F-2 消费前必修）

`TaLaCurveConfig.Interpolate` 三处：① 反查（invert）域上下界**颠倒**（`lo=末点.Y/hi=首点.Y`）⇒ 域内值恒被判域外钳到首点；
② 正查域上界误取 `末点.Y`（应为 `末点.X`）；③ Clamp 两端均返首点（高端应返末点）。
另：**单点内置锚点组按「默认 1:1 线性外延」**（过锚点斜率 1，P1 §3.3 明文），Reject 策略下仅锚点值有效。
外部多点表仍按 `Extrapolation` 策略（Clamp 端点钳位 / Reject 拒绝）。

## 备选方案

| 备选 | 放弃原因 |
|---|---|
| 动作逻辑放 `DeviceControlWork` | 需求 38/41 明文「激光头工作流」承载 TA/LA 算法；工作流已有「非阻塞动作指令」区 |
| 动作模式建枚举（Auto/Pose1/…） | ADR-055 零自建状态枚举；bool 标志足够支撑 break 门控与 UI 显示 |
| 限位报警放工作流按拍检查 | 违反 ADR-017 安全检查归口；且 `FlowProcess` 受 IsEnable 门控不满足「全模式」 |
| 限位另设报警阈值键 | 轴配置软限位已是同一物理量，双键必漂移 |
| break 用 CSP 保持当前位置 | 与「锁止为**力矩**锁止」字面不符；列为真机验证备选 |

## 后果

### 正面
- F-1/F-2 业务闭环：`SetTorque`/`StopTorque` 零消费者标记解除；曲线查表（`QueryLaPositionMm`/`QueryLaOffsetMm`）有了消费链
- 随动/Spot 共用同一公式，TA=0 特例自动成立；UI（P4）只绑按钮不带业务逻辑
- 限位报警复用软限位配置，零新增键；边沿触发不刷报警流

### 负面 / 待验证
- break 锁止硬件效果、CST↔CSP 模式切换两项待真机核实（见决策二）
- 9 个动作方法暂 0 UI 消费者（P4 U-1/U-2/U-5 绑定）；`QuerySpotMm` 仍 0 消费者（曲线A 正查，预留）
- 随动按拍下发受工作流节拍（三步环）约束，快速大幅 TA 移动时跟随粒度 = 3 拍周期

## 相关页面

- [[decisions/ADR-053-TaLaCurveAndMotorScale]] —— 曲线与量纲定义权（本 ADR 为其消费方落地）
- [[decisions/ADR-030-WeldHeadSlaveDeviceUnderMotionControl]] —— LA 归从站电机对象
- [[decisions/ADR-041-ResidentFlowNonBlockingParadigm]] —— 动作指令区范式
- [[decisions/ADR-017-SafetyCheckConsolidation]] —— 限位报警归安全线程
- [[decisions/ADR-055-SubFlowStateEliminationAndParamClassRelocation]] —— 零自建状态枚举
- [[api/LaserWeldHeadWorkflow]] · [[api/MontionManager]] · [[api/DeviceStatusWork]]
- [[lessons/SimulationAutoBranching]] —— 轴名禁硬编码
- [[project/ReviewOptimization-P1-StructureDesign]] —— 需求与控件归属（U-1/U-2/U-5）
