# -*- coding: utf-8 -*-
"""simplify_selfcheck.py —— 判据-标准一致性与**四重自证**（改标准/改判据后必跑）。

四重自证（判据纪律，见 lessons/StaticVerifierJudgements）：
  1. 干净基线：全库扫描器 error 数须等于 --expect-errors
  2. 注入对照：故意注入「同类成员重复定义」→ 扫描器**必须**报错；随后还原
  3. 结构判据：注入「类提前闭合」→ simplify_guard 必须报 ns-scope
  4. 零变化：还原后再跑，error 数须与第 1 步完全一致

口径-判据一致性：核对 standards/CodeSimplification.md 的「4.1 口径-判据映射表」
所列判据关键字在 scripts/csharp_review.py 中确实存在（防「改了标准忘了改判据」）。

用法：python simplify_selfcheck.py [--expect-errors N]
"""
import os, re, sys, shutil, tempfile, argparse

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import csharp_review as CR
import simplify_guard as G

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CODE = os.path.join(ROOT, "AdaWeldSystem")
STD = os.path.join(ROOT, "Vicoding管理平台", "LLMWiki", "wiki", "standards", "CodeSimplification.md")
SKIP = {"bin", "obj", "3rdDepend", ".vs"}

JUDGE = {
    "1 成员顺序": ["成员顺序错误"],
    "2 region": ["数量不匹配", "含过程性命名"],
    "3 XML 注释": ["未写 /// XML 注释", "缺少 <param>", "缺少 <returns>", "注释单条记录"],
    "4 过度等待": ["B.过度等待/延迟", "Task.Result"],
    "5 功能重叠": ["C.功能重叠"],
    "6 死函数只报": ["疑似死函数"],
    "7 Dispose/C#73": ["Dispose(bool)"],
    "8 命名空间": ["命名空间"],
    "9 多层锁": ["B.多层锁", "嵌套锁", "加锁顺序相反"],
    "11 平行指令入口": ["平行指令入口", "枚举参数内部 switch 分派"],
    "27 注释只写作用": ["A.注释含元信息", "COMMENT_META_RE", "注释禁含元信息"],
}


def scan_all():
    e = w = 0
    for dp, dn, fns in os.walk(CODE):
        dn[:] = [d for d in dn if d not in SKIP]
        for fn in sorted(fns):
            if not fn.endswith(".cs") or fn.endswith(".Designer.cs"):
                continue
            for it in CR.review_file(os.path.join(dp, fn)):
                if it.severity == "error":
                    e += 1
                elif it.severity == "warn":
                    w += 1
    return e, w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect-errors", type=int, default=0)
    a = ap.parse_args()
    ok = True

    print("== A 口径-判据一致性 ==")
    src = open(os.path.join(HERE, "csharp_review.py"), encoding="utf-8").read()
    for name, kws in JUDGE.items():
        miss = [k for k in kws if k not in src]
        if miss:
            ok = False
            print("  FAIL %-16s 判据缺关键字: %s" % (name, miss))
        else:
            print("  ok   %-16s %d 个关键字均在判据实现中" % (name, len(kws)))
    if os.path.exists(STD):
        t = open(STD, encoding="utf-8").read()
        need = ["4.1 口径-判据映射表", "private 允许且建议写", "不得据此删除既有",
                "region 内", "跨 region 不比较", "注释只写作用", "A.注释含元信息"]
        miss = [n for n in need if n not in t]
        if miss:
            ok = False
            print("  FAIL 标准页缺条款: %s" % miss)
        else:
            print("  ok   标准页含映射表与 private /// 新口径")
        # 映射表行 10：语法简化八则 ↔ simplify_run.py 第 5 关 IDE 门禁
        ide_kw = ["语法简化八则", "IDE0017", "IDE0018", "IDE0019", "IDE0031", "IDE0059",
                  "IDE0220", "IDE1005", "IDE0270"]
        miss = [n for n in ide_kw if n not in t]
        run_src = open(os.path.join(HERE, "simplify_run.py"), encoding="utf-8").read()
        run_kw = ["IDE0017", "IDE0018", "IDE0019", "IDE0031", "IDE0059", "IDE0220", "IDE1005", "IDE0270",
                  "--verify-no-changes", "--diagnostics"]
        miss_run = [k for k in run_kw if k not in run_src]
        if miss or miss_run:
            ok = False
            print("  FAIL 语法简化八则判据不一致: 标准缺 %s / 门禁缺 %s" % (miss, miss_run))
        else:
            print("  ok   语法简化八则 ↔ simplify_run 第 5 关 IDE 门禁（0 诊断）")
    else:
        ok = False
        print("  FAIL 找不到标准页")

    print("== A2 脚本 stdout UTF-8 化（防 GBK 崩溃）==")
    import glob
    need_reconf = []
    for sp in sorted(glob.glob(os.path.join(HERE, "*.py"))):
        t2 = open(sp, encoding="utf-8", errors="replace").read()
        if "reconfigure" not in t2:
            need_reconf.append(os.path.basename(sp))
    if need_reconf:
        ok = False
        print("  FAIL 缺 stdout UTF-8 重配置: %s" % need_reconf)
    else:
        print("  ok   全部脚本均已 UTF-8 化")

    print("== B 干净基线 ==")
    e1, w1 = scan_all()
    print("  errors=%d warns=%d (期望 errors=%d)" % (e1, w1, a.expect_errors))
    if e1 != a.expect_errors:
        ok = False
        print("  FAIL 基线 error 数与期望不符")

    print("== C 注入对照（故意注入同类成员重复定义，必须被抓到）==")
    victim = os.path.join(CODE, "MotionControl", "IMotion", "InterpolationMontionParam.cs")
    if not os.path.exists(victim):
        print("  SKIP 注入样本不存在: %s" % os.path.relpath(victim, CODE))
    else:
        tmpd = tempfile.mkdtemp(prefix="simplify_inject_")
        tmp = os.path.join(tmpd, "inject.cs")
        try:
            shutil.copy2(victim, tmp)
            t = open(tmp, "rb").read().decode("utf-8-sig")
            decl = "        private readonly ushort _axisCount;"
            if decl in t:
                t = t.replace(decl, decl + "\n" + decl, 1)
                open(tmp, "wb").write(t.encode("utf-8"))
                hit = [i for i in CR.review_file(tmp) if i.severity == "error"]
                if not hit:
                    ok = False
                    print("  FAIL 注入重复定义后判据未报错")
                else:
                    print("  ok   注入后被捕获: %s" % hit[0].message[:70])
            else:
                print("  SKIP 未找到注入锚点")
        finally:
            shutil.rmtree(tmpd, ignore_errors=True)

    print("== C2 结构判据自证（类闭合提前 + 成员跑到 namespace 必须被抓到）==")
    tmpd = tempfile.mkdtemp(prefix="simplify_struct_")
    try:
        bad = os.path.join(tmpd, "bad.cs")
        open(bad, "w", encoding="utf-8").write(
            "namespace N\n{\n    class A\n    {\n        private int _x;\n    }\n"
            "    public void F()\n    {\n    }\n}\n")
        hit = G.structural_fails(open(bad, encoding="utf-8").read())
        if not hit:
            ok = False
            print("  FAIL 结构判据未抓到「类闭合提前」")
        else:
            print("  ok   结构判据已捕获: %s" % hit[0][:70])
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("== C3 字体判据自证（非默认字体必须报 warn，默认字体不报）==")
    tmpd = tempfile.mkdtemp(prefix="font_judge_")
    try:
        p = os.path.join(tmpd, "font.cs")
        open(p, "w", encoding="utf-8").write(
            "namespace T { class A { void M() { "
            "var a = new System.Drawing.Font(\"\u5b8b\u4f53\", 9F); "
            "var b = new System.Drawing.Font(\"Microsoft YaHei UI\", 10F); } } }\n")
        hits = [i for i in CR.review_file(p) if i.category == "A.字体规范"]
        if len(hits) == 1 and "\u5b8b\u4f53" in hits[0].message:
            print("  ok   非默认字体被捕获，默认字体不报")
        else:
            ok = False
            print("  FAIL 字体判据异常: %s" % [i.message for i in hits])
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("== D 零变化（还原后再跑，error 数须与基线一致）==")
    e2, w2 = scan_all()
    print("  errors=%d warns=%d" % (e2, w2))
    if e2 != e1:
        ok = False
        print("  FAIL 还原后 error 数漂移")
    else:
        print("  ok   与基线一致")

    print("RESULT: %s" % ("PASS" if ok else "NOT-PASS"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
