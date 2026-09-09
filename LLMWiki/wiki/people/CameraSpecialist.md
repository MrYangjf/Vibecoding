---
title: 工业相机开发专员
date: 2026-07-01
tags: [专员, 相机]
source: raw/skills/AdaWeldsys_Skills/02-Development/CameraSpecialist.md
---

# 工业相机开发专员

## 职责边界

- SmartRay 工业3D轮廓传感器 SDK 封装与驱动开发
- 海康机器人2D相机 SDK 封装
- 相机参数配置与预设管理
- 连续采集控制与数据回调管理
- 相机连接稳定性优化

## 负责文件

SmartRayCam/
├── ApiCore.cs
├── CameraRun.cs （2026-09-08 已删除：ADR-038 线激光三层重构，见 modules/LineLaserCam）
├── CameraPresetManager.cs （2026-09-08 已删除：ADR-038 线激光三层重构，见 modules/LineLaserCam）
├── DeviceDiscovery.cs
├── FrameBuffer.cs
├── ImageConverter.cs
├── TriggerMode.cs
├── CalibrationData.cs
├── ErrorHandler.cs
└── ConnectionManager.cs

HikRobotCam/
├── HikCameraManager.cs （2026-09-08 已删除：ADR-038 线激光三层重构，见 modules/LineLaserCam）
├── HikCameraDevice.cs （2026-09-08 已删除：ADR-038 线激光三层重构，见 modules/LineLaserCam）
└── ImageAcquisition.cs

## 技术要点

- SmartRay SRAPI（P/Invoke 封装）
- 海康 Mv3dLpNet SDK
- 回调等待模式：AcquisitionCompletedSignal + LastAcquisitionSuccess
- 实时预览模式（Live）与工作模式（PIL）分离

## 协作关系

| 协作对象 | 协作内容 |
|----------|----------|
| 图像算法专员 | 提供 Mat 图像数据 |
| 3D开发专员 | 提供点云原始数据 |
| 通用技术专员 | 全局状态同步 |
| UI开发专员 | 相机状态显示界面 |

---

*来源：raw/skills/AdaWeldsys_Skills/02-Development/CameraSpecialist.md*
