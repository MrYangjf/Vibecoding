---
title: 配置所有权归 Manager 与跨页写入粒度
date: 2026-11-19
updated: 2026-11-19
tags: [教训, 配置, Manager, 写入粒度, 键级写入, 重构, 迁移]
status: active
---

# 配置所有权归 Manager 与跨页写入粒度

> **一句话**：配置所有权归 Manager 与跨页写入粒度

## 现象

把散落在各配置类里的配置路径与载体创建收归单一 Manager（ConfigFileManager）时，踩到两类坑：① 「跨页覆盖」的根因被误判为「文件数不够」—— 实测根因是写入粒度：载体是整文件重写（INIFile.SaveToFile = File.WriteAllText、SaveXdocument 整篇重写），未涉及的 section 取内存旧值覆盖磁盘新值；正解是保存前 Reload + 只写目标键（键级），单文件即可跨页隔离，不必拆文件。② 同一 section 被多个 TabPage 共享时（实测 PROCESS_CONTROL 被两个 TabPage 共用、SEAM_GUIDE 被两个共用），section 粒度不够，必须键级写入。③ 换归属模型时若保留旧数据与迁移代码，新旧两套读写器并存会让「迁移没生效」的现象与「路径没生效」难以区分，且迁移源与目标同物理文件时两套 reader 会互相覆盖写回。

## 根因

配置的所有权单元是 Manager，视图单元是 TabPage，两者粒度不同；用视图单元切分数据所有权会让所有权被切碎成多套载体。而整文件重写载体的覆盖问题不在文件数上，在于「写整个文件时未涉及的键取自内存」——把写入粒度降到键级并先 Reload，同一文件内即可承载跨页配置且互不干扰。反过来，重构归属模型时沿用迁移路径会同时保留新旧两套语义，失败现象互相掩盖，无法定位。

## 判据

① 先判「载体是否整文件重写」（SaveToFile / SaveXdocument 都是）⇒ 覆盖根因在写入粒度，先做 Reload + 键级写入的原型验证（副本目录），再决定要不要拆文件；② 同一 section 被多个 TabPage 共享时必须键级；③ 换归属模型（Manager 收口、目录统一）时直接舍弃旧数据 + 生成默认模板，不写迁移代码；④ 若必须迁移，迁移源与目标不得是同一物理文件的两套 reader；⑤ 补键模板写独立临时载体，不污染正式载体；⑥ 配置项清理要物理删除（含一次性迁移分支与日志）；⑦ 「区域」键清单以各区实际保存的键为准（读取键是保存键的超集）。

## 预防

- 配置所有权归 Manager、UI 不参与分割；覆盖根因在写入粒度而非文件数；同 section 跨 TabPage 必须键级写入；换归属模型直接舍弃旧数据而非迁移；迁移源目标不得同路径；补键模板用独立临时载体

## 相关页面

- [[decisions/ADR-006-ModuleOrganizationPatternStandard]] D2
- [[lessons/ConfigFileSplitByTabPage]]
- [[index/index]]
