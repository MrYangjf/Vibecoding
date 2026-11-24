---
title: ADR-070 振镜摆动即宽度来源开关（光斑宽度跟随并入）+ 手动宽度入振镜卡
date: 2026-10-15
updated: 2026-11-18
tags: [ADR, 配置, 语义合并, 振镜, 光斑宽度, SeamWidthSource, 工艺设置, GA分档, 手动自动互斥, GalvoShapePresets, GalvoGlobalParams]
status: accepted
---

# ADR-070：振镜摆动即宽度来源开关（光斑宽度跟随并入）

> 业主 2026-10-15 裁定两条：
> ① **「光斑宽度跟随」与「启用振镜摆动」实为一个意思**——光斑宽度不可调，真正变化的是振镜摆幅宽度形成了光斑宽度变化 ⇒ 合并为一个开关；
> ② 振镜工艺设置卡（`panelLaserGalvo`）补**手动模式下的固定宽度**输入（`ManualSeamWidthMm`）——「根据焊缝宽度设置摆幅」是自动模式，这里设的是手动模式固定宽度。

## 背景

2026-10-14 ADR-068 §四 引入 `EnableSpotWidthFollow`（②快捷区开关，`ENABLE_SPOT_WIDTH_FOLLOW` 键）单独控制 `SeamWidthSource` 派生。上机后业主点破物理机制：

- `EnableGalvoWeave` 消费链：`LaserWeldHeadWorkflow:259` 摆幅门控（关=振镜不动）+ `WeldParamControlWorkflow:186` `GetAmplitudeMm(w, enabled)` 摆幅计算门控；
- `EnableSpotWidthFollow` 消费链：`SeamWidthSource` 派生 → `WeldParamAdjustmentAlgorithm` 按源选 `CurrentSeamWidth`；
- **拼起来是一条链**：实测焊缝宽度 → 摆幅（还需 `EnableGalvoWeave=true`）→ 振镜摆幅变化 → 形成光斑宽度变化。

⇒ 两开关必须同时 true 才有完整效果，任何单独 true 都是半开状态。第二个开关是**同一件事的重复表达**。

## 决策

### 一、删除 `EnableSpotWidthFollow`，派生源改 `EnableGalvoWeave`

| 项 | 旧 | 新 |
|---|---|---|
| 派生式 | `EnableSpotWidthFollow ? Laser : Manual` | `EnableGalvoWeave ? Laser : Manual` |
| 配置键 | `ENABLE_SPOT_WIDTH_FOLLOW` | **删除**（停读写，存量残留无害） |
| UI 开关 | `swEnableSpotWidthFollow`（快捷区第 6 个） | **删除**（快捷区 6→5 个开关） |
| 属性 | `public bool EnableSpotWidthFollow` | **删除** |

- **振镜摆动开关语义扩展**：`EnableGalvoWeave` = 振镜摆动门控 **+ 焊缝宽度来源开关**（开=实测宽度驱动摆幅（Laser），关=手动固定宽度（Manual））
- **职责并入**：原 `swEnableSpotWidthFollow_CheckedChanged` 的 `RefreshSpotWidthByGain()` 重算，移入 `swEnableGalvoWeaveQuick_CheckedChanged`（快捷侧）与 `swEnableGalvoWeave_CheckedChanged`（激光工艺页侧）两处
- ⚠️ 兼容性：`SeamWidthSource` 属性保留只读派生（消费方 `WeldParamControlWorkflow`/`WeldParamAdjustmentAlgorithm`/`WeldParamManager` 零改动），仅**语义源**变化

### 二、手动固定宽度入振镜卡（`panelLaserGalvo`）

> **2026-10-15 补（同日三轮）——双入口文案语义修正（业主裁定）**：
> - **激光工艺卡 `lblGalvoWeave`**：「振镜摆动启用」→ **「开启摆动/停止摆动」**——它是**运动控制开关**（直接启停振镜摆动），语义即指令动作；
> - **快捷设置 `lblEnableGalvoWeaveQuick`**：「振镜摆动」→ **「振镜跟随摆动工艺」**——它是**工艺启停开关**，控制自适应过程中是否启用振镜跟随焊缝摆动；
> - `lblProcessEnableTip` 补一句「振镜跟随摆动工艺控制自适应过程中是否启用振镜跟随焊缝摆动」。
> ⚠️ 两控件仍绑定同一配置 `EnableGalvoWeave`（唯一键），文案差异表达**同一开关的两个操作视角**（运动 vs 工艺），不新增配置项。

- 新增 `lblManualWidth`（「手动焊缝宽度(mm)」）+ `txtManualWidth`（`AntdUI.Input`）挂 `gridLaserGalvo`（~~`40:165 120`~~ ⚠️ 三轮后 `30:160 160`，见 [[decisions/ADR-069-PanelInnerGridZoneCells|ADR-069]] §三）
- **失焦即存**：`txtManualWidth_Leave` → 正数校验（≤0/解析失败还原原值 + warn）→ `ManualSeamWidthMm` 赋值 → `SaveAlgorithmsZone(Adapt)`（该键属③自适应区）→ Manual 源时 `RefreshSpotWidthByGain()`
- **双入口同源**：与系统设置页 `txtParamManualWidth`（`BtnSaveAlgoThresh` 保存）读写**同一配置项** `ManualSeamWidthMm`；两页互不联动（后操作者生效，INI 为单一真相源，重开页面即回读一致）

## 关键约束

| 约束 | 说明 |
|---|---|
| ⛔ `EnableSpotWidthFollow` 不得再出现于代码 | 残留于注释的演进标注合法（如「已删除并入振镜摆动」） |
| ⛔ 快捷区开关数 = 5 | `gridProcessDebug` Span r2 由 4 列改 2 列（`40:165 95`），第 2 行只留 自适应+光丝对中 |
| ⛔ 手动宽度校验 | 正数校验失败须**还原原值**并 warn，不得落盘非法值 |
| ⚠️ 语义变化需上机确认 | 历史 INI 若 `ENABLE_GALVO_WEAVE=true` 而 `ENABLE_SPOT_WIDTH_FOLLOW=false`，合并后行为变为 Laser 源——**该组合本就是半开无效态**，但现场 INI 值需核对 |

## 后果

- **正面**：两开关合一消除半开态；「摆幅驱动光斑」物理链在配置模型中变成单一事实；振镜卡形成「图形→演示/回零→启用→手动宽度」完整工艺组
- **负面**：振镜摆动开关承载双重语义（摆动门控 + 宽度来源），日志/文档需说明；系统设置页 `txtParamManualWidth` 与振镜卡形成双编辑入口（同源无联动）
- **中性**：`SeamWidthSource` 消费方零改动（只读派生属性签名不变）

## 验证

- ⚠️ 真编译待 Visual Studio；真机验证见 log 条目

## 备选方案

- （待补：考虑过什么、为什么放弃）

### 2026-11-18 · 决策演进 · GA 按图形分档 + 手动宽度改由 GA 档承担 + 手动/自动两套模式

> 业主 2026-11-18 裁定三条：
> ① **图形设置完全由指令区接管**（GA 设置区的重复控件删除）；
> ② **GA 设置的宽度/长度/频率按每种图形各存一档**（不同图形这几个设置是变化的；没有配置时默认加载 Line 档）；
> ③ **GA 设置就是「自适应参数没有输出时的宽度」** —— 手动模式（振镜未启用 ⇒ Manual 源）的恒定宽度改由 GA 档承担。

#### 一、GA 图形参数按图形分档

| 项 | 旧 | 新 |
|---|---|---|
| 存储 | `WeldHeadConfig.DefaultGalvo` 单份宽/长/频 | `WeldHeadConfig.GalvoShapePresets`：每图形一份 `GalvoShapeParams`（宽/长/频） |
| 持久化 | `WeldHeadSlave.xml` 的 `GALVO/WIDTH\|LENGTH\|FREQUENCY` | 追加 `GALVO/<CIRCLE\|EIGHT\|LINE\|ARC>/WIDTH\|LENGTH\|FREQUENCY`；顶层保留为存量迁移基准 |
| 缺档回退 | — | 指定图形缺档 ⇒ 回退 **Line 档**（业主裁定「当没有配置是默认加载 Line」） |
| UI | 图形与宽/长/频各自独立 | 切换图形 Radio ⇒ 载入该图形档；保存 ⇒ 写回当前图形档 |

- **存量迁移**：老 XML 仅有顶层一份 ⇒ 各档缺省值取该旧单档值（读侧 `legacyWidth/legacyLength/legacyFrequency` 承接），不丢现场配置。
- **全局项不动**：角度/起止角/中心/压缩/目标尺寸/斜椭校正仍属 `DefaultGalvo`（各图形共用），**只有宽/长/频分档**。

#### 二、`DefaultGalvo` 改为「当前生效参数集合」

- GA 分档后 `DefaultGalvo` 的宽/长/频不再被 UI 直接编辑，但「**全量下发 `DefaultGalvo`**」的路径仍在（工艺页保存工艺参数、系统设置页保存激光头参数）⇒ 若不同步会把设备刷成陈旧旧值（本轮实测的真实缺口）。
- 正解：`WeldHeadConfig.SyncDefaultGalvoFromShape(pattern)` 把当前档镜像进 `DefaultGalvo`（图形 + 宽/长/频），三处调用点（页面加载 / 切换图形 / 保存档）。
- ⛔ 禁让「全量下发」路径直接使用未同步的 `DefaultGalvo`。

#### 三、手动宽度改由 GA 档承担（`ManualSeamWidthMm` 删除）

| 项 | 旧 | 新 |
|---|---|---|
| 配置项 | `ManualSeamWidthMm`（③Adapt 区，INI `MANUAL_SEAM_WIDTH_MM`） | **删除**（见 [[decisions/ADR-076-SettingsZoneSaveWiring]] 决策 D5） |
| Manual 源宽度 | `_config.ManualSeamWidthMm`（固定值） | **GA 档宽度**（`WeldParamAdjustmentAlgorithm.ManualFixedWidthMm()` ⇒ `GetGalvoShape(pattern).Width`） |
| UI 落点 | 振镜卡 `txtManualWidth` + 轨迹点区 `txtParamManualWidth` | **双入口均删除** |

- 依据：「GA 设置就是在自适应参数没有输出时的宽度」——Manual 源（振镜未启用 ⇒ 不随线激光宽度变化）恰是「自适应没有输出」的场景。
- 振镜未启用 ⇒ 没有图形 ⇒ 图形取配置（`ResolveGalvoPattern` 0/越界 ⇒ Line）⇒ 回退 **Line 档宽度**，与缺档回退同口径。
- ⛔ 该取宽度处**不写 `catch` 静默返 0**（「静默兜底掩盖未读到」，见 [[lessons/UiModuleRemovalCleanup]] 坑七）。

#### 四、手动 / 自动两套模式（互斥）

| | 自动模式 | 手动模式 |
|---|---|---|
| 触发 | 自动焊接 / 自适应工艺启动 | UI 手动调试（GA 区「手动下发 / 关闭退出」按钮组） |
| 振镜下发 | `ApplyGalvoAmplitude` 每拍随动 | **输出一次**（`GalvoManualStart`），不进随动循环 |
| 宽度来源 | Laser（线激光实测） | Manual（恒定，取 GA 档） |
| 互斥 | ⛔ 自动模式下 UI 手动按钮不生效 | ⛔ 手动动作与生产流程互斥 |

- 门禁复用 `LaserWeldHeadWorkflow.EnsureManualWeldHeadActionAllowed`（自动焊接流程在跑 ⇒ 拒绝）——与既有手动动作同口径，**不另立门禁**。
- UI 层同步置灰（`btnGalvoManualStart/Stop` ← `laReady && !IsAutoWeldingRunning`）；⛔ 手动按钮**不按振镜启用态禁用**（手动调试的目的正是「振镜未启用时也能下发看效果」）。
- 替代已删的 `GalvoDemo()`（零调用方 + UI 入口已删）：新 API 对 `GalvoManualStart(pattern, shape)` / `GalvoManualStop()`。

#### 五、默认长宽频清理（`DefaultGalvo` 拆出全局项类型）

> 业主裁定（2026-11-18 第二批）：「**GA 分档后，原来没有按照图形区分的默认长宽频需要清理掉，不再任何地方起作用**」。

- **不只标记弃用，而是物理删除**：`DefaultGalvo` 的类型由 `GalvoParams`（**协议参数结构**，含图形/宽/长/频）改为新建的 **`GalvoGlobalParams`**（只含 10 个全局项：角度/起止角/中心/压缩/目标尺寸/斜椭校正/使能）⇒ 该配置实例上**物理不存在**图形与宽/长/频。
- **下发改为组装**：新增 `WeldHeadConfig.BuildGalvoParamsFor(pattern)` —— 全局项取 `DefaultGalvo`，**图形 + 宽/长/频取该图形档** ⇒ 两处「全量下发 `DefaultGalvo`」的路径（工艺页保存工艺参数、系统设置页保存激光头参数）改走此方法。
  - ⚠️ **本节取代上文 §二 的「镜像」方案**：`SyncDefaultGalvoFromShape` / `SyncCurrentGalvoToDefault` 已随之删除 —— 镜像方案仍让 `DefaultGalvo` 保留无来源字段，与本裁定「清理掉」冲突。
- **XML 同步**：顶层 `GALVO/WIDTH|LENGTH|FREQUENCY` **不再写入**，也不再读进 `DefaultGalvo`；宽/长/频一律落 `GALVO/<图形>/` 子节点。
- **存量迁移**：老 XML 只有顶层三键 ⇒ 读一次作各档缺省值（缺省取协议默认 宽 1.0 / 长 1.0 / 频 50），读后即以档子节点为准。
- ⛔ 禁直接下发 `DefaultGalvo`（会带出无来源的空位）。
- ⛔ `GalvoParams` 的图形/宽/长/频字段本身**保留**（协议下发要用），但其**配置来源**已清空 —— 注释必须写明"配置路径已无来源，仅协议组装时由档填充"。

## 相关页面

- [[decisions/ADR-068-WeldAlgorithmsConfigZoneReorg]] —— EnableSpotWidthFollow 引入方（本 ADR 推翻其 §四 该项）
- [[decisions/ADR-069-PanelInnerGridZoneCells]] —— 振镜卡容器（本 ADR 向其补控件）
- [[decisions/ADR-042-SeamTrackingConsolidated]] —— 摆幅公式 `宽度×(1+k)` 裁定来源
- [[api/ProcessControlPage]] —— 消费方页面
