---
title: API · ConfigFileManager（全局配置文档总管）
date: 2026-11-19
updated: 2026-11-19
tags: [API, 配置, Manager, ConfigFileControl, 抽象层, 实现层]
status: active
---

# API · ConfigFileManager

> 全局配置文档的**唯一持有者**与**唯一对外访问口**（ADR-006 §3.4 Manager 四职责之三「持久化配置」）。
> 模块：`ConfigFileControl/`（命名空间 `AdaWeldSystem.ConfigFileControl`）。

## 一、分层结构

| 层 | 文件 | 内容 |
|---|---|---|
| 抽象层 | `Abstractions/IConfigFileProvider.cs` | 载体契约：读 / 写 / 存在性 / Reload / Save |
| 抽象层 | `Abstractions/IConfigRegion.cs` | 区域契约：按 TabPage 分区读写（**键级**） |
| 实现层 | `Implementations/IniConfigFile.cs` | INI 载体（包装 `INIFile`） |
| 实现层 | `Implementations/XmlConfigFile.cs` | XML 载体（包装 `XdocumentReaderWriter`） |
| 实现层 | `Implementations/ConfigFileManager.cs` | **Manager**：路径解析 + 载体装配 + 路由 |
| 实现层 | `Implementations/ConfigChangeLogger.cs` | 配置变更审计（**2026-11-19 改名**：原 `WeldParamChangeLogger`，因已记录所有配置变更而非仅焊参；标签可传，不依赖焊参类型） |
| 实现层 | `Implementations/ConfigSnapshot.cs` | 配置快照与差异比较（磁盘态） |

⛔ 不建 Core（场景 B 纯自研，ADR-006 D2）。

## 二、公共 API

| 成员 | 签名 | 说明 |
|---|---|---|
| `Instance` | `ConfigFileManager` | 全局唯一实例（普通单例） |
| `ConfigRootRelativeDir` | `const string` | 全局根目录 = `Config\ConfigFileControl` |
| `GetIni` | `IniConfigFile (string fileName)` | 取根目录下的 INI 载体（不存在则创建登记） |
| `GetXml` | `XmlConfigFile (string fileName, bool createIfMissing = true)` | 取根目录下的 XML 载体（文件名不含扩展名） |
| `GetModuleIni` | `IniConfigFile (string module, string fileName)` | 取模块子目录下的 INI 载体 |
| `GetModuleXml` | `XmlConfigFile (string module, string fileName, bool createIfMissing = true)` | 取模块子目录下的 XML 载体 |
| `ModuleRelativeDir` | `static string (string module)` | 模块子目录相对路径 |
| `ModuleAbsolutePath` | `static string (string module, string fileName)` | 模块内文件绝对路径 |
| `AbsolutePath` | `static string (string fileName)` | 根目录下文件绝对路径 |
| `ReloadAll` | `void ()` | 全部载体重新从磁盘载入 |
| `SaveIniWithAudit` | `static void (IniConfigFile file, string scene, string tag, Action saveAction = null)` | 保存 INI 载体并按文件键值**只记变动项** |
| `SaveXmlWithAudit` | `static void (XmlConfigFile file, string scene, string tag, Action saveAction = null)` | 保存 XML 载体并按元素值**只记变动项** |
| `SaveIni` | `static void (IniConfigFile file, string scene, string tag)` | 同上（就地落盘，简化入口） |

| `ReloadAll` | `void ()` | 全部载体重新从磁盘载入 |
| `RegisteredFiles` | `IEnumerable<string>` | 已登记的载体文件名（诊断用） |

## 三、目录结构（`Config\ConfigFileControl\`）

| 模块 | 文件 |
|---|---|
| `WeldParam` | `WeldParam.ini` · `WeldParam.xml` · `TaLaCurve.xml` · `WeldData.ini` |
| `MotionControl` | `DeltaMotionConfig.xml` · `WeldHeadSlave.xml` |
| `LineLaser` | `LineLaserConfig.xml` |
| `Comm` | `CommunicationSettings.ini` · `Server/Client/Send/Recive/RobotServer/RobotClient/PLC/Modbus.xml` |
| `MonitorCam` | `MonitorCamera.ini` |
| `PCLOperate` | `RenderConfig.ini` |
| `MainDeviceControl` | `SimulationController.ini` · 模组 workflow XML |
| `EmguALG` | `MonitorAlgorithm.ini` · `ImageRoi.ini` |

## 四、区域模型（`WeldParamConfig` 内部）

`WeldParamConfig`（原 `WeldAlgorithmsConfig`）按 **TabPage** 划 5 个区域：

| 区域 | TabPage | section | 键数 |
|---|---|---|---|
| `Preset` | 工艺·激光工艺设置 | `PROCESS_CONTROL` | 12 |
| `Adapt` | 工艺·自适应工艺参数设置 | `WELD_PARAM_ADJUST` | 2 |
| `Flow` | 系统·流程控制与测试 | `PROCESS_CONTROL` + `SEAM_GUIDE` | 5 |
| `System` | 系统·轨迹跟踪参数设置 | `SEAM_GUIDE` + XML 几何/标定 | 19 |
| `Quick` | 工艺·激光工艺设置（Y 轴锁定） | `PROCESS_CONTROL` | 1 |

### 跨页隔离机制（关键）

⛔ 载体是**整文件重写**（`INIFile.SaveToFile` = `File.WriteAllText`；`SaveXdocument` 整篇重写）⇒ 保存前必须：

```
① carrier.Reload()      ← 先拿其它区域已保存的最新值
② 只写本区域涉及的键    ← 键级（同 section 跨 TabPage 共享时必需）
③ carrier.Save()
```

## 五、相关页面

- [[decisions/ADR-006-ModuleOrganizationPatternStandard]] D2
- [[lessons/ConfigOwnershipByManager]] · [[lessons/ConfigFileSplitByTabPage]]
- [[api/WeldParamManager]]
