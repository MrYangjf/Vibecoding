---
title: Rules-Index — Skill 流程执行强制规则编号唯一准绳
date: 2026-10-30
updated: 2026-11-02
tags: [索引, 规则, Skill执行, 编号体系, 知识库治理]
status: accepted
---

# Rules-Index — Skill 流程执行强制规则编号唯一准绳

> **本类目 = Skill 执行工作流时必须遵守的强制规则**（原 Skill 里的「Key Rules」下沉后的落地处，2026-10-30 建；2026-11-02 收敛为纯流程类）。
> **收敛后的边界**：本类目只收**流程执行类**规则 —— 规定「AI 在跑这个工作流时该怎么做」；**约束代码 / 知识库内容本身**的规则一律归 lessons 坑页（index 第五节，见 [[lessons/WikiDriftCorrectionPitfalls]]）与 [[standards/WikiPageFormatSpec]]（格式规范）、决策类归 [[decisions/ADR-Index]]。
> **为什么这样分**：两类规则的**失效后果不同** —— 流程类失效 = 工作流跑偏（漏查、跳步、谎报）；内容类失效 = 写错代码 / 知识库漂移。把内容类塞进流程类清单，会让「查规则」变成「查技术判据」，检索路径混淆。

---

## 一、编号规则

- **现行编号：`KR-001 ~ KR-013` 连续无空洞**；新号 = 本表 `max+1` = **014**。
- ⛔ **废止不回收编号**（与 ADR 同规则）；重编号须同批回写全库引用。
- **一个主题一条规则** → 一页 `wiki/rules/KR-NNN-{Slug}.md`。
- **同主题的补充 / 演进 → 合并进既有页**（追加「## 演进记录」），**不新建页**（见 [[standards/WikiPageFormatSpec]] §三）。
- 本表是规则编号的**唯一权威**。

---

## 二、页面格式契约（固定结构）

```
--- (title 含 KR-NNN / date / updated / status / tags) ---
# KR-NNN <标题>

> **一句话规则**（≤120 字符，读者只看这行就能遵守）

## 适用范围        ← 何时必须遵守 / 何时不适用（新增，必填）
## 规则正文        ← 编号条目（每条 ≤200 字符；⛔ 禁止整段散文）
## 判据            ← 可机械检查的判定句 + 校验命令（≤8 行）
## 反例            ← 违规写法 → 正解（表格，≤4 行）
## 相关页面        ← [[...]]，必须回链 [[rules/Rules-Index]]
```

**硬约束**：
- ⛔ 单页 **≤150 行**；⛔ 规则条目**每条 ≤200 字符**（禁止整段叙述）。
- ⛔ 规则正文**不得**含验证叙事（静态 N/N · 阴性对照 · 探针实测）→ 属 log。
- ⛔ 规则正文**不得**含技术细节（代码写法、脚本陷阱、行尾 / 编码判据）→ 属 lessons 坑页（见 [[lessons/WikiDriftCorrectionPitfalls]]）。
- ⛔ **Skill 里不得维护规则清单** —— 规则正文只在本类目，Skill 只写「去哪查」。

---

## 三、路由机制（AI 如何找到规则）

| 场景 | 走哪条路 |
|---|---|
| 读 index 找规则 | `wiki/index/index.md` **第十二节「流程规则」**（本类目的页面表） |
| 按主题定位规则 | 本表「## 四、规则清单」的**主题列** |
| 编码前的规则门禁 | [[project/vibecoding-workflow]] 各 Phase 的「规则门禁」小节 → 指回本类目 |
| 要技术判据（代码 / 脚本 / 行尾 / 编码） | **不查本类目** → 走 lessons 坑页（index 第五节） |
| 要页面格式规范 | [[standards/WikiPageFormatSpec]] |
| 要决策理由 | [[decisions/ADR-Index]] |
| 机器校验 | `python tools/rules_check.py`（结构 + 编号连续 + 索引一致 + 判据非空） |

---

## 四、规则清单（13 条 · 流程执行类）

| 编号 | 主题 | 规则要点 | 页面 |
|---|---|---|---|
| KR-001 | 强制执行顺序 | 读工作流规范 → 读 AGENTS.md → 执行 Phase 0~4 | [[rules/KR-001-Execution-Order]] |
| KR-002 | 步骤级展示 | 每个 Step 必须显式展示编号+名称+输出；禁止合并成 Phase 摘要 | [[rules/KR-002-Step-Level-Display]] |
| KR-003 | 不得跳过 Query | 编码前必须完成 Phase 0 检索；先查代码地图 | [[rules/KR-003-No-Skipping-Query]] |
| KR-004 | Skill 降级为参考 | 指令权威在 wiki；Skill 与 wiki 冲突时 wiki 优先 | [[rules/KR-004-Skill-Demoted]] |
| KR-005 | ADR 与教训是编码前门禁 | ADR=编码前必查的硬约束；教训=编码前必过的门禁 | [[rules/KR-005-Adr-Lessons-Gates]] |
| KR-006 | Ingest 强制 | 编码不做知识沉淀即视为未完成 | [[rules/KR-006-Ingest-Mandatory]] |
| KR-007 | 新决策必须记录 | 涉及新架构选择 → 必须建 ADR（先合并后新建） | [[rules/KR-007-New-Decisions-Recorded]] |
| KR-008 | 时间戳取用 | 时间戳由脚本取，禁止估算 | [[rules/KR-008-Timestamp-Rule]] |
| KR-009 | Grep 是默认定位法 | code-graph 已废止；用 Grep 定位与影响面追踪 | [[rules/KR-009-Grep-Default]] |
| KR-010 | 无编译器要声明 | 不得把静态检查说成「构建通过」；能力分三类 | [[rules/KR-010-No-Compiler-Honesty]] |
| KR-011 | backup 与 output 时机不可互换 | backup 在改码前、output 在定稿后 | [[rules/KR-011-Backup-Output-Timing]] |
| KR-012 | Skill 双副本同步 | 同步前探行尾；仓库版规范化为 LF；报告 numstat | [[rules/KR-012-Skill-Dual-Copy]] |
| KR-013 | Skill 指向不得写死内容页 | Skill 只写角色级锚点与机制表述 | [[rules/KR-013-Skill-Pointer-Discipline]] |

---

## 五、已下沉条目去向表（2026-11-02 收敛）

> 原 29 条 Key Rules 中的 **16 条内容类规则**已下沉到 lessons 坑页（index 第五节）/ [[standards/WikiPageFormatSpec]] / [[decisions/ADR-Index]]，**rules 页已删除**；下表保留去向以便追溯。

| 原编号 | 主题 | 现权威位置 |
|---|---|---|
| KR-008（旧） | csproj 注册 | [[lessons/StaticVerifier-Batch-Script-Traps]] §七 |
| KR-010（旧） | 零消费 ≠ 死成员 | [[lessons/StaticVerifier-Wiring-Integrity]] §四 |
| KR-011（旧） | Wiki 页保持 LF | [[lessons/WikiDriftCorrectionPitfalls]] 坑一 |
| KR-012（旧） | 换行不可吞 | [[lessons/WikiDriftCorrectionPitfalls]] 坑二 |
| KR-013（旧） | 退役旧指引三档 | [[lessons/WikiGovernanceBatchingPitfalls]] |
| KR-014（旧） | 批量替换前查自引用 | [[lessons/WikiDriftCorrectionPitfalls]] 坑三 |
| KR-015（旧） | blockquote 须用固定串 | [[lessons/WikiDriftCorrectionPitfalls]] 坑十一 |
| KR-016（旧） | 同文件禁止并发 Edit | [[lessons/StaticVerifier-Batch-Script-Traps]] §八 |
| KR-017（旧） | ADR 号不复用 | [[lessons/StaticVerifier-AdrNumbering]] §8.3 + [[decisions/ADR-Index]] |
| KR-018（旧） | 批量改写两阶段 | [[lessons/StaticVerifier-Batch-Script-Traps]] §四之十四 |
| KR-019（旧） | 全库普查先于定向清扫 | [[lessons/WikiDriftCorrectionPitfalls]] 坑八 |
| KR-020（旧） | wiki 下只放 Markdown | [[lessons/WikiDriftCorrectionPitfalls]] 坑八 |
| KR-021（旧） | 跨会话残留要有指纹证据 | [[lessons/SimulationAutoBranching]] 陷阱二十 |
| KR-022（旧） | 锚点形态二分诊断 | [[lessons/StaticVerifier-Batch-Script-Traps]] §四之十四 |
| KR-024（旧） | 整文件 diff 归属判定 | [[lessons/WikiDriftCorrectionPitfalls]] 收尾判据 |
| KR-026（旧） | 页面格式契约 | [[standards/WikiPageFormatSpec]] §二 / §三 |

---

## 六、维护方式（脚本化）

```bash
python tools/rules_check.py                        # 校验：编号连续 / 结构契约 / 索引一致 / 判据非空
python tools/rules_new.py check <关键词>           # 合并检查（先合并后新建）
python tools/rules_new.py merge KR-NNN "主题" "变更" "理由" "影响"   # 追加演进记录
python tools/rules_new.py new <slug> <标题> "一句话规则" "正文" "判据"   # 新建（先过 check）
```

⛔ 规则正文**只在本类目维护**；⛔ SKILL.md 只保留**怎么用**（见 [[rules/KR-013-Skill-Pointer-Discipline]]）。

---

## 相关页面

- [[standards/WikiPageFormatSpec]] —— 页面格式契约（规则页本身也受其约束）
- [[project/vibecoding-workflow]] —— Phase 0~4 流程规范
- [[decisions/ADR-Index]] —— ADR 编号唯一准绳（规则页的孪生结构）
- [[lessons/WikiGovernanceBatchingPitfalls]] —— 本轮治理的事故清单
