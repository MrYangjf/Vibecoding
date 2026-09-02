---
title: QA/测试专员
date: 2026-07-01
tags: [专员, QA, 测试]
source: raw/skills/AdaWeldsys_Skills/01-Team/QASpecialist.md
---

# QA/测试专员

## 职责边界

- UI 界面功能测试
- 各模块业务逻辑单元测试
- 跨模块集成测试
- Bug 复现、定位与修复验证
- 性能测试（大数据量点云、高帧率图像、高频运动控制）

## 测试范围

| 测试类型 | 测试内容 | 对应专员 |
|----------|----------|----------|
| UI 测试 | 页面切换、控件响应、布局适配、数据绑定 | UI开发专员 |
| 相机测试 | 连接稳定性、数据采集完整性、回调频率 | 工业相机 |
| 算法测试 | 各阶段算法输出正确性、参数边界 | 图像算法 |
| 3D 测试 | 文件导入导出、重建质量、渲染性能 | 3D开发 |
| 通信测试 | TCP 连接/断开/重连、数据包完整性 | 通用技术 |
| 数据库测试 | 并发读写、数据一致性、权限控制 | 数据库 |
| 焊接工艺测试 | 参数公式计算正确性、在线修正精度 | 焊接工艺 |
| 运动控制测试 | 轴定位精度、软限位生效、急停响应 | 运动控制 |
| 集成测试 | 端到端流程（相机→算法→运动控制→焊接） | 全部 |

## UI 审查清单

| 检查项 | 检查位置 | 通过标准 |
|--------|----------|----------|
| 字段声明 | Designer.cs #endregion 后 | 控件字段存在，类型正确 |
| 实例化 | Designer.cs InitializeComponent | 必须有 new 语句 |
| 属性设置 | Designer.cs InitializeComponent | Font/Location/Size/Name 已设置 |
| 事件绑定 | Designer.cs InitializeComponent | 事件已绑定到正确方法 |
| 加入父容器 | Designer.cs InitializeComponent | Controls.Add 存在 |
| 事件方法 | .cs 文件 | 方法体存在，命名格式 控件名_事件名 |

---

*来源：raw/skills/AdaWeldsys_Skills/01-Team/QASpecialist.md*
