---
title: API — CommandCore 机器人指令协议（const string，取代 CommandTable）
date: 2026-09-04
tags: [API, 指令协议, 机器人, 主控, CommandCore, ADR-020]
source: AdaWeldSystem/MainDeviceControl/DeviceStateApiCore/CommandCore.cs
---

# API — CommandCore 机器人指令协议

> **本页述 `CommandCore`（静态常量类，机器人指令协议）**，ADR-020 裁定 C3，2026-09-04 落地。
>
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceStateApiCore/CommandCore.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`（2026-09-14 ADR-005 起命名空间随目录对齐；此前分属 `...DeviceState` / `...FlowState` 的旧写法已废止）
> **取代**：⛔ 已删除的 `CommandTable.cs`（const int + `RobotPose` / `RobotCommand` / `DeviceCommand` / `RobotPoseCode` / `SignalCode` / `InteractionTable` 六件套）
> **落地批次**：批次 0.3 / 0.4，见 [[architecture/DeviceControlArchitecture]] §15.2

## 三条硬约定

1. 机器人指令一律以 **字符串** 解析，**不使用** const int 编码，也不再保留 `RobotPose` / `RobotCommand` / `DeviceCommand` / `RobotPoseCode` 等枚举与映射表。
2. 指令值以 `const string` 固定，**不允许调用方自定义赋值**。
3. **不再监控机器人 pose**——设备运行全靠机器人指令驱动，设备无权限管理机器人状态。

> ⚠️ 指令集沿用旧 `DeviceCommand` / `RobotPose` 的语义落成字符串常量，**具体报文格式待机器人协议细化后对接**；
> 当前消费方（`DeviceControlWork.DispatchCommand`）对位姿类指令一律以 `// todo` 占位、仅记录不驱动流程。

---

## 协议方向标识（原档 R002/R003）

| 常量 | 值 | 说明 |
|---|---|---|
| `ReceiveCommand` | `"RECEIVE"` | 接受指令方向标识（机器人 → 设备）。原档拼写 `ReciveCommand`，按正确英文落地 |
| `SendCommand` | `"SEND"` | 发送指令方向标识（设备 → 机器人） |

## 接收指令（机器人 → 设备）

| 常量 | 值 | 旧语义 |
|---|---|---|
| `RxHomePose` | `RX_HOME_POSE` | 归零位 |
| `RxStartSafePose` | `RX_START_SAFE_POSE` | 进入安全起始位 |
| `RxPreWeldPose` | `RX_PRE_WELD_POSE` | 焊前位 |
| `RxWeldStartPose` | `RX_WELD_START_POSE` | 焊接起始位 |
| `RxPreStopPose` | `RX_PRE_STOP_POSE` | 预停位 |
| `RxWeldStopPose` | `RX_WELD_STOP_POSE` | 焊接停止位 |
| `RxStopSafePose` | `RX_STOP_SAFE_POSE` | 回到安全停止位 |
| `RxPreWeldRequest` | `RX_PRE_WELD_REQUEST` | 请求进入焊前 |
| `RxAbort` | `RX_ABORT` | 急停 / 中止 |

## 下发指令（设备 → 机器人）

| 常量 | 值 | 旧语义 |
|---|---|---|
| `TxGoHome` | `TX_GO_HOME` | 回零 |
| `TxGoStartSafe` | `TX_GO_START_SAFE` | 去安全起始位 |
| `TxGoPreWeld` | `TX_GO_PRE_WELD` | 去焊前位 |
| `TxGoWeldStart` | `TX_GO_WELD_START` | 去焊接起始位 |
| `TxGoPreStop` | `TX_GO_PRE_STOP` | 去预停位 |
| `TxGoWeldStop` | `TX_GO_WELD_STOP` | 去焊接停止位 |
| `TxGoStopSafe` | `TX_GO_STOP_SAFE` | 回安全停止位 |
| `TxNG` | `TX_NG` | **焊接中异常**（2026-10-22 新增，取代 `TX_OK`）：通知机器人停止动作 |
| `TxAbort` | `TX_ABORT` | 急停 / 中止 |

> ⚠️ **新增指令必须同批改三处（2026-10-19 业主约定「严格遵守」，原两处升级为三处）**：
> ① `IsKnownCommand` 的 `||` 硬编码链漏加 ⇒ 该指令被当未知命令丢弃（2026-10-08 实证）；
> ② `CommandDescriptions` 释意字典漏加 ⇒ Dash 机器人指令行显示原始指令串而非中文；
> ③ 本页 api 文档（指令表）同步补行。
> 剪丝的 **RSI 通道**走 `CutWire` 具名元素（`KukaRsiComm.SetReplyValues` 第 3 参），与本表的指令通道**并行独立**，不冲突。
> **2026-10-22 契约修订（机器人侧减指令）**：`TX_OK` 与 `TX_CUT_WIRE` 指令已废止（机器人端不再等待「焊前检查 OK」应答——机器人发下一步指令即默认检查通过；`TxCmd=10` 改为备用）；新增 `TX_NG`（8）供焊接中异常时通知机器人停止。剪丝唯一通道 = `CutWire` 具名元素。
> ⛔ **2026-10-21 ADR-026**：本表指令的传输通道唯一为 RSI 数值码（上行 `RxCmd`/`RxPayload`、下行 `TxCmd`/`TxPayload`/`TxSeq`），EKI 文本通道已退役。

---

## 公共函数

| 成员 | 签名 | 说明 |
|---|---|---|
| `Normalize` | `static string Normalize(string raw)` | 去空白 + `ToUpperInvariant`；null/空白返回 `string.Empty` |
| `IsKnownCommand` | `static bool IsKnownCommand(string raw)` | 命中任一协议常量返回 true（内部先 `Normalize`） |
| `TrySplitPayload` | `static bool TrySplitPayload(string normalized, out string command, out string payload)` | **2026-09-24 新增**：把带坐标载荷的报文拆成「指令名 + 载荷」。报文格式约定（待协议正式细化后替换解析器）：指令名后跟分隔符（空格/逗号/制表）与数值列表，如 `RX_WELD_STOP_POSE,1520.5` 或 `RX_WELD_STOP_POSE 1520.5 300.0`；指令名与数值连写（`RX_WELD_STOP_POSE1520.5`）亦可。整体命中已知指令时 `payload` 为空串；头部非已知指令返回 false |
| `CommandDescriptions` | `static readonly Dictionary<string, string>` | **2026-10-19 新增**：指令 → 中文释意字典（9 Rx + 9 Tx = 18 条，2026-10-22 起 TxOK/TxCutWire 已删、TxNG 已加），供 Dash 机器人指令行显示。⚠️ 新增指令必须同步补条目（三处同步之②） |
| `TranslateCommand` | `static string TranslateCommand(string command)` | **2026-10-19 新增**：指令/报文 → 中文释意。内部先 `Normalize`，再 `TrySplitPayload` 拆出指令头（带载荷报文如 `RX_WELD_STOP_POSE,1520.5` 也能命中字典），查 `CommandDescriptions`，未命中返回原文；空入参返回 `——`。消费方：`MainPage.OnRobotCommandReceived`（Dash 显示） |

---

## 数值码映射（2026-10-21 ADR-074，RSI 数值化协议）

> ⛔ RSI 的 SEND 段 `TYPE` 仅 `BOOL`/`DOUBLE`/`LONG`（不含 `STRING`），且 `DEF_EStr` 属写入关键词
> ⇒ **上行指令必须数值化**。字符串常量（`RX_*` / `TX_*`）保留为日志与 UI 显示载体，**线上承载的是数值码**。

| 上行码 | 指令常量 | 下行码 | 指令常量 |
|---|---|---|---|
| 1 | `RX_HOME_POSE` | 1 | `TX_GO_HOME` |
| 2 | `RX_START_SAFE_POSE` | 2 | `TX_GO_START_SAFE` |
| 3 | `RX_PRE_WELD_POSE` | 3 | `TX_GO_PRE_WELD` |
| 4 | `RX_WELD_START_POSE` | 4 | `TX_GO_WELD_START` |
| 5 | `RX_PRE_STOP_POSE` | 5 | `TX_GO_PRE_STOP` |
| 6 | `RX_WELD_STOP_POSE` | 6 | `TX_GO_WELD_STOP` |
| 7 | `RX_STOP_SAFE_POSE` | 7 | `TX_GO_STOP_SAFE` |
| 8 | `RX_PRE_WELD_REQUEST` | 8 | `TX_NG` |
| 9 | `RX_ABORT` | 9 | `TX_ABORT` |
| — | — | 10 | 备用（不映射） |

| 成员 | 签名 | 职责 |
|---|---|---|
| `RxCodeToCommandName` | `string (int rxCode)` | 上行数值码 → 指令常量名（未命中返回空串） |
| `TxCodeToCommandName` | `string (int txCode)` | 下行数值码 → 指令常量名 |
| `CommandToTxCodeValue` | `int (string command)` | 指令常量名 → 下行数值码（未命中返回 0） |
| `DescribeRxCode` | `string (int rxCode)` | 上行数值码 → 中文释意（调试面板用） |
| `DescribeTxCode` | `string (int txCode)` | 下行数值码 → 中文释意 |

⚠️ 下行码反查表由 `TxCodeToCommand` **反向自动生成**（不两处手写，防不同步）。

---

## 消费链路

```
GlobalCommData.CommunicationCommandReceived
    └─ DeviceControlWork.OnCommRecived(sender, msg)
          ├─ CommandCore.Normalize(msg)
          ├─ CommandCore.IsKnownCommand(cmd) 或 TrySplitPayload 拆头部 → 否则 Warning 丢弃
          ├─ 停止位报文（RX_WELD_STOP_POSE + 数值）→ 解析首个数值 → ApplyRobotStopPose(X) 缓存并改写行程目标
          └─ lock(_commLock) _commCommandQueue.Enqueue(cmd)
                                    ↓
    CommCommandWork 线程 → DequeueCommand() → DispatchCommand(cmd)
```

`DispatchCommand` 现状：

| 指令 | 行为 |
|---|---|
| `RxAbort` | → `EstopMachine("机器人主动急停指令")` |
| `RxPreWeldRequest` | `// todo` 待批次 4.5（Preworking 五项检查）落地后驱动整机进入 `PreWork` |
| `RxHomePose` / `RxStopSafePose` | `// todo` 待整机正常停止链（§7.6 Complete）落地后驱动收尾 |
| 其余 5 个位姿 | 仅记日志（裁定 C3：不再监控 pose） |
| `default` | Warning「收到未处理的机器人指令」 |

下发侧：

| 调用点 | 指令 |
|---|---|
| `DeviceControlWork.EstopMachine` → `EmergencyStop` | `TxAbort` |

> **2026-10-19 演进：Tx 下发同步广播**。`DeviceControlWork.SendRobotCommand` 发送成功后调 `GlobalCommData.BroadcastCommunicationCommand(command)`，
> 使 Dash 机器人指令行同时显示下发（Tx*）指令；接收侧 `OnCommRecived` 对 Tx 指令正常入队，`DispatchCommand` 命中 `default` 返回 null，无业务副作用。
> Rx 侧广播仍由 `EthernetXmlComm.Client_OnDataReceived` 负责。

> ⚠️ **`TxGoPreWeld` / `TxGoWeldStart` / `TxGoPreStop` / `TxGoWeldStop` / `TxGoStopSafe` / `TxGoHome` / `TxGoStartSafe` 当前 0 调用方**——
> 旧的按步下发逻辑（步 10 下发 `CmdGoPreWeld` 等）随内部执行步机制一并删除，
> 待 Preworking / Working 子流程（批次 4.5 / 4.6）落地后重新接入。**这不是死代码，是协议预置**。
> **2026-10-22 现状**：`TxNG` 已有 2 处调用（`DeviceControlWork.ReportAlarm` / `DoMotionBusFault`，均以 `IsWelding` 门控）；`TxAbort` 由 `EmergencyStop` 下发。

---

## 相关页面

- [[api/DeviceControlWork]] — 唯一消费方（指令队列 + `DispatchCommand`）
- [[architecture/DeviceControlArchitecture]] — §3.1 指令协议表、§7.3 指令交互线程
- [[decisions/ADR-035-RawDesignRefinement20260903]] — 裁定 C3（字符串协议 + 不再监控 pose）
- [[guides/Namespace-Compilation]] — 新增 .cs 必须登记 `.csproj`（`CommandCore.cs` 已登记）
