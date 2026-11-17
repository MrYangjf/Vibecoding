---
title: ADR-045 预测性机器人位姿快照
date: 2026-09-28
updated: 2026-10-30
tags: [决策, 焊缝跟踪, 机器人位姿, 预测, WeldParamControl]
status: accepted
---

# ADR-045：预测性机器人位姿快照

## 背景

机器人位姿按**固定频率喂入**（真实 = RSI 回包 ~83Hz；**模拟 = SimTick 节拍采样喂入**——底层墙钟连续计算，但只在每个节拍采样一次，业主 2026-09-28 确认两条链路同为阶梯）。两次喂入之间，`WeldParamManager.CurrentRobotX/CurrentRobotY` 呈**阶梯保持**。该阶梯经焊缝地图跟踪的**写入时刻机器人 Y 差分**（ADR-042 §1.2：`Yt − RobotYGain × (Yb2 − Yb1)`，Yb2 = 写入时刻机器人 Y）与查图中心 X 逐拍进入 CSP 闭环，业主在 SeamTraceY 数据上观测到 **CSPinY 与实时Y 周期性来回波动**，与喂入节拍同频——即阶梯激励的极限环响应。

## 决策

在位姿唯一持有者 `WeldParamManager` 内建**位姿预测器**（`UpdatePosePredictor` / `PosePredictElapsedSeconds` / `ClampPredictVelocity`，状态全部在 `_robotXLock` 内）：

1. **锚点**：每个喂入点到达即重设锚点 =（最新 X/Y，时刻 t_i）——「速度变化则变更 StartX + 新速度」的逐点重锚等价形式；
2. **速度**：V_i = (P_i − P_{i−1}) / (t_i − t_{i−1})，X/Y 各自差分、带符号；dt ≤ 0 保持旧 V；幅值钳位 `PosePredictMaxSpeedMmPerS = 100 mm/s`（吸收异常差分尖峰）；
3. **失效间隔守卫**：距上一喂入超过 `PosePredictStaleGapSeconds = 1.0 s`（源切换 / 暂停续跑）时速度清零重立锚，防旧速度串场外推；
4. **快照**：`CurrentRobotX/Y` getter 在预测器激活时返回**读取时刻外推值** = 锚点 + V × (t − t_锚)；外推时长钳位 `PosePredictMaxExtrapolateMs = 200 ms`（喂入停止即冻结，防按旧速度漂移）；
5. **双链路同机制**：真实 RSI（`OnRobotDataReceived`）与模拟节拍（`UpdateRobotPose(x,y,z)`）**都喂入预测器**——预测器与喂入源无关，两条链路的阶梯机理一致（业主 2026-09-28 确认模拟同病同修）；
6. **边界不变式**：~~地图入图 `SeamMapTrackingAlgorithm.OnRsiPose` **保持喂入原值**——喂入时刻预测值与喂入值相等，故地图键（测量时刻 RobotX + 前置量）…全部不变；只有**写入时刻读取**（Yb2、查图中心）从阶梯变为连续~~ ⚠️ **2026-09-29 业主纠正 + 就地补正（编号不变）**：「喂入原值」原则**只约束 Y**（Y 曾用滤波写入、效果差才回退为原值计算，见 ADR-048/049）；**X 从未被约束**，本条把 Y 的原则错套到了 X 上。X 侧的正确口径是 **写入与读出同源、都取预测值**：

 - 现状（错误）：`OnRsiPose` 喂入 RSI 原值 ⇒ `arriveX = _monotonicRobotX + 前置量` 为阶梯（实测约 50% 拍键不变、并出现 15~21mm 空洞），而查图/记录用外推值 ⇒ **两列不同源** ⇒ 目标阶梯保持与冻结，表现为**固定频率 X 导致的周期性微顿**。
 - 现行（2026-09-29 补正）：新增 `SeamMapTrackingAlgorithm.UpdatePredictedRobotX(robotX)`（只单调推进 `_monotonicRobotX`，未建基准不抢建），由 `WeldParamManager.OnSeamLaserResult` 在入图前以 `CurrentRobotX`（外推值）刷新 ⇒ **入图键与查图键同源于同一条连续 X 时间轴**。
 - 不变：`OnRsiPose` 仍喂原值（锚点/路径/折返语义不受影响）、`UpdatePosePredictor` 未动、ADR-042 的 `Yt = Ya1 + d` 公式结构与 Y 侧原值原则不变。

## 备选方案

- **对地图/差分输出做时间域低通**：⛔ 已有 ADR-042 明令禁止（地图值禁任何时间域低通——滤 d 会引入轴速度残余自激，滤合成引入恒滞后）；预测是**源头重建**而非输出滤波，不违反该禁令。
- **在运控侧（MotionControlWorkflow）单独平滑 robotY**：消费点分散（运控/记录/查表/UI），单点平滑会造成多源不一致，违反 Manager 单一入口范式（ADR-006）。
- **提高喂入频率 / 改 RSI 包结构 / 让模拟按墙钟连续喂入**：机器人侧改动超出主控可行动范围；模拟按更高频率喂入只是把阶梯变细、并不消除，且与真实链路口径不一致。
- **仅修真实链路、模拟不动**：⛔ 业主 2026-09-28 裁决推翻——模拟测试同样按频率喂入、同样有此问题，且模拟是 F1 验收必要条件，两条链路必须同机制。

## 后果

### 正面
- 写入时刻机器人 Y 差分（Yb2 − Yb1）与查图中心 X 由阶梯变连续，消除与喂入同频的闭环激励；真实与模拟两条链路同修；
- 记录（SeamTraceY 当前RobotX 列）、查表输出 X、界面观测同步受益，曲线无阶梯；
- 预测器未激活（无任何喂入）时完全回退既有行为（读 RobotWeldData 原值）。

### 负面
- 外推在喂入源变速瞬间存在至多一个喂入周期的误差，由下一喂入点重锚纠正；
- 喂入停止（失联/停走/模拟关闭）后位姿按锚点 + 速度 × 200ms 冻结，与旧行为（保持最后喂入值）存在有限偏差；
- 钳位参数目前为私有常量（非配置项），现场如需调整须改代码。

## 演进记录

### 线激光轮廓帧 X 改由位姿真相源提供（业主裁定）

- 原路径：`LineLaserManager.OnProfileFrame` 经 `DeviceControlWork.GetEffectiveRobotX()` 取 X，其语义为「模拟开 ? `CurrentRobotX` : 0.0」⇒ 真实焊接态所有轮廓帧 X 记为 0，并造成 `LineLaserCam → MainDeviceControl` 反向依赖。
- 现路径：直读 `WeldParamManager.Instance.CurrentRobotX`。模拟路由（`SimTick → UpdateRobotPose(_simRobotX)`）与真实路由（RSI `OnRobotDataReceived`）两条写入链原样保留，均汇入本属性并带读取时刻外推。
- 约束：**两条路都不得断**；`GetEffectiveRobotX()` 及其余模拟行程判定消费方保持不变。
- 后果：真实态轮廓帧 RobotX 由 0 变为真实坐标，历史记录数据语义改变（业主明确批准）。
- 配套：配置实例所有权收归 Manager（`MontionManager.CreatePreviewMotionConfig()` / `AlgorithmManager.CreateEmptyPipelineConfig()`），UI 不再外部 `new`。

## 相关页面

- [[decisions/ADR-042-SeamTrackingConsolidated]]（写入时刻机器人 Y 差分被本决策由阶梯演进为连续）
- [[modules/WeldParamControl]]
- [[api/WeldParamManager]]
- [[modules/KUKARobot]]（RSI 上报源）
