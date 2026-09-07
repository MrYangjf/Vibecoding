---
title: SqlLiteDatabase 模块 — SQLite数据库
date: 2026-07-01
tags: [模块, 数据库, SQLite, 权限, 配置]
source: raw/skills/02-Development/DatabaseSpecialist.md
---

# SqlLiteDatabase 模块 — SQLite数据库

> 负责 SQLite 数据库设计与操作：权限管理、产品参数、系统配置持久化、自动参数值管理。
> **模块位置**：`AdaWeldSystem/SqlLiteDatabase/`

## 目录结构

```
SqlLiteDatabase/
├── SqliteCore/
│   ├── SQLiteDataBase.cs                ← 数据库基础操作（CRUD + 基类）
│   └── DatabaseManagerBase.cs           ← 数据库管理器基类
├── AuthManager.cs                       ← 权限管理
├── ConfigManager.cs                     ← 配置管理
├── AutoParamManager.cs                  ← 自动参数数据库管理
├── ProductDatabaseManager.cs            ← 产品数据库管理
└── FaultRecordManager.cs                ← 故障记录数据库管理（2026-08-31 新增，ADR-027；已移除 2026-09-04，ADR-032 D3）
```

## 核心文件

| 文件 | 职责 |
|------|------|
| SqliteCore/SQLiteDataBase.cs | 数据库基础操作（CRUD + 基类） |
| SqliteCore/DatabaseManagerBase.cs | 数据库管理器基类（`DataBase\` 路径管理 + 连接初始化 + IDisposable） |
| AuthManager.cs | 权限管理（用户/角色验证） |
| ConfigManager.cs | 配置管理（系统配置持久化） |
| AutoParamManager.cs | 自动参数数据库管理（JSON 序列化） |
| ProductDatabaseManager.cs | 产品数据库管理（Product.db 按日期分表） |
| FaultRecordManager.cs | 故障记录持久化（`DataBase\FaultRecord.db` 表 FaultRecord，详见 [[api/FaultRecordManager]]；2026-08-31 自 FaultRecoveryManager 内联实现下沉而来；已移除 2026-09-04，ADR-032 D3） |

## 技术要点

- 库: System.Data.SQLite
- 数据库路径: AppDomain.CurrentDirectory + @\DataBase\
- 支持 Entity Framework 6 (System.Data.SQLite.EF6)
- 自动参数使用 Newtonsoft.Json 序列化参数字典到 SQLite
- 配置标识: 以 AutoParam.identityInfo 作为数据库表名/配置标识

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| [[modules/WeldParamControl]] | AutoParamManager, ConfigManager |
| [[modules/UIDesign]] | AuthManager, ConfigManager |
| [[modules/ProductFileManager]] | **FaultRecordManager 的唯一调用方是 `FaultRecoveryManager`（2026-09-01 起驻本模块，ADR-027 §3）**；故障记录 DB 型数据归本模块，文件型记录（.pDat/.tmp）归 ProductFileManager 自身 |
| [[modules/Safety]] | 历史协作方；`FaultRecoveryManager` 已随 2026-09-01 归口迁出，安全检查侧仅作消费方 |

## 相关教训

- [[guides/Config-Data-Tools]] — AutoParamManager 以 `identityInfo` 作为表名，必须避开 SQLite 保留关键字

---

*来源：raw/skills/02-Development/DatabaseSpecialist.md*
