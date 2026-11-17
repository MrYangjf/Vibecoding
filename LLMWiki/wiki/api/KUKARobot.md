---
title: KUKARobot API 参考（KUKA 机器人通讯 · RSI 单一通道现行契约与协议知识）
date: 2026-07-01
updated: 2026-10-21
tags: [API, KUKA, 机器人, 通讯, RSI, UDP, XML, 协议知识, 焊缝跟踪, KukaRsiComm, CommunicationManager, ADR-011, ADR-024, ADR-026, ADR-026, ADR-026, ADR-026]
source: AdaWeldSystem/Comm/Communication/Implementations
---

# KUKARobot API 参考


## 章节导航

- [1. KUKARobotManager](#1-kukarobotmanager)
- [2. RSICommunication](#2-rsicommunication)
- [3. KUKAXMLConfig](#3-kukaxmlconfig)
- [4. KUKADataTypes](#4-kukadatatypes)
- [5. 使用示例](#5-使用示例)
- [6. 协议知识（承继自 modules/KUKARobot，2026-09-17 合并）](#6-协议知识承继自-moduleskukarobot2026-09-17-合并)
- [7. 参考链接](#7-参考链接)

> KUKA 机器人通讯模块 C# API 参考
>
> 命名空间：实现类 `AdaWeldSystem.Comm.Communication.Implementations`（`KukaRsiComm`），门面 `AdaWeldSystem.Comm.Communication.CommunicationManager`（ADR-011 + ADR-005）
> 对应目录：`Comm/KUKARobot/`
> 门面统一入口见 [[api/CommunicationManager]]（`ConnectRobot`/`DisconnectRobot`/`SendRobotData`/`RobotDataReceived` 等机器人门面现归其承载）。

> ⚠️ **2026-09-15 ADR-024 修订**：本页第 1 章的 `KUKARobotManager` 已于 ADR-011 移除（门面并入 `CommunicationManager`）；`KukaRsiComm` 已按 KUKA RSI 3.3 官方语义重写——机器人 12ms 发 `<Rob><RIst/><IPOC>`，本机回复 `<Sen Type="SENTYPE"><Tech T11=功率 T12=送丝/><IPOC/></Sen>`（接收/回复双线程，`SetReplyValues` 写回复值）。新增门面：`UpdateRobotWeldParams(功率, 送丝)`、`SaveRobotRsiXml()`（生成机器人端 `WeldControlConfig.xml`）。下文旧方法签名仅作历史参考。
>
> ⛔ **2026-10-21 ADR-026 修订（RSI 单一通道，EKI/KRL 全面清理）**：~~RSI 与 EKI 互斥双通道~~ → **通讯通道唯一为 RSI**。EthernetKRL / EKI 相关的类、配置、协议说明在本页**整节删除**（不再是有效契约），代码侧清理见 [[decisions/ADR-026-RsiSemanticRewriteAndDualChannel]] §迁移清单第 7 项（`KukaEkiComm` / `EthernetXmlComm` / `RobotCommMode` 分支移除，`RobotCommMode` 固定为 0）。机器人端 XML **每次启动自动生成**（`InitializeRobotComm` → `SaveRobotRsiXml()`）。字段语义：`IP`=机器人 KLI 地址、`HOST_IP`=上位机本机 IP（机器人端 XML CONFIG 节，机器人据此发包）、`CYCLE`=预期周期（超时判定）。
>
> ⛔ **2026-10-21 RSI 指令承载数值化裁定**：~~上行指令走 `DEF_EStr` 字符串通道~~ → **不成立**。KST RSI 3.3 §7.4.2 规定 SEND 段 `TYPE` 仅 `BOOL`/`DOUBLE`/`LONG`（**不含 STRING**），且 `DEF_EStr` 属 §7.4.6 **写入**关键词（只能用于 RECEIVE 侧）。⇒ 上行指令改为数值化 `RxCmd`(LONG) + `RxPayload`(DOUBLE)，下行改为具名元素 `TxCmd`(LONG) / `TxPayload`(DOUBLE) / `TxSeq`(LONG)，不再依赖 `DEF_Tech.*` 内部编号。完整契约见交付目录 `robot-comm-spec/`（`WeldControlConfig.xml` + 信号流三件套（`WeldControl.rsi` / `.rsi.xml` / `.rsi.diagram`） / 双向通讯指令表 xlsx / `RSI部署与联调测试手册.html`（机器人端 5 件套））。
>
> **2026-09-15 增补（通讯周期可配置）**：`KukaRsiComm` 新增 `public int CycleMs { get; set; }`（默认 12；机器人 IPO 模式 12 / IPO_FAST 4，上位机侧为预期值）——`Start()` 设接收套接字超时=2×CycleMs，连续 5 周期（`StallWarnCycles`）无包告警一次（节流，恢复收包复位）。门面新增 `SetRsiCycleMs(int)`（写 `RsiComm.CycleMs` + 持久化 `RobotServerXdoc` 的 `CYCLE` 元素）与只读 `RsiCycleMs`；UI 入口为 `FilebackupPage`「通讯周期」下拉（4/12/24 ms）。
>
> **2026-09-15 增补（ADR-026 Tool 上行 + 配置目录）**：`RsiRobotPacket` 新增 `ToolX/ToolY/ToolZ`（double）——焊接时机器人基于车身坐标计算的工具位置，`ParseRobotPacket` 解析 `<Tool X Y Z>`（节点缺失保持 0 容错），经 `LatestPacket` / `RsiDataReceived` 透出；机器人端 XML（`SaveRobotRsiXml`）SEND 增 `DEF_Tool` 元素，机器人端需在 RSI 信号图把工具数据映射为 Tool 发送对象。**通讯配置目录统一 `Config\Comm\<通道>_XML\`**：`RobotServerXdoc` → `KUKARobot_RSI_XML\RobotServer.xml`、`RobotClientXdoc` → `KUKARobot_EKI_XML\RobotClient.xml`、机器人端 XML → `KUKARobot_RSI_XML\WeldControlConfig.xml`。旧 `Config\XML\` 下通讯文件的搬迁自 2026-09-21 起统一由 `FileOperate/ConfigPathMigrator.cs`（`Program.Main` 首步）承担，原 `MigrateLegacyCommXml()` 已删除。
>
> **2026-09-16 ADR-026 修订（收发格式文档驱动）**：~~组包/解析硬编码于 `BuildReplyXml`/`ParseRobotPacket`~~ → **格式文档驱动**。`RobotServer.xml` 扩展 `SEND_FORMAT`（Rob 包模板，解析依据）/`REPLY_FORMAT`（Sen 包模板，组包依据）两节（上位机一份文档含配置+格式）；机器人端 `SaveRobotRsiXml` 增生成 **`WeldControlSendFormat.xml`**（与 WeldControlConfig.xml 一同拷贝机器人侧）。`RsiPacketFormat`/`RsiFormatElement`/`RsiFormatAttribute` 模型 + `ParseFormatSection`/`LoadPacketFormat`；`KukaRsiComm.SendPacketFormat`/`ReplyPacketFormat` 由 `InitializeRobotComm` 装载，缺失回退内置默认；解析按格式属性顺序绑定 RIst/Tool，组包按占位值约定（`激光功率`/`送丝速度`/`原样回传`/`时间戳`/字面量）；**Tech 属性名固定 T11~T19、T110 十个**。改格式文档即改收发行为（语义绑定外无需改代码）。
>
> ⚠️ **2026-09-15 ADR-026 修订（Tool 上行结构）**：~~SEND 增 `DEF_Tool` 元素~~ → **`DEF_Tool` 非 RSI 3.3 合法关键词**（§7.4.5 关键词表无此词，加载会被控制器拒绝），且 ETHERNET 对象一个输入端只承载一个标量。工具 X/Y/Z 改为 **Tool.X / Tool.Y / Tool.Z 三标量元素映射 ETHERNET 输入端 1/2/3**（INDX 连续编号），机器人端在 WorkVisual RSI 信号图把工具坐标信号接到对应输入端；数据包为属性书写形式 `<Tool X= Y= Z=/>`，与 `ParseRobotPacket` 的 `//Tool` 属性解析天然对齐（解析侧零改动）。机器人端未接线时 ToolX/Y/Z 恒为 0（容错不报错）。

---

> **章节导航**（本页约 800 行，按章节定位再读）：1 KUKARobotManager（历史，已删类·沿革留存）｜2 RSICommunication｜3 KUKAXMLConfig（已并入实现类·沿革留存）｜4 KUKADataTypes｜5 使用示例｜**6 协议知识（6.1 RSI 概念 / 6.2 XML 配置 / 6.3 SEND 关键词 / 6.4 RSI 侧 KRL 调用 / 6.5 错误处理 / 6.6 旧文件沿革 / 6.7 FastIPO+EtherCAT 历史链路）**｜7 参考链接。现行契约以页首 ADR 修订块为准。

## 1. KUKARobotManager

统一管理层，对外提供 KUKA 机器人通讯的简化接口。

```csharp
public class KUKARobotManager : IDisposable
{
    // 属性
    public RSICommunication RSI { get; }
    public bool IsRSIConnected { get; }
    
    // 构造函数
    public KUKARobotManager();
    
    // RSI 方法
    public bool InitializeRSI(string xmlConfigPath);
    public bool StartRSI();
    public bool StopRSI();
    
    // 数据交换
    public KUKARobotData GetCurrentData();
    public void SendCorrectionData(KUKACorrectionData correction);
    
    // 事件
    public event EventHandler<KUKADataReceivedEventArgs> DataReceived;
    public event EventHandler<KUKAConnectionEventArgs> ConnectionStateChanged;
    
    // 释放
    public void Dispose();
}
```

---

## 2. RSICommunication

RSI (Robot Sensor Interface) UDP 实时通讯管理。

```csharp
public class RSICommunication : IDisposable
{
    // 属性
    public bool IsRunning { get; }
    public string RobotIP { get; set; }
    public int RobotPort { get; set; }
    public int LocalPort { get; set; }
    public ulong CurrentIPOC { get; private set; }
    
    // 构造函数
    public RSICommunication();
    public RSICommunication(string robotIP, int robotPort, int localPort);
    
    // 连接管理
    public bool Initialize(string xmlConfigPath);
    public bool Start();
    public bool Stop();
    
    // 数据发送（机器人状态 → 传感器）
    public void SendRobotData(KUKARobotData data);
    
    // 数据接收（传感器修正 → 机器人）
    public KUKACorrectionData ReceiveCorrectionData();
    public bool TryReceiveCorrectionData(out KUKACorrectionData correction, int timeoutMs);
    
    // XML 序列化
    public string SerializeRobotData(KUKARobotData data);
    public KUKACorrectionData DeserializeCorrectionData(string xml);
    
    // 事件
    public event EventHandler<RSIDataEventArgs> DataReceived;
    public event EventHandler<RSIErrorEventArgs> ErrorOccurred;
    
    // 释放
    public void Dispose();
}
```

### 2.1 RSIDataEventArgs

```csharp
public class RSIDataEventArgs : EventArgs
{
    public KUKARobotData RobotData { get; set; }
    public KUKACorrectionData CorrectionData { get; set; }
    public ulong IPOC { get; set; }
    public DateTime Timestamp { get; set; }
}
```

### 2.2 RSIErrorEventArgs

```csharp
public class RSIErrorEventArgs : EventArgs
{
    public string ErrorMessage { get; set; }
    public Exception Exception { get; set; }
    public RSIErrorType ErrorType { get; set; }
}
```

### 2.3 RSIErrorType

```csharp
public enum RSIErrorType
{
    ConnectionFailed,
    IPOMismatch,
    XMLSerializationError,
    XMLDeserializationError,
    NetworkTimeout,
    Unknown
}
```

---

## 3. KUKAXMLConfig

XML 配置生成与解析。（2026-09-14 起为 **partial class**：RSI 半边居 `KukaRsiComm.cs`，类型名与命名空间不变）

```csharp
public static partial class KUKAXMLConfig
{
    // RSI XML 配置生成
    public static string GenerateRSIXML(RSIConfig config);
    public static RSIConfig ParseRSIXML(string xmlContent);
    
    // 配置文件保存/加载
    public static void SaveRSIConfig(string filePath, RSIConfig config);
    public static RSIConfig LoadRSIConfig(string filePath);
}
```

### 3.1 RSIConfig

```csharp
public class RSIConfig
{
    public string IPNumber { get; set; }
    public int Port { get; set; }
    public string SenType { get; set; }
    public bool OnlySend { get; set; }
    public List<RSIElement> SendElements { get; set; }
    public List<RSIElement> ReceiveElements { get; set; }
}
```

### 3.2 RSIElement

```csharp
public class RSIElement
{
    public string Tag { get; set; }
    public RSIDataType Type { get; set; }
    public string Index { get; set; }    // "1"~"64" 或 "INTERNAL"
    public int HoldOn { get; set; }      // 0 或 1，仅 RECEIVE
}
```

### 3.3 RSIDataType

```csharp
public enum RSIDataType
{
    BOOL,
    DOUBLE,
    LONG,
    STRING
}
```

## 4. KUKADataTypes

数据结构定义。（2026-09-14 起独立文件移除：RSI 侧类型并入 `KukaRsiComm.cs`、管理层事件参数并入 `CommunicationManager.cs`，类型名与命名空间不变）

### 4.1 KUKARobotData

机器人状态数据（RSI 发送方向）。

```csharp
public class KUKARobotData
{
    // 笛卡尔位置
    public KUKAPosition RIst { get; set; }     // 实际位置
    public KUKAPosition RSol { get; set; }     // 额定位置
    
    // 轴位置
    public double[] AIPos { get; set; }        // A1-A6 实际位置 [6]
    public double[] ASPos { get; set; }        // A1-A6 额定位置 [6]
    public double[] EIPos { get; set; }        // E1-E6 实际位置 [6]
    public double[] ESPos { get; set; }        // E1-E6 额定位置 [6]
    
    // 电机电流
    public double[] MACur { get; set; }        // A1-A6 电机电流 [6]
    public double[] MECur { get; set; }        // E1-E6 电机电流 [6]
    
    // 技术参数
    public double[] TechC { get; set; }        // 主进技术参数 C1-C6 [6]
    public double[] TechT { get; set; }        // 预进技术参数 T1-T6 [6]
    
    // 状态
    public long Delay { get; set; }            // 延迟数据包数量
    public string EStr { get; set; }           // 提示/故障信息
    public ulong IPOC { get; set; }            // 时间戳
}
```

### 4.2 KUKACorrectionData

传感器修正数据（RSI 接收方向）。

```csharp
public class KUKACorrectionData
{
    // 笛卡尔修正
    public KUKAPosition RKorr { get; set; }    // X, Y, Z, A, B, C
    
    // 轴修正
    public double[] AK { get; set; }           // A1-A6 [6]
    public double[] EK { get; set; }           // E1-E6 [6]
    
    // 数字输出
    public long DiO { get; set; }
    
    // 时间戳（必须与发送的 IPOC 一致）
    public ulong IPOC { get; set; }
}
```

### 4.3 KUKAPosition

笛卡尔位姿。

```csharp
public struct KUKAPosition
{
    public double X { get; set; }
    public double Y { get; set; }
    public double Z { get; set; }
    public double A { get; set; }    // 绕 Z 轴旋转
    public double B { get; set; }    // 绕 Y 轴旋转
    public double C { get; set; }    // 绕 X 轴旋转
    
    public KUKAPosition(double x, double y, double z, double a, double b, double c);
}
```

### 4.4 KUKAFrame

坐标系（位姿六元组结构）。

```csharp
public struct KUKAFrame
{
    public double X { get; set; }
    public double Y { get; set; }
    public double Z { get; set; }
    public double A { get; set; }
    public double B { get; set; }
    public double C { get; set; }
    
    public KUKAFrame(double x, double y, double z, double a, double b, double c);
}
```

---

## 5. 使用示例

### 5.1 RSI 实时修正通讯

```csharp
// 创建 RSI 通讯实例
var rsi = new RSICommunication("192.168.1.10", 49152, 49153);

// 初始化并启动
rsi.Initialize(@"C:\KRC\ROBOTER\Config\User\Common\SensorInterface\RSI_Ethernet.xml");
rsi.Start();

// 订阅数据接收事件
rsi.DataReceived += (s, e) =>
{
    // 处理传感器返回的修正数据
    var correction = e.CorrectionData;
    Console.WriteLine($"修正: X={correction.RKorr.X}, Y={correction.RKorr.Y}");
};

// 发送机器人状态（通常在循环中）
var robotData = new KUKARobotData
{
    RIst = new KUKAPosition(1000, 200, 300, 0, 90, 0),
    IPOC = rsi.CurrentIPOC
};
rsi.SendRobotData(robotData);

// 停止
rsi.Stop();
rsi.Dispose();
```

### 5.3 统一管理层使用

```csharp
// 使用 KUKARobotManager 统一管理
using (var manager = new KUKARobotManager())
{
    // 初始化 RSI（唯一通道）
    manager.InitializeRSI(@"Config\RSI_Ethernet.xml");
    manager.StartRSI();
    
    // 订阅事件
    manager.DataReceived += (s, e) =>
    {
        Console.WriteLine($"收到数据: {e.RobotData}");
    };
    
    // 发送修正
    manager.SendCorrectionData(new KUKACorrectionData
    {
        RKorr = new KUKAPosition(0.5, 0.2, 0, 0, 0, 0)
    });
}
```

---

## 6. 协议知识（承继自 modules/KUKARobot，2026-09-17 合并）

> 原协议知识页 `modules/KUKARobot` 已于 2026-09-17 并入本节并收缩为指针页；报文周期、IPOC、CYCLE 超时、Tool 映射等与上方 ADR 修订块重叠的内容不再重复，以修订块为准。
>
> **历史名称提示（ADR-011）**：本节原文所引旧文件——`KUKARobotManager.cs`（已移除，门面并入 `CommunicationManager.cs`）、`RSICommunication.cs`（现役 `KukaRsiComm.cs`）、`KUKADataTypes.cs` / `KUKAXMLConfig.cs`（文件已移除：RSI 数据结构与 RSIConfig 并入 `KukaRsiComm.cs`、管理层事件参数并入 `CommunicationManager.cs`；`KUKAXMLConfig` 改为 **partial class**，类型名与命名空间不变）——删除去向亦见 [[decisions/ADR-025-CommModuleRefactor]]。
>
> 模块定位：KUKARobot 是通讯模块 [[modules/Comm]] 的子模块，负责与 KUKA KR C4 机器人控制系统双向数据交换——**RSI**：基于 UDP/IP 的实时传感器接口（唯一通道），12ms 周期内承载位姿上行、指令上下行与焊接参数下行。
>
> 协议原始文档：[KST_RSI_33_zh.pdf](../../raw/knowledge/KUKA_OPT/KST_RSI_33_zh.pdf)、[KST_Ethernet_KRL_22_zh.pdf](../../raw/knowledge/KUKA_OPT/KST_Ethernet_KRL_22_zh.pdf)

### 6.1 RSI 核心概念

| 概念 | 说明 |
|------|------|
| RSI 容器 (Container) | 信号流配置的运行时载体，通过 `RSI_CREATE()` 加载 |
| RSI 上下文 (Context) | 信号处理的执行环境，通过 `RSI_ON()` / `RSI_OFF()` 控制 |
| RSI 对象 (Object) | 信号流中的功能节点（如 ETHERNET、ANIN、POSCORR、AXCORR 等） |
| 信号流 (Signal Flow) | 通过 RSI Visual 配置的图形化数据处理流程，保存为 `.rsi` 文件 |
| IPOC | 时间戳机制，用于校验数据包时序一致性（现行收发方向与时序契约以上方 ADR-024 修订块为准） |

### 6.2 RSI XML 配置结构与关键属性

机器人端 RSI XML（如 `RSI_Ethernet.xml`）结构骨架：

```xml
<ROOT>
  <CONFIG>
    <IP_NUMBER>172.1.10.5</IP_NUMBER>
    <PORT>49152</PORT>
    <SENTYPE>ImFree</SENTYPE>
    <ONLYSEND>FALSE</ONLYSEND>
  </CONFIG>
  <SEND>
    <ELEMENTS>
      <!-- 发送给传感器的数据 -->
      <ELEMENT TAG="DEF_RIst" TYPE="DOUBLE" INDX="INTERNAL" />
      <ELEMENT TAG="DEF_AIPos" TYPE="DOUBLE" INDX="INTERNAL" />
      <ELEMENT TAG="DEF_MACur" TYPE="DOUBLE" INDX="INTERNAL" />
    </ELEMENTS>
  </SEND>
  <RECEIVE>
    <ELEMENTS>
      <!-- 从传感器接收的数据 -->
      <ELEMENT TAG="RKorr.X" TYPE="DOUBLE" INDX="1" HOLDON="1" />
      <ELEMENT TAG="RKorr.Y" TYPE="DOUBLE" INDX="2" HOLDON="1" />
      <ELEMENT TAG="RKorr.Z" TYPE="DOUBLE" INDX="3" HOLDON="1" />
      <ELEMENT TAG="RKorr.A" TYPE="DOUBLE" INDX="4" HOLDON="1" />
      <ELEMENT TAG="RKorr.B" TYPE="DOUBLE" INDX="5" HOLDON="1" />
      <ELEMENT TAG="RKorr.C" TYPE="DOUBLE" INDX="6" HOLDON="1" />
    </ELEMENTS>
  </RECEIVE>
</ROOT>
```

> 注：RECEIVE 段的 `RKorr.*` 示例为 ADR-024 之前的旧「传感器修正」方向骨架，现行接收语义（Tech T11/T12 等、格式文档驱动）以上方 ADR-024/054/055 修订块为准；CONFIG/SEND/RECEIVE 段结构与属性语义仍有效。

**CONFIG 段：**

| 元素 | 说明 | 范围 |
|------|------|------|
| IP_NUMBER | 传感器系统 IP 地址 | - |
| PORT | 传感器系统端口号 | 1 … 65534 |
| SENTYPE | 传感器标记（自由命名）| - |
| ONLYSEND | 数据交换方向 | TRUE=仅发送, FALSE=收发 |

**SEND/RECEIVE 段：**

| 属性 | 说明 | 可选值 |
|------|------|--------|
| TAG | XML 元素名称 | - |
| TYPE | 数据类型 | BOOL, DOUBLE, LONG, STRING |
| INDX | 对象输入/输出端编号或 INTERNAL 关键词 | 1…64 或 INTERNAL |
| HOLDON | 过晚数据包处理方式（仅 RECEIVE）| 0=重置, 1=保持 |

### 6.3 SEND 段 INTERNAL 读取功能关键词

| 关键词 | 数据类型 | 说明 |
|--------|---------|------|
| DEF_RIst | DOUBLE | 笛卡尔实际位置 |
| DEF_RSol | DOUBLE | 笛卡尔额定位置 |
| DEF_AIPos | DOUBLE | 轴 A1-A6 实际位置 |
| DEF_ASPos | DOUBLE | 轴 A1-A6 额定位置 |
| DEF_EIPos | DOUBLE | 附加轴 E1-E6 实际位置 |
| DEF_ESPos | DOUBLE | 附加轴 E1-E6 额定位置 |
| DEF_MACur | DOUBLE | 轴 A1-A6 电机电流 |
| DEF_MECur | DOUBLE | 附加轴 E1-E6 电机电流 |
| DEF_Delay | LONG | 太晚到达的数据包数量 |
| DEF_Tech.C1~C6 | DOUBLE | 主进中的技术参数 |
| DEF_Tech.T1~T6 | DOUBLE | 预进中的技术参数 |
| DEF_EStr | STRING | 提示或故障信息 |

### 6.4 RSI 侧 KRL 调用概览与修正模式

| 指令 | 功能 | 说明 |
|------|------|------|
| RSI_CREATE() | 初始化 RSI 容器 | 加载 .rsi 信号流配置 |
| RSI_ON() | 激活信号处理 | 参数 #RELATIVE 或 #ABSOLUTE |
| RSI_OFF() | 关闭信号处理 | - |
| RSI_MOVECORR() | 传感器引导运动 | 激活修正运动 |
| RSI_DELETE() | 删除 RSI 容器 | - |
| RSI_RESET() | 重置所有 RSI 对象 | - |
| RSI_ENABLE() | 启用 RSI 对象 | - |
| RSI_DISABLE() | 停用 RSI 对象 | - |
| RSI_GETPUBLICPAR() | 读取对象参数 | - |
| RSI_SETPUBLICPAR() | 设置对象参数 | - |

**修正类型：**
- **POSCORR**：笛卡尔修正（X, Y, Z, A, B, C）
- **AXCORR**：轴相关修正（A1-A6, E1-E6）

**修正模式（RSI_ON 参数）：**
- **#ABSOLUTE**：绝对修正（传感器给出绝对目标位置）
- **#RELATIVE**：相对修正（传感器给出相对偏移量）

典型 KRL 程序结构（历史参考——RKorr 修正方向，现行数据方向见上方 ADR-024 修订块）：

```krl
DEF RSI_Example()
  DECL INT ret
  
  ; 创建 RSI 上下文
  ret = RSI_CREATE("RSI_Ethernet.rsi", CONTID, TRUE)
  IF (ret <> RSIOK) THEN
    HALT
  ENDIF
  
  ; 激活信号处理（相对修正模式）
  ret = RSI_ON(#RELATIVE)
  IF (ret <> RSIOK) THEN
    HALT
  ENDIF
  
  ; 传感器引导运动
  RSI_MOVECORR()
  
  ; 关闭信号处理
  ret = RSI_OFF()
  IF (ret <> RSIOK) THEN
    HALT
  ENDIF
END
```

### 6.5 RSI 单一通道与 EKI/KRL 清理说明

⛔ **2026-10-21 ADR-026 裁定：通讯通道唯一为 RSI**，EthernetKRL / EKI 协议说明在本页**整节删除**——它不再是有效契约，保留只会诱导后续实现按已废弃的通道写代码。

RSI 单一通道的要素（现行唯一）：

| 维度 | 现行（RSI 唯一） |
|---|---|
| 传输 | UDP，IPO 周期级（12ms / 4ms） |
| 数据格式 | XML 固定结构：上行 `<Rob>` / 下行 `<Sen>` |
| 指令方向 | 数值码：`RxCmd`/`RxPayload` 上行、`TxCmd`/`TxPayload`/`TxSeq` 下行（**2026-10-22**：TX 8=`TX_NG` 焊接异常停止；`TX_OK` 废止，机器人侧不再等待焊前 OK 应答） |
| 机器人侧配置 | `SensorInterface\WeldControlConfig.xml`（以太网连接 XML）+ 信号流三件套 `WeldControl.rsi` / `WeldControl.rsi.xml` / `WeldControl.rsi.diagram` |
| 修正能力 | 支持实时轨迹修正（POSCORR / AXCORR） |

> **角色澄清（2026-10-22）**：RSI 为**机器人主动发包**模型——机器人 = 客户端/主动方，上位机 = **UDP 服务端/监听方**（绑定 `HOST_PORT`，回复发往收包远端端点）。UDP 无连接态：「监听已开启」≠「机器人在线」；在线判据 = 收到过包且最近一包在 `max(5×CYCLE, 500ms)` 内。

> **监听绑定（2026-10-22）**：`KukaRsiComm.Start()` 绑定 **`HOST_IP` 具体地址**（不再 `0.0.0.0`）。绑定前枚举本机网口：IP 未分配 ⇒ 失败原因只写 **`本机未找到该 IP`**（不再罗列全部本机 IPv4）；网口存在但非 Up ⇒ `网口 X 状态 Down（未启用/未连接）`；绑定异常 ⇒ `RSI 监听绑定失败 地址 … 错误码 … 原因 …`。失败原因统一落 **`KukaRsiComm.LastError`** 并同时写系统日志，返回 false。**没有对应网口不会出现“假监听”**。

RSI 侧硬约束（KST RSI 3.3）：
- §7.4.2 **SEND 段 `TYPE` 仅 `BOOL`/`DOUBLE`/`LONG`（不含 STRING）**；§7.4.3 RECEIVE 段普通元素同此。
- §7.4.4 TAG 含 `.` → 属性形式（`<Tool X="…"/>`）；不含 `.` → 元素形式（`<RxCmd>4</RxCmd>`）。
- §7.4.5 读取关键词：`DEF_RIst` / `DEF_RSol` / `DEF_AIPos` / `DEF_ASPos` / `DEF_EIPos` / `DEF_ESPos` / `DEF_MACur` / `DEF_MECur` / `DEF_Delay`。
- §7.4.6 写入关键词：`DEF_Tech.C1..C6` / `DEF_Tech.T1..T6` / `DEF_EStr`——**只能用于 RECEIVE 侧**。
- `INDX` 连续编号：SEND = ETHERNET 输入端 1…64，RECEIVE = 输出端 1…64。

⛔ 编码侧的连带清理（迁移清单第 7 项）：多通道切换分支与备用通道实现类移除，UI 通讯页去除多通道选择项，连接态判定并入 RSI。

#### 6.5.1 上位机运行时行为（2026-10-21 复核落地）

| 环节 | 现行实现 |
|---|---|
| 收包解析 | `ReceiveLoop` 调 `ParseRobotPacket(xml, SendPacketFormat)`——**按装载的格式文档解析**；文本节点按元素名分派（`IPOC`→`Ipoc`、`RxCmd`→long、`RxPayload`→double），不得统一当 IPOC |
| 回复时机 | **一包一回**：收包线程置位 `_replySignal`，回复线程醒后取回复缓存组 `Sen` 包并回传**同帧 IPOC**；不再以 1ms 盲发 |
| 格式契约 | `InitializeRobotComm` 先 `EnsureRsiFormatSections` 校验必备元素；旧 Tech 节（缺 `WeldPower`/`TxCmd`）原地升级为具名元素契约 |
| 上行去重 | `DeviceControlWork.OnRobotDataReceived` 按 `RxCmd` 变化沿处理（`0` 复位沿），机器人保持 ≥3 IPO 周期不会重复入队 |
| 端口 | 机器人端 XML `CONFIG.PORT` = 本机监听 `PORT`；`HOST_PORT` 仅核对，不一致时告警 |
| 开关 | 取消“启用机器人通讯”即 `DisconnectRobot()`，不再后台收包 |

### 6.6 常见错误与处理

| 错误码/现象 | 原因 | 解决方案 |
|------------|------|---------|
| RSI: 时间戳不一致 | 传感器返回的 IPOC 与发送不匹配 | 检查传感器程序是否正确回传 IPOC |
| RSI: 数据包延迟 | 网络拥塞或传感器处理慢 | 优化网络配置或降低发送频率 |
| RSI: 元素类型被拒 | SEND 段写了 STRING / 用了 `DEF_EStr` | 按 §7.4.2 / §7.4.6 修正类型与关键词归属 |
| RSI: 包全部无效 | IPOC 未原样回传 | 检查 Sen 组包是否透传 Rob 的 IPOC |
| RSI: 上行指令恒为 0 | SEND_FORMAT 缺 `RxCmd`/`RxPayload`，或解析把文本节点一律当 IPOC | 核对 `SEND_FORMAT` 必备元素（启动时自动升级）；解析按标签分派 |
| RSI: 同一指令执行多次 | 未做变化沿去重（机器人保持 ≥3 个 IPO 周期） | 在 `DeviceControlWork.OnRobotDataReceived` 按 `RxCmd` 变化沿处理 |

### 6.7 旧文件沿革与依赖关系

- `KUKAXMLConfig`（partial class）底层 DOM 操作统一调用 [[modules/FileOperate]] 的 `XdocumentReaderWriter` 通用方法（`AddElement`、`GetElementByPath`、`GetAttributeValue` 等），不再直接 `new XDocument`/`new XElement`
- 依赖 [[modules/Comm]] 的全局通讯基础设施（`GlobalCommData.ShowLog`）
- 可能被 [[modules/DeviceControl]] 调用（焊接工作流中的机器人控制步骤）
- 可能被 [[modules/WeldParamControl]] 调用（焊缝跟踪修正数据传递）

### 6.8 RSI FastIPO + EtherCAT 从站（历史链路参考）

> **决策依据**：[[decisions/ADR-027-MotionControllerDeltaReplacement]]（现行运控 = 台达 EtherCAT；原 RSI-CAMBOX 决策已随正运动移除，见 ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]））
> **详细设计**：[[architecture/DeviceControlArchitecture]]
> **核心用途**：为焊缝跟踪提供硬件级同步的主轴位置数据（台达侧承接方案 OPEN：ECAM2 / 虚拟轴 + GearIn / PVT）

链路特性：

| 维度 | 实现 |
|------|------|
| 传输方式 | EtherCAT PDO |
| 实时性 | 4ms 硬实时，抖动 < 100μs |
| 数据路径 | 运动内核 IPO → EtherCAT 从站 TxPDO |
| 延迟 | 1 个 IPO 周期（最小延迟） |
| 数据格式 | 二进制 PDO（REAL32 + UINT32） |
| PC 角色 | 只读监听（不参与实时链路） |

**FastIPO 模式**：RSI 的特殊模式，数据**直接从运动内核 IPO 插补器输出**——不经过 KRL、不经过 SPS、不经过 RSI 容器处理；延迟最小、抖动最小，是 RSI 能达到的最高实时等级。用途：焊缝跟踪主轴直接使用机器人进给位置，其精度与实时性直接决定跟踪精度，FastIPO 的超前位置数据天然补偿机械滞后。

**EtherCAT 从站模式**（设备控制架构中机器人配置为 EtherCAT 从站）：

```
正运动 ZMC（EtherCAT 主站）
    │
    ├─ 从站 1：KUKA 机器人（TxPDO: ToolRelX + TimeStamp）
    ├─ 从站 2：Y 轴伺服驱动器
    └─ ... 其他从站
```

TxPDO 数据定义（机器人 → 正运动）：

| 信号 | 类型 | 字节 | 说明 |
|------|------|------|------|
| `ToolRelX` | REAL32 | 4 | Tool 坐标系 X 方向相对焊接起点的行进位移（mm） |
| `TimeStamp` | UINT32 | 4 | 机器人运动内核高精度时间戳（μs） |
| **合计** | — | **8 字节** | — |

为什么用 EtherCAT 而不是 UDP：**硬件级同步**（分布式时钟 DC 亚微秒级同步）、**确定性**（PDO 周期固定，无网络拥塞/重传/抖动）、**零 CPU 开销**（数据直接映射控制器内存，不经协议栈）、**直接做编码器轴**（正运动 ATYPE=25 可将 PDO 数据直接映射为编码器位置）。

**ToolRelX 坐标系**：机器人 Tool 坐标系下 X 方向位移，相对于焊接起始点（`G_WELD_TOOL_START`），纯进给量、不受机器人姿态旋转影响，单位 mm。与 `$POS_ACT` 的区别：`$POS_ACT` 是笛卡尔空间绝对位置、受姿态影响；`ToolRelX` 只反映进给进度——焊缝跟踪只关心"焊枪走了多远"，ToolRelX 是最直接的表达。

KRL 焊接启停逻辑：

```krl
GLOBAL FRAME G_WELD_TOOL_START
GLOBAL BOOL G_WELD_IN_PROGRESS

; ===== 焊接启动 =====
G_WELD_TOOL_START = $POS_ACT_TCP_RSI  ; 记录起始 Tool 坐标系
G_WELD_IN_PROGRESS = TRUE
RSI_START_FASTIPO()                    ; 启动 FastIPO + EtherCAT TxPDO

; ===== 焊接结束 =====
RSI_STOP_FASTIPO()                     ; 停止 FastIPO
G_WELD_IN_PROGRESS = FALSE
```

PC 端数据接收：实时链路完全在 EtherCAT 总线上，PC 不直接从机器人接收实时 RSI 数据。PC 获取机器人位置的两种方式（均不参与实时运动控制，仅用于监控和显示）：①从正运动控制器读取——`EncoderAxis.GetCurrentPosition()` 读取 ATYPE=25 轴当前位置（UI 显示与状态监控）；②非实时查询——通过上位机主动轮询（配置管理、状态查询）。

历史组件职责（文件路径为 ADR-011 重构前旧路径，现役归属见本节历史名称提示）：

| 组件 | 旧路径 | 职责 |
|------|------|------|
| `RSICommunication` | `Comm/Robot/KUKARobot/RSICommunication.cs` | RSI UDP/XML 实时通讯。保留但非默认链路——实时主轴数据改由 EtherCAT PDO 直连正运动控制器，本组件作为备用/调试通道 |
| ~~`EKICommunication`~~ | ~~`Comm/Robot/KUKARobot/EKICommunication.cs`~~ | ⛔ **已废弃**（ADR-026：通讯通道唯一为 RSI），代码待清理 |
| `KUKADataTypes` | 并入 `KukaRsiComm.cs` / `CommunicationManager.cs` | 机器人数据结构，含 ToolRelX + 时间戳结构 |
| `KUKARobotManager` | 门面并入 `CommunicationManager.cs` | 统一管理 RSI（已移除，经 Manager 门面访问） |

> **实装状态**：CAMBOX 跟踪链路三组件（`EncoderAxis` / `CamBoxTracker` / `RSIPositionBuffer`）与 `MotionControlWorkflow` 编排均已落地；**KUKA 侧 RSI FastIPO + EtherCAT 从站配置需现场联调**，PLC/机器人点位待标定。

## 7. 参考链接

- 本页即原 modules/KUKARobot 承继页（协议知识节 + 现行契约），原页已收缩为指针页（2026-09-17 合并）
- [[modules/Comm]] —— 通讯总线模块
- 机器人端 RSI 配置与联调交付物：`robot-comm-spec/`（机器人端 5 件套：`WeldControl.rsi` / `.rsi.xml` / `.rsi.diagram` / `WeldControlConfig.xml` / `.src` + 通讯指令表 xlsx + `RSI部署与联调测试手册.html`）
- [[api/GlobalCommData]] —— 全局数据通讯中心

---

> 本 API 参考基于 KUKA.RobotSensorInterface 3.3 文档编制。Ethernet KRL / EKI 协议知识已于 2026-10-21 随 ADR-026 清理移除。
> Ingest 时间：2026-07-01
