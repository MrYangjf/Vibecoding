---
title: ADR-048 自动运行/手动连接模型（FlowProcess 唯一执行器 + 手动非阻塞连接）
date: 2026-09-02
tags: [决策, 架构, 工作流, 自动运行, 手动连接, FlowProcess, 初始化, 复位, 模拟归并, ADR-048]
status: accepted
---

> ⚠️ **已被取代（2026-09-02）**：本 ADR 的「`ManualOn`/`ManualOff` 手动连接」被新主控设计 `ConnectOn`/`ConnectOff` 契约取代（语义一致，命名收敛），详见 [[decisions/ADR-049-ThreeStateModelRefactor]]。本页保留作历史参考，不再作为现行约束。

# ADR-048：自动运行/手动连接模型（FlowProcess 唯一执行器 + 手动非阻塞连接）

## 背景

用户裁定（2026-09-01 初版，2026-09-02 两度修订）：

1. 基类须具备**初始化流程**、**复位流程**、**手动连接/断开**：初始化 = **阻塞同步**（`InitializeFlow`），统一由主设备级联完成，子设备**不存在「手动初始化/反初始化」**。
2. **自动运行只有 `FlowProcess` 一个入口**（step-case 严格分派，由常驻监听线程按节拍驱动）。原「阻塞式 `AutoRunFlow` + `AutoRun` 自动线程」为旧方式，**已废弃并删除**。
3. **自动运行由主设备发起**：主设备待机后收到通讯指令，在其自身 `FlowProcess` 中推进并管理子设备的 `FlowProcess` 生命周期（级联子设备）。
4. **手动连接/断开由界面 UI 驱动**：主界面按钮即「手动连接/断开连接」（部分设备需加载配置），**与流程无关、只关心设备状态**。手动连接 = 非阻塞，`ManualOn()`/`ManualOff()` **本身由子类内部自起后台线程**执行连接/断开，基类不包线程、不设看门狗。
5. 主设备初始化流程回归基类契约：`PowerOnInitialize` 收敛为私有 `InitializeAllSubDevices`，由 `InitializeFlow`（自动）复用；主设备初始化时若某设备已连接，**跳过连接那一步**。
6. `SimulationWorkflow` 不再独立存在，**全部成员归并到 `MainDeviceWorkflow`**。
7. **复位流程的意义**：a. 设备急停/报警后消除报警，设备处于「需复位」状态，点复位回到待机；b. 设备程序开启后需手动点初始化或通讯告知初始化，保证安全。

> 2026-09-02 三度修订缘由：初版把「阻塞式自动线程 + `AutoRunFlow` 排程器」与「`FlowProcess` 执行器」设为职责正交的两层；经澄清 `AutoRunFlow` 是多余排程层而删除，收敛为单一执行器模型。随后澄清「手动初始化/反初始化」亦为错误设定——子设备初始化一律由主设备初始化流程级联完成，仅保留「手动连接/断开」，故删除 `BeginManualInit`/`BeginManualUnInit`。第三度澄清：手动连接也不该由基类起线程再去调子类 `ManualOn`（线程套线程、流程套流程），而应**由子类 `ManualOn`/`ManualOff` 内部自起后台线程**，基类 `ManualStart`/`ManualStop` 这类中间包装方法直接删除，UI 按钮直调 `ManualOn`/`ManualOff`。
>
> 2026-09-02 四度修订缘由：`ManualOn`/`ManualOff` 不再决定 `WorkflowRunMode` 模式（它只与设备连接/断开相关）。删除 `WorkflowRunMode` 枚举及其配套死代码（`_runMode` 字段 / `RunMode` 属性 / `CanAcceptExternalCommand`）；模式的接入口由后续决策另行定义。
>
> 2026-09-02 五度修订缘由：拆分初始化职责——消除 `InitializeFlow` 中的「复位」职责，复位统一归 `ResetFlow` 单独管控（如 LineLaser 初始化四步第 3 步 `resetDevice` 关激光/关传感器移入 `ResetFlow`，初始化改三步 connect→readConfiguration→verify）；新增 `ClearAlarmFlow` 抽象契约作为「清除报警」动作，与复位正交（本次仅建契约，逻辑待后续实现）。抽象契约 6 → 7。

## 决策

### 1. 自动运行 = FlowProcess 唯一执行器（`DeviceWorkflowBase<TStep>`）

- **无独立自动入口**：删除 `AutoRun()` / `AutoThreadBody()` / `AutoWait()` / `IsAutoAbortRequested` / `RequestAutoAbort()` / `_autoThread` / `_autoAbortRequested` 及 `WorkflowRunMode.Auto` 枚举值。
- 自动运行 = `Initialize()`（到待机）→ `StartRunLoop()` → `FlowProcess()` 按 step-case 自动推进至完成。监听线程每拍 `ConsumeCommand()` + `FlowProcess()`。
- **主设备级联**：主设备在其 `FlowProcess` 某执行步内调子设备既有的启动方法（如 `_lineLaser.Start()`，其内部 `StartRunLoop` + `SetStep(PreWork)`），子设备 `FlowProcess` 自行按步推进，主设备订阅子设备 `StateChanged` 消费结果。

### 2. 初始化 / 手动连接断开

| 契约 | 语义 | 阻塞性 |
|---|---|---|
| `bool InitializeFlow()` | 初始化（上电→连接→读配置→校验→待机），统一由主设备级联；**不含复位职责（复位归 ResetFlow）** | **阻塞同步** |
| `void ManualOn()` | 手动连接（`public abstract`，子类内部自起后台线程） | **非阻塞**（子类自起线程） |
| `void ManualOff()` | 手动断开（`public abstract`，子类内部自起后台线程） | **非阻塞**（子类自起线程） |
| `void ResetFlow()` | 复位（急停/报警后回待机，含设备回初始位置 + 关外设） | 阻塞同步 |
| `void ClearAlarmFlow()` | 清除报警（报警后停止的处理流程，仅清报警态回就绪态） | 阻塞同步 |
| `void FlowProcess()` | 自动运行唯一执行器（step-case） | 节拍重入 |
| `string GetStepName(int)` | 步名映射 | — |

- `ManualOn()` / `ManualOff()` 为 **`public abstract`** 方法，是手动连接/断开的唯一契约，**界面 UI 开关按钮直调**。
- **删除**基类中间包装 `ManualStart()` / `ManualStop()`（原「基类起线程再调子类」造成线程套线程、流程套流程）。
- **后台线程由子类自起**：`ManualOn()` 内部 `new Thread(...)` 起线程执行「连接 + 置待机」，`ManualOff()` 内部起线程执行断开；线程体加 `_manualBusy`/`IsManualConnecting` 防重入标志。基类**不包线程、不设看门狗**。

### 3. 手动连接「快速连接 + 失败反馈 Info」

- 手动连接与流程无关：`ManualOn()` 内部**直接连接设备并置 Standby（Connect 态）**，不跑 `InitializeFlow` 的读配置/校验完整流程（快速连接）。
- 连接失败/异常由子类线程体内记 `MessageLevel.Info` 反馈，**不置 Alarm**，UI 据此刷新为未连接态。
- 主界面设备开关按钮语义：设备未连接 → 点击即快速连接；已连接 → 点击即断开（只关心设备状态，与流程状态无关）。

### 4. 复位 / 清除报警收敛：`Reset()` + `ResetFlow()` 与 `ClearAlarm()` + `ClearAlarmFlow()`

- 基类 `public void Reset()`（记日志 → 调 `ResetFlow()`）。子类 `ResetFlow()` 清命令变量/计数/报警、**关外设并回待机**（复位 = 设备回初始位置）。
- 基类 `public void ClearAlarm()`（记日志 → 调 `ClearAlarmFlow()`）。子类 `ClearAlarmFlow()` 仅清报警态回可复位/就绪态，**与复位正交**（不负责设备回位）。
- **初始化不复位**（2026-09-02 五度修订）：`InitializeFlow` 只做「连接→读配置→校验」，复位职责（如 LineLaser 关激光/关传感器）统一归 `ResetFlow` 单独管控，消除「初始化里藏复位」的职责混淆。

### 5. 模拟模式归并（取代 SimulationWorkflow）

- `SimulationWorkflow.cs` **已删除**（删除前有 tar.gz 备份），csproj 同步移除。
- 成员全部并入 `MainDeviceWorkflow`，对外 API 更名：`IsEnabled→IsSimulationEnabled`、`Enable→EnableSimulation`、`Disable→DisableSimulation`、`Load→LoadSimulation`、`Save→SaveSimulation`；`SimTestMode` 枚举迁至 `MainDeviceWorkflow.cs` 文件尾。
- **ADR-017 的「模拟是 MODE 不是线程」精神保留**，仅「独立 workflow 文件承载」的形态被取代。

### 6. 主设备与子流程初始化/连接

- `MainDeviceWorkflow.InitializeFlow()` = `InitializeAllSubDevices()`（私有，5 步编排，遇已连接设备跳过连接步），返回 `Step == MainDeviceFlowState.SafePose`；级联 `DoStartWelding` 步内 `_lineLaser.Start()`；`PowerOnInitialize` 内 `_lineLaser.Initialize()`（阻塞同步入口）。
- `MainDeviceWorkflow.ManualOn()` 自起后台线程调 `Start()`（启监听线程）；`ManualOff()` 自起后台线程调 `Stop()`（停监听线程 + 级联 `CascadeDisconnect`，级联内改调子设备 `ManualOff()`）。
- `LineLaserWorkflow.ManualOn()` 自起后台线程直接 `ConnectManual` 并置 Standby（不跑完整四步初始化）；`ManualOff()` 自起后台线程 `DisconnectManual` + 关外设回 Uninitialized。
- 其余子类（MotionControl/MonitorCamera/WeldParamControl/Safety/LaserWeldHead）删除 `AutoRunFlow` 与 `BeginManualInit`/`BeginManualUnInit`，`ManualOn`/`ManualOff` 升为 `public` 并各自自起后台线程；MotionControl/LaserWeldHead 骨架保持 TODO 待私有逻辑落地。

### 7. 已知限制（记录在案）

- MotionControl 的 `InitializeFlow()` 为骨架（返回 false），因其初始化依赖主设备级联传入控制器句柄（`Initialize(CamBoxConfig, EncoderAxisConfig, IntPtr)` 专用重载），无参自动初始化暂无法落地。
- **运行模式接入口待定（四度修订）**：`WorkflowRunMode` 枚举及其配套（`_runMode`/`RunMode`/`CanAcceptExternalCommand`）已删除——`ManualOn`/`ManualOff` 不再决定运行模式（只与设备连接/断开相关）。「手动连接态屏蔽主设备指令」这类保护逻辑若后续仍需，将由新模式接入口重建，而非沿用 `WorkflowRunMode`。

## 后果

### 正面
- 自动运行收敛为单一 `FlowProcess` 入口，消除「排程器 + 执行器」双层职责带来的困惑；主设备级联统一走子设备 `FlowProcess`。
- 初始化统一由主设备级联完成，手动仅保留「连接/断开」，语义清晰（连接非阻塞、快速连接、失败反馈 Info 不置 Alarm）。
- 删除 `ManualStart`/`ManualStop` 中间层与基类看门狗，消除「线程套线程、流程套流程」；后台线程职责下沉到子类，基类更薄。
- `Reset()` 收敛后外部调用零破坏；模拟控制器少一个文件、少一个单例。

### 负面
- 基类抽象契约稳定为 7（`InitializeFlow`/`ManualOn`/`ManualOff`/`ResetFlow`/`ClearAlarmFlow`/`FlowProcess`/`GetStepName`），7 子类一次性补齐（坑三：漏一个全项目编译失败）。
- 后台线程由各子类各自实现，防重入标志（`_manualBusy`/`IsManualConnecting`）需各子类自行维护，存在实现发散风险。

## 相关页面

- [[standards/StepDrivenWorkflow]] — 执行步与节拍
- [[modules/DeviceControl]] / [[architecture/DeviceControlArchitecture]]
- [[api/MainDeviceWorkflow]] — 模拟 API 新真相源
- [[api/SimulationWorkflow]] — 墓碑（已删除）
- [[decisions/ADR-017-SimulationModeThroughThreeWorkflows]] — 部分取代
- [[decisions/ADR-047-StepDrivenWorkflow]] / [[decisions/ADR-042-WorkflowStateBaseGeneric]]
