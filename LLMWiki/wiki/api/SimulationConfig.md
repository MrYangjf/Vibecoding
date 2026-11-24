---
title: SimulationConfig 模拟参数配置 API
date: 2026-11-23
updated: 2026-11-23
tags: [API, 模拟测试, 配置, MainDeviceControl]
status: accepted
---

# SimulationConfig 模拟参数配置 API

> 文件：`AdaWeldSystem\MainDeviceControl\SimulationConfig.cs`（命名空间 `AdaWeldSystem.MainDeviceControl`）
> 职责：`SimulationController.ini` 的**唯一持有者**，模拟测试参数只经本类读写。
> 载体路径：`Config\ConfigFileControl\MainDeviceControl\SimulationController.ini`（由 `ConfigFileManager` 统管）。

## 公共 API

| 成员 | 签名 | 说明 |
|---|---|---|
| `DefaultFilePath` | `static string DefaultFilePath` | 配置文件绝对路径，取 `ConfigFileManager.ModuleAbsolutePath` |
| `DefaultPreWorkStartXmm` | `const double = 100.0` | 焊接前寻位起点 X 缺省值（毫米） |
| `LoadLaserFrequencyHz` | `int LoadLaserFrequencyHz(int fallback)` | 读线激光数据频率（30/60/80/120Hz） |
| `SaveLaserFrequencyHz` | `bool SaveLaserFrequencyHz(int value)` | 写线激光数据频率 |
| `LoadPreWorkStartXmm` | `double LoadPreWorkStartXmm(double fallback)` | 读焊接前寻位起点 X；负值与缺键回退 `fallback` |
| `SavePreWorkStartXmm` | `bool SavePreWorkStartXmm(double value)` | 写起点 X；负值按 `DefaultPreWorkStartXmm` 落盘 |

## 配置键

| 节 | 键 | 语义 |
|---|---|---|
| `[Simulation]` | `LineLaserDataFrequencyHz` | 模拟线激光出帧频率 |
| `[Simulation]` | `PreWorkStartXmm` | 模拟机器人 PreWork 段移动到的寻位起点 X（毫米），到位即停 |

## 行为契约

1. **路径唯一**：存在性判断与真实读写必须用同一来源 —— 构造入参传 `DefaultFilePath`（载体路径），⛔ 不得由调用方手拼 `Config\MainDeviceControl\Simulation_INI\...` 历史目录，否则 `File.Exists` 恒假、读取永远回退缺省值。
2. **读侧零写盘**：文件或键缺失只回退 `fallback`，不生成模板、不补键。
3. **写侧审计**：保存走 `ConfigFileManager.SaveIni`，按文件键值记录变动项。
4. **负值语义**：起点 X 为负视为非法，读回退 `fallback`、写按 `DefaultPreWorkStartXmm` 落盘。
5. **线程安全**：全部成员在实例锁内串行，供模拟线程与 UI 线程并发访问。

## 相关页面

- [[api/ConfigFileManager]] —— 载体路径与统一落盘入口
- [[api/ConfigSelfHeal]] —— 自愈路径必须取载体路径的契约
- [[api/DeviceControlWork]] —— 唯一构造方，模拟调度消费本类参数
- [[decisions/ADR-114-prework-seek-position]] —— 焊前寻位起点 X 的决策来源
- [[lessons/SimulationAutoBranching]] —— 模拟注入与调度陷阱
- [[index/index]]
