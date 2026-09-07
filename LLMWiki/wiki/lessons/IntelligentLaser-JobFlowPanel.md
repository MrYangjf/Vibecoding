# 英莱 ILAlgoForm Job 流面板：flowPanel 动态按钮 + Modal 内联弹窗（2026-08-24）

## 背景

`ILAlgoForm` 重新布局：Job 选择从「下拉 Select」升级为「**按钮流**」（一个 Job 一个按钮，显示 Job 号+接头类型名），参数显示全部**事件触发**（删除手动「从设备读取」按钮）。

## 范式

### 1. flowPanel 动态 JOB 按钮流
- `RefreshJobFlow()`：`FetchJobList()`（jobdesclist.json）→ 每 Job 生成一个 `AntdUI.Button`（Text 两行 `"JOB {id}\n{类型名}"`，`Click += 闭包捕获 jobId`）加入 `flowPanel1.Controls`。
- **选中态**：`Button.Type = TTypeMini.Primary`（选中）/ `TTypeMini.Default`（未选中）——AntdUI 标准激活态，无需自定义着色。
- **数据流**：`_selectedJobId` 记录手动选中；`SyncSelectedJobFromDevice()` 在初始化/切 Job 回调时把选中态同步到设备当前 Job；`lblSelectJointType` 显示选中 Job 的接头类型名；`lblJointType` 显示**当前设备** Job 的接头类型（两者语义不同）。
- **重建即弃**：RefreshJobFlow 直接 `Controls.Clear()` + `_jobButtons.Clear()` 重建，闭包 lambda 无需退订（旧按钮对象整体丢弃回收）。

### 2. 删除保护
`btnDeleteJob`：先查 `FetchCurrentJobId()`，**选中 Job == 当前 Job 时拒绝删除**（弹 warn），确认弹窗用 `Modal.open(Config(form, "确认删除", msg, TType.Warn)) == DialogResult.OK` 判断。

### 3. 新建 JOB 弹窗：Modal 内联 FlowPanel（无独立 Form/UserControl 文件）

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

## 教训

1. **删控件必须同步清引用**：删除 Designer 按钮（btnFetch/btnSet）时，`.cs` 里的事件处理器（`btnFetch_Click`/`SetIlControlsEnabled` 中 `btnFetch.Enabled`）与输入框依赖（`txtJointType`/`txtJobDesc`）会留编译错误——重布局后先 grep 残留再改逻辑。
2. **「从设备读取」按钮已无意义**：参数全部走 SDK 回调（`OnJobParamsChanged` 事件），手动拉取按钮是冗余 UI。
3. **按钮流 vs 下拉**：flowPanel 按钮流适合「Job 数少、需要展示类型+ID」的场景；cmbJob 下拉（ILCamPage 简略版）适合仅切换。两者数据源相同（jobdesclist.json），互不冲突。
4. **Modal 内容控件必须给明确尺寸（2026-08-25）**：`Dock=Fill` 的裸容器（FlowPanel/Input 等）在 Modal 内容区高度塌缩为 0 → 弹窗空白。内容体应给显式 Width/Height（或包一层有明确高度的 Panel），`Modal.Config` 用 `TType.Info` + 明确 `Width`（参照 [[standards/UiStateSimplification]] 案例 ParamConfigPage.ShowInputStringDialog）。

## 关联

- 实现：[[api/IntelligentLaserCameraRun]]（`FetchJointTypes` / `GetJointTypeName` / `DeleteJob` / `CreateJob`）
- 模块：[[modules/IntelligentLaserCam]]
- 数据源：[[lessons/IntelligentLaser-JobListJsonSources]]
