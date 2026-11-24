---
title: CodeMap-Symbols-UIDesign — 代码地图·符号签名层·UIDesign（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 符号索引, 机器生成]
status: accepted
---

# CodeMap-Symbols-UIDesign — UIDesign 的类型与签名

> **一句话**：模块 `UIDesign` 的全部类型 → `文件:行` → 成员签名；⛔ 由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> UI 页面与权限：主界面 / 工艺 / 系统设置 / 追溯
> 总览见 [[architecture/CodeMap]]；调用关系见 [[architecture/CodeMap-Relations]]。

## 命名空间一览

| 命名空间 | 文件 | 类型 | 功能 | 模块归属 | 约束 ADR |
|---|---|---|---|---|---|
| `AdaWeldSystem.UIDesign.TabPage` | 6 | 20 | UI · 系统参数设置子页 | [[modules/UIDesign]] | ADR-008/036/055/057 |
| `AdaWeldSystem.UIDesign.ControlPage` | 4 | 10 | UI · 主内容页（主页面/数据追溯） | [[modules/UIDesign]] | ADR-008/049/053 |
| `AdaWeldSystem.UIDesign.SubDialog.DataReviewerDialog` | 4 | 5 | UI · 弹窗 · 数据回溯 | [[modules/UIDesign]] | ADR-009/036 |
| `AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog` | 4 | 7 | UI · 弹窗 · 英莱相机 | [[modules/UIDesign]] | ADR-009/012/036 |
| `AdaWeldSystem.UIDesign.SubDialog.UserManagerDialog` | 2 | 3 | UI · 弹窗 · 登录与用户管理（权限来源） | [[modules/UIDesign]] | ADR-009/036 |
| `AdaWeldSystem.UIDesign.MainWindow` | 1 | 1 | UI · 主窗体 | [[modules/UIDesign]] | ADR-008 |
| `AdaWeldSystem.UIDesign.SubDialog.CommConfigDialog` | 1 | 2 | UI · 弹窗 · 通讯配置 | [[modules/UIDesign]] | ADR-009/036 |
| `AdaWeldSystem.UIDesign.SubDialog.FormMainDialog` | 1 | 1 | UI · 弹窗 · 主窗体辅助（初始化等待） | [[modules/UIDesign]] | ADR-009 |
| `AdaWeldSystem.UIDesign.SubDialog.MonitorCamDialog` | 1 | 2 | UI · 弹窗 · 监控相机扫描 | [[modules/UIDesign]] | ADR-009/046 |
| `AdaWeldSystem.UIDesign.SubDialog.MotionControlDialog` | 1 | 2 | UI · 弹窗 · 运控配置 | [[modules/UIDesign]] | ADR-009/036 |
| `AdaWeldSystem.UIDesign.SubDialog.ParamContolDialog` | 1 | 2 | UI · 弹窗 · 焊参配置 | [[modules/UIDesign]] | ADR-009/036 |

| 项 | 值 |
|---|---|
| 类型数 | 55 |
| 方法数 | 870 |

## 章节导航

- [AutoParamForm](#AutoParamForm)
- [AutoParamRow](#AutoParamRow)
- [AxisConfigForm](#AxisConfigForm)
- [AxisConfigPreviewRow](#AxisConfigPreviewRow)
- [AxisReadoutSnapshot](#AxisReadoutSnapshot)
- [AxisRow](#AxisRow)
- [CameraParamRow](#CameraParamRow)
- [CmbJobItem](#CmbJobItem)
- [CommSettingPage](#CommSettingPage)
- [ConfigListRow](#ConfigListRow)
- [CylinderConfigPreviewRow](#CylinderConfigPreviewRow)
- [DataReviewRow](#DataReviewRow)
- [DataReviewerPage](#DataReviewerPage)
- [DeviceMonitorPage](#DeviceMonitorPage)
- [DeviceRow](#DeviceRow)
- [FileEditorForm](#FileEditorForm)
- [FileTraceForm](#FileTraceForm)
- [FileTraceRow](#FileTraceRow)
- [FilebackupPage](#FilebackupPage)
- [FormMain](#FormMain)
- [GalvoSnapshot](#GalvoSnapshot)
- [HelixRenderForm](#HelixRenderForm)
- [HoverHit](#HoverHit)
- [ILAlgoForm](#ILAlgoForm)
- [ILAlgorithmEditForm](#ILAlgorithmEditForm)
- [ILParamForm](#ILParamForm)
- [ILScanForm](#ILScanForm)
- [IlJobParamRow](#IlJobParamRow)
- [InitWaitingForm](#InitWaitingForm)
- [InspectResultRow](#InspectResultRow)
- [IoConfigPreviewRow](#IoConfigPreviewRow)
- [LaMotorSnapshot](#LaMotorSnapshot)
- [LineLaserCamPage](#LineLaserCamPage)
- [LoginForm](#LoginForm)
- [MainPage](#MainPage)
- [ManualOpOutcome](#ManualOpOutcome)
- [MonitorCamPage](#MonitorCamPage)
- [MonitorCamScanForm](#MonitorCamScanForm)
- [NavPage](#NavPage)
- [PlaybackRow](#PlaybackRow)
- [ProcessControlPage](#ProcessControlPage)
- [RecordConfigForm](#RecordConfigForm)
- [RefreshSnapshot](#RefreshSnapshot)
- [RenderParamForm](#RenderParamForm)
- [RowSpec](#RowSpec)
- [SensorRow](#SensorRow)
- [SeriesGroup](#SeriesGroup)
- [SeriesItem](#SeriesItem)
- [SessionCharts](#SessionCharts)
- [SystemControlPage](#SystemControlPage)
- [TemperatureSnapshot](#TemperatureSnapshot)
- [TxCmdOption](#TxCmdOption)
- [UserEditForm](#UserEditForm)
- [UserRow](#UserRow)
- [XmlPropertyRow](#XmlPropertyRow)

## AutoParamForm

- 签名：`partial class AutoParamForm`
- 位置：`UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:9`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.ParamContolDialog`
- 方法（5）：
  - `void uiDataGridView1_CellEndEdit(object sender, AntdUI.TableEndEditEventArgs e)` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:35`
  - `void InitTableColumns()` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:67`
  - `void UpdateParamValues()` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:86`
  - `void EffectiveSwingFrequency(AutoParam autoParam, double swingWidthMm)` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:126`
  - `void LoadConfigData(AutoParam autoParam)` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:151`
- 构造（2）：
  - `AutoParamForm()` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:18`
  - `AutoParamForm(Window _window)` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:20`

## AutoParamRow

- 签名：`public class AutoParamRow`
- 位置：`UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:137`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.ParamContolDialog`
- 属性（6）：
  - `string SeamWidth { get; set; }` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:139`
  - `string RobotSpeed { get; set; }` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:140`
  - `string FeedSpeed { get; set; }` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:141`
  - `string LaserPower { get; set; }` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:142`
  - `string SwingWidth { get; set; }` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:145`
  - `string SwingFrequency { get; set; }` — `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs:148`

## AxisConfigForm

- 签名：`public partial class AxisConfigForm : UserControl`
- 位置：`UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:12`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.MotionControlDialog`
- 方法（15）：
  - `void BuildRowSpecs()` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:118`
  - `void FieldRow(string caption, TextBox box)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:162`
  - `void EditorRow(string caption, Control editor)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:167`
  - `void Section(string caption)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:172`
  - `void BuildLayout(List<RowSpec> rows)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:178`
  - `void BtnOk_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:330`
  - `void BtnCancel_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:343`
  - `void LoadValues()` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:349`
  - `void ParseDouble(string s, double def)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:387`
  - `void ParseUShort(string s, ushort def)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:392`
  - `void ParseShort(string s, short def)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:400`
  - `void ParseInt(string s, int def)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:405`
  - `void TryNumber(TextBox box, double value)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:410`
  - `bool Validate(string error)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:419`
  - `void Commit()` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:478`
- 构造（2）：
  - `AxisConfigForm(DeltaAxisConfig config)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:64`
  - `AxisConfigForm(DeltaAxisConfig config, DeltaTaHomeConfig taHome)` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:72`
- 属性（2）：
  - `bool HasAxisSpecificSection { get; set; }` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:51`
  - `bool Committed { get; set; }` — `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:57`

## AxisConfigPreviewRow

- 签名：`public class AxisConfigPreviewRow`
- 位置：`UIDesign/TabPage/FilebackupPage.cs:1599`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 属性（19）：
  - `string AxisName { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1602`
  - `string NodeId { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1605`
  - `string SlotNo { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1608`
  - `string Enabled { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1611`
  - `string Equiv { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1614`
  - `string StrVel { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1617`
  - `string ConstVel { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1620`
  - `string AccTime { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1623`
  - `string DecTime { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1626`
  - `string STime { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1629`
  - `string EndVel { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1632`
  - `string HomeMode { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1635`
  - `string HomeOffset { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1638`
  - `string HomeFirstVel { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1641`
  - `string HomeSecondVel { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1644`
  - `string HomeAcc { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1647`
  - `string PositiveLimit { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1650`
  - `string NegativeLimit { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1653`
  - `string SoftLimitMode { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1656`

## AxisReadoutSnapshot

- 签名：`private sealed class AxisReadoutSnapshot`
- 位置：`UIDesign/TabPage/SystemControlPage.cs:2802`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 成员：（无）

## AxisRow

- 签名：`public class AxisRow`
- 位置：`UIDesign/TabPage/SystemControlPage.cs:41`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 属性（12）：
  - `string AxisName { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:43`
  - `string Position { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:44`
  - `CellBadge PositiveLight { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:45`
  - `CellBadge NegativeLight { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:46`
  - `CellBadge OriginLight { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:47`
  - `CellBadge AlarmLight { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:48`
  - `CellBadge ServoLight { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:49`
  - `string LayoutValue { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:50`
  - `string TargetPos { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:51`
  - `CellLink[] ParamBtn { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:52`
  - `DeltaAxisConfig Config { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:53`
  - `string Feedback { get; set; }` — `UIDesign/TabPage/SystemControlPage.cs:55`

## CameraParamRow

- 签名：`public class CameraParamRow`
- 位置：`UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:24`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog`
- 属性（7）：
  - `string Name { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:27`
  - `string Value { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:28`
  - `string Range { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:33`
  - `string Unit { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:34`
  - `string Desc { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:35`
  - `int Kind { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:36`
  - `IlJobParamInfo JobParam { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:37`

## CmbJobItem

- 签名：`private class CmbJobItem`
- 位置：`UIDesign/TabPage/LineLaserCamPage.cs:686`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 方法（1）：
  - `string ToString()` — `UIDesign/TabPage/LineLaserCamPage.cs:690`

## CommSettingPage

- 签名：`partial class CommSettingPage`
- 位置：`UIDesign/TabPage/CommSettingPage.cs:15`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 方法（22）：
  - `void CommSettingPage_HandleCreated(object sender, EventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:75`
  - `void CommSettingPage_HandleDestroyed(object sender, EventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:83`
  - `void GlobalCommData_CommunicationCommandReceived(object sender, string e)` — `UIDesign/TabPage/CommSettingPage.cs:92`
  - `void GlobalCommData_CommLogViewEvent(object sender, string e)` — `UIDesign/TabPage/CommSettingPage.cs:123`
  - `void LoadConfig()` — `UIDesign/TabPage/CommSettingPage.cs:152`
  - `void selectRsiCycle_SelectedIndexChanged(object sender, AntdUI.IntEventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:188`
  - `void SaveConfig()` — `UIDesign/TabPage/CommSettingPage.cs:199`
  - `void chkEnable_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:210`
  - `void ApplyEnableState()` — `UIDesign/TabPage/CommSettingPage.cs:228`
  - `void btnRobotStart_Click(object sender, EventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:239`
  - `void btnRobotStop_Click(object sender, EventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:273`
  - `void TryPassCommAction(string action)` — `UIDesign/TabPage/CommSettingPage.cs:293`
  - `void btnConfig_Click(object sender, EventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:313`
  - `void btnKeepConfig_Click(object sender, EventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:340`
  - `void radioModeRSI_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:348`
  - `void InitRsiDebugPanel()` — `UIDesign/TabPage/CommSettingPage.cs:372`
  - `void RsiDebugTimer_Tick(object sender, EventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:394`
  - `void btnSendTx_Click(object sender, EventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:452`
  - `void btnInjectWeldParams_Click(object sender, EventArgs e)` — `UIDesign/TabPage/CommSettingPage.cs:485`
  - `void ParseDebugDouble(string text)` — `UIDesign/TabPage/CommSettingPage.cs:518`
  - `void AppendLog(string message)` — `UIDesign/TabPage/CommSettingPage.cs:530`
  - `void DisposeComponents()` — `UIDesign/TabPage/CommSettingPage.cs:565`
- 构造（1）：
  - `CommSettingPage()` — `UIDesign/TabPage/CommSettingPage.cs:45`
- 属性（1）：
  - `bool IsUiAccessible { get; set; }` — `UIDesign/TabPage/CommSettingPage.cs:40`

## ConfigListRow

- 签名：`private class ConfigListRow`
- 位置：`UIDesign/TabPage/ProcessControlPage.cs:223`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 属性（2）：
  - `int No { get; set; }` — `UIDesign/TabPage/ProcessControlPage.cs:225`
  - `string Id { get; set; }` — `UIDesign/TabPage/ProcessControlPage.cs:226`

## CylinderConfigPreviewRow

- 签名：`public class CylinderConfigPreviewRow`
- 位置：`UIDesign/TabPage/FilebackupPage.cs:1685`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 属性（8）：
  - `string CylinderName { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1688`
  - `string StretchSensor { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1691`
  - `string RetractSensor { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1694`
  - `string CenterSensor { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1697`
  - `string StretchOutput { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1700`
  - `string RetractOutput { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1703`
  - `string StretchActionName { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1706`
  - `string RetractActionName { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1709`

## DataReviewRow

- 签名：`public class DataReviewRow`
- 位置：`UIDesign/ControlPage/DataReviewerPage.cs:20`
- 命名空间：`AdaWeldSystem.UIDesign.ControlPage`
- 属性（8）：
  - `bool Selected { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:25`
  - `int No { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:31`
  - `string Sn { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:32`
  - `string Time { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:33`
  - `string Status { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:34`
  - `string Result { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:35`
  - `string Info { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:36`
  - `DateTime StartTime { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:39`

## DataReviewerPage

- 签名：`partial class DataReviewerPage`
- 位置：`UIDesign/ControlPage/DataReviewerPage.cs:16`
- 命名空间：`AdaWeldSystem.UIDesign.ControlPage`
- 方法（41）：
  - `void DataReviewerPage_Disposed(object sender, EventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:205`
  - `void InitSeriesGroups()` — `UIDesign/ControlPage/DataReviewerPage.cs:221`
  - `void MakeItem(string text, string name, Color color)` — `UIDesign/ControlPage/DataReviewerPage.cs:267`
  - `void BuildGroup(int index, SeriesItem[] items)` — `UIDesign/ControlPage/DataReviewerPage.cs:274`
  - `void EstimateBoxWidth(string text)` — `UIDesign/ControlPage/DataReviewerPage.cs:302`
  - `void selSeriesGroup_SelectedIndexChanged(object sender, AntdUI.IntEventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:316`
  - `void ShowGroupOnly(int index)` — `UIDesign/ControlPage/DataReviewerPage.cs:326`
  - `void InitTableColumns()` — `UIDesign/ControlPage/DataReviewerPage.cs:360`
  - `void uiDateRange_ValueChanged(object sender, EventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:380`
  - `void IsReadyForQuery()` — `UIDesign/ControlPage/DataReviewerPage.cs:391`
  - `void DiagLog(string scene, string detail)` — `UIDesign/ControlPage/DataReviewerPage.cs:401`
  - `void InitPCLDir(DateTime start, DateTime end, bool userInitiated)` — `UIDesign/ControlPage/DataReviewerPage.cs:419`
  - `void LoadProductRecords(DateTime start, DateTime end)` — `UIDesign/ControlPage/DataReviewerPage.cs:455`
  - `void GetCellText(System.Data.DataRow row, string column)` — `UIDesign/ControlPage/DataReviewerPage.cs:506`
  - `void ParseRecordTime(string timeText, DateTime fallbackDate)` — `UIDesign/ControlPage/DataReviewerPage.cs:514`
  - `void AfterInitializeUI()` — `UIDesign/ControlPage/DataReviewerPage.cs:526`
  - `void ChkSeries_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:539`
  - `void RebuildChartDatasets()` — `UIDesign/ControlPage/DataReviewerPage.cs:546`
  - `void SessionLabel(string seriesName, int sessionIndex)` — `UIDesign/ControlPage/DataReviewerPage.cs:578`
  - `void AddSeries(string name, ChartVar cv, Color color)` — `UIDesign/ControlPage/DataReviewerPage.cs:587`
  - `void uiDataGridView1_CellClick(object sender, AntdUI.TableClickEventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:602`
  - `void btnRenerView_Click(object sender, EventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:615`
  - `void BtnRecordSetting_Click(object sender, EventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:630`
  - `void btnRefreshDate_Click(object sender, EventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:646`
  - `void formsPlotData_MouseMove(object sender, MouseEventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:660`
  - `void FindNearestPoint(int mouseX, int mouseY)` — `UIDesign/ControlPage/DataReviewerPage.cs:679`
  - `void VisibleSeries()` — `UIDesign/ControlPage/DataReviewerPage.cs:721`
  - `void GetPlotWindow(double xMin, double xMax, double yMin, double yMax)` — `UIDesign/ControlPage/DataReviewerPage.cs:740`
  - `void ShowHoverTip(HoverHit hit)` — `UIDesign/ControlPage/DataReviewerPage.cs:769`
  - `void ClearHoverTip()` — `UIDesign/ControlPage/DataReviewerPage.cs:787`
  - `void Datashow()` — `UIDesign/ControlPage/DataReviewerPage.cs:795`
  - `void CollectSelectedRows()` — `UIDesign/ControlPage/DataReviewerPage.cs:925`
  - `void BuildSummaryText(List<DataReviewRow> targets, int missingFiles, StringBuilder adjustSummary)` — `UIDesign/ControlPage/DataReviewerPage.cs:942`
  - `void TotalAdjustCount()` — `UIDesign/ControlPage/DataReviewerPage.cs:964`
  - `void btnSelectAll_Click(object sender, EventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:978`
  - `void btnSelectNone_Click(object sender, EventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:986`
  - `void btnSelectInvert_Click(object sender, EventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:994`
  - `void ApplySelection(bool? value, bool invert)` — `UIDesign/ControlPage/DataReviewerPage.cs:1002`
  - `void FillPage()` — `UIDesign/ControlPage/DataReviewerPage.cs:1016`
  - `void pagination1_ValueChanged(object sender, AntdUI.PagePageEventArgs e)` — `UIDesign/ControlPage/DataReviewerPage.cs:1033`
  - `void EnsureLoaded()` — `UIDesign/ControlPage/DataReviewerPage.cs:1038`
- 构造（1）：
  - `DataReviewerPage()` — `UIDesign/ControlPage/DataReviewerPage.cs:177`

## DeviceMonitorPage

- 签名：`partial class DeviceMonitorPage`
- 位置：`UIDesign/ControlPage/DeviceMonitorPage.cs:10`
- 命名空间：`AdaWeldSystem.UIDesign.ControlPage`
- 方法（6）：
  - `void DeviceMonitorPage_HandleCreated(object sender, EventArgs e)` — `UIDesign/ControlPage/DeviceMonitorPage.cs:23`
  - `void DeviceMonitorPage_HandleDestroyed(object sender, EventArgs e)` — `UIDesign/ControlPage/DeviceMonitorPage.cs:28`
  - `void RefreshTemperature()` — `UIDesign/ControlPage/DeviceMonitorPage.cs:36`
  - `void TimerRefresh_Tick(object sender, EventArgs e)` — `UIDesign/ControlPage/DeviceMonitorPage.cs:42`
  - `void CollectTemperature()` — `UIDesign/ControlPage/DeviceMonitorPage.cs:49`
  - `void ApplyTemperature(TemperatureSnapshot snapshot)` — `UIDesign/ControlPage/DeviceMonitorPage.cs:94`
- 构造（1）：
  - `DeviceMonitorPage()` — `UIDesign/ControlPage/DeviceMonitorPage.cs:14`

## DeviceRow

- 签名：`private class DeviceRow`
- 位置：`UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:27`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.MonitorCamDialog`
- 属性（7）：
  - `int No { get; set; }` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:29`
  - `bool Selected { get; set; }` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:32`
  - `string Ip { get; set; }` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:43`
  - `string ProductName { get; set; }` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:44`
  - `string SerialNumber { get; set; }` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:45`
  - `string PortType { get; set; }` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:46`
  - `string SensorType { get; set; }` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:47`

## FileEditorForm

- 签名：`partial class FileEditorForm`
- 位置：`UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:16`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.CommConfigDialog`
- 方法（13）：
  - `void InitPropertyGridTable()` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:64`
  - `void LoadXmlToTree(XElement element)` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:80`
  - `void BuildNodeDisplayText(XElement element)` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:101`
  - `void ClearXmlAllInfo()` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:119`
  - `void LoadDocument(XdocumentReaderWriter doc, string docType)` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:129`
  - `void SelectFirstNode()` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:145`
  - `void BtnRefresh_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:164`
  - `void BtnSave_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:195`
  - `void BtnExpandAll_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:211`
  - `void BtnCollapseAll_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:219`
  - `void XmlTreeView_SelectChanged(object sender, TreeSelectEventArgs e)` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:227`
  - `void LoadNodeToTable(XElement element)` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:241`
  - `void OpenDocument(XdocumentReaderWriter doc, string docType)` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:295`
- 构造（1）：
  - `FileEditorForm()` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:57`

## FileTraceForm

- 签名：`partial class FileTraceForm`
- 位置：`UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:11`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.DataReviewerDialog`
- 方法（9）：
  - `void InitTableColumns()` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:45`
  - `void LoadFileList()` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:65`
  - `void uiTableRecord_CellClick(object sender, AntdUI.TableClickEventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:113`
  - `void uiTableTemp_CellClick(object sender, AntdUI.TableClickEventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:126`
  - `void btnRefresh_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:136`
  - `void btnSelectRecord_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:141`
  - `void btnSelectTemp_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:154`
  - `void btnConvertTemp_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:167`
  - `void btnCancel_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:196`
- 构造（2）：
  - `FileTraceForm()` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:27`
  - `FileTraceForm(Window _window)` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:29`
- 属性（1）：
  - `string SelectedFilePath { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:24`

## FileTraceRow

- 签名：`private class FileTraceRow`
- 位置：`UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:203`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.DataReviewerDialog`
- 属性（4）：
  - `int No { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:205`
  - `bool Selected { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:208`
  - `string FileName { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:219`
  - `string FilePath { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs:220`

## FilebackupPage

- 签名：`partial class FilebackupPage`
- 位置：`UIDesign/TabPage/FilebackupPage.cs:18`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 方法（64）：
  - `void FilebackupPage_HandleDestroyed(object sender, EventArgs e)` — `UIDesign/TabPage/FilebackupPage.cs:87`
  - `void btnBrowseDir_Click(object sender, EventArgs e)` — `UIDesign/TabPage/FilebackupPage.cs:99`
  - `void InitDeltaConfigPanel()` — `UIDesign/TabPage/FilebackupPage.cs:119`
  - `void SegDeltaView_SelectIndexChanged(object sender, AntdUI.IntEventArgs e)` — `UIDesign/TabPage/FilebackupPage.cs:153`
  - `void ApplyDeltaView(int index)` — `UIDesign/TabPage/FilebackupPage.cs:161`
  - `void BindDeltaView(int index)` — `UIDesign/TabPage/FilebackupPage.cs:177`
  - `void ScanDeltaDirectory(string directoryPath)` — `UIDesign/TabPage/FilebackupPage.cs:264`
  - `void IsDocumentSource()` — `UIDesign/TabPage/FilebackupPage.cs:289`
  - `void RefreshDeltaPreview(ConfigDirectoryScan scan)` — `UIDesign/TabPage/FilebackupPage.cs:299`
  - `void LoadProjectXmlRows()` — `UIDesign/TabPage/FilebackupPage.cs:321`
  - `void BuildIoPreviewRow(string ioType, DeltaIOConfig cfg)` — `UIDesign/TabPage/FilebackupPage.cs:408`
  - `void UpdateDeltaStatusHint(int index)` — `UIDesign/TabPage/FilebackupPage.cs:426`
  - `void UpdateDeltaStatusText(ConfigDirectoryScan scan)` — `UIDesign/TabPage/FilebackupPage.cs:476`
  - `void LoadAxisPreview(string filePath)` — `UIDesign/TabPage/FilebackupPage.cs:510`
  - `void LoadIoPreview(string filePath)` — `UIDesign/TabPage/FilebackupPage.cs:548`
  - `void LoadCylinderPreview(string filePath)` — `UIDesign/TabPage/FilebackupPage.cs:574`
  - `void CsvCell(string[] headers, string[] row, string name)` — `UIDesign/TabPage/FilebackupPage.cs:604`
  - `void btnDeltaGen_Click(object sender, EventArgs e)` — `UIDesign/TabPage/FilebackupPage.cs:619`
  - `void ReloadDeltaConfigOnly()` — `UIDesign/TabPage/FilebackupPage.cs:685`
  - `void TableDeltaView_CellEndEdit(object sender, AntdUI.TableEndEditEventArgs e)` — `UIDesign/TabPage/FilebackupPage.cs:704`
  - `void TableDeltaView_CellClick(object sender, AntdUI.TableClickEventArgs e)` — `UIDesign/TabPage/FilebackupPage.cs:718`
  - `void InitDeltaTableMenu()` — `UIDesign/TabPage/FilebackupPage.cs:725`
  - `void AddDeltaRow()` — `UIDesign/TabPage/FilebackupPage.cs:736`
  - `void RemoveDeltaRow()` — `UIDesign/TabPage/FilebackupPage.cs:818`
  - `void RescanFromDirectory()` — `UIDesign/TabPage/FilebackupPage.cs:853`
  - `void ExportCurrentViewCsv()` — `UIDesign/TabPage/FilebackupPage.cs:865`
  - `void ValidateCurrentTables(List<string> hints)` — `UIDesign/TabPage/FilebackupPage.cs:897`
  - `void MergeView(List<string> viewErrors, int viewIndex, List<string> errors, List<string> hints)` — `UIDesign/TabPage/FilebackupPage.cs:929`
  - `void BuildHintSuffix(List<string> hints)` — `UIDesign/TabPage/FilebackupPage.cs:938`
  - `void MarkCurrentViewDirty(int viewIndex)` — `UIDesign/TabPage/FilebackupPage.cs:949`
  - `void ClearDirty()` — `UIDesign/TabPage/FilebackupPage.cs:956`
  - `void ValidateAxisRows(List<string> errors)` — `UIDesign/TabPage/FilebackupPage.cs:964`
  - `void ValidateIoRows(List<string> errors)` — `UIDesign/TabPage/FilebackupPage.cs:1000`
  - `void ValidateCylinderRows(List<string> errors)` — `UIDesign/TabPage/FilebackupPage.cs:1023`
  - `void ValidateWeldHeadRows(List<string> errors, List<string> hints)` — `UIDesign/TabPage/FilebackupPage.cs:1054`
  - `void Where(int rowIndex, int columnIndex, string columnName)` — `UIDesign/TabPage/FilebackupPage.cs:1101`
  - `void CheckUShort(string text, int rowIndex, int columnIndex, string columnName, int min, int max, List<string> errors)` — `UIDesign/TabPage/FilebackupPage.cs:1110`
  - `void CheckBool(string text, int rowIndex, int columnIndex, string columnName, List<string> errors)` — `UIDesign/TabPage/FilebackupPage.cs:1121`
  - `void CheckDouble(string text, int rowIndex, int columnIndex, string columnName, List<string> errors)` — `UIDesign/TabPage/FilebackupPage.cs:1131`
  - `void CheckHex(string text, int rowIndex, int columnIndex, string columnName, List<string> errors)` — `UIDesign/TabPage/FilebackupPage.cs:1141`
  - `void CheckIoReference(string reference, HashSet<string> candidates, int rowIndex, int columnIndex, string columnName, List<string> errors)` — `UIDesign/TabPage/FilebackupPage.cs:1150`
  - `void ParseDouble(string text, double defaultValue)` — `UIDesign/TabPage/FilebackupPage.cs:1162`
  - `void TryParseHex(string text, uint value)` — `UIDesign/TabPage/FilebackupPage.cs:1173`
  - `void IsInputType(string text)` — `UIDesign/TabPage/FilebackupPage.cs:1186`
  - `void IsOutputType(string text)` — `UIDesign/TabPage/FilebackupPage.cs:1195`
  - `void WriteTableSourceDirectory(string error)` — `UIDesign/TabPage/FilebackupPage.cs:1204`
  - `void WriteOrClearCsv(string dir, string fileName, string[] headers, List<string[]> rows)` — `UIDesign/TabPage/FilebackupPage.cs:1238`
  - `void AxisHeaders()` — `UIDesign/TabPage/FilebackupPage.cs:1252`
  - `void BuildAxisCsvRows()` — `UIDesign/TabPage/FilebackupPage.cs:1262`
  - `void IoHeaders()` — `UIDesign/TabPage/FilebackupPage.cs:1293`
  - `void BuildIoCsvRows()` — `UIDesign/TabPage/FilebackupPage.cs:1300`
  - `void CylinderHeaders()` — `UIDesign/TabPage/FilebackupPage.cs:1313`
  - `void BuildCylinderCsvRows()` — `UIDesign/TabPage/FilebackupPage.cs:1321`
  - `void ColumnHeaders(int index)` — `UIDesign/TabPage/FilebackupPage.cs:1335`
  - `void BuildCurrentViewRows(int index)` — `UIDesign/TabPage/FilebackupPage.cs:1350`
  - `void WriteCsvTable(string path, string[] headers, List<string[]> rows)` — `UIDesign/TabPage/FilebackupPage.cs:1370`
  - `void CsvEscape(string value)` — `UIDesign/TabPage/FilebackupPage.cs:1387`
  - `void SetRowCellValue(object record, int columnIndex, string value)` — `UIDesign/TabPage/FilebackupPage.cs:1400`
  - `void ReloadSystemConfig()` — `UIDesign/TabPage/FilebackupPage.cs:1471`
  - `void ReloadSystemConfig(bool reloadWeldHead)` — `UIDesign/TabPage/FilebackupPage.cs:1479`
  - `void btnExportPackage_Click(object sender, EventArgs e)` — `UIDesign/TabPage/FilebackupPage.cs:1505`
  - `void btnImportPackage_Click(object sender, EventArgs e)` — `UIDesign/TabPage/FilebackupPage.cs:1534`
  - `void ReadDirInput(AntdUI.Input input)` — `UIDesign/TabPage/FilebackupPage.cs:1578`
  - `void DisposeComponents()` — `UIDesign/TabPage/FilebackupPage.cs:1588`
- 构造（1）：
  - `FilebackupPage()` — `UIDesign/TabPage/FilebackupPage.cs:76`
- 属性（1）：
  - `bool IsUiAccessible { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:71`

## FormMain

- 签名：`partial class FormMain`
- 位置：`UIDesign/MainWindow/FormMain.cs:21`
- 命名空间：`AdaWeldSystem.UIDesign.MainWindow`
- 方法（14）：
  - `void FormMain_Shown(object sender, EventArgs e)` — `UIDesign/MainWindow/FormMain.cs:99`
  - `void OnInitCompleted(bool success)` — `UIDesign/MainWindow/FormMain.cs:119`
  - `void FormMain_FormClosing(object sender, FormClosingEventArgs e)` — `UIDesign/MainWindow/FormMain.cs:137`
  - `void LoadNavAndPages()` — `UIDesign/MainWindow/FormMain.cs:153`
  - `void OnWorkflowStateChanged(object sender, WeldStatusChangedEventArgs e)` — `UIDesign/MainWindow/FormMain.cs:235`
  - `void UpdateStatusLabel(SubDeviceWeldStatus state)` — `UIDesign/MainWindow/FormMain.cs:247`
  - `void ShowStatus()` — `UIDesign/MainWindow/FormMain.cs:266`
  - `void OperateLevelControl()` — `UIDesign/MainWindow/FormMain.cs:278`
  - `void HideTreeNode()` — `UIDesign/MainWindow/FormMain.cs:294`
  - `void ShowTreeNode()` — `UIDesign/MainWindow/FormMain.cs:307`
  - `void OnOperateLevelChanged(object sender, OperateLevel level)` — `UIDesign/MainWindow/FormMain.cs:322`
  - `void uiMillisecondTimer1_Tick(object sender, EventArgs e)` — `UIDesign/MainWindow/FormMain.cs:332`
  - `void FormMain_FormClosed(object sender, FormClosedEventArgs e)` — `UIDesign/MainWindow/FormMain.cs:340`
  - `void buttonSZ_Click(object sender, EventArgs e)` — `UIDesign/MainWindow/FormMain.cs:364`
- 构造（1）：
  - `FormMain()` — `UIDesign/MainWindow/FormMain.cs:39`

## GalvoSnapshot

- 签名：`private sealed class GalvoSnapshot`
- 位置：`UIDesign/TabPage/SystemControlPage.cs:2786`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 成员：（无）

## HelixRenderForm

- 签名：`partial class HelixRenderForm`
- 位置：`UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:20`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.DataReviewerDialog`
- 方法（20）：
  - `void HelixRenderForm_HandleDestroyed(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:94`
  - `void btnTraceFile_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:104`
  - `void btnZColor_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:177`
  - `void btnSurface_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:190`
  - `void ExecuteSurfaceRender()` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:209`
  - `void btnClearData_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:265`
  - `void btnRotate_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:270`
  - `void btnMove_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:277`
  - `void btnRound_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:285`
  - `void btnAssimpImport_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:292`
  - `void btnRenderParam_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:320`
  - `void DisposeComponents()` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:333`
  - `void LoadPointCloud(string filePath, = 2f)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:341`
  - `void LoadPointCloud(PointCloudData data, = 2f)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:350`
  - `void ReducePointCloud(float ratio)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:362`
  - `void ClearAll()` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:370`
  - `void SetPointSize(float size)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:382`
  - `void SetPointColor(DrawingColor color)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:389`
  - `void SetSurfaceColor(DrawingColor color)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:396`
  - `void SavePointCloud(string filePath)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:404`
- 构造（2）：
  - `HelixRenderForm()` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:80`
  - `HelixRenderForm(Window _window)` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:83`
- 属性（7）：
  - `Window Window { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:23`
  - `float PointSize { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:28`
  - `bool ZColorEnabled { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:43`
  - `float DisplayRatio { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:58`
  - `bool IsSurfaceVisible { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:72`
  - `bool IsPointCloudVisible { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:76`
  - `PointCloudData CurrentData { get; set; }` — `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs:100`

## HoverHit

- 签名：`private class HoverHit`
- 位置：`UIDesign/ControlPage/DataReviewerPage.cs:914`
- 命名空间：`AdaWeldSystem.UIDesign.ControlPage`
- 属性（5）：
  - `string SeriesName { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:916`
  - `double DataX { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:917`
  - `double DataY { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:918`
  - `double PixelX { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:919`
  - `double PixelY { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:920`

## ILAlgoForm

- 签名：`partial class ILAlgoForm`
- 位置：`UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:12`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog`
- 方法（23）：
  - `void InitTableColumns()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:57`
  - `void InitIlModule()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:70`
  - `void ClearJobFlow()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:96`
  - `void UpdateConnLabel()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:105`
  - `void SetIlControlsEnabled(bool enabled)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:129`
  - `void RefreshJobFlow()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:138`
  - `void SyncSelectedJobFromDevice()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:170`
  - `void UpdateJobButtonsState()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:177`
  - `void btnchangeJob_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:198`
  - `void btnDeleteJob_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:215`
  - `void RefreshJobParams()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:244`
  - `void GetCurrentJobDisplayKeys()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:272`
  - `void IsDisplayParam(List<string> displayKeys, string paramName)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:280`
  - `void UpdateJointTypeLabel()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:306`
  - `void LoadIlParamsToGrid(List<IlJobParamInfo> list)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:325`
  - `void GetParamGroup(string name)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:347`
  - `void OnJobParamsChanged(object sender, EventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:358`
  - `void btnCreate_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:380`
  - `void dgvILParams_CellEndEdit(object sender, AntdUI.TableEndEditEventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:435`
  - `void ParseAndValidate(IlJobParamInfo src, string raw)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:481`
  - `void BuildParamInfo(IlJobParamInfo src, string raw)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:497`
  - `void FormatCellValue(IlJobParamInfo p)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:516`
  - `void StopRefresh()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:528`
- 构造（1）：
  - `ILAlgoForm(IntelligentLaserCam ilCamera)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:37`

## ILAlgorithmEditForm

- 签名：`partial class ILAlgorithmEditForm`
- 位置：`UIDesign/SubDialog/IntelligentLaserDialog/ILAlgorithmEditForm.cs:11`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog`
- 方法（1）：
  - `void AlgorithmEditForm_HandleDestroyed(object sender, EventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgorithmEditForm.cs:42`
- 构造（1）：
  - `ILAlgorithmEditForm(Window _window, PipelineConfig config)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgorithmEditForm.cs:20`

## ILParamForm

- 签名：`partial class ILParamForm`
- 位置：`UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:13`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog`
- 方法（13）：
  - `void InitTableColumns()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:64`
  - `void UpdateConnLabel()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:78`
  - `void LoadParams()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:88`
  - `void MakeCameraRow(string name, string value, string unit, string desc, int kind, Dictionary<string, IlJobParamInfo> jobMap, string jobKey)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:121`
  - `void AddJobRow(string name, string jobKey, string desc, Dictionary<string, IlJobParamInfo> jobMap)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:137`
  - `void ValidateRow(CameraParamRow row, string raw)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:148`
  - `void CheckRange(IlJobParamInfo jp, double v)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:174`
  - `void CheckRange(IlJobParamInfo jp, long v)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:181`
  - `void FormatRange(IlJobParamInfo jp)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:187`
  - `void uiTableParam_CellEndEdit(object sender, AntdUI.TableEndEditEventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:195`
  - `void btnFetch_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:206`
  - `void btnSave_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:213`
  - `void btnCancel_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:288`
- 构造（1）：
  - `ILParamForm(Window _window, IntelligentLaserCam ilCamera)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs:43`

## ILScanForm

- 签名：`partial class ILScanForm`
- 位置：`UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:10`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog`
- 方法（5）：
  - `void InitTableColumns()` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:70`
  - `void LoadSensors(List<IlSensorInfo> sensors)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:85`
  - `void uiTableSensor_CellClick(object sender, AntdUI.TableClickEventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:112`
  - `void btnOK_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:122`
  - `void btnCancel_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:134`
- 构造（1）：
  - `ILScanForm(Window _window, List<IlSensorInfo> sensors)` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:52`
- 属性（1）：
  - `string SelectedIp { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:22`

## IlJobParamRow

- 签名：`public class IlJobParamRow`
- 位置：`UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:25`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog`
- 属性（5）：
  - `string Name { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:27`
  - `string Value { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:28`
  - `string Type { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:29`
  - `string Range { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:30`
  - `string Group { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs:31`

## InitWaitingForm

- 签名：`public class InitWaitingForm : UserControl`
- 位置：`UIDesign/SubDialog/FormMainDialog/InitWaitingForm.cs:8`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.FormMainDialog`
- 方法（2）：
  - `void SetResult(bool success)` — `UIDesign/SubDialog/FormMainDialog/InitWaitingForm.cs:39`
  - `void CloseModal()` — `UIDesign/SubDialog/FormMainDialog/InitWaitingForm.cs:45`
- 构造（1）：
  - `InitWaitingForm()` — `UIDesign/SubDialog/FormMainDialog/InitWaitingForm.cs:19`

## InspectResultRow

- 签名：`private class InspectResultRow`
- 位置：`UIDesign/TabPage/LineLaserCamPage.cs:95`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 属性（3）：
  - `string Field { get; set; }` — `UIDesign/TabPage/LineLaserCamPage.cs:97`
  - `string Value { get; set; }` — `UIDesign/TabPage/LineLaserCamPage.cs:98`
  - `string Unit { get; set; }` — `UIDesign/TabPage/LineLaserCamPage.cs:99`

## IoConfigPreviewRow

- 签名：`public class IoConfigPreviewRow`
- 位置：`UIDesign/TabPage/FilebackupPage.cs:1660`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 属性（7）：
  - `string IoType { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1663`
  - `string IoName { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1666`
  - `string NodeId { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1669`
  - `string SlotNo { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1672`
  - `string BitNo { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1675`
  - `string Enabled { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1678`
  - `string Remark { get; set; }` — `UIDesign/TabPage/FilebackupPage.cs:1681`

## LaMotorSnapshot

- 签名：`private sealed class LaMotorSnapshot`
- 位置：`UIDesign/TabPage/SystemControlPage.cs:2795`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 成员：（无）

## LineLaserCamPage

- 签名：`partial class LineLaserCamPage`
- 位置：`UIDesign/TabPage/LineLaserCamPage.cs:22`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 方法（33）：
  - `void RefreshUi(RefreshUiScope scope)` — `UIDesign/TabPage/LineLaserCamPage.cs:82`
  - `void OnMatUpdated(object sender, LineLaserMatEventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:104`
  - `void RefreshDisplay()` — `UIDesign/TabPage/LineLaserCamPage.cs:115`
  - `void ShowMat(Mat src)` — `UIDesign/TabPage/LineLaserCamPage.cs:138`
  - `void InitResultTable()` — `UIDesign/TabPage/LineLaserCamPage.cs:148`
  - `void RefreshInspectResult()` — `UIDesign/TabPage/LineLaserCamPage.cs:163`
  - `void btnConnect_Click(object sender, EventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:189`
  - `void TryPassPageAction(string action)` — `UIDesign/TabPage/LineLaserCamPage.cs:225`
  - `void LogPageWarning(string message)` — `UIDesign/TabPage/LineLaserCamPage.cs:250`
  - `void SyncFromHardwareCore()` — `UIDesign/TabPage/LineLaserCamPage.cs:255`
  - `void btnScan_Click(object sender, EventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:272`
  - `void btnLaser_Click(object sender, EventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:298`
  - `void btnCaptureCamera_Click(object sender, EventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:305`
  - `void btnAlgoEdit_Click(object sender, EventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:315`
  - `void btnParamEdit_Click(object sender, EventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:328`
  - `void RefreshJobSelect()` — `UIDesign/TabPage/LineLaserCamPage.cs:346`
  - `void cmbJob_SelectedIndexChanged(object sender, IntEventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:367`
  - `void OnIlJobParamsChanged(object sender, EventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:373`
  - `void btnApplyJob_Click(object sender, EventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:387`
  - `void RefreshFpsSelect()` — `UIDesign/TabPage/LineLaserCamPage.cs:414`
  - `void cmbFps_SelectedIndexChanged(object sender, IntEventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:433`
  - `void btnApplyFps_Click(object sender, EventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:439`
  - `void UpdateApplyButtonsState()` — `UIDesign/TabPage/LineLaserCamPage.cs:470`
  - `void IsWorkflowRunning(SubDeviceWeldStatus state)` — `UIDesign/TabPage/LineLaserCamPage.cs:505`
  - `void OnWorkflowStateChanged(object sender, WeldStatusChangedEventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:518`
  - `void swDisplay_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:530`
  - `void OnInitializationCompleted(bool success)` — `UIDesign/TabPage/LineLaserCamPage.cs:537`
  - `void UpdateModeUiCore()` — `UIDesign/TabPage/LineLaserCamPage.cs:548`
  - `void UpdateConnectionUiCore()` — `UIDesign/TabPage/LineLaserCamPage.cs:586`
  - `void UpdateLaserSensorUi()` — `UIDesign/TabPage/LineLaserCamPage.cs:622`
  - `void OnIlStateChanged(object sender, SubDeviceStateChangedEventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:633`
  - `void UpdateFpsDropdownState()` — `UIDesign/TabPage/LineLaserCamPage.cs:652`
  - `void ILCamPage_HandleDestroyed(object sender, EventArgs e)` — `UIDesign/TabPage/LineLaserCamPage.cs:663`
- 构造（1）：
  - `LineLaserCamPage()` — `UIDesign/TabPage/LineLaserCamPage.cs:28`

## LoginForm

- 签名：`partial class LoginForm`
- 位置：`UIDesign/SubDialog/UserManagerDialog/LoginForm.cs:9`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.UserManagerDialog`
- 方法（4）：
  - `void BtnLogout_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/UserManagerDialog/LoginForm.cs:28`
  - `void ShowCorButton()` — `UIDesign/SubDialog/UserManagerDialog/LoginForm.cs:39`
  - `void FormLogin_ButtonLoginClick(object sender, EventArgs e)` — `UIDesign/SubDialog/UserManagerDialog/LoginForm.cs:45`
  - `void btnUserManager_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/UserManagerDialog/LoginForm.cs:70`
- 构造（2）：
  - `LoginForm()` — `UIDesign/SubDialog/UserManagerDialog/LoginForm.cs:16`
  - `LoginForm(Window _window)` — `UIDesign/SubDialog/UserManagerDialog/LoginForm.cs:18`
- 属性（1）：
  - `bool IsLogin { get; set; }` — `UIDesign/SubDialog/UserManagerDialog/LoginForm.cs:13`

## MainPage

- 签名：`partial class MainPage`
- 位置：`UIDesign/ControlPage/MainPage.cs:21`
- 命名空间：`AdaWeldSystem.UIDesign.ControlPage`
- 方法（51）：
  - `void Log(string message, MessageLevel level)` — `UIDesign/ControlPage/MainPage.cs:198`
  - `void MainPage_HandleDestroyed(object sender, EventArgs e)` — `UIDesign/ControlPage/MainPage.cs:212`
  - `void StartProfilePolling()` — `UIDesign/ControlPage/MainPage.cs:220`
  - `void StopProfilePolling()` — `UIDesign/ControlPage/MainPage.cs:240`
  - `void ProfilePollLoop()` — `UIDesign/ControlPage/MainPage.cs:252`
  - `void AppendNewPoints(ChartVar source, ChartVar target, int lastIndex)` — `UIDesign/ControlPage/MainPage.cs:314`
  - `void ApplyProfileSnapshot(ProfileSnapshot snap)` — `UIDesign/ControlPage/MainPage.cs:339`
  - `void LockContourAxisOnce()` — `UIDesign/ControlPage/MainPage.cs:379`
  - `void UpdateChartUI()` — `UIDesign/ControlPage/MainPage.cs:418`
  - `void RefreshParamChartsUi()` — `UIDesign/ControlPage/MainPage.cs:456`
  - `void RefreshParamCharts()` — `UIDesign/ControlPage/MainPage.cs:469`
  - `void AddSeries(ScottPlot.FormsPlot chart, string seriesName, ChartVar data, System.Drawing.Color color)` — `UIDesign/ControlPage/MainPage.cs:503`
  - `void AddSeamWidthLimitLines(ScottPlot.FormsPlot chart)` — `UIDesign/ControlPage/MainPage.cs:517`
  - `void AfterInitializeUI()` — `UIDesign/ControlPage/MainPage.cs:568`
  - `void SetupMergedChart(ScottPlot.FormsPlot chart)` — `UIDesign/ControlPage/MainPage.cs:578`
  - `void CommenData_EventInfoHandler(object sender, MessageArgs e)` — `UIDesign/ControlPage/MainPage.cs:587`
  - `void inputLog_TextChanged(object sender, EventArgs e)` — `UIDesign/ControlPage/MainPage.cs:606`
  - `void MainPage_Shown(object sender, EventArgs e)` — `UIDesign/ControlPage/MainPage.cs:611`
  - `void BuildAlarmText(string prefix)` — `UIDesign/ControlPage/MainPage.cs:622`
  - `void OnMainDeviceStatusChanged(object sender, MainDeviceStatusChangedEventArgs e)` — `UIDesign/ControlPage/MainPage.cs:655`
  - `void ApplyDeviceStatus(MainDeviceStatus state)` — `UIDesign/ControlPage/MainPage.cs:669`
  - `void UiTimer_Tick(object sender, EventArgs e)` — `UIDesign/ControlPage/MainPage.cs:735`
  - `void OnRobotCommandReceived(object sender, string message)` — `UIDesign/ControlPage/MainPage.cs:749`
  - `void InitWeldFlowSteps()` — `UIDesign/ControlPage/MainPage.cs:758`
  - `void OnWeldFlowStepsMouseMove(object sender, MouseEventArgs e)` — `UIDesign/ControlPage/MainPage.cs:796`
  - `void OnWeldFlowStepsMouseLeave(object sender, EventArgs e)` — `UIDesign/ControlPage/MainPage.cs:822`
  - `void SetWeldFlowStep(WeldFlowStep step, AntdUI.TStepState state, bool allowBack)` — `UIDesign/ControlPage/MainPage.cs:833`
  - `void ApplyWeldFlowDeviceStatus(MainDeviceStatus previous, MainDeviceStatus state)` — `UIDesign/ControlPage/MainPage.cs:853`
  - `void OnWeldParamWeldStatusChanged(object sender, WeldStatusChangedEventArgs e)` — `UIDesign/ControlPage/MainPage.cs:889`
  - `void ApplyWeldFlowWeldStatus(SubDeviceWeldStatus status)` — `UIDesign/ControlPage/MainPage.cs:902`
  - `void AdvanceWeldFlowByCommand(string message)` — `UIDesign/ControlPage/MainPage.cs:925`
  - `void InitDeviceSwitchButtons()` — `UIDesign/ControlPage/MainPage.cs:956`
  - `void OnPanelFloatButtonSizeChanged(object sender, EventArgs e)` — `UIDesign/ControlPage/MainPage.cs:1014`
  - `void LayoutDeviceSwitchAreas()` — `UIDesign/ControlPage/MainPage.cs:1020`
  - `void BuildDeviceTooltipText(int idx, bool connected)` — `UIDesign/ControlPage/MainPage.cs:1051`
  - `void OnDeviceSwitchClick(int idx)` — `UIDesign/ControlPage/MainPage.cs:1057`
  - `void IsLineLaserRunning()` — `UIDesign/ControlPage/MainPage.cs:1070`
  - `void ToggleLineLaserConnection()` — `UIDesign/ControlPage/MainPage.cs:1076`
  - `void RefreshDeviceSwitchUi()` — `UIDesign/ControlPage/MainPage.cs:1105`
  - `void SetDeviceIconSvg(int idx, string iconSvg)` — `UIDesign/ControlPage/MainPage.cs:1149`
  - `void SetDeviceBadgeSvg(int idx, string badgeSvg)` — `UIDesign/ControlPage/MainPage.cs:1159`
  - `void ChkSeries_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/ControlPage/MainPage.cs:1171`
  - `void SeriesCheckboxes()` — `UIDesign/ControlPage/MainPage.cs:1198`
  - `void ApplySeriesSingleSelection(AntdUI.Checkbox keep)` — `UIDesign/ControlPage/MainPage.cs:1205`
  - `void ApplyLineColor(int start, int length, Color color)` — `UIDesign/ControlPage/MainPage.cs:1225`
  - `void OnWeldPreviewFrame(Mat frame)` — `UIDesign/ControlPage/MainPage.cs:1240`
  - `void ShowWeldPreviewFrame(Mat frame)` — `UIDesign/ControlPage/MainPage.cs:1265`
  - `void DisposePreviewFrame(Mat frame)` — `UIDesign/ControlPage/MainPage.cs:1286`
  - `void DisposeComponents()` — `UIDesign/ControlPage/MainPage.cs:1292`
  - `void LogAppend(Color color, string strMsg)` — `UIDesign/ControlPage/MainPage.cs:1335`
  - `void AddContourLineChart()` — `UIDesign/ControlPage/MainPage.cs:1368`
- 构造（1）：
  - `MainPage()` — `UIDesign/ControlPage/MainPage.cs:133`
- 属性（1）：
  - `bool IsWeldModeActive { get; set; }` — `UIDesign/ControlPage/MainPage.cs:207`

## ManualOpOutcome

- 签名：`private sealed class ManualOpOutcome`
- 位置：`UIDesign/TabPage/SystemControlPage.cs:906`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 成员：（无）

## MonitorCamPage

- 签名：`partial class MonitorCamPage`
- 位置：`UIDesign/TabPage/MonitorCamPage.cs:19`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 方法（64）：
  - `void MonitorCamPage_HandleDestroyed(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:82`
  - `void DisposeComponents()` — `UIDesign/TabPage/MonitorCamPage.cs:88`
  - `void WireButtons()` — `UIDesign/TabPage/MonitorCamPage.cs:104`
  - `void InitCalibUi()` — `UIDesign/TabPage/MonitorCamPage.cs:119`
  - `void ApplyAlignPermission()` — `UIDesign/TabPage/MonitorCamPage.cs:129`
  - `void OnOperateLevelChanged(object sender, OperateLevel level)` — `UIDesign/TabPage/MonitorCamPage.cs:137`
  - `void LoadAlignThresholds()` — `UIDesign/TabPage/MonitorCamPage.cs:148`
  - `void btnSaveAlign_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:159`
  - `void TryReadDouble(AntdUI.Input input, double value)` — `UIDesign/TabPage/MonitorCamPage.cs:190`
  - `void InitPlaybackTable()` — `UIDesign/TabPage/MonitorCamPage.cs:200`
  - `void InitializeConnectionBar()` — `UIDesign/TabPage/MonitorCamPage.cs:219`
  - `void UpdateConnectionUi()` — `UIDesign/TabPage/MonitorCamPage.cs:231`
  - `void btnScan_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:252`
  - `void btnConnect_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:278`
  - `void SetConnectIp(string ip)` — `UIDesign/TabPage/MonitorCamPage.cs:312`
  - `void LoadCameraParams()` — `UIDesign/TabPage/MonitorCamPage.cs:321`
  - `void btnStartCapture_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:336`
  - `void btnStopCapture_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:357`
  - `void Manager_PreviewFrame(Mat frame)` — `UIDesign/TabPage/MonitorCamPage.cs:364`
  - `void btnBrowseRecord_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:382`
  - `void btnStartRecord_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:401`
  - `void btnStopRecord_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:417`
  - `void btnApplyParam_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:431`
  - `void btnCalibSave_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:465`
  - `void btnFeedTest_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:488`
  - `void InitPlaybackUi()` — `UIDesign/TabPage/MonitorCamPage.cs:504`
  - `void tabsMonitor_SelectedIndexChanged(object sender, AntdUI.IntEventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:545`
  - `void btnRefreshPlay_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:563`
  - `void uiPlayDateRange_ValueChanged(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:572`
  - `void GetPlayRange(DateTime start, DateTime end)` — `UIDesign/TabPage/MonitorCamPage.cs:581`
  - `void WirePlaybackEvents()` — `UIDesign/TabPage/MonitorCamPage.cs:601`
  - `void UnwirePlaybackEvents()` — `UIDesign/TabPage/MonitorCamPage.cs:613`
  - `void OnPlayScanStarted(string caption)` — `UIDesign/TabPage/MonitorCamPage.cs:626`
  - `void OnPlayScanCompleted(PlaybackScanResult result)` — `UIDesign/TabPage/MonitorCamPage.cs:635`
  - `void OnPlayScanCrashed(string message)` — `UIDesign/TabPage/MonitorCamPage.cs:658`
  - `void OnPlayThumbnailReady(PlaybackFileInfo info)` — `UIDesign/TabPage/MonitorCamPage.cs:673`
  - `void OnPlayFrameReady(Mat frame)` — `UIDesign/TabPage/MonitorCamPage.cs:694`
  - `void OnPlayProgress(int frameIndex, int totalFrames, double fps)` — `UIDesign/TabPage/MonitorCamPage.cs:710`
  - `void OnPlayStateChanged(bool isPlaying, double speed)` — `UIDesign/TabPage/MonitorCamPage.cs:728`
  - `void ToPlaybackRow(PlaybackFileInfo info)` — `UIDesign/TabPage/MonitorCamPage.cs:743`
  - `void LoadPlaybackRange(DateTime start, DateTime end)` — `UIDesign/TabPage/MonitorCamPage.cs:757`
  - `void SetPlayCaption(string text)` — `UIDesign/TabPage/MonitorCamPage.cs:764`
  - `void ClearPlaybackRows()` — `UIDesign/TabPage/MonitorCamPage.cs:771`
  - `void playTable_CellClick(object sender, AntdUI.TableClickEventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:785`
  - `void PlaySelected()` — `UIDesign/TabPage/MonitorCamPage.cs:798`
  - `void sliderPlay_ValueChanged(object sender, AntdUI.IntEventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:808`
  - `void btnBack5Play_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:817`
  - `void btnForward5Play_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:825`
  - `void btnSlowPlay_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:833`
  - `void btnFastPlay_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:841`
  - `void btnPlayPause_Click(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:849`
  - `void UpdatePlayPauseUi()` — `UIDesign/TabPage/MonitorCamPage.cs:856`
  - `void FormatSpeed(double speed)` — `UIDesign/TabPage/MonitorCamPage.cs:863`
  - `void UpdatePlayTimeLabel(int frameIndex, int totalFrames, double fps)` — `UIDesign/TabPage/MonitorCamPage.cs:872`
  - `void FormatPlayTime(double seconds)` — `UIDesign/TabPage/MonitorCamPage.cs:881`
  - `void imageBoxPlay_MouseMove(object sender, MouseEventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:896`
  - `void imageBoxPlay_MouseLeave(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:904`
  - `void panelPlayBar_MouseEnter(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:914`
  - `void panelPlayBar_MouseLeave(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:922`
  - `void SetPlayBarVisible(bool visible)` — `UIDesign/TabPage/MonitorCamPage.cs:929`
  - `void sliderPlay_MouseEnter(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:938`
  - `void sliderPlay_MouseDown(object sender, MouseEventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:946`
  - `void sliderPlay_MouseUp(object sender, MouseEventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:954`
  - `void StatusTimer_Tick(object sender, EventArgs e)` — `UIDesign/TabPage/MonitorCamPage.cs:963`
- 构造（1）：
  - `MonitorCamPage()` — `UIDesign/TabPage/MonitorCamPage.cs:64`

## MonitorCamScanForm

- 签名：`partial class MonitorCamScanForm`
- 位置：`UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:10`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.MonitorCamDialog`
- 方法（5）：
  - `void InitTableColumns()` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:71`
  - `void LoadDevices(List<MonitorCamDeviceInfo> devices)` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:87`
  - `void uiTableDevice_CellClick(object sender, AntdUI.TableClickEventArgs e)` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:115`
  - `void btnOK_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:125`
  - `void btnCancel_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:137`
- 构造（1）：
  - `MonitorCamScanForm(Window _window, List<MonitorCamDeviceInfo> devices)` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:53`
- 属性（1）：
  - `string SelectedIp { get; set; }` — `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs:22`

## NavPage

- 签名：`partial class NavPage`
- 位置：`UIDesign/ControlPage/NavPage.cs:9`
- 命名空间：`AdaWeldSystem.UIDesign.ControlPage`
- 方法（7）：
  - `void LoadTabs()` — `UIDesign/ControlPage/NavPage.cs:64`
  - `void LoadTabs()` — `UIDesign/ControlPage/NavPage.cs:88`
  - `void LoadTabsLazy()` — `UIDesign/ControlPage/NavPage.cs:105`
  - `void LoadTabsLazy()` — `UIDesign/ControlPage/NavPage.cs:135`
  - `void EnsureTabLoaded(int index)` — `UIDesign/ControlPage/NavPage.cs:152`
  - `void LoadTabsWithItems(string text, UserControl control, string iconSvg, int index)` — `UIDesign/ControlPage/NavPage.cs:185`
  - `void NavPage_Disposed(object sender, EventArgs e)` — `UIDesign/ControlPage/NavPage.cs:202`
- 构造（1）：
  - `NavPage()` — `UIDesign/ControlPage/NavPage.cs:16`

## PlaybackRow

- 签名：`public class PlaybackRow`
- 位置：`UIDesign/TabPage/MonitorCamPage.cs:22`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 属性（6）：
  - `string FileName { get; set; }` — `UIDesign/TabPage/MonitorCamPage.cs:25`
  - `string FullPath { get; set; }` — `UIDesign/TabPage/MonitorCamPage.cs:28`
  - `string Modified { get; set; }` — `UIDesign/TabPage/MonitorCamPage.cs:31`
  - `string Size { get; set; }` — `UIDesign/TabPage/MonitorCamPage.cs:34`
  - `Bitmap Thumbnail { get; set; }` — `UIDesign/TabPage/MonitorCamPage.cs:37`
  - `object Preview { get; set; }` — `UIDesign/TabPage/MonitorCamPage.cs:40`

## ProcessControlPage

- 签名：`partial class ProcessControlPage`
- 位置：`UIDesign/TabPage/ProcessControlPage.cs:23`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 方法（106）：
  - `void ProcessControlPage_HandleDestroyed(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:35`
  - `void StartActionRefresh()` — `UIDesign/TabPage/ProcessControlPage.cs:51`
  - `void timerRefresh_Tick(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:57`
  - `void OnMotionStateSwitched(object sender, AdaWeldSystem.MainDeviceControl.DeviceStateApiCore.SubDeviceStateChangedEventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:71`
  - `void OnAxisReadyChanged()` — `UIDesign/TabPage/ProcessControlPage.cs:84`
  - `void OnTaZeroPoseStageChanged()` — `UIDesign/TabPage/ProcessControlPage.cs:90`
  - `void PostToUi(Action action)` — `UIDesign/TabPage/ProcessControlPage.cs:98`
  - `void ApplyTaZeroPoseStage()` — `UIDesign/TabPage/ProcessControlPage.cs:118`
  - `void ProcessControlPage_VisibleChanged(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:142`
  - `void OnMachineInitializationCompleted(bool success)` — `UIDesign/TabPage/ProcessControlPage.cs:151`
  - `void InitCommandTooltips()` — `UIDesign/TabPage/ProcessControlPage.cs:165`
  - `void InitConfigListColumns()` — `UIDesign/TabPage/ProcessControlPage.cs:233`
  - `void tableConfigList_CellClick(object sender, AntdUI.TableClickEventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:250`
  - `void LoadConfigList()` — `UIDesign/TabPage/ProcessControlPage.cs:263`
  - `void btnConfigAddNew_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:284`
  - `void btnConfigDelete_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:290`
  - `void ConfigSelect()` — `UIDesign/TabPage/ProcessControlPage.cs:314`
  - `void ParamAutoPage_Shown(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:330`
  - `void btnAddNewConfig_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:339`
  - `void LoadParamOnForm()` — `UIDesign/TabPage/ProcessControlPage.cs:358`
  - `void CollectParamFromForm()` — `UIDesign/TabPage/ProcessControlPage.cs:377`
  - `void LoadAutoParam()` — `UIDesign/TabPage/ProcessControlPage.cs:396`
  - `void BtnSaveAutoParam_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:404`
  - `void ApplyAdaptUiToMemory()` — `UIDesign/TabPage/ProcessControlPage.cs:426`
  - `void BtnReadAutoParam_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:448`
  - `void btnCorAutoParam_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:460`
  - `void btnCorBaseline_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:471`
  - `void btnShowAutoParam_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:479`
  - `void ApplyGalvoParamsToHead()` — `UIDesign/TabPage/ProcessControlPage.cs:498`
  - `void BtnReadLaserZone_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:531`
  - `void BtnModifyLaserZone_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:552`
  - `void BtnSaveLaserZone_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:566`
  - `void LoadProcessEnableOnForm()` — `UIDesign/TabPage/ProcessControlPage.cs:599`
  - `void ApplyDefaultCommandModes()` — `UIDesign/TabPage/ProcessControlPage.cs:618`
  - `void radioQuickY_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:650`
  - `void BuildYActionDetail(AntdUI.Radio radio, WeldParamConfig cfg)` — `UIDesign/TabPage/ProcessControlPage.cs:665`
  - `void ExecuteYAction(AntdUI.Radio radio, WeldParamConfig cfg)` — `UIDesign/TabPage/ProcessControlPage.cs:682`
  - `void MoveAxisHome(string[] keys, string actionName)` — `UIDesign/TabPage/ProcessControlPage.cs:710`
  - `void MoveAxisToTarget(string[] keys, double targetMm, string actionName)` — `UIDesign/TabPage/ProcessControlPage.cs:728`
  - `void HandleAxisReject(string rejectCode, string rejectDetail, string[] keys, string actionName)` — `UIDesign/TabPage/ProcessControlPage.cs:754`
  - `void ReportAxisResult(string actionName, bool ok, string evidence, string rejectDetail)` — `UIDesign/TabPage/ProcessControlPage.cs:789`
  - `void GalvoPatternText(WsgGalvoPattern pattern)` — `UIDesign/TabPage/ProcessControlPage.cs:838`
  - `void RefreshActionStates()` — `UIDesign/TabPage/ProcessControlPage.cs:850`
  - `void SetControlEnabled(Control control, bool value)` — `UIDesign/TabPage/ProcessControlPage.cs:898`
  - `void SetText(Control control, string text)` — `UIDesign/TabPage/ProcessControlPage.cs:907`
  - `void UpdateTaAutoGateHint(bool initDone, bool taMotionReady, bool taReady, string degradedReason)` — `UIDesign/TabPage/ProcessControlPage.cs:921`
  - `void LoadGalvoActionUi()` — `UIDesign/TabPage/ProcessControlPage.cs:943`
  - `void LoadGalvoShapeToInputs()` — `UIDesign/TabPage/ProcessControlPage.cs:959`
  - `void CurrentGalvoPattern()` — `UIDesign/TabPage/ProcessControlPage.cs:971`
  - `void ApplyGalvoPatternSelection()` — `UIDesign/TabPage/ProcessControlPage.cs:983`
  - `void ClearGalvoPatternSelection()` — `UIDesign/TabPage/ProcessControlPage.cs:1004`
  - `void btnGalvoManualStart_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:1013`
  - `void btnGalvoManualStop_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:1036`
  - `void ReadConfiguredGalvoPattern()` — `UIDesign/TabPage/ProcessControlPage.cs:1051`
  - `void EnableBackColorPaint(AntdUI.Radio radio)` — `UIDesign/TabPage/ProcessControlPage.cs:1061`
  - `void PrepareActionRadioBackColor()` — `UIDesign/TabPage/ProcessControlPage.cs:1079`
  - `void ConfirmInstruction(AntdUI.Radio radio, string axisName, string detail)` — `UIDesign/TabPage/ProcessControlPage.cs:1097`
  - `void UiMessage(bool error, string text)` — `UIDesign/TabPage/ProcessControlPage.cs:1110`
  - `void ApplyActionBack(AntdUI.Radio radio, bool ok)` — `UIDesign/TabPage/ProcessControlPage.cs:1131`
  - `void ApplyActionRunning(AntdUI.Radio radio)` — `UIDesign/TabPage/ProcessControlPage.cs:1143`
  - `void ResetActionBack(AntdUI.Radio radio)` — `UIDesign/TabPage/ProcessControlPage.cs:1154`
  - `void ResetOtherRadioBacks(AntdUI.Radio current)` — `UIDesign/TabPage/ProcessControlPage.cs:1165`
  - `void RadioGroupOf(AntdUI.Radio radio)` — `UIDesign/TabPage/ProcessControlPage.cs:1179`
  - `void RunInstruction(AntdUI.Radio radio, string axisName, string detail, Func<bool> exec, AntdUI.Radio last)` — `UIDesign/TabPage/ProcessControlPage.cs:1221`
  - `void MarkInstructionRejected(AntdUI.Radio radio, string logText)` — `UIDesign/TabPage/ProcessControlPage.cs:1283`
  - `void InstructionWorker(AntdUI.Radio radio, Func<bool> exec)` — `UIDesign/TabPage/ProcessControlPage.cs:1291`
  - `void RevertInstructionSelection(AntdUI.Radio radio, AntdUI.Radio last)` — `UIDesign/TabPage/ProcessControlPage.cs:1321`
  - `void ResolveAxisGateReason(AntdUI.Radio radio, MontionManager manager)` — `UIDesign/TabPage/ProcessControlPage.cs:1340`
  - `void ResolveInstructionAxisKey(AntdUI.Radio radio)` — `UIDesign/TabPage/ProcessControlPage.cs:1367`
  - `void LaserWeldHeadWorkflowInstance()` — `UIDesign/TabPage/ProcessControlPage.cs:1385`
  - `void MotionControlWorkflowInstance()` — `UIDesign/TabPage/ProcessControlPage.cs:1391`
  - `void DoTaAuto()` — `UIDesign/TabPage/ProcessControlPage.cs:1397`
  - `void DoTaBreak()` — `UIDesign/TabPage/ProcessControlPage.cs:1405`
  - `void DoTaPose1()` — `UIDesign/TabPage/ProcessControlPage.cs:1411`
  - `void DoTaPose2()` — `UIDesign/TabPage/ProcessControlPage.cs:1417`
  - `void DoTaRetract()` — `UIDesign/TabPage/ProcessControlPage.cs:1423`
  - `void DoTaZeroPose()` — `UIDesign/TabPage/ProcessControlPage.cs:1431`
  - `void DoLaAuto()` — `UIDesign/TabPage/ProcessControlPage.cs:1437`
  - `void DoLaSpot1()` — `UIDesign/TabPage/ProcessControlPage.cs:1442`
  - `void DoLaSpot2()` — `UIDesign/TabPage/ProcessControlPage.cs:1447`
  - `void DoLaPose1()` — `UIDesign/TabPage/ProcessControlPage.cs:1452`
  - `void DoLaDefaultFocus()` — `UIDesign/TabPage/ProcessControlPage.cs:1457`
  - `void SaveGalvoPattern(WsgGalvoPattern pattern)` — `UIDesign/TabPage/ProcessControlPage.cs:1462`
  - `void SetGalvoPattern(WsgGalvoPattern pattern)` — `UIDesign/TabPage/ProcessControlPage.cs:1472`
  - `void radioQuickTa_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:1481`
  - `void radioQuickTa_Click(object sender, EventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:1493`
  - `void WireTaInstructionClicks()` — `UIDesign/TabPage/ProcessControlPage.cs:1506`
  - `void BuildTaActionDetail(AntdUI.Radio radio)` — `UIDesign/TabPage/ProcessControlPage.cs:1520`
  - `void ExecuteTaAction(AntdUI.Radio radio)` — `UIDesign/TabPage/ProcessControlPage.cs:1551`
  - `void radioQuickLa_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/ProcessControlPage.cs:1567`
  - `void BuildLaActionDetail(AntdUI.Radio radio)` — `UIDesign/TabPage/ProcessControlPage.cs:1594`
  - `void ExecuteLaAction(AntdUI.Radio radio)` — `UIDesign/TabPage/ProcessControlPage.cs:1616`
  - `void RadioToGalvoPattern(string name)` — `UIDesign/TabPage/ProcessControlPage.cs:1631`
  - `void GalvoPatternToRadio(WsgGalvoPattern? pattern)` — `UIDesign/TabPage/ProcessControlPage.cs:1646`
  - `void LoadTaParamUi()` — `UIDesign/TabPage/ProcessControlPage.cs:1664`
  - `void ApplyTaToConfig(WeldParamConfig ta)` — `UIDesign/TabPage/ProcessControlPage.cs:1682`
  - `void LoadLaParamUi()` — `UIDesign/TabPage/ProcessControlPage.cs:1736`
  - `void ApplyLaToConfig(WeldParamConfig la)` — `UIDesign/TabPage/ProcessControlPage.cs:1750`
  - `void LoadYtCalibUi()` — `UIDesign/TabPage/ProcessControlPage.cs:1776`
  - `void ApplyYtCalibToConfig(WeldParamConfig cfg)` — `UIDesign/TabPage/ProcessControlPage.cs:1788`
  - `void LoadAlgoConfigOnForm()` — `UIDesign/TabPage/ProcessControlPage.cs:1805`
  - `void EnsureTaParamFilled()` — `UIDesign/TabPage/ProcessControlPage.cs:1815`
  - `void LoadFlowSwitchOnForm()` — `UIDesign/TabPage/ProcessControlPage.cs:1824`
  - `void ParseCalibDouble(AntdUI.Input box, double fallback)` — `UIDesign/TabPage/ProcessControlPage.cs:1836`
  - `void ParseInt(AntdUI.Input box, int fallback)` — `UIDesign/TabPage/ProcessControlPage.cs:1848`
  - `void ShowInputStringDialog(string value, string prompt)` — `UIDesign/TabPage/ProcessControlPage.cs:1862`
- 构造（1）：
  - `ProcessControlPage()` — `UIDesign/TabPage/ProcessControlPage.cs:192`

## RecordConfigForm

- 签名：`partial class RecordConfigForm`
- 位置：`UIDesign/SubDialog/DataReviewerDialog/RecordConfigForm.cs:11`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.DataReviewerDialog`
- 方法（5）：
  - `void LoadConfig()` — `UIDesign/SubDialog/DataReviewerDialog/RecordConfigForm.cs:28`
  - `void SaveConfig()` — `UIDesign/SubDialog/DataReviewerDialog/RecordConfigForm.cs:43`
  - `void btnBrowseRecord_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/RecordConfigForm.cs:69`
  - `void btnSave_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/RecordConfigForm.cs:80`
  - `void btnCancel_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/RecordConfigForm.cs:105`
- 构造（2）：
  - `RecordConfigForm()` — `UIDesign/SubDialog/DataReviewerDialog/RecordConfigForm.cs:18`
  - `RecordConfigForm(Window _window)` — `UIDesign/SubDialog/DataReviewerDialog/RecordConfigForm.cs:20`

## RefreshSnapshot

- 签名：`private sealed class RefreshSnapshot`
- 位置：`UIDesign/TabPage/SystemControlPage.cs:2770`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 成员：（无）

## RenderParamForm

- 签名：`partial class RenderParamForm`
- 位置：`UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs:9`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.DataReviewerDialog`
- 方法（8）：
  - `void InitializeComboBoxItems()` — `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs:33`
  - `void LoadConfigValues()` — `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs:49`
  - `void SaveConfigValues()` — `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs:91`
  - `void uiComboBox1_SelectedIndexChanged(object sender, IntEventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs:141`
  - `void UpdateParamVisibility()` — `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs:147`
  - `void AddParamRow(int row, Control label1, Control control1, Control label2, Control control2)` — `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs:189`
  - `void btnSave_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs:206`
  - `void btnCancel_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs:216`
- 构造（2）：
  - `RenderParamForm()` — `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs:17`
  - `RenderParamForm(Window _window)` — `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs:20`

## RowSpec

- 签名：`private sealed class RowSpec`
- 位置：`UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs:14`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.MotionControlDialog`
- 成员：（无）

## SensorRow

- 签名：`private class SensorRow`
- 位置：`UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:27`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.IntelligentLaserDialog`
- 属性（6）：
  - `int No { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:29`
  - `bool Selected { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:32`
  - `string Ip { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:43`
  - `string SerialNumber { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:44`
  - `string SoftwareVersion { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:45`
  - `string SensorType { get; set; }` — `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs:46`

## SeriesGroup

- 签名：`private sealed class SeriesGroup`
- 位置：`UIDesign/ControlPage/DataReviewerPage.cs:157`
- 命名空间：`AdaWeldSystem.UIDesign.ControlPage`
- 属性（2）：
  - `string Title { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:159`
  - `List<SeriesItem> Items { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:161`

## SeriesItem

- 签名：`private sealed class SeriesItem`
- 位置：`UIDesign/ControlPage/DataReviewerPage.cs:139`
- 命名空间：`AdaWeldSystem.UIDesign.ControlPage`
- 属性（5）：
  - `AntdUI.Checkbox Box { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:141`
  - `string Text { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:144`
  - `string Name { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:146`
  - `Color Color { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:147`
  - `Func<SessionCharts, ChartVar> GetChart { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:150`

## SessionCharts

- 签名：`private sealed class SessionCharts`
- 位置：`UIDesign/ControlPage/DataReviewerPage.cs:69`
- 命名空间：`AdaWeldSystem.UIDesign.ControlPage`
- 方法（1）：
  - `void Add(string seriesName, double x, double y)` — `UIDesign/ControlPage/DataReviewerPage.cs:93`
- 属性（1）：
  - `int PointCount { get; set; }` — `UIDesign/ControlPage/DataReviewerPage.cs:83`

## SystemControlPage

- 签名：`partial class SystemControlPage`
- 位置：`UIDesign/TabPage/SystemControlPage.cs:23`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 方法（157）：
  - `void ApplyPermissionGate()` — `UIDesign/TabPage/SystemControlPage.cs:133`
  - `void tabsSystem_SelectedIndexChanged(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:150`
  - `void EnsureAdminForWrite(string action)` — `UIDesign/TabPage/SystemControlPage.cs:164`
  - `void OnOperateLevelChanged(object sender, OperateLevel level)` — `UIDesign/TabPage/SystemControlPage.cs:177`
  - `void Log(string message, MessageLevel level)` — `UIDesign/TabPage/SystemControlPage.cs:191`
  - `void GetConfig()` — `UIDesign/TabPage/SystemControlPage.cs:196`
  - `void IsMotionReady()` — `UIDesign/TabPage/SystemControlPage.cs:203`
  - `void MakeLight(bool on, bool alarmSemantics)` — `UIDesign/TabPage/SystemControlPage.cs:214`
  - `void MakeLightGray()` — `UIDesign/TabPage/SystemControlPage.cs:223`
  - `void InitTables()` — `UIDesign/TabPage/SystemControlPage.cs:232`
  - `void CreateAxisColumns()` — `UIDesign/TabPage/SystemControlPage.cs:253`
  - `void BindEvents()` — `UIDesign/TabPage/SystemControlPage.cs:271`
  - `void LoadAxisRows()` — `UIDesign/TabPage/SystemControlPage.cs:368`
  - `void IsTraceAxis(DeltaAxisConfig axis)` — `UIDesign/TabPage/SystemControlPage.cs:407`
  - `void LoadTaAxisRow()` — `UIDesign/TabPage/SystemControlPage.cs:419`
  - `void GetTaRow()` — `UIDesign/TabPage/SystemControlPage.cs:448`
  - `void FillAxisRuntime(AxisRow row)` — `UIDesign/TabPage/SystemControlPage.cs:457`
  - `void CollectAxisReadout(DeltaAxisConfig config)` — `UIDesign/TabPage/SystemControlPage.cs:475`
  - `void CollectAxisReadouts(DeltaAxisConfig config)` — `UIDesign/TabPage/SystemControlPage.cs:502`
  - `void CollectAxisReadouts(List<DeltaAxisConfig> configs)` — `UIDesign/TabPage/SystemControlPage.cs:510`
  - `void ApplyAxisReadout(AxisRow row, AxisReadoutSnapshot snapshot)` — `UIDesign/TabPage/SystemControlPage.cs:522`
  - `void TableAxis_CellEndEdit(object sender, AntdUI.TableEndEditEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:558`
  - `void TableAxis_CellButtonClick(object sender, AntdUI.TableButtonEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:593`
  - `void TableTa_CellButtonClick(object sender, AntdUI.TableButtonEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:607`
  - `void OpenTaAxisEditor()` — `UIDesign/TabPage/SystemControlPage.cs:614`
  - `void TryTraceOperation(AxisManualOperation operation, double value, ushort dir, string axisName, bool servoOn, bool commandOk, string rejectReason)` — `UIDesign/TabPage/SystemControlPage.cs:656`
  - `void BuildOutcome(bool gatePassed, string rejectReason, bool commandOk, string axisName, string failReason)` — `UIDesign/TabPage/SystemControlPage.cs:671`
  - `void TryGetAxisPositionMm(string[] roleKeys, double positionMm, string axisName)` — `UIDesign/TabPage/SystemControlPage.cs:684`
  - `void GetFixedRow()` — `UIDesign/TabPage/SystemControlPage.cs:695`
  - `void FixedServo_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:700`
  - `void FixedHome_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:710`
  - `void FixedStop_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:722`
  - `void FixedMoveTo_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:735`
  - `void FixedStepBack_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:750`
  - `void FixedStepFwd_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:755`
  - `void FixedStep(int sign)` — `UIDesign/TabPage/SystemControlPage.cs:761`
  - `void FixedNegBack_MouseDown(object sender, MouseEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:780`
  - `void FixedNegFwd_MouseDown(object sender, MouseEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:785`
  - `void FixedJog(ushort dir)` — `UIDesign/TabPage/SystemControlPage.cs:792`
  - `void FixedJog_MouseUp(object sender, MouseEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:812`
  - `void FixedJog_MouseLeave(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:820`
  - `void StopJog()` — `UIDesign/TabPage/SystemControlPage.cs:826`
  - `void ResetJogFlag()` — `UIDesign/TabPage/SystemControlPage.cs:843`
  - `void IsGroupBusy(ManualOpGroup group)` — `UIDesign/TabPage/SystemControlPage.cs:874`
  - `void SetGroupBusy(ManualOpGroup group, bool busy)` — `UIDesign/TabPage/SystemControlPage.cs:888`
  - `void StartManualOperation(ManualOpGroup group, string actionLabel, Func<ManualOpOutcome> exec)` — `UIDesign/TabPage/SystemControlPage.cs:922`
  - `void FinishManualOperation(ManualOpGroup group, string actionLabel, ManualOpOutcome outcome)` — `UIDesign/TabPage/SystemControlPage.cs:969`
  - `void RefreshActionButtonStates()` — `UIDesign/TabPage/SystemControlPage.cs:995`
  - `void SetControlEnabled(Control control, bool value)` — `UIDesign/TabPage/SystemControlPage.cs:1032`
  - `void RefreshLaserHeadRuntime()` — `UIDesign/TabPage/SystemControlPage.cs:1040`
  - `void ParseStep(AxisRow row, double fallback)` — `UIDesign/TabPage/SystemControlPage.cs:1051`
  - `void ParseTarget(AxisRow row)` — `UIDesign/TabPage/SystemControlPage.cs:1057`
  - `void OpenAxisEditor(AxisRow row)` — `UIDesign/TabPage/SystemControlPage.cs:1068`
  - `void LoadAlgoThreshOnForm()` — `UIDesign/TabPage/SystemControlPage.cs:1096`
  - `void LoadLaserCalibOnForm()` — `UIDesign/TabPage/SystemControlPage.cs:1130`
  - `void LoadTimeoutOnForm()` — `UIDesign/TabPage/SystemControlPage.cs:1144`
  - `void BtnReadLocal_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1178`
  - `void BtnApplyParams_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1191`
  - `void BtnSaveLocal_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1267`
  - `void ParseCalibDouble(AntdUI.Input box, double fallback)` — `UIDesign/TabPage/SystemControlPage.cs:1280`
  - `void ParseInt(AntdUI.Input box, int fallback)` — `UIDesign/TabPage/SystemControlPage.cs:1288`
  - `void LoadProcessEnableOnForm()` — `UIDesign/TabPage/SystemControlPage.cs:1298`
  - `void SaveProcessEnable()` — `UIDesign/TabPage/SystemControlPage.cs:1319`
  - `void swEnableGalvoWeaveQuick_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1338`
  - `void swEnableSeamTrace_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1347`
  - `void swEnableAdapt_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1356`
  - `void swEnableWireAlign_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1365`
  - `void swEnableTempCtrl_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1374`
  - `void PopulateComboBoxItems()` — `UIDesign/TabPage/SystemControlPage.cs:1384`
  - `void LoadFromModel()` — `UIDesign/TabPage/SystemControlPage.cs:1392`
  - `void FrequencyToIndex(int hz)` — `UIDesign/TabPage/SystemControlPage.cs:1404`
  - `void IndexToFrequency(int index)` — `UIDesign/TabPage/SystemControlPage.cs:1418`
  - `void BtnSaveSim_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1429`
  - `void SyncSimParamsToController()` — `UIDesign/TabPage/SystemControlPage.cs:1437`
  - `void BtnStartSim_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1444`
  - `void StopSimulationFlows()` — `UIDesign/TabPage/SystemControlPage.cs:1519`
  - `void OnSimulationStopped(object sender, SimulationStoppedEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1531`
  - `void OnLineLaserStateChanged(object sender, WeldStatusChangedEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1561`
  - `void OnMainDeviceStatusChanged(object sender, MainDeviceStatusChangedEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1589`
  - `void ShowSimErrorDialog(string msg)` — `UIDesign/TabPage/SystemControlPage.cs:1610`
  - `void ShowSimStopMessage(string reason)` — `UIDesign/TabPage/SystemControlPage.cs:1629`
  - `void LogSimStopSummary(string reason)` — `UIDesign/TabPage/SystemControlPage.cs:1640`
  - `void SubscribeLineLaserEvents()` — `UIDesign/TabPage/SystemControlPage.cs:1654`
  - `void UnsubscribeLineLaserEvents()` — `UIDesign/TabPage/SystemControlPage.cs:1661`
  - `void SetSimButtonMode(SimButtonMode mode)` — `UIDesign/TabPage/SystemControlPage.cs:1667`
  - `void ShowSimErrorButton()` — `UIDesign/TabPage/SystemControlPage.cs:1695`
  - `void StopSimOnWeldComplete()` — `UIDesign/TabPage/SystemControlPage.cs:1701`
  - `void CleanupSimError()` — `UIDesign/TabPage/SystemControlPage.cs:1714`
  - `void AcceptRefreshSwitchOn(AntdUI.Switch toggle, string zoneName, Func<bool> zoneReady)` — `UIDesign/TabPage/SystemControlPage.cs:1805`
  - `void ApplyRefreshSwitchGate()` — `UIDesign/TabPage/SystemControlPage.cs:1823`
  - `void GateRefreshSwitch(AntdUI.Switch toggle, bool flag, bool ready)` — `UIDesign/TabPage/SystemControlPage.cs:1839`
  - `void IsMotionZoneReady()` — `UIDesign/TabPage/SystemControlPage.cs:1858`
  - `void IsLaZoneReady()` — `UIDesign/TabPage/SystemControlPage.cs:1865`
  - `void IsTaAxisLoaded()` — `UIDesign/TabPage/SystemControlPage.cs:1872`
  - `void IsTaRefreshReady()` — `UIDesign/TabPage/SystemControlPage.cs:1879`
  - `void SwGalvoRefresh_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1887`
  - `void SwLARefresh_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1906`
  - `void SwTARefresh_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1925`
  - `void BtnLhRead_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1944`
  - `void BtnLhApply_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1967`
  - `void BtnLhSave_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:1981`
  - `void LoadOpticsFromConfig()` — `UIDesign/TabPage/SystemControlPage.cs:1988`
  - `void LoadTempFromConfig()` — `UIDesign/TabPage/SystemControlPage.cs:2026`
  - `void UpdateMotorStateLabel()` — `UIDesign/TabPage/SystemControlPage.cs:2047`
  - `void UpdateCurveInfo()` — `UIDesign/TabPage/SystemControlPage.cs:2055`
  - `void RefreshGalvoStatus()` — `UIDesign/TabPage/SystemControlPage.cs:2064`
  - `void CollectGalvo()` — `UIDesign/TabPage/SystemControlPage.cs:2070`
  - `void ApplyGalvo(GalvoSnapshot snapshot)` — `UIDesign/TabPage/SystemControlPage.cs:2100`
  - `void BtnOptGalvoEnable_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2112`
  - `void RefreshLaMotorStatus()` — `UIDesign/TabPage/SystemControlPage.cs:2142`
  - `void CollectLaMotor()` — `UIDesign/TabPage/SystemControlPage.cs:2148`
  - `void ApplyLaMotor(LaMotorSnapshot snapshot)` — `UIDesign/TabPage/SystemControlPage.cs:2174`
  - `void RefreshTaMotorStatus()` — `UIDesign/TabPage/SystemControlPage.cs:2182`
  - `void TryTaOperation(AxisManualOperation operation, double value, ushort dir, string axisName, bool servoOn, bool commandOk, string rejectReason)` — `UIDesign/TabPage/SystemControlPage.cs:2198`
  - `void ApplyLaserHeadOnForm()` — `UIDesign/TabPage/SystemControlPage.cs:2208`
  - `void SaveLaserHead()` — `UIDesign/TabPage/SystemControlPage.cs:2291`
  - `void BtnOptMotorEnable_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2352`
  - `void BtnOptMotorBack_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2378`
  - `void BtnOptMotorFwd_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2386`
  - `void BtnOptMotorMoveTo_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2394`
  - `void StepLaMotor(int sign)` — `UIDesign/TabPage/SystemControlPage.cs:2424`
  - `void TaServo_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2457`
  - `void TaStop_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2471`
  - `void TaHome_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2484`
  - `void TaMoveTo_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2501`
  - `void TaStepBack_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2521`
  - `void TaStepFwd_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2529`
  - `void TaStep(int sign)` — `UIDesign/TabPage/SystemControlPage.cs:2534`
  - `void TaNegBack_MouseDown(object sender, MouseEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2559`
  - `void TaNegFwd_MouseDown(object sender, MouseEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2560`
  - `void TaNegBack_MouseUp(object sender, MouseEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2561`
  - `void TaNegFwd_MouseUp(object sender, MouseEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2562`
  - `void TaNegBack_MouseLeave(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2563`
  - `void TaNegFwd_MouseLeave(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2564`
  - `void StartTaJog(ushort dir)` — `UIDesign/TabPage/SystemControlPage.cs:2568`
  - `void StopTaJog()` — `UIDesign/TabPage/SystemControlPage.cs:2589`
  - `void ResetTaJogFlag()` — `UIDesign/TabPage/SystemControlPage.cs:2606`
  - `void BtnOptGalvoHome_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2614`
  - `void BtnOptImportCurve_Click(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2639`
  - `void Warn(string message)` — `UIDesign/TabPage/SystemControlPage.cs:2657`
  - `void TryReadDouble(AntdUI.Input input, double value)` — `UIDesign/TabPage/SystemControlPage.cs:2663`
  - `void TryReadInt(AntdUI.Input input, int value)` — `UIDesign/TabPage/SystemControlPage.cs:2672`
  - `void SwAutoRefresh_CheckedChanged(object sender, AntdUI.BoolEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2687`
  - `void IsRefreshPageVisible()` — `UIDesign/TabPage/SystemControlPage.cs:2706`
  - `void OnMotionStateSwitched(object sender, SubDeviceStateChangedEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2715`
  - `void OnInitializationCompleted(bool allReady)` — `UIDesign/TabPage/SystemControlPage.cs:2728`
  - `void OnInitializationSummaryReady(object sender, DeviceInitSummaryEventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2742`
  - `void OnAxisReadyChanged()` — `UIDesign/TabPage/SystemControlPage.cs:2756`
  - `void TimerRefresh_Tick(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2816`
  - `void CollectRefreshSnapshot(RefreshSnapshot request)` — `UIDesign/TabPage/SystemControlPage.cs:2874`
  - `void ApplyRefreshSnapshot(RefreshSnapshot request)` — `UIDesign/TabPage/SystemControlPage.cs:2890`
  - `void RefreshRuntime()` — `UIDesign/TabPage/SystemControlPage.cs:2930`
  - `void ApplyAxisReadouts(IList<AxisRow> rows, IList<AxisReadoutSnapshot> readouts)` — `UIDesign/TabPage/SystemControlPage.cs:2945`
  - `void AxisReadoutSignature(AxisReadoutSnapshot snapshot)` — `UIDesign/TabPage/SystemControlPage.cs:2964`
  - `void AxisReadoutSignatureChanged(AxisReadoutSnapshot snapshot)` — `UIDesign/TabPage/SystemControlPage.cs:2972`
  - `void SystemControlPage_HandleDestroyed(object sender, EventArgs e)` — `UIDesign/TabPage/SystemControlPage.cs:2985`
  - `void DisposeComponents()` — `UIDesign/TabPage/SystemControlPage.cs:2991`
- 构造（1）：
  - `SystemControlPage()` — `UIDesign/TabPage/SystemControlPage.cs:100`

## TemperatureSnapshot

- 签名：`private sealed class TemperatureSnapshot`
- 位置：`UIDesign/ControlPage/DeviceMonitorPage.cs:104`
- 命名空间：`AdaWeldSystem.UIDesign.ControlPage`
- 成员：（无）

## TxCmdOption

- 签名：`private sealed class TxCmdOption`
- 位置：`UIDesign/TabPage/CommSettingPage.cs:356`
- 命名空间：`AdaWeldSystem.UIDesign.TabPage`
- 成员：（无）

## UserEditForm

- 签名：`partial class UserEditForm`
- 位置：`UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs:11`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.UserManagerDialog`
- 方法（4）：
  - `void InitTableColumns()` — `UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs:34`
  - `void LoadUserList()` — `UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs:45`
  - `void btnSave_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs:69`
  - `void btnRefresh_Click(object sender, EventArgs e)` — `UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs:117`
- 构造（2）：
  - `UserEditForm()` — `UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs:20`
  - `UserEditForm(Window _window)` — `UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs:22`

## UserRow

- 签名：`public class UserRow`
- 位置：`UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs:123`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.UserManagerDialog`
- 属性（2）：
  - `string UserName { get; set; }` — `UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs:125`
  - `string UserLevel { get; set; }` — `UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs:126`

## XmlPropertyRow

- 签名：`class XmlPropertyRow`
- 位置：`UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:19`
- 命名空间：`AdaWeldSystem.UIDesign.SubDialog.CommConfigDialog`
- 属性（6）：
  - `string Name { get; set; }` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:22`
  - `string Value { get; set; }` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:25`
  - `XName AttributeName { get; set; }` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:28`
  - `bool IsElementName { get; set; }` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:31`
  - `bool IsElementValue { get; set; }` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:34`
  - `bool IsReadOnly { get; set; }` — `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs:37`

## 相关页面

- [[architecture/CodeMap]]
