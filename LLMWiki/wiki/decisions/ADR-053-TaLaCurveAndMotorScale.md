---
title: "ADR-053 TA/LA 标定曲线与 WSX 电机量纲（曲线为采样点表；量纲单一换算入口）"
date: 2026-10-08
updated: 2026-10-08
tags: [ADR, 焊接头, LA, TA, 标定曲线, 量纲, MotionControl, WeldParamControl]
status: accepted
---

# ADR-053 TA/LA 标定曲线与 WSX 电机量纲

## 背景

第一次评审新增两类需求：**LA 对焦轴按光斑大小定位**、**TA 送丝Z轴按力度设定**。两者都需要「工程值 ↔ 硬件值」的换算，而换算关系由光学/机械标定决定，**不是解析式**。

同时 WSX 从站电机对象（`0x7000`）的**量纲协议表未标单位**（只标「范围 0~1000」）。业主 2026-10-08 确认当前为 **10 计数 = 1mm**，但明示「后面可能会变动」。

## 决策

### 一、曲线只以采样点表表达，不用公式

⛔ **红线（2026-10-08 审计澄清：出处不是 ADR-043）**：原文在 `api/WeldParamControlWorkflow.md` 与 `architecture/DeviceControlArchitecture.md` —— 明令「不要用自创公式（如 `(SeamWidth - LaserDiameter)/2`），那是未经验证的推导」。本 ADR 明确：**离焦量↔光斑、位置↔力矩补偿的关系只以采样点表表达**，代码不内置任何解析式。

| 曲线 | 映射 | 内置锚点（不可删） | 默认外推 |
|---|---|---|---|
| 曲线A | LA 位置 → 光斑大小 | `LA = 0 ↔ 光斑 = 0.6mm`（最聚焦态） | 1:1 线性 + 端点钳位 |
| 曲线B | TA 位置 → LA 偏移补偿 | `TA = 0 ↔ 偏移 = 0` | 1:1 线性 + 端点钳位 |

**结构**（`WeldParamControl/Curves/TaLaCurveConfig.cs`）：

- `CurvePoint { double X; double Y; }` + `List<CurvePoint> PointsA/PointsB`
- `CurveInterpolation`：`PiecewiseLinear`（默认）/ `Nearest`
- `CurveExtrapolation`：`Clamp`（默认）/ `Reject`
- `Version`：标定值替换可溯
- `IsValid()`：**X 严格递增 + Y 单调不减**（离焦量增大光斑必增大；反向点拒绝导入）
- `LoadFromFile()`：**任一条曲线缺失或单调性不合法 ⇒ 整批不采用，保留内置默认**（半套曲线比无曲线更危险）
- 存储：`Config\WeldParamControl\Algorithm_XML\TaLaCurve.xml`（复用 `XdocumentReaderWriter` 三段式，ADR-033）

**外部标定值到位后只换数据不改代码。**

### 二、量纲可配置 + 换算单一入口

- `WeldHeadConfig.MotorPulsePerMm`（**可变属性** `public double`；默认值取常量 `DefaultMotorPulsePerMm = 10.0`），四点闭环键 `MOTOR/PULSE_PER_MM`
- 换算**只经两个私有方法** `MmToMotorCount` / `MotorCountToMm`；⛔ 禁止多处散算（量纲一变漏改 = 隐性 BUG）
- 初始化日志打印生效量纲（沿用 `lessons/JudgementThresholdScaleMismatch` 坑三「改动是否生效一眼可判」）

### 三、Manager 唯一口

`TaLaCurveConfig` 与 `WeaveWidthTable` 的实例**归 `WeldParamManager` 独占**，外部经 `TaLaCurve` / `WeaveTable` 属性只读消费（ADR-006 / ADR-038）。构造时 `LoadFromFile()` 失败**不报错**（保留内置默认，可直接跑）。
 - ⚠️ **2026-10-21 演进**：`WeaveWidthTable` 整类**已删除**（旧摆幅取值通道无使用方，业主裁定删除），`WeldParamManager.WeaveTable` 属性同步移除；本条「独占」约束现仅适用 `TaLaCurveConfig`。摆幅宽度/摆幅频率改由 `AutoParam.SpotSwingGain` + `AutoParam.CalSwingFrequency` + `WeldParamManager.SwingWidthDic`/`SwingFrequencyDic` 承载（详见 [[modules/WeldParamControl]]）。
 - ⚠️ **2026-10-21 演进（锚点读取口收口）**：曲线A 的**锚点光斑**（LA=0 处最聚焦光斑）原为 `TaLaCurveConfig` 的**编译期常量** `AnchorSpotMm = 0.6`，被模块外（`LaserWeldHeadWorkflow`）直写引用——违反本条「独占 + 唯一口」纪律。现状：常量改名 `DefaultAnchorSpotMm`（仅作无 X=0 锚点时的回退值），`AnchorSpotMm` 改为**实例属性**（从曲线A 采样点表取 X=0 点，随标定数据变化）；外部统一经 `WeldParamManager.AnchorSpotMm` facade 读取。**⛔ 外部不得再直读 `TaLaCurveConfig` 的任何配置值**（含常量与静态成员）。

## 备选方案

| 备选 | 放弃原因 |
|---|---|
| 曲线用公式（如 `spot = k * la`） | ADR-043 红线；且离焦↔光斑含镜头/材料非线性，公式化必失真 |
| 曲线硬编码在 `WeldParamManager` 内 | 会让 Manager 膨胀且不便交付标定表格；独立类便于「只换数据」 |
| 量纲写成编译期常量 | 业主明示「后面可能会变动」；改为配置项后变更成本为 0 |
| 每个调用点各自换算 mm↔count | 量纲变更时必漏改（同类漏改已发生过：`InstallOffsetY` 读写错位） |

## 后果

### 正面
- 外部标定值到位只需替换 XML 数据，**结构与代码零改动**
- 量纲变更改配置即生效，且换算只有两处，漏改面收窄到 2 行
- 默认线性组内置 ⇒ **不填表也能直接跑**，不阻塞现场

### 负面
- 采样点表需人工维护；单调性不合法时整批拒收（宁可无数据也不用半套）
- `Clamp` 外推在端点外恒返回端点值，域外输入不会报错（需 UI 侧提示已钳位）

## F-10 导入落地（2026-10-09 就地演进，条款增补）

「外部标定值到位后只换数据不改代码」的**导入通道**已落地（`TaLaCurveConfig.ImportFromCsv`）：

- **载体 = CSV/TSV**（两段式，含「曲线A」/「曲线B」段头；与 05 输入模板同构，交付 `TaLaCurve_输入模板.csv`）。
 ⛔ 不做 xlsx 直读（无第三方 Excel 库，且运行环境不应依赖办公组件）；业主填 05 页或模板 CSV 后另存/直接填 CSV 导入。
- **导入校验**：单调性（`IsValid`）+ **X=0 锚点行不可缺**（出厂缺省行勿删）——违反即**整批拒收保留现值**（与 `LoadFromFile` 半套拒收同则）。
- **版本可溯**：导入成功 `Version` 置「导入-yyyyMMddHHmmss」并落盘；曲线**只读**，UI 只提供导入入口不得改点值。
- 导入即生效（消费方经 `WeldParamManager.TaLaCurve` 唯一口读取，无需重启）。

## 相关页面

- [[decisions/ADR-042-SeamTrackingConsolidated]] —— 摆幅消费方（本 ADR 配套落地）
- [[decisions/ADR-043-WeldParamControlConsolidated]] —— 焊缝参数控制综合页（⚠️ 其正文**无**「自创公式」条款；红线原文见 `api/WeldParamControlWorkflow.md`）
- [[decisions/ADR-033-ConfigArchitectureStandard]] —— 配置三段式与四点闭环
- [[decisions/ADR-030-WeldHeadSlaveDeviceUnderMotionControl]] —— LA 改走从站（本 ADR 的前提）
- [[lessons/JudgementThresholdScaleMismatch]] —— 量纲/阈值类改动的日志自证做法
- [[project/ReviewOptimization-P1-StructureDesign]] —— 结构定稿（五份产物）
