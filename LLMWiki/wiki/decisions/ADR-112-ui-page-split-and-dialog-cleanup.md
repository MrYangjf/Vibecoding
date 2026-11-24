---
title: ADR-112 UI 页面拆分与死弹窗清理
date: 2026-11-20
updated: 2026-11-20
tags: [决策, UI, 页面拆分, 弹窗清理, 设备监控]
status: accepted
---

# ADR-112 UI 页面拆分与死弹窗清理

> **决策一句话**：职能独立的复合页拆为同级子页，零消费者弹窗物理删除，空占位 Tab 由空页类实体化。

## 背景

「系统参数设置」页下 `FilebackupPage` 以 `tabsBackup` 承载「通讯配置文件」与「系统配置文件」两个 Tab，二者职能独立（前者配置 RSI 通讯与调试，后者做配置文档生成与 `.awcfg` 包转移）却共用一个类，切页才能切换职能。`UIDesign/SubDialog/` 下 `ConfigForm` / `IoConfigForm` / `CylinderConfigForm` 三个弹窗在 2026-09-29 系统设置页取消输入IO/输出IO/气缸操作三表后失去全部调用方，两轮独立 Grep 确认仅存自身定义与构造函数。FormMain 的「设备监控」Tab 是空占位（无控件无类）。

## 决策

1. **复合页拆分**：`FilebackupPage` 保留类身份改作「设置备份」页，去掉 `tabsBackup` 外壳，以 `panelSystemCfg` 为根，只保留配置文档生成与 `.awcfg` 导入导出；新建 `CommSettingPage` 承载 RSI 通讯配置、调试面板与通讯日志。
2. **同级挂载**：两页同级挂入 `navPageParam.LoadTabs`（位于「监控相机设置」之后），顺序为「通讯设置」→「设置备份」，图标分别 `ApiOutlined` / `ApartmentOutlined`。
3. **死弹窗清理**：删除 `ConfigForm`（.cs/.Designer/.resx）、`IoConfigForm.cs`、`CylinderConfigForm.cs` 物理文件及各自 csproj 注册；在用的 `AxisConfigForm`（TA 轴参数）与 `RecordConfigForm` 不连坐。
4. **空占位实体化**：新建 `DeviceMonitorPage`（.cs/.Designer/.resx）空页，挂入 FormMain 的 `tabMonitor`，替换原「内容后续在 Designer 补」的纯占位。

## 备选方案

- **两个全新类并废弃 FilebackupPage**：命名对称但需迁移 `api/FilebackupPage` 文档及全部历史引用，改动面大；否决——保留类身份使文档与代码映射稳定，也贴合文件名语义。
- **保留 tabsBackup 仅做视觉分组**：不解决「两职能共一类」的耦合，且用户要求独立页面；否决。
- **死弹窗仅标记弃用不物理删除**：与项目「配置项/代码物理删除而非标记弃用」的一贯口径冲突，且零消费者无兼容负担；否决。

## 后果

### 正面

- 通讯与备份职能在导航层直接分离，无需二次切 Tab；两页各自持有控件与方法，交叉符号为零。
- 死代码物理清零，编译单元与 csproj 注册同步收敛。
- 设备监控有独立类落点，后续填内容无需再改 FormMain 挂载结构。

### 负面

- `FilebackupPage` 类名与「设置备份」显示名不再逐字对应（保留稳定的代价）。
- 拆分当轮需同步更新 `api/FilebackupPage`、CodeMap 与 drift 登记，遗漏会形成文档漂移。

## 相关页面

- [[decisions/ADR-Index]]
- [[modules/UIDesign]]
- [[api/FilebackupPage]]
- [[lessons/UiModuleRemovalCleanup]]
- [[lessons/UiLayoutChangeSyncPitfalls]]

## 演进记录

### 2026-11-20 · DeviceMonitorPage 接收焊接头温度显示

**变更**：设备监控页从空页承载焊接头实时温度显示（保护镜/腔体/温升/切割气压 4 项 + 报警状态），采集链 `CollectTemperature`/`TemperatureSnapshot`/`ApplyTemperature` 由系统设置页迁入；新页用自有 `timerRefresh`（Designer components 托管，500ms，仅 Visible 时刷新），⛔ 不依赖 FormMain 定时器。系统设置页温度区只保留焊接头节点号与 6 项阈值（温度警告/报警、温升警告/报警、气压报警/延时），删除温度自动刷新开关 `swTempRefresh`（保留其容器 `flowPanel3`，内有焊接头从站启用开关）。

**理由**：温度显示属监控职能，与阈值配置分离；业主观察到移走温度监控后刷新开关失去意义（显示由新页自有定时器驱动）。

**影响**：配置键与阈值读写链不变（阈值仍在系统设置页）；采集源仍为 `LaserWeldHeadWorkflow.Instance.LastTemperature` 与 `WeldHeadSlaveDevice.CurrentTemperature`；新页 Timer 生命周期随页面句柄创建/销毁。相关页：[[api/DeviceMonitorPage]] · [[api/SystemControlPage]]。
