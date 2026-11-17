---
title: 架构开发员
date: 2026-07-01
tags: [专员, 架构]
source: raw/skills/AdaWeldsys_Skills/01-Team/Architect.md
---

# 架构开发员

## 职责边界

- 整体架构设计：项目结构、模块划分、命名空间规划
- 接口定义：跨模块数据流、事件契约、数据接口
- 任务分配：根据需求确定负责专员、变更范围
- 技术选型：工具/库/框架的引入决策
- 代码审查：跨模块变更审批、架构合规性检查
- 规范制定：编码规范、文档规范、流程规范

## 负责文件

- AdaWeldSystem.csproj（项目文件管理）
- App.config
- Program.cs
- history.md
- Skills/ 目录下所有 skill 文件（维护）

## 技术要点

- .NET Framework 4.8 + C# 7.3 约束
- WinForms + AntdUI + HelixToolkit 技术栈（原 SunnyUI 已迁出，见 [[decisions/ADR-008-UIFrameworkMigration]]）
- 各模块依赖关系管理
- 跨模块数据流：相机→图像算法→焊接工艺→运动控制
- 事件总线模式：GlobalCommData 全局事件通信

## 协作关系

| 协作对象 | 协作内容 |
|----------|----------|
| 所有专员 | 任务分配、变更审批、架构决策 |
| UI开发专员 | 页面结构设计、导航层级定义 |
| 通用技术专员 | 全局状态管理、事件总线规范 |

---

*来源：raw/skills/AdaWeldsys_Skills/01-Team/Architect.md*
