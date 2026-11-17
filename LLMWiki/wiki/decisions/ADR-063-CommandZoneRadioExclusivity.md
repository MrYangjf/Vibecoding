---
title: ADR-063 指令区 Radio 互斥与指令/参数分离
date: 2026-10-12
updated: 2026-11-05
tags: [ADR, UI, Radio, 指令互斥, TA, LA, 工艺设置, 确认弹窗, 执行反馈]
status: accepted
---

# ADR-063：指令区 Radio 互斥与指令/参数分离

> 调试页的「指令区」改用 `AntdUI.Radio` 表达互斥指令，**删除按钮 + 状态标签**的旧范式；
> 工艺设置页的 TA 区拆成「指令」（快捷设置页）与「参数设定」（激光工艺页）两处，不再一区两用。

## 演进

- **2026-11-02 默认态与连机同步**：三个指令区（Y / LA / TA）加载后统一默认选中各自 Auto 项
  （`Y_AutoTracking` / `LA_Auto` / `TA_Auto`），构造期以 `_loadingProcessEnable` 抑制指令下发；
  `RefreshActionStates()` 扩为**唯一可用性同步入口**（补 Y 三 Radio，LA 就绪判据加 `MontionManager.IsInitialized`），
  并由 `MotionControlWorkflow.StateSwitched` 实时驱动（`InvokeRequired` 切 UI 线程），
  运控未连接/轴缺失时整组置灰，**已选中项保持不清空**。
- **2026-11-02 LA 指令区分组互斥**：LA 区实为**两套独立电机**（对焦电机 `LA_Auto~LA_Pose2` / 振镜电机 `LA_Galvo*`），
  原 9 个 Radio 全挂 `gridQuickLa` ⇒ 同父容器天然整区互斥。改为 `gridQuickLa` 内新增
  `gridQuickLaFocus` / `gridQuickLaGalvo` 两个子 `GridPanel` 各装一组 ⇒ **组内互斥、跨组独立**
  （可同时选中「一个对焦模式 + 一个振镜模式」）；删除 `_laMotionRadio` / `_laPatternRadio` / `RestoreLa*` 事后补救，
  互斥由容器天然成立（见 §五）。TA 区为单电机单容器，保持整区唯一。
- **2026-11-02 TA_Auto 受力矩模式门控**：`TA_Auto` 的可用性不再仅随连机状态，还跟随
  `MontionManager.TaTorqueModeEnabled`（非力矩模式置灰 + `DoTaAuto()` 拦截）；与 `LaserWeldHeadWorkflow.TaAuto()` 的底层门
  **读同一状态位**，避免「UI 可点、底层必败」。互斥语义不变（TA 5 项仍整区唯一），见 [[decisions/ADR-057-TaLaActionAndFollowControl]]。

- **2026-11-05 可用性口径改版 + 点击即确认 + 执行上色（替代本条前置与置灰规则）**：现场反馈「配置加载后指令区全部不可用」，
  业主新要求「控制器连上并装载该轴后，指令区就可以设置；点 Radio 需弹窗确认才执行；失败红底、成功绿底、未选中透明」。
  ⇒ ①可用性只看 `MontionManager.IsInitialized` + 该轴已装载/已创建，**不再用 ZeroPose 到位/力矩模式/其它前置置灰**（上一条「TA_Auto 受力矩模式门控」作废）；
  ②`CheckedChanged` 先弹 `AntdUI.Modal` 确认，取消则回退上一选中项（`_suppressActionRadio` 防递归）；
  ③执行成功/失败用 `Radio.Fill` 半透明绿/红上色，切走时旧项复位 `Transparent`；失败原因同时写日志与该 Radio 的 `Tooltip`。
  详见下文「六、可用性与执行反馈（2026-11-05 改版）」。

## 背景

批 J（ADR-060）用「按钮组 + 状态标签」实现 TA/LA 动作位，上机后发现三个问题：

1. **互斥靠代码保证**：4 个按钮谁都能点，实际语义是互斥（TA auto / break / Pose1 / Pose2 只能一个生效），
 旧实现只在后端 `TaAuto/Break/Pose1/Pose2` 各自生效，UI 层**看不出**当前哪个生效。
2. **状态标签冗余**：`lblQuickTaState` / `lblTaState` 反复显示「TA：力矩输出中（auto）」等文本，
 而选中态本身就能表达「哪个生效」，属重复信息。
3. **一区两用**：快捷设置区与激光工艺区**各放一套** TA 指令按钮（`btnQuickTa*` / `btnTa*`），
 同一动作两个入口，参数与指令混在一起。

## 决策

### 一、指令区统一用 `AntdUI.Radio`（同父容器自动互斥）

| 项 | 内容 |
|---|---|
| 控件 | `AntdUI.Radio`（官方成员：`Text` / `Checked` / `CheckedChanged` / `AutoCheck` / `ForeColor` / `Fill`） |
| 事件 | `CheckedChanged += new AntdUI.BoolEventHandler(handler)`，参数 `bool value`（⛔ **不是** `EventHandler`） |
| 互斥 | 同一父容器内的 Radio **自动互斥**（AntdUI 在 `Checked` 置 true 时把 `Parent.Controls` 内其它 Radio 置 false），无需手写 Group 或互斥代码；⚠️ **作用域 = 父容器**：不同电机的指令必须各自入独立容器，否则会被当成一组 |
| 触发时机 | ⛔ **仅在 `value == true`（从未选中变为选中）时触发指令**；取消选中是别的 Radio 被选中，不重复执行 |
| 处理器 | 一组共用一个 `radioQuickTa_CheckedChanged` / `radioQuickLa_CheckedChanged`，按 `radio.Name` 分发 |

### 二、选中态配色（业主裁定；**2026-11-05 改为「执行结果着色」**）

| 状态 | `ForeColor` | `Fill` |
|---|---|---|
| 选中 + **执行成功** | 默认（黑字） | `Color.FromArgb(64, 76, 175, 80)`（半透明绿，`64` 保留底纹可见） |
| 选中 + **执行失败** | 默认（黑字） | `Color.FromArgb(64, 244, 67, 54)`（半透明红） |
| **未选中 / 未执行** | 默认 | `Color.Transparent` |

> ⛔ 不再用「选中即绿底 `#52C41A`」——选中态由圆点表达，底色**只表达执行结果**；切换选中时旧项必须复位 `Transparent`。
> ⚠️ `AntdUI.Radio` **无 `Back` 属性**，`BackColor` 带 Alpha 会抛 `ArgumentException`（WinForms 限制）⇒ 采用可写的 `Fill`（`Nullable<Color>`，声明于 `AntdUI.Radio` 自身）+ `Invalidate()` 重绘。

### 三、指令与参数分离

| 页 | 职责 |
|---|---|
| **快捷设置**（`panelQuickTa` / `panelQuickLa`） | **只有指令**：TA 4 项（auto/break/Pose1/Pose2）+ LA 9 项（对焦 5：auto/Spot1/Spot2/Pose1/Pose2；振镜 4：GalvoCircle/Eight/Line/Arc），全为 Radio |
| **激光工艺设置**（`panelLaserTa`） | **只有参数**：TA_Force（可编辑，N）/ TA_Break 停止位（**只读**，mm）/ TA_Pose1（可编辑，mm）/ TA_Pose2（可编辑，mm） |

⇒ 在工艺页设好参数，快捷页点指令即可生效。**激光工艺区不再保留 TA 指令按钮。**

### 四、运行时只读反馈位（TA_Break 停止位）

`TA_Break` 无设定值，但指令发出后需要知道停止位置（业主：「在整个调试逻辑中是有作用的」）。
`LaserWeldHeadWorkflow.TaBreak()` 内已有 `double holdPosMm = axis.GetPosition();`，此前**只写日志、未外露**。

⇒ 新增只读属性 `TaBreakHoldMm` + `TaBreakHoldValid`（后者用于区分「未触发」与「锁存在 0 位」），
`TaBreak()` 成功时锁存；UI 只读展示，未触发显示 `--`。**不落配置**（运行时反馈值，非设定值）。

### 五、LA 分组互斥 vs TA 整区互斥（2026-11-02 演进）

| 区 | 电机 | 承载容器 | 互斥范围 |
|---|---|---|---|
| LA | 对焦电机（焊接头从站 LA 轴） | `gridQuickLaFocus`（`LA_Auto` / `Spot1` / `Spot2` / `Pose1` / `Pose2`） | **组内唯一** |
| LA | 振镜电机（焊接头从站振镜） | `gridQuickLaGalvo`（`LA_GalvoCircle` / `Eight` / `Line` / `Arc`） | **组内唯一** |
| TA | 送丝力矩电机（单轴） | `gridQuickTa` | **整区唯一**（~~`TA_Auto` 另受力矩模式门控~~ → 2026-11-05 作废，见 §六） |

⇒ LA 可同时存在「一个对焦模式 + 一个振镜模式」（两套电机独立执行，不冲突）；
TA 的 5 条指令都作用于同一根轴，必须整区唯一，**不得照搬 LA 的分容器做法**。

- **容器布局**：外层 `gridQuickLa.Span = "40:fill;60:fill;30:fill;30:fill"`（标题 / 对焦组 / 振镜组 / 提示），
  子 GridPanel 逆序入格；对焦组 `Span = "30:160 160 160 160;30:160"`，振镜组 `Span = "30:160 160 160 160"`。
- **删除的事后补救**：`_laMotionRadio` / `_laPatternRadio` / `RestoreLaMotionRadio` / `RestoreLaPatternRadio`
  已退场（容器分组后无需跨组回填）；`_syncingLaRadios` 保留，职责收窄为 **Radio↔`selGalvoPattern` 双向同步抑制**。
- **保留**：组内互斥、默认选中（对焦 `LA_Auto` / 振镜取工艺配置 `GalvoPattern`）、连机未就绪只改 `Enabled` 不改 `Checked`。

### 六、可用性与执行反馈（2026-11-05 改版）

#### 1. 可用性口径（唯一来源：`MontionManager` 轴注册表 + 连接态）

`ProcessControlPage.RefreshActionStates()` 判定：

| 区 | 判据（代码位置） | 说明 |
|---|---|---|
| Y | `manager.IsInitialized && manager.GetAxisByKeys(MontionManager.SeamTrackYKeys) != null` | `IsInitialized` = 主站初始化 + 轴/IO/气缸/焊接头装载成功（MotionControl 目录无独立 `IsOpen/IsConnected`） |
| LA | `manager.IsInitialized && manager.WeldHead != null` | 焊接头从站已创建即视为「轴已装载」 |
| TA | `manager.IsInitialized && manager.GetDeltaAxisByKeys(MontionManager.TaAxisKeys) != null` | `TA_ZeroPose` 同口径 |

⛔ **不再纳入** ZeroPose 到位、力矩模式、`TaMotionReady` 或其它前置条件——现场「配置加载后全部置灰」即由这些前置造成。
未就绪时 Radio 的 `Enabled=false`（连机前不可点）；连上并装载后即可点。

#### 2. 确认 → 执行 → 上色 → 复位 状态机

| 步骤 | 实现 | 关键点 |
|---|---|---|
| ① 点击 | `CheckedChanged` 且 `e.Value==true` | 三区统一走 `RunInstruction(radio, axisName, detail, exec, ref lastRadio)` |
| ② 确认 | `AntdUI.Modal.open(new Modal.Config(FindForm(), "指令确认", msg, TType.Info)) == DialogResult.OK` | msg 含：指令名、所属轴、关键参数（TA 力值/N + 方向 + 100% 基准、Pose1/2 mm、ZeroPose mm；Y 目标位；LA Spot/Pose 目标） |
| ③ 取消回退 | `_suppressActionRadio=true` → `lastRadio.Checked=true`（`ApplyDefaultCommandModes` 已把 `_last*Radio` 记为各自 Auto 项，故必有回退目标）→ 守卫复位 | **防递归**：三个 handler 顶部首句 `if (_suppressActionRadio) return;`；回填只改 `Checked` 不触发执行 |
| ④ 执行 | `exec()` 返回 `bool`；异常捕获后按失败处理 | `DoTa*` / `DoLa*` / `MoveAxisHome` / `MoveAxisToTarget` 由 `void` 改 `bool`，失败路径补 Error 日志 |
| ⑤ 上色 | `ApplyActionBack(radio, ok, reason)`：`radio.Fill = ok ? ActionBackOk : ActionBackFail` + `Invalidate()` | 成功绿 / 失败红 |
| ⑥ 复位 | 执行前 `ResetActionBack(lastRadio)`（`Fill=Transparent` + `Invalidate()`）；执行后 `last = radio`（成功失败都记） | 切换瞬间旧项底色清空，不残留；下一次取消回退目标 = 最近一次已执行项（哪怕它是红色） |
| ⑦ 原因可见 | `_tooltip.SetTip(radio, "指令：执行成功/失败 — 原因")`；原因取 `LaserWeldHeadWorkflow.LastActionMessage`（`DeviceWorkflowBase.Log` 记录最后一条） | **不能只靠颜色**；拒绝原因（如 `CheckTaAvailable` 的可读文案）直接进 Tooltip |

⛔ **不引入定时器刷新颜色**：颜色只在「切换选中」与「执行完成」两个事件里改，避免每拍重绘。

#### 3. TA 特殊处理

- `TA_Auto` 允许点击；`TaAvailable` / `TaMotionReady` 不满足时**走执行失败 → 标红 + Tooltip 原因**，不再置灰。
- `TA_ZeroPose` 仍可重试（失败不锁死，不改变 `TaAvailable`）。

#### 4. 上色可见性核查（实测）

- **控件类型**：Designer 中三个指令区全部为 `AntdUI.Radio`（`new AntdUI.Radio()`，非原生 `System.Windows.Forms.RadioButton`）。
- **`Back` 属性**：Reflection 实测 `AntdUI.Radio` **无 `Back`**；`Fill` = `System.Nullable<System.Drawing.Color>`、`CanWrite=True`、`DeclaringType=AntdUI.Radio`。
- **为何可见**：AntdUI 自绘控件按 `Fill` 绘制底色（旧版「选中即 `Fill=#52C41A` 绿底」长期可见即为证），`Invalidate()` 触发重绘；半透明色与底纹叠加，不遮挡文字与圆点。
- **为何不用 `BackColor`**：`Control.BackColor` 收到 Alpha≠255 会抛 `ArgumentException`（WinForms 限制），无法满足「半透明」要求。

## 后果

- **正面**：互斥由控件语义保证（不依赖代码）；选中态即状态显示（删 2 个状态标签）；指令/参数职责清晰；Break 停止位可观测
- **负面**：`CheckedChanged` 会在**初始化回填**时也触发一次（`Checked` 赋值即触发）⇒ 处理器必须以 `if (!e.Value) return;` 防抖，且**加载配置回填时须避免误触发指令**（当前 TA 区无 Radio，不受影响；若后续参数区也引入 Radio 需注意）
- **中性**：Radio 在项目内首次用于「指令组」（`FilebackupPage` 是首个 Radio 先例，可参照）

## 验证

- ** 实测法**（判据库 §7.3）：TA 4 Radio `x=20/232/415/536` 宽 181/177/115/115，右边缘 651 ≤ 666；LA 5 Radio 宽 118、右边缘 658 ≤ 666，全部同行不重叠
 ⚠️ **LA 侧 Radio 宽度上限**：5 个 Radio 宽 130 时右边缘 702 > 666（超出面板 36px，末个被裁掉）⇒ 宽度收敛为 118
- **互斥实测**：`Checked[0]=true` 后 `[0]=True [1..3]=False`；再 `Checked[2]=true` 后 `[0]=False [2]=True` ⇒ 互斥确认生效
- **LA 分组实测（2026-11-02 探针）**：两个独立 Panel 各放 2 个 `AntdUI.Radio` —— 跨容器两者同时 `Checked=true`；
  组内切换互斥；`OnClick` 触发振镜 Radio 后对焦组选中保持 ⇒ 容器作用域确认（同类 Radio 同容器才互斥）

- **回归**：本轮改动 5 个既有文件 + 新增 `TAConfig.cs` + `WeldParamManager.cs` 接线，无越界

## 备选方案

- （待补：考虑过什么、为什么放弃）

### 2026-11-17 · 决策 D28 · TA 指令区互斥单色：任何时刻最多一个 Radio 有底色；门禁改点击时直读权威源
- **变更**：TA 指令区互斥单色：任何时刻最多一个 Radio 有底色；门禁改点击时直读权威源
- **理由**：旧色只清不清导致点一下多一个红；门禁快照过期致状态显示异常
- **影响**：TA 区选中新指令即复位同组旧底色；门禁快照整体退场改直读

### 2026-11-17 · 决策 D31 · 指令区不变量：任一时刻每组最多一个 Radio 带底色，且带底色者=当前选中者
- **变更**：指令区不变量：任一时刻每组最多一个 Radio 带底色，且带底色者=当前选中者
- **理由**：旧色只清不清导致点一下多一个红；被拒回退选中态导致选中与带色者不一致
- **影响**：RunInstruction 改为确认→门禁→单飞→执行→上色；被拒保持选中并标红；取消确认复位自己底色；自动 ZeroPose 不抢选中态不占底色

## 相关页面

- [[decisions/ADR-064-TaConfigLayeredConsolidation]] —— TA 参数分层收口（ForceN/Pose 入 TAConfig）
- [[decisions/ADR-060-P4UiLanding]] §四 —— 按钮范式（本 ADR 将「指令按钮组」演进为 Radio）
- [[api/ProcessControlPage]] · [[api/LaserWeldHeadWorkflow]]
- [[guides/AntdUI-Reference]] —— Radio 范式与速查表
- [[lessons/StaticVerifierJudgements]] §0.4b（不凭空造成员名）· §0.9e（四件套）

## 演进记录

### 2026-11-05 上色改 BackColor、同轴单飞与 5s 状态检测

- **上色**：业主明确「不要用 `Fill`，`Fill` 是按钮颜色，直接改 `BackColor`」。实测（屏幕像素采样）：
  只设 `BackColor`（关闭 `AllPaintingInWmPaint`）采样 255,255,255 不可见；`BackColor` + `Fill=Transparent` + 关闭 `AllPaintingInWmPaint` 采样 76,175,80（与设定值一致）；只设 `Fill=绿` 采样 56,129,59（按钮色非目标色）；`BackColor` + `Fill=Transparent` 但不关 `AllPaintingInWmPaint` 采样 255,255,255 不可见。
  结论：构造期对每条指令 Radio 反射调 `SetStyle(ControlStyles.AllPaintingInWmPaint, false)` 并把 `Fill` 置 `Transparent`；结果色只用不透明 `BackColor`（成功 76,175,80 / 失败 244,67,54 / 执行中 189,189,189 / 未选中 White）。
- **单飞**：`MontionManager.TryBeginAxisInstruction(axisName, instruction, out token, out reason)` 按轴名登记；同一轴同一时刻只允许一条指令，重复点击在弹确认框之前即被拒（提示「正在执行 X（已 Y.Ys），暂不接受新指令」）；不同轴可并行，上色按各自 Radio 隔离。
- **状态检测**：指令下发后在同一后台线程内阻塞等待实测状态，不以 API 返回值判成功。统一超时常量 `MontionManager.InstructionDetectTimeoutSeconds = 5.0`（业主口径固定 5s，便于以后调整），采样 20ms、位置类连续 3 次稳定、扭矩类 40ms 确认窗；`TA_ZeroPose` 是唯一例外，沿用行程/速度估算（下限 10s、上限 60s）。
- **UI 线程**：指令执行与检测在后台线程，上色经 `BeginInvoke`；执行中先置中性灰，完成后才按结果上红/绿，失败原因写 Tooltip 与日志。
- **取消与清零**：`CancelAllAxisInstructions(reason)` 在初始化失败、急停、页面销毁时调用；所有指令的 `EndAxisInstruction` 必在 `finally` 执行。

### 2026-11-05 按轴门禁与指令流程归属（与 ADR-082 同轮）

- **门禁按轴**：`ProcessControlPage.RunInstruction` 改为按轴 `ResolveAxisGateReason` 预检（TA/Y 取 [[api/MotionControlWorkflow]]，LA 取 [[api/LaserWeldHeadWorkflow]]），
  ⛔ 不再用 `MontionManager` 混用总状态；`MoveAxisHome` / `MoveAxisToTarget` 也先过 `MontionManager.GetAxisGateReason(axis)`。
- **流程归属**：TA 六指令实现迁入 `MotionControlWorkflow`；`LaserWeldHeadWorkflow` 仅留同名薄转发（兼容壳，后续可清理）；LA/振镜/对焦与焊接头从站设备态不动。
- **失败原因按流程取**：`InstructionWorker` 按指令前缀取对应 workflow 的 `LastActionMessage`（Y/TA → 运控流程，LA → 激光头流程）。
- **单飞不变**：仍以轴名为键登记在 `MontionManager`；同轴跨流程互斥由「同一轴名唯一登记」保证。
