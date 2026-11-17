#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_toc.py —— 为超大页自动生成「章节导航」TOC（wiki_audit 体积检查要求）

判据：页行数 > 阈值 且 尚无「章节导航」段 → 在 H1 之后插入 TOC。
TOC 列出全部 '## ' 级标题（带行内锚点）。
退出码：0 成功；1 失败。
"""
import os
import re
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
WIKI = os.path.join(LLMWIKI, "wiki")
DRY = "--apply" not in sys.argv
THRESHOLD = 600

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def rd(p):
    b = open(p, "rb").read()
    bom = b[:3] == b"\xef\xbb\xbf"
    body = b[3:] if bom else b
    crlf = body.count(b"\r\n")
    lf = body.count(b"\n") - crlf
    return body.decode("utf-8", errors="replace").replace("\r\n", "\n"), bom, ("\r\n" if crlf > lf else "\n")


def wr(p, t, bom, nl):
    out = t.replace("\r\n", "\n").replace("\n", nl).encode("utf-8")
    if bom:
        out = b"\xef\xbb\xbf" + out
    open(p, "wb").write(out)


def anchor(t):
    s = t.strip().lower()
    s = re.sub(r"[^\w\u4e00-\u9fff\s-]", "", s)
    return s.replace(" ", "-")


def process(rel):
    p = os.path.join(WIKI, rel)
    text, bom, nl = rd(p)
    lines = text.split("\n")
    if len(lines) <= THRESHOLD:
        return False
    if any(l.startswith("## 章节导航") for l in lines):
        return False
    heads = [(i, l) for i, l in enumerate(lines) if re.match(r"^##\s+\S", l)]
    if len(heads) < 3:
        return False
    toc = ["## 章节导航", ""]
    for i, h in heads:
        title = h[3:].strip()
        toc.append("- [%s](#%s)" % (title[:60], anchor(title)))
    toc.append("")
    # 插入位置：H1 之后（跳过 frontmatter 与抬头说明），取 H1 后的第一个空行之后
    h1 = next((i for i, l in enumerate(lines) if re.match(r"^#\s+\S", l)), None)
    if h1 is None:
        return False
    ins = h1 + 1
    while ins < len(lines) and not lines[ins].strip():
        ins += 1
    new = lines[:ins] + [""] + toc + lines[ins:]
    wr(p, "\n".join(new), bom, nl)
    return True


def main():
    n = 0
    for cat in sorted(os.listdir(WIKI)):
        d = os.path.join(WIKI, cat)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md"):
                continue
            rel = os.path.join(cat, f)
            if process(rel):
                n += 1
                print("  +TOC %s" % rel)
    print("\n生成 TOC：%d 页 %s" % (n, "(DRY)" if DRY else "已写盘"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
