---
title: IntelligentLaser-Callback-Mechanism
date: 2026-10-30
updated: 2026-11-23
tags: [教训, 相机, 英莱, IntelligentLaser, 汇总, Job]
status: active
---


# 英莱相机教训：回调机制

> 本页为 [[lessons/IntelligentLaser-Pitfalls]] 的拆分页，仅含第 3 节。

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

> ⚠️ **2026-09-08 部分推翻（ADR-010）**：本条结论**只对「低频、同进程手动调试页面」成立**。
> 相机以 60Hz 出帧时，把每一帧都封送到 UI 线程会让消息队列被刷新请求淹没（产帧侧 20fps 节流只是把问题减半，且节流逻辑混进了采集实现层）。
> ADR-010 据此重新分工：
> - **实现层不再发显示事件**：`ContourFrameReady` / `ContourDataReady` 已删除，回调只触发 `ResultReady` + `ProfileReady` 两个中性事件。
> - **手动 UI 页（`ILCamPage`）**仍走事件：订阅 `LineLaserManager.Instance.MatUpdated`；是否生成 Mat 由 `SetDisplayOptions(enabled, fps, convert)` 开关控制，**默认关闭**——节流责任从采集侧移到业务侧。
> - **主页面（`MainPage`）轮廓改为线程轮询**：独立线程每 33ms 读 `LineLaserManager.Instance.Profile` 快照，用递增 `Version` 判断是否有新帧，无新帧直接跳过。
>   **关键差别**：轮询的是**预先填好的池化快照**（双缓冲，数组一次分配终身复用），不是「回调产数据、UI 再回头拉」，因此没有本条担心的双重浪费；且刷新节拍由 UI 自己掌握，相机帧率再高也不会压垮界面。
> - 判断准则：**事件 = 必须帧帧响应且低频；轮询 = 允许丢帧且高频。** 见 ADR-024（2026-09-17 删除，内容并入整合页；映射见 [[decisions/ADR-Index]]） D5。

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

### 4.1 校准框角点公式隐含「毫米原点居中」假设（两阶段修复）

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

**第一阶段修复（2026-08-18）—— 只解决 demo 的 `fPersent/dwOffset` 中心偏移**

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

该阶段消除了十字线不居中，**但遗留第二重假设**：`center ± |corner*rate|` 把绝对角点毫米坐标当作相对中心的偏移量展开，等价于要求「毫米原点恰在标定框中心」（`LeftTopCorner[1] = -LeftBottomCorner[1]`）。旧相机数据恰好满足，缺陷不可见。

**第二阶段修复（2026-11-23，现行终版）—— 统一仿射变换**

换用新英莱相机后，线激光调试页黄色标定框只显示一半、顶边被裁：新相机标定数据的毫米原点相对标定框偏置，`center.Y - |LeftTopCorner[1]|*rate` 越过画布上边界（数值仿真：旧实现 y 范围 [-52.3, 441.7]，新实现 [30, 524]）。

废止「绝对值展开」，改为单一仿射变换（[[decisions/ADR-113-line-laser-calib-affine-render-transform]]）：

```csharp
// 比例取四角毫米包围盒跨度；原点落点使包围盒居中
spanX = maxX - minX;  spanZ = maxZ - minZ;              // 四角毫米包围盒
rate  = min((w-2m)/spanX, (h-2m)/spanZ);
origin = (w/2 - (minX+maxX)/2*rate, h/2 + (minZ+maxZ)/2*rate);

// 唯一换算入口：角点、轮廓点、毫米刻度栅格共用
ToPixel(mm) = (origin.X + mm[0]*rate, origin.Y - mm[1]*rate);
```

要点：

1. **单一变换**：校准框、轮廓折线、刻度栅格全部经 `ToPixel()`，校准框与轮廓必然对齐。
2. **比例与原点由数据决定**：毫米原点偏置多少都完整可见，比例尺与标定数据一致。
3. **锚点用标定中心点**（`calib.Center`），越出标定区域时回退包围盒中心。
4. **形状不变**：梯形仍是梯形，只做平移与等比缩放。
5. **对称数据零回归**：标定框对中时 `origin` 恰为画布中心、四角像素与旧实现完全一致。

**关键**：demo 公式在「数据对称 + 中心对齐」时正确，跨相机不可靠；渲染层应按数据自身的包围盒定标定，而非假设毫米原点居中。

**中间弯路（must not repeat）**

1. **第一轮**：误把校准框折叠成半宽/半高对称矩形（`center±(halfW,halfH)`）——丢梯形，被拒。**居中 ≠ 可改形状**。
2. **第二轮**：用 `originX/originY` 间接映射，引入 mm 原点(0,0) 概念——负值 mm 溢出，被拒。
3. **第三轮**：用 `halfExtent` + `(corner-Center)` 相对偏移——自创公式偏离 demo 正确逻辑，被拒。
4. **终版**：**demo 原版公式 `center ± |corner*rate|` + `trans = center + mm*rate`，仅改 `center = (w/2, h/2)`**。**不要自创公式——demo 本身是对的，只是 center 没对齐图像中心**。

**通则**

1. **移植厂商 demo 几何公式时，先核实其坐标系假设**（如「原点=画面中心」）。demo 数据对称时公式看似正确，换真机数据即失效。
2. **"居中显示" ≠ "校正形状"**：默认只平移/缩放、保持被观察对象真实拓扑。
3. **以标定中心点（而非 mm 原点）为视图基准**：`calib.Center` 是唯一有意义的锚点，所有屏幕坐标应相对它计算。
4. **同一物理坐标系内的多个图元必须共用一套变换**：校准框、轮廓点、刻度栅格若各用各的换算，误差会以「框线错位」而非「框线缺失」暴露，排查成本更高。
5. **换相机后渲染异常先查渲染端坐标系假设，再查设备状态**：新相机数据一旦不满足旧公式的前提，先验假设（而非设备状态）才是首要怀疑对象。

---

## 相关页面

- [[lessons/IntelligentLaser-Sdk-Interop]] —— 同源拆分页
- [[lessons/IntelligentLaser-Ui-State]] —— 同源拆分页
- [[lessons/IntelligentLaser-Delegate-Gc]] —— 同源拆分页
- [[lessons/IntelligentLaser-Job-System]] —— 同源拆分页
- [[lessons/IntelligentLaser-Pitfalls]] —— 源页（拆分前全量）
