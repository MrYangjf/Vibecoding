---
title: "ADR-042 焊缝跟踪综合（物理场景 · 模拟环境 · 算法实现 · 实现路径 · 接入点；整合原 033/044~055/057/058/060/063~066）"
date: 2026-09-23
updated: 2026-10-08
tags: [ADR, 焊缝跟踪, CSP, 运动缓冲, 线激光, 闭环, 前置量, 速度前馈, WeldParamControl, MotionControl, merged]
status: accepted
evolved: 2026-10-08（新增 §5.5 振镜摆幅消费链路：CalcGalvoAmplitude 恒零占位已落地，业主裁定公式 宽度×(1+k)，k 默认 0.2，保留第 6 列查表覆盖）
merged_from: [ADR-033, ADR-044, ADR-045, ADR-046, ADR-047, ADR-048, ADR-049, ADR-050, ADR-051, ADR-052, ADR-053, ADR-054, ADR-055, ADR-057, ADR-058, ADR-060, ADR-063, ADR-064, ADR-065, ADR-066]
---

# ADR-042 焊缝跟踪综合（物理场景 · 模拟环境 · 算法实现 · 实现路径 · 接入点）

> 本页为焊缝跟踪主题的**唯一现行决策页**（2026-09-23 精简合并），收拢原 033/044/045/046/047/048/049/050/051/052/053/054/055/057/058/060/063/064/065/066 共 20 页（重排前编号，见 [[decisions/ADR-Index]] 删除对照表）的全部现行裁定。
> 「旧ADR-0XX」均指 **2026-09-23 重排前编号**。目标基准演进链（轴实际反馈 → 起焊锚点 → 标定轴值 → **测量时刻轴值 Ya1**）等过程性中间态压缩进「沿革」，逐轮实测取证细节看各旧页原档（tar.gz 备份）。

## 一、实际物理场景

### 1.1 机械结构（业主原述，权威）

- 焊接头 = **焊枪 + Y 轴 + 线激光**，整体挂在机器人上；机器人做 TCP（以焊枪为点）。
- 线激光固定在机器人工具 **X 前进方向 60mm** 处（`LeadDistanceMm = 60.0`）；焊接头 Y 轴与机器人 Y 轴**平行**。
- 两个事实：① **焊枪绝对 Y = 机器人 Y + 轴值**（+ 安装常数），二者并联合成；② **线激光偏差 d 是它自己坐标系内的量**——轴一动，焊缝相对激光坐标系反向移同样多，即 **d 里已"吃掉"轴的位移**。

### 1.2 标定对与目标链

- **标定对**：焊接前示教标定得到基准——轴回 Y 轴标定位 `TeachLockYMm`（PreWork 执行回归，容差 0.05mm），线激光读特征点 → `CalibratedCenterY`。二者构成一对，标定对成立是闭环可验证前提（起焊时偏差 >5mm 打 Warning 防呆）。
- **测量时刻**（机器人 X = RobotX）：激光测到 RobotXL = RobotX + 60 处偏差 d，此刻轴实际值 Ya1、机器人 Y 为 Yb1 ⇒ 该处轴侧绝对目标 `Yt = Ya1 + d`。
- **到达时刻**（RobotX 走到 RobotXL）：机器人 Y 为 Yb2 ⇒ 写入轴目标 `= Yt − RobotYGain × (Yb2 − Yb1)`（机器人 Y 增加使焊接头整体平移，跟踪轴**反向抵消**；Yb1 随地图点存储）。
 ⚠️ **2026-09-28 经 [[decisions/ADR-045-PredictiveRobotPoseSnapshot]] 演进**：Yb2 的取值由「写入时刻喂入原值（真实 RSI / 模拟节拍均为固定频率阶梯保持）」演进为「位姿预测器读取时刻外推值（锚点 + 相邻差分速度 × 时间差）」——位姿按固定频率喂入，阶梯值经本差分与查图中心逐拍进入闭环，业主在 SeamTraceY 数据上观测到 CSPinY 与实时Y 与喂入同频的周期性来回波动（真实与模拟同病，业主 2026-09-28 确认同修）；预测后写入时刻读取连续，波动源消除。Yt 公式结构与不变式不变（喂入时刻预测值==喂入值，Yb1/地图键语义不动）。
- **结构不变式（本主题核心判据）**：`Yt` 表达式内**不得出现可被自身执行改变的轴状态量**——d 的 −ΔYa 与 Ya1 的 +ΔYa 必须代数相消，否则闭环退化为正反馈积分器（实测后果：211 次方向反转、轴净位移 6.43mm 超行程）。**2026-09-23 补强与再裁定**：相消必须在「同帧配对的原始量」上完成，且**不得被任何后续滤波破坏**。低通对象取哪个都引误差 —— 滤偏差 d ⇒ `LPF(d)=d+τ·ḋ`、`ḋ=v_缝−ẏ_轴` ⇒ 入图值 = 真值 + **τ·(ẏ_轴 − v_缝)**，残余是**轴自身速度**的函数而轴速又由它驱动，环内重新出现可被自身执行改变的轴状态量（复刻仿真：拐点冲过头 0.226mm、裸结构命令反向 978/6000 拍）；滤合成目标 ⇒ 入图值 = 真值 − **τ·v_缝**，斜段恒滞后。故**地图值的时间域低通已彻底移除**：`Yt = Ya1 + d_raw`，`DyFilterAlpha` 参数与界面「dY低通系数」项一并删除（业主裁定「低通非必需，只要运动目的」）。抑噪由查图侧**零相位空间高斯**（σ=12mm、窗内约 300 点）与 ③/⑤/⑦ 三道突变闸门承担。

### 1.3 目标质量要求（业主口径）

1. **最终值不能突变**：正常序列中突然插入一次大偏差不可接受——合成后绝对目标帧间护栏 `MaxTargetStepMm`（默认 5.0mm，可调小），超限**拒绝该帧不入图**（不截断——截断造出现实中不存在的虚假目标）。
2. **最终值必须光滑、不能来来回回**：机器人示教沿工件方向连续，不可能出现 Y 向来回调动——方向锁 + 迟滞释放 + 输出死区 0.01mm（偏差 <0.05 不动的收窄落地）。
3. **焊接精度 0.1mm**；1.5m 全程机器人不停车，轴做**缓存的 CSP 连续运动**。
4. 全流程：a. 焊接头就位（Y 轴回标定位、线激光打开）→ b. 预焊点（线激光反馈、轴快速到位）→ c. 连续焊接（CSP 连续运动）。
5. X 方向：理论上不回退；**通讯抖动造成的回退须消除**（死区 `ReverseDeadbandMm = 0.1mm` 吞掉），**真回退须报警**（`ReverseAlarmMm = 1.0mm`，偶发仅警告一次 / 连发报警停机——用户裁定不复焊）。

## 二、模拟测试环境

### 2.1 与真实链路同构（同一扇门）

- 模拟调度器 `SimScheduleTick` 与真实 `IoSubPrework → IoSubWork` **同构**，步号 **10/20/21/22/30**（大步 10/20/30、小步 +1）：10 等线激光进 PreWork → 20 等 PreWork 完成反馈 → 21 焊接启动门控（与真实 `DoSubWork` **同一扇门** `IsSubWorkGateOpen`）→ 22 `DoSubPrework()`（焊前预置播种，预焊接点）→ 30 焊接中等待（行程到程由 `CheckWeldProgress` 收口）。
- 模拟不再跳过回位等待；焊接启动门控见 §5.2。

### 2.2 模拟保真度边界（⚠️ 已知，非缺陷）

- 虚拟相机**不随虚拟轴位移改变特征**（无「轴动 → 激光坐标反向偏移」的物理耦合），而 `CalibratedCenterY` 默认 5.0 ⇒ 模拟中结构不变式的相消前提不成立，目标会单向漂移至行程限幅——**模拟不能用于验证闭环自激**（[[lessons/SimulationAutoBranching]] 陷阱十九）。需把 `CalibratedCenterY` 设 0 或让虚拟相机把缝特征放在标定中心。
- **未装直线轴**时线激光不随轴动 ⇒ `filteredDy` 恒常量 ⇒ 目标退化为轴自身轨迹的延迟副本再减常量 ⇒ 恒速饱和冲刺（非跟踪）。复测前不宜据该工况数据调 `AxisMmPerLaserMm` / `CalibratedCenterY`。
- 模拟 robotX 由模拟线程 50Hz 喂入、记录按 100Hz 逐拍采样 ⇒ 焊缝 Y 记录 CSV 成对同 X 属**节拍差**，逐拍不去重不改（ADR-063 附带裁定；记录现为 `SeamTraceYRecord` 5 列）。

### 2.3 模拟启停与跨会话残留（ADR-050/052 收口）

- **对称复位**：停止侧 `DisableSimulation` 复位运控（`_motion.Stop()` + `ClearSeamAlarm()`）与焊接头；启动侧 `StartSimulation` 开头兜底对称清（`ErrorAborted` 时 `ResetProcess()`）。判据：**同一状态位的置位与清除必须成对出现在启/停两个入口**。
- `SeamMapTrackingAlgorithm.Reset()` 清 `_hasAlarm`；新会话喂入新起点前 `ResetSeamTracking()` + 位姿重置（防上一会话终点 X 触发「折返 1704mm」误报）。
- `StartCrdBuffer()` 遇残留坐标系失败（4627）先 `BufferStop` 再重试一次。⚠️ **2026-09-25 校正**：`BufferStop` 须传 **Mode 1（平滑停止）**——手册 9.7.16 明确它**已「清除 FIFO 並解除座標系」**，故无须再单独 `BufferClear`；旧版传 `Mode 0` 实为 **Feedhold 暂停**（什么都没清）⇒ 再清必被拒、坐标系残留 ⇒ 下一场单轴点位运动冲突。见 [[decisions/ADR-044-SeamEndSemanticsAndMotionAxisScope]] §2026-09-25 补正。
- 起焊沿复位分层见 §5.3（`ResetTrackingForWeldStart` 只清跟踪，工艺调整清零移至会话边界）。

### 2.4 取证工具链

| 工具 | 内容 |
|---|---|
| 焊缝 Y 记录 CSV | **5 列** `当前RobotX,入图RobotCSPX,CSPinYt,CSPoutY,实时Y`，**逐拍记录且不去重**（2026-09-24 取代原 4 列轨迹 CSV；由 `ProductFileRecordManager` 独占持有，与 .ply/.pDat 同会话子文件夹同基名，DB 按基名定位）。判读：入图线 vs 出图线之差 = 跟随误差 |
| ~~CspChain 数据链~~ | ⛔ **2026-09-24 业主令整体删除**（业主看不懂、不作查找依据）。需要段级取证时可从 git 历史恢复；现行业主验收只用焊缝 Y 记录 CSV 的「入图 vs 出图 vs 轴反馈」三路 Y |
| 调试行 | 「调试闭环」（标定中心/特征Y/特征修正/机器人项/总修正/地图点数/分源拒绝计数/机器人X）与「调试运控」（轴反馈/目标/命令/脉冲/段距/写段/运行/空闲拍/队列段/累计段/占空比/前馈/段时基/几何段速/段速/生效配置整行自证），Debug 级 500ms 限频 |
| 通用教训 | 热路径失败必须计数收敛不得静默重试；会话收口必须锁内幂等；行程限幅不得静默（截幅 >1mm 限频告警指向核查项）；「生效配置整行自证」——现场 INI 会覆盖代码默认值，不起焊首条日志打印生效值就无法判定改动是否生效 |

### 2.5 B1 核查结论（2026-09-28）：MIN_VEL 与缓冲段速无耦合

- 配置 `DeltaMotionConfig.xml` Y 轴 `MIN_VEL=1`（mm/s）解析为 `StrVel` → `axis.MinVel`，**只作 `AbsMove` / `AbsMoveNoBlock` / `JogMove` 的起始速度实参**（回标定位 / 点动链路）；`BufferLineTo` → `CSP_Start_MotionBuffer_Line_MultiAxis2` 的段速由 `QueueCspSegment` 几何折算显式传入（钳位带 [0.85,1.0]×几何速度、下限保底 `AxisEquivMm`），与 `MinVel` **零耦合** ⇒ 第二轮诊断 B1 的「把 Y 轴 MIN_VEL 降到 ≤0.02」分支在软件侧不成立，**不改配置**（降它不治跟踪锯齿、只拖慢点位起步）。
- 剩余唯一疑点 = 驱动器固件是否对缓冲段施加最小执行速度。取证手段：`调试运控` 行新增 **段时基 / 几何段速 / 段速** 三字段（`_cspLastSegSeconds` / `_cspLastGeomVelMmPerS` / `_cspLastSegVelMmPerS`，此前只写不读），与焊缝 Y 记录 CSV 的 `实时Y` 按段对齐算「段内轴实际速度 ÷ 写入段速」：比值远大于 1 ⇒ 固件抬速执行（每段独立启停坐实）；接近 1 仍有锯齿 ⇒ 亚脉冲插补量化。**两条均归周期写段（B2/B3）处置**，A1 起步 Ramp-In 待 B2 后按剩余幅度决定。

### 2.6 队列积压反馈（2026-09-29）：消除「实时轴落后 CSP 命令」的滞后

- **现象与定量**：`gap = CSPoutY − 实时Y` 中 **99% 是队列积压**（末段写入端点 − 轴反馈），「待写」项仅 0.004mm；且积压**随行程单调增长**（212343：0.349→0.494→0.597→0.667mm；212159：0.065→0.131mm）。每段「轴位移 ÷ 段距」中位数已是 **1.000**、均值 1.01~1.04 ⇒ **轴并非跟不上，而是队列只增不减**：上带 `sv≤gv` 使任何执行亏空（起步大步阶、脉冲截断残差、驱动器最小执行粒度，实测约 1% 亏空）**永久残留**（原代码注释已自陈该风险）。
- **改法**：几何钳位之后叠加 **积压比例反馈**——`段速 += clamp((积压 − 死区) × 增益, 0, 上限)`，积压按运动方向取号（`_cspLastQueuedPos − 轴反馈`）。参数：`CspBacklogVelGainPerS = 0.5`、`CspBacklogVelCapMmPerS = 0.5`、`CspBacklogDeadbandMm = 0.02`。
- **自限性（与旧失败模式的本质区别）**：增量随积压趋近死区而趋 0 ⇒ 自动退回 `sv≤gv` 的断供安全行为，**只有确实有余量可排时才提速**；⛔ 区别于「上带 1.5 恒定提速 ⇒ FIFO 抽空 ⇒ 段末冲过端点被位置环拉回」的历史回退。
- **不变量保持**：只改**写入段速**，**不碰**算法目标 `Yt`、不碰跟随器 `_cspFollowPos` ⇒ 不违反「闭环 = 绝对目标 `Yt = Ya1 + dY`，`Yt` 内不得出现可被自身执行改变的轴状态量」与「地图值禁时间域低通」。
- **预期与验收**：亏空 0.002~0.007mm/s ÷ 增益 0.5 ⇒ 稳态积压收敛到死区量级（**≤0.02mm**，原 0.13~0.67mm）；起步 1.28mm 步阶按 0.5mm/s 增量约 2~3s 排空。验收看「调试运控」新增 **积压 / 提速** 两字段：提速 >0 且积压收敛即为生效；若积压收敛而轴出现回退（负步占比上升）⇒ 增益/上限过大，先降 `CspBacklogVelCapMmPerS`。
- **未覆盖**：起步波浪（Q1）的过冲仍待 A1 起步 Ramp-In；小偏差锯齿（Q2）仍待 B2/B3 周期写段。本项不替代二者。

### 2.7 写段双门限（2026-09-29，B3）：消除低速「冲一下—停住」的停走

- **业主环境口径（2026-09-29 澄清，推翻此前的「模拟自激」定性）**：线激光**是否随轴安装**的唯一区别是——装在轴上 ⇒ 轴修复偏差、激光输出的偏差逐步减小至无需移动；未装在轴上 ⇒ **轴再怎么动偏差都在、轴一直追赶**。当前测试环境属后者，**「轴持续追赶恒定偏差」是预期行为，不是缺陷**（⛔ 因此不得以「消除漂移」为目的改目标基准，那会把被测现象本身抹掉）。
- **真实现象**：偏差恒定 ⇒ 轴应**持续、平顺**追赶；实测却是「快速拉升 → 走平 → 过一会又拉升」（212343：起步 0.86mm/s → 中段 0.25mm/s → 再 0.64mm/s）。
- **停走源之一（本项修复）**：写段由**距离门限单条件**触发 ⇒ 过程越慢间隔越长（小偏差实测约 356ms 才写一段）；间隔一旦超过时基上限 `CspSegSecondsCap=0.25s`，段速被高估约 42% ⇒ 驱动器提前跑完本段、干等下一段 ⇒ 轴停走。
- **改法**：判据改 **距离门限 OR 时间到点**（`CspWriteIntervalMaxSeconds = 0.15s`，且须已攒够 **1 个整脉冲**，防零位移段塞满缓冲）。间隔恒 ≤0.15s &lt; 0.25s ⇒ 时基不再被截断 ⇒ 段速回到真实几何速度 ⇒ 连续追赶。**只影响低速工况**（高速时距离门限先到，节拍不变）。
- **停走源之二（2026-09-29 同轮已修）**：入图空洞（212343 在键 130.65→151.97 之间 21mm 无新点）⇒ 高斯窗只剩旧值 ⇒ 目标冻结。根因是**入图键用了 RSI 固定频率喂入的原值（阶梯）**，而查图用外推值 ⇒ 两列不同源。按 [[decisions/ADR-045-PredictiveRobotPoseSnapshot|ADR-045（预测性机器人位姿快照）]] §6 补正：入图键改由 `UpdatePredictedRobotX(CurrentRobotX)` 刷为**预测值**，写入与读出同源（原「喂入原值」原则只约束 Y，不得套用于 X）。

### 2.8 缓冲 S 曲线时间常量化（2026-09-29，起焊过冲取证）——⚠️ 当日实测无效已回退

- **取证（Desktop.zip 六场 0929 模拟数据 + 运行日志）**：命令链 CSPoutY 六场全程 **0 次下降**（单调锁/死区/跟随器可证无责）；小偏差场（0.18mm）轴反馈回撤 85~93 次/场（中位 0.021mm），微观形态 = 突进 +7~13μm/拍 → **越过全部已缓冲段端点最高 26μm** → 指数回落 −1~3μm/拍；大偏差场（0.78/−2.32mm）仅 2~6 次、平顺。运行配置实际 `S_TIME=0`（无 S 曲线平滑），假设微段阶跃直接作用驱动器位置环为诱因。
- **小偏差才锯齿的机理**：小偏差 ⇒ 稳态斜率低（固定斜率 = 偏差/(τ+δ)，六场反解 δ≈0.9~1.1s 全吻合）⇒ 段流稀疏、停走交替 + 积压提速突进 ⇒ 过冲回落的执行侧极限环；大偏差段流连续，无停走。
- ~~**裁定（业主 2026-09-29）**：缓冲 S 曲线时间改为**代码常量固定 10ms**（`DeltaMontionAxis.BufferSCurveTimeSeconds = 0.01`），`StartCrdBuffer` 建系时不再读轴配置 `STime`~~。
- ⛔ **已回退（业主 2026-09-29 实测裁定）**：S 曲线常量 10ms 落地后 A/B 复测，起焊段与 `S_TIME=0` **效果基本一致**——**过冲/锯齿并非 S 曲线时间所致**，上述「微段阶跃直达位置环」假设不成立或非主因。代码已回退为 `StartCrdBuffer` 读轴配置 `STime`（配置文件 S_TIME 键重新生效）；建系成功日志的生效值自证保留。下一步排查方向：段流稀疏下的停走-突进极限环本身（写段匀速化/积压提速收敛，原方案 B/C）。
- **保留有效结论**：命令链单调无责、CSPinY 持平为测量语义、固定斜率定律 = 偏差/(τ+δ)——均经本轮复测再确认。

## 三、算法实现（SeamMapTrackingAlgorithm）

- 非单例，继承 `WeldAlgorithmBase`；**只计算**——不产 PVT 点、不持运动契约、不写控制器、不落盘（算法纯净性红线：禁 `RunRecordManager` / `System.IO` 等任何记录持久化符号）。
- 输入「线激光结果 + 机器人位姿 + 测量时刻轴值」，输出「按机器人 X 键的绝对目标地图 + 查询口 + 速度前馈口」。

### 3.1 帧处理 8 步（ProcessLaserResult）

| 步 | 处理 | 关键参数 |
|---|---|---|
| ① 特征偏差换算 | `d_raw = (featureY − CalibratedCenterY) × AxisMmPerLaserMm × GuideSign` | 标定中心/比例/方向 |
| ② 首帧种子闸门 | 首帧原始偏差超物理可能范围即判识别失败，不入图不建种子 | `MaxSeedDeviationMm = 10.0` |
| ③ 时间域突变剔除 | 单帧偏差跳变超限拒绝 + 连续拒绝达上限判**真实台阶**放行重置种子 | `MaxStepChangeMm = 0.5`；`ConsecutiveRejectFrames = 20` |
| ④ 合成绝对目标（**不做任何时间域低通**） | `Yt = Ya1 + d_raw`（Ya1 = 本帧测量时刻轴实际值，相机回调线程取）；相消必须在**同帧配对的原始量**上完成 | 结构不变式见 §1.2 |
| ⑤ 最终目标突变护栏 | 与上次接受 Yt 差超限拒绝不入图；连续拒绝放行 | `MaxTargetStepMm = 5.0`（可调小） |
| ⑥ 取查图键 | `arriveX = _monotonicRobotX + LeadDistanceMm`（= RobotXL，前置量入键） | — |
| ⑦ 空间域野值剔除 | **切向连续性**：地图尾部两点切线外推到 arriveX，偏离 > `0.2 + OutlierSlopeLimitMmPerMm × gap` 才判炸——**连续曲线（弧/直线/S 形）永不误杀**，只拦孤立飞点；3σ 统计判据保留互补；补真实台阶放行护栏 | 地板 0.2mm；切向系数 0.15（键值不变语义换轨） |
| ⑧ 存图 | `SeamMapPoint(RobotX = arriveX, TargetY = Yt, RobotY = Yb1)` 按 X 升序，容量 2000 | 前置量入键 |

### 3.2 方向平滑与死区（作用于查询后的绝对目标序列）

- **方向锁 + 迟滞释放**（`ApplyMonotonic`）：锁向取极值后仅当反向偏离超 `MonotonicReleaseMm = 0.30` 才判真实反弯解锁重新种子；`MonotonicDeadbandMm = 0.05` 判定死区；`MonotonicWindowMm = 200` 为持距兜底上限（防一次错误锁向绑架整条焊缝）。噪声无法制造往复，真实 S 形仍能跟随。开关 `EnableMonotonicConstraint`。
- **输出死区**：`OutputDeadbandMm` 默认 **0.01**，加载期上界 0.02（现场 INI 存旧值 0.05 时兜住——只改默认值不会生效，R3 教训）。抑噪职责由**零相位空间高斯**（σ=12mm）+ 3σ/切向判据 + 方向锁承担（**地图值时间域低通已于 2026-09-23 整项移除**）。

### 3.3 查询口与速度前馈口

- `TryGetTargetY(robotX, robotY, out targetY)`：对称高斯窗 `[robotX − GaussianHalfWindowMm, robotX + GaussianHalfWindowMm]`（±30，σ=12）零相位平滑查询；`CorrectionMm`（目标 − 标定轴值）仅诊断。
- `TryGetRequiredAxisVelocityMmPerS(robotVxMmPerS, out required)`：需求 = |地图局部斜率 × vX|；斜率取尾部 ≥`FeedforwardSlopeRefGapMm`(2mm) 基线割线 + EMA(0.2)，钳 ±5mm/mm。运控侧 `FeedforwardSafetyFactor`（默认 3.0，护栏 [1,10]）放大后作速度下限。**前馈只抬上限、不产生位移**——位移仍由位置闭环产生，需求失真仅使上限高估或回落既有行为，无新增失效模式。

### 3.4 分源观测

`TimeRejectCount` / `SpaceRejectCount` / `TargetStepRejectCount` / `JitterRejectCount` 四路独立计数，现场可区分「偶发野值」「识别失效」「死区不当」。

## 四、当前算法实现路径（数据源来路 → 计算 → 入图 → 出图）

### 4.1 数据源来路

| 源 | 通路 |
|---|---|
| 线激光 | 实例唯一持有者 = `LineLaserManager`；帧结果经 `WeldParamManager.OnSeamLaserResult(result, axisPosMm)` 入算法（axisPosMm = 测量时刻轴值 Ya1，PVT 路径传实轴 / CSP 无轴模拟传虚拟轴 `_simAxisPos`） |
| 机器人位姿 | **单一真相源在通讯层**：`CommunicationManager.RsiComm_DataReceived` 开头落加锁只读快照 `RobotPoseSnapshot`（X/Y/Z/Timestamp），经 `TryGetRobotPose` 暴露；`WeldParamManager` 订阅仅转发，⛔ 不另存副本 |
| 轴值 | 相机回调线程 `_seamAxis.GetPosition()`（`SeamAxisPosMm` 判断辅助属性集中取数；无轴模拟以 `_simAxisPos` 顶替） |

### 4.2 计算 → 入图

位姿帧：Y 滤波 → X 单调化（抖动吞掉不推进键、真回退不倒退键只累计 dx 交折返监测）→ 路径距离 → 折返监测。激光帧：§3.1 八步 → 地图（键 = arriveX = 单调 X + Lead）。

### 4.3 出图（CSP 运动缓冲流式，607A 逐拍改目标已实测废止）

`OutputCspTick()` 落 `FlowProcess` CSP 分支逐拍（10ms / 100Hz 基线，`SubDeviceWork` 驱动；**禁自起线程、case 体内禁 Sleep/轮询**）：

1. **查询**：当拍 robotX/robotY → `TryGetTargetY`；写入时刻机器人 Y 差分反向抵消（§1.2）；未命中（起焊前 60mm 前置段）回落 `TeachLockYMm`，天然不跳变。
2. **整形**：**一阶跟随**（τ=150ms 私有常量；**残差必须取「跟随器位置 `_cspFollowPos` → 目标」**——取「本拍输出 → 目标」会在限幅不生效时恒 0 自锁）→ 速度限幅 `max(MaxVelMmPerS, 前馈下限)` → 加速度限幅 `max(MaxAccMmPerS2, 前馈下限/τ)`。`_cspFollowPos` 与末段写入位置 `_cspLastQueuedPos` **解耦**；位置贴齐与按剩余距离限速两种旧整形已废除。
3. **段距门限**：`max(CspMinWriteSegMm = 0.01mm, 单脉冲半值)`——未写段拍距离照常累计（`_cspLastQueuedPos` 不推进），到门限一次性写入，几何速度不失真。低于 1 脉冲即零位移段会塞满驱动器缓冲，是脉冲域唯一硬门限。
4. **段速度**：时基 = **自上次写段的实测间隔**（cap `CspSegSecondsCap = 0.25s`；单拍折算会高估段速致停走）→ 平滑 = **加速度限幅跟随**（`velStep = MaxAcc × segSeconds`，长期零偏）→ **几何一致性钳位 `[0.85, 1.0] × |segMm|/segSeconds`**（~~上带 1.0 = 段速永不高过几何速度 ⇒ FIFO 永不断供，回退根除~~ ⚠️ **2026-09-29 演进**：上带 1.0 只保证「不断供」，却把任何执行亏空**永久固化为滞后**——实测实时轴落后 CSP 命令 0.13~0.67mm 且随行程单调增长，见 §2.6 ⇒ 几何带之后**再叠积压反馈增量**）→ `MaxVel` 上限 → 1 脉冲/秒保底。钳位顺序：跟随 → 几何带 → **积压反馈** → MaxVel → 保底。
5. **写入**：`BufferLineTo`（绝对模式，`ToPulse = (int)(v/Equiv)` 截断，`Equiv = 0.001`，绝对模式量化误差不累积）→ 起焊沿 `StartCrdBuffer` 建坐标系（SetOriginFlag=0，段目标=轴坐标系绝对坐标）→ 预载 **3 段** 后 `MotionBuffer_Start`；**以写代查**（余量/块数两查询实测不反映队列深度，废弃）→ 静止达 60 拍推断耗干 → 恢复写 1 段即重 Start 不重建坐标系。
6. **执行可观测**：`DetectCspExecutionStall`——连续 30 拍已写段而轴反馈位移 < 0.5μm 即判驱动已停、重建执行（`_cspBufferRunning` 只是「软件以为在跑」的自推断位，必须以轴反馈兜底）；触发时限频取 `ReadSlaveStatus` / `BufferMotionStatus` 原值。
7. **逐拍记录**：每拍无条件 `RecordCspPoint(command, axisNow)`；写段占空比观测（远低于 100% 即写段判据在砍节拍）。
8. **热路径失败收敛**：`BufferStart` 失败计数上限 3，达上限停该热路径并置 `_seamAlarmPending` 报警（由流程线程 `Fail()` 收尾，跨线程不直接推进执行步）。

### 4.4 会话边界与护栏

- **起焊沿**：`StartCspOutput()` 首行若 `_cspOutputRunning` 为真先 `StopCspOutput()`（不得以残留运行态早退）；顺序 = `ResetTrackingForWeldStart` → `BeginSeamTrackingCorrection` → 速度归零 → `StartCspOutput`。
- **停焊沿**：`WeldStatusTrans()` 的 `Stopping` / `ManualStopped` / `ErrorAborted` 分支必须调 `StopSeamTrackingOutput()`（= `StopCspOutput` + `FlushSeamBuffer(true)` + 复位标志）——**不依赖步机恰好走到**；收尾幂等；`BufferClear` 返回码透传，收尾失败连续 3 场升级 Warning。
- **急停双保险**：① 编排层非 Running 不调 `FlowProcess`；② tick 内 `IsEmergencyStop()` 置位即收口。**报警拍不写目标**（`_seamAlarmPending` volatile 置位、Fail 只在流程线程）。
- 行程限幅 `ClampToStroke(YAxisMinMm/YAxisMaxMm)` 是幅值唯一物理边界（`MaxCorrectionMm`/`ClampCorrection` 已删）；截幅超 1mm 限频告警。

### 4.5 算法配置（WeldAlgorithmsConfig，现行 43 项）

- 单类单文件 Manager 独占：`SEAM_GUIDE` 几何 **13**（`DY_FILTER_ALPHA` 于 2026-09-23 移除、`INSTALL_OFFSET_Y_MM` 于 2026-09-24 经业主令删除）+ INI 阈值 23 + `LASER_CALIBRATION` 7。算法只读消费（私有 `_config` + `LoadConfig(object)` 转型）；外部禁 new / 持有 / 回灌，只经 `Manager.AlgorithmsConfig` 只读访问；读写路径 `Config\WeldParamControl\Algorithm_INI\`（ADR-033 范式）。
- 跟踪几何/标定关键项：`AxisMmPerLaserMm` / `GuideSign` / `LeadDistanceMm`(60，兼地图键前置平移量) / `RobotYGain`(1.0，写入时刻差分反向抵消) / `TeachLockYMm`（Y 轴标定点 = 起焊种子 / 未就绪回退）/ `CalibratedCenterY` / `YAxisMinMm`/`YAxisMaxMm` / `MaxMapPoints`(2000) / `TrackingMode`。
- 标定记录项 3 项（`CalibratedCenterZ` 正名 / `LaserToHorizontalAngleDeg` / ~~`InstallOffsetY` 2026-09-24 业主令删除~~ / ~~`ApproachThreshold` 已根除~~）：**零消费 ≠ 无价值**——现场标定作业记录项，删任何业主可见参数前必须问业主。⚠️ `InstallOffsetY` 删除合规性：业主即本规则立规人、明示令删；该参数自ADR-042 起 0 消费，且 **Load 读 `SEAM_GUIDE` 段 / Save 写 `LASER_CALIBRATION` 段读写错位**（存了也读不回，双重失效），恢复可查本页与 log 历史。
- UI：线激光标定页 `tbpanelweldponts` 6 列×10 行（2026-09-24 删「安装偏移Y」整行 11→10；标定 5 项 + 跟踪几何 8 项），轨迹点控制页 `tbPanelAlogControl` 4 列 × **31 行**（阈值四组 **18 项**；2026-09-23 删 dY低通项后行号整体 −1）；**Designer 脚本化改写铁律**：TLP 内 `Dock=Fill` 的 Label 必须写 `AutoSize=false`（默认 true 与 Dock 冲突 = 吞行来源），新增控件四件套校验含 `= new` 行，覆盖率 100%。

## 五、算法接入点（内部流程如何调用消费）

### 5.1 唯一入口 WeldParamManager（单例）

外部禁直接访问算法实现 / 绕过 Manager 订阅事件。跟踪相关 API：`OnSeamLaserResult` / `TryGetSeamTrackingTargetY` / `TryGetSeamTrackingRequiredVelocityMmPerS` / `ResetSeamTracking(reason)` / `ResetTrackingForWeldStart` / `ClearSeamTrackingAlarm` / 各分源计数与诊断属性透传。

### 5.2 焊接启动链与门控（ADR-041/042 常驻范式）

- 运控 PreWork 步序：`StepServoOn = 10` → `StepReturnToCal = 11/12`（`AbsMoveNoBlock(TeachLockYMm)` 下发即返回 + 按拍到位判定，容差 0.05mm 超时 15s；已在位跳过）→ `StepReady = 20`。**线激光侧 PreWork 不写入任何值**，只检测稳定反馈。
- **焊接启动门控（受理制）**：`DoSubWork` 入口 `IsSubWorkGateOpen`——仅「运控处于 PreWork 且 `!IsCalibrationYReady`」时关门：置 `_subWorkPending` 挂起、不级联 Working；5 条子设备线程每拍轮询（锁内幂等仅首个命中线程补执行），`IsCalibrationYReady` 变 true 后补执行；运控 ErrorAborted 弃单报错；等待 2s 限频告警。**运控未启动或已就绪 → 放行**，历史行为不变。停止/急停/清状态链清挂起标志。
- 命令前置条件 `IsCommandPreconditionMet`；等待 = 按拍轮询变量 false→true，**绝非线程等待**。

### 5.3 起焊沿 / 逐拍 / 停焊沿（消费时序）

| 时点 | 动作 |
|---|---|
| 会话边界（点击模拟 / 焊前检查 DoSubPrework） | `ResetSeamTracking` 全清（跟踪 + 工艺调整）——窗口外清零 |
| 起焊沿（OnSeamTrackingStart） | `ResetTrackingForWeldStart` **只清 PVT + 焊缝地图**（工艺调整不清——管控窗口起点 = 播种后，窗口内任何路径不得清工艺调整）→ `BeginSeamTrackingCorrection`（修正量置 0 天然零跳变）→ `StartCspOutput` |
| 焊接中每拍（10ms） | `SubDeviceWork` → `FlowProcess` → `OutputCspTick`：查询 → 整形 → 写段 → 逐拍记录 |
| 停焊沿（焊接态出口） | `StopSeamTrackingOutput` 收尾幂等（§4.4） |

### 5.4 PVT 备用路径（保留但不验证）

- `SeamTrackingAlgorithm`（PVT 流式段）整链保留可一键回退；**PVT 模式临时禁切**——面板已删「焊缝跟踪模式」下拉，加载期强制 `TrackingMode = CspRealtime`（防误切，PVT 未验证）；PVT 参数 7 项退出界面但代码消费保留，PVT 回退路径部分语义未同步本页现行口径（前置量 / Ya1 基准），启用前须先同步。

### 5.5 振镜摆幅消费链路（2026-10-08 落地，取代原「无消费方」）

**原状**：`CalcGalvoAmplitude` 是 `return 0.0` 恒零占位，`SetGalvoParams` 全项目只在初始化调一次 ⇒ **运行期无调用链，界面改参数不生效**。

**现行链路**：

```
线激光焊缝宽度
 → CalcGalvoAmplitude(seamWidth) ← 查表优先 / 公式兜底
 → WeldParamOutput.GalvoAmplitude
 → WeldParamControlWorkflow.LastOutput
 → LaserWeldHeadWorkflow.ApplyGalvoAmplitude（StepGalvo 步）
 → WeldHead.SetGalvoParams
 → WSX RxPDO 0x7010
```

**摆幅计算规则**（业主 2026-10-08 裁定）：

```
摆幅宽度 = 焊缝识别宽度 × (1 + k) k = WEAVE_AMPLITUDE_K（可配置，默认 0.2）
```

**⚠️ 红线归属澄清（2026-10-08 审计）**：该红线原文出自 `api/WeldParamControlWorkflow.md`（并见 `architecture/DeviceControlArchitecture.md`），⛔ **ADR-043 正文并无「自创公式」条款**（其红线只有「算法纯净性」与「模拟不下发真实机器人」两条）——原写「与 ADR-043 红线的关系」属**悬空引用**，现改指真实出处。红线禁的是禁的是「**AI 自行发明**未经验证的公式」，并点名反面例 `(SeamWidth - LaserDiameter)/2`。本条是**业主裁定的业务规则**，不属「自行发明」，故可执行 —— 但**必须保留查表覆盖口子**：`AutoParamHelper` 第 6 列「振镜摆幅」若有该接头的实测值则**优先查表**，无记录才用公式兜底。理由：公式本质是**直焊缝的几何关系**（摆幅横向摆动 ⊥ 焊缝识别宽度为横向尺寸），角焊缝与复杂接头必须靠标定覆盖。

**双支路同源**：`FillOutput`（主支路）与 `FillXlOutput`（XL 缓存支路）**都必须调 `CalcGalvoAmplitude`**。此前 `FillXlOutput` 硬编码 `GalvoAmplitude = 0.0`，会造成两条下发路径摆幅不一致 —— 已修。

**门控**：`EnableGalvoWeave`（`ENABLE_GALVO_WEAVE`，默认 false）关闭时下发摆幅 0 + 振镜不使能，而非保持上次摆幅。

**⛔ 摆幅不参与 Y 向引导闭环**，禁引入时间域低通（同 ADR-043 自激/恒滞后机理）。

**第二个消费方（尚未落地）**：`DeviceControlWork.ApplySpotAlignCompensation` —— 光丝对中偏差驱动振镜 `XCenter/YCenter` 微调（todo）。⚠️ 该链路与摆动参数**都改中心偏移**，两者必须各自单一写入口，否则互相覆盖。

## 沿革（演进链摘要，细节见旧页原档）

- **ADR-042**（09-16）：PVT → CSP 换轨、双模式、位姿单一真相源、步骤驱动 `OutputCspTick`、示教锚定标定模型（`TeachLockYMm` 基准，后被废）、零相位高斯平滑与野值双判据。
- **ADR-042**（09-21）：607A 逐拍改目标实测不生效 → **运动缓冲流式段写入**；首跑钉死 SetOriginFlag=0、二跑钉死「以写代查」、静止补记。
- **ADR-042**（09-21）：路径 Y 相对增量跟随（机器人 Y 以 `ROBOT_Y_GAIN` 系数回归）；水位方案被「以写代查」取代。
- **ADR-042 → 047 → 048 → 049**（09-21~22）：目标基准四次换轨（轴实际反馈 → 起焊锚点 → 标定轴值 → **测量时刻轴值 Ya1**）——前三种基准在特定条件下均为正反馈积分器（实测 211 次方向反转 / 净位移 6.43mm）；沿途落地：方向锁迟滞释放、突变三重护栏、段距配置化、PVT 参数退场、UI 分离、前置量入键、对称查图窗、写入时刻机器人 Y 差分、X 单调化、`MaxTargetStepMm` 护栏、脉冲域量化。
- **ADR-042**（09-22）：零消费残骸清理（后被 055 部分撤销）+ 几何归位标定页 + 二次模拟跨会话残留清警四处根因。
- **ADR-042 / 052**（09-22）：热路径失败收敛 / 会话收口幂等 / 行程限幅告警 + 会话边界对称收敛 / 缓冲执行失步以轴反馈可观测（0.9s 轴冻结取证）。
- **ADR-042 → 054**（09-22）：段速度时基 = 自上次写段实测间隔（停走根因之一）+ 一阶跟随整形取代自锁式减速限幅 + 写段门限硬编单脉冲 + 死区 0.01/上界 0.02 + 耗干 60 拍 + 逐拍不去重 + 生效配置整行自证。
- **ADR-042**（09-23）：恢复误删标定记录项 + `CalibratedCenterZ` 正名 + 6×10 布局 + AutoSize=false 铁律。
- **ADR-042 / 058**（09-23）：空间野值切向连续性判据（连续曲线永不误杀，验收 RMS 3.22→0.77mm）+ Y 轴速度前馈口（v=5 RMS 3.79→0.79）。
- **ADR-042 → 064 → 065 → 066**（09-23）：段速度跨段连续化（EMA → 几何钳位 [0.6,1.5] → 收紧 [0.85,1.0] + 加速度限幅跟随 + 时基 cap 0.25s）逐轮根除轴回退 → CspChain 数据链软件无罪证明 → 段距门限 0.01mm（微段 ≪ S 曲线时间极限环）+ 预载 3 段 + CmdPosMm 终判列 + S_TIME 勘误（现场实际 0，台达建议 10ms）。
- **ADR-042**（09-23）：焊接启动门控 `IsCalibrationYReady` 消费落地 + 模拟调度器同构 + 轨迹成对同 X 节拍差裁定。
- **ADR-042**（11-16）：缺值量测改用**距离尺**——激光有效帧清零、位姿有效累计 `|ΔX|`、位姿停滞（>2×RSI 周期）按 `v_weld×Δt` 推定（钳位 100mm/s），只观测不动作；CSP 查图 X 改取 `WeldParamManager.CurrentRobotX` 与入图键同源（D21 修复，保留回退开关）；`NO_VALUE_TOLERANCE_MM` 默认 5.0 / 载入钳位 1~50mm。

## 背景

（待补：本决策要解决什么问题）

## 决策

1. （待补）

## 备选方案

- （待补：考虑过什么、为什么放弃）

## 后果

### 正面
- （待补）

### 负面
- （待补）

## 相关页面

- 模块：[[modules/WeldParamControl]] · [[modules/MotionControl]] · [[modules/Comm]] · [[modules/LineLaserCam]] · [[modules/UIDesign]]
- API：[[api/SeamMapTrackingAlgorithm]] · [[api/SeamTrackingAlgorithm]] · [[api/WeldParamManager]] · [[api/MotionControlWorkflow]] · [[api/LineLaserWorkflow]] · [[api/MontionManager]] · [[api/DeltaEtherCAT-Native]] · [[api/ProcessControlPage]]
- 架构：[[architecture/DeviceControlArchitecture]]；教训：[[lessons/SimulationAutoBranching]] · [[lessons/StepDrivenWorkflowPitfalls]] · [[lessons/JudgementThresholdScaleMismatch]]
- 焊参侧：[[decisions/ADR-043-WeldParamControlConsolidated]]（算法分层 / 配置合一 / 数据库关联）
- 通用约束：[[decisions/ADR-006-ModuleOrganizationPatternStandard]] · [[decisions/ADR-016-WorkflowResponsibilityBoundary]] · [[decisions/ADR-033-ConfigArchitectureStandard]] · [[decisions/ADR-041-ResidentFlowNonBlockingParadigm]] · [[decisions/ADR-039-SimulationTestAutoTerminationAndRecordCacheRelease]] · [[decisions/ADR-032-SimulationTestRedesign]] · [[decisions/ADR-037-ProductProductionRecordLifecycle]] · [[decisions/ADR-038-RobotCommandDrivenStepFlow]]
- 前序删除页：ADR-031/040/043/044/052/053/055/056/058/061（09-17 重排前编号，去向见 [[decisions/ADR-Index]] 删除对照表）
