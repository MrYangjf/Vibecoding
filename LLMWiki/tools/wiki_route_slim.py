#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_route_slim.py —— 速查路由表瘦身（按 WikiPageFormatSpec §2.1）
【安全铁律】绝不切断 [[...]] 链接：截断时保留完整链接单元，其余以「…」省略。

处理：
  1) 删除线 ~~X~~ → X
  2) 剥离纯沿革括注（含日期的「已废弃/已删除/已移除/归档/并入」括注）
  3) 连续标点/空白收敛
  4) 超长则按「链接单元」为最小单位截断（不切断链接）
退出码：0 成功；1 失败。
"""
import os
import re
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
IDX = os.path.join(LLMWIKI, "wiki", "index", "index.md")
LIMIT = 80

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


LINK = re.compile(r'\[\[[^\]]+\]\]')


def slim(cell):
    s = cell
    s = re.sub(r'~~([^~]*)~~', r'\1', s)
    # 剥离含日期或含「已废弃/已删除/已移除/归档」纯沿革括注
    for _ in range(3):
        s2 = re.sub(r'（[^（）]{0,60}(?:20\d\d-\d\d-\d\d|已废弃|已删除|已移除|已退役|归档)[^（）]{0,60}）', '', s)
        if s2 == s:
            break
        s = s2
    s = re.sub(r'\s*[，、；]\s*', ' · ', s)
    s = re.sub(r'\s*·\s*·\s*', ' · ', s)
    s = re.sub(r'\s{2,}', ' ', s).strip()
    s = re.sub(r'\s*·\s*([：:）)])', r'\1', s)
    s = s.rstrip(' ·')
    if len(s) <= LIMIT:
        return s
    # 按链接单元截断（绝不切断 [[...]]）
    units = LINK.split(s)          # 偶数位为链接
    kept = ''
    for i in range(0, len(units), 2):
        piece = units[i]
        link = units[i + 1] if i + 1 < len(units) else ''
        if not link:
            if len(kept) + len(piece) > LIMIT - 1:
                break
            kept += piece
            continue
        if len(kept) + len(piece) + len(link) > LIMIT - 1:
            # 链接本身放不下 → 只保留纯文本部分
            room = LIMIT - 1 - len(kept) - len(piece)
            if room > 8:
                kept += piece[:room].rstrip(' ·') + '…'
            break
        kept += piece + link
    kept = kept.rstrip(' ·') + '…'
    return kept


def main():
    t, bom, nl = read(IDX)
    lines = t.split("\n")
    s = next(i for i, l in enumerate(lines) if l.startswith("## ⚡ 场景速查路由"))
    e = next((i for i, l in enumerate(lines[s + 1:], s + 1) if l.startswith("## ")), len(lines))
    changed = 0
    for i in range(s, e):
        l = lines[i]
        if not l.startswith("|") or '---' in l:
            continue
        cells = [c.strip() for c in l.strip('|').split('|')]
        if len(cells) < 3:
            continue
        new3 = slim(cells[2])
        if new3 != cells[2]:
            lines[i] = "| " + " | ".join(cells[:2] + [new3]) + " |"
            changed += 1
    write(IDX, "\n".join(lines), bom, nl)
    print("速查路由表第三列压缩：%d 行" % changed)
    # 结构自检：每行 [[ 与 ]] 数量必须相等
    bad = []
    t2, _, _ = read(IDX)
    L = t2.split("\n")
    for i, l in enumerate(L, 1):
        if l.count("[[") != l.count("]]"):
            bad.append((i, l[:110]))
    print("  链接括号失衡行: %d" % len(bad))
    for i, l in bad[:10]:
        print("    L%d: %s" % (i, l))
    over = []
    s2 = next(i for i, l in enumerate(L) if l.startswith("## ⚡ 场景速查路由"))
    e2 = next((i for i, l in enumerate(L[s2 + 1:], s2 + 1) if l.startswith("## ")), len(L))
    for i in range(s2, e2):
        l = L[i]
        if l.startswith("|") and '---' not in l:
            c = [x.strip() for x in l.strip('|').split('|')]
            if len(c) >= 3 and len(c[2]) > LIMIT:
                over.append((i + 1, len(c[2]), l[:100]))
    print("  第三列超限: %d 行" % len(over))
    for i, n, l in over[:6]:
        print("    L%d (%d): %s" % (i, n, l))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
