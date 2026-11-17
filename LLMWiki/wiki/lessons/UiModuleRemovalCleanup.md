---
title: UI 功能模块删除的连带清理门禁
date: 2026-11-02
updated: 2026-11-02
tags: [UI, Designer, 模块删除, 控件清理, GridPanel, Span, 死成员]
status: active
source: AdaWeldSystem/UIDesign/ControlPage/DataReviewerPage.cs + .Designer.cs（2026-11-02 移除「按 X 范围显示区域」模块）
---

# UI 功能模块删除的连带清理门禁

> **一句话**：删一个 UI 功能模块 = 删代码 + 删 Designer 控件本体 + 删专属字段 + 改容器 `Span` 占位，漏一项就留残骸或编译不过。

**本案**：2026-11-02 移除 `DataReviewerPage` 的「按 X 范围显示区域」模块 —— 滑块 `uiTrackBar1`（`AntdUI.Slider`）+ 专属字段 `TrackbarRate` + 判据 `HasEnoughSeamWidthPoints` 全部移除，底行 GridPanel `Span` 由 4 行改为 `"fill;fill;fill 120;-35 fill 35"`（滑块行并入底行，图表 +35px、按钮保持原位）。

## 坑一：删 UI 功能 ≠ 删一个方法

### 现象

只删业务方法，Designer 里控件还在（用户仍看得到滑块）；或只删 Designer 控件、代码后置引用还在 → CS0103。

### 根因

Designer 控件在文件里有 **4 个落点**：实例化（`this.uiTrackBar1 = new AntdUI.Slider();`）、`Controls.Add`、属性块、字段声明。模块层另有专属字段（`TrackbarRate`）、专属方法与判据（`HasEnoughSeamWidthPoints`），容器层还有 **GridPanel `Span` 占位行**。漏任一处都不是「干净删除」。

### 判据

删除前逐项列清单并核对：① Designer 实例化 ② `Controls.Add` ③ 属性块 ④ 字段声明 ⑤ 专属字段 / 常量 ⑥ 专属方法与判据 ⑦ 容器 `Span` 占位行。删完后重新对齐：**GridPanel 行数 == 挂载控件数**。

### 预防

- 把「功能模块」当一个删除单元，7 项一次列全再动手，不要边删边想。
- ⛔ 删 GridPanel 子控件必须同批改 `Span`，否则其余控件整体错行。

## 坑二：零引用 ≠ 死成员 —— 查读取点，不凭名字判断

### 现象

`MinValueRobotX` / `MaxValueRobotX` 在扫描器眼里「只写不读」，像死字段，险些随滑块一起删。

### 根因

两者是 public 字段，**写入路径与读取路径分离**（悬停读数路径读取）；静态扫描按「本文件内调用」判定 ⇒ 跨方法读取不算调用 ⇒ 假阳性。名字里的 `Min`/`Max` 也不代表与滑块同属一套功能。

### 判据

判死成员前先问「有没有读取点」：全仓 `Grep` 该标识符全部出现位置，逐条分类为「写入 / 读取 / 委托 / 反射 / 字符串」；只有「仅声明 + 仅写入」才进删除候选。字段归属按**读取点所在的功能**判定，不按名字、不按同文件判定。

### 预防

- ⛔ 公共字段的归属看**读取方**，不看名字。
- 删除候选先列清单交业主裁定，⛔ 不自行批量删（裁定与执行分离）。

## 坑三：控件可能本就没有订阅 —— 删的是设计意图，不是运行行为

### 现象

`uiTrackBar1` 全项目 **0 处** `ValueChanged` 订阅，Designer 内也无事件挂接 ⇒ 滑块拖动本就无任何响应。

### 根因

控件被设计出来表达设计意图（可拖动的 X 范围定位），但接线从未完成。静态校验若只问「有没有订阅」，会把「未接线」与「已失效」混为一谈。

### 判据

删前查两件事：① 事件订阅点（`+=`）在 `.cs` 与 `.Designer.cs` 各几处；② 有无反射 / 委托 / `nameof` 形式的间接引用。全项目 0 处 ⇒ 该控件从未产生运行期行为，删除不改变运行时表现。

### 预防

- 记录「删的是未接线的设计意图」这一事实，避免后来者误以为删掉了可用功能。

## 坑四：Designer 的 `Dispose(bool)` 不可动，先确认控件是否在 `components` 内

### 现象

删控件时顺手清理 `components` 或 `Dispose(bool)` 块。

### 根因

`Dispose(bool)` 是设计器生成代码，手写会破坏释放链；**可视控件（`Control` 派生）不在 `components` 内**（只有 `Component` 派生如 `Timer` 在），所以删可视控件**不需要**动 `components` 与 `Dispose`。

### 判据

删前查 `components` 归属：可视控件 → 只删 4 个落点，⛔ **不动** `components` / `Dispose(bool)`；非可视组件（`Timer` 等 `Component`）→ 才需确认 `components.Dispose()` 链路是否仍闭合。

### 预防

- ⛔ 禁止手改 `Dispose(bool)`（见 [[guides/WinForms-Designer]]）。
- 改 Designer 走字节安全流程（保持 BOM / CRLF），见 [[lessons/WikiDriftCorrectionPitfalls]]。

## 坑五：GridPanel 删子控件会重排，`Span` 无编译期保护

### 现象

`Span` 是 `string` 属性，写错只导致布局不对，**不报错**；删掉一行控件而不同步改 `Span`，其余控件整体上移 / 错行。

### 根因

`AntdUI.GridPanel` 按 `Span` 的行定义分配格子，控件挂载顺序与行数强耦合；编译期零保护。

### 判据

改 `Span` 或删控件后，必须**运行期实测**每个子控件的 `Bounds`：`Form.Show()` 建句柄后取值（必要时反射 `GridPanel.ConvertToRects` 取格子矩形），确认图表 / 标签 / 按钮各在其位。实证写法见 [[guides/AntdUI-Reference]] 的 `Span` 一节。

### 预防

- ⛔ 静态校验只能断言 `Span` 字符串形态（行数 / 列数 / 行高个数），**不能替代**运行期实测。
- 删控件与改 `Span` 同一批次完成，中间不留半成品状态。

## 关联

- [[guides/AntdUI-Reference]] —— `Span` 语法与本项目实证（含 4 行改 3 行实例）
- [[guides/WinForms-Designer]] —— Designer 修改规范（字节安全 + `Dispose(bool)` 禁令）
- [[lessons/UiLayoutChangeSyncPitfalls]] —— 布局改版类相邻坑（控件三处对账、事件订阅唯一）
- [[lessons/StaticVerifier-Checker-FailureModes]] —— 零引用假阳性与判据设计
- [[api/DataReviewerPage]] —— 本案落地页
- [[standards/CodeSimplification]] —— 零消费预留成员禁删裁定

## 相关页面

- [[index/index]]
