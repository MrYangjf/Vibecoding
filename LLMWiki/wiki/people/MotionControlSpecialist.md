---
title: 运动控制开发专员
date: 2026-07-01
tags: [专员, 运动控制, 台达]
source: raw/skills/AdaWeldsys_Skills/02-Development/MotionControlSpecialist.md
---

# 运动控制开发专员

> ⚠️ **2026-09-17 审计修订**：本页原文为雷赛（Leadshine）时代内容，已随控制器换轨（[[decisions/ADR-027-MotionControllerDeltaReplacement]] / ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]），2026-09-07）整体过时，现按台达 EtherCAT 现行实况重写。原文仅存于 raw/skills/ 原档。

## 职责边界

- 台达 PCI-L221 EtherCAT 主站运动控制 API 封装与轴管理（`MotionControl/DeltaEtherCAT/`）
- 焊缝跟踪 CSP 实时目标逐拍输出（`OutputCspTick()`，ADR-027/058）
- 设备运行流程控制与三态模型状态机管理
- 轴/IO/气缸参数配置与持久化（`DeltaMotionConfig` + CSV 导入，ADR-035）
- 运动控制安全机制（软限位、急停、报警处理）

## 负责文件

> 现役文件清单以 [[modules/MotionControl]] 为权威，此处列骨干。

MotionControl/
├── IMotion/                    ← 中性抽象与运行时轴对象（MontionAxis 等）
├── DeltaEtherCAT/              ← 台达实现层（DeltaMontionAxis / EtherCAT Native / MotionConfigImporter）
├── MontionManager（单例）       ← 唯一对外入口
└── （沿革）雷赛时代 MotionController.cs / AxisManager.cs / MotionConfig.cs 已随 ADR-013/033 删除

设备状态归 `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs`：
- 连接态 `SubDeviceState`（2 态）+ 焊接过程态 `SubDeviceWeldStatus`（7 态）
- 状态写入唯一入口 `SetState`/`SetWeldStatus`（禁手工赋值）

## 技术要点

- 单例模式：`MontionManager.Instance`
- 脉冲当量：`Equiv` = mm/pulse，`ToPulse(v) = v / Equiv`
- 状态模型：三态模型 `SubDeviceState` + `SubDeviceWeldStatus` + `MainDeviceStatus`（ADR-021）
- CSP 输出：步骤驱动红线——模组工作流**禁自带常驻线程**（主工作即全阻塞 `FlowProcess`，由编排层 `DeviceControlWork.SubDeviceWork` 运行态 10ms/100Hz 节拍驱动）；**短生命周期线程允许**（如 `ConnectOn/ConnectOff`），但须 `IsBackground=true` 且 `finally` 释放资源；`case` 体内禁 `Thread.Sleep`/`while` 轮询（ADR-027/058）
- 层级约束：L2 零依赖，L3 继承 L2 调 L1，Native 只被 L3 调
- 安全机制：软限位检查、急停响应

## 处理流程

焊缝算法结果 ──▶ `SeamMapTrackingAlgorithm`（示教锚定 Y 空间地图 + CSP 实时目标，ADR-042）
                              │
                              ▼
`MotionControlWorkflow.UpdateSeamTracking()` → `OutputCspTick()` 逐拍写轴（实测 dt 限幅）

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| 图像算法专员 | 焊缝特征结果（经 `WeldParamManager.FeedSeamTracking`） |
| 焊接工艺专员 | `WeldParamManager.Instance.AlgorithmsConfig`（只读配置） |
| 3D开发专员 | PointCloudData（轮廓点云） |
| UI开发专员 | `MontionManager.Instance`，`MotionControlWorkflow.WeldStatus` |

---

*来源：raw/skills/AdaWeldsys_Skills/02-Development/MotionControlSpecialist.md（2026-09-17 按台达现况重写）*
