---
title: 启动初始化时序门禁：静态构造重入日志 / 界面未就绪开硬件 / UI 回调未判句柄
date: 2026-10-21
updated: 2026-11-11
tags: [lessons, 启动, 初始化, 静态构造, UI就绪, NullReference, 门控, ADR-074]
status: active
source: AdaWeldSystem/Comm/SystemComm/SystemComm.cs + UIDesign/MainWindow/FormMain.cs + MainDeviceControl/DeviceControlWork.cs
---

# 启动初始化时序门禁

> 同类事故已重复出现多次：程序在**界面尚未生成**时开启机器人 RSI，随后 UI 回调访问空控件，启动即崩。

## 现象

- 启动日志停在设备初始化前，随后未捕获异常 / 程序直接退出；
- 或界面已弹出但 RSI 相关面板一刷新就空引用；
- 日志里看到 RSI 已启动，但界面控件（状态条、日志框）尚未创建。

## 根因（四条，缺一即可能崩）

### 1. `GlobalCommData` 静态构造重入日志 ⇒ `_logArgs` 为 null

`Program.Main → new FormMain()` 期间，`MontionManager` 首次访问触发 `GlobalCommData` 静态构造，
构造内 `new CommunicationManager()` 可能回写日志（如 RSI 格式契约升级告警），
而当时静态字段初始化顺序是 `mCommunicationManager` **先于** `_logArgs`：

```csharp
static GlobalCommData()
{
    MachineLog = new Log(...);
    mCommunicationManager = new CommunicationManager();  // ⛔ 内部 ShowLog
    _logArgs = new MessageArgs();                        // ⛔ 还没赋值
}
```

⇒ `ShowLog` 第一行 `_logArgs.strMessage = message` 直接 `NullReferenceException`，整个类型初始化失败。

**正解**：`_logArgs` 必须是静态构造第一句；`ShowLog` / `ShowCommunicationLog` 对 `_logArgs`、
`MachineLog` / `TcpMessageLog` 全部空保护（静态构造期间 `EventInfoHandler` 必然为 null）。

### 2. 界面未就绪就开硬件/通讯

`FormMain_Shown` 本身在窗体显示后，看似安全；但初始化入口可能被其它路径（工具、测试、后续重构、
或把 `InitializeMachine()` 提前到构造函数）调用。一旦 RSI 先起来，收包线程会调用订阅了 UI 的回调。

**正解**：显式的「界面就绪」门控——

```csharp
// FormMain 构造函数：全部子页面实例化完成后
LoadNavAndPages();
GlobalCommData.MarkUiReady();

// DeviceControlWork 初始化步：未就绪则留在本步，IOWork 下一拍重试
if (!GlobalCommData.IsUiReady) { LogOnce("界面尚未就绪 机器人通讯暂缓开启"); return; }
InitializeRobotComm();
```

⛔ 不得在初始化步内 `Sleep` 等 UI（违反 ADR-041 非阻塞范式，且阻塞 IO 扫描线程）。

### 3. UI 回调未判句柄/释放状态

`Invoke` / `BeginInvoke` / 控件赋值在句柄未创建或已销毁时会抛
`InvalidOperationException` / `ObjectDisposedException`；若同时控件字段尚未赋值则为 `NullReferenceException`。

**正解**：所有面向 UI 的回调入口统一判据：

```csharp
if (!IsHandleCreated || IsDisposed || Disposing) return;
```

并给 `Invoke` 段加 `ObjectDisposedException` / `InvalidOperationException` 兜底（页面销毁与回调并发）。

### 4. 计时器在构造函数里 `Start()`

构造期启动的 `System.Windows.Forms.Timer` 只要有消息泵就可能 Tick；若此时页面尚未完全构造/挂载，
Tick 内访问的控件仍可能为空。

**正解**：构造期只订阅 `Tick`，启动放到 `HandleCreated`；`HandleDestroyed` 停表、退订、释放。

## 可推广判据

> ⛔ **判据一：静态构造函数是「无服务区」——任何被它间接调用的方法都必须容忍依赖字段仍为 null。**
> 事件参数、日志实例、配置对象都属于此类；初始化顺序按「被依赖者在前」排，并加空保护双保险。

> ⛔ **判据二：凡是「打开硬件 / 打开通讯 / 启动后台线程」的入口，前面必须有显式就绪门。**
> 门的状态由界面/配置的所有者显式 `MarkReady()`，而不是靠「调用顺序看起来对」；
> 门未开时按拍重试，不 Sleep、不抛异常、不静默跳过。

> ⛔ **判据三：UI 回调第一行永远是生命周期判据，第二行才是业务。**
> `IsHandleCreated / IsDisposed / Disposing` 三个都要，缺一会漏掉销毁瞬间的并发窗口。

> ⛔ **判据四：构造函数里不启动任何周期性 UI 刷新；改由 `HandleCreated` 启动、`HandleDestroyed` 停止。**

## 相关

- [[decisions/ADR-074-RsiNumericProtocolImplementation]]（决策 8：RSI 启动时序门控）
- [[decisions/ADR-041-ResidentFlowNonBlockingParadigm]]（初始化步按拍推进，禁 Sleep）
- [[lessons/UiRefreshUnifiedEntry]]（UI 刷新统一入口）
- [[modules/Comm]] · [[api/CommunicationManager]]

## 追加条目

### 坑 1 · 初始化未结束就判定连接态（2026-11-03）

- **现象**：运控初始化在 IO 工作线程执行，UI 500ms 计时器在主站打开窗口内照常 Tick，读到 `IsInitialized=false` 即记「未连接」并退回自动刷新开关，日志出现在「主站打开成功」之前。
- **判据**：连接态判定只能在初始化结束回调或连接态切换事件里做一次；刷新计时器只跳过刷新，不改开关、不记未连接日志。
- **预防**：UI 侧订阅既有 `StateSwitched` 与 `InitializationCompleted`，经 `InvokeRequired` 封送后走统一判定入口。

### 坑 8 · 坑 8 · 初始化未结束就开常驻线程并变更设备状态（2026-11-17）（2026-11-17）
- **现象**：现场日志 14:09:32 先开 5 模组线程与 IO 监控、紧接着置 IO_INIT，IOWork 首拍在 DoInitializeMachine 尚未受理的窗口跑互锁，把 NoReset 置为 A
- **判据**：凡启动即置位 IO_INIT 的路径，置位前必须先置初始化在途标志（覆盖受理窗口）；IOWork 在初始化在途只允许推进连接链，禁跑互锁/一致性/对齐等一切改状态巡检；模组工作线程与指令线程一律延后到
- **预防**：用独立受理标志（_initAccepted）与链推进标志（_initializing）分离，避免提前置位链标志被重复受理守卫拒绝；两标志在受理处相邻交接，保证 IOWork 全程看到在途态；所有初始化

## 相关页面

- [[index/index]]
- [[decisions/ADR-014-MainDeviceStateSemantics]]
- [[api/SystemControlPage]]

### 坑 2 · 先打「进入第 N 步」日志、判定却被 `&&` 短路（2026-11-05）

- **现象**：现场日志停在「初始化第2步 TA 轴配置加载完成，进入第3步使能」，之后没有任何使能日志、轴未使能；界面已选中 `TA_Auto` 并提示「正在执行 TA_ZeroPose」，其它指令永久被拒。
- **根因**：`bool servoReady = allReady && EnableAxesAfterInit();` 在 `allReady=false` 时不执行右侧；而「进入第3步」日志写在短路之前，形成「日志说有、代码没跑」的假象。ZeroPose 又藏在该方法末尾，于是 `TaAvailable=false` 把所有 TA 指令永久拒绝。
- **预防**：步骤日志必须与**实际执行**同源——先判定并打印原因，再无条件执行并逐项留痕；禁止 `bool ok = 前置 && 执行()` 这种把「前置不满足」和「执行未发生」混成一个布尔值的写法。失败路径必须 `finally` 清零运行标志与单飞登记。

### 坑 3 · 预创建追溯页在窗体 Show 时被「可见性门」放行（2026-11-09）

- **现象**：启动即查当日生产记录并弹「今天 至 今天 没有生产记录」，业主此前已要求「初始化不做数据追溯」。
- **根因（运行期实测，非推断）**：`DataReviewerPage` 用 `VisibleChanged` 当懒加载门，门判 `this.Visible && FindForm().Visible`。但 AntdUI 的 `Tabs` **不隐藏非当前 `TabPage`**：窗体 `Show()` 时全部子页 `Visible=true`，且每个子页都收到 `VisibleChanged`（实测 4 页全部触发，`FindForm()` 非空、宿主 `Visible=True`）→ 双判据整体通过 → 查询 + 空态提示 + `_firstShownLoaded=true`。
  - ⛔ 首版结论「装配期短暂可见」已被现场证伪：真凶发生在 `Show()` 时刻，而非 `Controls.Add`/`AddTabSelect` 装配期。
- **判据**：`Visible` / `FindForm().Visible` / `Created` / `IsHandleCreated` **都不能**表示「初始化完成」——它们在 AntdUI 容器下对非当前页恒为真，对装配期又可能瞬时为真。唯一可用判据是**显式运行态标志**：`GlobalCommData.IsAppRunning`，由 `FormMain` 在首次 `Shown` 的设备初始化结束后 `MarkAppRunning()` 置位。
- **预防**：加载入口收敛为一个 `EnsureLoaded()`，只由用户交互（导航/页签切换、刷新、改区间）调用；⛔ 不订阅 `VisibleChanged` 做加载；`InitPCLDir` 入口再做一次运行态硬闸（拒绝即返回，不查库、不扫记录、不弹空态）；未加载与已查询为空两态文案分离。初始化链路禁止出现任何历史数据查询与空态提示（ADR-078 通用化条目、[[standards/ModuleOrganizationPattern]] H11）。

### 坑 4 · 开闸排在自动回零之后 ⇒ 回零被静默跳过（2026-11-11）

- **现象**：现场日志有「阶段二 使能 送丝力矩电机 成功」，随后是「轴闸门 TA 关闭（初始化未完成（使能阶段尚未结束））」「初始化闸门已打开」，**全程没有一条 TA_ZeroPose 记录**；工艺设置报「TA 指令区不可用：TA_ZeroPose 未到位」，后续 TA 指令全被拒。
- **根因**：`FinishInitialization` 原文顺序是「使能 → 自动 ZeroPose → `LogAxisGateReport` → `MarkInitCompleted`」，而自动 ZeroPose 的守卫 `TaMotionReady` 首行即 `if (!_initCompleted) return false;` ⇒ 守卫恒 false，调用点永不进入；又因 `taConfigOk==true`，`else if (!taConfigOk)` 也不成立，**一条日志都不打**，表现为「没有执行、也没有原因」。
- **判据**：门禁属性的判据链上，任何「开闸」动作若排在**消费该门禁的调用点之后**，该调用点即被永久短路。排查方式：先按日志时序对齐「闸门打开」与「调用点」两条记录，谁在后谁就是元凶。
- **预防**：使能阶段一结束就 `MarkInitCompleted` 开闸，再按轴判定（`TaMotionReady` / `YReady` / `LaReady`）；单轴成功不因整机部分失败被他轴连带。自动回零等「需要门禁放行」的收尾动作必须排在开闸之后；未就绪分支一律 `else` 打真实降级原因，⛔ 不得用 `else if (配置OK)` 制造静默路径。

### 坑 5 · 回零没顶到限位就判完成：判据只看位置/速度（2026-11-11）

- **现象**：现场「回零没有走到极限位顶住就被置为 0」，日志 `TA 回零完成 期望 0.000mm 实测 0.000mm`，随后全机按错误原点跑绝对定位。
- **根因（三条叠加，缺一条都不会发生）**：① 初始化走 `HomeAxis` → `HomeNoBlock()`，**从不查驱动器 `Home_Status`**；② `WaitAxisHomed` 的完成条件只有 `Home_Status==0 ∧ |pos-HomeOffset|≤容差 ∧ 速度≤阈值`，`Home_Status==0` 在「未启动」与「已完成」两种状态下同值；③ `HomeOffset` 缺省 0，增量编码器上电位置也≈0，判据在 t=0 就成立，3 拍（≈48ms）即封完成。`WaitHomeDone` 的 120s 超时在这条路径上**根本没被调用**；即便调用了，它也是首拍 `status==0` 直接 `return true`。
- **判据**：驱动器状态字的「完成值」若同时是「空闲值」，**必须要求先观察到「进行中」再看到「完成」**，否则任何「下发即完成」都会被当成成功。位置/速度只能做二次门，不能替代权威信号。
- **预防**：回零一律走阻塞版 `Home()`（`HomeAxisAndWait`），要求 `Home_Status` 出现 1→0 才置 `HomeVerified`；下发后 2s 内始终为 0 判「未启动」失败；超时/失败一律中止，`TaHomed` 保持 false、不得继续 ZeroPose；成功日志必须带「用时 + 起点 + 终点」以便现场判断是否真的走了行程。

### 坑 6 · 关闭时脉冲型虚拟 IO 置位后扫描线程先停 ⇒ 级联断开从未执行（2026-11-13）
- **现象**：关闭程序只看到「线激光工作流 断开开始/断开完成」，其余模组无任何断开记录；下次上电台达主站初始化失败，表现为「主站初始化超时 超过 30 秒」。
- **根因（两条叠加）**：① `StopMachine()` 按原档语义**只置位脉冲型 `Stop_IO`**，执行体 `DoStopMachine()`（含 `CascadeDisconnect`）由 `thIOWork` 扫描消费；而 `DisposeComponents()` 紧接就 `MachineIOWorkClose()` 关闭扫描线程再 `ClearAllVirtualIo()` 清位 ⇒ **置位的脉冲永远无人消费**，级联断开从未执行。② `MotionControlWorkflow.Dispose()` / `MonitorCameraWorkflow.Dispose()` 全库无调用点 ⇒ 台达主站 `Master_Reset`+`Master_Close` 从未执行，上进程主站残留，新进程 `Master_Initial` 返回非 0。
- **判据**：**凡「置位 → 由他线程消费」的命令，在置位方即将退出的路径上必然丢失**。关闭路径不得依赖任何异步消费者；退出必经的硬件释放（主站关闭、相机停监督、图像缓冲释放）必须由退出链**同步**执行，且每个模组要有可见的断开行，否则「关没关」不可证。
- **预防**：① 关闭链改为同步调用 `CascadeDisconnect()`，不走 `Stop_IO` 脉冲；② `DisposeComponents` 之后显式 `Dispose` 运控与监控相机工作流（前者关台达主站，后者停监督与释放 Mat）；③ 断开日志用模组名（焊接头从站/运动控制器/线激光相机/监控相机）+ 「开始断开（后台执行）」，与 `InitializationLogSpec` 的模组命名口径一致；④ 原生 API 失败码**必须上报**（`CS_ECAT_Master_Initial` 返回非 0 立即失败并带错误码与描述），⛔ 不得记哨兵值后继续等超时——超时是最容易被误读为「时间不够」的错误码。
- **关联**：`DeviceControlWork.DisposeComponents` · `DeltaMontionControl.OpenAndInitialCards` · [[standards/InitializationLogSpec]] · [[api/DeviceControlWork]]

### 坑 7 · 关闭时先断设备后停线程 ⇒ 正常退出打急停；重开线程又立即自退（2026-11-13）

- **现象**：现场退出日志依次是「模组断开 … 已受理」→「整机工作线程关闭标志已置位」→「安全/IO/状态监控停止」→`[Warn] 台达运控全局急停已触发`→`台达运控已关闭`。业主判为「先关设备后关线程，中间触发急停」。另：停机后再初始化，线程建了却立刻退出。
- **根因（三条）**：① `DisposeComponents` 先 `CascadeDisconnect` 再 `MachineFlowWorkClose`，且后者只置标志不等待，线程仍在驱动设备；② `MontionManager.Close()` 无条件 `SetEmergencyStop(true)`，正常退出被记成急停警告；③ `IsCloseWork` 置 true 后全仓无复位点，而 `_workStarted` 被清 ⇒ 重开时新线程进入 `while (!IsCloseWork)` 立即退出，旧线程未退净还会叠线程。
- **判据**：关闭顺序恒为 **线程 → 设备 → 主站**：先通知并 `Join` 等线程退出，再级联断开，最后关主站。凡「置位型退出标志 + 立即重建线程」的组合，必须先把标志复位并 `Join` 旧线程，否则重建的线程是僵尸。
- **预防**：`MachineFlowWorkOpen` 重开前 `JoinModuleWorkThreads()` 再 `IsCloseWork=false`；`MachineFlowWorkClose`/`DoStopMachine`/`DisposeComponents` 三处都在断设备前 `Join` 并打印 `模组工作线程已退出 n/5 条`、`通讯线程已退出 n/2 条`；正常退出不再调用 `SetEmergencyStop`，停机由 `DeltaMontionControl.Close()` 的逐轴 `ServoOff` 完成；Idle 同因去重，避免退出时同一条巡检停止打两次。
- **关联**：`DeviceControlWork.DisposeComponents` · `DeviceControlWork.DoStopMachine` · `MontionManager.Close` · [[modules/DeviceControl]]
