---
title: ADR-078 焊接回放播放控件栏与日期目录录像列表
date: 2026-10-30
updated: 2026-11-03
tags: [决策, 监控相机, 回放, 播放控件栏, 录像日期目录, 缩略图, AntdUI, Emgu]
status: accepted
---

# ADR-078：焊接回放播放控件栏与日期目录录像列表

## 背景

业主需求（2026-10-30）在 ADR-048 既有「焊接回放」页上做三项强化：

| 现状（ADR-048） | 问题 |
|---|---|
| 回放仅有「右键→回放 / 停止回放」两个入口 | 无进度、无时间、无倍速、无跳转 |
| 录像直接落 `RecordDirectory` 根目录 | 长期运行后根目录平铺数千文件，按日期回溯困难 |
| 列表仅 No/文件名/修改时间/大小 | 无法按日期区间筛选，也无法凭文件名判断画面内容 |

## 决策

1. **底部播放控件栏：悬停显隐 + 双层 + 50% 半透明**
 - 实现载体 = `imageBoxPlay` 的子控件 `panelPlayBar`（`Dock=Bottom`、`Height=78`、`Visible=false`、`BackColor=Color.FromArgb(128,0,0,0)`）。作为 `ImageBox` 子控件，`PaintTransparentBackground` 会调父控件 `OnPaint`（`PanAndZoomPictureBox` 在此绘制画面），半透明层因此透出视频画面而非页面底色。
 - 显示/隐藏判定：`imageBoxPlay.MouseMove` 的 Y ≥ 高度 − 96px 即显示，其余区域隐藏；`MouseLeave` 隐藏；`panelPlayBar.MouseEnter` 保持显示。`panelPlayBar.MouseLeave` 以 `RectangleToScreen(...).Contains(Cursor.Position)` 复核，**移入子按钮不误判为离开**。
 - 上层 = 进度条 `sliderPlay`（`AntdUI.Slider`，`MinValue=0 / MaxValue=总帧数`）+ 时间 `lblPlayTime`（「当前 / 总时长」）；下层 = `flowPlayButtons` 居中承载 5 个 `Ghost` 按钮。
 - **2026-11-02 版式演进（本轮修正）**：回放栏最外层 ~~`tableLayoutPlayBar`（`TableLayoutPanel`，1 列 2 行）~~ → **`gridPlayBar`（`AntdUI.GridPanel`）**，由 GridPanel 承担区域分割：`Span = "fill;fill;-26 fill"`（2 行 × 1 列，行高 26px + 剩余），**逆序入格**（先 `Add(flowPlayButtons)` → 落第 2 格，后 `Add(gridPlayTime)` → 落第 1 格），子控件数 2 == 格子数 2。第 1 格 = 进度区 `gridPlayTime`（`AntdUI.GridPanel`，`Span="fill 90 128"` 1 行 3 列，**逆序入格** `lblPlayTime` → `lblPlaySpeed` → `sliderPlay`，3 子控件 == 3 格）；第 2 格 = 按钮区 `flowPlayButtons`（`AntdUI.FlowPanel`，`Align=TAlignFlow.Center`、`Gap=0`、`Margin=0`，**逆序入流** `btnFastPlay` → `btnForward5Play` → `btnPlayPause` → `btnBack5Play` → `btnSlowPlay`，5 枚 `Ghost` 图标按钮）。~~`gridPlayCenter`（曾误将按钮区单独包成 `GridPanel`）已删除~~ —— 按钮区只是整体分割后某一区域内的内容，不承担分割职责；~~`tableLayoutPlayCenter`（1×1 `TableLayoutPanel`，用于在格内居中按钮组）~~ 亦已删除，居中语义改由 `FlowPanel.Align=Center` 承担。**AntdUI 优先口径**：回放区现为**零原生布局容器**，`TableLayoutPanel` / `FlowLayoutPanel` 一律不得用于分格或摆间距 —— 页级两层同样已换：~~`tableLayoutPanelPlay`（2 行 × 2 列：45px / 100%、100% / 400px）~~ → **`gridPlayPage`**（`Span="fill 400;fill 400;-45 fill"`，4 子控件 == 4 格，逆序入格 `playTable` → `imageBoxPlay` → `gridPlayFilter` → `label1`）；~~`tableLayoutPlayFilter`（1 行 2 列：100% / 105px）~~ → **`gridPlayFilter`**（`Span="fill 105"`，2 子控件 == 2 格，逆序入格 `btnRefreshPlay` → `uiPlayDateRange`）。像素口径 = `gridPlayTime` 整数列宽 90/128 等价原 `Absolute 90F/128F`（100% DPI），`sliderPlay` 的 `Margin(0,0,8,0)` 由 GridPanel 从 fill 列宽扣减，按钮保留 `Margin(2,3,2,3)` 由 FlowPanel 尊重 —— 实测 Bounds 与替换前逐像素一致。外层遮罩 ~~`panelPlayBar`（`System.Windows.Forms.Panel`，`BackColor=ARGB(128,0,0,0)`）~~ → **`panelPlayBar`（`AntdUI.Panel`，`Back=ARGB(128,0,0,0)`，`Shadow=5` / `ShadowColor=Black` / `BorderColor=RGB(217,217,217)`；`BorderWidth` 保持默认 0，设 1 会再内缩 1px）**。AntdUI `Shadow` 会在内容区四周内缩 5px，故 `Padding` 由 (8,4,8,6) 校准为 (3,0,3,0)，使内层 `gridPlayBar` 仍为 603×68；悬停显隐仍基于 `Visible` + `RectangleToScreen`，无 `CreateParams` / 透明重写依赖。
 - **2026-11-02 控件形态**：倍速按钮图标化（慢放 `FastBackwardOutlined` / 快放 `FastForwardOutlined`，后退/前进 `StepBackwardOutlined` / `StepForwardOutlined`，均无文本）；进度条与时间之间新增 `lblPlaySpeed`（「速度 1.0x」，`MiddleCenter`），由 `UpdateSpeedButtons()` 单点回写；按钮 / 进度条事件订阅仍为单一入口（Designer 不重复 `+=`）。
2. **播放能力：帧索引为唯一进度轴**
 - 进度与定位统一用 `CapProp.PosFrames`（`VideoCapture.Set`）；总帧数 / 帧率取 `FrameCount` / `Fps`（非法帧率回退 30）。
 - **时间基准驱动（2026-11-03 修复 3 倍慢放）**：~~定时器 33ms 固定节拍 + 倍速帧累加器~~ → `Stopwatch _playClock` + 锚点（`_playAnchorFrames` / `_playAnchorSpeed`），每拍 `TargetPlayFrame() = 锚点帧 + 已播秒数 × Fps × 倍速`，取整后补齐到该帧（中间帧 `Dispose`，末帧上屏），**不做"每拍睡固定毫秒"或"每拍固定加 N 帧"的累加**；定时器抖动/单帧解码与绘制耗时不再累积成慢放（实测 1.0x 由 12.7s/9s → 9.0s/9s）。`_playClock.Restart()` 即重锚：`SeekToFrame` / 倍速切换 / 暂停恢复均以当前位置重锚（`RebasePlayClock()`），保证**切速不重置位置、不跳帧错位**（实测 1x→2x 中途切换点 135 帧不变、全程 6816ms ≈ 理论 6770ms：4.5s@1x + 4.5s/2）。定时器仍只有一个 `timerPlay`、仅作**触发节拍**（现 Interval 33ms 保持，不再承担时间语义），等待不在 UI 线程上做。
 - 倍速档位 `0.8 → 0.5 → 0.3 → 0.1 → 1.0`（慢放）、`1.5 → 2.0 → 2.5 → 3.0 → 1.0`（快放），均为点击循环；点击任一组即把另一组复位到 `1.0`。后退/前进 = 按当前 `Fps` 换算 ±5s 的帧数。
 - 播到结尾停在末帧（`FinishPlayback`：进度置满、按钮回「播放」态），再次点播放自动从头续播；暂停/恢复只停启定时器，解码资源保留。
 - 5 个按钮的 `showtips` 经 `AntdUI.TooltipComponent.SetTip` 绑定中文释意；进度条游标悬停为 `Cursors.Hand`、按下为 `Cursors.SizeWE`。
 - **旧「停止回放」按钮与底部 `flowPlayBar` 整行删除**（业主 2026-10-30 确认），停止语义由「暂停 + 播完自动停」承载。
3. **录像按日期文件夹落盘**
 - `MonitorCamManager.StartRecord(fileName)` 统一在 `RecordDirectory` 下拼 `yyyyMMdd` 子目录并建目录；**手动录像（页面）与自动录像（模拟焊接 `SimMonitorCamStartWeld`）同走此口**，实现层 `IMonitorCamApi.StartRecord(filePath)` 契约不变。
4. **回放列表：日期区间筛选 + 区间文件汇总（根 → 日期文件夹 → 文件）**
 - 顶栏筛选区 = `AntdUI.DatePickerRange`（`Value` 为 `DateTime[]` 两元素、闭区间、默认今天~今天、订阅放在初始赋值之后——与 [[decisions/ADR-056-DataReviewRangeFilterAndModularMultiSelect]] 同构）+ 既有「刷新列表」按钮。
 - 目录层级与扫描时机（**2026-11-03 两级汇总，业主最终口径**）：~~递归 `*.avi`（`SearchOption.AllDirectories`）~~ → ~~逐层懒加载（日期 → 扫描文件夹 → 文件）~~ → **日期区间 = 日期文件夹选择器，选完区间直接汇总区间内全部录像文件预览**：
   - **第 1 层 录像根地址**：唯一来源 `MonitorCamManager.RecordDirectory`（= 焊接相机参数设置落盘的 `MonitorCamConfig.RecordDir`，INI 键 `RecordDir`；无第二处硬编码）。
     - **默认值与运行期创建（2026-11-03 路径约定，业主口径「只改默认」）**：默认值唯一常量 `MonitorCamConfig.DefaultRecordDir = D:\WeldRecord`（INI 键缺失或为空时回落，仅内存纠正、不写盘）；`MonitorCamManager` 构造期 `EnsureRecordDirectory()` 仅在运行期检查并 `Directory.CreateDirectory` 创建，**不写 INI**；创建失败（无权/盘不存在/网络不可达）**只记 Warning 日志**（不弹窗骚扰）+ 回退 exe 目录下 `Record`（内存态，不覆盖用户配置），不阻塞启动。
     - **不做旧值迁移**：程序不替用户改写配置——裸盘符根（`D:\` 等）不再判定、不再改 INI、不再备份 INI、不写盘；配置由业主自行维护。
   - **第 2 层 日期文件夹**：`Directory.GetDirectories(root, "*", TopDirectoryOnly)` 一层，过滤 8 位 `yyyyMMdd` 且落在 `DatePickerRange` 区间内，**倒序（最新在上）**。
   - **第 3 层 文件汇总**：对区间内**每个日期目录**执行 `Directory.GetFiles(日期目录, "*.avi", TopDirectoryOnly)`（只取本层、**不递归子目录**），合并成一张预览列表；排序 = 日期倒序 + 日期内文件名序；行「修改时间」= 日期文件夹日期 + 文件时分，用于区分文件归属哪个日期。
   - **表格只渲染文件行**：~~`PlaybackRowKind`（`DateFolder` / `ScanFolder` / `File`）~~ 已删除；无日期行、无「扫描文件夹」中间层，不存在「必须点日期/文件夹才出录像」的下钻门；仅文件行右键「回放」，左键不触发加载。
   - 空态文案：区间内无日期文件夹 → 「日期区间内无日期文件夹 · 根目录」；有日期文件夹但均无 avi → 「该区间内无录像文件（N 个日期文件夹均为空）」。
 - **懒加载：初始化不读，进入页面才加载（2026-11-03 业主口径）**：构造期 / `FormMain` 装配期**不得**扫描录像目录、解码缩略图或读任何回放索引；只有用户首次切到「焊接回放」页签才触发首扫；`_playListLoaded` + 非空行保证反复切页不重复全量扫描，切走时 `CancelPlayScan()` 取消后台任务；`刷新列表` 与日期区间变化才按新区间重扫。
 - 线程与取消：统一走 `RunPlayScan`（后台 `Thread` 执行 `Func<CancellationToken, PlayScanOutcome>`，结果 `BeginInvoke` 回 UI）；`CancellationTokenSource`（`_playLoadCts`）+ 代数（`_playLoadGeneration`）双保险，切页/改区间取消旧任务，**旧结果不得覆盖新选择**（快速改区间时只保留最后一次）。
 - 快速失败：目录不存在 / 未配置 / 无权限 / 网络盘异常在后台捕获后回填「读取失败：…」标题，并 `GlobalCommData.ShowLog` + `AntdUI.Message.warn` 明确提示，绝不静默等待。
 - **口径变更**：根目录平铺的存量旧录像不进入回放列表（列表以日期文件夹为组织单位）；缩略图位图随行清空统一释放。
5. **列表行 = 预览图 + 文件名（+ 既有时间/大小）**
 - 行模型 `PlaybackRow.Preview` 返回 `AntdUI.CellImage`（`Size=96×54`、`ImageFit=Contain`），缩略图未就绪时返回 `CellText("加载中…")`；`Table.RowHeight=64`、`AutoSizeColumnsMode=Fill`。
 - **缩略图后台加载**：主表先绑列表（占位文字立即出），后台 `Thread` 逐行 `VideoCapture` 读首帧 → `ToBitmap` → 缩放 96×54 → 回填行对象 → `BeginInvoke` 刷新表格。取消机制用**代数计数**（重载/销毁即 `_thumbGeneration++`，旧线程自行退出并释放半成品位图）；缩略图位图由 `ClearPlaybackRows` 统一释放。

## 备选方案

| 方案 | 结论 |
|---|---|
| 进度条用毫秒（`PosMsec`） | 放弃：AVI 帧定位更稳定，且时间显示可由「帧/帧率」派生，单一真值轴避免两套换算 |
| 倍速改定时器 Interval | 放弃：Interval 精度低且 0.1x 需 330ms 级间隔，界面节拍不均；帧累加器保持 33ms 均匀刷新 |
| 控件栏做成独立面板置于画面下方（不叠加） | 放弃：业主明确要求「鼠标移到底部显示/移出隐藏」的悬浮层，叠加才不占用画面尺寸 |
| 缩略图同步解码后再绑定列表 | 放弃：文件多时首屏卡顿，违背「预览图资源后台加载不阻塞页面显示」 |
| 递归 `AllDirectories` 一次扫全量录像 | 放弃（2026-11-03）：`RecordDir` 现场被配成 `D:\`，整盘遍历在返回前无任何结果，页签一开即「未响应」 |
| 按日期 / 扫描文件夹逐层点击下钻 | 放弃（2026-11-03 业主澄清）：日期区间即日期文件夹选择器，选完区间直接汇总出全部录像预览，不得要求逐日期、逐文件夹点击 |
| ~~日期区间取目录名硬过滤~~ | 作废：改为按 `yyyyMMdd` 目录名过滤 + 本层 `*.avi` 汇总；根目录平铺旧录像不再回退兼容 |

## 实施约束

- **`AntdUI.AntList<T>` 只暴露非泛型 `IEnumerable` 与索引器**，不能直接喂 `List<T>` 的 `IEnumerable<T>` 构造器；跨线程取行须按索引逐个复制引用（构造期实测踩中，已按索引复制落地）。
- 后台线程只写行对象字段 + `BeginInvoke` 刷新，**不得弹窗、不得触碰控件**（[[guides/WinForms-UI-Threading]]）。
- 控件仍全部由 `MonitorCamPage.Designer.cs` 声明与挂载，`Table.Columns`/`Binding` 留代码后置（ADR-048 四次补充口径，[[guides/WinForms-Designer]] §6）。
- 缩略图 / `VideoCapture` / `Mat` 的释放边界：跳帧 `Dispose`、解码器 `using`、缩略图随行清空释放。

## 通用化（2026-11-09）：初始化零追溯 —— 全部追溯/历史页面强制

> **强制约束**：初始化链路只做设备与配置的**就绪判定**，⛔ 不读取任何业务历史数据（生产记录 / 录像索引 / 记录文件枚举 / 报表统计）。追溯类页面的查询只允许**用户主动交互**触发：点击该导航项/页签、点刷新、修改查询条件。

- **适用面**：由「焊接回放」页扩展为全部追溯页（数据追溯页、记录文件页、后续任何报表页）。
- **判据（哪些调用算违规）**：应用尚未进入正常运行态（`GlobalCommData.IsAppRunning == false`）时，出现 `ProductFileRecordManager.Select*`、`Directory.GetFiles` / `Directory.GetDirectories`、`RecordFileStore` 读取、或任何「查库后装配列表」的动作，均属违规。
- **判据来源**：`GlobalCommData.MarkAppRunning()` 由 `FormMain` 在首次 `Shown` 的设备初始化结束后显式置位；⛔ 不得用 `Visible` / `Created` / `IsHandleCreated` 充当「初始化完成」判据。
- **反例（2026-11-09，运行期实测）**：AntdUI 的 `Tabs` **不隐藏非当前 `TabPage`**——窗体 `Show()` 时全部子页 `Visible=true`，且每个子页都收到 `VisibleChanged`；页面若以 `this.Visible && FindForm().Visible` 为门，两条判据同时成立 → 启动即查当日生产记录并弹「… 至 … 没有生产记录」。该「双判据」已被现场与实测双重证伪，不得再用。
- **正解**：加载入口收敛为 `EnsureLoaded()`，只由用户交互（导航/页签切换、刷新、改区间）调用；`DataReviewerPage` 不再订阅 `VisibleChanged`；`InitPCLDir` 入口再做一次运行态硬闸（拒绝时记一条限流 Warning 并直接返回，不查库、不扫记录、不弹空态）；`_firstShownLoaded` 保证反复切页不重查。
- **两态区分**：未加载 → 中性文案「尚未加载生产记录」；已查询为空 → 才显示「所选区间无生产记录」并弹空态。
- ⛔ 空态提示（`AntdUI.Message.warn` 等）只在上述允许的查询**返回空结果后**显示；初始化期不得出现任何空态。

## 后果

### 正面

- 回放具备「进度-时间-倍速-跳转」完整控制，且控件栏不占画面、不遮挡常态画面。
- 录像按日归档，回放列表可按区间精准回溯；缩略图让内容可辨认。
- `StartRecord` 的日期子目录在 Manager 层统一，手动与自动录像一致。

### 负面

- 列表刷新会为每个文件解码首帧，大区间（数千文件）时后台 CPU 占用上升；代数机制可随时中止。
- 半透明叠加依赖 `ImageBox`（`PanAndZoomPictureBox.OnPaint`）绘制画面，若未来替换为不绘制 `OnPaint` 的宿主控件，叠加层将退化为底色。
- 播到结尾保留解码器以便续播，文件句柄直到下一次打开/离开页面才释放。

## 相关页面

- [[modules/MonitorCam]]、[[api/MonitorCamManager]] —— 录像落盘与回放链路
- [[modules/UIDesign]] —— MonitorCamPage 控件与布局
- [[decisions/ADR-048-MonitorCamTabsRecordPlayback]] —— 回放页初版（本 ADR 强化其决策 8）
- [[decisions/ADR-056-DataReviewRangeFilterAndModularMultiSelect]] —— 日期区间选中范式来源
- [[guides/AntdUI-Reference]] —— `CellImage` / `Slider` / `DatePickerRange` / `TooltipComponent` 用法与 `AntList` 约束
- [[guides/WinForms-UI-Threading]] —— 后台线程与 UI 封送
- [[decisions/ADR-010-LayoutContainerFreedom]] —— 布局容器自由化与 `GridPanel` 使用规则（逆序入格 / Span / 子控件数 == 格子数）
