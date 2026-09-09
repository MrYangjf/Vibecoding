# 算法程序改造指导（抽象层 / 实现层 / Manager 业务层）v2.0

> 版本：v2.0（算法内容更新：输入源收敛为监控相机，领域算法收敛为送丝距离检测 + 焊接质量检测；线激光点云链路删除）
> 适用：AdaWeldSystem.EmguALG 算法程序改造，对齐台达运控、线激光、监控相机模块架构
> 配套文档：《监控相机开发指导_MecaVision版》《运动控制模块开发文档_台达版》
> 改造原则：**不推翻现有良好基础，只做职责重排与边界补齐**——算子库保留、强类型配置保留；拆掉 PipelineManager 过载职责，补齐抽象接口、结果缓存、统一调度与依赖注入。

---

## 1. 模块定位（v2.0 更新）

### 1.1 职责边界

| 项 | 内容 |
|----|------|
| 输入源 | **仅监控相机图像（Mat）**——MecaVision 相机出图，无分析算法 |
| 检测任务 1 | **送丝距离检测**：监控相机图像中检测焊丝位置/尖端，计算送丝距离（伸出长度），输出偏差与判定 |
| 检测任务 2 | **焊接质量检测**：焊道成形质量（宽度/气孔/咬边/飞溅），输出质量分与 Pass/Warn/Fail |
| 不做 | ❌ 线激光点云识别（SeamRecognition 链路删除）、❌ 机器人坐标对齐（无点云输入） |

### 1.2 数据流（v2.0）

```
监控相机（MecaVision）── 帧回调 ──> 相机 Manager（MonitorCameraManager）
                                        │  帧（Mat，池化快照+版本号）
                                        ▼
                          算法 Manager（AlgorithmManager）
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
          送丝距离检测（WireFeedDistance）        焊接质量检测（WeldQuality）
                    │                                       │
                    └───────────┬───────────────────────────┘
                                ▼
                    结果分发：业务事件 + UI 轮询缓存
```

### 1.3 与线激光的关系（v2.0 明确）

- 线激光（英莱）**不再调用本算法模块**——线激光结果直接驱动 Y 轴 PVT（见《台达EtherCAT_PVT与电子凸轮运动开发指南》）
- 本算法模块的输入**只来自监控相机**（焊前/焊中实时画面）
- 线激光 Manager、相机 Manager、算法 Manager 三者平级，依赖单向（相机 → 算法；算法不反向依赖相机）

---

## 2. 现状诊断

### 2.1 现有文件与职责盘点（v2.0 处置更新）

| 文件 | 行数 | 当前职责 | v2.0 处置 |
|------|------|----------|-----------|
| Core/AlgorithmBase.cs | 154 | 抽象算法基类（模板方法 Execute/ExecuteCore、预处理编排、INI 契约） | ✅ 保留 |
| Core/AlgorithmResult.cs | 31 | 结果基类 | ✅ 保留 |
| Core/ProfileTransform.cs | 70 | mm↔px 变换（点云用） | ⚠️ **删除**（无点云输入） |
| Core/PreprocessConfig.cs | 231 | 预处理强类型配置（滤波/形态学/边缘） | ✅ 保留（供质量检测预处理） |
| ImageAlgorithm.cs | 937 | 静态算子库（含 DetectPreWeldAlignment / DetectWeldQuality / 预处理算子） | ✅ 保留（**迁移核心依据**） |
| EmguConfiger/AlgorithmManager.cs | 607 | PipelineManager 单例：配置+阶段编排+焊缝特征+事件 | ⚠️ 拆分（同 v1） |
| EmguConfiger/JobManager.cs | 280 | Job 配置管理 | ✅ 保留（若两检测需 Job） |
| EmguConfiger/AlgorithmJob.cs | 46 | Job 数据类 | ⚠️ Config 类型改为 WireFeedConfig/WeldQualityConfig |
| RealtimeMonitor/RealtimeMonitorAlgorithm.cs | 418 | CheckCentering（光斑+焊丝）+ CheckQuality（成形质量） | ✅ **迁移核心**：拆为两个领域算法 |
| SeamRecognition/SeamRecognitionAlgorithm.cs | 290 | 焊缝识别（点云输入） | ⚠️ **删除**（线激光不依赖） |
| SeamRecognition/SeamModel.cs | 160 | 焊缝模型（mm 语义） | ⚠️ **删除**（无点云） |
| Stages.cs | 410 | 旧参数网格（INotifyPropertyChanged） | ⚠️ 降级（保留给预处理 UI 或废弃） |
| ImageRoiTools.cs | 349 | ROI 工具 | ✅ 保留（UI 辅助） |

### 2.2 核心问题（不变，仍成立）

| # | 问题 | 后果 |
|---|------|------|
| P1 | PipelineManager 职责过载 | 无法替换、无法测试 |
| P2 | 类级 `_completedArgs` 复用，线程不安全 | 相机帧并发执行串结果 |
| P3 | 无抽象接口，单例直取 | 强耦合、无法 mock |
| P4 | 无结果缓存 | UI 无法轮询最新结果 |
| P5 | 两套配置并存（PipelineConfig vs 强类型） | Job 切换无法驱动强类型配置 |
| P6 | 无统一调度入口 | 消费关系混乱 |

---

## 3. 目标架构（v2.0 算法内容）

```
AlgorithmModule/
├── Abstractions/                     # 抽象层（接口）
│   ├── IAlgorithm.cs                     # IAlgorithm<Mat, TResult>（输入只有图像）
│   ├── IConfigurableAlgorithm.cs         # 配置切换（Job 驱动）
│   └── IResultStore.cs                   # 结果缓存接口
├── Native/                            # 算子层
│   └── ImageAlgorithm.cs                 # ✅ 保留原样（纯算子，无业务）
├── Core/                              # 核心基础设施
│   ├── AlgorithmBase.cs                  # ✅ 保留
│   ├── AlgorithmResult.cs                # ✅ 保留
│   └── PreprocessConfig.cs               # ✅ 保留（质量检测预处理用）
├── Implementations/                   # ★ 实现层（两个领域算法）
│   ├── WireFeedDistance/
│   │   ├── WireFeedDistanceAlgorithm.cs  # ★ 送丝距离检测（迁移 CheckCentering/DetectPreWeldAlignment）
│   │   ├── WireFeedConfig.cs             # ★ 送丝距离配置（强类型）
│   │   └── WireFeedResult.cs             # ★ 检测结果（距离 mm/判定/可视化）
│   └── WeldQuality/
│       ├── WeldQualityAlgorithm.cs       # ★ 焊接质量检测（迁移 CheckQuality/DetectWeldQuality）
│       ├── WeldQualityConfig.cs          # ★ 质量阈值配置
│       └── WeldQualityResult.cs          # ★ 质量结果（分/Pass/Warn/Fail/缺陷）
├── Manager/                          # Manager 业务层
│   ├── AlgorithmManager.cs               # 统一调度：DetectWireFeed / DetectQuality
│   ├── JobManager.cs                     # ✅ 保留（两检测的 Job 切换）
│   ├── AlgorithmResultStore.cs           # 最新结果缓存（池化快照+版本号）
│   └── AlgorithmWorkflow.cs              # 工作流线程（可选：拍照→检测→判定）
└── UI/（UIControl/AlgoControls/）
    ├── WireFeedResultPanel.cs            # 送丝距离显示（轮询）
    ├── WeldQualityResultPanel.cs         # 质量结果显示（轮询）
    └── ...（ROI 控件保留）
```

**依赖方向（单向，与相机模块一致）**：

```
UI ──注入──> AlgorithmManager ──> IAlgorithm<Mat, TResult>（两个检测实现）
                 │                          │
                 ├─> IResultStore ──────> (池化快照+版本号)
                 └─> JobManager ──────> WireFeedConfig / WeldQualityConfig
                                              │
                                              ▼
                    ImageAlgorithm（算子）──> Emgu.CV

监控相机 Manager ──帧(Mat)──> AlgorithmManager（依赖单向，不反向）
```

---

## 4. 领域算法设计（v2.0 核心）

### 4.1 送丝距离检测 `WireFeedDistanceAlgorithm`

**语义**：监控相机画面中检测焊丝尖端与参考点（激光光斑/工件表面）的位置，计算送丝距离（偏差 mm）。

**迁移来源**（现有代码可直接复用）：
- `RealtimeMonitorAlgorithm.CheckCentering`：光斑检测（`DetectCentroid`）+ 焊丝尖端检测（`DetectWireTip`）→ 像素偏差 × `PixelMmScale` → mm
- `ImageAlgorithm.DetectPreWeldAlignment`：光斑（阈值>240）+ 焊丝（150~245 排除光斑）→ OffsetX/OffsetY/Angle

**结果输出**（对齐现有 CenteringCheckResult 演进）：

```csharp
// Implementations/WireFeedDistance/WireFeedResult.cs
public class WireFeedResult : AlgorithmResult
{
    public double DistanceMM;        // 送丝距离（焊丝尖端到参考点，mm）
    public double DevXMM, DevZMM;    // 水平/垂直偏差（mm）
    public string Direction;         // "左/右/上/下/居中"
    public CheckGrade Grade;         // Pass / Warn / Fail（复用现有枚举）
    public PointF WireTipPx;         // 焊丝尖端（px，可视化用）
    public Mat OverlayMat;           // 叠加检测结果的图（UI 显示）
}
```

**配置**（强类型，迁移 MonitorConfig 中对中部分）：

```csharp
// Implementations/WireFeedDistance/WireFeedConfig.cs
public class WireFeedConfig
{
    [Category("焊丝检测")] public int WireMinGray { get; set; }   // 焊丝灰度下限（默认 150）
    [Category("焊丝检测")] public int WireMaxGray { get; set; }   // 焊丝灰度上限（默认 245，排除光斑）
    [Category("光斑检测")] public int SpotThreshold { get; set; } // 光斑亮度阈值（默认 240）

    [Category("容差(mm)"), Unit("mm")] public double WarnMM { get; set; }   // 预警（默认 0.3）
    [Category("容差(mm)"), Unit("mm")] public double FailMM { get; set; }   // 不合格（默认 0.8）
    [Category("标定")] public double PixelMmScale { get; set; }             // px→mm 系数（默认 0.05）

    // Clone / SaveToIni / LoadFromIni（同现有 MonitorConfig 模式）
}
```

**算法类**：

```csharp
public sealed class WireFeedDistanceAlgorithm :
    AlgorithmBase,
    IAlgorithm<Mat, WireFeedResult>,
    IConfigurableAlgorithm<WireFeedConfig>
{
    private WireFeedConfig _config;
    public WireFeedDistanceAlgorithm() { _config = new WireFeedConfig(); }

    public override string AlgorithmName => "WireFeedDistance";
    public WireFeedConfig Config => _config;
    public void SetConfig(WireFeedConfig cfg) { _config = cfg ?? new WireFeedConfig(); }

    // IAlgorithm<Mat, WireFeedResult> 入口（同步执行）
    public WireFeedResult Execute(Mat input)
    {
        // ===== 迁移 CheckCentering 主体 =====
        // 1. 灰度化（PrepareGray）
        // 2. 焊丝尖端：阈值 [WireMinGray, WireMaxGray] 取最大轮廓 → DetectWireTip
        // 3. 光斑：阈值 SpotThreshold → DetectCentroid
        // 4. 偏差 = (焊丝尖端 - 光斑中心) × PixelMmScale → DevXMM/DevZMM
        // 5. 距离 = sqrt(DevX² + DevZ²)，方向判定（ComputeDirection）
        // 6. Grade = GradeFromDeviation(距离, WarnMM, FailMM)
        // 7. 绘制 OverlayMat（焊丝/光斑圆圈 + 连线 + 文字）
        // 8. 填 WireFeedResult 返回
    }
}
```

### 4.2 焊接质量检测 `WeldQualityAlgorithm`

**语义**：焊道成形质量——焊道宽度/气孔/咬边/飞溅 → 扣分制 → Pass/Warn/Fail。

**迁移来源**（现有代码可直接复用）：
- `RealtimeMonitorAlgorithm.CheckQuality`：焊道宽度（矩 M00）+ 气孔计数（`CountDarkBlobs`）+ 咬边/飞溅占位 + 扣分制（100 起步，-40 宽度/-30 气孔/-15 咬边/-15 飞溅，≥80 Pass / ≥50 Warn / <50 Fail）
- `ImageAlgorithm.DetectWeldQuality`：焊道识别 + 缺陷列表 + QualityScore

**结果输出**：

```csharp
// Implementations/WeldQuality/WeldQualityResult.cs
public class WeldQualityResult : AlgorithmResult
{
    public int Score;                // 0~100
    public CheckGrade Grade;         // Pass / Warn / Fail（复用现有枚举）
    public List<string> Defects;     // 缺陷描述（"焊道宽度超差"等）
    public double BeadWidthMM;       // 焊道宽度（mm）
    public int PorosityCount;        // 气孔数
    public double UndercutMM;        // 咬边（mm）
    public double SpatterArea;       // 飞溅面积
    public Mat OverlayMat;           // 标注图（UI 显示）
}
```

**配置**（迁移 MonitorConfig 成形质量部分 + 现有 WeldQualityConfig）：

```csharp
// Implementations/WeldQuality/WeldQualityConfig.cs
public class WeldQualityConfig
{
    [Category("成形质量(mm)"), Unit("mm")] public double BeadWidthMinMM { get; set; }  // 默认 3.0
    [Category("成形质量(mm)"), Unit("mm")] public double BeadWidthMaxMM { get; set; }  // 默认 6.0
    [Category("成形质量")] public int PorosityMaxCount { get; set; }                   // 默认 3
    [Category("成形质量(mm)"), Unit("mm")] public double UndercutMaxMM { get; set; }   // 默认 0.2
    [Category("成形质量")] public double SpatterMaxArea { get; set; }                  // 默认 500
    [Category("分级")] public int PassScore { get; set; }                              // 默认 80
    [Category("分级")] public int WarnScore { get; set; }                              // 默认 50
    [Category("标定")] public double PixelMmScale { get; set; }                        // px→mm

    // Clone / SaveToIni / LoadFromIni
}
```

**算法类**：

```csharp
public sealed class WeldQualityAlgorithm :
    AlgorithmBase,
    IAlgorithm<Mat, WeldQualityResult>,
    IConfigurableAlgorithm<WeldQualityConfig>
{
    private WeldQualityConfig _config;
    public override string AlgorithmName => "WeldQuality";

    public WeldQualityResult Execute(Mat input)
    {
        // ===== 迁移 CheckQuality 主体 =====
        // 1. 灰度化
        // 2. 焊道掩膜（阈值）→ 矩 M00 → BeadWidthMM
        // 3. 气孔计数（CountDarkBlobs）
        // 4. 咬边/飞溅（现有占位，后续可接截面拟合）
        // 5. 扣分制 → Score → Grade（≥PassScore Pass / ≥WarnScore Warn / Fail）
        // 6. Defects 列表（BuildDefects）
        // 7. 填 WeldQualityResult + OverlayMat
    }
}
```

---

## 5. 抽象层接口（v2.0 简化）

```csharp
// Abstractions/IAlgorithm.cs —— 输入统一为 Mat（监控相机图像）
public interface IAlgorithm<TResult> where TResult : AlgorithmResult
{
    string AlgorithmName { get; }
    TResult Execute(Mat input);          // 同步执行
    bool IsBusy { get; }                 // 防重入
}

public interface IConfigurableAlgorithm<TConfig>
{
    TConfig Config { get; }
    void SetConfig(TConfig config);
}

// Abstractions/IResultStore.cs —— 结果缓存（池化快照 + 版本号，与相机帧缓存同构）
public interface IResultStore<TResult> where TResult : AlgorithmResult
{
    TResult GetLatest(out int version);
    int Version { get; }
}
```

---

## 6. Manager 层（v2.0）

### 6.1 AlgorithmManager（统一调度）

```csharp
// Manager/AlgorithmManager.cs
public sealed class AlgorithmManager
{
    private readonly IAlgorithm<WireFeedResult> _wireFeed;      // 送丝距离检测
    private readonly IAlgorithm<WeldQualityResult> _weldQuality; // 焊接质量检测
    private readonly IResultStore<AlgorithmResult> _resultStore;
    private readonly JobManager _jobManager;

    /// <summary>检测完成事件（低频率：状态灯/日志；高频结果走 ResultStore 轮询）</summary>
    public event EventHandler<AlgorithmCompletedEventArgs> AlgorithmCompleted;

    public AlgorithmManager(
        IAlgorithm<WireFeedResult> wireFeed,
        IAlgorithm<WeldQualityResult> weldQuality,
        IResultStore<AlgorithmResult> resultStore,
        JobManager jobManager)
    {
        _wireFeed = wireFeed;
        _weldQuality = weldQuality;
        _resultStore = resultStore;
        _jobManager = jobManager;
    }

    // ===== 统一入口（相机 Manager / 工作流调用）=====

    /// <summary>送丝距离检测（相机图像）</summary>
    public WireFeedResult DetectWireFeed(Mat image)
    {
        var r = _wireFeed.Execute(image);
        Publish(r);
        return r;
    }

    /// <summary>焊接质量检测（相机图像）</summary>
    public WeldQualityResult DetectWeldQuality(Mat image)
    {
        var r = _weldQuality.Execute(image);
        Publish(r);
        return r;
    }

    /// <summary>Job 切换 → 驱动两个检测算法 SetConfig</summary>
    public void SwitchJob(int jobId) => _jobManager.SwitchJob(jobId);

    private void Publish(AlgorithmResult r)
    {
        AlgorithmCompleted?.Invoke(this, new AlgorithmCompletedEventArgs
        {
            Success = r.Success,
            ElapsedMilliseconds = r.ElapsedMs,
            ErrorMessage = r.ErrorMessage
        });
        _resultStore.Publish(r);   // 出口2：UI 轮询缓存
    }
}
```

### 6.2 AlgorithmResultStore

与 v1 相同（池化快照 + 版本号，完全同构于相机帧缓存/线激光轮廓缓存），此处不再重复。

### 6.3 Job 配置（v2.0）

```csharp
// EmguConfiger/AlgorithmJob.cs（v2.0）
public class AlgorithmJob
{
    public int JobId { get; set; }
    public string JobName { get; set; }
    public WireFeedConfig WireFeedConfig { get; set; }   // 送丝距离参数
    public WeldQualityConfig WeldQualityConfig { get; set; } // 质量参数
    // 旧 PipelineConfig 由 GenericPipelineAlgorithm 承载（如需保留旧流水线），否则移除
}
```

`JobManager.ApplyCurrentJob` 切换时：遍历已注入的 `IConfigurableAlgorithm`，按类型分发 `SetConfig`（`WireFeedConfig` → 送丝算法，`WeldQualityConfig` → 质量算法）。

### 6.4 组合根

```csharp
// Composition Root（唯一 new 具体实现处）
var wireFeed = new WireFeedDistanceAlgorithm();
var weldQuality = new WeldQualityAlgorithm();
var store = new AlgorithmResultStore(4);
var jobMgr = JobManager.Instance;

var algoMgr = new AlgorithmManager(wireFeed, weldQuality, store, jobMgr);

// 相机 Manager 帧回调 → 算法（业务层组合，非算法内部依赖相机）
cameraMgr.FrameReceived += (s, f) => algoMgr.DetectWireFeed(ToMat(f));
```

---

## 7. 依赖关系与消费关系（v2.0）

```
┌──────────────────────────────────────────────────────────────┐
│ 监控相机 Manager（MonitorCameraManager）                        │
│   帧回调(Mat) ──> AlgorithmManager.DetectWireFeed(img)         │
│                ──> AlgorithmManager.DetectWeldQuality(img)    │
└───────────────────────────┬──────────────────────────────────┘
                            ▼
                   AlgorithmManager
                 │                │
                 ▼                ▼
        WireFeedDistance    WeldQuality
        (ImageAlgorithm)    (ImageAlgorithm)
                 │                │
                 └───────┬────────┘
                         ▼
              IResultStore（池化快照+版本号）
                         │
                         ▼
              UI Timer(33ms) 轮询 → 结果面板
```

**消费关系表**：

| 消费者 | 消费什么 | 通过什么 | 频率 |
|--------|----------|----------|------|
| 相机 Manager | 帧 → 触发检测 | AlgorithmManager（注入，业务层组装） | 相机帧率 |
| 业务层（焊接工艺） | 送丝距离/质量判定 | DetectWireFeed / DetectWeldQuality 返回值 | 帧率 |
| UI 结果面板 | 最新检测结果 | IResultStore.GetLatest（Timer 轮询） | 30Hz |
| UI 状态灯/日志 | 成功/失败/耗时 | AlgorithmCompleted 事件 | 低频率 |
| UI Job 下拉 | Job 切换 | JobManager | 手动 |

---

## 8. 删除清单（v2.0 新增）

| 删除项 | 原因 |
|--------|------|
| SeamRecognition/ 目录（SeamRecognitionAlgorithm.cs、SeamModel.cs） | 线激光不再依赖，无点云输入 |
| Core/ProfileTransform.cs | mm↔px 变换仅点云栅格化用，删除后 ImageAlgorithm.ConvertContourToMat(PointCloudData) 重载一并清理 |
| AlgorithmManager.Recognize(PointCloudData, robotX) | 无点云识别链路 |
| IAlgorithm<PointCloudData, TResult> 泛型 | 输入统一为 Mat |
| 相机/算法对 RobotX 的依赖 | 机器人 X 对齐只在线激光链路（台达文档），算法模块不涉及 |
| MonitorConfig 中"成形质量"部分 | 迁移进 WeldQualityConfig（MonitorConfig 本身并入两个新配置后删除） |

**保留迁移源**（代码直接搬）：`CheckCentering` → WireFeedDistanceAlgorithm.Execute；`CheckQuality` → WeldQualityAlgorithm.Execute；`DetectCentroid/DetectWireTip/CountDarkBlobs/ComputeDirection/GradeFromDeviation/BuildDefects` → 两个算法的私有方法。

---

## 9. 迁移顺序与验收清单（v2.0）

### 9.1 迁移顺序

```
第1步：新建 Abstractions/（IAlgorithm/IResultStore/IConfigurableAlgorithm）——纯新增
第2步：从 RealtimeMonitorAlgorithm 拆出两个领域算法
       （WireFeedDistanceAlgorithm ← CheckCentering；WeldQualityAlgorithm ← CheckQuality）
       + 各自强类型配置 WireFeedConfig/WeldQualityConfig
第3步：删除 SeamRecognition 链路、ProfileTransform、PointCloudData 输入
第4步：拆 PipelineManager（删配置/删阶段/删焊缝特征/删 ReportExternalResult 点云版）→ 组装 AlgorithmManager
第5步：新增 AlgorithmResultStore + UI 轮询改造（两个结果面板）
第6步：Job 强类型化（WireFeedConfig/WeldQualityConfig，兼容旧 INI 过渡）
第7步：组合根收口，UI/业务全部改走注入；相机 Manager 帧接入
```

### 9.2 验收清单

| # | 验收项 | 验证方式 |
|---|--------|----------|
| 1 | SeamRecognition/ 目录与 ProfileTransform 已删除，无残留引用 | Grep `SeamRecognition\|ProfileTransform\|PointCloudData` |
| 2 | 算法输入统一为 Mat，无点云输入 | IAlgorithm 定义检查 |
| 3 | 送丝距离检测输出距离 mm + Grade 判定 | 用监控相机实图验证 |
| 4 | 焊接质量检测输出 Score + Pass/Warn/Fail + 缺陷列表 | 用焊接画面验证 |
| 5 | PipelineManager 已拆分，无业务字段残留 | 删除清单核对 |
| 6 | UI/业务无 `XxxAlgorithm.Instance` 直取 | Grep `\.Instance` |
| 7 | 结果走 ResultStore 轮询，无高频事件风暴 | UI 无事件订阅高频结果 |
| 8 | Job 切换驱动两个强类型配置 | 切换 Job → 两算法 Config 变化 |
| 9 | 相机帧并发执行不串结果 | 多线程压测 |
| 10 | 换算法后端只改实现层，UI/Manager 不动 | 新增第三方实现类验证 |

### 9.3 风险与对策

| 风险 | 对策 |
|------|------|
| 删除 SeamRecognition 影响现有 UI（EmguAlgoPage 依赖） | 先确认无引用再删；有引用先留空壳过渡 |
| 送丝距离的 mm 标定（PixelMmScale）精度不足 | 保留现有 px→mm 系数，实际用标定板/相机内参校准 |
| 咬边/飞溅检测为占位逻辑 | 文档标注占位，后续接截面拟合/掩膜统计 |
| Job 旧 INI 兼容 | 双配置并行期过渡后清理 |
