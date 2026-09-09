---
title: ADR-032 架构原档单一来源约定（raw/architecture）
date: 2026-09-02
tags: [决策, 架构, 知识库治理, 原档, 单一来源, 主控设计, 泳道图, ADR-029]
status: accepted
---

> ⚠️ 历史名称提示：本页为**历史决策记录**，正文中的下列文件名为决策当时的旧名，
> 保留原文以留存上下文，现役对应如下：
>
> - `MachineControlWork.cs` → 现役 `MainDeviceControl/DeviceControlWork.cs`
> - `MachineStatusWork.cs` → 现役 `MainDeviceControl/DeviceStatusWork.cs`
>

# ADR-032 架构原档单一来源约定（raw/architecture）

> **2026-09-02 接受**：用户指令——「将架构设计 xlsx 和 pdf 文件沉淀到知识库原档，保证不会错误，并且后续我只需要修改这些文件，来更新架构」。**2026-09-02（晚）扩充**：新增第 3 份原档 `焊接系统工作流程业务流向图.pdf`（业务状态流），原档 2→3。
> **2026-09-04 扩为 3 份（md 版升为主源）**：用户指出 AI 对 PDF 的解析有欠缺，
> 人工将 `激光焊接系统业务流程图.pdf` 全量转写为 `激光焊接系统业务流程图20260904.md`（706 行）。
> **该 md 版取代 PDF 成为业务流原档的主源**，PDF 降级为图形备份（不再作为提取对象）。
> 原档集合现为 3 份：`主控设计.xlsx`（静态结构）+ `激光焊接系统业务流程图20260904.md`（业务流主源）
> + `激光焊接系统业务流程图.pdf`（图形备份）。
>
> **2026-09-03 收敛：3 → 2**。用户删除两份旧 PDF 与 3 张渲染辅助图，新增 `激光焊接系统业务流程图.pdf`（业务流 + 检查清单，PDF 含文本层）。**原档集合现为 2 份**：`主控设计.xlsx`（静态结构）+ `激光焊接系统业务流程图.pdf`（业务流 + 检查项）。
> 本 ADR 确立**架构知识的原档优先原则**：wiki 架构页从属于原档，不再是架构变更的第一入口。

## 背景

设备控制架构此前由 AI 逆向源码总结写入 wiki（[[architecture/DeviceControlArchitecture]]），多轮迭代中出现对用户设计意图的理解偏差（状态模型、泳道调用链误读），返工成本高。

用户提供设计原档作为架构意图的直接载体（**2026-09-03 收敛为现役 2 份**）：

| 原档 | 内容 | 判读方式 | 状态 |
|---|---|---|---|
| `raw/architecture/主控设计.xlsx` | 文件/职责/状态枚举定义表：DeviceStateApiCore 基类 3 文件（三态枚举 + 机器人指令表 + 基类 13 项契约）、DeviceWorkflow 5 流程（含各自差异化职责）、DeviceControlWork / DeviceStatusWork 的**成员级清单**（线程 / 私有方法 / 公共方法）与参考实现（`PcomDeviceInterface/Work/Process/StationProcess.cs` / `RollPressProcess.cs` / `AssemblyProcess.cs` / `MachineControlWork.cs` / `MachineStatusWork.cs`）；Sheet 名 `主控程序文件层级设计`，列：根文件夹 / 子文件夹·文件 / 文件 / 主要内容描述 / 实现 | openpyxl 直读（`data_only=True`；合并单元格 A2:A14 / B2:B7 / B8:B12 / C2:C3 / C4:C6，逐单元格 dump 比对差异） | **现役**，2026-09-03 15:37 修订 |
| `raw/architecture/激光焊接系统业务流程图.pdf` | 整机业务状态流 + 检查清单：上电 5×Connect On + 通讯 Open + IO Work → 三失败分支（Initialize / Reset / Pre-Working Fail）→ ResetMachine → Preworking 五项运行检查 → Working 四路焊接子流程 → 三终止分支（手动终止→Stop / 异常终止→Alarm / 焊接完成→StopMachine:Complete）→ 报警判断（故障树和代码）；旁路 EMG STOP → 子设备停机锁止 | **PDF 含文本层**，单页 928 字，`pypdf.PdfReader(...).pages[0].extract_text()` 全量提取，**无需渲染判读** | **现役**，2026-09-03 15:32 新增 |
| ~~`焊接设备工作流程图.pdf`~~ | ~~主从架构时序泳道图（9 泳道）~~ | 纯图形无文本层，曾以 `page_0.png` 渲染判读 | **2026-09-03 删除** |
| ~~`焊接系统工作流程业务流向图.pdf`~~ | ~~整机业务状态流图（旧版）~~ | 矢量 PDF 有文本层 | **2026-09-03 删除**（内容由新 PDF 取代并细化到检查项级） |
| ~~`page_0.png` / `业务流向图_overview.png` / `业务流向图_page0.png`~~ | 渲染辅助图 | — | **2026-09-03 删除** |

## 决策

### 1. 原档位与唯一修改入口

- 原档固定存放于 `LLMWiki/raw/architecture/`，**2026-09-03 起为 2 份**：`主控设计.xlsx` + `激光焊接系统业务流程图.pdf`。
- **KB 内这份副本是唯一修改入口**：用户后续架构变更只改这两份文件（KB 内副本），工作区根目录 / 飞书文档中的同名文件视为沉淀当日快照，不再跟踪。
- `raw/architecture/` 下**只放原档与渲染辅助图**（PNG），不放衍生 markdown——衍生内容一律写入 wiki 页。
- **原档删除即视为架构意图变更**：旧原档被删除时，AI 须在其取代者中核对内容覆盖情况，未被覆盖的部分（如旧泳道图的「类协作时序」）改以代码事实为准并在架构页标注，见 [[architecture/DeviceControlArchitecture]] §15。

### 2. 架构更新流程（原档驱动）

```
用户修改 raw/architecture/ 原档（2 份中任意一份）
    ↓ 触发同步（用户告知 AI）
AI 重读原档（xlsx 全量 dump + 与 git HEAD 版本逐单元格 diff + PDF 文本层提取）
    ↓ 产出「原档差异表 + 冲突裁定清单」
同步 wiki/architecture/DeviceControlArchitecture.md（以原档为准，源码为佐证）
    ↓ 原档已改代码未改的项登记到架构页 §15「待落地项与冲突裁定」
交叉更新受影响的 modules/ api/ standards/ lessons/ index 页
    ↓
**冲突项交用户裁定（ADR-029 §3），未裁定前不得改码**
    ↓
tools/wiki_audit.py + lint_scan.py + drift_scan_precise.py 全绿收口 + logs/log.md 记录
```

### 3. 冲突裁决顺序

**原档 > wiki 架构页 > 源码注释**。源码实现与原档不一致时，视为「代码待改」或「原档待更新」两种可能，**必须交由用户裁定**，AI 不得擅自单方改码或改原档。

### 4. 与既有治理约定的关系

- 本约定只收口**架构**原档；`raw/knowledge/` 下既有原档（如 `AdaWeldSystem_Wiki.md`）维持原状，不强制迁移。
- 架构页仍遵守「不按 V1/V2/V3 代际描述、只维护当前事实」（页头声明）；本 ADR 是该原则的上游保障——变更从 wiki 入口前移到原档入口。
- [[decisions/ADR-027-ThreeStateModelRefactor]] 记录的状态模型语义变更即首次按本流程落地（原档 xlsx Sheet1 E 列枚举定义 → 架构页 §1/§3）。

## 影响文件

- 2026-09-02 新增：`raw/architecture/主控设计.xlsx`、`焊接设备工作流程图.pdf`、`page_0.png`（渲染辅助）；当晚追加 `焊接系统工作流程业务流向图.pdf` + `业务流向图_overview.png`
- **2026-09-03 原档收敛（3 → 2）**：删除 `焊接设备工作流程图.pdf`、`焊接系统工作流程业务流向图.pdf`、`page_0.png`、`业务流向图_overview.png`、`业务流向图_page0.png`；新增 `激光焊接系统业务流程图.pdf`
- 修改：`wiki/architecture/DeviceControlArchitecture.md`（页头 source 与原档分工表改为 2 份；新增 §3.1 指令表、§6.1 子工作流差异化职责、§7.3.1 原档线程模型、§7.6 新业务主链、§7.7 五项运行检查、§7.8 四路子流程、§9 原档命名对照、§15 待落地与冲突裁定）
- 登记：`wiki/index/index.md`（raw 原档区 + 本 ADR 条目）
- 派生决策：[[decisions/ADR-029-RawDesignRefinement20260903]]（原档 9-03 细化内容的落地与裁定记录）
