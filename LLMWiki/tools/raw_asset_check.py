#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
raw_asset_check.py —— 原始资产检索表与 raw/ 实际内容的一致性自检

判据：
  C1 本表登记的路径必须真实存在（失效 ⇒ 幻觉条目）
  C2 raw/ 下的关键资产族必须被本表登记（漏登记 ⇒ 漏用风险）
  C3 本表引用的提炼页必须是存在的 wiki 页（红链）
退出码：0 通过；1 存在违规。
"""
import os
import re
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
RAW = os.path.join(LLMWIKI, "raw")
WIKI = os.path.join(LLMWIKI, "wiki")
CATALOG = os.path.join(WIKI, "guides", "RawAssetCatalog.md")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

violations = []


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8", errors="replace").replace("\r\n", "\n")


def main():
    if not os.path.isfile(CATALOG):
        print("未找到 raw 资产检索表：%s" % CATALOG)
        return 1
    text = read(CATALOG)
    # C1/C3：抽取 `raw/...` 路径与 [[...]] 链接
    paths = set(re.findall(r'`(raw/[^`]+)`', text))
    pages = set(re.findall(r'\[\[([^\]|#]+)', text))

    print("=== C1 登记路径存在性 ===")
    for p in sorted(paths):
        if "*" in p or "<" in p:          # 通配符/占位说明，不是真实路径
            continue
        p2 = p.rstrip("/")
        if not (os.path.exists(os.path.join(LLMWIKI, p2)) or os.path.exists(os.path.join(LLMWIKI, p))):
            violations.append("登记路径不存在: %s" % p)
    print("  登记 %d 条路径，失效 %d 条" % (len(paths), sum(1 for v in violations)))

    print("=== C2 raw/ 顶层资产族登记覆盖 ===")
    fams = sorted(d for d in os.listdir(RAW) if os.path.isdir(os.path.join(RAW, d)))
    covered = set()
    for p in paths:
        parts = p.replace("\\", "/").split("/")
        if len(parts) >= 2:
            covered.add(parts[1])
    for f in fams:
        mark = "✅" if f in covered else "❌ 未登记"
        if f not in covered:
            violations.append("raw/%s 资产族未在检索表登记（漏用风险）" % f)
        print("  %-14s %s" % (f, mark))

    print("=== C3 提炼页链接有效性 ===")
    existing = set()
    for dp, dn, fn in os.walk(WIKI):
        for f in fn:
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(dp, f), WIKI).replace("\\", "/")
                existing.add(rel[:-3])
    for pg in sorted(pages):
        tgt = pg.split("|")[0].strip()
        if tgt in ("", "index/index"):
            continue
        if tgt not in existing:
            violations.append("提炼页红链: [[%s]]" % tgt)
    print("  引用 %d 个页面，失效 %d 个" % (len(pages), sum(1 for v in violations if "红链" in v)))

    print()
    if violations:
        print("违规 %d 处：" % len(violations))
        for v in violations:
            print("  " + v)
        return 1
    print("通过：raw 资产检索表与 raw/ 实际内容一致，无漏登记与红链")
    return 0


if __name__ == "__main__":
    sys.exit(main())
