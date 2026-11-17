#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ingest_purity_scan.py —— 知识沉淀纯度强制检查（2026-10-14 业主裁定，第四扫描器）

背景：知识沉淀步骤曾出现「随意发挥」——把验证叙事（静态 N/N PASS、阴性对照、探针实测）、
批次进度、日期沿革、日志体等长篇记录回灌进只允许结构化内容的页面
（index 头部 9 行日志堆积、CodeMap 批次行、ADR-Index 日期 bullet 等，2026-10-14 已全部清理）。
本脚本以机械判据拦截回灌：Phase 4 Lint 必跑，违规非零退出。

扫描范围（七类页面；project/ guides/ modules/ api/ people/ 与 decisions/ 单个 ADR 页的
「验证」节属合法沉淀位置，log.md 与 logs/backup/ 是日志层本身，均豁免）：
  R1 wiki/index/index.md          只允许结构化索引（页面路由 / 表格 / 判据指针）
  R2 wiki/decisions/ADR-Index.md  只允许编号权威 + ADR 总表
  R3 wiki/architecture/CodeMap.md 只允许「代码块→实现的接口/功能 + 依据判断」对应表
  R4 wiki/architecture/*.md       只允许最新架构设计与实现位置（依据判断允许，验证叙事不允许）
  R5 wiki/lessons/*.md            教训页只查「纯日志体」（条目标题 / 「此前」）—— 记录事故是它的正当内容
  R6 wiki/standards/*.md          规范页禁「过程叙述」（探针实测 / 实测数据 / 静态 N/N PASS）
  R7 wiki/rules/*.md              规则页禁「过程叙述」（同上）

  ⚠️ 判据设计说明（2026-11-02 首版误报复盘）：**不按关键词查，按实质特征查**。
     「阴性对照」是判据区分度的标准术语、「回滚点」是 backup 业务术语 —— 按关键词查会误报；
     且 standards / rules 页里的自指行（「⛔ 不得含验证叙事（静态 N/N · 阴性对照 · 探针实测）」）
     本身就是在描述禁令，命中即自指误报，故自指行整体豁免。

退出码：0 = 通过；1 = 存在违规（逐条打印 文件:行号 [规则] 摘要）
路径：一律由 __file__ 推导，禁硬编码绝对路径。
"""
import os
import re
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)
WIKI = os.path.join(LLMWIKI, 'wiki')

# 叙事特征词（大小写敏感；不设 PASS 裸词，避免命中 IsPassed 等代码标识符）
NARRATIVE = [
    (r'静态\s*\d+\s*/\s*\d+', '验证叙事·静态N/N'),
    (r'阴性对照', '验证叙事·阴性对照'),
    (r'回滚点', '验证叙事·回滚点'),
    (r'探针', '验证叙事·探针'),
    (r'✅\s*20\d\d-', '日期叙事·✅后跟日期'),
    (r'^> 此前', '日志体·此前'),
]

violations = []


def read_lines(path):
    with open(path, 'rb') as f:
        return f.read().decode('utf-8', errors='replace').split('\n')


def check(rel, patterns, max_len=None, counts=None):
    path = os.path.join(WIKI, rel)
    if not os.path.isfile(path):
        violations.append('%s [文件缺失] 目标页不存在，路径可能漂移' % rel)
        return
    lines = read_lines(path)
    for i, ln in enumerate(lines, 1):
        for pat, label in patterns:
            if re.search(pat, ln):
                violations.append('%s:%d [%s] %s' % (rel, i, label, ln.strip()[:70]))
        if max_len and len(ln) > max_len:
            violations.append('%s:%d [行长 %d > %d] %s' % (rel, i, len(ln), max_len, ln.strip()[:70]))
    for pat, limit, label in (counts or []):
        n = sum(len(re.findall(pat, ln)) for ln in lines)
        if n > limit:
            violations.append('%s [计数 %s = %d > %d]' % (rel, label, n, limit))


# R1 index：只允许结构化索引
check(os.path.join('index', 'index.md'),
      NARRATIVE + [
          (r'^> \*\*同日', '日志体·同日'),
          (r'^## \[', '日志体·条目标题'),
          (r'^### 20\d\d-', '日志体·日期标题'),
          (r'^> 20\d\d-', '日志体·日期引用'),
      ],
      counts=[(r'最后更新', 1, '最后更新')])

# R2 ADR-Index：编号权威 + 总表（title 禁日期沿革；禁日期 bullet；行长 ≤600）
check(os.path.join('decisions', 'ADR-Index.md'),
      [(r'^title:.*20\d\d-', '标题行·日期沿革'),
       (r'^- 20\d\d-', '日志体·日期bullet')] + NARRATIVE,
      max_len=600)

# R3 CodeMap：文件↔功能↔wiki 对应表（禁叙事词；行长 ≤600）
check(os.path.join('architecture', 'CodeMap.md'), NARRATIVE, max_len=600)

# R4 其余架构页：只禁叙事词，不限行长（保留「依据的判断」长行）
_arch = os.path.join(WIKI, 'architecture')
for _name in sorted(os.listdir(_arch)):
    if _name.endswith('.md') and _name != 'CodeMap.md':
        check(os.path.join('architecture', _name), NARRATIVE)

# R5 lessons 页：只查「纯日志体」特征（教训页记录事故是正当内容，不查验证叙事）
#    ⚠️ 「阴性对照」是判据区分度的标准术语、「回滚点」是 backup 业务术语、
#       「此前」是教训页合法的沿革叙述 —— 三者均不查
_LESSON_LOG = [(r'^## \[20\d\d-\d\d-\d\d \d\d:\d\d:\d\d\]', '日志体·条目标题')]
_lessons = os.path.join(WIKI, 'lessons')
for _name in sorted(os.listdir(_lessons)):
    if _name.endswith('.md'):
        check(os.path.join('lessons', _name), _LESSON_LOG)

# R6 standards 页 + R7 rules 页：查「过程叙述」实质特征，豁免自指行
#    实质特征 = 探针实测 / 实测得到 / 跑出 N 项 / 静态 N/N PASS（带 PASS/通过）
#    自指行豁免 = 含「不得含」「禁含」「→ 属 log」「不属于」「不得使用」
_PROCESS = [(r'探针实测', '验证叙事·探针实测'),
            (r'实测得到|实测为|实测值', '验证叙事·实测数据'),
            (r'跑出\s*\d+\s*项', '验证叙事·实测批次'),
            (r'静态\s*\d+\s*/\s*\d+\s*(PASS|通过)', '验证叙事·静态N/N PASS')]
_SELFREF = ('不得含', '禁含', '→ 属 log', '不属于', '不得使用', '禁写', '不得维护', '⛔ 规则正文')


def _check_process(rel):
    """过程叙述检查，但豁免自指行"""
    path = os.path.join(WIKI, rel)
    if not os.path.isfile(path):
        violations.append('%s [文件缺失] 目标页不存在，路径可能漂移' % rel)
        return
    for i, ln in enumerate(read_lines(path), 1):
        if any(k in ln for k in _SELFREF):
            continue                      # 自指行：说的是「不要这样写」，本身不含叙述
        for pat, label in _PROCESS:
            if re.search(pat, ln):
                violations.append('%s:%d [%s] %s' % (rel, i, label, ln.strip()[:70]))


_std = os.path.join(WIKI, 'standards')
for _name in sorted(os.listdir(_std)):
    if _name.endswith('.md'):
        _check_process(os.path.join('standards', _name))

_rules = os.path.join(WIKI, 'rules')
for _name in sorted(os.listdir(_rules)):
    if _name.endswith('.md'):
        _check_process(os.path.join('rules', _name))

print('==== ingest_purity_scan：知识沉淀纯度检查 ====')
if violations:
    print('违规 %d 处：' % len(violations))
    for v in violations:
        print('  ' + v)
    sys.exit(1)
print('通过：七类页面无过程叙述 / 批次进度 / 日期沿革 / 日志体回灌')
sys.exit(0)
