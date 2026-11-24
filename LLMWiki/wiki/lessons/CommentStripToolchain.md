---
title: 全库注释瘦身工具链的四个坑
date: 2026-11-19
updated: 2026-11-19
tags: [教训, 注释, 批量改造, 行尾, BOM, 工具链]
status: active
---

# 全库注释瘦身工具链的四个坑

> **一句话**：全库注释瘦身工具链的四个坑

## 现象

把「移除 remarks + summary 压到 20 字」这类口径全库落到 1137 处 / 128 文件时，踩到四个坑：① **行尾基线不能用 `git show HEAD:`** —— 仓库 `core.autocrlf=true` 时 HEAD blob 是 LF、工作区是 CRLF，用 HEAD 比对会误报数十处「行尾变化」，正解是用本轮改码前的 backup 包做基线；② **读文件必须归一化 CRLF→LF、写回按原状加回** —— 直接 `split("\n")` 会把 `\r` 留在行尾而新行不带，造成「混行」，守卫会以 eol-mixed 拦下（首批 dry-run 全部 SKIP）；③ **`<see cref="X"/>` 是自闭合标签** —— 标签配对判据若用「开标签数 = 闭标签数」会把 26 处自闭合误报为不配对；④ **批量脚本禁跨脚本共享 cache** —— 后执行的脚本用旧 cache 覆盖先执行的成果（本轮 8 处接入被覆盖成 0 且不易察觉），正解是每个文件独立「读→改→立即写回」。

## 根因

注释类批量改造的正确性判据不是「跑完没报错」，而是「剥离注释后逐字比对证明代码字符零改动 + 行尾/BOM 与基线一致 + 标签配对无误」；而这三项判据自身若基线取错或口径有假阳性，会把正确文件判成损坏并触发错误修复，因此判据脚本必须自带「基线非空断言」与「自闭合标签排除」。

## 判据

① 改码前先出 backup 包并以其为行尾/BOM 基线（⛔ 禁用 `git show HEAD:` 做行尾基线）；② 脚本读写两侧都归一化行尾（读 CRLF→LF，写按原文件类别加回）；③ 标签配对判据排除自闭合标签（`<see .../>`）；④ 每个文件独立读改写，⛔ 禁跨脚本共享 cache；⑤ 收尾跑「剥离注释后逐字比对 + 行尾/BOM 基线比对 + remarks 计数归零 + summary ≤20 字」四项断言；⑥ 与既有注释补全工具的执行顺序固定为「先补 param/returns、再删 remarks/压 summary」。

## 预防

- 全库注释瘦身的四项断言：剥离注释逐字比对、基线取 backup 包而非 HEAD、自闭合标签排除配对、逐文件独立读写禁共享 cache

## 相关页面

- [[decisions/ADR-007-CodeSimplificationStandard]] D2
- [[standards/CodeSimplification]] §二②
- [[lessons/CommentSimplificationBatchPitfalls]]
- [[index/index]]
