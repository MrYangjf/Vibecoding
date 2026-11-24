---
title: ADR-006 模块组织范式沉淀（Core + 抽象层 + 实现层 + Manager 四件套）
date: 2026-09-14
updated: 2026-11-19
tags: [决策, 模块组织, 分层架构, 抽象层, 实现层, Manager, 第三方库封装, ConfigFileControl, 配置管理, ADR-006]
status: accepted
---

# ADR-006 模块组织范式沉淀（Core + 抽象层 + 实现层 + Manager 四件套）

## 状态

已采纳（2026-09-14）。

## 背景

项目在 2026-09 的一轮模块改造中，先后在四个模块独立收敛出了同一种结构，但**每次都是「就地决策」，没有一份跨模块的统一标准**：

| 模块 | 决策 | 结构 |
|---|---|---|
| `MotionControl` | [[decisions/ADR-027-MotionControllerDeltaReplacement]] / ADR-027（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） | `IMotion/` 抽象 + `DeltaEtherCAT/` 实现（含 `Native/`）+ `MontionManager` |
| `LineLaserCam` | [[decisions/ADR-024-LineLaserThreeLayerRefactor]] / ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） / ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） | `ILineLaser/` 抽象 + 英莱/虚拟实现 + `LineLaserManager`（唯一实例持有者） |
| `MonitorCam` | ADR-019（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） | `IMonitorCam/` 抽象 + `MecaVisionCam/` 实现 + `MonitorCamManager` |
| `EmguALG` | [[decisions/ADR-022-EmguALGThreeLayer]] / [[decisions/ADR-019-MonitorCamBoundaryAndEmguALGRefinement]] | `Abstractions/` + 领域算法实现 + `Core/` 算子 + `Manager/AlgorithmManager` |
| `WeldParamControl` | [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] | `Abstractions/WeldAlgorithmBase` + `Algorithms/` 实现 + `WeldParamManager`（**纯自研，无 Core**） |

五个模块结构同构，但「Core 是不是必需」「抽象层目录叫什么」「实现层要不要单例」在每个模块里各说各话。用户 2026-09-14 给出通用裁定，要求把范式固化为项目级标准，避免每新增一个模块都要重新讨论一遍结构。

## 决策

**D1 确立「四件套」范式**：一个功能族模块 = **Core（功能封装核心）+ 抽象层（对外功能与属性）+ 实现层（继承抽象并实现）+ Manager（管理全部实现类对象与数据、持久化配置、对外唯一访问口）**。

**D2 按「是否基于第三方库」分两种场景**：

| 组件 | 场景 A：基于第三方库 | 场景 B：非第三方库（纯自研） |
|---|---|---|
| Core | ✅ **必需** | ⚠️ **按需**——只有需要自成一体的算法结构时才建；原则上不需要，功能类自身的函数与算法直接写在实现类中 |
| 抽象层 | ✅ 必需 | ✅ 必需 |
| 实现层 | ✅ 必需（所有功能都必须继承抽象类实现） | ✅ 必需（同上） |
| Manager | ✅ 必需 | ✅ 必需 |

**D3 沉淀为标准页并路由**：新建 [[standards/ModuleOrganizationPattern]]，由 [[index/index]] 场景速查路由与 §四规范表收口；本 ADR 作为其决策锚点（做法同 [[decisions/ADR-007-CodeSimplificationStandard]]）。

**D4 依赖方向铁律**：抽象层零第三方依赖 → 实现层只被 Manager 装配、只允许出现厂商类型 → Core 只被实现层调用 → 外部只经 Manager 访问。四向单向，禁止反向。

**D5 Manager 四职责固定**：①管理所有功能类对象（唯一持有者）②管理数据 ③持久化配置 ④对外唯一访问口。**Manager 不放流程编排**（流程归 `MainDeviceControl/DeviceWorkflow/`，见 [[standards/WorkflowResponsibilityBoundary]]）。

## 后果

### 正面

- 新增 / 改造模块时不必再逐次讨论结构，直接按标准页第十节检查清单落地；
- 换厂商只动实现层，抽象层与 Manager 不动——这是本范式全部价值的落点；
- `WeldParamControl` 与 `EmguALG` 分别作为场景 A / 场景 B 的完整样本，标准有正反两侧可对照；
- 消除「平行工具类绕过抽象」「工作流持有厂商实例」「配置实现层落盘」三类高频违规（分别对应 H3 / H5 / H7）。

### 负面 / 遗留

- 既有的五个模块中，`MotionControl` 的抽象层目录名为 `IMotion/`、`MonitorCam` 为 `IMonitorCam/`，与标准页建议的 `Abstractions/` 不同名。**本轮不做目录改名**（改名成本与收益不匹配），标准页已明确「同一模块内只用一种命名风格」，两种命名均合规；
- `LineLaserCam` 的第三方封装不是独立 `Core/` 目录而是与实现类同文件，属标准页 §3.1 认可的第三种落地形态；若后续英莱 SDK 调用面扩大，可再评估独立成 `Native/`。

### 约束

- ⛔ 外部代码不得绕过 Manager 直取实现类（禁 `XxxAlgorithm.Instance` 式写法）；
- ⛔ 抽象层不得引入第三方依赖（无 `using` 厂商 SDK、无 `DllImport`、无厂商类型名）；
- ⛔ 同一模块内不保留平行双实现，旧实现整删（ADR-034 裁定先例）；
- ⛔ 不得在 Manager 内加入流程编排，不得在实现层做业务状态判断。

## 相关

- [[standards/ModuleOrganizationPattern]] —— 本标准页（含 H1~H11 硬规则与检查清单）
- [[standards/WorkflowResponsibilityBoundary]] —— 流程与子设备权责（与本页正交）
- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] —— 场景 B 先例
- [[decisions/ADR-022-EmguALGThreeLayer]] —— 场景 A 先例（Core 独立成目录）
- ADR-019（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） —— 换厂商只动实现层的实证
- ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） —— Manager 唯一持有者原则的实证
- [[decisions/ADR-007-CodeSimplificationStandard]] —— 「规范沉淀为标准页」的先例
- [[decisions/ADR-Index]] —— 编号总表

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 演进记录

### D2 · 新增 `ConfigFileControl` 模块（配置管理的四件套应用）

> 业主裁定（2026-11-19）：「新增一个文件夹 ConfigFileControl，按照抽象，实现，ConfigFileManager 来写。独立出来，不由 WeldParamManager 管理。」
> 配套裁定：**DB 类与 Records 类不变**；其余 Manager **不再管理配置文件，只应用参数**；全局配置文档与目录由 `ConfigFileManager` 统一管理。

**一、为什么需要这个模块**

改造前的现状（实测 32 个配置文件 / 10 个配置类）：

| 配置类 | 文件 | 归属 Manager | 路径管理方式 |
|---|---|---|---|
| `WeldAlgorithmsConfig` | XML + 4 INI | WeldParamManager | 类内常量 |
| `LineLaserConfig` | `LineLaserConfig.xml` | LineLaserManager | 类内常量 |
| `DeltaMotionConfig` | `DeltaMotionConfig.xml` | MontionManager | 类内常量 |
| `WeldHeadConfig` | `WeldHeadSlave.xml` | MontionManager | 类内常量 |
| `MonitorCamConfig` | `MonitorCamera.ini` | MonitorCamManager | 类内常量 |
| `CommunicationManager`（内嵌） | 8 XML + 1 INI | CommunicationManager | 构造内 `new` |
| `RenderConfig` / `SimulationConfig` | INI | 静态 / DeviceControlWork | 类内常量 |
| `TaLaCurveConfig` / `AlgorithmManager` | XML / INI | 各自 | 类内常量 |

⇒ **每个配置类自己管路径、自己 `new INIFile` / `new XdocumentReaderWriter`** —— 路径散落 11 个子目录，载体创建点散落全库（31 处），无人能一眼看全「哪些文件被谁写」。

**二、决策：四件套落到配置管理**

```
ConfigFileControl/                    命名空间 AdaWeldSystem.ConfigFileControl（ADR-005 严格对齐）
├── Abstractions/                     抽象层（零第三方依赖，ADR-006 H2）
│   ├── IConfigFileProvider.cs        载体契约（读/写/存在性/Reload/Save）
│   └── IConfigRegion.cs              区域契约（按 TabPage 分区读写）
└── Implementations/                  实现层
    ├── IniConfigFile.cs              INI 载体实现
    ├── XmlConfigFile.cs              XML 载体实现
    ├── ConfigFileManager.cs          Manager（唯一持有者 + 唯一对外口）
    └── WeldParamChangeLogger.cs      配置变更审计（由 WeldParamControl 迁入）
```

⛔ **不建 Core** —— 场景 B（纯自研），符合本 ADR D2「Core 按需」。

**三、职责收口**

| 项 | 改造前 | 改造后 |
|---|---|---|
| 配置路径 | 10 个配置类各自持有常量 | **全部由 `ConfigFileManager` 解析**（`Config\ConfigFileControl\<模块>\`） |
| 载体创建 | 31 处 `new INIFile` / `new XdocumentReaderWriter` 散落全库 | **只在 `ConfigFileManager` 内**（各 Manager 改为向它取） |
| Manager 职责 | 各 Manager 兼管配置（H7 违规面大） | 只有 `ConfigFileManager` 管配置；其余 Manager **只消费参数** |
| 改名 | `WeldAlgorithmsConfig` | **`WeldParamConfig`**（并扩展为全局配置类，内部按 TabPage 分区域） |
| 审计 | `WeldParamControl.WeldParamChangeLogger` | `ConfigFileControl.Implementations.WeldParamChangeLogger` |

**四、区域模型（`WeldParamConfig` 内部按 TabPage 分区）**

`ConfigRegion` = 区域名 + 节清单 + **键清单**（键清单以各区**实际保存的键**为准；读取键是保存键的超集，含只读忽略的旧键）。

| 区域（zone） | TabPage | 文件 | section | 键数 |
|---|---|---|---|---|
| `Preset` | 工艺·激光工艺设置 | `WeldParam.ini` | `PROCESS_CONTROL` | 12 |
| `Adapt` | 工艺·自适应工艺参数设置 | `WeldParam.ini` | `WELD_PARAM_ADJUST` | 2 |
| `Flow` | 系统·流程控制与测试 | `WeldParam.ini` | `PROCESS_CONTROL` + `SEAM_GUIDE` | 5 |
| `System` | 系统·轨迹跟踪参数设置 | `WeldParam.ini` + `WeldParam.xml` | `SEAM_GUIDE` + XML 几何/标定 | 19 |
| `Quick` | 工艺·激光工艺设置（Y 轴锁定） | `WeldParam.ini` | `PROCESS_CONTROL` | 1 |

**五、跨页覆盖的根治机制（关键）**

⚠️ 同 section 被两个 TabPage 共享（`PROCESS_CONTROL` 被 Preset 与 Flow 共用；`SEAM_GUIDE` 被 System 与 Flow 共用）⇒ **section 粒度不够，必须键级**。

区域保存三步：
```
① carrier.Reload()          ← 先从磁盘拿其它区域已保存的最新值
② 只写本区域涉及的键        ← 键级，不是段级
③ carrier.Save()            ← 落盘（未涉及的键此时是磁盘最新值）
```

> ⛔ 载体是**整文件重写**（`INIFile.SaveToFile` = `File.WriteAllText`；`SaveXdocument` 整篇重写）⇒ 不 Reload 就写，未涉及的 section 会取**内存旧值**把磁盘新值覆盖回去。**XML 侧同理**（其 `XDocument` 长期驻留内存）。

原型验证（副本目录，已跑通）：section 级隔离 ✓ / 键级隔离 ✓ / 同 section 被 3 个 TabPage 共享 ✓ / 交叉保存 ✓。

**六、旧配置：完全舍弃，不做迁移**

业主裁定：「这已经是重构了。迁移容易出现的问题在于新旧混乱。我需要你完全舍弃旧的……可以完全重新填入，你生成默认值就可以。」

⇒ **删除全部存量迁移代码**（`MigrateLegacyAlgorithmIni` 及其配套），新目录下的文件由 `ConfigSelfHeal` 按默认模板生成；旧目录文件保留在磁盘但代码不再读。
⇒ 连带删除：`LA_POSE2_MM` 旧键及其"一次性迁移"分支（业主指出我上轮漏删）；4 个零引用死配置；XML 死键 `Y_AXIS_MIN_MM`/`Y_AXIS_MAX_MM`；7 个失效路径常量；6 个孤儿配置文件（`IntelligentLaser.ini` / `CameraPresets.ini` / `CameraSelector.ini` / `JobIndex.ini` / `Job_001.ini` / `AlgorithmParams.ini` —— 全仓 0 读写方）。

**七、判据（可复用）**

- ⛔ **配置归 Manager 管，UI 分区不参与分割**：TabPage 是视图单元，Manager 是数据所有权单元；用视图单元切分数据所有权 ⇒ 所有权被切碎。
- ⛔ **整文件重写载体的根因是「写入粒度」不是「文件数」**：保存前 `Reload()` + 只写目标键 ⇒ 单文件即可跨页隔离。**先验证粒度方案，再考虑拆文件**。
- ⛔ **同一 section 被多个 TabPage 共享时，section 粒度不够** ⇒ 必须键级写入。
- ⛔ **迁移 ≠ 重构**：改语义可用一次性迁移；**换归属模型必须舍弃旧数据**，否则新旧两套读写器并存 ⇒ 混乱。
- ⛔ **补键模板必须写到独立临时载体**，不能污染正式载体（否则模板把默认值写进真实配置）。
- ⛔ **配置项清理要「物理删除」**：连同"一次性迁移"分支与日志一起删，不留"已弃用"的兼容路径。

**八、验证**

- 真编译 `errors=0 rc=0`；静态守卫 PASS；8 闸门全过
- **44 项自检**全通过（模块骨架 / Manager 职责 / 改名 / 区域模型 / 10 类收归 / 清理 / 不动的部分）
- **路径一致性验证**全通过（根目录常量 + 10 个模块常量 + 目标目录结构）
- **区域键级写入隔离验证**10 断言全通过

### D2 补充 · 收归后全量核查结论（2026-11-19）

业主在配置收归后追加三问核查，结果如下（均已落地修复）：

| 核查项 | 结论 |
|---|---|
| ① 各原 Manager 是否还重复持有配置 / 参数修改记录 | **已清零**：LineLaser / MonitorCam / Montion / Algorithm / Communication / WeldParam 六个 Manager 的**正式载体数全为 0**（`CommunicationManager` 的 8 个 Xdoc 成员来自 `ConfigFileManager`；`WeldParamManager` 残留 1 INI + 1 Xdoc 均为**补键模板的临时载体**）。`ProductFileRecordManager` 保留 2 处（**Records 按业主裁定不变**）。参数修改记录 `WeldParamChangeLogger` 仅 `WeldParamManager` 一处调用 4 次（已迁 `ConfigFileControl` 模块）。 |
| ② 迁移是否完全、是否缺配置项 | **已一致**：`WeldParamConfig` 五个区域的「实际读写键」与「区域声明键清单」**双向 diff 全部一致**（Adapt 4→2 / Flow 5 / Preset 12 / Quick 1 / System 19）。57 个 public 属性中 6 个未落盘：`Name` 属 `ConfigRegion`、其余 5 个是 PVT 回退路径（明确不持久化）。 |
| ③ 涉及文件的代码精简检测 | **死代码 0 / 空壳方法 0**；注释率整体约 20%（新建的两个抽象接口 46~55% 属接口文档惯例）。 |

**⭐ 本轮修复的 8 项**（其中第 1~2 项是**真实缺口**）：

| # | 修复项 | 说明 |
|---|---|---|
| **F1** | 删 `ConfigRelativeDir`（基类 + 5 个 override） | **死属性**：改造后无人读 |
| **F2** | `DeviceWorkflowBase.Config` 改按子类 `ConfigModule` 取载体 | **真实缺口** —— 5 个 workflow 的 override 仍指向旧目录，使基类新默认值被 override 掉 ⇒ **workflow 配置根本没走 `ConfigFileManager`**，旧目录文件成孤儿 |
| F3 | 删 `InstructionTorqueConfirmSamples` | 零引用常量 |
| F4 | 删 `LoadParamOutOnForm` + 3 处调用 | 空壳方法（删 3 个控件后残留） |
| F5 | 删 Adapt 区读 `IS_COUNT_TYPE`/`COUNT_NUM` | 已废配置项的「只读忽略」分支（业主裁定完全舍弃旧配置 ⇒ 纯噪音） |
| F6 | 修 `WeldParamConfig` 类注释的旧路径 | 注释指向已不用的 `Config\WeldParamControl\Algorithm_*` |
| F7 | `ConfigPathMigrator` 补 5 条 workflow 配置路径 | 收归后旧目录同名文件需搬到新模块目录 |
| F8 | 删 7 个孤儿配置文件 + 3 个空目录 | `JobIndex.ini` / `Job_001.ini` / `IntelligentLaserJobParams.ilini` / `CameraPresets.ini` / `CameraSelector.ini` / `AlgorithmParams.ini` / `IntelligentLaser.ini`（全仓零引用）；`Jobs/` / `LineLaser/Camera_INI/` / `IntelligentLaserCam/` |

**⭐ 新增判据（见 [[lessons/RefactorPostChecklist]]）**

- ⛔ **子类 override 的基类属性是收归类改造的最高频漏点**：基类改了默认值但子类还 override 旧值 ⇒ 改造静默失效；且该属性本身零引用，**静态零引用扫描查不出**（override 本身算一次引用）⇒ 必须逐个 Manager 核对载体归属。
- ⛔ **「只读忽略旧键」的读取分支会让配置项计数与区域键清单对不上**，破坏「逐项可核」的基础 ⇒ 已删配置项的这类分支要一并物理删除。
- ⛔ **孤儿文件不会自动消失**：判定须用「全仓引用（**排除路径迁移表**）+ 扩展名白名单」双口径 —— 扩展名可能是 `.ilini` 这类非 xml/ini。

### 通讯配置按 RSI 模式分层（2026-11-19 核定）

业主现状：**只有 1 台 KUKA 机器人的 RSI 通道；无 PLC；Modbus（对英莱）暂未启用**。

| 文件 | 角色 | 运行时消费方 | 处置 |
|---|---|---|---|
| `RobotServer.xml` | **RSI 核心**（IP/PORT/HOST_IP/HOST_PORT/SENTYPE/CYCLE + RSI 格式节） | `CommunicationManager` 初始化 + `EnsureRsiFormatSections` | **必需** |
| `WeldControlConfig.xml` / `WeldControlSendFormat.xml` | **机器人端部署件**（本机生成 → 拷到机器人 `SensorInterface\`） | 本机生成不读回 | 保留 |
| `Server/Client/Send/Recive.xml` | **仅 UI 文件编辑器查看**（`FileEditorForm`） | 无通讯链路消费 | 保留（RSI 格式模板） |
| `RobotClient.xml` | **零消费方**（EKI 通道未用） | — | 建议随未启用通道停用 |
| `PLC.xml` | 零消费方（`InitializePlcComm` 需 IP+Rack+Slot 非空 ⇒ 无 PLC 时不启用） | — | 同上 |
| `Modbus.xml` | 零消费方（`InitializeModbusComm` 需 IP+PORT 非空 ⇒ 未启用） | — | 同上 |

⇒ **不合并 8 个为一个**：它们语义层次不同（本机通讯参数 / UI 格式模板 / 机器人端部署件），且 RSI 模式下真正必需的只有 `RobotServer.xml` 一个；合并会让「机器人端部署件」与「本机参数」混在一文件里，反而破坏部署边界。

## 相关页面

- [[decisions/ADR-Index]]
