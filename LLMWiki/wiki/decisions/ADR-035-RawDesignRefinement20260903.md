---
title: ADR-035 原档 9-03 细化：主控设计完全重构与冲突裁定
date: 2026-09-03
updated: 2026-10-30
tags: [决策, 架构, 主控设计, 原档驱动, 已裁定, ADR-035, 三态模型, 线程模型, CommandCore]
status: accepted
---

# ADR-035 原档 9-03 细化——主控设计完全重构与冲突裁定

> **状态：accepted（2026-09-03 用户逐条裁定）**。本 ADR 记录 2026-09-03 用户修订 `raw/architecture/` 原档后的**架构意图变更**，以及用户对 7 项冲突的**逐条裁定**。
> 逐项落地表见 [[architecture/DeviceControlArchitecture]] §15；架构页已按本裁定**整体重写**。

## 背景

2026-09-03 用户更新 `raw/architecture/` 原档（ADR-007 唯一修改入口）：

1. `主控设计.xlsx` —— 从「一句话职责」细化为**成员级清单**（基类 17 项契约、5 子工作流差异化职责、两个独立管控类的线程/私有方法/公共方法全表），新增 `CommandCore` 与 `SubDeviceWeldStatus.NoReset`。
2. `激光焊接系统业务流程图20260904.md`（2026-09-04 新增，**业务流主源**）—— 用户人工全量转写版（706 行），取代 `激光焊接系统业务流程图.pdf` 成为提取对象；在原 PDF 基础上补齐 §2 IO 统一触发架构、§3.4 双态映射、§10 共 21 条机器人命令设计。PDF 保留为图形备份。

AI 重读原档、与 git HEAD 逐单元格 diff、提取 PDF 全文后，识别出 7 项与现行「步骤驱动」「双流程」「三态模型」三项决策或代码冲突之处，按 ADR-007 §3 **提交用户裁定**（未裁定不得改码）。

## 决策

### 0. 元原则：完全重构，不是补充（用户确立）

> 用户原话：「首先需要明确新的结构文档为全新设计和细化，不要带入老旧文档的设计思维，不是对旧文档的补充，是完全的重构。」

处理：架构页 [[architecture/DeviceControlArchitecture]] **整体重写**，不再以「旧 vs 新对照」的框架组织内容，而是直接表述新设计；被清除的旧机制只在页首「已清除的旧设计」表中留一行索引，正文不再保留其表述。改码与改文档时**不得沿用旧设计思维填补空缺**——原档未覆盖处才参考现有代码事实。

### 1. 七项冲突的裁定结论

| # | 裁定 | 用户原话要点 | 落地要求 |
|---|---|---|---|
| **C1** | 以新档为准，**旧设计全部清除** | 「旧文档设计的全部清除，以新档为准」 | `DeviceControlWork` 起 7 条常驻线程（5 子设备 + 2 通讯）驱动各子流程 `FlowProcess()`；**删除**基类 `DeviceWorkflowBase` 的常驻监听线程机制（`StartRunLoop` / `BeatMs` / `RunLoopPriority`） |
| **C2** | 以新档为准，**旧设计全部清除** | 同上 | `SubDeviceWeldStatus` 删 `Starting`，新增 `NoReset`（值 0），其余值顺延 |
| **C3** | 以新档为准 | 「机器人指令就是 String 方式解析得到。原定义完全删掉，不在监控机器人的 pose，因为设备运行全靠机器人指令驱动，设备无权限管理机器人状态。消费方可先 // todo」 | 改名 `CommandCore.cs`；指令用 **const string**；**按字符串解析**；删除三个枚举 + `RobotPoseCode` + 全部 const int；**不再监控机器人 pose**；消费方先 `// todo` 占位 |
| **C4** | 两组并存、**不重叠** | 「新文档 `InitializeOn`/`Off` 为阻塞连接，`ConnectOn`/`Off` 为非阻塞连接」 | `InitializeOn`（同步等待）/ `InitializeOff`（异步等待）属**阻塞**组；`ConnectOn` / `ConnectOff`（动作即退出释放）属**非阻塞**组 |
| **C5** | 职责分离 | 「Comm 提供的是机器人/PLC 通讯方法和管理，ControlWork 作为实际使用方」 | `Comm` 提供通讯方法与管理；`DeviceControlWork` 在 `InitializeMachine` 中**调用**其方法完成通讯 Open + Connect On，不自行实现通讯协议 |
| **C6** | 以新档为准 | 「以新档为准」 | 用 `RunStep` / `StepWorkTime` / `TimeOutSeconds`（秒），取代 `WorkStep` / `WorkStartTime` / `_timeoutMs`（毫秒） |
| **C7** | 原档笔误，实为 `public` | 「就是 Public，可能是我笔误。现在设计的很臃肿，以新档为准，每个流程下重新一次 log 的方法」 | `public abstract void SubDeviceLog()`；**每个子流程各自重写**，不走基类统一 `Log` 出口 |

### 2. 原档集合收敛 3 → 2（已生效）

现役原档 = `主控设计.xlsx`（静态结构）+ `激光焊接系统业务流程图20260904.md`（业务流 + 检查清单 + IO 触发 + 命令表，主源）。旧两份 PDF 及 3 张渲染图已删除；泳道图覆盖的「类协作时序」信息在新原档中不再覆盖，该部分以代码事实为准。

### 3. 受影响的既有 ADR 处置

| ADR | 状态 | 说明 |
|---|---|---|
| 步骤驱动工作流决策（已删除） | **部分被取代** | 线程模型（基类监听线程）**已废**；步骤驱动思想保留但机制改为 `RunStep` + bool 推进，`GoStep` / `SetStep` / `FailFlow` / `FailReason` / `FailStep` 等基类成员**全部清除** |
| 自动/手动双流程决策（已删除） | **需修正** | 「`FlowProcess` 唯一执行器」表述与新档不符——新档有 `FlowProcess` + `ResetProcess` 两个流程方法，**均**由 `RunStep` 驱动 |
| [[decisions/ADR-013-ThreeStateModelRefactor]] | **模型保留，枚举更新** | 三态模型（三个正交枚举）不变；`SubDeviceWeldStatus` 按 C2 调整取值，`SubDeviceState` 维持 2 态 |

### 4. 落地批次

裁定后改码按 5 批推进（详见架构页 §15.2）：

| 批次 | 内容 | 关键风险 |
|---|---|---|
| 0 | 枚举调整 + `CommandCore` 指令协议 | `FaultRecord.State` 历史值语义变化；`.csproj` 须同步 |
| 1 | 基类 17 项契约（**5 子类连锁**） | ⚠️ `LineLaserWorkflow` 已有 `RunStep` 方法 → **CS0102**，须先改名；基类新增抽象成员 → 5 子类同时编译失败 |
| 2 | `DeviceControlWork` 7 线程重构 | **须与批次 1.5 同批**——删基类线程与加编排线程不能留中间态 |
| 3 | `DeviceStatusWork` 线程命名统一 | 低风险 |
| 4 | 业务行为补全（温度阈值 / 轴控 / 送丝检测 / 工艺 bool / Preworking 五项 / Working 四路） | 纯新增，可增量 |

### 5. 参考实现模板：改码须套用（用户要求，2026-09-03）

> 用户原话：「在实现代码的时候，你仔细查看我给你的代码参考，你需要按照我给你的代码作为模板来设计重构设计代码修正方案。」

原档 `主控设计.xlsx` R007~R014 在「主要内容描述」列首行**逐类标注了参考实现路径**，指向既有项目
`HonorMachineTest`（`E:\SoftwareGit\HonorMachineTest\PcomDeviceInterface\Work\`）：

| 目标类 | 原档指定参考 |
|---|---|
| `DeviceWorkflowBase.cs` | `Process/StationProcess.cs` |
| `LineLaserWorkflow` / `LaserWeldHeadWorkflow` / `MonitorCameraWorkflow` / `WeldParamControlWorkflow` | `Process/RollPressProcess.cs` |
| `MotionControlWorkflow` | `Process/AssemblyProcess.cs` |
| `DeviceControlWork.cs` | `Work/MachineControlWork.cs` |
| `DeviceStatusWork.cs` | `Work/MachineStatusWork.cs` |

**决策**：上述 5 个参考文件为改码的**结构模板**，骨架与编码范式提炼进架构页 §16，
改码时按模板套用；**原档与参考实现冲突时以原档为准**，差异逐项登记（§16.7）。

已提炼的强制范式（详见架构页 §16）：

- **子流程 S1~S8**：`FlowProcess()` 首行启用门控 → `switch (RunStep)` → 每 `case` 内 bool 判定推进 →
 **改步必同步刷新步骤计时** → 原语 false 则 `break` 停在本步重试 → `ResetProcess()` 为线性阻塞链（非步控）
- **编排 M1~M9**：线程体五段式（`while(!IsClose)` → 非 Running 分支 `Sleep(100)` + `ResetWorkTime()` + `continue` →
 `FlowProcess()` → `Sleep(10)`）→ 复位走一次性 `Task` + 内部两步机 → `StartMachine()` 只切状态
- **状态 T1~T6**：线程进出成对维护标志位 → 急停边沿触发 → 三色灯 `switch (CurrentStatus)` 驱动

### 6. D1 / D2 裁定（用户，2026-09-03）

| # | 裁定 | 落地口径 |
|---|---|---|
| **D1** | **使用本项目的 XML 文档写法；子设备 workflow 中增加路径** | `LoadConfig()` / `SaveConfig()` **无参**，内部走 `AdaWeldSystem/FileOperate/XMLfile.cs` 的 `XdocumentReaderWriter`（`XDocument` / LINQ to XML；**2026-09-21 更新**：默认目录已废弃，落盘目录由构造参数 `relativeDirectory` 显式决定，如 `Config\LineLaser\LineLaser_XML`）。**不引入**参考实现的 `XmlReader` / `XmlWriter` 流式 API（避免两套 XML 体系分裂配置管理）。配置**路径由每个子设备 workflow 各自持有**（文件名成员 + 惰性读写器），基类只声明契约、不持有路径。模板见架构页 §4.6、§16.8 |
| **D2** | **`ClearProduct()` 暂不保留、暂不实现** | 清料逻辑须结合 `ProductFile` 一并设计，当前不成熟。**基类契约与 5 个子类均不新增**该成员，避免 5 个空实现污染契约；待 `ProductFile` 方案确定后另立 ADR |

> **D1 的四条铁律**（写入架构页 §16.8）：
> ① `SaveConfig()` 末尾必须 `Config.SaveXdocument()`（`SetElementValue` 只改内存）；
> ② 路径只在子设备 workflow 内定义，基类不硬编码文件名；
> ③ 读值一律走带默认值重载 `GetElementValue(name, defaultValue)`；
> ④ `XdocumentReaderWriter` 非线程安全，运行期禁止在 `FlowProcess()` 内读写配置。

## 备选方案

| 方案 | 说明 | 为何未采纳 |
|---|---|---|
| 直接按原档全量改码 | 一次性对齐 17 契约 + 7 线程 | 违反 ADR-007 §3「冲突须用户裁定」；C1/C2 一动全项目，未裁定即改不可回退 |
| 维持现状不记录 | — | 违反 ADR-007「原档即唯一入口」，架构页会与原档持续漂移 |
| 在旧架构表述上追加新内容 | 保留旧框架，新增章节描述新设计 | **用户明确否决**——「不要带入老旧文档的设计思维，不是对旧文档的补充，是完全的重构」 |

## 后果

### 正面

- 原档细化到成员级后，架构页首次具备「按原档逐条比对代码」的能力，架构漂移可被机械检出。
- 7 项冲突全部裁定，改码路径不再有悬而未决的阻塞点。
- 架构页整体重写后，不再存在「新旧两套描述并存」的认知负担。

### 负面 / 风险

- **C1 + C6 的组合改动面最大**：线程模型回退 + 5 子类契约重建，须一次性完成不可分批。
- **批次 1 与批次 2 必须同批**：删基类线程与加编排线程之间若留中间态，无人驱动 `FlowProcess`。
- **C3 遗留 `// todo`**：机器人指令的字符串协议尚未细化到消费点，20+ 处消费点暂时占位。
- **C2 影响历史数据**：`FaultRecord.State` 持久化值语义变化，需确认是否做值迁移。
- 沙盒无 C# 编译器，全部结论为静态自检，真编译须在 Visual Studio 验证。

## 相关页面

- [[architecture/DeviceControlArchitecture]] —— 唯一真相源，已按本裁定整体重写；§15 为落地清单
- [[decisions/ADR-034-ArchitectureRawSource]] —— 原档优先原则与同步流程
- 步骤驱动决策、双流程决策（均已删除）—— 受影响 / 部分被取代
- [[decisions/ADR-013-ThreeStateModelRefactor]] —— 部分被取代的 ADR
- [[lessons/StepDrivenWorkflowPitfalls]]（坑三：基类抽象成员连锁）、[[lessons/StepDrivenWorkflowPitfalls]]（七.6）（CS0102）—— 改码门禁
- [[modules/DeviceControl]]、[[api/DeviceControlWork]]、[[api/DeviceStatusWork]] —— 受影响页面（`api/DeviceLog` 页已随 `DeviceLog.cs` 于 2026-09-04 移除）
