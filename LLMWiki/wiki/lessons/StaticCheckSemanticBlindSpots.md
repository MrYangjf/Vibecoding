---
title: 静态校验的两类编译级盲区 — 可空引用类型与标识符定义域
date: 2026-10-08
updated: 2026-10-30
tags: [教训, 静态校验, 编译错误, C#7.3, 可空引用类型, 作用域, CS0103, CS8632]
status: accepted
---

# 静态校验的两类编译级盲区

> 来源：2026-10-08 P2 第一批。Step 2.6 静态校验 **63/63 全绿**，业主在 Visual Studio 真实编译时仍报出 **2 个编译错误**。本文记录这两类**静态校验天然抓不到、必须靠编译器**的错误，以及补进校验器的判据。

## 背景：本项目没有 C# 编译器

`dotnet` / `msbuild` / C# 编译器被安全策略拦截，本机无 Visual Studio（见 rules/KR-010）。因此 Step 2.6 用 Python 静态校验替代 —— **但静态校验的能力边界必须诚实界定**，否则「63/63 全绿」会给人虚假的安全感。

**判据**：静态校验擅长「**模式化**」错误（命名空间缺失、csproj 路径、语法禁用项、配置四点闭环）；不擅长「**语义化**」错误（类型系统合法性、名字解析）。后者只能靠编译器。

---

## 盲区 A · C# 8 可空引用类型（`ClassName?`）—— 报 CS8632

**现象**：`ReadMotorStatus()` 返回 `MotorState?`，而 `MotorState` 声明为 `class`。C# 7.3 报「可为 null 的引用类型在 C# 7.3 中不可用，请使用 8.0 或更高的语言版本」。

**为什么静态校验漏掉**：上一轮校验器的「C# 7.3 禁用语法」清单只列了 `switch 表达式` / `is not` / `record` / `init` / `??=` / `await using`，**没有 `ClassName?` 这一条**。

**关键区分**（这才是判据）：

| 写法 | 是什么 | C# 7.3 |
|---|---|---|
| `int?` / `double?` | `Nullable<T>` 值类型可空 | ✅ 合法（`Nullable<T>` 是 C# 2 就有的库类型） |
| `MotorState?`（`MotorState` 是 **class**） | **可空引用类型**，C# 8 语言特性 | ❌ **非法** |
| `MotorState?`（`MotorState` 是 **struct**） | `Nullable<MotorState>` 值类型可空 | ✅ 合法 |

⇒ **`?` 本身合法，取决于它修饰的是值类型还是引用类型。** 所以禁用清单不能只写「禁 `?`」，必须**先分出 class/struct 名单，再交叉判定**。

**修法（二选一）**：

| 方案 | 做法 | 适用 |
|---|---|---|
| **A1 改 struct（推荐）** | `class MotorState` → `struct MotorState` | 快照型数据天然适合值类型；`default(MotorState)` 即全零初值 |
| A2 不用可空 | 返回 `MotorState` + 另设 `bool TryReadMotorStatus(out MotorState)` | 不希望「null 表示读失败」时 |

⚠️ **A1 的连带约束（极易再踩）**：**C# 7.3 的 struct 不允许显式无参构造**（`public MotorState() { }` 是 **C# 10** 才有的特性）。改成 struct 后必须**删掉构造函数**，字段默认值靠 `default(T)` 承担。校验判据：struct 体内若出现 `()` 形式的构造函数 ⇒ 报 C# 10 特性。

**语义等价性核对**：删构造前确认 `default` 的零值与原构造赋值一致。本例原构造是 `State=Stopped / CurrentPositionMm=0.0 / IsReady=false`；`MotorRunState.Stopped = 0` ⇒ `default` 恰好等价。**若原构造赋了非零默认值（如 `IsReady=true`），改 struct 就改变了语义**，必须改为在声明处用属性初始化或保留工厂方法。

**补进校验器的判据**：

```python
# 全库：收集 class 名单 → 找 ClassName?
classes = set(re.findall(r'\bclass\s+([A-Za-z_]\w*)', src))
for cn in classes:
    # \b 后无 ? （排除 ?? 与可空值类型误判）
    if re.search(r'(?<![\w?])' + cn + r'\s*\?(?![\w?])', src):
        report(f'{cn}? 是可空引用类型（C#8），本项目 C# 7.3 非法')
```

同批补充的 C# 7.3/8/9 禁用项：`not null`(C#9) · `#nullable enable`(C#8) · `with { }`(C#9) · `struct` 无参构造(C#10)。

---

## 盲区 B · 标识符定义域（跨类 `private` 引用）—— 报 CS0103

**现象**：常量 `DefaultMotorPulsePerMm` 声明在 `WeldHeadSlaveDevice` 类内（`private const`），却在 `WeldHeadConfig` 类的构造函数里引用它 —— 报「当前上下文中不存在名称」。

**为什么静态校验漏掉**：上一轮只判「常量是否存在」，**没判「引用点在不在作用域内」**。全文件文本匹配对 `DefaultMotorPulsePerMm` 命中 3 处，看起来「定义 1 + 引用 2」齐备，实际上其中 1 处引用在另一个类里，够不着。

**同类高危模式**（都会编译失败）：

| 模式 | 症状 |
|---|---|
| 跨类引 `private` | CS0103 名称不存在 |
| 跨类引 `protected` 且无继承关系 | CS0103 |
| 引用**基类**的 `private` 成员 | CS0122/CS0103 |
| 同一文件内**两个类各有同名常量**，误以为共享 | CS0103（一个类遮蔽另一个） |
| 静态类里声明实例成员 | CS0710（见 `lessons` 已有条目） |

**修法（把默认值知识收敛到单一来源）**：本例把常量移到 `WeldHeadConfig` 并改 `public const`，`WeldHeadSlaveDevice` 构造经 `WeldHeadConfig.DefaultMotorPulsePerMm` 限定引用。选 `WeldHeadConfig` 的理由是**该类已集中持有全部默认值**（50/60/40/50/5/500 都在其构造函数内），默认值知识保持单一来源。

**补进校验器的判据**（按类切块 + 花括号配平，再做跨类互查）：

```python
# 1) 把文件按 class/struct/enum 切成块（花括号配平）
# 2) 收集每个块内的 private 成员名
# 3) 在**其它**块的正文里搜这些名字 → 命中即报 CS0103
for cname, body in blocks:
    for priv in re.findall(r'\bprivate\s+(?:const\s+|readonly\s+|static\s+)*[\w<>\[\]\.]+\s+([A-Za-z_]\w*)\s*(?:=|;)', body):
        for oname, obody in blocks:
            if oname != cname and re.search(r'(?<![\w.])' + priv + r'(?![\w])', obody):
                report(f'{priv} 是 {cname} 的 private，被 {oname} 引用 → CS0103')
```

⚠️ **注意排除「同名不同类」**：块内嵌套的局部变量、lambda 参数可能与 private 成员同名；判据要限定「声明为 private 成员」而非「文本出现过」。

---

## 结论：静态校验 63/63 ≠ 编译通过

**本项目的诚实表述模板**（每次交付都用）：

> Step 2.6 静态校验 N/N 通过，覆盖模式化错误（命名空间 / csproj 路径 / 语法禁用项 / 配置闭环 / 不变量）。
> ⚠️ **类型系统与名字解析类错误不在静态校验能力范围内**，本轮已发生的 CS8632 / CS0103 均为实例。
> ⛔ **真实编译待 Visual Studio 验证** —— 静态通过不等于编译通过。

**判据沉淀**：新增静态校验项时，先问「这是模式化还是语义化？」
- **模式化** → 可以静态查（如本例盲区 A 的 class/struct 交叉判定、盲区 B 的定义域切块）
- **语义化**（重载解析、装箱/类型提升、异步状态机、泛型推断、接口实现完整性）→ **静态查不可靠，必须编译器**

**减少往返的做法**：把「需要编译器才能确认」的错误类型（如可空引用类型）**提前写进禁用清单**，而不是等编译报出来再补 —— 本例两个错误都属于「一旦知道判据就能静态拦」的类型，属可预防。

> ⛔ **本专题已并入 [[lessons/StaticVerifierJudgements]]**（判据库第一章「C# 语法与类型系统」/ 第二章「名字解析与作用域」）。本页保留为原始案例记录，**新增判据一律写进判据库对应章节**，避免同一判据散落多处。
## 相关页面

- [[project/vibecoding-workflow]] — Step 2.6 正确性验证（本页为其判据补充）
- [[lessons/CSharp-Language-Pitfalls]] — C# 7.3 语法约束总表
- [[decisions/ADR-001-CS73-Constraint]] — C# 7.3 硬约束
- [[decisions/ADR-007-CodeSimplificationStandard]] — 字段初值写构造函数
- [[project/ReviewOptimization-P1-StructureDesign]] — 引入 `MotorState` 的那次结构落地
