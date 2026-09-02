---
title: ADR-034 Dispose 模式全覆盖 — 非 UI 类统一标准 IDisposable
date: 2026-08-19
tags: [决策, 资源释放, IDisposable, DisposeComponents, 全覆盖]
status: accepted
---

# ADR-034：Dispose 模式全覆盖 — 非 UI 类统一标准 IDisposable

## 背景

[[decisions/ADR-001-DisposePattern]] 定义了 `DisposeComponents()` 模式，但项目落地时**范围发生漂移**：多个非 UI 类（Workflow 状态机、ZMotion 运动控制组件、Comm 通讯类）也编写了 `DisposeComponents()` 方法，导致两个问题：

1. **资源释放通道不统一**：调用方（尤其按 `IDisposable` 接口释放的代码）调用标准 `Dispose()` 时，非 UI 类的释放逻辑若未转发则不会执行，资源得不到释放。
2. **语义混淆**：`DisposeComponents()` 的本意是规避 UI 设计器对 `Dispose(bool)` 的限制，非 UI 类无此限制，应直接使用标准 `IDisposable.Dispose()`。

## 决策

1. **`DisposeComponents()` 仅限 UI 设计器类**（Form / UserControl 及其 `.cs` 后置代码）——规避设计器对 `Dispose(bool)` 的约束，保留既有用法。
2. **非 UI 类（后端类）一律使用标准 `IDisposable.Dispose()`**，禁止编写 `DisposeComponents()`：
   - 释放逻辑直接放入 `Dispose()` 实现
   - 类声明实现 `IDisposable`
   - 禁止在非 UI 类中重写 `Dispose(bool)`（此禁令本就针对设计器场景；非 UI 类按需使用标准 .NET Dispose pattern 亦可）
3. **级联释放链**：主窗体关闭 → `MainDeviceThread.Instance.Dispose()` → 停止子线程 + 关闭机器人 + Shutdown 焊接头 + `GlobalCommData.mCommunicationManager.Dispose()`（释放全部通讯实例）。

## 落地范围（2026-08-19）

| 类 | 迁移前 | 迁移后 |
|----|--------|--------|
| `Workflow/MainDeviceThread` | `DisposeComponents()` | `IDisposable.Dispose()`（+ 级联释放通讯管理器） |
| `Workflow/LineLaserWorkflow` | `DisposeComponents()` | `IDisposable.Dispose()`（+ 释放 `_ilCamera`） |
| `Workflow/MonitorCameraWorkflow` | `DisposeComponents()` | `IDisposable.Dispose()`（+ 释放 Mat） |
| `Workflow/LaserCamBoxTrackingWorkflow` | `DisposeComponents()` | `IDisposable.Dispose()`（子组件同步改 `Dispose()`） |
| `MotionControl/ZMotion/CamBoxTracker` | `DisposeComponents()` + `Dispose()` 转发 | 合并为单一 `Dispose()` |
| `MotionControl/ZMotion/EncoderAxis` | 同上 | 合并为单一 `Dispose()` |
| `MotionControl/ZMotion/RSIPositionBuffer` | 同上 | 合并为单一 `Dispose()` |
| `MotionControl/ZMotion/ZMotionController` | 无释放入口 | 新增 `IDisposable.Dispose()`（停线程 + 释放 GCHandle + Close） |
| `Comm/CommunicationManager` | 无释放入口 | 新增 `IDisposable.Dispose()`（释放 4 个通讯实例） |
| `Comm/CommBase/Ethernet/TcpIpComm` | 无释放入口 | 新增 `IDisposable.Dispose()` |
| `Comm/CommBase/Ethernet/SstTcpServer` | 仅析构函数 | 新增 `IDisposable.Dispose()` |
| `Comm/CommBase/Ethernet/SstTcpClient` | 无释放入口 | 新增 `IDisposable.Dispose()` |

> 保留 `DisposeComponents()` 的 UI 类：`UIDesign/TabPage/CommPage.cs`、`UIDesign/TabPage/MonitorCamPage.cs`（合规）。

### UI 类 `DisposeComponents()` 按需使用判定（2026-08-19 补充）

> 用户澄清（2026-08-19）：`DisposeComponents()` **仅当 UI 设计器类持有「外部嵌套控件/资源」时才需要写**——设计器自生成的 `Dispose(bool)` 对 components 容器内 .NET 控件友好，但**覆盖不到外部嵌套控件与独立资源**（代码 new 的 Timer / 外部 SDK 实例 / WPF 嵌套控件 / 静态或单例事件订阅 / Mat 等）。无嵌套、无独立资源管理的 UI 类**不需要** `DisposeComponents()`。

**判定规则：**
1. UI 类持有**设计器 Dispose 覆盖不到的外部资源**（代码 `new` 的非容器控件、单例/静态事件订阅、外部对象引用且持有其生命周期）→ **需要** `DisposeComponents()`，并由 `HandleDestroyed` 或父页面关闭时调用
2. UI 类仅使用设计器 components 容器内控件 → **不需要** `DisposeComponents()`（设计器 `Dispose(bool)` 已覆盖）
3. UI 类持有的仅是**外部注入引用**（如 `CameraSelector.Active` 共享实例，不订阅事件、不持有生命周期）→ 不需要释放
4. **禁止**通过修改 `*.Designer.cs` 的 `Dispose(bool)` 释放外部资源（违反 Designer.cs 不可修改原则）；**禁止**用 finalizer 退订事件（事件源持引用时 finalizer 永不执行，无效模式）

**2026-08-19 第二轮修复（UI 类落地）：**
- `HelixRenderForm`：`_viewer`（PointCloudViewer 含 WPF Viewport3DX）为外部嵌套资源 → **还原被手动修改的 Designer.cs Dispose(bool)**，新增 `DisposeComponents()` + `HandleDestroyed` 触发
- `MainPage`：持 `GlobalCommData.EventInfoHandler` + `_contourCamera.ContourDataReady` 订阅 → **移除无效 finalizer**，新增 `DisposeComponents()` + `HandleDestroyed` 触发
- `CommPage`：`DisposeComponents()` 原本无调用者（泄漏）→ 新增 `HandleDestroyed` 触发
- `MonitorCamPage`：`HandleDestroyed` 改为调用完整 `DisposeComponents()`（含 SensorStop/Stop）
- `MotionControlPage`：订阅 `StateChanged` 无销毁兜底 → 新增 `HandleDestroyed` 退订
- `FormMain`：订阅 `StateChanged` 未退订 → `FormClosed` 补退订

**无需 `DisposeComponents()` 的 UI 类（无外部资源/仅注入引用）：** `ILAlgoPage`、`AlgorithmEditForm`、`ILParamPage`、`EmguAlgoPage`、`DataReviewPage`、`FileEditorPage`、`ParamConfigPage`、`AutoParamForm`、`ConfigForm`、`FileTraceForm`、`FormLogin`、`ILScanDialog`、`LLCameraSetting`（HandleDestroyed 直接释放）、`RecordConfigForm`、`RenderParamForm`、`UserEdit` 等。

**已用 `HandleDestroyed` 直接释放（等效正确位置）的 UI 类：** `ILCamPage`（退订+Mat+断开相机）、`LLCamWorkJob`（退订+Timer+Mat）、`LLCameraSetting`。这些类未写 `DisposeComponents()` 命名，但释放位置正确（HandleDestroyed 即「正确的地方」），按最小变更原则保留现状。

## 备选方案

- **保留非 UI 类的 `DisposeComponents()` 并让其 `Dispose()` 转发**：会造成双命名并存，调用方仍需区分，未根治"通道不统一"问题，弃用。
- **为全部类重写 `Dispose(bool)`**：非 UI 类可行但改动面过大，且与 ADR-001 字面禁令冲突（该禁令本意针对设计器），弃用。

## 后果

### 正面

- 非 UI 类释放通道统一为标准 `IDisposable.Dispose()`，接口调用即可正确释放
- UI 类 `DisposeComponents()` 语义澄清，不再与设计器冲突
- FormMain 关闭链级联释放全部通讯/运动/焊接资源，退出干净

### 负面

- 已按 `DisposeComponents()` 调用的旧代码需同步改名（本次已全量迁移，无遗留调用点）
- 需在 Lessons 中固化"非 UI 类禁止 `DisposeComponents()`"规则防止回潮

## 相关页面

- [[decisions/ADR-001-DisposePattern]]
- [[guides/WinForms-Designer]]
- [[modules/Comm]]
- [[modules/DeviceControl]]
- [[modules/MotionControl]]
