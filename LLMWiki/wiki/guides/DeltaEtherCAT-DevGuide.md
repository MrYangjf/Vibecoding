---
title: 台达 EtherCAT 运动控制模块落地规范
date: 2026-09-06
tags: [指导, 运控, 台达, EtherCAT, 雷赛基线, ECAM2, P/Invoke, 目录结构, 对外消费]
source: "原档 raw/delta/运动控制模块开发文档_台达版.md（目录结构与消费关系以原档为准）+ 雷赛参考实现 HonorMachineTest/PcomDeviceInterface/MotionControl/ + 台达 SDK 头文件核验"
---

# 台达 EtherCAT 运动控制模块 — 落地规范

> 模块基于台达 **PCI-L221 EtherCAT 主站卡**，目标框架 **.NET Framework 4.8**，定位为主程序中的运动控制模块。
> 本页是**全新模块的完整设计**：文件结构、命名、对外消费关系均以开发指导原档为准。
> 原档：`raw/delta/运动控制模块开发文档_台达版.md`（1323 行，13 章 + 附录 A/B）

**基线声明**：架构形态与抽象层契约参考雷赛 `LSnmcControler`（`E:\SoftwareGit\HonorMachineTest\PcomDeviceInterface\MotionControl\`），可借鉴的六条纪律见 [[api/LeadshineLSnmc-Reference]]。本页所有台达 API 名均经本机 SDK 头文件比对核验，原档失准处见 §12。

**边界声明**：振镜与对焦不属于本模块，由焊接头侧承接（见 [[modules/LaserWeldHead]]）。

## 章节导航

| 章 | 内容 | 用途 |
|----|------|------|
| §1 | 模块定位与三层架构 | 建立整体认知 |
| §2 | 目录结构与文件清单 | **照此建目录** |
| §3 | 对外消费契约 | **照此对接上层** |
| §4 | L1 原生封装层 `Native/` | 实现 P/Invoke |
| §5 | L3 台达实现层 `DeltaEtherCAT/` | 实现厂商逻辑 |
| §6 | L2 抽象接口层 `IMotion/` | 对外契约的定义处 |
| §7 | 业务层 `MontionManager` + `AxisRegistry` / `IORegistry` / `CylinderRegistry` | 上层如何组织 |
| §8 | 生命周期与初始化流程 | 上电/下电序列 |
| §9 | 关键机制 | 单位换算/前置检查/使能/回零/IO/急停 |
| §10 | 典型使用示例 | 照抄即可跑 |
| §11 | 抽象层 ↔ 台达 API 映射速查 | 写实现时对照 |
| §12 | API 名核验门禁 + 7 处订正 | 写完后必跑 |
| §13 | 注意事项与最佳实践 | 避坑 |
| §14 | 落地清单 | 逐项打勾 |
| §15 | OPEN 项 | 待定事项 |

---

## 1. 模块定位与三层架构

### 1.1 三层架构

自底向上三层，外加一层业务层：

| 层级 | 文件夹 | 职责 | 对应雷赛 |
|------|--------|------|----------|
| L1 原生封装层 | `DeltaEtherCAT/Native/` | 对 `EtherCAT_DLL.dll` 的 P/Invoke 封装，按功能域分文件 | `LSnmcControler/LTSMC.cs` |
| L2 抽象接口层 | `IMotion/` | 控制器/轴/IO 抽象基类与枚举，**与厂商无关** | `IMotion/` |
| L3 台达实现层 | `DeltaEtherCAT/` | 继承 L2，调用 L1，实现台达特有逻辑 | `LSnmcControler/` |
| 业务层 | 模块根 | `MontionManager` 聚合、三张注册表（轴 / IO / 气缸）、`Cylinder` 气缸实体在 `IMotion/` | 同名 |

**核心原则**：业务层面向 **L2 抽象**编程。L3 只在初始化时 `new` 一次，此后全程通过抽象基类访问。厂商切换 = 换一个 L3 目录，业务代码不动。

### 1.2 平台与部署约束

| 约束 | 内容 |
|------|------|
| 目标框架 | .NET Framework 4.8 |
| 平台目标 | 必须 `x86` 或 `x64`，**禁止 AnyCPU**（否则 `DllImport` 抛 `BadImageFormatException`） |
| DLL | 原生非托管 C DLL，安装路径 `D:\Program Files (x86)\Delta Industrial Automation\EtherCAT\dll\` |
| 部署 | `EtherCAT_DLL.dll`（x86）/ `EtherCAT_DLL_x64.dll`（x64）复制到可执行文件同目录 |
| 引用方式 | **不能直接添加引用**，必须 `DllImport` + `EntryPoint`（下划线前缀 C 函数名修饰） |

平台选择写法：

```csharp
#if X86
    private const string DllPath = "EtherCAT_DLL.dll";
#else
    private const string DllPath = "EtherCAT_DLL_x64.dll";
#endif
```

### 1.3 台达的六个固有特点

这些客观差异决定了 L3 实现层必须做的事：

| 特点 | 后果 |
|------|------|
| 轴定位三元 `CardNo + NodeId + SlotNo` | 轴/IO 对象构造时必须额外传 `nodeId` / `slotNo` |
| API 全部**脉冲单位** | 工程单位 ↔ 脉冲的换算必须在 L3 完成（见 §9.1） |
| 主站初始化**异步** | 必须轮询 `Master_Check_Initial_Done`，不能同步等待 |
| 伺服使能需先设模式 | `Set_Move_Mode(8=CSP)` → `Set_Svon(1)` → 轮询状态字 bit2 |
| 从站需枚举识别 | 需 `DeltaSlaveScanner` 按 VendorID + ProductCode 匹配设备类型 |
| IO 寻址加 `BitNo` | `CardNo + NodeId + SlotNo + BitNo` |

---

## 2. 目录结构与文件清单

> 本章照搬原档 §3，落地时**逐文件对应建立**。

### 2.1 完整目录树

```
MotionControl/                                    # 运动控制模块（主程序中的一个文件夹）
├── MontionManager.cs                             # 运动管理器（持有三张注册表）
├── AxisRegistry.cs                               # 轴注册表
├── IORegistry.cs                                 # IO 注册表（输入/输出分表）
├── CylinderRegistry.cs                           # 气缸注册表
│
├── IMotion/                                      # L2 抽象接口层
│   ├── Type.cs                                   # 枚举定义
│   ├── MontionControl.cs                         # 控制器抽象基类
│   ├── MontionAxis.cs                            # 轴抽象基类（默认实现 IPVTMotion）
│   ├── MontionIO.cs                              # IO 抽象基类
│   ├── InputIO.cs                                # 数字输入抽象基类
│   ├── OutputIO.cs                               # 数字输出抽象基类
│   ├── Cylinder.cs                               # 气缸实体（多 IO 复合，厂商无关）
│   ├── IPVTMotion.cs                             # PVT 能力契约 + PVTPoint + PVTInformation + PVTResult
│   └── InterpolationMontionParam.cs              # 插补运动参数类
│
└── DeltaEtherCAT/                                # L3 台达实现层
    ├── Native/                                   # L1 原生封装层（按功能域分文件）
    │   ├── EtherCATMasterNative.cs              # 主站/从站/SDO/PDO 管理 + 链路健康
    │   ├── EtherCATMotionNative.cs              # 运动控制（CSP/CSV/CST/回零/软限位）
    │   ├── EtherCATIONative.cs                  # 数字 IO / AD / DA
    │   ├── EtherCATAdvancedNative.cs            # 高级功能（插补/龙门/锁存/虚拟坐标偏移）
    │   ├── EtherCATPVTNative.cs                 # PVT A 套（int 脉冲）+ B 套（double 流式）
    │   ├── EtherCATEcam2Native.cs               # ECAM2 电子凸轮（建表/啮合/调整/飞剪/状态）
    │   └── DeltaErrorCode.cs                     # 错误码常量（按功能分组）
    │
    ├── DeltaMontionControl.cs                    # 台达控制器实现
    ├── DeltaMontionAxis.cs                       # 台达轴实现
    ├── DeltaInputIO.cs                           # 台达数字输入实现
    ├── DeltaOutputIO.cs                          # 台达数字输出实现
    └── DeltaSlaveScanner.cs                      # 从站扫描器（台达特有）
```

### 2.2 文件职责清单

| 文件 | 类名 | 类型 | 职责 |
|------|------|------|------|
| `EtherCATMasterNative.cs` | `EtherCATMasterNative` | `public static class` | 主站开关/初始化/复位、从站状态、SDO、PDO |
| `EtherCATMotionNative.cs` | `EtherCATMotionNative` | `public static class` | 模式/使能/报警复位、状态字、位置速度力矩、CSP/CSV/CST、回零、软限位、电子齿轮 |
| `EtherCATIONative.cs` | `EtherCATIONative` | `public static class` | 数字 IO 单路与整体读写、AD/DA（经 PDO OD） |
| `EtherCATAdvancedNative.cs` | `EtherCATAdvancedNative` | `public static class` | 多轴插补/圆弧/螺旋/同步、电子凸轮、龙门、运动缓冲、表运动、PVT、Touch Probe |
| `DeltaErrorCode.cs` | `DeltaErrorCode` | `public static class` | 错误码常量 + `GetMessage(ushort)` |
| `DeltaSlaveScanner.cs` | `DeltaSlaveScanner` | `public class` | 扫描总线从站，识别设备类型，输出 `SlaveInfos` |
| `DeltaMontionControl.cs` | `DeltaMontionControl` | `: MontionControl` | 主站初始化/关闭、轴与 IO 集合、总线健康检查、全局急停 |
| `DeltaMontionAxis.cs` | `DeltaMontionAxis` | `: MontionAxis` | 伺服/回零/点位/点动/位置读写/状态读取、单位换算 |
| `DeltaInputIO.cs` | `DeltaInputIO` | `: InputIO` | 单路数字输入读取 |
| `DeltaOutputIO.cs` | `DeltaOutputIO` | `: OutputIO` | 单路数字输出读写 |

### 2.3 与雷赛目录对应关系

| 雷赛 | 台达 | 说明 |
|------|------|------|
| `LSnmcControler/LTSMC.cs` | `DeltaEtherCAT/Native/*.cs` | 原生 P/Invoke 封装（台达按功能域拆为 4 文件 + 错误码） |
| `LSnmcControler/LSnmcMontionControl.cs` | `DeltaEtherCAT/DeltaMontionControl.cs` | 控制器实现 |
| `LSnmcControler/LSnmcMontionAxis.cs` | `DeltaEtherCAT/DeltaMontionAxis.cs` | 轴实现 |
| `LSnmcControler/LSnmcInputIO.cs` | `DeltaEtherCAT/DeltaInputIO.cs` | 输入实现 |
| `LSnmcControler/LSnmcOutputIO.cs` | `DeltaEtherCAT/DeltaOutputIO.cs` | 输出实现 |
| （无） | `DeltaEtherCAT/DeltaSlaveScanner.cs` | 从站扫描，台达特有 |
| `IMotion/*` | `IMotion/*` | 抽象层，形态一致 |
| `Cylinder.cs` | `IMotion/Cylinder.cs` | 厂商无关，2026-09-07 由模块根移入 L2 |
| `MontionManager.cs` | `MontionManager.cs` | 仅初始化时 `new` 的类型不同 |
| （无） | `AxisRegistry.cs` / `IORegistry.cs` / `CylinderRegistry.cs` | 注册表，把轴/IO/气缸登记进控制器 |
| （无） | `DeltaMotionConfig.cs` / `DeltaAxisConfig.cs` / `DeltaIOConfig.cs` | 配置实体（均为普通实例类），填补 `MotionConfig.cs` 删除后的空缺 |
| （无） | `IMotion/IPVTMotion.cs` | PVT 能力契约 + 数据结构（全大写 PVT） |

### 2.4 命名规范

| 规则 | 说明 | 示例 |
|------|------|------|
| 文件名 = 主类名 | 一个文件一个公共类 | `DeltaMontionAxis.cs` |
| 保留雷赛拼写 `Montion` | **不**改为 `Motion`，与抽象层保持一致 | `MontionControl` / `MontionAxis` |
| 实现类前缀 `Delta` | 对应雷赛 `LSnmc` 前缀 | `DeltaMontionControl` |
| Native 层按功能域分文件 | 不用台达官方单一大文件，按 API 域拆分 | `EtherCATMotionNative.cs` |
| Native 方法名保留台达风格 | 对应雷赛保留 `smc_*`，台达保留 `CS_ECAT_*` | `CS_ECAT_Master_Open` |
| 抽象层文件名与雷赛一致 | 便于对照 | `MontionAxis.cs` |

---

## 3. 对外消费契约

> 本章照搬原档 §9，是**上层对接本模块的唯一依据**。

### 3.1 消费关系图

```
主程序
  └──引用→ MotionControl 模块
            ├── MontionManager.cs ──引用→ IMotion (L2 抽象层)
            │                         └──引用→ DeltaEtherCAT (仅初始化时 new)
            ├── AxisRegistry.cs / IORegistry.cs / CylinderRegistry.cs ──引用→ IMotion
            │
            ├── IMotion/ (L2，无外部依赖)
            │
            └── DeltaEtherCAT/ (L3)
                  ├── Native/
                  │   ├── EtherCATMasterNative.cs ──DllImport→ EtherCAT_DLL.dll
                  │   ├── EtherCATMotionNative.cs ──DllImport→ EtherCAT_DLL.dll
                  │   ├── EtherCATIONative.cs     ──DllImport→ EtherCAT_DLL.dll
                  │   ├── EtherCATAdvancedNative.cs ─DllImport→ EtherCAT_DLL.dll
                  │   └── DeltaErrorCode.cs ──引用→ EtherCATMasterNative.cs
                  ├── DeltaSlaveScanner.cs ──引用→ Native/EtherCATMasterNative.cs + DeltaErrorCode.cs
                  ├── DeltaMontionControl.cs ──继承→ MontionControl, 引用→ Native/* + DeltaSlaveScanner.cs
                  ├── DeltaMontionAxis.cs ──继承→ MontionAxis, 引用→ Native/* + DeltaMontionControl.cs
                  ├── DeltaInputIO.cs ──继承→ InputIO, 引用→ Native/* + DeltaMontionControl.cs
                  └── DeltaOutputIO.cs ──继承→ OutputIO, 引用→ Native/* + DeltaMontionControl.cs
```

### 3.2 消费关系明细

| 消费者 | 消费对象 | 消费方式 |
|--------|----------|----------|
| `MontionManager` | `MontionControl` | 字段持有 + 方法调用；初始化时 `new DeltaMontionControl` |
| `MontionManager` | `MontionAxis` / `InputIO` / `OutputIO` / `Cylinder` | 经三张注册表聚合，按名称索引并回灌进控制器 |
| `DeltaMontionControl` | `Native/*` | 静态方法调用（主站 Open/Initial/Close） |
| `DeltaMontionControl` | `DeltaSlaveScanner` | 组合（字段持有），从站扫描委托 |
| `DeltaMontionAxis` | `Native/*` | 静态方法调用（全部运动控制 API） |
| `DeltaMontionAxis` | `DeltaMontionControl` | 构造注入（引用），取 CardNo、查急停 |
| `DeltaInputIO` / `DeltaOutputIO` | `Native/*` | 静态方法调用（DIO 单路读写） |
| `DeltaInputIO` / `DeltaOutputIO` | `DeltaMontionControl` | 构造注入（引用），取 CardNo |
| `DeltaSlaveScanner` | `Native/EtherCATMasterNative` | 静态方法调用（从站扫描） |
| `DeltaErrorCode` | `Native/EtherCATMasterNative` | 静态方法调用（错误描述） |
| `Cylinder`（位于 `IMotion/`） | `InputIO` / `OutputIO` | 字段持有，厂商无关；`GetAllIO()` 枚举占用点位供注册表登记 |

### 3.3 依赖方向铁律

1. **`IMotion/` 零外部依赖**——不引用任何厂商、不引用业务层、不引用 Native。
2. **L3 → L2 单向**：`DeltaEtherCAT/` 继承并依赖 `IMotion/`，反向禁止。
3. **Native 只被 L3 调用**：业务层禁止直接调用 `CS_ECAT_*`（错误码查询除外）。
4. **业务层只认抽象**：`MontionManager` / `Cylinder` 的成员类型一律用 `MontionControl` / `MontionAxis` / `InputIO` / `OutputIO`，不出现 `Delta*` 具体类型。
5. **L3 具体类型只在两处出现**：初始化时的 `new`；需要台达特有能力时的显式向下转型（`(DeltaMontionControl)mgr.MontionControl`）。

### 3.4 上层消费示例（最小契约面）

```csharp
// 上层只需 4 件事：初始化 → 建轴/建 IO → 注册 → 用
var mgr = MontionManager.Instance;
string msg = "";
if (!mgr.Initialization("设备名", ref msg)) { /* 处理失败 */ }

var xAxis = new DeltaMontionAxis(mgr.MontionControl, "X轴", nodeId: 1, slotNo: 0)
{
    Equiv = 0.0001, MaxVel = 50.0, MinVel = 0,
    AccTime = 0.2, DecTime = 0.2, STime = 0.05, StopVel = 0,
    HomeMode = 2, HomeDir = 1, HomeMaxVel = 20.0
};
mgr.AddAxis("X", xAxis);

xAxis.ServoOn();
xAxis.Home();
xAxis.AbsMove(100.0);          // 移动到 100mm（工程单位）
double pos = xAxis.GetPosition();

mgr.Close();
```

---

## 4. L1 原生封装层（Native/）

> 全部为 `public static class`，方法名保留台达官方 `CS_ECAT_*` 风格，便于对照官方示例。
> **本章出现的 API 名均为 SDK 实证名**；原档中 7 处失准名已订正，见 §12。

### 4.1 EtherCATMasterNative.cs — 主站与从站管理

#### 主站管理

| 台达 API | 说明 |
|----------|------|
| `CS_ECAT_Master_Open(ref ushort existcard)` | 打开主站，返回检测到的卡数量 |
| `CS_ECAT_Master_Initial(ushort CardNo)` | 初始化指定卡号主站 |
| `CS_ECAT_Master_Reset(ushort CardNo)` | 复位主站 |
| `CS_ECAT_Master_Close()` | 关闭主站（释放所有卡） |
| `CS_ECAT_Master_Get_CardSeq(ushort Seq, ref ushort CardNo)` | 按序号获取卡号 |
| `CS_ECAT_Master_Get_SlaveNum(ushort CardNo, ref ushort SlaveNum)` | 获取从站数量 |
| `CS_ECAT_Master_Get_Slave_Info(CardNo, SeqId, ref NodeID, ref VendorID, ref ProductCode, ref RevisionNo, ref DCTime)` | 获取从站信息 |
| `CS_ECAT_Master_Check_Initial_Done(ushort CardNo, ref ushort InitDone)` | 初始化完成检查：`0`=完成，`1`=进行中，`99`=失败 |
| `CS_ECAT_Master_Get_Initial_ErrorCode(ushort CardNo)` | 获取初始化错误码 |
| `CS_ECAT_Master_Get_Return_Code_Message(ushort ReturnCode, string Message)` | 返回码文字描述 |

#### 从站状态管理

| 台达 API | 说明 |
|----------|------|
| `CS_ECAT_Slave_Get_Connect_Status(CardNo, NodeID, SlotNo, ref OpState, ref AlarmStatus)` | `OpState`: 0=Init,1=PreOP,2=SafeOP,3=OP；`AlarmStatus`: 0=正常,1=报警 |
| `CS_ECAT_Slave_Request_State(CardNo, NodeID, SlotNo, OpState)` | 请求从站状态切换 |
| `CS_ECAT_Slave_Get_EMCY_Data(CardNo, NodeID, SlotNo, ref ErrorCode, ref ErrorRegister, ref Data)` | 获取紧急消息 EMCY |

#### SDO / PDO

| 台达 API | 说明 |
|----------|------|
| `CS_ECAT_Slave_SDO_Send_Message(...)` | SDO 写（非阻塞） |
| `CS_ECAT_Slave_SDO_Read_Message(...)` | SDO 读（非阻塞） |
| `CS_ECAT_Slave_SDO_Quick_Send_Message(...)` | SDO 快速写（阻塞） |
| `CS_ECAT_Slave_SDO_Check_Done(CardNo, NodeID, SlotNo, ref Done)` | `Done`: 0=完成, 1=进行中 |
| `CS_ECAT_Slave_PDO_Get_OD_Data(CardNo, NodeID, SlotNo, IOType, ODIndex, ODSubIndex, ByteSize, ref byte Data)` | 读 PDO OD 数据（AD 用） |
| `CS_ECAT_Slave_PDO_Set_OD_Data(CardNo, NodeID, SlotNo, ODIndex, ODSubIndex, ref byte Data)` | 写 PDO OD 数据（DA 用） |

### 4.2 EtherCATMotionNative.cs — 运动控制 API

#### 模式 / 使能 / 停止

```csharp
// 运动模式：PP=1, PV=3, Homing=6, CSP=8, CSV=9, CST=10
CS_ECAT_Slave_Motion_Get_MoveMode(ushort CardNo, ushort NodeID, ushort SlotNo, ref byte Mode);
CS_ECAT_Slave_Motion_Set_MoveMode(ushort CardNo, ushort NodeID, ushort SlotNo, ushort OpMode);

CS_ECAT_Slave_Motion_Set_Svon(ushort CardNo, ushort NodeID, ushort SlotNo, ushort On_Off); // 0=OFF, 1=ON
CS_ECAT_Slave_Motion_Ralm(ushort CardNo, ushort NodeID, ushort SlotNo);                     // 报警复位
CS_ECAT_Slave_Motion_Set_Position(ushort CardNo, ushort NodeID, ushort SlotNo, int Pos);    // 设指令位置

CS_ECAT_Slave_Motion_Emg_Stop(ushort CardNo, ushort NodeID, ushort SlotNo);                 // 急停
CS_ECAT_Slave_Motion_Sd_Stop(ushort CardNo, ushort NodeID, ushort SlotNo, double Tdec);     // 减速停止
```

#### 状态读取

| API | 返回 | 说明 |
|-----|------|------|
| `CS_ECAT_Slave_Motion_Get_StatusWord(...)` | `ref ushort` | 驱动器状态字（位解析见 §9.3） |
| `CS_ECAT_Slave_Motion_Get_Command(...)` | `ref int` | 指令位置（脉冲） |
| `CS_ECAT_Slave_Motion_Get_Position(...)` | `ref int` | 反馈位置（脉冲） |
| `CS_ECAT_Slave_Motion_Get_Actual_Position(...)` | `ref int` | 实际位置（脉冲） |
| `CS_ECAT_Slave_Motion_Get_Mdone(...)` | `ref ushort` | `0`=运动中，`1`=完成 |
| `CS_ECAT_Slave_Motion_Get_Current_Speed(...)` | `ref int` | 当前速度（脉冲/s） |
| `CS_ECAT_Slave_Motion_Get_Torque(...)` | `ref short` | 当前扭矩 |

#### CSP 周期同步位置运动（核心）

```csharp
// Dist/StrVel/ConstVel/EndVel: 脉冲；Tacc/Tdec: 秒；SCurve: 毫秒；IsAbs: 0=相对, 1=绝对
CS_ECAT_Slave_CSP_Start_Move(ushort CardNo, ushort NodeID, ushort SlotNo,
    int Dist, int StrVel, int ConstVel, int EndVel,
    double Tacc, double Tdec, ushort SCurve, ushort IsAbs);

// Jog：Dir 0=正, 1=负
CS_ECAT_Slave_CSP_Start_V_Move(ushort CardNo, ushort NodeID, ushort SlotNo,
    ushort Dir, int StrVel, int ConstVel, double Tacc, ushort SCurve);

// 运动中变更
CS_ECAT_Slave_CSP_TargetPos_Change(ushort CardNo, ushort NodeID, ushort SlotNo, int NewPos);
CS_ECAT_Slave_CSP_Velocity_Change(ushort CardNo, ushort NodeID, ushort SlotNo, int NewSpeed, double Tsec);
```

#### CSV / CST 模式

```csharp
CS_ECAT_Slave_CSV_Start_Move(CardNo, NodeID, SlotNo, int TargetVelocity, double Acceleration, ushort CurveMode, ushort AccType);
CS_ECAT_Slave_CST_Start_Move(CardNo, NodeID, SlotNo, short TargetTorque, uint Slope, ushort CurveMode);
```

#### 回零 / 软限位 / 电子齿轮

```csharp
// 速度: 脉冲/s；Acceleration: 毫秒
CS_ECAT_Slave_Home_Config(CardNo, NodeID, SlotNo, ushort Mode, int Offset, uint FirstVel, uint SecondVel, uint Acceleration);
CS_ECAT_Slave_Home_Move(CardNo, NodeID, SlotNo);
CS_ECAT_Slave_Home_Status(CardNo, NodeID, SlotNo, ref ushort Status);   // 0=完成, 1=进行中, 其他=错误

CS_ECAT_Slave_CSP_Set_Softlimit(CardNo, NodeID, SlotNo, int PosiLimit, int NegaLimit, ushort Mode);
CS_ECAT_Slave_CSP_Set_Gear(CardNo, NodeID, SlotNo, double Numerator, double Denominator, short Enable);
```

### 4.3 EtherCATIONative.cs — 数字 IO / AD / DA

| API | 说明 |
|-----|------|
| `CS_ECAT_Slave_DIO_Get_Input_Value(CardNo, NodeID, SlotNo, ref ushort Value)` | 读全部输入（16bit 位图） |
| `CS_ECAT_Slave_DIO_Get_Output_Value(CardNo, NodeID, SlotNo, ref ushort Value)` | 读全部输出 |
| `CS_ECAT_Slave_DIO_Set_Output_Value(CardNo, NodeID, SlotNo, ushort Value)` | 设全部输出 |
| `CS_ECAT_Slave_DIO_Get_Single_Input_Value(CardNo, NodeID, SlotNo, ushort BitNum, ref ushort Value)` | 读单路输入（BitNum 0~15） |
| `CS_ECAT_Slave_DIO_Get_Single_Output_Value(CardNo, NodeID, SlotNo, ushort BitNum, ref ushort Value)` | 读单路输出 |
| `CS_ECAT_Slave_DIO_Set_Single_Output_Value(CardNo, NodeID, SlotNo, ushort BitNum, ushort Value)` | 写单路输出 |

AD / DA 复用 PDO OD 接口（见 §4.1），不额外封装。

### 4.4 EtherCATAdvancedNative.cs — 高级功能

| API 组 | 关键方法 | 用途 |
|--------|----------|------|
| 多轴直线插补 | `CS_ECAT_Slave_CSP_Start_Multiaxes_Move` | 多轴同步直线 |
| 圆弧插补 | `CS_ECAT_Slave_CSP_Start_Arc_Move` | 圆心 + 角度 |
| 螺旋插补 | `CS_ECAT_Slave_CSP_Start_Heli_Move` | 螺旋运动 |
| 多轴同步 | `CS_ECAT_Slave_CSP_Sync_Config` + `CS_ECAT_Slave_CSP_Sync_Move` | 同步启动 |
| 电子凸轮 | `CS_ECAT_Slave_ECAM2_*` | 凸轮/追剪跟随（见 §9.7） |
| 龙门同步 | `CS_ECAT_Slave_Gantry_*` | 龙门双驱 |
| 运动缓冲 | `CS_ECAT_Slave_MotionBuffer_*` | 运动队列 |
| 表运动 / PVT | `CS_ECAT_Slave_TableMotion_*` / `CS_ECAT_Slave_PVT_*` | 轨迹规划 |
| Touch Probe | `CS_ECAT_Slave_TouchProbe_*` | 位置锁存 |

> 核心运动（点位/Jog/回零/IO）已由 §4.1~4.3 覆盖，高级功能按需求从官方示例补充到此文件。

### 4.5 DeltaErrorCode.cs — 错误码常量

按功能分组（`#region` 分隔）：

```csharp
namespace DeltaEtherCAT
{
    public static class DeltaErrorCode
    {
        #region 通用
        public const ushort NO_ERROR = 0x0000;
        #endregion

        #region 初始化
        public const ushort INITIAL_TIMEOUT = 0x1001;
        public const ushort INITIAL_SLAVE_FAIL = 0x1002;
        #endregion

        #region 状态检查
        public const ushort NEED_INITIAL = 0x1100;
        public const ushort NEED_RALM = 0x1104;       // 需先复位报警
        public const ushort NEED_SVON = 0x1105;       // 需先伺服使能
        public const ushort NEED_HOMECONFIG = 0x1106; // 需先配置回零
        #endregion

        #region 参数与模式
        public const ushort API_PARAMETER = 0x1201;
        public const ushort MODE_NOT_SUPPORT = 0x1204;
        public const ushort RING_BUFFER_FULL = 0x1200;
        #endregion

        #region SDO
        public const ushort SDO_TIMEOUT = 0x1301;
        #endregion

        #region 运动
        public const ushort MOTION_NOT_FINISHED = 0x0202;
        #endregion

        #region DLL
        public const ushort NO_DLL_FOUND = 0xF001;
        #endregion

        public static string GetMessage(ushort code)
        {
            string msg = new string('\0', 256);
            EtherCATMasterNative.CS_ECAT_Master_Get_Return_Code_Message(code, msg);
            return msg.TrimEnd('\0');
        }
    }
}
```

> 台达 SDK 共 336 个错误码，完整清单见 `raw/delta/EtherCAT_DLL_Err.cs` 与 [[api/DeltaEtherCAT-Native]]。

---

## 5. L3 台达实现层（DeltaEtherCAT/）

### 5.1 DeltaSlaveScanner.cs — 从站扫描器

#### 公共枚举 `SlaveDeviceType`

```csharp
public enum SlaveDeviceType
{
    Unknown,
    Servo_A2E,        // 台达 A2E 伺服
    Servo_EcAxis,     // 台达 EcAxis 单轴
    Servo_Ec4Axis,    // 台达 Ec4Axis 四轴
    DI_16Channel,     // 16 路数字输入
    DO_16Channel,     // 16 路数字输出
    AD_Module,        // AD 模拟量输入
    DA_Module,        // DA 模拟量输出
    Yaskawa_Servo     // 安川伺服
}
```

#### 公共嵌套类 `SlaveInfo`

```csharp
public class SlaveInfo
{
    public ushort SeqId { get; set; }
    public ushort NodeId { get; set; }
    public uint VendorId { get; set; }
    public uint ProductCode { get; set; }
    public uint RevisionNo { get; set; }
    public string DeviceName { get; set; }
    public SlaveDeviceType DeviceType { get; set; }
    public ushort AxisCount { get; set; }
}
```

#### 成员

| 成员 | 签名 | 说明 |
|------|------|------|
| `SlaveInfos` | `public List<SlaveInfo>` | 扫描结果 |
| 构造 | `public DeltaSlaveScanner()` | 初始化列表 |
| `Scan` | `public bool Scan(ushort cardNo)` | 扫描总线上所有从站并识别类型 |
| `GetByType` | `public List<SlaveInfo> GetByType(SlaveDeviceType)` | 按类型筛选 |
| `FindByNodeId` | `public SlaveInfo FindByNodeId(ushort)` | 按从站号查找 |
| `IdentifyDevice` | `private void IdentifyDevice(SlaveInfo)` | 按 VendorID + ProductCode 匹配 |

#### Scan 核心实现

```csharp
public bool Scan(ushort cardNo)
{
    SlaveInfos.Clear();
    ushort slaveNum = 0;
    if (EtherCATMasterNative.CS_ECAT_Master_Get_SlaveNum(cardNo, ref slaveNum) != DeltaErrorCode.NO_ERROR)
        return false;

    for (ushort seq = 0; seq < slaveNum; seq++)
    {
        ushort nodeId = 0;
        uint vendorId = 0, productCode = 0, revisionNo = 0, dcTime = 0;
        if (EtherCATMasterNative.CS_ECAT_Master_Get_Slave_Info(
            cardNo, seq, ref nodeId, ref vendorId, ref productCode, ref revisionNo, ref dcTime) != DeltaErrorCode.NO_ERROR)
            continue;

        var info = new SlaveInfo { SeqId = seq, NodeId = nodeId, VendorId = vendorId, ProductCode = productCode, RevisionNo = revisionNo };
        IdentifyDevice(info);
        SlaveInfos.Add(info);
    }
    return true;
}
```

#### 设备识别匹配表

| VendorID | ProductCode | 设备类型 | AxisCount |
|----------|-------------|----------|-----------|
| `0x01DD` | `0x10305070` | `Servo_A2E` | 1 |
| `0x01A05` / `0x01DD` | `0x00624` | `Servo_Ec4Axis` | 4 |
| `0x01A05` / `0x01DD` | `0x05621` | `Servo_EcAxis` | 1 |
| `0x01A05` / `0x01DD` | `0x06002` / `0x6022` / `0x6032` / `0x6142` | `DI_16Channel` | — |
| `0x01A05` / `0x01DD` | `0x07062` / `0x70A2` / `0x71A2` | `DO_16Channel` | — |
| `0x00539` | `0x2200001` | `Yaskawa_Servo` | 1 |

### 5.2 DeltaMontionControl.cs — 台达控制器实现

继承 `MontionControl`。

#### 成员

| 分类 | 成员 | 类型 | 说明 |
|------|------|------|------|
| 私有字段 | `_existCardCount` | `ushort` | 检测到的卡数量 |
| | `_cardNoList` | `ushort[]` | 卡号列表（长度 32，`99`=初始化失败） |
| | `_slaveScanner` | `DeltaSlaveScanner` | 从站扫描器 |
| | `_isEmergencyStop` | `bool` | 全局急停状态 |
| 公共静态字段 | `m_Log` | `Log4` | 日志对象 |
| 公共属性 | `CardNo` | `ushort` `get;` | 当前卡号（= ConnectNo） |
| | `SlaveScanner` | `DeltaSlaveScanner` `get;` | 从站扫描器 |
| | `EmergencyStop` | `bool` `get; set;` | 全局急停 |
| 构造 | `DeltaMontionControl(string DevName)` | — | 初始化卡号列表与扫描器 |
| override | `Initialization(ref string strMsg)` | `bool` | Open → Initial → 轮询 → 扫描 |
| | `Close()` | `void` | 全轴 ServoOff → Reset 每卡 → Master_Close |
| | `AddAxis` / `AddIO` | `void` | 去重后加入集合 |
| | `GetAxes` / `GetInPutIOs` / `GetOutPutIOs` | `List<>` | 返回集合 |
| | `GetControlType` | `ControlType` | 返回 `ControlType.EtherCATMaster` |
| | `GetManufacturerType` | `ManufacturerType` | 返回 `ManufacturerType.Delta` |
| 台达特有 | `CheckBusOK()` | `bool` | 所有从站 OpState==3 且无报警 |
| | `SetEmergencyStop(bool)` | `void` | 全局急停（所有轴 `AxisStop(1)`） |

#### Initialization 核心流程

```csharp
public override bool Initialization(ref string strMsg)
{
    // 1. 打开主站，检测卡
    ushort ret = EtherCATMasterNative.CS_ECAT_Master_Open(ref _existCardCount);
    if (ret != DeltaErrorCode.NO_ERROR || _existCardCount == 0) { /* 日志 + 返回 false */ }

    // 2. 遍历初始化每张卡
    for (ushort seq = 0; seq < _existCardCount; seq++)
    {
        ushort cardNo = 0;
        EtherCATMasterNative.CS_ECAT_Master_Get_CardSeq(seq, ref cardNo);
        ret = EtherCATMasterNative.CS_ECAT_Master_Initial(cardNo);
        _cardNoList[seq] = (ret == DeltaErrorCode.NO_ERROR) ? cardNo : (ushort)99;
    }
    _ConnectNo = _cardNoList[0];   // ConnectNo 映射为 CardNo

    // 3. 轮询等待初始化完成（InitDone == 0），超时 30s
    DateTime startTime = DateTime.Now;
    ushort initDone = 1;
    while (initDone != 0)
    {
        System.Threading.Thread.Sleep(100);
        EtherCATMasterNative.CS_ECAT_Master_Check_Initial_Done(_ConnectNo, ref initDone);
        if (initDone == 99) { /* 读 Get_Initial_ErrorCode，返回 false */ }
        if ((DateTime.Now - startTime).TotalSeconds > 30) { /* 超时返回 false */ }
    }

    // 4. 扫描从站
    _slaveScanner.Scan(_ConnectNo);
    _isInitial = true;
    return true;
}
```

### 5.3 DeltaMontionAxis.cs — 台达轴实现

继承 `MontionAxis`，对应雷赛 `LSnmcMontionAxis`。

#### 成员

| 分类 | 成员 | 说明 |
|------|------|------|
| 私有字段 | `_deltaControl` | 台达控制器强类型引用 |
| | `_nodeId` / `_slotNo` | 从站号 / 槽号（多轴从站用，单轴=0） |
| 公共属性 | `NodeId` / `SlotNo` | 从站号 / 槽号 |
| 构造 | `DeltaMontionAxis(MontionControl mControl, string _AName, ushort nodeId, ushort slotNo = 0)` | base 构造自动 `Container.AddAxis(this)` |

#### 私有辅助方法

```csharp
// 运动前统一检查（急停 / 总线状态 / 报警）
private bool PreMotionCheck(string funcName)
{
    if (_deltaControl.EmergencyStop) return false;
    ushort opState = 0, alarmStatus = 0;
    EtherCATMasterNative.CS_ECAT_Slave_Get_Connect_Status(
        _ConnectNo, _nodeId, _slotNo, ref opState, ref alarmStatus);
    if (opState != 3 || alarmStatus != 0) return false;
    return true;
}

// 工程单位 ↔ 脉冲（台达原生 API 全是脉冲单位）
private int ToPulse(double value) => (int)(value / Equiv);
private double ToUnit(int pulse) => pulse * Equiv;
```

#### 公共方法实现

| 分组 | 方法 | 核心台达 API |
|------|------|-------------|
| 运动状态 | `IsMoving()` | `Motion_Get_Mdone`（`Mdone == 0` 即运动中） |
| | `WaitMoveDone()` | 轮询 `IsMoving()`，超时 60s |
| | `AxisStop(ushort)` | `0`→`Motion_Sd_Stop`，`1`→`Motion_Emg_Stop` |
| 伺服控制 | `IsServoOn()` | `Motion_Get_StatusWord`，bit2(`0x0004`)=Operation enabled |
| | `ServoOn()` | 查报警→`Set_Move_Mode(8)`→`Set_Svon(1)`→轮询 bit2，超时 3s |
| | `ServoOff()` | `Motion_Set_Svon(0)` |
| | `ResetAlarm()` | `Motion_Ralm` + `Sleep(50)` |
| 回零 | `Home()` | `Home_Config`（速度→脉冲/s，加速→ms）→`Home_Move`→`WaitHomeDone` |
| | `HomeNoBlock()` | Config + Move，不等待 |
| | `WaitHomeDone()` | 轮询 `Home_Status`，超时 120s |
| 点位运动 | `AbsMove(...)` 多重载 | `CSP_Start_Move`（位置/速度→脉冲）→`WaitMoveDone` |
| | `AbsMoveNoBlock(...)` | `CSP_Start_Move`，不等待 |
| 点动 | `JogMove(...)` 多重载 | `CSP_Start_V_Move`（Dir 0=正 / 1=负） |
| 位置读写 | `GetPosition()` | `Motion_Get_Position` → 工程单位 |
| | `GetCommandPosition()` | `Motion_Get_Command` → 工程单位 |
| | `SetHomePosition()` | `Motion_Set_Position(0)` |
| | `SetPosition(double)` | `Motion_Set_Position(ToPulse(pos))` |
| 状态读取 | `GetCurrentSpeed()` | `Motion_Get_Current_Speed` → 工程单位/s |
| | `GetCurrentTorque()` | `Motion_Get_Torque` |
| | `GetStatusWord()` | `Motion_Get_StatusWord` |
| 台达特有 | `SetSoftLimit(double, double, bool)` | 软限位（工程单位→脉冲） |
| | `ChangeTargetPosition(double)` | `CSP_TargetPos_Change` |
| | `ChangeSpeed(double, double)` | `CSP_Velocity_Change` |

#### ServoOn 核心实现

```csharp
public override void ServoOn()
{
    if (!PreMotionCheck("ServoOn")) return;

    // 1. 检查报警（StatusWord bit3 = 0x0008），有报警先复位
    ushort statusWord = 0;
    EtherCATMotionNative.CS_ECAT_Slave_Motion_Get_StatusWord(_ConnectNo, _nodeId, _slotNo, ref statusWord);
    if ((statusWord & 0x0008) != 0)
    {
        EtherCATMotionNative.CS_ECAT_Slave_Motion_Ralm(_ConnectNo, _nodeId, _slotNo);
        System.Threading.Thread.Sleep(50);
    }

    // 2. 设置 CSP 模式 → 3. 伺服使能
    EtherCATMotionNative.CS_ECAT_Slave_Motion_Set_MoveMode(_ConnectNo, _nodeId, _slotNo, 8); // 8=CSP
    EtherCATMotionNative.CS_ECAT_Slave_Motion_Set_Svon(_ConnectNo, _nodeId, _slotNo, 1);

    // 4. 轮询等待 OperationEnabled（bit2），超时 3s
    DateTime start = DateTime.Now;
    while (!IsServoOn())
    {
        System.Threading.Thread.Sleep(20);
        if ((DateTime.Now - start).TotalSeconds > 3) { m_Log.Debug("ServoOn 超时"); return; }
    }
}
```

#### AbsMove 核心实现

```csharp
public override bool AbsMove(double pos, double minVel, double maxVel,
    double stopVel, double accTime, double decTime, double sTime, ushort posMode = 1)
{
    if (!PreMotionCheck("AbsMove") || !IsServoOn()) return false;

    ushort ret = EtherCATMotionNative.CS_ECAT_Slave_CSP_Start_Move(
        _ConnectNo, _nodeId, _slotNo,
        ToPulse(pos),             // 目标位置（脉冲）
        ToPulse(minVel),          // 起始速度（脉冲/s）
        ToPulse(maxVel),          // 运行速度（脉冲/s）
        ToPulse(stopVel),         // 末速度（脉冲/s）
        accTime, decTime,         // 加减速时间（s）
        (ushort)(sTime * 1000),   // S 曲线时间（ms）
        posMode);                 // 0=相对, 1=绝对

    if (ret != DeltaErrorCode.NO_ERROR) { m_Log.Debug(DeltaErrorCode.GetMessage(ret)); return false; }
    return WaitMoveDone();
}
```

### 5.4 DeltaInputIO.cs / DeltaOutputIO.cs — 数字 IO 实现

继承 `InputIO` / `OutputIO`，构造签名 `(MontionControl, string, ushort nodeId, ushort slotNo = 0)`，base 构造自动 `Container.AddIO(this)`。

**总线检查 + NPN 低电平有效**是这两个类的固定写法：

```csharp
public override bool IsON() => GetIOStatus() == 0;   // 0 = 有效

public override int GetIOStatus()
{
    ushort opState = 0, alarmStatus = 0;
    EtherCATMasterNative.CS_ECAT_Slave_Get_Connect_Status(
        _ConnectNo, _nodeId, _slotNo, ref opState, ref alarmStatus);
    if (opState != 3 || alarmStatus != 0 || !_IOEnable) return 1;

    ushort value = 0;
    try { EtherCATIONative.CS_ECAT_Slave_DIO_Get_Single_Input_Value(_ConnectNo, _nodeId, _slotNo, _IONo, ref value); }
    catch { }
    return value;
}

public override int SetON()  => EtherCATIONative.CS_ECAT_Slave_DIO_Set_Single_Output_Value(_ConnectNo, _nodeId, _slotNo, _IONo, 0);
public override int SetOFF() => EtherCATIONative.CS_ECAT_Slave_DIO_Set_Single_Output_Value(_ConnectNo, _nodeId, _slotNo, _IONo, 1);
```

> `SetON` 写 `0`、`SetOFF` 写 `1`——NPN 低电平有效，与雷赛版本语义一致，不可按直觉反转。

---

## 6. L2 抽象接口层（IMotion/）

本层是**对外契约的定义处**，共 8 个文件，不依赖任何厂商。

| 文件 | 内容 |
|------|------|
| `Type.cs` | `ControlType`、`ManufacturerType`、`IOType`、`MoveMode`、`HomingMode`、`StopMode`、`AxisState`、`InterpolationType`、`PVTTimeMode`、`EcamCurveType`、`EcamStartMode`、`EcamBufferMode` |
| `MontionControl.cs` | 控制器抽象基类 |
| `MontionAxis.cs` | 轴抽象基类（默认实现 `IPVTMotion`，四入口 `virtual` 返回 `PVTResult.NotSupported`） |
| `MontionIO.cs` | IO 抽象基类 |
| `InputIO.cs` / `OutputIO.cs` | 数字输入 / 输出抽象基类 |
| `Cylinder.cs` | 气缸实体（2 输入 + 2 输出 + 可选中间位，`Builder` 链式装配，`GetAllIO()` 枚举占用点位） |
| `IPVTMotion.cs` | `IPVTMotion` 契约 + `PVTPoint` + `PVTInformation` + `PVTResult`（全大写 PVT） |
| `InterpolationMontionParam.cs` | 插补运动参数类 |

> **2026-09-07**：原 `IOParam.cs`（IO 起始编号与数量）因业务层与 L3 均未引用而删除，L2 仍为 8 个文件。

### 6.1 MontionControl（控制器抽象基类）

| 成员 | 类型 | 说明 |
|------|------|------|
| `_ConnectNo` | `protected ushort` | 连接号（台达映射为 CardNo） |
| `_isInitial` | `protected bool` | 初始化状态 |
| `_axes` / `_inPuts` / `_outPuts` | `protected List<>` | 轴 / 输入 / 输出集合 |
| `ConnectNo` / `DeviceName` / `Initial` | `public` 属性 | 连接号 / 设备名 / 初始化状态 |
| `MontionControl(string DevName)` | `protected` 构造 | — |
| `Initialization(ref string strMsg)` | `public abstract bool` | 初始化 |
| `Close()` | `public abstract void` | 关闭 |
| `AddAxis(MontionAxis)` / `AddIO(MontionIO)` | `public abstract void` | 注册轴 / IO |
| `GetAxes()` / `GetInPutIOs()` / `GetOutPutIOs()` | `public abstract List<>` | 获取集合 |
| `GetControlType()` / `GetManufacturerType()` | `public abstract` | 类型标识 |

### 6.2 MontionAxis（轴抽象基类）

| 成员 | 类型 | 说明 |
|------|------|------|
| `_ConnectNo` / `_AxisNo` / `_AName` | `protected` | 连接号 / 轴号 / 轴名 |
| `Container` | `public MontionControl` | 所属控制器 |
| `MinVel` / `MaxVel` / `AccTime` / `DecTime` / `STime` / `StopVel` | `public double` | 运动参数（工程单位） |
| `Equiv` | `public double` | 脉冲当量（**工程单位/脉冲**，见 §9.1） |
| `HomeMode` / `HomeDir` / `HomeMaxVel` | `public` | 回零参数 |
| `MontionAxis(MontionControl, string)` | `protected` 构造 | 自动 `Container.AddAxis(this)` |
| `IsMoving()` / `WaitMoveDone()` / `AxisStop(ushort)` | `public abstract` | 运动状态 / 停止 |
| `IsServoOn()` / `ServoOn()` / `ServoOff()` / `ResetAlarm()` | `public abstract` | 伺服控制 |
| `Home()` / `HomeNoBlock()` / `WaitHomeDone()` | `public abstract bool` | 回零 |
| `AbsMove(...)` 多重载 / `AbsMoveNoBlock` | `public abstract bool` | 点位运动 |
| `JogMove(...)` 多重载 | `public abstract void` | 点动 |
| `GetPosition()` / `GetCommandPosition()` / `SetPosition(double)` | `public abstract` | 位置读写（工程单位） |
| `GetCurrentSpeed()` / `GetCurrentTorque()` / `GetStatusWord()` | `public abstract` | 状态读取 |

### 6.3 InputIO / OutputIO（IO 抽象基类）

| 成员 | 类型 | 说明 |
|------|------|------|
| `_ConnectNo` / `_IONo` / `_IOName` / `_IOEnable` | `protected` | 连接号 / IO 号 / 名称 / 使能 |
| `Container` | `public MontionControl` | 所属控制器 |
| `InputIO(MontionControl, string)` / `OutputIO(...)` | `public` 构造 | 自动 `Container.AddIO(this)` |
| `IsON()` / `GetIOStatus()` | `public abstract` | 状态读取 |
| `SetON()` / `SetOFF()` | `public abstract int` | 输出控制（仅 `OutputIO`） |

---

## 7. 业务层

### 7.1 MontionManager.cs — 运动管理器

- 单例（`MontionManager.Instance`）。
- 持有 `MontionControl` 抽象引用；初始化时 `new DeltaMontionControl(DevName)` 是**唯一**出现厂商具体类型的地方。
- 轴、IO、气缸由三张注册表聚合，按名称索引：`AddAxis(string, MontionAxis)` / `AddCylinder(string, Cylinder)`（对外 API 与旧版字典实现**完全一致**）。
- 注册表属性：`Axes` / `IOs` / `Cylinders`；`AttachAll()` 把全部对象回灌注册进控制器（`Initialization` 成功后自动调用）。
- 提供批量 `ServoOn` / `Home` / 急停等编排能力。
- `Initialization(string devName, ref string msg)` / `Close()` 为生命周期入口。

### 7.1.1 三张注册表（2026-09-07）

| 注册表 | 承载 | 说明 |
|--------|------|------|
| `AxisRegistry` | `Dictionary<string, MontionAxis>` | `Register` / `Get` / `GetAll` / `GetNames` / `Count` / `AttachAll(control)` |
| `IORegistry` | 输入、输出分表 | `RegisterInput` / `GetInput` / `RegisterOutput` / `GetOutput` / `InputCount` / `OutputCount` / `AttachAll` |
| `CylinderRegistry` | `Dictionary<string, Cylinder>` | `AttachAll` 逐个 `cylinder.GetAllIO()` 登记进控制器 |

要点：轴与 IO 在**构造时已向控制器自注册**（`container.AddAxis(this)` / `AddIO(this)`），`AttachAll` 是幂等回灌；气缸为多 IO 复合体，其点位必须靠 `GetAllIO()` 枚举后逐个登记。

### 7.2 Cylinder.cs — 气缸业务类（位于 `IMotion/`）

依赖 `InputIO` / `OutputIO` 抽象基类，**与厂商无关**。采用 Builder 模式装配：

```csharp
var clampCylinder = Cylinder.Builder("夹紧缸")
    .SetInStretchSensor(inStretch)      // 伸出位传感器
    .SetInRetractSensor(inRetract)      // 缩回位传感器
    .SetOutCylinderStretch(outStretch, "夹紧")
    .SetOutCylinderRetract(outRetract, "松开");
```

---

## 8. 生命周期与初始化流程

### 8.1 上电初始化序列

```
1. Master_Open                → 得到 existCardCount
2. for 每张卡: Get_CardSeq    → 取 cardNo
              Master_Initial → 启动初始化
3. 轮询 Check_Initial_Done    → 0=完成 / 1=进行中 / 99=失败
   ├─ 99 → 读 Get_Initial_ErrorCode，记录并退出
   └─ 超过 30s → 超时退出
4. SlaveScanner.Scan(CardNo)  → 枚举从站并识别类型
5. 置位 _isInitial = true
```

**顺序不可颠倒**：从站扫描必须在 `Check_Initial_Done` 返回完成后进行，否则 `Get_SlaveNum` 读到 0。

### 8.2 下电关闭序列

```
1. 遍历所有轴 → ServoOff()
2. foreach 卡 → Master_Reset(cardNo)
3. Master_Close()
```

### 8.3 从站状态机

`Slave_Get_Connect_Status` 的 `OpState`：

| 值 | 状态 | 含义 |
|----|------|------|
| 0 | Init | 初始化 |
| 1 | PreOP | 预运行 |
| 2 | SafeOP | 安全运行 |
| 3 | OP | **运行态，只有此态可运动** |

所有运动/IO 调用的前置检查都要求 `OpState == 3 && AlarmStatus == 0`。

---

## 9. 关键机制

### 9.1 单位换算

> **原档订正**：原档 §6.2 将 `Equiv` 注为"脉冲/工程单位"，与其 §7.3 的 `ToPulse(v) = v / Equiv` 矛盾。
> **正确语义：`Equiv` = 工程单位/脉冲（mm/pulse）**，与雷赛 `smc_set_equiv` 一致。

| 方向 | 公式 | 用途 |
|------|------|------|
| 工程单位 → 脉冲 | `pulse = value / Equiv` | 下发位置、速度 |
| 脉冲 → 工程单位 | `value = pulse * Equiv` | 上报位置、速度 |

换算只发生在 L3（`DeltaMontionAxis`）。**L2 抽象层与业务层一律使用工程单位**。示例：`Equiv = 0.0001`（10000 脉冲/mm）时，`AbsMove(100.0)` → `ToPulse` = 100 / 0.0001 = 1,000,000 脉冲。

| 量 | 抽象层单位 | 台达 API 单位 | 换算点 |
|----|-----------|--------------|--------|
| 位置 | mm | 脉冲 | `ToPulse` / `ToUnit` |
| 速度 | mm/s | 脉冲/s | `ToPulse` / `ToUnit` |
| 加减速时间 | s | s | 不换算 |
| S 曲线时间 | s | **ms** | `× 1000` |
| 回零速度 | mm/s | 脉冲/s | `ToPulse` |
| 回零加速度 | s | **ms** | `× 1000` |
| 扭矩 | 额定千分比 | 额定千分比 | 不换算 |

### 9.2 运动前统一检查（PreMotionCheck）

雷赛在每个运动入口都重复"总线错误码 → 轴状态机 → 运动中"三段检查，这是最值得照搬的纪律。台达的对应实现：

```csharp
private bool PreMotionCheck(string funcName)
{
    if (_deltaControl.EmergencyStop) return false;                 // ① 急停
    ushort opState = 0, alarmStatus = 0;
    EtherCATMasterNative.CS_ECAT_Slave_Get_Connect_Status(          // ② 总线 + 报警
        _ConnectNo, _nodeId, _slotNo, ref opState, ref alarmStatus);
    if (opState != 3 || alarmStatus != 0) return false;
    return true;
}
```

**所有运动入口（`ServoOn` / `AbsMove` / `JogMove` / `Home`）第一行必须调用它。**

### 9.3 状态字（StatusWord）位定义

| 位 | 掩码 | 含义 | 用途 |
|----|------|------|------|
| bit2 | `0x0004` | Operation enabled | `IsServoOn()` 判定 |
| bit3 | `0x0008` | Fault | 报警检测，置位需先 `Motion_Ralm` |

伺服使能完整链路：`PreMotionCheck` → 查 bit3 报警并复位 → `Set_Move_Mode(8=CSP)` → `Set_Svon(1)` → 轮询 bit2（超时 3s）。

### 9.4 回零

```
Home_Config(Mode, Offset, FirstVel, SecondVel, Acceleration)  →  Home_Move()  →  轮询 Home_Status
```

- 速度走脉冲/s，加速度走 ms。
- `Home_Status`：`0`=完成，`1`=进行中，其他=错误。
- 阻塞版 `Home()` 超时 120s；非阻塞版 `HomeNoBlock()` 需自行调用 `WaitHomeDone()`。

### 9.5 IO 极性与寻址

| 项 | 值 |
|----|-----|
| 寻址 | `CardNo + NodeId + SlotNo + BitNo(0~15)` |
| 有效电平 | **NPN 低电平有效**：`IsON()` ⇔ `GetIOStatus() == 0` |
| 输出 | `SetON()` 写 `0`，`SetOFF()` 写 `1` |
| 前置检查 | 读/写前均需 `OpState == 3 && AlarmStatus == 0`；输入额外查 `_IOEnable` |

### 9.6 急停

| 层级 | 手段 |
|------|------|
| 单轴减速停 | `AxisStop(0)` → `Motion_Sd_Stop(cardNo, nodeId, slotNo, Tdec)` |
| 单轴急停 | `AxisStop(1)` → `Motion_Emg_Stop(cardNo, nodeId, slotNo)` |
| 全局急停 | `DeltaMontionControl.SetEmergencyStop(true)` → 置 `_isEmergencyStop`，所有轴 `AxisStop(1)`；此后所有 `PreMotionCheck` 直接返回 false |

### 9.7 电子凸轮 / 追剪（ECAM2）

台达提供 `CS_ECAT_Slave_ECAM2_*` 系列（24 个 API），配合 `CSP_Virtual_Set_Command` 虚拟主轴与 `GearIn` 电子齿轮，可承接焊缝跟踪类的跟随运动。完整 API 分组见 [[api/DeltaEtherCAT-Native]]。

> 焊缝跟踪的具体主轴来源与凸轮曲线配置属于应用层设计，待工艺参数确定后补充，见 §15。

---

## 10. 典型使用示例

### 10.1 最小可运行

```csharp
using IMotion;
using DeltaEtherCAT;
using MasonMotionControl;

class Program
{
    static void Main(string[] args)
    {
        var mgr = MontionManager.Instance;
        string msg = "";

        // 1. 初始化
        if (!mgr.Initialization("测试设备", ref msg)) { Console.WriteLine(msg); return; }

        // 2. 创建轴（nodeId=1 假设是台达伺服从站）
        var xAxis = new DeltaMontionAxis(mgr.MontionControl, "X轴", nodeId: 1, slotNo: 0)
        {
            MaxVel = 50.0, MinVel = 0, AccTime = 0.2, DecTime = 0.2, STime = 0.05,
            StopVel = 0, Equiv = 0.0001, HomeMode = 2, HomeDir = 1, HomeMaxVel = 20.0
        };
        mgr.AddAxis("X", xAxis);

        // 3. 创建 IO
        var startBtn = new DeltaInputIO(mgr.MontionControl, "启动按钮", nodeId: 2, slotNo: 0) { IONo = 0 };
        var runLamp  = new DeltaOutputIO(mgr.MontionControl, "运行灯", nodeId: 3, slotNo: 0) { IONo = 0 };

        // 4. 使能 + 回零 + 点位运动
        xAxis.ServoOn();
        xAxis.Home();
        xAxis.AbsMove(100.0);
        Console.WriteLine("当前位置: " + xAxis.GetPosition().ToString("F3") + " mm");

        // 5. 点动 + IO
        xAxis.JogMove(0);
        System.Threading.Thread.Sleep(500);
        xAxis.AxisStop(0);
        runLamp.SetON();

        // 6. 关闭
        mgr.Close();
    }
}
```

### 10.2 气缸配置

```csharp
var ctrl = mgr.MontionControl;
var inStretch  = new DeltaInputIO(ctrl, "夹紧缸伸出位", nodeId: 2, slotNo: 0) { IONo = 5 };
var inRetract  = new DeltaInputIO(ctrl, "夹紧缸缩回位", nodeId: 2, slotNo: 0) { IONo = 6 };
var outStretch = new DeltaOutputIO(ctrl, "夹紧缸伸出", nodeId: 3, slotNo: 0) { IONo = 2 };
var outRetract = new DeltaOutputIO(ctrl, "夹紧缸缩回", nodeId: 3, slotNo: 0) { IONo = 3 };

var clampCylinder = Cylinder.Builder("夹紧缸")
    .SetInStretchSensor(inStretch)
    .SetInRetractSensor(inRetract)
    .SetOutCylinderStretch(outStretch, "夹紧")
    .SetOutCylinderRetract(outRetract, "松开");

mgr.AddCylinder("Clamp", clampCylinder);
clampCylinder.Stretch();
```

### 10.3 从站扫描与自动建轴

```csharp
var ctrl = (DeltaMontionControl)mgr.MontionControl;
foreach (var slave in ctrl.SlaveScanner.SlaveInfos)
    Console.WriteLine("NodeId=" + slave.NodeId + ", 设备=" + slave.DeviceName + ", 轴数=" + slave.AxisCount);

// 自动创建四轴从站的所有轴
var servos = ctrl.SlaveScanner.GetByType(DeltaSlaveScanner.SlaveDeviceType.Servo_Ec4Axis);
foreach (var servo in servos)
    for (ushort slot = 0; slot < servo.AxisCount; slot++)
    {
        var axis = new DeltaMontionAxis(ctrl, "轴" + servo.NodeId + "-" + slot, servo.NodeId, slot);
        mgr.AddAxis("Axis_" + servo.NodeId + "_" + slot, axis);
    }
```

---

## 11. 抽象层 ↔ 台达 API 映射速查

| 抽象层方法 | 台达原生 API | 单位转换 |
|-----------|-------------|----------|
| `MontionControl.Initialization` | `Master_Open` + `Master_Initial` + `Master_Check_Initial_Done` | — |
| `MontionControl.Close` | `Master_Reset` + `Master_Close` | — |
| `MontionAxis.ServoOn` | `Motion_Set_Move_Mode(8)` + `Motion_Set_Svon(1)` | — |
| `MontionAxis.ServoOff` | `Motion_Set_Svon(0)` | — |
| `MontionAxis.ResetAlarm` | `Motion_Ralm` | — |
| `MontionAxis.Home` | `Home_Config` + `Home_Move` | 速度→脉冲/s，时间→ms |
| `MontionAxis.AbsMove` | `CSP_Start_Move` | 位置/速度→脉冲 |
| `MontionAxis.JogMove` | `CSP_Start_V_Move` | 速度→脉冲/s |
| `MontionAxis.AxisStop(0/1)` | `Motion_Sd_Stop` / `Motion_Emg_Stop` | — |
| `MontionAxis.GetPosition` | `Motion_Get_Position` | 脉冲→工程单位 |
| `MontionAxis.IsMoving` | `Motion_Get_Mdone` | — |
| `MontionAxis.GetCurrentSpeed` | `Motion_Get_Current_Speed` | 脉冲/s→工程单位/s |
| `MontionAxis.GetCurrentTorque` | `Motion_Get_Torque` | — |
| `InputIO.GetIOStatus` | `DIO_Get_Single_Input_Value` | — |
| `OutputIO.SetON/SetOFF` | `DIO_Set_Single_Output_Value` | — |
| （插补） | `CSP_Start_Multiaxes_Move` / `CSP_Start_Arc_Move` | 位置→脉冲 |

---

## 12. API 名核验门禁

**写实现前/后必须跑一遍**：把文档与代码里出现的台达 API 名，与 SDK 头文件 `inc/C#/EtherCAT_DLL.cs`（832 个声明）逐一比对。照抄原档而不核验会直接编译不过。

### 12.1 原档 7 处 API 名订正表

| 原档写法 | SDK 真实名 | 影响 |
|----------|-----------|------|
| `CS_ECAT_Master_Get_Card_Seq` | `CS_ECAT_Master_Get_CardSeq` | 主站遍历取卡号 |
| `CS_ECAT_Master_Get_Slave_Num` | `CS_ECAT_Master_Get_SlaveNum` | 从站扫描 |
| `CS_ECAT_Master_Get_Initial_Error_Code` | `CS_ECAT_Master_Get_Initial_ErrorCode` | 初始化失败诊断 |
| `CS_ECAT_Slave_Motion_Get_Move_Mode` | `CS_ECAT_Slave_Motion_Get_MoveMode` | 模式读取 |
| `CS_ECAT_Slave_Motion_Set_Move_Mode` | `CS_ECAT_Slave_Motion_Set_MoveMode` | 模式设置 |
| `CS_ECAT_Slave_CSP_Start_VMove` | `CS_ECAT_Slave_CSP_Start_V_Move` | Jog 点动 |
| `CS_ECAT_Slave_CSP_Target_Pos_Change` | `CS_ECAT_Slave_CSP_TargetPos_Change` | 运动中改目标位 |

> 错误码常量基本准确，仅 `0x1002` 的描述标注有偏差（SDK 中该码语义不是"从站初始化失败"），落地时以 `raw/delta/EtherCAT_DLL_Err.cs` 为准复核。

### 12.2 核验配方

```python
import re, io

sdk = io.open(r"D:\Program Files (x86)\Delta Industrial Automation\EtherCAT\inc\C#\EtherCAT_DLL.cs",
              encoding="utf-8", errors="ignore").read()
sdk_names = set(re.findall(r"public static extern [\w\[\]\* ]+ (CS_ECAT_\w+)", sdk))

doc = io.open(r"<本页或实现文件>", encoding="utf-8").read()
claimed = set(re.findall(r"CS_ECAT_\w+", doc))

print("文档声称但 SDK 不存在：", sorted(claimed - sdk_names))
# 期望为空。本页 §12.1 订正表左列的 7 个名字是故意保留的反例，
# 核验本页时这 7 个会命中——属预期，不要"修正"它们。
```

---

## 13. 注意事项与最佳实践

1. **平台目标必须 x86 或 x64**，不能用 AnyCPU，否则 `DllImport` 因位数不匹配抛 `BadImageFormatException`。
2. **初始化是异步的**，必须轮询 `Check_Initial_Done`；`99` 表示失败，需读 `Get_Initial_ErrorCode`。
3. **从站扫描必须在初始化完成后**进行，否则读到 0 个从站。
4. **每次运动前做总线检查**（`OpState == 3 && AlarmStatus == 0`），不要只查一次。
5. **伺服使能必须先设 CSP 模式**（`Set_Move_Mode(8)`）再 `Set_Svon(1)`，并轮询状态字 bit2。
6. **IO 是低电平有效**：`SetON()` 写 `0`。这是最容易搞反的地方。
7. **单位换算集中在 L3**：抽象层与业务层只认工程单位；S 曲线时间与回零加速度是**毫秒**，其余时间是秒。
8. **阻塞与非阻塞成对提供**：`AbsMove` / `AbsMoveNoBlock`、`Home` / `HomeNoBlock`，由调用方选择。
9. **到位判定用 `Mdone`，停止原因另查**：不要把"停止"直接当成"到位成功"。
10. **急停贯穿全局**：置位后所有运动入口短路返回，恢复需显式调用 `SetEmergencyStop(false)`。
11. **新增 `.cs` 必须登记 `.csproj`**，见 [[guides/Namespace-Compilation]] §1.1。
12. **日志**：函数入口参数与关键返回值记 Debug，失败记错误码 + `DeltaErrorCode.GetMessage(ret)` 文本。

---

## 14. 落地清单

| # | 项 | 交付物 | 状态 |
|---|-----|--------|------|
| 1 | 建目录骨架 | `IMotion/` 8 文件 + `DeltaEtherCAT/` 5 文件 + `Native/` 5 文件 | ☐ |
| 2 | L1 主站封装 | `EtherCATMasterNative.cs` | ☐ |
| 3 | L1 运动封装 | `EtherCATMotionNative.cs` | ☐ |
| 4 | L1 IO 封装 | `EtherCATIONative.cs` | ☐ |
| 5 | L1 高级封装 | `EtherCATAdvancedNative.cs`（按需） | ☐ |
| 6 | 错误码 | `DeltaErrorCode.cs` | ☐ |
| 7 | 从站扫描器 | `DeltaSlaveScanner.cs` + 设备识别表 | ☐ |
| 8 | 控制器实现 | `DeltaMontionControl.cs` | ☐ |
| 9 | 轴实现 | `DeltaMontionAxis.cs`（含 `ToPulse`/`ToUnit`/`PreMotionCheck`） | ☐ |
| 10 | IO 实现 | `DeltaInputIO.cs` / `DeltaOutputIO.cs` | ☐ |
| 11 | 业务层接线 | `MontionManager` 初始化处 `new DeltaMontionControl(...)` | ☐ |
| 12 | 平台目标 | 项目属性设为 x86 或 x64 | ☐ |
| 13 | DLL 部署 | 对应平台 DLL 复制到输出目录 | ☐ |
| 14 | 核验门禁 | 跑 §12.2，确认不存在 SDK 未声明的 API 名 | ☐ |
| 15 | 联调 | 单轴使能 → 回零 → 点位 → Jog → IO → 急停 | ☐ |

---

## 15. OPEN 项

| # | 议题 | 说明 |
|---|------|------|
| 1 | 轴/IO 拓扑配置来源 | `nodeId` / `slotNo` / `Equiv` 目前由代码传入，是否改为配置文件（XML）待定 |
| 2 | 焊缝跟踪主轴方案 | ECAM2 的主轴来源（虚拟轴 / 外部编码器）与凸轮曲线待工艺参数确定 |
| 3 | 多卡场景 | 当前规范默认单卡（`_cardNoList[0]`），多卡并行时的轴归属规则待定 |
| 4 | AD/DA 通道映射 | 经 PDO OD 读写，OD 索引与物理通道的对应表待硬件清单确定 |
| 5 | 高级功能范围 | 插补 / 龙门 / PVT 是否一期需要，待工艺确认 |

> 振镜与对焦不在本模块，由焊接头侧承接：`ILaserWeldHeadController.SetAutoFocusPosition` 已覆盖对焦，振镜接口待焊接头文档定义。

---

## 相关页面

- [[api/DeltaEtherCAT-Native]] — 832 个台达 API 分组速查（SDK 实证）
- [[api/LeadshineLSnmc-Reference]] — 雷赛参考基线（抽象层形态与六条纪律）
- [[modules/MotionControl]] — 运动控制模块页
- [[decisions/ADR-036-MotionControllerDeltaReplacement]] — 运动控制器选型决策
