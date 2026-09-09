---
title: FaultRecordManager API — 故障记录数据库管理器
date: 2026-08-31
tags: [API, 故障恢复, SQLite, 单例, 数据库, 已废弃]
status: deprecated
---

# FaultRecordManager API — 故障记录数据库管理器

> ⛔ **整页废弃（2026-09-04）**：FaultRecordManager 已随 FaultRecoveryManager **整体从代码中移除**（[[decisions/ADR-031-ErrorReportingHierarchy]] D3）。历史存档见下文。

> **位置**：`SqlLiteDatabase/FaultRecordManager.cs`，命名空间 `AdaWeldSystem.SqlLiteDatabase`（2026-08-31 新增，ADR-027）。
> FaultRecord 表的建表、插入与查询；继承 `DatabaseManagerBase`，数据库文件 `DataBase\FaultRecord.db`（首启自动建目录建表）。

## 定位

- **只负责持久化**，故障恢复闭环逻辑（记录→重试→复位）见 [[api/FaultRecoveryManager]]。
- **不依赖领域类型**：`FaultRecord`/`FaultCategory` 定义于 `ProductFileManager/FaultRecoveryManager.cs`（2026-09-01 自 `MainDeviceControl/DeviceWorkflow/` 迁入，ADR-027 §3），本类以字符串值数组为写入契约，保持 SqlLiteDatabase 层不反向依赖业务层。

## 公共接口

| 成员 | 说明 |
|---|---|
| `static FaultRecordManager Instance` | 单例（Lazy） |
| `bool InsertFaultRecord(string[] values)` | 写入一条故障记录；values 按 Columns 顺序：Time/Device/State/Category/ErrorCode/ParamSnapshot/AutoRecovered/RecoveryAction |
| `DataTable SelectFaultRecords()` | 查询全部故障记录（供回溯 UI 预留） |

表结构：`FaultRecord(Time, Device, State, Category, ErrorCode, ParamSnapshot, AutoRecovered, RecoveryAction)`，TEXT 长度 24/32/16/16/32/200/8/64。

## 使用范式

调用方（FaultRecoveryManager.Persist）负责 FaultRecord → string[] 映射与截断（Device/ErrorCode 32、ParamSnapshot 200、RecoveryAction 64），并对写入失败记 Warning 日志——SqlLiteDatabase 管理器内部不做 try/catch 日志（对齐 ProductDatabaseManager 范式）。

## ⚠️ 设备键名陷阱

注册 key 与记录 key 必须同源，见 [[lessons/FaultRecoveryDeviceKey]]。

## 相关

- [[api/FaultRecoveryManager]] · [[modules/SqlLiteDatabase]] · [[decisions/ADR-026-ProductLifecycleRecordModule]] · [[decisions/ADR-024-SafetyCheckConsolidation]]
