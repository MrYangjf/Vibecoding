---
title: "ADR-060 P4 UI 落地范式（动作双区共用 · 未就绪置灰 · 振镜图形配置化 · 阴影卡控件范式）"
date: 2026-10-09
updated: 2026-10-09
tags: [ADR, UI, P4, 工艺设置, AntdUI, 动作绑定]
status: accepted
---

# ADR-060：P4 UI 落地范式

> P4 UI 落地的统一裁定。**批J（U-1 快速标定 + U-2 激光头工艺设置）先行落地**，批K/L/M（U-3~U-7）按本页范式续写并就地更新本页。

## 决策

### 一、动作绑定范式：双区共用共享方法

P1 §4.2 规定同一动作出现在两个板块（快速标定「动作位」+ 激光工艺「动作按钮组」，是**不同控件**）。
落地：Designer 双套按钮 → `.cs` 事件处理器（每键一行）→ **共享 `DoTaAuto/DoTaBreak/DoTaPose1/2/DoLaAuto/DoLaSpot1/2/DoLaPose1/2`** →
统一调 `LaserWeldHeadWorkflow` 动作 + `RefreshActionStates()`。⛔ 不复制动作逻辑。

### 二、未就绪轴动作置灰（U-2）

`RefreshActionStates()`：TA 就绪 = `MontionManager` 已初始化且 `TaAxisName` 轴已装配；LA 就绪 = `WeldHead != null`；
未就绪则对应动作按钮全部 `Enabled=false`，状态标签明示原因（「轴未就绪（动作不可用）」）。
状态标签同时显示 `TaTorqueActive`/`LaFollowActive`/`TargetSpotMm`（工作流只读属性）。

### 三、振镜图形 = 人工编辑项（配置化，不参与宽度自适应）

- `WeldAlgorithmsConfig.GalvoPattern`（`GALVO_PATTERN`，1 圆 2 八字 3 直线 4 圆弧，默认 3，四点闭环）——
 消费点 = `ApplyGalvoAmplitude`（振镜唯一下发口）。⚠️ 图形**种类**是人工选择（ADR-059 口径）；图形**尺寸**随摆幅自适应。
- 图形按钮（圆/八字/直线/圆弧）= 设图形并落盘；**手动演示** = `GalvoDemo(当前图形)` 一次性；**回到零位** = `GalvoHome()`。
- 目标光斑输入 → 存 `LaSpotTargetMm` + `LaApplyTargetSpot(spotMm)` 即时生效（新增工作流公开入口）。

### 四、控件范式（复用既有先例，禁凭空造成员）

- 区卡片 = `AntdUI.Panel`（`Back` 白 / `BorderColor` 217,217,217 / `Shadow=5` / `ShadowColor=Black` /
 `ShadowOpacity=0.2F` / `ShadowOpacityAnimation=true` / `AutoScroll` / `Padding=3`，`Dock=Fill` 入 TabPage）——
 与 `panelProcessDebug`/`panelWeldList` 同款。
- 三件套（实例化 + 属性块 + 字段声明）+ 容器 `Controls.Add` + 事件钩子；`Suspend/ResumeLayout` 不增删（四点闭环保持）。
- `AntdUI.Switch.CheckedChanged += new AntdUI.BoolEventHandler(...)`（ILCamPage `swDisplay` 先例）；
 ⛔ 不用 `AntdUI.Radio`（ADR-054：类名/事件名无先例）。
- 按钮 `Type = AntdUI.TTypeMini.Success` 等仅在有先例处使用；状态刷新回填用 `_loadingXxx` 静默标记。

### 五、区归属补记

- `tabLaserProcessTracking`（Tracking 设置）暂空：U-2 清单无 Tracking 项（线激光参数已迁 U-4 轨迹跟踪），留待后续需求。
- U-2 清单「TA·LA 启用开关」**未单独建控件**：P1 §4.2 同区只列「振镜启用开关（`EnableGalvoWeave`）」；
 TA 力矩模式启用（`TorqueModeEnabled`）/ LA 使能属 U-5「激光头控制」参数组，不重复建（同一控件不得出现在两个板块）。
- 振镜组（图形/演示/回零位/启用开关）落在 **LA 设置区**（光斑大小与振镜同为光学输出组）；业主若要独立「振镜设置」分区，可整体平移。

## 后果

- 正面：U-1/U-2 动作全部可点（绑定 P3 后端 12 个动作入口）；未就绪置灰防误操作；图形选择即持久化即生效
- 负面：TA/LA 动作在两区重复呈现（P1 明确要求，非控件重复）；演示摆幅 1.0mm 占位待现场

## 背景

（待补：本决策要解决什么问题）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 相关页面

- [[project/ReviewOptimization-P1-StructureDesign]] §4.2 控件级归属
- [[decisions/ADR-057-TaLaActionAndFollowControl]] · [[decisions/ADR-059-P3TailGalvoAndJointParam]]（动作/图形语义）
- [[api/ProcessControlPage]] · [[api/LaserWeldHeadWorkflow]]
- [[guides/AntdUI-Reference]]（控件成员先例）
