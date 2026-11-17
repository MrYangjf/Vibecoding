---
title: ADR-076 三界面参数读存与分区落盘接线裁定（分区归属随 UI 迁移 · 赋值先于落盘 · 禁跨区副作用）
date: 2026-10-23
updated: 2026-10-23
tags: [ADR, 配置架构, 分区落盘, AlgorithmsZone, WeldAlgorithmsConfig, SystemControlPage, ProcessControlPage, FilebackupPage, 读存按钮, 接线完整性]
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

## 备选方案

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

## 相关页面

- [[decisions/ADR-068-WeldAlgorithmsConfigZoneReorg]] —— 分区读写接口与四点闭环底座（分区归属随 UI 落点迁移的延伸）
- [[lessons/ConfigZoneSaveWiring]] —— 本族缺陷的教训页（判据清单）
- [[lessons/SignatureAndWiringConsistency]] —— 「接线完整性」三类判据的上位教训
- [[api/SystemControlPage]] · [[api/ProcessControlPage]] · [[api/FilebackupPage]] · [[architecture/CodeMap]]
