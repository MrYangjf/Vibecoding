---
title: 代码精简规范（精简代码区域 · 详尽版）
date: 2026-08-26
tags: [规范, 代码精简, 注释规范, 日志规范, 重构, 检查脚本]
status: accepted
---

# 代码精简规范（精简代码区域 · 详尽版）

> **用途**：本页是「代码精简」需求的**唯一标准源**。触发精简需求时，AI 直接读取本页执行，无需用户重复输入精简要求。由 [[index/index]] 的「代码精简规范」分类路由到此；沉淀决策见 [[decisions/ADR-038-CodeSimplificationStandard]]。
> **适用范围**：除 `*.Designer.cs`（设计器自动生成）外的全部业务源码（`UIDesign/` 下非设计器 `.cs` 同样适用五维度），且不触及外部厂商 SDK（即 `3rdDepend/` 下的 DLL 及相机/PLC 等厂商**原生** P/Invoke 签名、厂商**原生**数据结构定义不在整理范围；但项目中封装这些 SDK 的**自有逻辑代码**属于整理范围）。
> **工作单元**：以「一个文件夹」为整理单位，逐文件夹落地本规范。文件夹内每个 `.cs` 文件的具体审查可用检查脚本 `scripts/csharp_review.py` 逐文件扫描（详见第四节）。
> **版本说明**：2026-08-26 升级为详尽版——在原四维度粗版基础上，并入用户新建的 C# 代码审查规范（文件书写整理 / 逻辑精简 9 类 / 函数精简）与检查脚本。原设备日志规范（项目特有）保持不变。详细反例目录见文末「参考文件」。
> **范围裁定（易误读，必读）**：强制排除的**只有 `*.Designer.cs`**，`UIDesign/` 下非设计器 `.cs` 同样适用五维度 —— 详见 [[lessons/CodeSimplification-Scope-DesignerOnly]]。
> **落地进度快照**：2026-08-26 基线扫描进度表已归档至 [[project/CodeSimplification-Progress-20260826]]（历史快照，不随代码更新；新一轮扫描请在修复时另建）。

---

## 一、代码精简（五维度）

> 维度 ① 来自文件书写整理规则；② 来自原变量维度 + 逻辑规则 1；③ 来自原枚举维度 + 逻辑规则 5；④ 来自原逻辑维度 + 逻辑规则 2/3/4/6/7/8/9；⑤ 来自原辅助函数维度 + 函数精简规则。深度反例集见 [[standards/CodeSimplification-RefLogicSimplification]]、[[standards/CodeSimplification-RefFunctionSimplification]]、[[standards/CodeSimplification-RefFileOrganization]]。

### ① 文件书写整理：成员顺序、#region 划分、XML 注释

- **成员顺序固定**：类内自上而下为 `私有变量 → 公共变量(含属性/事件) → 构造函数 → 私有函数 → 公共函数`；嵌套类型/显式接口实现置后独立 region。不按"添加时间/迭代轮次"堆叠（AI 迭代常把新成员追加到类尾导致顺序混乱）。
- **#region 按成员类型划分**（中文名）：`#region 私有变量` / `公共变量` / `构造函数` / `私有函数` / `公共函数`。每个 region 有配对 `#endregion` 且不交叉嵌套；region 名用**类型名**而非功能名（禁止 `#region 新增功能` 这类写法）。
- **XML 注释**：`private` 方法**不写** `///`；`public`/`protected` 方法/属性/类**必须写** `///`（见第二节）。
- 详见 [[standards/CodeSimplification-RefFileOrganization]]。

### ② 变量与临时变量：提升反复新建的临时变量为具名私有成员

- 若某临时变量在同一方法内或同类多个方法中**被反复 new / 重新计算**，提升为类的 `private` 字段（`_camelCase` 具名），构造/初始化处一次性准备，方法中复用。
- 仅在某次调用内使用一次、生命周期限于方法栈的局部变量**保留为局部变量**，不强行提升（避免字段污染与线程隐患）。
- 提升后字段若多线程读写，保持既有同步手段（`volatile`/`lock`/`InvokeRequired`），不得因提升丢失同步。
- **禁止无意义临时变量**：名为 `temp`/`tmp`/`data`/`result`/`value` 且只使用一次、纯中转（`var temp1 = x; var temp2 = temp1;`）、把私有字段整体赋给同名局部变量后全程用局部变量等，应内联或改为有业务含义的命名。
- **禁止无意义 null 判断**（逻辑规则 2）：仅公共 API 边界/反序列化/UI 事件/第三方回调等确实可能为 null 处保留一次校验；对 `new` 结果、值类型（`int`/`bool`/`DateTime`/`enum` 等）、`this`、刚创建对象、本文件内私有方法参数（调用链上游已保证非空）的 null 检查均属冗余。详见 [[standards/CodeSimplification-RefLogicSimplification]] 第 2 节。

### ③ 枚举与事件：去重合并 + 禁止过度枚举

- 同类型功用的枚举只保留**一份**；子命名空间不得重复定义父命名空间已有枚举（见 [[decisions/ADR-026-EnumDeduplication]]）。
- 功能等价、命名不同但语义重复的枚举合并为一个（合并前 Grep 全量追溯引用并同步改名）。
- 事件同理：同一通知语义只保留一个事件；避免 `XxxChanged`/`OnXxx`/`XxxEvent` 三套并存。
- 合并属**跨文件变更**，必须 Grep 全量追溯引用并完成改名，禁止留下孤立旧枚举/旧事件。
- **禁止过度枚举**（逻辑规则 5）：二值状态用 `bool` 而非枚举；只在一处使用/只定义不消费的常量用 `private const`；枚举命名不加 `Enum` 后缀；`[Flags]` 仅在确实按位组合时使用。详见 [[standards/CodeSimplification-RefLogicSimplification]] 第 5 节。

### ④ 函数逻辑：去冗余、去嵌套、去互锁，并消除 9 类冗余

- 函数内部已写过安全校验/锁定/状态判定逻辑，**调用处不得二次书写同一套逻辑**（如函数已判空+加锁，调用方不要再判空+加锁）；线程内部不得补充与函数体重复的判定/锁；判定与锁的真相源唯一。
- 减少不必要的 `if` 嵌套与 `return` 前重复条件；能提前 `return` 的卫语句优先，减少深层缩进。
- 不引入新的互锁/重入保护，除非原有逻辑确实缺失（缺失属 Bug，单独记录）。
- **9 类禁止项**（逐项判定标准与 AI 高频反例见 [[standards/CodeSimplification-RefLogicSimplification]]）：
  1. 优先用类私有变量，控制临时变量（见 ②）
  2. 禁止无意义 null 判断（见 ②）
  3. **禁止无意义安全锁**：`lock(new object())` 完全无效；避免 `lock(this)`/`lock(typeof)`/`lock("字符串")`；UI 线程（WinForms/WPF）单线程上下文不加锁；锁对象须 `private readonly object`；锁内只做内存操作（禁 Sleep/IO/MessageBox）；非多线程访问的代码无脑加锁属冗余。
  4. **禁止无意义函数值赋值传递**：`return result;` 直接 `return` 表达式；参数原样赋给同名局部变量；纯透传的多层方法链（A→B→C 每层只加一行日志）应合并；`this.X = X;` 自赋值。
  5. 禁止过度枚举（见 ③）
  6. **禁止过度设定属性**：类外从不访问的值用私有字段；构造后不变用只读属性 `{ get; }` 或 `readonly` 字段；属性 get 不含重逻辑/副作用；集合属性返回只读包装或提供 Add/Remove，不返回内部可变引用。
  7. **禁止过度等待/延迟**：`Thread.Sleep` 等待异步、`while(!done) Sleep` 轮询、`Task.Run().Wait()`/`.Result` 阻塞（UI 线程尤忌死锁）、无超时 `WaitOne()` 均属冗余；异步用 `await`、条件等待用事件/信号量/回调。
  8. **禁止过度缓存数据**：只写不读、一次性数据、多层重复、无失效机制的静态缓存属冗余；方法间传值用参数而非字段（隐式参数耦合不是缓存）；缓存不可变数据或返回副本，避免可变对象引用污染。
  9. **禁止过度资源管理**：仅真正 `IDisposable`（文件流/连接/网络流/GDI 对象/WaitHandle）才 `using`/`Dispose`；纯托管对象不写终结器/`GC.Collect()`；GDI 对象（`Pen`/`Brush`/`Font`/`Graphics`/`Image`）用 `using`；`Dispose` 时取消事件订阅。

### ⑤ 辅助函数：归集重复 + 功能重叠合并 + 嵌套内联 + 死函数清理

- 同类辅助计算/类型转换/生成值等，若在**多个位置重复编写**，归集到所属文件夹就近的 `Helper`/`Utility` 私有静态方法，保留原行为，对外签名不变。
- 不跨区域随意新建公共工具类；优先模块内就近归集（见 [[project/vibecoding-workflow]] 模块边界约束）。
- **功能重叠合并**（函数精简规则 1）：AI 迭代倾向"新增函数而非改已有函数"，导致 `GetOrder`/`GetOrderEx`/`GetOrderV2`/`GetOrderWithDetail` 等同簇堆叠、或 `ProcessOrderWithNotificationAndLog` 只多一两步。判定：同动词+同宾语、一个函数是另一个超集、70% 以上方法体相同、仅参数默认值不同、只调另一个并加 null/日志——应合并（可选参数或内部条件分支）；合并**不修改对外函数签名**（public 保留薄包装或在报告中标注确认后删除）。
- **嵌套内联**（函数精简规则 2）：`private` 方法仅被 1 处调用、方法体 ≤3 有效行、无复杂控制流、命名只是"做某动作"——内联到调用方（递归/virtual/接口实现/P-Invoke/被委托事件反射引用/多处复用表达独立概念者保留）。
- **死函数清理**（函数精简规则 3）：`private` 方法本文件内零调用且无委托/事件/`nameof` 引用——确认后删除（外部引用按约束不延伸，但报告中提示用户确认）。
- 详见 [[standards/CodeSimplification-RefFunctionSimplification]]。

---

## 二、注释精简（三规则 + XML 注释规范）

### ① 减少不必要的说明注释

- 注释**只解释代码「做什么 / 为什么这样做」**，不对版本、过程、由来做解释（这些内容由 LLMWiki 知识库记录，不在代码里复述）。
- 删除「2026-XX 修改」「原因为…」「参考某次需求」之类过程性注释；删除显而易见、与代码同义的注释（如 `// 赋值` `// 循环`）。

### ② 函数外用 `///` 注释（标准化，不限公私）

- 无论 `public`/`protected`/`private`，只要写 `///` 注释就**必须符合 XML 注释规范**（summary 一行 + param/returns 完整）。
- `public`/`protected` 方法/属性/类/接口的 `/// <summary>` **建议写**（对外接口应有文档）；`private` 方法**可选**（复杂逻辑或不易理解的私有方法建议写，简单方法可不写）。
- `/// <summary>` 20 字内，动词开头描述"做什么"，不写过程/实现步骤/调用链（错误：`先校验参数然后调用 Repository 插入…`；正确：`创建订单`）。
- 类/结构体/枚举/接口 的 `/// <summary>` 必须一行完成，20 字内，不写多行。
- 每个 `<param name="x">` 说明参数含义/取值范围/是否可 null/单位/枚举语义，**不重复参数名本身**（错误 `<param name="order">order</param>`）；有返回值写 `<returns>` 说明 true/false 各自含义，不写"返回结果"废话；仅当调用方应感知并处理的异常才写 `<exception>`。
- C# 7.3 注意：不用 `string?` 可空性标注、不用 `<inheritdoc/>` 偷懒；泛型尖括号转义 `List&lt;T&gt;`。

### ③ 函数内用 `//` 注释

- **复杂逻辑**才加 `//`，解释内部变量意义、非显而易见的算法意图。
- **简单逻辑不写注释**（单步赋值、普通循环、常见判空）。

---

## 三、设备日志规范（项目特有，保持不变）

### ① 日志内容不使用符号，用文字表述

- 日志字符串中**不使用** `:` `=` `,` `()` `{}` `->` `|` 等符号分隔语义，改用**纯文字**表述。
- 反例：`连接失败: 192.168.0.11 (错误码: 1001)` → 正例：`连接失败 目标地址 192.168.0.11 错误码 1001`
- 数字、地址、错误码等**值本身**可保留（是内容不是分隔符号）；禁止用符号做「键:值」式排版。

### ② 日志记录时机：功能块始末，不额外增加

- 一个功能块的**开始**处记一条；能**反馈结果**的位置（成功/失败）记一条。
- **不**在中间每一步都记日志，不重复记、不冗余记。
- 示例：功能块开始 → `开始连接正运动控制器`；结果 → `正运动控制器连接成功` 或 `正运动控制器连接失败 错误码 1001`。

### ③ 通讯日志规范：全记录

- **通讯内容采用全记录模式**：通讯收发的内容（原始报文 / 解析后的关键字段）完整记录，便于排查。
- **开启 / 关闭通讯动作属于「设备日志」**（按①②记录始末即可）。
- **通讯建立监听之后，到停止监听之前的交互内容（收发报文）属于「通讯日志」**，采用全记录模式，不省略、不摘要。

### ④ 去符号执行细则（2026-08-21 第二轮补充）

- 除 `: = , ( ) { } -> |` 外，**`→`、全角 `：`、`（）`、半角括号、`=` 拼接（如 `IP={0}`）、`;` 等一律改为纯文字**。
- **保留**：`string.Format` 的占位符 `{0}` 及格式说明符（如 `{0:F2}` 中的冒号）；数值/地址/错误码本身；`[3/5]` 类步骤序号标记；`IP 192.168.0.11` 值本身。
- 中文全角补充性括号（如 `（整设备待机）`）属中文内容，可保留；半角括号一律去除。
- **英文 SDK 风格日志**（封装层自有逻辑）同样中文化去符号，如 `ROI initialized from INI: (x, y)` → `ROI 从 INI 初始化 起点 x y 宽 w 高 h`。
- 检查残留用 Grep：`(Log|ShowLog|HandleFailure|TryTransition|TransitionTo|ErrorInfo)[^"]*"[^"]*[;=,:|→][^"]*"` 应仅剩 UIDesign 与 Format 占位符。
- **⚠️ 检查盲区与兜底方法（2026-08-21 全量检测补充）**：上述正则只匹配**单行** Log 调用且只覆盖命令通道。实际漏网场景：
  1. **跨行调用**：`ShowLog(_tag,\n string.Format("...：...", ...))` 换行书写时正则失效 → 兜底用全量字符串扫描 `"[^"]*[：:][^"]*"` 甄别（排除 Format 占位符 `{0:F2}`、时间格式、文件路径、XML 报文、三元表达式）。
  2. **非命令通道**：`FailedItems.Add("...: ...")`、`throw new InvalidOperationException("...：...")`、图像叠加文本（`DrawTextOnImage`）、提示文案（`PathFallbackMessage`）等同样含符号，按同口径去符号。
  3. **模块整合/迁移后必须复跑**：SafetyInterlock.cs 因 ADR-036 整合迁入 Workflow 时未纳入清理，残留 7 处 FailedItems 符号 → 迁移/合并文件后复跑本检查。

---

## 四、检查脚本 `scripts/csharp_review.py`

> 配套单文件静态扫描器，由用户新建的 C# 代码审查规范衍生。用于逐文件机械标记冗余候选，**不替代人工语义判定**——脚本输出需结合业务确认。

**边界约束（不可违反）**：

1. 只处理**单个** `.cs` 文件，不跟踪项目引用、不跨文件分析。
2. **不处理 `*.designer.cs`**（设计器自动生成文件直接跳过）。
3. 不延伸到外部引用文件——问题只在当前文件内解决。
4. **不修改对外函数接口**：public/protected 方法签名（名称、参数、返回类型）不变。
5. **不修改对外变量名称**：public 属性/字段名不变。
6. 修复时优先改动 `private` 成员；涉及 public 成员的问题只报告不自动改。

**用法**：

```bash
python3 scripts/csharp_review.py <目标文件.cs>            # 默认报告（折叠提示级）
python3 scripts/csharp_review.py <目标文件.cs> --verbose  # 含提示级全部项
python3 scripts/csharp_review.py <目标文件.cs> --json     # JSON 输出（供工具消费）
```

**输出类别**（与本规范对应）：

| 类别 | 对应规范维度 | 检查内容 |
|------|--------------|----------|
| A. 文件书写整理 | ① | 成员顺序、#region 划分与配对、XML 注释（public 必写/私有不写/summary≤20字/param/returns）|
| B. 代码逻辑精简 | ② ③ ④ | 无意义 null 检查、无意义锁、冗余赋值传递、过度枚举、过度属性、过度等待/延迟、过度缓存、过度资源管理、临时变量滥用 |
| C. 函数精简 | ⑤ | 功能重叠（token 相似度≥50% 或超集关系）、嵌套内联候选（private 仅 1 调用且 ≤3 行）、疑似死函数 |

**严重级别**：`error`（确定 bug/严重违规，如 `lock(new object())`，必须改）/ `warn`（高概率冗余，逐条确认）/ `info`（风格建议，按需处理）。有 error/warn 时脚本退出码非零。

**成员顺序判定口径（2026-08-31 明确）**：脚本按 `fields/properties` 私有=1、公共=2，`#ctor`=3，`private` 方法=4、`public`/`protected` 方法=5 排序。
**`protected` 方法按公共层级（5）计**，因此**必须排在所有 `private` 方法（4）之后**——即类体内先私有方法、后 protected 覆写、再 public 方法。把 `protected override` 放在私有方法之前会触发 A 类「成员顺序错误」告警。

**有意例外：`Thread.Sleep` 周期轮询（2026-08-31 补充）**：④-7「禁止过度等待」针对的是**等待异步操作完成**（`Wait()`/`.Result`/轮询标志位）。**周期性轮询节拍**（如安全监控 `MonitorLoop` 按固定周期读 PLC）用 `Thread.Sleep` 是正确实现——此类场景无推送事件源，改用 Timer 会降级线程优先级。遇此告警按语义判定后保留，并在报告中标注为有意例外。

**脚本缺陷已修复（2026-08-31）**：`csharp_review.py` 的「属性注释检查」代码块此前被误置在 `_check_method_doc_quality()` 内且缩进进了 `if 有返回值` 分支，导致扫描含返回值方法的文件时抛 `NameError: name 'source' is not defined`，整个文件扫描失败。现已将该块移回 `check_doc_comments()` 作为独立的属性循环（每个类只跑一次）。若再遇 `扫描出错` 提示，先复跑确认并修脚本本体，勿误判为被扫描文件的问题。

**与文件夹工作单元的衔接**：脚本以单文件为粒度；落实本规范的「按文件夹」工作单元时，对文件夹内每个非 `designer.cs` 文件逐文件跑脚本，汇总 warn/error 后人工裁定，再统一修复并复跑至清零。

**推荐：按顶层文件夹扫描（进度可见 + 卡死可定位）**：全盘一次性平铺所有 `.cs` 文件时，既慢又无法判断卡在哪个文件/文件夹。改为**逐顶层文件夹扫描**——每进入一个文件夹打印 `>> [开始] <文件夹名>`，该文件夹内所有文件扫完后打印 `<< [完成] <文件夹名> 文件=N 错误=E 警告=W 提示=I`；若某文件夹始终不出「完成」行，即可锁定卡死位置。具体约定：

- **扫描范围** = `AdaWeldSystem/` 下**业务源码顶层文件夹**（排除 `*.Designer.cs` 即设计器自动生成、`3rdDepend/` 即厂商 SDK、`bin/`、`obj/`、`deliverables/`、`Resources/`、`Properties/` 等非源码目录；**`UIDesign/` 下非设计器 `.cs` 纳入扫描**）。
- **单文件超时保护**：每个文件调用加 `timeout 30`（单文件超时 30s 即跳过并标记 `!! [卡住]`），避免个别大文件/异常语法拖垮整轮。
- **增量落盘**：每个文件夹扫完即把汇总追加写入结果文件（`scripts/scan_by_folder.tsv`），中途中断也可查看已完成部分。
- **优先级**：汇总后按「错误+警告」降序排出高冗余文件夹，优先精简。

辅助脚本见 `scripts/scan_by_folder.sh`（用法：`bash scripts/scan_by_folder.sh [ROOT]`；`ROOT` 省略默认 `AdaWeldSystem/`）。运行环境用托管 Python：`PY_EXE` 可覆盖，默认 `C:/Users/yangjingfeng/.workbuddy/binaries/python/versions/3.13.12/python.exe`。

---

## 五、与其他规范的边界

| 已有约束 | 关系 |
|---|---|
| [[decisions/ADR-002-CS73-Constraint]] | 精简后仍须 C# 7.3 语法，禁用 switch 表达式 / 可空引用 / init / record 等 |
| [[decisions/ADR-026-EnumDeduplication]] | 本规范 ③ 枚举去重的具体执行依据 |
| [[decisions/ADR-001-DisposePattern]] / [[decisions/ADR-034-DisposePatternFullCoverage]] | 精简**不得**新增或重写 `Dispose(bool)`；非 UI 类保持标准 `IDisposable.Dispose()`（与 ④-9 禁止过度资源管理一致）|
| AGENTS.md Region 完整性 | `#region`/`#endregion` 必须配对，精简不得遗留孤立 `#endregion`（见 ①）|
| 公共接口契约 | 精简**不得**改变公共类型/方法签名与枚举成员名（除非走 ③ 合并流程并全量改名）；检查脚本亦不自动改 public 成员 |
| .csproj 注册 | 若因精简新建 .cs 文件，必须注册到 `AdaWeldSystem.csproj` |
| [[standards/UiStateSimplification]] | UI 层状态判断与控制**细则**（本地 bool 缓存设备态/单一控制函数/统一刷新入口/集中状态标签）由该页专管；`UIDesign/` 非设计器 `.cs` 的 ①②⑤ 维度（成员排序/变量/辅助函数）与 ③④（枚举事件/逻辑）仍由本页覆盖 |

---

## 六、执行清单（按文件夹）

对每个业务源码文件夹执行（含 `UIDesign/` 下非设计器 `.cs`；逐文件可辅以 `scripts/csharp_review.py`）：

- [ ] ① 文件按 私有变量→公共变量→构造函数→私有函数→公共函数 排序，#region 按类型划分且配对
- [ ] ② 提升反复新建的临时变量为私有字段；消除无意义临时变量与 null 检查
- [ ] ③ 枚举/事件去重合并（Grep 全量追溯）；移除过度枚举
- [ ] ④ 删除调用处与函数体重复的判定/锁/互锁，减少嵌套；消除 9 类冗余（锁/赋值传递/属性/等待/缓存/资源管理）
- [ ] ⑤ 归集重复辅助函数到就近 Helper；合并功能重叠函数；内联单层嵌套 private 方法；删除死函数
- [ ] 注释按第二节精简（`///` 标准化：无论公私，写了就要 summary 一行 + param/returns 完整；public/protected 建议写，private 可选；复杂逻辑才 `//`；类级 summary 一行 20 字）
- [ ] 日志按第三节改写（去符号、控时机、通讯全记录）
- [ ] 自审：无 ADR/Lessons 违反、无公共签名变更、region 配对、Dispose 未动
- [ ] 复跑 `scripts/csharp_review.py` 至 warn/error 清零（designer.cs 跳过）

### 已覆盖模块（历史轮次，粗版阶段）

| 轮次 | 日期 | 覆盖模块 | 重点 |
|------|------|---------|------|
| 第一轮 | 2026-08-21 | Comm / LineLaserCam / FileOperate / DeviceStateMachine | 日志归集 + 去符号 + 注释精简 |
| 第二轮 | 2026-08-21 | Workflow（Safety/PCL） / PCLOperate / SafetyInterlock | 状态机日志去符号 + FailedItems 去符号 + 注释精简 |
| 第三轮 | 2026-08-21 | EmguALG / MotionControl / WeldParamControl / SqlLiteDatabase / Workflow残留 / IntelligentLaserCam补漏 | 异常消息去符号 + 剩余模块注释精简 + 符号漏网补漏 |

> 未覆盖（不在精简范围）：`*.Designer.cs`（设计器自动生成）、厂商 SDK 原生代码（SmartRay ApiCore 等）、`3rdDepend/`

---

## 附：参考文件索引（详尽反例与脚本工作流）

- [[standards/CodeSimplification-ReviewWorkflow]] —— 检查脚本工作流（4 步：扫描→逐类审查→报告→确认后修复）
- [[standards/CodeSimplification-RefFileOrganization]] —— 文件书写整理规则全文（成员顺序/region/XML 注释 + AI 高频反例）
- [[standards/CodeSimplification-RefLogicSimplification]] —— 逻辑精简 9 类禁止项全文（判定标准 + AI 高频反例 + 修正方向）
- [[standards/CodeSimplification-RefFunctionSimplification]] —— 函数精简规则全文（功能重叠/嵌套内联/死函数 + 判定流程 + 例外）
- `scripts/csharp_review.py` —— 单文件静态扫描器（A/B/C 三类，error/warn/info 三级）
- `scripts/scan_by_folder.sh` —— 按顶层文件夹批量扫描器（进度可见 + 单文件超时 + 增量落盘 `scan_by_folder.tsv`，推荐全盘巡检用）
