---
title: ADR-071 系统设置页 4 TLP 转 GridPanel + 批M 自适应参数容器统一 + U-4 线激光十项归位工艺设置页
date: 2026-10-15
updated: 2026-10-15
tags: [ADR, UI, 布局, GridPanel, TableLayoutPanel, 批L, 批M, U-4, 跟踪工艺设置, 线激光参数]
status: accepted
---

# ADR-071：系统设置页 4 TLP 转 GridPanel + 批M 容器统一 + U-4 十项归位

> 业主 2026-10-15 裁定：**批L / 批M 开工**（方案 A = 容器统一 + U-4 归位；U-5/U-6 功能搭建下轮单独设计）；
> **U-4 归位方向修正**：线激光十项统一到**工艺设置页 `tbpanelweldponts`（跟踪工艺设置区）**——
> 迁入 = 标定中心 Y/Z + 示教 Y 锁定（原系统设置页）+ 激光超前量 + Y 轴行程上下限（原地已有）等，
> **10 项在跟踪工艺设置区满额**；系统设置页 `tlpLaserCalib` 只留线激光角度 + 超时组。

## 背景

P1 §4.2 的批L（系统设置页 U-4/U-5/U-6）与批M（U-3 自适应参数）自 2026-10-10 立项起未开工，两类遗留：

1. **容器形态分裂**：全项目 6 个 `TableLayoutPanel` 与已改造的 5 个区内 GridPanel 范式（ADR-069 §三 40/30/160）不一致；
2. **U-4 十项分裂两页**：4 项（角度/中心Y/中心Z/示教Y）在 SystemControlPage `tlpLaserCalib`，6 项（比例/偏差/超前/Y补偿/行程上下限×2/地图点数）在 ProcessControlPage `tbpanelweldponts`；
3. **迁移前置发现断链**：`tbpanelweldponts` 的保存处理器 `ProcessControlPage.BtnSaveLaserCalib_Click` **Designer 无订阅（死处理器）**——Tracking 区参数只有 Load 回填、没有保存入口。

## 决策

### 一、6 个 TLP → `AntdUI.GridPanel`（ADR-069 §三 规范全项目化）

| 旧 TLP | 新 Grid | 规格 | Span（标题 40 / 控件 30 / 列 160） |
|---|---|---|---|
| `tlpTrace` | `gridTrace` | 1×4 纵向 | ~~`40:fill;40:fill;40:fill;40:fill`~~ ⚠️ **2026-10-15 [[decisions/ADR-072-FullChainLayoutAndSplitPane|ADR-072]] 修正**——探针实证 `40:fill`=固定 40px（4×40 在 712 容器只占 160 致内容压扁），按原 TLP 绝对行高改回 `40:fill;1140:fill;340:fill;400:fill` + 恢复 AutoScroll（⚠️ **2026-10-16 再演进**：gridTrace 又改 2×2 大分区 `fill fill;fill fill`，以 [[decisions/ADR-072-FullChainLayoutAndSplitPane|ADR-072]] §① 为准） |
| `tlpLaserCalib` | `gridLaserCalib` | 6×8（迁出后 5 行） | ~~`40:fill;40:fill;30:160 160;30:160 160;40:fill;30:160×4;30:160×4`~~ ⚠️ **2026-10-16 四轮演进（业主：标题+四列标准）**：改 `40:fill;40:fill;30:160×4;40:fill;30:160×4;30:160×4` **6 行**（角度组两列并四列——视觉序反转恰与原 Add 序全等，零重排） |
| `tbPanelAlogControl` | `gridAlgoControl` | 4×31, 54 子 | ~~30 行（6 个 `SetColumnSpan` 分区标题 → `40:fill`）~~ ⚠️ **2026-10-16 四轮→五轮复正（业主：标题+四列）**：~~18 行~~（四轮段序逆 ⑤→①、⑤区两对粘主标题下、对内 txt\|lbl 倒置=业主报「参数变少、倒灌」）⇒ 现 **19 行**（6 标题 `40:fill` + 11 四列 + 2 两列，54 格零空格，视觉正序 ①→⑤、段内 `标签\|输入`）；resx Span 重写 + Add 块按目标视觉反转重建 |
| `tbPanelSimTest` | `gridSimTest` | 4×5 | `40:fill;30:160 160;30:160;30:160` |
| `tbPanelAdaparam` | `gridAdaparam` | 6×19, 45 子 | 18 行（5 分区标题 → `40:fill`，批M U-3；⚠️ 2026-10-16 删「焊接工艺库操作」区后 **16 行**，见 [[decisions/ADR-072-FullChainLayoutAndSplitPane|ADR-072]] §二） |
| `tbpanelweldponts` | `gridWeldPonts` | 6×6 → **7 行**（U-4 迁入） | `40:fill;30:160×4;30:160×4;30:160×4;30:160×4;30:160×4;30:160 160` |

**转换规则**（脚本 `_tmp_tlp2grid.py` 两阶段锚点验证，原 rules/KR-020（已并入 lessons/StaticVerifier-Batch-Script-Traps））：
- 标题行判定：单子行 + （全表纵向堆叠 ∨ `SetColumnSpan>1` ∨ 子控件 `Dock=Fill`）→ `40:fill`；其余单子 → `30:160`；多子行 → `30:` 按子数 `160`（>4 列中止）
- 每 TLP 六件套同批改：实例化 / Suspend+Resume / 属性块重写（注入 Span、剥 Column/RowStyles）/ Cell-Add 与 SetColumnSpan 删除 / 挂载行改名 + 逆序重插 / 字段声明改名
- ⛔ `PerformLayout()` 方法调用**改名不删**（Control 通用方法）；块正则必须容忍 `\r?\n`（原 rules/KR-014（已并入 lessons/WikiDriftCorrectionPitfalls））
- ⛔ 属性赋值块必须插在 `InitializeComponent` **方法内**（插到字段声明区 = CS0201 编译错，静态判据 X5 守）

### 二、U-4 十项归位跟踪工艺设置区（`gridWeldPonts`，7 行满额）

| 行 | 内容 |
|---|---|
| r0 | 标题「跟踪工艺设置(Tracking Settings)」`40:fill` |
| r1~r3 | 原 6 项：轴/激光比例、偏差方向、激光超前量、Y补偿系数、Y轴行程下限/上限 |
| r4 | **示教 Y 锁定**（迁入）+ 焊缝地图点数上限（原 r4 挪） |
| r5 | **标定中心 Y + 标定中心 Z**（迁入） |
| r6 | **读取 / 保存按钮**（新增 `btnReadWeldPonts` + `btnSaveWeldPonts`） |

- **迁出**：SystemControlPage `gridLaserCalib` 的 3 标签 + 3 输入（实例化/属性块/字段声明同步移除，`.cs` 残留 0）
- **保存入口闭环**（修复 Step 0.7 发现的死处理器）：
 - `btnSaveWeldPonts.Click → ProcessControlPage.BtnSaveLaserCalib_Click`（**双区落盘**：`AlgorithmsZone.Preset`（Tracking 几何 7 项）+ `AlgorithmsZone.System`（线激光标定 3 项））
 - `btnReadWeldPonts.Click → BtnReadWeldPonts_Click`（`LoadAlgorithmsConfig` 全量重载 + `LoadLaserCalibOnForm` 回填）
- **系统设置页侧收敛**：`SystemControlPage.LoadLaserCalibOnForm` 只留角度回填；`BtnSaveLaserCalib_Click` 只写 `LaserToHorizontalAngleDeg`（System 区）

### 三、U-5/U-6 落地（2026-10-21，接续本节旧范围裁定）

> ~~`panelOpticsSys` / `panelTempSys` 各只有 1 个占位 Label ⇒ 功能搭建（TA 力矩/LA 量纲/振镜内部参数 11 项/温度上下限阈值/示意图）= 新配置键 + 读写链开发，**下轮单独设计**，本轮仅完成容器统一与 U-4 归位（方案 A 范围）。~~
> ⚠️ **2026-10-21 已落地**：复核发现**无需新增配置键**——全部参数已有归宿，故修正本节「需新配置键」的预判。

| 区域 | 容器 | 控件 | 数据源 / 设备 |
|---|---|---|---|
| ① 温度监测 | `panelTempSys` → `gridTemp`（9 行 24 格） | 4 路实时温压 + 报警状态 + 6 项阈值 + 示意图占位 | `WeldHeadConfig.Temp*/Rise*/Pressure*`；`SetAlarmThresholds`（0x7020）· `ReadTemperature/ReadAlarmStatus` |
| ② 振镜控制 | `panelOpticsSys` → `gridOptics`（9 行 33 格） | 振镜 13 项内部参数 + 回零位 | `WeldHeadConfig.DefaultGalvo`；`SetGalvoParams` · `GalvoHome()` |
| ③ LA 对焦 + 光丝对中 | `panel1` → `gridTaLa`（2026-10-23 业主改名 `gridLa`；7 行 22 格） | LA 位置/使能状态、步距+前进/后退、使能切换、量纲；光丝对中警告/报警阈值、曲线导入/点数 | `WeldHeadConfig.MotorPulsePerMm`（`SetMotorPosEnable/ReadMotorStatus`）· `AlgorithmManager.WireFeed` · `WeldParamManager.TaLaCurve.ImportFromCsv` |
| ④ TA 送丝力矩电机 | `panel4` → `gridWireCurve`（8 行 29 格） | **与①跟踪轴控制同构**：位置/伺服/正限/负限/原点/报警状态 + 移动目标/步距输入 + 伺服·回零·停止·移动到 / 步退·步进·负向点动·正向点动 + 运动反馈（扭矩爬升速率已迁出，ADR-084） | 台达轴 `MontionManager.GetDeltaAxisByKeys(TaAxisKeys)` + `ToggleServo/StopAxis/JogStart/HomeAxis/MoveTo/StepMove`；状态判据同 Y 轴（`GetStatusWord` 0x0004/0x0008、软限位、`|pos|≤ε`、`LastCommand`）；`DeltaAxisConfig.TorqueSlope` |
| 底部操作条 | `flowPanel2` | **读取参数 / 修改参数 / 保存参数** | 读取=配置→界面；修改=界面→内存（不落盘不下发）；保存=内存→落盘 + 下发设备（不隐式重收集界面） |

- **TA 目标力**：唯一权威在工艺参数 `WeldAlgorithmsConfig.TaForceN`（ADR-066），本页**不再出现**；扭矩爬升速率曾属电机参数保留在④，**2026-11-05 已迁至 TA 轴「参数」弹窗**（ADR-084）。
- **④ = Y 轴同构**：TA 按钮/输入/状态与①跟踪轴一一对应——8 控制按钮同序（伺服·回零·停止·移动到 / 步退·步进·负向点动·正向点动），绝对/相对移动复用 `DoAbsolute/DoRelative`，点动复用 `JogStart` + `MouseUp/MouseLeave` 兜底；状态文本与轴表 `FillAxisRuntime` 同判据，运动反馈取 `MontionAxis.LastCommand`（ADR-073 下沉，UI 不直写轴）。

- **控件落地**：全部控件由 Designer 声明（符合 2026-09-29 业主裁定），`.cs` 零控件实例化、只做读写链与电机操作。
- **刷新**：唯一 `timerRefresh`（500ms）每拍刷 LA/TA 状态；温度仅在 `button4` 开关打开时刷新；轴表刷新仍受「自动刷新」开关控制。
- **权限**：修改/保存及电机动作（使能/点动/回零/LA 步进/曲线导入）接 `EnsureAdminForWrite`；TA 停止为安全操作不门控，读取按钮不门控。
- **LA 斜坡**：PDO 0x7000 无该对象，按业主要求**不建该项**（不新增无消费配置键）。
- ⚠️ 真编译待 VS；真机验证：四区显示、振镜写读、温压阈值下发、LA 步进/使能、TA 伺服/回零/停止/移动到/步退/步进/点动/扭矩爬升速率（2026-11-05 起该项校验在 TA 参数弹窗）、状态判据与反馈、光丝对中与曲线导入、三按钮读改存链路。

## 关键约束

| 约束 | 说明 |
|---|---|
| ⛔ 迁移三同步 | 控件（实例化+属性块+挂载+字段声明）与 读写链（Load+Save+按钮订阅）必须同轮迁移，漏一项 = wiring 断裂 |
| ⛔ 保存双区 | 迁入项字段属两个区：几何 7 项=④Preset、标定 3 项=①System ⇒ 单按钮双区落盘 |
| ⛔ `gridWeldPonts` 挂载去重 | 迁移组插入时原 map-pair mounts 遗留 ⇒ 已修（kids=23、无重复，判据 M4） |
| ⚠️ 同名方法不冲突 | 两页各有 `LoadLaserCalibOnForm`/`BtnSaveLaserCalib_Click`（不同类，各自私有），**合法**；语义已按页分叉（System=角度 only / Process=全量） |
| ⚠️ 布局判据 | 326 项判据全部通过；改前 backup 仅 7/54 通过（判据可区分新旧结构） |

## 后果

- **正面**：6 TLP 与 5 区内 Grid 范式统一（ADR-069 覆盖全项目）；线激光参数一处可管（跟踪工艺设置区 10 项满额）；死处理器修复，Tracking 区首次具备保存入口
- **负面**：线激光标定参数跨两页保存（系统设置页只存角度）；保存按钮双区落盘语义需上机确认
- **中性**：`.cs` 容器名引用本轮前全为 0 ⇒ 换容器零代码；U-5/U-6 占位维持

## 验证

- 布局判据 **326/326 通过**（判据自修 1 处：X5 布局判据从 PerformLayout 锚改邻域无 `private`）；改前 backup 仅 7/54 通过（准确报出全部旧结构）
- ⚠️ 真编译待 Visual Studio；真机验证见 log

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[decisions/ADR-069-PanelInnerGridZoneCells]] —— §三 布局规范（本 ADR 将其全项目化）
- [[decisions/ADR-060-P4UiLanding]] —— 批L/M 范式来源（本 ADR 落地 U-4 + 容器；U-5/U-6 留后续）
- [[api/SystemControlPage]] · [[api/ProcessControlPage]] —— 消费方页面
