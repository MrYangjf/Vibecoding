---
title: ADR-080 台达扭矩回零 -3 统一走 Home_Config（U16 强转）；P1.087/P1.088 写入链路已废弃
date: 2026-11-04
updated: 2026-11-05
tags: [决策, 台达, EtherCAT, 回零, 扭矩, P1.087, P1.088, 补码, 废弃, 4869]
status: accepted
---

# ADR-080 台达扭矩回零 -3 统一走 Home_Config（U16 强转）；P1.087/P1.088 写入链路已废弃

> **决策一句话**：`Home_Config` 的 `Mode` 形参是 U16，负值只需按 16 位补码强转（`(ushort)(mode & 0xFFFF)`，`-2 = 65534`、`-3 = 65533`）；正负值**统一走 `Home_Config`**，原 CoE 6098 分支已删除。
> **2026-11-05 最终决断**：P1.087/P1.088 是**伺服参数**，由驱动器默认参数决定，控制器**不写、不读、不提供配置入口**；原写入链路（`ApplyTorqueHomeDriveParams` / `WriteAndVerifyServoParameter` / `WriteCoEObject` / `ReadCoEObject` / `WaitSdoDone` / `DescribeSdoAbort`）与「扭矩侦测」UI 区已整体删除，见下方「D6」。

## 背景

业主确认扭矩回零模式为 -3（16#6098 有符号，范围 -4~35），但 `CS_ECAT_Slave_Home_Config` 的 `Mode` 声明为 `ushort`，负值无法下发。
业主另提供写侦测参数接口截图（`raw/delta/台达_扭矩回零_写侦测参数接口_4.jpg`），要求核对项目 API 并让参数真正到达驱动器。
此前现状：`HomeMode` 为 ushort、TA 区仅 4 项回零参数、P1.087/P1.088 无写入通道、无法校验写入是否生效。

## 决策

1. `HomeMode` 改为 `short`，配置 XML / CSV 导入 / UI 校验全链支持 -4~35，负值即台达扭矩回零模式。
2. **正负值统一走 `Home_Config`**：`ToHomeModeWord(short) => (ushort)(mode & 0xFFFF)` 后直接传 `CS_ECAT_Slave_Home_Config`，再 `Home_Move`；日志打印「逻辑值 → 下发值」（如 `-3 → 65533`），写后 SDO 回读 16#6098 并按 `ToHomeModeLogical(byte)` 反解，打印「下发值 → 逻辑值」两端，回读失败只告警不阻断。
3. ~~P1.087/P1.088 用 `DeltaServo_Write_Parameter(Page=1, Index=87/88)` 写入，随即 `Read_Parameter` 回读比对~~ **2026-11-05 整体废弃**：两参数属伺服侧参数，改由驱动器默认值决定，控制器不写不读（见 D6）。
4. 参数落 `DeltaMotionConfig.TaHome`（独立节点 `ROOT/TA_HOME`，键 `TA_HOME_*`），不进 `WeldParamManager`；保存走 `MontionManager.SaveTaHomeConfig()`，落盘 + 推回运行期（~~下发 P1 参数；`StartHome` 前再补写一次 P1~~ **已删除**，D6）。
5. UI 只经 `MontionManager`，非法值中文拦截；速度按台达伺服 **rpm**、加速按 **ms** 直写（2026-11-04 手册修正）。TA 回零参数不再占用通用 AXIS 字段，Y 轴 AXIS 节点零改动。

## 2026-11-05 · 决策 D6 · P1.087/P1.088 写入链路整体删除（本项已废弃）

> **本项已废弃，勿再尝试 SDO 写 16#2157 / 16#2158。** 详表见 [[guides/DeltaEtherCAT-DevGuide]] §15.7。

| 项 | 结论 |
|---|---|
| 现场证据 | 写 `16#2157`（P1.087 侦测扭力准位）后回读失败：`SDO 读取发起返回 4869（）`；**4869 手册未收录/未确证**（本地两份台达手册与安装目录 20 份 PDF 均无该码），⛔ 不猜其官方含义 |
| 台达结论 | 口头：**「这两个是伺服参数，不需要控制器设置，用驱动器默认参数即可。」** |
| 业主口径 | **「这两参数直接丢掉，不要再写配置，删除这段设置。」** |
| 代码处置 | 删除 `ApplyTorqueHomeDriveParams` / `ApplyTorqueHomeParamsBeforeServoOn` / `WriteAndVerifyServoParameter` / `WriteCoEObject` / `ReadCoEObject` / `WaitSdoDone` / `DescribeSdoAbort` / `_torqueHomeCoEObjectMissing` 及 `ServoOn()`、`StartHome()` 调用；删除 `EtherCATMasterNative` 3 个 SDO P/Invoke（Grep 确认无其它调用方；`SDO_Quick_Send_Message`/`Check_Done` 因 `DeltaSlaveDevice` 在用而保留） |
| 配置/界面 | 删除 `DetectTorquePercent` / `StopArrivalMs`（含 `DeltaAxisConfig` 镜像）、`TA_HOME_DETECT_TORQUE` / `TA_HOME_STOP_ARRIVAL_MS` 读写、TA 弹窗「扭矩侦测」分区与两行校验、`SaveTaHomeConfig` 相关赋值、自愈模板项 |
| 旧配置兼容 | 现场 XML 残留四键 = **遗留键，不再生效**：加载忽略、不报错、不删除；`EnsureXml` 只增不改保留旧值；新生成模板不再出现 |
| 回零判据后果 | `-3` 的「扭力达阈值 + 持续到达时间」**完全由驱动器默认 P1.087/P1.088 决定**，控制器只下发 `Home_Config` + `Home_Move` + 观测 `Home_Status` |
| **现场已验证** | 2026-11-05 业主实测：**-3 扭矩回零正常（回零成功、table 有反馈）** ⇒ 删除**不造成功能损失**，默认参数对该机构够用；「控制器不写这两个伺服参数」为**最终决断**（依据 = 台达口头结论 + 现场实测） |
| 可追溯边界 | 若日后**机构或丝径变化**导致默认值不合适，需**在驱动器侧（ASDA Soft）调整**；控制器**不提供该配置入口**，项目不再新增该链路 |

> 由此产生的「待实机验证：-3 能否触发 / `Home_Status` 判据 / P1 回读一致性」**已全部闭环**；「ASDA-A3/B3 伺服手册缺失」保留记录但**不再阻塞本项**。

## 备选方案

- ~~负值走 CoE `SDO_Quick_Send` 写 16#6098/6099/609A~~：**已删除**。删除理由：①台达正式回复已确认 `Home_Config` 的 U16 形参由底层强转即可收负值，CoE 路径不再必要；②两条主路径并存会让「单位/字节序/顺序」两套实现长期漂移（6099/609A 曾各改一次）；③`Home_Config` 原生覆盖 6098/6099/609A + `Home_Move`，代码量更小且与正值同一条链路。回读仍保留 SDO 读 6098 做现场核对，属验证而非下发路径。
- ~~按厂商口述「-2 → 65533」统一编码~~：**未采纳**。该值与标准补码 `-2 → 65534` 差一位；台达后续正式回复已明确「负值就是强转 U16，`-2` 即 65534」，口述数值记为现场举例笔误（详见「负值编码最终裁决」）。
- **只做 UI、不发负值**：UI 允许填 -3 但底层置灰。未采纳——业主明确要求扭矩回零可用，等于拒绝需求。
- **P1 参数走通用 SDO 写**：用 `SDO_Quick_Send_Message` 直接写 16#2157/16#2158。未采纳——官方清单已导出专用 `DeltaServo_Write/Read_Parameter`，专用接口带页/索引语义，且能配对回读。**（2026-11-05 一并作废：P1.087/P1.088 整条链路已删除，改由驱动器默认参数决定，见 D6）**

## 后果

### 正面
- 扭矩回零 -3 可真正下发，不再受 `ushort` 限制。
- 写入后回读有据可查（日志含写入值/回读值/错误码），不依赖「业主判断自动生效」。
- 参数持久化在轴配置域，与 `TORQUE_MODE` 等同域，不污染工艺配置。

### 负面
- 负值依赖 `Home_Config` 底层形参强转；若某版 DLL 对 U16 做范围校验（>32767 拒绝），需回退 SDO 6098（本 ADR 已记录回退思路，但代码不保留双路径）。
- ~~P1.087/P1.088 的合法范围资料未给，UI 暂按 0~1000% / 0~60000ms 拦截，存在越界风险（已标注待确认）。~~ **2026-11-05 删链**：UI 字段与校验一并删除，不再存在越界入口（D6）。
- ~~未实机验证：无板卡时只能给静态链路与回读接口证据。~~ **已现场验证（2026-11-05）**：`-3` 扭矩回零正常（回零成功、table 有反馈）；控制器不写 P1.087/P1.088，由驱动器默认参数决定回零判据。
- P1.087/P1.088 无控制器侧配置入口（2026-11-05 删链）：换机构/换丝径时须在驱动器侧调整，控制器不参与。

## 负值编码最终裁决（2026-11-04，台达书面/口头确认）

> 冲突来源：现场台达人员早前口述「负号赋值转 16 位无符号赋值，譬如 -2 转 65533」。
> 最终口径：台达正式回复「API 那个回零模式的参数定义的数据类型是 16 位无符号，你输参数需要底下强制转一下类型」——即**标准 U16 强转，`-2` = 65534、`-3` = 65533**。

| 口径 | -1 | -2 | -3 | -4 | 结论 |
|---|---|---|---|---|---|
| 标准 16 位补码（**采纳**） | 65535 (0xFFFF) | **65534 (0xFFFE)** | **65533 (0xFFFD)** | 65532 (0xFFFC) | `65536 + mode`，台达确认即此规则 |
| 现场口述（**不采纳**） | — | 65533 | （未给） | — | 与 -3 补码值相同，判定为举例笔误 |

- **手册证据（两份官方 PDF 全文检索）**：`DELTA_IA-GMC_EtherCAT_PM_TC_20250428.pdf` 中 `6098` 仅 1 次（§12.1 P636，`Mode U16`，注明「請參考台達伺服驅動器的復歸模式說明」）；§12 说明表（P637-638）只列 1~35（15/16、31/32 保留），**无负值段、无补码换算示例**。`DELTA EtherCAT UserGuild.pdf`（59 页）`6098` 出现 0 次。台达安装目录（`D:\Program Files (x86)\Delta Industrial Automation\EtherCAT`，20 份 PDF）亦无 ASDA-A3/B3 伺服手册，故负值段语义**无手册正文可引**。
- **裁决依据**：以**厂商正式书面/口头确认**为准（U16 强转 + 标准补码），不再标「一位偏差待书面确认」；手册未覆盖负值段一事在 §15.1 保留说明。
- **实现**：`ToHomeModeWord()` 统一换算，保存、下发、回读反解同一规则；日志样例：`回零模式换算 逻辑 -3 → 下发值 65533（16 位 0xFFFD，单字节 0xFD）`、`回零模式回读 下发值 65533 → 反解逻辑 -3`。

## 手册依据与修正记录（2026-11-04）

> 依据：`raw/delta/DELTA_IA-GMC_EtherCAT_PM_TC_20250428.pdf`（官方，1018 页，2025-04-28；与安装目录 `manual\API` 同文件 SHA256 一致）。

| 项 | 手册结论（页码） | 对原决策的修正 |
|---|---|---|
| `Home_Config` Mode | `U16`，§12 只列 1~35（P635-638） | 负值段手册未覆盖，改由台达确认「U16 强转」，**统一 Home_Config** |
| `6099:01/02` 单位 | 台达伺服 **rpm**（P636） | ❌ 原按「工程单位/秒→ToPulse」换算 → ✅ 改为 rpm 直写 |
| `609A` 单位 | **ms**，0→3000rpm 时间（P636） | 一致，无需改 |
| `P1.087/088` | 手册全文无定义（P776-781）；安装目录亦无 ASDA 手册 | 仍「手册未覆盖」；范围 0~1000%/0~60000ms 保留并标注 |
| `6072` | 仅示例出现（P435） | 仍「手册未覆盖」 |
| `Home_Status` | 0/1/2/3 定义（P653） | ✅ 新增 status=3 拦截 |
| CST `Curve_Mode` | 1=直线（默认）/2=曲线（P630） | ✅ 常量 0 → 1 |
| CST `Target_Torque` / `Slope` | 千分比 1~1000 / 0.1%/秒（P630） | ✅ 与实现一致；现场 Slope=0 属非法 |
| 错误码 | 4609=参数错误（=0x1201）、4617~4621、5376/5377（P939-943） | ✅ 日志按码回原文；现场 4609 根因确认 |

## 实现落点（2026-11-04）

| 内容 | 文件 | 要点 |
|---|---|---|
| 回零统一下发 | `MotionControl/DeltaEtherCAT/DeltaMontionAxis.cs` | `StartHome()` 单路径 `Home_Config`；`VerifyHomeModeReadback()` 回读反解；删除 `WriteHomeConfigViaCoe`/`SdoQuickWrite*` |
| TA 参数组 | `MotionControl/DeltaEtherCAT/DeltaTaHomeConfig.cs` | 四参模型（模式/两档速度/加速；2026-11-05 删两 P1 属性）+ 默认值 + `CopyFrom/CopyTo` |
| 配置节点 | `MotionControl/DeltaEtherCAT/DeltaMotionConfig.cs` | `ROOT/TA_HOME`；缺节点从 TA AXIS seed；保存镜像回 TA 节点（Y 轴不碰） |
| 统一保存 | `MotionControl/MontionManager.cs` | `TaHomeConfig` 只读属性、`SaveTaHomeConfig()`、`ApplyTaAxisRuntimeConfig()` 以 TaHome 覆盖 |
| UI | `UIDesign/TabPage/SystemControlPage(.Designer).cs` | TA 表格化；`tableTa` 复用 `CreateAxisColumns()`；「参数」弹窗改共用 `AxisConfigForm`（通用区 + 特有区），保存走 `SaveTaHomeConfig` |

## TA 参数弹窗统一与字段归属（2026-11-04 业主口径修正）

> 业主修正原话：「我想让 Ta 的列表中的参数按钮与 Y 轴那个按钮一样，将用于配置 TA 电机的参数都列出来。逻辑是控制器默认装载 2 轴。其中一个轴是 TA 轴，将重新装载 TA 轴特有的参数。这个参数按钮将弹出显示 TA 轴所需要的所有配置。」

### 追加决策

6. **一个弹窗组件、两轴共用**：`AxisConfigForm` 增加 `(DeltaAxisConfig, DeltaTaHomeConfig)` 重载。传 `null` 即通用轴编辑（Y 轴路径**原样**：19 行、行序/标签/尺寸不变、无校验、解析失败保留原值）；传 `TaHome` 则追加「回零参数」「扭矩侦测」两个特有区，形成「通用区 + 轴特有区」两段式，不复制第二份窗口代码。**（2026-11-05 修订：删除「扭矩侦测」分区；现为「回零参数 / 工作零位 / 力—力矩换算 / 力矩输出」四段，TA 弹窗 29 行）**
7. **字段归属（唯一落点）**：

| 字段 | Y 轴有无 | TA 原弹窗有无 | TA 应有 | 落点 / 键名 |
|---|---|---|---|---|
| 轴名称 AxisName | ✓（只读） | ✗ | ✓（只读） | `AXIS/AXIS_NAME` |
| 站点号 NodeId / 槽号 SlotNo | ✓ | ✗ | ✓ | `AXIS/NODE_ID`、`SLOT_NO` |
| 启用 Enabled | ✓ | ✗ | ✓ | `AXIS/ENABLED` |
| 脉冲当量 Equiv | ✓ | ✗ | ✓ | `AXIS/EQUIV` |
| 起始/匀速/末速度 | ✓ | ✗ | ✓ | `STR_VEL`、`CONST_VEL`、`END_VEL` |
| 加速/减速/S 曲线时间 | ✓ | ✗ | ✓ | `ACC_TIME`、`DEC_TIME`、`S_TIME` |
| 回零模式 | ✓ | ✓ | ✓ | TA：`TA_HOME/TA_HOME_MODE`（Y：`AXIS/HOME_MODE`） |
| 原点偏移 | ✓ | ✗ | ✓ | `AXIS/HOME_OFFSET`（`TA_HOME` 无此键，唯一落 AXIS） |
| 寻找速度 / 爬行速度 / 回零加减速 | ✓ | ✓ | ✓ | TA：`TA_HOME_FIRST_VEL`、`TA_HOME_SECOND_VEL`、`TA_HOME_ACC` |
| ~~侦测扭力准位 P1.087~~ | ~~✗~~ | ✓ | **✗（2026-11-05 废弃）** | 遗留键 `TA_HOME_DETECT_TORQUE` / `HOME_DETECT_TORQUE`，**不再生效**，读写已删 |
| ~~停止位到达时间 P1.088~~ | ~~✗~~ | ✓ | **✗（2026-11-05 废弃）** | 遗留键 `TA_HOME_STOP_ARRIVAL_MS` / `HOME_STOP_ARRIVAL_MS`，**不再生效**，读写已删 |
| 正/负向软限位、软限位模式 | ✓ | ✗ | ✓ | `AXIS/POSITIVE_LIMIT`、`NEGATIVE_LIMIT`、`SOFT_LIMIT_MODE` |
| 力矩模式 `TORQUE_MODE` | ✓ | ✗ | ✗（不纳入） | 运行期状态位，由 `swTaTorqueMode` / 指令写入，弹窗编辑会造双真相源 |
| 力矩目标 `TORQUE_TARGET` | ✓ | ✗ | ✗（不纳入） | 已弃用（改由 `TaForceN` 推导），保留只为兼容旧文件 |
| 扭矩爬升速率 `TORQUE_SLOPE` | ✓ | ✗ | ✗（不纳入） | **2026-11-05 起由 TA 轴「参数」弹窗 `AxisConfigForm` 统一维护**（ADR-084） |

8. **重复键唯一化（本轮回应的双真相源问题）**：`AXES/AXIS[AXIS_NAME=送丝力矩电机]` 的 `HOME_*` 与 `TA_HOME/TA_HOME_*` 在保存后同值，确实存在两处落键。定位为：
   - `ROOT/TA_HOME` = **可编辑唯一真相源**（弹窗只写这里）；
   - TA 的 `AXIS/HOME_*` = **`SaveConfig` 从 TaHome 派生的镜像**，仅供 CSV 导出 / 文件备份页预览 / `ApplyAxisConfig` 兜底读取，弹窗不再直接编辑；
   - 兼容：旧文件无 `TA_HOME` → `LoadTaHome` 从 AXIS seed 一次（不丢现场参数），此后 AXIS 只被镜像写入；读取顺序固定「AXIS 兜底 → TaHome 覆盖」。
9. **装载链路**：`CreateAxesFromConfig` 对每轴 `ApplyAxisConfig` 后调用 `ApplyTaHomeOnLoad`——仅当 `cfg.AxisName == TA_AXIS_NAME` 且 `TaHome` 非空时覆盖回零四参（模式/两档速度/加速；2026-11-05 删 P1 两项）并打印日志；Y 轴轴名不匹配，读取路径零改动。缺 `TA_HOME` 时覆盖值与镜像值一致，现场参数不变。
10. **校验只在特有区启用**：`AxisConfigForm.Validate()` 在 TA 弹窗「确定」时先跑（中文逐项提示、失败零写入）；Y 轴单参构造路径不调用，保持原「解析失败保留旧值」行为。

### 实现落点补充

| 内容 | 文件 | 要点 |
|---|---|---|
| 共用弹窗 | `UIDesign/SubDialog/MotionControlDialog/AxisConfigForm.cs` | 双构造；`HasAxisSpecificSection`；`Validate()` 仅 TA 启用；`Commit()` 按落点分离写；布局由字体实测自适应（见下节） |
| UI 入口 | `UIDesign/TabPage/SystemControlPage.cs` | `TableTa_CellButtonClick → OpenTaAxisEditor()`；删除 `CreateParamInput/AddParamRow` 与旧 6 参弹窗 |
| 装载时重套 | `MotionControl/MontionManager.cs` | `ApplyTaHomeOnLoad()`；`TaAxisConfig` 只读入口 |
| 保存 | `MontionManager.SaveTaHomeConfig()` | 落盘（AXIS 通用区随 `Config` 实例一并写入 + TaHome 镜像）→ 推回运行期；生效时机 = 下次回零（~~下发 P1~~ 2026-11-05 删除，D6） |

### 弹窗布局约束（2026-11-04 业主截图反馈后追加）

11. **禁止写死弹窗尺寸与行高**：`Size`、`MinimumSize` 由「行数 × 实测行高 + 内边距 + 底部按钮」推导；行高 = `Font.Height + 14`（下限 30），分区标题行 + 6。字体统一 `微软雅黑 9F` + `AutoScaleMode.None`，随 DPI 由 `Font.Height` 自然放大。
12. **标签与输入框必须基线对齐**：标签 `AutoSize=false` + `AutoEllipsis=true` + `MiddleLeft`（禁止 `AutoSize=true` 换行，换行会撑破固定行高并压住下一行）；输入控件放入单元格宿主 Panel 并按 `(cellHeight - editorHeight)/2` 逐像素垂直居中，⛔ 不用 `Dock=Fill`（单行 TextBox 高度不受 Dock 控制、会贴顶造成歪斜）。
13. **两轴共用同一套排布**：`BuildRowSpecs()` 是唯一字段清单（Y 轴 19 行顺序不变；TA = 25 字段 + 4 分区标题 = **29 行**，2026-11-05 删「扭矩侦测」后实测）；`BuildLayout()` 对两种构造走同一代码路径，⛔ 不得为某一只弹窗单独设尺寸。
14. **高度上限与滚动**：可用高 = `Screen.PrimaryScreen.WorkingArea.Height - 96`（预留 Modal 内边距 40 + 标题栏 22 + 余量）；内容超限时整表进 `Panel.AutoScroll`（竖向滚动），⛔ 禁止缩小字体来"塞进去"。AntdUI 无对应滚动容器，故此处用原生 `Panel.AutoScroll`，属允许兜底。
15. **Modal 尺寸由控件驱动**：AntdUI `Modal.Config.Width` 对 `Control` 型内容无效（实测 480 与 480+Width=560 生成的宿主窗体尺寸完全相同），尺寸以 `UserControl.Size` 为准；两处调用点均不传 `Width`。

### 2026-11-04 · 决策 D2 · P1.087/P1.088 回读哨兵与错误码释义（**2026-11-05 随链路删除作废**）
- ~~每次写后立即回读，不一致即 Warning；新增 `_torqueHomeCoEObjectMissing`，命中 `0x06020000` 停止硬写；`DescribeSdoAbort` 译码 abort code~~ **2026-11-05 全部随链路删除**。

### 2026-11-04 · 决策 D3 · TORQUE_SLOPE 按 U16 整数校验并显式报错
- **变更**：激光头区 `txtOptTaSlope` 由「非负 double + `(uint)` 强转」改为 1~65535 整数校验；写入前先定位 TA 轴，定位失败即失败返回。
- **理由**：`TORQUE_SLOPE` 为 U16 驱动器参数，0 会被 CST 下发判参数非法（4609），小数强转后同样为 0；旧写入路径在目标轴缺失时静默跳过仍返回成功。
- **影响**：修改后界面回填内存真实值并有可见回执；非法输入弹窗提示；保存仍由 `DeltaMotionConfig.SaveConfig` 写 `TORQUE_SLOPE`，归属不变。

### 2026-11-04 · 决策 D4 · TA_FORCE_N 负值放开（符号=反向出力）与整型截断前置拦截
- **变更**：`ProcessControlPage.ApplyTaToConfig` 放开负值，合法区间 **−1000 ≤ force ≤ 1000**；`0` 与「非零但 `(short)` 截断为 0」的输入（`|x| < 1`）在界面层拦下并弹窗；提示文案统一写「负值为反向出力」。
- **理由**：
  - 业主现场核实 **负号就是反向出力**；旧校验 `force < 0.0` 一律判非法（弹「请输入有效的下压力(N)」），与真实语义冲突 ⇒ 「填不了负数」。
  - UI 为小数输入，底层 `TA_Auto` 用 `(short)TaForceN` **向零取整**：`-0.5`/`0.5` 静默变 `0`，再由 `SetTorque`（`targetTorque == 0` 拒绝）与 `TA_Auto`（`TaForceN == 0` 拒绝）判定非法，且现场无提示。
- **三层口径（改后一致，未改中间层）**：

| 层 | 位置 | 口径 |
|---|---|---|
| 界面 | `ApplyTaToConfig` | −1000~1000，排除 0 与「非零绝对值<1」；越界弹窗写明合法范围与「负值=反向」 |
| 指令门 | `LaserWeldHeadWorkflow.TaAuto` | `== 0` 拒 / `> 1000 \|\| < -1000` 拒（**保持现状**） |
| 驱动器 | `DeltaMontionAxis.SetTorque` | `−1000 ≤ target ≤ 1000` 对称（**保持现状**） |

- **影响**：仅界面校验与 Designer 提示文案；回填仍 `F1` 保号。配置文件 `TA_FORCE_N` 的读写（`double` + `NumberStyles.Float`）未动，现场 Config 不被覆盖。

### 2026-11-04 · 决策 D5 · P1.087/P1.088 弃 P 群组、改 CoE 直写 16#2157/16#2158（**2026-11-05 整体废弃，见 D6；勿再实施**）
> 本决策曾取代 D1 第 3 条与备选方案第 4 条；**D6 已将其全部作废**，以下仅存档定位依据。

- 曾用：`odIndex = 0x2100 + index`（87→`16#2157`、88→`16#2158`）、`SubIndex=0`、2 字节小端，写后回读真比对；`DeltaServo_Write/Read_Parameter` 声明保留但无调用方。
- 曾判定「接口错」而非寻址/驱动器问题：P 群组通路返回 `5376=0x1500`（手册 §33.5 / PDF p.942）；手册 §7-2「SDO 可读写 PDO 外任一 OD」；设备参考图 3/4 证明参数存在且映射为 16#2157/2158。
- 曾有时序约束（`ParaType=2`：Servo ON 不可设定）⇒ 写入前移 `ServoOn()` 内 `Set_Svon(1)` 之前；已使能时只读并排队下次使能前预写。回复码 `0x06020000/0x06010000/0x06010002` 由 `DescribeSdoAbort` 译码并停止硬写。
- 现场结果：写 16#2157 后回读报 **4869（手册未收录）**，链路不可用 ⇒ 2026-11-05 整体删除，由驱动器默认参数决定（D6 现场已验证 -3 回零正常）。

## 相关页面

- [[decisions/ADR-Index]]
- [[decisions/ADR-081-InitUniformServoOn]]
- [[api/MontionManager]]
- [[modules/MotionControl]]
- [[guides/DeltaEtherCAT-DevGuide]]
- [[api/DeltaEtherCAT-Native]]
- [[lessons/ConfigZoneSaveWiring]]

## 演进记录

### 2026-11-20 · 回零完成判据改为 Home_Status 权威、位置仅告警

**变更**：`MontionManager.WaitAxisHomed` 原以 `expectHome = HomeOffset` 作硬位置门；扭矩回零模式（-3）下驱动器把 offset 反向应用（现场填 `HOME_OFFSET=1.0mm` → 终位 `-1.000mm`），硬门与实测差 2mm，导致驱动器已由 `Home_Status=0` 确认完成时仍报 `NOT_REACHED`。改为：`homeVerified && Home_Status==0 && speed 稳定` 即达成，位置偏差与 `HomeOffset` 不符时记 Warning 可见但不阻断。`MotionControlWorkflow.TryHomeAxisWithWait` 失败分支删除 `StopAxis`（回零已完成轴再发停止报 4866 无描述码）。

**理由**：回零权威完成信号是驱动器 `Home_Status`（手册 §12.3：0=完成/1=运动中/2=中止/3=错误），位置只是二次证据；负模式 offset 方向手册未覆盖（见本页「负值编码最终裁决」），不应让无手册约定的符号语义阻断已确认的回零。

**影响**：现场 offset 符号不再影响回零成败（只影响告警日志）；位置硬校验能力下降，若需严格位置校验须另行裁定（如按 |HomeOffset| 取绝对值判）。4866 噪声消除。
