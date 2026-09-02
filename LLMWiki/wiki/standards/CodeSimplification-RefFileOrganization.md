# 文件书写整理规则

> **归属（2026-09-01）**：本页是 [[standards/CodeSimplification]] 的配套深度反例/工作流，原位于 `wiki/standards/references/`，已扁平化为 `standards/` 下的独立文件。**standards/ 全库禁止子目录**——所有页面一律平铺为文件，靠命名前缀 `CodeSimplification-` 成组。

适用 .NET Framework 4.8 / C# 7.3。规范单个 `.cs` 文件内部的成员排列、`#region` 划分与 XML 注释格式。

## 目录

1. [成员排列顺序](#1-成员排列顺序)
2. [Region 划分要求](#2-region-划分要求)
3. [XML 注释规范](#3-xml-注释规范)
4. [常见问题](#4-常见问题)

---

## 1. 成员排列顺序

文件内成员按以下固定顺序自上而下排列。一个类内部严格遵循；多个类共存于同一文件时，每个类各自遵循。

| 顺序 | 成员类型 | 说明 |
|------|----------|------|
| 1 | 类声明 | `class` / `struct` 头部及特性 |
| 2 | 私有变量（字段） | `private` / `private static` / `private readonly` 字段，`_camelCase` 命名 |
| 3 | 公共变量（属性/公共字段） | `public` 属性；公共字段仅在 `const` 或互操作结构时允许 |
| 4 | 构造函数 | 实例构造函数、静态构造函数 |
| 5 | 私有函数 | `private` 方法 |
| 6 | 公共函数 | `public` / `protected` 方法 |

补充约定：

- 事件（`event`）归入公共变量区域，紧邻属性之前或之后，保持类内一致。
- 嵌套类型放在所有成员之后，用独立 region。
- 显式接口实现放在公共函数区域之后，用独立 region。
- 不要按"添加时间"或"功能迭代轮次"堆叠成员——AI 迭代时常把新成员追加到类末尾，导致顺序混乱。

---

## 2. Region 划分要求

使用 `#region` / `#endregion` 将上述每个区域包裹，region 名称使用中文，与成员类型对应：

```csharp
public class OrderService
{
    #region 私有变量
    private readonly IOrderRepository _repository;
    private int _retryCount;
    #endregion

    #region 公共变量
    public string ServiceName { get; }
    public event EventHandler<OrderEventArgs> OrderCreated;
    #endregion

    #region 构造函数
    public OrderService(IOrderRepository repository)
    {
        _repository = repository;
    }
    #endregion

    #region 私有函数
    private bool Validate(Order order)
    {
        return order != null && order.Items.Count > 0;
    }
    #endregion

    #region 公共函数
    /// <summary>
    /// 创建订单
    /// </summary>
    /// <param name="order">订单实例</param>
    /// <returns>创建后的订单编号</returns>
    public string Create(Order order)
    {
        if (!Validate(order)) throw new ArgumentException("订单无效");
        return _repository.Insert(order);
    }
    #endregion
}
```

规则：

- 每个 region 必须有配对的 `#endregion`，且 `#endregion` 后不跟多余文本。
- region 不可交叉、不可嵌套（除非是嵌套类内部再分 region）。
- 即使某个区域为空（如无公共变量），也保留该 region 并在内部写 `// 无`，或直接省略——但类内风格须统一，不要有的留有的删。
- 不要用 region 包裹零散的几行"临时逻辑"或"调试代码"；region 只按成员类型划分。
- `#region` 与首个成员之间、`#endregion` 与下个 `#region` 之间各空一行。

---

## 3. XML 注释规范

### 3.1 哪些需要注释

| 成员 | 是否需要 `///` 注释 |
|------|---------------------|
| public 方法 | **必须** |
| public 属性 | 必须（一句 summary 即可） |
| protected 方法 | 必须（视为对外接口） |
| public 类/接口/结构体 | 必须 |
| private 方法 | **不需要** |
| private 字段 | 不需要（名称自解释；特殊约束用行内 `//` 注释） |
| 公共字段（const） | 需要一句 summary |

### 3.2 公共方法注释格式

严格使用以下标签，顺序固定：`summary` → `param`（按参数顺序）→ `returns`（有返回值时）→ `exception`（仅当方法显式抛出且调用方需处理时）。

```csharp
/// <summary>
/// 创建订单
/// </summary>
/// <param name="order">订单实例，不可为 null</param>
/// <param name="priority">优先级，1-5</param>
/// <returns>新订单编号</returns>
public string Create(Order order, int priority)
```

**summary 要求**：

- 20 个汉字以内，用动词开头描述"做什么"，不描述"怎么做"。
- 不写过程、不写实现步骤、不写内部调用链。
  - 错误：`/// 先校验参数，然后调用 Repository.Insert 插入数据库，最后触发事件并返回编号`（这是过程描述）。
  - 正确：`/// 创建订单`。
- 不写版本历史、修改记录（如 `/// 2024-01-01 新增 by 张三`）。
- 不写废话：`/// 这是一个构造函数`、`/// Get 方法`。

**param 要求**：

- 每个参数都必须有对应 `<param name="...">`，`name` 与方法签名一致。
- 说明参数含义、取值范围或约束，不重复参数名本身。
  - 错误：`/// <param name="order">order</param>`（无信息）。
  - 错误：`/// <param name="priority">优先级参数</param>`（重复名称）。
  - 正确：`/// <param name="priority">优先级，1-5，默认 3</param>`。
- 参数是否可为 null、单位、枚举含义等关键约束写在 param 中。

**returns 要求**：

- 说明返回值含义，不写"返回结果"这种废话。
- 返回 bool 时说明 true/false 各自含义：`/// <returns>校验通过返回 true，否则 false</returns>`。

**exception 要求**：

- 仅列出调用方应当感知并处理的异常；参数校验抛出的 `ArgumentException` 等可列。
- 不要列出方法内部可能抛出但无法恢复的所有异常（如 `NullReferenceException`）。

### 3.3 公共属性注释格式

```csharp
/// <summary>
/// 服务名称
/// </summary>
public string ServiceName { get; }
```

一行 summary 即可，不需要 param/returns。

### 3.4 C# 7.3 注意事项

- 不使用 C# 8+ 的 `/// <param name="x">` 可空性标注（`string?`）。
- 不使用 `<inheritdoc/>` 偷懒——除非确实是重写且基类注释完整适用。
- XML 注释中的尖括号需转义：泛型用 `List&lt;Order&gt;`，代码引用用 `<see cref="..."/>`。

---

## 4. 常见问题

- **AI 给私有方法写的 `///` 不规范**：私有方法可以写 `///`，但必须符合 XML 注释规范（summary 20 字内 + param/returns 完整），缺参数或写成长段说明都是不合格的。
- **AI 给 region 起功能名而非类型名**：如 `#region 订单查询逻辑`、`#region 新增功能`——region 按成员类型划分，不按功能迭代划分。
- **AI 把字段和属性混排**：私有字段夹在方法中间，或属性散落在类各处。
- **AI 生成的 summary 超长**：把整个方法逻辑翻译成中文塞进 summary，应压缩到 20 字内。
- **AI 漏掉 param 或 returns**：有参数无 `<param>`、有返回值无 `<returns>`。
- **AI 在注释里写日期/作者**：版本信息归版本控制，不归注释。
