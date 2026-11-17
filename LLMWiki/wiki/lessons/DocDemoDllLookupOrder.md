---
title: 控件与 SDK 用法参考顺序：文档 → demo → DLL
date: 2026-10-14
updated: 2026-10-30
tags: [教训, AntdUI, 英莱, 监控相机, demo, DLL侦查, 参考顺序, 知识检索]
status: active
source: 业主 2026-10-14 裁定（batch K 容器改造轮，反复踩同一错误后固化）
---

# 控件与 SDK 用法参考顺序：文档 → demo → DLL

> **业主 2026-10-14 裁定**：这是一个**一直犯的错误**——查控件/SDK 用法时跳过文档与 demo、直接上 DLL 反射侦查（或凭记忆写法），
> 顺序颠倒既慢又容易得出错误结论。固化检索顺序如下，编码前强制遵守。

## 一、AntdUI 控件写法（三级顺序，⛔ 不可跳级）

| 级 | 参考源 | 查什么 |
|---|---|---|
| ① | **源码文档** `raw/AntdUI/wiki-zh/Control/<控件>.md` | 属性/事件/方法的官方定义、语法说明 |
| ② | **使用 demo** `M3/AntdUI使用demo/AntdUI-Demo-main/Views/*.Designer.cs` | 真实工程里的标准写法（如 GridPanel 语法说明原文就写在 demo 的 `label1.Text` 里） |
| ③ | **DLL 侦查**（反射 / `#US` 堆字面量 / PowerShell 加载 `3rdDepend\AntdUI.dll` 探针） | 仅当前两级**查不到**、或需**实测运行期布局行为**时才用 |

**为什么 DLL 必须排最后**：
- DLL 反射只暴露「有什么」，不暴露「怎么用」——拿属性存在性推断渲染/布局行为正是历史踩坑机制（见 [[guides/AntdUI-Reference]] §4.2 反证法警示）；
- 探针（判据库 §7.3）的定位是**验证已由文档/demo 得出的结论**，不是**代替**文档得出结论；
- ⚠️ 与 [[guides/AntdUI-Reference]] §2.2 旧表述「权威源顺序 ①demo ②wiki-zh ③DLL」的关系：**首位两版互换（本裁定以源码文档为先），「DLL 永远最后」两版一致**——如遇具体控件 demo 的自带说明与 wiki 文档冲突，以更具体者为准并记录。

## 二、设备 SDK（英莱线激光、监控相机等）：先 demo，后 DLL 侦查

| 级 | 参考源 | 本项目实例 |
|---|---|---|
| ① | **厂商 demo**（`raw/<vendor>/` 下官方示例源码） | 英莱：校准框公式、回调注册顺序（见 [[lessons/IntelligentLaser-Pitfalls]]）；麦格威：连接/取流范式 |
| ② | **DLL 侦查**（反射/导出表/探针） | demo 没覆盖的能力才查 DLL |

**设备 SDK 没有「① 源码文档」级时不硬造**：厂商 wiki/文档存在（如台达 `raw/delta/` 权威资料）则同样先于 demo；文档缺失则 demo 直接升为第①级。

## 三、违反本顺序的代价（已发生）

- **凭记忆/反证法推断 AntdUI 表头行为** → 误删三按钮 → 上机功能真空（ADR-056 两次裁定回滚，2026-10-10）；
- **不查 demo 直接猜 GridPanel Span 行为** → 「3 格写法末格拉伸」这类运行期行为官方 wiki 根本没写，只有 demo 示例 + 探针能证实（ADR-062）；
- 反复「先上探针后补文档」导致每轮重复侦查——**把已知结论沉淀为文档/demo 摘录，才是止血**。

## 四、门禁清单（编码前）

- [ ] 要用的 AntdUI 控件，是否已查过 ① wiki-zh 文档 ② 官方 demo？
- [ ] 是否把 DLL 侦查当作**结论验证**而非**结论来源**？
- [ ] 设备 SDK 用法是否先查了厂商 demo（`raw/<vendor>/`）？
- [ ] 侦查得出的**可复用结论**是否已回写 wiki（guides/lessons），避免下轮重查？

## 关联

- [[guides/AntdUI-Reference]] —— AntdUI 权威源顺序与 Span 语法（消费本教训的落点页）
- [[lessons/IntelligentLaser-Pitfalls]] —— 英莱相机 demo 优先实例
- [[lessons/StaticVerifierJudgements]] §7.3 —— 探针定位（验证，不代替文档）
- [[decisions/ADR-062-InpageZoneGridPanelLayout]] —— Span 行为以 demo+探针实测为准的裁定
## 相关页面

- [[index/index]]
