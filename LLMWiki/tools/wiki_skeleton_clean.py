#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_skeleton_clean.py —— 清理规范化误插入的「孤立尾部骨架」
判据：文件末尾连续的 `## 现象/## 根因/## 判据/## 预防/## 相关页面` 空节，
      且页面正文已有同名 `### ` 子章节（多坑结构）→ 整块删除。
退出码：0 成功；1 失败。
"""
import os
import re
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
WIKI = os.path.join(LLMWIKI, "wiki")
DRY = "--apply" not in sys.argv

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


SKELETON_H2 = ["## 现象", "## 根因", "## 判据", "## 预防"]
PLACEHOLDER = "（待补"


def clean(text):
    """删除误插入的占位骨架节（## 现象/根因/判据/预防 且内容为「（待补…）」）。
    ⚠️ 「## 相关页面」不在删除范围 —— 其下是真实链接列表。"""
    lines = text.split("\n")
    out = []
    i = 0
    removed = 0
    while i < len(lines):
        l = lines[i].strip()
        if l in SKELETON_H2:
            # 收集该节到下一个 ## 为止的内容
            j = i + 1
            seg = []
            while j < len(lines) and not lines[j].startswith("## "):
                seg.append(lines[j])
                j += 1
            body = "\n".join(seg)
            if PLACEHOLDER in body:          # 确认是占位骨架
                # 连同其前的空行一起删
                while out and not out[-1].strip():
                    out.pop()
                removed += 1
                i = j
                continue
        out.append(lines[i])
        i += 1
    if not removed:
        return text, False
    new = "\n".join(out)
    new = re.sub(r'\n{3,}', '\n\n', new)
    return new.rstrip("\n") + "\n", True


def main():
    n = 0
    for cat in ("lessons", "decisions", "modules", "api", "guides", "standards", "project", "people", "architecture"):
        d = os.path.join(WIKI, cat)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md"):
                continue
            p = os.path.join(d, f)
            text, bom, nl = rd(p)
            new, c = clean(text)
            if c:
                if not DRY:
                    wr(p, new, bom, nl)
                n += 1
                print(f"  {cat}/{f}")
    print(f"\n清理孤立骨架：{n} 文件 {'(DRY)' if DRY else '已写盘'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
