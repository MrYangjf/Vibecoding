---
title: IIO API — IO接口
date: 2026-08-04
tags: [API, 运控, IO, 接口]
source: AdaWeldSystem/MotionControl/IIO.cs
---

# IIO API — IO接口

> 定义输入/输出IO的泛化接口，位于 `AdaWeldSystem.MotionControl` 命名空间。

## 枚举

```csharp
public enum IOType { Input, Output }
```

## 接口层级

### IIO（基础接口）

| 成员 | 说明 |
|------|------|
| `IOName` | IO名称 |
| `IONumber` | IO号（在控制器中的索引） |
| `IsOn` | IO是否导通 |
| `GetIOType()` | 获取IO类型（Input/Output） |
| `GetIOStatus()` | 获取IO状态值 |

### IInputIO : IIO（输入IO）

| 成员 | 说明 |
|------|------|
| `IsEnabled` | 是否启用检测 |

### IOutputIO : IIO（输出IO）

| 成员 | 说明 |
|------|------|
| `SetON()` | 设置输出为ON |
| `SetOFF()` | 设置输出为OFF |
| `EmergencyStopOff` | 急停时是否自动关闭 |

## 默认实现

| 类 | 说明 |
|----|------|
| `ZMotionInputIO` | 正运动输入IO实现（`IInputIO`），由 `ZMotionController` 初始化时按配置创建；`NullInputIO` 已随 [[decisions/ADR-037-DefaultInitZMotion]] 删除 |
| `ZMotionOutputIO` | 正运动输出IO实现（`IOutputIO`），支持 SetON/SetOFF；`NullOutputIO` 已随 [[decisions/ADR-037-DefaultInitZMotion]] 删除 |

## 相关页面

- [[api/IMotionController]] — 运动控制器接口
- [[api/MotionManager]] — 运动控制器管理器
- [[api/IAxis]] — 运动轴接口
- [[modules/MotionControl]] — 模块文档