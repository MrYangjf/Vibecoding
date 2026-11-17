---
title: ADR-069 分区容器统一（Panel 卡片内嵌 GridPanel 区格，TableLayoutPanel 退役）
date: 2026-10-14
updated: 2026-10-14
tags: [ADR, UI, 布局, GridPanel, TableLayoutPanel, 分区容器, 批K, 工艺设置]
status: accepted
---

# ADR-069：分区容器统一（Panel 卡片内嵌 GridPanel 区格）

> 业主 2026-10-14 批K 裁定三条：① 快捷设置分区 **AntdUI.Panel 内的 `TableLayoutPanel` 改为 `GridPanel`**；
> ② 原本**裸放置**的区内控件**补 `GridPanel` 按区域放置**；③ 一处错误形态——**`GridPanel → GridPanel → Panel` 反向嵌套**（`gridLaserZones` 挂单子 `gridLaserLaZone` 再挂 `panelLaserLa`）必须纠正。
> 本 ADR 与 [[decisions/ADR-062-InpageZoneGridPanelLayout]] 配套：078 定**页级分区**（GridPanel 排分区卡片），085 定**卡片区内**（GridPanel 排区内控件）。

## 背景

批K 落地 ADR-062 页级分区后，卡片区内仍是旧形态，三种混用：

1. **TableLayoutPanel**：`panelProcessDebug` 内 `tlpProcessDebug`（5 行 × 5 列，含 2 处 `SetColumnSpan`）——与页级 GridPanel 范式不一致；
2. **裸放置**：`panelQuickTa` / `panelQuickLa` / `panelQuickTracking` 内控件全部绝对定位，无区域结构；
3. **反向嵌套**：`gridLaserZones`(Grid) → `gridLaserLaZone`(Grid，仅 1 子控件) → `panelLaserLa`(Panel) —— 单子 GridPanel 无分区意义，且嵌套方向与「GridPanel 排 Panel 卡片」的 078 范式相反。

## 决策

### 一、嵌套链方向固定为「页级 GridPanel → 分区 Panel → 区内 GridPanel」

```
tabPage → gridZones(GridPanel, ADR-062 页级分区)
 → panelXxx(Panel 卡片, ADR-060 形态)
 → gridXxx(GridPanel, 本 ADR 区内控件分区)
 → 控件
```

⛔ **禁止** GridPanel 套 GridPanel 再放 Panel（`gridLaserLaZone` 已改名 `panelLaserLaZone` 且降级为 Panel，删 `Span`）。

### 二、区内 GridPanel 的 Span 语法（`:` 行高 + `;` 行 + 空格列）

> ⚠️ 下表为**首版 Span**，已同日被下方「三、行高与四列规范」**演进**——现行 Span 一律 60/40 行高 + 四列（TA/LA 5 Radio 拆 4+1）。容器与原形态列仍有效。

| 分区 | 容器 | ~~首版 Span~~（⚠️ 已被 §三 演进） | 原形态 |
|---|---|---|---|
| 功能启用 | `gridProcessDebug` | ~~`42:fill;52:165 95 165 95;…;34:fill`~~ | `tlpProcessDebug` |
| TA 指令 | `gridQuickTa` | ~~`42:fill;50:150 130 130 100 100;30:fill`~~ | 裸放 |
| LA 指令 | `gridQuickLa` | ~~`42:fill;50:118×5;30:fill`~~ | 裸放 |
| Tracking | `gridQuickTracking` | ~~`40:fill;fill`~~ | 裸放 |

### 三、行高与四列规范（2026-10-14 业主裁定补，二轮演进）

> ⚠️ **2026-10-15 三轮演进（业主裁定补，现行规范）**：区内 GridPanel 一律 —— **标题行高 40、控件行高 30、每一行最多四列、每个控件区域宽度 160**（标题/Tip 行整行 `fill` 单列例外；行数按需增加）。
> 下表 60/40 行高已废止，列结构（4+1 拆行等）仍有效，列宽 `fill` → `160`。

| 分区 | Span（现行 40/30 + 160） | 结构说明 |
|---|---|---|
| `gridProcessDebug` | `40:fill;30:160 160 160 160;30:160 160;30:160 160 160 160;30:fill` | 5 开关：r1 四列 / r2 两列 / r3 四列 / Tip 整行 |
| `gridQuickTa` | `40:fill;30:160 160 160 160;30:160;30:fill` | 5 Radio 拆 4+1（r2 单格） |
| `gridQuickLa` | `40:fill;30:160 160 160 160;30:160;30:fill` | 同上 |
| `gridQuickTracking` | `40:fill;30:160` | 标题 + 单内容行 |
| `gridLaserGalvo` | `40:fill;30:160 160 160 160;30:160 160;30:160 160;30:160 160` | 图形 4 按钮 / 演示+回零 / 手动宽度 / **振镜开关+标签（最后一行，ADR-070 补）** |

> ~~旧（2026-10-14 二轮）：标题 60 / 控件 40 / 列宽 fill~~ ⚠️ 已被 2026-10-15 三轮演进废止。

### 四、振镜块迁位（2026-10-14 业主裁定补，二轮演进）

LA 参数区（`panelLaserLa`）内「振镜（功能与图形）」块拥挤 ⇒ 迁入 `gridLaserZones` **原空白的第 4 格**（右下）：

- 新增卡片 `panelLaserGalvo`（ADR-060 §四 卡片形态）+ 区内 `gridLaserGalvo`
- 迁移 10 控件：`lblGalvoTitle` / `btnGalvoCircle|Eight|Line|Arc|Demo|Home` / `swEnableGalvoWeave` / `lblGalvoWeave` / ~~`lblGalvoState`~~（⚠️ 2026-10-15 业主在 VS 删除——图形状态已由按钮选中态与 `RefreshActionStates` 承担，`.cs` 中 `lblGalvoState.Text` 刷新行同步移除，现 9 控件）
- `.cs` 引用全部按控件名 ⇒ 换父容器零代码改动（纯 Designer）
- `gridLaserZones` 由「声明 4 格挂 3 控件」变 **4 控件满格**（原奇数分区留空条款不再适用于本页）

### 五、TableLayoutPanel → GridPanel 对照要点

| TableLayoutPanel | GridPanel |
|---|---|
| `ColumnStyles/RowStyles` 绝对像素 | Span 行首 `N:` 行高 + 列像素列表（实测逐格几何一致） |
| `Controls.Add(ctrl, col, row)` | 单参 `Controls.Add(ctrl)` + **逆序入格** |
| `SetColumnSpan(ctrl, n)` | ⛔ **无等价**（`_N` 不可用）⇒ 标题/Tip 改占**整行 `fill` 单列** |

## 关键约束

| 约束 | 说明 |
|---|---|
| ⛔ 逆序入格 | `Controls.Add` 顺序 = 视觉倒序（实测证实） |
| ⛔ 行高写在行首 `:` | `60:fill` 而非尾部 `-` 全局表（多容器行高各异时 `:` 更贴文档语义） |
| ⛔ `SetColumnSpan` 消失 | 换容器时必须一并删除，残留 = CS0649/编译错 |
| ⛔ 删/改容器四件套 | 实例化 + Suspend/Resume + 属性块 + 字段声明 **同批改**，漏一处编译失败 |
| ✅ `.cs` 零引用 | 实测 `tlpProcessDebug` 等容器在代码后置零引用 ⇒ 纯 Designer 改动 |
| ⚠️ 残留 TLP 属后续批 | `tbPanelAdaparam`（批M 自适应页）、`tbpanelweldponts`（批L 线激光参数）不在本轮范围 |

## 后果

- **正面**：快捷设置 4 区容器形态与页级 GridPanel 范式统一；反向嵌套撤销，容器树层级一致；后续批L/M 填控件有统一形态参照
- **负面**：`GridPanel` 强排序心智（逆序入格）扩展到区内层；TableLayoutPanel 的格位合并能力在 GridPanel 缺失（用整行 `fill` 绕行）
- **中性**：控件名、事件订阅、`.cs` 全部零改动（纯容器替换）

## 验证

- **二轮（同日）**：探针 4 新结构（60/40 四列 + TA/LA 4+1 拆行 + 振镜网格 + 4 子格满挂）overlap=0；静态校验 37/37 PASS（判据自修 1 处：末行 Tip `fill` 单列属设计，S3 判据跳过首末行）
- **首轮**：实测（真实 `AntdUI.dll`，`guides/AntdUI-Reference` §2.x 语法）4 结构 overlap=0、行高列宽与原 TLP 几何一致；实测证实逆序；

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[decisions/ADR-062-InpageZoneGridPanelLayout]] —— 页级分区（本 ADR 的外层）
- [[decisions/ADR-060-P4UiLanding]] §四 —— 分区卡片 Panel 形态
- [[api/ProcessControlPage]] —— 消费方页面（分区容器表）
- [[lessons/DocDemoDllLookupOrder]] —— 文档→demo→DLL 参考顺序（本 ADR 据此先查 wiki-zh）
- [[guides/AntdUI-Reference]] §2.x —— Span 语法与 TableLayoutPanel 对照表
