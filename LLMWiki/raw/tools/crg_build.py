"""
crg_build.py — Windows 标准 code-review-graph 图谱构建包装脚本

标准用法（在项目根目录执行）:
    python "Vicoding管理平台/LLMWiki/raw/tools/crg_build.py" build --repo AdaWeldSystem

功能:
    1. 自动设置 CRG_PARSE_EXECUTOR=thread（Windows 多进程修复）
    2. 委托 code_review_graph.cli.main() 执行原始 CLI

版本适配:
    - v2.3.7: 移除 internal 模块 monkey-patch（模块已重构），--path 改为 --repo
    - v2.2.x: 旧版使用 internal.collect_all_files monkey-patch 和 --path 参数

Windows 兼容性:
    - 问题1：多进程 spawn 失败 → 设置 CRG_PARSE_EXECUTOR=thread
"""

import os
import sys

# ============================================================
# Step 1: 在 import 之前设置环境变量（Windows 必需）
# ============================================================
os.environ.setdefault("CRG_PARSE_EXECUTOR", "thread")

# ============================================================
# Step 2: 导入 code-review-graph 模块
# ============================================================
try:
    import code_review_graph.cli as cli
except ImportError:
    print("错误: 未安装 code-review-graph。请先执行: pip install code-review-graph")
    print("安装完成后重新运行此脚本。")
    sys.exit(1)

# ============================================================
# Step 3: 委托原始 CLI 执行
# ============================================================
if __name__ == "__main__":
    print(f"环境变量 CRG_PARSE_EXECUTOR={os.environ.get('CRG_PARSE_EXECUTOR', '未设置')}")
    print(f"Python 版本: {sys.version}")
    print("=" * 60)
    sys.argv[0] = "crg_build.py"
    cli.main()