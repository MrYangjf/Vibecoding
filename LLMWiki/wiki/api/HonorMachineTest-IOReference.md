---
title: HonorMachineTest IO 监控与执行参考基线
date: 2026-09-07
tags: [API, IO, 线程模型, 参考基线, DeviceStatusWork, 流程编排]
source: "E:\\SoftwareGit\\HonorMachineTest\\PcomDeviceInterface\\Work\\（MachineControlWork.cs（外部参考项目原文件名，本项目现役 DeviceControlWork.cs） + MachineStatusWork.cs（外部参考项目原文件名，本项目现役 DeviceStatusWork.cs） + Process/）"
---

# HonorMachineTest IO 监控与执行参考基线

> **章节导航**：
>
> - [1. 定位](#1-定位)
> - [2. 线程模型：三线程 + 工位线程](#2-线程模型三线程--工位线程)
> - [3. 耗时动作一律异步拉起](#3-耗时动作一律异步拉起)
> - [4. 触发只执行一次的两种闭锁](#4-触发只执行一次的两种闭锁)
> - [5. 状态前置门控](#5-状态前置门控)
> - [6. 对 AdaWeldSystem 的映射](#6-对-adaweldsystem-的映射)
> - [7. 刻意不借鉴的项](#7-刻意不借鉴的项)

## 1. 定位

`E:\SoftwareGit\HonorMachineTest\PcomDeviceInterface` 是本项目 `MotionControl/IMotion/` 抽象层的**原型来源**
（雷赛 `LSnmcControler` 实现层亦出自此，见 [[api/LeadshineLSnmc-Reference]]）。

2026-09-07 用户指定：本项目 **IO 监控与执行**的组织方式以此为参考基线。
涉及两个文件：

| 文件 | 行数 | 职责 |
|---|---|---|
| `Work/MachineStatusWork.cs` | 633 | 安全/IO/状态监控（`EMGIOWork` / `IOWork` / `StatusWork` 三线程） |
| `Work/MachineControlWork.cs` | 463 | 整机动作编排（启动/停止/复位/急停 + 每工位独立流程线程） |

## 2. 线程模型：三线程 + 工位线程

```
MachineStatusWork.StartWork()
  ├─ thEMGIOWork   EMGIOWork()    急停与安全门，循环内无 Sleep，全速扫描
  ├─ thIOWork      IOWork()       按钮/指示灯/安全装置，Thread.Sleep(30)
  └─ thStatusWork  StatusWork()   三色灯状态反射，Thread.Sleep(30)

MachineControlWork.StartWork()
  ├─ thLineWork / thScanWork / thAssemblyWork / thRollPressWork / thBatterySpaceWork
  └─ 每个工位一个线程，循环调 XxxProcess.Instance.FlowProcess()
```

**要点**：

- 急停扫描线程**不含 Sleep**，与常规 IO 扫描分离，保证最高响应；
- 状态反射（三色灯）与 IO 扫描分离，避免灯效逻辑拖慢安全判定；
- 每个工位的流程**各自一个线程**，互不阻塞，冷启动后由 `StartWork` 一次性拉起。

## 3. 耗时动作一律异步拉起

复位要跑数十秒，`MachineControlWork.ResetMachine()` 的做法是——**IO 扫描线程只拉起 Task 后立即返回**：

```csharp
public void ResetMachine()
{
    if (!IsReseting)
    {
        IsReseting = true;
        CommenData.CurrentStatus = MachineStatus.Reseting;
        new Task(() =>
        {
            int resetStep = 0;
            while (CommenData.CurrentStatus == MachineStatus.Reseting)
            {
                switch (resetStep) { /* 步骤推进 */ }
            }
            IsReseting = false;
        }).Start();                       // ← 异步，IO 线程不被占用
    }
}
```

而 `IOWork()` 里对按钮的响应只是置状态或调瞬时方法（`StartMachine` / `StopMachine` / `ClearAlarm`），
**没有任何一个分支会阻塞扫描循环**。

> **这是本项目 2026-09-07 修复的核心**：`DeviceStatusWork.ScanPulseIo` 原为同步调 `ExecuteIo`，
> 初始化链 20 秒独占 IO 线程。现改为 `TakeVirtualIo → 记日志 → DispatchAction（拉线程）→ 返回`。

## 4. 触发只执行一次的两种闭锁

物理按钮按下会持续为 ON，若不闭锁会每拍重复触发动作。参考项目用两种手段：

### 4.1 边沿标志 + 长按计时（按钮类）

```csharp
if (montionManager.InputStartButton.IsON())
{
    if (!IsStartButtonPress) { IsStartButtonPress = true; StartPressTime = DateTime.Now; }
    else if ((DateTime.Now - StartPressTime).TotalMilliseconds > 600)
    {
        IsStartButtonPress = false;
        machineControlWork.StartMachine();       // 长按 600ms 才生效
    }
}
else { IsStartButtonPress = false; }             // 松开复位标志
```

启动 600ms、复位 4000ms——**长按确认**兼作防误触。

### 4.2 一次性闭锁标志（急停类）

```csharp
if (pressed && !emgShown) { emgShown = true; /* 执行一次 */ }
else if (!pressed && emgShown) { emgShown = false; /* 松开后允许下次 */ }
```

**AdaWeldSystem 的等价实现**：脉冲型虚拟 IO 用 `TakeVirtualIo`（`HashSet.Remove`，命中即清位），
语义上比边沿标志更强——**IO 在动作开始前就已经不存在了**，不存在任何重复触发窗口。

## 5. 状态前置门控

安全装置检查带状态前置条件，避免已报警时反复重复报警：

```csharp
if (CommenData.CurrentStatus != MachineStatus.Alarm
 && CommenData.CurrentStatus != MachineStatus.EStop
 && CommenData.CurrentStatus != MachineStatus.Stop)
{
    if (CommenData.IsCheckDoor) { /* 门/风扇/气源 ... 首次命中即置 Alarm */ }
}
```

复位过程还带**中止检测**：每步 `Task.WaitAll` 后检查状态是否仍为 `Reseting`，
若已变（急停/报警）立即记「复位过程被中止」并返回 false。

## 6. 对 AdaWeldSystem 的映射

| 参考项目 | AdaWeldSystem | 状态 |
|---|---|---|
| `EMGIOWork`（全速） | `DeviceStatusWork.EMGWork`（`EmgPollIntervalMs` 50ms） | ✅ 已有，周期略长但可接受 |
| `IOWork`（30ms） | `DeviceStatusWork.IOWork`（50ms） | ✅ 已有 |
| `StatusWork`（三色灯） | `DeviceStatusWork.LightStatusWork` | ✅ 已有 |
| 每工位独立流程线程 | `DeviceControlWork` 5 条 `thXxxWork` | ✅ 已有 |
| 复位异步 `new Task().Start()` | `DispatchAction` 拉 `thAction` | ✅ 2026-09-07 补齐 |
| `EMGshow` 闭锁 | `emgShown` 闭锁 | ✅ 已有 |
| 按钮边沿 + 长按 | `TakeVirtualIo` 取走即清位 | ✅ 更强（无触发窗口） |
| 状态前置门控 | `IsSafe` + `CheckPreworkFailed` + `ScanPulseIo(requireRunning)` | ✅ 已有 / 2026-09-07 补齐 |
| 复位中止检测 | `DoResetMachine` 每步前置问询（`IsActionAborted` / `IsInitAborted` / `IsInitPreempted`）+ `CascadeResetProcess` 每步问询 `Reseting` | ✅ 2026-09-07 落地 |
| 运行态抢占即停 | `SubDeviceWork` 每拍问询 `Current`，从 Running **真正跌出**才记「停止驱动」（`wasDriving` 门控 + `LogDriveStopped` Interlocked 只记一次；启动默认态 NoReset 从未 Running，不打日志）；**线程不改状态**——状态只由 IO 动作链（DoXxx → SetStatus）管理 | ✅ 2026-09-07 落地 / 2026-09-08 修启动误报（用户裁定：线程只判断不执行，不修改状态） |

### 6.1 线程问询范式（2026-09-07 合规核对沉淀）

参考代码的两条铁律及我方逐点比对结论（**合规范**）：

1. **判断是否属于自己的状态，只判断不改**——线程问询 `Current` 后只决定「执行 / 不执行」，
   状态赋值只出现在动作链（参考：`ResetMachine` 的 `while (CurrentStatus == Reseting)` 门控 +
   `Task.WaitAll` 后复查；我方：`SubDeviceWork` 每拍问询、`CascadeResetProcess` 每步静默
   `Current != Reseting` 即中止）。
2. **防空调节拍**——所有循环必须有 Sleep：参考流程线程 非 Running `Sleep(100)+ResetWorkTime()` /
   Running `FlowProcess()+Sleep(10)`；我方同值（`BeatIdleMs=100` / `BeatWorkMs=10`），
   连接等待轮询 `WaitChildPollMs=100`，IO 三线程 50ms（参考 30ms，可接受）。
   参考的 `LineWork`（无 Sleep 空转）与 `RunControl`（`while(true)`）属第 7 节不借鉴项。

## 7. 刻意不借鉴的项

| 项 | 原因 |
|---|---|
| 物理 IO 直读（`montionManager.InputXxx.IsON()` 散落全方法） | 本项目为虚拟 IO 中转，三种触发源统一入口 `SetVirtualIo`，扫描器不区分来源 |
| `CommenData.CurrentStatus` 全局静态状态 | 本项目已收敛为 `DeviceControlWork.Current`（单一控制源，ADR-027） |
| `MessageBox.Show` 出现在流程层（`ClearMachineStatus` 里点检提示） | 违反分层，UI 交互不得下沉到设备流程 |
| `Task.WaitAll` 阻塞主线程等复位 | 本项目初始化链已改为「出结果即退出」，等待有界且可区分失败/超时 |
| 无 `IsClose` 优雅退出（`while(true)`） | 本项目 `_running` + `IsCloseWork` 标志位，禁 Abort |
