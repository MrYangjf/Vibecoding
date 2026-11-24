---
title: CodeMap-Relations-Methods-UIDesign-2 — 代码地图·方法级影响面·UIDesign（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-UIDesign-2 — 方法级影响面（低置信 · 调用方在 UIDesign · 名首字母 N-Z）

> **一句话**：**调用方位于 `UIDesign` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 162 |
| 调用点数 | 178 |

## 章节导航

- [OnDeviceSwitchClick](#OnDeviceSwitchClick)
- [OnIlJobParamsChanged](#OnIlJobParamsChanged)
- [OnIlStateChanged](#OnIlStateChanged)
- [OnInitializationCompleted](#OnInitializationCompleted)
- [OnLineLaserStateChanged](#OnLineLaserStateChanged)
- [OnMainDeviceStatusChanged](#OnMainDeviceStatusChanged)
- [OnMatUpdated](#OnMatUpdated)
- [OnMotionStateSwitched](#OnMotionStateSwitched)
- [OnOperateLevelChanged](#OnOperateLevelChanged)
- [OnPropertyChanged](#OnPropertyChanged)
- [OnSimulationStopped](#OnSimulationStopped)
- [OnWorkflowStateChanged](#OnWorkflowStateChanged)
- [OpenAxisEditor](#OpenAxisEditor)
- [OpenTaAxisEditor](#OpenTaAxisEditor)
- [OperateLevelControl](#OperateLevelControl)
- [ParseAndValidate](#ParseAndValidate)
- [ParseCalibDouble](#ParseCalibDouble)
- [ParseDebugDouble](#ParseDebugDouble)
- [ParseDouble](#ParseDouble)
- [ParseInt](#ParseInt)
- [ParseRecordTime](#ParseRecordTime)
- [ParseShort](#ParseShort)
- [ParseStep](#ParseStep)
- [ParseTarget](#ParseTarget)
- [ParseUShort](#ParseUShort)
- [PlaySelected](#PlaySelected)
- [PopulateComboBoxItems](#PopulateComboBoxItems)
- [PostToUi](#PostToUi)
- [PrepareActionRadioBackColor](#PrepareActionRadioBackColor)
- [RadioGroupOf](#RadioGroupOf)
- [RadioToGalvoPattern](#RadioToGalvoPattern)
- [ReadConfiguredGalvoPattern](#ReadConfiguredGalvoPattern)
- [ReadDirInput](#ReadDirInput)
- [RebuildChartDatasets](#RebuildChartDatasets)
- [RefreshActionButtonStates](#RefreshActionButtonStates)
- [RefreshActionStates](#RefreshActionStates)
- [RefreshDeltaPreview](#RefreshDeltaPreview)
- [RefreshDisplay](#RefreshDisplay)
- [RefreshFpsSelect](#RefreshFpsSelect)
- [RefreshGalvoStatus](#RefreshGalvoStatus)
- [RefreshInspectResult](#RefreshInspectResult)
- [RefreshJobFlow](#RefreshJobFlow)
- [RefreshJobParams](#RefreshJobParams)
- [RefreshJobSelect](#RefreshJobSelect)
- [RefreshLaMotorStatus](#RefreshLaMotorStatus)
- [RefreshLaserHeadRuntime](#RefreshLaserHeadRuntime)
- [RefreshParamCharts](#RefreshParamCharts)
- [RefreshParamChartsUi](#RefreshParamChartsUi)
- [RefreshRuntime](#RefreshRuntime)
- [RefreshTaMotorStatus](#RefreshTaMotorStatus)
- [RefreshTemperature](#RefreshTemperature)
- [RefreshUi](#RefreshUi)
- [ReloadDeltaConfigOnly](#ReloadDeltaConfigOnly)
- [ReloadSystemConfig](#ReloadSystemConfig)
- [RemoveDeltaRow](#RemoveDeltaRow)
- [ReportAxisResult](#ReportAxisResult)
- [RescanFromDirectory](#RescanFromDirectory)
- [ResetActionBack](#ResetActionBack)
- [ResetJogFlag](#ResetJogFlag)
- [ResetOtherRadioBacks](#ResetOtherRadioBacks)
- [ResetTaJogFlag](#ResetTaJogFlag)
- [ResolveAxisGateReason](#ResolveAxisGateReason)
- [ResolveInstructionAxisKey](#ResolveInstructionAxisKey)
- [RevertInstructionSelection](#RevertInstructionSelection)
- [RunInstruction](#RunInstruction)
- [SaveConfig](#SaveConfig)
- [SaveConfigValues](#SaveConfigValues)
- [SaveGalvoPattern](#SaveGalvoPattern)
- [SaveLaserHead](#SaveLaserHead)
- [SaveProcessEnable](#SaveProcessEnable)
- [ScanDeltaDirectory](#ScanDeltaDirectory)
- [Section](#Section)
- [SelectFirstNode](#SelectFirstNode)
- [SeriesCheckboxes](#SeriesCheckboxes)
- [SessionLabel](#SessionLabel)
- [SetConnectIp](#SetConnectIp)
- [SetControlEnabled](#SetControlEnabled)
- [SetGalvoPattern](#SetGalvoPattern)
- [SetGroupBusy](#SetGroupBusy)
- [SetIlControlsEnabled](#SetIlControlsEnabled)
- [SetPlayBarVisible](#SetPlayBarVisible)
- [SetPlayCaption](#SetPlayCaption)
- [SetRowCellValue](#SetRowCellValue)
- [SetSimButtonMode](#SetSimButtonMode)
- [SetText](#SetText)
- [SetWeldFlowStep](#SetWeldFlowStep)
- [SetupMergedChart](#SetupMergedChart)
- [ShowCorButton](#ShowCorButton)
- [ShowGroupOnly](#ShowGroupOnly)
- [ShowHoverTip](#ShowHoverTip)
- [ShowMat](#ShowMat)
- [ShowSimErrorButton](#ShowSimErrorButton)
- [ShowSimErrorDialog](#ShowSimErrorDialog)
- [ShowSimStopMessage](#ShowSimStopMessage)
- [ShowStatus](#ShowStatus)
- [ShowTreeNode](#ShowTreeNode)
- [ShowWeldPreviewFrame](#ShowWeldPreviewFrame)
- [StartActionRefresh](#StartActionRefresh)
- [StartManualOperation](#StartManualOperation)
- [StartProfilePolling](#StartProfilePolling)
- [StartTaJog](#StartTaJog)
- [StepLaMotor](#StepLaMotor)
- [StopJog](#StopJog)
- [StopProfilePolling](#StopProfilePolling)
- [StopSimOnWeldComplete](#StopSimOnWeldComplete)
- [StopSimulationFlows](#StopSimulationFlows)
- [StopTaJog](#StopTaJog)
- [SubscribeLineLaserEvents](#SubscribeLineLaserEvents)
- [SyncFromHardwareCore](#SyncFromHardwareCore)
- [SyncSelectedJobFromDevice](#SyncSelectedJobFromDevice)
- [SyncSimParamsToController](#SyncSimParamsToController)
- [TaStep](#TaStep)
- [ToPlaybackRow](#ToPlaybackRow)
- [ToggleLineLaserConnection](#ToggleLineLaserConnection)
- [TotalAdjustCount](#TotalAdjustCount)
- [TryGetAxisPositionMm](#TryGetAxisPositionMm)
- [TryNumber](#TryNumber)
- [TryParseHex](#TryParseHex)
- [TryPassCommAction](#TryPassCommAction)
- [TryPassPageAction](#TryPassPageAction)
- [TryReadDouble](#TryReadDouble)
- [TryReadInt](#TryReadInt)
- [TryTaOperation](#TryTaOperation)
- [TryTraceOperation](#TryTraceOperation)
- [UiMessage](#UiMessage)
- [UnsubscribeLineLaserEvents](#UnsubscribeLineLaserEvents)
- [UnwirePlaybackEvents](#UnwirePlaybackEvents)
- [UpdateApplyButtonsState](#UpdateApplyButtonsState)
- [UpdateChartUI](#UpdateChartUI)
- [UpdateConnLabel](#UpdateConnLabel)
- [UpdateConnectionUi](#UpdateConnectionUi)
- [UpdateConnectionUiCore](#UpdateConnectionUiCore)
- [UpdateCurveInfo](#UpdateCurveInfo)
- [UpdateDeltaStatusHint](#UpdateDeltaStatusHint)
- [UpdateDeltaStatusText](#UpdateDeltaStatusText)
- [UpdateFpsDropdownState](#UpdateFpsDropdownState)
- [UpdateJobButtonsState](#UpdateJobButtonsState)
- [UpdateJointTypeLabel](#UpdateJointTypeLabel)
- [UpdateLaserSensorUi](#UpdateLaserSensorUi)
- [UpdateModeUiCore](#UpdateModeUiCore)
- [UpdateMotorStateLabel](#UpdateMotorStateLabel)
- [UpdateParamVisibility](#UpdateParamVisibility)
- [UpdatePlayPauseUi](#UpdatePlayPauseUi)
- [UpdatePlayTimeLabel](#UpdatePlayTimeLabel)
- [UpdateStatusLabel](#UpdateStatusLabel)
- [UpdateTaAutoGateHint](#UpdateTaAutoGateHint)
- [Validate](#Validate)
- [ValidateAxisRows](#ValidateAxisRows)
- [ValidateCurrentTables](#ValidateCurrentTables)
- [ValidateCylinderRows](#ValidateCylinderRows)
- [ValidateIoRows](#ValidateIoRows)
- [ValidateRow](#ValidateRow)
- [ValidateWeldHeadRows](#ValidateWeldHeadRows)
- [VisibleSeries](#VisibleSeries)
- [Warn](#Warn)
- [Where](#Where)
- [WireButtons](#WireButtons)
- [WirePlaybackEvents](#WirePlaybackEvents)
- [WireTaInstructionClicks](#WireTaInstructionClicks)
- [WriteCsvTable](#WriteCsvTable)
- [WriteOrClearCsv](#WriteOrClearCsv)
- [WriteTableSourceDirectory](#WriteTableSourceDirectory)

## OnPropertyChanged

> 5 处调用 / 5 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [28]
- `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs` — 行 [215]
- `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` — 行 [31]
- `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs` — 行 [39]
- `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs` — 行 [39]

## OnOperateLevelChanged

> 3 处调用 / 3 个调用方文件

- `UIDesign/MainWindow/FormMain.cs` — 行 [326]
- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [141]
- `UIDesign/TabPage/SystemControlPage.cs` — 行 [181]

## ParseInt

> 3 处调用 / 3 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [511]
- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [432]
- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1258, 1257, 1256, 1252, 1250, 1249, 1248, 1247, 1239, 1238, 1237, 1206, 1198]

## OnMotionStateSwitched

> 2 处调用 / 2 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [77]
- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2720]

## OnWorkflowStateChanged

> 2 处调用 / 2 个调用方文件

- `UIDesign/MainWindow/FormMain.cs` — 行 [239]
- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [523]

## ParseCalibDouble

> 2 处调用 / 2 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1794, 1793, 1792, 434, 393, 392, 391, 390, 389, 388, 387, 386, 385, 384]
- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1255, 1254, 1251, 1246, 1231, 1230, 1228, 1225, 1221, 1218, 1217, 1215, 1214, 1213, 1212, 1210, 1209, 1208, 1205, 1204, 1203, 1202, 1201, 1200, 1199, 1197]

## ParseDouble

> 2 处调用 / 2 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [512, 510, 509, 508, 507, 502, 501, 500, 495, 494, 493, 492, 491, 490, 489, 488, 487, 486]
- `UIDesign/TabPage/FilebackupPage.cs` — 行 [993, 992]

## SaveConfig

> 2 处调用 / 2 个调用方文件

- `UIDesign/SubDialog/DataReviewerDialog/RecordConfigForm.cs` — 行 [95]
- `UIDesign/TabPage/CommSettingPage.cs` — 行 [342]

## SetControlEnabled

> 2 处调用 / 2 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [892, 891, 888, 887, 886, 885, 884, 883, 882, 879, 878, 877, 876, 875, 868, 867, 866]
- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1026, 1025, 1023, 1022, 1021, 1020, 1019, 1018, 1017, 1016, 1015, 1014, 1013, 1012, 1011, 1010, 1009, 1008, 1007, 1006, 1005, 1004]

## TryReadDouble

> 2 处调用 / 2 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [167, 166]
- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2675, 2427, 2397, 2253, 2248, 2248, 2243, 2243, 2235, 2226, 2225, 2221, 2220, 2212, 1282]

## UpdateConnLabel

> 2 处调用 / 2 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [372, 79]
- `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` — 行 [56]

## OnDeviceSwitchClick

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [986]

## OnIlJobParamsChanged

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [378]

## OnIlStateChanged

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [638]

## OnInitializationCompleted

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [542]

## OnLineLaserStateChanged

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1565]

## OnMainDeviceStatusChanged

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1593]

## OnMatUpdated

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [109]

## OnSimulationStopped

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1535]

## OpenAxisEditor

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [598]

## OpenTaAxisEditor

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [610]

## OperateLevelControl

> 1 处调用 / 1 个调用方文件

- `UIDesign/MainWindow/FormMain.cs` — 行 [329, 274]

## ParseAndValidate

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [446]

## ParseDebugDouble

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/CommSettingPage.cs` — 行 [500, 499, 498, 497, 496, 463]

## ParseRecordTime

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [487, 480]

## ParseShort

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [506, 499]

## ParseStep

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [765]

## ParseTarget

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [739]

## ParseUShort

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [484, 483]

## PlaySelected

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [791]

## PopulateComboBoxItems

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [113]

## PostToUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [92, 86]

## PrepareActionRadioBackColor

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [198]

## RadioGroupOf

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1167]

## RadioToGalvoPattern

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1575]

## ReadConfiguredGalvoPattern

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [991]

## ReadDirInput

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [875, 855]

## RebuildChartDatasets

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [906, 542, 321]

## RefreshActionButtonStates

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1598, 1572, 973, 935, 129]

## RefreshActionStates

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1476, 1311, 1046, 1032, 955, 336, 160, 146, 136, 80]

## RefreshDeltaPreview

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [282]

## RefreshDisplay

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [532, 112]

## RefreshFpsSelect

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [466, 449, 265]

## RefreshGalvoStatus

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1958, 1898, 1043]

## RefreshInspectResult

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [135]

## RefreshJobFlow

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [415, 235, 85]

## RefreshJobParams

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [416, 371, 86]

## RefreshJobSelect

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [406, 383, 264]

## RefreshLaMotorStatus

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1959, 1917, 1044]

## RefreshLaserHeadRuntime

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [991]

## RefreshParamCharts

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1194, 460]

## RefreshParamChartsUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [296]

## RefreshRuntime

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2698, 990, 600]

## RefreshTaMotorStatus

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1960, 1936, 638]

## RefreshTemperature

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DeviceMonitorPage.cs` — 行 [45]

## RefreshUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [648, 642, 545, 527, 219, 87, 69, 57]

## ReloadDeltaConfigOnly

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [679]

## ReloadSystemConfig

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1562, 1473]

## RemoveDeltaRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [729]

## ReportAxisResult

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [743, 719]

## RescanFromDirectory

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [731]

## ResetActionBack

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1253, 1230, 1172]

## ResetJogFlag

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [725]

## ResetOtherRadioBacks

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1587, 1500, 1486, 1285, 657]

## ResetTaJogFlag

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2474]

## ResolveAxisGateReason

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1236]

## ResolveInstructionAxisKey

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1244]

## RevertInstructionSelection

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1231]

## RunInstruction

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1588, 1501, 658]

## SaveConfigValues

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs` — 行 [208]

## SaveGalvoPattern

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1474, 995]

## SaveLaserHead

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1984]

## SaveProcessEnable

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1377, 1368, 1359, 1350, 1341]

## ScanDeltaDirectory

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [861, 111]

## Section

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [151, 149, 143]

## SelectFirstNode

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs` — 行 [141]

## SeriesCheckboxes

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1210, 1183]

## SessionLabel

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [734, 569, 563]

## SetConnectIp

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [297, 270]

## SetGalvoPattern

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1581]

## SetGroupBusy

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [972, 955, 934]

## SetIlControlsEnabled

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [81, 76]

## SetPlayBarVisible

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [925, 916, 908, 898]

## SetPlayCaption

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [667, 653, 646, 630]

## SetRowCellValue

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [708]

## SetSimButtonMode

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1766, 1697, 1552, 1547, 1515]

## SetText

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [63]

## SetWeldFlowStep

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [948, 945, 941, 938, 934, 918, 915, 911, 908, 879, 861]

## SetupMergedChart

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [570]

## ShowCorButton

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/UserManagerDialog/LoginForm.cs` — 行 [67, 25]

## ShowGroupOnly

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [320, 261]

## ShowHoverTip

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [672]

## ShowMat

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [132]

## ShowSimErrorButton

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1624, 1618]

## ShowSimErrorDialog

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1605, 1577, 1546, 1511, 1503, 1496]

## ShowSimStopMessage

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1767, 1551]

## ShowStatus

> 1 处调用 / 1 个调用方文件

- `UIDesign/MainWindow/FormMain.cs` — 行 [334]

## ShowTreeNode

> 1 处调用 / 1 个调用方文件

- `UIDesign/MainWindow/FormMain.cs` — 行 [285]

## ShowWeldPreviewFrame

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1260]

## StartActionRefresh

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [205]

## StartManualOperation

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2617, 2545, 2509, 2488, 2460, 2432, 2402, 2355, 2121, 766, 741, 713, 702]

## StartProfilePolling

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1407]

## StartTaJog

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2560, 2559]

## StepLaMotor

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2388, 2380]

## StopJog

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [822, 814]

## StopProfilePolling

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1317]

## StopSimOnWeldComplete

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1582]

## StopSimulationFlows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1722, 1704, 1466]

## StopTaJog

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2564, 2563, 2562, 2561]

## SubscribeLineLaserEvents

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1484]

## SyncFromHardwareCore

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [92]

## SyncSelectedJobFromDevice

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [370, 167]

## SyncSimParamsToController

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1474, 1431]

## TaStep

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2531, 2523]

## ToPlaybackRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [652]

## ToggleLineLaserConnection

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1060]

## TotalAdjustCount

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [952]

## TryGetAxisPositionMm

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2548, 769]

## TryNumber

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [471, 469, 459, 453, 451, 449, 447, 445, 440, 438, 436, 434, 432, 430, 428]

## TryParseHex

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1145]

## TryPassCommAction

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/CommSettingPage.cs` — 行 [275, 241]

## TryPassPageAction

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [192]

## TryReadInt

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2257, 2239, 2231, 2230, 2216, 1290]

## TryTaOperation

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2594, 2579, 2475, 2462]

## TryTraceOperation

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [831, 802, 726, 704]

## UiMessage

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [800, 771, 764, 758, 737]

## UnsubscribeLineLaserEvents

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2996, 1716, 1703, 1542, 1465]

## UnwirePlaybackEvents

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [95]

## UpdateApplyButtonsState

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [619, 467, 450, 436, 407, 384, 370, 269]

## UpdateChartUI

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [375]

## UpdateConnectionUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [966, 307, 285, 227]

## UpdateConnectionUiCore

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [90]

## UpdateCurveInfo

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2649, 2017]

## UpdateDeltaStatusHint

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [710, 259, 232, 212, 194]

## UpdateDeltaStatusText

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [283]

## UpdateFpsDropdownState

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [618, 579, 312, 268]

## UpdateJobButtonsState

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [174, 161]

## UpdateJointTypeLabel

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [269]

## UpdateLaserSensorUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [609, 310, 302, 261]

## UpdateModeUiCore

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [91]

## UpdateMotorStateLabel

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2016]

## UpdateParamVisibility

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs` — 行 [143]

## UpdatePlayPauseUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [539]

## UpdatePlayTimeLabel

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [722]

## UpdateStatusLabel

> 1 处调用 / 1 个调用方文件

- `UIDesign/MainWindow/FormMain.cs` — 行 [242, 81]

## UpdateTaAutoGateHint

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [872]

## Validate

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [332]

## ValidateAxisRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [903]

## ValidateCurrentTables

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [622]

## ValidateCylinderRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [911]

## ValidateIoRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [907]

## ValidateRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` — 行 [232, 201]

## ValidateWeldHeadRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [916]

## VisibleSeries

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [746, 694]

## Warn

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2653, 2574, 2542, 2507, 2429, 2399, 2311, 2297, 2266, 2259, 2255, 2251, 2246, 2241, 2237, 2233, 2228, 2223, 2218, 2214, 2117, 1818, 931, 926, 797, 621]

## Where

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1156, 1146, 1136, 1126, 1116, 1082, 1079, 1064, 1041, 1040, 1012, 1008, 1007, 994, 972, 971]

## WireButtons

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [73]

## WirePlaybackEvents

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [538]

## WireTaInstructionClicks

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [197]

## WriteCsvTable

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1243, 883]

## WriteOrClearCsv

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1219, 1217, 1215]

## WriteTableSourceDirectory

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [637]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
