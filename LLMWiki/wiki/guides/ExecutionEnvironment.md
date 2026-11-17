---
title: 执行环境事实（Windows + PowerShell + Python + Git）—— 每次动手前必读
date: 2026-10-30
updated: 2026-10-30
tags: [环境, 工具链, Python, PowerShell, Bash, 解释器, 路径, 事实]
status: accepted
---

# 执行环境事实（Windows + PowerShell + Python + Git）

> **本页是「环境事实表」**——记录**本机实际可用/不可用**的解释器、Shell、路径与工具。
> ⛔ **纪律**：动手前先查本页，**不要凭印象假设**「python 能用」「bash 能用」「路径是这样」。
> 每次因环境假设错误浪费的轮次，都应在此页补一条。

---

## 一、Python 解释器（⛔ `python` 命令不可用）

| 项 | 值 | 可用 |
|---|---|---|
| **首选解释器** | `D:\ProgramData\miniconda3\python.exe` | ✅ **3.13.13** |
| 备选（工具链专用） | `D:\ProgramData\miniconda3\envs\myenv\python.exe` | ✅ 3.12.13 |
| 备选（Trae 内置） | `C:\Users\yangjingfeng\.workbuddy\binaries\python\versions\3.13.12\python.exe` | ✅ 3.13.14 |
| **PATH 上的 `python`** | `C:\Users\yangjingfeng\AppData\Local\Microsoft\WindowsApps\python.exe` | ⛔ **0 字节占位符，不可用** |

**结论**：**永远用绝对路径**调用：
```powershell
& "D:\ProgramData\miniconda3\python.exe" "<脚本路径>"
```

⛔ 不要写 `python tools/xxx.py`（会命中 WindowsApps 占位符而失败）。

---

## 二、Shell（⛔ Bash 不可用）

| Shell | 状态 | 说明 |
|---|---|---|
| **PowerShell 5** | ✅ 默认 | 本机唯一可用的 Shell |
| **Bash / Git Bash** | ⛔ 不可用 | `ls` / `grep` / `head` / `tar` / `date` 均 `command not found`（PATH shim 损坏） |

**替代方案**：

| 需求 | ⛔ 不要用 | ✅ 改用 |
|---|---|---|
| 列目录 | `ls` | `Get-ChildItem` |
| 找文件 | `find` / `grep -r` | **Glob 工具** / `Get-ChildItem -Recurse` |
| 查内容 | `grep` | **Grep 工具** / `Select-String` |
| 读文件 | `cat` / `head` | **Read 工具** / `Get-Content -TotalCount N` |
| 打包 | `tar` | `python tools/backup_adaweld.py` |
| 时间戳 | `date` | `Get-Date -Format "yyyy-MM-dd HH:mm:ss"` |
| 写文件 | `cat > f` | **Write 工具**（PowerShell `>` 会写 UTF-16） |

⛔ **PowerShell 输出重定向坑**：`& $py x.py > out.txt` 产出 **UTF-16**，Read 工具报「binary file」。正确写法：
```powershell
& $py x.py 2>&1 | Out-File -FilePath out.txt -Encoding utf8
```

---

## 三、路径事实

| 路径 | 内容 |
|---|---|
| 工作区根 | `D:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\workbudddy` |
| 知识库根 | `workbudddy\Vicoding管理平台\LLMWiki\` |
| 代码根 | `workbudddy\AdaWeldSystem\` |
| 备份/出包落点 | **工作区根**（`backup_adaweld.py` 由 `__file__` 推导 ROOT） |
| 工具脚本 | `workbudddy\Vicoding管理平台\LLMWiki\tools\` |

⛔ **备份包不出工作区根**；⛔ **禁止手搓 tar**（一律走 `backup_adaweld.py`）。

---

## 四、Git

⛔ **LLMWiki 目录当前不是 Git 仓库**（`workbudddy/.git` 亦不存在）⇒ 本轮治理**无版本回退保障**，改前必须自备备份。
- `LLMWiki_backup_YYYYMMDD_HHMMSS.tar.gz`（工作区根）= 唯一的回滚点。
- 远程同步走 [[guides/SourceBackup-GitHub]]（双仓：代码 + 知识库，SSH over 443）。

---

## 五、脚本工具链（知识库治理用）

全部位于 `Vicoding管理平台\LLMWiki\tools\`，**路径一律由 `__file__` 推导**，可在任意 CWD 下运行：

| 脚本 | 用途 |
|---|---|
| `wiki_format.py` | **格式校验**（WikiPageFormatSpec 的机械判据） |
| `wiki_index_build.py` | 重建 index.md 骨架与分类表 |
| `wiki_route_rebuild.py` | 由 `routes.tsv` 重建速查路由表 |
| `wiki_log.py` | log 条目追加（时间戳自动取）+ **log 截断唯一入口**（`truncate`，含按日归档与 INDEX 重建） |
| `wiki_log_tidy.py` | log 排序 / 表头修正 / 归档索引（`truncate` 仅委托 `wiki_log.py`） |
| `wiki_normalize.py` | ADR / lessons 页 frontmatter 与章节骨架规范化 |
| `wiki_split.py` | 大教训页按主题拆分 |
| `wiki_toc.py` | 超大页生成章节导航 |
| `adr_new.py` / `lesson_new.py` | ADR / 教训「先合并后新建」助手 |
| `wiki_audit.py` `lint_scan.py` `drift_scan_precise.py` `ingest_purity_scan.py` | 既有四扫描器 |

**调用范式**：
```powershell
$py = "D:\ProgramData\miniconda3\python.exe"
$T  = "d:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\workbudddy\Vicoding管理平台\LLMWiki\tools"
& $py "$T\wiki_format.py"
```

---

## 六、踩坑记录（每次环境错误都补一条）

| # | 现象 | 根因 | 正解 |
|---|---|---|---|
| 1 | `python x.py` 报 0 字节 / 无法运行 | PATH 命中 WindowsApps 占位符 | 用绝对路径 `D:\ProgramData\miniconda3\python.exe` |
| 2 | `ls`/`grep`/`tar`/`date` 全部 not found | Bash PATH shim 损坏 | 用 PowerShell + Glob/Grep/Read 工具 |
| 3 | `& $py x.py > out.txt` 后 Read 报「binary file」 | PowerShell `>` 写 UTF-16 | `2>&1 \| Out-File -Encoding utf8` |
| 4 | 改页后整库 diff 膨胀 | Python 默认换行把 LF 写成 CRLF | 按字节读写 + 保持行尾同质（见 [[lessons/WikiDriftCorrectionPitfalls]]） |
| 5 | frontmatter 解析全部失败（判定「无 frontmatter」） | BOM 文件首行是 `\ufeff---`，`strip()` 后不等于 `---` | 判定前先剥 BOM |
| 6 | 脚本看似成功但字段未补 | 同上：BOM 导致解析分支未进 | 加 BOM 专项自检 |

---

## 七、相关页面

- [[standards/WikiPageFormatSpec]] —— 页面格式契约与增长规则
- [[guides/Project-Tools]] —— 项目工具与流程手册
- [[lessons/WikiDriftCorrectionPitfalls]] —— 批量改页的十一个坑
- [[project/vibecoding-workflow]] —— 工作流规范（Phase 0~4）
