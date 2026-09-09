> ⛔ **机制失效标注（2026-09-09 治理，ADR-027/029）**：本页针对的旧「设备状态机模板方法 + TryTransition」机制已随四态模型删除（现行 = 三态模型非泛型基类，`SetState`/`SetWeldStatus` 唯一写入入口）。**「同一状态转换不要两层各转一次」的思想仍有效**，落点变为：工作流层不得绕过基类手工给 `State`/`WeldStatus` 赋值。

# 教训：状态机重复转换

> **历史语境注记（2026-09-02，ADR-028）**：本页记录的是**已删除的旧架构**——`DeviceStateMachine/` 目录、`DeviceStateMachineBase` 模板方法、`_deviceStateMachine` 字段、`DeviceState` 四态枚举均已不复存在（2026-08-28 起）。现行状态由 `MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs` 承载三态模型，写入唯一入口为 `SetState`/`SetWeldStatus`/`SetStatus`。
> **本页保留的通用教训**：同一目标状态被两层代码各自推进一次 → 第二次命中非法转换守卫。**该反模式在三态模型下依然存在**（例如基类 `ConnectOn()` 与子类 `FlowProcess()` 都调 `SetState(Connected)`），规避动作不变：状态推进只允许一处负责。

## 现象

初始化日志中出现 `非法状态转换: Initializing -> Initializing`，随后初始化立即失败，设备状态停留在 `Initializing` 而无法进入 `Standby`。

## 根因

工作流层（`LineLaserWorkflow.Initialize()` / `InitializeSync()`）手动调用了一次 `_deviceStateMachine.TryTransition(DeviceState.Initializing, ...)`，而设备状态机模板方法 `_deviceStateMachine.Initialize()` 内部第一步也会调用 `TryTransition(DeviceState.Initializing, ...)`。两次转换同一个目标状态，第二次必然命中"非法状态转换"守卫，`Initialize()` 直接返回 false。

```
工作流层:  TryTransition(Initializing)   → 成功  Uninitialized → Initializing
模板方法:  TryTransition(Initializing)   → 失败  Initializing → Initializing（非法）
          Initialize() 返回 false        → 初始化失败
```

## 修复

移除工作流层的重复 `TryTransition(Initializing)` 调用。设备状态机的 `Initializing → 四步初始化 → Standby/Alarm` 完整流程统一由 `DeviceInitializationStateMachineBase.Initialize()` 模板方法负责，工作流层只需要转换自己的工作流状态（`LineLaserWorkflowState`）。

**正确模式**：
```csharp
// 工作流层：只管工作流状态机
TransitionTo(LineLaserWorkflowState.Initializing);
// 设备状态机的 Initializing 转换由模板方法内部负责
InitializeWorker();  // 内部调 _deviceStateMachine.Initialize(...)
```

## 预防措施

1. **职责分层**：工作流状态机（WorkflowState）和设备状态机（DeviceState）各司其职，工作流层不要越俎代庖操作设备状态机的初始化转换。
2. **代码审查**：新增初始化入口方法时，检查是否存在重复的状态转换。
3. **错误日志定位**：看到 `非法状态转换: X -> X` 时，第一反应就是找重复的 `TryTransition(X)` 调用。

## 相关页面

- [[modules/DeviceControl]]
- [[modules/IntelligentLaserCam]]
- [[modules/DeviceControl]]
