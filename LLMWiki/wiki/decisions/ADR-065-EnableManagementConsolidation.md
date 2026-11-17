---
title: ADR-065 启用管理收口与待补充区清理
date: 2026-10-13
updated: 2026-10-13
tags: [ADR, UI, 启用管理, 工艺开关, 待补充清理, 快捷设置]
status: accepted
---

# ADR-065：启用管理收口与待补充区清理

> 快捷设置页的「启用管理」区成为**工艺开关的唯一收口**；「待补充」占位区整体删除、转由 wiki 跟踪；
> 原「快捷调试」块按业主裁定拆分（搬到 Tracking 指令区 / 删除）。

## 背景

业主提出四点要求，核心是**职责分层**：
1. 工艺开关（跟踪启用、自动对焦启用、摆动启用等）集中在快捷设置的启用模块
2. 系统开关（追踪方式、追踪算法、对焦算法等）应放系统设置对应模块
3. 各 Panel 内部改用 GridPanel/4 列布局
4. 「待补充」区已补充，删除占位

## 决策

### 一、启用管理区收口 6 个工艺开关

`tlpProcessDebug` 改为 **4 列网格**（标签 + 开关 + 标签 + 开关），共 6 个开关：

| 开关 | 配置 | 语义 |
|---|---|---|
| `swEnableSeamTrace` | `EnableSeamTrace` | 焊缝跟踪 |
| `swEnableGalvoWeaveQuick` | `EnableGalvoWeave` | 振镜摆动（**与激光工艺页双向同步**） |
| `swEnableAdapt` | `EnableGuide` | 自适应引导 |
| `swEnableMonotonic` | `EnableMonotonicConstraint` | 单调约束（焊缝跟踪子项） |
| `swEnableWireAlign` | `EnableWireAlign` | 光丝对中 |
| `swEnableTempCtrl` | `EnableTempCtrl` | 温度控制 |

⛔ **不建重复开关**：`swEnableAdapt` 即 `EnableGuide`，不再建 `swEnableGuide`（自适应工艺页的 `selFlowEnableGuide` 下拉是既有第二入口，保留不动）。
⛔ **不建无配置的开关**：曾设想 `swEnableSpotAlign`，grep 无对应配置 ⇒ 不建。

### 二、⛔ 工艺开关不再依赖「保存按钮」，改为**即改即存**

原实现靠 `btnSaveProcessDebug` / `btnReadProcessDebug` 统一写回。这两个按钮随快捷调试块删除后，
**必须给每个开关补 `CheckedChanged` 订阅**，否则改了不生效（本轮自查抓到的真实缺陷）。
回填期用 `_loadingProcessEnable` 静默，防加载时误触发落盘。

### 三、振镜摆动双向同步（两侧异名）

| 侧 | 控件 | 处理器 |
|---|---|---|
| 快捷设置页（启用管理区） | `swEnableGalvoWeaveQuick` | `swEnableGalvoWeaveQuick_CheckedChanged` |
| 激光工艺页（振镜区） | `swEnableGalvoWeave` | `swEnableGalvoWeave_CheckedChanged` |

⛔ **不可同名**：同一窗体里两个同名控件会 CS0101；且两个同名处理器曾造成重复定义（本轮自查抓出）。
两侧用 `_loadingProcessEnable` / `_loadingGalvoUi` **互斥防重入**。

### 四、原「快捷调试」块按业主裁定拆分

| 原控件 | 裁定 | 处置 |
|---|---|---|
| `chkLockYCalib`（Y轴回标定位置） | 是 **Tracking 指令区**的 | **搬到** `panelQuickTracking` |
| `chkLockSpotCalib`（光斑回标定位置） | **没有这个指令**（暂无单独让光斑回标定位的逻辑） | **删除** |
| `chkLockWirePos`（送丝结构锁定位置） | **就是 TA_Pose** | **删除**（TA 参数区已有 `TA_Pose1/Pose2`） |

⛔ **删 UI 不删配置**：`LockYCalib` / `LockSpotCalib` / `LockWirePos` 三个配置项保留在 `WeldAlgorithmsConfig`，
避免破坏既有 INI 文件与轴表通道。

### 五、「待补充」占位区整体删除

| 控件 | 原内容 | 处置 |
|---|---|---|
| `lblWireAlignTip` | 「待补充：送丝压力值 / 对焦光斑大小设定 / 送丝轴位置锁定 / 对焦轴位置锁定」 | **删除**（连同其宿主 `panelWireAlign`） |
| `lblOpticsTip`（系统设置页） | 「待补充：送丝力矩电机配置参数 / 对焦电机配置参数 / 光斑大小·送丝轴标定参数」 | **本轮不删**（业主后续补充中） |

> 📌 删除理由：区域与范围已在 P1 §4.2 划定清楚，后续由 wiki 跟踪补充清单，**UI 上不再放占位文案**。
> ⚠️ 删除前已 grep 确认：光丝对中的阈值（警告 0.1mm / 报警 0.3mm）在配置中**无载体**，
> 相关参数（`SpotCalibPosMm`/`WireLockPosMm`/`LaSpot1Mm`/`LaSpot2Mm`）已存在于 `WeldAlgorithmsConfig`。

## 后果

- **正面**：工艺开关单一入口、即改即存；职责分层清晰（工艺开关 vs 系统开关）；去掉占位文案
- **负面**：每个开关都触发一次 `SaveAlgorithmsConfig()`（INI 落盘），频繁切换有 IO 开销 —— 可接受（开关切换是低频操作）
- **中性**：`EnableMonotonicConstraint` 首次有 UI 入口

## 验证

- **几何实测**：6 开关 3 行 × 2 列，`y=45/97/149`、`x=168/428`，右边缘 657 ≤ 660，全可见
- **回归**：仅 `ProcessControlPage.Designer.cs` + `ProcessControlPage.cs` 两个文件，零越界

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[decisions/ADR-063-CommandZoneRadioExclusivity]] —— 指令区 Radio 化（TA/LA 指令区）
- [[decisions/ADR-064-TaConfigLayeredConsolidation]] —— TA 配置分层收口
- [[api/ProcessControlPage]] · [[project/ReviewOptimization-P1-StructureDesign]] §4.2
- [[lessons/StaticVerifierJudgements]] §0.9e（四件套）
