---
title: ScottPlot SignalXY 的 X 单调约束与显示层回退剔除
date: 2026-11-20
updated: 2026-11-20
tags: [教训, UI, ScottPlot, SignalXY, 单调, 轮廓显示, 相机]
status: active
source: AdaWeldSystem/UIDesign/ControlPage/MainPage.cs（2026-11-20 更换线激光后 xs must not descend 异常）
---

# ScottPlot SignalXY 的 X 单调约束与显示层回退剔除

> **一句话**：`AddSignalXY` 的 X 数组必须严格升序；相机轮廓点局部回退会在 `Refresh()` 抛 `xs must not descend`，修复只在显示数组写入时剔除回退点，不动数据源。

## 现象

更换线激光后主页面板报错 `System.InvalidOperationException: xs must not descend: xs[927]=14.51 but xs[928]=14.47`，堆栈指向 `MainPage.UpdateChartUI()` 的 `formsPlot1.Refresh()`。旧相机无此问题。

## 根因

`AddSignalXY(_contourSignalXs, _contourSignalData)` 的 X = 物理坐标 Y（非等距，显式数组）。ScottPlot 的 `SignalPlotXY` 在 Refresh 时要求 X 严格升序；新相机在局部位置出现回退（差约 0.04mm），属抖动级回退，但已足以触发异常。数据本身没错（轮廓 Y 可回退），错在把原始点序直接喂给了要求升序的绘图类型。

## 判据

1. **不改数据源**：`LineLaserManager.Profile` 快照是算法与记录链路的共享真相源（`MotionControlWorkflow` 读 `HasResult`），显示层异常不得回改 Manager/算法/记录。
2. **显示数组写入时剔除**：拷入 `_contourSignalXs` 时，只在 `x > lastX` 才写入对应 X/Z 对，保证严格升序；渲染点数取实际写入数（`_snapPointCount = written`），`zero-written` 直接返回。
3. **X↔Z 成对写**：剔除判定后 X 与 Z 必须写在同一 `written` 索引，否则轮廓形状错位。
4. **整体降序属另一问题**：若相机整幅从右向左扫描（首尾 X 反转），剔除会只剩首点；应先判方向并整体反转数组（连同 Z），这属独立裁定，不与局部抖动混为一谈。本轮报错发生在第 927 点，判为局部回退。

## 预防

- 新增/更换相机时先抓一帧原始 Y 序列，检查单调性与回退幅度，再决定是否需显示层单调化。
- 显示层做单调化只在**拷入绘图数组**这一步做，⛔ 不污染上游快照与算法缓存。
- 真编译能抓语法/接线，但抓不到这类运行期数据约束；须以真实相机帧验证 Refresh 不再抛异常。

## 相关页面

- [[api/MainPage]] —— 轮廓图 `AddSignalXY` 与 `ApplyProfileSnapshot` 落地页
- [[api/IntelligentLaserCam]] —— §5.16 X 非等距必须 AddSignalXY、点序倒序会镜像
- [[decisions/ADR-097-algorithm-layer-ownership-single-entry]] —— 轮廓算法层归属
- [[index/index]]
