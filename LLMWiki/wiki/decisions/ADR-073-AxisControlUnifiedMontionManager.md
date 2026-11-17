---
title: ADR-073 轴控制统一入口 MontionManager（六函数收口 UI 直控 + 表格控制列迁固定按钮）
date: 2026-10-19
updated: 2026-10-19
tags: [ADR, MotionControl, MontionManager, 轴控制, UI, 固定按钮, SystemControlPage]
status: accepted
---

# ADR-073：轴控制统一入口 MontionManager

> 业主 2026-10-19 裁定：「控制逻辑是在本页编写，不符合代码设计：**控制归属于 motionmanager**，
> 需要通过它来控制，本页不写。这样的好处是 Y 轴和送丝轴可以使用同样的函数控制自己的轴，
> 节省代码。并且每个页面规划的轴都是固定的，**轴的查找和控制都可以写得很简洁**。」

## 一、决策

**轴控制的唯一入口 = `MontionManager` 六个单轴函数**（与 ADR-066 的「轴定位唯一入口」对偶——
082 管「找到哪个轴」，089 管「怎么控轴」）：

| 函数 | 签名 | 语义 |
|---|---|---|
| `MoveTo` | `bool MoveTo(MontionAxis axis, double target)` | 绝对定位（`posMode=1`），**伺服未使能则先自动使能** |
| `StepMove` | `bool StepMove(MontionAxis axis, double delta)` | 相对步进（`posMode=0`，delta 可负） |
| `ToggleServo` | `bool ToggleServo(MontionAxis axis)` | 使能翻转，返回翻转后状态 |
| `JogStart` | `void JogStart(MontionAxis axis, ushort dir)` | 连续点动（1=负向 0=正向） |
| `StopAxis` | `void StopAxis(MontionAxis axis)` | 减速停止（`StopMode.Deceleration`；点动松开与停止按钮共用） |
| `HomeAxis` | `void HomeAxis(MontionAxis axis)` | 非阻塞回零 |

- **null 轴一律不下发**（`MoveTo/StepMove/ToggleServo` 返回 false，其余静默返回）——校验责任上移到查找层。
- **日志与 UI 提示留在页面**（Manager 只回执行结果；`GlobalCommData.ShowLog` 是 UI 侧唯一日志口）。
- ⛔ **UI 页面不得直接调 `MontionAxis` 控制成员**（`AbsMove/JogMove/AxisStop/ServoOn/ServoOff/HomeNoBlock`）
 ——两页静态校验断言直接调用数 = 0。

## 二、页面范式（固定轴 + 固定按钮）

**查找**：每页规划轴固定 → `MontionManager.Instance.GetAxisByKeys(页角色关键字)`（ADR-066 入口），
一行拿到本页轴；`SystemControlPage` 用 `TraceAxisKeys = {Y, 横梁, 跟踪}`。

**控制（SystemControlPage 轨迹页，2026-10-19 表格→固定按钮）**：
- `tableAxis` **19→11 列**：删 8 个 `CellLink` 控制列（步距后退/前进·负向/正向·移动·回零·停止·使能），
 留 7 显示列 + `LayoutValue`(步距) + `TargetPos`(移动目标) + `ParamBtn`(参数) + `Feedback`。
- `AxisRow` 9→1 个 `CellLink[]` 属性；`Sym*` 常量 9→1（仅 `SymParam`）；
 `TableAxis_CellButtonClick` 只剩参数列分发（`OpenAxisEditor`）。
- 8 个 `AntdUI.Button`（`ServoBtn/HomeBtn/MoveToBtn/NegFwdBtn/StepFwdBtn/StopBtn/StepBackBtn/NegBackBtn`，
 由业主在 VS 置于 `gridTraceAxis` 固定行）经 `BindEvents` **后置订阅**接线（Click×6 +
 Jog `MouseDown/MouseUp/MouseLeave`×6）；`MouseLeave` = 按住拖离安全兜底（替代原表格 `MouseUp` 兜底）。
- 步距/移动目标取自轴表**首行**（`GetFixedRow()`，本页唯一跟踪轴行）。
- 原 `TableAxis_CellButtonDown/Up`、`TableAxis_MouseUp`、本地 `DoRelative/DoAbsolute/ToggleServo`
 直控实现全部删除或改调 Manager（`Do*` 保留为**日志包装**）。

**ProcessControlPage**：`MoveAxisToTarget` 的 `ServoOn+AbsMove` 直控改 `manager.MoveTo`（自动使能），与
系统设置页同一函数。

## 关键约束

| 约束 | 说明 |
|---|---|
| ⛔ UI 直控归零 | 页面 `*.AbsMove/.JogMove/.AxisStop/.ServoOn/.ServoOff/.HomeNoBlock` 调用数必须 = 0（校验判据） |
| ⛔ Manager 不打 UI 日志 | 六函数只返回结果；日志/Message 留页面（职责边界 ADR-016） |
| ⛔ 查找不自建匹配 | 页面只传 `GetAxisByKeys(keys)`（ADR-066），禁止再遍历 `MotionConfig`/`Contains` |
| ⚠️ 固定按钮无行上下文 | 控制列迁出后按钮不携带行；步距/目标值经 `GetFixedRow()` 取首行 |

## 演进

- 演进自 [[decisions/ADR-066-ThreeLayerConvergence]]（轴定位唯一入口 → 补齐控制唯一入口）。
- 同轮配套 UI 收口（轨迹页底部三按钮统一读存）见 [[decisions/ADR-072-FullChainLayoutAndSplitPane]] 六轮演进。

## 背景

（待补：本决策要解决什么问题）

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 后果

### 正面
- （待补）

### 负面
- （待补）

### 2026-11-17 · 决策 D25 · 手动轴操作改非阻塞下发并后台执行；回零退出手动入口统一走 TryHomeAxisWithWait
- **变更**：手动轴操作改非阻塞下发并后台执行；回零退出手动入口统一走 TryHomeAxisWithWait
- **理由**：AbsMove 阻塞等到位在 UI 线程调用会冻结界面；非阻塞回零不置已回零结论
- **影响**：新增 MoveToNoBlock/StepMoveNoBlock；AxisManualOperation.Home 与 Manager.HomeAxis 删除

## 相关页面

- [[api/MontionManager]] · [[api/SystemControlPage]] · [[api/ProcessControlPage]]
- [[decisions/ADR-066-ThreeLayerConvergence]] · [[decisions/ADR-016-WorkflowResponsibilityBoundary]]
