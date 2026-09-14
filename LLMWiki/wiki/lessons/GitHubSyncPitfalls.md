# GitHub 云端同步陷阱（AdaWeldSystem / LLMWiki）

> 把源码与知识库推到 GitHub 备份时实际踩到/必须规避的坑。操作手册见 [[guides/SourceBackup-GitHub]]。
> 本页 2026-09-14 修订：② 量级更正、③ 标记沿革（已改 SSH）、新增 ⑥⑦。

## ① 沙箱 `origin/main` 远程跟踪引用跨命令不落盘（最隐蔽）

- **现象**：`git fetch` 当次显示 `[new branch] main -> origin/main`，但下一条 Bash 命令里 `git rev-parse origin/main` 报 `unknown revision`，`git branch -r` 为空，`git status` 显示 `main...origin/main [gone]`。
- **根因**：当前沙箱环境下，远程跟踪引用（`refs/remotes/origin/*`）写入后跨命令不持久化（属本地书签层面问题，非数据丢失）。
- **影响**：**推送/拉取功能完全不受影响**——`git ls-remote` 验证远端 `main` 始终完整存在；只是本地状态栏显示 `[gone]`，以及依赖持久化 `origin/main` 的单独命令会"看不到"。
- **规避**：凡是需要比对本地/远端（ahead/behind）的逻辑，**必须在同一条命令内先 `git fetch` 再比较**（早期由 `ada_backup.sh` 内置，该脚本已于 2026-09-14 前退役）。不要依赖跨命令存活的 `origin/main`。

## ② `3rdDepend` 第三方 DLL 实测 380MB，且单文件已超 GitHub 100MB 硬限制（2026-09-14 更正量级）

- **现象**：`AdaWeldSystem/3rdDepend/` 实测 **380 MB / 127 个文件**（OpenCV / Emgu / EtherCAT / Skia 等），单文件最大 **`EtherCAT_DLL_x64.dll` 160 MB**，其次 `cvextern.dll` 45 MB、`opencv_videoio_ffmpeg4130_64.dll` 27 MB。
- **风险**：⚠️ **160 MB > GitHub 单文件 100 MB 硬限制**——一旦 `git add .` 漏配 `.gitignore`，**推送会被服务端直接拒绝**（不是"慢"而是"推不上去"），必须改写历史才能补救。旧版本页曾写"单文件最大 cvextern.dll 48MB，侥幸通过"，**该判断已不成立**。
- **规避**：`.gitignore` 必须含 `3rdDepend/`；定期用 `git ls-files | grep -c '^3rdDepend/'` 校验误跟踪数恒为 0；若误提交，立即 `git rm -r --cached 3rdDepend` 并改写历史/新提交移除。`bin/` 下的同名 DLL 与 `Records/*.ply`（50MB）同理，靠 `bin/` 规则兜住。

## ③ PAT 明文存 `~/.git-credentials` 有泄露风险

> ℹ️ **沿革（2026-09-14）**：两仓远程**已全部改为 SSH over 443**（`ssh://git@ssh.github.com:443/...`），不再使用 HTTPS + PAT，`~/.git-credentials` 已非必需。本条保留为"若将来回退到 PAT 方案"的警示。

- **现象**：为免密 HTTPS 推送，PAT 以 `https://用户:token@github.com` 形式明文写入 `~/.git-credentials`。
- **风险**：若 PAT 在对话/日志/截图中明文出现，等于把仓库写权限交出去。
- **规避**：PAT 一旦泄露，**立即到 GitHub → Settings → Developer settings 撤销并重发**；新 token 只更新 `~/.git-credentials` 那一行；切勿把 token 写进任何工作区文件或提交。

## ④ non-fast-forward 必须 `fetch+rebase`，禁止 `--force`

- **现象**：若远端有他人/他机的新提交，本地 `push` 会被拒（non-fast-forward）。
- **错误做法**：`git push --force` 会覆盖远端历史，可能丢失别人提交。
- **正确做法**：先 `git fetch origin main`，再 `git rebase origin/main`，解决可能的冲突后 `git push origin main`。冲突无法自动解决时立即 `git rebase --abort` 报错，交人工处理。

## ⑤ CRLF 警告可忽略

- `git add` 时大量 `warning: LF will be replaced by CRLF` 是 Windows 换行符自动转换的正常提示，不影响提交与推送，无需处理。

## ⑥ `git status` 的大批删除项必须与重命名对账，先分清「真删」与「改名」（2026-09-14）

- **现象**：知识库仓 `git status` 一次报出 **1166 项 `D`**，看上去像把整个目录删了。实际是 `raw/mecavision` 的**目录名从 GBK 乱码修正为正常名**——git 里存的路径是 `MecaVision_SDK+²¦¦+¦-Á+¸+-ÁÁ`（GBK 字节被当 UTF-8 解码），磁盘上已改为 `MecaVision_SDK/`，git 无法把这批全部识别为重命名。
- **对账方法**：先分类计数，再验等式——
  ```bash
  git diff --cached --name-status | awk '{print substr($1,1,1)}' | sort | uniq -c
  # D + R 应等于最初 status 报出的删除数（本例 963 D + 203 R = 1166 ✓ 完全对上）
  ```
- **再分「真删」**：`git ls-files <dir> | wc -l` vs `find <dir> -type f | wc -l`；差额用扩展名分布看删了什么（本例剔除了 155 `.h` / 103 `.cpp` / 47 `.vb` / 22 `.vi` 等 C++/VB/LabVIEW demo 与编译产物，1160 → 206，保留 C# demo + SDK 头文件 + 驱动）。
- **教训**：**看到大批 `D` 不要慌，也不要盲目 `git checkout` 恢复**——先对账。乱码路径在 Linux/macOS 上还会导致 checkout 失败，属必须修正的仓库卫生问题。

## ⑦ 推送前必做「四查」清单（2026-09-14 定型）

按序执行，任一不过就不推：

1. **连通与远程**：`git remote -v` 确认 URL（本仓为 SSH over 443）；`ssh -T -p 443 git@ssh.github.com` 期望 `Hi <user>!`；确认本地 HEAD 与 `origin/main` 一致（无未拉取提交）。
2. **大文件双查**——历史与待提交都要查，因 GitHub 有**单文件 100 MB 硬限制**：
   ```bash
   # ① 历史（已入库的，push 会连带传输）
   git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)'      | awk '$1=="blob" && $3>50000000 {printf "%8.1f MB  %s
", $3/1048576, $4}' | sort -rn | head
   # ② 待提交
   git status --porcelain -uall | sed 's/^...//' | tr -d '"'      | while read f; do [ -f "$f" ] && [ "$(stat -c%s "$f")" -gt 5000000 ]          && echo "$(( $(stat -c%s "$f")/1048576 )) MB $f"; done
   ```
3. **`.gitignore` 覆盖大依赖目录**：代码仓必须覆盖 `3rdDepend/`（380 MB，单文件 160 MB > 限制）；用 `git ls-files | grep -c '^3rdDepend/'` 验误跟踪恒为 0。⚠️ 只对**未跟踪**文件生效。
4. **删除项对账 + diff 性质甄别**：删除项按 ⑥ 对账；再用 `git diff --numstat | awk '$1==$2 && $1>50'` 查是否混入**行尾噪音**（命中大量文件 = 整文件重写，须先修行尾再提交）。
