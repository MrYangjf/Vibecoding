---
title: 台达 EtherCAT 部署规范（驱动 · 原生库 · 项目内落地）
date: 2026-09-07
updated: 2026-09-07
tags: [指南, 运控, 台达, EtherCAT, 部署, DLL, 驱动]
source: 台达安装程序 `C:\Program Files (x86)\Delta Industrial Automation\EtherCAT\` + `manual/API/DELTA EtherCAT UserGuild.pdf` 第 1 章
---

# 台达 EtherCAT 部署规范

> **依据（权威来源）**：台达安装程序目录 `C:\Program Files (x86)\Delta Industrial Automation\EtherCAT\`，
> 其中 `manual/API/DELTA EtherCAT UserGuild.pdf` 第 1 章「EtherCAT 安裝指南」为官方部署步骤，
> `EtherCAT\CopyCmdx86.bat` / `CopyCmdx64.bat` 为官方部署脚本，`sample/C#/Copy.bat` 为官方源码分发脚本。
> **本页是官方步骤在本项目中的落地约定**，与官方文档冲突时以官方文档为准并回灌本页。

## 章节导航

- [1. 官方部署三步法](#1-官方部署三步法)
- [2. 文件清单与落位对照](#2-文件清单与落位对照)
- [3. 项目内做法（3rdDepend + 输出目录）](#3-项目内做法3rddepend--输出目录)
- [4. 条件编译与平台约定](#4-条件编译与平台约定)
- [5. 部署校验清单](#5-部署校验清单)
- [6. 常见故障与定位](#6-常见故障与定位)

---

## 1. 官方部署三步法

来源：`manual/API/DELTA EtherCAT UserGuild.pdf` §1.1（64 位元手動安裝步驟）· §1.2（32 位元）。

**STEP 1 — 控制卡 Windows 驅動程式安裝**
裝置管理員 → 找到未安裝驅動的 PCI/PCIe 設備 → 右鍵「更新驅動程式」→「瀏覽電腦上的驅動程式軟體」→ 選目錄：

```
C:\Program Files (x86)\Delta Industrial Automation\EtherCAT\driver
```

**STEP 2 — 應用的資料安裝（系統級）**

| 目標位元 | 複製來源 | 目的地 |
|---|---|---|
| 64 位元 | `EtherCAT_DLL_x64.dll` + `msvcr100.dll` | `C:\Windows\System32\` |
| 64 位元 | `EtherCAT_DLL.dll`（x86 版）+ `msvcr100.dll` | `C:\Windows\SysWOW64\` |
| 32 位元 | `EtherCAT_DLL.dll` + `msvcr100.dll` | `C:\Windows\System32\` |

**STEP 3 — 運行環境**

- SDK 目錄整體置於 `C:\Program Files (x86)\Delta Industrial Automation\EtherCAT\`（安裝程序默認，勿改）。
- `WinRoot` 裡的 `EtherCAT` 資料夾複製到 `C:\`（即 **`C:\EtherCAT\`**），內含 `ESI/`、`AutoConf/`、`Config/`、`ECAT_Comm0.xml`——**從站描述檔（ESI）與自動配置 DAT 的工作目錄，缺此目錄 EcNavi 與自動配置不可用**。

> 官方 `CopyCmdx64.bat` 額外把 `BMCH_11X1_MD1_64.sys` / `PCI_L221_B1_64.sys` / `PCI_L221_P1_64.sys` 複製到 `C:\Windows\System32\drivers\`，並先刪除舊的 RTSS/RTDLL 殘留（`ECAT_STACK_*` / `ECAT_RTX_*`）。

---

## 2. 文件清单与落位对照

| 文件 | SDK 来源 | 系统级落位（官方） | 项目内落位（本项目） |
|---|---|---|---|
| `EtherCAT_DLL_x64.dll`（168,744,448 B） | `dll\EtherCAT_DLL_x64.dll` | `C:\Windows\System32\` | `AdaWeldSystem\3rdDepend\` → 输出到 `bin\x64\Debug\` |
| `EtherCAT_DLL.dll`（x86，169,133,056 B） | `dll\EtherCAT_DLL.dll` | `C:\Windows\SysWOW64\` | **不纳入**（项目 `PlatformTarget=x64`，无 x86 配置） |
| `msvcr100.dll` | 安装包 `System32/` | `C:\Windows\System32\` | 不纳入（系统已具备，见 §5） |
| 驱动 `*.sys` / `*.inf` / `*.cat` | `driver\` | `C:\Windows\System32\drivers\` | 不纳入（需管理员安装，走设备管理器） |
| `C:\EtherCAT\`（ESI/AutoConf/Config） | 安装包 `WinRoot\EtherCAT` | `C:\EtherCAT\` | 不纳入（运行期目录） |
| P/Invoke 声明 `EtherCAT_DLL_x64.cs` | `inc\C#\` | — | **不复制**：本仓自持 `MotionControl\DeltaEtherCAT\Native\*.cs` |

> **为何不复制官方 `EtherCAT_DLL_x64.cs`**：官方 `sample/C#/Copy.bat` 把整份 20 万字节头文件拷进每个示例工程（832 个 API 全量声明）。本项目按 [[guides/DeltaEtherCAT-DevGuide]] 只落地用到的 API，分层收在 `Native/`（见 [[api/DeltaEtherCAT-Native]] 全量速查）。

---

## 3. 项目内做法（3rdDepend + 输出目录）

用户裁定（2026-09-07）：**DLL 复制到项目内，随构建输出到 `bin`，不依赖系统目录**。

**3.1 放置**

```bash
cp "C:/Program Files (x86)/Delta Industrial Automation/EtherCAT/dll/EtherCAT_DLL_x64.dll" \
   AdaWeldSystem/3rdDepend/EtherCAT_DLL_x64.dll
```

**3.2 注册到 csproj（已落地）**

`AdaWeldSystem.csproj` → `Target Name="CopyNative3rdDependToOutput" AfterTargets="Build"`：

```xml
<!-- 台达 EtherCAT 原生依赖：主站库（x64，与 PlatformTarget 一致，禁 AnyCPU） -->
<Native3rdDepend Include="3rdDepend\EtherCAT_DLL_x64.dll" />
```

构建后自动拷贝到 `$(TargetDir)`（`SkipUnchangedFiles=true`）。

> ⚠️ `3rdDepend/` 被 `.gitignore` 整体忽略，**不入版本库**；新机器需按本页 §3.1 自行复制，或从备份 `AdaWeldSystem_backup_*.tar.gz` 恢复。

**3.3 与官方做法的差异（有意为之）**

| 维度 | 官方 | 本项目 | 理由 |
|---|---|---|---|
| 主库位置 | `C:\Windows\System32` | 项目 `3rdDepend` → `bin` | 不污染系统目录、可多版本并存、随仓备份 |
| 加载方式 | 系统目录搜索路径 | 应用程序目录优先 | Win32 加载顺序中**应用目录先于 System32**，故无需改代码 |
| 系统级副本 | 必须 | **可选**（目标机已具备） | 双重存在不冲突；若删系统副本，本项目仍可运行 |
| 驱动 | 设备管理器安装 | 同官方 | **不可省略**，无驱动则 `Master_Open` 返回卡数 0 |

---

## 4. 条件编译与平台约定

台达官方 C# 示例（`sample/C#/*/EtherCat.csproj`）按平台定义 `X86` 常量，源码用命名空间切换：

```csharp
#if X86
using EtherCAT_DLL;          // strDLL_Path = "EtherCAT_DLL.dll"      (x86)
#else
using EtherCAT_DLL_x64;      // strDLL_Path = "EtherCAT_DLL_x64.dll"  (x64)
#endif
```

本仓对应实现在 `MotionControl/DeltaEtherCAT/Native/EtherCATMasterNative.cs`：

```csharp
#if X86
    private const string DllPath = "EtherCAT_DLL.dll";
#else
    private const string DllPath = "EtherCAT_DLL_x64.dll";
#endif
```

规则：

1. 本项目 `AdaWeldSystem.csproj` **仅 x64 配置**（第 34 / 48 行 `PlatformTarget=x64`），`X86` 未定义 → 恒走 x64 分支，与已部署的 `EtherCAT_DLL_x64.dll` 一致。
2. 若日后新增 x86 平台配置，**必须**在该配置加 `<DefineConstants>...;X86</DefineConstants>`，并把 `3rdDepend\EtherCAT_DLL.dll`（x86 版）纳入 `Native3rdDepend`，否则会加载错位数的库。
3. **禁 AnyCPU**：原生库位数固定，AnyCPU 会在 x64 机器上以 64 位进程加载，误配 x86 库即 `BadImageFormatException`。

---

## 5. 部署校验清单

在目标机逐项确认（本机 2026-09-07 实测状态见「现状」列）：

| # | 检查项 | 命令 / 位置 | 现状 |
|---|---|---|---|
| 1 | 主站卡驱动已装 | 设备管理器无未知设备；`driver\*.sys` 已入 `System32\drivers` | ⚠️ 未落 `System32\drivers`，需设备管理器确认 |
| 2 | `C:\EtherCAT\` 存在 | `ls C:\EtherCAT` 含 `ESI` / `AutoConf` / `Config` | ✅ |
| 3 | 系统级 x64 库 | `C:\Windows\System32\EtherCAT_DLL_x64.dll` | ✅ 168,744,448 B |
| 4 | 系统级 x86 库 | `C:\Windows\SysWOW64\EtherCat_DLL.dll` | ✅ 169,133,056 B |
| 5 | VC++ 2010 运行库 | `C:\Windows\System32\msvcr100.dll` | ✅ |
| 6 | 项目内库 | `AdaWeldSystem\3rdDepend\EtherCAT_DLL_x64.dll` | ✅ 与系统副本同尺寸 |
| 7 | csproj 已注册 | `grep Native3rdDepend AdaWeldSystem.csproj` | ✅ 第 737 行 |
| 8 | 构建输出 | `AdaWeldSystem\bin\x64\Debug\EtherCAT_DLL_x64.dll` | ⏳ 待 VS 构建后确认 |
| 9 | 残留清理 | `bin\Debug` 无 `zauxdll.dll` / `zmotion.dll` / `ZmotionScanLaser.dll` | ⚠️ 仍有残留，需手工清理 |

---

## 6. 常见故障与定位

| 现象 | 根因 | 定位 |
|---|---|---|
| `Master_Open` 返回卡数 0 | 驱动未装 / 板卡未插好 | 设备管理器；确认 STEP 1 |
| `BadImageFormatException` | 位数不匹配（x86 库配 x64 进程，或反之） | 查 §4；确认 `PlatformTarget` 与 DLL 名 |
| `DllNotFoundException: EtherCAT_DLL_x64.dll` | `bin` 输出目录缺库 | 查 §5 第 7/8 项；确认构建已跑 `CopyNative3rdDependToOutput` |
| `Check_Initial_Done` 长期返回 1 或 99 | 从站未上电 / ESI 不匹配 / 网线未接 | `OpState==3` 判据；用 EcNavi (`app\EcNavi_x64.exe`) 扫描 |
| `0x1002` 错误码 | **模式切换失败**（`ERR_ECAT_MODE_CHANGE_FAILED`） | 不是「从站初始化失败」——规范页早期误注，已订正 |
| EcNavi 找不到从站型号 | 缺 ESI 文件 | 放 `C:\EtherCAT\ESI\`，由硬件厂商提供 |

---

## 关联

- [[guides/DeltaEtherCAT-DevGuide]] — 台达落地开发规范（API / 调用范式 / 错误码）
- [[modules/MotionControl]] — 运控模块（三层架构）
- [[api/DeltaEtherCAT-Native]] — 台达原生 API 全量速查
- [[decisions/ADR-036-MotionControllerDeltaReplacement]] — 台达替换决策
- [[decisions/ADR-037-ZMotionRemovalAndDeltaLanding]] — 正运动移除与台达落地（含原生依赖段改写）
