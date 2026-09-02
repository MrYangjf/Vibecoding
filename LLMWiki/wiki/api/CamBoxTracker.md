---
title: CamBoxTracker — CAMBOX 焊缝跟踪引擎
date: 2026-08-11
tags: [API, 运控, CAMBOX, 正运动, 硬件跟踪]
source: MotionControl/ZMotion/CamBoxTracker.cs
---

# CamBoxTracker — CAMBOX 焊缝跟踪引擎

> **所属模块**：[[modules/MotionControl]]
> **链路定位**：硬件级实时跟踪（PC 只写轨迹点，运动由硬件完成）
> **决策依据**：[[decisions/ADR-030-RSICamBoxTrackingArchitecture]]
> **架构设计**：[[architecture/DeviceControlArchitecture]]
> **核心职责**：管理 CAMBOX 电子凸轮的焊缝轨迹跟踪生命周期，包括轨迹点追加、前置补偿、启停控制、异常保护。
> **设计哲学**：PC 只写轨迹点，实时运动完全由硬件完成

---

## 概述

`CamBoxTracker` 是设备控制架构中运动控制链路的核心组件，封装了基于正运动控制器 CAMBOX 电子凸轮的焊缝实时跟踪功能。

与软件离散调整的根本区别：
- 软件离散调整：PC 每帧计算偏差 → `MoveAbsolute` 调整（软件驱动、抖动大）
- 当前架构：PC 将原始焊缝轨迹写入 CAMBOX → 硬件自动跟随（硬件驱动、零抖动）

**PC 端仅做三件事**：
1. 时序缓存 — 建立机器人位置+时间戳的环形缓冲
2. 插值对齐 — 激光帧时刻的机器人位置插值还原
3. 写入凸轮 — 经前置补偿后写入 CAMBOX 表

---

## 类定义

```csharp
namespace AdaWeldSystem.MotionControl.ZMotion
{
    public class CamBoxTracker : IDisposable
    {
        // 配置
        public CamBoxTrackingConfig Config { get; }
        
        // 状态
        public bool IsRunning { get; }
        public CamBoxTrackingState State { get; }
        
        // 统计
        public long TotalPointsAdded { get; }
        public long TotalPointsDiscarded { get; }
        public double CurrentMasterPosition { get; }
        public double CurrentSlavePosition { get; }
        
        // 事件
        public event EventHandler<CamBoxTrackingState> StateChanged;
        public event EventHandler<string> TrackingError;
        public event EventHandler<CamBoxPointEventArgs> PointAdded;
    }
}
```

---

## 配置（CamBoxTrackingConfig）

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `MasterAxisIndex` | int | 8 | 主轴轴号（ATYPE=25 通讯编码器轴） |
| `SlaveAxisIndex` | int | 0 | 从轴轴号（Y 纠偏伺服轴） |
| `CamIndex` | int | 0 | CAMBOX 通道号 |
| `LaserFrontOffset` | double | 50.0 | 激光前置距离（mm） |
| `MaxDeviation` | double | 5.0 | 最大纠偏量（mm），超偏丢弃 |
| `TableLength` | int | 10000 | 凸轮表长度（点数） |
| `Mode` | CamBoxMode | PositionFollow | 跟随模式（位置跟随 / 速度跟随） |
| `Direction` | CamBoxDirection | ForwardOnly | 跟随方向（仅正向 / 双向） |
| `BufferThreshold` | int | 10 | 缓冲阈值，低于此值触发低缓冲警告 |
| `LaserTimeoutMs` | int | 200 | 激光帧超时时间（ms），超时认为丢帧 |

---

## 状态枚举（CamBoxTrackingState）

| 枚举值 | 说明 |
|--------|------|
| `Idle` | 空闲，未启动 |
| `Initializing` | 初始化中（复位凸轮表、配置参数） |
| `WaitingForStart` | 等待启动信号（机器人开始运动） |
| `Tracking` | 正常跟踪中 |
| `Paused` | 暂停（激光丢帧等临时中断） |
| `Stopping` | 停止中 |
| `Error` | 异常状态（EtherCAT 断连、超偏超限等） |

---

## 公共方法

### Initialize — 初始化跟踪引擎

```csharp
public bool Initialize(CamBoxTrackingConfig config)
```

**功能**：
- 复位 CAMBOX 表
- 配置主轴/从轴映射
- 设置跟随模式和方向
- 初始化时序缓存

**返回**：初始化成功返回 `true`，失败返回 `false`

**前置条件**：正运动控制器已连接且 EtherCAT 通信正常

---

### Start — 启动跟踪

```csharp
public bool Start()
```

**功能**：
- 启动 CAMBOX 电子凸轮
- 状态迁移至 `WaitingForStart`
- 等待主轴开始运动后自动进入 `Tracking`

**返回**：启动成功返回 `true`

**前置条件**：`Initialize()` 已成功调用

---

### Stop — 停止跟踪

```csharp
public void Stop(bool immediate = false)
```

**参数**：
- `immediate`：`true` 立即停止（急停模式），`false` 平滑停止

**功能**：
- 停止 CAMBOX 电子凸轮
- 从轴保持当前位置（不回零、不突变）
- 状态迁移至 `Idle`（正常停止）或 `Error`（异常停止）

---

### AddTrajectoryPoint — 写入焊缝轨迹点

```csharp
public bool AddTrajectoryPoint(double masterPosition, double slaveOffset)
```

**参数**：
- `masterPosition`：主轴位置（已插值对齐 + 前置补偿后的 Cam_Key）
- `slaveOffset`：从轴偏移量（焊缝横向偏移 Y_offset）

**功能**：
- 超偏检查：`|slaveOffset| > MaxDeviation` 则丢弃
- 调用 `ZAux_CamBox_AddPoint` 写入 CAMBOX 表
- 统计加点数量

**返回**：写入成功返回 `true`，超偏或失败返回 `false`

> ⚠️ 此方法由 PC 端调用，是非实时的。实时跟随由 CAMBOX 硬件自动完成。

---

### AddTrajectoryPointWithTimestamp — 带时间戳写入（便捷方法）

```csharp
public bool AddTrajectoryPointWithTimestamp(
    double laserOffset, 
    DateTime laserTimestamp,
    RSIPositionBuffer positionBuffer)
```

**功能**：
- 从 `RSIPositionBuffer` 中插值获取激光采集时刻的主轴位置
- 自动加上前置距离补偿
- 调用 `AddTrajectoryPoint` 写入

**返回**：写入成功返回 `true`，插值失败或超偏返回 `false`

> 这是上层业务最常用的方法，封装了完整的"时间戳插值 + 前置补偿 + 写入"流程。

---

### Reset — 复位跟踪

```csharp
public void Reset()
```

**功能**：
- 清空凸轮表
- 复位统计计数器
- 状态回到 `Idle`

---

### UpdateStatus — 更新状态（周期调用）

```csharp
public void UpdateStatus()
```

**功能**：
- 读取当前主轴位置
- 读取当前从轴位置
- 检查激光帧超时
- 检查 EtherCAT 连接状态
- 状态机自动迁移

> 建议调用频率：10~100Hz（非实时，仅用于状态监控和异常检测）

---

## 事件

### StateChanged — 状态变更事件

```csharp
public event EventHandler<CamBoxTrackingState> StateChanged
```

跟踪状态发生变化时触发。参数为新状态。

---

### TrackingError — 跟踪错误事件

```csharp
public event EventHandler<string> TrackingError
```

发生跟踪异常时触发。参数为错误描述。

**可能的错误**：
- "EtherCAT communication lost"
- "Laser frame timeout"
- "Deviation exceeds maximum limit"
- "Cam table buffer low"

---

### PointAdded — 轨迹点添加事件

```csharp
public event EventHandler<CamBoxPointEventArgs> PointAdded
```

成功写入一个轨迹点时触发，用于调试和数据记录。

`CamBoxPointEventArgs` 包含：
- `MasterPosition`：主轴位置
- `SlaveOffset`：从轴偏移
- `Timestamp`：写入时间

---

## 异常保护逻辑

| 异常类型 | 检测方式 | 保护动作 | 恢复条件 |
|----------|---------|---------|---------|
| EtherCAT 断连 | 周期检查 ECAT 状态 | CAMBOX 停止，Y 轴锁止，进入 Error | 人工复位 |
| 激光丢帧 | `LaserTimeoutMs` 超时 | 停止加点，保持当前轨迹，进入 Paused | 收到新激光帧自动恢复 Tracking |
| 超偏 | `|slaveOffset| > MaxDeviation` | 丢弃当前点，统计丢弃数 | 偏差回落到范围内自动恢复 |
| 凸轮表低缓冲 | 剩余点数 < `BufferThreshold` | 触发警告事件，不停止 | 持续加点恢复缓冲 |
| 主轴停止 | 主轴位置长时间不变 | 保持当前从轴位置，不晃动 | 主轴恢复运动自动继续 |

---

## 与软件离散调整方案的差异

| 特性 | 软件离散调整（MoveControlData + MoveAbsolute） | CAMBOX 硬件跟随（CamBoxTracker） |
|------|--------------------------------------|---------------------|
| 驱动方式 | PC 软件驱动，每帧 MoveAbsolute | 硬件 CAMBOX 驱动，自动插值 |
| 实时性 | 10~20ms 周期，抖动大 | 硬件级，零抖动 |
| PC 角色 | 实时运动控制 + 数据处理 | 仅数据处理 + 轨迹写入 |
| 焊缝处理 | 平滑滤波（失真） | 原始数据（100% 保真） |
| 前置补偿 | 缓存键偏移（近似） | 时间戳插值 + Cam_Key 偏移（精确） |
| 异常保护 | 软件层，依赖 PC | 硬件层 + 软件监控 |
| 代码复杂度 | 高（状态机 + 缓存 + 插补） | 低（仅加点 + 状态监控） |

---

## 相关页面

- [[architecture/DeviceControlArchitecture]] — 设备控制架构规范页（第 10 章 运动控制）
- [[decisions/ADR-030-RSICamBoxTrackingArchitecture]] — RSI-CAMBOX 运动控制决策
- [[api/EncoderAxis]] — 通讯编码器轴（CAMBOX 主轴）
- [[api/ZMotionController]] — 正运动控制器
- [[api/RSIPositionBuffer]] — RSI 位置时间戳缓冲
- [[modules/MotionControl]] — MotionControl 模块
