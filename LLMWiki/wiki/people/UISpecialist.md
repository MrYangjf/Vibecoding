---
title: UI 开发专员
date: 2026-07-01
tags: [专员, UI, WinForms, AntdUI]
---

# UI 开发专员

## 职责边界

- 所有用户界面的设计与实现（WinForms + AntdUI，原 SunnyUI 已迁出，见 [[decisions/ADR-018-UIFrameworkMigration]]）
- 页面导航结构搭建（ParentUI → Sub1UI → Sub2UI → Sub3UI）
- 为算法/3D/相机/运动控制等模块提供可视化交互界面
- 控件布局、事件绑定、数据绑定
- 3D渲染区域集成（ElementHost + HelixToolkit）
- 响应式设计（TableLayoutPanel 自适应布局）

## 负责文件

```
UIDesign/                          ← 现役 4 个子目录：MainWindow / ControlPage / TabPage / SubDialog
├── MainWindow/
│   ├── FormMain.cs                ← 主窗体（原 ParentUI/FormMain.cs）
│   └── FormMain.Designer.cs
├── ControlPage/
│   ├── MainPage.cs
│   ├── NavPage.cs
│   └── DataReviewerPage.cs        ← 现役名（原 DataReviewPage.cs）
├── TabPage/                       ← 原 Sub2UI/（2026-08-05 重命名）
│   ├── ILCamPage.cs               ← 现役名（原 LLCamWorkJob.cs）
│   ├── ParamConfigPage.cs
│   ├── FileEditorPage.cs          ← 现役名（原 XMLEditor.cs）
│   ├── CommPage.cs
│   ├── MonitorCamPage.cs
│   └── MotionControlPage.cs
└── SubDialog/                     ← 对话窗，2026-09-07 由扁平 SubView/ 按业务域拆分为 5 个子目录
    ├── DataReviewerDialog/        （FileTraceForm / HelixRenderForm / RecordConfigForm / RenderParamForm）
    ├── FormMainDialog/            （InitWaitingForm ← 原 InitWaitingPanel）
    ├── IntelligentLaserDialog/    （ILAlgoForm / ILAlgorithmEditForm / ILParamForm / ILScanForm）
    ├── ParamContolDialog/         （AutoParamForm / ConfigForm）
    └── UserManagerDialog/         （LoginForm ← 原 FormLogin / UserEditForm ← 原 UserEdit）
```

> 完整旧→新对照表见 [[modules/UIDesign]] §「2026-09-07 目录与命名对照」。

> ⚠️ 历史名称提示：上表为现役结构；下列旧名均已不存在于代码库，保留以备对照——
> `Sub2UI/` → `UIDesign/TabPage/`（2026-08-05 重命名）；`Sub3UI/` → 并入 `UIDesign/SubDialog/`；
> `LLCamWorkJob.cs` → `UIDesign/TabPage/ILCamPage.cs`；`LLCameraSetting.cs` → `UIDesign/SubDialog/IntelligentLaserDialog/ILParamForm.cs`；
> `XMLEditor.cs` → `UIDesign/TabPage/FileEditorPage.cs`；`Helix3Drender.cs` → `UIDesign/SubDialog/DataReviewerDialog/HelixRenderForm.cs`；
> `EmguAlgoPage.cs` → 已移除（职责并入 `UIDesign/SubDialog/IntelligentLaserDialog/ILAlgoForm.cs`）；
> `TCPServer.cs` → 未落地（现役仅 `Comm/CommBase/Ethernet/TCPIPComm.cs` 客户端侧）；
> `TCPClinet.cs` → 历史拼写错误名，现役 `Comm/CommBase/Ethernet/TCPIPComm.cs`

## 技术要点

- Sub2UI 页面继承 `UserControl`（AntdUI 无 `UIPage` 基类，页面以 `UserControl` 承载），Sub3UI 弹窗继承 `AntdUI.Window`
- 控件优先在 Designer.cs 静态定义
- 所有 Workflow 事件处理必须检查 InvokeRequired
- 按钮尺寸：常规 100x35 ~ 140x35，Symbol 按钮 86x35

## 相关页面

- [[modules/UIDesign]]
- [[guides/WinForms-Designer]]
- [[project/SunnyUI-Legacy]]
- [[decisions/ADR-001-DisposePattern]]

