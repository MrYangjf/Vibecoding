#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_narrative_strip.py —— ADR 页「验证叙事」剥离（详细过程移入 log，结论与约束留在 ADR）

判据（对应 WikiPageFormatSpec §2.2）：
  · 「静态 N/N PASS」「阴性对照 a/b」这类**过程结果** → 剥离（属 log）
  · 「探针实测：具体尺寸/数值」这类**实测数据** → 保留结论（尺寸是约束），去掉过程措辞
  · 「探针法」「一律探针实测」这类**方法论约束** → 完整保留（是决策的一部分）
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


def strip_line(l):
    """返回 (新行, 是否改动, 剥离原因)"""
    orig = l
    # 1) 静态校验结果行（整行是过程记录）→ 删除该行
    if re.match(r'^\s*[-*]?\s*\*\*静态校验\*\*', l) or re.match(r'^\s*[-*]?\s*静态校验[:：]', l):
        return "", True, "静态校验结果行"
    # 2) 行内「静态 N/N PASS（阴性对照 a/b）」→ 删除该括注
    l = re.sub(r'[（(]\s*(?:阴性对照[^）)]*)?\s*(?:PASS|通过)[^）)]*[）)]', '', l)
    l = re.sub(r'\s*·?\s*静态校验[:：]\s*\d+/\d+\s*PASS', '', l)
    l = re.sub(r'\s*·?\s*阴性对照\s*\d+/\d+', '', l)
    # 3) 「探针实测确认/探针抓到」→ 保留结论，去掉过程措辞
    l = l.replace('（探针实测确认）', '（实测确认）')
    l = re.sub(r'探针实测\*\*', '实测**', l)
    l = re.sub(r'探针实测', '实测', l)
    l = re.sub(r'几何探针', '几何实测', l)
    l = re.sub(r'\s*·?\s*探针法', ' 实测法', l)
    l = re.sub(r'（实测法）', '（实测法）', l)
    # 4) 清理残留空标点
    l = re.sub(r'\s*·\s*(?=\||$)', '', l)
    l = re.sub(r'\s{2,}', ' ', l)
    l = re.sub(r'（\s*）', '', l)
    l = re.sub(r'\|\s*\|\s*\|', '| | |', l)
    if l != orig:
        return l, True, "叙事剥离"
    return orig, False, ""


def main():
    dec = os.path.join(WIKI, "decisions")
    total = 0
    for f in sorted(os.listdir(dec)):
        m = re.match(r"ADR-(\d{3})-(.*)\.md$", f)
        if not m:
            continue
        p = os.path.join(dec, f)
        text, bom, nl = rd(p)
        lines = text.split("\n")
        out = []
        ch = 0
        for l in lines:
            nl2, c, why = strip_line(l)
            if c:
                ch += 1
            out.append(nl2)
        if ch:
            new = "\n".join(out)
            # 删除产生的连续空行收敛
            new = re.sub(r'\n{3,}', '\n\n', new)
            if not DRY:
                wr(p, new, bom, nl)
            total += ch
            print(f"  {f}: {ch} 处")
    print(f"\n叙事剥离完成：{total} 处 {'(DRY)' if DRY else '已写盘'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
