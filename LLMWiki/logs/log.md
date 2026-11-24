## [2026-11-24 11:45:08] upload | 两仓库最新内容推送 GitHub（main）
- 来源：业主 2026-11-24 11:40『把最新内容上传到github仓库』
- 操作：
  1. AdaWeldSys.git：a1e086f..4e8b966（176 文件 / +58981 -59510，含多轮未推的 2 提交）；Vibecoding.git：f636e63..8ae1d3a（114 文件 / +27518 -5206，含多轮未推的 6 提交）
- 变更文件：AdaWeldSystem/; Vicoding管理平台/
- 结论 / 遗留：推送前 fetch 确认两端均快进（本地领先 2/6，远端 0）；敏感词扫描 3 处 .resx 命中均为 .NET PublicKeyToken 误报；output/backup 包被 gitignore 排除；推送后双仓 main...origin/main 均 0/0、工作区干净

## [2026-11-24 11:34:50] review | 模拟流程审查复核通过 + 三项加固落地
- 来源：业主 2026-11-24『审查刚刚对模拟流程的判断，修复是否正确』；复核对象=上轮 6 条判断 + 6 处修复
- 操作：
  1. N1 ResetSimulationSessionState 补 _subWorkPending/_subWorkPendingLogTs（15 项→17 项）；N2 StartSimulation 开启端补 ResetSeamTracking(模拟会话开启复位)；N3 删 6 处孤儿 summary（SimulationConfig/LineLaserConfig/MontionManager/DeltaMotionConfig/TaLaCurveConfig/WeldParamConfig）
- 变更文件：MainDeviceControl/DeviceControlWork.cs; MainDeviceControl/SimulationConfig.cs; LineLaserCam/LineLaserConfig.cs; MotionControl/MontionManager.cs; MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs; WeldParamControl/Curves/TaLaCurveConfig.cs; WeldParamControl/WeldParamConfig.cs; wiki/lessons/SimulationAutoBranching.md; wiki/lessons/CommentSimplificationBatchPitfalls.md; wiki/api/DeviceControlWork.md
- 结论 / 遗留：复核结论：上轮 J1~J6 判断全部成立（缺值累计未随会话复位为真根因，62.6mm 可复现）；三项残留均属登记不全/晚清/注释残留，非功能性故障。真编译 errors=0 rc=0；字节级比对仅目标行变动（BOM 与行尾守恒）。现场仍需覆盖三种结束方式（焊缝行程完成/手动停止/异常自动停止）各连点两轮验证

## [2026-11-24 11:18:51] refactor | 模拟测试时序复审 + 注释与代码精简：case7 发出才推进、位姿心跳证伪、单一注入出口
- 来源：-
- 操作：
  1. case7 改发出才推进（拒发原地重试）与 case21/24 统一
  2. 清除两文件注释中全部 ⛔/ADR-/remarks 元信息并压缩长注释
  3. TryInject/TryReinject 尾部重复提取 FireSimCommand 单一注入出口
  4. T2 跳喂经代码链证伪故保留位姿心跳
  5. Ack 三方法归一经评估回退（净行数反增）
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; wiki/api/DeviceControlWork.md; wiki/lessons/SimulationAutoBranching.md
- 结论 / 遗留：真编译 errors=0 rc=0；静态断言 56/56 PASS（T2b 判据首版字符串匹配过脆已修正）；T2 不改码有据：PoseAgeMs 入图门禁依赖持续喂入

## [2026-11-24 10:51:33] coding | 恢复 SystemControlPage 误删的温度警告/报警四个控件
- 来源：-
- 操作：
  1. Designer 补回 lblTempWarnCaption/txtTempWarn/lblTempAlarmCaption/txtTempAlarm 四件套
  2. 挂载 gridTemp 第 5 行
  3. TabIndex 163-166 按 HEAD 原值
  4. 属性逐项比对 HEAD 一致
- 变更文件：AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs; wiki/guides/ExecutionEnvironment.md; wiki/lessons/UiModuleRemovalCleanup.md
- 结论 / 遗留：真编译 errors=0 rc=0（首次失败为 HTTPS_PROXY/https_proxy 环境撞键 MSB3883，unset 小写后通过）；属性比对 20/20 PASS

## [2026-11-24 09:08:49] coding | 模拟测试新增会话变量统一复位函数，任意次点击均从 Home 重新开始
- 来源：-
- 操作：
  1. 新增 ResetSimulationSessionState(reason, restartFromHome) 复位 15 项会话变量
  2. StartSimulation 传 true 且前移到线程拉起前
  3. DisableSimulation 传 false 停在无效步
  4. 新增 _simHardwareSuspended 防使能快照被覆盖
  5. 重复开启改为有日志的幂等返回
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; wiki/lessons/SimulationAutoBranching.md; wiki/api/DeviceControlWork.md
- 结论 / 遗留：真编译 errors=0 rc=0；静态断言 15/15 PASS（R15 判据首版失效已修正）

## [2026-11-23 21:53:43] coding | 模拟测试第二轮首拍缺值报警：会话复位补清缺值累计与位姿锚点
- 来源：-
- 操作：
  1. ResetNoValueDistance 同时清 _noValueHasPoseAnchor/_noValueLastPoseX/_noValueLastPoseTime
  2. ResetSeamTracking 与 ResetTrackingForWeldStart 调用 ResetNoValueDistance
  3. DisableSimulation 复位焊缝跟踪会话
  4. StartSimulation 调度步复位前移到线程拉起之前
- 变更文件：AdaWeldSystem/WeldParamControl/WeldParamManager.cs; AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; wiki/lessons/SimulationAutoBranching.md; wiki/api/WeldParamManager.md
- 结论 / 遗留：根因：上一轮末段 60mm 无数据行程残留 62.6mm 被第二轮 PreWork 首拍继承；真编译 errors=0 rc=0；静态断言 9/9 PASS

## [2026-11-23 21:15:45] coding | 日志三问题收口：自愈路径统一、审计 before 保真、注入超时重发
- 来源：-
- 操作：
  1. 通讯自愈路径改 ConfigFileManager.ModuleAbsolutePath
  2. 相机默认配置路径改载体路径
  3. 仿真配置暴露 DefaultFilePath
  4. ReloadCurrentParamValues 去掉 DeleteTable
  5. 模拟注入 21/22 合并为发出后推进
  6. 新增 TryReinjectOnAckTimeout 超时重发
- 变更文件：AdaWeldSystem/Comm/Communication/CommunicationManager.cs; AdaWeldSystem/MonitorCam/MonitorCamConfig.cs; AdaWeldSystem/MainDeviceControl/SimulationConfig.cs; AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/WeldParamControl/WeldParamManager.cs; wiki/lessons/ConfigZoneSaveWiring.md; wiki/lessons/SimulationAutoBranching.md; wiki/api/ConfigSelfHeal.md
- 结论 / 遗留：真编译 errors=0 rc=0；静态断言 16/16 PASS；焊前位X此前从未送达，本轮修复

## [2026-11-23 17:30:26] review | 澄清 4610 官方语义并沉淀 0x12xx 错误码对照表
- 来源：台达《EtherCAT 程式開發手冊》§33-4 命令回傳值與訊息描述（PDF P941）
- 操作：
  1. 确认 4610=0x1202=ERR_ECAT_SLAVE_TYPE 官方描述「此模組不支援此 API」
  2. 区分邻近码 4609参数错/4611目标到达/4612模式不支持/4613轴不支持该运动模式/4614PDO未映射/4615固件版本不支持/4618原点偏移
  3. 结论 4610 应按「该模块不支持该 API」判定 不再继续调参数
- 变更文件：wiki/api/DeltaEtherCAT-Native
- 结论 / 遗留：纯知识澄清，代码零改动

## [2026-11-23 17:27:58] fix | 按现场原型校准建系参数：orgFlag=1 sCurveTime=10 上限留余量
- 来源：业主提供的早期可运行原型代码（EtherCAT MotionBuffer 调用样例）+ 业主口径（别写 Disable、MultiAxis2 轴数写 1 可以、Get_Remain_Buffer_Size 取剩余缓存）
- 操作：
  1. 建系 Set_Crd_Parameters 的 orgFlag 由 0 改为 1（原型值 需要工作坐标偏移 传0时坐标系未按驱动器要求建立）
  2. sCurveTime 由 0 改为 10（台达建议值与原型一致 轴配置优先）
  3. 坐标系速度加速度上限放大4倍留余量（手册9.7.1 参数超上限即回传错误 段速会被积压提速短时放大）
  4. 建系日志补 工作坐标偏移/轴数/节点/槽/表 便于现场核对
  5. 确认未调用 MotionBuffer_Disable 且余量查询已用于诊断
  6. 沉淀原型基准参数表到ADR-042 D5e 与 lessons 教训
- 变更文件：AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs; wiki/decisions/ADR-042; wiki/lessons/SimulationAutoBranching
- 结论 / 遗留：真编译 errors=0 rc=0。待现场复测 4610 是否消失

## [2026-11-23 17:22:31] fix | 4610 回退三次重试 + 双接口写段排查
- 来源：现场日志 20261123 17:11（建系成功但写段持续4610 队列段恒0 运行0 轴不动）+ 业主（CSP完全没奏效不能移动 以前只有电机没问题 装轴上 脉冲当量1000 4610确实是没有移动的报错 恢复三次重试后报错终止）
- 操作：
  1. 回退4610降级Debug：恢复计故障+跨拍挂起重写+达3次Fail终止焊接
  2. 核对官方EtherCAT_DLL.cs头文件与手册P9-150范例 建系参数/写段签名/脉冲当量全部一致 排除参数错位
  3. 发现从站被标「未识别设备」厂商0x1DD产品码0x60010 基础CSP可用但MotionBuffer被拒
  4. BufferLineTo改为优先Line_MultiAxis(手册标准流程Step3) 遇4610回落MultiAxis2 双失败打印节点槽表FIFO与目标脉冲
- 变更文件：AdaWeldSystem/MotionControl/DeltaEtherCAT/Native/EtherCATMotionBufferNative.cs; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; wiki/decisions/ADR-042
- 结论 / 遗留：真编译 errors=0 rc=0。若两接口均4610则判定驱动器固件不支持缓冲插补。待现场复测

## [2026-11-23 17:08:02] fix | 4610 降级 Debug：不计故障不重试不阻断
- 来源：业主裁定（将4610报错降级到Debug 不影响程序继续 不需要重试）
- 操作：
  1. CspResult 新增 EcatSlaveType=4610 常量
  2. ReportCspResult 遇4610输出Debug级 其余仍Error
  3. QueueCspSegment 写段遇4610直接返回 false 不计_cspWriteFailCount不挂起
  4. 挂起重写遇4610作废挂起段不再重试
  5. 其余非0返回码仍按故障挂起重写达3次Fail
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MotionControl/IMotion/MontionAxis.cs; wiki/decisions/ADR-042; wiki/api/MotionControlWorkflow
- 结论 / 遗留：真编译 errors=0 rc=0。区分 4610(降级) 与 其他返回码(仍故障) 的处置口径

## [2026-11-23 16:51:33] fix | CSP 全程一条缓冲流：到达焊前X不停启
- 来源：业主口径（到达焊接前X时不希望CSP停止 一直入一直按X出 无停止再启动）
- 操作：
  1. TryStartPreWorkTracking 在PreWork启动即建系(TryStartPreWorkCsp)并立即写段 Y边扫边跟
  2. 移除QueueCspSegment的X未到位不写段判定 改为全程连续写
  3. 到达焊前X与起焊沿均不停启 起焊沿走复用分支不重建系不收尾
  4. 仅停焊沿StopCspOutput收尾
  5. 建系紧贴首次写缓存保证无4610
  6. 知识库ADR-042 D5/D5b/D5d与api页改为全程连续语义
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; wiki/decisions/ADR-042; wiki/api/MotionControlWorkflow
- 结论 / 遗留：真编译 errors=0 rc=0。待现场复测：PreWork建系后立即写段无4610、X移动期间Y即开始跟随、到达焊前X与起焊沿均无缓冲停启日志

## [2026-11-23 16:47:56] fix | 按现场CSP缓冲语义回退「容忍预载失败」：写缓存失败即故障
- 来源：业主现场口径（台达CSP缓冲开启后按缓存值移动直到耗尽 结束后须重新开启 标准时序=线激光提前扫→提前写缓存→到位开启→监控空拍→清零后重启）
- 操作：
  1. 回退预载期容忍分支 写段失败一律计故障并跨拍挂起重写 达3次Fail暴露
  2. Start阈值恢复为成功段数_cspQueuedSegments(原用尝试次数会导致空缓存开启轴不动并掩盖故障)
  3. 删除_cspPreloadAttempts字段与8处赋值
  4. 保留建系紧贴首次写缓存(X到位才建系)与空拍60拍判耗尽后重新Start语义
  5. 知识库修正D5c为「写缓存失败即故障」并新增D5d现场标准时序五步
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; wiki/decisions/ADR-042; wiki/lessons/SimulationAutoBranching; wiki/api/DeltaEtherCAT-Native
- 结论 / 遗留：复核通过：①提前扫②提前写缓存③到位开启④空拍监控⑤清零后重启 五步与业主口径一致。真编译 errors=0 rc=0。output 包见最新 AdaWeldSystem_output_*.tar.gz

## [2026-11-23 16:43:04] fix | 4610 定论：建系须紧贴首次写段（经 git 版本对比定位）
- 来源：现场日志 20261123 16:29 轮（建系后1.4s首次写段即4610）+ 业主提示（看未修改前代码 那时跟踪正常 现在插入寻位跑不下去）+ git show HEAD 对比原始版本
- 操作：
  1. 查明真因 原始代码建系后下一拍即写段(约10ms) 改版后PreWork先建系等1.4s X到位才写段 台达坐标系表闲置失效致4610
  2. 重构 TryStartPreWorkTracking 只激活地图跟踪与喂帧不建系 新增 TryStartPreWorkCsp 由DoPreWorkSeek在X到位时调用建系
  3. 预载期写段失败不计故障不挂起 只计_cspPreloadAttempts Start阈值改用尝试次数而非成功段数
  4. StartCspOutput复用分支加_cspOutputRunning判定 未建系则补建
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; wiki/decisions/ADR-042; wiki/lessons/SimulationAutoBranching; wiki/api/MotionControlWorkflow; wiki/api/DeltaEtherCAT-Native
- 结论 / 遗留：三轮假设（坐标系表未激活/先Start/点位运动切模式）均被现场证伪，最终靠版本对比定位。真编译 errors=0 rc=0。output=AdaWeldSystem_output_20261123_164212.tar.gz。待现场复测 4610是否消失且寻位阶段Y跟随移动

## [2026-11-23 16:24:29] fix | 焊前寻位先扫后跟 + 回退错误的先Start时序 + 消除三处假报错
- 来源：现场日志 20261123 16:15:44~16:16:13（BufferStart成功仍4610 + 寻位开始0.147s即报焊前完成 + 4352重复清缓冲 + 从站未装载记Error）+ 业主口径（寻位与以前工作方式一致 线激光提前扫 X到了才开启Y跟随 线激光还没看到Y就报错）
- 操作：
  1. 回退建系后立即BufferStart（空缓冲先Start致FIFO已启动拒写段=4610真因 手册P9-146先存指令方能执行 恢复建系→写段(预载2段)→Start）
  2. 新增先扫后跟 QueueCspSegment 入口 X未到位不写段不驱轴 X到位后才开Y跟随
  3. 新增 _preWorkSeekReady/IsPreWorkSeekReady 独立标志 修正_calReturnReady在回归标定位即置位致寻位刚要0.147s就判完成
  4. CheckPreWorkCompleted与IsSubWorkGateOpen改判IsPreWorkSeekReady
  5. StopCspOutput 的BufferStop成功后清_cspBufferStartedOnce 消除重复Stop的4352假报错
  6. 新增LaserWeldHeadWorkflow.IsSlaveReady 从站未装载时跳过LA/振镜只记Warn不记Error
  7. 寻位会话态补_preWorkSeekReady双清零
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; wiki/decisions/ADR-042; ADR-114; wiki/lessons/SimulationAutoBranching; wiki/api/MotionControlWorkflow; api/DeltaEtherCAT-Native
- 结论 / 遗留：修正上一轮错误结论（坐标系表提前激活假设已被现场证伪）。真编译 errors=0 rc=0。output=AdaWeldSystem_output_20261123_162420.tar.gz。待现场复测：4610是否消失、寻位阶段X到位后Y是否真移动、4352与从站Error是否消失

## [2026-11-23 16:10:29] fix | 焊前寻位真实移动到焊接点 + 坐标系表提前激活 消除 4610 二度复发
- 来源：现场日志 20261123 15:45:36~15:46:11（CSP 缓冲写入 4610 连续失败3次 运控异常终止 + 寻位阶段轴反馈恒 -37.000 段距0.0000 轴未动）+ 业主口径（Y轴真实移动到焊接位置 未移动到要报PREWORK错误）+ 业主线索（早几天 CSP 缓存模式提前开启就没问题）
- 操作：
  1. 根因 4610=坐标系表未激活 同轴同API先失败后成功 排除轴类型与运动模式(点位运动本身即CSP API不切模式) 排除未Start不许写(ADR-042预载3段后Start为现场实证时序)
  2. 新增 DeltaMontionAxis.EnsureCspMode 读模式非CSP则切并校验读回 建系前/写段失败时调用
  3. ServoOn 的 Set_MoveMode 返回值不再忽略
  4. PreWork建系后立即 BufferStart 激活坐标系表 空缓冲Start失败则降级写满2段后Start
  5. 写段失败重写时先尝试Start激活再重写
  6. 寻位到位判据加轴累计位移>=0.002mm 禁止目标约等于当前位置假到位
  7. 寻位超时失败原因统一为 焊前寻位失败 PREWORK
  8. 寻位会话态 _preWorkSeekStartTicks/_preWorkXArrived/_preWorkSeekStartAxisPos 在 ClearStatus 与 ResetProcess 双清零
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs; wiki/decisions/ADR-042; ADR-114; wiki/lessons/SimulationAutoBranching; wiki/api/MotionControlWorkflow; api/DeltaEtherCAT-Native
- 结论 / 遗留：真编译 errors=0 rc=0。待现场复测确认 4610 消失且寻位阶段轴位置发生变化(累计位移>0.002mm)

## [2026-11-23 15:17:08] fix | 修复模拟注入反复重发：PreWork 阶段工作实际未发生的三处缺陷
- 来源：现场日志 20261123 15:05:17~15:05:32（模拟注入机器人指令反复重发 + 拒收 整机非 Stop 态 当前 Running + 地图点恒0 平滑跳过持续递增）
- 操作：
  1. 缺陷1 喂帧门禁只看得焊沿开关 _seamTrackingActive PreWork阶段为false致每帧被丢地图恒空寻位超时 改为加 !_cspPreWorkTracking 放行
  2. 缺陷2 OnSeamTrackingStart 起焊沿调 ResetTrackingForWeldStart 清空PreWork建好的地图 改为 _cspPreWorkTracking 为真时不复位跟踪算法 复用地图与基准
  3. 缺陷3 模拟步6自行DoStartMachine致随后 RX_PRE_WELD_REQUEST 被 IoStart 的Stop前置拒收 改为模拟不自行启动 交给注入命令触发 并放宽 IoStart 前置为 Stop或Running均放行
  4. 另加 DoSubPrework 幂等守卫 判据取运控PreWork态 不用线激光态(模拟会提前切)避免焊前准备被永久跳过
  5. 模拟步序重排 5/6/7/8/20/21/22/23/24/25/30
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; wiki/decisions/ADR-038; wiki/lessons/SimulationAutoBranching; wiki/api/DeviceControlWork; wiki/api/MotionControlWorkflow
- 结论 / 遗留：根因共性 命令发出不等于阶段工作已发生。真编译 errors=0 rc=0。output=AdaWeldSystem_output_20261123_151655.tar.gz。待现场复测确认 PreWork 阶段地图点开始增长、寻位在60s内完成

## [2026-11-23 14:56:30] review | 核对机器人作业循环全景 + TA_Auto 门禁问题确认已解决
- 来源：业主给出的作业循环口径 + 业主提问（PreWork 能否执行 TA_Auto）
- 操作：
  1. 逐节点核对 8 个循环节点与协议指令映射 全部一致 过渡点RX_START_SAFE_POSE无动作 焊接结束点RX_WELD_STOP_POSE仅记录由行程监视收口 预停语义由lead前置量实现
  2. 确认闭环条件 ConnectOff 只置子流程Disconnected不调InitializeOff 故第二轮Home复位仍可受理 EnsureResetReadiness通过
  3. 确认 TA_Auto 门禁问题已解决 新增 TaExecuteAuto 流程内入口绕过 CheckAutoWeldingConflict 仍受 CheckTaAvailable 约束(TaMotionReady&&TaHomed 复位链后成立)
  4. 沉淀 ADR-038 循环全景表 + api/MotionControlWorkflow 与 api/DeviceControlWork 横幅
- 变更文件：wiki/decisions/ADR-038; wiki/api/MotionControlWorkflow; wiki/api/DeviceControlWork
- 结论 / 遗留：本轮代码零改动（仅核查与沉淀），真编译 errors=0 rc=0。遗留：对外回复指令未接线、LA机械回零未实现、模拟侧只跑一轮焊接不做安全离开→Home收尾（下一轮=重新开启模拟）

## [2026-11-23 14:39:01] fix | 审查修正：四处真实流程断链 + PreWork 启动时机
- 来源：业主审查要求（梳理流程/查 manager 与 workflow 越界）+ 业主对 RxWeldStartPose 语义澄清
- 操作：
  1. 修正 RxPreWeldPose 误映射 IoSubPrework 改为仅记录坐标 PreWork 改由 RxPreWeld_REQUEST 启动（移动期间须起 否则X停地图建不起寻位必超时）
  2. RxPreWeld_REQUEST 额外置 IoSubPrework 与 IoStart 同时
  3. ScanPulseIo requireRunning 未满足改为保留IO供下拍重试 原为取走后丢弃
  4. IsCommandPreconditionMet 对 IoSubPrework/IoSubWork 改为不拒收 原为拒收丢指令
  5. DoStartMachine 统一启动运控步机 真实流程 Start() 此前零调用方致运控RunStep停0寻位不可达
  6. DoResetMachine 补 Running态拒绝复位 避免Running→NoReset被拒致状态不一致
  7. 模拟 EnsureRunningForSimulation 先停机再清态
  8. 模拟X推进拆两段 StartRobotXSeeking 与焊前准备同步起 消除移动段早于跟踪段的未引导数据
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/MainDeviceControl/DeviceStatusWork.cs; wiki/decisions/ADR-038; ADR-032; wiki/lessons/SimulationAutoBranching; wiki/api/DeviceControlWork; DeviceStatusWork
- 结论 / 遗留：越界自查：主控仅调子流程公开成员零私有直访；运控无 AdvanceStep(StepWorking) 不自迁跨阶段步；跨workflow直读两处为既有代码非本轮引入。真编译 errors=0 rc=0。output=AdaWeldSystem_output_20261123_143852.tar.gz

## [2026-11-23 14:29:52] fix | 三阶段命令驱动：Home→复位→焊前→焊接 + 阶段应答
- 来源：业主需求（三阶段信号交互）+ 业主裁定（主控被动接受命令/阶段完成需回复/对外指令待定）+ 业主确认（Home→触发复位、WELD_START_POSE 触发焊接、真正工作从prework开始）
- 操作：
  1. MapCommandToIo 补映射 RxHomePose→IoReset(原IoStop) RxPreWeldPose→IoSubPrework(原仅记录) RxWeldStartPose→IoSubWork(原仅记录)
  2. 新增阶段应答态 IsResetCompleted/IsPreWorkCompleted/IsWeldStartAcknowledged 对外回复指令待协议确定
  3. DoSubPrework 新增 EnterPreWorkWorkingModes 调 TA自动/LA自动/振镜按自适应基准值开启摆动
  4. 新增流程内自动入口 TaExecuteAuto/LaAutoAuto/GalvoWeaveStartAuto 不做手动动作门禁
  5. 焊接头ResetProcess 新增振镜回逻辑零位 LA机械回零待实现
  6. 模拟改注入Rx命令到真实队列 InjectSimRobotCommand 调度步重排5/6/10/20/21/22/23/24/30 并按1s限频重试注入
  7. DispatchAction 忙时保留IO供下拍重试 不再丢弃指令
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceStatusWork.cs; wiki/decisions/ADR-038; ADR-032; ADR-100; wiki/lessons/SimulationAutoBranching; wiki/api/DeviceControlWork; MotionControlWorkflow; LaserWeldHeadWorkflow; DeviceStatusWork
- 结论 / 遗留：真编译 errors=0 rc=0。遗留：对外回复指令未接线(等协议确定)、LA机械回零未实现、振镜LA工作模式待现场验证。output=AdaWeldSystem_output_20261123_142943.tar.gz

## [2026-11-23 13:43:46] fix | 新增焊前寻位流程与模拟寻位起点X配置
- 来源：业主需求（重做PreWork环节）+ 前序 4610 诊断
- 操作：
  1. 新增运控步 StepPreWorkSeek=13 焊前寻位 判据 X到位且Y到焊接点 超时60s报PreWork失败停焊
  2. PreWork阶段只激活地图跟踪不开缺值量测 不报NoValueAlarm
  3. 机器人焊前位X由 RX_PRE_WELD_POSE 报文记录 到位判据差≤5mm
  4. 模拟新增可配置 焊接前寻位起点X(mm) 存 SimulationController.ini 的 PreWorkStartXmm
  5. 模拟X两段式 开启即自0移向设定点到达即停 起焊段继续沿焊缝前进
  6. 建系后留50ms稳定窗口再写段
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; MainDeviceControl/DeviceControlWork.cs; MainDeviceControl/SimulationConfig.cs; UIDesign/TabPage/SystemControlPage.cs; SystemControlPage.Designer.cs; wiki/decisions/ADR-114; ADR-042; ADR-Index
- 结论 / 遗留：ADR-114 新建（新号=max+1=114 脚本页内标题需人工修正为114）。真编译 errors=0 rc=0。风险：真实流程依赖机器人先移动到焊前位，否则地图建不起寻位超时失败

## [2026-11-23 11:53:57] fix | PreWork 起跟踪 + 写段失败挂起重试 消除 CSP 4610
- 来源：现场日志 11:11:15:0260 CSP 缓冲写入失败 4610 + 台达官方手册 PM_TC_20250428 P941/P956
- 操作：
  1. 新增 TryStartPreWorkTracking PreWork 建系并激活地图跟踪 起焊沿复用不重建系
  2. 抽出 BuildCspCoordinateSystem 供 PreWork 与写段重试共用
  3. 写段失败不推进队列账本 段挂起延时0.05s跨拍重写 连续失败3次报警停焊
  4. 新增 BeginSeamTrackingForPreWork 只激活跟踪不开缺值量测
  5. 模拟X时钟前移到DoSubPrework 只喂位姿X不动 DoSubWork 调 StartRobotXMoving 起步
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/WeldParamControl/WeldParamManager.cs; wiki/decisions/ADR-042; wiki/lessons/SimulationAutoBranching; wiki/api/MotionControlWorkflow; api/DeviceControlWork; api/WeldParamManager
- 结论 / 遗留：4610=0x1202=ERR_ECAT_SLAVE_TYPE 此模块不支持此API(官方手册)，判定为建系后未Start窗口瞬态被拒。真编译 errors=0 rc=0。待现场复测确认不再出现4610

## [2026-11-23 11:25:28] diagnose | 诊断 CSP 缓冲写入 4610（只出诊断不改码）
- 来源：现场日志片段 2026-11-23 11:11:14~15:0260 + 台达官方手册 PM_TC_20250428 P941/P956
- 操作：
  1. 4610=0x1202=ERR_ECAT_SLAVE_TYPE 官方释义 此模块不支持此API
  2. 判定为建系后缓冲未Start窗口瞬态被拒 非永久轴类型问题
  3. 查出真正隐患 QueueCspSegment 写失败仍推进队列账本且 ReportCspResult 只限频记录无处置
  4. 沉淀 lessons/SimulationAutoBranching 陷阱廿四
- 变更文件：wiki/lessons/SimulationAutoBranching
- 结论 / 遗留：业主裁定本轮只出诊断不改码，代码零改动。写失败处置口径待业主确认后另案。无 output 包（无代码交付）

## [2026-11-23 11:08:13] fix | 模拟X时钟延后到PreWork完成 + 自适应复位首帧播种
- 来源：运行日志 20261123_智能填丝焊接系统日志.log（10:42~10:47 轮）+ 业主三问
- 操作：
  1. StartRobotXSimulation 从 StartSimulation 移到 DoSubWork 在 BeginWeldMonitor 前
  2. 起点复位改 ResetTrackingForWeldStart 不再全复位工艺调整
  3. WeldParamAdjustmentAlgorithm 增 _seamWidthSeeded 首帧有效宽度播种不算突变
  4. 问题3诊断 模拟线程职责边界合规不改码
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs; wiki/decisions/ADR-045; ADR-103; lessons/SimulationAutoBranching; api/DeviceControlWork
- 结论 / 遗留：真编译 errors=0 rc=0。output=AdaWeldSystem_output_20261123_110805.tar.gz。问题3按业主裁定保持 thSimTestWork 线程（位姿+日志），不改线程模型

## [2026-11-23 10:34:15] fix | 模拟测试自复位 + TA 复位区分 + 主页面轮廓手动门禁
- 来源：运行日志 20261123_智能填丝焊接系统日志.log + 业主口述需求
- 操作：
  1. 模拟启动自行触发 DoResetMachine 跳过机器人复位指令
  2. 新增 SimResetGateTick 门控 复位完成才进 Running 并启动子流程
  3. TA 复位按 TaHomed 区分首次回零+工作位/已回零仅工作位
  4. 主页面轮廓门禁改 IsAutoWeldingRunning||IsSimulationEnabled 手动时隐藏
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/UIDesign/ControlPage/MainPage.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; wiki/decisions/ADR-032; ADR-082; ADR-100; lessons/SimulationAutoBranching
- 结论 / 遗留：真编译 errors=0 rc=0。遗留：现场 TeachLockYMm=-37 越界 Y 软限位由业主自行修正，不在本轮改配置

## [2026-11-23 09:27:14] 修复 | 线激光调试页校准框显示不全：统一仿射变换
- 来源：业主报障（换新英莱相机后黄框只显示一半）
- 操作：
  1. 定位根因：渲染层沿用 demo 角点公式 center±|corner*rate|，隐含「毫米原点居中」假设，新相机标定原点偏置致顶边出画布；改为单一仿射变换（比例取四角毫米包围盒跨度、原点落点使包围盒居中）；角点/轮廓/毫米刻度栅格共用 ToPixel()；视图锚点取标定中心点、越界回退包围盒中心；数值仿真复现旧实现 y 范围 [-52.3,441.7]、新实现 [30,524]；顺带补齐上一轮遗留漂移（ILCamPage→LineLaserCamPage 改名登记 drift RENAMED + api 页改名 + CodeMap 生成器红链修复 + ADR-111 slug 修正）
- 变更文件：AdaWeldSystem/EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs; wiki/decisions/ADR-113-line-laser-calib-affine-render-transform.md; wiki/decisions/ADR-Index.md; wiki/lessons/IntelligentLaser-Callback-Mechanism.md; wiki/api/LineLaserContourAlgorithm.md; wiki/api/LineLaserCamPage.md; wiki/tools/codemap_build.py; wiki/tools/drift_scan_precise.py
- 结论 / 遗留：真编译 errors=0 rc=0；八闸门全绿（死链 0、ADR 冲突 0、漂移待修正 0）；对称标定数据下新旧像素完全一致 ⇒ 旧相机零回归

## [2026-11-23 09:05:19] refactor | 撤回上一轮BUG2未标定提示修复（业主澄清相机已标定，黄框画一半属比例尺问题另案）
- 来源：业主澄清：不会出现相机未标定状况，撤回上一轮 DrawNoCalibrationHint 修复
- 操作：
  1. LineLaserContourAlgorithm.cs 用改码前backup二进制覆盖，精确删 DrawNoCalibrationHint 方法+Render调用（md5还原468c8f47）
  2. BUG1回零修复保留不动
  3. api/LineLaserContourAlgorithm 去未标定提示横幅
  4. 教训页删坑二并改名 HomeStatusAuthorityPitfall
  5. MotionControlWorkflow 引用改新页名
  6. index重建
- 变更文件：EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs,wiki/lessons/HomeStatusAuthorityPitfall.md,wiki/api/LineLaserContourAlgorithm.md,wiki/api/MotionControlWorkflow.md
- 结论 / 遗留：真编译errors=0 rc=0；代码md5精确还原改码前；ADR-080演进纯BUG1未动；BUG2黄框显示一半（比例尺）为另案待查；无配置键变更

## [2026-11-22 21:26:35] fix | 修复Y轴回零NOT_REACHED误判与新相机无标定框
- 来源：现场报障：回零完成却报NOT_REACHED+4866；换英莱新型号后黄色标定框消失
- 操作：
  1. WaitAxisHomed改为Home_Status=0权威+位置偏差仅Warning
  2. TryHomeAxisWithWait失败分支删StopAxis
  3. LineLaserContourAlgorithm无标定时画黄色未标定提示
- 变更文件：MotionControl/MontionManager.cs,MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs,EmguALG/LineLaserContour/LineLaserContourAlgorithm.cs
- 结论 / 遗留：真编译errors=0 rc=0；静态判据0失败；配置同步=现场HOME_OFFSET=1.0mm不在包内但新判据已不受其符号影响；新相机需现场重新标定才有黄框；ADR-080演进+新教训HomeStatusAuthorityAndCalibFramePitfalls；output=AdaWeldSystem_output_20261122_212625.tar.gz

## [2026-11-20 17:48:20] fix | 修复线激光两BUG：手动数据串主页 + SignalXY xs回退异常
- 来源：业主报障：手动调试数据传主页显示；换新相机后 xs must not descend 异常
- 操作：
  1. BUG1 ProfilePollLoop加RunMode!=Manual门控仅自动模式消费轮廓（判据=workflow基类WorkflowRunMode，UI命令置Manual）
  2. BUG2 ApplyProfileSnapshot写_contourSignalXs时剔除X回退点保升序，X/Z成对写，渲染点数取written
- 变更文件：UIDesign/ControlPage/MainPage.cs
- 结论 / 遗留：真编译errors=0 rc=0；静态判据0失败；无配置键变更；现场提示=手动期间主页不显示轮廓，自动焊接启动置Auto后恢复；新教训ScottPlotSignalXyMonotonicPitfall；output=AdaWeldSystem_output_20261120_174812.tar.gz

## [2026-11-20 17:26:14] refactor | 温度显示迁至设备监控页并移除温度刷新开关
- 来源：业主需求：SystemControlPage温度显示迁DeviceMonitorPage，只留节点+阈值，移除温度刷新按钮
- 操作：
  1. DeviceMonitorPage 加9个温度显示控件+采集链+自有500ms Timer（保留业主VS布局image3D1/tlPTemp）
  2. SystemControlPage 删10控件+swTempRefresh+全套温度刷新链
  3. 阈值6项保留
  4. flowPanel3容器保留
- 变更文件：UIDesign/ControlPage/DeviceMonitorPage.cs(+Designer),UIDesign/TabPage/SystemControlPage.cs(+Designer)
- 结论 / 遗留：真编译errors=0 rc=0；双轮Grep温度链唯一归属DeviceMonitorPage；配置键无变更；output=AdaWeldSystem_output_20261120_172606.tar.gz；延时(ms)=气压报警消抖，下发从站OD子索引6

## [2026-11-20 14:44:30] refactor | UI 页面拆分与死弹窗清理
- 来源：用户需求：删除 SubDialog 死页面 / FilebackupPage 拆分 / ControlPage 新建空监控页
- 操作：
  1. 删除零消费弹窗 ConfigForm+IoConfigForm+CylinderConfigForm 及 csproj 注册
  2. FilebackupPage 去 tabsBackup 改作设置备份页
  3. 新建 CommSettingPage 承载通讯配置并挂入 navPageParam
  4. 新建 DeviceMonitorPage 空页挂入 FormMain.tabMonitor
  5. 更新 modules/api/ADR-112/lessons/CodeMap/drift
- 变更文件：UIDesign/MainWindow/FormMain.cs,UIDesign/TabPage/FilebackupPage.cs(+Designer/resx),UIDesign/TabPage/CommSettingPage.cs(+Designer/resx,新增),UIDesign/ControlPage/DeviceMonitorPage.cs(+Designer/resx,新增),AdaWeldSystem.csproj
- 结论 / 遗留：真编译 errors=0 rc=0；静态判据 0 失败；output=AdaWeldSystem_output_20261120_144422.tar.gz；配置同步清单：本轮无配置键变更

## [2026-11-20 09:00:41] refactor | 注释优化+新增约束C20：注释只写作用，禁⛔/日期/ADR元信息
- 来源：业主诉求「注释优化，且增加约束：新增代码注释不要包含⛔/日期/ADR，只写作用即可」
- 操作：
  1. 全库扫描145行违规（28文件）；精确整行映射批改143条+9处多行块合并；comment_scan long merged_over 82→0/var_multiline 7→0/legacy_line 3→0；元信息残留0；csharp_review新增A.注释含元信息(error级)+selfcheck JUDGE27+标准页裁定4/映射表行27；ADR-111+lesson CommentMetadataCleanup；index/route重建
- 变更文件：28个.cs源码; CodeSimplification.md; csharp_review.py; simplify_selfcheck.py; ADR-111; lessons/CommentMetadataCleanup.md
- 结论 / 遗留：阴性对照副本命中143/0遗漏；新判据阴阳性对照干净0误报/违规各命中1；真编译errors=0 rc=0；守卫175/0；200文件BOM/行尾零漂移；selfcheck PASS；output包20261120_090025.tar.gz

## [2026-11-19 17:50:45] refactor | 全库代码精简 P0：语法简化八则 IDE 17 项清零（官方 dotnet format 修复器）+ P1 注释超长项待业主裁决
- 来源：业主诉求「全库代码精简-按照wiki的代码精简要求来」→ Phase0 扫描器聚合 E=0、IDE 17、注释超长 82+7
- 操作：
  1. backup/基线快照
  2. dotnet format style 批改 17 项（IDE0059×8 out→弃元 / IDE0018×7 out var 内联 / IDE0270×1 ?? / IDE0031×1 ?.）
  3. 逐项复核弃元退化 0
  4. 真编译 errors=0 rc=0
  5. IDE 复验 0 诊断
  6. 结构守卫 175/0 PASS
- 变更文件：ConfigFileControl/Implementations/{ConfigFileManager,XmlConfigFile}.cs; MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; MotionControl/{DeltaEtherCAT/DeltaMotionConfig,WeldHeadSlaveDevice}.cs; UIDesign/TabPage/SystemControlPage.cs; WeldParamControl/WeldParamConfig.cs
- 结论 / 遗留：P0 完成：17→0 IDE 诊断，7 文件改动均语义等价、无弃元退化，真编译通过。P1（注释超长 82 条 + 变量注释多行 7 条）经判定为防错约束注释（含⛔/日期/ADR），机械压缩会丢失约束，按顶层裁定「只报不删、逐案裁决」列为待业主裁决项，本轮不擅自改写；465 warn 属存量 public 缺 /// 欠账（顶层裁定第3条不追溯）。output 包 AdaWeldSystem_output_20261119_175035.tar.gz

## [2026-11-19 17:40:13] fix | Phase3 复查补齐：修复 ADR-110 半成品（编号错写/正文截断/占位符）并登记索引；补登 drift RENAMED 关闭 1 处遗留漂移；清理 3 个临时脚本
- 来源：业主反馈「未按 skill 执行」→ 复查上一轮标定项迁移任务的 Phase3/4
- 操作：
  1. 修复 ADR-110 内部编号为 110、补全决策/备选/后果正文、去待补占位符；ADR-Index 登记 110 行；wiki_index_build + route_rebuild 重建索引；drift RENAMED 补登 WeldAlgorithmsConfig.cs→WeldParamConfig.cs（纯路径）+ ADR-067 旧名加注；清理 _tmp_migrate_{designer,code,meta}.py
- 变更文件：ADR-110-yt-calib-move-to-process-page.md; ADR-Index.md; drift_scan_precise.py; ADR-067-LATaSettingsSemanticRework.md; wiki/index/index.md
- 结论 / 遗留：八闸门 rc 全 0（drift 待修正 1→0）；output 包 AdaWeldSystem_output_20261119_174001.tar.gz（3.0MB）。Phase2 代码改动经复核全部在位（UI 落点/接线/分区归属三键写口），未改动代码逻辑

## [2026-11-19 15:20:29] fix | 补回标定区误删控件（示教Y轴锁定/标定中心点Y）并按业主裁定重排：Y与Z同行、示教Y下一行；跨页迁移五段完整性核查
- 来源：AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs（业主 2026-11-19 在 VS 调整标定区布局时误删 2 个控件）+ UIDesign/TabPage/SystemControlPage.cs（.cs 侧引用仍在 ⇒ CS0103 编译失败 4 处）
- 操作：
  1. Phase0 Query（定位三个标定项：TeachLockY 示教Y轴锁定坐标 / CalibratedCenterY 标定中心点Y / CalibratedCenterZ 标定中心点Z；查 Designer 发现 txtTeachLockY 与 txtCalibCenterY 的实例化+字段声明+Controls.Add 三处全丢，而 SystemControlPage.cs 仍在引用 ⇒ 必然 CS0103；查 git diff 确认 CalibCenterZ 为本轮新加、行 5 占用原行 5、行 6/7 空置；从上一版定稿包提取四个控件的原始属性块与文案）；Phase1 Plan（业主裁定布局：标定中心点 Y 与 Z 同行、示教Y轴锁定坐标下一行）；Phase2 Code（补回 lblCalibCenterY/txtCalibCenterY/lblTeachLockY/txtTeachLockY 的实例化+字段声明+属性块（文案照原：标定中心点Y(mm)/示教Y轴锁定坐标(mm)）+ 挂载；CalibCenterZ 由列0/1 移到列2/3 与 Y 并排；TeachLockY 落行 6；修 txtCalibCenterZ 字段声明重复 CS0102）；Phase3 Ingest（新建 lessons/MigrationCompletenessAudit + api/SystemControlPage 补标定区布局表）；Phase4 Lint（8 闸门 + 真编译 + 46 项自检 + 字节安全）
- 变更文件：AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs; LLMWiki/wiki/lessons/MigrationCompletenessAudit.md; LLMWiki/wiki/api/SystemControlPage.md
- 结论 / 遗留：真编译 errors=0 rc=0（⚠️ 修复前是 errors=4 rc=1）；静态守卫 files=175 fail=0 PASS；46 项自检全通过；字节安全 200 个 .cs 行尾/BOM 零变化。根因：业主 2026-11-19 15:12 在 VS 调整标定区布局（把 CalibCenterZ 上移占行 5）时误删了同行的 CalibCenterY 与下一行的 TeachLockY（实例化+字段声明+Controls.Add 三处全丢），而 SystemControlPage.cs 的 LoadLaserCalibOnForm 与 BtnApplyParams_Click 仍在引用 ⇒ CS0103 四处。⭐ 关键教训两条：① **编译结论是带时点的快照** —— 我上一轮报的 errors=0 是 15:11 的状态，业主 15:12 的 VS 改动使其失效，若不复编译就会带红灯交付；已固化进 lessons/MigrationCompletenessAudit。② **「控件存在」不等于「链路完整」** —— 本轮建五段核查表逐项机器断言（控件落点 / 回填 / 写入内存 / 落盘分区 / 持久化读写）：上一轮迁移的 14 项控件全部落位正确、链路完整（selGeoGuideSign 两处 FAIL 为判据误报 —— Select 控件用 SelectedIndex 而非 Text），工艺页零残留引用，YT 设置区现只剩 Y 指令三选项。修复后标定区布局：行5 = 标定中心点Y(列0/1) + 标定中心点Z(列2/3)，行6 = 示教Y轴锁定坐标(列0/1)，RowCount=10 / RowStyles=10 / 格位冲突 0。遗留：现场配置需重新填一遍（业主已确认）；通讯 8 个 XML 未合并（按 RSI 语义分层保留）；6 个孤儿配置文件全仓零引用已从迁移表移除但磁盘文件未删；存量 INI 的 LA_POSE2_MM 旧键仍留在 Preset 文件（运行时一次性迁移读它后停写）

## [2026-11-19 15:07:04] refactor | WeldParamChangeLogger → ConfigChangeLogger 改名 + 读取按钮严格按 TabPage 生效（修三处越界）+ 代码精简（删 4 项死成员）
- 来源：AdaWeldSystem/ConfigFileControl/Implementations/{ConfigChangeLogger.cs（改名）,ConfigFileManager.cs,ConfigSnapshot.cs} + WeldParamControl/WeldParamManager.cs + UIDesign/TabPage/{ProcessControlPage.cs,SystemControlPage.cs} + MonitorCam/MonitorCamManager.cs + UIDesign/ControlPage/MainPage.cs + UIDesign/MainWindow/FormMain.cs + AdaWeldSystem.csproj（业主 2026-11-19 三要求：① 变更日志记录所有变更故重命名为 ConfigChangeLogger ② 查每个页面读取-修改-保存按钮是否只对本页面生效并保证之 ③ 注释精简后再做一次代码精简）
- 操作：
  1. Phase0 Query（三问检索：读取链路实测为四层 UI→Manager→配置类→ConfigFileManager；变更日志机制本就支持只记变动项但覆盖面仅焊参；UI 读改存三段式实测建立「按钮→属性→zone」四段映射矩阵，得出三处「读取」越界 + 零引用扫描 74 个事件处理器/3 个空壳/115 个 public 零调用方分类）；Phase1 Plan（业主裁定：严格按 TabPage 边界 + 先出零调用方分类清单再定）；Phase2 Code（改名：文件重命名 + 类名 + 7 处引用 + csproj 同步 + 残留 0；读取按钮改造：LoadAlgorithmsZone 复活为 params 多 zone 重载 + 先 Reload 再读 + 写回现有对象不 new 不替换；三个读取按钮改刷本 TabPage zone 且移除跨 TabPage 回填；代码精简：删 MonitorCamManager.SensorStop（空壳+零调用）、ConfigFileManager.SaveWithAudit 与 SaveXml（自造未用 API）、MainPage.AddNewDataLineChart（空壳）+ FormMain 调用点）；Phase3 Ingest（ADR-076 决策 D9 含三处越界表+两缺陷+TabPage↔zone 对照表 + 新建 lessons/UiButtonZoneBoundary + api/ProcessControlPage + api/SystemControlPage + api/ConfigFileManager 改名同步 + CodeMap 改名与职责）；Phase4 Lint（8 闸门 + 真编译 + 19 项自检 + 死代码复扫 + 字节安全）
- 变更文件：AdaWeldSystem/ConfigFileControl/Implementations/ConfigChangeLogger.cs; AdaWeldSystem/ConfigFileControl/Implementations/ConfigFileManager.cs; AdaWeldSystem/ConfigFileControl/Implementations/ConfigSnapshot.cs; AdaWeldSystem/WeldParamControl/WeldParamManager.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; AdaWeldSystem/MonitorCam/MonitorCamManager.cs; AdaWeldSystem/UIDesign/ControlPage/MainPage.cs; AdaWeldSystem/UIDesign/MainWindow/FormMain.cs; AdaWeldSystem/AdaWeldSystem.csproj; LLMWiki/wiki/decisions/ADR-076-SettingsZoneSaveWiring.md; LLMWiki/wiki/lessons/UiButtonZoneBoundary.md; LLMWiki/wiki/api/ProcessControlPage.md; LLMWiki/wiki/api/SystemControlPage.md; LLMWiki/wiki/api/ConfigFileManager.md; LLMWiki/wiki/architecture/CodeMap-Files.md
- 结论 / 遗留：真编译 errors=0 rc=0；静态守卫 files=175 fail=0 PASS；8 闸门全过；19 项自检全通过；字节安全 vs backup 基线零变化。关键结论：① 改名 —— WeldParamChangeLogger → ConfigChangeLogger（它现记录所有配置变更，焊参专用依赖已解除，旧名名不副实）；② 读取按钮边界 —— 实测三处越界：三个「读取」都调 LoadAlgorithmsConfig()（全量 5 区 + new 对象替换 _algorithmsConfig ⇒ 其它 TabPage 未保存的内存改动被整体丢弃），且每页顺带回填别的 TabPage 控件（LoadFlowSwitchOnForm / LoadProcessEnableOnForm 被两页互用）；正解 = LoadAlgorithmsZone 复活为 params 多 zone 重载（先 Reload 载体 ⇒ 读磁盘真值；只读指定 zone；写回现有对象不 new 不替换）+ 三按钮只刷本 TabPage zone 并移除跨 TabPage 回填（被移走的控件由页面构造时的批量回填负责）；⛔ 写路径本就正确（SaveZoneIni 先 Reload 再只写本区键 = 键级隔离），「修改」「保存」两按钮原本就只写本区故未改；③ 代码精简 —— 零调用 public 115 个分类清单：未启用通道 9（PLC/Modbus）+ 预留 API 4 + 接口覆写契约 85 + 待甄别 17；按「删确认无用的、预留 API 保留」只删 4 项（MonitorCamManager.SensorStop 空壳+零调用、ConfigFileManager.SaveWithAudit 与 SaveXml 上轮自造未用 API、MainPage.AddNewDataLineChart 空壳+调用点）；保留 ImageAlgorithm 7 个算法库工具、PermissionLevel.GetDutyText/SetLevel、ConfigBackupHelper.BackupDirectory、RenderConfig.GetAlgorithmName/ResetToDefaults、KukaRsiComm.SaveRSIConfig、PointCloudReader.LoadFromPlyWithAssimp（均为合理公开能力）；⛔ radioModeRSI_CheckedChanged 虽空壳但 Designer 有反射订阅 ⇒ 删了编译不过，保留。遗留：现场配置需重新填一遍（业主已确认）；通讯 8 个 XML 未合并（按 RSI 语义分层保留）；6 个孤儿配置文件全仓零引用已从迁移表移除但磁盘文件未删；存量 INI 的 LA_POSE2_MM 旧键仍留在 Preset 文件（运行时一次性迁移读它后停写）

## [2026-11-19 14:21:26] refactor | 全库注释瘦身（remarks 一律移除 + summary 只记作用 ≤20 字）+ 配置变更审计下沉到 ConfigFileManager（载体快照，只记变动项）
- 来源：AdaWeldSystem/ 全库 173 个 .cs（注释）+ ConfigFileControl/Implementations/{ConfigSnapshot,ConfigFileManager,WeldParamChangeLogger}.cs（新建/改造）+ WeldParamControl/WeldParamProfileAudit.cs（新建）+ 10 个配置类的保存入口接入审计 + Vicoding管理平台/LLMWiki/scripts/simplify_strip_docs.py（新建工具）
- 操作：
  1. Phase0 Query（CodeMap 定位配置领域；三问检索：三层读取链路实测为四层（UI→Manager→配置类→ConfigFileManager，配置类夹在中间承载「配置项↔文件键」映射）；变更日志机制实测 LogObjectDiff 已是逐项 diff 但只服务焊参、仅 4 处调用；UI 按钮读写分派实测两页各一套「读取/修改/保存」三段式）；Phase1 Plan（业主三裁定：全库 1137 处全清 / 变更日志下沉到 ConfigFileManager 统一钩子 / 修「修改参数写了但保存只落 ①System 区」）；Phase2 Code（C 组：新增 scripts/simplify_strip_docs.py（删 remarks + 压 summary + 复用 simplify_guard 守卫 + 逐文件快照回滚）→ 副本目录试跑 → 四道校验 → 源目录执行 1137 处全清 595 处压缩；A1：WeldParamChangeLogger 通用化（Tag 可传、解除 WeldAutoParamProfile/Newtonsoft 依赖）+ LogProfileDiff 迁至 WeldParamProfileAudit；A2：新增 ConfigSnapshot（磁盘态快照 + Diff 只记变动项）+ ConfigFileManager 加 SaveIniWithAudit/SaveXmlWithAudit/SaveIni/SaveXml；A3：10 个配置类保存入口接入审计（线激光/监控相机/焊接头/运动控制/视觉ROI/渲染/仿真/视觉算法/通讯设置 9 处+TA曲线/焊参区）；XmlConfigFile 修文件名重复拼扩展名（TaLaCurve.xml.xml））；Phase3 Ingest（ADR-007 追加 D2 + standards/CodeSimplification 同步（remarks 一律移除 + 判据表 +2 行）+ 新建 lessons/CommentStripToolchain + 新建 api/ConfigSnapshot + api/ConfigFileManager 补审计钩子 + CodeMap 6 处行数 2 处职责 2 条新条目）；Phase4 Lint（8 闸门 + 真编译 + 35 项自检 + 四道校验 + 字节安全）
- 变更文件：AdaWeldSystem/ConfigFileControl/Implementations/ConfigSnapshot.cs; AdaWeldSystem/ConfigFileControl/Implementations/ConfigFileManager.cs; AdaWeldSystem/ConfigFileControl/Implementations/WeldParamChangeLogger.cs; AdaWeldSystem/ConfigFileControl/Implementations/XmlConfigFile.cs; AdaWeldSystem/WeldParamControl/WeldParamProfileAudit.cs; AdaWeldSystem/WeldParamControl/WeldParamManager.cs; AdaWeldSystem/LineLaserCam/LineLaserConfig.cs; AdaWeldSystem/MonitorCam/MonitorCamConfig.cs; AdaWeldSystem/MotionControl/MontionManager.cs; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs; AdaWeldSystem/EmguALG/Roi/ImageRoiTool.cs; AdaWeldSystem/EmguALG/Manager/AlgorithmManager.cs; AdaWeldSystem/PCLOperate/Render/RenderConfig.cs; AdaWeldSystem/MainDeviceControl/SimulationConfig.cs; AdaWeldSystem/Comm/Communication/CommunicationManager.cs; AdaWeldSystem/WeldParamControl/Curves/TaLaCurveConfig.cs; AdaWeldSystem/AdaWeldSystem.csproj; AdaWeldSystem/ 全库 173 个 .cs（注释精简）; Vicoding管理平台/LLMWiki/scripts/simplify_strip_docs.py; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-007-CodeSimplificationStandard.md; Vicoding管理平台/LLMWiki/wiki/standards/CodeSimplification.md; Vicoding管理平台/LLMWiki/wiki/lessons/CommentStripToolchain.md; Vicoding管理平台/LLMWiki/wiki/api/ConfigSnapshot.md; Vicoding管理平台/LLMWiki/wiki/api/ConfigFileManager.md; Vicoding管理平台/LLMWiki/wiki/architecture/CodeMap-Files.md
- 结论 / 遗留：真编译 errors=0 rc=0；静态守卫 files=175 fail=0 PASS；8 闸门全过；35 项自检全通过；字节安全 vs 本轮 backup 基线 173 文件行尾/BOM 零变化。关键结论与修正：① 业主问「应用层读各 manager 配置、manager 读配置走 configfilemanager」的理解基本正确，但实测是四层而非三层 —— 配置类（LineLaserConfig/DeltaMotionConfig/WeldParamConfig 等 10 个）夹在 Manager 与 ConfigFileManager 之间，承载「配置项 ↔ 文件键」的映射语义，ConfigFileManager 只提供载体与路径，不懂业务项；② 变更日志机制本就支持「只记变动项」（IsChanged 逐项过滤），缺口在覆盖面与位置 —— 本轮下沉为 ConfigFileManager 的载体快照钩子（SaveIniWithAudit/SaveXmlWithAudit），10 个配置类保存入口全部接入，Tag 可传（默认「配置变更」）；③ 关键正确性判据：快照必须取磁盘态而非载体内存态，否则写入已先于快照发生 ⇒ diff 检不出变更；④ ⚠️ B 组前提被实测推翻：BtnApplyParams 改写的 29 个属性经属性→zone 映射实测全部属 System 区，BtnSaveLocal 落 System 区是正确的，各页「改→存」分区闭环无缺口，本轮未改该处代码；⑤ C 组口径：remarks 一律移除、summary 只记作用 ≤20 字一字、余文直接删除不迁移（承载方是 CodeMap 与 wiki）；⑥ 批量工具链四个坑已入库 lessons/CommentStripToolchain（行尾基线须用 backup 包而非 git show HEAD、读写两侧归一化行尾、自闭合标签排除配对、逐文件独立读写禁跨脚本共享 cache）。遗留：① 现场配置需重新填一遍（业主已确认）；② 通讯 8 个 XML 未合并（按 RSI 语义分层保留，待业主裁定）；③ 6 个孤儿配置文件全仓零引用已从迁移表移除但磁盘文件未删；④ 存量 INI 的 LA_POSE2_MM 旧键仍留在 Preset 文件（运行时一次性迁移读它后停写）

## [2026-11-19 13:22:14] refactor | 配置收归后全量核查：Manager 载体清零验证 + 迁移完整性核对 + 死代码/过期注释清理（8 项修复）
- 来源：AdaWeldSystem/MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs + DeviceWorkflow/*.cs（5 个 workflow）+ MotionControl/MontionManager.cs + UIDesign/TabPage/ProcessControlPage.cs + UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs + WeldParamControl/WeldParamConfig.cs + FileOperate/ConfigPathMigrator.cs（业主 2026-11-19 三问：① 8 个通讯 XML 按 RSI 模式判断是否合并 ② 路径是否有需清理的 ③ 配置迁移大动作后的三项核查：各 Manager 是否还重复持有配置/参数修改记录、迁移是否完全是否缺配置项、涉及文件代码精简检测）
- 操作：
  1. Phase0 检索（RSI 通讯模式实测：4 个通讯实现类 EthernetXmlComm/InLaserModbusComm/KukaRsiComm/SiemensS7Comm；8 个 Xdoc 消费方逐个追踪 —— RobotServerXdoc 是 RSI 核心（IP/PORT/HOST_IP/HOST_PORT/SENTYPE/CYCLE + RSI 格式节），Server/Client/Send/Recive 仅 UI 文件编辑器用，RobotClient/Plc/Modbus 零消费方；PLC 与 Modbus 启用条件为「IP+Rack+Slot / IP+PORT 非空」且用户明确无 PLC、Modbus 未启用）；Phase1 Plan（8 项修复 F1-F8）；Phase2 Code（F1 删 ConfigRelativeDir 死属性 + F2 workflow 配置改按 ConfigModule 走 ConfigFileManager + F3 删 InstructionTorqueConfirmSamples 零引用常量 + F4 删 LoadParamOutOnForm 空壳方法及 3 处调用 + F5 删 Adapt 区已废旧键 IS_COUNT_TYPE/COUNT_NUM 读取与常量 + F6 修 WeldParamConfig 类注释旧路径 + F7 ConfigPathMigrator 补 5 条 workflow 配置路径 + F8 删 7 个孤儿配置文件与 3 个空目录）；Phase3 Ingest（ADR-006 D2 追加核查结论 + 新建 lessons/RefactorPostChecklist + CodeMap 更新）；Phase4 Lint（8 闸门 + 真编译 + 静态守卫 + 三项检查复核）
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LineLaserWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs; AdaWeldSystem/MotionControl/MontionManager.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; AdaWeldSystem/UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs; AdaWeldSystem/WeldParamControl/WeldParamConfig.cs; AdaWeldSystem/FileOperate/ConfigPathMigrator.cs; LLMWiki/wiki/decisions/ADR-006-ModuleOrganizationPatternStandard.md; LLMWiki/wiki/lessons/RefactorPostChecklist.md; LLMWiki/wiki/architecture/CodeMap-Files.md
- 结论 / 遗留：真编译 errors=0 rc=0；静态守卫 files=173 fail=0 PASS；8 闸门全过。核查结论三项：① 各 Manager 载体持有 —— LineLaser/MonitorCam/Montion/Algorithm/Communication/WeldParam 六个 Manager 正式载体全部为 0（CommunicationManager 的 8 个 Xdoc 成员来自 ConfigFileManager；WeldParamManager 残留 1 处 INI + 1 处 Xdoc 均为补键模板的临时载体）；ProductFileRecordManager 保留 2 处（Records 按业主裁定不变）；参数修改记录 WeldParamChangeLogger 仅 WeldParamManager 一处调用 4 次（已迁 ConfigFileControl 模块）。② 迁移完整性 —— WeldParamConfig 五个区域的实际读写键数与区域声明键清单逐项比对全部一致（Adapt 4→2 修掉已废旧键、Flow 5、Preset 12、Quick 1、System 19）；57 个 public 属性中 6 个未落盘（Name 属 ConfigRegion、其余 5 个是 PVT 回退路径明确不持久化）。③ 代码精简 —— 零引用私有成员 0、空壳方法 0（修掉 LoadParamOutOnForm）、注释率整体约 20%（新建的两个抽象接口 46~55% 属接口文档惯例）。本轮发现并修复 8 项：⭐ 真实缺口是 F1/F2 —— 收归后 5 个 workflow 的 ConfigRelativeDir override 仍指向旧目录使基类新默认值被 override 掉，且该属性在改造后已成死属性（无人读）⇒ workflow 配置根本没走 ConfigFileManager 且旧目录文件变孤儿；改为 ConfigModule 属性后 5 个 workflow 配置正确落到 Config\ConfigFileControl\<模块>\。路径清理：7 个孤儿配置文件全仓零引用已删（JobIndex.ini/Job_001.ini/IntelligentLaserJobParams.ilini/CameraPresets.ini/CameraSelector.ini/AlgorithmParams.ini/IntelligentLaser.ini）+ 3 个空目录（Jobs/LineLaser/Camera_INI/IntelligentLaserCam）。通讯结论（回答第一问）：RSI 模式下 RobotServer.xml 是唯一必需的本机通讯配置（含 RSI 格式节），Send/Recive/Server/Client 仅供 UI 文件编辑器查看、PLC.xml 与 Modbus.xml 因无 PLC 且 Modbus 未启用而未启用 ⇒ 不合并 8 个为一个（它们的语义层次不同：本机通讯参数 / UI 模板 / 机器人端部署件），但 RobotClient/Plc/Modbus 三个零消费方文件建议随未启用通道一并停用。遗留：① 现场配置仍需全部重填（业主已确认）；② 通讯 8 个 XML 未合并（按 RSI 语义分层保留，如需合并需业主裁定「本机通讯参数归一」）；③ RobotClient.xml / PLC.xml / Modbus.xml 三个零消费方文件已确认为未启用通道的产物，本轮只标注未删

## [2026-11-19 11:41:22] refactor | 新增 ConfigFileControl 模块（抽象+实现+ConfigFileManager）统一管理全局配置文档；WeldAlgorithmsConfig 改名 WeldParamConfig 并按 TabPage 分区域；10 个配置类载体收归；完全舍弃旧配置
- 来源：AdaWeldSystem/ConfigFileControl/（新建 6 文件）+ WeldParamControl/WeldParamConfig.cs（改名）+ WeldParamManager.cs + LineLaserCam/LineLaserConfig.cs + MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs + MotionControl/MontionManager.cs + MotionControl/WeldHeadSlaveDevice.cs + MonitorCam/MonitorCamConfig.cs + PCLOperate/Render/RenderConfig.cs + MainDeviceControl/SimulationConfig.cs + MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs + EmguALG/Manager/AlgorithmManager.cs + EmguALG/Roi/ImageRoiTool.cs + WeldParamControl/Curves/TaLaCurveConfig.cs + Comm/Communication/CommunicationManager.cs + FileOperate/ConfigPathMigrator.cs（业主 2026-11-19 裁定：① 新增文件夹 ConfigFileControl，按抽象/实现/ConfigFileManager 写，独立不由 WeldParamManager 管 ② DB 类与 Records 类不变 ③ 其余 Manager 不再管配置文件只应用参数 ④ 全局配置文档与目录由 ConfigFileManager 统一管 ⑤ 重构 WeldAlgorithmsConfig 与 WeldParamChangeLogger，WeldAlgorithmsConfig 改名 WeldParamConfig ⑥ WeldParamConfig 不再只管焊接算法，管所有的，内部按 tabpage 分区按区域读写 ⑦ 完全舍弃旧配置，生成默认值）
- 操作：
  1. Phase0 Query（8 个 Manager / 32 个配置文件 / 10 个配置类全量摸底；ADR-006 四件套范式 + ADR-005 命名空间规则 + ModuleOrganizationPattern H1~H11 硬规则核对；12 个 TabPage 全清单；6 个孤儿配置零读写方实证）；Phase1 Plan（业主三裁定：单一目录 ConfigFileControl/ + 完全舍弃旧配置 + 一轮全部收归；通讯按功能分类：本机 8 个 + 机器人端部署件 2 个）；Phase2 Code（S1 建模块骨架：抽象 IConfigFileProvider/IConfigRegion + 实现 IniConfigFile/XmlConfigFile/ConfigFileManager，csproj 注册 6 文件；S2 WeldAlgorithmsConfig→WeldParamConfig 改名（117 处 / 18 文件 + 文件重命名 + csproj 同步）；S3 区域模型：AlgorithmIniSet 换成 ConfigRegion + Regions 字典 + BuildRegions 落地 5 区域；载体改由 ConfigFileManager 提供；保存前 carrier.Reload() + 键级写入；补键模板加 WriteZoneIniTo/WriteConfigTo 写独立临时载体；S4 收归 10 个配置类 + DeviceWorkflowBase + WeldData.ini（31 处 new 载体收敛）；S5 清理：LA_POSE2_MM 全清（业主指出上轮漏删）+ 7 个死路径常量 + ConfigPathMigrator 迁移表指向新目录 + 旧根目录清理清单 + WeldParamChangeLogger 迁入新模块 + XML 死键清理）；S6 全量自检 + 路径一致性验证 + 区域隔离验证）；Phase3 Ingest（ADR-006 追加 D2 含六项判据 + 新建 lessons/ConfigOwnershipByManager + 新建 api/ConfigFileManager + api/WeldParamManager + CodeMap-Files 行数与职责 + 新模块 5 条条目）；Phase4 Lint（8 闸门 + 真编译 + 44 项自检 + 路径一致性验证 + 区域键级隔离验证 10 断言 + 字节安全核查）
- 变更文件：AdaWeldSystem/ConfigFileControl/Abstractions/IConfigFileProvider.cs; AdaWeldSystem/ConfigFileControl/Abstractions/IConfigRegion.cs; AdaWeldSystem/ConfigFileControl/Implementations/IniConfigFile.cs; AdaWeldSystem/ConfigFileControl/Implementations/XmlConfigFile.cs; AdaWeldSystem/ConfigFileControl/Implementations/ConfigFileManager.cs; AdaWeldSystem/ConfigFileControl/Implementations/WeldParamChangeLogger.cs; AdaWeldSystem/WeldParamControl/WeldParamConfig.cs; AdaWeldSystem/WeldParamControl/WeldParamManager.cs; AdaWeldSystem/LineLaserCam/LineLaserConfig.cs; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs; AdaWeldSystem/MotionControl/MontionManager.cs; AdaWeldSystem/MonitorCam/MonitorCamConfig.cs; AdaWeldSystem/PCLOperate/Render/RenderConfig.cs; AdaWeldSystem/MainDeviceControl/SimulationConfig.cs; AdaWeldSystem/MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs; AdaWeldSystem/EmguALG/Manager/AlgorithmManager.cs; AdaWeldSystem/EmguALG/Roi/ImageRoiTool.cs; AdaWeldSystem/WeldParamControl/Curves/TaLaCurveConfig.cs; AdaWeldSystem/Comm/Communication/CommunicationManager.cs; AdaWeldSystem/FileOperate/ConfigPathMigrator.cs; AdaWeldSystem/AdaWeldSystem.csproj; LLMWiki/wiki/decisions/ADR-006-ModuleOrganizationPatternStandard.md; LLMWiki/wiki/api/ConfigFileManager.md; LLMWiki/wiki/lessons/ConfigOwnershipByManager.md; LLMWiki/wiki/architecture/CodeMap-Files.md
- 结论 / 遗留：真编译 errors=0 rc=0；静态守卫 PASS；8 闸门全过；44 项自检全通过；路径一致性验证全通过（根目录常量 + 10 个模块常量 + 目标目录结构）；区域键级写入隔离验证 10 断言全通过。关键决策：① 新建 ConfigFileControl 模块（ADR-006 四件套 · 场景 B 无 Core）：抽象层 IConfigFileProvider/IConfigRegion + 实现层 IniConfigFile/XmlConfigFile/ConfigFileManager，全局根目录 Config\ConfigFileControl\；② 归属模型由「按 TabPage 分文件」纠正为「配置归 Manager 管、TabPage 只做区域划分」——上轮 4 个 TabPage 各一套 INI 的做法把 Manager 的配置所有权切碎了；③ 覆盖根因重新认定：不是文件数而是写入粒度（载体整文件重写 + 未涉及 section 取内存旧值）⇒ 正解是保存前 Reload + 只写本区域键（键级，因 PROCESS_CONTROL/SEAM_GUIDE 均被两个 TabPage 共用，section 粒度不够）；④ 完全舍弃旧配置：删 MigrateLegacyAlgorithmIni 全部迁移代码，新目录由 ConfigSelfHeal 按默认模板生成；⑤ 补键模板必须写独立临时载体（WriteZoneIniTo/WriteConfigTo），否则模板把默认值写进真实配置；⑥ DB/Records 按业主裁定不动（ProductFileRecordManager 保留自有载体）。遗留：① 现场所有配置需重新填一遍（业主已确认可接受，旧文件保留在磁盘但代码不再读）；② 通讯模块 10 个 XML 按功能分类（8 个本机 RSI 用 + 2 个机器人端部署件 WeldControlConfig/WeldControlSendFormat），本轮只收归读写器与路径、未合并文件（业主指示按功能分类，本机配置可由一个管理）；③ 6 个孤儿配置文件（IntelligentLaser.ini/CameraPresets.ini/CameraSelector.ini/JobIndex.ini/Job_001.ini/AlgorithmParams.ini）全仓零读写方，已从迁移表移除但磁盘文件未删；④ ConfigPathMigrator 仍保留（一次性把旧目录同名文件搬到新目录），如后续不再需要可整体删除

## [2026-11-19 10:33:40] refactor | INI 按 TabPage 逐项逐文件拆分（4 文件）+ 存量逐键迁移 + 4 个零引用死配置物理删除 + XML 死键清理
- 来源：AdaWeldSystem/WeldParamControl/WeldAlgorithmsConfig.cs + WeldParamManager.cs + UIDesign/TabPage/SystemControlPage.cs + FileOperate/ConfigPathMigrator.cs（业主 2026-11-19 裁定：① 完成逐项逐文件迁移 ② INI 拆到 4 个 TabPage 各一套 ③ 存量一次性逐键迁移、旧文件停读 ④ 删 4 个零引用死配置）
- 操作：
  1. Phase0 Query（四段映射脚本：配置项→控件→TabPage→(zone,载体,section)；实测推翻了 ADR-076 D6 方案表三处 —— ②Quick 的 5 个 Enable 开关实际在系统页·流程控制与测试（非工艺页）、同 zone 内部跨 TabPage、XML 只有一区拆不了；发现根因更深一层：INIFile.SaveToFile 是 File.WriteAllText 整文件重写 ⇒ INI 侧才是覆盖主战场；发现 4 个零引用死配置 LockSpotCalib/LockWirePos/SpotCalibPosMm/WireLockPosMm）；Phase1 Plan（业主三裁定：4 套 INI / 逐键迁移+旧文件停读 / 删死配置）；Phase2 Code（新增 AlgorithmsZone.Flow=4 区；WeldAlgorithmsConfig 新增 AlgorithmIniSet（FileFor 路由 + AllFiles 去重）；Load/SaveProcessIni 改按文件分组签名；SaveAlgorithmsZone 只落目标文件；Quick 区只剩 LOCK_Y_CALIB、新增 LoadZoneIniFlow/SaveZoneIniFlow；Manager 持 4 个 INI 读写器 + MigrateLegacyAlgorithmIni 逐键迁移（26 键迁移 + 36 键物理清理，幂等，先写目标落盘再删源键）；HealAlgorithmsConfigKeys 补键模板按文件分组；ConfigPathMigrator 加 3 条新路径；删 4 个死配置（属性+键常量+读写+默认赋值）；XML 死键 Y_AXIS_MIN_MM/Y_AXIS_MAX_MM 物理清理（新增 RemoveChild）；系统页 SaveProcessEnable 改走 Flow 区）；Phase3 Ingest（ADR-076 决策 D8 含 D6 方案表实测修正 + api/WeldParamManager + api/SystemControlPage + api/ProcessControlPage + CodeMap-Files 4 处行数 4 处职责 + 新建 lessons/ConfigFileSplitByTabPage）；Phase4 Lint（8 闸门 + 真编译 + 32 项自检 + 迁移逻辑验证 16 断言 + 核心诉求隔离验证 7 断言 + 字节安全核查）
- 变更文件：AdaWeldSystem/WeldParamControl/WeldAlgorithmsConfig.cs; AdaWeldSystem/WeldParamControl/WeldParamManager.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; AdaWeldSystem/FileOperate/ConfigPathMigrator.cs; LLMWiki/wiki/decisions/ADR-076-SettingsZoneSaveWiring.md; LLMWiki/wiki/api/WeldParamManager.md; LLMWiki/wiki/api/SystemControlPage.md; LLMWiki/wiki/api/ProcessControlPage.md; LLMWiki/wiki/architecture/CodeMap-Files.md; LLMWiki/wiki/lessons/ConfigFileSplitByTabPage.md
- 结论 / 遗留：真编译 errors=0 rc=0；静态守卫 files=168 fail=0 PASS；32 项自检全通过（1 项判据误报：ConfigPathMigrator 新路径行内出现 2 次而判据写 ==1）；迁移逻辑验证 16 断言全通过（副本目录、模拟存量、键分布 Trajectory 19/Adaptive 2/Flow 5/Preset 13、值保真 5 项逐值、幂等二次迁移 moved=0、空 section 自动清除对齐 INIFile.DeleteKey 删空节语义）；核心诉求隔离验证 7 断言全通过（拆分前「页B 保存覆盖页A 磁盘值」根因复现，拆分后页B 保存不触碰页A 文件）。关键决策：① 实测推翻 ADR-076 D6 方案表三处 ⇒ 新增 AlgorithmsZone.Flow 拆出系统页的 5 个 Enable 开关（原来与 ②Quick 混在同 zone 跨 TabPage）；② INI 由单文件拆 4 文件（工艺·激光工艺设置 / 工艺·自适应 / 系统·流程控制与测试 / 系统·轨迹跟踪），同名 section（PROCESS_CONTROL、SEAM_GUIDE）跨文件必须逐键迁移；③ 迁移源就是 Preset 文件本身（路径未变）—— 独立 legacy reader 会与 Preset reader 争用同一文件导致旧 section 被写回；④ 4 个零引用死配置物理删除；⑤ XML 死键 Y_AXIS_MIN_MM/Y_AXIS_MAX_MM 物理清理；⑥ 补键模板按文件分组（否则会把别页键补进本文件）。遗留：① 迁移后 Preset 文件只剩 PROCESS_CONTROL 一段，LA_POSE2_MM 旧键仍留在其中（运行时一次性迁移读它，迁完才停写）；② 轨迹跟踪 TabPage 的 19 项阈值在 Trajectory.ini，系统页该 TabPage 的「修改参数」按钮落 System 区、「保存参数」落 System 区，读取按钮亦然 —— 该 TabPage 独占该文件，跨页隔离成立；③ ConfigPathMigrator 为 3 个新文件加了旧目录映射，但旧目录下的同名文件内容是拆分前的单文件形态，迁移后仍需走一次逐键迁移逻辑（幂等）

## [2026-11-19 10:03:47] refactor | 代码地图改为机器生成（repomap 引擎 + 分片 + 调用边自研补齐）
- 来源：业主指令：codemap 不好用，改用 coderepomap 套 Claude Code Skill，并嵌入 skill 流程
- 操作：
  1. 安装官方 coderepomap 0.2.1（源码装，PyPI 未发布）并验证 C# 解析
  2. 新增 tools/codemap_build.py（官方引擎 + tree-sitter 全量成员 + 自研调用边 + 幂等生成）
  3. 产出 31 页代码地图（总览 + 符号分片 + 关系分片）入 wiki/architecture/
  4. 补齐官方缺口：public-only 过滤（47% 覆盖）→ 全量成员；零方法调用点 → 598 条高置信类型边 + 方法级低置信边
  5. 旧手写详表 CodeMap-Files.md 退役，6 处引用改指
  6. SKILL.md Step 0.0/2.5/3.6 接线并同步双副本
  7. 新建 ADR-108 + lessons/RepomapCSharpCallEdgeGap
- 变更文件：tools/codemap_build.py; tools/data/namespace_meta.json; wiki/architecture/CodeMap*.md; wiki/decisions/ADR-108-codemap-machine-generation.md; wiki/lessons/RepomapCSharpCallEdgeGap.md; skills/vibecoding-llmwiki/SKILL.md; wiki/project/vibecoding-workflow.md; AGENTS.md
- 结论 / 遗留：八闸门全绿（wiki_audit/wiki_format/ingest_purity_scan/lint_scan/drift_scan_precise/rules_check/skill_pointer_check/raw_asset_check）；重复度 0、孤儿仅剩退役页；生成器幂等（41 页 0 变更）；未改业务源码

## [2026-11-18 17:52:55] refactor | 跟踪几何项迁系统设置页标定参数区 + Y 轴行程上下限取消（限幅改接轴软限位）+ 配置文件按 TabPage 分割（第一步：XML 独占）
- 来源：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs + .Designer.cs + SystemControlPage.cs + .Designer.cs + MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs + MotionControl/MontionManager.cs + WeldParamControl/WeldAlgorithmsConfig.cs（业主 2026-11-18 裁定：① YT 设置下轴/激光比例系数、偏差方向、激光超前量、机器人Y补偿系数等跟踪几何项迁到系统设置页·轨迹跟踪·标定参数区 ② 取消 Y 轴行程上下限（Y 轴点击设置里已有）③ 配置文件按 tabpage 分割成不同文件）
- 操作：
  1. Phase0 Query（CodeMap 卡6；6 项控件定位 gridQuickTracking 行4-6；目标区 gridLaserCalib「线激光辅助参数/标定参数」；重复性核查：轴软限位 PositiveLimit/NegativeLimit 仅存储不下发、工艺侧 YAxisMin/MaxMm 是唯一限幅判据 ⇒ 判断不重复但配置两套并存）；Phase1 Plan（业主三裁定：限幅改接轴软限位 / 每 TabPage 一套文件 XML+INI / 本轮一并实施）；Phase2 Code（A 跨页搬 14 个控件（7 几何 + 标定中心Y/Z + 示教Y）+ 代码侧读写迁移 + 两容器行号重排；B 删 YAxisMin/MaxMm 六处 + 新增 GetAxisConfigByName 与 TryGetSeamAxisSoftLimit + ClampToStroke/ReportStrokeClamp 改接轴软限位 + 回归越界改判软限位；C-1 XML 侧 SEAM_GUIDE 几何 4 项由 ④Preset 区迁 ①System 区 ⇒ Load/SaveZoneXmlPreset 整体删除（section 名不变 ⇒ 存量零迁移）；C-2 标定项迁标定参数区 + 工艺页不再落 ①System 区 ⇒ XML 成轨迹跟踪 TabPage 独占）；Phase3 Ingest（ADR-076 决策 D6/D7 + api/ProcessControlPage + api/SystemControlPage + CodeMap-Files 5 处行数 4 处职责）；Phase4 Lint（8 闸门 + 真编译 + 16 项自检 + TLP 结构 + 字节安全）
- 变更文件：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.Designer.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MotionControl/MontionManager.cs; AdaWeldSystem/WeldParamControl/WeldAlgorithmsConfig.cs; LLMWiki/wiki/decisions/ADR-076-SettingsZoneSaveWiring.md; LLMWiki/wiki/api/ProcessControlPage.md; LLMWiki/wiki/api/SystemControlPage.md; LLMWiki/wiki/architecture/CodeMap-Files.md
- 结论 / 遗留：真编译 errors=0 rc=0；静态守卫 files=168 fail=0 PASS；16 项自检全通过（3 项为判据误报：lbl* 只在 Designer、YAxisMin/MaxMm 唯一残留是注释沿革）；10+ 个 TLP 结构 0 异常；字节安全 vs HEAD 全一致。关键结论：① 重复性核查=判断不重复但配置两套并存（轴软限位仅存储不下发，工艺侧是唯一限幅判据）② 限幅改接轴软限位后行为变化：原区间[-15,+15] ⇒ 现取轴软限位（现场实测正20/负-1，负值疑占位）⇒ 区间[-1,20]，需现场把 Y 轴正负软限位配成真实行程 ③ 根因：SaveAlgorithmsZone 只写自己 zone 但 SaveXdocument 重写整文件，未写 section 取内存旧值 ⇒ 另一页未保存的改动被覆盖；zone≠TabPage，跨页隔离必须物理分文件 ④ 本轮落地 XML 侧（几何 4 项归 ①System 区，section 名不变 ⇒ 存量零迁移）+ 工艺页不再落 System 区 ⇒ XML 成轨迹跟踪 TabPage 独占。遗留（下一轮）：INI 侧按 TabPage 拆文件（工艺设置页两个 TabPage 各自一套）+ LASER_CALIBRATION/SEAM_GUIDE 逐键迁移到第三个标定参数文件

## [2026-11-18 17:03:09] refactor | GA 默认长宽频清理（DefaultGalvo 拆 GalvoGlobalParams）+ LA_Pose2 → LA 默认焦平面（含初始化后回工作位）+ 死代码过期代码审查
- 来源：AdaWeldSystem/MotionControl/WeldHeadSlaveDevice.cs + MontionManager.cs + UIDesign/TabPage/ProcessControlPage.cs + .Designer.cs + SystemControlPage.cs + WeldParamControl/WeldAlgorithmsConfig.cs + MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs + MainDeviceControl/DeviceControlWork.cs（业主 2026-11-18 裁定：① GA 分档后未按图形区分的默认长宽频清理掉不再任何地方起作用 ② LA_Pose2 改为 LA_DefultFocus＝默认焦平面 LA 的位置 ③ 接入焊接头后初始化连接结束回该默认位置（LA 无轴 Home，此处回零＝回工作位）④ 审查大段改动产生的死代码与过期代码并精简）
- 操作：
  1. Phase0 Query（CodeMap 卡3/卡4/卡6；DefaultGalvo 消费面全量实测；LA 位置语义辨析 Spot=设光斑推算 vs Pose=直接移动；零引用扫描 179 候选全为事件处理器/单次调用）；Phase1 Plan（11 项改动 + 与业主确认默认焦平面是否自动引用）；Phase2 Code（DefaultGalvo 类型改 GalvoGlobalParams 物理删除图形与宽长频；新增 BuildGalvoParamsFor 组装下发；删镜像方案两方法；XML 顶层长宽频停写停读＋存量迁移；LA 全链路改名含 INI 旧键迁移；新增 MoveToDefaultFocus 并由 DeviceControlWork 初始化收尾主动调用；修 LoadConfig 过期注释）；Phase3 Ingest（ADR-070 §五 + ADR-067 演进记录 + api/ProcessControlPage + api/LaserWeldHeadWorkflow + api/SystemControlPage + CodeMap-Files 7 处行数 6 处职责 + 新建 lessons/PythonEditByteSafety）；Phase4 Lint（8 闸门 + 真编译 + 25 项自检 + 零引用复扫 + 字节安全核查）
- 变更文件：AdaWeldSystem/MotionControl/WeldHeadSlaveDevice.cs; AdaWeldSystem/MotionControl/MontionManager.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.Designer.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; AdaWeldSystem/WeldParamControl/WeldAlgorithmsConfig.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; LLMWiki/wiki/decisions/ADR-070-GalvoWeaveAsWidthSource.md; LLMWiki/wiki/decisions/ADR-067-LATaSettingsSemanticRework.md; LLMWiki/wiki/api/ProcessControlPage.md; LLMWiki/wiki/api/LaserWeldHeadWorkflow.md; LLMWiki/wiki/api/SystemControlPage.md; LLMWiki/wiki/architecture/CodeMap-Files.md; LLMWiki/wiki/lessons/PythonEditByteSafety.md
- 结论 / 遗留：真编译 errors=0 rc=0（VS18 Insiders 构建器 /t:Rebuild）；静态守卫 files=168 fail=0 PASS；25 项链路自检全通过；零引用私有成员复扫=0（无死成员）；字节安全 vs HEAD 复核 14 个 .cs 全一致（BOM＋CRLF）。关键决策：DefaultGalvo 拆为 GalvoGlobalParams（10 全局项）⇒ 默认长宽频物理删除而非标记弃用；振镜下发改 BuildGalvoParamsFor(pattern) 组装（全局项+图形档）；XML 顶层 GALVO/WIDTH|LENGTH|FREQUENCY 停写停读，老文件读一次作各档缺省值；LA 默认焦平面全链路改名且 INI 旧键 LA_POSE2_MM 一次性迁移后停写；MoveToDefaultFocus 由 DeviceControlWork 初始化收尾主动调用（⛔ 不在 workflow 构造期订阅 InitializationCompleted，否则构造期读 DeviceControlWork.Instance 触发整机初始化；⛔ 非阻塞下发不等到位；⛔ 不走手动门禁；不属 ADR-099 轴回零范畴）。遗留：① LaDefaultFocusMm 默认 0.0 ⇒ 未配置时初始化后自动就位跳过（现场示教后经 UI 保存才有值）；② 跨页/跨模块的 LA 就位状态未做 UI 显示同步；③ 本轮在 wiki 侧新建 lessons/PythonEditByteSafety（记录 Python 读写 .cs 的三坑：读不指定 newline 丢 CRLF、写用 utf-8-sig 误加 BOM、git show HEAD 路径须正斜杠否则核查脚本自身失效）

## [2026-11-18 16:03:11] refactor | GA 按图形分档 + 手动/自动两套模式 + ③自适应区删三项（ManualSeamWidthMm/SpotWidthGain/ParamOutputHz）
- 来源：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs + .Designer.cs + MotionControl/WeldHeadSlaveDevice.cs + MotionControl/MontionManager.cs + WeldParamControl/WeldAlgorithmsConfig.cs + WeldParamManager.cs + Algorithms/WeldParamAdjustmentAlgorithm.cs + Algorithms/WeldParamLookupAlgorithm.cs + MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs + WeldParamControlWorkflow.cs + LineLaserCam/VirtualCam/VirtualCam.cs（业主 2026-11-18 裁定：GA 图形按每种图形各存一档且未配置默认加载 Line；GA 设置即自适应无输出时的宽度；手动/自动两套模式互斥；输出频率改用段落长度）
- 操作：
  1. Phase0 Query（CodeMap 卡3/卡4/卡6；EnableGalvoWeave 与 DefaultGalvo 消费面实测；ADR 门禁命中 ADR-070/076/103 走合并路径；lessons 查重）；Phase1 Plan（9 项任务 + 4 项裁定 Q1-Q8）；Phase2 Code（删 GalvoDemo 改 GalvoManualStart/GalvoManualStop；删 SpotWidthGain 含查表 3 处乘算与 RefreshSpotWidthDic/RefreshSpotWidthByGain 四链；删 ManualSeamWidthMm 且 Manual 源宽度改取 GA 档 ManualFixedWidthMm；删 ParamOutputHz 且 TickXlOutput 时间维节流改距离维复用 SegmentDistanceMm；GA 宽长频按图形分 4 档含 GalvoShapeParams/GalvoShapePresets/GetGalvoShape/XML 4 组子节点与存量迁移；新增 GA 手动下发/关闭退出按钮组；删 GA 卡手动宽度与轨迹点区 3 个输出控件；VirtualCam 基准宽度改 const；DefaultGalvo 镜像当前档 SyncDefaultGalvoFromShape）；Phase3 Ingest（ADR-070 演进节 + ADR-076 决策 D5 + ADR-103 落地演进 + api/ProcessControlPage + api/LaserWeldHeadWorkflow + CodeMap-Files 9 处职责与 10 处行数 + 新建 lessons/ConfigKeyRemovalAndTruthSourceMigration）；Phase4 Lint（8 闸门 + 真编译 + 22 项链路自检）
- 变更文件：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.Designer.cs; AdaWeldSystem/MotionControl/WeldHeadSlaveDevice.cs; AdaWeldSystem/MotionControl/MontionManager.cs; AdaWeldSystem/WeldParamControl/WeldAlgorithmsConfig.cs; AdaWeldSystem/WeldParamControl/WeldParamManager.cs; AdaWeldSystem/WeldParamControl/Algorithms/WeldParamAdjustmentAlgorithm.cs; AdaWeldSystem/WeldParamControl/Algorithms/WeldParamLookupAlgorithm.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/WeldParamControlWorkflow.cs; AdaWeldSystem/LineLaserCam/VirtualCam/VirtualCam.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; LLMWiki/wiki/decisions/ADR-070-GalvoWeaveAsWidthSource.md; LLMWiki/wiki/decisions/ADR-076-SettingsZoneSaveWiring.md; LLMWiki/wiki/decisions/ADR-103-no-value-hold-and-distance-segment.md; LLMWiki/wiki/api/ProcessControlPage.md; LLMWiki/wiki/api/LaserWeldHeadWorkflow.md; LLMWiki/wiki/architecture/CodeMap-Files.md; LLMWiki/wiki/lessons/ConfigKeyRemovalAndTruthSourceMigration.md
- 结论 / 遗留：真编译 errors=0 rc=0（VS18 Insiders 构建器 /t:Rebuild）；静态守卫 files=168 fail=0 PASS；22 项链路自检全通过；字节安全复核（7 个文件行尾 CRLF 化 + 5 个文件 BOM 还原 + 2 个 wiki 文件 BOM 还原）。关键决策：GA 宽长频按图形分 4 档（缺档回退 Line 档），DefaultGalvo 改为当前生效参数集合并由 SyncDefaultGalvoFromShape 镜像当前档（修复整体下发刷陈旧旧值的缺口）；输出触发改按段落长度复用 SegmentDistanceMm（不新增变量，_lastXlOutputTick 被 _lastXlOutputRobotX 替换）；手动下发走 EnsureManualWeldHeadActionAllowed 互斥，UI 置灰 laReady && !IsAutoWeldingRunning 且不按振镜启用态禁用。事故与遗留：① 本轮中途 git checkout 覆盖了业主的 Designer 改动，已用可重放脚本从 HEAD 基线重建（11 控件删除 + label7/label8 新增 + tableLayoutPanel2 改名 tlPLASetting + gridQuickLa 布局重排 + 三个 TLP 行数调整），机检 10 个 TLP 结构 0 异常，但 TabIndex/Location 等初值可能与业主原版有细微差异，需业主在 VS 中目视确认；② 存量 WeldHeadSlave.xml 只有顶层单档时，迁移会把旧单档值灌进 4 个档（现场需确认是否符合预期）；③ 手动下发为输出一次语义，改参数后需再点一次；④ GA 手动按钮的置灰随 RefreshActionStates 刷新，自动焊接开始/结束未加事件即时刷新（点击时门禁为主防线）。

## [2026-11-18 13:30:41] fix | 振镜图形语义修正（以振镜启用态为前提）+ 系统设置页 Designer decimal? 赋值修复
- 来源：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs + MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs + UIDesign/TabPage/SystemControlPage.Designer.cs（业主 2026-11-18 补充裁定：未开启振镜自动运行=没有图形；启用了必须有一个图形，有设置用设置，没有则落回默认 Line；并报系统设置页 Designer 报错 Int32→Nullable<Decimal>）
- 操作：
  1. Phase0 Query（CodeMap 卡3/卡4/卡6；EnableGalvoWeave 链路实测；ADR-076 D3；lessons UiModuleRemovalCleanup 坑六/坑七）；Phase1 Plan（语义三层：配置/UI选态/设备下发 + 跨页启用态实时读）；Phase2 Code（UI 按启用态分支：未启用清空选中+整组置灰，已启用必有图形无设置落回 Line 并落盘；新增 LaserWeldHeadWorkflow.IsGalvoWeaveEnabled 实时读；删过期快照字段 _galvoWeaveEnabled；Designer numWeldHeadNode Maximum/Minimum/Value 加 M 后缀）；Phase3 Ingest（ADR-076 D4 + api/ProcessControlPage + api/LaserWeldHeadWorkflow + CodeMap-Files + lessons 坑七补充/坑八新增）；Phase4 Lint（8 闸门 + 真编译）
- 变更文件：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs; LLMWiki/wiki/decisions/ADR-076-SettingsZoneSaveWiring.md; LLMWiki/wiki/api/ProcessControlPage.md; LLMWiki/wiki/api/LaserWeldHeadWorkflow.md; LLMWiki/wiki/architecture/CodeMap-Files.md; LLMWiki/wiki/lessons/UiModuleRemovalCleanup.md
- 结论 / 遗留：真编译 errors=0 rc=0（VS18 Insiders 构建器 /t:Rebuild）；静态守卫 files=168 fail=0 PASS；Designer 报错根因=AntdUI InputNumber 的 Minimum/Maximum 为 decimal?，int 无隐式转换（int→decimal 有，故 Value 安全）⇒ 补 M 后缀；全库机检 decimal? 属性裸字面量 0 处。语义修正：未启用振镜⇒没有图形（清选中+整组置灰，物理上摆幅 0 不使能）；已启用⇒必有图形（无设置落回 Line 并落盘）；删 workflow 的 LoadConfig 期快照 _galvoWeaveEnabled 改实时读配置（运行期改开关立即生效）。遗留：① 跨页联动依赖切回工艺设置页触发 ParamAutoPage_Shown 刷新（未加事件总线）；② LaserWeldHeadWorkflow.GalvoDemo() 仍无 UI 入口，API 保留待裁定

## [2026-11-18 11:55:56] refactor | GA 图形语义收敛（三层：配置 0=未设置 / UI 不预选 / 下发兜底直线）+ 冗余清理
- 来源：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs + WeldParamControl/WeldAlgorithmsConfig.cs + MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs（业主 2026-11-18 裁定：初始使用读取、未读到默认没有图形、图形始终以实际为准）
- 操作：
  1. Phase0 Query（CodeMap 卡3/卡4/卡6；ADR-076 D3 追加；lessons UiModuleRemovalCleanup 坑七）；Phase1 Plan（语义分三层：配置/UI选态/设备下发）；Phase2 Code（删 _syncingLaRadios + 字段 _galvoPatternSelected；RadioToGalvoPattern/GalvoPatternToRadio 的 default 返 null；配置初值 3→0；INI 越界归 0 + Warning；新增 LaserWeldHeadWorkflow.ResolveGalvoPattern 兜底协议非法值）；Phase3 Ingest（ADR-076 D3 + api/ProcessControlPage + api/LaserWeldHeadWorkflow + CodeMap-Files + lessons 坑七）；Phase4 Lint（8 闸门 + 真编译）
- 变更文件：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; AdaWeldSystem/WeldParamControl/WeldAlgorithmsConfig.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; LLMWiki/wiki/decisions/ADR-076-SettingsZoneSaveWiring.md; LLMWiki/wiki/api/ProcessControlPage.md; LLMWiki/wiki/api/LaserWeldHeadWorkflow.md; LLMWiki/wiki/architecture/CodeMap-Files.md; LLMWiki/wiki/lessons/UiModuleRemovalCleanup.md
- 结论 / 遗留：真编译 errors=0 rc=0（VS18 Insiders 构建器 /t:Rebuild）；静态守卫 files=168 fail=0 PASS；删 2 个冗余成员（_syncingLaRadios 被 _loadingGalvoUi 完全覆盖、_galvoPatternSelected 写后无读者）；三处静默兜底直线全部消除。遗留：① 存量 INI 无 GALVO_PATTERN 键时首次上机 GA 指令区无预选项，须手动选一次（符合业主裁定，属现场行为变化）；② LaserWeldHeadWorkflow.GalvoDemo() UI 侧唯一入口已删，API 保留待业主裁定

## [2026-11-18 10:34:58] fix | 工艺设置页 GA 设置区 4 控件删除后代码后置收敛 + 编译修复
- 来源：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs + .Designer.cs（业主 2026-11-18 删 selGalvoPattern/lblGalvoPattern/btnGalvoDemo/btnGalvoHome）
- 操作：
  1. Phase0 Query（CodeMap 卡6 + index 路由 + ADR-076/067/070/075 + lessons UiModuleRemovalCleanup/UiLayoutChangeSyncPitfalls）
  2. Phase1 Plan（只改 ProcessControlPage.cs，Designer 不动）
  3. Phase2 Code（删 selGalvoPattern_SelectedIndexChanged；SetGalvoPattern 去 Select 回写；删 btnGalvoDemo_Click/btnGalvoHome_Click；保留 _syncingLaRadios/_loadingGalvoUi/workflow 层 GalvoDemo/GalvoHome）
  4. Phase3 Ingest（api/ProcessControlPage + CodeMap-Files + lessons/UiModuleRemovalCleanup 坑六）
  5. Phase4 Lint（8 闸门）
- 变更文件：AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs; LLMWiki/wiki/api/ProcessControlPage.md; LLMWiki/wiki/architecture/CodeMap-Files.md; LLMWiki/wiki/lessons/UiModuleRemovalCleanup.md
- 结论 / 遗留：基线真编译 errors=2（CS0103 selGalvoPattern ×2）→ 修复后 errors=0 rc=0（VS18 Insiders 构建器 /t:Rebuild），exe 时间戳已刷新；静态守卫 files=168 fail=0 PASS；10 个 TableLayoutPanel 行列数与格位冲突机检 0 异常；workflow 层 GalvoDemo 保留（UI 唯一入口删但属公共 API，留待业主裁定）

## [2026-11-17 21:01:58] fix | 工具与全量资产纳入 git 管控（Vicoding 4 提交 + AdaWeldSystem 2 提交，双仓库未跟踪清零）
- 来源：业主指令「工具纳入管控」；实际排查发现范围远超工具：Vicoding 仓库 209 项未跟踪（含 167 wiki 页 / 22 工具 / 7 脚本 / 8 raw / 4 logs），AdaWeldSystem 仓库 41 项未跟踪 + 143 项已修改未提交 —— 本轮两轮的核心代码改动（ProcessControlPage/SystemControlPage/MontionManager 等）全部不在版本控制内
- 操作：
  1. 提交前验证：csproj Compile 声明 193 项与磁盘 .cs 193 项完全一致（反斜杠路径导致的假阳性已排除）；真编译 Rebuild errors=0 rc=0；bin/obj/3rdDepend 未误纳入
- 变更文件：Vicoding管理平台/LLMWiki/tools/（29 个新跟踪）; Vicoding管理平台/LLMWiki/scripts/（7 个新跟踪）; Vicoding管理平台/LLMWiki/wiki/（313 文件变更）; Vicoding管理平台/LLMWiki/raw/（118 文件）; Vicoding管理平台/LLMWiki/logs/（23 文件）; Vicoding管理平台/.gitignore; Vicoding管理平台/LLMWiki/AGENTS.md; Vicoding管理平台/LLMWiki/skills/vibecoding-llmwiki/SKILL.md; AdaWeldSystem/（208 文件变更）; AdaWeldSystem/.gitignore
- 结论 / 遗留：终态：双仓库未跟踪 0 / 未提交 0；Vicoding 仓库 93MB，AdaWeldSystem 仓库 7.2MB。门禁复跑全绿：八闸门 exit=0（死链 0 / 孤儿 0 / ADR 冲突 0 / 外部链接失效 0 / 编号空洞 0，7 个废止留档号单列）；simplify_guard 168 文件 fail=0；simplify_selfcheck PASS。教训沉淀：① 判「删除是否丢内容」不能用逐字比对（承接是改写浓缩，逐字必假阴性）——须用 merged_from 关联 + 特征句检索 + 核心判据逐条落地三重证据；② 页面改名/拆分类重构的特征名会变（类名不同），判据须回落到「控件/成员是否保留」；③ .gitignore 须覆盖 output 定稿包（每轮 Phase 3 重新生成，不应入库）。遗留：① 本轮未做 git push（两仓库均在 main，本地已完整入库，推送与否待业主定）；② 仓库无 LFS，raw/delta 两份台达 PDF 共 17.2MB 直接入 blob，若后续 raw 资产继续增长需评估 LFS；③ 工作区根仍有 3 个 output 包（仓库外，未污染版本控制）

## [2026-11-17 18:49:07] fix | 治理工具常态化：新增 tools/adr_merge.py（整页合并助手 plan/apply/audit）+ WikiPageFormatSpec §3.1.3 合并路径契约 + lessons 两坑沉淀
- 来源：承接 ADR 治理轮：把一次性合并脚本沉淀为常态化工具，并把合并契约与两条新坑写入规范/教训页
- 操作：
  1. lessons/StaticVerifier-Batch-Script-Traps §四之十四 增两坑：坑⑦ 治理脚本写死绝对路径致「副本试跑」实际改了源目录（含 md5 前后比对断言与只读解锁要求）；坑⑧ 治理脚本非幂等致二次执行累积污染（表格行分隔符累积 / 空 blocks 仍插入 / 段落起点漂移三类根因）
- 变更文件：Vicoding管理平台/LLMWiki/tools/adr_merge.py; Vicoding管理平台/LLMWiki/wiki/standards/WikiPageFormatSpec.md; Vicoding管理平台/LLMWiki/wiki/lessons/StaticVerifier-Batch-Script-Traps.md
- 结论 / 遗留：工具验证（副本目录，源目录 md5 前后一致 = 零误改）：plan 零写盘 ✓ · apply 真实合并 99 页 + 三类残留引用 0 + 指针留档 1 行 ✓ · 幂等二次执行 0 变化 ✓ · wiki_format/wiki_audit/lint_scan/rules_check 四闸门 exit=0 ✓（wiki_format 唯一违规为 log 51 条超限，已 truncate 归档 1 条至 logs/backup/log_2026-11-10.md）。终态：八闸门全绿、死链 0、孤儿 0、ADR 编号冲突 0、外部链接失效 0、编号空洞 0（7 个废止留档号单列）、ADR 有效页 100。

## [2026-11-17 18:45:46] fix | ADR 库治理轮：相似度闸门止血 + 碎片合并 7 页 + 废弃清理 + 索引按主题族重排 + 引用与旧判据清零
- 来源：业主指令四项：① 加相似度阈值止血 ② 修 merge 截断 ③ 合并碎片重复、删除废弃 ④ index 处重新排序并检查 ADR 引用、不允许残留旧 ADR 判据（前置：2026-11-17 18:05 全库审计结论 = 无真重复，真问题是碎片化 + 合并机制形同虚设）
- 操作：
  1. 旧判据清零：全库指向已删页的 wikilink/裸号/相对路径链接均归零（此前 3 处相对路径链接漏改，已修正）；代码侧 DeltaAxisConfig.cs 的 ADR-090 注释改指 ADR-088；wiki_audit 的 ADR 判据修正（编号空洞须排除废止留档号；登记检查应查 ADR-Index 而非 index.md）
- 变更文件：Vicoding管理平台/LLMWiki/tools/adr_new.py; Vicoding管理平台/LLMWiki/tools/wiki_audit.py; Vicoding管理平台/LLMWiki/tools/wiki_index_build.py; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-Index.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-033-ConfigArchitectureStandard.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-075-LaserHeadUiControlConsistency.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-082-TaInitFourStepAndAvailability.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-084-TaForceToTorqueConversion.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-088-TaSharedTorqueLimit.md; Vicoding管理平台/LLMWiki/wiki/decisions/ADR-097-algorithm-layer-ownership-single-entry.md; Vicoding管理平台/LLMWiki/wiki/standards/WikiPageFormatSpec.md; Vicoding管理平台/LLMWiki/wiki/lessons/StaticVerifier-Batch-Script-Traps.md; Vicoding管理平台/LLMWiki/wiki/architecture/CodeMap.md; AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaAxisConfig.cs
- 结论 / 遗留：门禁：八闸门全绿（wiki_audit/lint_scan/drift_scan_precise/ingest_purity_scan/wiki_format/rules_check/skill_pointer_check/raw_asset_check 均 exit=0）；死链 0、孤儿 0、ADR 编号冲突 0、编号空洞 0（7 个废止留档号单列）；ADR 重复自检 100 页 4950 页对仅 1 对 ≥0.40（ADR-106↔107 共现仅 2 个文件名，实为不同子问题，提示级）。治理脚本阴性对照 4/4 通过（注入对照命中 ADR-088 J=0.857 拒绝 rc=2 + 全新主题放行 + 只读命令零副作用 + 决策号无 DD 前缀）。教训沉淀 2 条新坑（脚本写死绝对路径致副本试跑反改源目录 / 治理脚本非幂等致二次执行累积污染）。遗留：① 本轮只合并有明确自述取代关系的 7 组，其余同族页（如配置/键管理 11 页、状态机 9 页）落地实体不重叠，属主题相邻而非重复，未合；② ADR-089 指针行主题里保留了原页的删除线表述，后续可在标题列加「原页已删」以免与「已废弃」连读歧义；③ 合并执行脚本为一次性工具，落地后应把「承接 + 引用改写 + 索引重排」固化进 wiki_index_build 或新建 adr_merge.py 常态化入口

## [2026-11-17 18:23:19] fix | 焊接头节点号固定第三站 NodeId=2 + 节点号撞号校验 + UI 编辑入口
- 来源：现场日志 20261117_智能填丝焊接系统日志.log
- 操作：
  1. Phase0 检索 CodeMap/index/ADR-030/lessons
  2. Phase1 计划
  3. Phase2 改码 5 文件
  4. Phase2.6 静态校验 24 项通过 + 真编译 errors=0 rc=0
  5. Phase3 Ingest
- 变更文件：AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs, AdaWeldSystem/MotionControl/MontionManager.cs, AdaWeldSystem/MotionControl/DeltaEtherCAT/DeltaMontionControl.cs, AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs, AdaWeldSystem/UIDesign/TabPage/SystemControlPage.Designer.cs, AdaWeldSystem/bin/Debug/Config/MotionControl/Motion_XML/DeltaMotionConfig.xml
- 结论 / 遗留：根因: 焊接头 NODE_ID=0 与 Y 轴 NODE_ID=0 撞号, 握手 SDO 打到 Y 轴伺服读 0x2004 得 abort 0x1302; 教学页 lessons/NodeAddressCollision; ADR-030 演进记录 D030

## [2026-11-17 17:51:13] fix | 自动焊接禁 UI 手动操作 · TA_Zero 同口径要求已回零 · 指令区选中态与结果色一致 · 按钮禁用按电机分组
- 来源：业主现场反馈四项：① 焊接过程中设置界面手动操作都不允许（UI 动作一律手动模式，自动焊接中不可执行）② TA_Zero 与其它指令一样也须回零才能执行 ③ TA 指令区 radio 确认后选中态就变了，出现「TA_Zero 被选中、TA_Auto 是红色」的自相矛盾状态 ④ 按回零导致其它电机按钮也不可用（应各管各的）
- 操作：
  1. DeviceControlWork：新增 IsAutoWeldingRunning（线激光焊接过程态 ∈ PreWork/Working/Stopping）作手动动作唯一禁入判据；⛔ 不复用 IsWelding（覆盖整段开机期、过宽会连正常调试一起禁掉）
  2. MotionControlWorkflow：新增 AxisRejectAutoWelding；TryManualAxisOperation/TryMoveAxisToTarget/TryHomeAxisWithWait/TaExecute 增自动焊接禁入门禁（⛔ Stop/JogStop 永远放行）；ExecuteTaZeroPose 前置改 CheckTaAvailable（TA_Zero 同口径要求已回零）；删 CheckTaMotionReady 与「未回零只告警」块；GetTaGateReason 的 allowZeroPose 不再放宽
  3. LaserWeldHeadWorkflow：新增 EnsureManualWeldHeadActionAllowed 统一门禁，LaAuto/LaSpot1/LaSpot2/LaPose1/LaPose2/GalvoHome/GalvoDemo 全部接入；GalvoDemo 原用过宽的 IsWelding 判定一并改用该门禁
  4. ProcessControlPage：RunInstruction 链路改为「确认→门禁→单飞→执行→上色」（执行必须等用户点确定才生效）；门禁/单飞被拒保持当前选中态并标红 + 清同组旧底色；取消确认回退选中并复位自己底色；自动 TA_ZeroPose 不再抢用户选中态、不占指令区结果色；底色复位按容器作用域泛化到 Y/TA/LA/GA 四组；TA 门禁统一用 TaAvailable（含 TA_Zero）
  5. SystemControlPage：全局忙标志拆为 ManualOpGroup 四组独立标志（Trace/Ta/La/Galvo），一个电机的操作只禁用自己那组按钮；自动焊接中禁手动（_manualActionAllowed 由焊接状态事件驱动，⛔ 构造期不读 DeviceControlWork 单例避免触发主控初始化）
- 变更文件：AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs; AdaWeldSystem/MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs; AdaWeldSystem/UIDesign/TabPage/SystemControlPage.cs; AdaWeldSystem/UIDesign/TabPage/ProcessControlPage.cs
- 结论 / 遗留：真编译 Rebuild errors=0 rc=0 + simplify_guard 168 文件 fail=0。沉淀：按先合并后新建未新建 ADR —— ADR-100/082/063/075 各追加 2026-11-17 演进记录（D29~D32）；api/DeviceControlWork·MotionControlWorkflow·LaserWeldHeadWorkflow·SystemControlPage·ProcessControlPage 各追加改版段；lessons/TorqueModeAsUiGate（选中态与结果色必须是同一控件）与 UiRefreshUnifiedEntry（按钮管控作用域按设备隔离）各合并一条新坑；CodeMap 卡3/卡6 与 CodeMap-Files 同步；index 重建 165 条无重复。遗留：① 手动动作禁入的判据取焊接过程态 PreWork/Working/Stopping，是否还需把焊前准备段（对齐/光丝对中）纳入待业主确认；② 振镜按钮焊接中禁切换改由整机焊接状态事件驱动，焊接起止沿须现场验证；③ TA_Zero 现要求已回零 ⇒ 初始化后必须先回零才能用 TA 指令（含 TA_Zero），首台现场须确认操作顺序
