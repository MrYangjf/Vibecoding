---
title: ADR-047 记录实现类文件自包含（游离文件吸收 + WeldParamAdjustRecord 改名 + SmartRay 链删除）
date: 2026-09-14
tags: [决策, 产品记录, ProductFileControl, 文件自包含, 改名, ADR-047]
status: accepted
---

# ADR-047 记录实现类文件自包含（游离文件吸收 + 改名 + SmartRay 链删除）

## 状态

已采纳（2026-09-14）。

## 背景

[[decisions/ADR-046-ProductRecordModuleRefactor]] 落地后，`ProductFileControl/` 下仍存留 4 个不属三层架构（抽象层 / Records 实现层 / Manager）任一层级的游离文件：`RecordFileStore.cs` / `RecordFrame.cs` / `WeldActionRecord.cs` / `SmartRayConverter.cs`。用户 2026-09-14 裁定：**Implementations/Records 目录只留实现类，配置与数据结构并入各自实现类文件**（与当日 Comm 模块同原则）；并纠正命名——`SeamAdjustRecord` 语义错误，该记录实际是**根据焊缝（宽度等特征）调整激光功率、送丝速度等焊接参数时**的记录。

经 Grep 消费链核查：`SmartRayConverter` 唯一引用点 `SeamTrackRecord.AddSmartRayFrame`（及 Manager 透传 `AddSmartRayFrame`）在模块外 **0 调用**——整条 SmartRay 转换链为死代码。

## 决策

1. **同文件吸收**（对外 API 零变化）：
   | 游离文件 | 去向 |
   |---|---|
   | `RecordFileStore.cs` | 并入 `Records/SeamTrackRecord.cs`（internal sealed，会话/.pDat/.ply/.tmp/混淆回溯机制归焊缝追踪记录所有） |
   | `RecordFrame.cs` | 并入 `Records/SeamTrackRecord.cs`（public 保持——`GetAllFrames()` 返回类型） |
   | `WeldActionRecord.cs` | 并入 `Records/WeldParamAdjustRecord.cs`（public 保持——DataReviewerPage 回溯消费） |
   | `SmartRayConverter.cs` | **整链删除**（Converter + `SeamTrackRecord.AddSmartRayFrame` + `Manager.AddSmartRayFrame`，0 消费） |

2. **改名**：`SeamAdjustRecord` → **`WeldParamAdjustRecord`**；`SeamAdjustItem` → **`WeldParamAdjustItem`**（对齐 ADR-008 术语 `WeldParamAdjust` 与配置节 `WELD_PARAM_ADJUST`）。记录类 Name 属性、类头注释同步。

3. **范围外不动**：`WeldParamManager` 侧事件 `AdjustmentRecordRequested` / `WeldAdjustmentRecordEventArgs` 命名保持（跨模块最小变更）；ADR-008 双记录落同一 `.pDat` 机制原样搬运，不重设计。

## 目录结构（变更后）

```
ProductFileControl/
├── Abstractions/
│   └── ProductRecordBase.cs        ← 抽象层（RecordItem + SeamTrackItem/WeldParamAdjustItem/WeldResultItem）
├── Records/
│   ├── SeamTrackRecord.cs          ← 焊缝追踪记录 + RecordFrame + RecordFileStore（自包含）
│   ├── WeldParamAdjustRecord.cs    ← 焊接参数调整记录 + WeldActionRecord（自包含）★改名
│   └── WeldResultRecord.cs         ← 成功/产品信息记录（数据库）
└── ProductFileRecordManager.cs     ← 单例 Manager · 唯一对外入口
```

## 后果

- 正面：目录无游离文件，每个实现类文件自包含（数据结构随类走）；死代码 SmartRay 链清除；命名与 ADR-008 术语一致。
- 负面 / 沿革：`SeamAdjustRecord` / `SeamAdjustItem` / `RecordFileStore.cs`（文件名）/ `RecordFrame.cs` / `WeldActionRecord.cs` / `SmartRayConverter.cs` 旧名在 ADR-046 与日志中仍会出现（ADR-046 已加沿革横幅；drift REMOVED/RENAMED 表已登记）。
- 约束：
  - ⛔ Records/ 下不得再新开独立的数据结构/配置文件——数据结构并入对应实现类文件（ADR-042 实现层纪律的文件维度延伸）；
  - ⛔ RecordFileStore 仍为 internal，外部不得绕过 Manager 访问（H6 不变）。

## 相关

- [[decisions/ADR-046-ProductRecordModuleRefactor]] — 三层结构来源（本决策为其文件维度收尾）
- [[decisions/ADR-008-WeldActionRecord]] — WeldParamAdjust 术语与双记录设计
- [[decisions/ADR-042-ModuleOrganizationPatternStandard]] — 模块组织范式
- [[modules/ProductFileManager]] — 模块现行真相源
