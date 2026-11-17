---
title: 工业相机开发专员
date: 2026-07-01
tags: [专员, 相机]
source: raw/skills/AdaWeldsys_Skills/02-Development/CameraSpecialist.md
---

# 工业相机开发专员

> ⛔ **职责变更横幅（2026-09-17 审计）**：SmartRayCam/ 与 HikRobotCam/ 已于 2026-09-08 随 [[decisions/ADR-022-EmguALGThreeLayer]] 线激光三层重构**整目录删除**（下文仅存文件级注记不代表目录仍在）。**现役相机链**：线激光相机（英莱 IntelligentLaserCam + VirtualCam 虚拟相机，`LineLaserCam/`）与监控相机（麦格威 MecaVision，`MonitorCam/`）。本页保留作沿革与通用相机开发职责参考。

## 职责边界

- 线激光相机（英莱）SDK 封装、连接管理与数据回调（现役，`LineLaserCam/IntelligentLaserCam/`）
- 监控相机（麦格威 MecaVision）SDK 封装（现役，`MonitorCam/MecaVisionCam/`）
- 虚拟相机产帧（模拟测试，[[api/VirtualCam]]）
- 相机参数配置与连接稳定性优化
- （历史，已删）SmartRay 工业 3D 轮廓传感器 SDK 封装；海康机器人 2D/3D 相机 SDK 封装

## 负责文件

LineLaserCam/ （现役，ADR-007 三层结构，见 [[modules/LineLaserCam]]）
├── IntelligentLaserCam/IntelligentLaserCam.cs   ← 英莱相机实现
├── ILineLaser/LineLaserCameraBase.cs            ← 相机抽象基类（原 Api/ICameraRun 沿革承继）
├── LineLaserManager.cs                          ← 唯一对外入口（含 CameraRegistry）
└── VirtualCam/VirtualCam.cs                     ← 虚拟相机（模拟产帧）

MonitorCam/MecaVisionCam/ （现役，见 [[modules/MonitorCam]]）
└── Native/MVSDK.cs                              ← 厂商 SDK 原样（命名空间例外，ADR-005）

SmartRayCam/ / HikRobotCam/ （⛔ 2026-09-08 随 ADR-007 整目录删除，文件清单留史：
CameraRun / CameraPresetManager / HikCameraManager / HikCameraDevice 等均已删）

## 技术要点

- 英莱 SDK：三层控制解耦（SetSensorEnable 触发轮廓回调 / SetLaser 仅物理激光 / SetCaptureCamera 仅预览），详见 [[lessons/IntelligentLaser-Pitfalls]]
- MecaVision：Native DLL 加载时序（[[lessons/MecaVision-NativeDllLoadNRE]]）
- 虚拟相机：33ms 节拍产帧（[[api/VirtualCam]]）
- （历史）回调等待模式 AcquisitionCompletedSignal + LastAcquisitionSuccess；Live/PIL 分离

## 协作关系

| 协作对象 | 协作内容 |
|----------|----------|
| 图像算法专员 | 提供轮廓/图像数据 |
| 3D开发专员 | 提供点云原始数据 |
| 通用技术专员 | 全局状态同步 |
| UI开发专员 | ILCamPage / MonitorCamPage 状态显示 |

---

*来源：raw/skills/AdaWeldsys_Skills/02-Development/CameraSpecialist.md（2026-09-17 按现役相机链修订）*
