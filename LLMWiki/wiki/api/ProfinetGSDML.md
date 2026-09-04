---
title: Profinet GSDML 开发笔记
date: 2026-07-01
tags: [API, Profinet, PLC, GSDML, 通讯]
source: 网络公开资料整理
module: Comm
---

# Profinet GSDML 开发笔记

> **所属模块**：[[modules/Comm]] — Profinet 设备描述文件（GSDML）生成开发参考，基于网络公开资料整理。

## 1. 基本概念

- **GSD（General Station Description）**：描述 Profinet IO-Device 的 XML 文件。
- **GSDML（GSD Markup Language）**：GSD 的 XML 格式。
- **用途**：供 TIA Portal 等工程工具导入，配置现场设备。
- **PC 端限制**：普通 PC 无法直接作为 Profinet IO 控制器运行，通常需要专用硬件或 RTOS。PC 端主要负责生成 GSDML 文件。

## 2. 文件结构

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ISO15745Profile xmlns="http://www.profibus.com/GSDML/2009/11/DeviceProfile">
  <ProfileHeader>
    <ProfileIdentification>GSDML Device Profile</ProfileIdentification>
    <ProfileRevision>1</ProfileRevision>
    <ProfileName>...</ProfileName>
    <ProfileSource>...</ProfileSource>
  </ProfileHeader>
  <ProfileBody>
    <DeviceIdentity VendorID="..." DeviceID="...">
      <InfoText>...</InfoText>
      <VendorName>...</VendorName>
      <OrderNumber>...</OrderNumber>
    </DeviceIdentity>
    <DeviceFunction>
      <Family>...</Family>
    </DeviceFunction>
    <ApplicationProcess>
      <DeviceAccessPointList>...</DeviceAccessPointList>
      <ModuleList>...</ModuleList>
      <SubmoduleList>...</SubmoduleList>
      <ValueList>...</ValueList>
      <LogBookEntryList>...</LogBookEntryList>
      <CategoryList>...</CategoryList>
      <ChannelDiagList>...</ChannelDiagList>
      <ChannelProcessAlarmList>...</ChannelProcessAlarmList>
      <UnitDiagTypeList>...</UnitDiagTypeList>
      <GraphicsList>...</GraphicsList>
      <ExternalTextList>...</ExternalTextList>
    </ApplicationProcess>
  </ProfileBody>
</ISO15745Profile>
```

## 3. 关键元素

| 元素 | 说明 |
|------|------|
| DeviceIdentity | 厂商 ID、设备 ID、厂商名称、订货号 |
| DeviceFunction | 设备家族分类 |
| DeviceAccessPointList | 设备访问点（DAP）定义 |
| ModuleList | 可选模块列表 |
| SubmoduleList | 子模块列表 |
| ValueList | 参数值列表 |
| CategoryList | 设备分类 |
| ChannelDiagList | 通道诊断 |
| ExternalTextList | 多语言文本 |

## 4. 生成步骤

1. 从现有 GSDML 示例文件开始。
2. 使用 XML 编辑器（如 QXmlEdit、CAM editor、XML Notepad）编辑。
3. 使用 **Profinet GSD Checker** 验证文件结构。
4. 修改版本时同步更新：文件名、PNIO_Version 属性、ISO15745Profile schema。

## 5. 编码

文件头必须指定编码：

```xml
<?xml version="1.0" encoding="UTF-8"?>
```

若文本字段含非 ASCII 字符，必须使用 UTF-8。

## 6. 项目实现

- `Comm/Profinet/GSDMLGenerator.cs` — 生成 GSDML 文件到 `Config/GSDML/` 目录（ADR-007）。
- 生成后导入 TIA Portal 配置现场设备，配合专用硬件实现 IO 数据交换。

## 7. 注意事项

- PC 端不能直接作为 Profinet IO-Device 或 Controller。
- GSDML 只是设备描述，真正的实时通信由专用硬件/协议栈完成。
- 版本升级需同步修改文件名、PNIO_Version 和 schema 命名空间。
