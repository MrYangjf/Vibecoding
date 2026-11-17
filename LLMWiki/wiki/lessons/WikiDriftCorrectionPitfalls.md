---
title: Wiki 批量漂移修正十一坑（行尾污染 / 换行符被吃 / 机器替换语义破损 / 横幅自伤 / 外部参考误改 / 非知识库文件混入 / Skill 双副本漂移 / 原档裁剪 / 行尾探针失真 …）
date: 2026-09-03
updated: 2026-10-30
tags: [教训, LLMWiki, 漂移, 工具脚本, Python, 行尾, 批量编辑]
status: active
---

# Wiki 批量漂移修正十一坑

> **章节导航**（本页 11 个坑，按遇到顺序编号；超长页请先按坑号定位再读）：坑一 行尾污染 · 坑二 joiner 丢失换行 · 坑三 机器替换语义破损 · 坑四 横幅自伤 · 坑五 正则无边界断言 · 坑六 掩码漏修 · 坑七 CRCRLF 断言盲区 · 坑八 非知识库文件混入 · 坑九 Skill 双副本漂移 · 坑十 原档裁剪失去唯一真相源 · 坑十一 行尾探针失真（`grep -c $'\r'`）

> 来源：2026-09-03 「修正 skill 与代码的漂移（刚从 GitHub 导下来）」一次性任务。
> 目标是把 wiki 中 144 处失效的 `.cs` 引用对齐到代码库现役状态，同时重写 `tools/drift_scan_precise.py`。
> 五坑全部踩中，其中三坑造成过需要 `git checkout --` 回退的实质损坏。
> 工具脚本口径与红线见 [[index/index]] §维护说明，漂移分诊词典见 `tools/drift_scan_precise.py` 文件头。

---

## 坑一：Python 默认换行把整库 LF 写成 CRLF → diff 从 90 行膨胀成整文件重写

### 现象

批量脚本用 `open(p).read()` + `open(p, "w").write(...)` 改写 17 个 wiki 页。
`git status` 干净、内容看起来也对，但 `git diff --numstat` 显示**每个文件的改动行数 ≈ 文件总行数**。

### 根因

`LLMWiki/wiki/` 下所有页面**在仓库中以 LF 存储**。`core.autocrlf=true` 只影响 checkout 后的工作区形态，
不改变入库内容。Python 的 `open(p, "w")` 在 Windows 上把 `\n` 翻译成 `\r\n`。

### 更糟的二次伤害

发现告警后**方向修反了**：先入为主地认为「Windows 项目就该是 CRLF」，于是又跑了一遍脚本把文件**转成** CRLF，
把污染固化下来。真正的判据只有一个——**与 `HEAD` 比对**：

```python
def fmt(b):
    crlf = b.count(b"\r\n"); lf = b.count(b"\n") - crlf
    return "CRLF" if crlf and not lf else ("LF" if lf and not crlf else "MIX(%d/%d)" % (crlf, lf))

orig = subprocess.run(["git", "show", "HEAD:" + rel], capture_output=True).stdout
assert fmt(orig) == fmt(open(rel, "rb").read()), "行尾与 HEAD 不一致"
```

### 规避

- 脚本批量编辑一律**按字节读写**：`open(p, "rb").read()` / `open(p, "wb").write(bytes)`。
- 收尾前用 `git diff --numstat` 扫一遍，**改动行数等于总行数的文件 = 行尾污染**。
- 已固化到流程规则：[[rules/KR-009-Grep-Default]] 之外的代码定位纪律，以及本页「规则条目：wiki 页以 LF 存储」。

---

### 规则条目：wiki 页以 LF 存储，批量改写必须按字节读写

- **规则要点（原 rules/KR-013）**：`LLMWiki/wiki/` 下的页在仓库内一律 **LF**；批量改写**按字节读写并原样回写行尾**，⛔ 禁止 `open(p).read()` + `open(p,"w").write()`（默认换行会把整库写成 CRLF，diff 从 ~90 行膨胀成整文件重写）。
- **判据**：改完 `git diff --numstat` 无「改动行数 ≈ 总行数」的文件；行尾同质性用**字节计数**判（`crlf` / `loneLF` / `CRCRLF` / BOM），⛔ 不用 `grep -c $'\r'`（见坑十一）。
- **归因**：整文件级 diff **不一定**是本轮造成 —— 先核对 `HEAD` blob 的行尾与净行数差（见下方「收尾判据」的例外甄别），是别人的未提交改动就只报告、不顺手"修"。

## 坑二：行区间替换的 joiner 默认成 `""` → 整页压成零换行的单行

### 现象

`people/UISpecialist.md` 从 1752 字节 / 61 行变成 **3150 字节 / 0 个换行符**——整个文件挤成一行，
Markdown 渲染出来是一坨。

### 根因

替换行区间时把 joiner 初始化为空串，只在探测到 CRLF 时才赋值：

```python
tail = ""
if raw.endswith("\r\n"):          # 该文件是 LF，条件不成立
    tail = "\r\n"
    lines = [l.rstrip("\r") for l in lines]
out = tail.join(new_lines)        # tail == "" → 全部拼接，换行符被吃掉
```

### 规避

joiner **必须由文件探测得出，且默认不能是空串**：

```python
tail = "\r\n" if raw.endswith("\r\n") else "\n"
out = tail.join(lines)
```

### 自检

改写后立刻断言 `open(p, "rb").read().count(b"\n") > 0`。这一条能同时抓住坑一和坑二。

---

### 规则条目：joiner 必须与 splitter 匹配

- **规则要点（原 rules/KR-014）**：行区间替换时，**joiner 必须由文件探测得出、默认不能是空串，且必须与 splitter 匹配**。
- **判据**：⛔ 不用 `text.split("\n")` + `"\r\n".join()` 处理 CRLF 内容（`split` 给每行留尾 `\r`，重拼即得 CRCRLF）；优先按字节 `raw.split(b"\n")` → `b"\n".join(parts)`，让 `\r` 留在片段内。
- **预防**：替换整行时新片段要**带上文件实测的终止符**（`new_bytes + nl`），否则该行变 loneLF、文件被判 MIXED；断言要比 `
` / `
` / `
` 三个计数**与原值**对比（不是与 0 对比）；检测到污染从备份整目录回滚重做，⛔ 不在污染件上二次改写。

## 坑三：机器直接替换旧名 → 四处语义破损，16 页全部回退

### 现象

第一版策略是「旧名 → 现役全路径」直接 `str.replace`。落盘后抽查发现：

| 破损 | 原文 | 替换后 |
|------|------|--------|
| 路径拼贴 | `Sub2UI/LLCamWorkJob.cs` | `Sub2UI/UIDesign/TabPage/ILCamPage.cs`（旧目录 + 新全路径） |
| 外部项目被改 | `PcomDeviceInterface/MachineStatusWork.cs` | `PcomDeviceInterface/MainDeviceControl/DeviceStatusWork.cs` |
| 自指 | `**已完全替代原 ILCamPage.cs**` | `**已完全替代原 UIDesign/TabPage/ILCamPage.cs**`（一句话里自己替代自己） |
| 目录树塞全路径 | `├── LLCameraSetting.cs` | `├── UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs`（树结构被破坏） |

### 规避

改为**标注式**：保留旧名原文，在其后追加 `（现役 \`X.cs\`）` 或 `（已移除（原因））`。
历史 ADR 页则改用**页面级横幅**（页首 `> ⚠️ 历史名称提示` 块），纯新增、零删除，最安全。

### 三条硬性子规则

1. **同行已有移除语义则跳过**：`NOTED_KEYWORDS = ("已移除","已删除","已废弃","已替代","删除","移除","废弃","淘汰")`，
   否则会产出「删除 `X.cs`（已移除）」这类自相矛盾的句子。
2. **围栏代码块内的命中必须转人工**：在块尾追加标注会挂到收尾的 ``` 上。只有行内代码体可以追加到闭合反引号之后。
3. **多对一映射要查撞车**：7 个 Stage 文件都映射到 `Stages.cs`，同行替换会产出重复标注。

---

### 规则条目：批量替换前查自引用

- **规则要点（原 rules/KR-016）**：连续两次全局替换时，**新串不得包含被替换串** —— 否则产出嵌套删除线垃圾（`~~~~[[old]]~~ → [[new]]~~`）。
- **判据**：批量替换前断言 `new.find(old) == -1`；已损坏则用**精确子串配对**修复，⛔ 停止继续跑全局替换。

## 坑四：横幅块内的旧名被判为「未登记的新漂移」→ 自伤

### 现象

横幅里写「各 `XxxStateMachine.cs` 已统一迁移为 `MainDeviceControl/DeviceWorkflow/XxxWorkflow.cs`」，
扫描器把这**两个通配占位名**判成「未登记的新漂移」，待修正数卡在 2 下不去。

### 双重修复

1. **文案层**：横幅里不写不存在的通配文件名，改列举真名（`MonitorCameraStateMachine` / `MotionControlStateMachine` / `LaserWeldHeadStateMachine`）。
2. **工具层**：给扫描器加横幅块豁免——从 `> ⚠️ 历史名称提示` 起的连续 `>` 行整体豁免：

```python
def banner_lines(lines):
    out, in_banner = set(), False
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith(">"):
            if HISTORY_BANNER in line:
                in_banner = True
            if in_banner:
                out.add(i)
        else:
            in_banner = False          # 非引用行结束该块
    return out
```

---

## 坑五：正则无边界断言 → 158 处误报，真实漂移被淹没

### 现象

旧版正则 `([A-Za-z0-9_]+\.cs)` 在更长的标识符中间就开始匹配：

- `FormMain.Designer.cs` → 截成 `Designer.cs`（144 处误报）
- `AdaWeldSystem.csproj` → 截成 `AdaWeldSystem.cs`（14 处误报）

### 规避

吃掉点号 + 双侧边界断言：

```python
cs_ref_re = re.compile(
    r"(?<![A-Za-z0-9_.])([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*\.cs)(?![A-Za-z0-9_.])")
```

### 配套：四点分诊词典

光靠正则降噪不够，命中后要分类，只有前两类计入「待修正」：

| 类别 | 含义 | 是否待修正 |
|------|------|-----------|
| `RENAMED` | 有明确现役对应文件 | 是 |
| `REMOVED` | 已删除，需注明原因 | 是 |
| `EXTERNAL` | 外部参考项目（`PcomDeviceInterface/` / `HonorMachineTest/`） | 否 |
| `SPECULATIVE` | 设想/demo 文件，从未落地 | 否 |

### 顺带修的红链误报

`wiki_audit.py` 的红链检测原来不跳过多行代码块与行内代码体，导致规范文本自身举例
（「不要写 `[[old]]→[[new]]`」）被判成 2 条真红链。修法是 `mask_code()`——用**等长空白**替换围栏块与行内代码体，
保持字符偏移与行号不变：

```python
_FENCE_RE  = re.compile(r"```.*?```", re.S)
_INLINE_RE = re.compile(r"`[^`\n]*`")

def mask_code(txt):
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))
    return _INLINE_RE.sub(blank, _FENCE_RE.sub(blank, txt))
```

---

## 坑六：掩码只修了红链检测，漂移检测漏修 → 原档命名被判「未登记的新漂移」

### 现象

2026-09-03 把新架构原档沉淀进架构页 §15 冲突表后，`drift_scan_precise.py` 报出
**待修正 9 处**，全是「未登记的新漂移」：

```
architecture/DeviceControlArchitecture.md:117  CommandCore.cs
architecture/DeviceControlArchitecture.md:231  CommandCore.cs
architecture/DeviceControlArchitecture.md:271  RollPressProcess.cs
architecture/DeviceControlArchitecture.md:329~333  RollPressProcess.cs ×4
architecture/DeviceControlArchitecture.md:964  CommandCore.cs
decisions/ADR-034-ArchitectureRawSource.md:29  RollPressProcess.cs
```

但**这 9 处全部写在反引号代码体内**，是明确的历史名/原档名引用，不是真实引用。

### 根因

坑五里修的 `mask_code()` **只加进了 `wiki_audit.py` 与 `lint_scan.py`**，
`drift_scan_precise.py` 从头到尾没有掩码——三个脚本各自实现了一遍链接解析，
修的时候漏了一个。分诊词典再精细也拦不住「反引号里的名字」。

### 双重修复

1. **补掩码**：把同一份 `mask_code()` 移植进 `drift_scan_precise.py`，
   扫描时 `cs_ref_re.finditer(mask_code(line))`。
2. **补原档命名词典** `RAW_SPEC_NAMES`：即使正文裸写原档名也豁免。

```python
RAW_SPEC_NAMES = {
    "CommandCore.cs",       # 原档对 DeviceStateApiCore/CommandTable.cs 的命名
    "RollPressProcess.cs",  # 外部参考项目 PcomDeviceInterface 的工序实现
    "AssemblyProcess.cs",
    "DeviceStateMachineBase.cs",
}
```

### 顺带修的第二个 bug：外部路径前缀只匹配一级目录

原判定 `any(p + fname in line for p in EXTERNAL_PREFIXES)` 对多级路径失效——
`PcomDeviceInterface/Work/Process/RollPressProcess.cs` 里根本不含子串
`PcomDeviceInterface/RollPressProcess.cs`。改为先取出紧邻文件名的完整路径前缀再判：

```python
def is_external_ref(line, fname):
    for m in re.finditer(
            r"(?<![A-Za-z0-9_.])((?:[A-Za-z0-9_]+/)+)" + re.escape(fname)
            + r"(?![A-Za-z0-9_.])", line):
        if m.group(1).startswith(EXTERNAL_PREFIXES):
            return True
    return False
```

### 规避

**掩码是安全网，不是免检证。** 加掩码后「已标注」从 119 处降到 16 处（103 处本就
在反引号内），必须反过来抽查被掩码的名字，确认没有掩盖真实漂移：

- 反引号内引用的 .cs 名去重 181 个，其中代码库不存在的 62 个
- 逐个分类后确认全部属于：历史名（已登记且页面已加注）/ 占位名（`X.cs`、
  `XxxWorkflow.cs`、`Designer.cs`）/ 外部 SDK（`Zmcaux.cs`、`MVCamera.cs`、
  `Form1.cs`）/ 原档命名

修改扫描器后，**必须重跑并人工过一遍被新增豁免规则吃掉的名字**，否则「待修正 0 处」
可能只是把问题藏起来了。

---

## 坑七：`split("\n")` + `"\r\n".join()` 把 CRLF 写成 CRCRLF，而断言恰好抓不住（2026-09-11）

### 现象

批量订正 35 个 ADR 页的 frontmatter `title` 时，脚本读入后 `text.split("\n")` 切行、
再用 `"\r\n".join(lines)` 重组。落盘后每页 `git diff --numstat` 显示**改动行数 = 文件总行数**，
`repr()` 一看行尾全是 `\r\r\n`（CR CR LF）——CRLF 被多加了一遍。

### 根因

`split("\n")` 切出的每段**仍带着行尾的 `\r`**，`"\r\n".join()` 又在段间插入 `\r\n`，
每个行尾遂变成 `\r` + `\r\n` = `\r\r\n`。这是坑二的**镜像变体**：坑二是 joiner 默认成了空串（太短），
坑七是 joiner 与 split 不匹配（重复）。

### 更隐蔽的一点：断言盲区

收工断言写的是 `count(b"\r\n") == 原值`。但 `b"\r\r\n".count(b"\r\n")` 恰好等于 **1**（非重叠匹配），
与原始 CRLF 的计数**完全一致**——于是断言全绿，污染照旧入库。**"计数相等"证明不了"内容相同"。**

### 规避

- **行终止符全程不重建**：按字节操作，`parts = raw.split(b"\n")`、重组 `b"\n".join(parts)`——
  `\r` 始终留在段内，天然保真。比 `splitlines(True)` 更稳（后者会在 `\v`/`\f`/`\u2028` 处额外断行）。
- 断言改为**三重**：`count(b"\r\n")`、`count(b"\r\r\n")`、`count(b"\n")` 均须与原值一致；
  更强的是直接断言「除目标行外逐段字节相等」。
- 收尾判据补一条：**`b"\r\r\n"` 计数不得增加**（而非写死为 0，见下）。
- 出错后的正确动作：**从备份整目录回滚再重做**，不要在污染文件上二次改写。

### 附带发现

`ADR-016` / `ADR-024` 两页**原生**就各含 1 处 `\r\r\n`（历史遗留的裸 CR 混排），
所以断言不能写死 `== 0`，必须与原值比对——否则会误报成"本次污染"，
按坑三的教训，误报会诱导出错误的"修复"。

---

## 坑八：非知识库文件混入 `wiki/` 与 `raw/`（2026-09-12）

### 现象

全库卫生复查在两层都挖出了"不属于知识库"的文件：

| 位置 | 残留物 | 来源 |
|---|---|---|
| `scripts/` | `_tmp_api_dump.py`、`__pycache__/csharp_review.cpython-313.pyc` | 一次性脚本与 Python 字节码缓存，**已误入库** |
| `raw/mecavision/` | 厂商 SDK 的 `bin/obj` 与全部示例 `.exe/.pdb/.tds`（合计 34 MB） | 解压归档时连编译产物一起入库 |
| `raw/codebase/` | 0 字节空目录 | 早期规划目录，内容从未落地 |
| `raw/tools/` | `crg_build.py` | **已退役**的 code-review-graph 工具脚本 |
| `AGENTS.md:5` | 引用不存在的 `tools/KarpathyWikiManager.html` | 建库期的可视化工具，早已移除 |

### 根因

1. **仓库从无 `.gitignore`** —— `bin/`、`obj/`、`__pycache__/`、`*.pyc`、`*_backup_*.tar.gz` 全靠手工避免，
   而每轮 Phase 2 都会新建 `_tmp_*.py`，`raw/` 解压归档又会带进构建产物。
2. **退役工具只清文档、不清脚本** —— code-review-graph 已于 2026-08-19 退役、`guides/Project-Tools.md` §1 立了墓碑，
   但 `raw/tools/crg_build.py` 与 `raw/skills/.../05-Tools/CodeGraph.md` 作为物理文件留了下来；
   删这类文件后，`wiki/index/index.md` §十「来源索引」里的源文件行会变成悬空登记。

### 规避

- **新仓库先建 `.gitignore`**（本仓库 2026-09-12 补建），至少覆盖
  `bin/ obj/ [Dd]ebug/ [Rr]elease/ *.pyc __pycache__/ .vs/ *_backup_*.tar.gz _tmp_*.py`。
  ⚠️ `.gitignore` 只对**未跟踪**文件生效；已入库的需先物理删除（用普通 `rm`，**禁用 `git rm`**）。
- **删物理文件 → 三步收尾**：① 删文件；② 清 `wiki/index/index.md`「来源索引」中的对应行；③ 全库 Grep 残留引用。
- **`raw/` 是只读真相源，但不是免责区** —— 归档带进的 `bin/obj` 仍属非知识库文件。
  清理原则：**只删编译产物，保留厂商 SDK / Drivers / Document 与全部示例源码**。
  用「扩展名白名单（`.exe .pdb .tds .ilk .exp .cache`）+ 目录名（`bin obj`）」双条件，
  先 dry-run 打印体积分类表并核对**源码计数不变**（本次 cs93/h159/cpp103/vb47 前后一致），再执行。
- **目录名乱码**（解压 GBK/UTF-8 错配，如 `MecaVision_SDK+²¦¦+¦-Á+¸+-ÁÁ`）：
  用 Python 的 `os.listdir` 取到准确名后 `os.rename` 订正，**不要用 shell glob**（非 ASCII 路径易二次损坏）。

### 规则条目：定向清扫前先全库普查

- **规则要点（原 rules/KR-021）**：跨库改写某符号 / 路径 / 模式前，先用**最宽可用模式** Grep **整个仓库根**，再与脚本白名单求差集 —— **脚本白名单不是真相**（实测漏掉 15 个文件 / 54 行）。
- **判据**：差集必须逐文件处置：现行事实页**就地改写**；`decisions/` 历史页只加**就地演进标注**，⛔ 不改写正文。

### 规则条目：wiki 下只放 Markdown，工作区根也要清

- **规则要点（原 rules/KR-022）**：`wiki/` 下**只放 Markdown**；会话临时产物（`_tmp_*.py` / `_tmp_*.txt` / `*_out.txt` / `*.pyc` / `__pycache__/` / `*.bak`）同样要清 —— **落在工作区根的散落文件链接型扫描器永远看不见**，必须每轮显式删除。
- **判据**：`find wiki -type f ! -name "*.md"` 为空；按文件名前缀清工作区根（见下方「知识库卫生判据」）。

## 坑九：Skill 双副本漂移——版本号相同、内容不同（2026-09-12）

### 现象

`~/.workbuddy/skills/vibecoding-llmwiki/SKILL.md`（用户级，Skill 工具实际加载的那份）与
`LLMWiki/skills/vibecoding-llmwiki/SKILL.md`（仓库副本）**版本号同为 v1.6.0，内容却差 4 行**——
仓库副本的 原 rules/KR-013（已并入 lessons/WikiDriftCorrectionPitfalls）/14 还是旧短版，Tier 2 仍列 09-09 重排前的旧 ADR 号。

### 根因

改编号 / 补规则的批量操作只改了用户级副本，忘了同步仓库副本。**相同的版本号掩盖了内容漂移**。

### 规避

- **两副本必须字节一致**：`diff <(sed 's/\r$//' A) <(sed 's/\r$//' B)` 应为空；
  以**用户级**（实际被加载的那份）为准覆盖仓库副本。
- 两副本当前行尾均为 **CRLF + BOM**，直接 `cp` 覆盖即可（勿用会重建行尾的脚本）。
- 改编号时按记忆清单同步 **5 处**：`logs/` + `tools/` + 代码注释 + **skills 两副本** + `.workbuddy/memory/`。

---

## 坑十：裁撤厂商原档前未定位「唯一真相源」→ 差点删掉全库仅存的原生接口声明（2026-09-14）

### 现象

裁剪 `raw/mecavision/` 的 `Demo/` 示例（12 种语言 / 26 MB，本项目只用 C#）时，最初的判断是
「留着 C# 就够，其余全删」。实际勘察后发现：**全库唯一的 C 原生接口声明藏在 `Demo/VC++/Include/`**
——`CameraApi.h`（328 KB，`extern "C"` 全部 API）、`CameraApiDefine.H`（枚举·结构体）、
`CameraStatus.h`（错误码）等。而**厂商 `SDK/` 目录里一个头文件都没有**（`.Interface` 后缀看着像头文件，
实为 PE 二进制插件）。若按原判断直删，C# 侧的 `MVSDK.cs` 就失去了可回溯的 C 原文基线。

### 根因

1. **按「语言」筛选，而非按「内容唯一性」筛选**：示例目录的语言归属 ≠ 资料价值归属；
   厂商常把整个 `Include/` 通用头文件**搭在某个语言的 demo 里分发**。
2. **后缀误导**：`.Interface` 被当成接口声明；`.h` 被当成 demo 私有文件。
3. **未做跨目录去重核查**：同一组头文件在 `Demo/VC++/Include`、`Demo/QT/Include`、`Demo/QT5/Include`
   各存一份（md5 相同），按语言全删时会连带删光所有副本。

### 规避

- **删任何原档目录前，先做「唯一性扫描」**：
  1. 列出待删目录与保留目录的**文件类型分布**（按扩展名 count），找出手册/头文件/协议定义这类
     「非示例」资产；
  2. 对候选关键文件（`.h`/`.hpp`/`.idl`/`.proto`/`*.pdf`/`*.chm`）做 **md5 跨目录去重**，
     确认保留侧是否已有同内容副本；
  3. 校验候选文件**是不是真文本**（`head -c 2` 看是否 `MZ`/`PK` 等二进制魔数）——
     后缀不可信。
- **抽存优于齐删**：把原语声明类文件集中到语义化目录（本次 = `MecaVision/SDK/Include/`，
  与它们描述的 DLL 同处），再删其余。
- **删前必须能说清「删掉的东西里有没有不可再生内容」**；说不清就先只做只读清单，交给用户拍板。

### 本次结论（可作后续模板）

| 保留 | 理由 |
|---|---|
| `Demo/C#/`（`MVSDK.cs` 6884 行） | 本项目技术栈，唯一官方封装源 |
| `SDK/Include/` 六头文件（**从 `Demo/VC++/` 抽入**） | 全库唯一的 C 原生接口声明基线 |
| `SDK/`、`SDK/X64/`、`Drivers/`、`Document/` | 运行库 / 驱动 / 官方 CHM 手册 |

删除 10 种语言示例 + VC++ MFC 样板：26.07 MB → 1.29 MB；`MecaVision/` 87 MB → 61 MB。

---

## 坑十一：用 `grep -c $'\r'` 判行尾 → ANSI-C 未展开，静默统计成「含字母 r 的行数」（2026-09-16）

**现象**：本轮开工时用一个 for 循环批量读 11 个 wiki 页的行尾，`grep -c $'\r' "$f"` 对**每一个**文件都返回与总行数相等的值，于是全部判为「纯 CRLF」。后用 Python 字节计数复核，发现其中 **8 页其实纯 LF**、仅 5 页纯 CRLF——初始判断**整体错了一半**。

**根因**：本环境的 Git Bash shim（`shell-runtime-bash-env.sh`）**不展开 ANSI-C 引用**：`$'\r'` 没有被替换成 CR，而是**原样两个字符** `\r` 传给 grep；GNU grep 又把 `\r` 解释为**字面字母 `r`**。于是该命令实际是「统计**含字母 r 的行数**」——中文页里几乎每行都含 `r`（英文字母、变量名、`[[链接]]`），结果≈总行数，看起来就像「全是 CRLF」。

**最小复现（实测）**：

```
printf 'abc\ndef\n'     > _t_lf.txt     # 真 LF
printf 'abc\r\ndef\r\n' > _t_cr.txt     # 真 CRLF
grep -c $'\r' _t_lf.txt   # -> 0  (exit 1)
grep -c $'\r' _t_cr.txt   # -> 0  (exit 1)   ← 明明有 CR，却报 0
od -c _t_cr.txt           # -> a b c \r \n d e f \r \n   ← 真相
```

**正确做法**：行尾 / BOM 一律用 **Python 字节计数**或 `od -c`，禁用 `grep -c $'\r'`：

```python
b = open(p, 'rb').read()
crlf   = b.count(b'\r\n')
bare   = b.count(b'\n') - crlf
cr     = b.count(b'\r') - crlf
crcrlf = b.count(b'\r\r\n')
bom    = b[:3] == b'\xef\xbb\xbf'
```

判据：**文件内部均质**（`crlf == 0` 或 `bare == 0`，不得混存）、`crcrlf == 0`；工作区 LF / CRLF 混存是**既有状态**（`core.autocrlf=true` 下均归一为仓库 LF），**不是本轮污染**，报告即可、不要「修」。

> **同族误区**：凡「用 shell 内建做二进制特征判定」都值得先证伪一次——同族还有 `grep -n "^using"` 被 **UTF-8 BOM** 吃掉首行（2026-09-16 实证，见 [[lessons/CSharp-Language-Pitfalls]]）、`\>` 在 BRE 里是**词尾断言**而非字面 `>`（SKILL.md 原 rules/KR-017（已并入 lessons/WikiDriftCorrectionPitfalls））。

### 规则条目：验 blockquote 必须用固定串匹配

- **规则要点（原 rules/KR-017）**：验横幅 / blockquote 行一律用 `grep -nF`（固定串），⛔ 不用 `grep -n "^> ..."` —— BRE 里 `\>` 是**词尾锚点**不是字面 `>`，对 markdown blockquote 会**静默返回 0**。

## 收尾判据（可复制）

批量漂移修正收工前，逐条确认：

- [ ] `tools/drift_scan_precise.py` 输出「待修正 0 处」
- [ ] `tools/wiki_audit.py` 输出「红链 0 / 孤儿页 0 / 重复行 0 / 二级子目录 0」
- [ ] `git diff --numstat` 中**无**「改动行数 ≈ 总行数」的文件（行尾污染）
- [ ] 每个被改文件 `count(b"\n") > 0`（换行符未被吃）
- [ ] 每个被改文件 `count(b"\r\r\n")` **不超过原值**（坑七：CRLF 被加重）
- [ ] 例外甄别：个把文件整文件级 diff 可能是**仓库历史遗留**（blob 以 CRLF 入库，
      与其余页的 LF 不一致），用 `git -c core.autocrlf=false diff --numstat` 复核——
      关掉归一化后若骤降为个位数行，则与本轮改动无关，不要顺手"修"
- [ ] 覆盖式批量改写前**先整目录 tar 备份**；一旦发现污染，从备份回滚后重做，勿在污染件上二次改写
- [ ] 所有 `_tmp_*.py` 脚本已删除
- [ ] 新增行的语义抽查：无「已移除 + 现役」句式冲突、无外部项目路径被改、无目录树塞全路径

### 规则条目：整文件 diff 不自动是你的锅

- **规则要点（原 rules/KR-026）**：整文件级 `git diff --numstat` **不自动是本轮造成** —— 先查自己是否动过该文件。
- **判据**：比 `HEAD` blob 的行尾与净行数差（`git show HEAD:<path>` + 字节计数）；两侧同为 LF 而行数变动远超你的编辑量 ⇒ 来自**别的会话的未提交改动** —— **报告，不静默重排版**；只修自己写过的文件。

### 知识库卫生判据（2026-09-12 补，坑八/坑九）

- [ ] `find wiki -type f ! -name "*.md"` 为空（`wiki/` 下不得有非 Markdown 文件）
- [ ] 全库无 `_tmp_*` / `*.pyc` / `__pycache__/` / `*.bak` / `*~`
- [ ] `raw/` 下无 `bin/` `obj/` 与示例编译产物（`.exe/.pdb/.tds`）
- [ ] 无 0 字节空目录（`find <dir> -type d -empty`）
- [ ] 退役工具的**物理脚本**已删（不只是文档立墓碑）
- [ ] `wiki/index/index.md`「来源索引」中每条源文件路径 `os.path.exists == True`
- [ ] 全库无指向已删文件的引用（`grep -rn "<已删文件名>"`）
- [ ] `AGENTS.md` 目录树与实际目录一致、无死工具引用
- [ ] `.gitignore` 存在且覆盖构建产物 / 缓存 / 本地备份
- [ ] Skill 双副本 `diff` 为空（坑九）
- [ ] 行尾 / BOM 判定用**Python 字节计数或 `od -c`**，未使用 `grep -c $'\r'`（坑十一）

### 原档裁剪判据（2026-09-14 补，坑十）

- [ ] 待删目录已按**扩展名分布**扫描，找出 `.h/.hpp/.idl/.proto/*.pdf/*.chm` 等「非示例」资产
- [ ] 关键候选文件已做**跨目录 md5 去重**，确认保留侧是否已有同内容副本
- [ ] 候选文件已验**真实类型**（`head -c 2` 非 `MZ`/`PK`；后缀不可信）
- [ ] 抽存类文件已集中到语义化目录并逐个校验 md5（如 `SDK/Include/`）
- [ ] 删前能逐项说明「待删内容中无不可再生资料」；不能确定则只出只读清单交用户拍板
- [ ] 备份 tar 已核验**确实包含**待删内容（`tarfile.getnames()` 命中计数 > 0）
## 相关页面

- [[index/index]]
