#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
adr_new.py —— ADR 新增/合并助手（强制「先合并、后新建」）

子命令：
  check  <关键词...>   检索是否已有同主题 ADR（合并候选）—— 新建前必须先跑
  merge  <ADR-NNN> <决策号> <变更> <理由> <影响>
                      向既有 ADR 追加「演进记录」小节（不新建页）
  new    <slug> <标题> <背景> <决策...>
                      仅在 check 报告无候选时使用；自动分配新号并登记两处
  audit  [阈值]        全库重复度自检：按落地实体符号 Jaccard 找出疑似重复页对

编号：新号 = ADR-Index 中 max+1；废止页不回收编号。
退出码：0 成功；1 参数/校验错误；2 命中相似度阈值（疑似重复，禁止新建）。

2026-11-17 治理改造（ADR 库全库审计后）：
  ① check 增「相似度阈值」判据 —— 原实现只做关键词子串计数，命中即列候选，
     既阻断不了重复新建，也无法区分「同主题」与「同子串」。
     现增**落地实体符号 Jaccard**（Class.Member / Method() / ROOT/KEY 形态），
     ≥ 阈值即判「疑似同一实现被写成两页」，是判重复的权威依据。
     （2026-11-17 全库审计实证：5671 页对中仅 1 对 ≥0.40，落地实体 Jaccard
       是唯一能把「真重复」与「主题相邻」区分开的判据 —— 标题/正文措辞会误判。）
  ② new 强制先过 check —— 命中相似度阈值直接拒绝新建（退出码 2）。
  ③ merge 取消 change/reason/impact 的 100 字符硬截断 —— 硬截断会让演进记录
     尾部断在半句（原缺陷实例：ADR-100 D29「…各自前置拒绝，停」）。
     改为「按句边界软截断 + 显式提示需手工补全尾句」。
  ④ merge 的决策号不再自动加 D 前缀（原实现传 D24 会写出 DD24）。
"""
import os
import re
import sys
import itertools

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
DEC = os.path.join(LLMWIKI, "wiki", "decisions")
IDX = os.path.join(WIKI_INDEX := os.path.join(LLMWIKI, "wiki", "index"), "index.md")
ADRI = os.path.join(DEC, "ADR-Index.md")

# 相似度阈值：落地实体符号 Jaccard ≥ 此值 ⇒ 判「疑似重复，禁止新建」
SIM_THRESHOLD = 0.40

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


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


def adr_files():
    out = []
    for f in sorted(os.listdir(DEC)):
        m = re.match(r"ADR-(\d{3})-(.*)\.md$", f)
        if m:
            out.append((int(m.group(1)), m.group(2), f))
    return out


def max_no():
    ns = [n for n, _, _ in adr_files()]
    return max(ns) if ns else 0


# ---------- 相似度判据（落地实体符号） ----------

# 实体符号形态：Class.Member / Method() / `ROOT/KEY` —— 判「同一实现被写成两页」
_ENTITY = re.compile(r"([A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*)"
                     r"|([A-Za-z_][A-Za-z0-9_]*\(\))"
                     r"|(`ROOT/[A-Z_/]+`)")


def _section(text, name):
    m = re.search(r"^##\s*%s\s*$(.*?)(?=^##\s|\Z)" % re.escape(name), text, re.S | re.M)
    return m.group(1) if m else ""


def entities(text):
    """抽取实体符号集合（Class.Member / Method() / ROOT/KEY）"""
    out = set()
    for a, b, c in _ENTITY.findall(text):
        v = a or b or (c.strip("`") if c else "")
        if v:
            out.add(v)
    return out


def landing_entities(text):
    """落地节的实体符号 —— 决策「改同一批代码」的直接证据"""
    land = _section(text, "落地")
    if not land:
        land = text          # 无「落地」节时退回全文
    return entities(land)


def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if not inter:
        return 0.0
    return inter / float(len(a | b))


def sim_report():
    """返回 [(jaccard, no_a, slug_a, no_b, slug_b, 共同符号)] 按相似度降序"""
    recs = []
    for n, slug, f in adr_files():
        t = read(os.path.join(DEC, f))[0]
        recs.append((n, slug, landing_entities(t)))
    out = []
    for (na, sa, ea), (nb, sb, eb) in itertools.combinations(recs, 2):
        if not ea or not eb:
            continue
        inter = ea & eb
        if not inter:
            continue
        j = len(inter) / float(len(ea | eb))
        out.append((j, na, sa, nb, sb, sorted(inter)))
    out.sort(key=lambda x: -x[0])
    return out


def cmd_check(argv):
    if not argv:
        print("用法: adr_new.py check <关键词...>")
        return 1
    keys = [k.lower() for k in argv]
    hits = []
    for n, slug, f in adr_files():
        t = read(os.path.join(DEC, f))[0].lower()
        score = sum(1 for k in keys if k in t or k in slug.lower())
        if score:
            title = ""
            m = re.search(r"^title:\s*(.*)$", t, re.M)
            if m:
                title = m.group(1)
            hits.append((score, n, slug, title))
    hits.sort(reverse=True)

    # ---- 相似度判据：落地实体符号 Jaccard ≥ 阈值 ⇒ 疑似重复 ----
    # 判「同一实现被写成两页」的权威依据；标题/正文措辞会误判（实测同主题不同
    # 子问题的页对正文相似度可高达 0.14，而真重复的落地实体 Jaccard 显著更高）。
    sims = [(j, na, sa, nb, sb, inter)
            for (j, na, sa, nb, sb, inter) in sim_report() if j >= SIM_THRESHOLD]

    if not hits and not sims:
        print("未发现同主题候选 —— 可走新建路径（adr_new.py new）")
        return 0

    if hits:
        print("发现 %d 个同主题候选 —— 优先走【合并路径】（adr_new.py merge），不要新建页：" % len(hits))
        for s, n, slug, title in hits[:10]:
            print("  [关键词命中 %d/%d] ADR-%03d-%s  %s" % (s, len(keys), n, slug, title[:70]))
    if sims:
        print("\n  ⛔ 相似度超阈值的疑似重复页对（落地实体符号 Jaccard ≥ %.2f）：" % SIM_THRESHOLD)
        for j, na, sa, nb, sb, inter in sims[:10]:
            print("     J=%.3f  ADR-%03d-%s  ↔  ADR-%03d-%s" % (j, na, sa, nb, sb))
            print("            共同符号: %s" % ", ".join(inter[:10]))
        print("     ⇒ 这类页对必须走合并路径（内容并入承接页），不得各自新建。")
    return 0


def _soft_cut(text, limit):
    """软截断：优先在句边界断开，避免记录尾部断在半句。

    2026-11-17 治理改造：原实现用 change[:100] / reason[:100] / impact[:100]
    硬截断 ⇒ 演进记录尾部必然断在半句（实例：ADR-100 D29「…各自前置拒绝，停」）。
    改为按句边界截断；确无句边界时按字数截断并给出显式提示。
    """
    text = (text or "").strip()
    if len(text) <= limit:
        return text, False
    seg = text[:limit + 1]
    # 优先取最后一个句末标点（。！？；，、）
    cut = max(seg.rfind(c) for c in "。！？；")
    if cut < limit * 0.4:
        cut = max(seg.rfind(c) for c in "，、")
    if cut >= limit * 0.4:
        return text[:cut + 1].rstrip() + "…", True
    return text[:limit].rstrip() + "…", True


def cmd_merge(argv):
    if len(argv) < 5:
        print("用法: adr_new.py merge <ADR-NNN> <决策号> <变更> <理由> <影响>")
        return 1
    no = argv[0].replace("ADR-", "")
    dno, change, reason, impact = argv[1], argv[2], argv[3], argv[4]
    # 决策号：允许带或不带 D 前缀，内部统一为 D<N>
    dnum = re.sub(r"^D", "", str(dno).strip())
    dtag = "D%s" % dnum
    target = None
    for n, slug, f in adr_files():
        if ("ADR-%03d" % n) == ("ADR-" + no) or f.startswith("ADR-%s-" % no):
            target = f
            break
    if not target:
        print("未找到 ADR-%s" % no)
        return 1
    p = os.path.join(DEC, target)
    t, bom, nl = read(p)
    import datetime
    today = datetime.date.today().isoformat()
    c, c_cut = _soft_cut(change, 120)
    r, r_cut = _soft_cut(reason, 120)
    i, i_cut = _soft_cut(impact, 120)
    block = ["", "### %s · 决策 %s · %s" % (today, dtag, c[:60]),
             "- **变更**：%s" % c,
             "- **理由**：%s" % r,
             "- **影响**：%s" % i, ""]
    anchor = "\n## 相关页面"
    if anchor in t:
        t = t.replace(anchor, "\n".join(block) + anchor, 1)
    else:
        t = t.rstrip("\n") + "\n" + "\n".join(block)
    write(p, t, bom, nl)
    print("已向 %s 追加演进记录（决策 %s）" % (target, dtag))
    if c_cut or r_cut or i_cut:
        print("⚠️ 有字段被软截断（超出 120 字符）⇒ 尾部以「…」结束，"
              "请手工补全尾句后再进 Phase 3 沉淀")
    return 0


def cmd_new(argv):
    if len(argv) < 4:
        print("用法: adr_new.py new <slug> <标题> <背景> <决策1|决策2|...>")
        return 1
    slug, title, bg, decisions = argv[0], argv[1], argv[2], argv[3]
    n = max_no() + 1
    fname = "ADR-%03d-%s.md" % (n, slug)
    p = os.path.join(DEC, fname)
    if os.path.exists(p):
        print("文件已存在：%s" % fname)
        return 1

    # ---- 强制先过 check：相似度超阈值 ⇒ 拒绝新建（KR-007 先合并后新建）----
    # 2026-11-17 治理改造：原实现不强制 check，可绕过查重建重复页。
    # 判据：**拟建页**与**既有页**的落地实体符号 Jaccard ≥ SIM_THRESHOLD ⇒ 疑似重复。
    # ⛔ 只比「拟建页 vs 既有页」—— 库内既有的其它重复对与本次新建无关，
    #    若一并纳入会把所有合法新建都误拦（假阳性）。
    probe = "## 落地\n\n" + " ".join(x.strip() for x in decisions.split("|") if x.strip())
    probe_ent = entities(probe)
    if probe_ent:
        best = None
        for n, slug, f in adr_files():
            t = read(os.path.join(DEC, f))[0]
            j = jaccard(probe_ent, landing_entities(t))
            if best is None or j > best[0]:
                best = (j, n, slug, sorted(probe_ent & landing_entities(t)))
        if best and best[0] >= SIM_THRESHOLD:
            j, n, slug, inter = best
            print("⛔ 拒绝新建：疑似与既有 ADR 重复（落地实体符号 Jaccard=%.3f ≥ 阈值 %.2f）" % (j, SIM_THRESHOLD))
            print("   候选: ADR-%03d-%s" % (n, slug))
            print("   共同符号: %s" % ", ".join(inter[:10]))
            print("   ⇒ 必须走合并路径（adr_new.py merge），把新决策并入既有页")
            return 2
        if best:
            print("ℹ 相似度自检：与既有页最高 Jaccard=%.3f（ADR-%03d-%s），低于阈值 %.2f ⇒ 允许新建"
                  % (best[0], best[1], best[2], SIM_THRESHOLD))

    import datetime
    today = datetime.date.today().isoformat()
    L = ["---", "title: ADR-%03d %s" % (n, title), "date: %s" % today,
         "updated: %s" % today, "tags: [决策]", "status: proposed", "---", "",
         "# ADR-%03d %s" % (n, title), "",
         "> **决策一句话**：%s" % title[:120], "",
         "## 背景", "", bg[:800], "",
         "## 决策", ""]
    for i, d in enumerate([x.strip() for x in decisions.split("|") if x.strip()], 1):
        L.append("%d. %s" % (i, d[:100]))
    L += ["", "## 备选方案", "", "- （待补）", "", "## 后果", "",
          "### 正面", "- （待补）", "", "### 负面", "- （待补）", "",
          "## 相关页面", "", "- [[decisions/ADR-Index]]", ""]
    write(p, "\n".join(L), False, "\n")
    print("已创建 %s（新号 = max+1 = %d）" % (fname, n))
    print("⚠️ 仍需：① 在 ADR-Index 登记一行 ② 在 index.md §七 登记一行 ③ 填「备选方案/后果」")
    return 0


def cmd_audit(argv):
    """全库重复度自检：按落地实体符号 Jaccard 找出疑似重复页对"""
    thr = float(argv[0]) if argv else SIM_THRESHOLD
    sims = sim_report()
    total = sum(1 for _ in itertools.combinations(adr_files(), 2))
    print("=" * 96)
    print("ADR 重复度自检（判据：落地实体符号 Jaccard，阈值 %.2f）" % thr)
    print("=" * 96)
    print("  ADR 页数: %d   页对总数: %d" % (len(adr_files()), total))
    over = [x for x in sims if x[0] >= thr]
    print("  超阈值页对: %d" % len(over))
    for j, na, sa, nb, sb, inter in over[:20]:
        print("  ⚠ J=%.3f  ADR-%03d-%s  ↔  ADR-%03d-%s" % (j, na, sa, nb, sb))
        print("           共同符号: %s" % ", ".join(inter[:12]))
    if not over:
        print("  ✅ 无超阈值页对")
    mid = [x for x in sims if 0.20 <= x[0] < thr]
    print("\n  0.20~%.2f（主题相邻但落地不同，不判重复）: %d 对" % (thr, len(mid)))
    for j, na, sa, nb, sb, inter in mid[:8]:
        print("     J=%.3f  ADR-%03d-%s  ↔  ADR-%03d-%s" % (j, na, sa, nb, sb))
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "check":
        return cmd_check(rest)
    if cmd == "merge":
        return cmd_merge(rest)
    if cmd == "new":
        return cmd_new(rest)
    if cmd == "audit":
        return cmd_audit(rest)
    print("未知子命令：%s（可用 check / merge / new / audit）" % cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())
