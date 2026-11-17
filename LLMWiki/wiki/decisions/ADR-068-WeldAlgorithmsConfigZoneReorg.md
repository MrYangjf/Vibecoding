---
title: ADR-068 WeldAlgorithmsConfig 按 UI 4 分区重组（配置块重排 + 分区读写接口 + SeamWidthSource 派生化）
date: 2026-10-14
updated: 2026-10-14
tags: [ADR, 配置架构, WeldAlgorithmsConfig, 分区读写, AlgorithmsZone, SeamWidthSource, EnableSpotWidthFollow, WeldParamManager, ProcessControlPage, SystemControlPage]
status: accepted
---

# ADR-068：WeldAlgorithmsConfig 按 UI 4 分区重组（配置块重排 + 分区读写接口 + SeamWidthSource 派生化）

> 业主裁定：`WeldAlgorithmsConfig`（65 属性）配置代码块按 **UI 界面 4 个分区**重组，确保 **UI 面板与配置代码块一一对应**，并提供**分区粒度**的 Load/Save 接口。
> 同轮裁定：`SeamWidthSource` 改为**只读派生属性**，由新开关 `EnableSpotWidthFollow` 控制其值，删除 INI 键 `SEAM_WIDTH_SOURCE` 的读写逻辑。

## 背景：重组前的错位

- 配置属性**按历史追加顺序堆放**（历轮 ADR 各自追加），与 UI 四个分区（系统设置页 / 工艺快捷设置页 / 自适应面板 / 工艺设定值区）**无对应关系**——找某个 UI 控件的配置项要全文搜索。
- 落盘接口只有**全量** `LoadAlgorithmsConfig`/`SaveAlgorithmsConfig`，任一分区保存都全量写两文件（XML+INI），语义粗糙。
- `SeamWidthSource` 是可写枚举属性 + 独立 INI 键，但其取值实际上只由「是否启用光斑宽度跟随」决定——**两个开关表达一个语义**，且系统设置页与快捷设置页各有一个入口，违反唯一入口纪律（ADR-065 同款问题）。

## 决策

### 一、配置代码块按 UI 4 分区重排（净行为不变）

新增分区枚举，配置属性按四区重新排块（**只动代码块顺序与注释，不改属性名、不改 INI/XML 键、不改默认值**）：

| 分区 | 枚举值 | 对应 UI |
|---|---|---|
| ① 系统设置 | `AlgorithmsZone.System` | SystemControlPage |
| ② 工艺快捷 | `AlgorithmsZone.Quick` | ProcessControlPage 快捷设置页 |
| ③ 自适应 | `AlgorithmsZone.Adapt` | 自适应面板 |
| ④ 工艺设定值 | `AlgorithmsZone.Preset` | 工艺设定值区（TA/LA 参数区等） |

### 二、分区粒度读写接口

```csharp
// 四对分区方法（总入口内部调用，亦可单独调用）
LoadZoneXml(AlgorithmsZone) / SaveZoneXml(AlgorithmsZone) // XML 轨：Algorithm_XML\WeldParamControl.xml
LoadZoneIni(AlgorithmsZone) / SaveZoneIni(AlgorithmsZone) // INI 轨：Algorithm_INI\WeldParamControlAlgorithm.ini

// 总入口保持签名不变，内部改为按区顺序调分区方法（净行为不变）
LoadConfig / SaveConfig / LoadProcessIni / SaveProcessIni
```

落盘分流沿用 [[decisions/ADR-033-ConfigArchitectureStandard]]：XML（设备几何/标定）+ INI（流程阈值/开关/节拍）。

### 三、SeamWidthSource 派生化

> ⚠️ **2026-10-15 演进**：本节「新开关 `EnableSpotWidthFollow`」条款已被 [[decisions/ADR-070-GalvoWeaveAsWidthSource]] **推翻**——
> 业主裁定「光斑宽度跟随」与「启用振镜摆动」实为一个意思（光斑宽度不可调，真正变化的是振镜摆幅宽度），
> `EnableSpotWidthFollow` / `ENABLE_SPOT_WIDTH_FOLLOW` 已删除并入 `EnableGalvoWeave`；
> 「`SEAM_WIDTH_SOURCE` 独立键停用 + 只读派生」的结论仍然有效，仅**派生源**换为 `EnableGalvoWeave`。

```csharp
// ~~旧（2026-10-14）：值由新开关决定~~
// public bool EnableSpotWidthFollow { get; set; } // ⚠️ 已被 ADR-070 删除
// public SeamWidthSource SeamWidthSource =>
// EnableSpotWidthFollow ? SeamWidthSource.Laser : SeamWidthSource.Manual;
// 现行（2026-10-15 ADR-070）：
public SeamWidthSource SeamWidthSource =>
 EnableGalvoWeave ? SeamWidthSource.Laser : SeamWidthSource.Manual;
```

- ⛔ 删除 INI 键 `SEAM_WIDTH_SOURCE` 的读写逻辑（**仍然有效**）。
- ~~**唯一入口裁定**：`EnableSpotWidthFollow` 的 UI 入口归**①系统设置页**（新增开关控件）。~~
 ⚠️ 已被 [[decisions/ADR-070-GalvoWeaveAsWidthSource]] 演进：无独立开关，振镜摆动开关即来源开关（②快捷区 + 激光工艺页双同步）。

### 四、分区归属裁定（2026-10-14 业主确认）

| 配置项 | 归属 | 说明 |
|---|---|---|
| `ManualSeamWidthMm` / `SpotWidthGain` / `ParamOutputHz`（光斑宽度来源三项） | **③ 自适应** | 跟随自适应算法消费 |
| `EnableGuide` | **② 工艺快捷** 唯一入口 | 系统设置页对应选择控件**删除**（ADR-065 唯一入口纪律延续） |
| `EnableMonotonicConstraint`（轨迹点单调约束） | ~~**① 系统设置** 唯一入口~~ ⚠️ **2026-10-19 已被 [[decisions/ADR-072-FullChainLayoutAndSplitPane]] 六轮演进推翻**：唯一 UI 入口随「⑤工艺输出」区迁往**工艺设置页·自适应区**（selParamMono 下拉，收编 WeldParamAdjustmentAlgorithm facade）；**落盘分区仍为①System 不变**（唯一入口纪律本身仍有效，只换承载页） | ~~工艺快捷设置页对应开关控件删除~~（快捷页无控件结论仍成立） |

### 五、消费方改动

- **WeldParamManager.cs**：新增 `SaveAlgorithmsZone(AlgorithmsZone)` 分区落盘接口（透传至配置类分区方法）。
- **SystemControlPage.cs/.Designer.cs**：新增 `EnableSpotWidthFollow` 开关 UI；删除 `EnableGuide` 选择控件。
- **ProcessControlPage.cs**：删除 `EnableMonotonicConstraint` 开关控件。

## 必要说明（有意保留，记录在案）

| 项 | 说明 |
|---|---|
| `BtnSaveAlgoThresh` 双区落盘 | 为兼容现有编辑范围（阈值横跨两区）采用双区落盘，属**必要处理** |
| 4 处即改即存路径暂保留全量保存 | 净行为不变原则下本轮不扩散改动，待后续迭代切分区保存 |

## 后果

- **正面**：UI 面板 ↔ 配置代码块一一对应，可按分区独立读写；光斑宽度来源双开关合一；两个跨页重复入口收敛为唯一入口。
- **负面**：`WeldAlgorithmsConfig` 属性总数不变（65 个），ADR-066 遗留的「三类拆分」仍未做（需业主确认粒度）。
- **中性**：存量 INI/XML 文件中的 `SEAM_WIDTH_SOURCE` 键不再被读写（残留无害）；`EnableGuide` 系统设置页控件消失（功能不变，入口移至快捷设置页——此项实为恢复 ADR-065 既有语义）。

## 验证

- **静态校验 33/33 PASS**（含分区枚举四区齐备、四对分区方法读写闭环、总入口内部调用链、SeamWidthSource 只读派生、SEAM_WIDTH_SOURCE 键清除、EnableGuide/EnableMonotonicConstraint 控件删净、SaveAlgorithmsZone 透传链）。
- ⚠️ 沙箱无编译器：静态校验 ≠ 编译通过，上机编译需业主 VS 确认。
- **回归**：4 改（WeldAlgorithmsConfig / WeldParamManager / SystemControlPage×2 / ProcessControlPage），零越界、净行为不变。

## 背景

（待补：本决策要解决什么问题）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[decisions/ADR-067-LATaSettingsSemanticRework]] —— 同日姊妹轮（LA/TA 语义重构，其参数区保存走本 ADR 的 `SaveAlgorithmsZone(Preset)`）
- [[decisions/ADR-033-ConfigArchitectureStandard]] —— XML/INI 双轨落盘底座
- [[decisions/ADR-066-ThreeLayerConvergence]] —— 配置层归位前置（本轮为其「65 属性拆分」遗留的前置铺垫）
- [[decisions/ADR-065-EnableManagementConsolidation]] —— 唯一入口纪律来源
- [[modules/WeldParamControl]] · [[api/WeldParamManager]] · [[api/SystemControlPage]] · [[api/ProcessControlPage]] · [[architecture/CodeMap]]
