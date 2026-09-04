---
title: LaserWeldHeadWorkflow API 参考（焊接头工作流 · SubDeviceWeldStatus）
date: 2026-09-02
tags: [API, 工作流, 焊接头, 步骤驱动, SubDeviceWeldStatus, DeviceWorkflowBase, ADR-034]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs
---

# LaserWeldHeadWorkflow API 参考

> **⚠️ 2026-09-03 架构重构（ADR-036 已裁定，用户定性「完全重构」）**：本页描述的是**改造前**的 API 现状，改码尚未开工。
> 下列机制**已裁定清除，不得据本页改码**：`GoStep`/`SetStep` 改步 · `WorkStep`/`WorkStartTime` · 基类常驻监听线程（`StartRunLoop`/`BeatMs`） · `ManualOn`/`ManualOff` · 命令三槽与机器人 pose 监控 · const int 指令表。
> **现行规范唯一出处**：[[architecture/DeviceControlArchitecture]]（§4 基类 17 项契约 · §5 `RunStep` 驱动 · §7 7 线程编排 · §16 代码模板）。
> 本页将在 [[architecture/DeviceControlArchitecture]] §15 的改码批次完成后同步重写。

> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：非泛型 `DeviceWorkflowBase`（ADR-034）；单例 `Instance`（`Lazy<T>`）。
> **步骤驱动**：骨架期私有逻辑未落地，无执行步，故 `FlowProcess` 空转、`IsRunLoopActive = false`（不起空转线程，避免空转）。私有逻辑落地时按段位规范新增执行步并登记 `GetStepName`。
> **三态模型（ADR-034）**：对外焊接过程态统一经 `SetWeldStatus(SubDeviceWeldStatus)` 承载；连接态经 `ConnectOn`/`ConnectOff` 联动 `State`（`SubDeviceState`）。

---

## 核心类

```csharp
public class LaserWeldHeadWorkflow : DeviceWorkflowBase
{
    public static LaserWeldHeadWorkflow Instance { get; }   // Lazy<T> 单例

    // 连接契约（基类，受理式非阻塞，内部自起后台线程）
    public override bool ConnectOn();     // TODO 私有逻辑待实现：连接焊接头并置 State=Connected
    public override void ConnectOff();    // TODO 私有逻辑待实现：断开焊接头并置 State=Disconnected

    // 生命周期（基类 6 契约）
    public override bool ResetProcess();  // 清执行步与相位 → Standby
    public override void ClearStatus();   // 报警后回就绪
    public override void ResetWorkTime(); // 刷新工作时间计时

    // 对外只读
    public override string StateName { get; }   // "焊接头工作流"
}
```

> 本工作流**无主设备运行态**（`MainDeviceStatus` 仅 `DeviceControlWork` 持有）；其对外状态为「连接态 `State`（`SubDeviceState`）+ 焊接过程态 `WeldStatus`（`SubDeviceWeldStatus`）」。

---

## 焊接头工作流状态 LaserWeldHeadWorkflowState（私有相位）

> 私有 `_phase`（`LaserWeldHeadWorkflowState`），仅驱动 `FlowProcess` 与可观测性；对外统一映射到 `SubDeviceWeldStatus`。

| 取值 | 含义 | 映射 `SubDeviceWeldStatus` |
|---|---|---|
| `Uninitialized`(0) | 未初始化 | `Standby`（默认） |
| `Standby`(1) | 待机（已连接就绪） | `Standby` |
| `Working`(2) | 工作中 | `Working` |
| `ErrorAborted`(3) | 异常终止 | `ErrorAborted` |

映射逻辑（`MapWeldStatus`）：`Standby→Standby`、`Working→Working`、`ErrorAborted→ErrorAborted`、其余→`Standby`。

---

## 阶段态（焊接过程态）映射

私有 `SetStep(LaserWeldHeadWorkflowState step, string reason)` → 刷新 `_phase` 并调用基类 `SetWeldStatus(MapWeldStatus(step), reason)`。

- 对外只读属性 `WeldStatus`（`SubDeviceWeldStatus`）由基类提供，grep 不到赋值属正常（统一经 `SetWeldStatus`）。
- 切换焊接过程态即触发 `WeldStatusChanged`（基类事件）。

---

## 步骤驱动（骨架期）

| 项 | 现状 |
|---|---|
| `IsRunLoopActive` | `false`（不起常驻监听线程，避免空转） |
| `FlowProcess()` | 空转（无执行步） |
| `GetStepName(int)` | 按 `_phase` 返回中文名（待机/工作中/异常终止/未初始化） |
| `GoStep(n)` | 基类唯一改步入口可用，骨架期未推进 |

> 私有逻辑落地时：在 `FlowProcess()` 的 `switch(_phase)` 内新增执行步（段位规范见 [[architecture/DeviceControlArchitecture]] §5），`case` 内禁止 `Thread.Sleep`/`while` 轮询；新阶段切换走 `SetWeldStatus`（⛔ 旧写法 `SetStep`/`GoStep` 已于 2026-09-03 裁定清除）；执行步由 `RunStep` 在 `case` 内 bool 判定后推进并立即 `break`（见 [[architecture/DeviceControlArchitecture]] §5、[[lessons/StepDrivenWorkflowPitfalls]] 坑一保留思想）。

---

## 连接契约

| 方法 | 语义 | 状态联动 |
|---|---|---|
| `ConnectOn()` | 受理式非阻塞：内部自起后台线程连接焊接头，置 `State=Connected`（骨架 TODO） | `State` ← `SubDeviceState.Connected` |
| `ConnectOff()` | 断开焊接头（非阻塞） | `State` ← `SubDeviceState.Disconnected` |
| `ResetProcess()` | 清执行步与相位，回 `Standby` | `WeldStatus` ← `SubDeviceWeldStatus.Standby` |
| `ClearStatus()` | 报警后停止处理，回就绪 | `WeldStatus` ← `SubDeviceWeldStatus.Standby` |

---

## 用法示例

```csharp
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;

var head = LaserWeldHeadWorkflow.Instance;
head.ConnectOn();                              // 受理连接（上电初始化由 DeviceControlWork.InitializeMachine() 级联调用）
SubDeviceWeldStatus s = head.WeldStatus;       // 焊接过程态（对外只读）
// 现场排故：当前相位 + 卡了多久
string status = head.StateName + " / " + head.WorkStepName;
```

---

## 关联

- [[modules/DeviceControl]] — 所属架构（8 工作流之一）
- [[architecture/DeviceControlArchitecture]] — 架构规范页（§目录树 / 各工作流表）
- [[modules/LaserWeldHead]] — 焊接头模块（ILaserWeldHeadController 等）
- [[api/LaserWeldHeadController]] — 控制器 API
- [[standards/StepDrivenWorkflow]] — ⛔ 已整页废弃，现行 [[architecture/DeviceControlArchitecture]] §5 · §16
- [[decisions/ADR-034-ThreeStateModelRefactor]] — 三态模型（现行有效）
