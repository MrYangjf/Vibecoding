---
title: WeldDataManager API 参考
date: 2026-07-02
tags: [API, 焊接, 自动调整参数, 配置管理]
source: raw/skills/02-Development/WeldProcessSpecialist.md
---

# WeldDataManager API 参考

> 焊接数据管理器（单例）。
> 集中管理自动调整参数：运行时 `AutoParam`、分段数据表 `AutoParamManager`、配置映射 `ConfigManager`、当前配置标识 `CurrentAutoParamId`。
> `CurrentAutoParamId` 通过 `Config/INI/WeldData.ini` 持久化。

## 核心类

```csharp
public class WeldDataManager
{
    public static WeldDataManager Instance { get; }

    public AutoParam mAutoParam { get; private set; }
    public AutoParamManager mAutoParamManage { get; private set; }
    public ConfigManager mConfigManager { get; private set; }
    public string CurrentAutoParamId { get; private set; }

    public void SwitchConfig(string configId);
    public void SaveCurrentAutoParam();
    public AutoParam AddConfig(string configId);
    public bool DeleteConfig(string configId);
}
```

## 职责分层

```
WeldDataManager
├── mAutoParam          // 运行时当前 AutoParam 对象（内存实时使用）
├── mAutoParamManage    // AutoParamManager：按 identityInfo 管理四张分段数据表
├── mConfigManager      // ConfigManager：管理 AutoParam 基础配置与 JSON 映射
└── CurrentAutoParamId  // 当前选中的配置标识（INI 持久化）
```

| 层级 | 成员 | 职责 |
|------|------|------|
| 运行时 | `mAutoParam` | 内存中实时使用的焊接工艺参数 |
| 分段数据 | `mAutoParamManage` | 按 `identityInfo` 存储焊缝宽度/送丝速度/激光功率/焊接速度的分段数据表，支持手动微调 |
| 配置映射 | `mConfigManager` | 存储 AutoParam 基础信息（类型、焊丝材质、板材、时间、标识）与 JSON 对象的映射，用于列表展示与切换 |
| 当前标识 | `CurrentAutoParamId` | 当前激活的配置名，写入 `Config/INI/WeldData.ini` |

## 初始化流程

1. 加载 `Config/INI/WeldData.ini`，若不存在则自动创建
2. 读取 `CurrentAutoParamId`，缺失或为空时设为 `"DefaultParam"`
3. 构造 `AutoParamManager` 和 `ConfigManager`
4. **确保 DefaultParam 配置存在**：
   - 若 `ConfigManager` 无 DefaultParam，则创建 `AutoParam.CreateDefault()` 并写入
   - 若 `AutoParamManager` 无 DefaultParam 表，则 `SelectTable(defaultParam)` 创建并保存默认分段数据
5. 加载 `CurrentAutoParamId` 对应的配置，设置 `WeldProcess.Instance.CurrentAutoParam`

## 默认配置保护

- `AutoParam.DefaultIdentity` 常量值为 `"DefaultParam"`（避免使用 SQLite 保留关键字 `Default` 作为表名）
- `AutoParam.CreateDefault()` 返回标识为 `"DefaultParam"` 的默认实例
- `AutoParam.IsDefault` 属性判断当前实例是否为默认配置
- `WeldDataManager.DeleteConfig` 中：
  - `configId == "DefaultParam"` 返回 `false`
  - `configId == CurrentAutoParamId` 返回 `false`

## 配置切换

```csharp
WeldDataManager.Instance.SwitchConfig("NewConfig");
```

切换时会：
1. 校验配置存在性
2. 更新 `CurrentAutoParamId`
3. 写入 INI 文件
4. 从 `ConfigManager` 加载 `AutoParam`
5. 调用 `AutoParamManager.SelectTable` 加载分段数据
6. 同步设置 `WeldProcess.Instance.CurrentAutoParam`

## 新增配置

```csharp
WeldDataManager.Instance.AddConfig("NewConfig");
```

新增配置并自动切换为当前配置，同时创建对应分段数据表。

## 保存当前配置

```csharp
WeldDataManager.Instance.SaveCurrentAutoParam();
```

将 `mAutoParam` 序列化为 JSON 后保存/更新到 `ConfigManager`。

## 使用规范

- UI 页面（`ParamConfigPage`、`ConfigForm`、`AutoParamForm`）通过 `WeldDataManager.Instance` 访问自动调整参数
- 禁止直接修改 `CurrentAutoParamId`，必须通过 `SwitchConfig` 或 `AddConfig`
- `mAutoParam` 的字段修改后，需要调用 `SaveCurrentAutoParam()` 持久化到 `ConfigManager`
- 分段数据修改后，需要调用 `mAutoParamManage.UpdateParamValues()`

## 相关页面

- [[modules/WeldParamControl]] — 焊接工艺模块
- [[modules/SqlLiteDatabase]] — AutoParamManager / ConfigManager
- [[api/GlobalCommData]] — 全局事件总线（不再管理自动调整参数）
- [[decisions/ADR-002-CS73-Constraint]] — C# 7.3 语法约束
- [[guides/Config-Data-Tools]] — SQLite 保留关键字不能用作表名
