# AdaWeldSystem LLM Wiki — AI 知识库管理员工作规则

> 基于 Andrej Karpathy LLM Wiki 理论构建
> 版本：V1.0 | 创建时间：2026-07-01
> 位置：`Vicoding管理平台/LLMWiki/` —— 健康检查由 `tools/` 下四个只读扫描器（`wiki_audit.py` / `lint_scan.py` / `drift_scan_precise.py` / `ingest_purity_scan.py`）承担

---

## 核心理念

传统 RAG 的问题：AI 每次回答都在"从零开始"重新发现知识，没有积累。

LLM Wiki 的解决方式：AI 持续维护一个"活的"Wiki，知识编译一次后持续复用，交叉引用自动建立，矛盾自动标注。越用越丰富，有复利效应。

**分工关系**：
- **你（人类）**：负责找资料、提问题、做判断、审查 AI 输出
- **AI（知识库管理员）**：负责整理、交叉引用、标注冲突、归档、记账
- **Wiki 管理工具**：负责可视化浏览、知识图谱、搜索、双向链接

---

## 默认知识库路径

**当用户未显式指定知识库时，AI 必须默认使用以下路径作为知识库根目录：**

```
Vicoding管理平台/LLMWiki/
```

**规则**：
1. 每次收到开发指令（如 `/vibeCoding`、`/updateskill`、代码审查等），如果用户没有明确说"使用某某知识库"或"切换到某某 Wiki"，AI 自动将 `Vicoding管理平台/LLMWiki/` 视为当前知识库。
2. AI 在执行任何 Query/Ingest/Lint 操作前，先检查该路径是否存在：
   - 如果存在 → 正常执行工作流
   - 如果不存在 → 提示用户知识库未初始化，询问是否创建
3. 禁止在无知识库的情况下直接开始编程。如果默认路径不存在且用户未指定其他路径，AI 必须先初始化或要求用户指定，不能默认退回到"从零开始"模式。
4. 用户可以通过显式指令切换知识库，例如："切换到 D:/OtherProject/LLMWiki"。

## 目录结构

```
LLMWiki/
├── AGENTS.md              ← 本文件：AI 工作规则说明书（你和 AI 共同维护）
│
├── raw/                   ← 原始资料层：AI 只读不改（真相源）
│   ├── skills/            ← 开发团队 Skill 规范（从 Skills/ 同步）
│   ├── knowledge/         ← 第三方技术知识库原始资料（EmguCV / HelixToolkit / KUKA_OPT）
│   ├── history/           ← 开发历史记录（history.md 按时间分段）
│   ├── architecture/      ← 主控设计原档（主控设计.xlsx、激光焊接系统业务流程图.pdf）
│   ├── delta/             ← 台达 EtherCAT 厂商原始清单与错误码
│   └── mecavision/        ← 麦格威监控相机 SDK 原档（`MecaVision_SDK/`，仅存档，编译产物已清）
│   # ⚠️ 2026-09-12：原 `raw/codebase/`（0 字节空目录）与 `raw/tools/crg_build.py`（已退役的图谱工具）已删除
│
├── wiki/                  ← AI 维护的知识层：AI 全权负责写和维护
│   ├── project/           ← 项目整体知识（概览、技术栈、演进路线）
│   ├── modules/           ← 模块详解（每个模块一页，含依赖、接口、约束）
│   ├── api/               ← API 参考（公共类、方法、事件、配置）
│   ├── decisions/         ← 设计决策记录（ADR：为什么这样设计）
│   ├── standards/         ← 规范标准（**必须遵守**，由 index 路由触发，免重复输入）
│   ├── lessons/           ← 历史教训（**踩过什么坑**，编码前门禁检查项）
│   ├── guides/            ← 操作型指导与参考手册（**怎么做**，2026-09-01 新增，自 lessons/ 迁出）
│   ├── architecture/      ← 架构设计（设备控制架构规范页）
│   ├── people/            ← 专员职责与协作关系（谁负责什么）
│   ├── rules/             ← Skill 流程执行强制规则（KR-001~KR-013，**原 Skill Key Rules 的下沉处**，编号唯一权威 = rules/Rules-Index.md）
│
│   # 三层「规范性」分类判据（2026-09-01 确立，避免指导文件错放 lessons/）：
│   #   standards/ = 强制规范，违反即不合格，由 index 场景路由自动触发
│   #   lessons/   = 教训门禁，记录已发生过的坑，编码前逐条确认规避
│   #   guides/    = 怎么做，操作手册/参考手册/工具用法，查阅型，非强制非教训
│
│   # ⚠️ rules/ 的边界（2026-11-02 收敛）：rules/ 只收**流程执行类**规则
│   #   （规定「AI 跑这个工作流时该怎么做」）；**约束代码 / 知识库内容本身**的规则
│   #   一律归 lessons/（坑）、standards/（格式规范）、decisions/（决策理由）。
│   #   判据与示例见 [[standards/WikiPageFormatSpec]] §2.4b。
│
│   # ⚠️ 禁止子目录（2026-09-01 确立）：wiki/ 下各分类一律平铺为 .md 文件，
│   #   不再新建任何子目录。成组靠「文件名前缀 + 索引分组 + 横幅回链父页」三件套，
│   #   例：standards/CodeSimplification-RefFileOrganization.md（原 standards/references/ 已撤销）。
│
├── wiki/index/           ← 索引层（独立于日志）
│   └── index.md           ← 全库内容索引（内容导向，按分类组织）
│
├── tools/                 ← 脚本工具链（24 个：8 个扫描闸门 / 索引 / 日志与历史 / 治理 / 规范化 / 结构 / 出包）
├── scripts/               ← 代码审查与批量脚本（csharp_review.py / scan_by_folder.sh）
├── skills/                ← 工作流 Skill 的仓库副本（双副本之一）
│   # 双副本纪律（2026-11-02 收口）：本目录 + 用户级 `~/.trae-cn/skills/vibecoding-llmwiki/` 必须内容一致（行尾同为 LF）
│   #   —— 用户级是 Trae 实际加载的那份；两份都要随规范同步更新。
│   # 历史副本（不再维护、不再同步，仅作历史留存）：`~/.workbuddy/skills/vibecoding-llmwiki/SKILL.md`
│   #   —— ⛔ 不参与双副本一致性比对，也不由 `tools/skill_pointer_check.py` 校验；文件保留不删。
│
└── logs/                  ← 日志与历史层（三层载体，脚本串联）
    ├── log.md             ← 当轮变更明细（时间导向，倒序追加，上限 50 条）
    ├── INDEX.md           ← 归档索引（一行一天，由 wiki_log_tidy.py index 生成；截断后自动重建）
    └── backup/            ← 跨轮归档（log_YYYY-MM-DD.md，按日一份）
```

---

## 写作规则

1. **全部使用 Markdown**，保持纯文本、人类可读、可审计
2. **每页聚焦一个主题**，文件名使用 PascalCase 或 kebab-case
3. **使用 [[页面名]] 建立内部双向链接**，AI 自动维护链接关系
4. **更新已有页面而非创建重复页面**，避免信息分裂
5. **新信息与旧信息冲突时，明确标注矛盾**，格式：`> ⚠️ 矛盾标注：[新来源] 指出 XXX，与 [旧页面] 中的 YYY 冲突`
6. **代码块使用 ```csharp 语法高亮**
7. **页面顶部可选 YAML frontmatter**，用于 Dataview 查询

### 时间戳强制规范（严格执行）

**所有 Ingest/Mini-Ingest 追加 logs/log.md 时，时间戳必须通过以下 PowerShell 命令获取，严禁估算、猜测或手动填写：**

```powershell
Get-Date -Format "yyyy-MM-dd HH:mm:ss"
```

**执行要求**：
1. 每次追加日志记录前，必须先执行上述 PowerShell 命令获取当前系统时间
2. 禁止行为：
   - 禁止使用估算时间（如根据对话时间推测）
   - 禁止手动填写固定时间字符串
   - 禁止复用历史时间或递增历史时间
3. 如果因权限或环境限制无法执行 PowerShell 命令，时间戳字段应标记为 `[No.]`，**绝不允许猜测填写**
4. 沙盒环境中执行此命令，返回的格式直接作为日志时间戳

### 日志追加位置规范（严格执行）

> 历史教训：日志追加位置规则见 [[guides/Project-Tools]] 第 2.1 节 —— 曾因追加位置不统一导致 log.md 时间顺序完全混乱。

**所有 Ingest/Mini-Ingest 追加 logs/log.md 时，新记录必须添加在文件最前面（顶部），而非末尾。**

**执行要求**：
1. 追加位置：**文件最顶部**，紧接在 `---` 分隔符之后、所有已有日志条目之前
2. 排列顺序：整个 log.md 必须保持**严格的时间倒序**——最新的条目在最前面，旧的条目依次向后排列
3. 禁止行为：
   - 禁止将新日志追加到文件末尾
   - 禁止在已有条目中间插入新日志（除非是按时间倒序的正确位置）
   - 禁止产生时间顺序混乱（如后面的条目时间比前面还新）
4. 格式要求：每条记录以 `## [日期时间] 操作类型 | 描述` 开头，记录之间用 `---` 分隔

### 日志截断策略（每周任务，非每次任务）

> 用户约定 2026-08-12：**日志截断是每周任务，不是每次任务**。

- **平时每次 Ingest 追加日志一律不截断、不备份**——即使条目数超过 50 条也不在本任务内截断。
- **每周 Phase 4 Lint 时**一次性执行截断（保留最新 50 条）：`python tools/wiki_log.py truncate` —— 旧条目**按日期归档**到 `logs/backup/log_YYYY-MM-DD.md`（⛔ 截断是**归档不是丢弃**），并自动重建 `logs/INDEX.md` 归档索引（⛔ 归档存在却无索引 = 历史链路断裂）。
- **⛔ log 截断入口唯一** = `python tools/wiki_log.py truncate`（`wiki_log_tidy.py truncate` 仅是委托，⛔ 禁自建截断脚本）；排序与表头修正在 Phase 4 收尾可一并跑 `python tools/wiki_log_tidy.py all`。
- **查历史走 `logs/INDEX.md`** —— 定位日期 → 读对应归档文件；⛔ 禁凭记忆断言「上次怎么处理的」。
- **日志写入统一走脚本**：`python tools/wiki_log.py append <op> "<标题>" --src ... --op-list ... --files ... --note ...`（时间戳由脚本取，⛔ 禁止手填）。
- 完整命令与规则见 [[project/vibecoding-workflow]] Step 3.8「log 写入与截断」。

### 布局容器自由化（2026-08-12）

> 见 [[decisions/ADR-024-LineLaserThreeLayerRefactor]]。

- **GridPanel/FlowPanel 不再强制使用**——它们会强制排序子控件。
- 布局容器按需自由选择（GridPanel / FlowPanel / Panel 绝对定位 / Dock / Anchor / WinForms 原生容器等）。
- 项目 UI 主体保持 **AntdUI 风格**；AntdUI 缺失的控件可用 **WinForms 原生控件**兜底；**禁止使用 SunnyUI 控件**。
- 已用 GridPanel/FlowPanel 的页面**不强制重写**，由用户自行判断。

### Region/EndRegion 结构完整性（2026-08-13）

- `#region` 与 `#endregion` 代表一块代码区域的**函数功能划分**，是一对不可分割的结构，**缺一不可**。
- **禁止**删除某个方法时连带删除其所属的 `#region` 块；也不得在精简/重构时遗留孤立的 `#endregion`。
- 删除、移动或精简任何方法前，必须先确认其所属 region 结构的完整性，删除后必须保持 region/endregion 配对平衡。
- 每个 region 命名应概括该区域的功能语义（如"状态转换核心方法"、"工作循环子步骤"），不得包含迁移记录/实施日期等过程性信息。

**正确示例**（区域结构）：
```markdown
#region 工作循环子步骤
    #region 取图超时
    ...
    #endregion
    // 采集/分析/调整等子步骤方法
#endregion
```

**正确示例**（文件顶部）：
```markdown
# Wiki Log — 变更日志

> 时间导向的追加日志。每条记录以 `## [日期时间] 操作类型 | 描述` 开头。
> **最新记录始终在最前面**。

---

## [2026-07-03 14:15:57] fix | 最新的一条日志
- ...

---

## [2026-07-03 13:31:48] fix | 上一条日志
- ...
```

---

## Ingest 工作流（摄入新资料）

**触发条件**：新增 Skill 文件、代码变更、第三方技术资料、设计决策

> ⛔ **单一权威**：本工作流的**唯一规范 = [[project/vibecoding-workflow]]（Phase 0~4）**。
> 本节只作通俗别名（Query=Phase 0、Ingest=Phase 3、Lint=Phase 4），**不得**据此另立流程。

**Phase 0 Query（知识检索）**：读 `wiki/index/index.md` → 按 ⚡ 速查路由定位 1~3 页 → 读该页。⛔ 不得跳过 [[architecture/CodeMap]]（先查代码地图再 Grep）。
**Phase 3 Ingest（知识沉淀）**：更新 `modules/` / `api/` / `decisions/` / `lessons/` → 重建 index（`tools/wiki_index_build.py`）→ 追加 log（`tools/wiki_log.py append`，时间戳自动取）。
**Phase 4 Lint（健康检查）**：跑五扫描器 + 人工清单。

---

## 页面格式契约（强制）

⛔ 各页的**结构、字段、行数上限、增长规则**唯一规范 = [[standards/WikiPageFormatSpec]]，由 `tools/wiki_format.py` 机械校验（Phase 4 必跑，违规非零退出）。

四条最常用规则：

1. **ADR / 教训 / 规则新增必须「先合并、后新建」**：先跑 `tools/adr_new.py check <关键词>` / `tools/lesson_new.py check <关键词>` / `tools/rules_new.py check <关键词>`；命中同主题就**合并**进既有页（ADR 与规则加「演进记录」节，教训加「追加条目」节），**不新建页**。
2. **详细叙事只进 `logs/log.md`**：ADR / 教训 / 规则 / index 页只留结论与约束；验证过程（静态 N/N、探针数据、试错记录）属 log。
3. **index.md 由脚本生成**：⛔ 不得手工编辑其分类表与速查路由表（路由源 = `tools/data/routes.tsv`，由 `tools/wiki_route_rebuild.py` 生成）。
4. **新页须登记**：新建页面后跑 `tools/wiki_index_build.py` 重建索引，并确认对应索引页同步登记（ADR → [[decisions/ADR-Index]]；规则 → [[rules/Rules-Index]]）。

### 阅读顺序（三层）

| 层 | 内容 | 读多少 | 何时读 |
|---|---|---|---|
| **A · 流程约束** | `wiki/rules/`（KR-001~013） | **全读 13 条** | **动手之前**（最先读） |
| **B · 内容知识** | `wiki/standards/` `wiki/decisions/` `wiki/lessons/` | **按需**：命中才读 | Phase 0 检索时 |
| **C · 沉淀维护** | 格式契约 / 脚本工具 / log 链路 | **不预读**，用时现查 | Phase 3 沉淀 / Phase 4 校验 |

⛔ **A 层不得跳过**（顺序错 / 门禁漏 / 谎报编译都源于此）；⛔ **B 层不预读整类**（39 页 lessons + 78 页 ADR 全读会耗尽上下文）。

### 流程规则（Key Rules 的下沉处）

⛔ **Skill 里不再维护规则清单** —— 规则正文与判据在 **`wiki/rules/`**（`KR-001~KR-013`，编号唯一权威 = [[rules/Rules-Index]]）。
查法：index 第十二节 → Rules-Index → 规则页（固定结构：适用范围 / 规则正文 / 判据 / 反例 / 相关页面）。
新增/演进走 `tools/rules_new.py`（先 check 再 merge/new），校验走 `tools/rules_check.py`。

⛔ **rules/ 只收流程执行类规则** —— 约束「AI 跑这个工作流时该怎么做」；
⛔ **约束代码 / 知识库内容本身**的规则（csproj 注册 · 行尾守恒 · 锚点构造 · 并发 Edit · 零消费≠死成员 等）**一律不进 rules/**，归 `lessons/`（坑）/ `standards/`（格式规范）/ `decisions/`（决策理由）。判据见 [[standards/WikiPageFormatSpec]] §2.4b。

### Skill 指向纪律

⛔ **Skill 只写角色级锚点与「去哪查」的机制表述**，不写死具体内容页名（具体 ADR / lessons / guides / modules / api 页）—— 这些页会重编、拆分、合并，写死即失效。闸门：`tools/skill_pointer_check.py`。规范见 [[standards/WikiPageFormatSpec]] §六。

---

## 健康检查（Phase 4 必跑）

⛔ **用绝对路径解释器**（PATH 上的 `python` 是 0 字节占位符，不可用）——见 [[guides/ExecutionEnvironment]]。

```
python tools/wiki_audit.py          # 11 项体检：红链 / 孤儿 / 索引重复 / ADR 空洞 / 体积 / 重复度 / 错放 / 入链 / 子目录 / 过小分类 / lessons 三处一致
python tools/lint_scan.py           # 死链 / 孤儿 / ADR 编号冲突 / 外链失效
python tools/drift_scan_precise.py  # wiki 引用的 .cs 是否仍存在
python tools/ingest_purity_scan.py  # 沉淀纯度：index/ADR-Index/CodeMap/架构页禁验证叙事·日期沿革·日志体
python tools/wiki_format.py         # 页面格式契约：结构 / 字段 / 行数 / 增长规则
python tools/rules_check.py         # 流程规则页：编号连续 / 结构契约 / 索引一致 / 判据非空
python tools/skill_pointer_check.py # Skill 指向防漂移：⛔ 不得写死内容页名
python tools/raw_asset_check.py     # raw 资产检索表与实际内容一致
```

**健康判据**：红链 0 · 孤儿 0 · 索引重复行 0 · 二级子目录 0 · 过小分类 0 · lessons 三处一致（目录==§五表行==摘要计数）· drift 待修正 0 · 纯度违规 0 · **格式违规 0** · **规则违规 0** · **Skill 指向违规 0**。脚本一律按 `__file__` 推导路径，禁硬编码绝对路径。

---

## AI Coding 特殊规则

### Skill 与 Wiki 的协作关系

```
raw/skills/     →  开发规范（AI 执行代码时参考）
wiki/people/    →  专员职责详解（AI 分配任务时参考）
wiki/modules/   →  模块架构知识（AI 修改代码时参考）
wiki/lessons/   →  历史教训（AI 避免重复踩坑）
wiki/decisions/ →  设计决策（AI 理解"为什么这样设计"）
```

### 代码变更 → Wiki 更新联动（旧模式，已升级）

> ⚠️ 此机制已被 [[project/vibecoding-workflow]] 中的 **Phase 3: Ingest** 取代。旧模式仅在未触发完整 /vibeCoding 流程的零散代码修改时作为兜底保留。

旧模式步骤（Mini-Ingest）：
1. 读取最新 history.md 记录
2. 判断影响范围（哪些模块、哪些接口、哪些设计决策）
3. 更新对应 wiki/ 页面
4. 如果涉及设计变更 → 创建或更新 wiki/decisions/ 页面
5. 如果踩了新坑 → 更新 wiki/lessons/ 页面
6. 追加 logs/log.md

---

## /vibeCoding 工作流（LLMWiki 原生版）

**完整规范见 [[project/vibecoding-workflow]]。本节仅摘录核心规则。**

### 核心变革：从 Skill-Centric 到 LLMWiki-Native

```
旧模式：Skill 文件 → 指挥编码 → 可选更新 Wiki
新模式：Query Wiki → 规划约束 → 编码实现 → 强制 Ingest Wiki
```

### 触发条件

用户输入 `/vibeCoding`、"/vibecoding"，或明确表达开发/修复/实现需求时触发。

### 强制入口检查

1. **知识库存在检查**：默认路径 `Vicoding管理平台/LLMWiki/` 必须存在
2. **禁止"从零开始"**：不存在时必须先初始化 LLMWiki，不能直接编码
3. **禁止跳过 Query**：编码前必须先执行 Phase 0 Query，读取 wiki/index/index.md 定位相关页面

### 五阶段速查

| 阶段 | 核心动作 | 必读 Wiki 路径 | 产出 |
|------|---------|---------------|------|
| **Phase 0: Query** | 检索知识 | `wiki/index/index.md` → `wiki/decisions/` + `wiki/lessons/` + `wiki/modules/` + `wiki/api/` | 知识检索报告 |
| **Phase 1: Plan** | 规划 + 约束确认 | 基于 Query 结果 | 编码计划（含知识沉淀预判） |
| **Phase 2: Code** | 编码实现 | 实时对照 Phase 0 的 ADR 约束和 Lessons 门禁 | 代码文件 |
| **Phase 3: Ingest** | **强制知识沉淀** | 更新 `wiki/modules/`、`wiki/api/`、`wiki/decisions/`、`wiki/lessons/`、`wiki/index/index.md`、`logs/log.md` | 更新后的 Wiki |
| **Phase 4: Lint** | 健康检查 | 扫描矛盾、孤儿页面、红链 | 健康报告 |

### 关键规则

1. **ADR 即硬约束**：`wiki/decisions/` 中的架构决策记录（ADR）在编码前就成为必须遵守的约束。编码完成后必须回顾检查是否违反。
2. **Lessons 即门禁**：`wiki/lessons/` 中的踩坑记录是编码前的强制检查项。例如「新建 .cs 文件必须同步注册到 .csproj」见 [[guides/Namespace-Compilation]] 第 1.1 节。
3. **Skill 降级为参考**：`raw/skills/` 下的 Skill 文件是**参考资料**，不是**指令源**。如果 Skill 与 LLMWiki 内容冲突，以 LLMWiki 为准。
4. **Ingest 强制性**：Phase 3 Ingest 不是可选步骤。没有 Ingest 的编码视为未完成。
5. **新决策必须记录**：编码中如涉及新的架构选择，必须在 `wiki/decisions/` 创建 ADR。
6. **备份包落点唯一**：所有备份/出包压缩包（`AdaWeldSystem_backup_*.tar.gz`、`AdaWeldSystem_output_*.tar.gz`、`LLMWiki_backup_*.tar.gz`）一律落**工作区根**（workbudddy，由 `tools/backup_adaweld.py` ROOT 推导）；知识库包用 `--llmwiki` 模式生成（按天去重），禁止手搓 tar、禁止落到工作区外（2026-10-14 治理：外层错放 5 包已归位根目录）。

### 时间戳规范

Phase 3 Ingest 追加 `logs/log.md` 时，时间戳必须通过 PowerShell 获取：
```powershell
Get-Date -Format "yyyy-MM-dd HH:mm:ss"
```
严禁估算、猜测或手动填写。无法执行时标记为 `[No.]`。

### 双向链接规范

Wiki 页面中提到的**任何模块名、专员名、核心概念**，必须用 [[页面名]] 链接。

---

## 与人类协作规则

1. **人类拥有最终决策权**：AI 提出整理方案，人类确认后执行
2. **AGENTS.md 共同进化**：发现规则不适用时，双方协商修改
3. **Wiki 页面人类可编辑**：人类可以直接修改 wiki/ 中的任何页面
4. **敏感操作需确认**：删除页面、合并页面、重命名页面前需人类确认
5. **定期回顾**：每两周一次，人类审查 wiki/ 结构是否合理

---

## 版本控制

整个 LLMWiki/ 是一个 Git 仓库。建议初始化 Git：

```bash
cd LLMWiki/
git init
git add .
git commit -m "init: LLM Wiki v1.0"
```

