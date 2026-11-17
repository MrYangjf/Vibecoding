---
title: 代码精简规范（精简代码区域 · 详尽版）
date: 2026-08-26
tags: [规范, 代码精简, 注释规范, 日志规范, 重构, 检查脚本]
status: accepted
---

# 代码精简规范（精简代码区域 · 详尽版）

> **用途**：本页是「代码精简」需求的**唯一标准源**。触发精简需求时，AI 直接读取本页执行，无需用户重复输入精简要求。由 [[index/index]] 的「代码精简规范」分类路由到此；沉淀决策见 [[decisions/ADR-007-CodeSimplificationStandard]]。
> **适用范围**：除 `*.Designer.cs`（设计器自动生成）外的全部业务源码（`UIDesign/` 下非设计器 `.cs` 同样适用五维度），且不触及外部厂商 SDK（即 `3rdDepend/` 下的 DLL 及相机/PLC 等厂商**原生** P/Invoke 签名、厂商**原生**数据结构定义不在整理范围；但项目中封装这些 SDK 的**自有逻辑代码**属于整理范围）。
> **工作单元**：以「一个文件夹」为整理单位，逐文件夹落地本规范。文件夹内每个 `.cs` 文件的具体审查可用检查脚本 `scripts/csharp_review.py` 逐文件扫描（详见第四节）。
> **版本说明**：2026-08-26 升级为详尽版——在原四维度粗版基础上，并入用户新建的 C# 代码审查规范（文件书写整理 / 逻辑精简 9 类 / 函数精简）与检查脚本。原设备日志规范（项目特有）保持不变。详细反例目录见文末「参考文件」。
> **范围裁定（易误读，必读）**：强制排除的**只有 `*.Designer.cs`**，`UIDesign/` 下非设计器 `.cs` 同样适用五维度 —— 详见 [[lessons/CodeSimplification-Scope-DesignerOnly]]。
> **落地进度快照**：2026-08-26 基线扫描进度表已归档至 [[project/CodeSimplification-Progress-20260826]]（历史快照，不随代码更新；新一轮扫描请在修复时另建）。

---

## 一、代码精简（五维度）

> 维度 ① 来自文件书写整理规则；② 来自原变量维度 + 逻辑规则 1；③ 来自原枚举维度 + 逻辑规则 5；④ 来自原逻辑维度 + 逻辑规则 2/3/4/6/7/8/9；⑤ 来自原辅助函数维度 + 函数精简规则。深度反例集见 [[standards/CodeSimplification-RefLogicSimplification]]、[[standards/CodeSimplification-RefFunctionSimplification]]、[[standards/CodeSimplification-RefFileOrganization]]。

### ① 文件书写整理：成员顺序、#region 划分、XML 注释

- **成员顺序固定（2026-10-26 裁定：按 `#region` 分段判定，跨 region 不比较）**：每个 `#region` 段内自上而下为 `私有变量 → 公共变量(含属性/事件) → 构造函数 → 私有函数 → 公共函数`；嵌套类型/显式接口实现置后独立 region。不按"添加时间/迭代轮次"堆叠（AI 迭代常把新成员追加到类尾导致顺序混乱）。
- **#region 两种命名并存**（2026-10-26 修订）：**语义 region**（按功能块，如 `#region CSP 步骤输出`）与**类型 region**（`#region 私有变量` / `公共变量` / `构造函数` / `私有函数` / `公共函数`）**并存允许**，按文件实际情况择一或混用；**硬要求只有一条——`#region` 与 `#endregion` 必须配对、不交叉嵌套**，且 region 名**禁含**「新增功能」「临时」「TODO」这类过程性命名。⛔ 原「region 名必须用类型名、禁用功能名」条款**已废止**（与全库现状冲突：153 个非设计器 `.cs` 的 region 配对 100% 合规，而类型 region 覆盖率为 0；全量改写将挤掉有语义的 region）。
- **XML 注释**（2026-10-26 业主裁定，三条并存）：① `public`/`protected` 方法/属性/类 —— **新增或改动必须写** `///`；**存量欠账不追溯**（全库 public 成员 XML 覆盖率经实测为 0，共 2,217 处 warn，逐文件夹渐进偿还，**不设全库清零目标**）。② `private` 方法/属性 —— **允许且建议写** `///` 做总结（用于说明作用与关键约束），**不强制**；⛔ **不得据此删除既有 private `///`**（删除是信息损失，不属于精简）。③ 无论公私，**写了就要符合 XML 规范**（summary 一行 ≤20 字 + param/returns 完整）。口径依据见第二节顶层裁定第 3 条；对应判据与执行入口见 [[standards/CodeSimplification-Tooling]] 的「口径-判据映射表」。
- 详见 [[standards/CodeSimplification-RefFileOrganization]]。

### ② 变量与临时变量：提升反复新建的临时变量为具名私有成员

- 若某临时变量在同一方法内或同类多个方法中**被反复 new / 重新计算**，提升为类的 `private` 字段（`_camelCase` 具名），构造/初始化处一次性准备，方法中复用。
- 仅在某次调用内使用一次、生命周期限于方法栈的局部变量**保留为局部变量**，不强行提升（避免字段污染与线程隐患）。
- 提升后字段若多线程读写，保持既有同步手段（`volatile`/`lock`/`InvokeRequired`），不得因提升丢失同步。
- **禁止无意义临时变量**：名为 `temp`/`tmp`/`data`/`result`/`value` 且只使用一次、纯中转（`var temp1 = x; var temp2 = temp1;`）、把私有字段整体赋给同名局部变量后全程用局部变量等，应内联或改为有业务含义的命名。
- **禁止无意义 null 判断**（逻辑规则 2）：仅公共 API 边界/反序列化/UI 事件/第三方回调等确实可能为 null 处保留一次校验；对 `new` 结果、值类型（`int`/`bool`/`DateTime`/`enum` 等）、`this`、刚创建对象、本文件内私有方法参数（调用链上游已保证非空）的 null 检查均属冗余。详见 [[standards/CodeSimplification-RefLogicSimplification]] 第 2 节。

### ③ 枚举与事件：去重合并 + 禁止过度枚举

- 同类型功用的枚举只保留**一份**；子命名空间不得重复定义父命名空间已有枚举（见 [[decisions/ADR-003-EnumDeduplication]]）。
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

**语法简化八则（2026-10-29 增补，2026-10-30 扩至八则，对齐 VS IDE 建议）**：

- **IDE0017 对象初始化器**：`new T()` 后紧跟、且中间无其他使用的连续属性赋值，合并为 `new T { A = ..., B = ... }`；赋值顺序不得改变（有顺序副作用的 setter 保持原序）。
- **IDE0018 内联变量声明**：先声明、下一条语句立即赋值的局部变量，合并为声明即赋值；独立声明的 `out` 实参改为 `out var x` / `out T x`（C# 7.3 合法）。
- **IDE0031 空值传播**：`if (x != null) x.M();` → `x?.M();`；`x == null ? null : x.Y` → `x?.Y`。仅限**引用类型**且接收者为局部变量/字段（无随调用变化的 getter）；含 `else` 分支、多语句 body、或左值为属性的赋值**不得**改写。
- **IDE0019 模式匹配**：`var x = o as T; if (x != null) ...` → `if (o is T x) ...`；否定式 `if (!(o is T x)) return;` 等价于原 `as` + 判空。
- **IDE0059 不必要赋值**：局部变量的初值在首次读取前必被覆盖（如先声明默认值再在 `try`/分支内赋值）→ 删除初值；`out` 实参值全程未使用 → 改 `out _` 弃元。**例外**：`&&`/`||` 链中**非首项**的 `out` 变量、跨分支后仍需读取的变量，其默认值属编译器「确定赋值」要求，保留并加注释。
- **IDE0220 补显式强制转换**：`ArrayList`/非泛型集合取出的 `object` 赋给具体类型时补 `(T)`，避免隐式转换歧义。
- **IDE1005 条件委托调用**：`if (d != null) d(...)` → `d?.Invoke(...)`（仅限委托字段/局部变量；事件 `event` 只能在声明类型内这样调用）。
- **IDE0270 简化空值检查**：`if (x == null) throw ...; return x;` → `return x ?? throw ...`；`if (x == null) x = new T();` → `x ??= new T()`（C# 8 语法，C# 7.3 下**不适用**，保持 if 写法）。
- **批改方式**：一律用官方 Roslyn 修复器 `dotnet format style --diagnostics IDE0017 IDE0018 IDE0019 IDE0031 IDE0059 IDE0220 IDE1005 IDE0270`，判据为 `simplify_run.py` 第 5 关「0 诊断」；⛔ 禁止手写正则批量改写（会破坏注释/缩进/行尾）。**修复器对非字面量初值会退化为 `_ = expr;` 弃元语句 → 必须人工复核并把该死语句删掉**。

### ⑤ 辅助函数：归集重复 + 功能重叠合并 + 嵌套内联 + 死函数清理

- 同类辅助计算/类型转换/生成值等，若在**多个位置重复编写**，归集到所属文件夹就近的 `Helper`/`Utility` 私有静态方法，保留原行为，对外签名不变。
- 不跨区域随意新建公共工具类；优先模块内就近归集（见 [[project/vibecoding-workflow]] 模块边界约束）。
- **功能重叠合并**（函数精简规则 1）：AI 迭代倾向"新增函数而非改已有函数"，导致 `GetOrder`/`GetOrderEx`/`GetOrderV2`/`GetOrderWithDetail` 等同簇堆叠、或 `ProcessOrderWithNotificationAndLog` 只多一两步。判定：同动词+同宾语、一个函数是另一个超集、70% 以上方法体相同、仅参数默认值不同、只调另一个并加 null/日志——应合并（可选参数或内部条件分支）；合并**不修改对外函数签名**（public 保留薄包装或在报告中标注确认后删除）。
- **嵌套内联**（函数精简规则 2）：`private` 方法仅被 1 处调用、方法体 ≤3 有效行、无复杂控制流、命名只是"做某动作"——内联到调用方（递归/virtual/接口实现/P-Invoke/被委托事件反射引用/多处复用表达独立概念者保留）。
- **死函数清理**（函数精简规则 3）：`private` 方法本文件内零调用且无委托/事件/`nameof` 引用——确认后删除（外部引用按约束不延伸，但报告中提示用户确认）。⛔ **2026-10-10 业主裁定覆盖本条**：0 消费成员（含 private 死函数）**一律只报告不删**，是否删除由业主逐案裁决（见第二节顶层裁定第 2 条）。**2026-10-29 业主批准批次 A 例外删除 16 个**（见裁定 2a / B-5）；其余仍只报不删。
- 详见 [[standards/CodeSimplification-RefFunctionSimplification]]。

---

## 一之二、本项目已落地的精简范式（2026-09-22 实操沉淀）

> 触发本轮精简的用户口径三条：① **对象与类型调用必须明确**——禁业务层 `as` 转型、禁自建对象绕过既有访问口（如轴只能由 `MontionManager` 创建与下发）；② **函数内判断集中化**——抽象判断辅助成员，消临时变量与重复状态判断；③ **近义变量清理**——不同轮次修复留下的同义变量须合并或注明差异。

| 范式 | 做法 | 反例（2026-09-22 已修） |
|---|---|---|
| 判断辅助属性 | 散落的同一判断收敛为私有只读属性，调用处只读属性 | 方法内 `bool sim = DeviceControlWork.Instance.IsSimulationEnabled;` 后再判 `if (sim)`；同类判断在 8 处各写一遍 |
| 限频判定统一入口 | `IsElapsed(last, ms)`（只判定）+ `TakeElapsed(ref last, ms)`（命中推进时刻），日志限频与周期补记共用 | 5 处手写 `if ((DateTime.Now - _x).TotalMilliseconds >= 5000) { _x = DateTime.Now; ... }` |
| 单拍函数拆分 | 「门控 → 闭环计算 → 写段 → 观测」逐层拆开，每层 ≤40 行 | 单方法 121 行：门控、闭环计算、写段、三处限频日志混排（`OutputCspTick`） |
| 同调用链不重复判空 | 上游卫语句已判的，下游不重写（由唯一调用者/基类保证），并在注释标注「由调用方保证」 | `CspTick` 判 `_seamAxis == null` 后调 `OutputCspTick`，后者又判一次 |
| 能力经基类虚属性暴露 | 厂商特有反馈由基类 `virtual` + 子类 `override` 暴露，UI/业务层不做 `as` | `(axis as DeltaMontionAxis)?.LastCommand ?? string.Empty` |

> 落地实例与验证见 `logs/log.md` 2026-09-22 条目与 [[api/MotionControlWorkflow]]「判断辅助属性」小节。

### ⑥ 同类指令单一入口 + 内部 switch 分派（2026-11-09 业主裁定）

- **适用范围**：同一设备族的同类动作指令，例如 TA 族的 Auto / Retract / Break / Pose1 / Pose2 / ZeroPose。**禁止**为每条指令各写一个平行的公开方法。
- **表达方式**：一个公开入口 + 指令枚举（或参数）+ 内部 `switch` 分派；调用方只改传参，不改变调用形状。
- **内部允许分组**：入口 `switch` 只做转调，实现按语义分三组（进入力矩 / CSP 定位 / 零位定位），单分支不得膨胀成巨型方法。
- **形态必须一致**：同一设备族的同类指令，阻塞/异步形态不得混用；若确有异步需求，全族一起改，**不得为单条指令留特例**。
- **不卡 UI 的落实方式**：阻塞只允许发生在后台指令执行体（如 `InstructionWorker`、`thIOWork`）内；UI 只发起调用并消费结果/状态事件，⛔ 禁止 UI 线程同步执行指令，⛔ 禁止 UI 侧等待循环或事件等待。
- **自动流程约束**：自动流程对某设备族**只允许调用「自动」这一条指令**（如 TA 族只调 `TA_Auto`），且必须**同步等待到结果**后再继续：成功→反馈完成信号继续；失败/超时→反馈失败信号按失败处理，⛔ 不得静默继续、不得靠超时蒙过去。初始化自检中的零位动作属初始化流程，不受此限。
- **日志等值**：指令名由枚举参数带入日志，其余文案逐字不变。
- **判据**：`C.平行指令入口`（同类中 ≥3 个同前缀、无参、同返回类型的公开方法 → info）。

### ⑦ 单例取用：类级缓存优先（2026-11-10 业主裁定 · C17）

- **优先级**：`Workflow` 类先声明 1 个类级私有属性 `private static T Manager { get { return T.Instance; } }`，方法内一律用 `Manager`；**方法内局部声明全部清掉**。
- **为什么可缓存**：`Instance` 为 `Lazy<T>`，进程内只构造一次；`Close()`/重连**不替换、不 Dispose** 该实例（只复位内部控制器），类级引用永不指向废弃实例。
- **形态**：用**属性**而非字段，避免类型初始化期取值，也少一处可写引用；⛔ 不得声明 `public`/`internal` 静态成员，禁止 UI 或 Manager 改写该引用。
- **边界（跨类不缓存）**：只有 `Workflow` 类可缓存。⛔ UI 页（`SystemControlPage`、`ProcessControlPage` 等）**不缓存** —— 每页各持一份只是把重复换个位置；UI 内按方法取用，≥4 次才起局部变量。
- **方法内兜底尺子**（不适用类级缓存时）：同一方法内取用 **≥4 次** → 顶部起 **1 个**局部变量；**≤3 次 → 直取**。
- **禁止形态**：同一方法内 **2 处及以上同名单例局部声明** → 合并为 1 处，不受次数限制。
- **调用链**：已缓存 `Manager` 的类，其私有方法直接读 `Manager`，⛔ 不再加 `MontionManager mgr` 形参；未缓存的场景才用参数传播。
- **开销事实**：首次构造后 `Instance` 只是一次字段读 + 空判断，**无锁**；直取 ≠ 性能问题，故次数是唯一判据。
- **判据**：`scripts/csharp_review.py` 的 `A.单例重复声明`（同一方法内同名单例局部声明 ≥2 → warn）。

---

## 二、注释精简（三规则 + XML 注释规范）

> **⚠️ 顶层裁定（2026-10-10 业主，本节最高优先级）**：
> 1. **约束归知识库，注释只写作用**：真实约束、历史教训、裁定日期、变更史**一律由 LLMWiki 承载**（写入 [[architecture/CodeMap]] 对应文件行或相关 `api/`/`lessons/` 页），**代码注释只表达「作用 + 应用范围」**。注释中出现日期 / 业主裁定 / ADR 编号 / 需求批次 / 「原为 X 现为 Y」即为违规。
> 2. **0 消费对象是预留的，精简时严禁删除**：任何成员（字段/属性/方法/事件/常量/枚举值）即使全库零调用也**不许删、不许合并**——它们可能是预留接口或横切关注点载体。发现 0 消费成员**只记入报告**，由业主裁决。此规则优先于 ⑤「死函数清理」。
> 2a. **2026-10-29 业主批准批次 A 例外**：经逐案分析并获业主确认，删除 **16** 个真死函数（13 名单 + 3 级联：`FindTreeNode` / `LoadXdocument` / `AddNodesRecursively`）；本条仍适用于其余 0 消费成员，后续删除仍须逐案裁决。执行记录见 [[project/CodeSimplification-Backlog-20261026]] B-5。
> 3. **XML 文档覆盖口径（2026-10-26 业主裁定）**：「public 必写 `///`」的**执行范围收窄为「新增或改动的 public 成员」**——存量 2,217 处 public 成员缺 `///` 属**历史欠账**，**不追溯、不设全库清零目标**，改为逐文件夹渐进偿还。理由：与第 1 条「注释只写作用」及本轮「精简」方向直接冲突，全量补齐将净增约 1,500 行且不产生行为价值。⛔ 原第一节①「public 必须写 `///`」的**无条件表述同步废止**（两处口径由本条统一）。

### ① 减少不必要的说明注释

- 注释**只解释代码「做什么 / 为什么这样做」**，不对版本、过程、由来做解释（这些内容由 LLMWiki 知识库记录，不在代码里复述）。
- 删除「2026-XX 修改」「原因为…」「参考某次需求」之类过程性注释；删除显而易见、与代码同义的注释（如 `// 赋值` `// 循环`）。

### ② 函数外用 `///` 注释（标准化，不限公私）

- 无论 `public`/`protected`/`private`，只要写 `///` 注释就**必须符合 XML 注释规范**（summary 一行 + param/returns 完整）。
- `public`/`protected` 方法/属性/类/接口的 `/// <summary>`：**新增或改动必写**（存量欠账不追溯，见顶层裁定第 3 条）；`private` 方法/属性：**允许且建议写**（用于总结作用与关键约束），**不强制，也不得据此删除既有 private `///`**；无论公私，**写了就要写对**（summary 一行 ≤20 字 + param/returns 完整）。
- `/// <summary>` 20 字内，动词开头描述"做什么"，不写过程/实现步骤/调用链（错误：`先校验参数然后调用 Repository 插入…`；正确：`创建订单`）。
- 类/结构体/枚举/接口 的 `/// <summary>` 必须一行完成，20 字内，不写多行。
- `<remarks>` 不是长篇容身之处（2026-09-04 裁定）：类头 remarks **至多 1~2 行**，只写「为什么」级个性约束（差异化职责 R0xx、数据/权责边界）；子类与基类的共性描述（线程归属、推进模型、对外态承载）只在基类写一次；枚举值清单、执行步段位清单、数据流向分步、裁定日期等过程/由来描述由 LLMWiki 承载，不进代码。⛔ 且每行 / 每句仍受 §二④ **≤20 汉字** 约束。
- 每个 `<param name="x">` 说明参数含义/取值范围/是否可 null/单位/枚举语义，**不重复参数名本身**（错误 `<param name="order">order</param>`）；有返回值写 `<returns>` 说明 true/false 各自含义，不写"返回结果"废话；仅当调用方应感知并处理的异常才写 `<exception>`。
- C# 7.3 注意：不用 `string?` 可空性标注、不用 `<inheritdoc/>` 偷懒；泛型尖括号转义 `List&lt;T&gt;`。
- **P/Invoke 豁免（2026-09-07 裁定）**：`[DllImport] public static extern` 声明**不要求** `///` 注释。依据：本仓既有 P/Invoke（`LineLaserCam/SmartRayCam/ApiCore/SensorHelper.cs`、`Program.cs`）均无 XML 注释，声明名与厂商 SDK API 同名同签、自解释，逐条补 `///` 只是噪声。**约束**：豁免仅限 L1 原生封装目录（如 `MotionControl/DeltaEtherCAT/Native/`）；该目录内如有非 `extern` 的公共成员（如错误码常量表、辅助方法）**仍须写** `///`。

### ③ 函数内用 `//` 注释

- **复杂逻辑**才加 `//`，解释内部变量意义、非显而易见的算法意图。
- **简单逻辑不写注释**（单步赋值、普通循环、常见判空）。

### ④ 单条注释记录 ≤20 汉字（2026-11-10 业主裁定 · C16）

- **尺子**：一条注释记录的正文 **≤20 汉字**，超出即二选一 —— **拆成多条短句**，或**迁进 LLMWiki**（`api/` / `modules/` 对应页），代码里只留一条 ≤20 字的结论或指路。
- **「一条记录」的界定**：一行独立 `//`（整行算一条）；或 `///` 里一个语义完整的句子（按 `。；！？` 切分）；或一个 XML 标签（`<summary>` / `<remarks>` / `<param>` / `<returns>` / `<exception>`）的内容。
- **统计口径**：只数汉字 `[\u4e00-\u9fff]`；标点、XML 标签、拉丁字母与数字**均不计**。实现见 `scripts/comment_scan.py long`，可逐条复核。
- **来源与缺口**：本节旧文只约束 `<summary>` ≤20 字，`<remarks>`（仅「至多 1~2 行」）与独立 `//` **无字数上限** —— 这正是连续两轮「按条文改了仍不达标」的原因。本条把 2026-10-10 顶层裁定第 1 条（「约束归知识库，注释只写作用」）落成可执行上限。
- **不可压缩内容**（多组实测采样值、协议码、斜坡 / 超时算术、步骤清单）**一律迁 wiki**，⛔ 不得为凑字数删除约束；`private ///` 一条不删（可压到 20 字内）。
- **判据**：`scripts/comment_scan.py long` 目标 **0 条超长**；`scripts/csharp_review.py` 的 `A.注释超20字`。

### ⑤ 跨行合并计数（2026-11-10 业主裁定 · C18）

- **尺子**：一个 `<summary>` 或 `<remarks>`（含被拆成多行的续行）按**整段内容合并**后计算汉字数，一个语义完整句子 **≤20 汉字**。
- **动机**：业主指出「remark 行很多都是转行导致没有检测到超长度」—— 跨行不得成为逃避长度检查的方式。
- **口径变更**：历史上按「每行算一条」的口径**作废**；`comment_scan.py long` 的 `merged_over` 为权威数，`legacy_line` 仅留对账。
- **判据**：`scripts/comment_scan.py long`（`merged_over`）· `scripts/csharp_review.py` 的 `A.注释超20字`。目标 **0 条**。

### ⑥ 变量 / 字段 `//` 只许一行（2026-11-10 业主裁定 · C19）

- **尺子**：一个变量 / 字段的 `//` 注释**只允许一行**；已写成多行的必须合并成一行且 **≤20 汉字**。
- **T1 撕裂**：一句话被劈成多行（声明行尾注释 + 下方续行）的同样要合并。
- **判据**：`scripts/comment_scan.py long`（`var_multiline`）· `scripts/csharp_review.py` 的 `A.变量注释多行`。目标 **0 条**。

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
  3. **模块整合/迁移后必须复跑**：`SafetyInterlock.cs`（已移除）因早期安全模块整合迁入 Workflow 时未纳入清理，残留 7 处 FailedItems 符号 → 迁移/合并文件后复跑本检查。

### ⑤ 日志出口统一：一个标签 + 直连出口（2026-09-03 确立，2026-09-04 修正：无中间封装）

> **背景（2026-09-04 修正）**：曾以新建 `DeviceLog` 中间类收敛（起因：63 处 `GlobalCommData.ShowLog`、四类标签写法并存），后用户裁定**新架构未要求该中间层**，`DeviceLog.cs` 已移除，改直连 + 统一标签。原发散情形：（私有 `_tag` / 遮蔽基类的 `const Tag` / `StateName` / `_simTag`），
> 且子类 `private const string Tag` 遮蔽基类 `public object Tag` 触发 **CS0108** 与 `string`/`object` 类型对撞。详见 [[lessons/StepDrivenWorkflowPitfalls]]（七.3）。

**强制规则**：

| # | 规则 | 说明 |
|---|---|---|
| 1 | **设备日志出口 = 直连 `GlobalCommData.ShowLog`** | `MainDeviceControl/` 下禁止再直接调 `GlobalCommData.ShowLog`；`MainDeviceControl/` 下不设中间封装层，调用点直接 `GlobalCommData.ShowLog(tag, ...)` |
| 2 | **每个流程/管控类有且只有一个日志标签** | 子工作流用基类属性 `Tag`（构造函数首行赋值，禁止子类再声明同名成员）；独立管控类用私有 `_tag`；状态基座用 `StateName` |
| 3 | **本类内走 `Log(...)` 辅助方法，不重复传标签** | 基类提供 `protected void Log(string message, MessageLevel level = MessageLevel.Info)`；独立管控类各自定义私有 `Log(...)` 直连 `GlobalCommData.ShowLog(_tag, ...)` |
| 4 | **设备日志与通讯日志不得混用**（2026-11-17 ADR-106 修订归属） | 按**行为/结果**二分：**行为**（过程陈述：配置装载、线程启停、监听绑定、指令收发、收发报文）→ 通讯日志，需 FilebackupPage 查看的走 `ShowCommLogForView`（写 TcpMessageLog + 页面打开才显示），纯报文走 `ShowCommunicationLog`（见 ③）；**结果**（成败反馈）→ 主系统日志，但**自动重连轮询自愈循环的结果例外**（含重连成功、启动失败，降 `MessageLevel.Debug` 只记录不显示——每拍 5s 冷却反复触发）。⛔ `CommunicationCommandReceived` 是**指令事件**（4 订阅者含 2 Workflow），禁用于日志显示 |
| 5 | **跨线程共享的 `long`/`double`/`decimal` 字段禁止裸读写** | 时间戳、计数器、累计量一律 `Interlocked.Exchange` / `Interlocked.Read`；32 位平台上 64 位读写非原子 |

**自检命令**：

```bash
# ① 出口回归：MainDeviceControl/ 不应再有 DeviceLog / 中间封装（2026-09-04 移除）
grep -rn "DeviceLog" AdaWeldSystem/MainDeviceControl/   # 期望仅剩 C7 契约 SubDeviceLog

# ② 标签收敛：Tag 只应在基类声明 1 次 + 各子工作流构造函数赋值 1 次
grep -rn "string Tag\|Tag = \"" AdaWeldSystem/MainDeviceControl/
```

**判据补充（审计 0 消费成员时）**：`Tag` 曾因「全库 0 消费者」被误判为死成员。
**0 消费 ≠ 死成员**——若它是横切关注点的载体（日志标签 / 序列化键 / 权限标识），或 `raw/` 原档将其列为契约成员，
应先确认其设计意图再下结论。用户裁定：可观测性 API（`StepStatusText` / `WorkElapsedMs`）与安全钩子（`CheckDeviceIOSafe`）同样**不因 0 消费而删除**。

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
| A. 文件书写整理 | ① | 成员顺序、#region 划分与配对（**语义 region 合法，不强制类型 region**）、XML 注释（**新增/改动 public 必写**，存量欠账不追溯/summary≤20字/param/returns）|
| B. 代码逻辑精简 | ② ③ ④ | 无意义 null 检查、无意义锁、冗余赋值传递、过度枚举、过度属性、过度等待/延迟、过度缓存、过度资源管理、临时变量滥用 |
| C. 函数精简 | ⑤ | 功能重叠（token 相似度≥50% 或超集关系）、嵌套内联候选（private 仅 1 调用且 ≤3 行）、疑似死函数 |

**严重级别**：`error`（确定 bug/严重违规，如 `lock(new object())`，必须改）/ `warn`（高概率冗余，逐条确认）/ `info`（风格建议，按需处理）。有 error/warn 时脚本退出码非零。

**成员顺序判定口径（2026-08-31 明确，2026-10-26 修订判定范围）**：脚本按 `fields/properties` 私有=1、公共=2，`#ctor`=3，`private` 方法=4、`public`/`protected` 方法=5 排序。**判定范围 = 每个 `#region` 段内；跨 region 不比较**（语义 region 优先；无 region 的类仍按整类判定）。旧口径的「类内全局顺序」会把 42 个功能分区文件误报为违规，已废止。
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

### 4.1 口径-判据映射表（2026-10-26 建立 · **改标准必须同步改判据**）

> **目的**：杜绝「标准改了 → 判据没改 → 扫描器按旧口径报 → 噪声被忽略 → 再改回去」的循环。
> **每条硬要求都必须有对应判据项；改标准 = 同时改判据 + 跑 `scripts/simplify_selfcheck.py` 自检。**

| # | 标准条款 | 硬要求 | 对应判据（`scripts/csharp_review.py`） | 级 | 备注 |
|---|---|---|---|---|---|
| 1 | §一① 成员顺序（**region 内**） | 每个 `#region` 段内：私有变量→公共变量→构造函数→私有函数→公共函数；**跨 region 不比较** | `A.文件整理 / 成员顺序错误` | warn | 嵌套类型**不参与**判定（§一① 允许置后） |
| 2 | §一① region | `#region`/`#endregion` 必须配对；类型/语义命名并存；名禁过程性命名 | `#region 数量不匹配`（error）· `region 名含过程性命名`（warn） | error/warn | 类型 region **非强制**（248 处误报已废止） |
| 3 | §一① + §二② XML 注释 | public 新增/改动必写；**private 允许且建议写**；写了就要写对 | `公共方法未写 ///`（**info**，M1 存量不追溯）· `A.注释超20字`（**C16/C18 合并口径唯一判据**，warn）· `参数缺 <param>`（warn）· `返回值缺 <returns>`（warn） | info/warn | ⛔ **不得删除既有 private `///`**（无对应判据 ⇒ 属禁止动作）；⛔ 一个条款只许一个长度判据，按「整段 summary 汉字数」的旧口径已废止（会与权威分句口径冲突并产生假 warn） |
| 4 | §三 日志 | 去分隔符号；周期轮询 `Thread.Sleep` 属有意例外 | `B.过度等待/延迟`（循环体内 Sleep → info） | warn/info | `.Result` 判据**须带类型限定**（只认 `Task`/`ValueTask`） |
| 5 | §⑤ 功能重叠 | 70% 以上方法体相同；同名不同参是重载（不报）；薄包装不算重复 | `C.功能重叠`（阈值 0.7 + 排除薄包装） | warn | 语义不同者逐案判定「有意保留」 |
| 6 | §二 顶层裁定 2 / 2a | 0 消费成员**只报不删**；2026-10-29 批次 A 16 个经业主批准例外删除 | `C.疑似死函数`（**info**） | info | 其余删不删仍由业主裁决 |
| 7 | ADR-002 / ADR-001 | 禁 `Dispose(bool)` 覆写；禁 C# 8+ 语法 | 独立静态审计（`scripts/simplify_guard.py` 附带项） | error | |
| 8 | ADR-005 | namespace = 目录（§3 例外表豁免） | 独立静态审计 | warn | **例外登记表优先于规则正文** |
| 9 | §二 ③ 锁 | 禁止嵌套锁无顺序、锁字符串、锁局部对象；锁对象必须 `readonly` | `B.多层锁`（嵌套/顺序反转/字符串/局部对象）· `B.无意义锁`（readonly/锁内 IO） | warn/info | 线程语义需人工确认；锁内 IO 为有意串行化时豁免 |
| 10 | §二④ 语法简化八则 | 对象初始化器 / 内联变量声明 / 空值传播 / 模式匹配 / 不必要赋值 / 显式转换 / 条件委托调用 / 空值检查简化 | `simplify_run.py` 第 5 关：`dotnet format style --verify-no-changes --diagnostics IDE0017/0018/0019/0031/0059/0220/1005/0270 --severity info` | info | 判据即官方 Roslyn 修复器，**0 诊断 = 通过**；禁手写正则批改 |
| 11 | §一之二⑥ 同类指令单一入口 | 同设备族 ≥3 个同前缀、无参、同返回类型的公开方法应合并为单入口 + 枚举 switch；全族形态一致（阻塞/异步不混用）；自动流程只调「自动」指令并等完成信号 | `C.平行指令入口`（≥3 个同前缀无参公开方法） | info | 初始化自检的零位动作不属自动焊接流程，不受「只调自动指令」限制 |
| 12 | §二 注释三分计数（2026-11-09） | 总行 = 空行 + 代码行 + 注释行**互斥**；注释行 = `///` + 独立 `//` + 块注释；行尾注释不单独计行，只记 `code_trailing` | `scripts/comment_scan.py stats` | — | 历史「82,588 行」含 175 行文件尾幻影空行，权威口径为 **82,413**；历史「注释 16,264」把 216 行行尾注释重复计入，权威为 **16,048** |
| 13 | §二 撕裂四类（2026-11-09） | T4 缩进为 0（只改前导空白）/ T2 标签配对错 / T3 文档块与声明间空行 / T1 同块多 summary（句子劈半、文档错位） | `scripts/comment_scan.py trunc` | — | 四类**互斥**，`union` 为对账数；T4 修复须"去前导空白后逐字节比对"自证 |
| 14 | §二 复述三档（2026-11-09） | strict（注释=标识符中文义/通用动词）⊂ wide（注释含下一行 ≥4 字符标识符且无约束词）⊂ ultra（≥3 字符标识符子串） | `scripts/comment_scan.py restate --tier strict/wide/ultra` | — | 仅扫独立 `//` 行（`///` 属文档注释，另按 A.注释规范判定）；历史 609/983 不可复算，本轮权威 **190** |
| 15 | §二 占位式 XML（2026-11-09） | `<returns>返回值。</returns>` / `<param name="x">x 参数。</param>`（含大小写差异）一律删除；空块整块移除；`<summary>构造函数</summary>` 保留 | `A.占位式XML`（`csharp_review.py`）· `comment_scan.py xml` | info | 删除后「缺 param/returns」由 warn 降 info（裁定 #3 存量欠账不追溯），**不构成新增 warning** |
| 16 | **设备初始化必须按依赖层级**（2026-11-09） | 初始化节点表声明 `ParentKey`；父级结果 ≠ Success 时子级**记跳过且不发起连接**；三态 `Success/Failed/Skipped` 不许混用，Skipped 必须写 `BlockedBy` 且不计入失败；⛔ 不用固定等待；⛔ 不新增 `SubDeviceState.Skipped`（与运行态正交） | `C.设备初始化分层`（`csharp_review.py`） | warn | 详见 [[standards/DeviceInitializationDependency]]；重试须复位节点索引与上轮结果，整棵子树重走 |
| 17 | **刷新入口受硬件状态门禁**（2026-11-09） | 自动刷新默认关闭（Designer `Checked = false`）；按设备粒度判就绪，未就绪 `Enabled = false`；就绪只解冻不自动开启；定时刷新后台采集 + `BeginInvoke` 应用，不卡 UI | `B.刷新默认开`（`csharp_review.py`） | warn | 判据与门禁时机见 [[standards/DeviceInitializationDependency]] §四 |
| 18 | **§二④ 单条注释记录 ≤20 汉字（C16，2026-11-10）** | 一条记录 = 一行独立 `//` / `///` 内一个完整句 / 一个 XML 标签内容；只数汉字，标点与标签不计；超出即拆句或迁 wiki | `A.注释超20字`（`csharp_review.py`）· `scripts/comment_scan.py long` | warn | 目标 **0 条**；迁移落点见 `wiki/modules/CommentConstraintRegistry.md` |
| 19 | **§一之二⑦ 单例取用：类级缓存优先（C17，2026-11-10）** | `Workflow` 类声明类级私有属性 `Manager`，方法内清掉局部声明；UI 不缓存；未缓存场景同方法取用 ≥4 次才起局部；同名单例局部声明 ≥2 处 → 合并 | `A.单例重复声明`（`csharp_review.py`） | warn | 目标 **0 条**；`Instance` 为 Lazy，`Close()` 不替换实例 |
| 20 | **§二⑤ 跨行合并计数（C18，2026-11-10）** | 一个 `<summary>` / `<remarks>` 含续行按整段合并后，一个语义完整句 ≤20 汉字；逐行口径作废 | `A.注释超20字`（按合并后计）· `scripts/comment_scan.py long` 的 `merged_over` | warn | 目标 **0 条**；`legacy_line` 仅留对账 |
| 21 | **§二⑥ 变量 `//` 只许一行（C19，2026-11-10）** | 一个变量 / 字段的 `//` 注释只允许一行且 ≤20 汉字；跨行撕裂必须合并 | `A.变量注释多行`（`csharp_review.py`）· `scripts/comment_scan.py long` 的 `var_multiline` | warn | 目标 **0 条** |

| 22 | §一④-6 过度属性 | 只报访问器真的含重操作（循环 / `try` / IO / 日志 / 有效行 > 5）；`lock` 快照读取与 `new` 返回集合副本是项目范式，⛔ 不判违规 | `B.过度属性`（`csharp_review.py`，重操作正则 + 有效行门限） | info | ⛔ 旧口径 `len(body_text) > 20` 已废止（连 `get { return _x; }` 都误报）；「public set 能否改只读」需跨文件消费分析，不属单文件判据 |
| 23 | §二② 存量 XML 欠账输出 | 顶层裁定 3 的存量欠账 info 默认不进清单，`--verbose` 可查全量，按文件夹渐进偿还 | `A.注释规范` info（`csharp_review.py` 的 `INCLUDE_LEGACY` 开关） | info | ⛔ 不设全库清零目标；补齐全量 `///` 与「注释精简」方向冲突 |
| 24 | §一⑤ 嵌套内联豁免 | 台账 B-6 / B-8 已裁定保留的语义类别（Log 包装 / 指令分发 / 解析校验 / 卫语句 / 流程步骤 / 初始化与几何 / 事件抛出）不再重复上报 | `C.嵌套内联`（`csharp_review.py` 的 `inline_keep_prefixes`） | info | 短方法表达独立概念；内联会把守卫与语义散到调用方 |

**固定执行入口**（见 [[standards/CodeSimplification-Tooling]]）：
`simplify_guard.py`（结构守卫，改码前后必跑）→ `simplify_apply_member_order.py`（成员顺序重排）→ `simplify_apply_docs.py`（注释补全/压缩）→ `simplify_selfcheck.py`（判据-标准一致性 + 四重自证）。
**⛔ 禁止自写一次性批改脚本**（11 条已踩过的坑见 Tooling 页「禁区清单」）。

---

## 五、与其他规范的边界

| 已有约束 | 关系 |
|---|---|
| [[decisions/ADR-001-CS73-Constraint]] | 精简后仍须 C# 7.3 语法，禁用 switch 表达式 / 可空引用 / init / record 等 |
| [[decisions/ADR-003-EnumDeduplication]] | 本规范 ③ 枚举去重的具体执行依据 |
| ADR-002（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） / [[decisions/ADR-002-DisposePatternFullCoverage]] | 精简**不得**新增或重写 `Dispose(bool)`；非 UI 类保持标准 `IDisposable.Dispose()`（与 ④-9 禁止过度资源管理一致）|
| AGENTS.md Region 完整性 | `#region`/`#endregion` 必须配对，精简不得遗留孤立 `#endregion`（见 ①）|
| 公共接口契约 | 精简**不得**改变公共类型/方法签名与枚举成员名（除非走 ③ 合并流程并全量改名）；检查脚本亦不自动改 public 成员 |
| .csproj 注册 | 若因精简新建 .cs 文件，必须注册到 `AdaWeldSystem.csproj` |
| [[standards/UiStateSimplification]] | UI 层状态判断与控制**细则**（本地 bool 缓存设备态/单一控制函数/统一刷新入口/集中状态标签）由该页专管；`UIDesign/` 非设计器 `.cs` 的 ①②⑤ 维度（成员排序/变量/辅助函数）与 ③④（枚举事件/逻辑）仍由本页覆盖 |

---

## 六、执行清单（按文件夹）

对每个业务源码文件夹执行（含 `UIDesign/` 下非设计器 `.cs`；逐文件可辅以 `scripts/csharp_review.py`）：

- [ ] ① **每个 `#region` 段内**按 私有变量→公共变量→构造函数→私有函数→公共函数 排序（跨 region 不比较）；#region 与 #endregion **配对**（语义/类型两种命名并存，见第一节①）
- [ ] ② 提升反复新建的临时变量为私有字段；消除无意义临时变量与 null 检查
- [ ] ③ 枚举/事件去重合并（Grep 全量追溯）；移除过度枚举
- [ ] ④ 删除调用处与函数体重复的判定/锁/互锁，减少嵌套；消除 9 类冗余（锁/赋值传递/属性/等待/缓存/资源管理）
- [ ] ⑤ 归集重复辅助函数到就近 Helper；合并功能重叠函数；内联单层嵌套 private 方法；删除死函数
- [ ] 注释按第二节精简（`///` 标准化：无论公私，写了就要 summary 一行 + param/returns 完整；**新增/改动的 public/protected 必写，private 不写**；复杂逻辑才 `//`；类级 summary 一行 20 字）
- [ ] 日志按第三节改写（去符号、控时机、通讯全记录）
- [ ] 自审：无 ADR/Lessons 违反、无公共签名变更、region 配对、Dispose 未动
- [ ] 复跑 `scripts/csharp_review.py` 至 warn/error 清零（designer.cs 跳过）

### 已覆盖模块（历史轮次，粗版阶段）

> 下表为历史记录，模块名按当时口径保留。**`DeviceStateMachine` / `Workflow` / `SafetyInterlock` 三处现均已不存在**（`DeviceStateMachine/` 与 `Workflow/` 目录于 2026-08-28 删除，`SafetyInterlock.cs`（已移除）于 2026-08-31 三合一合并、2026-09-02 更名 `DeviceStatusWork.cs`）。

| 轮次 | 日期 | 覆盖模块 | 重点 |
|------|------|---------|------|
| 第一轮 | 2026-08-21 | Comm / LineLaserCam / FileOperate / DeviceStateMachine | 日志归集 + 去符号 + 注释精简 |
| 第二轮 | 2026-08-21 | Workflow（Safety/PCL） / PCLOperate / SafetyInterlock | 状态机日志去符号 + FailedItems 去符号 + 注释精简 |
| 第三轮 | 2026-08-21 | EmguALG / MotionControl / WeldParamControl / SQLiteDatabase / Workflow残留 / IntelligentLaserCam补漏 | 异常消息去符号 + 剩余模块注释精简 + 符号漏网补漏 |

> 未覆盖（不在精简范围）：`*.Designer.cs`（设计器自动生成）、厂商 SDK 原生代码（SmartRay ApiCore 等）、`3rdDepend/`

---

## 附：参考文件索引（详尽反例与脚本工作流）

- [[standards/CodeSimplification-ReviewWorkflow]] —— 检查脚本工作流（4 步：扫描→逐类审查→报告→确认后修复）
- [[standards/CodeSimplification-RefFileOrganization]] —— 文件书写整理规则全文（成员顺序/region/XML 注释 + AI 高频反例）
- [[standards/CodeSimplification-RefLogicSimplification]] —— 逻辑精简 9 类禁止项全文（判定标准 + AI 高频反例 + 修正方向）
- [[standards/CodeSimplification-RefFunctionSimplification]] —— 函数精简规则全文（功能重叠/嵌套内联/死函数 + 判定流程 + 例外）
- `scripts/csharp_review.py` —— 单文件静态扫描器（A/B/C 三类，error/warn/info 三级）
- `scripts/scan_by_folder.sh` —— 按顶层文件夹批量扫描器（进度可见 + 单文件超时 + 增量落盘 `scan_by_folder.tsv`，推荐全盘巡检用）
