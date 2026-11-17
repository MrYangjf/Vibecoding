---
title: "ADR-097 算法层归属与唯一入口（回放归 EmguALG）（整合旧 096（帧载体边界））"
merged_from: [ADR-096]
date: 2026-11-09
updated: 2026-11-17
tags: [决策]
status: accepted
---

# ADR-097 算法层归属与唯一入口（回放归 EmguALG）

> **决策一句话**：算法层 = `EmguALG`（EMGU 用法 + 算法配置）；`AlgorithmManager` 是算法层的**唯一实例化与取用入口**；同级 Manager 不互持算法对象；回放（解码 + 帧推进）属算法能力，落 `EmguALG/RealtimeMonitor/Playback`，流程层只编排、UI 只调用。

## 背景

上一轮把回放组件放在流程层（`MainDeviceControl/DeviceWorkflow/MonitorPlaybackController.cs`），并让 `MonitorCamManager` 持有 `AlgorithmManager` 并对 `DetectWireFeed/DetectWeldQuality` 做包装。业主复核后定稿四层口径：

1. **算法层 = `EmguALG`**：所有 EMGU 用法（图像运算、解码、检测）与算法自身参数配置都在层内。
2. **`AlgorithmManager` 唯一入口**：外部要用算法只能取 `AlgorithmManager.Instance`，不得自己 `new` 算法类，不得绕过它读算法配置。
3. **同级 Manager 不互相持有**：`MonitorCamManager` 与 `AlgorithmManager` 平级，需要算法直取 `AlgorithmManager.Instance`。Manager 互持会让算法生命周期被某个硬件 Manager 绑架。
4. **回放归算法层**：回放本质是「录像解码 + 帧推进」，不碰相机硬件、不知道业务流程，属算法能力；流程层只决定「什么时候放、放哪段、放完干什么」。

落地链：`EmguALG`（算法 + 算法配置，`AlgorithmManager` 唯一入口）→ Manager（硬件，平级直取 Instance）→ Workflow（编排）→ UI（只调用）。

## 决策

### D1 回放归算法层

- 新组件：`EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs`，命名空间 `AdaWeldSystem.EmguALG.RealtimeMonitor.Playback`（2026-11-09 二次调整：由 `EmguALG/Playback/MonitorPlaybackAlgorithm.cs` 迁入并改名，与 `WireFeedDistance/WireFeedDistanceAlgorithm`、`WeldQuality/WeldQualityAlgorithm` 同级同形）。
- DTO 下移：`PlaybackFileInfo` / `PlaybackScanResult` 归算法层（原 `MonitorPlaybackFileInfo` / `MonitorPlaybackScanResult` 删除），同目录独立文件。
- 反向依赖清除：不再读 `MonitorCamManager.RecordDirectory`，改为 `LoadRange(string root, DateTime start, DateTime end)`，根目录由流程层从硬件配置取出后传入；`EmguALG` 目录内不得出现 `MonitorCam` / `UIDesign` / `MainDeviceControl` 的引用。
- 生命周期：`AlgorithmManager.Playback` 惰性持有，**不随页面或线激光/监控相机 Manager 构造**；所有页面共用同一实例。
- 跨页面会话状态：`Stop()` 幂等；页面打开先 `Stop()` 复位到「无源、未播放、速度 1.0」；事件支持多次 `+=/-=`，退订后不再触发；页面关闭只 `Stop + CancelScan + 退订`，**不得 `Dispose` 单例组件**。

### D2 流程层门面，UI 不接触算法对象

`MonitorCameraWorkflow` 提供回放门面：9 方法（`CancelScan` / `LoadRange` / `PlayFile` / `TogglePlayPause` / `CycleSlow` / `CycleFast` / `SeekToFrame` / `SeekBySeconds` / `StopPlayback`）+ 3 属性（`HasSource` / `IsPlaying` / `Speed`）+ 7 转发事件（`ScanStarted` / `ScanCompleted` / `ScanCrashed` / `ThumbnailReady` / `FrameReady` / `ProgressChanged` / `PlayStateChanged`）。门面在构造期接线一次，UI 只订阅门面。

> `StopPlayback` 单独命名：`MonitorCameraWorkflow.Stop()` 语义是「停相机巡检 + 置手动停止」，两者不可合并。

### D3 撤销 Manager 算法包装

- 删除 `MonitorCamManager.DetectWireFeed/DetectWeldQuality` 与 `_algorithm` 字段；`MonitorCameraWorkflow` 直接 `AlgorithmManager.Instance.Detect*`。
- 标定十字：`MonitorCamManager.AnnotateSpot` 只从 `MonitorCamConfig` 取坐标，绘制改走 `AlgorithmManager.Instance.DrawSpotMark(Mat, int, int)`（绿色 `(0,255,0)`、半长 20px、线宽 1，越界/非正不画），出图与迁移前等价。

### D4 线激光轮廓算法收口

- `LineLaserManager` 不再 `new LineLaserContourAlgorithm()`；改取 `AlgorithmManager.Instance.LineLaserContour`。
- 生命周期随 `AlgorithmManager` 单例（惰性创建），不依赖 `LineLaserManager` 是否构造；`LineLaserManager.Dispose` 不再释放该算法。
- 该算法无可配置状态，故不新增配置入口；全仓不得出现第二处 `new LineLaserContourAlgorithm`。

## 行为等价

回放迁移按「等价搬移」执行：33 ms 定时器、`锚点帧 + 时钟 × 帧率 × 倍速`、慢/快档位数组、`CapProp.PosFrames` 跳转、缩略图后台线程 + 代数取消 + 96×54、事件后台线程抛出与 UI `BeginInvoke` 封送全部不变。样例对照（3s / 30fps / 320×240 MJPG）：`total=90 fps=30`、1s `idx=29`、暂停 400ms `delta=0`、恢复 +1.5x 0.7s `29→58`、`seek+5s` 解码位置 `90`、`stop` 归零。真实录像与现场相机未验。

## 保留域（本轮不改，登记）

| 项 | 现状 | 理由 |
|---|---|---|
| 焊参四算法 + `Algorithm_INI` | `WeldParamManager` 自持并自读 | 焊接工艺配置与运控时序耦合，硬并入会把工艺参数与流程配置绑死 |
| `ILCamPage.Clone()` | 线激光 UI 侧克隆帧 | 留待线激光界面收口时一并处理 |

## 2026-11-09 二次调整（业主要求）

### D5 回放迁入 `RealtimeMonitor` 并统一命名

- 位置：`EmguALG/RealtimeMonitor/Playback/`，与 `WireFeedDistance/`、`WeldQuality/` 同级并排。
- 命名：按同级既有形态「子目录名 + Algorithm」定名 `PlaybackAlgorithm`（原 `MonitorPlaybackAlgorithm` 去掉赘余的 `Monitor` 前缀，与 `WireFeedDistanceAlgorithm` / `WeldQualityAlgorithm` 对齐）。
- `AlgorithmManager`：`using` 改 `AdaWeldSystem.EmguALG.RealtimeMonitor.Playback`，`Lazy<PlaybackAlgorithm> _playback` + `PlaybackAlgorithm Playback` 惰性持有方式不变；流程门面 `MonitorCameraWorkflow` 的私有访问属性改为 `Playback`。

### D6 ROI 重建为通用工具（算法按需加载）

- 业主口径：ROI 是算法的辅助工具（画区域让算法只在指定区域执行），将来做通用工具、由算法按需加载。
- 落点：`EmguALG/Roi/ImageRoi.cs`（纯数据：启用标志 + X/Y/W/H + `ClampTo` + 坐标映射）+ `EmguALG/Roi/ImageRoiTool.cs`（`Load/Save` + `Crop` / `ApplyMask`）。
- 硬约束：不引用 `System.Windows.Forms`、不绑 `PictureBox`、不挂鼠标或 Paint 事件；场景未定，**不接任何算法、不新增调用点**，无不可达代码。
- 配置：默认 `Config/EmguALG/Algorithm_INI/ImageRoi.ini`，节名与键名沿用历史（`ImageROI` / `Enabled`、`X`、`Y`、`Width`、`Height`），迁移映射已恢复。

### D7 线激光轮廓算法底层依赖：A 类纯 DTO，已下移

- 核查结论：`LineLaserContourAlgorithm` 仅使用 `LineLaserCalibration` 的角点字段、`PointCloudData.Points` 的元素字段、`LineLaserSeamResult` 的 `Valid/FeatureY/FeatureZ`，**未调用任何设备或 IO 成员**，全部属 A 类。
- 处置：DTO 下移 `EmguALG/LineLaserContour/LineLaserContourData.cs`（`LineLaserProfileData` / `LineLaserCalibrationData` / `LineLaserSeamFeature`）；`ILineLaserContourAlgorithm.Render` 改收算法层 DTO；`LineLaserManager` 单点转换（轮廓复用缓冲零拷贝、标定按快照引用缓存）。
- 效果：算法层不再 `using LineLaserCam` / `PCLOperate.Models`，形成「硬件 → 算法」单向依赖，算法可脱机单测。

### D8 焊参算法与监控算法无混淆（登记，不拆）

核查 6 项均无真实耦合：`AlgorithmManager` 不含焊参四算法与焊参配置；`WeldParamManager` 不调用 `AlgorithmManager`；`MonitorAlgorithm.ini` 与焊参 `Algorithm_INI` 无键重叠、无互相读写、无同参数两处存；无共用可变 DTO（仅通用 `INIFile` 文件工具）；命名相邻但无数据通路；UI 不同页、不同调用链。结论：**0 处需拆**，仅在本 ADR 与模块页登记语义边界。

## 影响

- `EmguALG` 新增 `RealtimeMonitor/Playback/`（回放）、`Roi/`（通用 ROI 工具）、`LineLaserContour/LineLaserContourData.cs`（算法层 DTO）；`AlgorithmManager` 新增 `Playback`、`LineLaserContour` 属性与 `DrawSpotMark` 方法。
- `MainDeviceControl/DeviceWorkflow/MonitorPlaybackController.cs` 删除；`MonitorCamPage` 改订阅流程门面、页面关闭不释放组件。
- `EmguALG/Core/ImageRoiTools.cs`（Wi​nForms 绑定版）已删除，按通用工具形态重建为 `EmguALG/Roi/ImageRoi.cs` + `EmguALG/Roi/ImageRoiTool.cs`；`ImageRoi.ini` 迁移映射恢复。
- `ILineLaserContourAlgorithm.Render` 签名改收算法层 DTO（唯一调用方 `LineLaserManager` 同步转换，渲染结果等价）。
- `SystemComm` 删除无用 `using Emgu.CV`。

## 关联

- 取代：[[decisions/ADR-097-algorithm-layer-ownership-single-entry]] 的 D2「回放归流程层」与 D3「Manager 持有算法对象」（其余判据继续有效）
- 规范：[[standards/WorkflowResponsibilityBoundary]]
- 模块：[[modules/MonitorCam]]、[[modules/EmguALG]]
- API：[[api/AlgorithmManager]]、[[api/MonitorCamManager]]、[[api/MonitorCameraWorkflow]]、[[api/PlaybackAlgorithm]]

## 合并自 ADR-096 · 帧载体边界（不引入中性帧）

> 2026-11-17 治理轮合并：原页为独立 ADR-097，其现行裁定收归本页；原页文件已删除（**编号不回收**，废止号不复用）。原页的验证过程叙事已按格式契约 R2 剥离至 `logs/log.md`。

**原页决策一句话**：`Mat` 继续作为监控相机的帧载体，不新增中性帧类型、不改 `IMonitorCamApi` 帧契约；改用「层间禁止项」把边界卡死。

### 原页决策条目

采用 **B**。

> ⚠️ **部分被 [[decisions/ADR-097-algorithm-layer-ownership-single-entry]] 取代（2026-11-09）**：D2 中「回放解码与时间基准推进归流程层」、D3 中「回放迁 `MonitorCameraWorkflow`」，以及 Manager 持有算法对象的做法，已改判为「回放归算法层 `EmguALG/RealtimeMonitor/Playback`，`AlgorithmManager` 唯一入口，同级 Manager 不互持算法对象」。D1（不做中性帧）与其余判据继续有效。

### D1 为何不做中性帧

1. **契约面收益为零**：`ImageBox.Image`、`VideoCapture.QueryFrame`、`CvInvoke`、算法入参全部以 `Mat` 为通货；中性帧在每个边界都要做一次装箱/转换，实际只是把 `Mat` 藏到更深处。
2. **所有权更易失控**：增加一层 DTO 后，底层 `Mat` 的生命周期与 DTO 不再一一对应，`Dispose` 责任随创建方这条线会被打断。
3. **问题不在类型本身**：真正的违规是「UI 创建帧、做像素决策」，而不是「UI 看见了 `Mat`」。约束行为比替换类型更直接、可审查。

### D2 层间判据（与 [[standards/WorkflowResponsibilityBoundary]] 第七节同源）

| 层 | 允许 | 禁止 |
|---|---|---|
| UI | 接收上层给的**成品帧**并赋给显示控件 | `new Mat`、`CvInvoke.*`、`VideoCapture`、逐帧解码、像素运算、绘制标注 |
| 流程层 | 编排（何时采、何时析、何时回放）、消费结果（回放解码与时间基准推进**已改判归算法层**，见 ADR-097） | 直接向显示控件赋帧；自行拼厂商返回码 |
| Manager / 实现层 | 帧创建、标注、编码/解码、释放；返回码 → 文字映射 | 硬件对象/算法对象以公有属性外泄 |

- `Dispose` 责任随创建方；跨层移交必须在契约注释里写明所有权。
- 交付 UI 的帧必须是**成品帧**（标注、缩放已完成），UI 不做帧级决策。

### D3 本轮落地

- 预览标定十字：UI `AnnotateSpot` 删除，收进 `MonitorCamManager.RelayPreviewFrame`（分发副本前就地标注）。
- 软触发取帧：`MonitorCamPage.btnFeedTest_Click` 只调 `MonitorCamManager.TryAcquireCalibFrame`，判空与失败文案归 Manager。
- 回放解码/时间基准：⚠️ **已被 ADR-097 取代** —— 原「迁 `MonitorCameraWorkflow` 的回放组件」改为迁入 `EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm`，由 `AlgorithmManager.Playback` 持有，流程层只做门面转发。

### 原页背景

监控相机链路存在 UI 直接做帧处理的现象：`MonitorCamPage` 自取软触发帧、自判空、自行 `CvInvoke.Line` 画标定十字。核查时提出过两条路线：

- A：定义中性帧 DTO（`byte[] + 宽高 + 时间戳`），把 UI 与 EMGU 类型彻底隔离；
- B：保留 `Mat`，用判据约束「谁可以创建/处理帧」。

