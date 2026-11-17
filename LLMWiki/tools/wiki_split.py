#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_split.py —— 大教训页按主题拆分（章节边界机械切分，产出独立页 + 互链）

拆分配置：源文件 → [(新页名, 起始章节标题正则, 结束章节标题正则或 None)]
切分规则：保留源页 frontmatter（改 title/date/status）与抬头说明；各分段按
          '## 章节标题' 降级为 '## 章节标题' 原样保留，追加「## 相关页面」互链。
退出码：0 成功；1 失败。
"""
import os
import re
import sys
import datetime

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
LES = os.path.join(LLMWIKI, "wiki", "lessons")
DRY = "--apply" not in sys.argv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# (源文件, [(新页名, 章节起始正则), ...])；每页取「起始标题 → 下一个起始标题」之间的内容
SPLITS = {
 "IntelligentLaser-Pitfalls.md": [
   ("IntelligentLaser-Sdk-Interop", r"^## 1\. SDK 互操作与结构体"),
   ("IntelligentLaser-Callback-Mechanism", r"^## 3\. 回调机制"),
   ("IntelligentLaser-Ui-State", r"^## 5\. UI 层与状态管理"),
   ("IntelligentLaser-Delegate-Gc", r"^## 6\. 委托 GC 保护"),
   ("IntelligentLaser-Job-System", r"^## 7\. Job 体系教训"),
 ],
 "StaticVerifierJudgements.md": [
   ("StaticVerifier-CSharp-Scoping", r"^## 一、C# 语法与类型系统"),
   ("StaticVerifier-Wiring-Integrity", r"^## 三、接线完整性"),
   ("StaticVerifier-Checker-FailureModes", r"^## 四、静态校验器自身的失效模式"),
   ("StaticVerifier-Batch-Script-Traps", r"^## 四之十四、"),
   ("StaticVerifier-Tooling-Substitutes", r"^## 七、工具受限时的替代方案"),
   ("StaticVerifier-AdrNumbering", r"^## 八、ADR 编号"),
   ("StaticVerifier-RecentJudgements", r"^## 九、本轮"),
 ],
 "StepDrivenWorkflowPitfalls.md": [
   ("StepDriven-SixPitfalls", r"^## 坑一："),
   ("StepDriven-DeviceControl-Lessons", r"^## 七、设备控制与状态机教训"),
 ],
}


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


def split_file(src, parts):
    p = os.path.join(LES, src)
    text, bom, nl = rd(p)
    lines = text.split("\n")
    # frontmatter 与抬头
    fm_end = None
    if lines and lines[0].lstrip("\ufeff").strip() == "---":
        for i in range(1, min(30, len(lines))):
            if lines[i].strip() == "---":
                fm_end = i
                break
    if fm_end is None:
        fm_end = 0
    fm = lines[:fm_end + 1]
    head = lines[fm_end + 1:]
    # 抬头（第一个 ## 之前）
    first_sec = next((i for i, l in enumerate(head) if l.startswith("## ")), len(head))
    intro = head[:first_sec]
    body = head[first_sec:]

    # 各分段边界
    bounds = []
    for name, pat in parts:
        idx = next((i for i, l in enumerate(body) if re.match(pat, l)), None)
        if idx is None:
            print("  ❌ %s: 未找到章节 %s" % (src, pat))
            return None
        bounds.append((name, idx))
    bounds.sort(key=lambda x: x[1])
    # 每段结束 = 下一段开始；末段结束 = 源页中「## 相关页面」或文末
    tail_idx = next((i for i, l in enumerate(body) if re.match(r"^##\s*(相关页面|来源|关联)\s*$", l)), len(body))
    out_files = []
    today = datetime.date.today().isoformat()
    for k, (name, s) in enumerate(bounds):
        e = bounds[k + 1][1] if k + 1 < len(bounds) else tail_idx
        seg = body[s:e]
        if not seg:
            continue
        newfm = []
        for l in fm:
            if l.startswith("title:"):
                newfm.append("title: %s" % name)
            elif l.startswith("date:"):
                newfm.append("date: %s" % today)
            elif l.startswith("updated:"):
                newfm.append("updated: %s" % today)
            elif l.startswith("status:"):
                newfm.append("status: active")
            else:
                newfm.append(l)
        # 抬头 + 分段 + 互链
        doc = list(newfm) + [""]
        doc += [l for l in intro if l.strip() or True]
        doc.append("")
        doc += seg
        doc.append("## 相关页面")
        doc.append("")
        for other, _ in bounds:
            if other != name:
                doc.append("- [[lessons/%s]] —— 同源拆分页" % other)
        doc.append("- [[lessons/%s]] —— 源页（拆分前全量）" % src[:-3])
        doc.append("")
        out_files.append((name, "\n".join(doc)))
    # 源页改为「索引页」：只留抬头 + 各页指针
    idx_doc = list(fm)
    idx_doc[0] = idx_doc[0]
    doc = list(fm) + [""]
    doc += [l for l in intro if l.strip() or True]
    doc.append("## 本页已按主题拆分（2026-10-30）")
    doc.append("")
    doc.append("> 原页篇幅过大，按主题拆为下列独立页；本索引页保留抬头与指针。")
    doc.append("")
    for name, _ in bounds:
        doc.append("- [[lessons/%s]]" % name)
    doc.append("")
    doc.append("## 相关页面")
    doc.append("")
    doc.append("- [[index/index]]")
    doc.append("")
    out_files.append((src[:-3], "\n".join(doc)))
    return out_files


def main():
    for src, parts in SPLITS.items():
        res = split_file(src, parts)
        if res is None:
            return 1
        print("=== %s → %d 页" % (src, len(res)))
        for name, content in res:
            p = os.path.join(LES, name + ".md")
            exist = " [已存在，覆盖]" if os.path.exists(p) else ""
            if not DRY:
                wr(p, content, False, "\n")
            print("   %-40s %4d 行%s" % (name + ".md", content.count("\n") + 1, exist))
    print("\n%s" % ("DRY-RUN" if DRY else "已写盘"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
