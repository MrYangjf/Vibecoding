---
title: CodeMap-Symbols-FileOperate — 代码地图·符号签名层·FileOperate（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-FileOperate — FileOperate 的类型与签名

> **一句话**：模块 `FileOperate` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> 配置读写：INI + XML + 自愈 + 迁移 + 备份
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.FileOperate` | 5 | 6 | 文件 · 配置读写与日志 | [[modules/FileOperate]] | ADR-033/040/079 |

| 项 | 值 |
|---|---|
| 类型数 | 6 |
| 方法数 | 92 |

## 章节导航

- [ConfigBackupHelper](#ConfigBackupHelper)
- [ConfigPathMigrator](#ConfigPathMigrator)
- [ConfigSelfHeal](#ConfigSelfHeal)
- [INIFile](#INIFile)
- [IniDefault](#IniDefault)
- [XdocumentReaderWriter](#XdocumentReaderWriter)

## ConfigBackupHelper

- 签名：`public static class ConfigBackupHelper`
- 位置：`FileOperate/ConfigBackupHelper.cs:8`
- 命名空间：`AdaWeldSystem.FileOperate`
- 方法（4）：
  - `void CopyDirectory(string source, string target)` — `FileOperate/ConfigBackupHelper.cs:18`
  - `string CreateBackupFolder()` — `FileOperate/ConfigBackupHelper.cs:35`
  - `bool BackupFile(string relativePath, string backupFolder)` — `FileOperate/ConfigBackupHelper.cs:55`
  - `bool BackupDirectory(string relativeDirectory, string backupFolder)` — `FileOperate/ConfigBackupHelper.cs:82`

## ConfigPathMigrator

- 签名：`public static class ConfigPathMigrator`
- 位置：`FileOperate/ConfigPathMigrator.cs:8`
- 命名空间：`AdaWeldSystem.FileOperate`
- 方法（5）：
  - `void MoveDirectoryIfNeeded(string legacyRelativePath, string currentRelativePath)` — `FileOperate/ConfigPathMigrator.cs:41`
  - `void BuildMigrationMap()` — `FileOperate/ConfigPathMigrator.cs:70`
  - `void MoveToCurrentPath(string[] legacyCandidates, string currentRelativePath)` — `FileOperate/ConfigPathMigrator.cs:108`
  - `void PruneEmptyDirectories(string directory)` — `FileOperate/ConfigPathMigrator.cs:140`
  - `void MigrateAll()` — `FileOperate/ConfigPathMigrator.cs:159`

## ConfigSelfHeal

- 签名：`public static class ConfigSelfHeal`
- 位置：`FileOperate/ConfigSelfHeal.cs:14`
- 命名空间：`AdaWeldSystem.FileOperate`
- 方法（27）：
  - `void Log(string message, MessageLevel level)` — `FileOperate/ConfigSelfHeal.cs:34`
  - `bool EnsureIni(string fullPath, string relativePath, string fileLabel, IList<IniDefault> defaults, bool allowWrite)` — `FileOperate/ConfigSelfHeal.cs:53`
  - `bool EnsureXml(string fullPath, string relativePath, string fileLabel, XDocument template, bool allowWrite)` — `FileOperate/ConfigSelfHeal.cs:111`
  - ` Key(string section, string key, string value)` — `FileOperate/ConfigSelfHeal.cs:161`
  - `void Backup(string relativePath)` — `FileOperate/ConfigSelfHeal.cs:176`
  - `void WriteTextAtomically(string fullPath, string relativePath, string content, Encoding encoding)` — `FileOperate/ConfigSelfHeal.cs:195`
  - `void WriteXmlAtomically(string fullPath, string relativePath, XDocument document)` — `FileOperate/ConfigSelfHeal.cs:223`
  - `void WriteXmlAtomically(string fullPath, string relativePath, XDocument document, Encoding encoding, bool hasDeclaration)` — `FileOperate/ConfigSelfHeal.cs:235`
  - `void ReplaceFile(string tempPath, string fullPath)` — `FileOperate/ConfigSelfHeal.cs:271`
  - `void TryDelete(string path)` — `FileOperate/ConfigSelfHeal.cs:286`
  - `void ReadTextPreserveEncoding(string fullPath, string text, Encoding encoding)` — `FileOperate/ConfigSelfHeal.cs:305`
  - `void FindMissingIniKeys(string text, IList<IniDefault> defaults)` — `FileOperate/ConfigSelfHeal.cs:316`
  - `void PatchIniText(string original, List<IniDefault> missing)` — `FileOperate/ConfigSelfHeal.cs:357`
  - `void FindSectionInsertIndex(List<string> lines, int sectionStart, int sectionEndExclusive)` — `FileOperate/ConfigSelfHeal.cs:444`
  - `void WriteIniTemplate(string fullPath, string relativePath, string fileLabel, IList<IniDefault> defaults)` — `FileOperate/ConfigSelfHeal.cs:461`
  - `void ReadXmlPreserve(string fullPath, XDocument document, Encoding encoding, bool hasDeclaration)` — `FileOperate/ConfigSelfHeal.cs:497`
  - `void EnsureChildren(XElement realParent, XElement templateParent, List<string> added)` — `FileOperate/ConfigSelfHeal.cs:508`
  - `void FindMatch(XElement parent, XElement templateNode)` — `FileOperate/ConfigSelfHeal.cs:528`
  - `void InsertAtTail(XElement parent, XElement child)` — `FileOperate/ConfigSelfHeal.cs:557`
  - `void DetectNewline(XDocument document)` — `FileOperate/ConfigSelfHeal.cs:580`
  - `void DetectChildIndent(XElement parent)` — `FileOperate/ConfigSelfHeal.cs:595`
  - `void DetectNodeIndent(XElement node)` — `FileOperate/ConfigSelfHeal.cs:610`
  - `void BuildDisplayName(XElement node)` — `FileOperate/ConfigSelfHeal.cs:625`
  - `void VerifyXml(string fullPath, XDocument template, string fileLabel)` — `FileOperate/ConfigSelfHeal.cs:640`
  - `void LogBuildSummary(string fileLabel, IList<string> keys, string source)` — `FileOperate/ConfigSelfHeal.cs:668`
  - `void LogBuildSummary(string fileLabel, IList<IniDefault> keys, string source)` — `FileOperate/ConfigSelfHeal.cs:677`
  - `void LogBuildSummary(string fileLabel, List<string> keys, string source)` — `FileOperate/ConfigSelfHeal.cs:689`

## INIFile

- 签名：`public class INIFile`
- 位置：`FileOperate/INIFile.cs:9`
- 命名空间：`AdaWeldSystem.FileOperate`
- 方法（18）：
  - `string ReadString(string section, string key, = "")` — `FileOperate/INIFile.cs:66`
  - `int ReadInt(string section, string key, = 0)` — `FileOperate/INIFile.cs:88`
  - `double ReadDouble(string section, string key, = 0.0)` — `FileOperate/INIFile.cs:103`
  - `bool ReadBool(string section, string key, = false)` — `FileOperate/INIFile.cs:118`
  - `Dictionary<string, string> GetSectionKeys(string section)` — `FileOperate/INIFile.cs:136`
  - `List<string> GetAllSections()` — `FileOperate/INIFile.cs:153`
  - `bool SectionExists(string section)` — `FileOperate/INIFile.cs:164`
  - `bool KeyExists(string section, string key)` — `FileOperate/INIFile.cs:179`
  - `void WriteString(string section, string key, string value)` — `FileOperate/INIFile.cs:198`
  - `void WriteInt(string section, string key, int value)` — `FileOperate/INIFile.cs:220`
  - `void WriteDouble(string section, string key, double value)` — `FileOperate/INIFile.cs:229`
  - `void WriteBool(string section, string key, bool value)` — `FileOperate/INIFile.cs:238`
  - `bool DeleteKey(string section, string key)` — `FileOperate/INIFile.cs:251`
  - `bool DeleteSection(string section)` — `FileOperate/INIFile.cs:275`
  - `void SaveToFile()` — `FileOperate/INIFile.cs:291`
  - `void Reload()` — `FileOperate/INIFile.cs:312`
  - `void Clear()` — `FileOperate/INIFile.cs:325`
  - `void LoadFromFile()` — `FileOperate/INIFile.cs:338`
- 构造（1）：
  - `INIFile(string filePath)` — `FileOperate/INIFile.cs:38`
- 属性（2）：
  - `string FilePath { get; set; }` — `FileOperate/INIFile.cs:18`
  - `int SectionCount { get; set; }` — `FileOperate/INIFile.cs:21`

## IniDefault

- 签名：`public sealed class IniDefault`
- 位置：`FileOperate/ConfigSelfHeal.cs:19`
- 命名空间：`AdaWeldSystem.FileOperate`
- 属性（3）：
  - `string Section { get; set; }` — `FileOperate/ConfigSelfHeal.cs:22`
  - `string Key { get; set; }` — `FileOperate/ConfigSelfHeal.cs:25`
  - `string Value { get; set; }` — `FileOperate/ConfigSelfHeal.cs:28`

## XdocumentReaderWriter

- 签名：`public class XdocumentReaderWriter`
- 位置：`FileOperate/XdocumentReaderWriter.cs:11`
- 命名空间：`AdaWeldSystem.FileOperate`
- 方法（30）：
  - `void CheckFile(string configXmlPath, bool createDirectory)` — `FileOperate/XdocumentReaderWriter.cs:85`
  - `void NewXdocument()` — `FileOperate/XdocumentReaderWriter.cs:101`
  - `void NewXdocument(string rootName, = "1.0", = "UTF-8")` — `FileOperate/XdocumentReaderWriter.cs:110`
  - `void SaveXdocument()` — `FileOperate/XdocumentReaderWriter.cs:119`
  - `string GetIp()` — `FileOperate/XdocumentReaderWriter.cs:136`
  - `int GetPort()` — `FileOperate/XdocumentReaderWriter.cs:151`
  - `string GetConfig()` — `FileOperate/XdocumentReaderWriter.cs:166`
  - `void SetConfig(string name)` — `FileOperate/XdocumentReaderWriter.cs:181`
  - `string GetXmlSendStr()` — `FileOperate/XdocumentReaderWriter.cs:201`
  - `string GetXmlStrValue(string xmlStr, string element, string attribute)` — `FileOperate/XdocumentReaderWriter.cs:211`
  - `string GetXmlStrValue(string xmlStr, string element)` — `FileOperate/XdocumentReaderWriter.cs:222`
  - `void LoadFromXmlString(string xmlContent)` — `FileOperate/XdocumentReaderWriter.cs:230`
  - `void LoadFromFilePath(string filePath)` — `FileOperate/XdocumentReaderWriter.cs:238`
  - `bool Reload()` — `FileOperate/XdocumentReaderWriter.cs:246`
  - `void SaveToFilePath(string filePath)` — `FileOperate/XdocumentReaderWriter.cs:267`
  - `string ToXmlString()` — `FileOperate/XdocumentReaderWriter.cs:286`
  - ` GetXDocument()` — `FileOperate/XdocumentReaderWriter.cs:292`
  - `void SetXDocument(XDocument doc)` — `FileOperate/XdocumentReaderWriter.cs:298`
  - ` AddElement(string elementName, = null)` — `FileOperate/XdocumentReaderWriter.cs:309`
  - ` AddElement(XElement parent, string elementName, = null)` — `FileOperate/XdocumentReaderWriter.cs:323`
  - ` AddElementWithAttributes(XElement parent, string elementName, string> attributes, = null)` — `FileOperate/XdocumentReaderWriter.cs:338`
  - ` GetElement(string elementName)` — `FileOperate/XdocumentReaderWriter.cs:357`
  - ` GetElementByPath(string path)` — `FileOperate/XdocumentReaderWriter.cs:366`
  - `IEnumerable<XElement> GetElements(string elementName)` — `FileOperate/XdocumentReaderWriter.cs:387`
  - `IEnumerable<XElement> GetChildElements(string parentPath, string childName)` — `FileOperate/XdocumentReaderWriter.cs:396`
  - `string GetElementValue(string elementName, = "")` — `FileOperate/XdocumentReaderWriter.cs:406`
  - `string GetElementValueByPath(string path, = "")` — `FileOperate/XdocumentReaderWriter.cs:415`
  - `void SetElementValue(string elementName, string value)` — `FileOperate/XdocumentReaderWriter.cs:423`
  - `string GetAttributeValue(XElement element, string attributeName, = "")` — `FileOperate/XdocumentReaderWriter.cs:435`
  - `void SetAttributeValue(XElement element, string attributeName, string value)` — `FileOperate/XdocumentReaderWriter.cs:444`
- 构造（2）：
  - `XdocumentReaderWriter(string relativeDirectory, string xmlName, bool createIfMissing)` — `FileOperate/XdocumentReaderWriter.cs:45`
  - `XdocumentReaderWriter()` — `FileOperate/XdocumentReaderWriter.cs:75`

## 相关页面

- [[architecture/CodeMap]]
