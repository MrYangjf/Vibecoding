---
title: MotionManager API — 运动控制器管理器
date: 2026-08-04
tags: [API, 运控, 管理器, 单例]
source: AdaWeldSystem/MotionControl/MotionManager.cs
---

# MotionManager API — 运动控制器管理器

> 运动控制器管理器（单例），统筹所有控制器、轴、IO的创建与管理。
> 参考 PcomDeviceInterface 的 `MotionManager` 设计模式。
> 位于 `AdaWeldSystem.MotionControl` 命名空间。

## 单例访问

```csharp
public static MotionManager Instance { get; }
```

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `DefaultController` | `IMotionController` | 默认控制器（第一个注册的控制器） |
| `ControllerCount` | `int` | 控制器数量 |
| `IsInitialized` | `bool` | 是否已初始化 |

## 方法

| 方法 | 说明 |
|------|------|
| `Initialize()` | 初始化默认控制器（默认初始化正运动 ZMotion 控制器，按配置创建 Y轴/振镜轴/送丝伸缩臂轴/Z轴自动对焦轴 与 IO，见 [[decisions/ADR-027-DefaultInitZMotion]]） |
| `RegisterController(IMotionController)` | 注册控制器到管理器 |
| `GetController(string name)` | 按名称获取控制器 |
| `GetAxis(string axisName)` | 按名称获取轴（遍历所有控制器） |
| `GetInputIO(string ioName)` | 按名称获取输入IO（遍历所有控制器） |
| `GetOutputIO(string ioName)` | 按名称获取输出IO（遍历所有控制器） |
| `GetAllAxes()` | 获取所有轴列表（遍历所有控制器） |
| `SetGlobalEmergencyStop(bool)` | 设置全局急停（传播到所有控制器） |
| `ShutdownAll()` | 关闭所有控制器 |

## 使用模式

```csharp
// 初始化
MotionManager.Instance.Initialize();  // 默认初始化正运动 ZMotion 控制器（见 ADR-027）

// 工作流中控制轴
IAxis yAxis = MotionManager.Instance.GetAxis("Y轴");
yAxis.MoveTo(100.0, 20.0);

// 控制IO
IOutputIO weldStart = MotionManager.Instance.GetOutputIO("焊枪启动");
weldStart.SetON();

// 替换真实硬件
// var realCtrl = new RealMotionController("伺服控制器");
// realCtrl.AddAxis(realYAxis);
// realCtrl.AddIO(realOutput);
// MotionManager.Instance.RegisterController(realCtrl);

// 关闭
MotionManager.Instance.ShutdownAll();
```

## 相关页面

- [[api/IMotionController]] — 运动控制器接口
- [[api/IAxis]] — 运动轴接口
- [[api/IIO]] — IO接口
- [[modules/MotionControl]] — 模块文档