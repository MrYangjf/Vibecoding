---
title: 数据库开发专员
date: 2026-07-01
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

SqlLiteDatabase/
├── SQLiteDataBase.cs          ← 数据库基础操作（CRUD）
├── AuthManage.cs              ← 权限管理
├── ConfigManage.cs            ← 配置管理
├── AutoParamManager.cs        ← 自动参数数据库管理（JSON序列化）
├── ProductDatabaseManage.cs   ← 产品数据库管理
└── ConfigManager.cs           ← 焊接工艺配置管理

## 技术要点

- System.Data.SQLite
- 数据库路径: AppDomain.CurrentDirectory + @\DataBase\
- Entity Framework 6 (System.Data.SQLite.EF6)
- Newtonsoft.Json 序列化参数字典到 SQLite
- AutoParam.identityInfo 作为数据库表名/配置标识

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| 焊接工艺专员 | AutoParamManager, ConfigManager |
| UI开发专员 | AuthManage, ConfigManage |

---

*来源：raw/skills/AdaWeldsys_Skills/02-Development/DatabaseSpecialist.md*
