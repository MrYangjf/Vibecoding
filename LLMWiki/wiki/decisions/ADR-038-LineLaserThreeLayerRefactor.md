---
title: ADR-038 线激光三层重构与 SmartRay/海康 3D 移除
date: 2026-09-08
status: accepted
tags: [决策, 线激光, 相机, 三层架构, 管理器, 移除, ADR-038]
---

# ADR-038 线激光三层重构与 SmartRay/海康 3D 移除

## 背景

线激光族原为「`Api/ICameraRun` 接口 + 三套实现（SmartRay / 海康 3D / 英莱 / 虚拟）+ `CameraSelector` 静态选择器」结构，存在四个问题：

1. **实际只跑一条链路**：程序只使用英莱（真实）与虚拟（调试）两类相机，SmartRay 与海康 3D 属历史遗留，长期 0 使用却持续占据编译与维护成本；
2. **装配散落**：选择器 `CameraSelector` 是静态类，相机实例、连接态、IP 持久化三处逻辑分散在静态字段、INI 文件与具体相机类中；
3. **无抽象层承载基础设施**：事件与日志由各相机自行实现，跨相机订阅需逐个对接；
4. **与运控范式不一致**：[[modules/MotionControl]] 已确立「抽象层 + 厂商实现 + 业务层管理器」的三层范式，线激光未对齐。

## 决策

**D1 三层结构（仿运控）**

| 层 | 目录 | 内容 |
|---|---|---|
| L2 抽象 | `LineLaserCam/ILineLaser/` | `LineLaserType.cs`（`LineLaserKind` / `LineLaserConnectionState`）、`LineLaserEventArgs.cs`、`LineLaserCameraBase.cs` |
| L3 实现 | `IntelligentLaserCam/`、`VirtualCam/` | 英莱与虚拟相机，均继承 `LineLaserCameraBase` |
| 业务层 | 模块根 | `LineLaserManager.cs`（单例）+ `CameraRegistry.cs` + `LineLaserConfig.cs` |

**D2 抽象基类而非接口**：沿用运控 `MontionControl` 的抽象基类范式，把相机键名、连接态派生、帧就绪/状态变化两个事件与日志出口上提基类；派生类不得再声明私有 `Tag` / `Log`（避免 CS0108，见 [[lessons/DeviceControlWorkInheritanceBypass]] 坑一）。

**D3 管理器为唯一入口**：`LineLaserManager.Instance` 承担注册与选中、事件订阅与转发、连接态派生、配置持久化；`CameraSelector` 与 `ICameraRun` 一并删除。

**D4 配置改为 XML**：新增 `LineLaserConfig`（`Config/XML/LineLaserConfig.xml`，走 `FileOperate/XMLfile.cs`，`LoadConfig()`/`SaveConfig()` 无参，遵循 ADR-033 D1）。英莱 IP 由 `Config.SensorIp` 下发，原 `LoadSavedIp()` / `SaveSensorIp()` 与 `Config/INI/IntelligentLaser.ini` 弃用。

**D5 删除不再使用的实现**：`LineLaserCam/SmartRayCam/`（10 文件）、`LineLaserCam/HikRobotCam/`（3 文件）、`LineLaserCam/Api/`（2 文件），并移除 csproj 的 `Mv3dLpNet` 引用（海康 3D SDK）。
保留 `ProductFileManager/SmartRayConverter.cs` 与 `RunRecordManager.AddSmartRayFrame`——二者只依赖 `Smartray.Api.Point3d`（来自 `SRAPI_CSharp-x64` 引用，非本模块），属产品记录链路，不在本次移除范围。

**D6 命名采用规范拼写**：管理器为 `LineLaserManager`（非用户初稿的 `LinelaserMananger`），与既有 `MontionManager` 的历史拼写不再对齐——新模块一律规范命名。

**D7 消费方全量对接**：`LineLaserWorkflow`、`DeviceControlWork`、`ILCamPage`、`MainPage`、`ILAlgorithmEditForm` 五处由 `CameraSelector.X` 改为 `LineLaserManager.Instance.X`。

## 落地清单

| 项 | 状态 |
|---|---|
| L2 抽象三文件 | ✅ |
| 英莱 / 虚拟改继承基类（含 `RaiseFrameReady` / `RaiseStateChanged` 埋点） | ✅ |
| `CameraRegistry` / `LineLaserConfig` / `LineLaserManager` | ✅ |
| 删除 SmartRayCam / HikRobotCam / Api + `Mv3dLpNet` 引用 | ✅ |
| csproj 编译项更新（删 15 项 / 增 6 项） | ✅ |
| 消费方 5 文件改造（21 处调用点） | ✅ |
| Python 静态校验 18 项 | ✅ 全过 |
| **真编译** | ⏳ **待 Visual Studio**（沙箱无 C# 编译器） |

## 关联

- 模块页：[[modules/LineLaserCam]]、[[modules/VirtualCam]]、[[modules/IntelligentLaserCam]]
- API 页：[[api/LineLaserManager]]、[[api/VirtualCam]]、[[api/IntelligentLaserCam]]
- 历史决策（部分结论已被本 ADR 取代）：[[decisions/ADR-015-CameraConnectionStateDecoupled]]（连接态解耦**结论仍有效**，承载者由 `CameraSelector` 改为 `LineLaserManager`）、[[decisions/ADR-016-CameraSelectorUnifiedToApi]]（选择器已不存在）
- 范式来源：[[modules/MotionControl]]、[[decisions/ADR-036-MotionControllerDeltaReplacement]]、[[decisions/ADR-037-ZMotionRemovalAndDeltaLanding]]
