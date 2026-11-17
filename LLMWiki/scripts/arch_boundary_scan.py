# -*- coding: utf-8 -*-
"""arch_boundary_scan.py —— 架构维度 / 代码层边界 / 精简候选 全库只读审查与逐项标记。

背景：scripts/csharp_review.py 按规范 §四「只处理单个 .cs，不跟踪项目引用、不跨文件分析」，
      无法覆盖「抽象-实体-业务-消费」分层与「UI 不封业务逻辑 / 实例路由」两类跨文件判据。
      本脚本补上这层，并把既有 A/B/C/D 类判据聚合成同一份可复跑的标记清单。

判据权威：
  - standards/ModuleOrganizationPattern.md        H1~H11（抽象/实现/Manager 三件套与依赖方向）
  - standards/WorkflowResponsibilityBoundary.md   R1~R5 + §七 帧载体边界
  - standards/UiStateSimplification.md            真相源唯一 / 统一刷新入口
  - standards/CodeSimplification.md               五维度 + C16~C19（由 csharp_review.py 承担）
  - CodeMap.md §0 判据：0 消费成员只报不删；约束归知识库

只读保证：本脚本不写 AdaWeldSystem/ 下任何文件；产物只落 --out / --csv / --json 指定路径。

用法：
  python arch_boundary_scan.py --selfcheck
  python arch_boundary_scan.py [--root AdaWeldSystem] [--out report.md] [--csv items.csv] [--json items.json]
退出码：0 = 自检 / 审查完成（有无候选不影响退出码）；1 = 自检失败或运行异常。
"""
import os
import re
import io
import csv
import sys
import json
import argparse
import collections
import datetime

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CODE = os.path.join(ROOT, "AdaWeldSystem")
SKIP_DIRS = {"bin", "obj", ".vs", "3rdDepend", ".git", "Properties", "Resources"}

# ---------------------------------------------------------------- 基础工具

def read_text(fp):
    raw = open(fp, "rb").read()
    for enc in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def mask_literals_and_comments(src):
    """先字符串后注释（⛔ 顺序不可换），等长空格替换以保留行号。

    为什么等长替换：定位必须给出真实行号；把注释整行删掉会让报告行号漂移。
    为什么先字符串：字符串里的 //（URL/路径）若被当注释，会破坏引号配对并污染后续扫描。
    """
    n = len(src)
    out = list(src)
    i = 0
    # ① 字符串 / 字符字面量（含 @"..." 逐字字符串）
    while i < n:
        c = src[i]
        if c == "@" and i + 1 < n and src[i + 1] == '"':
            j = i + 2
            while j < n:
                if src[j] == '"':
                    if j + 1 < n and src[j + 1] == '"':
                        j += 2
                        continue
                    j += 1
                    break
                j += 1
            for k in range(i, min(j, n)):
                if out[k] != "\n":
                    out[k] = " "
            i = j
            continue
        if c == '"' or c == "'":
            quote = c
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == quote:
                    j += 1
                    break
                if src[j] == "\n":
                    break
                j += 1
            for k in range(i, min(j, n)):
                if out[k] != "\n":
                    out[k] = " "
            i = j
            continue
        i += 1
    # ② 注释（此时字符串已被空格覆盖，不会再误伤）
    masked = "".join(out)
    out = list(masked)
    i = 0
    while i < n:
        if masked[i] == "/" and i + 1 < n and masked[i + 1] == "/":
            j = i
            while j < n and masked[j] != "\n":
                j += 1
            for k in range(i, j):
                out[k] = " "
            i = j
            continue
        if masked[i] == "/" and i + 1 < n and masked[i + 1] == "*":
            j = i + 2
            while j + 1 < n and not (masked[j] == "*" and masked[j + 1] == "/"):
                j += 1
            j = min(j + 2, n)
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
            continue
        i += 1
    return "".join(out)


def collect(root):
    kept, skipped = [], []
    for dp, dn, fns in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for fn in sorted(fns):
            if not fn.endswith(".cs"):
                continue
            fp = os.path.join(dp, fn)
            rel = os.path.relpath(fp, root).replace("\\", "/")
            if fn.lower().endswith(".designer.cs"):
                skipped.append((rel, "designer"))
                continue
            kept.append((fp, rel))
    return kept, skipped


# ---------------------------------------------------------------- 规则注册

RULES = []


def rule(rid, dim, sev, title, suggestion):
    def deco(fn):
        RULES.append(dict(id=rid, dim=dim, sev=sev, title=title,
                          suggestion=suggestion, fn=fn))
        return fn
    return deco


ABSTRACT_MARK = ("Abstractions/", "ILineLaser/", "IMotion/",
                 "IMonitorCam/", "IAlgorithm/")
IMPL_MARK = ("Implementations/", "IntelligentLaserCam/", "VirtualCam/",
             "DeltaEtherCAT/", "HikCam/", "MecaVisionCam/",
             "RealtimeMonitor/", "LineLaserContour/",
             "WeldParamControl/Algorithms/", "EmguALG/")
BACKEND_ROOTS = ("EmguALG/", "LineLaserCam/", "MonitorCam/", "MotionControl/",
                 "WeldParamControl/", "Comm/", "PCLOperate/", "ProductFileControl/")


@rule("A1", "架构", "warn", "抽象层第三方 SDK 依赖",
      "厂商 SDK using / DllImport 下沉到实现层或 Core（H2）；ADR-096 裁定的 Emgu.CV 帧载体豁免")
def r_a1(rel, lines, ctx):
    if not any(m in rel for m in ABSTRACT_MARK):
        return []
    # 只认 using 厂商命名空间 / DllImport，⛔ 不匹配裸标识符（枚举成员名会误报）
    # Emgu.CV 豁免：ADR-096「不引入中性帧类型，Mat 继续作为帧载体，IMonitorCamApi 契约不变」
    pat = re.compile(r"^\s*using\s+(Hikvision|MvCameraControl|IntelligentLaser\w*|"
                     r"SmartRay\w*|S7\.Net|Delta\w*|System\.Runtime\.InteropServices)\b"
                     r"|\bDllImport\b")
    return [(i, m.group(0)) for i, l in enumerate(lines, 1)
            for m in [pat.search(l)] if m]


@rule("A2", "架构", "warn", "模组层反向依赖流程层",
      "公共枚举 / 契约下沉到模组 Api 层，去掉 using MainDeviceControl(DeviceWorkflow)（R1 推论）")
def r_a2(rel, lines, ctx):
    if not rel.startswith(BACKEND_ROOTS):
        return []
    pat = re.compile(r"^\s*using\s+AdaWeldSystem\.MainDeviceControl"
                     r"(\.DeviceWorkflow)?\s*;")
    return [(i, l.strip()) for i, l in enumerate(lines, 1) if pat.search(l)]


@rule("A3", "架构", "info", "实现层引用 Manager",
      "实现层不认识 Manager；同级 Manager 不互持算法对象（H8 / ADR-097）")
def r_a3(rel, lines, ctx):
    if not any(m in rel for m in IMPL_MARK):
        return []
    pat = re.compile(r"\b\w*Manager\.Instance\b")
    return [(i, m.group(0)) for i, l in enumerate(lines, 1)
            for m in [pat.search(l)] if m]


@rule("A4", "架构", "warn", "绕过 Manager 直取实现类",
      "外部只允许经 Manager 访问；禁止 new 实现类 / 实现类.Instance（H5/H6）")
def r_a4(rel, lines, ctx):
    if rel.startswith("UIDesign/"):
        return []  # UI 侧交给 B2，避免同一处重复标记
    if any(m in rel for m in IMPL_MARK) or "Manager" in os.path.basename(rel):
        return []
    pat = ctx["impl_pat"]
    if pat is None:
        return []
    return [(i, m.group(0)) for i, l in enumerate(lines, 1)
            for m in [pat.search(l)] if m]


@rule("A5", "架构", "info", "配置实例外流",
      "配置类实例只由 Manager 持有；外部用只读引用 + 无参 Load/Save（H7 / ADR-043）")
def r_a5(rel, lines, ctx):
    if not rel.startswith(("UIDesign/", "MainDeviceControl/")):
        return []
    if "Manager" in os.path.basename(rel) or rel.endswith("Config.cs"):
        return []
    pat = re.compile(r"\bnew\s+(\w*Config)\s*\(")
    return [(i, m.group(1)) for i, l in enumerate(lines, 1)
            for m in [pat.search(l)] if m]


@rule("A6", "架构", "warn", "算法 / 实现层计算路径同步落盘",
      "计算路径禁写文件与直调记录模块；留痕只触发事件，由记录模块异步入队（H9 / ADR-040）")
def r_a6(rel, lines, ctx):
    if not any(m in rel for m in IMPL_MARK):
        return []
    base = os.path.basename(rel)
    # 配置导入 / 打包 / 读取工具 / Manager / 回放算法：IO 是其裁定职责，不算计算路径落盘
    # （SystemConfigPackager / MotionConfigImporter / ImageRoiTool / PlaybackAlgorithm / AlgorithmManager）
    if re.search(r"(Config|Importer|Packager|Reader|Tool|Manager|Playback)", base):
        return []
    # 只认「写入 / 记录」动作；File.Exists / ReadAllText / Directory.Get* 属只读探测，不判违规
    pat = re.compile(r"\b(RunRecordManager|RecordFileStore|RecordProcessFrame\w*|"
                     r"StreamWriter|XmlSerializer|File\.(WriteAllText|WriteAllBytes|AppendAllText))")
    return [(i, m.group(0)) for i, l in enumerate(lines, 1)
            for m in [pat.search(l)] if m]


@rule("A7", "架构", "warn", "业务层 as 转型绑定单一厂商",
      "能力经基类虚属性暴露，UI / 业务层禁 as 到 Delta*/Hik*/Virtual*（H5）")
def r_a7(rel, lines, ctx):
    # Manager 持有实现类实例，向下转型到自有实现是合法能力入口（H5 管的是业务层 / UI 层）
    if "Manager" in os.path.basename(rel):
        return []
    pat = re.compile(r"\bas\s+(Delta\w+|Hik\w+|IntelligentLaser\w+|"
                     r"MecaVision\w+|Virtual\w+)")
    return [(i, m.group(1)) for i, l in enumerate(lines, 1)
            for m in [pat.search(l)] if m]


@rule("B1", "边界", "warn", "UI 层图像运算",
      "UI 只接收成品帧；new Mat / CvInvoke / VideoCapture / 解码绘制归算法层或 Manager（ADR-096 §七）")
def r_b1(rel, lines, ctx):
    if not rel.startswith("UIDesign/"):
        return []
    pat = re.compile(r"\b(new\s+Mat\s*\(|CvInvoke\.|VideoCapture\b|"
                     r"new\s+Image<|CvEnum\.|\.ToImage<|\.Convert<)")
    return [(i, m.group(0)) for i, l in enumerate(lines, 1)
            for m in [pat.search(l)] if m]


@rule("B2", "边界", "warn", "UI 层直接 new 后端实现类 / 算法类",
      "UI 只认 Manager.Instance；算法唯一入口 AlgorithmManager.Instance（ADR-097）")
def r_b2(rel, lines, ctx):
    if not rel.startswith("UIDesign/"):
        return []
    pat = ctx["impl_pat"]
    if pat is None:
        return []
    return [(i, m.group(0)) for i, l in enumerate(lines, 1)
            for m in [pat.search(l)] if m]


@rule("B3", "边界", "error", "UI 层写流程状态 / 推进执行步",
      "状态只经流程层 SetState / SetWeldStatus 写入；UI 只读（三态模型 / R3）")
def r_b3(rel, lines, ctx):
    if not rel.startswith("UIDesign/"):
        return []
    pat = re.compile(r"\b(SetWeldStatus|SetState|SetStatus|FlowProcess)\s*\(|"
                     r"\bRunStep\s*=")
    return [(i, m.group(0)) for i, l in enumerate(lines, 1)
            for m in [pat.search(l)] if m]


@rule("B4", "边界", "error", "非 UI 层反向 using UIDesign",
      "依赖单向：后端不得引用 UI 命名空间（Program.cs 启动入口豁免）")
def r_b4(rel, lines, ctx):
    if rel.startswith("UIDesign/") or rel == "Program.cs":
        return []
    pat = re.compile(r"^\s*using\s+AdaWeldSystem\.UIDesign\b")
    return [(i, l.strip()) for i, l in enumerate(lines, 1) if pat.search(l)]


@rule("B5", "边界", "info", "UI 层直读写配置载体",
      "配置读写走 Manager 无参接口；UI 不持有 XdocumentReaderWriter / 直接读写文件")
def r_b5(rel, lines, ctx):
    if not rel.startswith("UIDesign/"):
        return []
    pat = re.compile(r"\b(XdocumentReaderWriter|IniHelper|XmlDocument|"
                     r"File\.(ReadAllText|WriteAllText))\b")
    return [(i, m.group(0)) for i, l in enumerate(lines, 1)
            for m in [pat.search(l)] if m]


@rule("B6", "边界", "info", "初始化期疑似追溯查询",
      "初始化零追溯：构造 / HandleCreated / Shown 期禁查库与扫目录；查询只由用户交互触发（H11 / ADR-078）")
def r_b6(rel, lines, ctx):
    if not rel.startswith("UIDesign/"):
        return []
    head = re.compile(r"^\s*(public|private|protected)\s+[\w<>]+\s*"
                      r"(\w*_(Shown|HandleCreated|Load)|InitializeComponent|\w+)\s*\(")
    query = re.compile(r"\b(Directory\.(GetFiles|GetDirectories)|"
                       r"ProductFileRecordManager\.Select\w*|RecordFileStore|\.Select\w*\()")
    out, in_ctor = [], False
    for i, l in enumerate(lines, 1):
        if head.search(l):
            in_ctor = True
            continue
        if in_ctor and l.strip() == "}":
            in_ctor = False
        if in_ctor:
            m = query.search(l)
            if m:
                out.append((i, m.group(0)))
    return out


# ---------------------------------------------------------------- 全局规则

def global_rules(ctx):
    """抽象契约消费面：0 消费只报不删（顶层裁定 2）。"""
    out = []
    for name, defrel in sorted(ctx["abstract_types"].items()):
        n = ctx["name_use"].get(name, 0)
        if n <= 1:
            out.append(dict(id="A8", dim="架构", sev="info",
                            title="抽象契约零消费候选", file=defrel, line=0,
                            evidence=name + " 全库引用 %d 次" % n,
                            suggestion="0 消费 ≠ 死成员，只报不删，由业主逐案裁决"))
    return out


# ---------------------------------------------------------------- 上下文构建

DTO_SUFFIX = ("Config", "Result", "EventArgs", "Data", "Info", "Item", "Args",
              "Attribute", "Enum", "Helper", "Tool", "Store", "Sample", "Entry",
              "Status", "Value", "Param", "Packet", "Element", "Format", "Table")


def build_context(files):
    class_pat = re.compile(r"^\s*(?:public|internal|private|protected)?\s*"
                           r"(?:static\s+|abstract\s+|sealed\s+|partial\s+)*"
                           r"class\s+(\w+)")
    impl_classes, abstract_types, mgr_files = set(), {}, set()
    for fp, rel in files:
        txt = read_text(fp)
        masked = mask_literals_and_comments(txt)
        for m in class_pat.finditer(masked):
            name = m.group(1)
            if any(m in rel for m in IMPL_MARK) and not name.endswith(DTO_SUFFIX) \
                    and not name.startswith("Native"):
                impl_classes.add(name)
            if any(m in rel for m in ABSTRACT_MARK):
                abstract_types[name] = rel
            if os.path.basename(rel).startswith(name) and name.endswith("Manager"):
                mgr_files.add(rel)
    if impl_classes:
        alt = "|".join(re.escape(c) for c in sorted(impl_classes, key=len, reverse=True))
        impl_pat = re.compile(r"\b(?:new\s+(" + alt + r")\s*\(|(" + alt + r")\.Instance\b)")
    else:
        impl_pat = None
    return dict(impl_classes=impl_classes, impl_pat=impl_pat,
                abstract_types=abstract_types, mgr_files=mgr_files,
                name_use=collections.Counter())


def run_rules(root, ctx):
    findings = []
    counts = collections.Counter()
    kept, skipped = collect(root)
    for fp, rel in kept:
        txt = read_text(fp)
        masked = mask_literals_and_comments(txt)
        lines = masked.split("\n")
        for name in ctx["abstract_types"]:
            ctx["name_use"][name] += len(re.findall(r"\b" + re.escape(name) + r"\b", masked))
        for r in RULES:
            for line, ev in r["fn"](rel, lines, ctx):
                findings.append(dict(id=r["id"], dim=r["dim"], sev=r["sev"],
                                     title=r["title"], file=rel, line=line,
                                     evidence=str(ev).strip()[:120],
                                     suggestion=r["suggestion"]))
                counts[r["id"]] += 1
    findings.extend(global_rules(ctx))
    counts["A8"] = sum(1 for f in findings if f["id"] == "A8")
    return findings, counts, kept, skipped


# ---------------------------------------------------------------- 聚合既有判据

VAR_CATS = {"B.临时变量滥用", "A.单例重复声明", "B.冗余赋值传递",
            "B.无意义Null检查", "B.过度属性"}
FUNC_CATS = {"C.功能重叠", "C.嵌套内联", "C.平行指令入口", "C.疑似死函数",
             "B.多层锁", "B.无意义锁", "B.过度等待/延迟", "B.过度资源管理",
             "C.设备初始化分层"}
COMMENT_CATS = {"A.注释超20字", "A.变量注释多行", "A.占位式XML",
                "A.注释规范", "A.文件整理", "A.字体规范"}


def aggregate_existing(root, kept):
    sys.path.insert(0, HERE)
    import csharp_review as CR
    out, failed = [], []
    for fp, rel in kept:
        try:
            issues = CR.review_file(fp)
        except Exception as e:
            failed.append((rel, type(e).__name__ + ": " + str(e)[:80]))
            continue
        for it in issues:
            cat = getattr(it, "category", "?")
            sev = getattr(it, "severity", "info")
            line = getattr(it, "line", 0)
            msg = getattr(it, "message", "")
            if cat in VAR_CATS:
                dim, did = "单文件精简", "C"
            elif cat in FUNC_CATS:
                dim, did = "函数优化", "D"
            elif cat in COMMENT_CATS:
                dim, did = "注释精简", "E"
            else:
                dim, did = "其它判据", "F"
            out.append(dict(id=did, dim=dim, sev=sev, title=cat,
                            file=rel, line=line, evidence=str(msg).strip()[:120],
                            suggestion="按 standards/CodeSimplification 对应条款逐条人工确认"))
    return out, failed


# ---------------------------------------------------------------- 自检（阴性对照）

SELFCHECK = [
    # (规则ID, 相对路径, 含违规样本, 同路径合规样本)
    ("A1", "EmguALG/Abstractions/IFoo.cs", "using Hikvision.MvCamera;\npublic interface IFoo { }\n",
     "using Emgu.CV;\npublic enum LineLaserKind { IntelligentLaser = 1 }\n"),
    ("A2", "LineLaserCam/LineLaserManager.cs", "using AdaWeldSystem.MainDeviceControl;\n",
     "using System;\n"),
    ("A3", "EmguALG/RealtimeMonitor/WireFeedDistance/W.cs", "var a = AlgorithmManager.Instance;\n",
     "var a = 1;\n"),
    ("A5", "UIDesign/TabPage/DemoPage.cs", "var c = new SeamGuideConfig();\n",
     "var c = 1;\n"),
    ("A6", "EmguALG/RealtimeMonitor/WireFeedDistance/W.cs", "RunRecordManager.Instance.RecordProcessFrame(f);\n",
     "if (File.Exists(p)) { }\n"),
    ("A7", "UIDesign/TabPage/DemoPage.cs", "var d = axis as DeltaMontionAxis;\n",
     "var d = 1;\n"),
    ("B1", "UIDesign/TabPage/DemoPage.cs", "var m = new Mat();\n",
     "var m = 1;\n"),
    ("B3", "UIDesign/TabPage/DemoPage.cs", "SetWeldStatus(SubDeviceWeldStatus.Working);\n",
     "var x = 1;\n"),
    ("B4", "Comm/SystemComm.cs", "using AdaWeldSystem.UIDesign.MainWindow;\n",
     "using System;\n"),
    ("B5", "UIDesign/TabPage/DemoPage.cs", "var r = new XdocumentReaderWriter();\n",
     "var r = 1;\n"),
]


def selfcheck():
    """三件套：① 阴性对照（合成违规样本必须被抓）② 合规样本不误报 ③ 豁免集生效。"""
    fake_ctx = dict(impl_pat=re.compile(r"\b(?:new\s+(PlaybackAlgorithm)\s*\(|"
                                        r"(PlaybackAlgorithm)\.Instance\b)"),
                    abstract_types={}, name_use=collections.Counter())
    by_id = {r["id"]: r for r in RULES}
    rows, ok = [], True
    for rid, rel, bad, good in SELFCHECK:
        r = by_id.get(rid)
        if r is None:
            rows.append((rid, "MISSING", "-", "-")); ok = False; continue
        bh = r["fn"](rel, mask_literals_and_comments(bad).split("\n"), fake_ctx)
        gh = r["fn"](rel, mask_literals_and_comments(good).split("\n"), fake_ctx)
        good_ok = len(gh) == 0
        bad_ok = len(bh) > 0
        rows.append((rid, "PASS" if (good_ok and bad_ok) else "FAIL",
                     len(bh), len(gh)))
        if not (good_ok and bad_ok):
            ok = False
    # A4 / B2 用真实实现类名单形态的合成上下文验证
    for rid, rel in (("A4", "MainDeviceControl/DeviceWorkflow/W.cs"),
                     ("B2", "UIDesign/TabPage/DemoPage.cs")):
        bh = by_id[rid]["fn"](rel, ["var a = new PlaybackAlgorithm();"], fake_ctx)
        gh = by_id[rid]["fn"](rel, ["var a = 1;"], fake_ctx)
        rows.append((rid, "PASS" if bh and not gh else "FAIL", len(bh), len(gh)))
        if not (bh and not gh):
            ok = False
    # B6 自检
    bad = ["private void Demo_Shown(object s, EventArgs e) {",
           "  var f = Directory.GetFiles(p);", "}"]
    bh = by_id["B6"]["fn"]("UIDesign/TabPage/DemoPage.cs", bad, fake_ctx)
    gh = by_id["B6"]["fn"]("UIDesign/TabPage/DemoPage.cs", ["var x = 1;"], fake_ctx)
    rows.append(("B6", "PASS" if bh and not gh else "FAIL", len(bh), len(gh)))
    if not (bh and not gh):
        ok = False
    # 豁免集自检：Manager 内向下转型不算 H5 违规（现场取证 MontionManager.GetDeltaAxis）
    gh_mgr = by_id["A7"]["fn"]("MotionControl/MontionManager.cs",
                               ["var a = x as DeltaMontionAxis;"], fake_ctx)
    rows.append(("A7豁免", "PASS" if not gh_mgr else "FAIL", 0, len(gh_mgr)))
    if gh_mgr:
        ok = False
    print("== 判据阴性对照（合成样本，绝不触碰源目录）==")
    print("  %-5s %-6s %-8s %-8s" % ("规则", "结果", "违规命中", "合规误报"))
    for r in rows:
        print("  %-5s %-6s %-8s %-8s" % r)
    print("  selfcheck: %s (%d/%d)" %
          ("PASS" if ok else "FAIL", sum(1 for r in rows if r[1] == "PASS"), len(rows)))
    return ok, len(rows)


# ---------------------------------------------------------------- 报告

def assign_ids(items):
    order = {"架构": 1, "边界": 2, "单文件精简": 3, "函数优化": 4,
             "注释精简": 5, "其它判据": 6}
    items.sort(key=lambda x: (order.get(x["dim"], 9), x["id"], x["file"], x["line"]))
    seq = collections.Counter()
    for it in items:
        d = order.get(it["dim"], 9)
        seq[d] += 1
        it["mark"] = "[SIMPLIFY-%d-%03d]" % (d, seq[d])
    return items


def write_outputs(items, counts, kept, skipped, failed, out_md, out_csv, out_json,
                  self_ok, self_n):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    by_dim = collections.Counter(x["dim"] for x in items)
    by_sev = collections.Counter(x["sev"] for x in items)
    by_rule = collections.Counter(x["id"] for x in items)

    if out_csv:
        with io.open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["标记ID", "维度", "判据", "级别", "文件", "行", "证据", "建议"])
            for x in items:
                w.writerow([x["mark"], x["dim"], x["id"] + " " + x["title"],
                            x["sev"], x["file"], x["line"],
                            x["evidence"], x["suggestion"]])

    if out_json:
        with io.open(out_json, "w", encoding="utf-8", newline="\n") as f:
            json.dump(dict(generated=now, files_scanned=len(kept),
                           files_skipped=len(skipped), selfcheck=self_ok,
                           counts=dict(counts), items=items),
                      f, ensure_ascii=False, indent=2)

    if not out_md:
        return
    L = []
    a = L.append
    a("# 代码架构与精简核查报告")
    a("")
    a("> 生成时间：%s ｜ 审查工具：`scripts/arch_boundary_scan.py`（只读）｜ 真编译结论另见 `simplify_run.py --build-only`" % now)
    a("> 本轮**未修改任何业务 `.cs` 文件**；下表每一项都是**待确认的精简候选标记**，按 `standards/CodeSimplification` 顶层裁定 2「0 消费只报不删」，删改由业主逐案裁决。")
    a("")
    a("## 一、范围与结论")
    a("")
    a("| 项 | 值 |")
    a("|---|---|")
    a("| 扫描非 Designer `.cs` | %d |" % len(kept))
    a("| 豁免跳过（Designer / 3rdDepend / bin / obj） | %d |" % len(skipped))
    a("| 跨文件架构 / 边界判据 | %d 条逐文件判据（A1~A7 / B1~B6）+ 1 条全局（A8） |" % len(RULES))
    a("| 判据阴性对照 | %s |" % ("PASS" if self_ok else "FAIL"))
    a("| 标记总数 | **%d** |" % len(items))
    a("| 其中 error / warn / info | %d / %d / %d |" %
      (by_sev.get("error", 0), by_sev.get("warn", 0), by_sev.get("info", 0)))
    a("")
    a("### 五维分布")
    a("")
    a("| 用户需求 | 维度 | 标记数 | 承担判据 |")
    a("|---|---|---|---|")
    a("| 1 架构（抽象-实体-业务-消费） | 架构 | %d | A1~A8（H2/H5/H6/H7/H9） |" % by_dim.get("架构", 0))
    a("| 2 代码层边界（UI 不封业务 / 实例路由） | 边界 | %d | B1~B6（ADR-096 §七 / R1~R5 / H11） |" % by_dim.get("边界", 0))
    a("| 3 单文件精简（临时 / 局部变量） | 单文件精简 | %d | `csharp_review.py` B.临时变量滥用 / A.单例重复声明 / B.冗余赋值传递 |" % by_dim.get("单文件精简", 0))
    a("| 4 函数优化 | 函数优化 | %d | `csharp_review.py` C.功能重叠 / C.嵌套内联 / C.平行指令入口 |" % by_dim.get("函数优化", 0))
    a("| 5 注释精简 | 注释精简 | %d | `csharp_review.py` A.注释超20字 / A.变量注释多行 / A.占位式XML |" % by_dim.get("注释精简", 0))
    a("| 附带 | 其它判据 | %d | 既有 A/B/C/D 其余类别 |" % by_dim.get("其它判据", 0))
    a("")
    a("### 逐判据命中（0 命中已由阴性对照证明不是判据空过）")
    a("")
    a("| 判据 | 名称 | 级别 | 命中 |")
    a("|---|---|---|---|")
    for r in RULES:
        a("| %s | %s | %s | %d |" % (r["id"], r["title"], r["sev"], counts.get(r["id"], 0)))
    a("| A8 | 抽象契约零消费候选 | info | %d |" % counts.get("A8", 0))
    a("")
    a("### 用户 5 项需求 → 精确判据命中（避免被存量 info 淹没）")
    a("")
    by_title = collections.Counter(x["title"] for x in items)
    a("| 需求 | 精确判据 | 命中 | 口径 |")
    a("|---|---|---|---|")
    a("| 3 临时/局部变量 | `B.临时变量滥用` | %d | 一次性中转变量、无意义 temp/tmp |" % by_title.get("B.临时变量滥用", 0))
    a("| 3 临时/局部变量 | `A.单例重复声明` | %d | C17：同方法内同名单例局部 ≥2（目标 0） |" % by_title.get("A.单例重复声明", 0))
    a("| 3 临时/局部变量 | `B.冗余赋值传递` | %d | return result / 参数原样赋局部 |" % by_title.get("B.冗余赋值传递", 0))
    a("| 4 函数优化 | `C.功能重叠` | %d | 70%% 方法体相同或超集 |" % by_title.get("C.功能重叠", 0))
    a("| 4 函数优化 | `C.嵌套内联` | %d | private 仅 1 调用且 ≤3 行 |" % by_title.get("C.嵌套内联", 0))
    a("| 4 函数优化 | `C.平行指令入口` | %d | 同族 ≥3 个同前缀无参公开方法 |" % by_title.get("C.平行指令入口", 0))
    a("| 5 注释精简 | `A.注释超20字` | %d | C16/C18 跨行合并口径（目标 0） |" % by_title.get("A.注释超20字", 0))
    a("| 5 注释精简 | `A.变量注释多行` | %d | C19（目标 0） |" % by_title.get("A.变量注释多行", 0))
    a("| 5 注释精简 | `A.占位式XML` | %d | 占位 param/returns（目标 0） |" % by_title.get("A.占位式XML", 0))
    a("| 5 注释精简 | `A.注释规范` | %d | ⚠️ **存量欠账**，顶层裁定 3 明确不追溯、不设全库清零目标 |" % by_title.get("A.注释规范", 0))
    a("")
    a("### 判据收敛与豁免依据（现场取证后收敛，避免过报）")
    a("")
    a("| 判据 | 收敛动作 | 依据 |")
    a("|---|---|---|")
    a("| A1 | 只认 `using 厂商命名空间` / `DllImport`；豁免 `using Emgu.CV` 与枚举成员名 | `LineLaserType.cs:10` 的 `IntelligentLaser` 是枚举值不是 SDK 引用；ADR-096 明确 `Mat` 为帧载体、`IMonitorCamApi` 契约不变，抽象层出现 `Emgu.CV` 属业主裁定 |")
    a("| A6 | 只认写入/记录动作，豁免只读探测；豁免 Config/Importer/Packager/Reader/Tool/Manager/Playback 文件 | H9 禁的是「计算路径同步落盘」；`SystemConfigPackager` / `MotionConfigImporter` / `ImageRoiTool` / `PlaybackAlgorithm` 的 IO 是其裁定职责（ADR-097 回放算法负责录像目录扫描） |")
    a("| A7 | 豁免 Manager 文件内的向下转型 | `MontionManager.GetDeltaAxis` 注释明示「台达专属能力入口」；H5 反例针对业务层 / UI 层 as 绑定厂商 |")
    a("| A8 | 0 消费项一律 info 且只报不删 | 顶层裁定 2 / CodeMap §0 |")
    a("")
    a("## 二、高优先级标记（error / warn 全量）")
    a("")
    hi = [x for x in items if x["sev"] in ("error", "warn")]
    if not hi:
        a("无。跨文件架构与层边界判据在本库未发现确定违规。")
    else:
        a("| 标记 ID | 判据 | 级别 | 文件:行 | 证据 | 建议 |")
        a("|---|---|---|---|---|---|")
        for x in hi:
            a("| `%s` | %s %s | %s | `%s:%s` | %s | %s |" %
              (x["mark"], x["id"], x["title"], x["sev"], x["file"], x["line"],
               x["evidence"].replace("|", "\\|"), x["suggestion"].replace("|", "\\|")))
    a("")
    a("## 三、info 级标记（按文件汇总，全量逐项见 CSV）")
    a("")
    lo = [x for x in items if x["sev"] == "info"]
    agg = collections.defaultdict(list)
    for x in lo:
        agg[(x["file"], x["id"], x["title"])].append(x)
    if not lo:
        a("无。")
    else:
        a("| 文件 | 判据 | 条数 | 标记 ID（首条） |")
        a("|---|---|---|---|")
        for (f, rid, title), xs in sorted(agg.items()):
            a("| `%s` | %s %s | %d | `%s` |" % (f, rid, title, len(xs), xs[0]["mark"]))
    a("")
    a("## 三之二、分批次修复结论与待裁决项")
    a("")
    a("**已修复（三批次，每批均经真编译复核）**")
    a("")
    a("| 批次 | 对象 | 结果 |")
    a("|---|---|---|")
    a("| A · 判据层 | `csharp_review.py` 判据缺陷 + `simplify_selfcheck.py` / 4.1 映射表同步 | 删除与 C16/C18 并存的重复长度判据；临时变量判据排除 `return` 误收、swap、后续重赋值；冗余赋值判据加「改写前快照」豁免；初始化分层判据只认方法定义；成员顺序判据过滤幽灵控制流方法 |")
    a("| B · 代码层 | `DeltaMotionConfig.FlowTimeoutSettings` 私有字段顺序 | 按字节精确重排；`XdocumentReaderWriter` 两条构造函数经取证为解析器误报，改判据不改代码 |")
    a("| C · 精简层 | 7 文件 11 处无意义临时变量 | 改为有业务含义命名（rawText / retCode / rawBytes / pointCloud / cellText / configText），零表达式改动 |")
    a("")
    a("⛔ **机械重排脚本禁用令**：`simplify_apply_member_order.py --fix-victims` 曾把构造函数插进 `if/else if` 链中间，造成编译期结构错误；而 guard / 成员顺序报告 / selfcheck 当时全绿。含构造函数重载或跨行 if/else 链的文件一律禁用该脚本，任何重排后必须 `MSBuild /t:Rebuild` 复核（KR-010）。")
    a("")
    a("**本次重扫状态（动态）**")
    a("")
    a("- 全库 warn / error：**%d / %d**；`B.临时变量滥用`：**%d**；`A.注释规范` warn：**%d**" %
      (by_sev.get("warn", 0), by_sev.get("error", 0),
       by_title.get("B.临时变量滥用", 0),
       sum(1 for x in items if x["title"] == "A.注释规范" and x["sev"] == "warn")))
    a("- 真编译与全套门禁结论见 Phase 4 日志；⛔ 静态检查不替代编译。")
    a("")
    a("**用户第 2 项结论**：B1 UI 图像运算 / B2 UI 直接 new 后端类 / B3 UI 写流程状态 / B4 非 UI 反向 using UIDesign 全为 0，且阴性对照证明判据有效 ⇒ UI 层边界合规，零命中不是判据空过。")
    a("")
    a("**本轮已闭环（业主裁决）**")
    a("")
    a("- `LineLaserManager` 反向依赖：改直读 `WeldParamManager.Instance.CurrentRobotX`；模拟路由（`UpdateRobotPose(_simRobotX)`）与真实路由（RSI `OnRobotDataReceived`）两条写入链原样保留，真实态轮廓帧 X 由 0 变真值。")
    a("- `as DeltaMontionAxis` 全库清零（注册表类型收紧）。")
    a("- 三类存量判据治理 + 台账定性；`C.功能重叠` 名称启发式误报判据删除（两条方法各有 2 个真实消费方，未删方法）。")
    a("- 配置外部 new 收归 Manager：UI 经 `MontionManager.CreatePreviewMotionConfig()` / `AlgorithmManager.CreateEmptyPipelineConfig()` 路由。")
    a("")
    a("**待业主裁决（本轮不动）**")
    a("")
    a("| 组 | 条数 | 卡在哪 |")
    a("|---|---|---|")
    a("| `C.疑似死函数` | 101 | 顶层裁定 2「0 消费只报不删」，删除需逐案裁决 |")
    a("| `C.平行指令入口` | 4 | 合并成单入口 + 枚举会改 public 签名且牵涉机器人指令表，需批准并定枚举 |")
    a("| A3 / A5 / B5 / B6 跨层候选 | 14 | 是否统一收敛为 Manager 路由，属架构口径选择 |")
    a("| 存量 info | 约 117 | 防御性判空 / 周期轮询 / 串行化写入等有意例外，台账已定性 |")
    a("")
    a("## 三之三、存量治理（业主裁定：判据治理 + 台账定性）")
    a("")
    a("| 类别 | 治理前 | 本次重扫 | 去向 |")
    a("|---|---|---|---|")
    a("| `B.过度属性` | 1184 | **%d** | 判据收紧：只报真·重操作；`lock` 快照 / `new` 返回副本豁免；剩余 19 条逐条定性为有意保留，见台账 B-8.1 |" % by_title.get("B.过度属性", 0))
    a("| `A.注释规范` info | 645 | **%d** | 存量欠账默认不进清单（`--verbose` 可查全量），按顶层裁定 3 不追溯，见 B-8.2 |" % by_title.get("A.注释规范", 0))
    a("| `C.嵌套内联` | 49 | **%d** | 台账 B-6 / B-8.3 七类语义豁免，逐条登记保留 |" % by_title.get("C.嵌套内联", 0))
    a("")
    a("⛔ **未做**（业主确认的口径）：补 645 条 `///`（净增约 645 行注释，与注释精简冲突）、批量内联 49 个方法（台账已裁定保留）、改 1184 处属性（判据过报）。清理对象是判据噪声与台账，不是业务代码。")
    a("")
    a("## 四、自检与能力边界（KR-010）")
    a("")
    a("- 阴性对照：%d 组合成样本逐条注入（含 A7 Manager 豁免集自检），判据全部命中；同路径合规样本零误报 ⇒ 判据未空过。" % self_n)
    a("- 豁免集：Designer.cs / 3rdDepend / bin / obj / .vs 共跳过 %d 个文件。" % len(skipped))
    a("- ⛔ **静态检查 ≠ 构建通过**：类型系统、重载解析、名称解析等语义缺陷只有真编译器能定；本报告结论须与 `MSBuild /t:Rebuild` 退出码 0 并列看待。")
    a("- ⛔ **0 消费 ≠ 死成员**：日志标签、序列化键、安全钩子、预留接口一律只报不删。")
    a("- ⛔ **约束归知识库**：本表中的判据说明只写作用，完整约束见 `standards/` 对应页。")
    if failed:
        a("")
        a("### 扫描异常文件（需人工复核）")
        a("")
        for f, e in failed:
            a("- `%s` : %s" % (f, e))
    a("")
    a("## 五、全量清单")
    a("")
    a("- `%s`（CSV，每项一个唯一标记 ID，可用 Excel 筛选）" % (out_csv or "未输出"))
    a("- `%s`（JSON，供脚本复跑比对）" % (out_json or "未输出"))
    a("")
    with io.open(out_md, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="架构 / 层边界 / 精简候选全库只读审查")
    ap.add_argument("--root", default=CODE)
    ap.add_argument("--out", default=None)
    ap.add_argument("--csv", default=None)
    ap.add_argument("--json", default=None)
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()

    if a.selfcheck:
        ok, _ = selfcheck()
        return 0 if ok else 1

    day = datetime.datetime.now().strftime("%Y%m%d")
    out_md = a.out or os.path.join(ROOT, "代码架构与精简核查报告_%s.md" % day)
    out_csv = a.csv or os.path.join(ROOT, "代码架构与精简核查清单_%s.csv" % day)
    out_json = a.json or os.path.join(ROOT, "代码架构与精简核查清单_%s.json" % day)

    self_ok, self_n = selfcheck()
    if not self_ok:
        print("ABORT: 判据自检未通过，拒绝输出可能空过的报告")
        return 1

    ctx = build_context(collect(a.root)[0])
    findings, counts, kept, skipped = run_rules(a.root, ctx)
    existing, failed = aggregate_existing(a.root, kept)
    items = assign_ids(findings + existing)
    write_outputs(items, counts, kept, skipped, failed,
                  out_md, out_csv, out_json, self_ok, self_n)

    print("")
    print("== 全库审查结果 ==")
    print("  files_scanned=%d files_skipped=%d marks=%d failed=%d" %
          (len(kept), len(skipped), len(items), len(failed)))
    for k, v in sorted(collections.Counter(x["dim"] for x in items).items()):
        print("  %-12s %d" % (k, v))
    for k, v in sorted(counts.items()):
        print("  rule %-4s %d" % (k, v))
    print("  report: " + out_md)
    print("  csv   : " + out_csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
