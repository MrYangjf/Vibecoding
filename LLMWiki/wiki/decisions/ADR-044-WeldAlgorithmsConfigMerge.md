---
title: ADR-044 焊接算法配置合一（SeamGuideConfig + WeldParamAdjustmentConfig → WeldAlgorithmsConfig）
date: 2026-09-14
tags: [决策, 配置合一, 算法分层, WeldParamControl, Manager, ADR-044]
status: accepted
---

# ADR-044 焊接算法配置合一（SeamGuideConfig + WeldParamAdjustmentConfig → WeldAlgorithmsConfig）

## 状态

已采纳（2026-09-14）。

## 背景

[[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]] 决策 5 为「参数调整算法」新增了 `WeldParamAdjustmentConfig`（节 `WELD_PARAM_ADJUST`），与既有的 `SeamGuideConfig`（节 `SEAM_GUIDE`）**并列成两个配置类**，同存 `Config/XML/WeldParamControl.xml`、共用同一个 `XdocumentReaderWriter`。

用户 2026-09-14 指出：「两个算法配置合并成一个文件吧，命名为 `WeldAlgorithmsConfig`。」

复查现状：

| 项 | 合并前 | 问题 |
|---|---|---|
| 配置类 | `SeamGuideConfig`（13 项）+ `WeldParamAdjustmentConfig`（3 项），**两类两文件** | 同属一个模块、同一份 XML、同一个 reader，却要维护两条平行的类/方法线 |
| Manager 配置管理 | 4 个无参方法（`LoadAdjustmentConfig` / `SaveAdjustmentConfig` / `LoadSeamGuideConfig` / `SaveSeamGuideConfig`）+ 2 个只读属性 | 4 个方法里两两对称，语义重复；保存时是「两个方法各写一半」 |
| 算法侧 | 两算法各持一个**不同类**的 `_config` | 配置契约分裂，Manager 需两次分发 |

三处均无外部消费者（`SectionName` 虽 `public` 但仅本文件内引用，4 个方法零外部调用）——合并无兼容性负担。

## 决策

**粒度裁定（用户 2026-09-14 选定「单类合并」）**：合并为**一个类、一个文件**，而非「一文件多类」或「容器类 + 子对象」。

1. **新增 `WeldParamControl/WeldAlgorithmsConfig.cs`**，单一 `public class WeldAlgorithmsConfig`，承载两节全部 16 项参数（线激光引导 13 项 + 参数调整 3 项）。

2. **XML 节名与文件路径不变**：仍为 `SEAM_GUIDE` 与 `WELD_PARAM_ADJUST` 两节，仍在 `Config/XML/WeldParamControl.xml`。**存量配置文件零迁移**——合并只动代码，不动数据。
   - 公开常量 `SeamGuideSection = "SEAM_GUIDE"` / `AdjustmentSection = "WELD_PARAM_ADJUST"`（取代原两类各自的 `SectionName`）。

3. **一个 `LoadConfig(reader)` / 一个 `SaveConfig(reader)` 覆盖两节**：内部拆为私有 `LoadSeamGuide` / `SaveSeamGuide` / `LoadAdjustment` / `SaveAdjustment`，`public` 面收敛为一对。

4. **Manager 收敛为「一实例 · 一属性 · 一对方法」**：
   - 字段 `private WeldAlgorithmsConfig _algorithmsConfig;`（Manager 独占），构造时由 `LoadAlgorithmsConfig()` 创建并载入；
   - 只读属性 `AlgorithmsConfig`（取代原 `SeamGuideConfig` / `AdjustmentConfig` 两属性）；
   - 无参 `LoadAlgorithmsConfig()` / `SaveAlgorithmsConfig()`（取代原 4 个方法，均零外部消费者）。
   - `LoadAlgorithmsConfig()` 把**同一个实例**分发给 `WeldParamAdjustmentAlgorithm` 与 `SeamTrackingAlgorithm`（两算法只读消费）。

5. **算法侧类型随之收敛**：`WeldParamAdjustmentAlgorithm.Config` / `SeamTrackingAlgorithm.Config` 均为 `WeldAlgorithmsConfig`（`SetConfig` / `LoadConfig(object)` 转型同步）。
   - ⛔ 算法**只读消费**，不得持有 reader、不得落盘（承接 ADR-043 的算法纯净性）。
   - ⛔ 外部不得 `new WeldAlgorithmsConfig()`、不得持有或回灌实例。

6. **受影响的外部只读引用**：`MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` 两处 `WeldParamManager.Instance.SeamGuideConfig.{MinRemainBuffer, DefaultFrameSeconds}` → `AlgorithmsConfig.*`。

7. **删除两个旧配置类文件**：`SeamGuideConfig.cs`、`WeldParamAdjustmentConfig.cs`；csproj 两条 `<Compile Include>` 换为新的一条。

## 目录结构（变更后）

```
WeldParamControl/
├── WeldParamData.cs                     数据类集合（含记录请求事件参数）
├── WeldParamManager.cs                  单例 · 唯一外部入口（配置 + 全部算法实现 + 记录事件透传）
├── WeldAlgorithmsConfig.cs              焊接算法配置（SEAM_GUIDE + WELD_PARAM_ADJUST 两节合一）★合并
├── Abstractions/
│   └── WeldAlgorithmBase.cs             抽象基类：Name / IsReady / LoadConfig(object) / Reset
└── Algorithms/
    ├── SeamGuideSample.cs               算法私有输入结构
    ├── WeldParamLookupAlgorithm.cs      实现 a：参数查表调整
    ├── WeldParamAdjustmentAlgorithm.cs  实现 b：参数调整（只计算 + 发记录请求事件）
    └── SeamTrackingAlgorithm.cs         实现 c：线激光几何轨迹跟踪
```

配置仍分两节（`Config/XML/WeldParamControl.xml`，**格式不变**）：

```xml
<Root>
  <SEAM_GUIDE>          ...13 项线激光引导参数...   </SEAM_GUIDE>
  <WELD_PARAM_ADJUST>   ...3 项参数调整参数...       </WELD_PARAM_ADJUST>
</Root>
```

## 后果

- 正面：
  - 配置类数量 2 → 1，文件数 2 → 1，Manager 配置方法 4 → 2、属性 2 → 1，对称重复彻底消除；
  - **配置契约单一化**：两算法消费同一类型，Manager 一次载入一次分发；
  - **存量配置零迁移**（节名与文件路径不变），现场 `Config/XML/WeldParamControl.xml` 无需改动；
  - 合并粒度判据被固化到 [[lessons/AlgorithmControlRecordIsolation]]：**配置类划分跟随「谁写盘」而非「字段分几组」**。
- 负面 / 待决：
  - 一个类承载 16 项参数，比拆分时略长（约 270 行）；若后续某节参数膨胀到独立生命周期，需重新评估拆分；
  - ~~旧类名 `SeamGuideConfig` / `WeldParamAdjustmentConfig`~~ 在历史 ADR / 日志中仍会出现，检索时以本条与新页为准。
- 约束：
  - ⛔ 外部不得 `new WeldAlgorithmsConfig()`、不得持有或回灌配置实例；只经 `Manager.AlgorithmsConfig` 只读访问；
  - ⛔ 配置实例与读写器仍只归 `WeldParamManager` 独占（承接 ADR-041 / ADR-043）；
  - ⛔ 算法内不得出现持久化符号（承接 ADR-043）。

## 相关

- [[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]] — 算法纯净性与记录职责隔离（本决策是其配置部分的「合一」收紧）
- [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] — 算法分层（配置持久化只归 Manager）
- [[decisions/ADR-042-ModuleOrganizationPatternStandard]] — 模块组织范式
- [[standards/ModuleOrganizationPattern]] — §七检查清单
- [[lessons/AlgorithmControlRecordIsolation]] — 配套踩坑记录（§5 已补「多节可归一类」判据）
- [[api/WeldParamManager]] — Manager 唯一入口（`AlgorithmsConfig` + 一对 Load/Save）
- [[api/WeldParamAdjustmentAlgorithm]] — 参数调整算法（`Config` 类型已改）
- [[api/SeamTrackingAlgorithm]] — 轨迹跟踪算法（`Config` 类型已改）
- [[modules/WeldParamControl]] — 模块说明
