---
title: UI 开关兼任可用性门禁会导致操作后不可恢复
date: 2026-11-05
updated: 2026-11-05
tags: [教训, UI门控, Radio, Fill]
status: active
---

# UI 开关兼任可用性门禁会导致操作后不可恢复

> **一句话**：UI 开关兼任可用性门禁会导致操作后不可恢复

## 现象

点过 TA_Break/TA_Pose/TA_Recheck（现名 TA_Retract） 或手动轴操作后，TA_Auto 变灰且选中态被清除；必须回系统设置重新打开「力矩模式」开关才能再用

## 根因

「收力」动作被实现成 `SetTaTorqueMode(false)`，而 Auto 可用性又把这个 bool 当成唯一依据；UI 开关同时承担了「运行期模式」与「功能可用性」两种语义。

代码证据（改前）：
- `LaserWeldHeadWorkflow.ExitTaTorqueMode(string)` → `MontionManager.SetTaTorqueMode(false, actionName)`，被 `TaBreak`/`TaPose1`/`TaPose2`/`TaRetract`（原名 `TaRecheck`）/`TaZeroPose` 与六个手动轴操作调用
- `ProcessControlPage.RefreshActionStates`：`bool taTorqueMode = taReady && manager.TaTorqueModeEnabled; radioQuickTaAuto.Enabled = taTorqueMode;` 且非力矩模式时清 `radioQuickTaAuto.Checked`
- `LaserWeldHeadWorkflow.TaAuto()` 与 `ProcessControlPage.DoTaAuto()` 各有一次同样的 `if (!TaTorqueModeEnabled)` 拒绝

## 判据

同一 bool 既被写入又被当作 Enabled 判定 → 一次必要动作即可永久降级功能；且该 bool 不是设备真实态，UI 勾选无法证明驱动器仍在 CST。

## 预防

- 模式切换收进指令内部（进入时自切 CST、切走时撤力）；可用性只由设备/配置状态位（`TaAvailable`）决定
- 运行期输出态用设备可回读的状态（`GetMoveMode()` + 运行期标志），不用 UI 勾选
- 删除 UI 开关前先列全引用点（Designer / 页面 / 工作流 / 管理器 / 配置键 / wiki），并声明 XML 键的去留（见 ADR-082 D7）

## 后续反转（2026-11-05）：前置一律降级为「执行反馈」

现场出现「配置加载后指令区全部不可用」⇒ 业主最终口径：**连上控制器并装载该轴即可点**，任何前置不满足都走「执行失败 → 红底 + Tooltip 原因」，
⛔ 不再置灰。配套要点：

- 可用性唯一来源 = `MontionManager.IsInitialized` + `GetAxisByKeys/GetDeltaAxisByKeys` 命中（或 `WeldHead != null`）；⛔ 不掺 ZeroPose/力矩模式/其它派生状态。
- 点击先确认（`AntdUI.Modal`），取消回退上一选中项；回填 `Checked` 必须用守卫（`_suppressActionRadio`）防 `CheckedChanged` 递归执行指令。
- 上色用 **`AntdUI.Radio.Fill`**（`Nullable<Color>`，可写、支持半透明）：`ARGB(64,76,175,80)` 成功 / `ARGB(64,244,67,54)` 失败 / `Transparent` 未选中或未执行；
  ⚠️ `AntdUI.Radio` **没有 `Back` 属性**，`Control.BackColor` 带 Alpha 会抛 `ArgumentException`。
- 颜色只在「切换选中」「执行完成」两个事件里改，⛔ 不加计时器每拍重绘；切换时旧项必须 `ResetActionBack` 复位，否则残留旧色。
- 失败原因取 `LaserWeldHeadWorkflow.LastActionMessage`（`DeviceWorkflowBase.Log` 记录末条），写进该 Radio 的 Tooltip —— 只靠颜色不合规。

## 后续反转（2026-11-17）：前置结论只由一条路径置位 ⇒ 手动路径永远解不开

- **现象**：初始化完成后在系统设置页手动回零，`TA_Zero` 能执行，其它 TA 指令一律显示「TA 未回零」不能执行；且每点一个指令就多一个红底。
- **根因**：① 「已回零」结论（`TaHomed`）只在**阻塞等待回零**那条路径（复位回零）置位，手动回零走非阻塞路径 ⇒ 结论永不成立；② 指令被拒后当前项标红，但旧项底色**只清不清** ⇒ 红底逐个累积。
- **判据**：同一前置结论存在多条写入路径而只有一条会置位 ⇒ 命中；指令区底色只在「自己」复位、不复位同组其它项 ⇒ 命中。
- **预防**：
  - 前置结论的置位点必须**唯一**：所有产生该结论的动作走同一实现（手动回零与复位回零共用同一回零入口）。
  - ⛔ 禁让「非阻塞下发」承担需要置位结论的动作（结论无人兑现）。
  - 指令区互斥 ⇒ 任何时刻最多一个控件带结果色：选中新指令即复位同组其它项底色。
  - 门禁判定禁缓存会过期的快照，点击时直读权威源（见 [[standards/UiStateSimplification]] ①真相源唯一）。

## 后续反转（2026-11-17）：指令区「选中态」与「结果色」必须是同一个控件

- **现象**：点 TA_Auto 后确认，结果变成「TA_Zero 被选中、TA_Auto 是红的」；被拒一次就多一个红底。
- **根因**：① 自动流程（初始化自动 `TA_ZeroPose`）会**抢走用户的指令选中态**，并把自己的结果色落在 `TA_Zero` 上；② 被拒路径**回退选中态**到上一项（上一项带着旧的红底）⇒ 选中的与带色的不是同一个控件；③ 旧底色**只清不清** ⇒ 逐个累积。
- **判据**：指令区出现「选中项与带色项不一致」或「同组多个控件带底色」⇒ 命中；被拒路径调用了「回退选中态」⇒ 命中。
- **预防**：
  - 不变量：**任一时刻每组最多一个控件带底色，且带底色者 = 当前选中者**。
  - 自动流程**不抢用户的指令选中态**，也不占用指令区结果色（自动流程的反馈走日志与只读位）。
  - 被拒路径**保持当前选中态**并标红（回退选中态会把颜色与选中拆开）。
  - 取消确认才回退选中态，并复位本次的旧底色。
  - 底色复位按**容器作用域**分组（AntdUI Radio 互斥作用域 = 父容器），跨组不得互清。

## 相关页面

- [[decisions/ADR-082-TaInitFourStepAndAvailability]]
- [[decisions/ADR-063-CommandZoneRadioExclusivity]] §六（2026-11-05 可用性与执行反馈改版）
- [[api/MontionManager]]
- [[api/ProcessControlPage]]
- [[api/SystemControlPage]]
