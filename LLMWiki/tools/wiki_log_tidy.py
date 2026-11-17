#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_log_tidy.py —— log.md 的脚本化整理（排序 + 截断 + 按日备份）

子命令：
  sort     按时间戳重排条目（最新在前）；同日内保持原有相对顺序
  truncate **仅是委托**：真正实现是 `wiki_log.py truncate`（log 截断唯一入口）
  fixhdr   修正不合规条目头（如「时间不可考」段）→ 归入当日并标注
  index    生成 logs/INDEX.md（归档索引：一行一天，可路由）
  all      sort → fixhdr → truncate（委托 wiki_log.py）→ index
退出码：0 成功；1 失败。
"""
import os
import re
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
LOG = os.path.join(LLMWIKI, "logs", "log.md")
BACKUP = os.path.join(LLMWIKI, "logs", "backup")
INDEX = os.path.join(LLMWIKI, "logs", "INDEX.md")
KEEP = 50

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


HDR = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}:\d{2}))?")


def parse_entries(text):
    """返回 (head, [(ts_key, header_line, body_lines)], tail)"""
    lines = text.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("## [")]
    if not idx:
        return lines, [], []
    head = lines[:idx[0]]
    entries = []
    for k, i in enumerate(idx):
        end = idx[k + 1] if k + 1 < len(idx) else len(lines)
        blk = lines[i:end]
        hdr = blk[0]
        m = HDR.match(hdr)
        d = m.group(1) if m else "0000-00-00"
        t = m.group(2) or "00:00:00"
        entries.append((d + " " + t, hdr, blk[1:]))
    tail = []
    return head, entries, tail


def cmd_sort():
    text, bom, nl = rd(LOG)
    head, entries, _ = parse_entries(text)
    # 稳定排序：时间戳降序；同时间戳保持原序
    indexed = list(enumerate(entries))
    indexed.sort(key=lambda x: (x[1][0], -x[0]), reverse=True)
    out = list(head)
    for _, (k, hdr, body) in indexed:
        out.append(hdr)
        out.extend(body)
    while out and not out[-1].strip():
        out.pop()
    wr(LOG, "\n".join(out) + "\n", bom, nl)
    print("已按时间倒序重排 %d 条条目" % len(entries))
    return 0


def cmd_fixhdr():
    """把「## [2026-10-19 时间不可考…]」这类不合规头规范化为 '## [2026-10-19 00:00:00] …（原时间不可考）'"""
    text, bom, nl = rd(LOG)
    lines = text.split("\n")
    n = 0
    for i, l in enumerate(lines):
        if not l.startswith("## ["):
            continue
        if re.match(r"^## \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \S+ \| ", l):
            continue
        m = re.match(r"^## \[(\d{4}-\d{2}-\d{2})([^]]*)\](.*)$", l)
        if not m:
            continue
        d, mid, rest = m.group(1), m.group(2), m.group(3)
        note = "（原时间不可考）" if ("不可考" in mid or "未知" in mid) else ""
        mid2 = re.sub(r"\s*时间不可考.*$", "", mid).strip()
        tm = re.search(r"(\d{2}:\d{2}:\d{2})", mid2)
        ts = tm.group(1) if tm else "00:00:00"
        lines[i] = "## [%s %s]%s%s" % (d, ts, rest if rest.startswith(" ") else " " + rest.strip(), note)
        n += 1
        print("  修正条目头: %s" % lines[i][:110])
    wr(LOG, "\n".join(lines), bom, nl)
    print("修正不合规条目头 %d 处" % n)
    return 0


def scan(path):
    """返回 (日期, 条目数, 首条标题)；无条目返回 None"""
    if not os.path.isfile(path):
        return None
    t = rd(path)[0]
    hdrs = [l for l in t.split("\n") if l.startswith("## [")]
    if not hdrs:
        return None
    m = HDR.match(hdrs[0])
    d = m.group(1) if m else "?"
    title = hdrs[0].split("]", 1)[-1].strip()
    if title.startswith("|"):
        title = title[1:].strip()
    return d, len(hdrs), title


def cmd_index():
    lines = ["---",
             "title: Log Index — 日志与历史归档索引",
             "date: 2026-11-02",
             "updated: 2026-11-02",
             "tags: [索引, 日志, 历史, 归档]",
             "status: active",
             "---",
             "",
             "# Log Index — 日志与历史归档索引",
             "",
             "> **本文件由 `python tools/wiki_log_tidy.py index` 生成，⛔ 禁手工编辑。**",
             "> **链路**：`logs/log.md`（当轮明细，上限 50 条）→ `logs/backup/log_YYYY-MM-DD.md`（跨轮归档）→ 本索引（可路由）→ `LLMWiki_backup_*.tar.gz`（整库快照）。",
             "> **纪律**：截断是**归档不是丢弃**；⛔ 任何直接删除旧条目的做法都会断掉历史链路。",
             "",
             "---",
             "",
             "## 一、当轮日志（logs/log.md）",
             ""]
    cur = scan(LOG)
    if cur:
        lines.append("| 项 | 值 |")
        lines.append("|---|---|")
        lines.append("| 文件 | `logs/log.md` |")
        lines.append("| 条目数 | %d（上限 50） |" % cur[1])
        lines.append("| 最新条目 | %s |" % cur[2])
    else:
        lines.append("> 暂无当轮日志条目。")
    lines += ["", "---", "", "## 二、跨轮归档（logs/backup/）", "",
              "| 日期 | 条目数 | 首条摘要 | 归档文件 |",
              "|---|---|---|---|"]
    rows = []
    if os.path.isdir(BACKUP):
        for f in sorted(os.listdir(BACKUP), reverse=True):
            if not f.startswith("log_") or not f.endswith(".md"):
                continue
            r = scan(os.path.join(BACKUP, f))
            if not r:
                continue
            d, n, title = r
            # 归档日以**文件名**为准（log_YYYY-MM-DD.md），条目内的日期可能是更早的补录
            fd = f[len("log_"):-len(".md")]
            rows.append("| %s | %d | %s | `logs/backup/%s` |" % (fd, n, title.replace("|", "／")[:70], f))
    if rows:
        lines += rows
    else:
        lines.append("| — | — | 暂无归档 | — |")
    lines += ["", "> **查法**：先在本表定位日期 → 再读对应归档文件；⛔ 不要凭记忆断言「上次是怎么处理的」。",
              "", "## 相关页面", "",
              "- [[project/vibecoding-workflow]] —— Phase 0~4 流程规范",
              "- [[standards/WikiPageFormatSpec]] —— 页面格式契约（§2.5 log 条目契约）",
              ""]
    os.makedirs(os.path.dirname(INDEX), exist_ok=True)
    txt = "\n".join(lines)
    wr(INDEX, txt, False, "\n")
    print("已生成 logs/INDEX.md：%d 行（当轮 %d 条 / 归档 %d 天）"
          % (len(lines), cur[1] if cur else 0, len(rows)))
    return 0

def cmd_truncate(argv):
    """委托 wiki_log.cmd_truncate —— 截断实现只有一份，避免两处逻辑漂移"""
    if TOOLS_DIR not in sys.path:
        sys.path.insert(0, TOOLS_DIR)
    import wiki_log
    return wiki_log.cmd_truncate(argv)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    rest = sys.argv[2:]
    if cmd == "sort":
        return cmd_sort()
    if cmd == "fixhdr":
        return cmd_fixhdr()
    if cmd == "truncate":
        return cmd_truncate(rest)
    if cmd == "index":
        return cmd_index()
    if cmd == "all":
        cmd_sort()
        cmd_fixhdr()
        rc = cmd_truncate(rest)
        cmd_index()
        return rc
    print("未知子命令：%s（可用 sort / fixhdr / truncate / index / all）" % cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())
