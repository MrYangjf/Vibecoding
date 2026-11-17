---
title: ADR-106 通讯日志查看通道：行为入通讯日志、结果入系统日志
date: 2026-11-17
updated: 2026-11-17
tags: [决策, 通讯, 日志, RSI, UI]
status: accepted
---

# ADR-106 通讯日志查看通道：行为入通讯日志、结果入系统日志

> **决策一句话**：通讯过程（配置/启停/收发）写入通讯日志、仅 FilebackupPage 打开时显示；行为结果（成败反馈）写主系统日志。

## 背景

机器人 RSI 通讯原有日志全部走 `ShowLog`（MachineLog 文件 + MainPage 主系统日志），重连轮询与配置/启停过程会刷屏主界面。业主裁定：

- **通讯日志**记录通讯信息，即 RSI 配置、打开、关闭以及每次交互内容；是否显示由 FilebackupPage 是否打开决定——打开页面才显示，不打开只记录不显示。
- **主系统日志**只保留行为的反馈结果（成功/失败/异常），典型为初始化成功/失败与自动重连连接成功。

既有 `ShowCommunicationLog` 的 UI 显示走 MainPage 且受 `ShowCommLog` 开关控制，不满足"在 FilebackupPage 查看"；`CommunicationCommandReceived` 有 4 个订阅者（含 LineLaserWorkflow、DeviceControlWork 会把消息当通讯指令触发工作流步骤），不可复用。

## 决策

1. 新增 `GlobalCommData.CommLogViewEvent`（`EventHandler<string>`，仅 FilebackupPage 订阅）与 `ShowCommLogForView(source, message)`：写 `TcpMessageLog` 文件（始终全量，对应"不打开只记录"）+ 触发 `CommLogViewEvent`（对应"打开才显示"）；不写 MachineLog、不进 `EventInfoHandler`。
2. 日志按**行为 / 结果**二分：
   - **行为**（过程陈述 → 通讯日志）：配置装载（RSI 通道配置、收发格式已装载、XML 已生成、端口不一致提示）、线程启停（接收/回复线程已启动/已退出、已在运行中、已停止）、监听绑定、指令下发/清除、数据流恢复、接收超时、重连过程（通道未监听、重连失败、重连异常）。
   - **结果**（成败反馈 → 主系统日志）：配置加载成功/失败、监听启动成功/失败、线程异常、停止异常、重连成功、初始化成功/失败。
3. `FilebackupPage` 构造函数订阅 `CommLogViewEvent`、`DisposeComponents` 退订，handler 复用 `AppendLog` 的线程封送（`InvokeRequired` + `Invoke`），带 `[source]` 前缀显示到本页 inputLog。
4. 启动/停止失败的反馈原为 `MessageLevel.Debug`（UI 默认不显示），提为 `MessageLevel.Warning`，确保作为"结果"在主系统可见。
5. 心跳分级 H0~H4 维持现状（设备状态告警，不属于通讯过程）。
6. 修订 `standards/CodeSimplification` ⑤规则4 的日志归属口径：连接 open/close 不再一律归系统日志，按行为/结果二分。

## 备选方案

- 复用 `ShowCommunicationLog` → UI 显示在 MainPage 而非 FilebackupPage，且受 ShowCommLog 开关控制，弃。
- 复用 `CommunicationCommandReceived` 广播 → 4 个订阅者中 2 个 Workflow 会把日志当通讯指令触发步骤，严重逻辑污染，弃。
- 重连日志只写文件不推送界面 → 不满足"打开 FilebackupPage 就显示"，弃。

## 后果

### 正面
- 主系统日志只剩行为反馈结果，重连轮询与配置/启停不再刷屏主界面。
- 通讯过程信息在 FilebackupPage 集中查看，且未打开页面时也全量落 TcpMessageLog 文件，事后可查。
- 新增事件与指令事件隔离，无工作流误触发风险。

### 负面
- 通讯过程故障细节（如接收超时）需打开 FilebackupPage 才能实时看到；主界面只看得到成功/失败的结论。
- 静态事件要求订阅方显式退订，FilebackupPage 已按纪律在 DisposeComponents 退订；后续若新增订阅方须同样处理。
- "行为/结果"的二分依赖调用点的人工判定，新增日志时需按本决策归类。

## 落地

- `Comm/SystemComm/SystemComm.cs`：`CommLogViewEvent` / `ShowCommLogForView`
- `Comm/Communication/CommunicationManager.cs`：配置装载、指令下发、重连过程转通道
- `Comm/Communication/Implementations/KukaRsiComm.cs`：RSI 启停/绑定/收发/异常按二分归位
- `UIDesign/TabPage/FilebackupPage.cs`：订阅/退订/显示 handler
- `standards/CodeSimplification` ⑤规则4（归属口径修订）

### 2026-11-17 · 决策 D1 · 自动重连轮询结果降级 Debug
- **变更**：自动重连轮询结果降级 Debug
- **理由**：业主纠正：轮询自愈循环的结果也不在主系统显示，只记录降级 Debug。撤销上轮把启动失败提到 Warning 的操作
- **影响**：CommManager L794 重连成功 Info→Debug；KukaRsiComm L597/605/619/666 启动失败 Warning→Debug；其余链路（初始化/配置加载/线程异常/

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-102-heartbeat-levels-and-comm-reconnect]]
- [[api/GlobalCommData]]
- [[api/CommunicationManager]]
- [[api/FilebackupPage]]
- [[standards/CodeSimplification]]
