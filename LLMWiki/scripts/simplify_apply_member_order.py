# -*- coding: utf-8 -*-
"""simplify_apply_member_order.py —— 成员顺序重排器（§一① 私有变量→公共变量→构造函数→私有函数→公共函数）。

固化 2026-10-26 全库治理轮验证过的实现（禁区清单见 wiki/standards/CodeSimplification-Tooling）：
  · 整块切分（/// 文档+[特性]+声明+尾部空行；块间残留并入前块 ⇒ 切分无缝）
  · 字节级重组自证：header+按原序拼接的所有块 == 原类体区间（不等则放弃该文件）
  · 区域感知：#region 切段，段内重排、段间不跨越
  · **候选结构守卫**：候选文本先过 simplify_guard 的 namespace 级结构 + region 配对（2026-10-26 新增）
  · oracle：重排后扫描器违规数须下降，否则不写
  · 落盘后守卫复验，FAIL 立即用快照回滚（2026-10-26 新增）
用法：python simplify_apply_member_order.py --all [--dry-run] [--files a.cs ...]
"""
import os, re, sys, shutil, argparse, time

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import csharp_review as CR
import simplify_guard as G
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CODE = os.path.join(ROOT, "AdaWeldSystem")
SNAP = os.path.join(ROOT, "_simplify_snapshot")
SKIP = {"bin", "obj", "3rdDepend", ".vs"}
TW = re.compile(r"\b(class|struct|interface|enum)\b")


def sc(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r'@"(?:[^"]|"")*"', '""', s)
    s = re.sub(r'"(?:\\.|[^"\\])*"', '""', s)
    s = re.sub(r"'(?:\\.|[^'\\])'", "''", s)
    return re.sub(r"//.*$", "", s)


def tiers(cls, classes=None):
    nested = []
    if classes:
        cs = cls.get("start_line") or 0
        ce = cls.get("end_line") or 0
        for c in classes:
            if c is cls:
                continue
            s = c.get("start_line") or 0
            e = c.get("end_line") or 0
            if cs < s and e <= ce:
                nested.append((s, e))

    def _nested(ln):
        return any(s <= ln <= e for s, e in nested)

    ms = []
    for f in cls["fields"]:
        if _nested(f.start_line) or TW.search(getattr(f, "ftype", "") or ""):
            continue
        ms.append([1 if f.access == "private" else 2, f.start_line, "F", f.name, f])
    for p in cls["properties"]:
        if _nested(p.start_line) or TW.search(getattr(p, "ftype", "") or ""):
            continue
        ms.append([2 if p.access in ("public", "protected") else 1, p.start_line, "P", p.name, p])
    for m in cls["methods"]:
        if _nested(m.start_line):
            continue
        o = 3 if m.name == "#ctor" else (4 if m.access == "private" else 5)
        ms.append([o, m.start_line, "M", m.name, m])
    ms.sort(key=lambda x: x[1])
    return ms


def line_seg_map(lines):
    """逐行 region 段号：region 开标签行进入新段，end 标签行进入旧段。"""
    seg = []
    cur = 0
    for l in lines:
        s = l.strip()
        if s.startswith("#region"):
            cur += 1
        seg.append(cur)
        if s.startswith("#endregion"):
            cur += 1
    return seg


def viol(cls, segs=None, classes=None):
    """region 内顺序违规（2026-10-26 裁定：跨 region 不比较；嵌套类型成员不参与）。"""
    prev = {}
    out = []
    for m in tiers(cls, classes):
        ln = m[1] - 1
        sg = segs[ln] if segs and 0 <= ln < len(segs) else 0
        if m[0] < prev.get(sg, 0):
            out.append((m[2], m[3]))
        prev[sg] = m[0]
    return out


def all_viol(src):
    r = []
    segs = line_seg_map(src.split("\n"))
    classes = CR.parse_file(src)
    for c in classes:
        for k, n in viol(c, segs, classes):
            r.append((c.get("name"), k, n))
    return r


def stmt_end(lines, sl, maxl):
    depth = 0
    started = False
    for i in range(sl - 1, maxl):
        t = sc(lines[i])
        done = False
        for ch in t:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    done = True
                    break
            elif ch == ";" and depth == 0:
                done = True
                break
        if done:
            return i + 1
    return maxl


def attr_start(lines, end_idx):
    """从特性块末行反向找到 '[' 起始行（支持多行特性）。"""
    depth = 0
    j = end_idx
    while j >= 0:
        s = lines[j]
        depth += s.count("[") - s.count("]")
        if depth <= 0 and s.strip().startswith("["):
            return j
        if depth <= 0:
            return end_idx
        j -= 1
    return end_idx


def chunk_span(lines, sl, cls_end):
    i = sl - 1
    while i > 0:
        s = lines[i - 1].strip()
        if s.startswith("///"):
            i -= 1
            continue
        if s.endswith("]"):
            i = attr_start(lines, i - 1)
            continue
        break
    cs = i
    ce = stmt_end(lines, sl, cls_end)
    if ce < cs + 1:
        ce = cs + 1
    if ce > cls_end:
        ce = cls_end
    j = ce
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    return cs, j


def seg_ids(blocks):
    """region 感知分段：含 #region 的块开启新段，含 #endregion 的块结束当前段。"""
    seg = []
    cur = 0
    for b in blocks:
        bt = "\n".join(b)
        if "#region" in bt:
            cur += 1
        seg.append(cur)
        if "#endregion" in bt:
            cur += 1
    return seg


def region_title_map(lines):
    """逐行记录所属 region 标题（用于 --report 定位跨段违规）。"""
    out = []
    cur = "(无 region)"
    for l in lines:
        s = l.strip()
        if s.startswith("#region"):
            cur = s[len("#region"):].strip() or "(未命名 region)"
        elif s.startswith("#endregion"):
            cur = "(无 region)"
        out.append(cur)
    return out


def report_viols(src, rel):
    """打印剩余违规：文件 | 类 | 类型 | 成员 | 行 | region（region 内口径）。"""
    lines = src.split("\n")
    titles = region_title_map(lines)
    segs = line_seg_map(lines)
    n = 0
    classes = CR.parse_file(src)
    for cls in classes:
        prev = {}
        for m in tiers(cls, classes):
            ln = m[1]
            sg = segs[ln - 1] if 0 <= ln - 1 < len(segs) else 0
            if m[0] < prev.get(sg, 0):
                rt = titles[ln - 1] if 0 <= ln - 1 < len(titles) else ""
                print("%-58s | %-24s | %s.%-20s | L%-5d | %s" %
                      (rel, cls.get("name"), m[2], m[3], ln, rt))
                n += 1
            prev[sg] = m[0]
    return n


def reorder(src):
    lines = src.split("\n")
    classes = CR.parse_file(src)
    newsrc = src
    moved = 0
    reasons = []
    for cls in list(classes):
        segs = line_seg_map(lines)
        ms = tiers(cls, classes)
        if not viol(cls, segs, classes):
            continue
        cls_end = cls.get("end_line") or len(lines)
        spans = []
        for m in ms:
            cs, ce = chunk_span(lines, m[1], cls_end)
            spans.append((cs, ce, m))
        spans.sort(key=lambda x: x[0])
        if any(spans[i][1] > spans[i + 1][0] for i in range(len(spans) - 1)):
            reasons.append("%s:overlap" % cls.get("name"))
            continue
        cstart = cls.get("start_line") or 1
        n = len(spans)
        # 成员块只含「自身行」，块间间隙（#region/#endregion/空行）原地不动；
        # 旧实现把「从成员起点到类尾」整段当最后一块 ⇒ 搬动时把 #endregion + }
        # 一起搬走，导致类提前闭合（2026-10-26 结构事故根因）。
        blocks = [lines[cs:ce] for cs, ce, _ in spans]
        gaps = [lines[spans[i][1]:spans[i + 1][0]] for i in range(n - 1)]
        tail = lines[spans[-1][1]:cls_end]
        # 护栏：块内含**嵌套类型声明**时不搬动（嵌套类被字段解析器收进来，
        # 搬动它会把整个嵌套类体当成员移动，既可能破坏外层结构，也会让解析器失控）
        if any(re.search(r"\b(class|struct|interface|enum)\s+\w+", "\n".join(b)) for b in blocks):
            reasons.append("%s:nested-type" % cls.get("name"))
            continue
        header = lines[cstart - 1:spans[0][0]]
        chk = list(header)
        for i in range(n):
            chk.extend(blocks[i])
            chk.extend(gaps[i] if i < n - 1 else tail)
        if chk != lines[cstart - 1:cls_end]:
            reasons.append("%s:split-lossy" % cls.get("name"))
            continue
        seg = []
        cur = 0
        for i in range(n):
            seg.append(cur)
            g = gaps[i] if i < n - 1 else tail
            if any(("#region" in l or "#endregion" in l) for l in g):
                cur += 1
        order = list(range(n))
        i = 0
        while i < n:
            j = i
            while j + 1 < n and seg[j + 1] == seg[i]:
                j += 1
            grp = sorted(range(i, j + 1), key=lambda k: (spans[k][2][0], k))
            for pos, k in zip(range(i, j + 1), grp):
                order[pos] = k
            i = j + 1
        if order == list(range(n)):
            reasons.append("%s:already-ok" % cls.get("name"))
            continue
        new = list(header)
        for pos in range(n):
            new.extend(blocks[order[pos]])
            new.extend(gaps[pos] if pos < n - 1 else tail)
        cand = "\n".join(lines[:cstart - 1] + new + lines[cls_end:])
        broken = G.structural_fails(cand) + G.region_fails(cand)
        if broken:
            reasons.append("%s:struct-broken(%s)" % (cls.get("name"), broken[0][:40]))
            continue
        newclasses = CR.parse_file(cand)
        ncls = None
        for c in newclasses:
            if c.get("name") == cls.get("name"):
                ncls = c
        if ncls is None:
            reasons.append("%s:class-lost" % cls.get("name"))
            continue
        if len(viol(ncls, line_seg_map(cand.split("\n")), newclasses)) >= len(viol(cls, segs, classes)):
            reasons.append("%s:no-improve" % cls.get("name"))
            continue
        newsrc = cand
        lines = cand.split("\n")
        classes = CR.parse_file(cand)
        moved += 1
    return (newsrc, moved, reasons)


def fix_victims(src):
    """定点搬移：只把「违规成员段」搬到本 region 内第一个更高层级成员之前。

    适用于 overlap / 堆叠注释 / 嵌套类型等无法整类重排的文件；
    每轮只搬一段，最多 4 轮，搬后重新解析。
    """
    lines = src.split("\n")
    moves = 0
    reasons = []
    for _ in range(4):
        text = "\n".join(lines)
        classes = CR.parse_file(text)
        segs = line_seg_map(lines)
        changed = False
        for cls in classes:
            cls_end = cls.get("end_line") or len(lines)
            ms = tiers(cls, classes)
            if not viol(cls, segs, classes):
                continue
            spans = []
            for m in ms:
                cs, ce = chunk_span(lines, m[1], cls_end)
                spans.append((cs, ce, m))
            groups = {}
            for pos, sp in enumerate(spans):
                ln = sp[2][1] - 1
                sg = segs[ln] if 0 <= ln < len(segs) else 0
                groups.setdefault(sg, []).append(pos)
            done = False
            for sg, poslist in groups.items():
                prev = 0
                for pi, pos in enumerate(poslist):
                    m = spans[pos][2]
                    if m[0] < prev:
                        j = pi
                        while j + 1 < len(poslist) and spans[poslist[j + 1]][2][0] == m[0]:
                            j += 1
                        target_pos = None
                        # 目标是本 region 内**最早**的更高层级成员：只搬到最近的更高层级
                        # 仍会留在更早的更高层级之后，违规数不会下降（2026-10-29 实证）。
                        for k in range(0, pos):
                            if spans[poslist[k]][2][0] > m[0]:
                                target_pos = poslist[k]
                                break
                        if target_pos is None:
                            reasons.append("%s:%s:no-target" % (cls.get("name"), m[3]))
                            continue
                        run_start = spans[pos][0]
                        run_end = spans[poslist[j]][1]
                        tgt = spans[target_pos][0]
                        if tgt >= run_start:
                            reasons.append("%s:%s:overlap" % (cls.get("name"), m[3]))
                            continue
                        block = lines[run_start:run_end]
                        if any(("#region" in l or "#endregion" in l) for l in block) or \
                           re.search(r"\b(class|struct|interface|enum)\s+\w+", "\n".join(block)):
                            reasons.append("%s:%s:region-or-nested" % (cls.get("name"), m[3]))
                            continue
                        cand_lines = lines[:run_start] + lines[run_end:]
                        cand_lines = cand_lines[:tgt] + block + cand_lines[tgt:]
                        cand = "\n".join(cand_lines)
                        if G.structural_fails(cand) or G.region_fails(cand):
                            reasons.append("%s:%s:struct" % (cls.get("name"), m[3]))
                            continue
                        newclasses = CR.parse_file(cand)
                        ncls = None
                        for c in newclasses:
                            if c.get("name") == cls.get("name"):
                                ncls = c
                                break
                        if ncls is None:
                            continue
                        nsegs = line_seg_map(cand.split("\n"))
                        if len(viol(ncls, nsegs, newclasses)) >= len(viol(cls, segs, classes)):
                            reasons.append("%s:%s:no-improve" % (cls.get("name"), m[3]))
                            continue
                        lines = cand_lines
                        moves += 1
                        changed = True
                        done = True
                        break
                    prev = m[0]
                if done:
                    break
            if done:
                break
        if not changed:
            break
    return ("\n".join(lines), moves, reasons)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--fix-victims", action="store_true")
    a = ap.parse_args()
    if a.files:
        files = [os.path.abspath(p) for p in a.files]
    else:
        files = []
        for dp, dn, fns in os.walk(CODE):
            dn[:] = [d for d in dn if d not in SKIP]
            for fn in sorted(fns):
                if fn.endswith(".cs") and not fn.endswith(".Designer.cs"):
                    files.append(os.path.join(dp, fn))
        files.sort()
    if a.report:
        total = 0
        nhit = 0
        for f in files:
            src = open(f, "rb").read().decode("utf-8-sig")
            n = report_viols(src, os.path.relpath(f, CODE))
            total += n
            if n:
                nhit += 1
        print("member-order report: violations=%d files=%d" % (total, nhit))
        return 0
    os.makedirs(SNAP, exist_ok=True)
    t0 = time.time()
    nfix = 0
    for f in files:
        raw = open(f, "rb").read()
        bom = raw[:3] == b"\xef\xbb\xbf"
        src = raw.decode("utf-8-sig")
        before = len(all_viol(src))
        if before == 0:
            continue
        if a.fix_victims:
            new, moved, reasons = fix_victims(src)
        else:
            new, moved, reasons = reorder(src)
        after = len(all_viol(new)) if new else before
        if not moved or after >= before:
            print("SKIP  %-56s (%d) %s" % (os.path.relpath(f, CODE), before, ",".join(reasons[:3])))
            continue
        if a.dry_run:
            print("DRY   %-56s %d -> %d" % (os.path.relpath(f, CODE), before, after))
            continue
        rel = os.path.relpath(f, CODE)
        snap = os.path.join(SNAP, rel.replace("\\", "__"))
        shutil.copy2(f, snap)
        out = new.encode("utf-8")
        if bom:
            out = b"\xef\xbb\xbf" + out
        open(f, "wb").write(out)
        gfs = G.check(f, SNAP)
        if gfs:
            shutil.copy2(snap, f)
            print("ROLLBACK %-50s %s" % (rel, "; ".join(gfs[:2])))
            continue
        nfix += 1
        print("OK    %-56s %d -> %d" % (rel, before, after))
    print("member-order: fixed_files=%d elapsed=%.1fs snapshot=%s" % (nfix, time.time() - t0, SNAP))
    return 0


if __name__ == "__main__":
    sys.exit(main())
