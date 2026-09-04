---
title: API — DeviceLog 设备日志统一出口
date: 2026-09-03
tags: [API, 日志, 规范, DeviceLog, MainDeviceControl, 可观测性]
source: AdaWeldSystem/MainDeviceControl/DeviceLog.cs
---

# API — DeviceLog 设备日志统一出口

> **本页述 `DeviceLog`（静态工具类，`MainDeviceControl/DeviceLog.cs`，命名空间 `AdaWeldSystem.MainDeviceControl`）**。
> 它是 `MainDeviceControl/` 下**唯一的设备日志出口**，内部封装 `GlobalCommData.ShowLog`。
>
> **确立背景（2026-09-03）**：改造前 `MainDeviceControl/` 有 63 处 `GlobalCommData.ShowLog`，标签写法发散——
> 5 个子工作流各用私有 `_tag`，基类用 `StateName`，两个管控类各用私有 `_tag`，甚至出现子类 `const string Tag`
> 遮蔽基类 `public object Tag` 的 CS0108 类型冲突。本次收敛为「**一个出口 + 一个标签约定**」。

---

## `public static class DeviceLog`

| 成员 | 签名 | 说明 |
|---|---|---|
| `Write` | `static void Write(string tag, string message, MessageLevel level = MessageLevel.Info)` | 通用出口，全类唯一调用 `GlobalCommData.ShowLog` 的地方 |
| `Info` | `static void Info(string tag, string message)` | `Write(tag, message, MessageLevel.Info)` 的语法糖 |
| `Warn` | `static void Warn(string tag, string message)` | 同上，Warning 级 |
| `Error` | `static void Error(string tag, string message)` | 同上，Error 级 |

> **实现刻意保持极薄**：只做转发，不吞异常、不做格式化、不缓存。日志内容规范（纯文本无符号、记录时机、通讯全记录）见 [[standards/CodeSimplification]] §三。

---

## 标签约定（强制）

| 角色 | 标签来源 | 写法 |
|---|---|---|
| 子工作流（`DeviceWorkflowBase` 子类） | 基类属性 `Tag`（`public string Tag { get; protected set; }`） | 构造函数首行赋值 `Tag = "线激光工作流";`，日志一律调基类 `Log(...)` |
| 独立管控类（`DeviceControlWork` / `DeviceStatusWork`） | 私有只读字段 `_tag` | 本类私有 `Log(...)` 辅助方法内调 `DeviceLog.Write(_tag, ...)` |
| 状态基座 `DeviceStateBase` | 抽象属性 `StateName` | `DeviceLog.Write(StateName, ...)` |
| 模拟模式子控制器 | 独立字段 `_simTag` | `DeviceLog.Write(_simTag, ...)`（`DeviceControlWork` 内） |

**现行标签清单**

| 标签 | 归属 |
|---|---|
| `线激光工作流` | `LineLaserWorkflow` |
| `监控相机工作流` | `MonitorCameraWorkflow` |
| `运动控制工作流` | `MotionControlWorkflow` |
| `焊接工艺控制工作流` | `WeldParamControlWorkflow` |
| `焊接头工作流` | `LaserWeldHeadWorkflow` |
| `模拟模式控制器` | `DeviceControlWork` 的 `_simTag` |

> ⚠️ **禁止**在基类 `DeviceWorkflowBase` 的子类里再声明 `Tag` / `_tag` 同名成员——`private const string Tag`
> 遮蔽基类 `public string Tag` 会触发 **CS0108**，且把 `string` 与基类类型对撞，多态语义彻底失效。
> 详见 [[lessons/DeviceControlWorkInheritanceBypass]] 坑一与 [[lessons/StepMemberNameCollision]] 坑二。

---

## 用法

```csharp
// ① 子工作流内（继承基类 Log，无需传标签）
Log("流程已启动", MessageLevel.Info);
Alarm("运控流程异常终止", ex);   // ⛔ 旧写法 string.Format(..., FailReason) 已废止

// ② 独立管控类内（私有 Log 辅助方法固定带 _tag）
private void Log(string message, MessageLevel level = MessageLevel.Info)
{
    DeviceLog.Write(_tag, message, level);
}

// ③ 需要脱离自身标签时（如模拟模式）
DeviceLog.Write(_simTag, "模拟模式开启 " + mode, MessageLevel.Info);
```

### 设备日志 vs 通讯日志（不得混用）

| 类别 | 出口 | 覆盖范围 |
|---|---|---|
| 设备日志 | `DeviceLog`（→ `GlobalCommData.ShowLog`） | 运行/状态切换/异常/生命周期；**连接 open / close 归此类** |
| 通讯日志 | `GlobalCommData.ShowCommunicationLog` | 监听建立后到停止前的**收发报文内容**，全记录不摘要 |

---

## 相关页面

- [[standards/CodeSimplification]] — §三 设备日志规范（内容无符号、记录时机、通讯全记录）+ §三④ 日志出口统一
- [[api/DeviceControlWork]] — 主设备运行管控，日志经 `DeviceLog`
- [[api/DeviceStatusWork]] — 安全/IO/状态管控，日志经 `DeviceLog`
- [[api/GlobalCommData]] — 底层 `ShowLog` / `ShowCommunicationLog`
- [[lessons/DeviceControlWorkInheritanceBypass]] — 本次收敛的起因：5 个 BUG 与继承失效根因
- [[architecture/DeviceControlArchitecture]] §2 — 目录结构中的 `DeviceLog.cs`
