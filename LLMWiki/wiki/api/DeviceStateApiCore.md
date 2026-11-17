---
title: DeviceStateApiCore API 参考（设备状态核心 · DeviceStateBase / DeviceWorkflowBase）
date: 2026-09-17
tags: [API, 主设备控制, 状态机, 流程基类, 契约, 三态模型, ADR-017, ADR-023, ADR-005]
source: AdaWeldSystem/MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs
---

# DeviceStateApiCore API 参考

> 模组状态与流程的**抽象基类核心**：定义三态模型、状态唯一写入口规约与模组流程契约清单。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs`、同目录 `DeviceWorkflowBase.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`
> **沿革**：DeviceState / FlowState 目录已合并为 DeviceStateApiCore，命名空间随目录（[[decisions/ADR-005-NamespaceDirectoryAlignment]]）。

---

## 定位

```
DeviceStateBase（抽象：连接态 + 焊接过程态 + 设备安全）
  └─ DeviceWorkflowBase : DeviceStateBase, IDisposable（抽象：17 项流程契约 + 步控/计时机制）
       └─ 各模组流程实现（由 DeviceControlWork 编排驱动）
```

- 状态只经基类写入口写入，子类不得直接给 State/WeldStatus 赋值（属性 setter 为 `protected`）。
- 主设备运行态 `MainDeviceStatus` **不在本基类承载**，由 [[api/DeviceControlWork]] 统一持有（ADR-023 三态模型：连接态 / 焊接过程态 / 主设备运行态各归其位）。
- 不自带线程：FlowProcess 由 DeviceControlWork 的模组线程反复调用。

## 三态模型（枚举定义于 DeviceStateBase.cs）

| 枚举 | 取值 | 语义 |
|---|---|---|
| `SubDeviceState` | `Disconnected=0` / `Connected=1` | 模组连接态（两态联动） |
| `SubDeviceWeldStatus` | `NoReset=0` / `Standby=1` / `PreWork=2` / `Working=3` / `Stopping=4` / `ErrorAborted=5` / `ManualStopped=6` | 模组焊接过程态（7 态，ADR-017 裁定 C2） |
| `MainDeviceStatus` | `Running=0` / `Alarm=1` / `EStop=2` / `Stop=3` / `NoReset=4` / `Reseting=5` | 主设备运行态（6 态，由 DeviceControlWork 承载） |

## DeviceStateBase（状态核心）

### 状态写入口规约

| 成员 | 签名 | 职责 |
|---|---|---|
| `SetState` | `protected void (SubDeviceState newState, string reason)` | **State 唯一写入口**（Connected 时自动落定连接结果） |
| `SetWeldStatus` | `protected void (SubDeviceWeldStatus newStatus, string reason)` | **WeldStatus 唯一写入口**（变更后执行步由调用方推进） |
| `IsAlarm` | `bool { get; protected set; }` | 设备安全：急停/告警态（置 true 时触发 `AlarmOccurred`） |
| `EmergencyStop` | `virtual void ()` | 默认置 IsAlarm 并记日志；主设备侧子类重写以调用具体急停 |

### 连接尝试与事件

| 成员 | 签名 | 职责 |
|---|---|---|
| `BeginConnectAttempt` | `void ()` | 发起连接尝试前调用，复位上次结果（`ConnectSettled` 置 false） |
| `MarkConnectFailed` | `void (string reason)` | 异步连接拿到确定失败时调用，等待方不必等超时即可收敛 |
| `ConnectSettled` / `ConnectResult` | `bool` / `string { get; }` | 连接是否已出结果 / 结果描述（锁保护，区分「已确认失败」与「尚未反馈」） |
| `StateSwitched` | `event EventHandler<SubDeviceStateChangedEventArgs>` | 连接态切换事件（不记日志，ADR-034 报错分层） |
| `WeldStatusChanged` | `event EventHandler<WeldStatusChangedEventArgs>` | 焊接过程态变更事件 |
| `StateName` | `abstract string { get; }` | 设备名称（日志/事件标识），子类必须实现 |

## DeviceWorkflowBase（流程基类，17 项契约）

### 步控推进机制

- `RunStep`（volatile int）为执行步游标；`FlowProcess()` 以 RunStep 驱动，**每个 case 由 bool 判定推进，未完成直接结束本次调用，下周期重试**。
- ⛔ 红线：case 体内禁止 Thread.Sleep / while 轮询 / 无界同步等待。
- **推进步号前必须先调 `ResetWorkTime()`**（或用 `AdvanceStep`，改步与刷新计时成对），否则步骤计时把停留时长带入下一步误判超时。
- 通用步号约定：`StepIdle = 0`（待机）、`StepFinishOk = 800`（成功收尾）、`StepFinishFail = 900`（失败收尾），子类不得重复定义。
- `IsStepTimeout()`：单步停留超过 `TimeOutSeconds`（默认 30，0 表示不启用）即超时。

### 17 项抽象契约

| # | 成员 | 签名 | 职责 |
|---|---|---|---|
| 1 | `FlowProcess` | `void ()` | 流程处理（步控主循环体，由 DeviceControlWork 线程反复调用） |
| 2 | `ResetProcess` | `bool ()` | 复位流程（线性阻塞链 `if (!动作()) return false;`，非步控） |
| 3 | `ClearStatus` | `void ()` | 状态清理（标志位全复位 + RunStep 归零） |
| 4 | `ResetWorkTime` | `void ()` | 清除步骤用时（防暂停期时长计入导致异常超时，内部必须调 `ResetStepTime()`） |
| 5 | `InitializeOn` | `bool ()` | 设备连接（阻塞，同步等待至完成或超时） |
| 6 | `InitializeOff` | `bool ()` | 设备断开（阻塞） |
| 7 | `SubDeviceLog` | `void ()` | 设备差异化日志 |
| 8 | `LoadConfig` | `void ()` | 加载配置（走 XdocumentReaderWriter，裁定 D1） |
| 9 | `SaveConfig` | `void ()` | 保存配置（末尾必须 `Config.SaveXdocument()` 落盘） |
| 10 | `WeldStatusTrans` | `void ()` | 焊接工作状态切换管控 |
| 11 | `ConnectOn` | `bool ()` | 开启连接（**非阻塞**，结果由 SubDeviceState 异步反映） |
| 12 | `ConnectOff` | `bool ()` | 关闭连接（**非阻塞**） |
| 13 | `GetStepName` | `protected abstract string (int step)` | 步号映射中文名（可观测性，新增步必须登记） |

### 关键机制成员

| 成员 | 签名 | 职责 |
|---|---|---|
| `RequestWeldStatus` | `void (SubDeviceWeldStatus target, string reason)` | 编排层统一下发目标焊接态（SetWeldStatus 是 protected，经此转发） |
| `AdvanceStep` | `protected void (int step)` | 推进执行步并同步刷新步骤计时 |
| `IsEnable` | `bool { get; set; }` | 未启用的流程不参与编排 |
| `StepStatusText` | `string { get; }` | 可观测性摘要（如 `step:21 / 3.4s 等待数据稳定`），供 UI 一次性读取 |
| `Config` | `XdocumentReaderWriter { get; }` | 模组配置读写器（按 `ConfigFileName` 惰性创建；⛔ 运行期禁止在 FlowProcess 内读写） |
| `Log` | `protected void (string message, MessageLevel level)` | 统一日志出口（Tag = 流程名，子类构造内赋值） |
| `ReadInt` / `ReadDouble` | `protected int/double (string, 默认值)` | 读配置项（解析失败回退默认值） |
| `Dispose` | `void ()` | 标准 Dispose（ADR-001），子类释放钩子为 `DisposeManaged()` |

## 相关页面

- [[api/DeviceControlWork]] — 主设备编排（模组线程驱动 FlowProcess、持有 MainDeviceStatus）
- [[api/DeviceStatusWork]] — 设备状态监控
- [[api/CommandCore]] — 指令核心
- [[modules/DeviceControl]] — 模块说明
- [[decisions/ADR-031-ProductLifecycleRecordModule]] — 焊接过程 7 态裁定（C2）
- [[decisions/ADR-013-ThreeStateModelRefactor]] — 三态模型重构
- [[decisions/ADR-005-NamespaceDirectoryAlignment]] — 目录即命名空间（DeviceState/FlowState 合并）
