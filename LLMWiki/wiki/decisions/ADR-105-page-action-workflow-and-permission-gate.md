---
title: ADR-105 页面动作统一经工作流与页面级权限门控
date: 2026-11-17
updated: 2026-11-17
tags: [决策, UI, 权限, 页面生命周期, 线激光, 模拟测试]
status: accepted
---

# ADR-105 页面动作统一经工作流与页面级权限门控

> **决策一句话**：UI 页面只查询、不直连硬件；连接类动作统一交工作流后台线程执行；页面释放只退订事件与停本页预览、不断设备；手动连接与模拟测试受权限门控，初始化/关闭期间页面动作一律拒绝并给出原因。

## 背景

阶段 8 核对发现三处与总纲 V10 不符：

1. `ILCamPage.btnConnect_Click` 在 UI 线程直接调 `_ilCamera.ConnectManual(ip)`，随后又调 `LineLaserWorkflow.ConnectOn()` → 同一动作两条路径、阻塞 UI（缺陷 D18）。
2. `ILCamPage_HandleDestroyed` 在页面销毁时主动断开相机并调 `ConnectOff()`，把页面生命周期与设备生命周期绑在一起；页面切走即断设备，与「设备归主设备/工作流管理」冲突。
3. `ILCamPage` 手动连接无权限门控；`SystemControlPage` 模拟测试启停同键、启动无权限门控；初始化期间页面动作也不拦。

## 决策

1. **单一动作路径**：页面连接/断开只调 `LineLaserWorkflow.ConnectOn()` / `ConnectOff()`（后台线程 + 线程登记）；连接前把用户输入的 IP 写入 `LineLaserManager.Config.SensorIp` 并保存，供连接线程读取。
2. **连接态真相源**：页面以 `LineLaserWorkflow.State == Connected` 判定连接，不再以相机实例直连结果为准；硬件回填由 `StateSwitched` 的 `Disconnected→Connected` 边沿触发。
3. **页面释放不断设备**：`HandleDestroyed` 只退订全部事件、释放预览克隆对象；设备断开归主设备关闭链与工作流释放链。
4. **权限门控**：新增 `ILCamPage.TryPassPageAction`，按「关闭中 → 初始化中 → 权限不足」三档拒绝；手动连接要求工程师及以上。模拟测试启动要求管理员，停止与清理不受限（安全动作）。
5. **初始化期置灰**：连接按钮在初始化/关闭期间置灰，状态标签显示「初始化中，连接已锁定」；初始化结束事件触发恢复。
6. **不新增控件、不改配置存储**：参数显示仍复用轴表「参数」按钮与 `AxisConfigForm`，Y 取 `ROOT/AXES/AXIS`、TA 取 `ROOT/TA_HOME`，显示原值不折算。

## 备选方案

- 保留 `ConnectManual` 直连、仅删除重复 `ConnectOn()` → 仍卡 UI，且绕过线程登记与关闭 Join，弃。
- 页面释放时保留断设备 → 切页会误断正在焊接的设备，弃。
- 非管理员隐藏「连接」按钮 → 与「隐藏 ≠ 禁用」原则冲突，且无法给出原因，弃；改为点击拒绝 + 置灰。
- 模拟测试用持久化开关 → 引入新配置键且默认值语义复杂，弃；保持运行期瞬态、默认关闭。

## 后果

### 正面
- 线激光页不再阻塞 UI，连接/断开有唯一路径且可被关闭链 Join。
- 页面生命周期与设备生命周期解耦，切换页面不影响设备。
- 权限与初始化期动作边界清晰，拒绝原因可追溯（Warning 日志 + 界面提示）。

### 负面
- 连接为异步，点击后到状态刷新之间有一个短暂窗口，需以「连接正在进行」提示而非即时结果。
- 非管理员在工程页手动连接被拒，现场调试需先登录工程师账号。

## 落地

- `UIDesign/TabPage/ILCamPage.cs`：`btnConnect_Click`、`TryPassPageAction`、`UpdateModeUiCore`、`UpdateConnectionUiCore`、`OnInitializationCompleted`、`ILCamPage_HandleDestroyed`
- `UIDesign/TabPage/SystemControlPage.cs`：`BtnStartSim_Click`
- 复用既有：`PermissionLevel.IsEngineerOrAbove / IsAdmin`、`GlobalCommData.mOperateLevel`、`DeviceControlWork.IsInitializing / IsShuttingDown / InitializationCompleted`

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-101-shutdown-closure-and-estop]]
- [[api/LineLaserCamPage]]
- [[api/SystemControlPage]]
- [[modules/UIDesign]]
