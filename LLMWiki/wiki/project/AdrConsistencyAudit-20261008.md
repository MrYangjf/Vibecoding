---
title: ADR 一致性审计（2026-10-08）— 全库 ADR 及其引用处的逻辑缺陷与历史遗留
date: 2026-10-08
updated: 2026-10-08
tags: [审计, ADR, 编号体系, 一致性, 历史遗留, 逻辑缺陷, 知识库治理]
status: accepted
---

# ADR 一致性审计（2026-10-08）

> **一句话**：ADR 的**权威三元组（文件名 / `ADR-Index.md` / `index.md`）完全一致**，但 **24 个 ADR 页的 `title:` / H1 自称编号停留在「上一代编号」**，且这些旧号与现行其它页**撞车**；另有 6 条失效链接、2 处跨页数值矛盾、1 处悬空红线引用。全部为**历史修改遗留**，无「设计本身自相矛盾」型缺陷。

- **审计范围**：`wiki/decisions/` 53 个 ADR 页 + `ADR-Index.md` + `index.md` §7 + 全库 189 个 `.md` 的 764 条 `[[decisions/…]]` 链接与 3287 处裸编号引用
- **判据来源**：[[lessons/StaticVerifierJudgements]] §八（ADR 两套编号空间）· SKILL 原 rules/KR-019（已并入 lessons/StaticVerifier-AdrNumbering） / 21
- **结论**：**没有发现「现行决策互相矛盾」**；发现的问题分四层，A 层（编号错位）为**结构性**，必须处置

---

## 一、A 层：编号体系（结构性，最高优先）

### A1 ⛔ 24 页的 `title:` / H1 自称编号 ≠ 文件名编号（且与他页撞车）

**权威判定**：`ADR-Index.md` 是「编号唯一准绳」。实测 **53 页中，ADR-Index 行编号与文件名编号不符 0 处** ⇒ **文件名 + ADR-Index + index.md 三者一致，是权威**；页内元数据是遗留。

| 文件名编号 | 页内 H1 自称 | 页 | 撞车的现行页 |
|---|---|---|---|
| 002 | ADR-001 | DisposePatternFullCoverage | ADR-001-CS73-Constraint |
| 003 | ADR-004 | EnumDeduplication | ADR-004-NuGetLocalization |
| 009 | ADR-027 | DialogWindowToModalUserControl | ADR-027-MotionControllerDeltaReplacement |
| 010 | ADR-034 | LayoutContainerFreedom | ADR-034-ArchitectureRawSource |
| 012 | ADR-002 | AlgorithmEditInterfaceSplit | ADR-002-DisposePatternFullCoverage |
| 013 | ADR-023 | ThreeStateModelRefactor | ADR-023-LineLaserWorkflowRefactor |
| 014 | ADR-020 | MainDeviceStateSemantics | ADR-020-MonitorCamPage-AlgorithmInline |
| 015 | ADR-008 | ErrorReportingHierarchy | ADR-008-UIFrameworkMigration |
| 016 | ADR-027 | WorkflowResponsibilityBoundary | （唯一带「旧」前缀者，符合 原 rules/KR-019（已并入 lessons/StaticVerifier-AdrNumbering）） |
| 017 | ADR-018 | SafetyCheckConsolidation | ADR-018-CallbackAcquisition |
| 018 | ADR-004 | CallbackAcquisition | ADR-004-NuGetLocalization |
| 019 | ADR-028 | MonitorCamBoundaryAndEmguALGRefinement | ADR-028-MotionControlModule |
| 020 | ADR-001 | MonitorCamPage-AlgorithmInline | ADR-001-CS73-Constraint |
| 021 | ADR-016 | CameraConnectionStateDecoupled | ADR-016-WorkflowResponsibilityBoundary |
| 022 | ADR-007 | EmguALGThreeLayer | ADR-007-CodeSimplificationStandard |
| 023 | ADR-009 | LineLaserWorkflowRefactor | ADR-009-DialogWindowToModalUserControl |
| 024 | ADR-003 | LineLaserThreeLayerRefactor | ADR-003-EnumDeduplication |
| 025 | ADR-011 | CommModuleRefactor | ADR-011-ButtonShadowDeviceSwitch |
| 026 | ADR-024 | RsiSemanticRewriteAndDualChannel | ADR-024-LineLaserThreeLayerRefactor |
| 027 | ADR-021 | MotionControllerDeltaReplacement | ADR-021-CameraConnectionStateDecoupled |
| 028 | ADR-034 | MotionControlModule | ADR-034-ArchitectureRawSource |
| 029 | ADR-022 | CylinderConfigAndCsvImport | ADR-022-EmguALGThreeLayer |
| 031 | ADR-017 | ProductLifecycleRecordModule | ADR-017-SafetyCheckConsolidation |
| 035 | ADR-007 | RawDesignRefinement20260903 | ADR-007-CodeSimplificationStandard |

**撞车统计**：编号 `001` 被 **3** 处占用（ADR-001/002/020 的 H1）、`004` 被 **3** 处（ADR-003/004/018）、`007` 被 **3** 处（ADR-007/022/035）、`002` 被 2 处、`003` 被 2 处。⇒ **按编号检索会命中多个不同决策**。

**成因（有证据）**：`git ls-files` 显示 **HEAD 里的 49 个 decisions 文件名属于上一代编号**（如 HEAD `ADR-002-CS73-Constraint.md` ↔ 磁盘 `ADR-001-CS73-Constraint.md`）。
即历次重排**改了文件名 + 两个索引表，但没有回写每个页自己的 `title:` / H1 / `tags`** ⇒ 页内编号落后至少一代。工作树另有 **49 个未提交改名**。

**影响**：任何「见 ADR-004」式的引用，读者/AI 都可能落到 3 个不同决策之一。这是 原 rules/KR-019（已并入 lessons/StaticVerifier-AdrNumbering） 明文警告的「同号不同页」类，**三个扫描器都看不见**（`lint_scan` 的编号冲突检查只看文件名）。

### A2 ⚠️ `ADR-Index.md` 计数口径不完整（3 处）

| 位置 | 现值 | 应为 |
|---|---|---|
| 页面 `title:` | `（001~051，…追加至 067 + …）` | 补 068/069 |
| 头部块 | `现行编号：001~051 连续无断号` | `001~051 + 068/069 共 53 条` |
| 章节标题 | `## 全部 ADR（001~051，按模块分组）` | 同上（表内含 068/069 两行） |

**实测**：表行编号 `min=1 max=69 n=53`。

### A3 ⛔ `index.md` §7.0b 标题严重过期

> 现为：`### 7.0b 全量登记表（56 条，2026-09-17 重排后 + 09-20 追加 040/041/042/043 + 09-21 追加 044/045/046 + 09-22 追加 047/048/049/050/051/052/053/054 + 09-23 追加 055/056，编号即现状）`

**三个问题**：① 写「56 条」而实际 **53 条**；② 列举的 `052~056` **全部属于已废止的旧编号段**（现 `052~067` 为保留占位，不是现行 ADR）；③ 「编号即现状」与实际不符（期间又经 09-23 精简合并重排）。

### A4 ⚠️ 2 页缺 frontmatter

`ADR-002-DisposePatternFullCoverage.md`（无 `---` 块，直接从 `title:` 起）、`ADR-050-SimulationWeldCameraIntegration.md`（用行内 `- 状态：` / `- 日期：` 风格）。其余 51 页均为标准 frontmatter ⇒ 元数据格式不统一，frontmatter 解析类脚本会漏读这两页。

### A5 ⛔ 两页元数据块无法被解析（既存）

| 页 | 问题 |
|---|---|
| `ADR-002-DisposePatternFullCoverage` | frontmatter **起始分隔符是 `--`（两个连字符）**，应为 `---` ⇒ 该块不被识别为 frontmatter，`title/date/tags/status/merged_from` 全部失解析，`--` 还会被渲染成正文一行 |
| `ADR-050-SimulationWeldCameraIntegration` | **完全无 frontmatter**，用行内风格（`- 状态：` / `- 日期：` / `- 关联：`），首行即 H1 |

⇒ 全库 53 页中 **51 页格式统一，2 页例外**。

### A6 ✅ 两页行尾污染（2026-10-08 已修）

`ADR-023-LineLaserWorkflowRefactor`（CRLF=94 / loneLF=4 / **CRCRLF=1**）与 `ADR-028-MotionControlModule`（CRLF=61 / loneLF=4）。
**根因**：顶部「沿革标注」横幅是用 LF 写入的，而正文是 CRLF ⇒ 混行尾；ADR-023 另含一处 `\r\r\n`（原 rules/KR-014（已并入 lessons/WikiDriftCorrectionPitfalls） 事故型）。**本次已三步归一到 CRLF**，两页现均同质、无 CRCRLF。

### A7 ⚠️ `index.md §7.0b` 列数不一致（**2026-10-08 已修 1 行；原报「22 行 5 列」为判据错误**）

原报「表头 4 列、实测 46 行 4 列 / 22 行 5 列 / 2 行 6 列 / 1 行 7 列」—— **该结论是判据错误**：用 `line.count('|')` 数列数时，**别名链接 `[[A|B]]` 的 `|` 与行内转义竖线 `\|` 都会虚增计数**。改用「先屏蔽整个 `[[...]]`、再屏蔽 `\|`、最后切列」重算后，**主表 70 行里 69 行都是 4 列**。

**真实缺陷只有 1 行**：`ADR-042` 行缺尾列（3 列）⇒ **已补 `| accepted |`**（2026-10-08）。现主表 **69 行全部 4 列**。

### B1 ⚠️ 6 条 `[[decisions/…]]` 链接失效（全部在历史日志）

| 目标 | 现状 |
|---|---|
| `ADR-056-SeamWidthSourceAndParamXLOutput` | 页不存在（旧编号段） |
| `ADR-050-ResidualParamCleanupAndGeometryRepatriation` | 现 050 = SimulationWeldCameraIntegration |
| `ADR-033-SeamTrackingCspRealtimeMode` | 现 033 = ConfigArchitectureStandard（出现 3 次） |
| `ADR-039-UIControlPlacementRule` | 现 039 = SimulationTestAutoTerminationAndRecordCacheRelease |

全部位于 `logs/log.md` 的 **2026-09-16 ~ 09-23 历史条目**（行 914/918/1333/1539/1638/1756），引用的是**决策当时的页名**。**未处置**（历史记录，处置方式需业主裁定）。
除这 6 条外，**764 条链接中 758 条有效**（99.2%）—— 全库链接用的是**现行编号**，与文件名一致 ✅。

### B2 ⛔ 悬空引用：ADR-042 / ADR-053 / CodeMap 都称「红线源自 ADR-043」，而 ADR-043 正文无此条款

- `ADR-042` §摆幅计算规则：「⚠️ 与 **ADR-043 红线**的关系（如实记录）：红线原文（`api/WeldParamControlWorkflow.md`）…」
- `ADR-053` 「相关页面」：`[[decisions/ADR-043-WeldParamControlConsolidated]] —— 「⛔ 不要自创公式」红线来源`
- `CodeMap.md:692`：「约束 ADR：… ADR-043（⛔ 不用自创公式）…」

**实测**：`grep "自创\|不要用.*公式\|未经验证" ADR-043-WeldParamControlConsolidated.md` → **0 命中**；ADR-043 正文的「红线」只有两条：**算法纯净性红线**（不落盘/不记录）与**模拟红线**（不下发真实机器人）。
⇒ **红线真实出处是 `api/WeldParamControlWorkflow.md`（及 `architecture/DeviceControlArchitecture.md`）**。以 ADR 作为权威锚但该 ADR 无此条款 = **悬空引用**；后果是后人查 ADR-043 找不到依据，可能**误判「业主给定公式」违规**（这正是 2026-10-08 摆幅落地时真实卡住的点）。

---

## 三、C 层：跨页数值/表述矛盾（有代码证据）

### C1 ⛔ `WeldActionRecord` 字段数三处互斥

| 来源 | 声称 |
|---|---|
| `ADR-031` §四 | 「调整记录 **11 字段**…」并断言「其 **11 字段**与双记录设计**仍有效**」 |
| `ADR-052` | 「原 `WeldActionRecord` **15 字段**无这些」→ 15→20 |
| **代码实测** `ProductFileControl/Records/WeldParamControlRecord.cs` | **20 个属性** ✓（FrameIndex…AdjustData，含 SeamPointY/Z / TaPositionMm / LaPositionMm / GalvoAmplitudeMm / GalvoPatternId / HeadTempC） |

⇒ **ADR-031 的「11 字段…仍有效」是历史遗留错误陈述**，需就地加演进标注；ADR-052 的「15」是「扩展前」的历史值，也宜在 ADR-031 内对齐。

### C2 ⛔ `MotorPulsePerMm` 表述与代码不符（const 误标）

- `ADR-053`：「`WeldHeadConfig.MotorPulsePerMm`（`public const` 默认 **10**），四点闭环键 `MOTOR/PULSE_PER_MM`」—— **自相矛盾**：`const` 是编译期常量，**不可能**同时是配置项
- `ADR-030`：「**量纲可配置** `MotorPulsePerMm`（默认 10 计数/mm），配置键 `MOTOR/PULSE_PER_MM`」
- **代码实测** `MotionControl/WeldHeadSlaveDevice.cs`：
  - `public const double DefaultMotorPulsePerMm = 10.0;` ← **默认值**是常量
  - `public double MotorPulsePerMm { get; set; }` ← **字段本身可变**（`MontionManager:306/340` 读写 `MOTOR/PULSE_PER_MM` 四点闭环）

⇒ ADR-053 把「**默认值**常量」误写成「**字段**是 const」。修法：改为「`WeldHeadConfig.MotorPulsePerMm`（`double`，默认取常量 `DefaultMotorPulsePerMm = 10`）」。

### C3 ⚠️ 同一决策双页定义（双权威）

`MotorPulsePerMm` 量纲决策在 **ADR-030**（updated 2026-10-08）与 **ADR-053**（新，2026-10-08）各写一遍。两处取值一致（10 / 键一致），故**非矛盾**，但构成双权威：日后改一处必失同步。建议在 ADR-030 该条加「详见 ADR-053」指针，把定义权收归 ADR-053。

### C4 ⚠️ ADR-019 的合并来源编号与 `merged_from` 不一致

`ADR-019` 正文横幅写「整合原 **ADR-007**（监控相机模块架构）、**ADR-034**（麦格威三层重构）、**ADR-028**（业务边界澄清与 EmguALG 五层细化）」，
而该页 `merged_from: [ADR-007, ADR-034]` **只有 2 项**；且 `ADR-Index` 09-17 删除对照表记载第三项为 **ADR-019（监控相机麦格威三层）**。
⇒ 第三项的编号 `ADR-028` 与 `merged_from` / 删除对照表**三方不一致**（`ADR-028` 是另一决策：运控调整模块架构）。

---

## 四、D 层：其它历史遗留（低优先）

### D1 ⚠️ ADR 页内 39 处 `.cs` 名在代码中不存在

| ADR | 缺失 | 判定 |
|---|---|---|
| ADR-013 | `FaultRecoveryManager.cs` / `MainDeviceWorkflow.cs` / `MotionControlPage.cs` / `SafetyWorkflow.cs` / `WorkflowStateBase.cs` | 历史旧名，页内多数已有「历史名称提示」横幅 |
| ADR-017 | `SafetyFlow.cs` / `SafetyInterlock.cs` / `SafetyWorkflow.cs` / `FaultRecoveryManager.cs` | 同上 |
| ADR-025 | `GSDMLGenerator.cs` / `GlobalCommData.cs` / `KUKARobotManager.cs` / `SystemStatus.cs` | 同上 |
| ADR-031 | `RecordFrame.cs` / `RunRecordManager.cs` / `SeamTrackRecord.cs` / `WeldActionRecord.cs` … | 同上（页内已说明「已并入对应实现类文件」） |
| ADR-032 / ADR-048 | `Designer.cs`、`ParamConfigPage.cs`、`TableDemo.cs`、`ImagePage.cs` | **泛化名/示例名**误匹配，非真实漂移 |

⇒ 本体不阻塞（`drift_scan_precise.py` 健康判据 **0 处待修正**，说明这批都已带「已移除/历史名称」标注）；但 ADR-032 的 `ParamConfigPage.cs` 属**更名后未更新**（现役 `ProcessControlPage.cs`），可补标注。

### D2 ℹ️ 工作树 49 个改名未提交

`git ls-files` 50 个 vs 磁盘 54 个，49 个文件名不同 ⇒ HEAD 仍是上一代编号。提交后 git 会自动识别重命名；**但若只提交部分文件，会出现「索引是新编号、页内是旧编号」的混合态**。建议 A 层修复与本次改名**同批提交**。

---

### D3 ⚠️ tags 内的 ADR 编号 token（**2026-10-08 已判别：2 改 2 留**）

原报「4 页残留自指旧号」**部分误判** —— 带「旧」前缀或指向同族决策的 token 其实是**交叉引用**：

| 页 | tags token | 判别 | 处置 |
|---|---|---|---|
| `ADR-022-EmguALGThreeLayer` | `ADR-004` | 无旧前缀、且 004（NuGet）与本页（EmguALG 三层）无关 ⇒ **自指旧号** | ✅ 已改 `ADR-022` |
| `ADR-030-WeldHeadSlaveDevice…` | `ADR-012` | 无旧前缀、且 012（算法编辑界面）与本页（焊接头）无关 ⇒ **自指旧号** | ✅ 已改 `ADR-030` |
| `ADR-032-SimulationTestRedesign` | `ADR-042` | **带旧前缀** = 退役编号的合法交叉引用（旧058 → ADR-042 线激光跟踪） | ⏸ **保留不动** |
| `ADR-051-ILCamPageTabsConversion` | `ADR-048` | 现行编号、且 048（监控相机页 Tabs 化）与本页（ILCamPage Tabs 化）**同属「Tabs 化」决策族** ⇒ 交叉引用 | ⏸ **保留不动** |

**判据教训**：tags 里的 ADR 编号**不能一律按「自指旧号」批量替换** —— 必须先判「是否带旧前缀 / 是否与本页主题同族」。


---

## 六、批 2 执行结果（2026-10-08 17:28，业主裁定后执行）

**改动范围**：24 个 ADR 页 —— `title:` 前导编号 + 首个 H1 前导编号对齐到文件名（现行）编号；其中 **9 页**同步修正 `tags` 中「等于本页陈旧自指号」的 token（013/016/019/024/025/026/027/031/035）；其中 **2 页**（023/028）顺带把顶部横幅的混行尾归一到 CRLF。
**未动**：body 正文（含「整合原 ADR-XXX」等沿革交叉引用）、`ADR-Index` 的两张历史映射表、`index.md`、其它任何文件。

**校验**：
- `title` / `H1` / `ADR-Index` **三源编号 == 文件名编号：53/53**（唯一例外 `ADR-050` 无 `title:` 字段，属 A5 既存项，其 H1 已是 `ADR-050`）
- **编号撞车完全消除**：原 `001`/`004`/`007` 各被 3 页占用、`002`/`003` 各 2 页 ⇒ 现 **0 处**
- 行尾：**无 MIXED 文件、无 CRCRLF**（CRLF 25 / LF 28，维持「单文件同质、跨文件混用」既有状态）；BOM 18/53 守恒
- 抽检 4 页（002 无标准 frontmatter / 016 tags / 029 引号包裹 title / 031 merged_from）逐页目视确认

## 七、批 1 + 批 3 完成（2026-10-08 17:54）

**批 1（11 项全清）**：A2 `ADR-Index` 四处计数补 068/069 · A3 `index.md §7.0b` 标题 56 条→53 条并去掉已废止的 052~056 追加叙述 · A4 `ADR-002` frontmatter 起始 `--`→`---` · A5 `ADR-050` 补 frontmatter（7 行）· A7' `ADR-042` 行补尾列 · B2 红线归属澄清（`ADR-042` / `ADR-053` ×2 / `CodeMap` 共 4 处改指真实出处 `api/WeldParamControlWorkflow.md`，并写明 **ADR-043 正文无该条款**）· C1 `ADR-031` 两处加「11→20 字段」演进标注（保留原 11 字段历史描述）· C2 `ADR-053` `public const`→可变属性+默认常量 · C3 `ADR-030` 加「定义权归 ADR-053」指针 · C4 `ADR-019` 加三方不一致标注（⛔ 按 原 rules/KR-019（已并入 lessons/StaticVerifier-AdrNumbering） 不改 `merged_from`）· D3 2 改 2 留。

**批 3（6 条全清）**：`logs/log.md` 4 个失效页名共 6 处 → **`~~旧名~~`（去链接）+ 指向现行 ADR-042 / 036 / 043**。
⛔ **关键处置**：扫描器只屏蔽代码块与行内代码、**不屏蔽删除线** ⇒ `~~[[X]]~~` 仍会被当红链；故旧名一律**去链接**（删除线包纯文本），这是 原 rules/KR-015（已并入 lessons/WikiGovernanceBatchingPitfalls） 对归档内容的处置。

**三扫描**：死链 0 · 孤儿 0 · ADR 编号冲突 0 · 外部链接 0 · **红链 0（历史日志 4 类全清）** · drift 待修正 0。

## 相关页面

- [[decisions/ADR-Index]] — 编号唯一准绳（两张映射表）
- [[lessons/StaticVerifierJudgements]] §八 — ADR 两套编号空间的判据
- [[index/index]] §七 — 设计决策登记表
- [[lessons/WikiDriftCorrectionPitfalls]] — 知识库漂移修正的坑
