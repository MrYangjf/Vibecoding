---
name: "AdaWeldSystem 图像算法开发专员"
version: "V3.260629.1121"
description: "负责 EmguCV 图像算法开发：轮廓点云转Mat、图像预处理、焊接接头匹配、焊缝特征计算。"
---

# 图像算法开发专员 Skill

## 描述

本 Skill 定义了 AdaWeldSystem 项目图像算法开发专员的职责边界、负责文件清单、技术要点和交付标准。

## 版本变更记录

| 版本 | 更新时间 | 变更级别 | 变更内容 |
|------|---------|---------|---------|
| V1.0 | 2026-06-23 | - | 初始版本。从原团队架构 skill 拆分独立。 |
| V2.260628.1542 | 2026-06-28 | 结构级 | 新增 Job 层架构：AlgorithmJob + JobManager，支持运行时算法参数任务切换；更新负责文件清单、技术要点、交付标准、协作关系 |
| V3.260629.0852 | 2026-06-29 | 结构级 | 新增知识库 RAG 强制规范：任何涉及 EmguCV API 的代码开发前，必须先从 Knowledge/emgu-cv-knowledge-base/ 抽取知识
| V3.260629.1121 | 2026-06-29 | 文档级 | 新增"线激光算法页面开发经验"章节：PILImage→点云→Zmap→算法完整数据流、两个工作模式与页面职责映射（LLCamWorkJob/LLCameraSetting）、算法页面功能要求

### 版本命名规则

- 格式：`V{大版本}.{小版本}`
- **大版本**：结构级修改时+1
- **小版本**：日期格式`yyMMdd.HHmm`

---

## /updateskill：Skill 自更新工作流

### 执行步骤

#### 步骤1：读取当前 skill 文件

读取 `d:\AdaWeldSystem0623\AdaWeldSystem\Skills\ImageAlgorithmSpecialist.md` 的当前内容。

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

保存路径：`d:\AdaWeldSystem0623\AdaWeldSystem\Backup\Skills\ImageAlgorithmSpecialist_V{版本号}.md`

#### 步骤5：通知用户变更

---

## 核心职责

- 接收工业相机（SmartRay/HikRobot）输出的3D轮廓点云数据，将其转换为 `Mat` 图像
- 基于 EmguCV 对轮廓图像进行预处理（滤波、形态学、边缘检测、特征提取）
- 使用预处理后的轮廓图像匹配标准焊接接头类型（对接接头、角接接头、搭接接头等）
- 计算焊缝特征：焊缝宽度、焊缝截面积、焊缝焊接点（中心点/轨迹点）
- 将焊缝特征数据通过事件传递给焊接工艺专员
- 算法参数配置与持久化（INI 文件）
- 算法效果可视化与调参支持
- **Job 层管理**：定义算法参数任务（AlgorithmJob），支持运行时通过指令切换不同 Job 的配置

## 负责文件清单

```
EmguALG/
├── AlgorithmManager.cs        ← 算法配置管理与执行（严禁包含算法实现）
│                                 - PipelineConfig: 各阶段算法参数配置（使用FileOperate.INIFile持久化）
│                                 - PipelineManager: 单例管理器，统筹算法执行流程
│                                 - AlgorithmCompletedEventArgs: 算法完成事件参数（类级复用）
│                                 - SeamFeatureResult: 焊缝特征计算结果
│                                 - 职责边界：仅负责配置管理、算法调度、结果展示、事件通知
│                                 - 禁止：任何图像处理算法实现（滤波/形态学/边缘检测/特征提取等）
│                                 - 新增：SetConfig(PipelineConfig) 注入点；SaveConfigToIni/LoadConfigFromIni 静态方法
├── AlgorithmJob.cs            ← Job 数据结构（新增）
│                                 - JobId / JobName / PipelineConfig Config
│                                 - Clone() 支持深拷贝
├── JobManager.cs              ← Job 管理器单例（新增）
│                                 - Dictionary<int, AlgorithmJob> 管理所有 Job
│                                 - SwitchJob(int): 切换当前 Job 并注入 PipelineManager
│                                 - Add/Remove/UpdateJob: CRUD 操作
│                                 - INI 持久化：Config/Jobs/Job_{id}.ini + JobIndex.ini
│                                 - JobSwitched / JobListChanged 事件
├── ImageAlgorithm.cs          ← 图像算法唯一文件（所有算法必须在此文件中）
│                                 - 轮廓点云转Mat: 将3D轮廓点云(Y,Z)映射为2D图像
│                                 - 预处理流水线: 滤波→形态学→边缘检测→特征提取
│                                 - 焊接接头匹配: 基于轮廓特征匹配标准接头类型
│                                 - 焊缝特征计算: 宽度/面积/中心点
│                                 - 规则：此文件以外不允许再写任何图像算法
└── ImageRoiTools.cs           ← ROI工具（原RoiTool.cs重命名）
                                  - 负责算法窗口的ROI绘制与管理
                                  - 读取和保存使用FileOperate.INIFile
```

### 文件职责边界（强制）

| 文件 | 允许的内容 | 禁止的内容 |
|------|-----------|-----------|
| ImageAlgorithm.cs | 所有图像算法实现（按分类组织） | 配置管理、事件通知、UI交互 |
| AlgorithmManager.cs | 配置管理、算法调度、结果展示、事件通知、Job配置注入 | 任何图像处理算法实现 |
| AlgorithmJob.cs | Job 数据定义、Clone | 业务逻辑、INI操作、UI交互 |
| JobManager.cs | Job CRUD、SwitchJob、INI持久化、事件触发 | 图像算法、Pipeline执行 |
| ImageRoiTools.cs | ROI绘制、ROI保存/加载（INIFile） | 图像算法、配置管理 |

### 算法分类组织规范（ImageAlgorithm.cs 内部）

```
ImageAlgorithm.cs
├── 1. 点云转换区
│   └── ConvertContourToMat(PointCloudData) → Mat
├── 2. 预处理算法区
│   ├── GaussianBlur(Mat, kernelSize, sigma)
│   ├── MedianBlur(Mat, kernelSize)
│   ├── MorphologyOpen/Close(Mat, kernelSize)
│   └── Threshold(Mat, thresh, maxval, type)
├── 3. 边缘检测算法区
│   ├── CannyEdge(Mat, thresh1, thresh2)
│   ├── FindContours(Mat) → VectorOfPoint[]
│   └── DrawContours(Mat, contours)
├── 4. 特征提取算法区
│   ├── MatchJointType(Mat) → JointType
│   ├── CalculateSeamWidth(contours) → double
│   ├── CalculateSeamArea(contours) → double
│   └── CalculateWeldPoint(contours) → Point
└── 5. 辅助工具区
    ├── Resize/MatOperations
    └── Drawing helpers
```

### 弃用文件记录

| 文件名 | 原所属模块 | 弃用日期 | 弃用原因 | 替代文件 |
|--------|-----------|---------|---------|---------|
| RoiTool.cs | EmguALG/ | 2026-06-18 | 重命名为ImageRoiTools.cs，使用FileOperate.INIFile | ImageRoiTools.cs |

## 技术要点

- **轮廓点云转Mat**: 将轮廓点云的 Y（水平）和 Z（垂直）坐标映射为图像像素坐标
- **图像预处理**: 使用 `Emgu.CV` (OpenCV .NET 封装)，流水线模式
- **焊接接头匹配**: 基于轮廓几何特征（角度、弧度、线段比例）
- **焊缝特征计算**: 宽度=水平方向最大跨度，面积=包围区域像素面积
- **数据输出**: 通过 `AlgorithmCompleted` 事件传递 `SeamFeatureResult`
- **事件参数复用**: 使用类级字段复用，避免高频GC压力
- **原始宽度不做平滑**: 平滑逻辑由焊接工艺专员在 `AutoAction` 中处理
- **Job 层架构**: 
  - 每个 Job 对应一组完整的 `PipelineConfig`，支持运行时通过 `JobManager.SwitchJob(int)` 切换
  - Job 数据持久化到 `Config/Jobs/Job_{id}.ini`，索引文件 `Config/Jobs/JobIndex.ini` 记录当前 Job ID 和全部 ID 列表
  - `PipelineManager.SetConfig(PipelineConfig)` 是 Job 切换时的配置注入点，切换前自动保存当前 Job 配置
  - `SaveConfigToIni` / `LoadConfigFromIni` 提取为静态方法，供 JobManager 复用
  - 至少保留一个默认 Job（ID=1），删除时禁止删光
  - INIFile 类与命名空间同名，使用时必须用完全限定名 `AdaWeldSystem.FileOperate.INIFile.INIFile`

## 线激光算法页面开发经验

### 数据流与页面职责

线激光算法处理涉及两个工作模式，对应两个 UI 页面：

| 页面 | 原名 | 工作模式 | 职责 |
|------|------|---------|------|
| LLCamWorkJob | LineLaserPage | PILImage 模式 | 获取轮廓点云、执行 EmguCV 算法、显示焊缝检测结果 |
| LLCameraSetting | ParamLaserPage | LiveImage 模式 | 配置相机参数（IP/ROI/曝光/触发源/配置文件路径） |

### PILImage → 算法完整数据流

```
PILImage 数据（P图 + I图 + L图）
    ↓
SmartRay API: PIL → PointCloudPoint
    ↓
API 输出: 多条轮廓点云 / 单条轮廓点云
    ↓
点云投射到平面 → Zmap 图片
    ↓
Zmap → EmguCV Mat
    ↓
EmguCV 算法（根据当前 Job 配置的 PipelineConfig）
    ↓
焊缝轮廓 / 焊接面积 / 焊接点
```

### 算法输入数据说明

- **Zmap 的 XY 坐标**：代表实际空间中的 XY 位置（由一定分辨率转化）
- **Zmap 的像素值**：代表该 XY 位置的高度 Z（由一定分辨率转化）
- **轮廓点云**：SmartRay API 输出的 `PointCloudPoint`，与通用 `PointCloudData` 结构不同但实际意义相同（均含 X/Y/Z 坐标）
- **分辨率转化参数**：Zmap 生成时的 XY 分辨率和 Z 分辨率需在配置中可调，影响算法精度

### 算法页面（LLCamWorkJob）功能要求

1. **Job 选择**：显示当前可用的 Job 列表，支持切换
2. **算法配置显示**：显示当前 Job 的算法参数配置摘要（只读或快捷编辑）
3. **手动分析按钮**：触发单次算法执行（从 PILImage → Zmap → 算法 → 结果）
4. **结果显示**：显示算法检测到的焊缝轮廓、焊接面积、焊接点位置
5. **相机模式控制**：确保相机处于 PILImage 模式，必要时自动切换
6. **图像预览**：可选显示 Zmap 或算法处理后的结果图

### 相机设置页面（LLCameraSetting）与算法的协作边界

- LLCameraSetting **不负责**任何算法执行，仅配置相机硬件参数
- LLCamWorkJob **不负责**相机 IP/ROI 等基础参数设置，仅读取已配置的参数
- 两个页面的数据隔离：相机参数由 CameraRun/SensorManager 统一管理，算法页面通过 CameraRun 获取当前配置

## 知识库 RAG 强制规范

**目的**：确保所有涉及 EmguCV API 的代码实现都有知识库依据，避免凭记忆或推测编写 API 调用，减少运行时错误和版本兼容性问题。

**知识库路径**：`Knowledge/emgu-cv-knowledge-base/emgu-cv-knowledge-base.html`

### 强制读取时机

在以下任何场景下，**必须先读取知识库再编写代码**：

1. **新增算法功能**：在 `ImageAlgorithm.cs` 中新增任何图像处理算法（滤波、形态学、边缘检测、特征提取等）
2. **修改 Mat 操作**：涉及 `Mat` 构造函数、属性访问、方法调用、内存管理（Clone/Dispose/ROI）
3. **修改 PointCloudData 转换**：`ConvertContourToMat` 或相关点云→图像转换逻辑
4. **新增特征检测/匹配**：ORB/SIFT/特征匹配等相关 API
5. **修改颜色空间转换**：`CvInvoke.CvtColor` 及相关枚举
6. **任何不熟悉的 EmguCV API**：即使只是调用一个看似简单的静态方法

### 读取方式

使用 `Read` 工具读取知识库 HTML 文件的对应章节内容。知识库章节索引：

| 开发场景 | 必须读取的章节 |
|---------|--------------|
| Mat 创建/拷贝/ROI/Dispose | 2. Mat 核心数据结构 |
| 图像滤波（高斯/中值/双边） | 6.3 图像滤波 |
| 形态学操作（开/闭/膨胀/腐蚀） | 6.6 形态学操作 |
| 边缘检测（Canny/ Sobel/ Laplacian） | 6.4 边缘检测 |
| 轮廓检测与分析 | 18.5 轮廓检测与分析 |
| 颜色空间转换 | 6.2 颜色转换 |
| 特征检测（ORB/SIFT/SURF） | 3. 特征检测与匹配 |
| 点云相关操作 | 1. 点云与三维可视化 |
| 图像拼接 | 9. 图像拼接 |
| 相机标定 | 8. 相机标定与三维重建 |
| VideoCapture/VideoWriter | 5. Video 视频处理 |

### 读取流程

```
步骤1: 确定本次开发涉及哪些 EmguCV API
步骤2: 根据上表定位知识库章节
步骤3: 使用 Read 工具读取对应章节（HTML 文件支持按行读取）
步骤4: 从知识库中提取：API 签名、参数说明、返回值、注意事项、示例代码
步骤5: 基于提取的知识编写代码
步骤6: 代码审查时检查：每行 EmguCV API 调用都有知识库依据
```

### 禁止行为

- **禁止**不读取知识库直接编写 EmguCV API 调用
- **禁止**凭记忆或以往项目经验推测 API 参数顺序或类型
- **禁止**使用知识库中未提及的 API 重载或参数组合
- **禁止**忽略知识库中的"注意事项"和"平台限制"警告

### 知识库未覆盖的场景

如果知识库中没有当前开发场景所需的 API 说明：
1. 记录缺失场景
2. 通过 WebSearch 查找官方文档
3. 将查到的知识补充到知识库中（追加到 HTML 文件对应章节）
4. 然后再基于补充后的知识编写代码

## 交付标准

- [ ] 轮廓点云正确转换为Mat图像，轮廓线清晰可辨
- [ ] 各阶段预处理算法独立可测，参数可调
- [ ] 焊接接头类型识别准确率 > 90%
- [ ] 焊缝宽度、截面积、中心点计算正确
- [ ] 算法完成事件正确传递焊缝特征数据
- [ ] 参数变更实时生效，配置可保存/加载
- [ ] 算法执行失败时通过事件传递错误信息（不抛异常中断流程）
- [ ] 事件参数使用类级字段复用，避免高频GC压力
- [ ] Job 切换正确注入 PipelineManager，切换前自动保存当前配置
- [ ] Job 增删改查持久化到 INI，重启后配置恢复正确
- [ ] 至少保留一个默认 Job，删除时禁止删光
- [ ] JobManager 和 PipelineManager 单例初始化顺序正确（先 PipelineManager 后 JobManager）
- [ ] **知识库 RAG 检查通过**：所有 EmguCV API 调用都有知识库依据

## 协作关系

| 协作对象 | 协作内容 | 数据接口 |
|----------|----------|----------|
| **工业相机专员** | 接收3D轮廓点云数据 | `PointCloudData` (SmartRay/HikRobot回调) |
| **焊接工艺专员** | 传递焊缝特征数据（宽度/面积/中心点） | `AlgorithmCompletedEventArgs.SeamFeature` |
| **运动控制专员** | 传递焊缝偏移量引导XY轴移动 | `SeamFeatureResult.CenterX/CenterY` |
| **UI开发专员** | 算法参数配置界面（ParamLaserPage）、算法效果预览（LineLaserPage）、Job 切换 UI | `PipelineManager.Instance`, `JobManager.Instance`, `AlgorithmManager` |