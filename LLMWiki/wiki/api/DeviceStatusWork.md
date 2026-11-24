---
title: API — DeviceStatusWork 安全/IO/状态管控（+ SafetyFlow / SafetyInterlockChecker）
date: 2026-09-02
tags: [API, 安全检查, 安全互锁, 工作流, PLC, 日志, DeviceStatusWork, ADR-034]
source: AdaWeldSystem/MainDeviceControl/DeviceStatusWork.cs
---

# API — DeviceStatusWork 安全/IO/状态管控

> 🔄 **2026-11-23 单动作锁与运行态未就绪都不丢指令**：`DispatchAction` 返回值改为「是否已派发」——前一动作未结束时**保留虚拟 IO 供下一拍重试**（原为直接丢弃）；`ScanPulseIo` 的 `requireRunning` 未满足时**同样保留 IO 供下一拍重试**（原为取走后丢弃）。原因：① TA_Auto 会阻塞等力矩建立（有限等待），此窗口内到达的焊接启动命令若被丢弃会导致流程永久卡死；② `IoStart` 是**异步派发**，紧随其后的 `IoSubPrework` 若在 Running 前到达被丢弃则真实流程永久断链。⛔ 「先取走再派发」的队列语义，取走与派发之间若可能失败必须回填重试。见 [[lessons/SimulationAutoBranching]] 陷阱廿五。

> **本页述 `DeviceStatusWork`（单例，安全/IO/状态管控）**，见 [[decisions/ADR-013-ThreeStateModelRefactor]]。
> 安全类**不对外暴露模组状态**，仅以 `IsSafe` / `LastResult` 供主设备 `DeviceControlWork` 门控消费。
>
> **位置**：`MainDeviceControl/DeviceStatusWork.cs`（命名空间 `AdaWeldSystem.MainDeviceControl.DeviceWorkflow`）
> **继承**：**独立管控类，不继承 `DeviceWorkflowBase`/`DeviceStateBase`**；由三个常驻监控线程驱动（`IOWork` / `EMGWork` / `LightStatusWork`，各 20Hz；EMGWork 置 Highest）。
> **设计来源**：参考 `PcomDeviceInterface/MachineStatusWork.cs` 的 IOWork/EMGWork/StatusWork 三线程模型（见 `主控设计.xlsx`「设备安全/IO/状态管控」泳道）。
> **单文件承载**：互锁阈值与 PLC 地址（`SafetyFlow` 配置类）+ 互锁判定（`SafetyInterlockChecker`）+ 三线程监控循环（[[decisions/ADR-017-SafetyCheckConsolidation]]）。故障恢复模块已于 2026-09-04 整体移除（ADR-021 D3），本类不再做故障落库。
>
> **✅ 2026-09-04 已落地（ADR-020 批次 3）**：本类线程与入口**以原档命名为准统一**：三线程 `thIOWork`（Running IO + Alarm IO）/ `thEMGWork`（Safe IO）/ **`thLightStatusWork`（status IO，三色灯）**，循环标志位 `IsIOWorking` / `IsEMGWorking` / `IsLightStatusWorking`，公共入口 **`MachineIOWorkOpen()`**（取代旧 `StartWork()`）；线程方法体统一为 `IOWork()` / `EMGWork()` / `LightStatusWork()`。
> 原档未定义停止方法，补充 **`MachineIOWorkClose()`**（取代旧 `CloseWork()`）并保留——置 `_running = false` 后有限等待 `Join(1000)`，不 Abort。
> 调用方：`DeviceControlWork.InitializeMachine` / `StartMachine` → `MachineIOWorkOpen()`；`StopMachine` / `Dispose` → `MachineIOWorkClose()`。
> ⚠️ 真编译待 Visual Studio（沙盒无 C# 编译器，静态自检已通过）。见 [[architecture/DeviceControlArchitecture]] §9。

---

## `class DeviceStatusWork`

单例，由**三个常驻监控线程**按 50ms（20Hz）轮询驱动。报警/急停处置统一经 `DeviceControlWork` 单一控制源变更主设备运行态（Alarm/EStop/NoReset），不自行维护模组状态（ADR-023）。

> **日志出口（2026-09-04 回归直连）**：本类全部日志经私有 `Log(...)` → `GlobalCommData.ShowLog(_tag, ...)`，共 8 处（IOWork 异常 / 急停按钮按下 / 急停轮询异常 / 状态反射 / 状态反射异常 / 三色灯输出异常 / `MachineIOWorkOpen` / `MachineIOWorkClose`）。见 [[api/GlobalCommData]]。

### 公共成员

| 成员 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static DeviceStatusWork` | 单例实例 |
| `IsRunning` | `bool` | 三线程是否运行中 |
| `IsIOWorking` | `bool` | IO 互锁监控线程是否运行中（线程体进入/退出时置位） |
| `IsEMGWorking` | `bool` | 急停处置线程是否运行中 |
| `IsLightStatusWorking` | `bool` | 三色灯状态反射线程是否运行中 |
| `IsSafe` | `bool` | 是否安全；**监控未启动时不门控返回 true**，启动后取 `LastResult.IsPassed`，无结果视为不安全 |
| `LastResult` | `SafetyInterlockResult` | 最近一次互锁检查结果（IOWork 刷新） |
| `Config` | `SafetyFlow` | 阈值与 PLC 地址配置 |
| `MachineIOWorkOpen()` | `void` | 实例化 3 条线程并 Start（幂等，由 `DeviceControlWork.InitializeMachine`/`StartMachine` 调用） |
| `MachineIOWorkClose()` | `void` | 停止三线程（由 `DeviceControlWork.StopMachine`/`Dispose` 调用） |
| `Check()` | `SafetyInterlockResult` | 执行一次互锁检查并刷新 `LastResult`（供焊前一次性门控） |
| `Reset()` | `void` | 复位报警标记（`_alarmActive = false`） |
| `Dispose()` | `void` | 释放三线程（CloseWork） |

### 三线程职责（取代旧单 MonitorLoop）

| 线程 | 字段 / 入口方法 | 优先级 | 职责 |
|---|---|---|---|
| IO 轮询 | `thIOWork` / `IOWork()` | AboveNormal | 周期调用 `SafetyInterlockChecker.Check()`（急停除外）；失败首次 `ReportAlarm(reason)`，恢复 `ReportAlarmCleared`；**运控总线监督** `ScanMotionBusFault()`（2026-09-08，每 4 拍节流） |
| 急停处置 | `thEMGWork` / `EMGWork()` | Highest | **只看物理急停位（反逻辑：无电平信号=急停，有信号=不急停，按下/断线均表现为信号消失，故障安全）**；信号消失上升沿 `EstopMachine("急停按钮按下")`（内部直通 `DoEstopMachine`，无虚拟 IO）；**IO 上电（设备通知上位机安全）才允许取消**——信号恢复且处于 EStop → `EstopCancel()` + `ReportAlarmCleared`，未检测到取消前 EStop 状态无法清除。**急停专责**：普通 Alarm 不在此处置（用户 2026-09-08 裁定） |
| 状态反射 | `thLightStatusWork` / `LightStatusWork()` | Normal | 反射 `DeviceControlWork.Status`（MainDeviceStatus）到三色灯（`WriteBit`，地址待标定），状态切换才写 |

### 动作线程（2026-09-07 新增，第四条）

| 线程 | 字段 / 入口方法 | 职责 |
|---|---|---|
| 动作执行 | `thAction` / `DispatchAction(ioName)` | 承载 `ExecuteIo` 分派的 `DoXxx` 动作；**同一时刻只允许一个动作在跑**（`_actionBusy`），在跑时新命令记 Warning 后丢弃；**执行前后各问询一次运行态**，被急停/报警抢占记一次变更日志（2026-09-07） |

> **扫描与动作必须分离**：`IOWork` 只做「取走 IO → 记日志 → 拉起动作线程 → 立即返回」，
> 绝不直接执行 `DoXxx`。初始化链连接 4 个模组需数十秒，若同步执行会独占扫描线程，
> 期间急停等其它 IO 全部得不到响应（参考 `PcomDeviceInterface/MachineControlWork.ResetMachine`
> 用 `new Task(...).Start()` 异步拉起的同款做法）。
>
> **例外（同步执行白名单）**：①急停 `EstopMachine` **直通同步执行**（无虚拟 IO，2026-09-08 裁定）——急停必须立即生效，异步会引入延迟；
> ②运控总线报警 `IoMotionBusFault` 由 `IOWork` **同步**执行——纯状态迁移（`SetStatus(Alarm)`，µs 级无阻塞），
> 且**报警不允许被 `DispatchAction` 的忙丢弃机制拒绝**。

### 运控总线监督（2026-09-08，用户裁定：控制器状态注册成虚拟 IO）

`ScanMotionBusFault()`：**普通 Alarm 走 IOWork**（EMGWork 专责急停），每 4 拍（50ms×4=200ms）非阻塞采样一次：

1. 闭锁检查：`IsVirtualIoSet(IoMotionBusFault)` 已置位 → 若整机已离开 `Alarm`（消警/急停解除回 NoReset）
   则 `ClearVirtualIo` 解除闭锁后返回；仍处 Alarm 持续闭锁
2. `!MontionManager.Instance.IsInitialized` 跳过（避免启动阶段误报，同「启动默认态误报」教训）
3. `MontionManager.Instance.MontionControl.CheckBusOK(out desc)`（L2 virtual 契约，L3 台达逐从站读
   `CS_ECAT_Slave_Get_Connect_Status`，共享内存级非阻塞）
4. **OK→NG 上升沿**：根因归口记一次 Error（ADR-032 D1）→ `SetVirtualIo(IoMotionBusFault)` →
   同步 `ExecuteIo` → `DoMotionBusFault()` → `SetStatus(Alarm)`；**NG→OK 不自动消警**，归 ClearAlarm 链

### Running IO 状态前置门控（2026-09-07）

`ScanPulseIo(ioName, requireRunning)`：**子流程类 IO**（`IoSubPrework` / `IoSubWork` / `IoSubStop` /
`IoSubManualStop` / `IoSubAlarmStop`）取走后先问询运行态，整机已非 `Running`（停机/报警/急停）则记
Warning 丢弃、不分派——排队中的工作指令在停机后不再执行。命令类 IO（Init/Reset/Start/Stop/ClearAlarm）
不门控（停机后仍须可收命令）。

### 检查内容（IOWork 的两类互锁，急停由 EMGWork 专责）

1. **PLC 硬件项**（`SafetyInterlockChecker.CheckPlc`，经 `GlobalCommData.mCommunicationManager.PlcManager`）
   - 安全门位（为 0 即失败）
   - 保护气压 / 冷却水流量（下限判定）
   - 冷却水温度 / 激光头温度（上限判定）
   - 自动模式字（要求 =1，由 `RequireAutoMode` 开关控制）
   - ⚠️ 急停位**不再**在此检查——由 `EMGWork` 独占处置（置 `EStop`），避免与互锁报警态互相翻转
2. **设备态项**（`CheckDeviceStates`）
   - 焊接头 / 线激光 / 监控相机 / 运动控制 四个工作流均须 `SubDeviceState.Connected`
   - 机器人须在线（`IsRSIConnected`，受 `IsRobotEnabled` 控制；EKI 判定已随 ADR-026 退役清理）

> ⚠️ PLC 未连接或未启用时跳过硬件项并记一条失败项 → **互锁恒定不通过**。现场须先标定 `SafetyFlow` 点位，或暂不启动监控（默认随整机启动）。

### 行为约定

- IOWork 检查失败时**首次**触发 `DeviceControlWork.ReportAlarm(reason)`（故障落库已于 2026-09-04 随模块移除删除，ADR-021）；报警/恢复各触发一次（轮询周期 50ms，`_alarmActive` 保证一个报警周期只触发一次）
- EMGWork 急停（反逻辑物理 IO：信号消失=急停）→ `DeviceControlWork.EstopMachine`（2026-09-04 由 `EStopMachine` 改名，对齐原档 §7.5）；信号上电（设备通知安全）且处于 EStop → `EstopCancel` + `ReportAlarmCleared`
- 单次异常不中断循环（各线程 `while` 体内 try/catch）
- 监控未启动/已停止时 `IsSafe` 返回 true，不阻断整机

---

## `class SafetyFlow`

互锁阈值与 PLC 地址映射。数值为 PLC 原始单位，地址为默认占位，**投产前必须现场标定**。

| 类别 | 成员 | 默认值 |
|---|---|---|
| 阈值 | `MinGasPressure` / `MinCoolantFlow` | 40 / 10（下限） |
| 阈值 | `MaxCoolantTemperature` / `MaxHeadTemperature` | 35 / 60（上限） |
| 开关 | `RequireAutoMode` | true |
| 地址 | `PlcDb` | 1 |
| 地址 | `EmergencyStopBit` / `SafetyDoorBit` | 0 / 1（位索引，EMGWork 读急停位） |
| 地址 | `GasPressureWord` / `CoolantFlowWord` / `CoolantTempWord` / `HeadTempWord` / `ModeWord` | 10 / 12 / 14 / 16 / 20（字节地址） |
| 地址 | `StatusLampDb` | 0（三色灯输出 DB；置 0 表示未配置，LightStatusWork 不写） |
| 地址 | `GreenLightByte`/`GreenLightBit` · `YellowLightByte`/`YellowLightBit` · `RedLightByte`/`RedLightBit` · `BuzzerByte`/`BuzzerBit` | 0/0 · 0/1 · 0/2 · 0/3（三色灯+蜂鸣器输出点位，待标定） |

---

## `class SafetyInterlockResult`

互锁检查结果。

| 成员 | 类型 | 说明 |
|---|---|---|
| `IsPassed` | `bool` | 是否全部通过 |
| `FailedItems` | `List<string>`（只读集合属性） | 未通过项说明 |
| `Reason` | `string` | 汇总原因；通过为「安全互锁全部通过」，失败为未通过项以「，」连接 |
| `CheckTime` | `DateTime` | 检查时间戳 |

---

## `class SafetyInterlockChecker`

互锁判定器，由 `DeviceStatusWork` 持有并调用。

| 成员 | 签名 | 说明 |
|---|---|---|
| 构造函数 | `SafetyInterlockChecker(SafetyFlow thresholds = null)` | 传 null 使用默认 `SafetyFlow` |
| `Thresholds` | `SafetyFlow` | 当前生效配置 |
| `Check()` | `SafetyInterlockResult` | 同步检查，聚合 PLC 硬件项与设备态项（急停除外，由 EMGWork 专责） |

> 原 `CheckAsync()` 已于 2026-08-31 删除（仅 `Task.Run` 包装同步方法的伪异步，零调用方）。

设备就绪判定统一为 `SubDeviceState.Connected`。

---

## 用法

```csharp
// 焊前一次性门控
var result = DeviceStatusWork.Instance.Check();
if (!result.IsPassed)
{
    GlobalCommData.ShowLog("焊接", "安全互锁未通过 " + result.Reason, MessageLevel.Error);
    return;
}

// 周期监控：随整机启动（InitializeMachine / StartMachine 内已 MachineIOWorkOpen），IsSafe 自动刷新
if (!DeviceStatusWork.Instance.IsSafe) { /* 拒绝动作 */ }

// 现场标定 PLC 点位（含三色灯输出）
var cfg = DeviceStatusWork.Instance.Config;
cfg.PlcDb = 10;
cfg.EmergencyStopBit = 2;
cfg.StatusLampDb = 10;
```

---

## 相关页面

- [[api/GlobalCommData]] — 通讯与日志底层出口（本类 `_tag` 的直连落地）
- [[lessons/StepDrivenWorkflowPitfalls]]（七.3）— 日志出口发散与 CS0108 遮蔽的根因
- [[modules/Safety]] — 模块职责与闭环说明
- [[modules/DeviceControl]] — 工作流基类与三态模型
- [[api/DeviceControlWork]] — 消费方：`DeviceControlWork` 焊前门控**直接读** `IsSafe`（⛔ 旧包装方法 ~~`DeviceControlWork.IsRobotPoseSafe`~~ 已于 2026-09-03 移除，裁定 C3）
- ~~api/FaultRecoveryManager（⛔ 已移除删除，ADR-008/032） — 故障记录归口~~（⛔ 2026-09-04 模块整体移除，ADR-021）
- [[decisions/ADR-017-SafetyCheckConsolidation]] — 三文件合并决策
- [[decisions/ADR-013-ThreeStateModelRefactor]] — 归并重命名决策（现行有效）
- [[lessons/FaultRecoveryDeviceKey]] — 故障记录设备键名陷阱

## 初始化期互锁旁路（2026-11-16，阶段 3 / ADR-099）

- `IOWork` 的安全互锁判定改为三支：`DeviceControlWork.Instance.IsInitializing` 为真时**不判互锁、不改报警位**；否则再按模拟/真实分支进入 `SafetyInterlockChecker`。
- 依据：启动第一拍设备尚未连接，先报 Alarm 会掩盖「未连接」这一真实原因（D16）；初始化结束后互锁照常生效。
- `IsInitializing` 由 `DeviceControlWork` 只读暴露，不新增公共接口；旁路只跳判定，不跳 IO 分派与状态巡检。
- 关联：[[decisions/ADR-099-init-reset-separation]] · [[api/DeviceControlWork]]

## 状态一致性巡检接线（2026-11-17，阶段 4 / ADR-100）

- `IOWork` 在 `CheckPreworkFailed()` 之后每拍调用 `DeviceControlWork.Instance.ConsistencyTick()`；节流与纠偏逻辑在主控内，本类不持状态、不新增线程。
- 关联：[[decisions/ADR-100-state-union-and-action-gate]] · [[api/DeviceControlWork]]

## 关闭期只保活（2026-11-17，阶段 5 / ADR-101）

- `IOWork` 进入循环体后先判 `DeviceControlWork.Instance.IsShuttingDown`；为真时只 `Thread.Sleep(50)` 后 `continue`，不再执行 `ScanRunningIo` / `CheckPreworkFailed` / `ConsistencyTick` / `InitializeMachineTick` / `MonitorAlignTick`。
- 目的：关闭链正在 Join 与断设备时，扫描线程不得继续推进业务或改写状态（D11）。
- 关联：[[decisions/ADR-101-shutdown-closure-and-estop]] · [[api/DeviceControlWork]]
