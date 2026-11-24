# 代码精简修复进度表（新版标准）

> **2026-10-29 现行状态**：本页为 2026-08-26 历史快照，计数已过时。现行欠账见 [[architecture/CodeMap]] §5.7；工具链与放行条件见 [[standards/CodeSimplification-Tooling]]。成员顺序已按「**region 内排序、跨 region 不比较**」口径**清零**（0 处 / 0 文件），全库 `MSBuild /t:Rebuild` errors=0。

> **已归档（2026-09-01）**：本页是 2026-08-26 的一次**过程性进度快照**，不是规范，故自 `standards/` 迁出；2026-09-01 `archive/` 分类取消后归 `project/`。
> 规范正文见 [[standards/CodeSimplification]]；表中计数与当前代码已不同步，仅作历史追溯。

date: 2026-08-26
说明：按「顶层文件夹扫描」基线（task LwV0UC：112 文件 / 1089 警告 / 1315 提示 / 0 异常）。用户于 13:15 重定向优先级为**线激光英莱相机 + 英莱相关 UI**（`IntelligentLaserCam.cs` 等 `LineLaserCam` 模块 + 4 个 `IL*` UI 文件），优先于原 Top4 轨道。每修复一个文件/文件夹后复跑 `scripts/scan_by_folder.sh <文件夹>` 或单文件脚本取当前计数，更新本表。

关联标准：[[standards/CodeSimplification]] · 扫描脚本：`scripts/scan_by_folder.sh` · 单文件：`scripts/csharp_review.py`（均位于 `Vicoding管理平台/LLMWiki/scripts/`，非 wiki 页面）

## 轨道二：英莱相机 + 英莱 UI（用户重定向优先）
date: 2026-08-26 · 范围：LineLaserCam 模块(17) + IL* UI(4) = 20 文件 / 122 警告 / 250 提示
> **范围红线（用户澄清）**：「英莱相机」仅指 IntelligentLaser 品牌。SmartRayCam/HikRobotCam/VirtualCam 为不同品牌，不属本轨道，保持待修复。本轨道实际优先项 = 英莱核心(1) + IL* UI(4) = 5 文件。

| 文件 | 基线警告 | 基线提示 | 当前警告 | 当前提示 | 状态 | 备注 |
|---|---|---|---|---|---|---|
| LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs | 64 | 56 | 2 | 56 | 已修复 | 英莱相机核心；剩2=Log参数误报+B类Thread.Sleep(留业务确认) |
| LineLaserCam/SmartRayCam/ApiCore/SensorHelper.cs | 9 | 0 | 9 | 0 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| LineLaserCam/SmartRayCam/CameraRun.cs | 7 | 15 | 7 | 15 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| LineLaserCam/SmartRayCam/ApiCore/SensorImageData.cs | 6 | 2 | 6 | 2 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| LineLaserCam/Api/CameraSelector.cs | 5 | 10 | 5 | 10 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| LineLaserCam/HikRobotCam/HikCameraRun.cs | 4 | 17 | 4 | 17 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| LineLaserCam/VirtualCam/VirtualCam.cs | 4 | 16 | 4 | 16 | 待修复 | |
| LineLaserCam/SmartRayCam/ApiCore/PackagedImage.cs | 4 | 0 | 4 | 0 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| LineLaserCam/SmartRayCam/ApiCore/SensorPointCloudMSR.cs | 3 | 1 | 3 | 1 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| LineLaserCam/SmartRayCam/ApiCore/SensorPointCloud.cs | 3 | 1 | 3 | 1 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs | 2 | 8 | 1 | 9 | 已修复(留1误报) | UI·A类已清；CheckRange(double/long)为合法重载误报，留业务确认 |
| LineLaserCam/HikRobotCam/ApiCore/HikCameraDevice.cs | 2 | 29 | 2 | 29 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs | 2 | 28 | 0 | 21 | 已修复 | UI·A类已清（本次修复断裂的嵌套类 IlJobParamRow + 区域错乱） |
| LineLaserCam/SmartRayCam/CameraPresetManager.cs | 2 | 25 | 2 | 25 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| UIDesign/TabPage/ILCamPage.cs（已改名 LineLaserCamPage.cs） | 2 | 22 | 0 | 22 | 已修复 | UI·A类已清（功能型 region 保留，info 级） |
| LineLaserCam/HikRobotCam/ApiCore/HikCameraManager.cs | 1 | 7 | 1 | 7 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| LineLaserCam/SmartRayCam/ApiCore/SensorState.cs | 1 | 5 | 1 | 5 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| UIDesign/SubDialog/IntelligentLaserDialog/ILScanForm.cs | 1 | 4 | 0 | 5 | 已修复 | UI·A类已清 |
| LineLaserCam/Api/ICameraRun.cs | 1 | 2 | 1 | 2 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| LineLaserCam/SmartRayCam/ApiCore/SensorManager.cs | 0 | 1 | 0 | 1 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| LineLaserCam/SmartRayCam/ApiCore/Sensor.cs | 0 | 1 | 0 | 1 | 待修复 | （2026-09-08 已删除：ADR-007 线激光三层重构，见 modules/LineLaserCam） |
| **合计** | **122** | **250** | **54** | **245** | | 英莱5文件已修复（仅留误报/业务确认项） |

| 文件夹 | 文件数 | 基线警告 | 基线提示 | 当前警告 | 当前提示 | 状态 | 备注 |
|---|---|---|---|---|---|---|---|
| MotionControl | 17 | 336 | 174 | 336 | 174 | 待修复 | 最大冗余 |
| EmguALG | 15 | 163 | 243 | 163 | 243 | 待修复 | |
| Comm | 12 | 162 | 119 | 120 | 109 | 进行中 | EKICommunication 已完成 44→2（剩 Thread.Sleep 节流 + Initialize 重载误报，非冗余） |
| PCLOperate | 10 | 134 | 113 | 134 | 113 | 待修复 | |
| **合计** | 54 | 795 | 549 | 795 | 549 | | |

## 修复约束（来自 CodeSimplification.md）
- 不改 public/protected 方法签名与枚举成员名；不碰 designer.cs；#region 必须配对；Dispose 不动。
- A 类（文件整理/注释）：补 #region（按成员类型）、`///` 注释标准化（无论公私，写了就要 summary 一行 + param/returns 完整；public/protected 建议写，private 可选）、类级 summary ≤20字。 ⚠ **2026-10-26 口径已更新（本页为历史记录，冲突以此为准）**：① `#region` 类型/语义并存，只强制配对完整性 ② public 改为「新增或改动必写，存量欠账不追溯」③ **private 明确为「允许且建议写 `///` 做总结（不强制，且不得据此删除既有 private `///`）」** ④ 功能重叠阈值对齐 70%。现行口径见 [[standards/CodeSimplification]] 与 [[standards/CodeSimplification-Tooling]]。
- B 类（逻辑）：删无意义 null 检查（new/值类型/this/本文件私有参数）、删无效锁 `lock(new object())`、过度属性改只读、过度等待/缓存/资源管理按需清理。
- C 类（函数）：合并功能重叠、内联单层 private、删死函数（均须 Grep 确认引用）。
- 每文件夹修复后复跑脚本至清零或仅剩需业务确认的 B 类项；本项目无法编译，靠 Grep 影响半径 + 标准自检兜底。
