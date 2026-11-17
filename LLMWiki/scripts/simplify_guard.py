# -*- coding: utf-8 -*-
"""simplify_guard.py —— 代码精简批改的**结构守卫**（改码前后必跑）。

检查项（任一 FAIL 即必须回滚）：
  1. 花括号平衡
  2. **命名空间级结构**：namespace 作用域内不得出现成员声明/孤立语句/裸块（2026-10-26 新增）
  3. XML 文档标签闭合（summary/remarks/param/returns/exception）
  4. #region / #endregion 配对（2026-10-26 新增）
  5. 成员多重集差分（--baseline：丢成员 / 多出重复成员都报，2026-10-26 由 set 升级）
  6. 行尾同质（CRLF/LF 混合、CRCRLF）与 BOM 守恒（--baseline）
  7. 缩进同质（同一连续 /// 段内前导空白一致）

用法：
  python simplify_guard.py                        # 全库体检
  python simplify_guard.py <file.cs> [...]        # 指定文件
  python simplify_guard.py --baseline <快照目录>   # 与改前快照比对
退出码：0 = 全绿；1 = 有 FAIL。
"""
import os, re, sys, argparse, collections

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CODE = os.path.join(ROOT, "AdaWeldSystem")
SKIP = {"bin", "obj", "3rdDepend", ".vs"}
TAGS = ("summary", "remarks", "param", "returns", "exception")
TYPE_DECL = re.compile(
    r"^(?:(?:public|internal|private|protected|static|sealed|abstract|partial|unsafe|new|ref|readonly)\s+)*"
    r"(?:class|struct|interface|enum|delegate)\s+\w+")
NS_PREFIX = ("using ", "namespace ", "extern alias ", "[", "}")
BLOCK_KEYWORDS = ("try", "finally")


def strip_literals_and_comments(text):
    """把字符串/字符/注释替换为空格（保留换行），用于纯结构判读。"""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        # 行注释（含 ///）
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
            continue
        # 块注释
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join("\n" if ch == "\n" else " " for ch in text[i:j]))
            i = j
            continue
        # 逐字/插值字符串前缀
        verbatim = False
        if c == "@" and i + 1 < n and text[i + 1] == '"':
            verbatim = True
            i += 1
            c = text[i]
        elif c == "$" and i + 1 < n and text[i + 1] == "@" and i + 2 < n and text[i + 2] == '"':
            verbatim = True
            i += 2
            c = text[i]
        elif c == "@" and i + 1 < n and text[i + 1] == "$" and i + 2 < n and text[i + 2] == '"':
            verbatim = True
            i += 2
            c = text[i]
        elif c == "$" and i + 1 < n and text[i + 1] == '"':
            i += 1
            c = text[i]
        if c == '"':
            j = i + 1
            while j < n:
                if text[j] == "\n":
                    break
                if verbatim and text[j] == '"':
                    if j + 1 < n and text[j + 1] == '"':
                        j += 2
                        continue
                    break
                if not verbatim and text[j] == "\\":
                    j += 2
                    continue
                if not verbatim and text[j] == '"':
                    break
                j += 1
            out.append("".join("\n" if ch == "\n" else " " for ch in text[i:j + 1]))
            i = j + 1
            continue
        if c == "'":
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == "'":
                    break
                j += 1
            out.append(" " * (min(j + 1, n) - i))
            i = j + 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _is_type_or_ns(t):
    return bool(TYPE_DECL.match(t)) or t.startswith("namespace ")


def _allowed_at_ns(t, attr_depth=False):
    if t in ("{", "}", "};", ";"):
        return True
    if t.startswith(NS_PREFIX):
        return True
    if _is_type_or_ns(t):
        return True
    if t.startswith(":") or t.startswith("where "):
        return True
    if attr_depth:
        return True
    return False


def _next_nonempty(lines, idx):
    for j in range(idx, len(lines)):
        t = lines[j].strip()
        if t:
            return t
    return ""


def structural_fails(text):
    """命名空间级结构判据：成员/语句跑到 namespace 作用域即 FAIL。

    2026-10-26 事故：类闭合 `}` 被提前，成员被挤到类外——花括号总数仍平衡，
    旧守卫全绿。本判据按「行首深度 + 作用域种类」抓这类位置错误。
    """
    code = strip_literals_and_comments(text)
    body_lines = code.split("\n")
    raw_lines = text.split("\n")
    fails = []
    depth = 0
    attr_depth = 0
    prev = ""
    for idx, line in enumerate(body_lines, 1):
        raw = raw_lines[idx - 1] if idx - 1 < len(raw_lines) else ""
        if raw.lstrip().startswith("#"):
            continue
        t = line.strip().lstrip("\ufeff")
        if t:
            if depth <= 1 and not _allowed_at_ns(t, attr_depth > 0):
                fails.append("ns-scope line %d depth=%d: %s" % (idx, depth, raw.strip()[:70]))
            if depth <= 1 and t == "{" and not (_is_type_or_ns(prev) or prev.endswith(":")):
                fails.append("bare-block line %d: %s" % (idx, raw.strip()[:70]))
            if t in BLOCK_KEYWORDS:
                nxt = _next_nonempty(body_lines, idx)
                if not nxt.startswith("{"):
                    fails.append("missing-brace line %d: %s" % (idx, t))
            prev = t
        attr_depth += line.count("[") - line.count("]")
        if attr_depth < 0:
            attr_depth = 0
        depth += line.count("{") - line.count("}")
        if depth < 0:
            fails.append("brace-underflow line %d" % idx)
            depth = 0
    if depth != 0:
        fails.append("brace-final=%d" % depth)
    return fails


def region_fails(text):
    """#region / #endregion 配对与嵌套检查。"""
    fails = []
    d = 0
    for i, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if s.startswith("#region"):
            d += 1
        elif s.startswith("#endregion"):
            if d == 0:
                fails.append("endregion-without-region line %d" % i)
            else:
                d -= 1
    if d:
        fails.append("region-unclosed=%d" % d)
    return fails


MEMBER_RE = r"\b(?:class|struct|interface|enum)\s+(\w+)"
MEMBER_DECL = (r"\b(?:public|private|protected|internal)\s+"
               r"(?:static\s+|virtual\s+|override\s+|abstract\s+|sealed\s+|async\s+|"
               r"readonly\s+|const\s+|event\s+|partial\s+|new\s+)*"
               r"(?:[\w<>\[\],\.]+)\s+(\w+)\s*(?:\(|;|\{|=>)")


def members(text):
    """成员多重集（不是集合）：重复声明会体现为计数增加。"""
    s = collections.Counter()
    for m in re.finditer(MEMBER_RE, text):
        s["T" + m.group(1)] += 1
    for m in re.finditer(MEMBER_DECL, text):
        s["M" + m.group(1)] += 1
    return s


def eol_of(raw):
    cr = raw.count(b"\r\n")
    lf = raw.count(b"\n") - cr
    return cr, lf, raw.count(b"\r\r\n"), raw[:3] == b"\xef\xbb\xbf"


def indent_check(lines):
    bad = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("///"):
            j = i
            while j < len(lines) and lines[j].strip().startswith("///"):
                j += 1
            inds = set(len(re.match(r"^(\s*)", lines[k]).group(1)) for k in range(i, j))
            if len(inds) > 1:
                bad.append(i + 1)
            i = j
        else:
            i += 1
    return bad


def check_text(text, raw=None, baseline_text=None, baseline_raw=None):
    fails = []
    if text.count("{") != text.count("}"):
        fails.append("brace-imbalance %d/%d" % (text.count("{"), text.count("}")))
    fails.extend(structural_fails(text))
    fails.extend(region_fails(text))
    for tg in TAGS:
        o = len(re.findall(r"<%s[ >]" % tg, text))
        c = len(re.findall(r"</%s>" % tg, text))
        if o != c:
            fails.append("xml-tag <%s> %d/%d" % (tg, o, c))
    bad = indent_check(text.split("\n"))
    if bad:
        fails.append("indent-mixed at line %s" % bad[:3])
    if raw is not None:
        cr = raw.count(b"\r\n")
        lf = raw.count(b"\n") - cr
        if cr > 0 and lf > 0:
            fails.append("eol-mixed crlf=%d loneLF=%d" % (cr, lf))
        if raw.count(b"\r\r\n"):
            fails.append("crcrlf=%d" % raw.count(b"\r\r\n"))
    if baseline_text is not None:
        lost = members(baseline_text) - members(text)
        added = members(text) - members(baseline_text)
        if lost:
            fails.append("member-lost %s" % sorted(lost)[:5])
        if added:
            fails.append("member-added %s" % sorted(added)[:5])
    if baseline_raw is not None and raw is not None:
        bc, bl, bcc, bbom = eol_of(baseline_raw)
        cc, cl, ccc, cbom = eol_of(raw)
        added = len(text.split("\n")) - len(baseline_text.split("\n"))
        if bbom != cbom:
            fails.append("bom-changed")
        if bcc != ccc:
            fails.append("crcrlf-changed")
        if bc > 0:
            # CRLF 基线：loneLF 必须保持 0；CRLF 增量必须等于新增行数
            if cl != 0:
                fails.append("lone-lf-added=%d" % cl)
            if cc - bc != added:
                fails.append("crlf-drift %d!=%d" % (cc - bc, added))
        else:
            # LF 基线：不得引入 CRLF；LF 增量必须等于新增行数
            if cc != 0:
                fails.append("crlf-introduced=%d" % cc)
            if cl - bl != added:
                fails.append("lf-drift %d!=%d" % (cl - bl, added))
    return fails


def check(path, baseline=None):
    raw = open(path, "rb").read()
    text = raw.decode("utf-8-sig", errors="replace")
    btext = braw = None
    if baseline:
        bp = os.path.join(baseline, os.path.relpath(path, CODE).replace("\\", "__"))
        if os.path.exists(bp):
            braw = open(bp, "rb").read()
            btext = braw.decode("utf-8-sig", errors="replace")
    return check_text(text, raw, btext, braw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--baseline", default=None)
    a = ap.parse_args()
    if a.paths:
        files = [os.path.abspath(p) for p in a.paths]
    else:
        files = []
        for dp, dn, fns in os.walk(CODE):
            dn[:] = [d for d in dn if d not in SKIP]
            for fn in sorted(fns):
                if fn.endswith(".cs") and not fn.endswith(".Designer.cs"):
                    files.append(os.path.join(dp, fn))
    nfail = 0
    for f in files:
        try:
            fs = check(f, a.baseline)
        except Exception as e:
            fs = ["exception %s" % e]
        if fs:
            nfail += 1
            print("FAIL %-68s %s" % (os.path.relpath(f, CODE), "; ".join(fs)))
    print("guard: files=%d fail=%d  %s" % (len(files), nfail, "PASS" if nfail == 0 else "NOT-PASS"))
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
