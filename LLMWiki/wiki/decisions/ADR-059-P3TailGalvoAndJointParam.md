---
title: "ADR-059 P3 尾巴落地（振镜频率自适应与手动演示 · 对中→振镜补偿默认门控 · 接头参数收编）"
date: 2026-10-09
updated: 2026-10-09
tags: [ADR, 振镜, 接头, 基准工艺, 光丝对中, P3]
status: accepted
---

# ADR-059：P3 尾巴落地（F-3 / F-4 / F-6）

> P3 功能实现批H（收尾）：F-3 振镜手动演示与频率自适应、F-4 回零位/对中补偿、F-6 接头参数收编。

## 决策

### 一、F-3 振镜：频率随宽度自适应 + 手动演示

- **频率自适应**：沿 S-6 摆幅范式，`AutoParamHelper` 分段表加**第 7 列「振镜频率」**（JSON 宽度→Hz 字典，
 `EnsureGalvoFrequencyColumn` 补旧表）；`WeaveWidthTable.TryGetFrequencyHz` 查表优先，**无记录保持当前频率**
 （⛔ 不自创宽度→频率公式——分段表即「自适应模块自动匹配最优参数」（需求 24）的载体）。
 - ⚠️ **2026-10-21 演进**（业主裁定「旧思路没有使用方，需要删掉以免干扰」+「摆幅频率与摆幅反相关，据此构造基准公式」）：
 本条**频率读取通道整体退役**——`WeaveWidthTable` 整类删除（`TryGetFrequencyHz`/`LoadCalibration` 一并失效），`EnsureGalvoFrequencyColumn` 停用；
 溯源发现该装载入口**从无调用方** ⇒ DB 第 7 列标定值从未进内存，**「频率随宽度自适应」实际从未运行过**。
 现行机制：DB 新第 7 列「**摆幅频率**」+ `AutoParam.CalSwingFrequency` 两点线性反相关基准（摆幅 2mm→500Hz、10mm→200Hz），
 公式初值入表 → 表格手动核对 → 焊接时 `WeldParamControlWorkflow.CalcGalvoFrequency` 查表输出，
 经 `WeldParamAdaptControl.GalvoFrequency` 下发（`LaserWeldHeadWorkflow.ApplyGalvoAmplitude` 唯一下发口消费）。
 详见 [[modules/WeldParamControl]]「振镜摆幅：已实现」。
- **图形口径**：图形**尺寸**（Width/Length）已随摆幅自适应（既有 `ApplyGalvoAmplitude`）；图形**种类**（圆/八字/直线/圆弧）
 是 U-2 人工功能项（P1 §4.2），不参与宽度自动匹配。
- **手动演示 `GalvoDemo(pattern)`**（P1 §4.2「一次性动作，须与生产流程互斥」）：一次性下发演示参数
 （摆幅 1.0mm、频率协议默认、使能开）；`IsWelding` 时拒绝；**停止演示 = `GalvoHome()` 回零位**。
- **振镜唯一下发口**：`ApplyGalvoAmplitude`（摆幅+频率+中心三量合并，任一变化才重发）——
 延续批E 注记「中心偏移单写、两条链路不得互相覆盖」，`ApplyGalvoCenterOffset` 只改补偿状态。

### 二、F-4：回零位 + 对中补偿（⚠️ 需求 34 冲突裁定）

- `GalvoHome()`：回**逻辑零位**（`CreateLogicalHome`，直线+最小摆幅+不使能），中心补偿状态一并清零。
- **内部参数写入与回读** = 既有 `SetGalvoParams` / `ReadGalvoParams`（S-2 协议层完整），U-5 直绑，无新增码。
- **冲突**：需求 34「光丝对中仅做状态监控，**不支持自动调整光斑适配**」 vs F-4「光丝对中偏差驱动中心微调
 （ApplySpotAlignCompensation 落地）」。**裁定**：方法落地但**默认关闭**——
 `GALVO_AUTO_CENTER_COMP`（默认 **false** ⇒ 满足需求 34 仅监控）+ `GALVO_CENTER_COMP_GAIN`（默认 1.0，可负）。
 开启后：`AlignDatum.OffsetX/Y × PixelMmScale × 增益` → `LaserWeldHeadWorkflow.ApplyGalvoCenterOffset` 单写口
 → 随动步合并下发（防与摆幅链互覆）。⚠️ **真机核实**：像素→振镜中心符号方向现场标定。

### 三、F-6 接头参数收编

- **删 `WireType` / `PlateType`**（需求 28 原文：「焊丝类型和板材材质可删除，无用」）：AutoParam 字段 + 构造 +
 调用点 + UI 绑定行全清。**DB 插入列集不动**（调用点传 `string.Empty`）——旧列遗留不引用，防数据兼容风险。
- **`AutoParam.JointType`（int）**：接头类型（英莱 jointtypelist.json 20 类编号，0=未指定）。
 ⛔ 不建新枚举（P1 §3.2）；下拉数据源 `GetJointTypeName`/`GetJointTypeDisplayKeys` 已备（U-3 绑定）。
- **每接头默认基准工艺**：`WeldParamManager.GetOrCreateJointDefault(jointType)`——标识「接头默认_NN」，
 默认参数 = `AutoParam.CreateDefault()`（出厂占位，现场标定后保存）；U-3「选接头自动带出默认基准工艺」经此口。
- **删 EmguALG 死代码**：`JointType` 枚举 + `MatchJointType`/`CalculateLargestAngle`/`IsTJointShape`
 （双查零外部消费；接头识别以英莱 20 类为准，4 类轮廓猜测套废弃）。
- ⚠️ **裁决：`Platethickness` / `WireDiameter` 保留**——两者是 `AutoParam.CalVar` 与
 `WeldParamLookupAlgorithm` KVar/JVar 物理公式的输入；P1 §3.2 将 `PLATE_THICKNESS` 归入「板材材质」删除键
 **与公式依赖冲突**，按需求 28 原文（只删「焊丝类型和板材材质」两字符串）执行。`WireDiameter`「迁入基准工艺」
 = 归组语义（它本就在 AutoParam 基准工艺组内，U-3 分组呈现）。
- 「启用线激光引导收敛」（需求 28 尾句）：后端 `EnableGuide` 单源已有；自适应页重复 UI 入口消除归 U-3。

## 备选方案

| 备选 | 放弃原因 |
|---|---|
| 频率用公式随宽度推导 | 自创公式红线；分段表即需求 24 的「自动匹配最优参数」载体 |
| 对中补偿默认开启 | 直接违反需求 34「不支持自动调整」；默认关 + 可配开关两全 |
| 删 Platethickness/WireDiameter | 破坏 KVar/JVar 物理公式（需求 28 亦未列丝径/板厚数值项） |
| 接头类型建枚举 | P1 §3.2 明令读 jointtypelist.json，不建新枚举 |
| 演示做成循环流程 | P1 §4.2：一次性动作；停止语义用回零位承担 |

## 后果

### 正面
- 摆动「幅度+频率」双参数随焊缝宽度自适应（需求 24 闭环）；演示/回零位动作就绪（U-2/U-5 待绑）
- 对中补偿可落地但默认合规；接头 20 类 + 每接头默认基准工艺的数据链就绪（U-3 待绑）
- 死代码套（4 类接头猜测）清出；P3 功能项全部收口

### 负面 / 待验证
- 中心补偿符号、频率表数值需现场标定；演示摆幅 1.0mm 为占位
- DB 旧列（焊丝/板材）遗留冗余；`GetOrCreateJointDefault` 默认参数为出厂占位

## 背景

（待补：本决策要解决什么问题）

## 相关页面

- [[decisions/ADR-042-SeamTrackingConsolidated]]（摆幅消费链）· [[decisions/ADR-053-TaLaCurveAndMotorScale]]
- [[decisions/ADR-057-TaLaActionAndFollowControl]] · [[decisions/ADR-058-WireAlignMillimeterAndCutWireChain]]
- [[api/LaserWeldHeadWorkflow]] · [[api/DeviceControlWork]] · [[modules/MotionControl]]
- [[project/ReviewOptimization-P1-StructureDesign]]（需求 23/24/26/28 与控件归属）
