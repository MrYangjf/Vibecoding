---
title: Python 脚本改 .cs 的字节安全三坑
date: 2026-11-18
updated: 2026-11-18
tags: [教训, 工具坑, Python, 字节安全, BOM, CRLF, 行尾, git show, 批量改写]
status: active
source: AdaWeldSystem（2026-11-18 GA 分档改造 + LA 默认焦平面改名期间，7 个文件被写成 LF、6 个文件被误加/误去 BOM）
---

# Python 脚本改 .cs 的字节安全三坑

> **一句话**：Python 脚本改 .cs 的字节安全三坑

## 现象

用 Python 批量改写 C# 源文件后，行尾与 BOM 被静默破坏：① 读文件未指定 newline 保留，universal newlines 把 CRLF 全转成 LF，写回即整文件变 LF（仓库 core.autocrlf=true，工作区应为 CRLF）；② 写文件用 encoding=utf-8-sig，无条件给原本无 BOM 的文件加上 BOM；③ 核查脚本用 git show HEAD:<path> 取基线时在 Windows 上路径写成反斜杠，git 静默失败返回空字节，导致 HEAD_BOM 恒判 False，进而误判所有文件多了 BOM 并误执行去 BOM。

## 根因

Python 的文本模式读写默认做换行与编码转换（universal newlines + BOM 自动加），而 C# 源文件在这两个维度上都是仓库强约束（autocrlf 决定行尾、BOM 逐文件不同）；核查脚本若自身判据不可靠（基线读取失败当作无 BOM），会把正确文件当损坏文件修，越修越错。

## 判据

① 读写 .cs 一律二进制模式：读用 open(path,'rb') 后手动 decode，写用 open(path,'wb') 手写 BOM 与 CRLF；⛔ 禁 io.open(...,encoding='utf-8-sig') 写（无条件加 BOM），⛔ 禁 io.open(...).read() 后再写（默认换行转换丢 CRLF）。② 匹配多行文本前先归一化（读时 replace CRLF→LF，写时再 replace LF→CRLF），否则 CRLF 文件全部匹配失败。③ 核查基线时 git show HEAD:<path> 的路径必须用正斜杠（Windows 下 os.path.normpath 产生反斜杠，git 会静默失败）；④ 核查脚本必须先断言基线读取成功（len(head)>0）再判 BOM，否则空字节恒判无 BOM ⇒ 误执行修复。

## 预防

- 改码前记录 md5；统一用一个二进制读写 helper；收尾必跑行尾/BOM 与 HEAD 一致性核查，且核查脚本自带基线非空断言

## 相关页面

- [[lessons/ConfigKeyRemovalAndTruthSourceMigration]] —— 真相源迁移 + 删配置项 8 段清单（改造同一批文件）
- [[lessons/StaticVerifier-Batch-Script-Traps]] —— 批量脚本的其它事故（幂等 / 路径 / 副本试跑）
- [[lessons/WikiGovernanceBatchingPitfalls]] —— wiki 批量治理脚本事故清单
- [[decisions/ADR-070-GalvoWeaveAsWidthSource]] —— §五 默认长宽频清理（本次改造对象）
- [[decisions/ADR-067-LATaSettingsSemanticRework]] —— LA 默认焦平面（本次改造对象）
- [[architecture/CodeMap]] —— 模块骨架与定位陷阱
- [[index/index]]
