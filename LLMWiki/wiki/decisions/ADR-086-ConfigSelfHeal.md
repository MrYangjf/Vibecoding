---
title: ADR-086 配置自愈：缺键补写默认值 + 整文件缺失生成模板
date: 2026-11-05
updated: 2026-11-05
tags: [决策, 配置, 自愈, 幂等, 迁移]
status: accepted
---

# ADR-086 配置自愈：缺键补写默认值 + 整文件缺失生成模板

> **决策一句话**：所有权威配置加载入口统一经 `ConfigSelfHeal` 只增不改地补齐缺失键（整文件缺失生成完整默认模板），写前备份 + 临时文件原子替换 + 写后回读；预览/审计读一律零写盘。`TA_TORQUE_DIRECTION` 是唯一例外：加载期**不得**补默认 +1，必须等旧负值迁移判定后与其它缺键合并为**同一次**写盘。

## 背景

1. 多轮迭代后现场配置停留在旧版本，新键缺失时各配置类各自兜底：有的用字段默认、有的用方法内字面量、有的抛异常；排查只能靠日志猜。
2. 读取路径里已有隐式写盘（`XdocumentReaderWriter` / `INIFile` 构造时自动建空文件、`MonitorCamConfig` 缺文件即 `SaveToIni`、`CommunicationManager.Ensure*` 直接 `SaveXdocument`），预览读也会落盘，违反「只读预览」。
3. 本轮/上轮新增键（`TA_TORQUE_DIRECTION`、`TA_FORCE_100PCT_N`、`TA_HOME_ZERO_POSE_MM/VEL/TOL_MM`，以及入口迁移后的 `AXES/AXIS/TORQUE_SLOPE`）在旧配置首次启动时必须有确定行为，不能靠人工补文件。

## 决策

1. **D1 统一入口**：新增 `FileOperate\ConfigSelfHeal.cs`。INI 以「节 + 键 + 默认值」、XML 以「类自身 Save 产物作为模板镜像」对比真实文件；各配置类不得再复制补写代码。默认值只能来自字段初始化或类自身 Save 产物，**本类不内置业务字面量**。
2. **D2 只增不改**：仅当键/节点实际不存在时追加。INI 逐行保留原注释、空行与节顺序，缺键插在节内最后一条有效键之后；XML 用 `PreserveWhitespace` 加载，新节点插在同级末尾，保持节点顺序与缩进/换行风格。
3. **D3 幂等**：无缺键时**零写盘、零日志**；第二次启动不产生任何写操作，也不出现「配置补缺」日志。
4. **D4 写盘安全**：写前备份到既有 `Config\_backup\<时间戳>\`（复用 `ConfigBackupHelper`），临时文件 + `File.Replace`/`File.Move` 原子替换；只读/被占用时捕获异常、打 Warning、保留内存默认，**不阻断启动、不回滚既有内容**。
5. **D5 回读校验**：写后立即重新解析，缺键数必须为 0；失败只告警。
6. **D6 缺失文件**：整文件不存在时按模板生成完整默认文档，日志「配置缺失，已生成默认配置 <文件名>」；`App.config`/数据库不在此列。
7. **D7 只在权威路径写**：`LoadConfig(bool writeLog, bool allowHeal)` 的 `allowHeal` 显式区分；预览读、`FilebackupPage.LoadProjectXmlRows`、`ApplyDeltaView` 切视图、备份/校验读全部传 `false`。`XdocumentReaderWriter` 新增 `createIfMissing`，读取路径禁止隐式建文件。
8. **D8 方向键特例（执行顺序硬约束）**：
   - 加载期：`TA_TORQUE_DIRECTION` **已存在** → 可补其它缺键（一次写盘）；**缺省** → 整文件补缺全部推迟，绝不在加载期写入 +1。
   - 迁移期：`NormalizeTaForceDirection` 先只改内存（`<0` 且键缺 → `-1` + 绝对值；`>=0` 且键缺 → `+1`；键已存在 → 以键值为准并 Warning 提示双负号风险），随后 `MontionManager.EnsureMotionConfigKeys` 把「方向 + 其它缺键」合并为**一次**原子写盘。
   - 结果：同一进程最多一次写盘，绝不会出现「补键 +1 一次、迁移 -1 再一次」或方向被覆盖；第二次启动零写盘。
   - 迁移不再依赖 `IsInitialized`（只依赖已加载的配置），否则无硬件现场永远补不了缺键；旧 `TorqueTarget` 换算仍需轴实例，单独保留门禁。
   - **通则（2026-11-06 补充）**：凡「旧键 → 新键」的一次性迁移，**迁移必须写在补键之前**。补键会用默认值把新键写出来，之后迁移侧的「新键是否存在」判定恒为真，现场旧值会被误判为「已设定」而永久丢失。实例：`WeldParamManager.ReloadConfig` 的 `MigrateLegacyTaZeroPoseMm`（`TA_HOME/TA_HOME_ZERO_POSE_MM` → 工艺 INI `TA_ZERO_POSE_MM`）必须排在 `HealAlgorithmsConfigKeys` 之前；迁移只改内存，落盘交给随后的补键链路。
9. **D9 日志聚合**：单文件一条，形如「配置补缺 DeltaMotionConfig.xml：新增 3 键（TA_FORCE_100PCT_N=37、TA_HOME_ZERO_POSE_MM=0、TORQUE_SLOPE=100；来源 代码默认）」，逐键带默认值，超 8 项折叠计数。
10. **D10 现场现值不动**：补缺只针对不存在；`TA_FORCE_100PCT_N` 默认仍 37，规格书未到不改；不动 TaAvailable/ZeroPose、6098/6099/609A、换算公式。

## 备选方案

- **各配置类各写一套补丁**：被否 —— 十几个入口复制粘贴，备份/原子/回读/幂等必然走样。
- **加载时先补方向 +1，迁移再改 -1**：被否 —— 两次写盘，且补出的 +1 会被误判为「现场已设方向」，旧负数现场会悄悄翻向。
- **迁移里直接 `SaveTaHomeConfig` 全量重写**：被否 —— 与加载期补缺叠加会重复写盘，全量重写还会重排/改写无关键。
- **缺键抛异常强制人工处理**：被否 —— 现场停机成本高，与「程序不出错」诉求相反。

## 后果

### 正面
- 旧配置首次启动自动补齐新键并留一条聚合日志；二次启动零写盘。
- 预览/审计读不再隐式落盘；只读文件只告警。

### 负面 / 约束
- 期望键集依赖各类 `Save` 产物，新增键必须同时进 `Save` 路径，否则模板不含该键。
- XML 补缺按元素名（轴/IO/气缸按 `AXIS_NAME`/`IO_NAME`/`CYLINDER_NAME`）匹配，重名且无业务名的同级节点仍按首个匹配，需靠回读校验兜底。
