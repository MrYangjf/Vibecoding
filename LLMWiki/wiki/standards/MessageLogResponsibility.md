---
title: 提示与日志职责分离（弹窗只报结果 · BUG 归 LOG）
date: 2026-10-10
updated: 2026-11-03
status: accepted
tags: [标准, UI, 日志, 提示, 调试]
---

# 提示与日志职责分离（弹窗只报结果 · BUG 归 LOG）

> **业主约束（2026-10-10，上机实测轮固化）**：
> 「提示一般管的是结果反馈，譬如没有记录、测试结束、测试终止这类结果报告。
> 它们实际的 BUG 应该是由 log 记录，方便调试寻找问题。」
> 触发案例：追溯页选日期后同时弹「SQLite 单日查表错误」+「区间没有记录」两个框——
> 前者是 BUG 不该上弹窗，后者才是结果反馈。

## 判据

| 类别 | 归属 | 形态 | 例子 |
|---|---|---|---|
| **结果反馈**（用户动作的正常结果） | 弹窗 / 状态文案 | `AntdUI.Message`、界面标签 | 「区间没有生产记录」「测试结束」「测试终止」 |
| **实际 BUG / 异常**（本不该发生、需排查） | LOG | `GlobalCommData.ShowLog(TAG, msg, msgLevel)`（唯一日志口） | SQLite 查表异常、落库失败、读取生产记录失败 |

## 规则

1. **`catch` 块内禁止弹窗**：异常一律 `ShowLog`（`MessageLevel.Error`/`Warning`，带上下文参数与时间），
   然后按「零行 / 空值」继续走结果反馈路径（界面照常报「无记录」这类结果）。
2. **弹窗文案不得携带异常细节**（`ex.Message` 不进弹窗）——细节只进 LOG，方便调试定位。
3. 结果反馈文案用**用户视角的完整范围**（如「{start} 至 {end} 没有生产记录」），不做中间态误报。
4. 日志口唯一：`GlobalCommData.ShowLog(TAG, message, msgLevel)`；TAG 用类名。

## 落地位置（2026-10-10 首批）

- `DataReviewerPage.LoadProductRecords` catch：~~`Message.warn("读取生产记录失败：…")`~~ → `ShowLog`，
  结果提示统一由 `InitPCLDir` 的「区间没有生产记录」承担
- `ProductDatabaseHelper.SelectTables`：缺表跳过（缺表不是错误）；单日查表异常 `ShowLog` + 跳过当日，
  不中断整段区间、不向界面抛错

## 相关页面

- [[api/GlobalCommData]] —— ShowLog 唯一日志口
- [[api/DataReviewerPage]] —— 追溯页提示职责
- [[standards/CodeSimplification]] —— 注释/逻辑精简裁定（同为业主顶层裁定载体）
- [[rules/KR-008-Timestamp-Rule]] —— 日志时间戳 24 小时制

## 一次操作一次日志（2026-11-03 业主令）

> 触发案例：一次「重载保存」输出 6 条「焊接头配置加载完成」、同一 XML 备份两遍、末尾结论打两次。
> 业主口径：「一次重载保存的日志必须收敛」——整个操作 3~5 行，且**一条原因只出一条日志**。

| 规则 | 内容 |
|---|---|
| 唯一入口 | 仍只走 `GlobalCommData.ShowLog`；`msgLevel` 只控制颜色/级别，⛔ Debug 也会进界面日志，不能当「静默开关」用 |
| 同秒去重 | `ShowLog` 内 `IsDuplicateWithinSecond`：同一秒内 tag + 级别 + 文本完全一致只输出一次；不同文本、不同原因⛔不得合并 |
| 批量静默 | 上层批量回读/批量保存给下层传显式参数（如 `LoadConfig(false)`、`SaveConfig(backupFolder)`），由下层停掉自己的完成日志，结论由上层一次输出 |
| 一次一备份 | 一次写盘操作只允许调用一次 `ConfigBackupHelper.BackupFile`；各节导入必须复用上层已建目录（`SaveConfig(backupFolder)` 不再重复备份） |
| 操作日志骨架 | ①开始（目录/识别结论/跳过清单）②备份（每文件一行，不重复）③写入结果（一条结论含写入节 + 跳过节 + 备份路径）④回读校验（一条） |
