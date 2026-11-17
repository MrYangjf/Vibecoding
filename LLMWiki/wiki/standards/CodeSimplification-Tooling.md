---
title: CodeSimplification-Tooling 代码精简固定工具集（2026-10-26 v2）
date: 2026-10-26
tags: [规范, 代码精简, 工具, 检查脚本, 批改脚本, 判据]
status: accepted
---

# CodeSimplification-Tooling —— 代码精简固定工具集

> **缘由**：2026-10-26 全库治理轮里，**同一失效模式（插入点用陈旧行号 ⇒ 声明被复制而非移动 ⇒ CS0102）连续踩了 4 次**，随后又因批改脚本把「成员起点→类尾」整段当最后一块，搬动时把 `#endregion` 与类闭合 `}` 一起搬走，造成 **18 个文件 / 124 条编译错误**。
> **本页把「会踩的坑」固化成可复用脚本 + 硬性自证要求**，使后续批改**只调参数、不重写逻辑**。

## 一、固定脚本（v2，2026-10-26 加固）

| 脚本 | 作用 | 何时跑 | 硬性要求 |
|---|---|---|---|
| `scripts/simplify_guard.py` | **结构守卫**：花括号平衡、**namespace 级成员/孤立语句/裸块**、XML 标签闭合、`#region` 配对、成员多重集差分、行尾/BOM/CRCRLF 守恒、缩进同质 | **每次批改前后各跑一次** | 任一项 FAIL ⇒ **立即回滚** |
| `scripts/simplify_apply_member_order.py` | **成员顺序重排**（§一①，**region 内排序**）；`--report` 出清单、`--fix-victims` 定点搬移 | 处理 ① 类违规 | 候选先过结构守卫；落盘后守卫复验，FAIL 自动回滚；定点搬移只搬到本 region **最早**更高层级成员之前 |
| `scripts/simplify_apply_docs.py` | **注释补全/压缩**（§二②） | 处理 ② 类违规 | **private `///` 保留**；插入行继承缩进与文件行尾；写前/写后均过守卫 |
| `scripts/simplify_selfcheck.py` | **判据-标准一致性 + 四重自证** | 改标准/改判据后；发版前 | 干净基线 → 注入重复成员必被抓 → **结构判据自证** → 零变化 |
| `scripts/simplify_run.py` | **一键巡检**：guard + 扫描器聚合 + selfcheck + **真 MSBuild 编译门禁** | 每轮收尾 | 编译错误即 NOT-PASS |
| `scripts/comment_scan.py` | **注释可复算扫描**：三分计数 / 撕裂四类 / 复述三档 / 占位式 XML | 每轮精简的 Phase 0 与 Phase 4 各跑一次 | 数字必须来自本脚本输出，禁止自报 |
| `scripts/arch_boundary_scan.py` | **跨文件架构 / 层边界审查 + 精简候选逐项标记**：A1~A8 / B1~B6 跨文件判据 + 聚合 `csharp_review.py` 单文件判据，产出 Markdown 报告 / CSV / JSON | 全库架构核查、精简落地前的标记清单 | **只读**；`--selfcheck` 全绿才允许出报告；0 消费只报不删；⛔ 不得替代真编译 |

### 1.2 arch_boundary_scan.py（跨文件判据补位）

`csharp_review.py` 按本规范 §四「只处理单个 `.cs`，不跨文件分析」，覆盖不到**架构分层**（[[standards/ModuleOrganizationPattern]] H1~H11）与**代码层边界**（[[standards/WorkflowResponsibilityBoundary]] §七 / [[standards/UiStateSimplification]]）。本脚本补这一层，逐项产出唯一标记 ID，供业主逐案裁决。

```bat
python scripts/arch_boundary_scan.py --selfcheck   :: 判据阴性对照 + 合规样本零误报 + 豁免集自检
python scripts/arch_boundary_scan.py              :: 全库审查，产物落工作区根
```

**判据优先级**：A1 抽象层 SDK 依赖 / A2 模组反向依赖流程层 / A4 绕过 Manager / A5 配置实例外流 / A6 计算路径同步落盘 / A7 业务层绑定厂商 / B1 UI 图像运算 / B2 UI new 后端类 / B3 UI 写流程状态 / B4 非 UI 反向 using UIDesign / B5 UI 直读写配置 / B6 初始化期追溯；A3、A8 为 info 级只报不删。
**收敛纪律**：跨文件判据最容易过报，首版必须现场取证后收敛 —— 三类已实证的过报与豁免依据见 [[lessons/StaticVerifier-Checker-FailureModes]]「跨文件架构判据的四类过报」。

⛔ **`simplify_apply_member_order.py --fix-victims` 禁用令**：该脚本的块切分会把成员插进 `if (...) { }` 与 `else if (...)` 之间，切断 if/else 链并吞掉闭合花括号，产生编译期结构错误；而 `simplify_guard.py`、`--report`、`simplify_selfcheck.py` 当时全绿。含**构造函数重载**或**跨行 if/else 链**的文件一律禁用该脚本；确需重排时按字节手改，且必须 `MSBuild /t:Rebuild` 复核（[[rules/KR-010-No-Compiler-Honesty]]）。

### 1.1 comment_scan.py（2026-11-09 新增，专门治「自报数字不可复算」）

```bat
python scripts/comment_scan.py stats   --root AdaWeldSystem --out-dir <tmp>
python scripts/comment_scan.py trunc   --root AdaWeldSystem --out-dir <tmp>
python scripts/comment_scan.py restate --root AdaWeldSystem --out-dir <tmp>
python scripts/comment_scan.py xml     --root AdaWeldSystem --out-dir <tmp>
```

**口径（与标准 4.1 映射表第 12~15 行一一对应）**

| 子命令 | 输出 | 关键约束 |
|---|---|---|
| `stats` | 总/空/代码/注释（doc + 独立 `//` + 块）+ `code_trailing` | 三类**互斥**，脚本内 `assert` 自校验；文件尾换行不产生幻影空行 |
| `trunc` | T1 同块多 summary / T2 标签配对错 / T3 声明间空行 / T4 缩进为 0 | 四类**互斥**，`blocks` = union，用于对账 |
| `restate` | strict ⊂ wide ⊂ ultra 三档候选 | 只扫独立 `//` 行；`///` 归 A.注释规范，不混入 |
| `xml` | 占位式 `<returns>` / `<param>` | 与 `A.占位式XML` 判据同口径，删完必须为 0 |

> ⚠️ **教训**：2026-11-09 之前，「233 处撕裂 / 609 处复述」两轮自报数字都无脚本落盘、无法复算。
> 本轮起所有注释类数字一律由本脚本产出；临时脚本只允许做**批改**，不允许做**计数**。
> 历史数字对不上的部分已在标准 4.1 表第 12 行注明差异原因（幻影空行 / 行尾注释重复计入）。

**解释器**：`D:\ProgramData\miniconda3\envs\myenv\python.exe`（PATH 上的 `python` 是 0 字节 Store 占位符，不可用）。
**统一入口**：`python scripts/simplify_run.py`；批次间快验：`python scripts/simplify_run.py --build-only`。
**真编译入口（本机实测）**：`C:\Program Files\Microsoft Visual Studio\18\Insiders\MSBuild\Current\Bin\MSBuild.exe`
`MSBuild.exe AdaWeldSystem\AdaWeldSystem.csproj /t:Rebuild /p:Configuration=Debug /p:Platform=AnyCPU /v:m /nologo /clp:ErrorsOnly`
通过判据：**退出码 0 且 `bin\Debug\AdaWeldSystem.exe` 时间戳刷新**；警告可接受，错误必须为 0。

## 二、放行条件（四关，缺一不可）

必须**四关全过**才落盘，任一关不过就**放弃该文件**（不硬改）：

1. **切分无损**：`header + 成员块 + 固定间隙 == 原类体区间`（字节级相等；间隙含 `#region/#endregion/空行`，原地不动）
2. **搬后有序**：目标违规已消除，且扫描器违规总数**不上升**
3. **结构守恒**：guard 全绿（brace / namespace 级结构 / region 配对 / XML 标签 / 成员多重集 / 行尾 / 缩进）
4. **真编译**：`MSBuild /t:Rebuild` 错误 0（**静态守卫查不出「位置错误」**：花括号总数仍平衡、成员数量也没变，但类已提前闭合——2026-10-26 实证）

## 三、快速精简 SOP（每批只做一件事）

1. `simplify_apply_member_order.py --report` → 拿到「文件 | 类 | 类型 | 成员 | 行 | region」清单
2. `--dry-run --files <本批文件>` → 确认候选可安全重排（`DRY n -> m`），`SKIP` 的不要硬改
3. `--files <本批文件>` 落盘（脚本自动快照 + 候选守卫 + 写后守卫 + 回滚）
4. `simplify_run.py --build-only` → **编译 0 错误**；失败则从 `_simplify_snapshot/` 回滚
5. 全库 `simplify_guard.py --baseline _simplify_snapshot` → 结构/行尾/成员全绿
6. 收尾 `simplify_run.py` → guard + 扫描器 + 自检 + 编译全 PASS

## 四、禁区清单（已踩过的坑 → 脚本内置对策）

| # | 坑 | 症状 | 对策 |
|---|---|---|---|
| 1 | **插入点用删除前的行号** | 同一声明被**复制** N 份（曾 12 份）⇒ CS0102 | 删除后**重新解析**再定位锚点；落盘前断言该声明出现次数 == 1 |
| 2 | **用 `Method.end_line` 定位方法块尾** | 该值**不含方法闭合大括号** ⇒ 闭合行落进缺口 | 用「从 `start_line` 起做花括号/`;` 配对」 |
| 3 | **表达式体成员（`=> x;`）无 `{`** | 大括号配对找错位置 ⇒ 块跨度重叠 | 统一用语句配对法，不用 `body_start` 配对 |
| 4 | **行级插入未继承缩进** | 插入的 `///` 顶格，像坏掉的注释块 | 插入继承 doc 块首行缩进 + 事后缩进同质化扫描 |
| 5 | **内容不变式用顺序敏感比对** | 真重排必然报 drift ⇒ 全被误拒 | 用**多重集**（排序后）比对；顺序由「块是置换」保证 |
| 6 | **每轮全量重解析** | 单文件空转 588 秒 CPU、零落盘 | 每文件**只解析一次**，重排后复用结果 |
| 7 | **判据只看属性名** | `e.Result`（事件参数）被误判为 `Task.Result` 阻塞（9 处假阳性） | 判据**带类型限定**（`Task`/`ValueTask`） |
| 8 | **跨 `#region` 搬动成员** | 破坏区域结构 ⇒ region 配对失配 | **区域感知**：段内重排、段间不跨越 |
| 9 | **最后一块包含类尾**（2026-10-26 实证） | 搬动最后一块时把 `#endregion` + `}` 一起搬走 ⇒ 类提前闭合、成员跑到 namespace | **块/间隙模型**：成员块只含自身行，`#region/#endregion/}` 作为固定间隙原地不动 |
| 10 | **静态守卫只看数量** | brace 平衡、成员多重集全绿，但类已提前闭合 | 新增 **namespace 级结构判据**（成员/孤立语句/裸块）+ **真编译门禁** |
| 11 | **字段解析器把方法内局部变量当字段** | `for (int i = 0; ...)` 被报成 `F.i` | 成员顺序判定只认类体深度 1 的严格声明；发现误报按 `--report` 人工排除 |

## 五、口径-判据一致性（改标准 = 同时改判据）

[[standards/CodeSimplification]] 的「4.1 口径-判据映射表」是**唯一对照表**。任何一次改标准：

1. 同步改 `scripts/csharp_review.py` 对应判据（**含严重级与判定范围**）
2. 跑 `scripts/simplify_selfcheck.py`（含四重自证）
3. 在 `logs/log.md` 记录「标准条款 → 判据项」的对应变更

**2026-10-26 成员顺序口径修订**：判定范围 = **每个 `#region` 段内；跨 region 不比较**。旧「类内全局顺序」会把 42 个语义分区文件误报为违规，已废止。批改脚本与扫描器同步改为 region 内口径。

**2026-10-27 多层锁判据**：`csharp_review.py` 新增 `B.多层锁`（嵌套锁 / 跨方法锁顺序反转 / `lock("字符串")` / 锁局部对象）与锁字段 `readonly` 检查；`simplify_selfcheck.py` 的 JUDGE 增加「9 多层锁」。实测 0 处嵌套/顺序反转，说明现有锁均为扁平单锁。

**2026-10-29 成员顺序清零与判据修正**：`parse_file` 收录嵌套类型（外层类不再把嵌套类方法算作自身成员）；析构函数 `~ClassName()` 不再当构造函数；字段只认类体深度 0（方法内局部变量不再误报）；新增 `--fix-victims` 定点搬移，专治 overlap / 堆叠注释 / 嵌套类型文件。全库复核 `violations=0 files=0`。同日完成：`simplify_apply_docs.py` 二次清理 **51 warn**（trim 30 / param 16 / returns 6）；`C.功能重叠` 增加「**同名重载不参与判定**」，3 处登记为有意保留；修复 `simplify_apply_docs.py` 双 BOM。当前扫描器 **warn=0 / error=0**。同日两轮嵌套内联：判据由「1 个调用者」收紧为「1 个调用表达式」（`C.嵌套内联` 96→58），内联 **14** 条（7 格式化/转换 + 7 UI 单调用点），剩余 44 条语义/初始化/风险方法保留（96→44）。

**2026-10-29 续跑第 3/4 轮内联**：再内联 **10** 条 → `C.嵌套内联` **44→34**（第 4 关新增内容后复测为 35，新增 `FileEditorForm.ClearXmlAllInfo` 已登记保留：清除树+映射的语义复位）。第 3 轮 6 条（`GetAttr` / `InitializeDatabase` / `PageBangdingIni` / `JobButton_Click` / `MarkHealthy` / `CreatCamereDir`），第 4 轮 4 条（`InitializeTodayTable` / `RefreshParam` / `ResetWeldFlow` / `RefreshMotorStatus`）。余 34 条按 7 类登记保留（Log Tag 载体 6 / 快捷区指令分发 10 / 解析校验 5 / 卫语句 4 / 流程步骤 5 / 初始化与几何 3 / 事件抛出 1），不再每轮重复审理——分类台账见 [[project/CodeSimplification-Backlog-20261026]] B-6。内联落盘时必须同步清理被删方法的 `///` 注释块与缩进（本轮 `KukaRsiComm.cs` 因 doc 行缩进混用被 `simplify_guard` 拦下一次）。

**2026-10-29 语法简化四则（第 5 关）**：新增 `simplify_run.py` 第 5 关「IDE 语法简化门禁」——`dotnet format style --verify-no-changes --diagnostics IDE0017 IDE0018 IDE0019 IDE0031 --severity info --no-restore`，0 诊断即 PASS（无 dotnet SDK 时自动 SKIP，可 `--skip-ide` 显式跳过）。批改同样走官方修复器：`dotnet format style <csproj> --diagnostics IDE0017 IDE0018 IDE0019 IDE0031 --severity info --no-restore`，实测 **216 条 → 0**（IDE0017 75 / IDE0018 93 / IDE0019 9 / IDE0031 39），72 文件 +591 −729 行。

**2026-10-30 增补 IDE0059（五则）**：门禁诊断清单加入 `IDE0059`（不必要赋值），标准 §二④ 改称「语法简化五则」、映射表行 10 同步，`simplify_selfcheck.py` 关键字同步为 `语法简化五则 / IDE0059`。实测 **9 条 → 0**：`out var num`×2、`out string payload` → `out _`；`Mat copy = null`、`List<IlJobParamInfo> jobParams = null` 删初值；`double pattern = 0` 改首个 `out double pattern` 就地声明；`TemplateMatch` 三个初值删除（修复器对 `new Point(...)` 会退化成 `_ = new Point(...)` 死语句，**必须人工删除**）。

> ⚠️ **dotnet format 行尾坑（2026-10-29 实证）**：对原本 **LF** 的文件，修复器只把改动行写成 CRLF，结果同一文件混行尾，`simplify_guard` 报 `eol-mixed`（本轮 10 文件）。处置：批改后先跑 guard，按文件原有行尾**整文件归一**（本轮统一回 LF），再复跑；**不得**直接放过混行尾。
> ⚠️ **注释/缩进不归 format 管**：`--diagnostics` 只跑指定修复器，不做空格格式化（这是好事，避免全库重排）；但多语句单行（如 `_mat = null; GlobalCommData.ShowLog(...)`）需手工拆行。⛔ 不要为了省事跑无 `--diagnostics` 的 `dotnet format`，会把全库按默认规则重排。

⛔ **禁止**：只改标准不改判据；只改判据不改标准；发现噪声就「忽略」而不修判据（噪声必须归零或降级，不能靠人肉忽略）。

## 六、相关页面

- [[standards/CodeSimplification]] —— 标准正文（唯一标准源，含 4.1 口径-判据映射表）
- [[standards/CodeSimplification-ReviewWorkflow]] —— 检查脚本工作流（4 步）
- [[lessons/StaticVerifierJudgements]] —— §9.16 撕裂 / §9.17 真编译 / §9.18 最后一块包含类尾
- [[architecture/CodeMap]] —— §5.7 代码精简轮欠账台账（含剩余手工项）
