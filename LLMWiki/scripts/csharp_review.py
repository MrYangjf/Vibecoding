#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
csharp_review.py — .NET Framework 4.8 / C# 7.3 单文件冗余代码扫描器

扫描单个 .cs 文件（不处理 designer.cs、不跟踪外部引用），输出以下类别的问题候选：
  A. 文件书写整理：成员顺序、#region 划分、XML 注释规范
  B. 代码逻辑精简：无意义 null 检查、无意义锁、冗余赋值传递、
     过度枚举、过度属性、过度等待、过度缓存、过度资源管理
  C. 函数精简：功能重叠函数、单层嵌套内联候选、疑似死函数

脚本只做机械扫描和启发式标记，最终判定由审查者结合业务语义完成。

用法:
    python3 csharp_review.py <file.cs>
    python3 csharp_review.py <file.cs> --json
    python3 csharp_review.py <file.cs> --verbose   # 输出所有扫描项（含无问题项）
"""

import argparse
import json
import re
import sys
from collections import defaultdict


# ---------------------------------------------------------------------------
# 预处理：去除字符串/字符字面量内容，避免大括号和关键字干扰
# ---------------------------------------------------------------------------

def strip_strings_and_chars(source):
    """将字符串和字符字面量替换为空占位，保留原始长度和换行。
    返回处理后的文本。正则覆盖：
      - 常规字符串 "..."
      - 逐字字符串 @""...""
      - 插值字符串 $"...{...}..."  （C# 7.3 支持，但 { } 内是代码，这里简化处理）
      - 字符 '...'
    注释不在此处处理，由调用方决定。
    """
    result = []
    i = 0
    n = len(source)
    while i < n:
        ch = source[i]
        # 逐字字符串 @"...""
        if ch == '@' and i + 1 < n and source[i + 1] == '"':
            j = i + 2
            while j < n:
                if source[j] == '"' and j + 1 < n and source[j + 1] == '"':
                    j += 2
                    continue
                if source[j] == '"':
                    j += 1
                    break
                j += 1
            result.append(' ' * (j - i))
            i = j
            continue
        # 插值字符串 $"...{...}"  —— 简化：把 { } 内的代码保留，外层字符串替换
        if ch == '$' and i + 1 < n and source[i + 1] == '"':
            result.append('$"')
            j = i + 2
            while j < n:
                if source[j] == '{' and j + 1 < n and source[j + 1] == '{':
                    result.append('{{')
                    j += 2
                    continue
                if source[j] == '"':
                    result.append('"')
                    j += 1
                    break
                result.append(source[j])
                j += 1
            i = j
            continue
        # 常规字符串
        if ch == '"':
            j = i + 1
            while j < n:
                if source[j] == '\\' and j + 1 < n:
                    j += 2
                    continue
                if source[j] == '"':
                    j += 1
                    break
                j += 1
            result.append(' ' * (j - i))
            i = j
            continue
        # 字符字面量
        if ch == "'":
            j = i + 1
            while j < n:
                if source[j] == '\\' and j + 1 < n:
                    j += 2
                    continue
                if source[j] == "'":
                    j += 1
                    break
                j += 1
            result.append(' ' * (j - i))
            i = j
            continue
        result.append(ch)
        i += 1
    return ''.join(result)


def remove_comments(source):
    """移除 // 行注释和 /* */ 块注释，保留换行和长度。
    注意：/// XML doc 注释需要保留用于注释检查，所以本函数提供
    一个保留 /// 的版本。"""
    return _remove_comments_impl(source, keep_doc_comments=True)


def remove_all_comments(source):
    """移除所有注释包括 ///。"""
    return _remove_comments_impl(source, keep_doc_comments=False)


def remove_preprocessor_directives(source):
    """将 C# 预处理指令（#region/#endregion/#if/#endif 等行）替换为空格，
    保留换行以维持行号。"""
    result = []
    for line in source.split('\n'):
        stripped = line.lstrip()
        if stripped.startswith('#'):
            result.append(' ' * len(line))
        else:
            result.append(line)
    return '\n'.join(result)


def _remove_comments_impl(source, keep_doc_comments):
    result = []
    i = 0
    n = len(source)
    while i < n:
        # 行注释
        if source[i:i + 2] == '//':
            if keep_doc_comments and source[i:i + 3] == '///':
                # 保留整行
                nl = source.find('\n', i)
                if nl == -1:
                    result.append(source[i:])
                    i = n
                else:
                    result.append(source[i:nl])
                    i = nl
                continue
            nl = source.find('\n', i)
            if nl == -1:
                result.append(' ' * (n - i))
                i = n
            else:
                result.append(' ' * (nl - i))
                i = nl
            continue
        # 块注释
        if source[i:i + 2] == '/*':
            end = source.find('*/', i + 2)
            if end == -1:
                end = n
            else:
                end += 2
            # 保留换行
            for k in range(i, end):
                result.append('\n' if source[k] == '\n' else ' ')
            i = end
            continue
        result.append(source[i])
        i += 1
    return ''.join(result)


# ---------------------------------------------------------------------------
# 大括号匹配
# ---------------------------------------------------------------------------

def find_matching_brace(text, open_pos):
    """从 open_pos（指向 '{'）找到匹配的 '}' 位置。text 应已去除字符串。"""
    depth = 0
    i = open_pos
    n = len(text)
    while i < n:
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

class Issue:
    """一条审查发现。"""
    SEVERITY_ERROR = "error"
    SEVERITY_WARN = "warn"
    SEVERITY_INFO = "info"

    def __init__(self, category, severity, line, message, snippet=""):
        self.category = category
        self.severity = severity
        self.line = line
        self.message = message
        self.snippet = snippet.strip()

    def to_dict(self):
        return {
            "category": self.category,
            "severity": self.severity,
            "line": self.line,
            "message": self.message,
            "snippet": self.snippet,
        }


class Method:
    def __init__(self, name, access, is_static, return_type, params,
                 start_line, end_line, body_start, body_end, body_text,
                 is_public_api, is_virtual_override, is_async):
        self.name = name
        self.access = access
        self.is_static = is_static
        self.return_type = return_type
        self.params = params
        self.start_line = start_line
        self.end_line = end_line
        self.body_start = body_start
        self.body_end = body_end
        self.body_text = body_text
        self.is_public_api = is_public_api
        self.is_virtual_override = is_virtual_override
        self.is_async = is_async
        self.callers = []          # 本文件内调用此方法的方法名列表
        self.callees = []          # 此方法调用的本文件内方法名列表
        self.has_doc_comment = False
        self.doc_summary = ""
        self.doc_params = []       # [(name, text)]
        self.has_returns = False
        self.effective_body_lines = 0  # 非空非注释行


class Field:
    def __init__(self, name, access, is_static, is_readonly, ftype,
                 start_line, is_event, is_const):
        self.name = name
        self.access = access
        self.is_static = is_static
        self.is_readonly = is_readonly
        self.ftype = ftype
        self.start_line = start_line
        self.is_event = is_event
        self.is_const = is_const


class Property:
    def __init__(self, name, access, ftype, start_line, has_get, has_set,
                 set_access, is_static, is_virtual, body_text=""):
        self.name = name
        self.access = access
        self.ftype = ftype
        self.start_line = start_line
        self.has_get = has_get
        self.has_set = has_set
        self.set_access = set_access  # 'public' / 'private' / 'protected' / None
        self.is_static = is_static
        self.is_virtual = is_virtual
        self.body_text = body_text
        self.has_doc_comment = False


# ---------------------------------------------------------------------------
# 解析器
# ---------------------------------------------------------------------------

ACCESS_RE = re.compile(r'\b(public|private|protected|internal)\b')
STATIC_RE = re.compile(r'\bstatic\b')
READONLY_RE = re.compile(r'\breadonly\b')
CONST_RE = re.compile(r'\bconst\b')
VIRTUAL_OVERRIDE_RE = re.compile(r'\b(virtual|override|abstract|sealed|new)\b')
ASYNC_RE = re.compile(r'\basync\b')
EVENT_RE = re.compile(r'\bevent\b')

# 方法签名：[修饰符] 返回类型 方法名 ( 参数 ) [where ...]
# 排除构造函数（无返回类型）和属性（无括号）
METHOD_SIG_RE = re.compile(
    r'(?P<modifiers>(?:(?:public|private|protected|internal|static|readonly|'
    r'virtual|override|abstract|sealed|new|async|extern|unsafe|partial)\s+)*)'
    r'(?P<ret>(?:[A-Za-z_][\w<>\?\[\],\.\s]*?\s+))'
    r'(?P<name>[A-Za-z_]\w*)\s*'
    r'\((?P<params>[^)]*)\)\s*'
    r'(?:where\s+[^{]+?)?'
    r'\{'
)

# 构造函数
CTOR_RE = re.compile(
    r'(?P<modifiers>(?:(?:public|private|protected|internal|static)\s+)*)'
    r'(?P<name>[A-Za-z_]\w*)\s*'
    r'\((?P<params>[^)]*)\)\s*'
    r'(?::\s*[^{]+?)?'
    r'\{'
)

# 属性：[修饰符] 类型 名称 { get; set; }  或带访问器
PROPERTY_RE = re.compile(
    r'(?P<modifiers>(?:(?:public|private|protected|internal|static|virtual|'
    r'override|abstract|sealed|new|extern|unsafe)\s+)*)'
    r'(?P<type>[A-Za-z_][\w<>\?\[\],\.\s]*?)\s+'
    r'(?P<name>[A-Za-z_]\w*)\s*'
    r'\{\s*(?P<body>[^}]*)\}'
)

# 字段：[修饰符] 类型 名称 [= ...];
FIELD_RE = re.compile(
    r'(?P<modifiers>(?:(?:public|private|protected|internal|static|readonly|'
    r'const|new|unsafe|volatile)\s+)*)'
    r'(?P<type>[A-Za-z_][\w<>\?\[\],\.\s]*?)\s+'
    r'(?P<name>[A-Za-z_]\w*)\s*'
    r'(?:=[^;]*)?;'
)

ENUM_RE = re.compile(r'\benum\s+([A-Za-z_]\w*)')
CLASS_RE = re.compile(r'\b(class|struct|interface)\s+([A-Za-z_]\w*)')

# 控制流关键字，用于判断方法体复杂度
CONTROL_FLOW_RE = re.compile(
    r'\b(if|else|for|foreach|while|do|switch|case|try|catch|finally|using|lock)\b'
)

# 排除的方法名（不是真正的方法调用目标）
KEYWORDS_NOT_METHODS = {
    'if', 'for', 'foreach', 'while', 'switch', 'catch', 'using', 'lock',
    'return', 'throw', 'new', 'nameof', 'typeof', 'sizeof', 'checked',
    'unchecked', 'lock', 'yield', 'await', 'var', 'is', 'as', 'in', 'out',
    'ref', 'this', 'base', 'null', 'true', 'false', 'default',
}


def line_of(text, pos):
    return text.count('\n', 0, pos) + 1


def parse_file(source):
    """解析 C# 源文件，返回 classes 列表。每个 class 是 dict。"""
    # 去除字符串干扰（保留注释用于 doc 检查）
    clean = strip_strings_and_chars(source)
    # 去除所有注释和预处理指令用于结构解析（保留长度和换行，位置一致）
    code = remove_preprocessor_directives(remove_all_comments(clean))

    classes = []
    pos = 0
    while True:
        m = CLASS_RE.search(code, pos)
        if not m:
            break
        class_keyword = m.group(1)
        class_name = m.group(2)
        # 找类体的 {
        brace_pos = code.find('{', m.end())
        if brace_pos == -1:
            break
        end_pos = find_matching_brace(code, brace_pos)
        if end_pos == -1:
            break

        class_info = {
            'name': class_name,
            'kind': class_keyword,
            'start_line': line_of(source, m.start()),
            'end_line': line_of(source, end_pos),
            'header_start': m.start(),
            'body_start': brace_pos,
            'body_end': end_pos,
            'methods': [],
            'fields': [],
            'properties': [],
            'enums': [],
        }

        body_text = code[brace_pos + 1:end_pos]
        body_offset = brace_pos + 1

        # 收集枚举
        for em in ENUM_RE.finditer(body_text):
            class_info['enums'].append({
                'name': em.group(1),
                'line': line_of(source, body_offset + em.start()),
            })

        # 收集方法（在类体范围内扫描，用 code 做结构匹配）
        class_info['methods'] = _parse_methods(
            code, source, body_offset, end_pos, class_name
        )

        # 收集字段和属性
        class_info['fields'], class_info['properties'] = _parse_fields_and_props(
            code, source, body_offset, end_pos,
            {mth.name for mth in class_info['methods']},
            class_name=class_name,
        )

        # 剔除落在方法体/属性体内部的伪字段（见 _drop_pseudo_fields 说明）
        class_info['fields'] = _drop_pseudo_fields(class_info)

        classes.append(class_info)
        pos = end_pos + 1

    return classes


def _drop_pseudo_fields(class_info):
    """剔除落在方法体或属性体内部的伪字段。

    FIELD_RE 会把两类非字段文本误匹配成字段声明：
      1. 方法形参表，如 private void Log(string message, MessageLevel level)
         → 伪字段「private string message, MessageLevel level」
      2. 属性体中的对象初始化器，如 new T { Phase = _result.Phase, ... }
         → 伪字段「private _result.Phase, Pass」
    C# 不允许在方法体/属性体内声明字段，故凡落在任一方法或属性行区间内的
    匹配结果一律剔除，避免成员顺序检查产生假告警。
    """
    spans = [(m.start_line, m.end_line) for m in class_info['methods']]
    for prop in class_info['properties']:
        body_lines = prop.body_text.count('\n') if prop.body_text else 0
        spans.append((prop.start_line, prop.start_line + body_lines + 2))

    kept = []
    for f in class_info['fields']:
        if any(start <= f.start_line <= end for start, end in spans):
            continue
        kept.append(f)
    return kept


def _parse_methods(clean, source, body_start, body_end, class_name):
    methods = []
    pos = body_start
    # 扫描所有方法签名
    while pos < body_end:
        # 尝试匹配方法签名
        m = METHOD_SIG_RE.search(clean, pos, body_end)
        if not m:
            break
        name = m.group('name')
        # 排除不是方法的情况：属性 get/set、构造函数（ret 会包含类名）
        ret_raw = m.group('ret').strip()
        modifiers_raw = m.group('modifiers')
        params_raw = m.group('params')

        # 跳过 if/for/while/switch/catch/using/lock 等控制结构
        # 这些结构的"返回类型"会是关键字
        if ret_raw in ('if', 'for', 'foreach', 'while', 'switch', 'catch',
                       'using', 'lock', 'return', 'throw'):
            pos = m.end()
            continue

        # 构造函数会被误匹配：modifiers 匹配空，ret 匹配到 "public" 等修饰符
        if ret_raw in ('public', 'private', 'protected', 'internal',
                       'static', 'virtual', 'override', 'abstract',
                       'new', 'sealed', 'async', 'unsafe', 'extern',
                       'partial', 'readonly'):
            pos = m.end()
            continue

        # 排除属性访问器（在属性内部）
        if name in ('get', 'set'):
            pos = m.end()
            continue

        # 构造函数检测：返回类型恰好是类名
        is_ctor = (ret_raw == class_name or ret_raw.endswith(' ' + class_name))
        if is_ctor:
            # 构造函数用 CTOR_RE 更准确，这里跳过让下面的逻辑处理
            pass

        open_brace = m.end() - 1  # 指向 {
        close_brace = find_matching_brace(clean, open_brace)
        if close_brace == -1 or close_brace >= body_end:
            pos = m.end()
            continue

        # 解析修饰符
        mods = modifiers_raw.split()
        access = 'private'
        for acc in ('public', 'private', 'protected', 'internal'):
            if acc in mods:
                access = acc
                break
        is_static = 'static' in mods
        is_virtual_override = any(
            x in mods for x in ('virtual', 'override', 'abstract', 'new')
        )
        is_async = 'async' in mods

        # 提取方法体文本（用原始 source 保留注释和字符串）
        body_text_raw = source[open_brace + 1:close_brace]

        meth = Method(
            name=name,
            access=access,
            is_static=is_static,
            return_type=ret_raw,
            params=params_raw.strip(),
            start_line=line_of(source, m.start()),
            end_line=line_of(source, close_brace),
            body_start=open_brace + 1,
            body_end=close_brace,
            body_text=body_text_raw,
            is_public_api=(access in ('public', 'protected')),
            is_virtual_override=is_virtual_override,
            is_async=is_async,
        )
        # 有效行数
        body_clean = remove_all_comments(strip_strings_and_chars(body_text_raw))
        meth.effective_body_lines = sum(
            1 for line in body_clean.splitlines() if line.strip()
        )
        methods.append(meth)
        pos = close_brace + 1

    # 构造函数
    pos = body_start
    while pos < body_end:
        m = CTOR_RE.search(clean, pos, body_end)
        if not m:
            break
        name = m.group('name')
        if name != class_name:
            pos = m.end()
            continue
        mods = m.group('modifiers').split()
        access = 'public'
        for acc in ('public', 'private', 'protected', 'internal'):
            if acc in mods:
                access = acc
                break
        open_brace = m.end() - 1
        close_brace = find_matching_brace(clean, open_brace)
        if close_brace == -1 or close_brace >= body_end:
            pos = m.end()
            continue
        body_text_raw = source[open_brace + 1:close_brace]
        body_clean = remove_all_comments(strip_strings_and_chars(body_text_raw))
        meth = Method(
            name='#ctor',
            access=access,
            is_static='static' in mods,
            return_type=class_name,
            params=m.group('params').strip(),
            start_line=line_of(source, m.start()),
            end_line=line_of(source, close_brace),
            body_start=open_brace + 1,
            body_end=close_brace,
            body_text=body_text_raw,
            is_public_api=(access in ('public', 'protected')),
            is_virtual_override=False,
            is_async=False,
        )
        meth.effective_body_lines = sum(
            1 for line in body_clean.splitlines() if line.strip()
        )
        methods.append(meth)
        pos = close_brace + 1

    methods.sort(key=lambda x: x.start_line)
    return methods


def _parse_fields_and_props(clean, source, body_start, body_end, method_names,
                            class_name=None):
    fields = []
    properties = []
    # 按行扫描，识别字段和属性
    # 先移除方法体内容，避免方法内的局部变量干扰
    # 用一个掩码标记方法体区域
    mask = [True] * (body_end - body_start)  # True = 在成员区域（非方法体）
    # 重新找方法和属性体来屏蔽
    scan_text = clean[body_start:body_end]

    # 屏蔽所有方法体
    for m in METHOD_SIG_RE.finditer(scan_text):
        if m.group('name') in ('get', 'set'):
            continue
        ob = m.end() - 1  # 相对于 scan_text 的位置
        cb_rel = find_matching_brace(scan_text, ob)
        if cb_rel != -1:
            for k in range(ob, cb_rel + 1):
                if 0 <= k < len(mask):
                    mask[k] = False

    # 屏蔽构造函数体（仅当类名已知时）
    if class_name:
        for m in CTOR_RE.finditer(scan_text):
            if m.group('name') != class_name:
                continue
            ob = m.end() - 1  # 相对于 scan_text 的位置
            cb_rel = find_matching_brace(scan_text, ob)
            if cb_rel != -1:
                for k in range(ob, cb_rel + 1):
                    if 0 <= k < len(mask):
                        mask[k] = False

    # 屏蔽嵌套类体和枚举体
    for m in CLASS_RE.finditer(scan_text):
        bp = scan_text.find('{', m.end())
        if bp != -1:
            ep = find_matching_brace(scan_text, bp)
            if ep != -1:
                for k in range(bp, ep + 1):
                    if 0 <= k < len(mask):
                        mask[k] = False
    for m in ENUM_RE.finditer(scan_text):
        bp = scan_text.find('{', m.end())
        if bp != -1:
            ep = find_matching_brace(scan_text, bp)
            if ep != -1:
                for k in range(bp, ep + 1):
                    if 0 <= k < len(mask):
                        mask[k] = False

    # 构建屏蔽后的文本
    masked = []
    for idx, ch in enumerate(scan_text):
        masked.append(ch if mask[idx] else ' ')
    member_text = ''.join(masked)

    # 字段收集专用文本：在 member_text 基础上追加屏蔽 get/set 访问器体，
    # 否则访问器体内的局部变量（如 setter 里的 DeviceState old = _state;）
    # 会被 FIELD_RE 误判为字段，导致成员顺序假警告
    # （2026-09-01 实测 DeviceStateBase / SimulationWorkflow）。
    # 注意：访问器无参数列表，METHOD_SIG_RE 匹配不到，须用独立正则。
    mask2 = mask[:]
    for m in re.finditer(r'\b(get|set)\s*\{', scan_text):
        ob = m.end() - 1
        cb_rel = find_matching_brace(scan_text, ob)
        if cb_rel != -1:
            for k in range(ob, cb_rel + 1):
                if 0 <= k < len(mask2):
                    mask2[k] = False
    fields_text = ''.join(
        scan_text[k] if mask2[k] else ' ' for k in range(len(scan_text)))

    # 找属性
    for m in PROPERTY_RE.finditer(member_text):
        name = m.group('name')
        if name in method_names or name in ('get', 'set'):
            continue
        ftype = m.group('type').strip()
        mods = m.group('modifiers').split()
        access = 'private'
        for acc in ('public', 'private', 'protected', 'internal'):
            if acc in mods:
                access = acc
                break
        body = m.group('body')
        has_get = 'get' in body
        has_set = 'set' in body
        set_access = None
        if has_set:
            sm = re.search(r'(private|protected|internal)\s+set', body)
            if sm:
                set_access = sm.group(1)
            else:
                set_access = access
        is_static = 'static' in mods
        is_virtual = any(x in mods for x in ('virtual', 'override', 'abstract'))
        # 检查属性体是否有逻辑（不只是 get; set;）
        body_stripped = body.replace('get;', '').replace('set;', '')
        body_stripped = re.sub(r'(private|protected|internal)\s+set;?', '',
                               body_stripped)
        body_stripped = body_stripped.strip()
        prop = Property(
            name=name, access=access, ftype=ftype,
            start_line=line_of(source, body_start + m.start()),
            has_get=has_get, has_set=has_set, set_access=set_access,
            is_static=is_static, is_virtual=is_virtual,
            body_text=body_stripped,
        )
        properties.append(prop)

    # 找字段（排除属性、方法签名、事件；用 fields_text 避开访问器体局部变量）
    # 事件字段
    for m in re.finditer(
            r'(?P<modifiers>(?:(?:public|private|protected|internal|static|'
            r'readonly|const|new|unsafe|volatile|virtual|override|abstract)\s+)*)'
            r'event\s+(?P<type>[A-Za-z_][\w<>\?\[\],\.\s]*?)\s+'
            r'(?P<name>[A-Za-z_]\w*)\s*;',
            fields_text):
        name = m.group('name')
        mods = m.group('modifiers').split()
        access = 'private'
        for acc in ('public', 'private', 'protected', 'internal'):
            if acc in mods:
                access = acc
                break
        fields.append(Field(
            name=name, access=access, is_static='static' in mods,
            is_readonly='readonly' in mods, ftype=m.group('type').strip(),
            start_line=line_of(source, body_start + m.start()),
            is_event=True, is_const='const' in mods,
        ))

    # 普通字段
    for m in FIELD_RE.finditer(fields_text):
        name = m.group('name')
        ftype = m.group('type').strip()
        # 排除方法返回类型行、类名、属性类型等
        if name in method_names or name in ('get', 'set'):
            continue
        # 排除表达式体成员（属性/方法 => ...;）：FIELD_RE 的 match 终点在 ; 之后，
        # 须回看整个匹配文本（2026-09-01 实测 Instance => _lazy.Value; 被误判为字段）
        if '=>' in m.group(0):
            continue
        if ftype in ('class', 'struct', 'interface', 'enum', 'void', 'return',
                     'if', 'for', 'while', 'switch', 'catch', 'using',
                     'lock', 'throw', 'new'):
            continue
        # 排除已经识别为属性的
        if any(p.name == name for p in properties):
            continue
        mods = m.group('modifiers').split()
        access = 'private'
        for acc in ('public', 'private', 'protected', 'internal'):
            if acc in mods:
                access = acc
                break
        # 排除方法签名（返回类型+方法名被误匹配为字段）
        # 字段以 ; 结尾，方法以 ( 结尾；FIELD_RE 要求 ;，但方法签名前的修饰符行可能被误匹配
        # 检查该位置后面是否紧跟 (
        after = fields_text[m.end():m.end() + 5].strip()
        if after.startswith('('):
            continue
        fields.append(Field(
            name=name, access=access, is_static='static' in mods,
            is_readonly='readonly' in mods, ftype=ftype,
            start_line=line_of(source, body_start + m.start()),
            is_event=False, is_const='const' in mods,
        ))

    # 去重（按名称+行号）
    seen = set()
    unique_fields = []
    for f in fields:
        key = (f.name, f.start_line)
        if key not in seen:
            seen.add(key)
            unique_fields.append(f)
    seen_p = set()
    unique_props = []
    for p in properties:
        key = (p.name, p.start_line)
        if key not in seen_p:
            seen_p.add(key)
            unique_props.append(p)

    return unique_fields, unique_props


# ---------------------------------------------------------------------------
# XML 文档注释解析
# ---------------------------------------------------------------------------

DOC_SUMMARY_RE = re.compile(r'<summary>(.*?)</summary>', re.DOTALL)
DOC_PARAM_RE = re.compile(r'<param\s+name="([^"]+)"\s*>(.*?)</param>',
                          re.DOTALL)
DOC_RETURNS_RE = re.compile(r'<returns>(.*?)</returns>', re.DOTALL)


def parse_doc_comment(source, sig_start):
    """从方法签名位置向前查找 /// 注释块。"""
    # 向前找连续的 /// 行
    line_start = source.rfind('\n', 0, sig_start) + 1
    lines = []
    pos = line_start - 1
    while pos > 0:
        prev_nl = source.rfind('\n', 0, pos)
        line = source[prev_nl + 1:pos]
        stripped = line.strip()
        if stripped.startswith('///'):
            lines.append(stripped[3:].strip())
            pos = prev_nl
        else:
            break
    if not lines:
        return None
    lines.reverse()
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# 检查逻辑
# ---------------------------------------------------------------------------

def check_regions_and_order(source, classes, issues):
    """检查 #region 划分和成员顺序。"""
    # 收集所有 #region
    regions = []
    for m in re.finditer(r'#region\s*(.*)', source):
        line = line_of(source, m.start())
        name = m.group(1).strip()
        regions.append((line, name, m.start()))
    endregions = [line_of(source, m.start())
                  for m in re.finditer(r'#endregion', source)]

    if not regions:
        issues.append(Issue(
            "A.文件整理", Issue.SEVERITY_WARN, 1,
            "文件中未使用 #region 划分私有变量/公共变量/私有函数/公共函数",
        ))
        return

    # 检查 region 配对
    if len(regions) != len(endregions):
        issues.append(Issue(
            "A.文件整理", Issue.SEVERITY_ERROR, regions[0][0],
            f"#region({len(regions)}) 与 #endregion({len(endregions)}) 数量不匹配",
        ))

    # 检查 region 名称
    expected_regions = {'私有变量', '公共变量', '构造函数', '私有函数',
                        '公共函数'}
    found_region_names = {name for _, name, _ in regions}
    for expected in expected_regions:
        matched = any(expected in name for name in found_region_names)
        if not matched:
            issues.append(Issue(
                "A.文件整理", Issue.SEVERITY_INFO, 1,
                f"未找到 \"{expected}\" 区域的 #region（如该区域为空可忽略）",
            ))

    # 检查每个类的成员顺序
    for cls in classes:
        members = []
        for f in cls['fields']:
            order = 1 if f.access == 'private' else 2
            members.append((order, f.start_line, f"字段 {f.access} {f.ftype} {f.name}"))
        for p in cls['properties']:
            order = 2 if p.access in ('public', 'protected') else 1
            members.append((order, p.start_line, f"属性 {p.access} {p.ftype} {p.name}"))
        for mth in cls['methods']:
            if mth.name == '#ctor':
                order = 3
            elif mth.access == 'private':
                order = 4
            else:
                order = 5
            members.append((order, mth.start_line, f"方法 {mth.access} {mth.name}"))

        members.sort(key=lambda x: x[1])
        prev_order = 0
        for order, ln, desc in members:
            if order < prev_order:
                issues.append(Issue(
                    "A.文件整理", Issue.SEVERITY_WARN, ln,
                    f"成员顺序错误：{desc} 出现在更高顺序区域之后。"
                    f"应按 私有变量→公共变量→构造函数→私有函数→公共函数 排列",
                ))
                break
            prev_order = order


def check_doc_comments(source, classes, issues):
    """检查 XML 注释规范。
    规则：公共/受保护方法建议写 ///；私有方法可选；
    无论公私，只要写了 /// 就必须符合规范（summary 20字 + param/returns 完整）。
    """
    for cls in classes:
        for mth in cls['methods']:
            if mth.name == '#ctor':
                # 构造函数不强制要求注释
                continue
            doc = parse_doc_comment(source, _find_sig_start(source, mth))
            if mth.is_public_api:
                if not doc:
                    issues.append(Issue(
                        "A.注释规范", Issue.SEVERITY_WARN, mth.start_line,
                        f"公共方法 {mth.name} 缺少 /// XML 注释",
                    ))
                    continue
                mth.has_doc_comment = True
                _check_method_doc_quality(doc, mth, "公共方法", issues)
            else:
                if not doc:
                    # 私有方法可选，不写也不报错
                    continue
                mth.has_doc_comment = True
                _check_method_doc_quality(doc, mth, "私有方法", issues)

        # 属性注释：公共/受保护属性建议写一行 summary
        for prop in cls['properties']:
            if prop.access not in ('public', 'protected'):
                continue
            doc = parse_doc_comment(source, _find_sig_start(source, prop))
            prop.has_doc_comment = bool(doc)
            if not doc:
                issues.append(Issue(
                    "A.注释规范", Issue.SEVERITY_INFO, prop.start_line,
                    f"公共属性 {prop.name} 建议添加一行 /// <summary> 注释",
                ))


def _check_method_doc_quality(doc, mth, label, issues):
    """检查方法 XML 注释的质量（summary/param/returns 规范）。
    label 用于报错前缀，如"公共方法"或"私有方法"。
    """
    # summary
    sm = DOC_SUMMARY_RE.search(doc)
    if not sm:
        issues.append(Issue(
            "A.注释规范", Issue.SEVERITY_WARN, mth.start_line,
            f"{label} {mth.name} 的 /// 注释缺少 <summary>",
        ))
    else:
        summary = sm.group(1).strip()
        mth.doc_summary = summary
        # 20字限制（汉字计数）
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', summary))
        if chinese_chars > 20:
            issues.append(Issue(
                "A.注释规范", Issue.SEVERITY_WARN, mth.start_line,
                f"{label} {mth.name} 的 summary 超过20字（{chinese_chars}字），"
                f"应只描述\"做什么\"，不写过程",
                summary,
            ))
        # 检查是否包含过程描述词
        process_words = ['首先', '然后', '接着', '最后', '步骤',
                         '调用', '通过', '内部']
        if any(w in summary for w in process_words):
            issues.append(Issue(
                "A.注释规范", Issue.SEVERITY_INFO, mth.start_line,
                f"{label} {mth.name} 的 summary 可能包含过程描述，"
                f"summary 应只说明功能，不写实现过程",
                summary,
            ))
    # param 检查
    param_names = _parse_param_names(mth.params)
    found_params = {}
    for pm in DOC_PARAM_RE.finditer(doc):
        found_params[pm.group(1)] = pm.group(2).strip()
    mth.doc_params = list(found_params.items())
    for pname in param_names:
        if pname not in found_params:
            issues.append(Issue(
                "A.注释规范", Issue.SEVERITY_WARN, mth.start_line,
                f"{label} {mth.name} 的参数 \"{pname}\" 缺少 <param> 注释",
            ))
    for pname, ptext in found_params.items():
        if pname not in param_names:
            issues.append(Issue(
                "A.注释规范", Issue.SEVERITY_INFO, mth.start_line,
                f"{label} {mth.name} 的 <param name=\"{pname}\"> "
                f"在方法签名中不存在",
            ))
        if not ptext or ptext == pname:
            issues.append(Issue(
                "A.注释规范", Issue.SEVERITY_WARN, mth.start_line,
                f"{label} {mth.name} 的参数 \"{pname}\" 注释无信息"
                f"（\"{ptext}\"），应说明含义/取值范围",
            ))
    # returns 检查
    if mth.return_type.strip() != 'void':
        rm = DOC_RETURNS_RE.search(doc)
        if not rm:
            issues.append(Issue(
                "A.注释规范", Issue.SEVERITY_WARN, mth.start_line,
                f"{label} {mth.name} 有返回值但缺少 <returns> 注释",
            ))
        else:
            mth.has_returns = True
            rtext = rm.group(1).strip()
            if rtext in ('返回结果', '结果', '返回值', ''):
                issues.append(Issue(
                    "A.注释规范", Issue.SEVERITY_WARN,
                    mth.start_line,
                    f"{label} {mth.name} 的 <returns> 注释无信息"
                    f"（\"{rtext}\"），应说明返回值含义",
                ))


def _find_sig_start(source, method):
    """根据方法的 start_line 找到签名在 source 中的大致位置。"""
    lines = source.split('\n')
    pos = 0
    for i in range(method.start_line - 1):
        pos += len(lines[i]) + 1
    return pos


def _parse_param_names(params_str):
    """从参数字符串提取参数名列表。"""
    if not params_str.strip():
        return []
    names = []
    depth = 0
    current = ''
    for ch in params_str:
        if ch == '<' or ch == '[':
            depth += 1
            current += ch
        elif ch == '>' or ch == ']':
            depth -= 1
            current += ch
        elif ch == ',' and depth == 0:
            names.append(_extract_param_name(current.strip()))
            current = ''
        else:
            current += ch
    if current.strip():
        names.append(_extract_param_name(current.strip()))
    return [n for n in names if n]


def _extract_param_name(param_decl):
    """从 'ref int id' / 'out string name' / 'string s = null' 提取参数名。"""
    param_decl = re.sub(r'\s*=\s*.*$', '', param_decl)  # 去掉默认值
    tokens = param_decl.split()
    if not tokens:
        return ''
    # 去掉 ref/out/in/params
    while tokens and tokens[0] in ('ref', 'out', 'in', 'params', 'this'):
        tokens.pop(0)
    if not tokens:
        return ''
    # 最后一个 token 是参数名（可能带 [] 但数组在类型后）
    name = tokens[-1]
    # 处理 params int[] args
    name = name.lstrip('@')
    return name


def check_logic_issues(source, classes, issues):
    """检查代码逻辑精简问题。"""
    for cls in classes:
        # 枚举检查
        _check_enums(cls, issues)
        # 属性检查
        _check_properties(cls, issues)

        for mth in cls['methods']:
            body = mth.body_text
            body_clean = remove_all_comments(strip_strings_and_chars(body))
            offset_line = mth.start_line

            _check_null_checks(body, body_clean, offset_line, mth, issues)
            _check_locks(body_clean, offset_line, mth, issues)
            _check_redundant_assignment(body_clean, offset_line, mth, issues)
            _check_waits(body_clean, offset_line, mth, issues)
            _check_resource_management(body_clean, offset_line, mth, issues)
            _check_temp_vars(body, body_clean, offset_line, mth, issues)


def _check_enums(cls, issues):
    for enum_info in cls['enums']:
        name = enum_info['name']
        line = enum_info['line']
        if name.endswith('Enum'):
            issues.append(Issue(
                "B.过度枚举", Issue.SEVERITY_WARN, line,
                f"枚举 {name} 带 Enum 后缀，C# 惯例不加此后缀",
            ))


def _check_properties(cls, issues):
    for prop in cls['properties']:
        # public set 但可能只在构造函数用——需要检查
        if prop.has_set and prop.set_access == 'public':
            issues.append(Issue(
                "B.过度属性", Issue.SEVERITY_INFO, prop.start_line,
                f"属性 {prop.name} 声明了 public set，确认是否需要外部修改；"
                f"若仅构造函数赋值，应改为 {{ get; }} 只读属性",
            ))
        # 属性体有复杂逻辑
        if prop.body_text and len(prop.body_text) > 20:
            issues.append(Issue(
                "B.过度属性", Issue.SEVERITY_INFO, prop.start_line,
                f"属性 {prop.name} 的访问器包含逻辑，确认是否应改为方法；"
                f"属性 get 不应包含重操作或副作用",
                prop.body_text[:100],
            ))


def _check_null_checks(body, body_clean, offset_line, mth, issues):
    """检测无意义 null 检查模式。"""
    lines = body.split('\n')
    clean_lines = body_clean.split('\n')

    for i, (raw, clean) in enumerate(zip(lines, clean_lines)):
        ln = offset_line + i + 1  # 近似行号
        cs = clean.strip()

        # if (new X() == null) / if (new X() != null)
        if re.search(r'new\s+[\w<>\.]+\s*\([^)]*\)\s*[!=]=\s*null', cs):
            issues.append(Issue(
                "B.无意义Null检查", Issue.SEVERITY_WARN, ln,
                f"方法 {mth.name}: 对 new 表达式结果检查 null，new 永远不返回 null",
                raw.strip(),
            ))

        # if (this == null) / if (this != null)
        if re.search(r'this\s*[!=]=\s*null', cs):
            issues.append(Issue(
                "B.无意义Null检查", Issue.SEVERITY_WARN, ln,
                f"方法 {mth.name}: 对 this 检查 null，实例方法内 this 不可能为 null",
                raw.strip(),
            ))

        # 空 if 块：if (x == null) { } 或 if (x != null) { }
        if re.search(r'if\s*\([^)]*[!=]=\s*null[^)]*\)\s*\{\s*\}', cs):
            issues.append(Issue(
                "B.无意义Null检查", Issue.SEVERITY_WARN, ln,
                f"方法 {mth.name}: null 检查后是空块，无任何处理逻辑",
                raw.strip(),
            ))

        # 值类型 null 检查（int/bool/DateTime/decimal/double/long 等）
        vt = r'(int|bool|double|float|decimal|long|short|byte|char|DateTime|' \
             r'TimeSpan|Guid|DateTimeOffset|sbyte|uint|ulong|ushort|enum)'
        if re.search(rf'\b{vt}\s+\w+\s*[!=]=\s*null', cs):
            issues.append(Issue(
                "B.无意义Null检查", Issue.SEVERITY_WARN, ln,
                f"方法 {mth.name}: 对值类型变量检查 null，值类型永不为 null",
                raw.strip(),
            ))

    # 私有方法参数 null 检查统计
    if mth.access == 'private':
        null_arg_checks = re.findall(
            r'if\s*\(\s*(\w+)\s*==\s*null\s*\)\s*'
            r'(?:throw\s+new\s+Argument\w*Exception)?',
            body_clean,
        )
        param_names = _parse_param_names(mth.params)
        redundant = [p for p in null_arg_checks if p in param_names]
        if redundant:
            issues.append(Issue(
                "B.无意义Null检查", Issue.SEVERITY_INFO, mth.start_line,
                f"私有方法 {mth.name} 对参数 {redundant} 做 null 检查，"
                f"私有方法不是公开边界，应信任调用链；若参数确实可能为 null 则保留",
            ))

    # new 出来的对象紧接着检查 null（数据流启发式）
    for i, line in enumerate(clean_lines):
        mnew = re.match(
            r'\s*(?:var|[\w<>\?\[\]]+)\s+(\w+)\s*=\s*new\s+[\w<>\.]+\s*\(',
            line,
        )
        if mnew:
            var_name = mnew.group(1)
            for j in range(i + 1, min(i + 4, len(clean_lines))):
                ns = clean_lines[j].strip()
                if not ns:
                    continue
                if re.search(rf'\b{re.escape(var_name)}\s*[!=]=\s*null', ns):
                    ln = offset_line + j + 1
                    issues.append(Issue(
                        "B.无意义Null检查", Issue.SEVERITY_WARN, ln,
                        f"方法 {mth.name}: 变量 \"{var_name}\" 由 new 创建，"
                        f"new 永远不返回 null，后续 null 检查无意义",
                        lines[j].strip(),
                    ))
                break


def _check_locks(body_clean, offset_line, mth, issues):
    # lock (new object())
    for m in re.finditer(r'lock\s*\(\s*new\s+object\s*\(\s*\)\s*\)',
                         body_clean):
        ln = offset_line + body_clean[:m.start()].count('\n') + 1
        issues.append(Issue(
            "B.无意义锁", Issue.SEVERITY_ERROR, ln,
            f"方法 {mth.name}: lock(new object()) 每次锁定不同对象，完全无效",
        ))

    # lock(this) / lock(typeof(...))
    for m in re.finditer(r'lock\s*\(\s*(this|typeof\s*\([^)]+\))\s*\)',
                         body_clean):
        ln = offset_line + body_clean[:m.start()].count('\n') + 1
        issues.append(Issue(
            "B.无意义锁", Issue.SEVERITY_WARN, ln,
            f"方法 {mth.name}: 避免 lock(this)/lock(typeof)，外部可锁定导致死锁；"
            f"应使用 private readonly object 锁对象",
        ))

    # lock 内 Thread.Sleep / IO 操作
    for m in re.finditer(r'lock\s*\([^)]+\)\s*\{', body_clean):
        brace = body_clean.find('{', m.start())
        end = find_matching_brace(body_clean, brace)
        if end == -1:
            continue
        block = body_clean[brace:end]
        first_line = offset_line + body_clean[:m.start()].count('\n') + 1
        if re.search(r'Thread\.Sleep|\.Wait\(\)|\.Result\b|MessageBox\.Show',
                     block):
            issues.append(Issue(
                "B.无意义锁", Issue.SEVERITY_WARN, first_line,
                f"方法 {mth.name}: lock 块内包含 Sleep/Wait/MessageBox 等阻塞操作，"
                f"会严重拖垮并发甚至死锁",
            ))
        if re.search(r'\.Execute|\.Query|\.Read\(\)|\.Write\(|File\.|Socket',
                     block):
            issues.append(Issue(
                "B.无意义锁", Issue.SEVERITY_INFO, first_line,
                f"方法 {mth.name}: lock 块内可能包含 IO/数据库操作，"
                f"确认是否必要；锁内应只做内存操作",
            ))


def _check_redundant_assignment(body_clean, offset_line, mth, issues):
    """检测无意义赋值传递。"""
    lines = body_clean.split('\n')

    # var result = SomeCall(); return result;  模式
    for i, line in enumerate(lines):
        s = line.strip()
        mvar = re.match(
            r'(?:var|[\w<>\?\[\]]+)\s+(\w+)\s*=\s*(.+?);\s*$', s
        )
        if mvar:
            var_name = mvar.group(1)
            # 向下找最近的非空行
            for j in range(i + 1, min(i + 4, len(lines))):
                ns = lines[j].strip()
                if not ns:
                    continue
                if re.match(rf'return\s+{re.escape(var_name)}\s*;', ns):
                    ln = offset_line + i + 1
                    issues.append(Issue(
                        "B.冗余赋值传递", Issue.SEVERITY_INFO, ln,
                        f"方法 {mth.name}: 变量 \"{var_name}\" 赋值后立即 return，"
                        f"应直接 return 表达式",
                        s,
                    ))
                break

    # 参数原样赋给局部变量：void M(Foo config) { var cfg = config; ... }
    param_names = _parse_param_names(mth.params)
    for i, line in enumerate(lines):
        s = line.strip()
        mvar = re.match(
            r'(?:var|[\w<>\?\[\]]+)\s+(\w+)\s*=\s*(\w+)\s*;', s
        )
        if mvar and mvar.group(2) in param_names and mvar.group(1) != mvar.group(2):
            ln = offset_line + i + 1
            issues.append(Issue(
                "B.冗余赋值传递", Issue.SEVERITY_INFO, ln,
                f"方法 {mth.name}: 参数 \"{mvar.group(2)}\" 原样赋给局部变量 "
                f"\"{mvar.group(1)}\"，无转换，应直接使用参数",
                s,
            ))

    # this.X = X; 自赋值
    for i, line in enumerate(lines):
        s = line.strip()
        if re.match(r'this\.\w+\s*=\s*this\.\w+\s*;', s):
            ln = offset_line + i + 1
            issues.append(Issue(
                "B.冗余赋值传递", Issue.SEVERITY_WARN, ln,
                f"方法 {mth.name}: 属性/字段自赋值",
                s,
            ))


def _check_waits(body_clean, offset_line, mth, issues):
    patterns = [
        (r'Thread\.Sleep\s*\(', 'Thread.Sleep',
         '使用 Thread.Sleep 等待，不可靠且阻塞线程；异步操作用 await，'
         '条件等待用事件/信号量'),
        (r'\.Wait\(\)', '.Wait()',
         '阻塞等待 Task，可能死锁（尤其 UI 线程）；应使用 await'),
        (r'\.Result\b', '.Result',
         '访问 Task.Result 阻塞，可能死锁；应使用 await'),
        (r'Task\.Delay\s*\(\s*0\s*\)', 'Task.Delay(0)',
         'Task.Delay(0) 无意义，直接执行即可'),
        (r'GC\.Collect\s*\(\s*\)', 'GC.Collect()',
         '手动调用 GC.Collect 干扰 GC 策略，性能极差，应移除'),
    ]
    for pattern, label, desc in patterns:
        for m in re.finditer(pattern, body_clean):
            ln = offset_line + body_clean[:m.start()].count('\n') + 1
            sev = Issue.SEVERITY_WARN
            if 'Sleep' in label or '.Wait' in label or '.Result' in label:
                sev = Issue.SEVERITY_WARN
            issues.append(Issue(
                "B.过度等待/延迟", sev, ln,
                f"方法 {mth.name}: {desc}",
                label,
            ))


def _check_resource_management(body_clean, offset_line, mth, issues):
    # GC.Collect
    for m in re.finditer(r'GC\.Collect\s*\(\s*\)', body_clean):
        ln = offset_line + body_clean[:m.start()].count('\n') + 1
        issues.append(Issue(
            "B.过度资源管理", Issue.SEVERITY_WARN, ln,
            f"方法 {mth.name}: 手动 GC.Collect，应移除",
        ))

    # GC.SuppressFinalize 在没有析构函数的类中（跨方法检查在外部做）
    # 析构函数
    for m in re.finditer(r'~\w+\s*\(\s*\)', body_clean):
        ln = offset_line + body_clean[:m.start()].count('\n') + 1
        issues.append(Issue(
            "B.过度资源管理", Issue.SEVERITY_INFO, ln,
            f"方法 {mth.name}: 定义了析构函数（终结器），仅当类直接持有非托管资源时需要；"
            f"纯托管字段不需要终结器",
        ))

    # using 嵌套层数
    using_positions = [(m.start(), m.group()) for m in
                       re.finditer(r'using\s*\([^)]+\)', body_clean)]
    if len(using_positions) >= 4:
        ln = offset_line + body_clean[:using_positions[0][0]].count('\n') + 1
        issues.append(Issue(
            "B.过度资源管理", Issue.SEVERITY_INFO, ln,
            f"方法 {mth.name}: using 嵌套 {len(using_positions)} 层，"
            f"建议提取工厂方法或使用高层封装",
        ))


def _check_temp_vars(body, body_clean, offset_line, mth, issues):
    """检测无意义临时变量。"""
    raw_lines = body.split('\n')
    lines = body_clean.split('\n')
    for i, line in enumerate(lines):
        s = line.strip()
        mvar = re.match(
            r'(?:var|[\w<>\?\[\]]+)\s+(temp|tmp|data|result|value|val|item|obj)\s*=\s*(.+);',
            s, re.IGNORECASE,
        )
        if mvar:
            var_name = mvar.group(1)
            # 检查这个变量在后续使用了几次
            rest = '\n'.join(lines[i + 1:])
            uses = len(re.findall(rf'\b{re.escape(var_name)}\b', rest))
            if uses <= 1:
                ln = offset_line + i + 1
                raw_snippet = raw_lines[i].strip() if i < len(raw_lines) else s
                issues.append(Issue(
                    "B.临时变量滥用", Issue.SEVERITY_INFO, ln,
                    f"方法 {mth.name}: 临时变量 \"{var_name}\" 命名无意义"
                    f"且后续仅使用 {uses} 次，考虑内联或改为有业务含义的名称",
                    raw_snippet,
                ))


def check_function_simplification(source, classes, issues):
    """检查函数精简：功能重叠、嵌套内联、死函数。"""
    for cls in classes:
        methods = cls['methods']
        method_names = {m.name for m in methods if m.name != '#ctor'}

        # 构建调用关系
        _build_call_graph(methods, method_names)

        # 功能重叠检测
        _check_overlapping_methods(methods, issues)

        # 嵌套内联候选
        _check_inline_candidates(methods, issues)

        # 死函数检测
        _check_dead_methods(methods, method_names, issues)


def _build_call_graph(methods, method_names):
    for mth in methods:
        body_clean = remove_all_comments(strip_strings_and_chars(mth.body_text))
        # 找方法调用：标识符后跟 (
        calls = set()
        for m in re.finditer(r'\b([A-Za-z_]\w*)\s*(?:<[^>]+>)?\s*\(',
                             body_clean):
            name = m.group(1)
            if name in method_names and name != mth.name:
                calls.add(name)
            # 构造函数调用：new ClassName(
        mth.callees = list(calls)
        for called in calls:
            for other in methods:
                if other.name == called and other is not mth:
                    other.callers.append(mth.name)


def _normalize_name(name):
    """归一化方法名：去除常见后缀。"""
    n = name
    for suffix in ('V2', 'V3', 'Ex', 'Ex2', 'New', 'Old', 'Legacy',
                   'Backup', 'WithDetail', 'WithItems', 'WithCustomer',
                   'WithNotification', 'AndLog', 'Helper', 'Internal',
                   'Core', 'Wrapper'):
        if n.endswith(suffix) and len(n) > len(suffix):
            n = n[:-len(suffix)]
            break
    return n


def _body_tokens(body_text):
    """提取方法体的 token 集合（用于相似度比较）。"""
    clean = remove_all_comments(strip_strings_and_chars(body_text))
    tokens = re.findall(r'[A-Za-z_]\w*', clean)
    # 过滤关键字
    kws = {'if', 'else', 'for', 'foreach', 'while', 'do', 'switch', 'case',
           'break', 'continue', 'return', 'try', 'catch', 'finally', 'using',
           'lock', 'new', 'var', 'true', 'false', 'null', 'this', 'base',
           'throw', 'is', 'as', 'in', 'out', 'ref', 'default', 'nameof',
           'typeof', 'void', 'string', 'int', 'bool', 'double', 'float',
           'decimal', 'long', 'short', 'byte', 'char', 'object', 'var',
           'get', 'set', 'public', 'private', 'protected', 'internal',
           'static', 'readonly', 'const', 'class', 'struct', 'interface',
           'enum', 'namespace', 'async', 'await', 'yield'}
    return [t for t in tokens if t not in kws and len(t) > 1]


def _jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _check_overlapping_methods(methods, issues):
    # 按归一化名称聚类
    clusters = defaultdict(list)
    for mth in methods:
        if mth.name == '#ctor' or mth.is_virtual_override:
            continue
        norm = _normalize_name(mth.name)
        clusters[norm].append(mth)

    for norm, group in clusters.items():
        if len(group) < 2:
            continue
        # 两两比较
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                tokens_a = set(_body_tokens(a.body_text))
                tokens_b = set(_body_tokens(b.body_text))
                sim = _jaccard(tokens_a, tokens_b)
                if sim >= 0.5:
                    issues.append(Issue(
                        "C.功能重叠", Issue.SEVERITY_WARN, b.start_line,
                        f"方法 \"{b.name}\" 与 \"{a.name}\"（行{a.start_line}）"
                        f"功能重叠（token相似度 {sim:.0%}），考虑合并。"
                        f"AI 迭代时常新增函数而非修改已有函数",
                        f"{a.name} vs {b.name}",
                    ))

    # 检查同步/异步包装对：XAsync() { return Task.Run(() => X()); }
    for mth in methods:
        if mth.name.endswith('Async') and mth.is_public_api:
            body_clean = remove_all_comments(
                strip_strings_and_chars(mth.body_text))
            sync_name = mth.name[:-5]
            if re.search(rf'Task\.Run\s*\([^)]*\b{re.escape(sync_name)}\b',
                         body_clean):
                issues.append(Issue(
                    "C.功能重叠", Issue.SEVERITY_WARN, mth.start_line,
                    f"方法 {mth.name} 仅用 Task.Run 包装同步方法 {sync_name}，"
                    f"属于伪异步，应直接实现异步逻辑或不提供 Async 版本",
                ))

    # 检查旧函数残留
    for mth in methods:
        if re.search(r'(Old|Legacy|Backup|_Old|_Backup|_Deprecated)$', mth.name,
                     re.IGNORECASE):
            issues.append(Issue(
                "C.功能重叠", Issue.SEVERITY_INFO, mth.start_line,
                f"方法 {mth.name} 名称暗示是旧版本残留，确认无调用后删除",
            ))


def _check_inline_candidates(methods, issues):
    # 判断性/校验性函数名即使短也保留（表达独立业务概念）
    predicate_prefixes = ('Is', 'Can', 'Has', 'Should', 'Validate',
                          'Check', 'Ensure', 'Need')
    for mth in methods:
        if mth.name == '#ctor':
            continue
        if mth.access != 'private':
            continue
        if mth.is_virtual_override:
            continue
        if any(mth.name.startswith(p) for p in predicate_prefixes):
            continue
        # 只被一个方法调用
        unique_callers = set(mth.callers)
        if len(unique_callers) != 1:
            continue
        # 方法体不超过 3 行有效代码
        if mth.effective_body_lines > 3:
            continue
        # 不含复杂控制流
        body_clean = remove_all_comments(strip_strings_and_chars(mth.body_text))
        if CONTROL_FLOW_RE.search(body_clean):
            # 允许简单 if，但不允许循环/switch/try
            if re.search(r'\b(for|foreach|while|switch|try|catch)\b',
                         body_clean):
                continue
        # 不含递归
        if re.search(rf'\b{re.escape(mth.name)}\s*\(', body_clean):
            continue

        caller_name = next(iter(unique_callers))
        issues.append(Issue(
            "C.嵌套内联", Issue.SEVERITY_INFO, mth.start_line,
            f"私有方法 {mth.name} 仅被 {caller_name} 调用一次，"
            f"方法体仅 {mth.effective_body_lines} 行有效代码，"
            f"考虑内联到 {caller_name} 中（AI 迭代时常为新增一步单独建函数）",
        ))


def _check_dead_methods(methods, method_names, issues):
    # 检查文件内是否有事件订阅/委托引用（+= 或 new Action/Func/EventHandler）
    all_body = '\n'.join(m.body_text for m in methods)
    referenced_in_delegate = set()
    for m in re.finditer(r'\+=\s*(?:new\s+\w+\s*\(\s*)?([A-Za-z_]\w*)',
                         all_body):
        referenced_in_delegate.add(m.group(1))
    for m in re.finditer(r'(?:Action|Func|EventHandler)\s*<[^>]*>\s*\(\s*([A-Za-z_]\w*)',
                         all_body):
        referenced_in_delegate.add(m.group(1))

    for mth in methods:
        if mth.name == '#ctor':
            continue
        if mth.is_public_api:
            continue  # 公共方法可能被外部调用
        if mth.is_virtual_override:
            continue
        if mth.name in referenced_in_delegate:
            continue
        # 检查 nameof 引用
        if re.search(rf'nameof\s*\(\s*{re.escape(mth.name)}\s*\)', all_body):
            continue
        # 方法组引用（如 new Thread(RunLoop)、Func<T> f = Handler,）也视为被引用
        if re.search(rf'\b{re.escape(mth.name)}\b\s*[,)]', all_body):
            continue
        if len(mth.callers) == 0:
            issues.append(Issue(
                "C.疑似死函数", Issue.SEVERITY_INFO, mth.start_line,
                f"私有方法 {mth.name} 在本文件内无调用，"
                f"确认无反射/委托/外部引用后可删除",
            ))


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def _check_file_level_enums(source, classes, issues):
    """检查类外定义的枚举（命名空间级别）及 Enum 后缀。"""
    clean = strip_strings_and_chars(source)
    # 收集所有类体范围，排除类体内的枚举（已在 _check_enums 中处理）
    class_ranges = [(c['body_start'], c['body_end']) for c in classes]
    for m in ENUM_RE.finditer(clean):
        pos = m.start()
        in_class = any(s <= pos <= e for s, e in class_ranges)
        if in_class:
            continue
        name = m.group(1)
        ln = line_of(source, pos)
        if name.endswith('Enum'):
            issues.append(Issue(
                "B.过度枚举", Issue.SEVERITY_WARN, ln,
                f"枚举 {name} 带 Enum 后缀，C# 惯例不加此后缀",
            ))
        # 检查枚举是否被使用（简单启发式：除了定义处，文件中是否出现该名称）
        uses = len(re.findall(rf'\b{re.escape(name)}\b', clean)) - 1
        if uses == 0:
            issues.append(Issue(
                "B.过度枚举", Issue.SEVERITY_INFO, ln,
                f"枚举 {name} 在本文件中未被使用，确认是否需要定义",
            ))


def review_file(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        source = f.read()

    filename = filepath.lower()
    issues = []

    # designer.cs 不处理
    if filename.endswith('.designer.cs'):
        issues.append(Issue(
            "系统", Issue.SEVERITY_INFO, 1,
            "designer.cs 文件为设计器自动生成，按规则不检测",
        ))
        return issues

    classes = parse_file(source)

    if not classes:
        issues.append(Issue(
            "系统", Issue.SEVERITY_INFO, 1,
            "未在文件中找到 class/struct/interface 定义",
        ))
        return issues

    check_regions_and_order(source, classes, issues)
    check_doc_comments(source, classes, issues)
    check_logic_issues(source, classes, issues)
    check_function_simplification(source, classes, issues)
    _check_file_level_enums(source, classes, issues)

    # 按行号排序
    issues.sort(key=lambda x: (x.line, x.category))
    return issues


def format_report(issues, filepath, verbose=False):
    lines = []
    lines.append(f"代码审查报告: {filepath}")
    lines.append("=" * 70)

    if not issues:
        lines.append("未发现问题。")
        return '\n'.join(lines)

    # 按类别分组
    by_category = defaultdict(list)
    for issue in issues:
        by_category[issue.category].append(issue)

    error_count = sum(1 for i in issues if i.severity == Issue.SEVERITY_ERROR)
    warn_count = sum(1 for i in issues if i.severity == Issue.SEVERITY_WARN)
    info_count = sum(1 for i in issues if i.severity == Issue.SEVERITY_INFO)

    lines.append(f"共 {len(issues)} 项: {error_count} 错误 / "
                 f"{warn_count} 警告 / {info_count} 提示")
    lines.append("")

    for category in sorted(by_category.keys()):
        cat_issues = by_category[category]
        lines.append(f"── {category} ({len(cat_issues)} 项) " + "─" * 40)
        for issue in cat_issues:
            if not verbose and issue.severity == Issue.SEVERITY_INFO:
                # 非verbose模式下info折叠显示
                pass
            sev_mark = {
                Issue.SEVERITY_ERROR: "[错误]",
                Issue.SEVERITY_WARN: "[警告]",
                Issue.SEVERITY_INFO: "[提示]",
            }[issue.severity]
            lines.append(f"  行{issue.line:>5} {sev_mark} {issue.message}")
            if issue.snippet:
                snippet = issue.snippet[:120]
                lines.append(f"         >> {snippet}")
        lines.append("")

    if not verbose:
        info_total = sum(
            1 for cat in by_category.values()
            for i in cat if i.severity == Issue.SEVERITY_INFO
        )
        if info_total:
            lines.append(f"（另有 {info_total} 项提示，使用 --verbose 查看全部）")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='.NET 4.8 / C# 7.3 单文件冗余代码扫描器')
    parser.add_argument('file', help='要扫描的 .cs 文件路径')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式输出')
    parser.add_argument('--verbose', action='store_true',
                        help='显示所有项（含提示级别）')
    args = parser.parse_args()

    try:
        issues = review_file(args.file)
    except FileNotFoundError:
        print(f"错误: 文件不存在: {args.file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"扫描出错: {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps(
            [i.to_dict() for i in issues],
            ensure_ascii=False, indent=2,
        ))
    else:
        print(format_report(issues, args.file, args.verbose))

    # 有 error 或 warn 时返回非零退出码
    hard = sum(1 for i in issues
               if i.severity in (Issue.SEVERITY_ERROR, Issue.SEVERITY_WARN))
    sys.exit(1 if hard else 0)


if __name__ == '__main__':
    main()
