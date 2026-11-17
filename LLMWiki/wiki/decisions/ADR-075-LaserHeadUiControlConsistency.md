---
title: "ADR-075 激光头系统设置控件一致性（Switch 开关 / TA 复刻 Y 轴 / 振镜状态序 / 按钮样式统一）（整合旧 077（激光头页自动刷新与使能改按钮））"
merged_from: [ADR-077]
date: 2026-10-22
updated: 2026-11-17
tags: [ADR, UI, SystemControlPage, 激光头, 振镜, TA, LA, Switch, 按钮样式, ADR-073]
status: accepted
---

# ADR-075：激光头系统设置控件一致性

## 背景

业主 2026-10-22 对系统设置页「激光头系统参数设置」提出四项一致性要求：

1. 所有切换类按钮改为 **`AntdUI.Switch`**（按钮式开关不再作为切换载体）；
2. 送丝力矩电机（TA）的控件与控制**完全仿照 Y 轴电机控制**，UI 几乎一样；
3. 振镜卡片内的**状态信号在上、设置居中、按钮最后**；
4. 页面内按钮样式**完全与模拟测试页「保存模拟参数」一致**。

## 决策

### 一、切换类控件统一 `AntdUI.Switch`

| 原控件 | 现控件 | 语义 |
|---|---|---|
| `button4`（文本「自动刷新：开/关」） | `swTempRefresh` | 温度自动刷新开关（`CheckedText`/`UnCheckedText` 承载文案） |
| ~~`btnOptMotorEnable`（按钮「切换使能」）~~ | ~~`swLaMotorEnable`~~ | ~~LA 对焦电机使能开关~~ |
| ~~（无）~~ | ~~`swGalvoEnable`~~ | ~~振镜使能开关（2026-10-23 补，`gridOptics` 末行与回零按钮并列；`GalvoEnable`→0x7010 子索引 15）~~ |

> ⚠️ **2026-10-26 经 [[decisions/ADR-075-LaserHeadUiControlConsistency]] 演进**：上表后两行作废 —— **使能类控件由 Switch 改回按钮**（`swLaMotorEnable` → `btnOptMotorEnable`、`swGalvoEnable` → `btnOptGalvoEnable`，样式同 `TaServoBtn` 纯图标 + Tooltip，状态改由 `lblOptMotorState` / `lblOptGalvoEnableValue` 标签承载）。**自动刷新类控件仍为 Switch**（上表首行继续有效），仅「默认 ON + 分区门控」由 ADR-075 接管。

- ~~开关事件统一 `CheckedChanged(object, AntdUI.BoolEventArgs)`，在 `.Designer.cs` 订阅一次。~~
- ~~程序回写 `Checked` 必须经 `_syncingSwitch` 抑制，避免 500ms 状态刷新触发设备动作；`_loadingLaserHead` 期间同样忽略。~~
- ~~开关动作失败/权限拒绝时回退到原状态。~~

> ⚠️ **2026-10-26 经 [[decisions/ADR-075-LaserHeadUiControlConsistency]] 演进**：上三条随「使能类控件改按钮」一并作废 ——
> ① 使能改按钮后**无勾选态可回写**，`_syncingSwitch` / `SyncLaMotorSwitch` / `SyncGalvoSwitch` / `_motorEnabled` 已整组删除；按钮是**动作型**（点击读当前状态再翻转），失败只提示不回写。
> ② 订阅位置改**代码后置 `BindEvents()`**（四个刷新开关 + 三个新按钮），⛔ Designer 不再订阅这四个 Switch —— 同一事件只准一处 `+=`。
> ③ 开关动作失败回退仅对**仍为 Switch 的自动刷新开关**无意义（它们从不被程序回写），现由 ADR-075 的「标志初值取自设计器」取代。

- **振镜使能特殊门控（2026-10-23）**：焊接中 `LaserWeldHeadWorkflow.ApplyGalvoAmplitude()` 按摆幅自动写 `GalvoEnable = amplitude > 0`，手动开关在焊接中置灰并拒绝切换（与 `GalvoDemo` 的 `IsWelding` 互斥同范式）；非焊接时读当前 `GalvoParams` 后只翻转 `GalvoEnable` 再写回，保留其余振镜参数。

### 二、TA 送丝力矩电机复刻 Y 轴控制

- **UI**：`gridWireCurve` 末行为 8 个 `AntdUI.Button`（`TaNegBackBtn`/`TaStepBackBtn`/`TaStopBtn`/`TaStepFwdBtn`/`TaNegFwdBtn`/`TaMoveToBtn`/`TaHomeBtn`/`TaServoBtn`），顺序、图标、`Ghost`/`BackHover` 与 `gridTraceAxis` 的 Y 轴 8 键一致；均为图标按钮并配 `TooltipComponent` 语义提示。
- **状态**：当前位置 / 伺服 / 正限 / 负限 / 原点 / 报警 六项与轴表 `FillAxisRuntime` 同判据（`GetStatusWord` 0x0004/0x0008、软限位、`|pos|≤ε`），运动反馈取 `LastCommand`。
- **控制**：全部经 `MontionManager` 六函数（`ToggleServo` / `HomeAxis` / `StopAxis` / `MoveTo` / `StepMove` / `JogStart`），UI 零直控（沿 [[decisions/ADR-073-AxisControlUnifiedMontionManager]]）。
- **事件**：与 Y 轴固定按钮一致，在 `BindEvents()` 后置订阅 12 处（Click×6 + `MouseDown/MouseUp/MouseLeave`×6），Designer 不重复订阅。

### 三、振镜卡片顺序：状态 → 设置 → 按钮

`gridOptics` 由「标题 + 12 设置 + 斜椭校正 + 按钮」改为 11 行：

1. 标题；
2. **状态信号行**：振镜使能（`GalvoOn`）/ 驱动板报警（`DriverAlarm`），源为焊接头 `0x6010` 回读；
3. **回零状态行**：`lblOptGalvoHomeState`；
4. 设置行（图形/频率/宽/长/角/起止角/中心/压缩/目标尺寸/斜椭校正）；
5. **最后一行**：`btnOptGalvoHome` 单列跨满宽。

状态每拍随 `RefreshMotorStatus()` 刷新，不新增计时器；读失败显示「读取失败」。

### 四、按钮样式统一为「保存模拟参数」范式

页面内动作按钮（LA 前进/后退/导入曲线、振镜回零、读取/修改/保存参数、TA 8 键）统一：

| 属性 | 值 |
|---|---|
| `Ghost` | `true` |
| `Cursor` | `Cursors.Hand` |
| `Font` | 宋体 12F |
| `BackHover` | `(3, 169, 244)` |
| `IconSvg` | 对应语义图标 |

⛔ 不再使用 `Type = TTypeMini.Primary` 的实心按钮形态。

## 备选方案

- **保留按钮式开关**：业主已明确要求 Switch，且 Switch 状态回显更直观 → 放弃。
- **TA 直接复用 `tableAxis` 表格**：单轴无表格价值，且 Y 轴表格是页面唯一跟踪轴载体 → 保留 Y 轴表格，TA 以同构固定按钮 + 状态标签复刻。
- **振镜状态与按钮同处末行**：业主明确「状态在上、设置居中、按钮最后」→ 放弃。

**2026-10-23 补充（指令区与振镜工艺重排，业主裁定）**：① Tracking 指令改 3 Radio：`Y_AutoTracking`（默认，清 `LockYCalib`）/ `Y_ForceCalibPose`（移到 `TeachLockYMm` 并置位）/ `Y_ForceHome`（`MontionManager.HomeAxis`）；② 三个指令区 Radio 统一 `XXX_XXX` 短文本，中文释义放 Tooltip；③ LA 图形 `LA_GalvoCircle/Eight/Line/Arc` 与 `LA_Auto/Spot/Pose` **独立单选**（跨组互不取消），并与工艺设置 `selGalvoPattern` 双向同步；④ 激光工艺页振镜开关删除（硬件使能归系统设置 `swGalvoEnable`，工艺摆动保留快捷区 `swEnableGalvoWeaveQuick`），宽度/长度/频率自系统设置页迁入振镜工艺区；⑤ 「焊缝地图点数上限」自工艺设置页迁入系统设置页「线激光点过滤」。

## 后果

- ✅ 激光头页与跟踪页控制形态一致，TA 操作心智与 Y 轴相同。
- ✅ 开关类控件统一为 Switch，程序回写与用户操作可区分。
- ✅ 振镜状态可即时观察，按钮位置固定；振镜可在非焊接时手动使能/关闭（调试用）。
- ⚠️ 焊接中振镜使能仍以摆幅自动控制为准，手动开关不参与生产闭环。
- ⚠️ 按钮样式为 Designer 显式属性，后续新增按钮须沿用同一范式。
- ⚠️ 真编译待 Visual Studio（本环境无 C# 编译器）。

## 演进

- **2026-10-26 · [[decisions/ADR-075-LaserHeadUiControlConsistency]]**：本页**第一条（切换类控件统一 Switch）被部分演进** —— 仅「使能类」控件（LA 对焦电机 / 振镜）由 Switch 改回 TA 式纯图标按钮；「自动刷新类」仍为 Switch。同时作废「开关在 Designer 单点订阅」「程序回写经 `_syncingSwitch` 抑制」「失败回退开关状态」三条配套约定。第二 / 三 / 四条（TA 复刻 Y 轴 / 振镜卡片顺序 / 按钮样式范式）**继续有效**。

### 2026-11-17 · 决策 D32 · 手动操作按钮禁用按电机分组：一个电机的操作只影响自己那组按钮
- **变更**：手动操作按钮禁用按电机分组：一个电机的操作只影响自己那组按钮
- **理由**：全局单一忙标志会让 TA 回零把 Y/LA/GA 按钮一起变灰
- **影响**：SystemControlPage 改 ManualOpGroup 四组独立标志（Trace/Ta/La/Galvo）；防呆与禁用均按组隔离

## 合并自 ADR-077 · 激光头页自动刷新分区分控与前置门控 · 使能类控件由 Switch 改按钮

> 2026-11-17 治理轮合并：原页为独立 ADR-075，其现行裁定收归本页；原页文件已删除（**编号不回收**，废止号不复用）。原页的验证过程叙事已按格式契约 R2 剥离至 `logs/log.md`。

### 原页决策条目

### 一、LA 控制键一行四键 + 移动目标输入框

`gridLa.Span` 8 行 → **9 行**（`40:fill;35:fill;30:160×4;30:160×4;30:160×4;44:fill×4;40:fill;30:160×4;30:160 fill fill fill`）：

| 行 | 内容 |
|---|---|
| r2 | 当前位置 / 电机状态 |
| r3 | 步距(mm) / 输入 · **移动目标(mm) / 输入（新增）** |
| r4 | LA 量纲(脉冲/mm) / 输入 · 占位 / 占位 |
| **r5** | **后退 · 前进 · 移动到目标 · 使能（四键一行，高 44，与 TA 按钮行同高）** |

- 左→右沿用 TA 的方位语义（后退在前进左侧，与 `TaNegBackBtn`/`TaStepFwdBtn` 相对次序一致）。
- 新增控件：`lblOptMotorTarget` · `txtOptMotorTarget`（默认 `0`）· `btnOptMotorMoveTo` · `btnOptMotorEnable` · `lblMotorSpacer`。
- 控制仍走 `WeldHeadSlaveDevice`（LA 是 WSX 从站 `0x7000`/`0x6020`，**不是 MontionAxis**）——`SetMotorPosEnable(目标mm, 使能)` 是唯一 PDO 写口，故「使能/撤销」与「移动到目标」都写这两位。

### 二、自动刷新：分区分控 + 双层前置门控（复用 `timerRefresh`，⛔ 不新增计时器）

刷新链路唯一入口仍为 `TimerRefresh_Tick`：

```
CanRefreshNow() = 未 Dispose && this.Visible && IsMotionReady()
 └ 未切到系统设置页即全停 └ 未连接即全停
TimerRefresh_Tick:
 激光头页(idx 0=LaserHeadTabIndex) → 按四区开关分别刷 振镜 / LA / TA / 温度
 轨迹页 → 按 btnAutoRefresh(_autoRefresh) 刷轴表
```

| 开关 | 标志 | 默认 |
|---|---|---|
| `swTARefresh` | `_taAutoRefresh` | **ON**（Designer `Checked = true`） |
| `swLARefresh` | `_laAutoRefresh` | **ON** |
| `swGalvoRefresh` | `_galvoAutoRefresh` | **ON** |
| `swTempRefresh` | `_tempAutoRefresh` | **ON** |

- 标志初值在 `BindEvents()` 内从各 Switch 的 `Checked` 同步 —— **设计器是默认值的唯一真相源**，避免「界面显示开、代码认为关」。
- 开启开关时立即刷一次本区（不等下一拍）。
- 门控新增 `LaserHeadTabIndex = 1` 常量，`ApplyPermissionGate` / `tabsSystem_SelectedIndexChanged` 的裸 `1` 一并改用它。
- **⛔ 不新增独立计时器**（沿 [[api/SystemControlPage]] 既有约定「`timerRefresh` 为唯一 UI 计时器」）：分区分控靠标志，不靠计时器数量。
- ⚠️ **初版把两个前置条件合并成一个提前返回（缺陷）** ⇒ 已在 **§五「2026-10-26 修订」** 分治：`IsMotionReady()` 不满足要**回退开关**，`Visible` 不满足**只跳过刷新**。

### 三、使能类控件：Switch → TA 式纯图标按钮（演进 ADR-075 第一条）

| 原控件 | 现控件 | 语义 |
|---|---|---|
| `swLaMotorEnable`（Switch） | `btnOptMotorEnable`（Button） | LA 对焦电机使能/撤销切换 |
| `swGalvoEnable`（Switch） | `btnOptGalvoEnable`（Button） | 振镜使能/撤销切换 |

- 样式与 `TaServoBtn` 完全一致：`Ghost=true` + `IconSvg="CheckSquareOutlined"` + `Cursor=Hand` + 宋体 12F + `BackHover(3,169,244)` + `Dock=Fill`，**纯图标 + Tooltip**，不带文字。
- **状态不再由控件自身承载**：LA 由 `lblOptMotorState`（0x6020 回读）、振镜由 `lblOptGalvoEnableValue`（0x6010 `GalvoOn`）呈现 —— 这两处状态标签 ADR-075 已建，本轮无需新增。
- 按钮为**动作型**：点击时读当前状态再翻转（`!state.IsReady` / `!galvo.GalvoEnable`），失败只提示不回写。
 - 由此**删除** `SyncLaMotorSwitch` / `SyncGalvoSwitch` / `_syncingSwitch` / `_motorEnabled` —— Switch 的「程序回写抑制」机制随 Switch 一并退场（四个刷新开关也从不被程序回写，抑制标志失去全部用途）。
- 振镜「焊接中置灰」门控保留，载体由 Switch 改 Button 的 `Enabled`。

### 四、事件订阅收口

- 四个刷新开关 + 三个新按钮的 `+=` **统一落在 `BindEvents()`**（后置订阅）；Designer 中 `swTempRefresh.CheckedChanged` 的订阅一并移除 —— **同一事件只允许一处订阅**。
- `btnOptMotorBack` / `btnOptMotorFwd` 保持 Designer 订阅不变（`.cs` 不重复绑定）。

### 五、2026-10-26 修订（业主实机复查发现）：门控失效模式必须分治

**缺陷**：初版把两个前置条件**合并进同一个 `CanRefreshNow()`**（`未 Dispose && this.Visible && IsMotionReady()`），Tick 里 `if (!CanRefreshNow()) return;` 一挡了之。后果——**运控未连接时开关仍显示「自动刷新：开」**，与业主原话「没有连接上**自动退回**不刷新」不符（业主实机断开控制器后复查发现）。

**根因**：两个前置条件的**处置方式不同**，合并即丢失语义：

| 前置条件 | 不满足时应有处置 | 初版错误处置 |
|---|---|---|
| ① 运控已连接（`IsMotionReady()`） | **把四个开关自动回退 `Checked = false`**（开关显示必须与「是否具备刷新能力」一致） | 只跳过刷新，开关状态被留下 ⇒ 显示与实际不符 |
| ② 已切到本页（`this.Visible`） | **只跳过刷新，开关状态原样保留**（回到本页即继续按原设置刷新） | 与①同处置（虽无视觉差异，但语义被抹平） |

**修订后结构**（`TimerRefresh_Tick` 三段）：

```
① if (!IsMotionReady()) { SuspendRefreshSwitchesByDisconnect(); return; } // 回退四个开关 + 清标志 + 一次告警日志
② if (_refreshSuspendedByDisconnect) { ResumeRefreshSwitchesAfterConnect(); } // 重连 → 四开关恢复默认 ON
③ if (!IsRefreshPageVisible()) return; // 只跳过；开关状态保留
 随后按内页分发四区 / 轴表刷新
```

**配套裁定**：

1. **`CanRefreshNow()` 更名 `IsRefreshPageVisible()`** —— 名字只描述「本页是否可见」这一件事；⛔ 不得再把连接判据并回去（源码注释已写死该禁令）。
2. **开关本身也受前置条件约束**：未连接时用户手动拨到 ON 会被 `AcceptRefreshSwitchOn()` 拒绝并立即回退（否则开关会在 ON/OFF 间反复跳）。
3. **重连后自动恢复到默认 ON**（业主 2026-10-26 二次裁定）。已知代价：若操作者曾在**已连接时**主动关掉某个开关，断连再重连后该开关会被一并恢复为 ON —— 如需「保留操作者选择」需再加 4 位记忆（当前不做，业主可后续追加）。
4. **⛔ 程序回写 `Checked` 必须经 `_syncingRefreshSwitch` 抑制** —— 这正是上一轮删除、本轮重建的抑制标志：上一轮删除的前提是「不存在程序回写」，该前提**已被本条修订推翻**。回写点共 2 处（`AcceptRefreshSwitchOn` / `SetRefreshSwitches`），每处 `true` 均有同方法内的 `false` 闭合。
5. ~~**作用范围**：仅四个「自动刷新」**Switch**（TA/LA/振镜/温度）。轨迹页 `btnAutoRefresh`（`_autoRefresh`，ADR-073 时代既有）**未纳入** —— 其默认态为 OFF，若纳入「重连恢复默认 ON」会改变既有默认行为；如需一并处置须另行裁定。~~
 ⚠️ **2026-10-26 同日经 §六 推翻**：业主裁定把轨迹页一并纳入 —— `btnAutoRefresh` 改 Switch 且默认 ON，并删除冗余的「刷新轴状态」按钮。

### 六、2026-10-26 适用面扩展（业主令）：轨迹页轴表纳入同一套方式与约束

> 业主指令：「Y 轴那里的刷新开关两个按钮，你修改为与 TA/LA/振镜一致的方式和约束。」

**背景**：轨迹页（`tabPageTrajectoryParam`）工具条 `flpTraceToolbar` 承载两个按钮 —— `btnAutoRefresh`（Text/Type 切换的「自动刷新：开/关」）与 `btnAxisRefresh`（「刷新轴状态」）。二者都是 ADR-073 时代既有控件，**既非 Switch 形态，也不受前置条件约束**（未连接不回退、未切页照刷）。

**决策**：

1. **`btnAutoRefresh` → `swAutoRefresh`（`AntdUI.Switch`）**，与四区同范式：`CheckedText="自动刷新：开"` / `UnCheckedText="自动刷新：关"`、总宽 150、Designer `Checked = true`（**默认 ON**，业主裁定「与四区一致」）。
 - 事件由 `Click` 改 `CheckedChanged`；**⛔ 不再调用 `timerRefresh.Start()/Stop()`** —— 计时器常驻，启停由标志控制（原实现用按钮启停计时器，与四区「共用常驻计时器」的机制相冲突）。
 - 纳入 §五 全套约束：未连接自动回退 false、重连恢复默认 ON、未切页只跳过、未连接手动开启被拒绝、程序回写经 `_syncingRefreshSwitch` 抑制；`_autoRefresh` 初值改为在 `BindEvents()` 内从 Designer `Checked` 同步。
2. **`btnAxisRefresh`（「刷新轴状态」）整体删除** —— 业主裁定「有了自动刷新启停，这个按钮实际没有太多作用」。
 - **删除前接线核验（原 rules/KR-011（已并入 lessons/StaticVerifier-Wiring-Integrity））**：`LoadAxisRows()` 共 3 处消费者 —— 构造函数 `LoadAll()`、`OpenAxisEditor`（参数弹窗保存后重载）、`BtnAxisRefresh_Click`。删除后仍余 2 处 ⇒ **配置编辑后的重建行路径不受影响**，`LoadAxisRows` 非死代码。删除四处同清（`new` / `Controls.Add` / 属性块含段头 / 字段声明）。
3. **分发改为精确匹配**：`TimerRefresh_Tick` 的轴表分支原为 `else if (_autoRefresh)`，会把「模拟测试页（idx 2）」也算作命中；按业主「没有切换到对应页面时**不需要**去刷新 UI」原则改为 `else if (tabsSystem.SelectedIndex == TraceTabIndex && _autoRefresh)`（新增常量 `TraceTabIndex = 0`），⛔ 不留 `else` 兜底。

**结果——五个刷新开关同构（四区 + 轴表）**：`swTARefresh` / `swLARefresh` / `swGalvoRefresh` / `swTempRefresh` / `swAutoRefresh`，共用 `SetRefreshSwitches` 批量回写、`SuspendRefreshSwitchesByDisconnect` / `ResumeRefreshSwitchesAfterConnect` 统一处置、`AcceptRefreshSwitchOn` 统一前置校验。

### 原页背景

1. **LA 区控制形态不统一**：TA 区（`gridWireCurve`）末行是 8 个图标按钮一行；LA 区（`gridLa`）只有「后退/前进」两键夹一个使能 Switch，**无「移动到目标」**，也无目标值输入框 —— 与 TA 的心智不一致。
2. **三个自动刷新开关零接线**：业主已在 TA/LA/振镜三区顶部放置 `swTARefresh` / `swLARefresh` / `swGalvoRefresh`，但 Designer 无订阅、`.cs` 零引用（**0 消费者**）。同时原实现是「每 500ms 无条件读设备刷 UI」，即便本页未打开、运控未连接也照读，既浪费 EtherCAT 读取也易在未连接时刷出无效值。
3. **使能控件形态反复**：[[decisions/ADR-075-LaserHeadUiControlConsistency]] 第一条曾把切换类控件统一为 `AntdUI.Switch`；业主现裁定**使能类**应有明确「动作按钮」语义，改用 TA `TaServoBtn` 同款按钮。

### 原页后果

### 正面
- LA 与 TA 控制心智一致；LA 首次具备「绝对移动到目标」能力。
- 未切到系统设置页、或运控未连接时，本页**零设备读取**，EtherCAT 读取量按实际使用收敛。
- 使能动作语义明确（按钮=动作，标签=状态），不再依赖 Switch 的勾选态自证。
- 移除了 4 个已失去用途的成员（2 个回写函数 + 1 个抑制标志 + 1 个缓存字段）。

### 负面 / 风险
- `this.Visible` 依赖 AntdUI `TabPage` 对子树的隐藏行为；若未来把本页改为非 Tab 承载，门控需重新评估。
- 页不可见时 `TimerRefresh_Tick` 直接返回，**切回本页后的首个数据最多延迟 500ms**（下一拍）。
- 断连时**五个**开关（四区 + 轨迹页轴表，§六）被自动回退为 OFF；**重连后一律恢复为默认 ON** —— 操作者若曾在已连接时主动关闭某区，其选择会被覆盖（见 §五-3，当前不做记忆）。
- ~~四区刷新标志与 Designer `Checked` 的同步只发生在 `BindEvents()` 一次；若将来在运行期程序改写 Switch `Checked`，需重新引入抑制机制。~~ ⚠️ **2026-10-26 同日已被 §五修订推翻**：断连回退 / 重连恢复即运行期程序改写，抑制机制 `_syncingRefreshSwitch` 已按需重建（标志初值仍取 Designer `Checked`）。

### 既有缺陷（本轮只报不改）
- `gridLa` 之外的 `gridTemp` Span **24 格 / 23 挂载**（1 格空置）—— 与改码前逐项比对一致，非本轮引入。
- `lblOptTaSlope` / `lblOptSpacer3` 已声明并实例化但**未挂入任何容器** —— 同为改码前既有状态。

### 第三轮（§六 扩展）行为变更与风险
- **轨迹页轴表自动刷新默认态由 OFF 改 ON**（业主裁定）⇒ 开页后轴表即每 500ms 重绑一次（`RefreshRuntime` 只刷运行列）。若现场认为开销偏大，由开关手动关闭即可。
- **「刷新轴状态」按钮消失** ⇒ 若自动刷新关闭，用户无法再手动触发一次轴表刷新（配置列改动仍会在参数弹窗保存时经 `OpenAxisEditor` 重载）。这是业主明确接受的功能削减。
- ⛔ 删除按钮属**公开 UI 元素移除**（非公开接口），已按 原 rules/KR-011（已并入 lessons/StaticVerifier-Wiring-Integrity） 完成消费者核验后执行。


## 相关页面

- [[api/SystemControlPage]]
- [[modules/UIDesign]]
- [[decisions/ADR-073-AxisControlUnifiedMontionManager]]
- [[decisions/ADR-075-LaserHeadUiControlConsistency]] —— 第一条之演进（使能类控件改按钮 + 自动刷新分区门控）
- [[guides/AntdUI-Reference]]
