---
title: ADR-025 采用代码知识图谱辅助代码审查（已废弃）
date: 2026-08-01
tags: [决策, 工具, 代码审查, CodeGraph, 图谱, MCP]
status: deprecated
---

# ADR-025：采用代码知识图谱辅助代码审查

> ## ⚠️ 废弃声明（2026-08-19）
>
> **本决策已废弃**。用户反馈 code-review-graph 实际使用体验差：执行失败频繁、耗时久、经常误判（如死代码误报、调用链不准确）。
>
> **废弃内容**：
> - vibecoding-llmwiki 工作流中 Phase 0（Step 0.7/0.8）、Phase 2（Step 2.5）、Phase 4（代码漂移）的**图谱强制集成全部移除**
> - 回归图谱引入前的**默认方式**：Grep 定位符号 + 按行号精确读取 + 人工多级调用追溯
>
> **保留**：`raw/skills/AdaWeldsys_Skills/05-Tools/CodeGraph.md`（调研文档）与 `raw/tools/crg_build.py`（包装脚本）作为历史参考，不再在工作流中使用。
>
> 工作流现行规范以 [[project/vibecoding-workflow]] 为准。

## 背景

AdaWeldSystem 当时的架构包含 6 大集成模块、5 设备状态机、1 主线程 + 5 子线程，代码间调用关系复杂。当前 vibecoding-llmwiki 工作流在 Phase 0 (Query) 依赖 Grep + 人工读取文件理解代码结构，Phase 2 (Code) 依赖 Grep 追溯引用执行编码锚点四步法，Phase 4 (Lint) 依赖人工比对 wiki/modules/ 描述与代码的一致性。

存在的问题：
1. **跨文件调用链追踪效率低**：Grep 只能做文本匹配，无法理解语义调用关系（如继承链、接口实现）
2. **变更影响分析缺失**：修改一个公共方法后，无法快速获知所有受影响的调用方
3. **编码锚点追溯依赖人工**：「定义→搜索→验证→提交」四步中「搜索」和「验证」步骤缺少自动化工具
4. **代码漂移检测主观**：Phase 4 Lint 的「代码漂移」检查项依赖人工阅读代码，容易遗漏

## 决策

引入**代码知识图谱（Code Knowledge Graph）**作为 vibecoding-llmwiki 工作流的**辅助增强工具**，在代码审查阶段提供结构化的代码关系查询能力。

### 定位：辅助而非替代

```
LLMWiki (wiki/)     ← 唯一真相源（架构决策、教训、模块边界）
Code Graph (图谱)   ← 辅助工具（调用链、影响半径、代码级关系）
```

Code Graph 补充的是 LLMWiki 无法覆盖的**代码级结构关系**（函数调用链、类继承树、导入依赖），不替代 LLMWiki 的架构级知识。

### 选型

基于调研（见 `raw/skills/AdaWeldsys_Skills/05-Tools/CodeGraph.md`），两个候选项目：

| 项目 | 定位 | 语言支持 | 部署方式 |
|------|------|---------|---------|
| code-review-graph (tirth8205) | 审查专用 | 28+ (含 C#) | 本地优先，30 MCP 工具 |
| CodeGraph (colbymchenry/codegraph) | 通用代码图谱 | 28+ (含 C#) | 100% 本地，SQLite + MCP |

**决策：固定使用 code-review-graph**（审查场景更贴合，已验证在 Windows 环境下可稳定运行）。CodeGraph 仅作为技术参考保留在调研文档中，本项目不启用。

### 三阶段集成点（固定方法）

#### Phase 0 (Query) — 强制

```
读取 LLMWiki → code-review-graph status 验证 → code-review-graph search 定位 → code-review-graph query 查调用链 → 补充代码级关系
```

- 在读取 `wiki/modules/` 后，强制执行代码图谱查询，补充 Wiki 未覆盖的函数级调用关系
- 使用 `code-review-graph` 的 `status`/`search`/`query callers_of` 命令
- 用于快速理解模块间的实际代码依赖（区别于 Wiki 描述的逻辑依赖）
- **图谱辅助代码定位读取**：用 `search` / `query file_summary` 拿到符号的 `{file_path, line_start, line_end}`，再以 `Read(offset/limit)` 精确读取代码块，避免整文件通读（Phase 0 Step 0.8）
- **Windows 执行须知**：必须先设置环境变量 `CRG_PARSE_EXECUTOR=thread`，详见 [[guides/Project-Tools]] §Windows 兼容性注意事项
- **Python 环境**：conda myenv 不在系统 PATH，所有命令必须用绝对路径 `& "D:\ProgramData\miniconda3\envs\myenv\python.exe" -m code_review_graph ...`，禁止裸 `python`（详见 [[guides/Project-Tools]] §Python 环境）

#### Phase 2 (Code) — 强制

```
修改代码 → code-review-graph impact 验证影响范围 → code-review-graph query callers_of 追溯所有引用 → 编码锚点四步追溯
```

- 修改公共方法/类后，用 `& $pythonPath -m code_review_graph impact --repo $repoPath --files` 获取变更爆炸半径
- 用 `& $pythonPath -m code_review_graph query callers_of` 替代 Grep 执行编码锚点四步法中的「搜索」步骤，精确度更高
- 回退策略：仅允许回退到 Grep，不允许切换到其他图谱工具

#### Phase 4 (Lint) — 强制

```
code-review-graph dead-code → 检测死符号
code-review-graph large-functions → 识别重构候选
```

- 用 `& $pythonPath -m code_review_graph dead-code --limit 10 --repo $repoPath` 自动检测代码变更产生的死符号
- 用 `& $pythonPath -m code_review_graph large-functions --limit 5 --repo $repoPath` 发现架构热点和潜在重构目标
- 回退策略：仅允许回退到 Grep，不允许切换到其他图谱工具

### 约束

1. **LLMWiki 优先级不变**：Code Graph 查询结果与 LLMWiki 描述冲突时，以 LLMWiki 为准
2. **不向 Wiki 沉淀图谱原始数据**：图谱查询结果是即时上下文，不写入 `wiki/` 页面（避免代码漂移导致 Wiki 过期）
3. **图谱构建是强制步骤**：按 [[guides/Project-Tools]] 已验证的 Windows 执行方法，图谱构建是 /vibeCoding 工作流的强制步骤
4. **安装前需验证环境**：Python >= 3.10，已安装 code-review-graph v2.3.7+

## 备选方案

| 方案 | 说明 | 放弃理由 |
|------|------|---------|
| 维持 Grep + 人工审查 | 不引入新工具 | 跨文件调用链追踪效率低，影响分析缺失，编码锚点追溯依赖人工 |
| 向量 RAG（语义检索） | 用嵌入向量找语义相似代码 | 无法回答「谁调用了这个函数」的结构性问题，Token 效率低于图查询 |
| 自研代码解析工具 | 基于 Roslyn 分析 C# 代码 | 开发成本高，且 tree-sitter 已原生支持 C# 解析 |

## 后果

### 正面
- 代码审查阶段获得结构化的调用链、影响半径、架构热点信息
- 编码锚点四步法的「搜索」和「验证」步骤可自动化
- Phase 4 Lint 的「代码漂移」检查项获得自动化工具支持
- 补充 LLMWiki 无法覆盖的代码级关系（函数调用、类继承、导入依赖）
- **图谱辅助代码定位读取**：`search` / `file_summary` 提供符号的精确行号区间，驱动 `Read(offset/limit)` 精确读取，显著缩小代码读取范围（Phase 0 Step 0.8）

### 负面 / 待办
- 需安装并验证 code-review-graph 或 CodeGraph 工具链
- 图谱构建需在代码变更后增量更新，需纳入 CI/CD 或手动触发流程
- 当前项目 ~100+ .cs 文件，图谱收益在 200+ 文件后更显著
- 团队需学习 MCP 工具查询语法

## 相关页面

- `raw/skills/AdaWeldsys_Skills/05-Tools/CodeGraph.md` — 代码知识图谱参考文档（历史调研，不再使用）
- [[project/vibecoding-workflow]] — VibeCoding 工作流（当前规范，已回归 Grep 默认方式）
- [[guides/Project-Tools]] — 项目工具指南（§1 代码图谱已标记为历史参考）

---

*来源：2026-08-01 网上调研 + raw/skills/AdaWeldsys_Skills/05-Tools/CodeGraph.md | 2026-08-19 用户废弃（失败频繁/耗时久/误判多），回归 Grep 默认方式*
