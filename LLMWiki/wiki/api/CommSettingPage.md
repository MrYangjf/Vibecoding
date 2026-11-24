---
title: CommSettingPage 通讯设置页
date: 2026-11-20
tags: [API, UI, 通讯设置, RSI, 调试面板, TabPage]
source: AdaWeldSystem/UIDesign/TabPage/CommSettingPage.cs + .Designer.cs
---

# CommSettingPage — 通讯设置页

> 2026-11-20 由 [[api/FilebackupPage]] 的「通讯配置文件」Tab 拆出为独立页（[[decisions/ADR-112-ui-page-split-and-dialog-cleanup]]），与「设置备份」页同级挂入 `navPageParam.LoadTabs`。承载 RSI 通讯配置、调试面板与通讯日志，不触碰配置文档生成与 `.awcfg` 包。

## 基本信息

| 项 | 值 |
|----|----|
| 类 | `AdaWeldSystem.UIDesign.TabPage.CommSettingPage` |
| 基类 | `System.Windows.Forms.UserControl` |
| 文件 | `UIDesign/TabPage/CommSettingPage.cs` + `.Designer.cs` + `.resx` |
| 挂载 | `FormMain` → `navPageParam.LoadTabs(..."通讯设置", new CommSettingPage(), "ApiOutlined")` |
| 根容器 | `tableLayoutPanel1`（`Dock=Fill`）→ `tableLayoutPanel2`（9 列 × 9 行） |

## 职责

| 区块 | 控件 / 方法 | 说明 |
|---|---|---|
| 通讯配置 | `chkEnableRobot` / `selectRsiCycle` / `btnConnect` / `btnRobotDisconnect` / `btnConfig` / `btnKeepConfig` | `LoadConfig`/`SaveConfig`/`chkEnable_CheckedChanged`/`ApplyEnableState` 读写 `CommunicationManager`；`btnConfig_Click` 弹 `FileEditorForm` 编辑 `RobotServerXdoc` |
| 动作门控 | `TryPassCommAction` | 初始化中/关闭中拒绝设备动作（ADR-107） |
| RSI 调试 | `lblRsiStat` / `selectTxCmd` / `txtTxPayload` / `btnSendTx` / 5 焊参输入 / `btnInjectWeldParams` / `txtRsiRxPacket` / `txtRsiTxPacket` | `InitRsiDebugPanel`/`RsiDebugTimer_Tick`（500ms 状态刷新）/`btnSendTx_Click`（下行数值码）/`btnInjectWeldParams_Click`（焊参通道）/`ParseDebugDouble` |
| 通讯日志 | `inputLog` + `AppendLog` | 订阅 `GlobalCommData.CommunicationCommandReceived` 与 `CommLogViewEvent`（ADR-106），跨线程 `BeginInvoke` 封送，超 5000 字符截断 |

## 生命周期

- 构造函数：`InitializeComponent()` → RSI 周期下拉选项 → 订阅 `selectRsiCycle_SelectedIndexChanged` → `InitRsiDebugPanel()` → `LoadConfig()` → 订阅两个全局事件 → 挂 `HandleCreated`/`HandleDestroyed`。
- `HandleCreated` 启动 `_rsiDebugTimer`（500ms）；`HandleDestroyed` 停表/退订 `Tick`/`Dispose()` 表 → `DisposeComponents()` 退订两个全局事件。
- UI 类按需 `DisposeComponents()`，⛔ 不在 `.cs` 重写 `Dispose(bool)`（ADR-002）。

## 设计约束

- 通讯按钮日志一律走 `AppendLog`（本页 `inputLog`），不走 `GlobalCommData.ShowLog`（ADR-106 通讯/结果二分）。
- ⛔ 上行指令本地模拟已删除，调试仅针对真实连接的机器人，上行只能由机器人经 RSI 上报。
- 调试 Tx 与系统告警共用单槽（`_txCmd`），本轮只报不改。

## 相关页面

- 拆分来源：[[api/FilebackupPage]]（设置备份页）
- 日志通道：[[decisions/ADR-106-comm-log-view-channel]]
- 动作门控：[[decisions/ADR-107-init-phase-reconnect-gate]]
- 模块：[[modules/UIDesign]]
