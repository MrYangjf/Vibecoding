---
title: ADR-030 焊接头现行决策（WSX 从站挂靠台达 EtherCAT · 归运控管控；整合原 049/051）
date: 2026-09-15
updated: 2026-10-08
tags: [决策, 焊接头, WSX, 台达, EtherCAT, 从站, MotionControl, merged, ADR-030]
status: accepted
merged_from: [ADR-049, ADR-051]
evolved: 2026-10-08（第二节「对焦轴归运控」被业主决策 2 推翻，LA 改由从站电机对象实现）
---

# ADR-030：焊接头现行决策（WSX 从站挂靠台达 EtherCAT · 归运控管控；整合原 049/051）

> 本页为承继页：整合原 ADR-030（WSX 从站接入与对焦轴归运控）与 ADR-012（归运控单一从站实现类）的**现行裁定**。原 049 仅作沿革档案保留，现行结论以本页为准。
> ⚠️ **编号复用提示**：本页「原 ADR-030」指 **2026-09-17 重排前的旧编号**（内容已并入本页），与现行 [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（焊缝跟踪绝对目标基准）**同号不同页**，勿混。

## 沿革时间线

1. **2026-09-15 · 原 ADR-030**：万顺兴焊接头（Wsx_ScanCut）作为台达 PCI-L221 主站卡的 EtherCAT 从站接入；对焦轴归运控、送丝电机取消；设计 B1~B6 分期。其 B3「LaserWeldHead 三层重构」同日被裁定废止。
2. **2026-09-15 · 原 ADR-012**：焊接头无复用性、不需要抽象与独立 Manager——改为单一实现类 `WeldHeadSlaveDevice` 归 `MontionManager` 管控（同轴范式），`LaserWeldHead/` 目录整体删除；同时修正从站握手先于主站初始化的时序缺陷。

## 背景

- 厂商资料：ESI 文件 `Wsx_ScanCut.xml`（VendorID `0xE0000002` / ProductCode `0x26483052` / Rev 6）与寄存器表 `EtherCAT协议.xlsx`（58 变量），实施 B1 时归档至 `raw/wsx/`。
- 原 ADR-030 B3 按 ADR-006 三层范式落地（`ILaserWeldHeadController` + `WsxScanCutHeadController` + `WeldHeadManager`，独立目录 `LaserWeldHead/`）；用户评审后裁定误解了意图——焊接头作为台达 EtherCAT 从站设备**无复用性**，不需要抽象与独立 Manager。
- 原 B3 设计还存在**时序缺陷**：焊接头初始化排在运动控制器初始化之前，而从站 SDO 握手依赖台达主站已打开——主站未初始化前握手不可能成功；随运控初始化的方案正好修正此问题。
- 落地时 [[modules/MotionControl]] 台达三层已就绪，`DeltaSlaveScanner` 原只认 ProductCode `0x2200001`（台达伺服），需扩展登记 WSX 身份。

## 现行裁定

### 一、WSX 激光焊接头作为台达 EtherCAT 从站接入

1. WSX（Wsx_ScanCut）焊接头控制部分作为**台达 PCI-L221 主站卡的 EtherCAT 从站**接入；CoE（SDO + CompleteAccess）+ FoE，DC 支持 SM-Synchron / DC-Synchron。
2. **从站识别**：`DeltaSlaveScanner` 扩展登记 WSX 身份（VendorID `0xE0000002` / ProductCode `0x26483052`），识别为「焊接头从站」类别——**不当轴、不进 AxisRegistry**。
3. **依赖方向**：焊接头**不直调台达 Native**；统一经 `MotionControl` L3 的 `DeltaSlaveDevice` 通用从站通道（对指定 NodeId 提供 SdoRead/SdoWrite + PdoGet/PdoSet），厂商类型只在 MotionControl 域出现，焊接头可整体替换。L1 已有 `CS_ECAT_Slave_SDO_Read/Send_Message` 与 `CS_ECAT_Slave_PDO_Get/Set_OD_Data`，接入 WSX 无需新增 P/Invoke。
4. **PDO 固定映射**（Fixed+Mandatory，不可重配）：RxPDO 0x1601 振镜参数（Pattern 1圆 2八字 3直线 4圆弧、频率 10~500Hz、宽长、角度、中心、压缩、GalvoEnable）/ 0x1602 阈值 + LaserStatus 出光 + 复位；TxPDO 0x1A00 温度/气压/SensorStatus / 0x1A01 振镜状态 / 0x1A02 电容值；SDO 专属 0x2004 MCU 版本。0x7000/0x1600 电机对象留而不映射。
5. **定标**：寄存器表标注 float 精度 0.1、ESI 类型为 INT/UINT——**0.1 定标换算在上位机**（乘法），从站不还原。

### 二、对焦轴 ~~归运控~~ → **改由焊接头从站实现**（2026-10-08 就地补正）

> ⚠️ **2026-10-08 被业主决策 2 推翻并已落地**，理由 = 实际硬件形态：**LA（对焦轴）由焊接头从站的步进电机实现，不是台达伺服轴**。
>
> | 旧状态（推翻） | 现行做法 |
> |---|---|
> | Z 向对焦电机由台达伺服轴驱动，登记进 `DeltaMotionConfig` 轴表 | **轴表行 `Z向对焦电机` 已删除**（`AxisRegistry` 由 4 条降为 2 条：TA + 追踪轴） |
> | `SetAutoFocusPosition` 转发轴 API | **⛔ 已删除**（实测全库 0 消费者，属旧路由死代码） |
> | `AutoFocusExecutor` 保留为装配点 | **⛔ 已删除**（同上） |
> | — | **改用 WSX 从站电机对象**：`0x7000`（RxPDO）Sub1 目标位置 / Sub2 使能；`0x6020`（TxPDO）Sub2 状态 / Sub3 当前位置 / Sub4 就绪。API = `SetMotorPosEnable` / `ReadMotorStatus` / `StopMotor` + `MotorRunState` / `MotorState` |
> | — | **量纲可配置** `MotorPulsePerMm`（默认 **10** 计数/mm，业主 2026-10-08 确认），配置键 `MOTOR/PULSE_PER_MM`，换算单一入口 `MmToMotorCount` / `MotorCountToMm` —— **定义权归 [[decisions/ADR-053-TaLaCurveAndMotorScale]]**（曲线与量纲），本页仅作摘要，避免双权威 |
>
> ⚠️ 厂商协议表（`raw/wsx/EtherCAT协议.xlsx` 第 34-35 行）`0x7000` Sub1 **只标「范围 0~1000」未标单位**，10:1mm 为业主确认值；**上机前建议与厂商复核一次**。
>
> **③ 振镜不收编为运控 IO 的结论维持不变**（振镜仍归从站 OD 读写）；且轴表行 `振镜控制`（NodeId=4）因本就无代码消费，**同批删除**。

1. ~~Z 向对焦电机改由台达控制器（伺服轴）驱动~~ → **⛔ 已作废，改由从站电机对象实现**（见上表）。
2. ~~对焦轴登记进 `MontionManager` 轴体系~~ → **⛔ 已作废，轴表行已删除**；`SetAutoFocusPosition` / `AutoFocusExecutor` **⛔ 已删除**；新增 `MotorPulsePerMm` 量纲配置（四点闭环，走 `MontionManager` 持久化）。
3. **振镜不收编为运控 IO**：振镜是对象字典语义而非 IO 语义，归焊接头从站 OD 读写承载 —— **此条维持不变**。

### 三、WeldHeadSlaveDevice 归 MotionControl 管控（原三层结构已删）

1. **单一实现类**：`MotionControl/DeltaEtherCAT/WeldHeadSlaveDevice.cs`（命名空间随目录，ADR-005），合并 OD 读写、定标换算、阈值/振镜/出光/报警 API 与数据结构（`WsgGalvoPattern`/`GalvoParams`/`LaserHeadTemperatureData`/`HeadAlarmStatus`/`WeldHeadConfig` 同文件内嵌）。**无接口、无单例、无独立 Manager**；~~原 ADR-030 B3 的 `ILaserWeldHeadController` + `WsxScanCutHeadController` + `WeldHeadManager` 三层结构~~已整体删除（`LaserWeldHead/` 目录 + csproj 4 条 → 1 条）。
2. **Manager 注册装载**：`MontionManager` 仿 `CreateAxesFromConfig` 增加 `CreateWeldHeadFromConfig()`——读 `WeldHeadSlave` 配置节，Enabled 时构造 `WeldHeadSlaveDevice(CardNo, NodeId)` 并握手 + 下发阈值 + **赋电机量纲** + **下发振镜逻辑零位**（2026-10-08 改：原为「振镜默认参数」）；公开属性 `WeldHead`；`Close()` 一并释放；失败仅告警不阻塞轴初始化。
3. **配置归 Manager 持有**：`MontionManager.WeldHeadConfig` 实例与持久化独占（`Config/XML/WeldHeadSlave.xml`，`LoadWeldHeadConfig`/`SaveWeldHeadConfig` 走 `XdocumentReaderWriter`）。（**2026-09-20 演进**：路径按 ADR-033 迁至 `Config\MotionControl\WeldHead_XML\WeldHeadSlave.xml`；**2026-09-21 更新**：历史路径统一由 `FileOperate/ConfigPathMigrator.cs` 一次性迁移，原 `MigrateLegacyControllerXml()` 已删除）
4. **初始化顺序**（修正从站握手时序缺陷）：机器人通讯 → 运动控制器（含焊接头从站注册与握手）→ 焊接头状态同步（握手成功才 `_weldHead.ConnectOn()`）→ 线激光 → 监控。
5. **后续项**：TxPDO 周期读取与超阈事件接 `LaserWeldHeadWorkflow`（四态收敛 Disconnect/Connect/Work/Alarm）；振镜调试 UI 待做。`DeltaSlaveDevice` 通用从站通道与 WSX 识别（原 B1/B2）保留不变。
6. **上机验证项**（设计期无法闭环）：从站过程数据 Offset（主站扫描分配）、轮询周期与总线周期约束、DC 模式选择（SM-Synchron vs DC-Synchron）。
7. **WSX NodeId 校验**：`WeldHeadSlave` 配置节含 NodeId / Revision 校验 / 使能开关；WSX NodeId 进 `DeltaMotionConfig`，与轴表并列、不混入轴体系。

## 后果

- 正面：结构归位（焊接头 = 运控下的从站设备，与轴/IO 同范式）；初始化时序缺陷修正；少 3 个文件 1 层间接；焊接头获得真实硬件通路，对焦与振镜控制权清晰（对焦=轴，振镜=从站对象字典）。
- 负面 / 约束：`WeldHeadSlaveDevice` 同时承担 OD 读写与业务参数，若未来出现第二家焊接头厂商再评估抽抽象层；温度轮询周期受 EtherCAT 总线周期约束；`LaserWeldHeadWorkflow`（MainDeviceControl/DeviceWorkflow）保留不变，为后续数据链路接入点。

## 被推翻的中间态（沿革档案）

- ~~原 ADR-030 B3「LaserWeldHead 三层重构」~~：单实现零复用，抽象层与 Manager 无消费者（违反 ADR-007 精简精神），且原初始化顺序下从站握手先于主站初始化、时序上不可能成功——被「单一实现类归运控管控」取代。
- ~~直调台达 Native~~（放弃）：厂商类型泄漏进焊接头模块，焊接头不可替换。
- ~~LaserWeldHead 旧占位实现~~（Timer 轮询、COM 口配置、送丝参数）已删除。

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[modules/MotionControl]]（WeldHeadSlaveDevice 条目）、[[modules/Comm]]
- [[api/MontionManager]]、[[guides/DeltaEtherCAT-DevGuide]]
- [[decisions/ADR-006-ModuleOrganizationPatternStandard]]（本例为「单实现零复用」豁免场景）、[[decisions/ADR-027-MotionControllerDeltaReplacement]]、ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）、[[decisions/ADR-005-NamespaceDirectoryAlignment]]、[[decisions/ADR-007-CodeSimplificationStandard]]、ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）
- ADR-030-WeldHeadDeltaEtherCATSlave（已并入本页，沿革档案；B1/B2 结论保留）
- 原档：`raw/wsx/EtherCAT协议.xlsx`、`raw/wsx/Wsx_ScanCut.xml`（归档自 `M4/万顺兴焊接头资料/`）
