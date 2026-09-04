---
title: ADR-022 正运动控制器接入架构
date: 2026-08-10
status: accepted
tags: [ADR, 运控, 正运动, 架构]
---

> ⚠️ 历史名称提示：本页为**历史决策记录**，正文中的下列文件名为决策当时的旧名，
> 保留原文以留存上下文，现役对应如下：
>
> - `Zmcaux.cs` → 现役 `MotionControl/ZMotion/ZMotionNative.cs`
>

# ADR-022 正运动控制器接入架构

## 背景

项目确定使用正运动（ZMotion）运动控制器实现4轴运动控制：
- 轴0：Y轴（线激光焊缝焊接点引导）
- 轴1：振镜轴（线激光焊缝宽度设置摆幅和位置）
- 轴2：送丝伸缩臂轴（外部压力信号控制）
- 轴3：Z轴自动对焦轴（送丝臂位置传感器控制）

现有 MotionControl 模块已建立三层架构（`IMotionController` + `IAxis` + `IIO`）和 `NullMotionController` 空实现，需要对接真实正运动硬件。

## 决策

### 决策1：子目录实现 + 基类继承

**选择**：在 `MotionControl/ZMotion/` 子目录下实现正运动控制器，`ZMotionController` 继承 `MotionControllerBase`，`ZMotionAxis` 实现 `IAxis`，`ZMotionInputIO/ZMotionOutputIO` 实现 `IIO` 接口。

**理由**：
- 遵循 ADR-012 确立的三层架构（控制器层 + 轴层 + IO层）
- 插拔式设计，不修改现有 `NullMotionController` 默认行为
- 子目录隔离，便于未来添加其他品牌控制器实现（如固高、雷赛）
- 符合开闭原则：新增硬件不修改抽象层

**替代方案**：
- 修改 `NullMotionController` 为正运动实现 → 否决，破坏空实现默认行为
- 新建独立项目 → 否决，增加复杂度，且运控逻辑需共享同一 MotionManager

### 决策2：原生 API 精简封装

**选择**：基于官方 `Zmcaux.cs` 精简封装，创建 `ZMotionNative` 内部静态类，仅封装项目所需的连接、轴运动、IO操作函数（约20个P/Invoke入口）。

**理由**：
- 官方 Zmcaux.cs 包含数百个函数，体积大（1600+行），大部分本项目不用
- 精简封装降低维护成本，减少 P/Invoke 入口面
- `internal` 访问级别，只在 ZMotion 子目录内部使用，不暴露给上层
- 未来需要新功能时再按需添加

### 决策3：MotionManager 工厂方法 + 失败回退

**选择**（历史，已被 [[decisions/ADR-027-DefaultInitZMotion]] 修订）：在 `MotionManager` 中新增 `InitializeWithZMotion(ipAddress)` 工厂方法，连接失败时自动回退到 `NullMotionController` 空实现。

> ⚠️ **2026-08-21 修订**：`MotionManager.Initialize()` 默认即初始化正运动控制器，`NullMotionController` 空实现已删除，连接失败不再回退空控制器、仅记录告警（详见 [[decisions/ADR-027-DefaultInitZMotion]]）。

**理由**：
- 保持 `Initialize()` 默认空控制器的兼容性，不破坏现有调用方
- 失败回退保证系统在无硬件环境下仍可运行（调试/演示/离线开发）
- 工厂方法集中初始化逻辑，调用方无需关心具体控制器类型
- 符合「默认安全」原则：硬件故障不导致系统崩溃

### 决策4：默认轴参数硬编码 + 可调整

**选择**：在 `ZMotionController.InitializeAxes()` 中为4个轴设置默认参数（脉冲当量、速度、加速度等），参数值留注释说明，后续可通过配置文件或UI调整。

**理由**：
- 项目早期阶段，机械参数尚未最终确定
- 硬编码默认值可快速联调验证
- 后续可迁移到 `ConfigManager` 或 `AutoParamManager` 持久化

## 后果

### 正面

1. **架构清晰**：抽象层与硬件实现分离，新增硬件只需新增子目录
2. **兼容性好**：`MotionManager.Initialize()` 行为不变，现有代码零修改
3. **容错性强**：硬件连接失败自动回退，不影响其他模块运行
4. **维护成本低**：精简封装仅20个核心函数，易于理解和维护

### 负面

1. **需要部署原生DLL**：`zauxdll.dll` 源文件放于项目根 `3rdDepend\` 目录，构建时通过 `CopyNative3rdDependToOutput` 目标自动拷贝到输出目录，增加发布依赖项
2. **平台限制**：正运动 DLL 仅支持 Windows 平台（x86/x64）
3. **参数硬编码**：初期参数硬编码，后续需迁移到配置系统

### 风险

1. **P/Invoke 签名错误**：需仔细核对官方 Zmcaux.cs 中的函数签名
2. **多线程安全**：正运动 API 调用需注意线程安全，避免并发调用导致异常
3. **轴参数单位**：脉冲当量（units）需与实际机械结构匹配，否则位置计算错误

## 验证

- [x] `ZMotionController` 继承 `MotionControllerBase`，实现所有抽象方法
- [x] `ZMotionAxis` 实现 `IAxis` 接口所有方法
- [x] `ZMotionInputIO/ZMotionOutputIO` 实现 `IInputIO/IOutputIO` 接口
- [x] `MotionManager.InitializeWithZMotion()` 连接失败时回退到空控制器
- [x] 4个轴参数已设置，注释说明各参数含义
- [x] 急停机制：触发时停止所有轴、关闭标记IO
- [x] 新增 .cs 文件已注册到 `AdaWeldSystem.csproj`

---

## 第3轮迭代（2026-08-11）

> 第一轮完成基础4轴运动控制对接，第二轮扩展高级运动功能与运维能力，第三轮聚焦架构优化：电子凸轮完整封装、配置三合并一、字典查找模式。

### 决策5：电子凸轮完整 CAMBOX 封装（追剪只是特殊应用）

**背景**：初期只考虑了追剪（飞剪）这一种电子凸轮应用场景，设计了专门的追剪接口。但正运动控制器的 CAMBOX 是通用电子凸轮机制，追剪只是其典型应用之一。

**选择**：将电子凸轮作为通用能力完整封装，提供 `WriteCamTable` / `StartCambox` / `StopCambox` / `Movelink` / `Moveslink` 等通用接口，追剪模式在上层业务中通过配置特定凸轮表实现。

**理由**：
- **通用优先**：CAMBOX 是通用电子凸轮机制，追剪只是众多应用之一（还有旋切、同步输送、飞锯等）
- **扩展性好**：通用接口可适配未来不同工艺需求，不限于追剪
- **贴近硬件**：接口命名和语义与正运动控制器 BASIC 命令（`CAMBOX`、`MOVELINK`、`TABLE`）对应，降低理解成本
- **分层清晰**：通用凸轮能力在控制器层，具体工艺曲线（如追剪轨迹）在业务层

**替代方案**：
- 只封装追剪专用接口 → 否决，局限于单一应用，未来新需求需改底层
- 封装完整电子凸轮 + 额外提供追剪便捷方法 → 可作为后续增强，当前先做通用底层

### 决策6：三配置合一，统一为 MotionConfig.cs

**背景**：随着功能增加，运动控制相关的配置分散在三处：
1. 轴参数：硬编码在 `ZMotionController.InitializeAxes()` 中
2. IO 映射：散落在各调用方，名称与硬件索引的对应关系不统一
3. 心跳参数：准备新增，尚无明确归属

三处配置独立管理，修改时需要改动多个位置，容易遗漏且不一致。

**选择**：创建 `MotionControl/Config/MotionConfig.cs` 统一配置类，将轴参数、IO映射、心跳参数全部纳入，替代三个独立配置来源。配置文件存储为 INI 格式，路径 `Config/INI/MotionConfig.ini`。

**理由**：
- **单一真源**：所有运动控制参数集中在一个配置类，修改一处即可生效
- **便于持久化**：统一的 `LoadConfig` / `SaveConfig` 接口，加载保存逻辑一致
- **便于UI配置**：UI 页面对接一个配置对象即可完成所有运动参数设置
- **默认回退**：配置文件缺失或损坏时，使用硬编码默认值，保证系统可启动
- **与 INIFile 协同**：复用项目已有 `INIFile` 工具类（参见 [[guides/Config-Data-Tools]]）

**配置结构**：
```
MotionConfig
├── ControllerIp              ← 控制器IP
├── AxisConfigs [List]        ← 各轴参数（名称/轴号/脉冲当量/速度/加减速/S曲线）
├── InputIOMap [Dict]         ← 输入IO名称→索引映射
├── OutputIOMap [Dict]        ← 输出IO名称→索引映射
├── HeartbeatIntervalMs       ← 心跳间隔
└── HeartbeatTimeoutCount     ← 心跳超时次数
```

### 决策7：轴/IO 字典查找模式：通过名称索引轴和IO

**背景**：初期 `MotionControllerBase` 使用 `List<IAxis>` 存储轴，通过 `GetAxis(int index)` 按索引访问。调用方需要记住"Y轴是0号、振镜轴是1号"等对应关系，代码可读性差，且索引调整时需要修改多处硬编码。

**选择**：在 `MotionControllerBase` 中引入字典查找机制，维护 `Dictionary<string, IAxis>` / `Dictionary<string, IInputIO>` / `Dictionary<string, IOutputIO>` 三个字典，对外提供 `GetAxis(string name)` / `GetInputIO(string name)` / `GetOutputIO(string name)` 按名称查询。

**理由**：
- **语义化**：`GetAxis("Y轴")` 比 `GetAxis(0)` 直观易懂，代码自文档化
- **解耦索引**：硬件轴号调整只需修改配置映射，不影响业务代码
- **大小写不敏感**：内部统一转小写比较，避免"Y轴"/"y轴"不一致导致的查找失败
- **空值安全**：名称不存在时返回 `null` 而非抛异常，调用方判空即可
- **与配置映射配合**：IO 名称→索引的映射由 `MotionConfig.OutputIOMap` 统一配置，字典在初始化时根据配置构建

**设计细节**：
- 基类同时保留 List（用于遍历所有轴/IO）和 Dictionary（用于按名查找），两者同步维护
- `AddAxis` / `AddIO` 时同时加入 List 和 Dictionary
- 名称比较使用 `StringComparer.OrdinalIgnoreCase`
- 与 `MotionManager` 的按名查询接口保持一致：`MotionManager.Instance.GetAxis("Y轴")`

**替代方案**：
- 仅保留 List，每次按名查找时遍历 → 否决，O(n) 复杂度，且代码冗余
- 仅保留 Dictionary，丢失顺序信息 → 否决，遍历所有轴时顺序不确定

### 第3轮迭代后果

**正面**：
1. 电子凸轮通用化，适配未来多种同步运动需求
2. 配置统一管理，降低维护成本和出错概率
3. 字典查找提升代码可读性和可维护性

**负面**：
1. 配置类引入增加了一层抽象，新成员需要学习配置结构
2. 字典需要与 List 同步维护，增加少量内部复杂度

**风险**：
1. 凸轮表数据格式需要与工艺工程师对齐，避免曲线理解偏差
2. 配置迁移：现有硬编码参数需平滑迁移到 INI 文件，过渡期需保持兼容

### 第3轮迭代验证

- [x] 电子凸轮通用接口：WriteCamTable / StartCambox / StopCambox / Movelink / Moveslink
- [x] MotionConfig 统一配置类定义，包含轴参数/IO映射/心跳参数
- [x] MotionConfig.LoadConfig / SaveConfig 持久化方法
- [x] MotionControllerBase 中 Dictionary 字典查找机制
- [x] GetAxis / GetInputIO / GetOutputIO 按名称查询接口
- [x] 名称不区分大小写
- [x] 配置加载失败时回退到硬编码默认值

## 相关页面

- [[decisions/ADR-012-MotionControlModule]] — MotionControl 模块架构
- [[modules/MotionControl]] — MotionControl 模块文档
- [[api/ZMotionController]] — ZMotionController API 文档
- [[api/MotionManager]] — MotionManager API 文档
