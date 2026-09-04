# -*- coding: utf-8 -*-
"""LLMWiki Phase 4 Lint 扫描脚本：死链 / 孤儿页面 / ADR 编号冲突 / 外链完整性"""
import os
import re
import sys

# 2026-09-03：原为硬编码旧机器绝对路径（D:\A-A-项目类\...），迁移后必然 FileNotFoundError。
# 改为与 tools/wiki_audit.py 同款写法，按脚本自身位置推导，保证任意机器上可直接运行。
WIKI_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")
INDEX_FILE = os.path.join(WIKI_ROOT, "index", "index.md")

def walk_md(root):
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)

def rel_path(p):
    return os.path.relpath(p, WIKI_ROOT).replace("\\", "/")

# 收集所有实际存在的页面（相对路径，无扩展名，如 modules/Comm）
existing = set()
for p in walk_md(WIKI_ROOT):
    r = rel_path(p)
    existing.add(r)
    existing.add(r[:-3])  # 去 .md

# 解析 [[...]] 链接
link_re = re.compile(r"\[\[([^\]]+)\]\]")

# 2026-09-03：与 tools/wiki_audit.py 的 mask_code 同款。规范文档里举反面例子时
# 常写「不要写 `[[old]]→[[new]]`」，方括号落在行内代码体里仍会被当真链接解析，
# 产生 4 条假红链。链接解析前先屏蔽代码块与行内代码体；用等长空白替换而非删除，
# 可保持字符偏移与行号不变。
_FENCE_RE = re.compile(r"```.*?```", re.S)
_INLINE_RE = re.compile(r"`[^`\n]*`")


def mask_code(txt):
    """把围栏代码块与行内代码体替换为等长空白，保持偏移与行号不变。"""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))
    return _INLINE_RE.sub(blank, _FENCE_RE.sub(blank, txt))


def parse_links(text):
    links = []
    for m in link_re.finditer(mask_code(text)):
        target = m.group(1).strip()
        # 去掉锚点 #xxx
        target = target.split("#")[0].strip()
        # 去掉显示文本 |xxx
        target = target.split("|")[0].strip()
        links.append(target)
    return links

dead_links = []
all_pages = []
for p in walk_md(WIKI_ROOT):
    all_pages.append(p)
    with open(p, encoding="utf-8-sig") as fh:
        content = fh.read()
    for target in parse_links(content):
        if not target:
            continue
        # 候选解析：原样、加 .md、加路径前缀
        candidates = [target, target + ".md"]
        if "/" not in target:
            candidates += ["modules/" + target, "api/" + target,
                           "decisions/" + target, "lessons/" + target,
                           "people/" + target, "project/" + target,
                           "architecture/" + target]
        resolved = False
        for c in candidates:
            if c in existing:
                resolved = True
                break
        if not resolved:
            dead_links.append((rel_path(p), target))

# 孤儿页面：未被 index.md 索引的页面
with open(INDEX_FILE, encoding="utf-8-sig") as fh:
    index_content = fh.read()

orphans = []
for p in walk_md(WIKI_ROOT):
    if p == INDEX_FILE:
        continue
    r = rel_path(p)
    base = r[:-3]  # 去 .md
    # 检查 index 中是否出现该页面名（带路径或纯文件名）
    name = base.split("/")[-1]
    if base not in index_content and name not in index_content:
        orphans.append(r)

# ADR 编号冲突检测
adr_files = [p for p in walk_md(WIKI_ROOT) if p.startswith(os.path.join(WIKI_ROOT, "decisions"))]
adr_nums = {}
for p in adr_files:
    name = os.path.basename(p)
    m = re.match(r"ADR-(\d+)-", name)
    if m:
        num = int(m.group(1))
        adr_nums.setdefault(num, []).append(rel_path(p))

adr_conflicts = {k: v for k, v in adr_nums.items() if len(v) > 1}

# 外部文件链接检测（相对路径引用，非 http）
ext_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ext_issues = []
for p in walk_md(WIKI_ROOT):
    with open(p, encoding="utf-8-sig") as fh:
        content = fh.read()
    for m in ext_re.finditer(content):
        url = m.group(2).strip()
        if url.startswith("http") or url.startswith("#") or url.startswith("mailto"):
            continue
        # 去掉锚点
        path_part = url.split("#")[0].strip()
        if not path_part:
            continue
        # 相对 wiki 根解析
        cand = os.path.normpath(os.path.join(os.path.dirname(p), path_part))
        if not os.path.exists(cand):
            ext_issues.append((rel_path(p), url))

print("=" * 60)
print("LINT 扫描结果")
print("=" * 60)
print(f"扫描页面总数: {len(all_pages)}")
print(f"\n[1] 死链检测 ([[...]] 指向不存在页面): {len(dead_links)}")
for src, tgt in dead_links:
    print(f"  - {src} -> [[{tgt}]]")
print(f"\n[2] 孤儿页面检测 (未被 index.md 索引): {len(orphans)}")
for o in orphans:
    print(f"  - {o}")
print(f"\n[3] ADR 编号冲突: {len(adr_conflicts)}")
for k, v in adr_conflicts.items():
    print(f"  - ADR-{k:03d}: {v}")
print(f"\n[4] 外部文件链接失效: {len(ext_issues)}")
for src, url in ext_issues:
    print(f"  - {src} -> {url}")
print("=" * 60)
