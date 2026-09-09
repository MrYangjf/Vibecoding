---
title: HikRobotCam 模块 — 海康机器人3D线激光相机
date: 2026-07-01
tags: [模块, 相机, 海康, 线激光, 3D]
source: raw/knowledge/AdaWeldSystem_Wiki.md
---

# HikRobotCam 模块 — 海康机器人3D线激光相机

> **位置**：`AdaWeldSystem/LineLaserCam/HikRobotCam/`（2026-07-21 由根目录迁入 `LineLaserCam/` 父目录，与 SmartRayCam / VirtualCam 同属线激光相机族）。
> 负责海康机器人工业 **3D 线激光（轮廓）** 相机的 SDK 封装、图像采集和参数配置。使用 **Mv3dLpNet** SDK（海康 MV3D-LP 系列 3D 线激光轮廓传感器）。

## 核心文件

| 文件 | 职责 |
|------|------|
| HikCameraManager.cs | 相机管理器（单例，设备发现/连接管理） |
| HikCameraDevice.cs | 设备封装（连接/断开/采集，MV3D-LP 3D 线激光轮廓） |
| HikCameraRun.cs | 相机运行控制（实现 `ICameraRun`，Snapshot 单次采集，与 SmartRayCam.CameraRun 同级） |

## 技术要点

- SDK: Mv3dLpNet（海康 **MV3D-LP 系列 3D 线激光轮廓** SDK，对应 `MV3D_LP_*` 结构体）
- 支持 GigE/USB3 接口
- 与 modules/SmartRayCam 同为 **3D 线激光相机**：SmartRayCam 用 SmartRay SRAPI，本模块用海康 MV3D-LP SDK，二者均实现 `ICameraRun` 同一契约

## 协作关系

- modules/EmguALG → 提供 3D 轮廓/点云用于算法
- modules/UIDesign → 3D 轮廓实时显示
- modules/SmartRayCam / modules/VirtualCam → 同属 modules/LineLaserCam 线激光相机族，共享 `ICameraRun` 契约

---

*来源：raw/knowledge/AdaWeldSystem_Wiki.md + AdaWeldSystem/LineLaserCam/HikRobotCam/ 模块源码*
