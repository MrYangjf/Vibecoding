---
title: DeviceMonitorPage 设备监控页
date: 2026-11-20
updated: 2026-11-20
tags: [API, UI, 设备监控, 温度显示, 焊接头, ControlPage]
source: AdaWeldSystem/UIDesign/ControlPage/DeviceMonitorPage.cs + .Designer.cs
---

# DeviceMonitorPage — 设备监控页（焊接头温度显示）

> 2026-11-20 建页（[[decisions/ADR-112-ui-page-split-and-dialog-cleanup]]）替换 FormMain「设备监控」Tab 空占位；同日接收自 [[api/SystemControlPage]] 迁入的焊接头实时温度显示（ADR-112 演进记录）。页面布局由业主在 VS 中调整：`tableLayoutPanel1`（4×4）左格 `tlPTemp`（2 列 × 9 行）承载温度显示，右格 `image3D1`（AntdUI.Image3D，weldhead1 焊接头图）。

## 基本信息

| 项 | 值 |
|----|----|
| 类 | `AdaWeldSystem.UIDesign.ControlPage.DeviceMonitorPage` |
| 基类 | `System.Windows.Forms.UserControl` |
| 文件 | `UIDesign/ControlPage/DeviceMonitorPage.cs` + `.Designer.cs` + `.resx` |
| 挂载 | `FormMain.LoadNavAndPages()` → `tabMonitor.Controls.Add(deviceMonitorPage)`，`Dock=Fill` |
| 命名空间 | `AdaWeldSystem.UIDesign.ControlPage`（ADR-005：命名空间=目录） |

## 温度显示区（`tlPTemp`）

| 行 | 列 0（标题） | 列 1（实时值） |
|---|---|---|
| 0 | `lblTempLensCaption` 保护镜温度(℃) | `lblTempLensValue` |
| 1 | `lblTempAmbientCaption` 腔体温度(℃) | `lblTempAmbientValue` |
| 2 | `lblTempRiseCaption` 温升(℃) | `lblTempRiseValue` |
| 3 | `lblTempPressureCaption` 切割气压(Bar) | `lblTempPressureValue` |
| 4 | `lblTempState` 报警状态（跨 2 列） | — |

## 关键方法

| 方法 | 说明 |
|---|---|
| `DeviceMonitorPage()` | `InitializeComponent()` → 设 `timerRefresh.Interval=500` + 订阅 `Tick` → 挂 `HandleCreated`/`HandleDestroyed` |
| `RefreshTemperature()` | public 刷新入口（判 `IsDisposed/Disposing/IsHandleCreated`）→ `ApplyTemperature(CollectTemperature())`；采集与贴值同步在 UI 线程 |
| `TimerRefresh_Tick` | `!Visible` 时跳过（不取数）；否则调 `RefreshTemperature()` |
| `CollectTemperature()` | 读 `LaserWeldHeadWorkflow.Instance.LastTemperature/LastAlarmStatus`，为空回落 `MontionManager.Instance.WeldHead.CurrentTemperature/CurrentAlarmStatus`（从站已初始化时）；格式化为 `TemperatureSnapshot`（数值 `InvariantCulture`；报警态 `HeadAlarmStatus.Describe()`） |
| `ApplyTemperature(snapshot)` | 5 个标签贴值（Lens/Ambient/Rise/Pressure/State） |
| `TemperatureSnapshot` | 私有 sealed 类，字段 Lens/Ambient/Rise/Pressure/State |

## 刷新与生命周期

- **自有定时器**：`timerRefresh`（`System.Windows.Forms.Timer(this.components)`，Designer 托管，500ms），句柄创建即 Start、销毁即 Stop + 退订 `Tick`。⛔ 不依赖 FormMain 的 `uiMillisecondTimer1`，⛔ 不与 SystemControlPage 共用。
- **不新增配置键**：温度阈值与节点号仍归 SystemControlPage 配置链，本页只读展示。
- 权限显隐沿用 FormMain 的 `_hiddenItem1`（「设备监控」SegmentedItem），本页无自行门控。
- `Dispose(bool)` 仅 Designer 标准生成（经 components 容器释放 Timer），`.cs` 未重写。

## 相关页面

- 温度阈值配置来源：[[api/SystemControlPage]]（保留 6 项阈值 + 焊接头节点设置）
- 承载：[[api/FormMain]]（Tab1 设备监控）
- 同目录页面：[[api/MainPage]] · `NavPage` · [[api/DataReviewerPage]]
- 决策：[[decisions/ADR-112-ui-page-split-and-dialog-cleanup]]
- 模块：[[modules/UIDesign]]
