---
title: ADR-024 安全检查三文件合并为单一安全检查流程
date: 2026-08-31
tags: [决策, 架构, 安全互锁, 安全检查, 文件合并, SafetyWorkflow, MainDeviceControl]
status: accepted
---

> ⚠️ 历史名称提示：本页为**历史决策记录**，正文中的下列文件名为决策当时的旧名，
> 保留原文以留存上下文，现役对应如下：
>
> - `SafetyFlow.cs` → 已移除（ADR-025 合并进 DeviceStatusWork）
> - `SafetyInterlock.cs` → 已移除（ADR-025 合并进 DeviceStatusWork）
> - `SafetyWorkflow.cs` → 现役 `MainDeviceControl/DeviceStatusWork.cs`
>
> **⚠️ 2026-09-03 术语更新（ADR-030）**：本 ADR 的**安全闭环本身继续有效**（检查 → 报警 → 急停 → 记故障 → 复位，现行见 [[architecture/DeviceControlArchitecture]] §9），但正文下列表述**已过时，不得照搬**：
> ① `IsRobotPoseSafe()` 已**移除**（裁定 C3：不再监控机器人 pose，设备无权限管理机器人状态）——焊前门控改为直接读 `DeviceStatusWork.Instance.IsSafe`（本机安全 IO，与 pose 无关）；
> ② `SetStep(...)` 改态写法已废止（裁定 C6），现行以 `RunStep` 由 bool 判断推进；
> ③ 文中 `DeviceWorkflowBase<TStep>` 泛型基类已删，现为非泛型 `DeviceWorkflowBase`。
> 现行架构以 [[architecture/DeviceControlArchitecture]] 为唯一真相源。

# ADR-024 安全检查三文件合并为单一安全检查流程

> **后续更名（2026-09-02，ADR-028）**：本文决策的「合并产物 `DeviceWorkflow/SafetyWorkflow.cs`」已**整体更名为 `DeviceStatusWork.cs`**，并由「继承 `DeviceWorkflowBase<SafetyWorkflowState>` 的工作流」改为「**独立管控类 + IOWork/EMGWork/StatusWork 三线程**」（旧 `SafetyWorkflowState` 枚举已删除）。"三文件合一、单一入口"的核心结论继续有效，现行形态见 [[api/DeviceStatusWork]] 与 [[modules/Safety]]。

## 背景

用户审查 `MainDeviceControl/DeviceWorkflow/` 时指出：

> 用于安全检查的三个文件，应该是合并的。我看到三个文件：一个是安全变量值和检查地址、一个是安全锁检查、一个是安全流程。其实应该合并为一个安全检查流程。

合并前的安全能力被切成三块，各自都不完整：

| 文件 | 行数 | 内容 | 问题 |
|---|---|---|---|
| `SafetyFlow.cs` | 52 | 4 个阈值 + 1 模式开关 + PlcDb + 7 个 PLC 地址 | 纯数据模型，自己不会检查 |
| `SafetyInterlock.cs` | 212 | `FaultCategory` + `FaultRecord` + `SafetyInterlockResult` + `SafetyInterlockChecker` | 会检查，但**被动等别人调用** |
| `SafetyWorkflow.cs` | 104 | 单例 + 高优先级线程 + `MonitorLoop` + `MonitorOnce` | 有循环，但 `MonitorOnce` 是 **TODO 空桩** |

核心矛盾：**配置、判定、执行三者人为割裂**。判定器没有执行载体（零调用方），执行循环没有判定内容（空桩），配置既不被注入也不被标定。结果是安全子系统整体为零消费方的骨架。

同时发现两项既有缺陷：
1. `SafetyWorkflow` **未继承** `DeviceWorkflowBase<TStep>`，自建 `_thread`/`_running`/`_shouldStop`，而基类已提供 `Step`/`SetStep`/`State`/`EmergencyStop`/`StateChanged` —— 违反「共通能力继承、独有内容自建」约定。
2. `MainDeviceWorkflow.IsRobotPoseSafe()` 恒 `return true`，注释写着「后续接 SafetyFlow 互锁检查」—— 门控长期悬空。

## 决策

### 1. 三文件合并为 `DeviceWorkflow/SafetyWorkflow.cs`

| 合并前 | 合并后 |
|---|---|
| `SafetyFlow.cs` | `SafetyWorkflow.cs` 内 `SafetyFlow` 类（配置，类名与公共 API 不变） |
| `SafetyInterlock.cs` → `SafetyInterlockResult` / `SafetyInterlockChecker` | 同上文件内同两个类 |
| `SafetyInterlock.cs` → `FaultCategory` / `FaultRecord` | **迁入 `FaultRecoveryManager.cs`**（故障恢复链路的数据载体） |
| `SafetyWorkflow.cs` | 同上文件内 `SafetyWorkflow` 类（吸收检查与配置，成为唯一流程入口） |

删除 `SafetyFlow.cs`、`SafetyInterlock.cs`，csproj 移除 2 条注册。目录文件数 11 → 9。

`FaultRecoveryManager` 保持独立：**故障恢复 ≠ 安全检查**，前者是「记录 + 重试 + 复位」的持久化链路，后者是「周期判定 + 急停」的实时链路。

### 2. `SafetyWorkflow` 继承 `DeviceWorkflowBase<SafetyWorkflowState>`

新增流程态枚举并接入基类机制：

```csharp
public enum SafetyWorkflowState { Uninitialized, Monitoring, Alarm, Stopped }
```

映射：`Monitoring → Work`、`Alarm → Alarm`、`Uninitialized`/`Stopped → Disconnect`。

接入后自动获得：`Step`、`SetStep(newStep, reason)`、`StateChanged`、`DeviceState` 四态、`EmergencyStop()`、`IsAlarm`、`AlarmOccurred`。并重写 `CheckDeviceIOSafe()` 返回 `IsSafe`，接上 `DeviceStateBase` 的设备安全契约。

### 3. 检查失败走「急停 + 记故障」闭环

```
MonitorOnce() → Checker.Check()
  通过 → SetStep(Monitoring)    并清除报警记录标记
  失败 → 首次失败 TriggerAlarm() → EmergencyStop() + FaultRecoveryManager.RecordFault("Safety", ...)
       → SetStep(Alarm, reason)
```

- `_alarmRecorded` 保证**每个报警周期只记一次故障**，避免 50ms 轮询刷爆 SQLite
- `RecordFault` 传设备键 `"Safety"`，遵守 [[lessons/FaultRecoveryDeviceKey]]（注册 key 与记录 key 同源）
- 新增 `Reset()`：清 `IsAlarm` 与报警记录标记，供人工确认故障排除后调用

### 4. 主设备 Pose 门控接入

`MainDeviceWorkflow.IsRobotPoseSafe()` 由 `return true` 改为 `return SafetyWorkflow.Instance.IsSafe;`。

`IsSafe` 语义：**监控未启动时不门控**（返回 true，与合并前行为等价），启动后以最近一次互锁结果为准，无结果视为不安全。这样接入不会在 PLC 未标定的环境下阻断整机。

### 5. 删除伪异步 `CheckAsync`

`SafetyInterlockChecker.CheckAsync()` 仅用 `Task.Run` 包装同步 `Check()`，零调用方，属 [[standards/CodeSimplification]] ⑤ 伪异步反例，删除。Grep 全项目确认零引用。

## 备选方案

| 方案 | 放弃原因 |
|---|---|
| 只做物理合并，三类原样搬进一个文件 | 未解决「判定器与循环割裂」，检查器仍是零调用方、循环仍是空桩 |
| 把 `FaultRecord`/`FaultCategory` 也并入 SafetyWorkflow.cs | 它们是故障恢复链路的数据载体，与 `FaultRecoveryManager` 强耦合，且受 [[lessons/FaultRecoveryDeviceKey]] 约束，归入后者职责更清晰 |
| 保留 `CheckAsync` 以维持公共 API | 零调用方 + 伪异步，保留即累积死代码；ADR-023 明确此类应删 |
| 接入门控时未启动监控即判定不安全 | 会在 PLC 未标定的环境下直接阻断整机，行为回归风险不可控 |

## 后果

### 正面

- 配置 / 判定 / 执行内聚为单一流程，`MonitorOnce` 从 TODO 空桩变为真实互锁检查
- 安全子系统首次具备完整闭环：检查 → 报警 → 急停 → 记故障 → 复位
- 继承泛型基类后删除自建线程状态字段，`SetStep` 单点收口（`SetStep` 同值短路，50ms 轮询不会刷日志）
- 脚本告警 42 → 1，唯一残留为轮询节拍（见下）
- 设计天然满足 [[decisions/ADR-023-WorkflowResponsibilityBoundary]] R3（流程态通知走基类 `StateChanged`）与 R4（结果以 `LastResult` 只读属性暴露，不抛事件）

### 负面 / 已知取舍

- **残留 1 项脚本告警**：`MonitorLoop` 的 `Thread.Sleep`。安全监控是**周期性轮询**（PLC 无推送事件源），Sleep 是正确节拍；且原设计用 `ThreadPriority.Highest` 独立线程，改用 Timer 会降级为线程池普通优先级。此为 ADR-023「禁止过度等待」规则的**有意例外**（该规则针对"等待异步操作完成"，非"周期轮询节拍"）。
- **`Config` 与 `Check()` 当前零调用方**：保留作为现场标定入口与焊前一次性门控 API。
- **PLC 未连接时互锁恒定失败**：`CheckPlc` 被跳过并记一条 `PLC 未连接或未启用` 失败项 → 一旦启动安全监控，整机 Pose 将被门控。现场须先标定 `SafetyFlow` 的 PLC 点位，或暂不启动监控（默认即不启动）。

## 待办 / 后续

- [ ] 监控未接入上电初始化级联（`PowerOnInitialize` 5 步不含安全流程）—— 需用户确认是否纳入
- [ ] PLC 地址与阈值现场标定（`SafetyFlow` 默认值为占位）
- [ ] `_pollIntervalMs = 50`（20Hz S7 轮询）偏高，接入真实 PLC 后需评估是否调整为 200ms

## 关联

- 前置：[[decisions/ADR-023-WorkflowResponsibilityBoundary]]（R3/R4）
- 取代早期安全模块「三文件并存」的结论（其中「迁 Workflow 不建子文件夹」部分仍有效）
- 模块：[[modules/Safety]]、[[modules/DeviceControl]]
- API：[[api/DeviceStatusWork]]、[[api/DeviceControlWork]]
- 教训：[[lessons/FaultRecoveryDeviceKey]]、[[lessons/CSharp-Language-Pitfalls]]
- 规范：[[standards/CodeSimplification]]
