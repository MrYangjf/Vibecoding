---
title: ADR-041 焊接参数控制算法分层（抽象基类 + 实现类 + Manager 唯一入口）
date: 2026-09-14
updated: 2026-09-14
tags: [决策, 焊接参数, 算法分层, Manager, 抽象基类, WeldParamControl, ADR-041]
status: accepted
---

# ADR-041 焊接参数控制算法分层（抽象基类 + 实现类 + Manager 唯一入口）

## 状态

已采纳（2026-09-14），同日三次修订：① 轨迹算法纳入 Manager、配置管理并入 Manager、删除 `WeldDataManager`；② 线激光引导配置实例与持久化完全归 Manager 独占（自有 `Config/XML/WeldParamControl.xml`），外部不得持有或回灌配置实例，`SeamGuideSample` 归入 `Algorithms/`。

> ⚠️ **沿革（2026-09-14 同日）**：本决策中的配置类命名与数量已被后续决策取代——~~`SeamGuideConfig`~~ 与 ~~`WeldParamAdjustmentConfig`~~ 两类**当天合并**为单一 `WeldAlgorithmsConfig`（XML 两节名与文件路径不变、存量配置零迁移），Manager 对外改为 `AlgorithmsConfig` 只读属性 + 一对无参 `LoadAlgorithmsConfig()` / `SaveAlgorithmsConfig()`，见 [[decisions/ADR-044-WeldAlgorithmsConfigMerge]]；同日另有 [[decisions/ADR-043-AlgorithmPurityAndRecordIsolation]]（算法只计算、记录走事件）。**本决策的其余结论（抽象基类 + 实现类 + Manager 唯一入口 + 配置持久化只归 Manager）全部继续有效**；下文出现旧类名/旧方法名之处，按 ADR-043 / ADR-044 理解。

## 背景

`WeldParamControl` 模块原以单个 `WeldProcess` 单例承载**全部**职责：数据结构、参数计算公式、焊缝跟踪自适应算法、参数查表算法、折线图数据与完成事件。这带来四个问题：

1. **名实不符**：类名 `WeldProcess` 暗示「流程」，与「流程只在 `WeldParamControlWorkflow` 执行」的定位冲突。
2. **职责混杂**：算法、数据、配置、可观测性四类职责挤在一个类中。
3. **入口分散**：外部既可直接访问 `WeldProcess.Instance.SeamWidthList`，也可调用其算法方法，缺少唯一门面。
4. **Manager 重复**：`WeldDataManager` 与 `WeldParamManager` 并存，均对外暴露 `Instance`，违背「一个 Manager」原则。

用户裁定：
- `WeldParamControl` **管理所有焊接参数和焊接算法**，提供计算公式、接口与配置，**不单独开流程**；
- 算法应「**一个抽象类 + 若干实现类（非单例）+ 一个 Manager 唯一入口**」；
-  Manager 应**统一管理配置**（INI / ConfigHelper / AutoParamHelper），项目其他模块亦如此。

## 决策

1. **删除 `WeldProcess` 类**，模块不再承载任何流程概念。数据结构迁入 `WeldParamData.cs`。
2. **删除 `WeldDataManager` 类**，其参数持久化职责整体并入 `WeldParamManager`。
3. **删除 `SeamTrajectoryBuilder` / `ISeamTrajectoryBuilder`**，轨迹构造算法改为继承 `WeldAlgorithmBase` 的非单例实现 `SeamTrackingAlgorithm`。
4. **抽象基类** `Abstractions/WeldAlgorithmBase.cs`：
   - 公共属性：`Name` / `IsReady`；
   - 公共方法：`LoadConfig(object config)` / `Reset()`。
   - `LoadConfig` 参数为 `object`，实现类按自身配置类型（`AutoParam` / `SeamGuideConfig`）转换。
5. **新增/重命名三个非单例实现类**（`Algorithms/`）：
   - `WeldParamLookupAlgorithm` —— **焊接参数查表调整**：维护焊缝宽度查找表，承载公式与匹配；
   - `WeldParamAdjustmentAlgorithm` —— **焊缝宽度驱动的参数调整**：滑动平均 → 突变判定 → 调查表 → 输出工艺参数、图表与事件（原 `WeldSeamTrackingAlgorithm` 重命名，名实相符）；
   - `SeamTrackingAlgorithm` —— **线激光焊缝几何轨迹跟踪**：线激光结果 + 机器人坐标 → Y 轴 PVT 轨迹点，**只负责计算点，不直接写控制器**。
6. **Manager 单例** `WeldParamManager.cs`：
   - 模块**唯一外部访问入口**；
   - 持有全部算法实现（参数查表、参数调整、轨迹跟踪）；
   - 统一管理配置持久化（`CurrentAutoParamId` / `ConfigHelper` / `AutoParamHelper` / `SwitchConfig` / `AddConfig` 等）；
   - 代理算法公共入口（`TriggerAdjustment` / `FeedSeamTracking` / `TickSeamTracking` / `ResetSeamTracking` 等）；
   - **持有并独占线激光引导配置**：唯一 `SeamGuideConfig` 实例 + 自有配置文件 `Config/XML/WeldParamControl.xml`，对外仅 `SeamGuideConfig` 只读属性与**无参** `LoadSeamGuideConfig()` / `SaveSeamGuideConfig()`。
7. **控制器写入职责归运控工作流**：`MotionControlWorkflow` 负责 PVT 缓冲区管理、`BeginMove` / `ContinueMove` 写入、起止段控制。
8. **流程归属不变**：编排仍在 `WeldParamControlWorkflow`；`TriggerAdjustment()` 保持**无参**契约（ADR-009）。
9. **配置数据类归置**：`SeamGuideConfig` 保留在 `WeldParamControl/` 根目录（配置类，归 Manager 管理）；`SeamGuideSample` 迁入 `Algorithms/`（算法私有输入结构，与 `SeamTrackingAlgorithm` 同命名空间）。
10. **配置实例不得外流**（2026-09-14 第三次修订）：⛔ 外部不得 `new SeamGuideConfig()`、不得持有或回灌配置实例。原 `WeldParamControlWorkflow.SeamGuide` 属性、`SaveSeamGuide()` 方法与其 `_seamGuide` 字段已删除；`SEAM_GUIDE` 段随之从 `WeldParamControlWorkflow.xml` 迁出。

## 目录结构

```
WeldParamControl/
├── WeldParamData.cs                     数据类集合（RobotWeldData / AutoParam / ChartVar / ...）
├── WeldParamManager.cs                  单例 · 唯一外部入口（配置 + 全部算法实现）
├── SeamGuideConfig.cs                   线激光引导配置（标定与修正参数，Manager 独占）
├── Abstractions/
│   └── WeldAlgorithmBase.cs             抽象基类：Name / IsReady / LoadConfig(object) / Reset
└── Algorithms/
    ├── SeamGuideSample.cs               算法私有输入结构（结果 + 机器人坐标 + 时间戳）
    ├── WeldParamLookupAlgorithm.cs      实现 a：参数查表调整（公式 + 三张表）
    ├── WeldParamAdjustmentAlgorithm.cs  实现 b：焊缝宽度驱动的参数调整
    └── SeamTrackingAlgorithm.cs         实现 c：线激光焊缝几何轨迹跟踪（输出 PVT 点）
```

## 后果

- 正面：
  - 模块内「流程」概念收敛到 `WeldParamControlWorkflow` 单一处；
  - 算法按真实语义拆分（参数调整 vs 几何轨迹跟踪），边界清晰；
  - 算法与控制器解耦：算法只出点，运控负责写入；
  - 外部访问收敛为 `WeldParamManager.Instance` 唯一入口，配置与算法不外泄；
  - 实现类非单例，便于测试与未来多实例场景。
- 负面 / 待决：
  - 引用面涉及 `WeldParamControlWorkflow` / `MotionControlWorkflow` / `AutoParamForm` / `ConfigForm` / `ParamConfigPage` / `csproj` / 注释，已同步迁移；
  - `WeldProcessCompletedEventArgs` 与 `WeldProcessCompleted` 事件名保留历史命名，未随类名改造；
  - `CurrentRobotX` 仍无真实来源，保持兼容返回 0，待通信层对接 KUKA 真实坐标。
- 约束：
  - ⛔ 不得再向 `WeldParamManager` 或算法实现类中加入流程编排逻辑；
  - ⛔ 不得恢复 `WeldProcess` / `WeldDataManager` / `SeamTrajectoryBuilder`；
  - ⛔ 不得让外部绕过 Manager 直接访问算法实现；
  - ⛔ 外部不得 `new SeamGuideConfig()` 或持有/回灌配置实例，配置实例与持久化只归 `WeldParamManager`；
  - `TriggerAdjustment()` 必须保持无参（ADR-009）；
  - 轨迹算法只计算 PVT 点，不得直接调用 `IPVTMotion`。

## 相关

- [[modules/WeldParamControl]] — 模块说明（现行结构）
- [[api/WeldParamManager]] — Manager 唯一入口 API
- [[api/WeldParamAdjustmentAlgorithm]] — 参数调整算法 API
- [[api/SeamTrackingAlgorithm]] — 焊缝几何轨迹跟踪算法 API
- [[api/WeldParamControlWorkflow]] — 流程编排（计算后下发机器人）
- [[api/MotionControlWorkflow]] — 控制器写入与轨迹点消费方
- [[decisions/ADR-009-WorkflowAsAdjustmentDriver]] — 工作流作为调整主驱动（`TriggerAdjustment` 无参）
- [[decisions/ADR-040-SeamGuideTrajectoryBuilder]] — 线激光引导 Y 轴轨迹构造（已演进为 `SeamTrackingAlgorithm`）
- [[decisions/ADR-022-CodeSimplificationStandard]] — 代码精简规范
- [[decisions/ADR-023-WorkflowResponsibilityBoundary]] — 流程与对象权责边界
