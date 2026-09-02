# -*- coding: utf-8 -*-
"""代码漂移检测：比对 wiki 文档中记录的 .cs 文件与 AdaWeldSystem/ 实际代码"""
import os
import re
import glob

WIKI = r"D:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\workbudddy\Vicoding管理平台\LLMWiki\wiki"
CODE = r"D:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\workbudddy\AdaWeldSystem"

# 收集代码中所有 .cs 文件（相对路径，小写）
code_files = set()
for root, _, files in os.walk(CODE):
    if "bin" in root or "obj" in root or "3rdDepend" in root:
        continue
    for f in files:
        if f.endswith(".cs"):
            rel = os.path.relpath(os.path.join(root, f), CODE).replace("\\", "/")
            code_files.add(rel)
            code_files.add(os.path.basename(f))

# 从 wiki 文档中提取 .cs 文件名引用
cs_ref_re = re.compile(r"([A-Za-z0-9_]+\.cs)")
missing = []
found = []
for p in glob.glob(os.path.join(WIKI, "**", "*.md"), recursive=True):
    with open(p, encoding="utf-8-sig") as fh:
        content = fh.read()
    for m in cs_ref_re.finditer(content):
        fname = m.group(1)
        # 只检查看起来像真实代码文件的引用（排除模板示例）
        if fname in ("XXX.cs", "YYY.cs", "Title.cs", "AAA.cs", "BBB.cs"):
            continue
        if fname in code_files:
            found.append((os.path.relpath(p, WIKI), fname))
        else:
            missing.append((os.path.relpath(p, WIKI), fname))

# 去重
missing = sorted(set(missing))
found = sorted(set(found))

print("=" * 60)
print("代码漂移检测结果")
print("=" * 60)
print(f"代码库 .cs 文件总数: {len(code_files)}")
print(f"wiki 中引用且存在的 .cs 文件: {len(found)}")
print(f"\n[漂移] wiki 引用但代码中不存在的 .cs 文件: {len(missing)}")
for src, fname in missing:
    print(f"  - {src} -> {fname}")
print("=" * 60)
