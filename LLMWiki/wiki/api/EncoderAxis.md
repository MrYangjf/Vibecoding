---
title: EncoderAxis — 通讯编码器轴（ATYPE=25）
date: 2026-08-11
tags: [API, 运控, 正运动, 编码器, EtherCAT]
source: MotionControl/ZMotion/EncoderAxis.cs
---

# EncoderAxis — 通讯编码器轴（ATYPE=25）

> **所属模块**：[[modules/MotionControl]]
> **链路定位**：硬件级实时跟踪主轴（CAMBOX 电子凸轮主轴源）
> **决策依据**：[[decisions/ADR-023-RSICamBoxTrackingArchitecture]]
> **架构设计**：[[architecture/DeviceControlArchitecture]]
> **核心用途**：作为 CAMBOX 电子凸轮的主轴，接收 KUKA 机器人 EtherCAT PDO 推送的 ToolRelX 位置
> **本质**：不跑电机、不输出脉冲，完全由 EtherCAT 总线硬件周期刷新 MPOS 的虚拟编码器轴

---

## 概述

`EncoderAxis` 封装了正运动控制器 **ATYPE=25（EtherCAT 通讯编码器轴）** 的配置与读取接口。

在设备控制架构中，该轴承担 **CAMBOX 电子凸轮主轴** 的关键角色：

```
KUKA RSI FastIPO → EtherCAT PDO → ATYPE=25 轴 MPOS → CAMBOX 主轴 → Y 从轴纠偏
                          （硬件自动刷新）        （硬件插值）
```

**为什么用 ATYPE=25 而不是虚拟轴？**
- 虚拟轴（ATYPE=0 + 软件设置 MPOS）有软件延迟和抖动
- ATYPE=25 由 EtherCAT 硬件直接刷新 MPOS，零延迟、零抖动
- 完全等效物理光栅主轴，可直接接入 CAMBOX

---

## 类定义

```csharp
namespace AdaWeldSystem.MotionControl.ZMotion
{
    public class EncoderAxis
    {
        // 属性
        public int AxisIndex { get; }
        public string Name { get; }
        public double CurrentPosition { get; }
        public double Units { get; }
        public bool IsConnected { get; }
        public EncoderSourceType SourceType { get; }
        
        // 事件
        public event EventHandler<PositionUpdatedEventArgs> PositionUpdated;
    }
}
```

---

## 枚举

### EncoderSourceType — 编码器来源类型

| 枚举值 | 说明 |
|--------|------|
| `EtherCATPDO` | EtherCAT PDO 通讯编码器（默认，ATYPE=25） |
| `PulseInput` | 脉冲输入编码器（物理光栅尺） |
| `SSI` | SSI 绝对编码器 |
| `EnDat` | EnDat 绝对编码器 |

---

## 配置（EncoderAxisConfig）

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `AxisIndex` | int | 8 | 轴号（建议使用 8 及以上，避开物理伺服轴） |
| `Name` | string | "通讯编码器主轴" | 轴名称 |
| `SourceType` | EncoderSourceType | EtherCATPDO | 编码器来源类型 |
| `Units` | double | 1.0 | 脉冲当量（units/mm），与机器人单位对齐 |
| `EtherCATSlaveIndex` | int | 1 | EtherCAT 从站索引（机器人 = 从站 1） |
| `PDOEntryIndex` | int | 0 | PDO 数据项索引（ToolRelX 在 PDO 中的位置） |
| `DataSize` | int | 32 | 数据位数（32 = REAL32 / float） |
| `Direction` | int | 1 | 计数方向（1 正向 / -1 反向） |

---

## 公共方法

### Initialize — 初始化通讯编码器轴

```csharp
public bool Initialize(EncoderAxisConfig config, IntPtr controllerHandle)
```

**功能**：
- 设置 `ATYPE = 25`（EtherCAT 通讯编码器模式）
- 配置 `UNITS` 脉冲当量
- 配置 EtherCAT PDO 映射
- 设置计数方向
- 清零当前位置

**参数**：
- `config`：编码器轴配置
- `controllerHandle`：正运动控制器句柄（`ZMotionNative` 内部使用）

**返回**：初始化成功返回 `true`

**前置条件**：
- 正运动控制器已连接
- EtherCAT 总线已扫描，从站已配置

---

### GetCurrentPosition — 读取当前位置

```csharp
public double GetCurrentPosition()
```

**功能**：读取当前编码器轴位置（MPOS），单位由 `Units` 决定。

**返回**：当前主轴位置（mm）

> ⚠️ 此方法为软件读取，用于状态监控和调试。实时跟随由 CAMBOX 硬件直接访问 MPOS，不走软件路径。

---

### SetPosition — 设置当前位置

```csharp
public void SetPosition(double position)
```

**功能**：设置当前编码器轴位置（清零或设置初始值）。

**参数**：
- `position`：要设置的位置值

**使用场景**：
- 焊接开始前清零：`SetPosition(0)`
- 设置参考位置：与机器人 Tool 坐标系对齐

> ⚠️ 仅在 CAMBOX 未启动时调用。跟踪运行中修改位置会导致从轴突变。

---

### Reset — 复位轴

```csharp
public void Reset()
```

**功能**：
- 清零当前位置
- 复位轴状态

---

### UpdateStatus — 更新状态（周期调用）

```csharp
public void UpdateStatus()
```

**功能**：
- 读取当前位置到缓存
- 检查 EtherCAT 连接状态
- 触发 `PositionUpdated` 事件（如果位置有变化）

> 建议调用频率：10~50Hz（非实时，仅用于 UI 显示和状态监控）

---

## 事件

### PositionUpdated — 位置更新事件

```csharp
public event EventHandler<PositionUpdatedEventArgs> PositionUpdated
```

位置有变化时触发（由 `UpdateStatus()` 检测）。

`PositionUpdatedEventArgs` 包含：
- `Position`：当前位置
- `Delta`：位置变化量
- `Timestamp`：更新时间戳

> 此事件用于 UI 显示和数据记录，不应用于实时控制。实时跟随由 CAMBOX 硬件完成。

---

## 与 CAMBOX 的配合

### 作为 CAMBOX 主轴

```
CamBoxTracker 初始化时：
  CAMBOX_MASTER(camIndex, encoderAxis.AxisIndex)
  CAMBOX_MODE(camIndex, PositionFollow)
  CAMBOX_START(camIndex)
```

### 位置同步机制

1. KUKA 机器人每 4ms 通过 EtherCAT PDO 推送 ToolRelX
2. 正运动 EtherCAT 主站硬件接收 PDO 数据
3. **ATYPE=25 轴 MPOS 自动刷新**（硬件级，零延迟）
4. CAMBOX 以该轴为主轴，硬件查表插值驱动从轴

整个过程 **完全不经过 PC 软件**，也不经过控制器 CPU 处理，全部在总线硬件层完成。

---

## 注意事项

### 1. 轴号选择

- 建议使用 8 及以上轴号，避开物理伺服轴（0~3）
- 正运动控制器最大支持轴数取决于型号（如 ZMC432 支持 32 轴）
- ATYPE=25 的轴不占用脉冲输出通道

### 2. Units 对齐

- `Units` 必须与机器人 ToolRelX 的单位一致（mm）
- 建议设置为 `1.0`（1 unit = 1 mm）
- 单位不一致会导致凸轮表位置映射错误

### 3. 清零时机

- 必须在 CAMBOX 启动 **之前** 清零
- 焊接开始前，机器人到达起始位置时执行清零
- 跟踪运行中禁止清零，会导致从轴突变

### 4. EtherCAT 依赖

- ATYPE=25 完全依赖 EtherCAT 通信
- EtherCAT 断连时，轴位置保持最后值，不会归零
- 断连检测由 `CamBoxTracker` 的异常保护逻辑处理

---

## 相关页面

- [[architecture/DeviceControlArchitecture]] — 设备控制架构规范页（第 10 章 运动控制）
- [[decisions/ADR-023-RSICamBoxTrackingArchitecture]] — RSI-CAMBOX 运动控制决策
- [[api/CamBoxTracker]] — CAMBOX 跟踪引擎（使用编码器轴作为主轴）
- [[api/ZMotionController]] — 正运动控制器
- [[api/KUKARobot]] — KUKA 机器人管理器（RSI FastIPO）
- [[modules/MotionControl]] — MotionControl 模块
