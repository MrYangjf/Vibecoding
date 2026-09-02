# AdaWeldSystem 云端源码备份（GitHub）操作手册

> 把 `D:\焊接程序开发\AdaWeldSystem` 的源码备份到 GitHub 仓库 `MrYangjf/AdaWeldSys`（分支 `main`）的确定性做法。
> 同步陷阱见 [[lessons/GitHubSyncPitfalls]]。聊天触发见用户级技能 `github-push-adaweld`。

## 1. 仓库初始化（已完成）

```bash
cd /d/焊接程序开发/AdaWeldSystem
git init -b main
git remote add origin https://github.com/MrYangjf/AdaWeldSys.git
```

- 仅备份 `AdaWeldSystem` 目录（工作区另两大目录 `Vicoding管理平台/`、`AdaWeldSystem` 之外的文件不纳入）。
- 默认分支 `main`，远程默认分支也已设为 `main`。

## 2. 忽略规则（`.gitignore`）

必须忽略编译产物与第三方大体积二进制，仓库只留源码：

```gitignore
bin/
obj/
[Bb]in/
[Oo]bj/
*.user
*.suo
.vs/
.code-review-graph/
3rdDepend/        # 第三方 DLL 约 200MB，本地保留，绝不入库
Thumbs.db
Desktop.ini
.DS_Store
*.log
~$*
```

> ⚠️ `3rdDepend/` 是第三方依赖（OpenCV/Emgu/Skia 等），约 200MB，误提交会撑爆仓库、拖慢 clone。**永远不要把它加进版本控制。**

## 3. 凭据（HTTPS + PAT，免密）

PAT 写入本机 `~/.git-credentials`（仅 home，不进工作区）：

```bash
git config --global credential.helper store
printf 'https://MrYangjf:<PAT>@github.com\n' > ~/.git-credentials
chmod 600 ~/.git-credentials
```

- 首次推送即完成认证，之后全自动免密。
- PAT 若在对话中明文出现过，**立即到 GitHub 撤销重发**并更新该文件。

## 4. 确定性同步脚本 `ada_backup.sh`（核心）

所有推送/拉取/校验都锁死在这个脚本里，**不要手写散命令**，避免非快进、漏提交、误提交。

位置：`C:\Users\MrYang\ada_backup.sh`（Git Bash 运行）。

| 子命令 | 行为 |
|---|---|
| `bash ada_backup.sh push [提交信息]` | `add -A` → 有改动才 `commit` → `push origin main`；若远端有新提交自动 `fetch+rebase` 再推；rebase 冲突立即 `abort` 并报错 |
| `bash ada_backup.sh pull` | `fetch` + `rebase` 到本地；冲突即 `abort` 报错 |
| `bash ada_backup.sh status` / `verify` | 单命令内 `fetch` 后比对本地/远端，报告 `ahead`/`behind`/`dirty`/`3rdDepend 误跟踪` |

设计要点：**不依赖 `origin/main` 本地跟踪引用**（沙箱不落盘，见 [[lessons/GitHubSyncPitfalls]]），改用 `git ls-remote` 直连 GitHub 取远端 HEAD 的 SHA 做比对，推送直接 `git push`，rebase 用该 SHA。所有比较都不需要本地 `origin/main`。

## 5. 本地 / 远端一致性校验

`ada_backup.sh status` 输出示例：

```
本地 HEAD : ac502e5...
远端 HEAD : ac502e5...
ahead(本地领先)  : 0
behind(本地落后) : 0
工作区未提交改动  : 0
3rdDepend 误跟踪 : 0 (应为 0)
```

- 四项全 0 → 退出码 0，表示本地与远端完全一致、工作区干净。
- 任一非 0 → 退出码 1，按提示 `push` 或 `pull` 同步。
- `3rdDepend 误跟踪` 必须恒为 0，否则说明忽略规则被破坏。

## 6. 排错

| 现象 | 处理 |
|---|---|
| `push` 报 non-fast-forward | 脚本已自动 `fetch+rebase`；若 rebase 冲突，脚本 `abort` 后按提示手动解决冲突再 `push`。**禁止 `--force`** |
| 认证失败 | 检查 `~/.git-credentials` 中 PAT 是否有效（GitHub 可撤销/重发） |
| `status` 显示 `behind>0` | 本地落后，运行 `bash ada_backup.sh pull` |
| `status` 显示 `ahead>0` 或 `dirty>0` | 本地有未同步改动，运行 `bash ada_backup.sh push` |
| `3rdDepend 误跟踪 >0` | 立即 `git rm -r --cached 3rdDepend` 并从提交中移除，确认 `.gitignore` 含 `3rdDepend/` |

## 7. 持续校验（可选自动化）

可建每日/定期自动化运行 `bash ada_backup.sh status`，一旦发现本地与远端漂移即向用户报告，实现"时刻检验本地文件夹是否匹配"。
