---
title: "ADR-082 TA 轴初始化四步与可用性降级门禁（整合旧 083（TA 力矩模式门禁删除））"
merged_from: [ADR-083]
date: 2026-11-05
updated: 2026-11-17
tags: [决策]
status: proposed
---

# ADR-082 TA 轴初始化四步与可用性降级门禁

> **决策一句话**：TA 初始化四步（加载轴与 XML → 配置读-比对-写 → 成功才使能 → 使能后走工作零位），任一环失败 → TA 指令全降级拒绝

## 背景

业主明确 TA 初始化四步（加载轴与默认 XML → TA 配置读-比对-写 → 配置成功才使能 → 成败反馈与降级为 Null），并追加第 3 步下半段：
使能成功后自动执行 `TA_ZeroPose`（工作零位）。改前缺口：初始化期不比对驱动器值、使能不看配置结果、五个 TA 指令无统一可用性门禁，
且「工作零位」与「回零 Home」概念未分离，配置失败仍可下发力矩。

## 决策

1. D1 第2步只对可落盘且可比对的 P1.087(16#2157)/P1.088(16#2158) 做读-比对-写，无差异不写，日志逐项给出参数名/当前值/目标值/判定；两参数为 0 视为未配置且按成功
2. D2 第3步在 DeviceControlWork.InitStepEvaluate 先调 LoadTaAxisConfig 再 EnableAxesAfterInit；配置失败则该 TA 轴跳过使能
3. D3 新增 MontionManager.TaAvailable/TaDegradedReason 作为唯一状态位（=配置加载成功 + TA 轴已使能 + **TA_ZeroPose 已到位**），LaserWeldHeadWorkflow 全部 TA 入口前置拒绝
4. D4 使能成功只代表 TA 指令可用，TA_Auto 仍只由操作员点击触发，初始化流程不自动下发力矩（安全红线）
5. D5 回零模式/寻找速度/爬行速度/加速/偏移不在初始化落盘，仍由 Home_Config 每次回零逐次下发，6098/6099/609A 链路不改
6. D6 **TA_ZeroPose ≠ Home**：TA 轴为绝对编码器、掉电保留位置，工作零位只走 CSP 绝对定位（`AbsMoveNoBlock` posMode=1），
   到位判定 `|当前位置 − TA_HOME_ZERO_POSE_MM| ≤ TA_HOME_ZERO_POSE_TOL_MM`；⛔ 初始化链无任何 `Home_Move`/`Home_Config`，⛔ 不以 `Home_Status` 作前置门禁
7. D7 工作零位参数独立键 `TA_HOME_ZERO_POSE_MM / TA_HOME_ZERO_POSE_VEL / TA_HOME_ZERO_POSE_TOL_MM`（缺键默认 0 / 1.0mm/s / 0.1mm），
   界面入口放系统设置 → TA 轴「参数」弹窗（与回零六参同区，便于一眼确认「工作零位≠回零」），落盘 `ROOT/TA_HOME`
8. D8 自动动安全约束：仅使能成功后执行；移动前校急停/总线 OP/无报警/OperationEnabled；已在容差内 → 打印「已在工作零位，跳过」；
   超时（距离/速度×3，下限 10s、**上限 60s**）或位置连续 5s 无变化 → 判失败、减速停止、TA 降级并打印「TA_ZeroPose 失败 → TA 功能降级」
9. D9 `TA_ZeroPose` 作为 TA 指令区 radio 组一员（`radioQuickTaZeroPose`，与 Auto/Break/Pose1/Pose2/Retract 互斥）：
   切走时 `CancelTaZeroPose` 立即减速停止；从 Auto 切 ZeroPose 先 `StopTorque` 撤力矩；ZeroPose 自身不受到位条件限制（降级后可重试）

## 备选方案

- 复用 `Home()` 作为工作零位：被否，绝对编码器轴无需回零，且会改写 6098/6099/609A 现场参数。
- 以 `Home_Status` 作到位判据：被否，绝对位置有效即可比较，回零状态会误卡定位。
- 把 ZeroPose 目标放进 `WeldParamManager` 工艺参数：被否，属驱动器/轴配置语义，与回零六参同源更安全。

## 后果

### 正面
- 初始化链每一步都有明确产物与可读日志；失败即降级，不会「半可用」下发力矩。
- 工作零位与回零彻底分离：日志文案、状态位、参数键、接口路径均不重叠。

### 负面
- 初始化时间增加一次定位（已完成在容差内则跳过）。
- 工作零位失败后需操作员手动点 `TA_ZeroPose` 重试才能恢复 TA 指令。

### 2026-11-17 · 决策 D26 · TaAvailable 语义改为已使能+已回零；工作零位到位拆为 TaAtWorkZero 观测位
- **变更**：TaAvailable 语义改为已使能+已回零；工作零位到位拆为 TaAtWorkZero 观测位
- **理由**：位置类指令需要的是位置可信（已回零），不是已到工作零位
- **影响**：TA 指令门禁放宽；IsAtWorkZero 改读 TaAtWorkZero；L4 与指令可执行解耦

### 2026-11-17 · 决策 D30 · TA_Zero 与其它 TA 指令同口径：一律要求已使能+已回零
- **变更**：TA_Zero 与其它 TA 指令同口径：一律要求已使能+已回零
- **理由**：未回零时位置不可信，工作零位定位同样不可信；此前 ZeroPose 只查已使能
- **影响**：ExecuteTaZeroPose 前置改 CheckTaAvailable；删 CheckTaMotionReady（改后零消费）与「未回零只告警」块；GetTaGateReason 不再按指令放宽

## 合并自 ADR-083 · TA_Auto 自切模式并删除力矩模式门禁

> 2026-11-17 治理轮合并：原页为独立 ADR-082，其现行裁定收归本页；原页文件已删除（**编号不回收**，废止号不复用）。原页的验证过程叙事已按格式契约 R2 剥离至 `logs/log.md`。

**原页决策一句话**：删除「先开力矩模式才能用 TA_Auto」的专用开关，把 CSP→CST→输出使能收进 TA_Auto 自身，可用性只由 TaAvailable 决定

### 原页决策条目

1. D1 删除系统设置页「力矩模式」开关：`SystemControlPage.Designer.cs` 的 `swTaTorqueMode` 字段/实例化/控件挂载/属性块，
   `SystemControlPage.cs` 的 `_syncingTaTorqueMode`、`LoadTaTorqueMode`、`RefreshTaTorqueModeAvailability`、
   `SwTaTorqueMode_CheckedChanged` 及构造/计时器接线一并删除
2. D2 删除门禁语义：`MontionManager` 不再暴露 `TaTorqueModeEnabled`（TA 侧） / `SetTaTorqueMode` / `TaTorqueModeChanged`；
   新增 `ExitTaTorque(string reason)` 只做「撤 CST 输出 → 回 CSP」，⛔ 不承担任何可用性判定
3. D3 `TA_Auto` 可用性唯一口径 = `MontionManager.TaAvailable`（配置加载成功 ∧ TA 轴已使能 ∧ `TA_ZeroPose` 已到位）；
   `ProcessControlPage.RefreshActionStates` 与 `UpdateTaAutoGateHint` 只按该口径置灰/提示，Break/Pose/Retract **不得**再置灰 Auto
4. D4 `TA_Auto` 入口自切模式（沿用 `DeltaMontionAxis.SetTorque`，不另写一套）：
   `Set_MoveMode(CST=10)` 且**回读模式字 == 10** → `CST_Start_Move(目标扭矩, 扭矩爬升速率, 曲线=1)` →
   `CST_Output_Enable(1)`；任一步失败 `RestoreCspMode()` 回滚 CSP，可立即重试。
   **2026-11-06 被 [[decisions/ADR-087-TaCstEntryRampAndNoPositionResidual]] 取代**：冷启动改为
   「停稳位置运动 → 切 CST → ±1‰ 方向种子 → 开输出 → 再下发目标与 slope」，热切换直接重发目标
5. ~~D5 复用判定（避免重复切模式）为三条件 AND：运行期 `_torqueOutputEnabled` ∧ `GetMoveMode() == CST` ∧
   本次目标扭矩与扭矩爬升速率 == 上次成功下发值。`StopTorque`/`RestoreCspMode` 三者清零，回滚路径**不绕过**、也不会被误复用~~
   → **2026-11-06 已删除**：复用捷径会让 `TORQUE_SLOPE` 改小后仍沿用旧斜率，由 ADR-087 改为「任何进入力矩出力的路径都重新下发目标与 slope」
6. D6 保留语义：`Break`/`Pose1`/`Pose2`/`Retract`/`ZeroPose` 与手动轴操作进入时仍撤 CST 输出并回 CSP（收力与换模式必要），
   仅改变设备力矩输出态（`DeltaMontionAxis.TorqueOutputEnabled`），不影响 `TaAvailable`
7. D7 XML 键 `TORQUE_MODE` 与 `DeltaAxisConfig.TorqueModeEnabled` **保留**：送丝轴 `SetWireFeedTorque` 仍消费该位，
   CSV 导入导出（`MotionConfigImporter`）与现场既有 XML 依赖该键；`ChildValueAny` 缺键默认 FALSE，旧 XML 可正常加载。
   TA 侧不再读写该位，因此不构成「写进 XML 但没人读」的死配置
8. D8 互斥与顺序：切到 `TA_Auto` 先 `CancelTaZeroPose` 停掉 ZeroPose 运动，再切 CST；切走 Auto 先 `StopTorque` 撤扭矩；
   `TaZeroPose` 自身先撤力矩再走工作零位。日志统一写明「先停 X → 再进 Y」

### 原页背景

业主提出两条：①删除系统设置页的「力矩模式」专用开关；②修复「用过 Break/Pose/Retract 后 TA_Auto 变灰不可用」。
二者本质是同一件事——把模式切换从「操作员前置动作」收回到指令内部：点 `TA_Auto` 时由指令自己切 CST 并开输出。

改前实现把「是否允许力矩」做成一个 UI 开关（`swTaTorqueMode`）+ 一份内存轴配置位（`TaTorqueModeEnabled`），
并让 Break/Pose/Retract/ZeroPose 与六个手动轴操作统一调 `SetTaTorqueMode(false)`。于是「收力」这一必要动作
被误当成「关闭可用性」，Auto 被置灰且选中态被清除，操作员必须回系统设置重新打开开关才能再次使用。

### 原页后果

### 正面
- 操作员只需点 `TA_Auto`，不再需要「先去系统设置开力矩模式」；Break/Pose/Retract 后 Auto 立即可用。
- 可用性只有一个真相源（`TaAvailable`），UI 不再因「收力」被降级。
- 模式切换、失败回滚、复用判定都在轴层单点实现，日志可读（含模式字回读与复用原因）。

### 负面
- 首次进入 Auto 多一次模式切换（约一次 SDO 往返）；参数未变时靠复用规避。
- 现场旧习惯「先开力矩模式」失效，需在培训/验收说明中更新操作步骤。


## 相关页面

- [[decisions/ADR-Index]]
- [[api/MontionManager]]
- [[lessons/ConfigZoneSaveWiring]]

## 演进记录

### 2026-11-05 初始化静默使能与 ZeroPose 前置修正（现场故障）

- **现场现象**：日志停在「初始化第2步 TA 轴配置加载完成，进入第3步使能」后无任何使能日志、轴未使能；界面 `TA_Auto` 已选中并提示「正在执行 TA_ZeroPose」，其它 TA 指令永久被拒。
- **根因（逐条对应代码）**：
  1. `DeviceControlWork.InitStepEvaluate` 写成 `bool servoReady = allReady && EnableAxesAfterInit();`——`allReady=false` 时右侧被 `&&` 短路，「进入第3步」日志却在短路之前打印 → 静默。
  2. ZeroPose 自动调用藏在 `MontionManager.EnableAxesAfterInit` 末尾，使能未跑 → ZeroPose 未跑 → `_taZeroPoseDone=false` → `TaAvailable=false` → 其它 TA 指令被 `CheckTaAvailable` 永久拒绝；界面提示实际是 `TaReasonZeroPoseNotDone` 文案，不是运行态。
  3. `ProcessControlPage.RefreshActionStates` 用 `MontionManager.IsInitialized`（仅控制器初始化）冒充整机初始化完成，并打印「TA_Auto 已恢复可用」。
  4. `LaserWeldHeadWorkflow.TaZeroPose` 的 `worker.Start()` 无 `try/catch`，线程启动失败时运行标志泄漏。
- **决策修订**：
  1. 新增唯一初始化闸门 `MontionManager.IsInitCompleted`（`MarkInitCompleted(bool)` 由 `InitStepEvaluate` 收尾调用一次）；初始化完成前任何指令 radio 点击不执行、不弹确认、不启动检测线程、不启动 ZeroPose。
  2. 第 3 步使能必须「有声」：`初始化第3步 开始使能（逐轴）` → 每轴成功/失败（失败带 `LastCommand` 与状态字）→ `初始化第3步 使能完成 成功 N 轴 失败 M 轴` → `初始化第3步 结论 …`；删除 `allReady &&` 短路，使能结果与 `allReady` 分开判定。
  3. ZeroPose 改由 `RunTaZeroPoseAfterInit()` 在「闸门已开 ∧ 使能成功 ∧ TA 配置成功 ∧ `TaMotionReady`」后启动；`RunTaZeroPose` 的运行标志与同轴单飞登记在 `finally` 清零，任何失败路径都不得堵死 TA 指令。
  4. 界面文案三态：等待初始化完成 / 已初始化但不可用（含 `TaDegradedReason`）/ 就绪；删除「已恢复可用」类提前宣告；三个指令区 tip 初始化未完成时统一显示「等待初始化完成」。
- **边界**：`TaAvailable` 判据（配置 + 使能 + ZeroPose 到位）不变；6098/6099/609A 零改动；`TA_FORCE_100PCT_N` 默认 37 不变；指令确认与上色逻辑仍走 `RunInstruction` 公共链路。

### 2026-11-05 按轴门禁与设备/流程归属分离（业主口径）

- **现场事实**：TA 使能成功、Y 使能失败（状态字 0x0000），旧实现以整机布尔一刀切 → TA `ZeroPose` 被跳过、TA 指令区被连带降级。
- **决策修订 D10 按轴就绪**：单一 `IsInitCompleted` 拆为「整机汇总 + 每轴独立就绪」——`YReady`（`SeamTrackYKeys`）/ `TaAvailable`+`TaMotionReady`（`TaAxisKeys`）/ `LaReady`（焊接头从站），
  每份含装载、使能、本轴初始化后动作、降级原因；**只有该轴自己的判定影响该轴指令区**。
- **决策修订 D11 ZeroPose 与 Y 无关**：TA 配置 ∧ TA 使能 ∧ TA 可动即执行 `TA_ZeroPose`，成功后 TA 区放行，⛔ 不再因 Y 失败跳过。
- **决策修订 D12 汇总只展示**：结论行改为「整机初始化：部分完成（成功 N 轴 / 失败 M 轴：…）」；`InitializationCompleted` 订阅方（`FormMain` / `ProcessControlPage` / `SystemControlPage`）逐一核对后均非总闸。
- **决策修订 D13 日志按轴表达**：删除「闸门已打开 结果 失败」自相矛盾行，改为「Y 轴闸门：关闭（使能失败…）」「TA 轴闸门：打开（使能 + ZeroPose 完成）」。
- **决策修订 D14 失败可诊断**：`DescribeAxisDiagnosis` 串起总线状态含义、报警码、`ServoOn` 返回码 / `LastCommand`、从站是否发现与人话结论；⛔ 0x0000 官方定义未确证不得编造。
- **安全边界**：急停 / 总线非 OP / 驱动器报警 = **全局安全**（所有轴拒绝）；使能失败 / ZeroPose 未到位 = **按轴功能**（只关该轴）。

### 2026-11-05 闸门变化主动刷新与自动 ZeroPose 选中态（现场实测修订）

- **现场现象**：TA_ZeroPose 于 17:28:58 到位、闸门同时打印「TA_Auto 就绪」，但 `TA_Auto` 仍不可点；`radioQuickTaZeroPose` 未选中；点其它指令后才可执行。
- **根因 1（刷新链）**：页面只在构造、`StateSwitched`、`InitializationCompleted`、指令完成时刷新；初始化内部动作（逐轴使能、ZeroPose 完成/失败）**没有刷新触发点**，本次恰好在初始化末尾被 `InitializationCompleted` 兜住，其余场景（重试成功、单轴后补就绪）没有触发。
- **根因 2（假禁用）**：`ApplyDefaultCommandModes` 预选 `radioQuickTaAuto` —— 已选中的 Radio 再点击不产生 `CheckedChanged`，用户看到的就是「点不动」。点其它指令后 TA_Auto 被取消选中，再点才触发 → 形成「偶然修复」。
- **决策 D15 事件驱动刷新**：`MontionManager` 新增 `AxisReadinessChanged(axisName)` 与 `TaZeroPoseStageChanged`，在两个 workflow 上转发为 `AxisReadyChanged`（按 Y/TA 与 LA 过滤）；页面订阅后 `BeginInvoke` → `RefreshActionStates`，**⛔ 不用轮询 Timer**。
- **决策 D16 刷新幂等**：刷新只改 `Enabled` / 文案 / `Tooltip` / `BackColor`，不动任何 Radio 的 `Checked`，不触发指令执行；程序赋值一律走 `_suppressActionRadio`。
- **决策 D17 自动 ZeroPose 占选中态**：初始化内部执行的 `TA_ZeroPose` 开始时把 `radioQuickTaZeroPose` 置为选中（抑制事件），完成后保持选中并按结果上色；TA 区**不再预选 `TA_Auto`**（`_lastTaRadio = null`），消除假禁用。
- **决策 D18 可见兜底**：`VisibleChanged` 首次可见时刷新一次，避免页面构造早于初始化完成导致永久置灰。

### 2026-11-05 TA_Recheck → TA_Retract 语义重定义（⚠️ D20/D21/D23 已被现场否证，见下节）

- **决策 D19 指令更名与语义（有效）**：`TA_Recheck`（CSP 绝对定位回 0）更名为 **`TA_Retract`（回缩）**，语义 = `TA_Auto` 的相反动作——
  以 **CST 力矩反向出力**回缩，⛔ 不是 CSP 绝对定位到零。UI 文本 `TA_Retract`。
- **决策 D20 停机判据（❌ 已作废 · 2026-11-06 现场否证）**：~~起点取实测位置、终点 = `TA_HOME_ZERO_POSE_MM`，
  进入 `TA_HOME_ZERO_POSE_TOL_MM` 容差 → `StopTorque` 撤力 → `AbsMove` CSP 锁位~~。
  作废依据：现场日志「到位 当前 0.032mm 用时 3.0s / 撤力回 CSP 锁位 / 撤力回 CSP 达成」证明该判据把纯力矩输出变成了定位+撤力动作，
  与「Retract = Auto 反向」的业主口径相悖。
- **决策 D21 超时（❌ 已作废）**：~~回缩段超时 `clamp(5s, 行程/TA_HOME_ZERO_POSE_VEL×3, 60s)`~~。
  该动态放宽只为服务已作废的位置终点判定；现行只剩「力矩生效检测」一步，固定 `InstructionDetectTimeoutSeconds`（5s）。
- **决策 D22 回缩力来源（有效）**：复用 `WeldAlgorithmsConfig.TaForceN` 的**大小**、`TA_TORQUE_DIRECTION` **取反**的方向，
  换算仍走 `TA_FORCE_100PCT_N` 千分比；⛔ 不新增独立回缩力键、不改 `ConfigSelfHeal` 与参数弹窗布局。
- **决策 D23 方向保护（❌ 已作废）**：~~越过最接近零位点后偏差回升 >1mm 判失败（`InstructionRetractReverseGuardMm`）~~。
  该保护依赖位置终点判定，随 D20 一并删除；现行只保留 `SetTorque` 既有软限位前置检查与状态字/报警判定。
- **设施复用**：单飞 `TryBeginAxisInstruction("TA_Retract")`、力矩检测 `WaitTaTorqueOn`、5s 常量 `InstructionDetectTimeoutSeconds` 全部沿用。

### 2026-11-06 TA_Retract 收敛为「Auto 反向 · 纯力矩保持」（现场否证后重做）

- **决策 D24 语义定稿**：`TA_Retract` **就是 `TA_Auto` 把方向反过来**，其余一切同构——进入切 CST、开输出、按反向目标力矩持续出力，
  **保持出力返回**（不阻塞等位置、不驻留占轴、不自动撤力）。
- **决策 D25 禁止项**：⛔ 不设终点、⛔ 不判位置容差、⛔ 不做「回缩到位」、⛔ 不调 `StopTorque`、⛔ 不回 CSP、⛔ 不 `AbsMove` 锁位。
  `WaitTaRetractReach`、`CutTaTorqueAndLock`、`InstructionRetractReverseGuardMm` 全部删除。
- **决策 D26 退出方式**：与 `TA_Auto` 完全相同——由后续指令 / `ExitTaTorqueMode` / 急停等既有路径撤力回 CSP，⛔ 不给 Retract 单独造退出逻辑。
- **决策 D27 超时口径**：只保留「力矩生效检测」的固定 5s（`WaitTaTorqueOn`）；⛔ 删除按行程放宽到 21s/60s 的动态超时。
- **决策 D28 与 Auto 的唯一差异**：出力方向符号（`TryResolveTaTorque(..., reverse: true)`）与日志文案；
  单飞登记、伺服使能检查、`SetTorque` 调用、`WaitTaTorqueOn`、失败 `StopTorque` 收尾、`finally EndAxisInstruction` 逐行对齐 Auto。
- **决策 D29 UI 文案**：Tooltip 与确认弹窗改为「力矩反向出力（与 TA_Auto 方向相反，保持出力不定位）」，去掉「回缩至 X mm / 到 0 位」表述；
  上色、闸门、单飞、确认弹窗机制不变。

### 2026-11-10 TA 指令禁用权从 UI 移交执行段（业主口径）

- **现场问题**：初始化那一次的结果被当成永久结论——初始化没连上、之后手动把硬件连上，TA 指令按钮仍不可点；UI 没有事件能实时得知重连后的状态。
- **决策 D30 去禁用**：`ProcessControlPage.RefreshActionStates` 不再写 TA 六个 Radio 的 `Enabled`；就绪判定唯一权威 = 执行段 `CheckTaAvailable` / `CheckTaMotionReady` / `TryBeginAxisInstruction`。
- **决策 D31 反馈落点**（按钮可点后必须有人看得见）：`lblQuickTaTip` + 悬停 Tooltip 继续给原因文案；点击被拒时 `RunInstruction` 的按轴门禁先做「早失败」（日志 + Tooltip + 回退选中态，不弹确认框）；若已下发则由 `ApplyActionBack(false, reason)` 上红底并写 Tooltip。
- **保留项**：同轴指令执行中的 `IsAxisInstructionBusy` / `TryBeginAxisInstruction` 拒绝照旧（防重入）；Y、LA 两区 `Enabled` 不变。
- **决策 D32 判定去重**：`MontionManager.TaAvailable` 收敛为 `TaMotionReady && _taZeroPoseGate`；`RunTaZeroPoseAfterInit` 删去与 `CheckTaMotionReady` 重复的初始化闸门与可动判断，直接委托 `ExecuteTaZeroPose`。
- **边界**：`TaAvailable` 语义（配置 + 使能 + ZeroPose 到位）不变；拒绝文案与日志文案不变；架构边界不变（硬件归 `MontionManager`、指令归 Workflow、UI 不持轴）。

### 2026-11-13 指令区状态标签全部删除（业主口径）

- **决策 D33 状态出口收敛**：取消指令区所有写「不可用原因」的标签，状态只由按钮底色（灰/绿/红）+ 轴表指示灯与状态码 + 日志表达；
  `lblQuickTracking` 去掉原名 `Tip` 后缀且只保留静态标题，`UpdateCommandAreaTips` 整段删除。
- **D31 修订**：反馈落点不再含状态标签 / Tooltip 原因文案；被拒 = `Warning` 日志 + 红底 + 回退选中态，
  执行异常由 `InstructionWorker` 写 `Error` 日志并上红底。
- **边界**：`ApplyActionBack` 去掉无消费者的 `reason` 形参；Y/LA 未就绪仍由 `Enabled` 置灰，TA 六项仍不置灰。
