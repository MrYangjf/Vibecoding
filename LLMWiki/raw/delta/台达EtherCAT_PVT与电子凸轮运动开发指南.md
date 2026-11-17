# 台达 EtherCAT PVT 与电子凸轮运动开发指南

> 基于台达 PCI-L221 EtherCAT 主站卡，.NET Framework 4.8
> 涵盖 PVT（位置-速度-时间）多段插值运动与 ECAM/ECAM2 电子凸轮主从跟随运动

---

## 第一部分：PVT 运动（位置-速度-时间）

### 1.1 作用原理

PVT（Position-Velocity-Time）是一种**多段轨迹插值运动**，用户预先定义一系列路径点，每个点包含三个参数：

| 参数 | 含义 | 单位 |
|------|------|------|
| `TargetPos` | 目标位置 | 脉冲 |
| `TargetVel` | 该点的目标速度 | 脉冲/s |
| `TargetTime` | 到达该点的时间间隔 | ms |

主站卡（PCI-L221）内部根据相邻两点的位置、速度和时间，使用**三次多项式插值**（Cubic Spline）自动计算出平滑的运动轨迹，保证：
- 位置连续（经过每个定义点）
- 速度连续（每个点的速度等于设定值）
- 加速度连续（无冲击）

**与普通点位运动的区别**：普通 `CSP_Start_Move` 只能做单段 S 曲线加减速；PVT 可以一次性定义几十甚至上百个路径点，主站卡自动完成整条复杂轨迹的平滑运动，无需上位机逐段下发指令。

**典型应用**：
- 复杂曲线轨迹（如异形切割、涂胶路径）
- 需要经过中间精确点位的连续运动
- 多段速度变化的连续工艺动作

### 1.2 使用接口

PVT 共 6 个 API，全部在 `EtherCATAdvancedNative.cs`（或 `EtherCATMotionNative.cs`）中：

#### 1.2.1 PVT 运动（标准模式）

```csharp
// 标准 PVT 运动：位置+速度+时间三点定义
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_PVT_Move")]
public static extern ushort CS_ECAT_Slave_CSP_Start_PVT_Move(
    ushort CardNo,      // 卡号
    ushort NodeID,      // 从站号
    ushort SlotID,      // 槽号
    int DataCnt,        // 路径点数量
    ref int TargetPos,  // 目标位置数组（脉冲）
    ref int TargetTime, // 时间间隔数组（ms）
    ref int TargetVel,  // 目标速度数组（脉冲/s）
    ushort Abs);        // 0=相对位置, 1=绝对位置
```

#### 1.2.2 PVT Complete 运动（带起止速度约束）

```csharp
// PVT Complete：在标准 PVT 基础上增加起始速度和结束速度约束
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_PVTComplete_Move")]
public static extern ushort CS_ECAT_Slave_CSP_Start_PVTComplete_Move(
    ushort CardNo,
    ushort NodeID,
    ushort SlotID,
    int DataCnt,        // 路径点数量
    ref int TargetPos,  // 目标位置数组
    ref int TargetTime, // 时间间隔数组
    int StrVel,         // 起始速度（脉冲/s）
    int EndVel,         // 结束速度（脉冲/s）
    ushort Abs);        // 0=相对, 1=绝对
```

> **PVT vs PVT Complete 的区别**：标准 PVT 不约束第一段起点和最后一段终点的速度（由插值自动计算）；PVT Complete 允许显式指定起始速度和结束速度，适合与前后运动段无缝衔接。

#### 1.2.3 PVT 配置（预下载不启动）

```csharp
// 配置 PVT 数据到主站卡，但不启动运动（需配合其他触发方式）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_PVT_Config")]
public static extern ushort CS_ECAT_Slave_CSP_Start_PVT_Config(
    ushort CardNo, ushort NodeID, ushort SlotID,
    int DataCnt, ref int TargetPos, ref int TargetTime, ref int TargetVel, ushort Abs);

// PVT Complete 配置
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_PVTComplete_Config")]
public static extern ushort CS_ECAT_Slave_CSP_Start_PVTComplete_Config(
    ushort CardNo, ushort NodeID, ushort SlotID,
    int DataCnt, ref int TargetPos, ref int TargetTime,
    int StrVel, int EndVel, ushort Abs);
```

#### 1.2.4 PVT 多轴同步运动

```csharp
// 多轴 PVT 同步启动（需先逐轴调用 PVT_Config 下载数据，再统一启动）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_PVT_Sync_Move")]
public static extern ushort CS_ECAT_Slave_CSP_Start_PVT_Sync_Move(
    ushort CardNo,      // 卡号
    ushort AxisNum,     // 轴数量
    ref ushort AxisArray,  // 从站号数组
    ref ushort SlotArray); // 槽号数组
```

#### 1.2.5 PVT 状态读取

```csharp
// 获取当前 PVT 运动到第几个点（NowMotCount: 当前正在执行的路径点序号）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_PVT_Get_NowMotCount")]
public static extern ushort CS_ECAT_Slave_CSP_PVT_Get_NowMotCount(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ref ushort NowMotCount);
```

### 1.3 配置方法

#### 1.3.1 单轴 PVT 运动步骤

```
1. 初始化主站 + 伺服使能（CSP模式）
2. 准备路径点数组（TargetPos / TargetTime / TargetVel）
3. 调用 CS_ECAT_Slave_CSP_Start_PVT_Move 启动运动
4. 轮询 IsMoving() 或 PVT_Get_NowMotCount 监控进度
5. 运动完成后可继续下一段
```

#### 1.3.2 代码示例

```csharp
using DeltaEtherCAT;

// 假设已初始化，axis 是 DeltaMontionAxis，CardNo=0, NodeId=1, SlotNo=0
ushort cardNo = 0;
ushort nodeId = 1;
ushort slotNo = 0;

// 定义 5 个路径点（示例：走一个折线）
int pointCount = 5;
int[] targetPos  = new int[pointCount] { 10000, 30000, 50000, 70000, 100000 };  // 脉冲
int[] targetTime = new int[pointCount] { 500,   500,   1000,  500,   500 };        // ms
int[] targetVel  = new int[pointCount] { 10000, 20000, 30000, 20000, 10000 };      // 脉冲/s

// 启动 PVT 运动（绝对位置）
ushort ret = EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_PVT_Move(
    cardNo, nodeId, slotNo,
    pointCount,
    ref targetPos[0],
    ref targetTime[0],
    ref targetVel[0],
    1);  // 1=绝对位置

if (ret != DeltaErrorCode.NO_ERROR)
{
    Console.WriteLine($"PVT 启动失败: 0x{ret:X4}");
    return;
}

// 监控运动进度
while (axis.IsMoving() == 0)  // 0=运动中
{
    ushort nowCount = 0;
    EtherCATAdvancedNative.CS_ECAT_Slave_CSP_PVT_Get_NowMotCount(
        cardNo, nodeId, slotNo, ref nowCount);
    Console.WriteLine($"PVT 进度: {nowCount}/{pointCount}, 当前位置: {axis.GetPosition():F1}");
    System.Threading.Thread.Sleep(50);
}
Console.WriteLine("PVT 运动完成");
```

#### 1.3.3 多轴同步 PVT 运动步骤

```
1. 逐轴调用 PVT_Config 下载各自的路径点数据（不启动）
2. 调用 PVT_Sync_Move 统一启动所有轴
3. 逐轴监控运动状态
```

```csharp
// 轴1 下载数据
EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_PVT_Config(
    cardNo, nodeId1, slotNo1, count1, ref pos1[0], ref time1[0], ref vel1[0], 1);

// 轴2 下载数据
EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_PVT_Config(
    cardNo, nodeId2, slotNo2, count2, ref pos2[0], ref time2[0], ref vel2[0], 1);

// 统一启动
ushort[] axisArray = new ushort[] { nodeId1, nodeId2 };
ushort[] slotArray = new ushort[] { slotNo1, slotNo2 };
EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_PVT_Sync_Move(
    cardNo, 2, ref axisArray[0], ref slotArray[0]);
```

#### 1.3.4 注意事项

1. **数组传递**：C# 中传递数组首元素用 `ref array[0]`，数组必须在调用期间保持固定（不要被 GC 移动），建议用 `fixed` 或确保数组不被回收。
2. **时间间隔**：`TargetTime` 单位是 **ms**，不是秒。每个点的时间间隔是从**上一个点**到当前点的时间，不是绝对时间。
3. **速度约束**：`TargetVel` 是到达该点时的速度，主站卡会保证插值后该点速度等于设定值。如果速度设定不合理（如时间太短无法达到），可能返回参数错误。
4. **最大点数**：PVT 路径点数量受主站卡内存限制，建议单次不超过 256 点（具体上限参考台达官方手册）。
5. **位置单位**：`TargetPos` 是**脉冲单位**，需在应用层用 `Equiv` 做工程单位转换。
6. **运动模式**：PVT 运动基于 CSP 模式，启动前必须确保轴已在 CSP 模式且伺服使能。

---

## 第二部分：电子凸轮运动（ECAM / ECAM2）

### 2.1 作用原理

电子凸轮（Electronic CAM，ECAM）是一种**主从跟随运动**：一个从轴（Slave）的位置按照预先定义的**凸轮表（Cam Table）** 跟随一个主轴（Master）的位置运动。

```
主轴位置(Master) → 凸轮表映射 → 从轴位置(Slave)
```

**凸轮表**本质是一个"主轴位置 → 从轴位置"的映射表（类似机械凸轮的轮廓曲线），主站卡根据主轴实时位置，通过插值计算出从轴应处的位置并驱动从轴运动。

**主轴来源（SourceType）**：

| SourceType | 含义 | 说明 |
|------------|------|------|
| 0 | 实际轴（Actual Axis） | 另一个 EtherCAT 伺服轴的实际位置 |
| 1 | 指令轴（Command Axis） | 另一个 EtherCAT 伺服轴的指令位置 |
| 2 | 虚拟轴（Virtual Axis） | 主站卡内部虚拟编码器 |
| 3 | 外部编码器（External Encoder） | 接在主站卡上的外部编码器输入 |

**与电子齿轮的区别**：电子齿轮是固定比例跟随（从轴位置 = 主轴位置 × 齿轮比）；电子凸轮是**非线性映射**，从轴与主轴的关系可以是任意曲线（如先加速同步、再匀速同步、最后减速退出）。

**典型应用**：
- **飞剪（Flying Shear）**：刀具轴跟随物料输送轴，在同步段完成剪切
- **旋切（Rotary Cut）**：旋转刀辊跟随进料速度，在同步角度完成切割
- **间歇印刷（Intermittence Print）**：印刷滚筒跟随送料轴，在同步段印刷
- **包装机械**：封口、裁切、贴标等需要主从同步的工位

### 2.2 两代 API 对比

台达提供两代电子凸轮 API：

| 对比项 | ECAM（第一代） | ECAM2（第二代） |
|--------|---------------|-----------------|
| API 数量 | 13 个 | 19 个 |
| 凸轮表定义 | `ECAM_Table_Data`（位置表）/ `ECAM_Velocity_Data`（速度表） | `ECAM2_Profile_Data`（主从位置点表，更灵活） |
| 专用工艺 | 飞剪、间歇印刷（内置模板） | 飞剪、旋切（内置模板，参数更丰富） |
| 凸轮开关 | 无 | `ECAM2_CamSwitch`（按主轴位置触发输出） |
| 相位调整 | 无 | `ECAM2_Phasing`（动态相位偏移） |
| 轮廓修改 | 无 | `ECAM2_Profile_Modify`（运行中修改凸轮点） |
| 推荐使用 | 简单凸轮跟随 | 新项目优先使用，功能更全 |

### 2.3 ECAM（第一代）使用接口

#### 2.3.1 凸轮表数据定义

```csharp
// 位置表模式：定义主轴位置区间 → 从轴位置的映射
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Table_Data")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Table_Data(
    ushort CardNo,          // 卡号
    ushort ECAMNo,          // 凸轮表编号（0~N，主站卡支持多组凸轮表）
    int RegionNum,          // 区间数量
    ref int DataArray,      // 数据数组（每区间4个int: 主起, 主止, 从起, 从止）
    int Master_Pulse,       // 主轴每转脉冲数
    double Slave_mm_Pulse,  // 从轴脉冲当量（mm/脉冲）
    double Master_mm_Pulse); // 主轴脉冲当量（mm/脉冲）
```

```csharp
// 速度表模式：按速度百分比定义凸轮轮廓
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Velocity_Data")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Velocity_Data(
    ushort CardNo, ushort ECAMNo,
    int RegionNum,          // 区间数量
    ref int[] Percent,      // 每区间速度百分比数组
    int SCurveRegion,       // S曲线区间
    int TotalLength,        // 总长度
    int Master_Pulse_P,     // 主轴每转脉冲
    double Slave_mm_Pulse,  // 从轴脉冲当量
    double Master_mm_Pulse, // 主轴脉冲当量
    ushort Construct_Mode); // 构建模式
```

#### 2.3.2 专用工艺模板

```csharp
// 飞剪数据（自动生成飞剪凸轮表）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Flying_Shears_Data")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Flying_Shears_Data(
    ushort CardNo, ushort ECAMNo,
    double GearNum_A,       // 齿轮比分子
    double GearNum_B,       // 齿轮比分母
    int KnifeNum,           // 刀具数量
    double SlaveDiameter,   // 从轴（刀辊）直径
    double EncoderDiameter,  // 编码器轮直径
    int EncoderPulseRev,    // 编码器每转脉冲
    int SlavePUURev,        // 从轴每转脉冲
    int CutLength,          // 裁切长度
    int RegionNum,          // 区间数量
    ref int[] Region,       // 区间数据
    int Slave_Prelead,      // 从轴预行程
    int Master_Engage_Prelead, // 主轴啮合预行程
    ushort PreLeadMode);    // 预行程模式
```

```csharp
// 间歇印刷数据
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Intermittence_Print_Data")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Intermittence_Print_Data(
    ushort CardNo, ushort ECAMNo,
    int RegionNum,          // 区间数
    int PrintLength,        // 印刷长度
    int BlankLength,        // 空白长度
    double GearNum_A, double GearNum_B,
    int SlavePUURev,        // 从轴每转脉冲
    double SlaveDiameter,    // 从轴直径
    int MasterPulseRev,      // 主轴每转脉冲
    double MasterDiameter,   // 主轴直径
    int HoldingAreaDeg,      // 保持区角度
    int SCurveDeg,           // S曲线角度
    int SynIncreaseDeg);     // 同步增加角度
```

#### 2.3.3 啮合 / 脱离 / 补偿参数

```csharp
// 设置啮合参数（从轴何时开始跟随主轴）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Set_Engage_Parameters")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Set_Engage_Parameters(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort SourceType,       // 主轴来源类型（0=实际轴,1=指令轴,2=虚拟轴,3=外部编码器）
    ushort EngageNodeID,     // 啮合主轴从站号
    ushort EngageSlotID,     // 啮合主轴槽号
    ushort SourceNo,         // 来源编号（虚拟轴/编码器编号）
    int Engage_PreLed,       // 啮合预行程（从轴提前加速的距离）
    int Cycle_PreLead,       // 周期预行程
    ushort Engage_Mode);     // 啮合模式
```

```csharp
// 设置脱离参数（从轴何时退出跟随）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Set_DisEngage_Parameters")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Set_DisEngage_Parameters(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort SourceType,
    ushort DisEngageNodeID, ushort DisEngageSlotID,
    ushort SourceNo,
    int DisEngage_Position,  // 脱离位置（主轴位置到达此值时脱离）
    ushort DI_DisEngage,     // 数字输入触发脱离（0=不使用）
    ushort DisEngage_TurnOff, // 脱离后是否关闭伺服
    ushort DisEngage_Mode);   // 脱离模式
```

```csharp
// 设置补偿参数（从轴位置偏差自动补偿）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Set_Compensate_Parameters")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Set_Compensate_Parameters(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort SourceType,
    ushort CompensateNodeID, ushort CompensateSlotID,
    ushort SourceNo,
    int TargetPos,            // 目标位置
    int Max_Compensate_Ratio, // 最大补偿比例
    int Active_Range_Ratio,   // 生效范围比例
    ushort CompensateTime,    // 补偿时间
    ushort Enable);           // 使能
```

#### 2.3.4 启动 / 停止 / 状态

```csharp
// 启动电子凸轮运动
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Move")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Move(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort ECAMNo,            // 凸轮表编号
    ushort MasterNodeID,      // 主轴从站号
    ushort MasterSlotID,      // 主轴槽号
    ushort SourceType,        // 主轴来源类型
    ushort SourceNo);         // 来源编号
```

```csharp
// 运动中切换凸轮表
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Move_ChangeTable")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Move_ChangeTable(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort ECAMNo);  // 新凸轮表编号

// 设置缩放比例（运行中调整从轴跟随比例）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Set_Scale")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Set_Scale(
    ushort CardNo, ushort NodeID, ushort SlotID,
    double Percentage);  // 缩放百分比

// 禁用电子凸轮
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Disable")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Disable(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort Mode);  // 禁用模式

// 获取电子凸轮状态
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM_Get_Status")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM_Get_Status(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ref ushort Status);  // 状态输出
```

### 2.4 ECAM2（第二代）使用接口

#### 2.4.1 轮廓数据定义（推荐方式）

```csharp
// 定义凸轮轮廓：主轴位置 → 从轴位置 的点表（最灵活的定义方式）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Profile_Data")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_Data(
    ushort CardNo,          // 卡号
    ushort CamNo,           // 凸轮编号
    ushort DataNum,         // 数据点数量
    ref double MasterPos_mm,  // 主轴位置数组（工程单位mm）
    ref double SlavePos_mm,   // 从轴位置数组（工程单位mm）
    ref ushort Curve_Type,    // 曲线类型数组（每段的插值方式）
    ref double Velocity_Scale); // 速度缩放数组
```

```csharp
// 删除轮廓数据
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Delete_Profile_Data")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Delete_Profile_Data(
    ushort CardNo, ushort CamNo);

// 运行中修改某个凸轮点
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Profile_Modify")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_Modify(
    ushort CardNo, ushort CamNo,
    ushort PointNo,         // 要修改的点序号
    ref double Parameters);  // 新参数
```

#### 2.4.2 轮廓凸轮啮合 / 脱离

```csharp
// 轮廓凸轮啮合（从轴开始跟随主轴）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Profile_CamIn")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamIn(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort MasterNodeID, ushort MasterSlotID,  // 主轴
    ushort SourceType, ushort SourceNo,          // 主轴来源
    ushort CamNo,                                 // 凸轮编号
    ushort Periodic,                              // 是否周期循环
    ushort MasterAbsolute, ushort SlaveAbsolute,  // 主/从轴绝对/相对模式
    double MasterOffset, double SlaveOffset,      // 主/从轴偏移
    double MasterScaling, double SlaveScaling,    // 主/从轴缩放
    ushort StartMode,                             // 启动模式
    int MasterAxis_mm_Pulse, int SlaveAxis_mm_Pulse, // 主/从轴脉冲当量
    double Slave_MaxVel_mm,                       // 从轴最大速度
    double Slave_Acc_mm, double Slave_Dec_mm,     // 从轴加减速
    short MasterAxis_Dir, short SlaveAxis_Dir,    // 主/从轴方向
    ushort BufferMode);                            // 缓冲模式
```

```csharp
// 轮廓凸轮脱离（从轴停止跟随）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Profile_CamOut")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamOut(
    ushort CardNo, ushort NodeID, ushort SlotID);

// 轮廓凸轮设置
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Profile_CamSet")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamSet(
    ushort CardNo, ushort NodeID, ushort SlotID);
```

#### 2.4.3 专用工艺模板（飞剪 / 旋切）

```csharp
// 飞剪初始化（自动生成飞剪凸轮轮廓）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_FlyingShear_Initial")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_FlyingShear_Initial(
    ushort CardNo, ushort FlyingShearNo,
    double MasterRadius,        // 主轴（送料辊）半径
    double SlaveRadius,         // 从轴（刀辊）半径
    double CutLength,           // 裁切长度
    double MasterStartPosition, // 主轴起始位置
    double MasterSyncPosition,  // 主轴同步起始位置
    double SlaveSyncPosition,   // 从轴同步位置
    double SlaveEndPosition,    // 从轴结束位置
    double SlaveWaitPosition,   // 从轴等待位置
    double SlaveVelocity,       // 从轴速度
    double SlaveAcceleration,   // 从轴加速度
    double SlaveDeceleration);  // 从轴减速度

// 飞剪运动启动
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_FlyingShear_Move")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_FlyingShear_Move(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort FlyingShearNo,
    ushort MasterNodeID, ushort MasterSlotID,
    ushort SourceType, ushort SourceNo,
    int MasterAxis_PulseRev, int SlaveAxis_PulseRev,
    short MasterAxis_Dir, short SlaveAxis_Dir);
```

```csharp
// 旋切初始化
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_RotaryCut_Initial")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_RotaryCut_Initial(
    ushort CardNo, ushort RotCutNo,
    double RotaryAxisRadius,    // 旋转轴（刀辊）半径
    ushort RotaryAxisKnifeNum,  // 刀辊上的刀具数量
    double FeedAxisRadius,      // 进料轴半径
    double CutLenth,            // 裁切长度
    double SyncStartPos,        // 同步起始位置
    double SyncStopPos);        // 同步结束位置

// 旋切运动启动
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_RotaryCut_Move")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_RotaryCut_Move(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort RotCutNo,
    ushort MasterNodeID, ushort MasterSlotID,
    ushort SourceType, ushort SourceNo,
    int RotaryAxis_PulseRev, int FeedAxis_PulseRev,
    short RotaryAxis_Dir, short FeedAxis_Dir);
```

#### 2.4.4 啮合 / 脱离 / 补偿（ECAM2 版）

```csharp
// ECAM2 啮合参数
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Set_Engage_Parameters")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Set_Engage_Parameters(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort SourceType, ushort EngageNodeID, ushort EngageSlotID,
    ushort SourceNo, ushort Enable);

// ECAM2 脱离参数
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Set_DisEngage_Parameters")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Set_DisEngage_Parameters(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort SourceType, ushort DisEngageNodeID, ushort DisEngageSlotID,
    ushort SourceNo, ushort Enable);

// ECAM2 补偿参数
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Set_Compensate_Parameters")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Set_Compensate_Parameters(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ushort SourceType, ushort CompensateNodeID, ushort CompensateSlotID,
    ushort SourceNo,
    double TargetPos, double ActiveRangeRatio,
    double MaxVel, double Acceleration, double Deceleration,
    ushort Enable);
```

#### 2.4.5 状态 / 相位 / 凸轮开关

```csharp
// 获取 ECAM2 状态
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Get_Status")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Get_Status(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ref ushort Status);

// 获取从站信息（当前凸轮编号 + 当前表位置）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Get_Slave_Info")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Get_Slave_Info(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ref short pi16_CurrentCamNo,
    ref int pi32_CurrentTablePos);

// 禁用 ECAM2
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Disable")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Disable(
    ushort CardNo, ushort NodeID, ushort SlotID);

// 相位调整（运行中动态偏移从轴相位）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_Phasing")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_Phasing(
    ushort CardNo, ushort NodeID, ushort SlotID,
    double Dist,           // 相位偏移距离
    double MaxVel,         // 调整最大速度
    double Acceleration,   // 调整加速度
    double Deceleration);  // 调整减速度

// 凸轮开关（按主轴位置触发数字输出）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_CamSwitch")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_CamSwitch(
    ushort CardNo, ushort CamNo,
    ushort SwitchNum,      // 开关数量
    ref ushort Percent,     // 每个开关的触发位置百分比
    ushort Cam_Mode);       // 凸轮模式

// 凸轮开关状态
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Start_ECAM2_CamSwitch_Status")]
public static extern ushort CS_ECAT_Slave_CSP_Start_ECAM2_CamSwitch_Status(
    ushort CardNo, ushort NodeID, ushort SlotID,
    ref ushort Status);
```

### 2.5 配置方法（ECAM2 轮廓凸轮 — 推荐流程）

#### 2.5.1 标准电子凸轮使用步骤

```
1. 初始化主站 + 主轴/从轴伺服使能（CSP模式）
2. 定义凸轮轮廓数据（ECAM2_Profile_Data）
3. 配置啮合参数（ECAM2_Set_Engage_Parameters）— 可选
4. 启动凸轮啮合（ECAM2_Profile_CamIn）
5. 从轴自动跟随主轴运动
6. 运行中可修改轮廓（Profile_Modify）/ 调整相位（Phasing）/ 切换凸轮
7. 脱离凸轮（ECAM2_Profile_CamOut）
8. 禁用（ECAM2_Disable）
```

#### 2.5.2 代码示例（自定义轮廓凸轮）

```csharp
using DeltaEtherCAT;

ushort cardNo = 0;
ushort slaveNodeId = 2;   // 从轴（刀具）
ushort slaveSlotNo = 0;
ushort masterNodeId = 1;  // 主轴（送料）
ushort masterSlotNo = 0;
ushort camNo = 0;          // 凸轮表编号

// 第1步：定义凸轮轮廓（主轴位置 → 从轴位置映射）
// 示例：主轴 0~100mm 区间，从轴走一个"加速-同步-减速"曲线
ushort pointCount = 5;
double[] masterPos = new double[pointCount] { 0.0,  20.0, 50.0, 80.0, 100.0 };  // 主轴位置 mm
double[] slavePos  = new double[pointCount] { 0.0,  5.0,  50.0, 95.0, 100.0 };  // 从轴位置 mm
ushort[] curveType = new ushort[pointCount] { 1, 1, 1, 1, 1 };  // 1=S曲线插值
double[] velScale  = new double[pointCount] { 1.0, 1.0, 1.0, 1.0, 1.0 };

ushort ret = EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Profile_Data(
    cardNo, camNo, pointCount,
    ref masterPos[0], ref slavePos[0],
    ref curveType[0], ref velScale[0]);

// 第2步：启动凸轮啮合（从轴跟随主轴）
ret = EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamIn(
    cardNo, slaveNodeId, slaveSlotNo,
    masterNodeId, masterSlotNo,
    0,  // SourceType=0 实际轴
    0,  // SourceNo
    camNo,
    1,  // Periodic=1 周期循环
    1, 1,  // MasterAbsolute=1, SlaveAbsolute=1
    0.0, 0.0,  // 偏移
    1.0, 1.0,  // 缩放
    0,  // StartMode
    10000, 10000,  // 主/从轴脉冲当量（脉冲/mm）
    500.0,  // 从轴最大速度 mm/s
    1000.0, 1000.0,  // 从轴加减速 mm/s²
    1, 1,  // 主/从轴方向
    0);  // BufferMode

// 第3步：监控状态
ushort ecamStatus = 0;
EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Get_Status(
    cardNo, slaveNodeId, slaveSlotNo, ref ecamStatus);
Console.WriteLine($"ECAM2 状态: {ecamStatus}");

// 运行中动态调整相位（如补偿裁切偏差）
// EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Phasing(
//     cardNo, slaveNodeId, slaveSlotNo, 0.5, 100.0, 500.0, 500.0);

// 第4步：脱离凸轮
EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamOut(
    cardNo, slaveNodeId, slaveSlotNo);

// 第5步：禁用
EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Disable(
    cardNo, slaveNodeId, slaveSlotNo);
```

#### 2.5.3 飞剪使用流程（ECAM2 专用模板）

```
1. 初始化主站 + 送料轴（主轴）/ 刀辊轴（从轴）伺服使能
2. 调用 ECAM2_FlyingShear_Initial 配置飞剪参数（自动生成凸轮表）
3. 调用 ECAM2_FlyingShear_Move 启动飞剪跟随
4. 送料轴运动时，刀辊自动按飞剪曲线跟随：
   - 非同步段：刀辊加速/减速到同步速度
   - 同步段：刀辊线速度 = 送料速度，完成剪切
   - 剪切后：刀辊减速回到等待位置，准备下一次
5. 重复触发即可连续裁切
```

```csharp
// 飞剪初始化
EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_FlyingShear_Initial(
    cardNo,
    0,              // FlyingShearNo
    50.0,           // 主轴（送料辊）半径 mm
    30.0,           // 从轴（刀辊）半径 mm
    200.0,          // 裁切长度 mm
    0.0,            // 主轴起始位置
    50.0,           // 主轴同步起始位置
    0.0,            // 从轴同步位置
    360.0,          // 从轴结束位置（刀辊转一圈）
    180.0,          // 从轴等待位置
    300.0,          // 从轴速度 mm/s
    1000.0,         // 从轴加速度
    1000.0);        // 从轴减速度

// 启动飞剪
EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_FlyingShear_Move(
    cardNo, slaveNodeId, slaveSlotNo,
    0, masterNodeId, masterSlotNo,
    0, 0,  // SourceType=实际轴, SourceNo=0
    10000, 10000,  // 主/从轴每转脉冲
    1, 1);          // 主/从轴方向
```

#### 2.5.4 注意事项

1. **主轴必须先运动**：电子凸轮是从轴跟随主轴，主轴不动则从轴不动。啮合前确保主轴已在运动或即将运动。
2. **啮合预行程**：从轴需要提前加速到同步速度才能平稳啮合，`Engage_PreLed` 参数设置提前量。如果预行程不足，啮合时会有冲击。
3. **周期模式**：`Periodic=1` 时主轴走完一个周期后从轴自动回到起点重复，适合连续生产；`Periodic=0` 时只走一次。
4. **凸轮表编号**：主站卡支持多组凸轮表（`ECAMNo`/`CamNo`），可预下载多组，运行中通过 `ChangeTable` 切换。
5. **单位一致性**：`ECAM2_Profile_Data` 使用工程单位（mm），但脉冲当量参数必须正确设置，否则位置映射错误。
6. **从轴最大速度**：`Profile_CamIn` 中的 `Slave_MaxVel_mm` 必须大于凸轮表中从轴需要达到的最高速度，否则会报错或运动异常。
7. **ECAM vs ECAM2 选择**：新项目优先使用 ECAM2（功能更全、参数更合理、支持轮廓点表定义）；ECAM 保留用于兼容旧项目。

---

## 第三部分：应用场景 — 机器人X坐标驱动Y轴跟随

### 3.1 场景描述

设备挂载在机器人上，机器人沿 X 方向运动，X 坐标实时发送给上位机；上位机根据 X 坐标计算出 Y 轴目标位置，驱动台达直线电机（Y 轴）做跟随运动。

```
机器人X方向前进 ──(实时X坐标)──> 上位机计算Y坐标 ──(EtherCAT)──> 台达Y轴直线电机跟随
```

**核心需求**：
- 机器人 X 坐标实时接入（通信延迟尽可能低）
- Y 轴跟随平滑、无冲击
- X→Y 映射可能是固定曲线，也可能是动态计算

### 3.2 系统架构

```
┌──────────────┐   通信(TCP/SDK等)    ┌──────────────────────┐
│  机器人控制器  │ ───────────────────> │    上位机(PC)          │
│  (X轴运动)    │                        │  ① X坐标接收线程       │
└──────────────┘                        │  ② Y坐标计算           │
                                        │  ③ 写入虚拟轴/PVT下发  │
                                        └──────────┬─────────────┘
                                                   │ EtherCAT
                                        ┌──────────▼─────────────┐
                                        │   台达 PCI-L221         │
                                        │   (EtherCAT主站卡)      │
                                        └──────────┬─────────────┘
                                                   │
                                        ┌──────────▼─────────────┐
                                        │   Y轴直线电机            │
                                        │   (台达 EtherCAT 从站)   │
                                        └────────────────────────┘
```

### 3.3 机器人X坐标接入方式

| 接入方式 | 适用场景 | 实时性 | 实现复杂度 |
|---------|---------|--------|-----------|
| **KUKA RSI**（Robot Sensor Interface） | KUKA 机器人，需要实时位置反馈（推荐） | 极高（1~12ms 周期） | 中 |
| **KUKA Ethernet KRL**（EKI） | KUKA 机器人，TCP/XML 非实时通信 | 中（10~50ms） | 低 |
| 通用 TCP/IP Socket | 自定义协议，跨厂商 | 中（10~50ms） | 低 |
| 机器人 SDK 回调 | 机器人厂商提供 PC SDK | 高（1~10ms） | 中 |
| OPC UA | 工业标准协议，跨厂商 | 中（50~100ms） | 中 |
| 共享内存 | 机器人控制器与上位机同机或实时总线 | 极高（<1ms） | 高 |
| 串口 / Modbus RTU | 简单机器人或 PLC 中转 | 低（100ms+） | 低 |
| EtherCAT 从站模拟 | 上位机作为 EtherCAT 从站接收坐标 | 极高（周期级） | 高 |

**KUKA 推荐**：优先使用 **RSI**（UDP 实时接口，周期 1~12ms 可配置，可直接读取 `$POS_ACT.X`）；如果对实时性要求不高或机器人未安装 RSI 选项，使用 **Ethernet KRL**（TCP/XML，配置简单）。保证 X 坐标更新频率 ≥ 50Hz。

#### 3.3.1 X坐标接收线程（通用模板）

```csharp
using System.Net.Sockets;
using System.Threading;

public class RobotXPositionReceiver
{
    private TcpClient _tcpClient;
    private NetworkStream _stream;
    private Thread _receiveThread;
    private volatile bool _running;

    // 最新X坐标（线程安全读写）
    private readonly object _xLock = new object();
    private double _currentX;
    public double CurrentX
    {
        get { lock (_xLock) { return _currentX; } }
        private set { lock (_xLock) { _currentX = value; } }
    }

    // X坐标变化事件（可选，用于事件驱动模式）
    public event Action<double> OnXPositionUpdated;

    public bool Connect(string ip, int port)
    {
        try
        {
            _tcpClient = new TcpClient();
            _tcpClient.Connect(ip, port);
            _stream = _tcpClient.GetStream();
            _running = true;
            _receiveThread = new Thread(ReceiveLoop) { IsBackground = true };
            _receiveThread.Start();
            return true;
        }
        catch { return false; }
    }

    private void ReceiveLoop()
    {
        byte[] buffer = new byte[1024];
        while (_running)
        {
            try
            {
                int bytesRead = _stream.Read(buffer, 0, buffer.Length);
                if (bytesRead > 0)
                {
                    double x = ParseXPosition(buffer, bytesRead);
                    CurrentX = x;
                    OnXPositionUpdated?.Invoke(x);
                }
            }
            catch { Thread.Sleep(10); }
        }
    }

    // 根据具体机器人协议实现解析（示例：4字节double）
    private double ParseXPosition(byte[] data, int length)
    {
        return BitConverter.ToDouble(data, 0);
    }

    public void Close()
    {
        _running = false;
        _stream?.Close();
        _tcpClient?.Close();
    }
}
```

#### 3.3.2 KUKA RSI 接入（推荐，实时）

**RSI（Robot Sensor Interface）** 是 KUKA 官方的实时传感器接口，基于 UDP/IP 通信，周期可配置为 1~12ms，是获取机器人实时位置的最佳方式。

**工作原理**：
- 机器人端运行 RSI 上下文（RSIContext），每个插值周期（默认 12ms）向上位机发送一帧 XML 数据
- 数据包含机器人当前位置（`$POS_ACT` / `$AXIS_ACT`）、速度、IO 等
- 上位机解析 XML 提取 X 坐标，同时可返回修正量（CORR）给机器人
- 通信为 UDP，上位机作为 Server 监听指定端口

**机器人端配置（WorkVisual / SmartHMI）**：

```
1. 确认机器人已安装 RSI 选项（KSS 8.3+ 通常自带 RSI 3.x/4.x）
2. 在 WorkVisual 中导入 RSI 技术包
3. 配置 RSI 上下文：
   - 创建 RSIContext 对象
   - 添加 RSIObject：RSIBinary（UDP通信）
   - 配置目标 IP（上位机IP）和端口（如 59125）
   - 配置输出变量：$POS_ACT.X（X坐标）、$POS_ACT.Y、$POS_ACT.Z 等
   - 配置周期：12ms（默认）或 4ms/2ms/1ms（需高性能选项）
4. 在机器人程序中调用 RSI 上下文启动/停止
```

**机器人端 RSI 启动示例（KRL）**：

```pseudocode
DEF RSI_Follow()
  ; 初始化 RSI 上下文
  RSI_INIT("RSIContext1", 59125)  ; 端口号
  
  ; 启动 RSI 通信（开始向上位机发送位置）
  RSI_ON()
  
  ; 机器人运动（X方向前进）
  PTP XP1
  LIN XP2 C_DIS
  
  ; 停止 RSI
  RSI_OFF()
END
```

**上位机 C# RSI 接收实现**：

```csharp
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Xml.Linq;

public class KukaRsiReceiver
{
    private UdpClient _udpClient;
    private Thread _receiveThread;
    private volatile bool _running;
    private int _listenPort;

    private readonly object _xLock = new object();
    private double _currentX;
    private double _currentY;
    private double _currentZ;
    private int _sequenceCounter;

    public double CurrentX { get { lock (_xLock) { return _currentX; } } }
    public double CurrentY { get { lock (_xLock) { return _currentY; } } }
    public double CurrentZ { get { lock (_xLock) { return _currentZ; } } }

    public event Action<double, double, double> OnPositionUpdated;  // X, Y, Z

    public bool Start(int listenPort = 59125)
    {
        try
        {
            _listenPort = listenPort;
            _udpClient = new UdpClient(listenPort);
            _udpClient.Client.ReceiveTimeout = 5000;
            _running = true;
            _receiveThread = new Thread(ReceiveLoop) { IsBackground = true };
            _receiveThread.Start();
            return true;
        }
        catch { return false; }
    }

    private void ReceiveLoop()
    {
        IPEndPoint remoteEndPoint = new IPEndPoint(IPAddress.Any, 0);
        while (_running)
        {
            try
            {
                byte[] data = _udpClient.Receive(ref remoteEndPoint);
                if (data == null || data.Length == 0) continue;

                // RSI 数据为 XML 格式
                string xml = System.Text.Encoding.UTF8.GetString(data);
                ParseRsiXml(xml, remoteEndPoint);
            }
            catch (SocketException)
            {
                // 超时，继续等待
            }
            catch { Thread.Sleep(5); }
        }
    }

    private void ParseRsiXml(string xml, IPEndPoint remoteEndPoint)
    {
        try
        {
            XDocument doc = XDocument.Parse(xml);
            XElement root = doc.Root;

            // RSI XML 结构示例：
            // <Sen Type="ImFree">
            //   <AK>1</AK>          <!-- 序列号 -->
            //   <IPOC>123456</IPOC> <!-- 时间戳 -->
            //   <Pos X="100.5" Y="200.3" Z="50.0" A="0" B="0" C="0" />
            // </Sen>

            var posElem = root.Element("Pos");
            if (posElem != null)
            {
                double x = (double)posElem.Attribute("X");
                double y = (double)posElem.Attribute("Y");
                double z = (double)posElem.Attribute("Z");

                lock (_xLock)
                {
                    _currentX = x;
                    _currentY = y;
                    _currentZ = z;
                }
                OnPositionUpdated?.Invoke(x, y, z);
            }

            // 可选：向机器人返回应答（RSI 要求每帧都回复，否则超时断开）
            SendAck(remoteEndPoint);
        }
        catch { }
    }

    private void SendAck(IPEndPoint remoteEndPoint)
    {
        try
        {
            // RSI 应答帧（返回空修正量或ACK）
            string ack = "<Sen Type=\"ImFree\"><AK>1</AK><IPOC>0</IPOC></Sen>";
            byte[] ackData = System.Text.Encoding.UTF8.GetBytes(ack);
            _udpClient.Send(ackData, ackData.Length, remoteEndPoint);
        }
        catch { }
    }

    public void Stop()
    {
        _running = false;
        _udpClient?.Close();
    }
}
```

**RSI 关键注意事项**：
1. **必须回复每帧**：RSI 协议要求上位机每收到一帧就回复一帧，否则机器人端会判定通信超时并停止
2. **UDP 无连接**：使用 UDP，上位机作为 Server 监听端口，机器人作为 Client 主动连接
3. **XML 解析性能**：RSI 数据是 XML 格式，12ms 周期下解析开销可接受；1ms 周期建议用二进制模式（RSIBinary）
4. **坐标系确认**：确认 `$POS_ACT` 是基坐标系（BASE）还是工具坐标系（TOOL）下的位置，X 方向需与实际运动方向一致
5. **防火墙**：上位机防火墙需放行 RSI 监听端口（如 59125）的 UDP 入站

---

#### 3.3.3 KUKA Ethernet KRL (EKI) 接入（TCP/XML，非实时）

**Ethernet KRL（EKI）** 是 KUKA 官方的 TCP/IP 通信接口，使用 XML 格式数据，配置简单，适合对实时性要求不高的场景（10~50ms 更新率）。

**工作原理**：
- 机器人端配置 EKI 通道（XML 配置文件），建立 TCP 连接
- 机器人通过 `EKI_Send` 发送变量（如 `$POS_ACT.X`），通过 `EKI_GetString` / `EKI_GetReal` 接收数据
- 上位机作为 TCP Server 或 Client，解析 XML 提取 X 坐标
- 通信为 TCP，保证数据可靠传输

**机器人端 EKI 配置（XML 文件，如 `EKI_Config.xml`）**：

```xml
<ETHERNETKRL>
  <CONFIGURATION>
    <EXTERNAL>
      <IP>192.168.1.100</IP>       <!-- 上位机IP -->
      <PORT>54600</PORT>             <!-- 端口号 -->
      <TYPE>Client</TYPE>            <!-- 机器人作为Client连接上位机 -->
    </EXTERNAL>
    <INTERNAL>
      <ENVIRONMENT>Program</ENVIRONMENT>
      <BUFFERING Mode="FIFO" Limit="64"/>
      <PROTOCOL>XML</PROTOCOL>
    </INTERNAL>
  </CONFIGURATION>
  <RECEIVE>
    <XML>
      <ELEMENT Tag="Command/Type" Type="String"/>
      <ELEMENT Tag="Command/Value" Type="Real"/>
    </XML>
  </RECEIVE>
  <SEND>
    <XML>
      <ELEMENT Tag="Robot/Pos/X" Type="Real"/>    <!-- X坐标 -->
      <ELEMENT Tag="Robot/Pos/Y" Type="Real"/>
      <ELEMENT Tag="Robot/Pos/Z" Type="Real"/>
      <ELEMENT Tag="Robot/Vel/X" Type="Real"/>    <!-- X速度 -->
      <ELEMENT Tag="Robot/Status/Ready" Type="Bool"/>
    </XML>
  </SEND>
</ETHERNETKRL>
```

**机器人端 EKI 使用示例（KRL）**：

```pseudocode
DEF EKI_SendPosition()
  ; 初始化 EKI 通道
  EKI_Init("EKI_Config")
  EKI_Open("EKI_Config")
  
  ; 等待连接建立
  WAIT FOR EKI_CheckConnection("EKI_Config")
  
  ; 循环发送位置（在运动过程中持续发送）
  WHILE NOT $PROG_END
    ; 设置要发送的变量
    $FCT_INFO=1
    EKI_SetReal("EKI_Config", "Robot/Pos/X", $POS_ACT.X)
    EKI_SetReal("EKI_Config", "Robot/Pos/Y", $POS_ACT.Y)
    EKI_SetReal("EKI_Config", "Robot/Pos/Z", $POS_ACT.Z)
    EKI_SetReal("EKI_Config", "Robot/Vel/X", $VEL_ACT)
    
    ; 发送
    EKI_Send("EKI_Config", "Robot")
    
    ; 控制发送频率（如每20ms发送一次）
    WAIT SEC 0.02
  ENDWHILE
  
  EKI_Close("EKI_Config")
END
```

**上位机 C# EKI 接收实现**：

```csharp
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Xml.Linq;

public class KukaEkiReceiver
{
    private TcpListener _tcpListener;
    private TcpClient _robotClient;
    private NetworkStream _stream;
    private Thread _listenThread;
    private Thread _receiveThread;
    private volatile bool _running;
    private int _port;

    private readonly object _posLock = new object();
    private double _currentX;
    private double _currentY;
    private double _currentZ;
    private double _currentVelX;

    public double CurrentX { get { lock (_posLock) { return _currentX; } } }
    public double CurrentY { get { lock (_posLock) { return _currentY; } } }
    public double CurrentZ { get { lock (_posLock) { return _currentZ; } } }
    public double CurrentVelX { get { lock (_posLock) { return _currentVelX; } } }

    public event Action<double, double, double, double> OnPositionUpdated;  // X,Y,Z,Vx
    public event Action<bool> OnConnectionChanged;

    public bool Start(int port = 54600)
    {
        try
        {
            _port = port;
            _tcpListener = new TcpListener(IPAddress.Any, port);
            _tcpListener.Start();
            _running = true;
            _listenThread = new Thread(ListenLoop) { IsBackground = true };
            _listenThread.Start();
            return true;
        }
        catch { return false; }
    }

    private void ListenLoop()
    {
        while (_running)
        {
            try
            {
                _robotClient = _tcpListener.AcceptTcpClient();
                _robotClient.ReceiveBufferSize = 65536;
                _stream = _robotClient.GetStream();
                OnConnectionChanged?.Invoke(true);

                _receiveThread = new Thread(ReceiveLoop) { IsBackground = true };
                _receiveThread.Start();
                _receiveThread.Join();  // 阻塞直到断开

                OnConnectionChanged?.Invoke(false);
            }
            catch { Thread.Sleep(100); }
        }
    }

    private void ReceiveLoop()
    {
        byte[] buffer = new byte[65536];
        System.Text.StringBuilder xmlBuffer = new System.Text.StringBuilder();

        while (_running && _robotClient != null && _robotClient.Connected)
        {
            try
            {
                int bytesRead = _stream.Read(buffer, 0, buffer.Length);
                if (bytesRead <= 0) break;

                string fragment = System.Text.Encoding.UTF8.GetString(buffer, 0, bytesRead);
                xmlBuffer.Append(fragment);

                // EKI XML 以 <Robot> 开始 </Robot> 结束，可能有多帧粘包
                string allData = xmlBuffer.ToString();
                int endTagIndex;
                while ((endTagIndex = allData.IndexOf("</Robot>")) >= 0)
                {
                    int startTagIndex = allData.IndexOf("<Robot>");
                    if (startTagIndex >= 0 && startTagIndex < endTagIndex)
                    {
                        string frame = allData.Substring(startTagIndex, endTagIndex - startTagIndex + 8);
                        ParseEkiXml(frame);
                        allData = allData.Substring(endTagIndex + 8);
                    }
                    else
                    {
                        break;
                    }
                }
                xmlBuffer.Clear();
                xmlBuffer.Append(allData);
            }
            catch { Thread.Sleep(5); }
        }
    }

    private void ParseEkiXml(string xml)
    {
        try
        {
            XDocument doc = XDocument.Parse(xml);
            XElement root = doc.Root;  // <Robot>

            var posElem = root.Element("Pos");
            var velElem = root.Element("Vel");

            double x = posElem != null ? (double)posElem.Attribute("X") : 0;
            double y = posElem != null ? (double)posElem.Attribute("Y") : 0;
            double z = posElem != null ? (double)posElem.Attribute("Z") : 0;
            double vx = velElem != null ? (double)velElem.Attribute("X") : 0;

            lock (_posLock)
            {
                _currentX = x;
                _currentY = y;
                _currentZ = z;
                _currentVelX = vx;
            }
            OnPositionUpdated?.Invoke(x, y, z, vx);
        }
        catch { }
    }

    // 向上位机向机器人发送指令（可选）
    public void SendCommand(string type, double value)
    {
        if (_stream == null || !_robotClient.Connected) return;
        try
        {
            string xml = $"<Command><Type>{type}</Type><Value>{value}</Value></Command>";
            byte[] data = System.Text.Encoding.UTF8.GetBytes(xml);
            _stream.Write(data, 0, data.Length);
        }
        catch { }
    }

    public void Stop()
    {
        _running = false;
        _stream?.Close();
        _robotClient?.Close();
        _tcpListener?.Stop();
    }
}
```

**EKI 关键注意事项**：
1. **TCP 粘包处理**：EKI 使用 TCP 流式传输，XML 帧可能粘包，需要按 `<Robot>...</Robot>` 标签边界拆分
2. **发送频率控制**：机器人端用 `WAIT SEC 0.02` 控制发送频率，建议 20~50ms 一次，过快会导致缓冲区溢出
3. **连接方向**：EKI 支持机器人作为 Client（连接上位机）或 Server（等待上位机连接），推荐机器人作为 Client，上位机作为 Server 监听
4. **数据类型**：EKI 支持 String / Real / Int / Bool 等类型，坐标用 Real（对应 KRL 的 REAL，即 C# 的 double）
5. **配置文件部署**：EKI XML 配置文件需放到机器人 `C:\KRC\ROBOTER\Config\Common\EthernetKRL\` 目录下

---

#### 3.3.4 KUKA RSI vs EKI 选型对比

| 对比项 | RSI（Robot Sensor Interface） | EKI（Ethernet KRL） |
|--------|-------------------------------|---------------------|
| 协议 | UDP | TCP |
| 周期 | 1~12ms（可配置） | 20~50ms（程序控制） |
| 实时性 | 极高（硬实时级） | 中（非实时） |
| 数据格式 | XML / 二进制 | XML |
| 机器人端复杂度 | 高（需配置RSI上下文） | 低（EKI_Init + EKI_Send） |
| 上位机复杂度 | 中（需每帧回复ACK） | 中（需处理TCP粘包） |
| 能否控制机器人 | 可以（返回CORR修正量） | 可以（发送指令变量） |
| 适用场景 | 高精度实时跟随、力控、视觉伺服 | 状态监控、非实时数据交换、简单指令 |
| 推荐度（本场景） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**本场景建议**：Y 轴跟随机器人 X 坐标，对实时性要求高（跟随延迟直接影响精度），**优先使用 RSI**。如果机器人未安装 RSI 选项或调试时间有限，可先用 EKI 验证功能，后续再迁移到 RSI。

---

### 3.4 方案一：ECAM2 虚拟轴主轴（推荐）

#### 3.4.1 原理

将机器人 X 坐标作为**虚拟主轴**的位置输入，Y 轴作为从轴按预定义凸轮表跟随：

```
机器人X坐标 ──写入──> 虚拟轴位置(主轴) ──凸轮表映射──> Y轴位置(从轴)
```

- 主轴来源：`SourceType = 2`（虚拟轴）
- 凸轮表：预先定义 X→Y 的映射曲线（`ECAM2_Profile_Data`）
- 上位机职责：仅需把机器人 X 坐标实时写入虚拟轴位置
- 主站卡职责：内部插值计算 Y 轴位置，保证平滑无冲击

**优点**：
- 主站卡硬件插值，跟随平滑无冲击
- 上位机计算量极小（只写一个位置值）
- 支持 X→Y 映射为任意复杂曲线
- 自动处理加减速约束

**适用条件**：X→Y 映射关系是固定的或可预定义的，机器人 X 坐标更新频率稳定。

#### 3.4.2 虚拟轴位置写入 API

台达虚拟轴位置设置 API（在 `EtherCATAdvancedNative.cs` 中补充）：

```csharp
// 设置虚拟轴位置（将机器人X坐标写入虚拟轴）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Set_Virtual_Axis_Position")]
public static extern ushort CS_ECAT_Slave_CSP_Set_Virtual_Axis_Position(
    ushort CardNo,      // 卡号
    ushort VirtualNo,   // 虚拟轴编号
    int Position);      // 位置（脉冲）

// 设置虚拟轴速度（可选，速度模式下用）
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Set_Virtual_Axis_Velocity")]
public static extern ushort CS_ECAT_Slave_CSP_Set_Virtual_Axis_Velocity(
    ushort CardNo, ushort VirtualNo, int Velocity);

// 获取虚拟轴当前位置
[DllImport(DllPath, EntryPoint = "_ECAT_Slave_CSP_Get_Virtual_Axis_Position")]
public static extern ushort CS_ECAT_Slave_CSP_Get_Virtual_Axis_Position(
    ushort CardNo, ushort VirtualNo, ref int Position);
```

> 注：具体 API 名称以台达官方 `EtherCAT_DLL.cs` 为准，不同版本可能有差异。虚拟轴功能通常通过 `ECAT_Slave_CSP_Set_Virtual_Axis_*` 或 `ECAT_Master_Set_Virtual_Axis_*` 系列函数实现。

#### 3.4.3 配置步骤

```
1. 初始化主站 + Y轴伺服使能（CSP模式）
2. 定义凸轮表：ECAM2_Profile_Data（X位置 → Y位置映射）
3. 启动凸轮啮合：ECAM2_Profile_CamIn
   - SourceType = 2（虚拟轴）
   - SourceNo = 虚拟轴编号
   - Periodic = 0（非周期，X坐标持续递增）
4. 启动X坐标接收线程
5. 实时将机器人X坐标（mm）转换为脉冲，写入虚拟轴位置
6. Y轴自动按凸轮表跟随
7. 结束时：脱离凸轮 → 禁用 → 关闭X接收
```

#### 3.4.4 完整代码示例

```csharp
using DeltaEtherCAT;
using System.Threading;

public class RobotXYFollowController
{
    private ushort _cardNo = 0;
    private ushort _yNodeId = 1;      // Y轴从站号
    private ushort _ySlotNo = 0;
    private ushort _camNo = 0;         // 凸轮表编号
    private ushort _virtualNo = 0;     // 虚拟轴编号
    private double _xEquiv = 10000;    // X轴脉冲当量（脉冲/mm）
    private double _yEquiv = 10000;    // Y轴脉冲当量（脉冲/mm）

    private RobotXPositionReceiver _xReceiver;
    private Thread _followThread;
    private volatile bool _following;

    // X→Y映射函数（根据实际工艺定义）
    private Func<double, double> _xyMapping;

    public void Initialize(string robotIp, int robotPort, Func<double, double> xyMapping)
    {
        _xyMapping = xyMapping;

        // 1. 连接机器人，接收X坐标
        _xReceiver = new RobotXPositionReceiver();
        if (!_xReceiver.Connect(robotIp, robotPort))
            throw new Exception("机器人连接失败");

        // 2. Y轴伺服使能
        var yAxis = new DeltaMontionAxis(/* 控制器 */, "Y轴", _yNodeId, _ySlotNo);
        yAxis.Equiv = _yEquiv;
        yAxis.ServoOn();

        // 3. 定义凸轮表（X→Y映射）
        DefineCamProfile();

        // 4. 启动凸轮啮合（虚拟轴主轴）
        StartCamEngage();
    }

    private void DefineCamProfile()
    {
        // 假设X范围 0~1000mm，采样100个点
        ushort pointCount = 100;
        double[] masterPos = new double[pointCount];  // X位置 mm
        double[] slavePos  = new double[pointCount];  // Y位置 mm
        ushort[] curveType = new ushort[pointCount];
        double[] velScale  = new double[pointCount];

        double xMin = 0, xMax = 1000;
        for (int i = 0; i < pointCount; i++)
        {
            masterPos[i] = xMin + (xMax - xMin) * i / (pointCount - 1);
            slavePos[i]  = _xyMapping(masterPos[i]);  // 计算对应Y
            curveType[i] = 1;   // S曲线插值
            velScale[i]  = 1.0;
        }

        EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Profile_Data(
            _cardNo, _camNo, pointCount,
            ref masterPos[0], ref slavePos[0],
            ref curveType[0], ref velScale[0]);
    }

    private void StartCamEngage()
    {
        EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamIn(
            _cardNo, _yNodeId, _ySlotNo,
            0, 0,                              // 主轴NodeId/SlotId（虚拟轴时填0）
            2, _virtualNo,                     // SourceType=2 虚拟轴, SourceNo=虚拟轴编号
            _camNo,
            0,                                  // Periodic=0 非周期
            1, 1,                               // 主/从绝对模式
            0.0, 0.0,                           // 偏移
            1.0, 1.0,                           // 缩放
            0,                                  // 启动模式
            (int)_xEquiv, (int)_yEquiv,        // 主/从脉冲当量
            500.0,                              // Y轴最大速度 mm/s
            1000.0, 1000.0,                     // Y轴加减速 mm/s²
            1, 1,                               // 方向
            0);                                 // 缓冲模式
    }

    public void StartFollowing()
    {
        _following = true;
        _followThread = new Thread(FollowLoop) { IsBackground = true };
        _followThread.Start();
    }

    private void FollowLoop()
    {
        while (_following)
        {
            // 读取最新机器人X坐标
            double xMm = _xReceiver.CurrentX;

            // 转换为脉冲，写入虚拟轴位置
            int xPulse = (int)(xMm * _xEquiv);
            EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Set_Virtual_Axis_Position(
                _cardNo, _virtualNo, xPulse);

            // 控制更新频率（建议与机器人X坐标输出频率一致，如20ms）
            Thread.Sleep(20);
        }
    }

    public void StopFollowing()
    {
        _following = false;
        _followThread?.Join(1000);

        // 脱离凸轮
        EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamOut(
            _cardNo, _yNodeId, _ySlotNo);
        EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Disable(
            _cardNo, _yNodeId, _ySlotNo);

        _xReceiver?.Close();
    }
}
```

#### 3.4.5 使用示例

```csharp
// 定义X→Y映射：例如 Y = 50 * sin(0.01 * X) + 50
var controller = new RobotXYFollowController();
controller.Initialize("192.168.1.10", 10000, x => 50.0 * Math.Sin(0.01 * x) + 50.0);
controller.StartFollowing();

// 机器人开始X方向运动，Y轴自动跟随
// ...

controller.StopFollowing();
```

---

### 3.5 方案二：PVT 实时点序列

#### 3.5.1 原理

不使用凸轮表，而是实时接收 X 坐标、计算 Y 坐标，组成 PVT 点序列直接下发给 Y 轴：

```
机器人X坐标 ──> 计算Y坐标 ──> 组装PVT点(位置,速度,时间) ──> PVT_Config下发 ──> Y轴运动
```

**优点**：
- 极度灵活，Y 坐标可以是任意实时计算结果
- 不需要预定义凸轮表
- 适合 X→Y 映射随工艺参数动态变化的场景

**缺点**：
- 上位机计算量大（需要计算每个点的位置和速度）
- 需要管理 PVT 缓冲区，保证点序列连续不中断
- 实时性要求高（X 坐标接收→计算→下发必须在一个周期内完成）
- 速度需要手动计算（PVT 要求每个点的速度值）

**适用条件**：X→Y 映射无法预定义（如基于视觉检测结果动态计算），需要运行中动态调整 Y 坐标。

#### 3.5.2 配置步骤

```
1. 初始化主站 + Y轴伺服使能（CSP模式）
2. 启动X坐标接收线程
3. 维护PVT点缓冲区（环形队列）
4. 接收X坐标 → 计算Y坐标和速度 → 加入缓冲区
5. 缓冲区积累足够点数（如16点），调用PVT_Config下载
6. 调用PVT_Move启动（或使用运动缓冲连续下发）
7. 监控PVT_Get_NowMotCount，及时补充新点
8. 结束时停止运动
```

#### 3.5.3 代码示例（核心逻辑）

```csharp
public class PVTFollowController
{
    private ushort _cardNo = 0;
    private ushort _yNodeId = 1;
    private ushort _ySlotNo = 0;
    private double _yEquiv = 10000;

    private RobotXPositionReceiver _xReceiver;
    private Queue<PVTPoint> _pvtBuffer = new Queue<PVTPoint>();
    private double _lastY = 0;
    private DateTime _lastTime = DateTime.Now;
    private volatile bool _running;

    private struct PVTPoint
    {
        public int Position;   // Y位置（脉冲）
        public int Velocity;   // Y速度（脉冲/s）
        public int TimeMs;     // 时间间隔（ms）
    }

    public void Start()
    {
        _xReceiver = new RobotXPositionReceiver();
        _xReceiver.Connect("192.168.1.10", 10000);
        _xReceiver.OnXPositionUpdated += OnXUpdated;
        _running = true;

        var sendThread = new Thread(PVTSendLoop) { IsBackground = true };
        sendThread.Start();
    }

    private void OnXUpdated(double x)
    {
        // 根据X实时计算Y
        double y = CalculateY(x);

        // 计算速度和时间间隔
        DateTime now = DateTime.Now;
        double dtMs = (now - _lastTime).TotalMilliseconds;
        double dy = y - _lastY;
        double velocity = (dtMs > 0) ? (dy / dtMs * 1000) : 0;  // mm/s

        lock (_pvtBuffer)
        {
            _pvtBuffer.Enqueue(new PVTPoint
            {
                Position = (int)(y * _yEquiv),
                Velocity = (int)(velocity * _yEquiv),
                TimeMs = (int)Math.Max(dtMs, 1)
            });
        }

        _lastY = y;
        _lastTime = now;
    }

    // 实时计算Y坐标（可以是任意复杂逻辑，如视觉引导）
    private double CalculateY(double x)
    {
        return 50.0 * Math.Sin(0.01 * x) + 50.0;
    }

    private void PVTSendLoop()
    {
        const int batchSize = 16;
        while (_running)
        {
            PVTPoint[] batch;
            lock (_pvtBuffer)
            {
                if (_pvtBuffer.Count < batchSize)
                {
                    Thread.Sleep(5);
                    continue;
                }
                batch = new PVTPoint[batchSize];
                for (int i = 0; i < batchSize; i++)
                    batch[i] = _pvtBuffer.Dequeue();
            }

            int[] pos  = batch.Select(p => p.Position).ToArray();
            int[] vel  = batch.Select(p => p.Velocity).ToArray();
            int[] time = batch.Select(p => p.TimeMs).ToArray();

            // 下载PVT数据（使用运动缓冲连续模式）
            EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_PVT_Config(
                _cardNo, _yNodeId, _ySlotNo,
                batchSize, ref pos[0], ref time[0], ref vel[0], 1);

            Thread.Sleep(10);
        }
    }

    public void Stop()
    {
        _running = false;
        _xReceiver?.Close();
    }
}
```

---

### 3.6 两种方案对比与选型

| 对比项 | ECAM2 虚拟轴主轴（方案一） | PVT 实时点序列（方案二） |
|--------|---------------------------|------------------------|
| X→Y 映射 | 预定义凸轮表 | 实时计算 |
| 上位机计算量 | 极小（只写虚拟轴位置） | 大（计算位置+速度+缓冲管理） |
| 跟随平滑度 | 极高（硬件插值） | 高（取决于点密度和计算精度） |
| 实时性要求 | 低（写位置即可，主站卡插值） | 高（必须在周期内完成计算和下发） |
| 动态调整 Y | 需重新定义凸轮表或 `Profile_Modify` | 直接修改计算函数，即时生效 |
| 适用场景 | 固定曲线跟随（正弦、圆弧、预设轨迹） | 动态计算跟随（视觉引导、实时工艺调整） |
| 实现复杂度 | 中 | 高 |
| 推荐度 | ⭐⭐⭐⭐⭐（首选） | ⭐⭐⭐（特殊场景用） |

**选型建议**：
- X→Y 映射是固定曲线（如 Y = f(X) 已知且不频繁变化）→ **选 ECAM2 虚拟轴方案**
- Y 坐标需要基于外部输入（视觉、传感器、工艺参数）实时计算 → **选 PVT 方案**
- 可以混合使用：ECAM2 为主，运行中通过 `ECAM2_Profile_Modify` 动态调整个别凸轮点

---

### 3.7 关键注意事项

1. **X 坐标单位转换**：机器人 X 坐标通常是 mm，写入虚拟轴或 PVT 位置时需乘以脉冲当量 `_xEquiv`，确保单位一致。

2. **虚拟轴位置范围**：虚拟轴位置是 int 类型（32 位有符号），X 坐标持续递增时注意溢出。如果机器人 X 行程超过 2147483647 脉冲（约 214748mm @ 10000 脉冲/mm），需要定期清零虚拟轴并重新啮合。

3. **X 坐标更新频率**：建议 ≥ 50Hz（20ms）。频率过低会导致虚拟轴位置跳变，Y 轴跟随不平滑。

4. **凸轮表采样密度**：ECAM2 方案中，凸轮表点越多跟随越精确，但下载时间越长。建议在 X 行程范围内采样 50~200 个点，曲线曲率大的区域加密采样。

5. **Y 轴最大速度/加速度**：`Profile_CamIn` 中设置的 `Slave_MaxVel_mm` 和加减速必须大于实际跟随需要的值，否则主站卡会报错或截断运动。

6. **啮合时机**：建议在机器人开始 X 方向运动**之前**就启动凸轮啮合并写入初始 X 坐标，避免 Y 轴从静止突然跟随产生冲击。

7. **异常处理**：X 坐标通信中断时，应停止写入虚拟轴（Y 轴保持当前位置），并报警提示。恢复后重新同步 X 坐标再继续跟随。

8. **延迟补偿**：机器人 X 坐标从采集到上位机接收存在通信延迟（10~50ms），如果对跟随精度要求高，可以根据 X 速度做前馈预测：`X_predicted = X_current + Vx × delay`。

---

## 第四部分：UI 层设计（台达配置与监控界面）

> 本部分对齐现有 `UIControl/` 项目代码风格（`MasonMotionControl` 命名空间、`UserControl` + `IUpdate` 接口、构造注入、`UpdateStatus()`/`ShowStatus()` 刷新模式、Label 背景色状态灯、急停+安全检查、`Task` 异步操作、静态 `IsUIOperating` 防卡顿标志）。

### 4.1 UI 层在项目中的目录结构

UI 层作为 `MotionControl` 模块的子文件夹，与 `IMotion/`（抽象层）、`DeltaEtherCAT/`（台达实现层）并列：

```
MotionControl/                                    # 运动控制模块
├── Cylinder.cs                                   # 气缸业务类（不变）
├── MontionManager.cs                             # 运动管理器（不变）
│
├── IMotion/                                      # 抽象接口层（完全不变）
│   ├── Type.cs / MontionControl.cs / MontionAxis.cs
│   ├── InputIO.cs / OutputIO.cs / IOParam.cs ...
│
├── DeltaEtherCAT/                                # 台达实现层
│   ├── Native/                                   # L1 原生 P/Invoke 封装
│   │   ├── EtherCATMasterNative.cs              # 主站/从站/SDO/连接状态
│   │   ├── EtherCATMotionNative.cs              # 运动控制/回零/软限位
│   │   ├── EtherCATIONative.cs                  # 数字 IO
│   │   ├── EtherCATAdvancedNative.cs            # PVT/电子凸轮/电子齿轮
│   │   └── DeltaErrorCode.cs                     # 错误码
│   ├── DeltaMontionControl.cs                    # 台达控制器实现
│   ├── DeltaMontionAxis.cs                       # 台达轴实现
│   ├── DeltaInputIO.cs / DeltaOutputIO.cs       # 台达 IO 实现
│   └── DeltaSlaveScanner.cs                      # 从站扫描器
│
└── UIControl/                                    # UI 控件层（台达特有扩展）
    ├── IUpdate.cs                                # 刷新接口（不变，已有）
    ├── Events.cs                                 # 事件定义（不变，已有）
    ├── NativeMethods.cs                          # Win32 API（不变，已有）
    ├── ScrollFlowLayoutPanel.cs                  # 滚动流布局（不变，已有）
    │
    ├── AxisControl.cs / .designer.cs             # 轴控件（不变，已有，厂商无关）
    ├── CylinderControl.cs / .designer.cs         # 气缸控件（不变，已有）
    ├── MachineInputIO.cs / .designer.cs          # 输入IO控件（不变，已有）
    ├── MachineOutputIO.cs / .designer.cs         # 输出IO控件（不变，已有）
    │
    ├── DeltaMasterControl.cs / .designer.cs      # 【新增】台达主站状态控件
    ├── DeltaSlaveListControl.cs / .designer.cs   # 【新增】台达从站列表控件
    ├── DeltaAxisConfigDialog.cs / .designer.cs   # 【新增】台达轴参数配置弹窗
    ├── DeltaHomeConfigDialog.cs / .designer.cs   # 【新增】台达回零参数配置弹窗
    ├── DeltaCamConfigControl.cs / .designer.cs   # 【新增】电子凸轮表配置控件
    ├── DeltaPVTConfigControl.cs / .designer.cs   # 【新增】PVT 轨迹配置控件
    ├── DeltaConnectionMonitor.cs / .designer.cs   # 【新增】连接监控控件（WKC/帧计数）
    └── DeltaMainConfigForm.cs / .designer.cs      # 【新增】台达配置主窗体（TabControl）
```

**设计原则**：
- 现有 `AxisControl` / `MachineInputIO` / `CylinderControl` **完全不变**，因为它们面向 `MontionAxis` / `InputIO` / `OutputIO` 抽象基类编程，厂商无关
- 新增的台达特有控件（主站状态、从站列表、凸轮/PVT配置、连接监控）放在 `UIControl/` 下，前缀 `Delta` 区分
- 所有新增控件遵循同一套模式：`UserControl` + `IUpdate` + 构造注入 + `UpdateStatus()`/`ShowStatus()`

---

### 4.2 台达控制器在线与状态检查方式

台达 PCI-L221 **不需要应用层心跳**，EtherCAT 协议层 Working Counter（WKC）看门狗由主站卡硬件自动维护。UI 层通过以下 API 读取实时状态：

#### 4.2.1 状态检查 API 清单

| 状态维度 | API（`EtherCATMasterNative`） | 输出参数 | 判定逻辑 |
|---------|-------------------------------|----------|----------|
| **主站连接状态** | `CS_ECAT_Master_Get_Connect_Status` | `ref ushort Status` | `Status==0` 正常 |
| **WKC 看门狗** | `CS_ECAT_Master_Check_Working_Counter` | `ref ushort Abnormal_Flag`, `ref ushort Working_Slave_Cnt` | `Abnormal_Flag==0` 且 `Working_Slave_Cnt==期望从站数` |
| **WKC 错误计数** | `CS_ECAT_Master_Get_Working_Counter_ErrorCounter` | `ref ushort Error_Cnt` | 累计错误次数，持续增长=通信质量差 |
| **帧计数器** | `CS_ECAT_Master_Get_Frame_Counter` | `ref uint TxFrameCnt`, `RxFrameCnt`, `Frame_Error_Cnt` | `Frame_Error_Cnt` 持续增长=丢帧 |
| **周期耗时** | `CS_ECAT_Master_Get_Cycle_SpendTime` | `ref double Tx_Time`, `Tx_MaxTime`, `Rx_Time`, `Rx_MaxTime` | 最大耗时超过周期=延迟告警 |
| **从站连接状态** | `CS_ECAT_Slave_Get_Connect_Status` | `ref ushort OpState`, `ref ushort AlarmStatus` | `OpState==8`(OP，位掩码 0x08) 且 `AlarmStatus==0` |
| **轴状态字** | `CS_ECAT_Slave_Motion_Get_StatusWord` | `ref ushort StatusWord` | bit2(0x04)=Operation enabled, bit3(0x08)=Fault |

#### 4.2.2 OpState 状态码

| OpState | 含义 | UI 颜色 |
|---------|------|---------|
| 1 (0x01) | Init（初始化） | 灰色 |
| 2 (0x02) | Pre-Operational（预运行） | 黄色 |
| 4 (0x04) | Safe-Operational（安全运行） | 橙色 |
| 8 (0x08) | Operational（运行，正常） | 绿色 |

> **⚠️ OpState 编码更正（2026-09-18）**：上表原档写成 `0/1/2/3` 枚举，但实测 `CS_ECAT_Slave_Get_Connect_Status` 返回的是 **位掩码** `0x01/0x02/0x04/0x08`，Operational 真实值为 **8** 而非 3。代码常量 `EtherCATMasterNative.OpStateOperational` 已修正为 `8`。

#### 4.2.3 连接监控控件实现（`DeltaConnectionMonitor`）

对齐现有 `AxisControl` 的 `UpdateStatus()`/`ShowStatus()` 模式：

```csharp
namespace MasonMotionControl
{
    public partial class DeltaConnectionMonitor : UserControl, IUpdate
    {
        private DeltaMontionControl _deltaControl;
        private ushort _cardNo;
        private int _expectedSlaveCount;

        // 缓存状态字段（对齐 AxisControl 的 CurrentPos/CurrentIO/IsServoON 模式）
        private ushort _masterStatus;
        private ushort _wkcAbnormalFlag;
        private ushort _wkcWorkingSlaveCnt;
        private ushort _wkcErrorCnt;
        private uint _txFrameCnt;
        private uint _rxFrameCnt;
        private uint _frameErrorCnt;
        private double _txTime, _txMaxTime, _rxTime, _rxMaxTime;

        public DeltaConnectionMonitor(DeltaMontionControl control, int expectedSlaveCount)
        {
            InitializeComponent();
            _deltaControl = control;
            _cardNo = control.CardNo;
            _expectedSlaveCount = expectedSlaveCount;
            UpdateStatus();
        }

        // 对齐 IUpdate 接口
        public void UpdateStatus()
        {
            // 读取主站连接状态
            EtherCATMasterNative.CS_ECAT_Master_Get_Connect_Status(_cardNo, ref _masterStatus);
            // 读取 WKC 看门狗
            EtherCATMasterNative.CS_ECAT_Master_Check_Working_Counter(
                _cardNo, ref _wkcAbnormalFlag, ref _wkcWorkingSlaveCnt);
            // 读取 WKC 错误计数
            EtherCATMasterNative.CS_ECAT_Master_Get_Working_Counter_ErrorCounter(
                _cardNo, ref _wkcErrorCnt);
            // 读取帧计数器
            EtherCATMasterNative.CS_ECAT_Master_Get_Frame_Counter(
                _cardNo, ref _txFrameCnt, ref _rxFrameCnt, ref _frameErrorCnt);
            // 读取周期耗时
            EtherCATMasterNative.CS_ECAT_Master_Get_Cycle_SpendTime(
                _cardNo, ref _txTime, ref _txMaxTime, ref _rxTime, ref _rxMaxTime);

            ShowStatus();
        }

        private void ShowStatus()
        {
            if (InvokeRequired)
            {
                BeginInvoke(new Action(ShowStatus));
                return;
            }

            // 主站连接状态灯（对齐 MachineInputIO 的 lblIOStatus 背景色模式）
            lblMasterStatus.BackColor = (_masterStatus == 0) ? Color.DarkGreen : Color.Red;
            lblMasterStatus.Text = (_masterStatus == 0) ? "已连接" : "断开";

            // WKC 状态灯
            bool wkcOK = (_wkcAbnormalFlag == 0) && (_wkcWorkingSlaveCnt == _expectedSlaveCount);
            lblWkcStatus.BackColor = wkcOK ? Color.DarkGreen : Color.Red;
            lblWkcStatus.Text = wkcOK ? $"正常({_wkcWorkingSlaveCnt}/{_expectedSlaveCount})" : $"异常({_wkcWorkingSlaveCnt}/{_expectedSlaveCount})";

            // 帧错误率
            double errorRate = (_txFrameCnt > 0) ? (double)_frameErrorCnt / _txFrameCnt * 100 : 0;
            lblFrameError.Text = $"帧错误: {_frameErrorCnt} ({errorRate:F3}%)";
            lblFrameError.BackColor = (errorRate < 0.01) ? Color.DarkGreen : Color.Orange;

            // 周期耗时
            lblCycleTime.Text = $"发送: {_txTime:F2}ms(最大{_txMaxTime:F2}) 接收: {_rxTime:F2}ms(最大{_rxMaxTime:F2})";

            // WKC 错误计数
            lblWkcError.Text = $"WKC错误累计: {_wkcErrorCnt}";
        }
    }
}
```

#### 4.2.4 主程序中的刷新调度

对齐现有主程序的刷新模式（通常用 `Timer` 或后台线程定时调用所有 `IUpdate` 控件的 `UpdateStatus()`）：

```csharp
// 主窗体中，定时刷新所有 UI 控件（对齐现有模式）
private void timerRefresh_Tick(object sender, EventArgs e)
{
    if (AxisControl.IsUIOperating) return;  // 操作中暂停刷新，防卡顿（对齐现有静态标志）

    foreach (var ctrl in flowPanel.Controls.OfType<IUpdate>())
    {
        ctrl.UpdateStatus();
    }
}
```

---

### 4.3 配置轴 / IO / 运动的方式

#### 4.3.1 轴配置方式

轴配置分为**运行时参数**和**持久化参数**两类：

| 参数类型 | 配置方式 | API / 机制 |
|---------|---------|------------|
| 脉冲当量 Equiv | 运行时属性赋值 | `axis.Equiv = 10000;`（`DeltaMontionAxis` 属性） |
| 速度/加减速 | 运行时属性赋值 | `axis.MaxVel = 500; axis.AccTime = 0.2;` |
| 回零参数 | 配置弹窗 + API 下发 | `DeltaHomeConfigDialog` → `Home_Config` |
| 软限位 | 配置弹窗 + API 下发 | `DeltaAxisConfigDialog` → `CSP_Set_Softlimit` |
| 控制模式 | 伺服使能时自动设置 | `ServoOn()` 内部 `Set_Move_Mode(8=CSP)` |
| 电子齿轮比 | 高级配置 + API 下发 | `DeltaAxisConfigDialog` → `CSP_Set_Gear` |

**轴参数配置弹窗实现**（`DeltaAxisConfigDialog`），对齐现有 `AxisParam` 弹窗模式：

```csharp
namespace MasonMotionControl
{
    public partial class DeltaAxisConfigDialog : Form
    {
        private DeltaMontionAxis _axis;

        public DeltaAxisConfigDialog(DeltaMontionAxis axis)
        {
            InitializeComponent();
            _axis = axis;
            // 加载当前参数到控件
            txtEquiv.Text = _axis.Equiv.ToString();
            txtMaxVel.Text = _axis.MaxVel.ToString();
            txtAccTime.Text = _axis.AccTime.ToString();
            txtDecTime.Text = _axis.DecTime.ToString();
            txtPosLimit.Text = "1000";   // 正软限位
            txtNegLimit.Text = "-100";    // 负软限位
        }

        private void btnApply_Click(object sender, EventArgs e)
        {
            // 1. 应用运行时参数（属性赋值，对齐现有模式）
            _axis.Equiv = double.Parse(txtEquiv.Text);
            _axis.MaxVel = double.Parse(txtMaxVel.Text);
            _axis.AccTime = double.Parse(txtAccTime.Text);
            _axis.DecTime = double.Parse(txtDecTime.Text);

            // 2. 应用软限位（调用台达原生 API，脉冲单位转换）
            int posLimitPulse = (int)(double.Parse(txtPosLimit.Text) * _axis.Equiv);
            int negLimitPulse = (int)(double.Parse(txtNegLimit.Text) * _axis.Equiv);
            ushort ret = EtherCATMotionNative.CS_ECAT_Slave_CSP_Set_Softlimit(
                _axis.Container.ConnectNo, _axis.NodeId, _axis.SlotNo,
                posLimitPulse, negLimitPulse, 1);  // Mode=1 使能

            if (ret != DeltaErrorCode.NO_ERROR)
            {
                MessageBox.Show($"软限位设置失败: 0x{ret:X4}");
                return;
            }

            // 3. 保存到配置文件（持久化）
            SaveAxisConfigToFile();
            DialogResult = DialogResult.OK;
            Close();
        }
    }
}
```

#### 4.3.2 IO 配置方式

IO 配置通过 `DeltaInputIO` / `DeltaOutputIO` 的构造函数和属性完成，UI 层提供 IO 映射配置：

```csharp
// 创建台达 IO 实例（对齐现有 MachineInputIO 构造注入模式）
var startBtn = new DeltaInputIO(mgr.MontionControl, "启动按钮", nodeId: 2, slotNo: 0)
{
    IONo = 0,          // IO 位号
    IOEnable = true     // 使能
};
var runLamp = new DeltaOutputIO(mgr.MontionControl, "运行灯", nodeId: 3, slotNo: 0)
{
    IONo = 0
};

// UI 控件创建（完全复用现有 MachineInputIO / MachineOutputIO，厂商无关）
var inputCtrl = new MachineInputIO(startBtn);   // 现有控件，不变
var outputCtrl = new MachineOutputIO(runLamp);   // 现有控件，不变
flowPanel.Controls.Add(inputCtrl);
flowPanel.Controls.Add(outputCtrl);
```

**IO 映射配置 UI**（在 `DeltaMainConfigForm` 的 IO 页签中）：用 `DataGridView` 编辑 IO 名称、从站号、槽号、位号、逻辑功能，保存到 XML 配置文件。

#### 4.3.3 运动配置方式（PVT / 电子凸轮）

运动功能配置通过专用控件完成，对齐现有 `AxisControl` 的按钮操作模式：

**电子凸轮配置控件**（`DeltaCamConfigControl`）：

```csharp
namespace MasonMotionControl
{
    public partial class DeltaCamConfigControl : UserControl
    {
        private DeltaMontionAxis _slaveAxis;   // 从轴（Y轴）
        private ushort _camNo = 0;
        private DataTable _camTable;            // 凸轮表数据

        public DeltaCamConfigControl(DeltaMontionAxis slaveAxis)
        {
            InitializeComponent();
            _slaveAxis = slaveAxis;
            _camTable = new DataTable();
            _camTable.Columns.Add("主轴位置(mm)", typeof(double));
            _camTable.Columns.Add("从轴位置(mm)", typeof(double));
            _camTable.Columns.Add("曲线类型", typeof(ushort));
            dgvCamTable.DataSource = _camTable;
        }

        // 生成标准曲线（正弦/梯形/三角波），对齐现有 btnParam 弹窗模式
        private void btnGenerateSin_Click(object sender, EventArgs e)
        {
            _camTable.Clear();
            double xMin = 0, xMax = 1000, amplitude = 50, offset = 50;
            for (int i = 0; i <= 100; i++)
            {
                double x = xMin + (xMax - xMin) * i / 100;
                double y = amplitude * Math.Sin(0.01 * x) + offset;
                _camTable.Rows.Add(x, y, 1);  // 1=S曲线
            }
        }

        // 下载凸轮表到设备（调用 ECAM2_Profile_Data）
        private void btnDownload_Click(object sender, EventArgs e)
        {
            if (_camTable.Rows.Count < 2)
            {
                MessageBox.Show("凸轮表至少需要2个点");
                return;
            }

            int count = _camTable.Rows.Count;
            double[] masterPos = new double[count];
            double[] slavePos = new double[count];
            ushort[] curveType = new ushort[count];
            double[] velScale = new double[count];

            for (int i = 0; i < count; i++)
            {
                masterPos[i] = (double)_camTable.Rows[i][0];
                slavePos[i] = (double)_camTable.Rows[i][1];
                curveType[i] = (ushort)_camTable.Rows[i][2];
                velScale[i] = 1.0;
            }

            ushort ret = EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Profile_Data(
                _slaveAxis.Container.ConnectNo, _camNo, (ushort)count,
                ref masterPos[0], ref slavePos[0],
                ref curveType[0], ref velScale[0]);

            if (ret != DeltaErrorCode.NO_ERROR)
                MessageBox.Show($"凸轮表下载失败: 0x{ret:X4}");
            else
                MessageBox.Show("凸轮表下载成功");
        }

        // 启动凸轮啮合（虚拟轴主轴，SourceType=2）
        private void btnEngage_Click(object sender, EventArgs e)
        {
            ushort ret = EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamIn(
                _slaveAxis.Container.ConnectNo, _slaveAxis.NodeId, _slaveAxis.SlotNo,
                0, 0,                    // 主轴 NodeId/SlotId（虚拟轴填0）
                2, 0,                    // SourceType=2 虚拟轴, SourceNo=0
                _camNo,
                0,                       // Periodic=0 非周期
                1, 1,                    // 主/从绝对模式
                0.0, 0.0,                // 偏移
                1.0, 1.0,                // 缩放
                0,                       // 启动模式
                (int)_slaveAxis.Equiv, (int)_slaveAxis.Equiv,  // 脉冲当量
                _slaveAxis.MaxVel,       // 从轴最大速度
                1000.0, 1000.0,          // 加减速
                1, 1,                    // 方向
                0);                      // 缓冲模式

            if (ret != DeltaErrorCode.NO_ERROR)
                MessageBox.Show($"凸轮啮合失败: 0x{ret:X4}");
        }

        // 脱离凸轮
        private void btnDisengage_Click(object sender, EventArgs e)
        {
            EtherCATAdvancedNative.CS_ECAT_Slave_CSP_Start_ECAM2_Profile_CamOut(
                _slaveAxis.Container.ConnectNo, _slaveAxis.NodeId, _slaveAxis.SlotNo);
        }
    }
}
```

**PVT 配置控件**（`DeltaPVTConfigControl`）：类似模式，用 `DataGridView` 编辑 PVT 点表（位置/速度/时间），下载调用 `PVT_Config`，启动调用 `PVT_Move`。

---

### 4.4 UI 设计方法（对齐现有代码风格）

#### 4.4.1 统一控件模式

所有新增台达 UI 控件遵循与现有 `AxisControl` 完全一致的模式：

```
┌─────────────────────────────────────────────────────────────┐
│  控件类 : XxxControl : UserControl, IUpdate                  │
│  构造函数 : XxxControl(业务对象)  →  InitializeComponent + 赋值  │
│                                                                │
│  私有字段 : 缓存当前状态（对齐 CurrentPos/CurrentIO/IsServoON）│
│                                                                │
│  UpdateStatus() : 从业务对象/原生API读取最新状态 → ShowStatus() │
│  ShowStatus()   : InvokeRequired检查 → BeginInvoke → 更新控件   │
│                                                                │
│  操作按钮 Click : ①急停检查 ②安全检查 ③Task异步(长时间操作)    │
│  点动按钮 : MouseDown启动 → MouseUp/MouseLeave停止            │
│                                                                │
│  状态表示 : Label.BackColor（绿色=正常/ON, 红色=报警/OFF,     │
│             银色=无效, 橙色=警告）                             │
└─────────────────────────────────────────────────────────────┘
```

#### 4.4.2 主窗体布局（`DeltaMainConfigForm`）

用 `TabControl` 分页签，底部统一操作按钮，对齐现有主窗体风格：

```
┌─────────────────────────────────────────────────────────────┐
│  台达 EtherCAT 配置与监控                              [×]     │
├─────────────────────────────────────────────────────────────┤
│ [连接监控] [主站配置] [从站列表] [轴配置] [回零配置] [IO映射] │
│ [电子凸轮] [PVT轨迹]                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  （各页 UserControl 内容区）                                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  配置文件: [C:\Config\Delta_Config.xml] [浏览...]            │
│  [扫描总线] [加载配置] [保存配置] [应用到设备] [确定] [取消]  │
└─────────────────────────────────────────────────────────────┘
```

#### 4.4.3 主站状态控件布局（`DeltaMasterControl`）

对齐 `AxisControl` 的横向单行布局：

```
┌──────────────────────────────────────────────────────────────────┐
│[台达主站]│卡号:0│●已连接│●WKC正常(3/3)│帧错误:0(0.000%)│    │
│ 绿色背景  │      │ 绿色    │ 绿色           │ 绿色           │    │
└──────────────────────────────────────────────────────────────────┘
```

- 轴名标签位置 → 主站名标签（绿色背景 `Color.FromArgb(146,232,154)`，对齐 `lblAxisName`）
- 位置标签位置 → 卡号显示
- IO 状态灯位置（OL/PL/NL/ALM）→ 连接状态灯/WKC状态灯/帧错误灯
- 操作按钮位置 → 扫描总线/初始化/复位

#### 4.4.4 从站列表控件布局（`DeltaSlaveListControl`）

用 `DataGridView` 展示，对齐现有 IO 配置的表格风格：

```
┌────┬──────┬──────────┬────────┬──────┬────────┬───────────┐
│序号│NodeId│ 从站名称  │ 厂商ID │产品码│ OpState│ AlarmStatus│
├────┼──────┼──────────┼────────┼──────┼────────┼───────────┤
│ 0  │  1   │ASDA-A2-E │0x01DD │0x... │  OP(3) │  正常(0)  │ ← 绿色行
│ 1  │  2   │EC系列IO  │0x01DD │0x... │  OP(3) │  正常(0)  │ ← 绿色行
│ 2  │  3   │ASDA-A3-E │0x01DD │0x... │ SafeOP │  报警(1)  │ ← 红色行
└────┴──────┴──────────┴────────┴──────┴────────┴───────────┘
```

- OpState 列用颜色标识（0=灰, 1=黄, 2=橙, 3=绿）
- AlarmStatus 非零时整行红色背景
- 双击行弹出 SDO 读写调试窗口（可选）

#### 4.4.5 配置持久化（XML）

对齐现有项目的配置管理方式，用 `XmlSerializer` 序列化配置类：

```csharp
[Serializable]
public class DeltaUIConfig
{
    public DeltaMasterConfig Master { get; set; }
    public List<DeltaAxisUIConfig> Axes { get; set; }
    public List<DeltaIOUIConfig> Inputs { get; set; }
    public List<DeltaIOUIConfig> Outputs { get; set; }
    public List<DeltaCamUIConfig> CamTables { get; set; }
    public List<DeltaPVTUIConfig> PVTTrajectories { get; set; }

    public static DeltaUIConfig Load(string path)
    {
        using (var fs = new FileStream(path, FileMode.Open))
            return (DeltaUIConfig)new XmlSerializer(typeof(DeltaUIConfig)).Deserialize(fs);
    }
    public void Save(string path)
    {
        using (var fs = new FileStream(path, FileMode.Create))
            new XmlSerializer(typeof(DeltaUIConfig)).Serialize(fs, this);
    }
}
```

#### 4.4.6 与现有控件的集成方式

现有控件（`AxisControl` / `MachineInputIO` / `CylinderControl`）**完全不变**，通过以下方式与台达集成：

```csharp
// 主窗体初始化（对齐现有模式）
private void InitMotionUI()
{
    var mgr = MotionManager.GetMotionManager();
    var ctrl = (DeltaMontionControl)mgr.MontionControl;

    // 1. 台达特有控件（新增）
    var masterCtrl = new DeltaMasterControl(ctrl);
    var monitorCtrl = new DeltaConnectionMonitor(ctrl, expectedSlaveCount: 3);
    var slaveListCtrl = new DeltaSlaveListControl(ctrl);
    topPanel.Controls.Add(masterCtrl);
    topPanel.Controls.Add(monitorCtrl);

    // 2. 现有轴控件（完全不变，厂商无关）
    foreach (var axis in mgr.GetAxes())
    {
        var axisCtrl = new AxisControl(axis.Value);  // 现有控件，不变
        axisFlowPanel.Controls.Add(axisCtrl);
    }

    // 3. 现有 IO 控件（完全不变）
    foreach (var io in mgr.GetInPutIOs())
    {
        var ioCtrl = new MachineInputIO(io.Value);   // 现有控件，不变
        ioFlowPanel.Controls.Add(ioCtrl);
    }

    // 4. 现有气缸控件（完全不变）
    foreach (var cyl in mgr.GetCylinders())
    {
        var cylCtrl = new CylinderControl(cyl.Value); // 现有控件，不变
        cylFlowPanel.Controls.Add(cylCtrl);
    }
}
```

---

### 4.5 新增 UI 文件清单与职责

| 文件 | 类型 | 职责 | 对齐现有 |
|------|------|------|----------|
| `DeltaMasterControl.cs` | UserControl+IUpdate | 主站状态显示（卡号/连接/WKC/帧错误）+ 扫描/初始化/复位按钮 | `AxisControl` |
| `DeltaSlaveListControl.cs` | UserControl+IUpdate | 从站列表 DataGridView（OpState/Alarm/设备类型） | `MachineInputIO` 集合 |
| `DeltaAxisConfigDialog.cs` | Form | 轴参数配置弹窗（脉冲当量/速度/软限位/电子齿轮） | `AxisParam` |
| `DeltaHomeConfigDialog.cs` | Form | 回零参数配置弹窗（模式/速度/偏移/方向/加速时间ms） | — |
| `DeltaCamConfigControl.cs` | UserControl | 电子凸轮表编辑（DataGridView+生成曲线+下载+啮合/脱离） | — |
| `DeltaPVTConfigControl.cs` | UserControl | PVT 轨迹编辑（DataGridView+下载+启动/停止） | — |
| `DeltaConnectionMonitor.cs` | UserControl+IUpdate | 连接监控（WKC/帧计数/周期耗时/错误日志） | — |
| `DeltaMainConfigForm.cs` | Form | 配置主窗体（TabControl 8页签+配置文件读写） | 现有主窗体 |

---

*文档版本：v1.3 | 台达 PCI-L221 EtherCAT PVT 与电子凸轮运动开发指南，新增第四部分UI层设计（对齐现有UIControl代码风格）*
