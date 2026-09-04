---
title: MonitorAlgorithmManager API 参考
date: 2026-07-17
tags: [API, 监控, 算法, 管理器, 持久化]
source: AdaWeldSystem/MonitorCam/MonitorAlgorithmManager.cs
---

# MonitorAlgorithmManager API 参考

> 监控相机算法管理器（单例），位于 `MonitorCam/MonitorAlgorithmManager.cs`，命名空间 `AdaWeldSystem.MonitorCam`。
> 持有焊缝检查所需的**唯一一套可配置算法参数**（不切换 JOB），并持久化到 `Config/INI/MonitorAlgorithm.ini`。
> 与 `ImageAlgorithm` 纯算法实现分离（镜像 EmguALG 的 AlgorithmManager 范式，遵循 [[decisions/ADR-003-SingleAlgorithmFile]]）。

## 单例

```csharp
public static MonitorAlgorithmManager Instance { get; }   // Lazy<T>
```

## 公共属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `AlignmentConfig` | `PreWeldAlignmentConfig`（EmguALG） | 焊前对中算法参数（ToleranceX / ToleranceY / ToleranceAngle） |
| `QualityConfig` | `WeldQualityConfig`（EmguALG） | 焊中质检算法参数（PassScore） |

## 方法

| 方法 | 说明 |
|------|------|
| `void Load()` | 从 `Config/INI/MonitorAlgorithm.ini` 加载算法参数；须在 `FormMain` 启动期、创建子页面前调用（参见 [[guides/Project-Tools]]） |
| `void Save()` | 将当前算法参数持久化到 INI（用户「保存算法参数」时调用） |

## 与 MonitorCameraWorkflow 的协作

`MonitorCameraWorkflow.AnalyzeImage()` 统一从 `MonitorAlgorithmManager.Instance` 读取 `AlignmentConfig` / `QualityConfig` 传入 `ImageAlgorithm.DetectPreWeldAlignment` / `DetectWeldQuality`，
取代原先从 `MonitorCameraConfig` 直接读取阈值的做法，实现「算法配置管理」与「相机硬件配置」分离（参见 [[modules/MonitorCam]]）。

## 设计约束

- 单一可配置算法 Profile，**无 JOB 切换**（针对仅是焊缝检查、无多种类，符合用户需求）
- 持久化文件归 `Config/INI/`，遵循 [[decisions/ADR-007-ConfigLayout]]
- 启动加载遵循 [[guides/Project-Tools]]（否则仅写不读，每次打开需重新配置）
- C# 7.3（`using` 顶部声明、构造函数初始化），遵循 [[decisions/ADR-002-CS73-Constraint]]

---

*来源：AdaWeldSystem/MonitorCam/MonitorAlgorithmManager.cs*
