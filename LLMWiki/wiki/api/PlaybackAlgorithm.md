---
title: PlaybackAlgorithm — 监控相机回放算法（算法层）
date: 2026-11-09
updated: 2026-11-09
tags: [API, 监控相机, 回放, 算法层, EmguALG]
source: AdaWeldSystem/EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs
---

# PlaybackAlgorithm

> `AdaWeldSystem.EmguALG.RealtimeMonitor.Playback.PlaybackAlgorithm`（`EmguALG/RealtimeMonitor/Playback/PlaybackAlgorithm.cs`）。
> **2026-11-09 ADR-097**：回放（录像解码 + 帧推进）属算法能力，由 `AlgorithmManager.Playback` 惰性持有并跨页面共用；流程层 `MonitorCameraWorkflow` 只做门面转发，UI 只调用与展示。
> 命名与目录按 `RealtimeMonitor` 下同级算法的既有形态统一（`WireFeedDistance/WireFeedDistanceAlgorithm`、`WeldQuality/WeldQualityAlgorithm`）：**子目录名 + Algorithm**。原 `EmguALG/Playback/MonitorPlaybackAlgorithm.cs` 已迁入本目录并改名；行数据 `PlaybackFileInfo` / `PlaybackScanResult` 同目录独立文件。

## 公开成员

| 成员 | 类型 | 说明 |
|---|---|---|
| `LoadRange(string root, DateTime start, DateTime end)` | `void` | 按日期区间扫描录像（后台线程）；根目录由调用方注入，本层不依赖硬件 Manager |
| `CancelScan()` | `void` | 取消在跑的扫描与缩略图线程（代数自增，旧结果作废） |
| `PlayFile(string path)` | `string` | 打开录像并播放；空串成功，否则为可展示提示（文件不存在 / 解码不支持） |
| `TogglePlayPause()` | `string` | 播放/暂停；无打开文件时返回「请先在右侧列表右键选择要回放的录像文件！」 |
| `CycleSlow()` / `CycleFast()` | `void` | 0.8/0.5/0.3/0.1/1.0、1.5/2.0/2.5/3.0/1.0 循环，切速不重置位置 |
| `SeekToFrame(int frameIndex)` | `void` | 定位帧（`CapProp.PosFrames`）；暂停态补一帧供显示 |
| `SeekBySeconds(double seconds)` | `void` | ±5 秒按钮入口 |
| `Stop()` | `void` | 释放解码器并复位进度/倍速；**幂等**，可重复调用 |
| `Reset()` | `void` | 复位到干净会话（无源、未播放、倍速 1.0）+ 取消扫描与缩略图 |
| `HasSource` / `IsPlaying` / `Speed` | `bool` / `bool` / `double` | 只读状态 |
| `Dispose()` | `void` | 停定时器、释放解码器、取消扫描；**仅算法层持有方使用，页面不得调用** |

## 事件（后台线程抛出，订阅方自行 `BeginInvoke` 封送）

| 事件 | 载荷 | 用途 |
|---|---|---|
| `ScanStarted` | `string caption` | 清空列表 + 忙碌文案 |
| `ScanCompleted` | `PlaybackScanResult` | 行数据（`PlaybackFileInfo`）+ 结果文案 / 快速失败 |
| `ScanCrashed` | `string message` | 扫描线程异常原文 |
| `ThumbnailReady` | `PlaybackFileInfo` | 缩略图回填（96×54） |
| `FrameReady` | `Mat` | 本拍末帧上屏 |
| `ProgressChanged` | `int index, int total, double fps` | 进度条与时间标签 |
| `PlayStateChanged` | `bool playing, double speed` | 播放/暂停图标与速度标签 |

## 行为约束

- 时间基准：`锚点帧 + 时钟 × 帧率 × 倍速`（33ms 定时器）；暂停/定位/切速均重锚，误差不累积。
- 每拍只把末帧交 UI，中间帧就地 `Dispose`；解码在定时器线程，不占 UI 线程。
- 缩略图与扫描各起后台 `Thread`；代数失配立即退出并释放已解码位图。
- 帧所有权：`FrameReady` 交付的 `Mat` 随显示控件持有；扫描行 `Thumbnail` 由 UI 列表清空时释放。
- **跨页面会话**：`AlgorithmManager` 单例持有本组件；页面打开先 `Stop()` 复位，关闭只 `Stop + CancelScan + 退订`，不 `Dispose`；事件支持多次 `+=/-=`，退订后不再触发。

## 等价性验证

3s / 30fps / 320×240 MJPG 样例：`total=90 fps=30`、1s `idx=29`、暂停 400ms `delta=0`、恢复 +1.5x 0.7s `29→58`、`seek+5s` 解码位置 `90`、`stop` 归零（与迁移前逐项一致）。真实录像与现场相机未验。

## 关联

- [[modules/MonitorCam]]、[[api/MonitorCameraWorkflow]]、[[api/AlgorithmManager]]
- [[decisions/ADR-097-algorithm-layer-ownership-single-entry]]、[[decisions/ADR-078-MonitorPlaybackControlBarAndDatedRecords]]、[[decisions/ADR-097-algorithm-layer-ownership-single-entry]]
