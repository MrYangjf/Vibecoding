---
title: CodeMap-Relations-Methods-Comm — 代码地图·方法级影响面·Comm（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-Comm — 方法级影响面（低置信 · 调用方在 Comm）

> **一句话**：**调用方位于 `Comm` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 59 |
| 调用点数 | 67 |

## 章节导航

- [BuildReplyFormatElement](#BuildReplyFormatElement)
- [BuildReplyXml](#BuildReplyXml)
- [BuildSendFormatElement](#BuildSendFormatElement)
- [BuildXmlDocument](#BuildXmlDocument)
- [CheckReceiveStall](#CheckReceiveStall)
- [Close](#Close)
- [ConnectClient](#ConnectClient)
- [ConnectRobot](#ConnectRobot)
- [CreateTextElement](#CreateTextElement)
- [Disconnect](#Disconnect)
- [DisconnectClient](#DisconnectClient)
- [EnsureConfigElementExists](#EnsureConfigElementExists)
- [EnsureConnected](#EnsureConnected)
- [EnsureElementExists](#EnsureElementExists)
- [EnsureRobotServerConfigSection](#EnsureRobotServerConfigSection)
- [EnsureRsiFormatSections](#EnsureRsiFormatSections)
- [Execute](#Execute)
- [GenerateRSIXML](#GenerateRSIXML)
- [GetAttrByIndex](#GetAttrByIndex)
- [GetElementBool](#GetElementBool)
- [GetElementInt](#GetElementInt)
- [GetElementValue](#GetElementValue)
- [HandleErrorResponse](#HandleErrorResponse)
- [HasRequiredElements](#HasRequiredElements)
- [HealCommunicationIni](#HealCommunicationIni)
- [Initialize](#Initialize)
- [InitializeDefaultConfigs](#InitializeDefaultConfigs)
- [InitializeRobotComm](#InitializeRobotComm)
- [InitializeXmlDocuments](#InitializeXmlDocuments)
- [IsDuplicateWithinSecond](#IsDuplicateWithinSecond)
- [IsLocalAddressReady](#IsLocalAddressReady)
- [Load](#Load)
- [Log](#Log)
- [OnConnected](#OnConnected)
- [OnDisconnected](#OnDisconnected)
- [OnErrorOccurred](#OnErrorOccurred)
- [Open](#Open)
- [ParseDouble](#ParseDouble)
- [ParseFormatSection](#ParseFormatSection)
- [ParseRSIXML](#ParseRSIXML)
- [ParseRobotPacket](#ParseRobotPacket)
- [ReadExact](#ReadExact)
- [ResolvePlaceholder](#ResolvePlaceholder)
- [Save](#Save)
- [SaveRobotRsiXml](#SaveRobotRsiXml)
- [Send](#Send)
- [SendRobotCommand](#SendRobotCommand)
- [SendRobotCommandByName](#SendRobotCommandByName)
- [Start](#Start)
- [Stop](#Stop)
- [StopServer](#StopServer)
- [ToDegree](#ToDegree)
- [ToFirmwareVersion](#ToFirmwareVersion)
- [ToMillimeter](#ToMillimeter)
- [ToPercent](#ToPercent)
- [ToTemperature](#ToTemperature)
- [TryDeleteTempFile](#TryDeleteTempFile)
- [UpdateRobotPose](#UpdateRobotPose)
- [WriteXmlWithRetry](#WriteXmlWithRetry)

## Log

> 6 处调用 / 6 个调用方文件

- `Comm/Communication/Abstractions/CommChannelBase.cs` — 行 [83, 74]
- `Comm/Communication/CommunicationManager.cs` — 行 [1174, 1138, 1072, 1067, 1046, 1041, 956, 879, 873, 829, 794, 578, 500, 498, 496, 494]
- `Comm/Communication/Implementations/EthernetXmlComm.cs` — 行 [440, 425, 421, 412, 346, 315, 299, 290, 279, 269, 261, 133, 72, 70]
- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [366, 327, 319, 310, 302, 274, 229, 160, 140, 121, 114, 105]
- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [700, 658, 611, 597, 589, 554, 549, 533, 494, 405, 397]
- `Comm/Communication/Implementations/SiemensS7Comm.cs` — 行 [93, 77, 72]

## Disconnect

> 2 处调用 / 2 个调用方文件

- `Comm/Communication/Implementations/EthernetXmlComm.cs` — 行 [68]
- `Comm/Communication/Implementations/SiemensS7Comm.cs` — 行 [188, 66]

## OnErrorOccurred

> 2 处调用 / 2 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [328, 122]
- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [659, 612, 598, 590, 555, 534, 495, 406]

## Send

> 2 处调用 / 2 个调用方文件

- `Comm/Communication/Abstractions/CommChannelBase.cs` — 行 [86]
- `Comm/Communication/Implementations/EthernetXmlComm.cs` — 行 [132]

## BuildReplyFormatElement

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [948, 717, 713]

## BuildReplyXml

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [872, 480]

## BuildSendFormatElement

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [947, 702, 698]

## BuildXmlDocument

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/EthernetXmlComm.cs` — 行 [127]

## CheckReceiveStall

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [393]

## Close

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [329, 147, 94, 85]

## ConnectClient

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/EthernetXmlComm.cs` — 行 [55]

## ConnectRobot

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [791]

## CreateTextElement

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [1221, 1220, 1219, 1218, 1217, 1216, 1215, 1214]

## DisconnectClient

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/EthernetXmlComm.cs` — 行 [61]

## EnsureConfigElementExists

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [389, 388, 387, 386, 385, 384]

## EnsureConnected

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/SiemensS7Comm.cs` — 行 [178, 161, 148, 136, 129, 122, 111]

## EnsureElementExists

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [404, 403, 402, 398, 397, 396, 395]

## EnsureRobotServerConfigSection

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [383]

## EnsureRsiFormatSections

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [564, 391]

## Execute

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [248, 206, 171]

## GenerateRSIXML

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [1429]

## GetAttrByIndex

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [828, 827, 826, 820, 819, 818, 817, 816, 815]

## GetElementBool

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [1130]

## GetElementInt

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [1129, 1128, 1127]

## GetElementValue

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [1232, 1226, 1131, 1126]

## HandleErrorResponse

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [256, 214, 180]

## HasRequiredElements

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [709, 694]

## HealCommunicationIni

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [317]

## Initialize

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [529]

## InitializeDefaultConfigs

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [1139, 1107, 1096]

## InitializeRobotComm

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [790]

## InitializeXmlDocuments

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [321]

## IsDuplicateWithinSecond

> 1 处调用 / 1 个调用方文件

- `Comm/SystemComm/SystemComm.cs` — 行 [116]

## IsLocalAddressReady

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [594]

## Load

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [1079, 322]

## OnConnected

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [116]

## OnDisconnected

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [136]

## Open

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [79]

## ParseDouble

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [838, 833, 828, 827, 826, 820, 819, 818, 817, 816, 815, 806, 802]

## ParseFormatSection

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [1423]

## ParseRSIXML

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [1437]

## ParseRobotPacket

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [754, 351]

## ReadExact

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [316, 299]

## ResolvePlaceholder

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [918, 908]

## Save

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [1204, 1193, 1097]

## SaveRobotRsiXml

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [574]

## SendRobotCommand

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [832]

## SendRobotCommandByName

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [818]

## Start

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [563]

## Stop

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 [931, 569]

## StopServer

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/EthernetXmlComm.cs` — 行 [62]

## ToDegree

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [703]

## ToFirmwareVersion

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [723]

## ToMillimeter

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [701, 699, 697, 695, 693]

## ToPercent

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [709]

## ToTemperature

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/Implementations/InLaserModbusComm.cs` — 行 [713]

## TryDeleteTempFile

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [999, 991]

## UpdateRobotPose

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [610]

## WriteXmlWithRetry

> 1 处调用 / 1 个调用方文件

- `Comm/Communication/CommunicationManager.cs` — 行 [949, 938]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
