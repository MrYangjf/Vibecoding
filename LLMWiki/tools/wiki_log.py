#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_log.py —— 变更日志的脚本化写入与截断（唯一允许详细记录的载体）

子命令：
  append   在 logs/log.md 顶部追加一条变更记录（时间戳由脚本取，禁止手填）
  truncate **log 截断的唯一入口**：保留最新 N 条，旧条目按日期归档到
           logs/backup/log_YYYY-MM-DD.md，并自动重建 logs/INDEX.md 归档索引
  show     打印当前条目数与首条摘要（自检用）

⛔ 截断是**归档不是丢弃**；⛔ 不要另建截断脚本（历史脚本 truncate_log.py 已删除）。

条目格式：
  ## [YYYY-MM-DD HH:mm:ss] <op> | <标题>
  - 来源：...
  - 操作：...
  - 变更文件：...
  - 结论 / 遗留：...

退出码：0 成功；1 参数错误或写入失败。
"""
import os
import re
import sys
import datetime

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
LOG = os.path.join(LLMWIKI, "logs", "log.md")
BACKUP_DIR = os.path.join(LLMWIKI, "logs", "backup")
MAX_ENTRIES = 50


def read_log():
    if not os.path.isfile(LOG):
        return None
    with open(LOG, "rb") as f:
        raw = f.read()
    bom = raw[:3] == b"\xef\xbb\xbf"
    body = raw[3:] if bom else raw
    crlf = body.count(b"\r\n")
    lf = body.count(b"\n") - crlf
    nl = "\r\n" if crlf > lf else "\n"
    return body.decode("utf-8", errors="replace").replace("\r\n", "\n"), bom, nl


def write_log(text, bom, nl):
    out = text.replace("\r\n", "\n").replace("\n", nl).encode("utf-8")
    if bom:
        out = b"\xef\xbb\xbf" + out
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "wb") as f:
        f.write(out)


def entry_starts(lines):
    return [i for i, l in enumerate(lines) if l.startswith("## [")]


def cmd_append(argv):
    if len(argv) < 3:
        print("用法: wiki_log.py append <op> <标题> [--src 来源] [--op-list \"a; b; c\"] [--files \"x; y\"] [--note 结论]")
        return 1
    op, title = argv[0], argv[1]
    src, ops, files, note = "", "", "", ""
    i = 2
    while i < len(argv):
        k = argv[i]
        v = argv[i + 1] if i + 1 < len(argv) else ""
        if k == "--src": src = v
        elif k == "--op-list": ops = v
        elif k == "--files": files = v
        elif k == "--note": note = v
        i += 2
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = ["## [%s] %s | %s" % (now, op, title)]
    entry.append("- 来源：%s" % (src or "-"))
    if ops:
        parts = [p.strip() for p in ops.split(";") if p.strip()]
        entry.append("- 操作：")
        for n, p in enumerate(parts, 1):
            entry.append("  %d. %s" % (n, p))
    else:
        entry.append("- 操作：-")
    entry.append("- 变更文件：%s" % (files or "-"))
    entry.append("- 结论 / 遗留：%s" % (note or "-"))
    entry.append("")
    block = "\n".join(entry)

    data = read_log()
    if data is None:
        head = ["# Wiki Log — 变更日志", "",
                "> 时间导向的追加日志。每条记录以 `## [日期时间] 操作类型 | 描述` 开头。",
                "> **最新记录始终在最前面**。", "", "---", ""]
        text = "\n".join(head) + block + "\n"
        write_log(text, False, "\n")
        print("已创建 logs/log.md 并写入 1 条记录：%s" % now)
        return 0
    text, bom, nl = data
    lines = text.split("\n")
    idx = entry_starts(lines)
    insert_at = idx[0] if idx else len(lines)
    # 保持「---」分隔符结构：新条目插在第一条 ## [ 之前
    new_lines = lines[:insert_at] + block.split("\n")[:-1] + [""] + lines[insert_at:]
    write_log("\n".join(new_lines), bom, nl)
    print("已写入 1 条记录：%s（当前 %d 条）" % (now, len(entry_starts(new_lines))))
    return 0


def rebuild_index():
    """截断后重建 logs/INDEX.md 归档索引（截断=归档，归档必须可路由）
    索引生成逻辑归属 wiki_log_tidy.py（避免两处各写一份）"""
    if TOOLS_DIR not in sys.path:
        sys.path.insert(0, TOOLS_DIR)
    import wiki_log_tidy
    return wiki_log_tidy.cmd_index()


HDR = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}:\d{2}))?")


def parse_entries(text):
    """返回 (head, [(ts_key, header_line, body_lines)])"""
    lines = text.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("## [")]
    if not idx:
        return lines, []
    head = lines[:idx[0]]
    entries = []
    for k, i in enumerate(idx):
        end = idx[k + 1] if k + 1 < len(idx) else len(lines)
        blk = lines[i:end]
        m = HDR.match(blk[0])
        d = m.group(1) if m else "0000-00-00"
        t = m.group(2) or "00:00:00"
        entries.append((d + " " + t, blk[0], blk[1:]))
    return head, entries


def cmd_truncate(argv):
    """log 截断的唯一实现：保留最新 N 条，旧条目按日期归档，并重建归档索引"""
    keep = int(argv[0]) if argv else MAX_ENTRIES
    data = read_log()
    if data is None:
        print("logs/log.md 不存在，无需截断")
        return 0
    text, bom, nl = data
    head, entries = parse_entries(text)
    if len(entries) <= keep:
        print("当前 %d 条 ≤ 上限 %d，无需截断" % (len(entries), keep))
        return 0
    keep_set = entries[:keep]
    old = entries[keep:]
    os.makedirs(BACKUP_DIR, exist_ok=True)
    byday = {}
    for k, hdr, body in old:
        byday.setdefault(k.split()[0], []).append((k, hdr, body))
    for d in sorted(byday):
        bp = os.path.join(BACKUP_DIR, "log_%s.md" % d)
        exist = ""
        if os.path.isfile(bp):
            with open(bp, "rb") as f:
                rb = f.read()
            exist = rb.decode("utf-8", errors="replace").replace("\r\n", "\n").rstrip("\n") + "\n"
        chunk = []
        for k, hdr, body in byday[d]:
            chunk.append(hdr)
            chunk.extend(body)
        with open(bp, "wb") as f:
            f.write((exist + "\n".join(chunk).rstrip("\n") + "\n").encode("utf-8"))
    out = list(head)
    for k, hdr, body in keep_set:
        out.append(hdr)
        out.extend(body)
    while out and not out[-1].strip():
        out.pop()
    write_log("\n".join(out) + "\n", bom, nl)
    print("已截断：保留最新 %d 条，归档 %d 条 → %s" % (keep, len(old), BACKUP_DIR))
    rebuild_index()
    return 0


def cmd_show(argv):
    data = read_log()
    if data is None:
        print("logs/log.md 不存在")
        return 1
    text = data[0]
    lines = text.split("\n")
    idx = entry_starts(lines)
    print("当前条目数: %d（上限 %d）" % (len(idx), MAX_ENTRIES))
    for i in idx[:3]:
        print("  " + lines[i][:100])
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    rest = sys.argv[2:]
    if cmd == "append":
        return cmd_append(rest)
    if cmd == "truncate":
        return cmd_truncate(rest)
    if cmd == "show":
        return cmd_show(rest)
    print("未知子命令：%s（可用 append / truncate / show）" % cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())
