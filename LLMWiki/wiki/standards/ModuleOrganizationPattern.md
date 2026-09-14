---
title: 模块组织范式标准（Core · 抽象层 · 实现层 · Manager）
date: 2026-09-14
tags: [规范, 模块组织, 分层架构, 抽象层, 实现层, Manager, 第三方库封装, 持久化配置]
status: accepted
---

# 模块组织范式标准（ModuleOrganizationPattern）

> **触发**：用户提出「新增一个模块 / 改造一个模块 / 抽象层·实现层·Manager 怎么摆 / 封装一个第三方库 / 新增一个算法族 / 哪一个类该对外」时，AI **直接读取本页执行**，无需用户重复输入结构要求。
>
> **适用范围**：全项目所有「**一个功能族 = 多实现 + 统一入口**」型模块（相机、运控、算法、焊接工艺等）；不适用于 `UIDesign/` 页面层与 `MainDeviceControl/` 流程层（后者见 [[standards/WorkflowResponsibilityBoundary]] 与 [[architecture/DeviceControlArchitecture]]）。
>
> **沉淀决策**：[[decisions/ADR-042-ModuleOrganizationPatternStandard]]。各模块的落地先例见 [[decisions/ADR-036-LineLaserManagerSingleEntry]]（线激光）、[[decisions/ADR-037-MecaVisionMonitorCamera]]（监控相机）、[[decisions/ADR-038-EmguALGThreeLayer]] / [[decisions/ADR-039-MonitorCamBoundaryAndEmguALGRefinement]]（算法）、[[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]]（焊接工艺）。
>
> **原档依据**：`raw/knowledge/算法程序改造指导_抽象实现Manager三层_v2.0.md`（该文档为二手资料且基线为另一形态，落地时以代码现实为准，见 ADR-038 的三处错位表）。

---

## 一、一句话范式

> **一个功能族 = 抽象层（对外契约）+ 实现层（各自实现）+ Manager（唯一入口）；基于第三方库开发时，另加 Core（功能封装核心）。**

用户 2026-09-14 裁定：模块组织按「**是否基于第三方库**」分为两种场景；两者的抽象层 / 实现层 / Manager 三件套**完全一致**，差别只在 **Core 是否强制**。

---

## 二、两种场景

### 场景 A：基于第三方库开发

| 组件 | 是否必需 | 职责 |
|---|---|---|
| **Core（功能封装核心）** | ✅ **必需** | 把第三方库的原子能力封装成模块内可复用的纯技术层；厂商 SDK 只允许在此被引用，业务语义不得进入 |
| **抽象层（抽象类文件夹）** | ✅ 必需 | 定义**对外功能与属性**的抽象契约；零第三方依赖 |
| **实现层（实现类文件夹）** | ✅ 必需 | **所有需要使用的功能都必须继承抽象类并实现**；同一抽象可有多个实现（不同厂商 / 真实 + 虚拟） |
| **Manager** | ✅ 必需 | **管理所有功能类对象与数据、持久化配置、对外的唯一访问口** |

### 场景 B：非第三方库功能开发

| 组件 | 是否必需 | 职责 |
|---|---|---|
| **Core（功能封装核心）** | ⚠️ **按需** | **不强制**。只有「需要自己定义一整套算法结构与复杂处理」时才建独立 Core；原则上不建——属于该功能类的函数与算法**直接写在实现类中** |
| **抽象层（抽象类文件夹）** | ✅ 必需 | 定义对外属性与接口；自研场景下它同时承担「算法家族公共契约」的角色 |
| **实现层（实现类文件夹）** | ✅ 必需 | 所有功能都必须继承抽象类并实现 |
| **Manager** | ✅ 必需 | 管理所有功能类对象与数据、持久化配置、对外唯一访问口 |

> **判据**：Core 存在的唯一理由是「有一层**与业务无关的纯技术封装/算法结构**值得独立复用」。第三方 SDK 适配天然满足（故强制）；纯自研功能若只是「几个公式 + 几张表」，把它们写进实现类即可，多建一层 Core 只会制造跳转成本。

---

## 三、四个组件的判定标准

### 3.1 Core（功能封装核心）

- **装什么**：第三方 SDK 的原子能力（P/Invoke 封装、协议解析、原生句柄生命周期），或自研场景下自成体系的算法结构（如算子库）。
- **不装什么**：业务语义、状态机、事件分发、配置持久化——这些分别属于实现层与 Manager。
- **落地位置无强制**（三种均可，视 SDK 体量选择）：
  1. 独立 `Core/` 文件夹 —— 体量大、被多实现共用，如 `EmguALG/Core/`（`AlgorithmBase` / `PreprocessConfig` / 算子 `ImageAlgorithm.cs`）；
  2. 实现层内的 `Native/` 子目录 —— 与某一厂商绑定的原生封装，如 `MotionControl/DeltaEtherCAT/Native/`、`MonitorCam/MecaVisionCam/Native/MVSDK.cs`；
  3. 与实现类同文件 —— SDK 调用很薄时，如 `LineLaserCam/IntelligentLaserCam/` 内的英莱封装。
- **场景 B 不建 Core** 的示例：`WeldParamControl` 直接以 `Abstractions/WeldAlgorithmBase.cs` 定义契约，公式与查找表写在 `Algorithms/` 实现类内，无 Core。

### 3.2 抽象层（Abstractions）

- 命名：目录名 `Abstractions/`（无第三方依赖的模块可用 `I<ModuleName>/` 命名，如 `IMotion/`、`IMonitorCam/`、`ILineLaser/`，见既有先例）。**同一模块内只用一种命名风格。**
- 内容：**对外功能 + 对外属性**的契约（接口 / 抽象基类）+ 公共枚举 + 事件参数 + 值对象。
- **硬性**：抽象层**零第三方依赖**——不得 `using` 厂商 SDK、不得 `DllImport`、不得出现厂商类型名。
- 新增能力优先加在抽象层，并用 `public virtual` 给默认实现，派生类可暂不实现（ADR-036 先例：`LineLaserCameraBase` 的 7 个外设虚契约）。
- 枚举/事件遵循 [[decisions/ADR-017-EnumDeduplication]]，一个语义只定义一份。

### 3.3 实现层（Implementations）

- **所有需要使用的功能都必须继承抽象类并实现**——这是本范式的核心约束；不允许出现「绕过抽象、直接 new 出来的工具类」。
- 一个实现类 = 一个具体后端（厂商实现 / 虚拟实现 / 不同算法）。多实现并存时，**厂商专属类型名只允许出现在实现层内**。
- **实现层只做回调触发**：取数、抛事件即返回；业务判断、状态语义、配置持久化一律不在实现层（ADR-035/ADR-037 准则，把实现类从 1746 行压到 1324 行的关键）。
- 实现类**非单例**，由 Manager 在构造时创建并持有（ADR-041 裁定）。

### 3.4 Manager

**Manager 是模块的唯一对外访问口**，四项职责缺一不可：

| # | 职责 | 说明 |
|---|---|---|
| 1 | **管理所有功能类对象** | 构造时 `new` 出全部实现类并持有；实例的唯一持有者就是 Manager，**实现层不对外暴露实例** |
| 2 | **管理数据** | 结果缓存、当前值快照、运行输出；对外以只读属性 / 版本号轮询暴露 |
| 3 | **持久化配置** | 持有配置对象，负责读写落盘（INI / XML / 数据库，遵循 [[decisions/ADR-005-ConfigLayout]]） |
| 4 | **对外唯一访问口** | 外部（UI / 流程 / 其它模块）只允许 `Manager.Instance` 或注入的 Manager 引用；**禁止绕过 Manager 直取实现** |

- 单例形态：Lazy 单例（`MonitorCamManager` / `AlgorithmManager`）或普通单例（`MontionManager` / `LineLaserManager` / `WeldParamManager`），**同一模块内统一**。
- Manager 只做**调度与转发**，不放流程编排（流程归 `MainDeviceControl/DeviceWorkflow/`，见 [[standards/WorkflowResponsibilityBoundary]]）。

---

## 四、依赖方向（铁律）

```
            外部（UI / 流程 / 其它模块）
                      │  只认 Manager
                      ▼
                   Manager ──────────┐
                      │              │ 管理数据 / 持久化配置
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   抽象层 A 契约   抽象层 B 契约   抽象层 C 契约     ← 零第三方依赖
        ▲             ▲             ▲
        │             │             │
   实现类 A1/A2   实现类 B1      实现类 C1/C2      ← 只允许出现厂商类型
        │
        ▼
      Core（功能封装核心）→ 第三方 SDK / 自研算法结构
```

**单向依赖，禁止反向**：

- 抽象层 **不得**依赖实现层、Manager、Core；
- 实现层 **不得**依赖 Manager（由 Manager 注入配置/回调，实现层不认识 Manager）；
- Core **只被**实现层调用，**不得**反向依赖实现层或 Manager；
- Manager **不得**被实现层引用，**不得**把实现类实例传出模块。

---

## 五、硬规则（H1~H9）

| # | 规则 | 违反后果 |
|---|---|---|
| **H1** | 场景 A（第三方库）必须有 Core；场景 B 视「是否有自成一体的算法结构」按需建 | 第三方调用散落各处，无法换厂商 |
| **H2** | 抽象层零第三方依赖（无 `using` 厂商 SDK、无 `DllImport`、无厂商类型名） | 换厂商要动抽象层，抽象失效 |
| **H3** | 所有功能实现类必须继承抽象类/接口并实现，禁止平行工具类绕过抽象 | 多套并存、无法统一调度 |
| **H4** | 一个厂商实现只有一个实现类，同一模块内不保留平行双实现（旧实现整删，不并存） | 双数据源、依赖残留（ADR-037 裁定先例） |
| **H5** | Manager 是实现类实例的**唯一持有者**，实现层不对外暴露实例 | 业务层 `as` 转型绑定单一厂商（ADR-036 先例） |
| **H6** | 外部只允许经 Manager 访问；禁止 `XxxAlgorithm.Instance` 式直取实现 | 入口分散、契约形同虚设 |
| **H7** | 配置持久化只由 Manager 负责，实现层不落盘 | 配置源分散、切换 Job 不生效 |
| **H8** | Manager 内不放流程编排；实现层不做业务状态判断 | 与流程层职责重叠（ADR-023/ADR-041） |
| **H9** | 实现层**只计算**：不得直接调用记录/持久化模块（`RunRecordManager` / `System.IO` / `File.` / `StreamWriter` / `XmlSerializer`）；需留痕只**触发事件**，由记录模块订阅后**异步**落盘 | 计算路径被落盘拖慢甚至阻塞；模块依赖反向缠绕（ADR-043） |

---

## 六、项目内已落地实例

| 模块 | 场景 | Core | 抽象层 | 实现层 | Manager | 决策 |
|---|---|---|---|---|---|---|
| [[modules/EmguALG]] | A（EmguCV）+ 自研算子 | `Core/`（`AlgorithmBase` / `PreprocessConfig` / 算子 `ImageAlgorithm.cs`） | `Abstractions/`（`IAlgorithm` / `IConfigurableAlgorithm` / `IResultStore`） | `RealtimeMonitor/WireFeedDistance/` · `RealtimeMonitor/WeldQuality/` · `LineLaserContour/` | `Manager/AlgorithmManager`（+ `AlgorithmResultStore`） | ADR-038 / 039 |
| [[modules/MonitorCam]] | A（MecaVision MVSDK） | `MecaVisionCam/Native/MVSDK.cs` | `IMonitorCam/`（`IMonitorCamApi` + 枚举 + 事件参数） | `MecaVisionCam/MecaVisionCam.cs` | `MonitorCamManager.cs` | ADR-037 |
| [[modules/LineLaserCam]] | A（英莱 SDK） | 实现类内薄封装 | `ILineLaser/LineLaserCameraBase.cs` | `IntelligentLaserCam/` · `VirtualCam/` | `LineLaserManager.cs` | ADR-034 / 035 / 036 |
| [[modules/MotionControl]] | A（台达 EtherCAT） | `DeltaEtherCAT/Native/` | `IMotion/`（`MontionControl` / `MontionAxis` / `MontionIO` / `IPVTMotion`…） | `DeltaEtherCAT/`（`Delta*` 系列） | `MontionManager.cs`（+ 三张注册表） | ADR-032 / 033 |
| [[modules/WeldParamControl]] | **B（纯自研）** | ⛔ **无 Core**（公式与查找表写在实现类内） | `Abstractions/WeldAlgorithmBase.cs` | `Algorithms/`（`WeldParamLookupAlgorithm` / `WeldParamAdjustmentAlgorithm` / `SeamTrackingAlgorithm`） | `WeldParamManager.cs` | ADR-041 |

> **对照读法**：`WeldParamControl` 是唯一的**场景 B** 实例——它证明「纯自研功能可以不要 Core」，也证明抽象层 + 实现层 + Manager 三件套在自研场景同样成立。

---

## 七、新增 / 改造模块检查清单

- [ ] 判定场景：是否基于第三方库？是 → 落地 Core；否 → 是否需要独立算法结构？需要才建 Core。
- [ ] 目录命名统一：抽象层目录名（`Abstractions/` 或 `I<ModuleName>/`）在模块内只用一种风格。
- [ ] 抽象层无第三方依赖（Grep `using <厂商命名空间>` / `DllImport` 结果为空）。
- [ ] 每个实现类都继承抽象契约；无平行工具类绕过抽象。
- [ ] 厂商专属类型名只出现在实现层与 Core。
- [ ] Manager 持有全部实现类实例；实现层无对外暴露实例的成员。
- [ ] 全库 Grep `\.Instance`：无绕过 Manager 直取实现的写法。
- [ ] 配置落盘只在 Manager；实现层无 `File.WriteAllText` / INI 写入。
- [ ] 配置类**实例**只由 Manager 持有：全库 Grep `new <ConfigType>(`，命中必须只在 Manager 内部（外部 `new` 或往 Manager 回灌实例 = 越权）。
- [ ] 配置读写无参：Manager 对外只提供 `Load<X>Config()` / `Save<X>Config()`，不暴露「接收配置实例」的重载。
- [ ] Manager 内无流程编排；实现层无业务状态判断。
- [ ] **实现层无记录/持久化副作用**：Grep 实现类（剥注释后）`RunRecordManager` / `System.IO` / `File.` / `StreamWriter` / `XmlSerializer`，命中即为越界；留痕改触发事件。
- [ ] **记录请求事件由 Manager 透传，订阅方异步落盘**：事件载荷不得携带记录侧状态（如帧索引）；订阅方只入队（O(1)），禁止在计算路径上同步落盘（H9 / ADR-043）。
- [ ] 若删除旧实现：确认 0 消费方（≥2 次不同 pattern 的 Grep 交叉验证）后再删，不留平行实现。

---

## 八、高频违规样例

| 违规 | 反例 | 正例 |
|---|---|---|
| 工作流直接持有厂商实例 | `private IntelligentLaserCam _cam;` + `Active as IntelligentLaserCam` | `LineLaserManager.Instance.IntelligentLaser` |
| 实现层自建实例 | 实现类内 `new` 并对外暴露单例 | 实例注册进 Manager，由 Manager 持有 |
| Core 反向依赖业务 | `ImageAlgorithm` 内直接读配置、写日志事件 | 算子纯函数，业务语义在领域算法内 |
| Manager 变成上帝类 | Manager 内做流程推进、状态机、事件风暴 | 流程归 Workflow，Manager 只调度与转发 |
| 抽象层混入厂商类型 | `IAlgorithm` 签名出现 `Emgu.CV.Mat` 之外的厂商句柄 | 抽象层用中性类型，厂商句柄封在实现层 |
| 场景 B 硬造 Core | 纯自研的几张表 + 几个公式也拆出 `Core/` | 直接写进 `Algorithms/` 实现类 |
| **配置实例外流 / 外部回灌** | 工作流 `new SeamGuideConfig()` 自持一份，再 `Manager.LoadSeamGuideConfig(workflow.SeamGuide)` 反向 push；运控直读 `workflow.SeamGuide` —— 同一配置出现**两个活实例**，靠 push 同步 | 唯一实例由 Manager 持有（含 `XdocumentReaderWriter`）；对外只暴露 `Manager.AlgorithmsConfig` **只读引用** + **无参** `LoadAlgorithmsConfig()` / `SaveAlgorithmsConfig()`（`WeldAlgorithmsConfig` 两节合一，ADR-044） |
| **配置持久化点留在配置类**（上一条的根因） | `Config` 类自带 `LoadConfig(XdocumentReaderWriter)` / `SaveConfig(reader)`，于是「谁拿到 reader 谁就顺势接管配置所有权」——reader 属工作流 `Config`，配置就被工作流收走 | 配置类只负责「把自己序列化成给定 reader」；**reader 的创建与持有归 Manager**，Load/Save 由 Manager 无参发起 |
| **实现层直接落盘（记录越界）** | 算法内 `RunRecordManager.Instance.RecordProcessFrame(...)` / `RecordAdjustment(...)` / `AbortRecording()`，并 `using AdaWeldSystem.ProductFileManager`；落盘发生在计算线程的同步调用栈上，记录一慢就拖慢控制；算法还被追着感知帧索引等**记录侧状态** | 算法**只发事件**（`FrameRecordRequested` 等），由 Manager 透传、记录模块订阅后**异步**入队落盘；载荷只含过程快照，不含帧索引（ADR-043） |
| **计算路径上同步落盘** | 订阅方接到事件后**就地**写文件/写库再返回，事件回调直接阻塞计算线程 | 订阅方只做入队（O(1)），后台线程负责真正的落盘——「保存可能耗时，但不能影响功能的实现」 |
| **实现层运行参数硬编码** | 算法构造函数写死 `MaxConsecutiveFailures = 5; IsCountType = true; CountNum = 5;`，且 Manager 内再存一份同名属性（**配置双份**） | 外提为 `WeldAlgorithmsConfig`（两节合一，ADR-044），实例与持久化归 Manager，算法经 `Config` 只读消费（ADR-043 / ADR-044） |

---

## 九、与其它标准的关系

| 标准 | 分工 |
|---|---|
| [[standards/WorkflowResponsibilityBoundary]] | 管**流程层 ↔ 子设备对象**的权责；本页管**模块内部**的层与入口。二者正交，改造模块时都要看 |
| [[standards/CodeSimplification]] | 管代码书写与精简；本页管结构摆放 |
| [[standards/UiStateSimplification]] | 管 UI 状态真相源；本页的 Manager 是 UI 取数的唯一来源 |
| [[architecture/DeviceControlArchitecture]] | 管流程与状态机；本页是它下挂的模块组织约定 |

---

## 相关

- [[decisions/ADR-042-ModuleOrganizationPatternStandard]] —— 本标准的沉淀决策
- [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] —— 场景 B 先例
- [[decisions/ADR-038-EmguALGThreeLayer]] · [[decisions/ADR-039-MonitorCamBoundaryAndEmguALGRefinement]] —— 算法模块三层/五层
- [[decisions/ADR-037-MecaVisionMonitorCamera]] —— 监控相机三层重构
- [[decisions/ADR-036-LineLaserManagerSingleEntry]] · [[decisions/ADR-034-LineLaserThreeLayerRefactor]] · [[decisions/ADR-035-LineLaserResponsibilitySplit]] —— 线激光
- [[decisions/ADR-032-MotionControllerDeltaReplacement]] · [[decisions/ADR-033-ZMotionRemovalAndDeltaLanding]] —— 运控
- [[decisions/ADR-017-EnumDeduplication]] —— 抽象层枚举去重
- [[decisions/ADR-005-ConfigLayout]] —— 配置落盘分层
- [[modules/EmguALG]] · [[modules/MonitorCam]] · [[modules/LineLaserCam]] · [[modules/MotionControl]] · [[modules/WeldParamControl]] —— 落地实例
