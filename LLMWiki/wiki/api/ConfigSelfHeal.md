---
title: ConfigSelfHeal 配置自愈 API
date: 2026-11-05
updated: 2026-11-05
tags: [API, 配置, 自愈]
status: accepted
---

# ConfigSelfHeal 配置自愈 API

> 文件：`AdaWeldSystem\FileOperate\ConfigSelfHeal.cs`（命名空间 `AdaWeldSystem.FileOperate`）
> 决策来源：[[decisions/ADR-086-ConfigSelfHeal]]

## 公共 API

| 成员 | 签名 | 说明 |
|---|---|---|
| `EnsureIni` | `static bool EnsureIni(string fullPath, string relativePath, string fileLabel, IList<IniDefault> defaults, bool allowWrite)` | INI 补缺；文件缺失按模板生成；返回是否写盘 |
| `EnsureXml` | `static bool EnsureXml(string fullPath, string relativePath, string fileLabel, XDocument template, bool allowWrite)` | XML 补缺；`template` 由配置类自身 Save 产物生成；返回是否写盘 |
| `Key` | `static IniDefault Key(string section, string key, string value)` | 构造 INI 默认项 |
| `IniDefault` | `Section/Key/Value` | INI 模板项 |

## 行为契约

1. **只增不改**：已有键/节点不动、不删、不重排；INI 保留注释/空行/节序，XML 保留空白与节点顺序。
2. **幂等**：缺键数为 0 → 返回 `false`，不写盘、不打日志。
3. **写盘安全**：写前 `ConfigBackupHelper` 备份；临时文件 + 原子替换；异常 → Warning + 返回 `false`，调用方保留内存默认。
4. **回读校验**：写后重新解析并再次比对模板；仍有缺键 → Warning。
5. **缺失文件**：生成完整默认模板并记「配置缺失，已生成默认配置 <文件名>」。
6. **日志**：`配置补缺 <文件>：新增 N 键（K=v…；来源 代码默认）`，单文件一条。

## 哪些路径会写盘

| 入口 | 调用 | 写盘 |
|---|---|---|
| `DeltaMotionConfig.LoadConfig(bool writeLog)` | → `LoadConfig(writeLog, writeLog)` | 权威加载（true）允许；预览（false）禁止 |
| `DeltaMotionConfig.LoadConfig(bool, bool allowHeal)` | 方向键已存在时加载期补缺；缺失文件推迟 | 是（一次） |
| `MontionManager.EnsureMotionConfigKeys` | 迁移判定后合并补写方向 + 其它缺键 | 是（一次，幂等） |
| `LineLaserConfig.LoadConfig(bool allowHeal)` | 缺文件生成模板 + 缺键补写 | 是 |
| `MonitorCamConfig.LoadFromIni(string, bool allowHeal)` | 缺文件模板 + 缺键补写 | 是 |
| `WeldParamManager.HealAlgorithmsConfigKeys` | 工艺 XML + 工艺 INI 镜像补缺 | 是 |
| `CommunicationManager.HealCommunicationIni` | 通讯 INI 7 开关补缺 | 是 |
| `FilebackupPage.LoadProjectXmlRows` / `ApplyDeltaView` / 差异审计 | `LoadConfig(false)` / `LoadConfig(reader)` | **否** |

## 补键与一次性迁移的先后（2026-11-06，ADR-086 D8）

工艺 INI 新增键 `TA_ZERO_POSE_MM`（TA 工作零位坐标）走既有 `HealAlgorithmsConfigKeys` 补键，**不新建自愈入口**：
模板镜像来自 `WeldAlgorithmsConfig.SaveProcessIni()`，因此「只增不改 / 幂等零写 / 备份 + 原子替换 / 只读降级不阻断」四条契约自动继承。

⛔ **硬顺序**：`WeldParamManager.ReloadConfig` 内必须是
`MigrateLegacyTorqueTarget` → `MigrateLegacyTaZeroPoseMm` → `HealAlgorithmsConfigKeys`。
补键会以内存默认值 `0` 写出 `TA_ZERO_POSE_MM`；若先补键，迁移侧的 `KeyExists` 判定会恒为真，
现场旧值 `TA_HOME_ZERO_POSE_MM` 将被误判为「工艺页已设定」而永久丢失。迁移只改内存，落盘交给随后的补键链路。

## 相关改造

- `XdocumentReaderWriter(string relativeDirectory, string xmlName, bool createIfMissing = true)`：读取路径传 `false`，禁止自动建空文档。
- `DeltaMotionConfig.SelfHealMissingKeys(bool allowWrite, bool includeTorqueDirection)`：模板来自 `WriteConfigNodes`；`includeTorqueDirection=false` 时移除方向节点。
