# AdaWeldSystem / LLMWiki 云端源码备份（GitHub）操作手册

> 两个独立仓库备份到 GitHub，分支均为 `main`。同步陷阱见 [[lessons/GitHubSyncPitfalls]]。
> 本页 2026-09-14 按实况重写：路径、远程 URL、凭据方式、仓数量和脚本现状均与旧版不同。

## 1. 仓库结构（双仓）

| 仓 | 本地路径 | 远程 |
|---|---|---|
| 代码 | `<工作区>/AdaWeldSystem/` | `ssh://git@ssh.github.com:443/MrYangjf/AdaWeldSys.git` |
| 知识库 | `<工作区>/Vicoding管理平台/` | `ssh://git@ssh.github.com:443/MrYangjf/Vibecoding.git` |

- `<工作区>` 指 `D:\A-A-项目类\04_研发项目\MRDF-2608 自适应焊接系统\workbudddy`。
- **工作区根目录自身不是 git 仓**——两个子目录各为独立仓，顶层无 `.git`。推 LLMWiki 要进 `Vicoding管理平台/`，推代码要进 `AdaWeldSystem/`。
- 工作区根的备份包（`AdaWeldSystem_backup_*.tar.gz`、`AdaWeldSystem_output_*.tar.gz`、`LLMWiki_backup_*.tar.gz`）**不在任何仓库内**（由 `backup_adaweld.py` 统一生成，落点=工作区根），属本地快照，不入库。
- 默认分支 `main`。

## 2. 忽略规则（`.gitignore`）

两仓各自维护一份。

**代码仓**——只留源码，忽略编译产物与第三方大体积二进制：

```gitignore
bin/
obj/
[Bb]in/
[Oo]bj/
*.user
*.suo
*.userosscache
.sln.docstates
.vs/
.code-review-graph/
3rdDepend/
Thumbs.db
Desktop.ini
.DS_Store
*.log
~$*
```

> ⚠️ `3rdDepend/` 实测 **380 MB / 127 个 DLL**，单文件最大 `EtherCAT_DLL_x64.dll` **160 MB**——**已超 GitHub 100 MB 单文件硬限制**，一旦入库推送会被直接拒绝。**永远不要把它加进版本控制。**

**知识库仓**——忽略构建产物、本地备份包与临时脚本：

```gitignore
bin/
obj/
[Dd]ebug/
[Rr]elease/
*.pyc
__pycache__/
.vs/
*.user
*_backup_*.tar.gz
LLMWiki_backup_*.tar.gz
_tmp_*.py
```

## 3. 凭据（SSH over 443）

两仓远程均为 **SSH**（非 HTTPS + PAT），端口走 **443** 以穿透受限网络：

```bash
ssh -T -p 443 git@ssh.github.com
# 期望输出：Hi <user>! You've successfully authenticated, but GitHub does not provide shell access.
```

- 依赖本机 SSH 私钥（`~/.ssh/`），**无需** `~/.git-credentials`，也**不要**在仓库或工作区留存任何 token。
- 改远程：`git remote set-url origin ssh://git@ssh.github.com:443/<owner>/<repo>.git`。
- 沿革：早期曾用 HTTPS + PAT 明文写 `~/.git-credentials`，该方案已废弃（风险见 [[lessons/GitHubSyncPitfalls]] ③）。

## 4. 推送流程

~~早期封装的确定性脚本 `ada_backup.sh` 与其聊天触发技能 `github-push-adaweld` 均已退役~~（工具与脚本都不存在了，**不要再去调用**）。现按裸命令流程操作，**逐仓各执行一遍**：

```bash
cd <仓根>
git status --porcelain | head          # 先看改动面貌
git add -A
git diff --cached --shortstat          # 复核改动规模
git commit -F - <<'MSGEOF'
<提交信息>
MSGEOF
git push origin main
```

推送前的**必做四查**见 [[lessons/GitHubSyncPitfalls]] ⑦——尤其是大文件排查与删除项对账。

## 5. 本地 / 远端一致性校验

```bash
cd <仓根>
git rev-parse HEAD ; git rev-parse origin/main    # 两个 SHA 应相同
git status --short                                # 应为空
git ls-remote origin main | cut -c1-12            # 远端 HEAD 的权威取值
```

- 三项全绿（本地 SHA = 远程 SHA + 工作区干净 + `rev-parse origin/main` 吻合）即为完全同步。
- `git ls-remote` 是唯一权威的远端取值方式，**不依赖**本地 `origin/main` 跟踪引用（该引用在部分环境下跨命令不落盘，见 [[lessons/GitHubSyncPitfalls]] ①）。

## 6. 排错

| 现象 | 处理 |
|---|---|
| `push` 报 non-fast-forward | 先 `git fetch origin main` 再 `git rebase origin/main`；冲突立即 `git rebase --abort` 报错。**禁止 `--force`** |
| SSH 连接超时 | 确认走的是 `ssh.github.com:443` 而非 `github.com:22`；用 `ssh -T -p 443 git@ssh.github.com` 单独测 |
| `ssh -T` 报 Permission denied | 检查私钥是否加载（`ssh-add -l`）、公钥是否已加到 GitHub 账号 |
| 工作区出现大批 `D` 删除项 | **先对账再提交**——可能只是目录改名（应被识别为 `R`）而非真删，见 [[lessons/GitHubSyncPitfalls]] ⑥ |
| `3rdDepend 误跟踪 >0` | 立即 `git rm -r --cached 3rdDepend`，确认 `.gitignore` 含 `3rdDepend/` |
| 提交后远端仍缺文件 | 确认进对了仓（代码 / 知识库是两个独立仓，见第 1 节） |

## 7. 持续校验（可选自动化）

可建定期自动化运行第 5 节的校验命令，发现本地与远端漂移即报告。
