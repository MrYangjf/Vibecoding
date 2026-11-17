#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules_new.py —— 流程规则页的新增/合并助手（强制「先合并、后新建」，与 ADR 同规则）

子命令：
  check  <关键词...>    检索同主题规则页（合并候选）—— 新建前必须先跑
  merge  <KR-NNN> <主题> <变更> <理由> <影响>
                       向既有规则页追加「## 演进记录」小节（不新建页）
  new    <slug> <标题> <一句话规则> <正文> <判据>
                       仅在 check 报告无候选时使用；自动分配新号并登记 Rules-Index
退出码：0 成功；1 参数/校验错误。
"""
import os
import re
import sys
import datetime

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
RULES = os.path.join(LLMWIKI, "wiki", "rules")
INDEX = os.path.join(RULES, "Rules-Index.md")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def rd(p):
    b = open(p, "rb").read(); bom = b[:3] == b"\xef\xbb\xbf"; body = b[3:] if bom else b
    crlf = body.count(b"\r\n"); lf = body.count(b"\n") - crlf
    return body.decode("utf-8").replace("\r\n", "\n"), bom, ("\r\n" if crlf > lf else "\n")


def wr(p, t, bom, nl):
    out = t.replace("\r\n", "\n").replace("\n", nl).encode("utf-8")
    if bom: out = b"\xef\xbb\xbf" + out
    open(p, "wb").write(out)


def rule_files():
    out = []
    for f in sorted(os.listdir(RULES)):
        m = re.match(r"KR-(\d{3})-(.*)\.md$", f)
        if m:
            out.append((int(m.group(1)), m.group(2), f))
    return out


def max_no():
    ns = [n for n, _, _ in rule_files()]
    return max(ns) if ns else 0


def cmd_check(argv):
    if not argv:
        print("用法: rules_new.py check <关键词...>")
        return 1
    keys = [k.lower() for k in argv]
    hits = []
    for n, slug, f in rule_files():
        t = rd(os.path.join(RULES, f))[0].lower()
        score = sum(1 for k in keys if k in t or k in slug.lower())
        if score:
            m = re.search(r"^title:\s*(.*)$", t, re.M)
            hits.append((score, n, slug, m.group(1) if m else ""))
    hits.sort(reverse=True)
    if not hits:
        print("未发现同主题候选 —— 可走新建路径（rules_new.py new）")
        return 0
    print("发现 %d 个同主题候选 —— 优先走【合并路径】（rules_new.py merge），不要新建页：" % len(hits))
    for s, n, slug, title in hits[:10]:
        print("  [命中 %d/%d] KR-%03d-%s  %s" % (s, len(keys), n, slug, title[:70]))
    return 0


def cmd_merge(argv):
    if len(argv) < 5:
        print("用法: rules_new.py merge <KR-NNN> <主题> <变更> <理由> <影响>")
        return 1
    no = argv[0].replace("KR-", "")
    topic, change, reason, impact = argv[1], argv[2], argv[3], argv[4]
    target = None
    for n, slug, f in rule_files():
        if ("KR-%03d" % n) == ("KR-" + no) or f.startswith("KR-%s-" % no):
            target = f
            break
    if not target:
        print("未找到 KR-%s" % no)
        return 1
    p = os.path.join(RULES, target)
    t, bom, nl = rd(p)
    today = datetime.date.today().isoformat()
    block = ["", "### %s · %s" % (today, topic[:60]),
             "- **变更**：%s" % change[:100],
             "- **理由**：%s" % reason[:100],
             "- **影响**：%s" % impact[:100], ""]
    anchor = "\n## 相关页面"
    if anchor in t:
        t = t.replace(anchor, "\n" + "\n".join(block) + anchor, 1)
    else:
        t = t.rstrip("\n") + "\n" + "\n".join(block)
    wr(p, t, bom, nl)
    print("已向 %s 追加演进记录" % target)
    return 0


def cmd_new(argv):
    if len(argv) < 6:
        print("用法: rules_new.py new <slug> <标题> <一句话规则> <适用范围> <正文> <判据>")
        print("  适用范围写「**适用**：… / **不适用**：…」")
        print("  ⛔ rules/ 只收流程执行类；约束代码 / 知识库内容的规则请归 lessons/ 或 standards/")
        return 1
    slug, title, one, scope, body, judge = argv[0], argv[1], argv[2], argv[3], argv[4], argv[5]
    n = max_no() + 1
    fname = "KR-%03d-%s.md" % (n, slug)
    p = os.path.join(RULES, fname)
    if os.path.exists(p):
        print("文件已存在：%s" % fname)
        return 1
    today = datetime.date.today().isoformat()
    L = ["---", "title: KR-%03d %s" % (n, title), "date: %s" % today,
         "updated: %s" % today, "tags: [规则, 流程, Skill执行]", "status: accepted", "---", "",
         "# KR-%03d %s" % (n, title), "",
         "> **一句话规则**：%s" % one[:120], "",
         "## 适用范围", "", scope[:400], "",
         "## 规则正文", "", body[:2000], "",
         "## 判据", "", "- ⛔ 违反判定：%s" % judge[:200], "",
         "## 反例", "", "| 反例（违规写法） | 正解 |", "|---|---|",
         "| 跳过本规则直接动手 | 按「适用范围」执行本规则 |",
         "| 把内容类判据写进规则页 | 归 lessons/ 或 standards/ |", "",
         "## 相关页面", "", "- [[rules/Rules-Index]]", ""]
    wr(p, "\n".join(L), False, "\n")
    print("已创建 %s（新号 = max+1 = %d）" % (fname, n))
    # 登记 Rules-Index
    if os.path.isfile(INDEX):
        it, ibom, inl = rd(INDEX)
        row = "| KR-%03d | %s | %s | [[rules/%s]] |" % (n, title[:40], one[:40], fname[:-3])
        marker = "\n\n---"
        if marker in it:
            it = it.replace(marker, "\n" + row + marker, 1)
        else:
            it = it.rstrip("\n") + "\n" + row + "\n"
        wr(INDEX, it, ibom, inl)
        print("  Rules-Index 已登记一行")
    print("⚠️ 仍需：① 在 wiki/index/index.md 第十二节登记（跑 tools/wiki_index_build.py）② 跑 tools/rules_check.py")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "check":
        return cmd_check(rest)
    if cmd == "merge":
        return cmd_merge(rest)
    if cmd == "new":
        return cmd_new(rest)
    print("未知子命令：%s（可用 check / merge / new）" % cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())
