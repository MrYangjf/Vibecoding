---
title: GlobalCommData API 参考
date: 2026-07-02
tags: [API, 通讯, 全局状态, 事件总线]
source: raw/skills/02-Development/GeneralTechSpecialist.md
---

# GlobalCommData API 参考

> 全局数据通讯中心（事件总线模式）。
> 物理文件：`Comm/SystemComm/SystemComm.cs`（由原 `GlobalCommData.cs` 与 `SystemStatus.cs`（已移除） 合并而来；2026-09-14 ADR-011 迁入 `SystemComm/` 子目录；ADR-005 起命名空间随目录，现为 `AdaWeldSystem.Comm.SystemComm`）。
> 职责按优先级分为 3 类：全局事件触发、全局日志管理、全局通讯配置管理。
> **自动调整参数管理已迁出到 [[api/WeldParamManager]]**（2026-09-14：原 `WeldDataManager` 已并入 `WeldParamManager`）。
> **全局状态不再由本文件承载**：三态模型（ADR-034）的状态枚举与事件参数统一由 `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` 承载，见 [[architecture/DeviceControlArchitecture]]。

## 核心类

```csharp
static class GlobalCommData
{
    // 1. 全局事件触发
    public static event EventHandler<MessageArgs> EventInfoHandler;
    public static event EventHandler<string> CommunicationCommandReceived;

    // 1.1 通讯日志查看事件（2026-11-17 ADR-106）：仅 FilebackupPage 订阅，不承载指令语义
    public static event EventHandler<string> CommLogViewEvent;

    // 2. 全局日志管理
    // MachineLog 和 TcpMessageLog 为内部字段，外部代码禁止直接调用
    // 所有模块日志统一通过 ShowLog 接口输出
    public static Log MachineLog;
    public static Log TcpMessageLog;
    public static void ShowLog(string TAG, string message, MessageLevel msgLevel = MessageLevel.Info, MessageType msgType = MessageType.Debug);
    public static void ShowCommunicationLog(string source, string message);
    public static void ShowCommLogForView(string source, string message);  // 写 TcpMessageLog + 触发 CommLogViewEvent，不进系统日志

    // 3. 全局通讯配置管理
    public static CommunicationManager mCommunicationManager;
    public static void BroadcastCommunicationCommand(string message);

    // 3.1 界面就绪门控（2026-10-21，ADR-074 决策 8）
    public static bool IsUiReady { get; }        // 全部子页面实例化完成
    public static void MarkUiReady();             // FormMain 构造函数 LoadNavAndPages 之后调用

    // 3.2 正常运行态门控（2026-11-09，ADR-078 通用化 / H11）
    public static bool IsAppRunning { get; }     // 首屏设备初始化结束、进入正常运行态
    public static void MarkAppRunning();         // FormMain 首次 Shown 的设备初始化 Modal 关闭后调用一次

    // 遗留支持
    public static AuthHelper mAuthHelper;

    // 3.5 权限等级（⛔ 禁直接赋值，必须走 SetOperateLevel 以广播事件）
    public static OperateLevel mOperateLevel;                       // 静态构造初始化为 Admin（调试期裁定）
    public static event EventHandler<OperateLevel> OperateLevelChanged;
    public static void SetOperateLevel(OperateLevel level);          // 同值短路 + 广播 OperateLevelChanged

    // 7. UI 配置（AntdUI.Config 一次性加载，2026-08-13 新增）
    private static bool _uiConfigLoaded;           // 一次性加载守卫
    public static void UIConfigSetting();           // 集中管理 AntdUI.Config：主题(IsLight+Theme) + 文本渲染(TextRenderingHint/HighQuality)
}
```

## 权限等级机制（2026-10-08 S-11 落地）

| 项 | 内容 |
|---|---|
| **默认等级** | **`Admin`**（`SystemComm` 静态构造第 233 行）。⚠️ 原为 `Operator`，S-11 按业主裁定改为管理员 —— 调试测试需最高权限 |
| **注销降级** | `LoginForm.BtnLogout_Click` → `SetOperateLevel(OperateLevel.Operator)` |
| **统一写入口** | ⛔ `mOperateLevel` 禁止直接赋值（全库仅 `SetOperateLevel` 内部一处）。直接赋值不会广播事件 ⇒ 各页无法感知降权 |
| **变更广播** | `SetOperateLevel` 同值短路后触发 `OperateLevelChanged`，订阅方：`FormMain.OnOperateLevelChanged`（导航显隐 + 状态栏标签）、`SystemControlPage.OnOperateLevelChanged`（页级门控重算）。⛔ 两处订阅均在 `DisposeComponents`/`FormClosed` 显式退订（静态事件不随控件释放） |
| **等级职责** | 集中在 `PermissionLevel`（同目录 `PermissionLevel.cs`）：`GetDisplayName`（管理员/工程师/操作员）· `GetDutyText`（职责说明）· `IsAdmin` · `IsEngineerOrAbove`。⛔ 禁止在 UI 各处分散硬编码等级比较 |
| **门控落点** | 导航显隐与状态栏标签见 [[api/FormMain]]；激光头页三层门控见 [[api/SystemControlPage]]；用户登录/注销见 `LoginForm.cs` |

## 同文件类型定义

`SystemComm.cs` 同时定义了以下枚举和事件参数类：

```csharp
public enum MessageType { Summary, Run, Flow, Debug }
public enum MessageLevel { Info, Warning, Error, Debug }   // Debug：UI 默认不显示（受 ShowDebugToUi 控制），文件全量
public enum OperateLevel { Admin = 0, Engineer = 1, Operator = 2 }   // 数值越小权限越高

public class MessageArgs : EventArgs
{
    public string strMessage;
    public Color MessageShowColor;
}
```

> **2026-09-02（ADR-034）状态枚举与事件参数已全部迁出本文件**：`LineLaserWorkflowState` / `WorkflowSignalCode` / 泛型 `WorkflowStepChangedEventArgs<TStep>` 等**在 `SystemComm.cs` 中已不存在**。现行状态契约由 `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` 承载——`SubDeviceState` / `SubDeviceWeldStatus` / `MainDeviceStatus` 三枚举 + `WeldStatusChangedEventArgs` / `SubDeviceStateChangedEventArgs` / `MainDeviceStatusChangedEventArgs` 三事件参数。各工作流的阶段枚举降为**私有**、内联于各自工作流文件。详见 [[architecture/DeviceControlArchitecture]]、[[modules/DeviceControl]]。

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
[通讯实现] TCP/S7/Robot（EthernetXmlComm/SiemensS7Comm/KUKA RSI 单一通道）
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

## 静态构造与界面就绪约束（2026-10-21）

| 约束 | 说明 |
|---|---|
| 静态构造顺序 | `_logArgs` **最先**初始化，其次 `MachineLog`/`TcpMessageLog`，最后 `mCommunicationManager`。`CommunicationManager` 构造可能重入 `ShowLog`（RSI 格式契约升级告警），顺序颠倒即 `NullReferenceException` |
| `ShowLog` 空保护 | 静态构造期的 `_logArgs` / `MachineLog` / `TcpMessageLog` 都可能未就绪，全部按 null 跳过；`EventInfoHandler` 为 null 时不广播 |
| 界面就绪门控 | 硬件/通讯启动前必须 `IsUiReady == true`；`MarkUiReady()` 由 `FormMain` 在全部子页面实例化后调用一次。未就绪的初始化步留在本步按拍重试，禁 `Sleep` |
| 运行态门控 | 历史/追溯类数据查询前必须 `IsAppRunning == true`；`MarkAppRunning()` 由 `FormMain` 在首次 `Shown` 的设备初始化 Modal 关闭后调用一次。⛔ 不得用 `Visible` / `FindForm().Visible` / `Created` / `IsHandleCreated` 充当「初始化完成」判据——AntdUI 非当前 `TabPage` 恒为 `Visible=true`（2026-11-09 运行期实测） |

详见 [[lessons/StartupInitializationOrderGates]] 与 [[decisions/ADR-074-RsiNumericProtocolImplementation]] 决策 8。

## 使用规范

- 所有模块通过 GlobalCommData 进行跨模块通信
- 事件处理必须检查 InvokeRequired（UI 线程安全）
- **系统状态统一由三态模型管理（[[architecture/DeviceControlArchitecture]]）**：模组连接态 `Instance.State`（`SubDeviceState`）+ 焊接过程态 `Instance.WeldStatus`（`SubDeviceWeldStatus`）+ 整机运行态 `DeviceControlWork.Instance.Status`（`MainDeviceStatus`）；UI 通过订阅 `StateChanged` / `WeldStatusChanged` / `StatusChanged` 刷新状态显示
- **日志统一接口：`ShowLog(TAG, message, msgLevel)` 是唯一对外日志接口，所有模块禁止直接调用 `MachineLog.Debug/Info/Error/Warn`**
- **msgLevel 控制文件日志等级映射**：

| msgLevel | 文件日志等级 | UI 颜色 |
|----------|-------------|---------|
| `MessageLevel.Info` | `MachineLog.Info` | 黑色 |
| `MessageLevel.Warning` | `MachineLog.Warn` | 蓝色 |
| `MessageLevel.Error` | `MachineLog.Error` | 红色 |
| `MessageLevel.Debug` | `MachineLog.Debug` | 灰色（**仅 `ShowDebugToUi==true` 时显示**，默认关闭）|

- **Debug 级降噪约定**：轮询/重连/重试等高频过程日志统一用 `MessageLevel.Debug`——界面默认不显示（`ShowDebugToUi` 默认 false，由 `CommunicationManager.ShowDebugLog` INI 开关控制，默认关闭），文件端全量写入。**自动重连轮询自愈循环的结果（含重连成功、启动失败）也降 Debug**，主系统不显示只记录；设备初始化/配置加载/手动操作等一次性行为的结果保留 Info/Error 显示。机器人链路已在 `EnsureRobotChannelHealthy` 与 `KukaRsiComm.Start` 按此落地。
- **通讯日志查看通道（2026-11-17 ADR-106）**：`ShowCommLogForView(source, message)` = 写 `TcpMessageLog` 文件（始终全量）+ 触发 `CommLogViewEvent`。仅 FilebackupPage 订阅该事件并显示到本页 inputLog（页面未打开时不接收，但文件端已记录），不进 MachineLog、不进 MainPage。日志按**行为/结果**二分：行为（RSI 配置装载、线程启停、监听绑定、指令收发、重连过程）走本通道；结果（成败反馈：初始化/重连成败、配置加载成败、启停失败、线程异常）走 `ShowLog`。⛔ `CommunicationCommandReceived` 是指令事件（4 订阅者含 2 Workflow），禁用于日志显示。
- 高频事件参数已类级复用，避免每次调用 `new MessageArgs` 产生 GC 压力
- 所有 static 字段在 static 构造函数中集中初始化（ADR-001）
- 通讯 XML 结构已扩展为 7 个，按设备类型分离：Server/Client/Send/Recive（通用 TCP）+ RobotServer/RobotClient（机器人）+ PLC（PLC 通讯），详见 ADR-025（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）
- 通用以太网通讯实例 `EthernetComm`（`EthernetXmlComm`，2026-09-14 ADR-011 取代旧 `TcpIpComm`）由 `mCommunicationManager` 持有和管理，访问路径为 `GlobalCommData.mCommunicationManager.EthernetComm`
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
- **系统状态枚举与事件参数迁至 `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs`（2026-09-02 ADR-034 三态模型）**
- **`TCPIPComm` 纳入 `CommunicationManager` 管理（沿革：2026-09-14 ADR-011 废弃重写为 `EthernetXmlComm`，访问路径 `mCommunicationManager.EthernetComm`）**
- 删除 `EventTcpInfoHandler`、`EventTcpClientInfoHandler`、`EventLineLaserInfoHandler`、`EventRobotInfoHandler`
- 删除 `ShowTcpMessage`、`ShowTcpClientMessage`、`ShowLaserData`
- 删除 `ServerXdoc`、`ClientXdoc`、`SendXdoc`、`ReciveXdoc`、`ParamConfigXdoc`、`RenderConfigXdoc`
- ~~`TCPIPComm` 已迁移到 `AdaWeldSystem.Comm.Ethernet` 命名空间~~ → **2026-09-14 ADR-011**：废弃重写为 `EthernetXmlComm`（命名空间 `AdaWeldSystem.Comm.Communication.Implementations`），收发 KUKA 风格预定义 XML 文档

## 已知问题

- 与 [[modules/WeldParamControl]] 存在循环依赖
- 与 [[modules/SQLiteDatabase]] 存在循环依赖
- 与 [[modules/FileOperate]] 存在循环依赖

---

*来源：raw/skills/02-Development/GeneralTechSpecialist.md*
