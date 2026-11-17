---
title: KR-011 backup 与 output 时机
date: 2026-10-30
updated: 2026-11-02
tags: [规则, 流程, Skill执行]
status: accepted
---

# KR-011 backup 与 output 时机

> **一句话规则**：backup 在改码前出、output 在定稿后出，两者时机不可互换

## 适用范围

**适用**：Phase 2.1（改码前）与 Phase 3.7（定稿后）的出包动作。  
**不适用**：日常手动备份（非本流程）。

## 规则正文

1. ⛔ **backup 在 Phase 2.1（改码前）出，output 在 Phase 3.7（定稿后）出** —— 两者时机不可互换。
2. `backup_adaweld.py` 默认无参模式**只出 backup**；`--output` 只出最新 output 包；`--all` 仅作旧行为兼容、**流程内禁用**。
3. Phase 2.1 打出的 output 装的是**本轮改动之前**的代码 —— 现场拿它验证等于验旧码，**比没有包更危险**。
4. output 的语义是「定稿后的交付物」，只有走完 Phase 2（实现 → 自审 → 影响面 → 静态校验）才成立。

## 判据

- ⛔ 违反判定：Step 2.1 的动作清单里出现 `AdaWeldSystem_output_*.tar.gz`；或 Step 3.7 缺 `--output` 调用。
- ✅ 机器校验：Step 2.1 只出 backup 包、Step 3.7 产出 output 包。

## 反例

| 反例（违规写法） | 正解 |
|---|---|
| 「先打个 output 备份一下」 | 改码前只出 backup |
| 定稿了只出 backup 就交付 | 定稿后 Phase 3.7 必出 output |

## 相关页面

- [[guides/Project-Tools]]
- [[rules/Rules-Index]]
