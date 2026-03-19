# 🏛️ Brand-CLI: Master Design Specification  
*Version:* 1.0 (March 2026)  
*Role:* Single Source of Truth for Implementation Models  
*Client/Boss:* Bud (Grandpa Bud Plays)

---

## 1. Project Identity & Goal  
**Brand-CLI** is a professional-grade, Python-based Command Line Interface designed to automate the media review and content production workflow for a multi-platform creator brand. 

The primary goal is to take raw production artifacts (Transcripts, Notes, Metadata) and orchestrate a pipeline that interacts with AI Models (Gemini/OpenRouter) to generate structured outputs (Audits, YouTube Descriptions, Social Promos). It aims for **"Zero Fatigue"**—reducing manual path entry and repetitive prompting through stateful context and dynamic text assembly.

---

## 2. Current Architecture

### 🛰️ The Command Pattern  
The system uses a decoupled Command/Strategy pattern.   
* **The Entry Point:** `Brand.py` acts as the traffic controller.  
* **The Workflow Class:** Each task (e.g., `Audit`, `Draft`, `Feedback`, `Gold`) is a distinct class that orchestrates a specific sequence: Locating files -> Building Prompts -> Calling the AI Client -> Saving Output.

### 💾 Stateful Context (`brand_config.json`)  
To eliminate path-entry fatigue, the CLI maintains a hidden state file.  
* **Hierarchy:** IP > Series > Season > Episode.  
* **Resolution:** Commands like `Audit E005` automatically resolve to the full directory path based on the current active context. If the context is missing, the system performs a hierarchical "walk-up" search using `pathlib.Path` (uses path objects instead of strings). Includes enhanced error handling when walk-up fails.

### 🧩 The Polymorphic Fragment Engine (NEW)  
A specialized engine for assembling text without hardcoding. It treats every piece of text (System Prompts, Social Links, Random Tips) as a "Fragment."  
* **Hierarchical Resolution:** Fragments are searched from the Episode level up to the Global level.  
* **Fragment Types:**  
    * `Static`: Fixed text from a file.  
    * `Random`: Selects a random block from a delimited file.  
    * `Flagged`: Retrieves a specific section using `[TAGS]`.  
    * `Composite`: A container that chains multiple fragments together (Recursive Pattern).

---

## 3. State of the Union

### ✅ Finalized Logic (Ready for Implementation)  
* **MAM Structure:** The folder hierarchy and naming conventions are locked.  
* **Agnostic Philosophy:** The code must remain decoupled from specific game titles (e.g., Valheim) or branding.  
* **Fragment Strategy:** The class hierarchy for the Fragment engine is conceptually complete.  
* **Output Handling:** AI results are saved directly into "Bundled" episode folders.

### 🛠️ Conceptual / In-Progress  
* **Auto-Migration:** Logic for moving "Inbox" files into "Bundled" folders is designed but requires robust error handling.  
* **Fragment Integration:** The specific mapping of which Workflows use which Fragments is currently being defined.  
* **Multi-Client Support:** While currently locked to Gemini, the `Client` class must be prepared for OpenRouter abstraction.

---

## 4. Coding Standards  
Implementation models must strictly adhere to the following:  
* **Language:** Python 3.10+ with strict Type Hinting.  
* **Dependency Injection:** Classes (Workflow, Fragment, Client) must be instantiated with their dependencies to allow for unit testing.  
* **Error Handling:** "Fail Forward" policy. If a fragment or file is missing, the tool must output a clear error string within the generated document rather than crashing.  
* **Stateless Code/Stateful Data:** The code itself remains stateless; all environmental awareness must come from `brand_config.json` or `.brand_context`.

---

## 5. The 'Next Task'  
**Immediate Goal:** Implement the **Fragment Engine Hierarchy**.

**Instructions for the Implementation Model:**  
Develop the `Fragment` Abstract Base Class and its four subclasses (`Static`, `Random`, `Flagged`, `Composite`). Include a `FragmentFactory` and the `resolve_path` logic that performs the hierarchical directory walk (Episode -> Global). Ensure the `CompositeFragment` can recursively handle other fragments to build a complete System Prompt or File Footer.  
