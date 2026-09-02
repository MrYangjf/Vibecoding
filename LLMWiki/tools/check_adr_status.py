# -*- coding: utf-8 -*-
"""检查所有 ADR 的 frontmatter status/superseded_by 字段"""
import os, re, glob

DEC = r"D:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\workbudddy\Vicoding管理平台\LLMWiki\wiki\decisions"

for f in sorted(glob.glob(os.path.join(DEC, "*.md"))):
    with open(f, encoding="utf-8-sig") as fh:
        content = fh.read()
    # 提取 frontmatter
    m = re.match(r"^---\n(.*?)\n---", content, re.S)
    fm = m.group(1) if m else ""
    status = re.search(r"^status:\s*(.+)$", fm, re.M)
    superseded = re.search(r"^superseded_by:\s*(.+)$", fm, re.M)
    name = os.path.basename(f)
    print(f"{name:<55} status={status.group(1).strip() if status else 'N/A':<12} superseded_by={superseded.group(1).strip() if superseded else ''}")
