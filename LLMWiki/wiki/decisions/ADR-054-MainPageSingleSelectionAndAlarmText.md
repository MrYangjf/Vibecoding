---
title: "ADR-054 主页面选项单选与报警信息语义"
date: 2026-10-09
updated: 2026-10-30
tags: [决策, UIDesign, MainPage, UI交互, 报警]
status: accepted
---

# ADR-054 主页面选项单选与报警信息语义

> 需求来源：第一次评审优化需求 No.1~5（P1 §4.4）· 实施批次：P3 批 B（2026-10-09）

## 背景

`MainPage` 的工艺参数实时曲线（ScottPlot `formsPlot2`）由四个 `AntdUI.Checkbox`
（`chkSeamWidth`/`chkRobotSpeed`/`chkFeedSpeed`/`chkLaserPower`）控制显隐，**四者可同时勾选**，
同图叠四条不同量纲的曲线（焊缝宽度 mm / 速度 mm·s⁻¹ / 功率 W），纵轴被拉平，现场无法读数。
业主评审裁定：**改为单选**，并扩充为五项内容。

同时两处语义问题：

- 状态栏 `LabelStatus` 直出 `MainDeviceStatus` 枚举词（`设备状态：EStop`），现场看不懂发生了什么；
- 子设备快捷开关面板列了 6 项，其中「焊接头」由 WSX 从站托管、「PLC通讯」无通讯实例可切换 —— 是两个永假的按钮。

## 决策

### 决 1 — 五项互斥单选，控件形态用 Checkbox + 手动互销

| 项 | 值 |
|---|---|
| 控件形态 | **保留 `AntdUI.Checkbox` + `ApplySeriesSingleSelection` 手动互销** |
| 互斥时机 | 勾选事件内完成；取消勾选时**不互销**（允许取消到最后一项） |
| 防重入 | `_suppressSeriesEvent` 抑制标志（互销会让其余四项各自再触发一次 `CheckedChanged`） |
| 五项 | 接头宽 / 运动速度 / 送丝速度 / 激光功率 / 送丝Z轴位置 |

> ⛔ **不用 `AntdUI.Radio` 的原因（2026-10-09 核实）**：
> 类名是 `AntdUI.Radio`（**不是 `RadioButton`**），`Checked` 属性已由官方 demo `Views/RadioDemo.Designer.cs` 实证；
> 但**其事件名无先例且不可确定** —— demo 未挂任何 `radioN` 事件，`AntdUI.dll` 已混淆（字符串碎片化）扫不出成员名。
> 本机无 C# 编译器（rules/KR-010），赌错就是下一轮编译错 ⇒ 选已实证可用的 `Checkbox.CheckedChanged`。
> 详见 [[guides/AntdUI-Reference]] 「AntdUI 控件应用参考 demo」节。

### 决 2 — 「焊缝宽度」文案改「接头宽」

控件文案与图例常量 `NameSeamWidth` 同步改为「接头宽」；**字段名与数据源 `SeamWidth` 不改**
（改名会牵连 `WeldParamOutput`/`ChartVar`/记录 Schema，属ADR-052 范围，不在本次）。

### 决 3 — 送丝Z轴位置先建位不画线

`chkWireZ` 与 `WireZ`（`ChartVar`）已建并接入 `RefreshParamCharts`，但**后端字段 `TaPositionMm` 未落地**
（P1 §4.4 自列「⚠️ 需加 3 个力矩字段」）⇒ 序列保持空，`AddSeries` 对空序列直接 return。

> ⛔ **禁止画恒 0 假曲线**：宁可该选项下图表为空，也不要给现场一条看似正常的平线。
> 后端补齐后只需在数据点追加处加 `WireZ.Add(x, y)`，UI 侧无需再改。

### 决 4 — 状态栏改报警信息，去掉「设备状态：」前缀

`ApplyDeviceStatus` 六档文案由 `设备状态：{枚举词}` 改为可读文本（`运行中`/`复位中`/`已停止`/`未复位`）。
其中 **报警与急停两档追加具体原因**（`BuildAlarmText`），来源优先级：

1. 温控：`LaserWeldHeadWorkflow.Instance.IsTemperatureAlarm` → `保护镜温度超限`
2. 从站报警位：`LastAlarmStatus`（保护镜温度 / 温升 / 切割气压 / 驱动器）→ 分项文案
3. 兜底：`请检查设备`

> 未知态分支 ⛔ **禁止 `state.ToString()` 直出**（原实现就是），枚举名只进日志，标签显示「状态未知」。
> `BuildAlarmText` 内读设备状态包 `try/catch` —— **报警信息本身抛异常会导致状态栏崩**，降级为兜底文案并入日志。

### 决 5 — 子设备 6 → 4，索引同步

名表收敛为 `{ "线激光", "监控相机", "控制器", "机器人" }`。

> ⚠️ **索引语义随名表变化**：`LineLaserSwitchIndex` 由 `1` 改为 **`0`**。
> 该常量被 `RefreshDeviceSwitchUi`（判哪些按钮随线激光运行态切徽标）与 `BuildDeviceTooltipText`
> （判哪个按钮可操作）共用 ⇒ ⛔ **改名表必须同步改本值**，否则会操作到错误的设备。

## 后果

- `MainPage.Designer.cs` 732 行（+14）：新增 `chkWireZ` 四件套 + 文案改「接头宽」。
- `MainPage.cs` 五项订阅/退订配对、`RefreshParamCharts` 增 `chkWireZ` 分支、新增互销与报警文本两个方法。
- ✅ 图表现同图只显示一条曲线，纵轴不再被多量纲拉平。
- ⏳ 待补：`TaPositionMm`（送丝Z轴位置）与 Y 轴位置字段落地后接线；`AntdUI.Radio` 事件名一旦可确定可换回原生控件。

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[api/MainPage]] — 主页面接口与现状
- [[guides/AntdUI-Reference]] — ⭐ AntdUI 控件 demo 路径 + `Radio` 类名与事件不可知的结论
- [[decisions/ADR-049-MainPageDualChartAndCamPreview]] — 双图化前身（本 ADR 在其基础上改单选与文案）
- [[decisions/ADR-011-ButtonShadowDeviceSwitch]] — 子设备开关用 `ButtonShadow`（本次收敛其名表）
- [[project/ReviewOptimization-P1-StructureDesign]] — 需求来源 §4.4