﻿﻿---
title: MonitorCam 模块 — 自动焊接头监控相机（三层：IMonitorCam / HikCam / MonitorCamManager）
date: 2026-08-03
updated: 2026-11-09
tags: [模块, 相机, 监控, 焊前对中, 焊中质检, HikCam, 海康MVS, 三层架构, IP扫描]
source: raw/knowledge/AdaWeldSystem_Wiki.md (新增)
---

# MonitorCam 模块 — 自动焊接头监控相机

> 独立监控相机模块：负责焊前激光光斑/焊丝对中检测、焊中焊接质量检测，两者均具备画面输出与结果输出。
> **2026-09-08 三层重构（ADR-034 accepted）**：抽象层 `IMonitorCam/`、实现层、业务中枢 `MonitorCamManager.cs`，参照 MotionControl 与线激光范式。
> **2026-09-09 业务边界澄清（ADR-010 accepted）**：监控相机为 **2D 面阵相机，无 Live/PIL 模式切换**；画面显示采用「单次触发采集后刷新 Mat」的方式（与线激光手动调试页同构，频率可控）。
> **2026-09-29 连接入口与 IP 语义（ADR-046 accepted）**：页面顶栏复刻线激光调试页（连接态 + 相机IP + 扫描 + 连接/断开），新增设备扫描三层接口 `ScanDevices` 与 `MonitorCamScanForm` 单选回填；连接 IP **先落盘后连接**（INI），且**指定 IP 必须精确匹配、不匹配即连接失败**（不再静默回退枚举首台）。
> **2026-09-29 实现层切换海康 MVS（ADR-047 accepted）**：麦格威即海康魔改底层的实证成立，实现层由 `MecaVisionCam`（MVCAMSDK）整体切换为 `HikCam`（官方 MvCameraControl.Net V2）；**契约/业务层/UI 零改动**，严格 IP 匹配语义无损继承；麦格威实现与 6885 行 MVSDK 封装已删除。
> **2026-09-29 页 Tabs 化与录像/回放（ADR-048 accepted）**：`MonitorCamPage` 改 `tabsMonitor` 双页（焊接相机设置/焊接回放）；页1 右侧栏采集/录像/参数/标定四 panel（检测调试与算法参数区删除），页2 录像文件列表右键回放（Emgu VideoCapture）；契约扩展 12 成员（取流/录像/触发/参数），取帧单线程统一喂预览与录像。
> **2026-11-03 录像目录默认值（业主口径「只改默认」）**：`MonitorCamConfig.DefaultRecordDir` 定为唯一默认 `D:\WeldRecord`（INI `RecordDir` 缺失/为空回落，**仅内存纠正不写盘**）；`MonitorCamManager` 构造期 `EnsureRecordDirectory()` **只在运行期检查/创建目录、不写 INI**，失败（无权/盘不存在/网络不可达）**只记 Warning 日志（不弹窗）** + 回退 exe 下 `Record`（内存态，不覆盖配置），不阻塞启动；**不做旧值迁移**（裸盘符根不再判定、不改 INI、不备份 INI，配置由业主自行维护）。参数设置页 `txtRecordDir` 显示 `RecordDirectory` 实际值。
> **2026-11-03 回放列表两级汇总（ADR-078 演进，业主最终口径）**：~~三级懒加载（根 → 日期 → 扫描文件夹 → 文件）~~ → **日期区间 = 日期文件夹选择器**：① `Directory.GetDirectories(RecordDirectory, TopDirectoryOnly)` 一层，过滤落在区间内的 `yyyyMMdd` 目录（倒序）；② 对区间内**每个日期目录**直接 `GetFiles(日期目录, "*.avi", TopDirectoryOnly)`（只取本层、不递归、无「扫描文件夹」中间层），汇总成一张预览列表；③ 表格只渲染文件行（`PlaybackRowKind` 已删除），排序 = 日期倒序 + 日期内文件名序，行「修改时间」= 日期文件夹日期 + 时分；④ 空态 = 「日期区间内无日期文件夹 · 根目录」/「该区间内无录像文件（N 个日期文件夹均为空）」。统一 `RunPlayScan`：后台 `Thread` + `CancellationTokenSource`（`_playLoadCts`）+ 代数（`_playLoadGeneration`），快速改区间旧结果不回填。路径唯一来源 = `MonitorCamManager.RecordDirectory`。
> **2026-11-03 懒加载：初始化不读，进入页面才加载**：`MonitorCamPage` 构造期与 `FormMain` 装配期**不扫描录像目录、不解码缩略图**；首次切到「焊接回放」页签才首扫，`_playListLoaded` + 非空行保证反复切页不重复全量扫描，切走 `CancelPlayScan()`；`刷新列表` / 日期区间变化按新区间重扫。数据追溯页同口径：`DataReviewerPage` 由 `Load` 事件改为 `VisibleChanged` + `_firstShownLoaded` 守卫——初始化/反复切页不读生产记录，首次可见才 `InitPCLDir`。
> **2026-11-03 回放时间基准（ADR-078 修复 3 倍慢放）**：~~定时器 33ms 固定节拍 + 每拍固定推进帧（1.0x = 1 帧/拍）~~ → **时间基准驱动**：`Stopwatch _playClock` + 锚点（`_playAnchorFrames` / `_playAnchorSpeed`），每拍 `TargetPlayFrame() = 锚点帧 + 已播秒数 × Fps × 倍速`，取整后补齐到该帧（中间帧 `Dispose`、末帧上屏），不做「每拍睡固定毫秒 / 固定加 N 帧」的累加；`SeekToFrame` / 倍速切换 / 暂停恢复均 `RebasePlayClock()` 重锚，**切速不重置播放位置、不跳帧错位**。定时器仍只有 `timerPlay`（Interval 33ms 仅作触发节拍，不再承担时间语义），等待不在 UI 线程上做。根因（实测）：旧逻辑总时长 = 帧数 × 实际拍间隔——本机 270 帧 × 46ms = 12.7s（1.41 倍）；现场每拍叠加解码 + 绘制开销 ≈100ms → 27s（3 倍）；单帧纯解码仅 0.8~1.3ms，慢放非解码本身。实测（9s@30fps 素材）：1.0x 9069ms / 0.5x 18055ms / 2.0x 4552ms；1x→2x 中途切速全程 6816ms（理论 6770ms）且切换点 135 帧不变。
> **2026-11-02 回放栏版式修正（ADR-078 演进）**：回放栏最外层 = `gridPlayBar`（`AntdUI.GridPanel`，`Span="fill;fill;-26 fill"`，2 区域逆序入格）；区域 1 = `gridPlayTime`（`AntdUI.GridPanel`，`Span="fill 90 128"`：进度条 `sliderPlay` + 速度 `lblPlaySpeed` + 时间 `lblPlayTime`），区域 2 = `flowPlayButtons`（`AntdUI.FlowPanel`，`Align=Center`，5 按钮逆序入流）；**回放区零原生布局容器**（页级两层同换：`tableLayoutPanelPlay` → `gridPlayPage`（`Span="fill 400;fill 400;-45 fill"`，4 格）；`tableLayoutPlayFilter` → `gridPlayFilter`（`Span="fill 105"`，2 格）；栏内 `tableLayoutPlayTime` → `gridPlayTime`、`tableLayoutPlayCenter` 删除）。倍速 / 前进 / 后退按钮图标化。外层遮罩 `panelPlayBar` 改 `AntdUI.Panel`（`Back=ARGB(128,0,0,0)` 50% 黑 + `Shadow=5` / `ShadowColor=Black` / `BorderColor=RGB(217,217,217)`，`BorderWidth` 默认 0；`Padding` 校准为 (3,0,3,0) 抵消 `Shadow` 5px 内缩，内层仍 603×68），悬停显隐逻辑不变。
> **2026-10-30 回放强化（ADR-078 accepted）**：① 回放页画面底部**悬停显隐的 50% 半透明双层控件栏**（上层进度条 `sliderPlay` + 时间「当前/总时长」，下层慢放/后退5s/播放暂停/前进5s/快放 5 按钮居中，`TooltipComponent` 提供中文提示）；进度以 `CapProp.PosFrames` 为唯一轴，倍速用 33ms 定时器 + 帧累加器（慢 0.8/0.5/0.3/0.1/1.0、快 1.5/2/2.5/3/1.0），旧「停止回放」按钮删除。② 录像落 `RecordDirectory\yyyyMMdd\` 日期子目录（`MonitorCamManager.StartRecord` 统一，手动与模拟焊接自动录像同口）。③ 回放列表按 `DatePickerRange` 日期区间筛选（日期优先取日期子目录名、回退修改时间），行 = **预览缩略图（`CellImage` 96×54）+ 文件名 + 时间 + 大小**，缩略图由后台线程逐行解码首帧（代数计数取消 + `BeginInvoke` 刷新），列表先出占位不阻塞页面。

> **2026-11-09 三层收口（ADR-095 / ADR-097 / ADR-097）**：① 帧边界——UI 不再 `new Mat` / `CvInvoke` / `VideoCapture` / 逐帧解码 / 像素运算；标定十字与软触发取帧下沉 `MonitorCamManager`（`RelayPreviewFrame` / `TryAcquireCalibFrame`），UI 只收成品帧；十字绘制走 `AlgorithmManager.Instance.DrawSpotMark`。② 失败文案——新增 `DescribeLastError(MonitorCamErrorContext)`（实现层映射厂商码，分析语境走 Manager 口径），流程三条失败文案改为引用成品描述。③ 回放归算法层 `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm`（解码/时间基准/倍速/跳转/扫描/缩略图），由 `AlgorithmManager.Playback` 持有；流程层 `MonitorCameraWorkflow` 只做门面转发，UI 只调用与展示。④ 撤销 `MonitorCamManager` 算法包装：检测由流程直调 `AlgorithmManager.Instance.Detect*`，同级 Manager 不互持算法对象。

## 核心文件（三层目录）

| 层 | 文件 | 职责 |
|---|---|---|
| 抽象层 | `MonitorCam/IMonitorCam/IMonitorCamApi.cs` | 相机契约（扫描设备 / 连接 / 断开 / 单次触发取帧 / 释放） |
| 抽象层 | `MonitorCam/IMonitorCam/MonitorCamType.cs` | 4 枚举：`MonitorCameraConnectionState` / `MonitorCameraPhase` / `MonitorSupervisionState` / `MonitorCamErrorContext`（2026-11-09 新增，失败语境：Connection/Capture/Analyze） |
| 抽象层 | `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs` | 2 事件参数：监督状态变更 / 帧完成 |
| 抽象层 | `MonitorCam/IMonitorCam/MonitorCamDeviceInfo.cs` | 扫描结果设备信息（IP / 产品名称 / 序列号 / 接口类型 / 传感器类型）（2026-09-29 ADR-046 新增） |
| 实现层 | `MonitorCam/HikCam/HikCam.cs` | **海康实现（ADR-047）**：官方 MvCameraControl.Net V2 落地契约，只按契约单次取帧 + 枚举扫描（`ScanDevices`），不做业务判断 |
| 业务层 | `MonitorCam/MonitorCamManager.cs` | **对外唯一入口（Lazy 单例）**：连接编排、设备扫描、单次触发采集、帧分发（含标定十字标注）、健康巡检、配置落盘；算法经 `AlgorithmManager.Instance` 取用（2026-11-09 ADR-097，不持有算法对象） |
| 配置 | `MonitorCam/MonitorCamConfig.cs` | 硬件配置（IP/端口/曝光/尺寸），持久化 `Config/MonitorCam/Monitor_INI/MonitorCamera.ini` |
| 工作流 | `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` | 采集→分析→显示→结果，继承 `DeviceWorkflowBase`；录像触发与命名策略（`StartRecording`/`StopRecording`）；**2026-11-09 ADR-097** 回放门面（9 方法 + 3 属性 + 7 转发事件），UI 只订阅门面 |
| 算法层 | `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` | **2026-11-09 ADR-097** 回放算法（与 `WireFeedDistance` / `WeldQuality` 同级并排）：录像目录扫描、缩略图后台解码、`VideoCapture` 播放解码、时间基准/进度/暂停/倍速/±5 秒跳转；由 `AlgorithmManager.Playback` 持有，跨页面共用 |
| UI | `UIDesign/TabPage/MonitorCamPage.cs` | 页面（ADR-048 / ADR-078）：`tabsMonitor` 双页——焊接相机设置（顶栏 + 画面 + 采集/录像/参数/标定右侧栏）/ 焊接回放（日期区间筛选列表 + 右键回放 + 悬停双层播放控件栏）；**2026-09-30 控件与组件全归设计器**（字段声明/实例化/挂载齐备，`Timer` 随 `components` 托管，`.cs` 零控件实例化），`MonitorCamPage.resx` 已登记 csproj；**2026-10-30** 回放区新增 `panelPlayBar`（`imageBoxPlay` 子控件）+ `sliderPlay`/`lblPlayTime`/`flowPlayButtons` 五按钮、顶栏 `uiPlayDateRange`，删除旧 `flowPlayBar`/`btnStopPlay`；**2026-11-09** 只调用与展示（无解码/像素运算/帧创建，`timerPlay` 已删） |
| UI | `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs` | 扫描结果对话框（Table 单选回填 IP）（2026-09-29 ADR-046 新增） |

> **已删除文件（勿再引用）**：`MonitorCam/Api/IMonitorCameraApi.cs`（现役 `IMonitorCam/IMonitorCamApi.cs`）、`MonitorCam/Api/HikvisionCameraApi.cs`（旧海康实现，2026-09-08 删）、`MonitorCam/MonitorCameraRun.cs`（改名承接为 `MonitorCamManager.cs`）、`MonitorCam/AlgorithmManager.cs`（算法参数并入 `EmguALG/Manager/AlgorithmManager.cs`）、`MonitorCam/MecaVisionCam/MecaVisionCam.cs` + `MonitorCam/MecaVisionCam/Native/MVSDK.cs`（麦格威实现，2026-09-29 ADR-047 切海康 MVS 时整体删除）。
>
> ⚠️ **命名空间=类名同形规约（2026-09-09，CS0118 真编译暴露）**：实现层命名空间与类名同形（线激光 `LineLaserCam.IntelligentLaserCam` 先例同构；现 `AdaWeldSystem.MonitorCam.HikCam` + `HikCam`）。**实例化必须写 `new HikCam.HikCam()`（命名空间.类名限定）**，裸名会被解析为子命名空间报 CS0118。

## 职责分工

| 关注点 | 承载者 | 位置 |
|---|---|---|
| 连接编排、设备扫描、帧分发、健康巡检、配置 | `MonitorCamManager` | `MonitorCam/MonitorCamManager.cs` |
| 单次触发取帧 + 设备枚举扫描 | `HikCam` | `MonitorCam/HikCam/HikCam.cs` |
| 检测阶段枚举 | `MonitorCamPhase` | `MonitorCam/IMonitorCam/MonitorCamType.cs` |
| 连接态 + 焊接过程态 + 执行步 | `MonitorCameraWorkflow` | `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` |
| 主页面焊接预览（30Hz 节流 + 随焊接启停开关） | `MonitorCameraWorkflow.WeldPreviewFrame` / `StartWeldPreview` / `StopWeldPreview`（2026-11-11） | 同上 |
| IP 选择 / 扫描 / 连接入口 | `MonitorCamPage` 顶栏 + `MonitorCamScanForm` | `UIDesign/TabPage/` + `UIDesign/SubDialog/MonitorCamDialog/` |

> **权责边界（ADR-021）**：流程只输出「进度」，图像/连接态/健康度由 `MonitorCamManager` 输出（`FrameCompletedEvent` / `StatusChanged`），算法结果由流程以只读属性暴露。细则见 [[standards/WorkflowResponsibilityBoundary]]。

## 单次触发取图机制

```
MonitorCamManager.SensorRunContinue() 触发一次采集
└── Task 异步执行 HikCam.CaptureSingleFrame() 同步返回帧
    ├── StreamGrabber.GetImageBuffer(500) → PixelTypeConverter 像素归一 → Marshal.Copy 建 Mat
    ├── 写入 CurrentMat，LastAcquisitionSuccess = true/false
    └── AcquisitionCompletedSignal.Set()  // 通知 Workflow 等待线程
```

> 监控相机无 Live 模式，所有帧均为单次触发产出（ADR-010）。`SensorStop()` 保留方法签名但内部为空（单次任务由 Task 自行结束），仅兼容既有调用方。

## 关键属性（MonitorCamManager）

| 属性 | 类型 | 说明 |
|------|------|------|
| `AcquisitionCompletedSignal` | AutoResetEvent（readonly） | Workflow 等待的回调信号 |
| `CurrentMat` | Mat | 当前帧（lock 保护） |
| `LastAcquisitionSuccess` | bool | 最近一次采集是否成功 |
| `ConnectionState` | MonitorCameraConnectionState | 连接状态 |
| `SupervisionState` | MonitorSupervisionState | 健康巡检状态（Idle/Checking/Healthy/Degraded/Error） |
| `Config` | MonitorCamConfig | 硬件配置（IP/端口/曝光/尺寸） |
| `IsRun` | bool | 相机是否已连接（可运行） |
| `ScanDevices()` | List&lt;MonitorCamDeviceInfo&gt; | 枚举可用相机（含 GigE IP），UI 扫描入口（ADR-046） |
| `OpenSensor(ip, port)` | **bool** | 连接相机，返回是否成功（ADR-046 由 void 改 bool） |
| `CloseSensor()` | void | 断开并释放 SDK（先停巡检）（ADR-046） |
| `SaveConfig()` | void | 硬件配置（含连接 IP）落盘 INI（ADR-046） |

> 已删除：`IsLiveMode`、`ChangeMode`、`FrameReceived` 事件、`StartAcquisition()` / `StopAcquisition()`（ADR-010）。

## 与外部模块关系

- **算法**：流程直接 `AlgorithmManager.Instance.DetectWireFeed/DetectWeldQuality`（同级 Manager 不互持算法对象，2026-11-09 ADR-097）；标定十字绘制走 `AlgorithmManager.Instance.DrawSpotMark`
- **算法参数**：由 `EmguALG/Manager/AlgorithmManager` 持有强类型配置（`WireFeedConfig` / `WeldQualityConfig`），持久化 `Config/EmguALG/Algorithm_INI/MonitorAlgorithm.ini`
- **回放**：解码与时间基准在算法层 `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm`（`AlgorithmManager.Playback`），流程层 `MonitorCameraWorkflow` 只做门面转发与录像根目录注入
- **UI**：由 [[modules/UIDesign]] 的 `UIDesign.TabPage/MonitorCamPage` 页面驱动与展示（画面由检测触发后刷新，无实时预览开关）。**2026-09-29 ADR-046**：页面顶栏复刻线激光调试页的连接入口（连接态 Alert + 相机IP + 扫描 + 连接/断开），扫描结果对话框 `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm` 单选回填 IP
- **两路预览并存（2026-11-11）**：调试页 `MonitorCamPage` **直连** `MonitorCamManager.PreviewFrameEvent`（逐帧直刷、无节流，开关即页面生命周期）；主页面 `imb_WeldViewer` **经** `MonitorCameraWorkflow.WeldPreviewFrame`（流程节流 30Hz + 随焊接启停开关）。理由见 [[standards/WorkflowResponsibilityBoundary]] §八（主页面属焊接过程，调试页属设备级视图）
- **解耦**：单向依赖 `Comm`（日志）与 `EmguALG`；不反向依赖工作流
- **配置**：INI 落盘遵循 ADR-033（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）
- **参照范式**：本模块是 [[standards/ModuleOrganizationPattern]] 的**场景 A（基于第三方库，现海康 MVS）**样本——`IMonitorCam/` 抽象 + `HikCam/` 实现 + `MonitorCamManager` 唯一入口（原 MecaVision MVSDK 场景 A 样本，2026-09-29 ADR-047 载体切换）

## 相机实现（HikCam）— 2026-09-29 落地（ADR-047）

海康官方 MVS SDK（.NET 封装 `MvCameraControl.Net.dll`，win64/net40；原生运行时由已安装的 MVS 客户端提供）。实现要点（均以官方 BasicDemo / GigE_ConnectCameraByIP / Image_ConvertPixelType 示例为实证）：

1. `Connect(ip,port)`：`SDKSystem.Initialize`（进程级一次，静态守卫）→ `DeviceEnumerator.EnumDevices`（GigE+USB3+GenTL）→ **`IGigEDeviceInfo.CurrentIp` 按 IP 精确匹配**（指定 IP 未匹配即**连接失败并记日志，不回退枚举首台**——ADR-046 语义继承；仅 IP 为空取首台）→ `DeviceFactory.CreateDevice` + `Open` → GigE `GetOptimalPacketSize` 设 `GevSCPSPacketSize` → `AcquisitionMode=Continuous` + `TriggerMode=Off` → `StreamGrabber.StartGrabbing()`（取流常开）。
2. 扫描：`ScanDevices()` = EnumDevices → 逐台解码 `CurrentIp`（点分十进制）+ `UserDefinedName||ModelName` / `SerialNumber` / `TLayerType` / `ManufacturerName`；非 GigE（USB3）相机 IP 为空串；未连接也可调用（ADR-046）。
3. 取帧：`GetImageBuffer(500)` → 彩色经 `device.PixelTypeConverter` 转 RGB8_Packed、其余非 Mono8 转 Mono8 → `IImage.PixelData`（byte[]）经 `Marshal.Copy` 建独立 Mat（无需 Clone）→ **必须 `FreeImageBuffer`**（否则后续取帧持续超时）。海康输出方向正常，无麦格威的垂直镜像步骤。
4. 坑位：`SDKSystem.Finalize()` 仅在 `Dispose()` 调用；无断联回调——链路异常由 `MonitorCamManager` 健康巡检兜底（语义等价于麦格威版断联回调）；封装层加载原生库失败的异常会带 `TypeInitializationException` 包装，取内层才是真实原因。
5. 部署：现场机器须安装海康 MVS 客户端/运行时；`3rdDepend/MecaVision/` 原生件已不随构建复制（物理文件保留备查）。
6. 完整 API/取帧配方见 [[api/HikCam]]。

> 历史：早期曾用 `MonitorCameraSimulator` 占位、随后为旧海康 `HikvisionCameraApi`；2026-09-08 切麦格威（ADR-019）；2026-09-29 业主实证麦格威即海康魔改底层后，回归海康官方 MVS 并删除麦格威实现（ADR-047）。2026-09-09 删除 Live/PIL 模式相关接口与 UI。

## 设计决策

- [[decisions/ADR-019-MonitorCamBoundaryAndEmguALGRefinement]]：**监控相机业务边界澄清 + EmguALG 五层细化**（accepted）
- [[decisions/ADR-046-MonitorCamIpScanAndStrictMatch]]：**监控相机 IP 扫描与严格匹配**（accepted，2026-09-29：顶栏连接入口复刻线激光页 + 扫描三层接口 + 连接 IP 落盘 + 指定 IP 不匹配即失败）
- [[decisions/ADR-047-MonitorCamSwitchToHikMvs]]：**监控相机实现切换海康 MVS**（accepted，2026-09-29：实现层 MecaVisionCam→HikCam，契约/业务层/UI 零改动，麦格威实现退役）
- [[decisions/ADR-048-MonitorCamTabsRecordPlayback]]：**页 Tabs 化与录像/回放能力**（accepted，2026-09-29：双页布局 + 契约扩展 12 成员 + 单线程喂帧 + 标定 Calibration 节；ADR-020 算法内联条款随之废除）
- [[decisions/ADR-095-hardware-fault-tree-ownership]]：**硬件故障树归属硬件 Manager**（accepted，2026-11-09 监控相机落地：`DescribeLastError` 成品描述）
- [[decisions/ADR-097-algorithm-layer-ownership-single-entry]]：**帧载体边界**（accepted，2026-11-09：`Mat` 继续作帧载体，UI 禁创建/处理帧）
- [[decisions/ADR-078-MonitorPlaybackControlBarAndDatedRecords]]：**焊接回放播放控件栏与日期目录录像列表**（accepted，2026-10-30：悬停显隐 50% 半透明双层控件栏 + 帧索引倍速/±5s + 录像 `yyyyMMdd` 子目录 + `DatePickerRange` 区间筛选 + `CellImage` 缩略图后台加载）
- ADR-019（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）：**三层重构 + 切换麦格威 + 删除海康**（accepted；其中「切麦格威」载体条款已被 ADR-047 演进为海康 MVS）
- [[decisions/ADR-022-EmguALGThreeLayer]]：算法模块三层改造（输入源即本模块）
- ADR-019（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）：SDK 抽象、完全解耦（Live/PIL 双模式条款已被 ADR-010 废止）
- [[decisions/ADR-018-CallbackAcquisition]]：复用回调等待取图模式
- ADR-033（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）：配置文件归入 Config/INI/

## 相关教训

- [[guides/Namespace-Compilation]]：MonitorCam 文件已注册到 .csproj（`MonitorCamPage.resx` 的 `<EmbeddedResource>` 登记于 2026-09-30 补齐）
- [[guides/WinForms-Designer]] §6：控件与组件的设计器归属 + resx 工程登记（2026-09-30）
- [[guides/WinForms-UI-Threading]]：UI 事件处理均检查 InvokeRequired
- 真编译待 Visual Studio（本环境无 C# 编译器），改动以 Python 静态校验替代

---

*来源：用户需求「自动焊接头监控模块」+ 本模块源码（AdaWeldSystem/MonitorCam/）*
