---
title: IMotionController API — 运动控制器接口
date: 2026-08-04
tags: [API, 运控, 控制器, 接口]
source: AdaWeldSystem/MotionControl/IMotionController.cs
---

# IMotionController API — 运动控制器接口

> 运动控制器抽象接口，管理轴和IO的控制器生命周期。参考 PcomDeviceInterface 的 `MontionControl` 设计模式。
> 位于 `AdaWeldSystem.MotionControl` 命名空间。

## 接口定义

```csharp
public interface IMotionController
{
    // 属性
    string Name { get; }
    bool IsConnected { get; }
    int AxisCount { get; }
    int InputCount { get; }
    int OutputCount { get; }
    bool IsEmergencyStop { get; }

    // 控制器生命周期
    bool Initialize();
    void Close();

    // 轴管理
    void AddAxis(IAxis axis);
    void RemoveAxis(IAxis axis);
    IReadOnlyList<IAxis> GetAxes();
    IAxis GetAxis(ushort axisNumber);
    IAxis GetAxisByName(string axisName);

    // IO管理
    void AddIO(IIO io);
    void RemoveIO(IIO io);
    void ClearIO();
    IReadOnlyList<IIO> GetInputs();
    IReadOnlyList<IIO> GetOutputs();
    IInputIO GetInput(ushort ioNumber);
    IOutputIO GetOutput(ushort ioNumber);

    // 急停控制
    void SetEmergencyStop(bool isEmergencyStop);
}
```

## 派生类

| 类 | 说明 |
|----|------|
| `MotionControllerBase` | 抽象基类，实现轴/IO列表管理、线程安全锁、Add/Remove/Get逻辑 |
| `ZMotionController` | 正运动（ZMotion）控制器实现（以太网连接硬件，4轴+IO），2026-08-21 起为默认初始化控制器（见 [[decisions/ADR-027-DefaultInitZMotion]]）；原 `NullMotionController` 空实现已删除 |

## 使用方式

```csharp
// 通过 MotionManager 获取控制器
IMotionController controller = MotionManager.Instance.DefaultController;
controller.Initialize();

// 获取轴（实际轴由控制器初始化时按配置创建，亦可运行时补加）
IAxis yAxis = controller.GetAxis("Y轴");

// 获取IO（实际IO由控制器初始化时创建，亦可运行时补加）
IOutputIO weldStart = controller.GetOutputIO("焊枪启动");
weldStart.SetON();
```

## 相关页面

- [[api/MotionManager]] — 运动控制器管理器
- [[api/IAxis]] — 运动轴接口
- [[api/IIO]] — IO接口
- [[modules/MotionControl]] — 模块文档