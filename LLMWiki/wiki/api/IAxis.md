---
title: IAxis API — 运动轴接口
date: 2026-08-04
tags: [API, 运控, 轴, 接口]
source: AdaWeldSystem/MotionControl/IAxis.cs
---

# IAxis API — 运动轴接口

> 定义单轴运动控制的基本操作，由具体硬件实现（伺服/步进/直线电机）。
> 位于 `AdaWeldSystem.MotionControl` 命名空间。

## 接口定义

```csharp
public interface IAxis
{
    string AxisName { get; }
    ushort AxisNumber { get; set; }
    double CurrentPosition { get; }
    bool IsMoving { get; }
    bool IsServoOn { get; }
    bool IsConnected { get; }
    event EventHandler Stopped;

    bool MoveTo(double positionMm, double speed = 10.0);
    void MoveToNoBlock(double positionMm, double speed = 10.0);
    bool MoveRelative(double deltaMm, double speed = 10.0);
    void Stop(bool immediate = false);
    bool ServoOn();
    bool ServoOff();
    bool Home();
    void JogMove(bool direction, double speed = 10.0);
    void SetHomePosition();
    bool WaitMoveDone(int timeoutMs = 0);
}
```

## 默认实现

| 类 | 说明 |
|----|------|
| `ZMotionAxis` | 正运动轴实现（`IAxis`），由 `ZMotionController` 初始化时按 `MotionConfig` 轴字典创建；`NullAxis` 空实现已随 [[decisions/ADR-037-DefaultInitZMotion]] 删除 |

## 相关页面

- [[api/IMotionController]] — 运动控制器接口
- [[api/MotionManager]] — 运动控制器管理器
- [[api/IIO]] — IO接口
- [[modules/MotionControl]] — 模块文档