---
title: AlgorithmEditForm 算法编辑弹窗
date: 2026-07-17
tags: [API, UI, 算法, 配置, SubView, Modal]
---

# AlgorithmEditForm — 算法编辑弹窗

> 配置当前 Job 各算法阶段的「方法（Operation）」与「参数（Parameters）」的 UI 编辑器（**模块 A：EmguALG**）。
> 另含 **模块 B：英莱相机参数 (IntelligentLaser)** —— 编辑英莱设备侧 Job Parameter 并实时显示 `IlInspectResult` 识别结果（仅当前激活相机为英莱时可用）。
> 仅做配置编辑，**不实现任何图像处理算法**（符合 [[decisions/ADR-003-SingleAlgorithmFile]]）。

## 基本信息

| 项 | 值 |
|----|----|
| 命名空间 | `AdaWeldSystem.Sub3UI` |
| 基类 | `AntdUI.Window`（窗体对话框，AntdUI 无 UIForm2 基类） |
| 文件 | `UIDesign/Sub3UI/AlgorithmEditForm.cs` + `.Designer.cs` |
| 调用方 | `Sub2UI/LLCamWorkJob.cs`（现役 `UIDesign/TabPage/ILCamPage.cs`） 的 `btnEditJob_Click`（经 `ShowDialog(this)`），**替代原 TODO** |
| 关联模块 | [[modules/EmguALG]]、[[modules/UIDesign]]、[[modules/IntelligentLaserCam]]、[[api/IntelligentLaserCameraRun]] |

## 构造函数

```csharp
public AlgorithmEditForm(PipelineConfig config)
```

- `config`：当前 Job 的 `PipelineConfig`（即 `JobManager.Instance.CurrentJob.Config`），**就地编辑**；为 `null` 时抛 `ArgumentNullException`。

## 界面控件

> **容器（2026-07-27 按 [[decisions/ADR-017-AlgorithmEditInterfaceSplit]] 做接口分隔；2026-07-28 随 [[decisions/ADR-018-UIFrameworkMigration]] 迁移为 AntdUI）**：`GroupBox`(`panelMain`，标题由 `.Text` 承载) → 主 `TableLayoutPanel`（2 行：Tab + 底部按钮）→ `AntdUI.Tabs`(`tabsAlgo`)。两个子页 `EmguAlgoPage`("项目算法 (EmguALG)") / `ILAlgoPage`("英莱相机算法 (IntelligentLaser)") 均为 `UserControl`，构造期按 `CameraSelector.Active` 类型经 `tabsAlgo.AddTabSelect(UserControl)` **仅挂载匹配的那一页**（另一页根本不创建），实现「隐藏不使用的那一个」。底部 `tableLayoutPanelButtons`(确定/取消) 常驻、置于 `Tabs` 之外。

| 控件 | 类型（AntdUI） | 说明 |
|------|------|------|
| `cmbStage` | `AntdUI.Select` |（EmguAlgoPage）阶段选择：滤波 / 形态学 / 边缘检测 / 特征提取 / 模板匹配 |
| `chkEnabled` | `AntdUI.Checkbox` |（EmguAlgoPage）「启用此阶段」；仅滤波/形态学/边缘检测可见 |
| `cmbMethod` | `AntdUI.Select` |（EmguAlgoPage）当前阶段方法，填充对应枚举（`FilterOperation` / `MorphologyOperation` / `EdgeDetectionOperation` / `FeatureExtractionOperation` / `TemplateMatchOperation`） |
| `dgvParams` | `AntdUI.Table` |（EmguAlgoPage）两列「参数名 / 参数值」，编辑 `StageBase.Parameters` 字典（模块 A）；数据绑定 `AntList<T>` |
| `btnResetParams` | `AntdUI.Button` |（EmguAlgoPage）按当前方法重置参数为默认值 |
| `btnOK` / `btnCancel` | `AntdUI.Button` |（宿主窗体）确定 / 取消（仅持久化模块 A） |
| `lblConn` | `AntdUI.Label` |（ILAlgoPage）模块 B 连接状态：「英莱设备：已连接」(绿) / 「未连接」(红) / 「当前相机非英莱，参数不可用」(灰) |
| `btnFetch` | `AntdUI.Button` |（ILAlgoPage）模块 B「从设备读取」：调 `IntelligentLaserCameraRun.FetchAllJobParams()`，仅连接时可点 |
| `dgvILParams` | `AntdUI.Table` |（ILAlgoPage）模块 B 4 列「名称 / 值 / 类型 / 范围」，编辑英莱 Job Parameter；离线时只读 |
| `btnSet` | `AntdUI.Button` |（ILAlgoPage）模块 B「下发到设备」：回读网格→范围校验→`ApplyJobParams`；超界/格式错误拦截并 Warning 日志 |
| `dgvResult` | `AntdUI.Table` |（ILAlgoPage）模块 B 3 列「字段 / 值 / 单位」（只读），实时显示 `IlInspectResult`（150ms Timer 刷新） |

## 行为契约

1. **阶段切换**：`cmbStage_SelectedIndexChanged` —— 切换前先 `SyncGridToParams` 将上一阶段网格编辑写回字典，避免丢失；再 `LoadStage` 加载新阶段。
2. **加载阶段**（`LoadStage`）：用 `_loading` 标志保护，设置 `cmbMethod.SelectedItem` / `chkEnabled.Checked` 时不触发 `Operation` 重置（否则覆盖已保存参数）；随后 `LoadParamsToGrid` 展示当前 `Parameters`。
3. **切换方法**（`cmbMethod_SelectedIndexChanged`）：调用 `SetStageOperation` → `StageBase.Operation` setter 内部 `ResetParametersForOperation` 重置为该方法默认参数，并刷新网格。
4. **确定**（`btnOK_Click`）：`SyncGridToParams` 当前阶段 → `var host = FindForm(); if (host != null) host.DialogResult = DialogResult.OK;`（Modal 承载的 UserControl 无 `DialogResult`/`Close`，设宿主 Modal 的 `DialogResult` 即关闭并令 `Modal.open` 返回 OK，见 [[guides/AntdUI-Reference]]）。
5. **调用方持久化**（位于 `LLCamWorkJob.btnEditJob_Click`）：`PipelineManager.Instance.SetConfig(job.Config.Clone())` 应用到运行流水线 + `JobManager.Instance.UpdateJobConfig(job.JobId, job.Config)` 写入 INI + `UpdateConfigSummary()` 刷新显示。

## 页切换（接口分隔，2026-07-27）

构造期 `_ilCamera = CameraSelector.Active as IntelligentLaserCameraRun;` 之后**条件性挂载子页**（AntdUI 下经 `tabsAlgo.AddTabSelect(UserControl)`，非 `RemovePage`；原 SunnyUI 时代用 `UITabControl.AddPage(UIPage)`，见 [[decisions/ADR-017-AlgorithmEditInterfaceSplit]]）：

- `_ilCamera != null`（当前激活相机为英莱）→ 仅 `tabsAlgo.AddTabSelect(new ILAlgoPage(_ilCamera))`，显示「英莱相机算法」页；`EmguAlgoPage` 根本不创建；
- 否则（EmguALG / SmartRay / 虚拟等）→ 仅 `tabsAlgo.AddTabSelect(new EmguAlgoPage(config))`，显示「项目算法」页；`ILAlgoPage` 根本不创建。

由于未匹配的页从不实例化，天然实现「隐藏不使用的那一个」且零 `RemovePage`/`SelectedTab` 操作。窗口生命周期内激活相机不变，故仅构造期执行一次，无需运行中动态切换。详见 [[decisions/ADR-017-AlgorithmEditInterfaceSplit]]、[[decisions/ADR-018-UIFrameworkMigration]]。

## 模块 B：英莱相机参数（IntelligentLaser）

仅当 `CameraSelector.Active is IntelligentLaserCameraRun` 时启用；否则 `InitIlModule()` 显示「当前相机非英莱，参数不可用」并禁用所有英莱控件（离线缓存只读展示）。

1. **初始化**（`InitIlModule`）：连接态经 `UpdateConnLabel` 显示绿/红；连接时优先 `LoadOfflineCache()` 恢复，必要时 `FetchAllJobParams()` 拉设备实时值；离线时仅 `LoadOfflineCache()` 只读；无论是否连接都 `StartResultTimer()` 启动 150ms 结果刷新。
2. **读取**（`btnFetch_Click`）：调 `_ilCamera.FetchAllJobParams()` → `LoadIlParamsToGrid`，异常记 `Error` 日志。
3. **下发**（`btnSet_Click`）：从 `dgvILParams` 回读编辑值 → 按 `HasRange` 做 float/int 范围校验（类型解析失败或超界 → 记 `Warning` 日志并**阻止下发**）→ `_ilCamera.ApplyJobParams(edited)`，ret==0 记 `Info` 否则 `Error`。
4. **结果刷新**（`RefreshTimer_Tick`→`RefreshResult`）：`System.Windows.Forms.Timer`(150ms) 在 UI 线程触发，故直接读 `LastInspectResult` 无需 `BeginInvoke`；无结果时显示「状态/无识别结果」。
5. **回收**（`AlgorithmEditForm_HandleDestroyed`，订阅 `this.HandleDestroyed`）：经 `ILAlgoPage.StopTimer()` 停止 `_refreshTimer`（2026-07-30 经 [[decisions/ADR-019-DialogWindowToModalUserControl]] 由 `FormClosing` 改 `HandleDestroyed`——UserControl 无 `FormClosing`；遵循 [[decisions/ADR-001-DisposePattern]]：`.cs` 不重写 `Dispose(bool)`，Timer 由 Designer `Dispose` 释放）。

> 模块 B 所有 SDK 交互均经 `IntelligentLaserCameraRun` 封装（`FetchAllJobParams`/`ApplyJobParams`/`HasJobParamCache`/`LoadOfflineCache`），UI **不直连 `IntelligentLaser_export`**（呼应 [[api/IntelligentLaserSDK_CSharp_DevManual]] §7）。

## 设计约束

- 遵循 [[decisions/ADR-001-DisposePattern]]：`.cs` 未重写 `Dispose(bool)`，标准 Designer `Dispose` 不变。
- 遵循 [[guides/WinForms-Designer]]：控件声明于 `.Designer.cs`，`InitializeComponent()` 不含 `for`/`while`/`if`/`switch`/`foreach`。
- 遵循 [[guides/Namespace-Compilation]]：已注册至 `AdaWeldSystem.csproj`。
- 符合 [[decisions/ADR-003-SingleAlgorithmFile]]：本窗体只编辑 `PipelineConfig`，不新增任何算法实现（算法集中于 `ImageAlgorithm.cs`）。
- **布局范式（2026-07-27 按 [[decisions/ADR-017-AlgorithmEditInterfaceSplit]] 做接口分隔；2026-07-28 随 [[decisions/ADR-018-UIFrameworkMigration]] 迁移为 AntdUI）**：本窗体作为**单独个例**采用 `AntdUI.Tabs` + 两 `UserControl` 子页（EmguALG / IntelligentLaser，`AntdUI.Tabs` 经 `AddTabSelect(UserControl)` 挂载子页），按激活相机接口条件 `AddTabSelect` 匹配页；底部确定/取消按钮常驻于 `Tabs` 之外。此为本项目「弃 Tab」惯例下**仅记录的特例**，不推翻 2026-07-17 项目级决定（见 ADR-017）。主题由 AntdUI `Config.IsLight` 控制（原 SunnyUI Purple 主题见 [[project/SunnyUI-Legacy]]，已 deprecated）。
- **模块 B 后端 `TIntelligentJobParam.CurValue`/`value_Range` 字段名待 VS x64 构建确认**（QA P0，首次使用此类类型）。

## 已知限制

- `TemplateMatchStage.ShowResult`（结果显示开关）未在窗体中暴露，暂保持默认 `true`。
- `FeatureExtractionStage.ApproximationMethod` 作为 `Parameters["approximationMethod"]` 出现在参数网格中，以文本形式编辑。
- 模块 B 仅暴露「从设备读取 / 下发到设备」与结果只读展示；英莱 Job Parameter 的**名称/类型/范围不硬编码**，完全依赖 `RecvInitJobParamsInfo` 初始化回调下发，离线无缓存时网格为空。
- 模块 B 的连接态在窗体打开时快照（`_ilConnected`），窗体生命周期内不随设备热插拔刷新（结果区 Timer 仍持续读最新 `LastInspectResult`）。

---

*来源：2026-07-17 初版（`Sub3UI/AlgorithmEditForm.cs` + `.Designer.cs` + `LLCamWorkJob.btnEditJob_Click` 接线）；2026-07-26 扩展模块 B（英莱相机参数 + 实时识别结果，见 [[api/IntelligentLaserCameraRun]] 与 [[modules/IntelligentLaserCam]]）；2026-07-27 改为 `UITabControl` + 两 `UIPage` 子页接口分隔（[[decisions/ADR-017-AlgorithmEditInterfaceSplit]]），条件 `AddPage` 按相机接口显示对应页；2026-07-30 经 [[decisions/ADR-019-DialogWindowToModalUserControl]] 由 `AntdUI.Window` 改为 `UserControl` 迁入 `SubView/`，调用点改 `AntdUI.Modal.open`、`FormClosing`→`HandleDestroyed`（见 [[guides/AntdUI-Reference]]）。*
