---
title: MonitorCameraRun API 参考
date: 2026-07-13
updated: 2026-08-31
tags: [API, 相机, 监控, 运行控制, 健康巡检]
source: AdaWeldSystem/MonitorCam/MonitorCameraRun.cs
---

# MonitorCameraRun API 参考

> 监控相机运行控制单例。底层 SDK 通过 `IMonitorCameraApi` 抽象，当前实现为 `HikvisionCameraApi`（海康面阵相机，MvCameraControl.Net SDK）。
> 参考 SmartRay `CameraRun` 的 Live/PIL 模式与采集完成信号机制（[[decisions/ADR-005-CallbackAcquisition]]）。
>
> **权责（ADR-030 R1）**：本类是监控相机的**唯一数据产出方**——图像、连接态、健康巡检全部归属本类。
> 2026-08-31 由 `MonitorCameraWorkflow` 下沉健康巡检至此（此前流程越权持有，见 [[decisions/ADR-030-WorkflowResponsibilityBoundary]]）。

## 核心类

```csharp
public class MonitorCameraRun : IDisposable
{
    // 单例访问
    public static MonitorCameraRun Instance { get; }

    // 实时帧完成事件（UI 订阅，图像唯一输出通道）
    public delegate void MonitorCameraFrameCompletedHandler(object sender, MonitorCameraFrameCompletedEventArgs e);
    public static event MonitorCameraFrameCompletedHandler FrameCompletedEvent;

    // 健康监督状态变更事件（2026-08-31 由工作流下沉）
    public event EventHandler<MonitorSupervisionStatusChangedEventArgs> StatusChanged;

    // 采集完成信号（Workflow 回调等待，readonly 字段，非 static）
    public readonly AutoResetEvent AcquisitionCompletedSignal;

    // 公共属性
    public bool IsLiveMode;                       // Live 预览模式
    public bool LastAcquisitionSuccess { get; private set; }
    public Mat CurrentMat { get; }                // 当前帧（lock 保护）
    public bool IsRun { get; }                    // 是否已连接
    public MonitorCameraConnectionState ConnectionState { get; }
    public MonitorCameraConfig Config { get; set; }

    // 健康巡检属性（2026-08-31 新增）
    public MonitorSupervisionState SupervisionState { get; private set; }
    public bool IsMonitorCameraWorking { get; }   // 已连接 + 有效期内有过有效采集
    public DateTime LastHealthyTime { get; }
    public int CheckIntervalMs { get; set; }      // 巡检周期，默认 1000
    public int HealthyValidMs { get; set; }       // 健康有效期，默认 5000

    // 公共方法
    public void OpenSensor(string ip, string port);
    public void SetPhase(MonitorCameraPhase phase);
    public void ChangeMode(bool enableLive);      // true=启动 Live 采集，false=停止
    public void SensorRunContinue();              // 触发一次 PIL 采集（Live 模式不响应）
    public void SensorStop();                     // 停止采集并退出 Live
    public void StartSupervision();               // 启动健康巡检线程
    public void StopSupervision();                // 停止健康巡检线程
    public void Dispose();                        // IDisposable，非 Dispose(bool)
}
```

## 枚举与结构

```csharp
// 以下三者均定义于 MonitorCam/Api/IMonitorCameraApi.cs
//   MonitorCameraPhase 于 2026-08-31 由 MonitorCameraWorkflow.cs 下沉至子设备 Api 层
//   （此前子设备反向依赖流程命名空间，违反依赖方向约定）
public enum MonitorCameraPhase { Unknown, PreWeldAlignment, WeldQuality }
public enum MonitorCameraConnectionState { Disconnected, Connecting, Connected, Error }
public enum MonitorSupervisionState { Idle, Checking, Healthy, Degraded, Error }
```

## 健康巡检（2026-08-31 由工作流下沉）

内置巡检线程，`StartSupervision()` 启动、`StopSupervision()` 停止，`Dispose()` 中自动停止。

| 状态 | 判定条件 |
|---|---|
| `Idle` | 未启动巡检 |
| `Checking` | 刚启动，尚未完成首轮评估 |
| `Healthy` | 已连接 **且** 距 `LastHealthyTime` 在 `HealthyValidMs` 内 |
| `Degraded` | 已连接但有效期内无成功采集 |
| `Error` | 未连接 |

- **健康时间来源**：Live 回调 `OnApiFrameReceived` 与 PIL 成功采集 `RaiseFrameCompleted(true)` 均刷新 `LastHealthyTime`
- 状态或工作标志变化时触发 `StatusChanged` 并记录日志
- UI 侧（[[api/FormMain]] / MonitorCamPage）订阅后收敛到统一刷新入口，参见 [[lessons/UiRefreshUnifiedEntry]]

> 流程侧不再持有任何健康状态：`MonitorCameraWorkflow.SupervisionState` / `LastHealthyTime` / `CheckIntervalMs` / `IsMonitorCameraWorking` 均已移除，改读本类同名属性。

## 回调流程

`
SensorRunContinue() → Task 异步 AcquireOnce()
                           ↓
              _api.CaptureSingleFrame() 同步取帧 → 写入 CurrentMat
                           ↓
              LastAcquisitionSuccess = true/false
              AcquisitionCompletedSignal.Set()   // 通知 Workflow
              FrameCompletedEvent (IsLive=false)

// Live 模式（ChangeMode(true)）
HikvisionCameraApi 实时采集回调 → FrameReceived → FrameCompletedEvent (IsLive=true)
（不触发 AcquisitionCompletedSignal）
`

## 使用规范

- 调用 `SensorRunContinue()` 前必须确保 `ConnectionState == Connected`（先 `OpenSensor`）
- PIL 模式下 Workflow 使用 `AcquisitionCompletedSignal.WaitOne(5000)` 等待回调；Live 模式不参与
- 健康巡检由工作流在 `Start()`/`Stop()` 时调用 `StartSupervision()`/`StopSupervision()` 启停，也可由 UI 直接调用
- 释放资源调用 `Dispose()`（IDisposable），**禁止重写 `Dispose(bool)`**，遵循 [[decisions/ADR-001-DisposePattern]]
- 配置落盘路径：`Config/INI/MonitorCamera.ini`，遵循 [[decisions/ADR-007-ConfigLayout]]
- 权责边界见 [[standards/WorkflowResponsibilityBoundary]]：本类产出数据，[[api/MonitorCameraWorkflow]] 只做编排

---

## 关联

- [[api/MonitorCameraWorkflow]] — 消费本类的编排方（只读调用 + 拉结果）
- [[api/MonitorAlgorithmManager]] — 算法配置（对中容差 / 质量合格分）
- [[standards/WorkflowResponsibilityBoundary]] — 权责执行细则（R1 数据产出归属）
- [[decisions/ADR-030-WorkflowResponsibilityBoundary]] — 健康巡检下沉决策
- [[modules/MonitorCam]] — 所属模块

*来源：AdaWeldSystem/MonitorCam/MonitorCameraRun.cs + IMonitorCameraApi.cs*
