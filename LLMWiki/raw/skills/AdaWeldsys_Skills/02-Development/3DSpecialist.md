---
name: "AdaWeldSystem 3D开发专员"
version: "V3.260629.1037"
description: "负责3D点云数据处理、HelixToolkit渲染可视化、表面重建算法和3D模型导入导出。"
---

# 3D 开发专员 Skill

## 描述

本 Skill 定义了 AdaWeldSystem 项目 3D 开发专员的职责边界、负责文件清单、技术要点和交付标准。

## 版本变更记录

| 版本 | 更新时间 | 变更级别 | 变更内容 |
|------|---------|---------|---------|
| V1.0 | 2026-06-23 | - | 初始版本。从原团队架构 skill 拆分独立。 |
| V1.260624.0950 | 2026-06-24 | 文档级 | 技术要求 | 新增"INI配置文件自动初始化规范"：首次使用时必须通过静态构造函数自动检查配置文件是否存在，不存在则生成默认配置 |
| V1.260624.1420 | 2026-06-24 | 文档级 | 技术要点 | 新增"HelixToolkit知识背景"章节：明确HelixToolkit CameraMode与PointCloudViewer CameraControlMode的区别；修正相机控制模式描述为自定义枚举 |
| V2.260626.0951 | 2026-06-26 | 结构级 | 技术要点 | 大幅扩展"HelixToolkit知识背景"章节：新增Viewport3DX Camera API完整参考（CameraMode/CameraRotationMode/CameraController/事件处理器/CameraSetting），补充源码级属性方法说明，用于优化平移/旋转/缩放功能 |
| V2.260626.1205 | 2026-06-26 | 文档级 | 技术要点 | 新增"项目实际交互经验"章节：记录用户在AdaWeldSystem中验证的HelixToolkit交互行为（右键旋转、右键+Shift平移、滚轮缩放、PerspectiveCamera、FixedRotationPoint、Turntable特性） |
| V3.260629.0852 | 2026-06-29 | 结构级 | 新增知识库 RAG 强制规范：任何涉及 HelixToolkit API 的代码开发前，必须先从 Knowledge/helixtoolkit-knowledge-base/ 抽取知识；保留原有 HelixToolkit 知识背景章节作为补充参考
| V3.260629.1037 | 2026-06-29 | 文档级 | 新增"Assimp 导入与 SceneNode 边界框历史教训"章节：记录 [37][38][39] 三次 bug 修复的经验，作为后续 3D 开发专员的强制性避坑指南

### 版本命名规则

- 格式：`V{大版本}.{小版本}`
- **大版本**：结构级修改时+1
- **小版本**：日期格式`yyMMdd.HHmm`

---

## /updateskill：Skill 自更新工作流

### 执行步骤

#### 步骤1：读取当前 skill 文件

读取 `d:\AdaWeldSystem0623\AdaWeldSystem\Skills\3DSpecialist.md` 的当前内容。

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

保存路径：`d:\AdaWeldSystem0623\AdaWeldSystem\Backup\Skills\3DSpecialist_V{版本号}.md`

#### 步骤5：通知用户变更

---

## 核心职责

- 3D点云数据结构与基础操作
- 点云文件 I/O（TXT/XYZ/PLY/OBJ）
- 3D渲染与可视化（HelixToolkit.Wpf.SharpDX）
- 表面重建算法（三角剖分、泊松重建、MLS等）
- 3D模型导入（OBJ/STL等，通过 Assimp）
- 交互操作（平移/旋转/缩放/环绕）

## 负责文件清单

```
PointCloudData/
├── 3DModel/
│   ├── Point3D.cs             ← 3D点/彩色点结构体
│   └── PointCloudData.cs      ← 点云数据容器
├── DataIO/
│   ├── PointCloudReader.cs    ← 点云文件读取
│   └── PointCloudWriter.cs    ← 点云文件写入
└── Render/
    ├── PointCloudViewer.cs    ← 3D点云查看器（HelixToolkit）
    ├── SurfaceTriangulator.cs ← 表面重建算法
    └── RenderConfig.cs        ← 渲染参数配置类（INI持久化）
```

## 技术要点

- 几何体: `PointGeometry3D`, `MeshGeometry3D`
- 模型: `PointGeometryModel3D`, `MeshGeometryModel3D`
- 集合类型: `Vector3Collection`, `Color4Collection`, `IntCollection`
- 使用 `System.Numerics.Vector3` 进行数学运算
- 空间索引: 自定义 `SpatialIndex` 类（网格哈希）
- 重建算法: 邻域搜索、Ball Pivoting、Alpha Shape、Delaunay、Poisson、MLS
- 相机控制模式: PointCloudViewer.CameraControlMode（自定义枚举：Rotate/Move/Round），**非** HelixToolkit.CameraMode
- 渲染参数: RenderConfig 静态类，6种算法参数，INI持久化

## 知识库 RAG 强制规范

**目的**：确保所有涉及 HelixToolkit API 的代码实现都有知识库依据，避免凭记忆或推测编写 API 调用，减少运行时错误和版本兼容性问题。

**知识库路径**：`Knowledge/helixtoolkit-knowledge-base/helixtoolkit-knowledge-base.html`

### 强制读取时机

在以下任何场景下，**必须先读取知识库再编写代码**：

1. **新增 3D 渲染功能**：在 `PointCloudViewer.cs` 中新增任何 HelixToolkit 相关功能（几何体创建、材质设置、灯光配置、相机控制等）
2. **修改 Viewport3DX 属性**：涉及 `Camera`、`CameraMode`、`CameraRotationMode`、`EffectsManager` 等核心属性
3. **修改点云/网格显示**：`PointGeometry3D`、`MeshGeometry3D`、`PointGeometryModel3D`、`MeshGeometryModel3D` 的创建或更新
4. **新增表面重建算法**：涉及 `SurfaceTriangulator` 或任何 mesh 生成逻辑
5. **修改导入导出功能**：Assimp 导入、PLY/OBJ 读写相关 API
6. **任何不熟悉的 HelixToolkit API**：即使只是调用一个看似简单的属性或方法

### 读取方式

使用 `Read` 工具读取知识库 HTML 文件的对应章节内容。知识库章节索引：

| 开发场景 | 必须读取的章节 |
|---------|--------------|
| 几何体创建（点/线/网格） | Geometry3D / MeshGeometry3D / PointGeometry3D / LineGeometry3D |
| 材质配置（PBR/Phong/Diffuse） | MaterialCore / PBRMaterialCore / PhongMaterialCore / DiffuseMaterialCore |
| 场景节点管理 | SceneNode / GroupNode / GeometryNode / MeshNode / PointNode / LineNode |
| 灯光配置 | LightNode / AmbientLightNode / DirectionalLightNode / PointLightNode / SpotLightNode |
| 相机控制 | 相机系统 |
| 渲染主机设置 | 渲染主机 / EffectsManager |
| 模型导入 | Importer / MeshBuilder |
| 点云渲染 | 点云渲染 |
| GPU 实例化 | GPU 实例化 |
| 动态几何体 | 动态几何体 |
| 基础场景搭建 | 基础网格场景 |

### 读取流程

```
步骤1: 确定本次开发涉及哪些 HelixToolkit API
步骤2: 根据上表定位知识库章节
步骤3: 使用 Read 工具读取对应章节（HTML 文件支持按行读取）
步骤4: 从知识库中提取：API 签名、参数说明、返回值、注意事项、示例代码
步骤5: 基于提取的知识编写代码
步骤6: 代码审查时检查：每行 HelixToolkit API 调用都有知识库依据
```

### 禁止行为

- **禁止**不读取知识库直接编写 HelixToolkit API 调用
- **禁止**凭记忆或以往项目经验推测 API 参数顺序或类型
- **禁止**使用知识库中未提及的 API 重载或参数组合
- **禁止**忽略知识库中的"注意事项"和"平台限制"警告

### 知识库与本 Skill 的关系

- **知识库（Knowledge/helixtoolkit-knowledge-base/）** 是**首要参考**：包含完整 API 签名、参数列表、示例代码、注意事项，是编写代码前的**强制读取源**
- **本 Skill 的"HelixToolkit 知识背景"章节** 是**补充参考**：记录本项目已验证的交互行为、设计约束、实际经验，用于理解为什么这样设计，但不替代知识库的 API 参考

### 知识库未覆盖的场景

如果知识库中没有当前开发场景所需的 API 说明：
1. 记录缺失场景
2. 通过 WebSearch 查找 HelixToolkit 官方文档或源码
3. 将查到的知识补充到知识库中（追加到 HTML 文件对应章节）
4. 然后再基于补充后的知识编写代码

### HelixToolkit 知识背景（强制，补充参考）

**涉及 HelixToolkit 的修改和调用时，必须参考本章节。**

#### HelixToolkit CameraMode vs PointCloudViewer CameraControlMode

本项目存在两种相机模式概念，**严禁混淆**：

| 概念 | 定义位置 | 类型 | 用途 |
|------|---------|------|------|
| `HelixToolkit.Wpf.SharpDX.CameraMode` | HelixToolkit 库内部枚举 | `Inspect`, `Rotate`, `Zoom`, `Pan`, `Walk`, `Turntable` 等 | HelixToolkit 内置相机控制器的模式切换 |
| `PointCloudViewer.CameraControlMode` | PointCloudViewer.cs 嵌套枚举 | `Rotate`, `Move`, `Round` | 本项目自定义的 UI 按钮功能模式 |

**关键区别**：
1. **HelixToolkit CameraMode** 是 HelixToolkit 库自带的相机控制器模式，用于控制 Viewport3DX 内置的旋转/平移/缩放等交互行为。设置方式为 `_viewport.CameraMode = CameraMode.Rotate;`
2. **PointCloudViewer CameraControlMode** 是本项目在 PointCloudViewer 类中自定义的枚举，用于 UI 按钮的功能切换。它**借助** HelixToolkit 的底层能力（如设置 `IsRotationEnabled`/`IsPanEnabled`），但通过自定义的 `HandleRotateMode`/`HandleMoveMode`/`HandleRoundMode` 方法实现具体的相机运动逻辑

**映射关系**（非 1:1）：
- `CameraControlMode.Rotate` → 设置 `IsRotationEnabled=true, IsPanEnabled=false`，内部通过 `HandleRotateMode()` 围绕模型中心旋转相机位置
- `CameraControlMode.Move` → 设置 `IsRotationEnabled=false, IsPanEnabled=true`，内部通过 `HandleMoveMode()` 沿相机 Right/Up 方向平移
- `CameraControlMode.Round` → 设置 `IsRotationEnabled=true, IsPanEnabled=false`，内部通过 `HandleRoundMode()` 旋转相机 LookDirection（轨道模式）

**调用规范**：
- UI 层（Helix3Drender.cs）使用 `PointCloudViewer.CameraControlMode` 枚举
- UI 层通过 `_pointCloudViewer.SetCameraMode(mode)` 设置模式
- UI 层通过 `_pointCloudViewer.OnMouseDown/OnMouseMove/OnMouseUp()` 委托鼠标事件
- **禁止**在 UI 层直接使用 `HelixToolkit.CameraMode` 枚举
- **禁止**在 UI 层直接调用 `_viewport.CameraMode = ...`

#### HelixToolkit 核心类型参考

| 类型 | 命名空间 | 用途 |
|------|---------|------|
| `Viewport3DX` | HelixToolkit.Wpf.SharpDX | WPF 3D 视口控件，承载所有 3D 内容 |
| `PerspectiveCamera` | HelixToolkit.Wpf.SharpDX | 透视相机，通过 Position/LookDirection/UpDirection 控制 |
| `OrthographicCamera` | HelixToolkit.Wpf.SharpDX | 正交相机 |
| `DefaultEffectsManager` | HelixToolkit.Wpf.SharpDX | 默认渲染效果管理器 |
| `PointGeometry3D` | HelixToolkit.SharpDX | 点几何体数据（Positions/Colors/Indices） |
| `MeshGeometry3D` | HelixToolkit.SharpDX | 网格几何体数据 |
| `PointGeometryModel3D` | HelixToolkit.Wpf.SharpDX | 点渲染模型 |
| `MeshGeometryModel3D` | HelixToolkit.Wpf.SharpDX | 网格渲染模型 |
| `PhongMaterial` | HelixToolkit.Wpf.SharpDX | Phong 光照材质 |
| `AmbientLight3D` | HelixToolkit.Wpf.SharpDX | 环境光 |
| `DirectionalLight3D` | HelixToolkit.Wpf.SharpDX | 方向光 |
| `TransformManipulator3D` | HelixToolkit.Wpf.SharpDX | 3D 变换操纵器 |
| `Vector3Collection` | HelixToolkit | Vector3 集合 |
| `Color4Collection` | HelixToolkit | Color4 集合 |
| `IntCollection` | HelixToolkit | int 集合 |

#### Viewport3DX 相机属性详解

| 属性 | 类型 | 读写 | 说明 |
|------|------|------|------|
| `Camera` | ProjectionCamera | R/W | 当前相机实例（PerspectiveCamera 或 OrthographicCamera） |
| `CameraMode` | CameraMode | R/W | 相机控制模式（Inspect/WalkAround/FixedPosition），决定鼠标交互行为 |
| `CameraRotationMode` | CameraRotationMode | R/W | 旋转模式（Turntable/Turnball/Trackball），决定旋转自由度 |
| `EffectsManager` | IEffectsManager | R/W | 渲染效果管理器（必须设置，否则黑屏） |
| `BackgroundColor` | Color | R/W | 视口背景颜色 |
| `Items` | ItemCollection | R | 3D 对象集合（灯光、模型、几何体等） |
| `IsRotationEnabled` | bool | R/W | 是否启用旋转交互（默认 true） |
| `IsPanEnabled` | bool | R/W | 是否启用平移交互（默认 true） |
| `IsZoomEnabled` | bool | R/W | 是否启用缩放交互（默认 true） |
| `UseDefaultGestures` | bool | R/W | 是否使用默认鼠标手势（左键旋转、右键平移、滚轮缩放） |
| `ShowCoordinateSystem` | bool | R/W | 是否显示右下角 XYZ 坐标系指示器 |
| `ShowFrameRate` | bool | R/W | 是否显示左上角帧率信息 |
| `EnableDesignModeRendering` | bool | R/W | 设计模式下是否渲染（VS 设计器中使用） |
| `IsShadowMappingEnabled` | bool | R/W | 是否启用阴影映射 |

**关键依赖**：
- `Camera` 和 `EffectsManager` 是**必须设置**的核心属性，缺一不可
- `CameraMode`/`CameraRotationMode` 的变更会实时改变鼠标交互行为，无需重建视口
- `IsRotationEnabled`/`IsPanEnabled`/`IsZoomEnabled` 是独立开关，可与 `CameraMode` 组合使用

#### CameraMode 枚举详解（HelixToolkit 内置）

| 枚举值 | 行为描述 | 鼠标左键 | 鼠标右键 | 滚轮 |
|--------|---------|---------|---------|------|
| `Inspect` | 检视模式（默认）：固定目标点，旋转/平移围绕目标 | 旋转相机 | 平移相机 | 缩放（移动相机距离） |
| `WalkAround` | 漫游模式：固定相机位置，改变朝向 | 旋转朝向 | 平移（受限） | 改变视野 FOV |
| `FixedPosition` | 固定位置模式：相机位置不动，仅缩放改变 FOV | 旋转（受限） | 平移（受限） | 改变 FOV |

**使用建议**：
- 点云浏览场景推荐 `Inspect`（最自然的旋转/平移/缩放体验）
- 第一人称漫游场景使用 `WalkAround`
- 固定观察点场景使用 `FixedPosition`

#### CameraRotationMode 枚举详解

| 枚举值 | 旋转轴 | 适用场景 | 说明 |
|--------|--------|---------|------|
| `Turntable` | 2 轴（模型 Up + Right） | 建筑、机械零件 | 限制在水平面旋转，防止翻转 |
| `Turnball` | 3 轴（Forward/Right/Up） | 自由观察 | 类似手持球体旋转，更自由 |
| `Trackball` | 虚拟轨迹球 | 精细控制 | 屏幕映射到虚拟球面，适合精确旋转 |

**使用建议**：
- 焊接工件观察推荐 `Turntable`，保持工件直立
- 复杂模型全方位观察可用 `Turnball` 或 `Trackball`

#### CameraController 属性与方法（内置交互控制器）

Viewport3DX 内部包含 `CameraController` 实例，负责处理所有鼠标/触摸/键盘交互。

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| `CameraController.Camera` | ProjectionCamera | 当前控制的相机（与 Viewport3DX.Camera 同步） |
| `CameraController.CameraMode` | CameraMode | 当前相机模式 |
| `CameraController.CameraRotationMode` | CameraRotationMode | 当前旋转模式 |
| `CameraController.IsRotationEnabled` | bool | 旋转是否启用 |
| `CameraController.IsPanEnabled` | bool | 平移是否启用 |
| `CameraController.IsZoomEnabled` | bool | 缩放是否启用 |
| `CameraController.IsMoveEnabled` | bool | 移动是否启用（Walk 模式） |
| `CameraController.RotationSensitivity` | double | 旋转灵敏度 |
| `CameraController.PanSensitivity` | double | 平移灵敏度 |
| `CameraController.ZoomSensitivity` | double | 缩放灵敏度 |
| `CameraController.InertiaFactor` | double | 惯性因子（松手后继续滑动的程度） |
| `CameraController.IsInertiaEnabled` | bool | 是否启用惯性 |

**核心方法**：

| 方法 | 签名 | 功能 |
|------|------|------|
| `ResetCamera` | `ResetCamera()` | 重置相机到默认位置和目标 |
| `ZoomExtents` | `ZoomExtents(double animationTime = 0)` | 自适应缩放，使所有模型完整显示在视口内 |
| `LookAt` | `LookAt(Point3D target, double animationTime = 0)` | 改变相机注视点 |
| `ChangeDirection` | `ChangeDirection(Vector3D lookDir, Vector3D upDir, double time = 0)` | 改变相机朝向 |
| `AddRotateForce` | `AddRotateForce(double dx, double dy)` | 以编程方式施加旋转力（惯性效果） |
| `AddPanForce` | `AddPanForce(double dx, double dy)` | 以编程方式施加平移力 |
| `AddZoomForce` | `AddZoomForce(double delta)` | 以编程方式施加缩放量 |
| `PushCameraSetting` | `PushCameraSetting()` | 将当前相机状态压入内部堆栈 |
| `RestoreCameraSetting` | `RestoreCameraSetting()` | 从堆栈恢复相机状态 |

**使用规范**：
- **禁止**在 UI 层直接访问 `CameraController`（应通过 `PointCloudViewer` 封装方法）
- `ResetCamera()` 和 `ZoomExtents()` 是常用方法，可在 `PointCloudViewer` 中暴露为公共方法
- `PushCameraSetting`/`RestoreCameraSetting` 可用于实现"视角记忆"功能

#### 事件处理器（Handler）内部机制

HelixToolkit 通过以下 Handler 处理鼠标交互，理解其机制有助于自定义交互行为：

**PanHandler（平移处理器）**

| 方法 | 功能 |
|------|------|
| `Pan(Vector3D)` | 按 3D 向量平移相机位置和目标点 |
| `Pan(Vector)` | 按 2D 屏幕向量平移相机 |
| `Delta(ManipulationEventArgs)` | 鼠标移动时计算平移增量 |
| `Started/Completed` | 鼠标按下/释放时触发 |

**RotateHandler（旋转处理器）**

| 方法 | 功能 |
|------|------|
| `Rotate(Point, Point, Point3D)` | 围绕指定 3D 点旋转相机 |
| `RotateTurntable(Vector, Point3D)` | 使用转盘模式（2 轴）旋转 |
| `RotateTurnball(Point, Point, Point3D)` | 使用 Turnball 模式（3 轴）旋转 |
| `RotateTrackball(Point, Point, Point3D)` | 使用轨迹球模式旋转 |
| `Delta(ManipulationEventArgs)` | 鼠标移动时计算旋转增量 |

**ZoomHandler（缩放处理器）**

| 方法 | 功能 |
|------|------|
| `Zoom(double delta)` | 按增量缩放 |
| `Zoom(double delta, Point3D zoomAround)` | 围绕指定点缩放 |
| `ZoomByChangingCameraPosition` | 通过移动相机位置实现缩放 |
| `ZoomByChangingFieldOfView` | 通过改变 FOV 实现缩放 |
| `Delta(ManipulationEventArgs)` | 鼠标滚轮/手势时计算缩放量 |

#### CameraSetting（相机配置持久化）

用于保存/恢复相机状态，可配合 INI 实现视角配置持久化。

| 属性 | 类型 | 说明 |
|------|------|------|
| `Position` | Point3D | 相机位置 |
| `LookDirection` | Vector3D | 相机注视方向 |
| `UpDirection` | Vector3D | 相机上方向 |
| `FieldOfView` | double | 视野角度（透视相机） |
| `NearPlaneDistance` | double | 近裁剪面距离 |
| `FarPlaneDistance` | double | 远裁剪面距离 |
| `Width` | double | 视口宽度（正交相机） |

| 方法 | 功能 |
|------|------|
| `CameraSetting(ProjectionCamera)` | 从现有相机构造设置 |
| `UpdateCamera(ProjectionCamera)` | 将设置应用到相机 |

#### 与 PointCloudViewer 协作的优化指南

**1. 交互开关的正确使用**

```csharp
// 在 PointCloudViewer 中根据 CameraControlMode 设置交互开关
void UpdateInteractionState(CameraControlMode mode)
{
    switch (mode)
    {
        case CameraControlMode.Rotate:
            _viewport.IsRotationEnabled = true;
            _viewport.IsPanEnabled = false;
            // 可设置旋转模式为 Turntable 防止翻转
            _viewport.CameraRotationMode = CameraRotationMode.Turntable;
            break;
        case CameraControlMode.Move:
            _viewport.IsRotationEnabled = false;
            _viewport.IsPanEnabled = true;
            break;
        case CameraControlMode.Round:
            _viewport.IsRotationEnabled = true;
            _viewport.IsPanEnabled = false;
            // 轨道模式适合使用 Turnball
            _viewport.CameraRotationMode = CameraRotationMode.Turnball;
            break;
    }
}
```

**2. 自适应视角调整**

```csharp
// 加载点云后自动调整视角
public void FitViewToPointCloud()
{
    // ... 计算边界框 ...
    
    // 使用 Viewport3DX 的内置方法自适应缩放
    _viewport.ZoomExtents(0); // 0 表示无动画
}
```

**3. 相机状态保存/恢复**

```csharp
// 保存当前视角
public void SaveCurrentView()
{
    if (_viewport.Camera is PerspectiveCamera cam)
    {
        var setting = new CameraSetting(cam);
        // 保存到 INI 或内存
    }
}

// 恢复视角
public void RestoreView(CameraSetting setting)
{
    setting.UpdateCamera(_viewport.Camera);
}
```

**4. 注意事项**

- `Camera` 属性必须同时设置 `Position`、`LookDirection`、`UpDirection`，缺一不可
- 修改相机属性后，**不需要**手动刷新，Viewport3DX 会自动响应 `INotifyPropertyChanged`
- `EffectsManager` 在 Viewport3DX 卸载时必须释放，否则进程无法正常退出
- 鼠标事件优先绑定到 `Viewport3DX`（WPF 事件），而非 ElementHost（WinForms 事件）

#### 项目实际交互经验（AdaWeldSystem 验证结论）

**以下结论来自在 AdaWeldSystem 项目中对 HelixToolkit.Wpf.SharpDX 的实际操作验证，优先于理论文档。**

**1. 鼠标交互映射**

| 操作 | 行为 | 触发条件 |
|------|------|---------|
| 旋转 | 围绕旋转点旋转相机/模型视角 | 鼠标**右键**拖动 |
| 平移 | 沿相机 Right/Up 方向平移场景 | 鼠标**右键 + Shift** 拖动 |
| 缩放 | 改变相机与目标点的距离 | 鼠标**滚轮**滚动 |

**关键结论**：
- **右键负责旋转，右键+Shift 负责平移**（与默认文档描述的左键旋转/右键平移不同）
- 滚轮缩放始终有效（只要 `IsZoomEnabled = true`）

**2. Camera 配置约束**

- Viewport3DX 的 `Camera` 必须设置为 `PerspectiveCamera`，而非 `OrthographicCamera`
- 透视相机的参数设置示例：

```csharp
_viewport.Camera = new PerspectiveCamera
{
    Position = new Point3D(5, 5, 10),
    LookDirection = new Vector3D(-5, -5, -10),
    UpDirection = new Vector3D(0, 1, 0),
    FieldOfView = 45,
    NearPlaneDistance = 0.001,
    FarPlaneDistance = 100000
};
```

**3. 旋转点控制（Inspect 模式）**

在 `CameraMode.Inspect` 下，旋转行为由以下两个属性联合控制：

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `FixedRotationPointEnabled` | bool | false | 是否启用固定旋转点 |
| `FixedRotationPoint` | Point3D | (0, 0, 0) | 固定旋转点坐标 |
| `RotateAroundMouseDownPoint` | bool | false | 是否围绕鼠标点击点旋转 |

**使用场景**：
- **围绕模型中心旋转**：设置 `FixedRotationPointEnabled = true`，并将 `FixedRotationPoint` 设为模型中心点坐标
- **围绕鼠标点击位置旋转**：设置 `RotateAroundMouseDownPoint = true`（此时以鼠标在 3D 空间中命中点的位置为旋转中心）
- **默认行为（相机位置不变，旋转 LookDirection）**：两个属性均为 false

```csharp
// 围绕模型中心旋转的推荐配置
_viewport.FixedRotationPointEnabled = true;
_viewport.FixedRotationPoint = new Point3D(centerX, centerY, centerZ);
_viewport.RotateAroundMouseDownPoint = false;
```

**4. Turntable 旋转模式特性**

- `CameraRotationMode.Turntable` 会**固定围绕 Y 轴（世界坐标系 Up 方向）**旋转
- 视觉效果：旋转方向**不跟随鼠标移动方向**，而是被约束在水平面内
- 适用场景：需要保持模型直立、防止翻转的观察场景（如焊接工件浏览）
- 不适用场景：需要自由全方位旋转的精细观察

**使用建议**：
- 如果用户反馈"旋转不跟手"、"旋转方向奇怪"，检查是否误用了 `Turntable` 模式
- 自由旋转推荐 `Turnball` 或 `Trackball` 模式

### INI配置文件自动初始化规范（强制）

**要求**：所有使用 INI 文件持久化的配置类（如 RenderConfig），必须在类首次被访问时自动检查配置文件是否存在，不存在则生成包含所有默认参数的配置文件。

**实现方式**：使用静态构造函数 + 双重检查锁定

```csharp
private static bool _isInitialized = false;
private static readonly object _lock = new object();

static RenderConfig()
{
    EnsureInitialized();
}

public static void EnsureInitialized()
{
    if (_isInitialized) return;
    lock (_lock)
    {
        if (_isInitialized) return;
        try
        {
            if (!File.Exists(IniFilePath))
            {
                SaveToIni(); // 使用属性默认值生成默认配置
            }
            else
            {
                LoadFromIniInternal();
            }
            _isInitialized = true;
        }
        catch
        {
            _isInitialized = true; // 失败时使用默认值继续运行
        }
    }
}
```

**设计原则**：
- **无感初始化**：开发者无需手动调用初始化方法，类首次使用自动完成
- **线程安全**：双重检查锁定确保多线程环境安全
- **异常安全**：初始化失败时使用属性默认值继续运行，不阻塞程序启动
- **向后兼容**：保留 LoadFromIni/SaveToIni 公开方法，外部调用不受影响

### SurfaceRenderAlgorithm 枚举

| 算法 | 说明 | 关键参数 |
|------|------|----------|
| NeighborSearch | 邻域搜索 | 搜索半径 |
| BallPivoting | Ball Pivoting | 球半径、角度 |
| AlphaShape | Alpha Shape | Alpha值 |
| Delaunay3D | Delaunay三角剖分 | 最大边长 |
| Poisson | 泊松重建 | 八叉树深度 |
| MLS | 移动最小二乘 | 搜索半径 |

## 交付标准

- [ ] 支持 TXT/XYZ/PLY/OBJ 导入导出
- [ ] 点云显示流畅（支持降采样）
- [ ] 至少 3 种表面重建算法可用
- [ ] 视角自适应调整
- [ ] 支持 OBJ/STL 模型导入显示
- [ ] 支持 TransformManipulator3D 交互
- [ ] 渲染参数可配置可持久化
- [ ] **知识库 RAG 检查通过**：所有 HelixToolkit API 调用都有知识库依据

## 协作关系

| 协作对象 | 协作内容 | 数据接口 |
|----------|----------|----------|
| **UI开发专员** | 3D点云/模型显示页面、交互控制 | `PointCloudViewer`, `PointCloudData` |
| **焊接工艺专员** | 焊缝点云数据用于特征提取 | `PointCloudData`, `PointCloudReader` |

---

## Assimp 导入与 SceneNode 边界框历史教训（强制避坑指南）

> **以下四条教训来自 AdaWeldSystem 项目中 Assimp PLY 导入功能的实际 bug 修复（history.md [37][38][39]）。任何涉及 HelixToolkit `SceneNode` / Assimp 导入 / 边界框计算 / 相机自适应的代码，必须逐条对照执行，禁止跳过。**

### 教训一：SceneNode 父子附加规则 — [37] "SceneNode already attach to a different node"

**问题场景**：使用 `HelixToolkit.SharpDX.Assimp.Importer.Load()` 导入模型后，试图遍历 `scene.Root.Items` 将子节点逐个添加到 `SceneNodeGroupModel3D`。

**异常**：`SceneNode already attach to a different node`

**根因**：`Importer.Load()` 返回的 `HelixToolkitScene` 中，所有子节点在导入时已被自动附加到 `scene.Root` 上。`SceneNode` 的父子关系是**一对一**的，再次 `AddChildNode()` 会触发异常。

**强制规范**：
```csharp
// 正确：将根节点整体添加
_sceneModel.GroupNode.AddChildNode(scene.Root);

// 错误：逐个添加子节点
foreach (var child in scene.Root.Items)
{
    _sceneModel.GroupNode.AddChildNode(child); // 抛出异常
}
```

---

### 教训二：Bounds 只读计算属性的退化值问题 — [38] 模型飞出视野

**问题场景**：`FitViewToScene()` 直接使用 `rootNode.Bounds` 计算边界框，然后设置相机位置。执行后模型飞出视野或看不到。

**根因**：`SceneNode.Bounds` 是**只读计算属性**，其值基于子节点几何体的顶点数据动态计算。但在某些情况下（如节点尚未完成布局、几何体未加载、或内部 GroupNode 的空节点干扰），`Bounds` 可能返回**退化值**（全零或极小值），导致相机定位错误。

**强制规范**：
- **禁止**直接依赖 `rootNode.Bounds` 作为唯一边界框来源
- **必须**递归遍历 `SceneNode` 树，累加所有子节点的 `Bounds`
- **必须**对累加结果进行有效性验证后再用于相机计算

```csharp
// 正确：递归累加所有子节点的非空 Bounds
void AccumulateBounds(SceneNode node)
{
    var b = node.Bounds;
    // ... 空/无效检查（见教训三） ...
    if (!isEmpty)
    {
        if (b.Minimum.X < minX) minX = b.Minimum.X;
        if (b.Maximum.X > maxX) maxX = b.Maximum.X;
        // ... Y, Z 同理 ...
        hasBounds = true;
    }
    if (node is GroupNode group)
    {
        foreach (var child in group.Items)
            AccumulateBounds(child);
    }
}
```

---

### 教训三：空/无效边界框的严格检查规范 — [39] 纯黑界面

**问题场景**：`FitViewToScene()` 执行后界面**纯黑**。调试发现 `center = 1.7E+38`，`distance = Infinity`，`cameraPosition = {∞, -∞, ∞}`。

**根因**：某些 HelixToolkit 内部节点（如空 GroupNode、未初始化的中间节点）的 `Bounds` 返回**异常哨兵值**（如 `Minimum = (float.MaxValue, float.MaxValue, float.MaxValue)` 而 `Maximum = (0, 0, 0)`）。原有的 `isEmpty` 检查仅排除 `(0,0,0)`，无法过滤这类异常值，导致边界框计算溢出为 Infinity，相机参数无效，渲染管线失败。

**强制规范**：`isEmpty` 检查必须同时满足以下三条规则：

```csharp
// 规则1：Minimum >= Maximum 是空边界框的标准特征
bool isEmpty = b.Minimum.X >= b.Maximum.X
            && b.Minimum.Y >= b.Maximum.Y
            && b.Minimum.Z >= b.Maximum.Z;

// 规则2：过滤 Infinity / NaN 异常值
if (!isEmpty)
{
    if (float.IsInfinity(b.Minimum.X) || float.IsInfinity(b.Maximum.X) ||
        float.IsNaN(b.Minimum.X) || float.IsNaN(b.Maximum.X) ||
        // ... Y, Z 同理 ...
       )
    {
        isEmpty = true;
    }
}

// 规则3：总边界框计算完成后，验证 min <= max 关系
if (!hasBounds || minX > maxX || minY > maxY || minZ > maxZ)
    return; // 安全返回，不调整相机
```

**特别警告**：
- `float.MaxValue`（约 `3.4E+38`）和 `float.MinValue`（约 `-3.4E+38`）的初始值**不能作为有效数据**
- 如果一个节点的 `Bounds` 仅更新了 `minX` 而 `maxX` 保持 `float.MinValue`，最终 `(minX + maxX) / 2` 可能产生 `1.7E+38` 这类看似"正常"实则完全错误的中心点
- **必须**在累加完成后检查 `minX <= maxX`（而不是依赖 `hasBounds` 标志）

---

### 教训四：相机参数有效性验证

**问题场景**：即使边界框计算正确，如果 `radius` 或 `distance` 为 Infinity/NaN，直接赋值给 `PerspectiveCamera` 仍会导致黑屏或视图异常。

**强制规范**：在设置相机属性前，必须验证所有派生参数：

```csharp
float radius = /* ... 从边界框计算 ... */;
if (radius < 0.001f) radius = 100f;

// 必须在设置相机前验证
if (float.IsInfinity(radius) || float.IsNaN(radius))
    return; // 安全返回，不修改相机

// 同样验证 center
center = new Vector3((minX + maxX) / 2, (minY + maxY) / 2, (minZ + maxZ) / 2);
if (float.IsInfinity(center.X) || float.IsNaN(center.X))
    return;

// 现在可以安全设置相机
perspectiveCamera.Position = cameraPosition;
perspectiveCamera.LookDirection = lookDirection;
perspectiveCamera.UpDirection = upDirection;
```

**关键参数安全阈值**：
| 参数 | 危险值 | 验证方式 |
|------|--------|---------|
| `radius` | `Infinity`, `NaN`, `< 0.001f` | `float.IsInfinity`, `float.IsNaN`, 阈值检查 |
| `center.X/Y/Z` | `Infinity`, `NaN`, `> 1E+30` | `float.IsInfinity`, `float.IsNaN` |
| `distance` | `Infinity`, `NaN` | `float.IsInfinity`, `float.IsNaN` |
| `cameraPosition` 分量 | `Infinity`, `NaN` | 赋值前对 `center + distance` 结果验证 |

---

### 检查清单（强制）

在提交任何涉及 `SceneNode.Bounds` 累加或相机自适应调整的代码前，必须逐项确认：

- [ ] `SceneNode` 添加时遵循"整体添加根节点"原则，未逐个遍历 `Items`
- [ ] `AccumulateBounds` 使用递归遍历所有子节点，而非仅读取根节点 `Bounds`
- [ ] `isEmpty` 检查包含 `Minimum >= Maximum` 条件
- [ ] `isEmpty` 检查过滤了 `float.IsInfinity` 和 `float.IsNaN`
- [ ] 累加完成后验证了 `minX <= maxX && minY <= maxY && minZ <= maxZ`
- [ ] `radius` 计算后验证了非 Infinity / 非 NaN
- [ ] `center` 计算后验证了非 Infinity / 非 NaN
- [ ] 相机赋值前所有参数已通过上述验证
| **运动控制专员** | 自动对焦Z轴偏移量 | `PointCloudData` (Z轴高度数据) |