---
title: ADR-042 模块组织范式沉淀（Core + 抽象层 + 实现层 + Manager 四件套）
date: 2026-09-14
tags: [决策, 模块组织, 分层架构, 抽象层, 实现层, Manager, 第三方库封装, ADR-042]
status: accepted
---

# ADR-042 模块组织范式沉淀（Core + 抽象层 + 实现层 + Manager 四件套）

## 状态

已采纳（2026-09-14）。

## 背景

项目在 2026-09 的一轮模块改造中，先后在四个模块独立收敛出了同一种结构，但**每次都是「就地决策」，没有一份跨模块的统一标准**：

| 模块 | 决策 | 结构 |
|---|---|---|
| `MotionControl` | [[decisions/ADR-032-MotionControllerDeltaReplacement]] / [[decisions/ADR-033-ZMotionRemovalAndDeltaLanding]] | `IMotion/` 抽象 + `DeltaEtherCAT/` 实现（含 `Native/`）+ `MontionManager` |
| `LineLaserCam` | [[decisions/ADR-034-LineLaserThreeLayerRefactor]] / [[decisions/ADR-035-LineLaserResponsibilitySplit]] / [[decisions/ADR-036-LineLaserManagerSingleEntry]] | `ILineLaser/` 抽象 + 英莱/虚拟实现 + `LineLaserManager`（唯一实例持有者） |
| `MonitorCam` | [[decisions/ADR-037-MecaVisionMonitorCamera]] | `IMonitorCam/` 抽象 + `MecaVisionCam/` 实现 + `MonitorCamManager` |
| `EmguALG` | [[decisions/ADR-038-EmguALGThreeLayer]] / [[decisions/ADR-039-MonitorCamBoundaryAndEmguALGRefinement]] | `Abstractions/` + 领域算法实现 + `Core/` 算子 + `Manager/AlgorithmManager` |
| `WeldParamControl` | [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] | `Abstractions/WeldAlgorithmBase` + `Algorithms/` 实现 + `WeldParamManager`（**纯自研，无 Core**） |

五个模块结构同构，但「Core 是不是必需」「抽象层目录叫什么」「实现层要不要单例」在每个模块里各说各话。用户 2026-09-14 给出通用裁定，要求把范式固化为项目级标准，避免每新增一个模块都要重新讨论一遍结构。

## 决策

**D1 确立「四件套」范式**：一个功能族模块 = **Core（功能封装核心）+ 抽象层（对外功能与属性）+ 实现层（继承抽象并实现）+ Manager（管理全部实现类对象与数据、持久化配置、对外唯一访问口）**。

**D2 按「是否基于第三方库」分两种场景**：

| 组件 | 场景 A：基于第三方库 | 场景 B：非第三方库（纯自研） |
|---|---|---|
| Core | ✅ **必需** | ⚠️ **按需**——只有需要自成一体的算法结构时才建；原则上不需要，功能类自身的函数与算法直接写在实现类中 |
| 抽象层 | ✅ 必需 | ✅ 必需 |
| 实现层 | ✅ 必需（所有功能都必须继承抽象类实现） | ✅ 必需（同上） |
| Manager | ✅ 必需 | ✅ 必需 |

**D3 沉淀为标准页并路由**：新建 [[standards/ModuleOrganizationPattern]]，由 [[index/index]] 场景速查路由与 §四规范表收口；本 ADR 作为其决策锚点（做法同 [[decisions/ADR-022-CodeSimplificationStandard]]）。

**D4 依赖方向铁律**：抽象层零第三方依赖 → 实现层只被 Manager 装配、只允许出现厂商类型 → Core 只被实现层调用 → 外部只经 Manager 访问。四向单向，禁止反向。

**D5 Manager 四职责固定**：①管理所有功能类对象（唯一持有者）②管理数据 ③持久化配置 ④对外唯一访问口。**Manager 不放流程编排**（流程归 `MainDeviceControl/DeviceWorkflow/`，见 [[standards/WorkflowResponsibilityBoundary]]）。

## 后果

### 正面

- 新增 / 改造模块时不必再逐次讨论结构，直接按标准页第十节检查清单落地；
- 换厂商只动实现层，抽象层与 Manager 不动——这是本范式全部价值的落点；
- `WeldParamControl` 与 `EmguALG` 分别作为场景 A / 场景 B 的完整样本，标准有正反两侧可对照；
- 消除「平行工具类绕过抽象」「工作流持有厂商实例」「配置实现层落盘」三类高频违规（分别对应 H3 / H5 / H7）。

### 负面 / 遗留

- 既有的五个模块中，`MotionControl` 的抽象层目录名为 `IMotion/`、`MonitorCam` 为 `IMonitorCam/`，与标准页建议的 `Abstractions/` 不同名。**本轮不做目录改名**（改名成本与收益不匹配），标准页已明确「同一模块内只用一种命名风格」，两种命名均合规；
- `LineLaserCam` 的第三方封装不是独立 `Core/` 目录而是与实现类同文件，属标准页 §3.1 认可的第三种落地形态；若后续英莱 SDK 调用面扩大，可再评估独立成 `Native/`。

### 约束

- ⛔ 外部代码不得绕过 Manager 直取实现类（禁 `XxxAlgorithm.Instance` 式写法）；
- ⛔ 抽象层不得引入第三方依赖（无 `using` 厂商 SDK、无 `DllImport`、无厂商类型名）；
- ⛔ 同一模块内不保留平行双实现，旧实现整删（ADR-037 裁定先例）；
- ⛔ 不得在 Manager 内加入流程编排，不得在实现层做业务状态判断。

## 相关

- [[standards/ModuleOrganizationPattern]] —— 本标准页（含 H1~H9 硬规则与检查清单）
- [[standards/WorkflowResponsibilityBoundary]] —— 流程与子设备权责（与本页正交）
- [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] —— 场景 B 先例
- [[decisions/ADR-038-EmguALGThreeLayer]] —— 场景 A 先例（Core 独立成目录）
- [[decisions/ADR-037-MecaVisionMonitorCamera]] —— 换厂商只动实现层的实证
- [[decisions/ADR-036-LineLaserManagerSingleEntry]] —— Manager 唯一持有者原则的实证
- [[decisions/ADR-022-CodeSimplificationStandard]] —— 「规范沉淀为标准页」的先例
- [[decisions/ADR-Index]] —— 编号总表
