---
title: UI 状态判断与控制精简规范
date: 2026-08-24
tags: [规范, UI, 代码精简, 状态管理, 真相源]
status: accepted
---

# UI 状态判断与控制精简规范

> **用途**：本页是「UI 状态判断与控制精简」需求的**唯一标准源**，与 [[standards/CodeSimplification]]（ADR-023，覆盖除 `*.Designer.cs` 外的全部业务源码、含 `UIDesign/` 非设计器 `.cs` 五维度）互补——ADR-023 已覆盖 `UIDesign/` 非设计器 `.cs` 的 ①②⑤ 维度（成员排序/变量/辅助函数）与 ③④（枚举事件/逻辑），本页专门补上 `UIDesign/` 的**状态判断与控制细则**（禁本地 bool 缓存设备态/单一控制函数/统一刷新入口/集中状态标签）。触发此类需求时，AI 直接读取本页执行。
> **适用范围**：`UIDesign/` 全部 WinForms/AntdUI 代码。

---

## 一、UI 状态精简四原则

### ① 真相源唯一（最核心）
- UI 状态**一律从权威来源读取**，不得在本页维护本地 bool 副本：
  - 设备连接/开关态 → 设备的 `IsXxx()` 方法（`IsConnected` / `IsLaserOn()` / `IsCameraOn()`）；
  - 设备/整线状态 → 状态机（`LineLaserWorkflow.Instance.StateMachine.IsConnected` / `State`）。
- ❌ 禁止形如 `_isConnected` / `_isLaserOn` / `_isCameraOn` 的本地缓存字段（会与硬件真相脱节，尤其「上次异常退出未关硬件」场景）。
- 读取时机：每次需要判断时**直接读**；不要「构造时读一次存字段、之后多处用字段」。
- **设备层状态本地化（2026-08-25 补充，英莱案例）**：硬件查询有延迟（点击后立即读旧值导致按钮越点越乱）时，**允许将状态下沉到设备层**（如 `IntelligentLaserCameraRun._isLaserOn/_isCameraOn`）：连接成功时 `SyncHardwareStatus()` 从硬件同步一次（"第一次正确"），`SetXxx` 操作成功后本地更新；UI 层仍只读设备的 `IsXxx()` 属性，**不新增 UI 层副本**——原则①针对的是 UI 层，设备层维护同步状态是合法的真相源实现。详见 [[lessons/IntelligentLaserSensorControl]]。

### ② 单一控制函数（按钮 text / 使能 / ExtraMouseDown）
- 同一组按钮的 text、`ExtraMouseDown`、Enabled 等视觉状态，**收敛到一个控制函数**，所有入口（按钮点击 / 状态机回调 / 硬件同步 / 连接态刷新）都调它，消除多函数块重复 set text。
- 范例：
  - `ILCamPage.UpdateLaserSensorUi()` — 激光/传感器按钮 text 与 `ExtraMouseDown` 统一控制（基于 `IsLaserOn()` / `IsCameraOn()`）。
  - `MotionControlPage.SetSimButtonMode(SimButtonMode)` — 模拟流程按钮 text（开启/停止/清理异常）集中控制。

### ③ 统一刷新入口
- 页面有多个状态变更碎片（连接态 / 模式 / 硬件同步）时，收敛为**单入口** + `[Flags]` 枚举组合范围，消除嵌套调用与隐式刷新顺序依赖。
- 范例：`ILCamPage.RefreshUi(RefreshUiScope scope)`（`Connection` / `Mode` / `Hardware` 可组合，内置 `InvokeRequired` 封送），旧碎片函数降级为 `private *Core` 仅被它调用。

### ④ 集中状态标签
- 连接 / 设备状态标签（如 `lblConn` / `lbl_LineLaserConn`）由**单一方法**统一刷新，不在多个事件处理里散写 text + ForeColor。
- 范例：`FormMain.UpdateDeviceStatus()` 集中刷新全部设备连接状态标签。

---

## 二、红灯清单（命中即修）

| 反模式 | 示例 | 修法 |
|--------|------|------|
| 本地 bool 缓存设备态 | `private bool _ilConnected;` + 多处读写 | 删字段，改 `_ilCamera != null && _ilCamera.IsConnected` 直读 |
| 同组按钮 text 在 2+ 函数重复 set | `btnX.Text = on ? "关" : "开"` 出现在点击+同步+刷新三处 | 抽 `UpdateXxxUi()` 单一控制 |
| 状态标签散写多个事件 | `lblConn.Text=...` 在 3 个回调各写一遍 | 抽 `UpdateXxxStatus()` 统一刷 |
| 调用处重复函数体的判定 | 函数已判 `IsConnected`，调用方又判一遍再 set text | 调用方只调统一控制函数 |

---

## 三、与其他规范的边界

| 已有约束 | 关系 |
|---|---|
| [[standards/CodeSimplification]] / [[decisions/ADR-025-CodeSimplificationStandard]] | 互补：ADR-023 覆盖除 `*.Designer.cs` 外的全部业务源码（含 `UIDesign/` 非设计器 `.cs` 五维度），本页专补 `UIDesign/` 状态判断与控制细则 |
| [[decisions/ADR-002-CS73-Constraint]] | 精简后仍须 C# 7.3 语法 |
| [[decisions/ADR-001-DisposePattern]] / [[decisions/ADR-023-DisposePatternFullCoverage]] | 精简**不得**新增/重写 `Dispose(bool)` |
| 公共接口契约 | 精简**不得**改变公共类型/方法签名 |

---

## 四、已落地案例

| 日期 | 文件 | 改动 |
|------|------|------|
| 2026-08-25 | `LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs` | 设备层状态本地化：`IsLaserOn()`/`IsCameraOn()` 改本地状态（连接时 `SyncHardwareStatus` 同步一次 + `SetLaser`/`SetSensor` 本地更新），删 `IlHardwareStatus` 快照/`_isRunning`/`_isOpened`；UI 读取无延迟 |
| 2026-08-25 | `UIDesign/TabPage/ILCamPage.cs` | 连接态改 `_ilCamera.IsConnected` 设备真相源（独立调试页不依赖工作流状态机）；构造函数/连接成功/自动模式切换仅同步一次硬件 |
| 2026-08-24 | `UIDesign/TabPage/ILCamPage.cs` | 删 `_isLaserOn`/`_isCameraOn`，激光/传感器按钮 text 收敛到 `UpdateLaserSensorUi()`；`RefreshUi(RefreshUiScope)` 统一刷新入口 |
| 2026-08-24 | `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs` | 删 `_ilConnected` 缓存，4 处改直读 `IsConnected` |
| 2026-08-24 | `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs` | 删 `_ilConnected` 缓存，`UpdateConnLabel`/`LoadParams`/按钮守卫改直读 `IsConnected` |
| 参照（好范式，保留） | `UIDesign/TabPage/MotionControlPage.cs` | `SetSimButtonMode()` 已集中控制按钮 text |
| 参照（好范式，保留） | `UIDesign/MainWindow/FormMain.cs` | `UpdateDeviceStatus()` 已集中刷新状态标签 |
| 保留（合理本地态，非真相源副本） | `MonitorCamPage._isMonitoring` / `EmguAlgoPage._loading` / `NavPage._syncing` / `CommPage._isLogVisible` / `FileTraceForm._selected` | 本地 UI 活动/选择/可见性标志，不重复外部真相源，保留 |
