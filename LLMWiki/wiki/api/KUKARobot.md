# KUKARobot API 参考

> KUKA 机器人通讯模块 C# API 参考
>
> 命名空间：`AdaWeldSystem.Comm.KUKARobot`
> 对应目录：`Comm/KUKARobot/`

---

## 1. KUKARobotManager

统一管理层，对外提供 KUKA 机器人通讯的简化接口。

```csharp
public class KUKARobotManager : IDisposable
{
    // 属性
    public RSICommunication RSI { get; }
    public EKICommunication EKI { get; }
    public bool IsRSIConnected { get; }
    public bool IsEKIConnected { get; }
    
    // 构造函数
    public KUKARobotManager();
    
    // RSI 方法
    public bool InitializeRSI(string xmlConfigPath);
    public bool StartRSI();
    public bool StopRSI();
    
    // EKI 方法
    public bool InitializeEKI(string xmlConfigPath);
    public bool OpenEKI();
    public void CloseEKI();
    
    // 数据交换
    public KUKARobotData GetCurrentData();
    public void SendCorrectionData(KUKACorrectionData correction);
    
    // 事件
    public event EventHandler<KUKADataReceivedEventArgs> DataReceived;
    public event EventHandler<KUKAConnectionEventArgs> ConnectionStateChanged;
    
    // 释放
    public void Dispose();
}
```

---

## 2. RSICommunication

RSI (Robot Sensor Interface) UDP 实时通讯管理。

```csharp
public class RSICommunication : IDisposable
{
    // 属性
    public bool IsRunning { get; }
    public string RobotIP { get; set; }
    public int RobotPort { get; set; }
    public int LocalPort { get; set; }
    public ulong CurrentIPOC { get; private set; }
    
    // 构造函数
    public RSICommunication();
    public RSICommunication(string robotIP, int robotPort, int localPort);
    
    // 连接管理
    public bool Initialize(string xmlConfigPath);
    public bool Start();
    public bool Stop();
    
    // 数据发送（机器人状态 → 传感器）
    public void SendRobotData(KUKARobotData data);
    
    // 数据接收（传感器修正 → 机器人）
    public KUKACorrectionData ReceiveCorrectionData();
    public bool TryReceiveCorrectionData(out KUKACorrectionData correction, int timeoutMs);
    
    // XML 序列化
    public string SerializeRobotData(KUKARobotData data);
    public KUKACorrectionData DeserializeCorrectionData(string xml);
    
    // 事件
    public event EventHandler<RSIDataEventArgs> DataReceived;
    public event EventHandler<RSIErrorEventArgs> ErrorOccurred;
    
    // 释放
    public void Dispose();
}
```

### 2.1 RSIDataEventArgs

```csharp
public class RSIDataEventArgs : EventArgs
{
    public KUKARobotData RobotData { get; set; }
    public KUKACorrectionData CorrectionData { get; set; }
    public ulong IPOC { get; set; }
    public DateTime Timestamp { get; set; }
}
```

### 2.2 RSIErrorEventArgs

```csharp
public class RSIErrorEventArgs : EventArgs
{
    public string ErrorMessage { get; set; }
    public Exception Exception { get; set; }
    public RSIErrorType ErrorType { get; set; }
}
```

### 2.3 RSIErrorType

```csharp
public enum RSIErrorType
{
    ConnectionFailed,
    IPOMismatch,
    XMLSerializationError,
    XMLDeserializationError,
    NetworkTimeout,
    Unknown
}
```

---

## 3. EKICommunication

EKI (Ethernet KRL Interface) TCP 数据交换管理。

```csharp
public class EKICommunication : IDisposable
{
    // 属性
    public bool IsConnected { get; }
    public string ServerIP { get; set; }
    public int ServerPort { get; set; }
    public EKIMode Mode { get; set; }  // Client / Server
    public EKIEnvironment Environment { get; set; }
    
    // 构造函数
    public EKICommunication();
    public EKICommunication(string serverIP, int serverPort, EKIMode mode);
    
    // 连接管理
    public bool Initialize(string xmlConfigPath);
    public bool Open();
    public void Close();
    public void Clear();
    
    // 发送数据
    public bool Send(string elementPath);
    public bool SendRaw(byte[] data);
    public bool SendString(string xmlString);
    
    // 写入发送存储器
    public bool SetReal(string elementPath, double value);
    public bool SetInt(string elementPath, int value);
    public bool SetBool(string elementPath, bool value);
    public bool SetFrame(string elementPath, KUKAFrame frame);
    public bool SetString(string elementPath, string value);
    
    // 读取接收存储器
    public bool GetBool(string elementPath, out bool value);
    public bool GetInt(string elementPath, out int value);
    public bool GetReal(string elementPath, out double value);
    public bool GetString(string elementPath, out string value);
    public bool GetFrame(string elementPath, out KUKAFrame frame);
    
    // 事件
    public event EventHandler<EKIDataEventArgs> DataReceived;
    public event EventHandler<EKIConnectionEventArgs> ConnectionStateChanged;
    public event EventHandler<EKIErrorEventArgs> ErrorOccurred;
    
    // 释放
    public void Dispose();
}
```

### 3.1 EKIMode

```csharp
public enum EKIMode
{
    Client,   // EKI 作为客户端连接外部服务器
    Server    // EKI 作为服务器监听外部客户端
}
```

### 3.2 EKIEnvironment

```csharp
public enum EKIEnvironment
{
    Program,   // 程序复位/取消时删除连接
    Submit,    // 反选提交解释器时删除连接
    System     // 仅重新配置 IO 时删除连接
}
```

### 3.3 EKIStatus

```csharp
public struct EKIStatus
{
    public int Buff;      // 数据存储器中的数据组数量
    public int Read;      // 已从存储器读取的数据组数量
    public int MsgNo;     // 错误信息编号
    public bool Con;      // 连接状态
}
```

---

## 4. KUKAXMLConfig

XML 配置生成与解析。

```csharp
public static class KUKAXMLConfig
{
    // RSI XML 配置生成
    public static string GenerateRSIXML(RSIConfig config);
    public static RSIConfig ParseRSIXML(string xmlContent);
    
    // EKI XML 配置生成
    public static string GenerateEKIXML(EKIConfig config);
    public static EKIConfig ParseEKIXML(string xmlContent);
    
    // 配置文件保存/加载
    public static void SaveRSIConfig(string filePath, RSIConfig config);
    public static RSIConfig LoadRSIConfig(string filePath);
    public static void SaveEKIConfig(string filePath, EKIConfig config);
    public static EKIConfig LoadEKIConfig(string filePath);
}
```

### 4.1 RSIConfig

```csharp
public class RSIConfig
{
    public string IPNumber { get; set; }
    public int Port { get; set; }
    public string SenType { get; set; }
    public bool OnlySend { get; set; }
    public List<RSIElement> SendElements { get; set; }
    public List<RSIElement> ReceiveElements { get; set; }
}
```

### 4.2 RSIElement

```csharp
public class RSIElement
{
    public string Tag { get; set; }
    public RSIDataType Type { get; set; }
    public string Index { get; set; }    // "1"~"64" 或 "INTERNAL"
    public int HoldOn { get; set; }      // 0 或 1，仅 RECEIVE
}
```

### 4.3 RSIDataType

```csharp
public enum RSIDataType
{
    BOOL,
    DOUBLE,
    LONG,
    STRING
}
```

### 4.4 EKIConfig

```csharp
public class EKIConfig
{
    // EXTERNAL
    public string ExternalIP { get; set; }
    public int ExternalPort { get; set; }
    public EKIMode ExternalType { get; set; }
    
    // INTERNAL
    public EKIEnvironment Environment { get; set; }
    public string BufferingMode { get; set; }   // "FIFO" / "LIFO"
    public int BufferingLimit { get; set; }
    public int BuffSizeLimit { get; set; }
    public int TimeoutConnect { get; set; }
    public int AliveSetOut { get; set; }
    public int AliveSetFlag { get; set; }
    public int AlivePing { get; set; }
    
    // RECEIVE / SEND
    public List<EKIElement> ReceiveElements { get; set; }
    public List<EKIElement> SendElements { get; set; }
}
```

### 4.5 EKIElement

```csharp
public class EKIElement
{
    public string Tag { get; set; }
    public EKIDataType Type { get; set; }
    public string Mode { get; set; }      // "FIFO" / "LIFO"
    public int SetOut { get; set; }
    public int SetFlag { get; set; }
}
```

### 4.6 EKIDataType

```csharp
public enum EKIDataType
{
    STRING,
    REAL,
    INT,
    BOOL,
    FRAME,
    BYTE,
    STREAM
}
```

---

## 5. KUKADataTypes

数据结构定义。

### 5.1 KUKARobotData

机器人状态数据（RSI 发送方向）。

```csharp
public class KUKARobotData
{
    // 笛卡尔位置
    public KUKAPosition RIst { get; set; }     // 实际位置
    public KUKAPosition RSol { get; set; }     // 额定位置
    
    // 轴位置
    public double[] AIPos { get; set; }        // A1-A6 实际位置 [6]
    public double[] ASPos { get; set; }        // A1-A6 额定位置 [6]
    public double[] EIPos { get; set; }        // E1-E6 实际位置 [6]
    public double[] ESPos { get; set; }        // E1-E6 额定位置 [6]
    
    // 电机电流
    public double[] MACur { get; set; }        // A1-A6 电机电流 [6]
    public double[] MECur { get; set; }        // E1-E6 电机电流 [6]
    
    // 技术参数
    public double[] TechC { get; set; }        // 主进技术参数 C1-C6 [6]
    public double[] TechT { get; set; }        // 预进技术参数 T1-T6 [6]
    
    // 状态
    public long Delay { get; set; }            // 延迟数据包数量
    public string EStr { get; set; }           // 提示/故障信息
    public ulong IPOC { get; set; }            // 时间戳
}
```

### 5.2 KUKACorrectionData

传感器修正数据（RSI 接收方向）。

```csharp
public class KUKACorrectionData
{
    // 笛卡尔修正
    public KUKAPosition RKorr { get; set; }    // X, Y, Z, A, B, C
    
    // 轴修正
    public double[] AK { get; set; }           // A1-A6 [6]
    public double[] EK { get; set; }           // E1-E6 [6]
    
    // 数字输出
    public long DiO { get; set; }
    
    // 时间戳（必须与发送的 IPOC 一致）
    public ulong IPOC { get; set; }
}
```

### 5.3 KUKAPosition

笛卡尔位姿。

```csharp
public struct KUKAPosition
{
    public double X { get; set; }
    public double Y { get; set; }
    public double Z { get; set; }
    public double A { get; set; }    // 绕 Z 轴旋转
    public double B { get; set; }    // 绕 Y 轴旋转
    public double C { get; set; }    // 绕 X 轴旋转
    
    public KUKAPosition(double x, double y, double z, double a, double b, double c);
}
```

### 5.4 KUKAFrame

坐标系（EKI FRAME 类型）。

```csharp
public struct KUKAFrame
{
    public double X { get; set; }
    public double Y { get; set; }
    public double Z { get; set; }
    public double A { get; set; }
    public double B { get; set; }
    public double C { get; set; }
    
    public KUKAFrame(double x, double y, double z, double a, double b, double c);
}
```

---

## 6. 使用示例

### 6.1 RSI 实时修正通讯

```csharp
// 创建 RSI 通讯实例
var rsi = new RSICommunication("192.168.1.10", 49152, 49153);

// 初始化并启动
rsi.Initialize(@"C:\KRC\ROBOTER\Config\User\Common\SensorInterface\RSI_Ethernet.xml");
rsi.Start();

// 订阅数据接收事件
rsi.DataReceived += (s, e) =>
{
    // 处理传感器返回的修正数据
    var correction = e.CorrectionData;
    Console.WriteLine($"修正: X={correction.RKorr.X}, Y={correction.RKorr.Y}");
};

// 发送机器人状态（通常在循环中）
var robotData = new KUKARobotData
{
    RIst = new KUKAPosition(1000, 200, 300, 0, 90, 0),
    IPOC = rsi.CurrentIPOC
};
rsi.SendRobotData(robotData);

// 停止
rsi.Stop();
rsi.Dispose();
```

### 6.2 EKI 数据交换

```csharp
// 创建 EKI 通讯实例（客户端模式）
var eki = new EKICommunication("192.168.1.10", 54600, EKIMode.Client);

// 初始化并打开连接
eki.Initialize(@"C:\KRC\ROBOTER\Config\User\Common\EthernetKRL\MyConnection.xml");
eki.Open();

// 写入并发送数据
eki.SetReal("Robot/Pos/X", 1000.0);
eki.SetReal("Robot/Pos/Y", 500.0);
eki.SetInt("Robot/Status", 1);
eki.Send("Robot");

// 读取传感器数据
if (eki.GetReal("Sensor/Pos/X", out double sensorX))
{
    Console.WriteLine($"传感器 X: {sensorX}");
}

// 关闭连接
eki.Close();
eki.Clear();
eki.Dispose();
```

### 6.3 统一管理层使用

```csharp
// 使用 KUKARobotManager 统一管理
using (var manager = new KUKARobotManager())
{
    // 初始化 RSI
    manager.InitializeRSI(@"Config\RSI_Ethernet.xml");
    manager.StartRSI();
    
    // 初始化 EKI
    manager.InitializeEKI(@"Config\EKI_Connection.xml");
    manager.OpenEKI();
    
    // 订阅事件
    manager.DataReceived += (s, e) =>
    {
        Console.WriteLine($"收到数据: {e.RobotData}");
    };
    
    // 发送修正
    manager.SendCorrectionData(new KUKACorrectionData
    {
        RKorr = new KUKAPosition(0.5, 0.2, 0, 0, 0, 0)
    });
}
```

---

## 7. 参考链接

- [[modules/KUKARobot]] —— 模块详解
- [[modules/Comm]] —— 通讯总线模块
- [[api/GlobalCommData]] —— 全局数据通讯中心

---

> 本 API 参考基于 KUKA.RobotSensorInterface 3.3 和 KUKA.Ethernet KRL 2.2 文档编制。
> Ingest 时间：2026-07-01
