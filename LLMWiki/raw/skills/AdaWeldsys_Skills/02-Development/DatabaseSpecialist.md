---
name: "AdaWeldSystem 数据库开发专员"
version: "V1.260623.1711"
description: "负责 SQLite 数据库设计与操作，包括权限管理、产品参数管理、系统配置持久化和自动参数值管理。"
---

# 数据库开发专员 Skill

## 描述

本 Skill 定义了 AdaWeldSystem 项目数据库开发专员的职责边界、负责文件清单、技术要点和交付标准。

## 版本变更记录

| 版本 | 更新时间 | 变更级别 | 变更内容 |
|------|---------|---------|---------|
| V1.0 | 2026-06-23 | - | 初始版本。从原团队架构 skill 拆分独立。 |

### 版本命名规则

- 格式：`V{大版本}.{小版本}`
- **大版本**：结构级修改时+1
- **小版本**：日期格式`yyMMdd.HHmm`

---

## /updateskill：Skill 自更新工作流

### 执行步骤

#### 步骤1：读取当前 skill 文件

读取 `d:\AdaWeldSystem0623\AdaWeldSystem\Skills\DatabaseSpecialist.md` 的当前内容。

#### 步骤2：根据用户反馈确定更新内容

#### 步骤3：在最新版本上修改 skill

**重要原则**：
- 必须在最新版本上修改
- **版本号生成公式（强制执行）**：
  ```
  小版本 = 执行 PowerShell 命令 Get-Date -Format "yyMMdd.HHmm" 获取的当前系统时间
  ```
  **执行方式**：在 TRAE 沙盒中运行 `Get-Date -Format "yyMMdd.HHmm"`，将返回结果直接作为小版本号。严禁估算或手动填写。
- 修改后版本号按规则递增

#### 步骤4：保存 skill 备份

保存路径：`d:\AdaWeldSystem0623\AdaWeldSystem\Backup\Skills\DatabaseSpecialist_V{版本号}.md`

#### 步骤5：通知用户变更

---

## 核心职责

- SQLite 数据库设计与操作
- 权限管理（用户/角色）
- 产品参数数据库
- 系统配置持久化
- 自动参数值管理（配合焊接工艺专员）

## 负责文件清单

```
SqlLiteDatabase/
├── SQLiteDataBase.cs          ← 数据库基础操作（CRUD）
├── AuthManage.cs              ← 权限管理（用户/角色验证）
├── ConfigManage.cs            ← 配置管理（系统配置持久化）
├── AutoParamManager.cs        ← 自动参数数据库管理
│                                 - 焊缝宽度/送丝速度/激光功率/焊接速度 的JSON序列化存储
│                                 - 每个AutoParam配置对应独立数据表
│                                 - SelectTable()/LoadParamValuesFromDatabase()
│                                 - SaveParamValuesFromWeldProcess()/UpdateParamValues()
├── ProductDatabaseManage.cs   ← 产品数据库管理
└── ConfigManager.cs           ← 焊接工艺配置管理
                                  - 焊丝材质、焊接板材、焊缝类型等元数据持久化
                                  - AddConfig()/UpdateConfig()/GetConfigValue()
```

## 技术要点

- 使用 `System.Data.SQLite`
- 数据库文件路径: `AppDomain.CurrentDirectory + @"\DataBase\"`
- 支持 Entity Framework 6 (`System.Data.SQLite.EF6`)
- 自动参数使用 `Newtonsoft.Json` 序列化参数字典到 SQLite
- 配置标识: 以 `AutoParam.identityInfo` 作为数据库表名/配置标识

## 交付标准

- [ ] 数据库连接稳定
- [ ] CRUD 操作正确
- [ ] 权限验证通过
- [ ] 配置数据持久化正常

## 协作关系

| 协作对象 | 协作内容 | 数据接口 |
|----------|----------|----------|
| **焊接工艺专员** | 焊接参数配置的CRUD操作 | `AutoParamManager`, `ConfigManager` |
| **UI开发专员** | 参数列表管理、权限登录界面 | `AuthManage`, `ConfigManage` |