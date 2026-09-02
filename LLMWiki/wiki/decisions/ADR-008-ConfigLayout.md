---
title: ADR-008 Config 文件夹分层决策
date: 2026-07-03
tags: [决策, 配置, 文件结构, 规范]
status: accepted
---

# ADR-008：Config 文件夹按文件类型分层

## 背景

`Config/` 文件夹位于运行时目录（`AppDomain.CurrentDomain.BaseDirectory + "Config\"`），存放了所有 INI 配置、XML 通讯结构、GSDML 设备描述文件。

随着文件数量增加（7 个 INI + 7 个 XML + 若干 GSDML），所有文件平铺在 `Config/` 根目录下，查找和分类困难。

项目已有先例：`EmguALG/JobManager.cs` 使用 `Config/Jobs/` 子文件夹存放业务数据。

## 决策

在 `Config/` 下按文件类型创建三个子文件夹：

```
Config/
├── INI/    # INI 配置文件（7 个）
├── XML/    # XML 通讯结构文件（7 个）
└── GSDML/  # GSDML 设备描述文件（生成）
```

### 文件迁移映射

| 原路径 | 新路径 |
|---------|---------|
| `Config/*.ini` | `Config/INI/*.ini` |
| `Config/*.xml`（除 GSDML） | `Config/XML/*.xml` |
| `Config/*.GSDML.xml` | `Config/GSDML/*.GSDML.xml` |

### 代码变更

| 文件 | 变更内容 |
|------|---------|
| `FileOperate/XMLfile.cs` | `_configDirectory` 从 `\Config\` 改为 `\Config\XML\` |
| `Comm/CommunicationManager.cs` | XML 路径改为 `Config/XML/`，INI 路径改为 `Config/INI/` |
| `Comm/Profinet/GSDMLGenerator.cs` | 输出路径改为 `Config/GSDML/` |
| `InteliWeld/WeldDataManager.cs` | INI 路径改为 `Config/INI/` |
| `SmartRayCam/CameraRun.cs` | INI 路径改为 `Config/INI/` |
| `SmartRayCam/CameraPresetManager.cs` | INI 路径改为 `Config/INI/` |
| `EmguALG/ImageRoiTools.cs` | INI 路径改为 `Config/INI/` |
| `PointCloudData/Render/RenderConfig.cs` | INI 路径改为 `Config/INI/` |
| `PointCloudData/RunFileRecord/RunRecordManager.cs` | INI 路径改为 `Config/INI/` |
| `UIDesign/Sub2UI/XMLEditor.cs` | 初始目录改为 `Config/XML/` |

## 备选方案

1. **不分层，保持现状**：最简单，但文件越多越乱。
2. **按模块分子文件夹**（如 `Config/Comm/`、`Config/Camera/`）: 某些文件（如 `CommunicationConfig.xml`）难以划分到单一模块；且 INI 和 XML 仍混在一起。
3. **当前方案（按文件类型分层）**：最简单、最直观，与 `Config/Jobs/` 先例不冲突。

## 后果

### 正面

- 文件按类型归类，查找更直观
- 新增配置文件时，放置位置一目了然
- 与 `Config/Jobs/` 先例一致（业务数据用子文件夹）

### 负面

- 需要同步修改 10 个代码文件的路径引用
- 运行时需确保 `Config/INI/`、`Config/XML/`、`Config/GSDML/` 目录存在（`XMLfile.cs` 的 `CheckFile` 方法会自动创建）

## 相关页面

- [[modules/FileOperate]] — INIFile / XMLfile 工具库
- [[modules/Comm]] — CommunicationManager、GSDMLGenerator
- [[api/ProfinetGSDML]] — GSDML 生成说明

---
