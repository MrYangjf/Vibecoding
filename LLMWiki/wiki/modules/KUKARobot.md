---
title: KUKARobot 模块（已并入 api/KUKARobot）
date: 2026-07-01
updated: 2026-10-21
tags: [模块, KUKA, 机器人, 通讯, RSI, 指针页, 已合并]
source: raw/knowledge/KUKA_OPT
---

# KUKARobot 模块（指针页）

> ⛔ **本页内容 2026-09-17 已并入 [[api/KUKARobot]]**（协议知识节 + 现行契约），本页仅存指针；旧文件沿革（KUKADataTypes/KUKAXMLConfig/KUKARobotManager 删除去向）在 api 页与 [[decisions/ADR-025-CommModuleRefactor]] 均有记载。

**现行实现要点**：RSI = `KukaRsiComm`（UDP，唯一通道，原 RSICommunication）；对外统一经 `CommunicationManager` 门面（`ConnectRobot`/`DisconnectRobot`/`SendRobotData`/`RobotDataReceived`），见 [[api/CommunicationManager]] 与 [[modules/Comm]]。

⛔ **通讯通道唯一为 RSI**（ADR-026）：EthernetKRL / EKI 相关说明已于 2026-10-21 清理，本页与 [[api/KUKARobot]] 均不再保留 EKI 协议内容。

协议原始文档：[KST_RSI_33_zh.pdf](../../raw/knowledge/KUKA_OPT/KST_RSI_33_zh.pdf)
