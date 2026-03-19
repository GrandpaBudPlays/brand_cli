<div align="center">

# 🎬 brand_cli
**The AI-Powered Content Pipeline Orchestrator**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Gemini API](https://img.shields.io/badge/Google-Gemini_AI-orange.svg)](https://aistudio.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

A command-line tool designed to assist production teams with their workflow pipelines. It performs automated AI reviews, content extraction, and drafting directly from raw stream transcripts.

[Features](#-features) • [Installation](#-installation) • [Configuration](#-configuration) • [Usage](#-usage) • [Contributing](#-contributing)

</div>

---

## ✨ Features

- **Stateful Context (Zero Fatigue CLI):** Set your current focus (IP, Series, Season) once, and the CLI remembers it via a local hidden file. Run workflow operations seamlessly without constantly retyping long directory paths.
- **Agnostic Architecture:** Completely decoupled from the content repository. Point it at any Media Asset Management (MAM) archive on your machine using a simple JSON configuration.
- **Dynamic Terminology Injection:** Map generic MAM terms (IP, Series, Season, Arc, Episode) to your specific brand voice (e.g., "Franchise", "Show", "Saga", "Biome"). The AI automatically adopts your vocabulary in its prompts and output reports.
- **Polymorphic Fragment Engine:** Hierarchical text assembly system with:
  - Static fragments (exact file content)
  - Random fragments (random blocks from delimited files)
  - Flagged fragments (tagged sections with [TAG:NAME] syntax)
  - Composite fragments (recursive chaining with cycle detection)
- **Tactical Stream Audits:** Evaluates transcripts for pacing, filler words, and brand voice adherence (e.g., plain speech, guidance rules).
- **Strategic Gold Extraction:** Automatically identifies and timestamps moments for Shorts (Type A), Clips (Type B), Narrative/Action Montages (Type C), and strict YouTube Chapters.
- **Automated YouTube Drafting:** A multi-pass pipeline that generates complete "Triple-Threat" YouTube descriptions (Hook, Lore, Chronicle) and automatically injects SEO keywords.
- **Built-in Cost & Token Tracking:** Monitors API usage and prevents token-limit crashes by utilizing robust Gemini API wrappers.

---

## 🚀 Installation

### 1. Prerequisites
- Python 3.10 or higher
- A [Google Gemini API Key](https://aistudio.google.com/)

### 2. Clone the Repository
```bash
git clone https://github.com/GrandpaBud/brand_cli.git
cd brand_cli
```

### 3. Setup Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root of the project to securely store your API key:
```bash
echo "GEMINIAPIKEY=your_actual_api_key_here" > .env
```

---

## ⚙️ Configuration

brand_cli uses a modern JSON configuration structure built around the standard Media Asset Management (MAM) hierarchy (IP > Series > Season > Episode). By default, it looks for `brand_config.json` in the current working directory, or you can specify a path using the `BRAND_CONFIG_PATH` environment variable.

Create a `brand_config.json` file to point the CLI to your specific content archive and define your brand terminology:

```json
{
    "archive": {
        "content_root": "/absolute/path/to/your/Content-Archive"
    },
    "ips": {
        "Valheim": {
            "terminology": {
                "ip": "Game",
                "series": "Chronicles",
                "season": "Saga",
                "arc": "Biome"
            },
            "series": {
                "Chronicles": {
                    "path_relative": "010-Valheim/Chronicles-Of-The-Exile",
                    "global_lexicon_path": "010-Valheim/Saga-Lexicon-Valheim.md",
                    "arc_metadata_file": "Biome.md",
                    "default_arcs": {}
                }
            }
        }
    },
    "reports": {
        "group_by_episode": true
    }
}
```

---

## 💻 Usage

brand_cli features a **stateful context** so you can work friction-free. 

### 1. Set Your Context
First, tell the CLI what part of the archive you are working on. This is saved to a local hidden `.brand_context` file.

```bash
python Brand.py Context --ip "Valheim" --series "Chronicles" --season "Saga I"
```
*(You can clear your active context at any time using `python Brand.py Context --clear`)*

### 2. Run Operations
Once your context is set, you can execute workflow pipelines using clean, shorthand syntax:

```bash
python Brand.py Audit E005
```

If you prefer to run it without a saved context, explicitly provide the arguments:
```bash
python Brand.py Audit "Saga I" E005
```

### Available Operations

| Operation | Description | Output |
| :--- | :--- | :--- |
| **`Context`** | Sets or clears the active stateful session (`--ip`, `--series`, `--season`). | `.brand_context` file |
| **`Audit`** | Runs both `Feedback` and `Gold` operations sequentially. | Both Audit & Gold `.md` and `.json` files. |
| **`Feedback`** | Generates a tactical audit of the stream (pacing, filler words, brand rules). | `Audit.md` |
| **`Gold`** | Extracts strategic highlights (Shorts, Clips, Montages, Chapters). | `Gold.md` |
| **`Draft`** | 4-Pass pipeline generating YouTube descriptions. Pass 2 requires the `--continue` flag. | `Description.md` |
| **`Describe`**| Placeholder for future describe functionality. | N/A |

*(Note: Every operation outputs clean Markdown (`.md`) reports alongside raw `.json` files for programmatic chaining and debugging. The system acts as an auto-organizer: processing an episode automatically migrates its raw transcript into a dedicated episode folder where all generated reports are saved).* 

---

## 📂 Project Structure

```text
brand_cli/
├── pyproject.toml             # Project configuration and entry points
├── .env                       # API keys (Gemini/OpenAI) - DO NOT COMMIT
├── .brand_context             # Stateful context for the assembly engine
├── src/
│   └── brand_cli/             # Main package directory
│       ├── Brand.py           # Application entry point (main loop)
│       ├── config.py          # Configuration and Context loaders
│       ├── file_manager.py    # Workspace and file I/O logic
│       ├── ai/                # AI model adapters (Gemini, OpenAI, Azure)
│       ├── fragments/         # Polymorphic text components
│       ├── prompts/           # System instructions and templates
│       └── workflows/         # Business logic for Audit, Draft, etc.
├── docs/
│   └── brand_cli.md           # Technical documentation
├── misc/                      # Scripts and experimental tests
├── venv/                      # Virtual environment (local only)
└── README.md                  # Project overview
```

---

## 🤝 Contributing

Contributions make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---
<div align="center">
<i>Forged with 🛡️ by Grandpa Bud's Production Team</i>
</div>