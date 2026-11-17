# 需求覆盖与实现状态（AdaWeldSystem）

> 跨分类溯源页：把《产品软件设计需求书》的功能需求 FR-001~FR-051 与**当前代码 / 架构事实**逐条对照，标注实现状态。
> 本页是「需求 → 模块」的唯一溯源锚点；模块细节见 [[modules/DeviceControl]] 与 `modules/` 下各页，架构约束见 [[architecture/DeviceControlArchitecture]]。
> 编制：2026-09-18｜基线需求书 V1.0（2026-07-02）已严重偏离现行代码，本页以代码事实为准。

---

## 状态图例

| 标记 | 含义 |
|------|------|
| ✅ 已实现 | 代码存在与需求意图一致的工作实现 |
| 🔄 重构实现 | 需求被满足，但经架构重构（类名/机制与原需求书不同） |
| ⚠️ 部分实现 | 主体可用，存在已知缺口或占位 |
| ❌ 已删除 | 原需求对应的旧实现已被移除，由新机制替代（需求书未更新） |
| ⬜ 未实现 | 代码中无对应实现 |

---

## 一、相机控制（FR-001~FR-007）

| 需求 | 状态 | 现行对应 | 说明 |
|------|------|---------|------|
| FR-001 SmartRay 连接 | ❌ 已删除 | [[modules/LineLaserCam]] | SmartRay SDK 与 `CameraRun`/`CameraSelector` 已删；线激光相机现由英莱 `IntelligentLaserCam` + `VirtualCam` 经 [[api/LineLaserManager]] 承载（ADR-017/035/040） |
| FR-002 SmartRay PIL 采集 | ❌ 已删除 | [[api/IntelligentLaserCam]] | 英莱 `MillionOutlineInspect` 回调采集取代 PIL 模式；"PIL/Live 模式"概念已随 ADR-010 删除 |
| FR-003 SmartRay Live 采集 | ❌ 已删除 | [[api/MonitorCamManager]] | ADR-010 删除 Live/PIL，改为单次触发采集；监控相机现用麦格威（MecaVision） |
| FR-004 海康 3D 相机 | ❌ 已删除 | [[api/MonitorCamManager]] | 海康 3D 实现删除，监控相机改麦格威 `MecaVisionCam`（ADR-034） |
| FR-005 相机参数配置 | 🔄 重构实现 | [[api/IntelligentLaserCam]] / `LineLaserConfig.xml` | 参数以设备为唯一真相源（英莱 Job 参数 + 线激光标定），持久化 `Config/LineLaser/LineLaser_XML/LineLaserConfig.xml` |
| FR-006 点云数据生成 | ✅ 已实现 | [[modules/PointCloudData]] | 轮廓 → 点云 → Mat 链路（`PointCloudData` / `PointCloudWriter` / 轮廓渲染） |
| FR-007 相机预设管理 | ⚠️ 部分实现 | `LineLaserConfig` | 旧 `CameraPresetManager` 删除；现行单套 `LineLaserConfig` 加载/保存，多预设快速切换未实现 |

## 二、图像处理（FR-008~FR-016）

| 需求 | 状态 | 现行对应 | 说明 |
|------|------|---------|------|
| FR-008 算法管线配置 | 🔄 重构实现 | [[modules/EmguALG]] | 旧 5 级 `PipelineManager`/`Job` 流水线删除（ADR-007）；现三层 `Abstractions` + `RealtimeMonitor` + `Manager` |
| FR-009~012 滤波/形态学/边缘/特征 | ✅ 已实现 | [[api/AlgorithmManager]] | `EmguALG/Core/ImageAlgorithm.cs` 承载各算子 |
| FR-013 焊缝特征计算 | ✅ 已实现 | [[api/LineLaserContourAlgorithm]] | 轮廓 Mat 渲染 + 焊缝特征（`FeatureY/FeatureZ`/`Width0/Width1`） |
| FR-014 焊缝宽度滑动平均 | 🔄 重构实现 | [[api/WeldParamAdjustmentAlgorithm]] | 现为实时滑动平滑（宽度驱动参数调整内），非独立 `SeamCalData` |
| FR-015 Job 管理 | ❌ 已删除 | [[api/WeldParamManager]] | 旧 `JobManager` 删除（ADR-007）；现为算法配置 `WeldAlgorithmsConfig`（两节合一） |
| FR-016 ROI 设置 | 🔄 待设计场景 | `EmguALG/Roi/ImageRoi` + `ImageRoiTool` | ROI 通用工具（纯数据 + 裁剪/掩膜/坐标映射），算法按需加载；场景未定，暂不接算法（不标废弃，ADR-097） |

## 三、焊接控制（FR-017~FR-023）

| 需求 | 状态 | 现行对应 | 说明 |
|------|------|---------|------|
| FR-017 参数自适应调整 | ✅ 已实现 | [[api/WeldParamManager]] | 四算法 + Manager 唯一入口（ADR-015） |
| FR-018 参数调整公式 | ✅ 已实现 | [[api/WeldParamAdjustmentAlgorithm]] | 查表 + 宽度驱动公式 |
| FR-019 灵敏度控制 | ✅ 已实现 | `WeldAlgorithmsConfig` | 灵敏度阈值参数化 |
| FR-020 焊缝跟踪 | ✅ 已实现 | [[api/SeamTrackingAlgorithm]] / [[api/SeamMapTrackingAlgorithm]] | 双模式：PVT（备用）/ CSP 实时目标（默认，ADR-042/058） |
| FR-021 坐标转换 | ✅ 已实现 | `LineLaserCalibration` / 安装偏移 | 标定 + 示教锚定（ADR-042） |
| FR-022 失败检测与处理 | ✅ 已实现 | [[api/DeviceControlWork]] | 流程失败计数 + `Fail()`，时长判据（[[lessons/StepDrivenWorkflowPitfalls]]） |
| FR-023 手动调试模式 | ✅ 已实现 | [[architecture/DeviceControlArchitecture]] | 基类 `ManualStart`/`ManualStop`（非自起线程） |

## 四、工作流管理（FR-024~FR-028）

| 需求 | 状态 | 现行对应 | 说明 |
|------|------|---------|------|
| FR-024 10 态状态机 | ❌ 已删除 | [[architecture/DeviceControlArchitecture]] | 旧 10 态状态机删除；改为三态模型（`SubDeviceState`/`SubDeviceWeldStatus`/`MainDeviceStatus`，ADR-021） |
| FR-025 7 步骤工作流 | 🔄 重构实现 | [[api/DeviceStateApiCore]] | 改为 `RunStep` 布尔驱动步骤推进（无 `GoStep`，ADR-022） |
| FR-026 工作流启停 | ✅ 已实现 | [[api/DeviceControlWork]] | `StartMachine` / 通讯命令双入口 |
| FR-027 状态事件通知 | ✅ 已实现 | `StateChanged` / `StatusChanged` | 基类统一事件 |
| FR-028 异常中止处理 | ✅ 已实现 | `ErrorAborted` / `WeldStatus` | 三态模型错误态 |

## 五、通信管理（FR-029~FR-034）

| 需求 | 状态 | 现行对应 | 说明 |
|------|------|---------|------|
| FR-029 TCP/IP 通信 | ✅ 已实现 | `EthernetXmlComm` | 以太网 XML 重写（BytesIO + 预定义 XML，ADR-011） |
| FR-030 S7 PLC 通信 | ✅ 已实现 | `SiemensS7Comm` | S7NetPlus 封装 |
| FR-031 KUKA EKI/RSI | ✅ 已实现 | `KukaRsiComm` / `KukaEkiComm` | 门面并入 [[api/CommunicationManager]]（ADR-011） |
| FR-032 Profinet/GSDML | ❌ 未实现 | — | 需求书列出，代码已删除（KB `modules/Comm` 标注 Profinet/GSDML 已删除） |
| FR-033 全局数据中心 | 🔄 重构实现 | [[api/GlobalCommData]] / [[api/CommunicationManager]] | `SystemComm` + Manager 门面 |
| FR-034 通信配置管理 | ✅ 已实现 | 8 XML + INI | 持久化与旧路径迁移（ADR-011） |

## 六、数据管理（FR-035~FR-040）

| 需求 | 状态 | 现行对应 | 说明 |
|------|------|---------|------|
| FR-035 点云数据记录 | ✅ 已实现 | [[api/ProductFileRecordManager]] | `LineLaserContourRecord`（2026-09-20 由 SeamTrackRecord 更名收窄）→ `.ply` 点云 |
| FR-036 焊接动作记录 | ✅ 已实现 | `WeldParamControlRecord`（2026-09-20 由 WeldParamAdjustRecord 更名扩展：过程帧+调整动作） | ADR-008 双记录仍有效 |
| FR-037 异常恢复 | ✅ 已实现 | [[api/ProductFileRecordManager]] | 入队 O(1) + 后台落盘，异常可恢复 |
| FR-038 数据回放 | ✅ 已实现 | `DataReviewerPage` / `HelixRenderForm` | 历史点云/动作离线回放 |
| FR-039 日志管理 | ✅ 已实现 | [[modules/FileOperate]] | 分级 + 轮转 |
| FR-040 日志自动清理 | ✅ 已实现 | `Log` | 30 天清理 |

## 七、用户管理（FR-041~FR-044）

| 需求 | 状态 | 现行对应 | 说明 |
|------|------|---------|------|
| FR-041 登录认证 | ✅ 已实现 | `LoginForm` / `AuthHelper` | 密码加密（`AuthHelper` 继承 `DatabaseHelperBase`） |
| FR-042 三级权限管理 | ✅ 已实现 | [[modules/SQLiteDatabase]] | `level` 1/2/3 + UI 动态 |
| FR-043 用户管理界面 | ✅ 已实现 | `UserEditForm` | 增删改查 |
| FR-044 操作日志记录 | ⚠️ 部分实现 | `Log` | 关键操作有日志，但独立审计追溯体系待补 |

## 八、UI 界面（FR-045~FR-051）

| 需求 | 状态 | 现行对应 | 说明 |
|------|------|---------|------|
| FR-045 主页面 | 🔄 重构实现 | [[api/MainPage]] | ScottPlot 信号图 + 4 实时曲线 + 日志（AntdUI，ADR-008） |
| FR-046 参数界面 | 🔄 重构实现 | [[api/ProcessControlPage]] | `NavPage` ×2 承载工艺配置节点 |
| FR-047 图形界面 | 🔄 重构实现 | [[api/MainPage]] | 图像显示 + 算法调试（AntdUI 迁移） |
| FR-048 生产界面 | ✅ 已实现 | `DataReviewerPage` | 历史查询 + 回放 |
| FR-049 3D 点云显示 | ✅ 已实现 | `HelixRenderForm` / `PointCloudViewer` | HelixToolkit WPF 渲染 |
| FR-050 状态指示灯 | ✅ 已实现 | [[api/DeviceStatusWork]] | 三色灯 + 状态栏（AntdUI 状态标签） |
| FR-051 多语言支持 | ⬜ 未实现 | — | 需求书标"低"优先级，代码中无任何本地化支持 |

---

## 统计（2026-09-18 基线）

- ✅ 已实现：约 30 项
- 🔄 重构实现：约 11 项
- ⚠️ 部分实现：4 项（FR-007 / FR-044 / 振镜摆幅占位 / 距离分段）
- ❌ 已删除（被新机制替代）：8 项（FR-001/002/003/004/015/024/032 + 旧 10 态）
- ⬜ 未实现：2 项（FR-032 Profinet / FR-051 多语言）

> 待完成项明细与代码 TODO 行号见《实现待完成登记》（代码目录 `AdaWeldSystem/实现待完成登记.md`）及 `lessons/` 下相关门禁页。
