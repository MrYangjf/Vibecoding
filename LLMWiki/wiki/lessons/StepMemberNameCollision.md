---
title: 步号常量与单步方法同名导致 CS0102（含跨文件样板下沉与脚本误报两则）
date: 2026-09-01
tags: [教训, 步骤驱动, CSharp, 编译, ADR-028, DeviceWorkflowBase, 命名]
---

# 步号常量与单步方法同名 → CS0102

> 来源：2026-09-01 步骤驱动改造**落地后的第二轮精简审查**。
> 上一轮改造把 8 个 workflow 全部改成「常量步号 + 同名单步方法」的写法，本轮审查才发现这套写法**根本编译不过**。
> 规范正文见 [[architecture/DeviceControlArchitecture]] §5（⛔ 旧标准 [[standards/StepDrivenWorkflow]] 已废弃），本页只记踩坑与规避动作。
>
> **类名与规模注记（2026-09-02，ADR-034）**：文中「8 个 workflow」现为 **7 个**——5 个子设备工作流（`LineLaser`/`MonitorCamera`/`MotionControl`/`WeldParamControl`/`LaserWeldHead`）+ `DeviceControlWork` + `DeviceStatusWork`；`SafetyWorkflow` 现为 `DeviceStatusWork`（其 `StepAlarm = 900` 与 `DoAlarm()` 已随三线程模型移除）；`MainDeviceWorkflow` 现为 `DeviceControlWork`。**CS0102 同名冲突的规避动作继续有效**。
>
> **🔥 2026-09-03 新增实战案例（裁定 C6，改码前必看）**：按新原档把 `WorkStep` 改名为基类属性 **`RunStep`** 时，
> `LineLaserWorkflow.cs` 中**已存在** `private bool RunStep(Func<bool>, string, string)` 方法 → 新增属性 `RunStep` 直接触发
> **CS0102（同类成员重名）**。这是本页坑一的同型案例，**批次 1 改码第一步必须先给该方法改名**（建议 `RunStepGuard` / `ExecuteStep`），
> 否则全项目编译失败。同理 `StepWorkTime` / `TimeOutSeconds` 落地前也要先在 5 个子类里 grep 同名成员。
> 现行规范见 [[architecture/DeviceControlArchitecture]] §4.1、§16.3。

---

## 坑一：`const int StepXxx` 与 `void StepXxx()` 同一作用域 → CS0102

### 现象

按直觉给每一步写一对「常量 + 方法」，二者同名：

```csharp
private const int StepPreWork = 10;

private void StepPreWork()      // CS0102：类型已包含同名成员定义
{
    ...
}
```

C# 的常量、字段、方法、属性、事件**共享同一个成员命名空间**，不存在「常量名与方法名互不干扰」这回事。

### 影响面

本次实测：6 个 workflow 共 **27 处**同名冲突（`LineLaser` 9 / `MotionControl` 7 / `MonitorCamera` 5 / `WeldParamControl` 4 / `SafetyWorkflow` 2）。
**整个 `MainDeviceControl` 改造后处于无法编译状态**——而改造当时只做了 Grep 与人工核对，没人编译（本项目在本环境无法编译，见 [[guides/Namespace-Compilation]]）。

### 根因

命名时把「步号（数据）」与「动作（行为）」当成了两个维度，实际 C# 只认一个成员表。

### 规避（硬约束）

**步号常量 `StepXxx`，单步方法 `DoXxx()`，分派处 `case StepXxx: DoXxx(); break;`**

选 Do 前缀而非改常量名（Ws 前缀）或嵌套 `Steps` 静态类的原因：

| 方案 | 改动面 | 取舍 |
|---|---|---|
| **方法加 `Do` 前缀** | 只碰 `private` 方法名，无外部依赖 | ✅ 采纳 |
| 常量改 `Ws` 前缀 | 常量在 `case`/`GoStep`/`GetStepName` 三处出现，改动面×3 | 放弃 |
| 嵌套 `static class Steps` | 每个引用点都要加 `Steps.` 前缀，且段位表可读性下降 | 放弃 |

### 检索自检命令

改完必须跑（去注释后比对常量名与方法名）：

```bash
python - << 'EOF'
import io, re, glob
for p in glob.glob("MainDeviceControl/**/*.cs", recursive=True):
    code = re.sub(r'//[^\n]*', '', io.open(p, encoding="utf-8-sig").read())
    consts = set(re.findall(r'\bconst\s+int\s+(\w+)\s*=', code))
    methods = set(re.findall(r'\b(?:void|bool|int|string|double|DeviceState)\s+(\w+)\s*\(', code))
    if consts & methods:
        print(p, sorted(consts & methods))
EOF
```

---

## 坑二：下沉 `protected const` 后，子类残留同名定义 → CS0108

### 现象

把 8 个流程各抄一份的 `StepIdle=0` / `StepFinishOk=800` / `StepFinishFail=900` 下沉到基类后，若忘记删子类里的旧定义：

```csharp
// 基类
protected const int StepFinishFail = 900;

// 子类残留
private const int StepFinishFail = 900;   // CS0108 警告：隐藏继承成员
```

### 规避

下沉后**必须**全目录扫一遍重复定义：

```bash
grep -rn "StepFinishFail\s*=\|StepFinishOk\s*=\|StepIdle\s*=" AdaWeldSystem/MainDeviceControl
```

预期输出**只剩基类的 3 行**。子类里出现即未清理干净。

同理，`_failReason` / `_failStep` 字段与 `FailFlow()` 方法在 5 个文件各有一份实现，一并下沉基类后，子类改读基类的 `FailReason` / `FailStep` 只读属性。

### 语义合并注意

`SafetyWorkflow` 原本有自己的 `StepAlarm = 900`。安全流程没有 800 成功段，报警收尾与失败收尾语义重合，**直接并入基类 `StepFinishFail`**，方法名保留领域语义 `DoAlarm()`。
→ 教训：**下沉常量时要检查「同值不同名」的常量，它们往往是同一语义的两套叫法。**

---

## 坑三：反向问题——`DeviceControlWork`（原 `MainDeviceWorkflow`）一个常量都没有

与其余 6 个流程相反，主设备流程改造后**0 个步号常量**，`GoStep(10)` / `case 800:` 全是魔法数字。

**教训**：审查不能只盯「报错的那类问题」。同名冲突是硬错误、会报警，而魔法数字不报错、只能靠人工比对发现。
→ 落地后应对**整组文件做横向一致性检查**（有没有常量、常量命名是否统一、`case` 是否写常量），而不只是跑一遍报错扫描。

---

## 坑四：`csharp_review.py` 把形参表与对象初始化器误判成字段

### 现象

成员顺序检查报出「字段 private string message, MessageLevel level 出现在更高顺序区域之后」，但该文件成员顺序其实完全正确。

### 根因

`FIELD_RE` 依赖「修饰符 + 类型 + 名称 + `;`」匹配，两类非字段文本被误吃：

1. 方法形参表 `private void Log(string message, MessageLevel level = MessageLevel.Info)` → 伪字段「`private string message, MessageLevel level`」
2. 属性体内的对象初始化器 `new MonitorResult { Phase = _result.Phase, ... }` → 伪字段「`private _result.Phase, Pass`」

伪字段访问级 `private`（顺序 1）落在方法（顺序 4/5）之后，于是假报「顺序破缺」。

### 规避

已在 `scripts/csharp_review.py` 新增 `_drop_pseudo_fields()`：凡落在任一方法或属性行区间内的「字段」一律剔除（C# 不允许在方法体/属性体内声明字段，此过滤无副作用）。

→ **通用教训**：lint 报「成员顺序错误」时，先确认报错的那个「字段」在源文件里真的存在；名字里带 `,` `.` 或空格的，基本都是解析器误读。

---

## 坑五：批量移动多行属性时，块边界识别不全 → 文件结构被拆散

### 现象

写脚本把 `IsRunLoopActive` 属性从尾部 region 移到「公共变量」区，单行表达式体（`{ get { return _running; } }`）搬对了，多行体（`{ get { ... } }` 换行展开）**只搬走了签名行**，`{ get {...} }` 被留在原 region，文件结构直接损坏。

### 根因

判定块结束的 brace 计数从签名行起算，而多行体的签名行本身不含 `{`，计数为 0 立即判定「块已结束」。

### 规避

1. 签名行无 `{` 时，**先向下推进到含 `{` 的行再开始计数**。
2. 批量移动成员后，**必须立刻 `sed -n` 抽查首尾两处**，确认没有产生孤立的 `{ ... }` 残块。
3. 更稳的做法：批量改动前先 `tar.gz` 备份，出问题直接回滚重做——比就地修补更省时间。

---

## 关联

- 规范：[[architecture/DeviceControlArchitecture]] §5 · [[lessons/StepMemberNameCollision]]
- 教训：[[lessons/StepDrivenWorkflowPitfalls]]（上一轮改造五坑）
- 精简：[[standards/CodeSimplification]]
- 模块：[[modules/DeviceControl]]
- 决策：见 [[architecture/DeviceControlArchitecture]]
