---
title: ADR-050 架构原档单一来源约定（raw/architecture）
date: 2026-09-02
tags: [决策, 架构, 知识库治理, 原档, 单一来源, 主控设计, 泳道图, ADR-050]
status: accepted
---

# ADR-050：架构原档单一来源约定（raw/architecture）

> **2026-09-02 接受**：用户指令——「将架构设计 xlsx 和 pdf 文件沉淀到知识库原档，保证不会错误，并且后续我只需要修改这些文件，来更新架构」。**2026-09-02（晚）扩充**：新增第 3 份原档 `焊接系统工作流程业务流向图.pdf`（业务状态流），原档 2→3。
> 本 ADR 确立**架构知识的原档优先原则**：wiki 架构页从属于原档，不再是架构变更的第一入口。

## 背景

设备控制架构此前由 AI 逆向源码总结写入 wiki（[[architecture/DeviceControlArchitecture]]），多轮迭代中出现对用户设计意图的理解偏差（状态模型、泳道调用链误读），返工成本高。

用户提供三份设计原档作为架构意图的直接载体：

| 原档 | 内容 | 判读方式 |
|---|---|---|
| `raw/architecture/主控设计.xlsx` | 文件/职责/状态枚举定义表：DeviceStateApiCore 基类 2 文件（三态枚举 + 六抽象契约）、DeviceWorkflow 5 流程、DeviceControlWork / DeviceStatusWork 职责与参考实现（`PcomDeviceInterface/MachineControlWork.cs` / `MachineStatusWork.cs`） | openpyxl 直读文本 |
| `raw/architecture/焊接设备工作流程图.pdf` | 主从架构时序泳道图（9 泳道）：MainPage → DeviceControlWork / DeviceStatusWork → 5 workflow 的 Initialize / ConnectOn / ResetWorkTime+FlowProcess 心跳 / ResetMachine / StartMachine / StopMachine / EStopMachine 调用关系 | **纯图形矢量 PDF，无文本层**，判读以 pymupdf 150dpi 渲染图 `raw/architecture/page_0.png` 为准 |
| `raw/architecture/焊接系统工作流程业务流向图.pdf` | 整机业务状态流图：主链 NoReset→Reseting→Reset OK→Running→PreWorking/WeldWorking→Stop/Alarm + 三条横向常驻通道（通讯/命令-IO-Pose/EMG-故障树） | 矢量 PDF 有文本层，可 pymupdf 坐标化提取；渲染辅助图 `业务流向图_overview.png` |

## 决策

### 1. 原档位与唯一修改入口

- 原档固定存放于 `LLMWiki/raw/architecture/`：`主控设计.xlsx` + `焊接设备工作流程图.pdf` + `焊接系统工作流程业务流向图.pdf`。
- **KB 内这份副本是唯一修改入口**：用户后续架构变更只改这三份文件（KB 内副本），工作区根目录 / 飞书文档中的同名文件视为沉淀当日快照，不再跟踪。
- `raw/architecture/` 下**只放原档与渲染辅助图**（PNG），不放衍生 markdown——衍生内容一律写入 wiki 页。

### 2. 架构更新流程（原档驱动）

```
用户修改 raw/architecture/ 原档（三份中任意一份）
    ↓ 触发同步（用户告知 AI）
AI 重读原档（xlsx 全量 dump + PDF 重渲染判读）
    ↓
同步 wiki/architecture/DeviceControlArchitecture.md（以原档为准，源码为佐证）
    ↓
交叉更新受影响的 modules/ api/ standards/ lessons/ index 页
    ↓
tools/wiki_audit.py 全绿收口 + logs/log.md 记录
```

### 3. 冲突裁决顺序

**原档 > wiki 架构页 > 源码注释**。源码实现与原档不一致时，视为「代码待改」或「原档待更新」两种可能，**必须交由用户裁定**，AI 不得擅自单方改码或改原档。

### 4. 与既有治理约定的关系

- 本约定只收口**架构**原档；`raw/knowledge/` 下既有原档（如 `AdaWeldSystem_Wiki.md`）维持原状，不强制迁移。
- 架构页仍遵守「不按 V1/V2/V3 代际描述、只维护当前事实」（页头声明）；本 ADR 是该原则的上游保障——变更从 wiki 入口前移到原档入口。
- [[decisions/ADR-049-ThreeStateModelRefactor]] 记录的状态模型语义变更即首次按本流程落地（原档 xlsx Sheet1 E 列枚举定义 → 架构页 §1/§3）。

## 影响文件

- 新增：`raw/architecture/主控设计.xlsx`、`raw/architecture/焊接设备工作流程图.pdf`、`raw/architecture/page_0.png`（渲染辅助）；2026-09-02（晚）追加 `焊接系统工作流程业务流向图.pdf` + `业务流向图_overview.png`
- 修改：`wiki/architecture/DeviceControlArchitecture.md`（页头 source 字段声明原档入口）
- 登记：`wiki/index/index.md`（raw 原档区 + 本 ADR 条目）
