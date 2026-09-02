---
title: S7NetPlus / S7.Net 使用笔记
date: 2026-07-01
tags: [API, PLC, 西门子, S7, 通讯]
source: 网络公开资料整理
module: Comm
---

# S7NetPlus / S7.Net 使用笔记

> **所属模块**：[[modules/Comm]] — 西门子 S7 PLC 通讯开发参考，基于网络公开资料整理。

## 1. 安装

引用方式：本地 DLL 引用（ADR-028 NuGet 本地化）

```xml
<Reference Include="S7.Net">
  <HintPath>bin\Debug\3rdDepend\S7.Net.dll</HintPath>
  <Private>True</Private>
</Reference>
```

命名空间：

```csharp
using S7.Net;
```

## 2. 数据类型映射

| PLC 类型 | C# 类型 |
|---------|--------|
| Bit     | bool   |
| Byte    | byte   |
| Word    | ushort |
| DWord   | uint   |
| Int     | short  |
| DInt    | int    |
| Real    | float  |
| LReal   | double |
| String  | string |

## 3. 创建连接

```csharp
Plc plc = new Plc(CpuType.S71500, "192.168.0.101", 0, 1);
plc.Open();
if (plc.IsConnected)
{
    // 读写操作
}
plc.Close();
```

参数说明：
- `CpuType`：CPU 型号（S7200, S7300, S7400, S71200, S71500 等）
- IP 地址
- Rack（机架号）
- Slot（插槽号）

## 4. 读取变量

```csharp
bool db1Bool1 = (bool)plc.Read("DB1.DBX0.0");
bool db1Bool2 = (bool)plc.Read("DB1.DBX0.1");
short intVar = (short)plc.Read("DB1.DBW2.0");
float realVar = ((uint)plc.Read("DB1.DBD4.0")).ConvertToFloat();
int dIntVar = (int)plc.Read("DB1.DBD8.0");
uint dWordVar = (uint)plc.Read("DB1.DBD12.0");
ushort wordVar = (ushort)plc.Read("DB1.DBW16.0");
```

## 5. 写入变量

```csharp
plc.Write("DB1.DBX18.0", true);
plc.Write("DB1.DBW20.0", Convert.ToInt16(123));
plc.Write("DB1.DBD22.0", Convert.ToSingle(11.111f));
plc.Write("DB1.DBD26.0", 123);
plc.Write("DB1.DBD30.0", Convert.ToUInt32(22));
plc.Write("DB1.DBW34.0", Convert.ToUInt16(33));
```

## 6. 读取字节块

```csharp
byte[] bytes = plc.ReadBytes(DataType.DataBlock, 1, 0, 36);
```

## 7. 注意事项

- TIA Portal 中 DB 块需**取消"优化的块访问"**，否则 S7 协议无法按地址访问。
- 使用 S7-PLCSIM Advanced 仿真时，项目属性需勾选"块编译支持仿真"。
- `Real` 在 PLC 中占 4 字节，读取时按 `uint` 再 `ConvertToFloat()`。
- 连接失败常见原因：IP 不通、机架/插槽号错误、PLC 未启用 PUT/GET 通信、防火墙。

## 8. 参见

- `Comm/SiemensS7/S7PLCCommunication.cs` — 项目封装类
