# Technical Brief: Brand-CLI Development & Architecture

### 1. Core Brand Identity: "Chronicles of the Exile"
The CLI is designed to automate content creation for the YouTube channel "@budwheeler17" (Grandpa Bud Plays), enforcing a "Triple-Threat" narrative structure:
* **Voice A (Ulf):** Punchy, atmospheric, mythic Viking hook.
* **Voice B (Grandpa):** Calm, instructional, elder-warrior wisdom.
* **Voice C (Conrad):** Technical, factual, progress-oriented summary.
* **Lexicon Integration:** A `Saga-Lexicon.md` defines world-building terms (e.g., Birch = *The Iron-Bark*, Beehives = *The Golden Ones*) which must be injected into all creative prompts to maintain consistency.

### 2. CLI Architecture & Workflow
The system utilizes a modular, multi-pass pipeline managed by a `WorkflowContext` object.

#### A. The Gold Workflow (Mining)
* **Responsibility:** Analyzes ~30m transcripts (~10k tokens) to extract high-value moments.
* **Output:** Generates a `Gold Report` (JSON/Markdown) containing:
    * **Type A (Shorts):** 15-60s educational/hook moments.
    * **Type B (Clips):** 1-5m narrative beats.
    * **Type C (Arc):** Atmospheric montages.
    * **Ledger Entry:** A ~300-word narrative summary in the "Grandpa" voice.

#### B. The Draft Workflow (Assembly)
* **Pass 1 (Extraction):** Summarizes the raw transcript into a factual JSON list of events.
* **Pass 2 (Assembly):** Ingests the **Ledger Entry** (from the Gold Report) and the **Factual Extraction** to weave the final Triple-Threat YouTube description.
* **Efficiency:** Passing the `Gold Report` instead of the full transcript reduces input tokens from ~10k to <1k for the final drafting pass.

#### C. The Prompt Engine
* **Hybrid Loader:** `PromptLoader` prioritizes external YAML templates/fragments (supporting Jinja2 logic) but falls back to hard-coded Python classes/strings (legacy, to be retired) if files are missing.
* **Idempotency:** Workflows check for existing local artifacts (e.g., `chapters.json`) to skip redundant API calls and manage costs.

### 3. Technical Discoveries & Constraints
* **Gemini File API:** Transcripts are uploaded once and referenced by a `URI`. Subsequent calls "re-read" the file without re-uploading, though they still incur token processing costs.
* **Token Management:** Large transcripts (~10k tokens) require efficient multi-pass logic to avoid unnecessary "Double Token Taxes."
* **Parsing Logic:** Parsers in `mixins.py` must be structure-agnostic to handle non-deterministic JSON (handling both top-level Lists and Objects).
* **Formatting Guardrails:** Python’s `.format()` method is incompatible with Jinja2 syntax (`{% %}`) and single JSON braces. 
    * **Solution:** All literal JSON braces in Python-based templates must be doubled (`{{ }}`).

### 4. MVP Roadmap (Pending)
1.  **Ledger-Draft Integration:** Explicitly pass `ledger_entry` from the Gold Report into the Draft Pass 2 prompt to eliminate voice drift.
2.  **Local Caching:** Finalize the mechanism for writing/reading `chapters.json` locally to ensure 0-token re-runs for verified data.
3.  **Boilerplate Externalization:** Move social links, playlist IDs, and SEO tags into a centralized `config.yaml`.

**Target Environment:** Python 3.12, Gemini-3-Flash-Preview, Linux/Olathe-based dev environment.

### **Bud's Notes**
- Fragments will accept content as a parameter and not read/import data internally.
