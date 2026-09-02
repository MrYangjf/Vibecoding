---
title: ADR-040 渐进式启动与子页懒加载
date: 2026-08-26
status: rejected
tags: [决策, 启动性能, UI, 懒加载, 相机, 已回退]
module: UIDesign, LineLaserCam, Workflow
---

# ADR-040 渐进式启动与子页懒加载

> **状态：已回退（rejected）**——同日实施后用户反馈未感知到加速，且存在显示比例问题，决定回退到同步全量初始化方式。保留 CameraSelector 简化和 JobManager 移除两项业务变更。

## 背景

程序启动速度慢，用户体验差。根因分析：

1. **构造函数阻塞**：FormMain 构造函数中同步执行了所有初始化工作（8 个子页面全量实例化、5 个设备串行初始化、相机连接检测、6 个单例初始化）
2. **父窗口显示延迟**：必须等所有子页面和子控件全部加载完成后，FormMain 才能显示
3. **冗余初始化**：JobManager（自由算法 Job）和 CameraSelector.Load/DetectConnection 已不再需要——英莱相机已是默认且自带 Job 系统

## 决策

采用**渐进式启动（Progressive Startup）**模式，将启动分为三个阶段：

### 阶段一：框架快速显示（构造函数内，同步）
- `InitializeComponent()` + 设计器模式守卫
- 轻量配置加载（纯内存/文件读取：MoveControlData、SimulationController、MonitorAlgorithmManager）
- UI 主题配置（GlobalCommData.UIConfigSetting）
- 导航框架构建（NavPage 实例 + Tab 占位，子页懒加载）
- 首页面（MainPage）立即实例化并显示
- 事件订阅 + 状态栏初始化

### 阶段二：设备后台初始化（Shown 事件，异步）
- FormMain 首次 Shown 后，通过 `Task.Run` 在后台线程执行
- `MainDeviceThread.PowerOnInitialize()` + `MainDeviceThread.Start()`
- 完成后回到 UI 线程更新日志和状态栏

### 阶段三：子页面按需加载（懒加载）
- 顶层 Tab：主页面立即加载，数据追溯页选中时才创建
- NavPage 内部子页：第一个子页立即加载，其余通过 `LoadTabsLazy()` 传入工厂函数，首次选中时才实例化

### CameraSelector 简化
- 移除 `Load()` / `Save()` / `DetectConnection()` / `SelectReal()`
- 默认直接使用英莱(IntelligentLaser)相机，一步到达
- `Active` 属性首次访问时自动创建英莱相机实例
- 保留 `SelectVirtual()` / `SelectIntelligentLaser()` 用于模拟模式切换
- 保留 `SetWorking()` / `ConnectionState` / `Kind` / `IsVirtual` 等运行时接口

### JobManager 移除
- 英莱使用自己的 Job 系统，不再使用自由算法的 JobManager
- 移除 FormMain 构造函数中的 `JobManager.Instance.Initialize()` 调用

## 理由

1. **感知速度大幅提升**：父窗口先显示，用户立即看到界面框架，而非等待黑屏
2. **实际启动优化**：移除了冗余的 JobManager 初始化和相机选择器加载/连接检测
3. **按需加载**：不常用的子页面（如数据追溯、文件设置等）只在用户访问时才创建
4. **UI 响应性**：设备初始化在后台线程执行，不阻塞 UI 线程
5. **架构简洁**：CameraSelector 从多厂商选择器简化为「英莱默认 + 虚拟调试」二选一

## 后果

### 正面
- 启动感知速度显著提升（父窗口先显示）
- 构造函数执行时间大幅减少
- 内存占用降低（未访问的子页不创建）
- CameraSelector 接口更简洁

### 负面
- 首次切换到未加载的 Tab 时会有短暂延迟（子页实例化时间）
- 设备初始化完成前，状态栏显示设备未连接状态（正常，后台正在连接）
- SimulationController 中 `SelectReal()` 改为 `SelectIntelligentLaser()`，语义更明确

### 风险与应对
- **子页首次切换卡顿**：子页实例化通常 <100ms，用户感知不明显；如卡顿严重可考虑预加载常用页
- **设备初始化失败**：异常已捕获并写日志，不影响主窗口显示；用户可在界面上手动重连
- **懒加载导致的时序问题**：子页构造函数中访问外部单例时需确保单例已初始化（设备初始化在后台，但配置类单例在构造函数阶段已加载）

## 约束

- 所有 UI 更新必须检查 `InvokeRequired`（后台线程不直接操作 UI）
- 事件订阅与退订必须对称（FormClosed 中退订）
- 不修改 Designer.cs 文件
- 遵循 ADR-001 DisposePattern、ADR-002 CS73-Constraint
- NavPage 的旧 `LoadTabs()` 签名保留，向后兼容

## 相关页面

- [[modules/UIDesign]] — FormMain / NavPage 模块文档
- [[decisions/ADR-035-LineLaserWorkflowRefactor]] — 线激光工作流分步重构（前置决策；原链 `ADR-035-IntelligentLaserDefault` 为错名，2026-09-01 更正）
- [[guides/WinForms-UI-Threading]] — UI 线程安全规范
