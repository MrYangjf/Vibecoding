# -*- coding: utf-8 -*-
"""每周 Phase 4 Lint 日志截断：保留最新 50 条，旧条目按日期备份"""
import os
import re
import datetime

LOG = r"D:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\workbudddy\Vicoding管理平台\LLMWiki\logs\log.md"
BACKUP_DIR = r"D:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\workbudddy\Vicoding管理平台\LLMWiki\logs\backup"
TODAY = datetime.date.today().isoformat()  # 2026-08-18
BACKUP = os.path.join(BACKUP_DIR, f"log_{TODAY}.md")
KEEP = 50

with open(LOG, encoding="utf-8") as fh:
    lines = fh.readlines()

# 找到所有 ## [ 条目的起始行号（0-based）
idx = [i for i, ln in enumerate(lines) if re.match(r"^## \[", ln)]
total = len(idx)
print(f"log.md 条目数: {total}")

if total <= KEEP:
    print(f"条目数 {total} <= {KEEP}，跳过截断")
else:
    cut = idx[KEEP]  # 第 51 条起始行（保留前 50 条）
    keep_lines = lines[:cut]
    backup_lines = lines[cut:]

    # 备份：若今日备份文件不存在则创建，追加到末尾（保持时间正序）
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_exists = os.path.exists(BACKUP)
    with open(BACKUP, "a", encoding="utf-8") as fh:
        if backup_exists and os.path.getsize(BACKUP) > 0:
            fh.write("\n")
        fh.writelines(backup_lines)

    # 重写 log.md（保留头部 + 前 50 条）
    with open(LOG, "w", encoding="utf-8") as fh:
        fh.writelines(keep_lines)

    # 验证
    with open(LOG, encoding="utf-8") as fh:
        new_idx = [i for i, ln in enumerate(fh.readlines()) if re.match(r"^## \[", ln)]
    with open(BACKUP, encoding="utf-8") as fh:
        b_idx = [i for i, ln in enumerate(fh.readlines()) if re.match(r"^## \[", ln)]

    print(f"截断: 保留 {len(new_idx)} 条, 备份 {len(b_idx)} 条")
    print(f"备份文件: {BACKUP} ({'新建' if not backup_exists else '已存在-追加'})")
    print(f"log.md 头部保留: {len(keep_lines[:6])} 行")
