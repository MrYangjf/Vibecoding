---
title: 大类 UserControl 拆分的两类编译坑
date: 2026-11-20
updated: 2026-11-20
tags: [教训, UI, 页面拆分, Designer, 编译错误]
status: active
source: AdaWeldSystem/UIDesign/TabPage/FilebackupPage.cs 拆分为 CommSettingPage + FilebackupPage（2026-11-20）
---

# 大类 UserControl 拆分的两类编译坑

> **一句话**：拆分 2000+ 行的复合页时，region 抽取的黏行与 using 的过度精简会各产一个编译错误；静态判据方向写反会制造满屏假阳性。

## 坑一：region 切片末行黏连导致 CS1513

### 现象

按 `#region` 抽取方法块重组新类后，真编译报 `error CS1513: 应输入 }`，定位在文件尾部的 `#endregion    }` 行——闭合大括号被拼到了 `#endregion` 同一行。

### 根因

`'\n'.join(lines[start:end])` 产生的切片**末行不带换行符**，后续字符串拼接 `seg + '    }\n}\n'` 时直接黏连。

### 判据

生成后逐文件断言：`#region` 计数 == `#endregion` 计数；尾部结构为独立的 `#endregion` 行 + 独立闭合行；真编译 errors=0。

### 预防

- 切片末行与前导拼接前显式补换行，或拼接模板以 `\n` 起头。
- 抽取脚本先用 `--dry` 打印边界与行数，确认无 WARN 再落盘；用完即删。

## 坑二：精简 using 删掉保留半边仍需的命名空间

### 现象

拆分后真编译报 `CS0103 不存在名称 WeldParamManager` 与 `CS0246 找不到 CommunicationManager`——精简单页 using 时按「本页主题」删掉了 `WeldParamControl` 与 `Comm.Communication`，但保留在系统页的台达配置区 `ReloadSystemConfig` 仍引用这两个类型。

### 根因

using 是**整类共享**的，拆成两类后应按「各页保留 region 实际引用的类型并集」决定，不能按页名主题凭印象删减。

### 判据

先对保留 region 全文 grep 类型名，再决定是否保留对应 using；以真编译 errors=0 为最终闸门。

### 预防

- 拆分初期宁可两边 using 都保留全集，编译通过后再按 review 结果精简。
- ⛔ 静态守卫全绿不等于编译通过（[[rules/KR-010-No-Compiler-Honesty]]）。

## 坑三：静态判据方向写反制造假阳性

### 现象

自写 verifier 首版报 8 个 FAIL，其中 7 个是判据写反：把「通讯页必须含 inputLog/AppendLog」写成「通讯页禁含」，把「系统页必须含 tableDeltaView」写成「禁含」；剩下 1 个是子串重叠误报（`ConfigForm` 命中在用的 `RecordConfigForm`）。

### 根因

写「双向归属断言」时把「本职符号」与「越界符号」两列搞反；删除类型校验用了裸子串而非精确路径片段。

### 判据

判据须写成「该页**必含**本职符号 且 **禁含**对页符号」的明确双向形式；删除校验用精确路径片段（如 `ParamContolDialog\ConfigForm`）而非裸类型名。

### 预防

- 首版判据报大量 FAIL 时先怀疑判据本身（Step 2.6 两轮纪律），逐条核对方向后再改代码。
- 交并确保「命中集非空 + 阴性对照干净」（见静态校验判据库）。

## 相关页面

- [[lessons/UiModuleRemovalCleanup]] —— 删 UI 模块的 7 项清理清单
- [[lessons/UiLayoutChangeSyncPitfalls]] —— 设计器可见优先与事件不双写
- [[rules/KR-010-No-Compiler-Honesty]] —— 真编译门禁
- [[decisions/ADR-112-ui-page-split-and-dialog-cleanup]] —— 本轮拆分决策
- [[index/index]]
