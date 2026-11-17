# -*- coding: utf-8 -*-
"""AdaWeldSystem 代码项目 / LLMWiki 知识库 备份与出包 —— 三种压缩产物，**分模式触发**。

- 路径全部由 __file__ 推导，禁止硬编码绝对路径（工具化约定）。
- 压缩格式统一为 tar.gz，排除 3rdDepend、obj、bin、.vs、.git 与 *.csproj.user / *.suo：
  * 3rdDepend 为第三方源 DLL，体积大且可从厂商 SDK / 历史备份重建；
  * bin 为构建产物（exe + 运行所需原生 DLL + 本地 Config 配置），可由源码重新编译生成；
  * obj / .vs 为 Visual Studio 中间生成物与用户态缓存，可重新生成，
    且 .vs 含 VS 文件锁（FileContentIndex），打包时易触发 Permission denied；
  * .git 为仓库元数据（历史对象/钩子/本地 remote 配置），不属源码，且体积大。
  即压缩仅保留「源码 + 资源等非生成物」，恢复后通过 VS 重新编译即可部署。
  ⚠️ 本地 Config XML/INI 只存在于 bin/Debug/Config/ 下（已被 bin 排除），
  故包内不含任何业务配置；解压部署**不得覆盖**现场已有配置。
- 三种产物与它们各自的工作流位置（2026-10-10 拆分两产物；2026-10-14 增知识库包）：
  * **backup 包**（Step 2.1 用，编码**之前**的回滚点，每天至多一份、按天去重）：
    `AdaWeldSystem_backup_YYYYMMDD_HHMMSS.tar.gz`。
    工作区根若已存在当天（YYYYMMDD）的 backup 包，则跳过，不重复生成。
  * **output 包**（Step 3.8 用，编码**之后**的现场验证包，每次必生成、始终是最新代码）：
    `AdaWeldSystem_output_YYYYMMDD_HHMMSS.tar.gz`。每次生成后清理旧 output 包，
    目录中始终只保留「最新一份」output。
  * ⛔ 为什么 output 不再随 Step 2.1 一起出：Step 2.1 跑在改码**之前**，
    那时打出来的 output 反映的是本轮改动**之前**的代码，现场拿去验证会验到旧码。
    output 必须等到 Phase 3 收尾（本轮改码定稿、静态校验已过）再出。
  * **LLMWiki 知识库包**（治理/编码轮 Phase 3 收尾用，知识库定稿快照，每天至多一份、按天去重）：
    `LLMWiki_backup_YYYYMMDD_HHMMSS.tar.gz`，打包整个 `LLMWiki/` 目录（排除 __pycache__）。
    ⛔ 所有产物落点统一为工作区根（本脚本 ROOT 推导），禁止手搓 tar 落到工作区外（2026-10-14 治理）。
- 用 Python tarfile 实现，规避本机 bash PATH 损坏（ls/tar 不可用）问题。

用法：
  python backup_adaweld.py              # 默认 = 仅 backup（Step 2.1：编码前留回滚点）
  python backup_adaweld.py --output     # 仅 output（Step 3.8：本轮定稿后出现场验证包）
  python backup_adaweld.py --llmwiki    # 仅 LLMWiki 知识库包（治理/编码轮 Phase 3 收尾快照）
  python backup_adaweld.py --all        # backup + output 都出（兼容旧行为，日常不用）
  python backup_adaweld.py --help       # 用法说明

退出码：0 正常（含 backup「跳过」情形）；1 仅当确需创建却失败。
"""
import datetime
import glob
import os
import sys
import tarfile

# __file__ 位于 <workspace>/Vicoding管理平台/LLMWiki/tools/
# 推导：tools -> LLMWiki -> Vicoding管理平台 -> workspace 根（向上三级）
_TOOLS = os.path.dirname(os.path.abspath(__file__))   # .../LLMWiki/tools
_LLMWIKI = os.path.dirname(_TOOLS)                     # .../LLMWiki
ROOT = os.path.dirname(os.path.dirname(_LLMWIKI))      # .../workbudddy（workspace 根）
SRC = os.path.join(ROOT, "AdaWeldSystem")
PREFIX = "AdaWeldSystem_backup_"
OUTPUT_PREFIX = "AdaWeldSystem_output_"
LLM_PREFIX = "LLMWiki_backup_"

USAGE = """用法：python backup_adaweld.py [模式]

模式（默认 --backup）：
  --backup    仅出 AdaWeldSystem backup 包，按天去重（Step 2.1：改码前的回滚点）
  --output    仅出 output 包，每次必生成并清理旧包（Step 3.8：定稿后现场验证包）
  --llmwiki   仅出 LLMWiki 知识库包，按天去重（治理/编码轮 Phase 3 收尾快照）
  --all       backup + output 都出（兼容旧行为）
  -h/--help   显示本用法

所有产物一律落工作区根（脚本 ROOT 推导），禁止手搓 tar 或更改落点。
"""


def _exclude(tarinfo: tarfile.TarInfo) -> "tarfile.TarInfo | None":
    # 排除 3rdDepend（第三方源 DLL，体积大且可从厂商 SDK / 历史备份重建）、
    # bin（构建产物 + 本地 Config 配置，可由源码重新编译生成）、obj 与 .vs（VS 中间生成物/用户态缓存，
    # 可重新生成，且 .vs 含文件锁打包易失败）、.git（仓库元数据，不属源码且体积大）。
    # 压缩仅保留源码、资源等非生成物。
    # *.csproj.user / *.suo 为 VS 本机用户态设置（调试启动路径、启动参数），不属源码，
    # 且各机不同，入包会覆盖现场 VS 设置（2026-11-04 核包实测泄漏 1 项后补入排除）。
    low = tarinfo.name.lower()
    if low.endswith(".csproj.user") or low.endswith(".suo"):
        return None
    parts = tarinfo.name.split("/")
    if "3rdDepend" in parts or "bin" in parts or "obj" in parts or ".vs" in parts or ".git" in parts:
        return None
    return tarinfo


def _exclude_llmwiki(tarinfo: tarfile.TarInfo) -> "tarfile.TarInfo | None":
    # 知识库包仅排除 Python 缓存；其余（wiki / logs / tools / raw）全部保留。
    parts = tarinfo.name.split("/")
    if "__pycache__" in parts or tarinfo.name.endswith(".pyc"):
        return None
    return tarinfo


def _make_tar(out_path: str, src: str = None, arcname: str = "AdaWeldSystem",
              exclude_fn=None) -> bool:
    """构建 tar.gz。默认打包 AdaWeldSystem 源码（排除 3rdDepend/obj/bin/.vs/.git）。

    成功返回 True；失败则清理半截产物并返回 False，避免残留文件干扰去重闸门。
    """
    src = SRC if src is None else src
    exclude_fn = _exclude if exclude_fn is None else exclude_fn
    try:
        with tarfile.open(out_path, "w:gz") as tar:
            tar.add(src, arcname=arcname, filter=exclude_fn)
        return True
    except Exception as exc:  # noqa: BLE001 - 脚本级兜底，便于在会话中直接看到错误
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except OSError:
                pass
        print(f"[backup] 创建失败：{exc}", file=sys.stderr)
        return False


def _prune_old_outputs(keep_path: str) -> None:
    """清理旧 output 包，目录中只保留 keep_path 这一份（即最新）。"""
    keep_abs = os.path.abspath(keep_path)
    for f in glob.glob(os.path.join(ROOT, f"{OUTPUT_PREFIX}*.tar.gz")):
        if os.path.abspath(f) != keep_abs:
            try:
                os.remove(f)
            except OSError:
                pass


def _make_backup() -> int:
    """backup 包：每天至多一份，按天去重。Step 2.1 在改码**之前**调用。"""
    today = datetime.date.today().strftime("%Y%m%d")
    backup_pattern = os.path.join(ROOT, f"{PREFIX}{today}_*.tar.gz")
    existing_backups = sorted(glob.glob(backup_pattern))
    if existing_backups:
        print(f"[backup] 今日备份已存在，跳过：{os.path.basename(existing_backups[0])}")
        return 0
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_out = os.path.join(ROOT, f"{PREFIX}{ts}.tar.gz")
    if not _make_tar(backup_out):
        return 1
    size_mb = os.path.getsize(backup_out) / (1024 * 1024)
    print(f"[backup] 已生成备份：{os.path.basename(backup_out)}（{size_mb:.1f} MB，排除 3rdDepend/obj/bin/.vs/.git）")
    return 0


def _make_llmwiki_backup(force: bool = False) -> int:
    """LLMWiki 知识库包：每天至多一份，按天去重。治理/编码轮 Phase 3 收尾调用。

    ⚠️ 按天去重的隐含前提：**当日首个包就是本轮起点**。
    跨会话时当日已有包可能是【上一轮的状态】（例：13:33 的包是治理前，17:00 治理已改库），
    此时该包**不能**充当本轮回滚点 → 需 --llmwiki-force 绕过去重另出一份治理后快照。
    """
    today = datetime.date.today().strftime("%Y%m%d")
    llm_pattern = os.path.join(ROOT, f"{LLM_PREFIX}{today}_*.tar.gz")
    existing = sorted(glob.glob(llm_pattern))
    if existing and not force:
        print(f"[llmwiki] 今日知识库备份已存在，跳过：{os.path.basename(existing[0])}")
        return 0
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    llm_out = os.path.join(ROOT, f"{LLM_PREFIX}{ts}.tar.gz")
    if not _make_tar(llm_out, src=_LLMWIKI, arcname="LLMWiki", exclude_fn=_exclude_llmwiki):
        return 1
    size_mb = os.path.getsize(llm_out) / (1024 * 1024)
    tag = "（强制，绕过按天去重）" if force and existing else "，排除 __pycache__"
    print(f"[llmwiki] 已生成知识库备份：{os.path.basename(llm_out)}（{size_mb:.1f} MB{tag}）")
    return 0


def _make_output() -> int:
    """output 包：每次必生成、始终是最新代码，生成后清理旧包。Step 3.8 在改码定稿后调用。"""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_out = os.path.join(ROOT, f"{OUTPUT_PREFIX}{ts}.tar.gz")
    if not _make_tar(output_out):
        return 1
    _prune_old_outputs(output_out)
    size_mb = os.path.getsize(output_out) / (1024 * 1024)
    print(f"[output] 已生成最新代码包：{os.path.basename(output_out)}（{size_mb:.1f} MB，排除 3rdDepend/obj/bin/.vs/.git）")
    return 0


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if any(a in ("-h", "--help") for a in args):
        print(USAGE)
        return 0

    # 模式解析：默认 --backup；--output 只出 output；--llmwiki 只出知识库包；--all 出前两者。
    # --llmwiki-force：知识库包绕过去重（跨会话时当日首包非本轮起点，见 _make_llmwiki_backup 注释）
    force_llm = "--llmwiki-force" in args
    if force_llm:
        args = [a for a in args if a != "--llmwiki-force"]
    if "--all" in args:
        do_backup, do_output, do_llmwiki = True, True, False
    elif "--output" in args:
        do_backup, do_output, do_llmwiki = False, True, False
    elif "--llmwiki" in args:
        do_backup, do_output, do_llmwiki = False, False, True
    else:
        # 无参数 / 显式 --backup / 未知参数一律按 backup 处理，不误出 output。
        do_backup, do_output, do_llmwiki = True, False, False
    if force_llm:
        do_backup, do_output, do_llmwiki = False, False, True

    if do_llmwiki and not os.path.isdir(_LLMWIKI):
        print(f"[llmwiki] 源目录不存在：{_LLMWIKI}", file=sys.stderr)
        return 1
    if (do_backup or do_output) and not os.path.isdir(SRC):
        print(f"[backup] 源目录不存在：{SRC}", file=sys.stderr)
        return 1

    if do_backup:
        rc = _make_backup()
        if rc != 0:
            return rc
    if do_output:
        rc = _make_output()
        if rc != 0:
            return rc
    if do_llmwiki:
        rc = _make_llmwiki_backup(force=force_llm)
        if rc != 0:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())