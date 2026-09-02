# AdaWeldSystem LLM Wiki Browser

基于 **纯 HTML + 预生成 JS 数据** 的 Wiki 知识库浏览器，零依赖、即开即用。

## 问题背景

之前尝试了多种方案，各有问题：
- **HTML + 文件系统 API**：浏览器安全策略限制，无法自动读取本地文件夹
- **C# WinForms + HTTP 服务**：编译复杂、时序问题多
- **Python + PyQt6**：依赖安装麻烦、conda 加载慢、DLL 兼容问题

本方案采用 **预生成数据文件** 思路：
1. Python 脚本一次性扫描 LLMWiki 目录，生成 `wiki_data.js`
2. HTML 通过 `<script src="wiki_data.js">` 加载（浏览器对本地 JS 文件**无 CORS 限制**）
3. 双击 HTML 即可打开，无需任何运行时依赖

## 文件说明

```
tools/
├── WikiBrowser.html       # 主界面（单文件，内嵌 CSS + JS）
├── generate_wiki_data.py  # 数据生成脚本（扫描 LLMWiki 生成 wiki_data.js）
├── wiki_data.js           # 预生成的 Wiki 数据文件（由脚本自动生成）
└── README.md              # 本说明文档
```

## 使用方法

### 首次使用

1. 确保 `generate_wiki_data.py` 和 `WikiBrowser.html` 在同一目录
2. 运行生成脚本：
   ```bash
   cd tools
   python generate_wiki_data.py
   ```
3. 双击打开 `WikiBrowser.html`
4. 完成！页面自动加载所有 Wiki 内容

### 日常使用

- **双击 `WikiBrowser.html`** 即可打开（使用系统默认浏览器）
- 左侧文件树点击浏览页面
- 支持 [[双向链接]] 点击跳转
- 顶部搜索框跨全文搜索
- 浏览 / 图谱 / 索引 / 日志 视图切换

### Wiki 内容更新后

当 LLMWiki 中的 .md 文件有新增或修改时，重新运行：
```bash
python generate_wiki_data.py
```
然后刷新浏览器页面即可看到更新。

## 功能特性

| 功能 | 说明 |
|------|------|
| 📄 浏览 | 左侧文件树 + 右侧 Markdown 渲染，支持完整语法 |
| 🔗 双向链接 | 自动识别 `[[PageName]]`，点击跳转对应页面 |
| 🔍 搜索 | 跨所有页面全文搜索，支持文件名和内容匹配 |
| 🕸️ 知识图谱 | Canvas 绘制页面链接关系图 |
| 📑 索引/日志 | 一键切换查看 logs/index.md 和 logs/log.md |
| 🔄 重新生成 | 点击工具栏"重新生成数据"按钮查看提示 |

## 技术细节

- **Markdown 渲染器**：纯 JS 实现，支持标题、粗体/斜体、代码块、表格、列表、引用、链接、图片、水平线
- **数据格式**：`wiki_data.js` 包含所有 .md 文件的完整内容，JSON 结构
- **兼容性**：任何现代浏览器（Chrome、Edge、Firefox、Safari）
- **无需服务器**：`file://` 协议直接打开，无需 HTTP 服务

## 注意事项

1. `wiki_data.js` 文件较大（约 500KB），首次加载可能需要 1-2 秒
2. 如果 Wiki 内容敏感，请勿将 `wiki_data.js` 提交到公共仓库（它包含所有 .md 的完整内容）
3. 生成脚本需要 Python 3.6+，无需安装任何第三方库（仅使用标准库）
