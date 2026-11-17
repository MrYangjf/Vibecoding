---
title: StaticVerifier-Tooling-Substitutes
date: 2026-10-30
updated: 2026-10-30
tags: [教训, 静态校验, 编译错误, Step2.6, 判据库, CSharp, 工具链]
status: active
---


# 静态校验判据库

> **本页是 [[project/vibecoding-workflow]] Step 2.6「正确性验证」的判据全文库。**
> SKILL（`~/.workbuddy/skills/vibecoding-llmwiki/SKILL.md`）的 Step 2.6 只保留**用法 + 分类索引 + 指向本页的一行**，判据正文全部在此 —— 流程归 LLMWiki，教训也归 LLMWiki。
>
> **判据来源**：2026-09-03 ~ 2026-10-08 期间被**真实编译器**抓出、或由静态校验自身误报而暴露的问题。日期即实证日期。


## 七、工具受限时的替代方案

### 7.0 ⛔ 「本机无 C# 编译器」是错误条文（2026-11-09 更正，已存在 10 天）

**旧条文**（曾写入 [[rules/KR-010-No-Compiler-Honesty]]）："本机 `dotnet` / `msbuild` / C# 编译器被安全策略拦截且无 Visual Studio：⛔ 不要浪费轮次找编译器。"

**事实**：
- 本机有 `dotnet 11`（`dotnet format style` 可跑，八则门禁实测有效）；
- 有 VS18 MSBuild 两套路径：`C:\Program Files\Microsoft Visual Studio\18\Insiders\MSBuild\Current\Bin\MSBuild.exe` 与 `C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\MSBuild\Current\Bin\MSBuild.exe`；
- 2026-11-02、2026-11-09 等多轮 `MSBuild /t:Rebuild` 实测 `errors=0 rc=0`，并刷新 `bin\Debug\AdaWeldSystem.exe`。

**存在时长**：2026-10-30 立条 → 2026-11-09 更正，共 **10 天**。

**影响过的判断**：
1. 这 10 天里的精简轮把编译门禁整段跳过，只以 `simplify_guard.py` 静态绿灯放行 —— 语义型/接线型缺陷（重载、泛型推断、装箱、参数漏传）**无任何环节能发现**。
2. 多份报告用「静态检查全过」替代编译结论，属用模式型证据冒充语义型结论。
3. `simplify_run.py` 的 `BUILD SKIP` 分支被当成常规路径，掩盖了「本机其实能编译」。

**教训**：工具链能力属**可实测事实**，不得凭一次失败就写成长期条文；条文里凡出现「本机没有 X」，必须附一条可复跑的验证命令与其输出。

**本轮实证**：`python scripts/simplify_run.py --build-only` 第 4 关输出 `build: errors=0 rc=0`（VS18 Insiders MSBuild），`bin\Debug\AdaWeldSystem.exe` 时间戳刷新。

### 7.1 反射被安全策略拦截时的 `.Designer.cs` 属性校验

`[Reflection.Assembly]::LoadFrom(<dll>)` 被拒（"Reflection.Assembly load APIs execute arbitrary .NET code"）。

> ⚠️ **2026-10-09 实测更新：该拦截已不复现**——PowerShell 5.1 会话里 `LoadFrom("3rdDepend\AntdUI.dll")` 成功，
> 且能真实跑布局（见 7.3）。本节差集法降级为「快速静态筛查」，**运行期语义一律优先用 7.3 实测**。

**替代**：为新 Designer **及全库每个 `.Designer.cs`** 建 `控件字段 -> 类型` 映射，收集各类型**被使用过的属性名**，做差集。差集 = 风险集。2026-09-16 实测剩 5 项，全是 WinForms 基类属性（`Label.Margin` ×4、`Timer.Interval`）⇒ 可证安全。

**同法适用于 `.cs` 侧 AntdUI API 调用**（`ColumnCollection` / `AntList<T>` / `.Binding()` / `EditMode` / `AutoSizeColumnsMode` / `.SetEditable(true)` / `FolderBrowserDialog.DirectoryPath` + `ShowDialog()` / `Message.*(Form,…)` / `Modal.Config(Form,…)`）：**先例计数 ≥1 + 现有文件里形状完全一致**，是**无编译器时可得的最强证据**。

### 7.2 `.Designer.cs` 重构是字节安全的、三元配对的操作

这些文件是 **no-BOM + 纯 CRLF**。⛔ **绝不整文件 `Write`。**

**字节流程**：`raw.split(b"\n")` → 改片段 → `b"\n".join(parts)`（`\r` 留在片段内，原 rules/KR-014（已并入 lessons/WikiDriftCorrectionPitfalls））。整行替换时要重新发出该行的 `\r`。

**每个重建的 `TableLayoutPanel`，三件事必须一致**，否则运行期布局抛异常：
1. `Controls.Add(ctrl, col, row)` 的最大索引 < `RowCount`/`ColumnCount`
2. `RowStyles.Count == RowCount`
3. `ColumnStyles.Count == ColumnCount`

**验证法是重建**：按序 dump `name -> (col,row)`，把每个 label/box 映射到它被赋的 `.Text`，再把网格读回成文本。

⚠️ **`ColumnStyles.Count` 比 `ColumnCount` 多 1 是既有的、良性的** —— 它在未改动的备份里就存在，跑了四次都没事；多出的 `20F` 只是没被用。对称计数判据会报假阳性，**改之前先与编辑前的备份比对**。

**删控件要删三处**（属性块 + `new` 实例化 + 成员声明）；`Visible = false` 不是删除。**改名的控件可以合法地保留旧 `Name` 而带新 `Text`**（如 `lblPvtKernelTitle` 配 `Text = "② 方向平滑"`）—— 标记命名遗留，**不要强改**，更不要当成残留死控件计数。

### 7.3 ⭐ 无编译器 ≠ 无法核实运行期语义：PowerShell 加载项目 DLL 直接实测（2026-10-09 建立）

「本机无编译器，X 语义无法核实」**不再是终审结论**。Windows PowerShell 5.1 = .NET 4.8 运行时，
可 `LoadFrom` 项目自带 DLL（`3rdDepend\AntdUI.dll` 等）实例化真实控件做**运行期实验**。
本轮用 7 轮探针把 AntdUI GridPanel/FlowPanel 的「逆序入格 / `_N` 判废 / `SetIndex` / 嵌套 Margin」全部定案，
并做 **A/B 几何对照**（原 TableLayoutPanel 规格 vs 新方案逐控件比 rect，20/20 全等）——
布局类改动从此可**交付前定量验证**，不再是「上机目视」一锤子买卖。

**探针纪律（4 条，均踩过）**：
1. **布局须真实句柄**：`Form.Show()`（屏幕外 Location）才触发布局引擎；`PerformLayout()`/`CreateControl()` 单独调用不动它（不可见控件 `CreateControl` 是空操作）；
2. **同会话反复建 Form 会间歇性 `New-Object` 返 null** ⇒ 每段探针开**新进程**（`powershell.exe -NoProfile -STA -File`）；
3. 反射私有解析函数（如 `GridPanel.ConvertToRects(Rectangle, String)`）可直接读布局中间结果；返回结构体若字段大小写重名（`X`/`x`），PowerShell ETS 报 CLS 错 ⇒ 用 `GetField('x').GetValue()` 取值；
4. 实验结论回写 wiki 时标明**探针法**，后人可复跑复核。

#### 7.3.1 ⛔ 探针的 4 条补充纪律（2026-10-10 三次踩坑后追加）

| # | 坑 | 症状 | 正解 |
|---|---|---|---|
| 5 | **脚本文件含中文即被按 GBK 解析** | PowerShell 5.1 读 `.ps1` 用系统 ANSI 码页，UTF-8 中文变乱码 ⇒ `字符串缺少终止符` 等**语法错误** | 探针脚本**全 ASCII**；中文文案用 `[char]0x5168` 拼；DLL 路径用 `Join-Path (Get-Location)` 而**非**字面量中文路径（ASCII 化后字面量也坏） |
| 6 | **执行策略拦截** | `无法加载文件…未进行数字签名` | `powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File …`；输出重定向到文件再读（Bash 管道会吞中文） |
| 7 | **`$host` 是只读保留变量** | `无法覆盖变量 host` | 函数形参别叫 `$host`（也别叫 `$input`/`$args`） |
| 8 | **`AntdUI.Panel` 任意属性 set 都报 CLS 错** | `Padding/padding` 大小写重名 ⇒ 一旦碰这个对象，之后**任何**属性赋值都失败 | 探针里用 WinForms `Panel` 当外壳（几何等价），只保留 `AntdUI.Button` 等无冲突控件 |

> ⚠️ **第 8 条的真实代价**：探针**无法 100% 复刻** `AntdUI.Panel` 当父容器的情形。
> 本轮正是因此把外层换成 WinForms `Panel` 才跑通 —— 结论「三按钮是否重叠」对两种父容器**都成立**（重叠是 WinForms Dock 语义，与父容器类型无关），故不影响有效性。

### 7.3.2 ⛔⛔ 布局类判据：**同父 + 多 `Dock=Fill` = 必然重叠**（2026-10-10 上机打回）

**症状**：筛选栏三个按钮（全选/全取消/反选）代码全对、事件全绑、静态校验 65/65 全绿，
**上机只看得到一个**（最后添加的那个压在最上层）。

**根因**：WinForms 同一父容器内，**同级子控件 `Dock` 相同时会取到同一矩形**。
探针实测：三个 `Dock=Fill` 按钮 `Bounds` **全等 `(0,0,226,34)`**。
⛔ **「三件套齐全 + 事件已绑 + 挂在容器里」完全不能证明「控件可见」** —— 可见性是**布局**问题，不是**接线**问题。

> ⭐ **可脚本化判据（拦住整类问题）**：
> ```python
> # 同一父容器内出现 >=2 个 Dock=Fill 的同级子控件 => 判为重叠
> parent_of[b] = re.search(r'this\.(\w+)\.Controls\.Add\(this\.%s(?:,\s*\d+,\s*\d+)?\);', des).group(1)
> fill_by_parent[parent_of[b]].append(b) if re.search(r'this\.%s\.Dock = System\.Windows\.Forms\.DockStyle\.Fill;' % b, des)
> ```
> ⚠️ **豁免**：父容器是 `TableLayoutPanel` 时**同父 + 多 `Dock=Fill` 是正确范式**
> （TableLayoutPanel 正是靠 `Dock=Fill` + 格位 `(col,row)` 分配区域，探针实测三个 Bounds 互不相同）。
> 判据必须显式列出豁免集：`{声明为 TableLayoutPanel 的字段名}`。
>
> ⛔ **并排多控件的正解 = `TableLayoutPanel` + `Controls.Add(ctrl, col, row)`**（项目内 10 个窗体先例，
> 如 `RecordConfigForm.uiTableLayoutPanel2`）；配套 `ColumnStyles` 各 `Percent 33.33333` + `Margin` 归零。

#### 7.3.3 ⛔ 判据的 `Dock` 正则：前缀写全 + 必须带自检（2026-10-10 判据空过实录）

写完「同父多 Fill」判据后跑阴性对照，**基线竟然 PASS** —— 判据是空的。
原因：正则写成 `System\.Windows\.DockStyle\.Fill`（漏了 `Forms.`），而 Designer 里是
`System.Windows.Forms.DockStyle.Fill` ⇒ **永不匹配** ⇒ 「无重叠」恒真。

> ⛔ **判据自检三件套（写完必做，否则等于没写）**：
> 1. **阴性对照**：拿**含该 bug 的版本**跑，必须 FAIL（用上一轮 output 包解出即可）；
> 2. **命中自检**：判据内部打印 `fill_by_parent`，**非空**才说明正则真能命中（本轮加为常驻判据项）；
> 3. **豁免集自检**：豁免集（TableLayoutPanel 字段名）非空，防止「豁免条件写错 ⇒ 全量误报或全量漏报」。
>
> ⚠️ 本轮在这三条上**来回改了 3 版判据**才稳住。⭐ **通则：判据报错先怀疑代码，判据「莫名其妙全绿」先怀疑判据空过。**

### 7.4 行替换「吃换行」的两种现场形态（2026-10-09 两次命中，当场抓到）

同文件 Edit 用「整行」做 `old_string` 时：① `old_string` 带了行尾而匹配到行中 → 替换后**两行并成一行**
（实测 `SelectFlowPanel;` 与下一行声明合并）；② 在「成员声明区」按孤立锚点追加 → **重复声明**（CS0102，
实测 `tableLayoutPanel1` 被插了第二份）。**判据**：§一「字段声明唯一」正则 + 大括号配平必须常开；
改声明区前先读上下文锚点（锚点须带足上下文，不许单行孤锚）。

---

## 相关页面

- [[lessons/StaticVerifier-CSharp-Scoping]] —— 同源拆分页
- [[lessons/StaticVerifier-Wiring-Integrity]] —— 同源拆分页
- [[lessons/StaticVerifier-Checker-FailureModes]] —— 同源拆分页
- [[lessons/StaticVerifier-Batch-Script-Traps]] —— 同源拆分页
- [[lessons/StaticVerifier-AdrNumbering]] —— 同源拆分页
- [[lessons/StaticVerifier-RecentJudgements]] —— 同源拆分页
- [[lessons/StaticVerifierJudgements]] —— 源页（拆分前全量）
