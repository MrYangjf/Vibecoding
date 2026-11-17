#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""comment_scan.py —— 注释三分计数 / 撕裂四类 / 复述三档 可复算扫描器

用途
----
把「注释精简」轮里一直靠临时脚本自报的数字，固化成唯一可复跑口径：

  stats   三分计数：总行 / 空行 / 代码行 / 注释行（doc + 独立 // + 块注释）
  trunc   撕裂四类：T1 句子劈两半 / T2 XML 括号不闭合 / T3 与声明脱节 / T4 缩进为 0
  restate 复述三档：strict（高置信） / wide（宽） / ultra（超宽全集）
  xml     占位式 XML：<returns>返回值。</returns> / <param name="x">x 参数。</param>

用法
----
  python comment_scan.py stats   --root AdaWeldSystem
  python comment_scan.py trunc   --root AdaWeldSystem --json trunc.json
  python comment_scan.py restate --root AdaWeldSystem --tier ultra --json restate.json
  python comment_scan.py xml     --root AdaWeldSystem --json xml.json
  python comment_scan.py all     --root AdaWeldSystem --out-dir ./_scan

口径
----
* 统计范围：`*.cs` 全量；`*.Designer.cs` 单独打标并在 `--exclude-designer` 时剔除。
* 三分计数互斥：空行 / 代码行 / 注释行；块注释按行号归属注释行。
  行尾注释不单独计行，只记 `code_trailing` 供参考。
* 撕裂「处」= 一个连续 `///` 文档块命中一次；同一块命中多类时分别计入各类，
  但 `union` 只算一次（对账用 union）。
* 复述三档为包含关系：strict ⊂ wide ⊂ ultra。
  strict：注释文本去掉标点后，等于下一行代码中某个标识符的中文全等映射或
          仅为「赋值/循环/返回/初始化/调用/判断」这类无信息动词。
  wide  ：注释里出现下一行代码的标识符（长度 ≥4）且注释不含约束词。
  ultra ：注释里出现下一行代码的任一标识符子串（长度 ≥3）。
"""

import argparse
import json
import os
import re
import sys

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, 'reconfigure'):
        _s.reconfigure(encoding='utf-8', errors='replace')

# ---------------------------------------------------------------------------
# 基础读取
# ---------------------------------------------------------------------------

CS_EXTS = ('.cs',)


def is_designer(path):
    return path.endswith('.Designer.cs')


def read_text(path):
    with open(path, 'rb') as f:
        raw = f.read()
    bom = raw.startswith(b'\xef\xbb\xbf')
    text = raw.decode('utf-8-sig' if bom else 'utf-8', errors='replace')
    # 统一按 \n 切分，保留行尾信息
    crlf = text.count('\r\n')
    lf = text.count('\n') - crlf
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    # 文件以换行结尾时 split 会多出一个空元素，按行号口径去掉（否则总行数虚增）
    if lines and lines[-1] == '':
        lines.pop()
    return lines, bom, crlf, lf


def iter_cs(root, exclude_designer=False):
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in ('bin', 'obj', '.vs', 'packages')]
        for fn in sorted(filenames):
            if not fn.endswith(CS_EXTS):
                continue
            if exclude_designer and is_designer(fn):
                continue
            yield os.path.join(dirpath, fn)


# ---------------------------------------------------------------------------
# stats：三分计数
# ---------------------------------------------------------------------------

def classify_lines(lines):
    """返回每行类别：blank / code / doc / line / block"""
    kinds = []
    in_block = False
    for ln in lines:
        s = ln.strip()
        if in_block:
            kinds.append('block')
            if '*/' in s:
                in_block = False
            continue
        if s == '':
            kinds.append('blank')
            continue
        if s.startswith('///'):
            kinds.append('doc')
            continue
        if s.startswith('//'):
            kinds.append('line')
            continue
        if s.startswith('/*'):
            kinds.append('block')
            if '*/' not in s:
                in_block = True
            continue
        kinds.append('code')
    return kinds


def scan_stats(root, exclude_designer=False):
    agg = dict(total=0, blank=0, code=0, doc=0, line=0, block=0, code_trailing=0,
               files=0, designer_files=0, designer_lines=0, biz_lines=0)
    per_file = []
    for path in iter_cs(root, exclude_designer):
        lines, _bom, _crlf, _lf = read_text(path)
        kinds = classify_lines(lines)
        rec = dict(file=os.path.relpath(path, root), lines=len(lines))
        for ln, k in zip(lines, kinds):
            agg['total'] += 1
            agg[k] += 1
            if k == 'code' and '//' in ln.split('"')[0].split("'")[0]:
                agg['code_trailing'] += 1
        agg['files'] += 1
        if is_designer(path):
            agg['designer_files'] += 1
            agg['designer_lines'] += len(lines)
        else:
            agg['biz_lines'] += len(lines)
        rec['doc'] = kinds.count('doc')
        rec['line'] = kinds.count('line')
        rec['block'] = kinds.count('block')
        rec['code'] = kinds.count('code')
        rec['blank'] = kinds.count('blank')
        rec['designer'] = is_designer(path)
        per_file.append(rec)
    agg['comment'] = agg['doc'] + agg['line'] + agg['block']
    # 互斥校验
    assert agg['blank'] + agg['code'] + agg['comment'] == agg['total'], '三分计数不自洽'
    return dict(summary=agg, per_file=per_file)


# ---------------------------------------------------------------------------
# trunc：撕裂四类
# ---------------------------------------------------------------------------

XML_TAG = re.compile(r'<(/?)([A-Za-z][A-Za-z0-9_.-]*)([^>]*?)(/?)>')
CONSTRAINT_HINTS = (
    '单位', '值域', '范围', '可空', '默认', '约束', '协议', '硬件', '毫秒', '毫秒',
    '超时', '线程', '锁', '必须', '不得', '禁止', '注意', '否则', '原因', '因为',
    '实测', '索引', '序号', '字节', '帧', '采样', '精度', '容差', '上限', '下限',
)


def doc_blocks(lines):
    """产出 (start, end, indent_list)；end 为最后一行 //// 的下标（含）"""
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].lstrip().startswith('///'):
            j = i
            while j < n and lines[j].lstrip().startswith('///'):
                j += 1
            indents = [len(lines[k]) - len(lines[k].lstrip(' \t')) for k in range(i, j)]
            yield i, j - 1, indents
            i = j
        else:
            i += 1


def indent_of(line):
    return len(line) - len(line.lstrip(' \t'))


def scan_trunc(root, exclude_designer=False):
    out = []
    for path in iter_cs(root, exclude_designer):
        if is_designer(path):
            continue
        lines, _b, _c, _l = read_text(path)
        rel = os.path.relpath(path, root)
        n = len(lines)
        for start, end, indents in doc_blocks(lines):
            hits = []
            # 声明行：块后第一个非空、非注释行
            k = end + 1
            while k < n and lines[k].strip() == '':
                k += 1
            decl_line = lines[k] if k < n else ''
            decl_indent = indent_of(decl_line) if decl_line.strip() else None

            # T4 缩进为 0
            zero_lines = [start + idx for idx, ind in enumerate(indents) if ind == 0]
            if zero_lines and (decl_indent is None or decl_indent > 0):
                hits.append(('T4', start + 1, len(zero_lines),
                             '顶格 ///（%d 行），声明缩进 %s' % (len(zero_lines), decl_indent)))

            # T2 括号不闭合（按整块标签流配对，跨行标签不算错）
            stack = []
            bad = None
            bad_line = None
            for idx in range(start, end + 1):
                text = lines[idx].strip()[3:].strip()
                for m in XML_TAG.finditer(text):
                    closing, name, _attrs, selfclose = m.groups()
                    if selfclose:
                        continue
                    if closing:
                        if not stack or stack[-1] != name:
                            bad = name
                            bad_line = idx + 1
                            break
                        stack.pop()
                    else:
                        stack.append(name)
                if bad:
                    break
            if bad or stack:
                hits.append(('T2', bad_line or (start + 1), 1,
                             '括号不闭合：%s' % (bad or '/'.join(stack))))

            # T3 与声明脱节（中间空行）
            if k > end + 1 and decl_line.strip():
                hits.append(('T3', end + 1, k - end - 1,
                             '文档块与声明之间空 %d 行' % (k - end - 1)))

            # T1 句子被劈成两半
            seg = [lines[idx].strip()[3:].strip() for idx in range(start, end + 1)]
            joined = '\n'.join(seg)
            n_summary = len(re.findall(r'<summary>', joined))
            n_summary_close = len(re.findall(r'</summary>', joined))
            dup = re.findall(r'<summary>\s*(.*?)\s*</summary>', joined, re.S)
            split = False
            reason = ''
            if n_summary > 1:
                split = True
                reason = '同一块内 %d 个 <summary>' % n_summary
            elif n_summary != n_summary_close:
                split = True
                reason = 'summary 开闭数量不等 %d/%d' % (n_summary, n_summary_close)
            elif len(dup) >= 2 and dup[0].strip() == dup[1].strip():
                split = True
                reason = 'summary 文本重复'
            if split:
                hits.append(('T1', start + 1, end - start + 1, reason))

            if hits:
                out.append(dict(file=rel, start_line=start + 1, end_line=end + 1,
                                decl_line=k + 1 if k < n else None,
                                decl=decl_line.strip()[:120],
                                hits=[dict(cat=c, line=ln, count=cnt, detail=det)
                                      for c, ln, cnt, det in hits]))
    cats = {}
    union = 0
    for rec in out:
        union += 1
        for h in rec['hits']:
            cats[h['cat']] = cats.get(h['cat'], 0) + 1
    return dict(summary=dict(blocks=union, categories=cats,
                             T1=sum(1 for r in out if any(h['cat'] == 'T1' for h in r['hits'])),
                             T2=sum(1 for r in out if any(h['cat'] == 'T2' for h in r['hits'])),
                             T3=sum(1 for r in out if any(h['cat'] == 'T3' for h in r['hits'])),
                             T4=sum(1 for r in out if any(h['cat'] == 'T4' for h in r['hits']))),
                items=out)


# ---------------------------------------------------------------------------
# restate：复述三档
# ---------------------------------------------------------------------------

IDENT = re.compile(r'[A-Za-z_][A-Za-z0-9_]{2,}')
GENERIC = (
    '赋值', '循环', '返回', '初始化', '调用', '判断', '设置', '获取', '创建',
    '删除', '添加', '更新', '关闭', '打开', '启动', '停止', '保存', '加载',
    '清理', '重置', '执行', '处理', '检查', '遍历', '注册', '订阅', '写入',
    '读取', '发送', '接收', '开始', '结束',
)
CONSTRAINT = CONSTRAINT_HINTS + (
    '失败', '异常', '为空', '非空', '是否', '已经', '之前', '之后', '同时',
    '防止', '避免', '保证', '确保', '兼容', '并列', '优先', '仅', '只',
)

# 标识符切词 → 中文常见对应（只用于 strict 高置信判定）
EN2CN = {
    'remove': ('删除', '移除'), 'add': ('添加',), 'init': ('初始化',),
    'initialize': ('初始化',), 'load': ('加载',), 'save': ('保存',),
    'update': ('更新',), 'create': ('创建',), 'clear': ('清空', '清理', '清除'),
    'reset': ('重置',), 'start': ('开始', '启动'), 'stop': ('停止',),
    'close': ('关闭',), 'open': ('打开',), 'return': ('返回',),
    'count': ('数量', '计数'), 'index': ('索引',), 'name': ('名称',),
    'path': ('路径',), 'file': ('文件',), 'dir': ('目录',), 'value': ('值',),
    'result': ('结果',), 'list': ('列表',), 'item': ('项',), 'items': ('项',),
    'data': ('数据',), 'config': ('配置',), 'flag': ('标志',),
    'state': ('状态',), 'status': ('状态',), 'enable': ('启用',),
    'checked': ('选中', '勾选'), 'visible': ('可见',), 'text': ('文本',),
    'id': ('编号', 'ID'), 'time': ('时间',), 'read': ('读取',),
    'write': ('写入',), 'send': ('发送',), 'receive': ('接收',),
    'dispose': ('释放',), 'build': ('构建',), 'parse': ('解析',),
}


def strip_comment(ln):
    s = ln.strip()
    if s.startswith('//'):
        s = s[2:]
    return s.strip()


def next_code_line(lines, i):
    n = len(lines)
    j = i + 1
    while j < n:
        s = lines[j].strip()
        if s == '' or s.startswith('//'):
            j += 1
            continue
        return j, lines[j]
    return None, ''


def split_identifiers(code):
    out = []
    for m in IDENT.finditer(code):
        tok = m.group(0)
        # 跳过纯数值/常见关键字
        if tok in ('var', 'new', 'this', 'null', 'true', 'false', 'return',
                   'int', 'string', 'bool', 'double', 'void', 'public',
                   'private', 'static', 'readonly', 'const', 'using'):
            continue
        out.append(tok)
    return out


def word_hits(comment, identifiers, minlen):
    low = comment.lower()
    hits = []
    for tok in identifiers:
        if len(tok) < minlen:
            continue
        if tok.lower() in low:
            hits.append(tok)
    return hits


def has_constraint(comment):
    return any(h in comment for h in CONSTRAINT)


def matches_identifier_meaning(comment, identifiers):
    """strict：注释等于某标识符的中文对应，或仅为通用动词"""
    body = re.sub(r'[\s，。、：:；;,.!！?？]', '', comment)
    # 去掉方括号标签等
    body = re.sub(r'^\[[^\]]*\]', '', body)
    if not body:
        return False
    if body in GENERIC:
        return True
    for tok in identifiers:
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?![a-z])', tok)
        for w in words:
            cn = EN2CN.get(w.lower())
            if cn and body in cn:
                return True
    # 去掉注释里出现的标识符后剩余无信息
    rest = comment
    for tok in identifiers:
        rest = rest.replace(tok, '')
    rest = re.sub(r'[\s，。、：:；;,.!！?？()（）\[\]{}<>/\\_\-|+=*&%$#@~`\'"]', '', rest)
    if len(rest) <= 2 and identifiers:
        return True
    return False


def scan_restate(root, exclude_designer=False):
    strict, wide, ultra = [], [], []
    for path in iter_cs(root, exclude_designer):
        if is_designer(path):
            continue
        lines, _b, _c, _l = read_text(path)
        rel = os.path.relpath(path, root)
        for i, ln in enumerate(lines):
            s = ln.strip()
            if not s.startswith('//') or s.startswith('///'):
                continue
            j, code = next_code_line(lines, i)
            if j is None or not code.strip():
                continue
            body = strip_comment(ln)
            if not body:
                continue
            idents = split_identifiers(code)
            if not idents:
                continue
            rec = dict(file=rel, line=i + 1, comment=body, code=code.strip()[:160],
                       code_line=j + 1, identifiers=idents)
            if matches_identifier_meaning(body, idents):
                rec['tier'] = 'strict'
                strict.append(rec)
                continue
            hits = word_hits(body, idents, 4)
            if hits and not has_constraint(body):
                r = dict(rec)
                r['tier'] = 'wide'
                r['hits'] = hits
                wide.append(r)
                continue
            hits3 = word_hits(body, idents, 3)
            if hits3:
                r = dict(rec)
                r['tier'] = 'ultra'
                r['hits'] = hits3
                ultra.append(r)
    allc = strict + wide + ultra
    return dict(summary=dict(strict=len(strict), wide=len(wide), ultra=len(ultra),
                             all=len(allc)),
                strict=strict, wide=wide, ultra=ultra)


# ---------------------------------------------------------------------------
# xml：占位式 XML
# ---------------------------------------------------------------------------

PLACEHOLDER_RETURNS = re.compile(r'^\s*///\s*<returns>\s*(返回值|返回结果|返回)\s*[。.]?\s*</returns>\s*$')
PLACEHOLDER_PARAM = re.compile(
    r'^\s*///\s*<param name="([A-Za-z_][A-Za-z0-9_]*)">\s*\1\s*参数\s*[。.]?\s*</param>\s*$')


def scan_xml_placeholder(root, exclude_designer=False):
    returns, params = [], []
    for path in iter_cs(root, exclude_designer):
        if is_designer(path):
            continue
        lines, _b, _c, _l = read_text(path)
        rel = os.path.relpath(path, root)
        for i, ln in enumerate(lines):
            if PLACEHOLDER_RETURNS.match(ln):
                returns.append(dict(file=rel, line=i + 1, text=ln.strip(), kind='returns'))
            elif PLACEHOLDER_PARAM.match(ln):
                params.append(dict(file=rel, line=i + 1, text=ln.strip(), kind='param'))
    return dict(summary=dict(returns=len(returns), params=len(params),
                             total=len(returns) + len(params)),
                returns=returns, params=params)


# ---------------------------------------------------------------------------
# long：单条注释记录 ≤20 汉字（2026-11-10 业主裁定 · C16 / C18 / C19）
# ---------------------------------------------------------------------------

REC_LIMIT = 20
CJK_RE = re.compile(r'[\u4e00-\u9fff]')
SENT_RE = re.compile(r'[。；！？!?;]')
XML_TAG_STRIP = re.compile(r'<[^>]*>')
# 块级 XML 标签即记录边界，换成句末标点；同一标签内跨行续写因此在一条记录内合并
BLOCK_TAG_RE = re.compile(
    r'</?(?:summary|remarks|param|returns|value|exception|example|typeparam)\b[^>]*>')

# 非声明语句首词，避免把 return / throw 等误判成字段声明
DECL_SKIP_FIRST = frozenset((
    'return', 'throw', 'break', 'continue', 'goto', 'using', 'yield',
    'else', 'case', 'lock', 'if', 'while', 'for', 'foreach', 'switch', 'do',
))

DECL_RE = re.compile(
    r'^\s*(?:(?:public|private|protected|internal|static|readonly|const|volatile|'
    r'new|unsafe|extern|sealed|override|virtual|partial)\s+)*'
    r'(?P<type>[A-Za-z_][\w\.]*(?:\s*<[^;=]*?>)?(?:\s*\[\s*\])*\??)\s+'
    r'(?P<name>[A-Za-z_]\w*)\s*(?:=[^;]*)?;\s*(?P<trail>//(?!/).*)?$'
)


def cjk_len(text):
    """汉字数口径：只数 [\\u4e00-\\u9fff]，标点 / 标签 / 拉丁字母 / 数字均不计。"""
    return len(CJK_RE.findall(text))


def split_records(text):
    """按句末标点切成语义完整句子；每句一条记录。"""
    parts = [p.strip() for p in SENT_RE.split(text)]
    return [p for p in parts if p]


def merge_doc_block(block):
    """把一个连续 `///` 块合并成整段：续行不再单独成句（C18 跨行合并口径）。"""
    parts = []
    for ln in block:
        s = ln.strip()
        if s.startswith('///'):
            s = s[3:]
        s = s.strip()
        if s:
            parts.append(s)
    merged = ' '.join(parts)
    merged = BLOCK_TAG_RE.sub('。', merged)
    return XML_TAG_STRIP.sub('', merged)


def _is_decl(line):
    """判定是否为变量 / 字段声明行，返回匹配对象或 None。"""
    line = line.rstrip('\r')
    m = DECL_RE.match(line)
    if not m:
        return None
    first = line.strip().split()[0].rstrip('.;')
    if first in DECL_SKIP_FIRST:
        return None
    return m


def scan_var_multiline(lines, rel):
    """C19：一个变量 / 字段的 `//` 注释只许一行，多行即报。"""
    out = []
    n = len(lines)
    i = 0
    while i < n:
        s = lines[i].strip()
        if not s.startswith('//') or s.startswith('///'):
            i += 1
            continue
        j = i
        while j < n:
            t = lines[j].strip()
            if not t.startswith('//') or t.startswith('///'):
                break
            j += 1
        run = j - i
        above = _is_decl(lines[i - 1]) if i > 0 else None
        below = _is_decl(lines[j]) if j < n else None
        above_trail = 1 if (above and above.group('trail')) else 0
        below_trail = 1 if (below and below.group('trail')) else 0
        if above_trail and not below:
            total = run + above_trail
            decl_line = i
        elif below:
            total = run + below_trail
            decl_line = j + 1
        else:
            i = j
            continue
        if total > 1:
            out.append(dict(file=rel, line=decl_line, comment_line=i + 1,
                            lines=total, code=lines[decl_line - 1].strip()[:120]))
        i = j
    return out


def scan_long(root, exclude_designer=False, limit=REC_LIMIT):
    """统计超长注释：合并口径为主，旧逐行口径与变量多行 `//` 并行给出。"""
    items = []
    legacy = []
    var_items = []
    per_file = {}
    var_per_file = {}
    for path in iter_cs(root, exclude_designer):
        if is_designer(path):
            continue
        lines, _b, _c, _l = read_text(path)
        rel = os.path.relpath(path, root).replace('\\', '/')

        # 合并口径：一个 `///` 块整段切句（C18）
        for start, end, _ind in doc_blocks(lines):
            block = lines[start:end + 1]
            for rec in split_records(merge_doc_block(block)):
                n = cjk_len(rec)
                if n > limit:
                    items.append(dict(file=rel, line=start + 1, kind='doc',
                                      chars=n, text=rec))
                    per_file[rel] = per_file.get(rel, 0) + 1
            # 旧逐行口径，仅供对账（口径已作废）
            for k, ln in enumerate(block):
                body = XML_TAG_STRIP.sub('', ln.strip()[3:]).strip()
                for rec in split_records(body):
                    n = cjk_len(rec)
                    if n > limit:
                        legacy.append(dict(file=rel, line=start + k + 1,
                                           kind='doc', chars=n, text=rec))

        # 独立 `//` 行仍按行计数；变量多行另计（C19）
        for i, ln in enumerate(lines):
            s = ln.strip()
            if not s.startswith('//') or s.startswith('///'):
                continue
            for rec in split_records(s[2:].strip()):
                n = cjk_len(rec)
                if n > limit:
                    items.append(dict(file=rel, line=i + 1, kind='line',
                                      chars=n, text=rec))
                    per_file[rel] = per_file.get(rel, 0) + 1

        for rec in scan_var_multiline(lines, rel):
            var_items.append(rec)
            var_per_file[rel] = var_per_file.get(rel, 0) + 1

    items.sort(key=lambda x: (-x['chars'], x['file'], x['line']))
    var_items.sort(key=lambda x: (x['file'], x['line']))
    return dict(summary=dict(limit=limit, total=len(items),
                             files=len(per_file),
                             var_multiline=len(var_items),
                             var_files=len(var_per_file),
                             legacy_line=len(legacy),
                             over_by=dict((str(k), sum(1 for it in items if it['chars'] == k))
                                          for k in sorted(set(it['chars'] for it in items),
                                                          reverse=True))),
                per_file=per_file, var_per_file=var_per_file,
                items=items, legacy=legacy, var_items=var_items)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['stats', 'trunc', 'restate', 'xml', 'long', 'all'])
    ap.add_argument('--root', required=True)
    ap.add_argument('--json')
    ap.add_argument('--out-dir')
    ap.add_argument('--tier', default='ultra')
    ap.add_argument('--exclude-designer', action='store_true')
    a = ap.parse_args()

    if a.cmd == 'stats':
        res = scan_stats(a.root, a.exclude_designer)
        s = res['summary']
        print('files=%(files)d designer=%(designer_files)d total=%(total)d '
              'blank=%(blank)d code=%(code)d comment=%(comment)d '
              'doc=%(doc)d line=%(line)d block=%(block)d trailing=%(code_trailing)d' % s)
    elif a.cmd == 'trunc':
        res = scan_trunc(a.root, a.exclude_designer)
        s = res['summary']
        print('blocks=%(blocks)d T1=%(T1)d T2=%(T2)d T3=%(T3)d T4=%(T4)d' % s)
    elif a.cmd == 'restate':
        res = scan_restate(a.root, a.exclude_designer)
        print(res['summary'])
        if a.tier in ('strict', 'wide'):
            res = dict(summary=res['summary'], items=res[a.tier])
    elif a.cmd == 'xml':
        res = scan_xml_placeholder(a.root, a.exclude_designer)
        print(res['summary'])
    elif a.cmd == 'long':
        res = scan_long(a.root, a.exclude_designer)
        s = res['summary']
        print('limit=%d merged_over=%d files=%d var_multiline=%d var_files=%d legacy_line=%d'
              % (s['limit'], s['total'], s['files'], s['var_multiline'],
                 s['var_files'], s['legacy_line']))
        for f, c in sorted(res['per_file'].items(), key=lambda kv: -kv[1])[:30]:
            print('  %4d  %s' % (c, f))
        for f, c in sorted(res['var_per_file'].items(), key=lambda kv: -kv[1])[:30]:
            print('  var %3d  %s' % (c, f))
    else:
        res = dict(stats=scan_stats(a.root, a.exclude_designer),
                   trunc=scan_trunc(a.root, a.exclude_designer),
                   restate=scan_restate(a.root, a.exclude_designer),
                   xml=scan_xml_placeholder(a.root, a.exclude_designer),
                   long=scan_long(a.root, a.exclude_designer))
        print(json.dumps({k: v['summary'] for k, v in res.items()}, ensure_ascii=False))

    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
        name = {'stats': 'stats', 'trunc': 'trunc', 'restate': 'restate',
                'xml': 'xml', 'long': 'long', 'all': 'all'}[a.cmd]
        with open(os.path.join(a.out_dir, name + '.json'), 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
