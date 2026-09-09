---
title: ADR-040 线激光相机访问统一收口（Manager 持有实例 + 外设代理 + 辅助类归并）
date: 2026-09-08
status: accepted
tags: [决策, 线激光, 相机, 管理器, 单一入口, 抽象契约, ADR-040]
---

# ADR-040 线激光相机访问统一收口

## 背景

ADR-038/039 建成三层结构后，代码里仍残留三类「绕过管理器」的写法：

1. **工作流直接持有厂商实例**：`LineLaserWorkflow` 有 `private IntelligentLaserCam _ilCamera`，
   并以 `Active as IntelligentLaserCam` 转型后调 `ConnectManual` / `SetLaser` / `SetSensor`。
   这使工作流与单一厂商绑死——换成虚拟相机时 `_ilCamera` 变 null，逻辑退化成「跳过外设」，
   抽象层的互换性名存实亡。
2. **实现层自持实例**：与运控的台达实现层（`DeltaEtherCAT/` 无实例、实例注册进 `MontionManager`）
   不一致——线激光这边多处自行 `new` 或转型取实例。
3. **辅助类过度拆分**：`ProfileSnapshot` / `ProfileMatRenderer` / `SeamPvtFeeder` 三个类
   各自单独立文件，但它们**只被 `LineLaserManager` 一个消费者使用**，文件数虚增。

同时本轮排查出两个真实缺陷：`LineLaserResultEventArgs.HasValidResult` 不存在（编译报错），
以及**工作流从未调用 `StartAcquisition`**（相机连上也不出图，`PreWork` 必然等待数据稳定超时）。

## 决策

**D1 相机实例唯一持有者 = `LineLaserManager`**
管理器新增两个按类型的访问器：`IntelligentLaser` / `VirtualCamera`，
首次访问时创建 + `Register` 登记 + 套用配置。**厂商实现层不对外暴露实例**。
需要厂商专属能力的地方（英莱调试页 `ILCamPage` / `ILParamForm` / `ILAlgorithmEditForm`）
一律写 `LineLaserManager.Instance.IntelligentLaser`，**禁止** `Active as IntelligentLaserCam`。

**D2 外设操作由管理器代理，抽象层补虚契约**
`LineLaserCameraBase` 新增 7 个 `public virtual` 默认实现（与运控「加契约给默认实现」同法）：
`ConnectManual` / `DisconnectManual` / `ConfigureDefaultCommPeriod` / `IsCameraOn` /
`IsLaserOn` / `SetSensor` / `SetLaser`。默认实现为「不支持则告警返回 false / 空操作 / 返回 true」，
英莱与虚拟各自 `override`。
管理器对外提供 `Connect` / `Disconnect` / `ConfigureDefaultCommPeriod` / `IsCameraOn` /
`IsLaserOn` / `SetSensor` / `SetLaser` / `ShutdownPeripherals` 八个代理方法。
**工作流与流程层不再接触相机对象**，相机生命周期也归管理器（工作流 `Dispose` 不再 `Dispose` 相机）。

**D3 三个辅助类归并进 `LineLaserManager.cs`**
`ProfileSnapshot` / `ProfileMatRenderer` / `SeamPvtFeeder` 仍是独立类（不合并成一个），
但与管理器同驻一个文件，删除三个 `.cs` 并撤下 `.csproj` 登记。
理由：它们只有一个消费者，单独立文件只会制造跳转成本；保留独立类则保住职责边界与可测试性。

**D4 类名回归文件名**
英莱实现类 `IntelligentLaserCameraRun` → `IntelligentLaserCam`，与文件 `IntelligentLaserCam.cs`
及目录同名（虚拟侧 `VirtualCam` 已在此前完成同样对齐）。

**D5 补两处缺陷**
- `LineLaserWorkflow` 中 `e.HasValidResult` → `e.Result.Valid`（事件参数无此属性，编译报错）；
- `DoPreWorkOn` 补 `LineLaserManager.Instance.StartAcquisition()`——此前工作流只连相机不启动采集，
  相机不出图，`PreWork` 必然超时失败；
- 虚拟相机补模拟节拍：`SensorRunContinue()` 起 33ms（≈30Hz）定时器持续产帧，`SensorStop`/`Dispose` 停表。
  此前每次调用只产一帧，`PreWork` 凑不满 5 帧稳定判据。

## 影响面

| 文件 | 变更 |
|---|---|
| `LineLaserCam/ILineLaser/LineLaserCameraBase.cs` | 新增「外设虚契约」7 个 `public virtual` |
| `LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs` | 类名回归 + 7 个方法加 `override` |
| `LineLaserCam/VirtualCam/VirtualCam.cs` | `override` 5 个外设契约 + 模拟节拍定时器 |
| `LineLaserCam/LineLaserManager.cs` | 内嵌三辅助类 + 类型访问器 + 外设代理（现役 4 类同文件） |
| `LineLaserCam/ProfileSnapshot.cs` / `ProfileMatRenderer.cs` / `SeamPvtFeeder.cs` | **删除**（归并） |
| `MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs` | 去 `_ilCamera`，全走 Manager；修 `HasValidResult`；补启动采集 |
| `MainDeviceControl/DeviceControlWork.cs` | `Active as VirtualCam` → `Instance.VirtualCamera` |
| `UIDesign/TabPage/ILCamPage.cs`、`SubDialog/IntelligentLaserDialog/ILAlgorithmEditForm.cs` | `Active as IntelligentLaserCam` → `Instance.IntelligentLaser` |

## 约束（后续必须遵守）

- 业务与流程层**禁止**出现 `IntelligentLaserCam` / `VirtualCam` 的 `new` 与 `as` 转型；
- 新增相机能力优先加在**抽象层**并用 `public virtual` 给默认实现，派生类可暂不实现；
- 只有一个消费者的辅助类不再单独立文件，与消费者同文件但保持独立类。

## 关联

- 上游：[[decisions/ADR-038-LineLaserThreeLayerRefactor]]、[[decisions/ADR-039-LineLaserResponsibilitySplit]]
- 模块：[[modules/LineLaserCam]]、[[modules/VirtualCam]]
- API：[[api/LineLaserManager]]、[[api/IntelligentLaserCam]]、[[api/VirtualCam]]
- 参照范式：[[modules/MotionControl]]（台达实现层无实例、实例注册进 `MontionManager`）
