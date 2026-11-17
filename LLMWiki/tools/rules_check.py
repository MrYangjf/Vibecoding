#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules_check.py —— Skill 流程执行强制规则页（wiki/rules/）的结构与一致性校验

判据：
  R1 编号连续：KR-001 ~ KR-NNN 连续无空洞
  R2 页面结构契约：一句话规则 / 适用范围 / 规则正文 / 判据 / 反例 / 相关页面 六节齐备
  R3 frontmatter 完整（title 含自身编号 · date · updated · status · tags）
  R4 Rules-Index 登记一致：索引表行数 == 实际页数，且每页都在索引中出现
  R5 判据非空（「## 判据」节至少 1 条 ⛔ 违反判定）
  R6 规则正文不得含验证叙事（静态 N/N / 阴性对照 / 探针）
  R7 行数上限 150
  R8 数量上限 20（rules/ 只收流程执行类；超限即说明内容类规则混入）
  R9 适用范围非空（必须写明「何时适用 / 何时不适用」）
退出码：0 通过；1 存在违规。
"""
import os
import re
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
RULES = os.path.join(LLMWIKI, "wiki", "rules")
INDEX = os.path.join(RULES, "Rules-Index.md")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LIMIT_LINES = 150
LIMIT_PAGES = 20          # 规则页数量上限（见 WikiPageFormatSpec §3.4）
REQUIRED = ["## 适用范围", "## 规则正文", "## 判据", "## 反例", "## 相关页面"]
violations = []


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8", errors="replace").replace("\r\n", "\n")


def add(rel, ln, rule, msg):
    violations.append("%s:%d [%s] %s" % (rel, ln, rule, msg))


def main():
    if not os.path.isdir(RULES):
        print("未找到规则目录：%s" % RULES)
        return 1
    pages = {}
    for f in sorted(os.listdir(RULES)):
        m = re.match(r"KR-(\d{3})-(.*)\.md$", f)
        if m:
            pages[int(m.group(1))] = f
    if not pages:
        print("规则目录为空")
        return 1

    # R1 编号连续
    ns = sorted(pages)
    holes = [n for n in range(ns[0], ns[-1] + 1) if n not in pages]
    if holes:
        add("rules/", 1, "R1-编号", "编号空洞：%s" % holes)
    # R8 数量上限
    if len(pages) > LIMIT_PAGES:
        add("rules/", 1, "R8-数量", "规则页 %d 个 > %d 个上限（须强制合并）" % (len(pages), LIMIT_PAGES))

    # R2/R3/R5/R6/R7 逐页
    for n, f in sorted(pages.items()):
        rel = "rules/" + f
        t = read(os.path.join(RULES, f))
        L = t.split("\n")
        if len(L) > LIMIT_LINES:
            add(rel, 1, "R7-行数", "%d 行 > %d 行上限" % (len(L), LIMIT_LINES))
        # frontmatter
        fm = {}
        hl = list(L[:12])
        if hl and hl[0].startswith("\ufeff"):
            hl[0] = hl[0][1:]
        if hl and hl[0].strip() == "---":
            for l in hl[1:]:
                if l.strip() == "---":
                    break
                if ":" in l:
                    k = l.split(":", 1)[0].strip()
                    if k:
                        fm[k] = l.split(":", 1)[1].strip()
        for k in ("title", "date", "updated", "status", "tags"):
            if k not in fm:
                add(rel, 1, "R3-frontmatter", "缺字段 %s" % k)
        if "title" in fm and ("KR-%03d" % n) not in fm["title"]:
            add(rel, 1, "R3-标题", "title 不含自身编号 KR-%03d" % n)
        if not re.search(r"^#\s+KR-%03d\b" % n, t, re.M):
            add(rel, 1, "R2-H1", "H1 不含自身编号 KR-%03d" % n)
        # 必需章节
        for need in REQUIRED:
            if not re.search(r"^%s\s*$" % re.escape(need), t, re.M):
                add(rel, 1, "R2-章节", "缺章节 %s" % need)
        if not re.search(r"^>\s*\*\*一句话规则\*\*", t, re.M):
            add(rel, 1, "R2-摘要", "缺「> **一句话规则**」")
        # R5 判据非空
        m = re.search(r"^##\s*判据\s*$(.*?)(?=^##\s|\Z)", t, re.M | re.S)
        if not m or "违反判定" not in m.group(1):
            add(rel, 1, "R5-判据", "判据节为空或缺「违反判定」")
        # R9 适用范围非空（必须写明适用 / 不适用）
        m = re.search(r"^##\s*适用范围\s*$(.*?)(?=^##\s|\Z)", t, re.M | re.S)
        if not m or not m.group(1).strip():
            add(rel, 1, "R9-适用范围", "适用范围节为空（必须写明何时适用 / 何时不适用）")
        elif "适用" not in m.group(1):
            add(rel, 1, "R9-适用范围", "适用范围未写明「适用 / 不适用」")
        # R6 叙事（⛔ 不含「回滚点」—— 那是 backup 规则的正常业务术语）
        for i, l in enumerate(L, 1):
            if re.search(r"(静态\s*\d+\s*/\s*\d+|阴性对照|探针实测|探针抓到)", l):
                add(rel, i, "R6-叙事", "含验证过程叙事（应移入 log）")

    # R4 索引一致
    if not os.path.isfile(INDEX):
        add("rules/Rules-Index.md", 1, "R4-索引", "Rules-Index.md 不存在")
    else:
        it = read(INDEX)
        rows = re.findall(r"\[\[rules/KR-(\d{3})-", it)
        listed = sorted(set(int(x) for x in rows))
        actual = sorted(pages)
        if listed != actual:
            miss = sorted(set(actual) - set(listed))
            extra = sorted(set(listed) - set(actual))
            add("rules/Rules-Index.md", 1, "R4-索引", "索引与实际不一致：漏登记 %s / 多余 %s" % (miss or "无", extra or "无"))

    print("=" * 70)
    print("rules_check.py —— 流程规则页校验")
    print("=" * 70)
    print("  规则页 %d 个，编号 KR-%03d ~ KR-%03d" % (len(pages), ns[0], ns[-1]))
    if violations:
        print("\n违规 %d 处：" % len(violations))
        for v in violations:
            print("  " + v)
        return 1
    print("  通过：编号连续 / 结构契约齐备 / 索引一致 / 判据非空 / 无叙事")
    return 0


if __name__ == "__main__":
    sys.exit(main())
