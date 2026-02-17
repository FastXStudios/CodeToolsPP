<div align="center">
  <img src="docs/screenshots/icon.png" alt="Code Tools++" width="90"/>
  <h1>Code Tools ++</h1>
  <p><strong>AI-powered desktop toolkit for developers who work with large codebases.</strong><br>
  Explore, analyze, clean, document, and chat with your code — all from a single interface.</p>

  <p>
    <a href="README.md"><img src="assets/flags/en.png" width="32" height="32" alt="English"></a>
    <a href="docs/translations/README.es.md"><img src="assets/flags/es.png" width="32" height="32" alt="Español"></a>
    <a href="docs/translations/README.zh.md"><img src="assets/flags/zh.png" width="32" height="32" alt="中文"></a>
    <a href="docs/translations/README.ru.md"><img src="assets/flags/ru.png" width="32" height="32" alt="Русский"></a>
  </p>

  <p>
    <a href="#installation"><img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python"></a>
    <a href="#installation"><img src="https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white" alt="Platform"></a>
    <a href="#tech-stack"><img src="https://img.shields.io/badge/GUI-Tkinter-FFB000" alt="GUI"></a>
    <a href="#ai-chat--model-engine"><img src="https://img.shields.io/badge/AI-DeepSeek%20%7C%20OpenRouter-6C47FF?logo=openai&logoColor=white" alt="AI"></a>
    <a href="#license"><img src="https://img.shields.io/badge/License-MIT-22c55e.svg" alt="License"></a>
  </p>

  <p>
    <a href="#features">Features</a> •
    <a href="#ai-chat--model-engine">AI Engine</a> •
    <a href="#installation">Install</a> •
    <a href="#quick-start-30-seconds">Usage</a> •
    <a href="#project-architecture">Architecture</a> •
    <a href="#roadmap">Roadmap</a>
  </p>

  <hr>
  <em>Stop copying files by hand. Stop switching between 5 tools. Start shipping.</em>
</div>

---

## ⬇️ Download

<div align="center">

<h3>Code Tools ++ v1.0.0</h3>

<a href="https://fastxstudios.github.io/CodeToolsLandingPage/">
  <img src="https://img.shields.io/badge/Download-Windows_Installer-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows Installer">
</a>
&nbsp;
<a href="https://fastxstudios.github.io/CodeToolsLandingPage/">
  <img src="https://img.shields.io/badge/Download-Portable_Version-FFB000?style=for-the-badge&logoColor=white" alt="Portable">
</a>

</div>

---

## Why Code Tools ++?

Every developer who's ever prepped a codebase for AI review, an audit, or a release has done this:

1. Manually open folders, cherry-pick files.
2. Copy-paste contents into a prompt — hoping you didn't miss context.
3. Hunt down TODO/FIXMEs and dead code separately.
4. Clean up `print()` statements file by file.
5. Write a README from scratch at the end of the sprint.

**Code Tools ++ eliminates all of that.** It's a native desktop app (Python + Tkinter) built specifically for the workflows developers actually run — with a built-in AI assistant as a first-class feature, not an afterthought.

---

## Features

### 🤖 AI Chat & Model Engine

This is the core differentiator. Code Tools ++ ships with a full conversational AI interface directly connected to your selected files.

**Built-in model:** [DeepSeek](https://platform.deepseek.com/) — a high-performance, cost-efficient LLM optimized for code tasks.

**Custom model support via [OpenRouter](https://openrouter.ai/):** Add any model available on OpenRouter (GPT-4o, Claude, Gemini, Mistral, LLaMA, etc.) by providing a model ID and API key. No additional dependencies. The model selector supports animated GIF logos per model, persistent selection across sessions, and one-click deletion of custom entries.

**Context modes:**
- `Smart` — sends file metadata (name, extension, line count, size) for lightweight context queries.
- `Full` — sends complete file contents for deep analysis, refactoring, and documentation generation.

**Built-in actions (one-click prompts):**

| Action | What it does |
|---|---|
| **Analyze** | Reviews selected files for structure, patterns, and issues |
| **Fix Errors** | Identifies bugs and suggests corrected code |
| **Document** | Generates inline docstrings and function-level documentation |
| **Optimize** | Proposes performance improvements and refactoring |
| **Explain** | Produces plain-language explanations of what the code does |

**Markdown rendering in chat:** AI responses render code blocks with syntax highlighting (Python, JS/TS, JSON, Bash), a copy button per block, and auto-fit text wrapping — not just raw text.

**Persistence:** Chat history, selected model, context mode, and token usage counter are saved to disk and restored between sessions.

---

### 🗂️ Intelligent Repository Explorer

- File tree with recursive checkbox selection.
- Visual warnings for heavy/ignored directories (`node_modules`, `venv`, `.git`, `dist`, etc.) before you accidentally include them.
- Recent folders history with visual menu and one-click clear.
- Advanced file search with fast navigation.

---

### 📤 Professional Export for AI & Daily Work

Four export modes designed for real developer workflows:

| Mode | Output |
|---|---|
| **Copy with Content** | Full file contents, concatenated |
| **Copy Paths Only** | Relative paths of selected files |
| **Copy Tree** | ASCII directory structure |
| **Copy for LLM** | Structured format optimized for AI prompts — includes paths, language markers, and clean separators |

All modes available from a styled export menu. Save to file supported directly.

---

### 📊 Technical Quality Dashboard

A single view showing what you'd otherwise spend 20 minutes gathering:

- **Project statistics:** total files, lines of code, size distribution.
- **TODO/FIXME tracker:** lists every annotation with file location.
- **Duplicate detector:** flags files with identical or near-identical content.
- **Language distribution:** breakdown by file type with key metrics.

No external tooling required. Runs entirely on the local project.

---

### 🧹 LimpMax — Safe Bulk Code Cleaner

Removes development artifacts before commits, releases, or code reviews:

- Strips `print()` / `console.log()` / `logging.*` statements by language rules.
- Removes inline comments (configurable per language).
- Designed for pre-delivery cleanup — fast, deterministic, and reversible if combined with version control.

---

### 📝 Integrated README Generator

- Generates a full README in Markdown based on project structure.
- Live preview with rendered Markdown.
- Real-time language translation (ES / EN / ZH / RU) — switch language, preview updates immediately.
- Useful for standardizing documentation across teams or publishing open source projects fast.

---

### ⚡ UX Built for Speed

- Custom menus (`Recent`, `Export`) with PNG icons.
- Real-time file preview.
- Hot-swap theme and language without restart.
- Keyboard shortcuts for continuous workflow.

| Shortcut | Action |
|---|---|
| `Ctrl+O` | Open folder |
| `Ctrl+Q` | Exit the application |
| `F5` | Refresh file tree |
| `E` / `Space` | Mark / Unmark file |
| `Ctrl+C` | Copy selected |
| `Ctrl+D` | Clear selection |
| `Ctrl+F` | Search files |
| `Ctrl+P` | Show/Hide preview |
| `Double Click` | Mark file |
| `Right Click` | Open context menu |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Reset zoom |
| `Ctrl+Scroll` | Zoom with mouse scroll |

---

## Supported Languages (UI)

`Español` · `English` · `中文` · `Русский`

---

## Installation

### Prerequisites

- Python 3.12+
- Windows (primary), Linux/macOS (functional, not fully tested)

### 1. Clone

```bash
git clone https://github.com/FastXStudios/CodeToolsPP.git
cd CodeToolsPP
```

### 2. Create virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
python main.py
```

---

## Quick Start (30 seconds)

```
1. Open your project folder  →  Ctrl+O
2. Select relevant files     →  checkbox tree
3. Open AI Chat              →  ask anything about your code
4. Export context for LLM    →  Export menu → Copy for LLM
5. Check the Dashboard       →  find TODOs, duplicates, metrics
6. Run LimpMax               →  strip debug logs before commit
7. Generate README           →  Tools → README Generator
```

---

## AI Setup

### Using the built-in DeepSeek model

DeepSeek is pre-configured. Add your API key in **Settings → AI → API Key**.  
Get a key at [https://openrouter.ai/](https://openrouter.ai/).

### Adding a custom model (OpenRouter or any OpenAI-compatible endpoint)

1. Open the AI Chat window.
2. Click **Select Model → Add Custom Model**.
3. Fill in:
   - **Name** — display name (e.g. `GPT-4o`)
   - **Model ID** — as listed on OpenRouter (e.g. `openai/gpt-4o`)
   - **API Key** — your OpenRouter key
   - **Max Tokens** — context window limit
   - **Logo** — optional PNG/GIF for the model card
4. Save. The model appears in the selector immediately.

OpenRouter models include: `openai/gpt-4o`, `anthropic/claude-3-5-sonnet`, `google/gemini-pro`, `meta-llama/llama-3-70b-instruct`, `mistralai/mistral-large`, and hundreds more.

---

## Project Architecture

```
main.py
├── core/
│   ├── ai_manager.py          # Model registry, API calls, context preparation
│   ├── code_analyzer.py       # Static analysis, TODO/FIXME detection
│   ├── export_manager.py      # All export formats including LLM mode
│   ├── file_manager.py        # File I/O, metadata, info queries
│   ├── limpmax_processor.py   # Language-aware code cleaning engine
│   ├── project_stats.py       # Metrics aggregation
│   ├── selection_manager.py   # Checkbox state management
│   └── startup_preloader.py   # Background initialization
├── gui/
│   ├── main_window.py
│   ├── tree_view.py
│   ├── preview_window.py
│   ├── dashboard_window.py
│   ├── ai_window.py           # Full AI chat UI with markdown rendering
│   ├── limpmax_window.py
│   ├── search_dialog.py
│   ├── readme_generator_dialog.py
│   ├── recent_folders_menu.py
│   ├── export_menu.py
│   ├── widgets/
│   └── components/
└── utils/
    ├── config_manager.py
    ├── language_manager.py    # i18n: ES / EN / ZH / RU
    ├── theme_manager.py
    ├── file_icons.py
    ├── alerts.py
    └── helpers.py
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| GUI | Tkinter / ttk |
| Images | Pillow |
| HTML rendering | tkinterweb |
| Charts | matplotlib |
| Markdown | markdown2 |
| HTTP | requests |
| Clipboard | pyperclip |
| AI | OpenAI-compatible REST API (DeepSeek, OpenRouter) |

---

## Build Executable (PyInstaller)

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

Output: `dist/CodeToolsPP.exe`

---

## Screenshots

**Main Interface:** Main interface with toolbar and file, line, and size counters.
![Main](docs/screenshots/main.png)

**AI Chat:** AI chat with file analysis options.
![AI Chat](docs/screenshots/ai-chat.png)

**Model Selector:** AI model selector with DeepSeek V3.2 active and option to add custom models.
![Model Selector](docs/screenshots/model-selector.png)

**Export Menu:** Export menu with options to copy paths, tree structure, and LLM-ready format.
![Export](docs/screenshots/export-menu.png)

**Dashboard:** Statistics dashboard with file distribution, histogram, and pagination.
![Dashboard](docs/screenshots/dashboard.png)

**LimpMax:** Maximum cleanup tool to remove prints/logs and comments by language.
![LimpMax](docs/screenshots/limpmax.png)

**README Generator:** README generator with configurable sections, badges, and preview.
![README Generator](docs/screenshots/readme-generator.png)

---

## Real-World Use Cases

- **AI-assisted debugging:** Select the broken module → open AI chat → "Why is this function returning None?" — full file context sent automatically.
- **Pre-refactor audit:** Open a legacy repo → Dashboard shows language breakdown, TODO count, and duplicate files in seconds.
- **Pre-commit cleanup:** Run LimpMax to strip all `print()`/`console.log()` statements across 40 files at once.
- **Technical documentation:** Generate README from project structure, translate to English or Chinese, export — under 2 minutes.
- **Team onboarding:** Walk a new developer through project structure using the tree export + LLM-optimized copy for instant orientation.
- **Code review prep:** Export selected files as LLM context, paste into your AI of choice with zero noise.

---

## Roadmap

- [ ] Performance optimization for very large repositories (>10k files)
- [ ] More LLM export presets (system prompt templates, token budget awareness)
- [ ] Extended LimpMax rules and per-file safety controls
- [ ] Automated test suite
- [ ] Release pipeline and auto-update support
- [ ] Linux/macOS packaging

---

## Contributing

1. Fork the repository.
2. Create a branch: `git checkout -b feature/your-improvement`
3. Commit: `git commit -m "feat: your improvement"`
4. Push: `git push origin feature/your-improvement`
5. Open a Pull Request.

---

## Third-Party Assets

This project incorporates icon assets from:

**vscode-material-icon-theme**  
Copyright (c) 2025 Material Extensions  
Licensed under the MIT License  
https://github.com/material-extensions/vscode-material-icon-theme  

The original license is included in the `licenses/` directory.

---

## License

[MIT License](LICENSE)

---

## Author

**Byron Vera**  
GitHub: [FastXStudios](https://github.com/FastXStudios/CodeToolsPP)  
Email: byronvera113@gmail.com