---
title: 配置与数据工具使用指南
date: 2026-08-18
tags: [指导, 工具, 配置, 数据库, 汇总]
---

# 配置与数据工具使用指南

> **位置说明（2026-09-01）**：本页自 `wiki/lessons/` 迁入 `wiki/guides/`。
> 分类判据：**`guides/` = 「怎么做」的操作型指导与参考手册**；`lessons/` = 「踩过什么坑」的教训门禁；`standards/` = 「必须遵守」的强制规范。
> 页面内的历史 lessons 链接已同步更新为 guides 路径。


> 本文档汇总了项目中常用配置与数据工具的正确用法与常见踩坑点，涵盖 INI 配置文件读写、SQLite 数据库命名规范、EmguCV 图像 API 误用等内容，供开发人员快速查阅。

---

## 1. INIFile 使用规范

### 1.1 基本信息

项目中使用 `INIFile` 类进行 INI 配置文件的读写操作。

| 项 | 值 |
|----|-----|
| 命名空间 | `AdaWeldSystem.FileOperate` |
| 类名 | `INIFile`（三个字母全部大写） |
| 程序集 | `AdaWeldSystem` |
| 文件位置 | `FileOperate/INIFile.cs` |

### 1.2 构造函数

```csharp
using AdaWeldSystem.FileOperate;

// 创建 INIFile 实例，指定文件路径
// filePath: INI 文件的完整路径
INIFile ini = new INIFile(filePath);
```

- 构造函数仅记录文件路径，不立即读取文件内容
- 文件不存在时，读取方法返回默认值，写入方法自动创建文件
- 支持绝对路径和相对路径（相对于程序运行目录）

### 1.3 读取方法

#### ReadString — 读取字符串

```csharp
// section: 节名
// key: 键名
// defaultValue: 默认值（键不存在时返回）
string value = ini.ReadString(string section, string key, string defaultValue);
```

#### ReadInt — 读取整数

```csharp
int value = ini.ReadInt(string section, string key, int defaultValue);
```

#### ReadDouble — 读取浮点数

```csharp
double value = ini.ReadDouble(string section, string key, double defaultValue);
```

#### ReadBool — 读取布尔值

```csharp
bool value = ini.ReadBool(string section, string key, bool defaultValue);
```

- 支持的布尔值表示：`true/false`、`1/0`、`True/False`、`TRUE/FALSE`
- 无法解析时返回 `defaultValue`

### 1.4 写入方法

#### WriteString — 写入字符串

```csharp
ini.WriteString(string section, string key, string value);
```

#### WriteInt — 写入整数

```csharp
ini.WriteInt(string section, string key, int value);
```

#### WriteDouble — 写入浮点数

```csharp
ini.WriteDouble(string section, string key, double value);
```

#### WriteBool — 写入布尔值

```csharp
ini.WriteBool(string section, string key, bool value);
```

- 写入操作仅修改内存缓存，**不立即写入磁盘**
- 键已存在则覆盖，不存在则新增
- 节不存在则自动创建

### 1.5 SaveToFile — 保存到文件

```csharp
// 将内存中的修改写入磁盘文件
ini.SaveToFile();
```

- **重要**：调用写入方法后，必须调用 `SaveToFile()` 才能将修改持久化到磁盘
- 多次写入后只需调用一次 `SaveToFile()`，减少 IO 操作
- 写入失败时抛出异常（如文件只读、磁盘空间不足）

### 1.6 完整示例

```csharp
using AdaWeldSystem.FileOperate;

// 1. 创建实例
string configPath = @"Config\INI\MyApp.ini";
INIFile ini = new INIFile(configPath);

// 2. 读取配置
string serverIp = ini.ReadString("Connection", "ServerIP", "127.0.0.1");
int port = ini.ReadInt("Connection", "Port", 8080);
double timeout = ini.ReadDouble("Connection", "Timeout", 30.0);
bool enableLog = ini.ReadBool("Logging", "Enable", true);

// 3. 修改配置
ini.WriteString("Connection", "ServerIP", "192.168.1.100");
ini.WriteInt("Connection", "Port", 9090);
ini.WriteBool("Logging", "Enable", false);

// 4. 保存到文件
ini.SaveToFile();
```

### 1.7 注意事项

#### 类名拼写：INIFile（全大写）

**错误现象**：编译报 `CS0246: 找不到类型名"IniFile"`。

**原因分析**：类名拼写为小写 `IniFile`，与实际类名 `INIFile`（三个大写字母）不符。

**修复方案**：使用大写 `INIFile`。

```csharp
// 错误：类名应为 INIFile（三个大写字母）
IniFile ini = new IniFile(path);  // CS0246

// 正确：INI 三个字母全部大写
INIFile ini = new INIFile(path);
```

> 项目中所有 INI 相关命名均使用大写 `INI`，包括命名空间、类名、文件名。
> 这是本项目的命名约定，与微软 .NET 常规的 PascalCase 中「缩写词3字母以上只首字母大写」不同。

#### 命名空间

必须引入正确的命名空间 `AdaWeldSystem.FileOperate`，不要拼错为 `FileOperation` 或 `FileOperations`。

```csharp
using AdaWeldSystem.FileOperate;
```

#### 写入后必须 SaveToFile()

**错误现象**：写入后文件内容没变，程序退出后修改丢失。

**原因分析**：写入方法仅修改内存缓存，忘记调用 `SaveToFile()` 会导致修改不会持久化到磁盘。

**修复方案**：写入完成后调用 `ini.SaveToFile()`。

```csharp
// 错误：修改未保存
ini.WriteString("Config", "Key", "value");
// 程序退出后文件无变化

// 正确：修改后保存
ini.WriteString("Config", "Key", "value");
ini.SaveToFile();
```

#### 路径规范

- 优先使用相对于程序目录的相对路径，如 `@"Config\INI\xxx.ini"`
- 确保目录存在。目录不存在时 `SaveToFile()` 可能失败
- 遵循 [[decisions/ADR-005-ConfigLayout]] 配置目录布局规范

#### 多线程安全

- `INIFile` 类**非线程安全**
- 多线程场景下需自行加锁保护，或每个线程使用独立实例
- 对于全局配置单例，建议在单例内部做线程安全封装

#### 编码格式

- 默认使用系统默认编码（简体中文系统为 GB2312/GBK）
- 含特殊字符时注意编码一致性问题

### 1.8 常见错误排查

| 错误现象 | 可能原因 | 解决方法 |
|---------|---------|---------|
| `CS0246` 找不到类型 `IniFile` | 类名拼写为小写 `IniFile` | 改为大写 `INIFile` |
| `CS0246` 找不到类型 `INIFile` | 未引用命名空间 | 添加 `using AdaWeldSystem.FileOperate;` |
| 读取值永远是默认值 | 路径错误或文件不存在 | 检查文件路径是否正确 |
| 写入后文件没变 | 忘记调用 `SaveToFile()` | 在写入后调用 `ini.SaveToFile()` |
| 写入失败抛异常 | 目录不存在或文件只读 | 确保目录存在、文件可写 |

---

## 2. SQLite 保留关键字

### 2.1 问题现象

在将 `AutoParam.identityInfo` 直接作为 SQLite 数据表名使用时，如果 `identityInfo` 取值为 `Default`，执行 `CREATE TABLE Default (...)` 或 `SELECT * FROM Default` 等 SQL 语句会直接报语法错误。

```csharp
// 错误示例：Default 是 SQLite 保留关键字，不能裸用为表名
_currentTableName = "Default";
Database.CreateTable(_currentTableName, _paramColumns); // SQL 语法错误
```

### 2.2 根本原因

`Default` 是 SQLite 的保留关键字（reserved keyword）。虽然 SQLite 允许通过方括号 `[]` 或双引号 `""` 转义使用关键字作为标识符，但项目当前的数据库封装层直接拼接 SQL，未做关键字转义，因此任何保留关键字作为表名都会导致语法错误。

### 2.3 解决方案

**推荐方案**：避免将 SQLite 保留关键字用作标识符。将默认配置标识从 `Default` 改名为 `DefaultParam`：

```csharp
public class AutoParam
{
    public const string DefaultIdentity = "DefaultParam";
}
```

这样 `AutoParamManager` 以 `identityInfo` 作为表名时，表名变为 `DefaultParam`，不再是保留关键字，SQL 可以正常执行。

**备选方案**：在数据库封装层统一对所有标识符加方括号或双引号转义，例如 `[Default]`。但此方案改动范围大，且容易遗漏，不推荐单独使用。

### 2.4 命名建议

1. 以用户输入或配置项作为 SQL 标识符（表名、列名等）时，必须先校验其不是数据库保留关键字。
2. 项目中的默认/哨兵值命名应避免使用数据库保留关键字，如 `Default`、`Table`、`Index`、`Select` 等。
3. 常量集中管理：通过 `AutoParam.DefaultIdentity` 这样的常量统一管理默认标识，避免在多处硬编码字符串。
4. `WireType = "Default"`、`PlateType = "Default"` 等作为普通字段值存储在列中，不受保留关键字限制，不需要修改。

---

## 3. EmguCV 常见 API 误用

### 3.1 Bitmap → Mat 正确方法

#### 错误现象

```csharp
var mat = new Emgu.CV.Mat();
Emgu.CV.CvInvoke.CvMatFromBitmap(bmp, mat);  // ❌ 编译报错：方法不存在
```

尝试调用 `CvInvoke.CvMatFromBitmap()` 方法，编译器报方法不存在的错误。

#### 原因分析

EmguCV 中不存在 `CvMatFromBitmap` 这个静态方法。Bitmap 转 Mat 的正确方式是使用扩展方法 `ToMat()`，该方法定义在 `Emgu.CV.BitmapExtension` 类中，属于 `Emgu.CV` 命名空间。

#### 修复方案

使用 `bmp.ToMat()` 扩展方法，需先添加 `using Emgu.CV;`。

```csharp
using Emgu.CV;  // 必须添加此 using，使 ToMat() 扩展方法可用

var mat = bmp.ToMat();  // ✅ Emgu.CV.BitmapExtension.ToMat()
```

#### 注意事项

- `bmp.ToMat()` 会深拷贝 Bitmap 数据，在 `using (var bmp = ...)` 块内调用是安全的
- 不要在 `bmp.Dispose()` 之后再使用返回的 Mat

### 3.2 InRange 标量参数须用 ScalarArray 包裹

#### 错误现象

调用 `CvInvoke.InRange` 等以标量作为下/上界的 API 时，编译报 CS1503「参数 N: 无法从"Emgu.CV.Structure.MCvScalar"转换为"Emgu.CV.IInputArray"」（N 通常为参数 2 和 参数 3）。每条 `InRange` 调用会同时报两条（下界、上界各一条）。

```csharp
// ❌ 错误：MCvScalar 不能转为 IInputArray
CvInvoke.InRange(gray, new MCvScalar(150), new MCvScalar(245), wireMask);
```

#### 原因分析

`CvInvoke.InRange(IInputArray src, IInputArray lowerb, IInputArray upperb, IOutputArray dst)` 的第 2、3 个参数类型是 **`IInputArray`**（图像/数组），而代码直接传了 **`MCvScalar`**（颜色标量结构体）。`MCvScalar` **不实现** `IInputArray`，因此类型不匹配。

> 易错点：画图的 `CvInvoke.Circle/Line/Rectangle/PutText` 把 `MCvScalar` 放在颜色参数位（第 3/4/6 位），是正确的；但 `InRange`、`Add/Subtract/Min/Max/BitwiseXxx` 等把标量边界放在 `IInputArray` 位（第 2/3 位），**不能**直接传 `MCvScalar`。两者签名位置不同，容易混淆。

#### 修复方案

以 `Emgu.CV.ScalarArray` 包裹 `MCvScalar`——`ScalarArray` 实现了 `IInputArray`，是 EmguCV 中表示标量数组边界的标准类型：

```csharp
// ✅ 正确：用 ScalarArray 包裹
CvInvoke.InRange(gray, new ScalarArray(new MCvScalar(150)), new ScalarArray(new MCvScalar(245)), wireMask);
```

- `ScalarArray` 位于 `Emgu.CV` 命名空间（`using Emgu.CV;` 即可，与 `CvInvoke`/`Mat` 同命名空间），无需新增 using。
- 凡是把"标量值"放到 `IInputArray` 形参位的 EmguCV 调用（阈值下/上界、掩膜标量等），一律用 `ScalarArray` 包裹。
- `Mat.SetTo(MCvScalar)` 是 `Mat` 自身的重载，可直接传 `MCvScalar`，无需包裹（与上不同）。

---

## 来源

本文档由以下 lesson 页面汇总整理而成：

- [[guides/Config-Data-Tools]] — INIFile 类的正确用法
- [[guides/Config-Data-Tools]] — SQLite 保留关键字不能用作表名/列名
- [[guides/Config-Data-Tools]] — EmguCV Bitmap→Mat 正确方法
- [[guides/Config-Data-Tools]] — EmguCV InRange/标量边界须用 ScalarArray 包裹 MCvScalar
