---
title: LaserWeldHeadWorkflow API 参考（焊接头工作流 · 骨架期）
date: 2026-09-02
updated: 2026-09-04
tags: [API, 工作流, 焊接头, RunStep, SubDeviceWeldStatus, DeviceWorkflowBase, ADR-028, ADR-030]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs
---

# LaserWeldHeadWorkflow API 参考

> 焊接头工作流（单例，**骨架期**：私有相位驱动 + 差异化职责待落地）。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：非泛型 `DeviceWorkflowBase`（17 项契约）→ `DeviceStateBase`；`IDisposable` 由基类实现。

> **✅ 2026-09-04 已落地（ADR-030 批次 0~4.4）**：本类已按新架构改码——无自带线程、`RunStep` 驱动范式就位（骨架期无业务执行步）、对外焊接过程态统一经 `SetWeldStatus` 承载。旧 `GoStep`/`SetStep`/`WorkStep`/`StartRunLoop`/`ManualOn`/`ManualOff`/命令三槽等机制已全部清除，不得据旧内容改码。真编译待 VS（静态自检已通过）。
> 步骤驱动规范见 [[architecture/DeviceControlArchitecture]] §4（17 契约）· §5（`RunStep` 驱动）· §16（代码模板）。

---

## 公共成员

| 成员 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static LaserWeldHeadWorkflow` | `Lazy<T>` 单例 |
| `StateName` | `override string` | 对外名片名，返回 `Tag`（日志/事件标识） |
| `State` / `WeldStatus` | 基类属性 | 连接态（`SubDeviceState`）/ 焊接过程态（`SubDeviceWeldStatus`） |
| `RunStep` / `StepWorkTime` / `WorkStepName` / `StepStatusText` | 基类属性 | 执行步 / 步骤用时 / 步中文名 / 可观测摘要 |

> `ConfigFileName = "LaserWeldHeadWorkflow"`（protected override，配置落在 `Config/XML/` 下）。

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

## 差异化职责（原档 R009，ADR-030 批次 4.1 待办）

**温度阈值监控**——待硬件温度点位明确后落地。当前留痕位置：

- `FlowProcess()`：启用门控后仅 `// todo 温度阈值监控（原档 R009）待硬件温度点位明确后落地`，骨架期无执行步。
- `SubDeviceLog()`：`// todo` 温度与阈值日志，暂输出 相位/连接态/焊接过程态。

> 骨架期 `FlowProcess` 不推进 `RunStep`（`ClearStatus` 时归 `StepIdle` 0）；私有逻辑落地时在 `switch(RunStep)` 内新增执行步，每 case 靠 bool 判定推进、推进前刷新计时（§5 范式），新相位一律经 `SetWeldStatus` 映射。

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

`LoadConfig` / `SaveConfig` **无参**，走 `XdocumentReaderWriter`（XML 文件 `Config/XML/LaserWeldHeadWorkflow.xml`）；`SaveConfig()` 末尾 `Config.SaveXdocument()` 落盘（裁定 D1）。温度阈值等参数待落地后逐项读取/保存（`// todo`）。

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
- [[modules/LaserWeldHead]] — 焊接头模块（ILaserWeldHeadController 等）
- [[api/LaserWeldHeadController]] — 控制器 API
- [[decisions/ADR-027-ThreeStateModelRefactor]] — 三态模型（现行有效）
- [[decisions/ADR-029-RawDesignRefinement20260903]] — 原档细化与完全重构裁定
