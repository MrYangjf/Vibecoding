---
title: IntelligentLaser-Delegate-Gc
date: 2026-10-30
updated: 2026-10-30
tags: [教训, 相机, 英莱, IntelligentLaser, 汇总, Job]
status: active
---


# 英莱相机教训：委托 GC 保护与 CallbackOnCollectedDelegate

> 本页为 [[lessons/IntelligentLaser-Pitfalls]] 的拆分页，仅含第 6 节。

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

### 5.17 传感器状态真相源本地化 + 激光/传感器按钮 UI 单一刷新入口（2026-09-17 并入自 IntelligentLaserSensorControl 页）

- **状态真相源在设备层、且本地化**：`IsCameraOn()`/`IsLaserOn()` 读设备层本地状态（`_isCameraOn`/`_isLaserOn`，连接成功时 `SyncHardwareStatus()` 从硬件同步一次、`SetSensor`/`SetLaser` 成功后本地更新），UI 点击立即生效、无硬件查询延迟；**UI 层禁止维护「是否已开传感器」的本地 bool 副本**（与设备层脱节，违反 UiStateSimplification 原则①）。
- **按钮 text 与 `ExtraMouseDown` 收敛单一函数 `UpdateLaserSensorUi()`**：`btnLaser_Click` / `btnCaptureCamera_Click` / `SyncFromHardwareCore` / `UpdateConnectionUiCore` 四处全部汇聚到它，基于 `IsLaserOn()`/`IsCameraOn()` 统一设置两个按钮的 text 与 `ExtraMouseDown`；按钮点击后、硬件同步后、连接态刷新后都调它。
- 传感器启停语义（用 `SetSensor` 弃 `SetCaptureCamera`）见 §3.5，互为表里。

## 相关页面

- [[lessons/IntelligentLaser-Sdk-Interop]] —— 同源拆分页
- [[lessons/IntelligentLaser-Callback-Mechanism]] —— 同源拆分页
- [[lessons/IntelligentLaser-Ui-State]] —— 同源拆分页
- [[lessons/IntelligentLaser-Job-System]] —— 同源拆分页
- [[lessons/IntelligentLaser-Pitfalls]] —— 源页（拆分前全量）
