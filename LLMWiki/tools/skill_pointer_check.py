#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_pointer_check.py —— Skill 指向健康度检查（防漂移闸门）

Skill 的职责是「怎么查」，不是「查哪一页」。本页会随 wiki 重组而失效的具体页引用，
一旦写死就会指向不存在的页 —— 且漂移后比没有更危险（读者以为那是权威）。

判据：
  C1 写死的内容页引用（具体 ADR / lessons / guides / modules / api / people 页）
     —— 只允许「角色级锚点」（目录/索引/规范页），其余必须改成「去哪查」的机制表述
  C2 Skill 引用的 wiki 页必须真实存在（红链 = 失效指向）
  C3 Skill 引用的 tools 脚本必须真实存在
  C4 Skill 引用的 ADR 号必须在现行 ADR 页中存在
  C5 不得出现「内容清单表」——即连续 3 行以上形如 '| ADR-xxx |' 或 '| 历史教训 |' 的表
退出码：0 通过；1 存在违规。
"""
import os
import re
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
WIKI = os.path.join(LLMWIKI, "wiki")
SKILLS = [
    os.path.join(LLMWIKI, "skills", "vibecoding-llmwiki", "SKILL.md"),
    os.path.join(os.path.expanduser("~"), ".trae-cn", "skills", "vibecoding-llmwiki", "SKILL.md"),
]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 角色级锚点：长期稳定的目录/索引/规范页
ROLE_PAGES = {
    "index/index", "decisions/ADR-Index", "architecture/CodeMap",
    "architecture/DeviceControlArchitecture", "project/vibecoding-workflow",
    "standards/WikiPageFormatSpec", "guides/ExecutionEnvironment",
    "guides/RawAssetCatalog",
}

violations = []


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8", errors="replace").replace("\r\n", "\n")


def main():
    pages = set()
    for dp, dn, fn in os.walk(WIKI):
        for f in fn:
            if f.endswith(".md"):
                pages.add(os.path.relpath(os.path.join(dp, f), WIKI).replace("\\", "/")[:-3])
    adrs = set(f[:-3] for f in os.listdir(os.path.join(WIKI, "decisions")) if f.endswith(".md"))
    tools = set(f for f in os.listdir(os.path.join(LLMWIKI, "tools")) if f.endswith(".py"))

    for skill in SKILLS:
        if not os.path.isfile(skill):
            continue
        tag = "仓库版" if LLMWIKI in skill else "用户级"
        text = read(skill)
        L = text.split("\n")

        # C1 写死内容页
        for i, l in enumerate(L, 1):
            for m in re.finditer(r"(?:ADR-\d{3}-[A-Za-z0-9\-]+|(?:lessons|guides|modules|api|standards|people|project|architecture)/[A-Za-z0-9\-]+)", l):
                t = m.group(0)
                if "XXX" in t or "old" in t or "new" in t or "<" in t or "..." in t or "N" * 3 in t:
                    continue          # 模板占位符，非真实指向
                key = ("decisions/" + t) if t.startswith("ADR-") else t
                if key in ROLE_PAGES:
                    continue
                if key.split("/")[-1] in {p.split("/")[-1] for p in ROLE_PAGES}:
                    continue
                violations.append("%s SKILL.md:%d [C1-写死内容页] %s" % (tag, i, t))

        # C2 红链
        for i, l in enumerate(L, 1):
            for m in re.finditer(r"\[\[([^\]|#]+)", l):
                t = m.group(1).strip()
                if t.startswith(("raw/", "logs/", "wiki/")) or t in ("...", "X", "links", "new", "old", "reference"):
                    continue
                if "XXX" in t or "<" in t or "..." in t or "N" * 3 in t:
                    continue          # 模板占位符，非真实指向
                if t not in pages:
                    violations.append("%s SKILL.md:%d [C2-红链] [[%s]]" % (tag, i, t))

        # C3 工具脚本
        for m in set(re.findall(r"tools/([A-Za-z0-9_]+\.py)", text)):
            if m not in tools:
                violations.append("%s SKILL.md [C3-工具缺失] tools/%s" % (tag, m))

        # C4 ADR 号
        for no in set(re.findall(r"ADR-(\d{3})", text)):
            if not any(f.startswith("ADR-" + no + "-") for f in adrs):
                violations.append("%s SKILL.md [C4-ADR号不存在] ADR-%s" % (tag, no))

        # C5 内容清单表
        run = 0
        for i, l in enumerate(L, 1):
            if re.match(r"^\|\s*\*?\*?(ADR-\d{3}|Historical Lesson|ADR \|)", l) or \
               re.match(r"^\|\s*(DesignerCs|CodeProjectRegistration|AutoProperty|UI-Thread|LiveMode|Bounds|Assimp|UILight)", l):
                run += 1
                if run >= 3:
                    violations.append("%s SKILL.md:%d [C5-内容清单表] 连续 %d 行具体条目表（应改为机制表述）" % (tag, i, run))
            else:
                run = 0

    print("=" * 70)
    print("skill_pointer_check —— Skill 指向健康度（防漂移）")
    print("=" * 70)
    if violations:
        print("违规 %d 处：" % len(violations))
        for v in violations:
            print("  " + v)
        return 1
    print("通过：Skill 只含角色级锚点，无写死内容页 / 无红链 / 工具与 ADR 号均有效")
    return 0


if __name__ == "__main__":
    sys.exit(main())
