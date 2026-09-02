# GitHub 云端同步陷阱（AdaWeldSystem）

> 把源码推到 GitHub 备份时实际踩到/必须规避的坑。操作手册见 [[guides/SourceBackup-GitHub]]。

## ① 沙箱 `origin/main` 远程跟踪引用跨命令不落盘（最隐蔽）

- **现象**：`git fetch` 当次显示 `[new branch] main -> origin/main`，但下一条 Bash 命令里 `git rev-parse origin/main` 报 `unknown revision`，`git branch -r` 为空，`git status` 显示 `main...origin/main [gone]`。
- **根因**：当前沙箱环境下，远程跟踪引用（`refs/remotes/origin/*`）写入后跨命令不持久化（属本地书签层面问题，非数据丢失）。
- **影响**：**推送/拉取功能完全不受影响**——`git ls-remote` 验证远端 `main` 始终完整存在；只是本地状态栏显示 `[gone]`，以及依赖持久化 `origin/main` 的单独命令会"看不到"。
- **规避**：凡是需要比对本地/远端（ahead/behind）的逻辑，**必须在同一条命令内先 `git fetch` 再比较**（如 `ada_backup.sh status` 的做法）。不要依赖跨命令存活的 `origin/main`。

## ② `3rdDepend` 第三方 DLL 约 200MB 必须忽略

- **现象**：`AdaWeldSystem/3rdDepend/` 含 107 个第三方 DLL（OpenCV/Emgu/Skia 等），单文件最大 `cvextern.dll` 48MB。
- **风险**：一旦 `git add .` 漏配 `.gitignore`，会把 200MB 二进制塞进仓库，clone/push 极慢，且无法从 GitHub 100MB 单文件限制（此处单文件 <100MB 侥幸通过，但整体已不可接受）。
- **规避**：`.gitignore` 必须含 `3rdDepend/`；定期用 `git ls-files | grep -c '^3rdDepend/'` 校验误跟踪数恒为 0；若误提交，立即 `git rm -r --cached 3rdDepend` 并改写历史/新提交移除。

## ③ PAT 明文存 `~/.git-credentials` 有泄露风险

- **现象**：为免密 HTTPS 推送，PAT 以 `https://用户:token@github.com` 形式明文写入 `~/.git-credentials`。
- **风险**：若 PAT 在对话/日志/截图中明文出现，等于把仓库写权限交出去。
- **规避**：PAT 一旦泄露，**立即到 GitHub → Settings → Developer settings 撤销并重发**；新 token 只更新 `~/.git-credentials` 那一行；切勿把 token 写进任何工作区文件或提交。

## ④ non-fast-forward 必须 `fetch+rebase`，禁止 `--force`

- **现象**：若远端有他人/他机的新提交，本地 `push` 会被拒（non-fast-forward）。
- **错误做法**：`git push --force` 会覆盖远端历史，可能丢失别人提交。
- **正确做法**：先 `git fetch origin main`，再 `git rebase origin/main`，解决可能的冲突后 `git push origin main`。冲突无法自动解决时立即 `git rebase --abort` 报错，交人工处理（`ada_backup.sh` 已内置此逻辑）。

## ⑤ CRLF 警告可忽略

- `git add` 时大量 `warning: LF will be replaced by CRLF` 是 Windows 换行符自动转换的正常提示，不影响提交与推送，无需处理。
