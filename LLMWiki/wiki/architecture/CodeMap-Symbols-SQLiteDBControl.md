---
title: CodeMap-Symbols-SQLiteDBControl — 代码地图·符号签名层·SQLiteDBControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-SQLiteDBControl — SQLiteDBControl 的类型与签名

> **一句话**：模块 `SQLiteDBControl` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> SQLite 持久层
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.SQLiteDBControl.Helpers` | 4 | 5 | 数据库 · Helper（禁外部 new） | [[modules/SQLiteDatabase]] | ADR-033/043 |
| `AdaWeldSystem.SQLiteDBControl` | 1 | 1 | 数据库 · 核心 | [[modules/SQLiteDatabase]] | ADR-033 |
| `AdaWeldSystem.SQLiteDBControl.ISQLiteHelper` | 1 | 1 | 数据库 · 抽象契约（Helper 基类） | [[modules/SQLiteDatabase]] | ADR-033/006 |
| `AdaWeldSystem.SQLiteDBControl.SQLiteCore` | 1 | 1 | 数据库 · SQLite 封装 | [[modules/SQLiteDatabase]] | ADR-033 |

| 项 | 值 |
|---|---|
| 类型数 | 8 |
| 方法数 | 112 |

## 章节导航

- [AuthHelper](#AuthHelper)
- [AutoParamHelper](#AutoParamHelper)
- [ConfigHelper](#ConfigHelper)
- [DatabaseHelperBase](#DatabaseHelperBase)
- [ProductDatabaseHelper](#ProductDatabaseHelper)
- [SQLiteDataBase](#SQLiteDataBase)
- [SQLiteDatabaseManager](#SQLiteDatabaseManager)
- [WeldAutoParamProfile](#WeldAutoParamProfile)

## AuthHelper

- 签名：`public class AuthHelper : DatabaseHelperBase`
- 位置：`SQLiteDBControl/Helpers/AuthHelper.cs:11`
- 命名空间：`AdaWeldSystem.SQLiteDBControl.Helpers`
- 方法（10）：
  - `void InitializeUserTable()` — `SQLiteDBControl/Helpers/AuthHelper.cs:24`
  - `bool AddUser(string userName, string password, string userLevel)` — `SQLiteDBControl/Helpers/AuthHelper.cs:43`
  - `bool ValidateUser(string userName, string password)` — `SQLiteDBControl/Helpers/AuthHelper.cs:58`
  - `string GetUserLevel(string userName)` — `SQLiteDBControl/Helpers/AuthHelper.cs:79`
  - ` GetUserOperate(string userName)` — `SQLiteDBControl/Helpers/AuthHelper.cs:92`
  - `bool IsUserExist(string userName)` — `SQLiteDBControl/Helpers/AuthHelper.cs:111`
  - `bool UpdatePassword(string userName, string newPassword)` — `SQLiteDBControl/Helpers/AuthHelper.cs:125`
  - ` GetAllUsers()` — `SQLiteDBControl/Helpers/AuthHelper.cs:138`
  - `string GetUserLevelFromDb(string name)` — `SQLiteDBControl/Helpers/AuthHelper.cs:153`
  - `bool UpdateUserLevel(string name, string level)` — `SQLiteDBControl/Helpers/AuthHelper.cs:173`
- 构造（1）：
  - `AuthHelper()` — `SQLiteDBControl/Helpers/AuthHelper.cs:18`

## AutoParamHelper

- 签名：`public class AutoParamHelper : DatabaseHelperBase`
- 位置：`SQLiteDBControl/Helpers/AutoParamHelper.cs:8`
- 命名空间：`AdaWeldSystem.SQLiteDBControl.Helpers`
- 方法（18）：
  - `void CreateTableIfNotExist(string tableName)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:27`
  - `void EnsureGalvoAmplitudeColumn(string tableName)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:44`
  - `void EnsureSwingFrequencyColumn(string tableName)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:66`
  - `void EnsureSpotWidthColumn(string tableName)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:86`
  - `void GetSwingFrequencyColumnSafe()` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:107`
  - `void GetSwingWidthColumnSafe()` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:122`
  - `void GetSpotWidthColumnSafe()` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:137`
  - `void UpdateParamValues(WeldAutoParamProfile profile)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:150`
  - `bool IsTableExist(string tableName)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:170`
  - `void DeleteTable(string tableName)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:182`
  - `void SelectTable(string identityInfo)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:194`
  - ` LoadProfile(string identityInfo)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:218`
  - `void SaveProfile(string identityInfo, WeldAutoParamProfile profile)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:237`
  - `void UpdateProfile(string identityInfo, WeldAutoParamProfile profile)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:260`
  - `int GetRowCount(string tableName)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:291`
  - `void AddParamValues(string width, string feedSpeed, string laserPower, string robotSpeed, = null, = null, = null)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:311`
  - `string GetParamValue(string columnName)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:330`
  - `string GetParamValueSafe(string columnName)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:344`
- 构造（1）：
  - `AutoParamHelper()` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:20`
- 属性（1）：
  - `string CurrentTableName { get; set; }` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:17`

## ConfigHelper

- 签名：`public class ConfigHelper : DatabaseHelperBase`
- 位置：`SQLiteDBControl/Helpers/ConfigHelper.cs:8`
- 命名空间：`AdaWeldSystem.SQLiteDBControl.Helpers`
- 方法（10）：
  - `void InitializeConfigTable()` — `SQLiteDBControl/Helpers/ConfigHelper.cs:20`
  - `bool AddConfig(string configName, string configValue)` — `SQLiteDBControl/Helpers/ConfigHelper.cs:32`
  - `bool AddConfig(string identityInfo, string weldType, string wireType, string plateType, string createTime, string jsonString)` — `SQLiteDBControl/Helpers/ConfigHelper.cs:51`
  - `string GetConfigValue(string configName)` — `SQLiteDBControl/Helpers/ConfigHelper.cs:77`
  - `bool UpdateConfig(string configName, string configValue)` — `SQLiteDBControl/Helpers/ConfigHelper.cs:91`
  - `bool UpdateConfig(string identityInfo, string weldType, string wireType, string plateType, string jsonString)` — `SQLiteDBControl/Helpers/ConfigHelper.cs:110`
  - `bool IsConfigExist(string configName)` — `SQLiteDBControl/Helpers/ConfigHelper.cs:131`
  - `bool DeleteConfig(string configName)` — `SQLiteDBControl/Helpers/ConfigHelper.cs:144`
  - ` GetAllConfigs()` — `SQLiteDBControl/Helpers/ConfigHelper.cs:156`
  - `bool SaveConfig(string configName, string configValue)` — `SQLiteDBControl/Helpers/ConfigHelper.cs:165`
- 构造（1）：
  - `ConfigHelper()` — `SQLiteDBControl/Helpers/ConfigHelper.cs:14`

## DatabaseHelperBase

- 签名：`public abstract class DatabaseHelperBase : IDisposable`
- 位置：`SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs:9`
- 命名空间：`AdaWeldSystem.SQLiteDBControl.ISQLiteHelper`
- 方法（6）：
  - `void InitializeDatabasePath()` — `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs:36`
  - `void Dispose()` — `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs:47`
  - `void Dispose()` — `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs:48`
  - `void IsDatabaseFileExist()` — `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs:61`
  - `bool IsDatabaseFileExist()` — `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs:62`
  - `void BuildValues()` — `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs:69`
- 构造（1）：
  - `DatabaseHelperBase(string dbFileName)` — `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs:28`
- 属性（3）：
  - `SQLiteDataBase Database { get; set; }` — `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs:17`
  - `bool IsDisposed { get; set; }` — `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs:18`
  - `string DatabaseFilePath { get; set; }` — `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs:24`

## ProductDatabaseHelper

- 签名：`public class ProductDatabaseHelper : DatabaseHelperBase`
- 位置：`SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:9`
- 命名空间：`AdaWeldSystem.SQLiteDBControl.Helpers`
- 方法（13）：
  - `void EnsureTableSchema(string tableName)` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:34`
  - `void GetTableNameByDate(DateTime date)` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:66`
  - `void CreateEmptyProductTable()` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:72`
  - `void AppendRows(DataTable target, DataTable day)` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:85`
  - `void SelectTable(DateTime date)` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:103`
  - ` SelectTables(DateTime start, DateTime end)` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:116`
  - `void AddProductInfo(string sn, DateTime startTime, string status, string result, string info)` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:161`
  - `void EnsureTodayTableExists()` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:177`
  - ` GetProductDataByDate(DateTime date)` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:185`
  - ` GetTodayProductData()` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:193`
  - `void CleanOldData(int keepDays)` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:201`
  - `bool IsTableExist(DateTime date)` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:214`
  - `int GetRecordCount(DateTime date)` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:222`
- 构造（1）：
  - `ProductDatabaseHelper()` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:24`
- 属性（2）：
  - `string CurrentTableName { get; set; }` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:18`
  - `DataTable CurrentTable { get; set; }` — `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs:21`

## SQLiteDataBase

- 签名：`public class SQLiteDataBase`
- 位置：`SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:9`
- 命名空间：`AdaWeldSystem.SQLiteDBControl.SQLiteCore`
- 方法（26）：
  - `void Dispose()` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:32`
  - `void OnInitConnect()` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:60`
  - `void ExitConnect()` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:76`
  - `void ConnectDBFile(string dataBasePath)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:89`
  - `bool ExecuteSQL(string strSQL)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:98`
  - `bool ExecuteSQL(string strSQL, SQLiteParameter[] parameters)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:107`
  - ` GetDataSet(string strSQL)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:138`
  - ` GetDataSet(string strSQL, SQLiteParameter[] parameters)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:147`
  - `bool IsExistTable(string tableName)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:179`
  - `void DropDateTable(double n)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:209`
  - `bool IsExistFile(string strPathName)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:256`
  - `bool CreateTable(string strTableName, string[] tableColumn)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:265`
  - `bool CreateTable(string strTableName, string[] tableColumn, int[] columnLength)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:308`
  - `bool Insert(string tableName, string[] tableColumn, string[] values)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:348`
  - `bool Update(string tableName, string[] tableColumn, string[] values, string addressName, string value)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:382`
  - `bool Update(string tableName, string[] tableColumn, string[] values)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:414`
  - `void DropTable(string tableName)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:440`
  - ` GetDataTable(string sqlString)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:449`
  - ` GetDataRow(string sqlString)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:463`
  - `string GetDataString(string sqlString)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:477`
  - `string GetTableCellValue(string tableName, string columnName, string conditionColumn, string conditionValue)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:488`
  - `string GetTableColumnValue(string tableName, string columnName)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:502`
  - `bool HasTableValue(string tableName, string conditionColumn, string conditionValue)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:513`
  - `bool DeleteTableByCondition(string tableName, string conditionColumn, string conditionValue)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:530`
  - ` Select(string tableName)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:543`
  - `string GetDataString(string sqlString, SQLiteParameter[] parameters)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:553`
- 构造（2）：
  - `SQLiteDataBase()` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:19`
  - `SQLiteDataBase(string dataBasePath)` — `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs:25`

## SQLiteDatabaseManager

- 签名：`public class SQLiteDatabaseManager : IDisposable`
- 位置：`SQLiteDBControl/SQLiteDatabaseManager.cs:7`
- 命名空间：`AdaWeldSystem.SQLiteDBControl`
- 方法（1）：
  - `void Dispose()` — `SQLiteDBControl/SQLiteDatabaseManager.cs:39`
- 构造（1）：
  - `SQLiteDatabaseManager()` — `SQLiteDBControl/SQLiteDatabaseManager.cs:30`
- 属性（5）：
  - `SQLiteDatabaseManager Instance { get; set; }` — `SQLiteDBControl/SQLiteDatabaseManager.cs:15`
  - `AuthHelper AuthHelper { get; set; }` — `SQLiteDBControl/SQLiteDatabaseManager.cs:18`
  - `AutoParamHelper AutoParamHelper { get; set; }` — `SQLiteDBControl/SQLiteDatabaseManager.cs:21`
  - `ConfigHelper ConfigHelper { get; set; }` — `SQLiteDBControl/SQLiteDatabaseManager.cs:24`
  - `ProductDatabaseHelper ProductDatabaseHelper { get; set; }` — `SQLiteDBControl/SQLiteDatabaseManager.cs:27`

## WeldAutoParamProfile

- 签名：`public class WeldAutoParamProfile`
- 位置：`SQLiteDBControl/Helpers/AutoParamHelper.cs:358`
- 命名空间：`AdaWeldSystem.SQLiteDBControl.Helpers`
- 方法（1）：
  - `bool IsMeaningfulJson(string json)` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:399`
- 属性（8）：
  - `string SeamWidthJson { get; set; }` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:361`
  - `string FeedSpeedJson { get; set; }` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:364`
  - `string LaserPowerJson { get; set; }` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:367`
  - `string RobotSpeedJson { get; set; }` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:370`
  - `string SpotWidthJson { get; set; }` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:373`
  - `string SwingWidthJson { get; set; }` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:376`
  - `string SwingFrequencyJson { get; set; }` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:379`
  - `bool HasAnyValue { get; set; }` — `SQLiteDBControl/Helpers/AutoParamHelper.cs:382`

## 相关页面

- [[architecture/CodeMap]]
