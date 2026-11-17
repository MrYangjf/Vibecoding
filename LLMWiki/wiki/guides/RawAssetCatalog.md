---
title: 原始资产检索表（raw/）—— 编写前必查的官方文档与 demo 入口
date: 2026-10-30
updated: 2026-11-04
tags: [原始资料, 官方文档, demo, 检索表, 路由, 台达, AntdUI, 海康, KUKA]
status: accepted
---

# 原始资产检索表（raw/）

> **本页解决什么问题**：`raw/` 里放着厂商**官方文档与 demo**（台达 832 条 API 声明、AntdUI 85 篇官方控件文档、海康 SDK 头文件与 C# 例程、KUKA RSI 3.3 手册），但**过去常被忘记使用**——凭记忆或从混淆 DLL 反推 API，既慢又容易错。
> **纪律**：⛔ 编写任何涉及第三方 SDK / 控件 / 协议的代码前，**先查本页定位原始资料**（规则见 [[lessons/DocDemoDllLookupOrder]]）。官方文档与 demo **不是"参考资料"，是第一依据**。

---

## 一、总入口：按能力域找原始资料

| 能力域 | 原始资料位置 | 资产规模 | 提炼页（先读提炼页，再回原文查细节） |
|---|---|---|---|
| **台达 EtherCAT 原生 API** | `raw/delta/EtherCAT_DLL_API清单.txt` | **832 条** API 声明 | [[api/DeltaEtherCAT-Native]] |
| 台达错误码 | `raw/delta/EtherCAT_DLL_Err.cs` | 全量错误码表 | [[api/DeltaEtherCAT-Native]] |
| 台达运动控制开发文档 | `raw/delta/运动控制模块开发文档_台达版.md` | 官方 | [[guides/DeltaEtherCAT-DevGuide]] |
| 台达 PVT / ECAM 指南 | `raw/delta/台达EtherCAT_PVT与电子凸轮运动开发指南.md` | 官方 | [[guides/DeltaEtherCAT-AdvancedMotion]] |
| 台达部署（驱动/DLL） | `raw/delta/` + 官方 PDF | — | [[guides/DeltaEtherCAT-Deployment]] |
| **台达 EtherCAT 主站程式開發手冊**（官方，2025-04-28） | `raw/delta/DELTA_IA-GMC_EtherCAT_PM_TC_20250428.pdf` | **1018 页**：§12 原點復歸（P635-638）、§22 DeltaServo 參數（P776-781）、§33 命令回傳值（P939-943） | [[guides/DeltaEtherCAT-DevGuide]] §15.4、§15.5 |
| **台达 EtherCAT 用户指南**（官方，2019-06） | `raw/delta/DELTA EtherCAT UserGuild.pdf` | **59 页**：安装/配线/轴卡参数档（无 6098/6099/P1.087 内容） | [[guides/DeltaEtherCAT-Deployment]] |
| **台达扭矩回零参数**（业主提供的现场权威截图） | `raw/delta/台达_扭矩回零_OD参数表_1.jpg` · `raw/delta/台达_扭矩回零_CoE索引_2.jpg` · `raw/delta/台达_扭矩回零_ASDA原点回归_3.jpg` · `raw/delta/台达_扭矩回零_写侦测参数接口_4.jpg` | 4 张原始截图（OD 参数表 / CoE 索引 ST 代码 / ASDA 原点回归配置 / 写侦测参数接口） | [[guides/DeltaEtherCAT-DevGuide]] §15.2、§15.3 |
| **AntdUI 控件** | `raw/AntdUI/wiki-zh/` | **85 篇**（Control 68 + Form 3 + Config/Theme/UpdateLog） | [[guides/AntdUI-Reference]] |
| AntdUI 安装/更新 | `raw/AntdUI/README.md` `wiki-zh/Install*.md` | — | [[guides/AntdUI-Reference]] |
| **海康/麦格威 SDK** | `raw/mecavision/MecaVision_SDK/` | C 头文件 6 + C# 例程 | [[guides/MecaVision-DevGuide]] |
| ↳ C 原生接口声明（唯一真相源） | `raw/mecavision/MecaVision_SDK/MecaVision/SDK/Include/*.h` | 6 个头文件 | [[api/MecaVisionMVSDK-Native]] |
| ↳ C# 例程（用法范式） | `raw/mecavision/MecaVision_SDK/MecaVision/Demo/C#/` | Basic / FirstStep / Advanced | [[guides/MecaVision-DevGuide]] |
| ↳ C# 封装（MVSDK.cs） | `raw/mecavision/MecaVision_SDK/MecaVision/Demo/C#/MVSDK/MVSDK.cs` | 官方 C# 镜像 | [[api/MecaVisionMVSDK-Native]] |
| **KUKA 机器人** | `raw/knowledge/KUKA_OPT/` | RSI 3.3 / Ethernet KRL 22 / ProfiNet 32（PDF） | [[api/KUKARobot]] |
| ↳ RSI 3.3（协议/关键词） | `raw/knowledge/KUKA_OPT/KST_RSI_33_zh.pdf` | 官方手册 | [[lessons/ProtocolDirectionalConstraints]] |
| ↳ ProfiNet（**当前零利用**） | `raw/knowledge/KUKA_OPT/KUKA_ProfiNet_32_en.pdf` | 官方手册 | （尚无提炼页，按需建） |
| EmguCV | `raw/knowledge/emgu-cv-knowledge-base/` | 交互式知识库 | [[modules/EmguALG]] |
| HelixToolkit | `raw/knowledge/helixtoolkit-knowledge-base/` | 交互式知识库 | [[modules/PointCloudData]] |
| 算法三层改造指导 | `raw/knowledge/算法程序改造指导_抽象实现Manager三层_v2.0.md` | 二手指导 | [[standards/ModuleOrganizationPattern]] |
| 监控相机开发指导 | `raw/knowledge/监控相机开发指导_MecaVision版.md` | 二手指导（**须按 SDK 原文核验**） | [[guides/MecaVision-DevGuide]] |
| **万顺兴焊接头原档** | `raw/wsx/Wsx_ScanCut.xml`（ESI）+ `raw/wsx/EtherCAT协议.xlsx`（58 变量寄存器表） | 2 份 | [[modules/MotionControl]] · [[decisions/ADR-030-WeldHeadSlaveDeviceUnderMotionControl]] |
| **开发历史** | `raw/history/history.md` | 132 KB 按时间分段的变更史 | [[project/skill-evolution]] |
| **架构原档（唯一修改入口）** | `raw/architecture/主控设计.xlsx` + `raw/architecture/激光焊接系统业务流程图20260904.md` + `raw/architecture/激光焊接系统业务流程图.pdf` | 3 份 | [[architecture/DeviceControlArchitecture]] |
| 开发团队 Skill 规范 | `raw/skills/AdaWeldsys_Skills/` | 13 篇 | [[project/skill-evolution]] · [[people/Architect]] |

> ⚠️ **台达 PDF 归档来源取证（2026-11-04）**：上表两份台达 PDF 的归档件与客户机安装目录 `D:\Program Files (x86)\Delta Industrial Automation\EtherCAT\manual\API\` 下同名文件 **SHA256 完全一致**（来源路径即该安装目录，版本随原文件）。该目录全量遍历 178 目录 / 1816 文件 / 20 份 PDF，**无 ASDA-A3/B3 伺服 EtherCAT 用户手册** ⇒ 对象字典 `6098` 负值段、`P1.087/P1.088` 定义等仍以主站手册 + 厂商书面确认为依据，不以伺服手册裁决。

---

## 二、使用范式（强制顺序）

```
第 1 级  官方文档（raw/ 本表定位）      ← 首选：定义、限制、边界
第 2 级  官方 demo（raw/ 里的例程）      ← 次选：真实用法范式
第 3 级  DLL 侦查（反射/反编译）           ← 仅验证，绝不作结论源
```

⛔ **不得跳级**。DLL 反射只暴露"有什么"，不暴露"怎么用"。
✅ 设备 SDK 场景：文档缺失时，**demo 升为第 1 级**。
✅ 侦查出的可复用结论**必须回写提炼页**，避免每轮重复侦查。

---

## 三、本表自检（脚本化）

`tools/raw_asset_check.py` 校验：
- `raw/` 下每个资产文件是否在本表被登记（未登记 ⇒ 漏用风险）；
- 本表登记的路径是否真实存在（失效 ⇒ 幻觉条目）；
- 提炼页链接是否为红链。

---

## 四、新增原始资料时的动作

1. 放入 `raw/<厂商或域>/`（只读不改，AI 不修改原档）；
2. 在本表「总入口」加一行（能力域 · 路径 · 资产规模 · 提炼页）；
3. 若该能力域尚无提炼页 → 用 `tools/lesson_new.py` / `adr_new.py` 的模式**新建提炼页**并登记；
4. 跑 `tools/raw_asset_check.py` 验证。

⛔ **清理约束（2026-11-04 起）**：`raw/` 下的**厂商手册类资产**（`.pdf` / `.chm` / `.docx`）属于唯一权威依据，任何目录整理、体积瘦身、备份清理动作**不得删除或移动**；如需瘦身，只允许移入 raw 下的归档子目录（`_archive`，需先建目录并登记）并在本表保留登记。

---

## 五、相关页面

- [[lessons/DocDemoDllLookupOrder]] —— 参考顺序的强制规则与判据
- [[guides/AntdUI-Reference]] —— AntdUI 官方文档提炼
- [[api/DeltaEtherCAT-Native]] —— 台达 832 条 API 速查
- [[guides/MecaVision-DevGuide]] —— 海康/麦格威 SDK 与例程
- [[api/KUKARobot]] —— KUKA RSI 协议知识
- [[standards/WikiPageFormatSpec]] —— 页面格式与增长规则
