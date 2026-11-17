---
title: IntelligentLaser-Ui-State
date: 2026-10-30
updated: 2026-10-30
tags: [教训, 相机, 英莱, IntelligentLaser, 汇总, Job]
status: active
---


# 英莱相机教训：UI 层与状态管理

> 本页为 [[lessons/IntelligentLaser-Pitfalls]] 的拆分页，仅含第 5 节。

---


## 5. UI 层与状态管理

### 5.1 相机开启时禁止切换帧率（SDK 运行时限制）

**问题**

采集相机开启状态下调用 `SetSensorFpsModel` 切换帧率模式，SDK 会报错（返回非 0）。原因是帧率模式涉及传感器采集管道的重配置，采集运行中无法热切换。

**影响**

- 用户在相机开启状态下切换帧率 → 失败提示，体验差。
- 若 UI 未做保护，频繁失败提示可能导致用户误以为 SDK 或设备故障。

**修复 / 规避**

1. **UI 层下拉禁用**：`ILCamPage.UpdateFpsDropdownState()` 根据 `IsCaptureCameraOn()` 结果设置 `cmbFps.Enabled`——相机开启时禁用，关闭时恢复。
2. **二次校验**：`cmbFps_SelectedIndexChanged` 中再次检查相机状态，若已开启则弹警告并回滚下拉选中项（`RefreshFpsSelect()`）。
3. **自动模式下已禁用**：`UpdateModeUi` 自动运行分支也会禁用 `cmbFps`，双重保险。

**通则**

- 涉及硬件运行时配置变更的操作，先查硬件状态再决定 UI 可用性，不要依赖用户自觉。
- 下拉/按钮等交互控件须有「前置检查 + 后置回滚」双重保护。

### 5.2 实测 FPS 首帧必须剔除

**问题**

从第一次拿到数据开始计算帧率时，第一次计算的帧间隔是「上次重置时间 → 第一帧」的时间差，这个间隔可能很长（几秒甚至几分钟），导致 FPS 值极小，完全错误。

**影响**

- 相机刚开启时，实测 FPS 标签显示异常低的值（如 0.1Hz），误导用户。
- 需等第二帧后才恢复正常值，第一帧错误值闪烁体验差。

**修复 / 规避**

1. **首帧剔除机制**：用 `_firstFrameSkipped` 标志位，第一帧只记录 `_lastFrameTime`、不计算 FPS；从第二帧开始用 `1000ms / 帧间隔(ms)` 计算。
2. **重置时机**：`ResetMeasuredFps()` 将 `_lastFrameTime` 置 `MinValue`、`_firstFrameSkipped` 置 false、`_measuredFps` 置 0。`SetSensor(true)` 开启采集时自动调用重置，确保每次重开都从干净状态开始。
3. **UI 显示**：`lblMeasuredFps` 初始文本 "实测帧率：0.0 Hz"，首帧期间保持 0.0，第二帧后开始显示真实值。

**通则**

- 任何基于「两次间隔」的实时计算，首次数据点都要做剔除或标记处理。
- 计数器/计时器重置后，第一次结果不可信。

### 5.3 UI 层禁止直接引用 SDK 原生类型

**问题**

UI 层（`UIDesign/` 目录下）代码直接 `using IntelligentLaser_CSharp;` 并使用 SDK 原生枚举（如 `EmIntelligentFpsModel`）、原生结构体，违反「UI 不直接触碰 SDK」的分层原则——SDK 版本升级或更换厂商时，UI 层也要跟着改，且 UI 层依赖 SDK 原生类型增加了耦合面。

**影响**

- UI 层与 SDK 强耦合，换相机厂商时 UI 需大量改动。
- SDK 枚举值变化（重命名、值调整）会波及 UI 代码，不符合「UI 只依赖业务层接口」的架构原则。

**修复 / 规避**

1. **托管枚举**：在 `IntelligentLaserCam.cs` 同命名空间下定义 `IlFpsModel` 托管枚举（STANDERD=1/FAST_SPEED=2/HIGH_SPEED=3），UI 层只使用此托管枚举。
2. **公共方法重载**：`ApplyFrameRateModel(IlFpsModel)` 做 UI 层入口，内部映射到 SDK 枚举后调用私有 `ApplyFrameRateModel(EmIntelligentFpsModel)` 实现。SDK 原生枚举版本降为 `private`。
3. **UI 移除 SDK using**：`ILCamPage.cs` 移除 `using IntelligentLaser_CSharp;`，整个 `UIDesign/` 目录零 SDK 引用（已 `grep` 全量验证）。
4. **状态查询方法化**：`IsCaptureCameraOn()` / `IsSensorRunning()` / `FetchFpsModel()` / `DetectHardwareStatus()` 等方法封装所有 SDK 状态查询，UI 只调用方法、不触碰 SDK 类型。

**通则**

- UI 层依赖业务层接口，不直接引用第三方 SDK 类型。
- 所有 SDK 原生枚举/结构体在业务层做托管封装（命名空间同级），UI 只使用托管类型。
- 新增公共方法时，优先考虑 UI 层是否需要引入 SDK 命名空间——若需要，应增加托管重载。

### 5.4 连接后必须检测硬件实际状态

**问题**

程序异常退出（崩溃、强制结束进程）后重新连接，SDK 的 `ConnectToSensor` 只是建立网络连接，**不会改变硬件端的激光/相机/传感器状态**——上次开启的激光和相机仍然开着，但软件侧 `_isLaserOn`/`_isCaptureCameraOn` 等状态变量初始为 false，导致 UI 显示与硬件实际状态不一致。

**影响**

- UI 显示「激光已关」但实际激光开着 → 安全隐患。
- UI 显示「相机已关」但实际相机开着 → 用户点「开启相机」可能导致重复开启或 SDK 报错。
- 帧率下拉在相机实际开启时仍可操作 → 切换帧率报错（见 5.1）。
- JOB 参数页面显示离线缓存的默认值，而非当前设备实际值 → 误导用户。

**修复 / 规避**

1. **连接后状态检测**：`ILCamPage.btnConnect_Click` 在 `ConnectManual` 成功后调用 `_ilCamera.DetectHardwareStatus()`，获取 `IlHardwareStatus` 快照（LaserOn / CaptureCameraOn / SensorRunning / FpsModel / CurrentFps），同步到 UI 状态变量与控件文本。
2. **状态查询方法**：`IsLaserOn()`（已有）/ `IsCaptureCameraOn()`（新增，`FetchSensorInfo`→`DwCaptureCameraEnable`）/ `IsSensorRunning()`（新增，`FetchSensorFps` > 0 判断）/ `FetchFpsModel()`（新增，`FetchSensorFpsModel`）分别查询单项状态。
3. **帧率下拉状态联动**：`UpdateFpsDropdownState()` 根据 `IsCaptureCameraOn()` 动态设置可用/禁用，相机开启时禁用帧率切换。
4. **算法编辑页实时参数**：`ILAlgoForm.InitIlModule` 连接时优先 `FetchAllJobParams()` 从设备拉取实时参数，失败才回退离线缓存，确保展开的是当前 Job 的参数。

**通则**

- 「连接」≠「状态重置」——网络连接仅建立通信，硬件端状态不受影响。
- 连接后必须做一次全量状态同步（激光、相机、传感器、帧率模式、当前 JOB 等）。
- UI 状态变量的真值来源是硬件查询结果，而非软件初始值。

### 5.5 手动/自动模式数据流必须分离

**现象**

自动模式（工作流运行）下，`ILCamPage` 仍在回调中刷新轮廓图像和结果表格，与「自动模式数据应外传至 ScottPlot 和自动调整计算」的架构设计不符。页面上还额外提供一个「自动显示」Switch 开关让用户手动控制，增加了复杂度。

**根因**

`ILCamPage.OnContourFrameReady` → `RefreshDisplay()` 无条件刷新画面、轮廓点数、实测帧率、结果表。工作流自动运行时，页面仍在做 UI 绘制，既浪费性能，又造成「同一帧数据既在本页显示又外传」的双重消费混淆。

**修复**

1. `RefreshDisplay()` 增加模式守卫：工作流运行中（自动模式）直接 `return`，不刷新任何 UI 元素。
2. 仅手动/空闲模式下，在本页绘制 Mat（`ShowMat`）、轮廓点数、实测 FPS、结果表。
3. 自动模式下，数据通过 `ContourDataReady` 事件外传：
   - 轮廓数据 → 主页面 ScottPlot 实时显示
   - 焊缝特征点 + 宽度 → 自动调整计算模块
4. 移除「自动显示」`swDisplay` Switch 控件及所有相关逻辑（构造订阅、CheckedChanged、销毁取消订阅、`UpdateModeUi` 使能控制）。

**结论**

- 调试页（`ILCamPage`）是**手动模式**的调试工具，自动模式下不应抢数据做显示。
- 数据分发遵循「单源多订阅」：相机回调是唯一源，`ContourFrameReady`（UI 显示用，节流）和 `ContourDataReady`（数据消费用，全量）是两条独立链路。
- 自动模式下，数据消费者是工作流和 ScottPlot，不是调试页面。

### 5.6 双帧率显示：传感器帧率 vs 回调帧率

**概念区分**

英莱相机有两个不同的帧率概念，UI 上应分别显示、避免混淆：

| 帧率类型 | 来源 | 含义 | 显示位置 |
|---------|------|------|---------|
| **传感器帧率**（ScanRateHz） | `FetchSensorFps` / `SetSensorFpsModel` 设置后读取 | 传感器硬件的采集分析频率（目标帧率），由帧率模式档位决定 | `lblSenorfps`（中列） |
| **回调帧率**（MeasuredFps） | `MillionOutline` 回调逐帧计算（1000ms/帧间隔） | 实际收到回调的帧率，受数据处理、线程调度影响 | `lblMeasuredFps`（右列） |

**设计要点**

- 传感器帧率是**硬件能力/设定值**，连接后从硬件读取一次即可，不会频繁变化
- 回调帧率是**实测值**，每帧更新，首帧剔除后才准确
- 两个帧率并排显示，方便用户判断：回调帧率是否跟上了传感器设定帧率（如果回调帧率显著低于传感器帧率，说明处理链路有瓶颈）

**运行时实时刷新（2026-08-20 修复）**

`ScanRateHz` 不能只在连接时和设置帧率时各读一次——传感器实际帧率可能因曝光、激光强度、环境等因素波动，且用户需要通过它判断「传感器是否达到设定档位」。

修复方案：在 `MillionOutlineCallback` 中增加**节流式硬件查询**，每 500ms 调用一次 `FetchSensorFps` 更新 `_scanRateHz`。

```
传感器帧率刷新策略 = 回调驱动 + 500ms 节流
  ↓
每帧回调进入 → 距上次查询 ≥ 500ms ? → 是 → FetchSensorFps → 更新 _scanRateHz
                                 → 否 → 跳过
```

为什么是 500ms：
- `FetchSensorFps` 是 SDK 硬件查询，有网络/寄存器访问开销
- 60~120fps 回调中每帧查询会显著增加 CPU 占用
- 500ms（2Hz）对 UI 显示来说足够流畅，人眼感知为"实时"
- 帧率是缓慢变化的量，不需要毫秒级精度

**通则**

- 涉及帧率的 UI 必须明确标注是「传感器帧率」还是「回调帧率」，不能笼统写「实测帧率」
- 传感器帧率对应 `ScanRateHz` 属性，回调帧率对应 `MeasuredFps` 属性
- 传感器帧率必须**运行时周期性刷新**，不能只在连接/设置时读一次
- 硬件查询类 API 在回调中使用必须做**节流处理**，不能每帧调用

---

## 5.7 dwInstanceId 参数陷阱

**现象**

- `FetchSensorFpsModel` 返回 `ret=16777216 (0x1000000)` 即 `INTELLIGENT_E_UNINIT`（程序未初始化）
- `IsSensorRunning` 始终返回 false
- 传感器帧率（`ScanRateHz`）始终为 0 或默认值，不刷新
- `DetectHardwareStatus` 读不到帧率

**根因**

英莱 SDK 中几乎所有函数都有一个 `uint dwInstanceId` 参数，**默认值为 1**（对应第一个传感器实例）。如果代码中显式传 `0u`，SDK 会返回 `INTELLIGENT_E_UNINIT` 错误码（实例 0 不存在/未初始化）。

```csharp
// SDK 定义：dwInstanceId 默认值为 1
public static int FetchSensorFps(ref float fFps, uint dwInstanceId = 1)
public static int FetchSensorFpsModel(ref EmIntelligentFpsModel emLevel, uint dwInstanceId = 1)
public static int SetSensorFpsModel(EmIntelligentFpsModel emLevel, uint dwInstanceId = 1)
```

**易错点**

代码中容易出现混用——有些地方使用默认值（正确，实例 1），有些地方显式传 `0u`（错误，实例 0 未初始化）。

```csharp
// ✅ 正确：使用默认值（dwInstanceId = 1）
IntelligentLaser_export.SetSensorFpsModel(model);
IntelligentLaser_export.FetchSensorFps(ref fps);

// ✅ 正确：显式传 1u
IntelligentLaser_export.FetchSensorFps(ref fps, 1u);

// ❌ 错误：传 0u，实例 0 未初始化，返回 INTELLIGENT_E_UNINIT
IntelligentLaser_export.FetchSensorFps(ref fps, 0u);
IntelligentLaser_export.FetchSensorFpsModel(ref model, 0u);
```

**排查方法**

- 遇到 SDK 调用返回 `0x1000000` 时，优先检查 `dwInstanceId` 参数
- 搜索代码中所有 `IntelligentLaser_export.*, 0u)` 模式，确认是否为误传
- 单传感器场景下，统一使用默认值或显式 `1u`

**通则**

- 单传感器场景：**始终使用 SDK 默认值（不传 dwInstanceId）**，避免手写错误
- 如需显式传参：传 `1u`，不传 `0u`
- 新增 SDK 调用时，检查是否有 `dwInstanceId` 参数，确认传值正确
- 代码审查时重点检查 `0u` 参数是否为 `dwInstanceId`

---

### 5.8 回调模式分流：手动/自动模式数据路径必须分离

**问题背景**

英莱线激光相机有两种使用模式：
- **手动模式**：在 `ILCamPage` 手动调试，需要实时显示轮廓画面（Mat）+ 结果表 + 帧率标签
- **自动模式**：工作流运行中，只需要轮廓数据和算法结果外传（ScottPlot + 自动调整计算），不需要在相机页面显示画面

如果两种模式共用同一条回调路径（都生成 Mat + 都触发 UI 事件），自动模式下会浪费大量 CPU/GPU 在无用的画面渲染上。

**最佳实践：回调两步结构**

```
MillionOutlineCallback
├── 第一步：拿数据（所有模式共用，必须执行）
│   ├── 原生数据读取（using inspect）
│   ├── 轮廓点计数 → _lastContourCount
│   ├── 实测 FPS 计算（首帧剔除）
│   ├── 传感器 FPS 刷新（500ms 节流）
│   ├── 构建 PointCloudData
│   └── 读取 InspectResult → _lastInspect
│
└── 第二步：模式分支
    ├── 手动模式 (IsManualMode=true)
    │   ├── 生成/复用 Mat（ConvertContourToMatDemo：持久画布 Clear 重绘 + CopyTo 原地更新 _currentMat，不再每帧 new；2026-08-26 移除双缓冲换帧，详见 §5.10）
    │   ├── AcquisitionCompletedSignal.Set()
    │   ├── 数据记录（AddFrame）
    │   ├── ContourDataReady 事件（数据外传）
    │   └── NotifyFrameReady → ContourFrameReady（UI 刷新）
    │
    └── 自动模式 (IsManualMode=false)
        ├── AcquisitionCompletedSignal.Set()
        ├── 数据记录（AddFrame）
        └── ContourDataReady 事件（仅数据外传，不生成 Mat，不触发 UI）
```

**关键设计点**

1. **第一步拿数据与模式无关**：所有模式都需要读取原生数据、计算 FPS、构建点云、捕获算法结果。这部分不做模式判断，保证数据完整性。
2. **第二步模式互逆**：手动模式生成 Mat 并触发 UI 事件；自动模式不生成 Mat、不触发 UI 事件，仅外传数据。两条路径完全独立，互不干扰。
3. **IsManualMode 属性控制**：由调用方（UI 页面或工作流）设置，默认 true（兼容手动调试场景）。`ILCamPage.UpdateModeUi` 中根据工作流运行状态自动切换。
4. **减少临时变量**：自动模式完全不分配 Mat 对象；手动模式改为**复用持久画布 + 持久 `_currentMat`**（2026-08-26 重构，详见 §5.10），进一步消除每帧 `new Bitmap/Graphics/Mat` 分配，原「双缓冲换帧」已移除。移除不必要的中间引用变量（如 `var contour = inspect.ContourData`）。
5. **状态标签始终更新**：UI 页面的轮廓点、传感器帧率、回调帧率等状态标签不受模式限制，自动模式下也应实时显示（移到模式判断之前更新）。

**验证方法**

- 手动模式：确认画面正常刷新、结果表更新、帧率显示正确
- 自动模式：确认 `ContourDataReady` 事件正常触发、ScottPlot 有数据、工作流调整正常；确认 `ContourFrameReady` 不触发、`CurrentMat` 不更新（节省资源）
- 对比两种模式下的 CPU/GPU 占用率，自动模式应有明显下降

---

### 5.9 主界面轮廓 ScottPlot 必须每帧 Refresh（刷新放错分支导致冻结）

**问题现象**

主界面（`MainPage`）英莱轮廓 ScottPlot 出现「轮廓显示不对、运到（运行时）不刷新」。

**根因**

`MainPage.IlCamera_ContourDataReady` 回调里，信号处理（填充 `double[1920]` Signal 数组、`MaxRenderIndex` / `SampleRate` / `OffsetX`、特征点 `IsVisible`）每帧都执行，但 **`SetAxisLimits` + `Refresh()` 被放在 `else`（无有效焊缝结果）分支内**：

```csharp
if (e.HasValidResult)
{
    _featureXs[0] = e.Inspect.FeatureY; ...
    _featurePointPlot.IsVisible = true;   // 有焊缝时只显特征点
}
else
{
    _featurePointPlot.IsVisible = false;
    formsPlot1.Plot.SetAxisLimits(...);
    formsPlot1.Refresh();                 // ← Refresh 仅在此分支执行
}
```

生产态一旦 `HasValidResult==true`（识别出焊缝，正常工况），整帧既不重设轴范围也不 `Refresh()` → 轮廓曲线与特征点**永久冻结**，表现为「画面不动、轮廓陈旧/错位」。

**修复（2026-08-26）**

将 `SetAxisLimits` + `Refresh()` 提到分支外，**每帧**执行（与 ADR-003 Signal 模式「每帧原地修改数组 → Refresh 重绘」设计一致）。`AddContourLineChart` 订阅入口（`FormMain` 构造已显式调用）正常，根因就是刷新语句位置错误，非订阅/初始化问题。

**通则**

- ScottPlot（任何模式）的 `Refresh()` 必须与数据更新放在**同一控制流**中；切勿把刷新塞进某个条件分支，否则该分支不命中时画面冻结。
- 实时曲线「不刷新」优先排查 `Refresh()` 是否真的每帧可达，而非先怀疑数据源。

### 5.10 轮廓 Mat 复用持久画布（每帧 Clear 重绘，替代每帧 new）

**问题（用户提问）**

`ConvertContourToMatDemo`（GDI+ 绘制轮廓/校准框/特征点到 `Bitmap` 再 `ToMat()`）原先**每帧** `new Bitmap(834,554)` + `Graphics.FromImage` + `bmp.ToMat()`，回调（手动模式 ~60fps）下产生大量托管 Bitmap 与 unmanaged Mat 分配，GC 抖动大、显示更新延迟高。用户提议：「能否只用一个 Mat，setto0 后重绘？」

**结论（回答用户）**

**可以，且更优**。复用单一 `Bitmap` / `Graphics` / `_currentMat` 的代价：
- **资源占用**：消除每帧约 1.8MB `Bitmap` + `Graphics` + `Mat` 分配，GC 压力与 LOH 碎片显著下降；
- **显示延迟**：省去分配/回收开销，出帧到 `imageBox` 刷新更快；
- **仍线程安全**：`_currentMat` 在 `_matLock` 内原地更新，`CurrentMat` getter 克隆返回，调用方独占。

**修复（2026-08-26 实现）**

- 新增持久字段 `_canvasBmp`(`Bitmap`) / `_canvasG`(`Graphics`) / `CanvasW` / `CanvasH`，`EnsureCanvas()` 首次创建、之后复用；
- `ConvertContourToMatDemo` 改为 `void`，在 `lock(_matLock)` 内：`_canvasG.Clear(bg)` → 沿用原 `g`/`bmp` 绘制逻辑 → `UpdateCurrentMatFromCanvas()`；
- `UpdateCurrentMatFromCanvas()`：首帧 `_currentMat = _canvasBmp.ToMat()`（新建），后续 `_canvasBmp.ToMat()` 临时 Mat `CopyTo(_currentMat)` **原地复用**（同尺寸/类型时零新分配）；
- 回调手动分支移除「双缓冲换帧（`newMat` 交换 + 旧帧 `Dispose`）」，改为直接调用 `ConvertContourToMatDemo`（内部原地更新 `_currentMat`），天然替换原换帧临界区；
- `ReleaseNativeResources` 同步 `Dispose()` `_canvasG` / `_canvasBmp`，避免 GDI 句柄泄漏。

**注意事项**

- 采用 `Bitmap.ToMat()` + `Mat.CopyTo()`（Emgu.CV 4.x 确定性 API），未依赖 `Mat.ImportBitmap`（部分版本无此 API），版本安全。
- 绘制与 `_currentMat` 更新均在 `_matLock` 内串行，与 `CurrentMat` getter 互斥；销毁路径 `_matLock` 与绘制互斥，无竞态。
- 若后续接入 `ImportBitmap` / `Image.Bitmap` 共享内存画法，可进一步消除 `ToMat()` 临时 Mat，但当前 `CopyTo` 复用已满足「单 Mat 复用」目标。

---

### 5.11 主界面轮廓 ScottPlot 轴范围「连接时锁定、每帧只刷新数据」

**问题（用户需求 2026-08-27）**

主界面轮廓图（`MainPage.IlCamera_ContourDataReady`）原先**每帧**重算校准框轴范围 + 每帧 `SetAxisLimits`。用户指出：相机连接后校准数据只更新一次，轴范围（主轴 Y / 纵轴 Z）不变更，每帧重设轴范围既无意义又违背「连接后固定视图」的意图。

**结论 / 修复（2026-08-27 实现）**

- 新增 `bool _contourAxisLocked` 字段：轴范围是否已锁定。
- ① 轴范围计算加 `!_contourAxisLocked` 守卫——**仅首次**有效数据（校准框四角点已就绪）时 `SetAxisLimits` 锁定，并置 `_contourAxisLocked = true`；之后（未重连）跳过整个轴计算与 `SetAxisLimits`。**横轴 X（沿激光线，= 数据 Y 坐标）与纵轴 Y（高度，= 数据 Z 坐标）一律用校准框四角点 min/max 锁定，含负值，加 ±5% 边距**：即用户原「连接相机时用回调确认轴的限度（相机最大最小值，含负值）」方式，范围来自相机校准框、**不随实时数据动态规划上下限/左右限**。
- ④ 每帧只 `formsPlot1.Refresh()` 重绘轮廓与特征点，**不再重设轴范围**。
- `SubscribeContourCamera()` 重订阅时复位 `_contourAxisLocked = false`，使相机切换/重连后用新校准框重新锁定。
- 每帧仍保留生产者线程填充 SignalXY 双数组（`_contourSignalXs[i]=points[i].Y`、`_contourSignalData[i]=points[i].Z`）与特征点快照——纯数据更新，非改轴（详见 §5.16）。

**注意事项**

- 锁定时机 = 相机连接后校准框四角点首次就绪的帧（等价于用户所说「连接时」）；若校准框数据始终不到达，轴保持 `_contourYMin/Max`/`_contourZMin/Max` 默认回退范围（含负值，不锁定、每帧轻量检查）。
- 与 ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） 决策3（Signal 模式每帧刷新）不冲突：刷新照常 60Hz，仅轴范围从「每帧重设」改为「连接时一次锁定」。
- 切勿把 `SetAxisLimits` 重新放回每帧（会回到无意义开销）。校准框量程（含负值）通常远大于单条焊缝 Z 起伏，轮廓在固定相机量程视图下显得平缓属预期——这是用户明确的「固定相机量程」选择，不要为放大起伏而改用数据范围（见 §5.15 回退说明）。

### 5.12 主界面轮廓 Signal 轴映射：Y→X 轴、Z→Y 轴（首末点锚定防镜像）

主界面轮廓 ScottPlot（`MainPage.IlCamera_ContourDataReady`）需显示英莱传来的 `Point3D` 的 **Y 与 Z**：**Y 作 X 轴（沿激光线物理坐标 mm）、Z 作 Y 轴（高度 mm）**。约定与 imageBox 的 `ConvertContourToMatDemo` 坐标变换 `trans(y,z) => (center.X + y*rate, center.Y - z*rate)`（Y→横、Z→纵）保持一致，确保主界面与调试页朝向相同。

**轴赋值本身正确**（已核对）：
- Signal Y 数据 = `points[i].Z`（`_contourSignalData[i] = points[i].Z`）；
- SignalXY X 轴 = 显式数组 `points[i].Y`（`AddSignalXY(xs, ys)` 逐点真实 X，非均匀布点，终版方案）；
- 特征点散点 `_featureXs[0] = e.Inspect.FeatureY`、`_featureYs[0] = e.Inspect.FeatureZ`。

**隐患（曾导致"信号不正确/镜像"）**：原代码用 **全局 Y 极值**（`yMinPt/yMaxPt` = 整帧 min/max）作 `OffsetX/SampleRate`。这隐含假设轮廓点序一定是「小→大」。若英莱 SDK 返回点序为「大→小」（首点 Y = maxY），则 `OffsetX` 取全局 minY、曲线整体**左右镜像**，ScottPlot 与 imageBox 朝向相反——用户观感即"轮廓显示不对"。

**修复（早期方案，已被 §5.16 的 AddSignalXY 取代）**：`OffsetX/SampleRate` 锚定**首末点的真实 Y** 曾用于消除镜像；现终版改用 `AddSignalXY` 显式传 X，详见 §5.16：
```csharp
double yFirst = points[0].Y;
double yLast  = points[pointCount - 1].Y;
double dy = yLast - yFirst;
if (Math.Abs(dy) > 1e-6)
{
    _contourSignalPlot.SampleRate = dy / (pointCount - 1);
    _contourSignalPlot.OffsetX = yFirst;
}
```
- 升序点序（point[0]=minY）下与旧逻辑**数值完全等价**，零回归；
- 降序点序下 `dy<0` → `sampleRate` 为负，曲线自动反向绘制，与 imageBox 一致，消除镜像；
- 仅取首末点，不依赖全局极值，对"点序非严格单调"也最稳健（激光轮廓点沿扫描线基本等距，首末锚定足够）。

**教训**：ScottPlot `AddSignal` 的 X 是「索引×SampleRate+OffsetX」的**均匀布点**，不是逐点真实 X；当轮廓点 X 方向**非等距**时，X 位置算错、线形扭曲甚至局部压平。此类场景应改用 **`AddSignalXY(xs, ys)`**（显式 X + 保留 Signal 性能），而非 `AddScatter`（性能差）。终版见 §5.16。

**坐标系澄清（2026-08-27 用户）**：imageBox 与 ScottPlot **不必一致**。imageBox 因屏幕像素只能取正值、无负值，必须做 `center + y*rate` 平移（把 (0,0) 移到图像中心）才能显示；ScottPlot 直接绘原始数据坐标，**负值如实显示、不做任何平移**。故主界面轮廓与调试页 imageBox 的视图「不重合」属预期，绝不可为"与 imageBox 一致"而给 ScottPlot 加平移/居中。两者仅「朝向」相同（Y→横、Z→纵）。

**英莱轮廓点默认按 Y 轴由小到大排列**：故 `points[0].Y` 即最小、`points[last].Y` 即最大，首末锚定 = min/max；首末锚定对正常升序点序数值等价（零回归），且对点序偶发变化（大→小）也不会镜像（见上方 修复）。

### 5.13 主界面轮廓 Signal 初始不可见（不渲染 Z=0 假轮廓线）

**现象（2026-08-27）**：程序启动、未连接相机时，主界面 ScottPlot 却画出「一段奇怪的轮廓点／一条横线」，用户要求初始化时不要显示无关点。

**根因**：`_contourSignalData = new double[1920]` 全为 0；`AddSignalXY` 默认 `MaxRenderIndex = int.MaxValue` 会渲染全部 1920 个点 → 一条 **Z=0 的平直假轮廓**横跨整个 X 轴。未连接相机时无 `ContourDataReady` 帧，但 Signal 图已绑定该数组，故一打开就显示这条零线。

**修复**：`AddContourLineChart` 中 `AddSignalXY` 之后立即 `_contourSignalPlot.IsVisible = false`（不渲染空/零数据）；`IlCamera_ContourDataReady` 在确认 `pointCount > 0` 后首帧置 `IsVisible = true`；`SubscribeContourCamera()`（重订阅/重连）复位 `IsVisible = false` 防残留。默认轴范围（`SetAxisLimits` 默认回退值）仍保留，呈现干净的「空坐标 + 标签」无数据态，而非假轮廓线。

**教训**：Signal 图绑定固定数组时，初始化必须 `IsVisible=false` 或 `MaxRenderIndex=-1`，**绝不可让全 0 数组直接渲染**。与 §5.9（每帧 Refresh）不冲突：刷新照常，只是首帧前不显示。特征点散点（`_featurePointPlot`）本就初始 `IsVisible=false`，无需改动。

---

### 5.14 主界面轮廓 ScottPlot：高频事件禁止逐事件 BeginInvoke + 重活（合并派发 + 生产者预拷贝）

**问题现象（2026-08-27）**：使用 ScottPlot 后 ① 程序内存持续上涨 ② 主页面卡死、只有轮廓表在动。同时轮廓被报「显示为一条直线」。

**根因**：
- ①+② 同一根因：`ContourDataReady` 在相机回调内**无条件高频触发**（对比 `NotifyFrameReady` 有 16ms 节流，此处没有）。旧 `IlCamera_ContourDataReady` 用 `BeginInvoke` **逐事件**把「1920 点数组填充 + 首帧 SetAxisLimits + 全量 Refresh 重绘」整段重活封送 UI 线程。当相机帧率 > UI 刷新能力时，BeginInvoke 队列**无界堆积** → 委托 + 捕获的 `ContourDataEventArgs` + 数组拷贝越积越多（内存↑），UI 线程被渲染占满（卡死、仅图表在动）。
- ③（直线）根因确认：经对比 ImageBox（可见起伏）与 ScottPlot（平线），确认是**校准框量程（含负值，通常 ±几 mm 乃至更大）远大于单条焊缝 Z 起伏（0.0x~0.x mm）**，轮廓在固定相机量程视图下显得平缓。用户明确选择保留「连接时校准框量程锁定」（§5.11 终版），故此「平缓」属预期；曾尝试的「纵轴 Z 用数据实际范围锁定」已回退（见 §5.15）。「延迟读被回收缓冲」(b) 已由生产者预拷贝消除，「字段错」(c) 已排除（Y→X/Z→Y 映射正确，与 ImageBox 一致）。

**修复（2026-08-27 实现）**：
- 删去临时调试 `return;` 桩，恢复回调工作。
- **生产者线程立即预拷贝**：回调一进来先把 `points[i].Z`、Y 映射、特征点、首帧校准判定拷入复用数组/快照字段，再派发——彻底消除「延迟读被回收缓冲」（候选③-b）。
- **合并派发**：用 `volatile bool _uiUpdatePending` 保证 BeginInvoke 队列**最多 1 个待处理**（`if (_uiUpdatePending) return; _uiUpdatePending=true; BeginInvoke(UpdateChartUI)`），根治队列堆积（内存↑/卡死）。
- **`UpdateChartUI`（UI 线程）只做轻量**：应用轴锁定一次 + `MaxRenderIndex`（X 由显式 `_contourSignalXs` 给定，无需 `SampleRate`/`OffsetX`） + 特征点显隐 + `Refresh()`，`finally` 复位 `_uiUpdatePending`；ScottPlot 属性只在 UI 线程触碰，避免跨线程。
- **诊断代码已删除（2026-08-27 用户要求）**：原 `_contourDiagEnabled`/`_diagFrameCounter` 诊断门控（每 ~30 帧打印 `Z` 数据与锁定轴范围）已整体移除，不再保留于代码中。

**教训**：
- 高频相机/传感器事件**禁止逐事件 `BeginInvoke` + 在封送体内做重活**；必须「生产者预拷贝数据 + 合并/节流派发（volatile 标志或 Timer 限 ~60Hz）」，否则必现内存泄漏 + UI 饱和。
- 跨线程传递数据**不要延迟读调用方缓冲**：在生产者线程立即拷进自己的复用数组，封送只传「已落定的快照」。
- 与 ADR-003 Signal 模式「每帧刷新」、§5.9（每帧 Refresh）、§5.11（轴锁定：校准框量程）、§5.12（Y→X/Z→Y）、§5.13（初始不可见）、§5.16（AddSignalXY）均不冲突：刷新照常，仅把「数据拷贝」与「UI 重绘」拆到两个线程。

---

### 5.15 主界面轮廓 ScottPlot：曾尝试「纵轴 Z 用数据实际范围」已回退为校准框量程（§5.11 终版）

**现象（2026-08-27 早期尝试）**：ScottPlot 轮廓显示为一条水平直线，而同数据的 ImageBox 显示明显起伏的倾斜轮廓。

**早期根因与修复（已回退）**：原 §5.11 首帧锁定时横轴/纵轴均用**校准框**四角点范围（含负值，覆盖整个视野，通常 ±几 mm）。实际焊缝在该视野内的 Z 向起伏往往只有 **0.0x ~ 0.x mm**，在 8mm 级纵轴里几乎不可见 → 看起来是平线。ImageBox 的 `ConvertContourToMatDemo` 在校准模式下把同一小变化放大成多像素，放大倍率不同，并非数据问题。曾改为「纵轴 Z 用本帧数据实际 min/max + 边距、横轴用校准框范围」以放大起伏。

**回退决定（2026-08-27 用户明确要求）**：用户确认轮廓轴范围**使用原方式**——连接相机时用回调确认轴的限度（相机最大最小值，含负值），**不实时规划上下限/左右限**。即终版以 §5.11 的「校准框四角点 min/max + ±5% 边距、连接时锁定一次」为准。「平缓」是固定相机量程视图的固有表现，可接受，不应为放大起伏而改用数据范围。

**注意**：本条目仅作历史记录，防止误把已否决的「数据范围」方案重新引入；当前权威结论见 §5.11。

---

### 5.16 主界面轮廓 ScottPlot：X 非等距必须用 AddSignalXY，而非 AddSignal / AddScatter

**结论（2026-08-27 用户确认）**：轮廓点沿激光线的物理坐标 Y 在 X 方向**非等距**（相机采样疏密不均、偶发空档）。

- `AddSignal(ys)`：X 只能靠 `SampleRate`/`OffsetX` 推算**等距**布点 → 点序非均匀时 X 位置算错、线形扭曲/局部压平。
- `AddScatter(xs, ys)`：支持非等距 X，但属通用散点、**逐点绘制、性能差**（1920 点高频刷新拖累帧率）。
- **`AddSignalXY(xs, ys)`（终选）**：X 由显式数组逐点给定（支持非等距），且**仍走 Signal 高性能渲染路径**（Min/Max 降采样 + 零分配），兼顾正确性与性能。

**落地（2026-08-27 实现）**：`MainPage.AddContourLineChart` 用 `AddSignalXY(_contourSignalXs, _contourSignalData)`；生产者线程 `_contourSignalXs[i] = points[i].Y` 与 `_contourSignalData[i] = points[i].Z` 一并预拷贝；`UpdateChartUI` 不再设 `SampleRate`/`OffsetX`。字段 `_contourSignalXs` 与 `_contourSignalData` 同长 1920，复用不每帧分配。

**注意**：`AddSignalXY` 按数组顺序连线，要求 X 单调（升/降）才能正确连成轮廓；本项目英莱点序默认按 Y 升序，符合。若点序偶发非单调，线会折线/乱跳，需排序或回退 `AddScatter`。

---

### 5.17 主界面 plot2：参考线的绘制时机 + `Plot.Legend()` 是方法不是属性（不 Clear 又调 Legend ⇒ 图例叠加）

**现象（2026-10-21 业主报）**：主界面初始化时 plot2「焊缝宽度上下限参考线」被画了两次，**右下角图例区出现 4 条 txt 记录**（上下限各 2 条）；业主要求：**开始焊接后才画上下限，不是初始化就画**。

**根因 1 —— 两条初始化路径各自建了一次图例**：

| 路径 | 调用链 | 对 plot2 的动作 |
|---|---|---|
| A | `FormMain.LoadNavAndPages()` → `mainPage.AddNewDataLineChart()` → `RefreshParamCharts()` | `Plot.Clear()` → 画曲线 + 画上下限 → **`Plot.Legend()`** |
| B | `MainPage_Shown`（绑在 `this.Load`）→ `AfterInitializeUI()` → `SetupMergedChart(formsPlot2)` | **不 Clear** → 只设标题/轴标签 → **再 `Plot.Legend()`** |

⚠️ **ScottPlot 4.1 的 `Plot.Legend()` 是「方法」不是「属性」**：每次调用**新建一个 `Legend` renderable 并注册进 plot**。路径 B 不 Clear ⇒ plot2 上同时存在 **2 个 Legend 实例**，每个图例都自动收集 plot 上带 label 的项（焊缝宽度 + 焊缝宽度上限 + 焊缝宽度下限）⇒ 同一份条目被渲染两遍 ⇒ 右下角出现 4 条 txt 记录（2 个图例 × 2 条上下限）。

> **运行期实测（`ScottPlot.dll` 反射 + 实例化，非猜测）**：`Plot.Legend()` 签名 = `Legend Legend(bool?, Alignment?)`（方法）；`Plot.Clear()` 会清掉全部 renderable（含图例）⇒ **每轮刷新后只留 1 个图例**；不 Clear 又调 Legend ⇒ 叠加。

**根因 2 —— 参考线在初始化期被画**：上下限依**自适应参数配置**（`CurrentAutoParam.SeamWidthMax/Min`）而来，起焊前配置可能仍在调整，此时画出的参考线既无工艺意义、又叠加图例条目。

**修复（2026-10-21）**：

1. **参考线加「焊接开启」门控**：`AddSeamWidthLimitLines` 入口先判 `IsWeldModeActive`（整机 `Running`＝真焊+模拟，**与相机预览门控同源**，不另造状态源）——未起焊不画；起焊后随每轮 `RefreshParamCharts` 按当前配置**重画**（`Plot.Clear()` 已清理前一批 renderable，满足「按设定重新画、清理掉前面的」）。新增日志状态 `skip-not-welding`（**Info 级**，未起焊不是异常）以便现场区分「未起焊」/「未配置」/「上下限填反」。
2. **图例所有权单一化**：`SetupMergedChart` 降级为「只设标题/轴标签」，**不再建图例**；plot2 图例统一由 `RefreshParamCharts` 路径创建（该路径先 `Plot.Clear()`）。

**通用教训**：

- ⛔ **同一张图的图例只能有一个创建点**。多路径初始化时，**只让「会 Clear 再重建」的那条路径持有图例**；纯设标题/轴标签的路径不得再调 `Plot.Legend()`。
- ⛔ **ScottPlot 4.1 的 `Plot.Legend()` 是方法**（返回新 `Legend` 实例），不是可反复安全调用的属性——误当属性用会静默叠加。
- ⛔ **业务参考线/门限线只在业务真正开始后画**（起焊后），不要在初始化期画「依配置设定、但配置尚未定型」的值。
- ✅ **判据可静态化**：①「画参考线的方法体内必须出现业务门控（`IsWeldModeActive`），且门控分支内不得出现绘制调用」；②「同一图上 `Plot.Legend()` 的调用点数」；③「不 Clear 的路径里不得出现 `Plot.Legend()`」。

---

### 5.18 图表初始化期重复构图：同一张图被构建两遍 + `Plot.Clear()` 会清掉标题/轴

**现象（2026-10-21 业主报）**：`RefreshParamCharts` 在初始化阶段执行**两次**；业主要求「初始化只建立一次，UI 刷新与切换刷新在初始化时不应执行（重复构图浪费资源）」，并要求排查其它控件的同类问题。

**根因（MainPage plot2）**：

| # | 路径 | 触发时机 | 做的事 |
|---|---|---|---|
| ① | `FormMain.LoadNavAndPages()` → `mainPage.AddNewDataLineChart()` → `RefreshParamCharts()` | **FormMain 构造期** | `Clear()` + `AddSeries` + `Legend()` + `Refresh()` —— 此时算法输出缓存**尚无任何点**，画出来的是一张**空图** |
| ② | `AddContourLineChart()` → `StartProfilePolling()` → 轮询线程首帧 `AdjustmentOutputVersion != _lastParamVersion` → `BeginInvoke(RefreshParamChartsUi)` | 构造后 **33ms 内** | 又一次 `Clear()` + 重建（这次才有数据） |

⇒ ① 纯属浪费：紧接着被 ② 的 `Clear()` 推翻重画。

**同源的第二处**：`AfterInitializeUI()`（绑 `this.Load`）里 `SetupChart(formsPlot1, …)` 对已由 `AddContourLineChart` 完整构建过的 plot1 **重复设标题/轴**，且其 `Plot.Legend()` 在**不 Clear** 的路径上叠出第二个图例实例（与 §5.17 同一根因）。

**⭐ 连带发现（此前一直存在、无人察觉的隐患）**：**`Plot.Clear()` 会连同 `Title`/`XLabel`/`YLabel` 一起清掉**。

> **运行期实测**（`ScottPlot.dll` 反射 + 实例化 `ScottPlot.Plot(400,200)`，非猜测）：Clear 前后渲染位图 **8324 → 6256** 字节；"有标题"与"无标题"两张同系列图位图**不同**（6188 vs 5700 字节）⇒ 标题确实参与渲染且被 Clear 抹掉。
> ⇒ 任何「`Clear()` 后重建系列」的路径都必须在 Clear 之后**重设标题/轴**，否则**首帧之后图表标题会消失**。本项目 `RefreshParamCharts` 与 `RebuildChartDatasets` 此前都漏了这一步（既有缺陷，本轮一并修复）。

**修复（2026-10-21）**：

1. **初始化期不构图**：`AddNewDataLineChart()` 不再调 `RefreshParamCharts()`（只做订阅/准备）；首帧构图交给轮询线程**首次数据到达**（此时有数据、有图例，一次到位）。代价：算法首次执行（起焊/有机器人位置）前 plot2 只有坐标轴、无数据线与图例。
2. **每张图只有一个构建路径**：
   - plot1 → `AddContourLineChart()`（Clear + 建 2 系列 + 设轴 + **建图例**）
   - plot2 → `RefreshParamCharts()`（Clear + **重设标题/轴** + 建系列 + **建图例**）
   - plotData（数据追溯页）→ `RebuildChartDatasets()`（Clear + **重设标题/轴** + 建系列 + **建图例**）
   - `SetupChart`（0 调用者）删除；`SetupMergedChart` 降为**纯兜底**（不建图例）；`DataReviewerPage.AfterInitializeUI` 不再建图例。
3. **其它页面排查结论**：`SystemControlPage` / `ProcessControlPage` / `FilebackupPage` / `SubDialog/` 各弹窗**无任何 ScottPlot 调用** ⇒ 无同类问题。

**通用教训**：

- ⛔ **初始化期不要「先建空图再重建」**：构造期数据源通常还是空的，此刻 `Clear+AddSeries+Legend+Refresh` 全套开销白费，且下一帧就被推翻。正确做法：初始化只做订阅/准备，首帧构图交给**带数据的那一次**触发。
- ⛔ **`Plot.Clear()` 不是「只清系列」**：它连标题/轴一起清。`Clear()` 后必须重设 `Title`/`XLabel`/`YLabel`。
- ⛔ **同一张图的「Clear+建系列+建图例+设轴」只能有一个方法负责**，别处不得重复（尤其不要在不 Clear 的路径上再调 `Legend()`）。
- ✅ **判据可静态化**：①「初始化用的 public 方法体内不得调用重建方法」；②「同一图上 `Plot.Legend()` 的调用点数 == 1，且落在唯一构建路径上」；③「每个 `Plot.Clear()` 之后的 N 行内必须出现 `Title`/`XLabel`/`YLabel`」。

---

## 相关页面

- [[lessons/IntelligentLaser-Sdk-Interop]] —— 同源拆分页
- [[lessons/IntelligentLaser-Callback-Mechanism]] —— 同源拆分页
- [[lessons/IntelligentLaser-Delegate-Gc]] —— 同源拆分页
- [[lessons/IntelligentLaser-Job-System]] —— 同源拆分页
- [[lessons/IntelligentLaser-Pitfalls]] —— 源页（拆分前全量）
