---
title: StaticVerifier-Checker-FailureModes
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


## 四、静态校验器自身的失效模式

这一组不是「代码有 bug」，而是**校验器给出的绿灯是假的**。

### 4.1 「禁止某种写法」的文本判据必须先剥注释

正则 `Log\([^)]*"[⚠]` 会命中 `/// <summary>…⚠️…</summary>` 里的说明文字，报出并不存在的违规。**任何 banned-pattern 检查都先 `re.sub(r'///[^\n]*','',t)` 与 `//`。**

⚠️ 通用陷阱：**描述规则的注释本身会命中规则。**

### 4.2 批量脚本的 `assert` 会丢弃此前所有替换

Python 改文件的典型写法把 `open(p,'wb')` 放在最后 ⇒ 第 3 步 `assert` 失败会**连第 1、2 步的成功替换一起丢掉**。症状看起来毫不相干：「我明明加了 `using`，却报 CS0246」。

**做法**：先跑一遍 dry-run 断言**全部**锚点命中，再统一 replace + 一次 write；或用 Edit 工具逐处改。
⚠️ **按字节回写要显式补回 BOM**（`decode('utf-8-sig')` 会吃掉 BOM；本仓库部分文件带 BOM，掉了会产生整文件 diff）。

### 4.3 跨文件判据必须先探该文件行尾

判据写死 `'\n'` 而目标是 CRLF 文件 ⇒ 正则不匹配 ⇒ 假失败。实证：`KukaRsiComm.cs` 是 CRLF，用 `...sensorType,\n   double cutWireSignal = 0.0)` 匹配失败，改 `\s*\r?\n?\s*` 才通过。（同 原 rules/KR-013（已并入 lessons/WikiDriftCorrectionPitfalls） 的行尾家族问题。）

### 4.4 判据的正则本身要过护栏

关键词扫描漏了「左侧不是关键字」护栏 ⇒ 135 处假阳性。**写正则判据的判据**：先拿一份已知正常的大文件试跑，若报出成百上千条，先怀疑判据而不是代码。

### 4.5 绿灯不是证明 —— 打印一次中间值（空过防护）

96/96 全绿之后把抽取到的中间值打印出来（`BIND` / 表 `KEYS` / 每行类 `PROPS`），才发现「8/19/9 列 vs 10/20/10 属性」而差集为空 —— 匹配是**空转**的。

> ⛔ **放宽正则让判据通过，会把判据变成同义反复。** 永远重读底层值，别只信计数。

**⭐ 空过的新形态：CRLF 文件上 `;$` 会失配，让整组判据静默变空（2026-10-26 实测）**

```python
# ❌ 在 CRLF 文件上 0 命中 —— `$` 落在 `\r\n` 的 `\n` 之前，但该处字符是 `\r`
decls = re.findall(r'^        private (?:AntdUI|System\.Windows\.Forms)\.(\w+) (\w+);$', dz, re.M)
# ✅ 先在 LF 视图上跑正则，或把 `$` 换成 `;` 后自行截断
dz = dz_b.decode('utf-8').replace('\r\n', '\n')
```

- **危害链**：`decls == []` ⇒ 下游「235 个控件声明 ↔ 实例化 ↔ 挂载」判据**逐条空过**（`not missing_new` 对空列表恒真）⇒ **显示全绿且看不出任何异常**；同时「`.cs` 控件标识符 ⊆ 声明集」因声明集为空而把**全部**控件报成差集，噪声反而暴露了它。
- **判据**：凡「抽取一个集合 → 断言集合内每一项性质」的判据，**必须同时断言集合基数**（本轮加 `chk('3.0 声明集非空', len(decl_names) > 60)`）。集合相等类断言（`set_difference == []`）对空集恒真，是本形态的温床。
- **同族**：§4.3 写的 `\n` 判据在 CRLF 目标上假**失败**（会吵闹），本条是它在**反向**上的表现 —— 假**通过**（更危险）。

### 4.6 校验器能力三分类

| 类别 | 例子 | 谁来判 |
|---|---|---|
| **模式化** | 命名空间、csproj 路径、禁用语法、配置四点闭环、region 配对、结构不变量、签名-调用点实参数、关键字声明位、跨类裸调 static | ✅ 静态校验可负责 |
| **语义化** | 类型系统合法性、重载解析、装箱、泛型推断、接口实现完整性、async 状态机 | ⛔ 只有编译器能定 |
| **接线完整性** | 参数加了没传值、方法加了没消费者、配置能读能写但无消费者 | ⚠️ 需专项判据（见第三节） |
| **第三方 API 签名** | AntdUI 控件属性/事件/方法是否存在及其类型 | ✅ **有官方文档时静态可判**（见 4.8） |

> **绿灯既不代表构建过，也不代表功能通。**

**预防规则**：编译报的错若本可被已知判据拦住，**必须同轮把判据加进校验器** —— 只写 lessons 页不够，判据要活在检查里。

### 4.8 第三方 API 的核实能力分层（2026-10-09，AntdUI 接入官方 wiki 后）

**背景**：此前因「本机无编译器 + DLL 已混淆 + 反射被拦」，把 AntdUI 控件签名一律判为「语义判据 → 核实不了就别用」，导致大量**近似替代**（自算坐标、复用重填函数）与**错误免责**（「`Radio` 事件名不可确定，别赌」）。2026-10-09 起 `raw/AntdUI/wiki-zh/`（官方 wiki 全量镜像 85篇）落地，**这条 blanket 判定失效**。

**核实能力按六类分层**：

| # | 信息类别 | 官方文档能否判定 | 举例 |
|---|---|---|---|
| 1 | 属性是否存在 + 类型 + 默认值 | ✅ 能 | `Table.EmptyHeader` 是 `bool`；`Slider.MinValue` 是 `int` |
| 2 | 事件**名**是否存在 | ✅ 能 | `Radio.CheckedChanged`（此前误判为「不可确定」） |
| 3 | 方法名/ 重载 / 参数个数与类型 | ✅ 能 | `Table.Refresh<T>(AntList<T>)`；`ColumnCheck.Call(Func<bool,object?,int,int,bool>)` |
| 4 | 枚举成员 | ✅ 能 | `ColumnsMode.Fill` / `TEditMode.None` / `TTypeMini.Primary` |
| 5 | **某个API 不存在**（反向判据） | ✅ 能 | `Table` 无 `CheckAll` / `RefreshRows` / `GetCoordinate` / `ReadOnly` |
| 6 | **事件的 .NET委托类型名**（如`BoolEventHandler` vs `EventHandler<bool>`） | ⛔ **不能** —— 文档只给语义参数（`bool value`），不给委托类型 | `Checkbox.CheckedChanged` 在本项目已实证为 `(object, AntdUI.BoolEventArgs)`；`Radio` 同名事件**仍须 VS 编译确认**，**不得仅凭文档断言** |

**⭐ 由此得出两条通用纪律**：

1. **「核实不了」是阶段性结论，不是永久结论。** 写「本库/本机核实不了，先用近似」时，必须同时写明**核实路径为什么不通**（无编译器？DLL 混淆？官方无文档？）。**一旦该路径被补上（装了编译器 / 拿到官方文档），近似写法必须回头改回真接口。**
2. **「近似」有两种，处置相反**：
   - **因官方确实没有该API 而自算** ⇒ ✅ **是正解，不是妥协**，应正名为设计决策（例：`AntdUI.Slider` 只有 `int` 的 `Value/MinValue/MaxValue`，本就没有坐标换算API）；
   - **因核实不了而近似** ⇒ ⚠️ 是**技术债**，官方源到位后必须替换（例：批量勾选改用 `Refresh()` + `CheckedOverallChanged`，而非复用重填函数）。

**判据（可脚本化）**：当 `raw/<vendor>/` 下存在该库的官方文档镜像时，加一条**反向存在性检查**——断言「代码注释/文档中声称『不可确定 / 不存在 / 需近似』的每个 API 名」，在镜像里grep 一次；命中即说明**该免责已失效**，须就地纠正。**这条判据专门抓「基于猜测写下的免责条款」，它们最隐蔽也最耐久。**

### 4.7 生成式改码的「落点」判据：脚本插入必须锚定在类型体内（2026-10-08 真实事故）

**症状**：`SystemControlPage.Designer.cs` 编译一片红（CS1022 / CS0116 / CS1519），报错行全在文件**尾部**，提示「应输入类型、委托、枚举、接口或成员」。

**根因**：上一轮的迁移脚本把生成的 **238 行**块**追加到了文件末尾**，而该文件末尾早已是「`    }` 类闭合 + `}` 命名空间闭合」⇒ 生成代码**整体落在类型之外**。于是 `this.panelLaserCalibHost.Back = …` 这类语句出现在 namespace 之外。

> ⛔ **在 `.Designer.cs` / 任何 `partial class` 文件里，「文件末尾」不是一个合法插入点。** 生成式改码必须先把内容按语义锚点（new 区 / SuspendLayout 组 / 属性块区 / ResumeLayout 组 / 声明区）**分发到类体内**。

**判据 A —— 文件结构层（低成本，必须进校验器）**：

```
① 骨架定位：namespace / partial class / #region / #endregion / InitializeComponent 行号
   满足 ns < class < #endregion < classClose < nsClose，且各类关键字恰 1 个
② 类型闭合之后不得出现任何 this.xxx 语句        ← 本次应命中 238 行
③ 全文件花括号计数配平（{ == }）
```

**判据 B —— 孤立段头**：形如 `// name` 的段头若其后**没有任何 `this.name.` 属性行**，说明该控件的属性块被删/被搬而注释留在原处（本次命中 `lblGeoSecTitle`、`tabPageWireAlign`）。

> ⚠️ **该探针有一个已知误报源**：`TableLayoutPanel` 子控件的段首第一行是 `this.<容器>.SetColumnSpan(this.name, n);`（以容器开头而非 `this.name.`）⇒ 会把合法段误判成「0 属性」。探针必须把 **`(this.name,` 形式**（`Controls.Add(this.name, …)` / `SetColumnSpan(this.name, …)`）也算作该控件的行。
>
> ⚠️ **2026-10-26 补两处盲区（同一探针，实测一次报出 235 条假阳性 + 1 条；本论据出自 [[decisions/ADR-075-LaserHeadUiControlConsistency]] 的 Step 2.6）**：
> ① **段头扫描的「停止条件」不能是空注释行** —— VS 段头是 `// ` + `// <name>` + `// ` 三行，若把「遇到下一个 `// `」当停止条件，会在**段头自身第三行**就 break，于是**每一个段头都被判成孤儿**（本轮一次性报出全部 235 个控件）。停止条件必须是**下一个具名段头**（`^            // \w+$`）。
> ② **UserControl/Form 自身的段头命名 = 类名**，其属性写作 `this.AutoScaleMode` / `this.Name = "SystemControlPage"`，**永远不会出现 `this.SystemControlPage.`** ⇒ 必须显式排除「段名 == 所在类名」；
> ③ 既有**真孤儿**控件（声明 + 实例化但从未 `Controls.Add`）应登记为白名单并在交付中报告，而不是让探针长期报红 —— 否则下一次真孤儿会被淹没。

**⚠️ 这一轮为什么旧判据全绿**：旧判据只查「声明 ↔ 实例化 ↔ 属性引用」三向闭合 —— 而**这三向在类型外也照样自洽**。同一轮还连带丢了 `panelLaserCalibHost = new AntdUI.Panel();`（运行时 NRE）、把 `Name` 串写成 `"panel2"`、留下 2 处指向**源页**容器的 `tbpanelweldponts.SetColumnSpan(…)`（CS0103）。

> ⛔ **判据必须同时覆盖「符号层」与「文件层」：符号层自洽 ≠ 文件结构合法。**

---

## 四之九、两条委托/静态上下文陷阱（2026-10-09 S-11 编译打回）

业主 VS 真实编译报出 2 个错，**都在同一轮新增的事件机制里**：

```
1、OnOperateLevelChanged 没有与委托 Action<EventHandler<OperateLevel>> 匹配的重载
2、关键字 "this" 在静态属性、静态方法或静态字段初始值设定项中无效
```

### ⛔ 判据 A：`Action<TDelegate>` 不是「参数转发器」——它只接**一个**形参

我写的是：

```csharp
// ⛔ 错：Action<T> 是【单参无返回值】委托，这里却被当成 BeginInvoke 的参数打包器
this.BeginInvoke(new Action<EventHandler<OperateLevel>>(OnOperateLevelChanged), sender, level);
```

`OnOperateLevelChanged(object sender, OperateLevel level)` 是**两参**方法，`Action<T>` 只有一个 `T` 形参 ⇒ 无匹配重载。

**正解（本项目既有范式，`FormMain.cs:236` 早就在用）**：用 **lambda 闭包**捕获外部实参，`Action` 保持无参：

```csharp
this.BeginInvoke(new Action(() => OnOperateLevelChanged(sender, level)));
```

| 写法 | 适用 |
|---|---|
| `new Action(() => OnXxx(a, b))` | **默认选它** —— 捕获任意实参 |
| `new Action(RefreshUi)` | 目标方法**无参** |
| `new Action<string>(AppendLog)` | 目标方法**恰好 1 参**且类型须严格匹配 |
| `new Action<EventHandler<X>>(Handler)` | ⛔ 只有目标方法本身就是「单参、参数恰好是 `EventHandler<X>`」时才成立 |

**判据**（可全库跑）：
```
对每个 new Action<GEN>(Method)：
  GEN 无逗号 => Method 必须 0 参
  GEN 含逗号 => Method 必须 1 参
```
⚠️ **本项目有 4 处 `new Action<T>(Method)` 目标法带 1~2 参却是合法的** —— 因为它们的泛型实参写对了（`new Action<string>(AppendLog)` 对 `AppendLog(string)`）。**判据必须按「泛型参数个数 vs 目标方法形参个数」比对，不能只查「目标法是否有参」**。

### ⛔ 判据 B：static 上下文里 `this` 无效（CS0027）

```csharp
public static void SetOperateLevel(OperateLevel level)   // ⛔ static
{
    EventHandler<OperateLevel> handler = OperateLevelChanged;
    if (handler != null) handler(this, level);            // ⛔ 静态上下文无实例 this
}
```

**正解**：`handler(null, level)` —— 本项目 `SystemComm.cs:172` 早就是这个写法（`handler(null, message)`），**同文件既有范式就在隔壁**。

> ⛔ **判据：逐方法做花括号配平，标出 `static` 方法体，断言其内（剥掉 `//` 与 `///` 后）0 次出现裸 `this`。**
> ⚠️ 阴性对照是这条判据的生命线：修好后必须**从上一份 output 包解出修复前的文件跑同一判据**，
> 确认它**报得出那 1 处**，才能证明「0 处」是真清除而不是判据空过。

### 判据自身的三次坑（本轮）

| 坑 | 现象 | 正解 |
|---|---|---|
| **正则太宽** | `\w*[Hh]andler\(\s*this\b` 报 113 处 —— 把 `this.Controls.Add`、`EventHandler(this.XxxHandler)` 全匹配了 | 必须**先按花括号配平切出 static 方法体**，只在其中搜 |
| **误判框架语义** | 我断言「`enum` 不继承 `EventArgs` ⇒ `EventHandler<OperateLevel>` 违反 CS0453」 | ⛔ **错**：.NET 4.8 的 `EventHandler<T>` **没有** `where T : EventArgs` 约束；本项目 `EventHandler<int>`/`EventHandler<string>` 长期在用且能编译。**先查项目既有同类用法，再决定是否合法** |
| **计数写成下限** | 「转发调用 `>= 2`」实际应为「恰好 1」 | 一个 handler 只需一处转发；语义判据要写「恰好 N」不是「>= N」 |

## 四之八、只读标志型门控：标志写对了，门控却是空的（2026-10-08 S-11）

**现象**：`OperateLevelControl()` 里有完整的 `switch` 分三档，但**降权档是空分支**：

```csharp
case OperateLevel.Admin:
case OperateLevel.Engineer:
    ShowTreeNode();      // 恢复可见
    break;
case OperateLevel.Operator:
    break;               // ⛔ 什么都没做
```

配套的 `HidePage` 布尔**全库只被读、从不被置 `true`** ⇒ 隐藏路径永远进不去。

> ⛔ **判据：对「显隐门控」类需求，只查「等级分支存在」会被骗过 —— 必须查每一档是否有实际动作，
> 并查隐藏状态标志是否存在被置位的赋值点。**

**通用判据（对四类门控逐项成立）**：

| 门控形态 | 「看起来对」的假象 | 必须验的赋值点 |
|---|---|---|
| 控件可见性 | 置了 `Visible=false`，但值由**事件驱动**计算，事件**从未被触发** | 触发源是否存在订阅方 |
| 导航项显隐 | 写了 `Remove()`，但被 `if (已隐藏) return;` 守卫短路，而该标志从未被置位 | 标志的**置位赋值点**是否存在 |
| 权限等级 | 枚举加了新档并 `switch`，但新档是 `break` 空分支 | **每档至少一个非空动作**（`break` 视为可疑） |
| 写入守卫 | 写了 `EnsureXxx()` 校验方法，但**零调用方** | 判据要求「调用方 ≥ 1」，否则是死代码 |

**配套的第二类缺陷：改值不发通知**

原实现里 `mOperateLevel = OperateLevel.Operator;` 是**裸赋值**，任何页面都无法感知降权 —— 显示层、导航层各自都不会刷新。

> ⛔ **判据：全局可变状态若被多处读取，必须提供唯一写入口 + 变更事件**；扫描时断言「**除状态类内部外，0 处直接赋值**」。
> 静态事件订阅还须配对退订（控件 `DisposeComponents` / `FormClosed`），否则泄漏。

**第三类：新增状态标签漏了 Designer 四件套**

手工往 `ToolStrip` 插入标签时，须齐备：`new` 实例化 · `Items.AddRange` 挂载 · `Name` 与字段名一致 · 字段声明。缺一项即 CS0103 或运行时空引用。判据：**四项各恰好 1 处**。

## 四之十、批量删代码段的三类结构损伤（2026-10-09 ADR-055 实证）

删「枚举 + 方法 + 字段」这类**成组的代码段**时，最易留下**结构碎片**。本轮删 4 个 workflow 的自建状态，
每个 workflow 都出现同一类损伤，静态校验器最终只报出其中一处：

| 损伤形态 | 现象 | 判据 |
|---|---|---|
| **孤立注释 + 孤立 `}`** | 删方法体时把签名删了、body 留着（`{` 已开、`}` 已留）⇒ 花括号 -1 | 逐字符扫描求配平 |
| **孤立 XML 注释块** | 方法删净后留下 2~3 行 `/// <summary>` 悬空 | 成段删除时须连带吞掉紧邻的 `///` |
| **跨对象调用被误改** | 批量把 `SetPhase(` 改名时，连`cam.SetPhase(_phase)`（对 `MonitorCamManager` 的调用）也改了 | 替换必须排除**对象限定**形式 |

> ⛔ **判据：删代码段后必须跑「逐字符花括号扫描」而不是 `text.count('{')`。**
> `count` 会把**字符串字面量与注释里的花括号**算进去 —— 本轮 `WeldParamControlWorkflow.cs`
> 被 `count` 判为「平衡」而逐字符扫描判为 **-1**，差异全部来自注释文字。
> 逐字符扫描须正确跳过：`// 行注释` / `/* 块注释 */` / `"字符串"` / `'字符'` / `@"逐字字符串"`。

### ⛔ 更隐蔽的一种：判据自身把「同名不同义」当成残留

`MonitorCameraWorkflow` 有两个 `_phase`：

```csharp
private MonitorWorkflowState _flowState;              // 设备状态 → 本轮删除
private volatile MonitorCameraPhase _phase = ...;     // 算法相位 → 必须保留
```

判据「`_phase` 必须 0 处」会**逼你删掉算法相位**（`MonitorResult.Phase` 的数据源）。

> ⛔ **判据：字段残留检测必须按「类型」而非「名字」判定** ——
> 用 `private\s+(?:volatile\s+)?(\w+)\s+_phase\s*=` 抓出**声明**并断言其类型集合，而不是数名字出现次数。
> 同理「`SetPhase(` 残留」必须用 `(?<![.\w])SetPhase\s*\(` 排除 `cam.SetPhase(`。

### ⛔ 第三种：正则把方法定义行的形参当枚举成员

`re.sub(r'SetPhase\(\s*(?:XxxState\.)?(\w+)', ...)` 会匹配到**方法定义行** `SetPhase(XxxState phase, string reason)`
的形参名 `XxxState`，随后 `MAP['XxxState']` 抛 `KeyError`。

而且 `\w+` 会**重叠回溯**：`XxxState` 少吃一个字符又匹配上 `XxxStat`，报出
`KeyError: 'LaserWeldHeadWorkflowStat'`（少一个 `e`）—— 这种报错信息极具误导性。

> ⛔ **判据：枚举成员名到目标值的映射替换，一律用逐成员显式 `str.replace('Call(Enum.Member', ...)`，
> 不用正则捕获成员名。** 正则只用来定位「签名行」，不用来做替换。

## 四之十一、判据出现「全库只有 1 处」时先抽验（2026-10-09）

本轮我断言「只有 `LineLaserWorkflow` 覆写了 `GetStepName`」并据此计划「给其余四个补覆写」——
**实测五个 workflow 全部已覆写且全部按 `switch (step)` 判步号**，代码本已合规。

误报原因：Grep 正则 `override string GetStepName` **漏了 `protected`** 前缀。

> ⛔ **判据：任何「全库只有 N 处」的结论（N 很小，尤其 N=1），下结论前必须手工抽验 2~3 条命中，
> 确认正则没有漏掉修饰符/前缀。** 「1 处」与「几十处」的风险不对称：后者漏了也还会报出很多条，
> 前者漏一条就变成假阴性，直接导致「去改本来合规的代码」。

## 四之十三、⭐ 凭空造属性：凡第三方控件的成员名，**必须在官方文档里出现过**（2026-10-09 编译打回）

给 `AntdUI.Input` 做按行着色时，我写了 `inputLog.TextLength` 取本行起点。
业主编译后回：**「`int start = inputLog.Text.Length;` 才是正确的，你的写法又自己猜测了一部分属性！」**

**核对官方 `raw/AntdUI/wiki-zh/Control/Input.md` 属性表**：

| 我写的 | 官方有没有 | 正确写法 |
|---|---|---|
| `inputLog.TextLength` | ❌ **属性表里没有**（只有 `Text` / `IsTextEmpty` / `TextTotalLine` / `SelectionStart` / `SelectionLength`…）| `inputLog.Text.Length` |
| `inputLog.Text.Length` | ✅ `Text`（string）在表内，`.Length` 是 string 自身成员 | ✅ |

项目内还有**同型先例**可印证：`FilebackupPage.cs:660` 早就在写 `inputLog.SelectionStart = inputLog.Text.Length;`
（同样是 `AntdUI.Input`，长期在用）⇒ 我连本项目的既有用法都没查。

> ⛔ **判据（通用，可拦住整类问题）**：
> **凡第三方控件（含 AntdUI）实例上的成员名，必须在该控件的官方文档属性表/方法表里出现过；
> 没出现过 ⇒ 一律判为「凭空造」，不许写进代码。**
>
> 落地做法：把官方 md 的属性表用 `\*\*(\w+)\*\*` 抽成集合，
> 再把代码里 `控件名\.(\w+)` 抽成实际使用集合，**差集即违规**。
> ```python
> official = set(re.findall(r'\*\*(\w+)\*\*', open(WIKI, encoding='utf-8').read()))
> used     = set(re.findall(r'inputLog\.(\w+)', code))
> unknown  = used - official - ALLOWED_INHERITED   # ALLOWED_INHERITED 补基类/事件处理器
> ```
> 阴性对照：把 `TextLength` 注入回去，差集立刻报出它 ⇒ 判据有区分度。

**为什么值得单列一条**：本项目两天内已 **3 次**栽在「自己造 API」上
（`SetStyle` 拖到核实后才用、`GetCoordinate` 拿来做近似、`TextLength` 直接凭空造）。
共同点都是**「看起来很合理」的 API 名** —— 正因为合理，静态校验与肉眼 review 都拦不住，
⛔ **只能靠「官方文档集合做差集」这条机械判据**。

⚠️ **配套**：白名单要显式列出「官方 wiki 未收录但基类/继承链提供」的成员
（如 `TextChanged` / `ScrollToCaret` / `InvokeRequired` / `BeginInvoke` / `Dispose`），
否则会假阳性。但**白名单只收「确实存在且已实证」的**，⛔ 不许往里塞「我以为有的」。

### ⛔ 判据的覆盖盲区：只扫代码后置会漏掉 Designer（2026-10-09 二次打回）

上面这条判据落地时我只扫了 `code`（`.cs` 后置），**没扫 `.Designer.cs`**。
结果同一轮又造了一个属性：

```csharp
this.selSeriesGroup.ShowSearch = false;   // ← 编译报「未包含 ShowSearch 的定义」
```

**核对官方 `Select.md`：25 个属性里没有 `ShowSearch`，`Input.md` 的 97 个属性里也没有** ——
它不属于任何 AntdUI 控件，纯粹是我想当然。

> ⛔ **判据（补齐覆盖）**：
> **① 扫描源必须是「代码后置 + Designer 两份拼接后再抽成员名」** ——
> Designer 里 `this.<控件名>.<成员> = ` 是成员访问的**主要发生地之一**（布局属性全在这）。
> **② 对象初始化器要单独扫**：`new AntdUI.Checkbox { Name=..., Text=... }` 里的成员
> 既不带控件名前缀，也不在 `控件名.成员` 形态里，须用 `^\s+(\w+)\s*=` 从初始化器块里抽。
> **③ 嵌套成员访问只取第一段**：`selSeriesGroup.Items.Add(...)` 只查 `Items`，
> 不要把 `Add` 记到 `selSeriesGroup` 头上（`Add` 来自 `BaseCollection`，属另一层）。

**本轮全量核对结果**（4 处控件 × 官方 md 集合做差集）：

| 控件 | 用到成员 | 未证 |
|---|---|---|
| `selSeriesGroup`（Select） | `Dock`/`DropDownArrow`/`Font`/`Items`/`Location`/`Name`/`SelectedIndex`/`SelectedIndexChanged`/`Size`/`TabIndex` | **0** |
| `flowGroup*`（FlowPanel） | `Dock`/`Font`/`Location`/`Name`/`Size`/`TabIndex` + 基类 `SuspendLayout`/`ResumeLayout` | **0** |
| `panelSeriesHost`（Panel） | `Controls` + 基类布局成员 | **0** |
| 动态 `new AntdUI.Checkbox {…}` | `CheckState`/`Checked`/`Cursor`/`Font`/`ForeColor`/`Name`/`Size`/`Text` | **0** |

⭐ **副产品**：统计项目内 4 处既有 `Select` 控件（`selectRsiCycle`/`cmbJob`/`cmbFps`/`cmbFreq`/
`selFlowEnableGuide`…）实际只用 9 个属性 —— 可作为「写新 Select 时照抄哪几个」的**安全名单**。

⚠️ **纪律延伸**：`DropDownArrow` 官方 `Select.md:21` 确证存在（默认 `false`），故保留；
但**项目内 4 处 Select 无一用它** ⇒ 它属于「官方有、项目未实证」，首次用在项目里，
标注为「若上机表现异常，删掉这一行即回默认（无箭头）」。

---

## 四之十二、第三方 DLL 的 API 核实：换呈现通道，不换功能语义（2026-10-09 P3 批 C）

P3 批 C 要做图表**悬停读数**，需要「像素 → 数据坐标」换算。ScottPlot 是二进制 DLL，
本机**无 C# 编译器**（rules/KR-010），`Reflection.Assembly.LoadFrom` 又被安全策略拦截
（报「equivalent to Add-Type」）⇒ **无法核实方法签名**。

**我试过的路（都失败了，且失败形态各不相同）**：
1. 从 DLL 字节里正则捞方法名 → 只能证明「有这个字符串」，**证不出参数类型与返回值**。
2. 反射加载 DLL → **被安全策略拦截**。
3. 自己写 ECMA-335 元数据解析器读 `MethodDef` 签名 → 连续踩坑：
   - 元数据流偏移在本程序集是「**相对元数据根**」而不是规范说的 RVA；
   - `HeapSizes` 位与真实行布局不一致（实测标称 4 字节、实际 2 字节自洽）；
   - 行数在表头读过一次又被重读一次，整体错位。
   最终**未能定案**，脚本已删除（`_tmp_*` 清零）。

### ⭐ 最重要的教训：**不要为了绕开技术难度而改变功能语义**

拿到「核实不了像素↔坐标 API」这个结论后，我做的第一件事是**改功能**：
把「悬停读点值」改成「按 X 近似换算 + 鼠标移动区域持续显示」。
业主当轮即驳回：「**我要的是鼠标移到点上读出 Y 值，不是鼠标移动区域一直显示值**」。

> ⛔ **判据（本轮最可复用）**：
> 当「技术手段不可核实」时，**正确做法是换一条已实证的呈现通道**，
> 而不是把功能降级成「一个不需要该技术也能做的近似品」。
> 本轮正解：呈现改用 `AntdUI.TooltipComponent` —— 该控件在本项目 `MainPage` 已实证
> （`new AntdUI.TooltipComponent { ArrowAlign = AntdUI.TAlign.Top }` + `SetTip(control, string)` 两参），
> 于是**像素换算只影响命中手感，不影响读出的数值**（读数直接取自数据源，不是换算出来的）。
>
> **自检**：写完先问一句「业主要的是这个吗」，而不只是「技术上做得出吗」。

### 判据设计：像素距离 vs 数据距离

初版判「命中」用的是**数据 X 距离**（`Math.Abs(cv.X[i] - targetX)`）——
那正是「鼠标移动区域一直显示」的成因。修正为**二维像素距离** `Math.Sqrt(dx*dx + dy*dy)`，
配 `HoverPixelRadius = 18` px 硬半径：指针不在点附近就 `ClearHoverTip()`。

> ⛔ **判据（本次最可复用的一条）**：
> **第三方 DLL 的方法签名属语义判据。核实不了时，不要凭记忆写调用 ——
> 改写成只依赖「本文件已实证调用过的 API」，功能做近似而非精确。**
> 本轮落法：悬停按页面自己维护的 `MinValueRobotX/MaxValueRobotX` 与控件宽度做**线性近似**，
> ⛔ 不调 `GetCoordinate` 一类未核实方法；同理不调 AntdUI Table 的 `CheckAll`/`RefreshRows`，
> 改为「改数据源属性 + 复用已实证的 `FillPage()` 重填」。
>
> **代价要写进 wiki**：近似读数不承担精确量测职责（该「精确区段定位」能力**已于 2026-11-02 随 `DataReviewerPage`「按 X 范围显示区域」模块整体移除**，滑块 `uiTrackBar1` 与其专属判据一并删除；此后页面只有悬停近似读数，⛔ 不得再写成「由滑块承担」）。
> **收益**：一个编译期不确定点降为 0。宁可功能少一点精确，不要多一个 CS0029/CS1501。

**配套判据：负向对照是「全绿」的唯一有效证明**
本轮 89/89 全绿后，从上一份 `output` 包解出**修改前**的同名文件跑同一条判据
⇒ 报 **29/89（60 项 FAIL）**。这才证明判据在做区分。
⛔ 只报「0 处 FAIL」的静态校验没有任何信息量 —— 必须能对修复前的版本报出东西来。
（操作细节：解包目录要用**工作区内**的绝对路径；Windows Python 的 `/tmp`
与 Git Bash 的 `/tmp` 不是同一位置，会静默 `cp: cannot stat`。）

**配套判据：签名与调用点必须成对判**
本轮 `AppendNearest` 一度声明为 `void` 而调用点按 `string` 接收（**CS0029**）。
判据只查「方法存在」会漏；必须成对断言「**声明的返回类型 == 调用点接收的类型**」。
抓到的就是这个不一致 —— 静态校验器抓到的**唯一一处真实编译错误**。

---

## 五、成员遮蔽与回流

## 追加条目 · 跨文件架构判据的四类过报

> 触发场景：把「抽象-实体-业务-消费」与「代码层边界」做成可机械判定的**跨文件**判据
> （落点 `scripts/arch_boundary_scan.py`，登记见 [[standards/CodeSimplification-Tooling]]）。
> 单文件判据的过报多来自正则，跨文件判据的过报多来自**把职责内行为当成越界**。

### 坑 1 · 抽象层第三方依赖不能匹配裸标识符

- **现象**：抽象层枚举成员 `IntelligentLaser = 1` 被判成厂商 SDK 引用。
- **判据**：只认 `using <厂商命名空间>` 与 `DllImport`；裸词（枚举值 / 常量 / 标识符）一律不判。
- **豁免**：ADR 已裁定的**帧载体契约**不属于违规 —— `IMonitorCamApi` 以 `Mat` 为帧载体（ADR-097），抽象层出现 `using Emgu.CV` 是业主裁定，⛔ 不得按 H2「抽象层零第三方依赖」机械清扫。

### 坑 2 · 「计算路径落盘」必须区分写入与只读探测、区分职责内 IO

- **现象**：`File.Exists` / `File.ReadAllText` / `Directory.GetDirectories` 全被计为实现层落盘，造成大量假阳性。
- **判据**：只认**写入 / 记录**动作（`File.Write*`、`StreamWriter`、`XmlSerializer`、`RunRecordManager`），只读探测不判。
- **豁免**：配置导入 / 打包 / 读取工具 / Manager / 回放算法的文件 IO 是其**裁定职责**（H7 / ADR-097），豁免按**机制表述**而非目录名一刀切。

### 坑 3 · 厂商向下转型要分「Manager 能力入口」与「业务层绑定」

- **判据**：H5 反例针对**业务层 / UI 层** `as Delta*`；Manager 持有实现类实例，向下转型暴露厂商专属能力是合法入口（`MontionManager.GetDeltaAxis` 注释明示）。
- **落地**：判据排除 `*Manager.cs`，只报流程层 / UI 层；否则会把 Manager 的合法能力入口一起误杀。

### 坑 4 · 同一规范存在两套长度口径时，warn 不可信

- **结论**：`csharp_review.py` 的 `A.注释规范` 按「整段字数」判 `summary 超20字`，与 C16/C18 权威口径（只数汉字、按 `。；！？` 分句、跨行合并）不一致 ⇒ 该类 warn 属假阳性。
- **判据**：一个规范条款只许有一个权威判据；出现第二套口径时以 `comment_scan.py long` 的 `merged_over` 为准，并同步修 `csharp_review.py`，⛔ 不得靠人肉忽略噪声。
- **门禁联动**：改判据须与 [[standards/CodeSimplification]] 4.1 映射表同轮同步，并跑 `simplify_selfcheck.py`。

## 追加条目 · 判据误报与机械批改脚本的结构风险

### 坑 5 · 一个规范条款只许有一个权威判据

- **结论**：`A.注释规范` 按「整段 summary 汉字数」与 `A.注释超20字` 按「只数汉字、按 `。；！？` 分句、跨行合并」并存时，同一段注释会被两套口径判出相反结果，warn 不可信。
- **判据**：改标准必须同轮改判据，并同步 `simplify_selfcheck.py` 的关键字与 [[standards/CodeSimplification]] 4.1 映射表；权威口径以 `comment_scan.py long` 的 `merged_over` 为准。

### 坑 6 · 变量声明正则的类型位不能是语句关键字

- **现象**：`return value == null;` 被 `(?:var|[\w...]+)\s+(value)\s*=` 当成变量声明，统计出「后续使用 0 次」的幽灵命中。
- **判据**：声明正则前先排除 `return/throw/if/while/using` 等语句首关键字；swap 变量、后续被重新赋值的可变量、参数改写前的快照一律豁免。

### 坑 7 · 跨文件职责不能靠单文件文本判定

- **现象**：初始化父级门禁判据匹配 `InitializeMachineTick(`，把每拍驱动的**调用点**当成定义，误报缺 `ParentKey`。
- **判据**：判据锚点用**代码定义**（`public void X(`）而非调用；调用链上的约束应在被调用方判定。

### 坑 8 · 解析器幽灵成员会污染顺序判定

- **现象**：`else if (...)` 被方法解析器收成私有方法 `if`，其 order 高于后续构造函数，导致合规的构造函数重载被报顺序错误。
- **判据**：成员收集阶段过滤控制流关键字；顺序判据的命中必须能指向真实的成员声明行。

### 坑 9 · 机械成员重排脚本可切坏 if/else 链

- **结论**：`simplify_apply_member_order.py --fix-victims` 的块切分会把成员插入 `if (...) { }` 与 `else if (...)` 之间，造成类提前闭合与编译期结构错误。
- **判据**：含构造函数重载或跨行 if/else 链的文件禁用该脚本，改按字节手改；**任何重排后必须真编译复核**。结构守卫、成员顺序报告、判据自检三者全绿也不代表编译通过（[[rules/KR-010-No-Compiler-Honesty]]）。

### 坑 10 · 方法名启发式不能判「旧版本残留 / 死代码」

- **现象**：`(Old|Legacy|Backup|_Deprecated)$` 名称匹配就把方法报成「确认无调用后删除」，实际 `ConfigSelfHeal.Backup` 有 2 处调用（配置自愈前备份）、`WeldHeadSlaveDevice.DescribeTemperatureThreshold` 有 2 处调用（温度告警文案）。
- **判据**：死成员只能由**真实零消费**（`C.疑似死函数`）判定，且按顶层裁定 2「0 消费只报不删」；⛔ 名称、日期、版本号、注释里的「旧/废弃」字样都不是消费证据。
- **预防**：删除类判据上线前必须对命中集做两次独立 Grep 交叉验证消费方；发现任一命中仍有调用方，先删判据而不是删方法。

## 相关页面

- [[lessons/StaticVerifier-CSharp-Scoping]] —— 同源拆分页
- [[lessons/StaticVerifier-Wiring-Integrity]] —— 同源拆分页
- [[lessons/StaticVerifier-Batch-Script-Traps]] —— 同源拆分页
- [[lessons/StaticVerifier-Tooling-Substitutes]] —— 同源拆分页
- [[lessons/StaticVerifier-AdrNumbering]] —— 同源拆分页
- [[lessons/StaticVerifier-RecentJudgements]] —— 同源拆分页
- [[lessons/StaticVerifierJudgements]] —— 源页（拆分前全量）
