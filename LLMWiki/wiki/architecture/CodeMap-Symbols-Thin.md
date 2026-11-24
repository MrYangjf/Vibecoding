---
title: CodeMap-Symbols-Thin — 代码地图·符号签名层·薄模块合并页（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-Thin — 薄模块合并页 的类型与签名

> **一句话**：类型数少于 6 的小模块合并成一页（逐类 → `文件:行` → 成员签名）；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **为什么合并**：单独建小页会产出模板高度相似的碎页（触发重复度告警）且信息密度低。
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

| 模块 | 类型数 |
|---|---|
| `ConfigFileControl` | 5 |
| `Properties` | 2 |
| `Program.cs` | 1 |

## ConfigFileControl


| 项 | 值 |
|---|---|
| 类型数 | 5 |
| 方法数 | 50 |

### ConfigChangeLogger

- 签名：`public static class ConfigChangeLogger`
- 位置：`ConfigFileControl/Implementations/ConfigChangeLogger.cs:10`
- 命名空间：`AdaWeldSystem.ConfigFileControl.Implementations`
- 方法（8）：
  - `void CollectScalars(object source)` — `ConfigFileControl/Implementations/ConfigChangeLogger.cs:21`
  - `void IsScalar(Type type)` — `ConfigFileControl/Implementations/ConfigChangeLogger.cs:81`
  - `void IsIgnored(string name)` — `ConfigFileControl/Implementations/ConfigChangeLogger.cs:89`
  - `void IsChanged(string before, string after)` — `ConfigFileControl/Implementations/ConfigChangeLogger.cs:105`
  - `void Emit(string tag, string scene, string name, string before, string after)` — `ConfigFileControl/Implementations/ConfigChangeLogger.cs:127`
  - `void Display(string value)` — `ConfigFileControl/Implementations/ConfigChangeLogger.cs:136`
  - `void LogObjectDiff(string scene, object before, object after, = null)` — `ConfigFileControl/Implementations/ConfigChangeLogger.cs:146`
  - `void LogField(string scene, string name, string before, string after, = null)` — `ConfigFileControl/Implementations/ConfigChangeLogger.cs:177`

### ConfigFileManager

- 签名：`public class ConfigFileManager`
- 位置：`ConfigFileControl/Implementations/ConfigFileManager.cs:9`
- 命名空间：`AdaWeldSystem.ConfigFileControl.Implementations`
- 方法（12）：
  - `string AbsolutePath(string fileName)` — `ConfigFileControl/Implementations/ConfigFileManager.cs:39`
  - ` GetIni(string fileName)` — `ConfigFileControl/Implementations/ConfigFileManager.cs:47`
  - ` GetXml(string fileName, = true)` — `ConfigFileControl/Implementations/ConfigFileManager.cs:62`
  - `IEnumerable<string> RegisteredFiles()` — `ConfigFileControl/Implementations/ConfigFileManager.cs:71`
  - `void ReloadAll()` — `ConfigFileControl/Implementations/ConfigFileManager.cs:78`
  - `string ModuleRelativeDir(string module)` — `ConfigFileControl/Implementations/ConfigFileManager.cs:87`
  - ` GetModuleIni(string module, string fileName)` — `ConfigFileControl/Implementations/ConfigFileManager.cs:97`
  - ` GetModuleXml(string module, string fileName, = true)` — `ConfigFileControl/Implementations/ConfigFileManager.cs:115`
  - `string ModuleAbsolutePath(string module, string fileName)` — `ConfigFileControl/Implementations/ConfigFileManager.cs:129`
  - `void SaveIniWithAudit(IniConfigFile file, string scene, string tag, = null)` — `ConfigFileControl/Implementations/ConfigFileManager.cs:139`
  - `void SaveIni(IniConfigFile file, string scene, string tag)` — `ConfigFileControl/Implementations/ConfigFileManager.cs:159`
  - `void SaveXmlWithAudit(XmlConfigFile file, string scene, string tag, = null)` — `ConfigFileControl/Implementations/ConfigFileManager.cs:169`
- 构造（1）：
  - `ConfigFileManager()` — `ConfigFileControl/Implementations/ConfigFileManager.cs:32`
- 属性（1）：
  - `ConfigFileManager Instance { get; set; }` — `ConfigFileControl/Implementations/ConfigFileManager.cs:14`

### ConfigSnapshot

- 签名：`public static class ConfigSnapshot`
- 位置：`ConfigFileControl/Implementations/ConfigSnapshot.cs:10`
- 命名空间：`AdaWeldSystem.ConfigFileControl.Implementations`
- 方法（5）：
  - `Dictionary<string, string> OfIni(IniConfigFile file)` — `ConfigFileControl/Implementations/ConfigSnapshot.cs:15`
  - `Dictionary<string, string> OfXml(XmlConfigFile file)` — `ConfigFileControl/Implementations/ConfigSnapshot.cs:39`
  - `void Walk(XElement element, string prefix, Dictionary<string, string> map)` — `ConfigFileControl/Implementations/ConfigSnapshot.cs:67`
  - `void Diff(string scene, string> before, string> after, string tag)` — `ConfigFileControl/Implementations/ConfigSnapshot.cs:87`
  - `void Same(string before, string after)` — `ConfigFileControl/Implementations/ConfigSnapshot.cs:118`

### IniConfigFile

- 签名：`public class IniConfigFile`
- 位置：`ConfigFileControl/Implementations/IniConfigFile.cs:7`
- 命名空间：`AdaWeldSystem.ConfigFileControl.Implementations`
- 方法（7）：
  - `string Read(string section, string key, string defaultValue)` — `ConfigFileControl/Implementations/IniConfigFile.cs:32`
  - `void Write(string section, string key, string value)` — `ConfigFileControl/Implementations/IniConfigFile.cs:38`
  - `bool SectionExists(string section)` — `ConfigFileControl/Implementations/IniConfigFile.cs:44`
  - `bool KeyExists(string section, string key)` — `ConfigFileControl/Implementations/IniConfigFile.cs:50`
  - `void Reload()` — `ConfigFileControl/Implementations/IniConfigFile.cs:56`
  - `void Save()` — `ConfigFileControl/Implementations/IniConfigFile.cs:62`
  - `Dictionary<string, string> SectionKeys(string section)` — `ConfigFileControl/Implementations/IniConfigFile.cs:70`
- 构造（1）：
  - `IniConfigFile(string filePath, string fileName, string relativePath)` — `ConfigFileControl/Implementations/IniConfigFile.cs:15`
- 属性（3）：
  - `INIFile Raw { get; set; }` — `ConfigFileControl/Implementations/IniConfigFile.cs:23`
  - `string FileName { get; set; }` — `ConfigFileControl/Implementations/IniConfigFile.cs:26`
  - `string RelativePath { get; set; }` — `ConfigFileControl/Implementations/IniConfigFile.cs:29`

### XmlConfigFile

- 签名：`public class XmlConfigFile`
- 位置：`ConfigFileControl/Implementations/XmlConfigFile.cs:9`
- 命名空间：`AdaWeldSystem.ConfigFileControl.Implementations`
- 方法（7）：
  - `string Read(string section, string key, string defaultValue)` — `ConfigFileControl/Implementations/XmlConfigFile.cs:42`
  - `void Write(string section, string key, string value)` — `ConfigFileControl/Implementations/XmlConfigFile.cs:52`
  - `bool SectionExists(string section)` — `ConfigFileControl/Implementations/XmlConfigFile.cs:66`
  - `bool KeyExists(string section, string key)` — `ConfigFileControl/Implementations/XmlConfigFile.cs:72`
  - `void Reload()` — `ConfigFileControl/Implementations/XmlConfigFile.cs:79`
  - `void Save()` — `ConfigFileControl/Implementations/XmlConfigFile.cs:85`
  - `void WriteDouble(string section, string key, double value)` — `ConfigFileControl/Implementations/XmlConfigFile.cs:94`
- 构造（1）：
  - `XmlConfigFile(string relativeDir, string fileName, bool createIfMissing)` — `ConfigFileControl/Implementations/XmlConfigFile.cs:17`
- 属性（4）：
  - `string RelativeDir { get; set; }` — `ConfigFileControl/Implementations/XmlConfigFile.cs:30`
  - `string FileName { get; set; }` — `ConfigFileControl/Implementations/XmlConfigFile.cs:33`
  - `string RelativePath { get; set; }` — `ConfigFileControl/Implementations/XmlConfigFile.cs:36`
  - `XdocumentReaderWriter Raw { get; set; }` — `ConfigFileControl/Implementations/XmlConfigFile.cs:39`

## Properties


| 项 | 值 |
|---|---|
| 类型数 | 2 |
| 方法数 | 0 |

### Resources

- 签名：`internal class Resources`
- 位置：`Properties/Resources.Designer.cs:22`
- 命名空间：`AdaWeldSystem.Properties`
- 成员：（无）

### Settings

- 签名：`internal sealed partial class Settings`
- 位置：`Properties/Settings.Designer.cs:15`
- 命名空间：`AdaWeldSystem.Properties`
- 成员：（无）

## Program.cs

> 程序入口（Main）

| 项 | 值 |
|---|---|
| 类型数 | 1 |
| 方法数 | 2 |

### Program

- 签名：`internal static class Program`
- 位置：`Program.cs:11`
- 命名空间：`AdaWeldSystem`
- 方法（2）：
  - `bool SetProcessDPIAware()` — `Program.cs:13`
  - `void Main()` — `Program.cs:17`

## 相关页面

- [[architecture/CodeMap]]
