---
title: UI 功能模块删除的连带清理门禁
date: 2026-11-02
updated: 2026-11-18
tags: [UI, Designer, 模块删除, 控件清理, GridPanel, Span, 死成员, 孤儿处理器, 同步单向化, 静默兜底, 未读到即无值, 启用态前置, 字面量类型]
status: active
source: AdaWeldSystem/UIDesign/ControlPage/DataReviewerPage.cs + .Designer.cs（2026-11-02 移除「按 X 范围显示区域」模块）；2026-11-18 追加坑六（ProcessControlPage GA 设置区 4 控件删除）、坑七（静默兜底掩盖未读到 + 启用态前置）、坑八（Designer 字面量类型：编译过但设计器炸）
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

### 坑六 · 删控件后置的孤儿处理器与同步关系单向化（2026-11-18）

**现象**：Designer 删控件后，代码后置留下两类残留 —— ① 事件处理器方法体还在，但订阅点已随控件删除（方法永不可达，成为死代码）；② 原双向同步的一端被删后，另一端仍保留回写代码 → CS0103（引用已删字段）。

**根因**：Designer's「删控件」只清 4 个 Designer 落点，**不感知代码后置的事件订阅与方法体**；同步关系（本项目原为 `selGalvoPattern` Select ↔ GA 指令 Radio 双向）在删掉一端后，另一端的回写代码不会被自动失效。

**判据**：
1. 全仓 Grep 被删控件名，命中处逐条判定：**CS0103 硬错误**（引用已删字段）与**订阅点已消失的孤儿方法**（编译过但不可达）二者都须清理，不能只修编译错误。
2. 同步关系退化判定：原 Select↔Radio 双向 ⇒ Select 被删后，Radio 侧的回写代码连同其抑制标志包夹一并删除；⛔ 但抑制标志本身若仍服务于**另一处程序化回填**（如 `LoadGalvoActionUi` 回填 Radio）则**保留**。
3. ⛔ **workflow 层公共方法一律不连坐删**：`GalvoHome` 有系统设置页消费方；`GalvoDemo` 虽 UI 唯一入口被删，仍属 workflow 公共 API —— 删除属架构变更，须业主裁定，不在「修编译」范围内自行执行。

**预防**：
- 把「删控件」当一个删除单元清 7 项（Designer 四落点 + 代码后置引用 + 事件处理器 + 专属字段 + 容器占位）。
- ⛔ 禁因 UI 入口消失就删 workflow 公共方法；⛔ 抑制标志删除前先查其**全部使用点**。
- 案例：[[api/ProcessControlPage]]（2026-11-18 GA 设置区 4 控件删除）。

### 坑七 · 「静默兜底」掩盖「未读到」——默认值冒充实际值（2026-11-18）

**现象**：删控件后图形设置的语义被三处「静默兜底为直线」掩盖 —— ① 配置属性初值 `GalvoPattern = 3`；② INI 读取处 `if (值 < 1 || 值 > 4) 值 = 3`；③ UI 映射函数 `default: return Line`。结果：**配置里根本没读到图形**（缺键 / 越界 / 配置对象为空），界面却显示「直线」并把它当实际值落盘下去 —— 操作员看不出「这项还没配」。

**根因**：兜底值的语义被混淆 —— 「**读到了但值非法**」（脏数据纠错）与「**根本没读到**」（未设置）是两件事，前者可纠错，后者只能表达「没有」。用同一个默认值覆盖两者，就把「未设置」伪装成了「已设置为直线」。同理，UI 层的 `default:` 分支让「新增一个图形 Radio 但忘了加映射 case」也静默落成直线，无声无息。

**判据**：
1. **区分「未读到」与「读到但非法」**：未读到 ⇒ 表达「无」（不选 / 不写）；读到但非法 ⇒ 归「无」或显式报错 + 记日志，⛔ 不静默改成一个看似合法的值。
2. **兜底必须可见**：任何把非法值改成合法值的分支，都要**记一条日志**（Warning 及以上），否则现场无从追溯。
3. **UI 映射表不得有 `default` 兜底**：枚举 ↔ 控件双向映射的 `default` 应返回「无匹配」并让调用方显式处理，⛔ 禁静默落默认值（否则新增控件时会被静默归错）。
4. **协议层无「无」值时，下发路径单独兜底**：配置层可表达「未设置」，但设备协议枚举只有合法值时，须在**下发边界**统一转换（如 `ResolveGalvoPattern`：0/越界 ⇒ 逻辑零位值），⛔ 禁把非法值直接写进设备。

**预防**：
- 判定一个值是不是「实际值」时，问一句：**它是从存储里读到的，还是代码自己编的？** 后者一律不算。
- 配置层表达「未设置」+ 下发层统一兜底，两处分开写，不要把兜底混进读取层。
- ⚠️ **「无」的前提条件要问清**（2026-11-18 修正）：同一个「无」在不同前置条件下语义不同 —— 振镜图形「未读到 = 无图形」只在**振镜已启用**时成立；未启用时是「振镜不摆动 ⇒ 图形无物理意义」，属另一条链。⛔ 禁把「未读到」直接等同于「无」而不问前置条件。
- ⚠️ **跨页前置条件必须实时读**（2026-11-18）：前置条件（振镜启用态）在**别的页面**（系统设置页 `swEnableGalvoWeaveQuick`），本页只能通过**配置真相源**读到；⛔ 禁在 workflow 里缓存 `LoadConfig()` 期快照（运行期改开关不刷新）⇒ 改实时读，与同链其它消费方同口径。
- 案例：[[api/ProcessControlPage]] · [[api/LaserWeldHeadWorkflow]]（2026-11-18 振镜图形语义收敛，ADR-076 D3/D4）。

### 坑八 · Designer 属性赋值的字面量类型 —— 编译过、设计器炸（2026-11-18）

**现象**：系统设置页在 VS 设计器中打开即报「类型 `System.Int32` 的对象无法转换为类型 `System.Nullable\`1[System.Decimal]`」，但 `MSBuild /t:Rebuild` **编译完全通过**（errors=0）。

**根因**：`AntdUI.InputNumber` 的 `Minimum` / `Maximum` 属性类型是 **`decimal?`**（可空），而 Designer 里写的是裸 int 字面量：
```csharp
this.numWeldHeadNode.Maximum = 255;   // ❌ int → decimal? 无隐式转换
this.numWeldHeadNode.Minimum = 0;     // ❌
```
C# 编译器里 `int → decimal` **有**隐式转换（所以 `Value` 属性用裸数字没问题），但 `int → decimal?` **没有**（需先转 `decimal` 再装箱）⇒ **编译期不报，设计器反射赋值时才炸**。

**判据**：
1. **属性声明类型决定字面量后缀**：`decimal?` 属性必须写 `255M` / `0M`；`decimal` 属性写 `2` 或 `2M` 都行；`int` 属性写裸数字。
2. ⛔ **真编译通过 ≠ 设计器能加载**：设计器走**反射赋值**路径（`PropertyInfo.SetValue`），而编译期走**编译期转换**路径 —— 两者接受的类型集合不同。凡是「编译过但设计器报错」，优先查 Designer 里的字面量类型。
3. **机检判据**（全库可跑）：扫所有 `*.Designer.cs`，找 `decimal?` 类属性（`Minimum`/`Maximum`）被赋**裸 int 字面量** —— 命中即设计器必炸；`decimal` 非可空属性的裸字面量属安全（隐式转换成立），不报。
4. 官方属性类型查 `raw/AntdUI/wiki-zh/Control/<控件名>.md`（⛔ 不凭印象；`InputNumber` 的 `Minimum`/`Maximum` 是 `decimal?`，`Value`/`Increment` 是 `decimal`，`DecimalPlaces` 是 `int`）。

**预防**：
- 手工改 Designer 赋值时，凡目标属性是 `decimal` / `decimal?` ⇒ **一律加 `M` 后缀**，不靠"int 也能转"的直觉。
- 同页既有先例可参照（`RenderParamForm.Designer.cs` 全部用 `M` 后缀，是 VS 设计器为 `decimal?` 生成的标准写法）。
- 改 Designer 保持字节安全：BOM 原状 + CRLF 同质 + `\r\r\n` 为 0（改完用字节计数复核）。
- 案例：[[api/SystemControlPage]]（2026-11-18 `numWeldHeadNode`）、[[guides/WinForms-Designer]]。

### 坑九 · 误删控件的恢复口径：按当前布局补四件套，逐属性对 HEAD（2026-11-24）

- **现象**：误删 `txtTempWarn` / `txtTempAlarm` / `lblTempWarnCaption` / `lblTempAlarmCaption` 后，`SystemControlPage.cs` 里 4 处后置引用（3 行）仍在 ⇒ 编译 CS0103。
- **判据**：Designer 里 `grep -c` 命中 0、而 `.cs` 有引用 ⇒ 纯 Designer 侧丢失。此时 `git diff --stat` 显示 Designer 已大幅重排（本例 1099 行）⇒ ⛔ **不能整块回贴 HEAD**，行列位置与控件风格可能都已变。
- **恢复口径**：
  1. 从 `git show HEAD:<path>` 取原始属性块（⛔ 不用 `git checkout -- <file>` 恢复工作区）；
  2. 在当前 Designer 找**同类邻居**（同一 TableLayoutPanel 的相邻行）作风格模板：`Dock=Fill`、`Font`、`Size`、`TextAlign` 以邻居为准，值仍取 HEAD；
  3. 补四件套：字段声明 / `new` 实例化 / `Controls.Add(this.X, col, row)` / 属性块；`TabIndex` 用 HEAD 原值，**先确认当前未被占用**；
  4. 先确认目标行列**已留空**（本例 `gridTemp.RowCount=10`、行 5 无人使用）⇒ 直接补回即可，⛔ 不要新增 `RowStyle` 或改 `RowCount`；
  5. 逐属性比对：`HEAD 属性集 ⊆ 当前属性集` 且同名值一致，允许新增 `TextAlign` 这类对齐属性。
- **验证**：真编译 `errors=0 rc=0` + 属性比对脚本全 PASS（声明/实例化各唯一、挂载行列正确、TabIndex 无冲突、后置引用可解析）。

## 关联

- [[guides/AntdUI-Reference]] —— `Span` 语法与本项目实证（含 4 行改 3 行实例）
- [[guides/WinForms-Designer]] —— Designer 修改规范（字节安全 + `Dispose(bool)` 禁令）
- [[lessons/UiLayoutChangeSyncPitfalls]] —— 布局改版类相邻坑（控件三处对账、事件订阅唯一）
- [[lessons/StaticVerifier-Checker-FailureModes]] —— 零引用假阳性与判据设计
- [[api/DataReviewerPage]] —— 本案落地页
- [[standards/CodeSimplification]] —— 零消费预留成员禁删裁定

## 相关页面

- [[index/index]]
