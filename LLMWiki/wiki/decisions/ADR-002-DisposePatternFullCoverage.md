---
title: ADR-002 Dispose 模式现行决策（UI DisposeComponents + 非 UI 标准 IDisposable；整合原 001/020）
date: 2026-08-19
updated: 2026-10-30
tags: [决策, 资源释放, IDisposable, DisposeComponents, UI, WinForms, merged]
status: accepted
merged_from: [ADR-001, ADR-020]
---

# ADR-002 Dispose 模式现行决策（UI DisposeComponents + 非 UI 标准 IDisposable）

> 本页为整合页（2026-09-17），就地吸收并取代原 ADR-001 / ADR-001 两页，收拢 Dispose 模式全部现行裁定。沿革见文末。

## 背景

WinForms 设计器生成的 `*.Designer.cs` 包含 `Dispose(bool)`：手写或改写会破坏设计器生成逻辑、导致显示异常，且该重写只对 components 容器内的 .NET 控件友好。项目早期（ADR-001，2026-07-01）为此定义了 `DisposeComponents()` 模式；落地时范围一度漂移到非 UI 类（Workflow 状态机、运动控制组件、Comm 通讯类也写了 `DisposeComponents()`），造成释放通道不统一（调用方按 `IDisposable` 接口调用 `Dispose()` 不会命中释放逻辑）与语义混淆（该模式本意只是规避 UI 设计器约束，非 UI 类无此约束）。ADR-001（2026-08-19）完成全项目迁移纠偏。

## 现行决策

### 1. UI 设计器类（Form / UserControl 及其 `.cs` 后置代码）

1. **禁改 `*.Designer.cs` 的 `Dispose(bool)`**：外部资源不得经由设计器 Dispose 释放（违反 Designer.cs 不可修改原则）。
2. **UI 类 `.cs` 后置代码不直接重写 `Dispose(bool)`**：外部资源释放逻辑放入 `DisposeComponents()` 公共方法。
3. **`DisposeComponents()` 按需使用**——仅当 UI 类持有设计器 Dispose 覆盖不到的「外部嵌套控件 / 独立资源」（代码 `new` 的非容器控件、Timer、外部 SDK 实例、WPF 嵌套控件、静态/单例事件订阅、Mat 等）时才写；由 `HandleDestroyed` 或父页面关闭时调用。
4. **容器子控件释放约定**：设计器自生成的 `Dispose(bool)` 已覆盖 components 容器内的 .NET 子控件——**无需也不得重复释放**；`DisposeComponents()` 只收容器外的外部资源。
5. UI 类仅持**外部注入引用**（如 `CameraSelector.Active` 共享实例，不订阅事件、不持有生命周期）→ 不需要释放。
6. **禁止用 finalizer 退订事件**：事件源持引用时 finalizer 永不执行，属无效模式。

### 2. 非 UI 类（后端类）

1. **一律实现标准 `IDisposable.Dispose()`**：释放逻辑直接放入 `Dispose()` 实现，类声明实现 `IDisposable`。
2. **禁止编写 `DisposeComponents()`**（非 UI 类无设计器约束，无此模式的存在理由；2026-08-19 全项目迁移落地）。
3. 非 UI 类禁止重写 `Dispose(bool)`：该限制的直接触发场景是 `.designer.cs` 设计器文件；非 UI 类直接实现标准 `Dispose()` 即可。
4. 非 UI 类需自行确保 `Dispose()` 被调用——调用链由父容器 / 主窗体关闭时级联触发（见 [[modules/DeviceControl]]）。

### 3. 级联释放链

主窗体关闭 → `MainDeviceThread.Instance.Dispose()` → 停止子线程 + 关闭机器人 + Shutdown 焊接头 + `GlobalCommData.mCommunicationManager.Dispose()`（释放全部通讯实例）。

## 落地状态（2026-08-19 全量迁移，无遗留调用点）

- 非 UI 类已迁移为单一 `IDisposable.Dispose()`：`Workflow/MainDeviceThread`、`LineLaserWorkflow`、`MonitorCameraWorkflow`、`LaserCamBoxTrackingWorkflow`、`MotionControl/ZMotion/CamBoxTracker`、`EncoderAxis`、`RSIPositionBuffer`、`ZMotionController`（新增，停线程+释放 GCHandle+Close）、`Comm/CommunicationManager`（释放 4 个通讯实例）、`TcpIpComm`、`SstTcpServer`、`SstTcpClient`。
- 保留 `DisposeComponents()` 的 UI 类（合规）：`CommPage`（现役 `FilebackupPage.cs`）、`MonitorCamPage`、`HelixRenderForm`、`MainPage`、`MotionControlPage`（现役 `SystemControlPage.cs`）（`HandleDestroyed` 触发；`FormMain` 经 `FormClosed` 补退订 `StateChanged`）。
- 无外部资源 / 仅注入引用的 UI 类不写 `DisposeComponents()`：`ILAlgoForm`、`ILAlgorithmEditForm`、`ILParamForm`、`EmguAlgoPage`、`DataReviewerPage`、`FileEditorPage`、`ParamConfigPage`、`AutoParamForm`、`ConfigForm`、`FileTraceForm`、`LoginForm`、`ILScanForm`、`RecordConfigForm`、`RenderParamForm`、`UserEditForm` 等。
- `ILCamPage`、`LLCamWorkJob`、`LLCameraSetting` 用 `HandleDestroyed` 直接释放（退订+Mat+Timer/断开相机）——释放位置等效正确，按最小变更原则保留现状。

## 备选方案（已弃）

- 保留非 UI 类 `DisposeComponents()` 并让 `Dispose()` 转发：双命名并存、调用方仍需区分，未根治通道不统一，弃用。
- 为全部类重写 `Dispose(bool)`：非 UI 类可行但改动面过大，且与初版禁令字面冲突（该禁令本意针对设计器），弃用。

## 后果

### 正面

- 非 UI 类释放通道统一为标准 `IDisposable.Dispose()`，按接口调用即可正确释放
- UI 类 `DisposeComponents()` 语义澄清，不再与设计器冲突
- FormMain 关闭链级联释放全部通讯/运动/焊接资源，退出干净

### 负面

- 需手动确保父页面调用 `DisposeComponents()`（已以 `HandleDestroyed` 兜底）
- 非 UI 类需自行确保 `Dispose()` 被调用（依赖级联链）

## 沿革

- 2026-07-01 ADR-001 初版：定义 UI `DisposeComponents()` 模式，规避设计器对 `Dispose(bool)` 的限制。
- 2026-08-19 ADR-001：全覆盖纠偏——非 UI 类统一标准 `IDisposable`、UI 类按需判定与第二轮修复落地。本页（2026-09-17）整合两者，初版 001 就此并入。

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[guides/WinForms-Designer]]
- [[modules/UIDesign]] / [[modules/Comm]] / [[modules/DeviceControl]] / [[modules/MotionControl]]
