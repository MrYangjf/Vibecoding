---
title: 配置键删除与真相源迁移的连带门禁
date: 2026-11-18
updated: 2026-11-18
tags: [教训, 配置, 真相源, 删除配置项, 镜像同步, 陈旧值, 振镜, GA分档]
status: active
source: AdaWeldSystem/MotionControl/WeldHeadSlaveDevice.cs + MotionControl/MontionManager.cs + WeldParamControl/*（2026-11-18 GA 按图形分档 + 删三项自适应输出配置）
---

# 配置键删除与真相源迁移的连带门禁

> **一句话**：配置键删除与真相源迁移的连带门禁

## 现象

GA 宽/长/频由单份 DefaultGalvo 改为按图形分 4 档（GalvoShapePresets）后，① 旧的整体下发路径（工艺页保存、系统设置页保存各一次 SetGalvoParams(DefaultGalvo)）仍把 DefaultGalvo 整份写设备，而它的宽/长/频已无人维护、停在初始旧值 1.0/1.0/50 ⇒ 每次保存都把设备刷回旧参数；② 删配置项 ManualSeamWidthMm/SpotWidthGain/ParamOutputHz 后残留散落多层（INI 键常量、字段默认值、读取、钳位、保存、算法层转发属性、Manager 层转发属性、UI 读写与控件四落点），任一层漏删即成死配置。

## 根因

真相源迁移只改了写入端（谁负责赋新值），没检查整体下发端（谁把这个对象整份搬出去）；配置项删除只改了声明端，没顺着数据链逐层拔。字段在结构体里长期存在 ⇒ 整体下发路径永远合法 ⇒ 陈旧值必然被写下去。

## 判据

① 真相源迁移后必查：grep 该结构的全部整体写入点（如 SetXxxParams(obj)），逐个问这个对象的每个字段现在由谁维护；不再由 UI 维护的字段必须先有镜像同步点（本轮正解 = WeldHeadConfig.SyncDefaultGalvoFromShape(pattern) 把当前档镜像进 DefaultGalvo，调用点=页面加载/切换图形/保存档）。② 删配置项按 8 段清单逐项拔：INI 键常量 / 字段声明与默认值 / 读取 / 钳位与自愈 / 保存 / 算法层转发属性 / Manager 层转发属性 / UI 读写加控件四落点，缺一段即残留死配置。③ 残留检查只统计代码引用；注释里的沿革标注合法，不算残留。

## 预防

- 真相源迁移的必查动作 = grep 该结构的全部整体写入点并逐字段问由谁维护；删配置项用 8 段清单逐项打勾，残留统计按代码引用判定

## 相关页面

- [[decisions/ADR-070-GalvoWeaveAsWidthSource]] —— GA 按图形分档 + 手动/自动两套模式（演进节）
- [[decisions/ADR-076-SettingsZoneSaveWiring]] —— 决策 D5：③自适应区删三项 + 分区收缩
- [[decisions/ADR-103-no-value-hold-and-distance-segment]] —— 输出触发改按段落长度（落地演进）
- [[lessons/UiModuleRemovalCleanup]] —— 控件删除的 7 项删除单元 + 静默兜底反模式（坑七）
- [[lessons/ConfigZoneSaveWiring]] —— 分区落盘接线纪律
- [[api/ProcessControlPage]] · [[api/LaserWeldHeadWorkflow]] · [[architecture/CodeMap]]
- [[index/index]]
