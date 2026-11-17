---
title: "ADR-058 光丝对中毫米化与剪丝链（两套算法合并 · Y 三级只报警 · X 补偿单点耦合 · RSI T13 回检循环）"
date: 2026-10-09
updated: 2026-10-09
tags: [ADR, 光丝对中, 剪丝, 送丝, 监控相机, EmguALG, DeviceControlWork, P3]
status: accepted
---

# ADR-058：光丝对中毫米化与剪丝链

> P3 功能实现批F（F-7 光丝对中毫米化与三级报警 + F-8 剪丝异常检测与指令下发 + F-9 送丝控制正常路径）的落地裁定。
> 需求 33/34/35/36/37 + 决策④（剪丝本体不执行）/决策⑥（送丝机只前进）。

## 背景

光丝对中存在**两套算法**：在用像素套（`WireFeedDistanceAlgorithm → ImageAlgorithm.DetectPreWeldAlignment`，只出像素）
与死代码毫米套（`RealtimeMonitorAlgorithm.CheckCentering`，出 mm 三级分级 + 剪丝判据，零消费）。
剪丝链 S-8 已铺协议层（RSI Tech T13 / EKI `TxCutWire`）但**无触发方**；送丝指令与 X 补偿无耦合点。

## 决策

### 一、两套算法合并，死套整文件删除

毫米化/三级/剪丝判据语义**并入 `WireFeedDistance/` 三件**（`WireFeedResult` / `WireFeedConfig` / `DetectPreWeldAlignment`），
`RealtimeMonitorAlgorithm.cs` 整文件删除（双 pattern 交叉验证零外部消费；csproj 退注册 + `drift_scan_precise.py` REMOVED 登记）。
新枚举 `WireAlignGrade`（Pass/Warn/Fail）落 `WireFeedResult.cs`（替代死套 `CheckGrade`，ADR-003）。
`ToleranceAngle` 删除（需求 34/36 无角度判据，原「定义未参与判定」一并清走）。

### 二、轴向映射与毫米化（需求 36 的 XY 口径）

| 输出 | 含义 | 去向 |
|---|---|---|
| `WireStickoutDevMm` | 送丝方向偏差（需求 36 的 **X 向**，正=焊丝偏长） | F-9 送丝补偿 |
| `LateralDevMm` | 横向偏差（需求 36 的 **Y 向**） | F-7 三级报警（**只报警不自动调整**，需求 34/37） |
| `OffsetX/OffsetY`（像素） | 光斑对准偏差 | 振镜微调（F-4 `ApplySpotAlignCompensation`，批H） |

- 换算：`mm = 像素 × PixelMmScale`（标定系数，`PIXEL_MM_SCALE` 四点闭环）。
- **轴向假设**：水平像素轴 = 送丝方向（`StickoutAxisHorizontal`，装反置 false 换轴；`StickoutSign` 换符号）——
 ⚠️ **真机核实点 ①**：相机安装方向确认后固化默认值。

### 三、三级判定（需求 34/36）

按 **Y 向（横向）偏差**分级：≤ `WIRE_ALIGN_WARN_MM`（0.1）安全 / ≤ `WIRE_ALIGN_FAIL_MM`（0.3）黄灯提示 / 超红灯报警。
算法产出 `Grade`；消费方（`DeviceControlWork.MonitorAlignTick`）：红灯边沿 `ReportAlarm`/`ReportAlarmCleared`，
黄灯限频提示（约 5s 一条），安全静默。阈值可配（需求 33 UI 归 P4 监控相机页）。
⚠️ **存储位置注记**：P1 §3.2 记「MonitorCamera.ini」，实际随 `AlgorithmManager` 的算法 INI（`Alignment` 段）四点闭环持久化
（S-9 已有先例——阈值本属算法配置）；**键名不变**。

### 四、剪丝链（F-8，决策④：本体只发指令）

1. **判据**（S-9 口径）：`WireMatched=false`（焊丝未识别）或 `WireHeadAdhesion=true`（光斑未识别⇒遮挡/粘连）→
 `MonitorResult.WireAnomalyDetected/WireAnomalyReason`（本批补齐 S-8 预告字段）。
2. **回检循环**（`DeviceControlWork.MonitorAlignTick`，ADR-041 常驻非阻塞，⛔ case 内禁 Sleep/while）：
 异常 → 下发剪丝请求（**RSI Tech T13 置位**，经 `CommunicationManager.UpdateRobotWeldParams`——本批为该链首个消费者）→
 **无回执，超时兜底**（200 拍 ≈ 10s 复位 T13）→ 回逻辑1 重新检测 → 仍在异常则下一循环。
 **循环上限 `MaxCutWireCycles=3`** 超过降级：报警转人工（`_cutWireDegraded` 锁存，异常清除后复位）。
3. **降级备选**：EKI `CommandCore.TxCutWire` 已备，按外部依赖④「RSI 不行再启用 EKI+RSI 并行」——**暂不并行发送**。
4. 开关门控：`WIRE_ANOMALY_CUTWIRE`（默认 true，可配）。

### 五、X 向送丝补偿单点耦合（F-9）

`DeviceControlWork.ComposeWireFeedSpeed(algoFeedSpeed)` 是**送丝指令唯一组装点**：
`补偿后速度 = 工艺送丝速度 + (-WireStickoutDevMm × WIRE_FEED_COMP_GAIN)`，**钳 ≥0（决策⑥ 送丝机只前进，偏长只能减送不能回抽）**。
`WeldParamControlWorkflow.SendToRobot` 的 S 值与剪丝请求的 T12 值**都走此单点**（耦合防冲突）。
⚠️ **真机核实点 ②**：补偿增益（mm 偏差 → 速度补偿的比例）现场标定；偏长超限时物理上无法回抽，靠三级报警人工干预。

### 六、标定数据（需求 36 光斑/焊丝标定，流程数据先落配置）

`WireFeedConfig` 承载标定基准（`SPOT_REF_X/Y` 光斑视野位置、`WIRE_STICKOUT_TARGET_MM` 焊丝伸出目标（标定精度 ±0.02mm）、
`PIXEL_MM_SCALE` 像素→mm 系数），四点闭环。**标定操作流程 UI 归 P4**（相机设置·监控相机 + U-1 快速标定），P3 只落数据与消费。

## 备选方案

| 备选 | 放弃原因 |
|---|---|
| 保留两套算法各自演化 | 死套零消费且语义重复；合并避免双真相源（P1 明令「合并两套删死代码」） |
| 三级判定放 UI 层 | 判定是算法语义，UI 只显示三态（U-7） |
| 剪丝回检循环挂 MonitorCameraWorkflow | 02 sheet 裁定触发逻辑入 DeviceControlWork（工作流 using 通讯层破坏三层边界 + ADR-038 子流程不自迁步） |
| EKI+RSI 并行发剪丝 | 外部依赖④：先 RSI 主路径，实测不行再并行 |
| X 补偿独立下发通道 | 与送丝指令双写必冲突，收敛到单一组装点 |

## 后果

### 正面
- 光丝对中一套实现、毫米化、三级可视（U-7 三态数据源就绪）；死代码套出清（-431 行）
- 剪丝链闭环：判据 → 标志位 → 报警 → T13 → 超时兜底 → 回检 → 降级，全非阻塞
- 送丝指令单点组装，X 补偿耦合防冲突；正常路径不剪丝（决策④ 边界）

### 负面 / 待验证
- 轴向映射（水平=送丝方向）与补偿增益需现场核实/标定（真机核实点 ①②）
- 剪丝 T13 无回执，超时值（10s）为保守初值；回检循环上限 3 次为工程默认
- 标定操作 UI 未落地（P4）；`MonitorResult.OffsetX/Y` 的振镜消费（F-4）归批H

## 相关页面

- [[decisions/ADR-041-ResidentFlowNonBlockingParadigm]] —— 回检循环范式
- [[decisions/ADR-030-WeldHeadSlaveDeviceUnderMotionControl]] · [[decisions/ADR-057-TaLaActionAndFollowControl]]
- [[api/DeviceControlWork]] · [[api/AlgorithmManager]] · [[api/CommunicationManager]]
- [[lessons/JudgementThresholdScaleMismatch]] —— 阈值/量纲类改动日志自证
- [[project/ReviewOptimization-P1-StructureDesign]] —— 需求 33/34/36/37 与 02 sheet 链路图
