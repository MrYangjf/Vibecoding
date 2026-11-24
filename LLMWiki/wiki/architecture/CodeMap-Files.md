---
title: CodeMap-Files — 代码地图详表（文件↔职责，含沿革存档）
date: 2026-11-17
updated: 2026-11-17
tags: [代码地图, 索引, 架构, 详表]
status: accepted
---

# CodeMap-Files — 代码地图详表

> ⚠️ **历史名称提示**
> 本页为**手写逐文件详表**，已由机器生成的代码地图取代（2026-11-18）：
> · 模块骨架 + 定位陷阱 → [[architecture/CodeMap]]
> · 逐类 → `文件:行` → 成员签名 → `CodeMap-Symbols-<模块>.md` 分片
> · 影响面（谁调用谁）→ [[architecture/CodeMap-Relations]] 及方法级分片
> 本页保留仅供历史追溯；⛔ **不再维护、不得作为现行定位依据**。

> 本页是 [[architecture/CodeMap]] 总览的**详表分页**：按命名空间列出全部源码文件的职责。
> 总览页提供一页可读的「代码记忆卡 + 主干依附」，本页提供逐文件检索。
> ⛔ 本页只做**定位索引 + 一句话职责 + 状态标记**；沿革段落为历史存档，不作为现行职责依据（现行职责看每格首句）。

## 一、按命名空间的功能地图（Phase 0 入口）

> 按代码行数降序。**行数大 = 耦合高 = 读之前先看本表的功能定位，不要整文件通读**。

### `AdaWeldSystem`

- **功能**：程序入口 · 根命名空间（仅 Program.cs）
- **规模**：1 文件 / 32 行
- **模块归属**：（无专属模块页，见功能描述）
- **约束 ADR**：ADR-001

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `Program.cs` | 32 | class Program | 程序 Main 入口：AntdUI 启动与全局异常兜底 |

### `AdaWeldSystem.MainDeviceControl.DeviceWorkflow`

- **功能**：主控 · 五个模组工作流
- **规模**：5 文件 / 5201 行
- **模块归属**：[[modules/DeviceControl]]
- **约束 ADR**：ADR-016/038/041/044

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` | 3367 | class MotionControlWorkflow | 运控工作流（最大单文件）：CSP 写段逐拍、缓冲收尾、回标定位、收工语义、运控轴范围。**2026-10-09 ADR-055**：`MotionControlPhase` 枚举与 `_phase` 已删，`IsRunning` 改判 `MontionAxis.IsServoOn()`；**2026-10-10 ADR-061**：`WeldStatusTrans` 恒假条件修复（停焊沿分支恢复可达）+ `SubDeviceLog` 格式串 5占位→4占位 📄（CSP 写段逐拍、缓冲收尾、回标定位、收工语义、运控轴范围）；**2026-11-16**：CSP 查图 X 改取 `WeldParamManager.CurrentRobotX` 与入图键同源（修复 D21），保留 `_cspQueryXFromWeldParam` 回退开关 |
| `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` | 969 | class LineLaserWorkflow | 线激光工作流：分步 switch-case + 采样节拍 + 稳定性判定。**五个 workflow 的基准实现**（零自建状态枚举、零私有状态字段）📄 📄 |
| `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs` | 659 | class WeldParamControlWorkflow | 焊参工作流：功率/送丝/速度/摆幅计算与下发。**2026-10-09 ADR-055**：自建枚举与 `_phase` 已删；⛔ 原来内嵌的 `WeldParamOutput` 已迁至 `WeldParamData.cs` 并改名 `WeldParamAdaptControl`；**2026-10-10 ADR-061**：`WeldStatusTrans` 恒假镜像分支删除（单源化后无存在基础）；**2026-10-20**：`CalcGalvoAmplitude` 改「固定输出光斑模式返 0 / 非固定模式查表摆幅宽度 → 公式兜底」；**2026-10-21**：增 `CalcGalvoFrequency`（查表 → 基准公式兜底），两支路同源填 `GalvoFrequency`；**2026-11-18 ADR-103 落地演进**：`TickXlOutput` 时间维节流（`Environment.TickCount`+`intervalMs`）⇒ **距离维节流**（机器人 X 位移达 `SegmentDistanceMm` 才输出，首拍立即输出），`ParamOutputHz` 已删 ⇒ 阈值复用同一把距离尺 |
| `MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs` | 679 | class MonitorCameraWorkflow ; class MonitorResult | 监控相机工作流：采集→分析→填充结果；对中/质量两相位；剪丝异常标志位产出方。**2026-10-09 ADR-055**：`MonitorWorkflowState` 与 `_flowState` 已删；⚠️ `_phase` 是 **`MonitorCameraPhase` 算法相位**（`MonitorResult.Phase` 数据源）**保留**；**2026-11-09 ADR-095/096/097**：检测直调 `AlgorithmManager.Instance.Detect*`、三条失败文案引用 `DescribeLastError`；新增 `StartRecording/StopRecording`（录像命名与前置判断归本层）；新增回放门面（9 方法 + 3 属性 + 7 转发事件，`StopPlayback` 与设备侧 `Stop` 分开） |
| `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs` | 620 | class PlaybackAlgorithm | **2026-11-09（ADR-097）**：回放算法（算法层，与 `WireFeedDistance` / `WeldQuality` 同级并排）——录像目录扫描、缩略图后台解码、`VideoCapture` 播放解码、时间基准/进度/暂停/倍速/±5 秒跳转；`AlgorithmManager.Playback` 惰性持有，跨页面共用，`Stop` 幂等、页面不 Dispose。行数据 `PlaybackFileInfo` / `PlaybackScanResult` 为同目录独立文件 |
| `EmguALG/RealtimeMonitor/Playback/PlaybackFileInfo.cs` | — | class PlaybackFileInfo | **2026-11-09**：回放列表行数据（算法层产出，UI 只绑定显示） |
| `EmguALG/RealtimeMonitor/Playback/PlaybackScanResult.cs` | — | class PlaybackScanResult | **2026-11-09**：一次区间扫描结果（行数据 + 结果文案 / 错误） |
| `EmguALG/Roi/ImageRoi.cs` | — | class ImageRoi | **2026-11-09 新增**：ROI 区域纯数据（启用标志 + X/Y/W/H + `ClampTo` / 坐标映射），不引用 WinForms、不绑控件 |
| `EmguALG/Roi/ImageRoiTool.cs` | — | static class ImageRoiTool | **2026-11-09 新增**：通用 ROI 工具——`Load/Save`（`Config/EmguALG/Algorithm_INI/ImageRoi.ini`，节 `ImageROI`）+ `Crop` / `ApplyMask`；场景未定，暂不接任何算法（按需加载） |
| `EmguALG/LineLaserContour/LineLaserContourData.cs` | — | class LineLaserProfileData ; class LineLaserCalibrationData ; struct LineLaserSeamFeature | **2026-11-09 新增**：线激光渲染的算法层 DTO（轮廓 Y/Z 数组 + 点数、标定四角、特征点），硬件层转换后传入，算法层不再引用 `LineLaserCam` / `PCLOperate` |
| `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` | 835 | class LaserWeldHeadWorkflow | 焊接头工作流：温控闭环（温度/报警事件 + 二次判阈）。ADR-055 状态枚举已删；ADR-072 删 `StepIdle` 重写；ADR-053/066 振镜频率与光斑来源。**2026-11-05 ADR-082**：`CheckTaAvailable` 降级；`TaZeroPose`（CSP 绝对定位）；**ADR-082**：`TaAuto` 去力矩门禁、先停 ZeroPose 再 `SetTorque` 自切 CST；`TaTorqueActive` 转发 `axis.TorqueOutputEnabled`；**ADR-084/085**：力值 N 按 `TA_FORCE_100PCT_N` 换算 CST 千分比、力大小与方向分离（负值拒绝）；**2026-11-05**：TA/LA 阻塞式状态检测 + 同轴单飞（ADR-063）；**2026-11-16 ADR-098**：TA 分层就绪 `IsEnabled=TaMotionReady`/`IsHomed=TaHomed`/`IsAtWorkZero=TaAvailable` |；**2026-11-18 ADR-070 演进**：删 `GalvoDemo()`（零调用方）⇒ 新增 `GalvoManualStart(pattern, shape)` / `GalvoManualStop()`（手动模式输出一次，⛔ 自动模式互斥）；**ADR-076 D3**：新增 `static ResolveGalvoPattern(int)`（配置 0=未设置/越界 ⇒ 逻辑零位直线，⛔ 禁下发协议非法值到 0x7010 子索引 1）；**2026-11-18 ADR-067 演进**：`LaPose2()` → `LaDefaultFocus()`（LA 默认焦平面 = LA 默认工作位）；新增 `MoveToDefaultFocus()`（初始化连接结束后自动就位，非阻塞、不走手动门禁）；**ADR-076 D4**：新增 `static IsGalvoWeaveEnabled()`（实时读 `cfg.EnableGalvoWeave`）并**删过期快照字段 `_galvoWeaveEnabled`**（原 `LoadConfig` 期取值，运行期改开关不刷新 ⇒ 改实时读，与 `WeldParamControlWorkflow.GetAmplitudeMm` 同口径）；图形语义前置条件 = 振镜是否启用（未启用⇒无图形；已启用⇒必有图形，无设置落回 Line 并落盘） |

### `AdaWeldSystem.Comm.Communication.Implementations`

- **功能**：通讯 · 各厂商通道实现
- **规模**：4 文件 / 2812 行
- **模块归属**：[[modules/Comm]]
- **约束 ADR**：ADR-025/026/027

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `Comm/Communication/Implementations/KukaRsiComm.cs` | 1437 | class KukaRsiComm ; enum RSIDataType ; enum RSIErrorType ; struct KUKAPosition ; class RsiRobotPacket ; class KUKARobotData ; class KUKACorrectionData ; class RSIDataEventArgs ; class RSIErrorEventArgs ; class RsiFormatAttribute ; class RsiFormatElement ; class RsiPacketFormat ; class RSIElement ; class RSIConfig ; class KUKAXMLConfig | **RSI 数值化通道**（UDP 12ms）：坐标+Tool 上行 + `RxCmd`/`RxPayload` 指令上行；回复 8 具名元素（功率/送丝/剪丝/速度/摆幅 + TxCmd/TxPayload/TxSeq）；占位符 11 项；**收发均格式文档驱动**；**一包一回**（收包信号驱动 SendLoop，禁盲发）；文本节点按标签分派 📄 |
| `Comm/Communication/Implementations/InLaserModbusComm.cs` | 744 | class InLaserModbusComm ; class ModbusErrorEventArgs ; class ILModbusData ; class ControlRegisters ; class ResultRegisters ; class ControlCommands ; class StatusValues ; class InspectResultValues ; class ILModbusInspectResult | 英莱激光器 Modbus RTU：0x13 设备温度、控制/结果寄存器 |
| `Comm/Communication/Implementations/EthernetXmlComm.cs` | 439 | class EthernetXmlComm ; class SstTcpServer ; class SstTcpClient |  |
| `Comm/Communication/Implementations/SiemensS7Comm.cs` | 192 | class SiemensS7Comm |  |

### `AdaWeldSystem.UIDesign.TabPage`

- **功能**：UI · 系统参数设置子页
- **规模**：5 文件 / 5674 行
- **模块归属**：[[modules/UIDesign]]
- **约束 ADR**：ADR-008/036/055/057

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `UIDesign/TabPage/SystemControlPage.cs` | 3197 | class SystemControlPage ; class AxisRow ; enum SimButtonMode | 系统设置页：轨迹/激光头/模拟测试；gridTrace 2×2（ADR-071/088）、轴表 11 列 + 固定按钮（ADR-073）、四区（ADR-075/093）、分区读存（ADR-076）、唯一 timerRefresh（ADR-075）；TA 区 `tableTa` 复用 `CreateAxisColumns()/FillAxisRuntime()` + `AxisConfigForm`（AXIS + TA_HOME，ADR-080）；`tLPTimeout` 超时卡片含「主站初始化(秒)」项（`txtMasterInit`↔`MasterInitSeconds`，读改存三段式）；见 [[api/SystemControlPage]] |
| `UIDesign/TabPage/FilebackupPage.cs` | 2191 | class FilebackupPage ; class TxCmdOption ; class AxisConfigPreviewRow ; class IoConfigPreviewRow ; class CylinderConfigPreviewRow | 文档备份设置页：通讯配置 + 系统配置两页签（ADR-079）；职能收口 + 项目 XML 每切视图重读盘 + 列宽 1283；表格可编辑：`CellEndEdit`(bool) 写回 + ContextMenuStrip 增删行/反向 CSV + `_viewDirty[4]` 脏标记 + `ValidateCurrentTables(out hints)`；**只校验脏视图**（`MergeView` 脏阻断/未编辑仅提示，焊接头唯一键 = `BuildPdoObjectKey` 复合键，变量名重复非错误）；保存 5 行 / 备份一次 / `ReloadDeltaConfigOnly()` 只重载台达四块；见 [[api/FilebackupPage]] |
| `UIDesign/TabPage/ILCamPage.cs` | 649 | class ILCamPage ; enum RefreshUiScope ; class InspectResultRow ; class CmbJobItem | 线激光设置页（并入系统参数设置导航，tabs：线激光采集设置，ADR-051） |
| `UIDesign/TabPage/MonitorCamPage.cs` | 1233 | class MonitorCamPage ; class PlaybackRow ; class PlayScanOutcome | 监控相机页 tabs：焊接相机设置 + 焊接回放（ADR-048/078）；回放 = **日期区间汇总**（`GetDirectories` 一层过滤 `yyyyMMdd` → 每个日期目录 `GetFiles("*.avi", TopDirectoryOnly)` 汇总，表格只出文件行，无日期/扫描文件夹层，`RunPlayScan` 后台线程 + 代数取消）+ 悬停双层播放控件栏；**2026-11-03 时间基准驱动**：`Stopwatch` + 锚点（`TargetPlayFrame`/`RebasePlayClock`）替代每拍固定加帧，1.0x 实测 9.07s/9s；**2026-11-03**：初始化不读盘，首切「焊接回放」才首扫，反复切页幂等；**2026-11-02**：回放页四层 GridPanel 化（回放区零原生布局容器）；**2026-11-09**：对中阈值迁入 `grpParam`（仅 Admin） |
| `UIDesign/TabPage/ProcessControlPage.cs` | 1931 | class ProcessControlPage ; class ConfigListRow | 工艺设置页 3 tabs；批M GridPanel（ADR-071）；LA 对焦(`tlPLASetting`)/振镜(`gridQuickLa`)各自容器独立单选；⑤输出 11 控件入 gridAdaparam（ADR-072/089）；ADR-076 分区落盘；ADR-063：三指令区默认 Auto + `RefreshActionStates` 置灰；**ADR-082**：增 `radioQuickTaZeroPose`（互斥；2026-11-09 删 `CancelTaZeroPose`），`TaAvailable` 置灰其余；**ADR-082**：删力矩门禁与 `TaTorqueModeChanged` 订阅，`DoTaAuto` 直调 `TaAuto`；**ADR-084**：下压力按 N 校验并按 100% 力量基准换算；**ADR-084**：力值只填大小（负号拒绝）、回填取绝对值、方向只读 `TA_TORQUE_DIRECTION`；**2026-11-05**：指令区加初始化闸门、后台检测线程 + `BeginInvoke`、上色改 `BackColor`；**2026-11-18**：GA 设置区删 `selGalvoPattern`/`lblGalvoPattern`/`btnGalvoDemo`/`btnGalvoHome`，图形选择唯一入口 = GA 指令 Radio（`SetGalvoPattern` 单入口落 ④Preset 区），删 `selGalvoPattern_SelectedIndexChanged` 与两个孤儿按钮处理器，保留 workflow 层 `GalvoDemo`/`GalvoHome` |；；**2026-11-18 ADR-076 D6**：跟踪几何 7 项（轴/激光比例·偏差方向·激光超前量·机器人Y补偿·示教Y锁定·标定中心Y/Z）+ 标定角度迁入系统设置页·轨迹跟踪·标定参数区；工艺页不再落 ①System 区（XML 归轨迹跟踪 TabPage 独占）（控件/文案/配置项 `LaDefaultFocusMm`/INI 键 `LA_DEFAULT_FOCUS_MM` + 旧键一次性迁移）；**ADR-076 D3**：图形语义收敛（配置 0=未设置 ⇒ UI **不预选**任何 Radio，映射 `default` 返 null 不静默落直线）+ 删冗余 `_syncingLaRadios`（被 `_loadingGalvoUi` 覆盖）与字段 `_galvoPatternSelected`（写后无读者，；**ADR-070 演进（2026-11-18）**：GA 宽/长/频**按图形分 4 档**（`WeldHeadConfig.GalvoShapePresets`，XML `GALVO/<图形>/`，缺档回退 Line 档）；GA 区新增「手动下发/关闭退出」按钮组（`btnGalvoManualStart/Stop`，手动模式输出一次，⛔ 自动焊接中互斥置灰）；⛔ 删 GA 卡 `txtManualWidth`/`lblManualWidth` 与轨迹点区 3 个输出控件（光斑系数/输出频率/手动宽度） |

### `AdaWeldSystem.MainDeviceControl`

- **功能**：主控层 · 整机编排
- **规模**：2 文件 / 3622 行
- **模块归属**：[[modules/DeviceControl]]
- **约束 ADR**：ADR-013/014/017/038/041

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `MainDeviceControl/DeviceControlWork.cs` | 3964 | class MainDeviceStatusChangedEventArgs ; class SimulationStoppedEventArgs ; class MachineAlarmInfo ; class DeviceControlWork | 整机唯一编排：ExecuteIo、CascadeWeldStatus、模拟开关、SendRobotCommand、ReportAlarm、MonitorAlignTick + ComposeWireFeedSpeed；ADR-061：CascadeWeldStatus 末尾接 WeldStatusTrans；`InitStepRobotComm` 有 `IsUiReady` 门控 + `RxCmd` 去重 📄；ADR-082 使能逐轴留痕并开初始化闸门；**2026-11-13**：`DisposeComponents` 关闭链改**同步** `CascadeDisconnect()`（⛔ 不再置位脉冲型 `Stop_IO` 指望扫描线程消费——线程随即被关，脉冲必丢 ⇒ 级联断开从未执行）；**2026-11-17 ADR-107 演进**：`InitializeMachine` 只置 `_initAccepted`+开 IO 线程+置 IoInit，5 模组线程与指令线程延后到初始化出结果三出口（Finish/抢占/EndInitWithoutChain）；见 [[api/DeviceControlWork]] |
| `MainDeviceControl/DeviceStatusWork.cs` | 789 | class DeviceStatusWork ; class SafetyFlow ; class SafetyInterlockResult ; class SafetyInterlockChecker | 安全与状态巡检三线程：IO 扫描 / 急停 / 灯光；SafetyInterlockChecker 报警源判定中心；**ADR-091（2026-11-06）**：`ScanTaPositionLimit` 与 `_taLimitAlarmActive` 整段删除（越限撤力会打断力矩下压）；**2026-11-17**：IOWork 初始化在途时只推进连接链、冻结互锁/一致性/对齐等全部状态变更 |

### `AdaWeldSystem.MotionControl.DeltaEtherCAT`

- **功能**：运控 · 台达 EtherCAT 三层
- **规模**：14 文件 / 6039 行
- **模块归属**：[[modules/MotionControl]]
- **约束 ADR**：ADR-027/030/040/079

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` | 1288 | class DeltaMontionAxis | 台达轴运行时：CSP 绝对定位/扭矩 CST（失败回滚）/`Home_Config` 统一回零（`Home_Status=3` 拦截）；**2026-11-05**：P1.087/088 写读链路整段删除，-3 判据移交驱动器默认参数（ADR-080 §D6）；**ADR-082** `RunZeroPose` 容差到位；~~ADR-082 复用扭矩三条件~~ **2026-11-06 删除**；**2026-11-05**：`RunZeroPose` 增带取消重载，`WaitZeroPose` 超时上限 60s（ADR-082 演进）；**2026-11-10（ADR-087 演进）**：`SetTorque` 冷启动 = 位置停稳 → 切 CST → 目标+slope → 开输出（删 ±1‰ 同号种子）；热切换同号直接重发，反号走 `ReverseTorqueOutput`（撤输出 → 锁当前位切 CSP → Stop 停稳 → 切 CST → 反向目标 → 开输出；2026-11-10 第三次调整，原 2 条待裁定已按实测收口） |
| `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs` | 109 | class DeltaTaHomeConfig | TA 扭矩回零参数组：`HomeMode/HomeFirstVel/HomeSecondVel/HomeAcc`（**2026-11-05 删 `DetectTorquePercent`/`StopArrivalMs`**）；默认模式 -3；`CopyFrom/CopyTo` 做 AXIS 旧文件 seed 与保存镜像（Y 轴不参与，ADR-080）；`ZeroPoseMm`（工作零位坐标，默认 0；⛔ `CopyFrom/CopyTo` 不镜像；**2026-11-06 仅作迁移源，运行期读工艺 INI `TA_ZERO_POSE_MM`**）；**ADR-084**：增 `Force100PctN`（默认 37N）；**ADR-084**：增 `TorqueDirection`（±1，setter 归一，默认 +1）与内存态 `TorqueDirectionKeyPresent`（仅迁移判定、不落盘）；**ADR-091**：删 `ZeroPoseVelMmPerSec`/`ZeroPoseTolMm`（速度/容差复用 TA_Pose1/2 同源） |
| `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` | 1228 | class WeldHeadSlaveConfig ; class DeltaCylinderConfig ; class DeltaMotionConfig | 运控配置：AXES/INPUTS/OUTPUTS/CYLINDERS/WELD_HEAD_SLAVE/SEAM_TRACK/**TA_HOME** 七段+轴表 CRUD；`TaHome` 独立组（缺节点从 TA AXIS seed、保存镜像回 TA）；`SaveConfig` 备份+改名日志；`SaveConfig(backupFolder)` 非空=批量保存；**ADR-091** 工作零位仅留 `TA_HOME_ZERO_POSE_MM`（`_VEL`/`_TOL_MM` 已删）；**ADR-084** 增 `TA_FORCE_100PCT_N`（缺键默认 37）；**ADR-084** 增 `TA_TORQUE_DIRECTION`（缺键+1）；**ADR-086**：`LoadConfig(writeLog, allowHeal)` 预览零写，`SelfHealMissingKeys` 补缺（方向延后合并一次写盘）；**11-16**：轴组/TA_HOME 增已配置/未配置 Debug；**11-17**：轴参数/TA_HOME/流程超时/设备侧等待四处日志受 `writeLog` 门控，预览读静默不再重复刷屏 |
| `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` | 723 | class MotionConfigImporter | 轴/IO/缸三张 CSV 导入导出（IO 输入输出合表，用 IO_TYPE 列区分）；2026-11-03 分节重载 `Import(dir, bool axes, bool ios, bool cylinders, string backupFolder, ref msg)`，缺文件节跳过并保留原配置；批量复用上层备份目录，摘要只随 msg 上抛（不再单独打印） |
| `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` | 1074 | enum ConfigDirectoryLevel ; class ConfigDirectoryScan ; class DeltaControllerConfigImporter | 配置文档 → 项目 XML：Scan 分级 + ESI 即台达从站文档 + IO 表↔ESI 交叉校验（只告警）；Generate 备份后分节导入写 WELD_HEAD_SLAVE + IO_MAP，`GetParseFailures` 拦半成品；ESI 取首个带 `ProductCode` 的 `Type`，回溯 `Device` 取 Name；`Generate(dir, pdoEntries, out msg)` 表格为提交源（公共 `GenerateCore`）；新增 `BuildPdoObjectKey` 复合键（PDO I/S → SDO I/S → 空），⛔ 不按变量名判（ADR-079） |
| `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` | 568 | class SystemConfigPackager | 整站配置包 `.awcfg`：Export/Import + manifest/scope/SHA256/原子替换/回滚；**2026-11-03 范围反转** `scope=full-settings`，`Config/`+`DataBase/` 递归全量，仅排除 `Product.db`/`Auth.db`（含伴生文件）与 `Config\_import` （ADR-079） |
| `MotionControl/DeltaEtherCAT/XlsxSheetReader.cs` | 364 | class XlsxSheetReader | 自研 xlsx 只读解析（ZipFile + XDocument：sharedStrings / sheet1 / mergeCells），无第三方依赖；仅格式解析、不含列语义/协议常量（ADR-079） |
| `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` | 335 | class DeltaSlaveDevice | 通用从站通道：SdoRead/Write + PdoGet/Set（WSX 只经此访问对象字典） |
| `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs` | 288 | class DeltaMontionControl | 台达主站：`Master_Open`→`Master_Initial`（每卡）→轮询`Check_Initial_Done`→扫从站；**2026-11-13**：`Master_Initial` 返回非 0 **立即失败并上报卡号+返回码+描述**（原实现记哨兵卡号 99 后空等 30s 超时，掩盖真实原因）；`Get_CardSeq` 失败亦上报；新增 `_masterOpened` 标志（主站已打开但初始化失败时 `Close()` 仍执行 `Master_Reset`+`Master_Close`，主站不残留）；超时上限读 `FlowTimeoutSettings.Current.MasterInitSeconds` |
| `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs` | 209 | enum SlaveDeviceType ; class DeltaSlaveScanner ; class SlaveInfo | 从站扫描与身份识别（台达伺服 + WSX 焊接头；WSX 不当轴不进 AxisRegistry） |
| `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs` | 126 | class DeltaOutputIO |  |
| `MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs` | 128 | class DeltaAxisConfig | 单轴配置 22 属性（脉冲当量/速度/加减速/STime/回零/软限位 + TA 力矩 TorqueModeEnabled/TorqueTarget/TorqueSlope） |
| `MotionControl/DeltaEtherCAT/DeltaInputIO.cs` | 83 | class DeltaInputIO |  |
| `MotionControl/DeltaEtherCAT/DeltaIOConfig.cs` | 58 | class DeltaIOConfig |  |

### `AdaWeldSystem.ProductFileControl`

- **功能**：记录 · Manager
- **规模**：7 文件 / 3075 行
- **模块归属**：[[modules/SQLiteDatabase]]
- **约束 ADR**：ADR-031/037

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `ProductFileControl/Records/RecordFileStore.cs` | 1157 | class RecordFrame ; class RecordFileStore | 记录落盘与解析：ParsePDatRecords（列名内联无 Header 常量，旧记录回落待补） 📄 |
| `ProductFileControl/ProductFileRecordManager.cs` | 889 | class ProductFileRecordManager | 记录 Manager：按日分表查询 + 三份记录文件定位（.ply/.pDat/.csv） |
| `ProductFileControl/Abstractions/ProductRecordBase.cs` | 344 | class RecordItem ; class ContourFrameItem ; class WeldParamAdjustItem ; class WeldResultItem ; class ProductRecordBase |  |
| `ProductFileControl/Records/SeamTraceYRecord.cs` | 248 | class SeamTraceYPoint ; class SeamTraceYRecord | SeamTraceY 轨迹记录：5 列 BOM CSV，会话基名幂等（5 列常量在 :53） |
| `ProductFileControl/Records/WeldParamControlRecord.cs` | 239 | class WeldParamControlRecord ; class WeldActionRecord | 焊参控制记录：WeldActionRecord 15 字段（TA/LA/摆幅/温度字段待扩展） |
| `ProductFileControl/Records/LineLaserContourRecord.cs` | 91 | class LineLaserContourRecord |  |
| `ProductFileControl/Records/WeldResultRecord.cs` | 107 | class WeldResultRecord |  |

### `AdaWeldSystem.WeldParamControl`

- **功能**：焊参 · Manager 与配置
- **规模**：4 文件 / 3450 行
- **模块归属**：[[modules/WeldParamControl]]
- **约束 ADR**：ADR-033/043

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `WeldParamControl/WeldParamManager.cs` | 1613 | class WeldParamManager | 焊参 Manager：预测性位姿快照、ChartVar 数据源、配置加载、AutoParamHelper 持有；⑤工艺输出 5 facade 透传参数调整算法（ADR-072 §三②）；**2026-10-21** 增 `SwingFrequencyDic` facade + `TryLookupSwingFrequency`，移除 `WeaveTable` 持有；**同日增 `AnchorSpotMm` facade**（曲线A 锚点光斑，外部唯一读取口，ADR-053/ADR-066）📄；**ADR-084**：`TorqueTarget → TaForceN` 迁移按 `TaForceN = TorqueTarget × Force100PctN / 1000`，基准 ≤0 跳过并告警；**ADR-084**：迁移链末增 `NormalizeTaForceDirection`（旧负值 → 缺键置 -1 并取绝对值 / 有键以键值为准并告警）；**11-16**：新增缺值累计距离 `NoValueDistanceMm`/`NoValueSource`（只观测） |
| `WeldParamControl/WeldParamConfig.cs` | 1036 | enum SeamTrackingMode ; enum SeamWidthSource ; class WeldAlgorithmsConfig ; enum AlgorithmsZone | 焊参配置 55 属性 + 四点闭环（键常量/Load/Save/消费者）；含 6 项历史包袱；**2026-10-23（ADR-076）**：`MaxMapPoints` 的 XML 归属由 ④Preset 改 **①System**（UI 落点在系统设置页·线激光点过滤区，键路径 `SEAM_GUIDE/MAX_MAP_POINTS` 不变、存量文件兼容、Preset 区不再写该键）；**ADR-084**：`TaForceN` 单位为 N（非额定千分比），由 `LaserWeldHeadWorkflow.TaAuto` 按 100% 力量基准换算；**2026-11-16**：`NO_VALUE_TOLERANCE_MM` 默认 2.0→5.0，载入钳位 1~50mm、越界一条 Warning |；；**2026-11-18 ADR-076 D6/D7**：`SEAM_GUIDE` 几何 4 项由 ④Preset 区迁 ①System 区（XML 侧 Preset 分支整体删除，存量零迁移）；⛔ 删 `YAxisMinMm`/`YAxisMaxMm`（限幅改接轴软限位）（INI `LA_DEFAULT_FOCUS_MM`，旧键 `LA_POSE2_MM` 一次性迁移后停写）；**ADR-076 D3**：`GalvoPattern` 初值 3→**0=未设置（无图形）**，INI 越界归 0 + Warning（⛔ 不再静默回退直线）；**2026-11-18 ADR-076 D5**：⛔ 删 `SpotWidthGain`/`ManualSeamWidthMm`/`ParamOutputHz`（键常量+默认值+读写+钳位+保存+两层转发属性全清）⇒ ③Adapt 区只余「每段距离」 |
| `WeldParamControl/WeldParamData.cs` | 727 | enum WeldFlowStep ; class WeldFlowStepInfo ; class WeldFlowSteps ; class RobotWeldData ; class SeamCalData ; enum SeamType ; class WeldParamAdaptControl ; class WeldParamMontionControl ; class AutoParam ; class ChartVar ; class WeldProcessCompletedEventArgs ; class WeldFrameRecordEventArgs ; class WeldAdjustmentRecordEventArgs | 数据模型：RobotWeldData / SeamCalData / AutoParam / ChartVar（线程安全）+ `WeldParamAdaptControl` / `WeldParamMontionControl` + 焊接步条三件 + 3 个记录事件；`AutoParam` 含光斑摆幅系数 `SpotSwingGain`、摆幅宽度 `SwingWidth`、摆幅频率两点基准（2mm→500Hz / 10mm→200Hz） |
| └─（同上） | — | `class WeldParamAdaptControl ; class WeldParamMontionControl` | **2026-10-09 ADR-055**：参数类归位到此（自适应算法输出 / 主动控制轴位置） |
| `ConfigFileControl/Implementations/ConfigChangeLogger.cs` | 187 | class ConfigChangeLogger | **2026-11-19 改名**（原 `WeldParamChangeLogger`；已记录所有配置变更故去掉 WeldParam 前缀）： **2026-11-19 通用化**：日志标签可传（默认「配置变更」）；⛔ 解除对 `WeldAutoParamProfile`/`Newtonsoft` 的依赖（分段参数表审计迁至 `WeldParamProfileAudit`）。分段表差异审计（2026-10-21 增摆幅宽度/摆幅频率两行） |

### `AdaWeldSystem.WeldParamControl.Algorithms`

- **功能**：焊参 · 算法实现
- **规模**：5 文件 / 2564 行
- **模块归属**：[[modules/WeldParamControl]]
- **约束 ADR**：ADR-042/043

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` | 1060 | struct SeamMapPoint ; class TrackingAlarmEventArgs ; class SeamMapTrackingAlgorithm | 焊缝跟踪地图算法（最大算法文件 1087 行）：绝对目标 Yt=Ya1+dY、空间高斯+突变闸门、禁时间域低通 📄 |
| `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` | 643 | class WeldParamAdjustmentAlgorithm ; class XLPoint | 焊参调整算法：分段查表送丝/功率/速度；光斑宽度输出；⑤工艺输出属性收编（转发 _config，键/分区落盘兼容，ADR-072 §三②）；**2026-11-18**：Manual 源恒定宽度改取 GA 档（`ManualFixedWidthMm()`，⛔ 无 catch 静默返 0） |
| `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` | 378 | class SeamTrackingAlgorithm |  |
| `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs` | 367 | class WeldParamLookupAlgorithm | 查表算法：五张宽度档映射表（功率/送丝/速度/光斑宽/**摆幅宽度**/**摆幅频率**）+ `TryLookupSwingWidth`/`TryLookupSwingFrequency`（最近档容差 100）；摆幅频率初值由该档摆幅宽度按基准点反算（2026-10-21）；**2026-11-18 ADR-076 D5**：⛔ 删光斑宽度系数（`SetSpotWidthGain`/`_spotWidthGain`/`RefreshSpotWidthDic` 全清）⇒ 光斑宽 = 焊缝宽（乘 1.0 恒等，行为等价） |
| `WeldParamControl/Algorithms/SeamGuideSample.cs` | 63 | struct SeamGuideSample |  |

### `AdaWeldSystem.PCLOperate.Render`

- **功能**：点云 · 三维渲染与曲面重建
- **规模**：3 文件 / 2442 行
- **模块归属**：[[modules/Comm]]
- **约束 ADR**：ADR-035

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `PCLOperate/Render/PointCloudViewer.cs` | 1070 | class PointCloudViewer ; enum CameraControlMode | Helix3D 三维回溯渲染：点云/曲面显示 + 相机控制 📄 |
| `PCLOperate/Render/SurfaceTriangulator.cs` | 952 | class SurfaceTriangulator ; class VectorMath ; class SpatialIndex | 曲面重建算法：BallPivoting / AlphaShape / Delaunay3D / Poisson / MLS 📄 |
| `PCLOperate/Render/RenderConfig.cs` | 420 | enum SurfaceRenderAlgorithm ; class RenderConfig |  |

### `AdaWeldSystem.EmguALG.Core`

- **功能**：图像算法 · 核心算子
- **规模**：9 文件 / 1917 行
- **模块归属**：[[modules/EmguALG]]
- **约束 ADR**：ADR-022

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `EmguALG/Core/ImageAlgorithm.cs` | 692 | class ImageAlgorithm ; enum WeldDefectType ; class WeldDefect | 核心算子集中地：滤波/边缘/轮廓 + DetectPreWeldAlignment（光丝对中，**2026-10-09 F-7 毫米化三级判定**）+ JointType（4 类死代码） |
| `EmguALG/Core/Stages.cs` | 410 | class StageBase ; class FilterStage ; class MorphologyStage ; class EdgeDetectionStage ; class FeatureExtractionStage ; class TemplateMatchStage ; class PipelineConfig ; enum TemplateMatchOperation |  |
| `EmguALG/Core/ImageRoiTools.cs` | 327 | class ImageRoiTools |  |
| `EmguALG/Core/PreprocessConfig.cs` | 231 | class FilterConfig ; class MorphologyConfig ; class EdgeConfig ; class LineLaserConfig ; class PreprocessConfig |  |
| `EmguALG/Core/AlgorithmBase.cs` | 140 | class AlgorithmBase |  |
| `EmguALG/Core/AlgorithmOperations.cs` | 43 | enum FilterOperation ; enum MorphologyOperation ; enum EdgeDetectionOperation ; enum FeatureExtractionOperation |  |
| `EmguALG/Core/AlgorithmResult.cs` | 32 | class AlgorithmResult |  |
| `EmguALG/Core/RangeAttribute.cs` | 22 | class RangeAttribute |  |
| `EmguALG/Core/UnitAttribute.cs` | 20 | class UnitAttribute |  |

### `AdaWeldSystem.UIDesign.ControlPage`

- **功能**：UI · 主内容页（主页面/数据追溯）
- **规模**：3 文件 / 2607 行
- **模块归属**：[[modules/UIDesign]]
- **约束 ADR**：ADR-008/049/053

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `UIDesign/ControlPage/MainPage.cs` | 1347 | class MainPage | 主页面：焊缝轮廓图 + 工艺参数四合一图 + 状态栏 + 模组面板（2026-10-22 主界面相机预览已删）。**2026-11-03**：`LogAppend` 时间戳统一 `Log.FormatTimestamp`。**2026-10-09**：仪表盘 5 层 GridPanel（ADR-010）；**2026-10-19**：`_uiTimer` 两表合一；**2026-10-21**：参考线仅焊接开启后绘制（详见 [[api/MainPage]]）；**2026-10-22**：删 `panelCam`/`imageBoxCam` 与 30Hz 预览；`panelfloatbutton` 改 2×2 运行时核算；**2026-11-10**：业主删 `flowLayoutPanel1`/`gridPanel2`/统计 label/`lblRobotCommand`，`RefreshDashboard` 已删；`steps1` 删除后按指示补回（容器 `gridTopBlock.Span="60:fill;80:fill;fill"`），同日改横排（`Vertical=false`）；复选框改挂 `panelChart2` 右侧 |
| `UIDesign/ControlPage/DataReviewerPage.cs` | 1078 | class DataReviewerPage ; class DataReviewRow ; class SessionCharts ; class SeriesItem ; class SeriesGroup ; class HoverHit | 数据追溯页：时间区间筛选 + 记录多选 + 多选合并曲线 + 五大类模组（ADR-056）+ 悬停读点值 + 3D 回溯入口；图表唯一路径 `RebuildChartDatasets`；读取失败不弹窗（归 LOG）；加载只由用户交互触发（`EnsureLoaded()`），⛔ 不订阅 `VisibleChanged`；查询门槛 = `GlobalCommData.IsAppRunning`；未加载/已查空两态；`DataReviewDiag` 限流诊断仅用于门拒绝；**2026-11-13**：撤除正常查询路径 `DiagLog`（残留脚手架致每次点开都出 2 条带堆栈 Warning，像报错），`InitPCLDir` 增 `userInitiated`，**首进 0 行只更新底部文案不弹窗**；见 [[api/DataReviewerPage]] |
| `UIDesign/ControlPage/NavPage.cs` | 215 | class NavPage | 通用导航容器页（系统参数设置专用，LoadTabs 承载 5 子页） |

### `AdaWeldSystem.MotionControl`

- **功能**：运控 · Manager 与从站设备
- **规模**：6 文件 / 2049 行
- **模块归属**：[[modules/MotionControl]]
- **约束 ADR**：ADR-027/028/030

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `MotionControl/WeldHeadSlaveDevice.cs` | 1015 | class WeldHeadSlaveDevice ; enum WsgGalvoPattern ; enum MotorRunState ; struct MotorState ; class GalvoParams ; class LaserHeadTemperatureData ; class HeadAlarmStatus ; class WeldHeadConfig | WSX 焊接头从站（万顺兴 ScanCut）：0x6000 温度 / 0x6010 振镜回读 / 0x7010 振镜写 / 0x7020 阈值 / **0x7000+0x6020 电机（LA，2026-10-08 已启用）**；含 `CreateLogicalHome()` 逻辑零位 + `MotorPulsePerMm` 量纲；；**2026-11-18 ADR-076 D7**：新增 `GetAxisConfigByName`（精确名取轴配置，区别于关键字匹配）（10 个全局项）+ `BuildGalvoParamsFor(pattern)`（组装下发：全局项 + 图形档）；`DefaultGalvo` 类型改 `GalvoGlobalParams` ⇒ **物理不存在**图形与宽/长/频；**2026-11-18 ADR-070 演进**：新增 `GalvoShapeParams` + `WeldHeadConfig.GalvoShapePresets`（GA 宽/长/频**按图形分 4 档**）+ `GetGalvoShape()`（缺档回退 Line 档）+ `SyncDefaultGalvoFromShape()`（`DefaultGalvo` = 当前生效参数集合） |
| `MotionControl/MontionManager.cs` | 2268 | class MontionManager | 运控唯一管理器：轴/IO/缸装载 + 焊接头注册 + 配置持久化 + 六轴控制函数（ADR-073）；TA 门禁族 `LoadTaAxisConfig`/`TaAvailable`（ADR-082）；**2026-11-05**：`LoadTaAxisConfig` 改纯装载判定、`SaveTaHomeConfig` 删 P1（ADR-080 §D6）；ADR-082/084/085 扭矩与日志演进；**2026-11-05**：新增初始化闸门 `IsInitCompleted`/`MarkInitCompleted`、同轴单飞 `TryBeginAxisInstruction` 与 5s 状态检测族（ADR-082/063 演进）；**2026-11-18 ADR-070 演进**：XML 顶层 `GALVO/WIDTH|LENGTH|FREQUENCY` **不再写、不再读进 DefaultGalvo**（存量读一次作各档缺省值）；**2026-11-18 ADR-070 演进**：`GALVO` 段 XML 加 4 组子节点（`GALVO/<CIRCLE\|EIGHT\|LINE\|ARC>/WIDTH\|LENGTH\|FREQUENCY`）+ 存量迁移（各档缺省取顶层旧单档值） |
| `MotionControl/IORegistry.cs` | 150 | class IORegistry |  |
| `MotionControl/CylinderRegistry.cs` | 127 | class CylinderRegistry |  |
| `MotionControl/AxisRegistry.cs` | 121 | class AxisRegistry | 按轴名登记台达轴并回灌控制器；元素类型已收紧为 `DeltaMontionAxis`（全库零 `as` 下转型） |
| `MotionControl/MoveControlData.cs` | 80 | class MoveControlData |  |

### `AdaWeldSystem.FileOperate`

- **功能**：文件 · 配置读写与日志
- **规模**：6 文件 / 2039 行
- **模块归属**：[[modules/FileOperate]]
- **约束 ADR**：ADR-033/040/079

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `FileOperate/XdocumentReaderWriter.cs` | 458 | class XdocumentReaderWriter | XML 配置读写（⛔ 禁 XmlSerializer）：三段式路径由构造注入；**2026-11-04 新增 `Reload()`**：从磁盘重读绑定文件；**2026-11-05 构造函数新增 `createIfMissing`**：预览/审计读传 `false`，禁止隐式建空文档（ADR-086） |
| `FileOperate/ConfigSelfHeal.cs` | 664 | class ConfigSelfHeal | 配置自愈统一入口（ADR-086）：INI/XML 只增不改补缺、整文件缺失生成模板、备份+临时文件原子替换、写后回读、单文件聚合日志、幂等零写 |
| `FileOperate/INIFile.cs` | 389 | class INIFile | INI 配置读写：ReadString/ReadInt/ReadDouble/ReadBool + 段与键枚举 |
| `ConfigFileControl/Implementations/ConfigSnapshot.cs` | 130 | class ConfigSnapshot | 配置快照：把 INI/XML 文档摊平成「路径→值」字典（**取磁盘态**，不干扰载体内存）；`Diff` 只记录有变动的键 |
| `WeldParamControl/WeldParamProfileAudit.cs` | 164 | class WeldParamProfileAudit | 分段参数表变更审计（按宽度档逐项比较送丝/功率/速度/光斑/摆幅） |
| `ConfigFileControl/Implementations/ConfigFileManager.cs` | 213 | class ConfigFileManager | **2026-11-19**：新增变更审计钩子 `SaveIniWithAudit`/`SaveXmlWithAudit`/`SaveIni`/`SaveXml`（保存 → 快照 diff → 只记变动项）。**全局配置文档总管**（ADR-006 D2）：唯一持有者 + 唯一对外口；根目录 `Config\ConfigFileControl\`；`GetIni`/`GetXml`/`GetModuleIni`/`GetModuleXml` 路由；其余 Manager 只消费参数不落盘；**2026-11-19 核查**：六个 Manager 正式载体数已全部归零（Records 按业主裁定保留） |
| `ConfigFileControl/Implementations/IniConfigFile.cs` | 75 | class IniConfigFile | INI 载体实现（包装 `INIFile`） |
| `ConfigFileControl/Implementations/XmlConfigFile.cs` | 100 | class XmlConfigFile | XML 载体实现（包装 `XdocumentReaderWriter`） |
| `ConfigFileControl/Abstractions/IConfigFileProvider.cs` | 48 | interface IConfigFileProvider | 载体抽象契约（读/写/存在性/Reload/Save），零第三方依赖 |
| `ConfigFileControl/Abstractions/IConfigRegion.cs` | 29 | interface IConfigRegion | 区域抽象契约（按 TabPage 分区，**键级**写入） |
| `FileOperate/ConfigPathMigrator.cs` | 201 | class ConfigPathMigrator | 历史配置路径一次性迁移（ADR-033 路径范式落地） |
| `FileOperate/Log.cs` | 198 | class Log | 日志文件写入（`yyyy-MM-dd HH:mm:ss:ffff`）+ **统一时间戳 `FormatTimestamp`（`yyyy-MM-dd HH:mm:ss` 24 小时制，界面与文件一致）** |
| `FileOperate/ConfigBackupHelper.cs` | 106 | class ConfigBackupHelper | 配置写前备份：CreateBackupFolder → `Config\_backup\yyyyMMdd_HHmmss` + BackupFile/BackupDirectory（ADR-079） |

### `AdaWeldSystem.LineLaserCam.IntelligentLaserCam`

- **功能**：线激光 · 英莱 SDK 实现
- **规模**：1 文件 / 1347 行
- **模块归属**：[[modules/LineLaserCam]]
- **约束 ADR**：ADR-024/051

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` | 1347 | class IlJobParamInfo ; class IlSensorInfo ; class IlJobDescInfo ; class IlJointTypeInfo ; class IlCameraParam ; enum IlFpsModel ; class IntelligentLaserCam | 英莱相机实现：Job 下发（含 DwJointType）+ jointtypelist.json 20 类接头解析 📄 |

### `AdaWeldSystem.Comm.Communication`

- **功能**：通讯 · 通道管理（唯一出口）
- **规模**：1 文件 / 1192 行
- **模块归属**：[[modules/Comm]]
- **约束 ADR**：ADR-025/026

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `Comm/Communication/CommunicationManager.cs` | 1192 | enum CommunicationType ; class CommunicationConfig ; class CommunicationManager ; enum RobotCommModeType ; struct RobotPoseSnapshot ; class KUKADataReceivedEventArgs ; class KUKAConnectionEventArgs | 通讯唯一出口；**RSI 唯一通道**（ADR-074：EKI 退役）；`SendRobotCommand(int,double)` 数值码下发 + `SendRobotCommandByName`；`UpdateRobotWeldParams` 扩 5 焊参通道；`SaveRobotRsiXml` 生成 8 具名元素 XML；SEND/REPLY_FORMAT 契约校验与旧版升级；端口取本机监听口；连接/断复位位姿快照；`DisconnectRobot` 返回 bool；**2026-11-03**：`ReloadFromDisk()` 供 `.awcfg` 导入后即时回读 📄 |

### `AdaWeldSystem.UIDesign.SubDialog.DataReviewerDialog`

- **功能**：UI · 弹窗 · 数据回溯
- **规模**：4 文件 / 974 行
- **模块归属**：[[modules/UIDesign]]
- **约束 ADR**：ADR-009/036

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs` | 420 | class HelixRenderForm |  |
| `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs` | 218 | class RenderParamForm |  |
| `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs` | 222 | class FileTraceForm ; class FileTraceRow |  |
| `UIDesign/SubDialog/DataReviewerDialog/RecordConfigForm.cs` | 114 | class RecordConfigForm |  |

### `AdaWeldSystem.MotionControl.IMotion`

- **功能**：运控 · 抽象契约（轴/IO/缸）
- **规模**：9 文件 / 1043 行
- **模块归属**：[[modules/MotionControl]]
- **约束 ADR**：ADR-006/027

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `MotionControl/IMotion/MontionAxis.cs` | 287 | class MontionAxis ; class CspResult |  |
| `MotionControl/IMotion/Cylinder.cs` | 166 | class Cylinder |  |
| `MotionControl/IMotion/Type.cs` | 148 | enum ControlType ; enum ManufacturerType ; enum IOType ; enum MoveMode ; enum HomingMode ; enum StopMode ; enum AxisState ; enum InterpolationType ; enum PVTTimeMode ; enum EcamCurveType ; enum EcamStartMode ; enum EcamBufferMode |  |
| `MotionControl/IMotion/IPVTMotion.cs` | 126 | interface IPVTMotion ; struct PVTPoint ; struct PVTInformation ; class PVTResult |  |
| `MotionControl/IMotion/MontionControl.cs` | 116 | class MontionControl |  |
| `MotionControl/IMotion/MontionIO.cs` | 69 | class MontionIO |  |
| `MotionControl/IMotion/InterpolationMontionParam.cs` | 63 | class InterpolationMontionParam |  |
| `MotionControl/IMotion/OutputIO.cs` | 38 | class OutputIO |  |
| `MotionControl/IMotion/InputIO.cs` | 30 | class InputIO |  |

### `AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog`

- **功能**：UI · 弹窗 · 英莱相机
- **规模**：4 文件 / 1033 行
- **模块归属**：[[modules/UIDesign]]
- **约束 ADR**：ADR-009/012/036

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` | 538 | class ILAlgoForm ; class IlJobParamRow |  |
| `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` | 291 | class ILParamForm ; class CameraParamRow |  |
| `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs` | 142 | class ILScanForm ; class SensorRow |  |
| `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgorithmEditForm.cs` | 62 | class ILAlgorithmEditForm |  |

### `AdaWeldSystem.SQLiteDBControl.Helpers`

- **功能**：数据库 · Helper（禁外部 new）
- **规模**：4 文件 / 1173 行
- **模块归属**：[[modules/SQLiteDatabase]]
- **约束 ADR**：ADR-033/043

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `SQLiteDBControl/Helpers/AutoParamHelper.cs` | 477 | class AutoParamHelper ; class WeldAutoParamProfile | 自适应参数分段表：7 列（焊宽/送丝/功率/速度/光斑宽/**振镜摆幅=摆幅宽度**/**摆幅频率**）；**2026-10-20**：`SwingWidthJson` 读写闭环（该列此前只读不写）；**2026-10-21**：增第 7 列「摆幅频率」+ `SwingFrequencyJson` 闭环（旧「振镜频率」列停止读写，遗留不删） |
| `SQLiteDBControl/Helpers/AuthHelper.cs` | 217 | class AuthHelper | 用户与权限：GetUserOperate / UpdateUserLevel（支撑 Admin 专属参数） |
| `SQLiteDBControl/Helpers/ConfigHelper.cs` | 208 | class ConfigHelper |  |
| `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs` | 271 | class ProductDatabaseHelper | 产品库按 `yyyyMMdd` 分表。**`SelectTables(start,end)` 逐日读表合并**（区间查询，366 天上限；ADR-056）；**2026-10-10**：缺表 `IsExistTable` 跳过 + 单日异常 `ShowLog` 后跳过当日（曾直调 `Select` 致缺表日 `SQLiteException` 使整段区间读取失败） |

### `AdaWeldSystem.LineLaserCam`

- **功能**：线激光 · 管理与配置
- **规模**：3 文件 / 972 行
- **模块归属**：[[modules/LineLaserCam]]
- **约束 ADR**：ADR-023/024

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `LineLaserCam/LineLaserManager.cs` | 668 | class ProfileSnapshot ; class LineLaserManager | 线激光 Manager：轮廓快照 ProfileSnapshot（FeatureY/FeatureZ/Version 增量拷取）；`DescribeLastError` 代理诊断文本（ADR-095）；轮廓帧 X 直读 `WeldParamManager.CurrentRobotX`（模拟/真实双路，ADR-045 演进） |
| `LineLaserCam/LineLaserConfig.cs` | 246 | class LineLaserConfig | 线激光配置 XML；**ADR-086**：`LoadConfig(bool allowHeal)` 缺文件生成模板、缺键经 `ConfigSelfHeal` 只增不改补写，预览读零写 |
| `LineLaserCam/CameraRegistry.cs` | 91 | class CameraRegistry |  |

### `AdaWeldSystem.MotionControl.DeltaEtherCAT.Native`

- **功能**：运控 · 台达 P/Invoke 封装
- **规模**：8 文件 / 918 行
- **模块归属**：[[modules/MotionControl]]
- **约束 ADR**：ADR-027

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `MotionControl/DeltaEtherCAT/Native/EtherCATEcam2Native.cs` | 192 | class EtherCATEcam2Native |  |
| `MotionControl/DeltaEtherCAT/Native/EtherCATMotionNative.cs` | 160 | class EtherCATMotionNative |  |
| `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs` | 160 | class EtherCATMasterNative | 主站/从站 P/Invoke 声明；**2026-11-05**：`CS_ECAT_Slave_SDO_Quick_Read_Message` / `SDO_Read_Response` / `SDO_Get_ErrorCode` 随 P1.087/088 写读链路删除；`SDO_Quick_Send_Message`/`SDO_Check_Done` 保留（`DeltaSlaveDevice` 在用）；`DeltaServo_Write/Read_Parameter` 声明保留但无调用方 |
| `MotionControl/DeltaEtherCAT/Native/DeltaErrorCode.cs` | 124 | class DeltaErrorCode |  |
| `MotionControl/DeltaEtherCAT/Native/EtherCATPVTNative.cs` | 89 | class EtherCATPVTNative |  |
| `MotionControl/DeltaEtherCAT/Native/EtherCATAdvancedNative.cs` | 77 | class EtherCATAdvancedNative |  |
| `MotionControl/DeltaEtherCAT/Native/EtherCATMotionBufferNative.cs` | 62 | class EtherCATMotionBufferNative |  |
| `MotionControl/DeltaEtherCAT/Native/EtherCATIONative.cs` | 46 | class EtherCATIONative |  |

### `AdaWeldSystem.MonitorCam.HikCam`

- **功能**：监控相机 · 海康 MVS 实现
- **规模**：1 文件 / 868 行
- **模块归属**：[[modules/MonitorCam]]
- **约束 ADR**：ADR-047

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `MonitorCam/HikCam/HikCam.cs` | 868 | class HikCam | 海康 MVS 实现：ScanDevices/Connect/StartCapture/GetImageBuffer(必调 FreeImageBuffer)/录像 |

### `AdaWeldSystem.MainDeviceControl.DeviceStateApiCore`

- **功能**：主控 · 三态契约与命令常量
- **规模**：4 文件 / 906 行
- **模块归属**：[[modules/DeviceControl]]
- **约束 ADR**：ADR-013/038

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs` | 466 | class DeviceWorkflowBase | 模组工作流基类：步号范式(RunStep) + 手动/自动双入口 + 可观测性(StepStatusText/WorkElapsedMs)；**2026-11-05**：`Log` 记录 `_lastActionMessage` 并暴露 `LastActionMessage`；**2026-11-16 ADR-098**：`ReadinessStage` 枚举 + `IsEnabled/IsHomed/IsAtWorkZero` + `EnsureReadiness` 拒绝文案 |；**2026-11-19 ADR-006 D2**：`ConfigRelativeDir` 死属性已删，改用 `ConfigModule`（各 workflow 子类 override 到自身模块）⇒ 5 个 workflow 配置真正走 `ConfigFileManager`（此前 override 仍指旧目录 ⇒ 改造静默失效）
| `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` | 278 | enum SubDeviceState ; enum SubDeviceWeldStatus ; enum MainDeviceStatus ; class SubDeviceStateChangedEventArgs ; class WeldStatusChangedEventArgs ; class DeviceStateBase | 三组枚举与事件契约：⭐ **SubDeviceState(3态·物理设备态 = Disconnected/Connected/Alarm)** / **SubDeviceWeldStatus(7态·焊接流程态)** / MainDeviceStatus(6态) + AlarmOccurred。⚠️ **前两者正交不可混**：设备态由物理量决定，流程态由流程推进决定 |
| `MainDeviceControl/DeviceStateApiCore/CommandCore.cs` | 300 | class CommandCore | 机器人上下行指令常量表（const string，非枚举非命令字）+ IsKnownCommand 硬编码链 + 指令释意字典 CommandDescriptions（19 条）与 TranslateCommand（拆载荷查字典，2026-10-19），见 [[api/CommandCore]] |
| `MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs` | 56 | enum DeviceInitOutcome ; class DeviceInitOutcomeItem ; class DeviceInitSummaryEventArgs | **初始化三态结果（2026-11-09）**：Success/Failed/**Skipped**（上级未就绪未发起连接）+ 逐项 `BlockedBy`/`Reason` + 汇总计数；与运行态 `SubDeviceState` **正交**，⛔ 不给 `SubDeviceState` 加 Skipped。规则见 [[standards/DeviceInitializationDependency]] |

### `AdaWeldSystem.SQLiteDBControl.SQLiteCore`

- **功能**：数据库 · SQLite 封装
- **规模**：1 文件 / 671 行
- **模块归属**：[[modules/SQLiteDatabase]]
- **约束 ADR**：ADR-033

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `SQLiteDBControl/SQLiteCore/SQLiteDataBase.cs` | 671 | class SQLiteDataBase |  |

### `AdaWeldSystem.MonitorCam`

- **功能**：监控相机 · Manager 与配置
- **规模**：2 文件 / 628 行
- **模块归属**：[[modules/MonitorCam]]
- **约束 ADR**：ADR-019/021/047/094

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `MonitorCam/MonitorCamManager.cs` | 640 | class MonitorCamManager | 监控相机 Manager：CurrentMat + PreviewFrameEvent（帧所有权分治，分发前就地标注标定十字）+ 健康巡检；录像 `StartRecord` 落 `RecordDirectory\yyyyMMdd\` 日期子目录（ADR-078）；**2026-11-03** 构造期 `EnsureRecordDirectory` 只在运行期检查/创建录像目录（不写 INI），失败只记 Warning 日志 + 回退 exe 下 `Record`（内存态），不弹窗；**2026-11-09 ADR-095/096**：`DescribeLastError`、`TryAcquireCalibFrame`、算法对象唯一取用入口 `DetectWireFeed/DetectWeldQuality` |
| `MonitorCam/MonitorCamConfig.cs` | 166 | class MonitorCamConfig ; const DefaultRecordDir | 硬件配置（IP/端口/曝光/尺寸/录像目录/标定），INI `MonitorCamera.ini`；**2026-11-03** 默认 `RecordDir=D:\WeldRecord`（唯一常量）；**ADR-086**：`LoadFromIni(path, allowHeal)` 缺文件/缺键经 `ConfigSelfHeal` 生成模板或只增不改补写，预览零写；不替用户迁移裸盘符根 |

### `AdaWeldSystem.LineLaserCam.ILineLaser`

- **功能**：线激光 · 抽象契约
- **规模**：4 文件 / 539 行
- **模块归属**：[[modules/LineLaserCam]]
- **约束 ADR**：ADR-024

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `LineLaserCam/ILineLaser/LineLaserEventArgs.cs` | 224 | struct LineLaserSeamResult ; class LineLaserResultEventArgs ; class LineLaserProfileEventArgs ; class LineLaserMatEventArgs ; class LineLaserStateEventArgs | 线激光契约：LineLaserSeamResult(struct) / Profile / Mat / State 四种事件参数 |
| `LineLaserCam/ILineLaser/LineLaserCameraBase.cs` | 221 | class LineLaserCameraBase | 相机抽象；`DescribeLastError(LineLaserErrorContext)` 诊断契约（ADR-095），基类默认明确「未提供返回码」 |
| `LineLaserCam/ILineLaser/LineLaserCalibration.cs` | 62 | class LineLaserCalibration |  |
| `LineLaserCam/ILineLaser/LineLaserType.cs` | 48 | enum LineLaserKind ; enum LineLaserConnectionState ; enum LineLaserErrorContext | 种类 / 连接态 / 失败语境（ADR-095） |

### `AdaWeldSystem.UIDesign.SubDialog.CommConfigDialog`

- **功能**：UI · 弹窗 · 通讯配置
- **规模**：1 文件 / 460 行
- **模块归属**：[[modules/UIDesign]]
- **约束 ADR**：ADR-009/036

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs` | 460 | class FileEditorForm ; class XmlPropertyRow |  |

### `AdaWeldSystem.PCLOperate.DataIO`

- **功能**：点云 · 读写
- **规模**：2 文件 / 519 行
- **模块归属**：[[modules/Comm]]
- **约束 ADR**：ADR-035

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `PCLOperate/DataIO/PointCloudReader.cs` | 362 | class PointCloudReader |  |
| `PCLOperate/DataIO/PointCloudWriter.cs` | 157 | class PointCloudWriter |  |

### `AdaWeldSystem.UIDesign.SubDialog.MotionControlDialog`

- **功能**：UI · 弹窗 · 运控配置
- **规模**：3 文件 / 477 行
- **模块归属**：[[modules/UIDesign]]
- **约束 ADR**：ADR-009/036

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` | 525 | class AxisConfigForm | 轴完整参数弹窗（UserControl）：单参构造 = 通用轴 19 行（Y 轴原样、无校验）；`(DeltaAxisConfig, DeltaTaHomeConfig)` 构造 = 通用区 + TA 特有区（回零四参写 `TA_HOME`、`HomeOffset` 写 AXIS），`Validate()` 仅 TA 启用、失败零写入；**布局字体实测自适应**（行高 `Font.Height+14`、标签宽带实测、输入等宽居中、超屏 `Panel.AutoScroll`；⛔ 无写死尺寸，ADR-080 §布局约束）；**2026-11-05**：删「扭矩侦测」分区及两行字段（37→实测 29 行），TA 特有区剩「工作零位」三条；**ADR-084**：增「力—力矩换算」行 `TA_FORCE_100PCT_N`；**ADR-084**：增「力矩输出」区 `TORQUE_SLOPE`（1~65535，写 AXIS）与 `TA_TORQUE_DIRECTION`（+/-，写 TA_HOME）；Y 19 行 / TA 29 行（含 4 分区标题） |
| `UIDesign/SubDialog/MotionControlDialog/IoConfigForm.cs` | 137 | class IoConfigForm |  |
| `UIDesign/SubDialog/MotionControlDialog/CylinderConfigForm.cs` | 132 | class CylinderConfigForm |  |

### `AdaWeldSystem.EmguALG.LineLaserContour`

- **功能**：图像算法 · 线激光轮廓
- **规模**：2 文件 / 408 行
- **模块归属**：[[modules/EmguALG]]
- **约束 ADR**：ADR-022/024

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` | 380 | class LineLaserContourAlgorithm ; class ViewGeometry |  |
| `EmguALG/LineLaserContour/ILineLaserContourAlgorithm.cs` | 28 | interface ILineLaserContourAlgorithm |  |

### `AdaWeldSystem.UIDesign.SubDialog.ParamContolDialog`

- **功能**：UI · 弹窗 · 焊参配置
- **规模**：2 文件 / 392 行
- **模块归属**：[[modules/UIDesign]]
- **约束 ADR**：ADR-009/036

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `UIDesign/SubDialog/ParamContolDialog/ConfigForm.cs` | 172 | class ConfigForm ; class ConfigRow |  |
| `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs` | 220 | class AutoParamForm ; class AutoParamRow | 自动参数表弹窗：6 列（焊缝宽/焊接速度/送丝/焊接功率/**摆幅宽度**/**摆幅频率**）全部可编辑，修正写回查表并落库（2026-10-20 增摆幅宽度列，2026-10-21 增摆幅频率列） |

### `AdaWeldSystem.UIDesign.MainWindow`

- **功能**：UI · 主窗体
- **规模**：1 文件 / 358 行
- **模块归属**：[[modules/UIDesign]]
- **约束 ADR**：ADR-008

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `UIDesign/MainWindow/FormMain.cs` | 358 | class FormMain | 主窗体壳：header+segmented+tabs+toolstrip；顶部四页（主页面/设备监控空页/系统参数设置/数据追溯），系统参数设置 NavPage 五子页（工艺设置/系统设置/线激光设置/监控相机设置/文档备份设置）；**子页面全部实例化后 `GlobalCommData.MarkUiReady()`**（设备初始化前置门控）；**首次 `Shown` 的设备初始化 Modal 关闭后 `GlobalCommData.MarkAppRunning()`**（运行态唯一来源，此前历史数据查询一律拒绝）；**2026-11-13**：`FormClosed` 补释放运控工作流（**关台达主站** `Master_Reset`+`Master_Close`）与监控相机工作流（停监督 + 释放 Mat），此前二者 `Dispose` 全库无调用点 ⇒ 主站跨进程残留 |

### `AdaWeldSystem.EmguALG.Manager`

- **功能**：图像算法 · Manager 唯一口
- **规模**：3 文件 / 335 行
- **模块归属**：[[modules/EmguALG]]
- **约束 ADR**：ADR-022

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `EmguALG/Manager/AlgorithmManager.cs` | 248 | class AlgorithmManager | 算法 Manager 唯一口：DetectWireFeed / DetectWeldQuality + 版本号快照 |
| `EmguALG/Manager/AlgorithmResultStore.cs` | 64 | class AlgorithmResultStore |  |
| `EmguALG/Manager/AlgorithmCompletedEventArgs.cs` | 23 | class AlgorithmCompletedEventArgs |  |

### `AdaWeldSystem.LineLaserCam.VirtualCam`

- **功能**：线激光 · 虚拟相机（模拟）
- **规模**：1 文件 / 263 行
- **模块归属**：[[modules/LineLaserCam]]
- **约束 ADR**：ADR-032/039

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `LineLaserCam/VirtualCam/VirtualCam.cs` | 263 | class VirtualCam | 虚拟线激光（模拟测试）：生成**恒定宽度**平直搭接轮廓喂自适应算法；**2026-11-18**：`BaseSeamWidth`/`BaseSeamDepth` 收敛为 `const`（无可设入口，⛔ 模拟基准宽度恒定）；`FrameRateHz` 属系统设置页「线激光数据频率」（有外部写入，**不动**） |

### `AdaWeldSystem.Comm.SystemComm`

- **功能**：通讯 · 全局单例与事件
- **规模**：2 文件 / 351 行
- **模块归属**：[[modules/Comm]]
- **约束 ADR**：ADR-025

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `Comm/SystemComm/SystemComm.cs` | 313 | enum MessageType ; enum MessageLevel ; enum OperateLevel ; class MessageArgs ; class GlobalCommData | 全局单例：ShowLog 日志、**OperateLevel 权限（默认 Admin + SetOperateLevel/OperateLevelChanged 唯一写入口）**、通讯指令广播（⛔ 无报警事件）、**`IsUiReady`/`MarkUiReady` 界面就绪门控**、**`IsAppRunning`/`MarkAppRunning` 正常运行态门控**（由 `FormMain` 首次 `Shown` 设备初始化结束后置位；⛔ 追溯查询禁以 `Visible`/`Created`/`IsHandleCreated` 判据）；静态构造 `_logArgs` 最先赋值 + ShowLog 空保护（防构造期重入崩溃）；**2026-11-03 ShowLog 同秒去重 `IsDuplicateWithinSecond`**（tag+级别+文本一致只出一条）；**2026-11-17 ADR-106 通讯日志查看通道见 [[api/GlobalCommData]]** |
| `Comm/SystemComm/PermissionLevel.cs` | 69 | class PermissionLevel | 权限等级职责集中：GetDisplayName/GetDutyText/IsAdmin/IsEngineerOrAbove/SetLevel。⛔ 禁在 UI 各处分散硬编码等级比较（S-11 新增） |

### `AdaWeldSystem.MonitorCam.IMonitorCam`

- **功能**：监控相机 · 抽象契约
- **规模**：4 文件 / 258 行
- **模块归属**：[[modules/MonitorCam]]
- **约束 ADR**：ADR-019/021/047

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `MonitorCam/IMonitorCam/IMonitorCamApi.cs` | 111 | interface IMonitorCamApi |  |
| `MonitorCam/IMonitorCam/MonitorCamType.cs` | 59 | enum MonitorCameraConnectionState ; enum MonitorCameraPhase ; enum MonitorSupervisionState |  |
| `MonitorCam/IMonitorCam/MonitorCamEventArgs.cs` | 53 | class MonitorSupervisionStatusChangedEventArgs ; class MonitorCameraFrameCompletedEventArgs |  |
| `MonitorCam/IMonitorCam/MonitorCamDeviceInfo.cs` | 35 | class MonitorCamDeviceInfo |  |

### `AdaWeldSystem.UIDesign.SubDialog.UserManagerDialog`

- **功能**：UI · 弹窗 · 登录与用户管理（权限来源）
- **规模**：2 文件 / 210 行
- **模块归属**：[[modules/UIDesign]]
- **约束 ADR**：ADR-009/036

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs` | 127 | class UserEditForm ; class UserRow |  |
| `UIDesign/SubDialog/UserManagerDialog/LoginForm.cs` | 83 | class LoginForm |  |

### `AdaWeldSystem.PCLOperate.Models`

- **功能**：PLC · 数据模型
- **规模**：2 文件 / 223 行
- **模块归属**：（无专属模块页，见功能描述）
- **约束 ADR**：ADR-025

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `PCLOperate/Models/PointCloudData.cs` | 167 | class PointCloudData |  |
| `PCLOperate/Models/Point3D.cs` | 56 | struct Point3D ; struct Point3DColor |  |

### `AdaWeldSystem.EmguALG.RealtimeMonitor.WireFeedDistance`

- **功能**：图像算法 · 光丝对中（领域包装）
- **规模**：3 文件 / 247 行
- **模块归属**：[[modules/EmguALG]]
- **约束 ADR**：ADR-022/056

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedDistanceAlgorithm.cs` | 112 | class WireFeedDistanceAlgorithm | 光丝对中领域算法包装（**2026-10-09 F-7 毫米化已并入**：mm 偏差 + `WireAlignGrade` 三级 + 剪丝判据，ADR-058） |
| `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedResult.cs` | 69 | enum WireAlignGrade ; class WireFeedResult |  |
| `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedConfig.cs` | 66 | class WireFeedConfig |  |

### `AdaWeldSystem.EmguALG.RealtimeMonitor.WeldQuality`

- **功能**：图像算法 · 焊缝质量检测
- **规模**：3 文件 / 169 行
- **模块归属**：[[modules/EmguALG]]
- **约束 ADR**：ADR-022

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityAlgorithm.cs` | 112 | class WeldQualityAlgorithm |  |
| `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityResult.cs` | 37 | class WeldQualityResult |  |
| `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityConfig.cs` | 20 | class WeldQualityConfig |  |

### `AdaWeldSystem.UIDesign.SubDialog.MonitorCamDialog`

- **功能**：UI · 弹窗 · 监控相机扫描
- **规模**：1 文件 / 145 行
- **模块归属**：[[modules/UIDesign]]
- **约束 ADR**：ADR-009/046

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs` | 145 | class MonitorCamScanForm ; class DeviceRow |  |

### `AdaWeldSystem.Comm.Communication.Abstractions`

- **功能**：通讯 · 抽象契约（CommChannelBase）
- **规模**：1 文件 / 107 行
- **模块归属**：[[modules/Comm]]
- **约束 ADR**：ADR-025/006

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `Comm/Communication/Abstractions/CommChannelBase.cs` | 107 | class CommDataEventArgs ; class CommChannelBase |  |

### `AdaWeldSystem.SQLiteDBControl.ISQLiteHelper`

- **功能**：数据库 · 抽象契约（Helper 基类）
- **规模**：1 文件 / 105 行
- **模块归属**：[[modules/SQLiteDatabase]]
- **约束 ADR**：ADR-033/006

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `SQLiteDBControl/ISQLiteHelper/DatabaseHelperBase.cs` | 105 | class DatabaseHelperBase |  |

### `AdaWeldSystem.EmguALG.Abstractions`

- **功能**：图像算法 · 抽象契约（IAlgorithm / IConfigurableAlgorithm）
- **规模**：2 文件 / 72 行
- **模块归属**：[[modules/EmguALG]]
- **约束 ADR**：ADR-022

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `EmguALG/Abstractions/IAlgorithm.cs` | 43 | interface IAlgorithm ; interface IConfigurableAlgorithm |  |
| `EmguALG/Abstractions/IResultStore.cs` | 29 | interface IResultStore |  |

### `AdaWeldSystem.SQLiteDBControl`

- **功能**：数据库 · 核心
- **规模**：1 文件 / 72 行
- **模块归属**：[[modules/SQLiteDatabase]]
- **约束 ADR**：ADR-033

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `SQLiteDBControl/SQLiteDatabaseManager.cs` | 72 | class SQLiteDatabaseManager |  |

### `AdaWeldSystem.UIDesign.SubDialog.FormMainDialog`

- **功能**：UI · 弹窗 · 主窗体辅助（初始化等待）
- **规模**：1 文件 / 56 行
- **模块归属**：[[modules/UIDesign]]
- **约束 ADR**：ADR-009

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `UIDesign/SubDialog/FormMainDialog/InitWaitingForm.cs` | 56 | class InitWaitingForm | 初始化等待弹窗（长耗时操作前的过渡提示） |

### `AdaWeldSystem.WeldParamControl.Curves`

- **功能**：焊参 · 标定曲线与摆幅取值（2026-10-08 新增，ADR-053）
- **规模**：1 文件 / 438 行
- **模块归属**：[[modules/WeldParamControl]]
- **约束 ADR**：ADR-053（曲线与量纲）/ 红线原文 `api/WeldParamControlWorkflow.md`（⛔ 不用自创公式；⚠️ ADR-043 正文无此条款，原标注为悬空引用，2026-10-08 审计改指）/ ADR-033（四点闭环）

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `WeldParamControl/Curves/TaLaCurveConfig.cs` | 438 | enum CurveInterpolation ; enum CurveExtrapolation ; class CurvePoint ; class TaLaCurveConfig | 曲线A（LA 位置→光斑）/ 曲线B（TA 位置→LA 偏移）采样点表 + 分段线性插值 + 单调性校验 + XML 读写；**内置线性锚点，文件缺失保留默认不报错**；**2026-09-09 F-10**：`ImportFromCsv` 输入表格导入（CSV/TSV 两段式，半套拒收 + X=0 锚点校验 + 版本号落导入时刻）+ 交付 `TaLaCurve_输入模板.csv`；**2026-10-21**：`AnchorSpotMm` 由编译期常量改为**实例属性**（取曲线A 采样点表 X=0 锚点），内置常量改名 `DefaultAnchorSpotMm`（回退值），外部经 `WeldParamManager.AnchorSpotMm` 读取 |

### `AdaWeldSystem.WeldParamControl.Abstractions`

- **功能**：焊参 · 抽象契约（WeldAlgorithmBase）
- **规模**：1 文件 / 26 行
- **模块归属**：[[modules/WeldParamControl]]
- **约束 ADR**：ADR-006/043

| 文件 | 行 | 主要类型 | 本文件做什么 |
|---|---|---|---|
| `WeldParamControl/Abstractions/WeldAlgorithmBase.cs` | 26 | class WeldAlgorithmBase |  |

---


---

## 五、注释精简回收的工程约束（2026-10-10）

> **缘由**：2026-10-10 全库「注释只写作用与应用范围」精简（约 1900 行过程性注释删除）时，业主裁定**真实约束与历史教训归知识库管理**。本节集中承载从代码注释中回收的约束——查约束先来这里，不再翻源码注释。配套裁定见 [[standards/CodeSimplification]] 第二节顶层裁定；批量编辑的坑见 [[lessons/CommentSimplificationBatchPitfalls]]。

### 5.1 运控与焊接头（MotionControl）

| 文件 | 约束 |
|---|---|
| `WeldHeadSlaveDevice.cs` | 焊接头字典：RxPDO 0x7010 振镜 / 0x7020 阈值 / 0x7000 电机，TxPDO 0x6000 温压 / 0x6010 / 0x6020，SDO 0x2004；定标 0.1/0.01 |
| `WeldHeadSlaveDevice.cs` | **焊接头硬件故障文本唯一产出点**（ADR-095）：`HeadAlarmStatus.Describe()`（报警位→中文，含"驱动板报警"）/ `DescribeTemperatureThreshold`（阈值越界）；流程层与 UI 只读 |
| `WeldHeadSlaveDevice.cs` | 振镜零位 ≠ 协议默认（圆+1.0mm），禁改构造默认值；脉冲当量 10 计数/mm 可配（`MOTOR/PULSE_PER_MM`） |
| `DeltaMontionAxis.cs` | CSP 系 Mdone 为多值状态机（0/1/2/3/5），运动中 = 非 0 |
| `DeltaMontionAxis.cs` | `SetOriginFlag=1` 会平移原点致轴跑飞——缓冲建系必须**不设原点**；S 曲线走 `S_TIME` 配置 |
| `DeltaMontionAxis.cs` | `BufferStop` Mode：0=Feedhold / 1=平滑停 / 2=急停，收尾**禁传 0** |
| `EtherCATMasterNative.cs` | OP=8（ALState 位掩码，取 3 全拦截） |
| `MontionAxis.cs` | `IsMoving` 存在厂商语义差异；运动收尾须查报警（CiA402 Fault 0x0008） |
| `ConfigPathMigrator.cs` | **2026-11-19**：加 3 条新 INI 路径（Adaptive/Flow/Trajectory）旧目录映射；配置迁移必须先于任何 Manager 构造；迁移过程禁调 ShowLog |
| `ConfigPathMigrator.cs` | **2026-11-19**：加 3 条新 INI 路径（Adaptive/Flow/Trajectory）旧目录映射；配置迁移必须先于任何 Manager 构造；迁移过程禁调 ShowLog |
| `MontionManager.cs` | **轴角色关键字表**（焊接四类运动轴的定位词，轴名包含任一即命中）是轴定位唯一入口：`GetAxisByKeys` / `GetDeltaAxisByKeys` / `GetAxisConfigByKeys`；UI 禁自建关键字数组；六单轴控制函数 `MoveTo`（自动使能绝对定位）/ `StepMove`（posMode=0 相对步进）/ `ToggleServo` / `JogStart`（dir 1=负向 0=正向）/ `StopAxis`（减速停）是**轴控制唯一出口**；⛔ `MoveTo`/`StepMove` 阻塞等到位，UI 线程禁调 → 手动操作走 `MoveToNoBlock`/`StepMoveNoBlock`；⛔ `HomeAxis`（非阻塞回零）已于 2026-11-17 删除（回零统一走 `TryHomeAxisWithWait`，手动回零与复位回零同一实现） |
| `MontionManager.cs` | **轴硬件故障文本唯一产出点**（ADR-095）：`DescribeAxisDiagnosis` / `DescribeAxisStatusWord` / `DescribeAxisCspRuntime` / `DescribeAxisCommandReturnCode` / `DescribeAxisRetractFailure`；流程层⛔ 禁直读状态字/总线态拼文案 |
| `MontionManager.cs` | **TA 力矩运行期态唯一读写口 = `DeltaMontionAxis.TorqueOutputEnabled`**（ADR-082 删 `TaTorqueModeEnabled`/`SetTaTorqueMode`/`TaTorqueModeChanged`）；`ExitTaTorqueMode(axis, action)` 命中 TA 且 `TorqueOutputEnabled` 时撤 `CST_Output_Enable` → 回 CSP（`ExitTaTorque(reason)` 已于 2026-11-09 迁 Workflow，ADR-094）；六轴控制函数动作前仍走该出口；⛔ 不持久化；`DeltaAxisConfig.TorqueModeEnabled` 由 TA（送丝即 TA）消费 |
| `DeltaAxisConfig.cs` | 驱动器模板字段（`TorqueModeEnabled`/`TorqueSlope`/`TorqueTarget`）留轴配置；**TA 下压力已归工艺配置** `WeldAlgorithmsConfig.TaForceN`（不再寄居 `TorqueTarget`） |
| `LaserWeldHeadWorkflow.cs` | `LA_Spot` 与 `LA_Pose` 均**先退出** `LA_Auto` 随动再动作；TA 三项（`TaForceN`/`TaPose1Mm`/`TaPose2Mm`）取自 `WeldAlgorithmsConfig`（工艺配置唯一权威），禁直读轴配置；`TaBreak`/`TaPose1`/`TaPose2` 入口统一 `ExitTaTorqueMode`（ADR-082），⛔ 不再置灰 Auto；`TaAuto`/`TaRetract` 共用 `TryResolveTaTorque`（力值按 `TA_FORCE_100PCT_N` 换算千分比，ADR-084），`TaRetract` = `TaAuto` 方向取反的纯力矩保持（无位置终点、不撤力、不回 CSP，ADR-082 D24~D29） |

### 5.2 焊参与算法（WeldParamControl / EmguALG）

| 文件 | 约束 |
|---|---|
| `WeldParamConfig.cs` | CSP 段距门限 = 单脉冲当量 0.001mm；调至每拍步长（约 4.8μm）同量级会**轴停走**；`CspMinSegMm` 已不参与写段判定 |
| `WeldParamConfig.cs` | 输出死区上界 0.02mm（÷速度须 ≲τ150ms，否则阶跃+平台、驱动器耗干停走）；现场值 0.01mm；护栏须加载期钳位 |
| `SeamMapTrackingAlgorithm.cs` | `Yt=(特征Y−标定Y)×方向+轴实时Y+机器人Y`，`Ycsp=Yt−机器人Y`；**禁一切时间域低通**；VirtualCam 特征须随轴反向 |
| `SeamMapTrackingAlgorithm.cs` | 切向野值判据 limit=0.2+0.15×外推距离；入图键须用外推 X 与查图同源 |
| `WeldParamManager.cs` | 起焊沿**禁清**工艺调整（1.2→0→1.2 闪断）；空分段表**禁覆盖**内存查找表（否则输出恒 0）；载入序 = 基准兜底 → DB 覆盖 |
| `WeldParamManager.cs` | 焊前必须预置参数防空值事故；工艺清空在播种之前，管控自「下发参数后 start」起 |
| `AutoParamHelper.cs` | `[]/{}` 是合法非空串，判据用「承载实质数据」；第 6/7 列为查表覆盖口（振镜摆幅=摆幅宽度 / 摆幅频率）；旧「振镜频率」列读取方已废止，遗留不删 |
| `TaLaCurveConfig.cs` | CSV 导入半套拒收；X=0 锚点必须校验 |
| `WireFeedConfig.cs` | 对中三级阈值口径 0.1mm 安全 / 0.3mm 报警 |
| `AlgorithmManager.cs` | INI 兜底值：PixelMmScale=0.05、Warn=0.1、Fail=0.3；ToleranceAngle 已废（无角度判据） |
| `ImageAlgorithm.cs` | 剪丝判据：WireMatched=焊丝未识别、WireHeadAdhesion=光斑未识别；轴向映射可换轴换符号 |
| `LineLaserContourAlgorithm.cs` | 中心公式**勿改回**英莱 demo 的 fPersent/dwOffset 写法 |
| `LineLaserContourAlgorithm.cs` | 中心公式**勿改回**英莱 demo 的 fPersent/dwOffset 写法 |
| `WeldParamConfig.cs` | **五区域归属**（`AlgorithmsZone`：①System / ②Quick / ③Adapt / ④Preset）**2026-11-19 ADR-076 D8 新增 ②′Flow 区**（系统页·流程控制与测试的 5 个工艺启用开关，原与 ②Quick 混在同 zone 跨 TabPage）⇒ 拆为 5 区（`Flow = 4`）；**INI 按 TabPage 四文件**（`AlgorithmIniSet.FileFor(zone)` 路由：System→Trajectory / Quick→Preset / Flow→Flow / Adapt→Adaptive / Preset→Preset）⇒ `SaveAlgorithmsZone` 只落目标文件，页面保存不再覆盖别页未保存的值（根因：`INIFile.SaveToFile()` 整文件重写）；新增 `MigrateLegacyAlgorithmIni()` 存量逐键迁移（同名 section 跨文件必须逐键搬，幂等，先写目标落盘再删源键）；⛔ 删 4 个零引用死配置（`LockSpotCalib`/`LockWirePos`/`SpotCalibPosMm`/`WireLockPosMm`）+ XML 死键 `Y_AXIS_MIN_MM`/`Y_AXIS_MAX_MM` 物理清理，每区唯一写口；`SeamWidthSource` 为**只读派生**（派生源 = `EnableGalvoWeave` 振镜摆动，禁从 INI 读 `SEAM_WIDTH_SOURCE`）；光斑宽度来源三项（⛔ `ManualSeamWidthMm`/`SpotWidthGain`/`ParamOutputHz` **已删**（ADR-076 D5）⇒ ③Adapt 只余「每段距离」`SegmentDistanceMm`；`EnableGuide` 唯一入口 ②Quick、`EnableMonotonicConstraint` 唯一入口 ①System；`MaxMapPoints` 归 ①System（XML 键路径 `SEAM_GUIDE/MAX_MAP_POINTS` 不变） |
| `WeldParamManager.cs` | **2026-11-19 ADR-006 D2**：⛔ **不再持有任何配置载体**（全部由 `ConfigFileManager` 统一持有，本管理器只消费参数，H7）；删 4 个 INI 读写器 + `_configFile` + `AlgorithmIniSet` + `MigrateLegacyAlgorithmIni` 存量迁移（业主裁定完全舍弃旧配置）；`HealAlgorithmsConfigKeys` 补键模板改用 `WriteZoneIniTo`/`WriteConfigTo` 写独立临时载体（不污染正式载体） | 曲线实例归本管理器**独占持有**，外部不得直读 `TaLaCurveConfig` 锚点常量（唯一读取口 = `AnchorSpotMm` facade）；**工艺输出 5 项**（手动固定缝宽/光斑宽度系数/参数输出频率/前馈安全系数/单调方向锁）经本管理器透传参数调整算法；TA 下压力 `TorqueTarget → TaForceN` 为**一次性迁移**（仅首次运行且工艺 INI 未写过该键时生效）；**ADR-084**：迁移换算 `TaForceN = TorqueTarget × Force100PctN / 1000`，基准 ≤0 跳过并告警；**ADR-084**：迁移后 `NormalizeTaForceDirection` 统一「大小 + 方向」——缺 `TA_TORQUE_DIRECTION` 时旧负值推断 -1，已有键不覆盖并告警核对翻向风险 |
| `WeldParamAdjustmentAlgorithm.cs` | 工艺输出项由本算法**统一管理**（前馈系数/单调锁 ①System）；⛔ **2026-11-18 ADR-076 D5**：手动缝宽/光斑系数/输出频率三项已删 ⇒ Manual 源恒定宽度改取 **GA 档宽度**（`ManualFixedWidthMm()`） |

### 5.3 主控与流程（MainDeviceControl）

| 文件 | 约束 |
|---|---|
| `DeviceControlWork.cs` | 线激光收工行程 = 终止行程 − 前置量（下限 0）；停止位 X ≠ 收终点，须走完前置距离；机器人到终止 X 才发焊接完成 |
| `DeviceControlWork.cs` | 消除报警一律回 NoReset，复位成功才到 Stop；急停无虚拟 IO、只有物理 IO、同步执行 |
| `DeviceControlWork.cs` | 焊接启动门控：标定位未就绪挂起受理，按拍限频轮询（2s），不阻塞 |
| `DeviceControlWork.cs` | 模拟结束须对称回待机（残留 ErrorAborted 会拦二次模拟）；新起点须复位跟踪，否则误判折返 1704mm 复焊 |
| `DeviceControlWork.cs` | 光丝对中 Y 阈值 0.1/0.3mm；剪丝回检循环上限 3 次后降级转人工；RSI 剪丝占 T13；回检 case 内禁 Sleep |
| `DeviceControlWork.cs` | **2026-11-17 ADR-107**：初始化动作结束拿到结果前不得启动通讯线程（含自愈重连）——`thCommCommandWork` 改由 `EnsureCommandWorkStarted()` 在初始化链正常结束或抢占中止后统一开启；同日演进：模组线程亦延后、IOWork 初始化期冻结状态变更、`_initAccepted` 封堵首拍竞态 |
| `CommunicationManager.cs` | **2026-11-17 ADR-107**：`SaveRobotRsiXml` 写盘加 `_rsiXmlLock` + 临时文件 `File.Replace` 原子替换 + 占用退避重试；初始化期间禁手动设备动作（`FilebackupPage.TryPassCommAction` 两档门控） |
| `MotionControlWorkflow.cs` | Mode1 = 清 FIFO + 解除坐标系；停稳后才清缓冲（错误码 4359）/下电（伺服报警） |
| `MotionControlWorkflow.cs` | 写段：段距 0.01mm、双门限、时基 ≤250ms、钳位 [0.85,1.0]×几何速、占空比约 44% 即停走 |
| `MotionControlWorkflow.cs` | 失步检测后重启；残差禁设死区、禁取本拍输出（零步 26.4%、冻结风险） |
| `MotionControlWorkflow.cs` | 失步检测后重启；残差禁设死区、禁取本拍输出（零步 26.4%、冻结风险） |
| `DeviceControlWork.cs` | 级联写入后**立即**调 `WeldStatusTrans()` 委托各子流程自行迁移（停焊沿 / Stopping 入口的唯一入口）；上行指令经具名元素数值码承载（`RxCmd`/`RxPayload`）；焊接中异常与总线故障先发 **`TX_NG`** 通知机器人停止动作，再切报警态（`TxCmd=10` 为备用，`TxCutWire` 指令码不在映射表内）；连接能力由 Comm 提供，本类只调其方法完成 Open + Connect On |
| `WeldParamControlWorkflow.cs` | RSI 为唯一通道且指令/参数**全部数值化**；文本协议「P功率 S送丝 V速度 G摆幅」**已废止**，禁再走文本通道 |
| `DeviceControlWork.cs` | **2026-11-18 ADR-067 演进**：初始化收尾处**主动调用** `_weldHead.MoveToDefaultFocus()`（LA 就位默认焦平面；⛔ 不在 workflow 构造期订阅本类事件）；**阶段 3（ADR-099）**：初始化只连+使能，结束态「已连接/已使能/未回零/无运动」，回零归复位；`RobotComm` 节点 `Mandatory=true`；`DoInitializeMachine` 拒 Running/EStop/Reseting，`AllInitTargetsConnected()` 全连即跳过；复位沿用既有链（`ResetMachine`→`IoReset`→`DoResetMachine`→`CascadeResetProcess`），运控在级联内 |
| `MotionControlWorkflow.cs` | **阶段 3（ADR-099）**：`ResetProcess` 在既有复位链内做门槛 L1 与能力分支（需回零轴 Home→工作零位 / 免回零轴只去工作零位），轴动作锁外执行；`RunInitAutoHomeIfEnabled` 仅在 `INIT_RUN_TA_HOME=1` 时恢复初始化回零 |
| `DeviceStatusWork.cs` | **阶段 3（ADR-099）**：`IOWork` 在 `DeviceControlWork.Instance.IsInitializing` 为真时跳过安全互锁门控，避免设备未连先报 Alarm（D16） |
| `DeviceControlWork.cs` | **阶段 4（ADR-100）**：设备 6 态 × 流程 7 态矩阵，设备态不自动级联流程态；`ConsistencyTick` 挂 `thIOWork` 内部 1 s 节流，只纠 `Stop×Working` / `NoReset×非NoReset` / `Alarm\|EStop×Working`（报警 3 s 宽限）；`ErrorAborted` 只经 `ReportAlarm` 上升；`SetStatus` 变化沿一条 Info；`CheckActionGate` 接 `DoSubWork` L4 与 `DoSubPrework` L0；`GetStatusSnapshot` 统一快照 |
| `DeviceStatusWork.cs` | **阶段 4（ADR-100）**：`IOWork` 每拍调用 `DeviceControlWork.Instance.ConsistencyTick()`，节流与纠偏在主控内，本类不持状态 |
| `DeviceControlWork.cs` | **阶段 5（ADR-101）**：`DisposeComponents` 幂等 + 30 s 预算 + 强制退出留痕；`CascadeDisconnectWithWait` 受理+等待+单台 5 s；`MachineCommandWorkClose`/`_commCloseWork` 通讯线程独立停；`DoEstopMachine` 停运动→置EStop→停线程→`ServoOffAll` 不断设备；`CloseRobotChannel`；`GetWorkThreadExitSummary` 输出线程 n/11 |
| `DeviceStatusWork.cs` | **阶段 5（ADR-101）**：`IOWork` 读 `IsShuttingDown` 只保活，不推进扫描/巡检/初始化/对齐 |
| `MotionControlWorkflow.cs` | **阶段 5（ADR-101）**：`InitializeOff` 幂等守卫，`DisposeManaged` 委派 `InitializeOff`，关闭台达主站单一路径 |
| `MontionManager.cs` | **阶段 5（ADR-101）**：`Close()` 幂等守卫（未初始化且无控制器对象即返回） |
| `LineLaserWorkflow.cs` | **阶段 5（ADR-101）**：连接/断开线程保存句柄并登记，`DisposeManaged` 中 `Join` 超时留 Warning |
| `FormMain.cs` | **阶段 5（ADR-101）**：`FormClosed` 追加释放 `MonitorCamManager`/`LineLaserManager`/`CommunicationManager` SDK 资源 |
| `CommunicationManager.cs` | **阶段 6（ADR-102）**：`NeedHeartbeat`（INI 默认 true）只停分级日志；`EnsureRobotChannelHealthy` 5 s 冷却自动重连（通讯层自愈，指令线程每拍触发） |
| `DeviceControlWork.cs` | **阶段 6（ADR-102）**：`EnsureHeartbeatThread` 仅在 `ConnectRobot` 成功后创建心跳线程；`HeartInspectWork` 只报 H0/H1/H3/H4 变化沿，移除线程内重连；`HeartbeatLevel` 只读属性 |
| `MotionControlWorkflow.cs` | **阶段 7（ADR-103）**：`RunCspTick` 新增 `_cspHasHeldTarget`/`_cspHeldTargetY`，缺值取 held 不回落 `TeachLockYMm`；`RaiseNoValueAlarm` 一条 Error + `ReportAlarm`（TX_NG）+ `StopCspOutput` + `Fail("NoValueAlarm …")`，`_noValueAlarmRaised` 一次焊段只报一次，不复用 `DoStopMachine` |
| `MotionControlWorkflow.cs` | **2026-11-17（ADR-100 D29 / ADR-082 D30）**：新增 `AxisRejectAutoWelding`；`TryManualAxisOperation`/`TryMoveAxisToTarget`/`TryHomeAxisWithWait`/`TaExecute` 增「自动焊接在跑 ⇒ 拒绝手动」门禁（⛔ `Stop`/`JogStop` 永远放行）；`ExecuteTaZeroPose` 前置改 `CheckTaAvailable`（TA_Zero 同口径要求已回零），删 `CheckTaMotionReady` 与「未回零只告警」块；`GetTaGateReason` 的 `allowZeroPose` 不再放宽 |
| `SeamMapTrackingAlgorithm.cs` | **阶段 7（ADR-103）**：新增 `PauseIngest`，置位时 `OnLaserResult` 只计无效帧不入图；`ResetTracking` 清零 |
| `WeldParamManager.cs` | **阶段 7（ADR-103）**：新增 `PoseAgeMs`；`OnSeamLaserResult` 按缺值>0 或位姿 age>2T 设 `PauseIngest`；`FeedLatestSeamWidth` 改调 `AccumulateSeamWidth`；删除 `IsCountType`/`CountNum` facade，改 `SegmentDistanceMm` |
| `WeldParamConfig.cs` | **2026-11-19 ADR-006 D2**：由 `WeldAlgorithmsConfig` **改名**并扩展为全局配置类（内部按 TabPage 划 5 个 `ConfigRegion`）；载体经 `ConfigFileManager` 取（自身不再 `new`）；`Load/SaveProcessIni` 与 `Load/SaveZoneIni` 改无参/单参签名；**保存前 `carrier.Reload()` + 只写本区域键（键级）** ⇒ 同 section 跨 TabPage 共享时互不覆盖；新增 `BuildRegions()` 区域清单 + `WriteZoneIniTo`/`WriteConfigTo` 模板方法；`RemoveChild` 清理已废 XML 键；**阶段 7（ADR-103）**：新增 `SEGMENT_DISTANCE_MM`（1~50 默认 5，越界钳位 Warning）；删除 `IsCountType`/`CountNum`/`EnsureSupportedSegmentation`/`DistanceSegmentationUnsupportedReason`；旧键 `IS_COUNT_TYPE`/`COUNT_NUM` 只读忽略记一条 Info 且停写 |
| `WeldParamAdjustmentAlgorithm.cs` | **阶段 7（ADR-103）**：按距离分段实现——`AccumulateSeamWidth` 同步滑动窗与段累计，累计 `|ΔrobotX|` 达 `SegmentDistanceMm` 取段内均值查表；段内无点不查表交缺值报警；`Reset` 清零分段状态 |
| `ProcessControlPage(.Designer).cs` | **阶段 7（ADR-103）**：删「分段方式」下拉与「每段点数」标签，`txtFlowCountNum` 改「每段距离(mm)」；新增红色 `lblNoValueAlarmHint`；不加续焊按钮 |
| `DeviceControlWork.cs` | **阶段 7（ADR-103）**：`EvaluateHeartbeatLevel` 接入 H2（`IsNoValueOverLimit`），`LogHeartbeatEdge` 对 H2 只记 Debug；唯一 Error 仍由缺值报警发出 |
| `DeviceControlWork.cs` | **阶段 7（ADR-104）**：`ReportAlarm` 焊接中发 `TX_NG` 后立即 `CascadeWeldStatus(ErrorAborted)`，不等宽限；`MonitorAlignTick` 入口判 `IsAlarmstop` 停走并归零剪丝相位；`DoClearAlarm`/`ReportAlarmCleared` 调 `ClearRobotCommand` 停发报警标志，只回 `NoReset` 不改流程态 |
| `WeldParamControlWorkflow.cs` | **阶段 7（ADR-104）**：`FlowProcess` 顶部判 `ErrorAborted`/`IsAlarmstop` 直接返回，`StepCompute`/`StepOutput` 不再推进；`PreWork` 报警期拒单；`SendToRobot` 停止调用即 RSI 载荷冻结 |
| `CommunicationManager.cs` | **阶段 7（ADR-104）**：新增 `ClearRobotCommand` → `RsiComm.ClearTxCommand`，只清 `TxCmd/TxPayload`，不动焊参缓存与收发周期 |
| `LaserWeldHeadWorkflow.cs` | ；**2026-11-18 ADR-076 D7**：Y 轴限幅与回归越界判据改接**轴软限位**（`TryGetSeamAxisSoftLimit`，0 = 不启用则不限幅），非焊接态幅值归零、`GalvoEnable=false`，不沿用旧自适应摆幅 |

### 5.4 通讯与权限（Comm）

| 文件 | 约束 |
|---|---|
| `KukaRsiComm.cs` / `CommunicationManager.cs` | RSI IPO 12ms 周期内回包；HOLDON；Tool.X/Y/Z→ETHERNET 1/2/3；剪丝占 T13（两处格式生成同步改）——⚠️ 改造后：指令走 RxCmd/TxCmd 数值码、剪丝走 CutWire 具名元素；**2026-10-22**：RobotServer 连接参数挂 `<CONFIG>`（旧根级自动迁移），`HOST_PORT` 作监听口、`PORT` 写 RobotPort，默认 IP 192.168.10.100/192.168.10.50；**2026-10-22**：机器人=客户端/发包方、上位机=UDP 监听方，`IsRobotOnline` 以最近收包超时判定（监听态≠在线）；`Start` 绑定 `HOST_IP` 并预校验网口，无对应网口写错误日志并失败；`LastError` 集中暴露启停失败原因（不罗列本机 IP） |
| `InLaserModbusComm.cs` | 寄存器 0x00~0x28，标度 0.01mm |
| `PermissionLevel.cs` | 启动默认 Admin；降权必须广播 OperateLevelChanged 事件 |
| `SystemComm.cs` | 通讯建立监听后到停止前的报文走 ShowCommunicationLog 全记录；设备日志与通讯日志不混用 |
| `SystemComm.cs` | 通讯建立监听后到停止前的报文走 ShowCommunicationLog 全记录；设备日志与通讯日志不混用 |
| `CommandCore.cs` | **RSI SEND 段 TYPE 仅 BOOL/DOUBLE/LONG 不含 STRING** ⇒ 上行指令必须数值化（禁字符串指令）；契约文档 =《配置_本机(上位机)_RSI统一通讯配置.xml》 |
| `KukaRsiComm.cs` | 本机监听 IP 须**已分配到本机已启用网口**（`Start` 绑定具体 `HOST_IP`，不绑 0.0.0.0；无对应网口必须失败并给出可排查日志）；离线判定 = 5 个通讯周期且**不小于 500ms**；「机器人在线」= 监听运行中 + 收到过包 + 最近一包未超时（监听态 ≠ 在线） |

### 5.5 线激光与相机（LineLaserCam / MonitorCam / IntelligentLaser）

| 文件 | 约束 |
|---|---|
| `IntelligentLaserCam.cs` | 必须在 `ConnectToSensor` **前**注册全部回调，否则一次性回调丢失；SDK 函数实例 ID 用 1u；**空帧（未开激光/无结果）也发 `RaiseProfileReady(null)` 供画面清屏+画校准四边框，但 ⛔ 不发 `RaiseResultReady`**（会刷 `_lastResultValid` 与首结果超时判定打架） |
| `LineLaserConfig.cs` | 禁 XmlSerializer；非线程安全，运行期禁流程循环读写；**`ROOT/TIMEOUT` 三键（DATA_STABLE/WAIT_WORKING/FIRST_RESULT_SECONDS）= 线激光三处等待超时秒数**，`SanitizeSeconds` 收敛 1~3600，Tracking 设置页可改 |
| `LineLaserContourAlgorithm.cs` | **`BuildViewGeometry` 的校准块必须排在 `count<2` 判空之前**（角点与 `Rate` 只依赖 `calib`，与轮廓点数无关）；否则空帧（传感器已开但无结果）提前返回 ⇒ 校准四边框不画，且毫米刻度停在 `Rate=1` 而范围虚大 |
| `LineLaserCalibration.cs` | 校准角点/中心单位 mm，索引 0=横向 / 1=高度 |
| `LineLaserCameraBase.cs` | 抽象层禁引厂商 SDK 类型；线激光族仅英莱 + 虚拟 |
| `HikCam.cs` | MVS 4.8.1：net40 原生库由 MVS 客户端提供；GigE IP 取 `IGigEDeviceInfo.CurrentIp`；无垂直镜像；`IImage` 宽高为 uint 需收窄 |
| `MonitorCamManager.cs` | 帧所有权分治（CurrentMat + PreviewFrameEvent）；预览帧只释放本页副本 |

### 5.6 UI（UIDesign）

| 文件 | 约束 |
|---|---|
| `MainPage.cs` | 主动轴位置归 `WeldParamMontionControl` 非 AdaptControl；无数据源不画假曲线；跨线程只准 BeginInvoke 禁同步 Invoke；状态色映射 + EStop 红闪 0.5s；报警取首个、禁直出枚举名；单选互销须抑制标志防重入；开关名表与 `LineLaserSwitchIndex` 索引耦合 |
| `DataReviewerPage.cs` | ⛔ **`ColumnCheck` 双参表头无全选**（单参才有；勿用反证法推渲染行为）⇒ 全选/全取消/反选走 `panelSelectBar` 三按钮（作用于 `_allRows` 全集）；`DataReviewRow : AntdUI.NotifyProperty` + `OnPropertyChanged`（否则改值不刷新）；**多会话各自独立成线**（`SessionCharts` 一会话一份，`SessionLabel` 加 `#序号`，空会话不入）；**并排控件用 `TableLayoutPanel` 分格，⛔ 同父多 `Dock=Fill` 必重叠**；Columns 须代码后置创建；悬停 60ms 节流+像素容差；只画当前模组线 |
| `SystemControlPage.cs` | 权限隐藏≠禁用（同步禁用+保存二次校验+切页三层校验）；JOG 按住连续/松开停止；限位原点按软限位推导；**2026-11-17**：手动操作（Y 8 键 / TA 8 键 / LA 4 键 / GA 2 键）改「按钮禁用=执行中 → 后台线程执行 → 执行消息回 UI」；⛔ 停止键永远可用、点动键不进执行器（禁用会丢 MouseUp）；⛔ 刷新禁跨线程、禁每拍整表 Binding（差分才重绑），刷新只做显示信息、按钮管控改事件驱动；**2026-11-17 再演进**：按钮禁用按 `ManualOpGroup` 四组隔离（Trace/Ta/La/Galvo），⛔ 一个电机的操作不牵连其它电机按钮（ADR-075 D32）；自动焊接中禁手动（`_manualActionAllowed` 由焊接状态事件驱动，构造期不读主控单例）；本页 `timerRefresh` 由本 Designer 托管，**页内唯一实例**，⛔ 不与工艺设置页共用 |
| `ILCamPage.cs` | JOB/帧率下拉不立即切换须点应用；传感器运行禁切帧率（SDK 限制）；`SetSensor` 才是启停；**结果表恒显 状态/ParseRes/ErrorCode**（无结果时也要能看到状态码，判"为什么没值"），几何与测量值仅 `r.Valid` 时显示 |
| `MonitorCamPage.cs` | `FolderBrowserDialog` 无 IDisposable 禁 using；连接 IP 先落盘 |
| `MonitorCamPage.cs` | `FolderBrowserDialog` 无 IDisposable 禁 using；连接 IP 先落盘 |
| `ProcessControlPage.cs` | **振镜摆动开关兼作焊缝宽度来源开关**（开 = 实测宽度驱动摆幅 `SeamWidthSource.Laser`，关 = 手动固定宽度 `Manual`），切换后重算光斑宽度表；激光工艺页不设重复开关（硬件使能归系统设置页 `btnOptGalvoEnable`）；工艺输出 ⑤三项（手动宽度/光斑系数/输出频率）落 ③Adapt 区；LA·TA 为**参数区**（非指令区），指令区用 Radio 互斥（未就绪整组置灰但保留互斥关系） |
| `SystemControlPage.cs` | **五个「自动刷新」开关前置条件分治**：运控未连接 ⇒ 自动回退 false（重连自动恢复默认 ON）；当前页不可见 ⇒ **只跳过刷新、保留开关状态**（两条件不得合并进同一提前返回）；**2026-11-03**：连接态判定只在 `StateSwitched` / `InitializationCompleted` 后做一次，计时器只跳过刷新（初始化中不得误判未连接）；配置编辑后的重载走 `OpenAxisEditor`，运行态由开关按拍刷新 |
| `SystemControlPage.cs` | **TA 力矩模式开关已删（ADR-082）**：`RefreshTaTorqueModeAvailability()` 随 `swTaTorqueMode` 一并移除，⛔ 不得复活为 Auto 门禁；手动使能/前进/后退经 Manager 六轴函数统一退出力矩模式；轴控制零页面代码 |
| `ProcessControlPage.cs` | **LA 指令区两套电机分组互斥**：对焦 5 项入 `gridQuickLaFocus`、振镜 4 项入 `gridQuickLaGalvo`（AntdUI Radio 互斥作用域 = 父容器）；`gridQuickLa.Span="40:fill;60:fill;30:fill;30:fill"`；⛔ 不得把两套放回同一容器（会整区互斥）；TA 区仍单容器整区唯一 |
| `ProcessControlPage.cs` | **三指令区默认 Auto 与连机同步**：`ApplyDefaultCommandModes()` 构造期选各自 Auto（`_loadingProcessEnable` 抑制处理器）；`RefreshActionStates()` 是**唯一**启用/禁用同步入口，由 `MotionControlWorkflow.StateSwitched` 实时驱动；禁用只改 `Enabled` 禁改 `Checked`；**ADR-082**：TA_Auto 不再受力矩模式门控，可用性只由 `TaAvailable`（配置成功 ∧ 已使能 ∧ ZeroPose 到位），`DoTaAuto()` 直调 `TaAuto`；**ADR-084**：下压力按 N 校验并按 100% 力量基准换算；**2026-11-06**：TA 区新增 `txtTaZeroPose`（`WeldAlgorithmsConfig.TaZeroPoseMm`，工作零位坐标唯一可编辑源，与 `TA_Pose1/2` 同构） |
| 通用 | 事件订阅放代码后置防设计器丢失；Modal 内容控件须显式尺寸；配置迁移先于 Manager 构造（`Program.cs`） |

### 5.7 预留（0 消费）成员清单 —— ⛔ 禁删，待业主逐案裁决

> 2026-10-10 逻辑精简轮全库审计产出，**仅登记不处置**。分组摘要（完整名单见各批次报告，累计约 90+ 项）：

- **可观测性/安全钩子**（永不用删）：`StepStatusText` / `WorkElapsedMs` / `StepElapsedMs` / `SetWorkTimeStart` / `IsStepTimeout` / `CheckDeviceIOSafe`
- **DeviceControlWork 对外门面**：GetAlarmInfo、GetIOState、GetMainDeviceStatus、GetSubDeviceStatus、Get/SetWeldParam、Get/SetRobotCoord、IsRobotOnline
- **事件**：`DeviceStateBase.AlarmOccurred`（全库无订阅）
- **协议能力族**（ILModbusData 状态寄存器批量口）——✅ KukaEkiComm 相关已于 2026-10-21 随 ADR-074 整体退役（整文件删除）
- **运控管理口**：MontionManager 的 Add*/ServoOnAll/ServoOffAll/HomeAll、`WeldHeadSlaveDevice.ResetHead` 等
- **算法预留**：`AlgorithmBase` 整类（无子类）、`ImageAlgorithm` 模板匹配族、`WireFeedConfig` 仅 INI 往返字段
- **UI 预留**：HelixRenderForm 渲染控制族、`LoginForm.IsLogin`、各类 `Window` 属性
- **焊参预留**：`TaLaCurveConfig.ImportFromCsv`、`WeldParamManager.GetOrCreateJointDefault`、记录类只写字段（序列化载体）

> **2026-10-26 代码精简轮增补**（判据与标准对齐后的实测基线，逐批偿还台账）：
> - **① 成员顺序（2026-10-26 v2，region 内口径）**：**已清零（2026-10-29）**。轨迹：全局口径 93 处 → 安全批次 83 → 口径修订 26 → 自动 + 定点批次 **0 处 / 0 文件**。判据修正：`parse_file` 收录嵌套类型（外层不再计嵌套成员）、析构函数不再当构造函数、字段只认类体深度 0；新增 `--fix-victims` 定点搬移（搬违规段到本 region 最早更高层级成员前），覆盖 SurfaceTriangulator / ProductFileRecordManager / DataReviewerPage / CommunicationManager / IntelligentLaserCam。复核命令：`python scripts/simplify_apply_member_order.py --report` → `violations=0 files=0`。
> - **② 注释质量 1,145 → 0 处（本轮已全部修完）**：§二②「写了 `///` 就必须符合 XML 规范」—— 批量补 `<param>` **534** 个、`<returns>` **213** 个，压缩超 20 汉字的 summary **443** 处（单行 365 + 多行 78，余文移入 `<remarks>`）；**private 的 `///` 全部保留**（业主裁定：private 允许用 `///` 总结，不走删除路线。**2026-10-29 二次清理**：清零 51 warn（trim 30 / param 16 / returns 6），当前 **0 warn / 294 info**（M1 存量不追溯）。
> - **⑤ 功能重叠 0 warn（2026-10-29 判据豁免）**：`XdocumentReaderWriter.GetXmlStrValue`（3 参取属性 / 2 参取元素值）、`SQLiteDataBase.CreateTable`（列长与 `IsExistTable` 守卫不同）、`ProductFileRecordManager.AddFrame`（两版各 1 行薄包装）——均为**同名重载**，`csharp_review._check_overlapping_methods` 已增加「同名重载不参与功能重叠判定」；判据不再报警，无需合并。
> - **④ 过度等待 12 → 0 处**：原「`.Result` 阻塞」9 处实为**事件参数属性 `e.Result`**（同步取值，不阻塞）⇒ 判据已收窄为「`Task/ValueTask` 的 `.Result` / `.GetAwaiter().GetResult()`」；运控 `DeltaMontionAxis` 的直线 `Thread.Sleep` 2 处属**运控时序红线** ⇒ 已在判据中加**豁免清单**（标准 §四「有意例外」条款落地）。周期轮询类 `Thread.Sleep` 19 处按同条款降为 info。
> - **多层锁（2026-10-27 新增判据）**：嵌套锁 / 跨方法锁顺序反转 / `lock("字符串")` / 锁局部对象 → `B.多层锁`；锁对象字段非 `readonly` → `B.无意义锁`。实测 **0 处嵌套/顺序反转**；`Log.m_lock` 已补 `readonly`。函数块内逻辑精简（null/冗余赋值/临时变量/过度等待/资源管理）原判据已覆盖，当前 23/3/11/19/3 处 info。
> - **⚠ 成员顺序编辑的「复制而非移动」风险**：把声明搬到别处若分两步做（先插后删），中间态会留下**两份声明** ⇒ CS0102。2026-10-26 已在 `InterpolationMontionParam._axisCount` 上翻车一次（业主编译报「已包含定义」+ 成员二义性）。**纪律**：搬运必须一次原子完成，或第二步断言旧文本已不存在；搬完立刻断言「该声明出现次数 == 1」。扫描器已补 `check_duplicate_members`（**ERROR 级**，含重载与条件编译互斥豁免）自动拦截，详见 [[lessons/StaticVerifierJudgements]] §9.11。

### 5.8 待裁定点（2026-10-10 已全部销项，见下）

~~1. 焊参/运控 `WeldStatusTrans` 恒假条件 `WeldStatus==X && WeldStatus!=X`（疑历史改写残留，属行为修复）。~~
~~2. 运控 `SubDeviceLog` 格式串 5 占位符 4 实参，调用即 `FormatException`。~~
→ **2026-10-10 两项均已修复**（[[decisions/ADR-061-WeldStatusTransCascadeWiring]]）：恒假条件按 LineLaser 模板对齐、格式串 4 占位 4 实参；**同轮新发现并接线**：`DeviceControlWork.WeldStatusTrans()` 编排入口原为**零调用方**（`DispatchCommand` 移除时丢失），现已接在 `CascadeWeldStatus()` 末尾（ADR-042 停焊沿 / ADR-038 Stopping 入口恢复可达，停止路径待真机验证）。

---


---

## 设备归属与流程归属（2026-11-05）

| 文件 | 归属层 | 职责 | Wiki |
|---|---|---|---|
| `AdaWeldSystem/MotionControl/MontionManager.cs` | 硬件 / 连接层 | Y / TA 的轴对象、配置、使能、SDO、回零状态；按轴门禁 `YReady`/`TaAvailable`/`LaReady`/`GetAxisGateReason`；`DescribeAxisDiagnosis`（ADR-094 D2 保留）；单飞 `TryBeginAxisInstruction` + `CancelAxisInstruction`；**只读摘要 `TryGetAxisReadout` / `TryGetAxisNameByKeys`**；六单轴基础指令 + **中性运动能力 `TryMoveAbsoluteNoBlock` / `WaitAxisAtTarget`（7 参重载）/ `SetTaZeroPoseGate`（2026-11-09 门禁写入口）**。⛔ 手动轴操作分发、零位编排、TA 角色级力矩动作、整机初始化叙述均已迁 Workflow | [[api/MontionManager]] |
| `AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` | 流程层（Y / TA） | Y 轴与 TA（送丝即 TA，仅两轴）的指令编排与判据；TA 六指令唯一实现；**`TryManualAxisOperation`（UI 手动轴操作唯一入口）**；**`TryHomeAxisWithWait` / `TryMoveAxisToTarget` / `RunTaZeroPoseAfterInit` + 6 个 `AxisReject*` 常量**；**2026-11-09 迁入（ADR-094）：`ExitTaTorque` / `SetTaTorqueMode` / `SetTaTorque` / `StopTaTorque` / `BuildMachineInitSummary` / `LogAxisGateReport` / `TaZeroPoseStageChanged` + 四态属性**；`YReady`/`YGateReason`/`GetTaGateReason`/`TaPositionMm` | [[api/MotionControlWorkflow]] |
| `AdaWeldSystem/Comm/SystemComm/DeviceWaitSettings.cs` | 配置快照（中立） | 设备侧等待五项只读镜像（相机/落盘/线激光回调/Modbus 连接/读写）；真相源 `FlowTimeoutConfig`，避免 Comm / ProductFile 反向依赖运控命名空间 | [[decisions/ADR-093-FlowTimeoutConfigAndLayering]] |
| `AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` | 流程层（LA） | 自动对焦电机与振镜指令（`La*`/`Galvo*`）；焊接头从站温度/报警设备态；`LaReady`/`LaGateReason`；**TA 薄转发壳已于 2026-11-06 整体删除（ADR-092）**；报警/温度文本已下沉 `HeadAlarmStatus.Describe()` / `WeldHeadSlaveDevice.DescribeTemperatureThreshold`（ADR-095）；**2026-11-17（ADR-100 D29）** 新增 `EnsureManualWeldHeadActionAllowed` 统一门禁（自动焊接在跑 ⇒ 拒绝 LA/GA 手动动作），`GalvoDemo` 原用过宽的 `IsWelding` 判定一并改用该门禁 | [[api/LaserWeldHeadWorkflow]] |
| `AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs` | UI 层指令区 | Y / TA / LA 三区各自向对应 workflow 取门禁与失败原因；`RunInstruction` 按轴预检 + 单飞 + 确认 + 后台检测；⛔ 门禁**点击时直读权威源**（2026-11-17 删除门禁快照，`ActionGateSnapshot`/`_gateSnapshot` 已退场）；指令区**不变量**：每组最多一个 Radio 带底色且带底色者=选中者（ADR-063 D31）；链路改为**确认→门禁→单飞→执行→上色**，被拒保持选中并标红；自动 `TA_ZeroPose` 不抢选中态不占底色；`TA_Zero` 与其它 TA 指令同口径要求「已回零」（ADR-082 D30）；本页 `timerRefresh` 由本 Designer 托管，**页内唯一实例**，⛔ 不与系统设置页共用 | [[api/ProcessControlPage]] |

### 分层判据（2026-11-08，后续每轮自查）

| 层 | 允许 | 禁止 |
|---|---|---|
| 轴类 `MotionControl/DeltaEtherCAT/` | 使能/移动/回零/扭矩/状态字读写 | 工艺语义（`Auto`/`Break`/`Pose`/`ZeroPose`） |
| `MontionManager` | 按配置实例化轴并持有；按轴门禁、单飞登记、到位等待、原始状态摘要、单轴基础指令 | 角色级应用动作分发（2026-11-09 已清空，ADR-094 D1/D3） |
| `MotionControlWorkflow` | 应用层运动指令封装（唯一业务动作所在地） | 绕过轴类的直接寄存器时序 |
| UI | 发起后台调用、消费状态与结果 | 持轴对象、写动作封装、解析状态字位 |

**遗留项（2026-11-08 决策八已全部关闭）**：
- ~~`DeltaMontionAxis` 仍含 `StartZeroPoseMove` / `WaitZeroPose` / `RunZeroPose` / `TaZeroPoseTag`~~ → 已删除，编排迁至 `MotionControlWorkflow`。
- ~~`ProcessControlPage.L846/L912/L1433/L1438` 仍持 `MontionAxis` 局部变量~~ → 已改调 `TryHomeAxisWithWait` / `TryMoveAxisToTarget` / `TryGetAxisNameByKeys`，本页轴对象 = 0。

**保留项（非工艺语义，未中性化）**：`DeltaMotionConfig` 气缸三字段 `Retract*` 与 XML 键 `RETRACT_*` —— 通用气动"缩回"语义，若要求改名需同步 `MotionConfigImporter` CSV 列与现场 CSV。

### 四层边界现状（2026-11-09）

| 层 | 代表文件 | 实际依赖方向 | 当前事实 |
|---|---|---|---|
| 轴类 | `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` | → `Native/` L1、`IMotion/` L2 | 原生 DLL 调用 `CS_ECAT_*` 全量收敛在本目录 14 个文件（184 处）；UI / Workflow / Manager 侧 0 处 |
| 硬件 / 连接层 | `MotionControl/MontionManager.cs` | → 轴类、`MoveControlData`、`Comm` | 持有轴对象与运控配置；提供按轴门禁、单飞登记、到位等待、原始状态摘要（状态字/位置/模式只读快照）；**⛔ 不持 TA 角色语义、⛔ 不讲整机初始化故事（2026-11-09 清空）** |
| 流程层 | `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` | → `MontionManager`、具体轴类 `DeltaMontionAxis` | TA 六指令唯一实现 `TaExecute(TaCommand)`；TA 角色级力矩动作与 ZeroPose 四态/事件；Y 轴纠偏与标定回归编排 |
| UI | `UIDesign/TabPage/*` | → Workflow / Manager（只发起调用、只读摘要） | `MontionAxis` 类型在 `UIDesign/` 下 0 命中；`GetStatusWord()` 在 `UIDesign/` 下 0 命中 |

### 待收敛清单（登记，不改码）

| # | 位置 | 现象 | 与分层判据的偏差 | 影响面 | 风险 |
|---|---|---|---|---|---|
| 1 | `MotionControlWorkflow.cs` `SetTorque` / `StopTorque` / `AbsMove` / `AxisStop` / `ServoOn` / `GetPosition` 调用点（全文件 20 处） | 流程层直接依赖具体轴类型 `DeltaMontionAxis` 的硬件方法 | 判据允许「应用层运动指令封装」；**ADR-094 D5 已定：不引入 `IMotion.MontionAxis` 通用抽象**（TA/Y 均为台达轴、不会更换；通用抽象能力未写全） | TA / Y 两轴 | 接受 |
| 2 | ~~`MontionManager.cs` `ExitTaTorque` / `SetWireFeedTorqueMode` / `SetWireFeedTorque` / `StopWireFeedTorque`~~ | ~~硬件层内含角色级应用动作~~ | **2026-11-09 已关闭（ADR-094）**：迁 Workflow 并更名 `ExitTaTorque` / `SetTaTorqueMode` / `SetTaTorque` / `StopTaTorque`；送丝即 TA，⛔ 无第三轴 | — | — |
| 3 | ~~`MontionManager.cs` `MarkTaZeroPose*` / `TaZeroPoseStageChanged` / `BuildMachineInitSummary`~~ | ~~硬件层持有 TA 零位运行态与整机初始化叙述~~ | **2026-11-09 已关闭（ADR-094 D1/D3）**：迁 Workflow；`DescribeAxisDiagnosis` 按 D2 保留硬件层 | — | — |
| 4 | `MotionControlWorkflow.cs` 伺服使能失败日志 | 流程层拼接「状态字 0x%04X」展示文本 | 状态字解读与展示宜由摘要属性承担（仅文本，无位运算） | 单条错误日志 | 低 |
| 5 | `SystemControlPage.cs` 参数保存 | UI 直接取 `MoveData.MotionConfig` 并 `SaveConfig()` | UI 越过流程层直接落盘运控配置 | 参数保存 1 处 | 低 |
| 6 | `WeldParamManager.cs` TA 力值方向归一 | 工艺层直接取 `GetAxisConfigByKeys` 的运控配置 | 方向符合模块依赖图，但工艺层直接耦合运控配置 DTO | TA 力值方向 | 低 |
| 7 | `FilebackupPage.cs` 台达配置视图 | UI 直读运控配置 DTO 做预览 / 导入 | 配置工具页职责，未取轴对象 | 4 张预览表 | 低 |

**已关闭（本轮核查为 0 命中）**：

| 项 | 核查结论 |
|---|---|
| UI 持轴对象 / 解析状态字位 | `MontionAxis` 与 `GetStatusWord()` 在 `UIDesign/` 下 0 命中 |
| Workflow 直接寄存器操作 | `CS_ECAT_*` 在 `MainDeviceControl/` 下 0 命中 |
| Comm / ProductFile 反向依赖运控 | 代码级 0 命中（`DeviceWaitSettings.cs` 仅注释引用 `FlowTimeoutConfig`），见 [[decisions/ADR-093-FlowTimeoutConfigAndLayering]] |



> **2026-10-26 全库审计增补**（本轮 12 项静态审计 + `scripts/csharp_review.py` 全库扫描实测）：
> - **0 消费 private 方法 142 个**（文件内零调用、无委托/事件/`nameof` 引用）——分布：`DeviceWorkflowBase` 契约族（`AdvanceStep`/`IsStepTimeout`/`Log`/`SetWorkTimeStart`/`ReadInt`/`ReadDouble`）、`DeviceStateBase`（`SetWeldStatus`/`CheckDeviceIOSafe`）、`LineLaserCameraBase` 三 `Raise*`、`CommChannelBase.OnDataReceived`、`AlgorithmBase.Preprocess`、~~`ImageAlgorithm.CalculateAngle`~~（2026-10-29 已删）、`LaserWeldHeadWorkflow.GetStepName`、`LineLaserWorkflow.DisposeManaged` 等。⛔ **按 2026-10-10 顶层裁定只登记不删**，其中 `CheckDeviceIOSafe` 属安全钩子、`StepStatusText`/`WorkElapsedMs` 属可观测性 API，**永不因未使用而删除**。2026-10-29 批次 A 已批删 16 个；余仍只登记不删。
> - **疑似死函数 111 个**（`csharp_review.py` C 类提示级；2026-10-29 批次 A 删 16 个后，**2026-10-29 快照口径**）——其中 108 条为 Designer/委托假阳性，2 条待接线（`UpdateParamValues` / `SeamWidthShowRange`）+ `Main`；其余为跨文件 0 引用，删前须逐案确认是否为横切关注点载体（序列化键/日志标签/权限标记/DI 钩子）。**当前状态见下方 2026-11-02 变更两行。**
> - **2026-11-02 变更**：`SeamWidthShowRange` 已废弃并删除 ⇒ 上述快照的「2 条待接线」现为 1 条（`UpdateParamValues`）；连带 `HasEnoughSeamWidthPoints` 转为 0 引用。
> - **2026-11-02 变更（续）**：`DataReviewerPage`「按 X 范围显示区域」模块**整体移除** —— `HasEnoughSeamWidthPoints` 已随模块一并删除；`uiTrackBar1`（`AntdUI.Slider`）已从 `DataReviewerPage.Designer.cs` 移除（实例化 / `Controls.Add` / 属性块 / 字段声明）；专属字段 `TrackbarRate` 已删；`uiGridPanelRight.Span` 由 4 行改为 `"fill;fill;fill 120;-35 fill 35"`。
> - **跨命名空间同名类型 1 组（潜伏 CS0104）**：`EmguALG.Core.LineLaserConfig`（`PreprocessConfig.cs` 内嵌配置类，仅被 `PreprocessConfig` 自引用） vs `LineLaserCam.LineLaserConfig`（现役）。`ILCamPage.cs` 同时 `using` 两个命名空间但未引用该类型 ⇒ **当前不触发**；一旦在该页引用即 CS0104。处置建议（待业主）：EmguALG 侧改名 `LineLaserPreprocessConfig`（0 外部消费者，改名零风险）。
> - **`static class PermissionLevel` 等**：CS0710（static class 禁实例构造）实测 0 命中；`Dispose(bool)` 覆写实测 0 命中（ADR-002 合规）；同名枚举跨命名空间实测 0 命中（ADR-003 合规）。

> **2026-11-17 阶段 8 页面直连核查（ADR-105）**：
> - `UIDesign/TabPage/ILCamPage.cs`：连接/断开改走 `LineLaserWorkflow.ConnectOn()/ConnectOff()`，文件内 `ConnectManual(` / `DisconnectManual(` 0 命中；页面释放不再断设备（D18 关闭）。
> - `UIDesign/TabPage/SystemControlPage.cs`：`BtnStartSim_Click` 启动分支接 `EnsureAdminForWrite("开启模拟测试")`；停止/清理不门控。
> - 全 `UIDesign/` 目录 `MontionManager.Instance.Initialization()/Close()` 0 命中，页面不直连 Manager。
> - 参数显示核对：Y 行取 `ROOT/AXES/AXIS`、TA 行取 `TaAxisConfig + TaHomeConfig`（`ROOT/TA_HOME`）；`AxisConfigForm` 按 `_taHome` 分两套行清单，无单位折算、无新增控件（V15 静态成立）。