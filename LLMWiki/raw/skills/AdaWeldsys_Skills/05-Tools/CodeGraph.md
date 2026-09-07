# Code Graph — 代码知识图谱参考文档

> **定位**：本文件是参考资料，不是指令源。AI 编码时参考此文档理解 code graph 技术，
> 实际编码决策以 LLMWiki `wiki/` 内容为准（见 `decisions/ADR-023-CodeGraphForCodeReview`）。
>
> **重要**：本项目**固定使用 code-review-graph** 作为唯一代码图谱工具。CodeGraph (colbymchenry/codegraph) 仅作为技术竞品保留在此参考文档中，不启用、不降级、不路由。
>
> 来源：2026-08-01 网上调研，基于 CodeGraph (colbymchenry/codegraph) 和 code-review-graph (tirth8205/code-review-graph) 两个开源项目。

---

## 1. 核心概念

**代码知识图谱（Code Knowledge Graph）** 是一种将整个代码库解析为可查询图结构的技术方案：

- **节点（Nodes）**：函数、类、方法、变量、导入
- **边（Edges）**：调用关系、继承链、导入依赖、包含关系、测试覆盖
- **存储**：SQLite（嵌入式，零配置，100% 本地）
- **暴露**：通过 MCP（Model Context Protocol）协议向 AI Agent 提供查询接口

与向量 RAG 的本质区别：向量检索找「语义相似」，图谱检索找「结构关联」。

| 维度 | 向量 RAG | 图 RAG (Code Graph) |
|------|---------|---------------------|
| 检索依据 | 语义相似度 | 结构依赖关系 |
| 能回答的问题 | 「这段代码和什么长得像」 | 「这个函数被谁调用/调用了谁」 |
| 跨文件追踪 | 不支持 | 原生支持 |
| 影响分析 | 不支持 | 原生支持（Blast Radius） |
| Token 效率 | 低（需传大量候选片段） | 高（精确定位相关节点） |

## 2. 主流开源项目

### 2.1 CodeGraph (colbymchenry/codegraph)

- **GitHub**: https://github.com/colbymchenry/codegraph
- **Stars**: 20,000+（2026-07）
- **定位**: Pre-indexed code knowledge graph for Claude Code, Codex, Cursor, and OpenCode
- **语言支持**: 28+ 语言（含 C#）
- **部署**: 100% 本地，零配置

**四层架构**:

```
源码文件
  │
  ▼
tree-sitter 解析（增量解析，容错性强）→ AST
  │
  ▼
符号 · 边提取（函数/类/方法 + 调用/继承/引用/路由）
  │
  ▼
SQLite + FTS5 图谱存储（全文搜索 + 关系图）
  │
  ▼
MCP Server（暴露给 Claude Code/Cursor/Codex CLI）
```

**性能数据**（7 个真实开源项目，Claude Opus 4.7 + Claude Code v2.1.91）:

| 指标 | 平均提升 |
|------|---------|
| Token 消耗 | 减少 59% |
| 工具调用次数 | 减少 71% |
| 速度 | 提升 46% |

| 项目 | 文件数 | 无 CodeGraph | 有 CodeGraph | 工具调用减少 |
|------|--------|-------------|-------------|-------------|
| Excalidraw (TS) | ~600 | 47 次, 1m45s | 3 次, 29s | 94% |
| VS Code (TS) | ~4,000 | 52 次, 1m37s | 3 次, 17s | 94% |
| Claude Code (Java) | ~800 | 26 次, 1m22s | 1 次, 19s | 96% |

**关键特性**:
- 增量更新：文件保存后 2 秒自动同步索引
- 递归 CTE 图遍历：SQL 一行实现 N 层调用链追踪
- 框架路由识别：支持 13 个框架（含 ASP.NET）
- 混合检索：图结构 + 向量语义，7:3 权重融合

### 2.2 code-review-graph (tirth8205/code-review-graph)

- **GitHub**: https://github.com/tirth8205/code-review-graph
- **Stars**: 19,800+（2026-07）
- **定位**: 本地优先的代码智能图谱引擎，专注代码审查
- **语言支持**: 28+ 语言（含 C#）
- **License**: MIT

**核心能力**:
- **30 个 MCP 工具**：get_minimal_context、get_impact_radius、query_graph、traverse_graph、semantic_search、get_hub_nodes、get_bridge_nodes、detect_changes、refactor 等
- **影响半径分析（Blast Radius）**：变更文件时沿调用链反向追踪，AI 只读取影响范围内的文件
- **增量更新**：2900 文件项目 < 2 秒
- **Token 效率**：中位数降低 82 倍

**基准测试**（6 个开源仓库，13 次提交）:

| 仓库 | 全量 Token | 图查询 Token | 降低倍数 |
|------|-----------|-------------|---------|
| fastapi | 951,071 | 2,169 | 528.4x |

## 3. 技术架构详解

### 3.1 解析层：tree-sitter

tree-sitter 是纯 C 实现的增量解析库:
- 文件修改后只重建受影响的部分子树
- 代码写到一半（语法不完整）也能给出有意义的 AST
- 解析速度支持每次按键时运行
- 原生支持 C#（AdaWeldSystem 项目可直接使用）

### 3.2 存储层：SQLite

图结构通过两张核心表表达:

```sql
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,       -- function / class / method / variable
    file_path TEXT NOT NULL,
    line INTEGER NOT NULL,
    source_code TEXT          -- 代码片段
);

CREATE TABLE edges (
    source_id INTEGER REFERENCES nodes(id),
    target_id INTEGER REFERENCES nodes(id),
    kind TEXT NOT NULL,       -- calls / inherits_from / contains / depends_on
    file_path TEXT NOT NULL   -- 冗余字段，避免每次 join nodes 表
);
```

### 3.3 查询层：递归 CTE 图遍历

从 `login()` 出发 3 层调用链:

```sql
WITH RECURSIVE call_chain AS (
    SELECT n.id, n.name, n.kind, 0 AS depth
    FROM nodes n WHERE n.name = 'login'
    UNION ALL
    SELECT n.id, n.name, n.kind, c.depth + 1
    FROM call_chain c
    JOIN edges e ON c.id = e.source_id AND e.kind = 'calls'
    JOIN nodes n ON e.target_id = n.id
    WHERE c.depth < 3
)
SELECT DISTINCT * FROM call_chain ORDER BY depth, name;
```

### 3.4 接口层：MCP Protocol

AI Agent 通过 MCP 工具按需查询图谱:

| 工具 | 用途 | Token 消耗 |
|------|------|-----------|
| get_minimal_context | 超紧凑上下文 | ~100 tokens |
| get_impact_radius | 变更影响半径 | 精确到相关文件 |
| query_graph | 查调用者/被调用者/继承 | 按需 |
| traverse_graph | BFS/DFS 遍历（可设 token 预算） | 可控 |
| semantic_search | 语义搜索代码实体 | 混合检索 |

## 4. 适用场景

### 4.1 代码审查（Blast Radius 分析）

```
审查员："这次变更的爆炸半径有多大？"
系统 3 秒返回：
  直接影响：3 个函数（src/auth/login.cs, src/auth/session.cs, src/auth/token.cs）
  间接影响：2 个模块（订单模块的权限校验、支付模块的用户验证）
  风险等级：中（支付模块可能受影响，建议补集成测试）
```

### 4.2 编码锚点追溯（定义→搜索→验证→提交）

利用 code graph 的调用链追踪:
1. **定义**：新增/修改/删除类、函数、变量时，graph 中新增/更新对应节点
2. **搜索**：`query_graph` 查询所有引用该符号的文件
3. **验证**：`get_impact_radius` 确认变更影响范围
4. **提交**：确认无遗漏引用

### 4.3 新人入职 / 代码理解

- 自然语言查询调用流程，5 分钟获取完整调用链
- 系统化知识图谱永久留存，不依赖人脑记忆
- 图谱可视化展示模块间依赖关系

## 5. 在 AdaWeldSystem 中的应用建议

### 5.1 适用性评估

| 维度 | 评估 |
|------|------|
| 语言 | C# (.NET 4.8) — tree-sitter 原生支持 ✅ |
| 项目规模 | ~100+ .cs 文件 — 中型项目，200+ 文件收益陡增 ⚠️ |
| 架构复杂度 | V2 六大模块 + 五状态机 + 线程模型 — 结构关系复杂，图查价值高 ✅ |
| 编码锚点追溯 | 当前依赖 Grep + 人工检查 — code graph 可自动化 ✅ |

### 5.2 推荐使用方式

**Phase 0 (Query) 增强**:
- 在读取 LLMWiki 后，可选执行 `codegraph index` 构建代码图谱
- 用 `query_graph` 查询涉及模块的调用链，补充 Wiki 未覆盖的代码级关系

**Phase 2 (Code) 增强**:
- 修改代码后用 `get_impact_radius` 验证变更影响范围
- 用 `query_graph` 追溯所有引用，执行编码锚点四步追溯

**Phase 4 (Lint) 增强**:
- 用 `codegraph diff` 检测代码与 Wiki 描述的漂移
- 用 `get_hub_nodes` 发现架构热点（连接最多的节点）
- 用 `get_bridge_nodes` 发现架构瓶颈（介数中心性最高的节点）

### 5.3 安装方式

```bash
# 方式一：CodeGraph（通用型，本项目不启用，仅作技术参考）
npx codegraph index

# 方式二：code-review-graph（审查专用，本项目固定使用）
pip install code-review-graph
python -m code_review_graph build --repo AdaWeldSystem
```

> 注意：本项目**固定使用 code-review-graph v2.3.7+** 作为唯一图谱工具。v2.3.7 起 `--path` 改为 `--repo`，`index` 子命令改为 `build`。CodeGraph 仅作技术参考，不启用。

## 6. 参考文献

1. Colby McHenry, "CodeGraph: Pre-indexed Code Knowledge Graph for AI Agents," GitHub, 2026-05. https://github.com/colbymchenry/codegraph
2. tirth8205, "code-review-graph: Local-first code intelligence graph engine," GitHub, 2026. https://github.com/tirth8205/code-review-graph
3. Yamaguchi et al., "Modeling and Discovering Vulnerabilities with Code Property Graphs," IEEE S&P 2014. https://ieeexplore.ieee.org/document/6956589
4. Google, "AI Code Review Engineers Guide," 2025-05. https://developers.google.com/engineering-practices
5. 蚂蚁集团 CodeFuse 团队, "Code Graph Model (CGM)," NeurIPS 2025. https://arxiv.org/abs/2505.16901

---

*最后更新：2026-08-01*
