---
title: 英莱（IntelligentLaser）相机开发教训汇总
date: 2026-08-18
updated: 2026-10-30
tags: [教训, 相机, 英莱, IntelligentLaser, 汇总, Job]
status: active
---


# 英莱（IntelligentLaser）相机开发教训汇总
> **章节导航**（本页约 1350 行，超长页请先按章节定位再读）：
>
> - [1. SDK 互操作与结构体](#1-sdk-互操作与结构体)
> - [2. 连接与启动](#2-连接与启动)
> - [3. 回调机制](#3-回调机制)
> - [4. 校准框绘制](#4-校准框绘制)
> - [5. UI 层与状态管理](#5-ui-层与状态管理)
> - [5.7 dwInstanceId 参数陷阱](#57-dwinstanceid-参数陷阱)
> - [6. 委托 GC 保护与 CallbackOnCollectedDelegate](#6-委托-gc-保护与-callbackoncollecteddelegate)
> - [7. Job 体系教训（原三独立 Job 教训页 2026-09-17 并入，§7.1–§7.3）](#7-job-体系教训2026-08-24原三独立页-2026-09-17-并入)
> - [相关页面](#相关页面)
> - [来源](#来源)

本文档汇总英莱（IntelligentLaser）线激光相机在 C# / .NET Framework 4.8 开发过程中踩过的所有坑，按 SDK 互操作、连接启动、回调机制、校准框绘制四大主题归类，便于后续开发快速检索与规避。

---

## 本页已按主题拆分（2026-10-30）

> 原页篇幅过大，按主题拆为下列独立页；本索引页保留抬头与指针。

- [[lessons/IntelligentLaser-Sdk-Interop]]
- [[lessons/IntelligentLaser-Callback-Mechanism]]
- [[lessons/IntelligentLaser-Ui-State]]
- [[lessons/IntelligentLaser-Delegate-Gc]]
- [[lessons/IntelligentLaser-Job-System]]

## 相关页面

- [[index/index]]
