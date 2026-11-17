---
title: SQLiteDatabaseManager API 参考（SQLite 数据库管理器 · 模块唯一入口）
date: 2026-09-17
tags: [API, 数据库, SQLite, 管理器, 单例, 唯一入口, ADR-005, ADR-001]
source: AdaWeldSystem/SQLiteDBControl/SQLiteDatabaseManager.cs
---

# SQLiteDatabaseManager API 参考

> SQLiteDBControl 模块**唯一对外访问口径**（单例）：统一持有各功能 Helper，管理全部 SQLite 落库能力。
> **位置**：`AdaWeldSystem/SQLiteDBControl/SQLiteDatabaseManager.cs`
> **命名空间**：`AdaWeldSystem.SQLiteDBControl`
> **沿革**：2026-09-14 由 SqliteDatabase 重构为 SQLiteDBControl（命名空间随目录，[[decisions/ADR-005-NamespaceDirectoryAlignment]]）；WeldAutoParamProfile 已并入 AutoParamHelper。
> 模块背景见 [[modules/SQLiteDatabase]]。

---

## 定位

```
外部（登录 / 自动参数 / 产品记录 / 配置页）
  ↓ 只认 SQLiteDatabaseManager.Instance
SQLiteDatabaseManager（Helper 持有者，Lazy<T> 单例）
  ├─ AuthHelper            （Auth.db          权限：用户校验 / 级别 / 改密）
  ├─ AutoParamHelper       （AutoParamValue.db 自动参数分段数据表 + WeldAutoParamProfile）
  ├─ ConfigHelper          （Config.db        配置：自动参数配置 JSON 等）
  └─ ProductDatabaseHelper （Product.db       产品生产记录：按日期建表 / 列契约 SN·Time·Status·Result·Info / 增查 / 清旧）
       ↑ 全部继承 DatabaseHelperBase（ISQLiteHelper/ 抽象基类）
            └─ 持有 SQLiteDataBase（SQLiteCore/ ，连接与执行）
```

- **单例**（`Lazy<T>`，线程安全），私有构造函数内创建全部 4 个 Helper；实现标准 `IDisposable.Dispose()`（ADR-001）依次释放。
- **Helper 体系**：`DatabaseHelperBase`（抽象基类，`ISQLiteHelper/DatabaseHelperBase.cs`）负责数据库文件路径管理（`<启动目录>\DataBase\<文件名>`，目录不存在自动创建）、连接初始化与通用辅助；各 `*Helper`（`Helpers/`）只写业务 SQL。
- ⛔ **禁止外部 new Helper**：Helper 归 Manager 构造独占持有，外部一律经 `Instance.<XxxHelper>` 访问。
- `WeldAutoParamProfile`（分段数据表 JSON 载体：SeamWidthJson / FeedSpeedJson / LaserPowerJson / RobotSpeedJson，含 `HasAnyValue` 判定）已并入 AutoParamHelper 同文件，经 `LoadProfile` / `SaveProfile` / `UpdateProfile` 读写。

## 公共成员

| 成员 | 类型 | 职责 | 备注 |
|---|---|---|---|
| `Instance` | `static SQLiteDatabaseManager { get; }` | 全局唯一实例 | `Lazy<T>` 线程安全 |
| `AuthHelper` | `AuthHelper { get; }` | 权限库（`AuthHelper() : base("Auth.db")`） | AddUser / ValidateUser / GetUserLevel / UpdatePassword 等 |
| `AutoParamHelper` | `AutoParamHelper { get; }` | 自动参数值库（`AutoParamValue.db`）——**分段参数表 5 列：焊缝宽度/送丝速度/激光功率/焊接速度/光斑宽度**（第 5 列 2026-09-23 ADR-043 新增，旧表经 `EnsureSpotWidthColumn` ALTER 自动迁移，旧行空值由读取侧公式兜底） | SelectTable / AddParamValues / GetParamValue / LoadProfile / SaveProfile / UpdateProfile |
| `ConfigHelper` | `ConfigHelper { get; }` | 配置库（`Config.db`） | AddConfig / GetConfigValue / UpdateConfig / GetAllConfigs 等 |
| `ProductDatabaseHelper` | `ProductDatabaseHelper { get; }` | 产品生产记录库（`Product.db`，按日期分表 `TyyyyMMdd`） | `SelectTable(DateTime)`（回溯端一次性读取）/ `AddProductInfo(sn, startTime, status, result, info)` / `EnsureTodayTableExists` / `EnsureTableSchema`（当天表列集不符即重建）/ `CurrentTable` / `CurrentTableName` / `GetProductDataByDate` / `GetRecordCount` / `IsTableExist` / `CleanOldData`（[[decisions/ADR-037-ProductProductionRecordLifecycle]] 决 1） |
| `Dispose` | `void ()` | 释放全部 Helper | 标准 IDisposable（ADR-001），重复调用安全 |

## 目录结构

```
SQLiteDBControl/
├── SQLiteDatabaseManager.cs     # 唯一入口（本页）
├── SQLiteCore/SQLiteDataBase.cs # 连接与 SQL 执行（Helper 内部使用）
├── ISQLiteHelper/DatabaseHelperBase.cs  # Helper 抽象基类（路径管理 + 连接初始化）
└── Helpers/                     # 业务 Helper（禁外部 new）
    ├── AuthHelper.cs / AutoParamHelper.cs（含 WeldAutoParamProfile）/ ConfigHelper.cs / ProductDatabaseHelper.cs
```

## 相关页面

- [[modules/SQLiteDatabase]] — 模块说明
- [[api/WeldParamManager]] — 消费方（ConfigHelper / AutoParamHelper 用于自动参数）
- [[api/ProductFileRecordManager]] — 消费方（WeldResultRecord 落产品库）
- [[decisions/ADR-005-NamespaceDirectoryAlignment]] — 目录即命名空间（SqliteDatabase → SQLiteDBControl）
- [[decisions/ADR-002-DisposePatternFullCoverage]] — Dispose 规约
- [[decisions/ADR-006-ModuleOrganizationPatternStandard]] — 模块组织范式（唯一入口 + 实现类非单例）
