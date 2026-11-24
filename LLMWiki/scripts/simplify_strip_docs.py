# -*- coding: utf-8 -*-
"""simplify_strip_docs.py —— 文档注释瘦身器（移除 <remarks> + summary 压到 ≤20 字）。

口径（2026-11-19 业主裁定）：
  · <remarks> **一律移除**（含多行块）—— 约束/历史/裁定由 LLMWiki 承载，不在代码复述
  · <summary> **一行 ≤20 汉字**，只记作用；余文 **直接删除**（不迁 remarks、不进 wiki）
  · 只改注释文本（不动任何代码字符）—— 写回前用 simplify_guard.check_text 校验
  · 逐文件快照可回滚；BOM / 行尾 / CRLF 增量守恒

用法：
  python simplify_strip_docs.py --all [--dry-run]
  python simplify_strip_docs.py --files a.cs b.cs [--dry-run]
  python simplify_strip_docs.py --all --verify-only     # 只统计不写
"""
import os, re, sys, shutil, argparse, time

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import simplify_guard as G

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CODE = os.path.join(ROOT, "AdaWeldSystem")
SNAP = os.path.join(ROOT, "_simplify_snapshot")
SKIP = {"bin", "obj", "3rdDepend", ".vs"}
CJK = re.compile(r"[\u4e00-\u9fff]")
LIMIT = 20


def cjk_count(s):
    return len(CJK.findall(s))


def split_summary(plain, limit=LIMIT):
    """按自然断点切分 summary：括号或括号外冒号优先，超限再硬切。

    返回 (保留部分, 余文)。余文由调用方 **丢弃**（不进 remarks）。
    """
    depth, cjk, cands = 0, 0, []
    for i, ch in enumerate(plain):
        if ch in "（(":
            if depth == 0 and 4 <= cjk <= limit:
                cands.append(i)
            depth += 1
        elif ch in "）)":
            depth = max(0, depth - 1)
        elif ch in "：:" and depth == 0 and 4 <= cjk <= limit:
            cands.append(i)
        if CJK.match(ch):
            cjk += 1
        if cjk > limit:
            break
    if cjk <= limit:
        return plain, ""
    if cands:
        i = cands[-1]
        rest = plain[i:].strip().lstrip("（(：:，,；;、 ")
        if plain[i] in "（(":
            rest = rest.rstrip("。").rstrip("）)")
        return plain[:i].strip(), rest
    acc = ""
    for ch in plain:
        if cjk_count(acc + ch) > limit:
            break
        acc += ch
    return acc.strip(), plain[len(acc):].strip()


def strip_remarks(text):
    """移除全部 <remarks>...</remarks> 块（含跨行、含 <para>/<list> 等内嵌标签）。

    返回 (新文本, 删除处数)。
    """
    n = 0
    out = []
    i = 0
    while True:
        m = re.search(r"<remarks>", text[i:])
        if not m:
            out.append(text[i:])
            break
        start = i + m.start()
        end_m = re.search(r"</remarks>", text[start:])
        if not end_m:
            out.append(text[i:])
            break
        end = start + end_m.end()
        # 连带吃掉该 remarks 所在的 /// 前缀行（可能多行）
        seg = text[start:end]
        # 向前回退到最近的 /// 行首
        line_start = text.rfind("\n", 0, start) + 1
        prefix = text[line_start:start]
        if prefix.strip().startswith("///"):
            start = line_start
            seg = text[start:end]
        # 向后吃掉到行尾（含换行）
        nl = text.find("\n", end)
        if nl == -1:
            seg = text[start:]
            end = len(text)
        else:
            seg = text[start:nl]
            end = nl
        out.append(text[i:start])
        i = end
        n += 1
    return "".join(out), n


def compress_summary(text):
    """把 <summary> 压成一行 ≤20 汉字；余文丢弃。

    返回 (新文本, 是否改动, 丢弃字数)。
    """
    m = re.search(r"<summary>(.*?)</summary>", text, re.S)
    if not m:
        return text, False, 0
    inner = m.group(1)
    plain = re.sub(r"\s*///\s*", " ", inner).strip()
    plain = re.sub(r"\s+", " ", plain)
    if not plain:
        return text, False, 0
    acc, rest = split_summary(plain)
    if not rest and inner.strip().count("\n") == 0 and "///" not in inner:
        return text, False, 0
    # 单行化（标签内不留多余空格）
    new_inner = acc
    new_tag = "<summary>" + new_inner + "</summary>"
    text = text[:m.start()] + new_tag + text[m.end():]
    return text, True, cjk_count(rest)


def fix_doc_block(block):
    """对单个 /// 连续块做精简。返回 (新块, 删remarks数, 压summary数, 丢弃字数)。"""
    text = "\n".join(block)
    text, nrm = strip_remarks(text)
    text, nsum, dropped = compress_summary(text)
    # 清掉可能残留的空 /// 行（整行只有 ///）
    lines = [l for l in text.split("\n") if l.strip() != "///"]
    # 去尾部空行
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    return lines, nrm, nsum, dropped


def collect_blocks(lines):
    """返回 [(start, end)] 连续 /// 块的行号区间。"""
    res = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("///"):
            j = i
            while j < len(lines) and lines[j].strip().startswith("///"):
                j += 1
            res.append((i, j))
            i = j
        else:
            i += 1
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args()

    if a.files:
        files = [os.path.abspath(p) for p in a.files]
    else:
        files = []
        for dp, dn, fn in os.walk(CODE):
            dn[:] = [d for d in dn if d not in SKIP]
            for f in sorted(fn):
                if f.endswith(".cs") and not f.endswith(".Designer.cs"):
                    files.append(os.path.join(dp, f))
        files.sort()

    os.makedirs(SNAP, exist_ok=True)
    t0 = time.time()
    tot = {"files": 0, "remarks": 0, "summary": 0, "dropped": 0}
    nf = 0

    for f in files:
        raw = open(f, "rb").read()
        bom = raw[:3] == b"\xef\xbb\xbf"
        # 行尾：读时归一化 CRLF→LF，写时按原状加回（⛔ 禁混行）
        crlf = raw.count(b"\r\n") > 0 and (raw.count(b"\n") - raw.count(b"\r\n")) == 0
        text_all = raw.decode("utf-8-sig").replace("\r\n", "\n")
        lines = text_all.split("\n")
        blocks = collect_blocks(lines)
        if not blocks:
            continue

        new_lines = list(lines)
        edits = []   # (start, end, payload)
        for (bs, be) in blocks:
            blk = lines[bs:be]
            nblk, nrm, nsum, dropped = fix_doc_block(blk)
            if nblk != blk:
                edits.append((bs, be, nblk))
                tot["remarks"] += nrm
                tot["summary"] += nsum
                tot["dropped"] += dropped

        if not edits:
            continue
        nf += 1
        if a.verify_only:
            print("STAT  %-58s blocks=%d" % (os.path.relpath(f, CODE), len(edits)))
            continue

        # 从后往前替换
        edits.sort(key=lambda e: e[0], reverse=True)
        out = list(lines)
        for s, e, payload in edits:
            out[s:e] = payload
        cand = "\n".join(out)

        # 行尾守恒：CRLF 基线统一加回 \r
        cand = "\n".join(out)
        if crlf:
            cand = cand.replace("\n", "\r\n")
        cand_raw = cand.encode("utf-8")
        if bom:
            cand_raw = b"\xef\xbb\xbf" + cand_raw

        broken = G.check_text(cand, cand_raw, text_all, raw)
        if broken:
            print("SKIP  %-56s %s" % (os.path.relpath(f, CODE), "; ".join(broken[:3])))
            continue

        if a.dry_run:
            print("DRY   %-58s blocks=%d" % (os.path.relpath(f, CODE), len(edits)))
            continue

        rel = os.path.relpath(f, CODE)
        snap = os.path.join(SNAP, rel.replace("\\", "__"))
        shutil.copy2(f, snap)
        open(f, "wb").write(cand_raw)
        gfs = G.check(f, SNAP)
        if gfs:
            shutil.copy2(snap, f)
            print("ROLLBACK %-50s %s" % (rel, "; ".join(gfs[:3])))
            continue
        print("OK    %-58s blocks=%d" % (rel, len(edits)), flush=True)

    tot["files"] = nf
    print("strip: files=%d remarks=%d summary=%d dropped=%d elapsed=%.1fs"
          % (nf, tot["remarks"], tot["summary"], tot["dropped"], time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
