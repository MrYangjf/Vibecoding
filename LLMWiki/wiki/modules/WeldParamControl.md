---
title: WeldParamControl 模块 — 焊接参数控制与工艺计算
date: 2026-08-28
tags: [模块, 焊接, 工艺, 自适应, 功率, 送丝, 振镜, 焊缝]
source: AdaWeldSystem/WeldParamControl/ + MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs
---

# WeldParamControl 模块 — 焊接参数控制与工艺计算

> 目录 `AdaWeldSystem/WeldParamControl/`，命名空间 `AdaWeldSystem.WeldingData`。
> 负责焊接工艺核心逻辑：焊缝跟踪、自适应参数调整、焊接质量评估。

---

## 核心文件

| 文件 | 职责 |
|---|---|
| `WeldProcess.cs` | 焊接工艺主类（单例）：所有焊接数据结构、参数计算、自适应调整逻辑 |
| `WeldDataManager.cs` | 焊接数据管理器（单例）：集中管理 `AutoParam` / `AutoParamManager` / `ConfigManager` / `CurrentAutoParamId`，INI 持久化当前配置标识 |

> 运控调整相关功能已迁出至 [[modules/MotionControl]]；`WeldProcess` 仅保留 `CurrentRobotX`（真实坐标）与对 `MoveControlData` 的委派。

---

## WeldProcess 内含数据结构

| 类/结构 | 职责 |
|---|---|
| `RobotWeldData` | 机器人焊接数据（坐标、速度、焊接区域） |
| `LaserWeldData` | 激光焊接数据（功率、送丝速度） |
| `MotionWeldPoint` | 焊接点标定（相机坐标系到机器人坐标系转换） |
| `SeamCalData` | 焊缝宽度滑动平均计算器 |
| `AutoParam` | 自动参数配置（含 KVar/JVar 计算） |
| `ChartVar` | 折线图坐标数据 |
| `WeldProcessCompletedEventArgs` | 焊接工艺完成事件参数 |
| `SeamType` | 焊缝种类枚举（None/VType/TType） |

### 关键属性

| 属性 | 说明 |
|---|---|
| `CurrentAutoParam` | 当前自动参数配置（为 null 时无法计算） |
| `CurrentRobotX` | 当前机器人 X 坐标 |
| `CurrentSeamWidth` | 当前焊缝宽度（平滑后） |
| `LaserPowerOutput` | 激光功率输出 |
| `FeedSpeedOutput` | 送丝速度输出 |
| `RobotSpeedOutput` | 焊接速度输出 |
| `ConsecutiveFailureCount` | 连续失败计数 |
| `MaxConsecutiveFailures` | 最大连续失败阈值（默认 5） |

### 内部暂存字段

```csharp
private SeamFeatureResult _lastSeamFeature;   // 最近一帧焊缝特征
private double _lastRobotX;                   // 最近一帧机器人 X 坐标
```
由 `OnAlgorithmCompleted` 赋值，供 `TriggerAdjustment()` 使用。

---

## 触发接口：TriggerAdjustment（无参）

```csharp
public void TriggerAdjustment()
{
    if (CurrentAutoParam != null)
        AutoAction(CurrentAutoParam, IsCountType, CountNum, _lastRobotX,
            _lastSeamFeature != null ? _lastSeamFeature.ContourPoints : null,
            _lastSeamFeature);
}
```

> **重要**：`TriggerAdjustment()` 是**无参**方法。特征值与 RobotX 已由 `OnAlgorithmCompleted` 暂存在 `_lastSeamFeature` / `_lastRobotX`。**不要给它加参数**——这是本模块最容易写错的地方。

内部流程：滑动平滑 → 查找表匹配（送丝速度/焊接速度/激光功率三张表按焊缝宽度匹配）→ 灵敏度判定 → 输出更新。

---

## 焊接工艺控制流程（WeldParamControlWorkflow）

位于 `MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs`，详见 [[modules/DeviceControl]]。

### 定位（易错）

**不是有连接动作的设备**，而是**设备内部控制焊接工艺的一个流程**。

- 输入：机器人信息 + 线激光结果信息
- 计算：焊接功率、送丝速度、振镜摆幅、焊接速度
- 输出：下发给机器人

### 数据链路：焊缝信息即英莱线激光的结果

```
英莱线激光相机取像
  ↓ IlInspectResult 回调直接携带：FeatureY/FeatureZ（特征点）、Width0/Width1（宽度）
LineLaserWorkflow.OnContourFrameReady
  ↓ sf.CenterY = ir.FeatureY
    sf.CenterX = ir.FeatureZ
    sf.SeamWidth = (ir.Width0 + ir.Width1) * 0.5
    sf.SeamArea = ir.Area
PipelineManager.Instance.ReportExternalResult(sf, robotX, null)
  ↓
WeldProcess.OnAlgorithmCompleted → 暂存 _lastSeamFeature / _lastRobotX
  ↓
WeldParamControlWorkflow.ComputeAndOutput()
  ↓ WeldProcess.TriggerAdjustment()  【无参】
WeldParamOutput（功率/送丝/速度/摆幅）→ SendToRobot 下发机器人
```

**关键点**：英莱回调本就含特征点与宽度，链路本就通。`WeldParamControlWorkflow` 补的是「计算后下发到机器人」这一环。

### 私有阶段 → 焊接过程态映射（ADR-034）

**私有阶段枚举** `WeldParamControlWorkflowState`（内联本文件，不对外）：`Uninitialized`(0) / `Initializing`(1) / `Standby`(2) / `Computing`(3) / `Outputting`(4) / `Holding`(5) / `ErrorAborted`(6)

经 `MapWeldStatus(step)` 映射为对外焊接过程态 `SubDeviceWeldStatus`：

| 私有阶段 | 焊接过程态 `SubDeviceWeldStatus` |
|---|---|
| `Uninitialized` / `Standby` | `Standby` |
| `Initializing` / `Computing` / `Outputting` / `Holding` | `Working` |
| `ErrorAborted` | `ErrorAborted` |

> 连接态 `SubDeviceState` 由 `ConnectOn()`/`ConnectOff()` 联动（此处 `Connect` 语义为「工艺参数就绪」）。完整映射表以 [[architecture/DeviceControlArchitecture]] §6 为单一维护点。

### 不入上电级联

**不纳入** `DeviceControlWork.InitializeMachine()` 级联，由 `LineLaserWorkflow` 在连续成功帧达到阈值时触发，保持单一驱动源（[[decisions/ADR-011-WorkflowAsAdjustmentDriver]]）。

---

## 振镜摆幅：待实现（查表项，非公式）

`CalcGalvoAmplitude` 当前 TODO 占位返回 `0.0`。

`WeaveWidth`（振镜摆幅）与焊缝宽度关联（焊缝越宽 → 摆动宽度越大），规划为 **`AutoParamManager` 中的分段查找表**，与送丝速度/焊接速度/激光功率三张表同样的匹配方式落地。

> **反例警示**：不要用自创公式（如 `(SeamWidth - LaserDiameter) / 2`）代替查表——那是未经验证的推导，不是项目既定的匹配方式。

---

## 关联

- [[modules/DeviceControl]] — `WeldParamControlWorkflow` 所属架构
- [[architecture/DeviceControlArchitecture]] — 架构规范页（含完整数据链路）
- [[api/WeldDataManager]] — 焊接数据管理器 API
- [[decisions/ADR-011-WorkflowAsAdjustmentDriver]] — 工作流作为调整主驱动
- [[modules/LineLaserCam]] — 英莱线激光，焊缝信息源头
- [[modules/EmguALG]] — 算法管道，承载 `SeamFeatureResult` 上报
