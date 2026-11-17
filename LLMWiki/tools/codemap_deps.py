#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codemap_deps.py —— CodeMap 主干依附关系辅助提取（只读）

用途：扫描 AdaWeldSystem/ 源码，统计每个 .cs 文件的：
  ① 依赖的本项目命名空间（using AdaWeldSystem.*）
  ② 引用的单例 Manager（XxxManager.Instance / XxxWork.Instance）
输出候选依赖表，供人工核对/更新 CodeMap.md 的「代码记忆卡」。

⚠️ 本脚本只生成**候选事实**，不自动写 Wiki —— 主干依附由人工确认后写入总览，
   避免自动生成的内容淹没代码记忆。完整逐文件依赖请以 Step 0.7 Grep 为准。

用法：
  python tools/codemap_deps.py                 # 打印全部文件的依赖候选
  python tools/codemap_deps.py --module MotionControl   # 只看某目录
  python tools/codemap_deps.py --top 30         # 只打印依赖最多的 30 个文件
"""
import os
import re
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)               # LLMWiki/
VICODING = os.path.dirname(LLMWIKI)                # Vicoding管理平台/
WORKSPACE = os.path.dirname(VICODING)              # workbudddy/
CODE_ROOT = os.path.join(WORKSPACE, "AdaWeldSystem")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

USING_RE = re.compile(r"using\s+(AdaWeldSystem[\w.]*)\s*;")
INSTANCE_RE = re.compile(r"\b(\w+(?:Manager|Work|Control|Base))\s*\.\s*Instance\b")
EXCLUDE_DIRS = {"obj", "bin", "3rdDepend", ".vs", ".git"}


def iter_cs():
    for root, dirs, files in os.walk(CODE_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith(".cs") and not f.endswith(".Designer.cs"):
                yield os.path.join(root, f)


def main():
    args = sys.argv[1:]
    module = None
    top = None
    if "--module" in args:
        module = args[args.index("--module") + 1]
    if "--top" in args:
        top = int(args[args.index("--top") + 1])

    rows = []
    for path in iter_cs():
        rel = os.path.relpath(path, CODE_ROOT).replace("\\", "/")
        if module and module.lower() not in rel.lower():
            continue
        text = open(path, encoding="utf-8-sig", errors="replace").read()
        # strip 字符串与注释，避免误统计
        text = re.sub(r'//[^\n]*', '', text)
        text = re.sub(r'/\*[\s\S]*?\*/', '', text)
        text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
        usings = sorted(set(USING_RE.findall(text)) - {"AdaWeldSystem"})
        instances = sorted(set(INSTANCE_RE.findall(text)))
        rows.append((rel, usings, instances))

    rows.sort(key=lambda r: -(len(r[1]) + len(r[2])))
    if top:
        rows = rows[:top]

    print("CodeMap 依附候选（只读；主干以人工确认写入 CodeMap.md 为准）")
    print("文件数：%d\n" % len(rows))
    for rel, usings, instances in rows:
        print("- %s" % rel)
        if usings:
            print("    依赖命名空间: %s" % " · ".join(usings))
        if instances:
            print("    单例引用: %s" % " · ".join(instances))


if __name__ == "__main__":
    main()
