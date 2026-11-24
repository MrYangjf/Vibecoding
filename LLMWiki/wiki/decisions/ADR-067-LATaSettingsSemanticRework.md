---
title: ADR-067 LA/TA 工艺语义重构（指令→设置 · 三区改名 · LA 随动换轨 · TA_Retract（原 TA_Recheck））
date: 2026-10-14
updated: 2026-11-18
tags: [ADR, 工艺设置, LA, TA, 随动, 曲线反查, TA_Retract, Radio, ProcessControlPage, LaserWeldHeadWorkflow, WeldAlgorithmsConfig, 默认焦平面]
status: accepted
---

# ADR-067：LA/TA 工艺语义重构（指令→设置 · 三区改名 · LA 随动换轨 · TA_Retract（原 TA_Recheck））

> 业主三项裁定落地：
> ① 激光工艺设置下三模块改名：**跟踪工艺设置(Tracking Settings) / 对焦工艺设置(LA Settings) / 送丝下压工艺设置(TA Settings)**；
> ② **LA 工艺设置与 TA 同形态——是配置项不是指令动作**；LA 三指令语义重写（LA_Pose 纯到位 / LA_Spot 设定光斑反查 / LA_Auto 持续随动），联动关系由系统设置下的光斑-送丝标定曲线（[[decisions/ADR-053-TaLaCurveAndMotorScale|ADR-069 TaLaCurveConfig]]）决定；
> ③ TA 新增回缩指令（**TA_Retract**，原名 TA_Recheck；2026-11-06 定稿为 Auto 反向的纯力矩保持）。
> 另经业主补充裁定：**LA_Spot 与 LA_Pose 都会退出 LA_Auto**；「应用目标光斑」按钮并入保存按钮。

> ⚠️ **历史标注（2026-11-05）**：本条 ADR 中的 `TA_Recheck` 已更名为 **`TA_Retract`（回缩）**，
> 语义由「CSP 绝对定位回 0」重定义为「CST 力矩反向出力（Auto 反向的纯力矩保持，无位置终点）」（见 [[decisions/ADR-082-TaInitFourStepAndAvailability]] D19、D24~D29）。
> 以下「直接回零」实现为**历史记录**，已废止；当前实现以 `MotionControlWorkflow.TaRetract()` 为准。

## 背景：重构前的三处错位

### ① 命名错位

三区标题为「几何参数 / LA 动作 / TA 参数」类旧命名，与业主口径的三模块名不一致。

### ② LA 区形态错位（与 TA 不对称）

| TA 区（ADR-063/082 后） | LA 区（重构前） |
|---|---|
| 参数设置区：ForceN/Pose1/Pose2 三行输入 + 保存/读取 | **动作按钮组**：btnLaAuto / btnLaSpot1 / btnLaSpot2 / btnLaPose1 / btnLaPose2 + lblLaState + btnApplySpotTarget 共 **7 控件** |
| 配置项持久化 | 无参数输入框，按钮直发指令 |

LA 的「光斑1/光斑2/Pose1/Pose2」本质是**标定参数**（供曲线反查与随动基准），却以「按钮」形态呈现，语义错误。

### ③ 指令语义错位

- 旧 `LA_Auto` 只置标志位，定位逻辑与光斑目标脱节；
- `LaApplyTargetSpot()` 为死代码；
- TA 无「回零复查」入口，力矩模式下需手工 StopTorque + 点动回零。

## 决策

### 一、三区改名（ProcessControlPage.Designer.cs，仅文本）

| 控件 | 新文本 |
|---|---|
| `lblGeoSecTitle` | 跟踪工艺设置(Tracking Settings) |
| `lblLaserLaTitle` | 对焦工艺设置(LA Settings) |
| `lblLaserTaTitle` | 送丝下压工艺设置(TA Settings) |

### 二、LA 区形态重构：动作按钮组 → 参数设置区（与 TA 同形态）

- **删 7 控件**：`btnLaAuto` / `btnLaSpot1` / `btnLaSpot2` / `btnLaPose1` / `btnLaPose2` / `lblLaState` / `btnApplySpotTarget`（实例化 + Controls.Add + 属性块 + Click 订阅 + 字段声明全删）。
- **新 10 控件**（5 组标签+输入 + 2 按钮）：
 - `lblLaSpot1`(20,57)「LA Spot1 光斑(mm)」+ `txtLaSpot1`(195,50,110×29)
 - `lblLaSpot2`(330,57) + `txtLaSpot2`(505,50)
 - `lblLaPose1`(20,102)「LA Pose1 位(mm)」+ `txtLaPose1`(195,95)
 - `lblLaPose2`(330,102) + `txtLaPose2`(505,95)
 - `lblSpotTarget`(20,147)「目标光斑(mm)·auto用」+ `txtLaSpotTarget`(215,140)
 - `btnSaveLaParam`(350,138) + `btnReadLaParam`(490,138)（120×34，照 ADR-066 TA 参数区范式）
- `panelLaserLa.Size` (660,157) → **(660,360)**；振镜块整体上移（lblGalvoTitle y=195、6 个 btnGalvo y=235、swEnableGalvoWeave/lblGalvoWeave y=295、lblGalvoState y=340）。
- **快捷 Radio 指令链 `radioQuickLa*` 5 项保留不变**（指令与设置分离，ADR-063 语义延续：LA 的「执行」走快捷 Radio，参数走参数区）。

### 三、LA 三指令语义重写（LaserWeldHeadWorkflow.cs）

| 指令 | 语义 | 实现 |
|---|---|---|
| **LA_Pose** | **纯到位**——仅 LA 轴移动到指定位置，与其他逻辑无关联 | `LaMoveToPose`；`_laFollowActive=false` |
| **LA_Spot** | **设定光斑**——按目标光斑经**曲线 A 反查 LA 基准位**（`TaLaCurveConfig` 正向标定）→ 定位 → `ApplyLaFollow` 单次偏移补偿；成功后 `_laFollowActive=false` **退出随动** | `LaApplySpot` |
| **LA_Auto** | **模式开关**——`LaSpotTargetMm>0` 时先 `LaApplySpot` 定位（失败 return false），然后 `_laFollowActive=true; _lastLaTargetMm=NaN` 进入**持续随动**：运行期按 TA 实时位置经**曲线 B**（`QueryLaOffsetMm`，TA 偏移补偿）实时修正 LA，保持光斑恒定 | `LaAuto` 重写 |

- **联动关系唯一数据源**：系统设置下的 **TaLaCurveConfig** 标定曲线（曲线 A 基准反查 `QueryLaPositionMm` + 曲线 B TA 偏移 `QueryLaOffsetMm`，ADR-053 数据底座），LA/TA 之间为**内部联动**，无外部指令耦合。
- **退出随动的两个入口**（业主裁定）：LA_Spot 成功即退出；LA_Pose 执行即退出。
- **删除死代码** `LaApplyTargetSpot()`。

### 四、TA_Recheck 指令

- 工作流新增 `TaRecheck()`：`_taTorqueActive` 时先 `axis.StopTorque()`，再 `TaMoveTo(0.0, "TA Recheck")` **直接回零**。
- UI：快捷 Radio 第 5 项 `radioQuickTaRecheck`(176,60,130×45)「TA recheck 回零」，`AntdUI.BoolEventHandler` 订阅 `radioQuickTa_CheckedChanged`；原 4 Radio 重排一行（Auto 20 / Break 312 / Pose1 442 / Pose2 548，y=60）。
- `.cs` 加 `DoTaRecheck()` + `case "radioQuickTaRecheck"`；`RefreshActionStates` 加 `radioQuickTaRecheck.Enabled = taReady`（未就绪置灰，ADR-060 范式）。

### 五、参数区读写（ProcessControlPage.cs）

- 新增 `LoadLaParamUi` / `BtnSaveLaParam_Click` / `BtnReadLaParam_Click`，照 **ADR-066 TA 参数区范式**：Spot1/Spot2/Target 必须 >0 校验、Pose1/2 解析失败保旧值、`SaveAlgorithmsZone(AlgorithmsZone.Preset)` 分区落盘。
- `LoadGalvoActionUi` 移除 `txtLaSpotTarget` 回填（归属移交 LA 参数区）；`LoadAlgoConfigOnForm` 加 `LoadLaParamUi()`；删 5 个 `btnLa*_Click` + `btnApplySpotTarget_Click`。

### 六、配置备注同步（WeldAlgorithmsConfig.cs，现役 WeldParamConfig.cs）

5 个 LA 属性 remarks UI 落点同步为「工艺设置页·LA 参数区 txtLaXxx（BtnSaveLaParam 保存）」：`LaSpot1Mm` / `LaSpot2Mm` / `LaPose1Mm` / `LaPose2Mm` / `LaSpotTargetMm`。

## 后果

- **正面**：LA 与 TA 参数区形态对称；LA 三指令语义与业主口径一致；随动基准由标定曲线唯一决定；TA 回零一键化；LA 标定参数可持久化、可读取。
- **负面**：旧快捷 Radio 上的 LA 指令仍直发（参数区保存后才反映新值），操作习惯需适应。
- **中性**：`panelLaserLa` 增高 203px 由振镜块上移吸收，页内无滚动条变化。

## 验证

- **静态校验 57/57 PASS**（含 7 旧控件全链路清除、10 新控件声明/实例化/挂树/订阅四点闭环、三指令语义点、TaRecheck 链路、分区落盘调用、死代码清除）。
- ⚠️ 沙箱无编译器：静态校验 ≠ 编译通过，上机编译需业主 VS 确认。
- 手动验证清单：LA_Pose 纯到位不触发随动；LA_Spot 后随动退出；LA_Auto 定位失败不进随动、成功后随 TA 变化保光斑；TA_Recheck 在力矩激活时先泄力再回零；未就绪时 radioQuickTaRecheck 置灰。

## 背景

（待补：本决策要解决什么问题）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[decisions/ADR-053-TaLaCurveAndMotorScale]] —— 曲线 A/B 数据底座（本 ADR 联动关系唯一来源）
- [[decisions/ADR-057-TaLaActionAndFollowControl]] —— 前批 LA 随动底座（本轮换轨重写语义）
- [[decisions/ADR-063-CommandZoneRadioExclusivity]] · [[decisions/ADR-066-ThreeLayerConvergence]] —— 快捷 Radio 互斥 / TA 参数区范式（本轮 LA 参数区照抄）
- [[api/ProcessControlPage]] · [[api/LaserWeldHeadWorkflow]] · [[modules/WeldParamControl]] · [[architecture/CodeMap]]

## 演进记录

### 2026-11-05 TA_Retract 语义重定义（业主裁定）

- **更名**：`TA_Recheck` → `TA_Retract`（中文「回缩」），`radioQuickTaRecheck` → `radioQuickTaRetract`，UI 文本 `TA_Retract`。
- **语义**：⛔ 不再是 `TaMoveTo(0.0)` 的 CSP 绝对定位；改为 **CST 力矩反向出力**（`TaForceN` 大小 + `TA_TORQUE_DIRECTION` 取反）。
- **清理**：旧名在代码、Designer、Tooltip、日志前缀、api/modules/CodeMap 中零残留；本条 ADR 历史正文保留原名并加历史标注。

### 2026-11-06 TA_Retract 定稿（上一版位置终点判据已被现场否证）

- **定稿语义**：`TA_Retract` = `TA_Auto` 方向取反的**纯力矩保持**——切 CST、开输出、持续出力后即返回；
  ⛔ 无位置终点、⛔ 不判容差、⛔ 不撤力、⛔ 不回 CSP、⛔ 不 `AbsMove` 锁位。
- **作废**：2026-11-05 版的「进入零位容差 → 撤力 → CSP 锁位」及配套的 `WaitTaRetractReach`、`CutTaTorqueAndLock`、
  `InstructionRetractReverseGuardMm`、按行程动态超时全部删除（现场日志「到位 0.032mm / 撤力回 CSP 达成」即否证证据）。
- **口径**：见 [[decisions/ADR-082-TaInitFourStepAndAvailability]] D20/D21/D23（已作废）、D24~D29（定稿）与 [[lessons/TorqueActionNoPositionEndpoint]]。

### 2026-11-18 LA Pose2 → LA 默认焦平面（语义改名 + 初始化后回工作位）

> 业主裁定：「**LA_Pose2 修改为 LA_DefultFocus，意为默认焦平面 LA 的位置，不再是随意设置 LA_POSE**」
> +「在接入焊接头后作为初始化连接结束后回零的默认位置（因为 LA 没有轴的 Home 动作，这里的回零指的是回工作位）」。

**一、语义定位**

| 项 | 旧 | 新 |
|---|---|---|
| 槽位含义 | 第 2 个随意设置的调试位（与 Pose1 同质） | **LA 的默认工作位**（默认焦平面） |
| 控件 | `radioQuickLaPose2` / Text `LA_Pose2` | `radioQuickLaDefaultFocus` / Text `LA_DefaultFocus` |
| 参数区 | `lblLaPose2`（"LA Pose2 位(mm)"）/ `txtLaPose2` | `lblLaDefaultFocus`（"LA 默认焦平面(mm)"）/ `txtLaDefaultFocus` |
| 配置项 | `LaPose2Mm` | `LaDefaultFocusMm` |
| INI 键 | `LA_POSE2_MM` | `LA_DEFAULT_FOCUS_MM`（旧键**一次性迁移**后停写，记一条 Info） |
| workflow | `LaPose2()` | `LaDefaultFocus()` |
| UI 处理器 | `DoLaPose2()` | `DoLaDefaultFocus()` |

- **动作语义不变**（仍是「直接移到配置的 LA 电机绝对位置」，与 `Spot*` 的「设光斑 + 按 TA 推算」相对）；变化的是**业务含义** —— 从"调试位"升为"默认工作位"。
- `LA_Pose1` 保留（仍是另一个调试位）；**TA 侧 `Pose1/Pose2` 属另一条链路，不动**。
- ⚠️ 拼写：代码用标准拼写 `Default`（业主原文写作 `Defult`）。

**二、初始化后自动就位（新增行为）**

- `LaserWeldHeadWorkflow.MoveToDefaultFocus()`：读 `cfg.LaDefaultFocusMm` → `≤0` 跳过（未配置位置）→ 从站未就绪跳过 → **非阻塞**下发（`LaMoveTo`，不等到位，初始化流程不得阻塞）。
- 调用点：`DeviceControlWork` 初始化收尾处，`InitializationCompleted` 事件**之后**主动调用 `_weldHead.MoveToDefaultFocus()`。
- ⛔ **不在 workflow 构造期订阅 `DeviceControlWork.InitializationCompleted`**：`DeviceControlWork` 的 `readonly _weldHead = LaserWeldHeadWorkflow.Instance` 会在其构造期创建 workflow，此时读 `DeviceControlWork.Instance` 会触发整机初始化（违反「构造期禁读 `DeviceControlWork.Instance`」纪律）⇒ 只能由 `DeviceControlWork` 主动调。
- ⛔ **不走手动门禁**（`EnsureManualWeldHeadActionAllowed`）：初始化不是手动动作。
- ⛔ **不属 ADR-099「初始化只连接使能，回零归复位入口」范畴**：LA 无轴 Home，此处是**移到工作位**而非轴回零。
- 失败只记日志，**不影响初始化结论**（初始化结论已在事件前落定）。
