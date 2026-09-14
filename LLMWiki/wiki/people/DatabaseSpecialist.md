---
title: 数据库开发专员
date: 2026-09-14
tags: [专员, 数据库, SQLite]
source: raw/skills/AdaWeldsys_Skills/02-Development/DatabaseSpecialist.md
---

# 数据库开发专员

## 职责边界

- SQLite 数据库设计与操作
- 权限管理（用户/角色）
- 产品参数数据库
- 系统配置持久化
- 自动参数值管理（配合焊接工艺专员）

## 负责文件

```
SQLiteDBControl/
├── SQLiteCore/
│   └── SQLiteDataBase.cs          ← SQLite 数据库核心封装（CRUD）
├── ISQLiteHelper/
│   └── DatabaseHelperBase.cs      ← Helper 抽象基类
├── Helpers/
│   ├── AuthHelper.cs              ← 权限管理
│   ├── AutoParamHelper.cs         ← 自动参数数据库管理（JSON序列化）
│   │                                （含 WeldAutoParamProfile 数据结构）
│   ├── ConfigHelper.cs            ← 配置管理
│   └── ProductDatabaseHelper.cs   ← 产品数据库管理
└── SQLiteDatabaseManager.cs       ← 单例入口，聚合所有 Helper
```

## 技术要点

- System.Data.SQLite
- 数据库路径: `Application.StartupPath + @"\DataBase\"`
- Newtonsoft.Json 序列化参数字典到 SQLite
- `AutoParam.identityInfo` 作为数据库表名/配置标识
- 命名空间: `AdaWeldSystem.SQLiteDBControl`（子命名空间 `SQLiteCore` / `ISQLiteHelper` / `Helpers`，ADR-048）
- 对外唯一入口: `SQLiteDatabaseManager.Instance`

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| 焊接工艺专员 | `AutoParamHelper`, `ConfigHelper` |
| UI开发专员 | `AuthHelper`, `ConfigHelper` |

---

*来源：raw/skills/AdaWeldsys_Skills/02-Development/DatabaseSpecialist.md*
