---
title: WeldParamControlWorkflow API 参考（焊接工艺控制流程 · 三态模型）
date: 2026-09-02
updated: 2026-09-14
tags: [API, 工作流, 焊接, 工艺, 功率, 送丝, 振镜, RunStep, SubDeviceWeldStatus, DeviceWorkflowBase, ADR-034, ADR-020, ADR-008]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs
---

# WeldParamControlWorkflow API 参考

> 焊接工艺控制工作流（单例）：接收机器人信息（RobotX）+ 线激光结果（焊缝宽度/特征），计算焊接功率、送丝速度、振镜摆幅、焊接速度并下发给机器人。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：非泛型 `DeviceWorkflowBase`（17 项契约）→ `DeviceStateBase`；`IDisposable` 由基类实现。
> 模块背景见 [[modules/WeldParamControl]]。

> **✅ 2026-09-04 已落地（ADR-020 批次 0~4.4）**：本类已按新架构改码——无自带线程（由 `DeviceControlWork` 模组线程驱动 `FlowProcess()`，`StepIdle` 内消费 `_pendingCompute` 触发变量）、`RunStep` 每 case 靠 bool 推进。旧 `GoStep`/`SetStep`/`WorkStep`/`StartRunLoop`/`ManualOn`/`ManualOff`/`FailFlow`（基类自造）/命令三槽等机制已全部清除，不得据旧内容改码。真编译待 VS（静态自检已通过）。
> 步骤驱动规范见 [[architecture/DeviceControlArchitecture]] §4（17 契约）· §5（`RunStep` 驱动）· §16（代码模板）。
> **ℹ️ 2026-09-14（ADR-008）**：参数与算法承载者 ~~`WeldProcess`~~ → [[api/WeldParamManager]]；配置持久化 ~~`WeldDataManager`~~ → 并入 [[api/WeldParamManager]]；本类逻辑与步位**不变**，仅把旧引用替换为 `WeldParamManager.Instance`。
> **⛔ 同日第三次修订**：线激光引导配置脱离本类——~~`_seamGuide` 字段~~ / ~~`SeamGuide` 属性~~ / ~~`SaveSeamGuide()` 方法~~ **已删除**，`SEAM_GUIDE` 段随配置实例移交 [[api/WeldParamManager]]（`Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`）。本类不再有任何配置实例。

---

## 定位（易错，务必注意）

**不是有连接动作的设备**，而是**设备内部控制焊接工艺的一个流程**（原档 R012 + §8.1）：无实体设备，连接/断开只置一个 bool 变量即返回，不走真实设备连接流程。

```
输入：机器人信息（RobotX）+ 线激光结果（焊缝宽度/特征）
  ↓ WeldParamManager.TriggerAdjustment()（无参，内部取配置与机器人坐标）
分析计算：滑动平滑 + 查找表匹配 + 灵敏度判定
  ↓
输出：焊接功率 / 送丝速度 / 振镜摆幅 / 焊接速度（WeldParamOutput）
  ↓
下发：SendToRobot → KUKA 机器人（顶层 Comm 管控连接，此处只做数据下发）
```

- **不入 `DeviceControlWork` 上电级联**（ADR-023 权责边界），由线激光在 Working 态逐帧触发（单一驱动源，见 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]）。
- `ConnectOn()` 语义为「工艺参数就绪」（置 `Connected`）。
- 本流程是「被外部逐帧触发的一次性计算 + 下发」，**非自推进流程**：`ComputeAndOutput()` 只置 `_pendingCompute`，业务由编排线程按 10 计算 → 20 下发 → 800/900 收尾完成；**上一轮未跑完时新触发被丢弃**（`StepIdle` 才消费），天然节流不堆积。

---

## 公共成员

| 成员 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static WeldParamControlWorkflow` | `Lazy<T>` 单例 |
| `StateName` | `override string` | 对外名片名，返回 `Tag`（日志/事件标识） |
| `IsParamReady` | `bool` | 工艺参数是否已就绪（等价于连接态 `Connect`） |
| `ConsecutiveFailureCount` | `int` | 连续失败次数（**直通** `WeldParamManager.Instance`） |
| `LastOutput` | `WeldParamOutput` | 最近一次计算结果（**类级复用实例**，供 UI 折线图读取） |
| `State` / `WeldStatus` | 基类属性 | 连接态（`SubDeviceState`）/ 焊接过程态（`SubDeviceWeldStatus`） |
| `RunStep` / `StepWorkTime` / `WorkStepName` / `StepStatusText` | 基类属性 | 执行步 / 步骤用时 / 步中文名 / 可观测摘要 |
| `LoadParameters()` | `bool` | 载入工艺参数并进入待机（上电初始化 / 工艺切换时调用） |
| `ComputeAndOutput()` | `bool` | 触发工艺计算与下发（只置 `_pendingCompute`） |
| `Complete()` | `void` | 本轮焊接结束，回到待机（`Standby`） |
| `SwitchParameter(configId)` | `bool` | 切换工艺配置并重新载入参数 |

> `ConfigFileName = "WeldParamControlWorkflow"`（protected override，配置落在 `Config/WeldParamControl/Workflow_XML/` 下）。

---

## 业务相位 `WeldParamControlWorkflowState`（同文件公共枚举）

`_phase`（默认 `Uninitialized`）仅驱动 `FlowProcess` 与可观测性，对外经 `SetWeldStatus(MapWeldStatus(phase))` 映射：

| 取值 | 含义 | 映射 `SubDeviceWeldStatus` |
|---|---|---|
| `Uninitialized`(0) | 未初始化（尚未载入工艺参数） | `NoReset` |
| `Initializing`(1) | 初始化中（载入工艺参数/查找表） | `Working` |
| `Standby`(2) | 待机（工艺参数就绪，等待焊接开始） | `Standby` |
| `Computing`(3) | 计算中（机器人信息 + 线激光结果 → 工艺参数） | `Working` |
| `Outputting`(4) | 下发中（结果下发至机器人/激光器） | `Working` |
| `Holding`(5) | 保持中（连续失败超阈值，暂停调整） | `Working` |
| `ErrorAborted`(6) | 异常终止 | `ErrorAborted` |

> `SetPhase(phase, reason)` 是相位唯一写入口：刷新 `_phase` → `SetWeldStatus(MapWeldStatus(phase), reason)` → 把执行步复位到该阶段入口（`Computing`→10、`Outputting`→20、其余→0）。
> ⛔ 禁止手工 `WeldStatus = ...` / `State = ...` 赋值。映射由私有 `MapWeldStatus(phase)` 承载（取代旧基类 `MapToDeviceState`，已删）。

---

## 执行步表（`RunStep` 驱动）

| 步号 | 常量 | 中文名 | 内容 | 出口 |
|---|---|---|---|---|
| 0 | `StepIdle`（基类） | 待触发 | 消费 `_pendingCompute`（`default` 分支）：置 false → 10；**未触发且 `WeldStatus == Working` 时执行 `TickXlOutput()`（ADR-043：60Hz 节流 XL 输出支路，无新线程）**；否则空转 | → 10 / 持续 |
| 10 | `StepCompute` | 工艺参数计算 | `SetPhase(Computing)` → 校验 `CurrentAutoParam`（空 → `Fail`）→ 连续失败达阈值 → `SetPhase(Holding)` → `wp.TriggerAdjustment()`（无参）+ `FillOutput(wp)` | → 20 / 900 / 0(Holding) |
| 20 | `StepOutput` | 工艺参数下发 | **模拟态**（`DeviceControlWork.Instance.IsSimulationEnabled`）直接置 `_output.Success=true` 返回、**跳过 `SendToRobot`**（ADR-042 模拟红线：不下发真实机器人）；非模拟态 `SendToRobot(_output)` → 成功置 `_output.Success` → 800；失败 → `Fail` | → 800 / 900 |
| 800 | `StepFinishOk`（基类） | 成功收尾 | `SetPhase(Standby)`（结果在 `LastOutput`，订阅方拉取） | → 0 |
| 900 | `StepFinishFail`（基类） | 失败收尾 | `SetPhase(ErrorAborted)` + `IsAlarm` + `RecordFault`（`Process` / `WeldParamStepFail`） | → 0 |

### `FlowProcess()` switch 骨架

```
if (!IsEnable) return;
switch (RunStep) {
    case 10:  if (DoCompute())  SetPhase(Outputting, ...);  break;  // 内部 AdvanceStep(20)
    case 20:  if (DoOutput())   AdvanceStep(800);            break;
    case 800: if (DoFinishOk()) AdvanceStep(0);              break;
    case 900: if (DoFinishFail()) AdvanceStep(0);            break;
    default:  // StepIdle
        if (_pendingCompute) { _pendingCompute = false; AdvanceStep(10); }
        break;
}
```

> ⛔ 全部 case 无 `Thread.Sleep` / `while` 轮询。失败收尾（`Fail`）记录 `_failStep`/`_failReason` 后 `AdvanceStep(900)`（替代已删除的基类 `FailFlow`，原基类 `FailReason`/`FailStep` 已下沉为子类私有字段）。

---

## 关键行为

### ComputeAndOutput()（无参，命令变量模式）

```csharp
public bool ComputeAndOutput()
{
    _pendingCompute = true;   // 只置命令变量，业务由编排线程消费
    return _output.Success;   // 返回的是「上一轮」结果
}
```

**⚠️ 返回值语义（重要）**：计算被挪到编排线程（无自带线程）后，返回的是**上一轮 `_output.Success`**。调用方若需本轮结果，请在 `WeldStatusChanged` 收到 `Standby`/`ErrorAborted` 后读 `LastOutput.Success`（ADR-023 R4「推状态 + 拉数据」）。当前唯一调用方 `LineLaserWorkflow.RunAutoAdjust`（硬件 CAMBOX 未运行时）不使用返回值，无兼容问题。

**关键**：`WeldParamManager.TriggerAdjustment()` 是**无参**方法，内部取用 Manager 持有的 `CurrentAutoParam` / `IsCountType` / `CountNum` / `CurrentRobotX`——**不要给它加参数**（[[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]）。

### LoadParameters()（载入 → Standby）

`SetPhase(Initializing)` → `WeldParamManager.Instance.ReloadCurrentParamValues()` → 校验 `WeldParamManager.Instance.CurrentAutoParam`（null → `SetPhase(Uninitialized)` + false）→ `SetPhase(Standby)` + true；异常 → `SetPhase(ErrorAborted)` + false。

### SwitchParameter(configId) / Complete()

- `SwitchParameter`：`WeldParamManager.Instance.SwitchConfig(configId)` → `LoadParameters()`；异常 → `SetPhase(ErrorAborted)`。
- `Complete()`：`SetPhase(Standby, "本轮焊接完成，工艺控制回到待机")`（本轮焊接结束由主设备调用）。

### 数据链路（焊缝信息即英莱线激光的结果）

```
线激光结果（焊缝宽度）+ 机器人 RobotX
  → WeldParamControlWorkflow.ComputeAndOutput()（只置 _pendingCompute）
  → DoCompute()(10): WeldParamManager.Instance.TriggerAdjustment()【无参】
       → WeldParamAdjustmentAlgorithm.ExecuteAdjustment（平滑 + 查表 + 灵敏度判定）→ FillOutput
  → DoOutput()(20): 模拟态只记录（置 _output.Success=true，跳过 SendToRobot）；非模拟态 SendToRobot → KUKA → 成功收尾
```

### 振镜摆幅：TODO（查表项，非公式）

`CalcGalvoAmplitude(wp)` 当前占位返回 `0.0`（不摆动），不影响其余三项工艺参数下发。规划在 `AutoParamHelper` 新增 `WeaveWidth` **分段查找表**（与焊缝宽度关联，同送丝/速度/功率三张表的匹配方式）——⛔ 不要用自创公式（如 `(SeamWidth - LaserDiameter) / 2`），那是未经验证的推导。

### XL 输出支路（2026-09-23，ADR-043）

`FlowProcess` StepIdle 内 `TickXlOutput()`：仅 `WeldStatus == Working` 时按 `PARAM_OUTPUT_HZ`（默认 60，`Environment.TickCount` 差值节流）输出——

| 宽度来源 | 行为 |
|---|---|
| `Manual`（默认） | 每拍 `TriggerAdjustment()` + `FillOutput()`：固定宽度直查表，**输出全程恒定**，链路自驱不依赖线激光 |
| `Laser` | 按当拍机器人 X 经 `WeldParamManager.TryGetParamOutputAt` 取**已到达的最邻近 XL** 缓存参数 `FillXlOutput()`（无命中保持上一输出）——与焊缝跟踪前置量入键同语义 |

下发统一走 `SendToRobot`（**机器人通讯不可用时其内部自降级为不发送，仅记录**）；模拟态复用工艺参数模拟红线（不下发真实机器人，只更新 `LastOutput`）。**模拟测试零新增代码即触发本链路**（SimTick 推进 X + 虚拟相机产帧触发计算入缓存 + StepIdle 支路按拍输出）。光斑宽度字段随输出更新但不进协议串。详见 [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]]。

---

## 下发通道

`SendToRobot(output)`：`GlobalCommData.mCommunicationManager` 为空 / 机器人未启用（`!IsRobotEnabled`）/ `RobotManager` 为空 → 返回 `true`（无需下发，不视为失败）。否则按协议格式 `P{功率} S{送丝} V{速度} G{摆幅}` 组装 `payload` → `RobotManager.SendRobotData(new KUKARobotData { EStr = payload })`。连接本身由 `CommunicationManager` 管控，本类只做数据下发。

---

## 连接 / 生命周期契约（无实体设备，置 bool 即返回）

| 方法 | 语义 | 状态联动 |
|---|---|---|
| `InitializeOn()` | 阻塞：`_paramReady = LoadParameters()` | `State` = Ready ? `Connected` : `Disconnected`；`WeldStatus=NoReset` |
| `InitializeOff()` | 阻塞：清 `_paramReady` | `State=Disconnected` + `WeldStatus=NoReset` |
| `ConnectOn()` | 非阻塞：置 `_paramReady=true` | `State=Connected` |
| `ConnectOff()` | 非阻塞：清 `_paramReady` | `State=Disconnected` |
| `ResetProcess()` | 线性阻塞链：清触发/报警 → `LoadParameters()`（失败 false） | `WeldStatus=Standby` |
| `ClearStatus()` | 复位前状态清理 | `WeldStatus=NoReset` |
| `ResetWorkTime()` | `ResetStepTime()`（基类） | — |
| `WeldStatusTrans()` | **2026-10-10 ADR-061 修复后**：仅 `NoReset` return（镜像死分支已删）。~~`ErrorAborted` 且相位非 ErrorAborted → `SetPhase(ErrorAborted)`~~ ⚠️ 双源镜像判据已随 ADR-055 消解（`WeldStatus` 单源、级联写入即到位）；ErrorAborted 下输出停走由 FlowProcess「`WeldStatus != Working`」门禁承担，本流程无步号入口需推进；触发点 = `CascadeWeldStatus()` 末尾 | — |

---

## 配置项（`ConfigFileName = "WeldParamControlWorkflow"`）

| 配置元素 | 默认值 | 说明 |
|---|---|---|
| `TimeOutSeconds` | 30 | 基类超时阈值（秒） |

`LoadConfig` / `SaveConfig` **无参**，走 `XdocumentReaderWriter`（XML 文件 `Config/WeldParamControl/Workflow_XML/WeldParamControlWorkflow.xml`）；`SaveConfig()` 末尾 `Config.SaveXdocument()` 落盘（裁定 D1）。工艺参数本体由 `WeldParamManager` 承载，不落本配置。

> **2026-09-11（ADR-037）**：构造函数即调 `LoadConfig()`（此前无调用方）。
> **⛔ 2026-09-14（ADR-008 第三次修订）本类配置不再承载 `SEAM_GUIDE` 段**：线激光引导标定与修正参数
> （`ENABLE_GUIDE` / `AXIS_MM_PER_LASER_MM` / `LASER_ZERO_MM` / `GUIDE_SIGN` / `NO_VALUE_TOLERANCE_MM` /
> `OUTLIER_LIMIT_MM` / `MONOTONIC_WINDOW_MM` / `MONOTONIC_DEADBAND_MM` / `BATCH_SIZE` / `MIN_REMAIN_BUFFER` /
> `FRAME_SECONDS` / `MAX_OUTPUT_INTERVAL_MS` / `MAX_PENDING_POINTS`）
> 随配置实例一并移交 [[api/WeldParamManager]]，落在 `Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml`。
> 原只读属性 `SeamGuide`、方法 `SaveSeamGuide()` 与私有字段 `_seamGuide` **已删除**；
> `LoadConfig` / `SaveConfig` 只读写 `TimeOutSeconds`。配置清单见 [[api/WeldParamManager]]。

---

## 结果类型 `WeldParamOutput`（公共字段，类级复用实例）

| 字段 | 类型 | 说明 |
|---|---|---|
| `LaserPower` | double | 焊接功率（激光功率） |
| `FeedSpeed` | double | 送丝速度 |
| `RobotSpeed` | double | 焊接速度（机器人移动速度） |
| `GalvoAmplitude` | double | 振镜摆幅（**当前 TODO，占位返回 0**） |
| `SpotWidth` | double | **光斑宽度**（毫米，= 采用焊缝宽度 × 系数 W；ADR-043 新增，**暂不下发机器人**，后续供振镜摆幅控制使用） |
| `SeamWidth` | double | 本轮采用的焊缝宽度（平滑后） |
| `RobotX` | double | 当前机器人 X 坐标（真实坐标） |
| `Success` | bool | 计算是否成功 |
| `Timestamp` | DateTime | 时间戳 |

---

## 可观测性

`GetStepName` 映射：`0 待触发` / `10 工艺参数计算` / `20 工艺参数下发` / `800 成功收尾` / `900 失败收尾` / 其余 `未登记步(N)`。

`SubDeviceLog()`（C7 契约）：输出连接态 / 焊接过程态 / 相位 / 功率 / 送丝 / 速度 / 摆幅 / 缝宽。

---

## UI 接入

```csharp
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;

var wf = WeldParamControlWorkflow.Instance;
bool ready = wf.IsParamReady;          // 工艺参数是否就绪
var last = wf.LastOutput;              // 最近一轮结果（功率/送丝/速度/摆幅折线图数据源）
```

---

## 报警停焊冻结（2026-11-17，阶段 7 / ADR-104）

| 项 | 契约 |
|---|---|
| 流程门禁 | `FlowProcess` 顶部判 `WeldStatus == ErrorAborted` 或 `IsAlarmstop` 直接返回；`StepCompute`/`StepOutput` 不再推进，半途报警不会再下发一次，也不会把 `Working` 拉回 |
| 预置门禁 | `PreWork()` 入口判 `IsAlarmstop` 拒单并记 `Warning`「焊前预置被拒绝 当前为报警停焊状态」 |
| 周期输出 | `TickXlOutput` 原就以 `WeldStatus == Working` 为门禁，报警后不再调用 `SendToRobot` |
| 载荷 | `LastOutput` 保持报警时刻值，`UpdateRobotWeldParams` 不再被调用，RSI 回写通道与周期不受影响 |
| 恢复 | 清警只回 `NoReset`；载荷恢复刷新需下次焊接进入 `Working`，不自行续焊 |
| 关联 | [[decisions/ADR-104-rsi-channel-payload-freeze-alarm-stop]] · [[api/DeviceControlWork]] · [[api/CommunicationManager]] |

---

## 关联

- [[modules/WeldParamControl]] — 模块说明（含完整数据链路）
- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（§4 契约 · §5 RunStep 驱动 · §16 模板）
- [[api/WeldParamManager]] — 参数、算法与配置持久化的唯一入口（ADR-008）
- [[api/LineLaserWorkflow]] — 唯一触发方（Working 态逐帧 `ComputeAndOutput`）
- [[api/SeamTrackingAlgorithm]] — 线激光引导轨迹算法（配置由 [[api/WeldParamManager]] 自持自载，本类不再参与）
- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] — 单一驱动源决策
- [[decisions/ADR-013-ThreeStateModelRefactor]]、[[decisions/ADR-035-RawDesignRefinement20260903]] — 三态模型与原档细化裁定
