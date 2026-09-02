#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdaWeldSystem LLM Wiki 本地服务器
动态读取 LLMWiki/*.md 文件，通过 HTTP API 提供给 WikiBrowser.html。
无需预生成 wiki_data.js，数据始终是最新的。

用法:
  python wiki_server.py              # 默认 8080 端口
  python wiki_server.py --port 9000 # 自定义端口
  python wiki_server.py --wiki D:/path/to/LLMWiki  # 自定义 LLMWiki 路径
"""

import os
import sys
import json
import time
import mimetypes
import argparse
import urllib.parse
import webbrowser
import threading
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# ============ 配置 ============
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_WIKI_ROOT = SCRIPT_DIR.parent / "LLMWiki"
DEFAULT_PORT = 8080

# ============ 全局状态 ============
wiki_root = None


def find_wiki_root(custom_path=None):
    """定位 LLMWiki 目录"""
    if custom_path:
        p = Path(custom_path).resolve()
        if p.is_dir():
            return p
        raise FileNotFoundError(f"指定的 LLMWiki 路径不存在: {custom_path}")

    # 相对于 tools/ 的父目录下的 LLMWiki
    candidates = [
        SCRIPT_DIR.parent / "LLMWiki",
        SCRIPT_DIR / "LLMWiki",
        SCRIPT_DIR.parent / "vicoding管理平台" / "LLMWiki",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    raise FileNotFoundError(
        f"未找到 LLMWiki 目录。请确保 LLMWiki/ 在 tools/ 的同级目录下，\n"
        f"或使用时指定: python wiki_server.py --wiki <路径>"
    )


def scan_wiki_files(only_meta=False):
    """
    扫描 LLMWiki 目录下所有 .md 文件。
    only_meta=True: 只返回元数据（不含 content），用于轻量轮询。
    返回 (files_list, max_mtime, total_bytes)
    """
    files = []
    max_mtime = 0
    total_bytes = 0

    for dirpath, _dirnames, filenames in os.walk(wiki_root):
        for fname in filenames:
            if not fname.endswith(".md"):
                continue
            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, wiki_root).replace("\\", "/")
            name = os.path.splitext(fname)[0]
            stat = os.stat(full_path)
            mtime = stat.st_mtime
            if mtime > max_mtime:
                max_mtime = mtime
            size = stat.st_size
            total_bytes += size

            entry = {
                "path": rel_path,
                "name": name,
                "size": size,
                "modified": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
            }
            if not only_meta:
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        entry["content"] = f.read()
                except Exception as e:
                    entry["content"] = f"[读取失败: {e}]"
            files.append(entry)

    files.sort(key=lambda x: x["path"])
    return files, max_mtime, total_bytes


def build_api_response(only_meta=False):
    """构建 /api/files 的 JSON 响应"""
    files, max_mtime, total_bytes = scan_wiki_files(only_meta=only_meta)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "wikiRoot": str(wiki_root),
        "generatedAt": generated_at,
        "maxMtime": max_mtime,
        "totalFiles": len(files),
        "totalBytes": total_bytes,
        "files": files,
    }


# ============ HTTP Handler ============
class WikiRequestHandler(SimpleHTTPRequestHandler):
    """自定义请求处理器，支持 /api/* 端点"""

    def log_message(self, format, *args):
        """静默日志（只显示错误）"""
        if self.log_error:
            super().log_message(format, *args)

    def end_headers(self):
        """添加 CORS 头"""
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # ---- API: /api/status （轻量，只返回元数据）----
        if path == "/api/status":
            self._send_json(build_api_response(only_meta=True))
            return

        # ---- API: /api/files （完整数据）----
        if path == "/api/files":
            self._send_json(build_api_response(only_meta=False))
            return

        # ---- API: /api/file?path=xxx （单个文件内容）----
        if path == "/api/file":
            params = urllib.parse.parse_qs(parsed.query)
            rel_path = params.get("path", [None])[0]
            if not rel_path:
                self._send_error(400, "缺少 path 参数")
                return
            # 安全校验：防止路径穿越
            full = (wiki_root / rel_path).resolve()
            if not str(full).startswith(str(wiki_root.resolve())):
                self._send_error(403, "禁止访问路径之外的文件")
                return
            if not full.exists():
                self._send_json({"error": "文件不存在", "path": rel_path}, status=404)
                return
            try:
                with open(full, "r", encoding="utf-8") as f:
                    content = f.read()
                stat = os.stat(full)
                self._send_json({
                    "path": rel_path,
                    "content": content,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                })
            except Exception as e:
                self._send_error(500, f"读取失败: {e}")
            return

        # ---- 静态文件（默认行为）----
        # 如果请求的是 /，重定向到 /WikiBrowser.html
        if path == "/":
            self.path = "/WikiBrowser.html"
        super().do_GET()

    def _send_json(self, data, status=200):
        """发送 JSON 响应"""
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, code, message):
        """发送错误响应"""
        body = json.dumps({"error": message}, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


# ============ 主程序 ============
def main():
    global wiki_root

    parser = argparse.ArgumentParser(description="AdaWeldSystem LLM Wiki 本地服务器")
    parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT, help=f"监听端口 (默认 {DEFAULT_PORT})")
    parser.add_argument("--wiki", "-w", type=str, default=None, help="LLMWiki 目录路径 (默认自动检测)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="监听地址 (默认 127.0.0.1)")
    parser.add_argument("--open", action="store_true", default=True, help="启动时自动打开浏览器 (默认开启)")
    parser.add_argument("--no-open", dest="open", action="store_false", help="不自动打开浏览器")
    args = parser.parse_args()

    # 定位 LLMWiki 目录
    try:
        wiki_root = find_wiki_root(args.wiki)
    except FileNotFoundError as e:
        print(f"[错误] {e}")
        sys.exit(1)

    url = f"http://{args.host}:{args.port}/WikiBrowser.html?v={int(time.time())}"
    print(f"LLMWiki 目录: {wiki_root}")
    print(f"服务器地址: {url}")
    print(f"按 Ctrl+C 停止服务器")
    print("-" * 60)

    # 自动打开浏览器（强制新窗口，避免复用旧标签页的缓存状态）
    if args.open:
        def open_browser():
            import subprocess
            import platform
            if platform.system() == "Windows":
                # Windows: 用 start 命令强制开新窗口，绕过已有标签的缓存
                subprocess.Popen(["cmd", "/c", "start", "", url], shell=False)
            else:
                webbrowser.open(url)
        threading.Timer(0.5, open_browser).start()

    # 在 tools/ 目录下启动 HTTP 服务器
    os.chdir(SCRIPT_DIR)
    server = HTTPServer((args.host, args.port), WikiRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")


if __name__ == "__main__":
    main()
