# 🏛️ Architecture & Design Principles

This document captures the core design decisions, philosophies, and architectural patterns of the Brand-CLI. 

**Why does this file exist?** AI assistants are stateless. When a new chat session starts, the AI reads the repository to understand the rules. This document ensures that future AI assistants (and human contributors) strictly adhere to the established design goals and don't accidentally revert to old, hardcoded patterns.

---

## 1. The Core Philosophy: Agnostic & Decoupled
Brand-CLI is a generic tool built for *any* production team. It must never assume it is processing Valheim, gaming content, or any specific creator's IP.
* **Separation of Concerns:** The code lives in `Brand-CLI`. The content lives in a completely separate repository (the "Archive").
* **No Hardcoded Paths:** The tool must never hardcode directories like `/010-Valheim/`. It must rely entirely on the `brand_config.json` to locate the `content_root`.
* **Token Safety:** By keeping the codebase separate from the massive Markdown content archives, we prevent AI coding assistants from being overwhelmed by token limits when modifying the Python scripts.

## 2. Media Asset Management (MAM) Hierarchy
The archive structure follows professional Media Asset Management standards. The internal code must always use these generic terms, even if the user interface displays custom terminology.
* **IP:** The highest level (e.g., "The Valheim Franchise", "Tech Tutorials").
* **Series:** The specific show or format (e.g., "Chronicles of the Exile").
* **Season:** The narrative arc or milestone (e.g., "Saga I", "2024").
* **Episode:** The individual asset or segment (e.g., "E005").
* **Arc:** A thematic grouping, often synonymous with Season/Milestone (e.g., "Swamp Biome", "Q3 Goals").

## 3. Stateful Context (Zero Fatigue CLI)
To prevent users from typing long directory paths or specifying the IP/Series on every command, the CLI is *stateful*.
* **The `.brand_context` File:** The `Context` command writes the user's current focus (IP, Series, Season) to a hidden local file. 
* **Implicit Resolution:** Operations like `Audit E001` automatically read the context file to know exactly where to look.
* **Graceful Fallbacks:** If the context is empty, the `file_manager` performs a full-archive search. If collisions occur (e.g., multiple "E001" files exist across different IPs), it safely aborts and asks the user to narrow their context.

## 4. Dynamic Terminology Injection
Because "Season" or "Arc" doesn't fit every creator's brand, the AI prompts are dynamically injected with the creator's preferred terminology.
* **The Dictionary:** `brand_config.json` allows users to map generic MAM terms to their specific brand voice (e.g., `{"arc": "Biome", "season": "Saga"}`).
* **Prompt Engineering:** AI Prompts (like `audit.py`) must use variables like `{arc_term}` and `{arc}` rather than hardcoding words like "Biome".
* **Output:** The AI generates Markdown reports using the custom terminology, ensuring the final output perfectly matches the creator's brand voice.

## 5. Inbox to Bundled Episode Architecture
The system acts as a pipeline orchestrator that actively manages your raw file states.
* **The Staging Inbox:** Raw files exported from video software or transcript tools are initially dropped as flat files (e.g., `S01 E01 Transcript.md`). This indicates they are "unprocessed".
* **Auto-Migration:** Upon running any workflow (e.g., `Audit`), the `file_manager` locates the flat transcript and automatically migrates it into a "Bundled" directory structure (e.g., `S01 E01/Transcript.md`).
* **Clean Artifacts:** Once bundled, all AI-generated reports (`Audit.md`, `Gold.md`, `Draft.json`) are written directly to this new episode folder without redundant episode prefixes in their filenames.
