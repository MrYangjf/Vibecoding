---
name: "vibecoding-llmwiki"
description: "AdaWeldSystem LLMWiki-native vibecoding workflow. When user inputs /vibeCoding or asks for code development/bug fix/feature implementation, this skill forces AI to execute Phase 0~4 workflow with LLMWiki as the single source of truth."
version: "1.11.0"
agent_created: true
---

# /vibeCoding -- LLMWiki Native Workflow (WorkBuddy Edition)

> **core**: LLMWiki is the single source of truth. Before coding, Query the Wiki for context. After coding, Ingest knowledge back into the Wiki. Skill specs in `raw/skills/` are reference material only, not the command center.

## 0. Reading Order (Forced) —— 必读顺序

> **本 Skill 的三层知识，读的顺序与读的量都不同。** 读错顺序会浪费上下文，或漏掉硬约束。

| 层 | 内容 | 读多少 | 何时读 | 入口 |
|---|---|---|---|---|
| **A 层 · 流程约束** | **Key Rules（`wiki/rules/KR-001~013`）** | **全读 13 条**（每条 ≤45 行，一次读完） | **最先读**，动手之前 | `wiki/rules/Rules-Index.md` → 13 页 |
| **B 层 · 内容知识** | 标准 / 决策 / 教训 | **按需**：命中才读，不预读 | Phase 0 检索时 | index 速查路由 → 分类表 → 目标页 |
| **C 层 · 沉淀维护** | 沉淀链路 / 日志链路 / 脚本工具 | **不预读**，用时现查 | Phase 3 沉淀 / Phase 4 校验 | 本 Skill 对应两节 + `tools/` |

### A 层 · Key Rules —— 最先读，且**必须全读**

- **读什么**：`wiki/rules/KR-001 ~ KR-013` 共 13 页（流程执行强制规则）
- **读多少**：**全读 13 条**（每页 ≤45 行，一次读完 ≈ 550 行）
- **何时读**：**动手之前** —— 这是唯一强制预读的一层
- **怎么读**：`wiki/rules/Rules-Index.md`（编号唯一权威 + 路由表）→ 13 页正文；主题速查表见下方「Key Rules」段

⛔ **不得跳过 A 层直接进 Phase 0** —— 顺序错、门禁漏、谎报编译，都是 A 层没读的直接后果。
⛔ **不得只读 Rules-Index 的清单表就开工** —— 清单只给路由，**规则正文在规则页**（每页含「适用范围 / 规则正文 / 判据 / 反例」）。

### B 层 · 标准 / 决策 / 教训 —— 按需读，不预读

| 知识类型 | 何时读 | 怎么定位 | 读多少 |
|---|---|---|---|
| **标准**（`wiki/standards/`） | 改动命中该规范领域 | index 路由表 → 分类表 → 目标页 | 命中的那 1~3 页 |
| **决策**（`wiki/decisions/`） | 改动涉及架构选择 | `wiki/decisions/ADR-Index.md` 按主题定位 → 该 ADR 页 | 命中的那几页 |
| **教训**（`wiki/lessons/`） | 改动命中已踩过的坑 | index 第五节（一句话职责）→ 目标页 | 命中的那几页 |

⛔ **不要预读整类** —— 39 页 lessons + 78 页 ADR 全读会耗尽上下文且淹没真正命中的那几条。
⛔ **不要凭记忆记页名** —— 页会重编/拆分/合并（2026-10-30 治理轮就把判据库拆成 9 页）；一律现查。
✅ **命中判据**：index 速查路由第 2 列直接给出该读哪 1~3 页；命中即读，未命中不读。

### C 层 · 沉淀与维护 —— 用时现查，不预读

- **积累与沉淀链路** → 见本文「Knowledge Accumulation Chain（知识积累与沉淀链路）」
- **日志与历史记录链路** → 见本文「Log & History Chain（日志与历史记录链路）」
- **脚本工具** → 见「Workspace Path Map」的工具分组表

⛔ **不预读脚本源码** —— 工具是**执行**对象不是**阅读**对象；用时按表跑命令即可。

## Workspace Path Map

All paths in this skill are relative to the workspace root:

```
WORKSPACE_ROOT = D:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\workbudddy
```

> **⚠️ Do not trust the literal above blindly (2026-09-03)**: the previous literal was
> `D:\焊接程序开发`, left over from an older machine where it no longer existed — so every
> absolute path in this skill silently pointed nowhere and the scanners reported "0 files"
> while looking healthy. **At the start of a session run `pwd` (Bash) once and use that
> result.** If it differs from the literal above, the literal is stale — fix it here in the
> same turn. The same rule applies to every script under `tools/` (derive paths from `__file__`).

| Logical Name | Actual Path (relative to workspace) |
|---|---|
| LLMWiki Root | `Vicoding管理平台/LLMWiki/` |
| AGENTS.md | `Vicoding管理平台/LLMWiki/AGENTS.md` |
| Workflow Spec | `Vicoding管理平台/LLMWiki/wiki/project/vibecoding-workflow.md` |
| Wiki Index | `Vicoding管理平台/LLMWiki/wiki/index/index.md` |
| Wiki Log | `Vicoding管理平台/LLMWiki/logs/log.md` |
| Decisions (ADR) | `Vicoding管理平台/LLMWiki/wiki/decisions/` |
| Lessons | `Vicoding管理平台/LLMWiki/wiki/lessons/` |
| Modules | `Vicoding管理平台/LLMWiki/wiki/modules/` |
| API Docs | `Vicoding管理平台/LLMWiki/wiki/api/` |
| People | `Vicoding管理平台/LLMWiki/wiki/people/` |
| Standards | `Vicoding管理平台/LLMWiki/wiki/standards/` |
| Guides | `Vicoding管理平台/LLMWiki/wiki/guides/` |
| Architecture | `Vicoding管理平台/LLMWiki/wiki/architecture/` (single source of truth: `DeviceControlArchitecture.md`) |
| **Code Map** | `Vicoding管理平台/LLMWiki/wiki/architecture/CodeMap.md` — **代码地图：文件↔功能↔wiki 对应表**。Phase 0.0 必读，Phase 3.6 必更新 |
| Tool Scripts | `Vicoding管理平台/LLMWiki/tools/` —— **24 个脚本**，按用途分组（⛔ 全部由 `__file__` 推导路径，可在任意 CWD 运行）：<br>· **扫描（Phase 4 必跑 8 个）**：`wiki_audit.py` / `wiki_format.py` / `ingest_purity_scan.py` / `lint_scan.py` / `drift_scan_precise.py` / `rules_check.py` / `skill_pointer_check.py` / `raw_asset_check.py`<br>· **索引**：`wiki_index_build.py` / `wiki_route_rebuild.py` / `wiki_route_slim.py`<br>· **日志与历史**：`wiki_log.py`（⛔ **log 截断的唯一入口** = `wiki_log.py truncate`）/ `wiki_log_tidy.py`（排序 / 表头修正 / 索引；其 `truncate` 仅委托 `wiki_log.py`）<br>· **治理（先合并后新建）**：`adr_new.py` / `lesson_new.py` / `rules_new.py`<br>· **规范化**：`wiki_normalize.py` / `wiki_narrative_strip.py` / `wiki_narrative2.py` / `wiki_skeleton_clean.py`<br>· **结构**：`wiki_split.py` / `wiki_toc.py`<br>· **ADR 状态**：`check_adr_status.py`<br>· **出包**：`backup_adaweld.py`（⚠️ 在 `tools/` 外，见 Phase 2.1 / 3.7） |
| Raw Skills | `Vicoding管理平台/LLMWiki/raw/skills/AdaWeldsys_Skills/` |
| C# Style Guide | `Vicoding管理平台/LLMWiki/raw/skills/AdaWeldsys_Skills/04-Style/CSharpStyle.md` |
| History | `Vicoding管理平台/LLMWiki/raw/history/history.md` |
| Code Project | `AdaWeldSystem/AdaWeldSystem.csproj` |
| Code Root | `AdaWeldSystem/` |
| Vendor Docs (Delta) | `Vicoding管理平台/LLMWiki/raw/delta/` (**台达 EtherCAT 权威资料**：`EtherCAT_DLL_API清单.txt` = 832 条 API 声明 · `EtherCAT_DLL_Err.cs` 错误码表 · `运动控制模块开发文档_台达版.md` · `台达EtherCAT_PVT与电子凸轮运动开发指南.md`) |
| Vendor Docs (Others) | `Vicoding管理平台/LLMWiki/raw/<vendor>/`（如 `mecavision/`）；提炼页在 `wiki/guides/<Vendor>-*.md` |

> **⚠️ 厂商 API 检索顺序 (2026-09-24 教训)**：查某厂商设备的能力/状态接口时，
> **先 `ls`/`find` 列 `raw/<vendor>/` 的「全部」文件类型**，并读 `wiki/guides/<Vendor>-*.md`，
> 再看代码里的 native 封装 —— **不得只按代码扩展名（如 `**/*.cs`）Glob**。
> 2026-09-24：找台达「运动停止判定」指令时只 Glob 了 `*.cs`，漏掉
> `raw/delta/EtherCAT_DLL_API清单.txt`（832 条），于是把通用 `Motion_Get_Mdone` 当成专用判据、
> 险些自行编造判定方式，被业主纠正。台达**每种运动各有专用状态接口**：
> 点位 `CSP_Get_SoftTargetReach_Status`/点位待到位 `Motion_Set_Command_Wait_Target_Reach` ·
> 缓冲 `CSP_Start_MotionBuffer_Check_MotionDone` / `..._Get_Motion_Status` · PVT `CSP_Start_PVT_Get_Information` ·
> 回零 `Home_Status` · ECAM `CSP_Start_ECAM*_Get_Status` · 当前模式 `Motion_Get_MoveMode`。

> **⚠️ This skill is ahead of the wiki spec page (2026-09-03)**: `wiki/project/vibecoding-workflow.md`
> has not yet absorbed Step 2.6 (no-compiler → Python static verification).
> When this skill and that page disagree, **this skill wins**, and Phase 3 Ingest should bring
> the wiki page up to date.

## Trigger Conditions (Forced Match)

When the user inputs any of the following, this skill **must** be triggered:
- `/vibeCoding` or `/vibecoding` (case insensitive)
- Explicit development need: "develop a feature", "implement a requirement", "create a module"
- Explicit fix need: "fix a bug", "solve a problem"
- Explicit optimization need: "optimize a feature", "refactor code"

## Execution Priority (Forced)

Upon receiving `/vibeCoding` or equivalent intent, **do not** start coding directly or freely read files. Execute in this order:

1. **Read A 层 Key Rules (forced step 1)**:
   - Path: `wiki/rules/KR-001 ~ KR-013`（编号唯一权威 = `wiki/rules/Rules-Index.md`）
   - Action: **必须用 Read 工具把 13 条规则页全部读完**（每页 ≤45 行）—— 清单表只是路由，**规则正文在规则页**
   - If not found: log error and stop, prompt user "LLMWiki Key Rules missing, cannot execute /vibeCoding"
   - ⛔ **不得跳过本步直接进 Phase 0**（详见「## 0. Reading Order」）

2. **Read LLMWiki workflow spec** (forced step 2):
   - Path: `Vicoding管理平台/LLMWiki/wiki/project/vibecoding-workflow.md`
   - Action: **must use the Read tool to read the full content**
   - If not found: log error and stop, prompt user "LLMWiki workflow file missing, cannot execute /vibeCoding"

3. **Read AGENTS.md supplementary rules** (forced step 3):
   - Path: `Vicoding管理平台/LLMWiki/AGENTS.md`
   - Action: Read the `/vibeCoding Workflow (LLMWiki Native)` section

4. **Execute Phase 0~4 strictly** (forced step 4):
   - Follow `vibecoding-workflow.md` Phase 0 -> Phase 1 -> Phase 2 -> Phase 3 -> Phase 4
   - **Each Phase must be executed Step-by-Step** (Step 0.1 -> 0.2 -> ... -> Step 4.x)
   - After each Phase, report results to user, get confirmation before proceeding
   - **B 层内容知识（标准 / 决策 / 教训）在 Phase 0 按需检索**，⛔ 不预读整类

5. **Use TaskCreate/TaskUpdate for phase tracking**:
   - Create a task for each Phase before starting it
   - Mark task as `in_progress` when starting, `completed` when done

6. **Step-Level Display Rule (FORCED, Non-bypassable)**:
   - **Every Step must be explicitly shown to the user** with its number, name, and output
   - Display format: `### Step X.Y: StepName` followed by a concise output summary
   - **PROHIBITED**: Only showing Phase-level summaries without Step-level breakdown
   - **PROHIBITED**: Collapsing multiple Steps into a single line or summary
   - **PROHIBITED**: Executing Steps silently (reading files / checking constraints) without showing what was done
   - **REQUIRED**: After completing each Step, display the Step number, name, and key findings (files read, constraints found, decisions made, etc.)
   - **REQUIRED**: After completing all Steps within a Phase, show a Phase Summary table BEFORE asking user confirmation
   - **Example of correct output**:
     ```
     ### Step 0.1: Read Index
     - Read `wiki/index/index.md`
  - Related pages found: [[modules/<相关模块>]], [[api/<相关接口>]]

     ### Step 0.2: Read ADR
  - Read `wiki/decisions/ADR-<编号>-<主题>.md`（编号经 `wiki/decisions/ADR-Index.md` 定位）
  - Constraint: <该页「决策」节给出的硬约束>
     ```
   - **Example of WRONG output** (prohibited):
     ```
     Phase 0 complete. Found relevant pages.
     ```

## Phase Quick Reference (Forced Execution)

| Phase | Core Action | Required Wiki Paths | Output |
|---|---|---|---|
| **Phase 0: Query** | Knowledge retrieval + symbol location | `wiki/index/index.md` -> ADR + Lessons + Modules + API + **Grep symbol location** | Knowledge retrieval report |
| **Phase 1: Plan** | Planning & constraint confirmation | Based on Phase 0 results | Coding plan (with knowledge ingest forecast) |
| **Phase 2: Code** | Implementation + impact verification | ADR constraints + Lessons gates + **Grep impact tracing** | Code files + **backup 包（改码前回滚点）** |
| **Phase 3: Ingest** | **Forced knowledge deposition** + **出 output 包** | Update `wiki/modules/`, `wiki/api/`, `wiki/decisions/`, `wiki/lessons/`, `logs/` | Updated Wiki + **output 包（定稿后现场验证）** |
| **Phase 4: Lint** | Health check + code drift | Scan contradictions + orphan pages + red links + **Grep code drift** | Health report |

## Page Format Contract (Forced — 2026-10-30)

> **唯一规范 = `wiki/standards/WikiPageFormatSpec.md`**，由 `tools/wiki_format.py` 机械校验（Phase 4 必跑，违规非零退出）。

**Four hard rules** (violating them is a Phase 4 failure):

1. **ADR / lessons growth is 「merge first, create second」** — before writing a new page, run
   `python tools/adr_new.py check <keywords>` / `python tools/lesson_new.py check <keywords>`.
   On a hit, **merge into the existing page** (ADR adds an 「演进记录」 entry; lessons adds an
   「追加条目」 entry) — **do not create a new page**. New ADR number = `ADR-Index` max+1 (now **079**).
2. **Detailed narrative belongs ONLY in `logs/log.md`** — ADR / lessons / index pages carry
   *conclusions and constraints only*. Verification process (static N/N passes, probe measurements,
   trial-and-error history, date-by-date evolution) goes to the log via `python tools/wiki_log.py append`.
3. **index.md is script-generated** — never hand-edit its category tables or the 场景速查路由 table
   (route source = `tools/data/routes.tsv`; rebuild with `python tools/wiki_index_build.py` and
   `python tools/wiki_route_rebuild.py`).
4. **Format violations are Phase 4 failures** — `python tools/wiki_format.py` must exit 0.

**Reusable script toolchain** (all under `tools/`, paths derived from `__file__`, runnable from any CWD):

| Script | Purpose |
|---|---|
| `wiki_format.py` | Format contract validation (the fifth scanner) |
| `wiki_index_build.py` | Rebuild `index.md` skeleton + category tables from page frontmatter |
| `wiki_route_rebuild.py` | Rebuild the 场景速查路由 table from `tools/data/routes.tsv` |
| `wiki_log.py` | Append a log entry (timestamp taken by script — never hand-typed); **the sole entry point for log truncation** (`truncate` → archives to `logs/backup/` + rebuilds `logs/INDEX.md`) |
| `wiki_log_tidy.py` | Sort / fix headers / build the archive index (`index`); its `truncate` only delegates to `wiki_log.py` |
| `wiki_normalize.py` | Normalize ADR & lessons frontmatter + section skeleton |
| `wiki_split.py` | Split oversized lesson pages by topic |
| `wiki_toc.py` | Generate section navigation for oversized pages |
| `adr_new.py` / `lesson_new.py` | Merge-check / merge-append / number allocation helpers |

**Execution environment** — see `wiki/guides/ExecutionEnvironment.md`. Key facts: the `python` on PATH is a
**0-byte WindowsApps placeholder (unusable)** → always call `D:\ProgramData\miniconda3\python.exe`;
**Bash is broken** → use PowerShell + the Glob/Grep/Read tools; `& $py x.py > out.txt` writes UTF-16 →
use `2>&1 | Out-File -Encoding utf8`.

## Key Rules (Forced, Non-bypassable) —— A 层规则正文在哪

> **⛔ 规则正文在知识库，不在 Skill（2026-10-30 下沉 · 2026-11-02 收敛为纯流程类）**
> 现为 **`wiki/rules/KR-001 ~ KR-013`**（编号唯一权威 = `wiki/rules/Rules-Index.md`）。
> **为什么下沉**：① 页会重编/拆分/合并，写死在 Skill 里必然漂移，且失效后**比没有更危险**（读者以为那是权威）；
> ② 无法被 index 路由到（AI 读 index 时看不到它）；③ 无固定格式，无法机械校验。
> **现在 Skill 只写机制**：规则正文与判据在 wiki/rules，**每次现查**，不复制、不缓存。

> **⚠️ rules/ 的边界（2026-11-02 收敛）**：`wiki/rules/` 只收**流程执行类**规则 —— 规定「AI 跑这个
> 工作流时该怎么做」（执行顺序 · 步骤展示 · 检索门禁 · Ingest 强制 · 出包时机 …）。
> **约束代码 / 知识库内容本身**的规则（csproj 注册 · 行尾守恒 · 锚点构造 · 并发 Edit ·
> 零消费≠死成员 …）**不在 rules/**，在 `wiki/lessons/`（踩过的坑）与 `wiki/standards/`（格式规范）。

### 怎么查规则（三步）

1. **`wiki/index/index.md` 第十二节「流程规则」** —— 每行一条规则，含一句话摘要与页链接。
2. **`wiki/rules/Rules-Index.md`** —— 编号唯一权威（`KR-001~KR-013` 连续）+ 主题 → 页的路由表。
3. **读该规则页** —— 固定结构：适用范围 / 规则正文 / 判据 / 反例 / 相关页面。

### 按主题速查（主题 → 规则号；⛔ 非穷举，完整表见 Rules-Index）

| 主题 | 规则号 |
|---|---|
| 执行顺序 / 步骤展示 / 检索门禁 / Skill 权威顺序 | KR-001 ~ KR-005 |
| 知识沉淀 / 决策记录 / 时间戳 | KR-006 ~ KR-008 |
| 代码定位 / 验证诚实性 | KR-009 · KR-010 |
| 出包时机 / Skill 双副本 / Skill 指向 | KR-011 ~ KR-013 |

> **要技术判据（代码 / 脚本 / 行尾 / 编码 / 锚点）不查本节** → 走 `wiki/lessons/`（index 第五节定位）。

### 技术契约（不随页重组而变，可直接遵守）

这些是**编译期 / 语言期事实**，写在 Skill 里不会漂移：

| 领域 | 纪律 |
|---|---|
| 资源释放 | 用 `DisposeComponents()`；⛔ 任何 `.cs` 文件都**不得**新增或重写 `Dispose(bool)`；⛔ 不得修改 Designer.cs 的 Dispose |
| 语言版本 | **C# 7.3**：禁 auto-property initializer、禁 expression-body property、禁 `switch` 表达式、禁 property pattern、禁 nullable reference types、禁 `init`、禁 `record`、禁 range operator、禁 `using` 声明。**允许**：`out var`、元组、`nameof()`、`$""` 插值、`??`、`?.`、`=>` 表达式体、`readonly struct`、`async/await` |
| 插值陷阱 | ⛔ 不要在 `$""` 里用 `{expr:format}`（如 `{dt:yyyy-MM-dd}`）—— 先取到局部变量，否则本项目编译环境报 CS1739 |
| 设计器 | `InitializeComponent()` 内**不得**出现 `for` / `while` / `if` / `switch` / `foreach` —— 展开成逐条语句 |
| 代码定位 | ⛔ 不用 code-graph 工具（2026-08-19 已废止）；用 Grep（Step 0.7 / 2.5） |
| 配置访问 | 配置读静态项必须经 `WeldParamManager`；⛔ 不得直接读配置类静态成员 |
| 新文件 | 新建 `.cs` 必须注册进 `.csproj`（`<Compile Include=...>`），**按条目逐个验证路径存在**，⛔ 不用文件名 grep 判断 |

### 新增 / 演进规则（脚本化）

```bash
python tools/rules_new.py check <关键词>                                  # 合并检查（先合并后新建）
python tools/rules_new.py merge KR-NNN "主题" "变更" "理由" "影响"          # 追加「演进记录」
python tools/rules_new.py new <slug> <标题> "一句话规则" "正文" "判据"      # 新建（须先过 check）
python tools/rules_check.py                                               # 校验：编号连续 / 结构契约 / 索引一致 / 判据非空
```

⛔ **同主题的补充一律合并进既有页**（追加「## 演进记录」），**不新建页**；⛔ 新号 = `Rules-Index` 中 `max+1`，**废止不回收编号**。
⛔ **内容类规则（约束代码 / 知识库内容本身）不进 rules/** —— 归 `lessons/` / `standards/` / `decisions/`。

## Where to Find Constraints (Mechanism, Not a Hardcoded List)

> **⛔ 本节不写死任何 ADR / lesson 页名** —— 页会重编、拆分、合并（2026-10-30 治理轮就把判据库拆成 7 页、相机教训拆成 5 页）。写死的清单必然漂移，且漂移后**比没有更危险**（读者以为那是权威）。
> **正确做法**：⛔ 不要在本 Skill 里维护 ADR/lesson 清单；✅ **每次现查**。

### 查约束的三步（Phase 0 强制执行 —— B 层按需）

1. **读 `wiki/index/index.md` 的「⚡ 场景速查路由」** —— 每行 = 一个任务场景 → 直接该读的 1~3 页 + 硬约束提示。**命中即开工，无需扫全表**。
2. **按场景命中 ADR 约束** —— 读 `wiki/decisions/ADR-Index.md`（编号唯一权威，`001~078` 连续）按主题定位，再读该 ADR 页。
3. **按场景命中教训门禁** —— 读 `wiki/lessons/` 下与该场景相关的页（index 第五节列出全部教训页及其一句话职责）。

⛔ **只读命中的页** —— 39 页 lessons + 78 页 ADR 全读会耗尽上下文并淹没真正命中的那几条。

### 通用纪律（技术契约，与页名无关，长期有效）

✅ 完整技术契约表见本文「Key Rules (Forced, Non-bypassable)」段的「技术契约」小节（**全篇只此一份**）——
编译期 / 语言期事实，不随 wiki 页重组而变，可直接遵守。

### 需要具体约束时怎么办

⛔ **不要凭记忆**断言某个 ADR 号讲了什么（号会变、内容会迁）。
✅ 现查：`wiki/decisions/ADR-Index.md`（主题 → 号）→ 读该页的「决策 / 后果」。
✅ 拿不准就问用户，或跑 `python tools/adr_new.py check <关键词>` 检索同主题页。

## Phase 0: Query -- Forced Knowledge Retrieval (Detailed Steps)

> **REMINDER**: Must display each Step (0.1 ~ 0.7) with its number, name, and output. Do NOT collapse into a single summary.

### 规则门禁（先于 Step 0.0 —— A 层强制预读）

- **Action**：读 `wiki/rules/Rules-Index.md` → **把 13 页规则正文全部读完**（每页含「适用范围 / 规则正文 / 判据 / 反例」）。
- **为什么在 Phase 0 之内**：Phase 0 的每个 Step 都要按规则办事（Step 0.0 怎么定位、Step 0.2/0.3 查哪几页、Step 0.7 怎么 Grep）—— **规则先读，才知道每个 Step 怎么做**。
- **⛔ 不得只读 Rules-Index 的清单表就往下走** —— 清单是路由，判据在规则页。
- **Output**：本轮生效的流程约束清单（哪几条规则在管本轮任务 → 各自怎么遵守）。

### Step 0.0: Consult the Code Map (Forced, precedes every other lookup)
- **Action**: Read `Vicoding管理平台/LLMWiki/wiki/architecture/CodeMap.md` (the **overview** — one page, code memory). Read `CodeMap-Files.md` (detail pagination) only when per-file lookup is needed.
- **Purpose**: **Build code memory; stop re-scanning the whole tree.** CodeMap is split into two layers:
  - **Overview `CodeMap.md`**: 6 "function-domain memory cards" (entry → flow → Manager → device = main dependency direction) + requirement quick-lookup + location traps. **Read this page once to build the mental model of code and dependencies** — no full-tree Grep needed.
  - **Detail `CodeMap-Files.md`**: 49 namespaces / 166 files, one-line responsibility + state markers + dependency/history archive. Consult only for "which namespace is file X in / is it ⛔ or ⚠️".
- **⛔ Grep timing hard constraint (added 2026-11-17 after owner feedback)**:
  - Phase 0: read the overview to build memory first; on hit go **straight to Step 0.7** and read the specific code block.
  - ⛔ **NEVER start Phase 0 with a broad keyword Grep over the whole `AdaWeldSystem/` tree** (e.g. scanning Chinese semantic terms across all files) — this is the exact behavior that made CodeMap useless.
  - Step 0.7 Grep MUST carry a **concrete symbol name** and a path narrowed to the 1–3 files/dirs CodeMap identified. Whole-tree Grep is a fallback **only on CodeMap miss**, with the reason stated in the report.
  - **Multi-level impact Grep (Step 2.5) only in Phase 2 (coding)**, not during Query.
  - For dependency candidates run `python tools/codemap_deps.py --module <dir>` (read-only; never auto-writes Wiki).
- **Rules**:
  1. On a hit, go straight to Step 0.7 and read exact line ranges. ⛔ Do not scan the tree.
  2. On a miss, fall back to Steps 0.1–0.5 as usual.
  3. Line numbers in CodeMap are a **snapshot** — always re-confirm via Step 0.7 Grep before editing.
  4. **"Not implemented" has three distinct meanings**: (a) no code at all; (b) code exists but has **no consumer**; (c) code exists as a **placeholder returning a constant**. Each needs a different response; conflating them is the single most expensive error this map prevents.
  5. Also read the overview's 「易踩的定位陷阱」 — real misjudgements (e.g. `LineLaserSeamResult` is a `struct`, so a `class X` Grep reports zero hits).
- **Output**: a located candidate set (function domain → entry file → main dependency chain → related wiki pages) that narrows Step 0.7 from 166 files to 1–3.

### Step 0.1: Read Index (Forced)
- **Action**: Use Read tool to read `Vicoding管理平台/LLMWiki/wiki/index/index.md`
- **Purpose**: Quickly locate Wiki pages relevant to the current requirement
- **Output**: List related module pages, API pages, decision records, lesson records

### Step 0.2: Read Decision Constraints ADR (Forced)
- **Action**: Read the ADRs related to the involved modules — **先读 `wiki/decisions/ADR-Index.md`**（编号唯一权威 + 每条主题）定位，再读命中的 ADR 页。⛔ 不要凭记忆记 ADR 号（编号会重编）。
- **Purpose**: Get hard constraints -- these are deliberate architecture choices that must be followed
- **Output**: Decision constraint checklist (must follow, or explicitly override and record new ADR)

### Step 0.3: Read Historical Lessons (Forced)
- **Action**: Read the lessons pages relevant to the involved modules — **先读 `wiki/index/index.md` 第五节**（列出全部教训页及一句话职责）定位，再读命中的页。⛔ 不要凭记忆假设页名（本库教训页会拆分/合并，2026-10-30 治理轮就把 3 个超大教训页拆成了 11 个）。
- **Purpose**: Get gate check items -- these are pitfalls others have hit, must confirm avoidance
- **Output**: Historical lesson gate checklist (must confirm avoidance before coding)

### Step 0.4: Read Module Architecture (Forced)
- **Action**: Read the module pages for the involved modules (locate them via `wiki/index/index.md` 第二节)
- **Purpose**: Understand module boundaries, core files, collaboration, known issues

### Step 0.5: Read API Context (Forced)
- **Action**: Read the API pages for the involved modules (locate them via `wiki/index/index.md` 第三节)
- **Purpose**: Understand existing public interfaces, avoid reinventing or breaking contracts

### Step 0.6: Read History (Optional but Recommended)
- **Action**: 按「查什么」选载体，⛔ 不要凭记忆：
  | 要查 | 去哪 | 怎么查 |
  |---|---|---|
  | 项目演进史（跨版本） | `raw/history/history.md` | 按时间分段检索（只读原始层） |
  | 本库治理历史（改页 / 编号 / 脚本） | `logs/INDEX.md` | 定位到某天 → 读 `logs/backup/log_YYYY-MM-DD.md` |
  | 本轮刚做了什么 | `logs/log.md` 顶部 | 直接读第一条 |
- **Purpose**: Prevent new features from conflicting with historical ones
- **Note**: 历史链路见本文「Log & History Chain（日志与历史记录链路）」

### Step 0.7: Symbol Location via Grep (Default)
- **Action**: Locate involved symbols in code with Grep, then map file + line ranges:
  1. `Grep(pattern="<key symbol>", path="AdaWeldSystem/", output_mode="content", -n=true)` -- locate symbol definitions & usages
  2. Review matched lines to understand call relationships (callers/callees)
  3. For cross-file call chains, trace manually: search each caller symbol recursively (N-level)
  4. **MANDATORY cross-validation (2026-09-01)**: A single Grep result set **can be silently truncated** with no warning. When the goal is to enumerate **all callers/consumers** (e.g. "which files use this type"), you MUST run **at least two independent searches** with different patterns and confirm the file sets match. Narrow the pattern first (add `\b` word boundaries, drop substring-overlapping alternatives like `FaultRecord` vs `FaultRecordManager`), and re-Grep per-directory as a backstop if consumers are known to cluster in one folder. See the 「项目工具」guides 页（locate via index 第六节）相关小节.
- **Purpose**: Supplement LLMWiki architectural knowledge with code-level call relationships that Wiki does not cover
- **Output**: Code-level relationship report (callers, callees for involved symbols)
- **Note**: This is the default (pre-code-graph) method -- the code graph tool has been retired.

> **⚠️ Truncation incident (2026-09-01)**: migrating `FaultRecoveryManager`, the first Grep reported **2** consumers; a second narrower Grep revealed **6**. Four files (`LineLaserWorkflow` / `MonitorCameraWorkflow` / `MotionControlWorkflow` / `WeldParamControlWorkflow`) would have failed to compile. Never trust a single Grep for completeness.

## Phase 1: Plan -- Planning & Constraint Confirmation (Detailed Steps)

> **REMINDER**: Must display each Step (1.1 ~ 1.5) with its number, name, and output. Do NOT collapse into a single summary.

### Step 1.1: Requirement Parsing
- Summarize user core need in one sentence
- Confirm involved modules and boundaries

### Step 1.2: Change Scope Planning
- **First check the CodeMap's 「模块归属」 column** for each target file: it names the owning module, so you can confirm the change stays in bounds before touching anything (mirrors the Module Change Scope Control table below).
- Compare with module boundaries in `wiki/modules/`, clarify modification and addition scope
- Follow minimal change principle

### Step 1.3: Identify New Decisions (ADR Forecast)
- Determine if coding involves new architecture choices
- If yes, flag for Phase 3 to create new `wiki/decisions/ADR-XXX-{Title}.md`

### Step 1.4: Identify Knowledge Ingest Points
- Forecast Wiki pages to update or create after coding
- Module docs? API docs? New ADR? New Lessons?

### Step 1.5: Skill Reference (Demoted to Auxiliary)
- For specialist role details, read `raw/skills/` corresponding Skill files
- **Note**: Skill files are reference, not command source. All coding decisions based on LLMWiki query results.

## Phase 2: Code -- Coding Execution (Detailed Steps)

> **REMINDER**: Must display each Step (2.1 ~ 2.6) with its number, name, and output. Do NOT collapse into a single summary.

### Step 2.1: Project Backup（**只出 backup 包** · 每天至多一份，按天去重）
- **⛔ 本 Step 只负责 backup 包，output 包一律不在这里出** —— output 已挪到 **Step 3.7**（详见下方「为什么 output 不在 Step 2.1」）。
- **备份频率**：每天最多生成一份 `AdaWeldSystem_backup_YYYYMMDD_HHMMSS.tar.gz`（排除 3rdDepend / obj / bin / .vs）。备份前先检查工作区根是否已存在当天（`YYYYMMDD`）的备份；若存在则**跳过**，不重复生成。
- **✅ 唯一正确方式**：运行 `python Vicoding管理平台/LLMWiki/tools/backup_adaweld.py`（**无参数 = 只出 backup**）。脚本按 `__file__` 推导路径，自动完成"当天已存在则跳过 / 不存在则排除 3rdDepend/obj/bin/.vs 打包"，arcname 固定为 `AdaWeldSystem`。路径由脚本自身推导，不依赖当前工作目录，可在任意 CWD 下安全运行。
- **🚫 output 包不得在 Step 2.1 出（2026-10-10 用户纠正）**：Step 2.1 跑在**改码之前**，此刻打出的 output 反映的是本轮改动**之前**的代码 —— 现场拿它验证会验到旧码，验证结论无效。output 的语义是"本轮定稿后的交付物"，只能在 Phase 3 收尾出。详见 **rules/KR-011**。
- **📦 三种产物（代码两包内容范围一致，均排除 3rdDepend/obj/bin/.vs；知识库包排除 __pycache__），触发时机各不相同**：
  | 产物 | 命名 | 触发 Step | 频率 | 用途 |
  |---|---|---|---|---|
  | **backup 包** | `AdaWeldSystem_backup_YYYYMMDD_HHMMSS.tar.gz` | **Step 2.1**（改码**前**） | 每天至多一份，按天去重（当日已存在则跳过） | 日常回滚点 |
  | **output 包** | `AdaWeldSystem_output_YYYYMMDD_HHMMSS.tar.gz` | **Step 3.7**（改码**定稿后**） | 每次必生成，自动清理旧包，目录只留「最新一份」 | **现场验证** |
  | **LLMWiki 知识库包** | `LLMWiki_backup_YYYYMMDD_HHMMSS.tar.gz` | **Phase 3 收尾**（知识库定稿后） | 每天至多一份，按天去重 | 知识库快照（整个 `LLMWiki/`，排除 `__pycache__`） |
  - 命名规则即把 backup 包的 `backup` 前缀换成 `output`，其余（时间戳、排除项、arcname）完全相同。
- **脚本模式参数**：`--backup`（默认，无参数同效）/ `--output`（只出 output）/ `--llmwiki`（只出 LLMWiki 知识库包，落工作区根）/ `--all`（backup+output，兼容旧行为，日常不用）/ `--help`。
  - ⛔ **不要用 `--all` 走流程**：那会退回"改码前就把 output 出了"的旧行为。
- **🚫 禁止手搓 tar，禁用旧"等效 Bash"片段**：旧文档里的
  ```bash
  (cd AdaWeldSystem && tar -czf "../AdaWeldSystem_backup_${TS}.tar.gz" --exclude=bin --exclude=obj .)
  ```
  有三个致命缺陷，正是此前错误备份（把 3rdDepend/.vs 打进去、arcname 变成相对 `./`）的直接成因：
  1. **排除项不全**：只 `--exclude=bin --exclude=obj`，漏掉 `3rdDepend` 与 `.vs` → 体积虚高且混入不应打包的第三方 DLL / VS 缓存；
  2. **arcname 错误**：`cd AdaWeldSystem && tar .` 使条目以相对路径 `./` 为根，还原时会直接撒到当前目录而非 `AdaWeldSystem/`；
  3. **本机 Bash 不可用**：本机 Bash PATH 已损坏（`tar`/`ls`/`date` 均 `command not found`），该片段在本机根本跑不通。
  任何情况下都不要手搓压缩命令，以 `backup_adaweld.py` 为唯一真理来源。

### Step 2.2: Code Implementation
- **Continuously check** Phase 0 retrieved ADR constraints and Lessons gates during coding
- **When reading code, reuse Phase 0 Step 0.7 Grep-guided reading**: locate target symbols' file + line numbers via Grep, then read exact code blocks with `Read(offset/limit)`, avoiding whole-file reads
- **⚠️ DELETING a `.cs` file is blocked by the safe-delete guard — use the .NET API (2026-09-14)**: `rm`, `cmd /c del`, and Python `os.remove` all fail with `[safe-delete][SAFE_DELETE_BULK_GUARD_ERROR] state lock timeout` (retrying and `dangerouslyDisableSandbox` do NOT help). Use PowerShell instead: `[System.IO.File]::Delete("<abs path>")`. **Always confirm with Glob / `ls` afterwards** — the PowerShell tool may swallow stdout and still report exit 0, so a "successful" result proves nothing. (Relevant whenever a refactor merges/renames files, e.g. two config classes → one.)
- Follow C# code style (read `Vicoding管理平台/LLMWiki/raw/skills/AdaWeldsys_Skills/04-Style/CSharpStyle.md`)
- Minimal change, only modify directly related libraries and UI

### Step 2.3: Code Self-Review
- After implementation, check Phase 0 "Decision Constraint Checklist" and "Historical Lesson Gates" item by item
- **Mandatory Dispose check**: run `grep -rn "protected override void Dispose" --include="*.cs"` and verify that:
  - Designer.cs entries are unmodified (match standard generated pattern)
  - **No `.cs` file (excluding Designer.cs) contains `Dispose(bool)` override**
- Confirm no ADR or Lessons violations

### Step 2.4: .csproj Registration (If New Files Created **or Moved/Renamed**)
- If new .cs files were created, **must** add `<Compile Include="..." />` entries to `AdaWeldSystem/AdaWeldSystem.csproj`
- Use Edit tool to add entries in the appropriate `<ItemGroup>`
- **File moved/renamed → the existing `<Compile Include>` path is now stale.** Update the entry in place. Do NOT assume "the file still exists so the entry is fine" -- the path string is what the build uses.
- **Verification is per-entry existence, NOT grep hits** (2026-09-14 miss): after any add/move/rename, run
  ```python
  import re, os
  txt = open('AdaWeldSystem/AdaWeldSystem.csproj', encoding='utf-8-sig').read()
  incs = re.findall(r'<Compile Include="([^"]+)"', txt)
  miss = [i for i in incs if not os.path.exists(i.replace('\\', '/'))]
  print('missing:', len(miss), miss)   # must be 0
  ```
  A `grep` that merely finds the *filename* somewhere in the csproj proves nothing -- on 2026-09-14 `SeamGuideSample.cs` was moved into `Algorithms/` and the csproj kept the old root path, which passed the grep-based check and still would not compile. Also cross-check the reverse direction (every on-disk `.cs` under the changed folder is registered).

### Step 2.5: Impact Radius Verification via Grep (Default)
- **Action**: After code changes, verify impact scope using manual multi-level Grep tracing:
  1. `Grep(pattern="<changed_public_symbol>", path="AdaWeldSystem/", output_mode="content", -n=true)` -- find all references
  2. Trace each caller recursively (A->B->C: grep B, then grep each caller of B, etc.)
  3. Cross-check: every caller found must be reviewed for compatibility
  4. **Re-run with a different pattern before declaring done** -- Step 0.7's first Grep is exactly the one that got truncated (2 vs 6 consumers). This step is the safety net: do **not** skip it just because Phase 0 already grepped the symbol.
- **Purpose**: Catch indirect call chain breakages (A->B->C: changing B breaks A -- grep B, then grep callers of B to find A)
- **Output**: Impact report (affected files, caller chain depth, any broken references)
- **Note**: Manual multi-level Grep is the default method -- the code graph tool has been retired.

### Step 2.6: Correctness Verification (Forced -- substitutes for compilation)

> **Why**: this sandbox has no C# compiler (rules/KR-010). Never skip verification, never fake a build.

- **Action**: write a throwaway Python verifier; strip XML doc comments **first**; assert the invariants this change was supposed to establish. Iterate the script to a precise version -- first-draft scripts always produce false positives.
- **判据全文库**: `wiki/lessons/` 下的**静态校验判据库**（原 `StaticVerifierJudgements.md` 已于 2026-10-30 按主题拆为多页，现为索引页）。**定位方式**：读 `wiki/index/index.md` 第五节找到判据库索引页 → 按主题进入对应分页（语法/作用域 · 接线完整性 · 校验器失效模式 · 批量脚本陷阱 · 工具受限替代 · ADR 编号）。写新判据前先读对应主题页；出现新的可判定规则时**追加到该主题页**，并在该索引页登记。⛔ 不要在本 Skill 里复制判据正文。
- **How to use the library**: pick the section matching what you changed, implement only those checks, keep the list short. A 20-item generic checklist is not obeyed; a targeted 6-item list is.
- **The three capability classes** (rules/KR-010): *pattern-shaped* defects -> the verifier owns them; *semantic* defects (type-system legality, overload resolution, boxing, name resolution, generic inference, interface completeness) -> **only a compiler settles them**; *wiring* defects (parameter added but never passed, method added but no consumer, config readable/writable but unconsumed) -> need a dedicated check. **A green run never means the build is sound, nor that the feature works.**
- **Prevention rule**: when a compile error appears that a *known* judgement could have caught, add that judgement to the verifier **in the same round** -- a lesson page alone is not enough; the check must live in the check.
- **Before trusting a green run**: print the extracted intermediate values once (a loosened regex can turn a check into a tautology); and if a judgement suddenly reports hundreds of items, suspect the criterion before the code.
- **Cleanup**: delete every `_tmp_*.py` script before finishing.
- **Output**: static-check result table + explicit statement that real compilation is pending in Visual Studio. **Never describe static checks as "build passed".**

## Phase 3: Ingest -- Forced Knowledge Deposition (Detailed Steps)

> **REMINDER**: Must display each Step (3.1 ~ 3.8) with its number, name, and output. Do NOT collapse into a single summary.

**This phase is mandatory, not optional. Coding without Ingest is considered incomplete.**

### Step 3.1: Update Module Docs
- Update `wiki/modules/` pages for involved modules
- Update core file list, module responsibilities, collaboration, known issues

### Step 3.2: Update API Docs
- Update `wiki/api/` pages for involved APIs, or create new pages
- Update public classes/methods/events, interface signatures, usage specs

### Step 3.3: Create or Update Decision Records (ADR)
- If Phase 1.3 forecasted new decisions, create `wiki/decisions/ADR-XXX-{Title}.md`
- **⚠️ ADR 编号的唯一权威 = `wiki/decisions/ADR-Index.md`**（2026-10-30 起已重建为**单张按号排序表**，`001~NNN` 连续无断号；**不再有**历史上的「编号沿革 bullet 列表」与「删除对照表 / 幸存页重排映射」）。
  - 新号 = `ADR-Index` 中 `max+1`；⛔ **废止某 ADR 不回收编号**（避免与其它页引用的号撞车），改为在 ADR-Index 的主题列注明「已废止并入 XXX」。
  - **⛔ 禁止新建带「旧编号」的历史 ADR 页**：旧号语义冲突已通过**正文消歧**解决（旧号 → 现行页），不再保留映射表。
- **⚠️ 登记必须两处同步**（`wiki_audit.py` 会检查 ADR-Index 与 index 的一致性）：
  ① `wiki/decisions/ADR-Index.md` 加一行；② `wiki/index/index.md` 第七节 —— 但 index 的 ADR 表与计数**由脚本生成**（见 Step 3.5），故此处**只需跑脚本**，不要手改。

### Step 3.4: Create or Update Lesson Records
- If new pitfalls were discovered, create/update `wiki/lessons/{Title}.md`
- **⛔ 先合并后新建**（2026-10-30）：先跑 `python tools/lesson_new.py check <关键词>`；命中同族页就**追加「## 追加条目」**（`### 坑 N · 标题（日期）` + 现象/判据/预防），**不新建页**。同族多坑页用 `## 坑 N：` 分节，末尾统一 `## 相关页面`。
- **Pitfall knowledge belongs in LLMWiki, NOT in this SKILL file (2026-10-08)**: on that day Step 2.6 had grown to **17.4 KB of judgement prose inside a single Step** - long enough that the skill had become a lesson library, which contradicts its own core idea that LLMWiki is the single source of truth. Rule: **the SKILL states the *how* and *when*; the wiki carries the *what and why*.** When a compile error yields a judgeable rule, append it to the owning section of the judgement library, and leave a **one-line pointer plus the section name** in the SKILL.
- **⚠️ 判据库会按主题拆分/合并**（原单页 `StaticVerifierJudgements.md` 已于 2026-10-30 拆为多页 + 索引页）。⛔ **不要在本 Skill 里列出判据库的分页清单** —— 那是写死内容，下次拆分即失效。✅ **定位方式**：读 `wiki/index/index.md` 第五节找到判据库**索引页** → 由索引页进入各主题分页。

### Step 3.5: Update Index（**脚本化，勿手改**）
- **⛔ `wiki/index/index.md` 的分类表与速查路由表由脚本生成，禁止手工编辑**（2026-10-30 起）。
  ```bash
  python tools/wiki_index_build.py     # 重建 index.md 骨架 + 各分类表（摘要取自各页 frontmatter）
  python tools/wiki_route_rebuild.py   # 由 tools/data/routes.tsv 重建「⚡ 场景速查路由」表并校验
  ```
- **新建页面后必跑这两个脚本** —— 否则新页不会出现在 index（`wiki_audit.py` 会报「index 缺登记」/ lessons 三处不一致）。
- **路由表源 = `tools/data/routes.tsv`**（每行：`场景描述 \t 目标页链接 \t 硬约束提示(≤80字符)`）。新增场景**改 TSV**，不手改 index。
- **⚠️ 计数三处一致**（`wiki_audit.py` 第 11 项）：目录页数 == index §五表行数 == 摘要 `N 条坑`。脚本已改为**按实际页数动态生成**（ADR 条数、lessons 条数、people 角色数均不硬编码），故只要跑脚本即自动一致。
- **⚠️ 摘要必须短**（≤120 字符）：摘要取自各页 frontmatter `title`；脚本会**自动剥离**日期串与验证叙事词。若某页 `title` 过长或含 `YYYY-MM-DD`，应改该页 frontmatter，而不是加长 index。
- **⛔ 已废止的旧做法**（2026-10-30 治理轮已删除，勿再照做）：① 手工维护 index 的 `## 七` ADR 全量登记表与三处计数；② 手改 ADR 表行。ADR 全量登记表的唯一权威是 `wiki/decisions/ADR-Index.md`，index 只放指针。
- **完整沉淀链路见本文「Knowledge Accumulation Chain（知识积累与沉淀链路）」** —— 三层落位（结论进 wiki / 过程进 log / 原始资料进 raw）+ 沉淀三步（写入 → 登记 → 记录）+ 5 道机械闸门。

### Step 3.6: Update the Code Map (Forced)
- **Action**: update `wiki/architecture/CodeMap.md`
- **Why mandatory**: it is the only by-source-file view of functionality. If it goes stale, the next Phase 0 falls back to a full tree scan — exactly the cost this map exists to remove.
- **Update triggers** (any one hit ⇒ update):
  | Trigger | Action |
  |---|---|
  | a `.cs` added / deleted / moved | add/remove the row; on move or rename also register `RENAMED` in `drift_scan_precise.py` (**plain path, no parenthetical**) |
  | a file's responsibility changed (feature added / placeholder now implemented / consumer count changed) | refresh the 「本文件做什么」 text and the `⛔` / `⚠️` state marker |
  | new requirement landed | add a row to 「需求 → 代码落点速查」 |
  | an ADR changed hardware ownership | update the 「约束 ADR」 column and any hardware-ownership rows |
  | Step 2.6 static verification found new dead code / placeholders | update the corresponding state markers |
- **Boundary**: the CodeMap is a **locator + one-line responsibility + state marker** only. ⛔ Do not expand it into a feature specification — that belongs in `modules/`.

### Step 3.7: Generate the Field-Verification Package (output -- 强制，Phase 3 专属)
- **⛔ 为什么 output 必须落在 Phase 3 而不是 Step 2.1（2026-10-10 用户纠正）**：Step 2.1 跑在**改码之前**，那一刻打出来的包反映的是本轮改动**之前**的代码。现场拿这份包做验证，验的是旧码 —— 结论无效，且比没有包更危险（看起来验证过了）。output 的语义是**本轮定稿后的交付物**，只有走完 Phase 2（实现 + 自审 + 影响面 + 静态校验）之后才成立。
- **Action**：运行 `python Vicoding管理平台/LLMWiki/tools/backup_adaweld.py --output`
  - **每次必生成，不按天去重** —— 当日已有 backup 与本 Step 无关，output 只反映"本轮定稿后的最新代码"。
  - 生成后**自动清理旧 output 包**，工作区根始终只留「最新一份」`AdaWeldSystem_output_*.tar.gz`。⛔ 不要为了省事跳过它，也不要误删唯一的那份 output。
  - 排除项与 arcname 同 backup 包（3rdDepend / obj / bin / .vs，arcname=`AdaWeldSystem`），现场还原后用 VS 重新编译即可部署。
- **⚠️ 交付时必须附带配置同步清单**（本项目已知坑，见 index 第五节「模拟测试」相关教训页）：出包排除 `bin/`，所以 `DeltaMotionConfig.xml` / `LineLaserConfig.xml` **不随包到现场**；凡「代码默认值 + 可被 XML 覆盖」的配置（轴名 `SeamTrackAxisName`、轴地址 `NODE_ID` 等）须逐项列出人工核对值，否则现场仍按旧配置运行、实测机与本地行为不一致。
- **Output**：本轮 output 包的**文件名 + 大小**（写入 Step 3.8 的日志条目，供现场取包核对）。

### Step 3.8: Append Log（**脚本化，勿手改**）
- **⛔ 唯一合法写法 = `python tools/wiki_log.py append`**（时间戳由脚本取，⛔ 禁止手填；条目头格式由脚本保证）：
  ```bash
  python tools/wiki_log.py append <op> "<标题>" --src "<触发来源>" --op-list "操作1; 操作2" --files "<变更文件>" --note "<结论/遗留>"
  ```
  `<op>` 取值示例：`coding` / `governance` / `fix` / `docs` / `refactor`。
- **`log.md` 是 NEWEST-FIRST**（最新在最前）；条目数**上限 50**，超出由 `python tools/wiki_log.py truncate` 截断 —— 旧条目**按日期归档**到 `logs/backup/log_YYYY-MM-DD.md`（⛔ **截断是归档不是丢弃**），并自动重建 `logs/INDEX.md` 归档索引。排序与表头修正：`python tools/wiki_log_tidy.py sort` / `fixhdr`（一次全流程：`all` = sort → fixhdr → truncate → index）。
- **⛔ log 截断入口唯一** = `python tools/wiki_log.py truncate`（`wiki_log_tidy.py truncate` 仅委托它；⛔ 禁自建截断脚本）。
- **知识库包**（Phase 3 收尾）：`python tools/backup_adaweld.py --llmwiki` —— 整库快照落工作区根，每天至多一份（按天去重）。
- **完整链路见本文「Log & History Chain（日志与历史记录链路）」** —— `log.md` → `backup/` → `INDEX.md` → 压缩包，四层由脚本串联，⛔ 不要手工补环。
- **⛔ 已废止的旧做法**（2026-10-30 治理轮已删除，勿再照做）：① 用 Edit 工具手工在 `log.md` 顶部插入条目（历史上多次吃掉上一条的表头、撕裂条目）；② 用 heredoc 追加（会被安全策略拒绝）。
- **⚠️ 详细叙事只进 log**：ADR / 教训 / index 页只留结论与约束（见 Page Format Contract 第 2 条）。
- **⚠️ When superseding an entry's stated follow-up, strike it in place rather than leaving a stale "still pending" line** (e.g. `① ~~old item~~ → **2026-09-14 已处理**`), so the manual stale-content check in Step 4.2 stays clean.
- **⚠️ Write page-link mappings as plain text `api/old → api/new`, not `[[old]]→[[new]]`** — the link regex used to parse the brackets as real links and report red links (2026-09-02). `wiki_audit.py` now masks fenced blocks **and inline code spans** before link parsing (2026-09-03), so a mapping written inside backticks is safe; plain text is still preferred because it survives copy-paste out of the code span.

## Phase 4: Lint -- Health Check (Detailed Steps)

> **REMINDER**: Must display each checklist item with its result. Do NOT collapse into a single summary.

### Step 4.1: Run the Automated Wiki Audit (Forced)
Run the read-only audit script and fix everything it reports:

> **⚠️ Environment traps (2026-09-17, reproduced)** — the `cd … && python …` form below assumes a working shell; on this machine it does not:
> - **Bash is unusable**: `dirname` / `ls` / `grep` / `head` all fail with `command not found` (broken PATH shim). Do **not** burn turns on it — use the Grep / Glob / Read tool APIs for all lookup, and PowerShell only for process/delete work.
> - **PowerShell `>` writes UTF-16, and PowerShell often swallows stdout**: `& $py script.py > out.txt` produces a UTF-16 file that the Read tool rejects ("Cannot display content of binary file"). Use `& $py script.py 2>&1 | Out-File -FilePath out.txt -Encoding utf8` and then `Read` out.txt. For a plain value (e.g. a timestamp), `… | Out-File -Encoding ascii` into a temp file and read it back — the console echo is unreliable.
> - Because the scanners' output is still rendered in the console codepage, Chinese headings can appear as mojibake in the file; the ASCII/数字 parts (counts, `0`, code numbers) remain trustworthy — read those.

> **⚠️ A concurrent session may register a NEW ADR mid-flight (2026-09-17)** — this KB is edited by parallel sessions. If `ADR-Index.md` already shows a higher top number than your working baseline (real case: it read `001~061` because another session added `ADR-061`, while this session was on ADR-035), **align TO the higher number, never roll it back**: `ADR-Index.md` is the sole numbering authority. Concretely: (a) leave the other session's ADR-Index rows alone; (b) add the missing row for their ADR to `index/index.md` §7.1 (this is also what clears the scanner's "orphan page" hit — an ADR present in ADR-Index but absent from index.md is reported as an orphan AND as "registered-in-index missing"); (c) bump all three `index.md` counters to their number (see Step 3.5); (d) append both ADRs to the 编号沿革 clause. Then re-run the scanners — a green run is the acceptance test.

```bash
cd "Vicoding管理平台/LLMWiki" && python tools/wiki_audit.py
```

> **⚠️ The `python` on PATH is a 0-byte WindowsApps placeholder (unusable) — always use the absolute
> interpreter** `D:\ProgramData\miniconda3\python.exe` (or `.../envs/myenv/python.exe`).
> Full environment facts: `wiki/guides/ExecutionEnvironment.md`.

11 automated checks: ① red links ② orphan pages ③ duplicate `index.md` rows ④ ADR number gaps & unregistered ADRs ⑤ page size distribution (pages >600 lines need a TOC) ⑥ duplicate content (3-gram similarity) ⑦ misplaced guide-type pages in `lessons/` ⑧ `standards/` inbound-link stats ⑨ second-level subdirectories under `wiki/` (must be 0 -- all categories are flat `.md` files) ⑩ **over-small categories (<=2 pages -- merge into a related category; only `index/` and `architecture/` are exempt)** ⑪ **lessons 三处一致 (dir count == index §五 table rows == summary `N 条坑` count; non-zero exit on mismatch)**.

**Health criteria**: red links = 0, orphan pages = 0, duplicate index rows = 0, subdirectory count = 0, over-small categories = 0, lessons 三处一致 = yes.

Then run the **fifth scanner** — the format contract (forced since 2026-10-30) — plus the companion scanners:

```bash
cd "Vicoding管理平台/LLMWiki" && python tools/wiki_audit.py && python tools/wiki_format.py && python tools/ingest_purity_scan.py && python tools/lint_scan.py && python tools/drift_scan_precise.py && python tools/rules_check.py && python tools/skill_pointer_check.py && python tools/raw_asset_check.py
```

> **八个闸门必须全绿**（任一非零退出即 Phase 4 不合格）：
> `wiki_audit`（红链/孤儿/计数）· `wiki_format`（格式契约）· `ingest_purity_scan`（**沉淀纯度：赘述不入库**）· `lint_scan`（死链/编号冲突）· `drift_scan_precise`（代码漂移）· `rules_check`（规则页契约）· `skill_pointer_check`（Skill 指向防漂移）· `raw_asset_check`（raw 登记一致）。

- `skill_pointer_check.py` — **Skill 指向防漂移闸门**（2026-10-30 起强制）：⛔ Skill **不得写死内容页名**（具体 ADR / lessons / guides / modules / api 页）——这些页会重编、拆分、合并，写死即失效，且失效后比没有更危险（读者以为那是权威）。✅ Skill 只写**角色级锚点**（`wiki/index/index.md` / `wiki/decisions/ADR-Index.md` / `wiki/architecture/CodeMap.md` / `wiki/project/vibecoding-workflow.md` / `wiki/standards/WikiPageFormatSpec.md` / `wiki/guides/ExecutionEnvironment.md` / `wiki/guides/RawAssetCatalog.md`）与**「去哪查」的机制表述**。判据：C1 无写死内容页 · C2 无红链 · C3 工具脚本存在 · C4 ADR 号有效 · C5 无内容清单表。

- `wiki_format.py` — **page format contract** (per `wiki/standards/WikiPageFormatSpec.md`): index limits &
  route-column rules, ADR frontmatter/title/number consistency, lesson section structure, per-category
  line limits (single-decision ADR ≤200 lines, combined ADR ≤300, single-lesson ≤250, multi-lesson ≤700),
  log entry count (≤50) / reverse-chronological order / entry format. **Violations exit non-zero.**
  "建议"-level findings are informational and do not block.
- `ingest_purity_scan.py` — deposit purity: index / ADR-Index / CodeMap / architecture pages must not
  carry verification narrative (静态 N/N · 阴性对照 · 回滚点 · 探针), date-by-date evolution, or log-style dumps.
- `lint_scan.py` — dead links / orphan pages / ADR number conflicts / broken external file links. The hits in the workflow spec page are template placeholders (`modules/XXX`, `decisions/ADR-XXX`) and are expected.
- `drift_scan_precise.py` — wiki pages citing `.cs` files that no longer exist. **Current baseline (2026-09-03, re-measured 17:50): 0 pending, 16 annotated** — i.e. every surviving stale name now carries an explicit `（现役 X.cs）` / `（已移除）` note, or sits in a `历史名称提示` banner block on a historical ADR page. Re-measure before quoting this number; it moves as pages are annotated.
  - The scanner triages each hit into `RENAMED` / `REMOVED` / `EXTERNAL` (external reference projects such as `PcomDeviceInterface/`, `HonorMachineTest/`) / `SPECULATIVE` (proposed or demo files that never existed). Only the first two count as pending.
  - **A `历史名称提示` banner block (`> ⚠️ 历史名称提示` …) is itself exempt** — its `>` lines deliberately enumerate old names, so judging them again is self-inflicted noise.
  - **Your change must introduce 0 new drift** — verify by grepping the output for the pages you touched. **If every remaining pending hit belongs to files you never touched, they are ANOTHER session's in-flight work** (this KB is edited by parallel sessions) — **report them in the delivery, do NOT "fix" them**, or you will collide with a refactor still in progress. 2026-09-14: 4 pending hits (`RSICommunication.cs` / `EKICommunication.cs` / `KUKARobotManager.cs` / `TCPIPComm.cs`) all traced to a concurrent `Comm/` refactor, zero from that round's change.
  - If you must annotate by hand: keep the old name verbatim and append the note; **do not blind-substitute** the old name away (an earlier attempt produced broken text such as `Sub2UI/UIDesign/TabPage/ILCamPage.cs` and rewrote files in external projects).
  - **⚠️ Deleting code files = register them in the `REMOVED` table first (2026-09-08)**: `drift_scan_precise.py` only applies the "already annotated" (行内已标注 / 页面历史横幅) test inside the `elif fname in REMOVED:` branch. A deleted-but-unregistered name falls through to the `else` branch and is reported as **「未登记的新漂移」** — and annotating the historical pages does **nothing** to clear it. So after physically deleting files: add every deleted `Xxx.cs` to `REMOVED` with a one-line reason, *then* re-run the scanner. (Case in point: ADR-014 deleted 15 files; 22 hand annotations across 4 pages still reported 21 pending until the names were registered → dropped to 0 immediately.)
  - **⚠️ Pages moved into an archive dir are still scanned (2026-09-08)**: `wiki_audit.py` / `lint_scan.py` walk the whole wiki root, so a `_trash_YYYYMMDD/` folder's `[[...]]` links still count as red links and its pages still count as orphans. De-link (`[[X]]` → `X`) or delete the references before finishing.

> **Tooling rule (2026-09-03)**: every script under `tools/` must derive its paths from `__file__` (see `wiki_audit.py`). Never hardcode an absolute path — after a machine migration a hardcoded path makes a scanner report "0 files" and look healthy.

### Step 4.2: Manual Checklist
- [ ] **Contradiction detection**: Do new Ingested contents conflict with existing wiki pages?
- [ ] **Stale detection**: Did code changes overturn old design decisions?
- [ ] **Bidirectional links**: Do related pages reference each other?
- [ ] **Code drift**: Do `wiki/modules/` descriptions match current code? Use Grep to spot-check: search key symbols/modules described in Wiki, confirm presence & usage in code. Manually identify dead symbols or oversized functions when refactoring candidates matter (code graph retired, no graph tool needed).
- [ ] **CodeMap validity**: spot-check that the file paths in `wiki/architecture/CodeMap.md` still resolve — **per-entry `os.path.exists`, never a filename grep** (same lesson as Step 2.4). A `.cs` added / moved / deleted without a matching CodeMap update is drift: fix the map, not just the prose.
- [ ] **Verify before correcting stale docs**: when a wiki page names a file/type/component, **confirm existence with `find` / Glob first**. Pages may describe entities that were deleted (or still-existing ones as deleted). Never do blind text substitution of version labels.
- [ ] **Before merging or deleting a category directory**: measure pages / lines / inbound-link count for each candidate. The archived-semantics directory must never absorb the current normative page. Checking inbound-link distribution first often exposes duplicate pages (e.g. a second parallel architecture page) worth folding in at the same time.

### Step 4.3: Knowledge-base Hygiene Sweep (2026-09-12, run on the periodic full audit)

The automated scanners only see `[[links]]` and `.cs` names — they are blind to **junk that was never a link**. Run these when the user asks for a full KB audit/cleanup (not every coding round):

- [ ] **No non-Markdown under `wiki/`**: `find wiki -type f ! -name "*.md"` must be empty.
- [ ] **No leftovers anywhere**: `_tmp_*` (both `.py` **and** `.txt`), `*_out.txt`, `*.pyc`, `__pycache__/`, `*.bak`, `*~`, `*.orig`. **Also sweep the workspace root and the `LLMWiki/` root by name prefix** — the three scanners' console redirections (`_tmp_audit.txt` / `_audit_out.txt` / `_drift_check.txt` / …) are `_`-prefixed scratch that no link-based scanner can ever see.
- [ ] **A log/handover line that says「已删除」is not proof — Glob the path first (2026-09-21)**: a prior session may have written the deletion into `logs/log.md`, listed the filenames in `drift_scan_precise.py` REMOVED, and updated `软件设计文档.md` — while the files were still sitting on disk. Before treating any pending-deletion item as closed, `Glob` / `Test-Path` the exact path; if it still exists, delete it and record the discrepancy.
- [ ] **No build output under `raw/`**: a vendor SDK archive must not carry `bin/` `obj/` or demo `.exe/.pdb/.tds`. Clean by extension whitelist + directory name, **dry-run the size table first and re-count source files afterwards** — never blanket-delete a vendor archive (keep `SDK/` `Drivers/` `Document/` and all demo *sources*).
- [ ] **No 0-byte / empty directories**: `find <dir> -type d -empty`.
- [ ] **Before trimming a vendor archive by language/directory, locate the SOLE truth source (2026-09-14, 坑十)**: the only C/C++ header set and API declarations often ship **inside one language's demo folder** (e.g. `Demo/VC++/Include/CameraApi.h`) while the vendor `SDK/` carries no `.h` at all. Steps: (a) extension-distribution scan of the to-be-deleted vs. to-be-kept trees; (b) **cross-directory md5 de-dup** for `.h/.hpp/.idl/.proto/*.pdf/*.chm` to see whether a copy survives elsewhere; (c) verify real file type (`head -c 2` ≠ `MZ`/`PK` — suffixes lie; `.Interface` was a PE binary, not a header). **Extract-then-delete beats blanket delete**: relocate the declaration set to a semantic folder (`SDK/Include/`) and md5-verify each file. Only delete when you can state per item that nothing irreplaceable is lost.
- [ ] **Retired tools have no physical files left** — retiring a tool means deleting its script too, not only tombstoning the doc page.
- [ ] **Every row of `index.md`「来源索引」resolves**: `os.path.exists(path) == True` for each listed source file.
- [ ] **No dangling references to deleted files**: `grep -rn "<deleted-name>"` across `wiki/ AGENTS.md tools/`.
- [ ] **`AGENTS.md` matches reality**: directory tree consistent with actual dirs; no references to files that no longer exist.
- [ ] **`.gitignore` exists** and covers `bin/ obj/ *.pyc __pycache__/ .vs/ *.user Thumbs.db Desktop.ini *_backup_*.tar.gz LLMWiki_backup_*.tar.gz _tmp_*.py _tmp_*.txt *_out.txt`. ⚠️ It only affects **untracked** files — already-committed junk needs a plain `rm` (never `git rm`).
- [ ] **Skill dual copies identical** (双副本 = 仓库版 + 用户级 `~/.trae-cn`): `diff <(sed 's/\r$//' ~/.trae-cn/skills/vibecoding-llmwiki/SKILL.md) <(sed 's/\r$//' LLMWiki/skills/vibecoding-llmwiki/SKILL.md)` empty. **Same version number ≠ same content** (2026-09-12: both said v1.6.0 yet differed by 4 lines). User-level wins; overwrite by byte copy. ⛔ `~/.workbuddy/skills/vibecoding-llmwiki/SKILL.md` 是**历史副本，不再维护、不再同步**，仅作历史留存（⛔ 不参与双副本一致性比对，也不由 `skill_pointer_check.py` 校验）。

Pitfalls and the full copy-paste checklist: the Wiki 批量漂移修正教训页（坑八 / 坑九 / 坑十）—— locate via `wiki/index/index.md` 第五节。

## Knowledge Accumulation Chain（知识积累与沉淀链路）

> **积累 = 把知识变成可复用的约束；沉淀 = 把约束写回知识库。** 两者都**不是**"把内容抄进页面"。

### 三层落位（内容该去哪）

| 内容性质 | 落位 | 判据 | 反例 |
|---|---|---|---|
| **结论与约束** | `wiki/` 对应分类页 | 能被后续任务直接引用的**判定** | "本次改了 A、B、C 三处" → 属 log |
| **过程与证据** | `logs/log.md` | 试错、测量、探针数据、验证批次 | "静态检查 63/63 通过" → 属 log |
| **原始资料** | `raw/`（只读） | 厂商文档 / demo / 原档 | 把厂商手册摘要抄进 wiki → 破坏单一真相源 |

⛔ **同一份数据只在一处持有** —— 权威页存数据，其他页只放**指针**（`[[decisions/ADR-Index]]`）。
⛔ **索引摘要不得含日期串与验证叙事** —— 脚本会自动剥离，写进 `title` 会污染索引。
⛔ **叙事只进 log** —— ADR / lessons / rules / standards / index 页只留结论与约束。

### 沉淀三步（Phase 3 强制，每步都有脚本）

```bash
# ① 写入：只写「结论与约束」，过程另记 log
python tools/adr_new.py  check <关键词>      # ADR：命中同主题 → merge（不新建）
python tools/lesson_new.py check <关键词>     # 教训：命中同族 → 追加条目（不新建）
python tools/rules_new.py check <关键词>      # 规则：命中同主题 → merge（不新建）

# ② 登记：脚本重建索引与路由（⛔ 禁手工插表行、禁手工改计数）
python tools/wiki_index_build.py             # 重建 index.md 骨架 + 分类表 + 计数
python tools/wiki_route_rebuild.py           # 由 tools/data/routes.tsv 重建场景速查路由

# ③ 记录：log 条目由脚本写（时间戳由脚本取，⛔ 禁手填）
python tools/wiki_log.py append <op> "<标题>" --src "<来源>" --op-list "a; b" --files "<文件>" --note "<结论/遗留>"
```

### 门禁（Phase 4 必跑，非零退出即不合格）

| 闸门 | 拦什么 |
|---|---|
| `tools/wiki_format.py` | 页面结构 / 行数上限 / 摘要长度 / 索引计数 —— 格式违规 |
| `tools/ingest_purity_scan.py` | **验证叙事 / 批次进度 / 日期沿革 / 日志体回灌** —— 赘述入知识库 |
| `tools/rules_check.py` | 规则页编号连续 / 结构契约 / 判据非空 |
| `tools/skill_pointer_check.py` | Skill 写死内容页名 / 红链 / 工具缺失 |
| `tools/wiki_audit.py` `lint_scan.py` `drift_scan_precise.py` `raw_asset_check.py` | 红链 / 孤儿 / 编号冲突 / 代码漂移 / raw 登记 |

⛔ **「绿灯」不是「没问题的证明」** —— 静态检查只覆盖它能判的模式化缺陷；语义缺陷只有编译器能定（见 KR-010）。


## Log & History Chain（日志与历史记录链路）

> **变更记录与历史记录是同一条链的两端**：当轮的**明细**在 `logs/log.md`，跨轮的**归档**在 `logs/backup/`，
> 二者由脚本串联；再往上还有一层**整库快照**（压缩包）。

```
本轮变更发生
   │
   ▼  wiki_log.py append ──────────────▶ logs/log.md          （当轮明细 · 最新在前 · 上限 50 条）
   │                                              │
   │  条目数 > 50（每周 Phase 4 一次）                │
   ▼                                              ▼
wiki_log.py truncate ─────────────▶ logs/backup/log_YYYY-MM-DD.md   （跨轮归档 · 按日一份 · 唯一截断入口）
   │
   ▼  自动重建（截断后无需手动再跑 index）
logs/INDEX.md                              （归档索引 · 一行一天 · 可路由）
   │
   ▼  backup_adaweld.py --llmwiki
LLMWiki_backup_YYYYMMDD_HHMMSS.tar.gz     （整库快照 · 工作区根 · 每天至多一份）
```

### 三层载体的分工

| 载体 | 装什么 | 谁写 | 保留多久 |
|---|---|---|---|
| `logs/log.md` | **当轮**变更明细（来源 / 操作 / 变更文件 / 结论遗留） | `wiki_log.py append` | 最新 50 条 |
| `logs/backup/log_YYYY-MM-DD.md` | **跨轮**归档（被截断下来的旧条目） | `wiki_log.py truncate` | 永久 |
| `logs/INDEX.md` | 归档目录的**索引**（一行一天，含条目数与摘要） | `wiki_log_tidy.py index`（截断后自动重建） | 与归档同步 |
| `LLMWiki_backup_*.tar.gz` | 整库快照（含 logs/ 全部） | `backup_adaweld.py --llmwiki` | 每天一份，按天去重 |

### 四条链路纪律

1. **写 log 只能走脚本** —— `wiki_log.py append`。⛔ 禁手工 Edit 插条目（历史上多次吃掉上一条表头、撕裂条目）；⛔ 禁手填时间戳。
2. **截断是归档不是丢弃** —— 旧条目**按日归档**到 `logs/backup/`，不删除。⛔ 任何"直接删掉旧条目"的做法都会断掉历史链路。
3. **截断后索引必须同步** —— `wiki_log.py truncate` 已**自动重建** `logs/INDEX.md`；若归档文件存在却**不可路由**（历史查不到），即说明索引未同步 = 链路断裂。
4. **归档索引由脚本维护** —— ⛔ 禁手工在 `logs/INDEX.md` 加行；⛔ 禁在 wiki 页里写死 `log_2026-XX-XX.md` 文件名（日期会变）。

### 查历史的正确姿势

| 要查什么 | 去哪查 | 怎么查 |
|---|---|---|
| 本轮刚做了什么 | `logs/log.md` 顶部 | 直接读第一条 |
| 某天的变更 | `logs/INDEX.md` | 定位到那天的归档行 → 读 `logs/backup/log_YYYY-MM-DD.md` |
| 项目演进史 | `raw/history/history.md` | 按时间分段检索（只读原始层，不进 wiki） |
| 跨会话残留证据 | `logs/log.md` + `logs/backup/` | 找**只能来自上一轮**的指纹值，不靠错误码推测（见 lessons） |

⛔ **不要凭记忆断言"上次是怎么处理的"** —— 历史会重编、会归档、会迁移；一律现查。


## Prohibited Behaviors (Forced)

1. **Prohibited**: Skip Phase 0 Query and code directly
2. **Prohibited**: Skip Phase 3 Ingest
3. **Prohibited**: Execute from memory without reading LLMWiki
4. **Prohibited**: Continue implementation after finding conflicts without user confirmation
5. **Prohibited**: Delete existing public interfaces without retaining compatibility layer
6. **Prohibited**: Leave red links (`[[reference]]` to non-existent pages) in Wiki
7. **Prohibited**: Create new .cs files without registering to .csproj
8. **Prohibited**: Execute Steps silently without showing Step-level output (Step number + name + findings)
9. **Prohibited**: Only show Phase-level summaries without Step-level breakdown
10. **Prohibited**: Re-introducing code graph tools (code-review-graph / CodeGraph) into the workflow. Per the 2026-08-19 code-graph deprecation, code graph steps are retired -- use the Grep default method (Step 0.7 / 2.5) instead.

## WorkBuddy Tool Mapping

| Original Action | WorkBuddy Tool |
|---|---|
| Read file | Read tool |
| Write new file | Write tool |
| Edit existing file | Edit tool |
| Search file names | Glob tool |
| Search file contents | Grep tool |
| Execute shell command | Bash tool |
| Execute PowerShell | PowerShell tool |
| Get timestamp | Bash: `date "+%Y-%m-%d %H:%M:%S"` or PowerShell: `Get-Date -Format "yyyy-MM-dd HH:mm:ss"` |
| Create project backup | Step 2.1: `python Vicoding管理平台/LLMWiki/tools/backup_adaweld.py` (backup only, daily-dedup). Step 3.7: `python Vicoding管理平台/LLMWiki/tools/backup_adaweld.py --output` (field-verification package). Do NOT hand-roll tar; do NOT use `--all` inside the workflow; Bash `tar`/`ls` are broken on this machine |
| Phase tracking | TaskCreate / TaskUpdate / TaskList |
| Present results | present_files tool |

## Module Change Scope Control

| Change Type | Allowed Modification Scope | Prohibited Scope |
|---|---|---|
| Industrial camera | SmartRayCam/ and direct callers | Other modules |
| Image algorithm | EmguALG/ and direct callers | Other modules |
| 3D data processing | PointCloudData/ and direct callers | Other modules |
| General tech | FileOperate/, Comm/ | Other modules |
| Welding process | InteliWeld/, SqlLiteDatabase/AutoParamManager.cs | Other modules |
| Database | SqlLiteDatabase/ and direct callers | Other modules |
| Motion control | MotionControl/ and direct callers | Other modules |
| UI | UIDesign/ and directly called backend interfaces | Backend module internals |
