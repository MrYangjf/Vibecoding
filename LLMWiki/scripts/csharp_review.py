#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
csharp_review.py — .NET Framework 4.8 / C# 7.3 单文件冗余代码扫描器

扫描单个 .cs 文件（Designer.cs 只做字体规范检查，不跟踪外部引用），输出以下类别的问题候选：
  A. 文件书写整理：成员顺序、#region 划分、XML 注释规范、字体规范（默认 Microsoft YaHei UI）
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

# 存量注释欠账（顶层裁定 3：不追溯、不设全库清零目标）默认不进入清单；
# --verbose 可查看全部，便于按文件夹渐进偿还。
INCLUDE_LEGACY = False


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

# 当前被扫描的文件（供判据豁免清单按路径匹配使用；单线程 CLI 工具）
CURRENT_FILE = ""


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
        # 2026-10-29：从类名之后继续搜索，才能把**嵌套类型**也收进 classes；
        # 否则外层类的嵌套方法会被当成外层成员，造成成员顺序假违规。
        pos = m.end()

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
        # 2026-10-29：析构函数 `~ClassName()` 被 CTOR_RE 误当成构造函数；
        # 它不是成员顺序里的「构造函数」，不参与顺序判定。
        if m.start('name') > 0 and source[m.start('name') - 1] == '~':
            pos = m.end()
            continue
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
    # 逐字符花括号深度：字段只认类体深度 1，方法内局部变量（深度≥2）一律排除
    depth_at = []
    d = 0
    for ch in scan_text:
        depth_at.append(d)
        if ch == '{':
            d += 1
        elif ch == '}':
            d -= 1

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
        # scan_text 从类体 '{' 之后开始 ⇒ 类成员深度为 0，方法体内局部变量深度 ≥1
        if depth_at[m.start()] != 0:
            continue
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

    # 检查 region 配对
    if len(regions) != len(endregions):
        issues.append(Issue(
            "A.文件整理", Issue.SEVERITY_ERROR, regions[0][0],
            f"#region({len(regions)}) 与 #endregion({len(endregions)}) 数量不匹配",
        ))

    # 2026-10-26（M2 裁决，见 standards/CodeSimplification 第一节①）：
    # 语义 region 与类型 region 并存，只强制配对完整性。
    # 原「未使用类型 region」「缺少某类 region」两条判据已废止（248 处全为误报）。
    # 新增硬要求：region 名禁含过程性命名。
    # ⚠ 禁词须避开**领域名词**：「临时文件」是业务术语不是过程性命名，
    # 裸禁「临时」会误伤（实测 RecordFileStore.cs 的「临时文件处理/临时文件列表」）。
    bad_region_names = ('新增功能', 'TODO', '待办', '临时改动', '调试用', '废弃')
    for rln, rname, _ in regions:
        if any(bad in rname for bad in bad_region_names):
            issues.append(Issue(
                "A.文件整理", Issue.SEVERITY_WARN, rln,
                f"#region 名「{rname}」含过程性命名，改为语义或类型命名",
            ))

    # 检查每个类的成员顺序（2026-10-26 业主裁定：**region 内排序，跨 region 不比较**）
    lines = source.split('\n')
    seg_of = [0] * (len(lines) + 2)
    title_of = [""] * (len(lines) + 2)
    cur_seg = 0
    cur_title = "(无 region)"
    for i, ln_text in enumerate(lines, 1):
        s = ln_text.strip()
        if s.startswith('#region'):
            cur_seg += 1
            cur_title = s[len('#region'):].strip() or "(未命名 region)"
        seg_of[i] = cur_seg
        title_of[i] = cur_title
        if s.startswith('#endregion'):
            cur_seg += 1
            cur_title = "(无 region)"
    def _nested_ranges(cls):
        cs = cls.get('start_line') or 0
        ce = cls.get('end_line') or 0
        out = []
        for c in classes:
            if c is cls:
                continue
            s = c.get('start_line') or 0
            e = c.get('end_line') or 0
            if cs < s and e <= ce:
                out.append((s, e))
        return out

    for cls in classes:
        nested = _nested_ranges(cls)

        def _in_nested(ln, _n=nested):
            return any(s <= ln <= e for s, e in _n)

        members = []
        for f in cls['fields']:
            # 2026-10-26：嵌套类型（class/struct/interface/enum）被字段正则误收，
            # 但标准 §一① 明确「嵌套类型/显式接口实现置后独立 region」⇒ 不参与顺序判定。
            if _in_nested(f.start_line) or re.search(r'\b(class|struct|interface|enum)\b', f.ftype or ''):
                continue
            order = 1 if f.access == 'private' else 2
            members.append((order, f.start_line, f"字段 {f.access} {f.ftype} {f.name}"))
        for p in cls['properties']:
            if _in_nested(p.start_line) or re.search(r'\b(class|struct|interface|enum)\b', p.ftype or ''):
                continue
            order = 2 if p.access in ('public', 'protected') else 1
            members.append((order, p.start_line, f"属性 {p.access} {p.ftype} {p.name}"))
        cls_name = cls.get('name') or ''
        ctor_decl_re = re.compile(
            r'^\s*(?:public|private|protected|internal)\s+'
            + re.escape(cls_name) + r'\s*\('
        ) if cls_name else None
        for mth in cls['methods']:
            if _in_nested(mth.start_line):
                continue
            # 解析器会把 `else if (...)` / `while (...)` 等控制流行误收为方法；
            # 它们不是类成员，不参与顺序判定（否则幽灵方法会把后续构造函数压成违规）。
            if mth.name in _DECL_SKIP_FIRST:
                continue
            decl = lines[mth.start_line - 1] if 0 < mth.start_line <= len(lines) else ''
            # 构造函数重载：带参构造常被解析成普通 public 方法（order 5），
            # 会让紧随其后的无参构造（order 3）被误判为顺序错误 —— 一律按 3 计。
            if mth.name == '#ctor' or (ctor_decl_re and ctor_decl_re.match(decl)):
                order = 3
            elif mth.access == 'private':
                order = 4
            else:
                order = 5
            members.append((order, mth.start_line, f"方法 {mth.access} {mth.name}"))

        members.sort(key=lambda x: x[1])
        prev = {}
        for order, ln, desc in members:
            sg = seg_of[ln] if 0 < ln < len(seg_of) else 0
            if order < prev.get(sg, 0):
                rname = title_of[ln] if 0 < ln < len(title_of) and title_of[ln] else "(无 region)"
                issues.append(Issue(
                    "A.文件整理", Issue.SEVERITY_WARN, ln,
                    f"成员顺序错误（region「{rname}」内）：{desc} 出现在更高顺序成员之后。"
                    f"应按 私有变量→公共变量→构造函数→私有函数→公共函数 排列",
                ))
                break
            prev[sg] = order


def check_duplicate_members(source, classes, issues):
    """CS0102 同类内成员重复定义（成员名 + 参数表相同）。

    2026-10-26：批量「成员重排 / 声明前移」编辑曾把同一字段**复制**两份
    （而非移动），编译器报 CS0102 + 成员二义性。此判据用于自动拦住该类缺陷。
    排除项（否则误报）：同名**不同参数表**是重载（合法）；P/Invoke 的
    `[DllImport(DllPath, EntryPoint = "...")]` 属性实参、方法内局部变量不计入。
    """
    lines = source.split('\n')
    # 条件编译指令行：#if / #else 互斥分支内的同名声明**不是**重复定义
    # （例：台达 Native 层的 DllPath 在 #if X86 / #else 各声明一次，实际只编译一支）
    pp_lines = set(i for i, ln in enumerate(lines, 1) if ln.lstrip().startswith('#'))

    def _exclusive(lns):
        """两次声明之间存在预处理指令 ⇒ 位于互斥分支 ⇒ 不算重复。"""
        return any(lns[0] < p < lns[-1] for p in pp_lines)

    fld_re = re.compile(r'^\s*(?:public|private|protected|internal)\s+'
                        r'(?:static\s+|readonly\s+|const\s+|volatile\s+|new\s+|async\s+)*'
                        r'[\w<>\[\],\.]+\s+(\w+)\s*(?:=|;|\{)')
    for cls in classes:
        cname = cls.get('name')
        # 1) 方法：同名 + 同参数表
        mc = defaultdict(list)
        for mth in cls.get('methods', []):
            nm = getattr(mth, 'name', None)
            if nm == '#ctor':
                continue
            ps = tuple(re.sub(r'\s+', ' ', str(p)).strip()
                       for p in (getattr(mth, 'params', None) or []))
            mc[(nm, ps)].append(getattr(mth, 'start_line', 0))
        for (nm, ps), lns in mc.items():
            if len(lns) > 1 and not _exclusive(sorted(lns)):
                issues.append(Issue(
                    "A.文件整理", Issue.SEVERITY_ERROR, lns[1],
                    f"类 {cname} 内方法 {nm}({', '.join(ps)}) 重复定义"
                    f"（CS0102），行 {lns}",
                ))
        # 2) 字段：类体深度 1 的严格字段声明
        sl = cls.get('start_line') or 1
        el = cls.get('end_line') or len(lines)
        fc = defaultdict(list)
        depth = 0
        for ln in range(sl, el + 1):
            if ln - 1 >= len(lines):
                break
            t = lines[ln - 1].strip()
            if t.startswith('[') and t.endswith(']'):
                continue
            if t.endswith('{'):
                depth += 1
                continue
            if t.startswith('}'):
                depth -= 1
                continue
            if depth == 1:
                m = fld_re.match(lines[ln - 1])
                if m:
                    fc[m.group(1)].append(ln)
        for nm, lns in fc.items():
            if len(lns) > 1 and not _exclusive(sorted(lns)):
                issues.append(Issue(
                    "A.文件整理", Issue.SEVERITY_ERROR, lns[1],
                    f"类 {cname} 内字段 {nm} 重复定义（CS0102），行 {lns}",
                ))


def check_dispose_pattern(source, issues):
    """ADR-002：非设计器 .cs 禁 Dispose(bool) 覆写（应实现标准 IDisposable.Dispose()）。

    2026-10-26 补入正式判据：此前该检查只存在于一次性审计脚本中，
    口径-判据映射表第 7 条与实现不符（由 simplify_selfcheck.py 抓出）。
    """
    for m in re.finditer(r'\bvoid\s+Dispose\s*\(\s*bool\b', source):
        ln = line_of(source, m.start())
        issues.append(Issue(
            "A.文件整理", Issue.SEVERITY_ERROR, ln,
            "禁 Dispose(bool) 覆写（ADR-002）：应实现标准 IDisposable.Dispose()",
        ))


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
                    # 2026-10-26（M1 裁决）：public 缺 /// 的覆盖口径收窄为
                    # 「新增或改动的 public 成员」——存量欠账不追溯、不设全库清零目标，
                    # 故由 WARN 降为 INFO；「写了就要写对」的质量类检查仍保持 WARN。
                    issues.append(Issue(
                        "A.注释规范", Issue.SEVERITY_INFO, mth.start_line,
                        f"公共方法 {mth.name} 未写 /// XML 注释"
                        f"（存量欠账不追溯；新增/改动必写）",
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


REC_LIMIT_CJK = 20
_CJK_RE = re.compile(r'[\u4e00-\u9fff]')
_SENT_RE = re.compile(r'[。；！？!?;]')
_TAG_STRIP_RE = re.compile(r'<[^>]*>')
_BLOCK_TAG_RE = re.compile(
    r'</?(?:summary|remarks|param|returns|value|exception|example|typeparam)\b[^>]*>')


def _merge_doc_block(doc):
    """C18：`///` 块合并成整段，跨行续写不得逃过长度检查。"""
    parts = []
    for raw in doc.replace('\r\n', '\n').split('\n'):
        s = raw.strip()
        if s.startswith('///'):
            s = s[3:]
        s = s.strip()
        if s:
            parts.append(s)
    merged = ' '.join(parts)
    merged = _BLOCK_TAG_RE.sub('。', merged)
    return _TAG_STRIP_RE.sub('', merged)


def _check_long_records(doc, mth, label, issues):
    """C16 + C18：一条注释记录正文 ≤20 汉字（跨行合并后计数）。"""
    for rec in _SENT_RE.split(_merge_doc_block(doc)):
        rec = rec.strip()
        if not rec:
            continue
        n = len(_CJK_RE.findall(rec))
        if n > REC_LIMIT_CJK:
            issues.append(Issue(
                "A.注释超20字", Issue.SEVERITY_WARN, mth.start_line,
                f"{label} {mth.name} 的注释单条记录 {n} 汉字（上限 20，跨行合并计），"
                f"应拆句或迁 wiki",
                rec,
            ))


_DECL_SKIP_FIRST = frozenset((
    'return', 'throw', 'break', 'continue', 'goto', 'using', 'yield',
    'else', 'case', 'lock', 'if', 'while', 'for', 'foreach', 'switch', 'do',
))
_DECL_RE = re.compile(
    r'^\s*(?:(?:public|private|protected|internal|static|readonly|const|volatile|'
    r'new|unsafe|extern|sealed|override|virtual|partial)\s+)*'
    r'(?P<type>[A-Za-z_][\w\.]*(?:\s*<[^;=]*?>)?(?:\s*\[\s*\])*\??)\s+'
    r'(?P<name>[A-Za-z_]\w*)\s*(?:=[^;]*)?;\s*(?P<trail>//(?!/).*)?$'
)


def _is_decl_line(line):
    line = line.rstrip('\r')
    m = _DECL_RE.match(line)
    if not m:
        return None
    first = line.strip().split()[0].rstrip('.;')
    if first in _DECL_SKIP_FIRST:
        return None
    return m


def _check_var_multiline_comments(source, issues):
    """C19：一个变量 / 字段的 `//` 注释只允许一行。"""
    lines = source.replace('\r\n', '\n').split('\n')
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
        above = _is_decl_line(lines[i - 1]) if i > 0 else None
        below = _is_decl_line(lines[j]) if j < n else None
        above_trail = 1 if (above and above.group('trail')) else 0
        below_trail = 1 if (below and below.group('trail')) else 0
        if above_trail and not below:
            total, decl_line = run + above_trail, i
        elif below:
            total, decl_line = run + below_trail, j + 1
        else:
            i = j
            continue
        if total > 1:
            issues.append(Issue(
                "A.变量注释多行", Issue.SEVERITY_WARN, decl_line,
                f"变量 / 字段注释占 {total} 行 //（只允许一行），"
                f"应合并为一行且 ≤20 汉字",
                lines[decl_line - 1].strip(),
            ))
        i = j


# 注释元信息判据（2026-11-20 业主裁定）：代码注释只写作用，
# 禁含 ⛔ / ADR 编号 / 日期 / 业主裁定 / 改版 / 「原为 X 现为 Y」等过程性元信息。
# 约束、历史、裁定一律由 LLMWiki 承载（CodeMap / api / lessons / decisions）。
COMMENT_META_RE = re.compile(
    r'(⛔|ADR-\d{2,3}|20\d{2}-\d{2}-\d{2}|20\d{2}-\d{2}\b'
    r'|业主裁定|业主实测|裁定[:：]|改版|原为.{0,10}现为)')


def _check_comment_metadata(source, issues):
    """代码注释禁含 ⛔/日期/ADR/裁定等元信息（只写作用）。"""
    lines = source.replace('\r\n', '\n').split('\n')
    in_block = False
    for idx, raw in enumerate(lines):
        s = raw.strip()
        # 块注释 /* ... */ 的每行也算注释
        is_comment = s.startswith('//') or in_block or s.startswith('*')
        if '/*' in s:
            in_block = True
            is_comment = True
        if is_comment:
            m = COMMENT_META_RE.search(s)
            if m:
                issues.append(Issue(
                    "A.注释含元信息", Issue.SEVERITY_ERROR, idx + 1,
                    "注释禁含元信息（⛔/日期/ADR/裁定/改版），只写作用；约束归 wiki",
                    s[:100],
                ))
        if '*/' in s:
            in_block = False


def _check_method_doc_quality(doc, mth, label, issues):
    """检查方法 XML 注释的质量（summary/param/returns 规范）。
    label 用于报错前缀，如"公共方法"或"私有方法"。
    """
    # 2026-11-10（C16 业主裁定）：单条注释记录正文 ≤20 汉字
    _check_long_records(doc, mth, label, issues)
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
        # 单条注释记录 ≤20 汉字由 _check_long_records（C16/C18 分句 + 跨行合并口径）独占。
        # ⛔ 此处不再按「整段 summary 汉字数」重复判定：两套口径并存会产生假 warn。
        # 权威证据 = scripts/comment_scan.py long 的 merged_over。
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
            # 2026-11-09：缺 <param> 属「存量欠账」，与「public 未写 ///」同口径
            # （裁定 #3：不追溯、不设清零目标），由 WARN 降为 INFO。
            # 只有「写了但无信息 / 签名中不存在」才保持 WARN。
            issues.append(Issue(
                "A.注释规范", Issue.SEVERITY_INFO, mth.start_line,
                f"{label} {mth.name} 的参数 \"{pname}\" 缺少 <param> 注释"
                f"（存量欠账不追溯）",
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
        # 2026-11-09 新增判据：占位式 <param>xxx 参数。</param>，与删除口径闭环
        if re.fullmatch(rf'{re.escape(pname)}\s*参数\s*[。.]?', ptext, re.I):
            issues.append(Issue(
                "A.占位式XML", Issue.SEVERITY_INFO, mth.start_line,
                f"{label} {mth.name} 的参数 \"{pname}\" 为占位式注释"
                f"（\"{ptext}\"），应删除",
            ))
    # returns 检查
    if mth.return_type.strip() != 'void':
        rm = DOC_RETURNS_RE.search(doc)
        if not rm:
            issues.append(Issue(
                "A.注释规范", Issue.SEVERITY_INFO, mth.start_line,
                f"{label} {mth.name} 有返回值但缺少 <returns> 注释"
                f"（存量欠账不追溯）",
            ))
        else:
            mth.has_returns = True
            rtext = rm.group(1).strip()
            # 2026-11-09 新增判据：占位式 <returns>返回值。</returns>
            if re.fullmatch(r'(返回值|返回结果|返回)\s*[。.]?', rtext):
                issues.append(Issue(
                    "A.占位式XML", Issue.SEVERITY_INFO, mth.start_line,
                    f"{label} {mth.name} 的 <returns> 为占位式注释"
                    f"（\"{rtext}\"），应删除",
                ))
            elif rtext in ('返回结果', '结果', '返回值', ''):
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
        # 锁对象字段检查（readonly）
        _check_lock_fields(source, cls, issues)

        lock_orders = []
        for mth in cls['methods']:
            body = mth.body_text
            body_clean = remove_all_comments(strip_strings_and_chars(body))
            offset_line = mth.start_line

            _check_null_checks(body, body_clean, offset_line, mth, issues)
            _check_locks(body_clean, offset_line, mth, issues)
            _check_lock_layers(body_clean, offset_line, mth, issues, lock_orders)
            _check_redundant_assignment(body_clean, offset_line, mth, issues)
            _check_waits(body_clean, offset_line, mth, issues)
            _check_resource_management(body_clean, offset_line, mth, issues)
            _check_temp_vars(body, body_clean, offset_line, mth, issues)
            _check_singleton_locals(body_clean, offset_line, mth, issues)
        _check_lock_order(lock_orders, issues)


def _check_enums(cls, issues):
    for enum_info in cls['enums']:
        name = enum_info['name']
        line = enum_info['line']
        if name.endswith('Enum'):
            issues.append(Issue(
                "B.过度枚举", Issue.SEVERITY_WARN, line,
                f"枚举 {name} 带 Enum 后缀，C# 惯例不加此后缀",
            ))


# ⛔ 不把 lock / new 当重操作：
#   `get { lock(_x) { return _y; } }` 是跨线程共享字段的强制快照范式；
#   `get { return new List<T>(_x); }` 是「不返回内部可变引用」的推荐写法。
#   两者都属正解，判成违规会把项目范式刷成噪声。真在 lock 内做 IO 的，
#   会被下面的 File./ShowLog/有效行 > 5 兜住。
_HEAVY_ACCESSOR_RE = re.compile(
    r'\b(?:for|foreach|while|switch|try|catch|throw|await)\b'
    r'|\b(?:Thread|Task|File|Directory|StreamWriter|XmlSerializer)\.'
    r'|\b(?:ShowLog|Invoke|BeginInvoke|RunWorkerAsync)\s*\('
)


def _check_properties(cls, issues):
    """只报访问器真的含重操作的属性。

    ⛔ 旧口径 `len(body_text) > 20` 连 `get { return _x; }` 都判成「含逻辑」，
       全库刷出上千条噪声；「public set 能否改只读」需跨文件消费分析，
       单文件扫描器无能力判定，已移交人工/跨文件项，不再机械上报。
    """
    for prop in cls['properties']:
        clean = remove_all_comments(strip_strings_and_chars(prop.body_text or ''))
        effective = [l for l in clean.split('\n')
                     if l.strip() and l.strip() not in ('{', '}')]
        heavy = _HEAVY_ACCESSOR_RE.search(clean)
        if not heavy and len(effective) <= 5:
            continue
        why = heavy.group(0) if heavy else '访问器超过 5 行有效代码'
        issues.append(Issue(
            "B.过度属性", Issue.SEVERITY_INFO, prop.start_line,
            f"属性 {prop.name} 的访问器含重操作（{why}），确认是否应改为方法",
            clean.strip()[:100],
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


LOCK_BLOCK_RE = re.compile(r'lock\s*\(\s*([^)]+?)\s*\)\s*\{')


def _lock_spans(body_clean):
    """提取方法体内所有 lock 块（start/end 为字符位置，obj 为锁对象）。"""
    spans = []
    for m in LOCK_BLOCK_RE.finditer(body_clean):
        brace = body_clean.find('{', m.start())
        end = find_matching_brace(body_clean, brace)
        if end == -1:
            continue
        spans.append({'start': m.start(), 'end': end, 'obj': m.group(1).strip()})
    return spans


def _check_lock_fields(source, cls, issues):
    """锁对象字段必须 readonly（否则方法内重新赋值会使锁失效）。"""
    lines = source.split('\n')
    for f in cls.get('fields', []):
        if not re.search(r'(lock|sync|gate)', f.name, re.I) or f.is_readonly:
            continue
        if 0 < f.start_line <= len(lines) and 'new object' in lines[f.start_line - 1]:
            issues.append(Issue(
                "B.无意义锁", Issue.SEVERITY_WARN, f.start_line,
                f"字段 {f.name} 作为锁对象但未声明 readonly，重新赋值会使锁失效",
            ))


def _check_lock_layers(body_clean, offset_line, mth, issues, lock_orders):
    """多层锁：嵌套锁 / 锁字符串 / 锁局部对象 / 记录加锁顺序。"""
    spans = _lock_spans(body_clean)
    for inner in spans:
        for outer in spans:
            if outer['start'] < inner['start'] and inner['end'] < outer['end']:
                ln = offset_line + body_clean[:inner['start']].count('\n') + 1
                issues.append(Issue(
                    "B.多层锁", Issue.SEVERITY_WARN, ln,
                    f"方法 {mth.name}: 嵌套锁 lock({outer['obj']}) → lock({inner['obj']})，"
                    f"须确认全局加锁顺序一致，否则存在死锁风险",
                ))
                break
    locals_new = set(re.findall(
        r'(?:var|object|Object)\s+(\w+)\s*=\s*new\s+object\s*\(\s*\)', body_clean))
    seq = []
    for sp in spans:
        ln = offset_line + body_clean[:sp['start']].count('\n') + 1
        if sp['obj'].startswith('"'):
            issues.append(Issue(
                "B.多层锁", Issue.SEVERITY_WARN, ln,
                f"方法 {mth.name}: lock 字符串常量，字符串驻留可被其他代码共享导致死锁",
            ))
        if sp['obj'] in locals_new:
            issues.append(Issue(
                "B.多层锁", Issue.SEVERITY_WARN, ln,
                f"方法 {mth.name}: 对局部变量 {sp['obj']} 加锁，其他线程不可见，锁无效",
            ))
        if not any(x[0] == sp['obj'] for x in seq):
            seq.append((sp['obj'], ln))
    if len(seq) >= 2:
        lock_orders.append((mth.name, seq))


def _check_lock_order(lock_orders, issues):
    """跨方法锁顺序反转（a→b 与 b→a 并存）→ 经典死锁风险。"""
    for i in range(len(lock_orders)):
        for j in range(i + 1, len(lock_orders)):
            n1, s1 = lock_orders[i]
            n2, s2 = lock_orders[j]
            d1 = dict(s1)
            d2 = dict(s2)
            common = [o for o, _ in s1 if o in d2]
            if len(common) < 2:
                continue
            p1 = [o for o, _ in s1 if o in d2]
            p2 = [o for o, _ in s2 if o in d1]
            if p2 == list(reversed(p1)) and p1 != p2:
                issues.append(Issue(
                    "B.多层锁", Issue.SEVERITY_WARN, d2[p2[1]],
                    f"方法 {n1} 与 {n2} 的加锁顺序相反（{'→'.join(p1)} vs {'→'.join(p2)}），"
                    f"存在经典死锁风险",
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
            vname, pname = mvar.group(1), mvar.group(2)
            rest = '\n'.join(lines[i + 1:])
            # 豁免 ①：局部后续被重新赋值（可变量 / 钳制前快照 / 失败改写），不是纯透传
            if re.search(rf'\b{re.escape(vname)}\s*(?:=|\+\+|--|\+=|-=)', rest):
                continue
            # 豁免 ②：两变量交换（swap = start; start = end; end = swap;）
            nxt = '\n'.join(lines[i + 1:i + 4])
            if re.search(rf'\b{re.escape(pname)}\s*=\s*\w+\s*;', nxt) and \
               re.search(rf'\b\w+\s*=\s*{re.escape(vname)}\s*;', nxt):
                continue
            # 豁免 ③：参数后续被改写（钳制 / 归一化），局部是改写前快照，日志要对比两值
            if re.search(rf'\b{re.escape(pname)}\s*(?:=|\+\+|--|\+=|-=)[^=]', rest):
                continue
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


def _in_loop_body(body, pos):
    """判断 body[pos] 是否位于 while/for/foreach/do 循环体内。

    2026-10-26：standards/CodeSimplification §四「有意例外」条款 —— 周期性轮询节拍
    （如安全监控 MonitorLoop 按固定周期读 PLC）用 Thread.Sleep 是正确实现；
    此类场景无推送事件源，改用 Timer 会降级线程优先级。故循环体内的 Sleep 降为 INFO。
    """
    for m in re.finditer(r'\b(while|for|foreach|do)\b', body):
        i = body.find('{', m.end())
        if i < 0 or i > pos:
            continue
        depth = 0
        for j in range(i, len(body)):
            if body[j] == '{':
                depth += 1
            elif body[j] == '}':
                depth -= 1
                if depth == 0:
                    if i <= pos <= j:
                        return True
                    break
    return False


def _check_waits(body_clean, offset_line, mth, issues):
    # 判据豁免清单（2026-10-26）：standards/CodeSimplification §四「有意例外」条款落地。
    # 条目 = (文件路径子串, 方法名)；命中则该处的等待不报（须在报告中标注为有意例外）。
    WAIT_EXEMPT = (
        ("DeltaEtherCAT/DeltaMontionAxis.cs", "ServoOn"),
        ("DeltaEtherCAT/DeltaMontionAxis.cs", "ResetAlarm"),
    )
    patterns = [
        (r'Thread\.Sleep\s*\(', 'Thread.Sleep',
         '使用 Thread.Sleep 等待，不可靠且阻塞线程；异步操作用 await，'
         '条件等待用事件/信号量'),
        (r'\.Wait\(\)', '.Wait()',
         '阻塞等待 Task，可能死锁（尤其 UI 线程）；应使用 await'),
        # 2026-10-26 收窄：原判据 r'\.Result\b' 把**事件参数属性** e.Result / args.Result
        # 误判为阻塞等待（实测 9 处全为假阳性）。真正的阻塞写法是 Task/ValueTask 的
        # .Result 或 .GetAwaiter().GetResult()。
        (r'(?:Task|ValueTask)(?:<[^<>;]*>)?\s*\.\s*(?:Result|GetAwaiter\(\)\s*\.\s*GetResult\(\))',
         'Task.Result',
         '阻塞访问 Task 结果，可能死锁；应使用 await'),
        (r'\.GetAwaiter\(\)\s*\.\s*GetResult\(\)', 'GetAwaiter().GetResult()',
         '同步阻塞取 Task 结果，可能死锁；应使用 await'),
        (r'Task\.Delay\s*\(\s*0\s*\)', 'Task.Delay(0)',
         'Task.Delay(0) 无意义，直接执行即可'),
        (r'GC\.Collect\s*\(\s*\)', 'GC.Collect()',
         '手动调用 GC.Collect 干扰 GC 策略，性能极差，应移除'),
    ]
    for pattern, label, desc in patterns:
        for m in re.finditer(pattern, body_clean):
            ln = offset_line + body_clean[:m.start()].count('\n') + 1
            if any(fn in CURRENT_FILE and mn == mth.name for fn, mn in WAIT_EXEMPT):
                continue          # 判据豁免：有意例外（标准 §四），报告中标注
            sev = Issue.SEVERITY_WARN
            if label == 'Thread.Sleep' and _in_loop_body(body_clean, m.start()):
                sev = Issue.SEVERITY_INFO
                desc = ('Thread.Sleep 位于循环体内（周期轮询节拍）——'
                        '有意例外：此类场景无推送事件源，改用 Timer 会降级线程优先级；'
                        '若为直线等待请改用 await/事件/信号量')
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
        # 类型位不得是语句关键字：`return value == null;` 曾被误当成变量声明
        if re.match(r'^(?:' + '|'.join(sorted(_DECL_SKIP_FIRST)) + r')\b', s):
            continue
        mvar = re.match(
            r'(?:var|[\w<>\?\[\]]+)\s+(temp|tmp|data|result|value|val|item|obj)\s*=\s*(.+);',
            s, re.IGNORECASE,
        )
        if mvar:
            var_name = mvar.group(1)
            rhs = mvar.group(2).strip()
            rest = '\n'.join(lines[i + 1:])
            # 豁免 ①：后续被重新赋值（可变游标 / 钳制前快照），不是纯中转
            if re.search(rf'\b{re.escape(var_name)}\s*(?:=|\+\+|--|\+=|-=)', rest):
                continue
            # 豁免 ②：两变量交换（temp = start; start = end; end = temp;）不可内联
            if re.match(r'^\w+$', rhs):
                nxt = '\n'.join(lines[i + 1:i + 4])
                if re.search(rf'\b{re.escape(rhs)}\s*=\s*\w+\s*;', nxt) and \
                   re.search(rf'\b\w+\s*=\s*{re.escape(var_name)}\s*;', nxt):
                    continue
            # 检查这个变量在后续使用了几次
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


def _check_singleton_locals(body_clean, offset_line, mth, issues):
    """检测同名单例局部变量在方法内重复声明（C17）。"""
    lines = body_clean.split('\n')
    seen = {}
    for i, line in enumerate(lines):
        m = re.search(r'([\w\.]+)\s+(\w+)\s*=\s*([\w\.]+)\.Instance\s*;', line)
        if not m:
            continue
        key = (m.group(1), m.group(2), m.group(3))
        seen.setdefault(key, []).append(offset_line + i + 1)
    for (typ, var, owner), lns in seen.items():
        if len(lns) < 2:
            continue
        issues.append(Issue(
            "A.单例重复声明", Issue.SEVERITY_WARN, lns[1],
            f"方法 {mth.name}: {typ} {var} = {owner}.Instance 重复声明 {len(lns)} 次"
            f"（行 {', '.join(str(x) for x in lns)}），应合并为一处",
            f"{typ} {var} = {owner}.Instance;",
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
        _check_inline_candidates(methods, issues, source)

        # 死函数检测
        _check_dead_methods(methods, method_names, issues)

        # 同类指令平行入口检测
        _check_parallel_command_entries(methods, issues)


def _check_parallel_command_entries(methods, issues):
    """同一类中 ≥3 个同前缀、无参、同返回类型的公开方法视为平行指令入口。"""
    groups = {}
    for mth in methods:
        if mth.name == '#ctor' or mth.access != 'public':
            continue
        if mth.is_virtual_override or mth.params:
            continue
        m = re.match(r'^([A-Z][a-z])[A-Z]', mth.name)
        if not m:
            continue
        groups.setdefault((m.group(1), mth.return_type), []).append(mth)
    for (prefix, ret), items in groups.items():
        if len(items) < 3:
            continue
        names = "、".join(x.name for x in items)
        issues.append(Issue(
            "C.平行指令入口", Issue.SEVERITY_INFO, items[0].start_line,
            f"同类存在 {len(items)} 个 {prefix} 族平行公开指令方法（{names}），"
            f"建议合并为单一入口 + 枚举参数内部 switch 分派",
        ))


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


def _is_thin_wrapper(a, b):
    """a 是否只是调用 b 的薄包装。

    2026-10-26：standards/CodeSimplification ⑤「功能重叠合并」允许
    「public 保留薄包装」—— 一方方法体只是转发到另一方（可带 null 检查/日志）
    时不算功能重复，不再报重叠。真正的重复是「两边各写一份实现」。
    """
    clean = remove_all_comments(strip_strings_and_chars(a.body_text))
    kws = {'if', 'else', 'for', 'foreach', 'while', 'do', 'switch', 'case',
           'return', 'try', 'catch', 'finally', 'using', 'lock', 'new', 'throw',
           'nameof', 'typeof', 'checked', 'default', 'get', 'set'}
    calls = set()
    for m in re.finditer(r'\b([A-Za-z_]\w*)\s*(?:<[^>]+>)?\s*\(', clean):
        n = m.group(1)
        if n in kws or n == a.name:
            continue
        calls.add(n)
    return calls == {b.name}


def _check_overlapping_methods(methods, issues):
    # 按归一化名称聚类（同一类内 —— 调用方已按 cls 逐类传入）
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
                # 2026-10-29：**同名重载不参与功能重叠判定**——C# 重载本就允许
                # 同一语义的不同参数版本（如 GetXmlStrValue 取属性/取元素、
                # CreateTable 带/不带 IsExistTable 守卫、AddFrame 两版薄包装）。
                # 真正的重复实现由同名方法体内的 token 相似度判定；
                # 同名重复声明另由 check_duplicate_members（ERROR）拦截。
                if a.name == b.name:
                    continue
                # 排除薄包装形态（标准允许的 public 转发）
                if _is_thin_wrapper(a, b) or _is_thin_wrapper(b, a):
                    continue
                tokens_a = set(_body_tokens(a.body_text))
                tokens_b = set(_body_tokens(b.body_text))
                sim = _jaccard(tokens_a, tokens_b)
                # 2026-10-26：阈值对齐 standards/CodeSimplification ⑤「功能重叠合并」
                # 的判定口径「70% 以上方法体相同」——原 0.5 低于标准，会把
                # 「语义不同的重载」（如 CreateTable 的两版列长/守卫不同）误判为重复。
                if sim >= 0.7:
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

    # ⛔ 已废止「名称暗示旧版本残留」启发式判据：
    #   仅凭方法名含 Backup/Legacy/Old 就报「确认无调用后删除」，
    #   会把有真实消费方的活方法（ConfigSelfHeal.Backup 有 2 处调用、
    #   WeldHeadSlaveDevice.DescribeTemperatureThreshold 有 2 处调用）误判为死代码。
    #   死成员一律由 C.疑似死函数（真实零调用）判定，且按顶层裁定 2 只报不删。


def _check_inline_candidates(methods, issues, source):
    # 判断性/校验性函数名即使短也保留（表达独立业务概念）
    predicate_prefixes = ('Is', 'Can', 'Has', 'Should', 'Validate',
                          'Check', 'Ensure', 'Need')
    # 台账 B-6 / B-8 已逐条裁定保留的语义类别：Log 包装(Tag 载体)、快捷区指令分发、
    # 解析校验、卫语句、流程步骤与状态机、初始化序列与几何、事件抛出。
    # 这些短方法表达独立概念，内联会把守卫/语义散到调用方，不再重复上报。
    inline_keep_prefixes = (
        'Log', 'Raise', 'DoTa', 'DoLa', 'DoPreWork', 'DoStopping',
        'Parse', 'Read', 'Load', 'GetElement', 'Normalize', 'ToHome',
        'Handle', 'Process', 'Clear', 'Add', 'After', 'Subscribe',
        'Wait', 'Start', 'Update', 'Format', 'Play', 'Save', 'Reset',
        'Project', 'OnConnected', 'OnDisconnected',
    )
    code = remove_preprocessor_directives(remove_all_comments(strip_strings_and_chars(source)))
    for mth in methods:
        if mth.name == '#ctor':
            continue
        if mth.access != 'private':
            continue
        if mth.is_virtual_override:
            continue
        if any(mth.name.startswith(p) for p in predicate_prefixes):
            continue
        if any(mth.name.startswith(p) for p in inline_keep_prefixes):
            continue
        # 仅 1 个调用表达式（不是仅 1 个调用者方法）
        call_count = len(re.findall(rf'\b{re.escape(mth.name)}\s*\(', code)) - 1
        if call_count != 1:
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

        caller_name = mth.callers[0] if mth.callers else "调用方"
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

FONT_DEFAULT_FAMILY = "Microsoft YaHei UI"
FONT_DECL_RE = re.compile(r'new\s+(?:System\.Drawing\.)?Font\s*\(\s*"([^"]+)"')


def check_font_family(source, issues):
    """A.字体规范：显示字体必须是项目默认 Microsoft YaHei UI（2026-10-30 业主裁定）。

    判定只看 `new Font("族名", ...)` 的族名；字号/样式不限。注释里的示例不报。
    """
    for m in FONT_DECL_RE.finditer(source):
        family = m.group(1)
        if family == FONT_DEFAULT_FAMILY:
            continue
        line_start = source.rfind("\n", 0, m.start()) + 1
        if "//" in source[line_start:m.start()]:
            continue
        issues.append(Issue(
            "A.字体规范", Issue.SEVERITY_WARN, line_of(source, m.start()),
            '字体 "%s" 非项目默认 "%s"' % (family, FONT_DEFAULT_FAMILY),
        ))


REFRESH_SWITCH_ON_RE = re.compile(
    r'this\.(\w*[Rr]efresh\w*)\.Checked\s*=\s*true\s*;')


def check_refresh_default(source, issues):
    """B.刷新默认开：自动刷新开关必须默认关闭（硬件就绪后才由门禁解冻）。"""
    for m in REFRESH_SWITCH_ON_RE.finditer(source):
        issues.append(Issue(
            "B.刷新默认开", Issue.SEVERITY_WARN, line_of(source, m.start()),
            '自动刷新开关 %s 默认 Checked = true，应改为 false（默认关闭，就绪后才可开）' % m.group(1),
        ))


def check_init_dependency(source, issues):
    """C.设备初始化分层：初始化链必须按依赖层级驱动，父级未就绪时子级不发起连接。

    只在定义了 InitializeMachineTick 的整机管控类上判定，避免误报子设备工作流。
    """
    # 只认方法定义；DeviceStatusWork 每拍驱动里的调用点不应触发本判据
    m = re.search(r'\b(?:public|private|protected|internal)\s+void\s+InitializeMachineTick\s*\(', source)
    if not m:
        return
    head = m.start()
    body = source[head:]
    # ① 父级门禁：必须存在按父节点结果判定并记「跳过」的段落
    if 'ParentKey' not in body:
        issues.append(Issue(
            "C.设备初始化分层", Issue.SEVERITY_WARN, line_of(source, head),
            "初始化驱动未见父级门禁（ParentKey），疑似平级硬试"),
        )
        return
    if 'DeviceInitOutcome.Skipped' not in body:
        issues.append(Issue(
            "C.设备初始化分层", Issue.SEVERITY_WARN, line_of(source, head),
            "父级门禁未落「跳过」三态（应先记 Skipped 再推进，不发起连接）"),
        )
        return
    # ② 跳过分支不得先发起连接：Skipped 记录必须出现在首次 node.Start 之前
    i_skip = body.find('DeviceInitOutcome.Skipped')
    i_start = body.find('node.Start')
    if 0 <= i_start < i_skip:
        issues.append(Issue(
            "C.设备初始化分层", Issue.SEVERITY_WARN, line_of(source, head + i_start),
            "父级门禁之前已发起连接（node.Start），子级会白试一次"),
        )


def check_init_log(source, issues):
    """D.初始化日志：模组口径 + 阶段分离 + 汇总收尾唯一。"""
    for m in re.finditer(r'"\s*子设备', source):
        issues.append(Issue(
            "D.初始化日志", Issue.SEVERITY_WARN, line_of(source, m.start()),
            "日志/文案仍用「子设备」，应统一为「模组」（本设备下的模组，非独立设备）",
        ))

    m = re.search(r'private void FinishInitialization\s*\(', source)
    if not m:
        return
    body = source[m.start():]
    nxt = re.search(r'\n        (private|public|protected|internal) ', body[10:])
    if nxt:
        body = body[:10 + nxt.start()]
    i_summary = body.find('初始化汇总')
    if i_summary < 0:
        issues.append(Issue(
            "D.初始化日志", Issue.SEVERITY_WARN, line_of(source, m.start()),
            "整机初始化缺少唯一收尾行「初始化汇总 成功 X 失败 Y 跳过 Z」",
        ))
        return
    i_gate = body.find('LogAxisGateReport')
    if 0 <= i_summary < i_gate:
        issues.append(Issue(
            "D.初始化日志", Issue.SEVERITY_WARN, line_of(source, m.start() + i_summary),
            "轴门禁报告出现在汇总之后，汇总不再收尾（应前移到汇总之前）",
        ))
    tail = body[i_summary:]
    tail = tail[tail.find('\n') + 1:]
    if re.search(r'\bLog\s*\(', tail):
        issues.append(Issue(
            "D.初始化日志", Issue.SEVERITY_WARN, line_of(source, m.start() + i_summary),
            "「初始化汇总」之后仍有日志，收尾不唯一",
        ))

    # 密度回潮：Info 行里不得出现排查建议/未确证结论/绝对路径
    dense = re.compile(r'"(?:[^"\\]|\\.)*(?:常见于|未确证|[A-Za-z]:\\\\)')
    for mm in dense.finditer(source):
        line_text = line_of(source, mm.start())
        if 'MessageLevel.Debug' in source[mm.start():mm.start() + 400]:
            continue
        issues.append(Issue(
            "D.初始化日志", Issue.SEVERITY_WARN, line_text,
            "日志文案含排查建议/未确证结论/绝对路径，应删除或降 Debug（极简密度判据 6.3）",
        ))


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
    global CURRENT_FILE
    CURRENT_FILE = filepath.replace('\\', '/')
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        source = f.read()

    filename = filepath.lower()
    issues = []

    # 字体规范对 Designer.cs 同样生效（字体恰好全部由设计器写入）；其余项不处理
    check_font_family(source, issues)
    check_refresh_default(source, issues)
    if filename.endswith('.designer.cs'):
        return issues

    classes = parse_file(source)

    if not classes:
        issues.append(Issue(
            "系统", Issue.SEVERITY_INFO, 1,
            "未在文件中找到 class/struct/interface 定义",
        ))
        return issues

    check_regions_and_order(source, classes, issues)
    check_duplicate_members(source, classes, issues)
    check_dispose_pattern(source, issues)
    check_doc_comments(source, classes, issues)
    _check_var_multiline_comments(source, issues)
    _check_comment_metadata(source, issues)
    check_logic_issues(source, classes, issues)
    check_function_simplification(source, classes, issues)
    check_init_dependency(source, issues)
    check_init_log(source, issues)
    _check_file_level_enums(source, classes, issues)

    # 存量注释欠账默认不进清单（顶层裁定 3），--verbose 可查全量
    if not INCLUDE_LEGACY:
        issues = [x for x in issues
                  if not (x.severity == 'info' and x.category == 'A.注释规范')]

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
    # 控制台按 GBK 编码时，含 U+2212 等非 GBK 字符的扫描消息会触发
    # UnicodeEncodeError，导致整份扫描结果丢失（文件级假阴性）。
    # 输出统一转 UTF-8，并对不可映射字符降级替换。
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            try:
                _stream.reconfigure(encoding='utf-8', errors='replace')
            except (ValueError, OSError):
                pass

    parser = argparse.ArgumentParser(
        description='.NET 4.8 / C# 7.3 单文件冗余代码扫描器')
    parser.add_argument('file', help='要扫描的 .cs 文件路径')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式输出')
    parser.add_argument('--verbose', action='store_true',
                        help='显示所有项（含提示级别）')
    args = parser.parse_args()

    global INCLUDE_LEGACY
    if args.verbose:
        INCLUDE_LEGACY = True

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
