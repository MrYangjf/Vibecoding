---
title: ADR-040 线激光引导 Y 轴轨迹构造（PVT 写入权移交 WeldParamControl）
date: 2026-09-11
tags: [决策, 线激光, Y轴, PVT, 焊缝跟踪, 轨迹构造, WeldParamControl, ADR-040]
status: deprecated
superseded_by: ADR-041-WeldParamControlAlgorithmArchitecture
---

> ⛔ **已废弃**：本决策的轨迹构造机制已被 ADR-041 取代。`SeamGuide/` 目录、`ISeamTrajectoryBuilder` / `SeamTrajectoryBuilder` 单例已删除；轨迹跟踪算法现为 `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs`（非单例实现），由 `WeldParamManager` 统一管理，仅输出 `PVTPoint[]`，写入控制器职责保留在 `MotionControlWorkflow`。下文保留仅作历史沿革参考。

# ADR-040：线激光引导 Y 轴轨迹构造（PVT 写入权移交 WeldParamControl）

## 背景

ADR-035 把「结果侧算 Y 轴 PVT 点并下载」归到 `LineLaserManager`（内嵌 `SeamPvtFeeder`），实现了 `FeatureY → PVTPoint` 的最短链路。但该做法存在三个与现场不符的事实错位：

1. **直写 PVT 缺算法环节**：线激光特征值存在抖动（实测序列如 `2.55 2.57 2.56 2.58 2.55 2.58 2.59 2.56 2.59 2.59 2.57`），直接换算会让轴产生微小来回回调，对焊接轨迹是灾难性的；且线激光坐标与引导轴存在比例差（轴 1mm 对应线激光 0.9mm 量级）与零点不一致，必须经标定转换。
2. **缺机器人坐标与时间戳融合**：线激光前置在焊枪前约 50mm，最快 500ms 后焊枪 TCP 才到达该点。必须把线激光结果、机器人坐标、时间戳整帧绑定后再做轨迹计算，才能保证机器人到达时控制器已缓存轨迹段且仍在续写。
3. **职责归属错误**：线激光管理器承担的是「采集 + 识别结果转发」，把「运动轨迹生成」放在相机模块内，使相机模块反向持有运动语义；该算法属于焊接工艺侧，应在控制器工作流程中调用。

## 决策

1. **新增线激光引导子系统**（`WeldParamControl/SeamGuide/`，命名空间 `AdaWeldSystem.WeldParamControl.SeamGuide`）：
   - `SeamGuideSample`：把线激光结果、机器人 X 坐标、引导轴当前位置与时间戳搓合为一个中性样本。
   - `ISeamTrajectoryBuilder` / `SeamTrajectoryBuilder`：轨迹构造能力契约与实现（单例）。
   - `SeamGuideConfig`：标定与修正参数，**并入 WeldParamControl 现有配置**（`Config/XML/WeldParamControlWorkflow.xml` 的 `SEAM_GUIDE` 段）。

2. **两级修正 + 标定转换**（偏差模型）：
   - 标定转换：`偏差 = (特征Y − 零点) × 轴/线激光比例 × 方向`；`运动目标 = 轴当前值 + 偏差`。
   - 无值容差：机器人行程内无有效结果时偏差记 0 继续移动，累计行程超过 `NoValueToleranceMm` 即报警。
   - 超限剔除：相邻偏差跳变超过 `OutlierLimitMm` 的点不归入轨迹计算，保持上一有效偏差维持轨迹连续。
   - 单调约束：机器人行程窗口 `MonotonicWindowMm` 内轨迹只朝一个方向移动（方向由 `MonotonicDeadbandMm` 死区锁定），抑制反向微小回调。

3. **写入权移交**：`LineLaserManager` **不再直接写 PVT**——删除内嵌 `SeamPvtFeeder` 与 `AttachYAxis`，只保留 `ResultReady` 结果转发与轮廓侧业务。`LineLaserConfig` 的 PVT 三项（批次/帧间隔/水位）随之移除，仅保留 `SeamTrackAxisName`。

4. **调用方 = 控制器工作流程**：`MotionControlWorkflow` 在 `Ready` 相位周期驱动——
   - 装配：按 `SeamTrackAxisName` 取轴，`SeamTrajectoryBuilder.AttachAxis(IPVTMotion)`，并订阅 `LineLaserManager.ResultReady`；
   - 喂入：`LineLaserWorkflow` 进入 `Working` 时 `Reset()` 起段，逐帧 `Feed(结果, 实测帧率, 轴当前位置)`，离开 `Working` 或停机时 `Finish()` 收尾；
   - 节拍：`Tick()` 保证**至少每 `MaxOutputIntervalMs`（默认 250ms）输出一段 PVT 轨迹**，与 500ms 的相机前置滞后匹配；
   - 报警：`HasFault` 置位即 `Fail(FaultReason)` 转失败收尾。

## 后果

### 正面
- 相机模块与运动语义解耦：`LineLaserManager` 只做采集与结果转发，不再持有 PVT 写入能力。
- 轨迹质量可控：滤波/剔除/单调三条修正与标定转换集中在 `SeamTrajectoryBuilder`，参数落 XML 可现场标定。
- 实时性有保证：250ms 强制输出节拍 + 8000 点上限的流式攒批，覆盖 50mm 前置滞后。

### 负面 / 遗留
- `LineLaserCalibration` 的 Y 向标定未扩展；本轮标定以 `SEAM_GUIDE` 的比例/零点/方向三项承载，若后续需要旋转+平移的手眼标定模型需另立决策。
- 单调约束按机器人行程窗口自动重判方向；焊缝在窗口内反向拐弯的场景需现场实测后调整 `MonotonicWindowMm` / `MonotonicDeadbandMm`。
- `MotionControlWorkflow` 的周期驱动依赖 `DeviceControlWork` 子设备线程的 `FlowProcess` 节拍；若线程周期大于 250ms，输出节拍受其上限约束。
- 真编译待 Visual Studio；Python 静态校验已完成（新文件 csproj 注册一致、无残留 `SeamPvtFeeder`/`AttachYAxis`）。

## 相关页面

- [[modules/WeldParamControl]]
- [[api/SeamTrajectoryBuilder]]
- [[api/MotionControlWorkflow]]
- [[modules/LineLaserCam]]
- [[api/LineLaserManager]]
- [[api/SeamPvtFeeder]]（已废弃，⛔）
- [[decisions/ADR-035-LineLaserResponsibilitySplit]]
- [[decisions/ADR-039-MonitorCamBoundaryAndEmguALGRefinement]]
