# -*- coding: utf-8 -*-
"""simplify_run.py —— 代码精简**一键巡检**（每轮收尾必跑）。

依次执行：
  1. simplify_guard.py            结构守卫（brace / namespace 级结构 / region / XML / 缩进 / 成员 / 行尾）
  2. csharp_review.py 全库聚合      分类别 warn/error 统计
  3. simplify_selfcheck.py         口径-判据一致性 + 三重自证
  4. MSBuild /t:Rebuild            **真编译门禁**（2026-10-26 新增；静态守卫查不出位置错误）
  5. dotnet format 只读校验        **IDE 语法简化门禁**（语法简化八则：IDE0017/0018/0019/0031/0059，2026-10-29 新增；2026-10-30 增补 IDE0220/IDE1005/IDE0270）

用法：
  python simplify_run.py                 # 全套（含真编译 + IDE 门禁）
  python simplify_run.py --build-only    # 只跑真编译（批改批次间快速验）
  python simplify_run.py --skip-build    # 跳过编译（仅静态检查，须在日志注明残留）
  python simplify_run.py --skip-ide      # 跳过 IDE 门禁（无 dotnet SDK 时）
退出码：0 = 全绿；1 = 有 NOT-PASS。
"""
import os, re, sys, subprocess, argparse, collections, shutil

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CODE = os.path.join(ROOT, "AdaWeldSystem")
CSPROJ = os.path.join(CODE, "AdaWeldSystem.csproj")
SKIP = {"bin", "obj", "3rdDepend", ".vs"}
PY = sys.executable
MSBUILD_CANDIDATES = [
    r"C:\Program Files\Microsoft Visual Studio\18\Insiders\MSBuild\Current\Bin\MSBuild.exe",
    r"C:\Program Files\Microsoft Visual Studio\18\Insiders\MSBuild\Current\Bin\amd64\MSBuild.exe",
    r"C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\MSBuild\Current\Bin\MSBuild.exe",
    r"C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\MSBuild\Current\Bin\amd64\MSBuild.exe",
]


def run(script, args=()):
    p = subprocess.run([PY, os.path.join(HERE, script)] + list(args),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def find_msbuild():
    env = os.environ.get("MSBUILD_EXE")
    if env and os.path.isfile(env):
        return env
    for p in MSBUILD_CANDIDATES:
        if os.path.isfile(p):
            return p
    return shutil.which("msbuild") or shutil.which("MSBuild.exe")


def build_gate():
    exe = find_msbuild()
    if not exe:
        print("  BUILD SKIP 未找到 MSBuild（设置 MSBUILD_EXE 或安装 VS Build Tools）")
        return None
    cmd = [exe, CSPROJ, "/t:Rebuild", "/p:Configuration=Debug", "/p:Platform=AnyCPU",
           "/v:m", "/nologo", "/clp:ErrorsOnly"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900)
    except subprocess.TimeoutExpired:
        print("  BUILD FAIL timeout(900s)")
        return False
    out = ((p.stdout or "") + (p.stderr or ""))
    errs = [l.strip() for l in out.split("\n") if ": error " in l or l.strip().startswith("error ")]
    for l in errs[:20]:
        print("  ERROR " + l)
    print("  build: errors=%d rc=%d exe=%s" % (len(errs), p.returncode, exe))
    return p.returncode == 0 and not errs


def ide_gate():
    """IDE 语法简化门禁：dotnet format 只读校验（0 诊断 = 通过）。"""
    exe = shutil.which("dotnet")
    if not exe:
        print("  IDE SKIP 未找到 dotnet SDK（可 --skip-ide 显式跳过）")
        return None
    cmd = [exe, "format", "style", CSPROJ, "--verify-no-changes",
           "--diagnostics", "IDE0017", "IDE0018", "IDE0019", "IDE0031", "IDE0059",
           "IDE0220", "IDE1005", "IDE0270",
           "--severity", "info", "--no-restore", "--verbosity", "minimal"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900)
    except subprocess.TimeoutExpired:
        print("  IDE FAIL timeout(900s)")
        return False
    out = ((p.stdout or "") + (p.stderr or ""))
    # dotnet format 的长诊断行可能被终端折行，按 ID 出现次数计数（覆盖 IDE00xx 与 IDE0220/IDE1005 两种形态）
    ids = re.findall(r"IDE\d{4}", out)
    hits = [l.strip() for l in out.split("\n") if re.search(r"IDE\d{4}", l)]
    for l in hits[:10]:
        print("  IDE  " + l[:160])
    print("  ide: remaining=%d rc=%d (语法简化八则 IDE0017/0018/0019/0031/0059/0220/1005/0270)"
          % (len(ids), p.returncode))
    return p.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect-errors", type=int, default=0)
    ap.add_argument("--build-only", action="store_true")
    ap.add_argument("--skip-build", action="store_true")
    ap.add_argument("--skip-ide", action="store_true")
    a = ap.parse_args()
    if a.build_only:
        ok = build_gate()
        print("simplify_run: %s" % ("PASS" if ok else ("SKIP" if ok is None else "NOT-PASS")))
        return 0 if ok is not False else 1

    ok = True
    print("== 1 结构守卫 ==")
    rc, out = run("simplify_guard.py")
    print(out.strip().split("\n")[-1] if out.strip() else "(no output)")
    for l in out.split("\n"):
        if l.startswith("FAIL"):
            print("  " + l)
    if rc != 0:
        ok = False
    print("== 2 扫描器聚合 ==")
    import csharp_review as CR
    agg = collections.Counter()
    errs = []
    for dp, dn, fns in os.walk(CODE):
        dn[:] = [d for d in dn if d not in SKIP]
        for fn in sorted(fns):
            if not fn.endswith(".cs"):
                continue
            fp = os.path.join(dp, fn)
            for it in CR.review_file(fp):
                agg[(it.severity, it.category)] += 1
                if it.severity == "error":
                    errs.append((os.path.relpath(fp, CODE), it.line, it.message[:70]))
    for k, v in agg.most_common():
        print("  %-6s %-20s %d" % (k[0], k[1], v))
    for e in errs[:10]:
        print("  ERROR %s:%d %s" % e)
    if errs:
        ok = False
    print("== 3 判据自检 ==")
    rc, out = run("simplify_selfcheck.py", ["--expect-errors", str(a.expect_errors)])
    for l in out.split("\n"):
        if l.strip():
            print("  " + l)
    if rc != 0:
        ok = False
    print("== 4 真编译门禁 ==")
    if a.skip_build:
        print("  BUILD SKIP（--skip-build：须在日志注明「真编译待验」）")
    else:
        brc = build_gate()
        if brc is False:
            ok = False
    print("== 5 IDE 语法简化门禁 ==")
    if a.skip_ide:
        print("  IDE SKIP（--skip-ide）")
    else:
        irc = ide_gate()
        if irc is False:
            ok = False
    print("simplify_run: %s" % ("PASS" if ok else "NOT-PASS"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
