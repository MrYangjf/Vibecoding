---
title: MonitorCameraWorkflow API 参考（三态模型：SubDeviceState / SubDeviceWeldStatus）
date: 2026-09-02
updated: 2026-11-11
tags: [API, 工作流, 监控, 权责边界, RunStep, SubDeviceWeldStatus, DeviceWorkflowBase, ADR-023, ADR-034, ADR-020, ADR-028]
source: AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs
---

# MonitorCameraWorkflow API 参考

> 监控相机工作流（单例）。**只负责编排**：触发采集 → 调用算法 → 读取结果 → 推进焊接过程态。
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceWorkflow`
> **继承**：非泛型 `DeviceWorkflowBase`（17 项契约）→ `DeviceStateBase`；`IDisposable` 由基类实现。

> **✅ 2026-09-04 已落地（ADR-020 批次 0~4.4）**：本类已按新架构改码——无自带线程（由 `DeviceControlWork` 模组线程驱动 `FlowProcess()`）、`RunStep` 每 case 靠 bool 推进、采集等待改「`WaitOne(0)` 非阻塞探测 + 步骤计时判超时」（⛔ 不再 `WaitOne(5000)` 阻塞）。旧 `GoStep`/`SetStep`/`WorkStep`/`StartRunLoop`/`ManualOn`/`ManualOff`/命令三槽等机制已全部清除，不得据旧内容改码。真编译待 VS（静态自检已通过）。
> 步骤驱动规范见 [[architecture/DeviceControlArchitecture]] §4（17 契约）· §5（`RunStep` 驱动）· §16（代码模板）。

## 权责边界（ADR-023）

**本流程不产出任何设备数据事件**，职责划分：

| 内容 | 归属 | 通道 |
|---|---|---|
| 图像 / 实时帧 | [[api/MonitorCamManager]] | `MonitorCamManager.FrameCompletedEvent` |
| 相机连接态与**健康巡检** | [[api/MonitorCamManager]] | `MonitorCamManager.StatusChanged` + 只读属性（巡检由相机自启停） |
| 流程进度 | 本流程（基类提供） | `WeldStatusChanged`（`WeldStatusChangedEventArgs`） |
| 检测结果 | 本流程**只读持有** | `LastResult` / `LastOverlay` 属性，订阅方在流程态转 Completed 后按需拉取 |

> ⚠️ 历史版本曾提供 `DisplayEvent`/`ResultEvent`/`ErrorAborted`/`ManualStopped`/`StatusChanged` 五个自定义事件，**已全部移除**（仅剩基类三事件，ADR-023 R1~R4）。
>
> **唯一例外（2026-11-11）**：`WeldPreviewFrame` 交付的是**本流程已 30Hz 节流的成品帧**，开关随焊接启停，丢帧即释放，无订阅方由本流程释放——属 R1 受限例外，不是设备数据事件。理由与许可边界见 [[standards/WorkflowResponsibilityBoundary]] §八。

---

## 公共成员

| 成员 | 签名 | 说明 |
|---|---|---|
| `Instance` | `static MonitorCameraWorkflow` | `Lazy<T>` 单例 |
| `StateName` | `override string` | 对外名片名，返回 `Tag`（日志/事件标识） |
| `LastResult` | `MonitorResult` | 最近一轮检测结果（锁内快照拷贝，非事件参数） |
| `LastOverlay` | `Mat` | 最近一轮算法叠加图（`_resultLock` 保护） |
| `State` / `WeldStatus` | 基类属性 | 连接态（`SubDeviceState`）/ 焊接过程态（`SubDeviceWeldStatus`） |
| `RunStep` / `StepWorkTime` / `WorkStepName` / `StepStatusText` | 基类属性 | 执行步 / 步骤用时 / 步中文名 / 可观测摘要 |
| `Start(phase, continuous)` | `void` | 启动检测；`phase` 指定检测类型，`continuous=true` 连续循环 |
| `Stop()` | `void` | 手动停止：停相机巡检 + 置 `ManualStopped` |
| `StartRecording(prefix, out fileName, out failureMessage)` | `bool` | **2026-11-09** 录像触发：前置判断 + `{prefix}{yyyyMMdd_HHmmss}.avi` 命名与落盘目录策略归本层；UI/主控只传前缀常量 |
| `StopRecording()` | `void` | **2026-11-09** 停止录像（调用方只发起） |
| `StartWeldPreview()` | `void` | **2026-11-11** 开启焊接过程预览（幂等）；开启态才订阅 `MonitorCamManager.PreviewFrameEvent` |
| `StopWeldPreview()` | `void` | **2026-11-11** 关闭焊接过程预览（幂等）；退订后关闭态零订阅 |
| `WeldPreviewFrame` | `event Action<Mat>` | **2026-11-11** 已 30Hz 节流的成品帧；订阅方接管该帧所有权 |

### 焊接过程预览（2026-11-11，R1 受限例外）

| 项 | 实现 |
|---|---|
| 节流 | 独立常量 `WeldPreviewHz = 30`；`Stopwatch.Frequency / WeldPreviewHz` 得最小帧间隔，`Stopwatch.GetTimestamp()` 与 `_weldPreviewLastTicks` 比较，不足即丢弃（无定时器线程、无缓冲） |
| 开关 | `StartWeldPreview()` / `StopWeldPreview()`，`_weldPreviewOn`（`volatile`）+ `_weldPreviewLock` 保证幂等；**关闭态不留订阅** |
| 焊接启停 | `DeviceControlWork.SimMonitorCamStartWeld` 在 `StartCapture()` 成功后开启；`SimMonitorCamStopWeld` **首行**（早退之前）关闭，三条停止路径（`DoSubStop`/`DoSubManualStop`/`DoSubAlarmStop`）与急停均收敛于此 |
| 帧所有权 | 管理器对每个订阅方 `Clone()`；**被节流丢弃的帧当场 `Dispose`**；无订阅方时流程自行释放；正常返回即所有权移交订阅方 |
| 关闭收口 | `DisposeManaged()` 首行 `StopWeldPreview()`，退订失败不阻断释放 |
| 与调试页 | 调试页仍直连 `MonitorCamManager.PreviewFrameEvent`（逐帧直刷、无节流），两条通道互不影响 |

### 回放门面（2026-11-09 ADR-097）

回放算法在 `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm`（`AlgorithmManager.Playback`）；本流程只做门面转发与录像根目录注入，UI 不接触算法对象。

| 成员 | 签名 | 说明 |
|---|---|---|
| `CancelScan` | `void` | 取消区间扫描与缩略图解码 |
| `LoadRange` | `void LoadRange(DateTime start, DateTime end)` | 根目录取 `MonitorCamManager.Instance.RecordDirectory` 后转算法层 |
| `PlayFile` | `string PlayFile(string path)` | 空串成功，否则为可展示提示 |
| `TogglePlayPause` | `string` | 无打开文件时返回「请先在右侧列表右键选择要回放的录像文件！」 |
| `CycleSlow` / `CycleFast` | `void` | 0.8/0.5/0.3/0.1/1.0、1.5/2.0/2.5/3.0/1.0 循环 |
| `SeekToFrame` | `void SeekToFrame(int frameIndex)` | `CapProp.PosFrames` 定位 |
| `SeekBySeconds` | `void SeekBySeconds(double seconds)` | ±5 秒按钮入口 |
| `StopPlayback` | `void` | **幂等**；页面打开时调用即复位到「无源、未播放、速度 1.0」。与设备侧 `Stop()` 语义不同 |
| `HasSource` / `IsPlaying` / `Speed` | `bool` / `bool` / `double` | 只读状态 |
| 7 转发事件 | `ScanStarted` / `ScanCompleted` / `ScanCrashed` / `ThumbnailReady` / `FrameReady` / `ProgressChanged` / `PlayStateChanged` | 构造期接线一次，后台线程抛出，UI 自行 `BeginInvoke` |

> 页面关闭只 `StopPlayback + CancelScan + 退订`，**不得 `Dispose`** 单例组件。

> 执行步段位常量（私有）：`StepAcquireTrigger=10` / `StepAcquireWait=20` / `StepAnalyze=30`；通用三常量 `StepIdle=0` / `StepFinishOk=800` / `StepFinishFail=900` 由基类提供。
> 常量：`AcquireTimeoutSeconds=5`（采集超时，秒）/ `DefaultIp="192.168.1.100"` / `DefaultPort="5000"`（相机未配置时的兜底地址）。

---

## 执行步表（`RunStep` 驱动）

| 步号 | 常量 | 中文名 | 内容 | 出口 |
|---|---|---|---|---|
| 0 | `StepIdle`（基类） | 待机 | 非运行阶段态 | — |
| 10 | `StepAcquireTrigger` | 触发采集 | `SetPhase(_phase)` + `AcquisitionCompletedSignal.Reset()` + `EnsureConnected()` + `SensorRunContinue()` | → 20 |
| 20 | `StepAcquireWait` | 等待采集完成信号 | `WaitOne(0)` 非阻塞探测；未就绪且停留 >5s → `Fail("采集等待信号超时 5秒 " + DescribeLastError(Capture))`；信号就绪但结果无效 → `Fail("采集结果无效 图像为空或采集失败 " + DescribeLastError(Capture))`；有效则克隆 `CurrentMat` | → 30（`SetPhase(Analyzing)`） |
| 30 | `StepAnalyze` | 算法分析 | `AnalyzeImage()`：按 `_phase` 直调 **`AlgorithmManager.Instance.DetectWireFeed/DetectWeldQuality`**（同级 Manager 不互持算法对象，2026-11-09 ADR-097），锁内写 `_resultMat` 与 `_result`；失败 → `Fail("分析失败 " + DescribeLastError(Analyze))` | → 800（`SetPhase(Completed)`） |
| 800 | `StepFinishOk` | 成功收尾 | 连续模式 `SetPhase(Acquiring)` 回 10 起下一轮；单轮模式 `SetPhase(Standby)` 回待机 | → 10 / 0 |
| 900 | `StepFinishFail` | 失败收尾 | `SetPhase(ErrorAborted)` + `IsAlarm` + `RecordFault`（`MonitorStepFail`） | → 0 |

### `FlowProcess()` switch 骨架

```
if (!IsEnable) return;
switch (RunStep) {
    case 10:  if (DoAcquireTrigger()) AdvanceStep(20);           break;
    case 20:  if (DoAcquireWait())    SetPhase(Analyzing, ...);   break;  // 内部 AdvanceStep(30)
    case 30:  if (DoAnalyze())        SetPhase(Completed, ...);   break;  // 内部 AdvanceStep(800)
    case 800: if (DoFinishOk())       AdvanceStep(0);             break;
    case 900: if (DoFinishFail())     AdvanceStep(0);             break;
    default:  break;   // StepIdle 与未登记步：空转，靠流程态切换复位
}
```

> ⛔ 全部 case 无 `Thread.Sleep` / `while` 轮询 / 阻塞 `WaitOne`：等待靠「外部线程重入 + `StepWorkTime` 判超时」。

---

## 流程态 `MonitorWorkflowState`（私有相位，同文件公共枚举）

`_flowState`（默认 `Uninitialized`）仅驱动 `FlowProcess` 与可观测性，对外统一经 `SetWeldStatus(MapWeldStatus(state))` 映射：

| 取值 | 含义 | 映射 `SubDeviceWeldStatus` |
|---|---|---|
| `Uninitialized` | 未初始化 | `NoReset` |
| `Standby` | 待机 | `Standby` |
| `Acquiring` / `Analyzing` / `Completed` | 进程态（触发/分析/完成） | `Working` |
| `ErrorAborted` | 异常终止 | `ErrorAborted` |
| `ManualStopped` | 手动停止 | `ManualStopped` |

> `SetPhase(state, reason)` 是相位唯一写入口：刷新 `_flowState` → `SetWeldStatus(MapWeldStatus(state), reason)` → 把执行步复位到该阶段入口（`Acquiring`→10、`Analyzing`→30、`Completed`→800、其余→0）。
> ⛔ 禁止手工 `WeldStatus = ...` / `State = ...` 赋值。`MapWeldStatus` 取代旧基类 `MapToDeviceState`（已删）。

---

## 结果类型 `MonitorResult`（只读快照，非事件参数）

| 成员 | 类型 | 说明 |
|---|---|---|
| `Phase` | `MonitorCameraPhase` | 检测阶段（`PreWeldAlignment` 焊前对中 / `WeldQuality` 焊中质检） |
| `Pass` | `bool` | 是否合格 |
| `QualityScore` | `double` | 质量得分 |
| `OffsetX` / `OffsetY` | `double` | 光斑对准偏差 X/Y（**供控制器驱动振镜摆动光斑**，原档20260904 §7.4.5） |
| `WireStickoutDeviation` | `double` | 送丝距离差距值（**供机器人调整送丝距离**，原档 §7.4.5；用户裁定：相机只输出结果，不由相机自行补偿） |
| `Angle` | `double` | 角度偏差（焊前对中） |
| `DefectCount` | `int` | 缺陷数（焊中质检） |
| `Message` | `string` | 判定说明 |
| `Timestamp` | `DateTime` | 结果时间戳 |

阶段填充：`PreWeldAlignment` 填 OffsetX/OffsetY/Angle/Pass/QualityScore（对中合格=100）；`WeldQuality` 填 DefectCount/QualityScore/Pass；两结果均空则 `Pass=false`、Message「分析未完成」。

---

## 回放（2026-11-09 迁算法层，本层只做门面）

回放的解码、推进、时间基准、进度、暂停、倍速、±5 秒、目录扫描与缩略图全部在算法层 [[api/PlaybackAlgorithm]]（`AlgorithmManager.Playback`）；本流程只做门面转发与录像根目录注入，并负责录像触发的命名与前置判断（`StartRecording`/`StopRecording`）。UI `MonitorCamPage` 只调用与展示。

---

## 状态转换与关键行为

- `Start(phase, continuous)`：要求 `_flowState == Standby`（否则抛 `InvalidOperationException`，`RequireStandby`）→ 记 `_phase`/`_continuous` → `MonitorCamManager.StartSupervision()`（健康巡检由相机自启停）→ `SetPhase(Acquiring)`。
- `Stop()`：`MonitorCamManager.StopSupervision()` → 若未处于 `ManualStopped` 则 `SetPhase(ManualStopped)`。
- `ResetProcess()`：`Stop()` → 置 `SetPhase(Standby)` → `SetWeldStatus(Standby)`（线性阻塞链，非步控）。
- `ClearStatus()`：清报警与失败字段 → `SetPhase(Uninitialized)`（映射 `NoReset`）→ 执行步归 0。
- 连续监测（`continuous=true`）：每轮完成经步 800 `SetPhase(Acquiring)` 回步 10，`WeldStatus` 恒为 `Working`——单轮完成信号不经 `WeldStatusChanged` 透出，UI 按定时器节拍拉 `LastResult`/`LastOverlay` 刷新。
- 差异化职责（原档 R010）：**轴控制行为 + 送丝距离合规检查**——`SubDeviceLog()` 内 `// todo`，待落地后补充。

---

## 连接 / 生命周期契约

| 方法 | 语义 | 状态联动 |
|---|---|---|
| `InitializeOn()` | 阻塞连接（上电初始化用）：`EnsureConnected` + 校验连接态 | 成功：`State=Connected` + `SetPhase(Standby)` + `WeldStatus=NoReset` |
| `InitializeOff()` | 阻塞断开：`Stop()` + 清相位 | `State=Disconnected` + `WeldStatus=NoReset` |
| `ConnectOn()` | 非阻塞：自起后台线程（`MonitorCamManualConnect`，`_manualBusy` 防重入）连接相机 | 成功 `State=Connected`；失败 `State=Disconnected` |
| `ConnectOff()` | 非阻塞：`Stop()` 后置断开 | `State=Disconnected` |
| `ResetProcess()` | 见上 | `WeldStatus=Standby` |
| `ClearStatus()` | 复位前状态清理 | `WeldStatus=NoReset` |
| `ResetWorkTime()` | `ResetStepTime()`（基类） | — |
| `WeldStatusTrans()` | `NoReset` return；`ManualStopped`/`ErrorAborted` 且非 Standby → `SetPhase(Standby)` | — |

> `EnsureConnected()`：未连接时用 `MonitorCamManager.Config` 的 IP/Port 打开，配置为空则用 `DefaultIp`/`DefaultPort`。

---

## 配置项（`ConfigFileName = "MonitorCameraWorkflow"`）

| 配置元素 | 默认值 | 说明 |
|---|---|---|
| `TimeOutSeconds` | 30 | 基类超时阈值（秒） |

`LoadConfig` / `SaveConfig` **无参**，走 `XdocumentReaderWriter`（XML 文件 `Config/MonitorCam/Workflow_XML/MonitorCameraWorkflow.xml`）；`SaveConfig()` 末尾 `Config.SaveXdocument()` 落盘（裁定 D1）。采集超时用步 20 内 `AcquireTimeoutSeconds`（5s）判定，与 `TimeOutSeconds` 相互独立。

---

## 可观测性与释放

`GetStepName` 映射：`0 待机` / `10 触发采集` / `20 等待采集完成信号` / `30 算法分析` / `800 成功收尾` / `900 失败收尾` / 其余 `未登记步(N)`。

`SubDeviceLog()`（C7 契约）：输出连接态 / 焊接过程态 / 步骤名 / 检测阶段 / 合格 / 缺陷数。

`DisposeManaged()`（基类 `Dispose()` 钩子，ADR-027）：停相机巡检 + 释放 `_lastMat`/`_resultMat`（`_resultLock` 保护）。

---

## 事件

基类三事件之外，**仅 1 个受限例外**（ADR-016 R1 演进，2026-11-11）：

| 事件 | 来源 | 参数 |
|---|---|---|
| `WeldStatusChanged` | `DeviceStateBase` | `WeldStatusChangedEventArgs`（OldStatus/NewStatus/Reason/Timestamp） |
| `StateSwitched` | `DeviceStateBase` | `SubDeviceStateChangedEventArgs`（连接态） |
| `AlarmOccurred` | `DeviceStateBase` | `EventArgs` |
| `WeldPreviewFrame` | 本流程 | `Action<Mat>`，已 30Hz 节流的成品帧；订阅方拥有帧 |

---

## UI 接入（推状态 + 拉数据）

```csharp
using AdaWeldSystem.MainDeviceControl.DeviceWorkflow;
using AdaWeldSystem.MonitorCam;
using AdaWeldSystem.MonitorCam.Api;

// 1) 图像来自相机，不来自流程（R1）
MonitorCamManager.FrameCompletedEvent += OnFrameCompleted;
// 2) 健康状态来自相机（R1）
MonitorCamManager.Instance.StatusChanged += OnCamStatusChanged;
// 3) 流程进度来自基类（R3）
MonitorCameraWorkflow.Instance.WeldStatusChanged += OnWorkflowStatusChanged;

private void ShowResult()
{
    var wf = MonitorCameraWorkflow.Instance;
    Mat overlay = wf.LastOverlay;
    if (overlay != null && !overlay.IsEmpty) imageBox1.Image = overlay;
    MonitorResult r = wf.LastResult;
    txtResult.Text = string.Format("判定: {0}\r\n{1}", r.Pass ? "合格" : "不合格", r.Message);
}
```

调用方：`MonitorCamPage.cs`（`Stop()`）、`SystemControlPage.cs`（只读 `WeldStatus`）、`DeviceStatusWork`（按 `SubDeviceState` 参与互锁判定）。

---

## 关联

- [[modules/DeviceControl]] — 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（§4 契约 · §5 RunStep 驱动 · §16 模板）
- [[api/MonitorCamManager]] — 采集运行控制与健康巡检（图像/连接态/巡检的归属）
- [[api/AlgorithmManager]] — 算法层唯一实例化/取用入口（配置 + 检测 + 回放 + 线激光轮廓）；**2026-11-09 ADR-097 起本流程直取 `Instance`**（同级 Manager 不互持算法对象）
- [[api/PlaybackAlgorithm]] — 回放算法（扫描/解码/时间基准/倍速/跳转）
- [[decisions/ADR-016-WorkflowResponsibilityBoundary]] — 权责边界决策
- [[decisions/ADR-018-CallbackAcquisition]] — 回调采集（有界可失败语义）
- ADR-019（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[decisions/ADR-013-ThreeStateModelRefactor]]、[[decisions/ADR-035-RawDesignRefinement20260903]]、[[decisions/ADR-019-MonitorCamBoundaryAndEmguALGRefinement]]
