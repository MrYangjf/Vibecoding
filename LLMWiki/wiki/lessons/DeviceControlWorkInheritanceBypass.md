---
title: 教训 — 独立管控类绕过/复制基类机制的 5 类 BUG（Tag 遮蔽 · 日志出口发散 · 时间戳非原子 · 字段直读 · 停机重启误判超时）
date: 2026-09-03
tags: [教训, 继承, 并发, 日志, 步骤驱动, DeviceControlWork, CS0108, Interlocked, ADR-034]
source: AdaWeldSystem/MainDeviceControl/**（2026-09-03 修复）
---

# 独立管控类绕过/复制基类机制的 5 类 BUG

> **来源**：2026-09-03 对 `MainDeviceControl/` 的一次完整性审计 + 修复，共 5 个 BUG、8 个文件、约 63 处日志调用改造。
> 规范正文见 [[architecture/DeviceControlArchitecture]] 与 [[standards/CodeSimplification]] §三（⛔ 旧标准 [[standards/StepDrivenWorkflow]] 已于 2026-09-03 整页废弃）。本页只记**踩过的坑**与规避动作。
>
> **⚠️ 2026-09-03 机制变更（ADR-036，用户裁定「完全重构」）**：本页记录的 5 类 BUG 与「独立管控类另起炉灶会腐化」的**根因继续有效**，
> 但正文中的成员名已随旧框架清除（裁定 C1/C6）：`GoStep` → **`RunStep` 由 `case` 内 bool 推进**；`IsStepTimeout` → **`TimeOutSeconds`（秒）**；
> `FailFlow` → 超时后 Alarm + RecordFault + 跳 9xx 段；`ResetStepTime` → **`ResetWorkTime()`**。
> 另：`DeviceControlWork` **仍不继承** `DeviceWorkflowBase`（新架构下它是 7 线程编排层，与基类职责本就不同），
> 因此**本页「抄一份会腐化」的警示完全适用**，改码时须让它的步机制与基类保持同步演进。
> 现行规范见 [[architecture/DeviceControlArchitecture]] §4 · §5 · §7.2 · §16。

## 一句话根因

> **独立管控类（`DeviceControlWork` / `DeviceStatusWork`）不继承 `DeviceWorkflowBase`，于是把基类机制「抄」了一份私有实现。
> 抄的那份会随基类演进而腐化——基类后来补的正确性保障（原子读写、非运行态刷新时间戳）永远传导不过去。**

这是「子类重复基类功能导致继承失效」反模式的一个变体：**不是继承后重写覆盖，而是压根不继承、另起炉灶**。
前者至少还能被 `base.` 拉回来，后者连编译期关联都没有，审计时极易漏掉。

---

## 坑一：子类 `private const string Tag` 遮蔽基类 `public object Tag` → CS0108 + 类型对撞

### 现象

`MotionControlWorkflow` 常量区有：

```csharp
private const string Tag = "运动控制工作流";   // 基类已有 public object Tag
```

基类 `DeviceWorkflowBase` 提供 `public object Tag { get; set; }`。两者同名 → 编译器报 **CS0108**（`Tag` 隐藏继承成员）；
更要命的是**类型冲突**：基类是 `object`，子类是 `string`，任何经基类引用访问 `Tag` 的代码拿到的都是另一个东西，多态语义彻底失效。

### 根因

`Tag` 是 `raw/architecture/主控设计.xlsx` 列为**基类契约成员**的字段，但全库 **0 消费者**——
5 个子工作流实际都靠 **`private readonly string _tag` + 抽象属性 `StateName`** 承担日志标识，`Tag` 被架空。

审计时第一反应是「0 消费者 = 死成员，删掉」。**这个判断是错的**，被用户当场纠正：

> `Tag` 的作用我来说明，你沉淀进去：每个流程应该还需要增加 log 的统一写法，**tag 是给 log 用的**。
> 另外两个主设备 `StartWork` 也需要有统一的 log。这里的 log 写法是**将 comm 的 ShowLog 写法封装**。

### 规避（硬约束）

1. **`Tag` 不是死成员，是日志标签的真相源**——保留并收紧为 `public string Tag { get; protected set; }`（`object` → `string`，setter 降为 `protected`）。
2. **子类禁止再声明任何 `Tag` / `_tag` 同名成员**；日志标签只能在构造函数里给基类属性赋值：`Tag = "线激光工作流";`。
3. 每个流程与管控类**必须有且只有一个日志出口**。收敛结果见 [[api/DeviceLog]]。
4. **判据**：审计报「0 消费者」时，先问「它是不是某种横切关注点的载体（日志/权限/序列化）」，
   不要直接下「死成员」结论——尤其当 `raw/` 原档把它列为契约成员时。

> 同类问题另见 [[lessons/StepMemberNameCollision]] 坑二（下沉 `protected const` 后子类残留同名定义 → CS0108）。

---

## 坑二：日志出口发散 —— 63 处 `ShowLog` 各写各的标签

### 现象

改造前 `MainDeviceControl/` 共 **63 处** `GlobalCommData.ShowLog`，标签来源四套并存：

| 写法 | 使用者 |
|---|---|
| 私有 `readonly string _tag = "..."` | 4 个子工作流 |
| 私有 `const string Tag = "..."`（遮蔽基类） | `MotionControlWorkflow` |
| 抽象属性 `StateName` | `DeviceStateBase` |
| 私有 `_tag` / `_simTag` | `DeviceControlWork` / `DeviceStatusWork` |

后果：标签拼写无约束、级别默认值不统一（`MessageLevel.Info` 有的省略有的显式）、
新增流程时「照抄一个 `_tag`」成为默认动作，进一步加剧发散。

### 规避（硬约束）

新建 `AdaWeldSystem.MainDeviceControl.DeviceLog` 静态类作为**唯一设备日志出口**，收敛为四级约定：

| 角色 | 标签来源 | 调用写法 |
|---|---|---|
| 子工作流 | 基类 `Tag` | 基类 `protected void Log(string message, MessageLevel level = MessageLevel.Info)` |
| 独立管控类 | 私有 `_tag` | 本类私有 `Log(...)` → `DeviceLog.Write(_tag, ...)` |
| 状态基座 | `StateName` | `DeviceLog.Write(StateName, ...)` |
| 模拟模式 | `_simTag` | `DeviceLog.Write(_simTag, ...)` |

**验收口径（可用 grep 自检）**：

```
MainDeviceControl/ 下 ShowLog 命中应仅剩 DeviceLog.cs 一处（即封装点本身）
```

设备日志走 `DeviceLog`；**通讯收发报文仍走 `GlobalCommData.ShowCommunicationLog`，二者不得混用**
（连接 `open`/`close` 归设备日志，报文 `content`/`stop` 归通信日志）。

---

## 坑三：`long` 时间戳裸读写 —— 32 位平台非原子

### 现象

```csharp
_workStartTicks = DateTime.Now.Ticks;                       // 写
var start = new DateTime(_workStartTicks);                  // 读
```

`_workStartTicks` 是 `long`。**32 位平台上 `long` 的读写不保证原子性**，可能被拆成两次 32 位操作。
运行线程写、UI/排故/监控线程读，读到「高 32 位新 + 低 32 位旧」的撕裂值 → `DateTime` 构造出一个荒谬时间，
`IsStepTimeout` 直接误判。

> 本机目标框架是 .NET Framework 4.8、平台目标 x64，但**依赖「当前是 64 位」来保证正确性是脆弱假设**——
> 同一份代码被 AnyCPU 编译或部署到 32 位运行环境时即失效，且失效表现为**偶发**，极难复现。

### 规避（硬约束）

```csharp
Interlocked.Exchange(ref _workStartTicks, DateTime.Now.Ticks);   // 写
new DateTime(Interlocked.Read(ref _workStartTicks))              // 读
```

**判据**：跨线程共享的 `long`/`double`/`decimal` 字段（时间戳、计数器、累计量），
一律用 `Interlocked` 或锁，不允许裸读写。`bool`/`int`/引用类型才是天然原子的。

> 相关：[[lessons/CSharp-Language-Pitfalls]] §3.5 泛型类型参数不能声明 `volatile`（CS0677）——
> 想用 `volatile long` 也不行，只能走 `Interlocked`。

---

## 坑四：`_status` 字段直读绕过 `Status` 属性的锁（8 处）

### 现象

`DeviceControlWork` 同时有：

```csharp
private MainDeviceStatus _status;
private readonly object _statusLock = new object();
public MainDeviceStatus Status { get { lock (_statusLock) { return _status; } } }
```

但有 **8 处**业务代码图省事直接读 `_status`：

```csharp
if (_status != MainDeviceStatus.Stop || !_pendingPreWeldRequest) return;   // DoIdle
if (_status != MainDeviceStatus.Running)                                   // OnPoseArrived
if (_status != MainDeviceStatus.EStop && _status != MainDeviceStatus.Alarm) // StartMachine
```

`Status` 属性上的锁形同虚设——**加锁和不加锁的读混用，等于没加锁**。
`SetStatus` 在锁内改，直读方在锁外读，可能读到撕裂/陈旧值，状态门控在竞态窗口内失效。

### 规避（硬约束）

- **除 backing field 声明、属性 getter、`SetStatus` 锁内写块外，任何位置不得出现裸 `_status`**。
- 全部改走 `Status` 属性。
- **例外（必须保留裸读）**：`ClearAlarm` 里的「检查 + 写入」必须在**同一把锁内**完成（TOCTOU），
  写成 `if (Status != Alarm) return; SetStatus(...)` 会拆成两次加锁，中间可插入其他写入。

**自检**：

```bash
grep -n "_status" AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs
# 合法残留仅 5 处：110 声明 / 111 锁对象 / 199 getter / 375-379 SetStatus 锁内块 / 1304-1306 ClearAlarm 锁内块
```

> 通用判据：**字段有配套锁 ⇒ 该字段在锁外出现的每一处都是 BUG**，无一例外。

---

## 坑五：重造的私有步机制缺了基类两处保障 → 停机再启动首拍误判超时

### 现象

`DeviceControlWork` 不继承 `DeviceWorkflowBase`，于是自己抄了一套步机制：
`private GoStep` / `private IsStepTimeout` / `private FailFlow` / `private GetStepName` / 步号常量。
抄的版本**缺了基类后来补的两处正确性保障**：

| 基类 `DeviceWorkflowBase` | 抄到 `DeviceControlWork` 的版本 | 后果 |
|---|---|---|
| `RunLoop` 非运行态 `else { ResetStepTime(); }` | **无 else 分支** | 停机期间时间戳冻结在停机时刻 |
| `Interlocked.Exchange` / `Interlocked.Read` | 裸赋值/裸读（见坑三） | 32 位平台撕裂 |
| `ResetStepTime()` 公有可外部调用 | 无 | 无法在 `StartMachine` 里主动复位 |

**故障链**：停机 5 分钟 → `StartMachine()` 拉起线程 → 首拍 `IsStepTimeout(PoseWaitTimeoutMs)` 用**停机时刻**的时间戳计算 →
`5 min > 60 s` 直接判超时 → 跳 900 失败收尾。**现场表现为「停机久了再开机，一开机就报流程超时」。**

### 根因

旧标准（已废弃，现行 [[architecture/DeviceControlArchitecture]] §5）早已把「非运行态必须持续 `ResetStepTime()`」写为**关键细节（易漏）**，
§七「暂停/非运行态」、§十一审查清单也都列了这一条。

——**但那条规范只对继承基类的工作流生效。** `DeviceControlWork` 是独立管控类，
抄了一份实现就游离在规范覆盖范围之外，**规范写得再全也传导不过去**。

### 规避（硬约束）

1. `RunLoop` 必须补上非运行态分支：

   ```csharp
   if (_running) { ConsumeCommand(); FlowProcess(); }
   else { ResetStepTime(); }   // 非运行态持续刷新，防止恢复瞬间误判超时
   ```

2. `StartMachine()` 内显式 `GoStep(StepIdle)` 复位步号与时间戳——**重启一律从待机步起算**。
3. **审计新判据**：独立管控类若出现与基类同名的私有机制（`GoStep`/`IsStepTimeout`/`FailFlow`/`GetStepName`/`ResetStepTime`），
   逐成员比对两者实现差异，**差异处即为腐化点**，不得默认「抄的时候是一样的」。
4. 长期方向：把这套机制抽成可组合的组件（而非只能靠继承获得），让独立管控类也能复用同一份实现。

> 同源红线见 [[architecture/DeviceControlArchitecture]] §5（单步内禁止无界阻塞等待）与
> 原步骤驱动决策。本坑说明：**规范围不住「抄代码的人」**。

---

## 本次修复清单（验收用）

| # | BUG | 修复 | 文件 |
|---|---|---|---|
| 1 | 子类 `const string Tag` 遮蔽基类 `Tag`（CS0108） | 基类 `Tag` 收紧为 `public string { get; protected set; }`；子类删遮蔽声明，构造函数首行赋值 | `DeviceWorkflowBase.cs` + 5 个子工作流 |
| 2 | 日志出口发散 63 处 | 新建 `DeviceLog` 统一出口；全量改走 `Log(...)` / `DeviceLog.Write(...)` | 新增 `DeviceLog.cs` + 8 个文件 |
| 3 | `long` 时间戳裸读写 | `Interlocked.Exchange` / `Interlocked.Read` | `DeviceControlWork.cs` |
| 4 | `_status` 直读绕过锁（8 处） | 全部改走 `Status` 属性（保留 `ClearAlarm` 锁内 check-and-set） | `DeviceControlWork.cs` |
| 5 | 停机再启动首拍误判超时 | `RunLoop` 补 `else ResetStepTime()`；`StartMachine` 内 `GoStep(StepIdle)` | `DeviceControlWork.cs` |

**附加**：移除 `LaserWeldHeadWorkflow.cs` 中因改造而失效的 `using AdaWeldSystem.Comm;`。
**用户裁定**：其余 0 消费死成员（`CheckDeviceIOSafe()` / `IsStepTimeout()` 无参重载 / `StepStatusText` / `WorkElapsedMs`）**一律保留不删**——
可观测性 API 的 0 消费不构成删除理由。

---

## 关联

- [[api/DeviceLog]] — 本次新建的统一日志出口（标签约定在本页）
- [[standards/CodeSimplification]] §三 — 设备日志规范（内容无符号、记录时机、通讯全记录）
- [[architecture/DeviceControlArchitecture]] — §5 步骤驱动与超时、§15 落地清单、§16 代码模板
- [[api/DeviceControlWork]] — 主设备运行管控（坑三/四/五 的现场）
- [[lessons/StepMemberNameCollision]] — CS0108 的另一形态（常量下沉后子类残留）
- [[lessons/CSharp-Language-Pitfalls]] — C# 语言层陷阱合集
- [[lessons/DeviceWorkflowDualFlowCallerGate]] — 另一条关于「调用方入口」的红线
- [[decisions/ADR-034-ThreeStateModelRefactor]] — 三态模型与独立管控类定位
- [[architecture/DeviceControlArchitecture]] §2 — 独立管控类为何不在继承链上
