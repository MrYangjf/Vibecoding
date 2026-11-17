---
title: ADR-039-SimulationTestAutoTerminationAndRecordCacheRelease
date: 2026-09-20
updated: 2026-10-30
tags: [决策, 模拟测试, 自动终止, 记录缓存释放, 焊缝跟踪轴名, ADR-032, ADR-037, ADR-038]
status: accepted
---

# ADR-039 模拟测试自动终止契约与记录缓存释放

> **背景（2026-09-20 实测四 BUG）**：模拟测试一轮跑下来暴露四类问题——
> ① 机器人 X 从 15 一路跑到 7000 mm 仍不自动停，靠人工点「停止」；
> ② 记录文件 `.pDat` 与轨迹 `.csv` 为空（**并非**人工停止所致，而是记录链路未触发）；
> ③ 线激光正常模拟时内存持续上涨，点停止后不回落（缓存落盘后未释放）；
> ④ 日志显示轴移动报警，但模拟未停、继续跑（实际用的是送丝力矩电机而非 Y 向电机）。
> 本 ADR 将上述修复沉淀为**模拟测试终止与记录正确性契约**，杜绝回归。

## 决 1：模拟行程到程须自动终止整段模拟

`MainDeviceControl/DeviceControlWork.cs` 的 `CheckWeldProgress()` 原在焊缝行程完成时只调 `DoSubStop()`（级联子设备 `Stopping`），**不终止主控模拟线程、不停止 robotX 时钟**。
**契约**：行程到程（焊缝长度完成）须调 `DisableSimulation()`，使 `SimTick` 的 robotX 时钟与模拟编排线程停止、记录落盘——X 不得持续前进。

## 决 2：模拟期参与设备异常 / 整机急停须立即终止模拟

`DeviceControlWork.SimScheduleTick()` 原无异常守卫，子设备 `ErrorAborted` 或整机 `Alarm`/`EStop` 时模拟继续跑。
~~**契约**：`SimScheduleTick()` 顶部须守卫——`Current == Alarm || Current == EStop` 或任一子设备 `WeldStatus == ErrorAborted` 时，立即 `EndProductSessionSafely("fail", …)` + `DisableSimulation()` 后 return。~~

> ⚠️ **2026-09-20 第二轮实测演进**：守卫含 `Current == Alarm` 被实测证伪——初始化部分失败（监控相机缺失 / 焊接头未启用，属实验台常态）会残留 Alarm 态，模拟线程首拍读到清警前的 Alarm 被**误杀**（现象：点「开启」log 直接提示结束）。
> **现行契约**：守卫只判 `Current == EStop` + 三个参与设备（运控/线激光/焊参）`WeldStatus == ErrorAborted`；`Alarm` 不再判（模拟不判真实硬件态，ADR-042）。且 `StartSimulation()` 的 `SimTestWorkOpen()` 必须置于 `DoClearAlarm()/DoStartMachine()` **之后**——线程启动时序与守卫收窄缺一不可。

## 决 3：记录落盘后必须释放内存缓存

`ProductFileControl/Records/RecordFileStore.cs` 的 `SaveRecord()` 原把 `.ply`/`.pDat` 落盘后**不清空** `_frames` / `_actionRecords` 内存列表，长时模拟内存只涨不降。
**契约**：`SaveRecord()` 在持久化（含 `.tmp` 崩溃恢复 + `.pDat` 写入）完成后须 `_frames.Clear()` + `_actionRecords.Clear()`，缓存随落盘释放（崩溃恢复以 `.tmp` 为准，不需常驻内存）。

## 决 4（配置前置约束）：焊缝跟踪轴名须落在运控实际轴名集合

`LineLaserCam/LineLaserConfig.cs` 的 `SeamTrackAxisName` 默认值原为 `"Y轴"`，而 `DeltaMotionConfig.xml` 实际启用的轴名为 `送丝力矩电机` / `Y向电机` / `Z向对焦电机`（**无 "Y轴"**）。
`_seamAxis` 解析为 `null` → `MotionControlWorkflow.UpdateSeamTracking()` 早退 → 轨迹点零产出、`.csv` 空。
**契约**：`SeamTrackAxisName` 必须取 `DeltaMotionConfig.xml` 中真实存在的轴名（现行 = `"Y向电机"`）；`LineLaserConfig.xml` 为空 `<Root/>` 时不覆盖 C# 默认值，故默认值须与运控实际轴名对齐。

## 决 5（2026-09-20 第二轮实测补充）：停止路径的 UI 冻结与状态归位

1. **归档落盘禁上 UI 线程**：`DisableSimulation()` 内 `EndProductSessionSafely` 实测写 87.8MB `.ply` 冻结界面 3.2s（停止按钮「卡」）。契约：归档移入后台线程（`ThreadPool`），命令执行路径（`DoSubStop` 等，本就在后台线程）可保持同步。
2. **停止须对称复位全部级联状态**：`Working` 迁移是全 5 子设备级联的，停止时只复位线激光/焊参会留下监控 `Working`、V3 卡 `Stopping`（`Current→Stop` 后 FlowProcess 不再驱动，`Stopping` 永无法迁移）。契约：`DisableSimulation()` 补监控 `RequestWeldStatus(Standby)`；`MotionControlWorkflow.Stop()` 模拟态 `Stopping` 受理后直接 `SetPhase(Idle)`。
3. **配置 XML 不随包分发**：`backup_adaweld.py` 排除 `bin/`，`DeltaMotionConfig.xml` / `LineLaserConfig.xml` 不会随 output 包到现场——现场轴名（`SeamTrackAxisName`）与轴地址（`NODE_ID`）漂移须人工同步（本轮实测机轴名仍是旧值「Y轴」、Y 向电机 `NODE_ID 3→0` 须按实测机硬件改配）。

## 影响文件

- `MainDeviceControl/DeviceControlWork.cs`：`CheckWeldProgress()`（行程到程调 `DisableSimulation`）、`SimScheduleTick()`（顶部异常守卫）
- `ProductFileControl/Records/RecordFileStore.cs`：`SaveRecord()` 落盘后清缓存
- `LineLaserCam/LineLaserConfig.cs`：`SeamTrackAxisName` 默认值 `"Y轴"` → `"Y向电机"`
- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs`：虚拟相机分支须触发 `WeldParamControlWorkflow.ComputeAndOutput()` 驱动 `.pDat` 填充
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs`：`Stop()` 模拟态 `Stopping` 直归 `Idle`（2026-09-20 决 5.2）
- `bin/Debug/Config/XML/DeltaMotionConfig.xml`（现 `bin/Debug/Config/MotionControl/Motion_XML/DeltaMotionConfig.xml`）：`Y向电机` `NODE_ID 3→0`（按实测机硬件地址，2026-09-20 决 5.3）

## 关联

- 模拟统一化：[[decisions/ADR-032-SimulationTestRedesign]]
- 生产记录生命周期：[[decisions/ADR-037-ProductProductionRecordLifecycle]]
- 机器人指令驱动步骤流（行程判断归主控）：[[decisions/ADR-038-RobotCommandDrivenStepFlow]]
- 焊缝跟踪 CSP：[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]
- 运控台达：[[decisions/ADR-027-MotionControllerDeltaReplacement]]
- 配置架构：[[decisions/ADR-033-ConfigArchitectureStandard]]
- 教训：[[lessons/SimulationAutoBranching]]（陷阱九~十三）
- 模块：[[modules/LineLaserCam]] · [[modules/MotionControl]] · [[modules/ProductFileManager]]

## 背景

（待补：本决策要解决什么问题）

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 后果

### 正面
- （待补）

### 负面
- （待补）

## 相关页面

- [[decisions/ADR-Index]]
