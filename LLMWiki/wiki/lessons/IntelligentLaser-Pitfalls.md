---
title: 英莱（IntelligentLaser）相机开发教训汇总
date: 2026-08-18
tags: [教训, 相机, 英莱, IntelligentLaser, 汇总]
---

# 英莱（IntelligentLaser）相机开发教训汇总
> **章节导航**（本页 1218 行，超长页请先按章节定位再读）：
>
> - [1. SDK 互操作与结构体](#1-sdk-互操作与结构体)
> - [2. 连接与启动](#2-连接与启动)
> - [3. 回调机制](#3-回调机制)
> - [4. 校准框绘制](#4-校准框绘制)
> - [5. UI 层与状态管理](#5-ui-层与状态管理)
> - [5.7 dwInstanceId 参数陷阱](#57-dwinstanceid-参数陷阱)
> - [6. 委托 GC 保护与 CallbackOnCollectedDelegate](#6-委托-gc-保护与-callbackoncollecteddelegate)
> - [相关页面](#相关页面)
> - [来源](#来源)


本文档汇总英莱（IntelligentLaser）线激光相机在 C# / .NET Framework 4.8 开发过程中踩过的所有坑，按 SDK 互操作、连接启动、回调机制、校准框绘制四大主题归类，便于后续开发快速检索与规避。

---

## 1. SDK 互操作与结构体

英莱 C# 包装 `IntelligentLaser_CSharp.dll` 由 CppSharp 生成。首次使用其复杂结构体与命名空间时，有两个必须注意的互操作陷阱。

### 1.1 Job Parameter 结构体字段须以生成代码确认

**问题**

`TIntelligentJobParam`（含 `CurValue` union：`SzValue`/`FValue`/`DwValue`）与 `TIntelligentJobParamsGroup`（`DwParamNum`/`StParamArray[]`/`value_Range.float_range`/`value_Range.int_range`）等结构体用于设备侧 Job Parameter 的 Fetch/Set。

代码首次使用这些类型时，**仅靠开发手册 §6 描述的「形状」推断成员名**（如 `CurValue.SzValue`、`value_Range.float_range.FloatMin`）——CppSharp 对 C++ union / 嵌套 struct 的命名规则并不完全 predictable，且 `SzParamName`/`SzValue` 是定长 64 字节数组，字段名/布局可能因 SDK 版本或生成参数而异。

**影响**

- 若实际生成代码成员名与推断不符（如 union 字段命名、嵌套路径），`IntelligentLaserCameraRun.cs` 的 `InitJobParamsCallback`/`FetchAllJobParams`/`ApplyJobParams` 将**编译失败**（CS1061 找不到成员）。
- 定长 64 字节缓冲（`Make64Bytes`/`Read64Bytes`）处理 `SzParamName`/`SzValue` 是硬约束，封送越界会运行时崩溃。

**修复 / 规避**

- 在 `IntelligentLaserCameraRun.cs` 相关代码处标注 `// QA P0`：所有 `TIntelligentJobParam`/`TIntelligentJobParamsGroup` 成员的字段名与 union 布局**必须以 VS x64 构建确认为准**（首次使用此类类型）。
- 确认方式：在 VS 中「转到定义」查看 `IntelligentLaser_CSharp` 生成的 `TIntelligentJobParam`/`TIntelligentJobParamsGroup` 真实成员，必要时按生成代码微调字段路径。
- 始终保持全限定 `System.Runtime.InteropServices.Marshal.SizeOf(typeof(TIntelligentJobParamsGroup.__Internal))` 步进数组回调（规避 SDK 同名 `Marshal` 遮蔽，见下文 §1.2）。
- 64 字节缓冲务必用 `Make64Bytes`/`Read64Bytes` ASCII 处理（不足补 0、超长截断、遇 NUL 终止）。

**结论**

**CppSharp 生成的 union / 嵌套结构体成员名是「以生成代码为准」项，不能仅凭文档形状假设**；凡首次使用 SDK 包装的复杂结构体，编译前务必在 VS x64 下「转到定义」核对字段名。

### 1.2 命名空间遮蔽 BCL Marshal

**现象**

`IntelligentLaserCameraRun.cs` 编译报错：*"Marshal"未包含"ReadFloat"的定义*（或 `ReadSingle`）。

**根因**

本模块同时：
```csharp
using IntelligentLaser_CSharp;          // 英莱 SDK 包装命名空间
using System.Runtime.InteropServices;    // BCL
```
而 **`IntelligentLaser_CSharp` 命名空间自身也导出了一个 `Marshal` 类型**（与 `Mat` 类似）。当代码裸写 `Marshal.ReadFloat(...)` 时，标识符 `Marshal` 被解析到 **SDK 的 `Marshal`**（而非 BCL `System.Runtime.InteropServices.Marshal`）；SDK 的 `Marshal` 既没有 `ReadFloat` 也没有 `ReadSingle`，于是报"未包含该方法"的定义错误。

> 此前曾把 `ReadSingle`→`ReadFloat` 试图修复，**未触达根因**——两者都被同一 SDK `Marshal` 遮蔽，同样失败。

**修复（正确做法）**

使用**全限定 BCL 名称**绕过 `using` 解析，直接命中 `System.Runtime.InteropServices.Marshal`：
```csharp
byte[] buf = new byte[8];
IntPtr fp = ...; // FPoint 基址（y@0 / z@4，单位 mm）
System.Runtime.InteropServices.Marshal.Copy(fp, buf, 0, 8);
float y = System.BitConverter.ToSingle(buf, 0);
float z = System.BitConverter.ToSingle(buf, 4);
```
- `Marshal.Copy(IntPtr, byte[], int, int)` 与 `BitConverter.ToSingle(byte[], int)` 在 .NET Framework 4.8 均可用。
- 全限定 `System.Runtime.InteropServices.Marshal` 不受 SDK 同名类型遮蔽影响，编译确定通过。

**关联**

- 同名 `Mat` 遮蔽，需全限定 `Emgu.CV.Mat`
- 适用：任何 `using IntelligentLaser_CSharp;` 且又需 BCL `Marshal`/`Mat` 的代码点

### 1.3 StParamArray getter 缓存的 TIntelligentJobParamFullInfo 实例在 Group 释放后成为悬空指针

**问题**

`InitJobParamsCallback` 回调中访问 `TIntelligentJobParamsGroup.StParamArray` 时，CppSharp 生成的 getter 内部调用 `TIntelligentJobParamFullInfo.__GetOrCreateInstance(addr, saveInstance=true)`，将每个元素的 `TIntelligentJobParamFullInfo` 实例缓存到 `NativeToManagedMap` 中。

当 `TIntelligentJobParamsGroup` 副本被释放（`Dispose()` → `Marshal.FreeHGlobal`），副本的原生内存被释放，但缓存的 `TIntelligentJobParamFullInfo` 实例的 `__Instance` 指针仍指向已释放的地址。后续回调若 `Marshal.AllocHGlobal` 复用了相同地址，`__GetOrCreateInstance` 返回旧缓存实例，读到的是上一轮数据或垃圾数据。

**影响**

- `InitJobParamsCallback` 内解析的参数名/值类型/范围可能读到过期数据
- 用户观察到「21 组数据显示出几百组」——参数元数据缓存被污染
- 仅影响 `StParamArray` 访问器（`saveInstance=true`），`TIntelligentJobParam` 的 `__GetOrCreateInstance` 默认 `saveInstance=false` 不受影响

**修复方案**

**不要在 `InitJobParamsCallback` 内使用 `StParamArray` 访问器**。改用 `Marshal.Copy` / `Marshal.ReadInt32` 直接从回调缓冲区读取裸字节，完全绕过 CppSharp 的缓存机制：

```csharp
// ❌ 错误：StParamArray getter 内部缓存 TIntelligentJobParamFullInfo 实例
var arr = group.StParamArray;
var finfo = arr[j];
var name = Read64Bytes(finfo.StParam.SzParamName);

// ✅ 正确：直接内存读取，无缓存
int stParamArrayOffset = (int)Marshal.OffsetOf(typeof(TIntelligentJobParamsGroup.__Internal), "stParamArray");
int paramFullInfoSize = Marshal.SizeOf(typeof(TIntelligentJobParamFullInfo.__Internal));
IntPtr elemPtr = IntPtr.Add(gp, stParamArrayOffset + j * paramFullInfoSize);
byte[] nameBuf = new byte[64];
Marshal.Copy(elemPtr, nameBuf, 0, 64);
string name = ReadAsciiBytes(nameBuf);
uint valueType = (uint)Marshal.ReadInt32(elemPtr, 64); // dwValueType 在 stParam 中 offset 64
```

**各字段偏移量速查**

| 字段 | 路径 | 偏移量 |
|------|------|--------|
| `szParamName[64]` | `stParam` 起始 | 0 |
| `dwValueType` | `stParam` 中 | 64 |
| `value_Range` (union 8B) | 越过 `stParam(132)` + `DefValue(64)` | 196 |

**对应 demo 做法**

官方 .NET Framework Demo 的 `InitJobParamsCallback` 只创建 `TIntelligentJobParamsGroup` 副本并存储（`JobParamsGroupArray = paramArray`），**不在回调内访问 `StParamArray`**。对 `StParamArray` 的访问发生在后续 `QueryParamRange` 中按需进行，此时副本仍存活，缓存实例有效。

**结论**

- CppSharp 生成的 `StParamArray` getter 使用 `saveInstance=true`，会缓存内部 `TIntelligentJobParamFullInfo` 实例
- 回调内如果「创建副本 → 访问 StParamArray → 释放副本」，缓存实例成为悬空指针
- 绕过方式：在 `InitJobParamsCallback` 中用直接内存读取替代 `StParamArray` 访问器

### 1.4 直接内存读取的偏移量须用 Marshal.OffsetOf 获取（避免硬编码）

**问题**

`InitJobParamsCallback` 采用直接内存读取绕过 `StParamArray` 缓存后，`dwParamNum`、`dwValueType`、`value_Range` 的偏移量使用硬编码（32、64、196）。虽然理论上正确，但用户反馈「参数组异常」仍然存在。

**根因分析**

排查发现三个潜在问题：

1. **硬编码偏移量不够可靠**：虽然从结构体布局推算正确，但硬编码值不随结构体定义变化而自动更新，结构体变更时容易遗漏。
2. **直接读取回调缓冲区**：之前版本直接从 `pInstance` 回调缓冲区读取数据，但 SDK 回调可能多次触发，回调缓冲区的内存布局在不同调用间可能不一致。
3. **缺少调试信息**：回调日志只输出参数总数，没有输出每个 Group 的 `dwParamNum` 值和关键偏移量，难以定位异常根源。

**修复方案**

`InitJobParamsCallback` 改为「先复制 Group 数组，再读取数据」的两步结构，与官方 Demo 完全一致：

```csharp
// 步骤 1：按 Demo 方式复制 TIntelligentJobParamsGroup 数组
int stride = Marshal.SizeOf(typeof(TIntelligentJobParamsGroup.__Internal));
var groups = new TIntelligentJobParamsGroup[arraySize];
for (uint i = 0; i < arraySize; i++)
{
    IntPtr currentElementPtr = IntPtr.Add(pInstance, (int)(i * stride));
    TIntelligentJobParamsGroup instancePtr = TIntelligentJobParamsGroup.__GetOrCreateInstance(currentElementPtr);
    groups[i] = new TIntelligentJobParamsGroup(instancePtr);
    instancePtr.Dispose();
}

// 步骤 2：从复制后的 Group 原生内存读取参数数据
// 使用 Marshal.OffsetOf 获取所有偏移量，避免硬编码
int dwParamNumOffset = (int)Marshal.OffsetOf(typeof(TIntelligentJobParamsGroup.__Internal), "dwParamNum");
int stParamArrayOffset = (int)Marshal.OffsetOf(typeof(TIntelligentJobParamsGroup.__Internal), "stParamArray");
int dwValueTypeOffset = (int)Marshal.OffsetOf(typeof(TIntelligentJobParam.__Internal), "dwValueType");
int valueRangeOffset = (int)Marshal.OffsetOf(typeof(TIntelligentJobParamFullInfo.__Internal), "value_Range");

// 仍然使用直接内存读取（绕过 StParamArray getter 缓存）
foreach (var group in groups)
{
    IntPtr gp = group.__Instance;
    uint num = (uint)Marshal.ReadInt32(gp, dwParamNumOffset);
    // ... 读取参数名、类型、范围
}
```

**关键变更**

| 变更项 | 之前 | 之后 |
|--------|------|------|
| 数据来源 | 回调缓冲区 `pInstance` | 复制后的 `group.__Instance` |
| 偏移量 | 硬编码 (32/64/196) | `Marshal.OffsetOf` 动态获取 |
| 数据复制 | 不复制 | 按 Demo 方式复制 Group |
| 调试日志 | 仅输出参数总数 | 输出偏移量 + 参数总数 |

**验证**

构建验证通过（0 Error），日志会输出实际偏移量值，便于确认结构体布局。

**结论**

- 直接内存读取的偏移量应使用 `Marshal.OffsetOf` 获取，避免硬编码
- 回调数据应优先复制到独立内存再读取，与官方 Demo 做法一致
- 偏移量日志可作为结构体布局的运行时验证依据

---

## 2. 连接与启动

### 2.1 检测连通性只连接、不开激光相机（ConnectManual vs OpenSensor）

**问题**

应用启动时 `FormMain` 构造函数调用 `CameraSelector.DetectConnection()` 刷新线激光相机连接态。英莱分支原本写：

```csharp
_intelligentInstance.OpenSensor("192.168.178.210");
```

结果**应用一启动就直接开启了激光和采集相机**，与「连接测试只连接、不开外设」的预期不符。

**根因**

`IntelligentLaserCameraRun` 里有两个语义不同的连接方法：

| 方法 | 语义 | 适用场景 |
|------|------|---------|
| `OpenSensor(ip)` | **一键全开**：InitSDK→ConnectToSensor→`SetSensorEnable(true)`+`SetLaserEnable(true)`+`SetSensorCaptureCameraEnable(true)`→HIGH_SPEED→注册回调 | 工作流 `SensorRunContinue` 启动采集 |
| `ConnectManual(ip)` | **只连接**：InitSDK+ConnectToSensor+注册回调，**不开传感器/激光/相机** | 页面「连接」按钮、启动连通性检测 |

`DetectConnection` 的目的是「检测是否连得上」，却误用了给工作流「全开采集」的 `OpenSensor`，于是启动即开激光/相机。

**修复**

`CameraSelector.DetectConnection` 英莱分支改调 `ConnectManual`（只连接），IP 从 `Config/INI/IntelligentLaser.ini` 读取（替代硬编码）：

```csharp
if (!_intelligentInstance.IsConnected)
    _intelligentInstance.ConnectManual(IntelligentLaserCameraRun.LoadSavedIp());
```

开激光/开相机只能由用户在 `ILCamPage` 上显式点「开启激光」/「开启相机」触发（`SetLaser`/`SetCaptureCamera`）。

**结论**

- 「连接」与「开启外设」是两步动作，必须分离：连接 ≠ 开激光/开相机。
- `DetectConnection`（启动连通性检测）与 `OpenSensor`（工作流全开采集）语义不同，不可混用。
- 英莱 SDK 的 `ConnectToSensor` 本身只建立连接，开外设需显式 `SetLaserEnable`/`SetSensorEnable` 等。

---

## 3. 回调机制

英莱 SDK 的数据链路是回调驱动的，涉及画面显示、一次性初始化数据、传感器/激光/相机三层解耦、重连恢复等多个要点。

### 3.1 画面显示必须回调驱动，轮询只用于查询状态

**问题**

英莱相机页面（`ILCamPage`）用 `System.Windows.Forms.Timer`（50ms ≈ 20fps）轮询 `CurrentMat`/`LastContourPointCount`/`LastInspectResult` 刷新轮廓画面；算法编辑页 `ILAlgoForm` 用 150ms Timer 轮询 `LastInspectResult` 刷新「实时识别结果」表。这与英莱官方 .NET Framework Demo 严重不符。

**根因（对 demo 的语义误读）**

英莱官方 demo 里 **Timer 轮询与回调**各司其职，不可混用：

| 机制 | demo 用途 | 本项目误用 |
|------|----------|-----------|
| `MillionOutlineInspect` **回调** | **更新画面**（轮廓点、特征点、校准框），回调内 `BeginInvoke` 切 UI 线程绘制，50ms 时间戳节流到 ~20fps | 回调只做了「换帧 → `_currentMat`」，画面更新却交给 UI 层 Timer 轮询 |
| `Timer` **轮询**（1s） | **查询状态**：`FetchSensorInfo`（相机开/关）、`FetchLaserStatus`（激光开/关）等「激光和相机是否打开正常工作」 | 把轮询用在了「显示画面」上 |

即：**画面 = 回调驱动；状态 = 轮询**。本项目未启用 demo 的监控相机，故「监控相机状态」本就不需要。

**修复**

1. `IntelligentLaserCameraRun` 新增 `event EventHandler ContourFrameReady`：在 `MillionOutline` 回调成功换帧后调 `NotifyFrameReady()`，按 50ms 节流（~20fps，与 demo 一致）触发事件。事件在 SDK 原生线程触发，**不触碰 UI 控件**。
2. `ILCamPage` / `ILAlgoForm` 删除各自 Timer 轮询，改订阅 `ContourFrameReady`，处理器内 `InvokeRequired` 封送到 UI 线程再刷新。
3. 生命周期：`ILCamPage` 在 `HandleDestroyed` 退订；`ILAlgoForm` 的清理方法由 `StopTimer()` 改名 `StopRefresh()`（退订事件），`ILAlgorithmEditForm.HandleDestroyed` 同步改名调用。

**结论**

- 英莱 SDK 的数据链路本身**已经是回调**（`MillionOutlineInspect` → 换帧），UI 显示应顺势**订阅事件**，而不是再起一个 Timer 去拉取回调产出的数据——这是「回调产数据、轮询再消费」的双重浪费，且频率/时序与相机帧流脱节。
- 节流应在**产帧侧**（相机回调）做（50ms → 20fps），而非在 UI 侧 Timer 里模拟。
- 遵循本项目既有范式：`LLCamWorkJob` 早已用 `Workflow_DisplayEvent`（事件驱动）推帧显示，英莱页面应与之一致。

### 3.2 一次性回调必须在连接前注册

**问题现象**

英莱SDK连接 `ConnectToSensor` 时会**一次性触发**两个回调：
1. `InternalRefCornerPts` → 下发校准框角点（中心点+4角点）
2. `RecvInitJobParamsInfo` → 下发全部 Job Parameter 元数据（名称/类型/范围）

若回调注册（`IntelligentRegisterCallBack_*`）在 `ConnectToSensor` **之后**执行：
- 两个一次性回调都在注册前已经触发完成
- 托管层永远收不到这两个回调
- 结果：
  ① 校准框/十字架永远不显示（`_calibration.HasData=false`）
  ② 参数页面（`ILParamForm`/`ILAlgorithmEditForm`）永远无数据（`_jobParams` 为空缓存）

**根因分析**

英莱SDK的连接流程设计：
```
连接建立 → SDK内部完成握手与初始化 → SDK主动推送校准和参数元数据 → 应用层得到连接结果
```
推送的回调就是在连接握手阶段触发，所以必须在连接握手**之前**完成回调注册。

官方Demo（`Form1.cs:84-164`）顺序确认：
```csharp
int initret = IntelligentLaser_export.InitSDK(); // 1. InitSDK
// ... 此处注册全部回调，包括 InternalRefCornerPts 和 RecvInitJobParamsInfo ...
int connectRet = IntelligentLaser_export.ConnectToSensor(ip); // 2. ConnectToSensor
```

**修复方案**

连接顺序必须是：
```csharp
1. InitSDK();
2. RegisterCallbacks() → 注册所有回调（含一次性回调）
3. ConnectToSensor();
```

如果需要重试连接（多次调用 `ConnectCore`）：
- `RegisterCallbacks()` 每次都必须重新执行（因为每次连接 SDK 都会重新触发一次性回调）
- 必须先检查 `_hostHandle.IsAllocated` → 若已分配，先 `Free()` 再重新 `Alloc`，避免 `GCHandle` 泄漏

**代码修正位置**

- `IntelligentLaserCameraRun.ConnectCore(string ip)`
  ```csharp
  // BEFORE (bug):
  //   InitSDK → ConnectToSensor → RegisterCallbacks
  // AFTER (fixed):
  //   InitSDK → RegisterCallbacks → ConnectToSensor
  ```
- `IntelligentLaserCameraRun.RegisterCallbacks()` 首行新增：
  ```csharp
  // 连接失败重试时会被再次调用：先释放旧句柄，避免 GCHandle 泄漏
  if (_hostHandle.IsAllocated) _hostHandle.Free();
  ```

**验证方法**

连接后：
1. 查看日志：`CalibrationCallback` 是否被触发 → 若有日志，说明收到校准数据
2. 查看 `IlCalibrationInfo.Center`/`LeftTopCorner` 等是否有非零值 → 非零表示数据已接收
3. 查看 `_jobParams` 列表长度 → 大于零表示参数元数据已接收

### 3.3 传感器使能即出回调数据，激光仅控制照射与回调无关

**错误认知**

容易误认为「必须开启激光，MillionOutlineInspect 回调才会出数据」，或者「激光开关会影响图像回调的触发」。

**正确逻辑**

英莱 SDK 的三层控制是**完全解耦**的：

| 控制 | SDK 方法 | 作用 | 与回调关系 |
|------|----------|------|-----------|
| **传感器使能** | `SetSensorEnable(true)` | 启动传感器采集，**触发 MillionOutlineInspect 回调** | **回调的触发源头** |
| **激光开启** | `SetLaserEnable(true)` | 控制物理激光照射 | **无任何关系** |
| **采集相机** | `SetSensorCaptureCameraEnable(true)` | 控制 YUV 预览相机 | 仅影响 YUV 回调，不影响轮廓回调 |

**关键事实**：
- `SetSensorEnable(true)` 后，`MillionOutlineInspect` 回调即开始持续触发，数据链路正常工作
- 激光未开启时，回调数据中可能没有有效的激光线轮廓（因为没有激光照射），但**回调本身不受影响**
- 激光仅控制物理线激光的照射开关，是独立于数据采集链路的**外设控制**

**对本项目的影响**

当前代码已正确反映此逻辑，无需修改：

```
ConnectCore → InitSDK + RegisterCallbacks + ConnectToSensor
    ↓
OpenSensor → ConnectCore + SetSensor(true) + SetLaser(true) + SetCaptureCamera(true)  // 一键全开
ConnectManual → ConnectCore（只连接，不开任何外设）  // 手动分步控制
```

- `OpenSensor` 中 `SetSensor/SetLaser/SetCaptureCamera` 是三个**独立并列**调用，互不依赖
- `ConnectManual` 连接后，用户可单独按「开启激光」按钮（`SetLaser(true)`），不影响已运行的回调数据流
- `MillionOutlineCallback` 回调中**不检查激光状态**，仅检查 `_disposed` 和 `count` 有效性

**结论**

- **传感器使能 = 回调出数据**（可能无有效激光线导致结果错误，但回调本身正常触发）
- **激光开启 = 仅控制物理照射**，与数据回调流完全无关
- 二者是独立的外设控制，不可混为一谈

### 3.4 重连后需恢复传感器使能以恢复回调

**现象**

通过 `ILCamPage` 的「连接」按钮手动断开相机再重新连接后，`MillionOutlineInspect` 轮廓回调不再触发，画面冻结、结果不更新。

**根因**

`IntelligentLaserCameraRun.ConnectManual(string ip)` 只做了 **InitSDK → 注册回调 → ConnectToSensor** 三件事，**没有开启传感器使能（`SetSensorEnable(true)`）**。

而 `MillionOutlineInspect` 回调的触发前提是**传感器处于运行状态**（`SetSensorEnable(true)`）。`ConnectManual` 的设计语义是「只连接，不开外设」（让用户分步开启激光/相机），但传感器使能本身是「数据回调开关」，与激光/相机是解耦的三层控制体系（见 §3.3）。

断开时 `DisconnectManual` 会调用 `SetSensorEnable(false)`，所以第一次连接后如果用户开了传感器（点「开启相机」或其他路径），回调是正常的；但断开再重连后，传感器处于关闭状态，回调自然不触发。

**修复**

在 `ILCamPage.btnConnect_Click` 中，`ConnectManual` 成功后**自动调用 `_ilCamera.SetSensor(true)` 恢复传感器使能**，确保重连后 MillionOutline 回调立即恢复。

**注意**：这是 `ILCamPage`（手动调试页）的页面级修复，不改变 `ConnectManual` 本身的「只连接」语义（`ConnectManual` 仍保持纯连接，供其他调用方按需控制）。

**延伸**

- 自动工作流路径 `OpenSensor` 不会有此问题，因为 `OpenSensor` 本身就会调用 `SetSensor(true)`。
- `SensorRunContinue` 也有同样的逻辑：未运行时调用 `SetSensorEnable(true)`。

### 3.5 「开启相机」按钮应控制传感器使能（SetSensor），而非采集相机（SetCaptureCamera）

**现象**

用户点击「开启激光」后相机也像开启了（有回调数据），点击「关闭相机」后仍能收到回调值——按钮语义与用户预期不符。

**根因**

英莱 SDK 三层控制完全解耦（见 §3.3），但 UI 层「开启相机」按钮绑定的是 `SetCaptureCamera`（采集相机上电），而非 `SetSensor`（传感器使能=回调源头）。同时连接后自动调用 `SetSensor(true)` 启动了传感器，导致：
- 连接后传感器已在运行，用户点激光只是叠加激光、误以为「点激光也开了相机」
- 点「关闭相机」只关了采集相机电源，传感器仍在运行 → 回调继续

**修复**

1. 「开启相机」按钮改为控制 `SetSensor`（传感器使能）：开启时顺带确保采集相机上电（`SetCaptureCamera(true)` + `SetSensor(true)`），关闭时仅停传感器（`SetSensor(false)`）。
2. 连接后**不自动**开启传感器——移除 `SyncFromHardwareAfterConnect` 中的 `SetSensor(true)`，由用户手动点击「开启相机」控制。
3. 帧率切换保护（`UpdateFpsDropdownState` / `btnApplyFps_Click`）从 `IsCaptureCameraOn()` 改为 `IsSensorRunning()`——传感器运行时才禁止切帧率。
4. 按钮状态同步从 `hwStatus.CaptureCameraOn` 改为 `hwStatus.SensorRunning`。

**结论**

- 用户视角的「相机开关」=「数据采集开关」= 传感器使能（`SetSensor`），不是采集相机电源（`SetCaptureCamera`）。
- 采集相机电源是更低层的硬件控制，用户不需要感知这个层级。
- 「激光按钮仅控激光、相机按钮仅控相机」的前提是：相机按钮控制的是**传感器使能**（回调源头）。

### 3.6 DetectHardwareStatus 应同步更新 _scanRateHz

**现象**

相机已设置到最高帧率档位（HIGH_SPEED），重新连接后页面显示的帧率仍是默认标准值（60Hz），与硬件实际状态不符。

**根因**

`_scanRateHz` 字段仅在 `OpenSensor()` 和 `ApplyFrameRateModel()` 设置成功后更新，`DetectHardwareStatus()` 虽然从硬件读取了实际 FPS 并写入 `IlHardwareStatus.CurrentFps`，但**没有同步回 `_scanRateHz` 字段**。连接后 `ScanRateHz` 属性仍保留构造时的默认值（60Hz）。

**修复**

`DetectHardwareStatus()` 读取 `FetchSensorFps` 成功且 `fps > 0` 时，同步更新 `_scanRateHz = (double)fps`，确保 `ScanRateHz` 属性始终反映硬件实际帧率。

**结论**

- 任何从硬件读取实际帧率的路径，都应同步更新 `_scanRateHz`，不能只存入返回值快照。
- `ScanRateHz` 是对外公开的「当前帧率」契约属性，调用方（如 `LLCamWorkJob` 帧率显示、工作流超时缩放）依赖其准确性。

---

### 3.7 回调周期由 SetSensorCommPeriod 控制

**现象**

实测回调帧率始终在 30fps 左右，即使传感器帧率设置为 60Hz/120Hz 档位，回调频率也上不去。

**根因**

英莱 SDK 的 `MillionOutlineInspect` 回调频率不仅受传感器帧率模式（`SetSensorFpsModel`）限制，还受**数据通信周期**控制。`SetSensorCommPeriod` 函数通过 `IntelligentSdkCommCtrl` 结构体设置回调发送周期和缓冲时长，若未显式配置，可能使用 SDK 默认的较慢周期。

**结构体定义**

```csharp
// CppSharp 生成的托管包装（8 字节，两个 uint）
public class IntelligentSdkCommCtrl : IDisposable
{
    public uint DwSendCycle { get; set; }      // 发送周期（ms）
    public uint DwBufferDuration { get; set; } // 缓冲时长（ms）
}
```

**推荐配置（英莱技术支持建议）**

| 参数 | 值 | 说明 |
|------|----|------|
| `DwSendCycle` | 10 | 发送周期 10ms，理论回调频率上限约 100Hz |
| `DwBufferDuration` | 1000 | 缓冲时长 1000ms，平滑数据传输 |

**调用时机**

在 `ConnectCore` 连接成功后（`ConnectToSensor` 返回成功）立即调用，确保传感器开始工作前回调周期已配置到位。失败仅记 warning 日志，不影响连接结果。

```csharp
using (var commCtrl = new IntelligentSdkCommCtrl())
{
    commCtrl.DwSendCycle = 10u;
    commCtrl.DwBufferDuration = 1000u;
    int ret = IntelligentLaser_export.SetSensorCommPeriod(commCtrl, 1u);
    if (ret != 0) { /* 记 warning，不影响连接 */ }
}
```

**注意事项**

- 实际回调帧率 = min(传感器帧率, 通信周期频率)。设置 10ms 周期后，60Hz 档位下回调帧率应接近 60fps，120Hz 档位下应接近 100fps。
- `dwInstanceId` 须传 `1u`（与其他 SDK 函数一致，详见 §5.7）。
- 回调频率还受算法复杂度、PC 性能、网络带宽等因素影响，以上为理论上限。

---

## 4. 校准框绘制

### 4.1 demo 校准框角点公式隐含「原点在中心」假设

**问题现象**

英莱相机显示画面**四边框缺失/上半部分被裁、十字交叉不居中**。

`ConvertContourToMatDemo` 照搬官方 demo `Form1.cs` `resetInnerData()`（564-634）的角点公式绘制校准框：

```csharp
// demo resetInnerData 角点（绝对角点坐标 × rate，相对中心对称展开）
LeftTop    = (m_posCenter.X - |LeftTopCorner[0]    * rate|, m_posCenter.Y - |LeftTopCorner[1]    * rate|);
LeftBottom = (m_posCenter.X - |LeftBottomCorner[0] * rate|, m_posCenter.Y + |LeftBottomCorner[1] * rate|);
// ... rightTop/rightBottom 同理
```

**根因分析**

该公式用**绝对**角点坐标（`LeftTopCorner[1]` 等，物理 mm）直接乘 `rate` 当作相对中心的偏移，
**只有当校准坐标系原点是画面中心（即 `Center≈(0,0)`）时才成立**（此时 `|corner| = |Center-corner|`）。

但 demo 的同一边上：
- `center.Y = (H-2m)*fPersent + 2m`，其中 `fPersent = |Center[1]-LeftTopCorner[1]|/cornerH`（中心到顶部的 mm 距离占比）
- 而顶边用 `|LeftTopCorner[1]|*rate`（绝对，非 `|Center[1]-LeftTopCorner[1]|*rate`）

当真机 `Center[1] ≠ 0`（高度 mm 原点不在矩形中心）时，二者不一致 → 顶边上移 `Center[1]*rate` 像素 → **顶部被裁**、校准框歪斜、十字不居中。

**修复方案（2026-08-18 终版）**

**恢复 demo 原版角点公式，仅改 `center` 为图像中心**：

```csharp
// rate = cornerW/cornerH（同 demo，不变）
rate = min((w-2m)/cornerW, (h-2m)/cornerH);

// 唯一改动：center 直接设为图像中心（弃用 demo 的 fPersent/dwOffset）
center = (w/2, h/2);

// 角点公式同 demo（center ± |corner*rate|）
corners[0] = (center.X - |LeftTop[0]*rate|, center.Y - |LeftTop[1]*rate|);
// trans 同 demo
trans = (y, z) => (center.X + y*rate, center.Y - z*rate);
// 栅格原点(0,0) 在图像中心
screen_x = center.X + mm*rate;  screen_y = center.Y - mm*rate;
```

**关键**：demo 的角点/trans 公式本身正确，只是 `center` 的 `fPersent/dwOffset` 计算未对齐图像中心。修复只需改 `center` 为 `(w/2, h/2)`，其他全部保留 demo 原版。

**中间弯路（must not repeat）**

1. **第一轮**：误把校准框折叠成半宽/半高对称矩形（`center±(halfW,halfH)`）——丢梯形，被拒。**居中 ≠ 可改形状**。
2. **第二轮**：用 `originX/originY` 间接映射，引入 mm 原点(0,0) 概念——负值 mm 溢出，被拒。
3. **第三轮**：用 `halfExtent` + `(corner-Center)` 相对偏移——自创公式偏离 demo 正确逻辑，被拒。
4. **终版**：**demo 原版公式 `center ± |corner*rate|` + `trans = center + mm*rate`，仅改 `center = (w/2, h/2)`**。**不要自创公式——demo 本身是对的，只是 center 没对齐图像中心**。

**通则**

1. **移植厂商 demo 几何公式时，先核实其坐标系假设**（如「原点=画面中心」）。demo 数据对称时公式看似正确，换真机数据即失效。
2. **"居中显示" ≠ "校正形状"**：默认只平移/缩放、保持被观察对象真实拓扑。
3. **以标定中心点（而非 mm 原点）为视图基准**：`calib.Center` 是唯一有意义的锚点，所有屏幕坐标应相对它计算。

---

## 5. UI 层与状态管理

### 5.1 相机开启时禁止切换帧率（SDK 运行时限制）

**问题**

采集相机开启状态下调用 `SetSensorFpsModel` 切换帧率模式，SDK 会报错（返回非 0）。原因是帧率模式涉及传感器采集管道的重配置，采集运行中无法热切换。

**影响**

- 用户在相机开启状态下切换帧率 → 失败提示，体验差。
- 若 UI 未做保护，频繁失败提示可能导致用户误以为 SDK 或设备故障。

**修复 / 规避**

1. **UI 层下拉禁用**：`ILCamPage.UpdateFpsDropdownState()` 根据 `IsCaptureCameraOn()` 结果设置 `cmbFps.Enabled`——相机开启时禁用，关闭时恢复。
2. **二次校验**：`cmbFps_SelectedIndexChanged` 中再次检查相机状态，若已开启则弹警告并回滚下拉选中项（`RefreshFpsSelect()`）。
3. **自动模式下已禁用**：`UpdateModeUi` 自动运行分支也会禁用 `cmbFps`，双重保险。

**通则**

- 涉及硬件运行时配置变更的操作，先查硬件状态再决定 UI 可用性，不要依赖用户自觉。
- 下拉/按钮等交互控件须有「前置检查 + 后置回滚」双重保护。

### 5.2 实测 FPS 首帧必须剔除

**问题**

从第一次拿到数据开始计算帧率时，第一次计算的帧间隔是「上次重置时间 → 第一帧」的时间差，这个间隔可能很长（几秒甚至几分钟），导致 FPS 值极小，完全错误。

**影响**

- 相机刚开启时，实测 FPS 标签显示异常低的值（如 0.1Hz），误导用户。
- 需等第二帧后才恢复正常值，第一帧错误值闪烁体验差。

**修复 / 规避**

1. **首帧剔除机制**：用 `_firstFrameSkipped` 标志位，第一帧只记录 `_lastFrameTime`、不计算 FPS；从第二帧开始用 `1000ms / 帧间隔(ms)` 计算。
2. **重置时机**：`ResetMeasuredFps()` 将 `_lastFrameTime` 置 `MinValue`、`_firstFrameSkipped` 置 false、`_measuredFps` 置 0。`SetSensor(true)` 开启采集时自动调用重置，确保每次重开都从干净状态开始。
3. **UI 显示**：`lblMeasuredFps` 初始文本 "实测帧率：0.0 Hz"，首帧期间保持 0.0，第二帧后开始显示真实值。

**通则**

- 任何基于「两次间隔」的实时计算，首次数据点都要做剔除或标记处理。
- 计数器/计时器重置后，第一次结果不可信。

### 5.3 UI 层禁止直接引用 SDK 原生类型

**问题**

UI 层（`UIDesign/` 目录下）代码直接 `using IntelligentLaser_CSharp;` 并使用 SDK 原生枚举（如 `EmIntelligentFpsModel`）、原生结构体，违反「UI 不直接触碰 SDK」的分层原则——SDK 版本升级或更换厂商时，UI 层也要跟着改，且 UI 层依赖 SDK 原生类型增加了耦合面。

**影响**

- UI 层与 SDK 强耦合，换相机厂商时 UI 需大量改动。
- SDK 枚举值变化（重命名、值调整）会波及 UI 代码，不符合「UI 只依赖业务层接口」的架构原则。

**修复 / 规避**

1. **托管枚举**：在 `IntelligentLaserCameraRun.cs` 同命名空间下定义 `IlFpsModel` 托管枚举（STANDERD=1/FAST_SPEED=2/HIGH_SPEED=3），UI 层只使用此托管枚举。
2. **公共方法重载**：`ApplyFrameRateModel(IlFpsModel)` 做 UI 层入口，内部映射到 SDK 枚举后调用私有 `ApplyFrameRateModel(EmIntelligentFpsModel)` 实现。SDK 原生枚举版本降为 `private`。
3. **UI 移除 SDK using**：`ILCamPage.cs` 移除 `using IntelligentLaser_CSharp;`，整个 `UIDesign/` 目录零 SDK 引用（已 `grep` 全量验证）。
4. **状态查询方法化**：`IsCaptureCameraOn()` / `IsSensorRunning()` / `FetchFpsModel()` / `DetectHardwareStatus()` 等方法封装所有 SDK 状态查询，UI 只调用方法、不触碰 SDK 类型。

**通则**

- UI 层依赖业务层接口，不直接引用第三方 SDK 类型。
- 所有 SDK 原生枚举/结构体在业务层做托管封装（命名空间同级），UI 只使用托管类型。
- 新增公共方法时，优先考虑 UI 层是否需要引入 SDK 命名空间——若需要，应增加托管重载。

### 5.4 连接后必须检测硬件实际状态

**问题**

程序异常退出（崩溃、强制结束进程）后重新连接，SDK 的 `ConnectToSensor` 只是建立网络连接，**不会改变硬件端的激光/相机/传感器状态**——上次开启的激光和相机仍然开着，但软件侧 `_isLaserOn`/`_isCaptureCameraOn` 等状态变量初始为 false，导致 UI 显示与硬件实际状态不一致。

**影响**

- UI 显示「激光已关」但实际激光开着 → 安全隐患。
- UI 显示「相机已关」但实际相机开着 → 用户点「开启相机」可能导致重复开启或 SDK 报错。
- 帧率下拉在相机实际开启时仍可操作 → 切换帧率报错（见 5.1）。
- JOB 参数页面显示离线缓存的默认值，而非当前设备实际值 → 误导用户。

**修复 / 规避**

1. **连接后状态检测**：`ILCamPage.btnConnect_Click` 在 `ConnectManual` 成功后调用 `_ilCamera.DetectHardwareStatus()`，获取 `IlHardwareStatus` 快照（LaserOn / CaptureCameraOn / SensorRunning / FpsModel / CurrentFps），同步到 UI 状态变量与控件文本。
2. **状态查询方法**：`IsLaserOn()`（已有）/ `IsCaptureCameraOn()`（新增，`FetchSensorInfo`→`DwCaptureCameraEnable`）/ `IsSensorRunning()`（新增，`FetchSensorFps` > 0 判断）/ `FetchFpsModel()`（新增，`FetchSensorFpsModel`）分别查询单项状态。
3. **帧率下拉状态联动**：`UpdateFpsDropdownState()` 根据 `IsCaptureCameraOn()` 动态设置可用/禁用，相机开启时禁用帧率切换。
4. **算法编辑页实时参数**：`ILAlgoForm.InitIlModule` 连接时优先 `FetchAllJobParams()` 从设备拉取实时参数，失败才回退离线缓存，确保展开的是当前 Job 的参数。

**通则**

- 「连接」≠「状态重置」——网络连接仅建立通信，硬件端状态不受影响。
- 连接后必须做一次全量状态同步（激光、相机、传感器、帧率模式、当前 JOB 等）。
- UI 状态变量的真值来源是硬件查询结果，而非软件初始值。

### 5.5 手动/自动模式数据流必须分离

**现象**

自动模式（工作流运行）下，`ILCamPage` 仍在回调中刷新轮廓图像和结果表格，与「自动模式数据应外传至 ScottPlot 和自动调整计算」的架构设计不符。页面上还额外提供一个「自动显示」Switch 开关让用户手动控制，增加了复杂度。

**根因**

`ILCamPage.OnContourFrameReady` → `RefreshDisplay()` 无条件刷新画面、轮廓点数、实测帧率、结果表。工作流自动运行时，页面仍在做 UI 绘制，既浪费性能，又造成「同一帧数据既在本页显示又外传」的双重消费混淆。

**修复**

1. `RefreshDisplay()` 增加模式守卫：工作流运行中（自动模式）直接 `return`，不刷新任何 UI 元素。
2. 仅手动/空闲模式下，在本页绘制 Mat（`ShowMat`）、轮廓点数、实测 FPS、结果表。
3. 自动模式下，数据通过 `ContourDataReady` 事件外传：
   - 轮廓数据 → 主页面 ScottPlot 实时显示
   - 焊缝特征点 + 宽度 → 自动调整计算模块
4. 移除「自动显示」`swDisplay` Switch 控件及所有相关逻辑（构造订阅、CheckedChanged、销毁取消订阅、`UpdateModeUi` 使能控制）。

**结论**

- 调试页（`ILCamPage`）是**手动模式**的调试工具，自动模式下不应抢数据做显示。
- 数据分发遵循「单源多订阅」：相机回调是唯一源，`ContourFrameReady`（UI 显示用，节流）和 `ContourDataReady`（数据消费用，全量）是两条独立链路。
- 自动模式下，数据消费者是工作流和 ScottPlot，不是调试页面。

### 5.6 双帧率显示：传感器帧率 vs 回调帧率

**概念区分**

英莱相机有两个不同的帧率概念，UI 上应分别显示、避免混淆：

| 帧率类型 | 来源 | 含义 | 显示位置 |
|---------|------|------|---------|
| **传感器帧率**（ScanRateHz） | `FetchSensorFps` / `SetSensorFpsModel` 设置后读取 | 传感器硬件的采集分析频率（目标帧率），由帧率模式档位决定 | `lblSenorfps`（中列） |
| **回调帧率**（MeasuredFps） | `MillionOutline` 回调逐帧计算（1000ms/帧间隔） | 实际收到回调的帧率，受数据处理、线程调度影响 | `lblMeasuredFps`（右列） |

**设计要点**

- 传感器帧率是**硬件能力/设定值**，连接后从硬件读取一次即可，不会频繁变化
- 回调帧率是**实测值**，每帧更新，首帧剔除后才准确
- 两个帧率并排显示，方便用户判断：回调帧率是否跟上了传感器设定帧率（如果回调帧率显著低于传感器帧率，说明处理链路有瓶颈）

**运行时实时刷新（2026-08-20 修复）**

`ScanRateHz` 不能只在连接时和设置帧率时各读一次——传感器实际帧率可能因曝光、激光强度、环境等因素波动，且用户需要通过它判断「传感器是否达到设定档位」。

修复方案：在 `MillionOutlineCallback` 中增加**节流式硬件查询**，每 500ms 调用一次 `FetchSensorFps` 更新 `_scanRateHz`。

```
传感器帧率刷新策略 = 回调驱动 + 500ms 节流
  ↓
每帧回调进入 → 距上次查询 ≥ 500ms ? → 是 → FetchSensorFps → 更新 _scanRateHz
                                 → 否 → 跳过
```

为什么是 500ms：
- `FetchSensorFps` 是 SDK 硬件查询，有网络/寄存器访问开销
- 60~120fps 回调中每帧查询会显著增加 CPU 占用
- 500ms（2Hz）对 UI 显示来说足够流畅，人眼感知为"实时"
- 帧率是缓慢变化的量，不需要毫秒级精度

**通则**

- 涉及帧率的 UI 必须明确标注是「传感器帧率」还是「回调帧率」，不能笼统写「实测帧率」
- 传感器帧率对应 `ScanRateHz` 属性，回调帧率对应 `MeasuredFps` 属性
- 传感器帧率必须**运行时周期性刷新**，不能只在连接/设置时读一次
- 硬件查询类 API 在回调中使用必须做**节流处理**，不能每帧调用

---

## 5.7 dwInstanceId 参数陷阱

**现象**

- `FetchSensorFpsModel` 返回 `ret=16777216 (0x1000000)` 即 `INTELLIGENT_E_UNINIT`（程序未初始化）
- `IsSensorRunning` 始终返回 false
- 传感器帧率（`ScanRateHz`）始终为 0 或默认值，不刷新
- `DetectHardwareStatus` 读不到帧率

**根因**

英莱 SDK 中几乎所有函数都有一个 `uint dwInstanceId` 参数，**默认值为 1**（对应第一个传感器实例）。如果代码中显式传 `0u`，SDK 会返回 `INTELLIGENT_E_UNINIT` 错误码（实例 0 不存在/未初始化）。

```csharp
// SDK 定义：dwInstanceId 默认值为 1
public static int FetchSensorFps(ref float fFps, uint dwInstanceId = 1)
public static int FetchSensorFpsModel(ref EmIntelligentFpsModel emLevel, uint dwInstanceId = 1)
public static int SetSensorFpsModel(EmIntelligentFpsModel emLevel, uint dwInstanceId = 1)
```

**易错点**

代码中容易出现混用——有些地方使用默认值（正确，实例 1），有些地方显式传 `0u`（错误，实例 0 未初始化）。

```csharp
// ✅ 正确：使用默认值（dwInstanceId = 1）
IntelligentLaser_export.SetSensorFpsModel(model);
IntelligentLaser_export.FetchSensorFps(ref fps);

// ✅ 正确：显式传 1u
IntelligentLaser_export.FetchSensorFps(ref fps, 1u);

// ❌ 错误：传 0u，实例 0 未初始化，返回 INTELLIGENT_E_UNINIT
IntelligentLaser_export.FetchSensorFps(ref fps, 0u);
IntelligentLaser_export.FetchSensorFpsModel(ref model, 0u);
```

**排查方法**

- 遇到 SDK 调用返回 `0x1000000` 时，优先检查 `dwInstanceId` 参数
- 搜索代码中所有 `IntelligentLaser_export.*, 0u)` 模式，确认是否为误传
- 单传感器场景下，统一使用默认值或显式 `1u`

**通则**

- 单传感器场景：**始终使用 SDK 默认值（不传 dwInstanceId）**，避免手写错误
- 如需显式传参：传 `1u`，不传 `0u`
- 新增 SDK 调用时，检查是否有 `dwInstanceId` 参数，确认传值正确
- 代码审查时重点检查 `0u` 参数是否为 `dwInstanceId`

---

### 5.8 回调模式分流：手动/自动模式数据路径必须分离

**问题背景**

英莱线激光相机有两种使用模式：
- **手动模式**：在 `ILCamPage` 手动调试，需要实时显示轮廓画面（Mat）+ 结果表 + 帧率标签
- **自动模式**：工作流运行中，只需要轮廓数据和算法结果外传（ScottPlot + 自动调整计算），不需要在相机页面显示画面

如果两种模式共用同一条回调路径（都生成 Mat + 都触发 UI 事件），自动模式下会浪费大量 CPU/GPU 在无用的画面渲染上。

**最佳实践：回调两步结构**

```
MillionOutlineCallback
├── 第一步：拿数据（所有模式共用，必须执行）
│   ├── 原生数据读取（using inspect）
│   ├── 轮廓点计数 → _lastContourCount
│   ├── 实测 FPS 计算（首帧剔除）
│   ├── 传感器 FPS 刷新（500ms 节流）
│   ├── 构建 PointCloudData
│   └── 读取 InspectResult → _lastInspect
│
└── 第二步：模式分支
    ├── 手动模式 (IsManualMode=true)
    │   ├── 生成/复用 Mat（ConvertContourToMatDemo：持久画布 Clear 重绘 + CopyTo 原地更新 _currentMat，不再每帧 new；2026-08-26 移除双缓冲换帧，详见 §5.10）
    │   ├── AcquisitionCompletedSignal.Set()
    │   ├── 数据记录（AddFrame）
    │   ├── ContourDataReady 事件（数据外传）
    │   └── NotifyFrameReady → ContourFrameReady（UI 刷新）
    │
    └── 自动模式 (IsManualMode=false)
        ├── AcquisitionCompletedSignal.Set()
        ├── 数据记录（AddFrame）
        └── ContourDataReady 事件（仅数据外传，不生成 Mat，不触发 UI）
```

**关键设计点**

1. **第一步拿数据与模式无关**：所有模式都需要读取原生数据、计算 FPS、构建点云、捕获算法结果。这部分不做模式判断，保证数据完整性。
2. **第二步模式互逆**：手动模式生成 Mat 并触发 UI 事件；自动模式不生成 Mat、不触发 UI 事件，仅外传数据。两条路径完全独立，互不干扰。
3. **IsManualMode 属性控制**：由调用方（UI 页面或工作流）设置，默认 true（兼容手动调试场景）。`ILCamPage.UpdateModeUi` 中根据工作流运行状态自动切换。
4. **减少临时变量**：自动模式完全不分配 Mat 对象；手动模式改为**复用持久画布 + 持久 `_currentMat`**（2026-08-26 重构，详见 §5.10），进一步消除每帧 `new Bitmap/Graphics/Mat` 分配，原「双缓冲换帧」已移除。移除不必要的中间引用变量（如 `var contour = inspect.ContourData`）。
5. **状态标签始终更新**：UI 页面的轮廓点、传感器帧率、回调帧率等状态标签不受模式限制，自动模式下也应实时显示（移到模式判断之前更新）。

**验证方法**

- 手动模式：确认画面正常刷新、结果表更新、帧率显示正确
- 自动模式：确认 `ContourDataReady` 事件正常触发、ScottPlot 有数据、工作流调整正常；确认 `ContourFrameReady` 不触发、`CurrentMat` 不更新（节省资源）
- 对比两种模式下的 CPU/GPU 占用率，自动模式应有明显下降

---

### 5.9 主界面轮廓 ScottPlot 必须每帧 Refresh（刷新放错分支导致冻结）

**问题现象**

主界面（`MainPage`）英莱轮廓 ScottPlot 出现「轮廓显示不对、运到（运行时）不刷新」。

**根因**

`MainPage.IlCamera_ContourDataReady` 回调里，信号处理（填充 `double[1920]` Signal 数组、`MaxRenderIndex` / `SampleRate` / `OffsetX`、特征点 `IsVisible`）每帧都执行，但 **`SetAxisLimits` + `Refresh()` 被放在 `else`（无有效焊缝结果）分支内**：

```csharp
if (e.HasValidResult)
{
    _featureXs[0] = e.Inspect.FeatureY; ...
    _featurePointPlot.IsVisible = true;   // 有焊缝时只显特征点
}
else
{
    _featurePointPlot.IsVisible = false;
    formsPlot1.Plot.SetAxisLimits(...);
    formsPlot1.Refresh();                 // ← Refresh 仅在此分支执行
}
```

生产态一旦 `HasValidResult==true`（识别出焊缝，正常工况），整帧既不重设轴范围也不 `Refresh()` → 轮廓曲线与特征点**永久冻结**，表现为「画面不动、轮廓陈旧/错位」。

**修复（2026-08-26）**

将 `SetAxisLimits` + `Refresh()` 提到分支外，**每帧**执行（与 ADR-024 Signal 模式「每帧原地修改数组 → Refresh 重绘」设计一致）。`AddContourLineChart` 订阅入口（`FormMain` 构造已显式调用）正常，根因就是刷新语句位置错误，非订阅/初始化问题。

**通则**

- ScottPlot（任何模式）的 `Refresh()` 必须与数据更新放在**同一控制流**中；切勿把刷新塞进某个条件分支，否则该分支不命中时画面冻结。
- 实时曲线「不刷新」优先排查 `Refresh()` 是否真的每帧可达，而非先怀疑数据源。

### 5.10 轮廓 Mat 复用持久画布（每帧 Clear 重绘，替代每帧 new）

**问题（用户提问）**

`ConvertContourToMatDemo`（GDI+ 绘制轮廓/校准框/特征点到 `Bitmap` 再 `ToMat()`）原先**每帧** `new Bitmap(834,554)` + `Graphics.FromImage` + `bmp.ToMat()`，回调（手动模式 ~60fps）下产生大量托管 Bitmap 与 unmanaged Mat 分配，GC 抖动大、显示更新延迟高。用户提议：「能否只用一个 Mat，setto0 后重绘？」

**结论（回答用户）**

**可以，且更优**。复用单一 `Bitmap` / `Graphics` / `_currentMat` 的代价：
- **资源占用**：消除每帧约 1.8MB `Bitmap` + `Graphics` + `Mat` 分配，GC 压力与 LOH 碎片显著下降；
- **显示延迟**：省去分配/回收开销，出帧到 `imageBox` 刷新更快；
- **仍线程安全**：`_currentMat` 在 `_matLock` 内原地更新，`CurrentMat` getter 克隆返回，调用方独占。

**修复（2026-08-26 实现）**

- 新增持久字段 `_canvasBmp`(`Bitmap`) / `_canvasG`(`Graphics`) / `CanvasW` / `CanvasH`，`EnsureCanvas()` 首次创建、之后复用；
- `ConvertContourToMatDemo` 改为 `void`，在 `lock(_matLock)` 内：`_canvasG.Clear(bg)` → 沿用原 `g`/`bmp` 绘制逻辑 → `UpdateCurrentMatFromCanvas()`；
- `UpdateCurrentMatFromCanvas()`：首帧 `_currentMat = _canvasBmp.ToMat()`（新建），后续 `_canvasBmp.ToMat()` 临时 Mat `CopyTo(_currentMat)` **原地复用**（同尺寸/类型时零新分配）；
- 回调手动分支移除「双缓冲换帧（`newMat` 交换 + 旧帧 `Dispose`）」，改为直接调用 `ConvertContourToMatDemo`（内部原地更新 `_currentMat`），天然替换原换帧临界区；
- `ReleaseNativeResources` 同步 `Dispose()` `_canvasG` / `_canvasBmp`，避免 GDI 句柄泄漏。

**注意事项**

- 采用 `Bitmap.ToMat()` + `Mat.CopyTo()`（Emgu.CV 4.x 确定性 API），未依赖 `Mat.ImportBitmap`（部分版本无此 API），版本安全。
- 绘制与 `_currentMat` 更新均在 `_matLock` 内串行，与 `CurrentMat` getter 互斥；销毁路径 `_matLock` 与绘制互斥，无竞态。
- 若后续接入 `ImportBitmap` / `Image.Bitmap` 共享内存画法，可进一步消除 `ToMat()` 临时 Mat，但当前 `CopyTo` 复用已满足「单 Mat 复用」目标。

---

### 5.11 主界面轮廓 ScottPlot 轴范围「连接时锁定、每帧只刷新数据」

**问题（用户需求 2026-08-27）**

主界面轮廓图（`MainPage.IlCamera_ContourDataReady`）原先**每帧**重算校准框轴范围 + 每帧 `SetAxisLimits`。用户指出：相机连接后校准数据只更新一次，轴范围（主轴 Y / 纵轴 Z）不变更，每帧重设轴范围既无意义又违背「连接后固定视图」的意图。

**结论 / 修复（2026-08-27 实现）**

- 新增 `bool _contourAxisLocked` 字段：轴范围是否已锁定。
- ① 轴范围计算加 `!_contourAxisLocked` 守卫——**仅首次**有效数据（校准框四角点已就绪）时 `SetAxisLimits` 锁定，并置 `_contourAxisLocked = true`；之后（未重连）跳过整个轴计算与 `SetAxisLimits`。**横轴 X（沿激光线，= 数据 Y 坐标）与纵轴 Y（高度，= 数据 Z 坐标）一律用校准框四角点 min/max 锁定，含负值，加 ±5% 边距**：即用户原「连接相机时用回调确认轴的限度（相机最大最小值，含负值）」方式，范围来自相机校准框、**不随实时数据动态规划上下限/左右限**。
- ④ 每帧只 `formsPlot1.Refresh()` 重绘轮廓与特征点，**不再重设轴范围**。
- `SubscribeContourCamera()` 重订阅时复位 `_contourAxisLocked = false`，使相机切换/重连后用新校准框重新锁定。
- 每帧仍保留生产者线程填充 SignalXY 双数组（`_contourSignalXs[i]=points[i].Y`、`_contourSignalData[i]=points[i].Z`）与特征点快照——纯数据更新，非改轴（详见 §5.16）。

**注意事项**

- 锁定时机 = 相机连接后校准框四角点首次就绪的帧（等价于用户所说「连接时」）；若校准框数据始终不到达，轴保持 `_contourYMin/Max`/`_contourZMin/Max` 默认回退范围（含负值，不锁定、每帧轻量检查）。
- 与 [[decisions/ADR-026-YinglaiDataFlow]] 决策3（Signal 模式每帧刷新）不冲突：刷新照常 60Hz，仅轴范围从「每帧重设」改为「连接时一次锁定」。
- 切勿把 `SetAxisLimits` 重新放回每帧（会回到无意义开销）。校准框量程（含负值）通常远大于单条焊缝 Z 起伏，轮廓在固定相机量程视图下显得平缓属预期——这是用户明确的「固定相机量程」选择，不要为放大起伏而改用数据范围（见 §5.15 回退说明）。

### 5.12 主界面轮廓 Signal 轴映射：Y→X 轴、Z→Y 轴（首末点锚定防镜像）

主界面轮廓 ScottPlot（`MainPage.IlCamera_ContourDataReady`）需显示英莱传来的 `Point3D` 的 **Y 与 Z**：**Y 作 X 轴（沿激光线物理坐标 mm）、Z 作 Y 轴（高度 mm）**。约定与 imageBox 的 `ConvertContourToMatDemo` 坐标变换 `trans(y,z) => (center.X + y*rate, center.Y - z*rate)`（Y→横、Z→纵）保持一致，确保主界面与调试页朝向相同。

**轴赋值本身正确**（已核对）：
- Signal Y 数据 = `points[i].Z`（`_contourSignalData[i] = points[i].Z`）；
- SignalXY X 轴 = 显式数组 `points[i].Y`（`AddSignalXY(xs, ys)` 逐点真实 X，非均匀布点，终版方案）；
- 特征点散点 `_featureXs[0] = e.Inspect.FeatureY`、`_featureYs[0] = e.Inspect.FeatureZ`。

**隐患（曾导致"信号不正确/镜像"）**：原代码用 **全局 Y 极值**（`yMinPt/yMaxPt` = 整帧 min/max）作 `OffsetX/SampleRate`。这隐含假设轮廓点序一定是「小→大」。若英莱 SDK 返回点序为「大→小」（首点 Y = maxY），则 `OffsetX` 取全局 minY、曲线整体**左右镜像**，ScottPlot 与 imageBox 朝向相反——用户观感即"轮廓显示不对"。

**修复（早期方案，已被 §5.16 的 AddSignalXY 取代）**：`OffsetX/SampleRate` 锚定**首末点的真实 Y** 曾用于消除镜像；现终版改用 `AddSignalXY` 显式传 X，详见 §5.16：
```csharp
double yFirst = points[0].Y;
double yLast  = points[pointCount - 1].Y;
double dy = yLast - yFirst;
if (Math.Abs(dy) > 1e-6)
{
    _contourSignalPlot.SampleRate = dy / (pointCount - 1);
    _contourSignalPlot.OffsetX = yFirst;
}
```
- 升序点序（point[0]=minY）下与旧逻辑**数值完全等价**，零回归；
- 降序点序下 `dy<0` → `sampleRate` 为负，曲线自动反向绘制，与 imageBox 一致，消除镜像；
- 仅取首末点，不依赖全局极值，对"点序非严格单调"也最稳健（激光轮廓点沿扫描线基本等距，首末锚定足够）。

**教训**：ScottPlot `AddSignal` 的 X 是「索引×SampleRate+OffsetX」的**均匀布点**，不是逐点真实 X；当轮廓点 X 方向**非等距**时，X 位置算错、线形扭曲甚至局部压平。此类场景应改用 **`AddSignalXY(xs, ys)`**（显式 X + 保留 Signal 性能），而非 `AddScatter`（性能差）。终版见 §5.16。

**坐标系澄清（2026-08-27 用户）**：imageBox 与 ScottPlot **不必一致**。imageBox 因屏幕像素只能取正值、无负值，必须做 `center + y*rate` 平移（把 (0,0) 移到图像中心）才能显示；ScottPlot 直接绘原始数据坐标，**负值如实显示、不做任何平移**。故主界面轮廓与调试页 imageBox 的视图「不重合」属预期，绝不可为"与 imageBox 一致"而给 ScottPlot 加平移/居中。两者仅「朝向」相同（Y→横、Z→纵）。

**英莱轮廓点默认按 Y 轴由小到大排列**：故 `points[0].Y` 即最小、`points[last].Y` 即最大，首末锚定 = min/max；首末锚定对正常升序点序数值等价（零回归），且对点序偶发变化（大→小）也不会镜像（见上方 修复）。

### 5.13 主界面轮廓 Signal 初始不可见（不渲染 Z=0 假轮廓线）

**现象（2026-08-27）**：程序启动、未连接相机时，主界面 ScottPlot 却画出「一段奇怪的轮廓点／一条横线」，用户要求初始化时不要显示无关点。

**根因**：`_contourSignalData = new double[1920]` 全为 0；`AddSignalXY` 默认 `MaxRenderIndex = int.MaxValue` 会渲染全部 1920 个点 → 一条 **Z=0 的平直假轮廓**横跨整个 X 轴。未连接相机时无 `ContourDataReady` 帧，但 Signal 图已绑定该数组，故一打开就显示这条零线。

**修复**：`AddContourLineChart` 中 `AddSignalXY` 之后立即 `_contourSignalPlot.IsVisible = false`（不渲染空/零数据）；`IlCamera_ContourDataReady` 在确认 `pointCount > 0` 后首帧置 `IsVisible = true`；`SubscribeContourCamera()`（重订阅/重连）复位 `IsVisible = false` 防残留。默认轴范围（`SetAxisLimits` 默认回退值）仍保留，呈现干净的「空坐标 + 标签」无数据态，而非假轮廓线。

**教训**：Signal 图绑定固定数组时，初始化必须 `IsVisible=false` 或 `MaxRenderIndex=-1`，**绝不可让全 0 数组直接渲染**。与 §5.9（每帧 Refresh）不冲突：刷新照常，只是首帧前不显示。特征点散点（`_featurePointPlot`）本就初始 `IsVisible=false`，无需改动。

---

### 5.14 主界面轮廓 ScottPlot：高频事件禁止逐事件 BeginInvoke + 重活（合并派发 + 生产者预拷贝）

**问题现象（2026-08-27）**：使用 ScottPlot 后 ① 程序内存持续上涨 ② 主页面卡死、只有轮廓表在动。同时轮廓被报「显示为一条直线」。

**根因**：
- ①+② 同一根因：`ContourDataReady` 在相机回调内**无条件高频触发**（对比 `NotifyFrameReady` 有 16ms 节流，此处没有）。旧 `IlCamera_ContourDataReady` 用 `BeginInvoke` **逐事件**把「1920 点数组填充 + 首帧 SetAxisLimits + 全量 Refresh 重绘」整段重活封送 UI 线程。当相机帧率 > UI 刷新能力时，BeginInvoke 队列**无界堆积** → 委托 + 捕获的 `ContourDataEventArgs` + 数组拷贝越积越多（内存↑），UI 线程被渲染占满（卡死、仅图表在动）。
- ③（直线）根因确认：经对比 ImageBox（可见起伏）与 ScottPlot（平线），确认是**校准框量程（含负值，通常 ±几 mm 乃至更大）远大于单条焊缝 Z 起伏（0.0x~0.x mm）**，轮廓在固定相机量程视图下显得平缓。用户明确选择保留「连接时校准框量程锁定」（§5.11 终版），故此「平缓」属预期；曾尝试的「纵轴 Z 用数据实际范围锁定」已回退（见 §5.15）。「延迟读被回收缓冲」(b) 已由生产者预拷贝消除，「字段错」(c) 已排除（Y→X/Z→Y 映射正确，与 ImageBox 一致）。

**修复（2026-08-27 实现）**：
- 删去临时调试 `return;` 桩，恢复回调工作。
- **生产者线程立即预拷贝**：回调一进来先把 `points[i].Z`、Y 映射、特征点、首帧校准判定拷入复用数组/快照字段，再派发——彻底消除「延迟读被回收缓冲」（候选③-b）。
- **合并派发**：用 `volatile bool _uiUpdatePending` 保证 BeginInvoke 队列**最多 1 个待处理**（`if (_uiUpdatePending) return; _uiUpdatePending=true; BeginInvoke(UpdateChartUI)`），根治队列堆积（内存↑/卡死）。
- **`UpdateChartUI`（UI 线程）只做轻量**：应用轴锁定一次 + `MaxRenderIndex`（X 由显式 `_contourSignalXs` 给定，无需 `SampleRate`/`OffsetX`） + 特征点显隐 + `Refresh()`，`finally` 复位 `_uiUpdatePending`；ScottPlot 属性只在 UI 线程触碰，避免跨线程。
- **诊断代码已删除（2026-08-27 用户要求）**：原 `_contourDiagEnabled`/`_diagFrameCounter` 诊断门控（每 ~30 帧打印 `Z` 数据与锁定轴范围）已整体移除，不再保留于代码中。

**教训**：
- 高频相机/传感器事件**禁止逐事件 `BeginInvoke` + 在封送体内做重活**；必须「生产者预拷贝数据 + 合并/节流派发（volatile 标志或 Timer 限 ~60Hz）」，否则必现内存泄漏 + UI 饱和。
- 跨线程传递数据**不要延迟读调用方缓冲**：在生产者线程立即拷进自己的复用数组，封送只传「已落定的快照」。
- 与 ADR-024 Signal 模式「每帧刷新」、§5.9（每帧 Refresh）、§5.11（轴锁定：校准框量程）、§5.12（Y→X/Z→Y）、§5.13（初始不可见）、§5.16（AddSignalXY）均不冲突：刷新照常，仅把「数据拷贝」与「UI 重绘」拆到两个线程。

---

### 5.15 主界面轮廓 ScottPlot：曾尝试「纵轴 Z 用数据实际范围」已回退为校准框量程（§5.11 终版）

**现象（2026-08-27 早期尝试）**：ScottPlot 轮廓显示为一条水平直线，而同数据的 ImageBox 显示明显起伏的倾斜轮廓。

**早期根因与修复（已回退）**：原 §5.11 首帧锁定时横轴/纵轴均用**校准框**四角点范围（含负值，覆盖整个视野，通常 ±几 mm）。实际焊缝在该视野内的 Z 向起伏往往只有 **0.0x ~ 0.x mm**，在 8mm 级纵轴里几乎不可见 → 看起来是平线。ImageBox 的 `ConvertContourToMatDemo` 在校准模式下把同一小变化放大成多像素，放大倍率不同，并非数据问题。曾改为「纵轴 Z 用本帧数据实际 min/max + 边距、横轴用校准框范围」以放大起伏。

**回退决定（2026-08-27 用户明确要求）**：用户确认轮廓轴范围**使用原方式**——连接相机时用回调确认轴的限度（相机最大最小值，含负值），**不实时规划上下限/左右限**。即终版以 §5.11 的「校准框四角点 min/max + ±5% 边距、连接时锁定一次」为准。「平缓」是固定相机量程视图的固有表现，可接受，不应为放大起伏而改用数据范围。

**注意**：本条目仅作历史记录，防止误把已否决的「数据范围」方案重新引入；当前权威结论见 §5.11。

---

### 5.16 主界面轮廓 ScottPlot：X 非等距必须用 AddSignalXY，而非 AddSignal / AddScatter

**结论（2026-08-27 用户确认）**：轮廓点沿激光线的物理坐标 Y 在 X 方向**非等距**（相机采样疏密不均、偶发空档）。

- `AddSignal(ys)`：X 只能靠 `SampleRate`/`OffsetX` 推算**等距**布点 → 点序非均匀时 X 位置算错、线形扭曲/局部压平。
- `AddScatter(xs, ys)`：支持非等距 X，但属通用散点、**逐点绘制、性能差**（1920 点高频刷新拖累帧率）。
- **`AddSignalXY(xs, ys)`（终选）**：X 由显式数组逐点给定（支持非等距），且**仍走 Signal 高性能渲染路径**（Min/Max 降采样 + 零分配），兼顾正确性与性能。

**落地（2026-08-27 实现）**：`MainPage.AddContourLineChart` 用 `AddSignalXY(_contourSignalXs, _contourSignalData)`；生产者线程 `_contourSignalXs[i] = points[i].Y` 与 `_contourSignalData[i] = points[i].Z` 一并预拷贝；`UpdateChartUI` 不再设 `SampleRate`/`OffsetX`。字段 `_contourSignalXs` 与 `_contourSignalData` 同长 1920，复用不每帧分配。

**注意**：`AddSignalXY` 按数组顺序连线，要求 X 单调（升/降）才能正确连成轮廓；本项目英莱点序默认按 Y 升序，符合。若点序偶发非单调，线会折线/乱跳，需排序或回退 `AddScatter`。

---

## 6. 委托 GC 保护与 CallbackOnCollectedDelegate

### 6.1 问题现象

托管调试助手（MDA）报错：`CallbackOnCollectedDelegate`——"对 `IntelligentMillionOutlineInspectCallBack::Invoke` 类型的已垃圾回收委托进行了回调。这可能会导致应用程序崩溃、损坏和数据丢失。"

### 6.2 根因分析

英莱 SDK 的 `IntelligentRegisterCallBack_*` 系列函数接收托管委托，将其转换为函数指针后保存在非托管侧。回调触发时，非托管侧通过该函数指针调用回托管代码。

**常见误区**：以为只要用 `GCHandle.Alloc(this)` 钉住了宿主对象，委托就不会被回收。实际上：

1. **委托是独立对象**：`_cbMillionOutline = new IntelligentMillionOutlineInspectCallBack(MillionOutlineCallback)` 创建了一个委托实例，该实例持有对 `this` 和方法 `MillionOutlineCallback` 的引用。
2. **`GCHandle.Alloc(this)` 只钉住了 `this`**：`this` 引用了委托字段，但 GC 在压缩时可能只扫描到 `this`→委托的引用链，而**非托管侧持有的函数指针不被 GC 视为根引用**。当代码中长时间没有托管路径通过 `this` 访问委托字段时，GC 可能判定委托不可达并回收。
3. **JIT 优化可能提前判定对象死亡**：在回调方法执行过程中，如果 JIT 判定后续代码不再访问 `this` 的任何字段，可能在方法执行中间就将 `this` 标记为可回收，导致委托也被回收（极端情况）。

**释放路径泄漏**：`ConnectCore` 失败路径（`UnInitSDK()` 后未释放 `_hostHandle`）与 `DisconnectManual`（未释放 `_hostHandle`）导致 GCHandle 泄漏，句柄数随重连次数递增。

### 6.3 修复方案（标准三层防御）

**第一层：每个委托独立 GCHandle 钉住（核心修复）**

每个传递给非托管代码的委托都必须有**独立的** `GCHandle` 作为 GC 根，而不能仅依赖宿主对象的字段引用间接保活。

```csharp
// 字段：每个委托对应一个 GCHandle
private IntelligentMillionOutlineInspectCallBack _cbMillionOutline;
private GCHandle _hCbMillionOutline;       // 独立句柄

// 注册时钉住
_cbMillionOutline = new IntelligentMillionOutlineInspectCallBack(MillionOutlineCallback);
_hCbMillionOutline = GCHandle.Alloc(_cbMillionOutline);  // 直接钉住委托

// 释放时单独释放
if (_hCbMillionOutline.IsAllocated) _hCbMillionOutline.Free();
```

**第二层：回调方法末尾加 `GC.KeepAlive(this)`**

```csharp
private void MillionOutlineCallback(IntPtr pOutlineData, IntPtr pUser, uint dwInstanceId)
{
    // ... 回调处理逻辑 ...
    
    // 防止 JIT 在方法执行中提前回收 this
    GC.KeepAlive(this);
}
```

`GC.KeepAlive(this)` 确保 `this` 在方法执行期间始终被视为存活，间接保证委托不被回收。这是 P/Invoke 回调的标准防御模式。

**第三层：释放路径全覆盖**

所有会导致 SDK 停止回调的路径都必须释放委托 GCHandle：
- `ReleaseNativeResources()`（Dispose / 析构）
- `ConnectCore` 失败路径（`UnInitSDK()` 后）
- `DisconnectManual`（手动断开时）
- `RegisterCallbacks` 重试前清理（调用 `FreeCallbackHandles()`）

统一封装释放方法：
```csharp
private void FreeCallbackHandles()
{
    if (_hCbMillionOutline.IsAllocated) _hCbMillionOutline.Free();
    if (_hCbInitJobParams.IsAllocated) _hCbInitJobParams.Free();
    if (_hCbCalibration.IsAllocated) _hCbCalibration.Free();
}
```

### 6.4 验证方法

1. 启用 MDA：在 Visual Studio 中「调试 → 异常 → 托管调试助手 → 勾选 CallbackOnCollectedDelegate」
2. 运行程序，开启英莱相机，让回调持续触发几分钟
3. 手动断开→重连多次，观察是否有 MDA 报错
4. 在回调触发期间手动触发 GC（`GC.Collect(); GC.WaitForPendingFinalizers();`），验证无崩溃

### 6.5 通则

- **向非托管代码传递委托时，每个委托都必须有独立的 GC 根引用**（`GCHandle.Alloc(delegate)` 或 `static` 字段），不能仅依赖宿主对象字段间接保活。
- **回调方法末尾加 `GC.KeepAlive(this)`** 是 P/Invoke 回调的标准最佳实践，成本为零但可消除 JIT 优化导致的提前回收风险。
- **所有注册路径必须有对应的释放路径**：连接失败、手动断开、正常释放、重试清理——四处都要释放 GCHandle，避免句柄泄漏。
- **释放顺序**：先停止非托管回调（关传感器/断连/反初始化），再释放委托 GCHandle，最后释放宿主 GCHandle。

### 6.6 释放竞态（帧率切换后断开重连复现）

#### 问题现象

切换帧率后断开连接再重连，复现 `CallbackOnCollectedDelegate` MDA——即使已有独立 GCHandle 钉住委托，在特定时序下仍会触发。高帧率（HIGH_SPEED 120Hz）下回退中在途回调更多，更易复现。

#### 根因分析

「关传感器 → 释放委托 GCHandle」之间存在竞态窗口：

1. SDK 侧：`SetSensorEnable(false)` / `UnInitSDK()` 调用返回后，SDK 的回调线程可能还有几帧在途（已进入回调函数但尚未执行完毕）
2. 托管侧：释放 GCHandle 后，委托失去 GC 根引用，GC 可随时回收委托对象
3. 若回调线程在 GCHandle 释放后、GC 回收前还在执行委托方法中的代码：
   - 方法执行中**不会**触发 CallbackOnCollectedDelegate（委托还在栈上）
   - 但如果 GC 在方法执行期间触发并回收了委托（极端情况），或下一次回调在 GCHandle 释放后才进入托管入口，就会触发 MDA

**帧率切换后更易复现**：高帧率模式下回调频率高（120Hz），关传感器瞬间在途的回调帧数更多，竞态窗口更大。

#### 修复方案：引用计数 + 等待归零（第四层防御）

```csharp
// 字段
private int _activeCallbacks;
private const int CallbackWaitTimeoutMs = 2000;

// 回调方法：开头递增，finally 中递减
private void MillionOutlineCallback(IntPtr pOutlineData, IntPtr pUser, uint dwInstanceId)
{
    if (_disposed) return;
    System.Threading.Interlocked.Increment(ref _activeCallbacks);
    try
    {
        // ... 回调处理逻辑 ...
    }
    catch (Exception ex)
    {
        // ... 异常处理 ...
    }
    finally
    {
        System.Threading.Interlocked.Decrement(ref _activeCallbacks);
    }
    GC.KeepAlive(this);
}

// 释放前等待归零
private void WaitForCallbacksToFinish()
{
    int elapsed = 0;
    int sleepMs = 10;
    while (System.Threading.Interlocked.CompareExchange(ref _activeCallbacks, 0, 0) > 0
           && elapsed < CallbackWaitTimeoutMs)
    {
        System.Threading.Thread.Sleep(sleepMs);
        elapsed += sleepMs;
    }
    // 超时后仍有在途回调：记录警告，仍继续释放（避免死锁）
    int remaining = System.Threading.Interlocked.CompareExchange(ref _activeCallbacks, 0, 0);
    if (remaining > 0)
    {
        GlobalCommData.ShowLog(Tag,
            string.Format("WaitForCallbacksToFinish 超时，仍有 {0} 个在途回调", remaining),
            MessageLevel.Warning);
    }
}
```

**调用位置**：仅在 `ReleaseNativeResources()` 中 `UnInitSDK()` 之后、`FreeCallbackHandles()` 之前调用一次。`ShutdownPeripherals()` 中不再调用 `WaitForCallbacksToFinish()`，消除重复等待。

#### 后续优化：消除重复等待 + 缩短超时（2026-08-26）

**问题**：`ShutdownPeripherals()` 和 `ReleaseNativeResources()` 各调用一次 `WaitForCallbacksToFinish()`，合计最多 1000ms（500ms × 2）。加上 `Thread.Sleep(20)` 和 SDK 关闭调用本身的时间，英莱相机释放总时间可达 1.5s+，导致程序关闭明显卡顿。

**优化**：
1. **`ShutdownPeripherals()` 移除 `WaitForCallbacksToFinish()`**：只负责关外设，不等待回调。回调等待统一在 `ReleaseNativeResources()` 中 `UnInitSDK()` 后执行一次。
2. **`CallbackWaitTimeoutMs` 从 500 缩短到 200ms**：`UnInitSDK()` 后在途回调应快速归零，200ms 足够。
3. **移除 `Thread.Sleep(20)`**：`UnInitSDK()` 后不需要额外延迟。
4. **更新注释**：释放流程注释反映新的单次等待策略。

**效果**：英莱相机释放总等待时间从最多 1020ms（500ms × 2 + 20ms）降至最多 200ms。

#### 验证方法

1. 启用 `CallbackOnCollectedDelegate` MDA
2. 切换到 HIGH_SPEED（120Hz）模式
3. 开启传感器，等待回调稳定
4. 断开连接 → 立即重连 → 再断开 → 再重连，重复 10 次
5. 确认无 MDA 报错
6. 查看日志，确认 `WaitForCallbacksToFinish` 无超时警告（或偶尔出现但不崩溃）

#### 通则

- **关传感器 ≠ 回调立即停止**：SDK 关传感器后，回调线程可能还有若干在途帧，不能立即释放委托。
- **释放竞态窗口与帧率正相关**：帧率越高，在途回调越多，竞态窗口越大，越需要等待归零。
- **引用计数 + try/finally** 是标准的在途回调追踪方案：`Interlocked` 保证原子性，`finally` 保证异常路径也递减。
- **超时保护**：等待归零必须设超时，防止 SDK 异常导致死锁；超时后记警告日志，仍继续释放。
- **避免重复等待**：`WaitForCallbacksToFinish` 应在释放流程中仅调用一次，避免多次等待累积导致程序关闭卡顿。

---

## 相关页面

- [[modules/IntelligentLaserCam]] — 英莱相机模块文档
- [[api/IntelligentLaserCameraRun]] — 相机运行控制 API

---

## 来源

本文档由以下教训条目合并整理而成：

- `IntelligentLaser-JobParamStructs.md` — Job Parameter 结构体字段须以生成代码确认
- `IntelligentLaser-MarshalMasking.md` — SDK 命名空间遮蔽 BCL Marshal
- `IntelligentLaser-DetectConnection-ConnectOnly.md` — 启动连接只连接、不开激光相机
- `IntelligentLaser-CallbackDisplay-NotPolling.md` — 画面用回调驱动、轮询只用于查状态
- `IntelligentLaser-OneTimeCallbackOrder.md` — 一次性回调必须在连接前注册
- `IntelligentLaser-SensorCallback-LaserIndependence.md` — 传感器使能即出回调数据，激光仅控制照射
- `IntelligentLaser-ReconnectCallback.md` — 重连后无结果回调
- `IntelligentLaser-DemoCenterOriginAssumption.md` — demo 校准框角点公式隐含「原点在中心」假设
- `IntelligentLaser-FpsSwitchWhileCameraOn.md` — 相机开启时禁止切换帧率
- `IntelligentLaser-MeasuredFpsFirstFrameSkip.md` — 实测 FPS 首帧必须剔除
- `IntelligentLaser-UiNoSdkReference.md` — UI 层禁止直接引用 SDK 原生类型
- `IntelligentLaser-ConnectDetectStatus.md` — 连接后必须检测硬件实际状态

源码主要出处：`AdaWeldSystem/LineLaserCam/IntelligentLaserCam/IntelligentLaserCameraRun.cs`
