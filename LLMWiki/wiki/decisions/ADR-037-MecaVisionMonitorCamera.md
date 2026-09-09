---
title: ADR-041 监控相机三层重构并切换麦格威（IMonitorCam / MecaVisionCam / MonitorCamManager）
date: 2026-09-08
tags: [决策, 监控相机, MecaVision, MVSDK, 海康, ADR-009, ADR-038, ADR-039]
status: accepted
---

# ADR-041：监控相机三层重构并切换麦格威（IMonitorCam / MecaVisionCam / MonitorCamManager）

> 2026-09-08 落地：本 ADR 由「仅切换 SDK 实现」修订为「三层重构 + 切换」，目录结构对齐 MotionControl（ADR-036/037）与线激光（ADR-038/039）范式。

## 背景

监控相机模块（[[modules/MonitorCam]]）原为 4 文件平铺：`Api/IMonitorCameraApi.cs` + `Api/HikvisionCameraApi.cs`（海康 MvCameraControl.Net）+ `MonitorCameraRun.cs`（422 行业务单例）+ `MonitorAlgorithmManager.cs`（算法参数）。现供应商方案切换为麦格威（MecaVision）。二手开发指导给出的是「另一项目」风格的平行架构（新建 `MonitorCamera/` + `IVisionCamera` + `MonitorCameraManager`），与 ADR-009 抽象现状冲突。SDK 原文核验：33 个声称 API、13 个错误码数值、9 结构体、4 回调委托**零臆造**（见 [[api/MecaVisionMVSDK-Native]]）。

## 决策

1. **三层目录范式**（用户指定「参照 MotionControl」）：
   ```
   MonitorCam/
   ├── IMonitorCam/            # 抽象层 L2：IMonitorCamApi + 3 枚举 + 3 事件参数
   ├── MecaVisionCam/          # 实现层 L3：MecaVisionCam.cs + Native/MVSDK.cs（官方原样）
   └── MonitorCamManager.cs    # 业务中枢（Lazy 单例），由 MonitorCameraRun 改名承接
   ```
2. **实现层只做回调触发**（ADR-039 准则）：`MecaVisionCam` 只负责取帧并抛 `FrameReceived`；阶段语义、健康巡检、配置持久化全归 `MonitorCamManager`。
3. **删除海康实现**（用户裁定）：`HikvisionCameraApi.cs` 与 csproj 中 `MvCameraControl.Net` 引用一并删除，不保留平行双实现（ADR-038 处置先例）。
4. **命名空间**：抽象层 `AdaWeldSystem.MonitorCam.IMonitorCam`、实现层 `AdaWeldSystem.MonitorCam.MecaVisionCam`，与线激光 `ILineLaser/`、`IntelligentLaserCam/` 命名同构。
5. **取帧路径**（以官方 Basic/FirstStep 例程为实证，非推测）：
   - Init：`CameraSdkInit` → `CameraEnumerateDevice` → **`CameraGigeGetIp` 按 IP 匹配**（匹配不到回退首台并记日志）→ `CameraInit` → 黑白传感器 `CameraSetIspOutFormat(MONO8)` → `CameraSetTriggerMode(0)` → 挂断联回调。
   - Live：`CameraSetCallbackFunction` + `CameraPlay`，回调内 `CameraFlipFrameBuffer`（SDK 输出自底向上）→ 建 `Mat` → `Clone` 出独立副本。
   - PIL：`CameraGetImageBuffer` → `CameraImageProcess` → `CameraFlipFrameBuffer` → 建图 → **必须 `CameraReleaseImageBuffer`**。
6. **回调委托必须持引用**（`_snapProc`/`_connProc` 字段），否则 GC 后回调崩溃；`CameraHandle` 在 MVSDK.cs 中是**文件级 using 别名**，消费方须自行声明 `using CameraHandle = System.Int32;`。
7. **部署**：原生库已拷入 `3rdDepend/MecaVision/`（x64 四件套）；平台目标须显式 x64/x86（禁 AnyCPU）。

## 备选方案

- **方案 B（否决）**：按二手文档新建 `MonitorCamera/` 平行模块。否决原因：与 ADR-007（原 ADR-009，监控相机模块架构）冲突、产生两套监控相机体系、违反其「独立模块 + SDK 抽象」原则。
- **方案 C（否决）**：保留海康作为第二实现。否决原因：用户裁定删除，避免平行体系与依赖残留。

## 后果

### 正面
- 与运控、线激光三层心智完全一致；换厂商只动实现层目录。
- 官方 C# 封装原样复用（无需自写 DllImport）；`CameraGigeGetIp` 关闭了「枚举期无法按 IP 匹配」的 OPEN 项。
- 抽象层零实现依赖（静态校验通过）。

### 负面 / 遗留
- 消费方 `MonitorCameraWorkflow`（10 处）、`MonitorCamPage`（19 处）同步改名，属预期内改动。
- **真编译待 Visual Studio**（本环境无 C# 编译器）；已用 Python 静态校验（14/14 通过）替代。
- OPEN：① 平台目标与现场相机形态（GigE/USB3）待确认 ② 曝光/增益等参数接口尚未接入 ③ `MonitorCamConfig.Port` 字段麦格威不使用，保留仅为兼容历史 INI。

## 相关页面

- [[guides/MecaVision-DevGuide]] —— 开发指导与实施 plan
- [[api/MecaVisionMVSDK-Native]] —— 原生 API 速查
- [[modules/MonitorCam]]、[[api/MonitorCamManager]]、[[decisions/ADR-007-MonitorCameraModule]]
- [[decisions/ADR-034-LineLaserThreeLayerRefactor]]、[[decisions/ADR-017-EnumDeduplication]]
- [[decisions/ADR-038-EmguALGThreeLayer]] —— 配套的算法模块三层改造
