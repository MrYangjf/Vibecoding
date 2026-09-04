# -*- coding: utf-8 -*-
"""精确代码漂移检测：排查 wiki 引用的 .cs 文件名是否在代码中实际存在。

分诊口径（2026-09-03 重构，取代原先「25 处已知 + 85 处未分类」的粗放白名单）：

  1. RENAMED  已改名/重构 —— 旧名有确定的现役对应物。现状描述类页面应直接替换为新名；
              历史 ADR 页面允许保留旧名，但必须在同一行加注「（现役 `New.cs`）」。
  2. REMOVED  已移除 —— 旧名无对应物（合并/废弃/删除）。历史 ADR 页面允许保留旧名，
              但必须在同一行加注「（已移除）」。
  3. EXTERNAL 外部/库内部/大小写误报 —— 静默，不计入漂移。
  4. RAW_SPEC 原档命名 —— raw/architecture/ 设计原稿里的文件名，属设计意图引用，
     静默（2026-09-03 新增）。

判定规则：扫描器读取每个引用所在的整行，若该行已包含新名（RENAMED）或「已移除/已删除/
已废弃」（REMOVED），则计为「已标注」（informational）；否则计为「待修正」（需编辑 wiki）。

掩码约定（2026-09-03）：反引号代码体与围栏代码块**不参与漂移判定**，与 wiki_audit.py /
lint_scan.py 对齐。本库既定写法是「历史名、示例名、原档名一律写成 `Xxx.cs` 而非
[[链接]]」，因此行内代码体在本脚本中的语义即「非真实引用」。

健康判据：待修正 = 0。
"""
import os
import re
import glob

# 路径一律由脚本自身位置推导。禁止硬编码绝对路径——迁移机器后硬编码会让扫描器
# 恒扫 0 个文件却显示健康，比崩溃更危险（2026-09-03 踩过）。
# 目录关系：<工作区根>/{Vicoding管理平台/LLMWiki, AdaWeldSystem}
_LLMWIKI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WORKSPACE_ROOT = os.path.dirname(_LLMWIKI_ROOT)          # .../Vicoding管理平台
WIKI = os.path.join(_LLMWIKI_ROOT, "wiki")
CODE = os.path.normpath(os.path.join(_WORKSPACE_ROOT, "..", "AdaWeldSystem"))

# 收集代码中所有 .cs 文件（仅文件名 + 全路径，排除 bin/obj/3rdDepend）
code_files = {}
for root, _, files in os.walk(CODE):
    if "bin" in root or "obj" in root or "3rdDepend" in root:
        continue
    for f in files:
        if f.endswith(".cs"):
            code_files.setdefault(f, []).append(
                os.path.relpath(os.path.join(root, f), CODE).replace("\\", "/"))

# ---- 分诊词典 ------------------------------------------------------------------

# 1) 已改名/重构：旧名 -> 现役文件
RENAMED = {
    # 主控层：ADR-034 三态模型 + MainDeviceControl 单点合并
    "MainDeviceWorkflow.cs": "MainDeviceControl/DeviceControlWork.cs",
    "MachineControlWork.cs": "MainDeviceControl/DeviceControlWork.cs",
    "MachineStatusWork.cs": "MainDeviceControl/DeviceStatusWork.cs",
    "MainDeviceThread.cs": "MainDeviceControl/DeviceStatusWork.cs",
    "SafetyWorkflow.cs": "MainDeviceControl/DeviceStatusWork.cs",
    "WorkflowStateBase.cs": "MainDeviceControl/DeviceStateApiCore/DeviceWorkflowBase.cs",
    "DeviceStateMachineBase.cs": "MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs",
    "DeviceStateMachine.cs": "MainDeviceControl/DeviceStateApiCore/DeviceStateBase.cs",
    "MotionControlStateMachine.cs": "MainDeviceControl/DeviceWorkflow/MotionControlWorkflow.cs",
    "MonitorCameraStateMachine.cs": "MainDeviceControl/DeviceWorkflow/MonitorCameraWorkflow.cs",
    "LaserWeldHeadStateMachine.cs": "MainDeviceControl/DeviceWorkflow/LaserWeldHeadWorkflow.cs",
    # 通讯层
    "PLCCommunicationManager.cs": "Comm/PLC/Siemens/S7PLCCommunication.cs",
    "RobotCommunicationManager.cs": "Comm/Robot/KUKARobot/KUKARobotManager.cs",
    "GlobalCommData.cs": "Comm/SystemComm.cs",
    # 相机 / 运控 / 算法
    "MonitorCameraConfig.cs": "MonitorCam/MonitorCameraRun.cs",
    "Zmcaux.cs": "MotionControl/ZMotion/ZMotionNative.cs",
    "StageBase.cs": "EmguALG/Stages.cs",
    "FilterStage.cs": "EmguALG/Stages.cs",
    "EdgeDetectionStage.cs": "EmguALG/Stages.cs",
    "FeatureExtractionStage.cs": "EmguALG/Stages.cs",
    "MorphologyStage.cs": "EmguALG/Stages.cs",
    "TemplateMatchStage.cs": "EmguALG/Stages.cs",
    "PipelineConfig.cs": "EmguALG/Stages.cs",
    # UI：SunnyUI 时代页面 -> AntdUI 迁移后现役页面
    "Helix3Drender.cs": "UIDesign/SubView/HelixRenderForm.cs",
    "XMLEditor.cs": "UIDesign/TabPage/FileEditorPage.cs",
    "CommGeneralPage.cs": "UIDesign/TabPage/CommPage.cs",
    "CommRobotPage.cs": "UIDesign/TabPage/CommPage.cs",
    "ImagePage.cs": "UIDesign/TabPage/MonitorCamPage.cs",
    "ParamPage.cs": "UIDesign/TabPage/ParamConfigPage.cs",
    "EmguAlgoPage.cs": "UIDesign/SubView/ILAlgoPage.cs",
    "LLCamWorkJob.cs": "UIDesign/TabPage/ILCamPage.cs",
    "LLCameraSetting.cs": "UIDesign/SubView/ILParamPage.cs",
}

# 2) 已移除：无现役对应物，历史 ADR 可保留旧名但须加注「（已移除）」
REMOVED = {
    "SafetyFlow.cs": "ADR-031 合并进 DeviceStatusWork",
    "SafetyInterlock.cs": "ADR-031 合并进 DeviceStatusWork",
    "SimulationWorkflow.cs": "独立模拟流程已废弃（成员归并 DeviceControlWork）",
    "HorizontalMoveWorkflow.cs": "ADR-012 后移除",
    "TCPServer.cs": "未落地，现役仅有 TCPIPComm 客户端侧",
    "NetworkPortBase.cs": "网络端口抽象层未落地",
    "INetworkPort.cs": "网络端口抽象层未落地",
    "NullMotionController.cs": "ADR-027 删除空控制器",
    "Workflow.cs": "仅为目录/概念名，非实体文件",
    # 曾存在但代码中已无对应类型的旧名（保留原因说明，便于人工核对现役归属）
    "SystemStatus.cs": "已并入 Comm/SystemComm.cs",
    "TCPClinet.cs": "拼写错误的历史名；现役 Comm/CommBase/Ethernet/TCPIPComm.cs",
    "MonitorCameraEventArgs.cs": "事件参数类已移除；配置现由 MonitorCam/MonitorCameraRun.cs 承担",
    "YAxisController.cs": "Y 轴专用控制器已移除；现役 MotionControl/MotionManager.cs + ZMotion/ZMotionAxis.cs",
    "XMLEditor.Designer.cs": "随 XMLEditor.cs 一并移除；现役 UIDesign/TabPage/FileEditorPage.Designer.cs",
}

# 3) 外部参考 / 第三方库内部 —— 静默
EXTERNAL = {
    "StationProcess.cs": "外部参考实现（非本代码库）",
    "AssemblyProcess.cs": "外部参考实现（非本代码库）",
    "SvgDb.cs": "AntdUI 库内部类型",
    "Zmcaux.cs": "正运动官方 SDK 文件名（非本库文件），本项目对应 MotionControl/ZMotion/ZMotionNative.cs",
    "INIFile.cs": "大小写变体：现役 FileOperate/IniFile.cs",
    # 泛指设计器文件，非某个具体文件（真实文件形如 XxxForm.Designer.cs）
    "Designer.cs": "泛指设计器文件",
    "designer.cs": "泛指设计器文件（大小写变体）",
}

# 4) 设想文件 / 外部 demo —— people 专员页按职责域列举的假想文件名，
#    以及 AntdUI、EmguCV 官方 demo 项目里的文件，均非本代码库实体，静默。
SPECULATIVE = {
    # 外部 demo / 参考项目
    "Form1.cs", "BasicDemo.cs", "MVCamera.cs", "TableDemo.cs", "ModalDemo.cs",
    "GridPanelDemo.cs", "DataReview.cs", "SystemSet.cs", "Layout.cs", "Mouse.cs",
    "Template.cs", "DataUtil.cs", "MenuItems.cs", "MainWindow.cs",
    "IntelligentLaser.cs", "Program.cs", "ButtonDemo.Designer.cs",
    # people/ 专员职责域假想文件
    "ApiCore.cs", "CalibrationData.cs", "ConnectionManager.cs", "DeviceDiscovery.cs",
    "ErrorHandler.cs", "FrameBuffer.cs", "ImageAcquisition.cs", "ImageConverter.cs",
    "TriggerMode.cs", "3DModel.cs", "BoundingBoxCalculator.cs", "ColorMapper.cs",
    "CoordinateTransformer.cs", "DataIO.cs", "File3DManager.cs", "MeshBuilder.cs",
    "PointCloudFilter.cs", "Render.cs", "AuthManage.cs", "ConfigManage.cs",
    "ProductDatabaseManage.cs", "DeviceErrorCode.cs", "LogManager.cs",
    "ProfinetComm.cs", "SiemensS7Comm.cs", "XMLSerializer.cs", "AxisManager.cs",
    "MotionController.cs", "MotionEventArgs.cs",
    # AntdUI / 第三方库内部类型名
    "GridPanel.cs", "Table.cs", "Menu.cs", "Data.cs", "InputNumber.cs",
    # people/ 专员页按职责域列举的设想文件（从未落地，需改写为现役结构而非改名）
    "WeldProcessData.cs", "AutoAdjust.cs", "SeamTracker.cs",
    "WeldParameterCalculator.cs", "QualityEvaluator.cs",
}

# 占位/通配/示例文件名——正文里用来举例或泛指，不是真实文件引用。
# 2026-09-03 补：写规范文档时极易顺手产出 `X.cs` / `XxxWorkflow.cs` 这类泛指名，
# 扫描器会把它们当成「未登记的新漂移」，属于自伤，故显式豁免。
PLACEHOLDER_CS = {"XXX.cs", "YYY.cs", "Title.cs", "AAA.cs", "BBB.cs", "file.cs",
                  "X.cs", "Y.cs", "New.cs", "Old.cs",
                  "XxxStateMachine.cs", "XxxWorkflow.cs", "AdaWeldSystem.cs"}

# 占位名的形状规则，兜住上面没列全的同类写法：
#   Xxx*.cs / XXX*.cs —— 以 2 个以上连续 X 开头（大小写均可）
#   X.cs / Y.cs       —— 单字母文件名
placeholder_re = re.compile(r"^(?:[Xx]{2,}[A-Za-z0-9_]*|[A-Za-z])\.cs$")

# 外部参考项目的路径前缀：这些项目里的同名文件是真实存在的，不是本库的漂移
EXTERNAL_PREFIXES = ("PcomDeviceInterface/", "HonorMachineTest/")

# 行内已出现的「移除语义」关键词——该行本身就在描述旧文件被删，
# 再追加「（已移除）」会造成语义重复。2026-09-03。
NOTED_KEYWORDS = ("已移除", "已删除", "已废弃", "已替代", "删除", "移除", "废弃", "淘汰")

# 文件名正则需吃掉点号并做右边界断言，否则会误截断：
#   FormMain.Designer.cs  ->  Designer.cs（旧版因此产生 144 处误报）
#   AdaWeldSystem.csproj  ->  AdaWeldSystem.cs（旧版产生 14 处误报）
cs_ref_re = re.compile(
    r"(?<![A-Za-z0-9_.])([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*\.cs)(?![A-Za-z0-9_.])")

# 行内代码体 / 围栏代码块掩码（2026-09-03 补）。
# 与 wiki_audit.py / lint_scan.py 对齐：反引号代码体在本库的既定语义是
# 「非真实引用」——历史名、示例名、原档命名都改写为 `Xxx.cs` 而非 [[链接]]，
# 因此不应参与漂移判定。此前本脚本缺失掩码，导致架构页 §15 冲突表里
# 原档命名 `CommandCore.cs` 被判为「未登记的新漂移」（9 处误报）。
# 用等长空白替换而非删除，可保持行号与列偏移不变。
_FENCE_RE = re.compile(r"```.*?```", re.S)
_INLINE_RE = re.compile(r"`[^`\n]*`")


def mask_code(txt):
    """把围栏代码块与行内代码体替换为等长空白。"""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))
    return _INLINE_RE.sub(blank, _FENCE_RE.sub(blank, txt))


def is_external_ref(line, fname):
    """判断 fname 是否位于外部参考项目的路径下。

    2026-09-03 修复：原判定为 `prefix + fname in line`，只匹配到一级目录，
    对 `PcomDeviceInterface/Work/Process/RollPressProcess.cs` 这类多级路径失效
    （ADR-035 原档清单因此误报）。改为取出紧邻文件名的完整路径前缀再判前缀。
    """
    for m in re.finditer(
            r"(?<![A-Za-z0-9_.])((?:[A-Za-z0-9_]+/)+)" + re.escape(fname)
            + r"(?![A-Za-z0-9_.])", line):
        if m.group(1).startswith(EXTERNAL_PREFIXES):
            return True
    return False


# 原档命名（2026-09-03）：raw/architecture/ 下设计原稿里出现的文件名，
# 属于「设计意图引用」，既非现役代码也非历史遗留，不参与漂移判定。
# 掩码已覆盖绝大多数场景，此处作为正文裸写原档名时的兜底。
RAW_SPEC_NAMES = {
    "CommandCore.cs",          # 原档对 DeviceStateApiCore/CommandTable.cs 的命名
    "RollPressProcess.cs",     # 外部参考项目 PcomDeviceInterface 的工序实现
    "AssemblyProcess.cs",
    "DeviceStateMachineBase.cs",
}

# ---- 扫描 ----------------------------------------------------------------------
pending_renamed, pending_removed = [], []
noted_renamed, noted_removed = [], []
# 历史 ADR 页保留旧文件名以留存决策上下文，改用页面级横幅统一标注（2026-09-03 约定）。
# 页面正文出现该标记即视为「已标注」，无需逐行加注。
HISTORY_BANNER = "历史名称提示"


def banner_lines(lines):
    """返回「历史名称提示」引用块覆盖的行号集合。

    以 `> ⚠️ 历史名称提示` 起头的引用块，其后连续的 `>` 行本身就是在逐条列举
    「旧名 → 现役 / 已移除」映射。对这些行再判漂移属于自伤（2026-09-03 踩坑：
    project/overview.md 横幅里的通配占位名被判为「未登记的新漂移」）。
    遇到非 `>` 行即结束该块。
    """
    out, in_banner = set(), False
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith(">"):
            if HISTORY_BANNER in line:
                in_banner = True
            if in_banner:
                out.add(i)
        else:
            in_banner = False
    return out


for path in sorted(glob.glob(os.path.join(WIKI, "**", "*.md"), recursive=True)):
    src = os.path.relpath(path, WIKI).replace("\\", "/")
    with open(path, encoding="utf-8-sig") as fh:
        text = fh.read()
    lines = text.splitlines()
    page_annotated = HISTORY_BANNER in text
    exempt = banner_lines(lines)
    for i, line in enumerate(lines, 1):
        if i in exempt:
            continue
        for m in cs_ref_re.finditer(mask_code(line)):
            fname = m.group(1)
            if (fname in PLACEHOLDER_CS or fname in code_files
                    or fname in RAW_SPEC_NAMES
                    or placeholder_re.match(fname)):
                continue
            if fname in EXTERNAL or fname in SPECULATIVE:
                continue
            if is_external_ref(line, fname):
                continue
            if fname in RENAMED:
                noted = page_annotated or RENAMED[fname].split("/")[-1] in line
                (noted_renamed if noted else pending_renamed).append((fname, src, i, RENAMED[fname]))
            elif fname in REMOVED:
                noted = page_annotated or any(k in line for k in NOTED_KEYWORDS)
                (noted_removed if noted else pending_removed).append((fname, src, i, REMOVED[fname]))
            else:
                pending_removed.append((fname, src, i, "未登记的新漂移"))

W = 70
print("=" * W)
print("精确代码漂移检测")
print("=" * W)
print(f"\n代码根：{CODE}")
print(f"已索引 .cs 文件：{len(code_files)} 个（排除 bin/obj/3rdDepend）")

print(f"\n【待修正 · 已改名未同步】{len(pending_renamed)} 处")
for fname, src, ln, new in pending_renamed:
    print(f"  - {src}:{ln}  {fname}  ->  现役 {new}")

print(f"\n【待修正 · 已移除未标注】{len(pending_removed)} 处")
for fname, src, ln, why in pending_removed:
    print(f"  - {src}:{ln}  {fname}  ({why})")

print(f"\n【已标注 · 历史保留】{len(noted_renamed) + len(noted_removed)} 处（informational）")
for fname, src, ln, new in noted_renamed:
    print(f"  - {src}:{ln}  {fname}  ->  已注明现役 {new}")
for fname, src, ln, why in noted_removed:
    print(f"  - {src}:{ln}  {fname}  ->  已注明移除（{why}）")

todo = len(pending_renamed) + len(pending_removed)
print("\n" + "=" * W)
print(f"健康判据：待修正 {todo} 处 -> {'通过（0）' if todo == 0 else '不通过'}")
print("=" * W)
