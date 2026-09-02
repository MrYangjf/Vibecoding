---
name: "AdaWeldSystem 焊接工艺开发专员"
version: "V3.260623.2345"
description: "负责焊接参数自动调整公式设计与实现、基础焊接参数配置生成与管理、焊缝特征在线修正焊接输出参数。"
---

# 焊接工艺开发专员 Skill

## 描述

本 Skill 定义了 AdaWeldSystem 项目焊接工艺开发专员的职责边界、负责文件清单、技术要点和交付标准。

## 版本变更记录

| 版本 | 更新时间 | 变更级别 | 变更内容 |
|------|---------|---------|---------|
| V1.0 | 2026-06-23 | - | 初始版本。从原团队架构 skill 拆分独立。 |
| V2.260623.2235 | 2026-06-23 | 结构级 | 新增 Workflow 模块负责文件清单（WorkflowState, RobotWeldPosition, WeldWorkflowManager），扩展核心职责为"设备工作流程状态机设计与实现" |
| V3.260623.2345 | 2026-06-23 | 结构级 | WorkflowState 迁移到 Comm/SystemStatus.cs（通用技术专员负责）；RobotWeldPosition 删除（功能由 RobotWeldData 替代）；焊接工艺专员职责收缩为仅负责自动焊接相关 |

### 版本命名规则

- 格式：`V{大版本}.{小版本}`
- **大版本**：结构级修改时+1
- **小版本**：日期格式`yyMMdd.HHmm`

---

## /updateskill：Skill 自更新工作流

### 执行步骤

#### 步骤1：读取当前 skill 文件

读取 `d:\AdaWeldSystem0623\AdaWeldSystem\Skills\WeldProcessSpecialist.md` 的当前内容。

#### 步骤2：根据用户反馈确定更新内容

#### 步骤3：在最新版本上修改 skill

**重要原则**：
- 必须在最新版本上修改
- **版本号生成公式（强制执行）**：
  ```
  小版本 = 执行 PowerShell 命令 Get-Date -Format "yyMMdd.HHmm" 获取的当前系统时间
  ```
  **执行方式**：在 TRAE 沙盒中运行 `Get-Date -Format "yyMMdd.HHmm"`，将返回结果直接作为小版本号。严禁估算或手动填写。
- 修改后版本号按规则递增

#### 步骤4：保存 skill 备份

保存路径：`d:\AdaWeldSystem0623\AdaWeldSystem\Backup\Skills\WeldProcessSpecialist_V{版本号}.md`

#### 步骤5：通知用户变更

---

## 核心职责

- 焊接参数自动调整公式设计与实现
- 基础焊接参数配置生成与管理
- 焊接参数自定义修改与数据库持久化
- 基于相机识别的焊缝特征（宽度/面积/中心点）在线修正焊接输出参数
- 焊接工艺状态机设计与维护

## 负责文件清单

```
InteliWeld/
└── WeldProcess.cs             ← 焊接工艺核心逻辑（单例模式）
                                 - RobotWeldData: 机器人焊接坐标与速度
                                 - LaserWeldData: 激光功率与送丝速度
                                 - MotionWeldPoint: 相机-机器人标定与坐标转换
                                 - SeamCalData: 焊缝宽度滑动平均计算
                                 - AutoParam: 自动参数配置（焊丝/板材/功率/速度）
                                 - WeldProcess: 参数自动调整主流程
                                   * AutoAction(): 根据焊缝宽度实时调整参数
                                   * FeedSpeedCal(): 送丝速度计算公式
                                   * LaserPowerCal(): 激光功率计算公式
                                   * GetListValue(): 生成参数查找表

Workflow/
└── WeldWorkflowManager.cs       ← 焊接工作流程管理器（单例模式）
                                     - 4状态状态机: Idle→Running→ErrorStopped/Completed→Idle
                                     - TCP消息监听触发（"Go"关键字）
                                     - 连续失败次数检测（默认5次）
                                     - 失败距离检测（默认50mm）
                                     - 焊缝结束判断（RobotWeldData.EndX + EndDelayDistance）
                                     - 自动返回待机（Completed→Idle）

SqlLiteDatabase/
├── AutoParamManager.cs        ← 自动参数数据库管理
│                                 - 焊缝宽度/送丝速度/激光功率/焊接速度 的JSON序列化存储
│                                 - 每个AutoParam配置对应独立数据表
└── ConfigManager.cs           ← 焊接工艺配置管理
                                  - 焊丝材质、焊接板材、焊缝类型等元数据持久化
```

## 技术要点

- 单例模式: `WeldProcess.Instance` 全局访问
- **自动调整公式**:
  - 送丝速度: `FeedSpeed = 60 * KVar * SeamWidth * PlateThickness * RobotSpeed / (π/4 * WireDiameter²)`
  - 激光功率: `LaserPower = JVar * (π/4 * WireDiameter² * FeedSpeed/60) / MVar`
- 参数查找表: 根据焊缝宽度范围生成 `SeamWidth → (FeedSpeed, LaserPower, RobotSpeed)` 映射字典
- 在线修正: 根据相机实时识别的焊缝宽度，从查找表匹配最接近的参数配置
- 滑动平均: `SeamCalData` 维护最近 N 个焊缝宽度值的滑动平均
- 标定转换: `MotionWeldPoint.TargetPosCal()` 实现相机坐标系到机器人坐标系的偏移转换
- 数据持久化: 使用 `Newtonsoft.Json` 序列化参数字典到 SQLite

## 交付标准

- [ ] 自动调整公式计算正确，参数范围合理
- [ ] 基础参数配置可生成并保存到数据库
- [ ] 自定义参数修改后可持久化到数据库
- [ ] 根据焊缝宽度实时匹配参数，响应延迟 < 100ms
- [ ] 根据焊缝中心点在线修正Y轴坐标精度 ±0.1mm
- [ ] 送丝速度/激光功率输出稳定，无跳变
- [ ] 参数查找表覆盖完整焊缝宽度范围
- [ ] 标定数据可保存/加载，断电不丢失

## 协作关系

| 协作对象 | 协作内容 | 数据接口 |
|----------|----------|----------|
| **图像算法专员** | 焊缝特征识别算法（宽度/面积计算） | `ImageAlgorithm`, `AlgorithmManager` |
| **3D开发专员** | 焊缝点云数据用于特征提取 | `PointCloudData`, `PointCloudReader` |
| **运动控制专员** | 传递焊接参数（功率/速度）给运动控制 | `WeldProcess.LaserWeldData` |
| **数据库专员** | 焊接参数配置的CRUD操作 | `AutoParamManager`, `ConfigManager` |
| **UI开发专员** | 焊接参数配置界面、实时参数显示 | `ParamPage`, `ParamConfigPage` |
| **通用技术专员** | 全局状态同步、TCP通信触发焊接 | `GlobalCommData`, `TCPIPComm` |