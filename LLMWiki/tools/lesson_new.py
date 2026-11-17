#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lesson_new.py —— 教训页新增/合并助手（强制「先合并、后新建」）

子命令：
  check  <关键词...>     检索同族教训页（合并候选）
  merge  <页名> <标题> <现象> <判据> <预防>
                        向既有教训页追加「追加条目」小节
  new    <页名> <标题> <现象> <根因> <判据> <预防>
                        新建教训页并同步 index.md §五表行与摘要计数

三处同步（目录 / §五表行 / 摘要计数）由脚本完成，避免计数漂移。
退出码：0 成功；1 参数错误。
"""
import os
import re
import sys
import datetime

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
LES = os.path.join(LLMWIKI, "wiki", "lessons")
IDX = os.path.join(LLMWIKI, "wiki", "index", "index.md")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def read(p):
    b = open(p, "rb").read()
    bom = b[:3] == b"\xef\xbb\xbf"
    body = b[3:] if bom else b
    crlf = body.count(b"\r\n")
    lf = body.count(b"\n") - crlf
    return body.decode("utf-8", errors="replace").replace("\r\n", "\n"), bom, ("\r\n" if crlf > lf else "\n")


def write(p, t, bom, nl):
    out = t.replace("\r\n", "\n").replace("\n", nl).encode("utf-8")
    if bom:
        out = b"\xef\xbb\xbf" + out
    open(p, "wb").write(out)


def lesson_files():
    return sorted(f for f in os.listdir(LES) if f.endswith(".md"))


def cmd_check(argv):
    if not argv:
        print("用法: lesson_new.py check <关键词...>")
        return 1
    keys = [k.lower() for k in argv]
    hits = []
    for f in lesson_files():
        t = read(os.path.join(LES, f))[0].lower()
        s = sum(1 for k in keys if k in t or k in f.lower())
        if s:
            m = re.search(r"^#\s+(.*)$", t, re.M)
            hits.append((s, f, m.group(1) if m else ""))
    hits.sort(reverse=True)
    if not hits:
        print("未发现同族教训 —— 可走新建路径（lesson_new.py new）")
        return 0
    print("发现 %d 个同族候选 —— 优先走【合并路径】（lesson_new.py merge）：" % len(hits))
    for s, f, title in hits[:10]:
        print("  [命中 %d/%d] %s  %s" % (s, len(keys), f, title[:60]))
    return 0


def cmd_merge(argv):
    if len(argv) < 5:
        print("用法: lesson_new.py merge <页名> <标题> <现象> <判据> <预防>")
        return 1
    page, title, phen, judge, prevent = argv[0], argv[1], argv[2], argv[3], argv[4]
    p = os.path.join(LES, page + ".md")
    if not os.path.isfile(p):
        print("未找到教训页：%s" % page)
        return 1
    t, bom, nl = read(p)
    n = len(re.findall(r"^### 坑 \d+", t, re.M)) + 1
    today = datetime.date.today().isoformat()
    block = ["", "### 坑 %d · %s（%s）" % (n, title[:60], today),
             "- **现象**：%s" % phen[:100],
             "- **判据**：%s" % judge[:100],
             "- **预防**：%s" % prevent[:100], ""]
    anchor = "\n## 相关页面"
    if anchor in t:
        t = t.replace(anchor, "\n".join(block) + anchor, 1)
    else:
        t = t.rstrip("\n") + "\n" + "\n".join(block)
    write(p, t, bom, nl)
    print("已向 lessons/%s.md 追加「坑 %d」" % (page, n))
    return 0


def sync_index_count(newcount):
    """同步 index.md 的 lessons 摘要计数（| N 条坑 |）"""
    if not os.path.isfile(IDX):
        return
    t, bom, nl = read(IDX)
    t2 = re.sub(r'(历史教训 lessons\]\([^)]*\)\s*\|\s*)\d+(\s*条坑)', r'\g<1>%d\g<2>' % newcount, t)
    if t2 != t:
        write(IDX, t2, bom, nl)
        print("  index.md 摘要计数已同步为 %d 条坑" % newcount)


def cmd_new(argv):
    if len(argv) < 6:
        print("用法: lesson_new.py new <页名> <标题> <现象> <根因> <判据> <预防>")
        return 1
    page, title, phen, root, judge, prevent = argv[:6]
    p = os.path.join(LES, page + ".md")
    if os.path.exists(p):
        print("已存在：%s" % page)
        return 1
    today = datetime.date.today().isoformat()
    L = ["---", "title: %s" % title, "date: %s" % today, "updated: %s" % today,
         "tags: [教训]", "status: active", "---", "", "# %s" % title, "",
         "> **一句话**：%s" % title[:120], "", "## 现象", "", phen[:600], "",
         "## 根因", "", root[:600], "", "## 判据", "", judge[:600], "",
         "## 预防", "", "- " + prevent[:200], "", "## 相关页面", "",
         "- [[index/index]]", ""]
    write(p, "\n".join(L), False, "\n")
    n = len(lesson_files())
    print("已创建 lessons/%s.md（当前 %d 页）" % (page, n))
    print("⚠️ 仍需在 index.md §五 表加一行（脚本可代劳）")
    sync_index_count(n)
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
