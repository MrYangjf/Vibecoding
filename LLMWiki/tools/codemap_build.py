#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codemap_build.py —— 代码地图生成器（repomap 引擎 + 自研 C# 调用边抽取）

产出三份 wiki 页（落在 `wiki/architecture/`），供 Phase 0 定位与 Phase 2.5 影响面追踪：

  1. `CodeMap.md`            —— 总览：模块骨架 + 入口类 + 主干依赖 + 定位陷阱（**人工判断层**）
  2. `CodeMap-Symbols.md`    —— L2 签名层：逐类 → 文件:行 → 方法签名（**机器生成**）
  3. `CodeMap-Relations.md`  —— L3 关系层：调用边 + 继承边 + 反向被调清单（**机器生成**）

设计要点（2026-11-18）：
  · **引擎用官方 `coderepomap`**（PyPI 包名 coderepomap，源码 github.com/sputnicyoji/coderepomap）：
    复用其 tree-sitter C# 解析（类型 / 方法 / 签名 / 命名空间 / 行号）+ PageRank 排序，
    ⛔ 不自造解析器（避免与官方语义漂移）。
  · **调用边自研补齐**：官方 C# 解析器只发 `inherits` / `implements` 引用（实测 114 条、零方法调用），
    故本脚本用 tree-sitter 直接抽 `invocation_expression`，把「文件 → 被调方法」解析为
    「被调符号 → 调用方」反向清单 —— 这是 Phase 2.5 影响面追踪的加速器（⛔ 不替代 Grep，见 KR-009）。
  · **路径全部由 `__file__` 推导**，禁硬编码绝对路径（机器迁移后写死路径 ⇒ 扫描器报「0 文件」却看着健康）。
  · **幂等**：同一份源码重复跑，输出逐字节一致（时间戳字段除外）。
  · **只读源码**：不写 AdaWeldSystem/ 任何文件。

用法：
  python tools/codemap_build.py             # 生成三份页面
  python tools/codemap_build.py --check     # 只校验产物是否与当前源码同步（漂移检查）
  python tools/codemap_build.py --stats     # 只打印统计（不写盘）
"""
import os
import re
import sys
import json
import hashlib
import argparse

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LLMWIKI = os.path.dirname(TOOLS_DIR)                 # LLMWiki/
VICODING = os.path.dirname(LLMWIKI)                  # Vicoding管理平台/
WORKSPACE = os.path.dirname(VICODING)                # workbudddy/
CODE_ROOT = os.path.join(WORKSPACE, "AdaWeldSystem")
ARCH_DIR = os.path.join(LLMWIKI, "wiki", "architecture")
# 命名空间级人工判断层（功能 / 模块归属 / 约束 ADR）—— 机器给不出的经验判断，
# 存外部数据文件而非代码内常量，便于非程序员维护；⛔ 禁手改生成页。
NS_META_FILE = os.path.join(TOOLS_DIR, "data", "namespace_meta.json")

OUT_OVERVIEW = os.path.join(ARCH_DIR, "CodeMap.md")
OUT_SYMBOLS = os.path.join(ARCH_DIR, "CodeMap-Symbols.md")
OUT_RELATIONS = os.path.join(ARCH_DIR, "CodeMap-Relations.md")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

EXCLUDE_DIRS = {"bin", "obj", "3rdDepend", ".vs", ".git"}

# 模块 → 分类（与 repomap categories 一致；用于总览分组）
CATEGORY_RULES = [
    ("Core", ["MainDeviceControl", "Comm", "FileOperate"]),
    ("UI", ["UIDesign"]),
    ("Motion", ["MotionControl", "LineLaserCam"]),
    ("Vision", ["EmguALG", "MonitorCam"]),
    ("Data", ["SQLiteDBControl", "PCLOperate", "ProductFileControl"]),
]

# 人工判断：定位陷阱（机器给不出的经验判断，保留在总览页）
LOCATION_TRAPS = [
    ("`LineLaserSeamResult` Grep 零命中 ≠ 缺失",
     "它是 `struct`（`LineLaserCam/ILineLaser/LineLaserEventArgs.cs`）",
     "Grep `class\\s+X` 漏 struct；先分 class / struct / interface"),
    ("`MontionConfigForm` 不存在",
     "轴配置 UI 是 `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs`（UserControl）",
     "找 UI 扫 `UIDesign/` 全部子目录"),
    ("「光丝对中未实现」是误判",
     "有两套：在用套出像素、另一套出 mm 无消费者",
     "区分「无代码」与「有代码未接线」"),
    ("workflow 的 UI 在 `MainDeviceControl` 是误判",
     "业务在 `MainDeviceControl/DeviceWorkflow/`，UI 在 `UIDesign/TabPage/`",
     "业务逻辑与 UI 分目录"),
    ("振镜走运控轴是误判",
     "振镜走从站 OD（0x7010），ADR-030 已裁定",
     "硬件归属先查 ADR"),
    ("`MotorState?` 违反 ADR-001 是误判",
     "`MotorState` 是 struct，`?` = Nullable，C# 7.3 合法",
     "判可空前先分 class / struct"),
    ("`ProductFileControl/Records/*` 命名空间违规是误判",
     "ADR-005 §3 例外二：该目录扁平",
     "查命名空间先读 ADR-005 例外表"),
    ("UI 直调 `MoveTo`/`HomeAxis` 违规是误判",
     "`MontionManager.Instance.MoveTo` 等正是规定路径",
     "区分 `axis.AbsMove()` 与 Manager 门面"),
]

# 人工判断：功能域 → 入口文件（模块骨架的业务语义标注）
DOMAIN_HINTS = {
    "MainDeviceControl": "整机编排：设备初始化 / 状态机 / 五个模组 workflow",
    "Comm": "通讯：RSI 唯一机器人通道 + 日志双通道",
    "MotionControl": "运控：Y / TA 两轴 + 焊接头从站 OD（0x7000 / 0x6020 / 0x7010）",
    "WeldParamControl": "焊接工艺参数与自适应：焊参真相源 + 算法规格",
    "EmguALG": "视觉算法五层：EmguALG.Core / RealtimeMonitor / LineLaserContour",
    "LineLaserCam": "线激光相机：Manager 唯一口 + 英莱/虚拟实现",
    "MonitorCam": "监控相机：Manager 唯一口 + 海康/虚拟实现",
    "UIDesign": "UI 页面与权限：主界面 / 工艺 / 系统设置 / 追溯",
    "FileOperate": "配置读写：INI + XML + 自愈 + 迁移 + 备份",
    "SQLiteDBControl": "SQLite 持久层",
    "PCLOperate": "PLC 交互",
    "ProductFileControl": "产品记录与追溯 Schema",
    "Program.cs": "程序入口（Main）",
}


def sha256_of_tree():
    """源码树指纹（用于 --check 漂移判定）：路径 + 内容哈希，排序后取总哈希。"""
    h = hashlib.sha256()
    for path in sorted(iter_cs_files()):
        rel = os.path.relpath(path, CODE_ROOT).replace("\\", "/")
        with open(path, "rb") as fh:
            h.update(rel.encode("utf-8"))
            h.update(hashlib.sha256(fh.read()).digest())
    return h.hexdigest()


def iter_cs_files():
    for root, dirs, files in os.walk(CODE_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith(".cs") and not f.endswith(".Designer.cs"):
                yield os.path.join(root, f)


def load_engine():
    """加载官方 coderepomap 引擎 + tree-sitter C# 语法。缺依赖时给出可执行的修复指引。"""
    try:
        from coderepomap.core.generator import RepoMapGenerator
        import tree_sitter_c_sharp as ts_cs
        from tree_sitter import Language, Parser
    except ImportError as exc:
        sys.stderr.write(
            "[codemap_build] 缺少依赖：%s\n"
            "  修复（PyPI 未发布 coderepomap，须从源码装）：\n"
            "    pip install --user \"coderepomap[csharp]\"\n"
            "  若镜像源无此包：\n"
            "    git clone https://github.com/sputnicyoji/coderepomap.git\n"
            "    cd coderepomap && pip install --user \".[csharp]\"\n" % exc)
        return None
    return RepoMapGenerator, Language(ts_cs.language()), Parser


def build_symbol_table():
    """用官方引擎解析出符号表：返回 {module: {class_name: {...}}}。"""
    RepoMapGenerator, _lang, _parser = load_engine()
    if RepoMapGenerator is None:
        return None

    cfg = {
        "project_name": "AdaWeldSystem",
        "lang": "csharp",
        "source": {"root_path": "AdaWeldSystem", "exclude_patterns": []},
        "tokens": {"l1_skeleton": 3000, "l2_signatures": 8000,
                   "l3_relations": 8000, "encoding": "cl100k_base"},
        "pagerank": {"alpha": 0.85, "max_iter": 100},
        "output": {"directory": ".repomap/output"},
        "importance_boost": {"patterns": [], "priority_modules": []},
        "categories": {"Other": {"patterns": []}},
    }
    gen = RepoMapGenerator(config=cfg, project_root=__import__("pathlib").Path(WORKSPACE))
    files = gen.scan()
    gen.parse(files, verbose=False)
    gen.build()

    modules = {}
    for sym in gen.symbols:
        if sym.kind != "class":
            continue
        module = sym.file.split("/")[0] if sym.file else "Unknown"
        modules.setdefault(module, {})[sym.name] = {
            "signature": sym.signature,
            "file": sym.file,
            "line": sym.line,
            "namespace": sym.container,
            "fqn": sym.fqn,
        }
    # partial class 的位置修正：官方解析可能命中 `.Designer.cs`（自动生成）
    # ⇒ 同一类型名下若有非 Designer 文件，改用它（实现文件才是定位入口）。
    for _mod, _classes in modules.items():
        for _cname, _info in _classes.items():
            if _info["file"].endswith(".Designer.cs"):
                alt = None
                for _s in gen.symbols:
                    if (_s.kind == "class" and _s.name == _cname
                            and _s.file and not _s.file.endswith(".Designer.cs")):
                        if alt is None or _s.line < alt[1]:
                            alt = (_s.file, _s.line)
                if alt:
                    _info["file"], _info["line"] = alt
    methods = {}
    for sym in gen.symbols:
        if sym.kind != "method" or not sym.parent:
            continue
        methods.setdefault(sym.parent, []).append({
            "name": sym.name,
            "signature": sym.signature,
            "file": sym.file,
            "line": sym.line,
            "namespace": sym.container,
        })
    # 合并自研全量成员（补 official public-only 缺口）：官方条目按 (name,file,line) 去重后并入
    member_index = collect_members()
    for cname, members in member_index.items():
        bucket = methods.setdefault(cname, [])
        seen = {(m["name"], m["file"], m["line"]) for m in bucket}
        for mem in members:
            key = (mem["name"], mem["file"], mem["line"])
            if key in seen:
                continue
            seen.add(key)
            bucket.append({
                "name": mem["name"],
                "signature": mem["signature"],
                "file": mem["file"],
                "line": mem["line"],
                "namespace": "",
                "kind": mem["kind"],
            })
        # 官方条目的 kind 缺省为 method
        for m in bucket:
            m.setdefault("kind", "method")
    # 继承 / 实现边：官方引擎把 base_class / interfaces 放在 Symbol.lang_meta，
    # 而 references[].to_id 对未解析目标为空串 ⇒ 从 lang_meta 取才拿得到真实被继承类型名。
    inherits = []
    for sym in gen.symbols:
        if sym.kind not in ("class", "struct", "interface", "enum"):
            continue
        meta = getattr(sym, "lang_meta", {}) or {}
        base = (meta.get("base_class") or "").strip()
        if base:
            inherits.append((sym.name, base, "inherits"))
        for iface in (meta.get("interfaces") or []):
            ifaces = (iface or "").strip()
            if ifaces:
                inherits.append((sym.name, ifaces, "implements"))
    return {"modules": modules, "methods": methods, "inherits": inherits,
            "symbols": gen.symbols, "ranker": gen.ranker, "members": member_index}


def build_call_edges(symbols, member_index=None):
    """自研调用边抽取：tree-sitter 抽 invocation_expression → 项目内调用边。

    口径（关键设计，2026-11-18）：
      · **高置信边** = 成员调用且**接收者是项目内类型**（如 `GlobalCommData.ShowLog(...)`）
        ⇒ 被调方法确定属于该项目，改该类型必然影响此处。
      · **低置信边** = 纯标识符调用（`Log(...)` / `SetWeldStatus(...)`）且**同名方法存在于项目内**
        ⇒ 命中真实影响面，但同名不同类会误连（故标「低」）。
      · 由此排除 BCL 噪声（`string.Format` / `Path.Combine` / `List.Add` 等）——
        按**方法名**全收会把它们全收进来（实测 4454 条里绝大多数是这类无效边）。

    返回 (high_edges, low_edges)：元素均为 (caller_file, callee_key, line)。
      · high 的 callee_key = 被调**类型名**（聚合到类型级，影响面粒度正确）
      · low  的 callee_key = 被调**方法名**（类型未知，标低置信）
    """
    _R, lang, parser_cls = load_engine()
    if parser_cls is None:
        return [], []

    parser = parser_cls(lang)
    # 项目内类型名集合（判定 receiver 是否为项目类型）
    type_names = set()
    for sym in symbols:
        if sym.kind in ("class", "struct", "interface", "enum"):
            type_names.add(sym.name)
    # 项目内方法名集合（判定纯标识符调用是否命中项目方法）
    method_names = set()
    if member_index:
        for members in member_index.values():
            for mem in members:
                if mem["kind"] in ("method", "ctor"):
                    method_names.add(mem["name"])
    else:
        for sym in symbols:
            if sym.kind == "method":
                method_names.add(sym.name)

    high, low = [], []
    for path in iter_cs_files():
        try:
            src = open(path, "rb").read()
        except OSError:
            continue
        rel = os.path.relpath(path, CODE_ROOT).replace("\\", "/")
        try:
            tree = parser.parse(src)
        except Exception:
            continue
        stack = [tree.root_node]
        while stack:
            node = stack.pop()
            if node.type == "invocation_expression":
                fn = node.child_by_field_name("function")
                if fn is not None and fn.type == "member_access_expression":
                    nm = fn.child_by_field_name("name")
                    recv = fn.child_by_field_name("expression")
                    if nm is not None and recv is not None:
                        method = src[nm.start_byte:nm.end_byte].decode("utf-8", "replace")
                        recv_txt = src[recv.start_byte:recv.end_byte].decode("utf-8", "replace").strip()
                        # receiver 形如 `GlobalCommData` 或 `this.xxx`；只取最后一段标识符
                        m = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", recv_txt)
                        if m and m.group(1) in type_names:
                            high.append((rel, m.group(1), node.start_point[0] + 1))
                elif fn is not None and fn.type == "identifier":
                    callee = src[fn.start_byte:fn.end_byte].decode("utf-8", "replace")
                    if callee in method_names and callee not in type_names:
                        low.append((rel, callee, node.start_point[0] + 1))
            stack.extend(node.children)
    return high, low


def categorize(module):
    for cat, mods in CATEGORY_RULES:
        if module in mods:
            return cat
    return "Other"


def module_of(rel_file):
    return rel_file.split("/")[0] if "/" in rel_file else rel_file


def render_symbols(table):
    """L2 签名层：逐模块 → 逐类 → 文件:行 → 方法签名。"""
    methods = table["methods"]
    modules = table["modules"]
    out = []
    out.append("---")
    out.append("title: CodeMap-Symbols — 代码地图·符号签名层（机器生成）")
    out.append("date: 2026-11-18")
    out.append("updated: 2026-11-18")
    out.append("tags: [代码地图, 符号索引, 机器生成]")
    out.append("status: accepted")
    out.append("---")
    out.append("")
    out.append("# CodeMap-Symbols — 代码地图·符号签名层")
    out.append("")
    out.append("> **一句话**：逐类 → `文件:行` → 方法签名，供 Phase 0 定位与 Step 0.7 精读用；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。")
    out.append("> **生成方式**：`coderepomap` 官方 C# 解析（tree-sitter）+ 本仓库路径约定；**含** `文件:行`，可直接跳读。")
    out.append("> **配套**：总览与功能域判断见 [[architecture/CodeMap]]；调用/继承关系见 [[architecture/CodeMap-Relations]]。")
    out.append("")

    total_classes = sum(len(v) for v in modules.values())
    total_methods = sum(len(v) for v in methods.values())
    out.append("## 统计")
    out.append("")
    out.append("| 项 | 值 |")
    out.append("|---|---|")
    out.append("| 命名空间（模块）数 | %d |" % len(modules))
    out.append("| 类型数 | %d |" % total_classes)
    out.append("| 方法数 | %d |" % total_methods)
    out.append("")

    for mod in sorted(modules, key=lambda m: -len(modules[m])):
        classes = modules[mod]
        out.append("## %s" % mod)
        out.append("")
        if mod in DOMAIN_HINTS:
            out.append("> %s" % DOMAIN_HINTS[mod])
            out.append("")
        for cname in sorted(classes):
            info = classes[cname]
            out.append("### %s" % info["signature"])
            out.append("")
            out.append("- 位置：`%s:%d`" % (info["file"], info["line"]))
            out.append("- 命名空间：`%s`" % info["namespace"])
            ms = methods.get(cname, [])
            if ms:
                by_kind = {}
                for m in ms:
                    by_kind.setdefault(m.get("kind", "method"), []).append(m)
                label = {"method": "方法", "ctor": "构造", "property": "属性",
                         "field": "字段"}
                for kind in ("method", "ctor", "property", "field"):
                    items = by_kind.get(kind)
                    if not items:
                        continue
                    out.append("- %s（%d）：" % (label.get(kind, kind), len(items)))
                    for m in sorted(items, key=lambda x: x["line"] or 0):
                        out.append("  - `%s` — `%s:%d`" % (
                            m["signature"], m["file"], m["line"]))
            else:
                out.append("- 成员：（无）")
            out.append("")
    return "\n".join(out) + "\n"


def render_relations(table, high, low):
    """L3 关系层：**被调类型** → 调用方清单（类型级影响面）+ 继承边。

    聚合到**类型**而非方法：改一个类（加字段、改签名）影响的是所有引用该类型的调用点，
    类型级清单正是 Phase 2.5 要的粒度；方法级过细会撑爆页面且噪声大。
    """
    inherits = table["inherits"]

    # 反向清单：被调类型 → {调用方文件: [行号]}
    reverse = {}
    for caller, callee_type, line in high:
        reverse.setdefault(callee_type, {}).setdefault(caller, []).append(line)
    # 低置信：被调方法名 → {调用方文件: [行号]}
    low_rev = {}
    for caller, callee_method, line in low:
        low_rev.setdefault(callee_method, {}).setdefault(caller, []).append(line)

    out = []
    out.append("---")
    out.append("title: CodeMap-Relations — 代码地图·关系层（机器生成）")
    out.append("date: 2026-11-18")
    out.append("updated: 2026-11-18")
    out.append("tags: [代码地图, 依赖关系, 影响面, 机器生成]")
    out.append("status: accepted")
    out.append("---")
    out.append("")
    out.append("# CodeMap-Relations — 代码地图·关系层")
    out.append("")
    out.append("> **一句话**：被调**类型** → 调用方文件清单（影响面追踪加速器）+ 继承边；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。")
    out.append("> **⚠️ 边界**：调用边按**接收者类型名**匹配项目内类型（高置信）+ 纯标识符调用且同名类型存在（低置信）；**同名不同类型会误连** ⇒ **结论仍以 Step 0.7 / 2.5 的 Grep 为准**（见 [[rules/KR-009-Grep-Default]]），本页只用于**缩小搜索范围**。")
    out.append("> **⚠️ 官方 L3 的坑**：coderepomap 官方 C# 解析器只发 `inherits`/`implements`（零方法调用点），故调用边由本仓库自研补齐 —— 见 [[lessons/RepomapCSharpCallEdgeGap]]。")
    out.append("> **配套**：类 → `文件:行` 见 [[architecture/CodeMap-Symbols]]；模块骨架见 [[architecture/CodeMap]]。")
    out.append("")

    out.append("## 统计")
    out.append("")
    out.append("| 项 | 值 |")
    out.append("|---|---|")
    out.append("| 高置信调用边（receiver 是项目类型） | %d |" % len(high))
    out.append("| 低置信调用边（纯标识符 + 同名类型） | %d |" % len(low))
    out.append("| 被引用类型数 | %d |" % len(reverse))
    out.append("| 继承 / 实现边 | %d |" % len(inherits))
    out.append("")

    out.append("## 一、被引用类型 → 调用方（类型级影响面 · 高置信）")
    out.append("")
    out.append("> **怎么用**：改某类型前，先在此查「谁引用它」→ 得到候选文件 → 再用 Grep 确认（Step 2.5）。")
    out.append("> 高置信 = 接收者就是该类型实例（`X.Method(...)`），改该类型必影响此处。")
    out.append("")
    for callee in sorted(reverse, key=lambda k: (-len(reverse[k]), k)):
        callers = reverse[callee]
        total = sum(len(v) for v in callers.values())
        out.append("### %s（%d 处调用 / %d 个调用方文件）" % (callee, total, len(callers)))
        out.append("")
        for caller in sorted(callers):
            lines = sorted(callers[caller])
            out.append("- `%s` — 行 %s" % (
                caller, "、".join(str(x) for x in lines)))
        out.append("")

    out.append("## 二、被调方法 → 调用方（方法级影响面 · 低置信）")
    out.append("")
    out.append("> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。")
    out.append("> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认。")
    out.append("")
    for callee in sorted(low_rev, key=lambda k: (-sum(len(v) for v in low_rev[k].values()), k)):
        callers = low_rev[callee]
        total = sum(len(v) for v in callers.values())
        out.append("### %s（%d 处调用 / %d 个调用方文件）" % (callee, total, len(callers)))
        out.append("")
        for caller in sorted(callers):
            lines = sorted(callers[caller])
            out.append("- `%s` — 行 %s" % (
                caller, "、".join(str(x) for x in lines)))
        out.append("")

    out.append("## 三、继承 / 实现边")
    out.append("")
    for frm, to, kind in sorted(inherits):
        if to in ("IDisposable", "EventArgs", "UserControl", "Window", "Attribute",
                  "INotifyPropertyChanged"):
            continue
        out.append("- `%s` → `%s`（%s）" % (frm, to, kind or "关系"))
    out.append("")
    out.append("## 相关页面")
    out.append("")
    out.append("- [[architecture/CodeMap]]")
    out.append("- [[architecture/CodeMap-Symbols]]")
    out.append("- [[rules/KR-009-Grep-Default]]")
    return "\n".join(out) + "\n"


def render_overview(table, high, low):
    """总览页：机器骨架（模块 → 类数 → 代表类型）+ 人工判断层（功能域提示 + 定位陷阱）。"""
    modules = table["modules"]
    methods = table["methods"]

    out = []
    out.append("---")
    out.append("title: CodeMap — 代码地图总览（模块骨架 + 定位陷阱）")
    out.append("date: 2026-11-18")
    out.append("updated: 2026-11-18")
    out.append("tags: [代码地图, 索引, 架构, Phase0, 代码记忆]")
    out.append("status: accepted")
    out.append("---")
    out.append("")
    out.append("# CodeMap — 代码地图总览")
    out.append("")
    out.append("> **一句话**：一页看完代码骨架（模块 → 类 → 入口）+ 定位陷阱；⛔ 逐类签名见 [[architecture/CodeMap-Symbols-MotionControl]] 等分片，⛔ 依赖关系见 [[architecture/CodeMap-Relations]]。")
    out.append("> **使用纪律（强制）**：Phase 0 先读本页定位，**命中即直接读对应代码块**（Step 0.7），⛔ **不得一上来全项目 Grep**。详见 [[rules/KR-003-No-Skipping-Query]] 与 [[rules/KR-009-Grep-Default]]。")
    out.append("> **裁决顺序**：原档 > 架构页 > 源码注释；本表是导航层，不覆盖 ADR 结论。")
    out.append("> **生成方式**：模块骨架与计数由 `tools/codemap_build.py`（官方 `coderepomap` 引擎）产出；「定位陷阱」为人工经验判断，脚本原样保留。")
    out.append("")

    out.append("## 章节导航")
    out.append("")
    out.append("- [统计](#统计)")
    out.append("- [一、模块骨架](#一模块骨架)")
    out.append("- [二、模块 → 符号分片](#二模块--符号分片)")
    out.append("- [三、关系分片（影响面追踪）](#三关系分片影响面追踪)")
    out.append("- [四、易踩的定位陷阱](#四易踩的定位陷阱)")
    out.append("- [五、机器地图配套](#五机器地图配套)")
    out.append("")

    total_classes = sum(len(v) for v in modules.values())
    total_methods = sum(len(v) for v in methods.values())
    out.append("## 统计")
    out.append("")
    out.append("| 项 | 值 |")
    out.append("|---|---|")
    out.append("| 源码文件（`.cs`，不含 Designer） | %d |" % len(list(iter_cs_files())))
    out.append("| 模块（顶层目录）数 | %d |" % len(modules))
    out.append("| 类型数 | %d |" % total_classes)
    out.append("| 方法数 | %d |" % total_methods)
    out.append("| 高置信调用边 | %d |" % len(high))
    out.append("| 低置信调用边 | %d |" % len(low))
    out.append("")
    out.append("> **图例**：`⛔` 死代码/无调用方 · `⚠️` 占位/待扩展 · `📄` 同文件多职责。")
    out.append("> **0 消费者 ≠ 死成员**：标注 ⛔ 时删除前仍须确认非横切载体（日志标签/序列化键/权限标识/DI 钩子）。")
    out.append("")

    out.append("## 一、模块骨架")
    out.append("")
    out.append("| 模块 | 分类 | 类型数 | 方法数 | 功能（人工标注） |")
    out.append("|---|---|---|---|---|")
    for mod in sorted(modules, key=lambda m: -len(modules[m])):
        n_cls = len(modules[mod])
        n_mtd = sum(len(methods.get(c, [])) for c in modules[mod])
        out.append("| `%s` | %s | %d | %d | %s |" % (
            mod, categorize(mod), n_cls, n_mtd, DOMAIN_HINTS.get(mod, "—")))
    out.append("")

    out.append("## 二、模块 → 符号分片")
    out.append("")
    out.append("> **怎么用**：先按模块收敛 → 打开该模块分片 → 按类型名找到 `文件:行` → 直接跳读代码块（Step 0.7）。")
    out.append("")
    out.append("| 模块 | 符号分片页 | 类型数 |")
    out.append("|---|---|---|")
    THIN = 6
    thin_mods = [m for m in modules if len(modules[m]) < THIN]
    for mod in sorted(modules, key=lambda m: -len(modules[m])):
        if len(modules[mod]) < THIN:
            continue
        out.append("| `%s` | [[architecture/CodeMap-Symbols-%s]] | %d |" % (
            mod, slug_of(mod), len(modules[mod])))
    if thin_mods:
        out.append("| %s | [[architecture/CodeMap-Symbols-Thin]] | %d |" % (
            "、".join("`%s`" % m for m in sorted(thin_mods)),
            sum(len(modules[m]) for m in thin_mods)))
    out.append("")
    out.append("## 三、关系分片（影响面追踪）")
    out.append("")
    out.append("> **怎么用**：改某类型 / 方法前 → 查关系分片拿**候选调用方文件** → 再用 Grep 确认（Step 2.5）。")
    out.append("> ⛔ 关系分片是**候选集生成器**不是判决：类型级边高置信，方法级边可能同名误连 ⇒ Grep 定论。")
    out.append("")
    out.append("| 分片 | 内容 |")
    out.append("|---|---|")
    out.append("| [[architecture/CodeMap-Relations]] | 被引用**类型** → 调用方文件（高置信）+ 继承/实现边 |")
    for f in sorted(os.listdir(ARCH_DIR)):
        if not (f.startswith("CodeMap-Relations-Methods-") and f.endswith(".md")):
            continue
        stem = f[:-3]
        suffix = ""
        for s in ("-2",):
            if stem.endswith(s):
                suffix = s
                stem = stem[:-2]
        label = "名首字母 N-Z" if suffix else ""
        mod = stem[len("CodeMap-Relations-Methods-"):]
        mod_label = "薄模块合并页" if mod == "Thin" else "`%s`" % mod
        out.append("| [[architecture/%s]] | 调用方在 %s 的被调**方法** → 调用点（低置信%s） |" % (
            stem + suffix, mod_label, (" · " + label) if label else ""))
    out.append("")
    out.append("## 四、易踩的定位陷阱")
    out.append("")
    out.append("| 错误判断 | 实际 | 教训 |")
    out.append("|---|---|---|")
    for wrong, actual, lesson in LOCATION_TRAPS:
        out.append("| %s | %s | %s |" % (wrong, actual, lesson))
    out.append("")

    out.append("## 五、机器地图配套")
    out.append("")
    out.append("- 符号分片 —— 每模块一页（`CodeMap-Symbols-<模块>.md`），逐类 → `文件:行` → 成员签名。")
    out.append("- 关系分片 —— 类型级 / 方法级影响面清单（见上表）。")
    out.append("- 生成器：`tools/codemap_build.py`；引擎 = 官方 `coderepomap`（tree-sitter C# 解析 + PageRank）。")
    out.append("- 刷新：`python tools/codemap_build.py`；同步校验：`python tools/codemap_build.py --check`（非零退出 = 地图已过期）。")
    out.append("- ⛔ 本页骨架与计数随源码自动刷新；⛔ 「定位陷阱」为人工判断，改码后**不随脚本覆盖**。")
    out.append("")
    out.append("## 相关页面")
    out.append("")
    out.append("- [[architecture/CodeMap-Relations]]")
    out.append("- [[architecture/DeviceControlArchitecture]]")
    out.append("- [[project/vibecoding-workflow]]")
    out.append("- [[rules/KR-003-No-Skipping-Query]] · [[rules/KR-009-Grep-Default]]")
    return "\n".join(out) + "\n"


def write_if_changed(path, content):
    """只在内容变化时写盘（幂等 + 避免无谓 diff）。返回 True 表示已写。"""
    old = None
    if os.path.isfile(path):
        with open(path, "rb") as fh:
            old = fh.read().decode("utf-8", errors="replace")
    if old == content:
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    return True


def slug_of(module):
    """模块名 → 文件名安全的 slug。"""
    return re.sub(r"[^A-Za-z0-9]+", "-", module).strip("-")


def list_symbol_shards():
    """列出已存在的生成页（供清理孤儿产物）。"""
    if not os.path.isdir(ARCH_DIR):
        return []
    out = []
    for f in os.listdir(ARCH_DIR):
        if not f.endswith(".md"):
            continue
        if (f.startswith("CodeMap-Symbols-") or f.startswith("CodeMap-Relations")
                or f.startswith("CodeMap-Namespace-")):
            out.append(os.path.join(ARCH_DIR, f))
    return out


def render_symbol_shards(table):
    """符号层按**模块**分片：一模块一页 —— 页内含该模块全部类型 + 方法签名。

    分片而非单页的原因：单页实测 >3000 行，超 architecture 类行数上限；
    分片后单页规模可控，且 Phase 0 只需读命中模块那一张。

    **薄模块合并**（2026-11-18）：类型数 < 6 的模块（如 `Program.cs` / `Properties` /
    `MonitorCam` / `PCLOperate`）单独建页会产出**模板高度相似的小页** ⇒ 触发
    wiki_audit 的 3-gram 重复度告警且信息密度极低 ⇒ 合并进「薄模块页」单页。
    """
    modules = table["modules"]
    THIN_THRESHOLD = 6

    thin = {m: c for m, c in modules.items() if len(c) < THIN_THRESHOLD}
    main = {m: c for m, c in modules.items() if len(c) >= THIN_THRESHOLD}

    out = []
    for mod in sorted(main, key=lambda m: -len(main[m])):
        out.append((os.path.join(ARCH_DIR, "CodeMap-Symbols-%s.md" % slug_of(mod)),
                    _symbol_shard_body(table, mod, main[mod], thin_mods=None)))
    if thin:
        out.append((os.path.join(ARCH_DIR, "CodeMap-Symbols-Thin.md"),
                    _symbol_shard_body(table, None, {}, thin_mods=thin)))
    return out


def _member_lines(ms):
    """成员清单行（方法 / 构造 / 属性 / 字段分组）。"""
    if not ms:
        return ["- 成员：（无）"]
    by_kind = {}
    for m in ms:
        by_kind.setdefault(m.get("kind", "method"), []).append(m)
    label = {"method": "方法", "ctor": "构造", "property": "属性", "field": "字段"}
    out = []
    for kind in ("method", "ctor", "property", "field"):
        items = by_kind.get(kind)
        if not items:
            continue
        out.append("- %s（%d）：" % (label.get(kind, kind), len(items)))
        for m in sorted(items, key=lambda x: x["line"] or 0):
            out.append("  - `%s` — `%s:%d`" % (
                m["signature"], m["file"], m["line"]))
    return out


def _symbol_shard_body(table, mod, classes, thin_mods=None):
    """渲染一个符号分片页；thin_mods 非空时渲染「薄模块合并页」。"""
    methods = table["methods"]
    L = []
    if thin_mods is None:
        slug = slug_of(mod)
        title_mod = mod
    else:
        slug = "Thin"
        title_mod = "薄模块合并页"

    L.append("---")
    L.append("title: CodeMap-Symbols-%s — 代码地图·符号签名层·%s（机器生成）" % (slug, title_mod))
    L.append("date: 2026-11-18")
    L.append("updated: 2026-11-18")
    L.append("tags: [代码地图, 符号索引, 机器生成]")
    L.append("status: accepted")
    L.append("---")
    L.append("")
    L.append("# CodeMap-Symbols-%s — %s 的类型与签名" % (slug, title_mod))
    L.append("")
    if thin_mods is None:
        L.append("> **一句话**：模块 `%s` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。" % mod)
        if mod in DOMAIN_HINTS:
            L.append("> %s" % DOMAIN_HINTS[mod])
    else:
        L.append("> **一句话**：类型数少于 6 的小模块合并成一页（逐类 → `文件:行` → 成员签名）；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。")
        L.append("> **为什么合并**：单独建小页会产出模板高度相似的碎页（触发重复度告警）且信息密度低。")
    L.append("> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。")
    L.append("")

    if thin_mods is None:
        ns_rows = ns_rows_for_module(table, mod)
        if ns_rows:
            L.append("## 命名空间一览")
            L.append("")
            L.append("| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |")
            L.append("|---|---|---|---|---|---|")
            for r in ns_rows:
                L.append("| `%s` | %d | %d | %s | %s | %s |" % (
                    r["ns"], len(r["files"]), r["classes"],
                    r["func"] or "—", r["module_page"] or "—", r["adr"] or "—"))
            L.append("")
        n_mtd = sum(len(methods.get(c, [])) for c in classes)
        L.append("| 项 | 值 |")
        L.append("|---|---|")
        L.append("| 类型数 | %d |" % len(classes))
        L.append("| 方法数 | %d |" % n_mtd)
        L.append("")
        L.append("## 章节导航")
        L.append("")
        for cname in sorted(classes):
            L.append("- [%s](#%s)" % (cname, cname))
        L.append("")
        for cname in sorted(classes):
            info = classes[cname]
            L.append("## %s" % cname)
            L.append("")
            L.append("- 签名：`%s`" % info["signature"])
            L.append("- 位置：`%s:%d`" % (info["file"], info["line"]))
            L.append("- 命名空间：`%s`" % info["namespace"])
            L.extend(_member_lines(methods.get(cname, [])))
            L.append("")
    else:
        L.append("| 模块 | 类型数 |")
        L.append("|---|---|")
        for tmod in sorted(thin_mods, key=lambda m: -len(thin_mods[m])):
            L.append("| `%s` | %d |" % (tmod, len(thin_mods[tmod])))
        L.append("")
        for tmod in sorted(thin_mods, key=lambda m: -len(thin_mods[m])):
            tclasses = thin_mods[tmod]
            L.append("## %s" % tmod)
            L.append("")
            if tmod in DOMAIN_HINTS:
                L.append("> %s" % DOMAIN_HINTS[tmod])
            L.append("")
            n_mtd = sum(len(methods.get(c, [])) for c in tclasses)
            L.append("| 项 | 值 |")
            L.append("|---|---|")
            L.append("| 类型数 | %d |" % len(tclasses))
            L.append("| 方法数 | %d |" % n_mtd)
            L.append("")
            for cname in sorted(tclasses):
                info = tclasses[cname]
                L.append("### %s" % cname)
                L.append("")
                L.append("- 签名：`%s`" % info["signature"])
                L.append("- 位置：`%s:%d`" % (info["file"], info["line"]))
                L.append("- 命名空间：`%s`" % info["namespace"])
                L.extend(_member_lines(methods.get(cname, [])))
                L.append("")
    L.append("## 相关页面")
    L.append("")
    L.append("- [[architecture/CodeMap]]")
    return "\n".join(L) + "\n"



def collect_members():
    """全量成员抽取（补官方解析器的 public-only 缺口）。

    官方 `coderepomap` C# 解析器的 `_extract_method` 有 `if name and 'public' in modifiers`
    过滤 ⇒ **只收 public 方法**（实测 1321 / 2833 = 47% 覆盖），私有 / protected / internal
    方法与构造函数全丢 —— 而定位「实现在哪」恰恰主要靠私有方法。
    故本函数用 tree-sitter 直接抽全部成员节点，与官方类型解析合并。

    返回 {类型名: [成员, ...]}，成员 = {kind, name, signature, file, line}。
    """
    _R, lang, parser_cls = load_engine()
    if parser_cls is None:
        return {}
    parser = parser_cls(lang)

    out = {}
    for path in iter_cs_files():
        if path.endswith(".Designer.cs"):
            continue          # Designer 是自动生成的控件声明，噪声大且非定位入口
        try:
            src = open(path, "rb").read()
        except OSError:
            continue
        rel = os.path.relpath(path, CODE_ROOT).replace("\\", "/")
        try:
            tree = parser.parse(src)
        except Exception:
            continue
        _walk_types(tree.root_node, src, rel, out)
    return out


def _node_text(node, src):
    return src[node.start_byte:node.end_byte].decode("utf-8", "replace")


def _walk_types(node, src, rel, out):
    """递归找类型声明，把其成员挂到类型名下（嵌套类型用外层名+内层名）。"""
    for child in node.children:
        t = child.type
        if t in ("class_declaration", "struct_declaration", "interface_declaration",
                 "record_declaration", "enum_declaration"):
            nm = child.child_by_field_name("name")
            tname = _node_text(nm, src) if nm is not None else "?"
            body = child.child_by_field_name("body")
            members = []
            if body is not None:
                _collect_members(body, src, rel, members)
                # 嵌套类型
                _walk_types(body, src, rel, out)
            if members:
                out.setdefault(tname, []).extend(members)
        elif t in ("namespace_declaration", "file_scoped_namespace_declaration",
                   "declaration_list"):
            _walk_types(child, src, rel, out)


def _collect_members(body, src, rel, members):
    """抽取 body 下的成员声明（方法 / 构造 / 属性 / 字段 / 事件）。"""
    for child in body.children:
        t = child.type
        if t == "method_declaration":
            name = child.child_by_field_name("name")
            params = child.child_by_field_name("parameters")
            rtype = child.child_by_field_name("type")
            if name is None:
                continue
            members.append({
                "kind": "method",
                "name": _node_text(name, src),
                "signature": "%s %s(%s)" % (
                    _node_text(rtype, src) if rtype is not None else "void",
                    _node_text(name, src),
                    _param_text(params, src)),
                "file": rel,
                "line": child.start_point[0] + 1,
            })
        elif t == "constructor_declaration":
            name = child.child_by_field_name("name")
            params = child.child_by_field_name("parameters")
            if name is None:
                continue
            members.append({
                "kind": "ctor",
                "name": _node_text(name, src),
                "signature": "%s(%s)" % (_node_text(name, src), _param_text(params, src)),
                "file": rel,
                "line": child.start_point[0] + 1,
            })
        elif t == "property_declaration":
            name = child.child_by_field_name("name")
            ptype = child.child_by_field_name("type")
            if name is None:
                continue
            members.append({
                "kind": "property",
                "name": _node_text(name, src),
                "signature": "%s %s { get; set; }" % (
                    _node_text(ptype, src) if ptype is not None else "?", _node_text(name, src)),
                "file": rel,
                "line": child.start_point[0] + 1,
            })
        elif t == "field_declaration":
            ptype = child.child_by_field_name("type")
            for vd in child.children:
                if vd.type != "variable_declarator":
                    continue
                vn = vd.child_by_field_name("name")
                if vn is None:
                    continue
                members.append({
                    "kind": "field",
                    "name": _node_text(vn, src),
                    "signature": "%s %s" % (
                        _node_text(ptype, src) if ptype is not None else "?", _node_text(vn, src)),
                    "file": rel,
                    "line": child.start_point[0] + 1,
                })


def _param_text(params, src):
    if params is None:
        return ""
    parts = []
    for p in params.children:
        if p.type == "parameter":
            pt = p.child_by_field_name("type")
            pn = p.child_by_field_name("name")
            txt = _node_text(pt, src) if pt is not None else "?"
            if pn is not None:
                txt += " " + _node_text(pn, src)
            parts.append(txt)
    return ", ".join(parts)


def render_relations_shards(table, high, low):
    """关系层分片：高置信类型边一页 + 低置信方法边按首字母分片。

    分片原因：合并后实测 >5000 行，超 architecture 类行数上限。
    分片键：低置信节按被调方法名首字母分桶（A-M / N-Z），保持单页可控。
    """
    inherits = table["inherits"]

    reverse = {}
    for caller, callee_type, line in high:
        reverse.setdefault(callee_type, {}).setdefault(caller, []).append(line)
    low_rev = {}
    for caller, callee_method, line in low:
        low_rev.setdefault(callee_method, {}).setdefault(caller, []).append(line)

    out = []

    # ---- 分片 1：高置信类型级 ----
    L = []
    L.append("---")
    L.append("title: CodeMap-Relations — 代码地图·关系层·类型级影响面（机器生成）")
    L.append("date: 2026-11-18")
    L.append("updated: 2026-11-18")
    L.append("tags: [代码地图, 依赖关系, 影响面, 机器生成]")
    L.append("status: accepted")
    L.append("---")
    L.append("")
    L.append("# CodeMap-Relations — 类型级影响面（高置信）")
    L.append("")
    L.append("> **一句话**：被引用**类型** → 调用方文件清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。")
    L.append("> **置信度**：高置信 = 接收者就是该类型实例（`X.Method(...)`）⇒ 改该类型必影响此处。")
    L.append("> **⚠️ 边界**：同名不同类会误连 ⇒ **结论仍以 Step 0.7 / 2.5 的 Grep 为准**（见 [[rules/KR-009-Grep-Default]]），本页只用于**缩小搜索范围**。")
    L.append("> **低置信方法级影响面**（纯标识符调用）见下方「方法级影响面分片」清单。")
    L.append("> **⚠️ 官方 L3 的坑**：coderepomap 官方 C# 解析器只发 `inherits`/`implements`（零方法调用点），调用边由本仓库自研补齐 —— 见 [[lessons/RepomapCSharpCallEdgeGap]]。")
    L.append("")
    L.append("## 统计")
    L.append("")
    L.append("| 项 | 值 |")
    L.append("|---|---|")
    L.append("| 高置信调用边 | %d |" % len(high))
    L.append("| 被引用类型数 | %d |" % len(reverse))
    L.append("| 继承 / 实现边 | %d |" % len(inherits))
    L.append("")
    L.append("## 一、被引用类型 → 调用方")
    L.append("")
    L.append("> **怎么用**：改某类型前，先在此查「谁引用它」→ 得到候选文件 → 再用 Grep 确认（Step 2.5）。")
    L.append("")
    for callee in sorted(reverse, key=lambda k: (-len(reverse[k]), k)):
        callers = reverse[callee]
        total = sum(len(v) for v in callers.values())
        L.append("### %s（%d 处调用 / %d 个调用方文件）" % (callee, total, len(callers)))
        L.append("")
        for caller in sorted(callers):
            lines = sorted(callers[caller])
            L.append("- `%s` — 行 %s" % (
                caller, "、".join(str(x) for x in lines)))
        L.append("")
    L.append("## 二、继承 / 实现边")
    L.append("")
    for frm, to, kind in sorted(inherits):
        if to in ("IDisposable", "EventArgs", "UserControl", "Window", "Attribute",
                  "INotifyPropertyChanged"):
            continue
        L.append("- `%s` → `%s`（%s）" % (frm, to, kind or "关系"))
    L.append("")
    L.append("## 相关页面")
    L.append("")
    L.append("- [[architecture/CodeMap]]")
    L.append("@@METHOD_SHARDS_LIST@@")
    L.append("- [[rules/KR-009-Grep-Default]]")
    out.append((os.path.join(ARCH_DIR, "CodeMap-Relations.md"), "\n".join(L) + "\n"))

    # ---- 分片 2：低置信方法级（按**调用方模块**分片）----
    # 分片键选「调用方模块」而非被调方法名：Phase 2.5 问的是「改 X 会波及哪些模块」，
    # 按模块切分天然对齐工作流边界，且每片规模可控。
    buckets = {}
    for callee, callers in low_rev.items():
        for caller in callers:
            mod = caller.split("/")[0] if "/" in caller else caller
            buckets.setdefault(mod, {}).setdefault(callee, {}).setdefault(caller, []).append(
                callers[caller])
    # 薄模块合并：调用边数 < 30 的模块单独建页 ⇒ 模板高度相似的碎页（重复度告警）⇒ 合并
    THIN_EDGE = 30
    thin_buckets = {m: v for m, v in buckets.items()
                    if sum(sum(len(x) for x in c.values()) for c in v.values()) < THIN_EDGE}
    for m in thin_buckets:
        buckets.pop(m)
    if thin_buckets:
        merged = {}
        for m, v in thin_buckets.items():
            for callee, callers in v.items():
                merged.setdefault(callee, {}).update(callers)
        buckets["__thin__"] = merged

    for mod in sorted(buckets, key=lambda m: -len(buckets[m])):
        items = buckets[mod]
        # 二级分片：仅当单页会超行数上限时才按被调方法名首字母切分（A-M / N-Z）。
        # ⚠️ 不要无条件切：同模板小页会触发 wiki_audit 的 3-gram 重复度告警。
        # 判据：先估行数（每被调方法 ~4 行 + 标题开销），超 1200 行才切
        # （实测系数 4 偏小：MainDeviceControl 未切却达 2079 行 ⇒ 阈值下调）。
        est_lines = sum(len(v) * 4 + 6 for v in items.values())
        sub = {}
        if est_lines > 1200:
            for callee, callers in items.items():
                key = callee[0].upper()
                sub.setdefault("A-M" if key < "N" else "N-Z", {})[callee] = callers
        else:
            sub["ALL"] = items
        for sub_key in sorted(sub):
            sub_items = sub[sub_key]
            suffix = "" if sub_key in ("A-M", "ALL") else "-2"
            slug_mod = "Thin" if mod == "__thin__" else slug_of(mod)
            path = os.path.join(ARCH_DIR, "CodeMap-Relations-Methods-%s%s.md" % (
                slug_mod, suffix))
            M = []
            M.append("---")
            M.append("title: CodeMap-Relations-Methods-%s%s — 代码地图·方法级影响面·%s（机器生成）" % (
                slug_of(mod) if mod != "__thin__" else "Thin", suffix,
                mod if mod != "__thin__" else "薄模块合并页"))
            M.append("date: 2026-11-18")
            M.append("updated: 2026-11-18")
            M.append("tags: [代码地图, 依赖关系, 影响面, 机器生成]")
            M.append("status: accepted")
            M.append("---")
            M.append("")
            M.append("# CodeMap-Relations-Methods-%s%s — 方法级影响面（低置信 · 调用方在 %s%s）" % (
                slug_of(mod) if mod != "__thin__" else "Thin", suffix,
                mod if mod != "__thin__" else "薄模块合并页",
                "" if sub_key == "ALL" else " · 名首字母 " + sub_key))
            M.append("")
            M.append("> **一句话**：**调用方位于 `%s` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。" % (
                mod if mod != "__thin__" else "薄模块合并页"))
            M.append("> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。")
            M.append("> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。")
            M.append("> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。")
            M.append("")
            M.append("| 项 | 值 |")
            M.append("|---|---|")
            M.append("| 被调方法数 | %d |" % len(sub_items))
            M.append("| 调用点数 | %d |" % sum(
                sum(len(v) for v in c.values()) for c in sub_items.values()))
            M.append("")
            M.append("## 章节导航")
            M.append("")
            for callee in sorted(sub_items):
                M.append("- [%s](#%s)" % (callee, callee))
            M.append("")
            for callee in sorted(sub_items, key=lambda k: (-sum(len(v) for v in sub_items[k].values()), k)):
                callers = sub_items[callee]
                total = sum(len(v) for v in callers.values())
                M.append("## %s" % callee)
                M.append("")
                M.append("> %d 处调用 / %d 个调用方文件" % (total, len(callers)))
                M.append("")
                for caller in sorted(callers):
                    lines = sorted(callers[caller])
                    M.append("- `%s` — 行 %s" % (
                        caller, "、".join(str(x) for x in lines)))
                M.append("")
            M.append("## 相关页面")
            M.append("")
            M.append("- [[architecture/CodeMap-Relations]]")
            M.append("- [[architecture/CodeMap]]")
            out.append((path, "\n".join(M) + "\n"))

    # 方法级分片在上面的段落才生成，类型级关系页的分片清单占位符在此替换为实际分片
    method_shards = sorted(
        os.path.basename(p)[:-3] for p, _ in out
        if os.path.basename(p).startswith("CodeMap-Relations-Methods-"))
    if method_shards:
        shard_list = "\n".join("- [[architecture/%s]]" % s for s in method_shards)
        out = [(p, c.replace("@@METHOD_SHARDS_LIST@@", shard_list)) for p, c in out]
    return out


def load_ns_meta():
    """读命名空间级人工判断层（功能 / 模块归属 / 约束 ADR）。"""
    if not os.path.isfile(NS_META_FILE):
        return {}
    with open(NS_META_FILE, "rb") as fh:
        raw = fh.read().decode("utf-8", errors="replace")
    try:
        items = json.loads(raw)
    except ValueError:
        return {}
    return {it.get("ns", ""): it for it in items if it.get("ns")}


def render_namespace_shards(table):
    """命名空间层：**并入模块分片**（不单独建页）。

    设计变更（2026-11-18）：命名空间粒度过细（51 个命名空间 ⇒ 51 页），
    实测产生 51 个孤儿页（入链 0）+ 大量 3-gram 重复告警 ⇒ 违反 wiki 的
    「入链 / 重复度」闸门精神。命名空间信息（功能 / 模块归属 / 约束 ADR）
    与模块强相关 ⇒ 合并进模块分片的「命名空间一览」小节。
    """
    return []


def ns_rows_for_module(table, module):
    """模块内的命名空间一览（人工判断 + 机器计数），供模块分片渲染。"""
    ns_meta = load_ns_meta()
    ns_files = {}
    ns_classes = {}
    for mod, classes in table["modules"].items():
        if mod != module:
            continue
        for cname, info in classes.items():
            ns = info["namespace"]
            ns_files.setdefault(ns, set()).add(info["file"])
            ns_classes.setdefault(ns, set()).add(cname)
    rows = []
    for ns in sorted(ns_files, key=lambda k: (-len(ns_files[k]), k)):
        meta = ns_meta.get(ns, {})
        rows.append({
            "ns": ns,
            "files": sorted(ns_files[ns]),
            "classes": len(ns_classes[ns]),
            "func": meta.get("功能", ""),
            "module_page": meta.get("模块归属", ""),
            "adr": meta.get("约束 ADR", ""),
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description="生成代码地图页（coderepomap 引擎）")
    ap.add_argument("--check", action="store_true", help="只校验产物是否与源码同步")
    ap.add_argument("--stats", action="store_true", help="只打印统计")
    args = ap.parse_args()

    if not os.path.isdir(CODE_ROOT):
        sys.stderr.write("[codemap_build] 代码根不存在：%s\n" % CODE_ROOT)
        return 1

    table = build_symbol_table()
    if table is None:
        return 1
    high, low = build_call_edges(table["symbols"], table.get("members"))

    if args.stats:
        print("模块数=%d 类型数=%d 方法数=%d 高置信边=%d 低置信边=%d 继承边=%d" % (
            len(table["modules"]),
            sum(len(v) for v in table["modules"].values()),
            sum(len(v) for v in table["methods"].values()),
            len(high), len(low), len(table["inherits"])))
        return 0

    contents = [
        (OUT_OVERVIEW, render_overview(table, high, low)),
    ]
    # 关系层按置信度分片（实测合并后 >5000 行 ⇒ 拆「类型级高置信」+「方法级低置信」）
    contents.extend(render_relations_shards(table, high, low))
    # 符号页按模块分片：单页放不下（实测 >3000 行）⇒ 每模块一页，控制在行数上限内
    for path, content in render_symbol_shards(table):
        contents.append((path, content))
    # 命名空间层：承载「功能 / 模块归属 / 约束 ADR」人工判断 + 文件清单
    for path, content in render_namespace_shards(table):
        contents.append((path, content))

    if args.check:
        stale = []
        for path, content in contents:
            cur = None
            if os.path.isfile(path):
                with open(path, "rb") as fh:
                    cur = fh.read().decode("utf-8", errors="replace")
            if cur != content:
                stale.append(os.path.basename(path))
        if stale:
            print("[codemap_build] 产物与源码不同步：%s" % "、".join(stale))
            return 1
        print("[codemap_build] 全部产物均与当前源码同步")
        return 0

    changed = []
    for path, content in contents:
        if write_if_changed(path, content):
            changed.append(os.path.basename(path))
    # 清理已消失模块的旧分片（模块被删 ⇒ 分片应随之消失，否则残留孤儿页）
    expected = {os.path.basename(p) for p, _ in contents}
    for old in list_symbol_shards():
        if os.path.basename(old) not in expected:
            os.remove(old)
            changed.append(os.path.basename(old) + "（已清理）")
    print("[codemap_build] 已生成 %d 页（%d 更新 / %d 未变）" % (
        len(contents), len([c for c in changed if "清理" not in c]),
        len(contents) - len([c for c in changed if "清理" not in c])))
    for c in changed:
        print("  - %s" % c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
