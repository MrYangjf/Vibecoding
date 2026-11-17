---
title: IntelligentLaser-Job-System
date: 2026-10-30
updated: 2026-10-30
tags: [教训, 相机, 英莱, IntelligentLaser, 汇总, Job]
status: active
---


# 英莱相机教训：Job 体系

> 本页为 [[lessons/IntelligentLaser-Pitfalls]] 的拆分页，仅含第 7 节。

---


## 7. Job 体系教训（2026-08-24，原三独立页 2026-09-17 并入）

> 本节收拢原三个独立教训页（`lessons/IntelligentLaser-JobParamNoOfflineCache` / `lessons/IntelligentLaser-JobListJsonSources` / `lessons/IntelligentLaser-JobFlowPanel`）的全部技术事实；原页文件保留但不再单独维护，外部链接统一指向本节 §7.1–§7.3。注意：本页另有前章「6. 委托 GC 保护与 CallbackOnCollectedDelegate」（§6.1–§6.6），两章编号并列并存。

### 7.1 Job 参数离线缓存必须移除（设备为唯一真相源）

**结论（2026-08-24 用户澄清 + 代码精简）**：英莱 Job Parameter（设备侧算法参数）**以线激光设备为唯一真相源**——未连接设备即无 Job 参数，原离线缓存体系（`LoadOfflineCache` / `SaveOfflineCache` / `_ilIniFile` = `Config/Jobs/IntelligentLaserJobParams.ilini` / `HasJobParamCache`）**整体移除**。

**根因**：

1. **离线缓存会误导用户**：程序异常退出（崩溃/强杀）后重连，硬件端 Job 参数可能与上次落盘的 `.ilini` 不一致；离线缓存显示的是「上次成功写盘的旧值」而非设备实际值，违反「UI 状态真值来自硬件查询」（同 §5.4）原则。
2. **设备是唯一来源**：`InitJobParamsCallback`（全量元数据）与 `JobParamsChangedCallback`（当前 Job 参数集/增量）两个 SDK 回调已能在连接后实时把 Job 参数推到 `_jobParams` 缓存；切 JOB / 改参数都会经 `OnJobParamsChanged` 刷新，无需本地落盘兜底。
3. **无「枚举所有 Job 号」API**（2026-08-24 当时认知，后被 §7.2 落盘 JSON 补齐）：英莱 SDK 仅 `FetchJobInfo`（查当前 Job ID）+ `SetSensorJobInfo`（切换/新建/删除），没有列出全部 Job 号的能力——`cmbJob` 只能以「当前 Job」为唯一可选项（官方 demo 同样无 Job 列表 UI），因此「离线缓存所有 Job 号」本就无从谈起。

**修改清单（本次落地）**：

| 位置 | 改动 |
|------|------|
| `IntelligentLaserCam.cs` | 删 `_ilIniFile` / `LoadOfflineCache` / `SaveOfflineCache` / `HasJobParamCache` 及 3 处 `SaveOfflineCache` 调用；新增 `OnJobParamsChanged` 回调注册（`_cbJobParamsChanged`+GCHandle，遵循 GC 三层保护）、`JobParamsChangedCallback`（按名增量刷新 `_jobParams`）、`JobParamsChanged` 事件 |
| `ILCamPage.cs` | `RefreshJobSelect` 连接同步时从设备读当前 Job 预填 `cmbJob`（保持原逻辑，删离线无关代码无影响） |
| `ILAlgoForm.cs` | `InitIlModule` 删「拉取失败回退离线缓存」分支（未连接→空表；该 fallback 原记录于本页 §5.4，随本条一并失效）；订阅 `JobParamsChanged` → 重拉 `FetchAllJobParams` 刷新；`dgvILParams.CellEndEdit` 单元格级单条 `ApplyJobParams`（成功回读刷新该格、失败恢复原值），移除整表 `btnSet` 按钮 |
| `ILAlgoForm.Designer.cs` | 删除 `btnSet` 控件声明/初始化/字段（CellEndEdit 取代批量下发） |

关联：[[api/IntelligentLaserCam]]（`JobParamsChanged` / `OnJobParamsChanged` 回调契约）、[[standards/CodeSimplification]] / [[standards/UiStateSimplification]]（代码精简规范）；UI 不缓存设备态真相源另见 §5.17（2026-09-17 并入自 IntelligentLaserSensorControl 页）。

### 7.2 Job 列表与接头类型数据源：运行目录 JSON

**背景**：曾误判「SDK 未提供 JOB 列表枚举 API，只能显示当前 JOB」（见 §7.1 根因 3）。英莱技术人员确认：**连接相机后，原生 SDK 会在运行目录自动落盘两个 JSON**，分别提供「全部 Job 号」与「接头类型语义」，补齐了 Job 列表与参数对应显示两个缺口。

**数据源（运行目录 = `AppDomain.CurrentDomain.BaseDirectory`）**：

- **`IntelligentLaser_jobdesclist.json` —— 全部 Job**：

  ```json
  [{"jobdescribe":"","jointtype":32,"id":1},{"jobdescribe":"","jointtype":33,"id":2}, ...]
  ```

  `id`：Job 号；`jointtype`：接头类型编号（对应 jointtypelist 的 `int`）；`jobdescribe`：Job 描述。用途：`FetchJobList()` 解析 → `cmbJob` 下拉全量填充（需求①「读取所有 job 号」落地）。

- **`IntelligentLaser_jointtypelist.json` —— 接头类型语义字典**：

  ```json
  {"joint_types":[{"hex":"0x10","int":16,"name_zh":"左搭接","name_en":"Left-Lap",
    "lines":[{"line":[1,2],"name_zh":"左直线","name_en":"Left Line","order":1}, ...],
    "calculations":[{"type":"single_line_multi_value","line":[1,2]}, ...],
    "display":{"params_inspect_bp":0,"params_inspect_min_angle":90, ...},
    "green":["params_inspect_min_angle","params_inspect_max_angle"],
    "blue":["params_inspect_min_area","params_inspect_max_area"],
    "orange":["params_inspect_min_height1","params_inspect_max_height1"]}, ...]}
  ```

  - 覆盖 20+ 接头类型：16 左搭接 / 17 右搭接 / 32 对接 / 33 微对接 / 34 双卷边对接 / 48 厚板外角焊缝 / 49 V坡口 / 50-53 左右侧(半)V坡口 / 64 内角焊缝 / 65 外角焊缝 / 66-67 方管左右搭接 / 80 平板 / 96-97 直线圆管 / 112 圆对接 / 128 圆检测。
  - `display`：**该接头类型应显示的参数 key → 默认值**（后续 UI 拆分「相机参数 vs Job 算法参数」可据此过滤）。
  - `green`/`blue`/`orange`：参数类别分组（如 32 对接：blue=面积、orange=角度/高度/宽度），可作表格着色依据。

**教训**：

1. **官方 demo 与 SDK C# 包装都不读这两个 JSON**（原生层生成）——解析必须自行实现。本项目用 Newtonsoft.Json（csproj 已引用 `3rdDepend\Newtonsoft.Json.dll`），`IlJobDescInfo`/`IlJointTypeInfo` 字段按 JSON 小写键命名，Newtonsoft 大小写不敏感自动匹配。
2. **文件位置是运行目录（BaseDirectory），不是 Config 子目录**——与已删除的 `.ilini` 离线缓存（`Config/Jobs/`，见 §6.1）位置不同，勿混淆。
3. **未连接时文件可能残留上次连接的旧数据**——UI 必须「已连接才读」（`ILCamPage` 断开时清空 `cmbJob`，`RefreshJobSelect` 未连接直接 return），与「无线激光即无 Job」语义一致，不缓存不兜底。
4. `cmbJob` 下拉项从纯字符串 `"JOB N"` 升级为 `CmbJobItem` 对象（JobId + Text），切换/按钮态判定直取 JobId，移除 `Replace("JOB","").Trim()+TryParse` 脆弱解析。

关联：实现见 [[api/IntelligentLaserCam]]（`FetchJobList` / `GetJointTypeName` / `GetCurrentJobInfo`）。

### 7.3 ILAlgoForm Job 流面板：flowPanel 动态按钮 + Modal 内联弹窗

**背景**：`ILAlgoForm` 重新布局：Job 选择从「下拉 Select」升级为「**按钮流**」（一个 Job 一个按钮，显示 Job 号+接头类型名），参数显示全部**事件触发**（删除手动「从设备读取」按钮）。

**范式 1：flowPanel 动态 JOB 按钮流**

- `RefreshJobFlow()`：`FetchJobList()`（jobdesclist.json，见 §7.2）→ 每 Job 生成一个 `AntdUI.Button`（Text 两行 `"JOB {id}\n{类型名}"`，`Click += 闭包捕获 jobId`）加入 `flowPanel1.Controls`。
- **选中态**：`Button.Type = TTypeMini.Primary`（选中）/ `TTypeMini.Default`（未选中）——AntdUI 标准激活态，无需自定义着色。
- **数据流**：`_selectedJobId` 记录手动选中；`SyncSelectedJobFromDevice()` 在初始化/切 Job 回调时把选中态同步到设备当前 Job；`lblSelectJointType` 显示选中 Job 的接头类型名；`lblJointType` 显示**当前设备** Job 的接头类型（两者语义不同）。
- **重建即弃**：RefreshJobFlow 直接 `Controls.Clear()` + `_jobButtons.Clear()` 重建，闭包 lambda 无需退订（旧按钮对象整体丢弃回收）。

**范式 2：删除保护**

`btnDeleteJob`：先查 `FetchCurrentJobId()`，**选中 Job == 当前 Job 时拒绝删除**（弹 warn），确认弹窗用 `Modal.open(Config(form, "确认删除", msg, TType.Warn)) == DialogResult.OK` 判断。

**范式 3：新建 JOB 弹窗：Modal 内联 FlowPanel（无独立 Form/UserControl 文件）**

> ⚠️ **2026-08-25 空白修复**：初版用 `AntdUI.FlowPanel { Dock = DockStyle.Fill }` 作 Modal 内容体，**显示空白**——裸容器在 Modal 内容区高度塌缩为 0（与 ShowInputStringDialog 注释记录的裸 Input 高度 0 同类）。修复：改用 `System.Windows.Forms.FlowLayoutPanel`（**明确 Width=300/Height=360/AutoScroll=true**）+ `Modal.Config(TType.Info){ Width=320 }`（参照 ParamConfigPage.ShowInputStringDialog 范式）。

```csharp
var flow = new System.Windows.Forms.FlowLayoutPanel
{
    Width = 300,
    Height = 360,
    AutoScroll = true,
    Padding = new Padding(8)
};
foreach (IlJointTypeInfo jt in _ilCamera.FetchJointTypes())
{
    var b = new AntdUI.Button { Text = string.Format("{0} ({1})", jt.NameZh, jt.Int), ... };
    int type = jt.Int; // 闭包必须拷贝循环变量
    b.Click += (s, e) => { int ret = _ilCamera.CreateJob(type, "");
        var host = flow.FindForm(); // Modal 承载的宿主 Form
        if (ret == 0) { if (host != null) host.DialogResult = DialogResult.OK; RefreshJobFlow(); RefreshJobParams(); } };
    flow.Controls.Add(b);
}
AntdUI.Modal.open(new AntdUI.Modal.Config(this.FindForm(), "新建JOB - 选择接头类型", flow, TType.Info)
{ Width = 320, CloseIcon = true, BtnHeight = 0 });
```

- **`BtnHeight = 0`**：Modal 不显示底部按钮，内容控件自管交互与关闭。
- **关闭**：内容控件内 `flow.FindForm().DialogResult = DialogResult.OK`（同 ILScanForm 范式）。
- **闭包陷阱**：循环变量 `jt` 必须拷贝到局部变量（`int type = jt.Int`），否则所有按钮共用最后一个值（C# 5+ foreach 变量已安全，但显式拷贝更稳）。

**教训**：

1. **删控件必须同步清引用**：删除 Designer 按钮（btnFetch/btnSet）时，`.cs` 里的事件处理器（`btnFetch_Click`/`SetIlControlsEnabled` 中 `btnFetch.Enabled`）与输入框依赖（`txtJointType`/`txtJobDesc`）会留编译错误——重布局后先 grep 残留再改逻辑。
2. **「从设备读取」按钮已无意义**：参数全部走 SDK 回调（`OnJobParamsChanged` 事件），手动拉取按钮是冗余 UI。
3. **按钮流 vs 下拉**：flowPanel 按钮流适合「Job 数少、需要展示类型+ID」的场景；cmbJob 下拉（ILCamPage 简略版）适合仅切换。两者数据源相同（jobdesclist.json），互不冲突。
4. **Modal 内容控件必须给明确尺寸（2026-08-25）**：`Dock=Fill` 的裸容器（FlowPanel/Input 等）在 Modal 内容区高度塌缩为 0 → 弹窗空白。内容体应给显式 Width/Height（或包一层有明确高度的 Panel），`Modal.Config` 用 `TType.Info` + 明确 `Width`（参照 [[standards/UiStateSimplification]] 案例 ParamConfigPage.ShowInputStringDialog）。

关联：实现见 [[api/IntelligentLaserCam]]（`FetchJointTypes` / `GetJointTypeName` / `DeleteJob` / `CreateJob`）；数据源见 §7.2。
## 相关页面

- [[lessons/IntelligentLaser-Sdk-Interop]] —— 同源拆分页
- [[lessons/IntelligentLaser-Callback-Mechanism]] —— 同源拆分页
- [[lessons/IntelligentLaser-Ui-State]] —— 同源拆分页
- [[lessons/IntelligentLaser-Delegate-Gc]] —— 同源拆分页
- [[lessons/IntelligentLaser-Pitfalls]] —— 源页（拆分前全量）
