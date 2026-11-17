---
title: AntdUI Modal 内容控件在 open 返回前已被销毁 → 弹窗内改的参数不生效、再开复原
date: 2026-11-17
updated: 2026-11-17
tags: [教训]
status: active
---

# AntdUI Modal 内容控件在 open 返回前已被销毁 → 弹窗内改的参数不生效、再开复原

> **一句话**：AntdUI Modal 内容控件在 open 返回前已被销毁 → 弹窗内改的参数不生效、再开复原

## 现象

系统设置页 Y 轴 / TA 轴表格「参数」按钮弹窗（AxisConfigForm）里修改参数并点确定，参数不生效；再次点「参数」查看，界面又显示回原来的值。磁盘 DeltaMotionConfig.xml 的修改时间不前进，SaveConfig 从未被调用。

## 根因

宿主把「写回配置」放在 Modal.open 返回之后：AntdUI 的 LayeredFormModal 在窗体关闭时于 DestroyHandle() 内执行 config.Content.Dispose()，弹窗内容控件（UserControl）连同其全部 TextBox 已被销毁。此时再从 _txtXXX.Text 取值只会读到 LoadValues() 时的旧值（控件已 Dispose，Text 读取返回控件缓存/初值），ParseDouble 解析失败便保留原值 → 写回的永远是旧值。且宿主用 Modal.open(...) == DialogResult.OK 作为唯一执行门槛，一旦判定不成立，Commit + SaveConfig 整段被跳过，落盘与日志全部不发生（表现为磁盘文件时间不前进）。

## 判据

判据一：任何『弹窗内改值 → 宿主在 open 返回后读控件值写回』的写法即为缺陷。判据二：写回动作必须在控件存活期发生——由弹窗内部「确定」按钮触发 Commit，宿主只负责落盘。判据三：宿主判定『用户是否确认』不得依赖 Modal.open 的返回值，须用弹窗自持的 Committed 标志。判据四：Commit 必须幂等（_committed 早退），防止重复写回。判据五：确认路径的证据是磁盘文件 mtime 前进 + 落盘日志出现，二者缺一即判定链路未执行（绿灯不等于落盘）。

## 预防

- UI 弹窗取值一律在控件存活期完成；写回与落盘分离为两步（弹窗内写回内存、宿主落盘）。
- 跨弹窗边界的「用户是否确认」用弹窗自持标志，不用框架返回值。
- 核对生效性用磁盘 mtime + 落盘日志双证据，不靠界面回显。

## 相关页面

- [[api/SystemControlPage]]
- [[api/MontionManager]]
- [[lessons/AntdUI-Modal-Config-Overload-Cascade]]
- [[lessons/ConfigZoneSaveWiring]]
