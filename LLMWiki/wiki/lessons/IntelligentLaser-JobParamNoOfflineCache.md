---
title: 英莱 Job 参数离线缓存必须移除（设备为唯一真相源）
date: 2026-08-24
tags: [教训, 英莱, 线激光, Job参数, 离线缓存, 代码精简]
source: AdaWeldSystem/LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs, AdaWeldSystem/UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs
---

# 英莱 Job 参数离线缓存必须移除（设备为唯一真相源）

## 结论（2026-08-24 用户澄清 + 代码精简）

英莱 Job Parameter（设备侧算法参数）**以线激光设备为唯一真相源**：未连接设备即无 Job 参数，原离线缓存体系（`LoadOfflineCache` / `SaveOfflineCache` / `_ilIniFile` = `Config/Jobs/IntelligentLaserJobParams.ilini` / `HasJobParamCache`）**整体移除**。

## 根因

1. **离线缓存会误导用户**：程序异常退出（崩溃/强杀）后重连，硬件端 Job 参数可能与上次落盘的 `.ilini` 不一致；离线缓存显示的是「上次成功写盘的旧值」而非设备实际值，违反「UI 状态真值来自硬件查询」（见 [[lessons/IntelligentLaser-Pitfalls]] §5.4）原则。
2. **设备是唯一来源**：`InitJobParamsCallback`（全量）与 `JobParamsChangedCallback`（增量）两个 SDK 回调已能在连接后实时把 Job 参数推到 `_jobParams` 缓存；切 JOB / 改参数都会经 `OnJobParamsChanged` 刷新，无需本地落盘兜底。
3. **无「枚举所有 Job 号」API**：英莱 SDK 仅 `FetchJobInfo`（查当前 Job ID）+ `SetSensorJobInfo`（切换/新建/删除），**没有列出全部 Job 号的能力**——`cmbJob` 只能以「当前 Job」为唯一可选项（官方 demo 同样无 Job 列表 UI）。因此「离线缓存所有 Job 号」本就无从谈起。

## 修改清单（本次落地）

| 位置 | 改动 |
|------|------|
| `IntelligentLaserCameraRun.cs` | 删 `_ilIniFile` / `LoadOfflineCache` / `SaveOfflineCache` / `HasJobParamCache` 及 3 处 `SaveOfflineCache` 调用；新增 `OnJobParamsChanged` 回调注册（`_cbJobParamsChanged`+GCHandle，遵循 GC 三层保护）、`JobParamsChangedCallback`（按名增量刷新 `_jobParams`）、`JobParamsChanged` 事件 |
| `ILCamPage.cs` | `RefreshJobSelect` 连接同步时从设备读当前 Job 预填 `cmbJob`（保持原逻辑，删离线无关代码无影响） |
| `ILAlgoForm.cs` | `InitIlModule` 删「拉取失败回退离线缓存」分支（未连接→空表）；订阅 `JobParamsChanged` → 重拉 `FetchAllJobParams` 刷新；`dgvILParams.CellEndEdit` 单元格级单条 `ApplyJobParams`（成功回读刷新该格、失败恢复原值），移除整表 `btnSet` 按钮 |
| `ILAlgoForm.Designer.cs` | 删除 `btnSet` 控件声明/初始化/字段（CellEndEdit 取代批量下发） |

## 关联

- [[api/IntelligentLaserCameraRun]] — `JobParamsChanged` / `OnJobParamsChanged` 回调契约
- [[lessons/IntelligentLaser-Pitfalls]] — §5.4 连接后必须检测硬件实际状态（离线缓存误导同源）
- [[lessons/IntelligentLaserSensorControl]] — UI 不缓存设备态真相源
- [[standards/CodeSimplification]] / [[standards/UiStateSimplification]] — 代码精简规范
