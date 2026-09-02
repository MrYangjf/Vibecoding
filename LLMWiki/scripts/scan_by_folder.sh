#!/usr/bin/env bash
# 按顶层文件夹扫描 AdaWeldSystem 的 C# 代码精简问题（进度可见 + 卡死可定位）
# 用法: bash scripts/scan_by_folder.sh [ROOT]
#   ROOT 省略时默认 "D:/A-A-项目类/04_研发项目/MRDF-2608 自适应焊接系统/workbudddy/AdaWeldSystem"
# 设计：逐顶层文件夹扫描，每文件夹打印 开始/完成 标记；单文件 timeout 30s 防卡死；
#       每文件夹汇总追加写入 scripts/scan_by_folder.tsv（中途中断也可看已完成部分）。
# 注意：检查脚本由 Windows 版 Python 执行，路径须为 Windows 风格（D:/... 或 D:\...），
#       不能用 MSYS 的 /d/... 形式（Python 无法打开）。故用 cygpath -w 转换。
set -u

PY_EXE="${PY_EXE:-C:/Users/yangjingfeng/.workbuddy/binaries/python/versions/3.13.12/python.exe}"

raw_dir="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_DIR="$(cygpath -w "$raw_dir" 2>/dev/null || echo "$raw_dir")"
SCRIPT="$SCRIPT_DIR/csharp_review.py"

ROOT="${1:-D:/A-A-项目类/04_研发项目/MRDF-2608 自适应焊接系统/workbudddy/AdaWeldSystem}"
ROOT_W="$(cygpath -w "$ROOT" 2>/dev/null || echo "$ROOT")"

# 排除的非源码顶层目录（UI / 厂商 SDK / 构建产物 / 资源）
EXCLUDE="UIDesign 3rdDepend bin obj deliverables Resources Properties"

[ -f "$SCRIPT" ] || { echo "未找到检查脚本: $SCRIPT" >&2; exit 1; }
[ -x "$PY_EXE" ] || { echo "未找到 Python: $PY_EXE" >&2; exit 1; }

RESULT_TSV="$SCRIPT_DIR/scan_by_folder.tsv"
: > "$RESULT_TSV"

echo "=== 按顶层文件夹扫描: $ROOT_W ==="
echo "结果将写入: $RESULT_TSV"
echo

overall_e=0; overall_w=0; overall_i=0; overall_f=0; overall_err=0

for dir in "$ROOT_W"/*/; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  # 跳过排除目录
  skip=0
  for ex in $EXCLUDE; do [ "$name" = "$ex" ] && skip=1 && break; done
  [ $skip -eq 1 ] && { echo "## [跳过] $name (非源码目录)"; continue; }
  echo ">> [开始] $name"
  fe=0; fw=0; fi_=0; ff=0; stuck=""
  while IFS= read -r f; do
    ff=$((ff+1))
    out=$(timeout 30 "$PY_EXE" "$SCRIPT" "$f" 2>&1)
    rc=$?
    if [ $rc -eq 124 ]; then stuck="$f"; break; fi
    summ=$(printf '%s\n' "$out" | grep -oE '共 [0-9]+ 项: [0-9]+ 错误 / [0-9]+ 警告 / [0-9]+ 提示')
    if [ -z "$summ" ]; then
      echo "!! [扫描异常] $f (rc=$rc, 疑似脚本报错)"
      overall_err=$((overall_err+1))
      continue
    fi
    e=$(printf '%s\n' "$summ" | grep -oE '[0-9]+ 错误' | grep -oE '[0-9]+')
    w=$(printf '%s\n' "$summ" | grep -oE '[0-9]+ 警告' | grep -oE '[0-9]+')
    i=$(printf '%s\n' "$summ" | grep -oE '[0-9]+ 提示' | grep -oE '[0-9]+')
    fe=$((fe+e)); fw=$((fw+w)); fi_=$((fi_+i))
  done < <(find "$dir" -name '*.cs' ! -name '*.designer.cs')
  if [ -n "$stuck" ]; then
    echo "!! [卡住] $name 在文件: $stuck (超时跳过, 已扫 $ff 个)"
  else
    echo "<< [完成] $name  文件=$ff  错误=$fe  警告=$fw  提示=$fi_"
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$ff" "$fe" "$fw" "$fi_" "$stuck" >> "$RESULT_TSV"
  overall_e=$((overall_e+fe)); overall_w=$((overall_w+fw)); overall_i=$((overall_i+fi_)); overall_f=$((overall_f+ff))
done

echo
echo "=== 汇总: 文件=$overall_f  错误=$overall_e  警告=$overall_w  提示=$overall_i  扫描异常=$overall_err ==="
echo "=== 文件夹排名(错误降序, 其次警告降序) ==="
sort -t$'\t' -k3,3nr -k4,4nr "$RESULT_TSV" | awk -F'\t' 'NR>0 {print $1"\t文件="$2"\t错误="$3"\t警告="$4"\t提示="$5}'
