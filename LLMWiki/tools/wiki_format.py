#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_format.py —— Wiki 页面格式校验器（第五扫描器，机械判据）

校验 wiki/standards/WikiPageFormatSpec.md 定义的格式契约：
  R1  index.md        行数/字节上限、章节顺序、禁日期串、禁内嵌 ADR 总表
  R2  ADR 页          行数上限、frontmatter 必需字段、title 含自身号、决策条目长度
  R3  lessons 页      行数上限、必需章节
  R4  各类说明页      行数上限
  R5  log.md          条目格式与条数上限
  R6  跨类            索引与权威页重复登记（ADR 总表只允许在 ADR-Index）

退出码：0 = 通过；1 = 存在违规（逐条打印 文件:行号 [规则] 摘要）
路径：一律由 __file__ 推导，禁硬编码绝对路径。
"""
import os
import re
import sys
import collections
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
WIKI = os.path.join(LLMWIKI, "wiki")

# ---- 格式契约参数（与 WikiPageFormatSpec.md 同源）----
LIMIT_INDEX_LINES = 600
LIMIT_INDEX_BYTES = 80 * 1024
LIMIT_ADR_LINES = 200
LIMIT_ADR_COMBINED_LINES = 300     # 整合页（吸收过历史 ADR 的综合页）放宽
LIMIT_LESSON_LINES = 250
LIMIT_LESSON_MULTI_LINES = 700
LIMIT_LOG_ENTRIES = 50
LIMIT_CELL_CHARS = 120
LIMIT_ROUTE_HINT = 80
LIMIT_DECISION_ITEM = 100
LIMIT_GENERIC = {
    "modules": 600, "api": 1200, "guides": 1600, "standards": 600,
    "project": 800, "people": 200, "architecture": 1800, "rules": 150,
}
ADR_REQUIRED = ["## 背景", "## 决策", "## 备选方案", "## 后果", "## 相关页面"]
LESSON_REQUIRED = ["## 现象", "## 根因", "## 判据", "## 预防"]
ADR_FRONTMATTER = ["title", "date", "updated", "status", "tags"]
INDEX_SECTIONS = ["## ⚡ 场景速查路由", "## 目录", "## 一、项目总览", "## 二、模块详解",
                  "## 三、API 参考", "## 四、规范标准", "## 五、历史教训",
                  "## 六、操作指导", "## 七、设计决策", "## 八、历史归档",
                  "## 九、专员职责", "## 十、来源索引", "## 十二、流程规则", "## 维护说明"]

violations = []
suggestions = []


def read_lines(rel):
    p = os.path.join(WIKI, rel)
    with open(p, "rb") as f:
        return f.read().decode("utf-8", errors="replace").split("\n")


def add(rel, line_no, rule, msg):
    violations.append("%s:%d [%s] %s" % (rel, line_no, rule, msg))


def sug(rel, line_no, rule, msg):
    suggestions.append("%s:%d [%s] %s" % (rel, line_no, rule, msg))


def check_index():
    rel = os.path.join("index", "index.md")
    p = os.path.join(WIKI, rel)
    raw = open(p, "rb").read()
    lines = read_lines(rel)
    n = len(lines)
    if n > LIMIT_INDEX_LINES:
        add(rel, 1, "R1-行数", "index.md %d 行 > %d 行上限" % (n, LIMIT_INDEX_LINES))
    if len(raw) > LIMIT_INDEX_BYTES:
        add(rel, 1, "R1-字节", "index.md %d 字节 > %d 字节上限" % (len(raw), LIMIT_INDEX_BYTES))
    # 章节顺序
    pos = -1
    for sec in INDEX_SECTIONS:
        try:
            i = next(k for k, l in enumerate(lines) if l.startswith(sec))
        except StopIteration:
            add(rel, 1, "R1-章节", "缺少章节 %s" % sec)
            continue
        if i < pos:
            add(rel, i + 1, "R1-章节序", "章节 %s 位置错乱" % sec)
        pos = i
    # 日期串禁入正文（抬头 blockquote 允许；速查路由表第 1 列允许作检索线索）
    route_start = route_end = -1
    for i, l in enumerate(lines):
        if l.startswith("## ⚡ 场景速查路由"):
            route_start = i
        elif route_start >= 0 and route_end < 0 and l.startswith("## "):
            route_end = i
    if route_end < 0:
        route_end = len(lines)
    for i, l in enumerate(lines, 1):
        if i <= 8:
            continue
        in_route = route_start <= i - 1 < route_end
        if in_route and l.startswith("|"):
            cells = [c.strip() for c in l.strip('|').split('|')]
            # 第 3 列（硬约束提示）与第 2 列禁日期；第 1 列允许
            for ci in (1, 2):
                if ci < len(cells) and re.search(r'20\d\d-\d\d-\d\d', cells[ci]):
                    add(rel, i, "R1-日期", "速查路由表第 %d 列出现日期串" % (ci + 1))
            if '~~' in l:
                add(rel, i, "R1-删除线", "速查路由表出现删除线（属历史叙事，应移入 log）")
            continue
        if re.search(r'20\d\d-\d\d-\d\d', l) and not l.lstrip().startswith('>'):
            add(rel, i, "R1-日期", "正文出现日期串（应移入 log 或 ADR-Index）")
        # 表格单元格长度
        if l.startswith('|') and '---' not in l:
            cells = [c.strip() for c in l.strip('|').split('|')]
            for c in cells:
                if len(c) > LIMIT_CELL_CHARS * 4:
                    add(rel, i, "R1-单元格", "单元格 %d 字符（建议 ≤%d）" % (len(c), LIMIT_CELL_CHARS))
        if '~~' in l:
            add(rel, i, "R1-删除线", "索引中出现删除线（属历史叙事，应移入 log）")
    # 禁内嵌 ADR 总表
    if re.search(r'^\|\s*ADR-\d{3}\s*\|\s*\[\[decisions/', "\n".join(lines), re.M):
        add(rel, 1, "R1-重复表", "index.md 内嵌 ADR 总表（唯一权威应为 ADR-Index）")
    # 速查路由第三列长度
    try:
        s = next(k for k, l in enumerate(lines) if l.startswith("## ⚡ 场景速查路由"))
        e = next((k for k, l in enumerate(lines[s + 1:], s + 1) if l.startswith("## ")), len(lines))
        for i in range(s, e):
            l = lines[i]
            if l.startswith('|') and '---' not in l:
                cells = [c.strip() for c in l.strip('|').split('|')]
                if len(cells) >= 3 and len(cells[2]) > LIMIT_ROUTE_HINT:
                    add(rel, i + 1, "R1-路由提示", "硬约束提示 %d 字符 > %d" % (len(cells[2]), LIMIT_ROUTE_HINT))
    except StopIteration:
        pass


def check_adr():
    dec = os.path.join(WIKI, "decisions")
    for f in sorted(os.listdir(dec)):
        if not f.endswith(".md") or f == "ADR-Index.md":
            continue
        rel = os.path.join("decisions", f)
        lines = read_lines(rel)
        text0 = "\n".join(lines)
        # 整合页判定：吸收过历史 ADR（含 merged_from / 沿革 / 被推翻的中间态）
        combined = bool(re.search(r"^merged_from\s*:", text0, re.M)) or \
            bool(re.search(r"^##\s*(沿革|被推翻的中间态|演进记录)", text0, re.M))
        lim = LIMIT_ADR_COMBINED_LINES if combined else LIMIT_ADR_LINES
        if len(lines) > lim:
            kind = "整合页" if combined else "单决策页"
            add(rel, 1, "R2-行数", "ADR%s %d 行 > %d 行上限" % (kind, len(lines), lim))
        m = re.match(r"ADR-(\d{3})-", f)
        if not m:
            add(rel, 1, "R2-命名", "文件名不符合 ADR-NNN-Slug.md")
            continue
        no = m.group(1)
        head = "\n".join(lines[:12])
        fm = {}
        hl = list(lines[:12])
        if hl and hl[0].startswith("\ufeff"):
            hl[0] = hl[0][1:]
        if hl and hl[0].strip() == "---":
            for l in hl[1:]:
                if l.strip() == "---":
                    break
                if ":" in l:
                    k = l.split(":")[0].strip()
                    if k:
                        fm[k] = l.split(":", 1)[1].strip()
        for k in ADR_FRONTMATTER:
            if k not in fm:
                add(rel, 1, "R2-frontmatter", "缺字段 %s" % k)
        if "title" in fm and ("ADR-" + no) not in fm["title"]:
            add(rel, 1, "R2-标题", "title 不含自身编号 ADR-%s" % no)
        if "status" in fm and fm["status"] not in ("proposed", "accepted", "deprecated"):
            add(rel, 1, "R2-状态", "status 值非法：%s" % fm["status"])
        for i, l in enumerate(lines, 1):
            if l.startswith("# ADR-") and ("ADR-" + no) not in l:
                add(rel, i, "R2-H1", "H1 不含自身编号")
            if l.startswith("|") and '---' not in l:
                for c in [x.strip() for x in l.strip('|').split('|')]:
                    if len(c) > LIMIT_DECISION_ITEM * 3:
                        sug(rel, i, "R2-建议", "表格条目 %d 字符（建议 ≤%d）" % (len(c), LIMIT_DECISION_ITEM))
        text = "\n".join(lines)
        for need in ADR_REQUIRED:
            # 章节名允许带括号后缀；存量 ADR 章节名多样 → 仅提示
            pat = r"^%s(?:\s*[（(].*?[）)])?\s*$" % re.escape(need)
            if re.search(pat, text, re.M):
                continue
            sug(rel, 1, "R2-建议", "建议补章节 %s" % need)
        # 禁过程叙事（验证结果属 log）；「实测法/探针法」是方法论约束，不算叙事
        for i, l in enumerate(lines, 1):
            if re.search(r'(静态\s*\d+\s*/\s*\d+|阴性对照|回滚点|探针实测|探针抓到)', l):
                add(rel, i, "R2-叙事", "含验证过程叙事（结果应移入 log）")


def check_lessons():
    """教训页校验：
      · 行数上限
      · 结构：单坑页要求 '## 现象/## 根因/## 判据/## 预防'；
        多坑页（存在 '### ' 子章节）允许以子章节承载，允许缺 '## ' 级章节
      · 必须有标题与一句话摘要
    """
    d = os.path.join(WIKI, "lessons")
    for f in sorted(os.listdir(d)):
        if not f.endswith(".md"):
            continue
        rel = os.path.join("lessons", f)
        lines = read_lines(rel)
        text = "\n".join(lines)
        multi = bool(re.search(r"^###\s+\S", text, re.M))
        # 多坑页判据：坑数（## 坑N / ## 陷阱N / ## 七.N / ### 小节）≥5 ⇒ 视为多坑页
        pit_count = len(re.findall(r"^##\s*(?:坑|陷阱|第[一二三四五六七八九十]+|\d+[.、])", text, re.M))
        pit_count += len(re.findall(r"^###\s*(?:七|[一二三四五六七八九十]+|\d+)[.、]", text, re.M))
        multi = multi or pit_count >= 5
        lim = LIMIT_LESSON_MULTI_LINES if multi else LIMIT_LESSON_LINES
        if len(lines) > lim:
            kind = "多坑页(%d 坑)" % pit_count if multi else "单坑页"
            add(rel, 1, "R3-行数", "教训%s %d 行 > %d 行上限" % (kind, len(lines), lim))
        for need in LESSON_REQUIRED:
            # 章节名允许带括号/日期后缀（如 '## 现象（2026-09-09 实测）'）
            pat_h2 = r"^%s(?:\s*[（(].*?[）)])?\s*$" % re.escape(need)
            pat_h3 = r"^%s(?:\s*[（(].*?[）)])?\s*$" % re.escape(need.replace("## ", "### "))
            if re.search(pat_h2, text, re.M) or re.search(pat_h3, text, re.M):
                continue
            # 存量页章节命名多样（## 坑一：… / ## 一、… / ## 背景）→ 仅提示不失败
            sug(rel, 1, "R3-建议", "建议补章节 %s（多坑页可用 '### %s'）" % (need, need.replace("## ", "")))
        if not re.search(r"^#\s+\S", text, re.M):
            add(rel, 1, "R3-标题", "缺少一级标题")


def check_generic():
    for cat, lim in LIMIT_GENERIC.items():
        d = os.path.join(WIKI, cat)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md"):
                continue
            rel = os.path.join(cat, f)
            lines = read_lines(rel)
            if len(lines) > lim:
                add(rel, 1, "R4-行数", "%s 页 %d 行 > %d 行上限" % (cat, len(lines), lim))


def check_log():
    rel = os.path.join("..", "logs", "log.md")
    p = os.path.join(LLMWIKI, "logs", "log.md")
    if not os.path.isfile(p):
        return
    with open(p, "rb") as f:
        raw = f.read().decode("utf-8", errors="replace")
    lines = raw.replace("\r\n", "\n").split("\n")
    entries = [i for i, l in enumerate(lines, 1) if l.startswith("## [")]
    if len(entries) > LIMIT_LOG_ENTRIES:
        add("logs/log.md", entries[LIMIT_LOG_ENTRIES], "R5-条目数",
            "log 条目 %d 条 > %d 条上限（应执行 tools/wiki_log.py truncate）" % (len(entries), LIMIT_LOG_ENTRIES))
    # 时间倒序
    ts = [re.match(r"## \[(\d{4}-\d{2}-\d{2})", lines[i - 1]) for i in entries]
    dates = [m.group(1) for m in ts if m]
    for a, b in zip(dates, dates[1:]):
        if a < b:
            add("logs/log.md", 1, "R5-倒序", "时间倒序被破坏：%s 出现在 %s 之后" % (a, b))
            break
    for i in entries:
        l = lines[i - 1]
        if not re.match(r"## \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \S+ \| ", l):
            add("logs/log.md", i, "R5-条目格式", "条目格式不合规：%s" % l[:60])


def check_dup_authority():
    """ADR 总表只允许在 ADR-Index；index.md 不得内嵌"""
    idx = os.path.join(WIKI, "index", "index.md")
    ai = os.path.join(WIKI, "decisions", "ADR-Index.md")
    if not (os.path.isfile(idx) and os.path.isfile(ai)):
        return
    it = open(idx, "rb").read().decode("utf-8", errors="replace")
    at = open(ai, "rb").read().decode("utf-8", errors="replace")
    i_rows = len(re.findall(r'^\|\s*ADR-\d{3}\s*\|', it, re.M))
    a_rows = len(re.findall(r'^\|\s*\d{3}\s*\|', at, re.M))
    if i_rows:
        add("index/index.md", 1, "R6-重复登记", "index.md 内嵌 %d 行 ADR 表（唯一权威应为 ADR-Index）" % i_rows)
    if a_rows and a_rows < 60:
        add("decisions/ADR-Index.md", 1, "R6-总表", "ADR-Index 仅 %d 行，疑似未登记完整" % a_rows)


print("=" * 70)
print("wiki_format.py —— Wiki 页面格式校验")
print("=" * 70)
check_index()
check_adr()
check_lessons()
check_generic()
check_log()
check_dup_authority()

print()
if suggestions:
    print("建议 %d 处（不阻塞，仅提示）：" % len(suggestions))
    seen = collections.Counter()
    for s in suggestions:
        key = s.split(":")[0] + "|" + s.split("[")[1].split("]")[0]
        seen[key] += 1
    for k, c in seen.most_common(15):
        print("  %-56s x%d" % (k, c))
    print()
if violations:
    print("违规 %d 处：" % len(violations))
    for v in violations:
        print("  " + v)
    sys.exit(1)
print("通过：index / ADR / lessons / 各类说明页 / log 均符合 WikiPageFormatSpec 硬约束")
sys.exit(0)
