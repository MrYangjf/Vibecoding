---
title: ADR-018 相机连接状态与工作流程状态解耦
date: 2026-07-21
tags: [决策, 相机, 状态机, 状态栏]
status: accepted
source: 用户需求 + AdaWeldSystem/LineLaserCam/Api/CameraSelector.cs、AdaWeldSystem/Workflow/LineLaserWorkflow.cs、AdaWeldSystem/UIDesign/ParentUI/FormMain.cs
---

# ADR-018 相机连接状态与工作流程状态解耦

> 状态：已采纳（2026-07-21）
> 关联：[[api/CameraSelector]]、[[api/LineLaserWorkflow]]、[[modules/LineLaserCam]]、[[modules/Workflow]]、[[modules/UIDesign]]

## 背景与问题

用户提出两类**相互独立**的状态语义，旧实现把它们混在一起：

1. **线激光相机自身状态**：只关心硬件连接与否、是否正在出图——表达为「连接 / 断开 / 工作中」三态。
2. **工作流程状态**：线激光工作流 10 态状态机（Uninitialized…ManualStopped）；「进入流程后，未手动停止 / 未异常终止 / 未焊接结束之前，都算工作流程中」。

旧代码把「相机是否出图」等同于「工作流在跑」，二者耦合，无法在状态栏同时正确表达「相机已连但未开始工作」与「流程运行中」。

## 决策

**将相机的连接态与工作流程态彻底解耦，由不同来源派生：**

- 相机连接态由 `CameraSelector`（线激光相机选择器）**聚合派生**，定义在统一对外接口文件 `LineLaserCam/Api/ICameraRun.cs`：
  - 新增枚举 `LineLaserCameraConnectionState { Disconnected, Connected, Working }`
  - 新增枚举 `CameraKind { None=0, SmartRay=1, Hik=2, Virtual=3 }`
  - `CameraSelector.ConnectionState` 派生规则：
    - `_working == true` → `Working`（仅由工作流 `SetWorking(true/false)` 驱动）
    - 否则按 `Kind` 派生：`None`→Disconnected；`Virtual`→Connected（始终可用，待 UI 区分「工作中/待启用」）；`SmartRay`→按 `CameraRun.Instance.IsConnected`；`Hik`→按 `HikCameraRun.Instance.IsCameraInitialized`
  - `CameraSelector.SetWorking(bool)` 仅被 `LineLaserWorkflow.Start()`（置 true）与 `WorkflowLoopWorker.finally`（置 false）调用。
- 工作流程态由 `LineLaserWorkflow` 的 10 态状态机 + 新增 `IsInWorkflow` 属性表达：
  - `_isWorkflowActive` 标志区分「每轮瞬态 Completed」与「真正焊接结束」。
  - 状态栏映射：`Starting/Acquiring/Analyzing/Adjusting` 与持续运行下的 `Completed` 均显示「工作流程中」；真正的 `Completed`（IsInWorkflow==false）才显示「完成（焊接结束）」。

## 后果

- ✅ 状态栏设备状态区可同时显示「线激光连接状态（连接/断开/工作中）」与「工作流程状态（工作流程中/完成/手动停止/异常终止）」两个独立维度。
- ✅ 相机只表达硬件事实，不感知工作流语义；工作流只驱动 `SetWorking`，不直接改连接态。
- ✅ 虚拟相机（仅模拟启用）启动不检测；无相机显示「未连接」；SmartRay/Hik 启动连通性检测。
- ⚠️ 启动检测 IP 当前硬编码（`192.168.178.200` SmartRay、`192.168.178.201` Hik），待从 `Config/INI/CameraPresets.ini` 读取（见 [[api/CameraSelector]] TODO）。

## 设计要点

- 跨线程安全：设备状态由 UI 定时器 `uiMillisecondTimer1_Tick`（UI 线程）轮询 `UpdateDeviceStatus()` 刷新，规避 `InvokeRequired` 与跨线程访问。
- 连接态与流程态解耦是本项目「状态责任单一」原则的体现，避免状态语义互相污染。
