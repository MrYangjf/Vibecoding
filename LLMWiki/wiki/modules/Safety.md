---
title: Safety 模块 — 安全检查流程（DeviceStatusWork）+ 故障恢复
date: 2026-09-02
tags: [模块, 安全互锁, 安全检查, 故障恢复, 状态机, PLC, DeviceStatusWork, ADR-028]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/ 模块源码
---

# Safety 模块 — 安全检查流程（DeviceStatusWork）+ 故障恢复

> **当前形态（ADR-025 三合一 + ADR-028 归并）**：安全/IO/状态管控由**单一文件** `MainDeviceControl/DeviceStatusWork.cs` 承载——互锁阈值与 PLC 地址（`SafetyFlow` 配置类）+ 互锁判定（`SafetyInterlockChecker`）+ 三线程监控循环（`IOWork`/`EMGWork`/`StatusWork`）。设计参照 `PcomDeviceInterface/MachineStatusWork.cs`（见 `主控设计.xlsx`「设备安全/IO/状态管控」泳道）。
>
> **状态模型**：安全类**不对外暴露**子设备三态，仅以 `IsSafe` / `LastResult` 供主设备 `DeviceControlWork` 门控消费；主设备运行态经 `SetStatus` 单一入口变更。
>
> **故障恢复已迁出**：`FaultRecoveryManager.cs`（含 `FaultCategory` / `FaultRecord`）2026-09-01 归口 `ProductFileManager/`（[[decisions/ADR-026-ProductLifecycleRecordModule]] §3），本模块仅作消费方。完整说明见 [[modules/ProductFileManager]]。

---

## 核心文件（当前）

| 文件 | 职责 |
|---|---|
| `MainDeviceControl/DeviceStatusWork.cs` | **安全/IO/状态管控（三合一，参考 MachineStatusWork.cs 三线程模型）**：互锁阈值与 PLC 地址（`SafetyFlow`）+ 互锁判定（`SafetyInterlockChecker`）+ 三线程（IOWork/EMGWork/StatusWork）+ `SafetyInterlockResult` |

> **已迁出**：`FaultRecoveryManager.cs` → `ProductFileManager/ProductFileManager/FaultRecoveryManager.cs`（2026-09-01，ADR-027 §3）。本模块不再持有故障恢复文件，仅作为消费方调用。

---

## 一、安全检查流程（DeviceStatusWork）

`public class DeviceStatusWork`（单例，**独立管控类，不继承 `DeviceWorkflowBase`/`DeviceStateBase`**），由三个常驻监控线程（各 20Hz）内聚而成——IO 轮询（`IOWork`，AboveNormal）、急停处置（`EMGWork`，Highest）、状态反射（`StatusWork`，Normal）。配置（`SafetyFlow`）+ 判定（`SafetyInterlockChecker`）由 `IOWork` 周期调用。设计参照 `PcomDeviceInterface/MachineStatusWork.cs`（见 `主控设计.xlsx`「设备安全/IO/状态管控」泳道）。

> **报警与急停处置分工**：安全类不对外暴露子设备三态，仅以 `IsSafe` / `LastResult` 供主设备门控消费。报警处置：IOWork 调用 `ReportAlarm` + `RecordFault`，通知 `DeviceControlWork` 置 `Alarm`；急停处置：EMGWork 调用 `EStopMachine`，通知 `DeviceControlWork` 置 `EStop`；恢复处置：通知 `DeviceControlWork` 转 `NoReset`。

### 检查内容（两类互锁）

1. **PLC 硬件项**（`SafetyInterlockChecker.CheckPlc`，经 `GlobalCommData.mCommunicationManager.PlcManager`）
   - 安全门位（为 0 即失败）
   - ⚠️ 急停位**不在此检查**——由 `EMGWork` 线程独占轮询并置 `EStop`，避免与互锁报警态互相翻转
   - 保护气压 / 冷却水流量（下限判定）
   - 冷却水温度 / 激光头温度（上限判定）
   - 自动模式字（要求 =1，由 `RequireAutoMode` 开关控制）
2. **设备态项**（`CheckDeviceStates`）
   - 焊接头 / 线激光 / 监控相机 / 运动控制 四个工作流均须 `SubDeviceState.Connected`
   - 机器人须在线（`IsRSIConnected || IsEKIConnected`，受 `IsRobotEnabled` 控制）

> ⚠️ PLC 未连接或未启用时跳过硬件项并记一条失败项 → **互锁恒定不通过**。现场须先标定 `SafetyFlow` 点位，或暂不启动监控（默认不启动）。

### 闭环（三线程）

```
IOWork() → SafetyInterlockChecker.Check()
  通过 → 清 _alarmActive，ReportAlarmCleared()
  失败 → 首次：ReportAlarm(reason) + FaultRecoveryManager.RecordFault("Safety", ...)
EMGWork() → 轮询急停位
  按下 → EStopMachine("急停按钮按下")
  释放(且 EStop) → EStopCancel() + ReportAlarmCleared()
StatusWork() → 反射 DeviceControlWork.Status 到三色灯（状态切换才写）
```

`_alarmActive` 保证**每个报警周期只记一次故障**（IOWork 轮询周期 50ms）。

### 对外 API

| 成员 | 说明 |
|---|---|
| `Instance` | 单例 |
| `StartWork()` / `CloseWork()` | 启停三监控线程（各 20Hz；IOWork AboveNormal / EMGWork Highest / StatusWork Normal；由 `DeviceControlWork.StartMachine`/`StopMachine` 级联） |
| `Check()` | 执行一次互锁检查（供焊前一次性门控），返回 `SafetyInterlockResult` |
| `IsSafe` | 是否安全。**监控未启动时不门控返回 true**；启动后取最近一次结果 |
| `IsRunning` | 监控线程是否运行中 |
| `LastResult` | 最近一次检查结果（监控循环刷新） |
| `Config` | `SafetyFlow` 阈值与 PLC 地址配置 |
| `Reset()` | 人工复位报警标记（`_alarmActive = false`） |

### 主设备焊前门控

`DeviceControlWork` 焊前一次性门控**直接读** `DeviceStatusWork.Instance.IsSafe`。

> ⛔ **旧写法已移除（2026-09-03，裁定 C3）**：~~`DeviceControlWork.IsRobotPoseSafe(pose)`~~ 已从整机编排类删除——不再以「机器人 pose 是否安全」为门控输入，改为直接消费 `DeviceStatusWork` 的互锁结果。
> 安全闭环本身继续有效（见 [[decisions/ADR-024-SafetyCheckConsolidation]]），变的只是接入点：原 `IsRobotPoseSafe` 已删除（2026-09-03 裁定 C3：不再监控机器人 pose）；`DeviceStatusWork.IsSafe` 反映的是**本机安全 IO**（急停/安全门/互锁），与机器人 pose 无关。

监控未启动时 `IsSafe` 返回 true，与合并前「恒安全」行为等价，接入不阻断整机。

---

## 二、故障恢复（FaultRecoveryManager）

> **2026-09-01 已迁出**至 [[modules/ProductFileManager]]（命名空间 `AdaWeldSystem.ProductFileManager`），本节仅保留安全检查侧的使用要点，完整契约见 [[api/FaultRecoveryManager]]。

- **单例**：`FaultRecoveryManager.Instance`（`Lazy<T>`）。
- **持久化**：由 [[api/FaultRecordManager]]（[[modules/SqlLiteDatabase]]）承载，SQLite `DataBase/FaultRecord.db` 表 `FaultRecord`（ADR-027 下沉）。
- **恢复策略**：`RegisterRecoveryStrategy(string deviceKey, Func<bool> strategy)`；`GetRetryCount()` 提供重试上限（通讯 3 / 线激光 3 / 监控 2 / 机器人 3）。
- **安全类故障不自动恢复**（必须人工）：安全检查侧仅调用 `RecordFault("Safety", ...)` 记录，不注册恢复策略。
- **执行方式**：`ThreadPool.QueueUserWorkItem` 异步执行，不阻塞状态转换链。
- ⚠️ **命名约定陷阱**：策略注册 key（英文）与记录 key 必须同源，见 [[lessons/FaultRecoveryDeviceKey]]。

---

## 协作关系

- → [[modules/ProductFileManager]] — 故障恢复数据归口（`FaultRecoveryManager`，2026-09-01 自本模块迁出）
- → [[modules/DeviceControl]] — 工作流基类（`DeviceWorkflowBase` / `DeviceStateBase` 提供 SetState/SetWeldStatus/EmergencyStop）
- → [[modules/Comm]] — PLC(S7) 通讯（`S7PLCCommunication.ReadBit/Read<T>`）、机器人连接判定
- → [[api/DeviceControlWork]] — 消费 `IsSafe` 做 Pose 门控（现由 `DeviceControlWork` 承载）
- → [[decisions/ADR-024-SafetyCheckConsolidation]] — 本次三合一决策
- → [[decisions/ADR-027-ThreeStateModelRefactor]] — 本次归并重命名决策
- → [[lessons/FaultRecoveryDeviceKey]] — 故障恢复设备键名匹配陷阱

---

## 待办

- [ ] 监控未接入上电初始化级联（`PowerOnInitialize` 5 步不含安全流程），待用户确认
- [ ] PLC 地址与阈值现场标定（`SafetyFlow` 默认值为占位）
- [ ] 轮询周期 `_pollIntervalMs = 50`（20Hz）接入真实 PLC 后评估调整

---

*来源：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/ 模块源码（2026-09-02 归并为 DeviceStatusWork）*
