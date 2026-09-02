---
title: ADR-041 — 设备控制架构重构：MainDeviceControl（设备态四态 + 流程态分离）
date: 2026-08-28
status: accepted
tags: [决策, 架构, 设备控制, 状态机, 设备态四态, 流程态, MainDeviceControl, 重构]
---

> ⚠️ **已被取代（2026-09-02）**：本 ADR 的「设备四态 + 流程态分离」设计被新主控设计三态模型取代，详见 [[decisions/ADR-049-ThreeStateModelRefactor]]。本页保留作历史参考，不再作为现行约束。

# ADR-041 — 设备控制架构重构：MainDeviceControl

> **2026-08-28 修订**：原决定「`Workflow/Device/` 仅保留 `SimulationWorkflow.cs`、`WeldActionRecord.cs`」已被后续整理推翻——`Workflow/` 目录**整目录删除归零**：SimulationController 更名 **SimulationWorkflow** 迁入 `MainDeviceControl/DeviceWorkflow/`（namespace `AdaWeldSystem.MainDeviceControl.DeviceWorkflow`）；WeldActionRecord 迁入 `PCLOperate/RunFileRecord/`（namespace `AdaWeldSystem.PCLOperate.RunFileRecord`）。

> **2026-08-28 二次修订（同日）**：应用户要求完成两项收敛——
> ① **Safety 命名空间与文件夹解散**：`Safety/` 子目录删除，SafetyFlow / SafetyInterlock（含 FaultCategory/FaultRecord/SafetyInterlockResult/SafetyInterlockChecker）/ FaultRecoveryManager 平铺至 `DeviceWorkflow/`，命名空间统一为 `AdaWeldSystem.MainDeviceControl.DeviceWorkflow`；`SafetyMonitorThread` 更名 **SafetyWorkflow**（流程命名一律 Workflow，不用 Thread）。
> ② **WorkflowState.cs 删除**：共享状态契约不再单独成文件，按归属拆入各工作流文件内（命名空间 `AdaWeldSystem.MainDeviceControl.DeviceWorkflow`）：线激光 2 类型→LineLaserWorkflow.cs、监控 10 类型→MonitorCameraWorkflow.cs、CAMBOX 3 类型→MotionControlWorkflow.cs、SimTestMode→SimulationWorkflow.cs；零消费的 WorkflowSignalCode / WorkflowCompletedEventArgs / WorkflowErrorAbortedEventArgs / WorkflowManualStoppedEventArgs 直接删除。`AdaWeldSystem.Workflow` 命名空间**不复存在**。

> **2026-08-31 补充**：编译验证暴露同日遗留问题——`DeviceState` 枚举与子命名空间同名，C# 名称解析在父作用域先命中子命名空间，`MainDeviceControl` **子树内**的 7 个文件（6 工作流 + DeviceWorkflowBase）using 指令无法生效（CS0118）。修复：各文件在**命名空间声明内部**加 `using DeviceState = AdaWeldSystem.MainDeviceControl.DeviceState.DeviceState;` 别名（子树外 UI 文件的普通 using 有效，不受影响）。全项目扫描确认这是唯一一处类型名/命名空间段名碰撞。详见 [[guides/Namespace-Compilation]]（2026-08-31 修订）。

## 背景

重构前，设备状态管理分散在三套并存的结构中，职责重叠、语义混乱：

| 旧目录 | 问题 |
|---|---|
| `DeviceStateMachine/` | 9 个文件。11 态 `DeviceState` 枚举（Uninitialized/Initializing/Standby/Working/Completed/Alarm/Resetting/Offline/Online/Error/InitializationFailed），设备态与流程进度混为一谈 |
| `Workflow/Device/` | 状态机 + 工作流职责重叠，新旧实现并存（如 `MotionControlWorkflow` 与 `LaserCamBoxTrackingWorkflow` 并存） |
| `DataModels/` | 共享数据模型，实际仅 3 个类被引用，其余为孤儿 |

核心矛盾：**设备态与流程态没有分离**。同一个 `DeviceState` 枚举既用来对外承诺"设备能否用"，又用来表达"流程走到哪一步"，导致：
- 枚举不断膨胀（堆到 11 态）
- UI 判断逻辑同一设备可能得出矛盾结论
- 新增业务流程就要改公共枚举，违反开闭原则

## 决策

### 1. 三目录合并为 `MainDeviceControl`

```
MainDeviceControl/
├── DeviceState/     （设备态 + 流程态基类）
├── FlowState/       （工作流基类）
├── DeviceWorkflow/  （具体工作流 + Safety/）
└── WorkflowState.cs （共享状态枚举契约）
```

> **2026-09-01 目录后续收敛（决策主体仍然有效）**：上表 `DeviceState/` 与 `FlowState/` 两个**物理目录**已合并为 `DeviceStateApiCore/`（4 个文件原地迁移，无增删），`WorkflowState.cs` 亦早已删除。**命名空间刻意不变**（仍为 `...DeviceState` / `...FlowState`），故本 ADR 关于「设备态四态 + `MapToDeviceState` 映射 + 禁手工 `State=` 赋值」的全部结论不受影响。现行目录树以 [[architecture/DeviceControlArchitecture]] 第 2 章为准。

- `DeviceStateMachine/`、`DataModels/` 整目录删除
- `Workflow/Device/` 仅保留 `SimulationWorkflow.cs`、`WeldActionRecord.cs`（**2026-08-28 修订：两文件均已迁出，目录归零**，见顶部修订记录）
- `DataModels` 中被引用的 3 个类迁入 `LaserWeldHead/LaserWeldHeadData.cs`

### 2. 设备态收敛为固定四态

```csharp
public enum DeviceState
{
    Disconnect = 0,  // 未连接/未初始化
    Connect    = 1,  // 已连接/待机
    Work       = 2,  // 工作中（所有流程进程态）
    Alarm      = 3   // 报警
}
```

**固定不变、不可扩展**——这是对外承诺。

### 3. 流程态 = 设备工作态

业务相关、可丰富、各设备不同。每个工作流定义自己的流程态枚举。

**映射规则（强制）**：

```
流程「未初始化」        → Disconnect
流程「初始化完成/待机」 → Connect
流程「进程中的状态」    → Work
流程「报警」            → Alarm
```

各工作流实现 `MapToDeviceState(step)` 统一承载，**禁止手工 `State = ...` 赋值**（唯一例外：基类四个生命周期方法中的语义赋值，因那四处本身就是规则定义）。

### 4. 单继承线性基类链

```
DeviceStateBase → WorkflowStateBase → DeviceWorkflowBase → 具体 Workflow
```

### 5. 机器人/PLC 连接归属顶层 Comm

`MainDeviceWorkflow` **只做信号交互**（收 `RobotPose` / 下发 `DeviceCommand`），不直接持有连接。连接由 `CommunicationManager` 管控。

### 6. `WeldParamControlWorkflow` 不入上电级联

定位为「设备内部控制焊接工艺的流程」而非设备，由 `LineLaserWorkflow` 触发，保持单一驱动源（ADR-013）。

## 影响与实施

### 代码改动

| 类别 | 内容 |
|---|---|
| 新增 | `MainDeviceControl/` 15 个 .cs 文件 |
| 重写 | `MonitorCameraWorkflow`（移植健康巡检）、`MotionControlWorkflow`（移植 CAMBOX 引擎）、`MotionManager`（去状态机依赖） |
| 删除 | `DeviceStateMachine/`（9 文件）、`Workflow/Device/` 旧 5 文件、`DataModels/`（4 文件） |
| UI 重映射 | `FormMain` / `ILCamPage` / `MonitorCamPage` / `MotionControlPage` / `MainPage` 共 5 文件 |
| csproj | 删除 21 行失效条目，新增 15 行 |

### UI 接入约定

区分两个属性（**易错点**）：

- `Instance.Step` — **流程态**（各工作流自己的枚举），用于判断"是否运行"、显示进度
- `Instance.State` — **设备态**（四态），用于判断"能否操作"、销毁前是否断开

### 验证结果（本环境无编译器，静态自检）

12 项全 PASS：关键类型解析 14/14、csproj 无缺失无重复、无未注册孤儿、无 `Dispose(bool)` 违规（ADR-001）、继承链完整、设备四态正确、映射覆盖 4/4、工艺不入级联、UI using 5/5、旧符号清零、无 V2/V3 表述、旧目录已删。

## 修正记录（用户纠正，重要）

本 ADR 落地过程中，用户对三处理解作出纠正，均为架构语义性纠正：

1. **设备态数量**：初版写成 3 态（漏 `Alarm`）。用户纠正为**四态**，并明确"流程的报警对应设备的报警"。
2. **`WeldParamControlWorkflow` 定位**：初版按"有连接动作的设备"实现。用户纠正：**没有固定设备连接，它是设备中控制焊接工艺的一个流程**，职责是接收机器人信息+线激光结果→计算功率/送丝/摆幅/速度→发给机器人。
3. **焊缝信息来源**：初版称"来自 EmguALG 的 `PipelineManager`"。用户纠正：**焊缝信息就是英莱线激光的结果**，英莱回调已含 `FeatureY/FeatureZ`（特征点）与 `Width0/Width1`（宽度），只是此前没有让它直接给焊接参数赋值。

另外纠正一处**方法签名误解**：`WeldProcess.TriggerAdjustment()` 是**无参**方法（内部用已暂存的 `_lastSeamFeature`/`_lastRobotX`），初版误加了参数。

## 反例警示（勿重犯）

| 反例 | 正确做法 |
|---|---|
| 给 `TriggerAdjustment()` 加参数 | 无参调用，特征值已由 `OnAlgorithmCompleted` 暂存 |
| 自创振镜摆幅公式（如 `(SeamWidth - LaserDiameter)/2`） | `WeaveWidth` 是查表项，TODO 占位返回 0.0，等分段表落地 |
| 在具体 workflow 内 grep 不到 `ManualStart`/`StateSwitched` 就判定为缺陷 | 这些由基类提供，属正常（本次曾误判） |
| 把 `Instance.State`（设备态）改成 `Instance.Step`（流程态）一刀切 | 两者语义不同，按用途选择；读四态处应保持 `.State` |

## 关联

- 架构页：[[architecture/DeviceControlArchitecture]]（本 ADR 的承载文档，**唯一架构规范页**）
- 后续决策：[[decisions/ADR-042-WorkflowStateBaseGeneric]]（2026-08-31 流程态基类泛型化：Step/SetStep/StateChanged/映射下沉基类；本机 `DeviceFlowState` 更名 `MainDeviceFlowState` 下沉 `MainDeviceWorkflow`）
- 模块页：[[modules/DeviceControl]]、[[modules/Workflow]]、[[modules/WeldParamControl]]
- 前置决策：[[decisions/ADR-013-WorkflowAsAdjustmentDriver]]、[[decisions/ADR-030-RSICamBoxTrackingArchitecture]]、[[decisions/ADR-036-SafetyModuleConsolidation]]
