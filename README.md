<div align="center">

# 🎬 Brand-CLI
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

- **Tactical Stream Audits:** Evaluates transcripts for pacing, filler words, and brand voice adherence (e.g., plain speech, guidance rules).
- **Strategic Gold Extraction:** Automatically identifies and timestamps moments for Shorts (Type A), Clips (Type B), Narrative/Action Montages (Type C), and strict YouTube Chapters.
- **Automated YouTube Drafting:** A multi-pass pipeline that generates complete "Triple-Threat" YouTube descriptions (Hook, Lore, Chronicle) and automatically injects SEO keywords.
- **Agnostic Architecture:** Completely decoupled from the content repository. Point it at any Media Asset Management (MAM) archive on your machine using a simple JSON configuration.
- **Built-in Cost & Token Tracking:** Monitors API usage and prevents token-limit crashes by utilizing robust Gemini API wrappers.

---

## 🚀 Installation

### 1. Prerequisites
- Python 3.10 or higher
- A [Google Gemini API Key](https://aistudio.google.com/)

### 2. Clone the Repository
```bash
git clone https://github.com/GrandpaBud/Brand-CLI.git
cd Brand-CLI
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

Brand-CLI uses a modern JSON configuration structure built around standard Media Asset Management (MAM) terms. By default, it looks for `brand_config.json` in the current working directory, or you can specify a path using the `BRAND_CONFIG_PATH` environment variable.

Create a `brand_config.json` file to point the CLI to your specific content archive:

```json
{
    "archive": {
        "content_root": "/absolute/path/to/your/Content-Archive",
        "global_lexicon_path": "/absolute/path/to/your/Content-Archive/Global-Lexicon.md",
        "arc_metadata_file": "Arc.md"
    },
    "brand": {
        "default_arcs": {
            "Season 1": "The Beginning",
            "Season 2": "The Journey"
        }
    },
    "reports": {
        "group_by_episode": true
    }
}
```

---

## 💻 Usage

Run the orchestrator from the terminal using the following syntax:

```bash
python Brand.py <Operation> <Season> <Episode> [--continue]
```

**Example:**
```bash
python Brand.py Audit S01 E005
```

### Available Operations

| Operation | Description | Output |
| :--- | :--- | :--- |
| **`Audit`** | Runs both `Feedback` and `Gold` operations sequentially. | Both Audit & Gold `.md` and `.json` files. |
| **`Feedback`** | Generates a tactical audit of the stream (pacing, filler words, brand rules). | `{Ep} Audit.md` |
| **`Gold`** | Extracts strategic highlights (Shorts, Clips, Montages, Chapters). | `{Ep} Gold.md` |
| **`Draft`** | 4-Pass pipeline generating YouTube descriptions. Pass 2 requires the `--continue` flag. | `{Ep} Description.md` |

*(Note: Every operation outputs clean Markdown (`.md`) reports alongside raw `.json` files for programmatic chaining and debugging, cleanly organized into Episode folders if configured).*

---

## 📂 Project Structure

```text
Brand-CLI/
├── Brand.py                # Main entry point / CLI router
├── config.py               # JSON configuration manager
├── file_manager.py         # Agnostic file I/O & path resolution
├── requirements.txt        # Python dependencies
├── ai/                     # Gemini SDK wrappers, runners, & cost tracking
├── prompts/                # AI system instructions and templating engine
└── workflows/              # Business logic for Audit, Feedback, Gold, & Draft
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
