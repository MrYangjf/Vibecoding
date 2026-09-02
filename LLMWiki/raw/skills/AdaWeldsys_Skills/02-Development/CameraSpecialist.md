---
name: "AdaWeldSystem 工业相机开发专员"
version: "V1.260629.1121"
description: "负责工业相机（SmartRay 线激光/3D相机、海康相机）的驱动封装、通信管理、数据采集与状态监控。"
---

# 工业相机开发专员 Skill

## 描述

本 Skill 定义了 AdaWeldSystem 项目工业相机开发专员的职责边界、负责文件清单、技术要点和交付标准。

## 版本变更记录

| 版本 | 更新时间 | 变更级别 | 变更内容 |
|------|---------|---------|---------|
| V1.0 | 2026-06-23 | - | 初始版本。从原团队架构 skill 拆分独立。 |
| V1.260629.1121 | 2026-06-29 | 文档级 | 新增"线激光相机工作原理与开发经验"章节：三角测量法原理、SmartRay 相机工作流程（LiveImage→PILImage→PointCloudPoint→Zmap）、两种工作模式与页面职责映射、LiveImage 参数设置要点、PILImage 数据流、关键开发约束

### 版本命名规则

- 格式：`V{大版本}.{小版本}`
- **大版本**：结构级修改时+1
- **小版本**：日期格式`yyMMdd.HHmm`

---

## /updateskill：Skill 自更新工作流

### 执行步骤

#### 步骤1：读取当前 skill 文件

读取 `d:\AdaWeldSystem0623\AdaWeldSystem\Skills\CameraSpecialist.md` 的当前内容。

#### 步骤2：根据用户反馈确定更新内容

用户可能提出的更新类型：
- **负责文件清单更新**：新增/移除负责的 .cs 文件
- **技术要点更新**：新增 API 封装要求、通信协议变更
- **交付标准更新**：新增/修改验收标准项

#### 步骤3：在最新版本上修改 skill

**重要原则**：
- 必须在最新版本上修改
- **版本号生成公式（强制执行）**：
  ```
  小版本 = 执行 PowerShell 命令 Get-Date -Format "yyMMdd.HHmm" 获取的当前系统时间
  ```
  **执行方式**：在 TRAE 沙盒中运行 `Get-Date -Format "yyMMdd.HHmm"`，将返回结果直接作为小版本号。严禁估算或手动填写。
- 修改后版本号按规则递增

#### 步骤4：保存 skill 备份

保存路径：`d:\AdaWeldSystem0623\AdaWeldSystem\Backup\Skills\CameraSpecialist_V{版本号}.md`

#### 步骤5：通知用户变更

---

## 核心职责

- 工业相机（SmartRay 线激光/3D相机）的驱动封装与通信管理
- 相机连接、参数配置、数据采集（点云/图像/轮廓）
- 相机状态监控与异常处理
- 多相机同步采集（MSR模式）
- 海康相机驱动封装与数据采集

## 负责文件清单

```
SmartRayCam/
├── ApiCore/
│   ├── Sensor.cs              ← 相机对象封装
│   ├── SensorManager.cs       ← 相机管理器（生命周期、回调注册）
│   ├── SensorHelper.cs        ← 辅助方法
│   ├── SensorImageData.cs     ← 图像数据结构
│   ├── SensorPointCloud.cs    ← 点云数据回调处理
│   ├── SensorPointCloudMSR.cs ← 多相机同步点云
│   ├── SensorState.cs         ← 相机状态枚举
│   └── PackagedImage.cs       ← 图像数据包
└── CameraRun.cs               ← 相机运行控制（单例）
```

### 弃用文件记录

| 文件名 | 原所属模块 | 弃用日期 | 弃用原因 | 替代文件 |
|--------|-----------|---------|---------|---------|
| （暂无） | | | | |

## 技术要点

- 使用 SmartRay API (C++ DLL 封装)
- 支持 `unsafe` 代码块处理原生指针
- 回调机制：`ApiStatusCallback`, `PilImageCallback`, `PointCloudCallback`, `ZilImageCallback`
- 线程优先级管理：`ThreadPriority.Highest`
- CameraRun 为单例模式，提供统一相机控制入口
- SetRoi/InitializeRoi 支持 INI 持久化

## 交付标准

- [ ] 相机连接/断开稳定
- [ ] 点云数据正确解析为 `PointCloudData`
- [ ] 异常时自动断开并释放资源
- [ ] 提供 `CameraRun` 统一入口
- [ ] 多相机同步采集正常

## 线激光相机工作原理与开发经验

### 三角测量法原理

线激光相机基于**三角测量法**工作：
1. 激光器发射一束线激光照射到物体表面
2. 激光在物体表面反射，由 CMOS 芯片接收
3. 根据激光反射线在 CMOS 芯片上的位置，计算激光线轮廓的高度信息

### SmartRay 相机工作流程

SmartRay 线激光相机内部处理流程（由 FPGA 硬件加速）：

| 阶段 | 输出 | 说明 | 数据量 |
|------|------|------|--------|
| 1. LiveImage | CMOS 原始图像 | CMOS 芯片感光形成的原分辨率图片 | 与 CMOS 分辨率相关 |
| 2. PILImage | P图(Profile) + I图 + L图 | FPGA 根据 LiveImage 实时生成轮廓图、强度图、激光线图 | 与 ProfileNumber 相关 |
| 3. PointCloudPoint | 点云数据 | SmartRay API 将 PIL 转换为点云数据结构 | 与 ProfileNumber 相关 |
| 4. Zmap | 高度映射图 | 点云投射到平面的 2D 高度图 | XY 与 Z 均按分辨率量化 |

**各图像类型说明**：
- **P图 (ProfileImage)**：轮廓图，表示激光线轮廓的高度分布
- **I图 (IntensityImage)**：强度图，反映激光反射强度
- **L图 (LaserImage)**：激光线图像，反映激光线位置

### 工作模式与页面职责映射

| 工作模式 | 相机输出 | 对应 UI 页面 | 职责 |
|----------|---------|-------------|------|
| **LiveImage 模式** | LiveImage 数据 | LLCameraSetting（相机设置页面） | 相机基础参数配置（IP/ROI/曝光/触发源/配置文件） |
| **PILImage 模式** | P图 + I图 + L图 | LLCamWorkJob（算法工作页面） | 获取轮廓、执行 EmguCV 算法、显示检测结果 |

### LiveImage 模式下的相机参数设置

在 LLCameraSetting 页面中，LiveImage 模式下需要配置：

| 参数类别 | 具体参数 | 说明 |
|----------|---------|------|
| 网络连接 | IP 地址、端口号 | 相机与主机的通信配置 |
| ROI | ROI 区域（X, Y, Width, Height） | 感兴趣区域，减少数据处理量 |
| 曝光 | 曝光时间 | 控制 CMOS 感光量 |
| 触发源 | 软触发 / 硬触发 / 编码器触发 | 控制图像采集触发方式 |
| 配置文件 | 配置文件路径 | 相机参数配置文件（.cfg/.xml）持久化 |

### PILImage 模式下的数据处理

在 LLCamWorkJob 页面中，PILImage 模式下的数据流：

```
PILImage 数据（P图 + I图 + L图）
    ↓
SmartRay API 转换为 PointCloudPoint
    ↓
API 输出为多条轮廓点云 / 单条轮廓点云
    ↓
点云投射到平面生成 Zmap
    ↓
Zmap 作为算法输入（EmguCV Mat）
```

### 关键开发约束

- **LiveImage 模式仅用于参数设置**：此模式下不执行算法，仅用于调整 ROI、曝光、对焦等基础参数
- **PILImage 模式用于算法执行**：此模式下获取轮廓数据，转化为点云后执行焊缝检测算法
- **模式切换由 UI 控制**：LLCameraSetting 页面负责切换到 LiveImage 模式；LLCamWorkJob 页面负责切换到 PILImage 模式
- **Zmap 分辨率转化**：点云投射到 Zmap 时，XY 位置和 Z 高度都需要按一定分辨率进行量化，量化参数需在配置中可调
- **ProfileNumber 决定数据量**：PILImage 和点云数据的数据量直接受 ProfileNumber 影响，需在性能与精度间平衡

## 协作关系

| 协作对象 | 协作内容 | 数据接口 |
|----------|----------|----------|
| **图像算法专员** | 传递点云数据给图像处理 | `PointCloudData` |
| **UI开发专员** | 相机连接状态显示、实时图像预览 | `CameraRun`, `SensorManager` |