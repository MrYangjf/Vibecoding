---
title: ADR-005 回调等待取图决策
date: 2026-07-01
tags: [决策, 相机, 异步, 回调]
status: accepted
source: history.md [46]
---

# ADR-005：回调等待取图决策

## 状态
已采纳（2026-07-01）｜**结论有效，边界已澄清（2026-09-01 治理标注）**

> **ℹ️ 与「单步内禁阻塞等待」红线的关系**：**不冲突，本 ADR 的 `WaitOne` 属合法的有界等待**。
> 裁定判据（原见旧标准 [[standards/StepDrivenWorkflow]]（已废弃）红线 3，现由 [[architecture/DeviceControlArchitecture]] §5 承接）：**有界 + 可失败 = 合法；无界 + 静默 = 违规**。本方案的 `WaitOne` 满足①有上界（按帧周期缩放，默认上限 5000ms）②超时可失败（`_lastAcquiredMat = null`）③外部信号源驱动（相机回调 `Set()`，非空转轮询）。
> **约束**：若流程改为步骤驱动，该等待必须落在「等待完成」单步内，并在超时后跳 9xx 失败收尾；**不得演化为 `while(true)` 无界轮询**。

## 背景

Workflow 取图使用同步轮询（循环检查 CameraRun.CurrentMat 是否有新数据），CPU 占用高、响应延迟不确定。

## 决策

改为 **回调等待模式**：

`
AcquireImage():
    1. AcquisitionCompletedSignal.Reset()
    2. CameraRun.SensorRunContinue()  // 触发采集
    3. AcquisitionCompletedSignal.WaitOne(超时按当前扫描率帧周期缩放)  // 等待回调
    4. if (CameraRun.LastAcquisitionSuccess)
           获取 CameraRun.CurrentMat
           推进到下一步
       else
           停留重试
`

## 关键设计

- AcquisitionCompletedSignal：AutoResetEvent 实例字段（非 static）
- LastAcquisitionSuccess：bool 后备字段（MSBuild v4.0 兼容）
- WaitOne 超时按扫描率帧周期缩放（默认上限 5000ms）：超时后 _lastAcquiredMat = null
- CameraRun 连续运行模式：首次 SensorRunContinue 启动，后续回调自动触发

## 后果

- CPU 占用显著降低
- 取图响应时间确定（由相机帧率决定）
- 需要处理回调超时和失败重试

---

*来源：raw/history/history.md [46]*
