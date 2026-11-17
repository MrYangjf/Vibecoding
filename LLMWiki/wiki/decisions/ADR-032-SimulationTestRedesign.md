---
title: "ADR-032：模拟测试统一化重构（平直搭接 + 连接态自动分支 + CSP 轨迹记录器）"
date: 2026-09-17
updated: 2026-10-30
tags: [ADR, 模拟, 线激光, 运控, 焊缝跟踪, VirtualCam, DeviceControlWork, MotionControlWorkflow, SimTrajectoryRecorder, 记录, ADR-042]
status: accepted
---

> **沿革（2026-09-20 · ADR-038 修订）**：「模拟跳过 PreWork」已被部分取代——线激光模拟现走真实 PreWork 命令链（仿真器等完成反馈后再发 Working，真实相机未连自动连接）；运控仍跳过伺服（Working 命令门控直达就绪采样）。模拟行程目标改随机 1500~2000mm，到程由主控 CheckWeldProgress 下发焊接完成。详见 [[decisions/ADR-038-RobotCommandDrivenStepFlow]]。

# ADR-032：模拟测试统一化重构（平直搭接 + 连接态自动分支 + CSP 轨迹记录器）

## 状态

已采纳（2026-09-17，用户裁定：模拟测试流程统一为平直搭接焊缝、取消配置化焊缝类型与 A/B/C 模式、主链按设备连接态自动分支、全部模拟线程归 `DeviceControlWork`、UI 同步删除不再使用的参数；轨迹点由新增记录类缓存并落盘）。

## 背景

模拟测试原设计以「焊缝轮廓类型 + 随机模式 + 模拟模式(A/B/C) + 起点 + 速度 + 目标距离」六项参数驱动，运行期由 `SimTestMode` 枚举（`None/ModeA/ModeB/ModeC`）选择「虚拟相机 / 真实相机」「是否写轴」的不同组合。该设计在迭代中暴露四处问题：

1. **组合冗余**——A/B/C 三模式与「线激光是否连接」「运控是否连接」两个设备事实耦合，用户需手工选择与现场设备状态一致的组合，选错即失败（历史故障见 ~~lessons/SimulationC-Mode-Interruption~~，2026-09-17 有效经验已并入 [[lessons/SimulationAutoBranching]]）。
2. **参数冗余**——焊缝轮廓类型、随机模式在「统一平直搭接」的模拟目标下无意义；起点、速度、目标距离属可内部化的量（起点随机、速度内置），徒增界面与持久化负担。
3. **虚拟相机产帧带宽不可调**——虚拟相机节拍固定 33ms（≈30Hz），无法对齐真实线激光的数据频率（30/60/80/120Hz），模拟链路的跟踪带宽与真实场景脱节。
4. **轨迹不可回看**——模拟场景下「写入 CSP 的每一个点」未持久化，无运控连接时更是只算不留，无法复盘轨迹与工艺调整。

## 裁决

1. **焊缝统一平直搭接（取消配置化）**：`LineLaserConfig` 删除 `SimSeamProfile` / `SimRandomMode` / `SimTargetDistance` / `SimBaseSeamWidth` / `SimBaseSeamDepth` 与全部 XML 读写（`PROFILE` / `RANDOM_MODE` / `TARGET_DISTANCE` / `BASE_SEAM_WIDTH` / `BASE_SEAM_DEPTH` 节点直接消失，存量配置多余键被忽略、**零迁移**）。`VirtualCam` 删除 `SimSeamProfile` 枚举与 `SeamProfile` / `RandomMode` / `TargetDistance` 属性。
2. **虚拟相机直接输出平直搭接轮廓 + 中心焊缝点，且不生成 MAT**：`VirtualCam.GenerateSeamContour()` 固定按平直搭接生成轮廓——**基准 1000 点**，`Y` 均布 `[-halfWidth, +halfWidth]`，`|Y| < seamHalf` 处 `Z = -depth × (1 - |Y|/seamHalf)`（中心搭接缝槽最低点），其余 `Z = 0`，叠加极轻微 `sin` 起伏；`BuildResult()` 取**最接近 y=0 的点**为中心焊缝点（`centerY`/`centerZ`），宽度 = Y 跨度。`Dispose()` 调 `UpdateDisplayMat(null)`——**模拟场景不生成 MAT 给调试界面**（显示由 `LineLaserManager.DisplayEnabled` 网关控制）。
3. **参数精简 + 线激光数据频率可配**：焊接起点不再用户设定（`StartRobotXSimulation` 内 `_simRand.Next(0, 20)` 随机 0~20）；目标距离（默认 1500mm）与模拟速度（默认 60mm/s）**删除**——速度改为内部常量 `SimDefaultSpeedMmPerS = 60.0`；新增 `LineLaserConfig.LineLaserDataFrequencyHz`（默认 30，可选 **30/60/80/120Hz**，XML 路径 `ROOT/SIMULATION/DATA_FREQUENCY_HZ`），经 `LineLaserManager.ApplyConfig()` 套用至虚拟相机 `FrameRateHz`，决定模拟出图节拍（`1000/Hz` ms）与 `ScanRateHz`。
4. **取消 A/B/C 模式，主链按连接态自动分支**：删除 `SimTestMode` 枚举、`EnableSimulation(SimTestMode)`、`CurrentMode` / `SelectedMode` 及派生参数属性；改为**单一开关** `_simulationRunning` + `StartSimulation()` / `DisableSimulation()`，开启时按设备连接态自动判断：
 - **线激光未连接 → 自动用虚拟相机**（`ShouldUseVirtualCamera` = 模拟中且 `_lineLaser.State != Connected`）；
 - **运控未连接 → 不写轴，只记录轨迹点与工艺调整**（`ShouldMoveAxis` = 非模拟恒 true；模拟中取 `_motion.State == Connected`）。
 主链统一为：**线激光结果 → 生成轨迹 → 写运动控制器 → 计算焊缝工艺调整**，由连接态自动决定相机与是否写轴，用户无需选择模式。
5. **模拟线程全部归 `DeviceControlWork`**：子设备工作流（`LineLaserWorkflow` / `MotionControlWorkflow` / `WeldParamControlWorkflow`）**不得新增线程**（沿 ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） 步骤驱动红线）。虚拟相机内置帧 `Timer` 属「相机固有产帧语义」，保留；模拟编排线程仍为 `DeviceControlWork` 内按需线程 `thSimTestWork`。
6. ~~**新增 CSP 轨迹记录器 `SimTrajectoryRecorder`（静态，文件自包含）**~~（**2026-09-20 已被取代**：用户裁定「记录统一到 ProductFileRecordManager，模拟也走这个，不要自己开辟」——`SimTrajectoryRecorder` 删除，缓存+终止落盘语义由 `ProductFileControl/Records/TrajectoryRecord.cs` 原样承接并经 Manager 统一访问，落盘 `Records\yyyyMMdd\`，模拟文件名加「模拟」前缀，`StopRecording` 自动归档 `.ply`/`.pDat`；见 [[modules/ProductFileManager]]）：~~主链每拍写入 CSP 的轨迹点（`robotX` + `cspY` + 工艺调整快照）先**缓存内存**，不逐拍写盘；焊接停止 `FlushToFile()`、模拟关闭 `EndSession()`。**无运控时（`_seamAxis == null`）仍记录**——`RecordOnlyTick()` 以虚拟位置 `_simSeamY` 参与平滑后采样落缓存~~（缓存/无轴记录语义**仍有效**，仅归口变更）。

> 🔄 **2026-09-22 回归修复（决 6「无运控仍记录」曾静默失效）**：ADR-042/049 把闭环基准换成「测量时刻轴值 Ya1」后，`OnSeamLaserResult` 必须传轴位置，而 `MotionControlWorkflow.OnSeamResultReady` 以 `_seamAxis == null` **无条件早退** —— 无轴记录模式从此**永不喂入**，地图恒空，`RecordOnlyTick` 恒 `ready=false`、目标恒 `TeachLockYMm`，轨迹 CSV 退化成常量直线（与 2026-09-20 实测「CspY/AxisY 恒 5.000」同源）。修复：① 早退放宽为「无轴且（模拟记录 + CSP）才继续」，轴位置以虚拟轴 `_simAxisPos` 顶替（新增 `SeamAxisPosMm` 集中取数）；② `OnSeamTrackingStart` 内 `BeginSeamTrackingCorrection()` 上移至判轴 `return` 之前（算法 `_isTracking` 门禁）。判据：**「无轴另开一路」只是半程，喂入通路与算法激活两道门槛缺一不可**。见 [[lessons/SimulationAutoBranching]] 陷阱十九 · [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（其负面条款第 1 条同步演进）。
7. **`StepCspTarget` 解耦轴读取**：签名由 `StepCspTarget(MontionAxis axis, …)` 改为 `StepCspTarget(double current, …)`——真实/模拟带轴传 `axis.GetPosition()`，无轴（模拟记录）传虚拟 `_simSeamY`；写入仍由 `OutputCspTick()` 在 `_seamAxis != null` 时执行，无轴走 `RecordOnlyTick()`。
8. **UI 同步精简 + 模拟测试跨页迁移（回填 2026-09-17）**：`MotionControlPage` 删除 `cmbProfile` / `chkRandom` / `cmbSimMode` / `txtStartX` / `txtSpeed` / `txtTargetDist` 及对应标签，**降级为壳页**（`Designer.cs` 仅占位 `panel1`/`MontionControlPanel`，`.cs` 仅 `InitializeComponent()`，运动轴参数待完成）；**模拟测试全部控件与逻辑整体迁回工艺配置页 `ParamConfigPage` 的 `tbPanelSimTest`**（原 `MotionControlPage.tableLayoutPanel2` 重命名为 `tbPanelSimTest`；标题 Label 由 `label1` 改名为 `lblSimTestTitle`，避免与 `tbPanelAdaparam` 内既有 `label1` 重名导致 CS0102 编译错误）；迁移控件 = `lblSimTestTitle` / `lblFreq` / `cmbFreq`（30/60/80/120Hz，`FrequencyToIndex` / `IndexToFrequency`）/ `btnSaveSim` / `btnStartSim`，方法 `PopulateComboBoxItems` / `LoadFromModel` / `BtnSaveSim_Click` / `BtnStartSim_Click` 等随之迁至 `ParamConfigPage.cs`；`ParamConfigPage` 同期将 `tlPanelWeldPoints` 改名为 **`tbpanelweldponts`**（线激光标定：标定比例/前置距离/示教中心/示教Y轴点/Y行程上下限 + 整合 6 个残留控件）并新增 **`tbPanelAlogControl`**（轨迹滤波算法：点滤波 + 防错 + Cps + PVT，参考 `tbPanelAdaparam` 排列），与既有 `tbPanelAdaparam`（焊接工艺自适应调参模型）共同构成 2×2 网格（`tableLayoutPanel7`：左上 `panelWeldList`→`tbPanelAdaparam`、右上 `panel1`→`tbpanelweldponts`、左下 `tbPanelAlogControl`、右下 `tbPanelSimTest`）。

> 🔄 **2026-09-22 演进（[[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]）**：上段所述 `tbpanelweldponts`（线激光标定）与 `tbPanelAlogControl`（**「轨迹滤波算法」→ 已改名「轨迹点控制」**）两面板**已二度重组**——标定面板收窄为**纯标定 5 项**（6 列 × 5 行），轨迹点控制按五组重排（**4 列 × 34 行**）并**真删 PVT 参数 11 个控件**；本条中「点滤波 + 防错 + Cps + PVT」的四段划分**已不再适用**，现行结构见 [[api/ProcessControlPage]]。

## 备选方案（已否决）

- **保留 A/B/C 模式、仅在界面提示「按连接态选择」**（否决）：模式仍需用户判断设备连接态，与「自动判断」诉求方向相反，且枚举派生属性会继续扩散。
- **无运控时不记录、仅日志**（否决，用户裁定）：用户明确要求「没有运动控制器就不运动只记录轨迹点和工艺调整」，轨迹须可回看。
- **逐拍直接写文件**（否决，用户裁定）：逐拍写盘耗时且抖动，改为「先缓存、运动终止一次性落盘」。
- **虚拟相机节拍改由外部线程驱动**（否决）：违反 ADR-042「子设备工作流不得自起线程」；虚拟相机自带 `Timer` 属相机固有产帧语义，保留但不再新增编排线程。
- **虚拟相机生成 MAT 供调试界面显示**（否决，用户裁定）：模拟流程**不生成 MAT**（`UpdateDisplayMat(null)`）。

## 后果

- 正面：模拟入口收敛为单一开关 + 连接态自动分支，用户无需理解设备组合；模拟参数面从 6 项收敛为 1 项（数据频率）；虚拟相机产帧频率与真实线激光对齐；轨迹与工艺调整可落盘回看，无运控亦可复盘。
- 负面 / 约束：
 - **`SimTestMode` 枚举彻底移除**——凡引用旧枚举/旧属性的外部代码须同步改写（本轮已清理 `MotionControlPage` / `DeviceControlWork` 全部引用，全库 0 残留）。
 - **存量 INI 冗余键**：`bin/**/Config/MainDeviceControl/Simulation_INI/SimulationController.ini` 与 `MotionControlWorkflow.ini` 仍含旧键（`SimStartX` / `SimSpeed` / `SimTargetDistance` / `SeamProfile` / `RandomMode`），无害但陈旧；新代码只读 `LineLaserDataFrequencyHz`。
 - **真编译待 Visual Studio**：本次交付经 Python 静态校验（csproj 注册全量存在、废弃符号全库 0 残留、新符号就位、括号平衡、行尾均质、命名空间对齐），**真编译未完成**。
 - **轨迹落盘口径**：`FlushToFile()` 在焊接停止（`_seamTrackingActive` 由真跌假）时调用一次，`EndSession()` 在模拟关闭时再兜底落盘；同一会话多次启停焊接会追加到同一 CSV（表头只写一次）。
 - **模拟轨迹记录依赖运动工作流跑通 `UpdateSeamTracking`**：`MotionControlWorkflow.FlowProcess` 在模拟态放开 `IsEnable` 门禁（真实态仍保留），否则模拟无运控时 `FlowProcess` 早退、`UpdateSeamTracking` 不执行、轨迹 CSV 仅表头（「无运控仍记录」见 ADR-032 原裁定）；`SimSkipPreworkToWorking` 真实相机分支须与虚拟分支一致调用 `StartAcquisition()`，否则不产轮廓帧（`_frames` 为空 → 界面无数据、归档文件数 0）。

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- API：[[api/VirtualCam]]（平直搭接 1000 点 + 频率可配）· [[api/DeviceControlWork]]（`StartSimulation` / `ShouldUseVirtualCamera` / `ShouldMoveAxis` / `SimLaserFrequencyHz` / `SimTrajectoryRecorder`）· [[api/ProcessControlPage]]（UI 精简：模拟测试面板 + 线激光标定/轨迹点控制面板（2026-09-22 改名））· [[api/MotionControlWorkflow]]（`RecordOnlyTick` / `StepCspTarget` 解耦）
- 模块：[[modules/LineLaserCam]]（`LineLaserConfig` 数据频率）· [[modules/DeviceControl]]
- 前序：ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）（步骤驱动红线 · CSP 输出）· [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（CSP 目标）· [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] · ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）
- 教训：[[lessons/SimulationAutoBranching]]（本 ADR 沉淀，含承继的 A/B/C 时代经验；原 lessons/SimulationC-Mode-Interruption 页 2026-09-17 并入后删除）
