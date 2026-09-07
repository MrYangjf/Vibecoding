---
title: OPEN 消报语义：M5 应回落 Stop 还是 NoReset
date: 2026-09-04
tags: [待决问题, 架构, 状态机, 焊接工艺, MainDeviceStatus, ClearAlarm, 已关闭]
status: closed
---

# OPEN 议题：消除报警（M5）应回落 Stop 还是 NoReset

> ✅ **已关闭（2026-09-04 下午）**：用户最终裁定——**消除报警一律回 NoReset**，无论报警前是否处于 Running；只有复位流程执行成功才到达 Stop。已落地于 `DoClearAlarm`，正式决议见 [[decisions/ADR-034-MainDeviceStateSemantics]] D1。以下为存档。

> **状态：未决（Open）**。用户 2026-09-04 明确表示「我在这里犹豫了」，裁定**先按旧文档回到 Stop 处理**，
> 但要求**标记该问题**留待后续裁定。本页即该标记。

---

## 一、两种立场的冲突

| 立场 | 来源 | 规则 | 隐含假设 |
|---|---|---|---|
| **A：M5 → M1（NoReset）** | 原档20260904 §10.2 序号 5 | `ClearAlarm` 使 M5→M1，**消除后必须重新 Reset 才能运行** | 报警后设备物理状态未知，必须重新走完整复位链才能确认安全 |
| **B：M5 → M3（Stop）** | 旧文档（普通设备通用设计）+ 现有代码 | `ClearAlarm` 依 `Last` 决定回落 Stop 或 NoReset；`Last == Running` 时回 Stop，可立即再次启动 | 设备是**普通设备**，stop 后可原地 resume，状态未破坏 |

现有代码（`DeviceControlWork.DoClearAlarm()`）实现的是 **B**。

---

## 二、用户的核心洞察（焊接工艺约束）

> 用户原话（2026-09-04）：
> 「旧文档以普通设备写的（普通设备 running-stop-start running 合乎规则），
> 新文档考虑到焊接设备，**stop 后焊丝断裂已经无法接着焊接**，
> 只能机器人恢复、手动清理、机器人重新到达新焊接位开启焊接。
> **它有了一个中间过程，需要机器人重新确认状态**。」

这是**设备类型差异**导致的语义分歧，不是单纯的设计偏好：

```
普通设备：  Running ──stop──> Stop ──start──> Running   （状态可原地续接，合法）

焊接设备：  Running ──stop──> Stop ──✗──> Running
                              │
                              │ 焊丝已断裂，无法原地续焊
                              ▼
                    机器人恢复位姿 + 人工清理焊丝 + 机器人重新到达新焊接位
                              │
                              │  ← 这个「中间过程」在 M3 Stop 态下无法表达
                              ▼
                          重新 Preworking → Working
```

**关键矛盾**：`M3 设备停止` 在原档定义中是「设备已就绪并待机，可接收启动命令」，
但焊接设备的 stop 态**并不是真正就绪**——它还欠一个「机器人重新确认状态」的中间过程。
因此从语义严谨性看，**A 更正确**；但从操作习惯与现有代码看，**B 更少改动**。

---

## 三、当前裁定与代码落点

**裁定（2026-09-04）：暂按 B 实现，保留 A 的可能性。**

代码落点：`DeviceControlWork.DoClearAlarm()`
```csharp
bool wasRunning = Last == MainDeviceStatus.Running;
SetStatus(wasRunning ? MainDeviceStatus.Stop : MainDeviceStatus.NoReset, ...);
```

该方法已挂 `⚠️ C3 待决` 的 XML 备注指向本页，后续裁定改此处即可。

---

## 四、后续裁定需要回答的问题

1. **中间过程由谁承载？** 若采用 A，焊接设备 stop 后的「机器人恢复 + 人工清理 + 重新到位」
   是建模为一个新的 `MainDeviceStatus` 态（会打破原档 6 态约定），
   还是复用现有 `Reseting`（M2）语义，还是仅作为 `NoReset → Reseting → Stop` 的既有链路？
2. **UI 交互影响**：改为 A 后，操作工点「消除报警」后必须再点「复位」才能启动，
   比现在多一步。是否接受？
3. **报警分级**：是否所有报警都需重复位？轻微报警（如通讯抖动）与严重报警（如互锁触发）
   是否应区别对待？
4. **与急停的关系**：`M6 急停 → EstopCancel → M1 NoReset` 已明确要求重复位；
   若报警也要求重复位，两者语义将完全对齐——这是否更一致？

---

## 五、关联

- 原档：`raw/architecture/激光焊接系统业务流程图20260904.md` §3.2 / §4.2 / §10.2
- 代码：`AdaWeldSystem/MainDeviceControl/DeviceControlWork.cs` — `ClearAlarm()` / `DoClearAlarm()`
- 架构页：[[architecture/DeviceControlArchitecture]] §1.3（MainDeviceStatus 6 态）
- 触发本议题的原档解读：本轮新增原档补齐了 §10.2 命令表，才暴露出该冲突

> 裁定后请：① 更新本页 `status: resolved`；② 改 `DoClearAlarm()`；
> ③ 同步 `api/DeviceControlWork.md`；④ 删除代码中的 `⚠️ C3 待决` 标记。
