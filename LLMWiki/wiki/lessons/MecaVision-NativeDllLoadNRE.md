---
title: 麦格威 MVSDK 原生 DLL 未部署导致 NullReferenceException
date: 2026-09-09
tags: [教训, 麦格威, MecaVision, MVSDK, DLL部署, NullReferenceException, 动态加载]
---

# 麦格威 MVSDK 原生 DLL 未部署导致 NullReferenceException

> ⚠️ 关联：[[guides/MecaVision-DevGuide]] · [[api/MecaVisionMVSDK-Native]] · [[decisions/ADR-041-MecaVisionMonitorCamera]]

## 现象（2026-09-09 实测）

```
CameraSdkStatus status = MvApi.CameraSdkInit(0);
System.NullReferenceException: "未将对象引用设置到对象的实例。"
```

## 根因链（三层叠加，逐层定位）

1. **`MVSDK.cs` 无 DllImport**：`MvApi.CameraSdkInit` 是 **static 委托字段**，由静态构造函数 `LoadLibrary("MVCAMSDK_X64.dll")` + `GetProcAddress` 批量填充。
2. **`LoadLibrary` 失败不抛异常**：DLL 找不到 / 位数不匹配时静默返回 `IntPtr.Zero`，静态构造函数照常走完（`GetProcAddress(IntPtr.Zero,...)` 也只返回 Zero），**所有委托字段 = null**。
3. **csproj 拷贝清单漏项**：DLL 已落到 `3rdDepend/MecaVision/`，但 `CopyNative3rdDependToOutput` 目标没列它 → 输出目录无 DLL → 首次调用委托 → NRE。

## 修复（✅ 2026-09-09 已落地）

| 位置 | 变更 |
|---|---|
| `AdaWeldSystem.csproj` | `CopyNative3rdDependToOutput` 增加 `3rdDepend\MecaVision\` 下 4 文件（`MVCAMSDK_X64.dll`、`MVImageProcess_X64.DLL`、`GiGeCamera_X64.Interface`、`Usb3Camera0_X64.Interface`） |
| `MVSDK.cs` 静态构造 | 加 2 道守卫：`hSdkDll == IntPtr.Zero` → `DllNotFoundException`（报 DLL 名与部署提示）；`CameraSdkInit == null` → `EntryPointNotFoundException`（防误部署例程 bin 的旧互操作组件） |
| `MecaVisionCam.Connect` catch | 日志改取 `ex.InnerException?.Message`——静态构造异常被 `TypeInitializationException` 包装，外层 `ex.Message` 无诊断价值 |

## 教训要点

- **「加载失败静默继续」是动态加载类 SDK 的通病**：凡 static ctor + LoadLibrary + GetProcAddress 模式，NRE 的第一嫌疑就是原生库没加载上，先查输出目录再查代码。
- **`3rdDepend` 落文件 ≠ 部署完成**：本项目原生 DLL 统一经 csproj `CopyNative3rdDependToOutput` 拷到输出目录，新增原生依赖必须同步加条目（与台达 `EtherCAT_DLL_x64.dll` 同款流程）。
- **守卫把 NRE 变成可定位报错**：部署类故障应在加载点显式 fail-fast，而不是让 null 委托流到业务调用点爆炸。
