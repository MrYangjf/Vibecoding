---
title: 注释跨行合并迁出台账
date: 2026-11-10
tags: [注释, 迁移, 工程约束, C18, C19]
status: accepted
---

# 注释跨行合并迁出台账

> **用途**：[[modules/CommentConstraintRegistry]] 的续页。C18（跨行合并计数）/ C19（变量 `//` 只许一行）落地时，压不进 20 字的结构性细节在此留存。
> **维护**：按源文件分节，节内每条注明原行号与迁出原文。

## 章节导航

- [迁出条目（跨行合并补充）](#迁出条目跨行合并补充)
- [相关页面](#相关页面)

---

## 迁出条目（2026-11-10 跨行合并口径补充）

> 来源：C18 跨行合并计数 / C19 变量 `//` 只许一行落地时被压缩掉的细节。

### CommunicationManager.cs

`Comm/Communication/CommunicationManager.cs`

- 原约 L829：目标端口不一致会发到未监听端口

### KukaRsiComm.cs

`Comm/Communication/Implementations/KukaRsiComm.cs`

- 原约 L1327：格式按手册推导生成，便于现场核对

### IntelligentLaserCam.cs

`LineLaserCam/IntelligentLaserCam/IntelligentLaserCam.cs`

- 原约 L94：_lastErrorCode = 厂商返回码；_lastErrorLocal = true 表示本机拦截/异常，未取得厂商返回码
- 原约 L140：校准快照由回调捕获中心点与四角点，业务层读取后绘制校准框，本类只存储

### VirtualCam.cs

`LineLaserCam/VirtualCam/VirtualCam.cs`

- 原约 L25：模拟出图节拍由定时器代替 SDK 推帧；节拍由线激光数据频率（30/60/80/120Hz）决定，运行时可经 FrameRateHz 调整

### DeviceControlWork.cs

`MainDeviceControl/DeviceControlWork.cs`

- 原约 L265：模拟调度步（与主机同构，步号：大步 10/20/30、小步 +1） 10 等进入 PreWork；20 等 PreWork 反馈；21 启动门控；30 焊接中
- 原约 L268：焊接启动门控：IoSubWork 到达时运控仍在标定 → 挂起受理， 由模组线程按拍轮询 IsCalibrationYReady 后补执行。
- 原约 L915：上行指令经具名元素数值码承载（RxCmd/RxPayload）；EStr 在 RSI 包中恒为空串。
- 原约 L939：成功判据以 ConnectRobot 的真实返回值为准。
- 原约 L980：使 Dash 机器人指令行也能显示设备下发（Tx*）指令。
- 原约 L1960：打开后按 AlignDatum.OffsetX/Y × PixelMmScale × GALVO_CENTER_COMP_GAIN 得中心值， 交 LaserWeldHeadWorkflow.ApplyGalvoCenterOffset 单写口（与摆幅下发链合并，防互相覆盖）。

### CommandCore.cs

`MainDeviceControl/DeviceStateApiCore/CommandCore.cs`

- 原约 L183：带坐标载荷的报文（如「RX_WELD_STOP_POSE,1520.5」）先经 TrySplitPayload 拆出指令头再查字典， 保证载荷报文也能显示中文释意。
- 原约 L220：8=TX_NG（焊接中异常）/ 9=TX_ABORT / 10=备用（不映射）

### DeviceInitOutcome.cs

`MainDeviceControl/DeviceStateApiCore/DeviceInitOutcome.cs`

- 原约 L7：本枚举只表达「本次初始化怎么处置」；不是设备运行态。

### DeviceStateBase.cs

`MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs`

- 原约 L7：本枚举＝设备本体状况（未连/在线/故障），彼＝焊接流程阶段。

### LaserWeldHeadWorkflow.cs

`MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs`

- 原约 L327：LA_Spot 与 LA_Pose 一样退出 LA_Auto 随动——本方法先退出随动， 再按「曲线A 基准 + 曲线B 当前 TA 偏移」做一次定位下发；后下发 LA（单次动作，非随动）。
- 原约 L552：开启时从工艺配置 WeldAlgorithmsConfig.LaSpotTargetMm 读取目标光斑，按两曲线先下发一次，随后重新进入随动。

### LineLaserWorkflow.cs

`MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs`

- 原约 L314：行程完成判断归设备主控（DeviceControlWork.CheckWeldProgress）；本流程不自行推进步骤。

### MotionControlWorkflow.cs

`MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs`

- 原约 L28：执行步：0 待机 / 900 失败收尾，由基类提供 步号范式：大步 10/20/30，内部小步 +1（11/12）； 大步 10 = 启动段（11 使能→12 回归）；20 = 已使能待机
- 原约 L36：回归：发移动后先等运动停止，再判到位偏差 偏差 ≤ CalReturnToleranceMm 才算到位，否则重发；超 CalReturnMaxRetry 次或等停止超时即失败。 能否下发改看 Y 轴行程上下限，越界才报警
- 原约 L42：CSP 软目标到达窗口的「条件成立次数」（手册 9.1.12 WindowTime，单位=次數；示例 1ms×100=0.1s）。 50 为按 1ms 周期估的稳定窗，待现场核定。
- 原约 L45：收尾 BufferStop 必须用 Mode 1（平滑停止，清 FIFO 并解除坐标系）；Mode 0 是 Feedhold， 否则清缓冲被拒，残留坐标系致下次启动失败 减速中下电触发伺服报警，残留报警致使能失败
- 原约 L53：CSP 缓冲流式输出（由 FlowProcess 按拍写段，不自起线程）。 上游死区只作写入门限 150ms 使滞后上界 = MaxVel×τ = 1mm/s×0.15s = 0.15mm。 ⛔ 禁止位置贴齐与按剩余距离限速（会旁路限幅链） 剩余恒 0 ⇒ 速度清零、命令冻结、轴停走
- 原约 L61：⚠️ 分母越小 ⇒ 段速越高 ⇒ 段先跑完 ⇒ 断供 过小会高估段速，段末带速冲过端点后被拉回
- 原约 L90：段距门限 0.01mm 后段时长≈105ms@0.095mm/s， 3 段即约 300ms 前瞻；10 段会使启动累积 0.1mm≈1s 且该积压在 sv=gv 下永久残留为滞后
- 原约 L92：连续静止拍数达此值即判队列耗干（60 拍≈600ms） 阈值须大于目标台阶间隔，否则平台处误判耗干 误判耗干 ⇒ 轴停走
- 原约 L98：停止模式（手册 9.7.16）：0=保持 1=平滑停止 2=急停。 ⛔ 收尾必用 1：Mode 0 后清缓冲被拒，残留坐标系致失败
- 原约 L110：取 0.5μm（半脉冲当量）：正常每拍约 0.1mm
- 原约 L112：（30 拍≈300ms） 曾见写段持续成功而轴反馈冻结、全程零错
- 原约 L161：`Motion_Get_Mdone` 在指令刚下发时仍是上次的「已完成」态 直接判已停会当拍跳判、反复重发；两段判缺一不可。
- 原约 L169：（停稳后才下电）（StepStopping 未完成时 `FlowProcess` 会按拍重入本步）。
- 原约 L274：若以末段位置为基准，未写段拍的位移会被丢弃；写段只交出末端。
- 原约 L324：「测量时刻轴值 Ya1」参与绝对目标合成，使地图与反算链路与有轴模式同构。
- 原约 L391：——Standby 下 Ready 与 Idle 不可区分，不留替代标志。
- 原约 L557：小步 22：等轴运动停止（CSP 模式的「运动停止判定」；跳步拍写 log，判断点静默） ⚠️ 两段判：Mdone 在刚下发时仍是上次的「已完成」态 ⇒ 直接判已停会当拍跳判、反复重发； 故前半段先等已启动，后半段才等已停止。
- 原约 L569：⚠️ 位置优先短路：本轮可能是空动作，IsMoving 恒假 前半段等不到已启动，只能空等满超时 仅当已静止且在容差内直转 23 复核（结论仍由 23 给） 此处不置 _calReturnReady：未动且不在容差内时，超时兜底不变
- 原约 L693：不引入任何「距离过大/过小」的固定阈值。
- 原约 L755：手册 9.1.12：CSP 模式下从站未提供 CiA DS402 Statusword 的 target reached 功能时，用此 API 启用上位控制器到位信号。
- 原约 L774：Mode 1（平滑停止）已清 FIFO 并解除坐标系（手册 9.7.16），故 Stop 一步到位： 成功即视为已清干净，不再追加 BufferClear；Mode 0 实为暂停、什么都没清，故报清空失败。
- 原约 L798：收尾 BufferStop 用 Mode 1：清 FIFO 并解除坐标系，轴减速停稳，故须等 IsMoving 翻假再清理下电。
- 原约 L911：残留标志会让首拍即被报警拦截，表现为「启动就报警、清不掉」。
- 原约 L998：记录起点 = Ready 通过（轴到位且有数据）；否则曲线前端会压一段空行。
- 原约 L1280：速度、加速度限幅在本步完成，算法侧只给修正量，职责不重叠。
- 原约 L1365：收尾用 Mode 1：手册 9.7.16 明确已清 FIFO 并解除坐标系，故不再追加 BufferClear： 旧实现用 Mode 0 加 Clear ⇒ 面对未清空 FIFO 调 Clear 必被拒，即报警源。 仅当 Stop 自身失败时才兜底 Clear；失败计数保留为驱动器状态漂移的观测指标。
- 原约 L1390：段端点以「起焊锚点 + 修正量」为绝对目标，平滑基准与段距差分统一取队列末端。
- 原约 L1408：基准为标定轴值。
- 原约 L1421：目标 = 算法绝对 Y 目标（轴值 + 特征偏差 − Y 差分）。 绝对量直传，不做减标定轴值再加回的折算——否则基准出现两次、掩盖语义，限幅判据也含混。 无地图点时回落标定轴值，轴已归位，首段不跳变。
- 原约 L1427：跟随器按内部位置推进，未写段位移不得丢弃；段距仍以末段为基准。 段距是交给驱动器的位移，须与段端点口径一致。 前馈：X 向速度 × 地图局部斜率 = Y 轴速度需求。 需求失真时仅回退旧行为；抬升幅度记入诊断行。
- 原约 L1435：命令端点对齐整脉冲（与驱动器 ToPulse 同口径，截断取整）： 不对齐时段脉冲数偏少，差额留在队列末端、不随段写入复位，累积成系统性欠走 （AxisY 每拍平均位移 -1.1~-1.9μm，命令持续前进而轴长期少走）。 对齐后段距恒为整数脉冲，截断残差自动滚入下一拍，不再丢失。
- 原约 L1449：启动：未运行且已攒够阈值段（首启 10 段；耗尽重启 1 段）即 Start。 失败须计数收敛：恒失败码逐拍重试会刷满日志，且流程永远停在 Working 无法自终止，只能人工点停止。 达上限即停闭环并置报警，由流程线程 Fail 收尾（报警只置标志，不推进执行步）。
- 原约 L1497：段距判据：= max(CspMinWriteSegMm, 单脉冲当量半值)；门限 0.01mm 使巡航段时长 ≈ 105ms ≥ S 曲线时间（台达建议 10ms）。 门限与钳位共同保证段时长 ≥ 到下段的墙钟间隔；未写段拍段距照常累计，到门限一次性写入，几何速度不失真。 写段判据与时基共用同一间隔量。
- 原约 L1501：双门限：距离门限 OR 时间到点。时间侧附加已攒够整脉冲，保证写入段必有位移。 目的不是提速，而是不让写段间隔超时基上限；超限即高估段速，驱动器提前跑完本段后空等下一段（轴停走）。
- 原约 L1513：段速度时基 = 自上次写段的实测间隔，而不是单拍。段距是自上次写段以来累计的位移（中间可能夹着被跳过的拍）。 按单拍折算会高估段速，段时长不足而下段久等；驱动器缓冲周期跑空、轴呈停走。 按累计间隔折算，段时长恒等于下路段间隔；供需同步。
- 原约 L1520：段速平滑：相邻段速度差受加速度限幅（弃 EMA）。EMA 是低通滤波，输出与几何速度存在稳态偏差； 钳位只能压在带内（偏快断供、偏慢滞后累积）；限幅跟随每拍朝几何值移动，单拍变化不超加速度允许值，既平滑又长期无偏。
- 原约 L1539：积压反馈：几何钳位之上叠加提速量，正比于积压且有上限。 只作用于写入段速，不改目标与跟随器位置，闭环目标仍是绝对量。 自限性：积压趋近死区时增量趋 0，自动退回断供安全行为。
- 原约 L1628：写段占空比 = 写段数 / 输出拍数。远低于 100% 即说明段距判据在砍写段节拍， 下游会出现无段可执行空档（约 44% 时轴停走）。
- 原约 L1659：轴实速远大于写入段速，即段速被抬到最小执行速度。
- 原约 L1785：残差取跟随器位置，不取本拍输出（限幅失效时会旁路）。 也绝不对残差抹零（等于再插一级死区，段端点会冻结）。 亚脉冲残差由端点整脉冲对齐消化；跟随器位置始终保留残差。
- 原约 L2063：输出态可能正常出力，也可能撤力失败残留。
- 原约 L2500：扭矩上限（CSP 阻抗与 CST 出力共用）。 ⛔ 不当作已出力——驱动器仍按 slope 从当前扭矩爬升。
- 原约 L2544：（Auto 不读不打印）

### WeldParamControlWorkflow.cs

`MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs`

- 原约 L235：RSI 为唯一通道且指令/参数全部数值化；文本协议「P功率 S送丝 V速度 G摆幅」已废止。
- 原约 L587：历史双源镜像判据（WeldStatus==X 且 _phase!=X）已随状态消解； ErrorAborted 下的输出停走由 FlowProcess 的「WeldStatus != Working」消费门禁承担，本流程无步号入口需推进。

### HikCam.cs

`MonitorCam/HikCam/HikCam.cs`

- 原约 L46：_lastErrorCode = 厂商返回码；_lastErrorLocal = true 表示本机拦截/异常，未取得厂商返回码

### MonitorCamManager.cs

`MonitorCam/MonitorCamManager.cs`

- 原约 L40：录像目录（启动期可用性检查）；回退目录为内存态、不落盘、不覆盖配置

### DeltaAxisConfig.cs

`MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs`

- 原约 L76：下压力归 AdaWeldSystem.WeldParamControl.WeldAlgorithmsConfig.TaForceN（原注释为全限定类型名）

### DeltaControllerConfigImporter.cs

`MotionControl/DeltaEtherCAT/DeltaControllerConfigImporter.cs`

- 原约 L402：同一变量名在 Rx（0x1601 等）与 Tx（0x1A01 等）成对出现是 ESI/IO 表正常结构
- 原约 L603：供应商换版本（Vendor 值或 PDO 变化）仍可重新识别

### DeltaMontionAxis.cs

`MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs`

- 原约 L112：扭矩上限由 DeltaTaHomeConfig.GetTorqueLimitPerMille 换算后由 MontionManager 写入
- 原约 L411：模式换算：逻辑值（有符号）→ 16 位补码。台达确认 Mode 形参为 16 位无符号，负值强转即可。补码即正确编码（-2=65534），统一 Home_Config，不设 CoE 双路径。
- 原约 L1026：统一上限：CSP 阻抗与 CST 出力共用 TA_TORQUE_LIMIT_N。超上限即钳制，并区分被钳制与原本在内——⛔ 被钳制 ≠ 已出力，仍需按斜率爬升。
- 原约 L1058：不设参数相同即跳过：会沿用旧目标与斜率，而 TORQUE_SLOPE 改小后必须真实生效。热切换与冷启动都要把目标重新下发一次。

### DeltaSlaveDevice.cs

`MotionControl/DeltaEtherCAT/DeltaSlaveDevice.cs`

- 原约 L115：表内 0x1304 = MAILBOX / SDO_BUFFER_FULL / ESC_FAILED，0x1305 未收录；0x1305（=4869）不是 SDO 中止码

### DeltaTaHomeConfig.cs

`MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs`

- 原约 L34：软件侧由 DeltaMontionAxis.TorqueLimitPerMille 钳制 CST 目标；驱动侧在伺服 OFF 窗口写入 16#6072（Max torque）

### MotionConfigImporter.cs

`MotionControl/DeltaEtherCAT/MotionConfigImporter.cs`

- 原约 L11：电气填写的轴/IO/气缸三张 CSV（UTF-8 带 BOM）
- 原约 L652：CSV 导入的 TA 行同步进 TaHome，避免「导入只改 AXIS、运行期仍用旧 TA_HOME」的双源漂移

### MontionManager.cs

`MotionControl/MontionManager.cs`

- 原约 L1730：回零参数由 StartHome 每次 Home_Config 时下发，故下次回零即生效，无需重新使能或重新连接

### ProductFileRecordManager.cs

`ProductFileControl/ProductFileRecordManager.cs`

- 原约 L623：按时间区间查询生产记录的摘要原为「数据追溯页区间筛选入口」

### DataReviewerPage.cs

`UIDesign/ControlPage/DataReviewerPage.cs`

- 原约 L395：`⛔ 不用 Visible / FindForm().Visible / Created / IsHandleCreated：2026-11-09 运行期实测——AntdUI 的 Tabs 不隐藏非当前 TabPage，窗体 Show 时全部子页为 Visible=true 子页同时触发，双判据会被放行。` 被删细节：判据清单中的 FindForm().Visible；实测日期 2026-11-09；「子页同时触发」；「Tabs」的定冠词表述。

### MainPage.cs

`UIDesign/ControlPage/MainPage.cs`

- 原约 L47：`// 轮廓轮询：独立线程定节拍取快照，解耦帧率` + 行尾 `// 约 30Hz`：合并为一行后删去「取快照」，「解耦帧率」保留。
- 原约 L96：`// ── 焊接流程步骤条（steps1 由设计器声明）：五步 ──` 被删细节：steps1 由设计器声明；步骤条为五步；随该组字段的行尾注释（当前步骤正常只前进、复位/重新启动可回退）已并入标题行。
- 原约 L103：`// 硬件快捷开关：2×2 四区域，每区按钮 + Alert` 被删细节：「每区按钮 + Alert」——每区域为一个 ButtonShadow 按钮加一个设备名 Alert 提示（Alert 由下一字段 _deviceAlerts 注释承载）。
- 原约 L125：`// ── 整机状态标签（LabelStatus，承接原 FormMain 左下角整机状态）──` 被删细节：控件名为 LabelStatus；该标签承接原 FormMain 左下角整机状态（属过程/由来信息，按规范移出代码）。
- 原约 L521：`限值来自 CurrentAutoParam 真实配置非假数据；` + `防未配置限值线拉低纵轴。` 被删细节：限值非假数据；未配置限值线（0/0）会拉低纵轴——故上限≤下限时不画。
- 原约 L1345：`现改为：首帧数据到达时一次构图。` 被删细节：「现改为」这一变更史表述（按规范注释不写过程与演变），语义保留为「首帧数据到达时一次构图」。

### AxisConfigForm.cs

`UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs`

- 原约 L202：`// 实测（AntdUI Modal.open 承载 UserControl）：弹窗尺寸 = 控件尺寸 + 48(宽) / +62(高)，横向再预留 24px 余量，部分宿主会再收窄 24px` 被删细节：AntdUI Modal.open 承载 UserControl 这一实测场景；部分宿主会再收窄 24px；横向余量精确值 24px（值本身在代码常量中保留）。
- 原约 L205：`// 高度按内容 + 底部按钮 + 内边距；超出屏幕可用高度时由容器滚动（不缩小字体）。` + `// 预留 96px（内边距 40 + 标题 22 + 余量 34），保证不出工作区` 被删细节：超出屏幕可用高度时不缩小字体（改由容器滚动）；96px 的构成（内边距 40 + 标题 22 + 余量 34）。
- 原约 L301：`// 输入框放进单元格宿主并垂直居中` + `// 不居中就会与 MiddleLeft 的标签基线错开（即截图中的"歪斜"）` 被删细节：与 MiddleLeft 对齐标签的基线错开现象；截图中的「歪斜」表现。

### FilebackupPage.cs

`UIDesign/TabPage/FilebackupPage.cs`

- 原约 L1518：`同一变量在 Rx（0x1601 等）与 Tx（0x1A01 等）成对出现是 ESI/IO 表正常结构` + `（PDO Index/SubIndex 优先，仅 SDO 行用 SDO 复合键）` 被删细节：Rx 侧示例索引 0x1601、Tx 侧示例索引 0x1A01；复合键优先级为 PDO Index/SubIndex 优先，仅 SDO 行改用 SDO 复合键。
- 原约 L847：`// 预览不重复加载焊接头配置，避免刷日志` 被删细节：预览若重复加载焊接头配置会刷日志（改为取运行期已装载配置的原因）。

### ProcessControlPage.cs

`UIDesign/TabPage/ProcessControlPage.cs`

- 原约 L977：`// 门禁按轴独立：Y 失败只关 Y 区，不连带 TA/LA。` + `// 取值按流程归属：Y / TA → MotionControlWorkflow；LA → LaserWeldHeadWorkflow。` 被删细节：Y 轴失败只关闭 Y 区、不连带 TA/LA；门禁取值按流程归属，Y 与 TA 取 MotionControlWorkflow、LA 取 LaserWeldHeadWorkflow。

### SystemControlPage.cs

`UIDesign/TabPage/SystemControlPage.cs`

- 原约 L2044：`// ⛔ 不写 ④Preset 区：本按钮只存焊接头配置` + `// ④Preset（跟踪几何/LA·TA 预设/振镜图形）归工艺设置页` + `// 顺带落盘会把未保存值提前写盘（跨页副作用）` 被删细节：④Preset 区含跟踪几何、LA·TA 预设、振镜图形；该区归工艺设置页维护；顺带落盘会把未保存值提前写盘（跨页副作用）。
- 原约 L2052：`// 回零模式双端值：逻辑（有符号）↔ 16 位补码下发值。` + `// 台达确认 U16 强转，统一走 Home_Config。` 被删细节：逻辑值为有符号、下发值为 16 位补码的双端映射；台达已确认 U16 强转。

### WeldParamLookupAlgorithm.cs

`WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs`

- 原约 L92：摆幅宽度初值 = 光斑摆幅系数 × 焊缝宽；初值入表后可手动修正，最终输出用查表值；重建整表会用公式初值覆盖手工修正

---

## 相关页面

- [[modules/CommentConstraintRegistry]]
- [[standards/CodeSimplification]]
- [[architecture/CodeMap]]
