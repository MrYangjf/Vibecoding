---
title: ADR-025 MainPage 硬件快捷开关 FloatButton→ButtonShadow
date: 2026-08-31
tags: [决策, UI, AntdUI, MainPage, 快捷开关, ButtonShadow, FloatButton]
status: accepted
---

# ADR-025 MainPage 硬件快捷开关 FloatButton→ButtonShadow

## 背景

MainPage 底部 `panelfloatbutton` 面板原用 AntdUI `FloatButton.open(Config)` 悬浮覆盖层承载 6 个设备快捷开关。实践中暴露两个结构性问题：

1. **显隐需事件同步**：`FloatButton.open()` 打开的是独立覆盖层窗口（`FormFloatButton`），不属于 MainPage 控件树。页面切换时覆盖层窗口仍悬浮于其他页面之上，必须手工监听页面显隐事件来开关覆盖层——逻辑复杂且易漏。
2. **变色需整层重建**：`ConfigBtn` 的 `Type` 配色不可单独热更新，改连接态配色只能 `Close+open` 重建整个覆盖层（闪烁、抖动、生命周期管理负担）。该方案实施后被用户手动整块注释停用。

## 决策

改用 **`AntdUI.ButtonShadow` 常驻按钮**（继承 `AntdUI.Button` + 内建阴影绘制）：

- 6 个按钮在 `MainPage` 构造函数中代码后置创建（`InitDeviceSwitchButtons()`），直接 `Controls.Add` 进已有 `panelfloatbutton` 面板（不修改 Designer.cs）。
- 按钮属 MainPage 控件树，页面切换显隐由 WinForms 宿主机制自动处理，**零事件同步代码**。
- 连接态变色只改 `Type` 属性（Success/Error），由 `FormMain.uiMillisecondTimer1_Tick` → `RefreshDeviceSwitchUi()` 驱动，`_lastLlConnected` 去重避免每帧赋值。
- 布局：96×34、Y=13 垂直居中、左对齐横排（ADR-022 布局自由化允许手动定位）；`Round=true` 胶囊形；纯文本无图标。
- 删除全部 FloatButton 注释遗骸（BuildFloatButtonConfig/InitDeviceFloatButton/RebuildFloatButton/CloseDeviceFloatButton 等）。

## 备选方案

- **保留 FloatButton + 页面显隐事件同步**：需在 MainPage/父容器挂 VisibleChanged 等事件开关覆盖层，事件链复杂、易漏场景（如权限切页、异常销毁）——放弃。
- **AntdUI.Button + Panel 自绘阴影**：`ButtonShadow` 即官方 Button 阴影化封装，无需自行组合——放弃。

## 后果

### 正面
- 显隐随页面自动生效，无游离窗口、无事件同步负担
- 变色 O(1) 属性赋值，无重建无闪烁
- 释放路径简化：按钮随宿主控件树销毁，`DisposeComponents()` 无需关闭覆盖层

### 负面
- 按钮布局为手动坐标（面板 60px 固定行高内定死），面板行高变化需同步调整
- ~~不再支持 FloatButton 的 Tooltip/圆形悬浮形态（当前以按钮文本替代 Tooltip，无信息损失）~~ **已于同日风格迭代解除**（见下）

## 风格迭代（2026-08-31 同日，形态对齐 AntdUI Demo buttonShadow1）

初版为「96×34 文本按钮 + `Type` 配色」。用户要求对齐 AntdUI Demo `ButtonDemo` 中 `buttonShadow1`（本地 `M3/AntdUI使用demo/AntdUI-Demo-main/Views/ButtonDemo.Designer.cs`：50×50、`BorderWidth=1F`、`IconRatio=1.2F`、`IconSvg`=poweroff 电源 SVG（resx 资源）、`ShadowColor=黑`、`Badge=""`、`BadgeMode=true`），并补齐 Tooltip 与连接态徽标：

- **仅显示 SVG 图标**：`Text` 删除，默认图标 = Ant Design poweroff 电源 SVG（`DefaultDeviceIconSvg` 常量，与 demo 同源）。
- **设备名走 TooltipComponent**（TooltipDemo 范式）：单实例 `_tooltip`（微软雅黑 10F）`SetTip(btn, 设备名)`，`ArrowAlign = TAlign.Top`（顶部显示）；`DisposeComponents()` 释放。**Tooltip 文本含连接状态**（2026-08-31 14:42 补充）：形如「线激光：已连接/未连接」，经 `BuildDeviceTooltipText(idx, connected)` 统一构造，初始全部未连接，线激光随 `RefreshDeviceSwitchUi()` 状态刷新同步重设（`SetTip` 内部 `AddOrUpdate` 支持原地更新文本）。
- **连接态走原生徽标而非 `Type`**：AntdUI `IControl` 内建徽标属性（`Badge`/`BadgeSvg`/`BadgeAlign`/`BadgeMode`/`BadgeBack` 等）；**徽标内容为内置 SVG 图标**：连接=`CheckCircleFilled` 对勾 / 断开=`CloseCircleFilled` 叉号（SvgDb 内置图标名，用户由 CheckOutlined/CloseOutlined 手动改为 Filled 系列并加 `BadgeSize=1.0F`），填色经 `BadgeBack` 驱动：红=(255,77,79)/绿=(82,196,26)；按钮 `Type` 保持默认中性态。`RefreshDeviceSwitchUi()` 同步改 `BadgeSvg`+`BadgeBack`。（初版曾用 `Badge=""` 纯色圆点 + `BadgeMode=true` 镂空，SVG 徽标方案落地后二者已删——`BadgeMode` 仅作用于圆点渲染路径）
- **按钮背景随连接态（2026-08-31 14:22 补充）**：`DefaultBack` 断开=(158,158,158) 灰底 / 连接=null（主题默认白底）；`RefreshDeviceSwitchUi()` 一并刷新。
- **预留接口**：`SetDeviceIconSvg(idx, svg)`（替换按钮图标；**各按钮设备指向不同**，图标 SVG 经 `_deviceIconSvgs[]` 数组按设备逐个缓存+应用）、`SetDeviceBadgeSvg(idx, svg)`（映射原生 `BadgeSvg`，徽标 SVG 化后颜色仍随 BadgeBack）。
- **版本核对**：本项目 `3rdDepend/AntdUI.dll` 已含 `BadgeBack/BadgeSvg/BadgeMode/BadgeAlign/IconRatio/SetTip/TooltipComponent` 元数据（字符串表验证），无需升级 DLL。
- 教训沉淀：徽标渲染逻辑见 `Helper.GDI.PaintBadge`（`BadgeBack ?? Colour.Error` 兜底红），AntdUI 内置 SVG 图标名仅 24 个基础项（SvgDb.cs），业务图标须自备 SVG 字符串。
- **布局改纵向（2026-08-31 15:04）**：用户将 `panelfloatbutton` 面板竖直摆放，按钮创建布局同步改为纵向堆叠——X=2 左对齐固定，Y 按 `btnTop + i*(btnHeight+gap)` 自上而下递增（按钮 52×52、gap=15；6 按钮总高 389px，面板需相应拉高）；ADR-022 手动定位允许。
- **面板标题（2026-08-31 15:10）**：面板最上方代码后置创建 `AntdUI.Label`（`Text="子设备状态"`、`AutoSizeMode=Width` 自适应文本宽、高 24 定值、局部变量随面板销毁），按钮起始 Y 下移至标题下方（`btnTop = top + 24 + gap`，整体面板高度需求 428px）。

## 相关页面

- [[modules/UIDesign]] —— MainPage 硬件快捷开关章节
- [[decisions/ADR-013-CameraConnectionStateDecoupled]] —— 连接态真相源判定（读工作流 Step 不读 ConnectionState）
- [[decisions/ADR-019-LayoutContainerFreedom]] —— 布局容器自由化
- [[guides/AntdUI-Reference]] —— AntdUI 控件范式
