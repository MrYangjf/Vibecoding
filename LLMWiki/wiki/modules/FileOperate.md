---
title: FileOperate 模块 — 文件操作工具库
date: 2026-07-01
tags: [模块, 工具, 文件, INI, XML]
source: raw/knowledge/AdaWeldSystem_Wiki.md
---

# FileOperate 模块 — 文件操作工具库

> 项目通用文件操作工具库：INI 配置读写、日志记录、XML 序列化。
> **模块位置**：`AdaWeldSystem/FileOperate/`

## 目录结构

```
FileOperate/
├── INIFile.cs                           ← INI 配置文件读写
├── Log.cs                               ← 日志管理
└── XdocumentReaderWriter.cs             ← XML 文档操作（XdocumentReaderWriter）
```

## 核心文件

| 文件 | 职责 |
|------|------|
| INIFile.cs | INI 配置文件读写（自研，非 Windows API）；文件位于 `Config/INI/` |
| Log.cs | 日志管理（分级日志、文件轮转） |
| XdocumentReaderWriter.cs | XML 文档加载、保存、通用 DOM 操作（元素/属性读写、路径导航）；XML 文件位于 `Config/XML/` |

## XdocumentReaderWriter 通用方法（2026-07-01 扩展）

`XdocumentReaderWriter` 提供以下通用 XML 操作能力，供业务层调用：

| 方法 | 作用 |
|------|------|
| `NewXdocument(rootName, version, encoding)` | 创建带 XML 声明的新文档 |
| `AddElement(parent, name, value)` | 在指定父元素下添加子元素 |
| `AddElementWithAttributes(parent, name, attrs, value)` | 添加带属性的子元素 |
| `GetElement(name)` | 获取指定名称的第一个元素，**返回 `XElement`**（非 string） |
| `GetElementValue(name, default)` | 获取指定名称的第一个元素的**值**，**返回 `string`** |
| `GetElementByPath(path)` | 按路径获取元素（如 `"CONFIG/IP_NUMBER"`），**返回 `XElement`** |
| `GetChildElements(parentPath, childName)` | 获取指定父路径下的子元素集合 |
| `GetElementValueByPath(path, default)` | 按路径获取元素值，**返回 `string`** |
| `GetAttributeValue(element, name, default)` | 获取元素属性值 |
| `SetAttributeValue(element, name, value)` | 设置元素属性值 |

> **职责边界**：XMLfile 只提供通用 DOM 操作，不感知任何业务结构。KUKA 特定的 XML 结构生成由 `[[modules/KUKARobot]]/KUKAXMLConfig` 负责。

> ⚠️ **GetElement vs GetElementValue 陷阱**：`GetElement(name)` 返回 `XElement` 类型，`GetElementValue(name)` 返回 `string` 类型。将 `GetElement` 结果赋值给 `string` 变量会导致 CS0029 编译错误（无法将 XElement 隐式转换为 string）。**读取元素值用 `GetElementValue`，获取元素对象用 `GetElement`**。详见 [[lessons/CSharp-Language-Pitfalls]]。

## INIFile 特点

- 自研实现，不依赖 Windows API
- 支持 Section/Key/Value 三级结构
- INI 文件统一存放于 `Config/INI/`（ADR-007）
- 被几乎所有模块使用（配置持久化）

## XMLfile 特点

- XML 文件统一存放于 `Config/XML/`（ADR-007）
- `_configDirectory` 硬编码为 `AppDomain.CurrentDomain.BaseDirectory + @"\Config\XML\"`
- `CheckFile()` 方法会自动创建目录
- `XdocumentReaderWriter` 非 UI 类（非 `Control`）：`SaveXdocument`/`SaveToFilePath` 内原 `UIMessageBox.ShowError`（SunnyUI，已移除）现改用 `AntdUI.Modal.open(new AntdUI.Modal.Config(System.Windows.Forms.Form.ActiveForm, "错误", msg) { Icon = AntdUI.TType.Error, Draggable = true })`；`Modal.Config` 的 owner 须为 `Control`/`IWin32Window`，非 UI 类用 `System.Windows.Forms.Form.ActiveForm`，**不可传 `this`**；详见 [[project/SunnyUI-Legacy]]

## 协作关系

- 所有模块 → 通过 INIFile 保存配置
- [[modules/Comm]] → 日志系统与通讯耦合（已知循环依赖）

---

*来源：raw/knowledge/AdaWeldSystem_Wiki.md*
