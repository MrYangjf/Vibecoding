# AntdUI 官方文档镜像（raw 层· 第三方权威源）

> **本目录是 AntdUI 控件 API 的唯一权威源。**
> 任何属性名 / 事件名 / 事件参数 / 方法签名 / 枚举成员，**先查此目录，再写代码**。

## 来源

| 项 | 值 |
|---|---|
| 上游仓库 | `https://gitee.com/AntdUI/AntdUI` |
| 上游路径 | `doc/wiki/zh/`（中文；`en/` 为英文，本次未取） |
| 镜像日期 | **2026-10-09** |
| 文件数 | **85篇**（`Control/` 68 + `Form/` 3 + 顶层 14） |
| 抓取方式 | Gitee API `contents` + `raw` 端点，逐文件落盘 |
| 许可 | AntdUI 为 MIT 许可库；本目录仅为项目内部参考镜像 |

## 目录结构

```
wiki-zh/
├── Control/        68 个控件文档（Table/Tabs/Menu/Radio/Checkbox/Slider/Modal/Message/...）
├── Form/           3 篇（BaseForm / BorderlessForm / Window）
├── Config.md       全局配置（Config.Theme / IsLight / TextRenderingHint / Animation / ShadowEnabled）
├── Theme.md        主题
├── UpdateLog.md    版本变更史（判「某行为是新版才有还是一直有」的依据）
├── DPI.md / AOT.md / SVG.md / DropdownStyles.md / BlurredFont.md
└── Home.md Install.md PR.md Thanks.md
```

每篇控件文档的结构统一为：**默认属性 / 默认事件 → 属性表（名称|描述|类型|默认值）→ 事件表（名称|描述|返回值|参数）→ 方法表**，部分附代码示例。

## 使用纪律

1. ⛔ **不猜、不反编译 DLL、不从 demo 反推**。该DLL 已混淆，扫字节只能证「有这个名字」，证不出签名；`Reflection.Assembly.LoadFrom` 被本机安全策略拦截。
2. ⚠️ **官方 wiki 不给 .NET 委托类型**。事件表只给语义参数（如 `CheckedChanged` → `bool value`），**不给 `BoolEventHandler` 这类委托类型名**。这一子项属「语义判据」，只有编译器能定，仍须 VS 编译确认。
3. ✅ **属性名 / 事件名 / 方法名 / 方法签名 / 枚举成员 / 默认值** 这六类**已可 100% 核实**，不必再验证。
4. 项目侧提炼页：`wiki/guides/AntdUI-Reference.md`（§0 为权威源索引与已核实结论表，§2 起为本项目约定与踩坑）。
5. 版本对齐：项目 `csproj` 用 `3rdDepend\AntdUI.dll`（**NuGet 未钉版本**），镜像对应上游 `main` 分支。升级 DLL 后若行为异常，先查本目录 `UpdateLog.md`。

## 刷新方式

上游更新后重新镜像（需能访问 gitee；本机 `curl` 被代理拦截，走Python + `ssl.CERT_NONE` 的通道可用）：

```python
# 用 Gitee API contents列举 + raw 下载，逐文件覆盖
# 关键点：verify_mode=CERT_NONE（代理证书不含 keyUsage，会校验失败）
```