---
title: API · ConfigSnapshot（配置快照与差异审计）
date: 2026-11-19
updated: 2026-11-19
tags: [API, 配置, 快照, 差异审计, ConfigFileControl]
status: active
---

# API · ConfigSnapshot

> 把一份配置文档摊平成「路径 → 值」字典，用于比较保存前后的变动项。
> 模块：`ConfigFileControl/`（命名空间 `AdaWeldSystem.ConfigFileControl.Implementations`）。

## 一、公共 API

| 成员 | 签名 | 说明 |
|---|---|---|
| `OfIni` | `static Dictionary<string,string> (IniConfigFile file)` | INI 全量快照（键 = `节.键`） |
| `OfXml` | `static Dictionary<string,string> (XmlConfigFile file)` | XML 全量快照（键 = 元素路径） |
| `Diff` | `static void (string scene, Dictionary before, Dictionary after, string tag)` | 逐项比较，只记录**有变动**的键 |

## 二、关键设计

⛔ **快照取磁盘态，不取载体内存态** —— 若取内存态，写入已发生在快照之前则 diff 检不出变更。

- INI：`new INIFile(file.Raw.FilePath)` 独立读盘 ⇒ 不干扰载体内存。
- XML：按 `RelativeDir + FileName` 拼绝对路径后 `XDocument.Load`。

⛔ **数值等价判定** —— `1` 与 `1.0` 视为相同（避免格式性误报）；判定逻辑与 `WeldParamChangeLogger.IsChanged` 一致。

## 三、调用链

```
配置类.SaveConfig()
  → ConfigFileManager.SaveIniWithAudit / SaveXmlWithAudit / SaveIni / SaveXml
      ① ConfigSnapshot.OfIni/OfXml   ← 磁盘旧值
      ② 执行保存
      ③ ConfigSnapshot.Diff(旧, 新)   ← 只记变动项
```

## 四、相关页面

- [[api/ConfigFileManager]]
- [[decisions/ADR-007-CodeSimplificationStandard]] D2
- [[lessons/ConfigOwnershipByManager]]
