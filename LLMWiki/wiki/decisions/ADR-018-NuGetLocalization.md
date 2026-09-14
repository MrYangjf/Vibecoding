---
title: ADR-018 NuGet 本地化 — 所有依赖 DLL 从 3rdDepend 引用
date: 2026-08-06
tags: [决策, NuGet, 本地化, 依赖管理, 构建]
status: accepted
---

# ADR-018 NuGet 本地化 — 所有依赖 DLL 从 3rdDepend 引用

> **状态**：accepted | **日期**：2026-08-06

## 背景

项目原使用 `PackageReference` 方式引用 19 个 NuGet 包（含传递依赖共 ~80 个托管 DLL + ~30 个原生 DLL）。每次构建需从 NuGet 源或本地缓存解析依赖，存在以下问题：

1. **离线不可用**：无网络时无法还原包
2. **版本漂移风险**：NuGet 源更新可能导致意外升级
3. **构建环境依赖**：新机器需先执行 `nuget restore` 才能构建
4. **部署复杂性**：需确保 NuGet 缓存与目标环境一致

## 决策

将所有 NuGet 包 DLL 本地化，统一存放于 `bin\Debug\3rdDepend\` 目录：

- **移除**：.csproj 中所有 `<PackageReference>` 条目（19 个）
- **替换为**：`<Reference Include="...">` + `<HintPath>bin\Debug\3rdDepend\*.dll</HintPath>` + `<Private>True</Private>`
- **原生 DLL**：通过 `<Target Name="CopyNative3rdDependToOutput">` 在构建后从 3rdDepend 拷贝到输出目录
- **SQLite.Interop.dll**：按架构（x64/x86）分别存放于 `3rdDepend\x64\` 和 `3rdDepend\x86\`，构建时拷贝到对应输出子目录
- **卫星程序集 Target**：`RemoveNonEnglishSatelliteAssemblies` 已移除（本地引用不再产生卫星程序集）

## 影响范围

| 类别 | 数量 | 说明 |
|------|------|------|
| 托管 Reference | 53 | 含直接包 + 传递依赖（CommunityToolkit、SharpDX、System.* 等） |
| 原生 DLL 拷贝 | 28 | Emgu.CV/FFmpeg、HelixToolkit/GLib、VC Runtime 等 |
| SQLite.Interop | 2 | x64/x86 架构相关 |
| 移除的 PackageReference | 19 | Emgu.CV×4、HelixToolkit×4、SQLite×4、STTech×3 等 |

## 保持不变

- `Libs\IntelligentLaser\` — 英莱相机 SDK（非 NuGet，保持原有引用方式）
- `Libs\MvCameraControl\` — 海康相机 SDK（非 NuGet，保持原有引用方式）
- `SRAPI_CSharp-x64.dll` — SmartRay SDK（外部路径引用）
- `Mv3dLpNet.dll` — 海康 3D SDK（外部路径引用）

## 注意事项

1. **新增/更新 NuGet 包**：需手动将 DLL 复制到 `3rdDepend\`，并在 .csproj 中添加 `<Reference>` 条目
2. **3rdDepend 目录位置**：位于 `bin\Debug\3rdDepend\`，与输出目录同级。Clean 操作不会删除此目录
3. **PDB 文件**：3rdDepend 中也包含 PDB 调试符号文件（从 bin\Debug 复制），但不作为 Reference 引用
4. **构建验证**：需通过 Visual Studio 或安装了 Roslyn 的 MSBuild 构建（.NET Framework 4.0 自带 MSBuild 不支持 C# 7.3+ 语法）
5. **NuGet 残留清理**（2026-08-06 补充）：
   - 已删除 `NuGet.Config`（旧 NuGet.Config 本地源方案产物）
   - 已删除 `NuGetPackages/` 空文件夹（旧方案残留）
   - 已删除 `NuGet本地化操作指南.md`（旧方案文档）
   - `obj/` 中 NuGet 自动生成文件（`project.assets.json`、`*.nuget.g.props/targets`）已由 VS 清理
   - **教训**：切换 PackageReference → Reference 后，必须清理 obj/ 中的 NuGet 产物，否则 MSBuild 仍会导入 NuGet 缓存中的 build targets

## 补充：3rdDepend 移至项目根 + Private=True 标准模式（2026-08-06 最终）

**问题**：3rdDepend 放在 `bin\Debug\3rdDepend\`（输出子目录）导致 rebuild 后自动重建无法清除，且 `<Private>False</Private>` + `AppendPrivatePath` 方案增加复杂度。

**最终方案**：
1. **3rdDepend 源文件夹位于项目根目录 `AdaWeldSystem\3rdDepend\`**（不在 bin\ 下，Clean 不删除）
2. **全部 58 个第三方引用 HintPath 指向 `3rdDepend\*.dll`**
3. **全部设为 `<Private>True</Private>`**（标准模式：构建时复制到输出目录）
4. **`Program.cs` 无 `AppendPrivatePath`**（DLL 直接在输出目录，无需额外探测）
5. **`CopyIntelligentLaserNative` 仅拷贝 `Libs\IntelligentLaser\native\*.dll`**（原生 DLL 供 DllImport）
6. **`CopyNative3rdDependToOutput` 从 `3rdDepend\` 拷贝原生 DLL 到输出根**（assimp/FFmpeg/VC Runtime 等）

**教训**：
- 第三方 DLL 源文件夹不应放在 `bin\` 下（输出目录的子目录会被 rebuild 重建）
- `<Private>True</Private>` + 项目根目录源 = 标准 MSBuild 行为，简单可靠
- `AppendPrivatePath` 仅在 DLL 保留在子目录不复制时才有必要

## 补充：框架程序集引用修复（2026-08-06）

切换 PackageReference → Reference 后，`System.Numerics` 框架程序集引用丢失，导致编译错误：

> 未能在命名空间"System.Numerics"中找到类型名"Vector3"

**原因**：`System.Numerics.Vectors`（NuGet 包）已通过 3rdDepend 引用，但 `Vector3` 类型通过 type-forwarding 转发到 `System.Numerics`（GAC 框架程序集），需单独添加引用。

**修复**：在 .csproj 系统引用区域添加 `<Reference Include="System.Numerics" />`（无 HintPath，由 GAC 自动解析）。

**教训**：NuGet 包 `System.Numerics.Vectors` 不等于框架程序集 `System.Numerics`，两者需分别引用。

## 参考

- [[guides/Project-Tools]] — 已被本决策替代（卫星程序集清理不再需要）
- 相关文件：`AdaWeldSystem/AdaWeldSystem.csproj`
