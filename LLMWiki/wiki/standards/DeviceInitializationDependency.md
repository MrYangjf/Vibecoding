---
title: 设备初始化依赖层级与刷新门禁标准
date: 2026-11-09
tags: [规范, 设备初始化, 依赖层级, 三态, 自动刷新, 门禁]
---

# 设备初始化依赖层级与刷新门禁标准（DeviceInitializationDependency）

> **触发**：改动整机初始化顺序、连接重试、初始化汇总、自动刷新开关或刷新按钮可用性时，AI **先读本页再改码**，不自行发明「平级挨个硬试」的写法。
>
> **适用范围**：`MainDeviceControl/DeviceControlWork.cs`（初始化节点驱动与汇总）、`MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs`（三态结果）、`UIDesign/TabPage/SystemControlPage.cs`（刷新开关门禁与刷新执行）。

---

## 一、一句话判据

> **父级没起来，子级连试都不试；跳过不是失败，但必须先修父级。**

---

## 二、依赖层级从哪里来

层级关系**由对象归属与配置驱动**，⛔ 不在初始化流程里另写一份设备清单。

| 层级 | 节点 | 父节点 | 依赖性质 | 代码事实依据 |
|---|---|---|---|---|
| L1 | 机器人通讯 | 无 | 软依赖 | `InitializeRobotComm()` 独立于运控，走 TCP/Socket 通道 |
| L1 | 运动控制器（EtherCAT 主站） | 无 | 根节点 | `MotionControlWorkflow.ConnectOn()` → `MontionManager` 主站句柄 |
| L2 | 焊接头从站 | 运动控制器 | **硬依赖** | `MontionManager.WeldHead` 为主站装载的从站对象；主站未连则从站无总线 |
| L2 | 各运动轴（Y / TA / LA 等从站） | 运动控制器 | **硬依赖** | 轴对象由 `AxisRegistry` 随主站初始化登记，主站未连则 `TryGetAxisReadout` 恒失败 |
| L1 | 线激光相机 | 无 | 软依赖 | `LineLaserWorkflow` 独立 SDK 连接，不经 EtherCAT |
| L1 | 监控相机 | 无 | 软依赖 | `MonitorCamWorkflow` 独立 SDK 连接，不经 EtherCAT |

判据说明：

- **硬依赖**判据 = 子对象的实例由父对象持有/创建，父对象未就绪时子对象连「连接句柄」都不存在。
- **软依赖**判据 = 子对象有独立传输层（TCP / 相机 SDK），父级失败不影响其自身连接能力，只是业务上不可用。
- 新增轴**不需要**改初始化流程：轴从站由 `MontionManager` 内部按 `DeltaMotionConfig` 聚合，父子关系仍是「主站 → 轴」，节点表不动。新增**独立设备**时，只需在 `BuildInitPlan()` 里追加一个 `InitNode` 并声明 `ParentKey`。

---

## 三、四条硬约束

### R1 按层级顺序执行，父失败子跳过

- 初始化必须是**声明式节点表**（`InitNode { Key, ParentKey, Device, Start }`），顺序即执行顺序，父在前。
- 进入节点前先查父节点结果：父结果 **≠ Success** ⇒ 该节点记 **Skipped** 并直接推进，**不得调用 `Start`**、**不得发起连接**。

### R2 三态不许混用

初始化结果只有三种，语义互斥：

| 三态 | 含义 | 计数归属 |
|---|---|---|
| `Success` | 真连上且就绪 | 成功 |
| `Failed` | 真发起过连接且失败/超时 | 失败 |
| `Skipped` | 上级未就绪，**根本没试** | 单列，**不计入失败** |

- 日志、初始化汇总、界面提示三处都必须分开表达。
- `Skipped` 必须写明 `BlockedBy`（被哪个父节点挡住），⛔ 不允许只写「跳过」。
- `Skipped` 与设备运行态 `SubDeviceState` **正交**：⛔ 不给 `SubDeviceState` 增加 `Skipped` 枚举值（会改变公开语义）。

### R3 不用固定等待

- 跳过判定依据是**父级状态**，不是「等一会儿再说」。
- 连接等待沿用既有超时配置（`ROOT/FLOW_TIMEOUT/CASCADE_CONNECT_MS`），⛔ 不新增 `Thread.Sleep` / `Task.Delay`。

### R4 重试要整棵子树重走

- 「初始化」重试时必须复位节点索引与上一轮结果，让整棵子树按层级重走一遍。
- 父级修好后重试，原先 Skipped 的子级必须重新真正尝试连接。

---

## 四、自动刷新门禁

| 约束 | 判据 |
|---|---|
| 默认关闭 | 五个「自动刷新」开关在 Designer 里 `Checked = false`；⛔ 禁止「运控连上就自动置开」 |
| 按设备粒度门禁 | 轴表开关看运控初始化完成；LA / 振镜 / 温度看焊接头从站就绪；TA 看运控完成且 TA 轴已装载 |
| 门禁时机 | 运控状态切换、初始化结束、初始化汇总、轴就绪变化四处事件**统一走同一个门禁方法** |
| 就绪只解冻 | 硬件就绪只恢复 `Enabled`，不自动 `Checked = true`（默认关闭语义不得被绕过） |
| 未就绪不可点 | 对应硬件未初始化成功（含 Skipped）时开关 `Enabled = false`，不给「点了才报错」的机会 |
| 刷新不卡 UI | 定时刷新在后台线程采集纯数据快照，`BeginInvoke` 回 UI 线程只做赋值；单飞标记防堆积 |
| 刷新不绕过父级 | 调试开关打开时同样受门禁约束：子级硬件未就绪，刷新照旧不执行 |

---

## 五、审查判据（脚本对应）

`scripts/csharp_review.py` 已内置两条，改码后必须 0 警告：

| 类别 | 判定 |
|---|---|
| `C.设备初始化分层` | 定义了 `InitializeMachineTick` 的类：必须有 `ParentKey` 门禁、必须落 `DeviceInitOutcome.Skipped`、且 `Skipped` 记录必须在首次 `node.Start` 之前 |
| `B.刷新默认开` | 名称含 `Refresh` 的 Switch 在 `.Designer.cs` 中 `Checked = true` 即警告 |

---

## 六、反例（⛔ 不要再写）

```csharp
// 错：平级硬试——主站都没起来，焊接头还去连一次，白等一个超时
ConnectMotion();
ConnectWeldHead();   // 一定失败，还多花 CascadeConnectMs
ConnectLineLaser();

// 错：把跳过算成失败
if (result != Success) failCount++;

// 错：跳过不写被谁挡住
Log("焊接头 跳过");
```

```csharp
// 对：父级门禁 → 记 Skipped → 直接推进，不发起连接
if (!IsParentSuccess(node))
{
    RecordInitOutcome(node, DeviceInitOutcome.Skipped, parent.DisplayName,
        "被 " + parent.DisplayName + " 挡住 未发起连接");
    AdvanceInitNode();
    return;
}
```

---

## 七、TA 上电后必须回零（2026-11-11）

**规则**：伺服使能 → **满扭矩回零** → 确认到位 → 才允许 `TA_Auto` / `TA_Pose` / `TA_Break` / `TA_Retract`。

- **为什么**：本机 TA 轴按**增量式**使用，代码与配置（`DeltaAxisConfig` / `DeltaTaHomeConfig` / `Motion_XML`）里都没有编码器类型、多圈使能、电池状态参数，也没有上电 reference 流程。因此**上电后驱动器位置寄存器一律不可信**，历史实现「绝对编码器掉电保留位置」的假设不成立，直接 `TA_ZeroPose` 定位到错误坐标正是「回零位置找不对」的根因之一。
- **实现**：`MontionManager.TaHomed`（本次上电是否已回零）由 `WaitAxisHomed` 成功置位、初始化失败重来时清零；**2026-11-17 改版**：`TaAvailable = TaMotionReady ∧ TaHomed`（工作零位到位拆为 `TaAtWorkZero` 只读观测位，**不再是 TA 指令门禁** —— 位置类指令需要的是「位置可信（已回零）」），缺失时 `TaDegradedReason` 给出「TA 未回零（伺服下电后位置不可信，须先完成回零：手动回零或复位回零均可）」。
- ⛔ **回零结论的置位点必须唯一**：所有产生「已回零」的动作走同一实现（手动回零与复位回零共用 `MotionControlWorkflow.TryHomeAxisWithWait`），⛔ 禁让「非阻塞下发」承担需要置位结论的动作（结论无人兑现 ⇒ 手动回零后 TA 指令全被拒）。
- **顺序落点**：回零归**复位入口**（`MotionControlWorkflow.ResetAxesToWorkZero`：需回零轴先 Home 再去工作零位，免回零轴只去工作零位）；初始化只做连接 + 使能（ADR-099），⛔ 初始化不再自动回零（仅 `INIT_RUN_TA_HOME=1` 时走回退路径 `RunTaHomeThenZeroPose`）。
- **回零扭矩**：`DeltaMontionAxis.FullTorqueOnEnable = true`（TA 轴），使能时把 `16#6072` 写成额定上限；CST 目标仍按 `TorqueLimitPerMille` 软件钳制，下压力不受影响。
- **到位判据**：`WaitAxisHomed` 以「期望回零坐标（`HomeOffset`）」比对，不再一律拿 0 当原点；成功后复读一次位置，偏差超容差打日志。
- ⛔ 任何「上电未回零就信任位置」的代码都属违规；发现即标出并按本规则整改。

---

## 八、相关页

- [[standards/CodeSimplification]] §4.1 强制规范条目
- [[architecture/DeviceControlArchitecture]]
- [[modules/DeviceControl]]
- [[modules/MotionControl]]
- [[modules/UIDesign]]
