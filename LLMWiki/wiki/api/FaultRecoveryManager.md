---
title: API — FaultRecoveryManager 故障恢复管理器（+ FaultRecord / FaultCategory）
date: 2026-08-31
tags: [API, 故障恢复, SQLite, 单例, Safety, FaultRecord, 已废弃]
source: AdaWeldSystem/ProductFileManager/FaultRecoveryManager.cs（已移除，2026-09-04 ADR-032 D3）
status: deprecated
---

# API — FaultRecoveryManager 故障恢复管理器

> ⛔ **整页废弃（2026-09-04）**：FaultRecoveryManager / FaultRecordManager / FaultRecord / FaultCategory 已随架构裁定**整体从代码中移除**（用户裁定：架构上无「故障恢复」定义，见 [[decisions/ADR-031-ErrorReportingHierarchy]] D3）。报警语义由 `DeviceControlWork.ReportAlarm` / `ReportAlarmCleared` 承载。下文仅作历史存档，代码中不得再引用任何同名实体。

> **位置**：`ProductFileManager/FaultRecoveryManager.cs`（命名空间 `AdaWeldSystem.ProductFileManager`）
> **2026-09-01 迁址**：自 `MainDeviceControl/DeviceWorkflow/` 迁入 `ProductFileManager/`，成为故障恢复数据的归口使用方（ADR-027 §3）。**调用方需 `using AdaWeldSystem.ProductFileManager`**，API 签名与行为零变化。
> **2026-08-31**：`FaultCategory` 与 `FaultRecord` 由已删除的 `SafetyInterlock.cs` 迁入本文件（安全检查三文件合并，见 [[decisions/ADR-024-SafetyCheckConsolidation]]）。

---

## `enum FaultCategory`

故障分类。

| 成员 | 说明 |
|---|---|
| `Communication` | 通讯故障 |
| `Device` | 设备故障 |
| `Process` | 工艺故障 |
| `Safety` | 安全故障（安全检查流程互锁失败时使用） |
| `System` | 系统故障 |

---

## `class FaultRecord`

故障记录，是「检测 → 停机 → 记录 → 确认 → 排除 → 复位 → 复位验证」闭环的数据载体。

| 成员 | 类型 | 默认值 |
|---|---|---|
| `Time` | `DateTime` | `DateTime.Now` |
| `Device` | `string` | `"未知设备"` |
| `State` | `SubDeviceWeldStatus`（焊接过程态七态） | `Standby` |
| `Category` | `FaultCategory` | `Device` |
| `ErrorCode` | `string` | `string.Empty` |
| `ParamSnapshot` | `string` | `string.Empty` |
| `AutoRecovered` | `bool` | `false` |
| `RecoveryAction` | `string` | `string.Empty` |

---

## `class FaultRecoveryManager`

单例（`Lazy<T>`），故障记录持久化与自动恢复策略调度。

### 公共成员

| 成员 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static FaultRecoveryManager` | 单例 |
| `RegisterRecoveryStrategy` | `void (string deviceKey, Func<bool> action)` | 注册设备自动恢复策略（返回 true 表示已恢复）；重复注册覆盖 |
| `RecordFault` | `void (string deviceKey, FaultRecord record)` | **推荐重载**：按 `deviceKey` 精确匹配策略后异步重试 |
| `RecordFault` | `void (FaultRecord record)` | 兼容重载：按 `record.Device` 中文名模糊解析（不推荐） |

### 持久化

- 库：`DataBase/FaultRecord.db`（持久化实现下沉 [[api/FaultRecordManager]]，ADR-027），表 `FaultRecord`
- 列：`Time`(24) / `Device`(32) / `State`(16) / `Category`(16) / `ErrorCode`(32) / `ParamSnapshot`(200) / `AutoRecovered`(8) / `RecoveryAction`(64)
- 写入失败仅记 Warning 日志，不抛出异常中断调用链
- **为何 `Persist()` 不随 SQLite 实现一起下沉**：它只做「`FaultRecord` 领域对象 → `string[]` 值数组」映射 + 按列宽截断 + 失败记 Warning，**不含任何 SQLite 代码**。若搬进 `SqlLiteDatabase`，DB 层就必须引用 `FaultRecord` 领域类型，直接违反 ADR-027「DB 层不得反向依赖业务层」红线。这是分层取舍，不是漏拆。

### 消费方（6 处，均在 `MainDeviceControl/`）

`DeviceStatusWork`（安全互锁，`_tag`）· `DeviceControlWork`（`"MainDevice"`）· `LineLaserWorkflow` · `MonitorCameraWorkflow` · `MotionControlWorkflow` · `WeldParamControlWorkflow`（后四处传自身 `_tag`/`Tag`）。全部需 `using AdaWeldSystem.ProductFileManager`。

### 重试策略

`GetRetryCount(key)`：含 `Robot`/`LineLaser`/`Comm` 的 key 3 次，`Monitor` 2 次，其余 3 次，间隔 5s。
恢复动作经 `ThreadPool.QueueUserWorkItem` **异步执行**，不阻塞状态转换链。

> **安全类故障不自动恢复**（必须人工）：安全检查侧只调 `RecordFault("Safety", ...)` 记录，不注册恢复策略。

### 用法

```csharp
// 初始化阶段注册（key 用英文，与记录时同源）
FaultRecoveryManager.Instance.RegisterRecoveryStrategy("LineLaser",
    () => LineLaserWorkflow.Instance.Initialize());

// 故障时记录
FaultRecoveryManager.Instance.RecordFault("Safety", new FaultRecord
{
    Device = "安全检查流程",
    State = DeviceState.Alarm,
    Category = FaultCategory.Safety,
    ErrorCode = "INTERLOCK_FAILED",
    ParamSnapshot = result.Reason
});
```

⚠️ **P0 陷阱**：策略注册 key（英文）与记录用的 `deviceKey` 必须同源，否则 `ResolveKey` 的子串匹配永远失败、恢复策略永不触发。详见 [[lessons/FaultRecoveryDeviceKey]]。

---

## 相关页面

- [[modules/ProductFileManager]] — 本文件所属模块（故障恢复数据归口，2026-09-01 起）
- [[modules/Safety]] — 安全检查与故障恢复链路
- [[api/DeviceStatusWork]] — 安全检查流程，故障产生的上游
- [[modules/DeviceControl]] — 三态模型与非泛型工作流基类
- [[decisions/ADR-024-SafetyCheckConsolidation]] — 三文件合并决策
- [[lessons/FaultRecoveryDeviceKey]] — 设备键名匹配陷阱
