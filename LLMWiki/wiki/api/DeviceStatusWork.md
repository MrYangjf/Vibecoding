---
title: API — DeviceStatusWork 安全/IO/状态管控（+ SafetyFlow / SafetyInterlockChecker）
date: 2026-09-02
tags: [API, 安全检查, 安全互锁, 工作流, PLC, 日志, DeviceStatusWork, ADR-034]
source: AdaWeldSystem/MainDeviceControl/DeviceStatusWork.cs
---

# API — DeviceStatusWork 安全/IO/状态管控

> **本页述 `DeviceStatusWork`（单例，安全/IO/状态管控）**，见 [[decisions/ADR-034-ThreeStateModelRefactor]]。
> 安全类**不对外暴露子设备状态**，仅以 `IsSafe` / `LastResult` 供主设备 `DeviceControlWork` 门控消费。
>
> **位置**：`MainDeviceControl/DeviceStatusWork.cs`（命名空间 `AdaWeldSystem.MainDeviceControl.DeviceWorkflow`）
> **继承**：**独立管控类，不继承 `DeviceWorkflowBase`/`DeviceStateBase`**；由三个常驻监控线程驱动（`IOWork` / `EMGWork` / `LightStatusWork`，各 20Hz；EMGWork 置 Highest）。
> **设计来源**：参考 `PcomDeviceInterface/MachineStatusWork.cs` 的 IOWork/EMGWork/StatusWork 三线程模型（见 `主控设计.xlsx`「设备安全/IO/状态管控」泳道）。
> **单文件承载**：互锁阈值与 PLC 地址（`SafetyFlow` 配置类）+ 互锁判定（`SafetyInterlockChecker`）+ 三线程监控循环（[[decisions/ADR-031-SafetyCheckConsolidation]]）。故障恢复模块已于 2026-09-04 整体移除（ADR-038 D3），本类不再做故障落库。
>
> **✅ 2026-09-04 已落地（ADR-036 批次 3）**：本类线程与入口**以原档命名为准统一**：三线程 `thIOWork`（Running IO + Alarm IO）/ `thEMGWork`（Safe IO）/ **`thLightStatusWork`（status IO，三色灯）**，循环标志位 `IsIOWorking` / `IsEMGWorking` / `IsLightStatusWorking`，公共入口 **`MachineIOWorkOpen()`**（取代旧 `StartWork()`）；线程方法体统一为 `IOWork()` / `EMGWork()` / `LightStatusWork()`。
> 原档未定义停止方法，补充 **`MachineIOWorkClose()`**（取代旧 `CloseWork()`）并保留——置 `_running = false` 后有限等待 `Join(1000)`，不 Abort。
> 调用方：`DeviceControlWork.InitializeMachine` / `StartMachine` → `MachineIOWorkOpen()`；`StopMachine` / `Dispose` → `MachineIOWorkClose()`。
> ⚠️ 真编译待 Visual Studio（沙盒无 C# 编译器，静态自检已通过）。见 [[architecture/DeviceControlArchitecture]] §9。

---

## `class DeviceStatusWork`

单例，由**三个常驻监控线程**按 50ms（20Hz）轮询驱动。报警/急停处置统一经 `DeviceControlWork` 单一控制源变更主设备运行态（Alarm/EStop/NoReset），不自行维护子设备状态（ADR-030）。

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
| IO 轮询 | `thIOWork` / `IOWork()` | AboveNormal | 周期调用 `SafetyInterlockChecker.Check()`（急停除外）；失败首次 `ReportAlarm(reason)`，恢复 `ReportAlarmCleared` |
| 急停处置 | `thEMGWork` / `EMGWork()` | Highest | 轮询 PLC 急停位；按下 `EstopMachine("急停按钮按下")`，释放后 `EstopCancel()` + `ReportAlarmCleared` |
| 状态反射 | `thLightStatusWork` / `LightStatusWork()` | Normal | 反射 `DeviceControlWork.Status`（MainDeviceStatus）到三色灯（`WriteBit`，地址待标定），状态切换才写 |

### 检查内容（IOWork 的两类互锁，急停由 EMGWork 专责）

1. **PLC 硬件项**（`SafetyInterlockChecker.CheckPlc`，经 `GlobalCommData.mCommunicationManager.PlcManager`）
   - 安全门位（为 0 即失败）
   - 保护气压 / 冷却水流量（下限判定）
   - 冷却水温度 / 激光头温度（上限判定）
   - 自动模式字（要求 =1，由 `RequireAutoMode` 开关控制）
   - ⚠️ 急停位**不再**在此检查——由 `EMGWork` 独占处置（置 `EStop`），避免与互锁报警态互相翻转
2. **设备态项**（`CheckDeviceStates`）
   - 焊接头 / 线激光 / 监控相机 / 运动控制 四个工作流均须 `SubDeviceState.Connected`
   - 机器人须在线（`IsRSIConnected || IsEKIConnected`，受 `IsRobotEnabled` 控制）

> ⚠️ PLC 未连接或未启用时跳过硬件项并记一条失败项 → **互锁恒定不通过**。现场须先标定 `SafetyFlow` 点位，或暂不启动监控（默认随整机启动）。

### 行为约定

- IOWork 检查失败时**首次**触发 `DeviceControlWork.ReportAlarm(reason)`（故障落库已于 2026-09-04 随模块移除删除，ADR-038）；报警/恢复各触发一次（轮询周期 50ms，`_alarmActive` 保证一个报警周期只触发一次）
- EMGWork 急停按下 → `DeviceControlWork.EstopMachine`（2026-09-04 由 `EStopMachine` 改名，对齐原档 §7.5）；释放且处于 EStop → `EstopCancel` + `ReportAlarmCleared`
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
- [[lessons/DeviceControlWorkInheritanceBypass]] — 日志出口发散与 CS0108 遮蔽的根因
- [[modules/Safety]] — 模块职责与闭环说明
- [[modules/DeviceControl]] — 工作流基类与三态模型
- [[api/DeviceControlWork]] — 消费方：`DeviceControlWork` 焊前门控**直接读** `IsSafe`（⛔ 旧包装方法 ~~`DeviceControlWork.IsRobotPoseSafe`~~ 已于 2026-09-03 移除，裁定 C3）
- ~~[[api/FaultRecoveryManager]] — 故障记录归口~~（⛔ 2026-09-04 模块整体移除，ADR-038）
- [[decisions/ADR-031-SafetyCheckConsolidation]] — 三文件合并决策
- [[decisions/ADR-034-ThreeStateModelRefactor]] — 归并重命名决策（现行有效）
- [[lessons/FaultRecoveryDeviceKey]] — 故障记录设备键名陷阱
