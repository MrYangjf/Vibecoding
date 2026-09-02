---
title: ADR-033 V3 系统架构（统一状态管理 + 两级联动 + 安全互锁 + 故障恢复）
date: 2026-08-19
tags: [决策, 架构, V3, 状态机, 两级联动, 安全互锁, 故障恢复, Stateless, 离线构建]
status: accepted
---

# ADR-033：V3 系统架构（统一状态管理 + 两级联动 + 安全互锁 + 故障恢复）

## 状态
已采纳（2026-08-19）｜**已被取代（2026-09-01 治理标注）**

> **⚠️ 已被取代 —— 架构代际描述方式已废弃**
> - ❌ **失效**：本 ADR 描述的架构已被 [[decisions/ADR-041-MainDeviceControlArchitecture]] 取代。项目**不再按版本代际（V1/V2/V3）描述架构，只维护当前事实**；原 V2/V3 历史架构页已于 2026-09-01 **删除**（其中仍有效的技术要求已并入 [[architecture/DeviceControlArchitecture]] 第 9、10 章）。
> - ✅ **仍有效**：「不引入 Stateless 库」一条（Stateless 5.20.1 仅本地化待评估，不绑定消费代码）。
> - ❌ **连带失效**：其依赖的 [[decisions/ADR-032-UnifiedInitStateMachine]] 状态机体系亦已删除。
> - ✅ **仍然有效**：「不引入 Stateless 库、保持自定义状态机」；「安全互锁 + 故障恢复」作为能力保留（载体改为 `SafetyWorkflow` / `FaultRecoveryManager`，见 ADR-044/046）。
> - **当前真相源**：[[architecture/DeviceControlArchitecture]]（唯一架构规范页）。

## 背景

飞书文档《激光填丝焊接系统完整架构设计（Stateless）》提供了一套基于 `Stateless` NuGet 库的完整目标架构：两级状态机联动（子设备 `DeviceBase`（内嵌 Stateless）↔ 整机 `WeldingWorkflow`）、统一 `IDevice` 契约、设备管理器聚合、安全互锁、故障恢复、工厂 DI。

本项目（AdaWeldSystem）的实际状态：
- 已完成 V2「整机控制软件」演进（6 大集成模块、5 状态机、1 主线程 + 5 子线程）。
- 本会话（2026-08-19）刚完成状态机重构（[[decisions/ADR-032-UnifiedInitStateMachine]]）：引入 `DeviceInitializationStateMachineBase` 模板方法（连接→读配置→状态信号→复位，全 true 方 Standby）+ `MainDeviceStateMachine` 整机聚合 + `InitializationFailed=10` 枚举，两级联动已落地。
- 离线构建约束（[[decisions/ADR-028-NuGetLocalization]]）：所有第三方依赖以本地 DLL 引入，禁止 `PackageReference`。
- 运动实时链路已完成 V3 架构定义（[[decisions/ADR-030-RSICamBoxTrackingArchitecture]]）。

需要一份**系统级 V3 架构设计文档**（[[architecture/DeviceControlArchitecture]]）指导后续设计，并明确「是否采用 Stateless 库」这一关键取舍。

## 决策

1. **V3 系统架构定义**：以「统一状态管理 + 两级状态机联动 + 设备管理器聚合 + 安全互锁 + 故障恢复 + 工厂装配」为 V3 系统架构核心，吸收飞书 Stateless 文档的工程化理念。
2. **保持自定义状态机，不引入 Stateless 库**：
   - 离线构建约束（ADR-028）禁止 `PackageReference`，Stateless 需作为本地 DLL 引入（增加依赖面与打包复杂度）；
   - ADR-032 刚完成的模板方法重构已实现与 Stateless 等价的「两级联动 + 四步初始化固化」能力，无需替换；
   - 自定义状态机更贴合既有 `DeviceState`（11 态）语义与 `InitializationFailed` 终态。
   - **吸收 Stateless 文档的「模式」而非「库」**。若未来评估引入 Stateless，须先解决 ADR-028 离线 DLL 打包。
   - **2026-08-19 更新（ADR-033 修订）**：`Stateless 5.20.1` 已完成 ADR-028 本地化打包——`Stateless.dll` 拷入 `3rdDepend/`、csproj 以本地 `<Reference>` 引入（原违规 `PackageReference` 已移除，`obj/` NuGet 产物已清理）。**该本地化仅作为未来评估的离线前置，不绑定任何消费代码**；「保持自定义状态机」主决策不变。
3. **不强制引入统一 `IDevice` 接口**：以「状态机基类 + 委托注入」为事实统一契约面（子设备继承 `DeviceInitializationStateMachineBase` + 在 Workflow/Controller 注入 `Initialize` 四步委托），避免大改既有模块。
4. **安全互锁与故障恢复作为 V3 目标能力补齐**：参照飞书文档第 10/11 章，新增 `SafetyInterlockChecker`/`SafetyThresholds`/`SafetyInterlockResult` 与 `FaultRecord` + 自动重连/重测策略；当前 `Comm/PLC` 已具备读取能力、状态机已具备 `Alarm`/`Resetting`/`InitializationFailed` 终态，作为落地基础。
5. **工厂装配为可选演进方向**：当前 `MainDeviceThread` 单例 + 各模块单例引导可继续工作；必要时收敛到 `WeldingSystemFactory`（厂商 SDK 实例化须在工厂内，聚合根只依赖抽象）。

## 备选方案

- **直接采用 Stateless 库重建状态机**：能力等价且 DOT 可视化现成，但违反 ADR-028 离线构建约束（需本地 DLL 打包 Stateless + 其依赖），且与刚完成的 ADR-032 重构重复投入，放弃。
- **引入完整 `IDevice` 统一接口重构所有设备**：契约最干净，但改动面大（5+ 设备模块 + 所有调用点），ROI 低，放弃；采用「状态机基类 + 委托」事实契约更为务实。
- **仅写文档不立项 ADR**：V3 系统架构是显著的新架构代际定义，必须记录决策与 Stateless 取舍，放弃「只写不记」。

## 后果

### 正面
- V3 系统架构有明确、可执行的权威文档（[[architecture/DeviceControlArchitecture]]），后续设计有章可循。
- 两级联动、四步初始化固化等能力已落地（ADR-032），根治「未连接也算成功」「整机无条件就绪」两类 Bug。
- 不引入 Stateless，保持离线构建纯净性（ADR-028），降低依赖风险。
- 安全互锁/故障恢复有明确目标规范，可 staged 落地。

### 负面 / 风险
- 缺乏统一 `IDevice` 接口，新设备接入的「契约感」弱于 Stateless 方案，依赖团队遵循 ADR-032 模板约定。
- 安全互锁/故障恢复尚处目标阶段，需后续实现（阶段 B/C），当前未闭环。
  - **2026-08-19 更新**：阶段B（安全互锁：`SafetyInterlockChecker`/`SafetyThresholds`/`SafetyInterlockResult` + 焊接门控）与阶段C（故障恢复：`FaultRecord` + `FaultRecoveryManager` SQLite 持久化 + 重连/重测策略 + `FaultOccurred` 事件）已落地，见 [[modules/DeviceControl]]；此风险项已解除。
- 自定义状态机无 DOT 可视化（Stateless 自带 `ToDotGraph`），状态图需另寻方案。

## 相关页面

- [[architecture/DeviceControlArchitecture]] — 设备控制架构规范页（本 ADR 的承载文档，已按 ADR-041 去版本化）
- [[decisions/ADR-032-UnifiedInitStateMachine]] — 统一初始化状态机继承 + 整设备聚合（两级联动落地）
- [[decisions/ADR-030-RSICamBoxTrackingArchitecture]] — V3 运动实时跟踪架构
- [[decisions/ADR-028-NuGetLocalization]] — 离线构建（禁止 PackageReference，影响 Stateless 取舍）
- [[decisions/ADR-002-CS73-Constraint]] — C# 7.3 语法约束
- [[modules/DeviceControl]] — 状态机模块文档
- [[modules/Workflow]] — MainDeviceThread 聚合根
