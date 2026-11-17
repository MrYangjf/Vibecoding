---
title: 算法纯净性与记录职责隔离
date: 2026-09-14
updated: 2026-10-30
tags: [教训, 算法分层, 记录隔离, 事件驱动, 配置合一, WeldParamControl, ProductFileControl, ADR-033, ADR-043]
status: active
---

# 算法纯净性与记录职责隔离

## 坑

**算法实现类里直接调用记录/持久化模块**，把「计算」和「记录」两件事塞进同一条调用链。

2026-09-14 实例：`WeldParamAdjustmentAlgorithm` 内有 3 处直接落盘调用——

```csharp
// StoreChartData 内（每帧）
RunRecordManager.Instance.RecordProcessFrame(
    RunRecordManager.Instance.CurrentFrameIndex, robotX, ...);
// RecordActionToRunFileRecord 内
recordManager.RecordAdjustment(frameIndex, robotX, ..., paramBuilder.ToString());
// ExecuteAdjustment 内（连续失败超限）
RunRecordManager.Instance.AbortRecording();
```

## 三重危害

| # | 危害 | 说明 |
|---|---|---|
| 1 | **职责越界** | 算法是纯计算单元；记录（尤其耗时记录）是另一模块的职责。算法 `using AdaWeldSystem.ProductFileManager` 让模块依赖反向缠绕 |
| 2 | **控制被记录拖累** | 落盘在计算线程的同步调用栈上，记录一慢就拖慢甚至阻塞控制。「保存动作可能耗时，但不能影响功能的实现」 |
| 3 | **耦合面扩大** | 算法为了写记录，被迫感知**记录侧状态**（原代码用 `RunRecordManager.Instance.CurrentFrameIndex` 取帧索引），双方越缠越紧 |

顺带的**配置双份**：同一组运行参数在 `Manager` 与算法里各存一份（`IsCountType` / `CountNum`）。

## 正解

### 1. 算法只计算，不落盘

⛔ 算法实现类内**不得**出现 `RunRecordManager` / `ProductFileControl` / `System.IO` / `File.` / `StreamWriter` / `XmlSerializer`。

判据（可脚本化）：对算法文件剥掉注释后 Grep 上述符号，命中即违规。

### 2. 记录走事件请求，不走调用

算法只**触发事件**，落盘由记录模块订阅后执行：

| 事件 | 时机 | 载荷 |
|---|---|---|
| `FrameRecordRequested` | 每帧 | `WeldFrameRecordEventArgs` |
| `AdjustmentRecordRequested` | 调整成功 | `WeldAdjustmentRecordEventArgs` |
| `AbortRecordRequested` | 连续失败超限 | 无载荷 |

事件由 Manager **透传**（显式 `add`/`remove`），外部不得绕过 Manager 直取算法实例订阅。

### 3. 载荷不含记录侧状态，不构造格式化字符串

帧索引属记录侧，**由记录模块自己取**；算法不感知。原 `StringBuilder` 拼 `"SeamWidth=..;FeedSpeed=.."` 属序列化职责，一并移交记录侧。

### 4. 订阅方只入队，落盘在后台

「保存动作可能耗时，但不能影响功能的实现」——订阅方必须**入队即返回**（O(1)），真正落盘在后台执行，**绝不在计算路径上同步落盘**。

> ✅ 2026-09-14 落地状态：**订阅方已实现**——`ProductFileRecordManager` 构造时订阅三事件，事件处理器组装 item 后入队（O(1)），落盘由记录类后台线程异步执行（ADR-031（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]））。过程记录链路已闭环。

### 5. 运行参数走 Manager 独占配置（照 `WeldAlgorithmsConfig` 范式）

算法内硬编码的运行参数必须外提为配置类：

- 配置类只负责「把自己序列化成给定 reader」（`LoadConfig(reader)` / `SaveConfig(reader)`），**不自持 reader**；
- reader 的创建与持有归 **Manager**；
- 对外只暴露 `Manager.<X>Config` **只读引用** + **无参** `Load<X>Config()` / `Save<X>Config()`；
- 算法侧照 `SeamTrackingAlgorithm`：私有 `_config` + 只读 `Config` 属性 + `SetConfig` + `LoadConfig(object)` 转型。

多个配置节可共用**同一个 reader / 同一个文件**（`Config/WeldParamControl/Algorithm_XML/WeldParamControl.xml` 下 `SEAM_GUIDE` 与 `WELD_PARAM_ADJUST` 并存）；进一步地，**多个节也可归属于同一个配置类**——2026-09-14 两个算法配置类即合并为单一 `WeldAlgorithmsConfig`（同文件、同节名不变 → 存量配置**零迁移**），Manager 只持一个实例、只留一对无参 Load/Save。**判据：配置类的划分粒度应跟随「谁写盘」而非「字段分几组」——落盘只归 Manager 时，多节合一比多类并列更少歧义。**（ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]））

## 同类问题（未处置）

`LineLaserManager.cs` 内仍有 `RunRecordManager.Instance.AddFrame(e.Cloud)`——属 **Manager 层**直接落盘（不是算法）。同一原则是否适用于 Manager 层，另议。

## 相关

- ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 本轮决策
- [[decisions/ADR-043-WeldParamControlConsolidated|ADR-043（焊缝参数控制综合）]] — 算法分层
- ADR-043（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） — 焊接算法配置合一（`WeldAlgorithmsConfig`）
- [[decisions/ADR-006-ModuleOrganizationPatternStandard]] — 模块组织范式
- [[standards/ModuleOrganizationPattern]] — §七检查清单 / §八违规样例
- [[api/WeldParamAdjustmentAlgorithm]] — 参数调整算法（去记录化后）
- [[modules/ProductFileManager]] — 记录模块（订阅方已落地，ADR-031）
- [[lessons/WikiDriftCorrectionPitfalls]] — 知识库维护踩坑
## 相关页面

- [[index/index]]
