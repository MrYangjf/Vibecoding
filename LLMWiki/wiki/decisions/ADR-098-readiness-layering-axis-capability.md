---
title: ADR-098 分层就绪 L0~L4 与轴级能力
date: 2026-11-16
updated: 2026-11-16
tags: [决策]
status: accepted
---

# ADR-098 分层就绪 L0~L4 与轴级能力

> **决策一句话**：分层就绪 L0~L4 与轴级能力

## 背景

设备与流程只有 Connected/未 Connected 二值，免回零轴与需回零轴无法区分，动作入口无法给出可读的拒绝原因。

## 决策

1. 就绪分断连/L0 已连接/L1 已使能/L2 未回零/L3 已回零/L4 已到工作零位，数值只用于比较
2. 轴级能力用 NeedHoming/HasAbsoluteEncoder/WorkZeroSource 描述，免回零轴使能后直接进 L3
3. 禁按轴名写分支，能力由配置与硬件属性决定
4. 分层状态挂在 DeviceWorkflowBase，只按本流程依赖轴求值
5. 断连时 L1~L4 全部失效，不允许降级运行
6. 动作门槛：点动 L1、寻位 L3、自动焊接 L4；线激光/监控相机/焊接工艺/焊接头为 L0
7. 未达门槛由 EnsureReadiness 拒绝，原因固定含当前 L/需 L/动作/具体原因

## 备选方案

- 门槛只返回 bool 不给原因 → 现场无法判断缺哪一级，弃。
- 每根轴各建一个就绪类 → 与 Manager 重复持有状态，易失真，弃。
- 按轴名特判（`axis == "Y"`）→ 新增轴立即失效，弃。
- 保留 Connected 二值并在调用点各写判断 → 判据分散、口径漂移，弃。

## 后果

### 正面
- 动作入口拒绝信息含「当前 L / 需 L / 动作 / 原因」，可现场定位。
- 免回零轴使能后直接 L3，不再被 L2 永久卡住。
- 轴能力可复用，新增轴只填能力声明，不写分支。

### 负面
- 各流程须显式声明能力，漏声明会保守停在 L1（不放开、不误放）。
- 工作零位判 L4 依赖容差，容差过小会误判未到位。

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-042-SeamTrackingConsolidated]]
- [[api/MotionControlWorkflow]]
- [[api/LaserWeldHeadWorkflow]]
- [[modules/DeviceControl]]
