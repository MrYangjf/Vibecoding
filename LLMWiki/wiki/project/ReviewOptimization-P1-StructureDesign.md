---
title: P1 结构设计定稿 — 第一次评审优化（五份产物）
date: 2026-10-08
tags: [结构设计, 冻结点, 第一次评审, 硬件归属, 数据模型, 页面归属, ADR清单]
status: proposed
---

# P1 结构设计定稿 — 第一次评审优化

> **本层不写功能代码，只定结构。** 五份产物产出并经业主确认后，方可进入 [[project/vibecoding-workflow]] 的 **P2 结构落地**；P2 完成即**冻结**，此后只可追加不可挪位。
> **依据** = 业主 2026-10-08 六项决策 + 五项外部依赖处置 + [[architecture/CodeMap]] 实测 + ADR 001~051。
> **裁决顺序**：原档 > 架构页 > 源码注释 > 本表。
>
> **状态**：2026-10-08 业主五项遗留（Q1~Q5）已全部答复并落位（见 §⑥）。**P2 落地后本结构冻结：只可追加不可挪位。**
>
> 章节：① 硬件归属矩阵 · ② 模块与命名空间落位图 · ③ 数据模型定稿 · ④ 页面板块归属矩阵 · ⑤ ADR 清单 · ⑥ 遗留待确认（已答复）· ⑦ 遗留（不阻塞）· ⑧ 自校验结果

## 0. 产物清单与冻结判据

| # | 产物 | 回答什么问题 | 冻结判据 |
|---|---|---|---|
| ① | 硬件归属矩阵 | 每个设备走**运控轴**还是**焊接头从站**？参数落哪个字典段？ | 无「待定」格 |
| ② | 模块与命名空间落位图 | 新增/迁出文件放哪？csproj 登记什么？ | 每个新文件有唯一落点 |
| ③ | 数据模型定稿 | 加哪些字段/配置键/曲线表？ | 键名唯一且四点闭环齐备 |
| ④ | 页面板块归属矩阵 | 每个控件归工艺还是归系统？谁能看见？ | **无控件出现在两个板块** |
| ⑤ | ADR 清单 | 本轮新增/修订哪些决策？ | 编号无冲突（接 001~051） |

**冻结后的铁律**：新增只允许追加；发现问题记「结构变更申请」回 P1 评估，**不就地改**。

---

## ① 硬件归属矩阵

### 1.1 总矩阵

| 设备 | 物理承载 | 控制通道 | 配置落点 | 状态 |
|---|---|---|---|---|
| **TA**（送丝Z轴） | 送丝力矩电机（台达伺服轴，NodeId=1） | 台达 CSP **CST 力矩模式** | `Config/MotionControl/Motion_XML/DeltaMotionConfig.xml` → `ROOT/AXES/AXIS`（`AXIS_NAME=送丝力矩电机`） | ⚠️ 需加 3 个力矩字段 |
| **追踪轴**（Y） | Y向电机（台达伺服轴，NodeId=3） | 台达 CSP 缓冲（S 曲线读轴配置 `STime`） | 同上 + `ROOT/SEAM_TRACK/SEAM_TRACK_AXIS`（默认 `Y向电机`） | ✅ 现状不变 |
| **LA**（对焦轴） | 焊接头从站步进电机 | **WSX 从站 PDO** | `Config/MotionControl/WeldHead_XML/WeldHeadSlave.xml`（当前空文档 `<Root />`） | ⚠️ **0x7000/0x6020 待启用** |
| **振镜** | 焊接头从站 | **WSX 从站 PDO** | 同上（`GALVO` 段，当前缺） | ✅ 协议通，缺消费方 |
| **送丝机** | 独立设备，**只能送丝前进（X 向）** | 机器人侧调送丝 | 无本地配置 | ✅ 约束已定 |
| **温控** | 焊接头从站 MCU | WSX 从站 PDO（阈值下发） | `WeldHeadSlave.xml` `THRESHOLD` 段 | ⚠️ 文件为空，走代码默认值 |
| **监控相机** | 海康 MVS GigE 相机 | TCP | `Config/MonitorCam/Monitor_INI/MonitorCamera.ini` | ✅ 不变（ADR-047） |
| **线激光** | 英莱相机 | TCP | `Config/LineLaser/LineLaser_XML/LineLaserConfig.xml` | ✅ 不变 |

### 1.2 轴表变更（结构决策：删两行）

`轴IO气缸配置模板/轴配置表.csv` + `DeltaMotionConfig.xml` 同步处理：

| 轴名 | 现状 | 处置 | 理由 |
|---|---|---|---|
| `送丝力矩电机` | NodeId=1, ENABLED=TRUE | **保留**（语义=TA） | 决策 2 |
| `Y向电机` | NodeId=3, ENABLED=TRUE | **保留**（语义=追踪轴） | 决策 2 |
| `Z向对焦电机` | NodeId=2, ENABLED=FALSE | **删除整行** | LA 改由从站实现，轴行无消费者 |
| `振镜控制` | NodeId=4, ENABLED=FALSE | **删除整行** | 振镜走从站 OD，本就无代码消费 |

**连带影响**：`MontionManager.cs:99-103` 装载循环对 `!Enabled` 直接 `continue`，删行后 `AxisRegistry` 从 4 条降为 **2 条**（TA + 追踪轴）。须确认 `SystemControlPage` 的 `tableAxis`（19 列，仅渲染 Y 向）渲染不受影响。

**登记要求**：删行须在 `tools/drift_scan_precise.py` 登记 `REMOVED`，**值为纯路径**（`AXIS_NAME` 走 XML 键名，不是 `.cs` 路径 ⇒ 实际按 `DeltaMotionConfig.xml` 内的轴名登记，登记前先确认扫描器匹配口径）。

⚠️ **顺带确认**：`DeltaMotionConfig.xml` 存旧键（`MIN_VEL`/`MAX_VEL`/`HOME_DIR`/`HOME_MAX_VEL`），代码用 `ChildValueAny` 兼容读，但 `SaveConfig` 只写新键（`STR_VEL`/`CONST_VEL`/`END_VEL`/`HOME_FIRST_VEL`）⇒ **首次保存即丢旧键**。借本次删行一并清理。

### 1.3 LA 从站对象字典（结构核心）

> 依据 `raw/wsx/EtherCAT协议.xlsx`「扫描切」表第 34-35 行。**ADR-030 原声明「`0x7000`/`0x1600` 电机对象留而不映射」，决策 2 下必须启用。**

| 方向 | OD 段 | 子索引 | 含义 | 量纲 | 备注 |
|---|---|---|---|---|---|
| 写 | `0x7000`（RxPDO `0x1600`） | 1 | 电机目标位置 | **计数**，默认 10 计数 = 1mm | 范围 0~1000；⚠️ 协议表未标单位 |
| 写 | `0x7000` | 2 | 电机使能 | bool | |
| 读 | `0x6020`（TxPDO `0x1A02`） | 2 | 电机状态 | enum | 00停止/01负限位/02正限位/03运动 |
| 读 | `0x6020` | 3 | 电机当前位置 | 计数 | 同上量纲 |
| 读 | `0x6020` | 4 | 电机就绪 | enum | 00就绪/01报警 |

**量纲可配置项**（决策 2 二次答复）：`MotorPulsePerMm` 默认 **10**。
- 换算：`mm = count / MotorPulsePerMm`；`count = mm × MotorPulsePerMm`
- **单一换算入口**：`WeldHeadSlaveDevice` 内所有 mm↔count 必经同一方法，⛔ 禁止多处散算（量纲变更时漏改 = 隐性 BUG）
- 归**系统设置-激光头控制**，走四点闭环

### 1.4 振镜逻辑零位（新增概念）

> 决策 2 二次答复：PDO 字典无零位对象 ⇒ **以状态定义零位**。不等同物理轴回零，但从站换厂家时概念仍成立。

| 参数 | 零位取值 | 依据 |
|---|---|---|
| `Pattern` | **`WsgGalvoPattern.Line`（=3）** | 决策「按直线和最小摆幅做零位」 |
| `Width` / `Length` | **0**（最小摆幅） | 同上 |
| `XCenter` / `YCenter` / `XCompression` / `YCompression` | 0 | 中位 |
| `Angle` / `StartAngle` / `EndAngle` | 0 | 无旋转 |
| `GalvoEnable` | **false** | 静止初态 |

⚠️ **与现状的差异**：`GalvoParams` 构造函数默认 `Pattern=Circle, Width=1.0, Length=1.0, EndAngle=360.0, GalvoEnable=false`。⇒ **逻辑零位 ≠ 协议默认值**，须新增工厂方法 `CreateLogicalHome()` 显式构造，**不得改构造函数默认值**（否则 `WeldHeadConfig.DefaultGalvo` 与「回零」语义混淆）。

**落地**：`MontionManager.cs:260` 初始化时下发逻辑零位（替代现状下发 `DefaultGalvo`）；系统设置-激光头控制提供「回到零位」动作。

### 1.5 振镜参数 / 功能 二分（决策 1）

| 类别 | 参数 | 归属板块 |
|---|---|---|
| **内部设置** | Frequency / Width / Length / Angle / StartAngle / EndAngle / XCenter / YCenter / XCompression / YCompression / TargetSize / **逻辑零位** | 系统设置-激光头控制 |
| **功能与图形** | `Pattern`（圆/八字/直线/圆弧）图形编辑 · 手动演示 · 启用开关 · 随焊宽自适应 | 工艺设置-激光头工艺设置 |

⚠️ `TargetSize`（目标尺寸）虽在协议里与图形同段，但属**尺寸标定** ⇒ 归系统设置。`ActualSize` 仅回读，不设 UI。

### 1.6 摆幅消费方（决策 3：原「无消费方」）

```
线激光焊缝宽度
  → WeldParamAdjustmentAlgorithm（自适应算法）
  → AutoParamHelper 查表（第 6 列「振镜摆幅」）
  → WeldParamOutput.GalvoAmplitude        ← 现恒 0（:225 占位）
  → LaserWeldHeadWorkflow 按拍消费
  → WeldHead.SetGalvoParams()              ← 运行期无调用，需补
  → WSX RxPDO 0x7010
```

**第二个消费方（本次新发现）**：`DeviceControlWork.cs:317` 注释明载「OffsetX/Y 供控制器驱动振镜」，`api/DeviceControlWork.md:522` 记 `ApplySpotAlignCompensation` 为 todo ⇒ **光丝对中偏差驱动振镜 X/Y 中心微调**。链路：
```
光丝对中 OffsetX/OffsetY（mm）
  → DeviceControlWork.AlignDatum
  → ApplySpotAlignCompensation（待实现）
  → GalvoParams.XCenter / YCenter
  → SetGalvoParams
```

⚠️ **两条链路都改 `XCenter/YCenter`** ⇒ P2 需定**合并写入口**（单一 `ApplyGalvoCenterOffset()`），否则中心偏移与摆动参数互相覆盖。

---

## ② 模块与命名空间落位图

> 遵循 ADR-005：`namespace == "AdaWeldSystem" + 目录路径`。**落点在 P1 定死，P2 不得临时决定。**

### 2.1 新增文件（6 个 .cs + 6 个 Designer + 6 个 resx）

| # | 路径 | 命名空间 | 职责 | csproj |
|---|---|---|---|---|
| N1 | `WeldParamControl/Curves/TaLaCurveConfig.cs` | `AdaWeldSystem.WeldParamControl.Curves` | TA/LA 标定曲线采样点表 + 分段线性插值 + 外推策略 | `<Compile Include>` |
| N2 | `WeldParamControl/Curves/WeaveWidthTable.cs` | 同上 | 摆幅分段表（读 `AutoParamHelper` 第 6 列） | `<Compile Include>` |
| N3 | `UIDesign/TabPage/QuickCalibPanel.cs` | `AdaWeldSystem.UIDesign.TabPage` | 工艺设置·快速标定 | Compile + EmbeddedResource + DependentUpon |
| N4 | `UIDesign/TabPage/LaserHeadProcessPanel.cs` | 同上 | 工艺设置·激光头工艺设置（功能与图形） | 同上 |
| N5 | `UIDesign/TabPage/AdaptiveProcessPanel.cs` | 同上 | 工艺设置·自适应工艺参数 | 同上 |
| N6 | `UIDesign/TabPage/TempMonitorPanel.cs` | 同上 | 系统设置·温度监测 | 同上 |

⚠️ **每条 UI 新文件 = 3 条 csproj 登记**（`.cs` Compile + `.resx` EmbeddedResource + `.resx` DependentUpon），漏一条则 VS 树不嵌套 / 设计器资源无法嵌入。

### 2.2 改造文件（不新建，就地扩）

| 文件 | 改动 | 命名空间一致性 |
|---|---|---|
| `MotionControl/WeldHeadSlaveDevice.cs` | 加 4 常量 + 6 子索引 + 3 方法（LA）+ 2 换算方法 + `CreateLogicalHome()` + `MotorPulsePerMm` | ✅ 已是 `AdaWeldSystem.MotionControl` |
| `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs` | 加 `TorqueTarget` / `TorqueSlope` / `TorqueMode` | ✅ |
| `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` | 加 `SetTorque` / `StopTorque` / `GetTorque` | ✅ |
| `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` | 轴表头 19 → **22 列** | ✅ |
| `MotionControl/MontionManager.cs` | `:260` 初始化下发逻辑零位 | ✅ |
| `MainDeviceControl/DeviceStateApiCore/CommandCore.cs` | 加 `TxCutWire` + `IsKnownCommand` 行 | ✅ |
| `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` | `MonitorResult` 加异常标志位 | ✅ |
| `MainDeviceControl/DeviceControlWork.cs` | `SendCutWire()` + 订阅异常 + `ApplySpotAlignCompensation` | ✅ |
| `Comm/Communication/Implementations/KukaRsiComm.cs` | `ResolvePlaceholder` 扩 T13 占位符 | ✅ |
| `Comm/Communication/CommunicationManager.cs` | `SaveRobotRsiXml()` 生成 T13 | ✅ |
| `EmguALG/RealtimeMonitor/WireFeedDistance/*` | 三件扩 mm 字段 + 阈值 | ✅ |
| `ProductFileControl/Records/WeldParamControlRecord.cs` | 记录加 5 字段 | ✅ |
| `ProductFileControl/Records/RecordFileStore.cs` | 写侧+读侧+旧记录回落；列名抽常量 | ✅ |
| `SQLiteDBControl/Helpers/AutoParamHelper.cs` | `_paramColumns` 5 → **6 列** | ✅ |
| `WeldParamControl/WeldAlgorithmsConfig.cs` | 加 `EnableGalvoWeave`；删 `WireType`/`PlateType` | ✅ |
| `UIDesign/TabPage/ProcessControlPage.cs` | Tabs 重排 3 页 + 挂 N3/N4/N5 | ✅ |
| `UIDesign/TabPage/SystemControlPage.cs` | Tabs 重排 3 页 + 挂 N6 | ✅ |
| `UIDesign/TabPage/MonitorCamPage.cs` | 加光丝对中阈值控件 | ✅ |

### 2.3 迁出文件（跨页搬迁）

| 从 | 到 | 内容 | 清理要求 |
|---|---|---|---|
| `ProcessControlPage`（`tabPageLaserProcess`） | `SystemControlPage`（轨迹跟踪） | 线激光参数 10 项（标定中心 Y/Z、角度、示教 Y 锁定、轴激光比例、偏差方向、激光超前量、Y 补偿系数、行程上下限、地图点数上限） | ⛔ 搬迁后 Grep 原控件名，差集须为 0 |

### 2.4 落位红线

1. **不新建实现类**：`WeldHeadSlaveDevice` 内扩展 LA/振镜（ADR-030 裁定单实现零复用，不做抽象层）
2. **Manager 唯一口**：配置与资源归 `MontionManager` / `WeldParamManager` 独占
3. **UI 控件落设计器**（业主口径：不接受全动态加载）；例外 = `AntdUI.Table.Columns` 必须代码后置（全库 13 处一致）
4. **⛔ 曲线配置不建新配置类体系**：复用 `XdocumentReaderWriter` 三段式（ADR-033）

---

## ③ 数据模型定稿

### 3.1 记录 Schema 扩展

`WeldParamControlRecord.cs:155-225` `WeldActionRecord` 现有 **15 字段**（`FrameIndex`/`Timestamp`/`ActionType`/`RobotX`/`RobotY`/`RobotZ`/`RobotSpeed`/`FeedSpeed`/`LaserPower`/`WeldWidth`/`JobId`/`SeamPointY`/`SeamPointZ`/`AdjustExecuted`/`AdjustData`）。

**新增 5 字段**：

| 字段 | 类型 | 语义 | 数据源 |
|---|---|---|---|
| `TaPositionMm` | double | TA 送丝Z轴位置 | 台达轴反馈 |
| `LaPositionMm` | double | LA 对焦轴位置 | WSX `0x6020` Sub3 × 量纲 |
| `GalvoAmplitudeMm` | double | 振镜摆幅 | `WeldParamOutput.GalvoAmplitude` |
| `GalvoPatternId` | int | 振镜图形 | `WsgGalvoPattern` |
| `HeadTempC` | double | 激光头温度 | WSX `0x6000` Sub1 |

⚠️ **三点必须同批**（漏读侧 ⇒ 旧 `.pDat` 整批解析失败）：
1. 写侧追加
2. 读侧解析
3. **旧记录默认回落**（缺字段不抛异常）

⚠️ 顺带把 `ProductFileControl/Records/RecordFileStore.cs` 内联列名抽为 `CsvHeader` 常量（对齐 `ProductFileControl/Records/SeamTraceYRecord.cs:53` 既有范式）。

### 3.2 配置键清单（四点闭环逐项列全）

| 键 | 类型 | 默认 | 存储 | Load | Save | 消费者 |
|---|---|---|---|---|---|---|
| `MOTOR_PULSE_PER_MM` | double | 10 | `WeldHeadSlave.xml` | S-1 | S-1 | LA 换算（单一入口） |
| `ENABLE_GALVO_WEAVE` | bool | false | `WeldParamControlAlgorithm.ini` / `PROCESS_CONTROL` | S-7 | S-7 | `CalcGalvoAmplitude` 门控 |
| **`WEAVE_AMPLITUDE_K`** | double | **0.2** | 同上 | S-6 | S-6 | 摆幅公式 `宽度×(1+k)`（Q5 裁定） |
| `LA_SPOT_TARGET_MM` | double | 0.6 | 同上 | S-5 | S-5 | LA Spot 指令 |
| `WIRE_ALIGN_WARN_MM` | double | 0.1 | `MonitorCamera.ini` | S-9 | S-9 | Y 向三级判定 |
| `WIRE_ALIGN_FAIL_MM` | double | 0.3 | 同上 | S-9 | S-9 | Y 向三级判定 |
| `WIRE_ANOMALY_CUTWIRE` | bool | true | 同上 | S-8 | S-8 | 剪丝触发门控 |
| `CURVE_A_POINTS` | 采样点数组 | 见 3.3 | `WeldParamControl.xml` | S-5 | S-5 | LA Spot 反查 |
| `CURVE_B_POINTS` | 采样点数组 | 见 3.3 | 同上 | S-5 | S-5 | LA Auto 随动 |

**删除键**：`WIRE_TYPE`（焊丝类型）、`PLATE_TYPE` / `PLATE_THICKNESS`（板材材质）—— 决策 5 明确无用。`WIRE_DIAMETER` **不删**，迁移到基准工艺参数组。

⚠️ 删键须同步 `Load` + `Save` + UI 绑定三处；旧 INI 中残留键读回时忽略而非报错。

### 3.3 曲线表结构（采样点表，非公式）

> ⛔ **红线**：ADR-043 与 `api/WeldParamControlWorkflow.md:149` 明令「不要用自创公式（如 `(SeamWidth - LaserDiameter)/2`）」。曲线只以**采样点表**表达。

**曲线A · 光斑大小 ↔ LA 位置**

| 序号 | LA 位置(mm) | 光斑大小(mm) | 备注 |
|---|---|---|---|
| 1 | 0 | **0.6** | 内置缺省：最聚焦态光斑最小（**勿删**） |
| 2..n | *业主填* | *业主填* | 外部标定值到位后替换 |

默认线性外延：LA 每 +1mm → 光斑 +1mm（1:1）。物理含义：LA 离焦量决定光斑大小。

**曲线B · TA 位置 ↔ LA 偏移补偿**

| 序号 | TA 位置(mm) | LA 偏移(mm) | 备注 |
|---|---|---|---|
| 1 | 0 | **0** | 内置缺省（**勿删**） |
| 2..n | *业主填* | *业主填* | |

默认 1:1 线性。

**结构定义**（`TaLaCurveConfig.cs`）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `PointsA` / `PointsB` | `List<CurvePoint>` | `CurvePoint { double X; double Y; }`（X=LA或TA位置，Y=光斑或偏移） |
| `Interpolation` | enum | `PiecewiseLinear`（默认）· `Nearest` |
| `Extrapolation` | enum | `Clamp`（默认，钳位端点）· `Reject` |
| `Version` | string | 数据版本可溯 |

⚠️ **单调性校验**：曲线A 的 Y（光斑）须随 X 单调不减；反向点 ⇒ 导入拒绝并报警（离焦量增大光斑必增大）。
⚠️ **外部值只换数据不改代码**：结构已冻结，标定到位后仅替换 `PointsA/B` 内容。

### 3.4 摆幅计算规则（Q5 业主裁定，覆盖原「纯查表」规划）

> ✅ **业主 2026-10-08 裁定**：摆幅宽度 = **焊缝识别的宽度信息值 × (1 + k)**，`k` 可配置，**默认 0.2**。

**公式**：

```
摆幅宽度 = 焊缝宽度 × (1 + k)        k = WeaveAmplitudeK（默认 0.2，可配置）
```

**⚠️ 与现行 ADR-043 红线的关系（必须如实记录）**：

| 来源 | 原文 | 关系 |
|---|---|---|
| `api/WeldParamControlWorkflow.md:149` | 「规划在 `AutoParamHelper` 新增 `WeaveWidth` **分段查找表**……⛔ 不要用自创公式（如 `(SeamWidth - LaserDiameter)/2`），那是未经验证的推导」 | 本裁定**采用业主给定的公式**，非 AI 自创 |
| `architecture/DeviceControlArchitecture.md:668` | 「`WeaveWidth` 规划为**查表项**，**不是公式推导**——不要自行发明公式」 | 同上 |

**裁决记录**：红线原文禁止的是「**AI 自行发明**未经验证的公式」，并点名了反面例子 `(SeamWidth - LaserDiameter)/2`。业主 2026-10-08 明确给出 `焊缝宽度 × (1+k)`（k 可配置、默认 0.2）——这是**业主裁定的业务规则**，不属于「自行发明」。

**执行方式**：
1. `k` 走**四点闭环配置**（键 `WEAVE_AMPLITUDE_K`，`WeldAlgorithmsConfig` 新增属性 `WeaveAmplitudeK`，默认 0.2）
2. `CalcGalvoAmplitude(wp)` 改为读该 `k` + 焊缝宽度计算
3. **保留分段表作为可选覆盖**：若后续 `AutoParamHelper` 第 6 列已有该接头的实测摆幅值，**优先查表**；无记录才用公式兜底 ⇒ 现场标定值可覆盖默认值
4. **起焊首条日志打印生效的 `k` 与当前摆幅**（沿用 lessons/JudgementThresholdScaleMismatch 坑三的「改动是否生效一眼可判」做法）

**焊接速度门控（补充裁定）**：摆幅是振镜**横向摆动**，与焊道方向垂直。焊缝识别宽度是**横向**尺寸，故该公式在直焊缝成立；**角焊缝/复杂接头需现场标定覆盖**（第 3 条的查表覆盖机制即为此留的口子）。

> ⚠️ **`FillXlOutput` 支路**（现 `:164` 硬编码 `GalvoAmplitude = 0.0`）必须同步改，否则主支路有值、支路恒 0，两条下发路径不一致。

### 3.5 光丝对中结果字段（两套算法合并）

| 字段 | 类型 | 来源 | 说明 |
|---|---|---|---|
| `OffsetXmm` / `OffsetYmm` | double | `CheckCentering`（死代码套） | 毫米级；替代现行像素 `OffsetX/OffsetY` |
| `Direction` | enum | 同上 | 左/右/上/下/居中 |
| `Grade` | enum | 同上 | Pass / Warn / Fail（映射 0.1 / 0.3 阈值） |
| `SpotCenterPx` / `WireTipPx` | PointF | 同上 | 可视化用 |
| `WireMatched` | bool | 新增 | 焊丝是否识别成功（剪丝触发判据） |
| `WireHeadAdhesion` | bool | 新增 | 焊丝头部粘连（剪丝触发判据） |

⚠️ `ToleranceAngle`（`WireFeedConfig.cs:7`）现定义但**未参与判定** ⇒ 合并时二选一：纳入判定，或删除并说明。

---

## ④ 页面板块归属矩阵

### 4.1 导航结构（目标态）

```
FormMain
├── 主内容 Tab（Segmented 切换）
│   ├── MainPage            主页面
│   └── DataReviewerPage    数据追溯
└── 参数设置（NavPage）
    ├── ProcessControlPage  工艺设置
    │   ├── 快速标定            ← N3
    │   ├── 激光头工艺设置       ← N4
    │   └── 自适应工艺参数       ← N5
    ├── SystemControlPage   系统设置
    │   ├── 轨迹跟踪
    │   ├── 激光头控制          （Admin 专属）
    │   ├── 温度监测            （Admin 专属）
    │   └── 模拟测试            ✅ 业主 2026-10-08 裁定：单开一页
    └── FilebackupPage      文档备份设置
```

> ✅ **Q1 已裁定**（2026-10-08 业主答复）：**模拟测试归属系统设置，单开一页** ⇒ `tabsSystem` 维持 **4 页**（轨迹跟踪 / 激光头控制 / 温度监测 / 模拟测试）。
> 与 ADR-032（模拟测试统一化重构）现状一致 —— 该页现有完整功能（模拟参数保存 + 三态按钮「开启/停止/清理异常」+ 线激光频率配置 30/60/80/120Hz + `SimButtonMode` 枚举），**不迁入、不拆分**，仅位置保持在系统设置内。

### 4.2 控件级归属（同一控件不得出现在两个板块）

**工艺设置 · 快速标定**（高频动作，非 Admin 专属）

| 控件 | 来源 | 说明 |
|---|---|---|
| Y轴回标定位置 | 迁移 `chkLockYCalib` | 勾选即移轴并保持锁定，走 `IsCalibrationYReady` 门控 |
| 光斑回标定位置 | 迁移 `chkLockSpotCalib` | 同上 |
| 送丝结构锁定位置 | 迁移 `chkLockWirePos` | 同上 |
| TA 动作位 | **新增** | auto / break / pose1 / pose2 |
| LA 动作位 | **新增** | auto / Spot1 / Spot2 / Pose1 / Pose2 |
| 启用管理 | 迁移 `swEnableAdapt`/`swEnableSeamTrace`/`swEnableWireAlign`/`swEnableTempCtrl` | 4 个 Switch 集中；**启用线激光引导的重复入口在此收敛**（消除自适应页的第二处） |

**工艺设置 · 激光头工艺设置**（功能与图形，非 Admin 专属）

| 控件 | 说明 |
|---|---|
| TA 动作按钮组 | auto（设下压力）/ break（仅 auto 生效）/ pose1 / pose2 |
| LA 动作按钮组 | auto（随动）/ Spot1 / Spot2（设光斑大小）/ Pose1 / Pose2 |
| 振镜图形编辑 | 圆 / 八字 / 直线 / 圆弧（`WsgGalvoPattern`） |
| 振镜手动演示 | 一次性动作，须与生产流程互斥 |
| 目标光斑大小 | 驱动曲线A 反查 LA 位置 |
| 振镜启用开关 | 走 `EnableGalvoWeave` |

**工艺设置 · 自适应工艺参数**

| 控件 | 说明 |
|---|---|
| 接头类型下拉 | **20 类**，读 `jointtypelist.json`（`GetJointTypeName`） |
| 基准工艺参数组 | 光斑直径 / 激光功率 / 焊接速度 / 送丝速度 / 焊缝宽度 + 上下限 + 自适应灵敏度 |
| 焊丝直径 | 由基准工艺迁入 |
| 左侧工艺库列表 | 筛选按钮改「增加 / 删除」，选中行右键弹出 |
| ~~焊丝类型 / 板材材质~~ | ⛔ **删除** |
| ~~焊接调整段参数~~ | ⛔ **移除**，移交线激光设置（系统设置·轨迹跟踪）承接 |

**系统设置 · 轨迹跟踪**

| 控件 | 来源 |
|---|---|
| 轨迹点参数 21 项 | 迁移 `txtGeoRobotYFilterAlpha` 等 |
| Y 轴表 19 列 | 迁移 `tableAxis`（仅渲染 Y 向） |
| 线激光参数 10 项 | **跨页迁入**（决策 30） |

**系统设置 · 激光头控制**（内部设置，**Admin 专属，默认隐藏**）

| 控件 | 说明 |
|---|---|
| TA 力矩参数 | 目标力矩 / Slope / 限位 |
| LA 电机参数 | **量纲 `MotorPulsePerMm`** / 使能 / 斜坡 |
| 振镜内部参数 | 频率 / 宽度 / 长度 / 角度 / 起止角 / 中心 / 压缩 / 使能 / 目标尺寸 |
| **振镜逻辑零位** | 「回到零位」按钮 + 状态显示 |
| TA/LA 曲线标定入口 | 只读展示 + 输入表格导入 |
| 光丝对中阈值 | 警告 0.1mm / 报警 0.3mm |

**系统设置 · 温度监测**（**Admin 专属，默认隐藏**）

| 控件 | 说明 |
|---|---|
| 保护镜温度 | WSX `0x6000` Sub1 |
| 保护镜腔体温度 | Sub2 |
| 保护镜温升 | Sub3 |
| 切割气压 | Sub4 |
| 上下限阈值 | 写 `0x7020` Sub1~6 |
| **部件位置示意图** | ⚠️ **占位待补**（资源制作中，不阻塞） |

**相机设置 · 监控相机**

| 控件 | 说明 |
|---|---|
| 光丝对中报警阈值 | 需求 33 |

### 4.3 权限门控范围

| 范围 | 可见性 | 写权限 |
|---|---|---|
| 工艺设置全部三板块 | 所有人 | 所有人 |
| 系统设置·轨迹跟踪 | 所有人 | 所有人 |
| 系统设置·激光头控制 | **仅 `OperateLevel.Admin`** | **仅 Admin**（Load 期二次校验，防越权写入） |
| 系统设置·温度监测 | **仅 Admin** | **仅 Admin** |
| 监控相机页光丝对中阈值 | **仅 Admin** | 仅 Admin |

⚠️ **隐藏 ≠ 禁用**：非 Admin 若能通过加载回填看到值即等于未隐藏；保存前须二次校验权限。

> ✅ **2026-10-08 S-11 执行记录**：上表「系统设置·激光头控制」与「温度监测」两页已在本轮合并为**单页「激光头系统参数设置」**（见 S-10 第二轮），
> 故门控对象为 `tabPageLaserHeadParam`（含 `panelOpticsSys` + `panelTempSys`）。三层防线已落地：
> 显示层 `Visible=false` + 两面板 `Enabled=false` · 进入层 `tabsSystem.SelectedIndexChanged` 切页二次校验 · 写入层 `EnsureAdminForWrite`。
> 另「监控相机页光丝对中阈值」**控件尚不存在**（属需求 33；⚠️ 原预测编号 ADR-057 已被 2026-10-09 批E 的 [[decisions/ADR-057-TaLaActionAndFollowControl]] 占用，需求 33 的 ADR 顺延取号，以 ADR-Index 为准），门控随控件落地一并接入。
> **权限等级裁定补充**：调试测试需最高权限 ⇒ 程序启动默认 `Admin`（原为 `Operator`），用「注销」降为 `Operator` 核对门控。

### 4.4 主页面与数据追溯

| 页面 | 控件 | 说明 |
|---|---|---|
| MainPage | 折线图选项 | 4 Checkbox → **单选**；5 项：接头宽（替代「焊缝宽度」文案）/ 激光输入输出 / 送丝输入输出 / Y轴位置 / 送丝Z轴位置 |
| MainPage | 状态栏 | 改报警信息（去「设备状态：」前缀与枚举直出） |
| MainPage | 模组面板 | 6 项 → **4 项**（线激光 / 监控相机 / 控制器 / 机器人） |
| MainPage | 光丝对中状态区 | **新增**，三态可见（正常/黄灯/红灯） |
| DataReviewerPage | 时间筛选 | DatePicker → **区间** |
| DataReviewerPage | 筛选栏 | **新增** 全选 / 全取消 / 反选 |
| DataReviewerPage | 列表 | 增**多选列**（`ColumnCheck` + `SetAutoCheck(false)` 范式） |
| DataReviewerPage | 右侧图表 | ✅ **已落地**：7 平铺 Checkbox → **`Select` 五大类模组**（接头 / 激光头（Y轴·Z轴·摆动宽度·温度）/ 机器人（Y·Z·速度）/ 送丝机 / 激光器功率），每模组独立 Checkbox 多选。⛔ 不含 RobotX（它是横轴）。见 [[decisions/ADR-056-DataReviewRangeFilterAndModularMultiSelect]] §5 |
| DataReviewerPage | 图表交互 | **悬停显示数值**（指针进点 18px 内才显示该点 X/Y，移开即清） |

---

## ⑤ ADR 清单

### 5.1 新增（**068~074**，接 ADR-Index 现行有效段 001~051）

| 编号 | 标题 | 核心裁定 | 影响 No |
|---|---|---|---|
| **ADR-054** | 主页面选项单选与报警信息语义 | 折线图选项改单选 + 5 项内容（接头宽替代焊缝宽度、激光/送丝输入输出、Y轴位置、送丝Z轴位置）；状态栏改报警信息；模组收敛 4 项 | 1,2,3,4,5 |
| **ADR-055 → 实际 072** | 数据追溯区间筛选与模组化多选 | 日历天→时间区间；列表多选列（表头全选）；右侧图表按五大类模组化（`Select` 分选）；悬停命中点才显示数值 | 6~12 ✅ **已全部落地** |
| **ADR-052** | 生产记录 Schema 扩展 | `WeldActionRecord` 增 5 字段；写侧+读侧+旧记录回落三点同批；列名抽 `CsvHeader` 常量 | 9,11,32 |
| **ADR-056** | 工艺设置三板块重整与接头参数驱动 | 三板块重排；TA/LA 动作指令；接头类型接 20 类（弃 `EmguALG.JointType` 死代码）；删 `WireType`/`PlateType`；启用线激光引导收敛到快速设置 | 13~22,26~28 |
| **ADR-057** | 光丝对中毫米化与三级报警 | 两套算法合并为一套并毫米化；X 向送丝机补偿、Y 向仅三级报警（0.1/0.3）不自动调整；报警统一走 `ReportAlarm`；偏差驱动振镜中心微调 | 33~37 |
| **ADR-058** | 温控闭环与振镜参数功能二分 | 温控按 WSX `0x6000` 四项 + 订阅 `TemperatureAlarm` + 上下限（示意图占位）；振镜内部参数→系统设置 / 功能图形→工艺设置；逻辑零位；运行期消费方 + `EnableGalvoWeave` | 23,24,32 |
| **ADR-053** | TA/LA 标定曲线与 WSX 电机量纲 | 曲线A/B 内置默认线性组（LA=0↔0.6mm；TA=0↔偏移0），**采样点表非公式**；交付曲线输入表格模板；`MotorPulsePerMm` 默认 10 可配置；量纲换算单一入口 | 20,21,22,41 |

### 5.2 就地补正（不改编号）

| 页面 | 补正内容 |
|---|---|
| **ADR-030** | 「对焦轴归运控」结论**变更**：LA 不再是运控轴，改由 WSX 从站 `0x7000`/`0x6020` 电机对象实现；轴表 `Z向对焦电机` 废止。**振镜边界（归从站 OD）维持不变** |
| **ADR-042** | 补振镜摆幅运行期消费链路 + **摆幅公式 `宽度×(1+k)`（k 可配置默认 0.2，业主 Q5 裁定）** + 查表覆盖机制 + 逻辑零位；补 `FillXlOutput` 支路硬编码；替代 `CalcGalvoAmplitude` 恒 0 占位。**⚠️ 本条就摆幅计算规则就地裁定公式，取代「纯查表」原规划**（红线针对「AI 自创公式」，业主给定规则不属此列，详见 3.4） |

### 5.5 结构变更申请 #2（2026-10-08 P2 落地时提出，未就地执行）

> 冻结规则：本页结构已定稿，P2 只可追加不可挪位。以下为落地时**发现范围与规划不符**的项，
> 按规则**记申请回 P1 评估，不在 P2 就地改**。

**申请内容**：P1 §2.3 与 §4.1 规划的「工艺设置 4→3 页」与「`tabPageLaserProcess` 整页跨迁到系统设置·轨迹跟踪」，**实际是跨页功能搬迁，不是重命名**。Phase 0 实测规模：

| 项 | 实测量 | 说明 |
|---|---|---|
| 待迁控件 | **27 个子控件 + `panel1` + `tbpanelweldponts`** | 装在 `TableLayoutPanel`（6 列 × 11 行）内 |
| Designer 段 | 约 **240 行**（`ProcessControlPage.Designer.cs:1079~1320`） | 容器自带行列布局，**内部 27 项坐标一个都不用改** |
| 绑定代码 | `ProcessControlPage.cs:224/226/227/243/245/246` 等 | 读写 `txtCalibCenterY` / `txtCalibCenterZ` / `txtCalibAngle` 等 |
| 落地侧改动 | 需并入 `SystemControlPage` 的 `LoadConfig` / `SaveConfig` | 目标页的 `tabsSystem` 已满 4 页，要并入 `tabPageTrajectoryParam` |

**处置（本轮实际执行）**：业主 2026-10-08 选择「**保持内联 TabPage，只重命名与调整归属**」，
故本轮只做变量改名 + Text 改名 + 页序核对，**未搬任何控件、未改任何绑定代码**。

**待业主后续裁定**（二选一）：
| 选项 | 内容 | 代价 |
|---|---|---|
| **A. 执行搬迁** | 27 控件 + `panel1` + `tbpanelweldponts` 整体移入 `tabPageTrajectoryParam`；绑定代码从 `ProcessControlPage.cs` 迁到 `SystemControlPage.cs`；工艺设置页真正变 3 页 | 需单独一轮；改 Designer 大段控件树 + 跨页配置读写 |
| **B. 撤销搬迁** | 工艺设置保留 4 页，「线激光追踪工艺设置」留在工艺设置；§2.3 与 §4.1 相应修订 | 零代码；但与业主「参数归系统设置」的分工口径不符，需重新确认归属 |

> ⛔ **本项不阻塞后续**：现状（4 页 + 线激光标定在工艺设置）是**改动前的既有状态**，功能完整、可运行。

### 5.4 编号冲突修正（2026-10-08 P2 落地时发现）

⚠️ **本库存在两套 ADR 编号空间**，P1 原规划未察觉：

| 编号段 | 性质 | 占用情况 |
|---|---|---|
| **001~051** | 现行有效 ADR（有独立页面） | 连续无断号 |
| **052~067** | **旧编号段**（2026-09-23 精简合并时保留在 `ADR-Index` 映射表中，均标注「并入 ADR-0XX」） | **已占位，不是现行 ADR** |

**冲突实证**：P1 §5.1 原规划 052~058，其中 052/053/054/058 **全部落在旧编号段内** —— `ADR-Index.md` 已把 `054` 记为「输出整形换轨一阶跟随」、`058` 记为「Y 轴速度前馈算法口」（并入 ADR-042）。按「编号唯一准绳 = `ADR-Index`」裁定：**新号取 068 起**。

**修正后编号**：

| 新号 | 主题 | P1 原编号 |
|---|---|---|
| ADR-052 | 生产记录 Schema 扩展 | 054 |
| ADR-053 | TA/LA 标定曲线与 WSX 电机量纲 | 058 |
| ADR-054 | 主页面选项单选与报警信息语义 | 052 |
| ADR-055 | 数据追溯区间筛选与模组化多选 | 053 |
| ADR-056 | 工艺设置三板块重整与接头参数驱动 | 055 |
| ADR-057 | 光丝对中毫米化与三级报警 | 056 |
| ADR-058 | 温控闭环与振镜参数功能二分 | 057 |

> ⛔ **新增 ADR 前的必做动作**：查 `wiki/decisions/ADR-Index.md` 的**旧→新映射表**（不只现行有效表），确认目标号未被旧编号占用。

---

### 5.3 编号冲突检查

ADR-Index 现状 **001~051 连续无空洞**；本轮新增自 **068** 起（⛔ 跳过旧编号段 052~067 —— 见下方编号冲突修正）。

⚠️ 新增 ADR 须同步 4 处：`ADR-Index.md`（表 + 头部说明）×2、`index.md` §7.0 编号总表 + §7.1 现行有效表 + §7.0b 全量登记表。计数不一致即治理违规。

---

## ⑥ 遗留待确认（业主 2026-10-08 已全部答复）

| # | 事项 | 业主答复 | 落地影响 |
|---|---|---|---|
| ~~Q1~~ | 模拟测试页归属 | **归属系统设置，单开一页** | `tabsSystem` 维持 **4 页**；现有完整功能不迁、不拆（ADR-032 现状） |
| ~~Q2~~ | WSX 电机 `0x7000` 计数↔mm 量纲 | **确认 10:1mm** | 落为 `MotorPulsePerMm` 默认值 **10**，可配置；换算**单一入口**防量纲变更漏改 |
| ~~Q3~~ | `ToleranceAngle` 纳入判定 or 删除 | **见下方专项说明**（业主反问，已查清并答复） | 判定式 `|dx|≤TolX && |dy|≤TolY` 不含角度；**纳入角度判定**（焊丝倾角属对中合格要件） |
| ~~Q4~~ | 温控部件清单 | **确认，按 WSX 表格执行** | 四项（保护镜温度/腔体温度/温升/切割气压）+ Sub11 状态位；阈值写 `0x7020` Sub1~6；示意图位仍占位 |
| ~~Q5~~ | 摆幅宽度映射 | **摆幅宽度 = 焊缝宽度 × (1+k)，k 可配置默认 0.2** | 落为 `WEAVE_AMPLITUDE_K` 四点闭环 + 查表覆盖机制（见 3.4） |

### Q3 专项：`ToleranceAngle` 是什么（业主反问专项答复）

**定义**：`WireFeedConfig.cs:16` `public double ToleranceAngle { get; set; }`，默认 **2.0 度**，注释「角度容差（度）」。配套的结果字段是 `WireFeedResult.AngleDeg`（角度偏差，度）。

**它本该管什么**：焊丝**不该是斜的**。光斑是圆的、焊丝是细长条，理想状态下焊丝尖端应该垂直指向光斑中心；如果焊丝歪了（送丝嘴角度偏、丝有弯折），即使尖端 XY 位置在容差内，**实际焊接点也会偏离**。所以「对中合格」本应三条件同时满足：X 偏差、Y 偏差、**倾角**。

**现状（实测）**：

| 位置 | 情况 |
|---|---|
| `ImageAlgorithm.cs:654` 在用判定式 | `bool aligned = Math.Abs(dx) <= config.ToleranceX && Math.Abs(dy) <= config.ToleranceY;` —— ⛔ **只有 X/Y 两个条件，没有角度** |
| `AngleDeg` | 已在算、并在 `info` 文本里显示（「偏移X … 角度 … 对中 OK/NG」）—— **只报告不判定** |
| `AlgorithmManager.cs:169/190` | INI 读写该键（段 `Alignment`，键 `ToleranceAngle`）⇒ **配置项存在且可改，但改了不生效** |
| 死代码套 `CheckCentering` | 也不含角度判定（只有 X/Z 偏差 + 三级分级） |

**结论**：这是一个**「配置存在、值可改、但判定式没接入」**的历史遗留项——典型的「0 消费者」半成品。

**建议（P1 裁定）**：**纳入判定**，三条件与：

```
对中合格 = |dx| ≤ ToleranceX  &&  |dy| ≤ ToleranceY  &&  |AngleDeg| ≤ ToleranceAngle
```

理由：需求 36 要求「精度 ±0.02mm」，单靠 XY 容差无法约束倾角；且该值已在算、已在显示、已可配，**接入判定零新增成本**，只需改判定式一行。

⚠️ 若业主要求「焊丝允许一定倾角」（如大电流工况下丝有轻微摆动），则改为**放宽阈值**而非删除——阈值可配置正是为此保留的。**若现场实测 AngleDeg 波动远大于 2°，接入会导致长期 NG**，故 P2 落地时先以「只记录 + 主界面可见」过渡，现场标定出真实波动范围后再收紧为判据。

---

## ⑦ 遗留（不阻塞 P2）

| # | 事项 | 说明 |
|---|---|---|
| R1 | 温控**部件位置示意图资源** | 制作中，已设占位位，不阻塞数值面板与阈值配置 |
| R2 | WSX 电机**厂商确认量纲** | 业主已确认 10:1mm；仍建议上机前与厂商复核一次（O(1) 工作，配置化后改动成本低） |
| R3 | 摆幅**现场标定值** | 公式 `宽度×(1+k)` 为默认；角焊缝/复杂接头建议录入 `AutoParamHelper` 第 6 列覆盖 |
| R4 | `AngleDeg` 实测波动范围 | 决定 Q3 何时从「只记录」收紧为「参与判定」 |

---

## ⑧ 自校验结果（业主答复后复跑）

| 检查项 | 结果 |
|---|---|
| 硬件矩阵无「待定」格 | ✅ 8 行全部有裁定（Q2 已确认量纲） |
| 新增文件落点唯一（ADR-005 目录即命名空间） | ✅ 6 个文件各有唯一落点 |
| csproj 登记清单完整 | ✅ 6 文件 × 3 条（UI 类） |
| 配置键无重复 | ✅ **9 键**唯一（新增 `WEAVE_AMPLITUDE_K`）；删除 2 键 + 迁移 1 键已列 |
| 记录字段与数据源对应 | ✅ 5 字段各有来源 |
| **页面控件无重复归属** | ✅ 七板块（六 + 模拟测试独立页）控件互斥 |
| ADR 编号无冲突 | ⚠️ **原规划 052~058 与旧编号段冲突，已改号 068~074**（详见 §5.4） |
| 曲线为采样点表非公式 | ✅ 符合 ADR-043 红线（曲线**不含**摆幅） |
| **摆幅公式与 ADR-043 红线的关系已记录** | ✅ 业主裁定公式，非 AI 自创；保留查表覆盖口子（见 3.4） |
| 权限门控范围明确 | ✅ 2 板块 Admin 专属 + 写权限二次校验 |
| 业主五项答复已全部落位 | ✅ Q1~Q5 逐条对应到具体章节 |

---

## 相关页面

- [[architecture/CodeMap]] —— 本表全部代码落点的来源
- [[project/vibecoding-workflow]] —— P1/P2/P3 分层与冻结机制
- [[decisions/ADR-Index]] —— ADR 编号唯一准绳
- [[decisions/ADR-030-WeldHeadSlaveDeviceUnderMotionControl]] · [[decisions/ADR-042-SeamTrackingConsolidated]] · [[decisions/ADR-043-WeldParamControlConsolidated]] · [[decisions/ADR-005-NamespaceDirectoryAlignment]] · [[decisions/ADR-033-ConfigArchitectureStandard]]
