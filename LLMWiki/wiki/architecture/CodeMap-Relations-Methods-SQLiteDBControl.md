---
title: CodeMap-Relations-Methods-SQLiteDBControl — 代码地图·方法级影响面·SQLiteDBControl（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-SQLiteDBControl — 方法级影响面（低置信 · 调用方在 SQLiteDBControl）

> **一句话**：**调用方位于 `SQLiteDBControl` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 36 |
| 调用点数 | 39 |

## 章节导航

- [AddConfig](#AddConfig)
- [AddParamValues](#AddParamValues)
- [AddUser](#AddUser)
- [AppendRows](#AppendRows)
- [BuildValues](#BuildValues)
- [CreateEmptyProductTable](#CreateEmptyProductTable)
- [CreateTableIfNotExist](#CreateTableIfNotExist)
- [EnsureGalvoAmplitudeColumn](#EnsureGalvoAmplitudeColumn)
- [EnsureSpotWidthColumn](#EnsureSpotWidthColumn)
- [EnsureSwingFrequencyColumn](#EnsureSwingFrequencyColumn)
- [EnsureTableSchema](#EnsureTableSchema)
- [EnsureTodayTableExists](#EnsureTodayTableExists)
- [ExecuteSQL](#ExecuteSQL)
- [ExitConnect](#ExitConnect)
- [GetDataSet](#GetDataSet)
- [GetDataString](#GetDataString)
- [GetDataTable](#GetDataTable)
- [GetParamValue](#GetParamValue)
- [GetProductDataByDate](#GetProductDataByDate)
- [GetRowCount](#GetRowCount)
- [GetSpotWidthColumnSafe](#GetSpotWidthColumnSafe)
- [GetSwingFrequencyColumnSafe](#GetSwingFrequencyColumnSafe)
- [GetSwingWidthColumnSafe](#GetSwingWidthColumnSafe)
- [GetTableNameByDate](#GetTableNameByDate)
- [GetUserLevel](#GetUserLevel)
- [InitializeConfigTable](#InitializeConfigTable)
- [InitializeDatabasePath](#InitializeDatabasePath)
- [InitializeUserTable](#InitializeUserTable)
- [IsConfigExist](#IsConfigExist)
- [IsExistTable](#IsExistTable)
- [IsMeaningfulJson](#IsMeaningfulJson)
- [IsUserExist](#IsUserExist)
- [OnInitConnect](#OnInitConnect)
- [SelectTable](#SelectTable)
- [UpdateConfig](#UpdateConfig)
- [UpdateParamValues](#UpdateParamValues)

## BuildValues

> 4 处调用 / 4 个调用方文件

- `SQLiteDBControl/Helpers/AuthHelper.cs` — 行 [50]
- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [314]
- `SQLiteDBControl/Helpers/ConfigHelper.cs` — 行 [39]
- `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs` — 行 [165]

## AddConfig

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/ConfigHelper.cs` — 行 [178]

## AddParamValues

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [275, 247]

## AddUser

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AuthHelper.cs` — 行 [31, 30]

## AppendRows

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs` — 行 [139]

## CreateEmptyProductTable

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs` — 行 [125]

## CreateTableIfNotExist

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [205]

## EnsureGalvoAmplitudeColumn

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [210, 36]

## EnsureSpotWidthColumn

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [209, 35]

## EnsureSwingFrequencyColumn

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [211, 37]

## EnsureTableSchema

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs` — 行 [179, 28]

## EnsureTodayTableExists

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs` — 行 [195, 163]

## ExecuteSQL

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs` — 行 [537, 443, 435, 406, 372, 100]

## ExitConnect

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs` — 行 [338, 298, 248, 202, 170, 130]

## GetDataSet

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs` — 行 [555, 520, 465, 451, 140]

## GetDataString

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs` — 行 [505, 495, 479]

## GetDataTable

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs` — 行 [546]

## GetParamValue

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [348]

## GetProductDataByDate

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs` — 行 [224]

## GetRowCount

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [272]

## GetSpotWidthColumnSafe

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [228]

## GetSwingFrequencyColumnSafe

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [230]

## GetSwingWidthColumnSafe

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [229]

## GetTableNameByDate

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs` — 行 [216, 196, 187, 179, 173, 130, 105, 27]

## GetUserLevel

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AuthHelper.cs` — 行 [99]

## InitializeConfigTable

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/ConfigHelper.cs` — 行 [16]

## InitializeDatabasePath

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs` — 行 [31]

## InitializeUserTable

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AuthHelper.cs` — 行 [20]

## IsConfigExist

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/ConfigHelper.cs` — 行 [172]

## IsExistTable

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs` — 行 [276]

## IsMeaningfulJson

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [392, 391, 390, 389, 388, 387, 386]

## IsUserExist

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AuthHelper.cs` — 行 [175, 155]

## OnInitConnect

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs` — 行 [324, 283, 152, 111]

## SelectTable

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [271, 244, 220]

## UpdateConfig

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/ConfigHelper.cs` — 行 [174]

## UpdateParamValues

> 1 处调用 / 1 个调用方文件

- `SQLiteDBControl/Helpers/AutoParamHelper.cs` — 行 [285]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
