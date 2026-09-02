---
name: "AdaWeldSystem 运动控制开发专员"
version: "V1.260623.1711"
description: "负责雷赛控制卡运动控制API封装、焊缝跟踪算法结果引导运动轴移动、自动对焦算法结果引导Z轴移动、设备运行流程控制。"
---

# 运动控制开发专员 Skill

## 描述

本 Skill 定义了 AdaWeldSystem 项目运动控制开发专员的职责边界、负责文件清单、技术要点和交付标准。

## 版本变更记录

| 版本 | 更新时间 | 变更级别 | 变更内容 |
|------|---------|---------|---------|
| V1.0 | 2026-06-23 | - | 初始版本。从原团队架构 skill 拆分独立。 |

### 版本命名规则

- 格式：`V{大版本}.{小版本}`
- **大版本**：结构级修改时+1
- **小版本**：日期格式`yyMMdd.HHmm`

---

## /updateskill：Skill 自更新工作流

### 执行步骤

#### 步骤1：读取当前 skill 文件

读取 `d:\AdaWeldSystem0623\AdaWeldSystem\Skills\MotionControlSpecialist.md` 的当前内容。

#### 步骤2：根据用户反馈确定更新内容

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

保存路径：`d:\AdaWeldSystem0623\AdaWeldSystem\Backup\Skills\MotionControlSpecialist_V{版本号}.md`

#### 步骤5：通知用户变更

---

## 核心职责

- 雷赛控制卡（Leadshine）运动控制API封装与轴管理
- 焊缝跟踪算法结果引导XY运动轴移动
- 自动对焦算法结果引导Z轴移动
- 设备运行流程控制与状态机管理
- 轴参数配置与持久化（INI文件）
- 运动控制安全机制（软限位、急停、报警处理）

## 负责文件清单

```
MotionControl/
├── MotionController.cs        ← 运动控制器主类（单例模式）
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
```

## 技术要点

- 单例模式: `MotionController.Instance` 全局访问
- 雷赛控制卡API封装: 所有P/Invoke调用封装在 `MotionController` 中
- 轴控制参数: `AxisParameter` 结构体定义脉冲当量、速度、加速度、软限位等
- 设备状态枚举: `DeviceRunningState`（Uninitialized/Initializing/Ready/Running/Paused/Alarm/EmergencyStop/Homing/ShuttingDown）
- 轴状态枚举: `AxisState`（Disabled/Standby/Moving/Homing/Alarm/PositiveLimit/NegativeLimit/HomeDone）
- 状态机模式: `DeviceStateMachine` 管理设备整体运行流程，定义合法状态转移矩阵
- 运动控制事件: `MotionCompletedEventArgs`, `DeviceStateChangedEventArgs`（类级字段复用）
- 安全机制: 软限位检查、急停处理、报警状态管理
- 配置持久化: `MotionConfig` 使用 `FileOperate.INIFile` 保存轴参数

### 处理流程

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  焊缝算法结果    │ ──▶ │  运动控制器      │ ──▶ │  XY轴移动       │
│  (X/Y偏移量)    │     │  TrackSeamPos   │     │  焊缝跟踪       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
┌─────────────────┐     ┌─────┴───────────┐     ┌─────────────────┐
│  对焦算法结果    │ ──▶ │  运动控制器      │ ──▶ │  Z轴移动        │
│  (Z偏移量)      │     │  AdjustFocus    │     │  自动对焦       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  设备状态机      │
                       │  StateMachine   │
                       └─────────────────┘
```

## 交付标准

- [ ] 雷赛控制卡API封装完整，业务层不直接调用P/Invoke
- [ ] 轴使能/禁用/回零功能正常
- [ ] 绝对/相对定位运动精度 ±0.01mm
- [ ] 多轴直线插补运动流畅
- [ ] 软限位检查生效，超限运动被阻止
- [ ] 急停响应时间 < 50ms
- [ ] 设备状态机状态转移合法，无非法跳转
- [ ] 轴参数可保存/加载，断电不丢失
- [ ] 焊缝跟踪响应延迟 < 100ms
- [ ] 自动对焦精度 ±0.05mm

## 协作关系

| 协作对象 | 协作内容 | 数据接口 |
|----------|----------|----------|
| **图像算法专员** | 接收焊缝跟踪偏移量（X/Y方向） | `SeamFeatureResult.CenterX/CenterY` |
| **3D开发专员** | 接收自动对焦Z轴偏移量 | `PointCloudData` (Z轴高度数据) |
| **焊接工艺专员** | 接收焊接参数（功率/速度） | `WeldProcess.LaserWeldData` |
| **UI开发专员** | 运动控制状态显示、轴参数配置界面 | `MotionController.Instance`, `DeviceStateMachine` |
| **通用技术专员** | 全局状态同步、急停信号 | `GlobalCommData`, `SystemStatus` |