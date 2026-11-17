---
title: ADR-070 振镜摆动即宽度来源开关（光斑宽度跟随并入）+ 手动宽度入振镜卡
date: 2026-10-15
updated: 2026-10-15
tags: [ADR, 配置, 语义合并, 振镜, 光斑宽度, SeamWidthSource, 工艺设置]
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

## 相关页面

- [[decisions/ADR-068-WeldAlgorithmsConfigZoneReorg]] —— EnableSpotWidthFollow 引入方（本 ADR 推翻其 §四 该项）
- [[decisions/ADR-069-PanelInnerGridZoneCells]] —— 振镜卡容器（本 ADR 向其补控件）
- [[decisions/ADR-042-SeamTrackingConsolidated]] —— 摆幅公式 `宽度×(1+k)` 裁定来源
- [[api/ProcessControlPage]] —— 消费方页面
