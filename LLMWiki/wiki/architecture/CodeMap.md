---
title: CodeMap — 代码地图总览（模块骨架 + 定位陷阱）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 索引, 架构, Phase0, 代码记忆]
status: accepted
---

# CodeMap — 代码地图总览

> **一句话**：一页看完代码骨架（模块 → 类 → 入口）+ 定位陷阱；⛔ 逐类签名见 [[architecture/CodeMap-Symbols-MotionControl]] 等分片，⛔ 依赖关系见 [[architecture/CodeMap-Relations]]。
> **使用纪律（强制）**：Phase 0 先读本页定位，**命中即直接读对应代码块**（Step 0.7），⛔ **不得一上来全项目 Grep**。详见 [[rules/KR-003-No-Skipping-Query]] 与 [[rules/KR-009-Grep-Default]]。
> **裁决顺序**：原档 > 架构页 > 源码注释；本表是导航层，不覆盖 ADR 结论。
> **生成方式**：模块骨架与计数由 `tools/codemap_build.py`（官方 `coderepomap` 引擎）产出；「定位陷阱」为人工经验判断，脚本原样保留。

## 章节导航

- [统计](#统计)
- [一、模块骨架](#一模块骨架)
- [二、模块 → 符号分片](#二模块--符号分片)
- [三、关系分片（影响面追踪）](#三关系分片影响面追踪)
- [四、易踩的定位陷阱](#四易踩的定位陷阱)
- [五、机器地图配套](#五机器地图配套)

## 统计

| 项 | 值 |
|---|---|
| 源码文件（`.cs`，不含 Designer） | 174 |
| 模块（顶层目录）数 | 15 |
| 类型数 | 298 |
| 方法数 | 4521 |
| 高置信调用边 | 637 |
| 低置信调用边 | 4378 |

> **图例**：`⛔` 死代码/无调用方 · `⚠️` 占位/待扩展 · `📄` 同文件多职责。
> **0 消费者 ≠ 死成员**：标注 ⛔ 时删除前仍须确认非横切载体（日志标签/序列化键/权限标识/DI 钩子）。

## 一、模块骨架

| 模块 | 分类 | 类型数 | 方法数 | 功能（人工标注） |
|---|---|---|---|---|
| `MotionControl` | Motion | 55 | 882 | 运控：Y / TA 两轴 + 焊接头从站 OD（0x7000 / 0x6020 / 0x7010） |
| `UIDesign` | UI | 55 | 870 | UI 页面与权限：主界面 / 工艺 / 系统设置 / 追溯 |
| `EmguALG` | Vision | 36 | 272 | 视觉算法五层：EmguALG.Core / RealtimeMonitor / LineLaserContour |
| `Comm` | Core | 36 | 274 | 通讯：RSI 唯一机器人通道 + 日志双通道 |
| `MainDeviceControl` | Core | 25 | 751 | 整机编排：设备初始化 / 状态机 / 五个模组 workflow |
| `WeldParamControl` | Other | 24 | 436 | 焊接工艺参数与自适应：焊参真相源 + 算法规格 |
| `LineLaserCam` | Motion | 17 | 232 | 线激光相机：Manager 唯一口 + 英莱/虚拟实现 |
| `ProductFileControl` | Data | 14 | 203 | 产品记录与追溯 Schema |
| `SQLiteDBControl` | Data | 8 | 112 | SQLite 持久层 |
| `PCLOperate` | Data | 8 | 128 | PLC 交互 |
| `FileOperate` | Core | 6 | 92 | 配置读写：INI + XML + 自愈 + 迁移 + 备份 |
| `MonitorCam` | Vision | 6 | 108 | 监控相机：Manager 唯一口 + 海康/虚拟实现 |
| `ConfigFileControl` | Other | 5 | 50 | — |
| `Properties` | Other | 2 | 0 | — |
| `Program.cs` | Other | 1 | 2 | 程序入口（Main） |

## 二、模块 → 符号分片

> **怎么用**：先按模块收敛 → 打开该模块分片 → 按类型名找到 `文件:行` → 直接跳读代码块（Step 0.7）。

| 模块 | 符号分片页 | 类型数 |
|---|---|---|
| `MotionControl` | [[architecture/CodeMap-Symbols-MotionControl]] | 55 |
| `UIDesign` | [[architecture/CodeMap-Symbols-UIDesign]] | 55 |
| `EmguALG` | [[architecture/CodeMap-Symbols-EmguALG]] | 36 |
| `Comm` | [[architecture/CodeMap-Symbols-Comm]] | 36 |
| `MainDeviceControl` | [[architecture/CodeMap-Symbols-MainDeviceControl]] | 25 |
| `WeldParamControl` | [[architecture/CodeMap-Symbols-WeldParamControl]] | 24 |
| `LineLaserCam` | [[architecture/CodeMap-Symbols-LineLaserCam]] | 17 |
| `ProductFileControl` | [[architecture/CodeMap-Symbols-ProductFileControl]] | 14 |
| `SQLiteDBControl` | [[architecture/CodeMap-Symbols-SQLiteDBControl]] | 8 |
| `PCLOperate` | [[architecture/CodeMap-Symbols-PCLOperate]] | 8 |
| `FileOperate` | [[architecture/CodeMap-Symbols-FileOperate]] | 6 |
| `MonitorCam` | [[architecture/CodeMap-Symbols-MonitorCam]] | 6 |
| `ConfigFileControl`、`Program.cs`、`Properties` | [[architecture/CodeMap-Symbols-Thin]] | 8 |

## 三、关系分片（影响面追踪）

> **怎么用**：改某类型 / 方法前 → 查关系分片拿**候选调用方文件** → 再用 Grep 确认（Step 2.5）。
> ⛔ 关系分片是**候选集生成器**不是判决：类型级边高置信，方法级边可能同名误连 ⇒ Grep 定论。

| 分片 | 内容 |
|---|---|
| [[architecture/CodeMap-Relations]] | 被引用**类型** → 调用方文件（高置信）+ 继承/实现边 |
| [[architecture/CodeMap-Relations-Methods-Comm]] | 调用方在 `Comm` 的被调**方法** → 调用点（低置信） |
| [[architecture/CodeMap-Relations-Methods-EmguALG]] | 调用方在 `EmguALG` 的被调**方法** → 调用点（低置信） |
| [[architecture/CodeMap-Relations-Methods-FileOperate]] | 调用方在 `FileOperate` 的被调**方法** → 调用点（低置信） |
| [[architecture/CodeMap-Relations-Methods-LineLaserCam]] | 调用方在 `LineLaserCam` 的被调**方法** → 调用点（低置信） |
| [[architecture/CodeMap-Relations-Methods-MainDeviceControl-2]] | 调用方在 `MainDeviceControl` 的被调**方法** → 调用点（低置信 · 名首字母 N-Z） |
| [[architecture/CodeMap-Relations-Methods-MainDeviceControl]] | 调用方在 `MainDeviceControl` 的被调**方法** → 调用点（低置信） |
| [[architecture/CodeMap-Relations-Methods-MotionControl-2]] | 调用方在 `MotionControl` 的被调**方法** → 调用点（低置信 · 名首字母 N-Z） |
| [[architecture/CodeMap-Relations-Methods-MotionControl]] | 调用方在 `MotionControl` 的被调**方法** → 调用点（低置信） |
| [[architecture/CodeMap-Relations-Methods-PCLOperate]] | 调用方在 `PCLOperate` 的被调**方法** → 调用点（低置信） |
| [[architecture/CodeMap-Relations-Methods-ProductFileControl]] | 调用方在 `ProductFileControl` 的被调**方法** → 调用点（低置信） |
| [[architecture/CodeMap-Relations-Methods-SQLiteDBControl]] | 调用方在 `SQLiteDBControl` 的被调**方法** → 调用点（低置信） |
| [[architecture/CodeMap-Relations-Methods-Thin]] | 调用方在 薄模块合并页 的被调**方法** → 调用点（低置信） |
| [[architecture/CodeMap-Relations-Methods-UIDesign-2]] | 调用方在 `UIDesign` 的被调**方法** → 调用点（低置信 · 名首字母 N-Z） |
| [[architecture/CodeMap-Relations-Methods-UIDesign]] | 调用方在 `UIDesign` 的被调**方法** → 调用点（低置信） |
| [[architecture/CodeMap-Relations-Methods-WeldParamControl]] | 调用方在 `WeldParamControl` 的被调**方法** → 调用点（低置信） |

## 四、易踩的定位陷阱

| 错误判断 | 实际 | 教训 |
|---|---|---|
| `LineLaserSeamResult` Grep 零命中 ≠ 缺失 | 它是 `struct`（`LineLaserCam/ILineLaser/LineLaserEventArgs.cs`） | Grep `class\s+X` 漏 struct；先分 class / struct / interface |
| `MontionConfigForm` 不存在 | 轴配置 UI 是 `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs`（UserControl） | 找 UI 扫 `UIDesign/` 全部子目录 |
| 「光丝对中未实现」是误判 | 有两套：在用套出像素、另一套出 mm 无消费者 | 区分「无代码」与「有代码未接线」 |
| workflow 的 UI 在 `MainDeviceControl` 是误判 | 业务在 `MainDeviceControl/DeviceWorkflow/`，UI 在 `UIDesign/TabPage/` | 业务逻辑与 UI 分目录 |
| 振镜走运控轴是误判 | 振镜走从站 OD（0x7010），ADR-030 已裁定 | 硬件归属先查 ADR |
| `MotorState?` 违反 ADR-001 是误判 | `MotorState` 是 struct，`?` = Nullable，C# 7.3 合法 | 判可空前先分 class / struct |
| `ProductFileControl/Records/*` 命名空间违规是误判 | ADR-005 §3 例外二：该目录扁平 | 查命名空间先读 ADR-005 例外表 |
| UI 直调 `MoveTo`/`HomeAxis` 违规是误判 | `MontionManager.Instance.MoveTo` 等正是规定路径 | 区分 `axis.AbsMove()` 与 Manager 门面 |

## 五、机器地图配套

- 符号分片 —— 每模块一页（`CodeMap-Symbols-<模块>.md`），逐类 → `文件:行` → 成员签名。
- 关系分片 —— 类型级 / 方法级影响面清单（见上表）。
- 生成器：`tools/codemap_build.py`；引擎 = 官方 `coderepomap`（tree-sitter C# 解析 + PageRank）。
- 刷新：`python tools/codemap_build.py`；同步校验：`python tools/codemap_build.py --check`（非零退出 = 地图已过期）。
- ⛔ 本页骨架与计数随源码自动刷新；⛔ 「定位陷阱」为人工判断，改码后**不随脚本覆盖**。

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/DeviceControlArchitecture]]
- [[project/vibecoding-workflow]]
- [[rules/KR-003-No-Skipping-Query]] · [[rules/KR-009-Grep-Default]]
