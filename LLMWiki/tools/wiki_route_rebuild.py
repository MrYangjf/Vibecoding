#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_route_rebuild.py —— 从【结构化路由源】重建速查路由表（脚本化，杜绝手工维护与截断损坏）

路由源：wiki/index/routes.tsv —— 每行「场景描述 \t 目标页链接 \t 硬约束提示(≤80字符)」
本脚本：读 TSV → 生成 markdown 表格 → 校验（链接括号平衡 / 第三列长度 / 无日期 / 无删除线）
子命令：build（默认） | check
"""
import os
import re
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
IDX = os.path.join(LLMWMWIKI := os.path.join(LLMWIKI, "wiki"), "index", "index.md")
TSV = os.path.join(TOOLS_DIR, "data", "routes.tsv")
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


def load_routes():
    rows = []
    if not os.path.isfile(TSV):
        return rows
    for line in read(TSV)[0].split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        rows.append((parts[0].strip(), parts[1].strip(), parts[2].strip()))
    return rows


def check(rows):
    bad = 0
    for i, (a, b, c) in enumerate(rows, 1):
        if b.count("[[") != b.count("]]"):
            print("  行%d 链接括号失衡: %s" % (i, b)); bad += 1
        if len(c) > LIMIT:
            print("  行%d 第三列 %d 字符 > %d: %s" % (i, len(c), LIMIT, c[:70])); bad += 1
        if re.search(r'20\d\d-\d\d-\d\d', c):
            print("  行%d 第三列含日期: %s" % (i, c[:70])); bad += 1
        if '~~' in c:
            print("  行%d 第三列含删除线" % i); bad += 1
        for col, nm in ((a, '第1列'), (b, '第2列'), (c, '第3列')):
            if col.count("[[") != col.count("]]"):
                print("  行%d %s 链接括号失衡: %s" % (i, nm, col[:70])); bad += 1
    print("  路由行数 %d，问题 %d" % (len(rows), bad))
    return bad


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    rows = load_routes()
    if not rows:
        print("未找到路由源 %s" % TSV)
        return 1
    print("路由源：%s（%d 行）" % (TSV, len(rows)))
    bad = check(rows)
    if cmd == "check":
        return 1 if bad else 0
    if bad:
        print("⛔ 路由源有问题，未写盘")
        return 1
    t, bom, nl = read(IDX)
    lines = t.split("\n")
    s = next(i for i, l in enumerate(lines) if l.startswith("## ⚡ 场景速查路由"))
    e = next((i for i, l in enumerate(lines[s + 1:], s + 1) if l.startswith("## ")), len(lines))
    # 只替换表体行；⛔ 保留章节标题与说明行（此前实现用 lines[:s] 会把标题一起吃掉）
    ti = None
    te = None
    for i in range(s + 1, e):
        if lines[i].startswith("|"):
            if ti is None:
                ti = i
            te = i
        elif ti is not None:
            break
    if ti is None:
        print("⛔ 未找到速查路由表体，未写盘")
        return 1
    tbl = ["| 你要做的事 | 直接读这 1~3 页 | 硬约束提示 |", "|---|---|---|"]
    for a, b, c in rows:
        tbl.append("| %s | %s | %s |" % (a, b, c))
    out = lines[:ti] + tbl + lines[te + 1:]
    write(IDX, "\n".join(out), bom, nl)
    print("已重建速查路由表：%d 行（章节标题保留）" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
