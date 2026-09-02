---
title: LaserWeldHeadController API — 激光焊接头控制器
date: 2026-07-31
tags: [API, 激光焊接头, 控制器]
source: AdaWeldSystem/LaserWeldHead/ILaserWeldHeadController.cs
---

# LaserWeldHeadController API — 激光焊接头控制器

> 激光焊接头控制器，位于 `AdaWeldSystem.LaserWeldHead` 命名空间。

## 接口

### ILaserWeldHeadController

```csharp
public interface ILaserWeldHeadController : IDisposable
{
    bool IsInitialized { get; }
    bool IsLaserReady { get; }
    LaserHeadTemperatureData CurrentTemperature { get; }
    SafetyIOStatus CurrentSafetyIO { get; }
    AutoFocusPositionData CurrentAutoFocusPosition { get; }

    event EventHandler<LaserHeadTemperatureData> TemperatureAlarm;
    event EventHandler<SafetyIOStatus> SafetyIOAlarm;
    event EventHandler<AutoFocusPositionData> AutoFocusPositionChanged;

    bool Initialize();
    void Shutdown();
    LaserHeadTemperatureData ReadTemperature();
    bool SetAutoFocusPosition(double position);
    bool SetWireFeedPosition(double position, double torqueLimit);
    bool EnableLaser();
    bool DisableLaser();
    SafetyIOStatus ReadSafetyIO();
    bool StartWorking();
    void StopWorking();
}
```

| 成员 | 说明 |
|------|------|
| `IsInitialized` | 是否已初始化 |
| `IsLaserReady` | 激光器是否就绪 |
| `CurrentTemperature` | 当前温度数据（`LaserHeadTemperatureData`） |
| `CurrentSafetyIO` | 当前安全 IO 状态（`SafetyIOStatus`） |
| `CurrentAutoFocusPosition` | 当前自动对焦位置数据（`AutoFocusPositionData`） |
| `TemperatureAlarm` | 温度超阈报警事件（`EventHandler<LaserHeadTemperatureData>`） |
| `SafetyIOAlarm` | 安全 IO 触发报警事件（`EventHandler<SafetyIOStatus>`） |
| `AutoFocusPositionChanged` | 自动对焦位置变更事件（`EventHandler<AutoFocusPositionData>`） |
| `Initialize()` | 初始化：激光器握手 → 温度模块枚举 → IO 映射 → 启动温度轮询 |
| `StartWorking()` | 启动焊接头工作（Standby → Working），启用激光器 |
| `StopWorking()` | 停止焊接头工作（Working → Standby），关闭激光器 |
| `Shutdown()` | 关闭：停止轮询 → 关闭激光器 → 状态机 Reset |
| `ReadTemperature()` | 读取温度数据，返回 `LaserHeadTemperatureData` |
| `ReadSafetyIO()` | 读取安全 IO 状态，返回 `SafetyIOStatus` |
| `SetAutoFocusPosition(pos)` | 设置自动对焦电机位置 |
| `SetWireFeedPosition(pos, torqueLimit)` | 设置送丝电机位置（力矩控制模式） |
| `EnableLaser()` | 打开激光器（允许出光） |
| `DisableLaser()` | 关闭激光器 |

## 数据模型

### LaserWeldHeadConfig

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `LaserComPort` | COM1 | 激光器通讯端口 |
| `LaserBaudRate` | 115200 | 激光器波特率 |
| `TemperaturePollIntervalMs` | 1000 | 温度采集间隔（ms） |
| `CollimatorTempThreshold` | 60.0 | 准直镜温度阈值（°C） |
| `FocusLensTempThreshold` | 60.0 | 聚焦镜温度阈值（°C） |
| `ProtectionLensTempThreshold` | 80.0 | 保护镜温度阈值（°C） |
| `QBHInterfaceTempThreshold` | 70.0 | QBH 接口温度阈值（°C） |
| `AutoFocusMaxTravel` | 50.0 | 自动对焦电机最大行程（mm） |
| `WireFeedTorqueLimit` | 5.0 | 送丝电机力矩限制（N·m） |

### LaserHeadTemperatureData

| 属性 | 类型 | 说明 |
|------|------|------|
| `CollimatorTemp` | `double` | 准直镜温度（°C） |
| `FocusLensTemp` | `double` | 聚焦镜温度（°C） |
| `ProtectionLensTemp` | `double` | 保护镜温度（°C） |
| `QBHInterfaceTemp` | `double` | QBH 接口温度（°C） |
| `IsOverThreshold` | `bool` | 是否超阈值 |
| `OverThresholdLens` | `string` | 超阈值镜片名称 |
| `Timestamp` | `DateTime` | 采集时间戳 |

### SafetyIOStatus

| 属性 | 类型 | 说明 |
|------|------|------|
| `EmergencyStop` | `bool` | 急停信号 |
| `SafetyDoor` | `bool` | 安全门信号 |
| `Interlock` | `bool` | 互锁信号 |
| `Timestamp` | `DateTime` | 采集时间戳 |

### AutoFocusPositionData

| 属性 | 类型 | 说明 |
|------|------|------|
| `AutoFocusPos` | `double` | 自动对焦电机位置（mm） |
| `WireFeedPos` | `double` | 送丝电机位置（mm） |
| `WireFeedTorque` | `double` | 送丝电机力矩（N·m） |
| `Timestamp` | `DateTime` | 更新时间戳 |

## 相关页面

- [[modules/LaserWeldHead]] — 激光焊接头模块
- [[modules/DeviceControl]] — 设备状态机 API
- [[modules/DeviceControl]] — 设备状态机模块

---

*来源：AdaWeldSystem/LaserWeldHead/ILaserWeldHeadController.cs*