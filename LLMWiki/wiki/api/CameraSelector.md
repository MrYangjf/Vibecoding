---
title: CameraSelector API 参考（英莱默认 + 虚拟调试二选一）
date: 2026-09-03
tags: [API, 相机, 选择]
source: AdaWeldSystem/LineLaserCam/Api/CameraSelector.cs
---

# CameraSelector API 参考

> 相机选择器静态类，位于 `LineLaserCam/Api/CameraSelector.cs`（与 `ICameraRun` 同处线激光相机族统一对外接口层），命名空间 `AdaWeldSystem.LineLaserCamApi`（与 Api 目录对齐，统一对外接口层命名空间）。
> 维护当前激活的 `ICameraRun`（英莱真实 / 虚拟调试），工作流与界面经 `CameraSelector.Active` 取相机，无需关心具体类型。
> 同时聚合「线激光相机连接态」与「相机种类」（见 [[decisions/ADR-015-CameraConnectionStateDecoupled]]）。

> ⚠️ **2026-09-03 据代码事实重写**：本页原记录了 `Load()` / `Save()` / `DetectConnection()` / `SelectReal()` 四个成员，**均已从代码中移除**（源自 2026-08-26「渐进式启动与子页懒加载」决策中**唯一被保留**的相机选择器简化项，该决策页已按用户裁定删除）。
> 现行设计是**「英莱默认 + 虚拟调试」二选一、一步到达**——`Active` 首次访问即自动 `SelectIntelligentLaser()`，**无需启动加载、无需连通性检测、无配置持久化**。

## 成员（现行）

| 成员 | 说明 |
|------|------|
| `bool IsVirtual { get; }` | 当前是否使用虚拟调试相机（私有 setter，仅由两个 `SelectXxx()` 设置） |
| `ICameraRun Active { get; }` | 当前激活相机。**惰性创建**：`_active == null` 时自动调 `SelectIntelligentLaser()`，故首次访问即拿到可用实例 |
| `CameraKind Kind { get; }` | 当前相机种类，**只读**；默认 `IntelligentLaser`，仅能经 `SelectVirtual()` / `SelectIntelligentLaser()` 变更 |
| `LineLaserCameraConnectionState ConnectionState { get; }` | 线激光相机连接状态（连接/断开/工作中），与工作流程状态相互独立 |
| `void SetWorking(bool)` | 由工作流驱动：采集开始置 true（→`Working`），结束置 false（→回退派生态） |
| `void SelectVirtual()` | 创建并激活 `VirtualCameraRun`；置 `Kind=Virtual`、`IsVirtual=true` |
| `void SelectIntelligentLaser()` | 创建并激活 `IntelligentLaserCameraRun`；置 `Kind=IntelligentLaser`、`IsVirtual=false`（**默认路径**） |

### 已移除成员（2026-08-26 起，勿再引用或编写调用）

| 成员 | 移除原因 |
|------|----------|
| `void SelectReal()` | 真实相机收敛为英莱单一实现，由 `SelectIntelligentLaser()` 取代 |
| `void Load()` | 取消启动配置恢复，改为英莱默认一步到达 |
| `void Save()` | 取消相机选择持久化（`Config/INI/CameraSelector.ini` 不再读写） |
| `void DetectConnection()` | 取消启动连通性检测，连接态改为由硬件事实派生 |

## 枚举（定义于 `LineLaserCam/Api/ICameraRun.cs`）

```csharp
// 相机自身连接状态（与工作流程状态相互独立）
public enum LineLaserCameraConnectionState
{
    Disconnected,  // 未连接（无相机或连接失败）
    Connected,     // 已连接，空闲待命
    Working        // 已连接且正在采集/出图中（工作流处于采集态）
}

// 当前配置的相机种类
public enum CameraKind
{
    None = 0,             // 未配置相机
    SmartRay = 1,         // SmartRay 工业 3D 线激光（枚举值保留，当前实现未使用）
    Hik = 2,              // 海康机器人 3D 线激光（枚举值保留，当前实现未使用）
    Virtual = 3,          // 虚拟调试相机
    IntelligentLaser = 4  // 英莱(IntelligentLaser) 工业 3D 线激光（真实，默认）
}
```

> ⚠️ `CameraKind` 仍保留 `SmartRay` / `Hik` 两个枚举值，但 `CameraSelector` 的选择方法与连接态派生**均不处理**这两个分支（`switch` 的 `default` 一律返回 `Disconnected`）。
> ⚠️ `ICameraRun.cs` 中该枚举的 XML 注释仍写「当前工作流实际只接入 Virtual 与 SmartRay」，**已过时**（现为 Virtual 与 IntelligentLaser），属代码注释 drift，待随改码批次一并修正。

## 连接状态模型

> `ConnectionState` 是派生值，**不**由相机自己设置，而是由 `CameraSelector` 聚合：
> - `_working == true` → `Working`（仅 `SetWorking(true)` 驱动，调用方为工作流）。
> - 否则按 `Kind` 派生：
>   - `None` → `Disconnected`
>   - `Virtual` → `Connected`（始终可用；UI 据 `ConnectionState` 再区分「虚拟相机工作中」/「虚拟相机（待启用）」）
>   - `IntelligentLaser` → `_intelligentInstance != null && _intelligentInstance.IsConnected ? Connected : Disconnected`
>   - 其余（`SmartRay` / `Hik`）→ `default` 分支返回 `Disconnected`
>
> ⚠️ 相机连接态**只表达硬件事实**，不感知工作流语义；工作流只通过 `SetWorking` 影响「工作中」这一态。

## 启动检测与配置持久化 —— 均已取消

> ⛔ **本节所述机制现已整体移除**，保留仅作历史沿革，**勿据以改码**。
> 原设计：`FormMain` 构造期先 `CameraSelector.Load()` 从 `Config/INI/CameraSelector.ini`（节 `[Camera]`，键 `IsVirtual` / `Type`）恢复相机选择，再 `DetectConnection()` 按种类做连通性检测（SmartRay→`OpenSensor`、Hik→`OpenSensorByIP`、IntelligentLaser→`OpenSensor`，IP 均硬编码）。
> 现设计：**无需任何启动前调用**。`Active` 惰性创建英莱实例即可用，连接态随硬件事实派生，连接失败只表现为「未连接」，不阻塞启动。

## 使用

- `LineLaserWorkflow` / `MotionControlWorkflow` 取图经 `CameraSelector.Active`（未显式选择时自动为英莱相机实例）。
- 流程出图前后由工作流调 `CameraSelector.SetWorking(true/false)` 驱动「工作中」连接态。
- 需要虚拟调试时显式调用 `CameraSelector.SelectVirtual()`；恢复真实相机调 `SelectIntelligentLaser()`。

> 真实相机实现为 `IntelligentLaserCameraRun`（英莱），虚拟相机实现为 `VirtualCameraRun`，二者均实现 [[api/ICameraRun]]。

---

*来源：`AdaWeldSystem/LineLaserCam/Api/CameraSelector.cs` — 2026-09-03 据代码事实重写*
