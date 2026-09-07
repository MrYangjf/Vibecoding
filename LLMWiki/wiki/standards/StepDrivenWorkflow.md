---
title: 步骤驱动工作流标准（已废弃）
date: 2026-09-01
tags: [规范, 工作流, 步骤驱动, 已废弃, ADR-030]
status: deprecated
---

# 步骤驱动工作流标准（StepDrivenWorkflow）— ⛔ 已废弃

> ## ⛔ 本页已整页废弃，不再作为任何执行依据
>
> **废弃时间**：2026-09-03（用户裁定，见 [[decisions/ADR-033-RawDesignRefinement20260903]]）
> **废弃原因**：本页建立于 2026-09-01 的旧框架之上（命令变量三槽 + 常驻监听线程 + `WorkStep`/`GoStep`），
> 该框架已由 2026-09-03 的架构原档（`主控设计.xlsx` + `激光焊接系统业务流程图.pdf`）
> **整体重构并取代**。用户裁定：「新结构文档为全新设计和细化，不是对旧文档的补充，是完全的重构」。
>
> ### 现行唯一规范
>
> **[[architecture/DeviceControlArchitecture]]** —— 设备控制架构唯一规范页：
> - **§5** `RunStep` 驱动与超时控制（取代本页第二、五、六、七章）
> - **§4** 流程基类 17 项契约（取代本页第四章）
> - **§7** 运行编排与 7 线程模型（取代本页第 2.2 章「常驻监听线程」）
> - **§16** 参考实现与代码模板（**改码前必读**，取代本页第六、十二章）
>
> **⚠️ AI 与开发者注意**：本页保留仅为留存迁移上下文，**不得据本页改码**。
> 全文历史版本可从 git（`Vibecoding.git`）取回。

---

## 一、本页曾规定什么 → 现行做法对照

改码时若在本页看到下列旧概念，**一律按下表右列执行**：

| # | 本页旧规定（⛔ 废弃） | 现行做法（✅ 以架构页为准） | 见 |
|---|---|---|---|
| 1 | 基类自带**常驻监听线程**（`StartRunLoop` / `BeatMs` / `RunLoopPriority`） | **删除**。子流程无自带线程，由 `DeviceControlWork` 的 5 条常驻线程驱动 `FlowProcess()` | 架构页 §4.5、§7.2 |
| 2 | **命令变量三槽**（`_pendingAbort` > `_pendingCommand` > `_pendingPose`） | **删除**。机器人指令由 `CommandCore` 的 `const string` 解析 | 架构页 §3.1 |
| 3 | 监控机器人 pose（`RobotPose` 枚举 + `RobotPoseCode`） | **不监控**——设备由机器人指令驱动，无权限管理机器人状态 | 架构页 §3.1、§7.3 |
| 4 | 改步唯一入口 **`GoStep(n)`**；`SetStep()` 后立即 `return` | `RunStep` 由**每个 `case` 内的 bool 判断**推进，`true` 才进入下一步 | 架构页 §5 |
| 5 | 执行步字段 **`WorkStep` + `WorkStartTime`** | **`RunStep` + `StepWorkTime` + `TimeOutSeconds`（秒）** | 架构页 §4.1、§5 |
| 6 | 超时来源：全局 `CommenData.CylinderMoveTimeOut`（**毫秒**） | 基类属性 `TimeOutSeconds`（**秒**）——注意单位换算 | 架构页 §5、§16.7 |
| 7 | 步骤号段位（0 待机 / 10-99 / 100-199 / 700-799 / 800-899 / 900-999） | 段位约定**沿用**，但步号常量与推进方式按 `RunStep` 新范式 | 架构页 §5 |
| 8 | 基类统一 `Log` 出口 | 每个子流程**各自重写** `SubDeviceLog()`（`public`） | 架构页 §2、§4.1 |
| 9 | 手动接口 `ManualOn` / `ManualOff` | `ConnectOn` / `ConnectOff`（非阻塞）；另有阻塞组 `InitializeOn` / `InitializeOff` | 架构页 §4.3、§4.4 |
| 10 | 配置读写带 `XmlReader` / `XmlWriter` 参数（参考实现写法） | **无参** + 本项目 `XdocumentReaderWriter`；子设备 workflow 各自持有配置路径 | 架构页 §4.6、§16.8 |
| 11 | 清料抽象成员 `ClearProduct()` | **暂不实现**，待结合 `ProductFile` 另立方案 | 架构页 §16.7（裁定 D2） |

## 二、仍然有效的部分（已并入架构页，此处仅索引）

本页以下条目本身不依赖旧框架，已被吸收进架构页，**以架构页表述为准**：

| 原章节 | 内容 | 现行位置 |
|---|---|---|
| 六、单步写法三范式 | 瞬时动作步 / 等待完成步 / 分支派发步 | 架构页 §5 + §16.3 子流程模板 |
| 七、超时判据 | 步骤计时 + 超时进告警 | 架构页 §5 |
| 八、可观测性 | 「卡在第几步、卡了多久」可回答 | 架构页 §5 |
| 十一、审查清单 | 改 Workflow 前逐条过 | 架构页 §15 + §16.3 范式表 |

---

## 关联

- 现行规范：[[architecture/DeviceControlArchitecture]]
- 废弃依据：[[decisions/ADR-033-RawDesignRefinement20260903]]
- 被部分取代的决策：步骤驱动工作流决策（已删除）
- 相关教训：[[lessons/StepDrivenWorkflowPitfalls]]（已归档）
