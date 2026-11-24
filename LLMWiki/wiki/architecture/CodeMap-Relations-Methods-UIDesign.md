---
title: CodeMap-Relations-Methods-UIDesign — 代码地图·方法级影响面·UIDesign（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations-Methods-UIDesign — 方法级影响面（低置信 · 调用方在 UIDesign · 名首字母 A-M）

> **一句话**：**调用方位于 `UIDesign` 模块**的被调方法 → 调用点清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **⚠️ 低置信**：纯标识符调用（`Log(...)`），接收者类型未知 ⇒ **同名不同类会误连**。
> 用法：查「改这个方法名会影响谁」的**候选集**，⛔ 结论仍须 Grep 确认（Step 2.5）。
> 类型级影响面（高置信）见 [[architecture/CodeMap-Relations]]。

| 项 | 值 |
|---|---|
| 被调方法数 | 242 |
| 调用点数 | 259 |

## 章节导航

- [AcceptRefreshSwitchOn](#AcceptRefreshSwitchOn)
- [AddDeltaRow](#AddDeltaRow)
- [AddJobRow](#AddJobRow)
- [AddParamRow](#AddParamRow)
- [AddSeamWidthLimitLines](#AddSeamWidthLimitLines)
- [AddSeries](#AddSeries)
- [AdvanceWeldFlowByCommand](#AdvanceWeldFlowByCommand)
- [AfterInitializeUI](#AfterInitializeUI)
- [AppendLog](#AppendLog)
- [AppendNewPoints](#AppendNewPoints)
- [ApplyActionBack](#ApplyActionBack)
- [ApplyActionRunning](#ApplyActionRunning)
- [ApplyAdaptUiToMemory](#ApplyAdaptUiToMemory)
- [ApplyAlignPermission](#ApplyAlignPermission)
- [ApplyAxisReadout](#ApplyAxisReadout)
- [ApplyAxisReadouts](#ApplyAxisReadouts)
- [ApplyDefaultCommandModes](#ApplyDefaultCommandModes)
- [ApplyDeltaView](#ApplyDeltaView)
- [ApplyDeviceStatus](#ApplyDeviceStatus)
- [ApplyEnableState](#ApplyEnableState)
- [ApplyGalvo](#ApplyGalvo)
- [ApplyGalvoParamsToHead](#ApplyGalvoParamsToHead)
- [ApplyGalvoPatternSelection](#ApplyGalvoPatternSelection)
- [ApplyLaMotor](#ApplyLaMotor)
- [ApplyLaToConfig](#ApplyLaToConfig)
- [ApplyLaserHeadOnForm](#ApplyLaserHeadOnForm)
- [ApplyLineColor](#ApplyLineColor)
- [ApplyPermissionGate](#ApplyPermissionGate)
- [ApplyProfileSnapshot](#ApplyProfileSnapshot)
- [ApplyRefreshSnapshot](#ApplyRefreshSnapshot)
- [ApplyRefreshSwitchGate](#ApplyRefreshSwitchGate)
- [ApplySelection](#ApplySelection)
- [ApplySeriesSingleSelection](#ApplySeriesSingleSelection)
- [ApplyTaToConfig](#ApplyTaToConfig)
- [ApplyTaZeroPoseStage](#ApplyTaZeroPoseStage)
- [ApplyTemperature](#ApplyTemperature)
- [ApplyWeldFlowDeviceStatus](#ApplyWeldFlowDeviceStatus)
- [ApplyWeldFlowWeldStatus](#ApplyWeldFlowWeldStatus)
- [ApplyYtCalibToConfig](#ApplyYtCalibToConfig)
- [AxisHeaders](#AxisHeaders)
- [AxisReadoutSignature](#AxisReadoutSignature)
- [AxisReadoutSignatureChanged](#AxisReadoutSignatureChanged)
- [BindDeltaView](#BindDeltaView)
- [BindEvents](#BindEvents)
- [BuildAlarmText](#BuildAlarmText)
- [BuildAxisCsvRows](#BuildAxisCsvRows)
- [BuildCurrentViewRows](#BuildCurrentViewRows)
- [BuildCylinderCsvRows](#BuildCylinderCsvRows)
- [BuildDeviceTooltipText](#BuildDeviceTooltipText)
- [BuildGroup](#BuildGroup)
- [BuildHintSuffix](#BuildHintSuffix)
- [BuildIoCsvRows](#BuildIoCsvRows)
- [BuildIoPreviewRow](#BuildIoPreviewRow)
- [BuildLaActionDetail](#BuildLaActionDetail)
- [BuildLayout](#BuildLayout)
- [BuildNodeDisplayText](#BuildNodeDisplayText)
- [BuildOutcome](#BuildOutcome)
- [BuildParamInfo](#BuildParamInfo)
- [BuildRowSpecs](#BuildRowSpecs)
- [BuildSummaryText](#BuildSummaryText)
- [BuildTaActionDetail](#BuildTaActionDetail)
- [BuildYActionDetail](#BuildYActionDetail)
- [CheckBool](#CheckBool)
- [CheckDouble](#CheckDouble)
- [CheckHex](#CheckHex)
- [CheckIoReference](#CheckIoReference)
- [CheckRange](#CheckRange)
- [CheckUShort](#CheckUShort)
- [CleanupSimError](#CleanupSimError)
- [ClearAll](#ClearAll)
- [ClearDirty](#ClearDirty)
- [ClearGalvoPatternSelection](#ClearGalvoPatternSelection)
- [ClearHoverTip](#ClearHoverTip)
- [ClearJobFlow](#ClearJobFlow)
- [ClearPlaybackRows](#ClearPlaybackRows)
- [ClearXmlAllInfo](#ClearXmlAllInfo)
- [CollectAxisReadout](#CollectAxisReadout)
- [CollectAxisReadouts](#CollectAxisReadouts)
- [CollectGalvo](#CollectGalvo)
- [CollectLaMotor](#CollectLaMotor)
- [CollectParamFromForm](#CollectParamFromForm)
- [CollectRefreshSnapshot](#CollectRefreshSnapshot)
- [CollectSelectedRows](#CollectSelectedRows)
- [CollectTemperature](#CollectTemperature)
- [ColumnHeaders](#ColumnHeaders)
- [Commit](#Commit)
- [ConfigSelect](#ConfigSelect)
- [ConfirmInstruction](#ConfirmInstruction)
- [CreateAxisColumns](#CreateAxisColumns)
- [CsvCell](#CsvCell)
- [CsvEscape](#CsvEscape)
- [CurrentGalvoPattern](#CurrentGalvoPattern)
- [CylinderHeaders](#CylinderHeaders)
- [Datashow](#Datashow)
- [DiagLog](#DiagLog)
- [DisposeComponents](#DisposeComponents)
- [DisposePreviewFrame](#DisposePreviewFrame)
- [DoLaAuto](#DoLaAuto)
- [DoLaDefaultFocus](#DoLaDefaultFocus)
- [DoLaPose1](#DoLaPose1)
- [DoLaSpot1](#DoLaSpot1)
- [DoLaSpot2](#DoLaSpot2)
- [DoTaAuto](#DoTaAuto)
- [DoTaBreak](#DoTaBreak)
- [DoTaPose1](#DoTaPose1)
- [DoTaPose2](#DoTaPose2)
- [DoTaRetract](#DoTaRetract)
- [DoTaZeroPose](#DoTaZeroPose)
- [EditorRow](#EditorRow)
- [EffectiveSwingFrequency](#EffectiveSwingFrequency)
- [EnableBackColorPaint](#EnableBackColorPaint)
- [EnsureAdminForWrite](#EnsureAdminForWrite)
- [EnsureTaParamFilled](#EnsureTaParamFilled)
- [EnsureTabLoaded](#EnsureTabLoaded)
- [EstimateBoxWidth](#EstimateBoxWidth)
- [ExecuteLaAction](#ExecuteLaAction)
- [ExecuteSurfaceRender](#ExecuteSurfaceRender)
- [ExecuteTaAction](#ExecuteTaAction)
- [ExecuteYAction](#ExecuteYAction)
- [ExportCurrentViewCsv](#ExportCurrentViewCsv)
- [FieldRow](#FieldRow)
- [FillAxisRuntime](#FillAxisRuntime)
- [FillPage](#FillPage)
- [FindNearestPoint](#FindNearestPoint)
- [FinishManualOperation](#FinishManualOperation)
- [FixedJog](#FixedJog)
- [FixedStep](#FixedStep)
- [FormatCellValue](#FormatCellValue)
- [FormatPlayTime](#FormatPlayTime)
- [FormatRange](#FormatRange)
- [FormatSpeed](#FormatSpeed)
- [FrequencyToIndex](#FrequencyToIndex)
- [GalvoPatternText](#GalvoPatternText)
- [GalvoPatternToRadio](#GalvoPatternToRadio)
- [GateRefreshSwitch](#GateRefreshSwitch)
- [GetCellText](#GetCellText)
- [GetConfig](#GetConfig)
- [GetCurrentJobDisplayKeys](#GetCurrentJobDisplayKeys)
- [GetFixedRow](#GetFixedRow)
- [GetParamGroup](#GetParamGroup)
- [GetPlayRange](#GetPlayRange)
- [GetPlotWindow](#GetPlotWindow)
- [GetTaRow](#GetTaRow)
- [HandleAxisReject](#HandleAxisReject)
- [HideTreeNode](#HideTreeNode)
- [IndexToFrequency](#IndexToFrequency)
- [InitCalibUi](#InitCalibUi)
- [InitCommandTooltips](#InitCommandTooltips)
- [InitConfigListColumns](#InitConfigListColumns)
- [InitDeltaConfigPanel](#InitDeltaConfigPanel)
- [InitDeltaTableMenu](#InitDeltaTableMenu)
- [InitDeviceSwitchButtons](#InitDeviceSwitchButtons)
- [InitIlModule](#InitIlModule)
- [InitPCLDir](#InitPCLDir)
- [InitPlaybackTable](#InitPlaybackTable)
- [InitPlaybackUi](#InitPlaybackUi)
- [InitPropertyGridTable](#InitPropertyGridTable)
- [InitResultTable](#InitResultTable)
- [InitRsiDebugPanel](#InitRsiDebugPanel)
- [InitSeriesGroups](#InitSeriesGroups)
- [InitTableColumns](#InitTableColumns)
- [InitTables](#InitTables)
- [InitWeldFlowSteps](#InitWeldFlowSteps)
- [InitializeComboBoxItems](#InitializeComboBoxItems)
- [InitializeConnectionBar](#InitializeConnectionBar)
- [InstructionWorker](#InstructionWorker)
- [IoHeaders](#IoHeaders)
- [IsDisplayParam](#IsDisplayParam)
- [IsDocumentSource](#IsDocumentSource)
- [IsGroupBusy](#IsGroupBusy)
- [IsInputType](#IsInputType)
- [IsLaZoneReady](#IsLaZoneReady)
- [IsLineLaserRunning](#IsLineLaserRunning)
- [IsMotionReady](#IsMotionReady)
- [IsMotionZoneReady](#IsMotionZoneReady)
- [IsOutputType](#IsOutputType)
- [IsReadyForQuery](#IsReadyForQuery)
- [IsRefreshPageVisible](#IsRefreshPageVisible)
- [IsTaAxisLoaded](#IsTaAxisLoaded)
- [IsTraceAxis](#IsTraceAxis)
- [IsWorkflowRunning](#IsWorkflowRunning)
- [LaserWeldHeadWorkflowInstance](#LaserWeldHeadWorkflowInstance)
- [LayoutDeviceSwitchAreas](#LayoutDeviceSwitchAreas)
- [LoadAlgoConfigOnForm](#LoadAlgoConfigOnForm)
- [LoadAlgoThreshOnForm](#LoadAlgoThreshOnForm)
- [LoadAlignThresholds](#LoadAlignThresholds)
- [LoadAutoParam](#LoadAutoParam)
- [LoadAxisPreview](#LoadAxisPreview)
- [LoadAxisRows](#LoadAxisRows)
- [LoadCameraParams](#LoadCameraParams)
- [LoadConfig](#LoadConfig)
- [LoadConfigList](#LoadConfigList)
- [LoadConfigValues](#LoadConfigValues)
- [LoadCylinderPreview](#LoadCylinderPreview)
- [LoadDevices](#LoadDevices)
- [LoadDocument](#LoadDocument)
- [LoadFileList](#LoadFileList)
- [LoadFlowSwitchOnForm](#LoadFlowSwitchOnForm)
- [LoadFromModel](#LoadFromModel)
- [LoadGalvoActionUi](#LoadGalvoActionUi)
- [LoadGalvoShapeToInputs](#LoadGalvoShapeToInputs)
- [LoadIlParamsToGrid](#LoadIlParamsToGrid)
- [LoadIoPreview](#LoadIoPreview)
- [LoadLaParamUi](#LoadLaParamUi)
- [LoadLaserCalibOnForm](#LoadLaserCalibOnForm)
- [LoadNavAndPages](#LoadNavAndPages)
- [LoadNodeToTable](#LoadNodeToTable)
- [LoadOpticsFromConfig](#LoadOpticsFromConfig)
- [LoadParamOnForm](#LoadParamOnForm)
- [LoadParams](#LoadParams)
- [LoadPlaybackRange](#LoadPlaybackRange)
- [LoadPointCloud](#LoadPointCloud)
- [LoadProcessEnableOnForm](#LoadProcessEnableOnForm)
- [LoadProductRecords](#LoadProductRecords)
- [LoadProjectXmlRows](#LoadProjectXmlRows)
- [LoadSensors](#LoadSensors)
- [LoadTaAxisRow](#LoadTaAxisRow)
- [LoadTaParamUi](#LoadTaParamUi)
- [LoadTabsLazy](#LoadTabsLazy)
- [LoadTabsWithItems](#LoadTabsWithItems)
- [LoadTempFromConfig](#LoadTempFromConfig)
- [LoadTimeoutOnForm](#LoadTimeoutOnForm)
- [LoadUserList](#LoadUserList)
- [LoadValues](#LoadValues)
- [LoadXmlToTree](#LoadXmlToTree)
- [LoadYtCalibUi](#LoadYtCalibUi)
- [LockContourAxisOnce](#LockContourAxisOnce)
- [Log](#Log)
- [LogAppend](#LogAppend)
- [LogPageWarning](#LogPageWarning)
- [LogSimStopSummary](#LogSimStopSummary)
- [MakeCameraRow](#MakeCameraRow)
- [MakeItem](#MakeItem)
- [MakeLight](#MakeLight)
- [MakeLightGray](#MakeLightGray)
- [MarkCurrentViewDirty](#MarkCurrentViewDirty)
- [MarkInstructionRejected](#MarkInstructionRejected)
- [MergeView](#MergeView)
- [MotionControlWorkflowInstance](#MotionControlWorkflowInstance)
- [MoveAxisHome](#MoveAxisHome)
- [MoveAxisToTarget](#MoveAxisToTarget)
- [btnAddNewConfig_Click](#btnAddNewConfig_Click)

## InitTableColumns

> 8 处调用 / 8 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [180]
- `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs` — 行 [33]
- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [40]
- `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` — 行 [48]
- `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs` — 行 [56]
- `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs` — 行 [57]
- `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs` — 行 [24]
- `UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs` — 行 [26]

## DisposeComponents

> 6 处调用 / 6 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [216]
- `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs` — 行 [96]
- `UIDesign/TabPage/CommSettingPage.cs` — 行 [89]
- `UIDesign/TabPage/FilebackupPage.cs` — 行 [89]
- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [84]
- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2987]

## AddSeries

> 2 处调用 / 2 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [569, 563]
- `UIDesign/ControlPage/MainPage.cs` — 行 [490, 488, 487, 486, 482]

## AfterInitializeUI

> 2 处调用 / 2 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [1041]
- `UIDesign/ControlPage/MainPage.cs` — 行 [613]

## LoadConfig

> 2 处调用 / 2 个调用方文件

- `UIDesign/SubDialog/DataReviewerDialog/RecordConfigForm.cs` — 行 [24]
- `UIDesign/TabPage/CommSettingPage.cs` — 行 [61]

## LoadProcessEnableOnForm

> 2 处调用 / 2 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [545, 335, 203]
- `UIDesign/TabPage/SystemControlPage.cs` — 行 [112]

## Log

> 2 处调用 / 2 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1100, 845, 712, 646, 563, 559, 555]
- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2867, 2752, 2700, 2660, 2651, 2600, 2596, 2586, 2582, 2481, 2478, 2345, 2326, 2320, 1975, 1961, 1938, 1919, 1900, 1084, 1080, 987, 981, 837, 833, 809, 805, 732, 729, 636, 170]

## AcceptRefreshSwitchOn

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2690, 1928, 1909, 1890]

## AddDeltaRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [728]

## AddJobRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` — 行 [118, 117, 116, 115, 114]

## AddParamRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs` — 行 [182, 181, 177, 176, 172, 171, 167, 166, 162, 161, 157, 156]

## AddSeamWidthLimitLines

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [484]

## AdvanceWeldFlowByCommand

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [752]

## AppendLog

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/CommSettingPage.cs` — 行 [511, 507, 503, 492, 478, 473, 468, 459, 333, 329, 304, 298, 286, 280, 266, 260, 255, 250, 245, 224, 219, 204, 195, 136, 107]

## AppendNewPoints

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [287, 286, 285, 284]

## ApplyActionBack

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1310, 1286, 1268, 134, 133]

## ApplyActionRunning

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1254, 132]

## ApplyAdaptUiToMemory

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [462, 413]

## ApplyAlignPermission

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [144, 77]

## ApplyAxisReadout

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2955, 471]

## ApplyAxisReadouts

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2922, 2912, 2901]

## ApplyDefaultCommandModes

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [204]

## ApplyDeltaView

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [284, 155, 144]

## ApplyDeviceStatus

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [663, 660, 184]

## ApplyEnableState

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/CommSettingPage.cs` — 行 [223, 182, 159]

## ApplyGalvo

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2896, 2066]

## ApplyGalvoParamsToHead

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1021, 572, 558]

## ApplyGalvoPatternSelection

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [948]

## ApplyLaMotor

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2897, 2144]

## ApplyLaToConfig

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [571, 557]

## ApplyLaserHeadOnForm

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1970]

## ApplyLineColor

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1357, 1346]

## ApplyPermissionGate

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [184, 117]

## ApplyProfileSnapshot

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [267]

## ApplyRefreshSnapshot

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2870]

## ApplyRefreshSwitchGate

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2764, 2750, 2736, 2723]

## ApplySelection

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [996, 988, 980]

## ApplySeriesSingleSelection

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [165]

## ApplyTaToConfig

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [570, 556]

## ApplyTaZeroPoseStage

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [161]

## ApplyTemperature

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DeviceMonitorPage.cs` — 行 [39]

## ApplyWeldFlowDeviceStatus

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [729]

## ApplyWeldFlowWeldStatus

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [896]

## ApplyYtCalibToConfig

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [573, 559]

## AxisHeaders

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1344, 1215]

## AxisReadoutSignature

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2974]

## AxisReadoutSignatureChanged

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2956]

## BindDeltaView

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1567, 848, 813, 681, 171]

## BindEvents

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [107]

## BuildAlarmText

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [701, 695]

## BuildAxisCsvRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1365, 1216]

## BuildCurrentViewRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [882]

## BuildCylinderCsvRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1353, 1220]

## BuildDeviceTooltipText

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1133, 987]

## BuildGroup

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [248, 243, 237, 228, 224]

## BuildHintSuffix

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [672]

## BuildIoCsvRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1352, 1218]

## BuildIoPreviewRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [367, 363]

## BuildLaActionDetail

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1588]

## BuildLayout

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [112]

## BuildNodeDisplayText

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs` — 行 [82]

## BuildOutcome

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2464, 706]

## BuildParamInfo

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [453]

## BuildRowSpecs

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [111]

## BuildSummaryText

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [909]

## BuildTaActionDetail

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1501]

## BuildYActionDetail

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [658]

## CheckBool

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1017, 975]

## CheckDouble

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [989, 988, 987, 986, 985, 984, 982, 981, 980, 979, 978, 977, 976]

## CheckHex

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1074, 1073, 1072, 1071]

## CheckIoReference

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1047, 1046, 1045, 1044, 1043]

## CheckRange

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` — 行 [171, 168, 159, 154]

## CheckUShort

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1016, 1015, 1014, 990, 983, 974, 973]

## CleanupSimError

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1458]

## ClearAll

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs` — 行 [267]

## ClearDirty

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1565, 676, 276]

## ClearGalvoPatternSelection

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [988]

## ClearHoverTip

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [669]

## ClearJobFlow

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [91]

## ClearPlaybackRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [628, 96]

## ClearXmlAllInfo

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs` — 行 [131]

## CollectAxisReadout

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [516, 505, 471]

## CollectAxisReadouts

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2885, 2884, 2880]

## CollectGalvo

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2878, 2066]

## CollectLaMotor

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2879, 2144]

## CollectParamFromForm

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [473, 409]

## CollectRefreshSnapshot

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2863]

## CollectSelectedRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [797]

## CollectTemperature

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DeviceMonitorPage.cs` — 行 [39]

## ColumnHeaders

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [883]

## Commit

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [338]

## ConfigSelect

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [255]

## ConfirmInstruction

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1227]

## CreateAxisColumns

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [242, 235]

## CsvCell

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [593, 592, 591, 590, 589, 588, 587, 586, 566, 565, 564, 563, 562, 561, 560, 540, 539, 538, 537, 536, 535, 534, 533, 532, 531, 530, 529, 528, 527, 526, 525, 524, 523, 522]

## CsvEscape

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1378]

## CurrentGalvoPattern

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1022, 963, 585, 524]

## CylinderHeaders

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1338, 1219]

## Datashow

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [607]

## DiagLog

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [394]

## DisposePreviewFrame

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1305, 1281, 1277, 1256, 1245]

## DoLaAuto

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1620]

## DoLaDefaultFocus

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1624]

## DoLaPose1

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1623]

## DoLaSpot1

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1621]

## DoLaSpot2

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1622]

## DoTaAuto

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1556]

## DoTaBreak

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1557]

## DoTaPose1

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1559]

## DoTaPose2

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1560]

## DoTaRetract

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1558]

## DoTaZeroPose

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1561]

## EditorRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [154, 124]

## EffectiveSwingFrequency

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/ParamContolDialog/AutoParamForm.cs` — 行 [192]

## EnableBackColorPaint

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1090]

## EnsureAdminForWrite

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2641, 2616, 2570, 2536, 2503, 2486, 2459, 2426, 2396, 2354, 2114, 1983, 1969, 1472, 616, 154]

## EnsureTaParamFilled

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [202, 159]

## EnsureTabLoaded

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/NavPage.cs` — 行 [127, 48, 28]

## EstimateBoxWidth

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [289]

## ExecuteLaAction

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1589]

## ExecuteSurfaceRender

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs` — 行 [199]

## ExecuteTaAction

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1502]

## ExecuteYAction

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [659]

## ExportCurrentViewCsv

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [730]

## FieldRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [158, 157, 153, 152, 150, 148, 147, 146, 145, 144, 139, 138, 137, 136, 135, 131, 130, 129, 128, 127, 126, 125, 123, 122, 121]

## FillAxisRuntime

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2940, 2933, 2185, 442, 398]

## FillPage

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [1035, 448]

## FindNearestPoint

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [666]

## FinishManualOperation

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [951]

## FixedJog

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [787, 782]

## FixedStep

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [757, 752]

## FormatCellValue

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [470, 337]

## FormatPlayTime

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [876, 876]

## FormatRange

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` — 行 [144, 127]

## FormatSpeed

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [737]

## FrequencyToIndex

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1395]

## GalvoPatternText

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1475, 1031]

## GalvoPatternToRadio

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [999]

## GateRefreshSwitch

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1832, 1831, 1830, 1829]

## GetCellText

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [496, 495, 494, 492, 479]

## GetConfig

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2302, 2028, 423, 379]

## GetCurrentJobDisplayKeys

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [260]

## GetFixedRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [763, 737]

## GetParamGroup

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [342]

## GetPlayRange

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [574, 565, 556]

## GetPlotWindow

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [684]

## GetTaRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2853, 2839, 2537, 2504]

## HandleAxisReject

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [733, 715]

## HideTreeNode

> 1 处调用 / 1 个调用方文件

- `UIDesign/MainWindow/FormMain.cs` — 行 [289]

## IndexToFrequency

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1441]

## InitCalibUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [69]

## InitCommandTooltips

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [196]

## InitConfigListColumns

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [195]

## InitDeltaConfigPanel

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [81]

## InitDeltaTableMenu

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [135]

## InitDeviceSwitchButtons

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [156]

## InitIlModule

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [50]

## InitPCLDir

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [1059, 654, 651, 386]

## InitPlaybackTable

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [71]

## InitPlaybackUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [72]

## InitPropertyGridTable

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs` — 行 [60]

## InitResultTable

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [31]

## InitRsiDebugPanel

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/CommSettingPage.cs` — 行 [57]

## InitSeriesGroups

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [185]

## InitTables

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [106]

## InitWeldFlowSteps

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [168]

## InitializeComboBoxItems

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs` — 行 [24]

## InitializeConnectionBar

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [67]

## InstructionWorker

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1257]

## IoHeaders

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1337, 1217]

## IsDisplayParam

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [263]

## IsDocumentSource

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [306, 166]

## IsGroupBusy

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2572, 1002, 1001, 1000, 999, 924, 795]

## IsInputType

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1306, 1032, 1011]

## IsLaZoneReady

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1827]

## IsLineLaserRunning

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1118]

## IsMotionReady

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2825, 460]

## IsMotionZoneReady

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1881, 1826]

## IsOutputType

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1011]

## IsReadyForQuery

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [1040, 383]

## IsRefreshPageVisible

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2828]

## IsTaAxisLoaded

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1881, 1828]

## IsTraceAxis

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [383]

## IsWorkflowRunning

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [550, 127]

## LaserWeldHeadWorkflowInstance

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1459, 1454, 1449, 1444, 1439, 1345, 857, 211, 42]

## LayoutDeviceSwitchAreas

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [1016, 1008, 572]

## LoadAlgoConfigOnForm

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [334, 201]

## LoadAlgoThreshOnForm

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1182, 110]

## LoadAlignThresholds

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [70]

## LoadAutoParam

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [354, 200]

## LoadAxisPreview

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [313]

## LoadAxisRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1087, 108]

## LoadCameraParams

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [346, 301]

## LoadConfigList

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [332, 326, 309, 287, 199]

## LoadConfigValues

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs` — 行 [25]

## LoadCylinderPreview

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [315]

## LoadDevices

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MonitorCamDialog/MonitorCamScanForm.cs` — 行 [64]

## LoadDocument

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs` — 行 [297, 187, 184, 181, 178, 175]

## LoadFileList

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/DataReviewerDialog/FileTraceForm.cs` — 行 [183, 138, 41]

## LoadFlowSwitchOnForm

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1807, 451]

## LoadFromModel

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [114]

## LoadGalvoActionUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1808, 541]

## LoadGalvoShapeToInputs

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1583, 949]

## LoadIlParamsToGrid

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 [268, 248, 92]

## LoadIoPreview

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [314]

## LoadLaParamUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1809, 588, 542]

## LoadLaserCalibOnForm

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1183]

## LoadNavAndPages

> 1 处调用 / 1 个调用方文件

- `UIDesign/MainWindow/FormMain.cs` — 行 [73]

## LoadNodeToTable

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs` — 行 [235, 157]

## LoadOpticsFromConfig

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1972, 1955, 115]

## LoadParamOnForm

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [476, 452, 355, 333, 325]

## LoadParams

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` — 行 [209, 57]

## LoadPlaybackRange

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/MonitorCamPage.cs` — 行 [575, 566, 557]

## LoadPointCloud

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs` — 行 [345, 158]

## LoadProductRecords

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [426]

## LoadProjectXmlRows

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [1566, 680, 309, 168]

## LoadSensors

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs` — 行 [63]

## LoadTaAxisRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [2939, 2921, 2900, 2852, 2838, 2184, 109]

## LoadTaParamUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1819, 1810, 589, 543]

## LoadTabsLazy

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/NavPage.cs` — 行 [147]

## LoadTabsWithItems

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/NavPage.cs` — 行 [97]

## LoadTempFromConfig

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1956, 116]

## LoadTimeoutOnForm

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1184, 111]

## LoadUserList

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/UserManagerDialog/UserEditForm.cs` — 行 [119, 111, 30]

## LoadValues

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` — 行 [113]

## LoadXmlToTree

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/CommConfigDialog/FileEditorForm.cs` — 行 [138, 90]

## LoadYtCalibUi

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1811, 590, 544]

## LockContourAxisOnce

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [367]

## LogAppend

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/MainPage.cs` — 行 [602]

## LogPageWarning

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 [244, 236, 230]

## LogSimStopSummary

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [1768, 1555]

## MakeCameraRow

> 1 处调用 / 1 个调用方文件

- `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` — 行 [111, 110, 109]

## MakeItem

> 1 处调用 / 1 个调用方文件

- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 [250, 246, 245, 241, 240, 239, 235, 234, 233, 232, 231, 230, 226]

## MakeLight

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [551, 550, 549, 548, 547]

## MakeLightGray

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/SystemControlPage.cs` — 行 [537, 536, 535, 534, 533, 467, 466, 465, 464, 463]

## MarkCurrentViewDirty

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [847, 812, 709]

## MarkInstructionRejected

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1248, 1239]

## MergeView

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/FilebackupPage.cs` — 行 [917, 912, 908, 904]

## MotionControlWorkflowInstance

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [1673, 1433, 1425, 1419, 1413, 1407, 1401, 1344, 856, 730, 712, 212, 210, 120, 61, 43, 41]

## MoveAxisHome

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [700]

## MoveAxisToTarget

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [694]

## btnAddNewConfig_Click

> 1 处调用 / 1 个调用方文件

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 [286]

## 相关页面

- [[architecture/CodeMap-Relations]]
- [[architecture/CodeMap]]
