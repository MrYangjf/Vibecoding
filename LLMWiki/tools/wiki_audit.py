# -*- coding: utf-8 -*-
"""LLMWiki 全库体检脚本：红链 / 孤儿页 / 索引重复行 / ADR 编号空洞 / 体积分布 / 内容重复度。
只读扫描，不修改任何文件。"""
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = os.path.join(ROOT, "wiki")

link_re = re.compile(r"\[\[([^\]\|#]+)")
alias_re = re.compile(r"\[\[([^\]]+)\]\]")

# 文档中的「示例占位符」链接，不是真实页面引用，不算红链（2026-09-01 治理时梳理）
PLACEHOLDERS = {
    "引用页面", "相关页面", "页面名", "引用", "references", "reference",
    "提到但没有专属页面的概念", "lessons/...", "...",
}


def is_placeholder(raw):
    if raw in PLACEHOLDERS:
        return True
    if "..." in raw:
        return True
    # 全大写 X / Y 形式的示例名：ADR-XXX、lessons/XXX、modules/YYY
    for part in raw.split("/"):
        if part and re.fullmatch(r"[XY]{2,}", part):
            return True
        if re.fullmatch(r"[A-Z]+-[X]{2,}", part):
            return True
    return False


def walk_md(base):
    out = []
    for dp, dn, fn in os.walk(base):
        for f in fn:
            if f.lower().endswith(".md"):
                out.append(os.path.join(dp, f))
    return sorted(out)


all_files = walk_md(ROOT)
wiki_files = [f for f in all_files if os.path.abspath(f).startswith(os.path.abspath(WIKI))]

rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")

pages = {}          # logical name -> abs path
for f in wiki_files:
    r = rel(f)
    key = r[len("wiki/"):-3] if r.startswith("wiki/") else r[:-3]
    pages[key] = f

# ---------- 1. 红链 ----------
red = defaultdict(list)
placeholder = defaultdict(list)
inbound = defaultdict(set)
for f in all_files:
    src = rel(f)
    try:
        txt = open(f, encoding="utf-8-sig").read()
    except Exception:
        continue
    for m in link_re.finditer(txt):
        raw = m.group(1).strip()
        if is_placeholder(raw):
            placeholder[src].append(raw)
            continue
        key = raw.split("/")[-1] if "/" in raw else raw
        full = raw if raw.startswith(("wiki/", "raw/", "logs/")) else None
        # 解析目标
        if raw.startswith("wiki/"):
            target = raw[len("wiki/"):]
        elif raw.startswith("raw/") or raw.startswith("logs/"):
            continue  # 非 wiki 页面
        elif "/" in raw:
            target = raw
        else:
            # 裸名：尝试常见目录
            cands = [k for k in pages if k.split("/")[-1] == raw]
            if len(cands) == 1:
                target = cands[0]
            elif len(cands) > 1:
                target = cands[0]
            else:
                target = None
        if target is None or target not in pages:
            red[src].append(raw)
        else:
            inbound[target].add(src)

print("=" * 70)
print("1. 红链（[[引用]] 指向不存在的 wiki 页面）")
print("=" * 70)
if not red:
    print("  无（健康）")
for src, targets in sorted(red.items()):
    for t in sorted(set(targets)):
        print("  %-58s -> [[%s]]" % (src, t))
print()
print("  附：示例占位符链接（非红链，已白名单）：")
for src, targets in sorted(placeholder.items()):
    print("  %-58s -> %s" % (src, ", ".join(sorted(set(targets)))))

# ---------- 2. 孤儿页（wiki/ 下无入链）----------
print()
print("=" * 70)
print("2. 孤儿页（wiki/ 下无任何页面引用）")
print("=" * 70)
orph = [k for k in pages if k not in inbound]
if not orph:
    print("  无")
for k in sorted(orph):
    print("  %-58s (入链 0)" % k)

# ---------- 3. index.md 重复行 / 表头重复 ----------
print()
print("=" * 70)
print("3. index.md 重复条目行")
print("=" * 70)
idx = os.path.join(WIKI, "index", "index.md")
lines = open(idx, encoding="utf-8-sig").read().splitlines()
seen = defaultdict(list)
for i, ln in enumerate(lines, 1):
    s = ln.strip()
    if s.startswith("| [[") and s.endswith("|"):
        cell = s.split("|")[1].strip()
        m = link_re.search(cell)
        if m:
            seen[m.group(1).strip()].append(i)
dup = {k: v for k, v in seen.items() if len(v) > 1}
if not dup:
    print("  无")
for k, v in sorted(dup.items()):
    print("  [[%s]] 重复 %d 次：行 %s" % (k, len(v), v))

print()
print("--- index.md 结构统计 ---")
blocks = 0
prev_tbl = False
for ln in lines:
    is_tbl = ln.strip().startswith("|")
    if is_tbl and not prev_tbl:
        blocks += 1
    prev_tbl = is_tbl
hdr = sum(1 for ln in lines if ln.strip().startswith("| 页面 | 摘要 | 标签 |"))
print("  连续表格块数：%d（按设计分组，非碎片则健康）" % blocks)
print("  '| 页面 | 摘要 | 标签 |' 表头出现次数：%d" % hdr)
print("  场景速查路由表：%s" % ("有" if "场景速查路由" in "\n".join(lines) else "**缺失**"))

# ---------- 4. ADR 编号空洞 ----------
print()
print("=" * 70)
print("4. ADR 编号连续性")
print("=" * 70)
nums = set()
for k in pages:
    m = re.match(r"decisions/ADR-(\d+)-", k)
    if m:
        nums.add(int(m.group(1)))
lo, hi = min(nums), max(nums)
missing = [n for n in range(lo, hi + 1) if n not in nums]
print("  已存在编号：%d ~ %d（共 %d 个）" % (lo, hi, len(nums)))
print("  空洞编号：%s" % (missing if missing else "无"))
# index 是否登记全部 ADR
idx_txt = open(idx, encoding="utf-8-sig").read()
not_in_idx = sorted(["ADR-%03d" % n for n in nums if "ADR-%03d-" % n not in idx_txt])
print("  已存在但未登记进 index：%s" % (not_in_idx if not_in_idx else "无"))

# ---------- 5. 体积分布 ----------
print()
print("=" * 70)
print("5. wiki/ 页面体积分布（行数）")
print("=" * 70)
sizes = []
for k, p in pages.items():
    n = len(open(p, encoding="utf-8-sig", errors="ignore").read().splitlines())
    sizes.append((n, k))
sizes.sort(reverse=True)
for n, k in sizes[:15]:
    has_toc = "章节导航" in open(pages[k], encoding="utf-8-sig", errors="ignore").read()
    if n > 600:
        flag = "  <== 超大页，" + ("已加 TOC ✅" if has_toc else "**缺 TOC ❌（须加章节导航或拆分）**")
    else:
        flag = ""
    print("  %5d  %s%s" % (n, k, flag))
print("  ... 合计 %d 页，总 %d 行，均值 %d 行" % (len(sizes), sum(s[0] for s in sizes), sum(s[0] for s in sizes) // max(1, len(sizes))))

# ---------- 6. 内容重复度（标题级 Jaccard，阈值 0.6）----------
print()
print("=" * 70)
print("6. 疑似内容重复页（正文 3-gram 相似度 > 0.35）")
print("=" * 70)
def shingles(p):
    txt = open(p, encoding="utf-8-sig", errors="ignore").read()
    txt = re.sub(r"```.*?```", " ", txt, flags=re.S)
    txt = re.sub(r"\|", " ", txt)
    txt = re.sub(r"\s+", "", txt)
    return set(txt[i:i + 12] for i in range(0, max(0, len(txt) - 12), 4))

keys = sorted(pages)
sh = {}
for k in keys:
    try:
        sh[k] = shingles(pages[k])
    except Exception:
        sh[k] = set()
found = False
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        a, b = sh[keys[i]], sh[keys[j]]
        if not a or not b:
            continue
        inter = len(a & b)
        sim = inter / float(min(len(a), len(b)))
        if sim > 0.35:
            print("  %.2f  %s  <=>  %s" % (sim, keys[i], keys[j]))
            found = True
if not found:
    print("  无")

# ---------- 7. lessons 中疑似「指导文件」而非「教训」----------
print()
print("=" * 70)
print("7. lessons/ 中文件名含 Guide/Reference/Manual 的「指导型」页面（位置存疑）")
print("=" * 70)
for k in sorted(pages):
    if k.startswith("lessons/"):
        base = k.split("/")[-1]
        if re.search(r"Guide|Reference|Manual|Complete", base, re.I):
            n = len(open(pages[k], encoding="utf-8-sig", errors="ignore").read().splitlines())
            print("  %-52s %d 行" % (k, n))

print()
print("=" * 70)
print("8. standards/ 页面（2026-09-01 起平铺，禁止子目录）")
print("=" * 70)
for k in sorted(pages):
    if k.startswith("standards/"):
        n = len(open(pages[k], encoding="utf-8-sig", errors="ignore").read().splitlines())
        inc = len(inbound.get(k, []))
        print("  %-56s %4d 行  入链 %d" % (k, n, inc))

print()
print("=" * 70)
print("9. wiki/ 子目录检测（应为空——各分类一律平铺为 .md 文件）")
print("=" * 70)
# 一级分类目录是允许的（standards/、lessons/ …），禁止的是「分类下的二级子目录」
subs = []
for cat in sorted(os.listdir(WIKI)):
    cat_path = os.path.join(WIKI, cat)
    if not os.path.isdir(cat_path):
        continue
    for dp, dn, fn in os.walk(cat_path):
        if os.path.abspath(dp) == os.path.abspath(cat_path):
            continue
        subs.append(os.path.relpath(dp, WIKI).replace("\\", "/"))
for s in sorted(subs):
    print("  ❌ 发现二级子目录：%s" % s)
print("  一级分类目录：%d 个" % len([c for c in os.listdir(WIKI) if os.path.isdir(os.path.join(WIKI, c))]))
if not subs:
    print("  ✅ 无二级子目录，全库平铺合规")

print()
print("=" * 70)
print("10. 小分类检测（页数 <= 2 的一级分类，建议并入相近分类）")
print("=" * 70)
# 背景：2026-09-01 曾出现 architecture/(1 页) 与 archive/(2 页) 两个极小分类，
# 且名字相近易混，已合并为 architecture/。
# 豁免：index/ 是单页全库索引；architecture/ 虽只 1 页，但它是全项目架构唯一
# 真相源（598 行、53 处入链），独立分类便于检索，属设计内例外——不要合并掉。
EXEMPT = {"index", "architecture"}
small = []
for cat in sorted(os.listdir(WIKI)):
    cat_path = os.path.join(WIKI, cat)
    if not os.path.isdir(cat_path) or cat in EXEMPT:
        continue
    n = len([f for f in os.listdir(cat_path) if f.endswith(".md")])
    if n <= 2:
        small.append((cat, n))
for cat, n in small:
    print("  ⚠️ %-24s %d 页 —— 分类过小，考虑并入相近分类" % (cat + "/", n))
if not small:
    print("  ✅ 无过小分类（>2 页 / 或已在豁免名单）")
