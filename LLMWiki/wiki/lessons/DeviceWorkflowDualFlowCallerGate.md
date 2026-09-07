---
title: 设备工作流调用方入口红线
date: 2026-09-01
updated: 2026-09-02
tags: [教训, 工作流, 调用方, ConnectOn, ConnectOff, ADR-028]
status: active
---

# 设备工作流调用方入口红线

## 坑

驱动任一 `DeviceWorkflowBase` 子类（各子设备工作流）时，
**必须走基类提供的公共入口**，禁止直接调子类自身暴露的同名便捷方法：

| 应调用（基类入口） | 禁止调用（子类内部方法） | 后果 |
|---|---|---|
| `ConnectOn()`（开启连接，public abstract，受理式，UI 直调） | 内部编排方法（如连接后台线程方法） | 绕过受理式置态与连接语义 |
| `ConnectOff()`（断开连接，public abstract，UI 直调） | 内部断开方法 | 绕过断开置态语义 |
| `ResetProcess()`（流程复位） | 子类自有便捷方法 | 复位口径不一致 |
| `ClearStatus()`（清报警回待机） | 子类自有便捷方法 | 报警态清理遗漏 |

> **⚠️ 2026-09-03 机制变更（ADR-030，用户裁定「完全重构」）**：
> ① 「自动运行由**常驻监听线程**驱动」已废止（裁定 C1）——子流程**无自带线程**，改由 `DeviceControlWork` 的 7 条常驻线程驱动 `FlowProcess()`；
> ② `ConnectOn()` / `ConnectOff()` 现归**非阻塞组**（非常驻后台线程，动作即退出释放）；新原档另有一组**阻塞**接口
> `InitializeOn()`（同步等待）/ `InitializeOff()`（异步等待），**两组并存不重叠**（裁定 C4，架构页 §4.4）；
> ③ 「后台线程由子类内部自起」同样废止——子类不起线程。
> **本页「必须走基类公共入口、禁止直调子类便捷方法」的红线本身继续有效**，且新增：禁止直调 `InitializeOn/Off`。
> 现行规范见 [[architecture/DeviceControlArchitecture]] §4.2 · §4.3 · §4.4 · §7.2。
>
> ~~自动运行无独立入口：自动运行 = 仅 `FlowProcess()`，由常驻监听线程驱动；~~
> **自动运行 = 仅 `FlowProcess()`，由 `DeviceControlWork` 的常驻线程驱动**；
> 主设备 `DeviceControlWork` 在其单步分派中级联子设备（如启动焊接步内 `_lineLaser` 相应动作）。

`ConnectOn()`/`ConnectOff()` 为 `public abstract`，是连接/断开的唯一契约，**界面 UI 开关按钮直调**，后台线程由子类内部自起（基类不包线程、不设看门狗）。直接调子类内部方法会跳过受理式置位。

## 踩坑实录

- 2026-09-01 审计：顶层调用方 `FormMain.cs` 曾直接调 `PowerOnInitialize()` + `Start()`，绕过基类入口。
- 2026-09-02 收敛：`PowerOnInitialize` 收敛为私有初始化编排（自动初始化共用实现），外部无第三入口。
- 2026-09-02 再收敛：删除「手动初始化/反初始化」`BeginManualInit`/`BeginManualUnInit`，仅保留「手动连接/断开」入口（升抽象）。
- 2026-09-02 三度收敛：删除基类 `ManualStart`/`ManualStop` 中间包装（原「基类起线程再调子类」线程套线程、流程套流程）；连接/断开升为 `public abstract`，后台线程由子类内部自起，UI 按钮直调。
- 2026-09-02 ADR-028 三态模型定稿：基类泛型 `DeviceWorkflowBase<TStep>` 删除，连接/断开入口定名 **`ConnectOn()`/`ConnectOff()`**（原 `ManualOn`/`ManualOff` 废止）；初始化/启动收口为 `DeviceControlWork.InitializeMachine()` / `StartMachine()`。
- 2026-09-01 同轮修正 `MotionControlPage.cs`：**越权直驱非所属设备**——直接调 `LineLaserWorkflow.Instance` 的初始化/启停方法
  （线激光属线激光/ILCamPage 边界，且其模拟生命周期应由主设备统一编排）。
  已将线激光模拟启动/停止/复位上收至 `DeviceControlWork`（见 ADR-028），`MotionControlPage` 仅经这些方法触发，并**订阅事件 + 读状态消费结果**。
- 2026-09-02 修正 `MainPage.cs`：**主页面线激光设备开关按钮**直接调线激光流程的运行方法，
  三重违规——(1) 调子类便捷方法而非连接契约入口；(2) 语义错误，把「连接设备」实现成「开激光跑焊接流程」；
  (3) `MainPage` 属主设备边界，线激光非其所属设备，越权直驱。
  已改为**基于连接态判断**：`Disconnected` → `ConnectOn()`，`Connected` → `ConnectOff()`。
  徽标判定同步改为按连接态/焊接过程态判定（连接语义，与开关一致）。
- `ILCamPage.cs` 经核查为**正确调用**：仅用 `ConnectOn()`/`ConnectOff()`（public 连接/断开入口）驱动线激光连接/断开，
  线激光状态通过 `StateChanged`/`WeldStatusChanged` 事件与业务状态消费，无越权直驱。

## 第二条红线：UI 页设备归属边界

> 一个 UI 页只可**直接驱动其自身所属设备**的工作流；对**非所属设备**只能**消费结果**（订阅 `StateChanged`/`WeldStatusChanged` 事件、读取 `State`/`WeldStatus`/业务状态），
> 不得越权直调其 `ConnectOn`/`ConnectOff`/`ResetProcess`。
> 非所属设备的驱动应上收到**归属编排方**——模拟流程统一由 `DeviceControlWork` 编排，因其级联拥有线激光子设备且「模拟由主设备统一管理」。
>
> 例：`MotionControlPage`（运控页）属 `MotionControlWorkflow`（V3 跟踪）→ 可直驱 `MotionControlWorkflow`；
> 线激光（`LineLaserWorkflow`）不在其归属内 → 必须经 `DeviceControlWork` 模拟编排入口，不得直驱线激光内部方法。

## 红线

> 工作流的「驱动开关」只认基类入口；且**驱动权按设备归属划分**：UI 页只直驱自身设备，非自身设备只消费结果、由归属编排方编排。
> 子类暴露的内部启停方法不是对外驱动入口（对外连接/断开用 `ConnectOn`/`ConnectOff`）。
> 新增调用点前先确认：(1) 用的是 `ConnectOn/ConnectOff/ResetProcess/ClearStatus`；(2) 该设备确属本页/本调用方。
