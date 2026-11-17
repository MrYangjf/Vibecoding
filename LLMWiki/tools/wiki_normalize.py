#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_normalize.py —— ADR / lessons 页的【结构规范化】（补齐 frontmatter 与必需章节骨架）

原则：
  · 只【补】不【删】：缺失的 frontmatter 字段按规则填；缺失的章节追加占位骨架（标注「（待补）」）
  · 已有内容一律保留，位置不动
  · 章节插入顺序：按规范顺序插到「## 相关页面」之前；无该节则追加到文末
  · 字节级安全：保持 BOM / CRLF / LF 同质
退出码：0 成功；1 失败。
"""
import os
import re
import sys
import datetime

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


TODAY = datetime.date.today().isoformat()

ADR_SECTIONS = ["## 背景", "## 决策", "## 备选方案", "## 后果", "## 相关页面"]
ADR_SKELETON = {
    "## 背景": ["", "（待补：本决策要解决什么问题）", ""],
    "## 决策": ["", "1. （待补）", ""],
    "## 备选方案": ["", "- （待补：考虑过什么、为什么放弃）", ""],
    "## 后果": ["", "### 正面", "- （待补）", "", "### 负面", "- （待补）", ""],
    "## 相关页面": ["", "- [[decisions/ADR-Index]]", ""],
}
LESSON_SECTIONS = ["## 现象", "## 根因", "## 判据", "## 预防", "## 相关页面"]
LESSON_SKELETON = {
    "## 现象": ["", "（待补：症状）", ""],
    "## 根因": ["", "（待补：为什么）", ""],
    "## 判据": ["", "- （待补：可机械检查的判据）", ""],
    "## 预防": ["", "- （待补）", ""],
    "## 相关页面": ["", "- [[index/index]]", ""],
}


def normalize_frontmatter(text, kind, slug_hint, title_hint):
    """确保 frontmatter 完整且字段有序；返回 (新正文, 是否改动)
    ⚠️ BOM 陷阱：带 BOM 的文件首行是 '\\ufeff---'，判定前必须先剥 BOM，否则会误判为「无 frontmatter」"""
    lines = text.split("\n")
    if lines and lines[0].startswith("\ufeff"):
        lines[0] = lines[0][1:]
    fm = {}
    body_start = 0
    if lines and lines[0].strip() == "---":
        end = None
        for i in range(1, min(40, len(lines))):
            if lines[i].strip() == "---":
                end = i
                break
        if end:
            for l in lines[1:end]:
                if ":" in l:
                    k = l.split(":", 1)[0].strip()
                    if k:
                        fm[k] = l.split(":", 1)[1].strip()
            body_start = end + 1
    else:
        body_start = 0
    order = ["title", "date", "updated", "tags", "status"]
    default = {
        "title": title_hint,
        "date": TODAY,
        "updated": TODAY,
        "tags": "[决策]" if kind == "adr" else "[教训]",
        "status": "accepted" if kind == "adr" else "active",
    }
    changed = False
    for k in order:
        if not fm.get(k):
            fm[k] = default[k]
            changed = True
    if kind == "adr" and "title" in fm and "ADR-" not in fm["title"] and slug_hint:
        fm["title"] = "%s %s" % (slug_hint, fm["title"])
        changed = True
    out = ["---"]
    for k in order:
        out.append("%s: %s" % (k, fm[k]))
    for k, v in fm.items():
        if k not in order:
            out.append("%s: %s" % (k, v))
    out.append("---")
    out.append("")
    return "\n".join(out) + "\n".join(lines[body_start:]), changed


def normalize_sections(text, sections, skeleton):
    """仅在【整页完全没有该章节】时插入骨架。
    ⚠️ 已存在同类子章节（如 lessons 的 '### 现象'）的多坑页面，不得追加尾部骨架 —— 那会产生孤立空节。"""
    changed = False
    for sec in sections:
        if re.search(r"^%s\s*$" % re.escape(sec), text, re.M):
            continue
        # 已有同名子章节（### 现象 等）→ 该页是多坑结构，不追加尾部骨架
        sub = sec.replace("## ", "### ")
        if re.search(r"^%s\s*$" % re.escape(sub), text, re.M):
            continue
        changed = True
        block = [sec] + skeleton[sec]
        anchor = "\n## 相关页面"
        if anchor in text:
            text = text.replace(anchor, "\n" + "\n".join(block) + anchor, 1)
        else:
            text = text.rstrip("\n") + "\n\n" + "\n".join(block)
    return text, changed


def main():
    stats = {"adr": 0, "lesson": 0, "files": 0}
    dec = os.path.join(WIKI, "decisions")
    for f in sorted(os.listdir(dec)):
        m = re.match(r"ADR-(\d{3})-(.*)\.md$", f)
        if not m:
            continue
        p = os.path.join(dec, f)
        text, bom, nl = rd(p)
        no = m.group(1); slug = m.group(2)
        h1 = re.search(r"^#\s+(.+)$", text, re.M)
        title_hint = ("ADR-%s %s" % (no, slug)) if not h1 else h1.group(1).strip()
        new, c1 = normalize_frontmatter(text, "adr", "ADR-%s" % no, title_hint)
        new, c2 = normalize_sections(new, ADR_SECTIONS, ADR_SKELETON)
        if c1 or c2:
            if not DRY:
                wr(p, new, bom, nl)
            stats["adr"] += 1
            stats["files"] += 1
    les = os.path.join(WIKI, "lessons")
    for f in sorted(os.listdir(les)):
        if not f.endswith(".md"):
            continue
        p = os.path.join(les, f)
        text, bom, nl = rd(p)
        h1 = re.search(r"^#\s+(.+)$", text, re.M)
        title_hint = h1.group(1).strip() if h1 else f[:-3]
        new, c1 = normalize_frontmatter(text, "lesson", None, title_hint)
        new, c2 = normalize_sections(new, LESSON_SECTIONS, LESSON_SKELETON)
        if c1 or c2:
            if not DRY:
                wr(p, new, bom, nl)
            stats["lesson"] += 1
            stats["files"] += 1
    print("规范化：ADR %d 页 + lessons %d 页 = 共 %d 文件 %s" % (
        stats["adr"], stats["lesson"], stats["files"], "(DRY)" if DRY else "已写盘"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
