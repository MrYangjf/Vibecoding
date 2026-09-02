---
title: 运动控制开发专员
date: 2026-07-01
tags: [专员, 运动控制, 雷赛]
source: raw/skills/AdaWeldsys_Skills/02-Development/MotionControlSpecialist.md
---

# 运动控制开发专员

## 职责边界

- 雷赛控制卡（Leadshine）运动控制API封装与轴管理
- 焊缝跟踪算法结果引导XY运动轴移动
- 自动对焦算法结果引导Z轴移动
- 设备运行流程控制与状态机管理
- 轴参数配置与持久化（INI文件）
- 运动控制安全机制（软限位、急停、报警处理）

## 负责文件

MotionControl/
├── MotionController.cs        ← 运动控制器主类（单例）
│                                 - 雷赛控制卡API封装
│                                 - 轴使能/禁用/回零
│                                 - 绝对/相对定位运动
│                                 - 多轴直线插补
│                                 - 错误码转换与异常处理
├── AxisManager.cs             ← 轴管理器
│                                 - 单轴参数管理
│                                 - 轴状态监控
│                                 - 软限位检查
├── DeviceStateMachine.cs      ← 设备状态机
│                                 - 设备运行状态管理
│                                 - 状态转移合法性验证
│                                 - 状态变更事件通知
├── MotionConfig.cs            ← 运动参数配置
│                                 - 轴参数结构定义
│                                 - INI文件持久化
│                                 - 参数加载/保存
└── MotionEventArgs.cs         ← 运动控制事件参数
                                   - MotionCompletedEventArgs
                                   - DeviceStateChangedEventArgs
                                   - MotionErrorEventArgs

## 技术要点

- 单例模式: MotionController.Instance
- 轴控制参数: AxisParameter 结构体（脉冲当量、速度、加速度、软限位）
- 设备状态枚举: DeviceRunningState（Uninitialized/Initializing/Ready/Running/Paused/Alarm/EmergencyStop/Homing/ShuttingDown）
- 轴状态枚举: AxisState（Disabled/Standby/Moving/Homing/Alarm/PositiveLimit/NegativeLimit/HomeDone）
- 安全机制: 软限位检查、急停响应 < 50ms
- 焊缝跟踪响应延迟 < 100ms
- 自动对焦精度 ±0.05mm

## 处理流程

焊缝算法结果(X/Y偏移量) ──▶ MotionController.TrackSeamPos ──▶ XY轴移动(焊缝跟踪)
对焦算法结果(Z偏移量)  ──▶ MotionController.AdjustFocus    ──▶ Z轴移动(自动对焦)
                                    │
                                    ▼
                           DeviceStateMachine 状态管理

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| 图像算法专员 | SeamFeatureResult.CenterX/CenterY |
| 3D开发专员 | PointCloudData (Z轴高度数据) |
| 焊接工艺专员 | WeldProcess.LaserWeldData |
| UI开发专员 | MotionController.Instance, DeviceStateMachine |
| 通用技术专员 | GlobalCommData, SystemStatus |

---

*来源：raw/skills/AdaWeldsys_Skills/02-Development/MotionControlSpecialist.md*
