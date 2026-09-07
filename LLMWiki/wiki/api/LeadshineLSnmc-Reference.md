---
title: 雷赛 LSnmcControler 参考基线
date: 2026-09-05
tags: [API, 运控, 雷赛, Leadshine, 参考基线, EtherCAT]
source: "E:\\SoftwareGit\\HonorMachineTest\\PcomDeviceInterface\\MotionControl\\（IMotion/ 抽象层 + LSnmcControler/ 实现层）"
---

# 雷赛 LSnmcControler 参考基线

> **章节导航**：
>
> - [1. 定位与来源](#1-定位与来源)
> - [2. 目录结构](#2-目录结构)
> - [3. 抽象层契约](#3-抽象层契约)
> - [4. 实现层调用范式](#4-实现层调用范式)
> - [5. API 对照：雷赛 → 台达](#5-api-对照雷赛--台达)
> - [6. 关键实现片段](#6-关键实现片段)
> - [7. 台达不适用的项](#7-台达不适用的项)

本页是 **AdaWeldSystem 运动控制模块的参考基线**（2026-09-05 用户裁定：正运动实现当初就应当参考雷赛，台达落地以雷赛的组织形态与调用纪律为准）。

**雷赛 ≠ 迁移源**：本项目不会接入雷赛硬件，也不照抄 `smc_*` API。参考的是**架构与纪律**，API 一律以台达 SDK 为准（见 [[guides/DeltaEtherCAT-DevGuide]]）。

---

## 1. 定位与来源

| 项 | 内容 |
|----|------|
| 路径 | `E:\SoftwareGit\HonorMachineTest\PcomDeviceInterface\MotionControl\` |
| 厂商 | 雷赛智能（Leadshine），`ManufacturersType.LEADSHINE` |
| 控制器类型 | `ControlType.NmcController`（总线型运动控制器） |
| 命名空间 | 抽象层 `IMotion`，实现层 `LSnmcControler` |
| 参考值 | 三层分离、容器自注册、参数挂在轴上、**三段前置检查**、阻塞/非阻塞成对、急停贯穿 |

---

## 2. 目录结构

```
MotionControl/
├── IMotion/                     抽象层（厂商无关）
│   ├── MontionControl.cs        控制器抽象基类（3.5 KB，21 个抽象成员）
│   ├── MontionAxis.cs           轴抽象基类（9 KB，19 个抽象成员 + 20 个参数属性）
│   ├── MontionIO.cs             IO 抽象基类
│   ├── InputIO.cs / OutputIO.cs 数字输入/输出抽象基类
│   ├── Type.cs                  ControlType / ManufacturersType / IOType / InterpolationType
│   ├── IOParam.cs
│   └── InterpolationMontionParam.cs
├── LSnmcControler/              雷赛实现层
│   ├── LTSMC.cs                 P/Invoke 单文件（60 KB）
│   ├── LSnmcMontionControl.cs   控制器实现（330 行）
│   ├── LSnmcMontionAxis.cs      轴实现（625 行）
│   └── LSnmcInputIO.cs / LSnmcOutputIO.cs
├── MontionManager.cs            业务管理器（85 KB，厂商无关）
├── Cylinder.cs                  气缸业务类（厂商无关）
└── LiZhunCom485.cs              485 通讯
```

> ⚠️ 雷赛沿用 `Montion`（非 `Motion`）拼写，是历史遗留；本项目 `MotionControl/` 用正确拼写，**不必迁就**。

---

## 3. 抽象层契约

### 3.1 `MontionControl`（控制器）

| 类别 | 成员 |
|------|------|
| 状态字段 | `IsIniOK` / `EmergencyStop` / `CardNum` / `ConnectNo` / `NodeNo` / `MontionIP` |
| 集合 | `lstInputIO` / `lstOutputIO` / `lstMontionAxis` |
| 生命周期 | `IniControl(ref string strMsg)` / `CloseControl()` |
| 运动 | `InterpolationMontion(InterpolationMontionParam)` |
| 采集 | `ReadAD(ushort channel, ushort cardNo = 0)` / `ReadVolt(...)` |
| 安全 | `SetEmergencyStop(bool)` |
| 集合管理 | `AddIO` / `RemoveIO` / `ClearIO` / `AddAxis` / `RemoveAxis` / `GetInputIO` / `GetOutputIO` / `GetAxis` |
| IO 直读 | `GetInputIOStatus(int)` / `GetOutputIOStatus(int)` / `SetOutputIO(int, int)` |
| Modbus | `ReadModbusBit/Int/Float` + `WriteModbusBit/Int/Float` |
| 标识 | `GetName()` / `GetControlType()` / `GetManufacturersType()` |

### 3.2 `MontionAxis`（轴）

**参数属性**（一次配置、多次调用）：

| 组 | 成员 |
|----|------|
| 定位 | `AxisName` / `AxisNo` / `ConnectNo` / `NodeNo` / `SlotNo` / `AxisNotes` |
| 速度曲线 | `MinVel` / `MaxVel` / `AccTime` / `DecTime` / `STime` / `StopVel` / `HandMaxVel` |
| 回零 | `HomeDir` / `HomeMaxVel` / `HomeAccTime` / `HomeDecTime` / `HomeModel` |
| 硬件极性 | `org_logic` / `el_logic` / `el_enable` / `PlusOutModel` / `IsCheckPLimit` / `IsCheckNLimit` |
| 单位 | `Equiv`（脉冲当量） |
| 急停 | `EmergencyStop`（置位即刻 `AxisStop()`） |

**抽象成员**（19 个）：

```
IsMoving()                                      轴是否运动（0=运动中，1=停止）
WaitMoveDone()                                  阻塞等待到位 + 读停止原因
AxisStop(ushort stopmode = 0)                   0=减速停止 1=立即停止
GetAxisIO()                                     轴 IO 状态字
IsServoON() / ServoOn() / ServoOff()
GetStopReason()
AxisHome() / AxisHomeNoBlock() / WaitHomeDone()
AbsMove(pos [, posi_mode])                      3 个重载（阻塞）
AbsMoveNoBlock(pos, ...)                        3 个重载（非阻塞）
JogMove(...)                                    3 个重载
HandMove(ushort dir = 0)                        手动（用 HandMaxVel）
GetAxisPos() / SetAxisHomePos()
```

### 3.3 `InputIO` / `OutputIO`

| 成员 | 说明 |
|------|------|
| `_IOName` / `_IONo` / `_IOEnable` | 名称、全局编号、使能开关 |
| `IsON()` | 输入：`GetIOStatus() == 0`（低电平有效） |
| `GetIOStatus()` | 先查总线错误码，失败返回 1 |
| `SetON()` / `SetOFF()` | 输出：`SetON()` 写 0（NPN 低电平有效），PNP 需反转 |
| `EmergencyStop` | 由控制器 `SetEmergencyStop` 广播置位 |

---

## 4. 实现层调用范式

### 4.1 三段前置检查（每个运动入口都重复，最值得复制的纪律）

```csharp
// ① 总线错误码
LTSMC.nmcs_get_errcode(_ConnectNo, 2, ref errcode);        // 第 2 参 2 = EtherCAT 总线
if (errcode != 0) { Log("总线状态错误"); return false; }

// ② 轴状态机（DS402）
LTSMC.nmcs_get_axis_state_machine(_ConnectNo, AxisNo, ref State_Machine);
if (State_Machine != 4) { Log("轴状态错误"); return false; }   // 4 = Operation Enabled

// ③ 运动中检查（防指令叠罗汉）
if (IsMoving() == 0) { Log("轴正处于运动状态"); return false; }  // 注意：0 = 运动中
```

**台达对应**（见 [[guides/DeltaEtherCAT-DevGuide]] §7.2）：

| 雷赛 | 台达 |
|------|------|
| `nmcs_get_errcode(ConnectNo, 2, ref e)` | `CS_ECAT_Master_Get_Connect_Status(card, ref opState, ref alarm)`（判 `opState==3 && alarm==0`） |
| `nmcs_get_axis_state_machine(...)` 返 4 | `CS_ECAT_Slave_Motion_Get_StatusWord(...)` + 解析 **bit2** |
| `smc_check_done(...)` == 0 运动中 | `CS_ECAT_Slave_Motion_Get_Mdone(...)`（0=运动中，1=完成） |

### 4.2 单位换算（雷赛是控制器侧，台达必须改 PC 侧）

```csharp
LTSMC.smc_set_equiv(_ConnectNo, _AxisNo, _Equiv);              // 当量写进控制器（一次）
LTSMC.smc_set_profile_unit(_ConnectNo, _AxisNo, MinVel, MaxVel, AccTime, DecTime, StopVel);
LTSMC.smc_set_s_profile(_ConnectNo, _AxisNo, 0, _STime);
LTSMC.smc_pmove_unit(_ConnectNo, _AxisNo, pos, posi_mode);     // 直接吃工程单位
```

> ⚠️ **方向性差异**：雷赛 `*_unit` 后缀 API 由控制器换算，源码里**看不到任何乘除**。
> **台达无 `SetUnits`/`equiv` 机制**，所有参数为脉冲，必须在实现层手动换算（`mm × Equiv = pulse`）。切勿照抄「源码里没换算」。

### 4.3 阻塞 / 非阻塞成对

| 阻塞 | 非阻塞 | 补一个等待 |
|------|--------|-----------|
| `AbsMove(pos)` | `AbsMoveNoBlock(pos)` | `WaitMoveDone()` |
| `AxisHome()` | `AxisHomeNoBlock()` | `WaitHomeDone()` |

阻塞版内部是 `while (IsMoving() == 0) { if (EmergencyStop) return false; Application.DoEvents(); }`。
**本项目做法**：`Application.DoEvents()` 在 WinForms 主线程可用，但运控在工作线程中应改为 `Thread.Sleep(1~5)` + 超时 + 急停检查。

### 4.4 急停贯穿

```
MontionControl.EmergencyStop (setter)
   ├─ 遍历 lstOutputIO[i].EmergencyStop = value
   └─ 遍历 lstMontionAxis[i].EmergencyStop = value
            └─ setter 内：if (IsEmergencyStop) AxisStop();

MontionAxis.WaitMoveDone / AxisHome 的 while 循环：每圈 if (EmergencyStop) return false;
MontionControl.InterpolationMontion：if (EmergencyStop) return false;
```

### 4.5 到位后判停止原因

```csharp
while (IsMoving() == 0) { if (EmergencyStop) return false; Application.DoEvents(); }
int nReason = GetStopReason();          // smc_get_stop_reason
if (nReason == 1 || nReason == 2) {     // 1/2 = 非正常停止
    Log("非正常停止 错误代码 " + nReason);
    IsOK = false;
}
```

**台达无 `Get_Stop_Reason`**，改用 `Motion_Get_StatusWord` 位解析 + `Motion_Get_Record_Axis_Unusual`。

### 4.6 伺服使能要轮询状态机

```csharp
LTSMC.nmcs_get_errcode(_ConnectNo, 2, ref errcode);
if (errcode == 0)
{
    LTSMC.nmcs_set_axis_enable(_ConnectNo, _AxisNo);
    LTSMC.nmcs_get_axis_state_machine(_ConnectNo, _AxisNo, ref axis_statemachine);
    while (axis_statemachine != 4 && Environment.TickCount - startTime < 3000)
    {
        LTSMC.nmcs_set_axis_enable(_ConnectNo, _AxisNo);          // 重试使能
        LTSMC.nmcs_get_axis_state_machine(_ConnectNo, _AxisNo, ref axis_statemachine);
    }
}
```

**台达对应**：`Motion_Set_MoveMode(8=CSP)` → `Motion_Set_Svon(1)` → 轮询 `Motion_Get_StatusWord` 的 bit2，超时 3 s。

---

## 5. API 对照：雷赛 → 台达

> 台达侧名称均已对 `inc/C#/EtherCAT_DLL.cs`（832 个声明）逐字核验。

| 能力 | 雷赛 LTSMC | 台达 CS_ECAT（SDK 真实名） |
|------|-----------|---------------------------|
| 连接/初始化 | `smc_board_init(ConnectNo, 2, IP, 0)` | `CS_ECAT_Master_Initial(cardNo)` + 轮询 `Master_Check_Initial_Done` |
| 关闭 | `smc_board_close` | `CS_ECAT_Master_Reset` + `CS_ECAT_Master_Close` |
| 卡枚举 | （TCP 直连，无需） | `CS_ECAT_Master_Open` + `CS_ECAT_Master_Get_CardSeq` |
| 从站信息 | （无） | `CS_ECAT_Master_Get_SlaveNum` / `Get_Slave_Info` |
| 总线错误 | `nmcs_get_errcode(ConnectNo, 2, ref e)` | `CS_ECAT_Master_Get_Connect_Status` |
| 轴状态机 | `nmcs_get_axis_state_machine` 返 4 | `CS_ECAT_Slave_Motion_Get_StatusWord`（bit2/bit3） |
| 轴使能 | `nmcs_set_axis_enable` | `CS_ECAT_Slave_Motion_Set_MoveMode(8)` + `Set_Svon(1)` |
| 伺服断 | `smc_write_sevon_pin(no, axis, 1)` | `CS_ECAT_Slave_Motion_Set_Svon(..., 0)` |
| 报警复位 | — | `CS_ECAT_Slave_Motion_Ralm` |
| 运动中 | `smc_check_done`（0=运动中） | `CS_ECAT_Slave_Motion_Get_Mdone`（0=运动中） |
| 停止原因 | `smc_get_stop_reason` | 无直接对应 → `Get_StatusWord` + `Get_Record_Axis_Unusual` |
| 清停止原因 | `smc_clear_stop_reason` | 无直接对应 |
| 设当量 | `smc_set_equiv` | **无** → 实现层 PC 侧换算 |
| 速度曲线 | `smc_set_profile_unit` | **无独立 API** → 随 `CSP_Start_Move` 传入 |
| S 曲线 | `smc_set_s_profile(no, axis, 0, STime)` | `CS_ECAT_Slave_CSP_Scurve_Rate` |
| 点位运动 | `smc_pmove_unit(no, axis, pos, mode)` | `CS_ECAT_Slave_CSP_Start_Move(card,node,slot, Dist,StrVel,ConstVel,EndVel, Tacc,Tdec, SCurve, IsAbs)` |
| Jog | `smc_vmove(no, axis, dir)` | `CS_ECAT_Slave_CSP_Start_V_Move(card,node,slot, Dir,StrVel,ConstVel, Tacc, SCurve)` |
| 停止 | `smc_stop(no, axis, mode)` | `CS_ECAT_Slave_Motion_Sd_Stop(card,node,slot, Tdec)` |
| 急停 | （软件级） | `CS_ECAT_Slave_Motion_Emg_Stop` + 硬件 `CS_ECAT_GPIO_Emg_Enable` / `CS_ECAT_GPIO_Emg_Soft_Clear` |
| 读位置 | `smc_get_position_unit` | `CS_ECAT_Slave_Motion_Get_Position` / `Get_Command` / `Get_Actual_Position` |
| 写位置 | `smc_set_position_unit` | `CS_ECAT_Slave_Motion_Set_Position` |
| 回零配置 | `smc_set_homemode(no, axis, dir, 1, model, 0)` | `CS_ECAT_Slave_CSP_Home_Axis_Config(card, homeNo, node,slot, Mode,Offset, FirstVel,SecondVel, Tacc, Dir, Shift)` |
| 回零曲线 | `smc_set_home_profile_unit` | 含在 `Home_Axis_Config` 的 FirstVel/SecondVel/Tacc |
| 回零执行 | `smc_home_move` | `CS_ECAT_Slave_CSP_Home_Move(card, homeNo, limitNo)` |
| 回零结果 | `smc_get_home_result` | `CS_ECAT_Slave_CSP_Home_Status(card, homeNo, ref status)` |
| 限位模式 | `smc_set_el_mode` | `CS_ECAT_Slave_CSP_Remote_Limit_Config/Enable/Edge_Trigger_Level` |
| 原点电平 | `smc_set_home_pin_logic` | `Remote_Limit_Edge_Trigger_Level` 的 HomeSensor 参数 |
| 软限位 | `smc_set_softlimit_unit`（工程单位） | `CS_ECAT_Slave_CSP_Set_Softlimit`（脉冲） |
| 读输入 | `smc_read_inbit(ConnectNo, IONo)` | `CS_ECAT_Read_InBit(card, bitNo, ref v)` |
| 写输出 | `smc_write_outbit(ConnectNo, IONo, v)` | `CS_ECAT_Write_OutBit(card, bitNo, v)` |
| 轴 IO 状态 | `smc_axis_io_status` | `Get_StatusWord` 位 + `Remote_Limit_*` |
| AD 读（PDO） | `nmcs_get_node_od(no, 2, cardNo, ch, 2, 32, ref v)` | `CS_ECAT_Slave_PDO_Get_OD_Data` |
| Modbus | `smc_get_modbus_0x` / `smc_set_modbus_0x` / `smc_get_modbus_4x` / `smc_set_modbus_4x` | **无 Modbus** → PDO/SDO |
| 直线插补 | `smc_line_unit` | `CS_ECAT_Slave_CSP_Start_Multiaxes_Move` |
| 圆弧插补 | `smc_arc_move_center_unit` | `CS_ECAT_Slave_CSP_Start_Arc_Move` |
| 齿轮/凸轮 | — | `CSP_Start_GearIn_Move` / `Start_ECAM2_*` / `CSP_Virtual_Set_Command` |

---

## 6. 关键实现片段

### 6.1 回零完整链路（阻塞版）

```csharp
LTSMC.smc_clear_stop_reason(_ConnectNo, _AxisNo);
LTSMC.smc_set_pulse_outmode(_ConnectNo, _AxisNo, _PlusOutModel);   // 台达无此步
LTSMC.smc_set_equiv(_ConnectNo, _AxisNo, _Equiv);                  // 台达无此步
LTSMC.smc_set_homemode(_ConnectNo, _AxisNo, _HomeDir, 1, _HomeModel, 0);
LTSMC.smc_set_home_profile_unit(_ConnectNo, _AxisNo, _HomeMaxVel / 2, _HomeMaxVel, _HomeAccTime, _HomeDecTime);
LTSMC.smc_home_move(_ConnectNo, _AxisNo);
while (IsMoving() == 0) { if (IsEmergencyStop) return false; Application.DoEvents(); }
LTSMC.smc_get_home_result(_ConnectNo, AxisNo, ref state);
if (state == 1)
{
    LTSMC.smc_set_position_unit(_ConnectNo, AxisNo, 0);            // 回零后指令清零
    return true;
}
return false;                                                       // 失败
```

> 台达差异：无 `set_pulse_outmode` / `set_equiv`；回零前需先 `Remote_Limit_Config` 把原点/正负限位的 DI 点位映射到轴；回零后同样要 `Motion_Set_Position(0)`。

### 6.2 输入 IO 读取（总线异常时返回安全值）

```csharp
public override int GetIOStatus()
{
    ushort errcode = 0;
    LTSMC.nmcs_get_errcode(_ConnectNo, 2, ref errcode);
    if (errcode != 0) { Log("总线异常，无法获取状态"); return 1; }   // 1 = 非 ON（安全侧）
    if (!_IOEnable) return 1;
    int num = 0;
    try { num = LTSMC.smc_read_inbit(_ConnectNo, _IONo); } catch { }
    return num;
}
```

> 台达对应：`Master_Get_Connect_Status` → `CS_ECAT_Read_InBit`。同样保持「异常返回非 ON」的**安全侧默认**。

---

## 7. 台达不适用的项

| 雷赛项 | 台达处置 | 原因 |
|--------|----------|------|
| `smc_set_equiv` + `*_unit` API | **删**：改 PC 侧乘除 | 台达无当量机制 |
| `smc_set_pulse_outmode` | **删** | EtherCAT 无脉冲输出模式 |
| `PlusOutModel` 轴属性 | **删** | 同上 |
| Modbus 6 个抽象成员 | **替换**为 PDO/SDO | 台达无 Modbus 通道 |
| `nmcs_get_errcode(no, 2, ...)` 的「2」 | **替换**为 `Get_Connect_Status` | 总线类型常量语义不同 |
| `nmcs_get_axis_state_machine` 返 4 | **替换**为 `Get_StatusWord` 位解析 | 台达不给状态机枚举 |
| `smc_get_stop_reason` / `clear_stop_reason` | **替换**为状态字 + `Record_Axis_Unusual` | 无对应 API |
| `Application.DoEvents()` 等待 | **改** `Thread.Sleep` + 超时 | 本项目运控在工作线程 |
| `ConnectNo + AxisNo` | **改** `CardNo + NodeID + SlotNo` | EtherCAT 从站拓扑寻址 |
| （无） | **新增** `DeltaSlaveScanner` | 台达需扫描 VendorID/ProductCode |
| （无） | **新增** `GPIO_Emg_Enable` / `GPIO_Emg_Get_Status` / `GPIO_Emg_Soft_Clear` 硬件急停 | 卡级急停，雷赛无 |
| `GetManufacturersType()` | 保留语义 | 本项目用 L2 `ManufacturerType` 枚举（`Delta` / `Leadshine` / …），不再有独立厂商开关配置 |

---

## 相关页面

- [[guides/DeltaEtherCAT-DevGuide]] — 台达落地指导（以雷赛为参考基线）
- [[api/DeltaEtherCAT-Native]] — 台达原生 API 全量速查（832 个）
- [[modules/MotionControl]] — 本项目运控模块现状
- 源文件：`E:\SoftwareGit\HonorMachineTest\PcomDeviceInterface\MotionControl\`
