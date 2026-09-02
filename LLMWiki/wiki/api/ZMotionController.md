---
title: ZMotionController API — 正运动控制器
date: 2026-08-10
tags: [API, 运控, 正运动, 控制器, 4轴]
source: AdaWeldSystem/MotionControl/ZMotion/ZMotionController.cs
---

# ZMotionController API — 正运动控制器
> **章节导航**（本页 609 行，超长页请先按章节定位再读）：
>
> - [概述](#概述)
> - [类结构](#类结构)
> - [高级运动指令（第3轮迭代新增）](#高级运动指令第3轮迭代新增)
> - [使用示例](#使用示例)
> - [默认轴参数](#默认轴参数)
> - [电子凸轮（CAMBOX）](#电子凸轮cambox)
> - [连续插补（InterpolationEngine）](#连续插补interpolationengine)
> - [PTPVT 自定义曲线运动](#ptpvt-自定义曲线运动)
> - [主动上报与周期上报](#主动上报与周期上报)
> - [心跳检测](#心跳检测)
> - [轴字典与 IO 字典](#轴字典与-io-字典)
> - [配置管理](#配置管理)
> - [部署说明](#部署说明)
> - [相关页面](#相关页面)


> 正运动（ZMotion）运动控制器硬件对接实现，继承 `MotionControllerBase`，实现 `IMotionController` 接口。
> 命名空间：`AdaWeldSystem.MotionControl.ZMotion`
> 依赖：`zauxdll.dll`（64位），源文件位于项目根 `3rdDepend\` 目录，构建后通过 `CopyNative3rdDependToOutput` 目标拷贝到输出目录，运行时 `DllImport` 从程序输出目录加载

## 概述

基于正运动官方 `Zmcaux.cs` 精简封装，仅保留项目所需的核心功能：
- 以太网连接（`ZAux_OpenEth` / `ZAux_Close`）
- 4轴运动控制（绝对/相对/点动/回零）
- 轴参数设置（速度/加速度/减速度/S曲线）
- 输入输出 IO 控制
- 急停安全机制

## 类结构

### ZMotionController

继承 `MotionControllerBase`，封装正运动控制器的连接管理和轴/IO创建。

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `Name` | `string` | 控制器名称（继承自基类） |
| `IsConnected` | `bool` | 是否已连接（继承自基类） |
| `IsEmergencyStop` | `bool` | 急停状态（继承自基类） |
| `AxisCount` | `int` | 轴数量（继承自基类） |

#### 方法

| 方法 | 说明 |
|------|------|
| `Initialize()` | 连接控制器并初始化4轴+8IO |
| `Close()` | 停止所有轴、关闭所有IO、断开连接 |
| `SetEmergencyStop(bool)` | 触发/解除急停，传播到所有轴和IO |
| `SetIpAddress(string)` | 设置IP地址（需在 Initialize 前调用） |
| `ExecuteCommand(string, out string)` | 执行自定义 BASIC 命令 |

#### 4轴常量

| 常量名 | 值 | 说明 |
|--------|-----|------|
| `AxisName_Y` | `"Y轴"` | 轴0 - 线激光焊缝引导 |
| `AxisName_Galvo` | `"振镜轴"` | 轴1 - 焊缝宽度摆幅控制 |
| `AxisName_WireFeed` | `"送丝伸缩臂轴"` | 轴2 - 压力信号控制 |
| `AxisName_ZFocus` | `"Z轴自动对焦轴"` | 轴3 - 位置传感器对焦 |

### ZMotionAxis

实现 `IAxis` 接口，封装单轴运动控制。

#### 核心方法

| 方法 | 底层API | 说明 |
|------|---------|------|
| `MoveTo(pos, speed)` | `ZAux_Direct_Single_MoveAbs` | 绝对运动（阻塞等待） |
| `MoveToNoBlock(pos, speed)` | `ZAux_Direct_Single_MoveAbs` | 绝对运动（非阻塞） |
| `MoveRelative(delta, speed)` | `ZAux_Direct_Single_Move` | 相对运动（阻塞等待） |
| `Stop(immediate)` | `ZAux_Direct_Single_Cancel` | 停止运动 |
| `ServoOn()` | `ZAux_Direct_SetAxisEnable(1)` | 伺服使能 |
| `ServoOff()` | `ZAux_Direct_SetAxisEnable(0)` | 伺服关闭 |
| `Home()` | `ZAux_Direct_Single_Home` | 回零 |
| `JogMove(dir, speed)` | `ZAux_Direct_Single_Vmove` | 点动（连续运动） |
| `SetHomePosition()` | `ZAux_Direct_SetDpos(0)` | 设置当前位置为零点 |
| `WaitMoveDone(timeout)` | `ZAux_Direct_GetIfIdle` 轮询 | 等待运动完成 |
| `SetDefaultParams(...)` | 一组 SetSpeed/SetAccel 等 | 设置轴默认参数 |

#### 属性

| 属性 | 底层API | 说明 |
|------|---------|------|
| `CurrentPosition` | `ZAux_Direct_GetDpos` | 当前规划位置（mm） |
| `IsMoving` | `ZAux_Direct_GetIfIdle` | 是否正在运动 |
| `IsServoOn` | `ZAux_Direct_GetAxisEnable` | 伺服使能状态 |
| `IsConnected` | - | 连接状态 |

### ZMotionInputIO / ZMotionOutputIO

实现 `IInputIO` / `IOutputIO` 接口。

| 方法 | 底层API | 说明 |
|------|---------|------|
| `ZMotionInputIO.IsOn` | `ZAux_Direct_GetIn` | 读取输入状态 |
| `ZMotionOutputIO.SetON()` | `ZAux_Direct_SetOp(1)` | 输出打开 |
| `ZMotionOutputIO.SetOFF()` | `ZAux_Direct_SetOp(0)` | 输出关闭 |

### ZMotionNative（内部静态类）

正运动原生 DLL P/Invoke 封装，`internal` 访问级别，仅供 ZMotion 子目录内部使用。

封装的核心函数分类：
- **连接管理**：`ZAux_OpenEth`、`ZAux_Close`、`ZAux_Execute`
- **轴参数**：`ZAux_Direct_SetAtype`、`SetUnits`、`SetSpeed`、`SetAccel`、`SetDecel`、`SetSramp`、`SetLspeed`
- **轴运动**：`ZAux_Direct_Single_Move`、`Single_MoveAbs`、`Single_Vmove`、`Single_Cancel`、`Single_Home`
- **轴状态**：`ZAux_Direct_GetDpos`、`GetMpos`、`SetDpos`、`GetIfIdle`、`GetAxisStatus`、`GetAxisEnable`、`SetAxisEnable`
- **IO操作**：`ZAux_Direct_GetIn`、`SetOp`、`GetOp`

辅助方法：
- `IsSuccess(int ret)` — 判断返回值是否为成功
- `GetErrorDescription(int errorCode)` — 获取错误码描述

### ZMotionNativeLaser（内部静态类）

正运动激光振镜 DLL P/Invoke 封装，`internal` 访问级别，依赖 `ZmotionScanLaser.dll`（与 `zauxdll.dll` 配套）。此 DLL 同样通过 `CopyNative3rdDependToOutput` 目标拷贝到输出目录。

封装的核心函数分类：
- **基础配置**：`ZmotionLaser_SetOutput`（激光输出口）、`SetOtherOutDeal`（急停/功率锁存口）、`AoutInit`（功率 DAC）、`SetScanAxis`（振镜轴号）
- **工艺参数**：`SetVectPar` / `SetBmpPar`（矢量/位图打标参数）、`SetTextStyle` / `SetBmpStyle`、`SetFillParam`
- **开关光方式**：`SetMoveInstruct` / `SetMoveFunName` / `SetLightInstruct` / `SetLightString`
- **功率控制**：`SetPowerEnable` / `SetPowerMode` / `SetValidPowerLimit` / `SetPwmNum`
- **图形打标**：`Point` / `Line` / `Polyline` / `Circle` / `Arc` / `Text` / `BarCode` / `FileBmp` / `FileVector`
- **填充/异化**：`FillStart` / `FillEnd` / `AddString` / `SpiralStart` / `SpiralEnd`
- **加工文件**：`OpenFile3` / `CreateFile3` / `CloseFile3` / `GetProcessString` / `GetProEndString` / `ClearNewString`
- **平台联动**：`SetPlatParam`

辅助方法：`IsSuccess(uint ret)`（振镜成功码为 0）、`GetLaserErrorDescription(uint)`（错误码从 11000 起）。

### ZMotionGalvo

正运动激光振镜控制高级封装，面向业务提供振镜/激光打标接口。

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `IsInitialized` | `bool` | 振镜是否已初始化 |
| `ScanAxisX` / `ScanAxisY` | `int` | 振镜 X/Y 轴轴号（默认 4/5） |

#### 方法

| 方法 | 说明 |
|------|------|
| `Initialize(IntPtr)` | 初始化振镜（设置振镜轴 + 激光输出口 + 功率 DAC），需控制器连接后调用 |
| `SetScanAxis(int,int)` | 设置振镜轴号 |
| `SetLaserOutput(ap,mo,red)` | 设置激光开关/使能/红光输出口 |
| `SetVectPar(...)` | 设置矢量打标工艺参数（功率/频率/速度/延时） |
| `SetPowerMode(int)` | 设置功率模式（0-模拟量，1-PWM，2-输出口，3-PWM+输出口，4-模拟量+输出口） |
| `MarkPoint/MarkLine/MarkPolyline/MarkCircle/MarkArc/MarkText/MarkBarCode` | 图形打标系列 |
| `MarkBmpFile/MarkVectorFile` | 打位图/矢量（DXF）文件 |
| `SetFillParam/FillStart/FillEnd` | 填充控制 |
| `SetPlatformParam(...)` | 振镜与平台联动参数 |
| `OpenFile3/CreateFile3/CloseFile3` | 三次文件生成 |

## 高级运动指令（第3轮迭代新增）

> 在基础运动之上扩展位置比较输出、编码器锁存、螺距补偿、软限位等高级运动指令，封装于 `ZMotionAxis`。

### ZMotionAxis 高级方法

| 方法 | 底层API | 说明 |
|------|---------|------|
| `SetSoftLimit(pos, neg)` | `ZAux_Direct_SetLsoftpos` | 设置软限位（正/负向） |
| `SetPswitch(num, enable, outNum, outState, setPos, resetPos)` | `ZAux_Direct_Pswitch` | 软件位置比较输出（PSWITCH） |
| `Regist(mode)` | `ZAux_Direct_Regist` | 编码器锁存（触发→锁存当前编码器位置） |
| `GetRegistPosition()` | `ZAux_Direct_GetRegist` | 读取锁存位置 |
| `SetPitchCompensation(enable, startPos, interval, tableStart, comps)` | `ZAux_Direct_Pitchset` | 螺距补偿（热误差/螺距误差补偿表） |

## 使用示例

### 初始化正运动控制器

```csharp
// 通过 MotionManager 工厂方法初始化
bool success = MotionManager.Instance.InitializeWithZMotion("192.168.0.11");
if (!success)
{
    // 连接失败：不再回退到空控制器，仅记录告警（见 [[decisions/ADR-037-DefaultInitZMotion]]）
}
```

### 控制Y轴焊缝跟踪

```csharp
IAxis yAxis = MotionManager.Instance.GetAxis("Y轴");

// 绝对运动到目标位置（阻塞等待）
yAxis.MoveTo(targetYmm, speed: 30.0);

// 非阻塞运动（适合实时跟踪场景）
yAxis.MoveToNoBlock(targetYmm, speed: 50.0);

// 检查是否运动完成
if (!yAxis.IsMoving)
{
    // 运动已完成
}
```

### 控制振镜摆动

```csharp
IAxis galvoAxis = MotionManager.Instance.GetAxis("振镜轴");

// 设置摆动中心位置
galvoAxis.MoveTo(centerMm, speed: 200.0);

// 相对运动（摆幅调整）
galvoAxis.MoveRelative(swingWidthMm, speed: 150.0);
```

### 控制 IO

```csharp
// 读取输入
IInputIO pressureInput = MotionManager.Instance.GetInputIO("压力传感器信号");
bool pressureOK = pressureInput.IsOn;

// 设置输出
IOutputIO laserEnable = MotionManager.Instance.GetOutputIO("激光器使能");
laserEnable.SetON();
```

### 急停

```csharp
// 全局急停
MotionManager.Instance.SetGlobalEmergencyStop(true);

// 单轴停止
IAxis yAxis = MotionManager.Instance.GetAxis("Y轴");
yAxis.Stop(immediate: true);  // 急停
```

## 默认轴参数

各轴默认参数（可根据实际机械结构调整 `SetDefaultParams` 调用）：

| 参数 | Y轴 | 振镜轴 | 送丝臂轴 | Z对焦轴 |
|------|-----|--------|---------|--------|
| 脉冲当量 (units) | 1000 | 1000 | 1000 | 1000 |
| 起始速度 (mm/s) | 10 | 20 | 5 | 5 |
| 运行速度 (mm/s) | 50 | 200 | 30 | 40 |
| 加速度 (mm/s²) | 500 | 2000 | 300 | 400 |
| 减速度 (mm/s²) | 500 | 2000 | 300 | 400 |
| S曲线时间 (ms) | 50 | 20 | 50 | 50 |

## 电子凸轮（CAMBOX）

> 正运动控制器支持电子凸轮功能，通过 CAMBOX 模式实现从轴跟随主轴做非线性同步运动。追剪（飞剪）是电子凸轮的典型应用场景。

### WriteCamTable — 写入凸轮表

```csharp
// 写入凸轮表数据（主轴位置 → 从轴位置的映射表）
// camIndex: 凸轮表编号（0~7）
// table: 凸轮数据点数组，格式为 [masterPos0, slavePos0, masterPos1, slavePos1, ...]
// count: 数据点对数
int ret = ZMotionController.Instance.WriteCamTable(int camIndex, double[] table, int count);
```

- 底层API：`ZAux_Direct_SetTable` / BASIC 命令 `TABLE`
- 凸轮表数据点按「主轴位置, 从轴位置」成对排列
- 凸轮表可存储多组，通过 `camIndex` 索引

### StartCambox — 启动电子凸轮

```csharp
// 启动 CAMBOX 电子凸轮模式
// masterAxis: 主轴轴号
// slaveAxis: 从轴轴号
// camIndex: 使用的凸轮表编号
// tableLength: 凸轮表周期长度（主轴一个周期对应的位置增量）
int ret = ZMotionController.Instance.StartCambox(int masterAxis, int slaveAxis, int camIndex, double tableLength);
```

- 底层API：BASIC 命令 `CAMBOX`
- 启动后从轴自动跟随主轴位置，按凸轮表映射做非线性运动
- 主轴可由外部编码器或运动轴驱动

### StopCambox — 停止电子凸轮

```csharp
// 停止 CAMBOX 电子凸轮模式
// slaveAxis: 从轴轴号
int ret = ZMotionController.Instance.StopCambox(int slaveAxis);
```

- 底层API：BASIC 命令 `CANCEL` + `CAMBOX(0)`
- 停止后从轴脱离凸轮模式，恢复为独立轴控制

### Movelink — 电子齿轮联动（线性）

```csharp
// 启动电子齿轮联动（线性比例跟随）
// masterAxis: 主轴轴号
// slaveAxis: 从轴轴号
// ratio: 从轴/主轴速度比
int ret = ZMotionController.Instance.Movelink(int masterAxis, int slaveAxis, double ratio);
```

- 底层API：BASIC 命令 `MOVELINK`
- 线性同步，从轴速度 = 主轴速度 × ratio
- 适用于简单的同步传动场景

### Moveslink — 电子齿轮联动（S曲线）

```csharp
// 启动带S曲线的电子齿轮联动
// masterAxis: 主轴轴号
// slaveAxis: 从轴轴号
// ratio: 从轴/主轴速度比
// sramp: S曲线时间（ms）
int ret = ZMotionController.Instance.Moveslink(int masterAxis, int slaveAxis, double ratio, double sramp);
```

- 底层API：BASIC 命令 `MOVESLINK`
- 相比 `MOVELINK` 增加了 S 曲线平滑过渡，减少冲击

## 连续插补（InterpolationEngine）

> 连续插补引擎用于将多段运动指令连续下发，实现无缝衔接的轨迹运动。适用于焊接、切割等需要连续轨迹的场景。

### InterpolationEngine 类

位于 `ZMotion/InterpolationEngine.cs`，封装连续插补运动控制。

| 属性 | 类型 | 说明 |
|------|------|------|
| `IsRunning` | `bool` | 插补引擎是否正在运行 |
| `CurrentSegmentIndex` | `int` | 当前正在执行的段索引 |
| `TotalSegments` | `int` | 总段数 |

### MoveSegment — 追加运动段

```csharp
// 向插补缓冲区追加一段运动
// axes: 参与插补的轴号数组
// positions: 各轴目标位置数组（与axes一一对应）
// speed: 插补速度（mm/s）
// accel: 加速度（mm/s²）
bool success = interpolationEngine.MoveSegment(int[] axes, double[] positions, double speed, double accel);
```

- 底层API：`ZAux_Direct_Move` 多轴插补 + 缓冲区机制
- 采用前瞻缓冲机制，当前段运动时可预写下一段，实现无缝衔接
- 支持 2~4 轴直线插补

### 引擎控制方法

| 方法 | 说明 |
|------|------|
| `Start()` | 启动插补引擎，开始执行缓冲区中的段 |
| `Stop()` | 停止插补，清空缓冲区 |
| `Pause()` | 暂停插补（保留当前位置） |
| `Resume()` | 继续插补 |
| `ClearBuffer()` | 清空插补缓冲区 |

## PTPVT 自定义曲线运动

> PTPVT（Point-To-Point Velocity Time）模式支持用户自定义位置-速度-时间曲线，实现任意轨迹规划。

### PTPVT_Move — 追加PTPVT数据点

```csharp
// 向PTPVT缓冲区追加数据点
// axis: 轴号
// position: 目标位置（mm）
// velocity: 目标速度（mm/s）
// time: 到达目标点的时间（s）
int ret = ZMotionController.Instance.PTPVT_Move(int axis, double position, double velocity, double time);
```

- 底层API：BASIC 命令 `PTPVT`
- 每个数据点定义「位置 + 速度 + 时间」三要素
- 控制器自动在两点间做样条插值，保证速度平滑过渡

### PTPVT_Start — 启动PTPVT运动

```csharp
// 启动 PTPVT 运动
// axis: 轴号
int ret = ZMotionController.Instance.PTPVT_Start(int axis);
```

- 启动后轴按照缓冲区中的 PTPVT 数据点序列运动
- 需先通过 `PTPVT_Move` 填充数据点

### PTPVT_Stop — 停止PTPVT运动

```csharp
// 停止 PTPVT 运动
// axis: 轴号
int ret = ZMotionController.Instance.PTPVT_Stop(int axis);
```

- 立即停止PTPVT模式，清空缓冲区数据

## 主动上报与周期上报

> 正运动控制器支持两种数据上报模式：主动上报（事件触发）和周期上报（定时采样）。用于上位机实时获取控制器状态，避免轮询开销。

### StartAutoReport — 启动主动上报

```csharp
// 启动主动上报（事件触发模式）
// item: 上报项目（如 "AXISSTATUS", "IN", "OP" 等）
// axisOrIndex: 轴号或IO索引
int ret = ZMotionController.Instance.StartAutoReport(string item, int axisOrIndex);
```

- 底层API：BASIC 命令 `BASE_REPORT` + `ON_REPORT`
- 当指定状态发生变化时主动上报，减少无效通信
- 适用于状态变化不频繁但需要及时响应的场景

### StopAutoReport — 停止主动上报

```csharp
// 停止主动上报
// item: 上报项目
// axisOrIndex: 轴号或IO索引
int ret = ZMotionController.Instance.StopAutoReport(string item, int axisOrIndex);
```

### StartCycleReport — 启动周期上报

```csharp
// 启动周期上报（定时采样模式）
// item: 上报项目
// axisOrIndex: 轴号或IO索引
// cycleMs: 上报周期（毫秒）
int ret = ZMotionController.Instance.StartCycleReport(string item, int axisOrIndex, int cycleMs);
```

- 底层API：BASIC 命令 `REPORT`
- 按固定周期定时上报指定数据
- 适用于需要连续采样的实时监控场景

### StopCycleReport — 停止周期上报

```csharp
// 停止周期上报
// item: 上报项目
// axisOrIndex: 轴号或IO索引
int ret = ZMotionController.Instance.StopCycleReport(string item, int axisOrIndex);
```

### 上报回调机制

```csharp
// 注册上报数据回调
ZMotionController.Instance.OnReportData += (item, index, value) =>
{
    // item: 上报项目名
    // index: 轴号/IO索引
    // value: 上报值（字符串格式，需自行解析）
};
```

## 心跳检测

> 心跳检测用于监控控制器与上位机的连接状态，及时发现通信中断并触发保护动作。

### StartHeartbeat — 启动心跳

```csharp
// 启动心跳检测
// intervalMs: 心跳间隔（毫秒），默认1000ms
// timeoutCount: 超时次数阈值，默认3次
bool success = ZMotionController.Instance.StartHeartbeat(int intervalMs = 1000, int timeoutCount = 3);
```

- 后台线程定时向控制器发送心跳包
- 连续超时达到阈值时触发 `OnHeartbeatLost` 事件

### StopHeartbeat — 停止心跳

```csharp
// 停止心跳检测
ZMotionController.Instance.StopHeartbeat();
```

### CheckHeartbeat — 手动检测心跳

```csharp
// 手动检测一次心跳
// 返回值：true-控制器在线，false-控制器无响应
bool alive = ZMotionController.Instance.CheckHeartbeat();
```

- 底层API：`ZAux_Execute("?VERSION")` 或 `ZAux_Direct_GetDpos` 轻量调用
- 同步检测，调用方等待返回结果

### 心跳事件

```csharp
// 心跳丢失事件
ZMotionController.Instance.OnHeartbeatLost += () =>
{
    // 通信中断处理：停止运动、触发报警等
};

// 心跳恢复事件
ZMotionController.Instance.OnHeartbeatRestored += () =>
{
    // 通信恢复处理
};
```

## 轴字典与 IO 字典

> 通过名称索引快速查找轴和IO对象，替代传统的按索引遍历方式，提高代码可读性和安全性。

### GetAxisByName — 按名称获取轴

```csharp
// 通过轴名称获取轴对象（在ZMotionController内部使用）
// axisName: 轴名称，如 "Y轴"、"振镜轴"
IAxis axis = ZMotionController.Instance.GetAxisByName("Y轴");
```

- 内部维护 `Dictionary<string, IAxis>` 轴字典
- 名称不区分大小写
- 名称不存在时返回 `null`，调用方需判空

### GetInputIOByName — 按名称获取输入IO

```csharp
// 通过名称获取输入IO对象
// ioName: IO名称，如 "压力传感器信号"
IInputIO input = ZMotionController.Instance.GetInputIOByName("压力传感器信号");
```

### GetOutputIOByName — 按名称获取输出IO

```csharp
// 通过名称获取输出IO对象
// ioName: IO名称，如 "激光器使能"
IOutputIO output = ZMotionController.Instance.GetOutputIOByName("激光器使能");
```

> **注意**：上层应用应通过 `MotionManager.Instance.GetAxis(name)` / `GetInputIO(name)` / `GetOutputIO(name)` 访问，字典机制已封装在基类 `MotionControllerBase` 中。

## 配置管理

> 统一配置管理，将轴参数、IO配置、控制器参数集中管理，支持从文件加载和保存。

### MotionConfig 类

位于 `MotionControl/Config/MotionConfig.cs`，统一配置类。

| 配置节 | 类型 | 说明 |
|--------|------|------|
| `ControllerIp` | `string` | 控制器IP地址 |
| `AxisConfigs` | `List<AxisConfig>` | 各轴参数配置列表 |
| `InputIOMap` | `Dictionary<string, int>` | 输入IO名称→索引映射 |
| `OutputIOMap` | `Dictionary<string, int>` | 输出IO名称→索引映射 |
| `HeartbeatIntervalMs` | `int` | 心跳间隔（毫秒） |
| `HeartbeatTimeoutCount` | `int` | 心跳超时次数 |

### AxisConfig 轴参数配置

| 字段 | 类型 | 说明 |
|------|------|------|
| `Name` | `string` | 轴名称 |
| `AxisNumber` | `int` | 轴号 |
| `Units` | `int` | 脉冲当量（脉冲/mm） |
| `LSpeed` | `double` | 起始速度（mm/s） |
| `Speed` | `double` | 运行速度（mm/s） |
| `Accel` | `double` | 加速度（mm/s²） |
| `Decel` | `double` | 减速度（mm/s²） |
| `Sramp` | `double` | S曲线时间（ms） |

### LoadConfig — 加载配置

```csharp
// 从配置文件加载运动参数
// configPath: 配置文件路径（INI格式）
MotionConfig config = MotionConfig.LoadConfig(string configPath);
```

- 配置文件格式：INI，每个轴一个 section
- 加载失败时返回默认配置，不抛出异常

### SaveConfig — 保存配置

```csharp
// 将当前配置保存到文件
// configPath: 配置文件路径
config.SaveConfig(string configPath);
```

- 保存为 INI 格式，便于人工查看和修改
- 保存前自动备份原文件（加 `.bak` 后缀）

## 部署说明

1. 将正运动64位库文件中的 `zauxdll.dll` 放置到项目根目录 `3rdDepend\` 下
2. 构建时 `CopyNative3rdDependToOutput` 目标会自动将原生 DLL 拷贝到输出目录（`bin\Debug\` 或 `bin\Release\`）
3. 确保项目平台目标为 **x64**
4. 控制器默认 IP：`192.168.0.11`，可通过 `SetIpAddress()` 修改

## 相关页面

- [[api/MotionManager]] — 运动控制器管理器
- [[api/IMotionController]] — 运动控制器接口
- [[api/IAxis]] — 运动轴接口
- [[api/IIO]] — IO 接口
- [[modules/MotionControl]] — 模块文档
- [[decisions/ADR-029-ZMotionControllerIntegration]] — 架构决策
