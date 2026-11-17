﻿﻿﻿﻿﻿﻿---
title: MotionControl 模块 — 运控调整
date: 2026-07-31
updated: 2026-11-02
tags: [模块, 运控, 水平移动, 模拟测试, 运动轴, 状态机, 台达, EtherCAT, CSP, 焊缝跟踪, 步骤输出, 配置包, ADR-042, ADR-079]
source: AdaWeldSystem/MotionControl/ 模块源码
---

# MotionControl 模块 — 运控调整

> **2026-09-07 控制器整体换轨**：正运动（ZMotion）全套实现**已从代码库删除**，运动控制改由**台达 PCI-L221 EtherCAT 主站卡**承接（程序不再使用任何正运动设置）。差异对照见 §控制器换轨沿革。决策记录：ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。

独立运控模块（不再挂载于 InteliWeld），负责：

1. 线激光前装标定的水平移动距离计算与缓存（`MoveControlData`）；
2. **运动控制三层架构**（`IMotion/` 抽象 + `DeltaEtherCAT/` 台达实现 + `DeltaEtherCAT/Native/` 原生封装）；
3. 业务聚合（`MontionManager` 单例 + `Cylinder` 气缸）；
4. 运控工作流（`MotionControlWorkflow`，位于 `MainDeviceControl/DeviceWorkflow/`）。

设计遵循 ADR-027 的「独立模块 + Run/Workflow 分离」范式与 [[decisions/ADR-028-MotionControlModule]]、[[decisions/ADR-027-MotionControllerDeltaReplacement]]。

## 目录结构（2026-09-07 现行）

```
MotionControl/
├── IMotion/                           ← L2 抽象层（零外部依赖）
│   ├── Type.cs                        ← ControlType/ManufacturerType/IOType/MoveMode/HomingMode/StopMode/AxisState/InterpolationType/PVTTimeMode/Ecam*
│   ├── MontionControl.cs              ← 控制器抽象基类（管理轴/IO 列表）
│   ├── MontionAxis.cs                 ← 轴抽象基类（默认实现 IPVTMotion，能力默认「不支持」；文件尾含 CspResult 返回码；`LastCommand` 虚属性默认空串）
│   ├── MontionIO.cs                   ← IO 抽象基类
│   ├── InputIO.cs / OutputIO.cs       ← 输入/输出特化
│   ├── Cylinder.cs                    ← 气缸实体（多 IO 复合，Builder 链式装配）
│   ├── IPVTMotion.cs                  ← PVT 能力契约 + PVTPoint + PVTInformation + PVTResult
│   └── InterpolationMontionParam.cs   ← 插补参数（多轴直线/圆弧/螺旋）
├── DeltaEtherCAT/                     ← L3 台达实现
│   ├── DeltaMontionControl.cs         ← 台达控制器（开卡→初始化→轮询→扫从站）
│   ├── DeltaMontionAxis.cs            ← 台达轴（CSP/CSV/CST/回零/软限位）；CST 进=模式→扭矩→开输出，出=关输出→CSP，失败 `RestoreCspMode()` 回滚（2026-11-03）；下发前查参数/伺服/回零/回读模式字（2026-11-03 现场 4609 修复）；回零模式 signed，**正负值统一走 `Home_Config`**（台达确认 Mode 为 U16，`ToHomeModeWord()` 补码强转，逻辑 -3 → 65533），`Home_Move` 前补写 P1.087/P1.088 并回读，写后 SDO 回读 16#6098 反解打印两端值（2026-11-04，ADR-080）；原 CoE 6098 下发分支已删除
│   ├── DeltaInputIO.cs / DeltaOutputIO.cs
│   ├── DeltaSlaveScanner.cs           ← 从站扫描与识别（VendorID 匹配；2026-09-15 增 WSX 焊接头 0xE0000002/0x26483052 → WeldHead_ScanCut，非轴不进 AxisRegistry）
│   ├── DeltaSlaveDevice.cs            ← 通用从站 SDO/PDO 通道（2026-09-15 新增，ADR-030 B2）：SdoRead/SdoWrite + PdoGet/PdoSet + 定标换算（INT×0.1），厂商类型收敛于此
│   ├── DeltaMotionConfig.cs           ← 配置实例类（主站/轴/输入/输出/气缸 CYLINDERS/PVT/跟踪/标定/WELD_HEAD_SLAVE 焊接头从站节/`TA_HOME` 回零参数节，XMLfile 读写）
│   ├── DeltaTaHomeConfig.cs           ← TA（送丝力矩电机）扭矩回零参数组（六参 + 默认值 + AXIS 兼容 CopyFrom/CopyTo，2026-11-04）
│   ├── DeltaAxisConfig.cs             ← 单轴配置实体（NodeId+SlotNo 寻址，无 AxisNo）
│   ├── DeltaIOConfig.cs               ← 单路 IO 配置实体（NodeId+SlotNo+BitNo）
│   ├── DeltaCylinderConfig.cs 内嵌     ← 单气缸配置实体（同文件内嵌于 DeltaMotionConfig.cs，纯名称引用 8 字段，ADR-035）
│   ├── MotionConfigImporter.cs        ← CSV 导入 / 导出器（`Import(dir, ref msg)` 三表校验后全量替换进 DeltaMotionConfig 并落盘；`Export(dir, ref msg)` 反写同表头的 4 张 CSV——轴/输入/输出/气缸，UTF-8 BOM，ADR-035）
│   ├── XlsxSheetReader.cs             ← 自研 xlsx 只读解析（2026-11-02 ADR-079）：`ZipFile` + `XDocument` 读 sharedStrings / sheet1 / mergeCells，无第三方依赖
│   ├── DeltaControllerConfigImporter.cs ← 配置文档 → 项目 XML（2026-11-02 ADR-079）：`Scan(dir)` 分级 Invalid/Partial/Ready（CSV 按表头签名、ESI 按 VendorId、xlsx 按表头特征）；`Generate(dir, out msg)` 备份后复用 `MotionConfigImporter.Import` + 写 `WELD_HEAD_SLAVE` + `WeldHeadConfig.PdoMap`
│   └── SystemConfigPackager.cs        ← 整站配置包 `.awcfg`（2026-11-02 ADR-079；2026-11-03 范围反转为 `full-settings`）：`Export/Import`，`Config/`+`DataBase/` 递归全量（仅排除 `Product.db`/`Auth.db` 与 staging）、manifest + SHA256 + `excluded`、原子替换与失败回滚
│   └── Native/                        ← L1 原生 P/Invoke
│       ├── EtherCATMasterNative.cs    ← 主站管理（Open/Initial/Reset/Close/链路健康）
│       ├── EtherCATMotionNative.cs    ← 运动（模式/使能/停止/位置速度/回零）
│       ├── EtherCATIONative.cs        ← DIO 读写（全量 + 单路）
│       ├── EtherCATAdvancedNative.cs  ← 插补/同步/龙门/TouchProbe/虚拟坐标偏移
│       ├── EtherCATMotionBufferNative.cs ← 运动缓冲（Set_Crd/Line_MultiAxis2/Start/Stop/状态/清空，2026-09-21 新增 ADR-042）
│       ├── EtherCATPVTNative.cs       ← PVT A 套（int 脉冲）+ B 套（double 流式）
│       ├── EtherCATEcam2Native.cs     ← ECAM2 建表/啮合/调整/飞剪/状态
│       └── DeltaErrorCode.cs          ← 错误码常量 + GetMessage
├── AxisRegistry.cs                    ← 轴注册表（按名登记 + 回灌进控制器）
├── IORegistry.cs                      ← IO 注册表（输入/输出分表）
├── CylinderRegistry.cs                ← 气缸注册表（把气缸占用 IO 注册进控制器）
├── MontionManager.cs                  ← 业务层单例（唯一装配点，持有三张注册表 + MoveData）
├── MoveControlData.cs                 ← 台达运控配置持有者（纯 DeltaMotionConfig holder；标定包装与水平移动缓存已删，ADR-042）
└── WeldHeadSlaveDevice.cs             ← 万顺兴焊接头从站设备（2026-09-15 ADR-014，单一实现类无抽象）：OD 读写（0x6000 温度气压/0x6010 振镜回读/0x2004 MCU 版本/0x7010 振镜写/0x7020 阈值出光）+ GalvoParams 等数据结构同文件；由 MontionManager.CreateWeldHeadFromConfig() 按配置装载
```

> **实例化链（2026-09-07）**：`MontionManager`（单例）→ `new MoveControlData()` → `new DeltaMotionConfig()`。
> 三者均为「上层持有下层实例」，`DeltaMotionConfig` 与 `MoveControlData` **不再是单例**，全系统入口只有 `MontionManager.Instance.MoveData`。

> **命名空间**：`IMotion/` → `AdaWeldSystem.MotionControl.IMotion`；`DeltaEtherCAT/` → `AdaWeldSystem.MotionControl.DeltaEtherCAT`；`Native/` → `...DeltaEtherCAT.Native`；根目录 → `AdaWeldSystem.MotionControl`。
>
> **已删除目录**：`API/`（IAxis/IIO/IMotionController/MotionControllerBase）、`ZMotion/`（10 文件）。已删除文件：`MotionManager.cs`、`MotionConfig.cs`、`IMotion/IOParam.cs`（无引用空壳）。
>
> **2026-09-07 结构调整**：`Cylinder` 实体由模块根移入 `IMotion/`（与 `MontionAxis` / `MontionIO` 同为抽象层实体），模块根新增 `AxisRegistry` / `IORegistry` / `CylinderRegistry` 三张注册表；`IPvtMotion.cs` / `PvtPoint.cs` / `PvtInformation.cs` 三文件合并为 `IPVTMotion.cs`，命名统一全大写 PVT。

## 台达 EtherCAT 运动控制（现行）

> 本模块为**全新设计**：目录结构与对外消费关系以用户提供的开发指导原档为准，决策见 [[decisions/ADR-027-MotionControllerDeltaReplacement]]。

### 三层 + 业务层依赖铁律

```
        业务层  MontionManager + AxisRegistry·IORegistry·CylinderRegistry  ← 只面向 L2 抽象
                        ↓
        L2      IMotion/  MontionControl·MontionAxis·MontionIO·InputIO·OutputIO·Cylinder
                        ↑ 零依赖（不得出现 Delta/CS_ECAT/DllImport）
        L3      DeltaEtherCAT/  DeltaMontionControl·DeltaMontionAxis·Delta*IO
                        ↓
        L1      Native/  CS_ECAT_* P/Invoke（只被 L3 调用）
```

| 铁律 | 内容 |
|------|------|
| L2 零依赖 | `IMotion/` 内不得出现厂商名、`CS_ECAT_*`、`DllImport` |
| L3 调 L1 | 原生 API 只允许在 `DeltaEtherCAT/` 内调用 |
| 业务层只认抽象 | `Delta*` 具体类型**仅**在 `MontionManager.Initialization()` 中 `new` 一次 |
| Native 不外泄 | L1 不得被业务层或 UI 直接引用 |

> 校验结果（2026-09-07 静态扫描）：L2 回流 0 处、业务层/UI 回流 0 处、厂商类型越界 0 处（仅 `MontionManager.cs:96` 一处 `new DeltaMontionControl`，属合规装配点）。

### 关键机制（易错点）

| 机制 | 说明 |
|------|------|
| **单位换算** | 台达 API 全脉冲。`Equiv` = **工程单位/脉冲**（mm/pulse）；`ToPulse(v)=v/Equiv`、`ToUnit(p)=p*Equiv`。换算**只在 L3** |
| **初始化异步** | `Master_Open` → `Master_Initial`（**每卡逐个调用，返回非 0 立即失败并上报卡号+返回码+描述**，⛔ 不再记哨兵卡号 99 后空等超时）→ 轮询 `Check_Initial_Done`（0 完成 / 1 进行中 / 99 失败），超时上限取 `FlowTimeoutSettings.Current.MasterInitSeconds`（缺省 30s，可经系统设置页「流程与设备等待超时」卡片调整）→ 再扫从站；**2026-11-13**：`Master_Open` 成功后置 `_masterOpened`，`Close()` 据此决定是否执行 `Master_Reset`+`Master_Close`（主站已开但初始化失败时也必须关闭，不跨进程残留） |
| **伺服使能** | 必须先 `Set_Move_Mode(8=CSP)`，再 `Set_Svon(1)`，然后轮询状态字 bit2（Operation Enabled），超时 3s；使能前查 bit3 报警 |
| **IO 极性** | 台达为 **NPN 低电平有效**：`SetON()` 写 **0**、`SetOFF()` 写 **1** |
| **寻址** | 四元组 `CardNo + NodeId + SlotNo + BitNo`（非正运动的手柄 + 轴号） |
| **无 Modbus** | 台达无 Modbus 通道，寄存器访问走 **PDO/SDO**（`Slave_SDO_*` / `Slave_PDO_*`） |
| **时间单位** | S 曲线时间与回零加速度为 **ms**，其余速度/加减速时间为 **s** |
| **运动前置检查** | 所有运动入口统一 `PreMotionCheck`（急停 → 总线就绪 → 报警） |
| **回零前置（2026-11-03，2026-11-04 手册修正 + 单路径）** | `StartHome` 依次：`PreMotionCheck` → 伺服已使能（否则 `NEED_SVON=0x1105`）→ `Home_Status` 不得为 1（进行中）或 3（回零错误，6041h Bit13）→ 寻找/爬行速度与加速度均 > 0 → **正负值统一 `Home_Config(Mode=(ushort)(mode&0xFFFF), Offset, FirstVel, SecondVel, Acc)` + `Home_Move`**（Offset=脉冲数、速度 rpm、加速 ms，手册 §12.1 P636；`-3 → 65533` 为台达确认的 U16 强转）→ 写后 SDO 回读 16#6098 反解打印「下发值 → 逻辑值」 |
| **CST 前置（2026-11-03，2026-11-06 加上限）** | `SetTorque` 依次：目标扭矩 ∈ ±1000 且 ≠0（0 为非法参数）→ 扭矩爬升速率 ≠0 → **按 `TorqueLimitPerMille` 钳制幅值并打印目标/上限关系（ADR-088）** → `PreMotionCheck` → 状态字 bit2（伺服就绪）/bit3（报警）→ `Home_Status≠1`（仍在回零即拒）→ `Set_MoveMode(10)` 后 `Get_MoveMode` 回读须为 10 → `CST_Start_Move` → `CST_Output_Enable(1)`；任一步失败 `RestoreCspMode()` 回 CSP。现场 `4609`（`0x1201` 接口参数错误）主要由「目标扭矩 0 / 扭矩爬升速率 0」触发 |

### TA 回零参数与 Y 轴隔离（2026-11-04）

- **XML 落点**：`ROOT/TA_HOME`（`TA_HOME_MODE/FIRST_VEL/SECOND_VEL/ACC` + `TA_HOME_ZERO_POSE_MM` + `TA_FORCE_100PCT_N` + `TA_TORQUE_LIMIT_N` + `TA_TORQUE_DIRECTION`）为 TA 专属参数的真相源；Y 轴仍读 `ROOT/AXES/AXIS[AXIS_NAME=Y向电机]` 原参数，**本轮零改动**。⚠️ `TORQUE_SLOPE` 属轴配置 `AXES/AXIS`，**不写 `TA_HOME`**（ADR-084）；反向穿越斜率 / 交接点 / 速度守卫三项配置键已随 ADR-088 删除，**工作零位速度/容差两键已随 ADR-091 删除**（老配置里的孤键读侧不消费、写侧不生成，ConfigSelfHeal 也不再生成）。
- **兼容策略**：旧文件缺 `ROOT/TA_HOME` → `LoadTaHome` 从 TA 的 AXIS 既有 `HOME_*` seed（现场参数不丢）；保存时镜像回 TA 的 AXIS 元素（仅 TA，Y 轴节点不写），保证 CSV 导入导出同值。
- **运行期**：`MontionManager.ApplyTaAxisRuntimeConfig()` 先 `ApplyAxisConfig` 再以 `TaHome` 覆盖四参；Y 轴的 `ApplyAxisConfig` 路径不变。
- **CSV**：`MotionConfigImporter` 导入后 `TaHome.CopyFrom(TA 轴行)`，避免「AXIS 改了、TA_HOME 没改」的双源漂移。
- **UI**：TA 区不在页面内散编参数；表格「参数」按钮弹共用 `AxisConfigForm`（`(DeltaAxisConfig, DeltaTaHomeConfig)` 重载），按「通用区（AXIS）+ TA 特有区（TA_HOME）」两段呈现（TA 特有区含回零/力—力矩换算/力矩输出三段，TA 共 **23 行**；力矩输出段只有「扭矩爬升速率 `TORQUE_SLOPE`」与「扭矩上限 `TA_TORQUE_LIMIT_N`」两行；「工作零位」三分区与「软限位模式」行已于 **ADR-091** 删除，`PositiveLimit`/`NegativeLimit` 两行保留）；Y 轴仍走单参构造（19 行，行序/校验不变）；保存统一走 `SaveTaHomeConfig()`（落盘 + 推回运行期；P1 下发已删），生效时机 = 下次回零。
- **扭矩输出四项（ADR-084 / ADR-088 / ADR-088）**：力的大小（工艺 INI `TA_FORCE_N`，非负）/ 方向（`TA_HOME/TA_TORQUE_DIRECTION`，±1）/ **扭矩爬升速率**（`AXES/AXIS/TORQUE_SLOPE`，1~65535，正反向共用唯一值）/ **扭矩上限**（`TA_HOME/TA_TORQUE_LIMIT_N`，N，缺省 = 100% 力量基准即不降额）。⛔ 无第二套斜率参数。
- **单一夹子（ADR-088）**：`DeltaTaHomeConfig.GetTorqueLimitPerMille()` 是**唯一换算点**（上限 N ÷ `TA_FORCE_100PCT_N` × 1000，1~1000）；`MontionManager` 装载/运行期更新时写入 `DeltaMontionAxis.TorqueLimitPerMille`；CST 目标在 `SetTorque` 唯一下发点钳制，驱动侧在伺服 OFF 窗口写 `16#6072`（Max torque）使位置模式推动阻抗同值；该上限**运行期不可靠改写**（手册未收录，ADR-088 取定值路线），改上限后需重新使能伺服才作用于位置模式，CST 软件钳制即时生效。
- **行程边界扫描已删除（ADR-091）**：`DeviceStatusWork.ScanTaPositionLimit`（越限即 `StopTorque()` 撤力 + `ReportAlarm`）**整段移除** ——
  业主判定「锁不住位置，且会在焊接关键时刻退出力矩模式」。`POSITIVE_LIMIT` / `NEGATIVE_LIMIT` 键与 CSV 列**保留**（仅运行期不再有越限撤力行为），
  `SOFT_LIMIT_MODE` 键同样保留（CSV 往返需要），仅弹窗「软限位模式」设置行删除。⛔ 力矩模式下压不再被边界打断。
- **装载链路**：`CreateAxesFromConfig` 逐轴 `ApplyAxisConfig` → `ApplyTaHomeOnLoad()` 仅对 `TA_AXIS_NAME` 命中轴覆盖回零四参（日志打印四值）；Y 轴不命中、读取路径零改动；缺 `TA_HOME` 时 startup 覆盖值等于 AXIS seed/镜像值。

### 注册表机制（2026-09-07 新增）

模块根的三张注册表取代原先 `MontionManager` 内部四个裸字典，职责是「按名登记 + 保证已注册进控制器」。

```
业务代码 ──AddAxis(name,axis)──→ MontionManager ──→ AxisRegistry.Register()
                                                 └→ MontionControl.AddAxis(axis)   ← 真正进控制器
                                                        （Initialization 后再 AttachAll 幂等回灌）

                                AddCylinder ──→ CylinderRegistry.Register()
                                              └→ 逐个 cylinder.GetAllIO() → MontionControl.AddIO()
```

| 注册表 | 承载 | 关键成员 |
|--------|------|----------|
| `AxisRegistry` | `Dictionary<string, MontionAxis>` | `Register` / `Get` / `GetAll` / `GetNames` / `Count` / `AttachAll(control)` |
| `IORegistry` | 输入、输出**分表**存放（键名空间独立，允许同名） | `RegisterInput` / `GetInput` / `RegisterOutput` / `GetOutput` / `InputCount` / `OutputCount` / `AttachAll` |
| `CylinderRegistry` | `Dictionary<string, Cylinder>` | `Register` / `Get` / `GetAll` / `Count` / `AttachAll`（把气缸占用的全部 IO 注册进控制器） |

要点：

- `MontionAxis` / `MontionIO` 构造时已向所属控制器**自注册**（`container.AddAxis(this)` / `AddIO(this)`），`AttachAll` 是幂等回灌，用于校验注册表与控制器集合一致。
- 气缸是**多 IO 复合体**（2 输入 + 2 输出 + 可选中间位），`Cylinder.GetAllIO()` 是新增的枚举入口，`CylinderRegistry.AttachAll` 靠它一次性登记，避免逐个手工 `AddIO`。
- `MontionManager` 对外 API（`AddAxis` / `GetAxis` / `AddInputIO` / `GetInputIO` / `AddOutputIO` / `GetOutputIO` / `AddCylinder` / `GetCylinder`）**名字与签名不变**，消费方零改动。
- 三张注册表以属性暴露：`MontionManager.Instance.{Axes / IOs / Cylinders}`。

### PVT 能力契约（2026-09-07）

`IMotion/IPVTMotion.cs` 一个文件承载四件事，命名统一全大写 PVT（与台达 SDK 一致）：

| 成员 | 说明 |
|------|------|
| `interface IPVTMotion` | `BeginMove` / `ContinueMove` / `GetInformation` / `CycleStart` |
| `struct PVTPoint` | `Pos` / `Time` / `Vel`，工程单位 + 秒 |
| `struct PVTInformation` | `TotalCount` / `DoneCount` / `RemainBufferSize` / `Status` / `RemainCount` |
| `static class PVTResult` | `OK = 0` / `NotSupported = 0xFFFF` |

`MontionAxis` 默认实现 `IPVTMotion`，四个入口均为 `virtual` 且返回 `PVTResult.NotSupported` + 一条告警日志；具备该能力的厂商轴（台达）重写即可，**未重写不影响编译**。
调用前置条件：轴已切 **CSP 模式**且伺服使能，接口本身不负责模式切换。

### ~~CSP 能力契约~~（⛔ 2026-09-21 删除，ADR-042 首跑后用户裁定清库）

~~`IMotion/ICspMotion.cs`（`SetCspTargetPosition` / `SetCspSoftLimit` / `MontionAxis` 三个 virtual / `ChangeTargetPosition` / `CS_ECAT_Slave_CSP_TargetPos_Change`）~~ **全部删除**——607A 逐拍改目标实测写入不生效（原点平移 + 目标不生效双问题），由**运动缓冲流式段写入**取代（见上文运动缓冲 Native 与 `DeltaMontionAxis#region 运动缓冲`）。`static class CspResult`（`OK=0`/`NotSupported`）迁至 `MontionAxis.cs` 文件尾，供缓冲流式返回码判定沿用；`CS_ECAT_Slave_CSP_Start_Move`（普通点位 AbsMove 用）**保留**；`CS_ECAT_Slave_CSP_Set_Softlimit`（原普通软限位 `SetSoftLimit` 用）随 0 调用一并删除。

> **热路径纪律（ADR-007 / ADR-042 / ADR-042）**：缓冲段写入在**流程节拍**上调用——运行态基线 **10ms/100Hz**
>（节拍来源见 [[modules/DeviceControl]] 模组线程 `SubDeviceWork`）；
> 错误由调用方 [[api/MotionControlWorkflow]] 以「**同错误码 1s 限频**」记录，避免刷屏。

### 轴反馈文本上提（2026-09-22 精简）

`MontionAxis` 新增 `public virtual string LastCommand { get { return string.Empty; } }`，`DeltaMontionAxis` 改为 `public override string LastCommand` 返回 `_lastCommand`（台达轴原属性签名不变）。**目的**：UI（[[api/SystemControlPage]]）读轴反馈列不再写 `(axis as DeltaMontionAxis)?.LastCommand`——业务层不做运行时类型判断，能力经基类虚属性统一暴露（ADR-006：模块与对象调用关系明确）。全库轴对象创建点仍唯一（`MontionManager` 内 `new DeltaMontionAxis`），流程层只经 `MontionManager.GetAxis` / `GetDeltaAxis` 取轴。

### 消费方（模块外引用点）

| 消费方 | 引用形式 |
|--------|----------|
| `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` | `MontionManager.Instance.{Initialization/Close/ServoOnAll/ServoOffAll/SetEmergencyStop}` + `MontionControl.GetAxes()`；CSP 模式下经 `MontionControl.EmergencyStop` 做**按拍**急停判定（ADR-042） |
| `MainDeviceControl/DeviceControlWork.cs` | `private MontionManager Motion`（L193）+ `Motion = MontionManager.Instance`（L367） |
| `WeldParamControl/WeldParamManager.cs` | ⛔ 不直接引用运控类型——CSP 目标值经 `TryGetSeamTrackingCorrectionMm` 暴露，写轴由 `MotionControlWorkflow` 承担 |
| `UIDesign/TabPage/SystemControlPage.cs` | 只用 `MotionControlWorkflow.Instance.{Start/Stop/WeldStatus}`，**不接触运控类型** |

### 部署依赖

- **原生 DLL**：`3rdDepend\EtherCAT_DLL_x64.dll`（161 MB，来自台达 SDK `dll/` 目录）
- **平台目标**：`PlatformTarget=x64`（**禁 AnyCPU**——x86 版库名为 `EtherCAT_DLL.dll`，本项目按 x64 构建）
- **构建拷贝**：`CopyNative3rdDependToOutput` 目标在构建后拷至输出目录
- **已移除**：`zauxdll.dll` / `zmotion.dll` / `ZmotionScanLaser.dll`

### 相关页面

- **完整规范**：[[guides/DeltaEtherCAT-DevGuide]]（目录结构、对外消费契约、初始化序列、单位换算、示例、API 核验门禁、落地清单）
- **原生 API 速查**：[[api/DeltaEtherCAT-Native]]（832 个 API，签名由 SDK 头文件 `inc/C#/EtherCAT_DLL.cs` 逐字抽取核验）
- **业务层入口**：[[api/MontionManager]]
- **雷赛参考基线**：[[api/LeadshineLSnmc-Reference]]
- **原档归档**：`raw/delta/运动控制模块开发文档_台达版.md`

- **TA 出力协议：CST 力矩模式（2026-11-06 收口，ADR-088）**：`DeltaMontionAxis.SetTorque(short targetTorque, uint slope)` 冷启动（输出关或非 CST）必须
  「位置运动停稳（`IsMoving` 轮询，3s 超时即拒绝）→ `Set_MoveMode(CST)` 回读确认 → `CST_Start_Move(±1‰ 方向种子)`
  → `CST_Output_Enable(1)` → `CST_Start_Move(目标, slope)`」；热切换（输出开且 CST）直接重发目标与 slope。
  ⛔ 不设「参数未变即跳过」的复用捷径；⛔ 目标不得在输出关闭时下发（开输出会直接到目标值，绕过 `TORQUE_SLOPE`）。
  方向种子与目标同号，用于覆盖驱动器内残留的反向扭矩指令。**正反向共用唯一斜率 `TORQUE_SLOPE`**，
  两段式/交接点/速度守卫已删除（ADR-088 废弃）。
  `MotionControlWorkflow.SetTaTorque` / `StopTaTorque`（2026-11-09 自 `MontionManager.SetWireFeedTorque` 迁入，送丝即 TA）与 `TaTorque`（Auto/Retract 两支）均只传目标与斜率。
  ⛔ **CST 无速度上限**：`CST_Start_Move` 原生签名无速度形参，全库也从未写 `0x607F` / `0x6080`；
  135‰ 即可把轴推到 439mm/s（定位速度 10mm/s）→ 撞机械限位 → 反弹撞另一头。**此问题尚未闭合**，见 ADR-088。

- **扭矩上限单一夹子（2026-11-06，ADR-088）**：位置模式推动阻抗与 CST 力矩模式最大出力共用
  `ROOT/TA_HOME/TA_TORQUE_LIMIT_N`（N，缺省 = 100% 力量基准）。软件侧 `SetTorque` 在唯一下发点按
  `DeltaMontionAxis.TorqueLimitPerMille` 钳制目标；驱动侧 `ServoOn` 在 `Set_MoveMode` **之前**、伺服 OFF 窗口调
  `EnsureDriveTorqueLimit()`，**每次使能重试一次**（轮次计数进日志）：①基线读 `16#6041` 状态字，确认函数/长度/字节序/Done 时序；
  ②`16#6072` 只读探测 SubIndex 0 与 1，读通哪个才写哪个并回读；③失败只告警不阻断使能。
  **通道唯一**：写与回读都走 `DeltaSlaveDevice.ReadSdo/WriteSdo`（与 `16#6098/6099/609A` 及其它对象字典读写同一套握手：
  前置 10ms → `SDO_Check_Done` 轮询 → `SDO_Get_ErrorCode` 取中止码 → 邮箱类返回码 30ms 退避重试 3 次）。
  ⛔ 台达 P 参数旁路 `P1-12`（`0x210C`）**已删除**：映射未经手册证实，且其「子索引填轴号」与标准对象通道的
  「子索引 = 对象子索引」（`16#6099` 1/2 = 高低速即证）是两套约定，混用会读错对象。
  ⛔ 日志必须区分「本层 API 返回码」与「驱动器 SDO 中止码」：`0x1305`（=4869）是台达 DLL 返回码、表内未收录，
  与 P1.087/P1.088 失败同码，**不能**当成「对象未实现」；基线读失败时禁止对 0x6072 下结论。
  日志分四态：`CST 扭矩上限钳制`（目标超上限）/`已贴边`（目标 = 上限）/`余量仅 x%`（≤10%）/`有余量`。
  ⛔ `被钳制 ≠ 已出力`：驱动器仍需按 `TORQUE_SLOPE` 从当前扭矩爬升。

> **边界（2026-10-08 ADR-030 补正 / 2026-10-09 ADR-057 更新）**：振镜与 LA 对焦**归焊接头从站设备**（`WeldHeadSlaveDevice`，本模块内）——LA 走 `0x7000`/`0x6020` 电机对象（`SetMotorPosEnable`/`ReadMotorStatus`/`StopMotor` + `MotorPulsePerMm` 量纲单一入口；⛔ 原 `SetAutoFocusPosition`/`AutoFocusExecutor` 已删），振镜接口 `SetGalvoParams`/`ReadGalvoParams`。**TA/LA 动作与随动**（TA auto=`SetTorque` 下压力 / break=`StopTorque` 锁止 / Pose；LA auto=曲线B 随动 / Spot=曲线A 反查 / Pose）由 `LaserWeldHeadWorkflow` 消费（[[decisions/ADR-057-TaLaActionAndFollowControl]]）；~~TA 位置上下限报警归 `DeviceStatusWork.ScanTaPositionLimit`~~ **2026-11-06 整段删除（ADR-091）**。

## MoveControlData（台达运控配置持有者，ADR-042）

> **2026-09-17 重写（ADR-042）**：230 → 85 行，类收敛为**纯 `DeltaMotionConfig` 持有者**——水平移动缓存子系统（5 方法 + 2 字段）与全部标定包装属性（含私有 `CalibConfig`）**已从代码删除**；标定 / 几何 / 安装参数一律经 `WeldParamManager.Instance.AlgorithmsConfig` 读取（数据源唯一化）。

- 持有 `DeltaMotionConfig MotionConfig`（`Axes` 轴表 / `Inputs` 输入表 / `Outputs` 输出表 / `Cylinders` 气缸表 / PVT 段 / 跟踪段(`ROOT/SEAM_TRACK`，焊缝跟踪轴名 `SeamTrackAxisName`，ADR-033) / `WeldHeadSlave` 焊接头从站节），**注册的轴与 IO 的配置均从此对象读取**。
- 剩余 API 仅：`MotionConfig` 属性 / 构造函数 / `Load()` / `Save()`。

> **CSV 导入 / 导出通道（2026-09-16，ADR-035）**：`MotionConfigImporter.Import(dir, ref msg)` 解析电气填写的 `轴配置表.csv` / `IO配置表.csv` / `气缸配置表.csv`（UTF-8 BOM，模板沉淀于工作区 `轴IO气缸配置模板/`），校验通过后**全量替换**四表并 `SaveConfig()` 落盘，任一失败零写入；气缸表按 IO_NAME 引用 IO 表。`MontionManager.CreateCylindersFromConfig` 在 Initialization 中按名装配气缸，缺引用告警跳过。
>
> **导出同轮补齐**：`MotionConfigImporter.Export(dir, ref msg)` 按**与 Import 侧逐字一致的表头**反写 4 张 CSV（`轴配置表.csv` / `IO配置表.csv` 含输入+输出两段 / `气缸配置表.csv`），导出文件可**原样回导入**（双向闭环）；私有区新增 `CsvField`（含逗号/引号/换行时双引号包裹转义）、`CsvBool`（TRUE/FALSE）、`CsvDouble`（固定 `InvariantCulture`）、`WriteCsv`（`File.WriteAllLines` + `new UTF8Encoding(true)` 带 BOM）。UI 入口见 [[api/SystemControlPage]]（`MontionConfigForm` 已于 2026-09-17 删除，运控配置整体迁入 SystemControlPage；导入导出区后迁至 FilebackupPage）。
- **焊接头从站节（2026-09-15 ADR-030 B1）**：`WeldHeadSlave`（NodeId / Enabled / VendorId 0xE0000002 / ProductCode 0x26483052 / RevisionNo，hex 读写），`ROOT/WELD_HEAD_SLAVE` 节；`MontionManager.CreateWeldHeadFromConfig()` 从此取 CardNo + NodeId 建 `WeldHeadSlaveDevice`（ADR-014，原 `WeldHeadManager` 已删除）。
- **本地持久化（2026-09-20 按 ADR-033 三段式落位，2026-09-21 复正）**：`Load()`/`Save()` 委托 `MotionConfig.LoadConfig()` / `SaveConfig()`，读写 `Config\MotionControl\Motion_XML\DeltaMotionConfig.xml`；历史平铺路径的搬迁自 2026-09-21 起统一由 `FileOperate/ConfigPathMigrator.cs`（`Program.Main` 首步）承担，原 `MontionManager.MigrateLegacyControllerXml()` 已删除。`Load` 在 `MontionManager` 构造时自动执行（日志「运控配置已加载」），原 `Config/INI/MoveControlData.ini` 已弃用。同轮焊接头配置落 `Config\MotionControl\WeldHead_XML\WeldHeadSlave.xml`（独立文件保留）。`DeltaMotionConfig.xml` 2026-09-20 新增 `ROOT/SEAM_TRACK` 功能段（焊缝跟踪轴名 `SeamTrackAxisName`，与 PVT 平级、不属 PVT）。
- 访问路径：`MontionManager.Instance.MoveData`（`MoveControlData.Instance` 已移除）。
- ⛔ **已删除（2026-09-17，ADR-042）**：标定包装属性（`LaserFrontOffset` / `LaserToHorizontalAngleRad` / `LaserToHorizontalAngleDeg` / `LaserToHorizontalScaleX` / `CalibratedCenterX` / `CalibratedCenterY` / `ApproachThreshold`）；水平移动缓存子系统 `ComputeHorizontalMove` / `CacheHorizontalMove` / `TryGetNearestHorizontalMove` / `RemoveHorizontalMove` / `ClearHorizontalMoveCache`（含 `ComputeAndCacheHorizontalMove` 组合入口）；标定控件不再写入本类——改由 [[modules/UIDesign]] 的 `ProcessControlPage`「线激光」段经 `WeldParamManager.AlgorithmsConfig` 读写。

> 易误判点：`MoveControlData` 现仅为**台达运控配置持有者**，**不再**承载标定参数或水平移动缓存（ADR-042）。

### 配置文档 → 项目 XML（2026-11-02 ADR-079）

> 入口在 [[api/FilebackupPage]] 的系统配置文件页；本模块只提供解析与落盘能力。模板沉淀于工作区 `轴IO气缸配置模板/`（实为 6 个文件）。

| 来源文件 | 识别特征（内容优先） | 落点 |
|---|---|---|
| `轴配置表.csv` | 表头含 `AXIS_NAME` | `DeltaMotionConfig.xml` → `ROOT/AXES` |
| `IO配置表.csv` | 表头含 `IO_TYPE` | `ROOT/INPUTS` + `ROOT/OUTPUTS` |
| `气缸配置表.csv` | 表头含 `CYLINDER_NAME` | `ROOT/CYLINDERS` |
| `Wsx_ScanCut.xml`（ESI） | 结构判据：`EtherCATInfo/Vendor/Id` 存在 + `Device/Type` 带 `ProductCode`；`Device/Name` 为从站名 | **台达从站配置文档**：`ROOT/WELD_HEAD_SLAVE` 的 `VENDOR_ID` / `PRODUCT_CODE` / `REVISION_NO` |
| `EtherCAT协议.xlsx` | 表头含 `变量` + `SDO Index` + `PDO Index` | `WeldHeadSlave.xml` → `ROOT/IO_MAP/IO`（唯一权威源） |

- **分级**：`Invalid`（无任何可识别文档）/ `Partial`（缺文件或表头不符，仅预览）/ `Ready`（三表 + ESI + IO 表齐备）；ESI 存在即「台达从站」就绪，缺失清单只含三张 CSV 与焊接头 IO 表。
- **按节替换**：CSV 仍走 `MotionConfigImporter.Import`（`AXES/INPUTS/OUTPUTS/CYLINDERS` 整节替换），`MASTER` / `SEAM_TRACK` / `TA` / `PVT` / `WELD_HEAD_SLAVE` 保留；旧 CSV 行为不变。
- **写前备份**：`FileOperate/ConfigBackupHelper` 把 `DeltaMotionConfig.xml` + `WeldHeadSlave.xml` 复制到 `Config\_backup\<yyyyMMdd_HHmmss>\`；备份或解析失败即零写入。
- **焊接头结构**：`WeldHeadSlave.xml` 的 `ROOT/THRESHOLD`（温压阈值）、`ROOT/GALVO`（默认振镜）、`ROOT/MOTOR/PULSE_PER_MM`，本条新增 `ROOT/IO_MAP/IO`（每行 10 属性 `SEQ/VAR/NAME/TYPE/SDO_INDEX/SDO_SUB/ACCESS/PDO_INDEX/PDO_SUB/DESC`），读写仍唯一走 `MontionManager.SaveWeldHeadConfig()/LoadWeldHeadConfig()`。
- **xlsx 事实**：sheet 仅「扫描切」有数据；表头 10 列 `序号|变量|名称|数据类型|SDO Index|SDO SubIndex|Access|PDO Index|PDO SubIndex|说明`；59 行 = 1 表头 + 58 数据（56 条含 PDO + 2 条仅 SDO `0x2004`）。
- **权威源规则**：`EtherCAT协议.xlsx` 为唯一权威源（供应商参考文档，内容随版本可变）；行数、列值、SDO/PDO 索引全部来自表，代码不硬编码 PDO 清单与 SubIndex。ESI 仅交叉校验（对象地址缺失/变量名不一致/PDO 位置错位），只写 `Warning` 不回写。
- **可追溯**：生成时把 IO 表 `SOURCE_FILE` / `SOURCE_TIME` / `ROW_COUNT` 写入 `IO_MAP` 属性并记日志。
- **台达从站**：ESI 即台达从站配置文档（主站下挂各轴 + 唯一额外从站焊接头）；身份字段供 `ROOT/WELD_HEAD_SLAVE` 生成与焊接头视图使用。`NODE_ID` 不在 ESI 中，取 `WELD_HEAD_SLAVE/NODE_ID`（子元素），取不到或为 0 标「待填」，生成沿用旧值。2026-11-03 起不再单列「台达从站」视图（与焊接头从站重复）。

## MotionControlWorkflow（位于 `MainDeviceControl/DeviceWorkflow/`）

> ⚠️ **2026-07-20 架构纠正**：`MotionControlWorkflow` **不再持有独立模拟线程**。模拟模式（共享 robotX / A·B·C 模式 / 参数）统一由 [[api/DeviceControlWork]] 提供；本工作流仅：① 水平移动后台线程消费 `MoveControlData` 缓存；② 订阅 `PipelineManager.AlgorithmCompleted` 将线激光每帧焊缝特征缓存为水平移动距离。
> ⛔ **沿革**：① 所述水平移动缓存已于 2026-09-17 随 ADR-042 删除；② 的 `PipelineManager` 链路已随 ADR-007 删除——本段仅存历史。CSP 起焊种子现取 `WeldParamManager.Instance.AlgorithmsConfig.TeachLockYMm`（示教 Y 轴锁定坐标）。

- **状态模型（ADR-034 三态）**：连接态 `SubDeviceState` 与焊接过程态 `SubDeviceWeldStatus` 由基类 `DeviceStateBase` 承载，状态写入唯一入口为 `SetState`/`SetWeldStatus`，禁手工赋值。
- **初始化顺序与连接态判定（2026-11-03，ADR-014 演进 D3）**：`MontionManager.Initialization` 顺序固定为「配置加载 → 主站开卡 → 主站初始化 → 扫从站 → 按配置建轴/IO/气缸/焊接头 → `IsInitialized=true` → `AttachAll`」；配置先于连接是必要前置（卡号/轴表来自配置）。初始化跑在 IO 工作线程，**`IsInitialized` 在整段完成前恒为 false**，UI 必须等到初始化结束回调或连接态切换后再判定「未连接」。
- **2026-09-07 换轨改造**：删除全部 `ZMotion` 依赖（`CamBoxTracker` / `EncoderAxis` / `RSIPositionBuffer` / `InterpolationEngine`），私有阶段枚举改名 **`MotionControlPhase`**（`Idle` / `Initializing` / `Ready` / `Stopping` / `Error`），执行步位 `StepServoOn=10` / `StepReturnToCal=15`（2026-09-21 ADR-042 新增：PreWork 跟踪轴回归 Y 轴标定位）/ `StepReady=20` / `StepStopping=700`；初始化入口改为 `MontionManager.Instance.Initialization("台达运控", ref msg)`。
- **对外契约不变**：`Instance` / `Start()` / `Stop(bool)` / `IsRunning` / `WeldStatus` / `StateName`。
- **2026-09-16 CSP 步骤输出（ADR-042 → ADR-042 → **2026-09-21 ADR-042 缓冲流式**）**：CSP 段写入**就地落在 `FlowProcess` 的 CSP 分支内按拍推进**，**不自起线程**（原 `CspOutputLoop()` 1ms 后台线程已删除）——
  起焊沿 `StartCspOutput()` 建运动缓冲坐标系 + 复位段队列（`_cspLastQueuedPos = axis.GetPosition()`），
  每拍由私有 `OutputCspTick()` 读 `WeldParamManager.Instance.TryGetSeamTrackingCorrectionMm` 并按水位写 `BufferLineTo`、攒满预载即 `BufferStart`（详见 [[api/MotionControlWorkflow]]）；
  节拍由编排层模组线程决定（运行态 10ms/100Hz），`TakeCspElapsedSeconds()` 实测两拍间隔（两端钳位 `[0.001, 0.1]s`）供限幅器折算量纲。
  输出侧三段整形：速度限幅 `MaxVelMmPerS`(50mm/s) → 加速度限幅 `MaxAccMmPerS2`(500mm/s²) → 防过冲（差值 < 0.02mm 时速度减半并贴齐）。
  **急停双保险**：`SubDeviceWork` 的 `Current != Running` 门控使急停后不再调 `FlowProcess`，`OutputCspTick()` 内仍保留 `IsEmergencyStop()` 判据（置位即停写目标，避免在驱动器停机后重新驱动轴）。
  起焊沿顺序固定为 `ResetSeamTracking()` → `SeedSeamTrackingYAxisTarget(轴位置)` → 速度归零 → `StartCspOutput()`；
  停焊沿 `StopCspOutput()` 清除启用标志并配对归还定时器精度（`timeEndPeriod(1)`）。
- **跨线程不推进执行步（ADR-042）**：RSI 线程触发的折返报警**不直接**调 `Fail()`，只置 `volatile _seamAlarmPending`；
  由流程线程在 `UpdateSeamTracking()` 内 `Fail(...)`——保证状态单次转换，规避并发双转换。
- 资源释放：非 UI 类统一标准 `IDisposable.Dispose()`（ADR-002（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）），**禁 `DisposeComponents()`**（仅限 UI 设计器类）。

## 模拟测试（沿革）

> ⛔ **A/B/C 模式已取消（2026-09-17 ADR-032）**：`SimTestMode` 枚举与 `VirtualCameraRun` / `CameraRun` 类型均已删除；现行 = 单一开关 + 按设备连接态自动分支（线激光未连接→虚拟相机；运控未连接→只记录轨迹不写轴）。现行设计见 [[lessons/SimulationAutoBranching]] / [[decisions/ADR-032-SimulationTestRedesign]]。下表仅存史。

| 模式 | 相机 | 计算 | 记录 | 运动执行 |
|------|------|------|------|----------|
| ~~A~~ | ~~虚拟调试相机（`VirtualCameraRun`）~~ | ✅ | ✅ | ❌ |
| ~~B~~ | ~~虚拟调试相机~~ | ✅ | ✅ | ✅（~~`MontionManager.GetAxis("水平轴").AbsMove`~~） |
| ~~C~~ | ~~真实相机（`CameraRun`）~~ | ✅ | ✅ | ❌ |

## 控制器换轨沿革（2026-09-07）

> 2026-09-07 起运动控制**仅使用台达 PCI-L221 EtherCAT 主站**；此前基于正运动（ZMotion）的实现及其知识页已全部删除，详见 ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。

| 维度 | 正运动（已移除） | 台达（现行） |
|---|---|---|
| 连接 | 以太网 + 句柄 | PCI 主站卡（`CardNo` + `NodeId` + `SlotNo` + `BitNo`） |
| 初始化 | 同步 | **异步**：`Master_Initial` 后轮询 `Check_Initial_Done`(0/1/99) |
| 使能 | 直接使能 | 先 `Set_Move_Mode(8=CSP)`，再 `Set_Svon(1)`，轮询状态字 bit2 |
| IO 电平 | — | **NPN 低电平有效**（`SetON` 写 0） |
| 配置 | `MotionConfig`（IP/心跳/BAS/CAMBOX/ATYPE25） | 无独立配置文件（OPEN） |
| 振镜 / 对焦 | 占用 2 个轴 | 归焊接头（ADR-033 D5） |
| 心跳 / BAS 保护 | 应用层心跳 + BAS | **无**（WKC 看门狗由主站卡硬件维护，见 [[guides/DeltaEtherCAT-UIDesign]] §2） |
| 焊缝跟踪 | CAMBOX（ATYPE=25 通讯编码器主轴 AXIS8 + 从轴 AXIS0） | **方案未定（OPEN）**，见下节 |

## 高级运动能力（PVT / 电子凸轮）

> 完整规范见 [[guides/DeltaEtherCAT-AdvancedMotion]]；UI 见 [[guides/DeltaEtherCAT-UIDesign]]。

**PVT 多段插值**：A 套（`PVT_Move` / `PVTComplete_*` / `PVT_Config` / `PVT_Sync_Move` / `PVT_Get_NowMotCount`，int 脉冲，上限 **8000** 点）+ B 套（`PVT_Begin_Move` / `PVT_Continue_Move` / `PVT_CycleStart` / `PVT_Get_Information`，double 工程单位、**可流式续喂**、带 `RemainBufSize` 水位）。

**电子凸轮**：ECAM2 为首选（`Profile_Data` 建表 / `Profile_CamIn` 啮合 / `Profile_Modify` 改点 / `Phasing` 相位 / `Get_PreviewTable` 试算）；ECAM 一代仅兼容保留。
⚠️ **主轴来源 `SourceType` 只有 0（真实从站）与 1（轴卡板载脉冲输入）两个值——不存在「虚拟轴」**，台达的 `Virtual_Set_Enable/Command` 是坐标平移功能而非虚拟主轴。

**焊缝跟踪（机器人 X → Y 轴纠偏）方案裁决**：

| 方案 | 可行性 |
|---|---|
| ECAM2 + 虚拟轴主轴（二手文档推荐 ⭐⭐⭐⭐⭐） | ⛔ **不成立**：无虚拟轴 API、`SourceType=2` 不存在 |
| ECAM2 + 板载脉冲输入（`SourceType=1`） | ⚠️ 取决于现场是否有脉冲/编码器硬件信号 |
| PVT 实时点序列（B 套流式） | **2026-09-16 起降为备用模式**（`TRACKING_MODE = PvtStream`）。⚠️ **接线状态（2026-09-17 审计复核）**：上层消费在（`MotionControlWorkflow` PvtStream 分支调 `BeginMove`/`ContinueMove`）+ 配置链（`DeltaMotionConfig` PVT 节）+ `EtherCATPVTNative` A/B 套 DllImport 封装均就绪，**但 `DeltaMontionAxis` 尚未 override PVT 四入口**——现切 PvtStream 会落基类默认 `PVTResult.NotSupported` 告警；补接线 = 台达轴重写四入口对接 B 套流式入口（`EtherCATPVTNative` 非死代码，勿再列为清理候选） |
| **CSP 周期同步位置** | ✅ **现行默认（ADR-042）**：上位机按流程节拍（10ms/100Hz）逐拍写目标位置，驱动器内部插补 |

> **2026-09-16 换轨理由（ADR-042）**：PVT 把时间轴交给控制器——点表**一经预下载无法回撤**，
> 局部修正量与机器人位姿是实时变化的，只能等水位排空才生效，形成**结构性滞后**；
> CSP 把插补交给驱动器，上位机只给**目标位置**，可随时改写。代价是平滑度依赖上位机节拍，
> 故在输出侧加「速度 → 加速度 → 防过冲」三段整形，并以**实测 dt**（`TakeCspElapsedSeconds()`）折算限幅量纲，
> 使整形结果对调度抖动自适应；定时器精度 `timeBeginPeriod(1)` 保留，改为**起焊沿调用**、停焊沿配对归还。
> **双模式并存**：PVT 参数与链路原样保留，`SEAM_GUIDE/TRACKING_MODE` 开关切换，现场可回退。
> 详见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]、ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）。

X 坐标来源：`Comm/Communication/Implementations/KukaRsiComm.cs`（RSI UDP 12ms / IPO_FAST 4ms）+ `KukaEkiComm.cs`。
正运动删除后遗留的 **RSI 位置时序缓冲（`RSIPositionBuffer`）位姿上行继任者已落地**——
[[modules/Comm]] 在 `RsiComm_DataReceived` 开头调 `UpdateRobotPose(e)`，把最新位姿落为
**加锁快照 `RobotPoseSnapshot`（X/Y/Z/Timestamp，只读值对象，防 double 撕裂读）**，经
`HasRobotPose` / `TryGetRobotPose(out pose)` 对外暴露；[[api/WeldParamManager]] 订阅 `RobotDataReceived` 消费，
**不另存副本**（位姿单一真相源在通讯层，ADR-042）。

**能力现状**：`Native/EtherCATAdvancedNative.cs` 现仅 16 个 extern（ECAM2 覆盖 4、PVT 覆盖 2），落地前需补约 32 个声明（清单见规范页 §6）。
CSP ~~目标位置写入不依赖该文件——走 `Native/EtherCATMotionNative.cs` 的 `CS_ECAT_Slave_CSP_TargetPos_Change` / `CS_ECAT_Slave_CSP_Set_Softlimit`~~（⚠️ **2026-09-21 ADR-042 演进**：607A 逐拍改目标实测不生效废止；`CSP_Set_Softlimit` 2026-11-09 随 0 调用删除；CSP 现走 `Native/EtherCATMotionBufferNative.cs`（2026-09-21 新增，Set_Crd/Line_MultiAxis2/Start/Stop/状态/清空 8 个 extern）+ `DeltaMontionAxis` 的 `#region 运动缓冲` 单轴封装；`SetCspTargetPosition`/`StartCspMove` 契约保留但工作流不再调用）。

## 已知问题（模拟测试，2026-09-20 / [[decisions/ADR-039-SimulationTestAutoTerminationAndRecordCacheRelease]]）

- **模拟须自动终止**：行程到程（`CheckWeldProgress`）须调 `DisableSimulation()` 停 robotX 时钟；`SimScheduleTick()` 顶部须守卫模组 `ErrorAborted` / 整机 `Alarm`/`EStop`，否则模拟持续跑（[[lessons/SimulationAutoBranching]] 陷阱九/十三）。
- **CSP 轨迹记录依赖真实轴**：`SeamTrackAxisName` 必须落在 `DeltaMotionConfig.xml` 实际轴名集合（`Y向电机`），否则 `UpdateSeamTracking()` 早退、轨迹点零产出（[[lessons/SimulationAutoBranching]] 陷阱十）。
- **CSP 输出整形器不得自锁**（[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]）：限幅/整形环节的残差必须取「跟随器位置 → 目标」；取「本拍输出 → 目标」会在加速度限幅不生效时恒为 0 ⇒ 速度清零、命令冻结（实测写段占空比 7.3%、轴停走）。跟随器另须自持位置量 `_cspFollowPos`（与末段写入位置解耦）。相关经验见 [[lessons/JudgementThresholdScaleMismatch]]。

## 设计决策

- 运控数据/工作流**从 InteliWeld / Workflow 迁出**，归独立 `MotionControl` 模块。
- 运动控制采用**三层架构**（L1 Native / L2 `IMotion/` / L3 `DeltaEtherCAT/`）+ 业务层 `MontionManager`；业务层只面向 L2 抽象编程。
- **2026-09-07 控制器换轨**：移除正运动全套，全面落台达 EtherCAT；消费方全量对接 `MontionManager`。
- **2026-09-07 高级运动能力入档**：PVT 与 ECAM/ECAM2 的使用方式、API 真值核验、焊缝跟踪方案裁决，见 [[guides/DeltaEtherCAT-AdvancedMotion]]；配套 UI 设计见 [[guides/DeltaEtherCAT-UIDesign]]。
- **2026-09-16 CSP 实时目标落地（ADR-042）**：~~`ICspMotion` 契约按 `IPVTMotion` 同款范式扩展~~（⛔ 2026-09-21 ADR-042 首跑后删除，见上）；焊缝跟踪主方案由 PVT 换轨为 **CSP 周期同步位置**；PVT 链路原样保留为备用模式。
- **2026-09-22 CSP 输出整形换轨（ADR-042）**：`StepCspTarget` 由「位置贴齐 → 减速限幅」两代整形统一换为**一阶跟随**（τ=150ms）；写段门限**硬编单脉冲当量**；耗干阈值 `BufferIdleTicksToDrain` 20→60 拍；`OutputDeadbandMm` 默认 0.05→0.01 且加载期上界 0.02；轨迹记录逐拍不去重；起焊首条日志打印全部生效配置。详见 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]。
- **2026-09-16 CSP 输出并入流程步骤（ADR-042）**：CSP 目标写入由「独立 1ms 后台线程」改由 `FlowProcess` 的 CSP 分支**按拍写入**——起焊启用 → 逐拍写入 → 报警处置 → 停焊收口落在同一执行步序列内闭环，消除模组工作流自起线程、case 内 `while`/`Sleep` 两处架构契约违规；节拍随流程（10ms/100Hz），限幅器改按实测 dt 折算，`SEAM_GUIDE/CYCLE_TIME_MS` 配置项删除。
- 详阅 [[decisions/ADR-027-MotionControllerDeltaReplacement]]、ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]、ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[guides/DeltaEtherCAT-DevGuide]]、[[guides/DeltaEtherCAT-Deployment]]。

## 协作关系

| 协作对象 | 数据接口 |
|----------|----------|
| [[modules/DeviceControl]] | `MotionControlWorkflow` 承载运控启停编排；私有阶段枚举经 `MapWeldStatus` 映射为焊接过程态 `SubDeviceWeldStatus` |
| [[modules/WeldParamControl]] | `WeldParamManager.CurrentRobotX` 供真实机器人 X 读取（**PVT 模式**，历史遗留恒 0）；**CSP 模式**改为 `WeldParamManager` 暴露 `TryGetSeamTrackingCorrectionMm` / `SeamTrackingAlarmRequested`，由 `MotionControlWorkflow` 的 CSP 步骤按拍消费（ADR-042）；`MoveControlData` **不再**承接标定计算与水平移动缓存（⛔ 已随 ADR-042 删除；标定 / 几何 / 安装参数现经 `WeldParamManager.Instance.AlgorithmsConfig` 读取，CSP 起焊种子取 `AlgorithmsConfig.TeachLockYMm`） |
| [[modules/LineLaserCam]] | 模拟模式取虚拟相机 `LineLaserManager.Instance.VirtualCamera`（⛔ `CameraSelector` / `ICameraRun` / `CameraRun` 已随 ADR-017 / ADR-033 删除）；`Comm/SystemComm` 枚举 |
| [[modules/EmguALG]] | ⛔ 原 `PipelineManager.AlgorithmCompleted` / `SeamFeatureResult` 上报链已随 ADR-007 整条删除（焊缝特征改由线激光直接获取） |
| [[modules/Comm]] | `GlobalCommData.ShowLog` 日志（L2 不使用，仅 L3/业务层） |
| [[modules/UIDesign]] | `SystemControlPage`（原 `MotionControlPage`，2026-09-29 更名 + Tabs；运控 IO/轴/气缸 4 表 + CSV/XML 工具栏 + 参数编辑器，位于 `UIDesign.TabPage`；标定/模拟已迁 ProcessControlPage） |

> **参照范式**：本模块是 [[standards/ModuleOrganizationPattern]] 的**场景 A（基于第三方库台达 EtherCAT）**样本——`IMotion/` 抽象（零依赖）+ `DeltaEtherCAT/`（含 `Native/`）+ `MontionManager` 唯一入口与三张注册表。

---

*来源：AdaWeldSystem/MotionControl/ 模块源码*

## 初始化闸门与指令状态检测（2026-11-05，ADR-082/063 演进）

- 初始化唯一闸门 `MontionManager.IsInitCompleted`：未完成前 `TaAvailable`/`TaMotionReady` 均为 false，TA 指令在**执行段**被拒（⛔ 2026-11-17 起 UI 不再靠置灰表达不可用，见 ADR-063）。
- 第 3 步使能逐轴留痕（开始 / 每轴结果 / 汇总 / 结论）；⛔ 不允许「打印进入第3步却无后续日志」的静默路径。
- 指令状态检测族：`WaitAxisAtTarget` / `WaitAxisHomed` / `WaitTaTorqueOn` / `WaitTaTorqueOff` / `WaitLaMotorAtTarget`，统一 5s（ZeroPose 例外，行程估算 10~60s）。
- 同轴单飞 `TryBeginAxisInstruction` / `EndAxisInstruction`，全部调用方在 `finally` 释放；不同轴可并行。

## 设备归属与流程归属（2026-11-05）

| 层 | 归属 | 内容 |
|---|---|---|
| **硬件 / 连接层** | `MontionManager` + `DeltaMontionAxis`（Y、送丝 TA、焊接头从站） | 轴对象、轴配置、使能、SDO、回零状态、单飞登记、状态检测族、按轴门禁原子 |
| **流程层（Y / TA）** | [[api/MotionControlWorkflow]] | Y 轴与送丝轴的指令编排与判据：`TaTorque(Auto/Retract)`、`TaBreak/TaPose1/TaPose2/TaZeroPose`、`YReady`、`GetTaGateReason` |
| **流程层（LA）** | [[api/LaserWeldHeadWorkflow]] | 自动对焦电机与振镜的指令编排：`LaAuto/LaSpot/LaPose/Galvo*`、`LaReady/LaGateReason`；焊接头从站温度/IO/报警属设备层留此 |
| **UI 层** | `ProcessControlPage` 三个指令区 | Y 区向 `MotionControlWorkflow` 取 `YGateReason`；TA 区取 `GetTaGateReason`；LA 区向 `LaserWeldHeadWorkflow` 取 `LaGateReason` |

- **同一轴跨流程互斥**：单飞登记以**轴名**为键落在硬件层，任一 workflow 动作前都必须 `TryBeginAxisInstruction(axisName, …)`；
  同一物理轴只有一份轴名，故不可能被两个 workflow 同时操作；Y 与 TA 轴名不同、可并行。
- **安全全局、功能按轴**：急停 / 总线非 OP / 驱动器报警 = 全局（任何轴拒绝）；使能失败 / ZeroPose 未到位 = 按轴（只关该轴闸门）。
- **TA 位置读取**：LA 随动补偿经 `MotionControlWorkflow.TaPositionMm` 获取，⛔ 不再由激光头流程私持 TA 轴对象。
- **TA 工作零位坐标（2026-11-06）**：`MontionManager.TaZeroPoseTargetMm` 是唯一读取口，值来自工艺设置页 TA 区 `TA_ZERO_POSE_MM`
  （`WeldAlgorithmsConfig.TaZeroPoseMm`）；`ROOT/TA_HOME/TA_HOME_ZERO_POSE_MM` 仅作一次性迁移来源，⛔ 不再运行期读取。
  速度/容差/加减速**复用 TA_Pose1/2 同源**（ADR-091）：`taAxis.MaxVel`（≤0 兜底 1.0 并告警）+ `MontionManager.InstructionDefaultTolMm`（0.1mm）+ `AccTime/DecTime/STime`；⛔ 无独立配置键。
- **就绪变化通知（2026-11-05）**：硬件层 `AxisReadinessChanged(axisName)` 在「每轴使能完成 / ZeroPose 开始与结束 / 初始化完成」广播，两个 workflow 转发 `AxisReadyChanged`；工艺页订阅后即时重算三区可用性，⛔ 不依赖下一次点击或轮询。
