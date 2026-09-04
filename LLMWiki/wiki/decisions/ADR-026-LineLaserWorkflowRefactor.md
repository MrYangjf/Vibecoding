---
title: ADR-026 线激光工作流分步重构（switch-case + step）
date: 2026-08-20
status: accepted
tags: [ADR, 工作流, 线激光, 状态机]
---

# ADR-026 线激光工作流分步重构（switch-case + step）

## 背景

原有线激光工作流（`LineLaserWorkflow`）存在以下架构问题：

1. **Starting 态空转**：`Start()` 直接启动线程，线程里立刻 `TryTransitionTo(Running)`，Starting 没有实质动作（开激光/开传感器/等待数据稳定）
2. **待机时传感器开启**：`InitializeWorker` 的 `resetDevice` 步骤调用了 `SensorRunContinue()`，导致 Standby 状态下传感器就在运行（持续回调），浪费资源且不安全
3. **Running 单态大包干**：`WorkflowLoopWorker` 只有一个 while 循环调用 `ExecuteRunning()`，没有分步结构，无法体现 PreWork/Starting/Working/Stopping 的流程语义
4. **无 PreWork 步骤**：没有启动前的状态清理、计数重置、残留数据清理步骤
5. **与主设备协同缺失**：MainDeviceThread 只是调用 `Start()` 启动，没有分步协同机制

用户明确要求线激光工作流采用 switch-case + step 方式，由主设备分步驱动控制。

## 决策

将线激光工作流从「单 Running 态循环」重构为「switch-case + step 分步状态机」，由主设备分步驱动。

### 状态枚举扩展

从 7 态扩展为 9 态：

| 状态 | 说明 |
|------|------|
| Uninitialized | 未初始化 |
| Initializing | 初始化中 |
| Standby | 待机（传感器/激光均关闭） |
| **PreWork** | **启动前准备（清理状态/计数/残留数据）** |
| Starting | 启动中（开激光+开传感器+等待数据稳定） |
| **Working** | **工作中（回传ScottPlot+分析结果+数据记录）**——替代原 Running |
| **Stopping** | **停止中（关激光+关传感器+清理）** |
| ErrorAborted | 异常终止 |
| ManualStopped | 手动停止 |

### 状态流转路径

```
Uninitialized → Initializing → Standby
                                    ←──┐
Start() → PreWork → Starting → Working → Stopping → Standby
                                    ↓
                              ErrorAborted
```

### 主设备分步协同机制

由 `MainDeviceThread` 分步驱动线激光子设备：

1. **第一步**：`LineLaserWorkflow.Instance.Start()` → 进入 PreWork
2. **等待 PreWork 完成**：`WaitForLineLaserPreWork(timeout)` 轮询 `IsPreWorkDone`
3. **第二步**：`LineLaserWorkflow.Instance.BeginStarting()` → 进入 Starting（开激光+传感器）
4. **等待数据稳定**：`WaitForLineLaserDataStable(timeout)` 轮询 `IsDataStable`
5. **第三步**：`LineLaserWorkflow.Instance.BeginWorking()` → 进入 Working（焊接开始）

详见 [[modules/DeviceControl]] 线激光工作流章节和 [[api/LineLaserWorkflow]]。

### 待机安全默认态

待机状态下传感器、激光、采集相机均关闭。Starting 阶段才逐步开启：
1. 采集相机 → 2. 激光 → 3. 传感器

### Starting 阶段数据稳定性判断

- `_startingValidFrameCount` 累计连续有效帧数
- 必须连续 `DataStableFrameCount`（默认 5）帧有效才置 `_dataStable = true`
- 无效帧重置计数（必须连续有效，不能有中断）

## 后果

### 正面

- 流程语义清晰，分步可控，符合工业设备分步启动的工程惯例
- 待机时传感器关闭，更安全且节省资源
- 主设备可精确控制子设备启动节奏，便于多设备协同
- Starting 阶段数据稳定后才进入 Working，避免焊接初期数据不稳定
- switch-case 结构便于扩展（如新增预热/收尾步骤）

### 负面

- 状态枚举从 7 态扩展到 9 态，UI 层所有状态显示点需同步更新
- 启动流程变长（PreWork + Starting 两步等待），总启动时间增加约 1~2 秒
- MainDeviceThread 启动逻辑从单行调用变为三步协同，复杂度提升

### 缓解措施

- 所有 UI 状态显示点统一通过 `IsWorkflowRunning()` 辅助函数判断「运行中」集合，减少散点修改
- PreWork 为纯内存操作（计数清零），耗时 < 10ms，对启动时间影响可忽略
- Starting 阶段数据稳定判断有超时保护（10s），避免无限等待
