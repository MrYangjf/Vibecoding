# -*- coding: utf-8 -*-
"""ADR 页残留叙事的逐条改写（人工裁定的具体替换，逐行精确匹配，避免误伤）。"""
import os, re, sys
ROOT = r"D:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\workbudddy\Vicoding管理平台\LLMWiki\wiki\decisions"
DRY = "--apply" not in sys.argv

# (文件名, 原文片段, 替换文本) —— 原文片段必须唯一命中
REPL = [
 ("ADR-063-CommandZoneRadioExclusivity.md",
  "⚠️ **探针抓到 LA 溢出**：初版 5 个 Radio 宽 130，右边缘 **702 > 666**（超出面板 36px，最后一个会被裁掉）⇒ 收敛为宽 118 后复测通过",
  "⚠️ **LA 侧 Radio 宽度上限**：5 个 Radio 宽 130 时右边缘 702 > 666（超出面板 36px，末个被裁掉）⇒ 宽度收敛为 118"),
 ("ADR-069-PanelInnerGridZoneCells.md",
  "（探针阴性对照 E 证实）",
  "（实测证实）"),
 ("ADR-069-PanelInnerGridZoneCells.md",
  "- **首轮**：探针（真实 `AntdUI.dll`，`guides/AntdUI-Reference` §2.x 语法）4 结构 overlap=0、行高列宽与原 TLP 几何一致；阴性对照证实逆序；静态校验 39/39 PASS、",
  "- **首轮**：实测（真实 `AntdUI.dll`，`guides/AntdUI-Reference` §2.x 语法）4 结构 overlap=0、行高列宽与原 TLP 几何一致；实测证实逆序；"),
 ("ADR-071-SystemPageGridAndU4Rehome.md",
  "| ⚠️ 静态校验 | 326/326 PASS；阴性对照（改前 backup）**7/54** |",
  "| ⚠️ 布局判据 | 326 项判据全部通过；改前 backup 仅 7/54 通过（判据可区分新旧结构） |"),
 ("ADR-071-SystemPageGridAndU4Rehome.md",
  "- 静态校验 **326/326 PASS**（判据自修 1 处：X5 布局判据从 PerformLayout 锚改邻域无 `private`）；阴性对照 **7/54**（改前 backup 准确报出全部旧结构）",
  "- 布局判据 **326/326 通过**（判据自修 1 处：X5 布局判据从 PerformLayout 锚改邻域无 `private`）；改前 backup 仅 7/54 通过（准确报出全部旧结构）"),
 ("ADR-074-RsiNumericProtocolImplementation.md",
  "**验证**：Python 静态校验 29/29 通过；阴性对照（镜像副本注入 4 处旧行为）4 项 FAIL ⇒ 判据有区分度。⚠️ 真编译待 Visual Studio，DEMO 联调仍需现场验证 IPOC 回传与沿触发。",
  "**判据自证**：静态校验 29/29 通过；镜像副本注入 4 处旧行为后 4 项全部 FAIL（判据有区分度）。⚠️ 真编译待 Visual Studio，DEMO 联调仍需现场验证 IPOC 回传与沿触发。"),
 ("ADR-074-RsiNumericProtocolImplementation.md",
  "- ✅ 静态校验 47/47 通过；阴性对照（基线副本）22 项 FAIL ⇒ 判据有区分度",
  "- ✅ 静态校验 47/47 通过；基线副本 22 项 FAIL（判据有区分度）"),
 ("ADR-076-SettingsZoneSaveWiring.md",
  "- **静态校验 49/49 PASS**（配置四点闭环 5 项 + 分区落盘接线 13 项 + 读取接线 4 项 + 解析口径 4 项 + 接线完整性 2 项 + using/作用域 2 项 + C# 7.3/保留字 5 项 + Dispose 1 项 + csproj 路径 1 项 + Designer 控件闭环 3 项 + 行尾同质 4 项 + 阴性对照 5 组）。",
  "- **判据覆盖 49 项**（配置四点闭环 5 项 + 分区落盘接线 13 项 + 读取接线 4 项 + 解析口径 4 项 + 接线完整性 2 项 + using/作用域 2 项 + C# 7.3/保留字 5 项 + Dispose 1 项 + csproj 路径 1 项 + Designer 控件闭环 3 项 + 行尾同质 4 项 + 旧行为注入 5 组）。"),
 ("ADR-076-SettingsZoneSaveWiring.md",
  "- **阴性对照**：注入 5 组旧行为（Adapt→System / Preset→全量 / Quick→全量 / 删 MAX_MAP_POINTS 写 / 删 LoadWeldHeadConfig），对应判据**全部 FAIL** ⇒ 判据有区分度。",
  "- **旧行为注入**：注入 5 组旧行为（Adapt→System / Preset→全量 / Quick→全量 / 删 MAX_MAP_POINTS 写 / 删 LoadWeldHeadConfig），对应判据**全部 FAIL**（判据有区分度）。"),
]


def main():
    n = 0
    miss = []
    for fn, old, new in REPL:
        p = os.path.join(ROOT, fn)
        if not os.path.isfile(p):
            miss.append((fn, "文件不存在"))
            continue
        b = open(p, "rb").read()
        bom = b[:3] == b"\xef\xbb\xbf"
        body = b[3:] if bom else b
        crlf = body.count(b"\r\n")
        lf = body.count(b"\n") - crlf
        nl = "\r\n" if crlf > lf else "\n"
        txt = body.decode("utf-8", errors="replace").replace("\r\n", "\n")
        cnt = txt.count(old)
        if cnt != 1:
            miss.append((fn, "命中 %d 次（要求恰好 1 次）: %s" % (cnt, old[:50])))
            continue
        txt = txt.replace(old, new)
        if not DRY:
            out = txt.replace("\n", nl).encode("utf-8")
            if bom:
                out = b"\xef\xbb\xbf" + out
            open(p, "wb").write(out)
        n += 1
        print("  ✅ %s" % fn)
    print("\n已改写 %d 处" % n)
    if miss:
        print("未命中 %d 处：" % len(miss))
        for f, m in miss:
            print("  ❌ %s: %s" % (f, m))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
