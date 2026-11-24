---
title: ADR-109 UI 读改存三按钮的 TabPage 边界（严格化）
date: 2026-11-19
updated: 2026-11-19
tags: [决策, UI, TabPage, 配置, 分区, 读取, 边界]
status: accepted
---

# ADR-109 UI 读改存三按钮的 TabPage 边界（严格化）

> **决策一句话**：每个页面的「读取 / 修改 / 保存」按钮必须**只对本 TabPage 生效**（严格边界：同页不同 TabPage 之间也算越界）；「读取」写回**现有**配置对象而不替换它 ⇒ 其它 TabPage 已改未存的内存改动不被丢弃。

## 背景

配置按 TabPage 分区后（[[decisions/ADR-076-SettingsZoneSaveWiring]] D6/D8），写路径已按区分区落盘，但「读取」路径仍停留在全量语义。业主复核要求确认：**每个页面的读取/修改/保存按钮是不是只对本页面生效**。

实测建立「按钮 → 配置项 → zone」映射矩阵后，发现三处越界：

| 按钮 | 所在 TabPage | 原实现 | 问题 |
|---|---|---|---|
| `BtnReadAutoParam_Click` | 工艺·自适应 | `LoadAlgorithmsConfig()`（**全量 5 区**）+ 回填 `LoadProcessEnableOnForm` | ① 全量重载 ② 顺带刷新**激光工艺区**的 Y 指令 radio |
| `BtnReadLaserZone_Click` | 工艺·激光工艺设置 | 同上 + 回填 `LoadFlowSwitchOnForm` | 顺带刷新**自适应区**的两个输入框 |
| `BtnReadLocal_Click` | 系统·轨迹跟踪 | 同上 + 回填 `LoadProcessEnableOnForm` | 顺带刷新**流程控制区**的 5 个 Enable 开关 |

两个叠加缺陷：

1. **全量重载替换配置对象**：`LoadAlgorithmsConfig()` 内部 `new WeldParamConfig()` 并赋值给 `_algorithmsConfig` ⇒ 其它 TabPage 已「修改参数」但未保存的内存改动被**整体丢弃**（不只是没落盘，内存态也没了）。
2. **跨区回填**：`LoadFlowSwitchOnForm` 与 `LoadProcessEnableOnForm` 两个回填方法被两页互用，每页的「读取」顺带刷新别的 TabPage 的控件。

⛔ **写路径本就正确**：`SaveZoneIni(zone)` 先 `Reload()` 再只写本区键（键级）⇒ 跨 TabPage 不覆盖；「修改」「保存」两按钮原本就只写本区。

## 决策

1. **`LoadAlgorithmsZone` 复活并改造为 `params AlgorithmsZone[]` 重载**：
   - 先 `Reload()` 载体（⛔ 否则读到载体内存快照而非磁盘真值）；
   - 只读指定 zone；
   - **写回现有 `_algorithmsConfig` 对象**（⛔ 禁 `new`、禁替换实例）⇒ 其它 TabPage 的内存改动保留。
2. **三个「读取」按钮**改为：刷本 TabPage 的 zone + 只回填本 TabPage 的控件。
3. **跨 TabPage 回填从按钮移除**：被移走的控件由**页面构造**时的批量回填（`LoadXxxOnForm`）与本 TabPage 自己的读取入口负责。

### TabPage ↔ zone 对照（现行）

| TabPage | zone | XML | INI |
|---|---|---|---|
| 工艺·激光工艺设置 | `Preset` + `Quick` | — | `PROCESS_CONTROL`（12 + 1 键） |
| 工艺·自适应工艺参数设置 | `Adapt` | — | `WELD_PARAM_ADJUST`（2 键） |
| 系统·流程控制与测试 | `Flow` | — | `PROCESS_CONTROL`（5 键） |
| 系统·轨迹跟踪参数设置 | `System` | `SEAM_GUIDE` + `LASER_CALIBRATION`（13 键） | `SEAM_GUIDE`（16 键） |

## 后果

### 正面

- 「读取」不再丢弃其它 TabPage 未保存的内存改动。
- 每个按钮的「影响范围」可被「它会动到哪些区」单问题界定 ⇒ 可静态断言。

### 负面

- 「读取」不再刷新别的 TabPage 的控件（用户需切到那个 TabPage 再点它自己的读取）。

## 验证

- 真编译 `errors=0 rc=0`；静态守卫 PASS；19 项自检全通过（按钮→zone 映射、跨区回填移除、对象不替换、改名残留 0）。

## 相关页面

- [[decisions/ADR-076-SettingsZoneSaveWiring]]（分区落盘主线，D6/D8）
- [[lessons/UiButtonZoneBoundary]] · [[api/WeldParamManager]]
- [[api/ProcessControlPage]] · [[api/SystemControlPage]]
