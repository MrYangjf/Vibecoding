---
title: ADR-004 Step 状态机决策
date: 2026-07-01
tags: [决策, 工作流, 状态机]
status: accepted
source: history.md [45]
---

# ADR-004 Step 状态机决策

## 背景

LineLaserWorkflow 早期使用顺序流程控制（依次执行取图→分析→调整），流程耦合度高，失败处理困难。

## 决策

将工作循环改为 **Step 枚举控制**：每执行完一个 Step 自动跳到下一个 Step，等待操作封装在单个 Step 内部。

`csharp
public enum WorkflowStep
{
    Idle = 0,          // 空闲
    CheckJob = 1,      // 检查并加载 Job
    AcquireImage = 2,  // 获取图像
    AnalyzeImage = 3,  // 分析图像
    Display = 4,       // 显示结果
    Adjust = 5,        // 自动调整
    Complete = 6       // 完成
}
`

## Step 流转规则

| Step | 成功 | 失败 |
|------|------|------|
| CheckJob | → AcquireImage | 停留重试 |
| AcquireImage | → AnalyzeImage | 停留重试 |
| AnalyzeImage | → Display | 回退到 AcquireImage |
| Display | → Adjust | — |
| Adjust | → Complete | 回退到 AcquireImage |
| Complete | → Idle | — |

## 后果

- 每个 Step 独立封装，便于单元测试
- 失败时可回退到前一个 Step 重试
- WorkflowLoopWorker 改为 switch-case 分派模式

---

*来源：raw/history/history.md [45]*
