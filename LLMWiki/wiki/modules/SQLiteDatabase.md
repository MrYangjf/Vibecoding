---
title: SQLiteDatabase 模块 — SQLite数据库
date: 2026-09-14
tags: [模块, 数据库, SQLite, 权限, 配置]
source: raw/skills/02-Development/DatabaseSpecialist.md
---

# SQLiteDatabase 模块 — SQLite数据库

> 负责 SQLite 数据库设计与操作：权限管理、产品参数、系统配置持久化、自动参数值管理。
> **模块位置**：`AdaWeldSystem/SQLiteDBControl/`
> **命名空间**：`AdaWeldSystem.SQLiteDBControl`（子命名空间 `SQLiteCore` / `ISQLiteHelper` / `Helpers`；2026-09-14 ADR-048 起随目录对齐）

## 目录结构

```
SQLiteDBControl/
├── SQLiteCore/
│   └── SQLiteDataBase.cs                ← SQLite 数据库核心封装（CRUD）
├── ISQLiteHelper/
│   └── DatabaseHelperBase.cs            ← Helper 抽象基类
├── Helpers/
│   ├── AuthHelper.cs                    ← 权限管理
│   ├── AutoParamHelper.cs               ← 自动参数数据库管理
│   │                                      （含 WeldAutoParamProfile 数据结构）
│   ├── ConfigHelper.cs                  ← 配置管理
│   └── ProductDatabaseHelper.cs         ← 产品数据库管理
└── SQLiteDatabaseManager.cs             ← 单例入口，聚合所有 Helper
```

## 核心文件

| 文件 | 职责 |
|------|------|
| SQLiteCore/SQLiteDataBase.cs | 封装 `System.Data.SQLite`，提供连接、CRUD、事务等底层能力 |
| ISQLiteHelper/DatabaseHelperBase.cs | Helper 抽象基类：`DataBase\` 路径管理 + 连接初始化 + IDisposable |
| Helpers/AuthHelper.cs | 权限管理（用户/角色验证） |
| Helpers/ConfigHelper.cs | 配置管理（系统配置持久化） |
| Helpers/AutoParamHelper.cs | 自动参数数据库管理（JSON 序列化）；同文件内定义 `WeldAutoParamProfile` 数据结构（焊缝宽度/送丝速度/激光功率/焊接速度 JSON） |
| Helpers/ProductDatabaseHelper.cs | 产品数据库管理（Product.db 按日期分表） |
| SQLiteDatabaseManager.cs | 单例入口，统一持有各 Helper；对外唯一访问口径 |

## 技术要点

- 库: System.Data.SQLite
- 数据库路径: `Application.StartupPath + @"\DataBase\"`
- 自动参数使用 Newtonsoft.Json 序列化参数字典到 SQLite
- 配置标识: 以 `AutoParam.identityInfo` 作为数据库表名/配置标识
- 目录: `AdaWeldSystem/SQLiteDBControl/`；命名空间: `AdaWeldSystem.SQLiteDBControl`（根） + `SQLiteCore` / `ISQLiteHelper` / `Helpers`

## 使用方式

外部代码统一通过 `SQLiteDatabaseManager.Instance` 访问各 Helper：

```csharp
var auth = SQLiteDatabaseManager.Instance.AuthHelper;
var config = SQLiteDatabaseManager.Instance.ConfigHelper;
var autoParam = SQLiteDatabaseManager.Instance.AutoParamHelper;
var product = SQLiteDatabaseManager.Instance.ProductDatabaseHelper;
```

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| [[modules/WeldParamControl]] | `SQLiteDatabaseManager.Instance.AutoParamHelper`、`ConfigHelper` |
| [[modules/UIDesign]] | `SQLiteDatabaseManager.Instance.AuthHelper`、`ConfigHelper` |
| [[modules/Comm]] | `SQLiteDatabaseManager.Instance.AuthHelper`（经 `GlobalCommData.mAuthHelper` 暴露） |

## 历史变更

- 2026-09-14：纠正命名 `SqlLiteDatabase` → `SQLiteDatabase`；按 "core + 抽象基类 + Helper + Manager" 范式重构；删除 `IDatabaseManager` 接口与冗余抽象；功能类统一改为 `*Helper`；新增 `SQLiteDatabaseManager` 作为对外唯一入口。
- 2026-09-14（同日二次调整）：目录固定为 `SQLiteDBControl/`（用户手动层级），抽象基类移入 `ISQLiteHelper/`；`WeldAutoParamProfile` 不再是独立文件，作为 `AutoParamHelper` 的数据结构辅助类并入 `Helpers/AutoParamHelper.cs`。

## 相关教训

- [[guides/Config-Data-Tools]] — AutoParamHelper 以 `identityInfo` 作为表名，必须避开 SQLite 保留关键字

---

*来源：raw/skills/02-Development/DatabaseSpecialist.md*
