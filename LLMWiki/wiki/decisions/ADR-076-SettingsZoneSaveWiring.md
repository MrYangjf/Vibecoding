---
title: ADR-076 三界面参数读存与分区落盘接线裁定（分区归属随 UI 迁移 · 赋值先于落盘 · 禁跨区副作用）
date: 2026-10-23
updated: 2026-11-19
tags: [ADR, 配置架构, 分区落盘, AlgorithmsZone, WeldAlgorithmsConfig, SystemControlPage, ProcessControlPage, FilebackupPage, 读存按钮, 接线完整性, 振镜图形, 未读到即无图形]
status: accepted
---

# ADR-076：三界面参数读存与分区落盘接线裁定

> 背景：2026-10-23 对**系统设置页 / 工艺设置页 / 通讯调试页**做参数与按钮一致性盘查（读/改/存按钮响应 + 后端配置），
> 实测出**一族「改了不生效 / 保存了没落盘 / 落到了别人的区」缺陷**。本 ADR 裁定统一读存语义与分区落盘纪律。

## 背景：五类实测缺陷

| # | 缺陷 | 现象 | 根因 |
|---|---|---|---|
| ① | **⑤工艺输出三项不落盘** | 工艺设置页「保存焊参调整」提示已保存，重启后手动宽度/光斑系数/输出频率回旧值 | 三项按 ADR-068 归 **③Adapt 区**，但代码**在 Adapt 落盘之后**才赋值，且随后调的是 `SaveAlgorithmsZone(System)`（System 区不含这三个键）⇒ 双重错误 |
| ② | **焊缝地图点数上限不落盘** | 系统设置页「保存参数」提示已保存，`MaxMapPoints` 重启回旧值 | 该项 XML 归属 **④Preset 区**（`SEAM_GUIDE/MAX_MAP_POINTS`），但「保存参数」只落 **①System 区** |
| ③ | **跨页副作用** | 在系统设置页点过「修改参数」（只进内存）后，到工艺设置页点「保存焊参调整」，系统设置页的未保存参数被一并写盘 | 「保存焊参调整」末尾调 `SaveAlgorithmsZone(System)`，而它并不写 System 区的任何配置项 |
| ④ | **读取按钮名不副实** | 「读取参数」取不到文件最新值 | 两页的「读取参数」只读**内存**（`WeldHeadConfig` / `DeltaAxisConfig` / `WireFeedConfig`），从不调用 `MontionManager.LoadWeldHeadConfig()` 重载文件 |
| ⑤ | **全量保存污染** | 选一次振镜图形会连带重写 XML 与全部 INI 段 | `GalvoPattern` 属 ④Preset 区，却用**全量** `SaveAlgorithmsConfig()` 落盘 |

另有重复接线：`radioQuickY` 三处指令落盘、`SetGalvoPattern` / `selGalvoPattern_SelectedIndexChanged` 两处图形落盘、
`btnCorAutoParam` / `BtnSaveAutoParam` 两处写同一批 6 个配置项 —— 均已收口为单一入口。

## 决策

### 一、配置项的落盘分区随 UI 落点迁移（分区归属不得与 UI 落点脱节）

`MaxMapPoints` 的 UI 落点已于 2026-10-23 迁入**系统设置页·线激光点过滤区**，故其 XML 归属由 **④Preset 改为 ①System**。

- ⛔ **XML 键路径不变**（`SEAM_GUIDE/MAX_MAP_POINTS`）⇒ 存量配置文件继续可读，无需迁移脚本。
- ⛔ **同区唯一写口**：`SaveZoneXmlPreset` 不得再写该键（两区写同一键 ⇒ 归属漂移，ADR-068 的「UI 面板 ↔ 配置代码块一一对应」失效）。
- 判据：配置项的落盘分区 = 其**唯一 UI 落点所在页**对应的分区；UI 迁移时必须同步迁移分区归属。

### 二、赋值必须先于落盘（读/改/存三段式纪律）

任何「保存」按钮的顺序恒为：**UI → 内存（Apply）→ 落盘（Save）**，且**落盘必须使用该项所属分区的接口**。

- ⛔ 禁「先落盘、后赋值」（赋值晚于落盘 ⇒ 该项本次不落盘）。
- ⛔ 禁用**非所属分区**的落盘接口「顺带」落盘（跨页副作用）。
- ⛔ 禁用**全量** `SaveAlgorithmsConfig()` 落**单分区**的配置项（全量会重写 XML + 全部 INI 段，污染其它区）。

### 三、读取按钮必须真正读文件

「读取参数」= 文件 → UI。涉及文件承载的配置对象，必须先调用其**文件重载入口**再回填：

| 配置对象 | 文件重载入口 | 状态 |
|---|---|---|
| `WeldAlgorithmsConfig` | `WeldParamManager.Instance.LoadAlgorithmsConfig()` | ⚠️ **2026-11-04 修正**：该入口曾只读内存快照（读写器构造期缓存），已补 `Reload()` 前置刷新，现为真正的文件重载入口 |
| `WeldHeadConfig`（振镜宽/长/频/阈值/量纲） | `MontionManager.Instance.LoadWeldHeadConfig()` | ✅ **本轮接线**（此前 0 调用方） |
| `LineLaserConfig`（三处等待超时） | `LineLaserManager.Instance.LoadConfig()` | ✓ 已有 |

### 四、同一批配置项只允许一条落盘入口

- ⑤工艺输出三项 + 焊参调整三项 ⇒ 统一走 `ApplyAdaptUiToMemory()`（UI→内存，不落盘），「修改参数」与「保存焊参调整」共用。
- 振镜图形 ⇒ 统一走 `SaveGalvoPattern()`，落 ④Preset 区。
- Y 指令（`LockYCalib`）⇒ 落 ②Quick 区（禁全量保存）。
- 激光头保存 ⇒ 只落 `WeldHeadSlave.xml` + 运控轴配置，**不落 ④Preset 区**（该区归工艺设置页）。

### 五、数值解析口径统一

页面级参数解析统一为 **InvariantCulture 优先 → 当前文化回落 → 失败保留原值**；
两页的 `ParseCalibDouble` / `ParseInt` 不得各写一份且口径不同（此前两页一份、且同页另有 `TryReadDouble`/`TryReadInt` 两套）。

## 必要说明（有意保留）

| 项 | 说明 |
|---|---|
| ⑤工艺输出双入口（`txtManualWidth` 振镜卡 / `txtParamManualWidth` ⑤区） | 保留（wiki 已记载「双入口同源」）；两入口统一走 `ManualSeamWidthMm` 同一配置项，落盘分区同为 ③Adapt |
| 振镜宽/长/频与生产链路争用同一协议字段 | ⛔ **待业主裁决**（工作流每拍写 `galvo.Width/Length = amplitude`、`Frequency = 查表频率` ⇒ 三项运行期被覆盖）。本轮只报不改 |
| 振镜中心 X/Y 与运行期中心补偿单写口争用 | ⛔ 待裁决（ADR-059「中心补偿单写口」纪律） |

## 后果

- **正面**：⑤工艺输出与焊缝地图点数上限**真正落盘**；「保存」不再越区污染；「读取」真正读文件；三界面读存语义统一。
- **负面**：`MaxMapPoints` 的分区归属变更需同步 `api/*` 页与 `WeldAlgorithmsConfig` 注释（已同批改）。
- **中性**：存量 XML/INI 键路径与键值均未变，现场配置无需迁移。

## 验证

- **判据覆盖 49 项**（配置四点闭环 5 项 + 分区落盘接线 13 项 + 读取接线 4 项 + 解析口径 4 项 + 接线完整性 2 项 + using/作用域 2 项 + C# 7.3/保留字 5 项 + Dispose 1 项 + csproj 路径 1 项 + Designer 控件闭环 3 项 + 行尾同质 4 项 + 旧行为注入 5 组）。
- **旧行为注入**：注入 5 组旧行为（Adapt→System / Preset→全量 / Quick→全量 / 删 MAX_MAP_POINTS 写 / 删 LoadWeldHeadConfig），对应判据**全部 FAIL**（判据有区分度）。
- ⚠️ 沙箱无 C# 编译器：静态校验 ≠ 编译通过，**真编译待 Visual Studio**。

## 背景

（待补：本决策要解决什么问题）

## 演进记录

- （待补：考虑过什么、为什么放弃）

### 2026-11-04 · 决策 D1 · LoadAlgorithmsConfig 前置 Reload 磁盘
- **变更**：LoadAlgorithmsConfig 前置 Reload 磁盘
- **理由**：读写器仅构造期读盘，读取按钮与 .awcfg 导入回读校验长期读内存快照
- **影响**：读取与导入回读真正落盘生效；XdocumentReaderWriter 新增 Reload()

### 2026-11-04 · 决策 D2 · 分区首载与整型参数写入必须「可见且幂等」
- **变更**：① 组合加载入口（`LoadAlgoConfigOnForm`）补齐 TA 分区加载器，并加一次性补载守卫（构造 / 页面显示 / 初始化完成三处幂等）；
  ② 「修改」类按钮写入后回填内存真实值并给可见回执；写入前先定位目标对象，定位失败即失败返回；
  ③ 驱动器 U16 参数按整数范围校验（`TryReadInt` 1~65535），越界或小数弹窗提示，不再 `(uint)` 静默截断。
- **理由**：分区加载入口漏一组 ⇒ 该区首开空白；目标对象缺失静默跳过 ⇒ 界面显示成功但值未写入；小数强转 ⇒ 配置永久为 0。
- **影响**：工艺设置 TA 区进入即显示；系统设置页「扭矩爬升速率」修改后界面与内存一致、失败必可见（**2026-11-05 该入口已迁至 TA 轴「参数」弹窗，ADR-084；三点闭环语义不变**）；本 ADR 的「读取=文件→UI / 修改=UI→内存 / 保存=UI→内存→文件」三点闭环不变。

### 2026-11-18 · 决策 D3 · 振镜图形「未读到 = 无图形」三层语义（配置 0 / UI 不预选 / 下发兜底直线）

- **变更**：① 配置层 `WeldAlgorithmsConfig.GalvoPattern` 初值由 `3`（直线）改为 **`0` = 未设置（无图形）**，并把 INI 读取处的「越界强制回退 3」改为「越界归 0 + 记 Warning」（⛔ 不再静默兜底为直线）；
  ② UI 层（工艺设置页 GA 指令区图形 Radio）图形回填改为**以配置实际值为准**：读到有效值才选中对应 Radio，读不到（0 / 越界 / 配置对象为空）⇒ **不预选任何 Radio**，由操作员自行选择后落盘；
  ③ 设备下发层新增 `LaserWeldHeadWorkflow.ResolveGalvoPattern(int)`：`0` / 越界 ⇒ **逻辑零位的直线**（协议枚举 `WsgGalvoPattern` 为 1..4，**无 0**，⛔ 禁把 0 或越界值写入 0x7010 子索引 1）；
  ④ 删 UI 层冗余：`_syncingLaRadios`（与 `_loadingGalvoUi` 同生命周期完全覆盖）、字段 `_galvoPatternSelected`（写后无读者，降级为读取即用）；`RadioToGalvoPattern` / `GalvoPatternToRadio` 的 `default` 由**静默兜底直线**改为**返回 null + 记 Warning**。
- **理由**：原实现有三处「静默兜底为直线」——配置初值 3、INI 越界回退 3、UI 映射 `default` 落 Line。业主裁定「**初始使用读取，未读到默认没有图形，图形始终以实际为准**」：读到就用读到的，读不到就没有图形，⛔ 不用代码默认值冒充"实际值"。原 UI 字段 `_galvoPatternSelected` 则是图形 Select 时代遗留的**双向同步缓存**，Select 删除后其写点已无读者（ADR-076 §四「同一批配置项只允许一条落盘入口」在 UI 侧的自然收束）。
- **影响**：① **存量 INI 无 `GALVO_PATTERN` 键时**，图形由「直线」变为「未设置」⇒ 首次上机 GA 指令区**无预选项**，操作员须手动选一次并落盘（符合业主裁定，但属现场行为变化，需在交接说明中点出）；② 存量 INI **有**该键（1..4）时行为不变；③ 逻辑零位语义不变（`GalvoParams.CreateLogicalHome()` 仍为直线，注释「勿改构造默认值：协议默认 ≠ 逻辑零位」不受影响）；④ 记录层 `GalvoPatternId` 无生产写入方（只读 + 默认 0），与 0 语义天然一致，不外溢。

### 2026-11-18 · 决策 D4 · 振镜图形语义修正：以「振镜是否启用」为前提（未启用=无图形；已启用=必有图形）

- **变更**（**修正同日 D3**：D3 把「未读到图形」处理为全局无图形，D4 补上前置条件 —— 图形语义以**振镜是否启用**为前提）：
  ① **UI 层**（工艺设置页 GA 指令区图形 Radio）按振镜启用态分支：振镜**未启用** ⇒ **没有图形**（清空整组选中 + 整组置灰禁用）；振镜**已启用** ⇒ **必须有一个图形**（有设置则用设置；无设置（0）⇒ 落回默认 `Line` 并**落盘**，配置与显示一致）；
  ② **启用态来源统一**：`LaserWeldHeadWorkflow.IsGalvoWeaveEnabled()`（实时读 `cfg.EnableGalvoWeave`），工艺页与 workflow 共用同一入口（跨页同源，非各自副本）；
  ③ **删过期快照字段 `_galvoWeaveEnabled`**（原 `LoadConfig()` 期取值，运行期改开关不刷新）⇒ `ApplyGalvoAmplitude` 的摆幅门控改为实时读配置，与 `WeldParamControlWorkflow.GetAmplitudeMm` **同真相源、同实时性**；
  ④ **置灰与清选中的执行顺序**：清选中在 `RefreshActionStates()`（置灰）**之前**执行，避免对 Disabled 控件改 `Checked`；清选中触发的 `CheckedChanged` 由 `_loadingGalvoUi` 抑制标志拦下（⛔ 不误落盘、不误记日志）。
- **理由**：业主补充裁定完整链路 ——「**没有开启振镜自动运行时是没有图形的；当配置启用了振镜功能，那么必须有一个图形，如果有设置就用设置，如果没有就落回默认 Line**」。物理依据：`EnableGalvoWeave=false` ⇒ `CalcGalvoAmplitude` 返 0 ⇒ 摆幅 0 且 `GalvoEnable=false` ⇒ **设备不摆动，图形值无物理意义**。故「未启用 = 无图形」不是 UI 约定，而是设备真实状态；「已启用 = 必有图形」则是使用前提（图形是振镜摆动的形状载体，缺失则摆动无形状）。
- **影响**：① 振镜未启用时 GA 图形 Radio **整组置灰**（操作员须先在系统设置页启用振镜才能改图形）；② 振镜启用且配置无图形时，页面加载会**自动落盘 Line** 并记一条 Info（配置与显示一致，业主裁定为「兜底即落盘」）；③ 跨页联动路径已闭合 —— 系统设置页 `swEnableGalvoWeaveQuick` 切换 → 落 ②Quick 区 → 切回工艺设置页触发 `ParamAutoPage_Shown` → `LoadAlgoConfigOnForm` → `LoadGalvoActionUi` → 图形选态与置灰自动收敛；④ 删快照字段后，**运行期改开关立即生效**（原先须重启/重连才生效）；⑤ D3 的其余结论不变（配置层 `0`=未设置、INI 越界归 0 + Warning、协议层 `ResolveGalvoPattern` 兜底直线）。

### 2026-11-18 · 决策 D5 · ③自适应区瘦身（删三项输出参数）+ 分区归属收缩

> 业主 2026-11-18 裁定：自适应参数页「只保留对报警相关的」，三项输出参数判定为无作用并删除。

| 被删配置项 | 原分区 / INI 键 | 业主理由 | 替代来源 |
|---|---|---|---|
| `SpotWidthGain`（光斑宽度系数） | ③Adapt / `SPOT_WIDTH_GAIN` | 「暂时觉得不需要，即使需要也应该和调节灵敏度一个地方保存」 | ⛔ 彻底删（含查表算法 3 处乘算）⇒ 查表光斑宽 = 焊缝宽（乘 1.0 恒等，**行为等价**） |
| `ManualSeamWidthMm`（手动输出宽度） | ③Adapt / `MANUAL_SEAM_WIDTH_MM` | 「完全不需要，外面 GA 设置也有一个」 | GA 档宽度（见 [[decisions/ADR-070-GalvoWeaveAsWidthSource]] 演进三） |
| `ParamOutputHz`（输出频率） | ③Adapt / `PARAM_OUTPUT_HZ` | 「自动模式机器人 RSI 的输出频率是固定的，模拟测试的频率就不应该放在这里」 | 段落长度 `SegmentDistanceMm`（见 [[decisions/ADR-103-no-value-hold-and-distance-segment]] 落地演进） |

- **③自适应区只剩「每段距离」一项**（`SegmentDistanceMm`）⇒ 分区归属随之收缩（§一「落盘分区随 UI 落点迁移」的反向收缩）。
- ⛔ **删配置项必须连根拔**：INI 键常量 + 字段默认值 + 读取 + 钳位 + 保存 + 算法层转发属性 + Manager 层转发属性 + UI 读写 + UI 控件四落点，缺一即残留死配置（本轮实测：`ManualSeamWidthMm` 残 3 处、`ParamOutputHz` 残 2 处，均为注释沿革标注，非代码引用）。
- **「光斑宽度系数」的连带清理**（乘 1.0 恒等 ⇒ 删后行为等价）：`WeldParamLookupAlgorithm.SetSpotWidthGain` / `_spotWidthGain` / `RefreshSpotWidthDic` / `WeldParamManager.RefreshSpotWidthByGain` 四链全删（含 Manager 内 5 处调用），并清掉 `swEnableGalvoWeaveQuick_CheckedChanged` 里的重算调用。
- ⚠️ **模拟测试的线激光频率不动**：`VirtualCam.FrameRateHz`（系统设置页「线激光数据频率」）是**独立位置**的另一个概念，业主裁定的「输出频率」仅指自适应输出节拍。
- **关联**：本 D5 与 D3/D4 同属 2026-11-18 振镜语义收敛批次；GA 分档与手动/自动两套模式见 [[decisions/ADR-070-GalvoWeaveAsWidthSource]] 演进节。

### 2026-11-18 · 决策 D6 · 配置文件按 TabPage 分割（XML+INI 各一套）

> 业主新增要求：「将工艺设置和系统设置下的配置文档**按照 tabpage 页面分割成不同文件**。这样在页面进行保存和修改时**不影响其他页面的值**」。

**一、缺陷根因（实测）**

`WeldParamManager.SaveAlgorithmsZone(zone)` 的实现是「写自己 zone 的 section → `SaveXdocument()` **重写整个文件**」。
未写 section 的值取自**内存对象**（加载时的文件内容）⇒ **某页面改了 UI 但未点「修改参数」，另一页面再保存，就会用内存旧值把前者的改动覆盖掉**。
⇒ 分区落盘（①System/②Quick/③Adapt/④Preset）**只保证 zone 之间互不写**，**不保证 TabPage 之间互不影响** —— 同一 zone 被两个 TabPage 共享时即耦合。

**二、载体现状（2026-11-18 实测）**

| 页面 | TabPage | 配置载体 | 独立文件？ |
|---|---|---|---|
| 工艺设置 | 激光工艺设置 | `WeldParamControl.xml`（XML ①/④ 区）+ `WeldParamControlAlgorithm.ini`（INI ②/④ 区） | ❌ 与下页共用 |
| 工艺设置 | 自适应工艺参数设置 | 同上（INI ①/③ 区） | ❌ |
| 系统设置 | 流程控制与测试 | `LineLaserConfig.xml` | ✅ |
| 系统设置 | 激光头系统参数设置 | `WeldHeadSlave.xml` | ✅ |
| 系统设置 | 轨迹跟踪参数设置 | `DeltaMotionConfig.xml` + 标定参数寄居 `WeldParamControl.xml` | ⚠️ 半独立 |

**三、决策：按 TabPage 拆文件（XML + INI 各一套）**

目标布局（`Config\WeldParamControl\`）：

| 文件对 | 归属 TabPage | 内容 |
|---|---|---|
| `Algorithm_XML\WeldParamControl.xml` + `Algorithm_INI\WeldParamControlAlgorithm.ini` | 工艺设置页·激光工艺设置 | XML：跟踪几何的**工艺侧**项；INI：②Quick 开关 + ④Preset（LA/TA/GA 预设） |
| `Algorithm_XML\WeldParamControlAdaptive.xml` + `Algorithm_INI\WeldParamControlAlgorithmAdaptive.ini` | 工艺设置页·自适应工艺参数设置 | INI ①System 阈值段 + ③Adapt 段 |
| `Algorithm_XML\LaserCalibration.xml` + `Algorithm_INI\LaserCalibration.ini` | 系统设置页·轨迹跟踪参数设置 | XML：跟踪参数 + 标定参数（含 4 个跟踪几何项） |

**四、本轮已落地（D6 第一步，零存量迁移）**

- **XML 侧**：④Preset 区的 `SEAM_GUIDE` 几何 4 项（`AXIS_MM_PER_LASER_MM`/`GUIDE_SIGN`/`LEAD_DISTANCE_MM`/`ROBOT_Y_GAIN`）**迁入 ①System 区** ⇒ `SaveZoneXmlPreset`/`LoadZoneXmlPreset` 两个方法**整体删除**（XML 侧只剩 System 区）。
  - ⭐ **section 名不变 ⇒ 存量文件零迁移**（同一 `SEAM_GUIDE` 节点，只是归属 zone 变了）。
- **标定参数归位**：`TEACH_LOCK_Y_MM`（示教 Y 锁定）与 `CALIBRATED_CENTER_Y/Z`（标定中心点）随 UI 一并迁入系统设置页·轨迹跟踪·标定参数区（语义本属标定参数）⇒ **XML 的 ①System 区全部归该 TabPage 独占**。
- **工艺设置页不再落 ①System 区** ⇒ 工艺页保存只写 INI ②/④ 区 ⇒ **XML 文件成为「轨迹跟踪 TabPage」独占文件，跨 TabPage 覆盖问题在 XML 侧根治**。
- ⚠️ **残留（未闭环）**：INI 侧仍为单文件（②/④ 区与 ①/③ 区同文件）⇒ 工艺设置页两个 TabPage 之间**仍有覆盖风险**；且 `LASER_CALIBRATION`/`SEAM_GUIDE` 若要物理拆到第三个文件需**逐键迁移**（同名 section 跨文件拆分）⇒ 列为下一轮任务。

**五、判据（可复用）**

- ⛔ **zone ≠ TabPage**：分区落盘只解决「zone 之间」，跨 TabPage 隔离**必须靠物理分文件**。
- ⛔ 拆文件时优先选「**section 名不变、只改 zone 归属**」的路径 —— **存量零迁移**；只有必须分文件时才做逐键迁移。
- ⛔ 迁移项的**UI 落点必须与配置归属同页**（否则仍会跨页写同一文件）。

### 2026-11-18 · 决策 D7 · Y 轴行程上下限取消（改用轴软限位）

> 业主裁定：「取消 Y 轴行程上限和下限这个设置。这个在 Y 轴点击设置里面已经有了，请确认两块参数没有多次重复判断和使用」。

- **重复性核查结论**：两套配置**并存但判断不重复** —— 轴软限位（`DeltaMotionConfig` 的 `POSITIVE_LIMIT`/`NEGATIVE_LIMIT`，UI 在轴配置弹窗 `AxisConfigForm`）**仅随 XML/CSV 存储**（`SoftLimitMode` 注释明确「无下发路径，不送驱动器」），**未参与任何运行时判断**；而工艺配置侧 `YAxisMinMm`/`YAxisMaxMm` 是 `MotionControlWorkflow` 里**唯一**做限幅与越界判据的地方（`ClampToStroke` + 回归越界 + 限频告警）。
- **决策**：删 `YAxisMinMm`/`YAxisMaxMm`（属性 + Path 常量 + 默认值 + 读取 + 保存 + 互换钳位共 6 处），限幅与越界判据**改接轴软限位**（唯一真相源）—— 新增 `MontionManager.GetAxisConfigByName(axisName)`（精确名取轴配置）与 `MotionControlWorkflow.TryGetSeamAxisSoftLimit(out min, out max)`。
- ⛔ **台达软限位约定：0 = 不启用** ⇒ 两侧皆 0 时**不做限幅**（不静默按 0 夹紧）。
- ⚠️ **行为变化（必须现场核对）**：原限幅区间 `[-15, +15]`；改接后取轴软限位，现场 XML 实测值为**正 20 / 负 -1**（两轴相同，负值 -1 明显是占位值而非真实行程）⇒ 区间变为 `[-1, 20]`（下限收紧 14mm）。**需把 Y 轴正/负软限位配成真实行程**（如 -15/+15）才能恢复原有保护范围。

### 2026-11-19 · 决策 D8 · INI 按 TabPage 逐项逐文件拆分（完成 D6 残留）+ 死配置清理

> 业主裁定：「完成逐项逐文件迁移」+「INI 拆到 4 个 TabPage 各一套」+「存量一次性逐键迁移，旧文件停读」+「删 4 个零引用死配置」。

**一、D6 方案表的实测修正（本轮推翻原表三处）**

D6 表格基于「zone 归属」的假设，实测「**zone → 控件 → TabPage**」后修正如下：

| D6 原表写的 | 实测真相（控件树 + 代码调用双向核实） |
|---|---|
| ②Quick 开关归「工艺设置页」 | ❌ 5 个 Enable 开关（`swEnableAdapt`/`swEnableGalvoWeaveQuick` 等）实际在**系统页·流程控制与测试**（`tLPFlowSetting`） |
| ④Preset 归「工艺设置页」 | ✅ 对，但**同一 zone 内部跨 TabPage**：`LockYCalib`（`radioQuickYForceCalibPose`）在工艺页、Enable 开关在系统页 |
| XML 要拆 3 个文件 | ❌ XML 只有 ①System 一区，**拆不了**；要拆的是 INI |

⇒ **zone 粒度不足以表达 TabPage 归属** ⇒ 新增 `AlgorithmsZone.Flow`（②′）把系统页的启用开关组独立出来。

**二、根因（比 D6 认识的更深一层）**

`INIFile.SaveToFile()` 是 **`File.WriteAllText` 整文件重写** —— 与 XML 的 `SaveXdocument()` 同理 ⇒ **D6 只治了 XML，INI 才是主战场**。
且 D6 时的「XML 成轨迹跟踪 TabPage 独占」只解决了 XML 侧；INI 侧 `SEAM_GUIDE`(20 键) 与 `PROCESS_CONTROL`(22 键) 各自混装**两个 TabPage** 的键。

**三、最终文件布局（4 个 TabPage 各一套）**

| TabPage | INI 文件 | section | 项数 |
|---|---|---|---|
| 工艺·激光工艺设置 | `WeldParamControlAlgorithm.ini` | `PROCESS_CONTROL` | 13（Preset 12 + `LOCK_Y_CALIB`） |
| 工艺·自适应工艺参数设置 | `WeldParamControlAlgorithmAdaptive.ini` | `WELD_PARAM_ADJUST` | 2 |
| 系统·流程控制与测试 | `WeldParamControlAlgorithmFlow.ini` | `PROCESS_CONTROL` + `SEAM_GUIDE` | 5（4 开关 + `ENABLE_GUIDE`） |
| 系统·轨迹跟踪参数设置 | `WeldParamControlAlgorithmTrajectory.ini` | `SEAM_GUIDE` | 19（跟踪阈值） |

XML 侧不变（`WeldParamControl.xml` 已是轨迹跟踪 TabPage 独占）。

**四、实现要点**

- **zone → 文件路由**：`WeldAlgorithmsConfig.AlgorithmIniSet.FileFor(zone)`（`System→Trajectory` / `Quick→Preset` / `Flow→Flow` / `Adapt→Adaptive` / `Preset→Preset`）。
- **`SaveAlgorithmsZone(zone)` 只落目标文件**：改 `config.SaveZoneIni(targetIni, zone)` + `targetIni.SaveToFile()`，**不再**全量 `SaveToFile()` ⇒ 页 B 保存不触碰页 A 的文件。
- **`Load/SaveProcessIni` 改为按文件分组签名**（`AlgorithmIniSet`），逐文件落盘。
- **补键模板按文件分组**：`HealAlgorithmsConfigKeys` 对每个文件用**自己 zone** 的模板（否则会把别的 TabPage 的键补进本文件）。
- **`ConfigPathMigrator` 加 3 条新路径**（旧目录迁移）。

**五、存量逐键迁移（同名 section 跨文件 ⇒ 必须逐键搬）**

`MigrateLegacyAlgorithmIni()`：迁移 26 键（Trajectory 19 + Adaptive 2 + Flow 4 + Flow/ENABLE_GUIDE 1），随后从 Preset 文件**物理删除**已迁走的键 + 已废死键（36 键）⇒ 该文件只留自己 TabPage 的键。
- 幂等：目标文件已有该键则不覆盖；**顺序**：先写目标文件落盘 → 再删源键并落盘（中途崩溃 ⇒ 下轮重迁，不丢值）。
- ⛔ **迁移源就是 Preset 文件本身**（路径未变）—— 独立 legacy reader 会与 Preset reader 争用同一文件，导致落盘把已迁走的旧 section 原样写回。

**六、死配置清理（物理删除）**

- **4 个零引用死配置**：`LockSpotCalib` / `LockWirePos` / `SpotCalibPosMm` / `WireLockPosMm` —— 全仓引用数 **0**（无 UI 落点、无运行时消费），删属性 + INI 键常量 + 读写 + 存量键。
- **XML 死键**：`Y_AXIS_MIN_MM` / `Y_AXIS_MAX_MM`（D7 已删配置项，存量 XML 残留）⇒ 新增 `RemoveChild` 在保存时物理删除。
- **存量 INI 已废键**：`SEAM_WIDTH_SOURCE` / `MANUAL_SEAM_WIDTH_MM` / `SPOT_WIDTH_GAIN` / `PARAM_OUTPUT_HZ`（D5 已删配置项）⇒ 迁移清理时一并删。

**七、判据（可复用）**

- ⛔ **zone ≠ TabPage ≠ 文件**：zone 是 UI 语义分区，TabPage 是页面单元，文件是存储单元 —— 三者粒度不同 ⇒ 拆文件必须先建「zone → 控件 → TabPage」三段映射，**不能凭 zone 猜归属**。
- ⛔ **整文件重写的载体（`SaveToFile` / `SaveXdocument`）必然跨页覆盖** ⇒ 隔离的唯一手段是**物理分文件**，不是分区落盘。
- ⛔ **同名 section 跨文件 ⇒ 必须逐键迁移**，不能靠「section 名不变」零迁移。
- ⛔ **迁移源与目标不能是同一物理文件的两套 reader**（会互相覆盖写回）⇒ 合并为单一 reader + 迁走后物理删键。
- ⛔ 补键模板（自愈）也必须按文件分组，否则会把别页的键补进本文件。

**八、验证**

- 真编译 `errors=0 rc=0`；静态守卫 `files=168 fail=0 PASS`。
- **迁移逻辑验证（副本目录，绝不动源文件）**：16 项断言全通过 —— 键分布正确（Trajectory 19 / Adaptive 2 / Flow 5 / Preset 13）、值保真（5 项逐值比对）、幂等（二次迁移 moved=0）、空 section 自动清除（对齐 `INIFile.DeleteKey` 删空节语义）。
- **核心诉求验证**：拆分前「页 B 保存覆盖页 A 磁盘值」根因复现；拆分后页 B 保存不触碰页 A 文件 ⇒ **跨页隔离成立**。

### 2026-11-19 · 决策 D9 · 读/改/存三按钮的 TabPage 边界（严格化）

→ **已拆分为独立页**：[[decisions/ADR-109-UiButtonTabPageBoundary]]（本页超 300 行整合页上限）。
要点：三处「读取」按钮越界（全量重载替换配置对象 + 跨 TabPage 回填）⇒ 改用 `LoadAlgorithmsZone(zone)` 只刷本区、写回现有对象。

## 相关页面

- [[decisions/ADR-068-WeldAlgorithmsConfigZoneReorg]] —— 分区读写接口与四点闭环底座（分区归属随 UI 落点迁移的延伸）
- [[lessons/ConfigZoneSaveWiring]] —— 本族缺陷的教训页（判据清单）
- [[lessons/SignatureAndWiringConsistency]] —— 「接线完整性」三类判据的上位教训
- [[api/SystemControlPage]] · [[api/ProcessControlPage]] · [[api/FilebackupPage]] · [[architecture/CodeMap]]
