---
title: 模拟测试按设备连接态自动分支（取消模式选择）
date: 2026-09-17
updated: 2026-11-24
tags: [教训, 模拟, 线激光, 运控, 工作流, 线程, 记录, 机器人位姿, ADR-042, ADR-032, ADR-039, ADR-042]
status: active
source: AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs, AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs, AdaWeldSystem/ProductFileControl/Records/SeamTraceYRecord.cs, AdaWeldSystem/WeldParamControl/WeldParamManager.cs
---

# 模拟测试按设备连接态自动分支（取消模式选择）

> **背景**：模拟测试原以 `SimTestMode` 枚举（`None/ModeA/ModeB/ModeC`）让用户显式选择「虚拟相机 / 真实相机」「是否写轴」的组合。
> 2026-09-17（[[decisions/ADR-032-SimulationTestRedesign]]）取消模式选择，改为**单一开关 + 按设备连接态自动分支**。
> 本页沉淀该重构的设计要点与实现陷阱。

## 核心设计：模式由设备事实派生，不由用户选择

模拟的「怎么跑」完全由两个设备连接态决定，无需任何界面参数：

```
线激光未连接 → 自动用虚拟相机        ShouldUseVirtualCamera = 模拟中 && 线激光.State != Connected
运控未连接   → 不写轴、只记录轨迹     ShouldMoveAxis = !模拟 || 运控.State == Connected
```

- 属性实现必须是**纯计算**（每次读实时连接态），不可缓存成字段——否则设备中途连接/断开后分支不再更新。
- 真实运行时（未开模拟）`ShouldMoveAxis` 须恒 `true`（保证真机正常写轴），`ShouldUseVirtualCamera` 须恒 `false`（保证用真机相机）。
  ```csharp
  public bool ShouldMoveAxis {
      get { if (!_simulationRunning) return true;          // 非模拟：永远写轴
            return _motion.State == SubDeviceState.Connected; } }
  ```

## 陷阱一：无轴时 `_seamAxis == null`，主链整体早退 → 轨迹丢失

模拟且运控未连接时，轴未装配（`_seamAxis == null`），`MotionControlWorkflow.UpdateSeamTracking()` 开头的 `if (_seamAxis == null) return;` 会让**整条焊缝跟踪链停摆**，轨迹点一个也算不出来。

**修法**：把「整体早退」改为「记录模式另开一路」——
```csharp
bool simRecordOnly = DeviceControlWork.Instance.IsSimulationEnabled
                     && !DeviceControlWork.Instance.ShouldMoveAxis;
if (_seamAxis == null && !simRecordOnly) return;   // 仅记录模式不再早退
...
if (_seamAxis == null) RecordOnlyTick();           // 无轴：虚拟位置平滑 + 记录
else OutputCspTick();                              // 有轴：写控制器 + 记录
```
`RecordOnlyTick()` 以虚拟位置 `_simAxisPos`（工作流私有字段，初值 0）参与平滑，逐拍 `_simAxisPos = command` 推进，轨迹连续可记录。

> 🔄 **2026-09-22 演进**：「另开一路」只是**半程**——还须同时打通 ① **喂入通路**（相机特征帧进算法地图）与 ② **算法激活**（`_isTracking` 门禁）。缺任一，`RecordOnlyTick` 都取不到地图目标、轨迹仍是常量直线。详见本页**陷阱十九**。

## 陷阱二：把「读轴位置」写死在平滑函数里 → 无轴崩溃

`StepCspTarget` 原签名 `StepCspTarget(MontionAxis axis, double target, double tickSeconds)`，内部 `axis.GetPosition()`。
无轴场景直接空引用。**修法**：解耦成 `StepCspTarget(double current, …)` —— 调用方决定 `current` 来源：
- 有轴：`axis.GetPosition()`（真实/模拟带轴一致）；
- 无轴：`_simAxisPos`（虚拟位置跟踪）。

> 经验：**纯计算函数的入参应显式化**。凡是「从某对象取一个数」的取数逻辑，都应在调用方完成，函数只接收值——这样同一算法既能跑真机也能跑模拟回放。

## 陷阱三：轨迹逐拍写盘 → 抖动

用户明确：**「写入每一点先记录在缓存，等运动终止时一次性写文件」**。

~~`SimTrajectoryRecorder`（静态、`lock` 保护缓存）~~（**2026-09-20 演进**：删除并并入记录模块 `ProductFileControl/Records/TrajectoryRecord.cs`；**2026-09-24 再演进**：该类改名为 `SeamTraceYRecord.cs`，列改为入图/出图/轴反馈 5 列，经 `ProductFileRecordManager` 统一访问，模拟/真实同通道，文件落 `Records\yyyyMMdd\`，模拟加「模拟」前缀——用户裁定「记录统一到 ProductFileRecordManager，模拟也走这个，不要自己开辟」）：
- `BeginSession()`（`StartSimulation` 调）→ 建带时间戳 CSV + 表头；
- `RecordPoint(...)`（每拍）→ 仅入内存 List，**不碰磁盘**；
- `FlushToFile()`（焊接停止沿 `_seamTrackingActive` 真跌假时）→ 缓存批量 append + 清缓存；
- `EndSession()`（`DisableSimulation` 调）→ 兜底落盘并复位。

> 经验：**热路径只入内存、终止时批量落盘**。写盘失败仅告警、**缓存保留**以便下次重试，不要清缓存后再写。

## 陷阱四：以「模拟」为名新增线程 → 违反步骤驱动红线

ADR-042（内容并入 ADR-027）起，**子设备工作流不得自起常驻/长生命周期线程**（主工作即全阻塞 `FlowProcess`，由编排层常驻线程驱动）；**短生命周期线程允许**（如 `ConnectOn/ConnectOff`），但须 `IsBackground=true` 且 `finally` 释放资源；模拟编排线程只放 `DeviceControlWork`（`thSimTestWork`）。
虚拟相机内部保留的 `System.Threading.Timer` 属**相机固有产帧语义**（相机自己怎么出帧），不是编排线程，允许保留。
判定口径：**新增的线程是在「驱动流程推进」还是「模拟硬件自身行为」**？前者禁止，后者允许。

## 陷阱五：工艺参数模拟态不得下发机器人（只记录）

用户的第 6 条行为：**「参数调整模拟不需要发送给机器人，只记录就可以」**。

`WeldParamControlWorkflow.DoOutput()`（执行步 20）在模拟态（`DeviceControlWork.Instance.IsSimulationEnabled`）直接置 `_output.Success = true` 返回，**跳过 `SendToRobot`**——这样 `LineLaserWorkflow.RunAutoAdjust → ComputeAndOutput` 的模拟链路照常计算并写 `LastOutput`（UI 折线图可看），但不向真实 KUKA 发送模拟工艺参数。

> ⚠️ **与陷阱一/ShouldMoveAxis 区分**：运控轴是否写轴由「运动控制器连接态」决定（`ShouldMoveAxis`，用户第 5 条：连接+y轴在则运动）；而工艺参数下发与机器人相关，**模拟态一律不下发**。两者红线口径不同，不能混为一谈。也不要在模拟态用 `DetachSeamTrackAxis` 之类手段去"堵"下发——那会误伤运控记录路径（轴空 + 未连接判定下 `UpdateSeamTracking` 整体早退，既不运动也不记录）。

## 陷阱六：模拟态异常残留清不掉 → 清理与启动互相锁死（2026-09-20）

现象：点击「开启模拟流程」直接进入异常清理（日志指纹：`Stop 忽略 当前状态 ErrorAborted` → `复位拒绝 当前未连接` → `异常清理恢复`），且再次点击永远是清理，模拟永远起不来，只能重启软件。

根因三连环：
1. **安全互锁无模拟旁路**：模拟 `DoStartMachine()` 会拉起 `thIOWork`，`SafetyInterlockChecker.Check()` 在无硬件环境（PLC 未连 / 设备未就绪 / 机器人未在线）必然不通过 → `ReportAlarm` → 整机进 Alarm → 五条子流程线程停止驱动。修复：`IOWork` 模拟态整体旁路互锁检查。
2. **ErrorAborted 残留不可清理**：清理链三处全失效——`Stop()` 对 ErrorAborted 忽略；线激光 `ResetProcess()` 以未连接拒绝；运控 `Stop()` 对 Error 相位直接 return。修复：三者各加模拟分支（`IsSimulationEnabled` 时强制回 Idle/Standby 并清 `IsAlarm`），未连接/未初始化不再作为拒绝理由。
3. **启动守卫过粗**：`BtnStartSim_Click` 对"历史 ErrorAborted 残留 + 模拟未开启"也强制进清理分支。修复：守卫收窄为 `_simError || (模拟运行中 && ErrorAborted)`；残留态由启动链的 `ResetProcess` 模拟分支清掉后正常启动。配套 `SubscribeLineLaserEvents` 改为先退订再订阅（幂等防回调翻倍）。**2026-09-22 补强**：整机在模拟运行中进入报警（如运控总线故障 `ReportAlarm`/`DoMotionBusFault`）时，`SimScheduleTick` 守卫只判 `EStop`+子设备 `ErrorAborted`、不判 `Alarm` → 模拟不会自动停、按钮仍显「停止」；若仅走 `DisableSimulation`（`Current==Running` 才转 `Stop`）不会自动离 `Alarm`。故守卫再扩 `|| (模拟运行中 && 整机 Alarm)`，统一路由 `CleanupSimError()` 的 `ClearAlarm`——保证「测试报警→清除报警」单键可达（与陷阱十八同源）。

> ⚠️ 通用教训：**凡加"异常终止"态的流程，必须同时保证异常态可被复位链清除**；"未连接拒绝复位"这类真实链路守卫，在模拟分支里要显式放开，否则一次失败即永久锁死。

## 陷阱七：模拟无机器人指令 → 子流程启动级联缺失 + 二轮模拟误选真实相机（2026-09-20）

现象：模拟启动后日志停在「跳过 PreWork 直接就绪」，流程不再推进；用户裁定——**真实流程靠机器人指令触发启动（S2→S3→S4），模拟没有机器人指令，须自动补发转换指令**。

两个根因，一次修复：
1. **启动级联缺失**：真实流程由机器人指令（IoSubPrework / IoSubWork → DoSubPrework / DoSubWork）级联驱动子流程进入工作态，模拟无此指令。修复：`DeviceControlWork.SimAutoStartSubflows()` 在模拟进入 Running 后自动补发等效级联（PreWork → Working），**只作用于模拟参与子流程（线激光 / 运控 / 工艺参数）**——焊接头与监控相机是模拟停驱设备，不参与级联，避免残留非真实工作态；`DisableSimulation` 时工艺参数控制回 Standby 清残留。
2. **二轮模拟误选真实相机**：`ShouldUseVirtualCamera` 原以 `线激光State != Connected` 判断，但上一轮模拟结束后线激光 State 保持 Connected（虚拟相机）→ 第二轮模拟误选真实英莱相机 → 无数据 → `DoWorking` 卡在等有效结果（`线激光识别失败 ParseRes 非 1` 迟到）。修复：已连接时再按 `LineLaserManager.IsVirtual` 判断——虚拟相机保持虚拟，真实相机才复用真实。

> ⚠️ 通用教训：**「按连接态复用设备」的判断必须区分真实连接与虚拟残留连接**；模拟会改变设备状态机，轮次之间的状态残留是模拟测试的高发踩坑区（与陷阱六同源）。

## 陷阱八：记录链「静默死亡」+ 查表宽度序列无喂数 + 主界面曲线无喂数（2026-09-20）

用户裁定三连：**「记录统一到 ProductFileRecordManager，模拟也走这个，不要自己开辟」「现在默认记录数据不加密」「模拟数据的模拟方法都在模拟类实现，统一在一个地方，不要到各子流程各写一坨」**。排查发现三条断裂链，全部是「**有产出、无消费/无喂数**」型死链：

1. **记录会话无人启动**：`StartRecording()` 全库 0 调用方 → `Enqueue` 的 `IsRecording` 门禁把点云帧（`LineLaserManager.AddFrame` 每帧投递）与过程快照**全部静默丢弃**；且 `StopRecording` 原实现只删临时文件、`SaveRecord` 从无人调——`.ply`/`.pDat` 正式文件**从不出现**。修复：`StopRecording` 自动归档；模拟/真实统一在焊接启动命令开记录、停止命令关记录（均幂等）。
2. **查表宽度序列无喂数**：`SeamCalData.AddSeamWidth()` 全库 0 调用 → 滑动平均序列永远不足 `CountNum` → 查表**从未按实测宽度触发**（模拟与真实同样失效）。修复：`WeldParamManager.TriggerAdjustment()` 触发前喂入 `LineLaserManager.LastResult` 最近一帧宽度（宽度序列唯一喂数入口，统一收口 Manager，不散落子流程）。
3. **主界面曲线无喂数**：`MainPage` 四条工艺曲线 `ChartVar` 只创建与绑定、无任何 Add 调用 → 永远空白。修复：MainPage 订阅 `WeldParamManager.WeldProcessCompleted`（每次 `ExecuteAdjustment` 触发）追加数据 + BeginInvoke 刷新。

另：模拟机器人位姿（XYZ）现由 `DeviceControlWork.SimTick` 统一虚拟、经 `WeldParamManager.UpdateRobotPose(x, y, z)` **单入口**喂入（X 随节拍推进、Y/Z 恒 0；真实链路仍由 RSI 回包刷新）——模拟数据生成统一收口在模拟数据源（DeviceControlWork 模拟区 / VirtualCam），不在子流程各写一坨。**2026-09-22 收口**：原「SimTick 直写 `CurrentRobotX` + `GetEffectiveRobotX` 直读本地 `_simRobotX` 字段」的双源已合并为单源（见陷阱十七）。

> ⚠️ 通用教训：**接手"数据看不见"类问题，先查三类死链——门禁无人开门（会话/开关从未启动）、序列无人喂入（Add 方法 0 调用方）、UI 无人消费（ChartVar/缓存 0 读取方）**。产出端日志正常 ≠ 链路通。
>
> **演进（2026-09-20 同日）**：主界面工艺曲线喂数已由 `WeldProcessCompleted` 事件订阅改为**主界面轮询**（`ProfilePollLoop` 读 `WeldParamManager.AdjustmentOutputVersion` 判重后增量消费算法缓存）——死链第三类的形态随之变化：现在要查的是「**版本号不自增**（算法改缓存忘推版本）」或「**轮询端没接**」，而不是「UI 无人订阅」。

## 陷阱九：模拟行程到程 X 不自动停（2026-09-20，Bug 1 / ADR-039 决 1）

现象：机器人 X 从 15 一路跑到 7000 mm 仍不停止，只能人工点「停止」。
根因：`CheckWeldProgress()` 行程完成后只调 `DoSubStop()`（级联子设备 `Stopping`），**不终止主控模拟线程、不停止 robotX 时钟**——`SimTick` 持续把 X 往前推。
修复：行程到程后调 `DisableSimulation()`，使 robotX 时钟与模拟编排线程停止、记录落盘。
> ⚠️ 通用教训：**行程判断归主控**（ADR-038），到程不仅是「子设备停下」，更是「整段模拟结束」。

## 陷阱十：焊缝跟踪轴名须匹配实际轴，否则轨迹/工艺记录全空（2026-09-20，Bug 2 根因 / ADR-039 决 4）

现象：`.csv` 轨迹文件空、`.pDat` 也无轨迹点，但线激光在跑。
根因：`SeamTrackAxisName` 默认 `"Y轴"`，而 `DeltaMotionConfig.xml` 实际轴名为 `送丝力矩电机`/`Y向电机`/`Z向对焦电机`（**无 "Y轴"**）→ `_seamAxis == null` → `MotionControlWorkflow.UpdateSeamTracking()` 早退 → 轨迹点零产出。（彼时该字段在 `LineLaserConfig`，2026-09-20 ADR-033 已迁出至运控 `DeltaMotionConfig`。）
修复：`SeamTrackAxisName` 默认值（现位于运控 `DeltaMotionConfig`，2026-09-20 ADR-033 迁出）改为 `"Y向电机"`（与运控实际轴名对齐）；`DeltaMotionConfig.xml` 为空时不覆盖默认值，故默认值须与运控实际轴名一致。
> ⚠️ 配置约束：**凡是「按名取轴/取设备」的配置项，默认值必须等于 `DeltaMotionConfig.xml` 中真实存在的名字**，否则解析为 null 后整条链路静默早退（与陷阱一同源，但触发点是配置默认值而非连接态）。

## 陷阱十一：虚拟相机分支须触发 ComputeAndOutput，否则 .pDat 空（2026-09-20，Bug 2 另一因 / ADR-039 决 1 旁）

现象：虚拟相机下 `.pDat` 工艺过程帧空。
根因：`LineLaserWorkflow.DoWorking()` 虚拟相机分支只置 `_lastResultValid=true` 后 return，**从不调 `ComputeAndOutput`** → 工艺计算链不驱动 → `.pDat` 无填充。
修复：虚拟分支改调 `WeldParamControlWorkflow.Instance.ComputeAndOutput()`（包 try/catch 记日志），使 `.pDat` 按拍填充；实际计算在 `WeldParamControlWorkflow` 自身流程线程消费 `_pendingCompute` 时执行。
> ⚠️ 与陷阱十区分：轴名错导致「轨迹点算不出」（CSV 空），虚拟分支不调 ComputeAndOutput 导致「工艺帧不写」（PDAT 空）——两个独立死链，任一都会让记录文件空。

## 陷阱十二：SaveRecord 落盘后须释放内存缓存（2026-09-20，Bug 3 / ADR-039 决 3）

现象：线激光正常模拟时内存持续上涨，点停止后不回落；手动点「测试线激光」反而内存下降。
根因：`RecordFileStore.SaveRecord()` 把 `.ply`/`.pDat` 落盘后**不清空** `_frames`/`_actionRecords` 内存列表 → 缓存常驻、只增不减。
修复：`SaveRecord()` 持久化完成后 `_frames.Clear()` + `_actionRecords.Clear()`；崩溃恢复以 `.tmp` 文件为准，无需常驻内存。
> ⚠️ 通用教训：**数据一旦落盘，内存缓存即应释放**（用户原话：「记录数据到本地后，所有的缓存数据都需要释放」）。热路径只入内存、终止/落盘时批量清缓存，是模拟长时运行不爆内存的前提。

## 陷阱十三：模拟期子设备报警须自动终止模拟（2026-09-20，Bug 4 / ADR-039 决 2）

现象：日志显示轴移动报警，模拟却不停止、继续跑（且实际用的是送丝力矩电机而非 Y 向电机）。
根因：`SimScheduleTick()` 原无异常守卫，子设备 `ErrorAborted` 或整机 `Alarm`/`EStop` 时模拟继续推进。
修复：`SimScheduleTick()` 顶部守卫——`Current == Alarm || Current == EStop` 或任一子设备 `WeldStatus == ErrorAborted` 时，立即 `EndProductSessionSafely("fail", …)` + `DisableSimulation()` 后 return。
> ⚠️ 通用教训：**模拟是「假运行」，但异常处置必须和真机同口径**——子设备一旦进入异常/报警态，模拟须同步终止并落「fail」记录，不能「假装没看见」继续跑。

## 陷阱十四：报警守卫与启动时序竞态——「开启即结束」（2026-09-20 第二轮 / ADR-039 决 2 演进）

`SimScheduleTick` 顶部守卫若含 `Current == Alarm`，而 `StartSimulation()` 里 `SimTestWorkOpen()` 又排在 `DoClearAlarm()` 之前：初始化部分失败残留的 Alarm（实验台无监控相机是常态）会在模拟线程**首拍（10ms 内）**被守卫读到 → 模拟刚拉起即被 `DisableSimulation` 误杀，UI 按钮却已置「停止」——日志显示结束、按钮状态失同步。
**规避**：① 守卫只判 `EStop` + 三个参与设备 `ErrorAborted`（模拟不判真实硬件态，ADR-042）；② 模拟线程启动必须置于清警/进 Running 之后。守卫从「宽」改「窄」时，先枚举启动窗口期所有可能残留的状态再收口。

## 陷阱十五：秒级落盘上 UI 线程——停止按钮「卡」+ 状态残留误判「没有停止」（2026-09-20 第二轮 / ADR-039 决 5）

`DisableSimulation()` 在按钮点击处理器内同步调 `EndProductSessionSafely`，87.8MB `.ply` 写盘 3.2s → UI 冻结。且停止只复位线激光/焊参：监控残留 `Working`、V3 卡 `Stopping`（`Current→Stop` 后 FlowProcess 不再驱动，`Stopping` 迁移永不执行）——用户体感「点了停止没停」。
**规避**：① 归档移后台线程（UI 路径）；② 停止须**对称复位全部级联态**——Working 级联到几个子设备，停止就复位几个；③ 模拟态无硬件可平滑停，`Stopping` 受理后直接归 `Idle`。

## 陷阱十六：配置 XML 不随包分发——现场轴名/轴地址漂移（2026-09-20 第二轮 / ADR-039 决 5.3）

`backup_adaweld.py` 排除 `bin/`，output 包到现场后 `DeltaMotionConfig.xml` / `LineLaserConfig.xml` 仍是旧文件：代码默认值已改 `Y向电机`，实测机运行时仍报「未找到焊缝跟踪轴 Y轴」（本地 XML 覆盖默认值）→ 轨迹 `.csv` 全空；Y 向电机 `NODE_ID` 与实测机硬件地址不符 → 伺服控制落空。
**规避**：出包交付时**必须附配置同步清单**（逐个 XML 列出须人工核对的键值）；凡「代码默认值 + 可被 XML 覆盖」的配置，初始化日志要打印生效值，便于现场比对。

## 陷阱十七：模拟态位姿双源 -> 特征帧被 `_hasRobotY` 门禁整帧丢弃（2026-09-22）

现象：模拟测试闭环诊断行恒 `特征Y 0.000 特征修正 0.000`，但记录数据里相机特征 `SeamPointY` 约 -1.2mm **非零**——数据从相机一路到记录层，只卡在「进算法修正」这一步。

根因：`SeamMapTrackingAlgorithm.OnLaserResult` 有 `if (!_hasRobotY) return;` 门禁，而 `_hasRobotY` 只在 `OnRsiPose -> ProcessRsiPose -> FilterRobotY`（`SeamMapTrackingAlgorithm.cs:513-519`）内被置位。真实链路 RSI 回包会喂位姿；**模拟态无网络机器人，从不喂位姿 -> `_hasRobotY` 恒 false -> 每帧线激光特征被整帧丢弃** -> 特征Y/特征修正恒 0。

同时存在**两处模拟源**：① `SimTick` 直写 `WeldParamManager.CurrentRobotX`；② `GetEffectiveRobotX()` 直读本地 `_simRobotX` 字段（被 LineLaser 轮廓对齐 / Motion 轨迹记录 / 焊缝行程监视多处消费）。两者数值同源却各自成一份「当前机器人 X」真相。

修复（**单源收口**）：
1. `WeldParamManager` 新增 `UpdateRobotPose(double x, double y, double z)`——写 `RobotWeldData.PosX/Y/Z`（注意 `CurrentRobotZ` 仅 getter，须直接写载体字段）后调 `_seamMapTrackingAlgorithm.OnRsiPose(x, y, z)`，**写载体不受 `_isTracking` 门禁影响**（门禁在 `OnRsiPose` 内，位姿快照先落地）。
2. `SimTick` 改 `WeldParamManager.Instance.UpdateRobotPose(_simRobotX, 0.0, 0.0)`——模拟路径统一虚拟 XYZ（X 推进、Y/Z=0），经**单入口**喂入置位 `_hasRobotY`；删除原 `CurrentRobotX = _simRobotX` 直写。
3. `StartRobotXSimulation` 开启后即时喂一次初值，避免沿用上一轮真实运行的残留位姿。
4. `GetEffectiveRobotX()` 改为返回 `WeldParamManager.Instance.CurrentRobotX`（模拟态），删除对 `_simRobotX` 的直接读取；非模拟态保持返回 0.0 的原语义。

> 通用教训：**模拟「有多少个源」比「源对不对」更致命**——只要模拟位姿存在第二条读/写路径，算法门禁、记录对齐、行程监视就会各读各的。**模拟数据必须只有一个生成点（模拟线程）+ 一个喂入入口（Manager 单方法）+ 一个读取载体（Manager 属性）**。判据：全库检索被模拟置位的字段，若它在「生成侧」被写、又在「消费侧」被直接读，即为潜在双源。
> 与陷阱八区分：陷阱八讲「死链无人喂数」，本条讲「喂了但被门禁拦截 + 又多开一路源」。

## 其它要点

- **虚拟相机不生成 MAT**：模拟场景 `Dispose()` 调 `UpdateDisplayMat(null)`，调试界面图片由 `LineLaserManager.DisplayEnabled` 网关控制。
- **焊缝统一平直搭接**：轮廓基准固定 1000 点，中心焊缝点 = 最接近 `y=0` 的点（不再按轮廓类型/随机模式分支）。
- **参数面收敛**：模拟参数从 6 项（轮廓/随机/模式/起点/速度/目标距离）收敛为 1 项（线激光数据频率 30/60/80/120Hz）；起点内部随机 0~20、速度内部常量。
- **阈值/枚举删除要全库清零**：删 `SimTestMode` 后，凡引用旧枚举/旧属性的 `.cs` 必须同步改写（本轮 `MotionControlPage` / `DeviceControlWork` 全清），否则编译必失败。

## 承继自 A/B/C 时代的经验（原 lessons/SimulationC-Mode-Interruption，2026-09-17 并入后删除）

- **模拟链路要自驱动推进**：模拟流程不能依赖「生产模式才有的驱动事件」，状态机无人驱动会卡死在首阶段（现行由 `DeviceControlWork` 模拟编排驱动）。
- **虚拟相机要能产帧**：无帧则工作流连续失败中断；产帧节拍见 [[api/VirtualCam]]。
- **按钮状态复位必须放 `finally`**：「清理异常/复位界面」类操作的 UI 复位不得依赖后端调用成功。
- **启动异常要给 UI 反馈**：启动路径的 catch 不得只记日志，需弹窗——无需确认用 `AntdUI.Message`，需确认用 `AntdUI.Modal`。
- **停止反馈分两层 + `Disable` 要幂等**：底层状态迁移日志之外输出「人话」式停止确认（设备态+流程态+原因）；同一停止动作可能被多条路径触发，须以状态变化为前置条件，避免重复日志与重复副作用。

## 陷阱十八：模拟运行中整机报警须显式改变通知按钮为红字「清理异常」（2026-09-22）

现象：整机在模拟运行中因运控总线故障等进入 `Alarm`（`ReportAlarm`/`DoMotionBusFault`），但 `SimScheduleTick` 守卫只判 `EStop`+子设备 `ErrorAborted` 不判 `Alarm` → 模拟不自动停，按钮仍显示「停止」。用户点「停止」走 `DisableSimulation`，而它仅在 `Current==Running` 时转 `Stop`，对 `Alarm` 不自动离警 → 单键清不掉报警。

前置修复（2026-09-22 守卫扩第三条件）：`BtnStartSim_Click` 清理分支新增 `(模拟运行中 && 整机 Alarm)` → 路由 `CleanupSimError()`（含 `ClearAlarm`），保证单键清警。

本增强（2026-09-22）：仅单键可达还不够——报警后按钮**状态须显式改变**以提示用户。新增 `OnMainDeviceStatusChanged` 订阅 `DeviceControlWork.StatusChanged`：模拟运行中 `NewStatus==Alarm` 时 `ShowSimErrorDialog` 弹窗 + 按钮 `SetSimButtonMode(Cleanup)` 显式变红字「清理异常」（与子设备 `ErrorAborted` 路径视觉一致）。订阅随模拟启停上收（`BtnStartSim_Click` 订阅；`OnSimulationStopped`/`CleanupSimError`/`HandleDestroyed` 退订），`SetStatus` 可能工作流线程触发 → 处理器做 `InvokeRequired` 封送。

> ⚠️ 通用教训：**「事件通知按钮」的状态必须跟随事件源显式切换**，不能停留在上一态等用户盲点；报警/异常入口应与正常态视觉区分（红字），且清理逻辑须单键可达。

## 陷阱十九：无轴记录模式「地图无喂入」——两道门槛缺一即退化为常量直线（2026-09-22）

现象（只读审计发现，未上机）：模拟且运控未连接时 `ShouldMoveAxis == false`、`_seamAxis == null`，`UpdateSeamTracking` 正确地走 `RecordOnlyTick()`，但轨迹 CSV 的 `CspY/AxisY` **恒等于 `TeachLockYMm`**，不体现任何焊缝特征；与 2026-09-20/09-22 实测「CspY/AxisY 恒 5.000」「闭环诊断行恒 0」同源。

根因（两道门槛，任一缺失即死链）：

1. **喂入通路断**：ADR-042/049 把闭环基准换成「测量时刻轴值 Ya1」后，`OnSeamLaserResult(result, axisPosMm)` 必须传轴位置，而 `MotionControlWorkflow.OnSeamResultReady` 以 `if (_seamAxis == null) return;` **无条件早退** —— 该方法是**全库唯一**的地图喂入点，无轴时一次也不喂 → 地图恒空。
2. **算法门禁断**：`OnSeamTrackingStart` 里 `BeginSeamTrackingCorrection()` 排在 `if (!cspMode || _seamAxis == null) return;` **之后**，无轴时根本不执行 → `SeamMapTrackingAlgorithm._isTracking` 恒 false → 位姿帧与特征帧被 `OnRsiPose` / `OnLaserResult` 整帧丢弃。即使补了第 1 条也仍然为空。

修复（仅 `MotionControlWorkflow.cs` 三处）：

- 新增判断辅助属性 `SeamAxisPosMm`（有轴取 `_seamAxis.GetPosition()`、无轴取 `_simAxisPos`），把「Ya1 取数」集中到一处，消除 `_seamAxis == null` 三元散写；
- 早退放宽为两条：`_seamAxis == null && !IsSimRecordOnly` → return（非记录模式照旧早退）；`_seamAxis == null && !IsCspMode` → return（PVT 点下发依赖实轴，无轴静默以避 `GetInformation`/`BeginMove` 空引用）；
- `if (cspMode) BeginSeamTrackingCorrection();` 上移到判轴 `return` 之前（PVT 分支行为不变）。

> ⚠️ 通用教训：**「算法换了需要新输入的基准」时，必须同步复核该输入的**全部**供给路径与门禁**——供给路径只有一个调用点时，针对「无硬件」写的空值早退会在模拟分支里变成静默死链（与陷阱八「死链三类」、陷阱十七「门禁拦截」同源，本条多一层：**门禁开关本身也要在起焊沿被打开**）。修复后判据：模拟记录模式下 `SeamTrackingMapPointCount` 应从 0 起飞、`TryGetSeamTrackingTargetY` 应先 false 后 true。

**⚠️ 修复后仍存的模拟保真度缺口（未修，待用户裁定）**：虚拟相机 `BuildResult` 取最接近 `y=0` 的点作特征 → 特征恒 ≈0 且**不随虚拟轴位移变化**，即模拟中不存在「轴动 → 激光坐标反向偏移」的物理耦合；而 `CalibratedCenterY` 默认 **5.0**（现场两份算法配置均为空 `<Root/>`，全走 C# 默认）→ `rawDy ≡ −5.004mm` → `Yt = Ya1 − 5.004` 每拍下移 → **单向漂移至 `YAxisMinMm = −15` 截停**。故 ADR-042 的「代数相消」结构不变式在模拟工况下前提不成立，**模拟默认不能用于验证该闭环**。两选一处置：模拟口径把 `CalibratedCenterY` 设为 0；或让虚拟相机把缝特征放在标定中心（更贴近真实标定语义）。

## 陷阱二十：跨会话状态残留 → 二次模拟「启动即报警、清不掉」（2026-09-22 / ADR-042 决 3）

现象：首轮模拟正常跑完；第二轮点「开启模拟流程」**立刻**进子设备报警，点「清理异常」后仍报警，无法做第二次测试。停止汇总恒 `线激光：Standby | V3跟踪：ErrorAborted | 监控：Standby`。

日志指纹（顺序即因果链）：
```
[Error] 机器人 X 折返 累计 1704.35mm 超过阈值 1.00mm 疑似复焊
运控流程异常终止 → 模拟期间检测到参与设备异常或急停 自动终止模拟
消除报警命令已置位 ClearAlarm_IO → 已清除主设备报警        ← 主设备清了，子设备没清
[Error][台达运控轴] Y向电机 缓冲坐标系建立 失败 错误码 4627  ← 残留坐标系/缓冲
再次 4627 → 死循环
```

**四处根因（任意一个都会复现，叠加则必然死循环）**：

1. **`Reset()` 漏清报警位**：`SeamMapTrackingAlgorithm.Reset()` 只清 `_weldDirection` / `_reverseTravelMm` / `_reverseWarned`，**不清 `_hasAlarm`** → 复位后"已在报警态"分支恒返回，上层「子设备报警」判定长期为真。修：`Reset()` 末尾补 `ClearAlarm()`，另开对外 `ClearAlarmState()`。
2. **新会话起点与上一会话终点差 1700mm**：robotX 起点每轮随机回 0~20，上一轮已走到 1704mm，未复位跟踪 → **首帧**即判「X 折返 1704mm 疑似复焊」。修：`StartRobotXSimulation()` 喂入新起点**前**先 `ResetSeamTracking()` + `UpdateRobotPose(_simStartX, 0, 0)`。
3. **建系失败即放弃**：`StartCrdBuffer()` 遇上一会话残留坐标系/缓冲报 4627 后直接 return。修：失败后先 `BufferStop(Smooth)` + `BufferClear()` **再重试一次**，仍失败才报错。
4. **停止侧复位不对称**（ADR-039 决 5 的遗留缺口）：`DisableSimulation()` 只复位线激光/焊参/监控，**遗漏运控与焊接头** → 运控残留 `ErrorAborted`，下一轮启动瞬间被异常守卫判为"参与设备异常"自动终止。修：补 `_motion.Stop()` + `ClearSeamAlarm()` + `RequestWeldStatus(Standby)` 与 `_weldHead.RequestWeldStatus(Standby)`。
5. **启动侧无兜底**：异常退出未必经过 `DisableSimulation`。修：`StartSimulation()` 开头对称清一次（`ClearSeamAlarm()` + `ErrorAborted` 时 `ResetProcess()`）。

> ⚠️ 通用教训（与陷阱六/七同源但更深一层）：**状态位的"置位"与"清除"必须成对出现在启、停两个入口**。只在停止侧清，任何绕过停止侧的路径（崩溃、直接关页、异常早退）都会留下**跨会话残留**；而残留态会让下一会话在**首拍**被守卫判死，用户从 UI 上无法把它和"真报警"区分开——表现就是"启动就报警、清不掉"。
> **排查判据**：遇到"清不掉"的报警，先问三个问题——① 这个状态位有几个清除入口？② 清除是否覆盖了全部**参与设备**（级联了几个就复位几个）？③ 报警分支是不是在**首帧**就被触发（说明是残留而非新故障）？
> **与陷阱六区分**：陷阱六是"清理链三处全失效"（清不动），本条是"清理链本身没覆盖到运控/焊接头 + 复位漏清报警位"（根本没清）。

### 规则条目：跨会话残留要有指纹证据

- **规则要点（原 rules/KR-023）**：判定「跨会话残留」必须用**只可能来自上一轮的值**作证据，⛔ 不靠错误码推测 —— 错误码常常是**结果**而不是原因。
- **判据**：在调试日志**首行**找指纹值（如段队列尾值恰为上一轮末值 ⇒ 证明某函数**整体未执行**）；辅助判据：加**可观测第二判据**（如轴反馈位移）+ 限速原始状态字转储。
- **反例**：以错误码 4352（`NEED_INITIAL`）推断「用户点了点轴」—— 它的真实含义是「缓冲坐标系从未构建」，是**后果**；启发式定时器也不是状态（自计时器会让「已写未执行」在零错误码下隐形）。

## 陷阱二十一：模拟启动跳过复位 → TA 未回零 / Y 未到工作零位即进 PreWork（2026-11-23）

现象（现场日志 `20261123_智能填丝焊接系统日志.log`）：模拟开启后 `Alarm→NoReset（待复位）→Running` 直接进 PreWork，TA 闸门关闭（未回零）、Y 回归标定位目标 -37mm 越界 → `ErrorAborted` → 模拟自动终止。

根因：`EnsureRunningForSimulation()` 原只「清警 + DoStartMachine」，整段跳过复位。正常流程复位由机器人指令触发，模拟没有该指令。

修复：模拟自行触发既有复位链 `DoResetMachine`（内部已旁路机器人在位门禁），新增 `_simResetPending` + `SimResetGateTick` 门控——复位在途不推进任何大步，复位成功（Stop）才进 Running 并启动线激光/运控子流程；复位失败（Alarm）终止模拟暴露原因。⛔ UI 侧不得在 `StartSimulation()` 后立即 Start 子流程（与复位链抢轴，正是本现象的叠加因）。

> ⚠️ 通用教训：**凡「生产靠外部指令触发」的前置步骤（复位/使能/握手），模拟链路必须显式补发等效动作并等待完成**，不能因「模拟没有该指令」就跳过；且子流程启动必须在前置动作完成之后，否则前置形同虚设（与陷阱七同源，本条多一层「启动时序」）。

## 陷阱二十二：用 `RunMode != Manual` 判主页显示会误挡模拟（2026-11-23）

现象：主页面轮廓在手动调试切回后仍显示（旧门禁只不推进版本、不清空已绘轮廓）；改为清空后，又发现模拟态轮廓被误挡。

根因：模拟启动时 UI 把线激光流程置 `WorkflowRunMode.Manual`（「界面动作」语义），故 `RunMode != Manual` 在模拟态恒 false。

修复：主页显示门禁改用 `IsAutoWeldingRunning || IsSimulationEnabled`（ADR-100 D29 权威判据）；手动时 `HideContourForManual` 隐藏轮廓线与特征点 + 版本清零，切回自动/模拟按最新帧恢复。

> ⚠️ 通用教训：**`RunMode` 标的是「动作来源」（手动/自动），不是「是否在焊接流程中」**。模拟是界面启动（Manual）但属生产流程显示范畴；凡判「该不该显示/允不允许」，优先用流程态判据（`IsAutoWeldingRunning`），⛔ 不用 `RunMode`（与陷阱八「显示门控」同源）。

## 陷阱二十三：模拟 X 时钟开早 + 自适应复位首帧假突变（2026-11-23）

现象（现场日志）：模拟起点 X=1.0，但焊前检查会话复位后首帧宽度变化时 X 已是 659.835mm，随后 `NoValueAlarm 引导缺值报警 累计 5.1mm` 停焊。两处独立根因叠加：

1. **X 时钟开早**：`StartRobotXSimulation` 原在 `StartSimulation`（开模拟即跑），PreWork 期间 X 已跑 660mm，形成大截「未引导数据」。修（⚠️ 2026-11-23 焊前寻位改版）：X 改为**模拟开启即移向配置的「焊接前寻位起点 X」、到达即停**，起焊段再继续沿焊缝前进——**X 必须动**，否则地图建不起、Y 拿不到焊接点目标（与焊接工作模式一致：提前扫后跟踪）。见 [[decisions/ADR-114-prework-seek-position]]。
2. **复位首帧假突变**：自适应 `Reset()` 把 `CurrentSeamWidth` 与 `_lastLoggedSeamWidth` 清零，首个有效宽度 1.0 被判「0→1 第 1 次变化」。修：`_seamWidthSeeded` 标志，首个有效宽度（>0）播种为初始值、不计变化。

> ⚠️ 通用教训：**模拟的「时间起点」必须对齐真实链路的事件起点**——机械地「开模拟即跑时钟」会把前置流程（PreWork）的时间算进生产行程；且**复位后的第一帧是基准不是变化**，任何「变化/突变」判断都要先播种基准（与陷阱二十「残留 vs 新故障」同源，本条多一层「时间轴对齐」）。
>
> **模拟线程职责边界（业主裁定 2026-11-23）**：保留 `thSimTestWork` 线程用于「监控步骤/打日志/模拟机器人位姿」；⛔ 但模拟不得自己开线程去动作线激光或监控相机——设备动作一律走工作流公共方法。当前代码合规（`StartSimulationLineLaser`→工作流 `Start`；`ConnectOn` 内部短线程是工作流自身契约，非模拟额外开）。

## 陷阱二十四：CSP 缓冲写入返回 4610 被静默吞掉（2026-11-23 诊断，未改码）

现场日志（11:11:14~15）：缓冲闭环启用后首段写入报 `CSP 缓冲写入失败 返回码 4610`，诊断结论如下（业主裁定本轮只出诊断、不改码）：

- **4610 权威释义**（官方手册 `DELTA_IA-GMC_EtherCAT_PM_TC_20250428.pdf` P941/P956）：`4610` = `0x1202` = `ERR_ECAT_SLAVE_TYPE`，原文「**此模块不支持此 API**」；排解「参考手册确认该 API 是否适用于该模块或驱动器」。⛔ 不是 HOME_OFFSET（0x120A=4618）。
- **瞬态非永久**：报错后同 API 写段成功（队列段 0→11、运行 1），故非轴类型永久不支持。时序证据：报错时「运行 0 / 队列段 0 / 空闲拍 41」，处于「建系（StartCrdBuffer）已完成、缓冲尚未 Start」的窗口。
- **触发根因（判据级）**：`StartCrdBuffer` 与 `PreMotionCheck` 均不检查/不切轴运动模式（CSP 仅在 `ServoOn`/点位运动处切），首段写入落在缓冲状态未就绪窗口 ⇒ 台达返回 0x1202。
- **真正隐患（比 4610 本身重要）**：`QueueCspSegment` 无条件推进 `_cspLastQueuedPos` / 段计数 / 返回 true（`MotionControlWorkflow.cs` L1624-1630），`ReportCspResult` 只 1s 限频记录、**无失败处置** ⇒ 写失败被静默吞掉，软件队列末端与实际 FIFO「账实不符」，且日志只一条易被忽略。知识库既有约定（[[decisions/ADR-042-SeamTrackingConsolidated]] §写入、[[api/MotionControlWorkflow]] `ReportCspResult`）**均无写失败处置条款**。
- **待定**：写失败处置口径（重试 / 报警 / 停焊）须业主确认后另案实现；可参照 4627 建系失败先例（先 `BufferStop(Mode1)` 收尾再重试）。

> ⚠️ 通用教训：**设备 API 返回非 0 而调用方无条件推进内部账本 = 静默失步**。凡「写入即更新队列位置/计数」的链路，写失败必须要么回滚账本、要么显式失败处置，⛔ 不可只记日志后照常推进（与陷阱二十「跨会话残留」同源，本条多一层「账实不符」）。

### 2026-11-23 修复落地（业主裁定「先只出诊断」后同轮实施）
- **修法一（消除 4610 窗口）**：PreWork 建系 + 起焊沿复用（不再收尾重建系），把「建系未就绪即写段」窗口推到 PreWork 段（此时无引导不写段 ⇒ 不触发）。见 [[decisions/ADR-042-SeamTrackingConsolidated]] 2026-11-23 演进 D1。
- **修法二（延时等待，用户口径）**：写段失败**跨拍挂起重试**（延时 0.05s 给台达侧状态就绪时间），⛔ 同拍立即重试无效（状态不会因同拍就绪）。见 同页 D3。
- **修法三（账实不符）**：写失败不推进队列账本；连续失败达上限报警停焊暴露原因；会话收尾清挂起段。
- **配套**：PreWork 只激活地图跟踪、**不启缺值量测**（PreWork 引导未稳，量测开启必误累计触发 NoValueAlarm）；模拟位姿时钟前移到 PreWork（只喂位姿、X 不动）+ Working 才起步（对齐 ADR-038）。
- **实测待验**：现场再跑一轮模拟，确认不再出现 4610，且 PreWork 阶段跟踪有引导后能进闭环。

## 陷阱廿五：模拟旁路直调子流程 + 单动作锁吞指令（2026-11-23）

**症状**：模拟流程与真实机器人流程行为分叉；PreWork 阶段卡住不推进；「主控明明收到命令却没动作」。

**根因（四处断链，模拟是唯一能跑通的路径 ⇒ 掩盖了全部断链）**：
1. **模拟旁路直调子流程**：模拟调度步直接调 `DoSubPrework()` / `DoSubWork()`，绕过了「机器人命令 → `MapCommandToIo` → 虚拟 IO → 派发」这条唯一合法链路。真实流程的 `IoSubPrework` / `IoSubWork` **只有扫描、没有置位源** ⇒ 真实流程里这两个阶段**根本没人触发**。
2. **运控步机无启动方**：`MotionControlWorkflow.Start()` 在真实流程中**零调用方**（唯一调用点是模拟侧），运控 `RunStep` 停在初值 0、步机空转 ⇒ `StepServoOn→StepReturnToCal→StepPreWorkSeek` 永不执行 ⇒ **焊前寻位在真实流程不可达**。
3. **单动作锁吞指令**：`DispatchAction` 的 `_actionBusy` 是全局单动作锁，前一动作未结束时新命令被**直接丢弃**。TA_Auto 会阻塞等力矩建立（有限等待但可达数秒），此窗口内到达的焊接启动命令会被吞 ⇒ 流程永久卡死。
4. **运行态未就绪吞指令**：`ScanPulseIo` 先 `TakeVirtualIo` 再检查 `requireRunning`，不满足就**丢弃**（IO 已取走，永久丢失）。`IoStart` 是**异步派发**，紧随其后的 `IoSubPrework` 若在 Running 前到达即被吞 ⇒ 真实流程永久断链。同理 `IsCommandPreconditionMet` 对这两个 IO 的拒收也会丢指令（命令线程与 Running 建立之间存在时差）。

**修法**：
1. 模拟改为**注入机器人命令到真实指令队列**（`InjectSimRobotCommand`），与真实指令同队列同处理链；调度步序为「注入 → 等阶段应答」。
2. `DoStartMachine` 统一启动运控步机（真实与模拟同一条路径）；`Start()` 非幂等，模拟侧不再重复调。
3. `DispatchAction` 忙时改为**保留 IO 供下拍重试**（原为丢弃）；`ScanPulseIo` 的 `requireRunning` 未满足时同样保留重试；`IsCommandPreconditionMet` 对 `IoSubPrework`/`IoSubWork` 不拒收。
4. 模拟侧再加**限频重试注入**（1s）兜底：命令幂等，未收到应答则重发。

**阶段启动时机的判据（易错）**：
- ⚠️ **PreWork 阶段工作必须在机器人「移动到焊前位」之前启动**。寻位靠「X 移动中边走边建图」，若等机器人**到达**才下发 PreWork，X 已停 ⇒ 地图建不起 ⇒ 寻位超时必失败。故 PreWork 由「请求进入焊前」触发，而非「到达焊前位」触发。

**通用教训**：
- ⚠️ **「只有扫描、没有置位源」的虚拟 IO = 该动作在真实流程中不可达**。凡流程阶段，必须能指出它的真实触发源；找不到就是断链，模拟只是掩盖了它。
- ⚠️ **公开方法零调用方 = 该能力在真实流程中不可达**。静态扫描「有定义无调用」比「有调用无定义」更隐蔽，模拟旁路会把它藏起来。
- ⚠️ **「先取走再派发」的队列语义**：取走与派发之间若可能失败，⛔ 必须回填重试，否则丢的是不可恢复的指令（与陷阱二十四「写失败仍推进账本」同源，都是「失败即失步」）。
- ⚠️ **异步派发 + 同步前置校验 = 竞态丢指令**。前置校验与状态建立不在同一拍时，拒收/丢弃都是错的，应改为「保留待重试」。
- ⚠️ **模拟与真实必须共用同一条命令链**。模拟旁路直调子流程会让两条链行为分叉，且分叉点往往正是真实链的断链处。
- ⚠️ **「命令发出」≠「阶段工作已发生」**。三处静默失效的共性：注入日志打出来了、命令也进了队列，但**阶段工作从未执行**——① 喂帧门禁只看起焊沿开关 ⇒ PreWork 帧全丢 ⇒ 地图恒空；② 前置校验要求 Stop 态而模拟已自行 Running ⇒ 命令被拒收；③ 阶段动作的前置条件由**同一条命令自己造成的状态**满足（如「运控进 PreWork 态」是 `DoSubPrework` 自己切的，用它做幂等判据必须确认是「已切」而非「将切」）。
- ⚠️ **判据要区分「已发生」与「即将发生」**。用被本动作自己改变的状态当幂等判据时，若该状态在判据点**尚未改变**（本动作的结果），判据恒为假 ⇒ 幂等失效；若**已经改变**（别的动作造成），判据恒为真 ⇒ 动作被永久跳过。两种都要用**外部可观测事件**（如线激光出帧数、地图点数）复核，不能只看单个标志位。
- ⚠️ **「限频重试」会掩盖失败**：注入日志每秒重复出现时，应先问「阶段应答为何没到」，而不是加重试频率——重试只是让症状从「卡死」变成「刷屏」。
- ⚠️ **设备侧状态门禁要显式，不靠"应该已经就绪"**：台达 CSP 写段报 4610（`ERR_ECAT_SLAVE_TYPE`「此模块不支持此 API」）的真因是**新建坐标系表尚未激活**（表被启动过的会话写段正常）。⇒ 建表后**立即 Start 激活**，而不是假设「建表成功即可写」。同族：轴运动模式的 `Set_MoveMode` **返回值被忽略** ⇒ 静默失败 ⇒ 后续 API 全被拒。
- ⚠️ **「算对了」≠「真动了」**：到位判据若只用「目标值 ≈ 当前位置」，在目标恰好等于当前位置时会**假到位**（轴其实从未响应）。凡是"要求设备真的动"的场景，判据必须含**实际位移**（如累计位移 ≥ 阈值），否则会出现"什么都没做却报告成功"。
- ⚠️ **会话态必须随复位清零，且「数值 + 锚点」要成对清**：像「寻位计时起点」「起始轴位置」「缺值累计距离」这类**每轮重置后重新开始**的状态，不清则第二轮沿用上一轮数值。实测（2026-11-23）：第二次点模拟测试，PreWork 启动后 **45ms** 即报 `NoValueAlarm 累计 62.6mm > 阈值 5.0mm`；62.6mm 正是上一轮末段「线激光收工 1605mm → 机器人停止 1665mm」那 60mm 无数据行程 + 零散值——因为 `ResetSeamTracking` / `ResetTrackingForWeldStart` 只复位算法（`_noValueSpanMm`），**没清 `WeldParamManager` 的缺值累计**，而报警判据读的正是 `NoValueDistanceMm`。⛔ 更隐蔽的一层：`ResetNoValueDistance()` 原本只清数值、不清位姿锚点 `_noValueHasPoseAnchor`，若只补调用不清锚点，下一帧位姿会按旧锚点补出**整段跨会话位移**（比残留本身更大）。⇒ ① 清零函数必须「数值 + 锚点 + 时刻」三件套一起复位；② 凡带起始时刻/起始位置/累计量的判据都要登记清零点，并在**会话边界（模拟启停、焊前检查）各清一次**；③ 第二轮首拍就报超限时，先算「这个量在该时长内物理上可能达到吗」，不可能即为残留，不要去怀疑阈值或传感器。
- ⚠️ **设备 API 的时序语义要按「先...方能...」读**：台达手册「建立座標系 以及 向緩衝區存入運動指令，**方能開始執行運動**」= **先存指令再 Start**。反过来（空缓冲先 Start）会让 FIFO 进入「已启动」态而**拒绝后续写段**（实测 4610）——本条是被「提前激活坐标系表」的错误假设带偏后、靠现场实测纠正的。⇒ 改设备时序前先找手册里的**必要条件句**，别用因果倒置的猜测去"优化"。
- ⚠️ **同一标志承载两种语义 = 阶段被误判完成**：`_calReturnReady` 同时表示「回归标定位完成」与「寻位完成」，而前者在**寻位步之前**就置位 ⇒ 主控看到它为真即判 PreWork 完成 ⇒ 寻位开始 0.147s 后就发了焊接启动。⇒ 一个阶段一个完成标志，⛔ 不复用上游步骤的就绪位。
- ⚠️ **收尾路径要「幂等成对」**：`BufferStop(Mode 1)` 已清 FIFO 并解坐标系，若**不**把 `_cspBufferStartedOnce` 置假，后续收尾助手会再 Stop 一次 ⇒ 4352（NEED_INITIAL）⇒ 兜底 Clear 也 4352 ⇒ 日志出现「收尾清缓冲异常」的**假报错**。⇒ 凡是「Stop 即清空」的 API，Stop 成功后必须同步标志位。
- ⚠️ **「已知缺硬件」不该记 Error**：焊接头从站未装载（节点号撞号）时调 LA/振镜必失败，此时记 `Error` 会掩盖真正的流程异常。⇒ 调用前先判就绪（`IsSlaveReady`），不就绪则跳过并只记一条 Warn。
- ⚠️ **设备资源「建好就要马上用」**：台达坐标系表建系后**闲置会失效** —— 原始可工作代码是「建系 → 下一拍即写段」（≈10ms），而插入焊前寻位后变成「建系 → 1.4s 才写段」⇒ 写段报 4610（`ERR_ECAT_SLAVE_TYPE`「此模块不支持此 API」）。**这类资源必须紧贴其首次使用点创建**，⛔ 不要在流程早期"预先准备好等着用"。
- ⚠️ **排查设备 API 拒绝时，先做版本对比**：同一 API 曾经能跑，插入新阶段后不能跑 ⇒ 用 `git show HEAD:<path>` 取原始版本对比**调用时序与间隔**，比继续猜"模式/状态/参数"高效得多（本例三轮猜测全错，一对比即定位）。
- ⚠️ **「预载」类动作的失败是真故障，不是预期**：CSP 缓冲「开启后按缓存内容自动移动，耗尽后须重新开启」⇒ **缓存写不进去 = 开启后空转（轴不动）**。⇒ 预载期写段失败必须照常计故障并挂起重写；⛔ 不可用"尝试次数"当开启阈值——那会让空缓存开启、且把真故障藏起来（本项曾因"容忍预载失败"错误上线一轮，业主指出后回退）。
- ⚠️ **不要用「容忍失败」去绕过尚未定位的故障**：把失败判成"预期"只会把故障变成静默空转（轴不动、结果"看起来跑完了"）。定位不清时宁可让它报错暴露，也不要降级吞掉。
- ⚠️ **现场早期"确实动起来过"的原型代码/参数是排查设备问题的最高优先级判据，必须沉淀**：本例中「建系 `orgFlag` 该传 1 而非 0、`sCurveTime` 该传 10 而非 0、坐标系上限须远大于段速」全在早期原型里，但因未沉淀，导致连续多轮在"模式/时序/坐标系激活"上兜圈。⇒ 凡业主提供或历史上验证过的调用样例，**立即归档到对应 ADR 的参数基准小节**，并逐参数与当前实现做对照表。

- ⚠️ **注入节流会吞掉首发，等待步的"重发"其实是在补发**：两个相邻调度小步各调一次 `TryInjectSimCommand`（节流窗口 1s、模拟节拍仅几十毫秒）⇒ 第二次必被拒；若该小步**不判返回值就推进**，命令永久丢失（实测 `RX_PRE_WELD_POSE` 全程无注入记录，焊前位 X 从未送达，判据退化为"模拟 X 到位"）。⇒ ① 注入类小步「发出后才推进」，⛔ 不靠下一小步补发；② 等待应答的小步⛔ 裸调限频注入（每个窗口重发一次会把 `IO_START`/`IO_SUB_PREWORK` 重复派发、日志放大），改用「超时门限 + 长间隔」重发（`TryReinjectOnAckTimeout`：5s 门限 / 3s 间隔）；③ 对数验证：某条 Rx 命令的「模拟注入」日志与下游「已转换为虚拟 IO」必须成对，缺一侧即丢命令。

- ⚠️ **启停两端必须共用同一个会话复位函数**：把会话变量分散在各方法里清（`StartSimulation` 清步号、`DisableSimulation` 清三态……），第二轮必漏——实测漏项：焊前位 X 记录 `_hasRobotPreWeldPose`、位姿时钟 `_simStartTime`、真机使能快照 `_simSaved*`。⇒ 收敛成 `ResetSimulationSessionState(reason, restartFromHome)` 一处清全部 **17 项**（2026-11-24 审查补 `_subWorkPending` / `_subWorkPendingLogTs`：焊接启动挂起标志跨会话不清，下一轮门一开就会**未经机器人指令**补执行 `DoSubWork`；本例静态核对确认已被「离开运行态弃单」兜住，但**兜底 ≠ 已复位**——退出路径一旦不经 Stop 态即会真触发），四条硬约束：① 启动传 `true`（调度指向 Home 起步步）；② 停止传 `false`（调度停在**无效步**，否则停止中的线程下一拍就注入 `RX_HOME_POSE`，在 Stop 态触发一次真复位）；③ 复位必须早于 `SimTestWorkOpen()`（线程已在跑时残留步号会让首拍按上一轮步骤执行）；④ 开启端另补一次 `WeldParamManager.ResetSeamTracking("模拟会话开启复位")`——缺值累计/位姿锚点的公开清零点只有 `ResetSeamTracking` / `ResetTrackingForWeldStart`，而后者在复位完成后才跑，属"晚清"，异常退出跨轮时残留会先存活一段。⚠️ 使能快照要配「已挂起」标志：二次点击时当前使能已被置假，无条件存快照会把真机永久留在禁用态。

## 2026-11-24 时序复审与精简（陷阱廿六~廿七）

### 陷阱廿六：X 停止期每拍喂位姿是「位姿心跳」，⛔ 不可当冗余跳掉
复审发现 `SimTick` 在寻位等待期（X 已到寻位起点停住）仍每拍调 `UpdateRobotPose(_simRobotX, 0, 0)`，看似冗余。实测代码链证实**必须保留**：`WeldParamManager.IsIngestPaused()` 判 `PoseAgeMs > NoValueRsiCycleMs × 2`，跳喂会让位姿超龄 ⇒ 入图暂停 ⇒ 寻位建图缺点；`UpdatePosePredictor` 同样依赖持续喂入维持锚点。起焊沿 `BeginSeamTrackingCorrection` 虽会 `ResetNoValueDistance()`（清锚点+数值）再开窗，但建图阶段的位姿心跳不能断。⇒ 判据：凡「停止期仍持续调用」的喂入，先查下游是否有**时间年龄判据**（`PoseAgeMs` / stale gap / 超时看门狗），有则是心跳不是冗余。跳掉心跳的失败不报警、只表现为「地图建不起来」，比真故障更难定位。

### 陷阱廿七：注释精简时「归一」未必是精简——须同时满足减行数与提可读性
把三个具名响应方法（`AckResetCompleted` / `AckPreWorkCompleted` / `AckWeldStart`，各 3 行、调用点自解释）归一为 `SetAck(int stage)` + switch，实测行数从 15 行增至 19 行，且引入魔法数字 `0/1/2` 降低可读性——**与精简目标相悖**，当场回退。真正有价值的重复消除是提取公共注入出口：`TryInjectSimCommand` / `TryReinjectOnAckTimeout` 尾部重复的「更新节流时刻 + 注入 + return true」提取为 `FireSimCommand(command, payloadX, now)`，既减重复又形成单一注入点（利于静态判据断言「所有注入都经节流」）。⇒ 判据：结构精简须同时通过「净行数不增」与「调用点可读性不降」两关；只是把散落逻辑塞进带 flag/switch 的「万能方法」是伪精简。

## 关联

- 决策：[[decisions/ADR-032-SimulationTestRedesign]] · [[decisions/ADR-039-SimulationTestAutoTerminationAndRecordCacheRelease]] · [[decisions/ADR-042-SeamTrackingConsolidated|ADR-042（焊缝跟踪综合）]]（陷阱二十：跨会话残留清警） · ADR-042（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]）
- API：[[api/DeviceControlWork]] · [[api/MotionControlWorkflow]] · [[api/VirtualCam]] · [[api/SystemControlPage]]
- 模块：[[modules/LineLaserCam]] · [[modules/DeviceControl]]
- 历史：~~lessons/SimulationC-Mode-Interruption~~（A/B/C 时代故障页，2026-09-17 有效经验并入本页后删除）
## 相关页面

- [[index/index]]
