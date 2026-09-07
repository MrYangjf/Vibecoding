---
title: 台达 EtherCAT 高级运动（PVT / 电子凸轮）使用规范
date: 2026-09-07
status: active
tags: [指南, 运控, 台达, EtherCAT, PVT, ECAM2, 电子凸轮, 焊缝跟踪]
---

# 台达 EtherCAT 高级运动（PVT / 电子凸轮）使用规范

> **定位**：PCI-L221 主站卡的**高级运动能力**（多段 PVT 轨迹插值、ECAM/ECAM2 电子凸轮主从跟随）的使用方式与落地约束。
> 基础能力（初始化/使能/点位/回零/IO）见 [[guides/DeltaEtherCAT-DevGuide]]；部署见 [[guides/DeltaEtherCAT-Deployment]]；UI 见 [[guides/DeltaEtherCAT-UIDesign]]。
> **原档**：`raw/delta/台达EtherCAT_PVT与电子凸轮运动开发指南.md`（v1.3，含 PVT/ECAM/ECAM2/机器人跟随/UI 四部分）。

## 章节导航

| 节 | 内容 |
|---|---|
| [§1 权威顺序与核验方法](#1-权威顺序与核验方法) | 三方证据如何排序 |
| [§2 原档失准订正表](#2-原档失准订正表) | **6 处确定 + 1 处存疑，先看这张表** |
| [§3 PVT 多段插值](#3-pvt-多段插值) | 两套 API、参数语义、选型 |
| [§4 电子凸轮 ECAM / ECAM2](#4-电子凸轮-ecam--ecam2) | 主轴来源真值、建表、啮合/脱离 |
| [§5 机器人 X → Y 轴跟随选型](#5-机器人-x--y-轴跟随选型) | 本项目焊缝跟踪的方案裁决 |
| [§6 待补 Native 声明清单](#6-待补-native-声明清单) | 落地前需补的 P/Invoke |
| [§7 OPEN 项](#7-open-项) | 待现场/厂商确认 |

---

## 1. 权威顺序与核验方法

> **裁决顺序（沿用 ADR-039）**：**台达 SDK 头文件 > 官方编程手册 PM > 二手文档/规范页**。

| 证据 | 路径 | 说明 |
|---|---|---|
| SDK 头文件（最权威） | `D:\Program Files (x86)\Delta Industrial Automation\EtherCAT\inc\C#\EtherCAT_DLL.cs`（x86）/ `EtherCAT_DLL_x64.cs`（x64） | 832 个 `CS_ECAT_*` 符号；**API 名与签名的唯一真相源** |
| 官方编程手册 | `...\EtherCAT\manual\API\DELTA_IA-GMC_EtherCAT_PM_TC_20250428.pdf`（1018 页） | **参数语义/枚举值**的权威解释；比 SDK 头文件更细 |
| 安装指南 | `...\manual\API\DELTA EtherCAT UserGuild.pdf`（59 页） | 只有安装章节，无 API |
| 原档（二手） | `raw/delta/台达EtherCAT_PVT与电子凸轮运动开发指南.md` | **可用但须核验**，见 §2 |

⚠️ **手册滞后于 SDK**：`PVT_Begin_Move` / `PVT_Continue_Move` / `PVT_CycleStart` / `PVT_Get_Information` 在 2025-04 版 PM 手册中**查不到**，仅存在于 SDK 头文件。使用这几个 API 时**必须现场实测**。

---

## 2. 原档失准订正表

> 原档整体结构正确、示例代码工程化程度高，但**枚举值与 API 名存在编造/推测**。以下按 ADR-039 纪律逐条核验，编号延续 [[guides/DeltaEtherCAT-DevGuide]] 已记录的 8 处。

| # | 原档说法 | 核验结果（SDK + PM 手册） | 处置 |
|---|---|---|---|
| **9** | 3.4.2 虚拟轴 API：`CS_ECAT_Slave_CSP_Set_Virtual_Axis_Position` / `_Velocity` / `_Get_...` | **SDK 中 3 个名字全部不存在**（全文无 `Virtual_Axis`） | ⛔ 禁用；见下 |
| **10** | 方案一「ECAM2 虚拟轴主轴」= 把机器人 X 写进虚拟轴 | SDK 仅有的虚拟相关 API 是 `_Master_Virtual_NodeID_Alias_Enable` / `_Slave_CSP_Virtual_Set_Enable` / `_Slave_CSP_Virtual_Set_Command`。**PM 手册 p.257-259 明确**：其语义是**坐标系平移/零点偏移**（启用后 `Get_Position` 返回补偿后坐标，`Get_Actual_Position` 才返回马达真值），**不是创建虚拟主轴** | ⛔ 方案一不成立 |
| **11** | 2.1 `SourceType`：0=实际轴 1=指令轴 2=虚拟轴 3=外部编码器 | **PM 手册 p.554（ECAM2_Profile_CamIn）真值只有 2 个值**：`0`=远端脉波模块或伺服驱动器（`SourceNo` 0=马达回授/1=运动命令）、`1`=轴卡的脉波输入接口。**不存在 2 / 3**；`SourceType=1` 才是「外部编码器」 | ⛔ 编造值禁用 |
| **11b** | 2.3.3 ECAM 一代 `Set_Engage_Parameters` 的 `SourceType` 同表 | **PM 手册 p.506**：此处的 `SourceType` 是**啮合触发信号来源**，语义完全不同——`0`=远端模块数位输入、`4`=伺服 TouchProbe（`SourceNo` 1/2/3/4 = 上/下缘/Z 相上/下缘） | ⚠️ 同名不同义，勿混用 |
| **12** | 1.3.4「PVT 路径点单次不超过 256 点」 | **PM 手册 p.339**：`DataCount` **最大 8000 笔** | ✅ 订正为 8000 |
| **13** | 只讲 PVT A 套（`PVT_Move`/`PVT_Config`/`PVTComplete_*`/`PVT_Sync_Move`/`PVT_Get_NowMotCount`） | SDK 另有 **B 套流式 API**：`PVT_Begin_Move` / `PVT_Continue_Move` / `PVT_CycleStart` / `PVT_Get_Information`（参数用 `double` 工程单位、带 `TimeAbsMode`/`Finial`/`Retain`/`SdStopTime`/`RemainBufSize`）。原档**完全未提** | ✅ 补充，见 §3.2 |
| **?** | 1.3.4「`TargetTime` 是从上一个点到当前点的时间间隔」（相对） | PM 手册 p.339 示例为 `{0,100,200,300,400}`（等差，两种解释都成立）；但 `PVT_Begin_Move` 存在 `TimeAbsMode` 参数，说明**绝对/相对是可选模式** | ⚠️ **存疑**，现场用 `TimeAbsMode=0/1` 各测一次确认 |

> **额外提醒**：SDK 头文件中 `PVT_Continue_Move` 的 `EntryPoint` 写作 `"CS_ECAT_Slave_CSP_Start_PVT_Continue_Move"`（**无下划线前缀**），而同族其它 API 均为 `"_ECAT_..."`。疑为厂商头文件笔误；本仓封装时**先按 SDK 原文照抄**，若运行时抛 `EntryPointNotFoundException` 再改为 `_ECAT_` 前缀并记录。

---

## 3. PVT 多段插值

### 3.1 A 套：int 脉冲、一次性下发（原档已讲，参数已核验）

| API | 用途 |
|---|---|
| `CS_ECAT_Slave_CSP_Start_PVT_Move` | 单轴多段 PVT，**下发即启动** |
| `CS_ECAT_Slave_CSP_Start_PVTComplete_Move` | 同上，额外约束 `StrVel` / `EndVel` 起止速度 |
| `CS_ECAT_Slave_CSP_Start_PVT_Config` | 同 `PVT_Move`，但**只下载不启动**，配 `PVT_Sync_Move` 做多轴同动 |
| `CS_ECAT_Slave_CSP_Start_PVTComplete_Config` | 同上 + 起止速度约束 |
| `CS_ECAT_Slave_CSP_Start_PVT_Sync_Move` | 多轴统一启动（`AxisArray` + `SlotArray`） |
| `CS_ECAT_Slave_CSP_PVT_Get_NowMotCount` | 查询当前执行到第几个点 |

签名（SDK 原文）：

```csharp
CS_ECAT_Slave_CSP_Start_PVT_Move(ushort CardNo, ushort NodeID, ushort SlotID,
    int DataCnt, ref int TargetPos, ref int TargetTime, ref int TargetVel, ushort Abs);
// DataCnt ≤ 8000；TargetPos 脉冲；TargetTime ms；TargetVel 脉冲/s；Abs 0=相对 1=绝对
```

**前置条件**：轴必须已 `Set_Move_Mode(8=CSP)` 且伺服使能（bit2 置位）。加减速由主站自动运算，应用层不干预。

### 3.2 B 套：double 工程单位、流式续喂（原档未提，**连续跟随首选**）

```csharp
// 起始段：下发后可继续追加
CS_ECAT_Slave_CSP_Start_PVT_Begin_Move(ushort CardNo, ushort NodeID, ushort SlotID,
    int DataCount, ref double Pos, ref double Time, ref double Vel,
    ushort TimeAbsMode,   // 时间模式：0/1（绝对 or 相对，待实测确认）
    ushort Finial,        // 是否最后一段
    ushort Retain,        // （保留/保持，语义待实测）
    double SdStopTime);   // 平滑停止时间

// 续喂段：运动中继续追加点，不断流
CS_ECAT_Slave_CSP_Start_PVT_Continue_Move(ushort CardNo, ushort NodeID, ushort SlotID,
    int DataCount, ref double Pos, ref double Time, ref double Vel, ushort Finial);

CS_ECAT_Slave_CSP_Start_PVT_CycleStart(ushort CardNo, ushort NodeID, ushort SlotID);

CS_ECAT_Slave_CSP_Start_PVT_Get_Information(ushort CardNo, ushort NodeID, ushort SlotID,
    ref int TotalMcCount,    // 总点数
    ref int MdoneMcCount,    // 已完成点数
    ref int RemainBufSize,   // 剩余缓冲区 ← 续喂节拍据此调节
    ref ushort Status);
```

**为什么 B 套更适合焊缝跟踪**：`Get_Information.RemainBufSize` 提供**缓冲区水位**，可实现「水位低于阈值就补一批点」的闭环，避免 A 套"一次算 8000 点后无法响应实时偏差"的问题。单位是 `double`（工程单位 mm/s/mm·s），与本项目 `MontionAxis` 的工程单位语义一致，**不再需要调用方自己做 `Equiv` 换算**（换算仍在 L3 内完成）。

⚠️ B 套 4 个 API **无手册文档**，须现场实测后再进入生产链路。

### 3.3 PVT 通用约束（沿用原档，已核验）

- 数组用 `ref array[0]` 传首元素；数组在调用期间不可被 GC 移动（必要时 `fixed`）
- 位置单位脉冲（A 套）；B 套为工程单位
- 速度是「到达该点时的速度」，时间过短而无法达到会返回参数错误
- 基于 CSP 模式，启动前必须已在 CSP 且伺服使能

---

## 4. 电子凸轮 ECAM / ECAM2

### 4.1 主轴来源（SourceType）—— 以 SDK/手册为准

`ECAM2_Profile_CamIn` 的 `SourceType` **只有两个合法值**（PM p.554）：

| SourceType | 含义 | SourceNo |
|---|---|---|
| **0** | 远端脉波模块或伺服驱动器（**真实从站**） | 0=马达回授位置（默认）；1=运动命令 |
| **1** | **轴卡的脉波输入接口**（PCI-L221 板载脉冲输入 = 外部编码器） | 0=回授位置 |

> ⛔ **不存在 SourceType=2（虚拟轴）**。原档 2.1 的 0/1/2/3 四值表为编造。

**对本项目的含义**：机器人 X 坐标是 RSI/EKI 的**数字量报文**，不是脉冲串。因此**无法直接作为 ECAM2 的主轴**，除非机器人侧额外输出脉冲/编码器信号接入 PCI-L221 板载脉冲输入口（需现场确认硬件是否具备）。

### 4.2 ECAM2 建表（推荐方式）

```csharp
// 1) 建表：主轴位置(mm) → 从轴位置(mm) 点表
CS_ECAT_Slave_CSP_Start_ECAM2_Profile_Data(ushort CardNo, ushort CamNo, ushort DataNum,
    ref double MasterPos_mm, ref double SlavePos_mm,
    ref ushort Curve_Type, ref double Velocity_Scale);
// CamNo 0~31；DataNum ≤ 8000；Curve_Type 每段插值方式（0/1）

// 2) 造表模式（须在建表前调用）
CS_ECAT_Slave_CSP_Start_ECAM2_Set_Profile_Mode(ushort CardNo, ushort Mode);
// Mode 0=按用户参数造表(默认)  1=自动衔接(5次曲线)

// 3) 啮合
CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamIn(ushort CardNo, ushort NodeID, ushort SlotID,
    ushort MasterNodeID, ushort MasterSlotID, ushort SourceType, ushort SourceNo,
    ushort CamNo, ushort Periodic, ushort MasterAbsolute, ushort SlaveAbsolute,
    double MasterOffset, double SlaveOffset, double MasterScaling, double SlaveScaling,
    ushort StartMode, int MasterAxis_mm_Pulse, int SlaveAxis_mm_Pulse,
    double Slave_MaxVel_mm, double Slave_Acc_mm, double Slave_Dec_mm,
    short MasterAxis_Dir, short SlaveAxis_Dir, ushort BufferMode);
// Periodic 0=单周期 1=循环；StartMode 0=正向跳变 1=最短距离 2=正向 3=反向
// BufferMode 0=aborting 1=buffered

// 4) 运行中改点 / 相位 / 脱离 / 停用
CS_ECAT_Slave_CSP_Start_ECAM2_Profile_Modify(CardNo, CamNo, PointNo, ref double Parameters);
CS_ECAT_Slave_CSP_Start_ECAM2_Phasing(CardNo, NodeID, SlotID, Dist, MaxVel, Acc, Dec);
CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamOut(CardNo, NodeID, SlotID);
CS_ECAT_Slave_CSP_Start_ECAM2_Disable(CardNo, NodeID, SlotID);

// 5) 状态预览（不启动即可试算主→从映射）
CS_ECAT_Slave_CSP_Start_ECAM2_Get_PreviewTable(CardNo, CamNo,
    MasterPosMm, MasterOffset, SlaveOffset, MasterScaling, SlaveScaling, ref double SlavePosMm);
```

**映射公式**（PM p.567）：
`从轴位置 = f{ (主轴位置 + MasterOffset) × MasterScaling } × SlaveScaling + SlaveOffset`
⚠️ 偏移参数**仅在绝对模式有效且不可为负**；缩放不受绝对/相对影响。

### 4.3 时间模式凸轮（无位置主轴时的官方方案）

```csharp
// 主轴来源单位改为「时间」，之后用 CamIn_TimeMode 啮合（无需 MasterNodeID）
CS_ECAT_Slave_CSP_Start_ECAM2_Master_Axis_Source_Unit_Type(CardNo, NodeID, SlotID,
    ushort SourceUnitType,   // 0=位置  1=时间
    int PerodicTime);        // 一个周期的时间，单位 μs
// ⚠️ 必须在 Profile_CamIn 之前调用

CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamIn_TimeMode(CardNo, NodeID, SlotID,
    CamNo, Periodic, SlaveAbsolute, SlaveOffset, SlaveScaling, StartMode,
    SlaveAxis_mm_Pulse, Slave_MaxVel_mm, Slave_Acc_mm, Slave_Dec_mm, SlaveAxis_Dir, BufferMode);
```

**适用**：固定节拍的往复动作。**不适用**焊缝跟踪——从轴按时间推进，无法与机器人 X 位置保持同步。

### 4.4 ECAM 一代（兼容保留，新功能不用）

13 个 API：`ECAM_Table_Data` / `ECAM_Velocity_Data` / `ECAM_Flying_Shears_Data` / `ECAM_Intermittence_Print_Data` / `ECAM_Set_Engage|DisEngage|Compensate_Parameters` / `ECAM_Move` / `ECAM_Move_ChangeTable` / `ECAM_Set_Scale` / `ECAM_Disable` / `ECAM_Get_Status`。新项目一律用 ECAM2。

### 4.5 通用约束（沿用原档，已核验）

- 主轴必须先运动，主轴不动从轴不动
- `Slave_MaxVel_mm` / 加减速必须大于凸轮表实际所需，否则报错或截断
- 多组凸轮表可预下载，运行中 `ChangeTable`（ECAM2 用 `Profile_Modify` 或重下 `Profile_Data`）切换
- 啮合前先写入初始主轴位置，避免从轴从静止突然跟随产生冲击

---

## 5. 机器人 X → Y 轴跟随选型

> **这是本项目焊缝跟踪的核心问题**：机器人沿 X 前进，上位机按激光相机测得的焊缝偏差算出 Y 目标，驱动台达 Y 轴（直线电机）纠偏。原档第三部分即此场景。

### 5.1 X 坐标来源 —— 本项目已具备，不需要原档示例代码

| 能力 | 本项目现状 | 原档示例 |
|---|---|---|
| RSI（UDP，1~12ms） | ✅ `Comm/Robot/KUKARobot/RSICommunication.cs`（`DataReceived` 事件、`KUKAPosition{X,Y,Z,A,B,C}`、`CurrentIPOC` 时间戳） | 仅 Demo 级 `KukaRsiReceiver` |
| EKI（TCP/XML） | ✅ `Comm/Robot/KUKARobot/EKICommunication.cs` | 仅 Demo 级 |
| 位置结构 | ✅ `KUKAPosition` / `KUKAFrame` / `KUKARobotData` | 无 |

**结论**：原档 3.3 全节（接收线程/RSI/EKI 代码）**不落地**，本项目复用既有 `RSICommunication`。

### 5.2 三种跟随方案的可行性裁决

| 方案 | 机制 | 台达可行性 | 结论 |
|---|---|---|---|
| **原档方案一**：ECAM2 虚拟轴主轴 | 把 X 写进虚拟轴，硬件插值 Y | ⛔ **不成立**：无虚拟轴 API（失准 #9/#10）；`SourceType=2` 不存在（#11） | 排除 |
| **变体**：ECAM2 + 板载脉冲输入（`SourceType=1`） | 机器人输出脉冲/编码器信号 → PCI-L221 脉冲输入口做主轴 | ⚠️ 取决于现场是否有该硬件信号 | 待现场确认；若机器人只有 RSI 数字量则排除 |
| **原档方案二**：PVT 实时点序列 | X → 算 Y → 组 PVT 点下发 | ✅ 可行；**建议用 B 套**（`Begin_Move` + `Continue_Move` + `Get_Information.RemainBufSize` 闭环） | **推荐** |
| **补充方案**：CSP 周期同步位置 | 每周期直接写目标位置 | ✅ 可行，`CS_ECAT_Slave_CSP_Sync_*` 已在 [[guides/DeltaEtherCAT-DevGuide]] 覆盖 | 备选（平滑度依赖上位机节拍） |

**推荐排序**：PVT B 套 > CSP 周期同步 > ECAM2（仅当现场具备脉冲主轴时）。

### 5.3 跟随链路（推荐方案）

```
KUKA RSI (1~12ms UDP)
   → RSICommunication.DataReceived → KUKAPosition.X
   → 与激光帧按 IPOC/时间戳插值对齐（原 RSIPositionBuffer 的职责，正运动删除后需重建）
   → 计算 Y 目标（焊缝偏差 + 前馈补偿 X_predicted = X + Vx × delay）
   → 入 PVT 缓冲队列
   → 水位低于阈值 → PVT_Continue_Move 续喂（或 Begin_Move 起手）
   → 台达主站三次样条插值 → Y 轴平滑跟随
```

⚠️ 原档 3.7 的 8 条注意事项**仍然有效**（X 单位换算、int 溢出、更新频率 ≥50Hz、Y 轴速度/加速度须留余量、啮合时机、X 中断时保持位置并报警、延迟前馈补偿），建议照做。

---

## 6. 待补 Native 声明清单

现行 `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs` 仅 16 个 extern，ECAM2 只覆盖 4 个、PVT 只覆盖 2 个。落地前需补（均已在 SDK 头文件核验存在）：

**PVT（9 个，现有 2）**：`PVT_Move`、`PVTComplete_Move`、`PVTComplete_Config`、`PVT_Sync_Move`、`PVT_Get_NowMotCount`、`PVT_Continue_Move`、`PVT_CycleStart`、`PVT_Get_Information`（+ 已有 `PVT_Begin_Move`）

**ECAM2（15 个，现有 4）**：`Delete_Profile_Data`、`Profile_Modify`、`Profile_CamSet`、`FlyingShear_Initial`、`FlyingShear_Move`、`RotaryCut_Initial`、`RotaryCut_Move`、`Set_Engage_Parameters`、`Set_DisEngage_Parameters`、`Set_Compensate_Parameters`、`Get_Slave_Info`、`Phasing`、`CamSwitch`、`CamSwitch_Status`、`Master_Axis_Source_Unit_Type`、`Profile_CamIn_TimeMode`、`Profile_Auto_Smooth`、`Get_PreviewTable`、`Set_Profile_Mode`

**状态检查（5 个，UI 用）**：`CS_ECAT_Master_Get_Connect_Status`、`CS_ECAT_Master_Check_Working_Counter`、`CS_ECAT_Master_Get_Working_Counter_ErrorCounter`、`CS_ECAT_Master_Get_Frame_Counter`、`CS_ECAT_Master_Get_Cycle_SpendTime`

**虚拟坐标（3 个，仅作坐标平移用，勿当虚拟主轴）**：`CS_ECAT_Master_Virtual_NodeID_Alias_Enable`、`CS_ECAT_Slave_CSP_Virtual_Set_Enable`、`CS_ECAT_Slave_CSP_Virtual_Set_Command`

> 分层铁律（ADR-039）：声明全在 L1 `Native/`；L2 `IMotion/` 零依赖不得出现；业务层只认 `MontionAxis` 抽象。

---

## 7. OPEN 项

1. **`TimeAbsMode` / `Finial` / `Retain` 语义**：PVT B 套 4 个 API 无手册，须现场实测
2. **`PVT_Continue_Move` 的 EntryPoint 前缀**：SDK 写作无下划线，疑笔误，待运行时验证
3. **PCI-L221 板载脉冲输入是否可用**：决定 ECAM2 方案能否复活（需查硬件 + 机器人是否有脉冲输出）
4. **焊缝跟踪终选方案**：待用户拍板（PVT B 套 / CSP 周期同步 / ECAM2+脉冲主轴）
5. **B 套单位是工程单位还是脉冲**：签名是 `double` 但手册无记载，须实测
6. **RSIPositionBuffer 的继任者**：正运动删除后 X/Y 时序对齐缓冲未重建，需随方案一同落地

---

## 相关页面

- [[guides/DeltaEtherCAT-DevGuide]] — 台达模块落地规范（基础能力）
- [[guides/DeltaEtherCAT-Deployment]] — DLL 部署与校验
- [[guides/DeltaEtherCAT-UIDesign]] — 台达 UI 设计（AntdUI 版）
- [[modules/MotionControl]] — 运控模块
- [[decisions/ADR-036-MotionControllerDeltaReplacement]] — 台达换轨决策
- [[decisions/ADR-037-ZMotionRemovalAndDeltaLanding]] — 正运动移除与台达落地

*来源：raw/delta/台达EtherCAT_PVT与电子凸轮运动开发指南.md（v1.3）；核验于 2026-09-07，对照 SDK 头文件 832 符号 + PM 手册 1018 页。*
