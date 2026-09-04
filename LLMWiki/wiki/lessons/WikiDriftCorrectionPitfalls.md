---
title: Wiki 批量漂移修正五坑（行尾污染 / 换行符被吃 / 机器替换语义破损 / 横幅自伤 / 外部参考误改）
date: 2026-09-03
tags: [教训, LLMWiki, 漂移, 工具脚本, Python, 行尾, 批量编辑]
---

# Wiki 批量漂移修正五坑

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
- 已固化到工作流规范：[[project/vibecoding-workflow]] 核心规则 13。

---

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

## 坑三：机器直接替换旧名 → 四处语义破损，16 页全部回退

### 现象

第一版策略是「旧名 → 现役全路径」直接 `str.replace`。落盘后抽查发现：

| 破损 | 原文 | 替换后 |
|------|------|--------|
| 路径拼贴 | `Sub2UI/LLCamWorkJob.cs` | `Sub2UI/UIDesign/TabPage/ILCamPage.cs`（旧目录 + 新全路径） |
| 外部项目被改 | `PcomDeviceInterface/MachineStatusWork.cs` | `PcomDeviceInterface/MainDeviceControl/DeviceStatusWork.cs` |
| 自指 | `**已完全替代原 ILCamPage.cs**` | `**已完全替代原 UIDesign/TabPage/ILCamPage.cs**`（一句话里自己替代自己） |
| 目录树塞全路径 | `├── LLCameraSetting.cs` | `├── UIDesign/SubView/ILParamPage.cs`（树结构被破坏） |

### 规避

改为**标注式**：保留旧名原文，在其后追加 `（现役 \`X.cs\`）` 或 `（已移除（原因））`。
历史 ADR 页则改用**页面级横幅**（页首 `> ⚠️ 历史名称提示` 块），纯新增、零删除，最安全。

### 三条硬性子规则

1. **同行已有移除语义则跳过**：`NOTED_KEYWORDS = ("已移除","已删除","已废弃","已替代","删除","移除","废弃","淘汰")`，
   否则会产出「删除 `X.cs`（已移除）」这类自相矛盾的句子。
2. **围栏代码块内的命中必须转人工**：在块尾追加标注会挂到收尾的 ``` 上。只有行内代码体可以追加到闭合反引号之后。
3. **多对一映射要查撞车**：7 个 Stage 文件都映射到 `Stages.cs`，同行替换会产出重复标注。

---

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
decisions/ADR-035-ArchitectureRawSource.md:29  RollPressProcess.cs
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

## 收尾判据（可复制）

批量漂移修正收工前，逐条确认：

- [ ] `tools/drift_scan_precise.py` 输出「待修正 0 处」
- [ ] `tools/wiki_audit.py` 输出「红链 0 / 孤儿页 0 / 重复行 0 / 二级子目录 0」
- [ ] `git diff --numstat` 中**无**「改动行数 ≈ 总行数」的文件（行尾污染）
- [ ] 每个被改文件 `count(b"\n") > 0`（换行符未被吃）
- [ ] 所有 `_tmp_*.py` 脚本已删除
- [ ] 新增行的语义抽查：无「已移除 + 现役」句式冲突、无外部项目路径被改、无目录树塞全路径
