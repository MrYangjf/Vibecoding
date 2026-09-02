# 函数精简规则

> **归属（2026-09-01）**：本页是 [[standards/CodeSimplification]] 的配套深度反例/工作流，原位于 `wiki/standards/references/`，已扁平化为 `standards/` 下的独立文件。**standards/ 全库禁止子目录**——所有页面一律平铺为文件，靠命名前缀 `CodeSimplification-` 成组。

适用 .NET Framework 4.8 / C# 7.3。目标是消除 AI vibecoding 在迭代过程中产生的冗余函数：功能重叠的函数应合并，无意义的单层嵌套函数应内联。

## 目录

1. [功能重叠的函数合并](#1-功能重叠的函数合并)
2. [嵌套内容函数合并（内联）](#2-嵌套内容函数合并内联)
3. [判定流程](#3-判定流程)
4. [不应合并的例外](#4-不应合并的例外)

---

## 1. 功能重叠的函数合并

### 1.1 问题本质

AI 面对客户改造要求时，倾向于**新增一个函数**来实现新逻辑，而不是修改已有函数。原因是新增比修改"安全"——不会破坏旧逻辑。但结果是同一职责出现多个函数，调用方困惑，维护时需要同步修改多处。

### 1.2 判定标准

满足以下任一条件即视为功能重叠，应合并：

| 信号 | 说明 |
|------|------|
| 同动词 + 同宾语 | `GetOrder` / `GetOrderEx` / `GetOrderV2` / `GetOrderWithDetail` 处理同一实体 |
| 一个函数是另一个的超集 | `A()` 做步骤 1-2，`B()` 做步骤 1-3，B 只是多一步 |
| 两个函数被同一调用方先后调用 | `var x = Load(); var y = Parse(x);` 且 Parse 只被此处调用 |
| 函数体 70% 以上相同 | 复制粘贴后改了两三行 |
| 仅参数默认值不同 | `M(a)` 和 `M(a, b: true)` 可合并为带默认参数的一个方法（C# 7.3 支持可选参数） |
| 一个函数只调用另一个并加空判断/日志 | `M2()` = `if (x != null) M1(x);` |

### 1.3 AI 高频反例

**反例 A：版本后缀函数堆叠**

```csharp
// 原始函数
public void ProcessOrder(Order order) {
    Validate(order);
    Save(order);
}

// 客户要求加通知，AI 新增：
public void ProcessOrderWithNotification(Order order) {
    Validate(order);
    Save(order);
    Notify(order);  // 只多了这一步
}

// 客户又要求加日志，AI 又新增：
public void ProcessOrderWithNotificationAndLog(Order order) {
    Validate(order);
    Save(order);
    Notify(order);
    Log(order);
}
```

问题：三个函数 90% 重复，调用方不知该用哪个；修改 Validate 逻辑要改三处。

修正：合并为一个函数，通知和日志通过可选参数或内部步骤控制：

```csharp
public void ProcessOrder(Order order, bool notify = true, bool log = true) {
    Validate(order);
    Save(order);
    if (notify) Notify(order);
    if (log) Log(order);
}
```

如果分支逻辑复杂，考虑策略模式而非函数堆叠，但在单文件、不改变对外接口的约束下，可选参数或内部条件分支是首选。

**反例 B：查询函数按字段数量分裂**

```csharp
public Order GetOrder(int id) { ... }
public Order GetOrderWithItems(int id) { ... }
public Order GetOrderWithItemsAndCustomer(int id) { ... }
```

问题：同一查询三种"加载深度"，调用方按需要挑，维护三套 SQL/映射。

修正：保留一个 `GetOrder(int id)`，按需加载通过参数或在一个函数内统一加载关联数据；若延迟加载代价高，用 `GetOrderSummary` / `GetOrderDetail` 两个语义清晰的函数，而不是按 With 后缀堆叠。

**反例 C：新旧函数并存，旧函数无人调用**

AI 重写某功能后把旧函数改名为 `xxxOld`、`xxxLegacy`、`xxxBackup` 留在文件中。应确认无调用后直接删除（在单文件审查范围内，检查文件内是否有调用；外部引用按约束不延伸，但应在报告中提示用户确认）。

**反例 D：同步/异步包装对**

```csharp
public void Save() { ... }
public Task SaveAsync() { return Task.Run(() => Save()); }
```

问题：`SaveAsync` 只是把同步方法丢到线程池，不是真正的异步 IO，属于伪异步。.NET 4.8 下若没有真正的异步 API，不要包装；若有，应直接实现异步逻辑而非包装同步方法。

### 1.4 合并时的约束

- **不修改对外函数签名**：如果被合并的函数是 public 且外部可能调用，保留其签名作为薄包装（调用合并后的主函数），或在报告中标注"建议确认外部调用后删除"。优先在私有函数范围内合并。
- **不修改对外变量名称**：合并过程中不重命名公共属性/字段。
- 合并后公共函数的 XML 注释更新为新行为的 summary（20 字内）。

---

## 2. 嵌套内容函数合并（内联）

### 2.1 问题本质

AI 在迭代功能时，会为"新增的一步"单独开辟一个函数，即使这一步只有一两行、只被一个地方调用。结果是原函数内出现"函数套函数"的调用链：`A()` 调 `B()`，`B()` 调 `C()`，每层只有一行，阅读时需要反复跳转。

### 2.2 判定标准

同时满足以下条件的私有函数应内联到调用方：

- 只被**一个**方法调用（在本文件内）；
- 函数体不超过 **3 行**有效代码（不含大括号和注释）；
- 不含复杂分支、循环、递归；
- 函数名只是在描述"做某动作"而非表达独立业务概念；
- 内联后不会让调用方函数过长（调用方本身不超过约 40 行）。

### 2.3 AI 高频反例

**反例 A：为新增一步单独建函数**

```csharp
// 原始函数
public void SubmitOrder(Order order) {
    Validate(order);
    Repository.Save(order);
}

// 客户要求提交后刷新缓存，AI 新增：
public void SubmitOrder(Order order) {
    Validate(order);
    Repository.Save(order);
    RefreshCacheAfterSubmit(order);  // 新开辟函数
}

private void RefreshCacheAfterSubmit(Order order) {
    _cache.Remove(order.Id);  // 只有一行
}
```

问题：`RefreshCacheAfterSubmit` 只被调用一次、只有一行，内联后更直接：

```csharp
public void SubmitOrder(Order order) {
    Validate(order);
    Repository.Save(order);
    _cache.Remove(order.Id);
}
```

**反例 B：链式单层包装**

```csharp
private void LoadAll() {
    LoadConfig();
}
private void LoadConfig() {
    Config = ParseConfig(File.ReadAllText(_path));
}
```

`LoadAll` 只调 `LoadConfig`，`LoadConfig` 只被 `LoadAll` 调。两层都只有一行有效逻辑，应合并为一个方法。

**反例 C：条件分支抽成函数但只服务于一处**

```csharp
public void Process(string input) {
    if (IsValidInput(input)) {
        DoWork(input);
    }
}
private bool IsValidInput(string input) {
    return !string.IsNullOrEmpty(input);
}
```

`IsValidInput` 只被用一次且只有一行，直接内联为 `if (!string.IsNullOrEmpty(input))`。如果该校验在多处使用则保留。

**反例 D：事件处理器套一层**

```csharp
private void SaveButton_Click(object sender, EventArgs e) {
    HandleSaveButtonClick();
}
private void HandleSaveButtonClick() {
    SaveData();
}
```

事件处理器直接调一个只被它调用的私有方法，而该方法又只调另一个方法。应把逻辑直接写在 `SaveButton_Click` 中（或让事件处理器直接调 `SaveData`，去掉中间层）。

**反例 E：为 using/try-catch 包裹而建函数**

```csharp
private void ExecuteWithLog(Action action) {
    try { action(); }
    catch (Exception ex) { _logger.Error(ex); throw; }
}
```

这类横切包装如果只被调用一两次，属于过度抽象；被多处复用才有价值。

### 2.4 内联时的约束

- 只内联**私有函数**；公共/保护函数不内联（对外接口）。
- 内联后检查变量名冲突、`return`/`out`/`ref` 语义是否变化。
- 如果内联会导致调用方函数超过约 40 行或嵌套超过 4 层，说明调用方本身职责过多，应在报告中指出，而不是强行内联。
- 递归函数、虚方法、被反射调用的方法不内联。

---

## 3. 判定流程

对文件内所有函数执行以下检查：

```
1. 列出文件内所有方法（名称、访问修饰符、行号范围、参数签名、被调用次数）
2. 功能重叠检查：
   - 按方法名归一化（去 V2/Ex/New/With 后缀）找同簇
   - 比较同簇方法的方法体相似度（token 集合 Jaccard 或行级 diff）
   - 相似度 > 70% 或存在超集关系 → 标记为"建议合并"
3. 嵌套内联检查：
   - 统计每个 private 方法在本文件内的被调用次数
   - 被调用 1 次 + 方法体 ≤ 3 行 + 无复杂控制流 → 标记为"建议内联"
4. 死函数检查：
   - private 方法在本文件内零调用 → 标记为"疑似死代码（确认外部反射/委托引用后删除）"
5. 输出报告：每个问题给出 位置、类型、涉及函数、合并/内联建议
```

脚本 `scripts/csharp_review.py` 可自动完成第 1、2 步的机械扫描和第 3 步的初步筛选；最终是否合并由审查者结合业务语义判定。

---

## 4. 不应合并的例外

以下情况保留独立函数，即使满足上述信号：

- **递归函数**：合并会破坏递归结构。
- **被外部引用的 public 函数**：受"不修改对外函数接口"约束，保留签名。
- **被委托/事件/反射引用的函数**：即使本文件内只出现一次，可能被动态绑定。
- **override/interface 实现**：签名由基类/接口决定。
- **P/Invoke 或 extern 方法**：声明即接口。
- **函数虽短但表达独立业务概念且被多处复用**：如 `IsValidInput` 被 3 处以上调用，保留。
- **方法体短但有明确的单一职责且未来可能扩展**：如 `OnPropertyChanged` 这类标准模式方法。
- **为单元测试可测性而分离的纯函数**：但在不引入测试项目的单文件审查中，仅在函数名和注释明确表明测试用途时保留。
