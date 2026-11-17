---
title: ADR-093 — 流程超时配置化 · 未实现模块防呆 · 架构归属原则
date: 2026-11-06
updated: 2026-11-06
tags: [流程超时, 配置化, 防呆, 架构分层, 死亡等待]
status: accepted
---

# ADR-093 — 流程等待超时配置化与架构归属收口

## 结论

1. **所有流程等待超时收敛到配置对象**：运控侧唯一节点 `DeltaMotionConfig.xml` 的 `ROOT/FLOW_TIMEOUT`，由 [[api/MontionManager]] 持有（`FlowTimeouts`），运行期经 `FlowTimeoutSettings.Current` 只读快照发布；系统设置页「流程等待超时」区为唯一界面入口。⛔ 流程代码禁止再新增固定秒数。
2. **缺省值 = 改造前硬编码值**，上线零行为变化；越界值逐项回退缺省并告警。
3. **未实现模块必须防呆而非放行**：按距离分段统一由 `WeldAlgorithmsConfig.EnsureSupportedSegmentation()` 归一，配置加载降级、保存归一、界面拦截三处共用，⛔ 不得散落重复判断。
4. **架构归属**：硬件控制 → [[api/MontionManager]]；指令编排 → Workflow；UI 只调接口、不持轴对象；配置由专属配置对象持有。

## 业主原话

> `1、焊接头温度这块先不做，还有配置没拿到 2、TODO先不做，这块还没确认，但是做好防呆，不允许切入不让做的模块 3、空catch处理好 4、所有流程上的等待，都做成配置文档…我不希望进程中有几十秒的固定死等待 5、遵循硬件控制由motionmanager管理。指令由workflow管理的原则。尽量不要在UI层写函数接口。6、配置由专属配置对象持有，不单独new。`

## 决策一：温度报警暂缓（不删不臆造）

`WeldHeadSlaveDevice.TemperatureAlarm` 事件、订阅方、主界面报警分支**全部保留**，只加「阈值配置未取得，暂未启用」注释。
⛔ 不臆造阈值、不改报警口径；拿到阈值后再补唯一触发点。
CS0067（事件从未触发）为该状态的**预期警告**，已登记，不作为构建失败。

## 决策二：未实现模块防呆口径

| 环节 | 行为 |
|---|---|
| 配置加载 | 读到「按距离」→ 立即降级为按点数 + `Warning` 说明「不累计焊缝点、不查分段表、输出停旧值」 |
| 配置保存 | 落盘前归一，保证文件里不会出现未实现取值 |
| 界面提交 | 选到「按距离」→ 切回「按点数」+ 同句提示 |

提示文案唯一常量 `DistanceSegmentationUnsupportedReason`；判断唯一入口 `EnsureSupportedSegmentation()`。
⛔ 禁止各处手写 `if (!IsCountType)` 重复判断，⛔ 禁止只提示「非法」而不说明原因。

## 决策三：FLOW_TIMEOUT 键表与缺省值

| 键 | 缺省 | 语义 | 值域 |
|---|---|---|---|
| `INSTRUCTION_DETECT_SECONDS` | 5.0 | 指令状态检测统一超时 | 1~120 |
| `INSTRUCTION_SAMPLE_MS` | 20 | 指令检测采样周期 | 5~200 |
| `INSTRUCTION_STABLE_SAMPLES` | 3 | 位置类连续稳定次数 | 1~20 |
| `INSTRUCTION_TORQUE_SAMPLES` | 2 | 扭矩类确认窗次数 | 1~20 |
| `MOVE_DONE_SECONDS` | 60 | 单轴运动到位超时 | 5~600 |
| `HOME_DONE_SECONDS` | 120 | 单轴回零超时 | 10~1200 |
| `SERVO_ON_SECONDS` | 3 | 伺服使能超时 | 1~60 |
| `AXIS_POLL_MS` | 20 | 轴状态轮询周期 | 5~200 |
| `STOP_SETTLE_MS` | 50 | 停止/复位后沉降 | 0~500 |
| `TORQUE_ENTRY_STABILIZE_SECONDS` | 3.0 | 切 CST 前停稳上限 | 0.5~30 |
| `ZERO_POSE_NO_CHANGE_SECONDS` | 5.0 | TA 零位无变化判失败 | 2~60 |
| `ZERO_POSE_MIN_SECONDS` | 10.0 | TA 零位超时估算下限 | 5~120 |
| `ZERO_POSE_MAX_SECONDS` | 60.0 | TA 零位超时估算上限 | 10~600 |
| `ZERO_POSE_RESULT_WAIT_SECONDS` | 70.0 | 界面等零位结果上限 | 10~900 |
| `SDO_POLL_MS` | 2 | SDO 轮询周期 | 1~50 |
| `SDO_POLL_MAX_COUNT` | 250 | SDO 轮询次数（2×250=500ms） | 20~5000 |
| `SDO_PRE_DELAY_MS` | 10 | SDO 发起前等待 | 0~200 |
| `SDO_MAILBOX_RETRY_MS` | 30 | 邮箱忙退避 | 0~500 |
| `MASTER_INIT_SECONDS` | 30 | 主站初始化超时 | 5~300 |
| `MASTER_INIT_POLL_MS` | 100 | 主站初始化轮询 | 10~1000 |
| `CASCADE_CONNECT_MS` | 10000 | 级联连接无反馈超时 | 1000~120000 |

保留在各自配置对象、**不并入**本节点：线激光 `ROOT/TIMEOUT`（`DATA_STABLE_SECONDS`/`WAIT_WORKING_SECONDS`/`FIRST_RESULT_SECONDS`，已有界面）、各 Workflow `TimeOutSeconds`（已有键）。

## 决策四：消灭固定死等

`ProcessControlPage.DoTaZeroPose` 原「`while + Thread.Sleep(20)` 最长 70s」改为 `ManualResetEventSlim` 等待，
由既有 `TaZeroPoseStageChanged` 在阶段结束时置位；等待上限 `ZERO_POSE_RESULT_WAIT_SECONDS`。
结果判定仍取 `IsTaZeroPoseDone`，⛔ 不得提前上绿。

## 决策五：架构归属原则（硬约束）

| 层 | 允许 | 禁止 |
|---|---|---|
| UI | 调 Workflow / Manager 的对外方法；渲染状态摘要 | 直接持有 `DeltaMontionAxis` 下发使能/回零/停止/移动/点动；自行解析状态字位；写业务等待循环 |
| Workflow | 指令编排、门禁、步骤状态机 | 直接调 EtherCAT 原生 API；自行 new 配置读写器 |
| Manager | 硬件控制、状态摘要、配置持有 | 承载业务指令语义 |
| 配置 | 专属配置对象持有并暴露 | 业务代码 `new INIFile(...)` / `new XDocument(...)` 直接读配置 |

## 决策六：状态字解析单一化 · UI 不持轴 · 配置对象持有（Batch3~4）

### 6.1 A-5 状态字位判断盘点与改造前后等价对照

| # | 位置 | 改造前判断 | 语义 | 改造后 | 等价依据 |
|---|---|---|---|---|---|
| 1 | `MontionManager.DescribeAxisDiagnosis` | `(statusWord & 0x0008) != 0` | 故障位 | `AxisStatus.Parse(statusWord).Fault` | 掩码同为 0x0008 |
| 2 | 同上 | `(statusWord & 0x0004) == 0` | 未使能 | `!AxisStatus.Parse(statusWord).OperationEnabled` | 掩码同为 0x0004 |
| 3 | `WaitAxisAtTarget` | `axis.IsAlarm() \|\| (status & 0x0008) != 0` | 故障位 | `AxisStatus.Read(axis).Fault` | `IsAlarm()` 即同一 6041h 的 0x0008（基类唯一实现、无重写）；Fault 为锁存位，去掉同周期重复读不改变判定 |
| 4 | `WaitAxisHomed` | 同 #3 | 故障位 | 同上 | 同上 |
| 5 | `WaitTaTorqueOn` | 同 #3 | 故障位 | 同上 | 同上 |
| 6 | `WaitTaTorqueOn` | `(status & 0x0004) != 0` | 使能位（出力生效必要条件） | `.OperationEnabled` | 掩码同为 0x0004 |
| 7 | `WaitTaTorqueOff` | 同 #3 | 故障位 | 同上 | 同上 |
| 8 | `DeltaMontionAxis.EnsureDriveTorqueLimit` | `(GetStatusWord() & 0x0004) != 0` | 使能位（写窗口告警） | `AxisStatus.Read(this).OperationEnabled` | 掩码同为 0x0004 |
| 9 | `DeltaMontionAxis.IsServoOn` | `(statusWord & 0x0004) != 0` | 使能位 | 同上 | 掩码同为 0x0004 |
| 10 | `DeltaMontionAxis` 报警复位路径 | `(GetStatusWord() & 0x0008) != 0` | 故障位 | `.Fault` | 掩码同为 0x0008 |
| 11 | `DeltaMontionAxis.SetTorque` | `(statusWord & 0x0004) == 0` | 未使能（拒绝） | `!status.OperationEnabled` | 掩码同为 0x0004 |
| 12 | `DeltaMontionAxis.SetTorque` | `(statusWord & 0x0008) != 0` | 故障（拒绝） | `status.Fault` | 掩码同为 0x0008 |
| 13 | `MontionAxis.IsAlarm`（基类） | `(GetStatusWord() & 0x0008) != 0` | 故障位 | `AxisStatus.Parse(GetStatusWord()).Fault` | 掩码同为 0x0008；基类成为唯一定义处 |

**按代码实点计数**：`MontionManager` 7 处位判断（原估 9 处，差额为 2 个常量声明，非判断点）；`DeltaMontionAxis` 5 处 + 基类 1 处（原估 8 处，差额 3 处为 `Home_Status` 比较，见下）。

**保留差异（不强行合并）**：
- `statusWord == 0` 仍单独判「未取到状态字」，保留在诊断分支；并入解析器会丢失「没读到」与「未使能」的区分。
- `Home_Status`（台达回零状态返回码，取值 0/1/3）不是 6041h 位判断，保留独立比较。
- `SetTorque` 的「先判使能、再判报警」两条独立拒绝日志顺序保留（两种原因对现场处置不同）。

### 6.2 A-2 UI 状态字解析对照

| 位置 | 改造前 | 改造后 |
|---|---|---|
| `SystemControlPage.FillAxisRuntime` | `ushort sw = axis.GetStatusWord(); servo = (sw & 0x0004) != 0; alarm = (sw & 0x0008) != 0;` | `AxisStatus status = MontionManager.Instance.GetAxisStatus(axis); servo = status.OperationEnabled; alarm = status.Fault;` |

等价性：同一寄存器、同两位掩码；改造后为单次读取快照，伺服位与报警位在同一时刻自洽。

### 6.3 A-1 原调用点 → 新入口

| 原 UI 调用点 | 改造前 | 新入口（`MontionManager.TryManualAxisOperation`） |
|---|---|---|
| `FixedServo_Click` | `GetTraceAxis` → `ToggleServo(axis)` | `TraceAxisKeys` + `ToggleServo` |
| `FixedHome_Click` | `GetTraceAxis` → `HomeAxis(axis)` | `TraceAxisKeys` + `Home` |
| `FixedStop_Click` | `GetTraceAxis` → `StopAxis(axis)` | `TraceAxisKeys` + `Stop` |
| `FixedMoveTo_Click` | `GetTraceAxis` → `MoveTo(axis,target)` | `TraceAxisKeys` + `MoveTo` |
| `FixedStep` | `GetTraceAxis` → `StepMove(axis,delta)` | `TraceAxisKeys` + `StepMove` |
| `FixedJog` | `GetTraceAxis` → `JogStart(axis,dir)` | `TraceAxisKeys` + `JogStart` |
| `StopJog` | `StopAxis(_jogAxis)` | `TraceAxisKeys` + `JogStop` |
| `TaServo_Click` | `GetTaAxis` → `ToggleServo(axis)` | `TaAxisKeys` + `ToggleServo` |
| `TaStop_Click` | `GetTaAxis` → `StopAxis(axis)` | `TaAxisKeys` + `Stop` |
| `TaHome_Click` | `GetTaAxis` → `HomeAxis(axis)` | `TaAxisKeys` + `Home` |
| `TaMoveTo_Click` | `DoAbsolute(axis,target)` | `TaAxisKeys` + `MoveTo` |
| `TaStep` | `DoRelative(axis,delta)` | `TaAxisKeys` + `StepMove` |
| `StartTaJog` | `JogStart(axis,dir)` | `TaAxisKeys` + `JogStart` |
| `StopTaJog` | `StopAxis(_taJogAxis)` | `TaAxisKeys` + `JogStop` |
| 字段 `_jogAxis` / `_taJogAxis` | 持有轴对象以便停止 | 已删除（停止时按角色重新解析，语义等价） |

**门禁逐条保持**：① 运控已初始化；② 角色轴已装配。其余保护（伺服使能、`PreMotionCheck` 的急停/总线/报警、同轴单飞、指令超时）仍在下位方法 `MoveTo/StepMove/JogStart/ToggleServo/StopAxis/HomeAxis` 与轴实现内，未改动、未绕过。

**公开面**：未修改任何既有公开签名；新增 `AxisStatus`/`AxisStatusBits`、`MontionManager.GetAxisStatus`、`MontionManager.TryManualAxisOperation`、`AxisManualOperation`、`SimulationConfig`。

### 6.4 配置访问清单与收敛

| 位置 | 读取内容 | 处置 |
|---|---|---|
| `DeviceControlWork.cs`（原 2817/2833） | `Simulation/LineLaserDataFrequencyHz` | 收敛到 `SimulationConfig`（新增，随主控单例一份、读写加锁） |
| `ImageRoiTools.cs`（原 273/297） | `ImageROI/{X,Y,Width,Height,Enabled}` | 收敛到 `ImageRoiConfig`（同文件内专属对象） |
| `WeldParamManager` / `AlgorithmManager` / `CommunicationManager` / `MonitorCamConfig` / `RenderConfig` / `ProductFileRecordManager` / `DeltaMotionConfig` | 各自领域配置 | 保留：它们**就是**该配置的专属持有者 |
| `ConfigSelfHeal` / `XdocumentReaderWriter` / `DeltaControllerConfigImporter` / `XlsxSheetReader` | 修复/读写/导入 | 保留：工具层实现，非业务直接访问 |
| `KukaRsiComm` / `EthernetXmlComm` 的 `XmlDocument` | 通信报文 | 保留：运行时协议解析，不是配置读取 |

### 6.5 分层落地判据（哪类调用必须经过哪一层）

| 判据 | 唯一入口 |
|---|---|
| 任何对 6041h 的位判断（使能/报警） | `IMotion.AxisStatus`（⛔ 禁止再写 `(sw & 0x0004)`） |
| 任何给驱动器的运动/使能/停止/回零下发 | `MontionManager`（UI 经 `MotionControlWorkflow.TryManualAxisOperation`，Workflow 经其语义方法） |
| 任何跨步骤指令（含门禁、单飞、超时等待） | 对应 Workflow |
| 任何配置文件读写 | 对应专属配置对象（⛔ 业务代码不 `new INIFile` / `new XDocument`） |

## 决策七：设备侧等待五项 + 手动轴操作分层（2026-11-08）

### 7.1 设备侧等待接入 `ROOT/FLOW_TIMEOUT`

| 属性 | XML 键 | 缺省 | 值域 | 单位 | 消费点 |
|---|---|---|---|---|---|
| `CameraAcquireSeconds` | `CAMERA_ACQUIRE_SECONDS` | 5 | 1–60 | 秒 | `MonitorCameraWorkflow` 采集等待 |
| `RecordFlushSeconds` | `RECORD_FLUSH_SECONDS` | 5 | 1–60 | 秒 | `ProductRecordBase.FlushPending` |
| `LineLaserCallbackMs` | `LINE_LASER_CALLBACK_MS` | 200 | 20–5000 | 毫秒 | `IntelligentLaserCam.WaitForCallbacksToFinish` |
| `ModbusConnectMs` | `MODBUS_CONNECT_MS` | 3000 | 500–30000 | 毫秒 | `InLaserModbusComm.Open` 建连 |
| `ModbusReadWriteMs` | `MODBUS_READ_WRITE_MS` | 5000 | 500–60000 | 毫秒 | `InLaserModbusComm` 读写超时 |
| `UiRefreshMs` | `UI_REFRESH_MS` | 33 | 10–500 | 毫秒 | **2026-11-11 新增**：仅 UI 刷屏节拍（30Hz），与轮询节拍分离（[[api/SystemControlPage]] / [[api/ProcessControlPage]]） |

- 缺省值 = 改造前硬编码值，**上线零行为变化**；本轮只做"可见可配"，等待逻辑、重试次数、调用线程均未改。Modbus 连接与读写是**两个独立键**，不合并；毫秒项在界面文案中显式标注 `(ms)`。
- 读侧经中立快照 `Comm.SystemComm.DeviceWaitSettings`：真相源仍是 `FlowTimeoutConfig`，避免 Comm / ProductFileControl 反向依赖 `MotionControl.DeltaEtherCAT`。
- 系统设置页「流程等待超时」区内分两组：**流程等待**（6 项）与**设备侧等待**（8 项，含既有线激光 3 项 + 本轮 5 项）。

### 7.2 手动轴操作分层（判据）

| 层 | 职责 | 禁止 |
|---|---|---|
| 轴类 `MotionControl/DeltaEtherCAT/` | 使能/移动/回零/扭矩/状态字读写 | 工艺语义（Auto/Break/Pose/ZeroPose） |
| `MontionManager` | 按配置实例化轴并持有；按角色取轴、门禁、状态摘要、单轴基础指令 | 角色级应用动作分发（点动/步进/走位的"按角色选择"） |
| `MotionControlWorkflow` | 应用层运动指令封装（唯一业务动作所在地） | 绕过轴类的寄存器时序 |
| UI | 发起后台调用、消费状态与结果 | 持轴对象、写动作封装、解析状态字位 |

- `TryManualAxisOperation` 由 `MontionManager` 迁至 `MotionControlWorkflow`，签名不变；UI 两个调用点改调工作流。
- `MontionManager` 保留的 `MoveTo/StepMove/JogStart/ToggleServo/HomeAxis/StopAxis` 定性为**单轴基础指令**（接受 `MontionAxis` 参数、无角色/工艺语义），沿用 ADR-073「轴控制唯一出口」，不视为应用动作。
- UI 只读摘要新增 `MontionManager.TryGetAxisReadout(axisName, out position, out lastCommand, out servoOn, out fault)`；`SystemControlPage` 不再出现任何轴对象类型。

### 7.3 门禁核对（如实记录）

| 项 | 迁移前 | 迁移后 |
|---|---|---|
| 运控已初始化 | `MontionManager.TryManualAxisOperation` 内 | Workflow 同名方法内，等价 |
| 角色轴已装配 | 同上 | 同上，改调公开的 `GetDeltaAxisByKeys` |
| `PreMotionCheck`（急停/总线/报警） | 轴类内，由基础指令触发 | 未改动、未绕过 |
| 同轴单飞 | **手动路径本就没有**（`TryBeginAxisInstruction` 仅用于 TA/LA/ZeroPose 等跨步骤指令） | 原样，未新增 |
| 指令超时等待 | **手动路径本就没有**（下发即返回） | 原样，未新增 |

> 决策六中"同轴单飞、指令超时仍在下位方法与轴实现内"的表述对手动路径不成立，以本节为准。

### 7.4 依赖方向自查结果

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` 仍含 `ZeroPose` 工艺语义（`StartZeroPoseMove` / `WaitZeroPose` / `RunZeroPose` / `TaZeroPoseTag`）→ **遗留项，已于决策八关闭**。
- `MontionManager.TryManualAxisOperation` 已移除；保留 6 个单轴基础指令（见 7.2）。
- `UIDesign/SystemControlPage.cs` 已无轴对象/状态字位运算；`UIDesign/ProcessControlPage.cs` 仍有 4 处 `MontionAxis` 局部变量（L846/L912/L1433/L1438）→ **遗留项，已于决策八关闭**。
- `MotionControlWorkflow` 内 `DeltaMontionAxis` 调用均为应用动作壳（取轴→基础指令→等待），未直接写寄存器/状态字位。

## 决策八：轴类剥离 ZeroPose · UI 轴对象清零 · 配置属性中性化（2026-11-08）

### 8.1 结论

1. **轴类是纯基础能力层**：只保留 CSP 绝对定位（`AbsMoveNoBlock`）、按参数起停（`AxisStop`）、位置/速度/状态字读取、回零状态查询（`GetHomeStatus`）、扭矩（`SetTorque`/`StopTorque`）、CSP 缓冲族、`SetSoftTargetReach`。⛔ 不得再出现 `ZeroPose` / `Pose` / `Auto` / `Break` / `Retract` 等工艺词。
2. **工艺编排唯一归属 `MotionControlWorkflow`**：`RunTaZeroPoseAfterInit` / `RunTaZeroPoseSync` / `TryHomeAxisWithWait` / `TryMoveAxisToTarget`。
3. **`MontionManager` 只留"中性运动能力"**：`TryMoveAbsoluteNoBlock`（参数校验 + 已在位直通 + 8 参下发）、`WaitAxisAtTarget` 7 参重载（显式超时 / 无变化早停 / 可免速度稳定）、`TryGetAxisNameByKeys`（只读轴名解析）。⛔ 不得带工艺命名。
4. **UI 不持轴对象**：`ProcessControlPage` 已无 `MontionAxis` / `DeltaMontionAxis` 类型，改为调 Workflow 动作入口 + Manager 只读摘要（拒因码 + 证据字符串）。

### 8.2 原位置 → 新位置（门禁逐条标注 原有 / 新增）

| 门禁 | 原位置 | 新位置 | 性质 |
|---|---|---|---|
| 伺服/运动前置检查（急停/总线/报警） | 轴类 `StartZeroPoseMove` | 轴类 `StartMove`（`AbsMoveNoBlock` 内建） | **原有（下沉一层，未删）** |
| 已在容差内直通 | 轴类 `StartZeroPoseMove` | `MontionManager.TryMoveAbsoluteNoBlock` | **原有** |
| 到位容差 + 速度稳定 | 轴类 `WaitZeroPose` | `MontionManager.WaitAxisAtTarget`（7 参重载） | **原有** |
| 按行程/速度估算超时 | 轴类 `WaitZeroPose` | Workflow 估算 → 传 `WaitAxisAtTarget` | **原有** |
| 位置长时间无变化早停 | 轴类 `WaitZeroPose` | `WaitAxisAtTarget`（`noChangeSeconds`） | **原有** |
| TA 零位单飞 `_taZeroPoseRunning` | `MontionManager.RunTaZeroPose` | `MotionControlWorkflow.RunTaZeroPoseAfterInit` | **原有** |
| 运控未初始化拒绝 | UI `MoveAxisHome` / `MoveAxisToTarget` | Workflow 同名入口 | **原有** |
| 角色轴未装配拒绝 | UI 同上 | Workflow 同上 | **原有** |
| 按轴门禁 `GetAxisGateReason` | UI 同上 | Workflow 同上 | **原有** |
| 同轴单飞 `TryBeginAxisInstruction` | UI 同上 | Workflow 同上 | **原有** |
| 指令超时 `WaitAxisAtTarget`(5s) | UI 同上 | Workflow 同上 | **原有** |
| 失败减速停止 | UI 同上 | Workflow 内 `mgr.StopAxis` | **原有** |
| 拒因码 `AxisReject*`（6 个） | — | Workflow 对外契约 | **本轮新增（仅为把原 UI 分支的判定结果外传，判定条件本身未变）** |
| 手动点动单飞 / 指令超时 | — | — | **原本就没有，本轮未加** |

### 8.3 配置属性中性化（XML 键不变）

| 旧属性 | 新属性 | 挂载类 |
|---|---|---|
| `ZeroPoseNoChangeSeconds` | `PositionReachNoChangeSeconds` | `FlowTimeoutConfig` |
| `ZeroPoseMinSeconds` | `PositionReachMinSeconds` | `FlowTimeoutConfig` |
| `ZeroPoseMaxSeconds` | `PositionReachMaxSeconds` | `FlowTimeoutConfig` |
| `ZeroPoseResultWaitSeconds` | `PositionReachResultWaitSeconds` | `FlowTimeoutConfig` |
| `ZeroPoseMm` | `WorkOriginMm` | `DeltaTaHomeConfig` |

⛔ **XML 键 `ZERO_POSE_*` / `TA_HOME_ZERO_POSE_MM` 保持原样** —— 现场配置契约，改名等于让旧 XML 失效（静默回落缺省 = 行为语义变化）。

### 8.4 保留项（未中性化，需业主确认是否处理）

`DeltaMotionConfig` 气缸三字段 `RetractSensorName` / `RetractOutputName` / `RetractActionName` 与 XML 键 `RETRACT_SENSOR` / `RETRACT_OUTPUT` / `RETRACT_ACTION_NAME` 保留：判定为「气缸缩回」通用气动语义，非焊接工艺指令。若要求一并中性化，需同步改 `MotionConfigImporter` 的 CSV 列与现场 CSV。

## 决策九：TA_ZeroPose 重试闭环 · 失败上色 · 单飞逾期释放（2026-11-09）

### 9.1 三条必修（复现路径 → 修复点 → 验收口径）

| 缺陷（复现路径） | 修复点 | 验收口径 |
|---|---|---|
| 手动成功不写回：初始化 ZeroPose 失败 → TA 降级 → 手动点 ZeroPose → 到位后 `TaAvailable` 仍 false | `TaZeroPose` 已在位分支 + `TaZeroPoseWorker` 成功分支均调 `MarkTaZeroPoseSucceeded()` | 到位后 `TA_Auto` **立即**可点 |
| 已在位空等 `PositionReachResultWaitSeconds`（默认 70s） | 已在位分支也先 `MarkTaZeroPoseRunning(true)`，产出「开始 → 结束」完整序列 | 秒级结束并呈成功态 |
| 失败不上红（「从未执行」与「执行失败」不可区分） | 新增 `IsTaZeroPoseAttempted`（跑过没有）+ `IsTaZeroPoseFailed`（结果如何），UI 四态落色 | 自动失败呈红且 Tooltip 带原因；从未执行不上色 |

### 9.2 状态位与上色口径

- `_taZeroPoseRunning` 的清除覆盖全部出口：`TaZeroPose` finally（未移交后台）、worker finally、`RunTaZeroPoseSync` finally。
- 四态：运行 → 中性灰；成功 → 绿；失败 → 红；被切换中止（跑过但既未到位也未失败）→ 复位底色，⛔ 不算失败。
- ⛔ 上色只改 `BackColor`（`Fill` 仅 `Transparent`），成功绿 / 运行中性灰 / 未执行白的既有约定不变。

### 9.3 单飞逾期释放（A-5）

`TryBeginAxisInstruction` 对占用超过 `AxisInstructionLeaseSeconds`（600s）的登记项自动移除并告警，防异常路径漏 `EndAxisInstruction` 致该轴永久 BUSY；⛔ 不改公开签名与拒绝文案。

### 9.4 Batch B 等价精简（7 处，台账见 logs/log.md 同日条目）

`TaPose1`/`TaPose2` 合并为 `TaMoveToPreset(bool)`；删私有转发壳 `ExitTaTorqueMode(string)`；`TryBeginAxisInstruction` 单次 `TryGetValue` + 单次 `elapsed`；`DoTa*`/`DoLa*` 直接返回；提取 `PostToUi` / `HandleAxisReject` / `ReportAxisResult`；两条与行为不符的注释纠偏。

## 演进记录

- **2026-11-09**：决策九落地（手动 ZeroPose 成功写回 / 已在位不再空等 / 失败上色 / 单飞逾期释放）+ Batch B 等价精简 7 处；
  `MontionManager` 新增只读 `IsTaZeroPoseAttempted` / `IsTaZeroPoseFailed`（新增成员，未改既有签名）。
- **2026-11-08**：决策八落地（轴类剥离 ZeroPose / UI 轴对象清零 / 配置属性中性化）；
  `DeltaMontionAxis` 删除 `StartZeroPoseMove`/`WaitZeroPose`/`RunZeroPose`/`StopZeroPoseMotion`/`TaZeroPoseTag`；
  决策 7.4 列出的两条遗留项（轴类 ZeroPose 语义、`ProcessControlPage` 4 处轴对象）**已关闭**。
- **2026-11-06**：Batch1（温度暂缓 / 分段防呆 / 空 catch 注释补全）与 Batch2（FLOW_TIMEOUT 21 键 + 事件驱动替换 70s 忙等）落地；
  [[api/SystemControlPage]] 新增 6 项超时输入，标题由「线激光等待超时」改为「流程等待超时（秒 / ms）」。
- **2026-11-06**：Batch3（A-5 状态字单一解析器 + A-2 UI 改调摘要）与 Batch4（A-1 手动轴操作下沉、A-4/第 6 条配置对象持有）落地；
  `SystemControlPage` 不再持有轴对象，`ProcessControlPage` 仅保留只读轴名查询；详见决策六。


### 2026-11-08 · 决策 D7 · 手动轴操作下沉到 MotionControlWorkflow；设备侧等待五项接入 FLOW_TIMEOUT；流程等待分区
- **变更**：手动轴操作下沉到 MotionControlWorkflow；设备侧等待五项接入 FLOW_TIMEOUT；流程等待分区按语义分两组
- **理由**：业主 2026-11-08 三条要求：应用动作必须唯一归属 Workflow，UI 不持轴对象；相机/落盘/线激光/Modbus 等待需可见可配
- **影响**：MontionManager 删除 TryManualAxisOperation（等价入口 MotionControlWorkflow.Instance.TryManualAxisOperation）

## 相关页面

- [[api/MontionManager]] · [[api/SystemControlPage]] · [[api/ProcessControlPage]] · [[api/WeldParamManager]]
- [[modules/MotionControl]] · [[architecture/CodeMap]]
- [[decisions/ADR-092-ExceptionLoggingAndShellRemoval]]
