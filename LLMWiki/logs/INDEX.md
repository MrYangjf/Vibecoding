---
title: Log Index — 日志与历史归档索引
date: 2026-11-02
updated: 2026-11-02
tags: [索引, 日志, 历史, 归档]
status: active
---

# Log Index — 日志与历史归档索引

> **本文件由 `python tools/wiki_log_tidy.py index` 生成，⛔ 禁手工编辑。**
> **链路**：`logs/log.md`（当轮明细，上限 50 条）→ `logs/backup/log_YYYY-MM-DD.md`（跨轮归档）→ 本索引（可路由）→ `LLMWiki_backup_*.tar.gz`（整库快照）。
> **纪律**：截断是**归档不是丢弃**；⛔ 任何直接删除旧条目的做法都会断掉历史链路。

---

## 一、当轮日志（logs/log.md）

| 项 | 值 |
|---|---|
| 文件 | `logs/log.md` |
| 条目数 | 50（上限 50） |
| 最新条目 | fix | 工具与全量资产纳入 git 管控（Vicoding 4 提交 + AdaWeldSystem 2 提交，双仓库未跟踪清零） |

---

## 二、跨轮归档（logs/backup/）

| 日期 | 条目数 | 首条摘要 | 归档文件 |
|---|---|---|---|
| 2026-11-11 | 1 | refactor ／ 全库零 as 下转型 + 存量三类判据治理；机器人X获取路径调研 | `logs/backup/log_2026-11-11.md` |
| 2026-11-10 | 15 | fix ／ MainPage 业主界面改版落地 | `logs/backup/log_2026-11-10.md` |
| 2026-11-09 | 25 | 修复/精简 ／ TA_ZeroPose 手动重试闭环 + 失败上色 + 单飞逾期释放 + Batch B 等价精简 | `logs/backup/log_2026-11-09.md` |
| 2026-11-08 | 2 | 开发/优化 ／ 流程等待分区补全 + 设备侧等待五项 + 手动轴操作下沉 Workflow | `logs/backup/log_2026-11-08.md` |
| 2026-11-06 | 15 | fix ／ TA_Retract 收敛为 Auto 反向纯力矩保持（现场否证位置终点判据） | `logs/backup/log_2026-11-06.md` |
| 2026-11-05 | 13 | coding ／ TA 初始化四步对齐 + TA_ZeroPose 工作零位（非回零）落地 | `logs/backup/log_2026-11-05.md` |
| 2026-11-04 | 13 | 编码 ／ 台达扭矩回零 -3 经 CoE 下发 + P1.087/P1.088 写读校验 | `logs/backup/log_2026-11-04.md` |
| 2026-11-03 | 22 | fix ／ 台达从站源=ESI，EtherCAT协议.xlsx 为唯一权威源（ADR-079 收口） | `logs/backup/log_2026-11-03.md` |
| 2026-11-02 | 18 | governance ／ 复查轮：修复 index 专员职责缺失与路由章节丢失 + Key Rules 下沉为 wiki/rules（KR- | `logs/backup/log_2026-11-02.md` |
| 2026-10-30 | 10 | fix ／ RSI 重复定义事故修复（重放幂等 + 唯一性判据 J37/J38） | `logs/backup/log_2026-10-30.md` |
| 2026-10-29 | 6 | coding ／ 精简欠账清零：成员顺序 13→0（含判据三处假阳性修正） | `logs/backup/log_2026-10-29.md` |
| 2026-10-27 | 1 | coding ／ 精简检测补全：函数块逻辑已覆盖，新增多层锁判据（0 处） | `logs/backup/log_2026-10-27.md` |
| 2026-10-26 | 11 | coding ／ 激光头页自动刷新分区门控 + LA 四键一行 + 使能类控件 Switch→按钮（ADR-093） | `logs/backup/log_2026-10-26.md` |
| 2026-10-23 | 48 | governance ／ lessons 检索机制四件套：计数漂移修复 + wiki_audit 第 11 项闸门 + 路由全覆盖 + 三处 | `logs/backup/log_2026-10-23.md` |
| 2026-10-22 | 9 | coding ／ 主界面移除监控相机预览（删除 imageBoxCam + panelCam，行 0 重排） | `logs/backup/log_2026-10-22.md` |
| 2026-10-21 | 12 | fix ／ 主界面 plot2 上下限参考线改为焊接开启后绘制 + 消除初始化期图例叠加（4 条重复 txt 记录） | `logs/backup/log_2026-10-21.md` |
| 2026-10-20 | 10 | coding ／ 摆幅频率链路落地 + 旧摆幅通道（k / WeaveWidthTable）删除 | `logs/backup/log_2026-10-20.md` |
| 2026-10-19 | 4 | coding ／ 第九轮（第八轮返工）：D1-D5 缺陷修复 + MainPage UI 计时器两表合一 | `logs/backup/log_2026-10-19.md` |
| 2026-10-16 | 192 | refactor+ingest ／ 编码错误教训迁出 SKILL 入 LLMWiki（新建判据库页，Step 2.6 段瘦身 87%） | `logs/backup/log_2026-10-16.md` |
| 2026-10-15 | 4 | coding ／ 批L 二轮：系统设置三子页全链补齐（页级Grid→卡片Panel→区内Grid→控件）+ 自适应页数据回溯式左右分栏（AD | `logs/backup/log_2026-10-15.md` |
| 2026-10-14 | 2 | coding ／ 批K 三轮：60/40 行高 + 每行四列 + 振镜块迁入 gridLaserZones 第 4 格（ADR-084 §三 | `logs/backup/log_2026-10-14.md` |
| 2026-09-16 | 132 | coding ／ 启动日志 8 项问题修复：状态机语义 + 初始化时序 + 报错分层（ADR-021/038） | `logs/backup/log_2026-09-16.md` |

> **查法**：先在本表定位日期 → 再读对应归档文件；⛔ 不要凭记忆断言「上次是怎么处理的」。

## 相关页面

- [[project/vibecoding-workflow]] —— Phase 0~4 流程规范
- [[standards/WikiPageFormatSpec]] —— 页面格式契约（§2.5 log 条目契约）
