---
title: 配置文件按 TabPage 拆分的迁移与隔离判据
date: 2026-11-19
updated: 2026-11-19
tags: [教训, 配置, 拆分, TabPage, INI, 迁移, 隔离, 整文件重写]
status: active
---

# 配置文件按 TabPage 拆分的迁移与隔离判据

> **一句话**：配置文件按 TabPage 拆分的迁移与隔离判据

## 现象

把一份配置文件拆成多份（每个 TabPage 一套）以避免「某页保存覆盖别页未保存的值」时，踩了三类坑：① zone 粒度不足以表达 TabPage 归属 —— 同一 zone 的控件散落在不同 TabPage（实测 5 个 Enable 开关在系统页、LockYCalib 在工艺页），凭 zone 猜归属必然拆错；② 整文件重写的载体（INIFile.SaveToFile 是 File.WriteAllText、XML 的 SaveXdocument 同理）必然跨页覆盖，隔离的唯一手段是物理分文件，分区落盘不够；③ 迁移源与目标若是同一物理文件的两套 reader，会互相覆盖写回（落盘把已迁走的旧 section 原样写回）。此外同名 section 跨文件必须逐键迁移，不能靠「section 名不变」零迁移；补键模板（自愈）也必须按文件分组，否则会把别页的键补进本文件。

## 根因

配置的存储单元（文件）、页面单元（TabPage）、语义分区（zone）三者粒度不同，zone 只是一个中间概念；用 zone 直接推断文件归属会在「同 zone 跨页」时出错，而整文件重写会把这种错误的代价放大成静默数据丢失 —— 迁移源与目标同路径的两套 reader 又会在正确迁移后把旧键写回，让问题看起来像「迁移没生效」。

## 判据

① 先建「配置项 → 控件 → TabPage → (zone,载体,section)」四段映射（控件树用 Designer 的 Controls.Add 反查父链，TabPage 用 Text 识别），再定文件归属 —— 禁止凭 zone 猜；② 判定隔离是否成立的判据 = 载体是否整文件重写（SaveToFile / SaveXdocument 都是）⇒ 隔离必须物理分文件；③ 迁移源与目标必须是不同物理文件（若同路径就合并为单一 reader，迁走后物理删键）；④ 同名 section 跨文件必须逐键迁移，且迁移要幂等（目标已有键则不覆盖）并「先写目标落盘、再删源键落盘」；⑤ 补键模板按文件分组，只用自己 zone 的键；⑥ 迁移与隔离都要在副本目录用模拟存量文件验证（键分布 + 值保真 + 幂等 + 空 section 清除）。

## 预防

- 配置文件拆分的四段映射与判据：zone/控件/TabPage/文件四者粒度不同；整文件重写载体必须物理分文件；迁移源目标不得同路径；同名 section 跨文件逐键迁移且幂等；补键模板按文件分组

## 相关页面

- [[decisions/ADR-076-SettingsZoneSaveWiring]] D8
- [[lessons/ConfigKeyRemovalAndTruthSourceMigration]]
- [[index/index]]
