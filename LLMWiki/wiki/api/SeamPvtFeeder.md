---
title: API — SeamPvtFeeder 焊缝跟踪 PVT 点下发器
date: 2026-09-08
tags: [API, 运控, PVT, 台达, 焊缝跟踪, 依赖注入, ADR-039]
source: AdaWeldSystem/LineLaserCam/LineLaserManager.cs
---

# API — SeamPvtFeeder 焊缝跟踪 PVT 点下发器

> **2026-09-08 归并（ADR-040）**：本类不再单独立文件，与 `LineLaserManager` 同驻 `LineLaserCam/LineLaserManager.cs`。
> **位置**：`LineLaserCam/LineLaserManager.cs`（命名空间 `AdaWeldSystem.LineLaserCam`）
> **2026-09-08 新增（ADR-039）**：把线激光识别结果（焊缝特征点横向坐标 `FeatureY`）换算为 Y 轴 PVT 轨迹点，
> 按台达 **B 套流式**持续下载——`BeginMove` 起段 → 攒批 → 查缓冲区水位 → `ContinueMove` 续喂 → `FinishSegment` 收尾。
> **依赖注入面只有一个能力抽象 `IPVTMotion`**（L2），不感知控制器型号、不做脉冲换算（换算在 L3 完成）。

## 为什么走 PVT B 套

[[guides/DeltaEtherCAT-AdvancedMotion]] 结论③：PCI-L221 **无虚拟轴**（`Virtual_Set_Enable/Command` 只是坐标平移，
`Set_Virtual_Axis_*` 不存在），ECAM2 的 `SourceType` 只有 0（真实从站）/ 1（板载脉冲输入）两种取值，
机器人 X → Y 跟随无法用电子凸轮实现，**只能走 PVT 流式**。B 套即「起段 + 续喂 + 水位闭环」，可支撑无限长轨迹。

## 公共 API

| 成员 | 签名 | 说明 |
|------|------|------|
| 构造函数 | `(int batchSize, double defaultFrameSeconds, int minRemainBuffer)` | 攒批点数 / 帧率不可用时的默认帧间隔(秒) / 续喂水位下限 |
| `Attach` | `void (IPVTMotion axis)` | 注入 Y 轴 PVT 能力，传 `null` 撤除注入；内部先 `Detach()` |
| `Detach` | `void ()` | 收尾下发（`isFinal=true`）后撤除注入并复位状态 |
| `Reset` | `void ()` | 清空待下发点与运动状态，**不向轴发任何指令** |
| `FinishSegment` | `void ()` | 把剩余点标记为最后一段下发，结束本轮跟踪但**保留注入**（`SetWorking(false)` 时调用） |
| `SetParameters` | `void (int, double, int)` | 配置重载后更新三参数 |
| `Feed` | `void (LineLaserSeamResult result, double measuredFps)` | 喂入一帧结果；`!result.Valid` 直接丢弃；攒够 `BatchSize` 即 `Flush(false)` |
| `BatchSize` / `DefaultFrameSeconds` / `MinRemainBuffer` | 只读 | 当前参数 |
| `IsRunning` / `PendingCount` / `LastErrorCode` | 只读 | 起段后是否运动中 / 待下发点数 / 最近返回码（0 为成功） |

## 下发流程（Flush）

```
Feed(result, fps)
  → 帧间隔 dt = (fps > 1) ? 1/fps : DefaultFrameSeconds
  → 位置 pos = result.FeatureY（工程单位 mm）
  → 速度 vel = (pos - lastPos)/dt（首点 0）
  → _pending.Add(new PVTPoint(pos, dt, vel))    // 超过 MaxPending(8000) 丢弃最旧
  → _pending.Count >= BatchSize ? Flush(false) : 返回

Flush(isFinal)
  → 运动且非末段：GetInformation() 查 RemainBufferSize，< MinRemainBuffer 则保留本批继续攒
  → _running ? ContinueMove(segment, isFinal)
              : BeginMove(segment, PVTTimeMode.Relative, isFinal, false, 0.0)
  → 返回非 OK：_running = false + Error 日志「PVT 点下发失败 返回码 0x?? 点数 N」
```

## 约束与已知项

- **不持有 `MontionManager` / `MontionControl` / `Delta*`**：注入面只有 `IPVTMotion`（ADR-039 D6）。未实现 PVT 的轴由 `MontionAxis` 的 `virtual` 默认实现返回 `PVTResult.NotSupported`，**不抛异常、不连坐编译**，因此注入一个未支持的轴不会让线激光链路崩掉。
- **⚠️ 时间基准与速度前馈为待实测参数**：`Time` 取相邻帧实测间隔（`PVTTimeMode.Relative`），`Vel` 取位置一阶差分。现场需按实际跟随效果标定，配置项已预留 `LineLaserConfig.PvtFrameSeconds`（默认 1/60）、`PvtBatchSize`（16）、`PvtMinRemainBuffer`（200）。见 [[decisions/ADR-039-LineLaserResponsibilitySplit]] D7。
- **线程**：`Feed` 在 SDK 原生回调线程被调用（经 `LineLaserManager.OnCameraResultReady`），内部 `lock(_lock)` 保护；下发为同步调用，**耗时需关注**——批次过大可能拖慢回调，现场调 `PvtBatchSize`。
- 日志标签「焊缝跟踪」，纯文本无符号（[[standards/CodeSimplification]]）；注入/失败各一条，逐帧不记日志。

## 装配点

运控初始化成功后由 `MotionControlWorkflow.InitializeOn` 注入：

```csharp
string axisName = LineLaserManager.Instance.Config.SeamTrackAxisName;  // 默认 "Y轴"
MontionAxis axis = MontionManager.Instance.GetAxis(axisName);
if (axis == null) { Log("未找到焊缝跟踪轴 " + axisName, Warning); return; }
LineLaserManager.Instance.AttachYAxis(axis);   // 内部 SeamPvtFeeder.Attach(axis)
```

## 关联

- 决策：[[decisions/ADR-039-LineLaserResponsibilitySplit]]
- 持有者：[[api/LineLaserManager]]（`AttachYAxis` / `SetWorking`）
- 能力抽象：`MotionControl/IMotion/IPVTMotion.cs`（`IPVTMotion` + `PVTPoint` + `PVTInformation` + `PVTResult` + `PVTTimeMode`）
- 高级运动结论：[[guides/DeltaEtherCAT-AdvancedMotion]]
