---
title: 步骤驱动改造六坑（执行步复位覆盖 / 步内阻塞 / 抽象类级联编译 / 命令槽碰撞 / 失败计数爆表 / 故障快照类型错配）
date: 2026-09-01
tags: [教训, 步骤驱动, 执行步, DeviceWorkflowBase, 并发, 编译]
---

# 步骤驱动改造六坑

> 来源：2026-09-01 全量步骤驱动改造（当时已 accepted，该决策现已删除），8 个文件一次到位的实战总结。
> 规范正文见 [[architecture/DeviceControlArchitecture]]（⛔ 旧标准 [[standards/StepDrivenWorkflow]] 已废弃），本页只记**踩过的坑**与规避动作。
>
> **类名与机制注记（2026-09-02，ADR-028）**：文中的 `SafetyWorkflow` **现为 `DeviceStatusWork`**（`DoAlarm()` 已不存在，报警/急停改由 `DeviceStatusWork` 三线程经 `DeviceControlWork` 单一控制源处置）；`MainDeviceWorkflow` **现为 `DeviceControlWork`**；`MapToDeviceState(_step)` 四态映射已删除，改为 `SetWeldStatus(MapWeldStatus(_phase))`。~~六坑的规避动作本身继续有效~~ → **2026-09-03 起逐坑重新判定，见下方横幅与各坑标注**。
>
> ## ⛔ 2026-09-03 重大前提变更（ADR-030，用户裁定「完全重构」）
>
> 本页六坑建立于 **2026-09-01 旧框架**（`GoStep`/`SetStep` 改步 + 基类常驻监听线程 + 命令变量三槽）。
> 该框架已由架构原档**整体重构取代**（见 [[decisions/ADR-033-RawDesignRefinement20260903]]）：
>
> | 旧机制 | 处置 | 现行 |
> |---|---|---|
> | 基类常驻监听线程（`StartRunLoop`/`BeatMs`） | ⛔ 清除（C1） | 由 `DeviceControlWork` 的 7 条常驻线程驱动 `FlowProcess()` |
> | `GoStep(n)` / `SetStep()` 改步 | ⛔ 清除（C6） | `RunStep` 由每个 `case` 内的 bool 判断推进 |
> | 命令变量三槽 + Pose 监控 | ⛔ 清除（C3） | `CommandCore` 的 `const string` 解析，**不监控 pose** |
>
> **逐坑有效性已在各坑标题下标注**：✅ 仍有效 / ⚠️ 需按新机制重新表述 / ⛔ 机制已删除（仅留思想）。
> 现行规范唯一出处：**[[architecture/DeviceControlArchitecture]] §5 · §7 · §16**。

---

## 坑一：`OnStepChanged` 复位执行步 → `FlowProcess` 内 `SetStep` 后必须立即 `return`

> **⛔ 机制已删除（2026-09-03）**：`OnStepChanged` 与 `SetStep()` 已随旧框架清除（裁定 C6），本坑的**具体写法不再适用**。
> **保留的思想**：改步后必须**立即退出本步**（新范式为 `RunStep = M; break;`），否则同一拍内会连推多步、跳过中间判定。见架构页 §5。

### 现象

单步方法里写：

```csharp
private void StepCompute()
{
    ...
    SetStep(WeldParamControlWorkflowState.Outputting, "计算完成");
    DoSomethingAfter();   // ← 危险
}
```

`SetStep` 触发 `OnStepChanged`，而 `OnStepChanged` 里已经把执行步复位到新阶段的入口步（`Outputting → 20`）。
此时 `DoSomethingAfter()` 若再调 `GoStep(...)`，**会把刚复位的步号覆盖掉**，流程跳到错误分支，且极难复现（依赖基类事件时序）。

### 根因

阶段态（`Step`，对外名片）与执行步（`WorkStep`，内部游标）是**两个独立变量**，靠 `OnStepChanged` 单向同步：
阶段态一变，执行步被强制复位。这是刻意设计——它保证「阶段态 = 阶段入口步」的对应关系始终成立，UI 与运维只需看阶段态就能定位。

### 规避（硬约束）

**`FlowProcess()` 的每个分支中，`SetStep(...)` 必须是最后一句，后面立即 `return`。**

```csharp
SetStep(Outputting, "计算完成");
return;   // 不写 return 也可，但绝不能再出现 GoStep / 写 WorkStep
```

已落地的 8 个文件全部遵守此约定；`SafetyWorkflow.DoAlarm()` 中的恢复分支（`SetStep(Monitoring)` 后 return）是典型正确示例。

---

## 坑二：单步内阻塞等待会**同时**冻结超时判据与指令响应

> **✅ 仍有效**：新架构下 `FlowProcess()` 同样由外部线程**反复调用**，单步内阻塞等待会同时冻结步骤计时与指令响应。规避动作不变。

### 现象

`LineLaserWorkflow` 原有 `SpinWait(Func<bool>, timeout, name)`：内部 `while (!cond) { Thread.Sleep(10); }`。
`MonitorCameraWorkflow` 原有 `AcquisitionCompletedSignal.WaitOne(5000)`。

### 根因（比"卡 UI"更严重）

步骤驱动下，`RunLoop()` 是单线程节拍循环：

```
while (!closed) { ConsumeCommand(); FlowProcess(); Thread.Sleep(BeatMs); }
```

单步内阻塞意味着**同一时刻**三件事一起失效：

1. **超时判据失效** —— `IsStepTimeout()` 靠 `WorkStartTime` 与当前时间比较，但比较动作发生在下一拍，阻塞期间根本没人去比；
2. **指令响应失效** —— `ConsumeCommand()` 在下一拍才执行，急停/中止指令要等阻塞结束才被受理；
3. **阶段态事件延迟** —— UI 看到的状态滞后。

在焊接场景里第 2 条是安全问题：急停指令被阻塞 30 秒才生效。

### 规避

| 原写法 | 改法 |
|---|---|
| `while (!cond) Sleep(10)` 轮询 | 删掉；步内 `if (!cond) { if (IsStepTimeout(x)) FailFlow(...); return; }`，下一拍重入 |
| `WaitOne(5000)` | 改 `WaitOne(0)` **非阻塞探测**，未就绪就 `return` 等下一拍，超时跳 `9xx` |
| `Thread.Sleep(100)` 等外设 | 删除，改为步间推进 |

**周期节拍不算阻塞**：`SafetyWorkflow` 的 50ms、`MotionControlWorkflow` 的 20ms 由基类 `BeatMs` 承载，`Sleep` 在循环体末尾而非步内，不在此列。

---

## 坑三：基类新增抽象成员 → N 个子类**同时**编译失败

> **✅ 仍有效，且风险更高**：批次 1 要把基类契约从 6 项扩到 **17 项**，每新增 1 个抽象成员，**5 个子类必须同时实现**，`LaserWeldHeadWorkflow` 等骨架类也要补（空实现 + `IsRunLoopActive=false`）。见架构页 §15.2 批次 1。

### 现象

给 `DeviceWorkflowBase<TStep>` 加 `protected abstract void FlowProcess();` 与 `protected abstract string GetStepName(int step);` 后，
7 个子类（`MainDevice` / `LineLaser` / `MonitorCamera` / `MotionControl` / `WeldParamControl` / `LaserWeldHead` / `Safety`）**全部报错**：

```
CS0534: "XxxWorkflow" 不实现继承的抽象成员 "DeviceWorkflowBase<...>.FlowProcess()"
```

### 根因

抽象成员的约束是**编译期全量生效**的，没有"部分落地"的中间态。

### 规避

1. **先数清派生类清单再动手**：`grep -rn ": DeviceWorkflowBase<" --include=*.cs`，本次为 7 个；
2. **骨架类也要补**：`LaserWeldHeadWorkflow` 是空壳，也必须给出 `FlowProcess()`（空实现）+ `GetStepName()`，不能漏；
3. **不启线程也要显式声明**：骨架期加 `protected override bool IsRunLoopActive { get { return false; } }`，否则基类会为空壳起一条空转线程；
4. 本项目**无法在本环境编译**，改完必须人工自检：region 配对、抽象方法实现数、using 完整性。

---

## 坑四：Pose 与 Command 编码区间重叠 → 单槽命令变量会**丢指令**

> **⛔ 机制已删除（2026-09-03）**：命令三槽（`_pendingAbort`/`_pendingCommand`/`_pendingPose`）与 `RobotPose` 枚举已清除（裁定 C3），改为 `CommandCore` 的 `const string` 指令。
> **保留的思想**：**指令取值必须全局唯一**。字符串指令同样要保证「同一取值不会被两个语义复用」，否则解析歧义。

### 现象

`DeviceControlWork`（原 `MainDeviceWorkflow`，ADR-028）若把机器人上报的两类信号塞进同一个 `int` 命令槽：

```csharp
private volatile int _pendingSignal = -1;   // ❌ Pose 和 Command 共用
```

### 根因

两个枚举的 int 编码**天然重叠**（`MainDeviceControl/DeviceStateApiCore/CommandTable.cs`）：

| 枚举 | 成员 | 值 |
|---|---|---|
| `RobotPose` | `Unknown` / `HomePose` / `StartSafePose` / `PreWeldPose` / `WeldStartPose` / `PreStopPose` / `WeldStopPose` / `StopSafePose` | -1 / 0 / **1** / 2 / 3 / 4 / 5 / 6 |
| `RobotCommand` | `None` / `PreWeldRequest` / `Abort` | 0 / **1** / 2 |

`RobotPose.StartSafePose = 1` 与 `RobotCommand.PreWeldRequest = 1` **同值**。
共用一槽时后写覆盖先写，机器人"既到位又请求"的复合语义必然丢一半。

### 规避

**分槽存放 + 优先级消费**（`DeviceControlWork` 现为三槽）：

```
_pendingAbort (bool)  >  _pendingCommand (int)  >  _pendingPose (int)
```

`ConsumeCommand()` 按此顺序取快照并清零；另外用显式常量 `NoPendingPose = -1` / `NoPendingCommand = 0` 表达"空"，**不要用 0 当 Pose 的空值**（0 是合法的 `HomePose`）。

---

## 坑五：失败计数在每拍累加 → 阈值瞬间打满

> **✅ 仍有效**：新范式下原语返回 `false` 即停在本步、下一拍重试，同样是**每拍计数**。阈值换算成时长后再定（节拍 `Sleep(10)`，`N=5` 只有 50ms）。

### 现象

`LineLaserWorkflow.ExecuteWorking()` 原逻辑每拍（5ms）调用一次 `HandleFailure()`，连续失败 5 次即报警——
**实际只用了 25 毫秒**，正常焊接的一次抖动就会触发，误报率极高。

### 根因

计数器的累加频率与"节拍"绑定，而节拍是毫秒级的；"连续失败"的语义本应是**持续时长**而非**检查次数**。

### 规避

用**时长**表达，与超时判据统一：

```csharp
if (!IsStepTimeout(FirstResultTimeoutMs)) return;  // 5000ms 未满直接返回
HandleFailure("无有效跟踪结果");
ResetStepTime();                                    // 计一次后重新计时
```

原则：**凡是"连续 N 次"的阈值，先问一句"这 N 次在真实节拍下是多久"**，若不足 1 秒，就该改成时长判据。

---

## 坑六：失败收尾步写故障快照 `State = _step.ToString()` → CS0029

> **⚠️ 需按新机制重新表述**：`State` 现为 `SubDeviceState`（2 态）枚举，焊接进度由 `SubDeviceWeldStatus` + `SetWeldStatus` 承载（三态模型）。故障快照里写步号应落到**故障记录字段**而非状态枚举，类型错配（CS0029）的规避原则不变。

### 现象

`DoFinishFail()` 的 `FaultRecord` 初始化器里写 `State = _step.ToString()`。
`FaultRecord.State` 是**强类型 `DeviceState`**（ADR-027），string 无法隐式转换 → **CS0029 编译错误**，4 个 workflow（LineLaser / Monitor / Motion / WeldParam）同时报错。

### 根因

`FaultRecord` 由 `ProductFileManager/FaultRecoveryManager.cs` 归口后 `State` 收紧为 `DeviceState` 枚举（持久化层才转 `string[]`）；而工作流侧失败收尾样板是照早期 string 版本写的。**本项目无法在开发环境编译**，此类类型错配静态自检脚本查不出（脚本只查文本模式，不查类型），直到用户侧编译才暴露。

### 规避

写 `FaultRecord.State` 一律走设备态映射，与「禁手工 `State=` 赋值」同一口径：

```csharp
State = MapToDeviceState(_step),   // ErrorAborted/Error → Alarm，语义正确
```

原则：**凡跨层搬运枚举/状态，先核对目标属性的真实类型**，不要凭「那边以前是 string」的记忆写样板。

---

## 关联

- [[architecture/DeviceControlArchitecture]] — 现行规范（§5 段位与推进 / §15 落地清单 / §16 代码模板）
- [[modules/DeviceControl]] — 三层状态模型与基类成员表
- [[api/DeviceControlWork]] — 三槽命令变量实现
- [[lessons/StateMachine-DoubleTransition]] — 另一次"状态被后续代码覆盖"的同类教训
