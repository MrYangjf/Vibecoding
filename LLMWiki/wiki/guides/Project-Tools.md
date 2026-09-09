---
title: 项目工具、规范与常见问题汇总
date: 2026-08-18
tags: [指导, 工具, 规范, 模拟, 汇总]
---

# 项目工具、规范与常见问题汇总
> **章节导航**（本页 937 行，超长页请先按章节定位再读）：
>
> - [1. 代码图谱工具（code-review-graph）【已废弃 — 历史参考】](#1-代码图谱工具code-review-graph已废弃-历史参考)
> - [1.2 Grep 符号定位：结果截断导致的消费方漏统计](#12-grep-符号定位结果截断导致的消费方漏统计2026-09-01)
> - [2. Wiki 工作流规范](#2-wiki-工作流规范)
> - [2.5 批量重命名：子串碰撞导致「前缀重复污染」](#25-批量重命名子串碰撞导致前缀重复污染)
> - [3. 图表工具（ScottPlot.FormsPlot 4.1.74）](#3-图表工具scottplotformsplot-4174)
> - [4. 虚拟相机与模拟模式](#4-虚拟相机与模拟模式)
> - [5. 单例与启动初始化](#5-单例与启动初始化)
> - [6. 3D 相关（HelixToolkit / Assimp）](#6-3d-相关helixtoolkit-assimp)
> - [7. 海康相机运行时（MvCameraControl 原生 DLL 依赖）](#7-海康相机运行时mvcameracontrol-原生-dll-依赖)
> - [8. 历史参考](#8-历史参考)
> - [来源](#来源)


> **位置说明（2026-09-01）**：本页自 `wiki/lessons/` 迁入 `wiki/guides/`。
> 分类判据：**`guides/` = 「怎么做」的操作型指导与参考手册**；`lessons/` = 「踩过什么坑」的教训门禁；`standards/` = 「必须遵守」的强制规范。
> 页面内的历史 lessons 链接已同步更新为 guides 路径。


> 本文档汇总 AdaWeldSystem 项目开发中常用的工具使用指南、工作流规范、以及各类常见问题与避坑指南，作为开发人员的快速参考手册。
>
> 覆盖范围：代码图谱工具（**已废弃，历史参考**）、Wiki 工作流规范、图表工具、虚拟相机与模拟模式、单例启动初始化、3D 渲染、海康相机运行时、以及历史参考条目。

---

## 1. 代码图谱工具（code-review-graph）【已废弃 — 墓碑】

> ⛔ **本节已废弃（2026-08-19 废弃，2026-09-09 治理压缩为墓碑）**：code-review-graph 执行失败频繁、耗时久、误判多，
> 已从 vibecoding-llmwiki 工作流全部环节移除。代码定位 / 影响追溯 / 漂移检测一律使用 **Grep 默认方式**。
> 原始操作手册（约 240 行）已随 git 历史留存（本文件 2026-09-09 之前版本）。
> 现行检索纪律见下节 §1.2（Grep 截断陷阱：影响半径检索必须两次独立检索交叉验证）。

## 1.2 Grep 符号定位：结果截断导致的消费方漏统计（2026-09-01）

> 图谱退役后，Grep 是 Phase 0 Step 0.7 与 Phase 2 Step 2.5 的**唯一**代码定位手段。它有一个必须防范的行为：**单次 Grep 的匹配结果会被截断**，返回条数远少于真实命中数时**不会有任何提示**。

**事故实例**：迁移 `FaultRecoveryManager` 时首次 `Grep(pattern="FaultRecoveryManager|FaultRecordManager|FaultCategory|FaultRecord")` 只返回 2 个消费方（`SafetyWorkflow` 现为 `DeviceStatusWork`、`MainDeviceWorkflow` 现为 `DeviceControlWork`）。改用 `FaultRecord\b` 加词边界缩小命中范围后再次检索，实际是 **6 个**——遗漏的 4 个（`LineLaserWorkflow`/`MonitorCameraWorkflow`/`MotionControlWorkflow`/`WeldParamControlWorkflow`）若不补 using 会直接编译失败。

**规避做法**：

1. **窄化 pattern 再检索**：宽泛的 pattern（尤其含子串包含关系的多个备选，如 `FaultRecord` 与 `FaultRecordManager`）命中过多会触发截断。用 `\b` 词边界、更精确的符号名收敛命中量。
2. **交叉验证**：对"消费方/调用方"这类**必须穷举**的场景，用不同 pattern 至少检索两次（如先搜类型名、再搜方法名），比对文件集合是否一致。
3. **按目录二次确认**：若已知消费方集中在某目录（如 `MainDeviceControl/DeviceWorkflow/`），直接对该目录单独 Grep 一次做兜底。
4. **改完必复查**：Step 2.5 的 Grep 追溯不是走过场——本次正是它在提交前兜住了 4 处遗漏。

> 判据：**影响半径类检索（要改哪些调用方）必须做到「两次独立检索结果一致」**，不能依赖单次 Grep 的完整性。

---

## 2. Wiki 工作流规范

### 2.1 日志追加位置规则

> 教训来源：2026-07-03 修复 logs/log.md 顺序混乱问题
> 相关规范：AGENTS.md「日志追加位置规范」、[[project/vibecoding-workflow]] Phase 3.6

#### 问题现象

`logs/log.md` 在多次 Ingest 后，日志条目时而追加在文件最前面，时而追加在文件末尾，导致：

- 时间顺序完全混乱（7 月 3 日的条目出现在 7 月 1 日条目之后）
- 阅读理解困难，无法快速定位最新变更
- 历史追溯时容易产生误解

#### 根因

1. **规范缺失**：早期 AGENTS.md 和 vibecoding-workflow.md 未明确规定追加位置
2. **执行随意**：不同 AI 会话对"追加"的理解不一致（有的理解为 prepend，有的理解为 append）
3. **缺乏校验**：没有自动化检查确保时间倒序

#### 硬性规范（已写入 AGENTS.md）

1. **追加位置**：新日志必须添加在文件**最前面**（顶部），紧接在 `---` 分隔符之后
2. **排列顺序**：整个 log.md 必须保持**严格的时间倒序**——最新的条目在最前面
3. **禁止行为**：
   - 禁止将新日志追加到文件末尾
   - 禁止在已有条目中间插入新日志（除非是按时间倒序的正确位置）
   - 禁止产生时间顺序混乱

#### 格式要求

```markdown
# Wiki Log — 变更日志

> ...
> **最新记录始终在最前面**。  ← 头部提示已更新

---

## [YYYY-MM-DD HH:mm:ss] 类型 | 描述        ← 最新条目
...

---

## [YYYY-MM-DD HH:mm:ss] 类型 | 描述        ← 较旧条目
...
```

#### 验证方法

执行以下 PowerShell 命令快速检查时间顺序：

```powershell
$lines = Get-Content logs/log.md | Select-String '^## \[(.+?)\]'
$dates = $lines | ForEach-Object {
    $m = $_ -match '^## \[(.+?)\]'
    if ($matches[1] -ne 'No.') { [DateTime]::Parse($matches[1]) }
}
for ($i = 1; $i -lt $dates.Count; $i++) {
    if ($dates[$i] -gt $dates[$i-1]) { Write-Host "顺序错误: $($dates[$i]) 应在 $($dates[$i-1]) 之前" -ForegroundColor Red }
}
```

---

## 2.5 批量重命名：子串碰撞导致「前缀重复污染」

> 2026-08-31 实战：把 `DeviceFlowState` 全量替换为 `MainDeviceFlowState` 时，因 `MainDeviceFlowState`、`OnMainDeviceFlowStateSwitched` 都**包含** `DeviceFlowState` 子串，全量替换产出 `MainMainDeviceFlowState` / `OnMainMainDeviceFlowStateSwitched`，且方法名污染会连带破坏事件订阅（`+=` / `-=` 两端同时错）。

### 正确做法

1. **先查后改**：替换前先 Grep 出全部命中点，人工确认哪些是"完整标识符"、哪些是"长名字的子串"。
2. **带边界替换**：用更长的上下文限定，例如 `" DeviceFlowState"`、`"(DeviceFlowState"`、`"SetFlowState(DeviceFlowState"`；或先做旧名→新名的**一次性定向替换**（连同方法名一起改），再做剩余裸类型名替换。
3. **两步走**：先替换"已含有新名"的组合（如 ~~`SetFlowState(DeviceFlowState` → `SetStep(MainDeviceFlowState`~~，2026-09-03 注：两者均已是历史名，此处仅作**替换手法示例**），再替换裸类型名，最后 Grep 反向校验：
   ```bash
   grep -rn "MainMain\|ChangedChanged\|<WorkflowStepChangedEventArgs<WorkflowStep" --include="*.cs" .
   ```

### 禁止行为

- 禁止对**可能是其他标识符子串**的短名直接全量替换（`DeviceFlowState`、`State`、`Step`、`Comm` 等）。
- 禁止依赖"替换后看起来对"——方法名/事件名污染不会立刻报编译错，但会让 `+=`/`-=` 两端同时失配，排查成本极高。

---

## 3. 图表工具（ScottPlot.FormsPlot 4.1.74）

> 本项目用 **ScottPlot.FormsPlot（4.1.74）** 替换 AntdUI.Chart 作为折线/散点图承载控件。ScottPlot 是轻量、高性能的 .NET 绘图库，专为 WinForms 桌面应用设计，支持实时动态数据可视化。
> API 版本以官方 [ScottPlot 4 Cookbook](https://scottplot.net/cookbook/4.1/) 为准。

### 3.1 版本历史与锁定说明

- **2026-08-12**：图表全面改用 ScottPlot.FormsPlot 4.1.74（替换 AntdUI.Chart）。
- **2026-08-13 上午**：升级到 5.1.59，代码迁移 5.x API，解决 System.ValueTuple MSB3277 冲突。
- **2026-08-13 下午**：**回退到 4.1.74**。原因：5.x 基于 SkiaSharp 渲染，对 .NET 4.8 设计器不友好（设计器加载 FormsPlot 控件不稳定）。5.1.59 全套 DLL 已备份至 `3rdDepend\backup_5.1.59\`。

> **4.1 与 5.x API 差异**：4.1 用 `Plot.AddScatter(xs, ys, ...)`；**5.x 用 `Plot.Add.Scatter(...)`**（本项目当前锁定 4.1.74，必须用 4.1 语法）。搜索"Add.Scatter 报错"等多为把 5.x 示例误套到 4.1。

### 3.2 引用与工程配置

- **两个程序集必须同时引用**（4.1 拆分为核心 + 控件两层）：
  - `ScottPlot.dll`（核心，含 `ScottPlot.Plot` 类——即 `formsPlot.Plot` 的类型）
  - `ScottPlot.WinForms.dll`（控件，含 `ScottPlot.FormsPlot`）
  - 只引用 `ScottPlot.WinForms` 会报 CS0012「类型 Plot 在未引用的程序集中定义」，因为 `Plot` 定义在核心程序集。
- csproj 引用（项目根 `3rdDepend\`，经 MSBuild `<Private>True</Private>` 拷贝到 `bin\Debug\`）：
  ```xml
  <Reference Include="ScottPlot">
    <HintPath>3rdDepend\ScottPlot.dll</HintPath>
  </Reference>
  <Reference Include="ScottPlot.WinForms">
    <HintPath>3rdDepend\ScottPlot.WinForms.dll</HintPath>
  </Reference>
  ```
- **4.1 依赖**：4.1.74 基于 System.Drawing 渲染，**不需要 SkiaSharp/OpenTK/System.ValueTuple**。
- **命名空间**：4.1 的 FormsPlot 类型是 **`ScottPlot.FormsPlot`**（非 5.x 的 `ScottPlot.WinForms.FormsPlot`）。

### 3.3 核心对象模型

每个 `FormsPlot` 控件内含一个 **`Plot`** 对象（`ScottPlot.Plot`），所有绘图 API 都挂在 `Plot` 上；`Plot` 上可挂多种 **plottable**（如 `Scatter` 折线/散点、`SignalPlot` 信号图）。重绘由 `FormsPlot.Refresh()` 触发（非 `Render()`，`Render()` 用于独立 `Plot` 存图场景）。

### 3.4 常用 API（4.1 语法）

#### 初始化：标题 / 坐标轴标签 / 图例

```csharp
plot.Title("焊缝模型数据");        // 图标题
plot.XLabel("机器人 X 轴");        // X 轴标签
plot.YLabel("轮廓");               // Y 轴标签
plot.Legend();                     // 开启图例（读取各 plottable 的 label）
formsPlot.Refresh();               // 重绘
```

#### 添加折线/散点（AddScatter）

```csharp
// 4.1：AddScatter 长参数签名，label 直接设图例名
plot.AddScatter(xs, ys, Color.FromArgb(128, 0, 128), 2, markerSize: 0, label: "焊缝宽度");
```

- `xs`/`ys` 为对应长度的 `double[]`。
- 完整签名：`AddScatter(double[] xs, double[] ys, Color? color, double lineWidth, double markerSize, MarkerShape markerShape, LineStyle lineStyle, string label)`。
- `markerSize: 0` 表示纯折线不画数据点标记；`label` 设图例名（须先 `plot.Legend()` 才显示）。
- **颜色类型**：4.1 的 `AddScatter` 直接用 `System.Drawing.Color`（无需 5.x 的 `ScottPlot.Color` 转换）。
- `AddScatter` 返回 `ScottPlot.Plottable.Scatter` 对象，可保存后用它做运行时增删/改色。

#### 添加信号图（AddSignal）

```csharp
// 4.1：AddSignal 返回 SignalPlot（注意类型名是 SignalPlot，不是 Signal）
double[] data = new double[1920];
var signalPlot = plot.AddSignal(data, 1.0, Color.FromArgb(128, 0, 128), "轮廓");
signalPlot.LineWidth = 2;
signalPlot.MaxRenderIndex = data.Length - 1;
```

- 用于**等间距采样**的大批量数据（如传感器轮廓、波形），比 Scatter 快 5-20 倍（Min/Max 降采样渲染 + 零内存分配）。
- `AddSignal(double[] ys, double sampleRate, Color color, string label)` 返回 `ScottPlot.Plottable.SignalPlot`。
- **类型名注意**：4.1 中是 `ScottPlot.Plottable.SignalPlot`，**不是** `ScottPlot.Plottable.Signal`（易错点）。
- `data` 数组被直接引用（非拷贝），修改数组内容后调用 `Refresh()` 即可重绘，零分配。
- `MinRenderIndex` / `MaxRenderIndex` 控制可见数据范围（如实际点数少于数组长度时）。
- `AxisAutoY()` 可只自适应 Y 轴（X 轴范围固定时常用）。
- **X 轴物理坐标映射**：`SignalPlot.SampleRate` + `SignalPlot.OffsetX` 可将 X 轴从"点索引"映射到物理单位（如 mm）：
  ```csharp
  // 每帧根据实际数据范围动态调整（线激光轮廓 Ymin~Ymax 映射到 mm）
  signalPlot.SampleRate = (yMax - yMin) / (pointCount - 1);
  signalPlot.OffsetX = yMin;
  ```
- **锁定轴缩放/平移**：双重保险——① `Configuration.ScrollWheelZoom/LeftClickDragPan/RightClickDragZoom = false` 禁用鼠标交互；② 每帧 `SetAxisLimits(minX,maxX,minY,maxY)` 强制重置范围。

#### 清空与删除

```csharp
plot.Clear();                       // 移除全部 plottable
plot.Remove(plottable);             // 移除指定 plottable
```

#### 坐标轴自适应与范围

```csharp
plot.AxisAuto();                    // 依据所有 plottable 数据自动缩放
plot.SetAxisLimits(minX, maxX);     // 仅设 X 轴范围（Y 轴保持）
plot.SetAxisLimits(minX, maxX, minY, maxY); // 同时设 X/Y 范围
```

#### DPI 处理（4.1）

- **4.1 需显式置 `formsPlot.Configuration.DpiStretch = false`** 修复高 DPI 缩放字体锯齿：
  - `Program.cs` 用 `SetProcessDPIAware()`（System DPI aware），显示缩放 >100% 时默认 `DpiStretch=true` 会拉伸低分辨率位图导致字体模糊/锯齿。
  - 置 `false` 让 ScottPlot 按真实 DPI 渲染高分辨率位图。

### 3.5 5.x → 4.1 回退对照表

| 5.x（已废弃） | 4.1（当前） |
|---|---|
| `ScottPlot.WinForms.FormsPlot` | `ScottPlot.FormsPlot` |
| `plot.Add.Scatter(...)` + 属性设置 | `plot.AddScatter(xs, ys, c, 2, markerSize: 0, label: name)` |
| `plot.Axes.AutoScale()` | `plot.AxisAuto()` |
| `plot.Axes.SetLimits(min, max)` | `plot.SetAxisLimits(min, max)` |
| `plot.ShowLegend()` | `plot.Legend()` |
| 无 DpiStretch（5.x 移除） | `formsPlot.Configuration.DpiStretch = false` |
| 依赖 SkiaSharp/OpenTK/System.ValueTuple | 仅 System.Drawing（无需额外依赖） |

### 3.6 本项目落地范式

#### MainPage（5 图）

- `formsPlot1`：焊缝模型轮廓；`formsPlot2~5`：焊缝宽度/运动速度/送丝速度/激光功率。
- 初始化统一走 `SetupChart(formsPlot, title, seriesName)`：
  ```csharp
  private void SetupChart(ScottPlot.FormsPlot chart, string title, string seriesName)
  {
      chart.Configuration.DpiStretch = false;
      chart.Plot.Title(title);
      chart.Plot.XLabel("机器人 X 轴");
      chart.Plot.YLabel(seriesName);
      chart.Plot.Legend();
      chart.Refresh();
  }
  ```
- 数据绑定统一走 `BindChartVar(formsPlot, seriesName, ChartVar)`——以 `ChartVar` 的 X/Y 全量重建 plottable：
  ```csharp
  private void BindChartVar(ScottPlot.FormsPlot chart, string seriesName, ChartVar data)
  {
      chart.Plot.Clear();
      int count = data.Count();
      if (count > 0)
      {
          double[] xs = data.X.ToArray();
          double[] ys = data.Y.ToArray();
          chart.Plot.AddScatter(xs, ys, System.Drawing.Color.FromArgb(128, 0, 128), 2, markerSize: 0, label: seriesName);
          chart.Plot.AxisAuto();
      }
      chart.Refresh();
  }
  ```

#### DataReviewerPage（1 图）

- 多系列 + 复选框显隐：ScottPlot 无逐系列 `Visible`，故每次按勾选状态 `Clear()` 后重建 plottable。
- 滑块范围缩放：`formsPlotData.Plot.SetAxisLimits(min, max); formsPlotData.Refresh();`

### 3.7 正确做法

- 用 4.1 语法 `Plot.AddScatter(...)`，勿套 5.x `Plot.Add.Scatter(...)`（本项目当前锁定 4.1.74）。
- 折线关闭数据点标记：`markerSize: 0`。
- 颜色直接用 `System.Drawing.Color`（4.1 无需 `ScottPlot.Color` 转换）。
- 多系列显隐用"清空重建"模式（`Clear()` + 按条件 `AddScatter`），而非逐系列 Visible。
- 控件重绘用 `formsPlot.Refresh()`；`Plot.Render()` 是独立 `Plot` 对象存图用的，不要混用。
- 引用 `ScottPlot.dll`（核心）+ `ScottPlot.WinForms.dll` 4.1.74，两个程序集都要在 csproj 钉版本；漏引核心会报 CS0012。
- 高 DPI 缩放字体锯齿修复：`formsPlot.Configuration.DpiStretch = false`（4.1 必需）。
- 新增/替换 Designer 控件时，同步补 `private ScottPlot.FormsPlot xxx;` 字段声明。

### 3.8 禁止行为

- 在 4.1 项目里用 `Plot.Add.Scatter(...)`（5.x API）。
- 给 `FormsPlot` 加/改 plottable 后不调用 `Refresh()`（界面不更新）。
- 用 `Plot.ShowLegend()`（5.x API，4.1 已改为 `Legend()`）。
- 用 `Plot.Axes.AutoScale()` / `Plot.Axes.SetLimits()`（5.x API）。
- 用 `ScottPlot.WinForms.FormsPlot`（5.x 命名空间）。
- 直接传 `ScottPlot.Color` 给 `AddScatter`（4.1 用 `System.Drawing.Color`）。
- 用 `Plot.Render()` 重绘 `FormsPlot` 控件（应 `Refresh()`）。
- 将 `AddSignal` 返回值存为 `ScottPlot.Plottable.Signal`（4.1 正确类型名为 `ScottPlot.Plottable.SignalPlot`）。

---

## 4. 虚拟相机与模拟模式

> 本节汇总模拟模式下所有已知坑点，涵盖虚拟相机选择、轮廓合成、初始化异步、行程停止、Live 模式排除等常见问题。
> 关联决策：模拟模式相关决策已并入 [[api/DeviceControlWork]]
>
> ⚠️ **2026-09-03 决策沿革**：原「模拟模式贯穿三大流程」与「自动运行/手动连接模型」两份决策均已**废弃**（承载者 `SimulationWorkflow.cs` 已删除、成员归并 `DeviceControlWork`）。本节**坑点本身继续有效**，但文中 `SimulationWorkflow.*` 一律读作 `DeviceControlWork.*`（`Enable`→`EnableSimulation`、`Disable`→`DisableSimulation`、`IsEnabled`→`IsSimulationEnabled`）；现行架构以 [[architecture/DeviceControlArchitecture]] 为唯一指导。

### 4.1 工作流初始化必须用 CameraSelector.Active

#### 问题描述

模拟模式下，`DeviceControlWork.EnableSimulation()`（原 `SimulationWorkflow.Enable()`，2026-09-03 归并）已调用 `CameraSelector.SelectVirtual()` 将 `CameraSelector.Active` 切到虚拟相机 `VirtualCameraRun`。但 `LineLaserWorkflow.InitializeWorker()` 中写死：

```csharp
var camera = CameraRun.Instance;   // ❌ 直接取真实 SmartRay 单例
```

`CameraRun.Instance` 永远指向真实 SmartRay 相机，与 `CameraSelector` 的选择无关。结果：开启模拟流程后，初始化后台线程仍对真实相机执行 `OpenSensor("192.168.178.200","40")`，触发 SmartRay 报错——即"选了虚拟相机却仍在用真实相机"。

#### 正确做法

工作流取相机必须统一走 `CameraSelector.Active`（`_active ?? CameraRun.Instance`），与 `Start()`、`AcquireImage()` 已有用法保持一致：

```csharp
var camera = CameraSelector.Active;   // ✅ 模拟模式返虚拟相机，生产模式返真实相机
if (camera is VirtualCameraRun)
{
    TransitionTo(Standby, "虚拟相机就绪");
    return;
}

// 虚拟相机分支已 return；此处 camera 必为真实 SmartRay 相机（CameraRun）。
// isRun / OpenSensor / ChangeMode 是 SmartRay 硬件专属成员，不在 ICameraRun 共享契约内，
// 故必须转型为具体 CameraRun 才能调用（虚拟相机不实现、也不需要这些成员）。
var realCamera = (CameraRun)camera;
if (!realCamera.isRun)
{
    realCamera.OpenSensor("192.168.178.200", "40");
    realCamera.ChangeMode(false); // PIL 模式
    realCamera.SensorRunContinue();
}
TransitionTo(Standby, "相机初始化完成");
```

> **二次坑（CS1061）**：`CameraSelector.Active` 的静态类型是 `ICameraRun`。若直接写 `camera.isRun` / `camera.OpenSensor(...)` / `camera.ChangeMode(...)`，编译器报"ICameraRun 未包含 isRun/OpenSensor/ChangeMode 的定义"。
> 原因：`ICameraRun` 只声明了共享成员 `AcquisitionCompletedSignal`、`IsRunning`、`LastAcquisitionSuccess`、`CurrentMat`、`SensorRunContinue()`、`SensorStop()`；而 `isRun` / `OpenSensor` / `ChangeMode` 仅存在于具体 `CameraRun`（SmartRay 硬件连接细节），`VirtualCameraRun` 也不实现。
> 正确做法是在真实相机分支内**转型为具体 `CameraRun`** 调用，而非把这些 SmartRay 专属成员硬塞进共享接口。

### 4.2 虚拟相机合成轮廓必须保证 YZ 范围非零

#### 问题描述

模拟运行报错：
`[Debug][VirtualCameraRun1] VirtualCameraRun 生成轮廓失败: 轮廓点云YZ范围过小，无法生成有效图像`

#### 根本原因

`ImageAlgorithm.ConvertContourToMat(...)` 在 `yRange < 0.001f || zRange < 0.001f` 时抛
`InvalidOperationException("轮廓点云YZ范围过小...")`——这是为拦截真实传感器返回的退化点云而设的保护。

`VirtualCameraRun.GenerateSeamContour()` 的 `SimSeamProfile.Flat`（平直焊缝）原实现 `z = depth * 0.5`
是**横向恒定值**，整条轮廓 Z 完全相同 → `zRange = 0` → 命中阈值抛异常。V/U/Random 型因 Z 随 Y 演化故正常。

#### 正确做法

合成轮廓时，即便是「平直」焊缝也不能让 Z 恒定——现实中不存在绝对水平面。引入微小横向坡度 + 轻微起伏：

```csharp
case SimSeamProfile.Flat:
    z = depth * 0.5
        + depth * 0.05 * (t - 0.5)                       // 微小横向坡度
        + depth * 0.02 * Math.Sin(y / halfWidth * Math.PI); // 轻微起伏
    break;
```

`BaseSeamDepth` 默认 3.0mm，得 `zRange ≈ 0.15mm`，远超 0.001 阈值，且视觉上仍近似平直。

#### 通用规则

任何**合成 / 造数**的点云或轮廓（虚拟相机、测试夹具、回放数据），都要保证 Y、Z 方向存在有效跨度，
否则会被下游图像化 / 拟合算法的退化保护拦截。不要为「理想值」牺牲数值有效性。

### 4.3 线激光 Initialize 异步：开启模拟流程须等待 Standby 事件

> **症状**：程序启动后首次点击「开启模拟流程」，线激光停在 `Standby`（待机），未进入模拟测试；需点「关闭模拟流程」（实际仅 Disable）后再点「开启模拟流程」才能进入。
> **根因**：`LineLaserWorkflow.Initialize()` 是**后台线程异步初始化**——调用后状态仅置为 `Initializing` 并启动 `InitializeWorker` 线程，线程内（虚拟相机分支立即、真实相机分支连接后）才 `TransitionTo(Standby)`。消费方在 `Initialize()` 之后**同步**判断 `State == Standby` 调 `Start()`，此时状态仍是 `Initializing`，`Start()` 因要求 `Standby` 而抛 `InvalidOperationException` 或被跳过，线激光停在待机。
> **为什么二次正常**：首次点击走 `Initialize()` 分支但 `Start()` 被跳过；点「关闭」时 `Stop()` 因非运行态被 try/catch 吞掉，仅 `Disable()`；二次点击时线激光已是 `Standby`，直接 `Start()` 成功。

#### 正确做法（消费方如 MotionControlPage.BtnStartSim_Click）

- 若 `State == Uninitialized`：订阅 `StateChanged`，置挂起标记 `_pendingSimStart = true`，再调 `Initialize()`；在事件回调中待 `e.NewState == Standby` 时**回到 UI 线程**（`InvokeRequired`/`BeginInvoke`）调 `Start()`，并取消订阅、清除标记；`e.NewState == ErrorAborted` 时清理挂起标记与订阅。
- 若 `State == Standby`：可直接同步 `Start()`（二次开启场景）。
- 停止分支须 `ClearPendingSimStart()` 取消可能挂起的初始化，避免后台初始化完成误触发 `Start()`。
- `StartPendingLineLaser` 内加 `if (!DeviceControlWork.Instance.IsSimulationEnabled) return;` 守卫（原 `SimulationWorkflow.Instance.IsEnabled`）：用户若在初始化期间点击停止（`DisableSimulation()`），放弃启动，避免竞态误进入流程。

#### 错误写法（曾导致本 Bug）

```csharp
// ❌ 错误：Initialize 异步，紧接同步判断 Standby 必失败
var ll = LineLaserWorkflow.Instance;
if (ll.WeldStatus == SubDeviceWeldStatus.Standby)
    ll.Initialize();           // 仅转 Working，后台线程异步转回 Standby
if (ll.WeldStatus == SubDeviceWeldStatus.Standby)
    ll.Start();                // 此时仍是 Working → Start 被跳过/抛异常
```

> **术语对照（2026-09-02 ADR-028）**：旧代码写作 `ll.State == LineLaserWorkflowState.Uninitialized/Standby`（阶段枚举直接对外）；现行对外只有 `SubDeviceWeldStatus` 七态，阶段枚举降为私有。连接就绪另看 `ll.State`（`SubDeviceState` 两态）。

### 4.4 模拟测试：行程到达 = 正常停止，不是异常终止

#### 现象

模拟测试（虚拟相机）下，日志出现 `工作流异常终止 - 原因: 获取图像失败：机器人X行程1004.46mm，超过最大允许长度1000.00mm 终止码: FailureDistanceExceeded`。
用户质疑：用的是虚拟相机、不可能获取失败，而且"到达行程后应该停止，怎么会报异常终止"。

#### 根因

1. **语义错误**：`_maxWeldLength`（默认 1000mm）本就是整条焊缝长度。机器人X行程跑满 = 焊缝焊完 = **正常作业完成/停止**，
   旧实现却把行程到达当作失败 `FailureDistanceExceeded` 异常终止。
2. **检查位置错误（更隐蔽）**：行程检查只在 3 个失败处理函数内被调用
   （`HandleAcquireFailure` / `HandleAnalyzeFailure` / `HandleAdjustFailure` → `CheckFailureThresholds`），
   **正常运行跑到行程根本不会触发任何停止逻辑**，必须等某次失败顺带命中距离条件才停，否则无限循环。
3. **连带**：虚拟相机首帧后无后续帧（单帧生成语义 + `AcquireImage` 仅在 `!IsRunning` 触发），
   连续超时累计达 `_maxConsecutiveFailures` 后报 `ConsecutiveFailureExceeded`。

#### 修复方案

- `LineLaserWorkflow` 新增 `IsWeldLengthReached()` + `StopByWeldLengthReached()`：主循环 `WorkflowLoopWorker` 顶部**每轮**检查行程，
  命中即置 `_workThreadShouldStop`、转 `Completed`（reason「焊缝行程完成…」）、触发 `WorkflowCompleted`——**正常停止，非异常**。
- `IsValidTransition` 表增加 `Acquiring → Completed`，让任意活动态都能干净结束为 `Completed`。
- `CheckFailureThresholds` **移除条件2（行程距离）**，仅保留"连续失败次数"这一真正异常阈值。
- `AcquireImage()` 对虚拟相机（`CameraSelector.IsVirtual`）**每周期重新 `SensorRunContinue()`** 产帧。
- `MotionControlPage` 监听 `WorkflowCompleted`（reason 含「焊缝行程完成」）→ 联动 `StopSimulationFlows()` + 复位按钮为「开启模拟流程」，
  形成完整闭环：开启 → 停止（运行中）→ 焊缝完成自动停 → 开启。
- `TransitionToErrorAborted` 的 `ShowLog`+事件触发移入 `IsValidTransition` 守卫（`transitioned` 标志），杜绝同一异常重复日志。

#### 边界 / 注意

- 行程到达是**整段作业的停止信号**，不是"某次采集失败"。模拟模式下 `GetCurrentRobotX()` 由 `DeviceControlWork`（原 `SimulationWorkflow`）共享时钟驱动（`simStartX + simSpeed × elapsed`），
  故行程会随时间自然到达——这是预期行为，不是 bug。
- `WorkflowSignalCode.FailureDistanceExceeded` 已移除（2026-08-13 死代码清理时删除，行程到达不再作为失败信号）。
- 虚拟相机产帧采用**每周期重触发**（单线程、无后台 Timer），规避并发 dispose `_currentMat` 的线程安全竞态；`AcquireImage` 已对 `CurrentMat` 做 `Clone()`，独立于相机内部缓冲。

### 4.5 Live 模式不触发 AcquisitionCompletedSignal

#### 问题描述

CameraRun 的回调中无条件触发 AcquisitionCompletedSignal.Set()，导致 Live 预览模式也参与了 Workflow 取图流程，Workflow 获取到不完整的预览帧。

#### 根本原因

Live 模式（实时预览）和 PIL 模式（工作取图）共享同一个回调入口。Signal 的无条件触发使 Workflow 误将预览帧当作工作帧处理。

#### 正确做法

回调中区分模式，仅 PIL 模式触发 Signal：

```csharp
private void OnCompletedAcqEvent(object sender, AcquisitionEventArgs e)
{
    if (IsLiveMode)
    {
        // Live 模式：仅更新显示，不参与 Workflow
        UpdateLiveDisplay(e.Data);
        return;
    }
    
    // PIL 模式：处理工作帧并通知 Workflow
    ProcessAcquisitionData(e.Data);
    LastAcquisitionSuccess = true;
    AcquisitionCompletedSignal.Set();
}
```

---

## 5. 单例与启动初始化

> 具有 INI/文件持久化的单例（如 `JobManager`、`CameraSelector`），其「加载/恢复」方法必须**在应用启动、创建任何读取它的 UI 页面之前**被显式调用；否则保存逻辑写了文件，却从未读回，表现为「每次打开都要重新配置」。

### 5.1 触发场景（真实故障）

- `JobManager` 的 `LoadJobsFromIni()`（恢复 `CurrentId` 与各 `Job_*.ini`）只在 `Initialize()` 内调用；而 `Program.Main()` → `FormMain` 全程**从未调用** `JobManager.Instance.Initialize()`。
  - 结果：保存正常（`Config/Jobs/JobIndex.ini` 有内容），但每次启动 `_jobs` 为空、`CurrentJobId` 默认 1、`CurrentJob` 为 null → `LLCamWorkJob` 下拉框为空 / 「无可用配置」。
  - **并非路径错误**——INI 路径逻辑正确，问题在「只写不读（加载未触发）」。
- `CameraSelector.IsVirtual` 原先**完全没有持久化代码**（仅内存），每次启动重置为真实相机。

### 5.2 正确做法

1. 在 `FormMain` 构造函数、设计器模式守卫之后、**`new NavPage()/new NavPage()` 等子页面创建之前**，集中调用：
   ```csharp
   JobManager.Instance.Initialize();   // 加载 Job + CurrentId
   CameraSelector.Load();              // 从 Config/INI/CameraSelector.ini 恢复相机选择
   ```
2. 单例若只暴露 `Save()`/`Load()`，必须由启动入口负责调用——不要指望「某个页面第一次访问时自动加载」，UI 页面构造顺序不可控且可能晚于首次读取。
3. INI 持久化文件位置遵循 [[decisions/ADR-005-ConfigLayout]]：作业类归 `Config/Jobs/`，通用设置归 `Config/INI/`。

### 5.3 自检清单

- [ ] 凡是有 `Save*()`/`Write*()` 到 INI 的单例，是否也有对应 `Load()`/`Initialize()` 在启动期被调用？
- [ ] 调用点是否早于所有读取该单例的 UI 页面构造？
- [ ] 设计器模式（`LicenseManager.UsageMode == Designtime`）下是否跳过了文件 IO（避免设计器加载时触碰运行时配置）？

---

## 6. 3D 相关（HelixToolkit / Assimp）

> 本节汇总 HelixToolkit.SharpDX 与 Assimp 3D 模型导入中的常见坑点。

### 6.1 Assimp 导入必须整体添加 Root

#### 问题描述

使用 Assimp 导入 3D 模型后，逐个将子节点 AddChildNode 添加到场景中，导致模型层级关系丢失、坐标系错乱、部分 mesh 不显示。

#### 正确做法

必须将 scene.Root 整体加入 HelixToolkit 场景：

```csharp
// ✅ 正确
var scene = assimpContext.ImportFile(path);
viewport.Children.Add(scene.Root);

// ❌ 错误（禁止）
foreach (var child in scene.Root.Children)
{
    viewport.Children.Add(child);  // 层级关系丢失！
}
```

#### 原因

Assimp 的 scene.Root 包含完整的坐标变换层级（Transform 矩阵链）。拆分后每个子节点失去父级变换，导致位置/旋转/缩放全部错误。

### 6.2 Bounds 哨兵值导致黑屏

#### 问题描述

3D渲染时，如果点云数据的 Bounds（包围盒）出现 Minimum >= Maximum 的哨兵值，或者数据中存在 Infinity/NaN，HelixToolkit 渲染引擎会显示黑屏。

#### 根本原因

HelixToolkit.Wpf.SharpDX 的 Viewport3DX 在计算相机视角和裁剪平面时依赖 Bounds：
- Minimum >= Maximum → 包围盒无效 → 相机参数计算失败
- Infinity/NaN → 浮点数运算异常 → 渲染管线中断

#### 正确做法

加载数据前必须验证和过滤：

```csharp
public bool ValidateBounds(BoundingBox bounds)
{
    if (bounds.Minimum.X >= bounds.Maximum.X) return false;
    if (bounds.Minimum.Y >= bounds.Maximum.Y) return false;
    if (bounds.Minimum.Z >= bounds.Maximum.Z) return false;
    return true;
}

public PointCloudData FilterInvalidPoints(PointCloudData data)
{
    return data.Where(p => 
        !double.IsInfinity(p.X) && !double.IsNaN(p.X) &&
        !double.IsInfinity(p.Y) && !double.IsNaN(p.Y) &&
        !double.IsInfinity(p.Z) && !double.IsNaN(p.Z)
    ).ToList();
}
```

---

## 7. 海康相机运行时（MvCameraControl 原生 DLL 依赖）

### 7.1 现象

引用 `MvCameraControl.Net.dll`（托管封装）后**编译通过**，但运行到创建设备/采集时抛出 `DllNotFoundException` / `EntryPointNotFoundException` / `TypeLoadException`，或相机始终无法打开（`MV_CC_OpenDevice_NET` 返回非 0 且无更多信息）。

### 7.2 根因

`MvCameraControl.Net.dll` 只是**托管包装**，它通过 P/Invoke 调用原生核心 `MvCameraControl.dll`（C 导出）。本机的 MVS **Development（开发示例）包并不包含原生 `MvCameraControl.dll`**——只有：
- `Development/DotNet/{AnyCpu,win32,win64}/MvCameraControl.Net.dll`（托管）
- `Development/Libraries/{win32,win64}/MvCameraControl.lib`（导入库，非运行时）

原生 `MvCameraControl.dll` 由**完整 MVS 客户端/运行时安装**提供（通常位于 `C:\Program Files (x86)\MVS\Runtime\Win64\`，并写入系统 PATH）。若目标机器只装了 Development 包而未装完整 MVS，或运行时 PATH 缺失，托管 DLL 找不到原生 DLL → 运行时失败。

### 7.3 规避方案

1. **目标运行/调试机器必须安装完整 MVS 客户端**（含 Runtime），确保 `MvCameraControl.dll` 在 PATH 或可执行文件同目录。
2. 若需绿色部署（不依赖安装），将对应架构（x64）的原生 `MvCameraControl.dll` 及其配套原生 DLL（如 `MvUsb3Cam.dll`、`MvGigECam.dll` 等）复制到输出目录 `bin\x64\`（需从完整 MVS Runtime 目录获取）。
3. 本项目已将托管 `MvCameraControl.Net.dll` 复制到 `AdaWeldSystem/Libs/MvCameraControl/`（CopyLocal=true），编译自包含；原生运行时仍按上述第 1 条要求。
4. **架构匹配**：托管 DLL 为 AnyCpu，原生 DLL 分 win32/win64。Debug 平台目标为 x64，务必用 win64 原生 DLL；若切到 x86 进程需用 win32 原生 DLL。

---

## 8. 历史参考

> 本节条目对应的问题已被修复、方案已被替代，或已不再适用于当前代码。保留仅作历史参考，新代码请勿照搬。

### 8.1 NuGet 卫星资源程序集清理

> **已被 [[decisions/ADR-018-NuGetLocalization]] 替代**：项目已完全移除 NuGet PackageReference，改为本地 DLL 引用。卫星程序集清理 Target 不再需要。本小节保留作为历史参考。

#### 现象

构建后，`bin\Debug\`（或 `bin\Release\`）下出现若干以语言代码命名的子文件夹（`cs/de/es/fr/it/ja/ko`），内含 `*.resources.dll` 卫星资源程序集。

#### 根因

某些 NuGet 包（如 `Microsoft.CodeAnalysis.CSharp`）在 `lib\<tfm>\<culture>\` 中放置了 `.resources.dll`。使用 `PackageReference` 的旧式 `.csproj` 项目默认会把所有受支持文化的卫星资源一并复制到输出目录。

#### 解决方案（历史参考）

对于旧式 `.csproj`（非 SDK 风格），在 `.csproj` 末尾添加一个 Target，在 `ResolveAssemblyReferences` 之后将所有卫星资源从 copy-local 列表中移除：

```xml
<Target Name="RemoveNonEnglishSatelliteAssemblies" AfterTargets="ResolveAssemblyReferences">
  <ItemGroup>
    <ReferenceCopyLocalPaths Remove="@(ReferenceSatellitePaths)" />
    <ReferenceCopyLocalPaths Remove="@(ReferenceCopyLocalPaths)" Condition="$([System.Text.RegularExpressions.Regex]::IsMatch('%(Filename)', '\.resources$'))" />
  </ItemGroup>
</Target>
```

> 注：本项目已改用本地 DLL 引用，不再需要此 Target。SDK 风格项目可直接用 `<SatelliteResourceLanguages>en</SatelliteResourceLanguages>`。

### 8.2 Record.ini 存绝对路径导致迁移后失效

> **状态**：2026-08-14 已实施根治方案（`NormalizeDirectoryPath` 兜底回退）。本小节保留作为配置路径设计的教训参考。

#### 症状

文件追溯对话框打开后，正常记录文件列表和临时文件列表**都为空**，尽管用户已按日期把 `.ply` 文件归档到了 `Records\yyyyMMdd\` 子目录。

#### 根因

`bin/Debug/Config/INI/Record.ini` 的 `[Paths]` 节存的是**硬编码绝对路径**，指向旧项目位置。项目整目录复制迁移时 `bin/Debug` 连同 `Record.ini` 一起带走，路径从未更新。

路径来源：`RecordConfigForm` 用 `FolderBrowserDialog` 选目录后 `WriteString` 写入**绝对路径**（`RunRecordManager.SaveConfigToIni`）。

#### 临时修复（配置层）

删除 `Record.ini` 的 `[Paths]` 节（或删除 `RecordDirectory`/`TempDirectory` 两行），让 `ReadString` 返回默认相对路径 `baseDir\Records` / `baseDir\Temp`，随项目迁移自动正确。

> `INIFile.ReadString` 对「key 存在但值为空」返回空串 `""`（**不**返回默认值），所以必须**删除整行**，不能留 `RecordDirectory=` 空值——空值会导致 `_recordDirectory=""`，比原问题更糟。

#### 根治方案（已实施）

- `RunRecordManager.LoadConfigFromIni` 新增 `NormalizeDirectoryPath`：配置路径 `IsNullOrWhiteSpace` 为空时回退默认相对路径，并写入 `PathFallbackMessage` 属性（供 UI 提示）。
- `RecordConfigForm.LoadConfig` 改为读取 `RunRecordManager.Instance.RecordDirectory`/`TempDirectory`（规范化后的值），并弹出 `PathFallbackMessage` 提示。
- **保留绝对路径选择能力**（用户确认：相对路径无法选择项目外目录），仅对「空路径」兜底回退默认。
- 附带修复：`FileTraceForm` 的 `CellClick` 事件订阅从 Designer.cs 移至**代码后置构造函数**（Designer.cs 手写事件订阅会被设计器重新序列化时丢失），并默认选中第一个文件。

### 8.3 UILight 控件属性误用

> **UILight 已被 [[decisions/ADR-015-UIFrameworkMigration]] 取代**：UI 框架迁移至 AntdUI 后，状态指示灯改用 **`AntdUI.Signal`**（而非 SunnyUI `UILight`）。本小节的 UILight 三要素用法仅作**历史参考**；新代码请使用 `AntdUI.Signal` 的对应属性。

#### 问题描述

错误地使用 `Enabled` 和 `Blink` 属性控制 UILight 状态，这两个属性在 SunnyUI 的 UILight 中不存在。

#### 正确做法（历史参考）

使用三要素控制 UILight：

```csharp
// 初始化
uiLight.OffColor = Color.FromArgb(180, 180, 180);  // 灰暗 = 未连接
uiLight.OnColor = Color.LimeGreen;                  // 绿色 = 正常
uiLight.State = UILightState.Off;                   // 初始状态

// 状态切换
uiLight.State = UILightState.Off;    // 关闭（灰暗）
uiLight.State = UILightState.On;     // 常亮（绿色）
uiLight.State = UILightState.Blink;  // 闪烁（绿色闪烁）
```

#### 大小写陷阱：ON vs On

曾错误地使用了全大写的 `"ON"` 字符串来设置 UILight 状态，导致状态切换无效。SunnyUI 的 `UILightState` 枚举定义的是 `On`（首字母大写），而非 `"ON"`。

---

## 来源

本文档由以下 15 篇独立 lesson 合并整理而成：

1. `CodeGraphIntegrationGuide.md` — 代码图谱集成使用指南（**2026-08-19 已废弃，本节历史参考**）
2. `Log-Append-Position.md` — 日志追加位置规则
3. `NuGet-Satellite-Assemblies.md` — NuGet 卫星资源程序集清理（历史参考）
4. `RunRecordManager-RecordIni-StaleAbsolutePath.md` — Record.ini 绝对路径迁移失效（历史参考）
5. `ScottPlot-FormsPlot-Usage.md` — ScottPlot.FormsPlot 4.1.74 图表用法
6. `VirtualCameraSelectionInInit.md` — 工作流初始化必须用 CameraSelector.Active
7. `VirtualContour-NonZeroZRange.md` — 虚拟相机合成轮廓 YZ 范围非零
8. `SimStart-NeedsInitAwait.md` — 线激光 Initialize 异步，须等待 Standby 事件
9. `SimWeldLength-StopNotAbort.md` — 模拟测试行程到达 = 正常停止
10. `LiveMode-Exclusion.md` — Live 模式不触发 AcquisitionCompletedSignal
11. `MvCameraControl-NativeRuntime.md` — 海康相机原生运行时依赖
12. `StartupSingletonInitialization.md` — 单例持久化须在启动时加载
13. `Assimp-RootNode.md` — Assimp 导入必须整体添加 Root
14. `Bounds-Sentinel-BlackScreen.md` — Bounds 哨兵值导致黑屏
15. `UILight-Property.md` — UILight 控件属性误用（历史参考）

所有原始文件位于 `wiki/lessons/` 目录下。

---

*生成时间：2026-08-18 | 基于 15 篇 lesson 合并整理*

---

## §3 Python 批量重构脚本两坑（2026-09-01 实测）

### 坑一：`find()` 闭包引用旧列表 → 切片索引错位（本次事故）

批量重排脚本的 `find(pred, start=0)` 若闭包捕获旧列表 `lines`，而后续切片作用于新列表 `new_lines`（插入/删除 N 行后），所有定位整体偏移 N——本次把属性块切错、构造函数片段复制出孤儿体，文件直接损坏。

**规避**：查找函数把列表作为参数传入（`idx(ls, pred, start)`），每步操作后重新定位；或全程只在一个列表上就地 `del`/切片赋值，不制造第二个列表。

### 坏一即停：先备份、先校验大括号平衡

批量移动后立刻跑 `code.count("{") == code.count("}")` + region 配对 + 关键符号 grep 三项校验；发现损坏立即 `tar -xzf 备份.tar.gz -O <成员路径> > 恢复.cs` 单文件还原（`-O` 输出到 stdout，`-C` 解包整个目录），不要手补。

### csharp_review.py 解析精度补丁（同日三轮）

① get/set 访问器体不屏蔽 → setter 局部变量被误判为字段（成员顺序假警告）；访问器无参数列表，METHOD_SIG_RE 匹配不到，须用独立正则 `\b(get|set)\s*\{`；
② 表达式体成员（`Instance => _lazy.Value;`）头部被 FIELD_RE 误匹配为字段——FIELD_RE 的 match 终点在 `;` 之后，前瞻必须回看整个匹配文本（`'=>' in m.group(0)`）；
③ 方法组引用（`new Thread(RunLoop)`）不算调用 → 私有方法「无调用」假告警，补充 `\bname\b\s*[,)]` 检测。
