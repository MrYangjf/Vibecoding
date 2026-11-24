---
title: ADR-110 标定中心 Y/Z 与示教 Y 轴锁定坐标迁入工艺设置页 YT 设置区（分区归属随 UI 落点同步迁移）
date: 2026-11-19
updated: 2026-11-19
tags: [决策, UI, TabPage, 配置, 分区, 迁移]
status: accepted
---

# ADR-110 标定中心 Y/Z 与示教 Y 轴锁定坐标迁入工艺设置页 YT 设置区（分区归属随 UI 落点同步迁移）

> **决策一句话**：标定中心点 Y/Z、示教 Y 轴锁定坐标三个控件对迁至工艺设置页「YT 设置」区；其 XML 落盘分区归属随 UI 落点由 ①System 区迁至 ④Preset 区（XML 键路径不变 ⇒ 存量零迁移），同区唯一写口。

## 背景

2026-11-19 业主裁定：标定中心的 Y 和 Z 以及示教 Y 轴锁定坐标需要移动到工艺设置的 YT 设置下。此前这三项于 2026-11-18 由工艺页「YT 设置」迁入系统设置页·轨迹跟踪·标定参数区，其 XML 落盘分区（①System 区 `SEAM_GUIDE/TEACH_LOCK_Y_MM` 与 `LASER_CALIBRATION/CALIBRATED_CENTER_Y|Z`）也随之迁入。

按 [[decisions/ADR-076-SettingsZoneSaveWiring]] 决策一「落盘分区随 UI 落点迁移」，本轮反向迁回工艺页时，分区归属必须同步迁回工艺页所属区；否则会同时产生两类缺陷：工艺页改值不落盘（写口不在本页），或系统页保存顺带落别人的键（跨区副作用）。

## 决策

1. **UI 落点**：三个控件对（`lbl/txtCalibCenterY`、`lbl/txtCalibCenterZ`、`lbl/txtTeachLockY`）自 `SystemControlPage.gridLaserCalib` 行 5/6 迁至 `ProcessControlPage.gridQuickTracking` 的「YT 设置」区（行 4/5）；系统页删除控件四落点与读写代码，工艺页补回四件套。
2. **分区归属同步迁移**：`TEACH_LOCK_Y_MM` 与 `CALIBRATED_CENTER_Y|Z` 的读写归属由 ①System 区迁至 ④Preset 区。`SaveZoneXmlPreset` 独占三键写口；`WriteConfigTo` 补键模板同步纳入 Preset 区。
3. **XML 键路径不变**：`SEAM_GUIDE/TEACH_LOCK_Y_MM`、`LASER_CALIBRATION/CALIBRATED_CENTER_Y|Z` 三段路径原样保留 ⇒ 存量配置零迁移。
4. **读写入口收口**：工艺页「读取 / 修改 / 保存」三按钮负责三项的内存回填与落盘；`ApplyYtCalibToConfig` 写内存、`LoadYtCalibUi` 回填 UI，遵循 [[decisions/ADR-109-UiButtonTabPageBoundary]]。

## 备选方案

- 仅迁 UI 不迁分区：否决，会产生「工艺页改值不落盘 + 系统页跨区落键」双缺陷。
- 改 XML 键路径到 Preset 语义节点：否决，存量配置需数据迁移且违反「键路径稳定」。

## 后果

### 正面
- UI 落点与落盘归属一致，工艺术语「YT 设置」与配置项一一对应。
- 三键写口唯一（Preset 区独占），静态可断言。

### 负面
- 系统页「轨迹跟踪参数设置」区行数减少；切页才能看到这三项。

## 验证

- 真编译与静态守卫通过；迁移五段核查（控件落点 / 代码引用 / 写入内存 / 落盘分区 / 持久化路径）全通过。

## 相关页面

- [[decisions/ADR-076-SettingsZoneSaveWiring]]（分区归属随 UI 落点迁移）
- [[decisions/ADR-109-UiButtonTabPageBoundary]]（按钮 TabPage 边界）
- [[lessons/MigrationCompletenessAudit]] · [[api/ProcessControlPage]] · [[api/SystemControlPage]]
