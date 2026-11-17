---
title: KR-010 编译结论必须以真编译为准
date: 2026-10-30
updated: 2026-11-09
tags: [规则, 流程, Skill执行]
status: accepted
---

# KR-010 编译结论必须以真编译为准

> **一句话规则**：本机**有** C# 编译器（VS18 BuildTools + dotnet 11）；「编译通过」必须来自 `MSBuild /t:Rebuild` 的真实退出码 0，静态检查不得替代，也不得冒充。

## 适用范围

**适用**：所有涉及 C# 编译 / 构建结论的阶段（Phase 2.6 验证与 Phase 4 报告）。  
**不适用**：Python / 脚本类工具的运行结果。

## 规则正文

1. 本机**具备**真编译能力，已多次实测通过：`C:\Program Files\Microsoft Visual Studio\18\Insiders\MSBuild\Current\Bin\MSBuild.exe`（及 `Program Files (x86)\...\18\BuildTools` 备选），并有 `dotnet 11` 提供 `dotnet format` 语法门禁。⛔ 不得再以「本机无编译器」为由跳过真编译。
2. 编译结论的唯一判据：`MSBuild <csproj> /t:Rebuild /p:Configuration=Debug /p:Platform=AnyCPU` **退出码 0 且错误数 0**；`bin\Debug\AdaWeldSystem.exe` 时间戳刷新。⛔ 禁止把静态检查说成「构建通过」。
3. 静态校验（`simplify_guard.py` / `csharp_review.py`）只能覆盖**模式型**缺陷（括号/标签/成员多重集/行尾/结构位置）；**语义型**（类型系统、重载、装箱、名称解析、泛型推断、接口完整性）与**接线型**（参数加了没传、方法加了没调用方）只能由真编译 + 专项判据发现。
4. 真编译 0 error 也不证明功能可用；仍须列出语义型残余风险与接线缺口。

## 判据

- ⛔ 违反判定：报告出现「编译通过 / 构建成功」而实际未编译；或以「本机无编译器」为由跳过编译门禁。
- ✅ 机器校验：`simplify_run.py` 第 4 关输出 `build: errors=0 rc=0`；报告注明 MSBuild 路径与退出码。

## 反例

| 反例（违规写法） | 正解 |
|---|---|
| 「本机没有编译器，静态检查全过就算构建通过」 | 跑 `simplify_run.py --build-only`，贴 `errors=0 rc=0` |
| 「静态守卫全绿，所以没问题」 | 守卫只证明结构守恒；语义/接线仍须真编译与专项判据 |
| 「已验证，功能没问题」 | 列出语义型残余风险与接线缺口 |

## 更正记录（2026-11-09）

**被更正的旧条文**：「本机 `dotnet` / `msbuild` / C# 编译器被安全策略拦截且无 Visual Studio：⛔ 不要浪费轮次找编译器。」

- **存在时长**：2026-10-30 至 2026-11-09，共 **10 天**（`updated: 2026-11-02` 一次改版未触及该句）。
- **错误性质**：与事实不符——本机既有 `dotnet 11`，也有 VS18 BuildTools/Insiders MSBuild，且本轮及 2026-11-02、2026-11-09 多次真编译成功（`errors=0 rc=0`）。
- **影响过的判断**：
  1. 2026-10-30 至 2026-11-02 期间的「精简/修复」轮，编译门禁被整段跳过，仅以静态守卫放行；期间若有语义型/接线型缺陷，**无任何环节能发现**。
  2. 若干轮报告使用了「静态检查全过 → 视为通过」的表述，等同于用模式型检查冒充编译结论。
  3. `simplify_run.py` 的 `BUILD SKIP` 分支曾被当作常规路径使用，掩盖了「本机其实能编译」的事实。
- **纠正动作**：条文改写为「必须真编译」；`simplify_run.py` 的 MSBuild 候选路径保留 Insiders 与 BuildTools 两套，任一存在即执行；本轮起 `build: errors=0 rc=0` 为收尾必贴证据。

## 相关页面

- [[lessons/StaticVerifier-Checker-FailureModes]]
- [[lessons/StaticCheckSemanticBlindSpots]]
- [[rules/Rules-Index]]
