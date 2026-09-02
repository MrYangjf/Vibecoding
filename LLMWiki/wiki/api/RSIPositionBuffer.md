---
title: RSIPositionBuffer — RSI 位置时间戳环形缓冲
date: 2026-08-11
tags: [API, 运控, RSI, 时间戳, 插值]
source: MotionControl/ZMotion/RSIPositionBuffer.cs
---

# RSIPositionBuffer — RSI 位置时间戳环形缓冲

> **所属模块**：[[modules/MotionControl]]
> **链路定位**：硬件级实时跟踪的时序对齐组件
> **决策依据**：[[decisions/ADR-030-RSICamBoxTrackingArchitecture]]
> **架构设计**：[[architecture/DeviceControlArchitecture]]
> **核心用途**：缓存 KUKA RSI 推送的位置+时间戳序列，为激光帧提供时间戳插值对齐
> **设计哲学**：解决"激光采集时刻、机器人 PDO 时刻、网络接收时刻全部不对齐"的根本问题

---

## 概述

`RSIPositionBuffer` 是一个**固定大小的环形缓冲区**，存储 KUKA RSI 通过 EtherCAT PDO 推送的「位置 + 高精度时间戳」序列。

线激光传感器输出的焊缝偏移数据带有自身的硬件采集时间戳。通过在环形缓冲中查找该时间戳前后两个 RSI 数据点，进行**线性插值**，可以精确还原出激光真实采集时刻的机器人主轴位置。

**这是运动控制链路精度的基石**——彻底消除传输延迟误差。

---

## 为什么需要时间戳插值

### 问题：三处时间全部不对齐

```
T_robot:    t1 ───── t2 ───── t3 ───── t4 ─────    （机器人 PDO 发送时刻）
T_network:     t1' ──── t2' ──── t3' ──── t4' ─    （PC 接收时刻，有网络延迟）
T_laser:           t_laser                          （激光采集时刻）
```

- **机器人 PDO 周期**：4ms 一次，但激光采集是独立时钟
- **网络延迟**：EtherCAT 有传输延迟，PC 收到时已经滞后
- **不同时钟源**：机器人时钟和激光传感器时钟可能有偏移和漂移

### 错误做法（时间戳直读）

```
PC 收到激光帧 → 立即读取机器人位置 → 直接使用
```

问题：读取到的是"PC 收到激光帧时的机器人位置"，不是"激光采集时的机器人位置"。
误差 = 网络延迟 + 系统调度延迟 = 几 ms 到几十 ms 不等。

### 正确做法（时间戳插值对齐）

```
1. RSI 每帧带硬件时间戳，存入环形缓冲
2. 激光帧带硬件时间戳
3. 在环形缓冲中插值找到 t_laser 对应的精确位置
4. 得到的是激光真实采集时刻的机器人位置
```

精度取决于插值算法和时间戳分辨率，典型误差 < 0.01mm。

---

## 类定义

```csharp
namespace AdaWeldSystem.MotionControl.ZMotion
{
    public class RSIPositionBuffer : IDisposable
    {
        // 属性
        public int Capacity { get; }
        public int Count { get; }
        public bool IsFull { get; }
        
        // 最新数据（快速访问）
        public double LatestPosition { get; }
        public long LatestTimestamp { get; }
        
        // 统计
        public long TotalSamples { get; }
        public int InterpolationHitCount { get; }
        public int InterpolationMissCount { get; }
    }
}
```

---

## 数据结构

### PositionSample — 位置采样点

```csharp
public struct PositionSample
{
    public long Timestamp;      // 高精度时间戳（微秒）
    public double Position;     // 主轴位置（mm）
    public double Velocity;     // 瞬时速度（mm/s，可选）
}
```

**时间戳来源**：
- 机器人端：RSI FastIPO 硬件时间戳（UINT32，微秒或毫秒，需配置）
- 激光端：传感器硬件采集时间戳
- 统一转为微秒级 long 存储，避免回绕问题

---

## 公共方法

### AddSample — 添加位置采样

```csharp
public void AddSample(long timestamp, double position, double velocity = 0)
```

**功能**：向环形缓冲添加一个位置采样点。

**参数**：
- `timestamp`：时间戳（微秒）
- `position`：主轴位置（mm）
- `velocity`：瞬时速度（mm/s，可选，用于速度补偿插值）

**行为**：
- 缓冲区未满：直接追加
- 缓冲区已满：覆盖最旧的数据
- 保持时间戳严格递增（乱序数据会被丢弃并记录警告）

---

### InterpolatePosition — 插值获取指定时刻的位置

```csharp
public bool InterpolatePosition(long targetTimestamp, out double position)
```

**功能**：根据目标时间戳，在缓冲中插值计算对应的主轴位置。

**参数**：
- `targetTimestamp`：目标时间戳（微秒，即激光采集时刻）
- `position`：输出，插值得到的位置（mm）

**返回**：插值成功返回 `true`，失败返回 `false`

**插值算法**：线性插值

```
找到 t1 <= targetTimestamp <= t2 的两个采样点
position = p1 + (p2 - p1) * (targetTimestamp - t1) / (t2 - t1)
```

**失败条件**：
- 缓冲区数据不足 2 个点
- 目标时间戳在缓冲范围之外（太旧或太新）
- 时间戳回绕导致无法确定先后关系

---

### InterpolateWithVelocity — 带速度补偿的插值

```csharp
public bool InterpolateWithVelocity(long targetTimestamp, out double position)
```

**功能**：使用速度信息进行更精确的插值（考虑加减速变化）。

**算法**：基于两点位置和速度的 Hermite 插值（如果速度数据可用）。

> 对于机器人匀速进给场景，线性插值已足够精确。此方法用于高精度或速度变化大的场景。

---

### Clear — 清空缓冲区

```csharp
public void Clear()
```

**功能**：清空所有采样数据，重置统计计数。

**使用场景**：焊接开始前清零、重新开始跟踪时。

---

### GetLatestSample — 获取最新采样

```csharp
public PositionSample GetLatestSample()
```

**功能**：获取缓冲区中最新的一个采样点。

**返回**：最新采样点。如果缓冲区为空，返回默认值（timestamp=0, position=0）。

---

### GetSampleCountInRange — 获取时间范围内采样数

```csharp
public int GetSampleCountInRange(long startTime, long endTime)
```

**功能**：统计指定时间范围内的采样点数量，用于诊断数据密度。

---

## 环形缓冲设计

### 容量选择

默认容量：**250 个采样点**

计算依据：
- RSI PDO 周期：4ms → 250 Hz
- 250 个点 = 1 秒的数据
- 激光帧延迟通常 < 100ms，1 秒缓冲绰绰有余
- 极端网络拥塞下也能保证有足够数据插值

可配置范围：50 ~ 1000。

### 时间戳回绕处理

机器人时间戳可能为 UINT32，约 70 分钟回绕一次。

处理策略：
- 内部存储为 long（64位），检测到回绕时自动扩展高位
- 检测方法：新时间戳远小于上次时间戳（差值 > 最大周期的100倍）
- 回绕时不丢数据，保持时间线连续

---

## 精度评估

### 影响精度的因素

| 因素 | 典型值 | 对精度的影响 |
|------|--------|-------------|
| RSI 周期 | 4ms | 插值间隔 4mm（假设速度 1m/s） |
| 时间戳分辨率 | 1μs | 可忽略 |
| 插值算法误差 | 线性 vs 实际 | < 0.1%（匀速进给时） |
| 时钟偏移 | 机器人 vs 激光 | 需校准，否则产生系统偏差 |

### 典型精度

假设机器人进给速度 1 m/s（1000 mm/s）：

| 插值方式 | 位置误差 |
|----------|---------|
| 无插值（最近点） | ±2.0 mm 峰值 |
| 线性插值（默认） | < 0.01 mm 典型 |
| Hermite 插值（带速度） | < 0.005 mm |

> 线性插值在匀速进给场景下已足够，因为机器人焊接进给通常是匀速直线运动。

---

## 与其他组件的协作

```
RSICommunication（KUKARobot 模块）
    │ OnRSIDataReceived（每 4ms）
    ▼
RSIPositionBuffer.AddSample(timestamp, position)
    ▲
    │ InterpolatePosition(laserTimestamp)
    │
CamBoxTracker.AddTrajectoryPointWithTimestamp()
    │
    ├── 从 RSIPositionBuffer 插值得到 S_meas
    ├── 前置补偿：Cam_Key = S_meas + LaserFrontOffset
    └── ZAux_CamBox_AddPoint(Cam_Key, Y_offset)
```

---

## 相关页面

- [[architecture/DeviceControlArchitecture]] — 设备控制架构规范页（第 10 章 运动控制）
- [[decisions/ADR-030-RSICamBoxTrackingArchitecture]] — RSI-CAMBOX 运动控制决策
- [[api/CamBoxTracker]] — CAMBOX 跟踪引擎（使用本缓冲进行插值对齐）
- [[api/EncoderAxis]] — 通讯编码器轴（CAMBOX 主轴）
- [[api/KUKARobot]] — KUKA 机器人管理器（RSI 数据源）
- [[modules/MotionControl]] — MotionControl 模块
