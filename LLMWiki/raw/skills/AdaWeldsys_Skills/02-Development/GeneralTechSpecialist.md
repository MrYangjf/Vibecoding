---
name: "AdaWeldSystem 通用技术开发专员"
version: "V5.260624.1030"
description: "负责文件操作工具（INI/XML/日志）、系统通信（TCP/IP/S7/Profinet 统一设备通讯）、设备错误码体系（DeviceErrorCode）、全局状态管理与事件总线（含 WorkflowState 枚举及 DeviceRunningState 枚举）、程序入口与全局配置。三种通讯方式统一职责：触发工作流程（进入/退出/暂停/复位）+ 反馈设备运行状态。"
---

# 通用技术开发专员 Skill

## 描述

本 Skill 定义了 AdaWeldSystem 项目通用技术开发专员的职责边界、负责文件清单、技术要点和交付标准。

## 版本变更记录

| 版本 | 更新时间 | 变更级别 | 变更内容 |
|------|---------|---------|---------|
| V1.0 | 2026-06-23 | - | 初始版本。从原团队架构 skill 拆分独立。 |
| V2.260623.2235 | 2026-06-23 | 文件级 | GlobalCommData.cs 新增 TcpMessageReceived 事件和 ForwardTcpMessage 方法；TCPIPComm.cs Client_OnDataReceived 中调用 ForwardTcpMessage 供 Workflow 模块监听触发。 |
| V3.260623.2345 | 2026-06-23 | 结构级 | SystemStatus.cs 新增 WorkflowState 枚举和 WorkflowStateChangedEventArgs（从 Workflow/ 迁移）；WorkflowState 由通用技术专员负责维护；焊接工艺专员不再负责设备状态枚举。 |
| V4.260624.1015 | 2026-06-24 | 结构级 | 新增西门子S7通讯和Profinet通讯（含GSD文件编写）职责领域；新增 SiemensS7/ 和 Profinet/ 模块及负责文件清单；更新核心职责、技术要点、交付标准和协作关系。 |
| V5.260624.1030 | 2026-06-24 | 结构级 | 统一三种通讯方式（TCP/IP/S7/Profinet）的协作职责为"触发工作流程+反馈设备状态"；WorkflowState 枚举增加 Paused/Resetting；新增 DeviceErrorCode 设备错误码体系；新增 DeviceRunningState 设备运行状态枚举；重构协作关系表为统一通讯协作模型。 |

### 版本命名规则

- 格式：`V{大版本}.{小版本}`
- **大版本**：结构级修改时+1
- **小版本**：日期格式`yyMMdd.HHmm`

---

## /updateskill：Skill 自更新工作流

### 执行步骤

#### 步骤1：读取当前 skill 文件

读取 `d:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\M4\AdaWeldsys\AdaWeldSystem\Skills\02-Development\GeneralTechSpecialist.md` 的当前内容。

#### 步骤2：根据用户反馈确定更新内容

#### 步骤3：在最新版本上修改 skill

**重要原则**：
- 必须在最新版本上修改
- **版本号生成公式（强制执行）**：
  ```
  小版本 = 执行 PowerShell 命令 Get-Date -Format "yyMMdd.HHmm" 获取的当前系统时间
  ```
  **执行方式**：在 TRAE 沙盒中运行 `Get-Date -Format "yyMMdd.HHmm"`，将返回结果直接作为小版本号。严禁估算或手动填写。
- 修改后版本号按规则递增

#### 步骤4：保存 skill 备份

保存路径：`d:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\M4\AdaWeldsys\AdaWeldSystem\Backup\Skills\GeneralTechSpecialist_V{版本号}.md`

#### 步骤5：通知用户变更

---

## 核心职责

- 文件操作工具（INI/XML/日志）
- **统一设备通讯**（TCP/IP / S7 / Profinet 三种通讯方式，统一职责模型）
- **设备错误码体系**（DeviceErrorCode 固定编码，映射设备异常状态）
- **全局状态管理与事件总线**（WorkflowState / DeviceRunningState 枚举）
- 程序入口与全局配置

## 统一设备通讯职责模型

项目所有通讯方式（TCP/IP、S7、Profinet）遵循统一的职责模型，不区分协议差异：

### 通讯职责定义

所有通讯通道统一承担以下两类职责：

| 职责类别 | 具体操作 | 说明 |
|----------|---------|------|
| **工作流程控制指令（下行）** | 进入工作流程（Start） | 通知设备开始工作 |
| | 退出工作流程（Stop） | 通知设备停止工作 |
| | 暂停工作流程（Pause） | 通知设备暂停当前工作 |
| | 复位工作流程（Reset） | 通知设备复位到初始状态 |
| **设备运行状态反馈（上行）** | 设备状态上报 | 设备通过通讯通道上报当前运行状态 |
| | 异常错误上报 | 设备通过 DeviceErrorCode 上报具体异常 |

### 通讯协议与设备映射

| 通讯协议 | 适用设备 | 通讯方向 | 典型场景 |
|----------|---------|---------|---------|
| **TCP/IP** | 外部上位机/中控系统 | 双向 | 上位机下发工作流程控制指令，设备反馈运行状态 |
| **S7** | 西门子 PLC | 双向 | PLC 控制焊接/运动/相机等设备启停，反馈设备IO状态 |
| **Profinet** | Profinet IO 从站设备 | 双向 | PLC 通过 Profinet IO 控制从站设备，读取设备诊断数据 |

### 工作流程控制指令编码规范

所有通讯通道使用统一的指令编码，具体协议帧格式由各通讯模块自行封装：

```csharp
/// <summary>
/// 工作流程控制指令枚举（所有通讯通道统一使用）
/// </summary>
public enum WorkflowCommand
{
    Start = 0x01,      // 进入工作流程
    Stop = 0x02,       // 退出工作流程
    Pause = 0x03,      // 暂停工作流程
    Reset = 0x04       // 复位工作流程
}
```

## WorkflowState 枚举（工作流程状态）

```csharp
/// <summary>
/// 工作流程状态枚举
/// 由通用技术专员在 SystemStatus.cs 中维护
/// </summary>
public enum WorkflowState
{
    Idle,           // 空闲：等待启动指令
    Running,        // 运行中：工作流程正在执行
    Paused,         // 暂停：工作流程被暂停，可恢复
    Resetting,      // 复位中：设备正在复位到初始状态
    ErrorStopped,    // 异常停止：因设备错误导致流程停止
    Completed       // 已完成：工作流程正常结束
}
```

### WorkflowState 有效状态转换矩阵

```
Idle        → Running, Resetting
Running     → Paused, ErrorStopped, Completed, Stop(→Idle)
Paused      → Running(恢复), Stop(→Idle), Resetting
Resetting   → Idle（复位完成）
ErrorStopped→ Resetting, Idle（手动清除错误后）
Completed   → Idle, Resetting
```

## DeviceRunningState 枚举（设备运行状态）

```csharp
/// <summary>
/// 设备运行状态枚举（所有设备统一使用）
/// </summary>
public enum DeviceRunningState
{
    Uninitialized,   // 未初始化
    Initializing,    // 初始化中
    Ready,           // 就绪：设备已准备好接受指令
    Running,         // 运行中
    Paused,          // 暂停
    Alarm,           // 报警：设备存在非致命异常
    EmergencyStop,   // 急停
    Homing,          // 回零中
    ShuttingDown,    // 关机中
    Offline          // 离线：设备通讯中断
}
```

## DeviceErrorCode 设备错误码体系

### 编码规则

- 格式：`ErrorCode{4位数字}`，如 `ErrorCode0001`
- 范围：`ErrorCode0001` ~ `ErrorCode9999`
- 分段分配：每类设备分配独立的编码段，避免冲突

### 错误码分段分配表

| 编码范围 | 设备/模块类别 | 负责专员 | 说明 |
|----------|-------------|---------|------|
| ErrorCode0001 ~ ErrorCode0099 | 工业相机 | 工业相机开发专员 | 相机相关异常 |
| ErrorCode0100 ~ ErrorCode0199 | 图像算法 | 图像算法开发专员 | 算法处理异常 |
| ErrorCode0200 ~ ErrorCode0299 | 3D 传感器/点云 | 3D开发专员 | 3D 数据相关异常 |
| ErrorCode0300 ~ ErrorCode0399 | 运动控制 | 运动控制开发专员 | 轴运动/限位/回零异常 |
| ErrorCode0400 ~ ErrorCode0499 | 焊接工艺 | 焊接工艺开发专员 | 焊接参数/工艺异常 |
| ErrorCode0500 ~ ErrorCode0599 | 数据库 | 数据库开发专员 | 数据存储/读写异常 |
| ErrorCode0600 ~ ErrorCode0699 | 通讯系统 | 通用技术开发专员 | TCP/S7/Profinet 通讯异常 |
| ErrorCode0700 ~ ErrorCode0799 | UI 系统 | UI开发专员 | 界面交互异常 |
| ErrorCode0800 ~ ErrorCode0899 | 系统级 | 通用技术开发专员 | 程序启动/配置/全局异常 |
| ErrorCode0900 ~ ErrorCode0999 | 预留扩展 | — | 未来新增模块使用 |

### 已分配错误码明细

```csharp
/// <summary>
/// 设备错误码定义（固定编码，代表不同设备异常状态）
/// 各专员在各自编码段内分配，由通用技术专员统一维护本文件
/// </summary>
public static class DeviceErrorCode
{
    // ===== 工业相机 (0001~0099) =====
    public const string CameraOffline = "ErrorCode0001";         // 相机掉线
    public const string CameraInitFailed = "ErrorCode0002";      // 相机初始化失败
    public const string CameraTimeout = "ErrorCode0003";         // 相机采集超时
    public const string CameraDataError = "ErrorCode0004";       // 相机数据解析错误
    // ... 工业相机开发专员继续分配

    // ===== 图像算法 (0100~0199) =====
    public const string AlgorithmInitFailed = "ErrorCode0100";    // 算法初始化失败
    public const string AlgorithmTimeout = "ErrorCode0101";       // 算法处理超时
    public const string AlgorithmResultInvalid = "ErrorCode0102"; // 算法结果无效
    // ... 图像算法开发专员继续分配

    // ===== 3D 传感器 (0200~0299) =====
    // ... 3D开发专员分配

    // ===== 运动控制 (0300~0399) =====
    public const string AxisHomeFailed = "ErrorCode0300";         // 轴回零失败
    public const string AxisSoftLimit = "ErrorCode0301";         // 软限位触发
    public const string AxisHardLimit = "ErrorCode0302";         // 硬限位触发
    public const string AxisAlarm = "ErrorCode0303";             // 轴驱动器报警
    public const string AxisFollowingError = "ErrorCode0304";     // 跟随误差超限
    // ... 运动控制开发专员继续分配

    // ===== 焊接工艺 (0400~0499) =====
    // ... 焊接工艺开发专员分配

    // ===== 数据库 (0500~0599) =====
    // ... 数据库开发专员分配

    // ===== 通讯系统 (0600~0699) =====
    public const string TcpConnectionLost = "ErrorCode0600";      // TCP 连接断开
    public const string TcpTimeout = "ErrorCode0601";            // TCP 通讯超时
    public const string S7ConnectionLost = "ErrorCode0602";       // S7 连接断开
    public const string S7ReadFailed = "ErrorCode0603";          // S7 读取失败
    public const string S7WriteFailed = "ErrorCode0604";         // S7 写入失败
    public const string ProfinetDeviceOffline = "ErrorCode0605"; // Profinet 设备离线
    public const string ProfinetIoError = "ErrorCode0606";        // Profinet IO 数据异常
    // ... 通用技术开发专员继续分配

    // ===== UI 系统 (0700~0799) =====
    // ... UI开发专员分配

    // ===== 系统级 (0800~0899) =====
    public const string SystemConfigError = "ErrorCode0800";     // 系统配置错误
    public const string SystemStartupFailed = "ErrorCode0801";   // 系统启动失败
    public const string EmergencyStopTriggered = "ErrorCode0802";// 急停触发
    // ... 通用技术开发专员继续分配
}
```

### 错误码使用规范

1. **定义位置**：所有 `DeviceErrorCode` 常量统一定义在 `Comm/DeviceErrorCode.cs` 中
2. **分配权限**：各专员在各自编码段内分配新错误码，但定义文件由通用技术专员维护
3. **使用方式**：各专员在代码中通过 `DeviceErrorCode.CameraOffline` 等常量引用，禁止硬编码字符串
4. **事件上报**：设备异常时，通过 `GlobalCommData` 的事件总线发布 `DeviceErrorOccurred` 事件，携带 `DeviceErrorCode` 和设备标识
5. **日志记录**：错误码必须同时写入日志系统（`Log.cs`），格式：`[ErrorCode0001] 相机掉线 - SmartRay Camera #1`

## 负责文件清单

```
FileOperate/
├── IniFile.cs                 ← INI 文件读写（核心工具类）
├── Log.cs                     ← 日志系统
├── Win32API.cs                ← Win32 API 封装
└── XMLfile.cs                 ← XML 配置读写

Comm/
├── GlobalCommData.cs          ← 全局数据/事件总线
│                                 - TcpMessageReceived 事件: TCP消息转发供Workflow监听
│                                 - ForwardTcpMessage(): 转发TCP消息到订阅者
│                                 - 【新增】DeviceErrorOccurred 事件: 设备错误码上报
│                                 - 【新增】WorkflowCommandReceived 事件: 工作流程控制指令接收
├── SystemStatus.cs            ← 系统状态枚举
│                                 - WorkflowState 枚举: Idle/Running/Paused/Resetting/ErrorStopped/Completed
│                                 - 【新增】DeviceRunningState 枚举: 设备运行状态（所有设备统一）
│                                 - WorkflowStateChangedEventArgs: 工作流程状态变更事件参数
│                                 - 由通用技术专员负责维护（设备整体状态）
├── DeviceErrorCode.cs         ← 【新增】设备错误码体系
│                                 - DeviceErrorCode 静态常量类
│                                 - ErrorCode{4位数字} 格式
│                                 - 各设备编码段分配（见错误码分段分配表）
├── WorkflowCommand.cs         ← 【新增】工作流程控制指令定义
│                                 - WorkflowCommand 枚举: Start/Stop/Pause/Reset
│                                 - 所有通讯通道统一使用的指令编码
└── TCPIPComm.cs               ← TCP/IP 通信
                                   - Client_OnDataReceived 中调用 ForwardTcpMessage()
                                   - 【修改】解析 WorkflowCommand 指令并触发 WorkflowCommandReceived 事件
                                   - 【修改】解析 DeviceErrorCode 并触发 DeviceErrorOccurred 事件

SiemensS7/
├── S7Communication.cs         ← S7 协议通讯核心类
│                                 - Connect/Disconnect: PLC 连接管理
│                                 - ReadBytes/WriteBytes: 原始字节读写
│                                 - ReadInt16/WriteInt16: 16位整数读写
│                                 - ReadReal/WriteReal: 浮点数读写
│                                 - ReadBool/WriteBool: 布尔量读写（IO状态）
│                                 - ReadString/WriteString: 字符串读写
│                                 - ReadMultiple: 批量读取多地址数据
│                                 - 【新增】SendWorkflowCommand(): 通过S7下发工作流程控制指令
│                                 - 【新增】ReadDeviceStatus(): 通过S7读取设备运行状态
├── S7Address.cs               ← S7 地址解析与封装
├── S7ConnectionConfig.cs      ← S7 连接配置
└── S7DataConverter.cs         ← S7 数据类型转换工具

Profinet/
├── ProfinetDevice.cs          ← Profinet 设备通讯管理
│                                 - 设备发现与注册
│                                 - IO 数据 cyclic 读写
│                                 - 设备状态监控（Online/Offline/Error）
│                                 - 【新增】SendWorkflowCommand(): 通过Profinet下发工作流程控制指令
│                                 - 【新增】ReadDeviceStatus(): 通过Profinet读取设备诊断状态
├── ProfinetConfig.cs          ← Profinet 网络配置
├── GsdFileGenerator.cs         ← GSD 文件生成器
├── GsdTemplateManager.cs      ← GSD 模板管理
└── ProfinetIoMapping.cs       ← Profinet IO 映射表

Properties/
├── AssemblyInfo.cs            ← 程序集信息
├── Resources.resx             ← 资源文件
├── Resources.Designer.cs      ← 资源设计器
├── Settings.settings          ← 应用设置
└── Settings.Designer.cs       ← 设置设计器

Program.cs                     ← 程序入口
App.config                     ← 应用配置
```

### 弃用文件记录

| 文件名 | 原所属模块 | 弃用日期 | 弃用原因 | 替代文件 |
|--------|-----------|---------|---------|---------|
| （暂无） | | | | |

## 技术要点

### 文件操作与日志
- 全局状态使用 `static class` 管理
- 事件驱动: `EventHandler<TEventArgs>`
- 日志分级: `MessageLevel` (Info/Warning/Error)
- XML配置路径: `AppDomain.CurrentDomain.BaseDirectory + @"\Config\"`
- INIFile 支持方法: ReadInt/WriteInt, ReadDouble/WriteDouble, ReadBool/WriteBool, ReadString/WriteString, SaveToFile()

### 统一设备通讯
- **职责统一**：TCP/IP、S7、Profinet 三种通讯方式统一承担"工作流程控制指令下发"和"设备运行状态反馈"两类职责
- **指令统一**：所有通讯通道使用 `WorkflowCommand` 枚举（Start/Stop/Pause/Reset），各模块自行封装协议帧
- **状态统一**：所有设备使用 `DeviceRunningState` 枚举上报运行状态
- **错误统一**：所有设备异常使用 `DeviceErrorCode` 固定编码上报，禁止硬编码错误字符串
- **事件统一**：所有通讯模块收到指令或状态后，通过 `GlobalCommData` 事件总线发布统一事件

### TCP/IP 通信
- TCP通信: 使用 `STTech.BytesIO.Tcp`
- 支持连接/断开/重连机制
- TCP消息转发事件总线供 Workflow 模块监听
- 解析接收到的 `WorkflowCommand` 指令并触发 `WorkflowCommandReceived` 事件
- 解析接收到的 `DeviceErrorCode` 并触发 `DeviceErrorOccurred` 事件

### 西门子 S7 通讯
- **协议选型**：使用 S7 协议（非 OpenIEC/Snap7 等第三方库时需封装 P/Invoke）
- **连接参数**：IP地址、Rack（默认0）、Slot（默认1）、CPU类型
- **地址格式**：`DBX0.0`（位）、`DBB0`（字节）、`DBW0`（字）、`DBD0`（双字）、`DBR0`（实数）
- **数据读写原则**：
  - 所有 PLC 读写操作必须包含异常捕获和超时处理
  - 批量读取优先于单次读取（减少通讯次数）
  - 读写超时默认 500ms，可配置
- **连接管理**：
  - 支持自动重连（断线后指数退避重试）
  - 连接状态通过事件通知（`ConnectionStateChanged`）
  - 心跳检测：定期读取 DB1.X0.0 确认连接存活
- **配置持久化**：PLC 连接参数存储在 `Config/S7Connection.ini` 中
- **工作流程控制**：通过 `SendWorkflowCommand()` 将 `WorkflowCommand` 枚举写入 PLC 指定 DB 块
- **设备状态反馈**：通过 `ReadDeviceStatus()` 从 PLC 读取设备 IO 状态，映射为 `DeviceRunningState`

### Profinet 通讯
- **通讯模型**：基于 cyclic IO 数据交换（非基于消息的通讯）
- **GSD 文件规范**：
  - GSD 文件为 XML 格式（GSDML V2.3+）
  - 必须包含：VendorID、DeviceID、模块定义、IO 数据类型
  - GSD 文件放置路径：`Config/GSD/` 目录
  - 文件命名规范：`{VendorName}_{DeviceType}_{Version}.xml`
- **GSD 文件编写要点**：
  - `ISO15745ProfileContainer` 根节点
  - `ProfileBody` 定义设备能力
  - `ApplicationProcess` 定义 IO 模块及数据通道
  - `SubmoduleItem` 定义子模块的输入/输出字节数
  - `RecordData` 定义参数记录（如设备参数化）
- **IO 映射规范**：
  - 输入/输出数据区固定长度对齐
  - 使用 `ProfinetIoMapping` 类管理物理地址到逻辑变量的映射
  - IO 数据打包/解包使用 `BitConverter` 或 `Marshal` 进行高效转换
- **设备管理**：
  - 设备上线/下线事件通知
  - 设备诊断数据读取
  - 支持热插拔检测
- **工作流程控制**：通过 `SendWorkflowCommand()` 将控制指令写入 Profinet IO 输出区
- **设备状态反馈**：通过 `ReadDeviceStatus()` 从 Profinet IO 输入区读取设备状态，映射为 `DeviceRunningState`

## 交付标准

- [ ] 配置文件读写稳定
- [ ] 日志系统分级正确
- [ ] TCP通信可连接/断开/重连
- [ ] 全局事件订阅/发布正常
- [ ] **WorkflowState 枚举包含 Idle/Running/Paused/Resetting/ErrorStopped/Completed 六种状态**
- [ ] **DeviceRunningState 枚举包含 10 种设备运行状态**
- [ ] **DeviceErrorCode 错误码体系完整，各编码段已分配**
- [ ] **WorkflowCommand 枚举（Start/Stop/Pause/Reset）被三种通讯通道统一使用**
- [ ] **S7 PLC 可正常连接/断开，支持自动重连**
- [ ] **S7 数据读写正确（Int16/Real/Bool/String）**
- [ ] **S7 批量读取性能满足要求（单次读取耗时 < 50ms）**
- [ ] **S7 连接参数可通过 INI 配置持久化**
- [ ] **Profinet 设备可正常发现和注册**
- [ ] **Profinet IO cyclic 数据交换稳定**
- [ ] **GSD 文件格式正确，可通过 TIA Portal 导入**
- [ ] **GSD 文件模板可参数化生成**
- [ ] **设备错误码通过事件总线上报，日志系统正确记录**

## 协作关系

### 统一通讯协作模型

所有通讯方式（TCP/IP/S7/Profinet）与各专员的协作关系统一为以下两类：

| 协作方向 | 协作内容 | 数据接口 |
|----------|----------|----------|
| **通用技术 → 所有设备专员** | 下发工作流程控制指令（Start/Stop/Pause/Reset） | `WorkflowCommand` 枚举，通过各通讯通道下发 |
| **所有设备专员 → 通用技术** | 上报设备运行状态（DeviceRunningState）和设备错误码（DeviceErrorCode） | `DeviceRunningState` 枚举、`DeviceErrorCode` 常量，通过 `GlobalCommData` 事件总线上报 |

### 各专员具体协作关系

| 协作对象 | 协作内容 | 数据接口 |
|----------|----------|----------|
| **所有专员** | 提供 INI/XML 配置读写工具 | `FileOperate.INIFile` |
| **所有专员** | 提供设备错误码定义和使用规范 | `Comm.DeviceErrorCode` |
| **所有专员** | 提供工作流程控制指令枚举 | `Comm.WorkflowCommand` |
| **所有专员** | 提供设备运行状态枚举 | `Comm.SystemStatus.DeviceRunningState` |
| **UI开发专员** | 系统日志显示、通讯状态监控、工作流程状态显示、设备错误码告警显示 | `GlobalCommData`, `Log`, `SystemStatus.WorkflowState`, `DeviceErrorCode` |
| **焊接工艺专员** | 通过通讯通道下发焊接工作流程控制指令；焊接设备上报运行状态和错误码 | `WorkflowCommand`, `DeviceRunningState`, `DeviceErrorCode` |
| **运动控制专员** | 通过通讯通道下发运动控制工作流程指令；运动轴上报运行状态和错误码（限位/报警等） | `WorkflowCommand`, `DeviceRunningState`, `DeviceErrorCode` |
| **工业相机专员** | 通过通讯通道下发相机采集控制指令；相机上报运行状态和错误码（掉线/超时等） | `WorkflowCommand`, `DeviceRunningState`, `DeviceErrorCode.CameraOffline` |
| **3D开发专员** | 通过 Profinet 下发 3D 传感器控制指令；传感器上报运行状态和错误码 | `WorkflowCommand`, `DeviceRunningState`, `ProfinetDevice`, `ProfinetIoMapping` |
| **数据库专员** | 数据库异常错误码上报 | `DeviceErrorCode`（0500~0599 段） |
