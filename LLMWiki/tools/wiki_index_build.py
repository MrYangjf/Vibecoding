#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_index_build.py —— 从 wiki/ 目录【重建】index.md 骨架与各分类表（脚本化，杜绝手工维护）

设计（对应 wiki/standards/WikiPageFormatSpec.md §2.1）：
  · index.md 只做路由，不承载详情
  · 每类一张表：页面链接 / 一句话摘要（≤120 字符）/ 标签
  · 摘要来源 = 各页 frontmatter 的 title（缺则取 H1，再缺则取首个 blockquote 一句话）
  · ADR 全量表唯一权威在 wiki/decisions/ADR-Index.md —— index.md 只放指针
  · 分类明细过长时下沉到 wiki/index/<类别>.md
  · §一「项目总览」与 §八「历史归档」对 project/ 页**互斥归属**（详见 ARCHIVE_HINT）

子命令：
  build   重建 index.md（默认）
  --dry   只输出统计与摘要预览，不写盘
退出码：0 成功；1 失败。
"""
import os
import re
import sys
import collections

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
WIKI = os.path.join(LLMWIKI, "wiki")
IDX_DIR = os.path.join(WIKI, "index")
IDX = os.path.join(IDX_DIR, "index.md")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 分类 → (章节标题, 章节说明, 目录序号)
CATS = [
    ("project", "一、项目总览", "概览 / 架构 / 工作流规范", 1),
    ("modules", "二、模块详解", "模块边界与协作", 2),
    ("api", "三、API 参考", "公共契约（调用前查）", 3),
    ("standards", "四、规范标准", "强制遵守（违反即不合格）", 4),
    ("lessons", "五、历史教训", "编码前门禁（逐条规避）", 5),
    ("guides", "六、操作指导", "怎么做（查阅型）", 6),
]

# ---------- §一 / §八 对 project/ 页的互斥归属 ----------
# 成因（2026-11-03 修）：project/ 页曾被「§一 项目总览」全量渲染 + 「§八 历史归档」
#   排除 MAIN_PROJECT 后再渲染一次 ⇒ 台账/过程类页面在两节各列一次（wiki_audit §3 报重复）。
# 规则（互斥、完备）：project/ 下每个 .md **恰好**出现在 §一 与 §八 之一。
#   §一 = 现行有效的主线页（概览 / 架构 / 工作流规范 / Skill 体系演进）
#   §八 = 台账 / 过程 / 审计 / 进度快照类（只追溯，不作编码约束）
# 新增 project 页默认落 §一；若属台账/过程类，须显式加入本清单，否则生成期自检会拦下。
ARCHIVE_PROJECT = {
    "AdrConsistencyAudit-20261008.md",      # ADR 一致性审计报告
    "CodeSimplification-Backlog-20261026.md",  # 代码精简待办台账
    "CodeSimplification-Progress-20260826.md",  # 代码精简进度快照
    "RequirementsCoverage.md",              # 需求覆盖与实现状态表
    "ReviewOptimization-P1-StructureDesign.md",  # 第一次评审优化过程产物（五份）
}



def read(p):
    b = open(p, "rb").read()
    bom = b[:3] == b"\xef\xbb\xbf"
    body = b[3:] if bom else b
    crlf = body.count(b"\r\n")
    lf = body.count(b"\n") - crlf
    return body.decode("utf-8", errors="replace").replace("\r\n", "\n"), bom, ("\r\n" if crlf > lf else "\n")


def summary_of(path):
    """取一句话摘要：frontmatter title → H1 → 首句 blockquote
    剥离日期串（摘要列不得含日期，日期只属 log / ADR-Index）
    ⚠️ BOM 陷阱：带 BOM 的文件首行是 '\\ufeff---'，判 frontmatter 前先剥 BOM"""
    t, _, _ = read(path)
    if t.startswith("\ufeff"):
        t = t[1:]
    m = re.search(r"^title:\s*(.+)$", t, re.M)
    s = None
    if m:
        s = m.group(1).strip()
        s = re.sub(r"^ADR-\d{3}\s*", "", s)
    if not s:
        m = re.search(r"^#\s+(.+)$", t, re.M)
        if m:
            s = m.group(1).strip()
    if not s:
        m = re.search(r"^>\s*\*{0,2}(.+?)\*{0,2}\s*$", t, re.M)
        if m:
            s = m.group(1).strip()
    if not s:
        return ""
    s = re.sub(r"[（(][^）)]*20\d\d-\d\d-\d\d[^）)]*[）)]", "", s)
    s = re.sub(r"20\d\d-\d\d-\d\d", "", s)
    s = re.sub(r"\s*[—–-]\s*$", "", s)
    # 剥离验证叙事词（index 摘要禁含：静态N/N / 阴性对照 / 回滚点 / 探针 / 此前）
    s = re.sub(r"[（(][^）)]*(?:阴性对照|回滚点|探针|静态\s*\d+\s*/\s*\d+)[^）)]*[）)]", "", s)
    s = re.sub(r"\s*·?\s*(?:阴性对照|回滚点|探针实测|探针法|探针抓到)\b", "", s)
    s = re.sub(r"^此前\s*[，,]?\s*", "", s)
    s = re.sub(r"\s{2,}", " ", s).strip(" （）()·-—")
    return s[:120]


def tags_of(path):
    t, _, _ = read(path)
    m = re.search(r"^tags:\s*\[(.*?)\]", t, re.M)
    if not m:
        return ""
    tags = [x.strip() for x in m.group(1).split(",") if x.strip()]
    tags = [x for x in tags if x.lower() not in ("adr", "api", "模块", "规范", "教训", "指导")]
    return " ".join("#" + x for x in tags[:4])


def main():
    dry = "--dry" in sys.argv
    cats = collections.OrderedDict()
    for key, title, desc, no in CATS:
        d = os.path.join(WIKI, key)
        if not os.path.isdir(d):
            continue
        items = []
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md"):
                continue
            # §一 / §八 互斥：台账/过程类 project 页不在本节渲染（由 §八 单独渲染）
            if key == "project" and f in ARCHIVE_PROJECT:
                continue
            items.append((f[:-3], summary_of(os.path.join(d, f)), tags_of(os.path.join(d, f))))
        cats[key] = (title, desc, items)
    # people 单独成节（第九节），但仍需纳入扫描，否则该章节会整节缺失
    people_items = []
    pd_dir = os.path.join(WIKI, "people")
    if os.path.isdir(pd_dir):
        for f in sorted(os.listdir(pd_dir)):
            if not f.endswith(".md"):
                continue
            people_items.append((f[:-3], summary_of(os.path.join(pd_dir, f)), tags_of(os.path.join(pd_dir, f))))
    cats["people"] = ("九、专员职责", "分派任务", people_items)
    # rules 单独成节（第十二节）：流程规则（原 Skill 的 Key Rules 已下沉至此）
    rules_items = []
    rd_dir = os.path.join(WIKI, "rules")
    if os.path.isdir(rd_dir):
        for f in sorted(os.listdir(rd_dir)):
            if not f.endswith(".md") or f == "Rules-Index.md":
                continue
            rules_items.append((f[:-3], summary_of(os.path.join(rd_dir, f)), tags_of(os.path.join(rd_dir, f))))
    cats["rules"] = ("十二、流程规则", "编码前必过的规则门禁", rules_items)
    # §八 归档页数（ARCHIVE_PROJECT 中真实存在的文件数）
    proj_dir = os.path.join(WIKI, "project")
    archive_cnt = sum(1 for f in ARCHIVE_PROJECT if os.path.isfile(os.path.join(proj_dir, f)))

    total = sum(len(v[2]) for v in cats.values())
    print("分类统计：")
    for k, (t, d, items) in cats.items():
        print("  %-10s %3d 页   %s" % (k, len(items), t))

    if dry:
        print("\n摘要预览：")
        for k, (t, d, items) in cats.items():
            print("  [%s]" % t)
            for name, s, tg in items[:5]:
                print("    %-40s %s" % (name[:40], s[:80]))
        return 0

    # 读取速查路由：优先用结构化源 routes.tsv（唯一权威），回退到旧 index.md 内嵌表
    old = ""
    if os.path.isfile(IDX):
        old = read(IDX)[0]
    route_rows = []
    tsv = os.path.join(TOOLS_DIR, "data", "routes.tsv")
    if os.path.isfile(tsv):
        for line in read(tsv)[0].split("\n"):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                route_rows.append((parts[0].strip(), parts[1].strip(), parts[2].strip()))
    if not route_rows:
        m = re.search(r"## ⚡ 场景速查路由.*?\n\n(.*?)\n\n---", old, re.S)
        if m:
            for l in m.group(1).split("\n"):
                if not l.startswith("|") or '---' in l:
                    continue
                cells = [c.strip() for c in l.strip('|').split('|')]
                if len(cells) >= 3:
                    route_rows.append((cells[0], cells[1], cells[2]))

    L = []
    L.append("# Wiki Index — AdaWeldSystem 知识库索引")
    L.append("")
    L.append("> 内容导向路由索引。AI 回答查询前先读本文件定位相关页面，再读目标页。")
    L.append("> **最后更新：2026-10-30（全库治理轮：ADR 编号重编为 001~078 连续；本文件由 `tools/wiki_index_build.py` 生成，勿手工编辑分类表）**")
    L.append(">")
    L.append("> **格式契约**：见 [[standards/WikiPageFormatSpec]]——各页结构、字段、增长规则与脚本工具链的唯一规范。")
    L.append("> **详细叙事一律在 `logs/log.md`**，本页只做路由。")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## ⚡ 场景速查路由（首选入口 —— 命中即可开工，无需扫全表）")
    L.append("")
    L.append("> 用法：接到任务后先在下表命中一行，直接读右列页面。未命中再往下翻分类表。")
    L.append("")
    if route_rows:
        L.append("| 你要做的事 | 直接读这 1~3 页 | 硬约束提示 |")
        L.append("|---|---|---|")
        for a, b, c in route_rows:
            L.append("| %s | %s | %s |" % (a, b, c))
    else:
        L.append("| 你要做的事 | 直接读这 1~3 页 | 硬约束提示 |")
        L.append("|---|---|---|")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 目录")
    L.append("")
    L.append("| 章节 | 内容 | 何时看 |")
    L.append("|---|---|---|")
    for k, (t, d, items) in cats.items():
        if k in ("people", "rules"):
            continue          # people / rules 单独成节（第九 / 十二节），目录行已在下方单独输出
        extra = ""
        if k == "lessons":
            extra = " · %d 条坑" % len(items)
        L.append("| [%s](#%s) | %d 个页面%s · %s | %s |" % (
            t, re.sub(r'[^\w\u4e00-\u9fff]', '', t).lower(), len(items), extra, d, d))
    # lessons 计数须与 wiki_audit 的「历史教训 lessons](...) | N 条坑」口径一致
    L.append("| [五、历史教训 lessons](#五历史教训) | %d 条坑 | 编码前门禁 |" % len(cats.get("lessons", ("", "", []))[2]))
    adr_dir = os.path.join(WIKI, "decisions")
    adr_ns = sorted(int(m.group(1)) for m in
                    (re.match(r"ADR-(\d{3})-", f) for f in os.listdir(adr_dir)) if m)
    adr_cnt = len(adr_ns)
    adr_rng = "%03d~%03d" % (adr_ns[0], adr_ns[-1]) if adr_ns else "—"
    # 废止留档号：被并入他页的旧号（ADR-Index 中以指针行留档）—— 库内不变式「废止不回收编号」
    # ⇒ 磁盘无文件但编号仍在表内，故「连续」指的是编号区间连续，不是文件数连续。
    adr_index_path = os.path.join(adr_dir, "ADR-Index.md")
    adr_retired = []
    if os.path.isfile(adr_index_path):
        with open(adr_index_path, encoding="utf-8-sig") as fh:
            adr_retired = sorted(int(x) for x in
                                 re.findall(r"^\|\s*(\d{3})\s*\|\s*→", fh.read(), re.M))
    adr_note = ""
    if adr_retired:
        adr_note = "，另 %d 个旧号并入他页" % len(adr_retired)
    L.append("| [七、设计决策 ADR](#七设计决策) | %d 条（%s 连续%s） | 理解「为什么」/ 查约束 |"
             % (adr_cnt, adr_rng, adr_note))
    L.append("| [八、历史归档](#八历史归档现归-project) | %d 个页面 · 项目级台账与审计 | 追溯，不引用 |" % archive_cnt)
    L.append("| [九、专员职责](#九专员职责) | %d 个角色 | 分派任务 |" % len(cats.get("people", ("", "", []))[2]))
    L.append("| [十、来源索引](#十来源索引) | raw/ 映射 | 溯源 |")
    kr_ns = []
    kr_dir = os.path.join(WIKI, "rules")
    if os.path.isdir(kr_dir):
        for f in os.listdir(kr_dir):
            m = re.match(r"KR-(\d{3})-", f)
            if m:
                kr_ns.append(int(m.group(1)))
    L.append("| [十二、流程规则](#十二流程规则) | %d 条（KR-001~KR-%03d） | Skill 流程执行强制规则 |"
             % (len(cats.get("rules", ("", "", []))[2]), max(kr_ns) if kr_ns else 0))
    L.append("")
    for k, (t, d, items) in cats.items():
        if k in ("people", "rules"):
            continue          # 这两类单独成节（第九 / 十二节），在后面统一输出
        L.append("## %s" % t)
        L.append("")
        L.append("| 页面 | 摘要 | 标签 |")
        L.append("|---|---|---|")
        for name, s, tg in items:
            L.append("| [[%s/%s]] | %s | %s |" % (k, name, s, tg))
        L.append("")
    # 七 / 八 / 九 / 十 四节（按规范顺序）
    L.append("## 七、设计决策")
    L.append("")
    L.append("> **全量登记表唯一权威 = [[decisions/ADR-Index]]**（%s 连续无断号，含每条的主题/状态/日期；%d 个旧号已并入他页，以指针行留档）。本页不重复该表。"
             % (adr_rng, len(adr_retired)))
    L.append("> 新增决策前先跑 `tools/adr_new.py check <关键词>`——命中同主题则**合并**进既有页，不新建页；"
             "`check` 会按**落地实体符号 Jaccard** 判疑似重复（≥0.40 即拦截新建），"
             "命中即走 `adr_new.py merge`（规则见 [[standards/WikiPageFormatSpec]] §三）。")
    L.append("")
    L.append("## 八、历史归档（现归 project/）")
    L.append("")
    L.append("> 项目级过程台账、审计报告与进度快照；**不作为编码约束**，追溯用。")
    L.append("> ⛔ 与 §一「项目总览」**互斥**：每个 project 页只出现在其中一节（归属规则见生成器 `ARCHIVE_PROJECT`）。")
    L.append("")
    L.append("| 页面 | 摘要 | 标签 |")
    L.append("|---|---|---|")
    pd = os.path.join(WIKI, "project")
    if os.path.isdir(pd):
        for f in sorted(os.listdir(pd)):
            if not f.endswith(".md") or f not in ARCHIVE_PROJECT:
                continue
            L.append("| [[project/%s]] | %s | %s |" % (f[:-3], summary_of(os.path.join(pd, f)), tags_of(os.path.join(pd, f))))
    L.append("")
    L.append("## 九、专员职责")
    L.append("")
    L.append("| 页面 | 摘要 | 标签 |")
    L.append("|---|---|---|")
    for name, s, tg in cats.get("people", ("", "", []))[2]:
        L.append("| [[people/%s]] | %s | %s |" % (name, s, tg))
    L.append("")
    L.append("## 十、来源索引")
    L.append("")
    L.append("> raw/ 原始资料与 wiki 页的映射；**编写时先查此处**的官方文档与 demo（规则见 [[lessons/DocDemoDllLookupOrder]]）。")
    L.append("> **变更历史另见 `logs/INDEX.md`**（本库自身的归档索引，由 `tools/wiki_log_tidy.py index` 生成）—— 查「上次怎么处理的」走它，⛔ 不凭记忆。")
    L.append("")
    L.append("| 原始资产 | 内容 | 提炼页 |")
    L.append("|---|---|---|")
    for row in [
        ("raw/AntdUI/wiki-zh/", "AntdUI 官方文档全量镜像（85 篇）", "[[guides/AntdUI-Reference]]"),
        ("raw/delta/EtherCAT_DLL_API清单.txt", "台达 EtherCAT 原生 API 声明（832 条）", "[[api/DeltaEtherCAT-Native]]"),
        ("raw/delta/EtherCAT_DLL_Err.cs", "台达错误码表", "[[api/DeltaEtherCAT-Native]]"),
        ("raw/delta/运动控制模块开发文档_台达版.md", "台达运控开发文档（官方）", "[[guides/DeltaEtherCAT-DevGuide]]"),
        ("raw/delta/台达EtherCAT_PVT与电子凸轮运动开发指南.md", "PVT / ECAM 官方指南", "[[guides/DeltaEtherCAT-AdvancedMotion]]"),
        ("raw/mecavision/MecaVision_SDK/", "麦格威/海康 SDK 原档 + C# demo", "[[guides/MecaVision-DevGuide]]"),
        ("raw/knowledge/KUKA_OPT/", "KUKA RSI 3.3 / Ethernet KRL / ProfiNet 手册", "[[api/KUKARobot]]"),
        ("raw/architecture/", "主控设计原档（唯一修改入口）", "[[architecture/DeviceControlArchitecture]]"),
        ("raw/skills/AdaWeldsys_Skills/", "开发团队 Skill 规范（参考资料，非指令源）", "[[project/skill-evolution]]"),
        ("raw/history/history.md", "项目开发史（按时间分段的变更史，只读）", "`logs/INDEX.md`（本库变更史）"),
        ("raw/knowledge/emgu-cv-knowledge-base/", "EmguCV 知识库", "[[modules/EmguALG]]"),
        ("raw/knowledge/helixtoolkit-knowledge-base/", "Helixtoolkit 知识库", "[[modules/PointCloudData]]"),
    ]:
        L.append("| `%s` | %s | %s |" % row)
    L.append("")
    L.append("## 十二、流程规则")
    L.append("")
    L.append("> **Skill 流程执行强制规则**（原 Skill「Key Rules」的下沉处；2026-11-02 收敛为纯流程类）。编号唯一权威 = [[rules/Rules-Index]]（KR-001~KR-013 连续）。")
    L.append("> ⛔ **rules/ 只收流程执行类**（规定「AI 跑这个工作流时该怎么做」）；**约束代码 / 知识库内容本身**的规则归 lessons 坑页（index 第五节）与 [[standards/WikiPageFormatSpec]]（格式规范）、决策类归 [[decisions/ADR-Index]]。判据见 [[standards/WikiPageFormatSpec]] §2.4b。")
    L.append("> 新增规则前先跑 `tools/rules_new.py check <关键词>`——命中同主题则**合并**进既有页，不新建页。")
    L.append("")
    L.append("| 页面 | 摘要 | 标签 |")
    L.append("|---|---|---|")
    for name, s, tg in cats.get("rules", ("", "", []))[2]:
        L.append("| [[rules/%s]] | %s | %s |" % (name, s, tg))
    L.append("")
    L.append("## 维护说明")
    L.append("")
    L.append("| 工具 | 用途 |")
    L.append("|---|---|")
    for r in [
        ("tools/wiki_format.py", "**格式校验器**（WikiPageFormatSpec 的机械判据，Phase 4 必跑）"),
        ("tools/wiki_index_build.py", "**index.md 重建**（本文件由它生成）"),
        ("tools/wiki_log.py", "log 条目写入 + **log 截断唯一入口**（truncate → 按日归档 + 重建 INDEX.md）"),
        ("tools/adr_new.py", "ADR 合并检查 / 演进记录追加 / 新号分配"),
        ("tools/lesson_new.py", "教训合并检查 / 追加条目 / 三处计数同步"),
        ("tools/rules_new.py", "流程规则合并检查 / 演进记录追加 / 新号分配 / 索引登记"),
        ("tools/rules_check.py", "**流程规则页校验**（编号连续 / 结构契约 / 索引一致 / 判据非空）"),
        ("tools/skill_pointer_check.py", "**Skill 指向防漂移闸门**（⛔ 不得写死内容页名）"),
        ("tools/wiki_audit.py", "11 项体检：红链 / 孤儿 / 索引重复 / ADR 空洞 / 体积 / 重复度 / 错放 / 入链 / 子目录 / 过小分类 / lessons 三处一致"),
        ("tools/lint_scan.py", "死链 / 孤儿 / ADR 编号冲突 / 外链失效"),
        ("tools/drift_scan_precise.py", "wiki 引用的 .cs 是否仍存在"),
        ("tools/ingest_purity_scan.py", "沉淀纯度：禁验证叙事 / 日期沿革 / 日志体回灌"),
    ]:
        L.append("| `%s` | %s |" % r)
    L.append("")
    L.append("**执行方式**：在 `Vicoding管理平台/LLMWiki/` 下运行 `python tools/<script>.py`。")
    L.append("")
    L.append("**健康判据**：红链 0 · 孤儿 0 · 索引重复行 0 · 二级子目录 0 · 过小分类 0 · lessons 三处一致 · drift 待修正 0 · 纯度违规 0 · **格式违规 0**。")
    L.append("")

    text = "\n".join(L)
    # ---------- 生成期自检：索引条目不得重复 + §一/§八 对 project 页必须互斥且完备 ----------
    link_rows = collections.OrderedDict()
    for i, ln in enumerate(L, 1):
        s = ln.strip()
        if s.startswith("| [[") and s.endswith("|"):
            m = re.search(r"\[\[([^\]]+)\]\]", s.split("|")[1])
            if m:
                link_rows.setdefault(m.group(1).strip(), []).append(i)
    dups = {k: v for k, v in link_rows.items() if len(v) > 1}
    if dups:
        for k, v in sorted(dups.items()):
            print("❌ 索引重复条目：[[%s]] 出现 %d 次（行 %s）" % (k, len(v), v))
        return 1
    # project 页归属完备性：每个 project/*.md 恰好在 §一 或 §八 出现一次
    proj_pages = set()
    if os.path.isdir(proj_dir):
        proj_pages = {f[:-3] for f in os.listdir(proj_dir) if f.endswith(".md")}
    idx_project = {k.split("/", 1)[1] for k in link_rows if k.startswith("project/")}
    missing = sorted(proj_pages - idx_project)
    if missing:
        print("❌ project 页未进索引（§一/§八 归属缺失）：%s" % missing)
        return 1
    print("✅ 自检通过：索引条目 %d 条无重复；project 页 %d 个全部有归属（§一 %d / §八 %d）"
          % (len(link_rows), len(proj_pages),
             len(proj_pages - {f[:-3] for f in ARCHIVE_PROJECT}),
             len(proj_pages & {f[:-3] for f in ARCHIVE_PROJECT})))
    _, bom, nl = (read(IDX) if os.path.isfile(IDX) else ("", False, "\n"))
    out = text.replace("\n", nl).encode("utf-8")
    if bom:
        out = b"\xef\xbb\xbf" + out
    open(IDX, "wb").write(out)
    print("\n已重建 index.md：%d 行 / %d 字节（分类页合计 %d）" % (len(L), len(out), total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
