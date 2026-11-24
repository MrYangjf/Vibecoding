---
title: CodeMap-Relations — 代码地图·关系层·类型级影响面（机器生成）
date: 2026-11-18
updated: 2026-11-18
tags: [代码地图, 依赖关系, 影响面, 机器生成]
status: accepted
---

# CodeMap-Relations — 类型级影响面（高置信）

> **一句话**：被引用**类型** → 调用方文件清单；⛔ 本页由 `tools/codemap_build.py` 生成，⛔ 禁手工编辑。
> **置信度**：高置信 = 接收者就是该类型实例（`X.Method(...)`）⇒ 改该类型必影响此处。
> **⚠️ 边界**：同名不同类会误连 ⇒ **结论仍以 Step 0.7 / 2.5 的 Grep 为准**（见 [[rules/KR-009-Grep-Default]]），本页只用于**缩小搜索范围**。
> **低置信方法级影响面**（纯标识符调用）见下方「方法级影响面分片」清单。
> **⚠️ 官方 L3 的坑**：coderepomap 官方 C# 解析器只发 `inherits`/`implements`（零方法调用点），调用边由本仓库自研补齐 —— 见 [[lessons/RepomapCSharpCallEdgeGap]]。

## 统计

| 项 | 值 |
|---|---|
| 高置信调用边 | 637 |
| 被引用类型数 | 47 |
| 继承 / 实现边 | 113 |

## 一、被引用类型 → 调用方

> **怎么用**：改某类型前，先在此查「谁引用它」→ 得到候选文件 → 再用 Grep 确认（Step 2.5）。

### GlobalCommData（263 处调用 / 63 个调用方文件）

- `Comm/Communication/Abstractions/CommChannelBase.cs` — 行 61
- `Comm/Communication/CommunicationManager.cs` — 行 347、559、567、705、720、789、798、804、843、851、902、939、950
- `Comm/Communication/Implementations/EthernetXmlComm.cs` — 行 253、302、389
- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 340、365、411、430、436、500、580、651、694
- `Comm/SystemComm/PermissionLevel.cs` — 行 64
- `ConfigFileControl/Implementations/ConfigChangeLogger.cs` — 行 129
- `EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs` — 行 385
- `EmguALG/Manager/AlgorithmManager.cs` — 行 278
- `FileOperate/ConfigBackupHelper.cs` — 行 46、68、73、93、98
- `FileOperate/ConfigSelfHeal.cs` — 行 38
- `FileOperate/XdocumentReaderWriter.cs` — 行 144、159、174、194、260
- `LineLaserCam/ILineLaser/LineLaserCameraBase.cs` — 行 116
- `LineLaserCam/LineLaserConfig.cs` — 行 98
- `LineLaserCam/LineLaserManager.cs` — 行 308
- `MainDeviceControl/DeviceControlWork.cs` — 行 599、1159、1455、1468、1472、1487、2516、3680
- `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` — 行 204
- `MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs` — 行 265
- `MainDeviceControl/DeviceStatusWork.cs` — 行 122
- `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` — 行 462
- `MonitorCam/HikCam/HikCam.cs` — 行 141、157、167、181、192、200、244、251、269、273、296、300、321、352、369、377、383、415、444、452、461、479、496、503、527、532、538、554、558、577、580、585、605、608、613、689、715、750、760、777
- `MonitorCam/MonitorCamManager.cs` — 行 201、338、388、481、620
- `MotionControl/AxisRegistry.cs` — 行 44
- `MotionControl/CylinderRegistry.cs` — 行 43
- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 198、203、212、221、229、238、250、261、311、544、630、684、757、762、876
- `MotionControl/DeltaEtherCAT/DeltaInputIO.cs` — 行 74
- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 174
- `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs` — 行 63
- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 450
- `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs` — 行 68
- `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` — 行 68
- `MotionControl/DeltaEtherCAT/MotionConfigImporter.cs` — 行 30
- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 97、138、145、169、185、191、203、226、230、271、337、459
- `MotionControl/IMotion/Cylinder.cs` — 行 139、147
- `MotionControl/IMotion/MontionAxis.cs` — 行 233、243、253、261
- `MotionControl/IORegistry.cs` — 行 48
- `MotionControl/MontionManager.cs` — 行 1087、1820、1826、1832
- `MotionControl/MoveControlData.cs` — 行 40
- `MotionControl/WeldHeadSlaveDevice.cs` — 行 79
- `PCLOperate/Render/RenderConfig.cs` — 行 36
- `ProductFileControl/Abstractions/ProductRecordBase.cs` — 行 146
- `ProductFileControl/ProductFileRecordManager.cs` — 行 22
- `ProductFileControl/Records/SeamTraceYRecord.cs` — 行 79、104、149、222
- `ProductFileControl/Records/WeldResultRecord.cs` — 行 24
- `SQLiteDBControl/Helpers/ProductDatabaseHelper.cs` — 行 144
- `UIDesign/ControlPage/DataReviewerPage.cs` — 行 405、467
- `UIDesign/ControlPage/MainPage.cs` — 行 200
- `UIDesign/MainWindow/FormMain.cs` — 行 55、77、114
- `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` — 行 234、255、376、413、472、476
- `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` — 行 210
- `UIDesign/SubDialog/UserManagerDialog/LoginForm.cs` — 行 32、52
- `UIDesign/TabPage/CommSettingPage.cs` — 行 472
- `UIDesign/TabPage/FilebackupPage.cs` — 行 109、279、400、514、552、578、628、648、662、670、692、696、858、884、889、1492、1498、1523、1526、1554、1558
- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 252、398、457
- `UIDesign/TabPage/MonitorCamPage.cs` — 行 647、666
- `UIDesign/TabPage/ProcessControlPage.cs` — 行 280、310、690、717、736、741、759、766、772、777、791、796、930、936、996、1031、1045、1269、1274、1287、1300、1475、1578
- `UIDesign/TabPage/SystemControlPage.cs` — 行 193、1331、1612、1632、1650、1708、1726、1734、1742、1747、1752、1761
- `WeldParamControl/Algorithms/SeamMapTrackingAlgorithm.cs` — 行 307
- `WeldParamControl/Algorithms/SeamTrackingAlgorithm.cs` — 行 105
- `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` — 行 238
- `WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs` — 行 94
- `WeldParamControl/WeldParamConfig.cs` — 行 884、1000、1034
- `WeldParamControl/WeldParamManager.cs` — 行 603、667、763、870、877、884、904、911、929、936、946、971、1003、1203、1263、1412、1525、1536、1580
- `WeldParamControl/WeldParamProfileAudit.cs` — 行 64

### ConfigFileManager（30 处调用 / 11 个调用方文件）

- `Comm/Communication/CommunicationManager.cs` — 行 179、190、202、213、224、235、246、263、486
- `EmguALG/Manager/AlgorithmManager.cs` — 行 43、250
- `EmguALG/Roi/ImageRoiTool.cs` — 行 22、66
- `LineLaserCam/LineLaserConfig.cs` — 行 185、224、236
- `MainDeviceControl/SimulationConfig.cs` — 行 82
- `MonitorCam/MonitorCamConfig.cs` — 行 105
- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 457、1021、1179、1185、1224、1225
- `MotionControl/MontionManager.cs` — 行 1425
- `PCLOperate/Render/RenderConfig.cs` — 行 43、330
- `WeldParamControl/Curves/TaLaCurveConfig.cs` — 行 223
- `WeldParamControl/WeldParamManager.cs` — 行 966、997

### EtherCATMasterNative（22 处调用 / 7 个调用方文件）

- `MotionControl/DeltaEtherCAT/DeltaInputIO.cs` — 行 65
- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 141、206、1424
- `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs` — 行 71、92、101、134、138、164、228、232
- `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs` — 行 58
- `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` — 行 79、153、170、219、259、285
- `MotionControl/DeltaEtherCAT/DeltaSlaveScanner.cs` — 行 131、141
- `MotionControl/DeltaEtherCAT/Native/DeltaErrorCode.cs` — 行 115

### ConfigSelfHeal（26 处调用 / 5 个调用方文件）

- `Comm/Communication/CommunicationManager.cs` — 行 353、354、355、356、357、358、359、360、361、364
- `LineLaserCam/LineLaserConfig.cs` — 行 224
- `MonitorCam/MonitorCamConfig.cs` — 行 75、76、77、78、79、80、81、82、83、144、164
- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 1227
- `WeldParamControl/WeldParamManager.cs` — 行 967、993、998

### DeltaErrorCode（9 处调用 / 5 个调用方文件）

- `MotionControl/DeltaEtherCAT/DeltaInputIO.cs` — 行 74
- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 182、1251
- `MotionControl/DeltaEtherCAT/DeltaMontionControl.cs` — 行 74、96、105、139
- `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs` — 行 69
- `MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs` — 行 118

### PermissionLevel（12 处调用 / 5 个调用方文件）

- `UIDesign/MainWindow/FormMain.cs` — 行 281、283
- `UIDesign/SubDialog/UserManagerDialog/LoginForm.cs` — 行 42、53
- `UIDesign/TabPage/LineLaserCamPage.cs` — 行 239、241
- `UIDesign/TabPage/MonitorCamPage.cs` — 行 131、161
- `UIDesign/TabPage/SystemControlPage.cs` — 行 135、152、166、167

### CommandCore（14 处调用 / 4 个调用方文件）

- `Comm/Communication/CommunicationManager.cs` — 行 826
- `MainDeviceControl/DeviceControlWork.cs` — 行 901、1006、1012、1013、1151、1894
- `UIDesign/ControlPage/MainPage.cs` — 行 927、928
- `UIDesign/TabPage/CommSettingPage.cs` — 行 377、379、437、472、474

### ConfigBackupHelper（9 处调用 / 4 个调用方文件）

- `FileOperate/ConfigSelfHeal.cs` — 行 181、182
- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 225、233、234
- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 1178、1179
- `MotionControl/DeltaEtherCAT/SystemConfigPackager.cs` — 行 165、200

### AxisStatus（13 处调用 / 3 个调用方文件）

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 234、762、770、831、1124
- `MotionControl/IMotion/MontionAxis.cs` — 行 216
- `MotionControl/MontionManager.cs` — 行 321、463、467、529、813、907、965

### ImageAlgorithm（16 处调用 / 3 个调用方文件）

- `EmguALG/Core/AlgorithmBase.cs` — 行 39、42、45、48、51、60、63、66、69、78、81、84、87、100
- `EmguALG/RealtimeMonitor/WeldQuality/WeldQualityAlgorithm.cs` — 行 75
- `EmguALG/RealtimeMonitor/WireFeedDistance/WireFeedDistanceAlgorithm.cs` — 行 75

### LaserWeldHeadWorkflow（5 处调用 / 3 个调用方文件）

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 881、979、985
- `UIDesign/TabPage/SystemControlPage.cs` — 行 2333
- `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` — 行 228

### LineLaserSeamResult（3 处调用 / 3 个调用方文件）

- `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` — 行 1163
- `LineLaserCam/LineLaserManager.cs` — 行 292
- `LineLaserCam/VirtualCam/VirtualCam.cs` — 行 118

### MontionControl（4 处调用 / 3 个调用方文件）

- `MainDeviceControl/DeviceStatusWork.cs` — 行 309
- `MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs` — 行 505
- `MotionControl/MontionManager.cs` — 行 446、1628

### ConfigChangeLogger（5 处调用 / 2 个调用方文件）

- `ConfigFileControl/Implementations/ConfigSnapshot.cs` — 行 101、109
- `WeldParamControl/WeldParamManager.cs` — 行 1070、1302、1348

### ConfigHelper（19 处调用 / 2 个调用方文件）

- `UIDesign/TabPage/ProcessControlPage.cs` — 行 268、318、345
- `WeldParamControl/WeldParamManager.cs` — 行 532、536、561、568、796、802、810、1029、1047、1050、1052、1061、1105、1112、1150、1161

### ConfigSnapshot（12 处调用 / 2 个调用方文件）

- `ConfigFileControl/Implementations/ConfigFileManager.cs` — 行 143、152、152、173、182、182
- `WeldParamControl/WeldParamManager.cs` — 行 1338、1339、1346、1346、1347、1347

### DeviceWaitSettings（2 处调用 / 2 个调用方文件）

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 618
- `MotionControl/MontionManager.cs` — 行 1823

### EtherCATIONative（4 处调用 / 2 个调用方文件）

- `MotionControl/DeltaEtherCAT/DeltaInputIO.cs` — 行 70
- `MotionControl/DeltaEtherCAT/DeltaOutputIO.cs` — 行 90、104、116

### FlowTimeoutSettings（3 处调用 / 2 个调用方文件）

- `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` — 行 617、1033
- `MotionControl/MontionManager.cs` — 行 1822

### GalvoParams（5 处调用 / 2 个调用方文件）

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 260、276、711、735
- `MotionControl/MontionManager.cs` — 行 1329

### KUKAXMLConfig（4 处调用 / 2 个调用方文件）

- `Comm/Communication/CommunicationManager.cs` — 行 565、566、938
- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 529

### PointCloudWriter（2 处调用 / 2 个调用方文件）

- `ProductFileControl/Records/RecordFileStore.cs` — 行 405
- `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs` — 行 407

### WeldAutoParamProfile（3 处调用 / 2 个调用方文件）

- `WeldParamControl/WeldParamManager.cs` — 行 1180
- `WeldParamControl/WeldParamProfileAudit.cs` — 行 97、118

### WeldHeadConfig（3 处调用 / 2 个调用方文件）

- `MotionControl/MontionManager.cs` — 行 1453、1524
- `UIDesign/TabPage/ProcessControlPage.cs` — 行 585

### AutoParam（3 处调用 / 1 个调用方文件）

- `WeldParamControl/WeldParamManager.cs` — 行 534、798、820

### AutoParamHelper（10 处调用 / 1 个调用方文件）

- `WeldParamControl/WeldParamManager.cs` — 行 545、547、1081、1083、1085、1089、1119、1149、1170、1200

### ConfigPathMigrator（1 处调用 / 1 个调用方文件）

- `Program.cs` — 行 21

### Cylinder（1 处调用 / 1 个调用方文件）

- `MotionControl/MontionManager.cs` — 行 1222

### DeltaControllerConfigImporter（7 处调用 / 1 个调用方文件）

- `UIDesign/TabPage/FilebackupPage.cs` — 行 274、494、512、550、576、658、1076

### DeltaMotionConfig（1 处调用 / 1 个调用方文件）

- `MotionControl/MontionManager.cs` — 行 1114

### DeltaSlaveDevice（13 处调用 / 1 个调用方文件）

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 265、265、282、284、297、297、315、315、332、334、342、343、486

### EtherCATMotionBufferNative（8 处调用 / 1 个调用方文件）

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 1339、1366、1376、1389、1399、1411、1432、1440

### EtherCATMotionNative（40 处调用 / 1 个调用方文件）

- `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` — 行 394、455、469、521、538、574、592、605、610、709、721、746、747、772、783、785、811、860、891、1007、1019、1028、1036、1044、1053、1062、1071、1081、1090、1159、1164、1181、1201、1212、1217、1238、1272、1286、1297、1310

### LineLaserSeamFeature（1 处调用 / 1 个调用方文件）

- `LineLaserCam/LineLaserManager.cs` — 行 509

### MotionConfigImporter（1 处调用 / 1 个调用方文件）

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 246

### PointCloudReader（3 处调用 / 1 个调用方文件）

- `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs` — 行 155、306、344

### RenderConfig（1 处调用 / 1 个调用方文件）

- `UIDesign/SubDialog/DataReviewerDialog/RenderParamForm.cs` — 行 131

### RsiPacketFormat（2 处调用 / 1 个调用方文件）

- `Comm/Communication/Implementations/KukaRsiComm.cs` — 行 770、890

### SeamCalData（1 处调用 / 1 个调用方文件）

- `WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs` — 行 353

### SeamTraceYRecord（1 处调用 / 1 个调用方文件）

- `ProductFileControl/ProductFileRecordManager.cs` — 行 511

### SurfaceTriangulator（6 处调用 / 1 个调用方文件）

- `PCLOperate/Render/PointCloudViewer.cs` — 行 557、576、596、617、637、657

### SystemConfigPackager（2 处调用 / 1 个调用方文件）

- `UIDesign/TabPage/FilebackupPage.cs` — 行 1519、1550

### VectorMath（38 处调用 / 1 个调用方文件）

- `PCLOperate/Render/SurfaceTriangulator.cs` — 行 53、54、55、65、143、180、181、182、240、278、290、301、302、303、363、419、424、525、528、528、529、535、536、592、621、661、662、663、670、715、717、738、749、750、751、777、901、926

### WeldFlowSteps（5 处调用 / 1 个调用方文件）

- `UIDesign/ControlPage/MainPage.cs` — 行 786、835、836、844、873

### WeldHeadSlaveDevice（2 处调用 / 1 个调用方文件）

- `MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs` — 行 207、213

### WeldParamProfileAudit（1 处调用 / 1 个调用方文件）

- `WeldParamControl/WeldParamManager.cs` — 行 1092

### XlsxSheetReader（1 处调用 / 1 个调用方文件）

- `MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs` — 行 874

## 二、继承 / 实现边

- `AlgorithmResultStore` → `IResultStore<T>`（implements）
- `AuthHelper` → `DatabaseHelperBase`（inherits）
- `AutoParamHelper` → `DatabaseHelperBase`（inherits）
- `ConfigHelper` → `DatabaseHelperBase`（inherits）
- `ContourFrameItem` → `RecordItem`（inherits）
- `DeltaInputIO` → `InputIO`（inherits）
- `DeltaMontionAxis` → `MontionAxis`（inherits）
- `DeltaMontionControl` → `MontionControl`（inherits）
- `DeltaOutputIO` → `OutputIO`（inherits）
- `DeviceWorkflowBase` → `DeviceStateBase`（inherits）
- `EdgeDetectionStage` → `StageBase`（inherits）
- `EthernetXmlComm` → `CommChannelBase`（inherits）
- `FeatureExtractionStage` → `StageBase`（inherits）
- `FilterStage` → `StageBase`（inherits）
- `HikCam` → `IMonitorCamApi`（implements）
- `InLaserModbusComm` → `CommChannelBase`（inherits）
- `InputIO` → `MontionIO`（inherits）
- `IntelligentLaserCam` → `LineLaserCameraBase`（inherits）
- `KukaRsiComm` → `CommChannelBase`（inherits）
- `LaserWeldHeadWorkflow` → `DeviceWorkflowBase`（inherits）
- `LineLaserContourAlgorithm` → `ILineLaserContourAlgorithm`（implements）
- `LineLaserContourRecord` → `ProductRecordBase`（inherits）
- `LineLaserWorkflow` → `DeviceWorkflowBase`（inherits）
- `MonitorCameraWorkflow` → `DeviceWorkflowBase`（inherits）
- `MontionAxis` → `IPVTMotion`（implements）
- `MorphologyStage` → `StageBase`（inherits）
- `MotionControlWorkflow` → `DeviceWorkflowBase`（inherits）
- `OutputIO` → `MontionIO`（inherits）
- `ProductDatabaseHelper` → `DatabaseHelperBase`（inherits）
- `SeamMapTrackingAlgorithm` → `WeldAlgorithmBase`（inherits）
- `SeamTrackingAlgorithm` → `WeldAlgorithmBase`（inherits）
- `SiemensS7Comm` → `CommChannelBase`（inherits）
- `TemplateMatchStage` → `StageBase`（inherits）
- `VirtualCam` → `LineLaserCameraBase`（inherits）
- `WeldAdjustmentRecordEventArgs` → `WeldFrameRecordEventArgs`（inherits）
- `WeldParamAdjustItem` → `RecordItem`（inherits）
- `WeldParamAdjustmentAlgorithm` → `WeldAlgorithmBase`（inherits）
- `WeldParamControlRecord` → `ProductRecordBase`（inherits）
- `WeldParamControlWorkflow` → `DeviceWorkflowBase`（inherits）
- `WeldParamLookupAlgorithm` → `WeldAlgorithmBase`（inherits）
- `WeldQualityAlgorithm` → `IAlgorithm<T>`（implements）
- `WeldQualityAlgorithm` → `IConfigurableAlgorithm<T>`（implements）
- `WeldQualityResult` → `AlgorithmResult`（inherits）
- `WeldResultItem` → `RecordItem`（inherits）
- `WeldResultRecord` → `ProductRecordBase`（inherits）
- `WireFeedDistanceAlgorithm` → `IAlgorithm<T>`（implements）
- `WireFeedDistanceAlgorithm` → `IConfigurableAlgorithm<T>`（implements）
- `WireFeedResult` → `AlgorithmResult`（inherits）

## 相关页面

- [[architecture/CodeMap]]
- [[architecture/CodeMap-Relations-Methods-Comm]]
- [[architecture/CodeMap-Relations-Methods-EmguALG]]
- [[architecture/CodeMap-Relations-Methods-FileOperate]]
- [[architecture/CodeMap-Relations-Methods-LineLaserCam]]
- [[architecture/CodeMap-Relations-Methods-MainDeviceControl]]
- [[architecture/CodeMap-Relations-Methods-MainDeviceControl-2]]
- [[architecture/CodeMap-Relations-Methods-MotionControl]]
- [[architecture/CodeMap-Relations-Methods-MotionControl-2]]
- [[architecture/CodeMap-Relations-Methods-PCLOperate]]
- [[architecture/CodeMap-Relations-Methods-ProductFileControl]]
- [[architecture/CodeMap-Relations-Methods-SQLiteDBControl]]
- [[architecture/CodeMap-Relations-Methods-Thin]]
- [[architecture/CodeMap-Relations-Methods-UIDesign]]
- [[architecture/CodeMap-Relations-Methods-UIDesign-2]]
- [[architecture/CodeMap-Relations-Methods-WeldParamControl]]
- [[rules/KR-009-Grep-Default]]
