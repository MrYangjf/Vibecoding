---
title: "ADR-052 生产记录 Schema 扩展（20 字段 / 双写侧 / 旧记录逐列回落）"
date: 2026-10-08
updated: 2026-10-08
tags: [ADR, 记录, Schema, pDat, 向后兼容, ProductFileControl]
status: accepted
---

# ADR-052 生产记录 Schema 扩展

## 背景

第一次评审要求数据追溯能回看 **TA/LA 位置、振镜摆幅与图形、激光头温度**（原 `WeldActionRecord` 15 字段无这些）。

Phase 0 实测发现一个**既存缺陷**：`RecordFileStore.WriteActionToStream` 只写到 `JobId` 就结束，**`SeamPointY` / `SeamPointZ` 从未写入二进制侧** —— 只有 CSV 有。即「线激光特征点」在二进制记录里一直是恒 0，与 ADR-046/054 早期设计不符。

## 决策

### 一、字段按数据种类归属，**补全且不重复**

`WeldActionRecord` 15 → **20** 字段，按数据种类划分：

| 数据种类 | 字段 | 本轮动作 |
|---|---|---|
| 帧标识 | `FrameIndex` / `Timestamp` / `ActionType` | 保持 |
| 机器人位姿 | `RobotX` / `RobotY` / `RobotZ` | 保持 |
| 机器人运动 | `RobotSpeed` | 保持 |
| 送丝 | `FeedSpeed`（速度 m/min） | 保持 |
| 激光 | `LaserPower` | 保持 |
| 焊缝识别 | `WeldWidth`（宽度）/ `SeamPointY` / `SeamPointZ`（特征点坐标） | **二进制侧补齐**（既存缺失） |
| 线激光 Job | `JobId` | 保持 |
| **TA 送丝Z轴** | `TaPositionMm` | ➕ 新增 |
| **LA 对焦轴** | `LaPositionMm` | ➕ 新增 |
| **振镜** | `GalvoAmplitudeMm` / `GalvoPatternId` | ➕ 新增 |
| **激光头温度** | `HeadTempC` | ➕ 新增 |
| 调整动作 | `AdjustExecuted` / `AdjustData` | 保持 |

**不重复判据（正交性）**：

- `TaPositionMm`（位置 mm）≠ `FeedSpeed`（速率 m/min）—— 位置 vs 速率
- `LaPositionMm`（对焦轴 Z）≠ `RobotZ`（机器人 Z）—— 不同设备
- `GalvoAmplitudeMm`（摆动量）≠ `WeldWidth`（识别宽度）—— 施加量 vs 观测量

### 二、双写侧 + 版本回落

pDat 有 **两条写侧**（CSV 明文 `:SaveActionsToPDat` / 二进制 `:WriteActionToStream`）与**两条读侧**（`:ParsePDatRecords` / `:ReadActionFromStream`），**四点必须同批**：

| 侧 | 版本机制 | 回落方式 |
|---|---|---|
| 二进制 | `ActionFormatVersion` **3 → 4** | `if (version >= 4)` 读新字段，`< 4` 保持默认 0 |
| CSV | 列数判定 | `parts.Length >= 16..20` 逐列三元回落，缺列不抛 |

⛔ **漏读侧 ⇒ 旧 `.pDat` 整批解析失败**，因此版本判定必须在读侧最先做。

### 三、列名抽为常量

`RecordFileStore.ActionCsvHeader`（20 列）—— 写侧表头与文档共用同一份定义，避免两处手写漂移（对齐 `SeamTraceYRecord` 的既有范式）。

### 四、写入参数用可选参数扩展

`AddProcessRecord` 新增 5 个**可选参数**（默认 0.0），不改既有调用方签名；`WeldParamAdjustItem` 同步加 5 字段，`Persist` 透传。

## 备选方案

| 备选 | 放弃原因 |
|---|---|
| 只加 CSV 不加二进制 | 二进制是回溯主路径，缺列即数据丢失 |
| 升版本但**不补** `SeamPointY/Z` | 既存缺陷会被固化成「设计如此」，且与 CSV 侧矛盾 |
| 记录类拆成 4 个（按设备） | 过程帧是**同一时刻的横截面**，拆开反而破坏时间对齐；`WeldResultRecord` 已按产品级单独成类 |
| 加必填参数 | 破坏 `AddProcessRecord` 既有调用方，且 JobSwitch/Adjust 两条支路用不上 TA/LA |

## 后果

### 正面
- 旧 `.pDat` 照常可读（逐列 / 逐版本回落），无需迁移脚本
- 二进制侧不再丢特征点
- 字段归属有明确判据，后续再加字段不会重复造语义

### 负面
- 二进制单条记录增大 56 字节（4×double + 1×int + SeamPointY/Z 2×double）
- CSV 记录从 15 列变 20 列，**旧版 Excel 打开会多 5 列**（不影响解析）

## 相关页面

- [[api/ProductFileRecordManager]] —— 记录 API
- [[architecture/CodeMap]] —— 记录类落点
- [[decisions/ADR-042-SeamTrackingConsolidated]] —— 特征点来源（线激光）
- [[decisions/ADR-053-TaLaCurveAndMotorScale]] —— TA/LA 位置的数据源
- [[project/ReviewOptimization-P1-StructureDesign]] —— §3.1 记录 Schema 定稿
