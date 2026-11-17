---
title: ADR-095 硬件故障树归属硬件 Manager
date: 2026-11-09
updated: 2026-11-09
tags: [决策]
status: accepted
---

# ADR-095 硬件故障树归属硬件 Manager

> **决策一句话**：硬件故障/报错文本只由持有该硬件的 Manager 产出；流程层只标识失败步骤与硬件对象，UI 只展示成品文本。

## 背景

业主新增硬规则（2026-11-09）：

> 硬件故障/报错内容都归硬件 manager。硬件故障树在各自的硬件 manager 中。流程执行的失败只是表象，核心是硬件失效。

此前同一事实在多层各写一套：流程层直读 `GetStatusWord` / `ReadSlaveStatus` / `BufferMotionStatus` 拼日志，UI 层按 `HeadAlarmStatus` 位拼状态栏，同一报警位出现「驱动板报警」「驱动器报警」「驱动板」三种措辞。判定逻辑被迫与文案耦合，改一处文案要动多层。

## 决策

### D1 三层判据

| 层 | 允许做什么 | 禁止做什么 |
|---|---|---|
| **硬件 Manager**（持有该硬件的类：`MontionManager` / `WeldHeadSlaveDevice` / 相机、线激光、Modbus、温控各自的 Manager） | 读取状态字、报警位、总线态、从站扫描、厂商返回码，产出**可展示的成品诊断文本** | ⛔ 把原始位/码的语义解释责任推给上层 |
| **流程层**（`DeviceWorkflow/`） | 识别「哪一步失败、属于哪个硬件对象」，附 Manager 给出的诊断引用；写流程上下文（拍数、命令值、重试次数） | ⛔ 自己拼硬件细节文案；⛔ 解析状态字/报警位/返回码造句 |
| **UI 层**（`UIDesign/`） | 展示 Workflow / Manager 给的成品文本；按控件宽度**截断**展示 | ⛔ 加工硬件语义；⛔ 按位/按码自行造句 |

### D2 故障树归属

- 每个硬件对象的故障树（报警位定义 → 中文原因、状态字 → 结论、返回码 → 诊断）与其 Manager 同文件、同生命周期。
- 焊接头报警位文本唯一产出点 = `HeadAlarmStatus.Describe()`；温度阈值文本 = `WeldHeadSlaveDevice.DescribeTemperatureThreshold`。
- 轴级诊断文本唯一产出点 = `MontionManager.DescribeAxis*` 一系。
- 线激光诊断文本唯一产出点 = `LineLaserCameraBase.DescribeLastError`（实现层映射，`LineLaserManager` 代理）。

### D3 与既有 ADR 的关系（正面解释 ADR-094 D2）

ADR-094 D2 曾把 `DescribeAxisDiagnosis` / `GetAxisGateReason` / `YGateReason` 留在 `MontionManager` 记为一处「偏离」。本 ADR 将其**升格为通用原则而非个例**：它们留在硬件 Manager 不是妥协，而是本规则的直接推论——轴是硬件，轴的故障文本归持有该轴的 Manager。

同时承接 ADR-093「硬件控制 → `MontionManager`；指令编排 → Workflow；UI 不持轴不解析状态字」：本 ADR 补齐其中的「诊断文本」维度。

## 本轮落地

| 文本产出点 | 从 | 到 |
|---|---|---|
| 报警位原因 | `LaserWeldHeadWorkflow.DescribeAlarm` 私有副本 | `HeadAlarmStatus.Describe()` |
| 温度阈值文本 | `LaserWeldHeadWorkflow` 内联 `string.Format` | `WeldHeadSlaveDevice.DescribeTemperatureThreshold` |
| 状态字文本 | `MotionControlWorkflow` 直读 `GetStatusWord` | `MontionManager.DescribeAxisStatusWord` |
| 缓冲运行证据 | `MotionControlWorkflow` 直读 `ReadSlaveStatus` / `BufferMotionStatus` | `MontionManager.DescribeAxisCspRuntime` |
| PVT 返回码 | `MotionControlWorkflow` 内联 `0x{0:X}` | `MontionManager.DescribeAxisCommandReturnCode` |
| 撤力失败码 | `ProcessControlPage` 拼接 | `MontionManager.DescribeAxisRetractFailure` + Workflow `TaTorqueRetractFailureText` |
| 状态栏报警原因 | `MainPage` / `SystemControlPage` 按位拼接 | `HeadAlarmStatus.Describe()`（UI 仅截断） |

判定逻辑（含 `GetAxisGateReason` 空/非空即放行/拒绝）未改动。

## 第二轮落地（线激光诊断文本，2026-11-09）

业主已确认，本轮实施：

| 文本产出点 | 从 | 到 |
|---|---|---|
| 线激光厂商返回码 | `ILCamPage` / `ILAlgoForm` / `ILParamForm` 自拼 `ret={n}`（Grep 复核实测 **7 处**；首轮登记 6 处，少算 1 处） | `LineLaserCameraBase.DescribeLastError(LineLaserErrorContext)`，经 `LineLaserManager.DescribeLastError` 代理 |
| 连接/初始化/识别失败文案 | `LineLaserWorkflow` 7 处静态句 | 同 7 处追加 Manager 成品描述（`Connection` / `Initialization` / `Recognition` / `ReturnCode`） |

实现要点：

- 抽象层新增只读虚契约 `DescribeLastError(LineLaserErrorContext)`；默认实现明确返回「未提供返回码」，不留空串、不用 `NotImplementedException`。
- `IntelligentLaserCam` 用 `RecordVendorResult` / `RecordLocalFailure` 记录最后一次失败现场，按语境映射；SDK 未给出文字说明的码只报「厂商返回码 N（操作）」，**不编造语义**。
- `VirtualCam` 明确返回「未提供返回码（虚拟相机不走厂商 SDK）」。
- 判定逻辑（何时算失败）未改动，只搬移文本产出位置；界面/日志前缀保持原措辞。

## 只登记、未实施

（无。首轮登记的线激光两项已于第二轮实施，见上节。）

## 后果

- 新增硬件诊断时，先问「这个硬件归谁持有」，文本写进该 Manager，不要再在流程/UI 造句。
- 报警文案只有一处权威，UI 截断展示不算加工语义；完整文本始终可从 Manager 取到。
- 日志文案除上述 3 处已登记变更外，保持逐字等价。

## 相关页面

- [[architecture/DeviceControlArchitecture]]（§10.8 硬件故障树归属）
- [[decisions/ADR-093-FlowTimeoutConfigAndLayering]]（架构归属硬约束）
- [[decisions/ADR-094-ta-single-entry]]（D2 偏离的升格来源）
- [[api/MontionManager]] · [[api/MotionControlWorkflow]]
