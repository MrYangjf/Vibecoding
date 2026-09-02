---
title: UI 开发专员
date: 2026-07-01
tags: [专员, UI, WinForms, AntdUI]
---

# UI 开发专员

## 职责边界

- 所有用户界面的设计与实现（WinForms + AntdUI，原 SunnyUI 已迁出，见 [[decisions/ADR-021-UIFrameworkMigration]]）
- 页面导航结构搭建（ParentUI → Sub1UI → Sub2UI → Sub3UI）
- 为算法/3D/相机/运动控制等模块提供可视化交互界面
- 控件布局、事件绑定、数据绑定
- 3D渲染区域集成（ElementHost + HelixToolkit）
- 响应式设计（TableLayoutPanel 自适应布局）

## 负责文件

```
UIDesign/
├── ParentUI/
│   ├── FormMain.cs
│   ├── FormMain.Designer.cs
│   └── FormMain.resx
├── ControlPage/
│   ├── MainPage.cs
│   ├── NavPage.cs
│   ├── DataReviewPage.cs
│   └── FormLogin.cs
├── Sub2UI/
│   ├── LLCamWorkJob.cs
│   ├── Helix3Drender.cs
│   ├── ParamConfigPage.cs
│   ├── XMLEditor.cs
│   ├── TCPServer.cs
│   ├── TCPClinet.cs
│   └── UserEdit.cs
└── Sub3UI/
    ├── LLCameraSetting.cs
    ├── ConfigForm.cs
    ├── AutoParamForm.cs
    ├── FileTraceForm.cs
    ├── RecordConfigForm.cs
    └── RenderParamForm.cs
```

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

