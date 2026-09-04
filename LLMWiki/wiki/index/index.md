# Wiki Index — AdaWeldSystem 知识库索引

> 内容导向索引。AI 回答查询前必须先读取本文件定位相关页面。
> 最后更新：2026-09-02（**旧架构清零完成**：删除 6 个旧架构 ADR（027/032/033/036/041/042）+ `api/SimulationWorkflow` 墓碑 + `modules/Workflow` 存根共 8 页（已移出 `wiki/` 至 `_trash_20260902/`）；`api/MainDeviceWorkflow`→`api/DeviceControlWork`、`api/SafetyWorkflow`→`api/DeviceStatusWork` 对齐新架构类名；全库改链 52 处，红链 0；**现行页 100+ 处旧架构术语清理完毕**（含 `standards/WorkflowResponsibilityBoundary` 三态对齐、`guides/Namespace-Compilation` using 对照表更正、`DeviceStatusWork.cs` 路径勘误）。历史 ADR / lessons 保留原文并按页加「已被 ADR-034 取代 + 现行类名」注记。知识库只保留新架构理解）
> **架构真源**：`raw/architecture/` 三份原档（ADR-035） > `wiki/architecture/DeviceControlArchitecture.md` > 代码注释。**任何架构问题以 ADR-034 三态模型为准**，`decisions/` 下的旧 ADR 均为决策史，不代表现行约束。
> **三态模型（ADR-034）**：旧「设备四态 `DeviceState` + 泛型 `DeviceWorkflowBase<TStep>` + 流程态」模型已全部删除，改为 `SubDeviceState`(连接态) / `SubDeviceWeldStatus`(焊接过程态) / `MainDeviceStatus`(主设备运行态) 三态 + 各工作流私有阶段枚举；「步骤驱动」「自动手动双流程」两套旧模型均已于 2026-09-03 清除，现行规范唯一出处 = [[architecture/DeviceControlArchitecture]]
> **架构原档沉淀 `raw/architecture/`（ADR-035）**：**2026-09-03 收敛为 2 份**——`主控设计.xlsx`（成员级静态结构）+ `激光焊接系统业务流程图.pdf`（业务流 + 检查清单，含文本层）；旧两份 PDF 及 3 张渲染图已删除。为架构唯一修改入口，改原档→同步架构页）
> **原档 9-03 细化（ADR-036，✅ accepted，用户已裁定）**：基类 17 项契约 + 5 子工作流差异化职责 + `DeviceControlWork` 7 线程模型（5 子设备 + 2 通讯）+ **Preworking 五项运行检查 / Working 四路焊接子流程**（代码基本缺失）。**7 项冲突已逐条裁定——新档是完全重构而非对旧文档的补充**：清除基类监听线程 / `GoStep` 改步 / 命令三槽 / const int 指令表 / 机器人 pose 监控。**架构页已按裁定整体重写**，落地清单见 [[architecture/DeviceControlArchitecture]] §15
> 近期变更以 `logs/log.md` 为准（本索引仅结构化索引，不内联日志内容，遵循 AGENTS.md 规范）。
>
> **路径说明**：本文件位于 `wiki/index/index.md`，是知识库索引的**唯一规范位置**。
>
> **三层「规范性」分类判据（2026-09-01 确立）**：
> `standards/` = **必须遵守**的强制规范（由下方速查路由自动触发）
> `lessons/` = **踩过什么坑**的教训门禁（编码前逐条确认规避）
> `guides/` = **怎么做**的操作型指导与参考手册（查阅型，非强制非教训）

---

## ⚡ 场景速查路由（首选入口 —— 命中即可开工，无需扫全表）

> 用法：接到任务后先在下表命中一行，直接读右列页面。未命中再往下翻分类表。

| 你要做的事 | 直接读这 1~3 页 | 硬约束提示 |
|---|---|---|
| **代码精简 / 注释精简 / 日志规范** | [[standards/CodeSimplification]] | 强制排除的只有 `*.Designer.cs`，见 [[lessons/CodeSimplification-Scope-DesignerOnly]] |
| **UI 状态判断 / 按钮 text / 连接态刷新** | [[standards/UiStateSimplification]] | 与 CodeSimplification 互补，二者都要看 |
| **流程与子设备权责 / 这个事件该不该放流程** | [[standards/WorkflowResponsibilityBoundary]] | 判据「数据是设备的，进度是流程的」，R1~R5 |
| **流程怎么推进 / 步骤编号 / 卡在哪一步 / 超时判定** | **[[architecture/DeviceControlArchitecture]] §5 + §16.3**（⛔ 旧标准 [[standards/StepDrivenWorkflow]] 已于 2026-09-03 整页废弃） | 现行：`RunStep` 由**每个 `case` 内 bool 判定**推进（**无 `GoStep` 入口**）；步号段位、改步必刷新步骤计时见架构页 §5；步号常量与单步方法命名见 [[lessons/StepMemberNameCollision]]；**停机久了再开机报超时**见 [[lessons/DeviceControlWorkInheritanceBypass]] 坑五 |
| **写日志 / 日志标签怎么定 / `Tag` 有什么用** | [[api/DeviceLog]] + [[standards/CodeSimplification]] §三 | `Tag` 是**日志标签**（不是死成员）；设备日志唯一出口 `DeviceLog`，通讯报文走 `ShowCommunicationLog`；子工作流用基类 `Tag` + `Log(...)`，独立管控类用 `_tag` |
| **用户改了 `raw/architecture/` 原档，要同步架构** | [[architecture/DeviceControlArchitecture]] §15 + [[decisions/ADR-036-RawDesignRefinement20260903]] | 原档 > 架构页 > 源码注释；**冲突须用户裁定**（ADR-035 §3）；裁定后按 §15.2 五个批次推进改码 |
| **设备状态 / 工作流 / 上电初始化 / 状态机** | [[architecture/DeviceControlArchitecture]] → [[modules/DeviceControl]] | 三态模型：`SubDeviceState`(连接态) / `SubDeviceWeldStatus`(焊接过程态) / `MainDeviceStatus`(主设备运行态)；状态写入唯一入口 `SetState`/`SetWeldStatus`/`SetStatus`，禁手工赋值 |
| **新增或修改一个工作流** | **[[architecture/DeviceControlArchitecture]] §4 + §16**（契约与代码模板）+ [[modules/DeviceControl]] | ⚠️ 改码前必读 §16。现行契约 **17 项**（5 属性 + 10 阻塞方法 + 2 非阻塞方法）：`FlowProcess`/`ResetProcess` 双流程由 `RunStep` 驱动；连接分**阻塞组** `InitializeOn`/`InitializeOff` 与**非阻塞组** `ConnectOn`/`ConnectOff`；状态清理 `ClearStatus`、计时刷新 `ResetWorkTime`、焊接态切换 `WeldStatusTrans`；**每个子流程各自重写 `SubDeviceLog()`（public）**；配置读写 `LoadConfig()`/`SaveConfig()` **无参**，走本项目 `XdocumentReaderWriter`，**子设备各自持有配置路径**（§4.6 / §16.8）。过程态经 `SetWeldStatus(MapWeldStatus(...))`；**子流程不自带线程** |
| **安全检查 / 安全互锁 / 故障恢复** | [[api/DeviceStatusWork]] + [[api/FaultRecoveryManager]] | 故障恢复 2026-09-01 已归口 [[modules/ProductFileManager]]；记录 key 与注册 key 必须同源，见 [[lessons/FaultRecoveryDeviceKey]] |
| **线激光相机（族总览）** | [[modules/LineLaserCam]] | 统辖 SmartRay / Virtual / HikRobot / 英莱 |
| **英莱相机参数 / Job / 传感器** | [[modules/IntelligentLaserCam]] + [[lessons/IntelligentLaser-Pitfalls]] | 参数以设备为唯一真相源，禁离线缓存 |
| **监控相机 / 焊中质检** | [[modules/MonitorCam]] + [[api/MonitorCameraRun]] | 健康巡检在 `MonitorCameraRun`，不在工作流 |
| **运控 / CAMBOX / 正运动控制器** | [[modules/MotionControl]] + [[api/ZMotionController]] + [[api/CamBoxTracker]] | 主轴=虚拟编码器轴 axis8 |
| **焊接工艺计算 / 功率送丝摆幅** | [[modules/WeldParamControl]] + [[api/WeldParamControlWorkflow]] | `TriggerAdjustment()` 无参；不入上电级联 |
| **AntdUI 控件用法 / 迁移 / 设计范式** | [[guides/AntdUI-Reference]] | 禁用 SunnyUI |
| **WinForms 设计器报错 / 控件不显示** | [[guides/WinForms-Designer]] | Designer.cs 不可手改 |
| **跨线程更新 UI / InvokeRequired** | [[guides/WinForms-UI-Threading]] | 后台线程禁止模态弹窗 |
| **编译错误 / 命名空间 / 新文件不参与编译** | [[guides/Namespace-Compilation]] | 新建 .cs 必须注册 .csproj（§1.1） |
| **日志追加位置 / 批量重命名 / .csproj / VibeCoding** | [[guides/Project-Tools]] | 日志必须追加到**文件顶部** |
| **源码云端备份 / 推送拉取 GitHub / 本地远端一致性校验** | [[guides/SourceBackup-GitHub]] | 忽略 3rdDepend；用 `ada_backup.sh` 推送/拉取/校验 |
| **INI / SQLite / XML 配置读写** | [[guides/Config-Data-Tools]] | — |
| **产品记录 / 过程数据归档** | [[modules/ProductFileManager]] | ADR-033 |
| **改任何 C# 代码前的通用门禁** | [[lessons/CSharp-Language-Pitfalls]] | C# 7.3，禁 C# 8+ 语法（ADR-002） |

---

## 目录

| 章节 | 内容 | 何时看 |
|---|---|---|
| [一、项目总览](#一项目总览) | 概览、架构、工作流规范 | 接手项目 / 全局理解 |
| [二、模块详解](#二模块详解) | 19 个模块页面 | 定位代码归属 |
| [三、API 参考](#三api-参考) | 38 个公开接口页面 | 调用前查契约 |
| [四、规范标准 standards](#四规范标准-standards强制) | 4 规范 + 4 深反例 | **必须遵守** |
| [五、历史教训 lessons](#五历史教训-lessons门禁) | 16 条坑 | **编码前门禁** |
| [六、操作指导 guides](#六操作指导-guides怎么做) | 7 本手册 | 查「怎么做」 |
| [七、设计决策 ADR](#七设计决策-adr) | 41 条，按有效性分组（含 1 条待裁定） | 理解「为什么」/ 查约束 |
| [八、归档文档](#八归档文档) | 2 页历史 | 追溯，不引用 |
| [九、专员职责](#九专员职责) | 10 个角色 | 分派任务 |
| [十、来源索引](#十来源索引) | raw/ 映射 | 溯源 |

> **设备控制架构（必读）**：涉及设备状态、工作流、上电初始化、状态机时，先读 [[architecture/DeviceControlArchitecture]]。
> 核心（**2026-09-02 ADR-034 三态模型**）：**设备四态 `DeviceState` 已删除**，改为三态——连接态 `SubDeviceState`(Disconnected/Connected) + 焊接过程态 `SubDeviceWeldStatus`(Standby/PreWork/Starting/Working/Stopping/ErrorAborted/ManualStopped) + 主设备运行态 `MainDeviceStatus`(Running/Alarm/EStop/Stop/NoReset/Reseting)。状态写入唯一入口 `SetState`/`SetWeldStatus`/`SetStatus`，**禁止手工 `State=`/`WeldStatus=` 赋值**。
> **非泛型基类（ADR-034）**：`Step`/`WeldStatus`/`State`/`SetWeldStatus`/`StateSwitched`/`WeldStatusChanged` 统一由非泛型 `DeviceWorkflowBase`（`DeviceStateBase`）承载；旧 `WorkflowStateBase<TStep>`/`DeviceWorkflowBase<TStep>` 已删除。子工作流只保留**私有**阶段枚举（`_phase`/`_flowState`）+ 映射 + 业务。
> 工作流实现类位于 `MainDeviceControl/DeviceWorkflow/`，见 [[modules/DeviceControl]]、[[decisions/ADR-034-ThreeStateModelRefactor]]（现行有效）。
> **架构不按版本代际（V1/V2/V3）描述**，只维护当前事实；历史归档内容见「八、历史归档（现归 project/）」。
> **易误判**：`ConnectOn`/`ConnectOff`/`StateSwitched`/`WeldStatusChanged`/`State`/`WeldStatus` 由基类提供，具体工作流内 grep 不到属正常；`Instance.WeldStatus`（焊接过程态）与 `Instance.State`（连接态）是两个不同属性；主设备运行态走 `DeviceControlWork.Instance.Status`（`MainDeviceStatus`）。

---

## 一、项目总览

| 页面 | 摘要 | 标签 |
|------|------|------|
| [[project/overview]] | 项目整体介绍、技术栈、**13 个顶层模块清单（2026-09-01 实测文件数）**、统计数据 | #项目 #概览 #模块清单 |
| [[architecture/DeviceControlArchitecture]] | **设备控制架构（唯一规范页，1551 行）**：MainDeviceControl 两层目录（**2026-09-01 `DeviceState/` + `FlowState/` 合并为 `DeviceStateApiCore/`，命名空间不变**）+ **三态模型** + 状态写入唯一入口 + 焊接工艺数据链路 + 安全互锁与故障恢复 + CAMBOX 硬件实时跟踪全章 + 模块依赖与调用链（第 11 章）+ UI 接入约定。**2026-09-03 按 ADR-036 裁定整体重写（完全重构，非增量补充）**：§1 三态枚举真值（**`SubDeviceWeldStatus` 删 `Starting` 加 `NoReset`**）· **§3.1 `CommandCore` const string 指令协议（删除 pose 监控）** · **§4 基类 17 项契约（5 属性 + 10 阻塞方法 + 2 非阻塞方法；§4.4 阻塞/非阻塞职责边界）** · **§5 `RunStep` bool 驱动与超时控制** · **§6.2 五子工作流差异化职责** · **§7.2 七条常驻线程** · **§7.5 九个公共方法** · **§7.6 新业务主链** · **§7.7 Preworking 五项运行检查** · **§7.8 Working 四路焊接子流程** · **§15 落地清单（五批次改码 Plan，改码前必读）** · **§16 参考实现与代码模板（改码前必读）**：原档 R007~R014 逐类标注的 5 个参考实现（`StationProcess.cs` / `RollPressProcess.cs` / `AssemblyProcess.cs` / `MachineControlWork.cs` / `MachineStatusWork.cs`）骨架提炼 + 强制范式 S1~S8 / M1~M9 / T1~T6 + 与原档差异。不按 V1/V2/V3 代际描述，只维护当前事实 | #架构 #设备控制 #状态机 #三态模型 #流程态 #CAMBOX #安全互锁 #MainDeviceControl #依赖 #静态推导 #原档驱动 #完全重构 #RunStep #CommandCore |
| [[project/skill-evolution]] | Skill 体系演进历史、版本变更轨迹 | #Skill #演进 |
| [[project/vibecoding-workflow]] | VibeCoding 工作流规范（LLMWiki 原生版）；Phase 0 用 Grep 定位符号 + 按行号精确读取（Step 0.7，已废弃 code-review-graph 图谱）；**2026-09-03 补「核心规则」14 条 + Step 2.6 正确性验证（无 C# 编译器 → Python 静态校验，须显式声明「真编译待 VS」）**，与 `~/.workbuddy/skills/vibecoding-llmwiki/SKILL.md` 对齐，冲突时以 Skill 为准 | #工作流 #规范 #VibeCoding #Step2.6 #静态校验 |

---

## 二、模块详解

| 页面 | 摘要 | 标签 |
|------|------|------|
| [[modules/EmguALG]] | 图像算法模块：AlgorithmJob、JobManager、AlgorithmManager、ImageAlgorithm、ImageRoiTools | #图像算法 |
| [[modules/PointCloudData]] | 3D点云数据处理：3DModel、DataIO、Render；**RunFileRecord 已迁出 [[modules/ProductFileManager]]（ADR-033）** | #3D #点云 |
| [[modules/SmartRayCam]] | **位置** `LineLaserCam/SmartRayCam/`。SmartRay 工业3D线激光相机驱动：ApiCore、CameraRun、`Api/ICameraRun` 抽象（与 [[modules/VirtualCam]]/[[modules/HikRobotCam]] 共享）；虚拟相机/选择器已迁出至 [[modules/VirtualCam]] | #相机 #线激光 |
| [[modules/VirtualCam]] | **位置** `LineLaserCam/VirtualCam/`（与 SmartRayCam 平级）。虚拟调试相机模块：仅含 `VirtualCameraRun` 虚拟线激光（`CameraSelector` 选择器已上提至 `LineLaserCam/Api/`，见 [[api/CameraSelector]]），共享 `ICameraRun` 契约 | #相机 #虚拟 #模拟 #线激光 |
| [[modules/MotionControl]] | 运控调整独立模块：**接口归入 `API/` 子目录**；正运动控制器实现（`ZMotion/` 子目录，4轴+8IO）；`MoveControlData`（标定+计算+缓存）；`MotionControlWorkflow` 现位于 `MainDeviceControl/DeviceWorkflow/`，见 [[api/MotionControlWorkflow]]；**2026-08-19 ZMotionController/CamBoxTracker/EncoderAxis/RSIPositionBuffer/InterpolationEngine 统一标准 IDisposable.Dispose()（ADR-025）** | #运控 #水平移动 #模拟 #正运动 |
| [[modules/HikRobotCam]] | **位置** `LineLaserCam/HikRobotCam/`。海康机器人 **3D 线激光**相机驱动（MV3D-LP SDK，与 SmartRayCam 同族，均实现 `ICameraRun`） | #相机 #海康 #线激光 #3D |
| [[modules/LineLaserCam]] | **线激光相机族父目录** `LineLaserCam/`：统辖 SmartRayCam / VirtualCam / HikRobotCam 三个同类 3D 线激光模块，共享 `ICameraRun` 契约；**2026-07-21 新增相机连接状态模型（Kind/ConnectionState/SetWorking/DetectConnection）+ `CameraKind`/`LineLaserCameraConnectionState` 枚举** | #相机 #线激光 #目录 #连接态 |
| [[modules/IntelligentLaserCam]] | 英莱(IntelligentLaser) 线激光相机模块，实现 ICameraRun 接口；硬件状态检测/帧率切换保护/实测 FPS/UI 层不直引 SDK/按钮语义修正/手动自动数据流分离 | #相机 #英莱 #线激光 #ICameraRun |
| [[modules/WeldParamControl]] | 焊接参数控制模块：`WeldProcess`（工艺计算/自适应调整，单例）+ `WeldDataManager`（参数持久化）；**`TriggerAdjustment()` 无参**（用内部暂存的焊缝特征与 RobotX）；配套 [[api/WeldParamControlWorkflow]] 负责「计算后下发机器人」，振镜摆幅为查表项（当前 TODO 返回 0） | #焊接 #工艺 #自适应 |
| [[modules/LaserWeldHead]] | 激光焊接头模块：**`API/ILaserWeldHeadController.cs`** + Controller + Data（3 文件）；原 `LaserWeldHeadStateMachine.cs` 已移除，状态机职责现由 `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` 承接 | #焊接头 #模块 |
| [[modules/MonitorCam]] | 监控相机模块：焊前对中/焊中质检、SDK 抽象、完全解耦 | #相机 #监控 |
| [[modules/FileOperate]] | 文件操作工具库：INI、Log、XML | #工具 |
| [[modules/Comm]] | 通讯模块：全局状态、TCP/S7/Profinet/Modbus、事件总线、**`CommBase/` 通讯实现基座（`CommBase/Ethernet/`、`CommBase/Modbus/`、`CommBase/Profinet/`、`CommBase/S7Net/` 四层 + `IntelligentLaserModbus/` 独立 Modbus 层 + `Robot/KUKARobot/`）**；NetworkPort 统一抽象层已取消（未实装）；**2026-08-19 CommunicationManager/TcpIpComm/SstTcpServer/SstTcpClient 新增标准 IDisposable.Dispose()（ADR-025）** | #通讯 |
| [[modules/DeviceControl]] | **设备控制核心模块（三态模型）** `MainDeviceControl/`：**`DeviceStateApiCore/` 基类层**（`DeviceStateBase` 三态枚举 + `DeviceWorkflowBase` 非泛型工作流基类 + `CommandTable` 机器人握手表）+ **根目录两个独立管控类**（`DeviceControlWork` 整机运行编排 / `DeviceStatusWork` 安全·IO·状态三线程，二者**均不继承**工作流基类）+ **`DeviceWorkflow/` 实现层 5 个工作流**（LineLaser / MonitorCamera / MotionControl / WeldParamControl / LaserWeldHead）；⚠️ 目录名 ≠ 命名空间，`DeviceStateApiCore/` 下仍分属 `...DeviceState` / `...FlowState`；状态写入唯一入口 `SetState`/`SetWeldStatus`/`SetStatus`（禁手工赋值），执行步由 `RunStep` 驱动（`GoStep` 已废） | #模块 #设备控制 #状态机 #三态模型 #执行步 #MainDeviceControl #非泛型 #ADR-034 |
| [[modules/Safety]] | **2026-08-31 三文件合并（ADR-031）+ 2026-09-02 三线程重设计（ADR-034）** 安全/IO/状态管控：代码位于 `MainDeviceControl/DeviceWorkflow/`——`DeviceStatusWork.cs`（`IOWork` 互锁检查 / `EMGWork` 急停 / `StatusWork` 三色灯 三线程，参考 `MachineStatusWork.cs`；`SafetyFlow` 配置 + `SafetyInterlockChecker` 判定）；**原 SafetyFlow.cs / SafetyInterlock.cs 已删除**；**2026-09-01 `FaultRecoveryManager.cs` 已迁出归口 [[modules/ProductFileManager]]（ADR-033 §3）**，本模块仅作消费方 | #模块 #安全互锁 #安全管控 #PLC #三线程 #ADR-034 |
| [[modules/ProductFileManager]] | **2026-08-31 新增（ADR-033）；2026-09-01 故障恢复归口** 产品生命周期记录模块（`ProductFileManager/`）：`RunRecordManager` 单例（.pDat v2 序列化 + .tmp 崩溃恢复 + 日期归档 + 混淆回溯）+ RecordFrame + WeldActionRecord（双记录 ADR-010）+ SmartRayConverter + **`FaultRecoveryManager`（2026-09-01 自 `MainDeviceControl/DeviceWorkflow/` 迁入，故障恢复数据归口使用方）**；类名与公共 API 不变，共 14 消费方（过程记录 8 + 故障恢复 6）；持久化仍走 [[api/FaultRecordManager]]，DB 层不反向依赖领域类型 | #模块 #产品记录 #过程数据 #生产信息 #故障恢复 #迁移 #归口 #ADR-033 |
| [[modules/KUKARobot]] | KUKA 机器人通讯：RSI 实时传感器接口 + EKI 以太网数据交换 | #通讯 #KUKA #机器人 |
| [[modules/SqlLiteDatabase]] | SQLite 数据库模块：SqliteCore（SQLiteDataBase + DatabaseManagerBase）+ Auth/Config/AutoParam/Product 管理器；**2026-08-31 新增 FaultRecordManager**（故障记录持久化，ADR-033 自 FaultRecoveryManager 下沉） | #数据库 |
| [[modules/UIDesign]] | UI 界面模块：**目录重命名（2026-08-05）** MainWindow(ControlPage/TabPage/ViewPage/SubView；运控参数页 `MotionControlPage` 位于 TabPage，接入 NavPage（参数界面）工艺配置节点，重指向 [[modules/MotionControl]]/[[modules/VirtualCam]]）；ControlPage 含 NavPage×2（NavPage 统一导航页面，替代 ImagePage/ParamPage，通过 LoadTabs 实例化两次；2026-08-06 导航从 Segmented 改回 Menu，Vertical 模式，BackActive=White，BackHover=Gray，Round=false） | #UI |

---

## 三、API 参考

| 页面 | 摘要 | 标签 |
|------|------|------|
| [[api/LineLaserWorkflow]] | 线激光工作流（`MainDeviceControl/DeviceWorkflow/`）：9 态分步状态机（PreWork→Starting→Working→Stopping），Working 态事件驱动触发焊接工艺计算；`WeldStatus`（焊接过程态）与 `State`（连接态）双属性；**焊缝信息即英莱线激光结果**（FeatureY/FeatureZ + Width0/Width1）；继承非泛型 `DeviceWorkflowBase`（ADR-034），状态转换走基类 `SetWeldStatus`；**2026-09-01 修正**：删工作流自建手动流程（`StartManualMode`/`StopManualMode`/`IsManualMode`），严格继承基类 `ManualStart`/`ManualStop`。⚠️ 早期「基类监听线程 + 执行步 0/10/…/900」步骤驱动机制已于 2026-09-03 清除 | #API #工作流 #状态机 #英莱 #三态模型 #非泛型 #执行步 #ADR-034 |
| [[api/MonitorCameraRun]] | 监控相机运行控制：Live/PIL 模式、采集完成信号；**2026-08-31 起为监控相机唯一数据产出方**——新增健康巡检（`StartSupervision`/`StopSupervision`/`SupervisionState`/`LastHealthyTime`/`IsMonitorCameraWorking` + `StatusChanged`），由工作流下沉而来（ADR-030 R1） | #API #相机 #监控 #健康巡检 |
| [[api/MonitorCameraWorkflow]] | 监控相机工作流（`MainDeviceControl/DeviceWorkflow/`）：**只做编排**（触发采集→调用算法→读取结果→推进流程态）；7 态（删 `Displaying`，R5）；**零自定义事件**，2026-08-31 移除 DisplayEvent/ResultEvent/ErrorAborted/ManualStopped/StatusChanged 五个越权事件，结果改 `LastResult`/`LastOverlay` 只读属性供 UI 拉取（ADR-030）。含完整迁移对照表；**2026-09-01 步骤驱动改造**：`WaitOne(5000)` → `WaitOne(0)` 非阻塞探测，执行步 0/10/20/30/800/900；**同日二次审查修复 `new Initialize()` 隐藏基类反模式**（体移入 `InitializeFlow()`，回归基类包装器） | #API #工作流 #监控 #权责边界 #ADR-030 #执行步 |
| [[api/DeviceControlWork]] | **整机主控（DeviceControlWork，ADR-034 由 MainDeviceWorkflow 归并重命名）**（`MainDeviceControl/DeviceWorkflow/`）：上电初始化 5 步同步序列（焊接头→运控+CAMBOX→线激光→监控相机→机器人通讯）+ 聚合判定；`Status`(`MainDeviceStatus` 6 态) / `IsWelding`；**机器人/PLC 连接由顶层 Comm 管控，本工作流只做信号交互**（收 RobotPose / 下发 DeviceCommand）；**✅ 命令受理（早期步骤驱动形态，2026-09-03 已重设计）**：接收 RobotPose 链路改为「回调只写命令变量 → 常驻线程消费 → 执行步推进」；`DeviceStatusWork.StartWork()` 随 `StartMachine()` 拉起；**2026-09-03 三项修复**：状态读取一律走 `Status` 属性（`_status` 直读绕过锁 8 处已收敛）、步时间戳改 `Interlocked` 原子读写、`RunLoop` 补非运行态 `ResetStepTime()` 且 `StartMachine` 内 `GoStep(StepIdle)`（修「停机超 60s 再开机首拍即误判超时跳 900」）；日志收敛至 [[api/DeviceLog]]，见 [[lessons/DeviceControlWorkInheritanceBypass]] | #API #工作流 #主控 #上电初始化 #MainDeviceStatus #执行步 #并发 #ADR-034 |
| [[api/FaultRecoveryManager]] | 故障恢复管理器单例（**2026-09-01 迁至 `ProductFileManager/`，命名空间 `AdaWeldSystem.ProductFileManager`**，ADR-033 §3；原 `MainDeviceControl/DeviceWorkflow/`）；自动恢复策略 `RegisterRecoveryStrategy`；**2026-08-31 起承载 `FaultCategory` 与 `FaultRecord`**（自已删除的 SafetyInterlock.cs 迁入，ADR-031）；**SQLite 持久化已下沉 [[api/FaultRecordManager]]**（ADR-033，仅留 `Persist` 做领域对象→string[] 适配）；6 消费方须 `using AdaWeldSystem.ProductFileManager`；⚠️注册 key 与记录 key 必须同源，见 [[lessons/FaultRecoveryDeviceKey]] | #API #故障恢复 #SQLite #单例 #归口 #ADR-033 |
| [[api/FaultRecordManager]] | **2026-08-31 新增（ADR-033）** 故障记录数据库管理器（`SqlLiteDatabase/FaultRecordManager.cs`，继承 DatabaseManagerBase）：`DataBase\FaultRecord.db` 表 FaultRecord 的建表/插入/查询；以 string[] 为写入契约不依赖领域类型；只管持久化，恢复闭环见 [[api/FaultRecoveryManager]] | #API #故障恢复 #SQLite #单例 #数据库 #ADR-033 |
| [[api/DeviceLog]] | **设备日志统一出口（`MainDeviceControl/DeviceLog.cs` 静态类，2026-09-03 新增）**：封装 `GlobalCommData.ShowLog`，是全目录唯一设备日志调用点；收敛原 63 处发散写法（私有 `_tag` / 遮蔽基类的 `const Tag` / `StateName` / `_simTag` 四套并存）；标签约定=子工作流用基类 `public string Tag { get; protected set; }`（构造函数赋值）+ 基类 `Log(...)`，独立管控类用私有 `_tag` + 本类 `Log(...)`；**通讯收发报文仍走 `ShowCommunicationLog`，二者不得混用** | #API #日志 #规范 #DeviceLog #可观测性 |
| [[api/DeviceStatusWork]] | **安全/IO/状态管控（DeviceStatusWork，ADR-034 由 SafetyWorkflow 重设计）**（`MainDeviceControl/DeviceStatusWork.cs`，参考 `MachineStatusWork.cs`）：`IOWork`(互锁→Alarm) + `EMGWork`(急停→EStop) + `StatusWork`(反射三色灯) 三线程（非步骤驱动）；`SafetyFlow`(阈值与 PLC 地址 + 三色灯地址) + `SafetyInterlockResult` + `SafetyInterlockChecker`；`IsSafe` 供主设备 Pose 门控（未启动返 true）；`FaultCategory`/`FaultRecord` 已迁 [[api/FaultRecoveryManager]]；`StartWork()`/`CloseWork()` 随整机启动/停止 | #API #安全互锁 #安全管控 #工作流 #PLC #三线程 #ADR-034 |
| [[api/MotionControlWorkflow]] | **运控工作流（CAMBOX 硬件实时跟踪）**（`MainDeviceControl/DeviceWorkflow/`）：7 态，电子凸轮由硬件总线完成、PC 仅做启停编排；Idle 一态两义按 `_initialized` 区分；替代已归档的 LaserCamBoxTrackingWorkflow；**2026-09-01 步骤驱动改造**：`MonitorLoop` 并入基类监听线程（`BeatMs=20`），执行步 0/10/20/30/100/110/700/900，`Start()` 由「同步完成动作」改为「受理指令」 | #API #工作流 #运控 #CAMBOX #实时跟踪 #执行步 |
| [[api/WeldParamControlWorkflow]] | **焊接工艺控制流程**（`MainDeviceControl/DeviceWorkflow/`）：**非设备**，输入机器人信息+线激光结果→计算功率/送丝/摆幅/速度→下发机器人；`ComputeAndOutput()` 调无参 `TriggerAdjustment()`；**不入上电级联**，由线激光触发；**2026-09-01 步骤驱动改造**：`ComputeAndOutput()` 改命令变量模式（只置 `_pendingCompute`），执行步 0/10/20/800/900，⚠️ 返回值语义变为「上一轮是否成功」 | #API #工作流 #焊接 #工艺 #功率 #送丝 #执行步 |
| [[api/MonitorAlgorithmManager]] | 监控相机算法管理器：单一可配置算法参数 + INI 持久化（无 JOB 切换） | #API #监控 #算法 #管理器 #持久化 |
| [[api/HikvisionCameraSDK]] | 海康 MvCameraControl.Net SDK 详细用法：枚举/按IP连接/Live回调/单帧/像素转换/参数/原生依赖 | #API #相机 #海康 #MVS |
| [[api/IAxis]] | 运动轴接口，定义 Jog/MoveTo/Stop/GetPosition 等轴控制方法 | #API #运动控制 #轴 #接口 |
| [[api/CameraRun]] | SmartRay 相机运行控制接口 | #API #相机 |
| [[api/ICameraRun]] | 相机运行抽象接口（LineLaserCam/Api，三套线激光相机共享统一对外契约） | #API #相机 #接口 |
| [[api/IIO]] | IO 接口，定义 SetDO/GetDI/SetAO/GetAI 等 IO 操作方法 | #API #IO #接口 |
| [[api/VirtualCameraRun]] | 虚拟调试相机：自生成轮廓点云，实现 ICameraRun | #API #相机 #虚拟 |
| [[api/CameraSelector]] | 相机选择器（位于 `LineLaserCam/Api/CameraSelector.cs`，命名空间 `AdaWeldSystem.LineLaserCamApi`）：**2026-08-26 简化**，默认英莱线激光相机一步到达（删 Load/Save/DetectConnection/SelectReal），保留 SelectVirtual/SelectIntelligentLaser 用于模拟切换 + Active/Kind/ConnectionState/SetWorking 运行时接口 | #API #相机 #选择 #连接态 #英莱 |
| [[api/IntelligentLaserCameraRun]] | 英莱(IntelligentLaser) 工业3D线激光相机运行控制：实现 ICameraRun，MillionOutlineInspect 回调→mm轮廓→PointCloudData→Mat 无缝接入取图链；x64 + 原生 DLL 部署；托管枚举 IlFpsModel/DetectHardwareStatus/MeasuredFps/ResetMeasuredFps/IsCaptureCameraOn/IsSensorRunning/FetchFpsModel | #API #相机 #英莱 #线激光 #ICameraRun |
| [[api/IntelligentLaserSDK_CSharp_DevManual]] | 英莱智能激光 C# SDK 开发手册：接口说明、数据结构、回调机制 | #API #相机 #英莱 #SDK #开发手册 |
| [[api/MoveControlData]] | 运控标定+水平移动计算+缓存（MotionControl 模块） | #API #运控 #水平移动 |
| [[api/IMotionController]] | 运动控制器接口，定义轴/IO 管理 + Connect/Disconnect/IsConnected/EmergencyStop | #API #运动控制 #控制器 #接口 |
| [[api/MotionManager]] | 运动管理器单例，聚合 IMotionController，管理所有轴和 IO | #API #运动控制 #管理器 #单例 |
| [[api/ZMotionController]] | **2026-08-10 新增** 正运动（ZMotion）控制器实现：ZMotionController/ZMotionAxis/ZMotionIO/ZMotionNative，4轴（Y/振镜/送丝臂/Z对焦）+ 8IO，以太网连接，失败自动回退到空控制器；**2026-08-11 新增振镜控制（ZMotionNativeLaser+ZMotionGalvo）+ 高级运动指令（软限位/PSWITCH/锁存/螺距补偿）** | #API #运动控制 #正运动 #控制器 #4轴 |
| [[api/CamBoxTracker]] | CAMBOX 焊缝跟踪引擎：轨迹点追加、前置补偿、启停控制、超偏保护、异常保护体系，硬件级实时跟踪核心组件 | #API #运控 #CAMBOX #正运动 #跟踪 |
| [[api/EncoderAxis]] | ATYPE=25 通讯编码器轴：EtherCAT PDO 硬件自动刷新位置，作为 CAMBOX 电子凸轮的主轴 | #API #运控 #编码器 #正运动 #EtherCAT |
| [[api/RSIPositionBuffer]] | RSI 位置时间戳环形缓冲：缓存机器人位置+时间戳序列，激光帧时间戳插值对齐，跟踪精度基石 | #API #运控 #RSI #时间戳 #插值 |
| [[api/MotionControlPage]] | 运控调整参数页（Sub2UI，设计器生成，接入 NavPage（参数界面）工艺配置节点） | #API #运控 #UI #参数页 |
| [[api/FormMain]] | 主窗口（AntdUI Window，设计器生成）：构建顶部 Segmented+Tabs 导航联动、加载 4 子页（MainPage/NavPage×2/DataReviewPage）、整机状态标签、线激光/设备连接态刷新、关闭前询问+单例 Dispose 级联；2026-08-27 代码精简（删死函数 HideTreeNode、补 3 #region、7 方法 XML 注释精简） | #API #UI #主窗口 #导航 #状态标签 |
| [[api/MainPage]] | 主页面（Sub1UI UserControl，设计器生成）：英莱轮廓 ScottPlot Signal 图 + 4 条实时数据曲线（焊缝宽度/运动速度/送丝速度/激光功率）+ 全局日志框；2026-08-27 代码精简（删 4 未用字段+死函数 ResetChartLineData、内联 LoadComponent、补 5 #region、4 public 方法归集、XML 注释补全） | #API #UI #主页面 #ScottPlot #英莱 #轮廓 |
| [[api/AlgorithmEditForm]] | 算法编辑弹窗（SubView，`UserControl`，Modal 承载）：模块A 配置 EmguALG PipelineConfig + 模块B 英莱 Job Parameter 编辑与实时识别结果（IlInspectResult 只读）；两模块分 `UserControl` 子页经 `AntdUI.Tabs.AddTabSelect` 按 `CameraSelector.Active` 挂载，替代 LLCamWorkJob「编辑」TODO；2026-07-30 经 `ADR-019` 由 `AntdUI.Window` 改 `UserControl` 迁 SubView，调用点 `LLCamWorkJob` 以 `AntdUI.Modal.open` 弹出 | #API #UI #算法 #配置 #SubView #英莱 #Modal |
| [[api/PointCloudViewer]] | 3D渲染引擎公共接口 | #API #3D |
| [[api/WeldDataManager]] | 焊接数据管理器：AutoParam / 分段数据 / 配置映射 / INI 持久化 | #API #焊接 #自动调整参数 |
| [[api/KUKARobot]] | KUKA 机器人通讯 C# API：RSI/EKI 接口、数据类型、配置管理 | #API #通讯 #KUKA |
| [[api/S7NetPlus]] | S7NetPlus / S7.Net 使用笔记 | #API #PLC #西门子 |
| [[api/ProfinetGSDML]] | Profinet GSDML 文件结构与生成方法 | #API #Profinet #GSDML |
| [[api/GlobalCommData]] | 全局数据通讯中心接口（自动调整参数已迁出）；**机器人/PLC 连接由 `CommunicationManager` 管控，`DeviceControlWork` 经此做信号交互** | #API #通讯 #机器人 |
| [[api/LaserWeldHeadController]] | 激光焊接头控制器：ILaserWeldHeadController 接口、LaserWeldHeadConfig、LaserWeldHeadEventArgs | #API #激光焊接头 #控制器 |
| [[api/LaserWeldHeadWorkflow]] | 激光焊接头工作流（`MainDeviceControl/DeviceWorkflow/`）：非泛型 `DeviceWorkflowBase`（ADR-034）；单例；骨架期 `IsRunLoopActive=false`（不起空转线程）、`FlowProcess` 空转；连接态 `State`(`SubDeviceState`) + 焊接过程态 `WeldStatus`(`SubDeviceWeldStatus`)；`ConnectOn`/`ConnectOff`/`ResetProcess`/`ClearStatus`；私有 `_phase`→`SetWeldStatus(MapWeldStatus)` | #API #工作流 #焊接头 #SubDeviceWeldStatus #步骤驱动 #ADR-034 |

---

## 四、规范标准（standards/，强制）

> 本分类页面由顶部「⚡ 场景速查路由」自动触发，命中后**直接读取执行，无需用户重复输入要求**。

| 页面 | 摘要 | 标签 |
|------|------|------|
| [[standards/CodeSimplification]] | **代码精简标准源（详尽版 2026-08-26）**：五维度（①文件书写整理 成员顺序/region/XML注释 ②变量与临时变量 ③枚举事件去重+禁过度枚举 ④逻辑去冗余去互锁+9类禁止项 ⑤辅助函数归集/功能重叠合并/嵌套内联/死函数）+ 注释规范 + 设备/通讯日志规范（去符号细则）+ **检查脚本 `scripts/csharp_review.py`**（A/B/C 三类 error/warn/info）；深度反例见下方 4.1 节；按文件夹落实、逐文件用脚本扫描；**⚠️ 强制排除仅 `*.Designer.cs`**：`UIDesign/` 下非设计器 `.cs` 同样适用五维度，仅状态控制细则由 [[standards/UiStateSimplification]] 互补（2026-08-27 用户裁定，见 [[lessons/CodeSimplification-Scope-DesignerOnly]]）；进度快照见 [[project/CodeSimplification-Progress-20260826]]；**2026-09-03 §三新增⑤ 日志出口统一**：设备日志唯一出口 [[api/DeviceLog]]、一个标签一个出口、`long`/`double` 跨线程字段禁裸读写、0 消费 ≠ 死成员（可观测性 API 与安全钩子不删） | #规范 #代码精简 #注释 #日志 #检查脚本 #DeviceLog |
| [[standards/UiStateSimplification]] | **UI 状态判断与控制精简标准源（2026-08-24 新增）**：专补 `UIDesign/` 状态判断与控制细则（ADR-028 已覆盖其非设计器 `.cs` 五维度）；四原则（真相源唯一：禁本地 bool 缓存设备态 / 单一控制函数收敛按钮 text+ExtraMouseDown+Enabled / 统一刷新入口 RefreshUi(Flags) / 集中状态标签）；红灯清单 + 已落地案例（ILCamPage/ILAlgoPage/ILParamPage 删 `_isXxx` 缓存，MotionControlPage.SetSimButtonMode 与 FormMain.UpdateDeviceStatus 为好范式） | #规范 #UI #代码精简 #状态管理 #真相源 |
| [[standards/WorkflowResponsibilityBoundary]] | **流程与子设备对象权责边界标准（2026-08-31，ADR-030）**：一句话判据「数据是设备的，进度是流程的」+ 流程职责白名单（触发/调用/读取结果/推进流程态/执行动作）+ 五条硬规则——R1 数据产出归属（流程不输出图像/算法结果/设备健康）· R2 禁止转发子设备事件（订阅方直接订阅 `Tracker` 等子设备）· R3 流程态通知统一走基类 `StateChanged`（禁自造 Completed/ErrorAborted/ManualStopped）· R4 流程做动作而非抛事件（结果放只读属性 `LastResult`/`LastOutput`）· R5 流程态只描述流程（禁 `Displaying` 等 UI 职责态）；另含依赖方向（子设备不得 using 流程层）、审查清单（含删事件后 region 失衡易踩坑）、正反例、UI「推状态+拉数据」范式 | #规范 #权责边界 #工作流 #子设备 #事件 #ADR-030 |
| ~~[[standards/StepDrivenWorkflow]]~~ | **⛔ 已整页废弃（2026-09-03，ADR-036，用户裁定「完全重构」）**：本页曾规定命令变量三槽 + 常驻监听线程 + `WorkStep`/`WorkStartTime` + `GoStep(n)` 改步，上述机制**已全部清除，不得据本页改码**。**现行规范唯一出处 = [[architecture/DeviceControlArchitecture]]**（§4 基类 17 项契约 · §5 `RunStep` 驱动 · §7.2 7 线程编排 · §16 代码模板）。本页保留仅作迁移对照，内含「旧规定 → 现行做法」11 条对照表 | #规范 #工作流 #步骤驱动 #已废弃 |

### 4.1 深反例与脚本工作流（standards/ 平铺，无子目录）

> [[standards/CodeSimplification]] 的配套深度反例集，仅在需要具体反例时查阅。
> **2026-09-01 扁平化**：原 `standards/references/` 子目录已撤销，4 个页面平铺为 `standards/CodeSimplification-*` 独立文件（靠命名前缀成组、靠横幅回链父页）。**wiki/ 各分类下禁止再建子目录**——新增页面一律平铺，索引按主题前缀分组即可。

| 页面 | 摘要 | 标签 |
|------|------|------|
| [[standards/CodeSimplification-RefFileOrganization]] | 文件书写整理维度深反例：成员顺序、#region 划分、XML 注释规范的正反例 | #规范 #反例 #文件书写 |
| [[standards/CodeSimplification-RefLogicSimplification]] | 逻辑精简维度深反例：9 类禁止项逐条反例（无意义锁/冗余赋值/过度属性/过度等待/过度缓存/过度资源管理/null/临时变量） | #规范 #反例 #逻辑精简 |
| [[standards/CodeSimplification-RefFunctionSimplification]] | 函数精简维度深反例：功能重叠合并、嵌套内联、死函数清理 | #规范 #反例 #函数精简 |
| [[standards/CodeSimplification-ReviewWorkflow]] | C# 代码审查脚本工作流：`csharp_review.py` 的按文件夹扫描流程与结果判读 | #规范 #脚本 #审查工作流 |

---

## 五、历史教训（lessons/，门禁）

> **编码前逐条确认规避。** 2026-08-18 知识库瘦身：原 64 个分散 lessons 合并为主题页；2026-09-01 二次治理：其中 6 个「操作型指导/参考手册」迁出至 [六、操作指导](#六操作指导-guides怎么做)，本分类回归纯教训。

| 页面 | 摘要 | 标签 |
|------|------|------|
| [[lessons/FaultRecoveryDeviceKey]] | **故障恢复设备键名匹配陷阱（P0 严重）**：`RegisterRecoveryStrategy` 用英文 key 注册策略，但故障记录 Device 字段存中文设备名，`ResolveKey` 的 `IndexOf` 子串匹配永远失败，自动恢复策略永不触发；修复：`RecordFault` 新增 `deviceKey` 参数，调用方传入与注册一致的 key，精确匹配优先 | #教训 #Safety #故障恢复 #状态机 #命名约定 #严重 |
| [[lessons/StepDrivenWorkflowPitfalls]] | **步骤驱动改造六坑（2026-09-01 全量落地实战；机制已于 2026-09-03 清除，坑点思想仍有效）**：① `OnStepChanged` 会复位执行步 → `FlowProcess` 内 `SetStep()` 后**必须立即 return**，否则覆盖刚复位的步号 ② 单步内阻塞等待会**同时**冻结超时判据与指令响应（急停延迟！），`WaitOne(5000)` 须改 `WaitOne(0)` 探测 ③ 基类新增抽象成员 → 7 个子类同时编译失败，骨架类也要补（并显式 `IsRunLoopActive=false`） ④ `RobotPose.StartSafePose=1` 与 `RobotCommand.PreWeldRequest=1` 编码重叠，单槽命令变量必丢指令，须三槽分存 ⑤ 失败计数按拍累加会 25ms 打满阈值，须改时长判据 ⑥ 失败收尾步 `FaultRecord.State` 强类型改为 `MainDeviceStatus`（ADR-034 三态模型，`DeviceState` 已删），写 `_step.ToString()` 即 CS0029，须经状态映射方法转换 | #教训 #步骤驱动 #执行步 #并发 #编译 #ADR-034 |
| [[lessons/StepMemberNameCollision]] | **步号常量与单步方法同名（CS0102，2026-09-01 精简审查）**：`private const int StepXxx` 与 `private void StepXxx()` 同类作用域同名即 CS0102 硬编译错误，6 个 workflow 共 27 处；修复=**方法改 Do 前缀**（`case StepXxx: DoXxx();`）+ **通用三常量 `StepIdle`/`StepFinishOk`/`StepFinishFail` 与 `FailFlow(reason)`/`FailReason`/`FailStep` 下沉基类**（子类重复定义 protected const 会触发 CS0108）；配套 `DeviceControlWork` 魔法数字补齐 7 个步号常量 | #教训 #步骤驱动 #命名约定 #CS0102 #CS0108 #代码精简 #ADR-028 |
| [[lessons/StateMachine-DoubleTransition]] | **状态机重复转换陷阱**：工作流层手动调 `TryTransition(Initializing)`，而设备状态机模板方法 `Initialize()` 内部也会转一次，造成 `Initializing→Initializing` 非法转换 → 初始化立即失败；修复：设备状态机的初始化转换统一由模板方法负责，工作流层不要越俎代庖 | #教训 #状态机 #初始化 #架构分层 |
| [[lessons/CSharp-Language-Pitfalls]] | **C# 语言陷阱综合（改任何 C# 代码前的通用门禁）**：C# 7.3 语法约束、构造函数（拷贝构造消无参构造）、auto-property initializer、static class 声明、枚举去重、命名空间迁移/同名冲突、using 缺失、跨模块类型可见性、P/Invoke 重复声明、XElement 类型转换、接口与基类成员不同步（CS1061）、**基类事件在派生类不可赋值（只能 +=/-=）**、**泛型参数不能声明 volatile（CS0677）** | #教训 #C# #语法 #编译错误 #命名空间 #枚举 #事件 #volatile |
| [[lessons/CodeSimplification-Scope-DesignerOnly]] | **代码精简范围裁定（P1 易误读）**：强制排除的**只有 `*.Designer.cs`**，不是整个 `UIDesign/`。早期表述「`UIDesign/` 除外」被误读为跳过整个 UI 目录，2026-08-27 用户裁定更正；含正确边界表（Designer.cs / UIDesign 非设计器 / 厂商 SDK / 其余业务源码） | #教训 #代码精简 #范围 #Designer.cs #UIDesign #误解 |
| [[lessons/UiRefreshUnifiedEntry]] | **UI 状态刷新统一入口（2026-08-24）**：页面多状态变更函数碎片（连接态/模式/硬件同步）收敛为单入口 `RefreshUi(RefreshUiScope scope)`（`[Flags]` 枚举 + 内置 InvokeRequired 封送），旧函数降级为 private `*Core`；消除嵌套调用与隐式刷新顺序依赖 | #教训 #UI #状态刷新 #代码精简 #重构 #Flags |
| [[lessons/SimulationC-Mode-Interruption]] | **模拟 C 模式进不到测试阶段（2026-08-25）**：三个叠加根因——① `Enable(C)` 的 `SelectReal()` 选 SmartRay 占位，`InitializeWorker` 在 `Start()` 前读到它直接 ErrorAborted；② 模拟流程只调 `Start()` 无人调 `BeginStarting/BeginWorking` → 所有模拟模式卡死 PreWork；③ 虚拟相机无回调 → Working 连续失败中断。修复：C 模式 InitializeWorker 显式切英莱 + 模拟模式自驱动 PreWork→Starting→Working + 虚拟相机默认通过 | #教训 #模拟 #线激光 #工作流 #状态机 |
| [[lessons/AntdUI-Modal-Config-Overload-Cascade]] | **AntdUI Modal.Config 第三参数未定义级联误报 Form→Target**：content（第三参数）为未定义标识符时编译器误报"Form 无法转换为 Target"，实为重载解析级联；owner 用 `Form.ActiveForm`/`this.FindForm()` 合法（Modal owner=Control），见 [[guides/AntdUI-Reference]] | #教训 #UI #AntdUI #Modal #编译错误 #重载解析 |
| [[lessons/IntelligentLaser-Pitfalls]] | **英莱智能激光相机踩坑汇总**（全库最大页，1217 行，建议按章节跳转）：Job 参数结构体核对（CppSharp 生成）、Marshal 封送、检测连接≠开激光（ConnectManual vs OpenSensor）、回调驱动显示非轮询、一次性回调注册顺序、校准框居中（demo 公式勿自创）、传感器/激光/回调三层解耦、重连后恢复传感器使能、帧率设置与 JOB 切换、**§5 UI 与状态管理** | #教训 #英莱 #相机 #线激光 #回调 #SDK #互操作 #校准框 |
| [[lessons/IntelligentLaserSensorControl]] | **英莱传感器控制与激光/传感器按钮 UI 统一（2026-08-24）**：启停传感器用 `SetSensor`（弃 `SetCaptureCamera`）；传感器状态以 `IsCameraOn()`（=`StCtrl.DwCameraEnable`）为真相源、禁本地 bool 副本；激光/传感器按钮 text 与 `ExtraMouseDown` 收敛到单一 `UpdateLaserSensorUi()` | #教训 #英莱 #线激光 #传感器 #UI #代码精简 |
| [[lessons/IntelligentLaser-JobParamNoOfflineCache]] | **英莱 Job 参数离线缓存必须移除（2026-08-24）**：参数以设备为唯一真相源，删 `LoadOfflineCache`/`SaveOfflineCache`/`HasJobParamCache`/`.ilini` 落盘；注册 SDK `OnJobParamsChanged` 回调刷新缓存；`ILAlgoPage` 改单元格级单条下发 | #教训 #英莱 #线激光 #Job参数 #离线缓存 #代码精简 |
| [[lessons/IntelligentLaser-JobListJsonSources]] | **英莱 Job 列表与接头类型数据源：运行目录 JSON（2026-08-24）**：连接相机后原生 SDK 自动落盘 `IntelligentLaser_jobdesclist.json`（全部 Job：id/jointtype/jobdescribe）与 `IntelligentLaser_jointtypelist.json`（接头类型语义）；SDK C# 包装与 demo 均不读此 JSON，须自行解析（Newtonsoft）；文件在运行目录非 Config，未连接时可能残留旧数据须以「已连接」为前提读取 | #教训 #英莱 #线激光 #Job列表 #JSON #接头类型 |
| [[lessons/IntelligentLaser-JobFlowPanel]] | **英莱 ILAlgoPage Job 流面板 + Modal 内联弹窗（2026-08-24）**：flowPanel 动态 JOB 按钮（`TTypeMini.Primary` 激活态）；删「从设备读取」按钮，参数全事件触发（`OnJobParamsChanged`）；删除保护（当前 Job 不可删）；新建 JOB 弹窗用 `Modal.Config(BtnHeight=0)` 内联 FlowPanel，`flow.FindForm().DialogResult=OK` 关闭；闭包须拷贝循环变量；**2026-08-25 修复弹窗空白：Modal 内容控件必须给明确尺寸，Dock=Fill 裸容器高度塌缩为 0** | #教训 #英莱 #线激光 #Job #flowPanel #Modal #弹窗 |
| [[lessons/GitHubSyncPitfalls]] | **GitHub 云端同步陷阱（2026-09-01）**：①沙箱 `origin/main` 远程跟踪引用跨 Bash 命令不落盘（状态显示 `[gone]`），推送/拉取不受影响，校验须单命令内 fetch ②`3rdDepend` 第三方 DLL 约 200MB 必须忽略，误提交会撑爆仓库 ③PAT 明文存 `~/.git-credentials` 有泄露风险，建议 GitHub 撤销重发 ④non-fast-forward 须先 `fetch+rebase` 再 push，禁止 `--force` | #教训 #GitHub #备份 #同步 #PAT #rebase |
| [[lessons/DeviceWorkflowDualFlowCallerGate]] | **设备工作流调用方入口红线（2026-09-01）**：驱动任一工作流子类必须走基类公共入口，禁止直接调子类同名便捷方法——连接/断开唯一入口 `ConnectOn()`/`ConnectOff()`（ADR-034 定名），内部启停方法会绕过受理式置态语义；UI 页只直驱自身所属设备，非所属设备只消费结果 | #教训 #工作流 #调用方 #ConnectOn #ConnectOff #ADR-034 |
| [[lessons/DeviceControlWorkInheritanceBypass]] | **独立管控类绕过/复制基类机制的 5 类 BUG（2026-09-03）**：一句话根因=**不继承基类、另起炉灶抄一份私有实现，基类后补的正确性保障永远传导不过去**。① 子类 `private const string Tag` 遮蔽基类 `Tag` → CS0108 + string/object 类型对撞（**`Tag` 是日志标签不是死成员，0 消费 ≠ 可删**）② 63 处 `ShowLog` 标签四套写法发散 → 收敛为 [[api/DeviceLog]] 统一出口 ③ `long` 时间戳裸读写 32 位平台非原子 → `Interlocked` ④ `_status` 直读绕过 `_statusLock`（8 处）→ 加锁与不加锁混用等于没加锁（例外：`ClearAlarm` 的 check-and-set 必须同锁内）⑤ 抄的步机制漏了基类「非运行态刷新时间戳」→ **停机超 60s 再开机首拍即误判超时跳 900**，须补 `else ResetStepTime()` + `StartMachine` 内 `GoStep(StepIdle)` | #教训 #继承 #并发 #日志 #步骤驱动 #CS0108 #Interlocked #DeviceControlWork #ADR-034 |
| [[lessons/WikiDriftCorrectionPitfalls]] | **Wiki 批量漂移修正五坑（2026-09-03，一次性修正 144 处失效 `.cs` 引用）**：① Python 默认换行把整库 LF 写成 CRLF → diff 从 90 行膨胀成整文件重写（**仓库以 LF 入库**，`core.autocrlf=true` 只影响 checkout；误判方向后反向修会固化污染，唯一判据是与 `HEAD` 比对）② 行区间替换 joiner 默认 `""` → `people/UISpecialist.md` 压成零换行的 3 KB 单行（joiner 必须由 `raw.endswith("\r\n")` 探测，默认 `"\n"`）③ 机器直接替换旧名 → 路径拼贴 / 外部项目（`PcomDeviceInterface/`）被改 / 自指 / 目录树塞全路径，16 页全部回退，改**标注式**（保留旧名 + 追加「现役 X.cs」）④ 横幅块内旧名被判为「未登记的新漂移」自伤 → 扫描器加 `> ⚠️ 历史名称提示` 块豁免 ⑤ 正则无边界断言 → `FormMain.Designer.cs` 截成 `Designer.cs`（144 处误报），须双侧断言 + RENAMED/REMOVED/EXTERNAL/SPECULATIVE 四点分诊 | #教训 #LLMWiki #漂移 #工具脚本 #Python #行尾 #批量编辑 |

---

## 六、操作指导（guides/，怎么做）

> **2026-09-01 新建分类**：自 `lessons/` 迁出。判据 —— 本分类回答「**怎么做**」（操作手册 / 参考手册 / 工具用法），不是强制规范（standards），也不是已发生的坑（lessons）。

| 页面 | 摘要 | 标签 |
|------|------|------|
| [[guides/AntdUI-Reference]] | **AntdUI 完整参考与迁移手册**（1063 行，按章节跳转）：控件 API 迁移坑（Select/Table/GridPanel/Splitter/InputNumber）、Table 固定范式（Columns/DataSource/设计器序列化/Binding）、GridPanel Span 语法、Message/Modal Owner 规范、Menu+Tabs 导航正确用法、命名空间类型冲突（CS0104）、Modal 承载 UserControl 范式、Window+PageHeader 旧范式、FlowPanel 表单布局、Splitter→GridPanel 改造、ToolStrip→FlowPanel 改造、Table ColumnCheck 单选、SunnyUI 迁移对应、命名空间约定 | #指导 #UI #AntdUI #迁移 #设计范式 #Table #GridPanel #Modal #Menu #Tabs |
| [[guides/Project-Tools]] | **项目工具与流程手册**（959 行）：§1 代码图谱工具（**已废弃，历史参考**）· **§1.2 Grep 结果截断陷阱（影响半径检索必须两次独立检索交叉验证）** · §2 Wiki 工作流规范（**§2.1 日志追加位置规则**：新记录必须加在文件最顶部，保持严格时间倒序）· §2.5 批量重命名子串碰撞（须先查后改）· §3 图表工具 ScottPlot 4.1.74 · 虚拟相机与模拟模式 · 单例持久化启动加载 · .csproj 相关 | #指导 #工具 #项目配置 #日志 #重命名 #ScottPlot #模拟 #Grep |
| [[guides/WinForms-Designer]] | **WinForms 设计器规范与常见错误**：`*.Designer.cs` 不可修改、设计器下单例初始化陷阱、Controls.Add 前必须实例化、resx 孤儿类型引用、System.Void 基类级联、Bounds 哨兵值黑屏、Assimp RootNode 导入、ScottPlot FormsPlot 用法、Table/GridPanel/设计器序列化；**2026-08-19 澄清：DisposeComponents() 仅限 UI 类，非 UI 类须用标准 IDisposable.Dispose()（ADR-025）** | #指导 #UI #WinForms #设计器 #ScottPlot #3D |
| [[guides/WinForms-UI-Threading]] | **WinForms UI 线程与线程安全**：Workflow 事件 InvokeRequired、后台线程禁止模态 MessageBox、线程启动顺序（上电两阶段）、UI 线程封送、模拟启动异步等待、UI Message/Modal 的 Target/Owner 规范 | #指导 #UI #线程 #工作流 #线程安全 #模拟 |
| [[guides/Namespace-Compilation]] | **命名空间与编译错误排错手册**：**§1.1 代码文件注册到 `.csproj`**（新建 .cs 必须加 `<Compile Include>`，否则不参与编译）、命名空间迁移补 using、命名空间与类同名歧义、枚举命名空间重复、跨模块类型可见性嵌套、新增文件缺失 using、半成品代码引用不存在控件、P/Invoke 重复 DllImport、设计器 resx 孤儿引用 | #指导 #命名空间 #编译错误 #迁移 #csproj #代码质量 |
| [[guides/Config-Data-Tools]] | **配置/数据/工具手册**：INI 文件使用规范、Record.ini 绝对路径失效、SQLite 保留关键字、NuGet 多语言资源文件夹、XElement 类型转换、日志追加位置规范、.csproj 文件注册、单例持久化启动加载 | #指导 #配置 #INI #SQLite #NuGet #工具 #XML |
| [[guides/SourceBackup-GitHub]] | **AdaWeldSystem 云端源码备份（GitHub）操作手册**：repo 初始化/HTTPS+PAT 免密/`.gitignore` 忽略 3rdDepend 等/确定性脚本 `ada_backup.sh`（push/pull/status）/本地远端一致性校验/排错 | #指导 #GitHub #备份 #同步 #ada_backup |

---

## 七、设计决策（ADR）

> **编号说明（2026-09-03 整理）**：现存 **001~036 共 36 条，编号连续、无断号**。
> **下列「旧编号」已随决策页删除而失效——它们与现存同号条目并非同一决策，检索时请勿混淆**：
> 旧 006 / 009（SunnyUI 时期，见 [[project/SunnyUI-Legacy]]）、旧 023 / 024（一体化控制架构时期）、
> 旧 027 / 032 / 033 / 036 / 041 / 042（旧架构：设备四态 + 流程态 + 泛型 `TStep` 基类 + 独立状态机目录，2026-09-02 整页删除）、
> 旧 017 / 025 / 040 / 047 / 048（模拟模式 / 代码图谱 / 渐进式启动 / 步骤驱动 / 自动手动双流程，2026-09-03 用户裁定删除）。
> 上述页面**仍有效的结论**已全部并入 [[decisions/ADR-034-ThreeStateModelRefactor]]、[[decisions/ADR-036-RawDesignRefinement20260903]]、[[architecture/DeviceControlArchitecture]] 及本页各章节。
> ⚠️ **历史文档豁免**：`logs/` 工作日志与 `raw/` 原档中的旧编号**保留原貌**（改号会破坏可追溯性），检索时以本表为唯一准绳。

### 7.1 现行有效（accepted，编码前须遵守）

| 页面 | 摘要 | 标签 |
|------|------|------|
| [[decisions/ADR-001-DisposePattern]] | 为什么使用 DisposeComponents() 而非在 .cs/Designer.cs 中重写 Dispose；**2026-08-19 澄清：DisposeComponents() 仅限 UI 设计器类且按需使用，非 UI 类统一标准 IDisposable.Dispose()（见 ADR-025）** | #决策 #UI #资源释放 |
| [[decisions/ADR-002-CS73-Constraint]] | 为什么限制 C# 7.3 语法（MSBuild v4.0 兼容性） | #决策 #语法 |
| [[decisions/ADR-003-SingleAlgorithmFile]] | 为什么 ImageAlgorithm.cs 是唯一算法文件 | #决策 #算法 |
| [[decisions/ADR-004-WorkflowStepEnum]] | 为什么使用 7 Step 枚举替代顺序流程（switch 分派）；**与「步骤驱动」旧模型是补充关系而非冲突**——后者保留分派模型，只细化分派键并补时间维度（该模型已于 2026-09-03 清除） | #决策 #工作流 |
| [[decisions/ADR-005-CallbackAcquisition]] | 为什么 Workflow 取图使用回调等待模式；**2026-09-01 边界澄清**：其有界 `WaitOne`（上限 5000ms、超时可失败）**不违反**「单步禁阻塞等待」红线，判据「有界+可失败=合法」 | #决策 #相机 #异步 #回调 |
| [[decisions/ADR-006-CommRefactor]] | Comm 模块重构：合并文件、移除 MachineStatus、TCPIPComm 纳入 CommunicationManager | #决策 #通讯 #重构 |
| [[decisions/ADR-007-ConfigLayout]] | Config 文件夹按文件类型分层（INI/XML/GSDML） | #决策 #配置 #文件结构 |
| [[decisions/ADR-008-CommXmlSeparation]] | 通讯 XML 配置按设备类型分离：RobotServer/RobotClient/PLC 独立 XML + 独立日志开关 | #决策 #通讯 #XML #配置管理 |
| [[decisions/ADR-009-MonitorCameraModule]] | MonitorCam 监控相机模块架构：SDK 抽象、完全解耦、Live/PIL 双模式 | #决策 #相机 #监控 |
| [[decisions/ADR-011-WorkflowAsAdjustmentDriver]] | 工作流作为调整主驱动：RunAutoAdjust → WeldProcess.TriggerAdjustment（无参），WeldProcess 仅暂存帧特征；**目录已迁 `MainDeviceControl/DeviceWorkflow/`，结论不变** | #决策 #工作流 #焊接 #驱动 |
| [[decisions/ADR-012-MotionControlModule]] | 运控调整模块架构：VirtualCam（与 SmartRayCam 平级）+ MotionControl（独立模块）重构 | #决策 #运控 #模块 #解耦 |
| [[decisions/ADR-014-MonitorCamPage-AlgorithmInline]] | 监控相机页面命名与算法参数内联：`MonitorCamWorkJob` → `MonitorCamPage`，算法编辑内联右侧 panelRight；**实现控件已随 ADR-018 迁移为 AntdUI**（容器改 `System.Windows.Forms.GroupBox`、状态指示改 `AntdUI.Signal`），命名与「算法内联右侧」的决策精神不变 | #决策 #监控相机 #UI #命名 #算法编辑 |
| [[decisions/ADR-015-CameraConnectionStateDecoupled]] | 线激光相机连接态（连接/断开/工作中）与工作流程态解耦：CameraSelector 聚合派生 ConnectionState/Kind，工作流经 SetWorking 驱动「工作中」 | #决策 #相机 #状态机 #解耦 |
| [[decisions/ADR-016-CameraSelectorUnifiedToApi]] | CameraSelector 由 VirtualCam/ 上提至 LineLaserCam/Api/；命名空间改 `AdaWeldSystem.LineLaserCamApi`；VirtualCam 仅余 VirtualCameraRun | #决策 #相机 #目录 #接口层 #重构 |
| [[decisions/ADR-017-AlgorithmEditInterfaceSplit]] | 算法编辑界面按接口分隔（EmguALG vs 英莱）；**框架层已迁移**为 AntdUI.Tabs+UserControl | #决策 #UI #算法编辑 #AntdUI |
| [[decisions/ADR-018-UIFrameworkMigration]] | UI 框架从 SunnyUI（GPL v3）迁移至 AntdUI（MIT）；25/25 文件全部完成；状态：accepted（2026-07-28 确认） | #决策 #UI #迁移 #SunnyUI #AntdUI |
| [[decisions/ADR-019-DialogWindowToModalUserControl]] | 子对话窗承载方式：从 AntdUI.Window+PageHeader 改为 Modal 承载的 UserControl，8 个对话窗统一迁移到 SubView/ | #决策 #UI #AntdUI #Modal #UserControl |
| [[decisions/ADR-020-EnumDeduplication]] | 枚举去重策略：子命名空间禁止重复定义父命名空间已有枚举 | #决策 #枚举 #命名空间 #DRY |
| [[decisions/ADR-021-NuGetLocalization]] | NuGet 本地化：移除全部 PackageReference，改为 bin\Debug\3rdDepend\ 本地 DLL 引用（53 托管 + 28 原生），实现离线构建 | #决策 #NuGet #本地化 #依赖管理 |
| [[decisions/ADR-022-ZMotionControllerIntegration]] | **2026-08-10** 正运动控制器接入架构：ZMotion/ 子目录实现 + 基类继承 + MotionManager 工厂方法 + 失败回退 + 原生 API 精简封装 | #决策 #运控 #正运动 #控制器 #架构 |
| [[decisions/ADR-023-RSICamBoxTrackingArchitecture]] | **2026-08-11** RSI-CAMBOX 硬件级实时焊缝跟踪架构：运动实时链路 100% 硬件总线化，PC 退化为非实时轨迹规划器 | #决策 #运控 #RSI #CAMBOX #正运动 #实时跟踪 #EtherCAT |
| [[decisions/ADR-024-LayoutContainerFreedom]] | **2026-08-12** 布局容器自由化：解除 GridPanel/FlowPanel 强制使用；按需自由选择；AntdUI 缺失控件可用原生控件，SunnyUI 禁用；不重写已有页面 | #决策 #UI #GridPanel #FlowPanel #布局 |
| [[decisions/ADR-025-DisposePatternFullCoverage]] | **2026-08-19** Dispose 模式全覆盖：非 UI 类统一标准 IDisposable.Dispose()（迁移 Workflow×4/ZMotion×4/Comm×4 + 新增 CommunicationManager/TcpIpComm/ZMotionController 释放入口 + FormMain 关闭级联链）；第二轮：UI 类按需使用 DisposeComponents() | #决策 #资源释放 #IDisposable #全覆盖 |
| [[decisions/ADR-026-LineLaserWorkflowRefactor]] | **2026-08-20** 线激光工作流分步重构：从 7 态扩展为 9 态（新增 PreWork/Working/Stopping），switch-case + step 分步结构，待机时传感器/激光均关闭（安全默认态） | #决策 #工作流 #线激光 #状态机 #分步驱动 |
| [[decisions/ADR-027-DefaultInitZMotion]] | **2026-08-21** 默认初始化切到正运动控制器 + 删除 Null 空控制器；CAMBOX 跟踪随正运动句柄自动初始化 | #决策 #运动控制 #正运动 #CAMBOX |
| [[decisions/ADR-028-CodeSimplificationStandard]] | 代码精简规范沉淀决策：固化为标准页并由 index 路由，免重复输入；**范围裁定见 [[lessons/CodeSimplification-Scope-DesignerOnly]]** | #决策 #代码精简 #规范沉淀 |
| [[decisions/ADR-029-YinglaiDataFlow]] | **2026-08-18** 英莱线激光数据流架构：CamRun 数据分发中心 + Running 单态监听调整一体化 + ScottPlot Signal 模式高性能轮廓显示 | #决策 #线激光 #英莱 #数据流 #ScottPlot |
| [[decisions/ADR-030-WorkflowResponsibilityBoundary]] | **2026-08-31** 流程与子设备对象权责边界 R1~R5：核查 6 子流程发现 11 处越权（5 个零订阅死代码 + `DisplayEvent`/`FrameCompletedEvent` 双通道 + 依赖倒置）；治理后自定义工作流事件归零、健康巡检下沉 `MonitorCameraRun`、`MonitorCameraPhase` 下沉子设备 Api 层。执行细则 [[standards/WorkflowResponsibilityBoundary]] | #决策 #权责边界 #工作流 #子设备 #事件 #ADR-030 |
| [[decisions/ADR-031-SafetyCheckConsolidation]] | **2026-08-31** 安全检查三文件合并为单一 `SafetyWorkflow.cs`（2026-09-02 ADR-034 重设计命名为 `DeviceStatusWork.cs`、改为 `IOWork`/`EMGWork`/`StatusWork` 三线程、非泛型 `DeviceWorkflowBase`）；`FaultCategory`/`FaultRecord` 迁入 `FaultRecoveryManager.cs`；**⚠️ 2026-09-03（裁定 C3）**：`IsRobotPoseSafe` 已**移除**（不再监控机器人 pose），改为直接读 `DeviceStatusWork.Instance.IsSafe`（未启动返 true）；删伪异步 `CheckAsync` | #决策 #架构 #安全互锁 #文件合并 #DeviceStatusWork #ADR-034 |
| [[decisions/ADR-032-ButtonShadowDeviceSwitch]] | **2026-08-31** MainPage 硬件快捷开关 FloatButton→ButtonShadow；同日风格迭代：50×50 仅 SVG 图标 + TooltipComponent 提示 + 原生徽标 Badge 红/绿 + 预留 SetDeviceIconSvg/SetDeviceBadgeSvg | #决策 #UI #MainPage #快捷开关 #ButtonShadow #AntdUI |
| [[decisions/ADR-033-ProductLifecycleRecordModule]] | **2026-08-31 + 2026-09-01 §3 追加** 产品生命周期记录归口：`PCLOperate/RunFileRecord/` 迁入 `ProductFileManager/`（命名空间 `AdaWeldSystem.ProductFileManager`，公共 API 不变）；新建 `SqlLiteDatabase/FaultRecordManager.cs`；**§3：`FaultRecoveryManager.cs` 自 `MainDeviceControl/DeviceWorkflow/` 迁入 `ProductFileManager/`**，6 消费方补 using；**保留 `FaultRecord.State` 强类型 DeviceState 枚举**（接受 ProductFileManager ↔ MainDeviceControl 枚举级循环依赖，架构页 11.3 环数 4→5）；DB 层不反向依赖领域类型 | #决策 #产品记录 #文件迁移 #故障恢复 #归口 #循环依赖 #SQLite #ProductFileManager |
| [[decisions/ADR-034-ThreeStateModelRefactor]] | **2026-09-02（✅ accepted，现行有效；⚠️ 2026-09-03 枚举取值由 ADR-036 更新：`SubDeviceWeldStatus` 删 `Starting`、新增 `NoReset`(0)，余值顺延）** 三态模型重构：删除四态 `DeviceState` 枚举，改为 `SubDeviceState`(连接态,2) + `SubDeviceWeldStatus`(焊接过程态,7) + `MainDeviceStatus`(主设备运行态,6) 三态；基类由泛型 `DeviceWorkflowBase<TStep>` 改为非泛型 `DeviceWorkflowBase`（承载 State/WeldStatus/SetWeldStatus/StateSwitched/WeldStatusChanged）；`MainDeviceWorkflow`→`DeviceControlWork`、`SafetyWorkflow`→`DeviceStatusWork`（三线程 IOWork/EMGWork/StatusWork）；`MainDeviceFlowState` 删除。取代此前「设备态四态 + 泛型 TStep 基类」设计；原步骤驱动决策与双流程决策已由 ADR-036 整体取代并删除 | #决策 #架构 #三态模型 #SubDeviceState #SubDeviceWeldStatus #MainDeviceStatus #非泛型 #ADR-034 |
| [[decisions/ADR-035-ArchitectureRawSource]] | **2026-09-02（✅ accepted，当晚扩充 2→3；2026-09-03 收敛 3→2）** 架构原档单一来源约定：**现役 2 份**——`raw/architecture/主控设计.xlsx`（静态结构/枚举真值/成员级清单）+ `激光焊接系统业务流程图.pdf`（业务状态流 + 检查清单，含文本层）；旧两份 PDF 与 3 张渲染图于 2026-09-03 删除。沉淀为**架构唯一修改入口**——用户后续只改这两份原档，AI 按流程同步架构页（原档 > 架构页 > 源码注释，冲突须用户裁定）。**原档删除即视为架构意图变更**，须核对取代者的内容覆盖情况 | #决策 #架构 #知识库治理 #原档 #单一来源 #ADR-035 |
| [[decisions/ADR-036-RawDesignRefinement20260903]] | **2026-09-03（✅ accepted，用户已逐条裁定）** 原档细化的**完全重构**与冲突裁定：元原则=新档是**全新设计而非对旧文档的补充**，改码不得沿用旧设计思维填补空缺。C1~C7 裁定结论——C1 `DeviceControlWork` 起 7 条常驻线程驱动子流程、**基类监听线程机制全部清除**；C2 `SubDeviceWeldStatus` 删 `Starting` 加 `NoReset`(0)；C3 指令改 `CommandCore` **const string** 解析、**删除三个枚举与 pose 监控**（消费方 `// todo`）；C4 `InitializeOn/Off` 阻塞 vs `ConnectOn/Off` 非阻塞，**两组并存不重叠**；C5 `Comm` 提供通讯方法与管理、`DeviceControlWork` 是使用方；C6 命名改 `RunStep`/`StepWorkTime`/`TimeOutSeconds`(秒)；C7 `SubDeviceLog()` 为 **`public abstract`**，每个子流程各自重写。原步骤驱动决策与双流程决策已整页废弃并删除，模拟模式决策已废弃并删除，三态模型枚举取值更新。另：D1 配置读写走本项目 `XdocumentReaderWriter`（子设备各自持有路径）；D2 `ClearProduct()` **暂不实现**。落地分 5 批，见 [[architecture/DeviceControlArchitecture]] §15.2 | #决策 #架构 #原档驱动 #完全重构 #线程模型 #CommandCore #ADR-036 |

### 7.2 待决 / 进行中（proposed）

当前无待决 ADR。

### 7.3 已废弃 / 已被取代 / 已回退（仅历史追溯，编码前不得引用其失效结论）

| 页面 | 失效结论 | 现行真相源 |
|------|---------|-----------|
| [[decisions/ADR-010-WeldActionRecord]] | **仅「归属目录/命名空间」失效**（已从 `Workflow/` 迁 `ProductFileManager/`）；双记录设计（ProcessFrame/WeldParamAdjust）**仍有效** | [[modules/ProductFileManager]]、ADR-033 |
| [[decisions/ADR-013-WorkflowAsHub]] | ①「所有工作流迁入 `Workflow/`」被推翻（现 `MainDeviceControl/DeviceWorkflow/`）②`MonitorSupervisionWorkflow` 健康巡检被推翻（下沉 `MonitorCameraRun`）；仅 `MonitorAlgorithmManager` 仍有效 | [[modules/DeviceControl]]、[[standards/WorkflowResponsibilityBoundary]] |

---

## 八、历史归档（现归 project/）

> **2026-09-01 目录合并**：`archive/` 分类**已取消**——它与 `architecture/` 同是全库最小的分类（1~2 页），且名字相近易混。其中 2 页（UI 迁移史、精简进度快照，均非架构内容）迁入 `project/`，**全库不再设归档分类**。
> **同时收口第二个架构页**：原 `project/architecture.md`（模块依赖图）**并入** [[architecture/DeviceControlArchitecture]] 第 11 章，全库只保留**一个**架构页。
> **架构历史版本**：7 个 V2/V3 代际架构/模块页已删除，其中仍有效的技术要求已并入架构页；架构演进脉络查 [[decisions/ADR-034-ThreeStateModelRefactor]]（若干早期架构 ADR 已整页删除）。

| 页面 | 摘要 | 标签 |
|------|------|------|
| [[project/SunnyUI-Legacy]] | **已归档** SunnyUI 框架历史内容：UI 框架迁移总览、废弃决策（**UILight 属性规范** / **全局 UI 风格统一为 Purple**）、迁移教训汇总、迁移状态追踪；2026-07-28 全面迁移至 AntdUI 后归档 | #归档 #SunnyUI #UI #历史 |
| [[project/CodeSimplification-Progress-20260826]] | **2026-09-01 归档**（原 `standards/CodeSimplification-progress`）代码精简修复进度快照：2026-08-26 基线扫描（112 文件 / 1089 警告 / 1315 提示）的英莱轨道与文件夹轨道计数。历史快照，与当前代码已不同步 | #归档 #代码精简 #进度快照 |

---

## 九、专员职责

| 页面 | 摘要 | 标签 |
|------|------|------|
| [[people/Architect]] | 架构开发员：整体架构、模块划分、接口定义 | #专员 #架构 |
| [[people/QASpecialist]] | QA/测试专员：代码审查、测试计划、Bug 归属 | #专员 #QA |
| [[people/CameraSpecialist]] | 工业相机开发专员 | #专员 #相机 |
| [[people/ImageAlgorithmSpecialist]] | 图像算法开发专员 | #专员 #图像算法 |
| [[people/3DSpecialist]] | 3D开发专员 | #专员 #3D |
| [[people/GeneralTechSpecialist]] | 通用技术开发专员 | #专员 #通用技术 |
| [[people/DatabaseSpecialist]] | 数据库开发专员 | #专员 #数据库 |
| [[people/WeldProcessSpecialist]] | 焊接工艺开发专员 | #专员 #焊接 |
| [[people/MotionControlSpecialist]] | 运动控制开发专员 | #专员 #运动控制 |
| [[people/UISpecialist]] | UI开发专员 | #专员 #UI |

---

## 十、来源索引

| 来源文件 | 类型 | 对应 Wiki 页面 |
|----------|------|---------------|
| raw/skills/AdaWeldsys_Skills/00-Root/SkillRoot.md | Skill 规范 | [[project/skill-evolution]]、所有 people/ 页面 |
| raw/skills/AdaWeldsys_Skills/04-Style/CSharpStyle.md | 代码规范 | [[decisions/ADR-002-CS73-Constraint]] |
| raw/skills/AdaWeldsys_Skills/05-Tools/CodeGraph.md | 代码图谱参考文档 | [[guides/Project-Tools]] |
| raw/skills/AdaWeldsys_Skills/03-Workflow/WorkMap.md | 工作流地图 | [[project/vibecoding-workflow]] |
| raw/history/history.md | 开发历史 | [[project/skill-evolution]]、多个 lessons/ 和 decisions/ |
| raw/knowledge/AdaWeldSystem_Wiki.md | 项目知识库 | [[project/overview]]、[[architecture/DeviceControlArchitecture]]、所有 modules/ 和 api/ |
| raw/knowledge/emgu-cv-knowledge-base/ | 第三方知识 | [[modules/EmguALG]]、[[people/ImageAlgorithmSpecialist]] |
| raw/knowledge/helixtoolkit-knowledge-base/ | 第三方知识 | [[modules/PointCloudData]]、[[people/3DSpecialist]] |
| raw/knowledge/KUKA_OPT/KST_RSI_33_zh.pdf | KUKA 技术文档 | [[modules/KUKARobot]]、[[api/KUKARobot]] |
| raw/knowledge/KUKA_OPT/KST_Ethernet_KRL_22_zh.pdf | KUKA 技术文档 | [[modules/KUKARobot]]、[[api/KUKARobot]] |
| raw/architecture/主控设计.xlsx | **架构原档（ADR-035，唯一修改入口）**：文件/职责/三态枚举真值 + **2026-09-03 细化到成员级**（基类 17 项契约 / 5 子工作流差异化职责 / `DeviceControlWork`+`DeviceStatusWork` 线程·私有方法·公共方法全表 / 新增 `CommandCore` 与 `SubDeviceWeldStatus.NoReset`） | [[architecture/DeviceControlArchitecture]]、[[decisions/ADR-034-ThreeStateModelRefactor]]、[[decisions/ADR-036-RawDesignRefinement20260903]] |
| raw/architecture/激光焊接系统业务流程图.pdf | **架构原档（ADR-035，唯一修改入口；2026-09-03 新增，取代已删除的两份旧 PDF）**：整机业务状态流 + 检查清单——上电 5×Connect On+通讯 Open+IO Work → 三失败分支 → ResetMachine → **Preworking 五项运行检查** → **Working 四路焊接子流程** → 三终止分支 → 报警判断（故障树和代码）；旁路 EMG STOP→子设备停机锁止。**PDF 含文本层，pypdf 直接提取，无需渲染** | [[architecture/DeviceControlArchitecture]] §7.6/§7.7/§7.8、[[decisions/ADR-035-ArchitectureRawSource]]、[[decisions/ADR-036-RawDesignRefinement20260903]] |

---

## 维护说明

### 体检与漂移扫描脚本

| 脚本 | 职责 | 健康判据 |
|------|------|---------|
| `tools/wiki_audit.py` | 只读 10 项体检：红链 / 孤儿页 / 索引重复行 / ADR 编号空洞 / 页面体积 / 疑似内容重复 / `lessons/` 错放 / `standards/` 入链 / 二级子目录 / 过小分类 | 红链 0 · 孤儿页 0 · 索引重复行 0 · 二级子目录 0 · 过小分类 0 |
| `tools/lint_scan.py` | 死链 / 孤儿页 / ADR 编号冲突 / 外部文件链接失效 | 除 `project/vibecoding-workflow` 的模板占位符（`modules/XXX`、`decisions/ADR-XXX`）外无命中 |
| `tools/drift_scan_precise.py` | wiki 页引用的 `.cs` 文件在代码库中已不存在 | **待修正 0 处** |

**执行方式**：在 `Vicoding管理平台/LLMWiki/` 目录下运行 `python tools/<script>.py`。

**健康判据**：红链 0 · 孤儿页 0 · 索引重复行 0 · 页面均 < 600 行（超限须加章节 TOC 或拆分）。
**分类判据**：写新页前先判三层 —— 必须遵守放 `standards/`、踩过的坑放 `lessons/`、怎么做放 `guides/`。

#### drift_scan_precise.py 口径（2026-09-03 重写）

- **当前基线**：待修正 0 处 / 已标注 116 处。每一处失效引用都带显式「现役 `X.cs`」或「已移除（原因）」注记。
- **四点分诊**：`RENAMED`（有现役对应）/ `REMOVED`（已删除需注明原因）/ `EXTERNAL`（外部参考项目 `PcomDeviceInterface/`、`HonorMachineTest/`）/ `SPECULATIVE`（设想或 demo 文件，从未落地）。**只有前两类计入待修正**。
- **历史 ADR 页**用页首 `> ⚠️ 历史名称提示` 横幅统一标注（纯新增、零删除），正文保留旧名以留存决策上下文。
- **横幅块自身豁免**：从 `> ⚠️ 历史名称提示` 起的连续 `>` 行不再逐行判漂移——那些行本就是在列举「旧名 → 现役」映射，再判一次是自伤。
- **正则必须带双侧边界断言**：`(?<![A-Za-z0-9_.])([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*\.cs)(?![A-Za-z0-9_.])`。无断言版本把 `FormMain.Designer.cs` 截成 `Designer.cs`，一次产生 144 处误报。

#### 两条脚本编写红线（2026-09-03 踩坑）

1. **路径自愈**：`tools/` 下脚本一律用 `__file__` 推导路径，禁止硬编码绝对路径。迁移机器后硬编码路径会让扫描器**静默扫到 0 个文件并报告「健康」**——比崩溃更危险。
2. **行尾保持**：wiki 页在仓库中以 **LF** 入库（`core.autocrlf=true` 只影响 checkout）。脚本批量编辑必须**按字节读写**并原样回写探测到的换行符，禁止 `open(p).read()` + `open(p,"w").write()`。收尾用 `git diff --numstat` 确认没有文件的改动行数 ≈ 其总行数。详见 [[lessons/WikiDriftCorrectionPitfalls]]。

#### wiki_audit.py 的链接解析豁免（2026-09-03）

红链检测会先 `mask_code()`——用**等长空白**替换围栏代码块与行内代码体（保持字符偏移与行号不变），再解析 `[[链接]]`。
否则规范文本中举例说明的「不要写 `[[old]]→[[new]]`」会被判成 2 条真红链。
即便如此，**日志与正文中的页面改名映射仍建议写成纯文本** `api/old → api/new`，因为纯文本被复制出代码体后依然成立。
