---
title: ADR-048 监控相机页 Tabs 化与录像/回放能力
date: 2026-09-29
updated: 2026-10-30
tags: [决策, 监控相机, UI, Tabs, 录像, 回放, 标定, 契约扩展, HikCam]
status: accepted
---

# ADR-048：监控相机页 Tabs 化与录像/回放能力

## 背景

业主要求（2026-09-29）：监控相机调试页改为 **Tabs 双页**——页1「焊接相机设置」、页2「焊接回放」。页1 右侧栏自上而下四组：采集（开始/停止）、录像（路径选择/开始/停止）、参数设置（曝光/增益）、标定设置（mm/pixel 尺度、光斑点坐标按坐标画十字、焊丝识别设置暂空、送丝距离测试）。

裁定补充（AskUserQuestion 确认）：
1. 原「检测调试」（相位/单次检测/连续监控/结果）与「算法参数」（对中容差/合格分）两区**删除**，后续算法确认后再对接；
2. 录像默认目录 = **exe 目录下「焊接」文件夹**，可经路径选择修改并记忆；
3. 采集/停止**对齐官方 demo**（开始采集即连续模式取流刷图）；**录像须先开始采集**，停止采集时若在录像须先停录像再停采集；**送丝距离测试** = 切触发模式软触发单帧（采集中先自动停止采集），图像供分析显示（算法占位）。

## 决策

1. **页面 Tabs 化**（照 [[decisions/ADR-036-UIControlPlacementRule]] 同代 Tabs 范式与 SystemControlPage 双写铁律）：`MonitorCamPage` 根容器改 `tabsMonitor`（`Controls.Add` + `Pages.Add` 双写）。页1 承载顶栏连接区（ADR-046 原样）+ `imageBox1` + 右侧栏（TableLayoutPanel 1 列 4 行 AutoScroll：采集/录像/参数/标定四个 GroupBox）；页2 = 左 `playTable`（AntdUI Table）+ 右 `imageBoxPlay`。
2. **契约扩展（IMonitorCamApi 新增 12 成员）**：`IsGrabbing/IsRecording/PreviewFrame 事件/StartCapture/StopCapture/TriggerSingleShot/StartRecord(path)/StopRecord/SetExposureTime/SetGain/GetExposureTime/GetGain`；Manager 一一透传。`CaptureSingleFrame` 保留供工作流分析链路。
3. **取帧线程单线程化**：连续采集的预览抛帧与录像喂帧**共用一个取帧线程**（GrabLoop：`GetImageBuffer → 录像中 InputOneFrame → BuildMat 抛 PreviewFrame → FreeImageBuffer`），避免多线程争抢帧队列；`StopCapture` 内保证「先停录像 → 停线程 → 停取流」顺序（用户裁定顺序）。
4. **录像**（照官方 BasicDemo 原文）：`device.VideoRecorder.StartRecord(path, RecordParam)`，RecordParam 宽高取参数 `Width/Height`（long 收窄 uint）、PixelType 取 `PixelFormat` 枚举当前值、帧率取 `ResultingFrameRate`（回退 30）、AVI；文件名 `MonitorCam_yyyyMMdd_HHmmss.avi`。
5. **软触发单帧**：`TriggerMode=On + TriggerSource=Software → StartGrabbing → TriggerSoftware → GetImageBuffer(5000) → BuildMat → StopGrabbing`；**保持触发模式**（连续点按复用），`StartCapture` 时恢复 `TriggerMode=Off`。
6. **参数**：`ExposureAuto/GainAuto=0` 后 `SetFloatValue("ExposureTime"/"Gain")`；连接成功后 `GetFloatValue` 回填 UI。
7. **标定配置**：`MonitorCamConfig` 新增 `RecordDir`（Camera 节）与 `MmPerPixel/SpotX/SpotY`（**新 Calibration 节**），读写同段同键核验；画面十字画在预览帧显示副本上（绿色半长 20px），**不动原始帧数据链**。
8. **回放**（数据追溯同构）：`AntdUI.Table + AntList<PlaybackRow>` 绑定，列 No/文件名/修改时间/大小；`CellClick` 右键 → `AntdUI.ContextMenuStrip.open(…, "回放")` → `Emgu.CV.VideoCapture` 打开 + 33ms WinForms Timer 逐帧 `QueryFrame` → `imageBoxPlay`（播完自动停；「停止回放」按钮兜底）。解码依赖 = 既有 `3rdDepend` ffmpeg 套件（avcodec-58/avformat-58/avutil-56/swscale-5/opencv_videoio_ffmpeg4130_64）。
 - ~~列 No/文件名/修改时间/大小；「停止回放」按钮兜底~~ ⚠️ **2026-10-30 经 [[decisions/ADR-078-MonitorPlaybackControlBarAndDatedRecords]] 演进**：No 列改**预览图列**（`CellImage` 缩略图后台加载），并新增**悬停双层播放控件栏**（进度/时间 + 倍速/跳转/播放暂停）；「停止回放」按钮**已删除**（停止语义由暂停 + 播完自动停承载）；列表改按日期区间筛选、录像改落 `yyyyMMdd` 子目录。右键「回放」入口与 33ms Timer 节拍语义不变。
9. **检测调试/算法参数删除**：页内相关控件（cmbPhase/btnSingleCheck/btnStartMonitor/btnStopMonitor/txtResult/uiGroupBoxAlgorithm/lblStatus/uiLightStatus）整体移除；`MonitorCameraWorkflow` 与 `MonitorCamManager.FrameCompletedEvent` 分析链路**不动**（自动焊接流程仍用），仅本页不再调用检测入口。

## 勘误（2026-09-29 晚，实测反馈）

- **现象**：连接后点「开始采集」画面无图；录像停止后文件无法打开（回放报「无法打开录像文件」）。
- **根因（单一）**：`Connect` 开启取流并置 `IsGrabbing=true`，但**从未启动取帧线程**；`StartCapture` 幂等守卫 `if (IsGrabbing) return true` 直接空转 ⇒ `GrabLoop` 不存在 ⇒ `PreviewFrame` 永不触发（预览无图）且录像 `InputOneFrame` 零喂帧（AVI 只有文件头，打不开）。
- **修复**：线程启动收敛为私有 `StartGrabThreadLocked()`（须持 `_sync`、取流已开启）；`Connect` 成功即调用（补全「取流常开」语义）；`StartCapture` 守卫改为 `IsGrabbing && GrabRunning`，对「已取流未起线程」存量状态补启动；线程体构造唯一（`new Thread(GrabLoop)` ×1，收敛进 Locked 方法）。
- **教训**：状态标志（`IsGrabbing`）只表达「取流已开」，不表达「消费线程在跑」；幂等守卫条件必须覆盖**两个**状态量，否则「生产者已启动、消费者未启动」的中间态会被永久跳过。

### 二次勘误（2026-09-29 同日，业主实测再裁）

- **现象**：连接后（未点开始采集）`MonitorCamPage.Manager_PreviewFrame` 内抛 `System.AccessViolationException`（读取或写入受保护的内存）。
- ~~上条修复「`Connect` 成功即调用 `StartGrabThreadLocked()`（补全「取流常开」语义）~~ ⛔ **方向错误，已回退**：业主裁定**对齐官方 demo——连接（打开设备）不开启采集**，取流与取帧线程只由 `StartCapture()` 显式开启。
- **修复**：① `Connect` 删 `StartGrabbing` 与起线程，仅开设备 + 预置参数（`AcquisitionMode=Continuous` + `TriggerMode=Off`），日志「相机已连接（未开启采集）」；② `GrabLoop` 把 `PreviewFrame` 分发**移到 `_sync` 锁外**（锁内只做 `GetImageBuffer` / `InputOneFrame` / `BuildMat` / `FreeImageBuffer`），消除锁内 UI 分发与页面/健康链路 `CaptureSingleFrame` 锁内 SDK 调用的竞争窗口（AV 直接成因）；③ `StartCapture` 守卫 `IsGrabbing && GrabRunning` 语义至此自洽。
- **连带语义**：连接后未采集 ⇒ 预览无帧（属预期，非故障）；健康巡检显示「Degraded 已连接但近期无有效采集」（正确降级提示）；`TriggerSingleShot` 在未采集状态可用（守卫 `_isGrabbing=false`）。
- **教训**：官方 demo 的生命周期边界（打开 ≠ 采集）是 SDK 线程安全假设的一部分——连接即取帧让取帧线程与 UI 初始化链路在 `StreamGrabber` 上首次交叠，属偏离 demo 的自造风险；**遵循 demo 生命周期优先于「语义更顺」的自创优化**。

### 三次补充（2026-09-29 同日，双订阅方 AV 与副本所有权）

- **现象**：连接不采集修复后，第一次开采集仍在 `MonitorCamPage.Manager_PreviewFrame` 的 `frame.IsEmpty` 处抛 `AccessViolationException`。
- **根因**：`RelayPreviewFrame` 把**同一个 Mat 实例**广播给两个订阅方——业主确认双预览是设计意图（**主页 = 运行时自动模式、调试页 = 点采集手动模式**）。主页处理器把帧存入 30Hz 交换槽并在换帧时 `Dispose()`（ADR-049 所有权约定），调试页是 `BeginInvoke` 异步排队后访问帧——主页先释放、调试页后访问 ⇒ 踩已释放内存。本页「负面后果」预警过的『新增其他 PreviewFrame 订阅方需改为 Clone』正式触发。
- **修复**：`RelayPreviewFrame` 改为**每订阅方独立副本**——`GetInvocationList()` 逐订阅方 `frame.Clone()` 分发（订阅方同步异常时收回副本），全部分发完毕 `finally` 释放原始帧。**事件契约升级：订阅方收到即拥有副本、负责释放**；~~主页 30Hz 管线（本就按自有副本释放）~~（⛔ 2026-10-22 主页订阅方已移除）与调试页（`ImageBox` 换帧释放）语义不变。
- **教训**：事件广播**禁止多订阅方共享同一含原生资源的实例**——只要存在一个「异步消费或延迟释放」的订阅方，同步订阅方的生命周期假设即全部失效；副本所有权必须在**分发点**切割，而非依赖订阅方自觉。

### 四次补充（2026-09-30，控件与组件的设计器归属收敛）

- **触发**（业主）：MonitorCamPage 控件疑似代码生成，要求核查是否由 `Designer.cs` 完全设计、`.cs` 只做使用。
- **核查结论（与预期相反）**：可视控件**已 100% 由设计器声明**——48 个字段全部实例化并挂载、`Name`↔字段名 48/48 一致、`TabIndex` 组内无重复、`Suspend/Resume` 与两处 `ImageBox` 的 `BeginInit/EndInit` 配对完整、8 个 `TableLayoutPanel` 的 `Count`↔`Styles` 计数一致且无越界、`.cs` 零控件实例化 / 零 `Controls.Add` / 零事件双写（22 处控件属性写入全为运行期状态）。**设计器侧无需改造**。
- **实际收敛两处**：
 1. **非可视组件归位**：`_statusTimer` / `_playTimer` 由 `.cs` 的 `new Timer()` 迁入设计器（`timerStatus` / `timerPlay`：`new System.Windows.Forms.Timer(this.components)` + `Interval` 500/33 + `Tick +=` 订阅）；`.cs` 只保留 `Start()` / `Stop()`，释放交 `components.Dispose()`（不再手工 `Dispose()`）。决策 8「33ms WinForms Timer」的实现落点随之由代码后置改为设计器，**节拍与播放语义不变**。
 2. **`.resx` 工程登记补齐**：`MonitorCamPage.resx` 为全库 25 个 `.resx` 中**唯一**未登记进 csproj 者，补 `<EmbeddedResource>` + `<DependentUpon>MonitorCamPage.cs</DependentUpon>`。
- **保留（不得搬入设计器）**：`playTable.Columns = new AntdUI.ColumnCollection{…}` 与 `playTable.Binding()` 留在代码后置（AntdUI 约束，全库 13 处一致，Designer 中零例）。
- **影响面**：`MonitorCamPage` 全库唯一实例化点 = `FormMain.cs:73`，契约零变更；Designer 763→777 行、`.cs` 599→581 行，BOM/CRLF 守恒，32 项静态校验全 PASS。
- **教训**：「控件由设计器完全设计」的口径覆盖**三层**——可视控件、**非可视组件（Timer）**、**工程登记（resx）**；只对可视控件对账会漏掉后两层。门禁与对账法见 [[lessons/UiLayoutChangeSyncPitfalls]] 坑二附二 与 [[guides/WinForms-Designer]] §6。

## 备选方案

| 方案 | 结论 |
|---|---|
| 采集 = UI 定时器逐拍 `CaptureSingleFrame` | 放弃：与「对齐 demo 开始/停止采集」的裁定不符；周期取帧节拍受 Timer 精度与单帧超时影响 |
| 录像独立线程另起 `GetImageBuffer` | 放弃：与预览线程争抢帧队列，两路各拿一半帧；单线程统一喂帧更可控 |
| 回放用 WMP/自建解码 | 放弃：Emgu VideoCapture + 既有 ffmpeg 依赖零新增部署 |
| 检测调试区保留挪位 | 放弃：业主裁定删除，待算法确认后再对接 |

## 后果

### 正面

- 监控相机页具备「预览-录像-回放」闭环调试能力，标定参数（尺度/光斑点）可视可存。
- 契约扩展一次性落齐取流/录像/参数能力，后续算法对接（焊丝识别/送丝距离）只需消费 `TriggerSingleShot` 帧。
- 预览帧与工作流分析帧通道分离（`PreviewFrameEvent` vs `FrameCompletedEvent`），互不触发。

### 负面

- `IMonitorCamApi` 契约扩大（+12 成员），未来实现类需同步实现。
- 连续采集预览每帧做像素转换建 Mat（全帧率），CPU 占用上升；如需降载可在 GrabLoop 加抽帧间隔。
- 预览帧标注十字为就地修改（每帧独立副本仅本页消费），若未来新增其他 PreviewFrame 订阅方需改为 Clone 后标注。
- 页面销毁（HandleDestroyed）即 `StopCapture`——切走页签不销毁控件则采集持续（AntdUI Tabs 常驻语义）。

## 相关页面

- [[modules/MonitorCam]]、[[api/HikCam]]、[[api/MonitorCamManager]] —— 核心文件/契约/透传更新
- [[decisions/ADR-046-MonitorCamIpScanAndStrictMatch]] —— 顶栏连接区原样保留
- [[decisions/ADR-047-MonitorCamSwitchToHikMvs]] —— 录像/触发的 SDK 事实基线
- [[decisions/ADR-020-MonitorCamPage-AlgorithmInline]] —— 「算法参数内联右侧」条款随本决策废除（控件已删，算法确认后另行对接）
- [[decisions/ADR-078-MonitorPlaybackControlBarAndDatedRecords]] —— 回放控件栏 / 日期目录 / 缩略图列表（演进本页决策 8 的列与停止按钮条款）
- [[modules/UIDesign]] —— Tabs 双写与 Table 代码后置范式
- [[guides/WinForms-Designer]] —— 控件与组件的设计器归属 + resx 工程登记（2026-09-30 四次补充）
- [[lessons/UiLayoutChangeSyncPitfalls]] —— 坑二附二：组件归属与 resx 登记
