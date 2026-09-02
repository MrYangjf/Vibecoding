---
name: "vibecoding-llmwiki"
description: "AdaWeldSystem LLMWiki-native vibecoding workflow. When user inputs /vibeCoding or asks for code development/bug fix/feature implementation, this skill forces AI to execute Phase 0~4 workflow with LLMWiki as the single source of truth."
version: "1.5.0"
agent_created: true
---

# /vibeCoding -- LLMWiki Native Workflow (WorkBuddy Edition)

> **core**: LLMWiki is the single source of truth. Before coding, Query the Wiki for context. After coding, Ingest knowledge back into the Wiki. Skill specs in `raw/skills/` are reference material only, not the command center.

## Workspace Path Map

All paths in this skill are relative to the workspace root:

```
WORKSPACE_ROOT = D:\焊接程序开发
```

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
| Raw Skills | `Vicoding管理平台/LLMWiki/raw/skills/AdaWeldsys_Skills/` |
| C# Style Guide | `Vicoding管理平台/LLMWiki/raw/skills/AdaWeldsys_Skills/04-Style/CSharpStyle.md` |
| History | `Vicoding管理平台/LLMWiki/raw/history/history.md` |
| Code Project | `AdaWeldSystem/AdaWeldSystem.csproj` |
| Code Root | `AdaWeldSystem/` |

## Trigger Conditions (Forced Match)

When the user inputs any of the following, this skill **must** be triggered:
- `/vibeCoding` or `/vibecoding` (case insensitive)
- Explicit development need: "develop a feature", "implement a requirement", "create a module"
- Explicit fix need: "fix a bug", "solve a problem"
- Explicit optimization need: "optimize a feature", "refactor code"

## Execution Priority (Forced)

Upon receiving `/vibeCoding` or equivalent intent, **do not** start coding directly or freely read files. Execute in the following order:

1. **Read LLMWiki workflow spec** (forced step 1):
   - Path: `Vicoding管理平台/LLMWiki/wiki/project/vibecoding-workflow.md`
   - Action: **must use the Read tool to read the full content**
   - If not found: log error and stop, prompt user "LLMWiki workflow file missing, cannot execute /vibeCoding"

2. **Read AGENTS.md supplementary rules** (forced step 2):
   - Path: `Vicoding管理平台/LLMWiki/AGENTS.md`
   - Action: Read the `/vibeCoding Workflow (LLMWiki Native)` section

3. **Execute Phase 0~4 strictly** (forced step 3):
   - Follow `vibecoding-workflow.md` Phase 0 -> Phase 1 -> Phase 2 -> Phase 3 -> Phase 4
   - **Each Phase must be executed Step-by-Step** (Step 0.1 -> 0.2 -> ... -> Step 4.x)
   - After each Phase, report results to user, get confirmation before proceeding

4. **Use TaskCreate/TaskUpdate for phase tracking**:
   - Create a task for each Phase before starting it
   - Mark task as `in_progress` when starting, `completed` when done

5. **Step-Level Display Rule (FORCED, Non-bypassable)**:
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
     - Related pages found: [[modules/Comm]], [[api/GlobalCommData]]

     ### Step 0.2: Read ADR
     - Read `wiki/decisions/ADR-007-CommRefactor.md`
     - Constraint: TCPIPComm under CommunicationManager
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
| **Phase 2: Code** | Implementation + impact verification | ADR constraints + Lessons gates + **Grep impact tracing** | Code files |
| **Phase 3: Ingest** | **Forced knowledge deposition** | Update `wiki/modules/`, `wiki/api/`, `wiki/decisions/`, `wiki/lessons/`, `logs/` | Updated Wiki |
| **Phase 4: Lint** | Health check + code drift | Scan contradictions + orphan pages + red links + **Grep code drift** | Health report |

## Key Rules (Forced, Non-bypassable)

1. **No skipping Query**: Before coding, Phase 0 must be executed to retrieve context from LLMWiki. Coding from memory or Skill files alone is prohibited.
2. **Skill demoted to reference**: `raw/skills/` Skill files are **reference material**, not **command source**. Process authority belongs to LLMWiki. If Skill and LLMWiki conflict, LLMWiki prevails.
3. **ADR is hard constraint**: Architecture Decision Records in `wiki/decisions/` are mandatory constraints before coding. After coding, must review to check for violations.
4. **Lessons are gates**: Pitfall records in `wiki/lessons/` are mandatory pre-coding check items. E.g., registering new .cs files to .csproj — see [[guides/Namespace-Compilation]] section 1.1 (the old `lessons/CodeProjectRegistration` page was consolidated there on 2026-09-01).
5. **Ingest is mandatory**: Phase 3 Ingest is not optional. Coding without Ingest is considered incomplete.
6. **New decisions must be recorded**: If coding involves new architecture choices, must create ADR in `wiki/decisions/`.
7. **Timestamp rule**: Phase 3 Ingest appending `logs/log.md` must get timestamp via Bash `date "+%Y-%m-%d %H:%M:%S"` or PowerShell `Get-Date -Format "yyyy-MM-dd HH:mm:ss"`. Never estimate. If unable to execute, mark as `[No.]`.
8. **New .csproj registration**: When creating new .cs files, **must** add `<Compile Include="..." />` entries to `AdaWeldSystem/AdaWeldSystem.csproj`.
9. **Step-Level Display (Non-bypassable)**: Every Step within each Phase MUST be explicitly shown to the user with its number, name, and output. Skipping Step-level display is a violation. See Execution Priority section 5 for details.
10. **Grep is the default code-location method**: Per ADR-025 deprecation (2026-08-19), code-review-graph is **retired**. Use Grep to locate symbols (Step 0.7), read exact line ranges (Step 0.7), and trace impact with manual multi-level Grep (Step 2.5). No code graph tool is required or allowed as a mandatory step.
11. **0 consumers ≠ dead member (2026-09-03, learned the hard way)**: When an audit reports a symbol with zero consumers, **do not propose deleting it** until you have asked whether it is a **cross-cutting-concern carrier** — a log tag, serialization key, permission marker, or DI/registration hook. Also check whether `raw/` source documents list it as a **contract member**. The user's own project convention: observability APIs (`StepStatusText` / `WorkElapsedMs`) and safety hooks (`CheckDeviceIOSafe`) are **never** deleted for being unused. Propose "tighten the type / lower the visibility" instead of removal, and let the user decide.
12. **No compiler in this sandbox — declare it, don't fake it (2026-09-03)**: `dotnet`, `msbuild` and the C# compiler are blocked by the security policy (Known Windows LOLBin), and this machine has no `C:\Program Files\Microsoft Visual Studio`. Never burn turns hunting for them. Use the Python static-consistency verifier (Step 2.6) instead, and **explicitly report "real compilation pending in Visual Studio" as a known residual item** in the final delivery. Do not describe static checks as "build passed".

## Critical ADR Constraints (Must Check Before Coding)

| ADR | Constraint |
|---|---|
| ADR-001-DisposePattern | Use `DisposeComponents()` method; **never add or override `Dispose(bool)` in any `.cs` file**; never modify Designer.cs Dispose |
| ADR-002-CS73-Constraint | C# 7.3 only. No auto-property initializer, no expression-body property, no `out var`, no tuple deconstruction (see note below) |
| ADR-003-SingleAlgorithmFile | ImageAlgorithm.cs is the only algorithm file |
| ADR-004-WorkflowStepEnum | Use 7 Step enum, not sequential flow |
| ADR-005-CallbackAcquisition | Workflow image acquisition uses callback wait pattern |
| ADR-006-UILightProperty | UILight must use OnColor/OffColor/State |

> **Note on ADR-002**: The original ADR-002 prohibits `out var` and tuple deconstruction due to MSBuild v4.0. However, the CSharpStyle.md V2.260624 allows `out var` and tuples. **Follow CSharpStyle.md** (the latest authority) for syntax questions. When in doubt, Query the Wiki.

## Critical Lessons (Must Avoid Before Coding)

| Lesson | Pitfall |
|---|---|
| DesignerCs-Immutable | Never modify Designer.cs Dispose method; also **never add `Dispose(bool)` override in `.cs` files** -- use `DisposeComponents()` instead |
| CodeProjectRegistration (**now [[guides/Namespace-Compilation]] §1.1**) | New .cs files must be registered to .csproj |
| AutoProperty-Initializer | auto-property initializer causes CS1519 on MSBuild v4.0 |
| UI-Thread-Safety | Workflow events must use InvokeRequired |
| LiveMode-Exclusion | Live mode does not trigger AcquisitionCompletedSignal |
| Bounds-Sentinel-BlackScreen | Bounds sentinel value causes black screen |
| Assimp-RootNode | Assimp import must add entire scene.Root |
| UILight-Property | UILight must use OnColor/OffColor/State; case-sensitive "On" not "ON" |

## C# 7.3 Quick Reference (from CSharpStyle.md)

**Allowed**: `out var`, tuples, `nameof()`, `$""` interpolation, `??`, `?.`, `=>` expression body, `readonly struct`, `async/await`

**Prohibited (C# 8.0+)**: switch expressions, property pattern matching, `using` declarations, nullable reference types, `init` accessor, `record`, range operator, `$@""` interpolation with colon formatting

**Special trap**: Do NOT use `{expr:format}` inside `$""` interpolation (e.g., `{dt:yyyy-MM-dd}`). Extract to local variable first. This causes CS1739 in this project's build environment.

**WinForms designer**: `InitializeComponent()` must NOT contain `for`/`while`/`if`/`switch`/`foreach`. Expand loops to individual statements.

## Phase 0: Query -- Forced Knowledge Retrieval (Detailed Steps)

> **REMINDER**: Must display each Step (0.1 ~ 0.7) with its number, name, and output. Do NOT collapse into a single summary.

### Step 0.1: Read Index (Forced)
- **Action**: Use Read tool to read `Vicoding管理平台/LLMWiki/wiki/index/index.md`
- **Purpose**: Quickly locate Wiki pages relevant to the current requirement
- **Output**: List related module pages, API pages, decision records, lesson records

### Step 0.2: Read Decision Constraints ADR (Forced)
- **Action**: Read all ADRs under `Vicoding管理平台/LLMWiki/wiki/decisions/` related to involved modules
- **Purpose**: Get hard constraints -- these are deliberate architecture choices that must be followed
- **Output**: Decision constraint checklist (must follow, or explicitly override and record new ADR)

### Step 0.3: Read Historical Lessons (Forced)
- **Action**: Read all lessons under `Vicoding管理平台/LLMWiki/wiki/lessons/` related to involved modules
- **Purpose**: Get gate check items -- these are pitfalls others have hit, must confirm avoidance
- **Output**: Historical lesson gate checklist (must confirm avoidance before coding)

### Step 0.4: Read Module Architecture (Forced)
- **Action**: Read module pages under `Vicoding管理平台/LLMWiki/wiki/modules/` for involved modules
- **Purpose**: Understand module boundaries, core files, collaboration, known issues

### Step 0.5: Read API Context (Forced)
- **Action**: Read API pages under `Vicoding管理平台/LLMWiki/wiki/api/` for involved modules
- **Purpose**: Understand existing public interfaces, avoid reinventing or breaking contracts

### Step 0.6: Read History (Optional but Recommended)
- **Action**: Read `Vicoding管理平台/LLMWiki/raw/history/history.md`, search for related historical changes
- **Purpose**: Prevent new features from conflicting with historical ones

### Step 0.7: Symbol Location via Grep (Default)
- **Action**: Locate involved symbols in code with Grep, then map file + line ranges:
  1. `Grep(pattern="<key symbol>", path="AdaWeldSystem/", output_mode="content", -n=true)` -- locate symbol definitions & usages
  2. Review matched lines to understand call relationships (callers/callees)
  3. For cross-file call chains, trace manually: search each caller symbol recursively (N-level)
  4. **MANDATORY cross-validation (2026-09-01)**: A single Grep result set **can be silently truncated** with no warning. When the goal is to enumerate **all callers/consumers** (e.g. "which files use this type"), you MUST run **at least two independent searches** with different patterns and confirm the file sets match. Narrow the pattern first (add `\b` word boundaries, drop substring-overlapping alternatives like `FaultRecord` vs `FaultRecordManager`), and re-Grep per-directory as a backstop if consumers are known to cluster in one folder. See [[guides/Project-Tools]] §1.2.
- **Purpose**: Supplement LLMWiki architectural knowledge with code-level call relationships that Wiki does not cover
- **Output**: Code-level relationship report (callers, callees for involved symbols)
- **Note**: This is the default (pre-code-graph) method -- the code graph tool (ADR-025) has been retired.

> **⚠️ Truncation incident (2026-09-01)**: migrating `FaultRecoveryManager`, the first Grep reported **2** consumers; a second narrower Grep revealed **6**. Four files (`LineLaserWorkflow` / `MonitorCameraWorkflow` / `MotionControlWorkflow` / `WeldParamControlWorkflow`) would have failed to compile. Never trust a single Grep for completeness.

## Phase 1: Plan -- Planning & Constraint Confirmation (Detailed Steps)

> **REMINDER**: Must display each Step (1.1 ~ 1.5) with its number, name, and output. Do NOT collapse into a single summary.

### Step 1.1: Requirement Parsing
- Summarize user core need in one sentence
- Confirm involved modules and boundaries

### Step 1.2: Change Scope Planning
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

> **REMINDER**: Must display each Step (2.1 ~ 2.5) with its number, name, and output. Do NOT collapse into a single summary.

### Step 2.1: Project Backup
- Use Bash to create a zip backup of the project:
  ```bash
  cd "D:/焊接程序开发"
  # Get timestamp for backup filename
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  # Create backup (exclude bin/obj)
  cd AdaWeldSystem && tar -czf "../AdaWeldSystem_backup_${TIMESTAMP}.tar.gz" --exclude="bin" --exclude="obj" . && cd ..
  ```

### Step 2.2: Code Implementation
- **Continuously check** Phase 0 retrieved ADR constraints and Lessons gates during coding
- **When reading code, reuse Phase 0 Step 0.7 Grep-guided reading**: locate target symbols' file + line numbers via Grep, then read exact code blocks with `Read(offset/limit)`, avoiding whole-file reads
- Follow C# code style (read `Vicoding管理平台/LLMWiki/raw/skills/AdaWeldsys_Skills/04-Style/CSharpStyle.md`)
- Minimal change, only modify directly related libraries and UI

### Step 2.3: Code Self-Review
- After implementation, check Phase 0 "Decision Constraint Checklist" and "Historical Lesson Gates" item by item
- **Mandatory Dispose check**: run `grep -rn "protected override void Dispose" --include="*.cs"` and verify that:
  - Designer.cs entries are unmodified (match standard generated pattern)
  - **No `.cs` file (excluding Designer.cs) contains `Dispose(bool)` override**
- Confirm no ADR or Lessons violations

### Step 2.4: .csproj Registration (If New Files Created)
- If new .cs files were created, **must** add `<Compile Include="..." />` entries to `AdaWeldSystem/AdaWeldSystem.csproj`
- Use Edit tool to add entries in the appropriate `<ItemGroup>`

### Step 2.5: Impact Radius Verification via Grep (Default)
- **Action**: After code changes, verify impact scope using manual multi-level Grep tracing:
  1. `Grep(pattern="<changed_public_symbol>", path="AdaWeldSystem/", output_mode="content", -n=true)` -- find all references
  2. Trace each caller recursively (A->B->C: grep B, then grep each caller of B, etc.)
  3. Cross-check: every caller found must be reviewed for compatibility
  4. **Re-run with a different pattern before declaring done** -- Step 0.7's first Grep is exactly the one that got truncated (2 vs 6 consumers). This step is the safety net: do **not** skip it just because Phase 0 already grepped the symbol.
- **Purpose**: Catch indirect call chain breakages (A->B->C: changing B breaks A -- grep B, then grep callers of B to find A)
- **Output**: Impact report (affected files, caller chain depth, any broken references)
- **Note**: Manual multi-level Grep is the default method -- the code graph tool (ADR-025) has been retired.

### Step 2.6: Correctness Verification (Forced -- substitutes for compilation)

> **Why this step exists**: this sandbox has no C# compiler (Key Rule 12). Do not skip verification, and do not pretend a build ran.

- **Action**: write a throwaway Python verifier that strips XML doc comments **first**, then asserts the invariants your change was supposed to establish. Typical checks that caught real bugs on 2026-09-03:
  - member shadowing: a derived-class `Tag`/`_tag`/`StepXxx` redeclaring a base member (CS0108)
  - residual old symbol after a rename (e.g. `_tag` left over after unifying on base `Tag`)
  - back-flow: a banned call site reappearing (e.g. `ShowLog` after routing everything through `DeviceLog`)
  - now-unused `using` directives left behind by the change
- **Two-pass discipline**: expect the first version of the verifier to produce false positives (comment matches, namespace-only usages). Iterate to a precise version rather than eyeballing away the noise.
- **Cleanup**: delete every `_tmp_*.py` script before finishing.
- **Output**: static-check result table + explicit statement that real compilation is pending.

## Phase 3: Ingest -- Forced Knowledge Deposition (Detailed Steps)

> **REMINDER**: Must display each Step (3.1 ~ 3.6) with its number, name, and output. Do NOT collapse into a single summary.

**This phase is mandatory, not optional. Coding without Ingest is considered incomplete.**

### Step 3.1: Update Module Docs
- Update `wiki/modules/` pages for involved modules
- Update core file list, module responsibilities, collaboration, known issues

### Step 3.2: Update API Docs
- Update `wiki/api/` pages for involved APIs, or create new pages
- Update public classes/methods/events, interface signatures, usage specs

### Step 3.3: Create or Update Decision Records (ADR)
- If Phase 1.3 forecasted new decisions, create `wiki/decisions/ADR-XXX-{Title}.md`

### Step 3.4: Create or Update Lesson Records
- If new pitfalls were discovered, create/update `wiki/lessons/{Title}.md`

### Step 3.5: Update Index
- Update `Vicoding管理平台/LLMWiki/wiki/index/index.md`
- Add new pages to corresponding category tables, update existing page summaries

### Step 3.6: Append Log
- Append to `Vicoding管理平台/LLMWiki/logs/log.md`
- Format: `## [YYYY-MM-DD HH:mm:ss] coding | description`
- **Timestamp must be obtained via Bash `date "+%Y-%m-%d %H:%M:%S"` or PowerShell `Get-Date -Format "yyyy-MM-dd HH:mm:ss"`, never guess**
- **⚠️ Append with the Edit tool, not a heredoc (2026-09-03)**: `cat >> logs/log.md << 'EOF'` gets rejected by the security policy whenever the body trips a keyword filter (e.g. it mentions a C# compiler). Read the file's tail first, then `Edit` the last line to append.
- **⚠️ Do not write page-link mappings as `[[old]]→[[new]]` inside `log.md`** — `wiki_audit.py` parses the brackets as real links and reports red links. Write them as plain text `api/old → api/new` (2026-09-02).

## Phase 4: Lint -- Health Check (Detailed Steps)

> **REMINDER**: Must display each checklist item with its result. Do NOT collapse into a single summary.

### Step 4.1: Run the Automated Wiki Audit (Forced)
Run the read-only audit script and fix everything it reports:

```bash
cd "Vicoding管理平台/LLMWiki" && python tools/wiki_audit.py
```

10 automated checks: ① red links ② orphan pages ③ duplicate `index.md` rows ④ ADR number gaps & unregistered ADRs ⑤ page size distribution (pages >600 lines need a TOC) ⑥ duplicate content (3-gram similarity) ⑦ misplaced guide-type pages in `lessons/` ⑧ `standards/` inbound-link stats ⑨ second-level subdirectories under `wiki/` (must be 0 -- all categories are flat `.md` files) ⑩ **over-small categories (<=2 pages -- merge into a related category; only `index/` and `architecture/` are exempt)**.

**Health criteria**: red links = 0, orphan pages = 0, duplicate index rows = 0, subdirectory count = 0, over-small categories = 0.

Then run the two companion scanners (both were repaired on 2026-09-03 — they had a hardcoded path from a previous machine and were **silently** scanning 0 files, which is worse than crashing):

```bash
cd "Vicoding管理平台/LLMWiki" && python tools/lint_scan.py && python tools/drift_scan_precise.py
```

- `lint_scan.py` — dead links / orphan pages / ADR number conflicts / broken external file links. The 8 hits in `project/vibecoding-workflow.md` are template placeholders (`modules/XXX`, `decisions/ADR-XXX`) and are expected.
- `drift_scan_precise.py` — wiki pages citing `.cs` files that no longer exist. **Known backlog: 25 real drift entries**, all pre-existing (deliberately-deleted files such as `SafetyFlow.cs` / `SafetyInterlock.cs` / `SafetyWorkflow.cs` / `SimulationWorkflow.cs` / `MainDeviceWorkflow.cs` / `WorkflowStateBase.cs`, external reference implementations `StationProcess.cs` / `AssemblyProcess.cs`, and case-sensitivity false positives on `designer.cs`). **Your change must introduce 0 new drift** — verify by grepping the output for the pages you touched.

> **Tooling rule (2026-09-03)**: every script under `tools/` must derive its paths from `__file__` (see `wiki_audit.py`). Never hardcode an absolute path — after a machine migration a hardcoded path makes a scanner report "0 files" and look healthy.

### Step 4.2: Manual Checklist
- [ ] **Contradiction detection**: Do new Ingested contents conflict with existing wiki pages?
- [ ] **Stale detection**: Did code changes overturn old design decisions?
- [ ] **Bidirectional links**: Do related pages reference each other?
- [ ] **Code drift**: Do `wiki/modules/` descriptions match current code? Use Grep to spot-check: search key symbols/modules described in Wiki, confirm presence & usage in code. Manually identify dead symbols or oversized functions when refactoring candidates matter (ADR-025 code graph retired, no graph tool needed).
- [ ] **Verify before correcting stale docs**: when a wiki page names a file/type/component, **confirm existence with `find` / Glob first**. Pages may describe entities that were deleted (or still-existing ones as deleted). Never do blind text substitution of version labels.
- [ ] **Before merging or deleting a category directory**: measure pages / lines / inbound-link count for each candidate. The archived-semantics directory must never absorb the current normative page. Checking inbound-link distribution first often exposes duplicate pages (e.g. a second parallel architecture page) worth folding in at the same time.

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
10. **Prohibited**: Re-introducing code graph tools (code-review-graph / CodeGraph) into the workflow. Per ADR-025 deprecation (2026-08-19), code graph steps are retired -- use the Grep default method (Step 0.7 / 2.5) instead.

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
| Create zip backup | Bash: `tar -czf backup.tar.gz --exclude=bin --exclude=obj .` |
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
