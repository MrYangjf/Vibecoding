---
title: GlobalCommData API 参考
date: 2026-07-02
tags: [API, 通讯, 全局状态, 事件总线]
source: raw/skills/02-Development/GeneralTechSpecialist.md
---

# GlobalCommData API 参考

> 全局数据通讯中心（事件总线模式）。
> 物理文件：`Comm/SystemComm/SystemComm.cs`（由原 `GlobalCommData.cs` 与 `SystemStatus.cs`（已移除） 合并而来；2026-09-14 ADR-045 迁入 `SystemComm/` 子目录；ADR-048 起命名空间随目录，现为 `AdaWeldSystem.Comm.SystemComm`）。
> 职责按优先级分为 3 类：全局事件触发、全局日志管理、全局通讯配置管理。
> **自动调整参数管理已迁出到 [[api/WeldParamManager]]**（2026-09-14：原 `WeldDataManager` 已并入 `WeldParamManager`）。
> **全局状态不再由本文件承载**：三态模型（ADR-028）的状态枚举与事件参数统一由 `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` 承载，见 [[architecture/DeviceControlArchitecture]]。

## 核心类

```csharp
static class GlobalCommData
{
    // 1. 全局事件触发
    public static event EventHandler<MessageArgs> EventInfoHandler;
    public static event EventHandler<string> CommunicationCommandReceived;

    // 2. 全局日志管理
    // MachineLog 和 TcpMessageLog 为内部字段，外部代码禁止直接调用
    // 所有模块日志统一通过 ShowLog 接口输出
    public static Log MachineLog;
    public static Log TcpMessageLog;
    public static void ShowLog(string TAG, string message, MessageLevel msgLevel = MessageLevel.Info, MessageType msgType = MessageType.Debug);
    public static void ShowCommunicationLog(string source, string message);

    // 3. 全局通讯配置管理
    public static CommunicationManager mCommunicationManager;
    public static void BroadcastCommunicationCommand(string message);

    // 遗留支持
    public static AuthHelper mAuthHelper;
    public static OperateLevel mOperateLevel;

    // 7. UI 配置（AntdUI.Config 一次性加载，2026-08-13 新增）
    private static bool _uiConfigLoaded;           // 一次性加载守卫
    public static void UIConfigSetting();           // 集中管理 AntdUI.Config：主题(IsLight+Theme) + 文本渲染(TextRenderingHint/HighQuality)
}
```

## 同文件类型定义

`SystemComm.cs` 同时定义了以下枚举和事件参数类：

```csharp
public enum MessageType { Summary, Run, Flow, Debug }
public enum MessageLevel { Info, Warning, Error }
public enum OperateLevel { Operator = 2, Engineer = 1, Admin = 0 }

public class MessageArgs : EventArgs
{
    public string strMessage;
    public Color MessageShowColor;
}
```

> **2026-09-02（ADR-028）状态枚举与事件参数已全部迁出本文件**：`LineLaserWorkflowState` / `WorkflowSignalCode` / 泛型 `WorkflowStepChangedEventArgs<TStep>` 等**在 `SystemComm.cs` 中已不存在**。现行状态契约由 `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` 承载——`SubDeviceState` / `SubDeviceWeldStatus` / `MainDeviceStatus` 三枚举 + `WeldStatusChangedEventArgs` / `SubDeviceStateChangedEventArgs` / `MainDeviceStatusChangedEventArgs` 三事件参数。各工作流的阶段枚举降为**私有**、内联于各自工作流文件。详见 [[architecture/DeviceControlArchitecture]]、[[modules/DeviceControl]]。

## 自动调整参数管理（已迁出）

自动调整参数管理已迁出到 [[api/WeldParamManager]]。`GlobalCommData` 不再持有 `mAutoParam`、`mAutoParamManage`、`mConfigManager`、`CurrentAutoParamId`。

| 原字段 | 新位置 | 说明 |
|--------|--------|------|
| `GlobalCommData.CurrentAutoParamId` | `WeldParamManager.Instance.CurrentAutoParamId` | INI 持久化 |
| `GlobalCommData.mAutoParam` | `WeldParamManager.Instance.CurrentAutoParam` | 运行时对象 |
| `GlobalCommData.mAutoParamManage` | `WeldParamManager.Instance.AutoParamHelper` | 分段数据表管理 |
| `GlobalCommData.mConfigManager` | `WeldParamManager.Instance.ConfigHelper` | 配置映射管理 |

## 通讯指令流程

```
[通讯实现] TCP/S7/Robot（EthernetXmlComm/SiemensS7Comm/KUKA RSI+EKI）
        │
        ▼
GlobalCommData.BroadcastCommunicationCommand(message)
        │
        ▼
GlobalCommData.CommunicationCommandReceived
        │
        ▼
[Workflow] LineLaserWorkflow.OnCommunicationCommandReceived
        │
        ▼
GlobalCommData.ShowCommunicationLog(source, message)
        │
        ▼
EventInfoHandler → MainPage.inputLog（AntdUI.Input，受 ShowCommLog 开关控制）
```

## 使用规范

- 所有模块通过 GlobalCommData 进行跨模块通信
- 事件处理必须检查 InvokeRequired（UI 线程安全）
- **系统状态统一由三态模型管理（[[architecture/DeviceControlArchitecture]]）**：子设备连接态 `Instance.State`（`SubDeviceState`）+ 焊接过程态 `Instance.WeldStatus`（`SubDeviceWeldStatus`）+ 整机运行态 `DeviceControlWork.Instance.Status`（`MainDeviceStatus`）；UI 通过订阅 `StateChanged` / `WeldStatusChanged` / `StatusChanged` 刷新状态显示
- **日志统一接口：`ShowLog(TAG, message, msgLevel)` 是唯一对外日志接口，所有模块禁止直接调用 `MachineLog.Debug/Info/Error/Warn`**
- **msgLevel 控制文件日志等级映射**：

| msgLevel | 文件日志等级 | UI 颜色 |
|----------|-------------|---------|
| `MessageLevel.Info` | `MachineLog.Info` | 黑色 |
| `MessageLevel.Warning` | `MachineLog.Warn` | 蓝色 |
| `MessageLevel.Error` | `MachineLog.Error` | 红色 |
- 高频事件参数已类级复用，避免每次调用 `new MessageArgs` 产生 GC 压力
- 所有 static 字段在 static 构造函数中集中初始化（ADR-002）
- 通讯 XML 结构已扩展为 7 个，按设备类型分离：Server/Client/Send/Recive（通用 TCP）+ RobotServer/RobotClient（机器人）+ PLC（PLC 通讯），详见 [[decisions/ADR-006-CommXmlSeparation]]
- 通用以太网通讯实例 `EthernetComm`（`EthernetXmlComm`，2026-09-14 ADR-045 取代旧 `TcpIpComm`）由 `mCommunicationManager` 持有和管理，访问路径为 `GlobalCommData.mCommunicationManager.EthernetComm`
- 通讯日志显示开关已扩展为 3 个：`ShowCommLog` / `ShowRobotCommLog` / `ShowPlcCommLog`，各通讯页面独立控制
- 三个通讯页面均订阅 `EventInfoHandler` 事件，在 `chkShowCommLog` 勾选时将通讯日志显示到页面 `txtLog`
- 自动调整参数管理已迁出到 [[api/WeldParamManager]]，不再使用 `ParamConfigXdoc`

## 新增/变更

- **新增 `UIConfigSetting()`（2026-08-13）**：集中管理 AntdUI.Config 全局 UI 配置，一次性加载（`_uiConfigLoaded` 守卫）。将原先分散在 `Program.Main`（`TextRenderingHint`/`TextRenderingHighQuality`）与 `FormMain` 构造函数（`IsLight` + `Theme().Dark().Light().FormBorderColor()`）的 AntdUI 配置统一迁入，`FormMain` 构造改调 `GlobalCommData.UIConfigSetting()`
- **通讯 XML 配置按设备类型分离（ADR-008）**：新增 `RobotServerXdoc` / `RobotClientXdoc` / `PlcXdoc`，新增 `ShowRobotCommLog` / `ShowPlcCommLog` INI 持久化开关
- **三个通讯页面完善**：CommGeneralPage 新增保存配置按钮和事件订阅；CommRobotPage 改用 `RobotServerXdoc`，新增保存配置按钮和 `chkShowCommLog`；CommPLCPage 改用 `PlcXdoc`，新增保存配置按钮和 `chkShowCommLog`
- 新增 `mCommunicationManager`：通讯对象持久化配置管理，内部持有 Server/Client/Send/Receive XML
- 新增 `CommunicationCommandReceived` + `BroadcastCommunicationCommand`：统一通讯指令广播
- 新增 `ShowCommunicationLog(source, message)`：受 `mCommunicationManager.ShowCommLog` 控制的通讯日志
- 迁出 `CurrentAutoParamId`、`mAutoParam`、`mAutoParamManage`、`mConfigManager` 到 [[api/WeldParamManager]]（2026-09-14：原 `WeldDataManager` 已并入 `WeldParamManager`）
- **合并 `GlobalCommData.cs` 与 `SystemStatus.cs`（已移除） 为 `SystemComm.cs`**
- **移除 `MachineStatus` 枚举、`MachineStatusMessageArgs`、`EventStatusHandler`、`CurrentStatus`、`LastStatus`**
- **系统状态枚举与事件参数迁至 `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs`（2026-09-02 ADR-028 三态模型）**
- **`TCPIPComm` 纳入 `CommunicationManager` 管理（沿革：2026-09-14 ADR-045 废弃重写为 `EthernetXmlComm`，访问路径 `mCommunicationManager.EthernetComm`）**
- 删除 `EventTcpInfoHandler`、`EventTcpClientInfoHandler`、`EventLineLaserInfoHandler`、`EventRobotInfoHandler`
- 删除 `ShowTcpMessage`、`ShowTcpClientMessage`、`ShowLaserData`
- 删除 `ServerXdoc`、`ClientXdoc`、`SendXdoc`、`ReciveXdoc`、`ParamConfigXdoc`、`RenderConfigXdoc`
- ~~`TCPIPComm` 已迁移到 `AdaWeldSystem.Comm.Ethernet` 命名空间~~ → **2026-09-14 ADR-045**：废弃重写为 `EthernetXmlComm`（命名空间 `AdaWeldSystem.Comm.Communication.Implementations`），收发 KUKA 风格预定义 XML 文档

## 已知问题

- 与 [[modules/WeldParamControl]] 存在循环依赖
- 与 [[modules/SQLiteDatabase]] 存在循环依赖
- 与 [[modules/FileOperate]] 存在循环依赖

---

*来源：raw/skills/02-Development/GeneralTechSpecialist.md*
