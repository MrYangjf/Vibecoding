---
title: WeldDataManager API 参考（已并入 WeldParamManager）
date: 2026-07-02
updated: 2026-09-14
tags: [API, 焊接, 自动调整参数, 配置管理, 已废弃, ADR-041]
source: AdaWeldSystem/WeldParamControl/WeldParamManager.cs
---

# WeldDataManager API 参考（已并入 WeldParamManager）

> ⛔ **本类已删除**（2026-09-14 ADR-041 第二次修订）。
> 原 `WeldDataManager` 承担的参数持久化职责（`AutoParam` / `AutoParamHelper` / `ConfigHelper` / `CurrentAutoParamId` / INI）
> 已全部并入 [[api/WeldParamManager]]，由 Manager 统一管理配置。
> 本页仅作沿革与迁移参考。

---

## 沿革

| 时间 | 状态 | 说明 |
|---|---|---|
| 2026-07-02 | 创建 | 作为 WeldParamControl 模块的参数持久化入口，管理 `AutoParam` / `AutoParamHelper` / `ConfigHelper` |
| 2026-09-14 | 删除 | 与「一个 Manager」原则冲突，整体并入 `WeldParamManager` |

---

## 迁移对照

| 原 `WeldDataManager` 调用 | 现调用 |
|---|---|
| `WeldDataManager.Instance.mAutoParam` | `WeldParamManager.Instance.CurrentAutoParam` |
| `WeldDataManager.Instance.mAutoParamManage` | `WeldParamManager.Instance.AutoParamHelper` |
| `WeldDataManager.Instance.mConfigManager` | `WeldParamManager.Instance.ConfigHelper` |
| `WeldDataManager.Instance.CurrentAutoParamId` | `WeldParamManager.Instance.CurrentAutoParamId` |
| `WeldDataManager.Instance.SwitchConfig(configId)` | `WeldParamManager.Instance.SwitchConfig(configId)` |
| `WeldDataManager.Instance.AddConfig(configId)` | `WeldParamManager.Instance.AddConfig(configId)` |
| `WeldDataManager.Instance.DeleteConfig(configId)` | `WeldParamManager.Instance.DeleteConfig(configId)` |
| `WeldDataManager.Instance.SaveCurrentAutoParam()` | `WeldParamManager.Instance.SaveCurrentAutoParam()` |
| `WeldDataManager.Instance.SaveCurrentProfile()` | `WeldParamManager.Instance.SaveCurrentProfile()` |
| `WeldDataManager.Instance.ReloadCurrentParamValues()` | `WeldParamManager.Instance.ReloadCurrentParamValues()` |
| `WeldDataManager.Instance.LoadProfileIntoLookupTable(identityInfo)` | `WeldParamManager.Instance.LoadProfileIntoLookupTable(identityInfo)` |

---

## 原职责分层（归档）

```
WeldDataManager
├── mAutoParam          // 运行时当前 AutoParam 对象
├── mAutoParamManage    // AutoParamHelper：按 identityInfo 管理四张分段数据表
├── mConfigManager      // ConfigHelper：管理 AutoParam 基础配置与 JSON 映射
└── CurrentAutoParamId  // 当前选中的配置标识（INI 持久化）
```

---

## 相关页面

- [[api/WeldParamManager]] — 参数、算法与配置持久化的唯一入口（替代本页）
- [[modules/WeldParamControl]] — 焊接工艺模块
- [[modules/SQLiteDatabase]] — AutoParamHelper / ConfigHelper
- [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] — 删除本类的决策
