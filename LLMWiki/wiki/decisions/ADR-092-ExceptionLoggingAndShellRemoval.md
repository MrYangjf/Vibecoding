---
title: ADR-092 — 异常留痕分级策略 · TA 兼容壳删除 · TODO 处置
date: 2026-11-06
updated: 2026-11-06
tags: [异常处理, 日志, 空catch, 兼容壳, TODO, 代码治理]
status: accepted
---

# ADR-092 — 异常留痕分级策略与代码治理收口

## 结论

1. **TA 兼容壳整体删除**：`LaserWeldHeadWorkflow` 的 7 个 TA 转发方法（`TaAuto/TaBreak/TaPose1/TaPose2/TaRetract/TaZeroPose/CancelTaZeroPose`）与 `#region` 已删，全库 TA 指令唯一入口 = [[api/MotionControlWorkflow]]。
2. **空 `catch` 不再一律静默**：按「失败是否可观测」分级留痕，**禁止在循环/定时/日志渲染路径无脑打**。
3. **TODO 一律保留**，措辞改为「现状 + 待办」双段，⛔ 不删待办事项。

## 业主原话

> `LaserWeldHeadWorkflow中不在做TA指令相关使用，请删除` / `空catch加日志记录异常(但请注意不要在循环线程做和重复判断时输出这个...)` / `空todo是什么？有可能是待做事项的注释` / `代码架构、逻辑、冗余等检测，全面精简代码和注释做了吗？`

## 决策一：空 catch 四级分类（全库 32 处实测）

| 级 | 判定条件 | 处理 | 本轮实例 |
|---|---|---|---|
| **A 必打** | 一次性调用路径，失败会让后续状态「看起来正常实则异常」 | `Warning` + 异常类型 + 消息 + 动作名 | 轴减速停止失败（3 处）、点动停止失败（2 处）、相机停止取流/采集失败（2 处） |
| **B 汇总** | 批量/清理型失败，逐条打会淹没日志 | 计数后打 1 条汇总 | 过期记录清理（当前保持静默，见 C） |
| **C 静默-清理** | `Dispose`/`Close`/`Free`/`Cancel`/`Stop` 的 best-effort | 不打（避免二次异常 + 退出噪声） | HikCam 释放链 11 处、MonitorCamManager 3 处、MonitorCamPage 3 处、FormMain 1 处 |
| **D 静默-探测** | 失败本身就是正常结果，且已体现在返回值/回退值里 | 不打（或 `Debug`） | `DescribeAxisDiagnosis` 3 处、`BuildMachineInitSummary` 1 处、帧率探测 1 处 |
| **E 静默-递归** | 位于日志渲染/上色路径，打日志会递归 | 不打（硬约束） | `MainPage.ApplyLineColor`、`MainPage` 追加行重试 |

**未引入节流封装的理由**：逐处核对后，**A/B 级没有一处位于循环或定时线程**（全是一次性失败路径），
因此不需要 `N 秒去重` 封装；`GlobalCommData.ShowLog` 本身已有「同秒同 Tag 同文本只打一次」的抑制。
若将来把 A 级日志下沉到轮询路径，必须先补节流再打。

## 决策二：兼容壳删除的判据

删除前必须同时满足：① 全库引用 = 0（Grep 证据）；② 原实现仍在（转发目标未删）；③ 无外部程序集反射调用。
本轮 `LaserWeldHeadWorkflow` 三项全满足（7 方法 0 调用方，`ProcessControlPage` 全部直调 `MotionControlWorkflow`）。

## 决策三：TODO 处置

| 位置 | 原文 | 判定 | 处置 |
|---|---|---|---|
| `WeldAlgorithmsConfig.cs:348` | `是否按点数分段计算（false 为按距离分段，待实现）` | 真待办（距离分段未实现） | 保留，改写为「true=按点数（已实现）/ false=按距离（待实现，当前不累计不查表）」 |
| `WeldParamAdjustmentAlgorithm.cs:446` | `// TODO: 按距离分段计算模式待实现` | 真待办（该 `else` 分支体为空） | 保留，扩写为现状说明（输出保持上次值、`actionSuccess=false`） |

## 后果

- 温度报警链路仍断（事件从不触发）：另立待决项，见 `.trae/documents/代码清理待决项说明.md`。
- UI 直连 `DeltaMontionAxis`（约 20 处）、UI 线程 70s 忙等仍存在，属「建议修改」待拍板，本轮未动。
