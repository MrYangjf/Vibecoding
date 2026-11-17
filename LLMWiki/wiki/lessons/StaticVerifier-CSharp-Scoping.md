---
title: StaticVerifier-CSharp-Scoping
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


## 一、C# 语法与类型系统

### 1.1 可空引用类型是 CLASS-only 语法错误（CS8632）

`SomeClass?` 是 C# 8 的**可空引用类型**特性，C# 7.3 拒绝；`int?` / `double?` 是 `Nullable<T>`（C# 2 就有），合法。

**⇒ 「禁 `?`」是错判据。** 必须先分 class / struct 名单再交叉判定：

```python
types = set(re.findall(r'\b(?:class|struct)\s+(\w+)', src))
# 仅当 X 同时是 class 名单成员时，X? 才是 CS8632
if re.search(r'\b' + name + r'\s*\?', code) and name in class_names:
    report(name)
```

**连带陷阱**：改为 `struct` 后，**C# 7.3 不允许显式无参构造**（C# 10 才有）⇒ 须删构造并靠 `default(S)`。且**必须核对 `default` 零值与被删构造语义等价**（`enum {Stopped=0}` ⇒ `default` 恰好等于 `Stopped/0.0/false`；若原构造赋了非零默认，改 struct 会静默改语义 ⇒ 改用工厂方法）。

**扩充禁用清单**：`not null`(C#9) · `#nullable enable`(C#8) · `with { }`(C#9) · 显式无参 struct 构造(C#10)。

### 1.2 关键字当标识符（CS1002/CS1519）—— 一处非法声明引发一串假错误

**现象**（2026-10-08 实证）：`ApplyGalvoAmplitude` 报 3 个错，指向 3 个不同位置

```
1、表达式项“=”无效
2、未提供与“SetGalvoParams(GalvoParams)”的所需参数“param”对应的参数
3、应为标识符；“params”是关键字
```

**真根因只有一个**：`GalvoParams params = CreateLogicalHome();` —— `params` 是参数数组修饰符，声明非法 ⇒ 名字未绑定 ⇒ 后续使用全部级联报错。

> ⛔ **判据：多个错误聚在同一方法 + 错误信息含「应为标识符 / 是关键字」⇒ 先找那一条非法声明，不要逐条追。**

**判据实现**（全库可跑）：对每个 `<Type> <name>` 声明位断言 `name` 不在保留字集合。

⚠️ **正则必须带护栏**，否则 `return true;` 被解析成「类型 `return`、变量名 `true`」⇒ **135 处误报**。正确做法：① 先剥 `///` 与 `//` ② 左侧类型不能是关键字/字面量（`NOT_TYPE`）③ 匹配声明形态 `\s*(?==|[;,){])` + 小写开头名。

**C# 保留字全集**：`abstract as base bool break byte case catch char checked class const continue decimal default delegate do double else enum event explicit extern false finally fixed float for foreach goto if implicit in int interface internal is lock long namespace new null object operator out override params private protected public readonly ref return sbyte sealed short sizeof stackalloc static string struct switch this throw true try typeof uint ulong unchecked unsafe ushort using virtual void volatile while`

**连带处置**：修完顺手改掉**诱发它的近似名**。`param` 合法而 `params` 保留，只差一个字母 —— 把形参 `SetGalvoParams(GalvoParams param)` 改成 `galvo`，坑就消失了，而不是留在记忆里。

**近似关键字**（合法但诱人，实测存量 16 处，**一律不动**）：`param` `value` `args` `record` `group` `where` `select` `from` `join` `into` `let` `yield` `add` `remove` `set` `when` `with` `init` `managed`。本项目实例：`IFloatValue value`(HikCam) · `WeldActionRecord record`(RecordFileStore) · `GroupNode group`(PointCloudViewer) · `AutoParam param`(ProcessControlPage)。**处置原则：存量合法不动，新写代码避开。**

### 1.3 值类型与 `null` 比较（CS0019）

```csharp
if (e.RobotData.RIst == null)   // ❌ RIst 是值类型
```

⚠️ 判据方向：**先确认该字段是否值类型**（`GetType().IsValueType` 或看定义），再决定要不要 `== null`。

### 1.4 静态类不能有实例构造（CS0710）

`static class` 不得声明实例构造。工具类写了 `private ClassName() {}` 是**既非法又多余**（C# 本就禁止实例化静态类）—— 直接删，**不要**补一个 `static` 构造（工具类两者都不需要）。判据：断言无 `static class X` 含 `X()` 实例构造。

### 1.5 ⭐ 关键字作变量名 = **整段解析失败**（2026-10-09 业主编译打回，第 7 次绿灯被打回）

```csharp
private void ChkSeries_CheckedChanged(object sender, AntdUI.BoolEventArgs e)
{
    AntdUI.Checkbox checked = sender as AntdUI.Checkbox;   // ❌ checked 是运算符关键字
    if (checked != null && checked.Checked) { ... }        // ⛔ 整个方法体连带报错
}
```

业主原话：「**使用 checked 做变量导致整段错误**」—— ⛔ **不是一处报错，是整个方法体都挂**，
因为解析器在该处就崩了。

**为什么会写进去**：`sender as AntdUI.Checkbox` 转出来的局部变量，
最自然的名字是「和 Checkbox 相关的词」→ 直觉写了 `checked`。

> ⛔ **判据（业主长期约定）**：**不要使用 C# 关键字做变量/字段/参数名**，容易报错；
> **需要时在前面增加小写字符来避免**（项目内既有范式：`chkSelf` / `box` / `cv` / `sel`）。
> 正确写法：`AntdUI.Checkbox chkSelf = sender as AntdUI.Checkbox;`

**本条判据的三次设计失误（判据自身比代码更难写，供复用）**：
| 失误 | 现象 | 正解 |
|---|---|---|
| ① 把「关键字 + 标识符相邻」当命中 | 误报 `private const int HoverThrottleMs = 60`、`private long _lastParamVersion` —— 那里 `int`/`long` 是**类型位置**不是变量名位置 | 必须判**「关键字出现在标识符位置」**：`(?:Type\|var)\s+kw\s+标识符` 或 `kw\s*=`（作左值） |
| ② 把 `foreach (var rec in actions)` 的 `in` 当命中 | 误报 | `in` 在 `foreach` 里是**语法关键字**，不是标识符 ⇒ 不纳入 `OTHER_RISK` |
| ③ 把 `string`/`int`/`object` 等**基类类型名**与 `checked` 一视同仁 | 判据整体失效（几乎每个字段都会命中） | 只查**既不能作类型、也不能作变量名**的运算符型关键字：`checked` `unchecked` `lock` `fixed` `event` `delegate` `params` `ref` `out` `base` `this` `operator` `typeof` `sizeof` `default` `new` `null` `true` `false` `void` |

**判据验证方式（人造样本，比阴性对照更可靠）**：
本条的阴性对照**做不出来** —— 引入 `checked` 变量的那次修改晚于当天备份包，
备份里没有该代码。故改用**人造样本**双向验证：
- 7 个**合法**样本（`private const int X = 60` / `private long _y` / `foreach (var rec in actions)` /
  `int checkedValue = 3` / `var locked = 1` …）⇒ 全部**不命中**
- 4 个**非法**样本（`AntdUI.Checkbox checked = …` / `checked = sender;` /
  `private int unchecked = 5;` / `object @params = null;`）⇒ 前 3 个**全部命中**；
  第 4 个 MISS ⛔ **不是真漏** —— `@params` 是 C# 合法转义写法，本就不是非法样本。

**扫哪些文件**：所有 `.cs`（含 `.Designer.cs`）。**命名约定也一并检查**：
若项目统一用 `chk` 前缀（`chkSelf` / `chkSeamWidth`），可作为软约定写进 `raw/skills/AdaWeldsys_Skills/04-Style/CSharpStyle.md`（该文件在 `raw/` 层，**不是 wiki 页面**，故用纯文本路径而非 `[[链接]]`）。

### 1.6 ⭐ 常量/字段的声明类型必须与其消费点目标类型匹配（CS0266 隐式窄化）

**实证（2026-10-21 业主编译打回）**：`CalcGalvoFrequency`（返回 `int`）与 `EffectiveSwingFrequency`（返回 `int`）内 `return AutoParam.DefaultSwingFreqHz1;` 报「无法将类型 double 隐式转换为 int」——根因是**默认常量声明成了 `const double`**，而协议侧频率本就是整型（`GalvoParams.Frequency` 为 `int`，10~500Hz 精度 1）。

```csharp
public const double DefaultSwingFreqHz1 = 500.0;   // ❌ 消费点是 int 返回值
public const int    DefaultSwingFreqHz1 = 500;     // ✅ 与协议整型一致
```

**判据（可静态化）**：扫「**返回类型为 `int` 的方法**内是否 `return` 了**声明为 `const double` 的成员**」。
- 「int 方法直返 double 常量」⇒ 命中（CS0266 防线）。
- 关键：**不是所有 double→int 都错**——`double h1 = cond ? doubleField : intConst;` 是**合法**的三元提升（int 隐式转 double），只有「目标是 int 上下文」才窄化失败。判据必须**限定消费点上下文**，不能只扫「double 与 int 同现」。

**配套判据（配置读取纪律，同轮发现）**：模块外直读配置类的**静态成员**（`ConfigClass.Member`）违反「配置读取经 `WeldParamManager` 唯一入口」（ADR-053 / ADR-066）。例外白名单须显式列出（如分区路由枚举 `WeldAlgorithmsConfig.AlgorithmsZone`，它是**传给 Manager 方法的路由参数**，不是配置值直读）；模块内部（`WeldParamControl/`）由 Manager 独占持有，豁免。

> ⚠️ **两处误报必须人工甄别、不得放宽标准凑绿**（本轮实测）：① `AlgorithmsZone` 枚举路由 → 列入白名单；② `WeldAlgorithmsConfig.ProcessControlSection` 出现在 `WeldParamManager.cs` **模块内部** → 豁免模块内路径。
> ⛔ **判据自身是"静态近似"**：它只覆盖「int 返回值直返 double 常量」这一形态；**重载解析/隐式转换的完整合法性只有编译器能定**——绿灯后仍须声明「真编译待 VS」。

---

## 二、名字解析与作用域

### 2.1 静态方法跨类必须写类型名

编译器**只把静态成员纳入「同类型」的名字查找**。`GalvoParams.CreateLogicalHome()` 是 static，在 `LaserWeldHeadWorkflow` 里裸调 `CreateLogicalHome()` ⇒ 「当前上下文中不存在名称」。

**判据**：
```
① 收集所有 public/internal static 方法 → 记住所属类型
② 调用点若无 '.' 前缀，且该方法的所有定义都不在本文件 ⇒ 跨类裸调，判违规
```

⚠️ **「同类内豁免」不可省**：`KukaRsiComm` 里的 `ParseRobotPacket` / `BuildReplyXml` / `GenerateRSIXML` / `ParseRSIXML` 都是**同类静态互调，完全合法**。初版漏了豁免 ⇒ 7 处误报。

### 2.2 跨类引用 `private` 成员（CS0103）

同名文件里同级类互引 `private` 是高频形态（本项目 `WeldHeadSlaveDevice.cs` 一个文件塞 4 个类：`WeldHeadSlaveDevice` / `WeldHeadConfig` / `GalvoParams` / `MotorState`；`DeltaMotionConfig.cs` 塞 2 个）。

**为何静态校验易漏**：只判「符号是否存在」时，全文件匹配到 1 定义 + 2 引用，看着齐备，实际其中 1 处够不着。

**判据**：
```python
# 1) 按花括号配平把文件切成 class/struct/enum 块
# 2) 收集每块的 private 成员名
# 3) 在【其它】块的正文里搜这些名字 → 命中即 CS0103
```

同类高发形态：引用基类 `private`、无继承却用 `protected`、**同级两个类各声明同名常量**（一个遮蔽另一个）。**共享默认值放在已经持有其它默认值的那个类上，并改 `public const`。**

### 2.3 实参必须用「该方法作用域内」真实存在的名字

`FillOutput(WeldParamManager wp)` 体内写 `CalcGalvoAmplitude(seamWidth)`，但该方法内无 `seamWidth`（宽度来自 `wp.CurrentSeamWidth`）；**同文件** `FillXlOutput(seamWidth)` 的 `seamWidth` 却是真实形参 —— 改签名时看串。

**判据**：按花括号配平切方法体 → 建「局部变量 + 形参 + `foreach` 变量 + 本类字段」集合 → 断言每个调用实参可溯。

⛔ **禁全文判同名** —— 本项目一文件多类，同名标识符在不同类/方法里含义不同。

### 2.4 重载 + 可选参数 ⇒ 遮蔽（最隐蔽）

```csharp
A: BuildReplyXml(double laserPower, double wireSpeed, string ipoc, string sensorType)            // 4 参
B: BuildReplyXml(RsiPacketFormat replyFormat, double, double, string, string, double = 0.0)      // 6 参（末位可选）
```

调 `BuildReplyXml(laserPower, wireSpeed, packet.Ipoc, SenType, cutWireSignal)`（5 实参）期望匹配 B，**实际报「参数 1: 无法从 double 转换为 RsiPacketFormat」** —— 编译器先试 A，A 的前 3 参类型全对（只少一个可选尾参）⇒ 咬定 A。

> ⛔ **可选参数不参与重载候选的优先级判定 —— 编译器在展开可选参数之前就已经决定。**

| 修法 | 做法 | 适用 |
|---|---|---|
| **A 同步补参数**（实证采用） | A 也加同名可选参数并转发给 B | 两条路径等价，调用方无感 |
| 调用方消歧 | 调 B 写全 6 参 | 不想动公开签名时 |

**防复发**：改重载集后断言「每个调用点实参数 ≥ 某重载必填数」**且**「任意两重载首参类型可区分」（若前 N 参类型完全相同、只尾部可选参数不同 ⇒ 必然遮蔽）。

---

## 相关页面

- [[lessons/StaticVerifier-Wiring-Integrity]] —— 同源拆分页
- [[lessons/StaticVerifier-Checker-FailureModes]] —— 同源拆分页
- [[lessons/StaticVerifier-Batch-Script-Traps]] —— 同源拆分页
- [[lessons/StaticVerifier-Tooling-Substitutes]] —— 同源拆分页
- [[lessons/StaticVerifier-AdrNumbering]] —— 同源拆分页
- [[lessons/StaticVerifier-RecentJudgements]] —— 同源拆分页
- [[lessons/StaticVerifierJudgements]] —— 源页（拆分前全量）
