# 代码逻辑精简规则

> **归属（2026-09-01）**：本页是 [[standards/CodeSimplification]] 的配套深度反例/工作流，原位于 `wiki/standards/references/`，已扁平化为 `standards/` 下的独立文件。**standards/ 全库禁止子目录**——所有页面一律平铺为文件，靠命名前缀 `CodeSimplification-` 成组。

适用 .NET Framework 4.8 / C# 7.3。每条规则给出判定标准、AI 高频反例与修正方向。

## 目录

1. [优先使用类私有变量，控制临时变量](#1-优先使用类私有变量控制临时变量)
2. [禁止无意义的 NULL 判断](#2-禁止无意义的-null-判断)
3. [禁止无意义的安全锁逻辑](#3-禁止无意义的安全锁逻辑)
4. [禁止无意义的函数值赋值传递](#4-禁止无意义的函数值赋值传递)
5. [禁止过度使用枚举类型](#5-禁止过度使用枚举类型)
6. [禁止过度设定属性](#6-禁止过度设定属性)
7. [禁止过度等待、延迟](#7-禁止过度等待延迟)
8. [禁止过度缓存数据](#8-禁止过度缓存数据)
9. [禁止过度资源管理](#9-禁止过度资源管理)

---

## 1. 优先使用类私有变量，控制临时变量

**判定标准**：跨方法共享、表示对象状态的值应作为类私有字段；仅在单个方法内做链式中转、且名称不增加语义的临时变量应消除。临时变量在以下情况允许存在：需要多次复用、需要捕获中间结果做分支判断、名称能解释含义（如 `var isValid = ...`）。

**AI 高频反例**：

- 把本应是类状态的值在每个方法里重复声明临时变量，导致同一概念在多处各存一份。
- 链式调用中插入 `var temp1 = ...; var temp2 = temp1;` 之类纯中转变量。
- 临时变量命名为 `temp`、`tmp`、`data`、`result`、`value`，且只使用一次。
- 方法开头把私有字段逐一赋值给同名局部变量再使用（`var config = _config;` 后全程用 config，但 _config 不会被重新赋值）。
- 循环外声明的临时变量在循环内只做累加，本可直接用字段或 LINQ 表达。

**修正方向**：跨方法状态提升为 `private` 字段并加 `_camelCase` 前缀；单方法内一次性中转变量直接内联；确需保留的临时变量起能表达业务含义的名字。

---

## 2. 禁止无意义的 NULL 判断

**判定标准**：null 检查只在以下场景有意义：参数来自外部输入（公共 API 边界、反序列化、UI 事件、第三方回调）；值确实可能为 null 且后续逻辑依赖此判断；框架/契约要求。对生命周期内不可能为 null 的对象做检查即为冗余。

**AI 高频反例**：

- **防御式编程泛滥**：对每个私有方法的每个参数都加 `if (x == null) throw new ArgumentNullException(nameof(x))`，但调用链上游已保证非空，私有方法不是公开边界。
- **对刚创建的对象检查 null**：
  ```csharp
  var list = new List<int>();
  if (list != null) { list.Add(1); }  // new 永远不会返回 null
  ```
- **对值类型检查 null**：`if (id != null)` 其中 id 是 `int`/`bool`/`DateTime`/`enum`（值类型永不为 null，C# 7.3 下编译都可能警告）。
- **对 `this` 检查 null**：`if (this == null) return;`（实例方法内 this 不可能为 null）。
- **重复检查**：方法 A 入口检查了参数 null，A 调用的私有方法 B 又对同一参数检查一遍。
- **空检查后什么都不做**：`if (obj == null) { }` 或 `if (obj != null) { }` 块内无实质逻辑。
- **out 参数赋值前检查 null**：out 参数在方法返回前必须赋值，调用方传入的变量不需要在方法内检查。
- **对 `as` 表达式立即检查但不使用检查结果**：`var x = obj as Foo; if (x != null) { /* 不用 x，重新 cast 一次 */ }`。
- **对已知字符串常量/资源检查 null**：如 `Properties.Resources.Msg` 这类资源在程序集加载后非空。
- **`?.` 滥用**：对生命周期内确定非空的对象链使用 `?.`，掩盖真实的空引用风险，让真正需要检查的地方不突出。

**修正方向**：公共方法入口对外部参数保留一次 null 校验；私有方法信任调用链；删除对 new 结果、值类型、this 的检查；null 检查必须伴随有意义的分支（抛异常、返回默认、记录日志后降级）。

---

## 3. 禁止无意义的安全锁逻辑

**判定标准**：锁只在以下场景需要：多线程访问共享可变状态；存在明确的竞态条件；锁对象是私有只读引用类型。单线程上下文（如 WinForms/WPF UI 线程、ASP.NET 经典管道请求上下文）、不可变数据、局部变量不需要锁。

**AI 高频反例**：

- **对局部变量加锁**：`lock (new object())` 每次 lock 的都是不同对象，完全无效；或对方法内 `var list = new List<T>()` 加锁，该变量不被其他线程可见。
- **对不会多线程访问的代码加锁**：WinForm 事件处理程序里加 lock，但该控件只在 UI 线程被访问。
- **`lock(this)` / `lock(typeof(T))` / `lock("字符串")`**：外部对象可被其他代码锁定，导致死锁；字符串因驻留可能被跨上下文共享。
- **为每个方法无脑加锁**：类的所有方法都 `lock (_lock)`，但类根本不跨线程使用，或方法只操作局部变量。
- **锁内执行耗时操作**：在 lock 块内做文件 IO、网络请求、数据库查询、`MessageBox.Show`，严重拖垮并发甚至死锁。
- **嵌套锁无顺序约定**：`lock (a) { lock (b) { ... } }` 与另一处 `lock (b) { lock (a) { ... } }` 形成经典死锁。
- **不必要的双重检查锁定**：对每次调用都会初始化、或初始化代价极低的对象做 double-check locking。
- **锁只读操作**：对只读取不可变数据或只读取值类型副本的方法加锁。
- **用锁保护本可用并发集合的场景**：`lock (_lock) { _list.Add(x); }` 但 .NET 4.8 已有 `ConcurrentBag<T>`/`ConcurrentQueue<T>` 更合适。
- **锁对象不是 readonly**：`private object _lock = new object();` 缺少 `readonly`，方法内可能被重新赋值导致锁失效。

**修正方向**：确认多线程访问证据后再加锁；锁对象用 `private static readonly object` 或 `private readonly object`；锁内只做内存操作；能靠 `Concurrent*` 集合或不可变设计解决的不用显式锁；UI 线程代码不加锁。

---

## 4. 禁止无意义的函数值赋值传递

**判定标准**：函数返回值、参数、属性之间的赋值如果没有产生任何转换、校验、副作用或语义命名，即为冗余传递。

**AI 高频反例**：

- **返回值中转后立即返回**：
  ```csharp
  private int Calc() {
      var result = ComputeValue();
      return result;  // 应直接 return ComputeValue();
  }
  ```
- **参数原样赋给局部变量**：`void M(Foo config) { var cfg = config; cfg.Run(); }`，cfg 与 config 完全等价且无转换。
- **多层透传包装**：`A()` 只调 `B()`，`B()` 只调 `C()`，每层只加一行无意义日志或直接透传，真正逻辑在 `C()`。AI 迭代时常这样叠床架屋。
- **属性→局部变量→属性回写**：`var x = this.Name; this.Name = x;` 或 `this.Count = this.Count;`。
- **out 参数先赋默认值再赋实际值**：`result = 0; ... result = actual;`，中间的默认值从不被读取。
- **ref 参数无修改地传入传出**：方法声明 ref 但内部既不读也不写该参数。
- **构造函数参数赋值给字段后，构造函数内又用局部变量而非字段**：`this._x = x; var tmp = x;` 后续用 tmp。
- **把方法返回值赋给字段，字段只在下一行被读取一次后再无使用**：本可直接用返回值。
- **委托/事件包装层无附加逻辑**：`public event EventHandler Click; protected virtual void OnClick() { Click?.Invoke(this, EventArgs.Empty); }` 这类标准模式除外；但 `private void Handler(object s, EventArgs e) { OnClick(s, e); }` 纯转发无意义。

**修正方向**：直接 return 表达式；消除只赋值一次且无转换的中转变量；合并纯透传的方法链；ref/out 参数只在确实需要时使用。

---

## 5. 禁止过度使用枚举类型

**判定标准**：枚举适用于表示一组固定、有限、在多处被分支判断或 switch 的命名常量。只有两个状态、只在一处使用、需要频繁与字符串互转、或值会动态扩展的场景不适合枚举。

**AI 高频反例**：

- **二值状态用枚举**：`enum Status { Enabled, Disabled }` 实际就是 bool 语义，用 `bool enabled` 更直接。
- **枚举只定义不消费**：定义了 `enum ResultCode { ... }`，但全代码中没有任何 switch/if 基于它做分支，只是在方法间原样传递。
- **一次性枚举**：为某个方法内部的临时步骤定义枚举（如 `enum Step { Init, Load, Process, Save }`），方法外用不到，用局部常量或整数即可。
- **枚举与字符串/int 频繁互转**：`Enum.Parse`、`ToString()`、`(int)code` 在代码中反复出现，说明枚举并未真正提供类型安全价值。
- **枚举值带 `Enum` 后缀**：`enum OrderStatusEnum`（C# 惯例不加 Enum 后缀）。
- **Flags 特性滥用**：加了 `[Flags]` 但枚举值从不会按位组合；或反之，需要组合却没加 Flags 且值不是 2 的幂。
- **枚举值数量爆炸**：把所有可能的状态码（包括第三方系统返回码）都纳入枚举，实际只处理其中两三个。
- **用枚举代替异常/多态**：`enum ErrorType { Null, Empty, TooLong, Format }` 然后在方法里返回该枚举让调用方 switch，本可用异常或不同的校验策略。
- **枚举值命名冗余**：`enum Color { ColorRed, ColorGreen }`（前缀重复类型名）。

**修正方向**：二值用 bool；只在一处用的常量用 `private const`；需要扩展的用字符串/字典；真正需要类型安全且多处分支判断的才用枚举；命名不带 Enum 后缀。

---

## 6. 禁止过度设定属性

**判定标准**：公共属性用于表达对象的公开状态契约。仅在构造函数赋值、外部从不读取/设置、或只在类内部使用的值应作为私有字段。自动属性不是"免费"的——它会生成隐藏字段，过度使用会膨胀类的状态面。

**AI 高频反例**：

- **为每个私有字段配公共属性，但类外从不访问**：AI 习惯性给所有字段加 `{ get; set; }`，破坏封装。
- **私有字段配公共属性，类内部却绕过属性直接用字段**：属性存在的意义（如校验、通知）被架空。
- **只读语义用了全公共 set**：属性只应在构造函数或初始化时赋值，却声明了 public set，外部可随意篡改。
- **属性内含重逻辑**：get 访问器里做数据库查询、文件读取、复杂计算，调用方以为是简单取值，实际有严重副作用和性能陷阱。
- **属性每次访问返回新集合/新对象**：
  ```csharp
  public List<Item> Items { get { return new List<Item>(_items); } }
  ```
  调用方 `foreach` 一次就创建一次副本，且 `obj.Items.Add(...)` 不会影响内部状态，容易误用。
- **对不参与数据绑定的类实现 `INotifyPropertyChanged`**：POCO/业务对象加了 PropertyChanged 事件但从未被订阅。
- **自动属性 + private set + 仅构造函数赋值**：本可用 `{ get; }` 只读属性（C# 7.3 支持）或 readonly 字段。
- **属性作为临时数据传递通道**：方法 A 设置属性，方法 B 立即读取，本应作为方法参数传递，却变成了隐式的对象状态。
- **虚属性/抽象属性过度**：基类定义了一堆属性，只有一个派生类用到。
- **属性返回内部集合的可变引用**：`public List<T> Data => _data;` 外部可修改内部集合，却没有文档说明；要么返回 `ReadOnlyCollection<T>`，要么用方法。

**修正方向**：只暴露真正需要公开的状态；构造后不变的用只读属性或 readonly 字段；类内部共享用私有字段；重逻辑改为方法；集合属性考虑返回只读包装或提供 Add/Remove 方法。

---

## 7. 禁止过度等待、延迟

**判定标准**：`Thread.Sleep`、`Task.Delay`、`.Wait()`、`.Result`、轮询等待只在明确的节流/退避场景下使用。等待异步操作完成应使用 `await`；等待条件成立应使用事件、信号量、回调或 `TaskCompletionSource`。

**AI 高频反例**：

- **用 `Thread.Sleep` 等待异步操作**：
  ```csharp
  StartAsyncOperation();
  Thread.Sleep(3000);  // 猜测 3 秒能完成，不可靠且阻塞线程
  CheckResult();
  ```
- **固定延时轮询代替事件**：`while (!done) { Thread.Sleep(500); Check(); }`，应使用 `ManualResetEventSlim`、`Monitor.Wait/Pulse` 或异步 `TaskCompletionSource`。
- **UI 线程上 Sleep/Wait**：WinForms/WPF 事件处理中 `Thread.Sleep` 或 `.Result`，直接冻结界面，.NET 4.8 下还可能死锁（SynchronizationContext）。
- **`Task.Run(...).Wait()` / `.Result` 套娃**：在异步方法上用 `.Result` 阻塞，若该 Task 需要回到被阻塞的上下文则死锁。
- **不必要的 `Task.Delay`**：`await Task.Delay(100)` 后执行本可同步完成的代码，纯属拖慢响应。
- **`ConfigureAwait(false)` 滥用**：在不需要恢复上下文的类库中是正确的，但 AI 常在 UI 层代码里也加，导致后续代码不在 UI 线程而抛跨线程异常。
- **无限等待无超时**：`_event.WaitOne()` 无超时参数，若信号永不触发则永久挂起。
- **锁/Sleep 组合当节流**：`lock` 里 `Sleep` 模拟"处理时间"，测试代码残留到生产。
- **`Task.Yield()` 不必要使用**：在非热路径强行让出控制权，增加调度开销。
- **异步方法里混合同步等待**：方法声明 `async`，内部却用 `.Wait()` 等待另一个 Task，既阻塞又可能死锁。
- **超时值魔法数字**：`WaitOne(5000)` 等硬编码超时无注释说明来源。

**修正方向**：异步操作用 `await`；条件等待用事件/信号量/回调；UI 代码绝不 Sleep/Wait；需要超时时用 `WaitOne(timeout)` 并处理超时分支；节流/退避场景保留 Delay 但注释说明原因。

---

## 8. 禁止过度缓存数据

**判定标准**：缓存适用于获取成本高、变化频率低、读取频率高的数据。缓存必须有明确的生命周期、失效策略和读取方。只写不读、一次性使用、多层重复缓存、无失效机制的缓存都是冗余。

**AI 高频反例**：

- **只写不读的缓存**：`_cache[key] = value;` 之后全代码中再无 `_cache[key]` 的读取，缓存字段纯浪费内存。
- **一次性数据缓存**：数据在一次操作中计算并缓存，但该操作只执行一次（如窗体加载、单次导入），缓存永不再被命中。
- **多层重复缓存**：同一数据同时存在静态字段、实例字段、`MemoryCache` 三处，值可能不一致。
- **缓存无过期/清理**：`private static readonly Dictionary<string, Data> _cache` 只增不删，长期运行内存泄漏；.NET 4.8 下应使用 `MemoryCache` 带策略或自己实现淘汰。
- **用缓存代替参数传递**：方法 A 把值存入 `_currentXxx` 字段，方法 B 读取该字段——这是隐式参数耦合，不是缓存；方法间传值应用参数。
- **缓存键过度设计**：数据只有两三条，却拼接复杂字符串键、做键规范化。
- **缓存大对象但只用一小部分**：缓存整个 DataTable/List，但调用方只取其中一行/一个字段。
- **缓存了频繁变化的数据**：每次读取都重新刷新缓存（`_cache = Load()`），缓存退化为冗余赋值。
- **缓存可变对象的引用**：缓存了 `List<T>` 并返回给调用方，调用方修改了集合，缓存被意外污染。
- **双重检查锁定缓存但初始化极廉价**：为获取一个常量或简单计算结果做 double-check locking 缓存。
- **静态缓存持有上下文相关对象**：静态缓存持有 HttpContext、窗体控件、数据库连接等短生命周期对象，导致内存泄漏和状态串用。

**修正方向**：确认有读取方和命中率才缓存；用 `MemoryCache` 带绝对/滑动过期；缓存不可变数据或返回副本；一次性数据用局部变量；方法间传值用参数而非字段。

---

## 9. 禁止过度资源管理

**判定标准**：`using`/`Dispose` 只用于封装非托管资源或持有非托管资源的托管对象（文件流、数据库连接、网络流、GDI 对象、WaitHandle 等）。纯托管对象、内存对象、不实现 IDisposable 的对象不需要 Dispose。.NET 4.8 下 C# 7.3 没有 `using` 声明，需用 `using (...)` 块。

**AI 高频反例**：

- **对不实现 IDisposable 的对象套 using**：`using (var list = new List<int>())` 编译错误；或对 DataTable/DataSet（不实现 IDisposable 的有效释放）做 using。
- **手写完整 Dispose 模式但无非托管资源**：类里只有托管字段，却写了 `~Finalizer`、`Dispose(bool disposing)`、`GC.SuppressFinalize` 全套。仅当类直接持有非托管资源（IntPtr、句柄）时才需要终结器。
- **手动调用 `GC.Collect()`**：AI 有时在"释放资源"后加 `GC.Collect(); GC.WaitForPendingFinalizers();`，干扰 GC 策略且性能极差。
- **对托管对象写析构函数**：`~MyClass() { }` 中清理托管对象，终结器执行顺序不保证，且会延长对象生命周期。
- **using 嵌套过深**：
  ```csharp
  using (var conn = new SqlConnection(...))
  using (var cmd = new SqlCommand(...))
  using (var reader = cmd.ExecuteReader())
  using (var ms = new MemoryStream())
  { ... }
  ```
  超过 3 层应考虑工厂方法或 DataAdapter 等高层封装。
- **对 MemoryStream 过度 Dispose**：MemoryStream 不持有非托管资源，Dispose 后仍可读取（在 .NET 中），但 AI 常为它写复杂的 try/finally。
- **finally 中重复 Dispose**：`using` 已保证 Dispose，又在 finally 里手动 `Dispose`；或 `if (obj != null) obj.Dispose()` 与 using 重复。
- **为 IDisposable 创建纯透传包装**：包装类只实现 IDisposable 并把调用转发给内部对象，没有附加生命周期管理逻辑。
- **类级别持有短生命周期 IDisposable**：窗体/服务类持有 `SqlConnection`、`FileStream` 作为字段并在多次方法调用间保持打开，连接池被浪费、文件被长期锁定。应按需创建、using 释放。
- **Dispose 后未标记对象不可用**：多次 Dispose 抛异常或访问已释放资源；标准 Dispose 应允许多次调用且对已释放对象的访问抛 `ObjectDisposedException`。
- **GDI 对象泄漏**：`Pen`、`Brush`、`Font`、`Graphics`、`Icon`、`Image` 等 GDI+ 对象实现了 IDisposable，AI 常在 Paint 事件中 `new Pen(...)` 后不 Dispose，GDI 句柄泄漏。
- **事件订阅不取消**：对象订阅了长生命周期对象的事件（如静态事件、父窗体事件），自身 Dispose 时不取消订阅，导致无法 GC（这不是 Dispose 本身，但属于资源管理过度/不足）。

**修正方向**：只对真正的 IDisposable 用 using；短生命周期资源按需创建、using 释放；无非托管资源不写终结器；绝不手动 GC.Collect；GDI 对象用 using；Dispose 时取消事件订阅。
