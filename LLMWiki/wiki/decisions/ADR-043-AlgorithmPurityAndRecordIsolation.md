---
title: ADR-043 算法纯净性与记录职责隔离（算法只计算 · 记录归 ProductFileControl · 异步不阻塞）
date: 2026-09-14
tags: [决策, 算法分层, 记录隔离, 事件驱动, 配置合一, WeldParamControl, ProductFileControl, ADR-043, ADR-044]
status: accepted
---

# ADR-043 算法纯净性与记录职责隔离（算法只计算 · 记录归 ProductFileControl · 异步不阻塞）

## 状态

已采纳（2026-09-14）。

> ⚠️ **沿革（2026-09-14 同日）**：本决策「决策 5」新建的 `WeldParamAdjustmentConfig` 类，与既有的 `SeamGuideConfig` 类**当天被合并**为单一 `WeldAlgorithmsConfig`（XML 两节名与文件路径不变，存量配置零迁移），见 [[decisions/ADR-044-WeldAlgorithmsConfigMerge]]。本决策的**其余结论（算法只计算、记录走事件、异步落盘）全部继续有效**，仅「配置类粒度」一项被 ADR-044 收紧。下文出现 `WeldParamAdjustmentConfig` 之处，均按 `WeldAlgorithmsConfig` 理解。

> ⚠️ **沿革（2026-09-14，ADR-046 + ADR-048）**：决策 §7 与「负面 / 待决」中「`ProductFileControl/` 目录名与 `AdaWeldSystem.ProductFileManager` 命名空间暂不一致」**已闭环**——命名空间已统一为 `AdaWeldSystem.ProductFileControl`（ADR-046），且 `Abstractions/` 与 `Records/` 两个子目录**不产生子命名空间**（扁平裁定，ADR-048 §3）。§7 的「暂不一致」表述不再适用，其「只同步 csproj 路径」的操作方式亦随之失效（本轮已改命名空间）。

## 背景

[[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] 确立「算法 = 实现类，由 Manager 持有，配置持久化只归 Manager」后，复查发现**算法仍直接落盘**：

用户 2026-09-14 指出：「`ExecuteAdjustment` 算法和 `SeamTrackingAlgorithm` 应该都不包含记录本地的功能……算法的核心是计算。保存这一个动作由其他模块实现（`ProductFileControl`）。过程中只是触发保存事件去执行（保存动作可能耗时，但是不能影响功能的实现，隔离开控制与记录）。」

复查结论：

| 算法 | 记录/落盘调用 | 判定 |
|---|---|---|
| `WeldParamAdjustmentAlgorithm` | `StoreChartData` 内 `RunRecordManager.Instance.RecordProcessFrame(...)`（每帧）<br>`RecordActionToRunFileRecord` 内 `recordManager.RecordAdjustment(...)`<br>`ExecuteAdjustment` 内 `RunRecordManager.Instance.AbortRecording()` | ⛔ **违规**：算法直接依赖记录模块，并在计算路径上同步调用落盘 |
| `SeamTrackingAlgorithm` | 无（仅 `GlobalCommData.ShowLog`，属横切可观测性） | ✅ 合规，无需修改 |

问题的本质有二：

1. **职责越界**：算法是纯计算单元，记录（尤其**耗时**的记录）属另一模块的职责。算法 `using AdaWeldSystem.ProductFileManager` 使模块依赖反向缠绕（`WeldParamControl` → `ProductFileControl`）。
2. **控制路径被记录路径污染**：落盘发生在计算线程的同步调用栈上，记录一慢就拖慢甚至阻塞控制；且算法要知道「帧索引」这类**记录侧状态**（原代码用 `RunRecordManager.Instance.CurrentFrameIndex`），耦合面继续扩大。

同时，`WeldParamAdjustmentAlgorithm` 的三项运行参数（连续失败阈值、分段方式、每段点数）**硬编码在构造函数内**，未按 [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] 的配置范式由 Manager 统一管理：

```csharp
MaxConsecutiveFailures = 5;
IsCountType = true;
CountNum = 5;
```

（`IsCountType` / `CountNum` 另在 `WeldParamManager` 中重复存了一份，属**配置双份**。）

## 决策

1. **算法只计算，不落盘、不记录**：⛔ 算法实现类内**不得**出现 `RunRecordManager` / `System.IO` / `File.` / `StreamWriter` / `XmlSerializer` 等任何记录或持久化符号。

2. **记录通过事件请求，不通过调用**：算法在需要留痕时**只触发事件**（[事件形态] 三个独立事件）：

   | 事件 | 触发时机 | 载荷 |
   |---|---|---|
   | `FrameRecordRequested` | 每帧计算完成 | `WeldFrameRecordEventArgs`（过程快照 7 项） |
   | `AdjustmentRecordRequested` | 调整成功 | `WeldAdjustmentRecordEventArgs`（继承前者，契约独立演进） |
   | `AbortRecordRequested` | 连续失败超限 | 无载荷（对应 `AbortRecording()` 无参签名） |

   `WeldParamManager` 作为唯一外部入口**透传**这三个事件（显式 `add` / `remove`），外部不得绕过 Manager 直取算法实例订阅。

3. **事件载荷不含记录侧状态**：帧索引（`FrameIndex`）属记录侧，由记录模块自行取用；算法**不感知**帧索引。算法也不构造任何格式化字符串（原 `StringBuilder` 拼 `"SeamWidth=..;FeedSpeed=.."` 属序列化职责，移交记录侧）。

4. **记录的落盘由 `ProductFileControl` 承担，且必须异步**：订阅方**只做入队**（O(1)），真正的落盘在后台执行，**绝不在计算路径上同步落盘**——「保存动作可能耗时，但不能影响功能的实现」。
   > **待办（TODO）**：本轮**不实现**订阅方（`ProductFileControl` 自身结构待一并优化）；订阅方落地前，记录请求事件**无消费者**，过程记录暂缺。产品记录可观测性以 `RunRecordManager` 现状为准。

5. **运行参数改为 Manager 托管的配置结构**（参照 `SeamGuideConfig` 范式）：
   - 新增 `WeldParamControl/WeldParamAdjustmentConfig.cs`，节名 `WELD_PARAM_ADJUST`，与 `SEAM_GUIDE` 同存 `Config/XML/WeldParamControl.xml`；
   - 配置**实例**与**读写器**均由 `WeldParamManager` 独占（`_configFile` 一个 reader 服务两个节）；
   - 对外仅 `AdjustmentConfig` **只读引用** + **无参** `LoadAdjustmentConfig()` / `SaveAdjustmentConfig()`；
   - 算法侧照 `SeamTrackingAlgorithm` 范式：私有 `_config` + 只读 `Config` 属性 + `SetConfig` + `LoadConfig(object)` 转型。

6. **`ExecuteAdjustment` 签名收敛**：去掉 `isCountType` / `countNum` 形参，改从 `Config` 内部读取；保留 `robotX` / `contourPoints` 可选参数。`TriggerAdjustment()` 的**无参契约不变**（[[decisions/ADR-009-WorkflowAsAdjustmentDriver]]）。

7. **`ProductFileManager` → `ProductFileControl` 目录改名只同步 csproj 路径**：命名空间 `AdaWeldSystem.ProductFileManager` 本轮**不动**（用户裁定），故目录名与命名空间暂时不一致（与 `MainDeviceControl/DeviceStateApiCore/` 同类情况）。

## 目录结构（变更后）

```
WeldParamControl/
├── WeldParamData.cs                     数据类集合（含 WeldFrameRecordEventArgs / WeldAdjustmentRecordEventArgs）
├── WeldParamManager.cs                  单例 · 唯一外部入口（配置 + 全部算法实现 + 记录事件透传）
├── SeamGuideConfig.cs                   线激光引导配置（SEAM_GUIDE，Manager 独占）
├── WeldParamAdjustmentConfig.cs         参数调整配置（WELD_PARAM_ADJUST，Manager 独占）★新增
├── Abstractions/
│   └── WeldAlgorithmBase.cs             抽象基类：Name / IsReady / LoadConfig(object) / Reset
└── Algorithms/
    ├── SeamGuideSample.cs               算法私有输入结构
    ├── WeldParamLookupAlgorithm.cs      实现 a：参数查表调整
    ├── WeldParamAdjustmentAlgorithm.cs  实现 b：参数调整（只计算 + 发记录请求事件）★去记录化
    └── SeamTrackingAlgorithm.cs         实现 c：线激光几何轨迹跟踪（本已合规）
```

配置分节（`Config/XML/WeldParamControl.xml`）：

```xml
<Root>
  <SEAM_GUIDE>          ...13 项线激光引导参数...   </SEAM_GUIDE>
  <WELD_PARAM_ADJUST>                               <!-- ★新增 -->
    <MAX_CONSECUTIVE_FAILURES>5</MAX_CONSECUTIVE_FAILURES>
    <IS_COUNT_TYPE>TRUE</IS_COUNT_TYPE>
    <COUNT_NUM>5</COUNT_NUM>
  </WELD_PARAM_ADJUST>
</Root>
```

## 后果

- 正面：
  - 算法恢复为纯计算单元，可独立测试、可脱离记录模块运行；
  - `WeldParamControl` **不再依赖** `ProductFileControl`（原反向 `using` 已删），模块依赖方向单向化；
  - 控制与记录解耦：留痕走事件，落盘由记录侧异步执行，记录变慢不再拖累控制；
  - 记录侧可获得完整结构化快照（不再依赖算法拼字符串）；
  - 三项运行参数纳入统一配置范式，消除 `Manager` 与算法之间的配置双份。
- 负面 / 待决：
  - **记录订阅方未实现（TODO）**：`ProductFileControl` 结构待优化后接入，接入前过程记录缺位；
  - `ProductFileControl/` 目录名与 `AdaWeldSystem.ProductFileManager` 命名空间暂不一致；
  - `LineLaserManager.cs` 内仍有 `RunRecordManager.Instance.AddFrame(e.Cloud)`（**Manager 层**直接落盘，非算法）——本轮未处置，同类问题另议。
- 约束：
  - ⛔ 算法实现类内不得出现任何记录 / 持久化符号；
  - ⛔ 不得在计算路径上同步落盘；订阅方必须入队后异步落盘；
  - ⛔ 外部不得绕过 `WeldParamManager` 订阅算法事件；
  - ⛔ 外部不得 `new WeldParamAdjustmentConfig()` 或持有/回灌配置实例；
  - `ExecuteAdjustment` 不再接收分段参数；`TriggerAdjustment()` 保持无参。

## 相关

- [[decisions/ADR-041-WeldParamControlAlgorithmArchitecture]] — 算法分层（本决策是其「算法纯净性」补充）
- [[decisions/ADR-044-WeldAlgorithmsConfigMerge]] — 焊接算法配置合一（同日收紧本决策「决策 5」的配置类粒度）
- [[decisions/ADR-042-ModuleOrganizationPatternStandard]] — 模块组织范式（H7 配置落盘只归 Manager）
- [[standards/ModuleOrganizationPattern]] — §七检查清单 / §八违规样例
- [[lessons/AlgorithmControlRecordIsolation]] — 本轮踩坑记录
- [[api/WeldParamAdjustmentAlgorithm]] — 参数调整算法 API
- [[api/WeldParamManager]] — Manager 唯一入口（含配置与事件透传）
- [[modules/WeldParamControl]] — 模块说明
- [[modules/ProductFileManager]] — 记录模块（订阅方待办）
- [[decisions/ADR-008-WeldActionRecord]] — 双记录设计（ProcessFrame / WeldParamAdjust）
- [[decisions/ADR-009-WorkflowAsAdjustmentDriver]] — `TriggerAdjustment` 无参契约
