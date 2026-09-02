---
title: CameraRun API 参考
date: 2026-07-01
tags: [API, 相机, SmartRay, 线激光]
source: AdaWeldSystem/LineLaserCam/CameraRun.cs
module: LineLaserCam
---

# CameraRun API 参考

> **所属模块**：[[modules/LineLaserCam]] — SmartRay 线激光相机运行控制接口。

## 核心类

`csharp
public class CameraRun
{
    // 单例访问
    public static CameraRun Instance { get; }
    
    // 公共属性
    public AutoResetEvent AcquisitionCompletedSignal { get; }
    public bool LastAcquisitionSuccess { get; }
    public Mat CurrentMat { get; }
    public bool IsLiveMode { get; set; }
    
    // 公共方法
    public bool Connect(string deviceId);
    public void Disconnect();
    public void SensorRunContinue();
    public void StopAcquisition();
    public void SetPreset(CameraPreset preset);
    
    // 事件
    public event EventHandler<AcquisitionEventArgs> OnCompletedAcqEvent;
    public event EventHandler<ErrorEventArgs> OnErrorEvent;
}
`

## CameraPreset 结构

`csharp
public struct CameraPreset
{
    public int Exposure;      // 曝光时间 (us)
    public int Gain;          // 增益
    public int LaserPower;    // 激光功率 (%)
    public int TriggerMode;   // 触发模式
}
`

## 回调流程

`
SensorRunContinue() → SmartRay SDK 单次采集（PIL/工作流：Snapshot 模式；Live 预览：RepeatSnapshot 连续）
                           ↓
              OnCompletedAcqEvent (回调)
                           ↓
              if (!IsLiveMode):
                  - 处理点云 → Mat
                  - LastAcquisitionSuccess = true/false
                  - AcquisitionCompletedSignal.Set()
              if (IsLiveMode):
                  - 仅更新 Live 显示
`

> **采集模式（AcquisitionMode）**：
> - **工作流 / PIL 模式**：`Api.AcquisitionMode.Snapshot`（单次快照）—— 每次 `SensorRunContinue()` 采集一帧；`OnCompletedAcqEvent` 在单帧交付、`AcquisitionCompletedSignal.Set()` 后复位 `isRun`，由 `LineLaserWorkflow.AcquireImage` 每周期重新触发（runonce 语义，避免连续产帧与工作流分析/资源销毁竞争）。
> - **Live 实时预览**：`Api.AcquisitionMode.RepeatSnapshot`（连续快照）—— `ChangeConfig(true)` 切换时设置，持续产帧供预览。

---

*来源：raw/knowledge/AdaWeldSystem_Wiki.md + raw/skills/02-Development/CameraSpecialist.md*
