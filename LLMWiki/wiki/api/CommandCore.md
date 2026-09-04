---
title: API — CommandCore 机器人指令协议（const string，取代 CommandTable）
date: 2026-09-04
tags: [API, 指令协议, 机器人, 主控, CommandCore, ADR-036]
source: AdaWeldSystem/MainDeviceControl/DeviceStateApiCore/CommandCore.cs
---

# API — CommandCore 机器人指令协议

> **本页述 `CommandCore`（静态常量类，机器人指令协议）**，ADR-036 裁定 C3，2026-09-04 落地。
>
> **位置**：`AdaWeldSystem/MainDeviceControl/DeviceStateApiCore/CommandCore.cs`
> **命名空间**：`AdaWeldSystem.MainDeviceControl.DeviceState`（⚠️ 目录 `DeviceStateApiCore/` 下的类分属 `...DeviceState` 与 `...FlowState` 两个命名空间，禁止新增 `...DeviceStateApiCore`）
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
| `TxOK` | `TX_OK` | 设备就绪 / 跟踪 OK，反馈机器人继续 |
| `TxAbort` | `TX_ABORT` | 急停 / 中止 |

---

## 公共函数

| 成员 | 签名 | 说明 |
|---|---|---|
| `Normalize` | `static string Normalize(string raw)` | 去空白 + `ToUpperInvariant`；null/空白返回 `string.Empty` |
| `IsKnownCommand` | `static bool IsKnownCommand(string raw)` | 命中任一协议常量返回 true（内部先 `Normalize`） |

---

## 消费链路

```
GlobalCommData.CommunicationCommandReceived
    └─ DeviceControlWork.OnCommRecived(sender, msg)
          ├─ CommandCore.Normalize(msg)
          ├─ CommandCore.IsKnownCommand(cmd)? 否 → Warning 丢弃
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

> ⚠️ **`TxGoPreWeld` / `TxGoWeldStart` / `TxGoPreStop` / `TxGoWeldStop` / `TxGoStopSafe` / `TxOK` / `TxGoHome` / `TxGoStartSafe` 当前 0 调用方**——
> 旧的按步下发逻辑（步 10 下发 `CmdGoPreWeld` 等）随内部执行步机制一并删除，
> 待 Preworking / Working 子流程（批次 4.5 / 4.6）落地后重新接入。**这不是死代码，是协议预置**。

---

## 相关页面

- [[api/DeviceControlWork]] — 唯一消费方（指令队列 + `DispatchCommand`）
- [[architecture/DeviceControlArchitecture]] — §3.1 指令协议表、§7.3 指令交互线程
- [[decisions/ADR-036-RawDesignRefinement20260903]] — 裁定 C3（字符串协议 + 不再监控 pose）
- [[guides/Namespace-Compilation]] — 新增 .cs 必须登记 `.csproj`（`CommandCore.cs` 已登记）
