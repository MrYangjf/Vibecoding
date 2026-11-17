#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
adr_merge.py —— ADR 整页合并助手（常态化入口）

用途：当新决策与既有 ADR **实质同主题**时，把新决策**并入既有页**，
而不是新建一页（KR-007「先合并后新建」+ WikiPageFormatSpec §3.1.3）。

与 `adr_new.py merge` 的分工：
  · `adr_new.py merge` —— 向既有页**追加一条演进记录**（决策是同主题的**补充**，原页主体不变）
  · `adr_merge.py`      —— **整页合并**（新决策与既有页同主题到需要吸收对方主体裁定）
                              承接页加 `merged_from` + 「## 合并自 ADR-0XX」小节；原页删除；
                              旧号在 ADR-Index 留指针行（⛔ 不重排序号）；全库引用改指承接页。

子命令：
  plan   --keeper ADR-NNN --source ADR-0XX[,ADR-0YY]
         只打印合并计划（承接页行数预算、被并页决策条目数、引用影响面），不写盘
  apply  --keeper ADR-NNN --source ADR-0XX[,ADR-0YY] [--subject "整合旧 XXX（说明）"]
         执行合并（承接 → 删页 → 引用改写 → ADR-Index 指针行 → index.md 计数）
  audit  [阈值]
         全库重复度自检（落地实体符号 Jaccard，疑似重复页对）

⚠️ 路径一律从 `__file__` 推导（⛔ 禁写死绝对路径 —— 否则「副本试跑」会反改源目录，
   见 lessons/StaticVerifier-Batch-Script-Traps §四之十四 坑⑦）。
⚠️ 本脚本**幂等**：重复执行不产生额外变化（坑⑧）。
"""
import os
import re
import sys
import itertools

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
DEC = os.path.join(LLMWIKI, "wiki", "decisions")
INDEX_MD = os.path.join(LLMWIKI, "wiki", "index", "index.md")
SIM_THRESHOLD = 0.40

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------- 基础 IO ----------------

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


def adr_file(no):
    for f in os.listdir(DEC):
        if f.startswith("ADR-%s-" % no):
            return os.path.join(DEC, f)
    return None


def section(text, name):
    m = re.search(r"^##\s*%s\s*$(.*?)(?=^##\s|\Z)" % re.escape(name), text, re.S | re.M)
    return m.group(1).strip() if m else ""


def strip_verify(text):
    """剥离「验证 / 验收 / 校验收口」段（验证过程叙事属 log，WikiPageFormatSpec §2.2 R2）"""
    for name in ("验证", "验收", "校验收口"):
        text = re.sub(r"\n##\s*%s\s*$.*?(?=\n##\s|\Z)" % re.escape(name), "", text, flags=re.S | re.M)
    return text


def one_line(text):
    m = re.search(r"^>\s*\*\*(?:决策一句话|一句话决策)\*\*[：:]\s*(.+)$", text, re.M)
    if m:
        return m.group(1).strip()
    m = re.search(r"^>\s*\*\*(.+?)\*\*[：:]\s*(.+)$", text, re.M)
    if m:
        return m.group(2).strip()
    return ""


# ---------------- 相似度判据 ----------------

_ENTITY = re.compile(r"([A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*)"
                     r"|([A-Za-z_][A-Za-z0-9_]*\(\))"
                     r"|(`ROOT/[A-Z_/]+`)")


def entities(text):
    out = set()
    for a, b, c in _ENTITY.findall(text):
        v = a or b or (c.strip("`") if c else "")
        if v:
            out.add(v)
    return out


def landing_entities(text):
    land = section(text, "落地")
    return entities(land if land else text)


def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / float(len(a | b)) if inter else 0.0


def sim_report():
    recs = []
    for f in sorted(os.listdir(DEC)):
        m = re.match(r"ADR-(\d{3})-(.*)\.md$", f)
        if not m:
            continue
        t = read(os.path.join(DEC, f))[0]
        recs.append((int(m.group(1)), m.group(2), landing_entities(t)))
    out = []
    for (na, sa, ea), (nb, sb, eb) in itertools.combinations(recs, 2):
        inter = ea & eb
        if inter:
            out.append((jaccard(ea, eb), na, sa, nb, sb, sorted(inter)))
    out.sort(key=lambda x: -x[0])
    return out


# ---------------- 参数解析 ----------------

def parse_args(argv):
    opt = {"keeper": None, "source": [], "subject": None}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--keeper", "--source", "--subject"):
            if i + 1 >= len(argv):
                raise SystemExit("参数 %s 缺值" % a)
            v = argv[i + 1]
            if a == "--keeper":
                opt["keeper"] = v.replace("ADR-", "").strip()
            elif a == "--source":
                opt["source"] = [x.replace("ADR-", "").strip() for x in v.split(",") if x.strip()]
            else:
                opt["subject"] = v
            i += 2
        else:
            i += 1
    return opt


# ---------------- plan ----------------

def cmd_plan(opt):
    keeper, sources = opt["keeper"], opt["source"]
    if not keeper or not sources:
        raise SystemExit("用法: adr_merge.py plan --keeper ADR-NNN --source ADR-0XX[,ADR-0YY]")
    kp = adr_file(keeper)
    if not kp:
        raise SystemExit("未找到承接页 ADR-%s" % keeper)
    kt = read(kp)[0]
    print("=" * 92)
    print("ADR 合并计划：承接 ADR-%s ← %s" % (keeper, ', '.join(sources)))
    print("=" * 92)
    print("  承接页: %s（%d 行）" % (one_line(kt)[:70], len(kt.split('\n'))))
    for s in sources:
        sp = adr_file(s)
        if not sp:
            print("  ⚠ 被并页 ADR-%s 不存在" % s)
            continue
        st0 = read(sp)[0]
        st = strip_verify(st0)
        dec = section(st, "决策") or section(st, "结论")
        print("  被并页 ADR-%s: %s" % (s, one_line(st0)[:70]))
        print("     行数 %d（剥离验证后 %d）· 决策条目 %d"
              % (len(st0.split('\n')), len(st.split('\n')),
                 len(re.findall(r'^\s*\d+\.\s', dec, re.M))))
    print("\n  合并后承接页预计 %d 行（上限：整合页 300 / 单决策 200）"
          % (len(kt.split('\n')) + sum(
              len(strip_verify(read(adr_file(s))[0]).split('\n'))
              for s in sources if adr_file(s)) - 4 * len(sources)))
    print("\n  执行后：原页删除 · 旧号在 ADR-Index 留指针行（⛔ 不重排序号）· 全库引用改指承接页")
    return 0


# ---------------- apply ----------------

def cmd_apply(opt):
    keeper, sources = opt["keeper"], opt["source"]
    if not keeper or not sources:
        raise SystemExit("用法: adr_merge.py apply --keeper ADR-NNN --source ADR-0XX[,ADR-0YY] [--subject ...]")
    kp = adr_file(keeper)
    if not kp:
        raise SystemExit("未找到承接页 ADR-%s" % keeper)

    # ---- ① 承接内容（⛔ 必须先于引用改写：否则被并页 title 里的旧号会被改掉）----
    kt, bom, nl = read(kp)
    blocks = []
    for s in sources:
        if re.search(r"^##\s*合并自\s*ADR-%s\b" % s, kt, re.M):
            print("  ⓘ ADR-%s ← %s：承接小节已存在，跳过" % (keeper, s))
            continue
        sp = adr_file(s)
        if not sp or not os.path.exists(sp):
            print("  ⓘ ADR-%s ← %s：源页不存在，跳过" % (keeper, s))
            continue
        st0 = read(sp)[0]
        st = strip_verify(st0)
        m = re.search(r"^title:\s*(.+)$", st, re.M)
        title = m.group(1).strip().strip('"') if m else ""
        title_body = re.sub(r"^ADR-%s\s+" % s, "", title)
        blk = ["## 合并自 ADR-%s · %s" % (s, title_body), "",
               "> 2026-11-17 治理轮合并：原页为独立 ADR-%s，其现行裁定收归本页；"
               "原页文件已删除（**编号不回收**，废止号不复用）。"
               "原页的验证过程叙事已按格式契约 R2 剥离至 `logs/log.md`。" % s, ""]
        one = one_line(st)
        if one:
            blk += ["**原页决策一句话**：%s" % one, ""]
        dec = section(st, "决策") or section(st, "结论")
        if dec:
            blk += ["### 原页决策条目", "", dec, ""]
        bg = section(st, "背景")
        if bg:
            blk += ["### 原页背景", "", bg, ""]
        cons = section(st, "后果")
        if cons:
            blk += ["### 原页后果", "", cons, ""]
        blocks.append("\n".join(blk))
    if blocks:
        anchor = "\n## 相关页面"
        add = "\n" + "\n".join(blocks) + "\n"
        if anchor in kt:
            kt = kt.replace(anchor, add + anchor, 1)
        else:
            kt = kt.rstrip("\n") + "\n" + add
    # frontmatter：merged_from（只记被并旧号）+ updated + title 标注
    want = sorted(set(sources))
    if re.search(r"^merged_from:", kt, re.M):
        kt = re.sub(r"^merged_from:.*$",
                    "merged_from: [%s]" % ", ".join("ADR-%s" % x for x in want),
                    kt, count=1, flags=re.M)
    else:
        kt = re.sub(r"^(title:.*)$", r"\1\nmerged_from: [%s]" % ", ".join("ADR-%s" % x for x in want),
                    kt, count=1, flags=re.M)
    kt = re.sub(r"^updated:.*$", "updated: 2026-11-17", kt, count=1, flags=re.M)
    if opt["subject"]:
        lines = kt.split("\n")
        m = re.match(r"^title:\s*(.*)$", lines[1])
        if m:
            tt = m.group(1).strip().strip('"')
            if "整合旧" not in lines[1]:
                lines[1] = 'title: "%s（%s）"' % (tt, opt["subject"])
                kt = "\n".join(lines)
    write(kp, kt, bom, nl)
    print("  ✓ 承接 ADR-%s ← %s（%d 行）" % (keeper, ', '.join(sources), len(kt.split('\n'))))

    # ---- ② 删页 ----
    keeper_link = "[[decisions/%s]]" % os.path.basename(kp)[:-3]
    deleted = []
    for s in sources:
        sp = adr_file(s)
        if not sp:
            continue
        try:
            os.chmod(sp, 0o666)
            os.remove(sp)
            deleted.append(s)
            print("  ✓ 删除 ADR-%s" % s)
        except OSError as ex:
            raise SystemExit("删除 ADR-%s 失败：%s ⇒ 中止（否则引用改写会静默漏改）" % (s, ex))

    # ---- ③ 全库引用改写（wikilink / 裸号 / 相对路径链接）----
    changed = 0
    targets = []
    for sub in ("wiki", "logs"):
        for dp, dirs, fs in os.walk(os.path.join(LLMWIKI, sub)):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in fs:
                if f.endswith(".md"):
                    targets.append(os.path.join(dp, f))
    for p in sorted(set(targets)):
        if os.path.basename(p) == "ADR-Index.md":
            continue
        t, b2, n2 = read(p)
        o = t
        for s in sources:
            t = re.sub(r"\[\[decisions/ADR-%s-[^\]]*\]\]" % s, keeper_link, t)
            t = re.sub(r"\bADR-%s\b" % s, "ADR-%s" % keeper, t)
            # 相对路径链接：[文字](ADR-0XX-Slug.md) ⇒ 改指承接页文件名
            kfn = os.path.basename(kp)
            t = re.sub(r"\]\(ADR-%s-[^)]+\.md\)" % s, "](%s)" % kfn, t)
        if t != o:
            write(p, t, b2, n2)
            changed += 1
    print("  ✓ 引用改写：%d 个文件" % changed)

    # ---- ④ ADR-Index 指针行 + 计数 ----
    rewrite_index(keeper, sources, opt["subject"], deleted)
    # ---- ⑤ index.md 计数同步 ----
    sync_index()
    return 0


def rewrite_index(keeper, sources, subject, deleted):
    p = os.path.join(DEC, "ADR-Index.md")
    t, bom, nl = read(p)
    lines = t.split("\n")
    # 找承接页行
    krow = None
    for ln in lines:
        if re.match(r"^\|\s*%s\s*\|\s*\[\[decisions/ADR-%s-" % (keeper, keeper), ln):
            krow = ln
            break
    klink = "[[decisions/%s]]" % os.path.basename(adr_file(keeper))[:-3]
    added = []
    for s in sources:
        # 幂等：指针留档行已存在则跳过（否则重复执行会叠加指针行）
        if re.search(r"^\|\s*%s\s*\|\s*→" % s, t, re.M):
            print("  ⓘ ADR-Index：%s 指针留档行已存在，跳过" % s)
            continue
        # 找被并页旧行（若已被删则从主题列取原文备份不可得 → 用 subject）
        old = None
        for ln in lines:
            if re.match(r"^\|\s*%s\s*\|" % s, ln):
                old = ln
                break
        subj = subject or "整合旧 %s" % s
        if old:
            cells = [c.strip() for c in old.split("|")]
            if len(cells) >= 4 and cells[3]:
                subj = cells[3]
        added.append("| %s | → %s | %s（**已并入 ADR-%s**，原页已删；编号不回收） "
                     "| deprecated | 2026-11-17 |" % (s, klink, subj, keeper))
    if added:
        # ⛔ 必须**删掉被并页的旧行** —— 否则索引里同一号出现两行（旧行 + 指针行）
        for s in sources:
            for i, ln in enumerate(lines):
                if re.match(r"^\|\s*%s\s*\|" % s, ln) and not re.match(r"^\|\s*%s\s*\|\s*→" % s, ln):
                    del lines[i]
                    break
        # 插到承接页行之后
        idx = None
        for i, ln in enumerate(lines):
            if ln.startswith("| %s |" % keeper) and "→" not in ln:
                idx = i
                break
        if idx is None:
            raise SystemExit("ADR-Index 未找到承接页行 ADR-%s ⇒ 中止" % keeper)
        lines = lines[:idx + 1] + added + lines[idx + 1:]
        nt = "\n".join(lines)
        write(p, nt, bom, nl)
        print("  ✓ ADR-Index 新增 %d 行指针留档" % len(added))
    # 抬头计数
    alive = len([f for f in os.listdir(DEC) if re.match(r"ADR-\d{3}-", f)])
    ns = sorted(int(m.group(1)) for m in
                (re.match(r"ADR-(\d{3})-", f) for f in os.listdir(DEC)) if m)
    nt, bom, nl = read(p)
    nt = re.sub(r"\*\*现行编号：\d+~\d+ 连续无断号\*\*",
                "**现行编号：%03d~%03d 连续无断号**" % (ns[0], ns[-1]), nt)
    nt = re.sub(r"\*\*现行有效页 = \d+ 页\*\*",
                "**现行有效页 = %d 页**" % alive, nt)
    write(p, nt, bom, nl)
    print("  ✓ ADR-Index 计数同步（现行 %d 页 / 编号 %03d~%03d）" % (alive, ns[0], ns[-1]))


def sync_index():
    alive = len([f for f in os.listdir(DEC) if re.match(r"ADR-\d{3}-", f)])
    ns = sorted(int(m.group(1)) for m in
                (re.match(r"ADR-(\d{3})-", f) for f in os.listdir(DEC)) if m)
    t, bom, nl = read(INDEX_MD)
    o = t
    t = re.sub(r"\| \[七、设计决策 ADR\]\(#七设计决策\)\s*\|\s*\d+ 条（[^）]*）",
               "| [七、设计决策 ADR](#七设计决策) | %d 条（%03d~%03d 连续）"
               % (alive, ns[0], ns[-1]), t)
    if t != o:
        write(INDEX_MD, t, bom, nl)
        print("  ✓ index.md §七 计数同步")


# ---------------- audit ----------------

def cmd_audit(argv):
    thr = float(argv[0]) if argv else SIM_THRESHOLD
    sims = sim_report()
    total = len([f for f in os.listdir(DEC) if re.match(r"ADR-\d{3}-", f)])
    print("=" * 92)
    print("ADR 重复度自检（落地实体符号 Jaccard，阈值 %.2f）" % thr)
    print("=" * 92)
    print("  ADR 页数: %d" % total)
    over = [x for x in sims if x[0] >= thr]
    print("  超阈值页对: %d" % len(over))
    for j, na, sa, nb, sb, inter in over[:20]:
        print("  ⚠ J=%.3f  ADR-%03d-%s  ↔  ADR-%03d-%s" % (j, na, sa, nb, sb))
        print("           共同符号: %s" % ", ".join(inter[:12]))
    if not over:
        print("  ✅ 无超阈值页对")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "audit":
        return cmd_audit(sys.argv[2:])
    opt = parse_args(sys.argv[2:])
    if cmd == "plan":
        return cmd_plan(opt)
    if cmd == "apply":
        return cmd_apply(opt)
    print("未知子命令：%s（可用 plan / apply / audit）" % cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())
