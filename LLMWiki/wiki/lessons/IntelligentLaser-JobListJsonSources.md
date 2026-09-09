# 英莱 Job 列表与接头类型数据源：运行目录 JSON（2026-08-24）

## 背景

曾误判「SDK 未提供 JOB 列表枚举 API，只能显示当前 JOB」。英莱技术人员确认：**连接相机后，原生 SDK 会在运行目录自动落盘两个 JSON**，分别提供「全部 Job 号」与「接头类型语义」，补齐了 Job 列表与参数对应显示两个缺口。

## 数据源（运行目录 = `AppDomain.CurrentDomain.BaseDirectory`）

### IntelligentLaser_jobdesclist.json —— 全部 Job
```json
[{"jobdescribe":"","jointtype":32,"id":1},{"jobdescribe":"","jointtype":33,"id":2}, ...]
```
- `id`：Job 号；`jointtype`：接头类型编号（对应 jointtypelist 的 `int`）；`jobdescribe`：Job 描述。
- 用途：`FetchJobList()` 解析 → `cmbJob` 下拉全量填充（需求①「读取所有 job 号」落地）。

### IntelligentLaser_jointtypelist.json —— 接头类型语义字典
```json
{"joint_types":[{"hex":"0x10","int":16,"name_zh":"左搭接","name_en":"Left-Lap",
  "lines":[{"line":[1,2],"name_zh":"左直线","name_en":"Left Line","order":1}, ...],
  "calculations":[{"type":"single_line_multi_value","line":[1,2]}, ...],
  "display":{"params_inspect_bp":0,"params_inspect_min_angle":90, ...},
  "green":["params_inspect_min_angle","params_inspect_max_angle"],
  "blue":["params_inspect_min_area","params_inspect_max_area"],
  "orange":["params_inspect_min_height1","params_inspect_max_height1"]}, ...]}
```
- 覆盖 20+ 接头类型：16 左搭接 / 17 右搭接 / 32 对接 / 33 微对接 / 34 双卷边对接 / 48 厚板外角焊缝 / 49 V坡口 / 50-53 左右侧(半)V坡口 / 64 内角焊缝 / 65 外角焊缝 / 66-67 方管左右搭接 / 80 平板 / 96-97 直线圆管 / 112 圆对接 / 128 圆检测。
- `display`：**该接头类型应显示的参数 key → 默认值**（后续 UI 拆分「相机参数 vs Job 算法参数」可据此过滤）。
- `green`/`blue`/`orange`：参数类别分组（如 32 对接：blue=面积、orange=角度/高度/宽度），可作表格着色依据。

## 教训

1. **官方 demo 与 SDK C# 包装都不读这两个 JSON**（原生层生成）——解析必须自行实现。本项目用 Newtonsoft.Json（csproj 已引用 `3rdDepend\Newtonsoft.Json.dll`），`IlJobDescInfo`/`IlJointTypeInfo` 字段按 JSON 小写键命名，Newtonsoft 大小写不敏感自动匹配。
2. **文件位置是运行目录（BaseDirectory），不是 Config 子目录**——与已删除的 `.ilini` 离线缓存（`Config/Jobs/`）位置不同，勿混淆。
3. **未连接时文件可能残留上次连接的旧数据**——UI 必须「已连接才读」（`ILCamPage` 断开时清空 `cmbJob`，`RefreshJobSelect` 未连接直接 return），与「无线激光即无 Job」语义一致，不缓存不兜底。
4. `cmbJob` 下拉项从纯字符串 `"JOB N"` 升级为 `CmbJobItem` 对象（JobId + Text），切换/按钮态判定直取 JobId，移除 `Replace("JOB","").Trim()+TryParse` 脆弱解析。

## 关联

- 实现：[[api/IntelligentLaserCam]]（`FetchJobList` / `GetJointTypeName` / `GetCurrentJobInfo`）
- 模块：[[modules/IntelligentLaserCam]]
- 兄弟教训：[[lessons/IntelligentLaser-JobParamNoOfflineCache]]
