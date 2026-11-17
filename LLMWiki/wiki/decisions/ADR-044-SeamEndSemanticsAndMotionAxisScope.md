---
title: "ADR-044 焊缝收尾语义与运控轴范围（终止X · 线激光前置收工 · 只服务Y向轴）"
date: 2026-09-24
updated: 2026-10-30
tags: [ADR, 焊缝收尾, 行程监视, 前置距离, LeadDistance, 线激光, 运控, 轴范围, DeviceControlWork, MotionControlWorkflow, LineLaserWorkflow]
status: accepted
---

# ADR-044 焊缝收尾语义与运控轴范围（终止X · 线激光前置收工 · 只服务Y向轴）

> 本页固化 2026-09-24 业主两条裁定。二者都属「物理实际意义」层面的口径，一旦混淆会直接导致收尾动作错位（本主题曾出现「机器人停止目标叠加前置量」的反向实现，同日修正）。

## 一、焊缝收尾语义（业主口径，权威）

**物理事实**：线激光装在焊枪**前方一个前置距离** `LeadDistanceMm` 上；入图键 = 测量时刻 RobotX + 前置量。

设起点 X₀、**焊缝终止 X**（= 焊缝末端在机器人 X 轴上的位置），令终止行程 = |X₁ − X₀|：

| 角色 | 动作点 | 说明 |
|---|---|---|
| **线激光** | X = **X₁ − 前置量**（行程 = 终止行程 − 前置量） | 机器人走到该处时激光恰好扫过焊缝末端（入图键 = 测量X + 前置量 = X₁），再往前已无焊缝可测 ⇒ **停止工作**（停采集 / 关激光与传感器），此后无数据帧、自然不再写值入图 |
| **机器人（焊枪）** | X = **X₁**（行程 = 终止行程） | 末端焊缝仍须由焊枪走完 ⇒ **必须实际走到 X₁ 才停止**、才下发焊接完成 |

**实现落点**：
- `DeviceControlWork.BeginWeldMonitor`：`_weldTargetMm = 终止行程`（⛔ **不得叠加前置量**）；`_laserStopStrokeMm = max(0, 终止行程 − 前置量)`。
- `DeviceControlWork.CheckWeldProgress`：先判**线激光收工行程**（命中即 `LineLaserWorkflow.FinishMeasureByStroke()`），再判**终止行程**（命中才 `DoSubStop`）。
- `LineLaserWorkflow.FinishMeasureByStroke()`：**只关外设**（`SafeShutdownPeripherals()`：停采集 → 关激光 → 关传感器）并置 `_measureFinished`，⛔ **不改 `WeldStatus`（保持 `Working`）** —— 因为**收工只代表测量结束、焊接尚未结束**：机器人还要走到焊缝结束位置。`DoWorking` 见标志即短路（跳过工艺调整与「有效结果缺失」失效判定）；新一沿（`PreWork`/`Working`）复位。**行程判据唯一归属主控**。
- **两条独立时间线**（业主口径，2026-09-24 复正）：
 1. **入图**（测量侧）——收工后无数据帧 ⇒ 入图键 `X + 前置距离` 与 `CSPinY` **不再产生（冻结）**；
 2. **出图与记录**（焊接侧）——`IsSeamWelding`（= 线激光 `WeldStatus == Working`）**保持为真** ⇒ 运控继续写段与出图，`CSPoutY`／`实时Y`／SeamTraceY 记录**一路到焊缝行程结束**（机器人走到终止 X），届时主控 `DoSubStop` 统一收口。
 - ⛔ **不得把「收工」实现成「焊接结束」**：曾让线激光进 `Stopping`，`IsSeamWelding` 瞬变假 ⇒ 运控「停焊沿」在**段未走完时清缓冲** ⇒ `清空 4359` + 坐标系残留 ⇒ 下次启动的标定位回归（点位指令在执行 `StartCspOutput` 建系之前）被 CSP 残留状态挡住而**运动超时**（现场实测链）。
- 末端跟随安全性：`MinSmoothPoints = 3`（硬编码），机器人从 (X₁ − 前置量) 走到 X₁ 的这段里高斯窗内仍有点 ⇒ 查图不回落、轴目标不跳变。

**终止位来源（数据通道）**：
- 优先 **机器人上报停止位 X**：`RX_WELD_STOP_POSE` 携带数值（报文经 `CommandCore.TrySplitPayload` 拆「指令名 + 载荷」，首个数值即停止位 X）→ `DeviceControlWork.ApplyRobotStopPose(X)`。**模拟测试的停止状态同样由机器人发来**。
- 模拟兜底：`_simWeldLengthMm`（随机 1500~2000mm）。
- **真实模式现为占位空缺**：无机器人上报时不做线激光收工判断（仅按兜底行程监视），日志标注「真实占位空缺(待机器人下发)」。协议细化后由机器人下发真实终止 X 取代。

⛔ **易错点**：本主题曾把「前置量」加到**机器人停止目标**上（= `终止行程 + 前置量`），方向与物理实际相反——那会让激光越过焊缝末端后继续工作、机器人多走一个前置量。前置量属于**测量侧的提前量**，只能从线激光一侧扣除。

## 二、运控流程的轴范围（业主口径，权威）

**运控流程只负责 Y 向焊缝跟踪轴的跟随**，其他轴（送丝力矩电机等）不归本流程处理。

- 伺服使能：只使能焊缝跟踪轴（`_seamAxis.ServoOn()`；模拟态取 `GetAxis(SeamTrackAxisName)`）。⛔ 不再调用 `MontionManager.ServoOnAll()`。
- 停止 / 异常收尾：只对焊缝跟踪轴执行**三步闭环** `ShutdownSeamAxis()` —— `ServoOff()`（下电）→ `ResetAlarm()`（清报警）→ **`ServoOn()`（重新上电）**，顺序固定。⛔ 不再调用 `ServoOffAll()` / `ResetAlarmAll()`。
 - ⚠️ **必须含「重新上电」**（2026-09-24 现场实测补正）：只做「下电 + 清报警」会让轴停在下电态，**第二次启动时轴无法响应指令**（标定位回归点位移动 15s 超时）。上电让轴交回「可响应」的待机态。
- **现场实证（2026-09-24 日志）**：运控配置创建 2 个轴（Y向电机 + 送丝力矩电机），全轴收尾会打到送丝力矩电机并报
 `[Error][台达运控轴] 送丝力矩电机 伺服下电 失败 错误码 256`、`报警复位 失败 错误码 256`。
- `MontionManager.ServoOnAll` / `ServoOffAll` / `ResetAlarmAll` **保留**（全轴通用能力成对存在，供多轴场景与维护使用），运控侧不再调用。

## 三、收尾时序与启动前复位（2026-09-24 现场实证补正）

**驱动器返回码语义（取自 `raw/delta/EtherCAT_DLL_Err.cs`）**：
- `0x1107 = ERR_ECAT_NEED_STOP = 4359`「**需要先停止**」——即在**轴未停稳**的状态下调用 `BufferClear()` 必被拒。
- 邻居码：`0x1100 NEED_INITIAL = 4352`（缓冲坐标系未建立）、`0x1104 NEED_RALM = 4356`（报警未复位）、`0x1105 NEED_SVON = 4357`（伺服未使能）、`0x1200 RING_BUFFER_FULL = 4608`（缓冲满）。
- ⇒ 历史 wiki 记的「缓冲**空闲态** Clear 报 4359」口径**不准确**：真正的判据是**轴必须处于停止态**。`BufferStopModeSmooth = 0` 是**减速停（异步）**，紧跟清空必然命中 4359。

**现场实测链（2026-09-24 二跑失败）**：

| 环节 | 事实 |
|---|---|
| ① 收尾清缓冲 | `StopCspOutput` 内 `BufferStop(Smooth)`（异步减速停）**紧随** `BufferClear()` ⇒ 轴仍在减速 ⇒ **4359**，缓冲与坐标系残留 |
| ② 收尾下电 | 紧接着 `ShutdownSeamAxis()` 的 `ServoOff()` **在轴仍在减速时下电** ⇒ 驱动器报伺服类报警（现场「跑完以后轴报警」） |
| ③ 二跑启动 | 报警 / 残留坐标系 ⇒ 小步 11 的 `ServoOn()` 不生效、小步 21 的 `AbsMoveNoBlock` 点位指令被挡 ⇒ 小步 22 **15s 超时**（`Y 轴标定位回归超时`）。点位发生在起焊沿 `StartCrdBuffer` 建系之前，**没有自愈机会**（`StartCspOutput` 的「建系失败先停+清再重试」覆盖不到此处） |
| ④ 人工干预 | 点「清理报警」后再次启动即可运动 ⇒ **反证**根因是驱动器报警 + 缓冲/坐标系残留 |

**裁定（实现落点）**：

1. **两阶段收尾（步 700 / 步 900 同构）**：首次进入只 `StopSeamTrackingOutput()`（停写段 + 平滑停缓冲）；随后**按拍等轴停稳**（`IsSeamAxisSettled()`：无轴 / `!IsMoving()` / `!IsServoOn()` 三选一放行，超时 `StoppingSettleSeconds = 5s` 兜底），停稳后**才**清缓冲与下电。未停稳时 `return false`，由 `FlowProcess` 下一拍重入本步（⛔ 禁 while/Sleep，步骤驱动红线）。标志位 `_stopTeardownStarted` / `_failTeardownStarted` 保证停输出只做一次。
2. **启动前复位（点位移前必须无残留）**：
 - 小步 11：**先 `ResetAlarm()` 再 `ServoOn()`**——上一场残留报警会让直接使能被拒，之后点位指令也不响应。⛔ 顺序不可颠倒。
 - 小步 12（使能完成）→ 移动前：`ResetSeamAxisBufferBeforeMove()` = `BufferStop(Smooth)` + `BufferClear()`（`AbsMoveNoBlock` 点位指令在 `StartCrdBuffer` 建系之前下发，此处不清必被残留坐标系挡成超时）；清空成功即复位 `_cspBufferStartedOnce`，本会话按「首启」预载段数起步。
 - 收尾侧停稳后亦复用同一方法（**双保险**：收尾就地清一次，启动前再清一次）。
3. **只服务 Y 向轴不变**：上述所有动作只作用于 `_seamAxis`。

## 四、PreWork 回标定位步序（CSP 运动模式，2026-09-24 业主口径）

**前提**：Y 轴是 **CSP 运动模式**——下发移动坐标（`AbsMoveNoBlock`）后，驱动器提供**「是否运动停止」判定**（`MontionAxis.IsMoving()` ← 台达 `Mdone`）。

**四步小步流**（`DoReturnToCalibration()`，小步 21 → 22 → 23，未到位回 21）：

| 小步 | 动作 | 失败出口 |
|---|---|---|
| 21 `SubCalCheck` | 判位（已在位即跳过、无跟踪轴直接放行）+ **行程上下限门禁** → `AbsMoveNoBlock(calY)` 下发移动 → 记 `_calStopWaitStart` → 跳 22 | 下发失败 / 越界 → `Fail` |
| 22 `SubCalWait` | **等轴运动停止**（`IsMoving()` 翻假）→ 跳 23；⚠️ 轴**已静止且已在容差内**则**位置优先短路**直接跳 23（2026-09-28 补正，见下） | **超时未停止**（`CalReturnTimeoutSeconds = 15s`，**每次下发后重新计时**，用局部起点而非步停留时长）→ `Fail`「运动停止超时」 |
| 23 `SubCalVerify` | **判到位偏差** ≤ `CalReturnToleranceMm = 0.02mm`（原 0.05）→ 完成、置 `_calReturnReady` | 未到位 → `_calRetryCount++` 并**回 21 重发移动指令**；`_calRetryCount > CalReturnMaxRetry = 3` → `Fail`「未到位且重试已超限」 |

- ⛔ **不得以「位置差」代替「运动停止判定」**：CSP 模式下必须先确认轴已停止，再判偏差——未停止时的位置差不构成到位判据。
- ⛔ 全程非阻塞按拍推进（禁 while/Sleep）；22/23 是按拍反复进入的热路径，分支内静默，仅跳步拍、重试拍与超时拍写 log。
- 重试计数 `_calRetryCount` 在小步 11（伺服使能下发）复位 ⇒ 每次启动都是全新计数。

**与旧实现的差异**：旧版为「21 下发 → 22 等到位（容差 0.05、单次判定、按步停留时长判超时）」，**无运动停止判定、无重试**；新版改为「等停 → 判偏差 → 未到位重发（≤3 次）」，并把超时基准换成**每次下发后的局部计时**（重试不再吃掉同一个 15s 窗口）。

### 2026-09-24 晚补正（官方 demo + 现场日志核对）

- **🔴 判停根因（2026-09-24 依台达官方手册定位）：`IsMoving()` 判据取反。** 台达 `_ECAT_Slave_Motion_Get_Mdone`（EtherCAT 程式開發手冊 8.12 / **P8-18**）在 Cyclic Synchronous 系列（含 CSP）下是**多值状态机**：`0`=靜止、`1`=加速中、`2`=常態速度狀態、`3`=減速中、`5`=MailBox 通訊處理中（Profile 系列 `0`=靜止 / `1`=運動中）⇒ **「運動中」= `Mdone != 0`**。旧实现写 `Mdone == 0`（沿用**雷赛**「0=运动中」语义，见 `raw/skills` 早期封装）**恰好取反**，与现场日志逐条吻合：① 指令刚下发（`Mdone=1` 加速中）被判「已停止」⇒ 当拍跳到位判定、必然未到位而反复重发（日志 L10→L11）；② 轴到位静止（`Mdone=0`）反被判「仍在運動」⇒ 等停 15s 超时（日志 L40）。**修**：`DeltaMontionAxis.IsMoving()` 改 `mdone != 0`（一处修正，`WaitMoveDone()` / `AbsMove()` / 收尾 `IsSeamAxisSettled()` 同步受益）；**两段判**（`_calMotionStarted`：先等「已启动」再等「已停止」）保留为防「下发到启动」空窗的双保险。
- **⛔ 设备初始状态不得清缓冲**：本会话从未建系时 `BufferClear` 必报 **4352 = `ERR_ECAT_NEED_INITIAL`**（日志 L7/L38 实证），此时无残留可清 ⇒ `ResetSeamAxisBufferBeforeMove` 加 `_cspBufferStartedOnce` 门控，且**只在收尾两处调用**（PreWork 移动前那次已按业主口径撤销）。
- **收尾轴处理改「按需」**（业主收尾链末段：清理 → 查报警 → 有则清报警+失能+再使能 / 无则回初始状态）：判据 `MontionAxis.IsAlarm()`（状态字 Fault 位 `0x0008`）；无报警**保持使能**，有报警才 `ServoOff → ResetAlarm → ServoOn`。⛔ 不再无条件下电。
- **台达 API 核对（权威原档）**：官方 demo（`06_EC_CSPMove`，578 条声明）与本项目 110 条 native 声明逐条比对 ⇒ **0 条 EntryPoint 缺失、0 条签名不符**；全量清单 `EtherCAT_DLL_API清单.txt`（828 条）同样零差异。官方 demo 的 CSP 点位运动即 `CSP_Start_Move` + `Motion_Get_Mdone`（状态刷新），**接口选择本身无误**，错在用法竞态。
- **CSP 族专用到位判定已接入（手册 9.1.12 / 9.1.13 原文依据）**：`CSP_Set_SoftTargetReach(CardNo, NodeID, SlotID, U16 WindowTime, U32 PositionWindow, U16 Enable)` —— 手册目的原文：「啟用當前軸的**軟體到位訊號功能**。當連結的 Slave 在 CSP 模式下**未提供 CiA DS402 Statusword (OD 6041h) 的 target reached 功能**時，可使用此 API 啟用上位控制器的到位訊號功能。」参数语义：`PositionWindow` 单位 = **脈波數**（設定到位訊號區間）、`WindowTime` 单位 = **次數**（設定觸發狀態成立的條件次數；手册示例「主站周期 1ms × 100 次 = 0.1s」）；位置一旦超出窗口，累计次数归零。`Get_SoftTargetReach_Status`：`0` = 未到達 PositionWindow 區間 / `1` = 到達。**落地**：回标定位下发前 `ConfigureSoftTargetReachWindow()`（`PositionWindow = CalReturnToleranceMm / AxisEquivMm` = **20 脈波 ↔ 0.02mm**，`WindowTime = 50` 待现场按主站周期核定），小步 23 读状态**留痕佐证**；⛔ **到位主判据仍是位置偏差 ≤ 0.02mm**（业主口径，不用窗口替代）。

### 2026-09-25 补正：`BufferStop` 的 Mode 语义（清空失败 + 二跑失败的真因）

**手册 9.7.16 `_ECAT_Slave_CSP_Start_MotionBuffer_Stop` 原文**（程式開發手冊 P9-180）：
- `Mode 0` = **Feedhold**：「**不會清除 FIFO**，執行 `_ECAT_Slave_CSP_Start_MotionBuffer_Start` 可以**繼續接續執行**」⇒ 这是**暂停**，不是停止；
- `Mode 1` = **平滑停止**：「**清除 FIFO 並解除座標系**」；
- `Mode 2` = **緊急停止**：「清除 FIFO 並解除座標系」。

⇒ **本页此前口径（「`BufferStopModeSmooth = 0` 是减速停（异步）、紧跟 Clear 报 4359」）不准确** —— 真正的问题是**模式选错**。另注：`Clear_Buffer`（9.7.14）与 `Disable`（9.7.29）在手册里都被标注「**(緩衝區指令)**」，即写入 FIFO 排队执行的指令；面对**未被 Mode 1 清空**的 FIFO，清空请求自然被拒。

**现场现象链（业主 2026-09-25 报障：每次收尾都报警清空失败 ⇒ 二跑失败 ⇒ 清报警后三跑正常）**：

| # | 事实 |
|---|---|
| ① | 收尾 `BufferStop(0)` = **Feedhold 暂停** ⇒ FIFO **未清**、坐标系**未解除** |
| ② | 紧接着 `BufferClear()` ⇒ **被拒**（「每次都报警清空失败」） |
| ③ | 残留的**插补坐标系**与下一场的**单轴点位运动**（`CSP_Start_Move`，回标定位所用）冲突 ⇒ **第二场启动失败**（手册 9.7 开篇：「在插補運動模式下，**無法隨意切換到其他運動模式，否則會破壞插補座標系**，且原本載入插補緩衝區的數據將會遺失」） |
| ④ | 人工清报警后第三场可跑 ⇒ 反证根因 = 「报警 + 残留坐标系」 |

**裁定与实现落点**：
- 常量三值齐备：`BufferStopModeFeedhold = 0` / **`BufferStopModeSmooth = 1`（收尾用）** / `BufferStopModeEmergency = 2`。
- `StopCspOutput` 与 `ResetSeamAxisBufferBeforeMove`：**`BufferStop(Mode 1)` 成功即视为收尾完成，不再无条件 `BufferClear()`**；仅 Stop 失败时兜底 Clear 并计入失败计数。
- `StartCspOutput` 建系失败重试：同为 `BufferStop(Mode 1)`，仅失败才 Clear。
- ⛔ **收尾禁止传 Mode 0**（暂停语义，会留下 FIFO + 坐标系）。

### 2026-09-28 补正：小步 22 位置优先短路（真机实测，消除回标定位 15s 阻塞）

- **现象**（`20260928.zip` 日志，三次会话完全一致）：回标定位耗时 **15.00~15.01s**，而轴实际早已停在标定位（「未见启动 等待 15s 转到位判定 **当前 5.000mm 目标 5.000mm**」，随后小步 23 报「回归到位 偏差 0.0000mm」）；日志全程**只有**这一条 15s 记录，从未出现「运动已启动 / 运动已停止 / 重发移动指令」。
- **实测链**（业主 2026-09-28 真机复核裁定）：① 轴离标定位较远时，运动到 **~5.2mm** 处 `IsMoving()` 翻假 ⇒ 小步 22 判「已停止」；② 小步 23 判偏差 0.2mm > 0.02 ⇒ `_calRetryCount++` 重发移动指令；③ 重发时轴已运动到/已接近 `5.000mm`，该次下发成为**空动作** ⇒ `IsMoving()` 恒假、两段判前半段永远等不到「运动已启动」⇒ 空等满 `CalReturnTimeoutSeconds` 才由超时兜底。
- **⚠️ 判据本身无误**：业主真机实测确认 **`IsMoving()` 可正常判断运动**，2026-09-24 晚补正的 `mdone != 0` 修正是对的；本场故障**纯属状态机路径问题**（空动作下发），与 `Mdone` 语义无关——此前「CSP 点位运动下 Mdone 语义不符 / 读不回来」的推测**作废**。
- **裁定（实现落点：`MotionControlWorkflow.DoReturnToCalibration()` 小步 22 前半段）**：在「等运动已启动」之外**先判位置**——**轴已静止**（`!IsMoving()`）**且** `|TeachLockYMm − 轴位| ≤ CalReturnToleranceMm` ⇒ 直接转小步 23 复核（新增日志「PreWork 焊缝跟踪轴已静止且在标定位容差内 转到位判定」），免等 15s。
- ⛔ **与本节「不得以位置差代替运动停止判定」不冲突**：本短路**仍以「已静止」为前置**（未静止不判），位置只用于在静止前提下**免去等待「运动已启动」这一空窗**；到位结论仍**单一由小步 23 给出**（短路分支不置 `_calReturnReady`）。
- **未放松任何失败出口**：轴真未动且不在容差内时，15s 超时兜底、重发重试与 `_calRetryCount` 超限 `Fail` 路径完全不变。
- **残余观察（非本补正范围，待现场定性）**：轴为何在 **~5.2mm** 处被判「已停止」——若属减速段 `Mdone` 瞬时翻 0 后滑行到 5.000mm，则这次重发属多余一轮；若轴真停在 5.2mm，则由小步 23 的重发兜住（设计内出口）。两种情形下 15s 阻塞均不再发生。

## 五、相关页面

- [[api/DeviceControlWork]] · [[api/LineLaserWorkflow]] · [[api/MotionControlWorkflow]] · [[api/MontionManager]]
- [[decisions/ADR-042-SeamTrackingConsolidated]]（焊缝跟踪闭环与前置量入键）· [[decisions/ADR-043-WeldParamControlConsolidated]]（`LeadDistanceMm` 配置）
- 相关模块：[[modules/DeviceControl]] · [[modules/ProductFileManager]]

## 背景

（待补：本决策要解决什么问题）

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 后果

### 正面
- （待补）

### 负面
- （待补）

## 相关页面

- [[decisions/ADR-Index]]
