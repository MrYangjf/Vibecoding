# KUKARobot 模块

> KUKA 机器人通讯模块：RSI (Robot Sensor Interface) 实时传感器接口 与 EKI (Ethernet KRL Interface) 以太网数据交换接口
> **章节导航**（本页 570 行，超长页请先按章节定位再读）：
>
> - [1. 模块定位](#1-模块定位)
> - [2. RSI (Robot Sensor Interface)](#2-rsi-robot-sensor-interface)
> - [3. EKI (Ethernet KRL Interface)](#3-eki-ethernet-krl-interface)
> - [4. RSI vs EKI 对比](#4-rsi-vs-eki-对比)
> - [5. 与 AdaWeldSystem 的集成](#5-与-adaweldsystem-的集成)
> - [6. 常见错误与处理](#6-常见错误与处理)
> - [7. RSI FastIPO + EtherCAT 从站](#7-rsi-fastipo-ethercat-从站)
> - [8. 参考链接](#8-参考链接)

>
> 对应目录：`Comm/Robot/KUKARobot/`（由 `Comm/KUKARobot/` 迁入 `Robot/` 子目录）
> 来源：[KST_RSI_33_zh.pdf](../../raw/knowledge/KUKA_OPT/KST_RSI_33_zh.pdf)、[KST_Ethernet_KRL_22_zh.pdf](../../raw/knowledge/KUKA_OPT/KST_Ethernet_KRL_22_zh.pdf)

---

## 1. 模块定位

KUKARobot 是 AdaWeldSystem 通讯模块 [[modules/Comm]] 的子模块，负责与 KUKA KR C4 机器人控制系统进行双向数据交换。该模块支持两种通讯方式：

- **RSI**：基于 UDP/IP 的实时传感器接口，用于毫秒级传感器修正（如焊缝跟踪实时纠偏）
- **EKI**：基于 TCP/IP 的 XML 数据交换，用于非实时数据通讯（如程序控制、状态监控）

---

## 2. RSI (Robot Sensor Interface)

### 2.1 核心概念

| 概念 | 说明 |
|------|------|
| RSI 容器 (Container) | 信号流配置的运行时载体，通过 `RSI_CREATE()` 加载 |
| RSI 上下文 (Context) | 信号处理的执行环境，通过 `RSI_ON()` / `RSI_OFF()` 控制 |
| RSI 对象 (Object) | 信号流中的功能节点（如 ETHERNET、ANIN、POSCORR、AXCORR 等） |
| 信号流 (Signal Flow) | 通过 RSI Visual 配置的图形化数据处理流程，保存为 `.rsi` 文件 |
| IPOC | 时间戳机制，用于校验数据包时序一致性 |

### 2.2 数据交换原理

RSI 通过 **UDP/IP** 协议与外部系统（传感器/上位机）交换 XML 数据：

1. **发送方向**：机器人控制系统 → 传感器系统
   - 机器人状态（实际位置、额定位置、电机电流等）
   - 通过 `<SEND>` 配置的 XML 结构自动发送
   - 自动附加 `<IPOC>` 时间戳

2. **接收方向**：传感器系统 → 机器人控制系统
   - 传感器修正值（笛卡尔修正或轴修正）
   - 通过 `<RECEIVE>` 配置的 XML 结构解析
   - 必须包含与发送一致的 `<IPOC>` 时间戳

### 2.3 XML 配置结构

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

### 2.4 关键属性说明

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

### 2.5 读取功能关键词（SEND 段 INTERNAL）

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

### 2.6 KRL 指令概览

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

### 2.7 修正类型与模式

**修正类型：**
- **POSCORR**：笛卡尔修正（X, Y, Z, A, B, C）
- **AXCORR**：轴相关修正（A1-A6, E1-E6）

**修正模式（RSI_ON 参数）：**
- **#ABSOLUTE**：绝对修正（传感器给出绝对目标位置）
- **#RELATIVE**：相对修正（传感器给出相对偏移量）

### 2.8 典型 KRL 程序结构

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

---

## 3. EKI (Ethernet KRL Interface)

### 3.1 核心概念

| 概念 | 说明 |
|------|------|
| EKI 通道 | 通过 XML 配置文件定义的 TCP/IP 连接 |
| 客户端模式 | EKI 主动连接外部服务器 |
| 服务器模式 | EKI 监听外部客户端连接 |
| 数据存储器 | 接收数据的缓冲存储区（FIFO 或 LIFO）|
| XML 数据交换 | 基于结构化 XML 的数据收发 |
| 原始数据交换 | 基于 BYTE/STREAM 的二进制数据收发 |

### 3.2 数据交换原理

EKI 通过 **TCP/IP** 协议与外部系统交换数据：

1. **连接建立**：`EKI_Init()` 读取配置 → `EKI_Open()` 建立连接
2. **数据发送**：`EKI_Send()` 发送 XML 或二进制数据
3. **数据写入**：`EKI_SetXxx()` 将数据写入发送存储器
4. **数据读取**：`EKI_GetXxx()` 从接收存储器读取数据
5. **连接关闭**：`EKI_Close()` 关闭连接 → `EKI_Clear()` 删除通道

### 3.3 XML 配置文件结构

```xml
<ETHERNETKRL>
  <CONFIGURATION>
    <EXTERNAL>
      <IP>172.1.10.5</IP>
      <PORT>60000</PORT>
      <TYPE>Server</TYPE>  <!-- 或 Client -->
    </EXTERNAL>
    <INTERNAL>
      <ENVIRONMENT>Program</ENVIRONMENT>
      <BUFFERING Mode="FIFO" Limit="10"/>
      <BUFFSIZE Limit="16384"/>
      <TIMEOUT Connect="60000"/>
      <ALIVE Set_Out="666" Ping="200"/>
    </INTERNAL>
  </CONFIGURATION>
  <RECEIVE>
    <XML>
      <ELEMENT Tag="Sensor/Message" Type="STRING"/>
      <ELEMENT Tag="Sensor/Pos/X" Type="REAL"/>
      <ELEMENT Tag="Sensor/Pos/Y" Type="REAL"/>
      <ELEMENT Tag="Sensor/Pos/Z" Type="REAL"/>
      <ELEMENT Tag="Sensor/Status/IsActive" Type="BOOL"/>
    </XML>
  </RECEIVE>
  <SEND>
    <XML>
      <ELEMENT Tag="Robot/Data/LastPos/@X"/>
      <ELEMENT Tag="Robot/Data/LastPos/@Y"/>
      <ELEMENT Tag="Robot/Data/LastPos/@Z"/>
      <ELEMENT Tag="Robot/Status"/>
    </XML>
  </SEND>
</ETHERNETKRL>
```

### 3.4 配置元素说明

**EXTERNAL 段：**

| 元素 | 说明 | 范围/值 |
|------|------|---------|
| IP | 外部系统 IP（客户端模式）| - |
| PORT | 外部系统端口（客户端模式）| 54600 … 54615 |
| TYPE | EKI 运行模式 | Server / Client |

**INTERNAL 段：**

| 元素 | 说明 | 范围/值 |
|------|------|---------|
| ENVIRONMENT | 连接生命周期环境 | Program / Submit / System |
| BUFFERING Mode | 数据存储器模式 | FIFO / LIFO |
| BUFFERING Limit | 存储器数据组数量限制 | - |
| BUFFSIZE Limit | 套接字缓冲区大小 | 字节 |
| TIMEOUT Connect | 连接超时 | 0 … 65534 ms |
| ALIVE Set_Out | 连接激活时设置输出端 | 1 … 4096 |
| ALIVE Set_Flag | 连接激活时设置旗标 | 1 … 1024 |
| ALIVE Ping | Ping 命令周期 | 1 … 65534 s |

### 3.5 数据类型

| 类型 | 说明 | 用途 |
|------|------|------|
| STRING | 字符串 | 文本数据 |
| REAL | 浮点数 | 坐标、测量值 |
| INT | 整数 | 计数、状态码 |
| BOOL | 布尔值 | 开关状态 |
| FRAME | 坐标系 | 位姿数据 (X,Y,Z,A,B,C) |
| BYTE | 固定长度二进制 | 原始数据（Size 固定）|
| STREAM | 可变长度二进制 | 原始数据（EOS 结尾标识）|

### 3.6 EKI 函数概览

**连接管理：**

| 函数 | 功能 |
|------|------|
| EKI_Init(CHAR[]) | 初始化连接（读取 XML 配置）|
| EKI_Open(CHAR[]) | 打开连接 |
| EKI_Close(CHAR[]) | 关闭连接 |
| EKI_Clear(CHAR[]) | 删除连接 |

**发送数据：**

| 函数 | 功能 |
|------|------|
| EKI_Send(CHAR[], CHAR[], INT) | 发送 XML 或二进制数据 |

**写入发送存储器：**

| 函数 | 功能 |
|------|------|
| EKI_SetReal(CHAR[], CHAR[], REAL) | 写入 REAL 值 |
| EKI_SetInt(CHAR[], CHAR[], INT) | 写入 INT 值 |
| EKI_SetBool(CHAR[], CHAR[], BOOL) | 写入 BOOL 值 |
| EKI_SetFrame(CHAR[], CHAR[], FRAME) | 写入 FRAME 值 |
| EKI_SetString(CHAR[], CHAR[], CHAR[]) | 写入 STRING 值 |

**读取接收存储器：**

| 函数 | 功能 |
|------|------|
| EKI_GetBool(CHAR[], CHAR[], BOOL) | 读取 BOOL 值 |
| EKI_GetBoolArray(CHAR[], CHAR[], BOOL[]) | 读取 BOOL 数组 |
| EKI_GetInt(CHAR[], CHAR[], INT) | 读取 INT 值 |
| EKI_GetIntArray(CHAR[], CHAR[], INT[]) | 读取 INT 数组 |
| EKI_GetReal(CHAR[], CHAR[], REAL) | 读取 REAL 值 |
| EKI_GetRealArray(CHAR[], CHAR[], REAL[]) | 读取 REAL 数组 |
| EKI_GetString(CHAR[], CHAR[], CHAR[]) | 读取 STRING 值 |
| EKI_GetFrame(CHAR[], CHAR[], FRAME) | 读取 FRAME 值 |
| EKI_GetFrameArray(CHAR[], CHAR[], FRAME[]) | 读取 FRAME 数组 |

### 3.7 EKI_STATUS 结构

```krl
GLOBAL STRUC EKI_STATUS INT Buff, Read, Msg_No, BOOL Con
```

| 字段 | 类型 | 说明 |
|------|------|------|
| Buff | INT | 数据存储器中的数据组数量 |
| Read | INT | 已从存储器读取的数据组数量 |
| Msg_No | INT | 错误信息编号 |
| Con | BOOL | 连接状态（TRUE=已连接）|

### 3.8 典型 KRL 程序结构

```krl
DEF EKI_Example()
  DECL EKI_STATUS RET
  
  ; 初始化并打开连接
  RET = EKI_Init("MyConnection")
  RET = EKI_Open("MyConnection")
  
  ; 写入并发送数据
  EKI_SetReal("MyConnection", "Robot/Pos/X", 1000.0)
  EKI_SetReal("MyConnection", "Robot/Pos/Y", 500.0)
  RET = EKI_Send("MyConnection", "Robot")
  
  ; 读取接收数据
  DECL REAL sensorX
  RET = EKI_GetReal("MyConnection", "Sensor/Pos/X", sensorX)
  
  ; 关闭连接
  RET = EKI_Close("MyConnection")
  RET = EKI_Clear("MyConnection")
END
```

---

## 4. RSI vs EKI 对比

| 特性 | RSI | EKI |
|------|-----|-----|
| 协议 | UDP/IP | TCP/IP |
| 实时性 | 高（IPO 周期级）| 中（毫秒~秒级）|
| 数据格式 | XML（固定结构）| XML 或二进制 |
| 修正能力 | 支持实时轨迹修正 | 不支持直接修正 |
| 连接模式 | 客户端（主动发送）| 客户端/服务器 |
| 典型应用 | 焊缝跟踪、力控 | 状态监控、程序控制 |
| 配置方式 | .rsi 信号流 + XML | XML 配置文件 |
| 数据方向 | 双向（强制同步）| 双向（独立收发）|

---

## 5. 与 AdaWeldSystem 的集成

### 5.1 模块架构

```
Comm/
├── KUKARobot/
│   ├── RSICommunication.cs    ← RSI UDP 通讯管理
│   ├── EKICommunication.cs    ← EKI TCP 通讯管理
│   ├── KUKAXMLConfig.cs       ← XML 配置生成与解析
│   ├── KUKADataTypes.cs       ← 数据结构定义
│   └── KUKARobotManager.cs    ← 统一管理层
```

### 5.2 职责分工

- **RSICommunication**：管理 UDP 套接字、XML 序列化/反序列化、IPOC 时间戳校验、实时数据循环
- **EKICommunication**：管理 TCP 连接、XML 数据交换、连接状态监控
- **KUKAXMLConfig**：生成 RSI/EKI 的 XML 配置文件、解析配置参数
- **KUKADataTypes**：定义 KUKA 相关的数据实体（位姿、修正值、状态等）
- **KUKARobotManager**：统一入口，协调 RSI 和 EKI 的工作，对外提供简化接口

### 5.3 代码实现概要

**KUKADataTypes.cs**：
- 定义了 RSI/EKI 的枚举类型（`RSIDataType`、`EKIDataType`、`EKIMode`、`EKIEnvironment`、`RSIErrorType`）
- 定义了位姿结构 `KUKAPosition` 和 `KUKAFrame`
- 定义了数据实体 `KUKARobotData`（机器人状态）、`KUKACorrectionData`（传感器修正）
- 定义了 EKI 状态结构 `EKIStatus`
- 定义了各类事件参数（`RSIDataEventArgs`、`EKIDataEventArgs` 等）

**KUKAXMLConfig.cs**：
- 静态类，提供 RSI/EKI 的 XML 配置生成与解析
- `GenerateRSIXML` / `ParseRSIXML`：RSI XML 配置的序列化/反序列化
- `GenerateEKIXML` / `ParseEKIXML`：EKI XML 配置的序列化/反序列化
- `SaveRSIConfig` / `LoadRSIConfig` / `SaveEKIConfig` / `LoadEKIConfig`：文件持久化
- 配置类：`RSIConfig`、`RSIElement`、`EKIConfig`、`EKIElement`
- **实现方式**：底层 DOM 操作统一调用 `[[modules/FileOperate]]/XMLfile.cs` 的 `XdocumentReaderWriter` 通用方法（`AddElement`、`GetElementByPath`、`GetAttributeValue` 等），不再直接 `new XDocument`/`new XElement`

**RSICommunication.cs**：
- 基于 `UdpClient` 实现 UDP/IP 通讯
- `Initialize`：加载 RSI XML 配置
- `Start` / `Stop`：启动/停止 UDP 接收线程
- `SendRobotData`：序列化 `KUKARobotData` 为 XML 并发送
- `ReceiveCorrectionData` / `TryReceiveCorrectionData`：接收并反序列化修正数据
- `SerializeRobotData` / `DeserializeCorrectionData`：XML 序列化/反序列化
- IPOC 时间戳自动递增与校验机制
- 独立的 `ReceiveLoop` 后台线程处理入站数据

**EKICommunication.cs**：
- 基于 `TcpClient` 实现 TCP/IP 通讯
- `Initialize`：加载 EKI XML 配置
- `Open` / `Close` / `Clear`：连接生命周期管理
- `Send` / `SendRaw` / `SendString`：发送 XML/二进制/字符串数据
- `SetReal` / `SetInt` / `SetBool` / `SetFrame` / `SetString`：写入发送存储器
- `GetBool` / `GetInt` / `GetReal` / `GetString` / `GetFrame`：读取接收存储器
- 独立的 `ReceiveLoop` 后台线程处理入站数据

**KUKARobotManager.cs**：
- 统一入口，聚合 `RSICommunication` 和 `EKICommunication`
- 封装 RSI/EKI 的初始化和连接管理方法
- 提供 `SendRobotData`、`ReceiveCorrectionData`、`GetCurrentData` 等高层数据接口
- 统一事件转发（`DataReceived`、`ConnectionStateChanged`）
- 实现 `IDisposable` 接口确保资源释放

### 5.4 依赖关系

- 依赖 [[modules/Comm]] 的全局通讯基础设施（`GlobalCommData.ShowLog`）
- 可能被 [[modules/DeviceControl]] 调用（焊接工作流中的机器人控制步骤）
- 可能被 [[modules/WeldParamControl]] 调用（焊缝跟踪修正数据传递）

---

## 6. 常见错误与处理

| 错误码/现象 | 原因 | 解决方案 |
|------------|------|---------|
| RSI: 时间戳不一致 | 传感器返回的 IPOC 与发送不匹配 | 检查传感器程序是否正确回传 IPOC |
| RSI: 数据包延迟 | 网络拥塞或传感器处理慢 | 优化网络配置或降低发送频率 |
| EKI: 连接超时 | IP/端口配置错误或外部系统未启动 | 检查 XML 配置和网络连通性 |
| EKI: XML 解析错误 | 发送/接收的 XML 结构与配置不匹配 | 检查 ELEMENT Tag 和 Type 配置 |
| EKI: 存储器溢出 | BUFFERING Limit 设置过小 | 增大 Limit 或及时读取数据 |

---

## 7. RSI FastIPO + EtherCAT 从站

> **决策依据**：[[decisions/ADR-036-MotionControllerDeltaReplacement]]（现行运控 = 台达 EtherCAT；原 RSI-CAMBOX 决策已随正运动移除，见 [[decisions/ADR-037-ZMotionRemovalAndDeltaLanding]]）
> **详细设计**：[[architecture/DeviceControlArchitecture]]
> **核心用途**：为焊缝跟踪提供硬件级同步的主轴位置数据（台达侧承接方案 OPEN：ECAM2 / 虚拟轴 + GearIn / PVT）

### 7.1 链路特性

| 维度 | 实现 |
|------|------|
| 传输方式 | EtherCAT PDO |
| 实时性 | 4ms 硬实时，抖动 < 100μs |
| 数据路径 | 运动内核 IPO → EtherCAT 从站 TxPDO |
| 延迟 | 1 个 IPO 周期（最小延迟） |
| 数据格式 | 二进制 PDO（REAL32 + UINT32） |
| PC 角色 | 只读监听（不参与实时链路） |

### 7.2 FastIPO 模式

**什么是 FastIPO**：
- RSI 的特殊模式，数据**直接从运动内核 IPO 插补器输出**
- 不经过 KRL、不经过 SPS、不经过 RSI 容器处理
- 延迟最小、抖动最小，是 RSI 能达到的最高实时等级

**为什么需要 FastIPO**：
- CAMBOX 主轴直接使用机器人进给位置
- 主轴位置的精度和实时性直接决定焊缝跟踪精度
- FastIPO 提供的超前位置数据天然补偿机械滞后

### 7.3 EtherCAT 从站模式

在设备控制架构中，KUKA 机器人配置为 **EtherCAT 从站**：

```
正运动 ZMC（EtherCAT 主站）
    │
    ├─ 从站 1：KUKA 机器人（TxPDO: ToolRelX + TimeStamp）
    ├─ 从站 2：Y 轴伺服驱动器
    └─ ... 其他从站
```

**TxPDO 数据定义（机器人 → 正运动）**：

| 信号 | 类型 | 字节 | 说明 |
|------|------|------|------|
| `ToolRelX` | REAL32 | 4 | Tool 坐标系 X 方向相对焊接起点的行进位移（mm） |
| `TimeStamp` | UINT32 | 4 | 机器人运动内核高精度时间戳（μs） |
| **合计** | — | **8 字节** | — |

**为什么用 EtherCAT 而不是 UDP**：
- **硬件级同步**：EtherCAT 分布式时钟（DC）实现亚微秒级同步
- **确定性**：PDO 周期固定，无网络拥塞、无重传、无抖动
- **零 CPU 开销**：数据直接映射到控制器内存，不经过协议栈处理
- **直接做编码器轴**：正运动 ATYPE=25 可直接将 PDO 数据映射为编码器位置

### 7.4 ToolRelX 坐标系

**ToolRelX 的定义**：
- 机器人 Tool 坐标系下的 X 方向位移
- 相对于焊接起始点（`G_WELD_TOOL_START`）
- 纯进给量，不受机器人姿态旋转影响
- 单位：mm

**与 $POS_ACT 的区别**：
- `$POS_ACT` 是笛卡尔空间绝对位置，受姿态影响
- `ToolRelX` 是 Tool 坐标系下的相对位移，只反映进给进度
- 焊缝跟踪只关心"焊枪走了多远"，ToolRelX 是最直接的表达

### 7.5 KRL 焊接启停逻辑

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

### 7.6 PC 端数据接收

在设备控制架构中，PC **不直接从机器人接收 RSI 数据**（实时链路完全在 EtherCAT 总线上）。

PC 获取机器人位置的两种方式：
1. **从正运动控制器读取**：通过 `EncoderAxis.GetCurrentPosition()` 读取 ATYPE=25 轴的当前位置（用于 UI 显示和状态监控）
2. **EKI 非实时查询**：通过 EKI TCP 接口查询机器人状态（用于非实时监控、配置管理）

> ⚠️ 两种方式都不参与实时运动控制，仅用于监控和显示。

### 7.7 组件职责

| 组件 | 文件 | 职责 |
|------|------|------|
| `RSICommunication` | `Comm/Robot/KUKARobot/RSICommunication.cs` | RSI UDP/XML 实时通讯。**保留但非默认链路**——实时主轴数据改由 EtherCAT PDO 直连正运动控制器，本组件作为备用/调试通道 |
| `EKICommunication` | `Comm/Robot/KUKARobot/EKICommunication.cs` | EKI TCP 数据交换，用于非实时配置管理与状态监控 |
| `KUKADataTypes` | `Comm/Robot/KUKARobot/KUKADataTypes.cs` | 机器人数据结构，含 ToolRelX + 时间戳结构 |
| `KUKARobotManager` | `Comm/Robot/KUKARobot/` | 统一管理 RSI + EKI，由 `CommunicationManager.RobotManager` 直接暴露 |

> **实装状态**：CAMBOX 跟踪链路三组件（`EncoderAxis` / `CamBoxTracker` / `RSIPositionBuffer`）与 `MotionControlWorkflow` 编排均已落地；**KUKA 侧 RSI FastIPO + EtherCAT 从站配置需现场联调**，PLC/机器人点位待标定。

## 8. 参考链接

- [[api/KUKARobot]] —— C# API 参考
- [[modules/Comm]] —— 通讯总线模块
- [[modules/WeldParamControl]] —— 焊接工艺模块
- [[modules/MotionControl]] —— 运动控制模块（台达 EtherCAT 三层架构）
- [[architecture/DeviceControlArchitecture]] —— 设备控制架构规范页（第 10 章 运动控制）
- [[decisions/ADR-036-MotionControllerDeltaReplacement]] —— 台达 EtherCAT 运控决策
- [[people/MotionControlSpecialist]] —— 运动控制专员
- [[people/GeneralTechSpecialist]] —— 通用技术专员

---

> 来源：KUKA.RobotSensorInterface 3.3 (KST_RSI_3.3_zh.pdf)、KUKA.Ethernet KRL 2.2 (KST_Ethernet_KRL_2.2_zh.pdf)
> Ingest 时间：2026-07-01
> CAMBOX 链路扩展：2026-08-11
