---
title: UI 布局改版的同步与所有权门禁
date: 2026-09-29
updated: 2026-10-30
tags: [教训, UI, Designer, 事件订阅, 跨线程, Mat, 资源释放, 组件归属, Timer, resx注册]
status: active
source: AdaWeldSystem/UIDesign/ControlPage/MainPage.cs + .Designer.cs（2026-09-29 主界面双图化）
---

# UI 布局改版的同步与所有权门禁

> 业主在 Visual Studio 中**先行改好设计器布局**、再交 AI 补代码后置，是本项目常见的协作方式（2026-09-29 主界面五图精简为双图即属此类）。
> 这种「先布局、后接线」的节奏会同时踩中五类坑：编译期残留引用、回填触发事件、跨线程资源所有权、**控件与组件该落在设计器还是代码后置**，以及**`.resx` 工程登记**。
>
> **2026-10-22 状态更新**：主界面监控预览（`panelCam` / `imageBoxCam`）已按需求移除；坑二附的 `ImageBox` 装配示例与坑四的 `Mat` 所有权口径作为**该范式的历史实证**保留，仍适用于其他设计器声明控件 / 跨线程图像场景。现行预览承载页 = [[modules/MonitorCam]]。

## 坑一：设计器删控件，代码后置引用未同步 ⇒ 编译阻断（CS0103）

**现象**：`MainPage.Designer.cs` 已删除 `formsPlot3/4/5` 与 `panelChart3/4/5`，但 `MainPage.cs` 的 `RefreshParamCharts()` / `AfterInitializeUI()` 仍逐条引用这 5 个控件 —— `MainPage` 类里根本没有这些字段，**编译必然失败**（CS0103「当前上下文中不存在名称」）。

**为什么容易漏**：设计器改动「看起来」只影响 `.Designer.cs`；而代码后置里对控件的引用散落在方法体内，不报错到没人查。**改版方（业主在 VS 里）看到的只是设计器预览正常**，编译错误要等下一次 VS 编译才暴露。

**门禁做法**：

1. **布局改版后强制「控件引用对账」**：把代码后置里出现的所有控件标识符（`formsPlotN` / `panelXxx` / `checkboxN` / `labelN` / `tableLayoutPanelN` / …）抽出来，逐个到 `.Designer.cs` 的字段声明里核验存在性；差集必须为 0。
2. 删除控件的**三个位置**要一起清（属性块 + `new` 实例化 + 字段声明），只删一处同样编译失败。
3. 旧控件删除后，**同名/同职责的新控件要显式接管**：本轮即「4 张独立图」→「1 张四合一图 + 4 个复选框」，`BindChartVar` 删除、`AddSeries` 接管（口径写入 [[decisions/ADR-049-MainPageDualChartAndCamPreview]]）。
4. 该对账已纳入 Step 2.6 静态校验脚本的可复用检查项（见 [[guides/Project-Tools]] 静态校验一节）。
5. **统计/状态类控件删除要单独确认「数据显示出口」**（2026-11-10 实例）：业主删除运行时长/数量 label 后，`RefreshDashboard` 仍在写 `.Text` ⇒ 编译阻断；删引用后数据变成**无出口的活数据**——既不能静默丢弃，也不得自行补控件，须列清单报业主定去向。后续裁定：`WeldCount`/`CompleteCount` 查证无记录文件/追溯页/PLC/Modbus/RSI/Config 消费后**连数据一起删除**（属性 + 复位 + 两处自增），`SoftwareStartTime` 保留；步骤条 `steps1` 确认需保留后原样补回（Designer 属性块 + 代码装配/联动一并恢复）。

## 坑二：控件落地位置——业主口径是「设计器可见」，不是「代码后置兜底」

**业主裁定（2026-09-29）**：新增控件**要在设计器上就能看到**，**不接受全部动态加载**。首版把预览 `ImageBox` 与复选框文本/勾选态都放在代码后置，被要求**迁回设计器**。

**正确做法（现行）**：

| 内容 | 落在哪里 | 理由 |
|---|---|---|
| 控件实例化 / 属性（`Dock`、`Size`、`FunctionalMode`…） | **`*.Designer.cs`** | 设计器可见，布局评审不依赖运行期观察 |
| 初始文本 / 默认勾选态（`Text`、`Checked`） | **`*.Designer.cs`** | 同上；且天然避开「回填触发事件」（见下） |
| 数据绑定 / 事件订阅 / 业务逻辑 | 代码后置 | 设计器不承载逻辑 |

**为什么「不能改 `.Designer.cs`」不是理由**：本项目确实禁止在 `.Designer.cs` 里塞逻辑、禁止重写 `Dispose(bool)`（见 [[guides/WinForms-Designer]]），但**增删控件本身正是设计器的职责**。改法必须走**字节安全流程**（保留 BOM/CRLF、按字符串锚点而非行号、改完读回核对）——本轮实测 `MainPage.Designer.cs` 净增 20 行、`CRLF` 同质、`\r\r\n` 为 0、BOM 未引入，风险完全可控。

### 坑二附：设计器声明 `ImageBox` 的三个必需配套（缺一即报错）

```csharp
// ① 实例化
this.imageBoxCam = new Emgu.CV.UI.ImageBox();
// ② Suspend/Resume 成对（容器首次含子控件）
this.panelCam.SuspendLayout();   ...   this.panelCam.ResumeLayout(false);
// ③ ISupportInitialize 成对（ImageBox 实现该接口）
((System.ComponentModel.ISupportInitialize)(this.imageBoxCam)).BeginInit();
((System.ComponentModel.ISupportInitialize)(this.imageBoxCam)).EndInit();
// ④ 挂载 + 属性块 + 成员声明
this.panelCam.Controls.Add(this.imageBoxCam);
private Emgu.CV.UI.ImageBox imageBoxCam;
```

### 坑二附二：非可视组件（Timer）同属设计器；`.resx` 必须登记进 csproj

**立项依据（业主口径 2026-09-30）**：「控件由 `*.Designer.cs` 完全设计，代码后置只做使用」。核查 `MonitorCamPage` 时确认该口径覆盖**三层**——可视控件、**非可视组件（Timer）**、**工程登记（resx）**；只对可视控件对账会漏掉后两层。

| 核查层 | 结论（`MonitorCamPage` 2026-09-30 实测） |
|---|---|
| 可视控件 | 48 个字段**全部由 Designer 声明**：实例化 48/48、`Controls.Add` 46（两个 Timer 为组件不参与挂载）、缺 0 |
| 三方对账 | `Name`↔字段名 48/48 一致、`TabIndex` 组内无重复、`Suspend/Resume` 与 `ImageBox` 的 `BeginInit/EndInit` 配对完整、8 个 `TableLayoutPanel` 的 `Count`↔`Styles` 计数一致、越界 0 |
| `.cs` 侧 | 零控件实例化、零 `Controls.Add`、零事件双写；22 处控件属性写入全为**运行期状态**（配置回填 / 连接态 / 帧图像 / 播放态） |
| **非可视组件** | `.cs` 内 `new Timer()` ×2 ⇒ **迁入设计器**：`new System.Windows.Forms.Timer(this.components)` + `Interval` + `Tick +=`；`.cs` 只留 `Start()` / `Stop()`，释放交 `components.Dispose()`（**不再手工 `Dispose()`**） |
| **`.resx` 登记** | 磁盘 25 个 `.resx`，csproj 仅 24 条 `<EmbeddedResource>`——**唯一缺失者即 `MonitorCamPage.resx`** ⇒ 补登记 |

```csharp
// Designer：组件实例化 + 属性 + 订阅（挂 components 容器托管）
this.timerStatus = new System.Windows.Forms.Timer(this.components);
this.timerStatus.Interval = 500;
this.timerStatus.Tick += new System.EventHandler(this.StatusTimer_Tick);
private System.Windows.Forms.Timer timerStatus;

// 代码后置：只启停，不 new、不 Dispose、不订阅
private void StartStatusTimer() { timerStatus.Start(); }
private void StopStatusTimer()  { timerStatus.Stop(); }
```

```xml
<!-- csproj：.resx 必须登记，否则 VS 树不嵌套、设计器资源无法嵌入 -->
<EmbeddedResource Include="UIDesign\TabPage\MonitorCamPage.resx">
  <DependentUpon>MonitorCamPage.cs</DependentUpon>
</EmbeddedResource>
```

**保留项（不得搬进设计器）**：`AntdUI.Table` 的 `Columns = new AntdUI.ColumnCollection{…}` 与 `Binding()` 必须留在代码后置——全库 **13 处**一致（含 `DataReviewerPage.cs` / `MonitorCamPage.cs`），`InitializeComponent` 内**不可**赋值 `ColumnCollection`（AntdUI 约束，Designer 中零例）。

**五面对账（本环境无 C# 编译器时用 Python 静态替代）**：

| # | 对账 | 判据 |
|---|---|---|
| ① | Designer 三面 | 字段声明数 == `this.X = new …` 数；可视控件均有 `Controls.Add(this.X)` |
| ② | 代码后置引用 | `.cs` 出现的控件标识符 ⊆ Designer 字段声明（差集 0） |
| ③ | 组件归属 | `.cs` 中 `new Timer()`（及任何 `Component`）== 0 |
| ④ | 事件不双写 | 同一事件 `.cs` 与 Designer 的 `+=` 计数只允许一处非 0 |
| ⑤ | resx 登记 | 磁盘 `*.resx` 集合 == csproj `<EmbeddedResource>` 集合（双向差集均为空） |

## 坑三：回填 `Checked` 会触发 `CheckedChanged`；订阅点也只允许一处

**现象 A（误触发副作用）**：`AntdUI.Checkbox` / `AntdUI.Switch` 的 `CheckedChanged(object, AntdUI.BoolEventArgs)` 在**代码回填 `Checked` 时同样触发**。若回填发生在已订阅之后、而处理器会下发运动指令或重建图表，则「加载即误执行」。

**本轮的正解（比抑制标志更省）**：**把初始值交给设计器**。`InitializeComponent()` 里回填 `Checked` 时处理器**尚未订阅**（订阅在构造函数的 `InitSeriesToggles()` 中，晚于 `InitializeComponent()`），因此**天然不会触发**——首版为此加的抑制标志 `_loadingSeriesToggles` 已随之删除。

**只有在无法回避时**（回填与订阅都在代码后置、且回填在订阅之后）才需要抑制标志：

```csharp
_loadingSeriesToggles = true;
for (...) { _seriesToggles[i].Text = _seriesNames[i];   // 回填与订阅同在代码后置时
            _seriesToggles[i].Checked = true;           // ← 会触发 CheckedChanged
            _seriesToggles[i].CheckedChanged += SeriesToggle_CheckedChanged; }
_loadingSeriesToggles = false;
private void SeriesToggle_CheckedChanged(object sender, AntdUI.BoolEventArgs e)
{ if (_loadingSeriesToggles) return; RefreshParamCharts(); }
```

**现象 B（一次操作触发两次）**：同一控件的 `Click`/`CheckedChanged` **只允许在一处订阅**——若 Designer 的 `InitializeComponent()` 与代码后置构造函数各绑一次，一次操作会执行两遍。核验方法：对同一事件名统计 `.cs` 与 `.Designer.cs` 的 `+=` 次数（本轮 `checkbox1~4` 的 `CheckedChanged` 期望 **`.cs = 1 / Designer = 0`**）。

## 坑四：跨线程帧交接的 `Mat` 所有权——不释放别人的帧，也不能不释放自己的副本

**背景**：监控相机预览帧有**两个来源、两种所有权**：

| 来源 | 谁创建 | 谁释放 |
|---|---|---|
| `MonitorCamManager.PreviewFrameEvent` 抛出的帧 | 相机取流线程（每帧新副本） | **订阅方**（本页） |
| `MonitorCamManager.CurrentMat`（单次采集写入） | 相机管理器 | **相机管理器**，订阅方只读 |

**坑 4-1 · 释放了不属于自己的帧**：把 `CurrentMat` 当成自有副本 `Dispose()`，会破坏相机管理器的后续读帧（同一实例被复用）。**做法**：用所有权标志（本轮 `_displayedFrameOwned`）区分，只对自有副本调用 `Dispose()`。

**坑 4-2 · 自有副本不释放 ⇒ 内存压力**：相机帧是**非托管** `Mat`，30Hz 上屏若每帧都新建且不释放，GC + 终结器驱动下内存持续抖动。**做法**：新帧上屏后释放**上一帧**（`ImageBox` 继承 `PictureBox`，赋值即转位图，上一帧此刻已可安全释放）；被新帧顶替而**从未上屏**的待显示帧，在交接处就地释放。

**做法（本轮实现口径）**：

```csharp
// 相机线程：只入待显示槽；被顶替的待显示帧就地释放
Mat replaced = Interlocked.Exchange(ref _pendingPreviewFrame, frame);
if (replaced != null) { try { replaced.Dispose(); } catch { } }

// UI 线程 30Hz：取槽上屏 → 释放上一帧（仅当为自有副本且非同一实例）
imageBoxCam.Image = next;                       // 设计器声明的控件
Mat previous = _displayedFrame;
bool previousOwned = _displayedFrameOwned;
_displayedFrame = next; _displayedFrameOwned = owned;
if (previousOwned && previous != null && !ReferenceEquals(previous, next))
{ try { previous.Dispose(); } catch { } }
```

**配套**：`DisposeComponents()` 必须收尾——停表 → 退订 `PreviewFrameEvent` → 释放在槽帧与已上屏自制帧 → `imageBoxCam.Image = null`（控件本身随控件树释放，**不置空设计器字段**）；**页面不可见时应丢弃待显示帧**（否则切页期间空转做位图转换）。

## 编码前门禁清单（布局改版类任务）

- [ ] 布局改版方是否只改了 `.Designer.cs`？→ 逐控件对账代码后置引用（差集 0）
- [ ] 删除控件的三处（属性块 / 实例化 / 字段声明）是否都清了？旧职责是否已被新控件显式接管？
- [ ] **新增控件是否优先落在设计器（业主口径：设计器可见、不全部动态加载）？** 若落在代码后置，是否有正当理由？
- [ ] Designer 新增控件是否配齐：实例化 / 属性块 / `Controls.Add` / 成员声明 /（容器）`SuspendLayout+ResumeLayout` /（`ISupportInitialize` 控件）`BeginInit+EndInit`？
- [ ] Designer 落盘是否保持 **BOM 原状 + CRLF 同质 + `\r\r\n` 为 0**（字节安全脚本，按字符串锚点不按行号）？
- [ ] 新挂的 `CheckedChanged` / `Click` 是否只在**一处**订阅（`.cs` 与 Designer 不双写）？
- [ ] 初始值（`Text` / `Checked`）是否优先放设计器？若必须在代码回填且订阅已生效，是否用抑制标志包住？
- [ ] **非可视组件（`Timer` 等 `Component`）是否也在设计器声明（`new …(this.components)` 托管）？`.cs` 内是否已无 `new Timer()`、无手工 `Dispose()`？**
- [ ] **页面/窗体的 `.resx` 是否已登记进 csproj（`<EmbeddedResource>` + `<DependentUpon>`）？磁盘 `*.resx` 集合与 csproj 条目集合是否双向一致？**
- [ ] 新引入的跨线程资源（`Mat`/图像/句柄）所有权是否明确？谁创建谁释放？`DisposeComponents()` 是否收口？

## 关联

- [[api/MainPage]] — 本轮落地页（`InitSeriesToggles` / `InitCameraPreview` / 所有权标志 / 设计器 `imageBoxCam`；⛔ 2026-10-22：`InitCameraPreview` 与 `imageBoxCam` 已随主界面预览移除，`InitSeriesToggles` 此前亦已删）
- [[decisions/ADR-049-MainPageDualChartAndCamPreview]] — 本轮决策
- [[guides/WinForms-Designer]] — Designer 修改规范（字节安全 + `Dispose(bool)` 禁令）
- [[decisions/ADR-011-ButtonShadowDeviceSwitch]] — 运行期生成动态控件集合的先例（与「设计器可见」口径的边界）
- [[lessons/UiRefreshUnifiedEntry]] — UI 刷新单一入口（坑三现象 B 的同源问题）
- [[guides/Namespace-Compilation]] — 新增/移动 `.cs` 的 csproj 登记门禁
## 相关页面

- [[index/index]]
