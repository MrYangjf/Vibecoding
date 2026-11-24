---
title: 拿位置硬门覆盖驱动器回零完成信号的现场坑
date: 2026-11-20
updated: 2026-11-23
tags: [教训, 运控, 回零, 台达]
status: active
source: 现场报障 2026-11-20（Y轴回零 NOT_REACHED 误判）
---

# 拿位置硬门覆盖驱动器回零完成信号的现场坑

> **一句话**：回零完成以驱动器 Home_Status 为权威、位置只作告警；两者冲突时先怀疑判据的门控层级。

## 现象

Y 轴回零日志显示「回零完成 用时 3.3s 起 -9.985mm 终 -1.000mm」，但上层仍报 `NOT_REACHED`；随后「停止轴 失败 错误码 4866 描述为空」。

## 根因

`WaitAxisHomed` 用 `expectHome = HomeOffset` 作位置硬门。扭矩回零模式（-3）下台达把 offset 反向应用（配置 `HOME_OFFSET=1.0mm` → 终位 -1.000mm），硬门与实测差 2mm。而权威信号 `Home_Status`（手册 §12.3：0=完成/1=运动中/2=中止/3=错误）已确认完成。失败分支又对已静止轴补发 `StopAxis`，产生 4866。

## 判据

1. 回零完成 = `HomeVerified && Home_Status==0 && 速度稳定`；位置与期望不符只记 Warning，不阻断。
2. 负模式 offset 方向手册未覆盖（见 [[decisions/ADR-080-DeltaTorqueHomingSignedModeAndDetectParams]]），⛔ 不得让无手册约定的符号语义成为完成硬门。
3. 失败分支不再对回零已完成轴补发 Stop（避免 4866 噪声）；真超时/未启动才需要停机。

## 预防

运动完成的权威信号优先取设备状态字，位置是二次证据；两者冲突时先怀疑判据的门控层级，而非设备动作。

## 相关页面

- [[decisions/ADR-080-DeltaTorqueHomingSignedModeAndDetectParams]]
- [[api/MontionManager]] · [[api/MotionControlWorkflow]]
- [[guides/DeltaEtherCAT-DevGuide]]
- [[index/index]]
