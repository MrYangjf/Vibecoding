# -*- coding: utf-8 -*-
"""精确代码漂移检测：排查 wiki 引用的文件名是否在代码中实际存在"""
import os
import re
import glob

# 2026-09-03：原为硬编码旧机器绝对路径，迁移后扫描恒为 0（静默失效）。改为按脚本自身位置推导。
# LLMWiki/ 与 AdaWeldSystem/ 是工作区根下的兄弟关系：D:\焊接程序开发\{Vicoding管理平台\LLMWiki, AdaWeldSystem}
_LLMWIKI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WORKSPACE_ROOT = os.path.dirname(_LLMWIKI_ROOT)          # .../Vicoding管理平台
WIKI = os.path.join(_LLMWIKI_ROOT, "wiki")
CODE = os.path.normpath(os.path.join(_WORKSPACE_ROOT, "..", "AdaWeldSystem"))

# 收集代码中所有 .cs 文件（仅文件名 + 全路径，排除 bin/obj/3rdDepend）
code_files = {}  # 文件名 -> 所有匹配路径
for root, _, files in os.walk(CODE):
    if "bin" in root or "obj" in root or "3rdDepend" in root:
        continue
    for f in files:
        if f.endswith(".cs"):
            code_files.setdefault(f, []).append(os.path.relpath(os.path.join(root, f), CODE).replace("\\", "/"))

# 从 wiki 提取 .cs 引用
cs_ref_re = re.compile(r"([A-Za-z0-9_]+\.cs)")
refs = set()
for p in glob.glob(os.path.join(WIKI, "**", "*.md"), recursive=True):
    with open(p, encoding="utf-8-sig") as fh:
        for m in cs_ref_re.finditer(fh.read()):
            fname = m.group(1)
            if fname in ("XXX.cs", "YYY.cs", "Title.cs", "AAA.cs", "BBB.cs", "file.cs"):
                continue
            refs.add((fname, os.path.relpath(p, WIKI)))

# 对每个引用，检查是否在代码中找到
# 特别关注：已被移除的旧文件（V3迁移）、已重命名的文件
print("=" * 70)
print("精确代码漂移检测")
print("=" * 70)

# 已确认的已知漂移（旧文件已被移除或重命名）
known_removed = {
    "MotionControlWorkflow.cs", "MotionControlWorkflowState.cs",
    "WeldProcessAdjustmentWorkflow.cs", "LineLaserWorkflowState.cs",
    "MonitorWorkflowState.cs", "XMLEditor.cs",
    "ImagePage.cs", "ParamPage.cs",
    "HorizontalMoveWorkflow.cs", "SystemStatus.cs",
    "MonitorSupervisionWorkflow.cs", "CommGeneralPage.cs",
    "CommRobotPage.cs", "Helix3Drender.cs",
    "TCPClinet.cs", "TCPServer.cs",
    "YAxisController.cs", "MonitorCameraConfig.cs",
    "MonitorCameraEventArgs.cs", "Communication.cs",
    "Processing.cs", "State.cs", "WorkLoop.cs",
    "AutoAdjust.cs", "QualityEvaluator.cs",
    "SeamTracker.cs", "WeldParameterCalculator.cs",
    "WeldProcessData.cs",
}
known_demo = {
    "AdaWeldSystem.cs", "Form1.cs", "BasicDemo.cs",
    "MVCamera.cs", "IntelligentLaser.cs",
    "TableDemo.cs", "ModalDemo.cs", "GridPanelDemo.cs",
    "DataReview.cs", "SystemSet.cs", "Layout.cs",
    "Mouse.cs", "Template.cs", "DataUtil.cs",
    "MenuItems.cs", "MainWindow.cs",
}
known_antdui = {
    "GridPanel.cs", "Table.cs", "Menu.cs", "Data.cs",
    "InputNumber.cs", "Designer.cs",
}
known_people = {
    "ApiCore.cs", "CalibrationData.cs", "ConnectionManager.cs",
    "DeviceDiscovery.cs", "ErrorHandler.cs", "FrameBuffer.cs",
    "ImageAcquisition.cs", "ImageConverter.cs", "TriggerMode.cs",
    "3DModel.cs", "BoundingBoxCalculator.cs", "ColorMapper.cs",
    "CoordinateTransformer.cs", "DataIO.cs", "File3DManager.cs",
    "MeshBuilder.cs", "PointCloudFilter.cs", "Render.cs",
    "AuthManage.cs", "ConfigManage.cs", "ProductDatabaseManage.cs",
    "DeviceErrorCode.cs", "LogManager.cs", "ProfinetComm.cs",
    "SiemensS7Comm.cs", "XMLSerializer.cs",
    "AxisManager.cs", "MotionController.cs", "MotionEventArgs.cs",
    "DeviceStateMachine.cs", "INIFile.cs",
}

# 检查每个引用
real_drifts = []
for fname, src in sorted(refs, key=lambda x: x[0]):
    if fname in code_files:
        continue  # 文件存在
    if fname in known_removed:
        real_drifts.append((fname, src, "已移除/重命名"))
        continue
    if fname in known_demo:
        continue  # demo 项目引用，非本代码库
    if fname in known_antdui:
        continue  # AntdUI 库引用
    if fname in known_people:
        continue  # 专员职责假想文件
    # 其他未分类的文件
    real_drifts.append((fname, src, "未找到"))

print(f"\n[真实漂移 - 已移除/重命名文件] {len([d for d in real_drifts if d[2]=='已移除/重命名'])} 处")
for fname, src, reason in real_drifts:
    if reason == "已移除/重命名":
        print(f"  - {src} -> {fname}")

print(f"\n[真实漂移 - 未找到文件] {len([d for d in real_drifts if d[2]=='未找到'])} 处")
for fname, src, reason in real_drifts:
    if reason == "未找到":
        print(f"  - {src} -> {fname}")
print("=" * 70)