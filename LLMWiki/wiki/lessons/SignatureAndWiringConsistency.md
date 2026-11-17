---
title: "签名-调用点一致性（改签名必查调用点，否则「全绿却编译不过」）"
date: 2026-10-08
updated: 2026-10-30
tags: [教训, 编译错误, 签名, 调用点, 静态校验, 可空引用类型, 跨类作用域]
status: accepted
---

# 签名-调用点一致性：静态校验的第三类盲区

> 本页记录 2026-10-08 P2 第二批（S-4~S-9）真实踩到的两类编译错误，以及它们暴露的**校验器盲区分类**。
> 前置页：[[lessons/StaticCheckSemanticBlindSpots]]（第一批：可空引用类型 + 跨类 private）。

## 一、事件

改 `KukaRsiComm.ResolvePlaceholder` 与 `BuildReplyXml` 的签名（各加一个带默认值的可选参数），改完「方法存在性」判据全绿，**实际上两处调用点都没传新参** —— 编译必然失败（CS7036 / 缺参）。

同一个文件里还发生了：批量 Python 脚本因 `assert` 中途失败而**整体回滚**，导致前面已成功的替换也丢失（`using` 没加上 → CS0246），而校验器只报「using 缺失」这一条，看不出它是**回滚副作用**。

## 二、判据一：改签名后必须逐个调用点核对实参个数

```
凡本轮改过签名的方法：
  1. 从方法定义取出「必填参数数」= 无默认值的参数个数
  2. 找出该方法所有调用点（跨文件！不只本文件）
  3. 每个调用点的实参个数 >= 必填参数数
```

⚠️ **两个高频漏点**：

| 漏点 | 后果 |
|---|---|
| **同文件内的调用点** | 最容易漏 —— 改签名和改调用点常分两次编辑 |
| **Manager 门面层** | 底层加了参，上层 `CommunicationManager.UpdateRobotWeldParams` 也要透传，否则功能是哑的 |

⚠️ **可选参数不是万能护身符**：加默认值确实能保证编译通过，但**语义上会静默丢值**（新参恒为默认值，功能不生效且无任何报错）。所以「加可选参数」只解决编译，**不等于接线完成**，必须另有一条判据核对「该参数真的被传了值」。

## 三、判据二：跨类作用域（上轮已立，本轮复现）

`DefaultMotorPulsePerMm` 类问题 —— 常量在类 A 的 `private const`，却在**同文件同级类** B 里引用。本轮新增的 `TorqueCurveModeTrapezoid` / `DeltaEnableOff` 若不加 `private const` 定义就会直接编译失败。

**校验做法**：按花括号配平切出顶层 `class/struct/enum` 块 → 收集各块 `private` 成员 → 在**其它**块正文互查这些名字。

本项目 `WeldHeadSlaveDevice.cs` 一个文件塞了 4 个类（设备 / `WeldHeadConfig` / `GalvoParams` / `MotorState`），`DeltaMotionConfig.cs` 塞了 2 个，**同级互引是高频形态**。

## 四、判据三：日志符号检查必须先剥离注释

误报实证：判据用 `Log\([^)]*"[^"]*[⚠]` 扫全文，命中 `DeltaMontionAxis.cs` 的 `/// <summary>…⚠️ 该位语义…</summary>` —— 符号在 **XML 文档注释**里，不是日志文本。

**正确做法**：先 `re.sub(r"///[^\n]*", "", txt)` 与 `//...` 剥离注释，再扫。⚠️ 同理适用于**任何**「禁止某种写法」的文本判据：不剥注释就会把注释本身当违规。

## 五、批量脚本改文件的原子性

Python 脚本里 `assert` 失败会**丢弃已做的替换**（本次 `open(p,'wb')` 在最后才执行，前面 replace 全在内存里）。两种改法：

| 改法 | 适用 |
|---|---|
| 逐个 `assert` + 立即 `write` | 每步独立可验，但中途失败会留下半成品 |
| **全部 `assert` 通过后再统一 `write`** | 需要先跑一遍 dry-run 校验全部锚点命中 |

⚠️ 更稳的做法：**改之前先 `assert txt.count(old) == 1` 全部检查完，再统一 replace**；或直接用 Edit 工具逐处改（本轮 `TaLaCurveConfig.cs` 缺 `using System.Xml.Linq` 就是靠 Edit 改的）。

⚠️ **另注**：按字节读写时**必须保留原 BOM 状态**（本仓库部分文件带 BOM）。`raw.decode('utf-8-sig')` 会吃掉 BOM，回写时要显式补回，否则整文件 diff。

## 五之二、关键字当标识符：一个非法声明引发一串假错误（2026-10-08 第二批踩到）

**现象**：`ApplyGalvoAmplitude` 报 3 个错，指向 3 个不同位置：

```
1、表达式项“=”无效
2、未提供与“WeldHeadSlaveDevice.SetGalvoParams(GalvoParams)”的所需参数“param”对应的参数
3、应为标识符；“params”是关键字
```

**真根因只有一个**：`GalvoParams params = CreateLogicalHome();` —— `params` 是 C# **参数数组修饰符**，不能作变量名。

| 表面错误 | 实际是 |
|---|---|
| ① `params.Width = amplitude` 表达式项 `=` 无效 | `params` 从未绑定成变量 |
| ② `SetGalvoParams(params)` 未提供实参 | 同上，名字不存在 |
| ③ 「`params` 是关键字」 | ⭐ **这才是真因** |

> ⛔ **判据：多个错误聚在同一方法、且错误信息里出现「应为标识符 / 是关键字」⇒ 先找那一条非法声明，不要逐条追。** 编译器把一个根因级联成 N 个症状。

**修法**：`params` → `galvo`。同时把接口形参 `SetGalvoParams(GalvoParams param)` 也改成 `galvo` —— **`param` 与 `params` 只差一个字母**，不改掉等于给后人留同一个坑（这正是本次事故的诱因：写调用处时把形参名 `param` 记成了 `params`）。两个调用方都是位置传参，改形参名零影响（Step 2.5 已换 pattern 复跑确认）。

### 校验判据（全库可跑，成本极低）

对每个 `<Type> <name>` 声明位，断言 `name` 不在 C# 保留字集合内。⚠️ **正则必须带护栏，否则 135 处误报**：

```
❌ 无护栏：return true;  →  type='return', name='true'  ⇒  报 135 处
✅ 带护栏：要求左侧不是关键字/字面量（NOT_TYPE）+ 匹配声明形态 + 先剥 /// 与 //
```

**其它易误判的坑**：`params` 只在**声明位**是关键字，`SetGalvoParams`（方法名）与注释里出现它都合法 —— 判据必须剥注释后、且按声明形态匹配，不能全文搜。

### 近似关键字（合法但诱人）

`param` · `value` · `args` · `record` · `group` · `where` · `select` · `from` · `join` · `into` · `let` · `yield` · `add` · `remove` · `set` · `when` · `with` · `init` · `managed`

本项目实测存量 16 处（`IFloatValue value` / `WeldActionRecord record` / `GroupNode group` 等）—— **均合法，不动**。新写代码避开即可。

## 五之三、三类「作用域/解析」错误的判据（2026-10-08 第三批踩到）

同一次编译报出三处**根因完全不同**的错误，都属于「名字解析」类，但机理各异：

### 1. 静态方法必须写 `类型名.` 前缀（CS0103 in context）

`GalvoParams.CreateLogicalHome()` 是 **static** 方法。我在新写的实例方法里裸调 `CreateLogicalHome()` ⇒ 「当前上下文中不存在名称」。

**为什么它比普通方法更易错**：`CreateLogicalHome` 定义在**另一个类**（`GalvoParams`）里，`LaserWeldHeadWorkflow` 只是使用者。编译器只在**同一类型内**才会把静态成员纳入名字查找。

**判据**：
```
① 收集所有 public/internal static 方法名 → 记住所属类型
② 每个调用点若前面不是 '.'，则该 static 的所有定义必须都在本文件（= 同类内互调，C# 允许）
③ 否则判为「跨类裸调 static」
```
⚠️ **判据自己踩过一次**：初版没做「同类内豁免」，把 `KukaRsiComm` 里的 `ParseRobotPacket` / `BuildReplyXml` / `GenerateRSIXML` 等**同类静态互调**全报成违规（7 处误报）。**同类内调同类静态方法完全合法** —— 加豁免后归零。

### 2. 实参必须用「作用域内真实存在」的名字（CS0103）

`FillOutput(WeldParamManager wp)` 体内我写了 `CalcGalvoAmplitude(seamWidth)` —— 但 `seamWidth` **在该方法内不存在**（宽度来自 `wp.CurrentSeamWidth`）。而**同一个文件的 `FillXlOutput(seamWidth)` 里 `seamWidth` 是真实形参** —— 两处同名不同源，改签名时看串了。

**判据**：对每个方法体（花括号配平切出）建 `局部变量/形参/字段` 集合，断言函数调用实参里的每个标识符在该集合内。
⚠️ 本项目 `MotionControl/WeldHeadSlaveDevice.cs` 一文件塞 4 个类、`DeltaMotionConfig.cs` 塞 2 个 —— **同名标识符在不同类/方法里含义不同**，必须按方法体判，不能全文搜。

### 3. 重载 + 可选参数 ⇒ 遮蔽（overload resolution trap，CS1503 参数类型不匹配）

这是最隐蔽的一种。`KukaRsiComm` 有两个重载：

```
A: BuildReplyXml(double, double, string, string)
B: BuildReplyXml(RsiPacketFormat, double, double, string, string, double = 0.0)
```

调用传 5 实参 `(double, double, string, string, double)`，期望匹配 B（末位可选）。**实际报「参数 1: 无法从 double 转换为 RsiPacketFormat」** —— 编译器先试 A，A 的前 3 参类型全对（只是少一个可选尾参）⇒ 报错说「你该给我 RsiPacketFormat」。

> ⛔ **判据：给「首选重载」新增可选参数时，必须检查其它重载不会先「部分匹配」并遮蔽它。** 可选参数**不参与**候选选择的优先级判定 —— 编译器在展开可选参数**之前**就已被 A 咬住。

**两种正确修法**：
| 修法 | 做法 | 适用 |
|---|---|---|
| **A 同步补参数**（本轮采用） | 把 A 也加上同名可选参数并转发给 B | 保持两条路径等价，调用方无感 |
| 调用方显式消歧 | 调 B 时写全 6 参，或在 A 首参位置传 `default(double)` | 不想动公开签名时 |

**防复发**：新增/修改重载后，断言「每个调用点的实参个数 ≥ 匹配重载的必填参数数」，且**重载集合中任意两个的首参类型可区分**（若两重载前 N 参类型完全相同，只是尾部可选参数不同 ⇒ 必然遮蔽）。

> ⛔ **本专题已并入 [[lessons/StaticVerifierJudgements]]**（第三章「接线完整性」/ 第四章「校验器自身的失效模式」）。本页保留为原始案例记录，**新增判据一律写进判据库对应章节**。

## 六、校验器能力的三分类（沿用并细化 rules/KR-010）

| 类别 | 例子 | 谁来判 |
|---|---|---|
| **模式化** | 命名空间、csproj 路径、禁用语法、配置四点闭环、region 配对、结构不变量、**签名-调用点实参数** | ✅ Python 静态校验可负责 |
| **语义化** | 类型系统合法性（CS8632）、名字解析（CS0103）、重载解析、装箱、泛型推断、接口实现完整性 | ⛔ 只有编译器能定 |
| **接线完整性** | 「参数加了但没被传值」「方法加了但没有消费者」「配置能读能写但无消费者」 | ⚠️ 需**专项判据**（本轮新增三类），绿灯也不代表功能通 |

> **绿灯绝不能暗示构建没问题，更不能暗示功能通。**

## 七、相关

- [[lessons/StaticCheckSemanticBlindSpots]] —— 第一批盲区（可空引用类型 / 跨类 private）
- [[lessons/CSharp-Language-Pitfalls]] —— C# 7.3 语法门禁
- [[decisions/ADR-001-CS73-Constraint]] —— 语言版本约束
- [[project/vibecoding-workflow]] —— Step 2.6 正确性验证
## 相关页面

- [[index/index]]
