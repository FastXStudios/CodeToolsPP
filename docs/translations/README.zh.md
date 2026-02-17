<div align="center">
  <img src="../../docs/screenshots/icon.png" alt="Code Tools++" width="90"/>
  <h1>Code Tools ++</h1>

  <p><strong>面向大型代码库开发者的 AI 驱动桌面工具包。</strong><br>
  在单一界面中探索、分析、清理、记录并与你的代码对话。</p>
  <p>语言：点击旗帜切换</p>

  <p align="center">
    <a href="../../README.md"><img src="../../assets/flags/en.png" width="32" height="32" alt="English"></a>
    <a href="README.es.md"><img src="../../assets/flags/es.png" width="32" height="32" alt="Español"></a>
    <a href="README.zh.md"><img src="../../assets/flags/zh.png" width="32" height="32" alt="中文"></a>
    <a href="README.ru.md"><img src="../../assets/flags/ru.png" width="32" height="32" alt="Русский"></a>
  </p>

  <p>
    <a href="#安装"><img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python"></a>
    <a href="#安装"><img src="https://img.shields.io/badge/平台-Windows-0078D6?logo=windows&logoColor=white" alt="平台"></a>
    <a href="#技术栈"><img src="https://img.shields.io/badge/GUI-Tkinter-FFB000" alt="GUI"></a>
    <a href="#ai-聊天--模型引擎"><img src="https://img.shields.io/badge/AI-DeepSeek%20%7C%20OpenRouter-6C47FF?logo=openai&logoColor=white" alt="AI"></a>
    <a href="#许可证"><img src="https://img.shields.io/badge/许可证-MIT-22c55e.svg" alt="许可证"></a>
  </p>

  <p>
    <a href="#功能特性">功能特性</a> •
    <a href="#ai-聊天--模型引擎">AI 引擎</a> •
    <a href="#安装">安装</a> •
    <a href="#快速开始30秒">使用方法</a> •
    <a href="#项目架构">架构</a> •
    <a href="#路线图">路线图</a>
  </p>

  <hr>

  <p><em>不再手动复制文件。不再在 5 个工具之间切换。开始高效交付。</em></p>
</div>

---
## ⬇️ 下载

<div align="center">

<h3>代码工具增强版 v1.0.0</h3>

<a href="https://fastxstudios.github.io/CodeToolsLandingPage/">
  <img src="https://img.shields.io/badge/下载-Windows_安装程序-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows 安装程序">
</a>
&nbsp;
<a href="https://fastxstudios.github.io/CodeToolsLandingPage/">
  <img src="https://img.shields.io/badge/下载-便携版-FFB000?style=for-the-badge&logoColor=white" alt="便携版">
</a>

</div>

---

## 为什么选择 Code Tools ++？

每个曾经为 AI 审查、审计或发布准备代码库的开发者都经历过：

1. 手动打开文件夹，逐一筛选文件。
2. 将内容复制粘贴到提示词中——祈祷没有遗漏上下文。
3. 单独搜索 TODO/FIXME 和死代码。
4. 逐文件清理 `print()` 语句。
5. 在冲刺结束时从头编写 README。

**Code Tools ++ 消除了所有这些麻烦。** 它是一款原生桌面应用（Python + Tkinter），专为开发者实际使用的工作流程而构建——内置 AI 助手作为核心功能，而非事后添加。

---

## 功能特性

### 🤖 AI 聊天 & 模型引擎

这是核心差异化功能。Code Tools ++ 内置完整的对话式 AI 界面，直接与你选择的文件连接。

**内置模型：** [DeepSeek](https://platform.deepseek.com/) — 高性能、高性价比的 LLM，针对代码任务优化。

**通过 [OpenRouter](https://openrouter.ai/) 支持自定义模型：** 提供模型 ID 和 API 密钥，即可添加 OpenRouter 上的任意模型（GPT-4o、Claude、Gemini、Mistral、LLaMA 等）。无需额外依赖。模型选择器支持每个模型的动态 GIF 徽标、跨会话持久化选择，以及一键删除自定义条目。

**上下文模式：**
- `Smart` — 发送文件元数据（名称、扩展名、行数、大小），适用于轻量级上下文查询。
- `Full` — 发送完整文件内容，适用于深度分析、重构和文档生成。

**内置操作（一键提示）：**

| 操作 | 功能 |
|---|---|
| **分析** | 审查选定文件的结构、模式和问题 |
| **修复错误** | 识别 Bug 并建议修正代码 |
| **文档化** | 生成内联文档字符串和函数级文档 |
| **优化** | 提出性能改进和重构建议 |
| **解释** | 用通俗语言解释代码的功能 |

**聊天中的 Markdown 渲染：** AI 响应会渲染带有语法高亮的代码块（Python、JS/TS、JSON、Bash），每个代码块配有复制按钮，并自动适配文本换行——而非纯文本。

**持久化：** 聊天历史、选定模型、上下文模式和 Token 使用计数器会保存到磁盘，并在会话之间恢复。

---

### 🗂️ 智能仓库浏览器

- 文件树，支持递归复选框选择。
- 在意外包含重型/忽略目录（`node_modules`、`venv`、`.git`、`dist` 等）之前显示视觉警告。
- 最近文件夹历史记录，带可视化菜单和一键清除。
- 高级文件搜索，支持快速导航。

---

### 📤 专业导出，适用于 AI 和日常工作

四种为真实开发者工作流程设计的导出模式：

| 模式 | 输出 |
|---|---|
| **复制含内容** | 完整文件内容，串联输出 |
| **仅复制路径** | 选定文件的相对路径 |
| **复制树形结构** | ASCII 目录结构 |
| **复制供 LLM 使用** | 针对 AI 提示优化的结构化格式——包含路径、语言标记和干净分隔符 |

所有模式均可从样式化导出菜单访问。支持直接保存到文件。

---

### 📊 技术质量仪表板

单一视图，呈现你通常需要花 20 分钟才能收集的信息：

- **项目统计：** 总文件数、代码行数、大小分布。
- **TODO/FIXME 追踪器：** 列出每条注释及其文件位置。
- **重复检测器：** 标记内容相同或近似相同的文件。
- **语言分布：** 按文件类型分类，附关键指标。

无需外部工具，完全在本地项目上运行。

---

### 🧹 LimpMax — 安全批量代码清理器

在提交、发布或代码审查前移除开发痕迹：

- 按语言规则删除 `print()` / `console.log()` / `logging.*` 语句。
- 删除内联注释（可按语言配置）。
- 专为交付前清理设计——快速、确定性，与版本控制结合使用时可逆。

---

### 📝 集成 README 生成器

- 根据项目结构生成完整的 Markdown README。
- 实时预览，渲染 Markdown 效果。
- 实时语言翻译（ES / EN / ZH / RU）——切换语言，预览立即更新。
- 适合跨团队标准化文档或快速发布开源项目。

---

### ⚡ 为速度而生的用户体验

- 自定义菜单（`最近`、`导出`）配 PNG 图标。
- 实时文件预览。
- 无需重启即可热切换主题和语言。
- 键盘快捷键支持连续工作流。

| 快捷键 | 操作 |
|---|---|
| `Ctrl+O` | 打开文件夹 |
| `Ctrl+Q` | 退出应用程序 |
| `F5` | 刷新文件树 |
| `E` / `空格` | 标记 / 取消标记文件 |
| `Ctrl+C` | 复制选定内容 |
| `Ctrl+D` | 清除选择 |
| `Ctrl+F` | 搜索文件 |
| `Ctrl+P` | 显示/隐藏预览 |
| `双击` | 标记文件 |
| `右键` | 打开上下文菜单 |
| `Ctrl++` | 放大 |
| `Ctrl+-` | 缩小 |
| `Ctrl+0` | 重置缩放 |
| `Ctrl+滚轮` | 用鼠标滚轮缩放 |

---

## 支持的语言（界面）

`Español` · `English` · `中文` · `Русский`

---

## 安装

### 前提条件

- Python 3.12+
- Windows（主要平台），Linux/macOS（功能正常，未完全测试）

### 1. 克隆仓库

```bash
git clone https://github.com/FastXStudios/CodeToolsPP.git
cd CodeToolsPP
```

### 2. 创建虚拟环境

**Windows (PowerShell)：**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS：**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行

```bash
python main.py
```

---

## 快速开始（30秒）

```
1. 打开你的项目文件夹  →  Ctrl+O
2. 选择相关文件       →  复选框树
3. 打开 AI 聊天       →  询问任何关于代码的问题
4. 为 LLM 导出上下文  →  导出菜单 → 复制供 LLM 使用
5. 检查仪表板         →  查找 TODO、重复项、指标
6. 运行 LimpMax       →  提交前去除调试日志
7. 生成 README        →  工具 → README 生成器
```

---

## AI 设置

### 使用内置 DeepSeek 模型

DeepSeek 已预配置。在 **设置 → AI → API 密钥** 中添加你的 API 密钥。  
在 [https://openrouter.ai/](https://openrouter.ai/) 获取密钥。

### 添加自定义模型（OpenRouter 或任何兼容 OpenAI 的端点）

1. 打开 AI 聊天窗口。
2. 点击 **选择模型 → 添加自定义模型**。
3. 填写：
   - **名称** — 显示名称（例如 `GPT-4o`）
   - **模型 ID** — 如 OpenRouter 上所列（例如 `openai/gpt-4o`）
   - **API 密钥** — 你的 OpenRouter 密钥
   - **最大 Token 数** — 上下文窗口限制
   - **徽标** — 模型卡片的可选 PNG/GIF
4. 保存。模型立即出现在选择器中。

OpenRouter 模型包括：`openai/gpt-4o`、`anthropic/claude-3-5-sonnet`、`google/gemini-pro`、`meta-llama/llama-3-70b-instruct`、`mistralai/mistral-large` 等数百个。

---

## 项目架构

```
main.py
├── core/
│   ├── ai_manager.py          # 模型注册表、API 调用、上下文准备
│   ├── code_analyzer.py       # 静态分析、TODO/FIXME 检测
│   ├── export_manager.py      # 所有导出格式，包括 LLM 模式
│   ├── file_manager.py        # 文件 I/O、元数据、信息查询
│   ├── limpmax_processor.py   # 语言感知代码清理引擎
│   ├── project_stats.py       # 指标聚合
│   ├── selection_manager.py   # 复选框状态管理
│   └── startup_preloader.py   # 后台初始化
├── gui/
│   ├── main_window.py
│   ├── tree_view.py
│   ├── preview_window.py
│   ├── dashboard_window.py
│   ├── ai_window.py           # 完整 AI 聊天界面，含 Markdown 渲染
│   ├── limpmax_window.py
│   ├── search_dialog.py
│   ├── readme_generator_dialog.py
│   ├── recent_folders_menu.py
│   ├── export_menu.py
│   ├── widgets/
│   └── components/
└── utils/
    ├── config_manager.py
    ├── language_manager.py    # 国际化：ES / EN / ZH / RU
    ├── theme_manager.py
    ├── file_icons.py
    ├── alerts.py
    └── helpers.py
```

---

## 技术栈

| 层级 | 技术 |
|---|---|
| 语言 | Python 3.12+ |
| GUI | Tkinter / ttk |
| 图像 | Pillow |
| HTML 渲染 | tkinterweb |
| 图表 | matplotlib |
| Markdown | markdown2 |
| HTTP | requests |
| 剪贴板 | pyperclip |
| AI | 兼容 OpenAI 的 REST API（DeepSeek、OpenRouter） |

---

## 构建可执行文件（PyInstaller）

```powershell
  .\.venv\Scripts\python.exe -m PyInstaller
  --noconfirm --clean --onefile 
  --windowed --name "CodeToolsPP" 
  --icon ".\icon.ico" --add-data ".\assets;assets" 
  --add-data ".\data;data" 
  --add-data ".\icon.ico;." 
  --hidden-import "PIL._tkinter_finder" 
  --collect-submodules "PIL" 
  --collect-data "tkinterweb" 
  .\main.py
```

输出：`dist/CodeToolsPP.exe`

---

## 截图

**主界面：** 带工具栏及文件、行数和大小计数器的主界面。
![Main](../../docs/screenshots/main.png)

**AI 聊天：** 带文件分析选项的 AI 聊天界面。
![AI Chat](../../docs/screenshots/ai-chat.png)

**模型选择器：** 激活 DeepSeek V3.2 并可添加自定义模型的 AI 模型选择器。
![Model Selector](../../docs/screenshots/model-selector.png)

**导出菜单：** 含复制路径、树形结构和 LLM 就绪格式选项的导出菜单。
![Export](../../docs/screenshots/export-menu.png)

**仪表板：** 带文件分布、直方图和分页的统计仪表板。
![Dashboard](../../docs/screenshots/dashboard.png)

**LimpMax：** 按语言删除 print/日志和注释的最大清理工具。
![LimpMax](../../docs/screenshots/limpmax.png)

**README 生成器：** 带可配置章节、徽标和预览的 README 生成器。
![README Generator](../../docs/screenshots/readme-generator.png)

---

## 真实使用场景

- **AI 辅助调试：** 选择有问题的模块 → 打开 AI 聊天 → "为什么这个函数返回 None？"——完整文件上下文自动发送。
- **重构前审计：** 打开遗留仓库 → 仪表板在数秒内显示语言分布、TODO 数量和重复文件。
- **提交前清理：** 运行 LimpMax，一次性删除 40 个文件中的所有 `print()`/`console.log()` 语句。
- **技术文档：** 根据项目结构生成 README，翻译成英文或中文，导出——不到 2 分钟。
- **团队入职：** 使用树形导出 + LLM 优化复制，引导新开发者快速了解项目结构。
- **代码审查准备：** 将选定文件导出为 LLM 上下文，粘贴到你喜欢的 AI 中，零噪音。

---

## 路线图

- [ ] 针对超大型仓库（>10k 文件）的性能优化
- [ ] 更多 LLM 导出预设（系统提示模板、Token 预算感知）
- [ ] 扩展的 LimpMax 规则和每文件安全控制
- [ ] 自动化测试套件
- [ ] 发布流水线和自动更新支持
- [ ] Linux/macOS 打包

---

## 贡献

1. Fork 仓库。
2. 创建分支：`git checkout -b feature/your-improvement`
3. 提交：`git commit -m "feat: your improvement"`
4. 推送：`git push origin feature/your-improvement`
5. 打开 Pull Request。

---

## 第三方资源

本项目使用了以下图标资源：

**vscode-material-icon-theme**  
Copyright (c) 2025 Material Extensions  
基于 MIT 许可证授权  
https://github.com/material-extensions/vscode-material-icon-theme  

原始许可证包含在 `licenses/` 目录中。

---

## 许可证

[MIT 许可证](LICENSE)

---

## 作者

**Byron Vera**  
GitHub: [FastXStudios](https://github.com/FastXStudios/CodeToolsPP)  
Email: byronvera113@gmail.com